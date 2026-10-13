"""What each GBA part plays (notes/MUSIC.md "Instrument mapping"): for every song, track and voice, its notes'
register, lengths, chords and whether another track plays the same notes; the role m4a_to_sseq.py uses to pick a
Black 2 instrument for parts without a Black 2 equivalent (square waves, the programmable wave, noise).

    python3 music_roles.py [SONG ...]          table of the PSG parts (all songs by default)

Roles: bass (median key below 52), double (half its notes or more sound with the same key class in another track at
the same tick), lead (one note at a time, a melody), arpeggio (short notes in quick runs), stabs (short notes with
rests: off-beat chords), pad (long notes or chords)."""
import os, sys, statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m4a  # noqa: E402

BATTLE = ('mus_vs_', 'mus_encounter_', 'mus_victory_', 'mus_intro_battle')


def song_context(name):
    return 'battle' if name.startswith(BATTLE) else 'field'


def parts(rom, name):
    """{(track, voice): dict(notes=[(tick, key, vel, gate)], kind)} with every note's key after KEYSH."""
    h, trs = m4a.parse_song(rom, rom.song_index(name))
    vg = h['voicegroup']
    out = {}
    for i, tr in enumerate(trs):
        v, ks = 0, 0
        for e in tr.events:
            if e[0] == 'voice': v = e[2]
            elif e[0] == 'keysh': ks = e[2] - 256 if e[2] > 127 else e[2]
            elif e[0] == 'note':
                gate = e[4] if e[4] else 96
                out.setdefault((i, v), dict(notes=[]))['notes'].append((e[1], e[2] + ks, e[3], gate))
    for (i, v), p in out.items():
        t = rom.voice(vg, v)['type']
        p['kind'] = 'drums' if t & 0x80 else 'split' if t & 0x40 else {0: 'sample', 1: 'square', 2: 'square',
                                                                           3: 'wave', 4: 'noise'}[t & 7]
        p['duty'] = rom.voice(vg, v)['wav'] & 3 if t & 7 in (1, 2) and not t & 0xC0 else None
    return h, trs, out


def role(key, p, everything):
    """The role of part `key` = (track, voice) among all parts of the song."""
    n = p['notes']
    keys = [x[1] for x in n]
    gates = [x[3] for x in n]
    med_key, med_gate = statistics.median(keys), statistics.median(gates)
    onsets = defaultdict(set)
    for (t2, v2), q in everything.items():
        if t2 == key[0]: continue
        for x in q['notes']: onsets[x[0]].add(x[1] % 12)
    dbl = sum(1 for x in n if x[1] % 12 in onsets.get(x[0], ())) / len(n)
    ticks = defaultdict(int)
    for x in n: ticks[x[0]] += 1
    chords = sum(1 for c in ticks.values() if c > 1) / max(1, len(ticks))
    starts = sorted(ticks)
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    med_gap = statistics.median(gaps) if gaps else 96
    fill = statistics.mean(min(g, gp) / gp for g, gp in zip(gates, gaps)) if gaps else 1
    stats = dict(n=len(n), key=med_key, lo=min(keys), hi=max(keys), gate=med_gate, gap=med_gap, chords=round(chords, 2),
                 double=round(dbl, 2), fill=round(fill, 2))
    if med_key < 52: r = 'bass'
    elif dbl >= 0.5: r = 'double'
    elif chords >= 0.3 or med_gate >= 48: r = 'pad'
    elif med_gate <= 6 and fill < 0.6: r = 'stabs'
    elif med_gap <= 12 and med_gate <= 12: r = 'arpeggio'
    else: r = 'lead'
    return r, stats


def main(argv):
    rom = m4a.GbaRom()
    import m4a_to_sseq
    names = argv or m4a_to_sseq.SONGS
    for name in names:
        h, trs, ps = parts(rom, name)
        for key, p in sorted(ps.items()):
            if p['kind'] not in ('square', 'wave', 'noise'): continue
            r, st = role(key, p, ps)
            print(f'{name:28s} t{key[0]} v{key[1]:3d} {p["kind"]:6s} {r:8s} {st}')


if __name__ == '__main__':
    main(sys.argv[1:])
