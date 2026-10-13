"""Trainer card badge page with Hoenn's Gym Leaders and badges (v165_fixes 2026-10-11, user decision 2026-10-11:
"trainer card badge page gets Hoenn's leaders"; notes/NPC_MOVEMENT.md is unrelated; notes/RESEARCH_STORY_SPRITES.md
"Trainer card"). Black 2's art and Sapphire's art only, resized, nothing drawn:

The page (ov186 func_ov186_021ab178 .. 021ab25c) reads everything from a/0/3/9 [code]:
  - NCGR 28 + NSCR 38 rows 1-10: the eight leader pennants (32x80, one BG palette each: NCLR 0 palettes 0-7 in colour,
    NCLR 1 palettes 0-7 grey = no badge yet; ov186 copies colour over grey per badge obtained). Now Hoenn's leaders in
    Sapphire's badge order, each a 2x crop of Black 2's own PWT front sprite (a/0/7/1 sprites 118-125, 140: Roxanne,
    Brawly, Wattson, Flannery, Norman, Winona, Tate + Liza stacked, Wallace) inside the pennant's own dark banner;
    the grey palettes follow Black 2's grey rule (luminance x 0.31, measured on its own colour/grey pairs).
  - NSCR 38 rows 11-20 (palette 8): the badge case's empty slots (Unova badge silhouettes) -> silhouettes of Sapphire's
    trainer-card badges (graphics/trainer_card/badges.png, 16x16, at 2x) in the case's own slot colours.
  - NCGR 31 cells 0-7 (NCER 52, 32x64 each, NCLR 4 palettes 1, 6, 2, 3, 4, 5, 7, 0): the badges in the case -> Sapphire's
    badges at 2x (its 6 card colours), centred in the cell.
  - BMD0 56-63: the badge on the top screen when one is touched -> src/trainer_card/badge3d_N.nsbmd, Sapphire's badge at
    2x on a thin two-sided plate (b2tools/trainer_card_models.py).
  - ov186 0x021ad19c: the trainer class per badge whose battle sprite stands on the top screen -> Hoenn's leader classes
    (data/hoenn_trainer_classes.json: Roxanne 112, Brawly 113, Wattson 115, Flannery 114, Norman 117, Winona 116,
    Tate & Liza 118, Wallace 119).
  - text: src/text/overrides_trainer_card.json (system 379 lines 65-110: names, mottos from Sapphire's Gym signs, a
    line each leader says in Sapphire, badge names).
a/0/3/9 has no build_rom.py RESERVE: it is rebuilt at its old size (zero padding inside GMIF), so the ROM's file layout
and the savestates stay as they were. The card's front picture (sprites.py CARD_PICTURE_EDIT, sprite_switch's a/0/4/0
copies) is a different archive and different ov186 code: untouched.
"""
import os, sys, struct, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import narcio, sprites as S, title_art as T                                   # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'src', 'trainer_card')
ARC = 39
SAP_BADGES = os.path.join(ROOT, 'external', 'pokeruby', 'graphics', 'trainer_card', 'badges.png')
OV186, OV186_BASE = 'arm9_ov186.bin', 0x021A75A0
CLASS_TABLE = 0x021AD19C                                         # u16[8]: trainer class per badge (top-screen sprite)
CLASS_OLD = [115, 116, 113, 112, 117, 114, 118, 119]             # Black 2: Cheren, Roxie, Burgh, Elesa, Clay, Skyla, Drayden, Marlon
CLASS_NEW = [112, 113, 115, 114, 117, 116, 118, 119]             # Sapphire's badge order (data/hoenn_trainer_classes.json)
# Sapphire's badge order: (front sprite(s) in a/0/7/1, crop) - the crop is the head and shoulders, 15 x 35 pixels of the
# 80x80 still from (x, y) (None: found from the head's top row), drawn at 2x
LEADERS = [('Roxanne', [118]), ('Brawly', [119]), ('Wattson', [120]), ('Flannery', [121]), ('Norman', [122]),
           ('Winona', [123]), ('Tate & Liza', [124, 125]), ('Wallace', [140])]
BADGE_PALS = [1, 6, 2, 3, 4, 5, 7, 0]                           # NCLR 4 palette of 2D badge cell k (ov186 table)
CASE_Y0, CASE_Y1 = 88, 168                                       # NSCR 38 rows 11-20: the badge case
PEN_Y0, PEN_Y1 = 8, 88                                           # rows 1-10: the pennants
FILL, RING, RING_R, LOW, BG = 15, 14, 13, 11, 12                 # case colours (palette 8 indices): silhouette, its edge,
                                                                 # its right edge, the light line under it, the case


def front_still(files, sprite):
    ents = narcio.load(files, 71) if not hasattr(front_still, 'ents') else front_still.ents
    front_still.ents = ents
    f = S.tr_files(sprite)
    _, _, pix = S.tr_decode_image(ents[f['static']], 'static')
    _, pal = S.nclr_colors(ents[f['palette']])
    return pix, [S.bgr555_to_rgb(c) for c in pal]


def head_crop(pix, w=15, h=35, dy=0):
    """(x0, y0) of a w x h box on the head: the top opaque row, centred on the opaque pixels of the 12 rows below it."""
    rows = [y for y in range(80) if any(pix[y * 80 + x] for x in range(80))]
    top = rows[0]
    xs = [x for y in range(top, top + 12) for x in range(80) if pix[y * 80 + x]]
    cx = round(sum(xs) / len(xs))
    return max(0, min(80 - w, cx - w // 2)), max(0, top - 1 + dy)


def portrait(files, sprites_):
    """{(x, y): rgb} of the pennant portrait (2x crops, 30 px wide; two people stacked)."""
    out = {}
    parts = [(sp, 35 if len(sprites_) == 1 else 17) for sp in sprites_]
    y_at = 0
    for sp, hgt in parts:
        pix, rgb = front_still(files, sp)
        x0, y0 = head_crop(pix, 15, hgt)
        for y in range(hgt):
            for x in range(15):
                v = pix[(y0 + y) * 80 + x0 + x]
                if v:
                    for a in (0, 1):
                        for b in (0, 1): out[(2 * x + a, y_at + 2 * y + b)] = rgb[v]
        y_at += 2 * hgt + (2 if len(parts) > 1 else 0)
    return out


def merge_colours(cols, n):
    """At most n colours: the closest pairs (RGB distance) merged into the more used one."""
    from collections import Counter
    c = Counter(cols)
    keep = list(c)
    while len(keep) > n:
        best = None
        for i in range(len(keep)):
            for j in range(i + 1, len(keep)):
                d = sum((p - q) ** 2 for p, q in zip(keep[i], keep[j]))
                if best is None or d < best[0]: best = (d, i, j)
        _, i, j = best
        a, b = keep[i], keep[j]
        lose, win = (a, b) if c[a] < c[b] else (b, a)
        c[win] += c.pop(lose); keep.remove(lose)
        cols = [win if q == lose else q for q in cols]
    return cols


def grey_of(rgb):
    """Black 2's grey for a pennant colour (fitted on its own NCLR 0 -> NCLR 1 pairs: luminance x 0.31, a trace of tint)."""
    lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return T.to555(tuple(max(0, min(255, round(0.31 * lum + 0.08 * (c - lum)))) for c in rgb))


def sapphire_badges():
    """8 x (32x32 palette indices at 2x, the 16 colours) of Sapphire's trainer card badges."""
    from PIL import Image
    im = Image.open(SAP_BADGES)
    pal = im.getpalette()[:48]; rgb = [tuple(pal[i:i + 3]) for i in range(0, 48, 3)]
    px = list(im.getdata())
    out = []
    for k in range(8):
        b = [[px[y * 128 + 16 * k + x] for x in range(16)] for y in range(16)]
        out.append([[b[y // 2][x // 2] for x in range(32)] for y in range(32)])
    return out, rgb


class Screen:
    """NSCR 38 over NCGR 28 as a 256x256 grid of (palette, colour index) pixels; written back into new tiles."""
    def __init__(self, ncgr, nscr):
        self.bpp, self.tiles = T.ncgr_tiles(ncgr)
        self.w, self.h, self.mode, self.ents = T.nscr_entries(nscr)
        self.pal = [[0] * 256 for _ in range(256)]; self.idx = [[0] * 256 for _ in range(256)]
        for i, e in enumerate(self.ents[:1024]):
            t = T.flip_tile(self.tiles[e & 0x3ff], e >> 10 & 1, e >> 11 & 1)
            for y in range(8):
                for x in range(8):
                    self.pal[i // 32 * 8 + y][i % 32 * 8 + x] = e >> 12
                    self.idx[i // 32 * 8 + y][i % 32 * 8 + x] = t[y * 8 + x]
        self.used = {e & 0x3ff for e in self.ents}

    def rewrite(self, cells):
        """New tiles for the given (cx, cy) cells, in tile slots the page's VRAM holds: the slots only these cells used,
        then the free ones below the last slot Black 2 uses (tiles past it are not loaded: they showed as garbage);
        identical tiles (flips too) shared."""
        cells = set(cells)
        limit = max(self.used)
        users = {}
        for i, e in enumerate(self.ents[:1024]): users.setdefault(e & 0x3ff, set()).add((i % 32, i // 32))
        pool = sorted({t for t, u in users.items() if u <= cells} | {t for t in range(1, limit + 1) if t not in users})
        pool = [t for t in pool if t != 0]
        made = {}
        for cx, cy in sorted(cells):
            pal = self.pal[cy * 8][cx * 8]
            t = bytes(self.idx[cy * 8 + y][cx * 8 + x] for y in range(8) for x in range(8))
            assert all(self.pal[cy * 8 + y][cx * 8 + x] == pal for y in range(8) for x in range(8)), (cx, cy)
            if not any(t): self.ents[cy * 32 + cx] = pal << 12; continue
            if t not in made:
                assert pool, 'badge page: no free tile slot left'
                k = pool.pop(0); self.tiles[k] = t
                for hf in (0, 1):
                    for vf in (0, 1): made.setdefault(T.flip_tile(t, hf, vf), (k, hf, vf))
            k, hf, vf = made[t]
            self.ents[cy * 32 + cx] = k | hf << 10 | vf << 11 | pal << 12
        return len(pool)

    def ncgr(self, old):
        u = bytearray(old)
        th, tw, depth, mapping, tiled, size, off = struct.unpack_from('<HHIIIII', u, 0x18)
        raw = bytes((t[i] & 15) | (t[i + 1] & 15) << 4 for t in self.tiles for i in range(0, 64, 2))
        assert len(raw) == size
        u[0x18 + off:0x18 + off + size] = raw
        return bytes(u)

    def nscr(self, old):
        u = bytearray(old)
        struct.pack_into(f'<{len(self.ents)}H', u, 0x24, *self.ents)
        return bytes(u)


def pennants(files, arc, scr, log):
    """Leader pennants: NSCR 38 rows 1-10, NCLR 0/1 palettes 0-7."""
    col = T.nclr_colours(arc[0]); grey = T.nclr_colours(arc[1])
    cells = []
    for k, (name, sps) in enumerate(LEADERS):
        x0 = 32 * k
        region = [(x, y) for y in range(PEN_Y0, PEN_Y1) for x in range(x0, x0 + 32)]
        banner = [(x, y) for x, y in region if scr.pal[y][x] == k and scr.idx[y][x]]
        dark = min({scr.idx[y][x] for x, y in banner}, key=lambda i: sum(col[16 * k + i]))   # the banner's darkest colour
        dark_rgb = col[16 * k + dark]
        bx0 = min(x for x, _ in banner); by0 = min(y for _, y in banner)
        art = portrait(files, sps)
        new = {}
        for x, y in banner:
            new[(x, y)] = art.get((x - bx0, y - by0), dark_rgb)
        # palette: index 0 kept (transparent / the backdrop), the banner's dark colour, the portrait's colours (<= 14)
        rgbs = merge_colours([new[p] for p in banner], 15)
        uniq = [dark_rgb] + sorted({c for c in rgbs if c != dark_rgb}, key=lambda c: sum(c))
        assert len(uniq) <= 15, (name, len(uniq))
        slot = {c: 1 + i for i, c in enumerate(uniq)}
        for (x, y), c in zip(banner, rgbs):
            scr.idx[y][x] = slot[c]
        for i in range(1, 16):
            c = uniq[i - 1] if i - 1 < len(uniq) else (0, 0, 0)
            col[16 * k + i] = T.to555(c); grey[16 * k + i] = grey_of(c)
        cells += sorted({(x // 8, y // 8) for x, y in banner})
        log.append(f'{name} {len(uniq)} colours')
    arc[0] = T.nclr_build(arc[0], col); arc[1] = T.nclr_build(arc[1], grey)
    return cells


def silhouettes(arc, scr, badges, log):
    """Badge case: the Unova silhouettes out, Sapphire's badges' silhouettes (2x) in, centred where each 2D badge sits."""
    bpp, otiles = T.ncgr_tiles(arc[31])
    old_masks = []
    for k in range(8):
        m = [[bool(otiles[32 * k + (y // 8) * 4 + x // 8][(y % 8) * 8 + x % 8]) for x in range(32)] for y in range(64)]
        old_masks.append(m)
    # the old silhouettes: connected FILL (palette 8) components in the case
    seen, comps = set(), []
    for y in range(CASE_Y0, CASE_Y1):
        for x in range(256):
            if (x, y) in seen or not (scr.pal[y][x] == 8 and scr.idx[y][x] == FILL): continue
            comp, todo = [], [(x, y)]; seen.add((x, y))
            while todo:
                p = todo.pop(); comp.append(p)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (p[0] + dx, p[1] + dy)
                    if q not in seen and CASE_Y0 <= q[1] < CASE_Y1 and 0 <= q[0] < 256 and scr.pal[q[1]][q[0]] == 8 and scr.idx[q[1]][q[0]] == FILL:
                        seen.add(q); todo.append(q)
            if len(comp) > 40 and len({p[0] for p in comp}) < 40: comps.append(comp)
    comps.sort(key=lambda c: min(p[0] for p in c))
    assert len(comps) == 8, f'badge case: {len(comps)} silhouettes found'
    cells = set()
    for k, comp in enumerate(comps):
        # where the 2D badge's cell sits: its mask's best overlap with the silhouette
        cs = set(comp)
        bx, by = min(p[0] for p in comp), min(p[1] for p in comp)
        best = None
        for ox in range(bx - 32, bx + 8):
            for oy in range(by - 64, by + 8):
                s = sum(1 for y in range(64) for x in range(32) if old_masks[k][y][x] and (ox + x, oy + y) in cs)
                if best is None or s > best[0]: best = (s, ox, oy)
        _, ox, oy = best
        # erase the old one: the Unova badge's own shape there, 3 pixels around it (4 below: the light line) - its
        # silhouette and edge - back to the case colour
        old = {(ox + x, oy + y) for y in range(64) for x in range(32) if old_masks[k][y][x]}
        near = {(x + dx, y + dy) for x, y in old for dx in range(-3, 4) for dy in range(-3, 5)}
        for x, y in near:
            if CASE_Y0 <= y < CASE_Y1 and 0 <= x < 256 and scr.pal[y][x] == 8 and scr.idx[y][x] in (FILL, RING, RING_R, LOW):
                scr.idx[y][x] = BG; cells.add((x // 8, y // 8))
        # the new one: Sapphire's badge k at 2x, centred in the cell (rows 16-47 of 64)
        m = {(ox + x, oy + 16 + y) for y in range(32) for x in range(32) if badges[k][y][x]}
        inside = lambda q: ox + 1 <= q[0] <= ox + 30          # (the edge stays in the badge's own cell: 2x badges are
        ring = {(x + dx, y + dy) for x, y in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - m   # 30 px wide)
        ring = {q for q in ring if inside(q)}
        low = {(x, y + 1) for x, y in ring if (x, y + 1) not in m and (x, y + 1) not in ring}
        for x, y in low:
            if scr.idx[y][x] == BG: scr.idx[y][x] = LOW
        for x, y in ring: scr.idx[y][x] = RING_R if (x - 1, y) in m and (x + 1, y) not in m else RING
        for x, y in m: scr.idx[y][x] = FILL
        cells |= {(x // 8, y // 8) for x, y in m | ring | low}
        log.append(f'slot {k} at {ox},{oy}')
    # specks left of the old edges (a lone pixel in the case colour's surroundings)
    for y in range(CASE_Y0 + 1, CASE_Y1 - 1):
        for x in range(1, 255):
            if scr.pal[y][x] == 8 and scr.idx[y][x] in (RING, RING_R, LOW) and \
                    all(scr.idx[y + dy][x + dx] == BG for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
                scr.idx[y][x] = BG; cells.add((x // 8, y // 8))
    return sorted(c for c in cells if CASE_Y0 // 8 <= c[1] < CASE_Y1 // 8)


def badges2d(arc, badges, rgb):
    """NCGR 31 cells 0-7: Sapphire's badges at 2x (rows 16-47 of each 32x64 cell); NCLR 4: its colours."""
    u = bytearray(arc[31])
    th, tw, depth, mapping, tiled, size, off = struct.unpack_from('<HHIIIII', u, 0x18)
    bpp, tiles = T.ncgr_tiles(arc[31])
    for k in range(8):
        for t in range(32):
            tx, ty = t % 4, t // 4
            tiles[32 * k + t] = bytes((badges[k][ty * 8 + y - 16][tx * 8 + x] if 16 <= ty * 8 + y < 48 else 0)
                                      for y in range(8) for x in range(8))
    raw = bytes((t[i] & 15) | (t[i + 1] & 15) << 4 for t in tiles for i in range(0, 64, 2))
    u[0x18 + off:0x18 + off + size] = raw[:size]
    arc[31] = bytes(u)
    cols = T.nclr_colours(arc[4])
    for p in BADGE_PALS:
        for i in range(1, 16): cols[16 * p + i] = T.to555(rgb[i])
    arc[4] = T.nclr_build(arc[4], cols)


def models(arc, log):
    n = 0
    for k in range(8):
        p = os.path.join(SRC, f'badge3d_{k}.nsbmd')
        if os.path.exists(p): arc[56 + k] = open(p, 'rb').read(); n += 1
    log.append(f'{n} 3D badges' + ('' if n == 8 else ' (missing: run b2tools/trainer_card_models.py)'))


def apply(files):
    arc = narcio.load(files, ARC)
    sizes = [len(e) for e in arc]
    log = []
    scr = Screen(arc[28], arc[38])
    cells = pennants(files, arc, scr, log)
    badges, rgb = sapphire_badges()
    cells += silhouettes(arc, scr, badges, log)
    free = scr.rewrite(sorted(set(cells)))
    arc[28] = scr.ncgr(arc[28]); arc[38] = scr.nscr(arc[38])
    badges2d(arc, badges, rgb)
    models(arc, log)
    path = os.path.join(files, 'a', '0', '3', '9')
    old = os.path.getsize(path) if not os.path.islink(path) else os.path.getsize(os.path.realpath(path))
    narcio.save(files, ARC, arc)
    new = os.path.getsize(path)
    assert new <= old, f'a/0/3/9 grew {old} -> {new} B (no RESERVE: the ROM layout would move)'
    if new < old:                                      # pad inside GMIF to the old size (the file table stays the same)
        d = bytearray(open(path, 'rb').read())
        hdr, = struct.unpack_from('<H', d, 0xC); o = hdr
        for _ in range(2): o += struct.unpack_from('<I', d, o + 4)[0]
        assert d[o:o + 4] == b'GMIF'
        struct.pack_into('<I', d, o + 4, struct.unpack_from('<I', d, o + 4)[0] + old - new)
        struct.pack_into('<I', d, 8, old)
        if os.path.islink(path): os.unlink(path)
        open(path, 'wb').write(bytes(d) + bytes(old - new))
    return f'a/0/3/9: pennants, badge case, badges ({"; ".join(log)}; {free} tile slots spare); {old} B kept'


def apply_code(code):
    path = os.path.join(code, OV186)
    d = bytearray(open(path, 'rb').read())
    at = CLASS_TABLE - OV186_BASE
    now = list(struct.unpack_from('<8H', d, at))
    assert now in (CLASS_OLD, CLASS_NEW), f'ov186 {CLASS_TABLE:#x}: unexpected {now}'
    struct.pack_into('<8H', d, at, *CLASS_NEW)
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(bytes(d))
    return f'{OV186} {CLASS_TABLE:#x}: badge-page leader classes {CLASS_NEW}'
