"""Sapphire's Poké Mart item lists (data/hoenn_shops.json, made by b2tools/shops_data.py) into Black 2's shop list
archive a/2/8/2 (u16 item ids per list file; shop id k reads file k + 6) and their counts into a/2/8/3 file 0 (one
byte per list file). How Black 2 reads them: see b2tools/shops_data.py.

a/2/8/2 keeps exactly its original size (1300 bytes): it is not padded by build_rom.py (RESERVE), and savestates
keep the ROM's file table in RAM, so a different size would be read short after loading a state. The patch fails
instead of growing it. Badge lists (files 0-5) and the empty files 32-79 are left as they are."""
import os, json, struct
import narcio
from b2files import arc_path

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')


def _pad_to(path, size):
    """Grow the NARC's GMIF (last section) with zero bytes to `size` (as build_rom.pad_archives does)."""
    data = bytearray(open(path, 'rb').read())
    assert len(data) <= size, f'{path}: {len(data)} bytes, over its fixed size {size}'
    hdr = struct.unpack_from('<H', data, 0xC)[0]
    off = hdr
    for _ in range(2):
        off += struct.unpack_from('<I', data, off + 4)[0]
    assert data[off:off + 4] == b'GMIF'
    extra = size - len(data)
    struct.pack_into('<I', data, off + 4, struct.unpack_from('<I', data, off + 4)[0] + extra)
    struct.pack_into('<I', data, 8, size)
    data += bytes(extra)
    open(path, 'wb').write(data)


def apply(files):
    shops = json.load(open(os.path.join(ROOT, 'data', 'hoenn_shops.json')))['shops']
    lists, counts = narcio.load(files, 282), narcio.load(files, 283)
    size0 = os.path.getsize(arc_path(files, 282))
    cnt = bytearray(counts[0])
    for k, s in shops.items():
        f = int(k) + 6
        assert 6 <= f < 32, f'shop id {k}: only Black 2\'s specialty slots (ids 0-25) are rewritten'
        assert 0 < len(s['ids']) < 256, f'shop id {k}: {len(s["ids"])} items'
        lists[f] = struct.pack(f'<{len(s["ids"])}H', *s['ids'])
        cnt[f] = len(s['ids'])
    counts[0] = bytes(cnt)
    narcio.save(files, 282, lists); narcio.save(files, 283, counts)
    _pad_to(arc_path(files, 282), size0)
    return f'{len(shops)} shop lists (ids {min(map(int, shops))}-{max(map(int, shops))}), a/2/8/2 kept at {size0} bytes'
