"""Title screen art for Pokémon Sapphire (notes/RESEARCH_TITLE.md option A): the formats of `a/0/2/6` and the new
"Pokémon Sapphire" logo.

    python3 title_art.py drafts         draw the logo drafts -> data/title/drafts/draft_N/{logo,strip}.png and the
                                        previews screenshots/title/logo_draft_N.png (+ _2x)
    python3 title_art.py use N          copy draft N to data/title/logo.png + strip.png (what patches/title.py packs)
    python3 title_art.py preview OUT    preview of both screens from the files in data/title/ (as the patch packs them;
                                        the bottom screen: Sapphire's title scene at frame 128, scene_image)
    HOENN_VERSION=ruby python3 title_art.py drafts | use N | preview OUT
                                        the same for Ruby: RUBY_DRAFTS -> data/title/ruby/ (version.py TABLE['title']),
                                        previews in screenshots/title/ruby/; the bottom screen shows Groudon

Formats (decoded from the game's own files, see RESEARCH_TITLE.md "The 2D files"; every builder below is checked by
decoding Black 2's own files and building them again):
- LZ10 (GBATEK "LZ77", header 0x10 + u24 size): what the title code loads with compressed = TRUE.
- NCGR 'RGCN' (header 0x10, 2 sections): RAHC (u16 tiles high, u16 tiles wide, u32 depth 3 = 4bpp / 4 = 8bpp,
  u32 mapping 0, u32 tiled 0, u32 data size, u32 data offset 0x18, then the tiles) + SOPC (16 bytes: u32 0,
  u16 tiles wide, u16 tiles high).
- NSCR 'RCSN': NRCS (u16 width px, u16 height px, u16 colour mode 0 = 16 / 1 = 256, u16 0, u32 data size, then
  u16 entries: tile | hflip << 10 | vflip << 11 | palette << 12).
- NCLR 'RLCN': TTLP (u32 depth, u32 0, u32 data size 0x200, u32 offset 0x10, then 256 BGR555 colours).

The top screen (sub engine) is one 256-colour palette shared by the logo (sub BG3, files 0/1/2) and the scrolling
crystal strip (sub BG2, file 3, same tiles): at most 512 8bpp tiles together. Index 0 is the backdrop colour.
The bottom screen (main BG3, files 8/9/10) is 4bpp, 16 palettes; palette 0 colour 0 is the backdrop.
"""
import os, struct, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import version  # noqa: E402  (HOENN_VERSION: Sapphire's or Ruby's title, version.py TABLE['title'])
TITLE = version.TABLE['title']
DATA = os.path.join(ROOT, *TITLE['data'].split('/'))      # data/title (Sapphire) or data/title/ruby (Ruby)
SHOTS = os.path.join(ROOT, 'screenshots', 'title', *([version.OVERLAY] if version.OVERLAY else []))   # previews
SRC_FILES = os.path.join(ROOT, 'external', 'pokebw2', 'extract', 'b2_us', 'files')
ARC_TITLE, ARC_POKEGRA = 26, 4
KYOGRE_STILL, KYOGRE_PAL = TITLE['still'], TITLE['pal']   # a/0/0/4: species * 20 + 0 (front still) / + 18 (normal
                                                           # palette): Sapphire 382 Kyogre 7640/7658, Ruby 383 Groudon

# ---------------------------------------------------------------------------------------------------- LZ10

def lz10_decompress(d):
    assert d[0] == 0x10, 'not LZ10'
    size = d[1] | d[2] << 8 | d[3] << 16; pos = 4; out = bytearray()
    while len(out) < size:
        flags = d[pos]; pos += 1
        for bit in range(8):
            if len(out) >= size: break
            if flags & (0x80 >> bit):
                x = d[pos] << 8 | d[pos + 1]; pos += 2
                n, disp = (x >> 12) + 3, (x & 0xfff) + 1
                for _ in range(n): out.append(out[-disp])
            else:
                out.append(d[pos]); pos += 1
    return bytes(out)

def lz10_compress(data):
    """LZ10 with an optimal parse (fewest bytes). Copies are 3..18 bytes from 2..4096 bytes back (distance 1 is
    never used, like Nintendo's VRAM-safe compressor). Output padded to a multiple of 4 like the game's files."""
    n = len(data)
    heads = {}; longest = [(0, 0)] * n
    for pos in range(n):
        best_len = best_disp = 0
        ml = min(18, n - pos)
        if ml >= 3:
            chain = heads.get(data[pos:pos + 3], ())
            for c in reversed(chain):
                d = pos - c
                if d > 0x1000: break
                if d < 2: continue
                l = 3
                while l < ml and data[c + l] == data[pos + l]: l += 1
                if l > best_len:
                    best_len, best_disp = l, d
                    if l == ml: break
        longest[pos] = (best_len, best_disp)
        if pos + 3 <= n: heads.setdefault(data[pos:pos + 3], []).append(pos)
    # cost in bits from each position to the end; a token costs its bytes * 8 + its flag bit
    cost = [0] * (n + 1); choice = [0] * n
    for pos in range(n - 1, -1, -1):
        best, pick = cost[pos + 1] + 9, 1
        l, _ = longest[pos]
        for k in range(3, l + 1):
            c = cost[pos + k] + 17
            if c < best: best, pick = c, k
        cost[pos] = best; choice[pos] = pick
    out = bytearray([0x10, n & 0xff, n >> 8 & 0xff, n >> 16 & 0xff])
    pos = 0
    while pos < n:
        flag_at = len(out); out.append(0); flags = 0
        for bit in range(8):
            if pos >= n: break
            k = choice[pos]
            if k >= 3:
                d = longest[pos][1] - 1
                flags |= 0x80 >> bit
                out += bytes([(k - 3) << 4 | d >> 8, d & 0xff]); pos += k
            else:
                out.append(data[pos]); pos += 1
        out[flag_at] = flags
    while len(out) % 4: out.append(0)
    assert lz10_decompress(bytes(out)) == bytes(data)
    return bytes(out)

# ---------------------------------------------------------------------------------------------------- NCGR / NSCR / NCLR

def bgr555_to_rgb(v): return tuple((c << 3) | (c >> 2) for c in (v & 31, v >> 5 & 31, v >> 10 & 31))
def rgb_to_bgr555(rgb): return sum(((c * 31 + 127) // 255) << (5 * i) for i, c in enumerate(rgb[:3]))
def to555(rgb): return bgr555_to_rgb(rgb_to_bgr555(rgb))   # the colour the DS shows for an 8-bit RGB

def ncgr_tiles(u):
    """Tiles of an uncompressed NCGR: (bits per pixel, [64 palette indices per tile])."""
    assert u[:4] == b'RGCN' and u[0x10:0x14] == b'RAHC'
    th, tw, depth, mapping, tiled, size, off = struct.unpack_from('<HHIIIII', u, 0x18)
    raw = u[0x18 + off:0x18 + off + size]
    if depth == 4:
        return 8, [bytes(raw[i:i + 64]) for i in range(0, size, 64)]
    assert depth == 3
    px = bytes(b for v in raw for b in (v & 15, v >> 4))
    return 4, [px[i:i + 64] for i in range(0, len(px), 64)]

def ncgr_build(tiles, bpp, tiles_wide=32):
    """An NCGR of the layout the title's BG files use (RAHC + SOPC), tile count padded to whole rows."""
    tiles = list(tiles)
    while len(tiles) % tiles_wide: tiles.append(bytes(64))
    th = len(tiles) // tiles_wide
    if bpp == 8:
        raw = b''.join(tiles)
    else:
        raw = bytes((t[i] & 15) | (t[i + 1] & 15) << 4 for t in tiles for i in range(0, 64, 2))
    rahc = b'RAHC' + struct.pack('<IHHIIIII', 0x20 + len(raw), th, tiles_wide, 4 if bpp == 8 else 3, 0, 0,
                                 len(raw), 0x18) + raw
    sopc = b'SOPC' + struct.pack('<IIHH', 0x10, 0, tiles_wide, th)
    body = rahc + sopc
    return b'RGCN' + struct.pack('<HHIHH', 0xFEFF, 0x0101, 0x10 + len(body), 0x10, 2) + body

def nscr_entries(u):
    assert u[:4] == b'RCSN' and u[0x10:0x14] == b'NRCS'
    w, h, mode, _, size = struct.unpack_from('<HHHHI', u, 0x18)
    return w, h, mode, list(struct.unpack_from(f'<{size // 2}H', u, 0x24))

def nscr_build(w, h, mode, entries):
    raw = struct.pack(f'<{len(entries)}H', *entries)
    body = b'NRCS' + struct.pack('<IHHHHI', 0x14 + len(raw), w, h, mode, 0, len(raw)) + raw
    return b'RCSN' + struct.pack('<HHIHH', 0xFEFF, 0x0100, 0x10 + len(body), 0x10, 1) + body

def nclr_colours(n):
    assert n[:4] == b'RLCN' and n[0x10:0x14] == b'TTLP'
    size, off = struct.unpack_from('<II', n, 0x20)
    return [bgr555_to_rgb(v) for v in struct.unpack_from(f'<{size // 2}H', n, 0x18 + off)]

def nclr_build(template, colours):
    """`template` (an NCLR of the same size) with its colours replaced."""
    out = bytearray(template)
    size, off = struct.unpack_from('<II', out, 0x20)
    assert len(colours) == size // 2, (len(colours), size)
    struct.pack_into(f'<{len(colours)}H', out, 0x18 + off, *[rgb_to_bgr555(c) for c in colours])
    return bytes(out)

# ---------------------------------------------------------------------------------------------------- images <-> BG

def flip_tile(t, h, v):
    return bytes(t[(7 - y if v else y) * 8 + (7 - x if h else x)] for y in range(8) for x in range(8))

def render_screen(tiles, entries, w, h, bpp):
    """Palette-index picture (bytes, w*h) of a BG screen. 4bpp: index = palette * 16 + colour (0 stays 0)."""
    img = bytearray(w * h); cols = w // 8
    for i, ent in enumerate(entries[:cols * (h // 8)]):
        tx, ty = i % cols, i // cols
        t = flip_tile(tiles[ent & 0x3ff], ent >> 10 & 1, ent >> 11 & 1); p = ent >> 12
        for y in range(8):
            row = t[y * 8:y * 8 + 8]
            if bpp == 4: row = bytes(p * 16 + v if v else 0 for v in row)
            img[(ty * 8 + y) * w + tx * 8:(ty * 8 + y) * w + tx * 8 + 8] = row
    return bytes(img)

class TileSet:
    """Distinct tiles with H/V flips folded, tile 0 blank (the game's files start with a blank tile too)."""
    def __init__(self):
        self.tiles = [bytes(64)]; self.index = {bytes(64): (0, 0, 0)}
    def seed(self, tiles):
        """Start from an existing tile list (indices kept, as its screen refers to them)."""
        assert not any(tiles[0])
        self.tiles = list(tiles); self.index = {}
        for k, t in enumerate(tiles):
            for h in (0, 1):
                for v in (0, 1):
                    self.index.setdefault(flip_tile(t, h, v), (k, h, v))
        return self
    def add(self, t):
        if t in self.index:
            return self.index[t]
        k = len(self.tiles); self.tiles.append(t)
        for h in (0, 1):
            for v in (0, 1):
                self.index.setdefault(flip_tile(t, h, v), (k, h, v))
        return self.index[t]

def screen_from_image(ts, pix, w, h, palette=0):
    """Screen entries for a palette-index picture (row-major bytes, w x h), adding its tiles to TileSet `ts`.
    4bpp pictures give 0..15 indices plus `palette`. Empty tiles -> entry 0 (the blank tile)."""
    out = []
    for ty in range(h // 8):
        for tx in range(w // 8):
            t = bytes(pix[(ty * 8 + y) * w + tx * 8 + x] for y in range(8) for x in range(8))
            if not any(t):
                out.append(0); continue
            k, hf, vf = ts.add(t)
            out.append(k | hf << 10 | vf << 11 | palette << 12)
    return out

# ---------------------------------------------------------------------------------------------------- Black 2's art

def title_entries(files=SRC_FILES):
    from b2files import narc_entries, arc_path
    return narc_entries(arc_path(files, ARC_TITLE))

def original_top(e):
    """Black 2's logo layer (256x192 indices), strip layer (256x192) and 256-colour palette."""
    _, tiles = ncgr_tiles(lz10_decompress(e[0]))
    w, h, _, logo = nscr_entries(lz10_decompress(e[1]))
    w2, h2, _, strip = nscr_entries(lz10_decompress(e[3]))
    logo_px = render_screen(tiles, logo, w, h, 8)[:256 * 192]
    return logo_px, render_screen(tiles, strip, w2, h2, 8), nclr_colours(e[2])

def original_bottom(e):
    """Black 2's bottom BG3: (tiles, entries, palette colours) of the credit line."""
    _, tiles = ncgr_tiles(lz10_decompress(e[9]))
    w, h, _, ents = nscr_entries(lz10_decompress(e[10]))
    return tiles, ents, nclr_colours(e[8])

def kyogre_sprite(files=SRC_FILES):
    """Kyogre's Black 2 front still (a/0/0/4 7640, LZ11 NCGR, 96x96 4bpp in OBJ order 64x64, 32x64, 64x32, 32x32)
    and its normal palette (7658): (96*96 indices, 16 colours)."""
    from b2files import narc_entries, arc_path
    from sprites import lz11_decompress
    e = narc_entries(arc_path(files, ARC_POKEGRA))
    _, tiles = ncgr_tiles(lz11_decompress(e[KYOGRE_STILL]))
    pix = bytearray(96 * 96); k = 0
    for ox, oy, ow, oh in [(0, 0, 64, 64), (64, 0, 32, 64), (0, 64, 64, 32), (64, 64, 32, 32)]:
        for t in range(ow * oh // 64):
            tx, ty = ox + t % (ow // 8) * 8, oy + t // (ow // 8) * 8
            for j in range(64):
                pix[(ty + j // 8) * 96 + tx + j % 8] = tiles[k][j]
            k += 1
    assert k == len(tiles) == 144
    return bytes(pix), nclr_colours(e[KYOGRE_PAL])

def press_start(e):
    """The 'PRESS START' OBJ (files 4/5/6, cell 1) drawn at the actor's (128, 96) on a 256x192 RGBA image."""
    from PIL import Image
    from sprites import OBJ_SIZES
    _, tiles = ncgr_tiles(lz10_decompress(e[5]))
    cols = nclr_colours(e[4])
    ncer = e[6]
    n, attr, celloff = struct.unpack_from('<HHI', ncer, 0x18)
    base = 0x18 + celloff; csz = 16 if attr & 1 else 8; oambase = base + n * csz
    img = Image.new('RGBA', (256, 192), (0, 0, 0, 0))
    no, _, oo = struct.unpack_from('<HHI', ncer, base + csz * 1)
    for j in range(no):
        a0, a1, a2 = struct.unpack_from('<HHH', ncer, oambase + oo + 6 * j)
        y = a0 & 0xff; y -= 256 if y >= 128 else 0
        x = a1 & 0x1ff; x -= 512 if x >= 256 else 0
        w, h = OBJ_SIZES[(a0 >> 14, a1 >> 14)]
        t0 = a2 & 0x3ff; pal = a2 >> 12
        for k in range(w * h // 64):
            tile = tiles[t0 + k]
            bx, by = 128 + x + k % (w // 8) * 8, 96 + y + k // (w // 8) * 8
            for j in range(64):
                if tile[j]:
                    img.putpixel((bx + j % 8, by + j // 8), cols[pal * 16 + tile[j]] + (255,))
    return img

# ---------------------------------------------------------------------------------------------------- the new logo
# Drawn here as vector letters (rectilinear outlines with cut or rounded corners, triangular A/V like Black 2's "A"),
# rendered 8x supersampled with numpy, then reduced to 1x and to the free palette slots. No font files are used.

SS = 8                      # supersampling
LOGO_Y0, LOGO_H = 96, 56    # the band of the top screen the new lettering is drawn in (y 96..151)

def _np():
    import numpy as np
    return np

def corner_poly(pts, r_out, r_in, style='cut', over=None):
    """Cut (45 degree chamfer) or round every corner of a closed polygon: convex corners by r_out, concave by r_in,
    `over` = {vertex index: radius} overrides. Radii are clamped to half of each edge."""
    import math
    n = len(pts); over = over or {}
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    out = []
    for i in range(n):
        (ux, uy), (vx, vy), (wx, wy) = pts[i - 1], pts[i], pts[(i + 1) % n]
        cross = (vx - ux) * (wy - vy) - (vy - uy) * (wx - vx)
        r = over.get(i, r_out if (cross > 0) == (area > 0) else r_in)
        lu, lw = math.hypot(ux - vx, uy - vy), math.hypot(wx - vx, wy - vy)
        r = min(r, lu / 2, lw / 2)
        if r <= 0.01:
            out.append((vx, vy)); continue
        a = (vx + (ux - vx) * r / lu, vy + (uy - vy) * r / lu)
        b = (vx + (wx - vx) * r / lw, vy + (wy - vy) * r / lw)
        if style == 'cut':
            out += [a, b]
        else:   # quadratic Bezier through the corner
            for k in range(9):
                t = k / 8
                out.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * vx + t * t * b[0],
                            (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * vy + t * t * b[1]))
    return out

def glyph(ch, W, H, T, M0, M1):
    """Shapes of one letter: [(points, 'add' | 'cut', corner overrides)], in pixels from its top-left."""
    if ch == 'S':
        return [([(0, 0), (W, 0), (W, T), (T, T), (T, M0), (W, M0), (W, H), (0, H), (0, H - T), (W - T, H - T),
                  (W - T, M1), (0, M1)], 'add', {})]
    if ch == 'E':
        We = W * 0.86
        return [([(0, 0), (W, 0), (W, T), (T, T), (T, M0), (We, M0), (We, M1), (T, M1), (T, H - T), (W, H - T),
                  (W, H), (0, H)], 'add', {})]
    if ch in 'PR':
        out = [([(0, 0), (W, 0), (W, M1), (T, M1), (T, H), (0, H)], 'add', {}),
               ([(T, T), (W - T, T), (W - T, M0), (T, M0)], 'cut', {})]
        if ch == 'R':
            out.insert(1, ([(W - T * 1.95, M1 - 0.6), (W - T * 0.8, M1 - 0.6), (W, H), (W - T * 1.15, H)], 'add', {}))
        return out
    if ch == 'H':
        return [([(0, 0), (T, 0), (T, M0), (W - T, M0), (W - T, 0), (W, 0), (W, H), (W - T, H), (W - T, M1),
                  (T, M1), (T, H), (0, H)], 'add', {})]
    if ch == 'I':
        return [([(0, 0), (W, 0), (W, H), (0, H)], 'add', {})]
    if ch == 'O':
        return [([(0, 0), (W, 0), (W, H), (0, H)], 'add', {}), ([(T, T), (W - T, T), (W - T, H - T), (T, H - T)], 'cut', {})]
    if ch == 'N':
        t = T * 1.05
        return [([(0, 0), (t, 0), (W - t, H * 0.6), (W - t, 0), (W, 0), (W, H), (W - t, H), (t, H * 0.4), (t, H),
                  (0, H)], 'add', {})]
    if ch in 'AV':
        top = T * 1.25                      # flat apex width
        th = T * 1.2                        # horizontal width of a slanted leg
        s = (W - top) / 2                   # outer leg run over the full height
        xo_l = lambda y: s * (1 - y / H)    # outer left edge at y (A: wide at the bottom)
        xi_l = lambda y: xo_l(y) + th
        xi_r = lambda y: W - xo_l(y) - th
        ya = H * (1 - (W / 2 - th) / s) if s > 0 else 0     # where the inner edges meet
        if ch == 'A':
            c0, c1 = M0 + (M1 - M0) * 0.55, M1 + (M1 - M0) * 0.45
            yt = max(T * 0.95, ya)
            return [([(xo_l(0), 0), (W - xo_l(0), 0), (W, H), (W - th, H), (xi_r(c1), c1), (xi_l(c1), c1), (th, H),
                      (0, H)], 'add', {0: 0.3, 1: 0.3}),
                    ([(xi_l(yt), yt), (xi_r(yt), yt), (xi_r(c0), c0), (xi_l(c0), c0)], 'cut', {})]
        flip = lambda pts: [(x, H - y) for x, y in pts]        # V = A upside down without the bar
        return [(flip([(xo_l(0), 0), (W - xo_l(0), 0), (W, H), (W - th, H), (W / 2, max(ya, 0)), (th, H), (0, H)]),
                 'add', {0: 0.3, 1: 0.3})]
    if ch == 'U':                           # Ruby's letters (RUBY): built like O, H and P
        return [([(0, 0), (T, 0), (T, H - T), (W - T, H - T), (W - T, 0), (W, 0), (W, H), (0, H)], 'add', {})]
    if ch == 'B':                           # Black 2's B: two counters, a notch on the right between the bowls
        n = T * 0.45
        return [([(0, 0), (W, 0), (W, H), (0, H)], 'add', {}),
                ([(T, T), (W - T, T), (W - T, M0), (T, M0)], 'cut', {}),
                ([(T, M1), (W - T, M1), (W - T, H - T), (T, H - T)], 'cut', {}),
                ([(W - n, M0 + 1.2), (W + 1, M0 + 1.2), (W + 1, M1 - 1.2), (W - n, M1 - 1.2)], 'cut', {})]
    if ch == 'Y':                           # V's arms (leg width T * 1.2) meeting on a stem T * 1.05 wide
        th, hs, yj = T * 1.2, T * 1.05 / 2, M1 - 1
        yv = (W / 2 - th) * yj / (W / 2 - hs)
        return [([(0, 0), (th, 0), (W / 2, yv), (W - th, 0), (W, 0), (W / 2 + hs, yj), (W / 2 + hs, H), (W / 2 - hs, H),
                  (W / 2 - hs, yj)], 'add', {})]
    if ch == 'L':                           # Emerald's letters (EMERALD): E's stem and bottom bar
        return [([(0, 0), (T, 0), (T, H - T), (W, H - T), (W, H), (0, H)], 'add', {})]
    if ch == 'D':                           # O with its right-hand corners cut deep (a D in Black 2's square style)
        c, ci = T * 1.3, T * 0.55
        return [([(0, 0), (W - c, 0), (W, c), (W, H - c), (W - c, H), (0, H)], 'add', {}),
                ([(T, T), (W - T - ci, T), (W - T, T + ci), (W - T, H - T - ci), (W - T - ci, H - T), (T, H - T)],
                 'cut', {})]
    if ch == 'M':                           # two stems joined by N's diagonals (t = T * 1.05) meeting in the middle
        t = T * 1.05
        yo, yi = H * 0.56, H * 0.56 + T * 1.25        # the V's outer (top) and inner (bottom) points
        return [([(0, 0), (t, 0), (W / 2, yo), (W - t, 0), (W, 0), (W, H), (W - T, H), (W - T, H * 0.36),
                  (W / 2, yi), (T, H * 0.36), (T, H), (0, H)], 'add', {})]
    raise KeyError(ch)

BIG = dict(H=24, T=5.5, M0=9.25, M1=14.75, widths=dict(S=23, A=26, P=22, H=23, I=6, R=23, E=21, U=23, B=23, Y=25,
                                                     M=29, L=19, D=23),
           gap=3.5)
SMALL = dict(H=8.5, T=2.3, M0=3.1, M1=5.4, widths=dict(V=11.5, E=9.5, R=10, S=10, I=2.6, O=11, N=11), gap=3.2)

def word_shapes(text, spec, cx, y, r_out, r_in, style):
    """Polygons ('add'/'cut') of a word centred on x = cx with its top at y, and its left and right x."""
    w = spec['widths']
    total = sum(w[c] for c in text) + spec['gap'] * (len(text) - 1)
    x = cx - total / 2; out = []
    for ch in text:
        for pts, kind, over in glyph(ch, w[ch], spec['H'], spec['T'], spec['M0'], spec['M1']):
            r_o = r_out * (0.45 if kind == 'cut' else 1)
            pts = corner_poly(pts, r_o, r_in, style, over)
            out.append(([(x + px, y + py) for px, py in pts], kind))
        x += w[ch] + spec['gap']
    return out, (cx - total / 2, cx + total / 2)

def raster(shapes, w=256, h=LOGO_H, y0=LOGO_Y0):
    """Bool mask (h*SS, w*SS) of polygons, adds then cuts per letter in order."""
    from PIL import Image, ImageDraw
    np = _np()
    img = Image.new('L', (w * SS, h * SS), 0); d = ImageDraw.Draw(img)
    for pts, kind in shapes:
        d.polygon([(x * SS, (y - y0) * SS) for x, y in pts], fill=255 if kind == 'add' else 0)
    return np.array(img) > 127

def dilate(m, r):
    """Dilate a bool mask by r supersampled pixels (octagon: alternating 4- and 8-neighbour steps)."""
    np = _np()
    m = m.copy()
    for i in range(int(round(r))):
        n = m.copy()
        n[1:] |= m[:-1]; n[:-1] |= m[1:]; n[:, 1:] |= m[:, :-1]; n[:, :-1] |= m[:, 1:]
        if i % 2:
            n[1:, 1:] |= m[:-1, :-1]; n[:-1, :-1] |= m[1:, 1:]; n[1:, :-1] |= m[:-1, 1:]; n[:-1, 1:] |= m[1:, :-1]
        m = n
    return m

def blur(a, r):
    """Box blur of radius r, three times (about a Gaussian), on a float array."""
    np = _np()
    a = a.astype('float32')
    for _ in range(3):
        for axis in (0, 1):
            pad = [(0, 0), (0, 0)]; pad[axis] = (r + 1, r)
            c = np.cumsum(np.pad(a, pad, mode='edge'), axis=axis, dtype='float64')
            sl_hi = [slice(None)] * 2; sl_lo = [slice(None)] * 2
            sl_hi[axis] = slice(2 * r + 1, None); sl_lo[axis] = slice(0, -(2 * r + 1))
            a = ((c[tuple(sl_hi)] - c[tuple(sl_lo)]) / (2 * r + 1)).astype('float32')
    return a

def ramp(t, stops):
    """Colours (…, 3) along gradient stops [(t, (r, g, b))] for an array t."""
    np = _np()
    ts = np.array([s[0] for s in stops], 'float32'); cs = np.array([s[1] for s in stops], 'float32')
    return np.stack([np.interp(t, ts, cs[:, k]) for k in range(3)], -1)

def mix(a, b, f):
    np = _np()
    f = np.clip(f, 0, 1)[..., None]
    return a * (1 - f) + np.asarray(b, 'float32') * f

def bevel(core, r, light=(-0.6, -0.8)):
    """-1..1 lighting of a mask's bevel: + on edges facing the light (top-left), - on the far side."""
    np = _np()
    h = blur(core.astype('float32'), r)
    gy, gx = np.gradient(h)
    s = -(gx * light[0] + gy * light[1]) * (r * 2.2)   # outward normal = -gradient
    return np.clip(s, -1, 1) * core

def sparkle(canvas, alpha, x, y, size, colour=(255, 255, 255), y0=LOGO_Y0, halo_colour=(150, 210, 255)):
    """A four-point star (long cross + short diagonals, arms tapering to a point, a round glow in the middle) drawn
    into a supersampled float RGB canvas + alpha. x, y, size in screen pixels."""
    np = _np()
    H, W = alpha.shape
    yy, xx = np.mgrid[0:H, 0:W].astype('float32')
    dx = (xx - x * SS) / SS; dy = (yy - (y - y0) * SS) / SS

    def arm(along, across, length, width):
        return ((np.abs(across) < width * np.clip(1 - np.abs(along) / length, 0, 1)) &
                (np.abs(along) < length)).astype('float32')
    d1, d2 = (dx + dy) / 1.414, (dx - dy) / 1.414
    f = np.maximum.reduce([arm(dx, dy, size, 0.9), arm(dy, dx, size, 0.9), arm(d1, d2, size * 0.45, 0.6),
                           arm(d2, d1, size * 0.45, 0.6), (np.hypot(dx, dy) < 1.1).astype('float32')])
    halo = np.clip(1 - np.hypot(dx, dy) / (size * 0.5), 0, 1) * 0.55
    canvas[:] = mix(canvas, halo_colour, halo * (1 - f))
    canvas[:] = mix(canvas, colour, f)
    alpha[:] = np.maximum(alpha, np.maximum(f, halo))

def layer_down(rgb, alpha):
    """Supersampled RGB + alpha -> 1x premultiplied (rgb, alpha) by box averaging."""
    np = _np()
    H, W = alpha.shape; h, w = H // SS, W // SS
    a = alpha.reshape(h, SS, w, SS).mean((1, 3))
    c = (rgb * alpha[..., None]).reshape(h, SS, w, SS, 3).mean((1, 3))
    return c, a

# ---------------------------------------------------------------------------------------------------- the drafts
SAPPHIRE_Y, VERSION_Y = 106, 137          # top of the letters' fill (outlines grow around it)
CX = 128

def _chrome(text_shapes, top, height, stops, outlines, bevel_r=10, bevel_k=0.55, shine=None, dark=(6, 14, 60)):
    """Letters filled with a vertical gradient + bevel light, then outlines [(width px, colour or (top, bottom))]."""
    np = _np()
    core = raster(text_shapes)
    H, W = core.shape
    yy = (np.mgrid[0:H, 0:W][0].astype('float32') / SS + LOGO_Y0 - top) / height
    rgb = ramp(yy, stops)
    b = bevel(core, bevel_r)
    rgb = mix(rgb, (255, 255, 255), np.clip(b, 0, 1) * bevel_k)
    rgb = mix(rgb, dark, np.clip(-b, 0, 1) * bevel_k)
    if shine is not None: rgb = shine(rgb, core, yy)
    rgb = rgb * core[..., None]; alpha = core.astype('float32'); inner = core
    for width, colour in outlines:
        ring = dilate(inner, width * SS) & ~inner
        c = ramp(yy, [(0, colour[0]), (1, colour[1])]) if isinstance(colour[0], tuple) else np.broadcast_to(
            np.asarray(colour, 'float32'), rgb.shape)
        rgb = np.where(ring[..., None], c, rgb); alpha = np.maximum(alpha, ring)
        inner = inner | ring
    return rgb.astype('float32'), alpha.astype('float32')

def _over(dst, src):
    """Alpha-composite supersampled (rgb, alpha) src over dst."""
    np = _np()
    (dr, da), (sr, sa) = dst, src
    return dr * (1 - sa[..., None]) + sr * sa[..., None], np.maximum(da, sa)

def draft_1():
    """Chrome: Black 2's look in sapphire blue. Polished-metal bands with a dark horizon, bevel, navy line and a
    pale silver rim; VERSION in silver chrome; two sparkles. Black 2's crystal strip unchanged."""
    big, _ = word_shapes('SAPPHIRE', BIG, CX, SAPPHIRE_Y, 3.2, 0.9, 'cut')
    stops = [(0, (236, 248, 255)), (0.16, (156, 210, 255)), (0.45, (44, 118, 230)), (0.47, (14, 38, 126)),
             (0.62, (22, 66, 176)), (0.9, (66, 150, 246)), (1, (150, 222, 255))]
    def shine(rgb, core, yy):
        np = _np()
        line = np.exp(-((yy - 0.1) / 0.03) ** 2) * core
        return mix(rgb, (255, 255, 255), line * 0.7)
    a = _chrome(big, SAPPHIRE_Y, BIG['H'], stops, [(1.0, (8, 18, 70)), (1.5, ((226, 238, 255), (128, 156, 204)))],
                shine=shine)
    small, _ = word_shapes('VERSION', SMALL, CX, VERSION_Y, 1.1, 0.3, 'cut')
    vstops = [(0, (250, 252, 255)), (0.4, (176, 190, 216)), (0.5, (78, 92, 132)), (1, (196, 212, 236))]
    b = _chrome(small, VERSION_Y, SMALL['H'], vstops, [(0.8, (10, 20, 72)), (0.9, ((150, 176, 220), (90, 116, 170)))],
                bevel_r=3, bevel_k=0.3)
    rgb, alpha = _over(a, b)
    sparkle(rgb, alpha, 30.5, SAPPHIRE_Y + 0.5, 7.0)
    sparkle(rgb, alpha, 226, SAPPHIRE_Y + 13.5, 4.5)
    return rgb, alpha

def draft_2():
    """Crystal: letters cut into facets like a sapphire (each facet its own blue, lighter towards the top), bevel
    light, a bright rim and a navy line; VERSION between two small cut gems; sparkles."""
    import random
    np = _np()
    big, (x0, x1) = word_shapes('SAPPHIRE', BIG, CX, SAPPHIRE_Y, 3.6, 0.9, 'cut')
    core = raster(big); H, W = core.shape
    yy, xx = np.mgrid[0:H, 0:W].astype('float32')
    yr = (yy / SS + LOGO_Y0 - SAPPHIRE_Y) / BIG['H']
    rnd = random.Random(382)                      # fixed seeds: the same facets every run
    seeds = [(x0 + rnd.uniform(-4, x1 - x0 + 4), SAPPHIRE_Y + rnd.uniform(-4, BIG['H'] + 4)) for _ in range(90)]
    sx = np.array([s[0] for s in seeds], 'float32'); sy = np.array([s[1] for s in seeds], 'float32')
    ys, xs = np.nonzero(core)
    px, py = xs / SS, ys / SS + LOGO_Y0
    best = np.full(len(xs), 1e9, 'float32'); lab = np.zeros(len(xs), int)
    for i in range(len(seeds)):
        d = (px - sx[i]) ** 2 + ((py - sy[i]) * 1.3) ** 2
        m = d < best; best[m] = d[m]; lab[m] = i
    tone = np.array([np.clip(0.62 - 0.55 * (sy[i] - SAPPHIRE_Y) / BIG['H'] + rnd.uniform(-0.3, 0.3), 0, 1)
                     for i in range(len(seeds))], 'float32')
    stops = [(0, (12, 34, 120)), (0.35, (30, 84, 204)), (0.65, (66, 140, 244)), (0.85, (140, 200, 255)),
             (1, (214, 240, 255))]
    rgb = np.zeros((H, W, 3), 'float32')
    rgb[ys, xs] = ramp(tone[lab], stops)
    b = bevel(core, 10)
    rgb = mix(rgb, (255, 255, 255), np.clip(b, 0, 1) * 0.5)
    rgb = mix(rgb, (6, 14, 60), np.clip(-b, 0, 1) * 0.5) * core[..., None]
    alpha = core.astype('float32'); inner = core
    for width, colour in [(0.9, (226, 244, 255)), (1.25, (8, 22, 82)), (0.6, (44, 96, 190))]:
        ring = dilate(inner, width * SS) & ~inner
        rgb = np.where(ring[..., None], np.asarray(colour, 'float32'), rgb); alpha = np.maximum(alpha, ring)
        inner = inner | ring
    a = (rgb, alpha)
    small, (v0, v1) = word_shapes('VERSION', SMALL, CX, VERSION_Y, 1.1, 0.3, 'cut')
    vstops = [(0, (255, 255, 255)), (0.55, (214, 230, 252)), (1, (150, 186, 236))]
    b = _chrome(small, VERSION_Y, SMALL['H'], vstops, [(0.9, (8, 22, 82)), (0.6, (44, 96, 190))], bevel_r=3,
                bevel_k=0.25)
    rgb, alpha = _over(a, b)
    for gx_ in (v0 - 10, v1 + 10):                                   # two small cut gems beside VERSION
        gem = [(gx_ - 4.5, VERSION_Y + 4.25), (gx_, VERSION_Y - 0.5), (gx_ + 4.5, VERSION_Y + 4.25),
               (gx_, VERSION_Y + 9)]
        m = raster([(gem, 'add')])
        top = raster([([gem[0], gem[1], gem[2]], 'add')])
        left = raster([([gem[0], (gx_, VERSION_Y + 4.25), gem[3]], 'add')])
        col = np.where(top[..., None], np.where(left[..., None], (196, 232, 255), (110, 176, 255)),
                       np.where(left[..., None], (40, 100, 214), (18, 52, 150))).astype('float32')
        ring = dilate(m, 0.9 * SS) & ~m
        g = np.where(m[..., None], col, (8, 22, 82)).astype('float32')
        rgb, alpha = _over((rgb, alpha), (g, (m | ring).astype('float32')))
    for sx_, sy_, s in [(x0 + 1.5, SAPPHIRE_Y + 0.5, 7.0), (x1 - 1.0, SAPPHIRE_Y + BIG['H'] - 1, 5.0)]:
        sparkle(rgb, alpha, sx_, sy_, s)
    return rgb, alpha

def draft_3():
    """Glossy sea: rounded letters, cyan-to-deep-blue water gradient with a wave-edged gloss, thick white line and
    a navy rim (closest to Sapphire's own GBA colours, drawn in Gen 5 style); white VERSION."""
    np = _np()
    big, _ = word_shapes('SAPPHIRE', BIG, CX, SAPPHIRE_Y, 3.4, 1.0, 'round')
    stops = [(0, (120, 226, 255)), (0.5, (42, 140, 240)), (1, (18, 64, 186))]
    def shine(rgb, core, yy):
        H, W = core.shape
        xx = np.mgrid[0:H, 0:W][1].astype('float32') / SS
        edge = 0.47 + 0.07 * np.sin(xx * 2 * np.pi / 36 + 0.6)
        gloss = (yy < edge) * np.clip(1 - yy / edge, 0, 1) ** 0.6
        rgb = mix(rgb, (240, 252, 255), gloss * 0.5)
        under = np.clip(1 - np.abs(yy - edge - 0.04) / 0.05, 0, 1)
        return mix(rgb, (14, 58, 170), under * 0.35)
    a = _chrome(big, SAPPHIRE_Y, BIG['H'], stops, [(1.4, ((255, 255, 255), (206, 232, 255))), (1.3, (10, 30, 104)),
                                                    (0.5, (30, 80, 170))], bevel_r=8, bevel_k=0.3, shine=shine)
    small, _ = word_shapes('VERSION', SMALL, CX, VERSION_Y, 1.4, 0.4, 'round')
    b = _chrome(small, VERSION_Y, SMALL['H'], [(0, (255, 255, 255)), (1, (214, 236, 255))],
                [(0.9, (10, 30, 104)), (0.5, (30, 80, 170))], bevel_r=2, bevel_k=0.0)
    rgb, alpha = _over(a, b)
    sparkle(rgb, alpha, 29.5, SAPPHIRE_Y - 0.5, 7.0)
    return rgb, alpha

DRAFTS = {1: draft_1, 2: draft_2, 3: draft_3}
# the crystal strip of each draft: hue (degrees), saturation and value factors applied to Black 2's ice crystals
STRIP_TINT = {1: (0, 1.0, 1.0), 2: (14, 1.1, 0.92), 3: (6, 1.0, 1.0)}

# ---------------------------------------------------------------------------------------------------- Ruby's drafts
# Ruby's logo is made as Sapphire's was: Black 2's "Pokemon" wordmark and crystal strip, new lettering in the band
# below. The pokeruby logo files were checked first (graphics/title_screen, src/data/graphics.c:1305-1316,
# src/title_screen.c): pokemon_ruby.png is the GBA "POKeMON" wordmark (the same in both games), rubyversion.png the
# "RUBY VERSION" banner (two 64x32 8bpp OBJs, white and grey letters), logo_ruby.pal their palette; the decomp notes
# that the visible logo and banner colours of Ruby and Sapphire are the same. Sapphire's chosen logo (draft 1) used
# none of them, so Ruby's draft 1 repeats draft 1 in ruby red; draft 2 uses pokeruby's own banner pixels.
RUBY_HUE = 135              # degrees: Sapphire's blues (hue ~215) -> ruby red (~350)

def _hue(c, dh=RUBY_HUE, ds=1.0):
    """An RGB colour with its hue turned by dh degrees (value kept, saturation times ds)."""
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in c])
    return tuple(round(x * 255) for x in colorsys.hsv_to_rgb((h + dh / 360) % 1, min(1, s * ds), v))

def ruby_draft_1(ds=1.0):
    """Chrome (Ruby): Sapphire's draft 1 (the logo the user chose) for RUBY: the same letter construction, sizes,
    corners, bevel, outlines, shine line and sparkles (at the same places relative to the word), every colour hue-
    turned to ruby red (_hue); VERSION in the same silver chrome, its tints turned the same way. ds: saturation
    factor of the RUBY letters' gradient (draft 3)."""
    big, (x0, x1) = word_shapes('RUBY', BIG, CX, SAPPHIRE_Y, 3.2, 0.9, 'cut')
    stops = [(t, _hue(c, ds=ds)) for t, c in [(0, (236, 248, 255)), (0.16, (156, 210, 255)), (0.45, (44, 118, 230)),
                                       (0.47, (14, 38, 126)), (0.62, (22, 66, 176)), (0.9, (66, 150, 246)),
                                       (1, (150, 222, 255))]]
    def shine(rgb, core, yy):
        np = _np()
        line = np.exp(-((yy - 0.1) / 0.03) ** 2) * core
        return mix(rgb, (255, 255, 255), line * 0.7)
    a = _chrome(big, SAPPHIRE_Y, BIG['H'], stops, [(1.0, _hue((8, 18, 70))),
                                                    (1.5, (_hue((226, 238, 255)), _hue((128, 156, 204))))],
                shine=shine, dark=_hue((6, 14, 60)))
    small, _ = word_shapes('VERSION', SMALL, CX, VERSION_Y, 1.1, 0.3, 'cut')
    vstops = [(t, _hue(c)) for t, c in [(0, (250, 252, 255)), (0.4, (176, 190, 216)), (0.5, (78, 92, 132)),
                                        (1, (196, 212, 236))]]
    b = _chrome(small, VERSION_Y, SMALL['H'], vstops, [(0.8, _hue((10, 20, 72))),
                                                       (0.9, (_hue((150, 176, 220)), _hue((90, 116, 170))))],
                bevel_r=3, bevel_k=0.3, dark=_hue((6, 14, 60)))
    rgb, alpha = _over(a, b)
    # Sapphire's sparkles sit 2.25 px left of the word's top-left and 2.75 px right of its end, 13 rows lower
    sparkle(rgb, alpha, x0 - 2.25, SAPPHIRE_Y + 0.5, 7.0, halo_colour=_hue((150, 210, 255)))
    sparkle(rgb, alpha, x1 + 2.75, SAPPHIRE_Y + 13.5, 4.5, halo_colour=_hue((150, 210, 255)))
    return rgb, alpha

def gba_banner(name='rubyversion.png', pal='logo_ruby.pal'):
    """pokeruby's version banner as (index array cropped to its pixels, palette): the left OBJ (tiles 0-31) and the
    right OBJ (tiles 32-63, title_screen.c VERSION_BANNER_RIGHT_TILEOFFSET 64 in 32-byte units) side by side, as the
    title screen places them (x 98 and 162)."""
    from PIL import Image
    np = _np()
    g = os.path.join(ROOT, 'external', 'pokeruby', 'graphics', 'title_screen')
    a = np.array(Image.open(os.path.join(g, name)))
    b = np.hstack([a[:32], a[32:64]])
    vals = open(os.path.join(g, pal)).read().split()
    cols = [tuple(int(v) for v in vals[3 + 3 * i:6 + 3 * i]) for i in range(int(vals[2]))]
    ys, xs = np.nonzero(b)
    return b[ys.min():ys.max() + 1, xs.min():xs.max() + 1], cols + [(0, 0, 0)] * (256 - len(cols))

def ruby_draft_2():
    """pokeruby's own "RUBY VERSION" banner (gba_banner), doubled (2x, nearest neighbour: 142x56) and centred in the
    lettering band under Black 2's wordmark, in its own colours. No new pixels."""
    np = _np()
    b, cols = gba_banner()
    b = b.repeat(2, 0).repeat(2, 1)
    h, w = b.shape
    ox, oy = CX - w // 2, (LOGO_H - h) // 2
    pal = np.asarray(cols, 'float32')
    rgb = np.zeros((LOGO_H, 256, 3), 'float32'); alpha = np.zeros((LOGO_H, 256), 'float32')
    rgb[oy:oy + h, ox:ox + w] = pal[b]; alpha[oy:oy + h, ox:ox + w] = b != 0
    return rgb.repeat(SS, 0).repeat(SS, 1), alpha.repeat(SS, 0).repeat(SS, 1)

def ruby_draft_3():
    """Draft 1 with the RUBY letters' gradient 1.6x as saturated: the hue-turned pale blues of Sapphire's chrome come
    out pink, so this one reads deeper ruby red (VERSION, outlines and sparkles as draft 1)."""
    return ruby_draft_1(ds=1.6)

RUBY_DRAFTS = {1: ruby_draft_1, 2: ruby_draft_2, 3: ruby_draft_3}
RUBY_STRIP_TINT = {n: (RUBY_HUE, 1.0, 1.0) for n in RUBY_DRAFTS}      # Black 2's ice crystals turned ruby red

# ---------------------------------------------------------------------------------------------------- Emerald's drafts
# Emerald's top screen in the Sapphire/Ruby style (user 2026-10-12: "make the TOP screen match the style of our Sapphire
# and Ruby title screens"; the bottom keeps Emerald's own Rayquaza scene): made as Ruby's was. Draft 1 repeats
# Sapphire's chosen draft 1 (letter construction, sizes, corners, bevel, outlines, shine line, sparkles at the same
# places relative to the word) for EMERALD with every colour hue-turned to emerald green; draft 2 is pokeemerald's own
# "EMERALD VERSION" banner (graphics/title_screen/emerald_version.png: two 64x32 OBJs side by side, its own greys; in the
# user's dump, emerald_src.py verify) doubled, as Ruby's draft 2; draft 3 is draft 1 with the letters' gradient 1.6x as
# saturated: a deeper green (Ruby's chosen draft 3). EMERALD needs three letters SAPPHIRE and RUBY do not: M, L, D
# (glyph(): built like N, the E's stem and the O). The crystal strip: Black 2's ice crystals hue-turned the same way.
EMERALD_HUE = -70           # degrees: Sapphire's blues (hue ~215) -> emerald green (~145)

def emerald_draft_1(ds=1.0):
    """Chrome (Emerald): Sapphire's draft 1 for EMERALD, every colour hue-turned by EMERALD_HUE (VERSION's silver
    chrome turned the same way). ds: saturation factor of the EMERALD letters' gradient (draft 3)."""
    h = lambda c, ds_=1.0: _hue(c, EMERALD_HUE, ds_)
    big, (x0, x1) = word_shapes('EMERALD', BIG, CX, SAPPHIRE_Y, 3.2, 0.9, 'cut')
    stops = [(t, h(c, ds)) for t, c in [(0, (236, 248, 255)), (0.16, (156, 210, 255)), (0.45, (44, 118, 230)),
                                        (0.47, (14, 38, 126)), (0.62, (22, 66, 176)), (0.9, (66, 150, 246)),
                                        (1, (150, 222, 255))]]
    def shine(rgb, core, yy):
        np = _np()
        line = np.exp(-((yy - 0.1) / 0.03) ** 2) * core
        return mix(rgb, (255, 255, 255), line * 0.7)
    a = _chrome(big, SAPPHIRE_Y, BIG['H'], stops, [(1.0, h((8, 18, 70))), (1.5, (h((226, 238, 255)), h((128, 156, 204))))],
                shine=shine, dark=h((6, 14, 60)))
    small, _ = word_shapes('VERSION', SMALL, CX, VERSION_Y, 1.1, 0.3, 'cut')
    vstops = [(t, h(c)) for t, c in [(0, (250, 252, 255)), (0.4, (176, 190, 216)), (0.5, (78, 92, 132)),
                                     (1, (196, 212, 236))]]
    b = _chrome(small, VERSION_Y, SMALL['H'], vstops, [(0.8, h((10, 20, 72))), (0.9, (h((150, 176, 220)), h((90, 116, 170))))],
                bevel_r=3, bevel_k=0.3, dark=h((6, 14, 60)))
    rgb, alpha = _over(a, b)
    # Sapphire's sparkles sit 2.25 px left of the word's top-left and 2.75 px right of its end, 13 rows lower
    sparkle(rgb, alpha, x0 - 2.25, SAPPHIRE_Y + 0.5, 7.0, halo_colour=h((150, 210, 255)))
    sparkle(rgb, alpha, x1 + 2.75, SAPPHIRE_Y + 13.5, 4.5, halo_colour=h((150, 210, 255)))
    return rgb, alpha

def emerald_banner():
    """pokeemerald's "EMERALD VERSION" banner (emerald_version.png, 128x32: the left and right 64x32 OBJs side by side,
    as the title screen places them at x 98 and 162) cropped to its pixels, and its own colours (the PNG's palette,
    gTitleScreenEmeraldVersionPal)."""
    from PIL import Image
    np = _np()
    im = Image.open(os.path.join(ROOT, 'external', 'pokeemerald', 'graphics', 'title_screen', 'emerald_version.png'))
    a = np.array(im)
    p = im.getpalette()[:48]
    cols = [tuple(p[3 * i:3 * i + 3]) for i in range(16)]
    ys, xs = np.nonzero(a)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], cols + [(0, 0, 0)] * (256 - len(cols))

def emerald_draft_2():
    """pokeemerald's own "EMERALD VERSION" banner, doubled (nearest neighbour) and centred in the lettering band under
    Black 2's wordmark, in its own colours. No new pixels. The banner is 29 rows (58 doubled): the band grows 2 rows."""
    np = _np()
    b, cols = emerald_banner()
    b = b.repeat(2, 0).repeat(2, 1)
    h, w = b.shape
    H = max(LOGO_H, h)
    ox, oy = CX - w // 2, (H - h) // 2
    pal = np.asarray(cols, 'float32')
    rgb = np.zeros((H, 256, 3), 'float32'); alpha = np.zeros((H, 256), 'float32')
    rgb[oy:oy + h, ox:ox + w] = pal[b]; alpha[oy:oy + h, ox:ox + w] = b != 0
    return rgb.repeat(SS, 0).repeat(SS, 1), alpha.repeat(SS, 0).repeat(SS, 1)

def emerald_draft_3():
    """Draft 1 with the EMERALD letters' gradient 1.6x as saturated: a deeper green (as Ruby's chosen draft 3)."""
    return emerald_draft_1(ds=1.6)

EMERALD_DRAFTS = {1: emerald_draft_1, 2: emerald_draft_2, 3: emerald_draft_3}
EMERALD_STRIP_TINT = {n: (EMERALD_HUE, 1.0, 1.0) for n in EMERALD_DRAFTS}   # Black 2's ice crystals turned green

def version_drafts():
    """(drafts, strip tints) of the build's version."""
    if version.is_emerald():
        return EMERALD_DRAFTS, EMERALD_STRIP_TINT
    return (RUBY_DRAFTS, RUBY_STRIP_TINT) if version.is_ruby() else (DRAFTS, STRIP_TINT)

# ---------------------------------------------------------------------------------------------------- composing
WORDMARK_DX = 6                  # Black 2's "Pokémon" (centred on x 122) moves to the screen centre
STRIP_SLOTS = range(160, 238)    # palette indices of Black 2's crystal strip, kept
BACKDROP = (0, 0, 0)

def wordmark(logo_px):
    """Black 2's "Pokémon" wordmark + TM: the parts of its logo above y 102 that do not reach y 102 (that is
    "BLACK" and the "2"'s ice burst). Returns {(x, y): palette index} of the original palette."""
    from collections import deque
    pts = {(i % 256, i // 256): v for i, v in enumerate(logo_px) if v}
    seen, keep = set(), {}
    for p in pts:
        if p in seen: continue
        comp, q = [], deque([p]); seen.add(p)
        while q:
            x, y = q.popleft(); comp.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in pts and n not in seen: seen.add(n); q.append(n)
        if max(y for _, y in comp) < 102:
            keep.update({c: pts[c] for c in comp})
    return keep

def tint(rgb, dh, ds, dv):
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(*[c / 255 for c in rgb])
    r, g, b = colorsys.hsv_to_rgb((h + dh / 360) % 1, min(1, s * ds), min(1, v * dv))
    return to555((round(r * 255), round(g * 255), round(b * 255)))

def quantize(colours, weights, k, iters=12):
    """k-means (seeded by median cut) of RGB colours -> k BGR555-exact colours and the label of each input."""
    from PIL import Image
    np = _np()
    cols = np.asarray(colours, 'float32'); wts = np.asarray(weights, 'float32')
    if len(cols) <= k:
        return [to555(tuple(int(v) for v in c)) for c in cols], list(range(len(cols)))
    reps = np.repeat(cols.astype('uint8'), np.maximum(1, (wts / wts.max() * 40).astype(int)), axis=0)
    img = Image.fromarray(reps.reshape(1, -1, 3), 'RGB').quantize(k, method=Image.Quantize.MEDIANCUT, dither=0)
    cent = np.asarray(img.getpalette()[:3 * k], 'float32').reshape(-1, 3)
    for _ in range(iters):
        lab = ((cols[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
        for j in range(len(cent)):
            m = lab == j
            if m.any(): cent[j] = (cols[m] * wts[m, None]).sum(0) / wts[m].sum()
    lab = ((cols[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
    return [to555(tuple(int(round(v)) for v in c)) for c in cent], list(lab)

def compose_top(n, files=SRC_FILES):
    """Draft n -> (logo indices 256x192, strip indices 256x192, 256 colours)."""
    np = _np()
    e = title_entries(files)
    logo0, strip0, pal0 = original_top(e)
    pal = [BACKDROP] + [(0, 0, 0)] * 255
    drafts_, tints = version_drafts()
    dh, ds, dv = tints[n]
    for i in STRIP_SLOTS: pal[i] = tint(pal0[i], dh, ds, dv)
    assert all(v == 0 or v in STRIP_SLOTS for v in strip0)
    free = [i for i in range(1, 256) if i not in STRIP_SLOTS]
    logo = bytearray(256 * 192)
    # 1. Black 2's wordmark, exact colours
    wm = wordmark(logo0); remap = {}
    for (x, y), v in sorted(wm.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if v not in remap:
            remap[v] = free.pop(0); pal[remap[v]] = pal0[v]
        logo[y * 256 + x + WORDMARK_DX] = remap[v]
    # 2. the new lettering, reduced to the free slots
    c, a = layer_down(*drafts_[n]())
    rgb = c + (1 - a[..., None]) * np.asarray(BACKDROP, 'float32')
    ys, xs = np.nonzero(a >= 0.12)
    px = [to555(tuple(int(round(v)) for v in rgb[y, x])) for y, x in zip(ys, xs)]
    uniq = sorted(set(px)); count = {u: 0 for u in uniq}
    for p in px: count[p] += 1
    cents, lab = quantize(uniq, [count[u] for u in uniq], len(free))
    slot = {}
    for j, cc in enumerate(cents):
        slot[j] = free[j]; pal[free[j]] = cc
    look = {u: slot[l] for u, l in zip(uniq, lab)}
    for (y, x), p in zip(zip(ys, xs), px):
        logo[(y + LOGO_Y0) * 256 + x] = look[p]
    return bytes(logo), strip0, pal

def top_image(logo, strip, pal, with_press_start=True, files=SRC_FILES):
    from PIL import Image
    img = Image.new('RGB', (256, 192), pal[0])
    for layer in (strip, logo):
        rgba = Image.new('RGBA', (256, 192)); rgba.putdata([pal[v] + (255,) if v else (0, 0, 0, 0) for v in layer])
        img.paste(rgba, (0, 0), rgba)
    if with_press_start:
        ps = press_start(title_entries(files)); img.paste(ps, (0, 0), ps)
    return img

def save_indexed(path, pix, pal, w=256, h=192):
    from PIL import Image
    im = Image.frombytes('P', (w, h), bytes(pix)); im.putpalette([v for c in pal for v in c])
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path)

def load_indexed(path):
    from PIL import Image
    im = Image.open(path); assert im.mode == 'P', f'{path}: not an indexed PNG'
    p = im.getpalette(); p += [0] * (768 - len(p))
    return im.tobytes(), [to555(tuple(p[3 * i:3 * i + 3])) for i in range(256)], im.size

def drafts():
    from PIL import Image
    os.makedirs(SHOTS, exist_ok=True)
    for n in version_drafts()[0]:
        logo, strip, pal = compose_top(n)
        d = os.path.join(DATA, 'drafts', f'draft_{n}')
        save_indexed(os.path.join(d, 'logo.png'), logo, pal); save_indexed(os.path.join(d, 'strip.png'), strip, pal)
        img = top_image(logo, strip, pal)
        img.save(os.path.join(SHOTS, f'logo_draft_{n}.png'))
        img.resize((512, 384), Image.NEAREST).save(os.path.join(SHOTS, f'logo_draft_{n}_2x.png'))
        used = len(set(logo) | set(strip)) - 1
        print(f'draft {n}: {used} colours, saved {d}')

def use(n):
    d = os.path.join(DATA, 'drafts', f'draft_{n}')
    for f in ('logo.png', 'strip.png'):
        shutil.copyfile(os.path.join(d, f), os.path.join(DATA, f))
    open(os.path.join(DATA, 'CHOSEN'), 'w').write(f'{n}\n')
    print(f'{os.path.relpath(DATA, ROOT)}/logo.png + strip.png = draft {n}')

# ---------------------------------------------------------------------------------------------------- packing
# (The 2026-10-06 and 2026-10-08 bottom screens below are kept for HOENN_TITLE_STILL=1 / HOENN_TITLE_MCSS=1; the
# default since 2026-10-11 is Sapphire's own scene, "Sapphire's scene" further down.)
# Bottom screen: Kyogre's front still, 1x, its figure centred at about (128, 88) (sprite top-left on the tile grid),
# on a pale sea-blue backdrop; Black 2's "Developed by GAME FREAK inc." line kept, its colours redone for the backdrop.
# Since 2026-10-08 the title animates the figure (patches/title.py ANIMATED_DOC): BG3 then holds the backdrop and the
# credit line only (bottom_screen(still=False)) and MCSS draws the figure in front of it, its first frame over the
# still's place (mcss_origin below). The still is kept here for preview() and for HOENN_TITLE_STILL=1 builds.
# Every pixel of main BG3 is opaque: tested in DeSmuME, pixels left transparent show black (the 3D layer and the
# display capture do not let the backdrop colour through), so the backdrop colour is drawn into the tiles. Kyogre's
# tiles keep its exact colours: each tile goes in a copy of its palette where one colour that tile does not use is
# swapped for the backdrop (Kyogre uses all 15 colours, but no tile does).
KYOGRE_AT = tuple(TITLE['at'])                 # Sapphire (80, 40)
BOTTOM_BACKDROP = tuple(TITLE['backdrop'])     # Sapphire (206, 234, 247)
CREDIT_TEXT = (64, 24, 8) if version.is_ruby() else (8, 24, 64)   # Sapphire navy; Ruby its red-brown mirror
CREDIT_RAMP = [0, 0.03, 0.13, 0.22, 1.0]   # Black 2's credit colours 0..4 = white -> black at these steps
BG_INDEX = 5                                # palette 0: the backdrop colour as an opaque index

def lz_title(data):
    """The compressed form of a title file: LZ10 (as Black 2's own files), Emerald LZ11. Emerald's scene has 321 bottom
    tiles (Sapphire's 137) and with LZ10 a/0/2/6 would be 25592 bytes, over Black 2's 24436 (title.py keeps the
    archive at Black 2's size, so the ROM layout does not change); LZ11 makes it 1.9 KB smaller. The title's loader
    takes both: every compressed load (GFL_ArcSysReadHeapNewLZ, GFL_BGSysTransferUncomp) goes through
    sys_uncomp_lz1x (arm9 0x0207909c), which reads the header's low nibble (`tst r5, #0xf; movne r7, #1`) and decodes
    LZ11's long matches when it is 1 [asm], into a heap buffer."""
    if not version.is_emerald():
        return lz10_compress(data)
    from sprites import lz11_compress, lz11_decompress
    out = lz11_compress(data)
    assert lz11_decompress(out) == bytes(data)
    return out

def lz_decompress_any(d):
    """LZ10 or LZ11 (title files: lz_title)."""
    if d[0] == 0x11:
        from sprites import lz11_decompress
        return lz11_decompress(d)
    return lz10_decompress(d)

def pack_top(logo, strip, pal):
    """Files 0 (NCGR, LZ10), 1 (NSCR 256x256, LZ10), 2 (NCLR, uncompressed) and 3 (NSCR 256x192, LZ10) from the
    logo and strip pictures (palette indices, 256x192) and their 256 colours. Returns ({file: bytes}, tile count)."""
    e = title_entries()
    ts = TileSet()
    logo_map = screen_from_image(ts, logo, 256, 192) + [0] * (32 * 8)     # the map is 256x256, rows 24..31 empty
    strip_map = screen_from_image(ts, strip, 256, 192)
    n = len(ts.tiles)
    if n > 512:
        raise SystemExit(f'title logo + strip: {n} tiles, the top screen holds 512')
    tiles = ts.tiles + [bytes(64)] * (512 - n)       # the code loads exactly 0x8000 bytes of tiles
    return {0: lz_title(ncgr_build(tiles, 8)),
            1: lz_title(nscr_build(256, 256, 1, logo_map)),
            2: nclr_build(e[2], list(pal) + [(0, 0, 0)] * (256 - len(pal))),
            3: lz_title(nscr_build(256, 192, 1, strip_map))}, n

def bottom_screen(files=SRC_FILES, still=True):
    """The bottom BG3 as (tiles, 32x24 entries, 16 palettes of 16 colours), every pixel opaque. still=False: the
    backdrop and the credit line only (the animated title draws the figure with MCSS in front of BG3)."""
    e = title_entries(files)
    tiles, ents, cols = original_bottom(e)
    assert cols[0] == (255, 255, 255) and cols[4] == (0, 0, 0) and all(c == (0, 0, 0) for c in cols[5:16]), cols[:16]
    credit = render_screen(tiles, ents, 256, 192, 4)             # palette 0 indices 1..4
    kyogre, kpal = kyogre_sprite(files)
    kx, ky = KYOGRE_AT
    kpix = bytearray(256 * 192)
    for i, v in enumerate(kyogre if still else ()):
        kpix[(ky + i // 96) * 256 + kx + i % 96] = v
    pal0 = [to555(tuple(round(BOTTOM_BACKDROP[j] + (CREDIT_TEXT[j] - BOTTOM_BACKDROP[j]) * t) for j in range(3)))
            for t in CREDIT_RAMP]
    pals = [pal0 + [to555(BOTTOM_BACKDROP)] + [(0, 0, 0)] * 10]
    assert pals[0][BG_INDEX] == pals[0][0]
    swap_order = sorted(range(1, 16), key=lambda c: kyogre.count(c))   # swap Kyogre's least-used colours first
    swapped = {}                                                    # Kyogre colour swapped -> palette number
    ts = TileSet(); out = []
    blank = None
    for ty in range(24):
        for tx in range(32):
            at = [(ty * 8 + y) * 256 + tx * 8 + x for y in range(8) for x in range(8)]
            k = [kpix[p] for p in at]; c = [credit[p] for p in at]
            if any(k):
                assert not any(c), 'Kyogre overlaps the credit line'
                used = set(k)
                x = next((s for s in swapped if s not in used), None) or next(s for s in swap_order if s not in used)
                if x not in swapped:
                    swapped[x] = len(pals)
                    pals.append([kpal[i] if i != x else to555(BOTTOM_BACKDROP) for i in range(16)])
                t = bytes(v or x for v in k); pal = swapped[x]
            else:
                t = bytes(v or BG_INDEX for v in c); pal = 0
            ki, hf, vf = ts.add(t)
            out.append(ki | hf << 10 | vf << 11 | pal << 12)
    assert len(pals) <= 16
    return ts.tiles, out, pals + [[(0, 0, 0)] * 16] * (16 - len(pals))

def pack_bottom(files=SRC_FILES, still=True):
    """Files 8 (NCLR), 9 (NCGR 4bpp, LZ10), 10 (NSCR 256x192, LZ10). Returns ({file: bytes}, tile count)."""
    e = title_entries(files)
    tiles, ents, pals = bottom_screen(files, still)
    if len(tiles) > 512:
        raise SystemExit(f'bottom BG3: {len(tiles)} tiles, it holds 512')
    return {8: nclr_build(e[8], [c for p in pals for c in p]), 9: lz10_compress(ncgr_build(tiles, 4)),
            10: lz10_compress(nscr_build(256, 192, 0, ents))}, len(tiles)

# Animated title (title_anim, 2026-10-08; patches/title.py, patches/title_mcss.c): the figure is Black 2's MCSS sprite,
# placed so that its first frame covers the still exactly. The still is the multi-cell animation's first pose: tick 0
# of mcss.render matches the still on 99.9% (Kyogre) and 100% (Groudon) of the still's pixels, with the still's 96x96
# box at (-56, -95) (Kyogre) / (-48, -85) (Groudon) from the sprite's origin. So the origin goes to KYOGRE_AT minus
# that offset.
def mcss_still_offset(files=SRC_FILES):
    """(dx, dy): the still's 96x96 box top-left relative to the MCSS sprite's origin, found by matching the still
    against Black 2's own MCSS data posed at tick 0 (mcss.py), and the share of the still's pixels that match."""
    import numpy as np
    import mcss, sprites
    from b2files import narc_entries, arc_path
    e = narc_entries(arc_path(files, ARC_POKEGRA))
    first = KYOGRE_STILL                                   # species * 20: +2 MCSS texture, +4..+7 the animation
    sp = mcss.Sprite(e, first + 2)
    w, h, tex = sprites.tr_decode_image(e[first + 2], 'parts')
    a = mcss.render(sp, np.frombuffer(tex, np.uint8).reshape(h, w), 0, 0)
    still = np.frombuffer(kyogre_sprite(files)[0], np.uint8).reshape(96, 96)
    ys, xs = np.nonzero(a); sy, sx = np.nonzero(still)
    best = None
    for dy in range(ys.min() - sy.min() - 6, ys.min() - sy.min() + 7):
        for dx in range(xs.min() - sx.min() - 6, xs.min() - sx.min() + 7):
            ok = (sy + dy >= 0) & (sy + dy < a.shape[0]) & (sx + dx >= 0) & (sx + dx < a.shape[1])
            score = (a[sy[ok] + dy, sx[ok] + dx] == still[sy[ok], sx[ok]]).mean()
            if best is None or score > best[0]:
                best = (score, dx, dy)
    assert best[0] > 0.99, f'the still does not match the MCSS pose ({best[0]:.3f})'
    return best[1] - mcss.ORIGIN[0], best[2] - mcss.ORIGIN[1], best[0]

def mcss_origin(files=SRC_FILES):
    """Screen pixel (x, y) of the MCSS sprite's origin so that its first frame covers the still at KYOGRE_AT."""
    dx, dy, _ = mcss_still_offset(files)
    return KYOGRE_AT[0] - dx, KYOGRE_AT[1] - dy

# ---------------------------------------------------------------------------------------------------- Sapphire's scene
# Since 2026-10-11 (title_anim; user: "Kyogre's animation on the title screen looks off") the bottom screen is
# Sapphire's own title scene, Ruby's in Ruby (pokeruby src/title_screen.c, graphics/title_screen/; patches/title.py
# SCENE_DOC): the dark Kyogre (Groudon) over its gradient on one BG, the sea (lava) on another BG blended over it,
# moved by patches/title_scene.c exactly as Sapphire moves them. Only Sapphire's/Ruby's own tiles, maps and colours,
# 1x: Sapphire's 240x160 screen sits at SCENE_AT on the DS's 256x192 screen (centred), and the strips the GBA never
# shows are filled with Sapphire's own edge tiles (scene_maps). Black 2's credit line stays in front, in Black 2's own
# colours (white letters, black outline), on its own BG3.
# Emerald (emerald_art, 2026-10-12): Emerald's own scene (pokeemerald src/title_screen.c, graphics/title_screen/;
# its tiles, maps and palette verified in the user's dump by b2tools/emerald_src.py): the dark Rayquaza over its
# gradient (BG0: rayquaza.png + rayquaza.bin, 30x20 visible) and the clouds blended over it (BG1: clouds.png +
# clouds.bin, 32x32, its own tiles), one palette for both (rayquaza_and_clouds.pal at slot 14, after the logo's 224
# colours: gTitleScreenBgPalettes). Its phase 3 differs from Sapphire's in three things, all in render_scene and
# patches/title_scene.c (TITLE_EMERALD): the clouds rise a pixel every 4 frames (gBattle_BG1_Y = tBg1Y / 2, tBg1Y +1
# every second frame), the blend is BLDALPHA(6, 15) (EVA 6, EVB 15; the same targets: clouds over Rayquaza +
# backdrop), and Rayquaza's markings (palette 14 colour 15) follow a cosine: every 4th frame
# RGB(31 - I*31/256, 31 - I*22/256, 12) with I = Cos(frame, 128) + 128 (UpdateLegendaryMarkingColor), from dark
# teal-blue to a bright yellow and back over 256 frames. The wave (ScanlineEffect_InitWave(0, 160, 4, 4, 0, BG1HOFS)),
# the phase timing (256 + 1 + 144 + 1 frames before phase 3: SCENE_WAVE0) and the backdrop (black) are Sapphire's.
EMERALD_SCENE = version.is_emerald()
GBA_TITLE = os.path.join(ROOT, 'external', 'pokeemerald' if EMERALD_SCENE else 'pokeruby', 'graphics', 'title_screen')
SCENE_MON, SCENE_SEA = ('rayquaza', 'clouds') if EMERALD_SCENE else ('groudon', 'lava') if version.is_ruby() else \
    ('kyogre', 'water')
SCENE_AT = (8, 16)                   # Sapphire's screen (0, 0) on the DS bottom screen
SCENE_FILES = (15, 16)               # a/0/2/6: BG1's map (the legendary), BG2's map (the sea); new files
SCENE_PALS = (14, 14) if EMERALD_SCENE else (14, 15)    # Sapphire's palette slots (LoadPalette(sLegendaryMonPalettes,
                                                        # 0xE0, ...)), kept; Emerald's one palette at 14
SCENE_BLEND = (6, 15) if EMERALD_SCENE else (15, 16)    # BLDALPHA (EVA, EVB): Emerald BLDALPHA_BLEND(6, 15),
                                                        # Sapphire 0x1F0F (EVB 31 = 16)

def jasc(path):
    """A JASC .pal as 5-bit colours the way gbagfx builds the .gbapal (8-bit value / 8), shown as 8-bit RGB."""
    vals = open(path).read().split()
    n = int(vals[2])
    return [bgr555_to_rgb(sum((int(vals[3 + 3 * i + j]) // 8) << (5 * j) for j in range(3))) for i in range(n)]

def gba_scene():
    """Sapphire's (Ruby's) title scene files: (4bpp tiles of <mon>.png, the 32x20 mon map, the 32x32 sea map,
    palette 14 = <mon>_dark, palette 15 = <mon>_glow)."""
    from PIL import Image
    im = Image.open(os.path.join(GBA_TITLE, SCENE_MON + '.png'))
    w, h = im.size
    px = im.tobytes()
    tiles = [bytes(px[(ty * 8 + y) * w + tx * 8 + x] for y in range(8) for x in range(8))
             for ty in range(h // 8) for tx in range(w // 8)]
    def tmap(name):
        d = open(os.path.join(GBA_TITLE, name + '_map.bin'), 'rb').read()
        return list(struct.unpack(f'<{len(d) // 2}H', d))
    mon, sea = tmap(SCENE_MON), tmap(SCENE_SEA)
    assert len(mon) == 32 * 20 and len(sea) == 32 * 32
    return tiles, mon, sea, jasc(os.path.join(GBA_TITLE, SCENE_MON + '_dark.pal')), \
        jasc(os.path.join(GBA_TITLE, SCENE_MON + '_glow.pal'))

def gba_scene_emerald():
    """Emerald's title scene files: (4bpp tiles of rayquaza.png, of clouds.png, the 32x32 rayquaza map (rows 0-19,
    columns 0-29 shown), the 32x32 clouds map, palette 14 = rayquaza_and_clouds)."""
    from PIL import Image
    def tiles_of(name):
        im = Image.open(os.path.join(GBA_TITLE, name + '.png'))
        w, h = im.size
        px = im.tobytes()
        return [bytes(px[(ty * 8 + y) * w + tx * 8 + x] for y in range(8) for x in range(8))
                for ty in range(h // 8) for tx in range(w // 8)]
    def tmap(name):
        d = open(os.path.join(GBA_TITLE, name + '.bin'), 'rb').read()
        return list(struct.unpack(f'<{len(d) // 2}H', d))
    mon, sea = tmap(SCENE_MON), tmap(SCENE_SEA)
    assert len(mon) == 32 * 32 and len(sea) == 32 * 32
    return tiles_of(SCENE_MON), tiles_of(SCENE_SEA), mon, sea, jasc(os.path.join(GBA_TITLE, 'rayquaza_and_clouds.pal'))

def scene_maps():
    """The DS maps (32x32 entries each, Sapphire's tile numbers and palettes) of BG1 (the legendary) and BG2 (the sea).
    BG1: Sapphire's map moved by SCENE_AT. Of it the GBA shows columns 0-29 and rows 0-19; the DS also shows one column
    left and right and two rows above and below: columns wrap around Sapphire's 30 (the gradient rows are one tile
    repeated, Groudon's ground row repeats every 3 tiles: 30 = 10 repeats), rows repeat Sapphire's first and last row.
    BG2 (scrolled by the code): Sapphire's 256x256 map turned by SCENE_AT, so that the code's offsets are Sapphire's.
    Emerald: the same, except that the rows below repeat the last row's background tile (its first column, the
    gradient's darkest tile 255): Rayquaza's tail reaches into that row, so repeating the whole row would copy it."""
    if EMERALD_SCENE:
        _, _, mon, sea, _ = gba_scene_emerald()
    else:
        _, mon, sea, _, _ = gba_scene()
    dx, dy = SCENE_AT[0] // 8, SCENE_AT[1] // 8
    def bg1_entry(r, c):
        g = r - dy
        if EMERALD_SCENE and g > 19:
            return mon[19 * 32]
        return mon[min(max(g, 0), 19) * 32 + (c - dx) % 30]
    bg1 = [bg1_entry(r, c) if r < 24 else 0 for r in range(32) for c in range(32)]
    bg2 = [sea[((r - dy) % 32) * 32 + (c - dx) % 32] for r in range(32) for c in range(32)]
    assert all(e >> 12 == SCENE_PALS[0] for e in bg1[:32 * 24]) and all(e >> 12 == SCENE_PALS[1] for e in bg2)
    return bg1, bg2

def scene_screens(files=SRC_FILES):
    """(tiles, {file: 32x32 entries} for 10 (BG3: the credit line), 15 (BG1), 16 (BG2), 16 palettes): Sapphire's
    tiles repacked with Black 2's credit-line tiles into one 4bpp set (BG1-3 share char base 0x4000)."""
    if EMERALD_SCENE:
        mtiles, stiles, _, _, pal14 = gba_scene_emerald()
    else:
        gtiles, _, _, dark, glow = gba_scene()
        mtiles = stiles = gtiles
    btiles, bents, bcols = original_bottom(title_entries(files))
    assert bcols[0] == (255, 255, 255) and bcols[4] == (0, 0, 0), bcols[:5]
    ts = TileSet()
    def repack(ents, tiles):
        out = []
        for e in ents:
            t = flip_tile(tiles[e & 0x3ff], e >> 10 & 1, e >> 11 & 1)
            if not any(t) and e >> 12 == 0:
                out.append(0); continue
            k, hf, vf = ts.add(t)
            out.append(k | hf << 10 | vf << 11 | (e & 0xf000))
        return out
    credit = repack(bents[:32 * 24], btiles) + [0] * (32 * 8)
    bg1, bg2 = scene_maps()
    screens = {10: credit, SCENE_FILES[0]: repack(bg1, mtiles), SCENE_FILES[1]: repack(bg2, stiles)}
    pals = [[(0, 0, 0)] * 16 for _ in range(16)]
    pals[0][:5] = [(0, 0, 0)] + list(bcols[1:5])          # the backdrop black (Sapphire's), Black 2's credit colours
    if EMERALD_SCENE:                                     # (Emerald's backdrop is black too: pokemon_logo.pal colour 0)
        pals[SCENE_PALS[0]] = list(pal14)
    else:
        pals[SCENE_PALS[0]], pals[SCENE_PALS[1]] = list(dark), list(glow)
    return ts.tiles, screens, pals

def scene_image(frame, files=SRC_FILES):
    """The bottom screen at frame `frame` of the title (title_scene.c's counter), rendered from the packed data and
    title_scene.c's rules: the reference for the emulator captures (and the preview)."""
    tiles, screens, pals = scene_screens(files)
    return render_scene(tiles, screens, pals, frame, SCENE_AT)

def scene_wave(j):
    """Sapphire's wave, gSineTable[(4 j) & 255] * 4 / 256 (C division), from pokeruby's own table (src/trig.c)."""
    import re
    src = open(os.path.join(ROOT, 'external', 'pokeruby', 'src', 'trig.c')).read()
    body = src[src.index('gSineTable[]'):]; body = body[:body.index('};')]
    s = int(float(re.findall(r'Q_8_8\((-?[0-9.]+)\)', body)[(4 * j) & 255]) * 256)
    return int(s * 4 / 256)

SCENE_WAVE0 = 17     # Sapphire's wave phase at its phase-3 frame 0: the wave task starts with the logo (its frame 1
                     # uses offset 0) and phase 3 starts 402 frames later (256 + 1 + 144 + 1); 402 % 64 = 18 - 1

def sine_table(decomp='pokeruby'):
    """gSineTable (src/trig.c, Q_8_8 values: (s16)(x * 256)) of a decomp, all its entries (pokeemerald: 320)."""
    import re
    src = open(os.path.join(ROOT, 'external', decomp, 'src', 'trig.c')).read()
    body = src[src.index('gSineTable[]'):]; body = body[:body.index('};')]
    return [int(float(v) * 256) for v in re.findall(r'Q_8_8\((-?[0-9.]+)\)', body)]

def emerald_mark_colours():
    """Emerald's UpdateLegendaryMarkingColor for frameNum = 0, 4, ... 252 (64 BGR555 values): I = Cos(frameNum, 128)
    + 128 = (128 * gSineTable[frameNum + 64]) >> 8 + 128; RGB(31 - (int)(I * 31 / 256), 31 - (int)(I * 22 / 256), 12)."""
    sine = sine_table('pokeemerald')
    out = []
    for m in range(64):
        i = ((128 * sine[4 * m + 64]) >> 8) + 128
        assert i >= 0
        out.append((31 - i * 31 // 256) | (31 - i * 22 // 256) << 5 | 12 << 10)
    return out

def mark_colour(n):
    """UpdateLegendaryMarkingColor at Sapphire's phase-3 frame n (the colour set at the last multiple of 4), 5-bit.
    (Emerald: emerald_mark_colours()[(n & 255) >> 2], a BGR555 value.)"""
    m = (n & 255) >> 2
    return 31 - (m & 31) if m & 32 else m & 31

def render_scene(tiles, screens, pals, n, at, gba=False):
    """RGB picture of the scene at frame n: BG2 (the sea, x by Sapphire's wave per line, y one pixel per two frames)
    blended over BG1 (the legendary, its markings at mark_colour(n)) as Sapphire's BLDCNT 0x2142 / BLDALPHA 0x1F0F
    (EVA 15, EVB 16), BG3 (the credit line) in front. gba=True: Sapphire's own 240x160 screen (at = (0, 0) of the
    GBA maps: pass Sapphire's maps in `screens`)."""
    from PIL import Image
    w, h = (240, 160) if gba else (256, 192)
    p = [list(x) for x in pals]
    if EMERALD_SCENE:
        p[SCENE_PALS[0]][15] = bgr555_to_rgb(emerald_mark_colours()[(n & 255) >> 2])
    else:
        c = mark_colour(n)
        p[SCENE_PALS[0]][15] = bgr555_to_rgb(c << 10 if version.is_ruby() else c)
    def px(ents, x, y):
        e = ents[(y // 8 % 32) * 32 + x // 8 % 32]
        t = tiles[e & 0x3ff]
        v = t[((7 - y % 8) if e >> 11 & 1 else y % 8) * 8 + ((7 - x % 8) if e >> 10 & 1 else x % 8)]
        return p[e >> 12][v] if v else None
    mon, sea = screens[SCENE_FILES[0]], screens[SCENE_FILES[1]]
    credit = screens.get(10)
    img = Image.new('RGB', (w, h)); out = img.load()
    vofs = ((n + 1) >> 1) >> 1 if EMERALD_SCENE else (n + 1) >> 1     # Emerald: tBg1Y / 2
    for y in range(h):
        line = y - (0 if gba else at[1])            # Sapphire's line number
        hofs = scene_wave((n + SCENE_WAVE0 + line) % 64)
        for x in range(w):
            fg = px(credit, x, y) if credit else None
            if fg:
                out[x, y] = fg; continue
            a = px(sea, (x + hofs) % 256, (y + vofs) % 256)
            b = px(mon, x, y) or p[0][0]
            if a is None:
                out[x, y] = b; continue
            out[x, y] = blend(a, b, *SCENE_BLEND)
    return img

def blend(a, b, eva=15, evb=16):
    """The 2D engines' alpha blend (GBA and DS alike): each 5-bit channel min(31, (a * EVA + b * EVB) >> 4)."""
    a, b = rgb_to_bgr555(a), rgb_to_bgr555(b)
    return bgr555_to_rgb(sum(min(31, ((a >> s & 31) * eva + (b >> s & 31) * evb) >> 4) << s for s in (0, 5, 10)))

def gba_scene_image(n):
    """Sapphire's own title screen bottom layers (240x160) after its phase-3 frame n, rendered straight from
    pokeruby's files with title_screen.c's rules (no DS repacking): what scene_image must reproduce."""
    pals = [[(0, 0, 0)] * 16 for _ in range(16)]
    if EMERALD_SCENE:                   # one tile list: Rayquaza's 256 tiles, then the clouds' (their entries moved)
        mt, st, mon, sea, pal14 = gba_scene_emerald()
        pals[SCENE_PALS[0]] = list(pal14)
        sea = [e + len(mt) for e in sea]
        return render_scene(mt + st, {SCENE_FILES[0]: mon, SCENE_FILES[1]: sea}, pals, n, (0, 0), gba=True)
    gtiles, mon, sea, dark, glow = gba_scene()
    pals[SCENE_PALS[0]], pals[SCENE_PALS[1]] = list(dark), list(glow)
    return render_scene(gtiles, {SCENE_FILES[0]: mon + [0] * 384, SCENE_FILES[1]: sea}, pals, n, (0, 0), gba=True)

def pack_scene(files=SRC_FILES):
    """Files 8 (NCLR), 9 (NCGR 4bpp, LZ10), 10 (BG3), 15 (BG1), 16 (BG2) (NSCR 256x256, LZ10)."""
    e = title_entries(files)
    tiles, screens, pals = scene_screens(files)
    if len(tiles) > 512:
        raise SystemExit(f'bottom BG1-3: {len(tiles)} tiles, char base 0x4000 holds 512')
    out = {8: nclr_build(e[8], [c for p in pals for c in p]), 9: lz_title(ncgr_build(tiles, 4))}
    for k, ents in screens.items():
        out[k] = lz_title(nscr_build(256, 256, 0, ents))
    return out, len(tiles)

def bottom_image(files=SRC_FILES):
    from PIL import Image
    tiles, ents, pals = bottom_screen(files)
    pix = render_screen(tiles, ents, 256, 192, 4)
    img = Image.new('RGB', (256, 192))
    img.putdata([pals[v >> 4][v & 15] for v in pix])
    return img

def preview(out):
    from PIL import Image
    logo, pal, _ = load_indexed(os.path.join(DATA, 'logo.png'))
    strip, pal2, _ = load_indexed(os.path.join(DATA, 'strip.png'))
    img = Image.new('RGB', (256, 384))
    img.paste(top_image(logo, strip, pal), (0, 0)); img.paste(scene_image(128), (0, 192))   # bottom: Sapphire's scene
    img.resize((512, 768), Image.NEAREST).save(out)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'drafts': drafts()
    elif cmd == 'use': use(int(sys.argv[2]))
    elif cmd == 'preview': preview(sys.argv[2])
    else: print(__doc__)
