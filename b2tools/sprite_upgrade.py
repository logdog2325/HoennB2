"""Sapphire's own sprites redrawn in Gen 5 style (DECISIONS 2026-10-06, "character sprites from Sapphire's own art";
user 2026-10-06: touched up lightly "to the point where they look like actual Gen 5 sprites from Black 2 and White 2").

    python3 sprite_upgrade.py [name ...]        default: every character in CHARS
        -> src/sprites/trainer/front/<slot>-<name>/ and src/sprites/overworld/<code>-<name>/ (installed by
           patches/sprites.py) and screenshots/sprites/upgrade_review.png
    python3 sprite_upgrade.py review [name ...]  only the review sheet (Sapphire / Black 2 reference / new)

Characters (slots registered in data/sprite_map.json; front = a/0/7/1 sprite, ow = object code):
    Aqua grunt M front 149 / ow 293, Aqua grunt F 150 / 294, Archie 151 / 353, Matt 152 / 88, Shelly 153 / 92,
    Magma grunt M 154 / 302, Magma grunt F 156 / 192, Maxie 148 / 303, Wally 127 / 87, Sidney 79 / 94, Phoebe
    77 / 93, Glacia 80 / 96, Drake 78 / 89. Sapphire battles no Magma trainer (its admins Tabitha/Courtney are Ruby's),
    so 148/154/156 are drawn but no Hoenn class shows them yet. Sapphire draws Matt and Shelly with the grunt overworld
    sprites; their own sheets are the grunt sheets changed to their battle designs (matt_frame, shelly_frame).
    Ruby (HOENN_VERSION=ruby python3 sprite_upgrade.py): Tabitha front 152 / ow 88, Courtney 153 / 92 (Matt's and
    Shelly's slots, which play the Magma admins in Ruby), written to the ruby/ overlay folders
    (src/sprites/trainer/front/ruby/, src/sprites/overworld/ruby/; notes/RUBY.md "WP0 layout"), plus the overworld
    art swap RUBY_SWAPS (ruby/ folders with only {"copy_of": N}: Magma art on the evil-team codes 293/294/353, Aqua
    art on the good-team codes 302/192/303) and screenshots/sprites/upgrade_review_ruby.png. Their battle pictures
    are pokeruby's magma_admin_m / magma_admin_f; Ruby has no overworld sprite for either (it shows the grunts), so
    their sheets are the Magma grunt sheets changed to their battle designs (tabitha_frame, courtney_frame).
    Test: HOENN_TEST_SPRITES=trainer,code (scripts patch): Littleroot's town sign makes object `code` walk a loop,
    then battles Black 2 trainer `trainer` (345 = Ghetsis's class, front 151).

Source art: pokeruby graphics/trainers/<pic>.png (battle, 64x64) and graphics/object_events/pics/people/*.png
(overworld, 16x32 frames, palette from the object's palette tag), loaded as converter/sprite_sheet.py does. Each
picture keeps the Gen 3 drawing (design, pose, colours) and is brought to Black 2's size and style:

  1. clean-up: single stray pixels inside a colour area (Gen 3 dithering / noise) take the area's colour
  2. Gen 5 proportions and size: battle pictures fill Black 2's 80x80 still with the head x1.15, the body below the
     neck x1.35 tall (Gen 5 limbs, up to the canvas) and x1.2 wide; overworld 16x20 figures -> about 19x28 in the
     32x32 frame (head x1.25, body x1.5 tall). Nearest-neighbour, then every feature that was one pixel wide
     (outlines, creases, eyes) and got doubled is thinned back to one pixel, keeping the copy on the side where it
     continues diagonally, and doubled steps of outlines are removed (clean_corners), so lines stay one pixel thick
  3. Gen 5 outlines: the figure's edge is outlined; black on clothes, but around skin and hair the material's own
     dark tone (colour_outlines), as Black 2 draws them; dark masses (a beard) keep a black edge
  4. colours: Black 2's own skin ramps (B2_SKIN, B2_SKIN_OW: the same four tones on every Black 2 person), the rest
     Sapphire's palette (15 colours + clear) with per-character changes listed in CHARS; overworld sheets take the
     character's colours from their battle picture where the Gen 3 overworld palette was a shared one
  5. hand fixes per character (fixes: pixel overlays on the picture)

Battle sprites keep Black 2's MCSS layout (b2tools/mcss.py): the picture is cut onto the parts of a Black 2 trainer
("layout"), whose 8 files the build copies into the slot (sprite.json "mcss_from"), so the slot plays that trainer's
intro gesture with the new art; a layout whose parts cannot show every pixel is refused. "intro": "still" makes the
sprite stand still during the intro (sprite.json "static_intro": the build points the intro's frames at the still
figure), for pictures no clean Black 2 gesture fits. Overworld sheets use Black 2's 12-frame layout (controller 3: up,
down, left, right x stand + 2 steps; the steps rise one pixel as Black 2's do; right = left mirrored, as Sapphire does).
"""
import json, os, shutil, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import sprites, mcss  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

SRC = os.path.join(ROOT, 'src', 'sprites')
SHOTS = os.path.join(ROOT, 'screenshots', 'sprites')
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
FILES = sprites.SRC_FILES
OUTLINE = 15

# ---------------------------------------------------------------------------------------------------- Sapphire art

_S = {}
def sapphire():
    if 's' not in _S:
        import sprite_sheet
        _S['s'] = sprite_sheet.Sapphire()
    return _S['s']

def gen3_trainer(pic):
    """(64x64 index array, 16 RGB) of graphics/trainers/<pic>.png (its PNG palette is the game's)."""
    from PIL import Image
    im = Image.open(os.path.join(RUBY, 'graphics', 'trainers', f'{pic}.png'))
    p = im.getpalette()[:48]
    return np.array(im).astype(np.uint8), [tuple(p[3 * i:3 * i + 3]) for i in range(16)]

def gen3_overworld(gfx):
    """([9 frames, 32x16 index arrays], 16 RGB): Sapphire's frames 0 down, 1 up, 2 left, 3-4 down walking,
    5-6 up walking, 7-8 left walking (gObjectEventPicTable_*), palette of the object's palette tag."""
    from PIL import Image
    S = sapphire()
    info = S.info[S.info_of[gfx]]
    pal = S.tag_pal[info['palette_tag']]
    vals = open(os.path.join(S.root, S.pal_file[pal])).read().split()
    rgb = [tuple(int(v) for v in vals[3 + 3 * i:6 + 3 * i]) for i in range(int(vals[2]))]
    frames = []
    for pic, w, h, k in S.pic_table[info['images']]:
        png = Image.open(os.path.join(S.root, S.pic_file[pic]))
        fw, fh = w * 8, h * 8; per_row = max(1, png.width // fw)
        box = (k % per_row * fw, k // per_row * fh, k % per_row * fw + fw, k // per_row * fh + fh)
        frames.append(np.array(png.crop(box)).astype(np.uint8))
    return frames, (rgb + [(0, 0, 0)] * 16)[:16]

# ---------------------------------------------------------------------------------------------------- drawing steps

def undither(a, pal, maxdist=90):
    """Single pixels whose 4 neighbours are all one other, similar colour take that colour (not outline/clear, not
    white: a white speck is a shine)."""
    H, W = a.shape; out = a.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            v = a[y, x]
            if v in (0, OUTLINE) or min(pal[v]) >= 230:        # white specks are shines, kept
                continue
            n = {a[y - 1, x], a[y + 1, x], a[y, x - 1], a[y, x + 1]}
            if len(n) != 1:
                continue
            b = n.pop()
            if b in (0, OUTLINE, v):
                continue
            if sum((p - q) ** 2 for p, q in zip(pal[v], pal[b])) ** 0.5 <= maxdist:
                out[y, x] = b
    return out

def axis_map(n_in, n_out):
    """Source index of every output index for a uniform scale (centre sampling)."""
    return np.minimum(n_in - 1, np.floor((np.arange(n_out) + 0.5) * n_in / n_out).astype(int))

def scale_cols(a, idx):
    """Columns of `a` resampled by the source-index map `idx`; one-pixel-wide features that got repeated keep one
    copy (on the side where they continue diagonally), the other copies take the neighbouring colour."""
    H, W = a.shape
    out = a[:, idx].copy()
    runs = {}
    for o, c in enumerate(idx):
        runs.setdefault(int(c), []).append(o)
    for c, outs in runs.items():
        if len(outs) < 2:
            continue
        for r in range(H):
            v = a[r, c]
            L = a[r, c - 1] if c > 0 else 0
            R = a[r, c + 1] if c + 1 < W else 0
            if L == v or R == v:
                continue
            def has(rr, cc):
                return 0 <= rr < H and 0 <= cc < W and a[rr, cc] == v
            right = has(r - 1, c + 1) or has(r + 1, c + 1)
            left = has(r - 1, c - 1) or has(r + 1, c - 1)
            if right and left:
                continue
            keep = outs[-1] if right else outs[0] if left else outs[len(outs) // 2 if len(outs) > 2 else 0]
            for o in outs:
                if o < keep:
                    out[r, o] = L
                elif o > keep:
                    out[r, o] = R
    return out

def rescale(a, xmap, ymap):
    return scale_cols(scale_cols(a, xmap).T, ymap).T

def outline_edges(a):
    """Gen 5 outline: opaque pixels next to clear ones (4-neighbourhood) become the outline colour."""
    op = a != 0
    pad = np.pad(op, 1)
    edge = op & (~pad[:-2, 1:-1] | ~pad[2:, 1:-1] | ~pad[1:-1, :-2] | ~pad[1:-1, 2:])
    out = a.copy(); out[edge] = OUTLINE
    return out

def clean_corners(a, colour=OUTLINE):
    """Pixel-perfect lines: a pixel of `colour` that only joins two neighbours at a right angle ("L" corner) while
    those two already touch diagonally is a doubled step of the scaled line; it takes the colour of the side it sits
    on (the most common of its other neighbours), so outlines are clean one-pixel diagonals as Gen 5 draws them."""
    H, W = a.shape
    out = a.copy()
    def at(y, x): return a[y, x] if 0 <= y < H and 0 <= x < W else 0
    for y in range(H):
        for x in range(W):
            if a[y, x] != colour:
                continue
            n = {d: at(y + dy, x + dx) == colour for d, (dy, dx) in
                 dict(u=(-1, 0), d=(1, 0), l=(0, -1), r=(0, 1)).items()}
            for v, h in (('u', 'l'), ('u', 'r'), ('d', 'l'), ('d', 'r')):
                ov, oh = {'u': 'd', 'd': 'u'}[v], {'l': 'r', 'r': 'l'}[h]
                if not (n[v] and n[h]) or n[ov] or n[oh]:
                    continue
                dy, dx = (-1 if v == 'u' else 1), (-1 if h == 'l' else 1)
                if at(y + dy, x + dx) == colour:          # a filled 2x2 block, not a doubled step
                    continue
                side = [at(y - dy, x), at(y, x - dx), at(y - dy, x - dx)]
                side = [c for c in side if c != colour]
                if side:
                    out[y, x] = max(set(side), key=side.count)
                break
    return out

def colour_outlines(a, groups):
    """Black 2 outline colours: Black 2 outlines are black on clothes but take a dark tone of the material around
    skin and hair. groups = [(member indices, outline index, last row or None)]: an outline pixel whose coloured
    neighbours (4-neighbourhood) all belong to one group, and that sits on the figure's edge or on a line of such pixels
    reaching it (finger lines, the jaw), takes the group's outline colour. Lines inside a face that do not reach the
    edge (eyes, mouth) stay black."""
    H, W = a.shape
    cand = np.zeros((H, W), np.int16) - 1
    for y in range(H):
        for x in range(W):
            if a[y, x] != OUTLINE:
                continue
            nb = [a[j, i] for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if 0 <= j < H and 0 <= i < W and a[j, i] not in (0, OUTLINE)]
            if not nb:
                continue
            for members, oi, last in groups:
                if (last is None or y < last) and all(v in members for v in nb):
                    cand[y, x] = oi
                    break
    bk = np.pad(a == OUTLINE, 1)                    # black areas (a beard, dark clothes) keep a black edge
    mass = (a == OUTLINE) & bk[:-2, 1:-1] & bk[2:, 1:-1] & bk[1:-1, :-2] & bk[1:-1, 2:]
    near = np.zeros((H, W), bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near |= np.roll(np.roll(mass, dy, 0), dx, 1)
    cand[near] = -1
    op = np.pad(a != 0, 1)
    edge = (a != 0) & (~op[:-2, 1:-1] | ~op[2:, 1:-1] | ~op[1:-1, :-2] | ~op[1:-1, 2:])
    keep = np.zeros((H, W), bool)
    stack = [(y, x) for y, x in zip(*np.nonzero(edge & (cand >= 0)))]
    while stack:
        y, x = stack.pop()
        if keep[y, x]:
            continue
        keep[y, x] = True
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                j, i = y + dy, x + dx
                if 0 <= j < H and 0 <= i < W and not keep[j, i] and cand[j, i] == cand[y, x]:
                    stack.append((j, i))
    out = a.copy()
    out[keep] = cand[keep]
    return out

def fill_mass(a, members, fill):
    """Gen 3 overworld sprites draw dark clothes as solid outline colour; Black 2 draws them in a dark fill inside a
    one-pixel outline. Outline pixels whose 4 neighbours are all opaque and of the clothes' colours (`members`, plus
    the outline) take palette index `fill`."""
    H, W = a.shape
    ok = np.isin(a, list(set(members) | {OUTLINE}))
    pad = np.pad(ok, 1)
    inner = (a == OUTLINE) & pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    out = a.copy(); out[inner] = fill
    return out

def overlay(a, fix):
    """Hand fix: fix = (x, y, rows) with rows of hex digits ('.' = keep, '_' = clear)."""
    x0, y0, rows = fix
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            a[y0 + j, x0 + i] = 0 if ch == '_' else int(ch, 16)
    return a

# ---------------------------------------------------------------------------------------------------- characters
# battle: pic = pokeruby trainer pic; slot = Black 2 front sprite (a/0/7/1) that gets the art; layout = Black 2
#   sprite whose parts/animation it uses; intro 'gesture' (the layout's) or 'still'; colours = {index: rgb};
#   fixes = overlays on the 80x80 picture.
# overworld: gfx = Sapphire graphics id; code = Black 2 object code that gets the sheet; colours = {index: rgb};
#   neck = row of the 32-row Sapphire frame where the body starts.

SKIN = {1: (255, 222, 205), 2: (238, 180, 148), 3: (197, 139, 106), 4: (106, 74, 74)}   # Sapphire's battle skin
# Black 2's own skin ramps (every Black 2 trainer / person uses them; the darkest is the skin's outline colour)
B2_SKIN = {1: (255, 214, 189), 2: (222, 173, 132), 3: (189, 115, 90), 4: (123, 74, 90)}
B2_SKIN_OW = {1: (255, 214, 189), 2: (239, 181, 140), 3: (214, 156, 115), 4: (123, 74, 49)}
SKIN_GROUP = ({1, 2, 3, 4}, 4)          # skin indices of every Sapphire palette, outline = the darkest

CHARS = {
    'aqua-grunt-m': dict(
        note='Team Aqua grunt (M)',
        battle=dict(pic='aqua_grunt_m', slot=149, layout=73, intro='gesture', neck=20),
        overworld=dict(gfx='OBJ_EVENT_GFX_AQUA_MEMBER_M', code=293, neck=22, colours={
            **SKIN, 5: (90, 131, 189), 6: (65, 90, 139), 7: (33, 49, 90), 11: (213, 222, 230), 13: (57, 57, 66)})),
    'aqua-grunt-f': dict(
        note='Team Aqua grunt (F)',
        battle=dict(pic='aqua_grunt_f', slot=150, layout=73, intro='still', neck=20, hair=[({10, 12, 13}, 10)]),
        overworld=dict(gfx='OBJ_EVENT_GFX_AQUA_MEMBER_F', code=294, neck=22, hair=[({8, 9, 10}, 10)], colours={
            **SKIN, 5: (90, 131, 189), 6: (65, 90, 139), 7: (33, 49, 90), 8: (255, 106, 98), 9: (205, 82, 74),
            10: (164, 74, 65), 11: (213, 222, 230)})),
    'archie': dict(
        note='Archie (Team Aqua leader)',
        battle=dict(pic='archie', slot=151, layout=73, intro='gesture', neck=17),
        overworld=dict(gfx='OBJ_EVENT_GFX_ARCHIE', code=353, neck=22, colours={
            **SKIN, 8: (148, 156, 222), 9: (106, 115, 213), 10: (82, 90, 156), 11: (213, 213, 222),
            12: (106, 123, 148), 13: (82, 90, 115)},
            mass=(5, (49, 55, 86), {12, 13}))),
    'matt': dict(
        note='Matt (Team Aqua admin)',
        battle=dict(pic='aqua_admin_m', slot=152, layout=152, intro='still', neck=17, hair=[({10, 12, 13}, 13)]),
        overworld=dict(base='aqua-grunt-m', edit='matt', code=88)),
    'shelly': dict(
        note='Shelly (Team Aqua admin)',
        battle=dict(pic='aqua_admin_f', slot=153, layout=152, intro='still', neck=15, hair=[({10, 12, 13}, 13, 'all')]),
        overworld=dict(base='aqua-grunt-f', edit='shelly', code=92, colours={
            8: (255, 131, 41), 9: (238, 98, 41), 10: (180, 65, 41), 13: (57, 57, 66)})),
    'magma-grunt-m': dict(
        note='Team Magma grunt (M)',
        battle=dict(pic='magma_grunt_m', slot=154, layout=57, intro='gesture', neck=22),
        overworld=dict(gfx='OBJ_EVENT_GFX_MAGMA_MEMBER_M', code=302, neck=22, colours={
            **SKIN, 8: (222, 82, 98), 9: (189, 57, 74), 10: (139, 49, 65), 12: (90, 90, 90), 13: (57, 57, 65)},
            mass=(5, (66, 66, 74), {12, 13}))),
    'magma-grunt-f': dict(
        note='Team Magma grunt (F)',
        battle=dict(pic='magma_grunt_f', slot=156, layout=73, intro='still', neck=18, hair=[({7, 9}, 9)]),
        overworld=dict(gfx='OBJ_EVENT_GFX_MAGMA_MEMBER_F', code=192, neck=22, hair=[({11, 12}, 12)], colours={
            **SKIN, 7: (41, 49, 82), 8: (222, 82, 98), 9: (189, 57, 74), 10: (139, 49, 65), 11: (82, 98, 148),
            12: (65, 74, 115), 13: (57, 57, 65)},
            mass=(5, (66, 66, 74), {13}))),
    'maxie': dict(
        note='Maxie (Team Magma leader)',
        battle=dict(pic='maxie', slot=148, layout=108, intro='gesture', neck=14, hair=[({10, 12, 13}, 10)]),
        overworld=dict(gfx='OBJ_EVENT_GFX_MAXIE', code=303, neck=22, hair=[({8, 9, 10}, 10)], colours={
            **SKIN, 8: (213, 82, 90), 9: (180, 41, 57), 10: (131, 16, 41), 12: (74, 82, 98)},
            mass=(5, (49, 57, 82), {12}))),
    'wally': dict(
        note='Wally',
        battle=dict(pic='wally', slot=127, layout=108, intro='gesture', neck=21, hair=[({7, 8, 10, 11}, 11)]),
        overworld=dict(gfx='OBJ_EVENT_GFX_WALLY', code=87, neck=22, hair=[({11, 12, 13}, 13)], colours={
            **SKIN, 8: (156, 196, 238), 9: (98, 156, 222), 10: (49, 82, 140), 11: (189, 205, 98), 12: (148, 172, 74),
            13: (65, 106, 24)})),
    'sidney': dict(
        note='Sidney (Elite Four)',
        battle=dict(pic='sidney', slot=79, layout=51, intro='gesture', neck=22, hair=[({11, 12}, 12)]),
        overworld=dict(gfx='OBJ_EVENT_GFX_SIDNEY', code=94, neck=22, hair=[({8, 9}, 10)], colours={
            **SKIN, 5: (238, 213, 139), 6: (197, 164, 106), 7: (131, 106, 74), 8: (255, 98, 90), 9: (197, 65, 65),
            10: (98, 24, 33), 13: (57, 65, 82)},
            mass=(12, (57, 65, 82), {13}))),
    'phoebe': dict(
        note='Phoebe (Elite Four)',
        battle=dict(pic='phoebe', slot=77, layout=73, intro='gesture', neck=20, hair=[({10, 11}, 11), ({12, 13}, 13)]),
        overworld=dict(gfx='OBJ_EVENT_GFX_PHOEBE', code=93, neck=22, hair=[({11, 12, 13}, 13), ({5, 6, 7}, 7)], colours={
            **SKIN, 5: (255, 82, 156), 6: (197, 65, 90), 7: (123, 41, 74), 8: (57, 131, 255), 9: (32, 106, 230),
            10: (41, 49, 123), 11: (156, 131, 131), 12: (115, 98, 106), 13: (74, 57, 65), 14: (255, 255, 255),
            15: (0, 0, 0)})),
    'glacia': dict(
        note='Glacia (Elite Four)',
        battle=dict(pic='glacia', slot=80, layout=86, intro='still', neck=16, hair=[({9, 10, 11}, 4)]),
        overworld=dict(gfx='OBJ_EVENT_GFX_GLACIA', code=96, neck=22, hair=[({5, 6, 7}, 4)], colours={
            **SKIN, 5: (255, 255, 164), 6: (213, 197, 90), 7: (156, 148, 90), 8: (148, 90, 164), 9: (115, 65, 123),
            10: (82, 41, 82), 11: (189, 197, 205), 12: (148, 148, 164), 13: (82, 41, 82), 14: (222, 230, 238)})),
    'drake': dict(
        note='Drake (Elite Four)',
        battle=dict(pic='drake', slot=78, layout=62, intro='still', neck=16),
        overworld=dict(gfx='OBJ_EVENT_GFX_DRAKE', code=89, neck=22, colours={
            **SKIN, 5: (197, 197, 213), 6: (139, 131, 164), 7: (106, 98, 123), 10: (255, 222, 106),
            12: (139, 82, 82), 13: (98, 57, 65)},
            mass=(11, (57, 65, 82), {6, 7, 10}))),
    # Ruby (version='ruby': written to the ruby/ overlay folders, notes/RUBY.md "WP0 layout"; the Ruby ROM puts them
    # in Matt's and Shelly's slots, which play the Magma admins there). Ruby draws both with the grunt overworld
    # sprites, so their sheets are the Magma grunt sheets changed to their battle designs, as Matt's and Shelly's.
    'tabitha': dict(
        note='Tabitha (Team Magma admin)', version='ruby',
        battle=dict(pic='magma_admin_m', slot=152, layout=152, intro='still', neck=19),
        overworld=dict(base='magma-grunt-m', edit='tabitha', code=88, colours={
            6: (123, 123, 123), 7: (189, 189, 180)})),
    'courtney': dict(
        note='Courtney (Team Magma admin)', version='ruby',
        battle=dict(pic='magma_admin_f', slot=153, layout=153, intro='still', neck=19, hair=[({7, 9}, 9)]),
        overworld=dict(base='magma-grunt-f', edit='courtney', code=92, colours={
            6: (123, 123, 123), 7: (189, 189, 180), 13: (90, 90, 90)})),
}

def char_version(name):
    return CHARS[name].get('version', 'sapphire')

# Ruby's overworld art swap (notes/RUBY.md 3.2 "Models / sprites"): the story objects keep Sapphire's codes for their
# roles (evil team M/F, evil leader, good team M/F, good leader), so in Ruby those codes trade art. Each entry is a
# ruby/ folder holding only sprite.json {"copy_of": shared folder}: code -> (name, shared code whose art it shows).
RUBY_SWAPS = {'overworld': {293: ('magma-grunt-m', 302), 294: ('magma-grunt-f', 192), 353: ('maxie', 303),
                            302: ('aqua-grunt-m', 293), 192: ('aqua-grunt-f', 294), 303: ('archie', 353)}}

# ---------------------------------------------------------------------------------------------------- battle

_tr = {}
def tr_entries(side='front'):
    if side not in _tr:
        _tr[side] = narc_entries(arc_path(FILES, sprites.ARC_TR[side]))
    return _tr[side]

def tr_donor(s):
    e = tr_entries()
    _, pal = sprites.nclr_colors(e[8 * s + 7])
    _, _, parts = sprites.tr_decode_image(e[8 * s + 1], 'parts')
    _, _, still = sprites.tr_decode_image(e[8 * s], 'static')
    return (np.frombuffer(parts, np.uint8).reshape(128, 256).copy(), np.frombuffer(still, np.uint8).reshape(80, 80).copy(),
            [sprites.bgr555_to_rgb(c) for c in pal], mcss.Sprite(e, 8 * s))

HEAD_Y, BODY_Y, WIDE = 1.15, 1.35, 1.2   # battle: head x1.15, body x1.35 tall (Gen 5 limbs), x1.2 wide

def battle_picture(spec):
    """(80x80 picture, 16 RGB) of a character's battle sprite: Sapphire's pic cleaned, scaled to Gen 5 proportions
    (head x1.15, body below spec['neck'] x1.35 up to the 80-row canvas, x1.2 wide), Gen 5 outlines (black on
    clothes, skin's and hair's own dark tone around them), Black 2's skin ramp, hand fixes."""
    a, pal = gen3_trainer(spec['pic'])
    pal = list(pal)
    for i, c in {**spec.get('colours', {}), **B2_SKIN}.items():
        pal[i] = tuple(c)
    a = undither(a, pal)
    ys, xs = np.nonzero(a)
    top, bot, neck = ys.min(), ys.max(), spec['neck']
    head, body = np.arange(top, neck), np.arange(neck, bot + 1)
    hn = round(len(head) * HEAD_Y)
    bn = min(round(len(body) * BODY_Y), 80 - hn)
    ymap = np.concatenate([head[axis_map(len(head), hn)], body[axis_map(len(body), bn)]])
    b = clean_corners(outline_edges(rescale(a, axis_map(64, round(64 * WIDE)), ymap)))
    groups = [(*SKIN_GROUP, None)] + [(set(h[0]), h[1], None if h[2:] == ('all',) else hn + 2)
                                      for h in spec.get('hair', [])]
    b = colour_outlines(b, groups)
    out = np.zeros((80, 80), np.uint8)
    h, w = b.shape
    out[80 - h:, (80 - w) // 2:(80 - w) // 2 + w] = b
    for fix in spec.get('fixes', []):
        overlay(out, fix)
    return out, pal

def battle_sprite(spec):
    """(still 80x80, parts 128x256, palette, report) on the layout's parts."""
    still, pal = battle_picture(spec)
    dparts, dstill, dpal, sp = tr_donor(spec['layout'])
    off = mcss.still_offset(sp, dparts, dstill)
    W, H = mcss.CANVAS
    ys, xs = np.nonzero(still)
    whole, partsm = mcss.coverage(sp, dparts)
    shifts = [tuple(spec['shift'])] if 'shift' in spec else \
        sorted(((dx, dy) for dx in range(-12, 13) for dy in range(-4, 3)), key=lambda d: abs(d[0]) + abs(d[1]))
    def lost(dx, dy):                # pixels the whole-figure cell / the parts cannot show at this placement
        X, Y = xs + off[0] + dx, ys + off[1] + dy
        ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
        return (int((~ok).sum() + (~whole[Y[ok], X[ok]]).sum()),
                0 if spec.get('intro') == 'still' else int((~ok).sum() + (~partsm[Y[ok], X[ok]]).sum()))
    dx, dy = min(shifts, key=lambda d: lost(*d))      # first (smallest) shift among the best
    fig = np.zeros((H, W), np.uint8)
    fig[ys + off[1] + dy, xs + off[0] + dx] = still[ys, xs]
    parts, rep = mcss.distribute(sp, dparts, fig, OUTLINE)
    rep = dict(rep, shift=(dx, dy))
    if rep['lost_in_whole'] or (spec.get('intro') != 'still' and rep['lost_in_parts']):
        raise SystemExit(f'{spec["pic"]}: layout {spec["layout"]} cannot show every pixel ({rep}): pick another '
                         f'layout or intro="still"')
    return still, parts, pal, rep, sp, off

def write_battle(name, ch):
    spec = ch['battle']
    still, parts, pal, rep, sp, off = battle_sprite(spec)
    slot, layout = spec['slot'], spec['layout']
    kind_dir = kind_folder(name, 'trainer', 'front')
    folder = os.path.join(kind_dir, f'{slot:03d}-{name}')
    _replace_folder(kind_dir, slot, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), parts.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), still.tobytes(), 80, 80, pal)
    meta = dict(kind='trainer', side='front', sprite=slot, archive=sprites.ARC_TR['front'], files=sprites.tr_files(slot),
                name=name, note=ch['note'], source=f'pokeruby graphics/trainers/{spec["pic"]}.png',
                layout=f'parts and animations of Black 2 front sprite {layout}', made_by='b2tools/sprite_upgrade.py')
    if layout != slot:
        meta['mcss_from'] = layout
    if spec.get('intro') == 'still':
        meta['static_intro'] = True
    sprites.write_json(os.path.join(folder, 'sprite.json'), meta)
    return folder, rep

# ---------------------------------------------------------------------------------------------------- overworld

OW_HEAD_Y, OW_BODY_Y, OW_X = 1.25, 1.5, 1.2
OW_FEET = 30                 # Black 2's standing frames end on row 30 (steps one row lower, one higher)

def ow_figure(f, neck):
    """One Sapphire 16x32 frame scaled to Black 2 proportions: (array, its feet row, its centre x)."""
    ys, xs = np.nonzero(f)
    top, bot = ys.min(), ys.max()
    head = np.arange(top, neck); body = np.arange(neck, bot + 1)
    ymap = np.concatenate([head[axis_map(len(head), round(len(head) * OW_HEAD_Y))],
                           body[axis_map(len(body), round(len(body) * OW_BODY_Y))]])
    xmap = axis_map(16, round(16 * OW_X))
    return rescale(f, xmap, ymap)

def ow_frames(spec):
    """12 Black 2 frames (and 16 colours) of a character's overworld sheet; spec 'base' + 'edit' = the frames of
    another character's sheet changed by an EDITS function (Matt and Shelly: Sapphire draws them with the grunts)."""
    if 'base' in spec:
        frames, pal = ow_frames(CHARS[spec['base']]['overworld'])
        pal = list(pal)
        for i, c in spec.get('colours', {}).items():
            pal[i] = tuple(c)
        frames = [EDITS[spec['edit']](f, k) for k, f in enumerate(frames[:9])]
        return frames + [f[:, ::-1].copy() for f in frames[6:9]], pal
    frames, pal = gen3_overworld(spec['gfx'])
    pal = list(pal)
    for i, c in {**spec.get('colours', {}), **B2_SKIN_OW}.items():
        pal[i] = tuple(c)
    big = [outline_edges(ow_figure(undither(f, pal), spec['neck'])) for f in frames]
    if 'mass' in spec:
        idx, rgb, members = spec['mass']
        pal[idx] = tuple(rgb)
        big = [fill_mass(b, members, idx) for b in big]
    head_rows = round((spec['neck'] - 11) * OW_HEAD_Y) + 1        # Sapphire's people start on row ~11
    groups = [(*SKIN_GROUP, None)] + [(set(h[0]), h[1], None if h[2:] == ('all',) else head_rows)
                                      for h in spec.get('hair', [])]
    big = [colour_outlines(b, groups) for b in big]
    def place(b, rise=0):
        out = np.zeros((32, 32), np.uint8)
        h, w = b.shape
        x0 = 16 - w // 2; y0 = OW_FEET + 1 - h - rise
        out[max(0, y0):y0 + h, x0:x0 + w] = b[max(0, -y0):, :]
        return out
    def step(b):                     # body rises one pixel, the hips stretch to keep the feet on the ground
        hip = int(b.shape[0] * 0.62)
        return np.vstack([b[:hip], b[hip - 1:hip], b[hip:]])
    order = [(1, 0), (5, 1), (6, 1), (0, 0), (3, 1), (4, 1), (2, 0), (7, 1), (8, 1)]   # up, down, left x stand/steps
    out = [bigger_eyes(place(step(big[k]), 0) if s else place(big[k])) for k, s in order]
    out += [f[:, ::-1].copy() for f in out[6:9]]
    return out, pal

def bigger_eyes(f, skin=(1, 2, 3), last_row=20):
    """Gen 5 overworld eyes are two pixels tall; Sapphire's are often one. A single eye pixel (any colour but skin,
    skin left, right and below, the brow or hair above) in the face grows one pixel down onto the skin below it."""
    out = f.copy()
    H, W = f.shape
    for y in range(1, min(last_row, H - 2)):
        for x in range(1, W - 1):
            v = f[y, x]
            if v == 0 or v in skin or v == 4:
                continue
            if f[y - 1, x] not in (0, v) and all(f[j, i] in skin for j, i in ((y + 1, x), (y, x - 1), (y, x + 1))):
                out[y + 1, x] = v
    return out

def _torso(f, colours):
    """(top row, bottom row, centre x) of the rows holding the shirt colours `colours` below the head."""
    rows = [y for y in range(10, 28) if np.isin(f[y], list(colours)).sum() >= 2]
    if not rows:
        return None
    xs = np.nonzero(np.isin(f[rows[0]:rows[-1] + 1], list(colours)).any(axis=0))[0]
    return rows[0], rows[-1], (xs.min() + xs.max()) / 2

def matt_frame(f, k):
    """Matt from the Aqua grunt (M) frames: Sapphire's battle Matt wears an open sleeveless blue vest over a bare
    chest and bare arms, where the grunt wears a striped shirt. Front: chest skin down the middle, vest beside it,
    arms skin; back: the vest; side: the vest with a bare arm."""
    out = f.copy()
    stripes = {11, 12, 13, 14}
    t = _torso(f, stripes)
    if t is None:
        return out
    r0, r1, cx = t
    for y in range(r0, r1 + 1):
        for x in range(32):
            v = f[y, x]
            d = abs(x - cx)
            if k in (3, 4, 5):                                     # front
                if v in stripes:
                    out[y, x] = (1 if d <= 1 else 2) if d <= 2 else (5 if v in (11, 14) else 6) if d <= 4 else \
                        (2 if v in (11, 14) else 3)
            elif k in (0, 1, 2):                                   # back: the vest
                if v in stripes or (v == OUTLINE and d <= 4 and 0 < y < 31 and 0 not in
                                    (f[y - 1, x], f[y + 1, x], f[y, x - 1], f[y, x + 1])):
                    out[y, x] = 5 if v in (11, 14) else 6 if d <= 4 else (2 if v in (11, 14) else 3)
            else:                                                  # side: vest, the near arm bare
                if v in stripes:
                    out[y, x] = 5 if v in (11, 14) else 6
    return out

def shelly_frame(f, k):
    """Shelly from the Aqua grunt (F) frames: long orange hair (the grunt's side bunches grown three rows longer,
    over the back from behind), a black top inside the blue vest."""
    out = f.copy()
    hair = {8, 9, 10}
    t = _torso(f, {5, 6})
    hy, hx = np.nonzero(np.isin(f, list(hair)))
    if len(hy):
        cx = (hx.min() + hx.max()) / 2
        for x in sorted(set(hx.tolist())):
            col = hy[hx == x]
            bottom = col.max()
            if k in (0, 1, 2) or abs(x - cx) >= 4:                # behind the head / beside the shoulders
                for y in range(bottom + 1, min(31, bottom + 4)):
                    if k in (0, 1, 2) or f[y, x] in (0, OUTLINE):
                        out[y, x] = 9 if y < bottom + 3 else 10
        out = colour_outlines(outline_edges(out), [(*SKIN_GROUP, None), ({8, 9, 10}, 10, None)])
    if t is not None and k in (3, 4, 5):                          # front: the black top between the vest's edges
        r0, r1, cx = t
        for y in range(r0, min(r1 + 1, r0 + 3)):
            for x in range(32):
                if f[y, x] in (5, 6) and abs(x - cx) <= 2:
                    out[y, x] = 13
    return out

def _components(mask):
    """Lists of (y, x) of the 4-connected components of a bool mask."""
    seen = np.zeros_like(mask, bool); out = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        comp, todo = [], [(y, x)]; seen[y, x] = True
        while todo:
            j, i = todo.pop(); comp.append((j, i))
            for b, a in ((j + 1, i), (j - 1, i), (j, i + 1), (j, i - 1)):
                if 0 <= b < mask.shape[0] and 0 <= a < mask.shape[1] and mask[b, a] and not seen[b, a]:
                    seen[b, a] = True; todo.append((b, a))
        out.append(comp)
    return out

def tabitha_frame(f, k):
    """Tabitha (Ruby) from the Magma grunt (M) frames: Ruby draws him with the grunt sprite; his battle picture wears
    lighter grey trousers with pale bands and a plain hood (the grunt's hood has the Magma emblem). Trousers: the
    grunt's dark grey below the waist (front: dark areas not joined to the gloves; back from row 24, side from row
    23) becomes colour 6, the widest trouser row under the top one the pale band 7. Front: the hood's emblem (black,
    rows 8-10 around x 16) takes the hood colour beside it. (His emblem moved to the chest was tried: the chest is
    5 pixels between the arm lines and it read as a black smudge.)"""
    out = f.copy()
    view = k // 3                                   # 0 back, 1 front, 2 side
    pants = np.zeros_like(f, bool)
    if view == 1:
        for comp in _components(np.isin(f, (5, 12, 13))):
            if min(y for y, _ in comp) >= 23:
                for y, x in comp:
                    pants[y, x] = f[y, x] == 5
    else:
        top = 24 if view == 0 else 23
        pants[top:] = f[top:] == 5
    out[pants] = 6
    rows = [y for y in range(23, 31) if pants[y].any()]
    if len(rows) > 1:
        by = max(rows[1:], key=lambda y: (int(pants[y].sum()), -y))
        if pants[by].sum() >= 3:
            out[by][pants[by]] = 7
    if view == 1:
        logo = [(y, x) for y in range(8, 11) for x in range(13, 20) if f[y, x] in (OUTLINE, 5)]
        for y, x in logo:
            l = x
            while (y, l) in logo:
                l -= 1
            out[y, x] = f[y, l]
    return out

def courtney_frame(f, k):
    """Courtney (Ruby) from the Magma grunt (F) frames: her hair stays inside the hood (the grunt's long blue strands
    from row 14 down become the red of her cape over the shoulders: light blue 11 -> red 9, dark 12/7 -> 10), and her
    knee-long grey skirt (6, shade 13) with its pale hem band (7) covers rows 23-25 down to the boots, 11 pixels wide
    around the belt buckle (front) / belt (back), as wide as the legs' row 25 from the side."""
    out = f.copy()
    view = k // 3
    below = np.arange(f.shape[0])[:, None] >= 14
    out[below & (f == 11)] = 9
    out[below & np.isin(f, (12, 7))] = 10
    if view < 2:
        mark = np.nonzero(f[22] == (9 if view == 0 else 14))[0]
        c = int(round((mark.min() + mark.max()) / 2))
        L, R = c - 5, c + 5
    else:
        xs = np.nonzero(f[25])[0]
        L, R = int(xs.min()), int(xs.max())
    for y in (23, 24, 25):
        for x in range(L, R + 1):
            out[y, x] = OUTLINE if x in (L, R) else 7 if y == 25 else 13 if x == R - 1 else 6
    return out

EDITS = {'matt': matt_frame, 'shelly': shelly_frame, 'tabitha': tabitha_frame, 'courtney': courtney_frame}

def write_overworld(name, ch):
    spec = ch['overworld']
    frames, pal = ow_frames(spec)
    code = spec['code']
    table = sprites.ow_table(FILES)
    sheet, rec = sprites.ow_sheet_of(FILES, code, table)
    btx = narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS))[sheet]
    lay, pname, _ = sprites.btx_layout(btx)
    assert rec['spriteControllerType'] == 3 and len(lay) == 12 and lay[0][1] == 32, (code, rec['spriteControllerType'])
    kind_dir = kind_folder(name, 'overworld')
    folder = os.path.join(kind_dir, f'{code:03d}-{name}')
    _replace_folder(kind_dir, code, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    for i, f in enumerate(frames):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), f.tobytes(), 32, 32, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='overworld', code=code, sheet=sheet, frames=12, size=[32, 32], controller=3,
        textures=[l[0] for l in lay], palette=pname, name=name, note=ch['note'],
        source=(f'pokeruby {spec["gfx"]} (graphics/object_events/pics/people)' if 'gfx' in spec else
                f'the {spec["base"]} sheet, changed to the {name} design ({GAME[char_version(name)]} has no {name} '
                f'overworld sprite)'),
        made_by='b2tools/sprite_upgrade.py'))
    return folder

# ---------------------------------------------------------------------------------------------------- files
GAME = {'sapphire': 'Sapphire', 'ruby': 'Ruby'}

def kind_folder(name, *kind):
    """src/sprites/<kind> for Sapphire's characters, its ruby/ overlay folder for Ruby's (notes/RUBY.md "WP0 layout")."""
    d = os.path.join(SRC, *kind)
    return os.path.join(d, 'ruby') if char_version(name) == 'ruby' else d

def write_swaps():
    """The Ruby art swap (RUBY_SWAPS): src/sprites/<kind>/ruby/<code>-<name>/sprite.json = {"copy_of": <shared code>}."""
    done = []
    for kind, swaps in RUBY_SWAPS.items():
        kind_dir = os.path.join(SRC, kind, 'ruby')
        for code, (name, src) in sorted(swaps.items()):
            folder = os.path.join(kind_dir, f'{code:03d}-{name}')
            _replace_folder(kind_dir, code, folder)
            os.makedirs(folder, exist_ok=True)
            sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
                copy_of=src, name=name, note=f'Ruby: code {code} shows the art of the shared folder {src} ({name})'))
            done.append(os.path.relpath(folder, ROOT))
    return done

def _replace_folder(kind_dir, n, keep):
    """Another folder for the same number (an older name) moves to ~/.Trash, so the build never sees two."""
    if not os.path.isdir(kind_dir):
        return
    for d in os.listdir(kind_dir):
        p = os.path.join(kind_dir, d)
        if d.split('-')[0].isdigit() and int(d.split('-')[0]) == n and p != keep:
            dst = os.path.join(os.path.expanduser('~/.Trash'), f'{d}-{time.strftime("%Y%m%d-%H%M%S")}')
            shutil.move(p, dst)

# ---------------------------------------------------------------------------------------------------- previews

def rgba(a, pal):
    from PIL import Image
    lut = np.zeros((256, 4), np.uint8)
    for i in range(1, 16):
        lut[i] = (*pal[i], 255)
    return Image.fromarray(lut[a], 'RGBA')

def anim_frames(sp, parts, pal, ticks):
    """Images of the intro at the given ticks and the still loop, cropped to the union of their pixels."""
    ims = [mcss.render(sp, parts, 0, t) for t in ticks] + [mcss.render(sp, parts, 1, 0)]
    on = np.any([i != 0 for i in ims], axis=0)
    ys, xs = np.nonzero(on)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    return [rgba(i, pal).crop(box) for i in ims]

# Black 2 sprites of similar characters, shown beside the new art in the review (front sprite, object code)
REF = {'aqua-grunt-m': (149, 293), 'aqua-grunt-f': (150, 294), 'archie': (151, 353), 'matt': (149, 293),
       'shelly': (150, 294), 'magma-grunt-m': (149, 293), 'magma-grunt-f': (150, 294), 'maxie': (151, 353),
       'tabitha': (149, 293), 'courtney': (150, 294),
       'wally': (127, 231), 'sidney': (79, 94), 'phoebe': (77, 93), 'glacia': (80, 96), 'drake': (100, 229)}
REF_NAME = {149: 'Plasma grunt', 150: 'Plasma grunt', 151: 'Ghetsis', 127: 'Hugh', 79: 'Grimsley', 77: 'Shauntal',
            80: 'Caitlin', 100: 'Drayden', 293: 'Plasma grunt', 294: 'Plasma grunt', 353: 'Ghetsis', 231: 'Nate',
            94: 'Grimsley', 93: 'Shauntal', 96: 'Caitlin', 229: 'Drayden'}

def _b2_front(s):
    """Black 2's own front sprite s (the still figure), RGBA, cropped."""
    dp, _, dpal, dsp = tr_donor(s)
    img = mcss.render(dsp, dp, 1, 0); ys, xs = np.nonzero(img)
    return rgba(img[ys.min():ys.max() + 1, xs.min():xs.max() + 1], dpal)

def _b2_overworld(code, frames=(3, 4, 0, 6)):
    table = sprites.ow_table(FILES)
    sheet, _ = sprites.ow_sheet_of(FILES, code, table)
    fr, _, pal = sprites.btx_decode(narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS))[sheet])
    rgbs = [sprites.bgr555_to_rgb(c) for c in pal]
    return [rgba(np.frombuffer(bytes(fr[k][3]), np.uint8).reshape(32, 32), rgbs) for k in frames]

def review(names, path=None):
    """Sapphire (Ruby) / Black 2 reference / new for every character -> screenshots/sprites/upgrade_review.png."""
    from PIL import Image, ImageDraw
    BG, PANEL = (96, 120, 136), (112, 140, 156)
    rows = []
    for n in names:
        ch = CHARS[n]
        cells = []                                  # (label, [images], scale)
        rf, ro = REF[n]
        b = ch['battle']
        a, pal = gen3_trainer(b['pic'])
        game = GAME[char_version(n)]
        cells.append((game, [rgba(a, pal)], 2))
        cells.append((f'Black 2: {REF_NAME[rf]} ({rf})', [_b2_front(rf)], 2))
        still, parts, npal, rep, sp, off = battle_sprite(b)
        T = sp.length(0)
        fr = anim_frames(sp, parts, npal, [0, T // 3, 2 * T // 3])
        cells.append((f'new: front {b["slot"]}', [fr[-1]], 2))
        cells.append((f'intro (layout {b["layout"]})' if b.get('intro') != 'still' else 'intro: still', fr[:3], 1))
        o = ch['overworld']
        gfx = o.get('gfx') or CHARS[o['base']]['overworld']['gfx']
        g, gpal = gen3_overworld(gfx)
        cells.append((game + ('' if 'gfx' in o else ' (grunt)'), [rgba(g[k], gpal) for k in (0, 3, 1, 2)], 3))
        cells.append((f'Black 2: {REF_NAME[ro]} ({ro})', _b2_overworld(ro), 3))
        nf, npal = ow_frames(o)
        cells.append((f'new: code {o["code"]}', [rgba(nf[k], npal) for k in (3, 4, 0, 6, 7, 9)], 3))
        rows.append((ch['note'], cells))
    def cell_img(label, ims, sc):
        ims = [i.resize((i.width * sc, i.height * sc), Image.NEAREST) for i in ims if i is not None]
        w = max(sum(i.width + 4 for i in ims) + 4, 6 * len(label) + 8, 60)
        h = max([i.height for i in ims] + [40]) + 18
        c = Image.new('RGBA', (w, h), PANEL); d = ImageDraw.Draw(c)
        d.text((4, 2), label, fill=(255, 255, 255, 255)); x = 4
        for i in ims:
            c.alpha_composite(i, (x, h - i.height - 2)); x += i.width + 4
        return c
    built = [(title, [cell_img(*c) for c in cells]) for title, cells in rows]
    W = max(sum(i.width + 6 for i in imgs) for _, imgs in built) + 12
    H = sum(max(i.height for i in imgs) + 22 for _, imgs in built) + 30
    out = Image.new('RGBA', (W, H), BG); d = ImageDraw.Draw(out)
    game = 'Ruby' if all(char_version(n) == 'ruby' for n in names) else 'Sapphire'
    d.text((6, 6), f'{game}\'s characters redrawn in Black 2 style (b2tools/sprite_upgrade.py): battle (front) | '
                   f'overworld (down, step, up, left, right)  -  {game} / Black 2 reference / new', fill=(255, 255, 255, 255))
    y = 26
    for title, imgs in built:
        d.text((6, y), title, fill=(255, 240, 160, 255)); y += 14; x = 6
        for i in imgs:
            out.alpha_composite(i, (x, y)); x += i.width + 6
        y += max(i.height for i in imgs) + 8
    path = path or os.path.join(SHOTS, 'upgrade_review.png')
    out.convert('RGB').save(path)
    return path

def main(argv):
    """Default: the characters of the build's version (HOENN_VERSION, b2tools/version.py); Ruby also writes the swap
    folders and its review to upgrade_review_ruby.png. A plain (Sapphire) run is unchanged by the Ruby entries."""
    import version
    mine = [n for n in CHARS if char_version(n) == version.VERSION]
    shot = os.path.join(SHOTS, 'upgrade_review.png' if version.VERSION == 'sapphire' else
                        f'upgrade_review_{version.VERSION}.png')
    if argv[:1] == ['review']:
        print(review(argv[1:] or mine, None if argv[1:] else shot)); return
    names = argv or mine
    for n in names:
        ch = CHARS[n]
        if 'battle' in ch:
            folder, rep = write_battle(n, ch)
            print(n, 'battle ->', os.path.relpath(folder, ROOT), rep)
        if 'overworld' in ch:
            print(n, 'overworld ->', os.path.relpath(write_overworld(n, ch), ROOT))
    if version.is_ruby() and not argv:
        for f in write_swaps():
            print('swap ->', f)
    print(review(mine, shot))

if __name__ == '__main__':
    main(sys.argv[1:])
