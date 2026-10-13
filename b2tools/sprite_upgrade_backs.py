"""Wally's back sprite for his catching tutorial, from Sapphire's own (b2tools/sprite_upgrade.py method).

Wally's catch (chapter Ch1, b2tools/patches/capture_demo.py) is Black 2's capture demo, whose thrower is back sprite 6
(a/0/7/2 files 48-55: Bianca's, class PKMN_TRAINER_BIANCA 38 in TRAINER_CLASS_BACK_SPRITES, arm9 0x02092314; Black 2
shows it only in that demo and when Bianca fights beside the player, which Hoenn never does). Sapphire's
graphics/trainers/wally_back.png has four 64x64 frames: standing, winding up, throwing, following through.

Each frame is scaled as the front sprites are (head x1.15, body x1.35, x1.2 wide; one-pixel lines kept), given Gen 5
outlines and Black 2's skin ramp, and his chest (where Sapphire's picture stops) continues down to the screen's edge
as Black 2's back sprites do (it sits behind the message box). Bianca's throw is cut-out parts (body, arm, raised arm,
lean); Wally's frames are whole pictures, so each pose shows one or two of her cells re-used as whole-figure cells
(their texture rectangles, +6 quads, unchanged), by data only (same sizes, b2tools/patches/sprites.py):
  animation 0 and the throw's first 35 ticks (multi-cells 0, 1)  standing, frame 0: cell 0 (56x128); her arm
                                                                cells 1, 2 left clear
  wind-up, 19 ticks (multi-cells 2, 3)                          frame 1: cell 5 (64x112); multi-cell 2's body node
                                                                plays cell 5's animation instead of the body's
  throw, 64 ticks (multi-cell 4)                                frame 2: cell 7 (40x24, the top of his hair) over
                                                                cell 6 (80x88)
Sapphire's own placement of the frames gives the motion, so animation 1 no longer slides multi-cells 2-4. Sapphire's
fourth frame (follow-through) has no cell left: the throw frame holds to the end.

    python3 sprite_upgrade_backs.py          writes src/sprites/trainer/back/006-wally
    python3 sprite_upgrade_backs.py review   screenshots/sprites/wally_back_review.png (Sapphire / new / Bianca)
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcss, sprites  # noqa: E402
import sprite_upgrade as U  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

SLOT = 6                                  # Bianca's back sprite: the capture demo's thrower
PIC = 'wally_back'
HAIR = ({7, 8, 10, 11}, 11)               # Wally's greens, outline = the darkest
ORIGINAL_ONLY = True                       # only Sapphire's own pixels (resized as the fronts): no body drawn below
SHIRT = {5, 6, 9, 13, 14}                 # his shirt's colours (the chest continued below the picture)
NECK = 45                                 # Sapphire's first row below his head (frame 0)
SHIRT_ROWS = 22                           # below the picture: his long shirt (as in his front picture), then trousers
BODY_NODE = (0, -56)                      # Bianca's body node (multi-cells 0-2): cell 0 spans y -128..0 from here
# (Sapphire frame, [(cell, multi-cell, node)]): the cells each pose shows; the first listed is drawn on top
POSES = [(0, [(0, 0, 1), (0, 1, 1)]),
         (1, [(5, 2, 2), (5, 3, 0)]),
         (2, [(7, 4, 1), (6, 4, 0)])]
CLEAR = (1, 2, 3, 4)                      # her arm cells: clear (the standing and wind-up frames are whole)


def donor():
    e = narc_entries(arc_path(U.FILES, sprites.ARC_TR['back']))
    _, pal = sprites.nclr_colors(e[8 * SLOT + 7])
    _, _, parts = sprites.tr_decode_image(e[8 * SLOT + 1], 'parts')
    return (e, np.frombuffer(parts, np.uint8).reshape(128, 256).copy(), [sprites.bgr555_to_rgb(c) for c in pal],
            mcss.Sprite(e, 8 * SLOT))


def sapphire():
    """Sapphire's four frames (64x64) and 16 colours, Black 2's skin ramp."""
    a, pal = U.gen3_trainer(PIC)
    pal = list(pal)
    for i, c in U.B2_SKIN.items():
        pal[i] = c
    return [U.undither(a[64 * k:64 * k + 64], pal) for k in range(4)], pal


def scaled(f, top):
    """A frame at Black 2's proportions with Gen 5 outlines; below the picture his body goes on to the screen's edge
    as his front picture draws it: the long white shirt (as wide as the bottom row's first to last shirt pixel), then
    two legs of green trousers."""
    head, body = np.arange(top, NECK), np.arange(NECK, 64)
    ymap = np.concatenate([head[U.axis_map(len(head), round(len(head) * U.HEAD_Y))],
                           body[U.axis_map(len(body), round(len(body) * U.BODY_Y))]])
    b = U.rescale(f, U.axis_map(64, round(64 * U.WIDE)), ymap)
    if ORIGINAL_ONLY:                   # user 2026-10-09: only Sapphire's picture, nothing drawn below or filled in
        b = np.concatenate([b, np.zeros((1, b.shape[1]), np.uint8)])
        b = U.colour_outlines(U.clean_corners(U.outline_edges(b)), [(*U.SKIN_GROUP, None), (*HAIR, None)])
        return b[:-1]
    last = b[-1]
    shirt = np.nonzero(np.isin(last, list(SHIRT)))[0]
    ext = np.zeros((80, b.shape[1]), np.uint8)
    x0, x1 = shirt.min(), shirt.max()
    for x in range(x0, x1 + 1):                               # his long shirt, lit from the left as his
        r = (x - x0) / max(1, x1 - x0)
        ext[:SHIRT_ROWS, x] = 14 if r < 0.15 else 9 if r < 0.7 else 13 if r < 0.9 else 5
    mid = (x0 + x1) // 2                                      # then his green trousers (front picture), two legs
    for lx0, lx1 in ((x0 + 2, mid - 1), (mid + 2, x1 - 2)):
        for x in range(lx0, lx1 + 1):
            r = (x - lx0) / max(1, lx1 - lx0)
            ext[SHIRT_ROWS:, x] = 8 if r < 0.3 else 10 if r < 0.75 else 11
    n = len(b)
    b = np.concatenate([b, ext])
    for y in range(n - 8, n):                                 # the gaps between his arms and chest just above it
        gap = b[y, x0:x1 + 1] == 0
        b[y, x0:x1 + 1][gap] = ext[0, x0:x1 + 1][gap]
    b = U.colour_outlines(U.clean_corners(U.outline_edges(b)), [(*U.SKIN_GROUP, None), (*HAIR, None)])
    return b[:-1]                                             # (the bottom row of the outline is off-screen)


def figures():
    """[canvas picture per pose] (screen bottom = canvas row 128), Sapphire's relative placement kept; 16 colours."""
    e, tex, dpal, sp = donor()
    fr, pal = sapphire()
    top = min(int(np.nonzero(f.any(1))[0][0]) for f in fr)
    d = mcss.render(sp, tex, 0, 0)
    dy0 = int(np.nonzero(d.any(1))[0][0])                      # Bianca's head: top row and centre
    dcols = np.nonzero(d[dy0:dy0 + 20].any(0))[0]
    pics = [scaled(fr[k], top) for k in range(4)]
    f0top = int(np.nonzero(fr[0].any(1))[0][0])
    y0 = round((f0top - top) * U.HEAD_Y)                       # frame 0's head top in the scaled pictures
    wcols = np.nonzero(pics[0][y0:y0 + 20].any(0))[0]
    dy = dy0 - y0
    dx = int(round((dcols.min() + dcols.max()) / 2 - (wcols.min() + wcols.max()) / 2))
    H, W = mcss.CANVAS[::-1]
    out = []
    for k, _ in POSES:
        c = np.zeros((H, W), np.uint8)
        b = pics[k]
        by, bx = np.nonzero(b)
        Y, X = by + dy, bx + dx
        ok = (Y >= 0) & (Y < mcss.ORIGIN[1]) & (X >= 0) & (X < W)
        c[Y[ok], X[ok]] = b[by[ok], bx[ok]]
        out.append(c)
    return out, pal, (e, tex, dpal, sp)


def quad(sp, ci):
    """The cell's rectangle (x0, y0, x1, y1) relative to its node (bounding box of its OBJs)."""
    c = sp.cells[ci]
    return (min(o[0] for o in c), min(o[1] for o in c), max(o[0] + o[2] for o in c), max(o[1] + o[3] for o in c))


def layout(sp, figs):
    """Node edits placing each pose's cells over its figure, and the canvas rows each cell takes."""
    O = mcss.ORIGIN
    edits, rows = [], {}
    for (k, cells), fig in zip(POSES, figs):
        ys, xs = np.nonzero(fig)
        fx0, fx1 = xs.min() - O[0], xs.max() + 1 - O[0]
        bottom = O[1]                                          # cells stack upwards from the screen's edge
        for ci, mc, node in reversed(cells):
            if ci in rows:                                     # the same cell again (another multi-cell)
                edits.append(dict(mc=mc, node=node, seq=seq_of(sp, ci), x=rows[ci][2], y=rows[ci][3]))
                continue
            qx0, qy0, qx1, qy1 = quad(sp, ci)
            ny = bottom - O[1] - qy1
            cols = xs[(ys >= bottom - (qy1 - qy0)) & (ys < bottom)] - O[0]
            cx0, cx1 = (cols.min(), cols.max() + 1) if len(cols) else (fx0, fx1)
            assert cx1 - cx0 <= qx1 - qx0, f'pose {k}: {cx1 - cx0} columns, cell {ci} is {qx1 - qx0} wide'
            nx = int(round((cx0 + cx1) / 2 - (qx0 + qx1) / 2))
            rows[ci] = (bottom - (qy1 - qy0), bottom, nx, ny)
            edits.append(dict(mc=mc, node=node, seq=seq_of(sp, ci), x=nx, y=ny))
            bottom -= qy1 - qy0
    return edits, rows


def seq_of(sp, ci):
    """The cell animation that shows only cell ci."""
    for s, sq in enumerate(sp.nanr):
        if {r['idx'] for _, r in sq['frames']} == {ci}:
            return s
    raise ValueError(f'no cell animation shows cell {ci} alone')


def build():
    figs, pal, (e, tex, dpal, sp) = figures()
    edits, rows = layout(sp, figs)
    new = np.zeros_like(tex)
    O = mcss.ORIGIN
    lost = 0
    for (k, cells), fig in zip(POSES, figs):
        own = np.zeros(fig.shape, bool)
        for ci, mc, node in cells:
            r0, r1, nx, ny = rows[ci]
            X, Y, Uu, V = mcss.cell_pixels(sp.cells[ci], (0, 1, 1, nx, ny))
            X = X + O[0]; Y = Y + O[1]
            ok = (X >= 0) & (X < fig.shape[1]) & (Y >= r0) & (Y < r1)
            new[V[ok], Uu[ok]] = fig[Y[ok], X[ok]]
            own[Y[ok], X[ok]] = True
        lost += int(((fig != 0) & ~own).sum())
    for ci in CLEAR:
        for (x, y, w, h, u, v, hf, vf) in sp.cells[ci]:
            new[v:v + h, u:u + w] = 0
    # the edited sprite, for previews
    e2 = list(e)
    e2[8 * SLOT + 4] = mcss.set_nodes(e[8 * SLOT + 4], edits)
    e2[8 * SLOT + 5] = mcss.still_translations(e[8 * SLOT + 5], 1, [2, 3, 4])
    sp2 = mcss.Sprite(e2, 8 * SLOT)
    return new, pal, dict(lost=lost, edits=edits), (e, tex, dpal, sp, sp2), figs


def write():
    new, pal, rep, (e, tex, dpal, sp, sp2), figs = build()
    folder = os.path.join(U.SRC, 'trainer', 'back', f'{SLOT:03d}-wally')
    U._replace_folder(os.path.join(U.SRC, 'trainer', 'back'), SLOT, folder)
    os.makedirs(folder, exist_ok=True)
    _, _, still = sprites.tr_decode_image(e[8 * SLOT], 'static')     # Black 2 leaves the back still empty
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), new.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), bytes(still), 80, 80, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='trainer', side='back', sprite=SLOT, archive=sprites.ARC_TR['back'], files=sprites.tr_files(SLOT),
        name='wally', note="Wally, the catching tutorial's thrower (Black 2's capture demo shows back sprite 6)",
        source=f'pokeruby graphics/trainers/{PIC}.png (frames 0-2)',
        layout=f'cells, quads and throw timing of Black 2 back sprite {SLOT} (Bianca); whole-figure poses',
        node_edits=rep['edits'], still_multicells=[2, 3, 4], made_by='b2tools/sprite_upgrade_backs.py'))
    data = sprites.tr_encode_image(e[8 * SLOT + 1], 'parts', new.tobytes())
    return (os.path.relpath(folder, U.ROOT), dict(lost=rep['lost']),
            f'parts {len(data)} bytes compressed (Bianca\'s {len(e[8 * SLOT + 1])})')


def review(path=None):
    from PIL import Image, ImageDraw
    new, pal, rep, (e, tex, dpal, sp, sp2), figs = build()
    a, gp = U.gen3_trainer(PIC)
    T = sp.length(1)
    ticks = [(0, 0), (1, 10), (1, 25), (1, 34), (1, 40), (1, 50), (1, 56), (1, 80), (1, T - 1)]
    def frame(spr, t_, p_, an, t):
        im = U.rgba(mcss.render(spr, t_, an, t), p_)
        return im.crop((0, 0, im.width, mcss.ORIGIN[1]))           # the screen's edge
    rows = [('Sapphire (graphics/trainers/wally_back.png, x2)',
             [U.rgba(a[64 * k:64 * k + 64], gp).resize((128, 128), Image.NEAREST) for k in range(4)]),
            ('new: animation 0 (still), then the throw (animation 1) at ticks ' + ', '.join(str(t) for _, t in ticks[1:]),
             [frame(sp2, new, pal, an, t) for an, t in ticks]),
            ('Black 2 back sprite 6 (Bianca), same ticks', [frame(sp, tex, dpal, an, t) for an, t in ticks])]
    W = max(sum(i.width + 4 for i in ims) for _, ims in rows) + 20
    H = sum(max(i.height for i in ims) + 22 for _, ims in rows) + 10
    out = Image.new('RGBA', (W, H), (88, 112, 128, 255)); d = ImageDraw.Draw(out); y = 6
    for label, ims in rows:
        d.text((10, y), label, fill=(255, 255, 255, 255)); y += 16
        x = 10; h = max(i.height for i in ims)
        for im in ims:
            out.alpha_composite(im, (x, y + h - im.height)); x += im.width + 4
        y += h + 6
    path = path or os.path.join(U.SHOTS, 'wally_back_review.png')
    out.save(path)
    return path


if __name__ == '__main__':
    if sys.argv[1:2] == ['review']:
        print('review ->', review(*sys.argv[2:3]))
    else:
        print(write())
