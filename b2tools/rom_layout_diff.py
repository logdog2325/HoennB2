"""Compare the file layout of two NDS ROMs (ruby_infra 2026-10-08; notes/RUBY.md 3.3 test 2).

    python3 rom_layout_diff.py A.nds B.nds [--content] [--all]

The game keeps the ROM's file table (FAT) in RAM and reads overlays through it, so a savestate made on ROM A only
works on ROM B when both lay out their files identically (build_rom.py RESERVE). This compares what the game reads
from the ROM's tables (GBATEK "DS Cartridge Header", "DS Cartridge NitroROM and NitroARC File Systems"):
  - header: ARM9/ARM7 offset and size, FNT/FAT/OVT offsets and sizes, banner offset, used ROM size (0x20-0x84)
  - FNT (file names and directory order): bytes compared
  - FAT (u32 start, u32 end per file id; overlays are file ids named by the OVT, NitroFS files by the FNT)
  - ARM9/ARM7 overlay tables (32 bytes per overlay: id, RAM address, RAM size, BSS size, static initialisers,
    file id, compressed size | flags << 24)
--content also lists the files whose bytes differ while their FAT entries are equal (what padding absorbed: an
archive in build_rom.py RESERVE, or one a patch keeps at Black 2's size), with each one's unused padding at the end
(trailing zero bytes of the larger of the two). --all prints every differing file, not only the first 40.
Exit status 0 when the layout (header tables, FNT, FAT, OVTs) is identical, 1 otherwise.
"""
import hashlib, os, struct, sys

HEADER = [(0x20, 'arm9 rom offset'), (0x2C, 'arm9 size'), (0x30, 'arm7 rom offset'), (0x3C, 'arm7 size'),
          (0x40, 'FNT offset'), (0x44, 'FNT size'), (0x48, 'FAT offset'), (0x4C, 'FAT size'),
          (0x50, 'ARM9 OVT offset'), (0x54, 'ARM9 OVT size'), (0x58, 'ARM7 OVT offset'), (0x5C, 'ARM7 OVT size'),
          (0x68, 'banner offset'), (0x80, 'used ROM size'), (0x84, 'header size')]

class Rom:
    def __init__(self, path):
        self.path = path
        self.d = open(path, 'rb').read()
        d = self.d
        self.h = {name: struct.unpack_from('<I', d, off)[0] for off, name in HEADER}
        fnt, fnt_size = self.h['FNT offset'], self.h['FNT size']
        fat, fat_size = self.h['FAT offset'], self.h['FAT size']
        self.fnt = d[fnt:fnt + fnt_size]
        self.fat = [struct.unpack_from('<II', d, fat + 8 * i) for i in range(fat_size // 8)]
        self.names = {}
        def walk(dir_id, prefix):
            sub, first, _ = struct.unpack_from('<IHH', d, fnt + 8 * (dir_id & 0xFFF))
            p, fid = fnt + sub, first
            while True:
                n = d[p]; p += 1
                if n == 0: break
                name = d[p:p + (n & 0x7F)].decode('ascii', 'replace'); p += n & 0x7F
                if n & 0x80:
                    walk(struct.unpack_from('<H', d, p)[0], prefix + name + '/'); p += 2
                else:
                    self.names[fid] = prefix + name; fid += 1
        walk(0xF000, '')
        self.ovt = {}
        for cpu, off_key, size_key in (('arm9', 'ARM9 OVT offset', 'ARM9 OVT size'), ('arm7', 'ARM7 OVT offset', 'ARM7 OVT size')):
            o, n = self.h[off_key], self.h[size_key]
            for k in range(n // 32):
                e = struct.unpack_from('<8I', d, o + 32 * k)
                self.ovt[(cpu, e[0])] = e
                self.names.setdefault(e[6], f'{cpu} overlay {e[0]:03d} ({"ov" if cpu == "arm9" else "arm7_ov"}{e[0]:03d})')

    def name(self, fid):
        return self.names.get(fid, f'file {fid}')

    def file(self, fid):
        s, e = self.fat[fid]
        return self.d[s:e]

def reserve_note(name):
    """What keeps an archive's size fixed (build_rom.py RESERVE, or a patch), for --content."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import build_rom
        if name.startswith('a/') and len(name) == 7:
            arc = int(name[2] + name[4] + name[6])
            if arc in build_rom.RESERVE: return f'RESERVE[{arc}] {build_rom.RESERVE[arc] >> 10} KB'
            known = {26: 'title.py pads to Black 2\'s size', 89: 'trainers.py keep_size', 90: 'trainers.py keep_size',
                     91: 'trainers.py keep_size', 2: 'text.py fixed slots'}
            if arc in known: return known[arc]
    except Exception:
        pass
    return 'same size'

def trailing_zeros(b):
    return len(b) - len(b.rstrip(b'\0'))

def main(args):
    paths = [a for a in args if not a.startswith('--')]
    if len(paths) != 2: print(__doc__); return 2
    a, b = Rom(paths[0]), Rom(paths[1])
    ok = True
    print(f'A {a.path}\n  sha1 {hashlib.sha1(a.d).hexdigest()}, {len(a.d)} bytes\nB {b.path}\n  sha1 {hashlib.sha1(b.d).hexdigest()}, {len(b.d)} bytes')
    diff_h = [k for k in a.h if a.h[k] != b.h[k]]
    for k in diff_h:
        layout = k not in ('arm9 size', 'arm7 size')
        ok &= not layout
        print(f'header {k}: {a.h[k]:#x} vs {b.h[k]:#x}' + ('' if layout else ' (code size: boot only, not a file-table entry)'))
    if not diff_h: print('header: tables at the same offsets and sizes')
    print('FNT: identical (same names, same directory order)' if a.fnt == b.fnt else 'FNT: DIFFERENT')
    ok &= a.fnt == b.fnt
    if len(a.fat) != len(b.fat):
        print(f'FAT: {len(a.fat)} vs {len(b.fat)} files'); ok = False
    moved = [(i, x, y) for i, (x, y) in enumerate(zip(a.fat, b.fat)) if x != y]
    if moved:
        ok = False
        print(f'FAT: {len(moved)} entries differ')
        for i, (s0, e0), (s1, e1) in moved[:200]:
            what = 'start moved' if s0 != s1 else f'same start, end {e1 - e0:+d} bytes'
            print(f'  {i:5d} {a.name(i)}: {s0:#x}-{e0:#x} vs {s1:#x}-{e1:#x} ({what})')
    else:
        print(f'FAT: identical ({len(a.fat)} files, every start and end)')
    ovt_diff = [k for k in sorted(set(a.ovt) | set(b.ovt)) if a.ovt.get(k) != b.ovt.get(k)]
    for k in ovt_diff:
        ok = False
        ea, eb = a.ovt.get(k), b.ovt.get(k)
        print(f'OVT {k[0]} overlay {k[1]}: {ea} vs {eb}')
    if not ovt_diff: print(f'OVT: identical ({len(a.ovt)} overlays: RAM addresses, sizes, compressed sizes)')
    if '--content' in args and len(a.fat) == len(b.fat):
        same = [i for i in range(len(a.fat)) if a.fat[i] == b.fat[i] and a.file(i) != b.file(i)]
        print(f'content: {len(same)} files differ inside an identical FAT entry'
              + (' (their changes fit the same size):' if same else ''))
        lim = None if '--all' in args else 40
        for i in same[:lim]:
            fa, fb = a.file(i), b.file(i)
            nd = sum(1 for x, y in zip(fa, fb) if x != y)
            print(f'  {i:5d} {a.name(i)}: {len(fa)} bytes, {nd} differ; trailing zero padding {trailing_zeros(fa)} / '
                  f'{trailing_zeros(fb)} bytes ({reserve_note(a.name(i))})')
        if lim and len(same) > lim: print(f'  ... {len(same) - lim} more (--all)')
        rest = [i for i in range(len(a.fat)) if a.fat[i] != b.fat[i]]
        if rest: print(f'content: {len(rest)} files with other FAT entries (above)')
    print('LAYOUT IDENTICAL' if ok else 'LAYOUT DIFFERS')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
