"""Make every polygon's first vertex absolute in an NSBMD (buildings_audit, 2026-10-08).

CTRMap's NSBMD writer (b2tools/java/ToNsbmd.java) encodes a vertex near its polygon's node origin (the material's
bounding-box centre) as VTX_DIFF / VTX_XY / VTX_XZ / VTX_YZ, counting from (0, 0, 0) at the start of every polygon's
display list. The DS geometry engine keeps the last vertex across polygons (and display lists): those commands are
relative to whatever vertex was drawn before, so the polygon's first triangle came out sheared and the triangle it
belonged to went missing (Sky Pillar top's stairs: a sky-coloured triangle beside a slanted face, DeSmuME; the same
model written without that vertex command draws right). 7 of the 4,708 polygons of the 422 world cells began so.

fix_first_vertex(bmd) rewrites such a first vertex command as VTX_10 (absolute, same size: 1 parameter): the position
the writer meant, rounded to VTX_10's 1/64 of a model unit (at most 32/4096 off per axis, under 0.1 world units at a
cell's scale). Every other byte stays. Display lists are parsed as b2tools ... dlist.py does (GX command packing).

    python3 nsbmd_fix.py MODEL.nsbmd [...]       (report only)
"""
import struct, sys, os

PARAMS = {0x00: 0, 0x10: 1, 0x11: 0, 0x12: 1, 0x13: 1, 0x14: 1, 0x15: 0, 0x16: 16, 0x17: 12, 0x18: 16, 0x19: 12, 0x1A: 9,
          0x1B: 3, 0x1C: 3, 0x20: 1, 0x21: 1, 0x22: 1, 0x23: 2, 0x24: 1, 0x25: 1, 0x26: 1, 0x27: 1, 0x28: 1, 0x29: 1,
          0x2A: 1, 0x2B: 1, 0x30: 1, 0x31: 1, 0x32: 1, 0x33: 1, 0x34: 32, 0x40: 1, 0x41: 0, 0x50: 1, 0x60: 1, 0x70: 3,
          0x71: 2, 0x72: 1}
VTX = (0x23, 0x24, 0x25, 0x26, 0x27, 0x28)

def _s(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v

def _dict(d, off):
    cnt = d[off + 1]
    tree = off + 4 + 8 + 4 * cnt
    unit, _ = struct.unpack_from('<HH', d, tree)
    return [d[tree + 4 + unit * j:tree + 4 + unit * (j + 1)] for j in range(cnt)]

def _polygons(b):
    """(display list start, length) of every polygon of every model in a BMD0."""
    nb = struct.unpack_from('<H', b, 0xE)[0]
    mdl = next((o for o in (struct.unpack_from('<I', b, 0x10 + 4 * k)[0] for k in range(nb)) if b[o:o + 4] == b'MDL0'), None)
    if mdl is None: return
    for ent in _dict(b, mdl + 8):
        m = mdl + struct.unpack_from('<I', ent, 0)[0]
        meshes = m + struct.unpack_from('<I', b, m + 0xC)[0]
        for pe in _dict(b, meshes):
            p = meshes + struct.unpack_from('<I', pe, 0)[0]
            off, ln = struct.unpack_from('<II', b, p + 8)
            yield p + off, ln

def fix_first_vertex(bmd):
    """-> (new bytes, number of polygons changed). Same length as bmd."""
    if bmd[:4] != b'BMD0': return bmd, 0
    out = bytearray(bmd); fixed = 0
    for start, ln in _polygons(bmd):
        i, end, done = start, start + ln, False
        while i < end and not done:
            word = i; cmds = list(bmd[i:i + 4]); i += 4
            for slot, c in enumerate(cmds):
                n = PARAMS.get(c)
                if n is None: done = True; break                  # (unknown command: leave the polygon alone)
                if c in VTX:
                    if c in (0x25, 0x26, 0x27, 0x28):            # relative to the vertex before: as the writer meant it,
                        p = struct.unpack_from('<I', bmd, i)[0]   # from (0, 0, 0)
                        if c == 0x28: v = [_s(p, 10), _s(p >> 10, 10), _s(p >> 20, 10)]
                        elif c == 0x25: v = [_s(p, 16), _s(p >> 16, 16), 0]
                        elif c == 0x26: v = [_s(p, 16), 0, _s(p >> 16, 16)]
                        else: v = [0, _s(p, 16), _s(p >> 16, 16)]
                        q = [max(-512, min(511, int(round(x / 64)))) & 0x3FF for x in v]
                        out[word + slot] = 0x24
                        struct.pack_into('<I', out, i, q[0] | q[1] << 10 | q[2] << 20)
                        fixed += 1
                    done = True; break
                i += 4 * n
    return bytes(out), fixed

# Black 2's round-tree materials (b2_trees, 2026-10-11). In all 96 Black 2 chunks with the round tree (ki03: Route 6,
# Route 7 ...) its four materials have diffuse 25/31 with "diffuse is the vertex colour" set and ambient 31
# (NNSG3dResMatData diffAmb 0x7fffe739), and the side cards ki03ax are drawn from both sides (polyAttr 0x1f80c1, the
# others 0x1f8081; apicula info "Cull: None"). CTRMap's writer gives every material diffuse 31 (0x7fff7fff) and
# back-face culling, so our trees' tops came out brighter than Black 2's. The snowy ash copies (*_y) are the same trees.
B2_TREE_DIFFAMB = 0x7fffe739
TREE_MATS = {'ki03ax', 'ki03bx', 'ki03dx', 'ki02c', 'ki03ax_y', 'ki03bx_y', 'ki03dx_y',
             'ki04ax', 'ki04bx', 'ki04c', 'ki04dx'}       # (+ Humilau's palm, terrain/palms.py: the same values there)
TWO_SIDED = {'ki03ax', 'ki03ax_y', 'ki04ax'}
POLY_BACK = 0x40                                   # GX polygon attribute: render back faces

def _ndict(d, o):
    """NNSG3dResDict at o: [(data bytes offset, name)]."""
    n = d[o + 1]; e = o + struct.unpack_from('<H', d, o + 6)[0]
    unit = struct.unpack_from('<H', d, e)[0]
    names = e + 4 + unit * n
    return [(e + 4 + unit * i, bytes(d[names + 16 * i:names + 16 * i + 16]).rstrip(b'\0').decode('ascii', 'replace'))
            for i in range(n)]

def tree_materials(bmd):
    """-> (new bytes, materials changed): Black 2's material values on the round-tree materials (see TREE_MATS)."""
    if bmd[:4] != b'BMD0': return bmd, 0
    d = bytearray(bmd); n = 0
    mdl = struct.unpack_from('<I', d, 16)[0]
    for ent, _ in _ndict(d, mdl + 8):
        m = mdl + struct.unpack_from('<I', d, ent)[0]
        mo = m + struct.unpack_from('<I', d, m + 8)[0]          # NNSG3dResMdl ofsMat
        for me, name in _ndict(d, mo + 4):
            if name not in TREE_MATS: continue
            at = mo + struct.unpack_from('<I', d, me)[0]        # NNSG3dResMatData: tag, size, diffAmb, specEmi, polyAttr
            struct.pack_into('<I', d, at + 4, B2_TREE_DIFFAMB)
            if name in TWO_SIDED:
                struct.pack_into('<I', d, at + 12, struct.unpack_from('<I', d, at + 12)[0] | POLY_BACK)
            n += 1
    return bytes(d), n

if __name__ == '__main__':
    for f in sys.argv[1:]:
        b = open(f, 'rb').read()
        nb, k = fix_first_vertex(b)
        print(f, k, 'polygon(s) start relative')
