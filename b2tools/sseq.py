"""Read and write NitroSDK sequences (SSEQ), as Black 2's sound archive stores them (notes/MUSIC.md "SSEQ").

    python3 sseq.py SEQ_NAME|FILE.sseq [--dump]      tracks, programs, note ranges and loop points of a sequence

File: 'SSEQ' FEFF 0100 u32 size, u16 0x10, u16 1 block; 'DATA' u32 size, u32 data offset (0x1C); then commands.
Times are ticks, 48 per quarter note. Commands (NitroSDK NNS_SndSeq, as decoded by the SDK's own sequence player):
  00-7F  note: key, u8 velocity, var-length duration (with note-wait on, the track also waits that long)
  80 var wait, 81 var program, 93 u8 track + u24 offset (open track), 94 u24 jump, 95 u24 call, FD return,
  FE u16 track mask (allocate; first command of track 0), FF end of track
  C0 pan, C1 volume, C2 player volume, C3 transpose (s8), C4 pitch bend (s8), C5 bend range, C6 priority,
  C7 note-wait mode (1 on = mono), C8 tie, C9 portamento key, CA mod depth, CB mod speed, CC mod type,
  CD mod range, CE portamento on/off, CF portamento time, D0 attack, D1 decay, D2 sustain, D3 release,
  D4 loop start (count), D5 expression, D6 print var, E0 u16 mod delay, E1 u16 tempo, E3 s16 sweep pitch, FC loop end
  A0-A2 prefixes (random / variable / if) and B0-BD variable commands: not written by this converter.
"""
import os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ONE_BYTE = {0xC0: 'pan', 0xC1: 'volume', 0xC2: 'master_volume', 0xC3: 'transpose', 0xC4: 'bend', 0xC5: 'bend_range',
            0xC6: 'priority', 0xC7: 'note_wait', 0xC8: 'tie', 0xC9: 'porta_key', 0xCA: 'mod_depth', 0xCB: 'mod_speed',
            0xCC: 'mod_type', 0xCD: 'mod_range', 0xCE: 'porta', 0xCF: 'porta_time', 0xD0: 'attack', 0xD1: 'decay',
            0xD2: 'sustain', 0xD3: 'release', 0xD4: 'loop_start', 0xD5: 'expression', 0xD6: 'print'}
TWO_BYTE = {0xE0: 'mod_delay', 0xE1: 'tempo', 0xE3: 'sweep'}
CODE = {v: k for k, v in {**ONE_BYTE, **TWO_BYTE}.items()}


def varlen(d, p):
    v = 0
    while True:
        b = d[p]; p += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80: return v, p


def enc_varlen(v):
    out = [v & 0x7F]
    v >>= 7
    while v:
        out.append(0x80 | (v & 0x7F)); v >>= 7
    return bytes(reversed(out))


def data_of(sseq):
    assert sseq[:4] == b'SSEQ', sseq[:4]
    off = struct.unpack_from('<I', sseq, 0x18)[0]
    return sseq[off:]


def decode(sseq, max_ticks=None):
    """{track: dict(events=[(tick, name, *args)], loop_tick, end_tick)}: each track followed from its start, through
    calls, until it ends or jumps back to where it has been (the loop)."""
    d = data_of(sseq)
    starts = {0: 0}
    p = 0
    if d[0] == 0xFE: p = 3
    while d[p] == 0x93:
        starts[d[p + 1]] = d[p + 2] | d[p + 3] << 8 | d[p + 4] << 16
        p += 5
    starts[0] = p
    out = {}
    for tr, pc in sorted(starts.items()):
        ev, t, stack, seen, loops = [], 0, [], {}, []
        loop_tick = None
        note_wait = True
        steps = 0
        while pc < len(d):
            steps += 1
            if steps > 100000 or (max_ticks and t > max_ticks): break
            if not stack: seen.setdefault(pc, t)
            c = d[pc]; pc += 1
            if c < 0x80:
                vel = d[pc]; dur, pc = varlen(d, pc + 1)
                ev.append((t, 'note', c, vel, dur))
                if note_wait: t += dur
            elif c == 0x80:
                w, pc = varlen(d, pc); t += w
            elif c == 0x81:
                v, pc = varlen(d, pc); ev.append((t, 'program', v))
            elif c == 0x93:
                pc += 4
            elif c == 0x94:
                tgt = d[pc] | d[pc + 1] << 8 | d[pc + 2] << 16
                if not stack and tgt in seen: loop_tick = seen[tgt]; break
                pc = tgt
            elif c == 0x95:
                stack.append(pc + 3); pc = d[pc] | d[pc + 1] << 8 | d[pc + 2] << 16
            elif c == 0xFD:
                if not stack: break
                pc = stack.pop()
            elif c == 0xFE:
                pc += 2
            elif c == 0xFF:
                break
            elif c in ONE_BYTE:
                v = d[pc]; pc += 1
                if c in (0xC3, 0xC4): v = v - 256 if v > 127 else v
                if c == 0xC7: note_wait = bool(v)
                if c == 0xD4: loops.append((pc, v))
                ev.append((t, ONE_BYTE[c], v))
            elif c == 0xFC:
                if loops:
                    lp, n = loops[-1]
                    # count 0 = forever; else repeat n times in all
                    key = ('loop', lp)
                    cnt = seen.get(key, 0) + 1
                    seen[key] = cnt
                    if n == 0 or cnt < n: pc = lp
                    else: loops.pop(); seen[key] = 0
            elif c in TWO_BYTE:
                v = struct.unpack_from('<h' if c == 0xE3 else '<H', d, pc)[0]; pc += 2
                ev.append((t, TWO_BYTE[c], v))
            elif 0xA0 <= c <= 0xBD:
                ev.append((t, f'cmd{c:02X}')); break      # variables/random: not decoded
            else:
                ev.append((t, f'unknown{c:02X}')); break
        out[tr] = dict(events=ev, loop_tick=loop_tick, end_tick=t)
    return out


class Writer:
    """Builds the command streams of the tracks and links them into one SSEQ (track 0 first, with FE and 93s)."""
    def __init__(self):
        self.tracks = []

    def track(self):
        t = TrackWriter(); self.tracks.append(t); return t

    def sseq(self):
        mask = (1 << len(self.tracks)) - 1
        head = bytearray(b'\xFE' + struct.pack('<H', mask))
        head_len = len(head) + 5 * (len(self.tracks) - 1)
        bodies, offs, pos = [], [], head_len
        for t in self.tracks:
            offs.append(pos)
            pos += len(t.buf)
        for i, t in enumerate(self.tracks[1:], 1):
            o = offs[i]
            head += bytes([0x93, i, o & 0xFF, (o >> 8) & 0xFF, o >> 16])
        data = bytearray(head)
        for i, t in enumerate(self.tracks):
            b = bytearray(t.buf)
            for at, target in t.jumps:        # relative to the track -> absolute in the data
                a = offs[i] + target
                b[at:at + 3] = bytes([a & 0xFF, (a >> 8) & 0xFF, a >> 16])
            data += b
        while len(data) % 4: data += b'\0'
        size = 0x1C + len(data)
        return (b'SSEQ' + struct.pack('<HHIHH', 0xFEFF, 0x0100, size, 0x10, 1) +
                b'DATA' + struct.pack('<II', size - 0x10, 0x1C) + bytes(data))


class TrackWriter:
    def __init__(self):
        self.buf = bytearray()
        self.jumps = []

    def here(self): return len(self.buf)
    def wait(self, ticks):
        while ticks > 0:
            step = min(ticks, 0x0FFFFFFF)
            self.buf += b'\x80' + enc_varlen(step); ticks -= step
    def note(self, key, vel, dur): self.buf += bytes([key, vel]) + enc_varlen(max(1, dur))
    def program(self, p): self.buf += b'\x81' + enc_varlen(p)
    def cmd(self, name, v):
        c = CODE[name]
        if c in TWO_BYTE: self.buf += bytes([c]) + struct.pack('<h' if c == 0xE3 else '<H', v)
        else: self.buf += bytes([c, v & 0xFF])
    def jump(self, target):
        self.buf += b'\x94'; self.jumps.append((len(self.buf), target)); self.buf += b'\0\0\0'
    def end(self): self.buf += b'\xFF'


def main(argv):
    from sdat import SDAT, DEFAULT
    name = argv[0]
    if os.path.exists(name):
        data = open(name, 'rb').read()
    else:
        s = SDAT(open(DEFAULT, 'rb').read())
        i = s.index('seq', name)
        data = s.seq(i)
        e = s.info['seq'][i]
        print(f'{name}: seq {i}, {len(data)} B, bank {e["bank"]} {s.name("bank", e["bank"])}, volume {e["volume"]}')
    tr = decode(data)
    for k, t in tr.items():
        notes = [e for e in t['events'] if e[1] == 'note']
        progs = sorted({e[2] for e in t['events'] if e[1] == 'program'})
        keys = [e[2] for e in notes]
        print(f'  track {k}: {len(notes)} notes {min(keys) if keys else "-"}..{max(keys) if keys else "-"}, programs {progs},'
              f' loop {t["loop_tick"]} -> {t["end_tick"]}')
        if '--dump' in argv:
            for e in t['events'][:60]: print('     ', e)


if __name__ == '__main__':
    main(sys.argv[1:])
