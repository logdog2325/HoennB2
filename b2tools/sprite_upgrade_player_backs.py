"""Brendan's and May's battle backs (player back sprites 0 and 1, a/0/7/2) from Sapphire's own brendan_back.png and
may_back.png, by Wally's method (b2tools/sprite_upgrade_backs.py; user 2026-10-08: the redraws on Nate/Rosa "look
terrible", use their real back sprites).

Sapphire's back pictures have four 64x64 frames. pokeruby data/mon_attrs.s (gUnknown_081ECACC, the player's back
animations) shows which is which: animation 0, shown while the player slides in, is frame 3 (standing); the throw
(animation 1) plays frames 0 (ball raised) 24 ticks, 1 (wind-up) 9, 2 (throw) 24, 0 9, 3 50.

Each frame is scaled as the fronts and Wally's back are (head x1.15, body below the neck x1.35, x1.2 wide; one-pixel
lines kept), with Gen 5 outlines (black on clothes, the skin's and hair's own dark tone) and Black 2's skin ramp, and
the body continues below the picture to the screen's edge (Black 2's backs reach it; the message box covers the lower
part during the throw): the bottom rows go on a little (jacket / top), then Brendan's navy trousers, May's white skirt,
black bike shorts and bare legs, in their own Sapphire colours as their front pictures show them.

Black 2's player backs are cut-out parts (a body and arm cells). Sapphire's frames are whole pictures, so each pose
uses one to three of the donor's own cells as whole-figure pieces (texture rectangles and quads unchanged), by data
only (same sizes, b2tools/patches/sprites.py "node_edits" and "still_multicells"). Three Sapphire poses fit; the
fourth has no texture room (each pose needs one of the donor's three big cells), so frame 0 (ball raised) is left out
and the throw goes standing -> wind-up -> throw:
  Brendan on Nate's sprite 0:  standing (frame 3) = cells 0 + 1 in multi-cells 0 and 1 (animation 0 and the throw's
                               first 20 ticks, Nate's own body + arm nodes); wind-up (frame 1) = cell 4 (multi-cells 2,
                               3; 20 ticks); throw (frame 2) = cell 5 (multi-cell 4); cells 2, 3 clear
  May on Rosa's sprite 1:      standing (frame 3) = cell 5 (multi-cells 0, 1); wind-up (frame 1) = cells 1 + 2 + 0
                               (multi-cell 2's three nodes, 15 ticks); throw (frame 2) = cell 6 (multi-cells 3, 4: the
                               throw shows 4 ticks earlier, multi-cell 3 has one node); cells 3, 4 clear. Her head top
                               sits 4 rows below Rosa's so the throw fits cell 6 (96 rows)
Sapphire's own placement of the frames gives the motion, so animation 1 no longer slides multi-cells 2-4.

    python3 sprite_upgrade_player_backs.py            writes src/sprites/trainer/back/000-brendan, 001-may
    python3 sprite_upgrade_player_backs.py review     screenshots/sprites/player_backs_review.png
"""
import io, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcss, sprites  # noqa: E402
import sprite_upgrade as U  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

# poses: (Sapphire frame, [cell, ...] in drawing order (first on top), [(multi-cell, node, cell)]) ; a node given
# cell None shows a cleared cell (CLEAR)
ORIGINAL_ONLY = True        # only Sapphire's own pixels (resized as the fronts): no body drawn below the picture
CHARS = {
    'brendan': dict(
        slot=0, pic='brendan_back', note='Brendan (player back), from Sapphire', neck=42, head_drop=0, hair=[],
        poses=[(3, [1, 0], [(0, 0, 1), (0, 1, 0), (1, 0, 1), (1, 1, 0)]),
               (1, [4], [(2, 0, 4), (2, 1, None), (3, 0, 4)]),
               (2, [5], [(4, 0, 5)])],
        clear=[2, 3], blank_seq=3,
        # below the picture: the jacket and pack go on (EXTEND rows), then navy trousers (light, mid, dark)
        extend=9, legs=dict(colours=(5, 6, 7), inset=0.1, gap=2)),
    'may': dict(
        slot=1, pic='may_back', note='May (player back), from Sapphire', neck=45, head_drop=4, hair=[({7, 8}, 8)],
        poses=[(3, [5], [(0, 1, 5), (0, 0, None), (1, 1, 5), (1, 0, None)]),
               (1, [1, 2, 0], [(2, 0, 1), (2, 1, 2), (2, 2, 0)]),
               (2, [6], [(3, 0, 6), (4, 0, 6)])],
        clear=[3, 4], blank_seq=4,
        # below the picture: the top and waist pack go on, then the white skirt, black bike shorts, bare legs
        extend=4, skirt=dict(rows=12, colours=(14, 9, 5)), shorts=dict(rows=4, colours=(6, 6, 15)),
        legs=dict(colours=(1, 2, 3), inset=0.16, gap=4)),
}
ROOT = os.path.abspath(os.path.join(HERE, '..'))


def donor(slot):
    e = narc_entries(arc_path(U.FILES, sprites.ARC_TR['back']))
    _, pal = sprites.nclr_colors(e[8 * slot + 7])
    _, _, parts = sprites.tr_decode_image(e[8 * slot + 1], 'parts')
    return (e, np.frombuffer(parts, np.uint8).reshape(128, 256).copy(), [sprites.bgr555_to_rgb(c) for c in pal],
            mcss.Sprite(e, 8 * slot))


def sapphire(pic):
    """Sapphire's four frames (64x64) and 16 colours, Black 2's skin ramp."""
    a, pal = U.gen3_trainer(pic)
    pal = list(pal)
    for i, c in U.B2_SKIN.items():
        pal[i] = c
    return [U.undither(a[64 * k:64 * k + 64], pal) for k in range(4)], pal


def band(ext, y0, y1, x0, x1, colours):
    """Rows y0..y1 between columns x0..x1 in a material lit from the left: light, base, dark (Black 2's shading)."""
    light, base, dark = colours
    for x in range(x0, x1 + 1):
        r = (x - x0) / max(1, x1 - x0)
        ext[y0:y1, x] = light if r < 0.2 else base if r < 0.75 else dark


def lower_body(c, b):
    """Rows below the picture down to the screen's edge (80 rows; cut later)."""
    last = b[-1]
    xs = np.nonzero(last)[0]
    ext = np.zeros((80, b.shape[1]), np.uint8)
    x0, x1 = xs.min(), xs.max()
    n = c['extend']
    ext[:n] = last                                            # the jacket / top goes on
    w = x1 - x0
    lx0, lx1 = int(round(x0 + w * c['legs']['inset'])), int(round(x1 - w * c['legs']['inset']))
    y = n
    if 'skirt' in c:                                          # May: white skirt, flared one pixel each side
        s = c['skirt']
        band(ext, y, y + s['rows'], lx0 - 1, lx1 + 1, s['colours'])
        y += s['rows']
        h = c['shorts']
        band(ext, y, y + h['rows'], lx0 + 1, lx1 - 1, h['colours'])
        y += h['rows']
    mid = (lx0 + lx1) // 2
    g = c['legs']['gap']
    for a, z in ((lx0 + 1, mid - g // 2), (mid + g - g // 2, lx1 - 1)):   # two legs
        band(ext, y, 80, a, z, c['legs']['colours'])
    return ext


def scaled(c, f, top):
    """A frame at Black 2's proportions with Gen 5 outlines, its body continued to the screen's edge."""
    neck = c['neck']
    head, body = np.arange(top, neck), np.arange(neck, 64)
    ymap = np.concatenate([head[U.axis_map(len(head), round(len(head) * U.HEAD_Y))],
                           body[U.axis_map(len(body), round(len(body) * U.BODY_Y))]])
    b = U.rescale(f, U.axis_map(64, round(64 * U.WIDE)), ymap)
    # user 2026-10-09: nothing below Sapphire's picture (the drawn jacket, trousers, skirt and legs looked wrong)
    ext = lower_body(c, b) if not ORIGINAL_ONLY else np.zeros((1, b.shape[1]), np.uint8)
    n = len(b)
    b = np.concatenate([b, ext])
    groups = [(*U.SKIN_GROUP, None)] + [(set(h[0]), h[1], None) for h in c['hair']]
    b = U.colour_outlines(U.clean_corners(U.outline_edges(b)), groups)
    return b[:-1], n


def figures(c):
    """[canvas picture per pose] (screen edge = canvas row 128), Sapphire's relative placement kept; 16 colours."""
    e, tex, dpal, sp = donor(c['slot'])
    fr, pal = sapphire(c['pic'])
    top = min(int(np.nonzero(f.any(1))[0][0]) for f in fr)
    d = mcss.render(sp, tex, 0, 0)
    dy0 = int(np.nonzero(d.any(1))[0][0])                      # the donor's head: top row and centre
    dcols = np.nonzero(d[dy0:dy0 + 20].any(0))[0]
    pics = {k: scaled(c, fr[k], top)[0] for k, _, _ in c['poses']}
    ref = c['poses'][0][0]
    rtop = int(np.nonzero(fr[ref].any(1))[0][0])
    y0 = round((rtop - top) * U.HEAD_Y)
    wcols = np.nonzero(pics[ref][y0:y0 + 20].any(0))[0]
    dy = dy0 + c['head_drop'] - y0
    dx = int(round((dcols.min() + dcols.max()) / 2 - (wcols.min() + wcols.max()) / 2))
    H, W = mcss.CANVAS[::-1]
    out = []
    for k, _, _ in c['poses']:
        cv = np.zeros((H, W), np.uint8)
        b = pics[k]
        by, bx = np.nonzero(b)
        Y, X = by + dy, bx + dx
        ok = (Y >= 0) & (Y < mcss.ORIGIN[1]) & (X >= 0) & (X < W)
        cv[Y[ok], X[ok]] = b[by[ok], bx[ok]]
        out.append(cv)
    return out, pal, (e, tex, dpal, sp)


def quad(sp, ci):
    cl = sp.cells[ci]
    return (min(o[0] for o in cl), min(o[1] for o in cl), max(o[0] + o[2] for o in cl), max(o[1] + o[3] for o in cl))


def place(fig, sizes):
    """Top-left canvas corners of rectangles `sizes` [(w, h)] covering every pixel of fig: the first anywhere (searched),
    the rest over what it leaves (one rectangle: its bounding box; two: split by a vertical or horizontal cut)."""
    ys, xs = np.nonzero(fig)
    if len(sizes) == 1:
        w, h = sizes[0]
        assert xs.max() - xs.min() < w and ys.max() - ys.min() < h, f'pose needs {np.ptp(xs) + 1}x{np.ptp(ys) + 1}'
        cx = int(round((xs.min() + xs.max() + 1) / 2 - w / 2))
        return [(min(max(cx, xs.max() + 1 - w), xs.min()), 128 - h)]
    (w1, h1), rest = sizes[0], sizes[1:]
    for y in range(128 - h1, ys.min() - h1, -1):                 # prefer the first cell at the screen's edge
        rowin = (ys >= y) & (ys < y + h1)
        for x in range(xs.min() - w1 + 1, xs.max() + 1):
            inside = rowin & (xs >= x) & (xs < x + w1)
            rx, ry = xs[~inside], ys[~inside]
            if not len(rx):
                return [(x, y)] + [(0, 0)] * len(rest)
            if len(rest) == 1:
                w2, h2 = rest[0]
                if np.ptp(rx) < w2 and np.ptp(ry) < h2:
                    return [(x, y), (int(rx.min()), int(ry.min()))]
                continue
            for v in (rx, ry):
                for cut in np.unique(v)[1:]:
                    A = v < cut
                    (wa, ha), (wb, hb) = rest
                    if np.ptp(rx[A]) < wa and np.ptp(ry[A]) < ha and np.ptp(rx[~A]) < wb and np.ptp(ry[~A]) < hb:
                        return [(x, y), (int(rx[A].min()), int(ry[A].min())), (int(rx[~A].min()), int(ry[~A].min()))]
    raise AssertionError('no placement covers the pose')


def seq_of(sp, ci):
    """The cell animation that shows only cell ci, unrotated."""
    for s, sq in enumerate(sp.nanr):
        if {r['idx'] for _, r in sq['frames']} == {ci} and all(r.get('rot', 0) == 0 for _, r in sq['frames']):
            return s
    raise ValueError(f'no still cell animation shows cell {ci} alone')


def build(name):
    c = CHARS[name]
    figs, pal, (e, tex, dpal, sp) = figures(c)
    O = mcss.ORIGIN
    new = np.zeros_like(tex)
    edits, lost = [], 0
    for (k, cells, nodes), fig in zip(c['poses'], figs):
        qs = {ci: quad(sp, ci) for ci in cells}
        corners = place(fig, [(qs[ci][2] - qs[ci][0], qs[ci][3] - qs[ci][1]) for ci in cells])
        own = np.zeros(fig.shape, bool)
        node_xy = {}
        for ci, (cx, cy) in zip(cells, corners):
            qx0, qy0, _, _ = qs[ci]
            nx, ny = cx - O[0] - qx0, cy - O[1] - qy0
            node_xy[ci] = (nx, ny)
            X, Y, Uu, V = mcss.cell_pixels(sp.cells[ci], (0, 1, 1, nx, ny))
            X = X + O[0]; Y = Y + O[1]
            ok = (X >= 0) & (X < fig.shape[1]) & (Y >= 0) & (Y < fig.shape[0])
            mine = np.zeros(len(X), bool)
            mine[ok] = ~own[Y[ok], X[ok]]                       # a pixel belongs to the first cell drawn over it
            val = np.zeros(len(X), np.uint8)
            val[mine] = fig[Y[mine], X[mine]]
            new[V, Uu] = val
            own[Y[mine], X[mine]] = True
        lost += int(((fig != 0) & ~own).sum())
        for mc, node, ci in nodes:
            if ci is None:
                edits.append(dict(mc=mc, node=node, seq=c['blank_seq']))
            else:
                edits.append(dict(mc=mc, node=node, seq=seq_of(sp, ci), x=int(node_xy[ci][0]), y=int(node_xy[ci][1])))
    for ci in c['clear']:
        for (x, y, w, h, u, v, hf, vf) in sp.cells[ci]:
            new[v:v + h, u:u + w] = 0
    assert lost == 0, f'{name}: {lost} pixels outside every cell'
    e2 = list(e)
    e2[8 * c['slot'] + 4] = mcss.set_nodes(e[8 * c['slot'] + 4], edits)
    e2[8 * c['slot'] + 5] = mcss.still_translations(e[8 * c['slot'] + 5], 1, [2, 3, 4])
    sp2 = mcss.Sprite(e2, 8 * c['slot'])
    return new, pal, edits, (e, tex, dpal, sp, sp2), figs


def write(name):
    c = CHARS[name]
    new, pal, edits, (e, tex, dpal, sp, sp2), figs = build(name)
    s = c['slot']
    folder = os.path.join(U.SRC, 'trainer', 'back', f'{s:03d}-{name}')
    U._replace_folder(os.path.join(U.SRC, 'trainer', 'back'), s, folder)
    os.makedirs(folder, exist_ok=True)
    _, _, still = sprites.tr_decode_image(e[8 * s], 'static')            # Black 2 leaves the back still empty
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), new.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), bytes(still), 80, 80, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='trainer', side='back', sprite=s, archive=sprites.ARC_TR['back'], files=sprites.tr_files(s),
        name=name, note=c['note'], source=f"pokeruby graphics/trainers/{c['pic']}.png (frames 3, 1, 2)",
        layout=f'cells, quads and throw timing of Black 2 back sprite {s}; whole-figure poses',
        node_edits=edits, still_multicells=[2, 3, 4], made_by='b2tools/sprite_upgrade_player_backs.py'))
    data = sprites.tr_encode_image(e[8 * s + 1], 'parts', new.tobytes())
    return f'{os.path.relpath(folder, U.ROOT)}: parts {len(data)} bytes compressed (donor {len(e[8 * s + 1])})'


def _git_parts(s, name):
    """The committed art (the Nate/Rosa redraws), for the review sheet."""
    try:
        data = subprocess.run(['git', 'show', f'HEAD:src/sprites/trainer/back/{s:03d}-{name}/parts.png'], cwd=ROOT,
                              capture_output=True, check=True).stdout
        pal = subprocess.run(['git', 'show', f'HEAD:src/sprites/trainer/back/{s:03d}-{name}/palette.pal'], cwd=ROOT,
                             capture_output=True, check=True).stdout
    except Exception:
        return None, None
    from PIL import Image
    im = Image.open(io.BytesIO(data))
    p = im.getpalette()[:48]
    return np.array(im), [tuple(p[3 * i:3 * i + 3]) for i in range(16)]


def review(path=None):
    from PIL import Image, ImageDraw
    ticks = [(0, 0), (1, 10), (1, 25), (1, 36), (1, 45), (1, 99)]
    def frame(spr, t_, p_, an, t):
        im = U.rgba(mcss.render(spr, t_, an, t), p_)
        return im.crop((24, 0, im.width - 24, mcss.ORIGIN[1]))     # the screen's edge
    rows = []
    for name, c in CHARS.items():
        new, pal, edits, (e, tex, dpal, sp, sp2), figs = build(name)
        a, gp = U.gen3_trainer(c['pic'])
        rows.append((f"{name}: Sapphire (graphics/trainers/{c['pic']}.png, frames 0-3, x2; the new sprite uses 3, 1, 2)",
                     [U.rgba(a[64 * k:64 * k + 64], gp).resize((128, 128), Image.NEAREST) for k in range(4)]))
        rows.append((f'{name}: NEW, animation 0 (standing), then the throw at ticks ' +
                     ', '.join(str(t) for _, t in ticks[1:]), [frame(sp2, new, pal, an, t) for an, t in ticks]))
        old, op = _git_parts(c['slot'], name)
        if old is not None:
            rows.append((f'{name}: current (HEAD, redrawn on Black 2\'s parts), same ticks',
                         [frame(sp, old, op, an, t) for an, t in ticks]))
        rows.append((f"Black 2 back sprite {c['slot']} ({'Nate' if c['slot'] == 0 else 'Rosa'}), same ticks",
                     [frame(sp, tex, dpal, an, t) for an, t in ticks]))
    W = max(sum(i.width + 4 for i in ims) for _, ims in rows) + 20
    H = sum(max(i.height for i in ims) + 22 for _, ims in rows) + 10
    out = Image.new('RGBA', (W, H), (88, 112, 128, 255)); d = ImageDraw.Draw(out); y = 6
    for label, ims in rows:
        d.text((10, y), label, fill=(255, 255, 255, 255)); y += 16
        x = 10; h = max(i.height for i in ims)
        for im in ims:
            out.alpha_composite(im, (x, y + h - im.height)); x += im.width + 4
        y += h + 6
    path = path or os.path.join(U.SHOTS, 'player_backs_review.png')
    out = out.resize((out.width * 2, out.height * 2), Image.NEAREST)
    out.save(path)
    return path


if __name__ == '__main__':
    if sys.argv[1:2] == ['review']:
        print('review ->', review(*sys.argv[2:3]))
    else:
        for n in (sys.argv[1:] or list(CHARS)):
            print(write(n))
