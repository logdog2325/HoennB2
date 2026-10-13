"""Read and rewrite Black 2's sound archive (files/swan_sound_data.sdat, NitroSDK SDAT; notes/MUSIC.md).

    python3 sdat.py [SDAT] [seq|bank|wavearc|player|group|strm|NAME...]    list records (default: the decomp's SDAT)

Layout (checked on swan_sound_data.sdat, 89,373,024 B): a 0x40 header with 4 blocks (offset, size): SYMB (names),
INFO (one record list per kind), FAT (16 B per file: offset from the SDAT start, size, 8 reserved) and FILE (the
files, 32-byte aligned, in FAT order). INFO records (NitroSDK NNSSndArc*Info):
  SEQ      u32 file, u16 bank, u8 volume, u8 channel priority, u8 player priority, u8 player, u16 reserved
  SEQARC   u32 file
  BANK     u32 file, u16 wave archive[4] (0xFFFF none)
  WAVEARC  u32 file (low 24 bits; top 8 bits flags: bit 0 = load each wave on its own)
  PLAYER   u8 max sequences, u8 pad, u16 channel mask, u32 heap size
  GROUP    u32 count, then {u8 type, u8 load flags, u16 pad, u32 index}
  PLAYER2  u8 count, u8 channels[16], u8 pad[7]                      (stream players)
  STRM     u32 file, u8 volume, u8 priority, u8 player, u8 pad[5]
"""
import os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
DEFAULT = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files', 'swan_sound_data.sdat')
KINDS = ['seq', 'seqarc', 'bank', 'wavearc', 'player', 'group', 'player2', 'strm']


class SDAT:
    def __init__(self, data):
        self.data = data = bytes(data)
        assert data[:4] == b'SDAT', 'not an SDAT'
        (self.symb_off, self.symb_size, self.info_off, self.info_size, self.fat_off, self.fat_size,
         self.file_off, self.file_size) = struct.unpack_from('<8I', data, 0x10)
        self.names = self._symbols() if self.symb_off else {k: [] for k in KINDS}
        self.info = self._info()
        n = struct.unpack_from('<I', data, self.fat_off + 8)[0]
        self.fat = [struct.unpack_from('<II', data, self.fat_off + 12 + 16 * i) for i in range(n)]

    # ---- reading
    def _symbols(self):
        d, base = self.data, self.symb_off
        rec = struct.unpack_from('<8I', d, base + 8)
        def strs(off):
            n = struct.unpack_from('<I', d, base + off)[0]
            out = []
            for i in range(n):
                o = struct.unpack_from('<I', d, base + off + 4 + 4 * i)[0]
                out.append(d[base + o:d.index(b'\0', base + o)].decode() if o else None)
            return out
        names = {}
        for k, off in zip(KINDS, rec):
            if not off: names[k] = []; continue
            if k == 'seqarc':      # {name, sub-record of sequence names} pairs
                n = struct.unpack_from('<I', d, base + off)[0]
                names[k] = []
                for i in range(n):
                    o, _sub = struct.unpack_from('<II', d, base + off + 4 + 8 * i)
                    names[k].append(d[base + o:d.index(b'\0', base + o)].decode() if o else None)
            else:
                names[k] = strs(off)
        return names

    def _info(self):
        d, base = self.data, self.info_off
        rec = struct.unpack_from('<8I', d, base + 8)
        info = {}
        for k, off in zip(KINDS, rec):
            n = struct.unpack_from('<I', d, base + off)[0]
            entries = []
            for i in range(n):
                o = struct.unpack_from('<I', d, base + off + 4 + 4 * i)[0]
                if not o: entries.append(None); continue
                p = base + o
                if k == 'seq':
                    f, bank, vol, cpr, ppr, ply = struct.unpack_from('<IHBBBB', d, p)
                    e = dict(file=f, bank=bank, volume=vol, channel_prio=cpr, player_prio=ppr, player=ply, _at=p)
                elif k == 'seqarc':
                    e = dict(file=struct.unpack_from('<I', d, p)[0], _at=p)
                elif k == 'bank':
                    f, *wa = struct.unpack_from('<I4H', d, p)
                    e = dict(file=f, wavearcs=[w for w in wa if w != 0xFFFF], _at=p)
                elif k == 'wavearc':
                    f = struct.unpack_from('<I', d, p)[0]
                    e = dict(file=f & 0xFFFFFF, flags=f >> 24, _at=p)
                elif k == 'player':
                    mx, _, mask, heap = struct.unpack_from('<BBHI', d, p)
                    e = dict(max_seqs=mx, channel_mask=mask, heap=heap, _at=p)
                elif k == 'group':
                    cnt = struct.unpack_from('<I', d, p)[0]
                    e = dict(items=[struct.unpack_from('<BBHI', d, p + 4 + 8 * j) for j in range(cnt)], _at=p)
                elif k == 'player2':
                    cnt = d[p]
                    e = dict(channels=list(d[p + 1:p + 1 + cnt]), _at=p)
                else:  # strm
                    f, vol, pri, ply = struct.unpack_from('<IBBB', d, p)
                    e = dict(file=f, volume=vol, priority=pri, player=ply, _at=p)
                entries.append(e)
            info[k] = entries
        return info

    def name(self, kind, i):
        n = self.names.get(kind, [])
        return n[i] if i < len(n) and n[i] else f'{kind}{i}'

    def index(self, kind, name):
        return self.names[kind].index(name)

    def file(self, fid):
        off, size = self.fat[fid]
        return self.data[off:off + size]

    def seq(self, i): return self.file(self.info['seq'][i]['file'])
    def bank(self, i): return self.file(self.info['bank'][i]['file'])
    def wavearc(self, i): return self.file(self.info['wavearc'][i]['file'])

    # ---- writing
    ENTRY_SIZE = {'seq': 12, 'seqarc': 4, 'bank': 12, 'wavearc': 4, 'player': 8, 'player2': 24, 'strm': 12}

    def raw_entry(self, kind, i):
        e = self.info[kind][i]
        if e is None: return None
        size = 4 + 8 * len(e['items']) if kind == 'group' else self.ENTRY_SIZE[kind]
        return self.data[e['_at']:e['_at'] + size]

    @staticmethod
    def seq_entry(file, bank, volume=100, channel_prio=30, player_prio=64, player=0):
        return struct.pack('<IHBBBBH', file, bank, volume, channel_prio, player_prio, player, 0)

    @staticmethod
    def bank_entry(file, wavearcs):
        wa = list(wavearcs) + [0xFFFF] * (4 - len(wavearcs))
        return struct.pack('<I4H', file, *wa)

    @staticmethod
    def wavearc_entry(file, flags=0):
        return struct.pack('<I', file | flags << 24)

    def build(self, files=None, new_files=(), entries=None):
        """A new SDAT with the same SYMB block: `files` {file id: bytes} replaces files, `new_files` are appended
        (ids len(fat), len(fat)+1, ...), `entries` {(kind, index): raw entry bytes} sets INFO entries (an index past
        the end grows that list; skipped indices stay null). The INFO and FAT blocks are rebuilt in Black 2's own
        layout (each kind's record - count and entry offsets - followed by its entries; FAT 16 B per file; files
        32-byte aligned in id order). With no changes the result is byte-identical to the input (checked by
        `python3 sdat.py --selftest`)."""
        files, entries = files or {}, entries or {}
        # INFO
        info = bytearray(b'INFO' + bytes(4) + bytes(32) + bytes(24))
        rec_offs = []
        for k in KINDS:
            n = max([len(self.info[k])] + [i + 1 for kk, i in entries if kk == k])
            raws = []
            for i in range(n):
                if (k, i) in entries: raws.append(entries[(k, i)])
                elif i < len(self.info[k]): raws.append(self.raw_entry(k, i))
                else: raws.append(None)
            rec_offs.append(len(info))
            pos = len(info) + 4 + 4 * n
            offs, body = [], bytearray()
            for r in raws:
                if r is None: offs.append(0)
                else: offs.append(pos + len(body)); body += r
            info += struct.pack(f'<I{n}I', n, *offs) + body
        while len(info) % 4: info += b'\0'
        struct.pack_into('<I', info, 4, len(info))
        struct.pack_into('<8I', info, 8, *rec_offs)
        # FAT + FILE
        datas = [files.get(f, self.file(f)) for f in range(len(self.fat))] + list(new_files)
        fat_size = 12 + 16 * len(datas)
        symb = self.data[self.symb_off:self.symb_off + self.symb_size] if self.symb_off else b''
        info_off = (0x40 + len(symb) + 3) & ~3 if symb else 0x40
        fat_off = info_off + len(info)
        file_off = fat_off + fat_size
        out = bytearray(file_off + 16)
        out[0:0x40] = self.data[0:0x40]
        if symb: out[0x40:0x40 + len(symb)] = symb
        out[info_off:fat_off] = info
        pos = (file_off + 16 + 31) & ~31
        fat = bytearray(b'FAT ' + struct.pack('<II', fat_size, len(datas)))
        chunks = []
        for dd in datas:
            fat += struct.pack('<IIII', pos, len(dd), 0, 0)
            chunks.append((pos, dd))
            pos = (pos + len(dd) + 31) & ~31
        out[fat_off:file_off] = fat
        out += bytes(pos - len(out))
        for p, dd in chunks: out[p:p + len(dd)] = dd
        out[file_off:file_off + 16] = b'FILE' + struct.pack('<III', len(out) - file_off, len(datas), 0)
        struct.pack_into('<I', out, 8, len(out))
        struct.pack_into('<8I', out, 0x10, self.symb_off, self.symb_size, info_off, len(info), fat_off, fat_size,
                         file_off, len(out) - file_off)
        return bytes(out)


INST_TYPES = {1: 'pcm', 2: 'psg', 3: 'noise', 4: 'directpcm', 5: 'null', 16: 'drumset', 17: 'keysplit'}


def parse_sbnk(data):
    """SBNK: 'SBNK' header (0x10), 'DATA' block: magic, size, 32 reserved bytes, u32 count, then count records
    {u8 type, u16 offset (from the file start), u8 pad}. Type 1-5: one 10-byte note definition; 16 (drum set):
    u8 low key, u8 high key, then one {u16 type, 10 bytes} per key; 17 (key split): 8 region top keys (0 = unused),
    then one {u16 type, 10 bytes} per used region. A note definition: u16 wave (PSG: duty), u16 wave archive slot
    (0-3), u8 base key, u8 attack, u8 decay, u8 sustain, u8 release, u8 pan. Returns {program: (type, regions)} with
    regions [(low key, high key, kind, wave, archive slot, base key, attack, decay, sustain, release, pan)]."""
    assert data[:4] == b'SBNK', data[:4]
    n = struct.unpack_from('<I', data, 0x38)[0]
    out = {}
    for i in range(n):
        t, off, _ = struct.unpack_from('<BHB', data, 0x3C + 4 * i)
        if t == 0: continue
        if t < 16:
            out[i] = (t, [(0, 127, t) + struct.unpack_from('<HHBBBBBB', data, off)])
        elif t == 16:
            lo, hi = data[off], data[off + 1]
            out[i] = (t, [(lo + k, lo + k) + struct.unpack_from('<HHHBBBBBB', data, off + 2 + 12 * k)
                          for k in range(hi - lo + 1)])
        elif t == 17:
            tops = [x for x in data[off:off + 8] if x]
            regs, lo = [], 0
            for j, top in enumerate(tops):
                regs.append((lo, top) + struct.unpack_from('<HHHBBBBBB', data, off + 8 + 12 * j))
                lo = top + 1
            out[i] = (t, regs)
    return out


def build_sbnk(instruments):
    """The inverse of parse_sbnk: {program: (type, regions)} -> SBNK bytes (same layout as Black 2's own banks)."""
    n = max(instruments) + 1 if instruments else 0
    recs, body = bytearray(), bytearray()
    base = 0x3C + 4 * n
    for p in range(n):
        if p not in instruments:
            recs += struct.pack('<BHB', 0, 0, 0); continue
        t, regs = instruments[p]
        off = base + len(body)
        recs += struct.pack('<BHB', t, off, 0)
        if t < 16:
            r = regs[0]
            body += struct.pack('<HHBBBBBB', *r[3:11])
        elif t == 16:
            lo, hi = regs[0][0], regs[-1][1]
            body += bytes([lo, hi])
            for r in regs: body += struct.pack('<HHHBBBBBB', *r[2:11])
        else:
            tops = [r[1] for r in regs] + [0] * (8 - len(regs))
            body += bytes(tops)
            for r in regs: body += struct.pack('<HHHBBBBBB', *r[2:11])
        while len(body) % 4: body += b'\0'
    data = bytes(32) + struct.pack('<I', n) + recs + body
    block = b'DATA' + struct.pack('<I', 8 + len(data)) + data
    size = 0x10 + len(block)
    return b'SBNK' + struct.pack('<HHIHH', 0xFEFF, 0x0100, size, 0x10, 1) + block


def parse_swar(data):
    """SWAR: header, 'DATA' block: magic, size, 32 reserved bytes, u32 count, u32 offsets (from the file start);
    each wave is an SWAV without its file header (u8 encoding 0 PCM8 / 1 PCM16 / 2 IMA-ADPCM, u8 loop, u16 sample
    rate, u16 timer, u16 loop start (words), u32 length after the loop start (words), then the data)."""
    assert data[:4] == b'SWAR', data[:4]
    n = struct.unpack_from('<I', data, 0x38)[0]
    offs = struct.unpack_from(f'<{n}I', data, 0x3C)
    ends = list(offs[1:]) + [len(data)]
    return [data[o:e] for o, e in zip(offs, ends)]


def build_swar(waves):
    n = len(waves)
    head = 0x3C + 4 * n
    offs, body = [], bytearray()
    for w in waves:
        offs.append(head + len(body)); body += w
        while len(body) % 4: body += b'\0'
    data = bytes(32) + struct.pack('<I', n) + struct.pack(f'<{n}I', *offs) + body
    block = b'DATA' + struct.pack('<I', 8 + len(data)) + data
    return b'SWAR' + struct.pack('<HHIHH', 0xFEFF, 0x0100, 0x10 + len(block), 0x10, 1) + block


_IMA_STEP = [7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88,
             97, 107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658,
             724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660,
             4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818,
             18500, 20350, 22385, 24623, 27086, 29794, 32767]
_IMA_INDEX = [-1, -1, -1, -1, 2, 4, 6, 8]


def wave_info(w):
    enc, loop, rate, timer, loop_start, length = struct.unpack_from('<BBHHHI', w, 0)
    return dict(encoding=enc, loop=bool(loop), rate=rate, timer=timer, loop_start=loop_start * 4, length=length * 4)


def decode_wave(w):
    """An SWAR wave -> (float samples in -1..1, sample rate, loop start sample or None)."""
    import numpy as np
    i = wave_info(w)
    raw = w[12:]
    if i['encoding'] == 0:
        s = np.frombuffer(raw, dtype=np.int8).astype(np.float32) / 128
        ls = i['loop_start']
    elif i['encoding'] == 1:
        s = np.frombuffer(raw[:len(raw) // 2 * 2], dtype='<i2').astype(np.float32) / 32768
        ls = i['loop_start'] // 2
    else:
        pred, idx = struct.unpack_from('<hB', raw, 0)
        out = []
        for b in raw[4:]:
            for nib in (b & 15, b >> 4):
                step = _IMA_STEP[idx]
                diff = step >> 3
                if nib & 1: diff += step >> 2
                if nib & 2: diff += step >> 1
                if nib & 4: diff += step
                pred = max(-32768, min(32767, pred - diff if nib & 8 else pred + diff))
                idx = max(0, min(88, idx + _IMA_INDEX[nib & 7]))
                out.append(pred)
        s = np.array(out, dtype=np.float32) / 32768
        ls = max(0, (i['loop_start'] - 4) * 2)
    return s, i['rate'], (ls if i['loop'] else None)


def main(argv):
    if argv and argv[0] == '--selftest':
        s = SDAT(open(DEFAULT, 'rb').read())
        same = s.build() == s.data
        print('SDAT rebuild with no changes is byte-identical:', same)
        return 0 if same else 1
    path = argv[0] if argv and os.path.exists(argv[0]) else DEFAULT
    args = argv[1:] if argv and os.path.exists(argv[0]) else argv
    s = SDAT(open(path, 'rb').read())
    print(f'{path}: {len(s.data):,} B; SYMB {s.symb_size:,} INFO {s.info_size:,} FAT {s.fat_size:,} ({len(s.fat)} files) '
          f'FILE {s.file_size:,}')
    print('  counts:', {k: len(v) for k, v in s.info.items()})
    want = args or []
    for k in KINDS:
        if want and k not in want and not any(w.startswith(('SEQ_', 'BANK_', 'WAVE_', 'PLAYER_', 'GROUP_')) for w in want):
            continue
        for i, e in enumerate(s.info[k]):
            if e is None: continue
            nm = s.name(k, i)
            if want and k not in want and nm not in want: continue
            extra = {x: y for x, y in e.items() if not x.startswith('_')}
            if 'file' in e and k not in ('player', 'group', 'player2'):
                extra['size'] = s.fat[e['file']][1]
            if k == 'seq':
                extra['bank'] = f"{e['bank']} {s.name('bank', e['bank'])}"
                extra['player'] = f"{e['player']} {s.name('player', e['player'])}"
            if k == 'bank':
                extra['wavearcs'] = [f'{w} {s.name("wavearc", w)}' for w in e['wavearcs']]
            print(f'{k} {i} {nm}: {extra}')


if __name__ == '__main__':
    main(sys.argv[1:])
