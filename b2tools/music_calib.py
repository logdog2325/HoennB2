"""Measure every Black 2 library instrument the converted songs play, in game, for m4a_to_sseq.py's automatic balance
(data/hoenn_music_levels.json; notes/MUSIC.md "Balance").

    python3 music_calib.py BASE.nds TEST.nds         (run with ../.venv/bin/python; TEST.nds needs a battery save in
                                                      Littleroot: music_record.py save)

For each program the songs use: one note at each grid key near the keys it plays (36 ... 96) and each grid length
(6, 24, 96 GBA ticks = 12, 48, 192 SSEQ ticks at 120 bpm), velocity 113 and track volume 113 (the converter's sqrt
curve of 100), INFO volume 100; the drum kit per key played. The notes go into batches of at most ~200 KB of samples,
each installed into Littleroot's slot of TEST.nds (patches/hoenn_music.py install_in_place on BASE.nds's sound archive)
and recorded from a cold boot (music_record.py). A note's level is its RMS over 1.2 s from its start (the same window
m4a_to_sseq.gba_level uses for the GBA voice). "ratio" is the median of Black 2 / GBA over all the songs' parts, so
the median part keeps its velocities.
"""
import json, math, os, subprocess, sys, wave, statistics
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import m4a, sseq, m4a_to_sseq as conv  # noqa: E402
from sdat import SDAT, DEFAULT, parse_sbnk, parse_swar, build_sbnk, build_swar  # noqa: E402

GRID_KEYS = [36, 48, 60, 72, 84, 96]
GRID_GATES = [6, 24, 96]
SEG = 288                     # SSEQ ticks per note slot: 3 s at 120 bpm (the longest note, 2 s, and its release end inside it)
VEL = conv.sqrt_curve(100)    # 113
WAVE_BUDGET = 200000
SLOT = 1172


def usage(rom, mp, sd):
    """{program: Counter of keys} over all songs, and every part's (program, key, gate, GBA level, voicegroup, voice)."""
    progs, parts = {}, []
    for name in conv.SONGS:
        s = conv.Song(name, rom=rom, mapping=mp, sdat=sd, levels={'programs': {}, 'ratio': 1})
        s.convert()
        for prog, keys in s.notes_used.items():
            d = progs.setdefault(prog, {})
            for k, c in keys.items(): d[k] = d.get(k, 0) + c
        for (t, v), m in s.decisions.items():
            p = s.parts.get((t, v))
            if not p or not p['notes'] or m['vk'] == 'drums' or m.get('noise') or m.get('drum_key'): continue
            key = int(statistics.median(x[1] for x in p['notes'])); gate = int(statistics.median(x[3] for x in p['notes']))
            parts.append(dict(song=name, prog=m['program'], key=key + m.get('transpose', 0), gate=gate,
                              g=conv.gba_level(rom, s.header['voicegroup'], v, key, gate)))
    return progs, parts


def points(progs, drum_prog):
    pts = []
    for prog, keys in sorted(progs.items()):
        if prog == drum_prog:
            pts += [(prog, k, 6) for k in sorted(keys)]
            continue
        lo, hi = min(keys), max(keys)
        ks = [k for k in GRID_KEYS if lo - 12 < k < hi + 12] or [min(GRID_KEYS, key=lambda k: abs(k - lo))]
        pts += [(prog, k, g) for k in ks for g in GRID_GATES]
    return pts


def batches(pts, lib, lib_waves, drum_prog):
    def waves_of(p):
        prog, k, g = p
        t, regs = lib[prog]
        if t == 16: return {r[3] for r in regs if r[0] == k}
        if t == 17: return {r[3] for r in regs if r[0] <= k <= r[1] and r[2] == 1}
        return {regs[0][3]} if regs[0][2] == 1 else set()
    out, cur, ws = [], [], set()
    for p in pts:
        w = waves_of(p)
        if cur and sum(len(lib_waves[x]) for x in ws | w) > WAVE_BUDGET:
            out.append(cur); cur, ws = [], set()
        cur.append(p); ws |= w
    if cur: out.append(cur)
    return out


def build(batch, lib, lib_waves):
    used, inst = [], {}
    def wave(i):
        if i not in used: used.append(i)
        return used.index(i)
    for prog in sorted({p[0] for p in batch}):
        keys = {p[1] for p in batch if p[0] == prog}
        t, regs = lib[prog]
        if t == 16:
            lo, hi = min(keys), max(keys)
            by = {r[0]: r for r in regs}
            inst[prog] = (16, [(k, k, by[min(keys, key=lambda x: abs(x - k)) if k not in keys else k][2],
                                wave(by[k if k in keys else min(keys, key=lambda x: abs(x - k))][3]), 0)
                               + tuple(by[k if k in keys else min(keys, key=lambda x: abs(x - k))][5:]) for k in range(lo, hi + 1)])
        elif t == 17:
            inst[prog] = (17, [(r[0], r[1], r[2], wave(r[3]) if r[2] == 1 else r[3], 0) + tuple(r[5:]) for r in regs
                               if any(r[0] <= k <= r[1] for k in keys)])
        else:
            r = regs[0]
            inst[prog] = (t, [(0, 127, r[2], wave(r[3]) if r[2] == 1 else r[3], 0) + tuple(r[5:])])
    w = sseq.Writer(); tr = w.track()
    tr.cmd('note_wait', 0); tr.cmd('tempo', 120); tr.cmd('volume', VEL); tr.cmd('pan', 64); tr.cmd('expression', 127)
    tr.wait(96)
    for prog, key, gate in batch:
        tr.program(prog); tr.note(key, VEL, gate * 2); tr.wait(SEG)
    tr.wait(96); tr.end()
    return w.sseq(), build_sbnk(inst), build_swar([lib_waves[i] for i in used])


def measure(path, n):
    wv = wave.open(path)
    x = np.frombuffer(wv.readframes(wv.getnframes()), dtype='<i2').reshape(-1, 2).astype(np.float64)
    m = x.mean(1)
    win = int(44100 * 0.01)
    env = np.sqrt(np.convolve(m ** 2, np.ones(win) / win, 'same'))
    on = int(np.argmax(env > max(env.max() * 0.01, 20)))      # the first note
    sr, step = 44100, int(SEG / 96 * 44100)                   # 120 bpm: 96 ticks per second
    out = []
    for i in range(n):
        a = on + i * step; b = a + int(1.2 * sr)
        seg = x[a:b]
        out.append(float(np.sqrt(((seg[:, 0] ** 2 + seg[:, 1] ** 2) / 2).mean())) if len(seg) else 0.0)
    return out


def main(argv):
    base, test = argv[0], argv[1]
    from rom_layout_diff import Rom
    from hoenn_music import install_in_place
    rom, mp, sd = m4a.GbaRom(), conv.load_mapping(), SDAT(open(DEFAULT, 'rb').read())
    li = sd.index('bank', mp['library'])
    lib = parse_sbnk(sd.bank(li)); lib_waves = parse_swar(sd.wavearc(sd.info['bank'][li]['wavearcs'][0]))
    drum = mp['defaults']['drums']['program']
    progs, parts = usage(rom, mp, sd)
    pts = points(progs, drum)
    bs = batches(pts, lib, lib_waves, drum)
    print(f'{len(progs)} programs, {len(pts)} notes, {len(bs)} batches', flush=True)
    r = Rom(base)
    names = {v: k for k, v in r.names.items()} if isinstance(next(iter(r.names)), int) else r.names
    s0, e0 = r.fat[names['swan_sound_data.sdat']]
    sdat = r.d[s0:e0]
    work = os.path.join(ROOT, 'work', 'agents', 'music_check', 'calib'); os.makedirs(work, exist_ok=True)
    levels = {}
    for i, b in enumerate(bs):
        q, bk, sw = build(b, lib, lib_waves)
        new, _, _ = install_in_place(sdat, SLOT, q, bk, sw, 100)
        with open(test, 'r+b') as f: f.seek(s0); f.write(new)
        wav = os.path.join(work, f'batch{i}.wav')
        secs = (96 + len(b) * SEG + 96) / 96 + 3
        subprocess.run([os.path.join(ROOT, '.venv', 'bin', 'python'), os.path.join(HERE, 'music_record.py'), 'boot', test,
                        wav, str(secs), os.path.join(work, f'batch{i}.png')], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        for (prog, key, gate), lv in zip(b, measure(wav, len(b))):
            levels.setdefault(str(prog), {})[f'{key},{gate}'] = round(lv, 2)
        print(f'batch {i}: {len(b)} notes, {len(sw)} B of samples', flush=True)
    out = dict(_doc='Black 2 library instruments measured in game (b2tools/music_calib.py): RMS of one note over 1.2 s '
                    '("key,gate": gate in GBA ticks), velocity 113, volume 113, INFO 100. ratio: median Black 2 / GBA '
                    'level over every converted part, the target of m4a_to_sseq.auto_gain.',
               drum_program=drum, programs=levels)
    ratios = []
    for p in parts:
        b = conv.b2_level(out, p['prog'], p['key'], p['gate'])
        if b and p['g']: ratios.append(b / p['g'])
    out['ratio'] = round(statistics.median(ratios), 3)
    drum_ratio = []
    json.dump(out, open(conv.LEVELS, 'w'), indent=1)
    print('ratio', out['ratio'], '->', conv.LEVELS)


if __name__ == '__main__' and sys.argv[1:2] not in (['--gains'], ['--gba']):
    main(sys.argv[1:])


# ---- per-part gains (python3 music_calib.py --gains): the whole part, not one note --------------------------------
GAINS = os.path.join(ROOT, 'data', 'hoenn_music_gains.json')
CAL_GATE_SEC = {6: 0.125, 24: 0.5, 96: 2.0}      # the calibration notes' lengths at 120 bpm


def pan_power(p):
    """Black 2's stereo power at SSEQ pan p relative to the centre: the DS mixes each channel linearly between the speakers
    (GBATEK: "64 = half volume on both speakers"), so a hard-panned part is 3 dB above the same part centred (the
    calibration notes are centred). The GBA side needs nothing: m4a_render pans as the GBA does (CgbPan: hard-panned PSG
    on one side only). Measured: Littleroot's hard-panned square parts (pan 3 and 127) were 1.5-1.7x louder in game
    than the centred-pan model said, the others within 1 dB (work/agents/music_check/out/stems)."""
    l, r = (127 - p) / 127, p / 127
    return (l * l + r * r) / 2 / 0.25


WINDOW = 90.0                  # seconds of each part (or the song up to its loop end, when shorter)


def song_window(song, window=WINDOW):
    tempo = next((e[2] for tr in song.tracks for e in tr.events if e[0] == 'tempo'), 75)
    tps = tempo * 2 * m4a.FRAME_HZ / 150
    end = max(tr.end_tick for tr in song.tracks) / tps
    return tps, (min(window, end) if end > 1 else window)


def b2_part_levels(song, window=WINDOW):
    """{(track, voice): Black 2 RMS predicted from the calibrated notes} over the window. Every note's energy (its
    calibrated level squared x max(1.2 s, length + 0.2 s), scaled by velocity and track volume squared and by the pan's
    stereo power) summed incoherently, so dense parts with long releases count their overlap."""
    import bisect
    tps, D = song_window(song, window)
    ev = {}
    for i, tr in enumerate(song.tracks):
        ev[i] = {k: sorted((e[1], e[2]) for e in tr.events if e[0] == k) for k in ('vol', 'pan')}
    drums = {int(k): x for k, x in {**song.map.get('drum_keys', {}), **song.cfg.get('drums', {})}.items()}
    out = {}
    for (t, v), m in song.decisions.items():
        p = song.parts.get((t, v))
        if not p or not p['notes']: continue
        e_b2 = 0.0
        for tick, key, vel, gate in p['notes']:
            ts = tick / tps
            if ts >= D: continue
            gs = gate / tps
            if m['vk'] == 'drums': k, gc = drums.get(key, key), 6
            elif m.get('noise'): k, gc = (m['noise']['long'] if gate >= m['noise']['long_gate'] else m['noise']['short']), 6
            elif m.get('drum_key'): k, gc = m['drum_key'], 6
            else:
                k = key + m.get('transpose', 0)
                gc = min(CAL_GATE_SEC, key=lambda x: abs(math.log(CAL_GATE_SEC[x]) - math.log(max(gs, 0.02))))
            lv = conv.b2_level(song.levels, m['program'], k, gc) or 0.0
            at = {}
            for kind, dflt in (('vol', 100), ('pan', 64)):
                xs = ev[t][kind]; i = bisect.bisect_right(xs, (tick, 999)) - 1
                at[kind] = xs[i][1] if i >= 0 else dflt
            e_b2 += lv ** 2 * max(1.2, gs + 0.2) * (vel / 100) ** 2 * (at['vol'] / 100) ** 2 * pan_power(at['pan'])
        out[(t, v)] = math.sqrt(e_b2 / D)
    return out


def gba_part_levels(song, window=WINDOW):
    """{(track, voice): GBA RMS of the part alone} over the window (m4a_render; the slow half)."""
    import m4a_render
    tps, D = song_window(song, window)
    out = {}
    for (t, v), m in song.decisions.items():
        p = song.parts.get((t, v))
        if not p or not p['notes'] or min(x[0] for x in p['notes']) / tps >= D: continue
        r = m4a_render.Renderer(song.rom, song.n); r.solo = t; r.solo_voice = v
        l, rr = r.render(D)
        out[(t, v)] = float(np.sqrt(((l ** 2 + rr ** 2) / 2).mean()))
    return out


def part_levels(song, window=WINDOW):
    """{(track, voice): (GBA RMS of the part alone, Black 2 RMS predicted)} over the window."""
    b = b2_part_levels(song, window)
    return {k: (g, b.get(k, 0.0)) for k, g in gba_part_levels(song, window).items()}


GBA_CACHE = os.path.join(ROOT, 'work', 'agents', 'music_check', 'calib', 'gba_parts')


def _songs(lv):
    rom, mp, sd = m4a.GbaRom(), conv.load_mapping(), SDAT(open(DEFAULT, 'rb').read())
    lv0 = {k: x for k, x in lv.items() if k != 'gains_table'}
    for name in conv.SONGS:
        s = conv.Song(name, rom=rom, mapping=mp, sdat=sd, levels=lv0)
        s.convert()
        yield name, s


def gba_main(i, n):
    """--gba I/N: the GBA level of every part of every N-th song from I (cached: GBA_CACHE/<song>.json)."""
    os.makedirs(GBA_CACHE, exist_ok=True)
    for j, (name, s) in enumerate(_songs(conv.load_levels())):
        if j % n != i: continue
        path = os.path.join(GBA_CACHE, name + '.json')
        if os.path.exists(path): continue
        g = gba_part_levels(s)
        json.dump({f't{t}v{v}': x for (t, v), x in g.items()}, open(path, 'w'))
        print(name, len(g), flush=True)


def gains_main():
    """--gains: each part's gain from the cached GBA levels (--gba) and the Black 2 model."""
    rows = {}
    for name, s in _songs(conv.load_levels()):
        path = os.path.join(GBA_CACHE, name + '.json')
        if not os.path.exists(path): raise SystemExit(f'{name}: no GBA levels: run --gba first')
        g = json.load(open(path))
        for (t, v), b in b2_part_levels(s).items():
            gg = g.get(f't{t}v{v}', 0.0)
            if gg > 1e-3 and b > 1e-3: rows[f'{name}:t{t}v{v}'] = b / gg
    ref = statistics.median(rows.values())
    out = dict(_doc='b2tools/music_calib.py --gains: each part\'s gain, so Black 2 / GBA level (the whole part over its '
                    f'first {WINDOW:.0f} s, part_levels: GBA from m4a_render, Black 2 from the calibrated notes, with pan) is '
                    'the median of all parts; m4a_to_sseq.auto_gain uses it before the one-note model.',
               ref=round(ref, 3), gains={k: round(max(0.1, min(4.0, ref / x)), 3) for k, x in sorted(rows.items())})
    json.dump(out, open(GAINS, 'w'), indent=0)
    print(len(rows), 'parts; ref', ref, '->', GAINS)


if __name__ == '__main__' and sys.argv[1:2] == ['--gba']:
    a, b = sys.argv[2].split('/')
    gba_main(int(a), int(b))
if __name__ == '__main__' and sys.argv[1:2] == ['--gains']:
    gains_main()
