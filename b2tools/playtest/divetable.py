"""The dive table (patches/dive.py, a/1/2/6 file 297): {zone: [(x0, z0, w, h, dest, ax, az, flags, tiles)]}."""
import struct
from pt import rom
def table():
    d = rom().ents[297]
    out = {}
    nz = len(rom().hdr)
    for z in range(nz):
        if 2 * z + 2 > len(d): break
        v = struct.unpack_from('<H', d, 2 * z)[0]
        if not v: continue
        off, cnt = (v >> 4) * 16, v & 15
        recs = []
        for k in range(cnt):
            x0, z0, w, h, dest, ax, az, mo, fl = struct.unpack_from('<HHBBHhhHH', d, off + 16 * k)
            bm = d[mo:mo + w * h]
            tiles = [(x0 + i, z0 + j) for j in range(h) for i in range(w) if bm[j * w + i]]
            recs.append(dict(x0=x0, z0=z0, w=w, h=h, dest=dest, ax=ax, az=az, flags=fl, tiles=tiles))
        out[z] = recs
    return out
if __name__ == '__main__':
    import sys; sys.path.insert(0, '.')
    import places as PL
    for z, rs in table().items():
        for r in rs: print(z, PL.NAME.get(z), '->', r['dest'], PL.NAME.get(r['dest']), len(r['tiles']), r['tiles'][:2], 'flags', r['flags'], (r['ax'], r['az']))
