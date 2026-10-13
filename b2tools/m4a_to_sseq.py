"""Convert a Ruby/Sapphire song (M4A sequence in the GBA ROM) into a Black 2 sequence (SSEQ) played on Black 2's own
instruments, with a bank and wave archive cut from Black 2's instrument library (notes/MUSIC.md).

    python3 m4a_to_sseq.py SONG [OUT_DIR]      e.g. mus_littleroot -> OUT_DIR/SONG.{sseq,sbnk,swar,txt}
    python3 m4a_to_sseq.py --all [OUT_DIR]     every song of SONGS, with a summary (sizes, instruments)

What is kept: every note (key, velocity, length; TIE/EOT become lengths), the tempo, the loop (each track's GOTO back
to its loop label becomes a jump to the same tick), track volume, pan, key shift, pitch bend and bend range, and the
vibrato (MOD/LFOS/LFODL/MODT, converted approximately). Not kept: the GBA's pseudo-echo (XCMD xIECV/xIECL; Black 2's
instruments have their own release), TUNE, PRIO and MEMACC, the voices' own GBA envelopes.

Instruments (data/hoenn_music.json): each GBA part (one voice in one track) gets a program of Black 2's instrument
library: by the GBA sample's name ("defaults"), by its role for the parts Black 2 has no equivalent for (square waves,
the programmable wave: music_roles.py; "roles", per context: field or battle), noise as the drum kit's hi-hats
("noise"), the drum kit key for key (both kits are General MIDI; "drums" fixes the odd ones), and per song by voice or
by part ("songs" ... "voices" / "parts"). Balance: each part's notes are scaled so Black 2's level / the GBA's level is
the same for every part (data/hoenn_music_levels.json: every program measured in game, b2tools/music_calib.py; the GBA
voice rendered by m4a_render), then "gain" / "track_gain" if set by hand. Loudness: "volume" (the sequence's INFO
volume, linear) per context, and per song.

Units: SSEQ ticks are 48 per quarter note, M4A's 24, so every time doubles. M4A's TEMPO byte is bpm/2 at 59.7275
frames per second; NitroSDK's sequencer runs 192 updates per second (64 * 2728 cycles at 33.51 MHz) and ticks every
240 tempo units, so the SSEQ tempo is round(2 * byte * 0.99576). Volumes and velocities: the GBA mixes them linearly,
Black 2 through a decibel table on a squared curve (40 log10(v/127), measured: notes/MUSIC.md), so v' = 127 sqrt(v/127).
"""
import json, math, os, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import m4a  # noqa: E402
import sseq  # noqa: E402
import music_roles  # noqa: E402
from sdat import SDAT, DEFAULT, parse_sbnk, build_sbnk, parse_swar, build_swar  # noqa: E402

MAPPING = os.path.join(ROOT, 'data', 'hoenn_music.json')
LEVELS = os.path.join(ROOT, 'data', 'hoenn_music_levels.json')
# pokeruby songs no map, battle or event of Ruby/Sapphire plays (test songs, Gold/Silver leftovers, link contests)
UNUSED = {'mus_dummy', 'mus_littleroot_test', 'mus_gsc_route38', 'mus_gsc_pewter', 'mus_c_comm_center',
          'mus_c_vs_legend_beast', 'mus_link_contest_p1', 'mus_link_contest_p2', 'mus_link_contest_p3',
          'mus_link_contest_p4', 'mus_radio_tower_takeover'}
SONGS = [n for n in re.findall(r'^\s*song\s+(mus_\w+),', open(os.path.join(m4a.PRUBY, 'sound', 'song_table.inc')).read(), re.M)
         if n not in UNUSED]
NDS_UPDATES_PER_SEC = 33513982 / (64 * 2728)          # 191.95: sequencer and LFO updates
PSG_DUTY = {0: 101, 1: 102, 2: 104, 3: 106}           # GBA duty 12.5/25/50/75 % -> library PSG programs (NDS duty 0/1/3/5)


def sqrt_curve(v, gain=1.0):
    return max(0, min(127, round(127 * math.sqrt(max(0.0, min(1.0, v * gain / 127))))))


def load_mapping(path=MAPPING):
    return json.load(open(path))


GAINS = os.path.join(ROOT, 'data', 'hoenn_music_gains.json')


def load_levels(path=LEVELS):
    """The calibration (music_calib.py), with the per-part gains (music_calib.py --gains) as 'gains_table'."""
    if not os.path.exists(path): return None
    lv = json.load(open(path))
    if os.path.exists(GAINS): lv['gains_table'] = json.load(open(GAINS))['gains']
    return lv


def voice_key(rom, vg, v):
    """The mapping key of a GBA voice: its sample name without the key suffix, or square / wave / noise / drums."""
    t = rom.voice(vg, v)
    if t['type'] & 0x80: return 'drums'
    if t['type'] & 0x40:
        t = rom.tone(t['wav'] + 12 * rom.d[(t['keysplit'] + 60) & 0x1FFFFFF])
    kind = t['type'] & 7
    if kind == 0: return re.sub(r'_\d+$', '', rom.sample_name(t['wav']))
    return {1: 'square', 2: 'square', 3: 'wave', 4: 'noise'}[kind]


_GBA_LEVEL = {}


def gba_level(rom, vg, voice, key, gate):
    """RMS of one GBA note (velocity 100, VOL 100, 120 bpm) over 1.2 s, as m4a_render plays it."""
    k = (vg, voice, key, gate)
    if k not in _GBA_LEVEL:
        import numpy as np
        import m4a_render
        l, r = m4a_render.Renderer.phrase(rom, vg, voice, key, gate).render(1.2)
        _GBA_LEVEL[k] = float(np.sqrt(((l ** 2 + r ** 2) / 2).mean()))
    return _GBA_LEVEL[k]


def b2_level(levels, prog, key, gate):
    """Black 2's measured level of `prog` (velocity 113 = sqrt-curve 100, volume 113, INFO 100) at key and gate (GBA
    ticks), interpolated over the calibration grid in key and log(gate); drum kit programs per key."""
    tab = levels['programs'].get(str(prog))
    if not tab: return None
    pts = {tuple(map(int, k.split(','))): v for k, v in tab.items()}
    keys = sorted({k for k, g in pts}); gates = sorted({g for k, g in pts})
    if len(keys) == 1 or prog == levels.get('drum_program', 80):
        kk = min(keys, key=lambda x: abs(x - key))
        return pts.get((kk, gates[0]))

    def bracket(vals, x):
        if x <= vals[0]: return vals[0], vals[0], 0.0
        if x >= vals[-1]: return vals[-1], vals[-1], 0.0
        for a, b in zip(vals, vals[1:]):
            if a <= x <= b: return a, b, (x - a) / (b - a)
    k0, k1, fk = bracket(keys, key)
    lg = [math.log(g) for g in gates]
    g0, g1, fg = bracket(lg, math.log(max(1, gate)))
    G = {math.log(g): g for g in gates}

    def at(k, g):
        v = pts.get((k, G[g]))
        return math.log(max(v, 1e-6)) if v else None
    vals = [(at(k0, g0), (1 - fk) * (1 - fg)), (at(k1, g0), fk * (1 - fg)), (at(k0, g1), (1 - fk) * fg), (at(k1, g1), fk * fg)]
    vals = [(v, w) for v, w in vals if v is not None]
    if not vals: return None
    tw = sum(w for v, w in vals) or 1
    return math.exp(sum(v * w for v, w in vals) / tw) if tw else math.exp(vals[0][0])


class Song:
    def __init__(self, name, rom=None, mapping=None, sdat=None, levels=None):
        self.rom = rom or m4a.GbaRom()
        self.map = mapping or load_mapping()
        self.sdat = sdat or SDAT(open(DEFAULT, 'rb').read())
        self.levels = levels if levels is not None else load_levels()
        self.name = name
        self.n = self.rom.song_index(name)
        self.cfg = self.map['songs'].get(name, {})
        self.context = self.cfg.get('context') or music_roles.song_context(name)
        self.header, self.tracks, self.parts = music_roles.parts(self.rom, name)
        self.roles = {k: music_roles.role(k, p, self.parts) for k, p in self.parts.items()}
        self.notes_used = {}           # program -> set of keys
        self.report = []
        self.solo = None               # analysis only: keep the notes of this track alone
        self.decisions = {}            # (track, voice) -> dict(program, why, gain, ...)

    # ---- instruments
    def part_map(self, track, v):
        """The Black 2 instrument of GBA voice v in track `track`: dict(program, why, kind, drum_key, transpose, gain)."""
        key = (track, v)
        if key in self.decisions: return self.decisions[key]
        vg = self.header['voicegroup']
        vk = voice_key(self.rom, vg, v)
        p = self.parts.get(key, dict(kind='sample', notes=[]))
        role, st = self.roles.get(key, ('lead', {}))
        m, why = {}, ''
        over = self.cfg.get('parts', {}).get(f't{track}v{v}') or self.cfg.get('voices', {}).get(str(v))
        if vk == 'drums':
            m, why = dict(self.map['defaults']['drums']), 'drum kit, key for key'
        elif vk == 'noise':
            m, why = dict(program=self.map['defaults']['drums']['program']), 'noise -> drum kit hi-hats'
            m['noise'] = self.map['noise']
        elif vk in ('square', 'wave'):
            r = self.map['roles'][self.context][vk][role]
            if isinstance(r, list):
                r = next(x[1] for x in r if st.get('key', 60) >= x[0])
            if r == 'psg':
                m = dict(program=PSG_DUTY[p.get('duty') or 2])
            else:
                m = dict(program=r) if isinstance(r, int) else dict(r)
            why = f'{vk} {role} ({self.context})'
        else:
            if vk not in self.map['defaults']:
                raise SystemExit(f'{self.name}: GBA voice {v} ({vk}) has no Black 2 instrument in {MAPPING}')
            m, why = dict(self.map['defaults'][vk]), f'default for {vk}'
        if over:
            m.update({k: x for k, x in over.items() if k != 'why'})
            why = over.get('why', 'set for this song')
        m.update(why=why, vk=vk, role=role, stats=st)
        m['gain_auto'] = self.auto_gain(track, v, m)
        self.decisions[key] = m
        return m

    def auto_gain(self, track, v, m):
        """Scale so that Black 2 level / GBA level is the library's reference ratio (data/hoenn_music_levels.json).
        Drums and noise: per played key, weighted by its notes."""
        if not self.levels or self.cfg.get('no_auto_gain') or not self.levels.get('programs'): return 1.0
        tab = self.levels.get('gains_table')
        if tab and f'{self.name}:t{track}v{v}' in tab: return tab[f'{self.name}:t{track}v{v}']
        p = self.parts.get((track, v))
        if not p or not p['notes']: return 1.0
        vg = self.header['voicegroup']
        if m['vk'] == 'drums' or m.get('noise') or m.get('drum_key'):
            drums = {int(k): x for k, x in {**self.map.get('drum_keys', {}), **self.cfg.get('drums', {})}.items()}
            gs = bs = 0.0
            counts = {}
            for x in p['notes']: counts[(x[1], min(x[3], 96))] = counts.get((x[1], min(x[3], 96)), 0) + 1
            for (k, gate), c in counts.items():
                if m['vk'] == 'drums': bk = drums.get(k, k)
                elif m.get('noise'): bk = m['noise']['long'] if gate >= m['noise']['long_gate'] else m['noise']['short']
                else: bk = m['drum_key']
                g = gba_level(self.rom, vg, v, k, gate if m.get('noise') or m.get('drum_key') else 6)
                b = b2_level(self.levels, m['program'], bk, 6)
                if g and b: gs += c * g; bs += c * b
            return max(0.1, min(4.0, self.levels['ratio'] * gs / bs)) if bs else 1.0
        keys = [x[1] for x in p['notes']]
        gates = [x[3] for x in p['notes']]
        key = int(statistics.median(keys)); gate = int(statistics.median(gates))
        g = gba_level(self.rom, vg, v, key, gate)
        b = b2_level(self.levels, m['program'], key + m.get('transpose', 0), gate)
        if not g or not b: return 1.0
        return max(0.1, min(4.0, self.levels['ratio'] * g / b))

    # ---- the sequence
    def build_sseq(self):
        w = sseq.Writer()
        tempo_byte = None
        for tr in self.tracks:
            for e in tr.events:
                if e[0] == 'tempo': tempo_byte = tempo_byte or e[2]
        ticks_per_sec = (tempo_byte or 75) * 2 * m4a.FRAME_HZ / 150
        # a song whose gains need more than velocity 127: every part down, the INFO volume up (song_scale)
        for i, tr in enumerate(self.tracks):
            for e in tr.events:
                if e[0] == 'voice': self.part_map(i, e[2])
        self.song_scale = 1.0
        peak = max([self.total_gain(k, m) for k, m in self.decisions.items()] + [1.0])
        if peak > 1.25: self.song_scale = 1.25 / peak
        for i, tr in enumerate(self.tracks):
            self._track(w.track(), tr, i, ticks_per_sec)
        return w.sseq()

    def total_gain(self, key, m):
        tg = self.cfg.get('track_gain', {}).get(str(key[0]), 1.0)
        return m['gain_auto'] * m.get('gain', 1.0) * tg

    def _track(self, tw, tr, idx, ticks_per_sec):
        ev = tr.events
        ends, open_ties = {}, {}
        for j, e in enumerate(ev):
            if e[0] == 'note' and e[4] == 0: open_ties.setdefault(e[2], []).append(j)
            elif e[0] == 'eot' and open_ties.get(e[2]):
                ends[open_ties[e[2]].pop(0)] = e[1]
        voice, keysh, mapping = None, 0, None
        tw.cmd('note_wait', 0)
        tw.cmd('priority', 64)
        tw.cmd('bend_range', 2)                   # M4A's track default (MPlayMain: bendRange = 2)
        t_out = 0
        loop_at = None
        once = self.cfg.get('once', False)
        drums = {int(k): v for k, v in {**self.map.get('drum_keys', {}), **self.cfg.get('drums', {})}.items()}
        cur_prog = None
        for j, e in enumerate(ev):
            t = e[1] * 2
            if j == tr.loop_event:
                tw.wait(tr.loop_tick * 2 - t_out); t_out = tr.loop_tick * 2
                loop_at = tw.here()
            if t > t_out:
                tw.wait(t - t_out); t_out = t
            kind = e[0]
            if kind == 'voice':
                voice = e[2]; mapping = self.part_map(idx, voice)
                if mapping['program'] != cur_prog:
                    tw.program(mapping['program']); cur_prog = mapping['program']
            elif kind == 'tempo':
                tw.cmd('tempo', round(e[2] * 2 * 0.99576))
            elif kind == 'vol':
                tw.cmd('volume', sqrt_curve(e[2], self.cfg.get('level', 1.0)))
            elif kind == 'pan':
                tw.cmd('pan', e[2])
            elif kind == 'keysh':
                keysh = e[2] - 256 if e[2] > 127 else e[2]
            elif kind == 'bend':
                tw.cmd('bend', max(-128, min(127, (e[2] - 64) * 2)))
            elif kind == 'bendr':
                tw.cmd('bend_range', e[2])
            elif kind == 'mod':
                tw.cmd('mod_depth', min(127, round(e[2] * 8.6)))
            elif kind == 'lfos':
                hz = ticks_per_sec * e[2] / 256
                tw.cmd('mod_speed', max(1, min(127, round(hz / (NDS_UPDATES_PER_SEC / 512)))))
            elif kind == 'lfodl':
                tw.cmd('mod_delay', round(e[2] / ticks_per_sec * NDS_UPDATES_PER_SEC))
            elif kind == 'modt':
                tw.cmd('mod_type', min(2, e[2]))
            elif kind == 'note':
                if self.solo is not None and idx != self.solo: continue
                if mapping is None:
                    voice = 0; mapping = self.part_map(idx, 0)
                key, vel, gate = e[2], e[3], e[4]
                if gate == 0:
                    gate = ends.get(j, tr.end_tick) - e[1]
                    if gate <= 0: continue
                if mapping['vk'] == 'drums':
                    k = drums.get(key, key)
                elif mapping.get('noise'):
                    nz = mapping['noise']
                    k = nz['long'] if gate >= nz['long_gate'] else nz['short']
                elif mapping.get('drum_key'):
                    k = mapping['drum_key']
                else:
                    k = key + keysh + mapping.get('transpose', 0)
                if not 0 <= k <= 127: continue
                prog = mapping['program']
                if cur_prog != prog:
                    tw.program(prog); cur_prog = prog
                self.notes_used.setdefault(prog, {}); self.notes_used[prog][k] = self.notes_used[prog].get(k, 0) + 1
                g = self.total_gain((idx, voice), mapping) * self.song_scale
                tw.note(k, max(1, sqrt_curve(vel, g)), gate * 2)
        # data "songs" {"loop": true}: a song that ends in Sapphire loops from its start, every track at the song's end
        # (the credits: Black 2's run longer than Sapphire's song; check_waits' "not_waited" lets SEQ_BGM_ENDING loop)
        force_loop = self.cfg.get('loop', False) and tr.loop_tick is None
        end = (max(x.end_tick for x in self.tracks) if force_loop else tr.end_tick) * 2
        if end > t_out: tw.wait(end - t_out)
        if (tr.loop_tick is not None or force_loop) and not once:
            tw.jump(loop_at if loop_at is not None else 0)
        else:
            tw.end()

    # ---- the bank and wave archive
    def build_bank(self, budget=None):
        """The song's bank and wave archive from the library: the programs it plays, only the key-split regions and drum
        keys it uses. Over `budget` bytes (SSEQ + SBNK + SWAR; data 'budget'), key-split regions are merged into a
        neighbour (its sample then plays those notes, further from its own pitch), cheapest first: the fewest notes x
        semitones moved per byte saved."""
        s = self.sdat
        li = s.index('bank', self.map['library'])
        lib = parse_sbnk(s.bank(li))
        lib_waves = parse_swar(s.wavearc(s.info['bank'][li]['wavearcs'][0]))
        budget = budget or self.cfg.get('budget', self.map.get('budget', 242000))
        kept = {}
        for prog, keys in self.notes_used.items():
            t, regs = lib[prog]
            if t == 17:
                kept[prog] = [list(r) for r in regs if any(r[0] <= k <= r[1] for k in keys)]

        def waves_total():
            ws = set()
            for prog, keys in self.notes_used.items():
                t, regs = lib[prog]
                if t == 17: ws |= {r[3] for r in kept[prog] if r[2] == 1}
                elif t == 16: ws |= {r[3] for r in regs if r[0] in keys}
                elif regs[0][2] == 1: ws.add(regs[0][3])
            return sum(len(lib_waves[w]) + 3 & ~3 for w in ws)

        self.merged = []
        while waves_total() + getattr(self, 'seq_size', 0) + 64 * len(self.notes_used) > budget:
            best = None
            for prog, regs in kept.items():
                if len(regs) < 2: continue
                for i, r in enumerate(regs):
                    played = {k: c for k, c in self.notes_used[prog].items() if r[0] <= k <= r[1]}
                    for j in (i - 1, i + 1):
                        if not 0 <= j < len(regs): continue
                        base = regs[j][5]
                        cost = sum(c * abs(k - base) for k, c in played.items()) / len(lib_waves[r[3]])
                        if best is None or cost < best[0]: best = (cost, prog, i, j)
            if best is None: break
            _, prog, i, j = best
            regs = kept[prog]
            r, nb = regs[i], regs[j]
            if j < i: nb[1] = r[1]                      # the lower neighbour takes the removed region's top
            else: nb[0] = r[0]
            self.merged.append(f'{prog}: {r[0]}-{r[1]}@{r[5]} -> @{nb[5]}')
            del regs[i]
        used_waves, out = [], {}

        def wave(idx):
            if idx not in used_waves: used_waves.append(idx)
            return used_waves.index(idx)

        for prog, keys in sorted(self.notes_used.items()):
            t, regs = lib[prog]
            if t == 16:                                    # drum set: only the played keys' range
                lo, hi = min(keys), max(keys)
                by_key = {r[0]: r for r in regs}
                missing = [k for k in keys if k not in by_key]
                if missing: raise SystemExit(f'{self.name}: drum keys {missing} not in program {prog}')
                new = []
                for k in range(lo, hi + 1):
                    src = by_key[k] if k in keys else by_key[min(keys, key=lambda x: abs(x - k))]
                    new.append((k, k, src[2], wave(src[3]), 0) + tuple(src[5:]))
                out[prog] = (16, new)
            elif t == 17:
                new = [(r[0], r[1], r[2], wave(r[3]) if r[2] == 1 else r[3], 0) + tuple(r[5:]) for r in kept[prog]]
                out[prog] = (17, new)
            else:
                r = regs[0]
                out[prog] = (t, [(0, 127, r[2], wave(r[3]) if r[2] == 1 else r[3], 0) + tuple(r[5:])])
        return build_sbnk(out), build_swar([lib_waves[i] for i in used_waves]), used_waves

    def volume(self):
        """The INFO volume (linear): per context (data 'volume'), per song, divided by song_scale; what is left above
        127 goes to the track volumes ("level")."""
        base = self.cfg.get('volume', self.map['volume'].get(self.context, 100))
        v = base / self.song_scale
        if v > 127:
            self.cfg = dict(self.cfg, level=self.cfg.get('level', 1.0) * v / 127)
            v = 127
        return int(round(v))

    def convert(self):
        data = self.build_sseq()
        vol = self.volume()
        if self.cfg.get('level', 1.0) != 1.0:          # 'level' changed by volume(): write the track volumes again
            self.notes_used = {}
            data = self.build_sseq()
        self.seq_size = len(data)
        bank, swar, waves = self.build_bank()
        self.info_volume = vol
        h = self.header
        vg = h['voicegroup']
        size = len(data) + len(bank) + len(swar)
        rep = [f'{self.name} (song {self.n}, {self.context}): {h["tracks"]} tracks, loop {self.tracks[0].loop_tick} -> '
               f'{self.tracks[0].end_tick} GBA ticks; SSEQ {len(data)} B, SBNK {len(bank)} B, SWAR {len(swar)} B '
               f'({len(waves)} waves): {size} B loaded; INFO volume {vol}, scale {self.song_scale:.2f}'
               + (f'; merged to fit: {", ".join(self.merged)}' if self.merged else '')]
        names = self.map.get('instruments', {})
        for (t, v), m in sorted(self.decisions.items()):
            st = m.get('stats') or {}
            rep.append(f'  t{t} v{v:3d} {self.rom.describe_voice(vg, v)[:40]:40s} {m["role"] if m["vk"] in ("square", "wave") else "":8s}'
                       f' -> {m["program"]:3d} {names.get(str(m["program"]), "")[:28]:28s} gain {self.total_gain((t, v), m) * self.song_scale:.2f}'
                       f' ({m["why"]}; {st.get("n", 0)} notes, key {st.get("key", "-")})')
        self.report = rep
        self.size = size
        return data, bank, swar


def main(argv):
    if argv and argv[0] == '--all':
        out = argv[1] if len(argv) > 1 else os.path.join(ROOT, 'work', 'agents', 'music_check', 'out', 'all')
        os.makedirs(out, exist_ok=True)
        rom, mp, sd, lv = m4a.GbaRom(), load_mapping(), SDAT(open(DEFAULT, 'rb').read()), load_levels()
        tot = 0
        lines = []
        for name in SONGS:
            song = Song(name, rom=rom, mapping=mp, sdat=sd, levels=lv)
            data, bank, swar = song.convert()
            for ext, b in (('sseq', data), ('sbnk', bank), ('swar', swar)):
                open(os.path.join(out, f'{name}.{ext}'), 'wb').write(b)
            lines += song.report
            tot += song.size
            print(f'{name:30s} {song.size:7d} B  vol {song.info_volume:3d}  {len(song.notes_used)} programs'
                  + (f'  merged {len(song.merged)}' if song.merged else ''))
        open(os.path.join(out, 'report.txt'), 'w').write('\n'.join(lines) + '\n')
        print(f'{len(SONGS)} songs, {tot:,} B')
        return
    name = argv[0] if argv else 'mus_littleroot'
    out = argv[1] if len(argv) > 1 else os.path.join(ROOT, 'work', 'agents', 'music_check', 'out')
    os.makedirs(out, exist_ok=True)
    song = Song(name)
    data, bank, swar = song.convert()
    for ext, b in (('sseq', data), ('sbnk', bank), ('swar', swar)):
        open(os.path.join(out, f'{name}.{ext}'), 'wb').write(b)
    open(os.path.join(out, f'{name}.txt'), 'w').write('\n'.join(song.report) + '\n')
    print('\n'.join(song.report))


if __name__ == '__main__':
    main(sys.argv[1:])
