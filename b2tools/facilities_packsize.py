"""The facilities agent's memory check: sizes of the interior areas' building packs and texture sets in a built ROM.

    python3 facilities_packsize.py [ROM] [AREA ...]     (default: work/agents/facilities/rom/hoenn.nds, the areas below)

Reads the ROM's own file system (NDS header: FNT at 0x40, FAT at 0x48; FNT main table of 8-byte entries, sub-tables of
length-prefixed names, bit 7 = directory) and the area table a/0/1/3 (u16 pack, u16 texset, ...: notes/GEN5_MAPS.md),
then prints per area: interior building pack a/2/2/6 (models), its building textures a/1/7/5, and the map texture set
a/0/1/4, next to the same entries in the unmodified game.
"""
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b2files

ROOT = os.path.abspath(os.path.join(HERE, '..'))
FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
AREAS = [289, 298, 323, 330, 338, 284, 285]          # facilities rooms (+ the generated rooms' 284/285)

def nds_files(rom):
    """{path: bytes} reader for the ROM's file system."""
    d = open(rom, 'rb').read()
    fnt, fnt_size, fat, fat_size = struct.unpack_from('<IIII', d, 0x40)
    paths = {}
    def walk(dir_id, prefix):
        sub, first, _ = struct.unpack_from('<IHH', d, fnt + 8 * (dir_id & 0xFFF))
        p, fid = fnt + sub, first
        while True:
            n = d[p]; p += 1
            if n == 0: break
            name = d[p:p + (n & 0x7F)].decode('ascii'); p += n & 0x7F
            if n & 0x80:
                walk(struct.unpack_from('<H', d, p)[0], prefix + name + '/'); p += 2
            else:
                paths[prefix + name] = fid; fid += 1
    walk(0xF000, '')
    def read(path):
        s, e = struct.unpack_from('<II', d, fat + 8 * paths[path])
        return d[s:e]
    return read

def narc(data):
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.narc', delete=False) as f:
        f.write(data); name = f.name
    try: return b2files.narc_entries(name)
    finally: os.remove(name)

def main(rom, areas):
    read = nds_files(rom)
    raw = read('a/0/1/3')
    sets = {k: narc(read(p)) for k, p in (('pack', 'a/2/2/6'), ('btex', 'a/1/7/5'), ('tex', 'a/0/1/4'))}
    orig = {k: b2files.narc_entries(b2files.arc_path(FILES, a)) for k, a in (('pack', 226), ('btex', 175), ('tex', 14))}
    for a in areas:
        pack, texset = struct.unpack_from('<HH', raw, a * 10)
        p, b, t = len(sets['pack'][pack]), len(sets['btex'][pack]), len(sets['tex'][texset])
        op, ob, ot = len(orig['pack'][pack]), len(orig['btex'][pack]), len(orig['tex'][texset])
        print(f'area {a}: pack {pack} models {p / 1024:.1f} KB (game {op / 1024:.1f}) + textures {b / 1024:.1f} KB '
              f'(game {ob / 1024:.1f}) = {(p + b) / 1024:.1f} KB; map texture set {texset} {t / 1024:.1f} KB (game {ot / 1024:.1f})')

if __name__ == '__main__':
    a = sys.argv[1:]
    rom = a.pop(0) if a and a[0].endswith('.nds') else os.path.join(ROOT, 'work', 'agents', 'facilities', 'rom', 'hoenn.nds')
    main(rom, [int(x) for x in a] or AREAS)
