"""The FAIRY type icon (fairy_ui, 2026-10-08) and Black 2's type-icon formats.

Icon helpers: decode/encode Black 2's 32x16 4bpp 1D-mapped icons of a/0/8/2 and their palette.

Format (read from the files): RGCN, RAHC at 0x10, tiles h/w = 0xFFFF (1D OBJ), depth 3 (4bpp), mapping 0x10,
256 bytes = 8 tiles of 8x8, row-major (tiles 0-3 top row, 4-7 bottom row). Palette a/0/8/2 entry 33: RLCN/TTLP,
512 bytes = 16 rows of 16 BGR555 colours; row per type from arm9 data_0209208c (func_0202d7e8)."""
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

VANILLA = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
ARM9 = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build', 'arm9.bin')

def c5to8(c): return (c << 3) | (c >> 2)
def bgr(v): return (c5to8(v & 31), c5to8((v >> 5) & 31), c5to8((v >> 10) & 31))
def to555(rgb): r, g, b = (round(c * 31 / 255) for c in rgb[:3]); return r | g << 5 | b << 10

def icon_decode(ncgr, w=32, h=16):
    off = 0x18 + struct.unpack_from('<I', ncgr, 0x2C)[0]
    size = struct.unpack_from('<I', ncgr, 0x28)[0]
    raw = ncgr[off:off + size]
    tw = w // 8
    pix = [[0] * w for _ in range(h)]
    for t in range(size // 32):
        tx, ty = t % tw, t // tw
        for j in range(64):
            b = raw[t * 32 + j // 2]
            v = b & 15 if j % 2 == 0 else b >> 4
            pix[ty * 8 + j // 8][tx * 8 + j % 8] = v
    return pix

def icon_encode(ncgr, pix, w=32, h=16):
    out = bytearray(ncgr)
    off = 0x18 + struct.unpack_from('<I', ncgr, 0x2C)[0]
    size = struct.unpack_from('<I', ncgr, 0x28)[0]
    tw = w // 8
    raw = bytearray(size)
    for t in range(size // 32):
        tx, ty = t % tw, t // tw
        for j in range(0, 64, 2):
            lo = pix[ty * 8 + j // 8][tx * 8 + j % 8]
            hi = pix[ty * 8 + (j + 1) // 8][tx * 8 + (j + 1) % 8]
            raw[t * 32 + j // 2] = lo | hi << 4
    out[off:off + size] = raw
    return bytes(out)

def palette(nclr):
    size, off = struct.unpack_from('<II', nclr, 0x20)
    return list(struct.unpack_from(f'<{size // 2}H', nclr, 0x18 + off))

def set_palette(nclr, cols):
    size, off = struct.unpack_from('<II', nclr, 0x20)
    out = bytearray(nclr)
    struct.pack_into(f'<{size // 2}H', out, 0x18 + off, *cols)
    return bytes(out)

def type_rows():
    d = open(ARM9, 'rb').read()
    return list(d[0x0209208c - 0x02004000:0x0209208c - 0x02004000 + 24])

def cat_rows():
    d = open(ARM9, 'rb').read()
    return list(d[0x02092080 - 0x02004000:0x02092080 - 0x02004000 + 12])

# ---- the FAIRY icon ------------------------------------------------------------------------------------------
"""Build the FAIRY type icon from Black 2's own icons (fairy_ui; the user's art rule: recolour an existing icon frame,
letters from the existing icons' own letter pixels, nothing drawn from scratch, nothing downloaded).

Sources (a/0/8/2, type icon = entry 34 + type):
  frame  : FIRE (entry 43), border/fill indices 10/11 of palette row 0 -> 8/9 of row 2 (free colours in row 2)
  letters: F, I from FIRE; A, R from DARK (entry 50); Y from FLYING (entry 36). Glyph pixels = colour 15 (white) and
           14 (shadow 0x294a); everything else in a glyph cell becomes the fill. Spacing as Black 2's 5-letter words
           (GRASS: cells abut, the shadow column is the gap), centred like GRASS (columns 4-28).
Colours (BGR555, 5-bit per channel): fill = Gen 6 Fairy pink #EE99AC -> (29,19,21); border = darker, in the ratio Black
2's own icons use (border about half the fill: FIRE (30,10,6)/(14,4,1), PSYCHIC (31,14,20)/(13,7,7)) -> (15,9,11)."""

FILL = 29 | 19 << 5 | 21 << 10
BORDER = 15 | 9 << 5 | 11 << 10
ROW, C_BORDER, C_FILL = 2, 8, 9            # palette a/0/8/2 entry 33 row 2: colours 8-13 unused (0x7c1f filler)
TYPE_FIRE, TYPE_DARK, TYPE_FLYING = 9, 16, 2
# (source type, first column, width) of each letter cell, rows 4-11 (glyph 7 rows + shadow row)
LETTERS = [(TYPE_FIRE, 5, 5), (TYPE_DARK, 11, 5), (TYPE_FIRE, 11, 4), (TYPE_DARK, 17, 5), (TYPE_FLYING, 11, 6)]
START = 4

def build(entries):
    """(new entry 51 bytes, new palette entry 33 bytes) from the a/0/8/2 entries."""
    src = {t: icon_decode(entries[34 + t]) for t in (TYPE_FIRE, TYPE_DARK, TYPE_FLYING)}
    fire = src[TYPE_FIRE]
    out = [[0] * 32 for _ in range(16)]
    for y in range(16):
        for x in range(32):
            v = fire[y][x]
            out[y][x] = {10: C_BORDER, 11: C_FILL}.get(v, v)
            if 4 <= y <= 11 and v in (14, 15): out[y][x] = C_FILL      # remove FIRE's letters
    x0 = START
    for t, col, w in LETTERS:
        for y in range(4, 12):
            for dx in range(w):
                v = src[t][y][col + dx]
                out[y][x0 + dx] = v if v in (14, 15) else C_FILL
        x0 += w
    assert x0 <= 29, x0
    # every pixel's colour is one of: 0 (transparent rows), border, fill, 14, 15
    assert {v for r in out for v in r} <= {0, C_BORDER, C_FILL, 14, 15}
    ncgr = icon_encode(entries[51], out)
    pal = palette(entries[33])
    assert pal[ROW * 16 + C_BORDER] == 0x7c1f and pal[ROW * 16 + C_FILL] == 0x7c1f, 'row 2 colours 8/9 not free'
    pal[ROW * 16 + C_BORDER], pal[ROW * 16 + C_FILL] = BORDER, FILL
    return ncgr, set_palette(entries[33], pal), out

if __name__ == '__main__':
    # review sheet: python3 fairy_art.py OUT.png (screenshots/fairy_ui/01_icon_review.png)
    import narcio
    sys.path.insert(0, os.path.join(HERE, 'patches'))
    import fairy_ui
    from PIL import Image, ImageDraw
    S = 4
    NAMES = 'Normal Fighting Flying Poison Ground Rock Bug Ghost Steel Fire Water Grass Electric Psychic Ice Dragon Dark Fairy'.split()

    def icon_img(pix, pal, row, scale=S):
        im = Image.new('RGB', (32, 14), (255, 255, 255))
        for y in range(2, 16):
            for x in range(32):
                v = pix[y][x]
                if v: im.putpixel((x, y - 2), bgr(pal[row * 16 + v]))
        return im.resize((32 * scale, 14 * scale), Image.NEAREST)

    e = narcio.load(VANILLA, 82)
    ncgr, nclr, _ = build(e)
    pal_old, pal_new = palette(e[33]), palette(nclr)
    rows = type_rows(); rows[17] = ROW
    W = 6 * 40 * S + 16
    sheet = Image.new('RGB', (W, 640 + 30 * S + 300), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    d.text((8, 4), "Black 2's 17 type icons (a/0/8/2 34-50) and the new FAIRY icon (entry 51, type 17)", fill=(0, 0, 0))
    for t in range(18):
        pix = icon_decode(ncgr if t == 17 else e[34 + t])
        im = icon_img(pix, pal_new, rows[t])
        cx, cy = 8 + (t % 6) * 40 * S, 20 + (t // 6) * 22 * S
        sheet.paste(im, (cx, cy))
        d.text((cx, cy + 14 * S + 2), NAMES[t] + ('  <- NEW' if t == 17 else ''), fill=(200, 0, 80) if t == 17 else (0, 0, 0))
    y0 = 20 + 3 * 22 * S + 10
    d.text((8, y0), 'How it was made: FIRE frame recoloured (border/fill -> palette 33 row 2 colours 8/9), letters taken from '
           'FIRE (F, I), DARK (A, R), FLYING (Y):', fill=(0, 0, 0))
    srcs = [(9, 'FIRE'), (16, 'DARK'), (2, 'FLYING')]
    for k, (t, n) in enumerate(srcs):
        im = icon_img(icon_decode(e[34 + t]), pal_old, rows[t], 6)
        sheet.paste(im, (8 + k * 36 * 6, y0 + 14))
    im = icon_img(icon_decode(ncgr), pal_new, ROW, 6)
    sheet.paste(im, (8 + 3 * 36 * 6, y0 + 14))
    d.text((8 + 3 * 36 * 6, y0 + 14 + 14 * 6 + 2), 'FAIRY', fill=(200, 0, 80))
    # colour swatches
    y1 = y0 + 14 + 14 * 6 + 24
    d.text((8, y1), f'Fairy pinks (BGR555): fill {FILL:#06x} = Gen 6 #EE99AC, border {BORDER:#06x}; '
           'battle-button ramp (a/0/1/1 572, from Psychic 469):', fill=(0, 0, 0))
    bt = palette(narcio.load(VANILLA, 11)[469])
    ramp = fairy_ui.gradient(bt[8:14], fairy_ui.FAIRY_RGB)
    for k, c in enumerate([FILL, BORDER] + bt[8:14] + ramp):
        x = 8 + k * 44 + (20 if k >= 2 else 0) + (20 if k >= 8 else 0)
        d.rectangle((x, y1 + 14, x + 40, y1 + 40), fill=bgr(c))
    d.text((8 + 2 * 44 + 20, y1 + 44), 'Psychic button ramp', fill=(0, 0, 0))
    d.text((8 + 8 * 44 + 40, y1 + 44), 'Fairy button ramp', fill=(0, 0, 0))
    sheet = sheet.crop((0, 0, W, y1 + 64))
    sheet.save(sys.argv[1]); print(sys.argv[1])
