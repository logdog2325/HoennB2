"""The starter screen's own graphics (overlay 316 "psel", archive a/2/0/2 = ARCID 202), made Hoenn.

What overlay 316 loads from a/2/0/2 (traced in its disassembly, `tools/dsd dis --overlay 316`):
- per starter i (table data_ov316_0219fac0, 5 bytes each: 0c 00 15 19 01 / 0d 02 16 1a 03 / 0e 04 17 1b 05):
  NCGR 12+i = the coloured picture shown when its ball is picked (96x96 OBJ, 144 tiles 4bpp in the order
  64x64, 32x64, 64x32, 32x32; cell NCER 21+i, animation NANR 25+i), palettes 2i (colours) and 2i+1 (dark), of which
  func_ov316_0219eaf0 copies the first 16 colours and fades between them into OBJ palette slot i
  (func_ov316_0219ebe0). Slot i is also the palette of the small silhouette, which is the species' own front still
  from a/0/0/4 (func_ov316_0219d534 -> MakePokeGraArcHandle, species from the table at ov316 0x2C14; patch
  `starters`). Black 2's pictures are hand-made 2x redraws of Snivy/Tepig/Oshawott's stills (Snivy 40x37 -> 80x77);
  ours are Treecko/Torchic/Mudkip's Black 2 stills scaled 2x with Scale2x (no new colours), dark palettes made like
  Black 2's (each 5-bit channel at about 11%).
- the 3D scene (data_ov316_0219fbf0: files 34-37, 39-41): model 34 `psel_s02` is Bianca (materials bell_*, skinned
  to her joints) holding the case (case_m/grip/huta, its own nodes under the root) in front of a room (haikei);
  39 `psel_mb` are the balls. Bianca is taken out by turning her shapes' draw commands (SBC `SHP`, 2 bytes) into
  NOPs (00 00); everything else is untouched. Files 29-33 (`psel_s01`, Black/White's gift box) are not loaded.
- also used: NSCR 18-20 + NCGR 15/16 (grass/fire/water top-screen backgrounds), NCGR 17/NCER 24/NANR 28 (the ball
  ring), palettes 6-11, curves 33/38: no Unova content. Texts come from script text 169 lines 35-44 (captions by
  type, "Choose a Pokemon.", YES/NO), which name no one.
"""
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sprites import lz11_decompress
from title_art import ncgr_tiles

ARC_PSEL, ARC_POKEGRA = 202, 4
STARTERS = (252, 255, 258)            # Treecko, Torchic, Mudkip (left, middle, right ball)
ORDER = [(0, 0, 64, 64), (64, 0, 32, 64), (0, 64, 64, 32), (64, 64, 32, 32)]   # OBJ order of a 96x96 still

# ------------------------------------------------------------------------------------------------- 2D pictures

def still_pixels(u):
    """96*96 palette indices of an uncompressed 96x96 OBJ-ordered NCGR."""
    _, tiles = ncgr_tiles(u)
    pix = bytearray(96 * 96); k = 0
    for ox, oy, ow, oh in ORDER:
        for t in range(ow * oh // 64):
            tx, ty = ox + t % (ow // 8) * 8, oy + t // (ow // 8) * 8
            for j in range(64): pix[(ty + j // 8) * 96 + tx + j % 8] = tiles[k][j]
            k += 1
    assert k == len(tiles) == 144
    return pix

def fits(pix):
    """True if the whole figure lies inside the middle 48x48 (so 2x about the centre loses nothing)."""
    return all(p == 0 for i, p in enumerate(pix) if not (24 <= i % 96 < 72 and 24 <= i // 96 < 72))

def scale2x(pix):
    """2x about the picture's centre (48, 48) with Scale2x (AdvMAME2x): edges smoothed, no new colours."""
    src = lambda x, y: pix[(y + 24) * 96 + x + 24] if 0 <= x < 48 and 0 <= y < 48 else 0
    out = bytearray(96 * 96)
    for y in range(48):
        for x in range(48):
            p = src(x, y); a, b, c, d = src(x, y - 1), src(x + 1, y), src(x - 1, y), src(x, y + 1)
            e = [p, p, p, p]
            if b != c and a != d:
                if c == a: e[0] = a
                if a == b: e[1] = b
                if d == c: e[2] = c
                if b == d: e[3] = d
            out[2 * y * 96 + 2 * x], out[2 * y * 96 + 2 * x + 1] = e[0], e[1]
            out[(2 * y + 1) * 96 + 2 * x], out[(2 * y + 1) * 96 + 2 * x + 1] = e[2], e[3]
    return out

def ncgr_with(template, pix):
    """`template` (psel's own 96x96 OBJ NCGR, 4bpp, 144 tiles) with new pixels in the same OBJ order."""
    u = bytearray(template)
    th, tw, depth, mapping, tiled, size, off = struct.unpack_from('<HHIIIII', u, 0x18)
    assert depth == 3 and size == 144 * 32, (depth, size)
    tiles = []
    for ox, oy, ow, oh in ORDER:
        for t in range(ow * oh // 64):
            tx, ty = ox + t % (ow // 8) * 8, oy + t // (ow // 8) * 8
            tiles.append([pix[(ty + j // 8) * 96 + tx + j % 8] for j in range(64)])
    u[0x18 + off:0x18 + off + size] = bytes((t[i] & 15) | (t[i + 1] & 15) << 4 for t in tiles for i in range(0, 64, 2))
    return bytes(u)

def pal16(nclr):
    size, off = struct.unpack_from('<II', nclr, 0x20)
    return list(struct.unpack_from('<16H', nclr, 0x18 + off))

def nclr_with(template, cols16):
    """`template` with its first 16 colours replaced (the code copies only those 32 bytes)."""
    u = bytearray(template)
    size, off = struct.unpack_from('<II', u, 0x20)
    struct.pack_into('<16H', u, 0x18 + off, *cols16)
    return bytes(u)

def dark(c):
    """Black 2's silhouette palettes (1/3/5 against 0/2/4): each 5-bit channel at about 11%."""
    return sum(int((c >> s & 31) * 0.11 + 0.5) << s for s in (0, 5, 10))

# ------------------------------------------------------------------------------------------------- 3D (BMD0)

def _dict(d, off):
    """Nitro dictionary at `off`: [(name, offset of the entry's data)]."""
    num = d[off + 1]
    p = off + struct.unpack_from('<H', d, off + 6)[0]     # past the header and the tree (size includes the 4-byte head)
    esz, dsz = struct.unpack_from('<HH', d, p)
    return [(d[p + dsz + 16 * i:p + dsz + 16 * i + 16].rstrip(b'\0').decode('latin1'), p + 4 + i * esz)
            for i in range(num)]

def bmd_models(d):
    """[{name, sbc, sbc_end, objs, mats, shps}] of a BMD0 (render command list = sbc .. the material block)."""
    assert d[:4] == b'BMD0'
    mdl0 = struct.unpack_from('<I', d, 0x10)[0]
    assert d[mdl0:mdl0 + 4] == b'MDL0'
    out = []
    for name, doff in _dict(d, mdl0 + 8):
        moff = mdl0 + struct.unpack_from('<I', d, doff)[0]
        _, sbc, mat, shp, _ = struct.unpack_from('<5I', d, moff)
        out.append(dict(name=name, sbc=moff + sbc, sbc_end=moff + mat, objs=[n for n, _ in _dict(d, moff + 0x40)],
                        mats=[n for n, _ in _dict(d, moff + mat + 4)], shps=[n for n, _ in _dict(d, moff + shp)]))
    return out

# SBC command lengths (NitroSystem render commands; 0x09 NODEMIX and 0x0A CALLDL have their own)
_LEN = {0x00: 1, 0x01: 1, 0x02: 3, 0x03: 2, 0x04: 2, 0x24: 2, 0x44: 2, 0x05: 2, 0x06: 4, 0x26: 5, 0x46: 5, 0x66: 6,
        0x07: 2, 0x27: 3, 0x47: 3, 0x67: 4, 0x08: 2, 0x28: 3, 0x48: 3, 0x68: 4, 0x0B: 1, 0x2B: 1, 0x0C: 3, 0x0D: 3}

def sbc_commands(d, start, end):
    """[(offset, opcode, bytes)] up to and including RET (0x01); raises on an unknown opcode."""
    p, out = start, []
    while p < end:
        op = d[p]
        ln = 3 + 3 * d[p + 2] if op == 0x09 else 9 if op == 0x0A else _LEN[op]
        out.append((p, op, d[p:p + ln])); p += ln
        if op == 0x01: return out
    raise ValueError('render commands without RET')

def hide_materials(bmd, prefix):
    """NOP (00 00) every SHP command drawn with a material named `prefix`*. -> (new bytes, [shape names])"""
    d = bytearray(bmd); hidden = []
    for m in bmd_models(bmd):
        cur = None
        for p, op, b in sbc_commands(bmd, m['sbc'], m['sbc_end']):
            if op & 0x1F == 0x04: cur = m['mats'][b[1]]
            elif op == 0x05 and cur and cur.startswith(prefix):
                d[p:p + 2] = b'\0\0'; hidden.append(m['shps'][b[1]])
    return bytes(d), hidden

# ------------------------------------------------------------------------------------------------- the patch

def hoenn_entries(psel, pokegra, species=STARTERS):
    """{a/2/0/2 index: new bytes} from the original psel entries and the pokegra archive (lists of bytes)."""
    out = {}
    for i, sp in enumerate(species):
        pix = still_pixels(lz11_decompress(pokegra[sp * 20]))          # +0: front still (LZ11)
        assert fits(pix), f'species {sp}: figure larger than 48x48'
        out[12 + i] = ncgr_with(psel[12 + i], scale2x(pix))
        pal = pokegra[sp * 20 + 18]                                      # +18: normal palette
        cols = pal16(lz11_decompress(pal) if pal[0] == 0x11 else pal)
        out[2 * i] = nclr_with(psel[2 * i], cols)
        out[2 * i + 1] = nclr_with(psel[2 * i + 1], [cols[0]] + [dark(c) for c in cols[1:]])
    out[34], hidden = hide_materials(psel[34], 'bell_')
    assert len(hidden) in (14, 0), hidden            # Bianca's 14 shapes (polygon12-25); 0 = already done (no --clean)
    for k, v in out.items(): assert len(v) == len(psel[k]), k            # same sizes: the ROM layout stays
    return out
