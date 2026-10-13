"""Read Ruby/Sapphire's music from the GBA ROM: the M4A ("Sappy"/MP2K) song table, song headers, voicegroups,
samples and track bytecode (notes/MUSIC.md "The GBA side"). Engine semantics are pokeemerald's src/m4a_1.s /
src/m4a.c (the same engine as Ruby/Sapphire); names of voices and samples are pokeruby's sound/*.inc.

    python3 m4a.py [ROM] SONG          dump a song (index or pokeruby name, e.g. mus_littleroot): voices and tracks

The ROM is the user's own dump (roms/sapphire_rev1_original.gba); nothing is downloaded.
"""
import os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
ROM_PATH = os.path.join(ROOT, 'roms', 'sapphire_rev1_original.gba')
PRUBY = os.path.join(ROOT, 'external', 'pokeruby')

# gClockTable (pokeemerald src/m4a_tables.c): wait W00..W96 = 0x80..0xB0, note lengths N01..N96 = 0xD0..0xFF
CLOCK = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 28, 30, 32, 36,
         40, 42, 44, 48, 52, 54, 56, 60, 64, 66, 68, 72, 76, 78, 80, 84, 88, 90, 92, 96]
CMD = {0xB1: 'FINE', 0xB2: 'GOTO', 0xB3: 'PATT', 0xB4: 'PEND', 0xB5: 'REPT', 0xB9: 'MEMACC', 0xBA: 'PRIO',
       0xBB: 'TEMPO', 0xBC: 'KEYSH', 0xBD: 'VOICE', 0xBE: 'VOL', 0xBF: 'PAN', 0xC0: 'BEND', 0xC1: 'BENDR',
       0xC2: 'LFOS', 0xC3: 'LFODL', 0xC4: 'MOD', 0xC5: 'MODT', 0xC8: 'TUNE', 0xCC: 'PORT', 0xCD: 'XCMD', 0xCE: 'EOT',
       0xCF: 'TIE'}
XCMD_LEN = {0: 0, 1: 4, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 2, 13: 4}
FRAME_HZ = 59.7275                     # GBA frames per second: the engine runs once per V-blank
NOTE_NAMES = ['Cn', 'Cs', 'Dn', 'Ds', 'En', 'Fn', 'Fs', 'Gn', 'Gs', 'An', 'As', 'Bn']


def note_name(k):
    return f'{NOTE_NAMES[k % 12]}{k // 12 - 2}'.replace('-', 'M')   # MPlayDef: Cn3 = 60


class GbaRom:
    def __init__(self, path=ROM_PATH):
        self.d = open(path, 'rb').read()
        self.song_table = self._find_song_table()
        self.sample_names = None

    def u8(self, a): return self.d[a & 0x1FFFFFF]
    def u16(self, a): return struct.unpack_from('<H', self.d, a & 0x1FFFFFF)[0]
    def u32(self, a): return struct.unpack_from('<I', self.d, a & 0x1FFFFFF)[0]

    def _find_song_table(self):
        """gSongTable: 8-byte entries {song header pointer, u16 music player, u16 music player}. The player pattern of
        pokeruby's sound/song_table.inc (468 songs) finds it (Sapphire rev 1: 0x08455500)."""
        pat = [tuple(map(int, m.groups())) for m in
               re.finditer(r'^\s*song\s+\w+,\s*(\d+),\s*(\d+)', open(os.path.join(PRUBY, 'sound', 'song_table.inc')).read(), re.M)]
        self.song_names = re.findall(r'^\s*song\s+(\w+),', open(os.path.join(PRUBY, 'sound', 'song_table.inc')).read(), re.M)
        d = self.d
        for off in range(0, len(d) - 8 * 40, 4):
            if all(struct.unpack_from('<HH', d, off + 8 * i + 4) == pat[i] and
                   0x08000000 <= struct.unpack_from('<I', d, off + 8 * i)[0] < 0x0A000000 for i in range(40)):
                return 0x08000000 + off
        raise SystemExit('song table not found')

    def song_index(self, name_or_index):
        if str(name_or_index).isdigit(): return int(name_or_index)
        return self.song_names.index(name_or_index)

    def header(self, n):
        a = self.u32(self.song_table + 8 * n)
        tracks, blocks, prio, rev = self.d[a & 0x1FFFFFF:(a & 0x1FFFFFF) + 4]
        tone = self.u32(a + 4)
        parts = [self.u32(a + 8 + 4 * i) for i in range(tracks)]
        return dict(addr=a, tracks=tracks, priority=prio, reverb=rev, voicegroup=tone, parts=parts)

    def tone(self, addr):
        """One ToneData (12 bytes): type, key, length, pan_sweep, wav (pointer or CGB duty), attack, decay, sustain,
        release (keysplit voices: the keysplit table pointer in place of the envelope)."""
        t, key, length, ps, wav, a, dcy, s, r = struct.unpack_from('<BBBBIBBBB', self.d, addr & 0x1FFFFFF)
        v = dict(addr=addr, type=t, key=key, length=length, pan_sweep=ps, wav=wav, attack=a, decay=dcy, sustain=s,
                 release=r)
        if t & 0x40: v['keysplit'] = self.u32(addr + 8)
        return v

    def voice(self, vg, n):
        return self.tone(vg + 12 * n)

    def wave(self, addr):
        """WaveData: u16 type, u16 status (0x4000 = loop), u32 freq (Hz * 1024 at key 60), u32 loop start, u32 size,
        then size signed 8-bit samples."""
        typ, status, freq, loop, size = struct.unpack_from('<HHIII', self.d, addr & 0x1FFFFFF)
        o = (addr & 0x1FFFFFF) + 16
        return dict(addr=addr, type=typ, loop=bool(status & 0xC000), freq=freq / 1024, loop_start=loop, size=size,
                    data=self.d[o:o + size])

    def sample_name(self, addr):
        """pokeruby's label of a DirectSound sample (sound/direct_sound_data.inc lists them with Ruby's addresses;
        Sapphire rev 1's sound data sits at a fixed offset from Ruby's, found from the first sample)."""
        if self.sample_names is None:
            labels = re.findall(r'^(DirectSoundWaveData_\w+):: @ ([0-9A-F]+)',
                                open(os.path.join(PRUBY, 'sound', 'direct_sound_data.inc')).read(), re.M)
            self.sample_names = {}
            # the offset: the first sample (Ruby address) holds a valid WaveData header at the same relative spot
            base = int(labels[0][1], 16)
            for delta in range(-0x2000, 0x2000, 4):
                a = base + delta
                h = struct.unpack_from('<HHIII', self.d, a & 0x1FFFFFF)
                nxt = int(labels[1][1], 16) + delta
                if h[0] == 0 and h[1] in (0, 0x4000) and 0 < h[4] < 0x100000 and (a + 16 + h[4] + 3) & ~3 == nxt:
                    self.sample_names = {int(x, 16) + delta: n.replace('DirectSoundWaveData_', '') for n, x in labels}
                    break
        return self.sample_names.get(addr, f'{addr:08X}')

    def describe_voice(self, vg, n):
        v = self.voice(vg, n)
        t = v['type']
        if t & 0x80: return f'drum kit {v["wav"]:08X}'
        if t & 0x40: return f'keysplit {v["wav"]:08X}: ' + '/'.join(sorted({self.sample_name(self.tone(v['wav'] + 12 * i)['wav'])
                                                                            for i in self.keysplit_indices(v)}))
        if t & 7 == 0: return f'directsound {self.sample_name(v["wav"])}' + (' (fixed pitch)' if t & 8 else '')
        return {1: 'square 1', 2: 'square 2', 3: 'programmable wave', 4: 'noise'}[t & 7] + \
            (f' duty {v["wav"] & 3}' if t & 7 in (1, 2) else '')

    def keysplit_indices(self, v, keys=range(36, 97)):
        """Sub-voices a key split uses over `keys` (pokeruby's tables only cover part of 0-127: keysplit_tables.inc)."""
        tab = v['keysplit']
        return sorted({self.d[(tab + k) & 0x1FFFFFF] for k in keys})

    def resolve(self, vg, voice, key):
        """The ToneData that plays `key` with voice `voice` (ply_note: keysplit -> table[key]; drum kit -> sub-voice
        `key`, played at the sub-voice's own key) and the key it plays at."""
        v = self.voice(vg, voice)
        if v['type'] & 0x40:
            idx = self.d[(v['keysplit'] + key) & 0x1FFFFFF]
            return self.tone(v['wav'] + 12 * idx), key
        if v['type'] & 0x80:
            sub = self.tone(v['wav'] + 12 * key)
            return sub, sub['key']
        return v, key


class Track:
    """A track flattened into timed events (ticks: 24 per quarter note). The GOTO back to the loop label ends it:
    loop_event/loop_tick are where that label is, end_tick where the GOTO is."""
    def __init__(self):
        self.events, self.loop_event, self.loop_tick, self.end_tick = [], None, None, 0


def parse_track(rom, addr, warn=print):
    tr = Track()
    pc, t, stack, run = addr & 0x1FFFFFF, 0, [], None
    key, vel = 60, 127
    rep = {}
    seen = {}                                  # pc at pattern level 0 -> (event index, tick): the loop label
    d = rom.d
    steps = 0
    while True:
        steps += 1
        if steps > 200000: raise SystemExit(f'track {addr:08X}: runaway')
        if not stack: seen.setdefault(pc, (len(tr.events), t))
        c = d[pc]
        if c < 0x80:
            if run is None: raise SystemExit(f'track {addr:08X}: data byte {c} with no running status at {pc:X}')
            c = run
        else:
            pc += 1
            if c >= 0xBD: run = c
        if c >= 0xCF:                               # TIE / N01..N96
            gate = CLOCK[c - 0xCF]
            if d[pc] < 0x80:
                key = d[pc]; pc += 1
                if d[pc] < 0x80:
                    vel = d[pc]; pc += 1
                    if d[pc] < 0x80:
                        gate += d[pc]; pc += 1
            tr.events.append(('note', t, key, vel, gate))      # gate 0: TIE, held until EOT
        elif c <= 0xB0:
            t += CLOCK[c - 0x80]
        elif c == 0xB1:                              # FINE
            break
        elif c == 0xB2:                              # GOTO
            target = struct.unpack_from('<I', d, pc)[0] & 0x1FFFFFF
            if not stack and target in seen:
                tr.loop_event, tr.loop_tick = seen[target]
                break
            pc = target
        elif c == 0xB3:                              # PATT (3 levels)
            stack.append(pc + 4)
            pc = struct.unpack_from('<I', d, pc)[0] & 0x1FFFFFF
        elif c == 0xB4:                              # PEND
            if stack: pc = stack.pop()
        elif c == 0xB5:                              # REPT count, address
            n = d[pc]
            target = struct.unpack_from('<I', d, pc + 1)[0] & 0x1FFFFFF
            if n == 0:
                pc = target
            else:
                rep[pc] = rep.get(pc, 0) + 1
                if rep[pc] < n: pc = target
                else: rep[pc] = 0; pc += 5
        elif c == 0xB9:                              # MEMACC: not used by field songs; skipped
            warn(f'track {addr:08X}: MEMACC at {pc:X} ignored')
            op = d[pc]; pc += 3 + (4 if op >= 6 else 0)
        elif c == 0xCD:                              # XCMD sub, params
            sub = d[pc]
            tr.events.append(('xcmd', t, sub, d[pc + 1:pc + 1 + XCMD_LEN.get(sub, 1)]))
            pc += 1 + XCMD_LEN.get(sub, 1)
        elif c == 0xCE:                              # EOT [key]
            if d[pc] < 0x80: key = d[pc]; pc += 1
            tr.events.append(('eot', t, key))
        elif c == 0xCC:                              # PORT reg, value
            pc += 2
        elif c in CMD:
            tr.events.append((CMD[c].lower(), t, d[pc])); pc += 1
        else:
            warn(f'track {addr:08X}: command {c:02X} ends the track (ply_fine)')
            break
    tr.end_tick = t
    return tr


def parse_song(rom, n):
    h = rom.header(n)
    return h, [parse_track(rom, p) for p in h['parts']]


def tempo_bpm(value):
    """TEMPO's byte is bpm/2 (ply_tempo: tempoD = byte * 2); a tick passes every 150/tempoD frames, 24 ticks per
    quarter note, so the real beat is bpm * 59.7275 / 60."""
    return value * 2 * FRAME_HZ / 60


def main(argv):
    rom_path = argv[0] if argv and argv[0].endswith('.gba') else ROM_PATH
    args = argv[1:] if argv and argv[0].endswith('.gba') else argv
    rom = GbaRom(rom_path)
    n = rom.song_index(args[0] if args else 'mus_littleroot')
    h, tracks = parse_song(rom, n)
    print(f'song {n} {rom.song_names[n]}: header {h["addr"]:08X}, {h["tracks"]} tracks, priority {h["priority"]}, '
          f'reverb {h["reverb"]:#x}, voicegroup {h["voicegroup"]:08X} (song table {rom.song_table:08X})')
    used = {}
    for i, tr in enumerate(tracks):
        voices = sorted({e[2] for e in tr.events if e[0] == 'voice'})
        notes = [e for e in tr.events if e[0] == 'note']
        keys = [e[2] for e in notes]
        kinds = sorted({e[0] for e in tr.events})
        print(f'  track {i}: {len(notes)} notes {note_name(min(keys)) if keys else "-"}..{note_name(max(keys)) if keys else "-"}, '
              f'voices {voices}, loop at tick {tr.loop_tick} -> {tr.end_tick}, events {kinds}')
        for v in voices: used.setdefault(v, []).append(i)
        for e in tr.events:
            if e[0] in ('tempo', 'vol', 'pan', 'keysh', 'mod', 'lfos', 'bendr', 'modt', 'lfodl', 'tune', 'xcmd', 'prio') \
                    and e[1] == 0:
                print(f'      t0 {e[0]} {e[2:]}')
    for v, trs in sorted(used.items()):
        print(f'  voice {v} (tracks {trs}): {rom.describe_voice(h["voicegroup"], v)}')


if __name__ == '__main__':
    main(sys.argv[1:])
