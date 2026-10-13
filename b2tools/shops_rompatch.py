"""Shops agent test helper: apply the build patch `shops` (b2tools/patches/shops.py) to an already built ROM in place,
for agent test builds whose patch list (b2tools/agent_build_rooms.sh) does not have it yet.

    python3 shops_rompatch.py work/agents/shops/rom/hoenn.nds

The patch keeps a/2/8/2 and a/2/8/3 at their sizes, so the files are rewritten where they are (FAT unchanged)."""
import os, sys, struct, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))


def fs_files(rom):
    fnt_off, fnt_size, fat_off, fat_size = struct.unpack_from('<IIII', rom, 0x40)
    def walk(dir_id, path):
        off = fnt_off + (dir_id & 0xFFF) * 8
        sub, first, _ = struct.unpack_from('<IHH', rom, off)
        p = fnt_off + sub; fid = first; out = {}
        while True:
            t = rom[p]; p += 1
            if t == 0: break
            ln = t & 0x7F; name = rom[p:p + ln].decode(); p += ln
            if t & 0x80:
                did = struct.unpack_from('<H', rom, p)[0]; p += 2
                out.update(walk(did, path + name + '/'))
            else:
                out[path + name] = fid; fid += 1
        return out
    return {k: struct.unpack_from('<II', rom, fat_off + 8 * v) for k, v in walk(0xF000, '').items()}


def main(path):
    import shops
    rom = bytearray(open(path, 'rb').read())
    fat = fs_files(rom)
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, 'a', '2', '8'))
        for f in ('a/2/8/2', 'a/2/8/3'):
            s, e = fat[f]; open(os.path.join(t, f), 'wb').write(rom[s:e])
        print(shops.apply(t))
        for f in ('a/2/8/2', 'a/2/8/3'):
            s, e = fat[f]; d = open(os.path.join(t, f), 'rb').read()
            assert len(d) == e - s, (f, len(d), e - s)
            rom[s:e] = d
    open(path + '.tmp', 'wb').write(rom); os.replace(path + '.tmp', path)
    print(path, 'patched in place')


if __name__ == '__main__':
    main(sys.argv[1])
