"""Brendan, May and Prof. Birch: Sapphire's own sprites resized and animated for Black 2, the sprite_upgrade.py way
(user 2026-10-06: "the overworld sprite and front sprite for Brendan and May should just be a resized and properly
animated version of the Gen 3 ones like you did for the other trainers ... do the same for Brendan and May and Birch").

    python3 sprite_upgrade_players.py [part ...]     default: all parts
        brendan, may   every player overworld set (walk-run, bike, surf, item, action2, action5, throw, balance,
                       fishing: 231-239 / 240-248) and the battle front (a/0/7/1 sprite 0 / 1)
        birch          overworld 104 (Cedric Juniper's slot)
        intro          the new-game intro professor (a/1/6/8, Juniper's MCSS set) from Sapphire's Birch picture
        review         screenshots/sprites/upgrade_review_players.png (Sapphire / new / Black 2 reference)

Same steps as sprite_upgrade.py (clean-up, Gen 5 proportions, one-pixel lines, Gen 5 outlines with the skin's and
hair's own dark tone, Black 2's skin ramps, two-pixel overworld eyes, the battle picture's colours on the overworld
sheets). Frames come from Sapphire's own sets (graphics/object_events/pics/people/brendan|may): walking and running
(normal.png), Mach Bike, surfing, field move and fishing; Black 2 sets Sapphire has no pictures for take the nearest
Sapphire frames (PLAYER_SETS lists every frame). Each frame is scaled as a whole (head rows x1.25, body rows x1.5,
x1.2 wide; bikes smaller to fit Black 2's 32x32 frame), placed with Sapphire's feet row and frame centre on Black 2's
(row 30, x 16; the 64x64 fishing frames 16 further), and Black 2's walking bob (one pixel up on the step frames).
The rival NPC sheets (1-6, 136-161) and the player icons (src/sprites/objframes) copy these folders in the build.
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sprites, mcss  # noqa: E402
import sprite_upgrade as U  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

GFX = 'OBJ_EVENT_GFX_{who}_{set}'

# Black 2 sheet -> frames: (Sapphire set, frame, flags) with flags 'm' = mirrored (right from left), 's' = a step
# frame (Black 2's walking bob). Black 2's orders (checked on Nate's sheets): walk-run 0-2 up, 3-5 down, 6-8 left,
# 9-11 right, then the same for running; bike the same 12 + one still frame per direction; surf up, down, left,
# right; balance 4 per direction; fishing (64x64) up: line out x2, rod raised x2; down: raised x2, out x2; left:
# raised x2, out x2 (Sapphire's take-out-rod frames: down 8-11 and left 0-3 rod raised -> line out, up 4-7 line out
# -> rod raised; matched by looking at them).
def _dirs(up, down, left, steps=True):
    """Walk-style block: up, down, left (stand, step, step) and right = left mirrored."""
    s = 's' if steps else ''
    out = []
    for st, a, b in (up, down, left):
        out += [(st[0], st[1], ''), (a[0], a[1], s), (b[0], b[1], s)]
    out += [(f, k, fl + 'm') for f, k, fl in out[6:9]]
    return out

N, B, S, F, FI = 'NORMAL', 'MACH_BIKE', 'SURFING', 'FIELD_MOVE', 'FISHING'
PLAYER_SETS = {   # offset in the code range (231 + n for Brendan, 240 + n for May): (name, frames)
    0: ('walk-run', _dirs(((N, 1), (N, 5), (N, 6)), ((N, 0), (N, 3), (N, 4)), ((N, 2), (N, 7), (N, 8))) +
                    _dirs(((N, 10), (N, 14), (N, 15)), ((N, 9), (N, 12), (N, 13)), ((N, 11), (N, 16), (N, 17)))),
    1: ('bike', _dirs(((B, 1), (B, 5), (B, 6)), ((B, 0), (B, 3), (B, 4)), ((B, 2), (B, 7), (B, 8)), steps=False) +
                [(B, 1, ''), (B, 0, ''), (B, 2, ''), (B, 2, 'm')]),
    2: ('surf', [(S, 1, ''), (S, 0, ''), (S, 2, ''), (S, 2, 'm')]),
    3: ('item', [(N, 0, ''), (F, 4, 'm')]),                     # stand; arm raised (Sapphire's field move)
    4: ('action2', [(N, 0, ''), (F, 2, '')]),                   # stand; hands in front
    5: ('action5', [(N, 2, ''), (N, 2, ''), (N, 1, ''), (N, 1, ''), (N, 1, '')]),
    6: ('throw', [(F, 2, ''), (F, 2, ''), (F, 4, 'm'), (F, 3, 'm')]),   # ball held, raised, thrown
    7: ('balance', [(N, 1, ''), (N, 5, 's'), (N, 1, ''), (N, 6, 's'), (N, 0, ''), (N, 3, 's'), (N, 0, ''), (N, 4, 's'),
                    (N, 2, ''), (N, 7, 's'), (N, 2, ''), (N, 8, 's'), (N, 2, 'm'), (N, 7, 'sm'), (N, 2, 'm'),
                    (N, 8, 'sm')]),
    8: ('fishing', [(FI, 4, ''), (FI, 5, ''), (FI, 6, ''), (FI, 7, ''), (FI, 8, ''), (FI, 9, ''), (FI, 10, ''),
                    (FI, 11, ''), (FI, 0, ''), (FI, 1, ''), (FI, 2, ''), (FI, 3, '')]),
}

# Colours: the battle picture's (trainers/brendan.png, may.png; birch_speech/birch.png for Birch) on Sapphire's
# overworld palette indices; skin = Black 2's overworld ramp (sprite_upgrade.B2_SKIN_OW).
PLAYERS = {
    'brendan': dict(who='BRENDAN', base=231, note='Brendan', colours={
        5: (74, 90, 131), 6: (49, 65, 106), 8: (24, 41, 82)}, hair=[],
        battle=dict(pic='brendan', slot=0, layout=108, intro='gesture', neck=24)),
    'may': dict(who='MAY', base=240, note='May', colours={}, hair=[({7, 8}, 8)],
                battle=dict(pic='may', slot=1, layout=108, intro='gesture', neck=23, hair=[({7, 8}, 8)])),
}
BIRCH = dict(gfx='OBJ_EVENT_GFX_PROF_BIRCH', code=104, neck=22, hair=[({11, 12, 13}, 13)], colours={
    5: (205, 205, 222), 6: (148, 148, 148), 7: (98, 98, 115), 8: (189, 156, 90), 9: (139, 115, 57),
    10: (74, 49, 24), 11: (180, 115, 82), 12: (115, 74, 57), 13: (74, 49, 24)})

SX, HY, BY = U.OW_X, U.OW_HEAD_Y, U.OW_BODY_Y       # 1.2, 1.25, 1.5
NECK, FEET = 22, 30                                  # Sapphire's people: body from row 22, feet on row 30

_g3 = {}
def g3(who, s):
    key = (who, s)
    if key not in _g3:
        _g3[key] = U.gen3_overworld(GFX.format(who=who, set=s))
    return _g3[key]

def scale_frame(f, sx=SX, hy=HY, by=BY, neck=NECK):
    """A whole Sapphire frame scaled (rows above `neck` x hy, below x by, columns x sx). Returns (array, row of
    Sapphire's feet row, column of Sapphire's frame centre) in the scaled array."""
    H, W = f.shape
    hn, bn = round(neck * hy), round((H - neck) * by)
    ymap = np.concatenate([np.arange(neck)[U.axis_map(neck, hn)], np.arange(neck, H)[U.axis_map(H - neck, bn)]])
    xmap = U.axis_map(W, round(W * sx))
    b = U.rescale(f, xmap, ymap)
    feet = int(np.nonzero(ymap == FEET)[0][-1])
    return b, feet, len(xmap) / 2

def fit_factors(frames):
    """Bike frames: Sapphire's bikes are wide; keep the whole set inside Black 2's 32x32 frame."""
    w = max(np.ptp(np.nonzero(f.any(0))[0]) + 1 for f in frames)
    h = max(FEET - np.nonzero(f.any(1))[0][0] + 1 for f in frames)
    s = min(SX, 31 / w)
    return s, min(HY, 30 / h * 0.97), min(BY, 30 / h)

ANCHOR = {'surf': 28}                               # Black 2's sitting surf frames end higher than row 30

def place(b, feet, cx, size, rise=0, anchor=FEET):
    out = np.zeros((size, size), np.uint8)
    off = (size - 32) // 2
    y0 = anchor + off - feet - rise
    x0 = int(round(16 + off - cx))
    ys, xs = np.nonzero(b)
    Y, X = ys + y0, xs + x0
    ok = (Y >= 0) & (Y < size) & (X >= 0) & (X < size)
    out[Y[ok], X[ok]] = b[ys[ok], xs[ok]]
    return out

def step(b, feet):
    """Black 2's walking bob: the body one pixel higher, the hips stretched by a row, the feet where they were."""
    ys = np.nonzero(b.any(1))[0]
    hip = int(ys[0] + (feet - ys[0]) * 0.62)
    return np.vstack([b[:hip], b[hip - 1:hip], b[hip:]]), feet + 1

def player_sheet(spec, n):
    """(frames, 16 colours, size) of Black 2 sheet base+n for a player spec."""
    name, plan = PLAYER_SETS[n]
    code = spec['base'] + n
    _, _, meta = U_donor(code)
    size = meta['size'][0]
    pal = None
    sets = {s for s, _, _ in plan}
    factors = {}
    for s in sets:
        fr, p = g3(spec['who'], s)
        factors[s] = fit_factors(fr) if s == B else (SX, HY, BY)
    out = []
    for s, k, fl in plan:
        fr, p = g3(spec['who'], s)
        if pal is None:
            pal = list(p)
            for i, c in {**spec['colours'], **U.B2_SKIN_OW}.items():
                pal[i] = tuple(c)
        f = U.undither(fr[k], pal)
        b, feet, cx = scale_frame(f, *factors[s])
        b = U.outline_edges(b)
        b = U.colour_outlines(b, [(*U.SKIN_GROUP, None)] + [(set(h[0]), h[1], round(NECK * HY) + 1)
                                                            for h in spec.get('hair', [])])
        rise = 0
        if 's' in fl:
            b, feet = step(b, feet)
        frame = U.bigger_eyes(place(b, feet, cx, size, rise, ANCHOR.get(name, FEET)), last_row=20 + (size - 32) // 2)
        if 'm' in fl:
            frame = frame[:, ::-1].copy()
            if size == 32:
                frame = np.roll(frame, 0, axis=1)
        out.append(frame)
    return out, pal, size

_donors = {}
def U_donor(code):
    if code not in _donors:
        table = sprites.ow_table(U.FILES)
        sheet, rec = sprites.ow_sheet_of(U.FILES, code, table)
        btx = narc_entries(arc_path(U.FILES, sprites.ARC_OW_SHEETS))[sheet]
        frames, pname, pal = sprites.btx_decode(btx)
        meta = dict(kind='overworld', code=code, sheet=sheet, frames=len(frames), size=[frames[0][1], frames[0][2]],
                    controller=rec['spriteControllerType'], textures=[f[0] for f in frames], palette=pname)
        arrs = [np.frombuffer(bytes(px), np.uint8).reshape(h, w).copy() for _, w, h, px in frames]
        _donors[code] = (arrs, [sprites.bgr555_to_rgb(c) for c in pal], meta)
    return _donors[code]

def write_sheet(code, name, frames, pal, note, source):
    arrs, _, meta = U_donor(code)
    assert len(frames) == meta['frames'] and frames[0].shape == arrs[0].shape, (code, len(frames), meta['frames'])
    folder = os.path.join(U.SRC, 'overworld', f'{code:03d}-{name}')
    U._replace_folder(os.path.join(U.SRC, 'overworld'), code, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    w, h = meta['size']
    for i, f in enumerate(frames):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), f.tobytes(), w, h, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(meta, name=name, note=note, source=source,
                                                                   made_by='b2tools/sprite_upgrade_players.py'))
    return folder

def player(who):
    spec = PLAYERS[who]
    done = []
    for n, (name, plan) in PLAYER_SETS.items():
        frames, pal, size = player_sheet(spec, n)
        sets = sorted({s.lower() for s, _, _ in plan})
        done.append(write_sheet(spec['base'] + n, f'{who}-{name}', frames, pal, f'{spec["note"]} (player), {name}',
                                f'pokeruby graphics/object_events/pics/people/{who}/' + ', '.join(sets)))
    ch = dict(note=f'{spec["note"]} (rival battles, Hall of Fame)', battle=spec['battle'])
    folder, rep = U.write_battle(who, ch)
    done.append(folder)
    return [os.path.relpath(d, U.ROOT) for d in done] + [str(rep)]

def birch():
    ch = dict(note='Prof. Birch', overworld=BIRCH)
    return os.path.relpath(U.write_overworld('prof-birch', ch), U.ROOT)


# ---------------------------------------------------------------------------------------------------- intro professor
# The new-game intro's professor (ov294 sProfessorLoadInfo: a/1/6/8 parts 25, palette 28, cells 27, cell animations 24,
# multi-cells 30, multi-cell animations 29, MCSS data 26). Its three animations: 0 idle (tosses a Poke Ball and
# catches it), 2 the throw that brings out Azurill (the head swaps to an open-mouth head 27 during it), 1 standing
# (blinking: eye strip cell 3 = closed, 2 = open). Sapphire's Birch picture (graphics/birch_speech/birch.png, 64x64)
# is scaled to Juniper's height (113 px) and cut onto her parts as she stands in animation 1 (mcss.distribute_pose);
# the Poke Ball cells keep their art; the open-mouth head 27 gets an open-mouth version of the picture. The blink strip
# and the talking mouth (cell 4's MCSS quad, toggled by the talk flag) are moved onto his eyes and mouth (intro_build).
INTRO_ARC = 168
INTRO_FILES = dict(parts=25, palette=28, cells=27, nanr=24, nmcr=30, nmar=29)
INTRO_BALLS = (19, 20, 21, 22)
BIRCH_PIC = os.path.join(U.RUBY, 'graphics', 'birch_speech', 'birch.png')
BIRCH_EYES = [(9, 29), (9, 30), (10, 29), (10, 30), (9, 35), (9, 36), (10, 35), (10, 36)]   # (row, col) in birch.png
# Birch's open mouth (talking, the throw's shout), drawn on the scaled picture: (row, column) from the bottom-left of
# his eyes, colour: upper lip, red mouth, lower lip, over his closed mouth line
BIRCH_MOUTH_OPEN = [(5, 4, 4), (5, 5, 4), (5, 6, 4), (5, 7, 4), (5, 8, 4), (6, 4, 4), (6, 5, 13), (6, 6, 13),
                    (6, 7, 13), (6, 8, 4), (7, 5, 4), (7, 6, 4), (7, 7, 4)]
BIRCH_LID = 6                       # closed eyes' line (the eyes' dark colour)
BLINK_SEQ, MOUTH_SEQ = 1, 15        # the cell animations that show the eye strip (cells 2/3) and the mouth (cell 4)
BALL_RED = (206, 82, 82)
BALL_MAP = {8: 13, 9: 13, 14: 14, 15: 15, 6: 9, 7: 5}   # Juniper's ball colours -> Birch's palette (red, white...)

class IntroSprite(mcss.Sprite):
    def __init__(self, e):
        f = INTRO_FILES
        self.cells = sprites.ncer_cells(e[f['cells']])
        self.nanr = mcss.parse_anim(e[f['nanr']])
        self.nmcr = mcss.parse_nmcr(e[f['nmcr']])
        self.nmar = mcss.parse_anim(e[f['nmar']])

def intro_donor():
    e = narc_entries(arc_path(U.FILES, INTRO_ARC))
    _, pal = sprites.nclr_colors(e[INTRO_FILES['palette']])
    _, _, raw = sprites.tr_decode_image(e[INTRO_FILES['parts']], 'parts')
    return e, IntroSprite(e), np.frombuffer(raw, np.uint8).reshape(128, 256).copy(), \
        [sprites.bgr555_to_rgb(c) for c in pal]

def intro_pictures(sp, tex):
    """(figure, closed-eye figure, open-mouth figure) on the mcss canvas, and 16 colours."""
    from PIL import Image
    im = Image.open(BIRCH_PIC)
    a = np.array(im).astype(np.uint8)
    p = im.getpalette()[:48]
    pal = [tuple(p[3 * i:3 * i + 3]) for i in range(16)]
    for i, c in U.B2_SKIN.items():
        pal[i] = c
    a[a == 13] = 8                     # Birch's darkest brown joins the hair's dark brown: index 13 = the ball's red
    pal[13] = BALL_RED
    a = U.undither(a, pal)
    closed = a.copy()
    for y, x in BIRCH_EYES:
        closed[y, x] = 1                                   # marks the eyes (the closed eyes are drawn after scaling)
    jun = mcss.render(sp, tex, 1, 0)
    jy, jx = np.nonzero(jun)
    ys, xs = np.nonzero(a)
    reach = np.zeros(jun.shape, bool)                      # canvas pixels the standing pose's parts can show
    for ci, tr, k in mcss.pose(sp, 1, 0):
        X, Y, _, _ = mcss.cell_pixels(sp.cells[ci], tr)
        X = X + mcss.ORIGIN[0]; Y = Y + mcss.ORIGIN[1]
        ok = (X >= 0) & (X < reach.shape[1]) & (Y >= 0) & (Y < reach.shape[0])
        reach[Y[ok], X[ok]] = True
    def build(src, f, dx, dy):
        m = U.axis_map(64, round(64 * f))
        b = U.clean_corners(U.outline_edges(U.rescale(src, m, m)))
        b = U.colour_outlines(b, [(*U.SKIN_GROUP, None), ({7, 8}, 8, round(18 * f))])
        canvas = np.zeros(jun.shape, np.uint8)
        by, bx = np.nonzero(b)
        Y, X = by + dy, bx + dx
        ok = (Y >= 0) & (Y < canvas.shape[0]) & (X >= 0) & (X < canvas.shape[1])
        canvas[Y[ok], X[ok]] = b[by[ok], bx[ok]]
        return canvas
    # Placement: feet on Juniper's, centred on her, as big as her parts can show (Juniper's height at most; his
    # outstretched hand is wider than her pose). His eyes and mouth are lower than hers: intro_build moves the blink
    # and talking-mouth nodes there (putting his eyes in her blink strip instead cuts his hand off and the throw's
    # arm parts then carry pieces of his coat: tried).
    f0 = (jy.max() - jy.min() + 1) / (ys.max() - ys.min() + 1)
    best = None
    for shrink in np.arange(1.0, 0.84, -0.01):
        f = f0 * shrink
        m = U.axis_map(64, round(64 * f))
        b = U.rescale(a, m, m)
        by, bx = np.nonzero(b)
        dy = jy.max() - by.max()
        for dxe in range(-4, 5):
            dx = int(round((jx.min() + jx.max()) / 2 - (bx.min() + bx.max()) / 2)) + dxe
            Y, X = by + dy, bx + dx
            ok = (Y >= 0) & (Y < reach.shape[0]) & (X >= 0) & (X < reach.shape[1])
            lost = int((~ok).sum() + (~reach[Y[ok], X[ok]]).sum())
            key = (lost, abs(dxe))
            if best is None or key < best[0]:
                best = (key, f, dx, dy)
        if best[0][0] == 0:
            break
    _, f, dxe, dye = best
    fig = build(a, f, dxe, dye)
    eye = fig != build(closed, f, dxe, dye)                # Birch's eyes on the canvas
    ys, xs = np.nonzero(eye)
    eyes = (xs.min(), ys.min(), xs.max(), ys.max())
    closed = fig.copy()                                    # closed: skin, a one-pixel lid line low in each eye
    closed[eye] = 1
    cols = np.unique(xs)
    for run in np.split(cols, np.nonzero(np.diff(cols) > 1)[0] + 1):
        closed[eyes[3] - 1, run.min():run.max() + 1] = BIRCH_LID
    mouth = fig.copy()
    for dy, dx, c in BIRCH_MOUTH_OPEN:
        mouth[eyes[3] + dy, eyes[0] + dx] = c
    return [fig, closed, mouth], pal, eyes

def intro_build():
    """(files, sprite with the blink and mouth moved, Juniper's texture, her colours, new texture, colours, report,
    node moves). Juniper's blink strip and talking mouth (cells 2/3 and the mouth quad of cell 4: texture rows 56
    while the mouth is open, 64 when closed, MCSS flag 0x100 that ov294's talk command toggles; see
    notes/RESEARCH_STORY_SPRITES.md 5.4) are moved onto Birch's eyes and mouth and drawn from his face: open eyes,
    closed eyes, open mouth, closed mouth."""
    e, sp, tex, dpal = intro_donor()
    (fig, closed, mouth), pal, eyes = intro_pictures(sp, tex)
    O = mcss.ORIGIN
    def at(seq, changed):                                  # node = centre of the pixels the overlay changes
        ys, xs = np.nonzero(changed)
        return dict(seq=seq, x=int((xs.min() + xs.max() + 1) // 2) - O[0], y=int((ys.min() + ys.max() + 1) // 2) - O[1])
    blink, talk = at(BLINK_SEQ, closed != fig), at(MOUTH_SEQ, mouth != fig)
    moves = [blink, talk]
    e = list(e)
    e[INTRO_FILES['nmcr']] = mcss.move_nodes(e[INTRO_FILES['nmcr']], moves)
    sp = IntroSprite(e)
    new, rep = mcss.distribute_pose(sp, tex, fig, ref=(1, 0), keep=INTRO_BALLS, variants={27: mouth},
                                    overlays=(2, 3, 4, 5))
    # The overlays hold only the pixels they change; the rest of each strip is clear, so his face underneath (the
    # head part) shows through and an overlay never covers a moving part with stale pixels.
    def paint(ci, node, figure):
        X, Y, Uu, V = mcss.cell_pixels(sp.cells[ci], (0, 1, 1, node['x'], node['y']))
        X = X + O[0]; Y = Y + O[1]
        new[V, Uu] = np.where(figure[Y, X] != fig[Y, X], figure[Y, X], 0)
        assert (figure != fig).sum() == (new[V, Uu] != 0).sum(), f'cell {ci} misses changed pixels'
    paint(2, blink, fig)                                   # eyes open: clear
    paint(3, blink, closed)                                # eyes closed
    paint(4, talk, mouth)                                  # mouth quad, flag clear: rows 56 = open (talking)
    paint(5, talk, fig)                                    # flag set: rows 64 = closed (at rest): clear
    for ci in INTRO_BALLS:                                 # the balls' pixels, in Birch's colours
        for (x, y, w, h, u, v, hf, vf) in sp.cells[ci]:
            box = new[v:v + h, u:u + w]
            box[:] = np.vectorize(lambda c: BALL_MAP.get(int(c), int(c)))(tex[v:v + h, u:u + w])
    return e, sp, tex, dpal, new, pal, rep, moves

def intro_render(sp, tex, anim, t, talking=False):
    """mcss.render of the intro professor with the talk flag: the mouth quad (cell 4) shows texture rows 56 while
    the flag is clear (talking, every other 6 frames) and rows 64 when it is set (at rest)."""
    class Talk:
        pass
    s = Talk(); s.__dict__.update(sp.__dict__)
    s.cells = list(sp.cells)
    if not talking:
        s.cells[4] = [(x, y, w, h, u, v + 8, hf, vf) for (x, y, w, h, u, v, hf, vf) in sp.cells[4]]
    return mcss.render(s, tex, anim, t)

def intro():
    e, sp, tex, dpal, new, pal, rep, moves = intro_build()
    data = sprites.tr_encode_image(e[INTRO_FILES['parts']], 'parts', new.tobytes())
    folder = os.path.join(U.SRC, 'mcss', 'intro-professor-birch')
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), new.tobytes(), 256, 128, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='mcss', archive=INTRO_ARC, files={'parts': INTRO_FILES['parts'], 'palette': INTRO_FILES['palette'],
                                               'nmcr': INTRO_FILES['nmcr']},
        keep_size=True, node_moves=moves, name='intro-professor-birch', donor='Professor Juniper, intro (a/1/6/8 files 24-30)',
        note='Prof. Birch in the new-game intro, from Sapphire\'s Birch picture', source='pokeruby graphics/birch_speech/birch.png',
        made_by='b2tools/sprite_upgrade_players.py'))
    return os.path.relpath(folder, U.ROOT), rep, f'parts compress to {len(data)} of {len(e[INTRO_FILES["parts"]])} bytes'

# ---------------------------------------------------------------------------------------------------- review

def review():
    """screenshots/sprites/upgrade_review_players.png: Sapphire / new / Black 2 reference for every set."""
    from PIL import Image, ImageDraw
    rgba = U.rgba
    def strip(ims, sc, gap=4):
        ims = [i.resize((i.width * sc, i.height * sc), Image.NEAREST) for i in ims]
        W = sum(i.width + gap for i in ims); H = max(i.height for i in ims)
        o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = 0
        for i in ims:
            o.alpha_composite(i, (x, H - i.height)); x += i.width + gap
        return o
    def crop(im):
        a = np.array(im)[..., 3]
        ys, xs = np.nonzero(a)
        return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    sections = []
    for who, spec in PLAYERS.items():
        name = spec['note']
        for n, (setname, plan) in PLAYER_SETS.items():
            code = spec['base'] + n
            frames, pal, size = player_sheet(spec, n)
            don, dpal, meta = U_donor(code)
            sc = 3 if size == 32 else 2
            srcs = []
            for s_, k, fl in plan:
                fr, gp = g3(spec['who'], s_)
                img = rgba(fr[k], gp)
                srcs.append(img.transpose(Image.FLIP_LEFT_RIGHT) if 'm' in fl else img)
            sections.append((f'{name} {setname} ({code})', [('Sapphire', strip(srcs, sc)),
                                                           ('new', strip([rgba(f, pal) for f in frames], sc)),
                                                           (f'Black 2 (Nate/Rosa {code})', strip([rgba(f, dpal) for f in don], sc))]))
        b = spec['battle']
        a, gp = U.gen3_trainer(b['pic'])
        still, parts, npal, rep, sp, off = U.battle_sprite(b)
        T = sp.length(0)
        fr = U.anim_frames(sp, parts, npal, [0, T // 4, T // 2, 3 * T // 4])
        dp, dstill, ddpal, dsp = U.tr_donor(b['slot'])
        ref = mcss.render(dsp, dp, 1, 0)
        sections.append((f'{name} battle front {b["slot"]} (intro: layout {b["layout"]})', [
            ('Sapphire', strip([rgba(a, gp)], 2)), ('new (still, intro)', strip([fr[-1]] + fr[:4], 2)),
            (f'Black 2 ({"Nate" if b["slot"] == 0 else "Rosa"})', strip([crop(rgba(ref, ddpal))], 2))]))
    g, gp = U.gen3_overworld(BIRCH['gfx'])
    nf, npal = U.ow_frames(BIRCH)
    don, dpal, _ = U_donor(104)
    sections.append(('Prof. Birch overworld (104)', [('Sapphire', strip([rgba(g[k], gp) for k in (1, 5, 6, 0, 3, 4, 2, 7, 8)], 3)),
                                                     ('new', strip([rgba(f, npal) for f in nf], 3)),
                                                     ('Black 2 (Cedric Juniper)', strip([rgba(f, dpal) for f in don], 3))]))
    e, sp, tex, dpal, new, pal, rep, moves = intro_build()
    from PIL import Image as I
    birch_pic = I.open(BIRCH_PIC).convert('RGBA')
    px = np.array(birch_pic); px[(px[..., :3] == (115, 197, 164)).all(-1)] = 0
    shots = [(1, 0, False), (1, 151, False), (1, 0, True), (0, 60, False), (0, 70, True), (2, 0, False),
             (2, 50, False), (2, 70, False), (2, 96, False)]
    dsp = IntroSprite(intro_donor()[0])                    # Juniper's own blink / mouth places
    def faces(spr, t_, p_, scale):
        im = [crop(rgba(intro_render(spr, t_, a_, t, k), p_)) for a_, t, k in shots[:3]]
        return [i.crop((0, 0, i.width, 60)).resize((i.width * scale, 60 * scale), I.NEAREST) for i in im]
    sections.append(('New-game intro professor (a/1/6/8, Juniper\'s MCSS set): standing, blink, talking; idle ball '
                     'toss; throw; faces x3 (rest, blink, talk)', [
        ('Sapphire (birch_speech/birch.png)', strip([I.fromarray(px)], 2)),
        ('new', strip([crop(rgba(intro_render(sp, new, a_, t, k), pal)) for a_, t, k in shots] +
                      faces(sp, new, pal, 3), 1)),
        ('Black 2 (Juniper)', strip([crop(rgba(intro_render(dsp, tex, a_, t, k), dpal)) for a_, t, k in shots[:6]] +
                                    faces(dsp, tex, dpal, 3), 1))]))
    rows = []
    for title, cells in sections:
        rows.append(('T', title))
        for label, im in cells:
            rows.append((label, im))
    W = max(im.width for k, im in rows if k != 'T') + 190
    H = sum((16 if k == 'T' else im.height + 6) for k, im in rows) + 30
    out = Image.new('RGBA', (W, H), (88, 112, 128, 255)); d = ImageDraw.Draw(out)
    d.text((6, 6), 'Brendan, May, Prof. Birch: Sapphire\'s own sprites resized and animated for Black 2 '
                   '(b2tools/sprite_upgrade_players.py) - Sapphire / new / Black 2 reference', fill=(255, 255, 255, 255))
    y = 26
    for k, im in rows:
        if k == 'T':
            d.text((6, y), im, fill=(255, 240, 160, 255)); y += 16
        else:
            d.text((6, y + 2), k, fill=(230, 236, 255, 255))
            out.alpha_composite(im, (184, y)); y += im.height + 6
    path = os.path.join(U.SHOTS, 'upgrade_review_players.png')
    out.convert('RGB').save(path)
    return path

PARTS = {'brendan': lambda: player('brendan'), 'may': lambda: player('may'), 'birch': birch, 'intro': intro, 'review': review}

def main(argv):
    for name in (argv or list(PARTS)):
        print(name, '->', PARTS[name]())

if __name__ == '__main__':
    main(sys.argv[1:])
