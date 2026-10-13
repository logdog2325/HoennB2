"""Sapphire's characters as Gen 5-style edits of Black 2's own sprites (DECISIONS 2026-10-06).

    python3 sprite_art.py [recipe ...]     default: all recipes
        -> src/sprites/... (installed by patches/sprites.py) and screenshots/sprites/<recipe>.png (before/after)

Every recipe starts from the Black 2 donor sheet in the extracted ROM and repaints it: the donor's palette roles are
re-coloured region by region (head / body / feet, found per frame from the donor's own colours), and shapes are
edited where the Sapphire design differs. Frame layout, sizes, outline and shading style stay Black 2's. pokeruby's
sprites were only looked at for each character's colours and clothes; no GBA pixels are used.

Recipes:
    brendan  Nate 231-239 -> Brendan: white knit hat (Nate's hair), dark band with red edge (the visor), dark hair
             under the hat, navy top with red trim, yellow gloves, yellow pack on the back, red shoes
    may      Rosa 240-248 -> May: red bandana (Rosa's visor and the crown above it), brown hair (Rosa's buns stay
             hair; the twin tails are cut to side bunches), red top, white skirt, dark shorts/leggings, red-white shoes
    rivals   Hilbert 1/2/3/136/138/140/156/158/160 and Hilda 4/5/6/137/139/141/157/159/161 -> copies of the
             Brendan / May art (rival NPCs; same frame layouts, checked by the build patch)
    birch    Cedric Juniper 104 -> Prof. Birch: red-brown hair, beard, white lab coat open over a dark shirt, khaki
             shorts, bare shins, brown sandals
    mom      Mom 251 and Mom-with-phone 357 -> Hoenn Mom: bun removed (round top), red-brown hair, blue hair clip
             (the old hair tie), pink top, blue skirt, dark eyes
    bag      gift box 208 (one-frame object) -> Birch's bag: a brown leather satchel with handle, flap and buckle,
             redrawn on the box's footprint and outline style
    trainers battle sprites: Nate front 0 / back 0 -> Brendan (white hat, navy, yellow strap, bag and gloves; a
             yellow pack drawn on the back poses), Rosa front 1 / back 1 -> May (red bandana over the crown, brown
             buns, red top, white skirt; the front loses the long twin tails, the back keeps them: they are drawn
             over the body there, and removing them would need the back redrawn by hand)
    intro    the new-game intro's Professor Juniper (MCSS set in a/1/6/8) -> Prof. Birch
    teams, teams_battle: the earlier Team Aqua/Magma recolours of Team Plasma; superseded by b2tools/sprite_upgrade.py
             (same slots), so they only run when named and would overwrite the redrawn art
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import sprites  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

SRC = os.path.join(ROOT, 'src', 'sprites')
SHOTS = os.path.join(ROOT, 'screenshots', 'sprites')
FILES = sprites.SRC_FILES

# ---------------------------------------------------------------------------------------------------- donors

_cache = {}
def _ow_data():
    if 'ow' not in _cache:
        _cache['ow'] = (sprites.ow_table(FILES), narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS)))
    return _cache['ow']

def donor(code):
    """(frames as 2-D uint8 index arrays, 16 RGB colours, export metadata) of an overworld code in the original ROM."""
    table, sheets = _ow_data()
    sheet, rec = sprites.ow_sheet_of(FILES, code, table)
    frames, pname, pal = sprites.btx_decode(sheets[sheet])
    arrs = [np.frombuffer(bytes(px), np.uint8).reshape(h, w).copy() for _, w, h, px in frames]
    meta = dict(kind='overworld', code=code, sheet=sheet, frames=len(frames), size=[frames[0][1], frames[0][2]],
                controller=rec['spriteControllerType'], textures=[f[0] for f in frames], palette=pname)
    return arrs, [sprites.bgr555_to_rgb(c) for c in pal], meta

def folder_name(code, name): return os.path.join(SRC, 'overworld', f'{code:03d}-{name}')

def write_ow(code, name, frames, pal, note, donor_desc):
    """Write an overworld art folder for `code` (frames: index arrays; pal: {index: rgb})."""
    _, _, meta = donor(code)
    folder = folder_name(code, name)
    _clear(os.path.join(SRC, 'overworld'), code)
    os.makedirs(folder, exist_ok=True)
    rgbs = [tuple(pal[i]) for i in range(16)]
    sprites.write_pal(os.path.join(folder, 'palette.pal'), rgbs)
    w, h = meta['size']
    for i, f in enumerate(frames):
        assert f.shape == (h, w) and f.max() < 16
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), f.tobytes(), w, h, rgbs)
    sprites.write_json(os.path.join(folder, 'sprite.json'),
                       dict(meta, name=name, donor=donor_desc, note=note, made_by='b2tools/sprite_art.py'))
    return folder

def write_alias(code, name, of_code, note):
    _clear(os.path.join(SRC, 'overworld'), code)
    folder = folder_name(code, name)
    os.makedirs(folder, exist_ok=True)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(copy_of=of_code, name=name, note=note))
    return folder

def _clear(kind_dir, n):
    """Remove an older folder for the same number (another name), so the patch never sees two."""
    import shutil
    if not os.path.isdir(kind_dir):
        return
    for d in os.listdir(kind_dir):
        if d.split('-')[0].isdigit() and int(d.split('-')[0]) == n:
            shutil.rmtree(os.path.join(kind_dir, d))

def render(frames, pal, scale=3, gap=2):
    """Frames side by side as an RGBA PIL image (index 0 clear)."""
    from PIL import Image
    h, w = frames[0].shape
    lut = np.zeros((16, 4), np.uint8)
    for i in range(1, 16): lut[i] = (*pal[i], 255)
    strip = np.zeros((h, len(frames) * (w + gap) - gap, 4), np.uint8)
    for k, f in enumerate(frames):
        strip[:, k * (w + gap):k * (w + gap) + w] = lut[f]
    img = Image.fromarray(strip, 'RGBA')
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)

def save_preview(name, rows, title=None):
    """rows: [(label, PIL image)] -> screenshots/sprites/<name>.png on a mid-tone background."""
    from PIL import Image, ImageDraw
    os.makedirs(SHOTS, exist_ok=True)
    W = max(r.width for _, r in rows) + 16
    H = sum(r.height + 18 for _, r in rows) + (20 if title else 0) + 8
    img = Image.new('RGB', (W, H), (88, 112, 128)); d = ImageDraw.Draw(img); y = 6
    if title: d.text((8, y), title, fill=(255, 255, 255)); y += 20
    for label, r in rows:
        d.text((8, y), label, fill=(230, 236, 255)); y += 14
        img.paste(r, (8, y), r); y += r.height + 4
    path = os.path.join(SHOTS, f'{name}.png')
    img.save(path)
    return path

def pal_dict(rgbs): return {i: tuple(c) for i, c in enumerate(rgbs)}

# ---------------------------------------------------------------------------------------------------- helpers

def remap(f, mask, table):
    """In-place: pixels under `mask` whose index is in `table` get table[index]."""
    out = f
    src = f.copy()
    for old, new in table.items():
        out[mask & (src == old)] = new
    return out

def rows_with(f, colours, at_least=1, start=0):
    return [y for y in range(start, f.shape[0]) if np.isin(f[y], list(colours)).sum() >= at_least]

def figure_rows(f):
    ys = np.nonzero(f.any(axis=1))[0]
    return int(ys[0]), int(ys[-1])

def cut(f, out, delete):
    """Delete the pixels in `delete` (to transparent); deleted pixels that touch a kept coloured pixel become
    outline (index 0xF), so the figure stays closed."""
    h, w = f.shape
    res = out.copy(); res[delete] = 0
    kept = (~delete) & (f != 0) & (f != 0xF)
    for y, x in zip(*np.nonzero(delete)):
        for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= j < h and 0 <= i < w and kept[j, i]:
                res[y, x] = 0xF
                break
    return res

# ---------------------------------------------------------------------------------------------------- Brendan

NATE_HAIR, NATE_VISOR, NATE_JACKET = {6, 0xB, 8}, {1, 3, 4}, {2, 5, 7}
BRENDAN_PAL = {0: (115, 82, 107), 1: (140, 33, 41), 2: (33, 33, 57), 3: (230, 74, 57), 4: (181, 41, 41),
               5: (49, 57, 99), 6: (198, 206, 222), 7: (82, 99, 165), 8: (99, 107, 148), 9: (189, 140, 41),
               0xA: (214, 156, 115), 0xB: (247, 206, 74), 0xC: (255, 214, 189), 0xD: (255, 255, 255),
               0xE: (239, 239, 247), 0xF: (0, 0, 0)}
HAT = {6: 0xE, 0xB: 6, 8: 8}                 # hair above the band -> white hat, grey shade, blue-grey outline
UNDER_HAIR = {6: 5, 0xB: 2, 8: 2}            # hair below the band -> dark navy
BAND = {3: 3, 4: 5, 1: 2}                    # visor: light edge red, the rest navy
BODY = {5: 5, 7: 7, 2: 2, 0xD: 3, 0xE: 4, 9: 5, 8: 2, 6: 9, 0xB: 2, 0xC: 0xB, 0xA: 9}   # strap red, hands yellow
BACK_BODY = {**BODY, 0xD: 0xB, 0xE: 9}       # back views: the bag becomes Brendan's yellow pack
NATE_BACK_FRAMES = {231: [0, 1, 2, 12, 13, 14], 232: [0, 1, 2, 12], 233: [0], 236: [2, 3, 4], 238: [0, 1, 2, 3],
                    239: [0, 1, 2, 3]}

def brendan_frame(f, back):
    h, w = f.shape
    vrows = rows_with(f, NATE_VISOR)
    vtop = vrows[0] if vrows else 0
    jrows = rows_with(f, NATE_JACKET, 3, vtop + 1)          # first row of the jacket (the rod is thinner)
    body_top = jrows[0] if jrows else h
    vis = [y for y in vrows if y < body_top]
    vbot = vis[-1] if vis else body_top
    yy = np.mgrid[0:h, 0:w][0]
    head = yy < body_top
    out = f.copy()
    remap(out, head & (yy <= vbot), HAT)
    remap(out, head & (yy > vbot), UNDER_HAIR)
    remap(out, head, BAND)
    remap(out, ~head, BACK_BODY if back else BODY)
    return out

def brendan():
    names = {231: 'walk-run', 232: 'bike', 233: 'surf', 234: 'item', 235: 'action2', 236: 'action5',
             237: 'throw', 238: 'balance', 239: 'fishing'}
    rows = []
    for code, what in names.items():
        frames, rgbs, meta = donor(code)
        new = [brendan_frame(f, i in NATE_BACK_FRAMES.get(code, [])) for i, f in enumerate(frames)]
        write_ow(code, f'brendan-{what}', new, BRENDAN_PAL, 'Brendan (player)', f'Nate {code}')
        sc = 3 if meta['size'][0] == 32 else 2
        rows += [(f'{code} Nate {what} (Black 2)', render(frames, pal_dict(rgbs), sc)),
                 (f'{code} Brendan', render(new, BRENDAN_PAL, sc))]
    return save_preview('brendan', rows, 'Brendan, player sets (repainted from Nate 231-239)')

# ---------------------------------------------------------------------------------------------------- May

ROSA_HAIR = {1, 2, 7}
MAY_PAL = {0: (115, 198, 140), 1: (173, 115, 74), 2: (132, 82, 57), 3: (247, 206, 82), 4: (189, 140, 24),
           5: (222, 49, 57), 6: (140, 33, 41), 7: (82, 49, 41), 8: (214, 156, 115), 9: (255, 214, 189),
           0xA: (255, 255, 255), 0xB: (198, 206, 214), 0xC: (255, 107, 99), 0xD: (74, 74, 74), 0xE: (41, 41, 49),
           0xF: (0, 0, 0)}
BANDANA = {1: 0xC, 2: 5, 7: 6}               # crown and buns above the visor -> red bandana
BANDANA_FRONT = {0xB: 0xA, 0xA: 0xC, 5: 5, 6: 6, 3: 0xA, 4: 0xB}   # visor: white stripe on top, red below
MAY_BODY = {0xA: 5, 0xB: 6, 0xC: 0xE, 5: 5, 6: 6, 3: 0xA, 4: 0xB}  # white top -> red, yellow skirt -> white
MAY_FEET = {0xC: 0xB, 0xB: 0xA, 5: 5, 6: 6}
TAIL_RADIUS = 11                             # hair farther than this from the head's centre is cut

def may_frame(f):
    h, w = f.shape
    vrows = [y for y in range(h) if (f[y] == 5).sum() >= 2]
    vtop = vrows[0] if vrows else 0
    brows = rows_with(f, {0xA, 0xB, 0xC, 0xE, 6, 0xD}, 3, vtop + 3)
    body_top = brows[0] if brows else h
    _, bottom = figure_rows(f)
    yy, xx = np.mgrid[0:h, 0:w]
    head = yy < body_top
    # the bandana covers the crown above the visor, as wide as the visor; Rosa's buns beside it stay brown hair
    vis = np.isin(f, [5, 0xA, 0xB]) & (yy >= vtop) & (yy < vtop + 4)
    vx = np.nonzero(vis.any(axis=0))[0]
    x0, x1 = (vx[0] - 1, vx[-1] + 1) if len(vx) else (0, w)
    crown = (xx >= x0) & (xx <= x1)
    out = f.copy()
    remap(out, head & (yy < vtop) & crown, BANDANA)
    remap(out, head & (yy < vtop + 5) & (crown | (yy >= vtop)), BANDANA_FRONT)
    feet = ~head & (yy >= bottom - 3) & np.isin(f, list(MAY_FEET))
    remap(out, feet, MAY_FEET)
    remap(out, ~head & ~feet, MAY_BODY)
    # shorten the twin tails: hair (and its own outline) far from the head's centre
    hy, hx = np.nonzero(head & (f != 0))
    far = np.hypot(yy - hy.mean(), xx - hx.mean()) > TAIL_RADIUS
    delete = far & np.isin(f, list(ROSA_HAIR))
    for y, x in zip(*np.nonzero(far & (f == 0xF))):
        nb = f[max(0, y - 1):y + 2, max(0, x - 1):x + 2]
        if np.isin(nb, list(ROSA_HAIR | {0, 0xF})).all():
            delete[y, x] = True
    return cut(f, out, delete)

def may():
    names = {240: 'walk-run', 241: 'bike', 242: 'surf', 243: 'item', 244: 'action2', 245: 'action5',
             246: 'throw', 247: 'balance', 248: 'fishing'}
    rows = []
    for code, what in names.items():
        frames, rgbs, meta = donor(code)
        new = [may_frame(f) for f in frames]
        write_ow(code, f'may-{what}', new, MAY_PAL, 'May (player)', f'Rosa {code}')
        sc = 3 if meta['size'][0] == 32 else 2
        rows += [(f'{code} Rosa {what} (Black 2)', render(frames, pal_dict(rgbs), sc)),
                 (f'{code} May', render(new, MAY_PAL, sc))]
    return save_preview('may', rows, 'May, player sets (repainted from Rosa 240-248)')

# ---------------------------------------------------------------------------------------------------- rivals

RIVAL_COPIES = {  # Hilbert / Hilda NPC code: (player code with the same layout, name)
    1: (231, 'rival-brendan-walk-run'), 2: (232, 'rival-brendan-bike'), 3: (233, 'rival-brendan-surf'),
    136: (234, 'rival-brendan-item'), 138: (235, 'rival-brendan-action2'), 140: (236, 'rival-brendan-action5'),
    156: (237, 'rival-brendan-throw'), 158: (238, 'rival-brendan-balance'), 160: (239, 'rival-brendan-fishing'),
    4: (240, 'rival-may-walk-run'), 5: (241, 'rival-may-bike'), 6: (242, 'rival-may-surf'),
    137: (243, 'rival-may-item'), 139: (244, 'rival-may-action2'), 141: (245, 'rival-may-action5'),
    157: (246, 'rival-may-throw'), 159: (247, 'rival-may-balance'), 161: (248, 'rival-may-fishing'),
}

def rivals():
    rows = []
    for code, (src, name) in RIVAL_COPIES.items():
        frames, rgbs, meta = donor(code)
        pframes, prgbs, pmeta = donor(src)
        assert meta['textures'] == pmeta['textures'] and meta['size'] == pmeta['size'], (code, src)
        write_alias(code, name, src, f'same art as {src}')
        if code in (1, 4):
            from PIL import Image
            art = os.path.join(SRC, 'overworld', next(d for d in os.listdir(os.path.join(SRC, 'overworld'))
                                                       if d.startswith(f'{src:03d}-')))
            new = [np.array(Image.open(os.path.join(art, f'frame_{i:02d}.png'))) for i in range(pmeta['frames'])]
            newpal = pal_dict(sprites.read_pal(os.path.join(art, 'palette.pal')))
            who = 'Hilbert' if code == 1 else 'Hilda'
            rows += [(f'{code} {who} (Black 2)', render(frames, pal_dict(rgbs))),
                     (f'{code} rival {"Brendan" if code == 1 else "May"} (= {src})', render(new, newpal))]
    return save_preview('rivals', rows, 'Rival NPCs: Hilbert 1-6/136-161 and Hilda codes show the Brendan / May art '
                                        '(walk sheets shown; the other 16 sheets are copies the same way)')

# ---------------------------------------------------------------------------------------------------- Birch

CEDRIC_SHIRT = {1, 2, 3}
BIRCH_PAL = {0: (165, 165, 165), 1: (140, 148, 173), 2: (214, 222, 231), 3: (173, 148, 90), 4: (57, 49, 33),
             5: (90, 49, 33), 6: (140, 74, 49), 7: (181, 99, 57), 8: (214, 132, 82), 9: (66, 82, 74),
             0xA: (123, 74, 49), 0xB: (231, 189, 140), 0xC: (255, 231, 198), 0xD: (115, 99, 57),
             0xE: (255, 255, 255), 0xF: (0, 0, 0)}
CEDRIC_FRONT = (3, 4, 5)

def birch_frame(f, front):
    h, w = f.shape
    out = f.copy()
    trows = rows_with(f, CEDRIC_SHIRT, 2)
    t0, t1 = trows[0], trows[-1]
    yy, xx = np.mgrid[0:h, 0:w]
    torso = (yy >= t0) & (yy <= t1)
    remap(out, torso, {3: 0xE, 2: 2, 1: 1, 0xD: 9})            # yellow shirt -> white coat (buckle -> shirt)
    if front:                                                 # open coat: dark shirt down the middle
        xs = np.nonzero(np.isin(f[t0 + 2:t1 + 1], list(CEDRIC_SHIRT)).any(axis=0))[0]
        cx = (xs[0] + xs[-1]) / 2
        out[torso & (yy >= t0 + 2) & (abs(xx - cx) <= 1.5) & np.isin(f, list(CEDRIC_SHIRT))] = 9
    legs = yy > t1
    shoe_rows = [y for y in range(t1 + 1, h) if (f[y] == 6).any()]
    shin = (shoe_rows[0] - 1) if shoe_rows else h
    remap(out, legs & (yy < shin), {5: 3, 4: 0xD})             # trousers -> khaki shorts
    remap(out, legs & (yy == shin), {4: 0xB, 5: 0xB})          # bare shins
    face = [y for y in range(t0) if np.isin(f[y], [0xB, 0xC]).any()]
    if face:                                                  # beard along the jaw and chin
        last = face[-1]
        remap(out, (yy < t0) & (yy >= last - 2), {0xB: 6, 0xA: 5})
        remap(out, (yy < t0) & (yy == last), {0xC: 7})
    return out

def birch():
    frames, rgbs, meta = donor(104)
    new = [birch_frame(f, i in CEDRIC_FRONT) for i, f in enumerate(frames)]
    for a, b in ((9, 6), (10, 7), (11, 8)):                  # the right-facing frames stay mirrors of the left
        assert (frames[a] == frames[b][:, ::-1]).all()
        new[a] = new[b][:, ::-1].copy()
    write_ow(104, 'prof-birch', new, BIRCH_PAL, 'Prof. Birch (NPC)', 'Cedric Juniper 104')
    return save_preview('birch', [('104 Cedric Juniper (Black 2)', render(frames, pal_dict(rgbs), 4)),
                                  ('104 Prof. Birch', render(new, BIRCH_PAL, 4))],
                        'Prof. Birch (repainted from Cedric Juniper 104)')

# ---------------------------------------------------------------------------------------------------- Mom

MOM_COLOURS = {1: (148, 49, 90), 2: (165, 99, 90), 3: (123, 165, 222), 4: (231, 115, 156), 5: (57, 82, 156),
               6: (66, 33, 24), 7: (115, 57, 41), 8: (165, 90, 57), 9: (206, 132, 90), 0xE: (239, 214, 222)}

def mom_frame(f):
    """Black 2's Mom has a bun tied with a pink band on top; Sapphire's Mom has none: cut everything above the band
    and close the head with a rounded two-row cap. Her pink eyes (index 3, now blue) become dark brown."""
    out = f.copy()
    h, w = f.shape
    tie = [y for y in range(16) if (f[y] == 3).sum() >= 2]
    if tie:
        t = tie[0]
        out[:t + 1] = 0
        r = t + 1
        xs = np.nonzero(out[r])[0]
        x0, x1 = xs[0], xs[-1]
        out[r, x0] = out[r, x1] = 0xF
        out[r - 1, x0 + 1:x1] = 8
        out[r - 1, x0 + 1] = out[r - 1, x1 - 1] = 0xF
        out[r - 1, x0 + 2] = out[r - 1, x1 - 2] = 7
        out[r - 2, x0 + 2:x1 - 1] = 0xF
    yy = np.mgrid[0:h, 0:w][0]
    face = [y for y in range(20) if (f[y] == 0xC).any()]
    if face:
        remap(out, (yy >= face[0]) & (yy <= face[-1]) & (f == 3), {3: 6})
    return out

def mom():
    rows = []
    for code, name in ((251, 'hoenn-mom'), (357, 'hoenn-mom-phone')):
        frames, rgbs, meta = donor(code)
        pal = {**pal_dict(rgbs), **MOM_COLOURS}
        new = [mom_frame(f) for f in frames]
        write_ow(code, name, new, pal, 'Mom (Hoenn)', f'Mom {code}')
        rows += [(f'{code} Mom (Black 2)', render(frames, pal_dict(rgbs), 4)), (f'{code} Hoenn Mom', render(new, pal, 4))]
    return save_preview('mom', rows, 'Hoenn Mom (repainted from Mom 251 and 357)')

# ---------------------------------------------------------------------------------------------------- Birch's bag

BAG_DONOR = 208   # gift box: a one-frame, 32x32 object (controller 4) with a box footprint
BAG_ART = [       # . clear, f outline, b/d/e/c/a leather light -> dark, 8/9 strap, 7/6 brass buckle
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...........ffffffffff...........",
    "..........f8888888888f..........",
    ".........f89ffffffff98f.........",
    ".........f8f........f8f.........",
    ".........f8f........f8f.........",
    "......fffff8ffffffffff8ffff.....",
    "......fbbdddddddddddddddddef....",
    "......fbddddddddddddddddddef....",
    "......fdddddddddddddddddddcf....",
    "......feeeeeeeeeeeeeeeeeeecf....",
    ".......feeeeeeee98eeeeeeecf.....",
    ".......fceeeeeee98eeeeeeccf.....",
    "........fccccccc98ccccccff......",
    ".......fffffffff7766ffffff......",
    "......fdeccccccc7766cccccaf.....",
    "......fdcccccccccccccccccaf.....",
    "......fecccccccccccccccccaf.....",
    "......fecccccccccccccccccaf.....",
    "......fecccccccccccccccccaf.....",
    "......fecccccccccccccccccaf.....",
    "......fccaaaaaaaaaaaaaaaaaf.....",
    ".......faaaaaaaaaaaaaaaaaf......",
    "........ffffffffffffffffff......",
    "................................",
]
BAG_COLOURS = {6: (181, 132, 41), 7: (239, 198, 82), 8: (132, 82, 49), 9: (90, 57, 33), 0xA: (115, 66, 41),
               0xB: (247, 206, 148), 0xC: (165, 99, 57), 0xD: (222, 156, 99), 0xE: (189, 123, 74),
               0xF: (57, 33, 24)}

def bag():
    frames, rgbs, meta = donor(BAG_DONOR)
    rows = [r.ljust(32, '.')[:32] for r in BAG_ART]
    art = np.array([[0 if ch == '.' else int(ch, 16) for ch in r] for r in rows], np.uint8)
    assert art.shape == frames[0].shape
    # same ground line as the box (its lowest row), so it stands where the box stood
    assert figure_rows(art)[1] == figure_rows(frames[0])[1]
    pal = {**pal_dict(rgbs), **BAG_COLOURS}
    write_ow(BAG_DONOR, 'birchs-bag', [art], pal, "Birch's bag (one-frame object)", 'gift box 208')
    return save_preview('birch_bag', [('208 gift box (Black 2)', render(frames, pal_dict(rgbs), 6)),
                                      ("208 Birch's bag", render([art], pal, 6))], "Birch's bag (on gift box 208)")

# ---------------------------------------------------------------------------------------------------- battle sprites

def tr_donor(side, s):
    """(parts 128x256, static 80x80, 16 RGB colours, cells, metadata) of a trainer sprite in the original ROM."""
    key = ('tr', side)
    if key not in _cache:
        _cache[key] = narc_entries(arc_path(FILES, sprites.ARC_TR[side]))
    ents = _cache[key]
    _, pal = sprites.nclr_colors(ents[8 * s + sprites.TR_PALETTE])
    _, _, parts = sprites.tr_decode_image(ents[8 * s + sprites.TR_PARTS], 'parts')
    _, _, static = sprites.tr_decode_image(ents[8 * s + sprites.TR_STATIC], 'static')
    cells = sprites.ncer_cells(ents[8 * s + 2])
    meta = dict(kind='trainer', side=side, sprite=s, archive=sprites.ARC_TR[side],
                files={'static': 8 * s, 'parts': 8 * s + 1, 'palette': 8 * s + 7})
    return (np.frombuffer(parts, np.uint8).reshape(128, 256).copy(),
            np.frombuffer(static, np.uint8).reshape(80, 80).copy(),
            [sprites.bgr555_to_rgb(c) for c in pal], cells, meta)

def write_tr(side, s, name, parts, static, pal, note, donor_desc, mcss_from=None):
    """Write a trainer art folder for slot `s`; `mcss_from` = the sprite whose parts layout the art uses (its MCSS
    files get copied into slot `s` by the build patch)."""
    *_, meta = tr_donor(side, s if mcss_from is None else mcss_from)
    meta = dict(meta, sprite=s, files=sprites.tr_files(s))
    if mcss_from is not None and mcss_from != s:
        meta['mcss_from'] = mcss_from
    kind_dir = os.path.join(SRC, 'trainer', side)
    _clear(kind_dir, s)
    folder = os.path.join(kind_dir, f'{s:03d}-{name}')
    os.makedirs(folder, exist_ok=True)
    rgbs = [tuple(pal[i]) for i in range(16)]
    sprites.write_pal(os.path.join(folder, 'palette.pal'), rgbs)
    sprites.write_png(os.path.join(folder, 'parts.png'), parts.tobytes(), 256, 128, rgbs)
    sprites.write_png(os.path.join(folder, 'static.png'), static.tobytes(), 80, 80, rgbs)
    sprites.write_json(os.path.join(folder, 'sprite.json'),
                       dict(meta, name=name, donor=donor_desc, note=note, made_by='b2tools/sprite_art.py'))
    return folder

def cell_box(cell):
    return (min(o[4] for o in cell), min(o[5] for o in cell),
            max(o[4] + o[2] for o in cell), max(o[5] + o[3] for o in cell))

def figure_offset(parts, static, cells):
    """(dx, dy) with parts[y + dy, x + dx] == static[y, x] over the whole-figure cell, or None when the still
    picture is empty or differs from the whole figure."""
    if not static.any():
        return None
    x0, y0, x1, y1 = cell_box(cells[sprites.whole_figure_cell(cells)])
    fig = parts[y0:y1, x0:x1]
    fy, fx = np.nonzero(fig); sy, sx = np.nonzero(static)
    ox, oy = sx.min() - fx.min(), sy.min() - fy.min()       # where the figure's top-left lands in the still
    canvas = np.zeros((80, 80), np.uint8)
    for j, i in zip(fy, fx):
        if not (0 <= oy + j < 80 and 0 <= ox + i < 80):
            return None
        canvas[oy + j, ox + i] = fig[j, i]
    return (x0 - ox, y0 - oy) if (canvas == static).all() else None

def box_mask(shape, boxes, dx=0, dy=0):
    m = np.zeros(shape, bool)
    for x0, y0, x1, y1 in boxes:
        m[max(0, y0 + dy):max(0, y1 + dy), max(0, x0 + dx):max(0, x1 + dx)] = True
    return m

def head_split(img, head, hair, band):
    """Hair pixels inside `head`: (above the band = hat, below = under-hair). Per column, a band pixel below means
    hat and one above means under-hair; columns without band pixels follow the nearest band pixel."""
    h, w = img.shape
    hairm = head & np.isin(img, list(hair)); bandm = head & np.isin(img, list(band))
    hat = np.zeros_like(hairm); under = np.zeros_like(hairm)
    by, bx = np.nonzero(bandm)
    for y, x in zip(*np.nonzero(hairm)):
        col = by[bx == x]
        below = col[(col > y) & (col - y <= 28)]; above = col[(col < y) & (y - col <= 28)]
        if len(below) and (not len(above) or below.min() - y <= y - above.max()):
            hat[y, x] = True
        elif len(above):
            under[y, x] = True
        elif len(by):
            k = np.argmin((by - y) ** 2 + (bx - x) ** 2)
            (hat if y < by[k] else under)[y, x] = True
        else:
            hat[y, x] = True
    return hat, under

def tr_repaint(img, regions, maps, hair, band, hat_depth=None):
    """regions: {name: mask}, in priority order (a pixel belongs to the first region that has it). maps: {region
    name: {old: new}} on the original indices; the region 'head' is split into 'hat' (hair above the band) and
    'under' (hair below it) plus its own map for the rest. Pixels in no region use maps['body']."""
    out = img.copy()
    used = np.zeros(img.shape, bool)
    for name, mask in regions.items():
        m = mask & ~used
        if name == 'head':
            hat, under = head_split(img, m, hair, band)
            if hat_depth is not None:              # only the band of hair just above the band: the rest stays hair
                bandm = np.isin(img, list(band)) & m
                for y, x in zip(*np.nonzero(hat)):
                    below = np.nonzero(bandm[y:, x])[0]
                    if not len(below) or below[0] > hat_depth:
                        hat[y, x] = False
            for sub, sm in (('hat', hat), ('under', under)):
                for o, n in maps[sub].items(): out[sm & (img == o)] = n
            m = m & ~hat & ~under
        for o, n in maps.get(name, {}).items(): out[m & (img == o)] = n
        used |= mask
    for o, n in maps['body'].items(): out[~used & (img == o)] = n
    return out

def cut_far(img, out, centres, radius, hair, outline=None):
    """Delete hair (and its own outline) farther than `radius` from every centre, closing the cut with outline."""
    h, w = img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    far = np.ones(img.shape, bool)
    for cx, cy in centres:
        far &= np.hypot(yy - cy, xx - cx) > radius
    delete = far & np.isin(img, list(hair))
    if outline is not None:
        for y, x in zip(*np.nonzero(far & np.isin(img, list(outline)))):
            nb = img[max(0, y - 1):y + 2, max(0, x - 1):x + 2]
            if np.isin(nb, list(set(hair) | set(outline) | {0})).all():
                delete[y, x] = True
    res = out.copy(); res[delete] = 0
    ol = min(outline) if outline else 0xF
    kept = ~delete & (img != 0) & ~np.isin(img, list(outline or ()))
    for y, x in zip(*np.nonzero(delete)):
        for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= j < h and 0 <= i < w and kept[j, i]:
                res[y, x] = ol
                break
    return res

def tr_render(parts, static, pal, cells, scale=2):
    """Preview row: still figure (if any), whole figure from the parts, the parts sheet."""
    from PIL import Image
    lut = np.zeros((16, 4), np.uint8)
    for i in range(1, 16): lut[i] = (*pal[i], 255)
    P = Image.fromarray(lut[parts], 'RGBA'); S = Image.fromarray(lut[static], 'RGBA')
    fig = sprites.render_cell(P, cells[sprites.whole_figure_cell(cells)])[0]
    ims = ([S] if static.any() else []) + [fig, P]
    W = sum(i.width for i in ims) + 6 * len(ims); H = max(i.height for i in ims)
    row = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = 0
    for i in ims: row.alpha_composite(i, (x, H - i.height)); x += i.width + 6
    return row.resize((row.width * scale, row.height * scale), Image.NEAREST)

def tr_recipe(side, s, name, spec):
    parts, static, rgbs, cells, meta = tr_donor(side, s)
    pal = {**pal_dict(rgbs), **spec['colours']}
    regions_p = {}
    for region, ids in spec.get('cells', {}).items():
        m = np.zeros(parts.shape, bool)
        for ci in ids:
            for x, y, w, h, tx, ty, hf, vf in cells[ci]:
                m[ty:ty + h, tx:tx + w] = True
        regions_p[region] = m
    for region, boxes in spec.get('parts_boxes', {}).items():
        regions_p[region] = regions_p.get(region, np.zeros(parts.shape, bool)) | box_mask(parts.shape, boxes)
    off = figure_offset(parts, static, cells)
    regions_s = {}
    for region, boxes in spec.get('static_boxes', {}).items():
        regions_s[region] = box_mask(static.shape, boxes)
        if off:                                   # the whole figure in the parts sheet is the same picture
            regions_p[region] = regions_p.get(region, np.zeros(parts.shape, bool)) | \
                box_mask(parts.shape, boxes, *off) & box_mask(parts.shape, [cell_box(cells[sprites.whole_figure_cell(cells)])])
    order = spec.get('order')
    if order:
        regions_p = {k: regions_p[k] for k in order if k in regions_p}
        regions_s = {k: regions_s[k] for k in order if k in regions_s}
    new_parts = tr_repaint(parts, regions_p, spec['maps'], spec['hair'], spec['band'], spec.get('hat_depth'))
    new_static = tr_repaint(static, regions_s, spec['maps'], spec['hair'], spec['band'], spec.get('hat_depth'))
    if 'cut' in spec:                               # hair cut short: drop strands far from the head
        c = spec['cut']
        new_static = cut_far(static, new_static, [c['centre']], c['radius'], c['hair'], c.get('outline'))
        if off:
            fig = box_mask(parts.shape, [cell_box(cells[sprites.whole_figure_cell(cells)])])
            cutp = cut_far(parts, new_parts, [(c['centre'][0] + off[0], c['centre'][1] + off[1])], c['radius'],
                           c['hair'], c.get('outline'))
            new_parts[fig] = cutp[fig]
        strands = set(c['hair']) | set(c.get('outline', ()))
        for ci in c.get('cells', []):               # loose strands drawn as their own parts: removed
            for x, y, w, h, tx, ty, hf, vf in cells[ci]:
                box = new_parts[ty:ty + h, tx:tx + w]
                box[np.isin(parts[ty:ty + h, tx:tx + w], list(strands))] = 0
    if 'edit' in spec:
        new_parts, new_static = spec['edit'](new_parts, new_static, off)
    write_tr(side, s, name, new_parts, new_static, pal, spec['note'], spec['donor'])
    return [(f'{side} {s} {spec["donor"]} (Black 2)', tr_render(parts, static, pal_dict(rgbs), cells)),
            (f'{side} {s} {spec["note"]}', tr_render(new_parts, new_static, pal, cells))]

def draw_pack(img, box, inside, straps=(), ol=1, fill=5, light=7, dark=0xE, metal=4):
    """Brendan's yellow pack: rounded box with outline, gold fill, yellow light upper left, brown shade lower right,
    a flap seam with a small buckle, and shoulder straps; drawn only where the figure already has pixels."""
    x0, y0, x1, y1 = box
    def put(x, y, v):
        if inside[y, x]: img[y, x] = v
    for sx, sy, ex, ey in straps:                      # straps first, the pack covers their lower ends
        n = max(abs(ex - sx), abs(ey - sy))
        for k in range(n + 1):
            x = round(sx + (ex - sx) * k / n); y = round(sy + (ey - sy) * k / n)
            put(x, y, fill); put(x + 1, y, light); put(x - 1, y, ol); put(x + 2, y, ol)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = min(x - x0, x1 - x); dy = min(y - y0, y1 - y)
            if dx + dy < 2:                            # rounded corners
                continue
            if dx == 0 or dy == 0 or dx + dy == 2:
                v = ol
            elif y == y0 + 6:
                v = dark
            elif dx <= 2 and x - x0 <= 2 or y - y0 <= 2 or y == y0 + 7:
                v = light
            elif x1 - x <= 2 or y1 - y <= 2:
                v = dark
            else:
                v = fill
            put(x, y, v)
    cx = (x0 + x1) // 2
    for x in (cx, cx + 1):
        for y in (y0 + 6, y0 + 7):
            put(x, y, metal)
    put(cx, y0 + 8, ol); put(cx + 1, y0 + 8, ol)
    return img

def brendan_back_edit(parts, static, off):
    inside = parts != 0
    draw_pack(parts, (64, 61, 84, 82), inside, straps=[(66, 62, 62, 55), (81, 62, 86, 54)])   # pose 1, upper back
    draw_pack(parts, (151, 72, 173, 91), inside, straps=[(153, 73, 147, 67), (170, 73, 176, 68)])  # pose 2
    return parts, static

TR_SPECS = {
    ('front', 1): ('may', dict(
        donor='Rosa front 1', note='May (rival battles; player front)',
        hair={2, 3, 7}, band={5},
        colours={4: (148, 33, 49), 5: (222, 57, 57), 6: (247, 214, 90), 0xE: (247, 115, 99)},
        maps={'hat': {3: 5, 7: 0xE, 2: 4}, 'under': {}, 'buns': {},
              'bag': {5: 6, 4: 7, 0xE: 5, 0xF: 0xE}, 'shoes': {0xE: 5},
              'body': {0xF: 0xE, 0xE: 5, 6: 0xF}},
        cells={'buns': [0, 2], 'head': [5, 29, 4], 'bag': [10], 'shoes': [18, 14, 28]},
        static_boxes={'buns': [(30, 11, 39, 22), (46, 11, 56, 21)], 'head': [(26, 8, 58, 32)],
                      'bag': [(48, 37, 60, 50)], 'shoes': [(26, 66, 64, 80)]},
        order=['buns', 'head', 'bag', 'shoes'],     # Rosa's buns stay brown hair
        cut=dict(centre=(42, 21), radius=13, hair={2, 3, 7}, outline={1, 0xB}, cells=[3, 20, 1]))),
    ('back', 1): ('may', dict(
        donor='Rosa back 1', note='May (player back)',
        hair={0xB, 0xC}, band={3, 4},
        colours={3: (222, 57, 57), 4: (148, 33, 49), 6: (247, 115, 99)},
        maps={'hat': {0xB: 3, 0xC: 4}, 'under': {}, 'keep': {}, 'body': {2: 6, 6: 3, 5: 4, 7: 2}}, hat_depth=5,
        parts_boxes={'keep': [(86, 12, 100, 22), (226, 8, 246, 22), (212, 80, 226, 92)],
                     'head': [(0, 22, 48, 60), (60, 22, 104, 62), (152, 34, 196, 72)]},
        order=['keep', 'head'])),
    ('front', 0): ('brendan', dict(
        donor='Nate front 0', note='Brendan (rival battles; player front)',
        hair={7, 8, 0xE}, band={2},
        colours={1: (239, 239, 247), 3: (222, 82, 57), 4: (57, 66, 115), 5: (41, 44, 82), 6: (24, 27, 49),
                 7: (247, 206, 74), 8: (189, 140, 49), 0xC: (181, 185, 206), 0xD: (132, 99, 41)},
        maps={'hat': {8: 1, 7: 0xB, 0xE: 0xC}, 'under': {7: 6, 8: 0xE},
              'pants': {1: 4, 0xC: 5, 0xD: 6, 0xB: 4},
              'yellow': {1: 7, 0xC: 8, 0xB: 7},
              'body': {1: 7, 0xC: 8}},
        cells={'head': [1, 17, 27], 'pants': [25, 23, 11, 14], 'yellow': [7, 8, 9, 10, 32, 35, 18]},
        static_boxes={'head': [(0, 0, 80, 29)], 'pants': [(22, 44, 49, 64)], 'yellow': [(28, 29, 50, 47), (46, 32, 62, 62)]})),
    ('back', 0): ('brendan', dict(
        donor='Nate back 0', note='Brendan (player back)',
        hair={0xE, 0xF, 6}, band={0xD},
        colours={3: (247, 247, 255), 4: (198, 202, 218), 5: (181, 132, 41), 7: (247, 206, 74), 8: (57, 66, 115),
                 9: (41, 44, 82), 0xA: (24, 27, 49)},
        maps={'hat': {0xE: 2, 0xF: 3, 6: 4}, 'under': {0xE: 9, 0xF: 0xA, 6: 0xA}, 'head': {5: 4, 7: 8},
              'pants': {3: 8, 4: 9, 5: 0xA, 0xE: 9, 0xF: 0xA, 7: 8}, 'strap': {2: 7, 3: 7, 4: 5, 5: 5, 7: 8},
              'body': {5: 4, 7: 8}},
        parts_boxes={'head': [(0, 8, 48, 58), (48, 8, 98, 60), (136, 22, 192, 68)],
                     'pants': [(0, 98, 48, 128), (48, 94, 112, 128), (112, 90, 200, 128)],
                     'strap': [(20, 54, 42, 86)]},
        order=['head', 'pants', 'strap'],
        edit=brendan_back_edit)),
}

def trainers():
    rows = []
    for (side, s), (name, spec) in TR_SPECS.items():
        rows += tr_recipe(side, s, name, spec)
    return save_preview('trainers', rows, 'Battle sprites (front a/0/7/1, back a/0/7/2): Black 2 donor above, edit below')

# ---------------------------------------------------------------------------------------------------- intro Birch

INTRO_ARC, INTRO_PARTS, INTRO_PAL, INTRO_CELLS = 168, 25, 28, 27   # sProfessorLoadInfo (ov294 intro_cmd.c)
INTRO_COLOURS = {1: (181, 156, 99), 2: (132, 107, 66), 3: (198, 115, 74), 4: (148, 82, 49), 5: (247, 247, 255),
                 6: (214, 218, 230), 7: (156, 165, 189), 9: (66, 74, 74), 0xD: (99, 57, 41)}
SKIN = (0xA, 0xB, 0xC)

def beard(out, src, box, rows_full=4, rows_side=7, side=3):
    """Skin in the lowest `rows_full` rows of the face in `box`, and at its sides `rows_side` up, becomes beard."""
    x0, y0, x1, y1 = box
    sub = src[y0:y1, x0:x1]
    ys, xs = np.nonzero(np.isin(sub, SKIN))
    if not len(ys):
        return
    bottom = ys.max(); sel = ys >= bottom - rows_side
    fx0, fx1 = xs[sel].min(), xs[sel].max()
    for y, x in zip(ys, xs):
        if y >= bottom - rows_full or (y >= bottom - rows_side and (x <= fx0 + side or x >= fx1 - side)):
            out[y0 + y, x0 + x] = {0xA: 4, 0xB: 4, 0xC: 0xD}[sub[y, x]]

def intro():
    """Professor Juniper in the new-game intro (MCSS set in a/1/6/8) -> Prof. Birch: red-brown hair without the top
    tuft, beard (jaw, chin, the old earrings), dark eyes, white coat, dark shirt, khaki shorts (the skirt), brown
    sandals. Her build stays (the parts and cells are fixed; a male donor would mean a different MCSS set, which
    does not fit the archive's size and may lack the intro's animations). The mouth
    strips get the beard too, so talking keeps it. Texture pixels that no cell draws (a leftover third mouth strip)
    are cleared, which keeps the recompressed picture within the file's original size (keep_size)."""
    ents = narc_entries(arc_path(FILES, INTRO_ARC))
    _, pal = sprites.nclr_colors(ents[INTRO_PAL])
    rgbs = [sprites.bgr555_to_rgb(c) for c in pal]
    _, _, raw = sprites.tr_decode_image(ents[INTRO_PARTS], 'parts')
    a = np.frombuffer(raw, np.uint8).reshape(128, 256).copy()
    cells = sprites.ncer_cells(ents[INTRO_CELLS])
    def cellmask(ids):
        m = np.zeros(a.shape, bool)
        for ci in ids:
            for x, y, w, h, tx, ty, hf, vf in cells[ci]: m[ty:ty + h, tx:tx + w] = True
        return m
    out = a.copy()
    heads = [(192, 0, 224, 32), (224, 0, 256, 32), (0, 0, 64, 30)]
    mouths = [(96, 56, 128, 64), (96, 64, 128, 72)]
    head = box_mask(a.shape, heads + mouths + [(80, 56, 96, 72)])
    remap(out, head, {1: 0xD, 2: 0xF, 8: 4, 9: 0xD})        # eyes dark, earrings -> beard sides, lips dark
    out_src = a                                              # beard decisions on the original pixels
    for b in heads + mouths:
        beard(out, out_src, b)
    remap(out, cellmask([6, 7, 8]), {0xE: 9, 8: 4, 9: 0xD})    # torso: white top -> dark shirt
    beard(out, out_src, (140, 44, 172, 50), rows_full=3, rows_side=5, side=2)   # the chin drawn on the torso
    remap(out, cellmask([29, 30]), {5: 4, 6: 3, 7: 0xD, 0xE: 3, 8: 0xD, 9: 0xD})  # sneakers -> sandals
    remap(out, cellmask([19, 20, 21, 22, 25]), {9: 8})       # Poké Balls keep their red (9 is the shirt now)
    for x0, y0, x1, y1 in heads:                             # shorter hair: the tuft on top of the head goes
        sub = out[y0:y1, x0:x1]
        ys, xs = np.nonzero(sub)
        top, left = ys.min(), xs[ys <= ys.min() + 3].min()
        tuft = np.zeros(sub.shape, bool)
        tuft[top:top + 7, left:left + 4] = True
        tuft &= sub != 0
        sub[tuft] = 0
        for y, x in zip(*np.nonzero(tuft)):                  # close the new edge with outline
            if x + 1 < sub.shape[1] and sub[y, x + 1] not in (0, 0xF):
                sub[y, x + 1] = 0xF
    out[~cellmask(range(len(cells)))] = 0                    # pixels no cell draws
    newpal = {**pal_dict(rgbs), **INTRO_COLOURS}
    folder = os.path.join(SRC, 'mcss', 'intro-professor-birch')
    os.makedirs(folder, exist_ok=True)
    rg = [tuple(newpal[i]) for i in range(16)]
    sprites.write_pal(os.path.join(folder, 'palette.pal'), rg)
    sprites.write_png(os.path.join(folder, 'parts.png'), out.tobytes(), 256, 128, rg)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='mcss', archive=INTRO_ARC, files={'parts': INTRO_PARTS, 'palette': INTRO_PAL}, keep_size=True,
        name='intro-professor-birch', donor='Professor Juniper, intro (a/1/6/8 files 24-30)',
        note='Prof. Birch in the new-game intro', made_by='b2tools/sprite_art.py'))
    new = sprites.tr_encode_image(ents[INTRO_PARTS], 'parts', out.tobytes())
    assert len(new) <= len(ents[INTRO_PARTS]), (len(new), len(ents[INTRO_PARTS]))
    static0 = np.zeros((80, 80), np.uint8)
    return save_preview('intro_birch', [
        ('intro professor (Black 2: Juniper)', tr_render(a, static0, pal_dict(rgbs), cells, 3)),
        (f'Prof. Birch (parts recompress to {len(new)} of {len(ents[INTRO_PARTS])} bytes)',
         tr_render(out, static0, newpal, cells, 3))], 'New-game intro professor (a/1/6/8, MCSS)')

# ---------------------------------------------------------------------------------------------------- Team Aqua / Magma

# Overworld: Neo Team Plasma grunts 293 (M) and 294 (F) are the donors for every member (Sapphire uses the grunt
# sheets for the admins too). Black 2 codes that are Plasma / Unova-only take the results:
#   Aqua grunt M -> 293 (itself), Aqua grunt F -> 294 (itself), Magma grunt M -> 302 (Zinzolin),
#   Magma grunt F -> 192 (robed elder, Undella only), Archie -> 353 (Ghetsis, Giant Chasm), Maxie -> 303 (Pokestar
#   Studios actor). All six are 12-frame (controller 3) sheets with the same layout as the donors (checked).
PLASMA_GREYS, PLASMA_SKIN, PLASMA_HAIR = {1, 2, 3, 4, 5}, {0xB, 0xC, 0xD}, {7, 8, 9, 0xA}
GREY_RAMP = {1: (33, 33, 41), 2: (74, 74, 82), 3: (123, 123, 132), 4: (181, 181, 189), 5: (231, 231, 239)}

def flood(mask, seeds):
    out = np.zeros_like(mask); stack = list(seeds)
    H, W = mask.shape
    while stack:
        y, x = stack.pop()
        if 0 <= y < H and 0 <= x < W and mask[y, x] and not out[y, x]:
            out[y, x] = True; stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    return out

def plasma_regions(f):
    """Per frame of a Neo Plasma grunt sheet: cap (the grey beret, flood-filled from the top), hair (the orange
    hair under it), mask (the grey face mask next to the skin), torso / legs / shoes rows below the face."""
    H, W = f.shape
    yy, xx = np.mgrid[0:H, 0:W]
    s0 = rows_with(f, PLASMA_SKIN)[0]
    greys = np.isin(f, list(PLASMA_GREYS))
    top = figure_rows(f)[0]
    cap = flood(greys & (yy < s0 + 3), [(top, x) for x in range(W) if greys[top, x]])
    skin = np.isin(f, list(PLASMA_SKIN))
    near = np.zeros_like(skin)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            near |= np.roll(np.roll(skin, dy, 0), dx, 1)
    mask = greys & ~cap & near & (yy >= s0) & (yy < s0 + 8) & (f != 1)
    hair = np.isin(f, list(PLASMA_HAIR)) & (yy < s0 + 8)
    body_top, legs_top = s0 + 7, s0 + 13
    bottom = figure_rows(f)[1]
    body = (yy >= body_top) & ~mask
    return dict(cap=cap, hair=hair, mask=mask, torso=body & (yy < legs_top), legs=body & (yy >= legs_top) & (yy < bottom - 2),
                shoes=body & (yy >= bottom - 2), body_top=body_top, legs_top=legs_top, xx=xx, yy=yy)

def team_frame(f, spec, i):
    r = plasma_regions(f); out = f.copy()
    W = f.shape[1]; cx = (W - 1) / 2; xx, yy = r['xx'], r['yy']
    def app(mask, table):
        for o, n in table.items(): out[mask & (f == o)] = n
    M = spec['maps']
    for name in ('cap', 'hair', 'mask'):
        app(r[name], M.get(name, {}))
    middle = abs(xx - cx) <= 6                        # legs and shoes; the gloved hands at the sides stay black
    app(r['legs'] & middle, M.get('legs', {})); app(r['shoes'] & middle, M.get('shoes', {}))
    t = r['torso']; core = t & (abs(xx - cx) <= spec.get('half', 5))
    if 'stripes' in spec:                             # Aqua's black-and-white striped shirt, 2-row stripes
        white = core & np.isin((yy - r['body_top']) % 4, [1, 2])
        app(white, spec['stripes']['white']); app(core & ~white, spec['stripes']['black'])
    elif 'torso_upper' in spec:                       # Maxie: dark top above, red below
        mid = r['body_top'] + spec['split']
        app(core & (yy < mid), spec['torso_upper']); app(core & (yy >= mid), M.get('torso', {}))
    else:
        app(core, M.get('torso', {}))
    app(t & ~core, M.get('arms', {}))
    if spec.get('midriff'):                           # Aqua grunt F's crop top
        app(core & (yy == r['legs_top'] - 1) & (abs(xx - cx) <= 3), {1: 0xC, 2: 0xC, 3: 0xD, 4: 0xD, 5: 0xD, 6: 0xD})
    if spec.get('glasses') is not None:               # Maxie: the eye whites become lenses
        face = (yy >= rows_with(f, PLASMA_SKIN)[0]) & (yy < r['body_top'])
        out[face & (f == 0xE)] = spec['glasses']
    if spec.get('horns'):                             # Magma's hood: two small black horns on top
        H = f.shape[0]
        top = figure_rows(out)[0]
        xs = np.nonzero(out[top + 2])[0]; x0, x1 = xs[0], xs[-1]
        side = 6 <= i % 12 <= 11
        spots = ([x1 - 3] if i % 12 >= 9 else [x0 + 3]) if side else [x0 + 2, x1 - 2]
        for x in spots:
            for dy, dx, v in ((-1, 0, 1), (-2, 0, 1), (-1, 1, 1), (-2, 1, 0xF), (-3, 0, 0xF), (-1, -1, 0xF),
                              (-2, -1, 0xF), (-1, 2, 0xF), (0, 0, 1), (0, 1, 1)):
                y_, x_ = top + 1 + dy, x + dx
                if 0 <= y_ < H and 0 <= x_ < W and (out[y_, x_] == 0 or v != 0xF):
                    out[y_, x_] = v
    return out

TEAM_OW = {  # name: (donor code, target code, note, spec)
    'aqua-grunt-m': (293, 293, 'Team Aqua grunt (M)', dict(
        pal={**GREY_RAMP, 6: (66, 115, 198), 7: (41, 66, 140), 8: (66, 99, 173), 9: (41, 57, 115), 0xA: (115, 156, 222)},
        maps=dict(cap={2: 6, 1: 7, 5: 0xE}, hair={7: 1, 8: 2, 9: 2, 0xA: 3}, mask={2: 0xC, 3: 0xC, 4: 0xD, 5: 0xD},
                  legs={1: 9, 2: 9, 3: 8, 4: 0xA, 6: 8}, arms={6: 2}),
        stripes=dict(white={1: 3, 2: 4, 3: 5, 4: 5, 6: 5}, black={6: 1, 3: 2, 4: 3}))),
    'aqua-grunt-f': (294, 294, 'Team Aqua grunt (F)', dict(
        pal={**GREY_RAMP, 3: (148, 41, 74), 6: (66, 115, 198), 7: (41, 66, 140), 8: (66, 99, 173), 9: (41, 57, 115),
             0xA: (214, 82, 115)},
        maps=dict(cap={2: 6, 1: 7, 5: 0xE, 3: 4, 4: 4}, hair={7: 3, 8: 3, 9: 0xA, 0xA: 0xA},
                  mask={2: 0xC, 3: 0xC, 4: 0xD, 5: 0xD}, legs={1: 9, 2: 9, 3: 8, 4: 8, 6: 8}, shoes={3: 2},
                  arms={6: 2, 3: 2}),
        stripes=dict(white={1: 4, 2: 4, 3: 5, 4: 5, 6: 5}, black={6: 1, 3: 2, 4: 2}), midriff=True)),
    'magma-grunt-m': (293, 302, 'Team Magma grunt (M)', dict(
        pal={**GREY_RAMP, 6: (206, 57, 57), 7: (140, 33, 41), 8: (239, 115, 99), 9: (90, 24, 33), 0xA: (255, 165, 140)},
        maps=dict(cap={2: 6, 1: 7, 3: 8, 4: 8, 5: 6}, hair={7: 9, 8: 7, 9: 6, 0xA: 8},
                  mask={2: 0xC, 3: 0xC, 4: 0xD, 5: 0xD}, torso={1: 7, 2: 6, 3: 8, 4: 8, 6: 1},
                  arms={1: 7, 2: 6, 3: 8, 4: 8}, legs={}, shoes={1: 9, 2: 7, 3: 6, 4: 8}),
        half=6, horns=True)),
    'magma-grunt-f': (294, 192, 'Team Magma grunt (F)', dict(
        pal={**GREY_RAMP, 6: (206, 57, 57), 7: (140, 33, 41), 8: (239, 115, 99), 9: (90, 49, 33), 0xA: (156, 99, 57)},
        maps=dict(cap={2: 6, 1: 7, 3: 8, 4: 8, 5: 6}, hair={7: 9, 8: 0xA, 9: 0xA, 0xA: 0xA},
                  mask={2: 0xC, 3: 0xC, 4: 0xD, 5: 0xD}, torso={1: 7, 2: 6, 3: 8, 4: 8, 6: 1},
                  arms={1: 7, 2: 6, 3: 8, 4: 8}, legs={}, shoes={1: 7, 2: 6, 3: 8, 4: 8}),
        half=6, horns=True)),
    'archie': (293, 353, 'Archie (Team Aqua leader)', dict(
        pal={**GREY_RAMP, 6: (99, 148, 214), 7: (57, 99, 173), 8: (49, 49, 57), 9: (24, 24, 33), 0xA: (165, 198, 239),
             0xB: (132, 82, 57), 0xC: (173, 115, 82), 0xD: (206, 156, 115)},
        maps=dict(cap={2: 6, 1: 7, 5: 0xE, 3: 0xA, 4: 0xA}, hair={7: 9, 8: 8, 9: 8, 0xA: 2},
                  mask={2: 9, 3: 8, 4: 8, 5: 2}, torso={6: 0xE}, arms={6: 2}, legs={}, shoes={}),
        half=6)),
    'maxie': (293, 303, 'Maxie (Team Magma leader)', dict(
        pal={**GREY_RAMP, 6: (181, 41, 49), 7: (115, 24, 33), 8: (222, 82, 74), 9: (74, 16, 24), 0xA: (189, 214, 231)},
        maps=dict(cap={2: 6, 1: 7, 3: 6, 4: 6, 5: 6}, hair={7: 9, 8: 7, 9: 6, 0xA: 8},
                  mask={2: 0xC, 3: 0xC, 4: 0xD, 5: 0xD}, torso={1: 7, 2: 6, 3: 8, 4: 8, 6: 1},
                  arms={2: 1, 3: 2, 4: 2}, legs={}, shoes={}),
        torso_upper={6: 1, 3: 2, 4: 2}, split=3, half=6, glasses=0xA)),
}

def teams():
    """Team Aqua / Magma overworld sprites (see TEAM_OW)."""
    rows = []; shown = set()
    for name, (src, dst, note, spec) in TEAM_OW.items():
        frames, rgbs, meta = donor(src)
        _, _, dmeta = donor(dst)
        assert dmeta['textures'] == meta['textures'] and dmeta['size'] == meta['size'], (src, dst)
        pal = {**pal_dict(rgbs), **spec['pal']}
        new = [team_frame(f, spec, i) for i, f in enumerate(frames)]
        write_ow(dst, name, new, pal, note, f'Neo Team Plasma grunt {src}')
        if src not in shown:
            shown.add(src)
            rows.append((f'{src} Neo Team Plasma grunt ({"M" if src == 293 else "F"}), Black 2: the donor',
                         render(frames, pal_dict(rgbs), 3)))
        if dst != src:
            old, orgbs, _ = donor(dst)
            rows.append((f'{dst} before (Black 2; Unova-only, overwritten)', render(old, pal_dict(orgbs), 3)))
        rows.append((f'{dst} {note}', render(new, pal, 3)))
    return save_preview('team_overworld', rows, 'Team Aqua / Magma overworld (Gen 5 edits of the Neo Team Plasma grunts)')

# Battle (front, a/0/7/1): the Neo Plasma grunt sprites 149 (M) and 150 (F) are the donors. Sapphire battles the
# Aqua grunts, Matt, Shelly and Archie only (Team Magma trainers are Ruby's), so five slots of Team Plasma's sprites
# take them: 149 Aqua grunt M (itself), 150 Aqua grunt F (itself), 151 (Ghetsis) Archie, 152 (Rood) Matt, 153
# (Zinzolin) Shelly. The last three are drawn on a grunt's parts, so the build copies that grunt's MCSS files.
TEAM_SKIN = (9, 0xA, 0xB)

def team_tr_regions(img, boxes_by_region, order, maps):
    """Repaint `img` region by region (first region wins). 'head' boxes split per box at the first skin row:
    above = maps['cap'], below = maps['face']. A map {'_stripes': .., 'white': .., 'black': ..} paints 2-row
    stripes (rows 1-2 of every 4 white)."""
    out = img.copy(); used = np.zeros(img.shape, bool)
    yy = np.mgrid[0:img.shape[0], 0:img.shape[1]][0]
    def app(mask, table):
        if '_stripes' in table:
            white = mask & np.isin(yy % 4, [1, 2])
            for o, n in table['white'].items(): out[white & (img == o)] = n
            for o, n in table['black'].items(): out[mask & ~white & (img == o)] = n
        else:
            for o, n in table.items(): out[mask & (img == o)] = n
    for name in order:
        for box in boxes_by_region.get(name, []):
            m = box_mask(img.shape, [box]) & ~used
            if name == 'head':
                rows = [y for y in range(box[1], box[3]) if (m[y] & np.isin(img[y], TEAM_SKIN)).any()]
                split = rows[0] if rows else box[3]
                app(m & (yy < split), maps['cap']); app(m & (yy >= split), maps['face'])
            else:
                app(m, maps.get(name, {}))
            used |= m
    app(~used, maps['body'])
    return out

def team_tr(slot, name, spec):
    src = spec['from']
    parts, static, rgbs, cells, meta = tr_donor('front', src)
    off = figure_offset(parts, static, cells)
    assert off, f'sprite {src}: still and whole figure differ'
    fig = cell_box(cells[sprites.whole_figure_cell(cells)])
    boxes_p = {r: [cell_box(cells[c]) for c in ids] for r, ids in spec['cells'].items()}
    for r, bs in spec['static_boxes'].items():           # the whole figure in the parts sheet = the still, shifted
        for x0, y0, x1, y1 in bs:
            b = (max(x0 + off[0], fig[0]), max(y0 + off[1], fig[1]), min(x1 + off[0], fig[2]), min(y1 + off[1], fig[3]))
            if b[0] < b[2] and b[1] < b[3]:
                boxes_p.setdefault(r, []).append(b)
    new_parts = team_tr_regions(parts, boxes_p, spec['order'], spec['maps'])
    new_static = team_tr_regions(static, spec['static_boxes'], spec['order'], spec['maps'])
    pal = {**pal_dict(rgbs), **spec['colours']}
    write_tr('front', slot, name, new_parts, new_static, pal, spec['note'], f'Neo Team Plasma grunt front {src}',
             mcss_from=src)
    _, ostatic, orgbs, ocells, _ = tr_donor('front', slot)
    return new_parts, new_static, pal, cells, ostatic, orgbs

TORSO_STRIPES = {'_stripes': True, 'white': {7: 0xE, 8: 4, 3: 0xE, 0xE: 0xE, 5: 0xE, 6: 4}, 'black': {3: 8, 0xE: 7, 5: 7, 6: 8}}
SLEEVE_STRIPES = {'_stripes': True, 'white': {5: 0xE, 6: 4}, 'black': {5: 7, 6: 8}}
JEANS = {5: (74, 107, 181), 6: (49, 74, 140)}
M_REGIONS = dict(cells={'head': [0, 1, 16], 'torso': [9], 'sleeves': [4, 5, 17, 23, 6], 'pants': [10, 13]},
                 static_boxes={'head': [(24, 9, 50, 30)], 'torso': [(31, 29, 47, 48)], 'sleeves': [(14, 24, 60, 44)],
                               'pants': [(16, 46, 66, 80)]})
F_REGIONS = dict(cells={'head': [0, 1], 'torso': [6], 'sleeves': [2, 4, 7, 8, 14, 17], 'pants': [11, 13, 16]},
                 static_boxes={'head': [(26, 26, 52, 44)], 'torso': [(32, 44, 45, 57)], 'sleeves': [(18, 43, 64, 57)],
                               'pants': [(16, 56, 60, 80)]})
TEAM_TR = {  # slot: (folder name, spec); regions in priority order
    149: ('aqua-grunt-m', dict(M_REGIONS, **{'from': 149}, note='Team Aqua grunt (M)', order=['head', 'torso', 'sleeves', 'pants'],
          colours={2: (66, 115, 198), 0xD: (41, 66, 140), 4: (189, 197, 206), **JEANS},
          maps={'cap': {7: 2, 8: 0xD, 6: 0xD, 5: 2}, 'face': {5: 9, 6: 0xB, 2: 8},
                'torso': TORSO_STRIPES, 'sleeves': SLEEVE_STRIPES, 'pants': {}, 'body': {5: 7, 6: 8}})),
    150: ('aqua-grunt-f', dict(F_REGIONS, **{'from': 150}, note='Team Aqua grunt (F)', order=['head', 'torso', 'sleeves', 'pants'],
          colours={3: (66, 115, 198), 0xD: (41, 66, 140), 2: (214, 82, 115), 4: (189, 197, 206), **JEANS},
          maps={'cap': {7: 3, 8: 0xD, 6: 0xD, 5: 3}, 'face': {5: 9, 6: 0xB},
                'torso': TORSO_STRIPES, 'sleeves': SLEEVE_STRIPES, 'pants': {}, 'body': {5: 7, 6: 8}})),
    151: ('archie', dict(M_REGIONS, **{'from': 149}, note='Archie (Team Aqua leader)', order=['head', 'torso', 'sleeves', 'pants'],
          colours={2: (99, 148, 214), 0xD: (57, 99, 173), 7: (57, 66, 107), 8: (33, 36, 66), 9: (214, 156, 115),
                   0xA: (181, 123, 90), 0xB: (148, 99, 66), 0xC: (99, 57, 41)},
          maps={'cap': {7: 2, 8: 0xD, 6: 0xD, 5: 2}, 'face': {5: 8, 6: 7, 2: 8}, 'torso': {3: 0xE, 5: 7, 6: 8},
                'sleeves': {5: 7, 6: 8}, 'pants': {5: 7, 6: 8}, 'body': {5: 7, 6: 8}})),
    152: ('matt', dict(cells={**M_REGIONS['cells'], 'chest': []},
          static_boxes={**M_REGIONS['static_boxes'], 'chest': [(35, 29, 43, 48)]},
          **{'from': 149}, note='Matt (Team Aqua admin)', order=['head', 'chest', 'torso', 'sleeves', 'pants'],
          colours={2: (66, 115, 198), 0xD: (41, 66, 140), 9: (231, 173, 132), 0xA: (198, 140, 99), 0xB: (165, 107, 74),
                   **JEANS},
          maps={'cap': {7: 2, 8: 0xD, 6: 0xD, 5: 2}, 'face': {5: 9, 6: 0xB, 2: 8},
                'chest': {7: 9, 8: 0xA, 3: 9, 0xE: 9, 5: 9, 6: 0xA}, 'torso': {7: 2, 8: 0xD, 3: 2, 0xE: 2, 5: 9, 6: 0xA},
                'sleeves': {5: 9, 6: 0xA}, 'pants': {}, 'body': {5: 7, 6: 8}})),
    153: ('shelly', dict(F_REGIONS, **{'from': 150}, note='Shelly (Team Aqua admin)', order=['head', 'torso', 'sleeves', 'pants'],
          colours={3: (66, 115, 198), 0xD: (41, 66, 140), 2: (239, 115, 49), **JEANS},
          maps={'cap': {7: 3, 8: 0xD, 6: 0xD, 5: 3}, 'face': {5: 9, 6: 0xB}, 'torso': {5: 9, 6: 0xA},
                'sleeves': {5: 9, 6: 0xA}, 'pants': {}, 'body': {5: 7, 6: 8}})),
}

def teams_battle():
    """Team Aqua battle sprites for Sapphire (see TEAM_TR)."""
    rows = []
    for slot, (name, spec) in TEAM_TR.items():
        src = spec['from']
        parts, static, rgbs, cells, meta = tr_donor('front', src)
        new_parts, new_static, pal, cells, ostatic, orgbs = team_tr(slot, name, spec)
        S0 = np.zeros((80, 80), np.uint8)
        if slot != src:
            _, _, orgbs2, ocells, _ = tr_donor('front', slot)
            oparts = tr_donor('front', slot)[0]
            rows.append((f'front {slot} before (Black 2; Team Plasma, overwritten)',
                         tr_render(oparts, ostatic, pal_dict(orgbs), ocells, 2)))
        else:
            rows.append((f'front {slot} Neo Team Plasma grunt (Black 2)', tr_render(parts, static, pal_dict(rgbs), cells, 2)))
        rows.append((f'front {slot} {spec["note"]}' + (f' (drawn on grunt {src}\'s parts)' if slot != src else ''),
                     tr_render(new_parts, new_static, pal, cells, 2)))
    return save_preview('team_battle', rows, 'Team Aqua battle sprites (front, a/0/7/1) for Sapphire')

RECIPES = {'brendan': brendan, 'may': may, 'rivals': rivals, 'birch': birch, 'mom': mom, 'bag': bag,
           'trainers': trainers, 'intro': intro, 'teams': teams, 'teams_battle': teams_battle}

SUPERSEDED = ('teams', 'teams_battle')   # replaced by b2tools/sprite_upgrade.py (redrawn from Sapphire's own art)
SUPERSEDED += ('mom',)                    # replaced by b2tools/sprite_unique.py (Hoenn Mom 251/357 redrawn)
SUPERSEDED += ('brendan', 'may', 'birch', 'trainers', 'intro')   # replaced by b2tools/sprite_players.py
SUPERSEDED += ('bag',)                    # replaced by b2tools/models_objects.py (Sapphire's own bag pixels, 2026-10-08)

def main(argv):
    names = argv or [r for r in RECIPES if r not in SUPERSEDED]
    for n in names:
        print(n, '->', RECIPES[n]())

if __name__ == '__main__':
    main(sys.argv[1:])
