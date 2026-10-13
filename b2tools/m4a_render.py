"""Render a Ruby/Sapphire song from the GBA ROM to a WAV, following the M4A engine (pokeemerald src/m4a_1.s and
src/m4a.c; Ruby's settings from pokeruby src/libs/m4a.c: 5 DirectSound channels at 13,379 Hz, 8-bit output, master
volume 12, the song's reverb). For listening comparisons (notes/MUSIC.md); an approximation of the hardware mixer.

    python3 m4a_render.py SONG OUT.wav [SECONDS]

Modelled: the engine's 59.7275 Hz frame loop and tempo counter (ticks every 150 tempo units), each track's events
(m4a.parse_track, the loop repeated), gate times, TIE/EOT, channel allocation by priority (5 DirectSound channels,
one each of square 1, square 2, wave, noise), keysplit and drum-kit voices, TrkVolPitSet / ChnVolSetAsm volumes and
pan, MidiKeyToFreq pitch (bend, bend range, key shift, the triangle LFO), the DirectSound envelope (attack added,
decay / release multiplied each frame, sustain level, pseudo-echo), fixed-pitch samples at the mixing rate, the
reverb (mono sum of this and the previous DMA buffer, times reverb / 512, written back to both sides). CGB channels:
square duties, the 4-bit wave, noise, and their 0-15 envelopes stepped per frame (an approximation of the 1/64 s
hardware steps); hard left / centre / right panning as CgbPan.
"""
import os, sys, struct, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m4a  # noqa: E402

MIX_HZ = 13379
SPF = 224                     # samples per V-blank at 13,379 Hz
DMA_PERIOD = 1584 // SPF      # 7 frames per DMA buffer
MASTER = 12
MAX_DS = 5
OUT_HZ = 44100


class Chan:
    def __init__(self): self.on = False


def unrolled(tr, until):
    """The track's events up to tick `until`, the loop part repeated."""
    out = list(tr.events)
    if tr.loop_tick is None: return out
    loop = [e for e in tr.events[tr.loop_event:]]
    span = tr.end_tick - tr.loop_tick
    k = 1
    while tr.end_tick + (k - 1) * span < until and span > 0:
        out += [(e[0], e[1] + k * span) + tuple(e[2:]) for e in loop]
        k += 1
    return out


class Renderer:
    def __init__(self, rom, n):
        self.rom = rom
        self.h, self.tracks = m4a.parse_song(rom, n)
        self.vg = self.h['voicegroup']
        self.reverb = self.h['reverb'] & 0x7F if self.h['reverb'] & 0x80 else 0
        self.waves = {}
        self.solo = None               # analysis only: keep the notes of this track alone

    @classmethod
    def phrase(cls, rom, voicegroup, voice, key, gate, vel=100, vol=100, tempo=60, reverb=0):
        """A renderer for one note of `voice` (calibration: m4a_to_sseq's levels): TEMPO 60 = 120 bpm."""
        r = cls.__new__(cls)
        r.rom, r.vg, r.reverb, r.waves, r.solo = rom, voicegroup, reverb, {}, None
        tr = m4a.Track()
        tr.events = [('tempo', 0, tempo), ('voice', 0, voice), ('vol', 0, vol), ('pan', 0, 64), ('note', 0, key, vel, gate)]
        tr.end_tick = 10 ** 6
        r.h, r.tracks = dict(voicegroup=voicegroup, reverb=0), [tr]
        return r

    def wavedata(self, addr):
        if addr not in self.waves:
            w = self.rom.wave(addr)
            self.waves[addr] = (np.frombuffer(w['data'], dtype=np.int8).astype(np.float32), w)
        return self.waves[addr]

    def render(self, seconds):
        frames = int(seconds * m4a.FRAME_HZ)
        until = 10 ** 9
        tempo_d = 150
        # per track state
        T = []
        for i, tr in enumerate(self.tracks):
            T.append(dict(ev=unrolled(tr, 200000), pos=0, voice=None, vol=0, pan=0, volX=64, panX=0, bend=0,
                          bendr=2, keysh=0, tune=0, mod=0, modT=0, lfos=22, lfodl=0, lfodlC=0, lfosC=0, modM=0,
                          prio=0, echoV=0, echoL=0, chans=[], key=60, idx=i, volMR=0, volML=0, keyM=0, pitM=0))
        ds = [Chan() for _ in range(MAX_DS)]
        cgb = [Chan() for _ in range(4)]
        out_l = np.zeros(frames * SPF, np.float32)
        out_r = np.zeros(frames * SPF, np.float32)
        ring_l = np.zeros(DMA_PERIOD * SPF, np.float32)    # the DMA buffers (reverb reads them back)
        ring_r = np.zeros(DMA_PERIOD * SPF, np.float32)
        tick = 0
        tempo_c = 0
        cgb_buf_rate = 4 * MIX_HZ

        def trk_volpit(t):
            x = (t['vol'] * t['volX']) >> 5
            if t['modT'] == 1: x = (x * (t['modM'] + 128)) >> 7
            y = 2 * t['pan'] + t['panX']
            if t['modT'] == 2: y += t['modM']
            y = max(-128, min(127, y))
            t['volMR'] = ((y + 128) * x) >> 8
            t['volML'] = ((127 - y) * x) >> 8
            p = (t['tune'] + t['bend'] * t['bendr']) * 4 + (t['keysh'] << 8)
            if t['modT'] == 0: p += 16 * t['modM']
            t['keyM'], t['pitM'] = p >> 8, p & 0xFF

        def chan_vol(c, t):
            c.rvol = min(255, (c.vel * (0x80 + c.rpan) * t['volMR']) >> 14)
            c.lvol = min(255, (c.vel * (0x7F - c.rpan) * t['volML']) >> 14)

        def chan_freq(c, t):
            k = max(0, c.key + t['keyM']) + t['pitM'] / 256
            if c.kind == 0:
                c.freq = c.wavinfo['freq'] * 2 ** ((k - 60) / 12)
            elif c.kind in (1, 2, 3):
                c.freq = 440 * 2 ** ((k - 69) / 12)
            else:
                c.freq = k

        def note_on(t, key, vel, gate):
            v = self.rom.voice(self.vg, t['voice'])
            tone, play_key = self.rom.resolve(self.vg, t['voice'], key)
            if tone['type'] & 0xC0: return
            rpan = 0
            if v['type'] & 0x80 and tone['pan_sweep'] & 0x80: rpan = (tone['pan_sweep'] - 0xC0) * 2
            prio = min(255, t['prio'])
            kind = tone['type'] & 7
            if kind == 0:
                pick = next((c for c in ds if not c.on), None)
                if pick is None:
                    stopping = [c for c in ds if c.stop]
                    if stopping: pick = min(stopping, key=lambda c: c.prio)
                    else:
                        low = min(ds, key=lambda c: (c.prio, -c.track['idx']))
                        if low.prio > prio or (low.prio == prio and low.track['idx'] < t['idx']): return
                        pick = low
            else:
                c0 = cgb[kind - 1]
                if c0.on and not c0.stop and (c0.prio > prio or (c0.prio == prio and c0.track['idx'] < t['idx'])):
                    return
                pick = c0
            c = pick
            if c.on and c in c.track['chans']: c.track['chans'].remove(c)
            c.on, c.stop, c.track, c.kind = True, False, t, kind
            c.key, c.midi_key, c.vel, c.rpan, c.prio, c.gate = play_key, key, vel, rpan, prio, gate
            c.a, c.d, c.s, c.r = tone['attack'], tone['decay'], tone['sustain'], tone['release']
            c.echoV, c.echoL = t['echoV'], t['echoL']
            c.state, c.env, c.phase = 'attack', 0, 0.0
            c.fixed = bool(tone['type'] & 8) and kind == 0
            if kind == 0:
                c.data, c.wavinfo = self.wavedata(tone['wav'])
            elif kind in (1, 2):
                c.duty = [0.125, 0.25, 0.5, 0.75][tone['wav'] & 3]
            elif kind == 3:
                raw = self.rom.d[tone['wav'] & 0x1FFFFFF:(tone['wav'] & 0x1FFFFFF) + 16]
                c.wave4 = np.array([n for b in raw for n in (b >> 4, b & 15)], np.float32)
                c.wavinfo = None
            t['chans'].append(c)
            if t['lfodl']:
                t['lfodlC'] = t['lfodl']; t['modM'] = 0; t['lfosC'] = 0
            trk_volpit(t); chan_vol(c, t); chan_freq(c, t)

        for f in range(frames):
            tempo_c += tempo_d
            while tempo_c >= 150:
                for t in T:
                    for c in list(t['chans']):
                        if c.on and not c.stop and c.gate:
                            c.gate -= 1
                            if c.gate == 0: c.stop = True
                    ev = t['ev']
                    while t['pos'] < len(ev) and ev[t['pos']][1] == tick:
                        e = ev[t['pos']]; t['pos'] += 1
                        k = e[0]
                        if k == 'note':
                            if (self.solo is None or t['idx'] == self.solo) and \
                                    (getattr(self, 'solo_voice', None) is None or t['voice'] == self.solo_voice):
                                note_on(t, e[2], e[3], e[4])
                        elif k == 'eot':
                            for c in t['chans']:
                                if c.on and not c.stop and c.midi_key == e[2]: c.stop = True; break
                        elif k == 'voice': t['voice'] = e[2]
                        elif k == 'vol': t['vol'] = e[2]
                        elif k == 'pan': t['pan'] = e[2] - 64
                        elif k == 'bend': t['bend'] = e[2] - 64
                        elif k == 'bendr': t['bendr'] = e[2]
                        elif k == 'keysh': t['keysh'] = e[2] - 256 if e[2] > 127 else e[2]
                        elif k == 'tune': t['tune'] = e[2] - 64
                        elif k == 'mod':
                            t['mod'] = e[2]
                            if not e[2]: t['modM'] = 0; t['lfosC'] = 0
                        elif k == 'lfos':
                            t['lfos'] = e[2]
                            if not e[2]: t['modM'] = 0; t['lfosC'] = 0
                        elif k == 'lfodl': t['lfodl'] = e[2]
                        elif k == 'modt': t['modT'] = e[2]
                        elif k == 'prio': t['prio'] = e[2]
                        elif k == 'tempo': tempo_d = e[2] * 2
                        elif k == 'xcmd':
                            if e[2] == 8: t['echoV'] = e[3][0]
                            elif e[2] == 9: t['echoL'] = e[3][0]
                    if t['lfos'] and t['mod']:
                        if t['lfodlC']: t['lfodlC'] -= 1
                        else:
                            t['lfosC'] = (t['lfosC'] + t['lfos']) & 0xFF
                            sc = t['lfosC']
                            tri = (sc if sc < 0x80 else sc - 256) if ((sc - 0x40) & 0xFF) >= 0x80 else 0x80 - sc
                            t['modM'] = (t['mod'] * tri) >> 6
                tick += 1
                tempo_c -= 150
            for t in T:
                trk_volpit(t)
                t['chans'] = [c for c in t['chans'] if c.on]
                for c in t['chans']: chan_vol(c, t); chan_freq(c, t)
            # ---- DirectSound: envelope per frame, then mix SPF samples
            mix_l = np.zeros(SPF, np.float32); mix_r = np.zeros(SPF, np.float32)
            for c in ds:
                if not c.on: continue
                if c.state == 'echo':
                    c.echoL -= 1
                    if c.echoL <= 0: c.on = False; continue
                elif c.stop:
                    c.env = (c.env * c.r) >> 8
                    if c.env <= c.echoV:
                        if c.echoV == 0: c.on = False; continue
                        c.env = c.echoV; c.state = 'echo'
                elif c.state == 'attack':
                    c.env += c.a
                    if c.env >= 255: c.env = 255; c.state = 'decay'
                elif c.state == 'decay':
                    c.env = (c.env * c.d) >> 8
                    if c.env <= c.s:
                        c.env = c.s
                        if c.s == 0:
                            if c.echoV: c.env = c.echoV; c.state = 'echo'
                            else: c.on = False; continue
                        else: c.state = 'sustain'
                e2 = (c.env * (MASTER + 1)) >> 4
                vr, vl = (c.rvol * e2) >> 8, (c.lvol * e2) >> 8
                step = 1.0 if c.fixed else c.freq / MIX_HZ
                n = len(c.data)
                idx = c.phase + step * np.arange(SPF)
                info = c.wavinfo
                if info['loop'] and n > info['loop_start']:
                    ls = info['loop_start']
                    over = idx >= n
                    idx = np.where(over, ls + np.mod(idx - ls, n - ls), idx)
                    valid = np.ones(SPF, bool)
                else:
                    valid = idx < n - 1
                i0 = np.minimum(idx.astype(np.int64), n - 1)
                i1 = np.minimum(i0 + 1, n - 1)
                fr = idx - np.floor(idx)
                smp = (c.data[i0] * (1 - fr) + c.data[i1] * fr) * valid
                mix_r += smp * vr / 256
                mix_l += smp * vl / 256
                c.phase = float(idx[-1] + step)
                if info['loop'] and c.phase >= n: c.phase = info['loop_start'] + (c.phase - info['loop_start']) % (n - info['loop_start'])
                if not info['loop'] and c.phase >= n - 1: c.on = False
            # reverb: this slot's previous contents and the next slot (the oldest), mono, * reverb / 512
            slot = f % DMA_PERIOD
            a, b = slot * SPF, ((slot + 1) % DMA_PERIOD) * SPF
            if self.reverb:
                rv = (ring_l[a:a + SPF] + ring_r[a:a + SPF] + ring_l[b:b + SPF] + ring_r[b:b + SPF]) * self.reverb / 512
                base_l, base_r = rv.copy(), rv.copy()
            else:
                base_l = np.zeros(SPF, np.float32); base_r = np.zeros(SPF, np.float32)
            buf_l = np.clip(base_l + mix_l, -128, 127); buf_r = np.clip(base_r + mix_r, -128, 127)
            ring_l[a:a + SPF], ring_r[a:a + SPF] = buf_l, buf_r
            # ---- CGB channels (rendered at the same rate, envelope 0-15 per frame)
            cg_l = np.zeros(SPF, np.float32); cg_r = np.zeros(SPF, np.float32)
            for i, c in enumerate(cgb):
                if not c.on: continue
                goal = min(15, (c.lvol + c.rvol) // 16)     # CgbModVol: envelopeGoal
                if c.stop:
                    if c.r == 0: c.on = False; continue
                    c.cnt = getattr(c, 'cnt', c.r) - 1
                    if c.cnt <= 0:
                        c.env -= 1; c.cnt = c.r
                        if c.env <= 0: c.on = False; continue
                elif c.state == 'attack':
                    if c.a == 0: c.env = goal; c.state = 'decay'; c.cnt = c.d
                    else:
                        c.cnt = getattr(c, 'cnt', c.a) - 1
                        if c.cnt <= 0:
                            c.env += 1; c.cnt = c.a
                            if c.env >= goal: c.env = goal; c.state = 'decay'; c.cnt = c.d
                elif c.state == 'decay':
                    sus = (goal * c.s + 15) >> 4
                    if c.d == 0: c.env = sus; c.state = 'sustain'
                    else:
                        c.cnt -= 1
                        if c.cnt <= 0:
                            c.env -= 1; c.cnt = c.d
                            if c.env <= sus:
                                c.env = sus; c.state = 'sustain'
                                if c.s == 0: c.on = False; continue
                else:
                    c.env = (goal * c.s + 15) >> 4
                ph = c.phase + c.freq / MIX_HZ * np.arange(SPF)
                if c.kind in (1, 2):
                    w = np.where(np.mod(ph, 1.0) < c.duty, 1.0, -1.0)
                elif c.kind == 3:
                    w = (c.wave4[(np.mod(ph, 1.0) * 32).astype(int)] - 7.5) / 7.5
                else:
                    w = np.random.uniform(-1, 1, SPF)
                c.phase = float(np.mod(ph[-1] + c.freq / MIX_HZ, 1.0))
                # a PSG channel swings 0..15 * (NR50 7 + 1) = 0..120 (GBATEK), a DMA FIFO at 100% -512..511 for
                # the 8-bit sample: so +-60/4 = +-15 in 8-bit sample units at volume 15
                amp = min(15, c.env)
                if c.rvol >= c.lvol and c.rvol // 2 >= c.lvol: cg_r += w * amp
                elif c.lvol > c.rvol and c.lvol // 2 >= c.rvol: cg_l += w * amp
                else: cg_l += w * amp; cg_r += w * amp
            out_l[f * SPF:(f + 1) * SPF] = buf_l + cg_l
            out_r[f * SPF:(f + 1) * SPF] = buf_r + cg_r
        return out_l, out_r


def write_wav(path, left, right, rate=MIX_HZ, out_rate=OUT_HZ):
    n = len(left)
    t_out = np.arange(int(n * out_rate / rate)) * rate / out_rate
    l = np.interp(t_out, np.arange(n), left); r = np.interp(t_out, np.arange(n), right)
    peak = max(1e-9, np.abs(np.concatenate([l, r])).max())
    scale = 32767 * 0.9 / peak
    pcm = np.stack([l * scale, r * scale], 1).astype('<i2')
    w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(out_rate)
    w.writeframes(pcm.tobytes()); w.close()


def main(argv):
    name, out = argv[0], argv[1]
    secs = float(argv[2]) if len(argv) > 2 else 65
    rom = m4a.GbaRom()
    r = Renderer(rom, rom.song_index(name))
    l, rr = r.render(secs)
    write_wav(out, l, rr)
    print(out, f'{secs:.0f} s')


if __name__ == '__main__':
    main(sys.argv[1:])
