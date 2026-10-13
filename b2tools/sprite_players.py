"""Brendan, May and Prof. Birch as new Gen 5-style sprites drawn from their Sapphire (Gen 3) art (user request
2026-10-06: "upgrade their Gen 3 sprites directly ... the recolours aren't that great"; style: "very lightly touch
them up, but to the point where they look like actual Gen 5 sprites from Black 2 and White 2").

    python3 sprite_players.py [recipe ...]     default: all recipes, in this order:
      swan     the intro's boy/girl choice pictures (a/1/6/8 model 22, int_swan_m/f .1/.2): the user's official Omega
               Ruby / Alpha Sapphire art (src/reference/) resampled to Nate / Rosa's size, 256 colours, darkened copy
      card     src/sprites/cardpic/: the trainer card picture (a/0/4/0 avatars) = the battle front still (front 0 /
               1, copied at build time, so it follows whoever draws the fronts)
      backs    battle backs 0 / 1 (a/0/7/2, MCSS with Black 2's throw), Sapphire outfits
      review   screenshots/sprites/players_upgrade_review.png
    Moved to b2tools/sprite_upgrade.py (lead, 2026-10-06): the overworld sheets 231-248 (and the rival copies), the
    battle fronts 0 / 1, the player icons, Prof. Birch (overworld 104, intro professor). Their old recipes stay in
    this file as code only (brendan_ow, may_ow, birch_ow, brendan_front, may_front, intro_birch, write_player_icons)
    and are not run.
    Installed by patches/sprites.py; formats in sprites.py (all byte-exact round trips, `sprites.py check`).

How the art is made (pixel art on Black 2's own poses, not a filter):
- Overworld heads are drawn by hand, one template per view (front, back, side, front looking down), at Black 2's head
  size and in Black 2's style (black outer outline, coloured inner lines, 2-3 tone shading lit from the upper left,
  2-pixel eyes), with the Sapphire design and colours: Brendan's white knit hat with its point, black band with red
  marks, navy hair; May's red bandana with the white stripe and knot, brown hair in side bunches; Birch's messy
  red-brown hair and beard. Each donor frame gets the matching template at the donor head's own position (the
  donors' faces are rigid stamps that move with the walk bob and the run lean; found by matching); the donor's hair
  is erased first, hands and Poke Balls in front of the head stay in front.
- Bodies keep the donor's poses (frame layout and animation are Black 2's) and are repainted by material: each donor
  colour role (jacket and its tones, strap, bag, shorts, leggings, skin, shoes) takes the Sapphire material and tone
  it stands for; Sapphire-only details are drawn on (Brendan's red trim, yellow pack and strap; May's white skirt,
  bike shorts, bare shins; Birch's open coat and sandals). Battle sprites: the parts are labelled by cell (and the
  still picture by matching the cells into it), heads drawn anew (polygons, cel shading and hand patches), Rosa's
  twin tails cut to May's length.
- One 16-colour palette per sprite (Black 2's limit), colour 0 transparent; overworld and battle use the same colours.
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import sprites  # noqa: E402
import sprite_art as SA  # noqa: E402   donor(), write_ow(), render(), save_preview()

SHOTS = os.path.join(ROOT, 'screenshots', 'sprites')
RUBY = os.path.join(ROOT, 'external', 'pokeruby', 'graphics')

# ---------------------------------------------------------------------------------------------------- templates

def parse(rows, letters):
    """Template rows (strings) -> index array; '.' = not part of the stamp (-1)."""
    w = max(len(r) for r in rows)
    out = np.full((len(rows), w), -1, np.int16)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.':
                out[y, x] = letters[ch]
    return out

def stamp_at(frame, st, x0, y0, protect=None):
    """Paint stamp `st` (with -1 holes) onto `frame` with its top-left at (x0, y0); pixels in `protect` stay."""
    h, w = frame.shape
    for y, x in zip(*np.nonzero(st >= 0)):
        X, Y = x0 + x, y0 + y
        if 0 <= X < w and 0 <= Y < h and not (protect is not None and protect[Y, X]):
            frame[Y, X] = st[y, x]

def mirror(st):
    return st[:, ::-1].copy()

# ---------------------------------------------------------------------------------------------------- Brendan

B_LET = {'W': 1, 'w': 2, 'g': 3, 'o': 4, 'n': 5, 'N': 6, 'm': 7, 'R': 8, 'r': 9, 'Y': 0xA, 'y': 0xB,
         'S': 0xC, 's': 0xD, 'E': 0xE, 'K': 0xF}
B_PAL = {0: (115, 82, 107), 1: (255, 255, 255), 2: (214, 222, 239), 3: (156, 165, 198), 4: (99, 107, 140),
         5: (24, 32, 57), 6: (41, 52, 90), 7: (66, 82, 132), 8: (239, 90, 66), 9: (165, 41, 41),
         0xA: (255, 214, 90), 0xB: (214, 165, 57), 0xC: (255, 214, 189), 0xD: (206, 148, 123),
         0xE: (99, 120, 181), 0xF: (0, 0, 0)}           # the battle sprites' colours (BB_PAL / BF_PAL)

# Heads, drawn on the reference frame of Nate's walk sheet 231 (whole 32-px rows from y = first row):
# front = frame 3, back = frame 0, side (facing left) = frame 6, front looking down (running) = frame 15.
B_HEADS = {
    'down': (4, [
        '....................oo..........',
        '...................oWgo.........',
        '..........ooooo...oWwgo.........',
        '........ooWWWWWoooWwwgoo........',
        '.......oWWWWWWWWWWWwwwggo.......',
        '......oWWWwWWWWWwWWwwwgggo......',
        '......KwWWwWWWWWwWwwgwgggK......',
        '......KnnnnnnnnnnnnnnnnnnK......',
        '......KnnnnRRRRnnRRRRnnnnK......',
        '......KNnnnnnrrrrrrnnnnnNK......',
        '......KmNnssssssssssssnNmK......',
        '.......KNmSSSSSSSSSSSSmNK.......',
        '.......KNmSSWKSSSSKWSSmNK.......',
        '........KNSSWKSSSSKWSSNK........',
        '........KNsSSSSSSSSSSsNK........',
        '.........KKKsSSSSSSsKKK.........',
    ]),
    'up': (4, [
        '...........oo...................',
        '..........ogWo..................',
        '..........ogwWo...ooooo.........',
        '.........oWWwWWooooWWWWoo.......',
        '.......ooWWWWWWWWWWWWWwwgo......',
        '......oWWWwWWWWwWWWWwwwggo......',
        '......KWWWwWWWWwWWWwwwgggK......',
        '......KwWWwWWWWwWWwwwgwggK......',
        '......KwwWwwWWwwwwwwwgwggK......',
        '......KgwwgwwwwgwwwwgggggK......',
        '......KggwgggwwggwwgggggoK......',
        '......KnnnnnnnnnnnnnnnnnnK......',
        '......KsNNmNNNNNNNNNNmNNsK......',
        '........KnNNNNNNNNNNNNnK........',
        '.........KnnNNNNNNNNnnK.........',
        '...........KKssssssKK...........',
    ]),
    'left': (4, [
        '..................oo............',
        '.................oWgo...........',
        '..........ooooo.oWwgo...........',
        '........ooWWWWWooWwwgoo.........',
        '.......oWWWWWWWWWWwwwwggo.......',
        '......oWWWWWWWWWwwwwwwwggo......',
        '......KwWWWWWWwwwwwwwwwgggo.....',
        '......KnnnnnnnnnnnoggggggK......',
        '......KRRnnnnnnnnnNoggK.........',
        '......KrrnnnnnnnnNNNNK..........',
        '.......KssssNmNNNNNNK...........',
        '........KSSSSsNmNNNNNK..........',
        '........KSSSKWNNmNNNK...........',
        '........KSSSKWsNNNmNK...........',
        '.........sSSSSssKNNNK...........',
        '..........KsSsKnnnK.............',
        '...........KKKK.................',
    ]),
}
_d = B_HEADS['down'][1]
B_HEADS['dtilt'] = (4, _d[:12] + ['.......KNmSSKKSSSSKKSSmNK.......'] + _d[14:])


# ---------------------------------------------------------------------------------------------------- May

M_LET = {'W': 1, 'w': 2, 'R': 3, 'r': 4, 'd': 5, 'H': 6, 'h': 7, 'b': 8, 'S': 9, 's': 0xA, 'Y': 0xB, 'y': 0xC,
         'k': 0xD, 'n': 0xE, 'K': 0xF}
M_PAL = {0: (115, 198, 140), 1: (255, 255, 255), 2: (206, 206, 222), 3: (239, 74, 66), 4: (189, 41, 49),
         5: (123, 24, 33), 6: (189, 132, 90), 7: (140, 90, 57), 8: (90, 57, 41), 9: (255, 214, 189), 0xA: (222, 156, 123),
         0xB: (255, 214, 82), 0xC: (198, 148, 41), 0xD: (74, 74, 82), 0xE: (49, 49, 57),
         0xF: (0, 0, 0)}                                 # the battle sprites' colours (MF_PAL / MB_PAL)

# May's heads on Rosa's walk sheet 240 (front = frame 3, back = 0, side = 6, front looking down = 15): the red
# bandana tied on top (its two knot ends stand up like ears), the white stripe across it, brown hair falling in two
# flared bunches at the sides, Black 2's face.
M_HEADS = {
    'down': (4, [
        '.......KKK............KKK.......',
        '......KRRdK..........KdRRK......',
        '......KRrrdKKKKKKKKKKdrrRK......',
        '.......KdrRRRRRRRRRRRRrdK.......',
        '......KRRRRRRRRRRRRRRRRrrK......',
        '......KWWWWWWWWWWWWWWWWwwK......',
        '......KrrrrrrrrrrrrrrrrddK......',
        '.....KhHHHHHbHHHHHHbHHHHHhK.....',
        '.....KhHHbHHHbHHHHbHHHbHHhK.....',
        '.....KhHbHSbSSbSSbSSbSHbHhK.....',
        '....KhHHbSSSSSSSSSSSSSSbHHhK....',
        '....KhHbSSSSSSSSSSSSSSSSbHhK....',
        '...KhHHbKSSWKSSSSSSKWSSKbHHhK...',
        '...KhHHbKSSWKSSSSSSKWSSKbHHhK...',
        '...KhhbKKsSSSSSSSSSSSSsKKbhhK...',
        '....KKK..KKsSSSSSSSSsKK..KKK....',
    ]),
    'up': (4, [
        '.......KKK............KKK.......',
        '......KRRdK..........KdRRK......',
        '......KRrrdKKKKKKKKKKdrrRK......',
        '.......KdrRRRRRRRRRRRRrdK.......',
        '......KRRRRRRRRRRRRRRRRrrK......',
        '......KrRRRRRRRRRRRRRRRrdK......',
        '......KdrrrrrrrrrrrrrrrddK......',
        '......KhHHHHHHHHHHHHHHHHhK......',
        '......KhHHHHhHHHHhHHHHHHhK......',
        '......KhHHHhHHHHHHhHHHHHhK......',
        '.....KhHHHHhHHHHHHhHHHHHhK......',
        '.....KhHHHhHHHHHHHHhHHHHHhK.....',
        '....KhHHHhhHHHHHHHHhhHHHHhK.....',
        '...KhHHHhbKhHHHHHHhKbhHHHHhK....',
        '...KhhhbKKKhhhhhhhhKKKbhhhK.....',
        '....KKK....KKKKKKKK....KKK......',
    ]),
    'left': (4, [
        '..................KKK...KK......',
        '.................KRRdK.KdRK.....',
        '..........KKKKKKKRrrdKKdrRK.....',
        '........KKRRRRRRRRKdrdrrdK......',
        '.......KRRRRRRRRRRRRKddddK......',
        '......KWWWWWWRRRRRRRRrrK........',
        '......KrrrrrWWWWWWWWRrrdK.......',
        '......KHbHHHrrrrrrrrrrddK.......',
        '......KbHHHHHHHHHHhHHHHhK.......',
        '.......KHbHHHHHHHhHHHHHhK.......',
        '.......KSSbHHHHHHhHHHHHhK.......',
        '........KSSSbHHHHHhHHHHhK.......',
        '........KSKWSbHHHHhHHHHhhK......',
        '........KSKWSShHHhHHHHhhbK......',
        '.........sSSSSsbHhHHHHhhbK......',
        '..........KsSSsKbhhhhKKKKK......',
        '...........KKKK.KKKKK...........',
    ]),
}
_m = M_HEADS['down'][1]
M_HEADS['dtilt'] = (4, _m[:12] + ['...KhHHbKSSKKSSSSSSKKSSKbHHhK...'] + _m[14:])

# ---------------------------------------------------------------------------------------------------- composing

def head_fit(ref, f, mask, pad=6):
    """(dx, dy, quality): where the donor's rigid head pixels (`mask` of frame `ref`) sit in frame `f` (the donors'
    faces are stamps that move with the walk bob and the run lean)."""
    ys, xs = np.nonzero(mask)
    best = (-1, 0, 0)
    H, W = f.shape
    for dy in range(-pad, pad + 1):
        for dx in range(-pad, pad + 1):
            y2, x2 = ys + dy, xs + dx
            ok = (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
            m = int((f[y2[ok], x2[ok]] == ref[ys[ok], xs[ok]]).sum())
            if m > best[0]:
                best = (m, dx, dy)
    return best[1], best[2], best[0] / max(1, len(ys))

def grow(mask, allowed):
    """Flood `mask` through 4-connected pixels of `allowed`."""
    out = mask.copy()
    H, W = mask.shape
    stack = list(zip(*np.nonzero(mask)))
    while stack:
        y, x = stack.pop()
        for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= j < H and 0 <= i < W and allowed[j, i] and not out[j, i]:
                out[j, i] = True
                stack.append((j, i))
    return out

def close_outline(frame, erased, outline=0xF):
    """Pixels erased from the donor that now border a kept coloured pixel become outline (closes the figure)."""
    H, W = frame.shape
    res = frame.copy()
    for y, x in zip(*np.nonzero(erased & (frame == 0))):
        for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= j < H and 0 <= i < W and frame[j, i] not in (0, outline):
                res[y, x] = outline
                break
    return res

class Character:
    """A redraw recipe: donor reference frames (view -> (frames, code, frame, first body row)), the head templates,
    the body repaint."""
    def __init__(self, name, letters, pal, heads, refs, rigid_colours, hair_colours, repaint):
        self.name, self.letters, self.pal, self.heads = name, letters, pal, heads
        self.refs, self.rigid_colours = refs, rigid_colours
        self.hair_colours, self.repaint = hair_colours, repaint
        self._stamps = {}

    def stamp(self, view):
        if view not in self._stamps:
            if view == 'right' and 'right' not in self.heads:
                y0, rows = self.heads['left']
                self._stamps[view] = (y0, mirror(parse(rows, self.letters)))
            else:
                y0, rows = self.heads[view]
                self._stamps[view] = (y0, parse(rows, self.letters))
        return self._stamps[view]

    def ref_frame(self, view):
        frames, code, k, body_top = self.refs[view]
        return frames[k], body_top

    def rigid_mask(self, view, shape):
        f, body_top = self.ref_frame(view)
        m = np.isin(f, list(self.rigid_colours))
        m[body_top:] = False
        big = np.zeros(shape, bool); big[:f.shape[0], :f.shape[1]] = m
        return big

    def classify(self, f, views=None):
        """Best (quality, view, dx, dy) for donor frame f (a 64-px frame is searched over its whole canvas)."""
        res = []
        for v in (views or self.refs):
            ref, _ = self.ref_frame(v)
            big = np.zeros(f.shape, np.uint8); big[:ref.shape[0], :ref.shape[1]] = ref
            pad = 6 if f.shape == ref.shape else f.shape[0] - ref.shape[0] + 4
            m = self.rigid_mask(v, f.shape)
            dx, dy, q = head_fit(big, f, m, pad)
            res.append((round(q, 2), int(round(q * m.sum())), v, dx, dy))
        q, n, v, dx, dy = max(res)               # best fit, then the most matched pixels (a back view has few)
        return q, v, dx, dy

    def frame(self, f, view, dx, dy, edits=None):
        """Redraw one donor frame: repaint the body, erase the donor head, paint the new head, close the outline.
        Erased: pixels of the donor's head where this frame shows the reference head (the rigid face, the visor,
        the hair where it did not move) and every hair-coloured pixel joined to it (the moving strands); kept in
        front of the new head: anything else there (a hand, a Poke Ball, an arm)."""
        ref, body_top = self.ref_frame(view)
        refpad = np.zeros(f.shape, np.uint8); refpad[:ref.shape[0], :ref.shape[1]] = ref
        head_ref = refpad.copy(); head_ref[body_top:] = 0
        hs = np.zeros(f.shape, np.uint8)
        ys, xs = np.nonzero(head_ref)
        y2, x2 = ys + dy, xs + dx
        ok = (y2 >= 0) & (y2 < f.shape[0]) & (x2 >= 0) & (x2 < f.shape[1])
        hs[y2[ok], x2[ok]] = head_ref[ys[ok], xs[ok]]
        hm = hs != 0
        limit = np.zeros(f.shape, bool); limit[:max(0, body_top + dy)] = True
        hairc = np.isin(f, list(self.hair_colours)) & limit
        same = hm & (f == hs) & (f != 0)
        erase = same | grow(same & hairc, hairc) | (hm & hairc)
        erase = grow(erase, hairc)
        out = self.repaint(f, view, body_top + dy)
        out[erase] = 0
        # outline left hanging from the donor's hair: outline pixels with no coloured neighbour any more
        for _ in range(2):
            H, W = out.shape
            for y, x in zip(*np.nonzero((out == 0xF) & limit)):
                nb = [out[j, i] for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= j < H and 0 <= i < W]
                if not any(v not in (0, 0xF) for v in nb):
                    out[y, x] = 0; erase[y, x] = True
        y0, st = self.stamp(view)
        cand = (f != 0) & ~erase & (f != 0xF) & ~((hs != 0) & (f == hs))
        protect = grow(cand & ~hm, cand)            # only what reaches in from outside the head (hand, ball, arm)
        above = protect & limit
        if above.any():                             # repainted as body (a hand above the shoulders)
            out[above] = self.repaint(f, view, 0)[above]
        stamp_at(out, st, dx, y0 + dy, protect)
        out = close_outline(out, erase)
        if edits:
            edits(out)
        return out.astype(np.uint8)

# ---------------------------------------------------------------------------------------------------- Brendan body

def first_row(f, colours, at_least, start):
    for y in range(start, f.shape[0]):
        if np.isin(f[y], list(colours)).sum() >= at_least:
            return y
    return f.shape[0]

def brendan_repaint(f, view, body_top):
    """Nate's outfit by material -> Brendan's: blue jacket -> navy top (its light / mid / dark tones) with red on
    the shoulders and the outer sleeves, white strap and bag -> yellow strap and pack, grey shorts and black
    leggings -> navy trousers, hands -> yellow gloves, red shoes stay red."""
    H, W = f.shape
    yy, xx = np.mgrid[0:H, 0:W]
    body = yy >= body_top
    legs_top = first_row(f, {9}, 2, body_top + 2)
    legs = body & (yy >= legs_top)
    torso = body & ~legs
    cols = np.nonzero((f[body_top:legs_top] != 0).any(axis=0))[0]
    cx = (cols[0] + cols[-1]) / 2 if len(cols) else W / 2 - 0.5
    neck = body & (yy <= body_top + 1) & (abs(xx - cx) <= 3.5)
    T = {1: 9, 2: 5, 3: 8, 4: 8, 5: 6, 6: 0xD, 7: 7, 8: 0xF, 9: 0xE, 0xA: 0xB, 0xB: 0xB, 0xC: 0xA, 0xD: 0xA, 0xE: 0xB,
         0xF: 0xF}
    L = {1: 9, 2: 7, 3: 8, 4: 8, 5: 7, 6: 7, 7: 0xE, 8: 0xF, 9: 0xE, 0xA: 0xB, 0xB: 0xB, 0xC: 0xA, 0xD: 0xE, 0xE: 7,
         0xF: 0xF}
    N = {0xA: 0xD, 0xB: 0xD, 0xC: 0xC, 6: 0xD, 8: 0xF}
    out = f.copy()
    for o in range(16):
        if o in T: out[torso & (f == o)] = T[o]
        if o in L: out[legs & (f == o)] = L[o]
        if o in N: out[neck & (f == o)] = N[o]
    if view in ('up', 'down', 'dtilt'):      # red on the shoulders and down the outer sleeves (Sapphire's trim)
        sides = torso & (abs(xx - cx) >= 4) & (abs(xx - cx) <= 7) & (yy <= body_top + 3)
        out[sides & (f == 7)] = 8
        out[sides & (f == 5)] = 9
    return out


# ---------------------------------------------------------------------------------------------------- May body

def may_repaint(f, view, body_top):
    """Rosa's outfit by material -> May's: white top -> red top (its light and shade), pink bag -> yellow waist
    pack, yellow skirt -> white skirt, leggings -> black bike shorts, shoes -> red and yellow; collar black."""
    H, W = f.shape
    yy, xx = np.mgrid[0:H, 0:W]
    body = yy >= body_top
    _, bottom = SA.figure_rows(f) if f.any() else (0, H - 1)
    feet = body & (yy >= bottom - 1)
    legs_top = first_row(f, {3, 4}, 2, body_top + 2)
    legs = body & (yy >= legs_top) & ~feet
    torso = body & ~legs & ~feet
    T = {0xA: 3, 0xB: 4, 0xC: 5, 5: 0xB, 6: 0xC, 0xD: 0xE, 0xE: 0xE, 8: 0xA, 9: 9, 3: 1, 4: 2, 1: 7, 2: 7, 7: 8, 0xF: 0xF}
    L = {3: 1, 4: 2, 0xD: 0xD, 0xE: 0xE, 0xA: 1, 0xB: 2, 0xC: 0xD, 5: 0xB, 6: 0xC, 8: 0xA, 9: 9, 1: 7, 2: 7, 7: 8, 0xF: 0xF}
    F = {0xC: 3, 0xB: 0xB, 6: 5, 0xD: 0xE, 0xE: 0xE, 5: 4, 0xA: 1, 3: 0xB, 4: 0xC, 0xF: 0xF, 8: 0xA, 9: 9}
    out = f.copy()
    for o in range(16):
        if o in T: out[torso & (f == o)] = T[o]
        if o in L: out[legs & (f == o)] = L[o]
        if o in F: out[feet & (f == o)] = F[o]
    return out

_rosa = {}
def rosa():
    if not _rosa:
        _rosa['f'] = SA.donor(240)[0]
    return _rosa['f']

def may_char():
    fr = rosa()
    refs = {'up': (fr, 240, 0, 20), 'down': (fr, 240, 3, 20), 'left': (fr, 240, 6, 20), 'right': (fr, 240, 9, 20),
            'dtilt': (fr, 240, 15, 19)}
    return Character('may', M_LET, M_PAL, M_HEADS, refs, rigid_colours={5, 6, 0xA, 0xB, 8, 9},
                     hair_colours={1, 2, 7}, repaint=may_repaint)

# ---------------------------------------------------------------------------------------------------- Prof. Birch

P_LET = {'W': 1, 'w': 2, 'g': 3, 'H': 4, 'h': 5, 'b': 6, 'S': 7, 's': 8, 'N': 9, 'n': 0xA, 'Y': 0xB, 'y': 0xC,
         'd': 0xD, 'e': 0xE, 'K': 0xF}
P_PAL = {0: (165, 165, 165), 1: (255, 255, 255), 2: (214, 218, 230), 3: (156, 165, 189), 4: (189, 115, 82),
         5: (123, 74, 57), 6: (90, 57, 41), 7: (255, 230, 205), 8: (230, 186, 148), 9: (74, 82, 90), 0xA: (49, 52, 66),
         0xB: (189, 156, 90), 0xC: (139, 115, 57), 0xD: (90, 57, 41), 0xE: (107, 110, 132),
         0xF: (0, 0, 0)}                                 # the intro picture's colours (IB_PAL)

# Birch's heads on Cedric Juniper's sheet 104 (front = frame 3, back = 0, side = 6): Sapphire's messy red-brown
# hair standing up in tufts, the beard along the jaw and chin, Black 2's face.
P_HEADS = {
    'down': (3, [
        '.............K...K..............',
        '..........K.KhK.KhK.K...........',
        '.........KhKHHhKHHhKhK..........',
        '........KHHHHHHHHHHHHHK.........',
        '........KHHhHHHHHhHHHHhK........',
        '.......KhHHHhHHHHHHhHHhbK.......',
        '.......KhHhbHHbHHbHHbhbbK.......',
        '.......KhbSbSSbSSSbSSbbbK.......',
        '........KbSSSSSSSSSSSSbK........',
        '........KbSSSSSSSSSSSSbK........',
        '........KbSWKSSSSSSKWSbK........',
        '........KbSWKSSSSSSKWSbK........',
        '........KbbSSSSssSSSSbbK........',
        '.........KbbSbbbbbbSbbK.........',
        '.........KbbbbSSSSbbbbK.........',
        '..........KKbbbbbbbbKK..........',
    ]),
    'up': (3, [
        '.............K...K..............',
        '..........K.KhK.KhK.K...........',
        '.........KhKHHhKHHhKhK..........',
        '........KHHHHHHHHHHHHHK.........',
        '........KHHhHHHHHhHHHHhK........',
        '.......KhHHHhHHHHHHhHHhbK.......',
        '.......KhHhhHHhHHhHHhhhbK.......',
        '.......KhhHhhhHhhhHhhhbbK.......',
        '.......KbhhbhhhhhhhhbhbbK.......',
        '.......KsbhhbhhhbhhhbhbsK.......',
        '........KbbhbhhhhhhbhbbK........',
        '........KbbbbbhhhhbbbbbK........',
        '.........KbbbbbbbbbbbbK.........',
        '..........KKssssssssKK..........',
        '............KKKKKKKK............',
    ]),
    'left': (3, [
        '...............K..K.............',
        '............K.KhKKhK............',
        '...........KhKHHhHHhKK..........',
        '..........KHHHHHHHHHHhK.........',
        '.........KHHHHHHHHHhHHhK........',
        '.........KHhHHHHHHHHhHhbK.......',
        '........KHhbHHHHHHhHHhhbK.......',
        '........KHbSbHHHhHHHhhbbK.......',
        '........KbSSSbHHHhhHhhbK........',
        '........KSSSSSbhHHhhhbbK........',
        '........KSKWSSShhssshbbK........',
        '........KSKWSSShbsSsbbK.........',
        '.........SSSSSSbhssbbK..........',
        '.........sbbbSSbhbbbK...........',
        '..........KbbbbbbbbK............',
        '...........KKKKKKKK.............',
    ]),
}

def birch_repaint(f, view, body_top):
    """Cedric's clothes by material -> Birch's: yellow shirt -> white lab coat (open in front over a dark shirt),
    brown trousers -> khaki shorts above bare shins, shoes -> brown sandals."""
    H, W = f.shape
    yy, xx = np.mgrid[0:H, 0:W]
    body = yy >= body_top
    _, bottom = SA.figure_rows(f) if f.any() else (0, H - 1)
    legs_top = first_row(f, {4, 5}, 4, body_top + 3)
    feet = body & (yy >= bottom - 1)
    shins = body & (yy >= bottom - 3) & ~feet
    legs = body & (yy >= legs_top) & ~shins & ~feet
    torso = body & ~legs & ~shins & ~feet
    cols = np.nonzero((f[body_top:legs_top] != 0).any(axis=0))[0]
    cx = (cols[0] + cols[-1]) / 2 if len(cols) else W / 2 - 0.5
    T = {3: 1, 2: 2, 1: 3, 0xE: 9, 4: 0xA, 5: 9, 6: 0xD, 0xD: 3, 0xA: 8, 0xB: 7, 0xC: 7, 7: 5, 8: 4, 0xF: 0xF}
    L = {4: 0xC, 5: 0xB, 6: 0xC, 0xD: 0xB, 0xA: 8, 0xB: 7, 0xC: 7, 0xE: 0xB, 3: 1, 2: 2, 1: 3, 0xF: 0xF}
    SH = {4: 8, 5: 7, 6: 8, 0xD: 7, 0xF: 0xF, 0xA: 8, 0xB: 7, 0xC: 7}
    F = {6: 0xD, 4: 0xD, 5: 0xD, 0xD: 8, 0xF: 0xF, 0xA: 8, 0xB: 7, 0xC: 7}
    out = f.copy()
    for o in range(16):
        if o in T: out[torso & (f == o)] = T[o]
        if o in L: out[legs & (f == o)] = L[o]
        if o in SH: out[shins & (f == o)] = SH[o]
        if o in F: out[feet & (f == o)] = F[o]
    if view in ('down', 'dtilt'):                    # the open coat shows the dark shirt down the middle
        mid = torso & (abs(xx - cx) <= 1.5) & (yy >= body_top + 1) & np.isin(f, [1, 2, 3])
        out[mid] = 9
    return out

_cedric = {}
def cedric():
    if not _cedric:
        _cedric['f'] = SA.donor(104)[0]
    return _cedric['f']

def birch_char():
    fr = cedric()
    refs = {'up': (fr, 104, 0, 19), 'down': (fr, 104, 3, 19), 'left': (fr, 104, 6, 19), 'right': (fr, 104, 9, 19)}
    return Character('birch', P_LET, P_PAL, P_HEADS, refs, rigid_colours={0xA, 0xB, 0xC},
                     hair_colours={5, 6, 7, 8}, repaint=birch_repaint)

# ---------------------------------------------------------------------------------------------------- shape painter
# For the large pictures (battle backs, the intro): regions are laid out as polygons (the drawing's construction
# lines), filled, cel-shaded by Black 2's rule (light from the upper left: a lit rim on the upper-left edges, a shadow
# band along the lower-right edges), outlined (black outside, a darker tone of the lower region on inner edges),
# then finished by hand with ASCII patches.

def poly_mask(shape, pts):
    """Pixels whose centres lie inside the polygon `pts` [(x, y)] (even-odd rule)."""
    H, W = shape
    m = np.zeros(shape, bool)
    n = len(pts)
    for y in range(H):
        cy = y + 0.5
        xs = []
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
            if (y0 <= cy < y1) or (y1 <= cy < y0):
                xs.append(x0 + (cy - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            lo, hi = int(np.ceil(a - 0.5)), int(np.floor(b - 0.5))
            if hi >= lo:
                m[y, max(0, lo):min(W, hi + 1)] = True
    return m

def ellipse_mask(shape, cx, cy, rx, ry):
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1

def edge_dist(mask, dx, dy, k):
    """Pixels of `mask` whose neighbour k steps along (dx, dy) is outside the mask."""
    H, W = mask.shape
    out = np.zeros_like(mask)
    ys, xs = np.nonzero(mask)
    y2, x2 = ys + dy * k, xs + dx * k
    ok = (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
    inside = np.zeros(len(ys), bool)
    inside[ok] = mask[y2[ok], x2[ok]]
    out[ys[~inside], xs[~inside]] = True
    return out

def cel(mask, base, light=None, dark=None, deep=None, lit=1, shade=2, deep_w=1, ldir=(-1, -1)):
    """{index: mask} tones for a region: `lit` px of light along the edges facing the light, `shade` px of dark
    along the edges facing away, `deep_w` px of deep shadow at the very edge facing away."""
    lx, ly = ldir
    out = np.full(mask.shape, -1, np.int16)
    out[mask] = base
    if dark is not None:
        for k in range(1, shade + 1):
            for ddx, ddy in ((-lx, -ly), (-lx, 0), (0, -ly)):
                out[mask & edge_dist(mask, ddx, ddy, k)] = dark
    if deep is not None:
        for k in range(1, deep_w + 1):
            out[mask & edge_dist(mask, -lx, -ly, k)] = deep
    if light is not None:
        for k in range(1, lit + 1):
            for ddx, ddy in ((lx, ly), (0, ly)):
                out[mask & edge_dist(mask, ddx, ddy, k)] = light
    return out

def paint(canvas, tones):
    canvas[tones >= 0] = tones[tones >= 0]

def outline_outside(canvas, figure, colour):
    """The figure's own edge pixels (next to transparent) become `colour`."""
    H, W = canvas.shape
    edge = figure & (edge_dist(figure, 1, 0, 1) | edge_dist(figure, -1, 0, 1) | edge_dist(figure, 0, 1, 1) |
                     edge_dist(figure, 0, -1, 1))
    canvas[edge] = colour
    return edge

def inner_line(canvas, upper, lower, colour):
    """Pixels of `lower` next to `upper` (the region drawn over it) become `colour` (inner contour)."""
    H, W = canvas.shape
    nb = np.zeros_like(upper)
    nb[1:] |= upper[:-1]; nb[:-1] |= upper[1:]; nb[:, 1:] |= upper[:, :-1]; nb[:, :-1] |= upper[:, 1:]
    canvas[lower & ~upper & nb] = colour

def patch(canvas, rows, letters, x0, y0):
    """Hand finishing: ASCII rows over the canvas from (x0, y0); '.' keeps, ' ' keeps, '_' clears."""
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch in '. ':
                continue
            canvas[y0 + j, x0 + i] = 0 if ch == '_' else letters[ch]


# ---------------------------------------------------------------------------------------------------- battle backs

def drop_specks(out, region, min_size=30):
    """Remove small floating bits (left-over donor hair) inside `region`: 8-connected groups of coloured pixels
    smaller than `min_size` that do not reach outside the region."""
    H, W = out.shape
    seen = np.zeros(out.shape, bool)
    for y, x in zip(*np.nonzero(region & (out != 0))):
        if seen[y, x]:
            continue
        comp, stack, leaks = [], [(y, x)], False
        seen[y, x] = True
        while stack:
            j, i = stack.pop(); comp.append((j, i))
            for dj in (-1, 0, 1):
                for di in (-1, 0, 1):
                    jj, ii = j + dj, i + di
                    if 0 <= jj < H and 0 <= ii < W and out[jj, ii] != 0 and not seen[jj, ii]:
                        if not region[jj, ii]:
                            leaks = True; continue
                        seen[jj, ii] = True; stack.append((jj, ii))
        if len(comp) < min_size and not leaks:
            for j, i in comp: out[j, i] = 0

def box(shape, x0, y0, x1, y1):
    m = np.zeros(shape, bool)
    m[max(0, y0):y1, max(0, x0):x1] = True
    return m

def neighbours(mask):
    nb = np.zeros_like(mask)
    nb[1:] |= mask[:-1]; nb[:-1] |= mask[1:]; nb[:, 1:] |= mask[:, :-1]; nb[:, :-1] |= mask[:, 1:]
    return nb

def stamp_head(out, donor, c, fig, x0, y0, allowed, clear_box, hair, outline=1, through=()):
    """Paint head `c` (mask `fig`) with its top-left at (x0, y0) where `allowed`; then clear the rest of the donor's
    hair inside `clear_box`: its hair-coloured pixels and whatever joins them through `through` colours (the hair's
    outline and dark strands), and close the cut with outline."""
    H, W = out.shape
    placed = np.zeros(out.shape, bool)
    for y, x in zip(*np.nonzero(fig)):
        X, Y = x0 + x, y0 + y
        if 0 <= X < W and 0 <= Y < H and allowed[Y, X]:
            out[Y, X] = c[y, x]; placed[Y, X] = True
    a, b, cc, d = clear_box
    zone = box(out.shape, a, b, cc, d)
    seeds = zone & np.isin(donor, list(hair)) & ~placed
    gone = grow(seeds, zone & np.isin(donor, list(set(hair) | set(through))) & ~placed)
    out[gone] = 0
    for _ in range(2):                                    # donor outline that only bordered the old hair
        lone = zone & (out == outline) & ~placed
        coloured = (out != 0) & (out != outline)
        out[lone & ~neighbours(coloured)] = 0
        gone |= lone & ~neighbours(coloured)
    coloured = (out != 0) & (out != outline)
    out[gone & (out == 0) & neighbours(coloured)] = outline
    return placed

def red_trim(out, region, jacket, red, outline=1, d=(0, -1), width=1, dark=None):
    """Sapphire's red stripe: the jacket pixels of `region` just inside its contour on side `d` (the neighbour that
    way is outline or empty); `width` px, the inner one `dark` when given."""
    H, W = out.shape
    dx, dy = d
    src = out.copy()
    hit = np.zeros(out.shape, bool)
    for k in range(width):
        ys, xs = np.nonzero(region & np.isin(src, list(jacket)))
        for y, x in zip(ys, xs):
            j, i = y + dy * (k + 1), x + dx * (k + 1)
            nb = src[j, i] if 0 <= j < H and 0 <= i < W else 0
            if nb in (0, outline):
                out[y, x] = red if (k == 0 or dark is None) else dark
                hit[y, x] = True
    return hit

def draw_pack(out, pts, flap, light, base, dark, outline, metal, front=None, straps=()):
    """Brendan's backpack from its outline polygon: cel-shaded body (lit upper-left rim, dark lower-right band),
    a curved flap seam through the points `flap` (dark line, lit row under it), a small buckle at the flap's middle,
    shoulder straps [(x0, y0, x1, y1)] going up from the top; pixels in `front` (an arm) stay in front."""
    m = poly_mask(out.shape, pts)
    t = cel(m, base, light, dark, None, lit=2, shade=3)
    for (x0, y0), (x1, y1) in zip(flap, flap[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for k in range(n + 1):
            x = int(round(x0 + (x1 - x0) * k / n)); y = int(round(y0 + (y1 - y0) * k / n))
            if m[y, x]:
                t[y, x] = dark
                if y + 1 < out.shape[0] and m[y + 1, x] and t[y + 1, x] == base: t[y + 1, x] = light
    bx, by = flap[len(flap) // 2]
    for dy, row in enumerate(((outline, outline, outline), (metal, metal - 1, outline), (metal, metal, outline))):
        for dx, v in enumerate(row):
            if m[by + dy, bx - 1 + dx]: t[by + dy, bx - 1 + dx] = v
    for x0, y0, x1, y1 in straps:
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for k in range(n + 1):
            x = int(round(x0 + (x1 - x0) * k / n)); y = int(round(y0 + (y1 - y0) * k / n))
            for dx, v in ((-2, outline), (-1, light), (0, base), (1, dark), (2, outline)):
                if t[y, x + dx] < 0 or not m[y, x + dx]:
                    t[y, x + dx] = v
    edge = m & neighbours(~m)
    t[edge] = outline
    keep = t >= 0
    if front is not None:
        keep &= ~front
    out[keep] = t[keep]
    return m


# ---------------------------------------------------------------------------------------------------- Brendan battle back

BB_PAL = {0: (181, 255, 173), 1: (16, 16, 24), 2: (255, 255, 255), 3: (214, 222, 239), 4: (156, 165, 198),
          5: (99, 107, 140), 6: (24, 32, 57), 7: (41, 52, 90), 8: (66, 82, 132), 9: (99, 120, 181), 0xA: (239, 90, 66),
          0xB: (148, 104, 33), 0xC: (255, 214, 90), 0xD: (214, 165, 57), 0xE: (255, 214, 189), 0xF: (206, 148, 123)}
BB_LET = {'K': 1, 'W': 2, 'w': 3, 'g': 4, 'o': 5, 'n': 6, 'N': 7, 'm': 8, 'M': 9, 'R': 0xA, 'r': 0xB, 'Y': 0xC,
          'y': 0xD, 'S': 0xE, 's': 0xF}

def line_px(x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(int(round(x0 + (x1 - x0) * k / n)), int(round(y0 + (y1 - y0) * k / n))) for k in range(n + 1)]

def brendan_back_head():
    """Brendan's head from behind, turned to the right (Sapphire's back picture, frame 0, at Black 2's size): the
    white knit hat over the back of the head with its two points trailing back, the navy front of the hat, black
    hair at the nape, the ear, cheek and the corner of the eye. 48 x 38."""
    sh = (38, 48)
    hat = poly_mask(sh, [(28, 1), (33, 1), (37, 3), (32, 10), (28, 16), (25, 21), (21, 24), (18, 27), (16, 22), (12, 21),
                         (1, 23), (8, 17), (11, 14), (9, 12), (2, 4), (10, 5), (14, 6), (17, 4), (22, 2)])
    cap = poly_mask(sh, [(33, 1), (38, 2), (43, 6), (46, 11), (47, 16), (46, 19), (41, 19), (34, 18), (29, 20), (25, 21),
                         (28, 16), (32, 10), (37, 3)])
    hair = poly_mask(sh, [(25, 21), (30, 19), (35, 19), (36, 26), (34, 31), (30, 34), (26, 33), (22, 29), (20, 25)])
    face = poly_mask(sh, [(34, 18), (41, 19), (47, 18), (47, 22), (46, 28), (44, 32), (41, 35), (36, 37), (31, 36),
                          (30, 34), (33, 30), (35, 26)])
    c = np.zeros(sh, np.int16)
    paint(c, cel(face, 0xE, None, 0xF, None, shade=2))
    paint(c, cel(hair, 6, 7, None, None, lit=1))
    paint(c, cel(hat, 2, None, 3, 4, shade=5, deep_w=1))
    paint(c, cel(cap, 8, 9, 7, 6, lit=1, shade=3, deep_w=1))
    inner_line(c, hat, hair, 1); inner_line(c, cap, hat, 5); inner_line(c, cap | hair | hat, face, 0xF)
    fig = hat | cap | hair | face
    e = outline_outside(c, fig, 1)
    c[e & hat & ~neighbours(cap | hair)] = 5           # white things are outlined in slate (as Black 2's caps)
    for a, b in (((31, 5), (20, 8)), ((20, 8), (14, 12)), ((28, 11), (19, 14)), ((19, 14), (12, 19))):   # knit ribs
        for x, y in line_px(*a, *b):
            if hat[y, x] and c[y, x] == 2: c[y, x] = 3
    patch(c, [                                         # ear, sideburn, cheek and the corner of the eye
        '....................',
        'nnnnnnnnnnnnnnnnnnnK',
        'NnnnnnnNNNnnnnmKKKKK',
        'nnnNNNNnnKKKKNnsSWNK',
        'nnNNNNNnnKsSsNnsSWnK',
        'nNNNNNnnnKsSSNsSSSSK',
        'nNNNNnnnnKssSnSSSSSK',
        'NNNNnnnnnKsSssSSSSSK',
        '.........nKsKsSSSSSK',
        '.........nnKsSSSSSSK',
        '.........nnnsSSSSSsK',
        '.........nnnsSSSSsK_',
        '.........nnsSSSSssK_',
        '.........nsSSSSssK__',
    ], BB_LET, 28, 17)
    return c, fig

# Nate's battle back (a/0/7/2 sprite 0; parts sheet 256 x 128): cells 0 = standing turned right (idle, with arm
# cell 1 hanging), 2 and 3 = the arm raising the ball, 4 = the wind-up seen from behind, 5 = the throw.
NATE_BACK = dict(
    jacket={8: 8, 9: 7, 0xA: 6, 7: 0xA, 1: 1, 2: 9, 3: 9, 4: 8, 5: 7},          # blue jacket -> navy, cyan -> red trim
    pants={3: 9, 4: 8, 5: 7, 2: 9, 6: 6, 0xE: 8, 0xF: 7, 0xA: 6, 8: 7, 9: 6, 7: 7},   # grey shorts -> navy trousers
    sleeve={0xB: 8, 0xC: 7, 0xE: 7, 0xF: 6, 5: 7, 6: 6},                        # bare forearms -> long navy sleeves
    glove={0xB: 0xC, 0xC: 0xD, 0xE: 0xD, 0xF: 0xB, 5: 5, 6: 6, 2: 2, 3: 3, 4: 4, 0xA: 6, 8: 8, 9: 7},   # yellow gloves
    face={0xB: 0xE, 0xC: 0xF, 0xE: 0xF, 0xF: 0xF, 6: 6, 5: 0xF},
    pants_boxes=[(0, 98, 48, 128), (48, 96, 112, 128), (112, 94, 200, 128)],
    hand_boxes=[(216, 8, 237, 28), (206, 78, 228, 97), (232, 108, 256, 128), (78, 9, 102, 26), (52, 86, 64, 98),
                (112, 72, 128, 92), (177, 96, 200, 113)],
    face_boxes=[(24, 40, 48, 60), (70, 36, 100, 56), (160, 52, 195, 72)],
    heads=[((0, 18), (0, 0, 48, 64), (0, 14, 48, 52), None),                     # (top-left, cell box, clear, arm)
           ((50, 18), (48, 0, 112, 128), (50, 14, 100, 50), (92, 8, 112, 52)),
           ((145, 30), (112, 16, 200, 128), (144, 26, 192, 64), None)],
    hair={6, 0xD, 0xE, 0xF},
)

def brendan_back():
    """Brendan's battle back (a/0/7/2 sprite 0, MCSS) on Nate's parts and throw animation: Sapphire's back
    picture redrawn at Black 2's size: the white knit hat with its points, the navy outfit with red trim on the
    shoulders and sleeves, the big yellow backpack, yellow gloves, navy trousers."""
    parts, static, rgbs, cells, meta = SA.tr_donor('back', 0)
    d = parts.astype(np.int16); sh = d.shape
    out = d.copy()
    N = NATE_BACK
    def apply(mask, table):
        for o, n in table.items(): out[mask & (d == o)] = n
    def boxes(lst):
        m = np.zeros(sh, bool)
        for b in lst: m |= box(sh, *b)
        return m
    pants, hands, faces = boxes(N['pants_boxes']), boxes(N['hand_boxes']), boxes(N['face_boxes'])
    apply(~pants & ~hands, N['jacket'])
    apply(pants, N['pants'])
    apply(~faces & ~hands & ~pants, N['sleeve'])
    apply(hands, N['glove'])
    apply(faces, N['face'])
    c, fig = brendan_back_head()
    headish = np.isin(d, [0, 1, 6, 0xD, 0xE, 0xF]) | (faces & np.isin(d, [0xB, 0xC]))
    for (x0, y0), cb, clear, arm in N['heads']:
        allowed = headish & box(sh, *cb)
        if arm: allowed &= ~box(sh, *arm)
        stamp_head(out, d, c, fig, x0, y0, allowed, clear, N['hair'], through={1, 0xA})
    left = box(sh, 144, 50, 196, 72) & np.isin(d, [0xB, 0xC, 2, 3, 4, 5, 0xD]) & (out != 0) & \
        ~np.isin(out, [1, 2, 3, 4, 5, 6, 7, 8, 0xE, 0xF])
    out[left] = 0
    for cb in ((0, 0, 48, 128), (48, 0, 112, 128), (112, 16, 200, 128)):
        drop_specks(out, box(sh, *cb))
    J = {6, 7, 8}                                          # red trim along the shoulders and sleeves
    for b, dd in (((14, 52, 32, 66), (0, -1)), ((232, 62, 256, 96), (-1, 0)), ((200, 84, 234, 126), (-1, 0)),
                  ((216, 26, 256, 56), (0, -1)), ((216, 26, 232, 56), (-1, 0)), ((92, 20, 112, 60), (1, 0)),
                  ((48, 56, 70, 100), (-1, 0)), ((112, 60, 165, 84), (0, -1)), ((176, 62, 200, 104), (1, 0))):
        red_trim(out, box(sh, *b), J, 0xA, d=dd)
    arm4l = (out != 0) & box(sh, 46, 56, 64, 100) & ~box(sh, 58, 56, 64, 70)
    draw_pack(out, [(6, 66), (12, 62), (19, 63), (22, 70), (22, 92), (18, 97), (9, 97), (5, 92)],
              [(6, 74), (13, 72), (21, 74)], 0xC, 0xD, 0xB, 1, 4)
    draw_pack(out, [(60, 64), (66, 60), (80, 59), (87, 63), (89, 86), (85, 96), (64, 97), (59, 90)],
              [(60, 72), (72, 70), (88, 72)], 0xC, 0xD, 0xB, 1, 4, front=arm4l, straps=[(66, 60, 64, 54), (82, 59, 86, 53)])
    draw_pack(out, [(140, 74), (150, 67), (163, 64), (171, 67), (174, 84), (168, 93), (147, 97), (140, 90)],
              [(141, 80), (156, 75), (173, 76)], 0xC, 0xD, 0xB, 1, 4, straps=[(152, 66, 150, 62), (167, 65, 170, 61)])
    return parts, rgbs, out.astype(np.uint8), cells

_nate = {}
def nate():
    if not _nate:
        _nate['f'] = SA.donor(231)[0]
    return _nate['f']

def brendan_char():
    fr = nate()
    refs = {'up': (fr, 231, 0, 20), 'down': (fr, 231, 3, 20), 'left': (fr, 231, 6, 20), 'right': (fr, 231, 9, 20),
            'dtilt': (fr, 231, 15, 19)}
    return Character('brendan', B_LET, B_PAL, B_HEADS, refs, rigid_colours={1, 3, 4, 0xA, 0xC},
                     hair_colours={6, 8, 0xB}, repaint=brendan_repaint)

def build_sheet(ch, code, overrides=None, log=None):
    frames, rgbs, meta = SA.donor(code)
    new = []
    for k, f in enumerate(frames):
        q, v, dx, dy = ch.classify(f)
        if overrides and k in overrides:
            v, dx, dy = overrides[k][:3]
        if log is not None: log.append((code, k, v, dx, dy, round(q, 2)))
        new.append(ch.frame(f, v, dx, dy))
    return frames, rgbs, meta, new

# ---------------------------------------------------------------------------------------------------- Brendan battle front

BF_PAL = {**BB_PAL, 0: (74, 206, 57), 0xB: (165, 41, 41)}       # dark red instead of the pack's dark gold

BF_HEADS = {   # 24 wide; 'front' sits on Nate's head (static picture: top-left (27, 8)), 'bow' on his bowed head
    'front': [
        '...............KK.......',
        '..............oWgo......',
        '.......ooooo.oWWgo......',
        '.....ooWWWWWooWwwgo.....',
        '....oWWWWWWWWWWwwwgo....',
        '...oWWWWWWWWWWwwwwggo...',
        '..oWWWwWWWWWwWWwwwgggo..',
        '..KwWWwWWWWWwWwwgwgggK..',
        '.KnnnnnnnnnnnnnnnnnnnnK.',
        '.KnnnnnRRRRnnRRRRnnnnnK.',
        '.KNnnnnnnrrrrrrnnnnnnNK.',
        '.KmNnssssssssssssssnNmK.',
        'KmNNSSSSSSSSSSSSSSSSNNmK',
        'KNmNSKKKSSSSSSSSKKKSNmNK',
        '.KNNSWKNSSSSSSSSWKNSNNK.',
        '.KNmSWKNSSSSSSSSWKNSmNK.',
        '..KNSSSSSSSSSSSSSSSSNK..',
        '..KNsSSSSSSSSSSSSSSsNK..',
        '...KKsSSSSSKKSSSSSsKK...',
        '.....KKssSSSSSSssKK.....',
        '.......KKKKKKKKKK.......',
    ],
    'bow': [
        '..........KK............',
        '.........oWgo...........',
        '......oooWWgoooo........',
        '....ooWWWWWWWWWWoo......',
        '...oWWWWWWWWWWWWwwo.....',
        '..oWWWWWWWWWWWWwwwgo....',
        '.oWWWwWWWWWwWWWwwwggo...',
        '.oWWWwWWWWWwWWwwwwggo...',
        'KwWWWwWWWWwWWwwwgwgggK..',
        'KwwWwwWWWwwWwwwwgwgggK..',
        'KggwgwwwwgwwwwwgggggoK..',
        'KnnnnnnnnnnnnnnnnnnnnK..',
        'KnnnnnRRRRnnRRRRnnnnnK..',
        '.KNnnnnnrrrrrrnnnnnNK...',
        '..KNNssssssssssssNNK....',
        '...KKKsSSSSSSSSsKKK.....',
        '......KKKKKKKKKK........',
    ],
}

# Nate's battle front (a/0/7/1 sprite 0): parts sheet cells by what they show
NATE_FRONT_CELLS = dict(head=[1, 17], bow=[27], torso=[2], sleeve=[3, 5, 19, 21, 28, 18], strap=[7, 8, 9],
                        bag=[10, 32, 35, 29], shorts=[11, 14, 23, 25], legs=[12, 15, 24, 26, 33, 36],
                        shoes=[13, 16, 34], arm=[4, 6, 20, 22, 30, 31])
NATE_FRONT_HANDS = [(0, 84, 14, 92), (0, 59, 16, 72), (64, 45, 80, 56), (48, 45, 64, 56), (96, 117, 112, 128),
                    (112, 44, 128, 56)]                                   # below the wrist (wristband or bend)
NATE_FRONT_STATIC = dict(head=(0, 0, 80, 28), bag=(45, 42, 60, 62), shorts=(20, 44, 52, 62), legs=(20, 60, 60, 71),
                         shoes=(18, 70, 62, 80), hands=[(25, 42, 34, 50), (41, 43, 50, 51)],
                         arm=[(22, 33, 34, 50), (40, 37, 56, 51)])
_NF0 = {0xF: 1, 0xE: 6, 8: 1, 7: 0xF, 9: 0xF, 0xA: 0xE}        # outline, near-black, skin: same in every part
NF = dict(   # Nate's front colours (a/0/7/1 #0 palette) -> Brendan's, by part
    jacket={**_NF0, 4: 8, 5: 7, 6: 6, 3: 6, 0xB: 0xC, 0xC: 0xD, 1: 0xC, 0xD: 7, 2: 0xA},
    strap={**_NF0, 0xB: 0xC, 0xC: 0xD, 1: 0xC, 0xD: 0xD, 6: 6, 4: 8, 5: 7, 3: 6},
    bag={**_NF0, 1: 0xC, 0xB: 0xC, 0xC: 0xD, 0xD: 0xD, 0xE: 6, 3: 0xA, 6: 6, 4: 8, 5: 7, 2: 0xA},
    shorts={**_NF0, 1: 9, 0xB: 9, 0xC: 8, 0xD: 7, 0xE: 6, 6: 6, 3: 8, 4: 8, 5: 7},
    legs={**_NF0, 0xE: 7, 6: 6, 3: 8, 0xD: 7, 0xC: 8, 1: 9, 4: 8, 5: 7},
    shoes={**_NF0, 2: 0xA, 0xB: 2, 0xC: 3, 1: 3, 0xD: 5, 0xE: 6, 6: 6, 7: 0xB, 8: 1},
    arm={**_NF0, 0xA: 8, 9: 7, 7: 6, 8: 1, 2: 0xA, 0xB: 0xC, 0xC: 0xD, 4: 8, 5: 7, 6: 6},   # bare forearms -> sleeves
    cord={**_NF0, 0xB: 8, 1: 8, 0xC: 7, 0xD: 7, 6: 6, 4: 8, 5: 7},          # Nate's drawstrings: gone into the trousers
    glove={**_NF0, 0xA: 0xC, 9: 0xD, 7: 0xD, 8: 1, 2: 0xA, 0xB: 0xC, 0xC: 0xD, 0xD: 6, 4: 8, 5: 7, 6: 6},
)

_last_labels = {}

def label_still(parts, still, cells, cats, min_q=0.45):
    """Which part of the body each pixel of the still picture is: every cell named in `cats` ({cell: category}) is
    matched into the still (best offset, exact colours); matched pixels take its category (better matches first),
    the rest the category of their nearest labelled neighbour. Returns an int array (-1 = empty)."""
    lab = np.full(still.shape, -1, np.int16)
    found = []
    for ci, cat in cats.items():
        x0, y0, x1, y1 = SA.cell_box(cells[ci])
        sub = parts[y0:y1, x0:x1]
        ys, xs = np.nonzero(sub)
        best = (0, 0, 0)
        H, W = still.shape
        for dy in range(-sub.shape[0], H):
            for dx in range(-sub.shape[1], W):
                y2, x2 = ys + dy, xs + dx
                ok = (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
                if ok.sum() < len(ys) * 0.5:
                    continue
                q = (still[y2[ok], x2[ok]] == sub[ys[ok], xs[ok]]).sum() / len(ys)
                if q > best[0]:
                    best = (q, dx, dy)
        if best[0] >= min_q:
            found.append((best[0], ci, cat, best[1], best[2], ys, xs, sub))
    for q, ci, cat, dx, dy, ys, xs, sub in sorted(found, key=lambda t: -t[0]):
        y2, x2 = ys + dy, xs + dx
        ok = (y2 >= 0) & (y2 < still.shape[0]) & (x2 >= 0) & (x2 < still.shape[1])
        y2, x2, ys2, xs2 = y2[ok], x2[ok], ys[ok], xs[ok]
        hit = (still[y2, x2] == sub[ys2, xs2]) & (lab[y2, x2] < 0)
        lab[y2[hit], x2[hit]] = cat
    todo = (still != 0) & (lab < 0)
    while todo.any():
        grown = False
        for y, x in zip(*np.nonzero(todo)):
            for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= j < lab.shape[0] and 0 <= i < lab.shape[1] and lab[j, i] >= 0:
                    lab[y, x] = lab[j, i]; grown = True; break
        todo = (still != 0) & (lab < 0)
        if not grown:
            break
    return lab

def repaint_by_labels(img, lab, maps):
    out = img.astype(np.int16).copy()
    for cat, table in maps.items():
        for o, n in table.items():
            out[(lab == cat) & (img == o)] = n
    return out

def tr_front(side_sprite, cats, maps, heads, head_cat, pal_extra=None):
    """A battle front redrawn on its donor's parts: cells by category (`cats`), each category's colours mapped
    to the new outfit (`maps`), the head cells cleared and the new heads stamped [(stamp, cell or 'still', x, y)];
    the still picture and the whole-figure cell are labelled from the cells (label_still)."""
    side, s = side_sprite
    parts, static, rgbs, cells, meta = SA.tr_donor(side, s)
    sh = parts.shape
    labp = np.full(sh, -1, np.int16)
    for ci, cat in cats.items():
        for x, y, w, h, tx, ty, hf, vf in cells[ci]:
            labp[ty:ty + h, tx:tx + w] = cat
    figci = sprites.whole_figure_cell(cells)
    fx0, fy0, fx1, fy1 = SA.cell_box(cells[figci])
    off = SA.figure_offset(parts, static, cells)
    labs = label_still(parts, static, cells, {ci: c for ci, c in cats.items() if ci < 17 or s != 0})
    if off:
        sub = labp[fy0:fy1, fx0:fx1]
        for y in range(fy0, fy1):
            for x in range(fx0, fx1):
                sy, sx = y - off[1], x - off[0]
                labp[y, x] = labs[sy, sx] if 0 <= sy < 80 and 0 <= sx < 80 else -1
    labp[parts == 0] = -1
    if 'hand' in maps.get('_split', {}):                  # the lowest rows of each arm piece are the hand
        arm_cat, hand_cat, rows = maps['_split']['hand']
        for lab in (labp, labs):
            comp_all = lab == arm_cat
            seen = np.zeros(lab.shape, bool)
            for y, x in zip(*np.nonzero(comp_all)):
                if seen[y, x]:
                    continue
                comp = grow(np.pad(np.zeros((0, 0), bool), 0) if False else (np.arange(lab.size).reshape(lab.shape) == y * lab.shape[1] + x), comp_all)
                seen |= comp
                ys = np.nonzero(comp.any(axis=1))[0]
                lab[comp & (np.arange(lab.shape[0])[:, None] > ys.max() - rows)] = hand_cat
    maps = {k: v for k, v in maps.items() if k != '_split'}
    _last_labels['parts'] = labp
    out = repaint_by_labels(parts, labp, maps)
    sout = repaint_by_labels(static, labs, maps)
    for st, where, x0, y0 in heads:
        if where == 'still':
            tgt, lab = sout, labs
            stamp_list = [(tgt, lab, x0, y0)]
            if off:
                stamp_list.append((out, labp, x0 + off[0], y0 + off[1]))
        else:
            cx0, cy0, cx1, cy1 = SA.cell_box(cells[where])
            stamp_list = [(out, labp, x0, y0)]
        for tgt, lab, X, Y in stamp_list:
            if where != 'still':
                clear = box(sh, cx0, cy0, cx1, cy1) & (lab == head_cat)
            else:
                clear = (lab == head_cat)
                if tgt is out:
                    clear &= box(sh, fx0, fy0, fx1, fy1)
            tgt[clear] = 0
            stamp_at(tgt, st, X, Y)
    return parts, static, rgbs, cells, out.astype(np.uint8), sout.astype(np.uint8), labs

NF_CATS = {1: 'head', 17: 'head', 27: 'head', 2: 'torso', 7: 'strap', 8: 'cord', 9: 'cord', 10: 'bag', 32: 'bag',
           35: 'bag', 29: 'bag', 11: 'shorts', 14: 'shorts', 23: 'shorts', 25: 'shorts', 12: 'legs', 15: 'legs',
           24: 'legs', 26: 'legs', 33: 'legs', 36: 'legs', 13: 'shoes', 16: 'shoes', 34: 'shoes', 3: 'sleeve',
           5: 'sleeve', 19: 'sleeve', 21: 'sleeve', 28: 'sleeve', 18: 'sleeve', 4: 'arm', 6: 'arm', 20: 'arm',
           22: 'arm', 30: 'arm', 31: 'arm'}
CATN = {k: i for i, k in enumerate(['head', 'torso', 'strap', 'bag', 'shorts', 'legs', 'shoes', 'sleeve', 'arm', 'hand',
                                     'cord'])}

def brendan_front():
    """Brendan's battle front (a/0/7/1 sprite 0: the rival battles and the Hall of Fame) on Nate's parts and
    animation, in Sapphire's design: the white knit hat with its point, black band with the red marks, navy hair,
    navy top with red trim, yellow strap and hip bag (Nate's messenger bag), yellow gloves, navy trousers."""
    cats = {ci: CATN[c] for ci, c in NF_CATS.items()}
    arm = NF['arm']
    maps = {CATN['torso']: NF['jacket'], CATN['sleeve']: NF['jacket'], CATN['strap']: NF['strap'],
            CATN['bag']: NF['bag'], CATN['shorts']: NF['shorts'], CATN['legs']: NF['legs'], CATN['shoes']: NF['shoes'],
            CATN['arm']: arm, CATN['hand']: NF['glove'], CATN['head']: {}, CATN['cord']: NF['cord'],
            '_split': {'hand': (CATN['arm'], CATN['hand'], 7)}}
    front = parse(BF_HEADS['front'], BB_LET); bow = parse(BF_HEADS['bow'], BB_LET)
    heads = [(front, 'still', 27, 8), (front, 1, 5, 5), (front, 17, 36, 6), (bow, 27, 101, 5)]
    parts, static, rgbs, cells, out, sout, labs = tr_front(('front', 0), cats, maps, heads, CATN['head'])
    labp = _last_labels['parts']
    for o, lab in ((out, labp), (sout, labs)):           # Sapphire's red trim: shoulders and outer sleeves
        top = np.isin(lab, [CATN['torso'], CATN['sleeve']])
        red_trim(o, top, {6, 7, 8}, 0xA, d=(0, -1))
        red_trim(o, lab == CATN['sleeve'], {6, 7, 8}, 0xA, d=(-1, 0))
        red_trim(o, lab == CATN['sleeve'], {6, 7, 8}, 0xA, d=(1, 0))
    return parts, static, rgbs, cells, out, sout

# ---------------------------------------------------------------------------------------------------- May battle front

MF_PAL = {0: (90, 189, 82), 1: (16, 16, 16), 2: (255, 255, 255), 3: (206, 206, 222), 4: (140, 140, 156),
          5: (239, 74, 66), 6: (189, 41, 49), 7: (123, 24, 33), 8: (189, 132, 90), 9: (140, 90, 57),
          0xA: (90, 57, 41), 0xB: (255, 214, 189), 0xC: (222, 156, 123), 0xD: (255, 214, 82), 0xE: (198, 148, 41),
          0xF: (49, 49, 57)}
MF_LET = {'K': 1, 'W': 2, 'w': 3, 'g': 4, 'R': 5, 'r': 6, 'd': 7, 'H': 8, 'h': 9, 'b': 0xA, 'S': 0xB, 's': 0xC,
          'Y': 0xD, 'y': 0xE, 'n': 0xF}
MF_HEAD = [    # 24 x 24, the head cell box (still: top-left (30, 10))
    '........................',
    '.........KKKKKK.........',
    '.......KKRRRRRRKK.......',
    '......KRRRRRRRRRrK......',
    '.....KRRRRRRRRRRrrK.....',
    '....KRRRRRRRRRRRRrrK....',
    '....KWWWWWWWWWWWWWwK....',
    '...KrRRRRRRRRRRRRRrrK...',
    '...KhrrrrrrrrrrrrrrdK...',
    '..KHhHHhHHHhHHHhHHhhbK..',
    '..KHHhHSHhSSSSHhSHhHbK..',
    '..KHhbSSSSSSSSSSSSShbK..',
    '..KHbKSKKSSSSSSKKSKbhK..',
    '..KhbSSWnSSSSSSWnSSbhK..',
    '..KhbSSWnSSSSSSWnSSbhK..',
    '..KhbsSSSSSSSSSSSSsbhK..',
    '.KHhbKsSSSSrrSSSSsKbhHK.',
    'KHHhhbKsSSSSSSSSsKbhhHHK',
    'KHhhhbbKKsssssKKbbhhhhHK',
    'KhhbbKK..KKKKK..KKbbhhhK',
    '.KbbK..............KbbK.',
    '..KK................KK..',
    '........................',
    '........................',
]
MF_KNOT = [    # 16 x 16, the bun cell at the head's left (still: top-left (25, 12)): the bandana's knot
    '................',
    '.KKK............',
    'KRRrK..KK.......',
    'KRrrrKKRrK......',
    '.KrrdRRrrK......',
    '..KKdRRdK.......',
    '...KrrdK........',
    '....KKK.........',
]
_MF0 = {0xB: 1}                                           # Rosa's black outline
MFM = dict(     # Rosa's front colours (a/0/7/1 #1) -> May's, by part
    torso={**_MF0, 0xF: 5, 0xE: 6, 0xD: 7, 5: 0xF, 4: 1, 1: 1, 0xC: 1, 9: 0xC, 0xA: 0xB, 8: 7, 7: 0xC, 2: 0xA, 3: 9,
           6: 0xD},
    sleeve={**_MF0, 0xF: 5, 0xE: 5, 0xD: 6, 0xC: 7, 1: 1, 8: 7, 9: 0xC, 0xA: 0xB, 5: 5, 4: 6},
    arm={**_MF0, 0xA: 0xB, 9: 0xC, 8: 0xC, 7: 0xC, 1: 1, 0xE: 5, 0xD: 6, 0xF: 5, 5: 5, 4: 6},
    glove={**_MF0, 0xA: 0xF, 9: 0xF, 8: 1, 7: 4, 1: 1, 0xE: 2, 0xD: 3, 0xF: 2, 5: 5, 4: 6},
    bag={**_MF0, 5: 0xD, 4: 0xE, 0xF: 0xD, 0xE: 0xD, 0xD: 0xE, 8: 0xE, 1: 1, 0xC: 1, 3: 0xE, 2: 0xA, 9: 0xC, 0xA: 0xB},
    skirt={**_MF0, 6: 2, 7: 3, 8: 4, 0xC: 1, 1: 1, 2: 4, 3: 4, 0xF: 2, 0xE: 3, 0xD: 4},
    shorts={**_MF0, 0xC: 0xF, 0xD: 4, 4: 0xF, 5: 0xF, 1: 1, 0xE: 4},
    shin={**_MF0, 0xC: 0xB, 0xD: 0xC, 4: 0xC, 5: 0xB, 1: 1, 0xE: 0xB},
    sock={**_MF0, 0xC: 0xF, 0xD: 4, 4: 0xF, 5: 0xF, 1: 1, 0xE: 4},
    shoes={**_MF0, 0xF: 2, 0xE: 5, 0xD: 6, 6: 0xD, 7: 0xE, 4: 6, 5: 5, 1: 1, 0xC: 0xF, 3: 4},
)
RF_CATS = {4: 'head', 5: 'head', 29: 'head', 0: 'bun', 2: 'knot', 1: 'tail', 3: 'tail', 20: 'tail', 6: 'torso',
           8: 'sleeve', 21: 'sleeve', 7: 'arm', 9: 'arm', 22: 'arm', 23: 'arm', 30: 'arm', 10: 'bag', 11: 'skirt',
           15: 'skirt', 12: 'legs', 13: 'legs', 16: 'legs', 17: 'legs', 24: 'legs', 25: 'legs', 26: 'legs',
           27: 'legs', 31: 'legs', 14: 'shoes', 18: 'shoes', 28: 'shoes'}
MCAT = {k: i for i, k in enumerate(['head', 'bun', 'knot', 'tail', 'torso', 'sleeve', 'arm', 'hand', 'bag', 'skirt',
                                    'legs', 'shin', 'sock', 'shoes'])}

def split_rows(lab, cat, new_cat, from_top=None, from_bottom=None):
    """Per connected piece of `cat`: rows from_top..from_bottom counted from its top row (or the last
    `from_bottom` rows) become `new_cat`."""
    comp_all = lab == cat
    seen = np.zeros(lab.shape, bool)
    H, W = lab.shape
    for y, x in zip(*np.nonzero(comp_all)):
        if seen[y, x]:
            continue
        seed = np.zeros(lab.shape, bool); seed[y, x] = True
        comp = grow(seed, comp_all); seen |= comp
        ys = np.nonzero(comp.any(axis=1))[0]
        rows = np.arange(H)[:, None]
        if from_top is not None:
            lab[comp & (rows >= ys.min() + from_top) & (rows <= ys.max() - (from_bottom or 0))] = new_cat
        elif from_bottom is not None:
            lab[comp & (rows > ys.max() - from_bottom)] = new_cat

def may_front():
    """May's battle front (a/0/7/1 sprite 1: rival battles, Hall of Fame) on Rosa's parts and animation, in
    Sapphire's design: red bandana with the white stripe and its knot, brown hair flaring at the sides (Rosa's
    buns and twin tails go), red top with a dark collar, yellow waist pack (Rosa's bag), white skirt, black bike
    shorts, bare shins, dark socks, red-and-yellow shoes, black gloves."""
    parts, static, rgbs, cells, meta = SA.tr_donor('front', 1)
    sh = parts.shape
    labp = np.full(sh, -1, np.int16)
    for ci, cat in RF_CATS.items():
        for x, y, w, h, tx, ty, hf, vf in cells[ci]:
            labp[ty:ty + h, tx:tx + w] = MCAT[cat]
    figci = sprites.whole_figure_cell(cells)
    fx0, fy0, fx1, fy1 = SA.cell_box(cells[figci])
    off = SA.figure_offset(parts, static, cells)
    labs = label_still(parts, static, cells, {ci: MCAT[c] for ci, c in RF_CATS.items()})
    for y in range(fy0, fy1):
        for x in range(fx0, fx1):
            sy, sx = y - off[1], x - off[0]
            labp[y, x] = labs[sy, sx] if 0 <= sy < 80 and 0 <= sx < 80 else -1
    labp[parts == 0] = -1
    for lab in (labp, labs):
        split_rows(lab, MCAT['arm'], MCAT['hand'], from_bottom=6)
        split_rows(lab, MCAT['legs'], MCAT['shin'], from_top=6, from_bottom=2)
        split_rows(lab, MCAT['legs'], MCAT['sock'], from_bottom=2)
    maps = {MCAT[k]: v for k, v in MFM.items() if k in MCAT}
    maps[MCAT['legs']] = MFM['shorts']; maps[MCAT['hand']] = MFM['glove']
    out = repaint_by_labels(parts, labp, maps)
    sout = repaint_by_labels(static, labs, maps)
    gone = [MCAT['head'], MCAT['bun'], MCAT['knot'], MCAT['tail']]
    out[np.isin(labp, gone)] = 0
    sout[np.isin(labs, gone)] = 0
    head, knot = parse(MF_HEAD, MF_LET), parse(MF_KNOT, MF_LET)
    for ci in (4, 5, 29):
        x0, y0, _, _ = SA.cell_box(cells[ci]); stamp_at(out, head, x0, y0)
    x0, y0, _, _ = SA.cell_box(cells[2]); stamp_at(out, knot, x0, y0)
    stamp_at(sout, knot, 25, 12); stamp_at(sout, head, 30, 10)
    stamp_at(out, knot, 25 + off[0], 12 + off[1]); stamp_at(out, head, 30 + off[0], 10 + off[1])
    for o in (out, sout):
        drop_specks(o, np.ones(o.shape, bool), 4)
    return parts, static, rgbs, cells, out.astype(np.uint8), sout.astype(np.uint8)

# ---------------------------------------------------------------------------------------------------- May battle back

MB_PAL = {0: (255, 132, 255), 1: (255, 222, 198), 2: (255, 255, 255), 3: (239, 74, 66), 4: (189, 41, 49),
          5: (115, 24, 33), 6: (49, 49, 57), 7: (173, 173, 189), 8: (189, 132, 90), 9: (140, 90, 57), 0xA: (90, 57, 41),
          0xB: (240, 186, 156), 0xC: (206, 148, 123), 0xD: (255, 214, 82), 0xE: (198, 148, 41), 0xF: (16, 16, 16)}
ROSA_BACK = dict(
    body={1: 1, 0xA: 0xC, 2: 3, 5: 4, 6: 3, 8: 5, 9: 4, 3: 6, 4: 0xF, 7: 0xD, 0xD: 4, 0xE: 6, 0xF: 0xF,
          0xB: 9, 0xC: 0xA},
    skirt={7: 2, 9: 2, 0xA: 7, 8: 7, 5: 7, 2: 2, 6: 2, 1: 2, 0xB: 7, 0xC: 6, 0xE: 6, 0xF: 0xF, 0xD: 4, 3: 6, 4: 0xF},
    glove={1: 6, 0xA: 0xF, 2: 2, 8: 7, 9: 7, 0xD: 3, 3: 3, 4: 4, 5: 7, 6: 2, 0xB: 0xF, 0xC: 0xF, 0xE: 0xF, 0xF: 0xF,
           7: 2},
    skirt_boxes=[(0, 96, 48, 116), (48, 90, 120, 112), (120, 92, 208, 112)],
    hand_boxes=[(228, 104, 256, 128), (216, 80, 234, 99), (236, 8, 256, 30), (84, 10, 104, 30), (120, 74, 140, 95),
                (186, 96, 204, 114)],
    heads=[((-3, 26), (0, 24, 48, 128), (20, 44)), ((59, 26), (48, 8, 120, 128), (84, 44)),
           ((153, 38), (120, 32, 208, 128), (178, 56))],
)

MB_LET = {'S': 1, 'W': 2, 'R': 3, 'r': 4, 'd': 5, 'n': 6, 'w': 7, 'H': 8, 'h': 9, 'b': 0xA, 'B': 0xB, 's': 0xC,
          'Y': 0xD, 'y': 0xE, 'K': 0xF}

def may_back_head():
    """May's head from behind, turned right (Sapphire's back picture, frame 0, redrawn at Black 2's head size,
    47 x 35): the red bandana fitted over the head like cloth (folds running from the knot, the white panel at the
    front), the knot's two tails standing out at the back, brown hair showing below it and a lock in front of the
    ear, the cheek."""
    sh = (35, 47)
    band = poly_mask(sh, [(11, 21), (10, 14), (12, 8), (17, 3), (24, 1), (31, 1), (37, 4), (41, 9), (43, 15), (43, 19),
                          (39, 19), (34, 18), (28, 19), (22, 21), (16, 22)])
    tail1 = poly_mask(sh, [(13, 10), (8, 5), (3, 2), (0, 4), (2, 9), (7, 12), (12, 13)])
    tail2 = poly_mask(sh, [(12, 15), (6, 15), (1, 17), (1, 21), (5, 22), (10, 19), (13, 18)])
    knot = ellipse_mask(sh, 12.5, 13.5, 3.2, 3.6)
    hair = poly_mask(sh, [(10, 19), (16, 22), (22, 21), (28, 19), (34, 18), (35, 24), (33, 30), (28, 33), (21, 34),
                          (14, 32), (8, 33), (4, 31), (7, 27), (9, 23)]) & ~band
    face = poly_mask(sh, [(34, 18), (39, 19), (43, 19), (46, 21), (46, 25), (45, 29), (42, 32), (37, 34), (32, 33),
                          (31, 30), (34, 26)]) & ~band
    lock = poly_mask(sh, [(33, 18), (38, 19), (39, 25), (37, 31), (34, 27)]) & ~band
    c = np.zeros(sh, np.int16)
    paint(c, cel(face, 1, None, 0xB, None, shade=2))
    paint(c, cel(hair | lock, 9, 8, 0xA, None, lit=1, shade=2))
    paint(c, cel(tail1 | tail2, 3, None, 4, 5, shade=2))
    paint(c, cel(band, 3, None, 4, 5, shade=3, deep_w=1))
    paint(c, cel(knot, 4, 3, 5, None, lit=1, shade=1))
    for a_, b_ in (((15, 11), (24, 4)), ((15, 15), (28, 9)), ((16, 18), (31, 14))):    # folds from the knot
        for x, y in line_px(*a_, *b_):
            if band[y, x]: c[y, x] = 4
    for x, y in line_px(27, 2, 40, 12):                    # the white panel at the front, as Sapphire's
        for dy, v in ((0, 2), (1, 2), (2, 7)):
            if band[y + dy, x] and (v == 2 or c[y + dy, x] != 2): c[y + dy, x] = v
    for x, y in line_px(4, 4, 10, 10):                     # a crease along each tail
        if tail1[y, x]: c[y, x] = 4
    for x, y in line_px(3, 19, 10, 16):
        if tail2[y, x]: c[y, x] = 4
    inner_line(c, band, hair | face | lock, 0xF)
    inner_line(c, (tail1 | tail2) & ~band, band | knot, 5)
    inner_line(c, knot, band | tail1 | tail2, 5)
    inner_line(c, lock, face, 0xA)
    fig = band | tail1 | tail2 | knot | hair | face | lock
    outline_outside(c, fig, 0xF)
    patch(c, ['..KK....', '.KSBK...', '.KSsK...', '..KBK...'], MB_LET, 30, 22)       # the ear
    patch(c, ['.K', 'KW', 'Kn'], MB_LET, 43, 22)                                      # the corner of the eye
    return c, fig

def cut_hair(out, donor, hair, centre, radius, zone, outline=0xF):
    """Rosa's twin tails cut to May's shoulder length: hair pixels of the donor in `zone` farther than `radius`
    from `centre` are removed; holes this leaves inside the figure are filled from the nearest kept pixel of the
    same row (the clothes under the hair), and the new edge is outlined."""
    H, W = out.shape
    yy, xx = np.mgrid[0:H, 0:W]
    far = np.hypot(xx - centre[0], yy - centre[1]) > radius
    hairm = zone & far & np.isin(donor, list(hair))
    # outline pixels that only bordered the hair go too
    ol = zone & far & (donor == outline)
    nb_hair = neighbours(hairm)
    nb_other = neighbours(zone & ~hairm & (donor != 0) & (donor != outline))
    dele = hairm | (ol & nb_hair & ~nb_other)
    out[dele] = 0
    # holes: transparent pixels of the zone not reachable from the zone's edge through transparent pixels
    a = zone & (out == 0)
    edge = a & ~neighbours(~zone) & False
    border = np.zeros_like(a); border[[0, -1], :] = True; border[:, [0, -1]] = True
    zb = zone & neighbours(~zone)
    outside = grow(a & (zb | border), a)
    holes = a & ~outside
    for y, x in zip(*np.nonzero(holes)):
        for d in range(1, 12):
            for i in (x - d, x + d):
                if 0 <= i < W and out[y, i] not in (0, outline) and not holes[y, i]:
                    out[y, x] = out[y, i]; break
            else:
                continue
            break
    gone = dele & (out == 0)
    coloured = (out != 0) & (out != outline)
    out[gone & neighbours(coloured)] = outline
    return dele

def may_back():
    """May's battle back (a/0/7/2 sprite 1, MCSS) on Rosa's parts and throw animation, in Sapphire's design:
    red bandana with the white stripe and the knot, brown hair cut to the shoulders (Rosa's twin tails go), red
    top with a dark collar (Rosa's bow), white skirt, black gloves."""
    parts, static, rgbs, cells, meta = SA.tr_donor('back', 1)
    d = parts.astype(np.int16); sh = d.shape
    out = d.copy()
    R = ROSA_BACK
    def boxes(lst):
        m = np.zeros(sh, bool)
        for b in lst: m |= box(sh, *b)
        return m
    skirt, hands = boxes(R['skirt_boxes']), boxes(R['hand_boxes'])
    for o, n in R['body'].items(): out[~skirt & ~hands & (d == o)] = n
    for o, n in R['skirt'].items(): out[skirt & ~hands & (d == o)] = n
    for o, n in R['glove'].items(): out[hands & (d == o)] = n
    c, fig = may_back_head()
    for ((x0, y0), cb, centre), top in zip(R['heads'], R['skirt_boxes']):
        above = box(sh, cb[0], cb[1], cb[2], top[1]) & ~hands
        below = box(sh, cb[0], top[1], cb[2], cb[3]) & ~hands
        cut_hair(out, d, {0xB, 0xC, 0xE}, centre, 22, above)
        cut_hair(out, d, {0xB, 0xC}, centre, 22, below)      # the legs are 0xE too: only the tails' browns
        allowed = box(sh, *cb) & (np.isin(d, [0, 0xB, 0xC, 0xE, 0xF, 3, 4, 0xA, 1]) | (out == 0))
        stamp_head(out, d, c, fig, x0, y0, allowed, (cb[0], cb[1], cb[2], centre[1] + 6), {3, 4, 0xB, 0xC, 0xE},
                   outline=0xF, through={0xF})
    for cb in ((0, 24, 48, 128), (48, 8, 120, 128), (120, 32, 208, 128)):
        drop_specks(out, box(sh, *cb), 40)               # cut-off tail ends and their highlights
    return parts, rgbs, out.astype(np.uint8), cells

# ---------------------------------------------------------------------------------------------------- intro Birch

INTRO_ARC, INTRO_PARTS, INTRO_PAL, INTRO_CELLS, INTRO_NANR, INTRO_NMCR = 168, 25, 28, 27, 24, 30   # sProfessorLoadInfo
IB_PAL = {0: (24, 189, 107), 1: (189, 156, 90), 2: (139, 115, 57), 3: (189, 115, 82), 4: (123, 74, 57),
          5: (247, 247, 255), 6: (214, 218, 230), 7: (156, 165, 189), 8: (206, 82, 82), 9: (74, 82, 90),
          0xA: (255, 230, 205), 0xB: (230, 186, 148), 0xC: (198, 148, 115), 0xD: (90, 57, 41), 0xE: (255, 255, 255),
          0xF: (24, 24, 33)}
IB_LET = {'k': 1, 'K': 0xF, 'H': 3, 'h': 4, 'd': 0xD, 'S': 0xA, 's': 0xB, 't': 0xC, 'W': 0xE, 'n': 9, 'r': 8}
IB_HEAD = [    # 32 x 32, Juniper's head frame (cell 27 at (192, 0)): Birch's messy hair, beard, 3/4 to the right
    '................................',
    '..........K...K.....K...........',
    '.........KHK.KHK...KHK..........',
    '........KHHhKHHHKKKHHK.K........',
    '.......KHHHHHHHHHHHHHHKHK.......',
    '......KhHHHHHHHHHHHHHHHHHK......',
    '.....KhHHhHHHHHHhHHHHHHHHHK.....',
    '.....KhHhHHHHHHHHhHHHHHHHHK.....',
    '....KhHhHHhHHHHHHHhHHHHHHhhK....',
    '....KhhHhHHHhHHHHHHHhHHHHhhK....',
    '....KhHhHhHHHhhHHHHHHhhHHhhhK...',
    '....KhhHhHhHHHhhSSHHHhSHHhhhK...',
    '....KhhhhhhSSSSSSSSSSSSSShhhK...',
    '.....KhhhhSSSSSSSSSSSSSSSShhK...',
    '.....KhhhSSKKKKSSSSKKKKKSShK....',
    '.....KhhhSSSSSSSSSSSSSSSSStK....',
    '.....KhhtSSSKKSSSSSSKKSSStK.....',
    '....KhhhtSSSWnSSSSSSWnSSStK.....',
    '....KhhhtSSSnKSSSSSSnKSSStK.....',
    '.....KhhtSSSSSSSSSSStSSSstK.....',
    '.....KhhhtSSSSSSSSStSSSSstK.....',
    '......KhhhSSSSSSSSSSSSSShK......',
    '......KhhhhtSSSSSSSSSShhhK......',
    '.......KhhhhhSSSSSSSShhhhK......',
    '.......KhhHhhhhKKKKKhhhHK.......',
    '........KhhHhhhhhhhhhhHhK.......',
    '........KhhhHhhhhhhhHhhK........',
    '.........KhhhhhHHhhhhhK.........',
    '..........KKhhhhhhhhKK..........',
    '............KKtttttK............',
    '.............tssssst............',
    '.............tssssst............',
]

def intro_birch_head(mouth=0):
    h = parse(IB_HEAD, IB_LET)
    if mouth:                                             # talking: the mouth open in the beard
        h[24, 15:20] = [0xF, 0xD, 8, 0xD, 0xF] if mouth == 1 else [0xF, 8, 8, 8, 0xF]
        if mouth == 2: h[25, 16:19] = [0xF, 8, 0xF]
    return h

# Juniper's intro head is cut into pieces that animate: head frame = cell 27 (192, 0) / 28 (224, 0) (32 x 32, used
# by multi-cell 1); multi-cells 0 and 2 build it from cell 1 (the top, inside the 64 x 128 body cell), the blinking
# eye strip (cells 2 / 3), the mouth strip (cells 4 / 5) and the chin at the top of the talking torsos (cells 6-8).
# Each piece's texel (x, y) shows head-frame pixel (x - cx0 + dx, y - cy0 + dy) (offsets found by matching
# Juniper's own pixels).
INTRO_PIECES = {1: (-16, 0, 'top'), 2: (8, 15, 'open'), 3: (8, 15, 'blink'), 4: (0, 24, 'mouth0'),
                5: (0, 24, 'mouth1'), 6: (0, 24, 'mouth0'), 7: (0, 24, 'mouth1'), 8: (0, 24, 'mouth2')}
INTRO_HEADISH = {3, 4, 8, 9, 0xA, 0xB, 0xC, 0xD, 0xF, 1, 2}

def intro_birch():
    """Prof. Birch in the new-game intro (Juniper's MCSS set in a/1/6/8: her poses, Poke Ball throw and talking
    animation stay): Sapphire's Birch head (messy red-brown hair, beard, thick brows) drawn into every head piece,
    white lab coat, dark shirt (her white top), khaki shorts (her skirt), brown sandals (her sneakers)."""
    from b2files import arc_path, narc_entries
    ents = narc_entries(arc_path(SA.FILES, INTRO_ARC))
    _, pal = sprites.nclr_colors(ents[INTRO_PAL])
    rgbs = [sprites.bgr555_to_rgb(c) for c in pal]
    _, _, raw = sprites.tr_decode_image(ents[INTRO_PARTS], 'parts')
    a = np.frombuffer(raw, np.uint8).reshape(128, 256).copy()
    cells = sprites.ncer_cells(ents[INTRO_CELLS])
    sh = a.shape
    def cellmask(ids):
        m = np.zeros(sh, bool)
        for ci in ids:
            for x, y, w, h, tx, ty, hf, vf in cells[ci]: m[ty:ty + h, tx:tx + w] = True
        return m
    out = a.astype(np.int16).copy()
    torso = cellmask([6, 7, 8])
    out[torso & (a == 0xE)] = 9                            # white top -> dark shirt
    feet = cellmask([29, 30])                              # sneakers -> sandals: bare feet, brown straps
    for o, n in {0xE: 0xB, 5: 0xB, 6: 0xC, 7: 0xC, 8: 0xD, 9: 0xD, 1: 0xD, 2: 0xD}.items():
        out[feet & (a == o)] = n
    out[cellmask([19, 20, 21, 22, 25]) & (a == 9)] = 8     # the Poke Balls keep their red (9 is the shirt now)
    heads = {'open': intro_birch_head(0), 'mouth0': intro_birch_head(0), 'mouth1': intro_birch_head(1),
             'mouth2': intro_birch_head(2), 'top': intro_birch_head(0)}
    blink = intro_birch_head(0).copy()
    blink[17, :] = np.where(np.isin(blink[17, :], [0xE, 9]), 0xA, blink[17, :])
    blink[18, :] = np.where(np.isin(blink[18, :], [0xE, 9, 0xF]) & (np.arange(32) > 10) & (np.arange(32) < 24), 0xF, blink[18, :])
    blink[16, :] = np.where((blink[16, :] == 0xF) & (np.arange(32) > 10) & (np.arange(32) < 24), 0xA, blink[16, :])
    heads['blink'] = blink
    for ci, (dx, dy, which) in INTRO_PIECES.items():
        hd = heads[which]
        x0, y0, x1, y1 = SA.cell_box(cells[ci])
        for y in range(y0, y1):
            for x in range(x0, x1):
                hx, hy = x - x0 + dx, y - y0 + dy
                if not (0 <= hx < 32 and 0 <= hy < 32):
                    continue
                if ci in (6, 7, 8) and hy >= 29:           # below the chin: the torso's own neck and collar
                    continue
                v = hd[hy, hx]
                if v >= 0:
                    out[y, x] = v
                elif a[y, x] in INTRO_HEADISH:
                    out[y, x] = 0
    for (x0, y0), hd in (((192, 0), intro_birch_head(0)), ((224, 0), intro_birch_head(1))):
        out[y0:y0 + 32, x0:x0 + 32] = 0
        stamp_at(out, hd, x0, y0 - (1 if x0 == 224 else 0))
    out[70:77, 33] = 2                                     # the skirt becomes shorts: a seam and a gap
    out[76, 33] = 0xF; out[77, 32] = 0xF; out[77, 33] = 7; out[77, 34] = 0xF
    out[~cellmask(range(len(cells)))] = 0                  # texels no cell draws
    return a, rgbs, out.astype(np.uint8), cells

def write_intro_birch():
    from b2files import arc_path, narc_entries
    a, rgbs, out, cells = intro_birch()
    ents = narc_entries(arc_path(SA.FILES, INTRO_ARC))
    new = sprites.tr_encode_image(ents[INTRO_PARTS], 'parts', out.tobytes())
    assert len(new) <= len(ents[INTRO_PARTS]), f'intro parts compress to {len(new)} > {len(ents[INTRO_PARTS])}'
    folder = os.path.join(SA.SRC, 'mcss', 'intro-professor-birch')
    os.makedirs(folder, exist_ok=True)
    rg = [tuple(IB_PAL[i]) for i in range(16)]
    sprites.write_pal(os.path.join(folder, 'palette.pal'), rg)
    sprites.write_png(os.path.join(folder, 'parts.png'), out.tobytes(), 256, 128, rg)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='mcss', archive=INTRO_ARC, files={'parts': INTRO_PARTS, 'palette': INTRO_PAL}, keep_size=True,
        name='intro-professor-birch', donor='Professor Juniper, intro (a/1/6/8 files 24-30: poses and animation)',
        note='Prof. Birch in the new-game intro, drawn from Sapphire', made_by='b2tools/sprite_players.py'))
    return f'{folder} ({len(new)} of {len(ents[INTRO_PARTS])} bytes)'

# ---------------------------------------------------------------------------------------------------- gender choice

# The intro's boy/girl choice shows a 3D model (a/1/6/8 file 22, IntroG3d in ov294) whose textures int_swan_m.2 /
# int_swan_f.2 are the full-body pictures (128 x 256, 8 bpp, own 256-colour palette, colour 0 clear) and
# int_swan_m.1 / f.1 the same pictures darkened (the side not chosen). Brendan and May there: ref_intro() below.
# The darkened pictures go through Black 2's own darkening (fitted on Nate's and Rosa's pairs: about 0.29 x colour - 2
# per channel).

SWAN = dict(m=('int_swan_m.2', 'int_swan_m.1'), f=('int_swan_f.2', 'int_swan_f.1'))
SWAN_FILE = 22

def swan_rgba(name):
    from b2files import arc_path, narc_entries
    data = narc_entries(arc_path(SA.FILES, INTRO_ARC))[SWAN_FILE]
    texels, w, h, cols = sprites.tex8_decode(data, name)
    lut = np.zeros((256, 4), np.int16)
    for i, c in enumerate(cols): lut[i] = (*sprites.bgr555_to_rgb(c), 255)
    lut[0, 3] = 0
    return lut[np.frombuffer(texels, np.uint8).reshape(h, w)]

def hsv_planes(rgba):
    rgb = rgba[..., :3].astype(float) / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    h = np.where(mx - mn < 1e-6, 0, h)
    lum = 0.30 * r + 0.59 * g + 0.11 * b
    return h, s, v, lum

def to_ramp(img, mask, ramp, lo=None, hi=None):
    """Pixels of `mask`: their brightness rank inside the material picks a colour of `ramp` (dark -> light), so the
    material keeps its own shading steps in the new colours."""
    _, _, _, lum = hsv_planes(img)
    vals = lum[mask]
    if not len(vals):
        return
    lo = np.percentile(vals, 3) if lo is None else lo
    hi = np.percentile(vals, 97) if hi is None else hi
    t = np.clip((lum - lo) / max(hi - lo, 1e-6), 0, 0.999)
    idx = (t * len(ramp)).astype(int)
    R = np.array(ramp)
    img[mask, :3] = R[idx[mask]]

def darken(img):
    out = img.copy()
    out[..., :3] = np.clip(np.round(img[..., :3] * 0.29 - 2), 0, 255)
    return out

def to_indexed(img):
    """RGBA (alpha 0 / 255) -> (indices, palette) with colour 0 transparent, colours snapped to BGR555, at most 256."""
    rgb = img[..., :3].astype(int)
    q = (rgb * 31 + 127) // 255
    key = q[..., 0] | q[..., 1] << 5 | q[..., 2] << 10
    opaque = img[..., 3] > 0
    cols = np.unique(key[opaque])
    if len(cols) > 255:
        from PIL import Image
        im = Image.fromarray(img[..., :3].astype(np.uint8), 'RGB').quantize(255, method=Image.Quantize.MEDIANCUT)
        idx = np.array(im) + 1
        pal = [(0, 0, 0)] + [tuple(im.getpalette()[3 * i:3 * i + 3]) for i in range(255)]
        idx[~opaque] = 0
        return idx.astype(np.uint8), [tuple(sprites.c5to8(sprites.c8to5(v)) for v in c) for c in pal]
    lut = {int(k): i + 1 for i, k in enumerate(cols)}
    idx = np.zeros(key.shape, np.uint8)
    for k, i in lut.items():
        idx[(key == k) & opaque] = i
    pal = [(0, 0, 0)] + [(sprites.c5to8(k & 31), sprites.c5to8(k >> 5 & 31), sprites.c5to8(k >> 10 & 31)) for k in cols]
    return idx, pal

def write_swan(key, img):
    """Folders src/sprites/texture/intro-swan-<key>-2 (the picture) and -1 (darkened)."""
    done = []
    for name, pic in ((SWAN[key][0], img), (SWAN[key][1], darken(img))):
        idx, pal = to_indexed(pic)
        folder = os.path.join(SA.SRC, 'texture', name.replace('.', '-').replace('_', '-'))
        os.makedirs(folder, exist_ok=True)
        from PIL import Image
        im = Image.frombytes('P', (idx.shape[1], idx.shape[0]), idx.tobytes())
        im.putpalette([v for c in pal for v in c] + [0] * (3 * (256 - len(pal))))
        im.save(os.path.join(folder, 'texture.png'), transparency=0)
        sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
            kind='texture', archive=INTRO_ARC, file=SWAN_FILE, texture=name, palette=name + '_pl',
            note=('Brendan' if key == 'm' else 'May') + ' at the intro\'s gender choice' +
                 (' (darkened: not chosen)' if name.endswith('.1') else ''),
            donor='src/reference/' + REF_PICTURE[key] + ' (the user\'s official art) resampled; slot: ' +
                  ('Nate' if key == 'm' else 'Rosa') + "'s picture", made_by='b2tools/sprite_players.py'))
        done.append(folder)
    return done


# ---------------------------------------------------------------------------------------------------- intro pictures

# User answer 2026-10-06 (after a hand-drawn version): the gender-choice pictures are the official Omega Ruby /
# Alpha Sapphire art the user supplied (src/reference/*_official.png) itself, resampled to Nate's / Rosa's picture
# size and place (same height, same feet line, centred), quantized to the texture's 256 colours (no dithering), with a
# clean transparent edge, and darkened for the side not chosen as Black 2 does.

REF = os.path.join(ROOT, 'src', 'reference')
REF_PICTURE = {'m': 'brendan_official.png', 'f': 'may_official.png'}

def ref_intro(key):
    """RGBA 128 x 256 picture for SWAN[key] from the user's reference art."""
    from PIL import Image
    im = np.array(Image.open(os.path.join(REF, REF_PICTURE[key])).convert('RGBA')).astype(np.int32)
    alpha = im[..., 3]
    rgb = im[..., :3].copy()
    known = alpha >= 250                                  # edge pixels carry the art's old background (a light
    for _ in range(12):                                   # fringe): they take the nearest solid pixel's colour
        if known.all():
            break
        acc = np.zeros_like(rgb); n = np.zeros(alpha.shape, np.int32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            k = np.roll(np.roll(known, dy, 0), dx, 1)
            acc += np.roll(np.roll(rgb, dy, 0), dx, 1) * k[..., None]; n += k
        take = ~known & (n > 0)
        rgb[take] = acc[take] // n[take][:, None]
        known |= take
    src = Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), 'RGBA')
    donor = swan_rgba(SWAN[key][0])
    ys, xs = np.nonzero(donor[..., 3] > 0)
    top, bottom = int(ys.min()), int(ys.max())            # Nate's / Rosa's head top and feet line
    H = bottom - top + 1
    W = int(round(src.width * H / src.height))
    small = src.convert('RGBa').resize((W, H), Image.LANCZOS).convert('RGBA')
    a = np.array(small)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    out = np.zeros((256, 128, 4), np.int16)
    x0 = (128 - W) // 2
    out[top:top + H, x0:x0 + W] = a
    return quantize_rgba(out)

def quantize_rgba(img, colours=255):
    """At most `colours` BGR555 colours over the opaque pixels (median cut, no dithering)."""
    from PIL import Image
    op = img[..., 3] > 0
    px = img[op][:, :3].astype(np.uint8)
    q = Image.fromarray(px.reshape(1, -1, 3), 'RGB').quantize(colours, method=Image.Quantize.MEDIANCUT,
                                                              dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:3 * colours], np.int16).reshape(-1, 3)
    pal = np.array([[sprites.c5to8(sprites.c8to5(v)) for v in c] for c in pal], np.int16)
    out = np.zeros_like(img)
    out[op, :3] = pal[np.array(q)[0]]
    out[op, 3] = 255
    return out

# ---------------------------------------------------------------------------------------------------- previews

def _unlz(d):
    return sprites.lz11_decompress(d) if d[:1] == b'\x11' else d

def anim_bank(d):
    """NANR / NMAR (KNBA block): [(element type, play mode, [(duration, data)])]; data = (cell,) for type 0,
    (cell, rotation, sx, sy, x, y) for type 1, (cell, 0, x, y) for type 2."""
    import struct
    b = 0x10
    assert d[b:b + 4] == b'KNBA'
    nseq, nfr, so, fo, do = struct.unpack_from('<HHIII', d, b + 8)
    base = b + 8
    seqs = []
    for i in range(nseq):
        n, start, typ, atype, mode, foff = struct.unpack_from('<HHHHII', d, base + so + 16 * i)
        frames = []
        for k in range(n):
            doff, dur = struct.unpack_from('<IH', d, base + fo + foff + 8 * k)
            at = base + do + doff
            fmt = {0: '<H', 1: '<HHiihh'}.get(typ & 0xff, '<HHhh')
            frames.append((dur, struct.unpack_from(fmt, d, at)))
        seqs.append((typ, mode, frames))
    return seqs

def multicells(d):
    """NMCR (KBCM block): per multi-cell, its nodes [(NANR sequence, x, y, flags)]; node 0 is drawn on top."""
    import struct
    b = 0x10
    assert d[b:b + 4] == b'KBCM'
    n, _, mo, ho = struct.unpack_from('<HHII', d, b + 8)
    base = b + 8
    out = []
    for i in range(n):
        nn, nca, noff = struct.unpack_from('<HHI', d, base + mo + 8 * i)
        out.append([struct.unpack_from('<HhhH', d, base + ho + noff + 8 * k) for k in range(nn)])
    return out

def mcss_anim(arc, files):
    """Cells, cell animations and multi-cells of an MCSS sprite; files = (NCER, NANR, NMCR) indices."""
    from b2files import arc_path, narc_entries
    ents = narc_entries(arc_path(SA.FILES, arc))
    return dict(cells=sprites.ncer_cells(ents[files[0]]), nanr=anim_bank(_unlz(ents[files[1]])),
                nmcr=multicells(ents[files[2]]))

def multicell_strip(parts, pal, a, scale=2, gap=8):
    """Every multi-cell of the sprite (the poses its animation shows), side by side on the sprite's origin."""
    from PIL import Image
    lut = np.zeros((16, 4), np.uint8)
    for i in range(1, 16): lut[i] = (*pal[i], 255)
    Pimg = Image.fromarray(lut[np.asarray(parts, np.uint8)], 'RGBA')
    mcs = []
    for nodes in a['nmcr']:
        pieces = []
        for seq, x, y, flags in nodes:
            typ, mode, frames = a['nanr'][seq]
            data = frames[0][1]
            if not a['cells'][data[0]]:
                continue
            ox, oy = (data[4], data[5]) if typ == 1 else (data[2], data[3]) if typ == 2 else (0, 0)
            im, (x0, y0) = sprites.render_cell(Pimg, a['cells'][data[0]])
            pieces.append((im, x + x0 + ox, y + y0 + oy))
        X0 = min(p[1] for p in pieces); Y0 = min(p[2] for p in pieces)
        X1 = max(p[1] + p[0].width for p in pieces); Y1 = max(p[2] + p[0].height for p in pieces)
        img = Image.new('RGBA', (X1 - X0, Y1 - Y0), (0, 0, 0, 0))
        for im, x, y in reversed(pieces):
            img.alpha_composite(im, (x - X0, y - Y0))
        mcs.append((img, (X0, Y0)))
    X0 = min(o[0] for _, o in mcs); Y0 = min(o[1] for _, o in mcs)
    X1 = max(o[0] + im.width for im, o in mcs); Y1 = max(o[1] + im.height for im, o in mcs)
    w, h = X1 - X0, Y1 - Y0
    out = Image.new('RGBA', (len(mcs) * (w + gap), h), (0, 0, 0, 0))
    for k, (im, (x, y)) in enumerate(mcs):
        out.alpha_composite(im, (k * (w + gap) + x - X0, y - Y0))
    return out.resize((out.width * scale, out.height * scale), Image.NEAREST)

def folder_frames(folder):
    """(frames, palette) of an overworld art folder."""
    from PIL import Image
    meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
    pal = pal_of(folder)
    return [np.array(Image.open(os.path.join(folder, f'frame_{i:02d}.png'))) for i in range(meta['frames'])], pal

def pal_of(folder):
    return {i: tuple(c) for i, c in enumerate(sprites.read_pal(os.path.join(folder, 'palette.pal')))}

def png_rgba(path, scale=1, box=None):
    from PIL import Image
    im = Image.open(path).convert('RGBA')
    if box: im = im.crop(box)
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)

def gen3_frames(path, w, n=None, scale=3, gap=2, order=None, frame_h=32):
    """A Sapphire sheet (frames side by side, or stacked when the picture is taller than wide) as one strip."""
    from PIL import Image
    im = Image.open(path).convert('RGBA')
    if im.height > im.width:
        k = im.height // frame_h
        ims = [im.crop((0, frame_h * i, im.width, frame_h * (i + 1))) for i in range(k)]
    else:
        k = im.width // w
        ims = [im.crop((w * i, 0, w * (i + 1), im.height)) for i in range(k)]
    if order: ims = [ims[i] for i in order]
    if n: ims = ims[:n]
    W = sum(i.width for i in ims) + gap * (len(ims) - 1); H = max(i.height for i in ims)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = 0
    for i in ims: out.alpha_composite(i, (x, H - i.height)); x += i.width + gap
    return out.resize((out.width * scale, out.height * scale), Image.NEAREST)

def review_sheet(path, title, sections, bg=(72, 92, 108)):
    """sections: [(heading, [(label, PIL image)])] -> a labelled sheet."""
    from PIL import Image, ImageDraw
    rows = []
    for heading, items in sections:
        rows.append(('h', heading, None))
        for label, im in items:
            rows.append(('r', label, im))
    W = max(im.width for k, _, im in rows if im is not None) + 150
    H = 34 + sum(26 if k == 'h' else im.height + 10 for k, _, im in rows)
    img = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(img)
    d.text((10, 10), title, fill=(255, 255, 255)); y = 34
    for k, label, im in rows:
        if k == 'h':
            d.rectangle([0, y + 2, W, y + 22], fill=(48, 62, 76)); d.text((10, y + 7), label, fill=(255, 236, 160)); y += 26
        else:
            d.text((10, y + 4), label, fill=(225, 232, 255))
            img.paste(im, (140, y), im); y += im.height + 10
    img.save(path)
    return path

# ---------------------------------------------------------------------------------------------------- recipes

BRENDAN_OW = {231: 'walk-run', 232: 'bike', 233: 'surf', 234: 'item', 235: 'action2', 236: 'action5', 237: 'throw',
              238: 'balance', 239: 'fishing'}

def brendan_ow(codes=None, fixes=None):
    ch = brendan_char()
    made = {}
    for code, what in BRENDAN_OW.items():
        if codes and code not in codes:
            continue
        frames, rgbs, meta, new = build_sheet(ch, code)
        for k, f in (fixes or BRENDAN_FIXES).get(code, {}).items():
            f(new[k], frames[k])
        write_ow(code, f'brendan-{what}', new, B_PAL, 'Brendan (player), drawn from Sapphire',
                    f'Nate {code} (frame layout and poses)')
        made[code] = (frames, rgbs, new)
    return made

def write_ow(code, name, frames, pal, note, donor):
    """sprite_art.write_ow, marked as made here."""
    folder = SA.write_ow(code, name, frames, pal, note, donor)
    meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
    meta['made_by'] = 'b2tools/sprite_players.py'
    sprites.write_json(os.path.join(folder, 'sprite.json'), meta)
    return folder

def recolour_box(x0, y0, x1, y1, table):
    """A per-frame fix: donor pixels inside the box get table[donor index] (e.g. a Poke Ball's red and white)."""
    def fix(new, donor):
        sub = donor[y0:y1, x0:x1]
        for o, n in table.items():
            new[y0:y1, x0:x1][sub == o] = n
    return fix

NATE_BALL = {1: 9, 3: 8, 4: 8, 6: 3, 9: 3, 0xD: 1, 0xE: 2, 0xC: 1, 8: 0xF, 0xF: 0xF}     # -> Brendan's palette
ROSA_BALL = {5: 3, 6: 5, 1: 0xF, 0xB: 1, 0xA: 1, 0xC: 2, 0xF: 0xF}                       # -> May's palette
MAY_OW = {240: 'walk-run', 241: 'bike', 242: 'surf', 243: 'item', 244: 'action2', 245: 'action5', 246: 'throw',
          247: 'balance', 248: 'fishing'}
MAY_FIXES = {246: {1: recolour_box(19, 17, 26, 23, ROSA_BALL), 2: recolour_box(26, 10, 32, 16, ROSA_BALL),
                   3: recolour_box(26, 12, 32, 18, ROSA_BALL)}}

def may_ow(codes=None):
    ch = may_char()
    made = {}
    for code, what in MAY_OW.items():
        if codes and code not in codes:
            continue
        frames, rgbs, meta, new = build_sheet(ch, code)
        for k, f in MAY_FIXES.get(code, {}).items():
            f(new[k], frames[k])
        write_ow(code, f'may-{what}', new, M_PAL, 'May (player), drawn from Sapphire', f'Rosa {code} (frame layout and poses)')
        made[code] = (frames, rgbs, new)
    return made

def birch_ow():
    ch = birch_char()
    frames, rgbs, meta, new = build_sheet(ch, 104)
    write_ow(104, 'prof-birch', new, P_PAL, 'Prof. Birch (NPC), drawn from Sapphire', 'Cedric Juniper 104 (frame layout and poses)')
    return [104]

def drawn_mask(cells, shape=(128, 256)):
    m = np.zeros(shape, bool)
    for c in cells:
        for x, y, w, h, tx, ty, hf, vf in c:
            m[ty:ty + h, tx:tx + w] = True
    return m

def write_tr_art(side, s, name, parts_out, static_out, pal, note, donor, cells):
    """Battle sprite folder (sprite_art.write_tr), with texture pixels no cell draws cleared (they would only
    cost compressed bytes)."""
    parts_out = parts_out.copy()
    parts_out[~drawn_mask(cells)] = 0
    folder = SA.write_tr(side, s, name, parts_out, static_out, pal, note, donor)
    meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
    meta['made_by'] = 'b2tools/sprite_players.py'
    sprites.write_json(os.path.join(folder, 'sprite.json'), meta)
    return folder

def write_battle():
    done = []
    parts, rgbs, out, cells = brendan_back()
    done.append(write_tr_art('back', 0, 'brendan', out, np.zeros((80, 80), np.uint8), BB_PAL,
                             'Brendan (player back), drawn from Sapphire', 'Nate back 0 (parts and throw animation)', cells))
    parts, rgbs, out, cells = may_back()
    done.append(write_tr_art('back', 1, 'may', out, np.zeros((80, 80), np.uint8), MB_PAL,
                             'May (player back), drawn from Sapphire', 'Rosa back 1 (parts and throw animation)', cells))
    parts, static, rgbs, cells, out, sout = brendan_front()
    done.append(write_tr_art('front', 0, 'brendan', out, sout, BF_PAL, 'Brendan (rival battles, Hall of Fame), '
                             'drawn from Sapphire', 'Nate front 0 (parts and animation)', cells))
    parts, static, rgbs, cells, out, sout = may_front()
    done.append(write_tr_art('front', 1, 'may', out, sout, MF_PAL, 'May (rival battles, Hall of Fame), drawn from '
                             'Sapphire', 'Rosa front 1 (parts and animation)', cells))
    return [os.path.basename(os.path.dirname(f)) + '/' + os.path.basename(f) for f in done]

BRENDAN_FIXES = {237: {1: recolour_box(24, 16, 31, 22, NATE_BALL), 2: recolour_box(26, 10, 32, 16, NATE_BALL),
                       3: recolour_box(26, 12, 32, 18, NATE_BALL)}}

# The player icons of the start menu's Continue panel, the GTS and Spin Trade / Battle Video (a/0/3/0) are copies of
# walk-run sheet frames (sprites.py, "Player icons"): these folders make the build copy our frames there.
PLAYER_ICONS = {'brendan': (231, 4, {5: [3, 0, 6, 9, 1, 2, 4, 5, 7, 8, 10, 11, 12, 15, 18, 21, 13, 14, 16, 17, 19, 20, 22, 23],
                                     14: [0, 9, 3, 6, 1, 2, 5, 4, 8, 7, 11, 10], 20: [3, 12, 6, 9]}),
                'may': (240, 6, {7: [3, 0, 6, 9, 1, 2, 4, 5, 7, 8, 10, 11, 12, 15, 18, 21, 13, 14, 16, 17, 19, 20, 22, 23],
                                 17: [0, 9, 3, 6, 1, 2, 5, 4, 8, 7, 11, 10], 23: [3, 12, 6, 9]})}

def write_player_icons():
    from b2files import arc_path, narc_entries
    ents = narc_entries(arc_path(SA.FILES, 30))
    done = []
    for who, (code, pal, ncgrs) in PLAYER_ICONS.items():
        _, rg, meta = SA.donor(code)                     # the order above: check it against Black 2's own files
        frames = [bytes(f) for f in (np.array(x).tobytes() for x in SA.donor(code)[0])]
        for f, order in ncgrs.items():
            assert sprites.objframes_decode(ents[f]) == [frames[k] for k in order], (who, f)
        folder = os.path.join(SA.SRC, 'objframes', f'player-icons-{who}')
        os.makedirs(folder, exist_ok=True)
        sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
            kind='objframes', archive=30, palette=pal, from_code=code, ncgr={str(k): v for k, v in ncgrs.items()},
            note=f'{who.title()}: start menu Continue panel (NCGR {list(ncgrs)[0]}), GTS ({list(ncgrs)[1]}), Spin '
                 f'Trade / Battle Video ({list(ncgrs)[2]}): frames of overworld sheet {code}',
            made_by='b2tools/sprite_players.py'))
        done.append(folder)
    return done

# The trainer card (ov186) shows the player's Union Room avatar: a/0/4/0 NCGR 16 + v / NCLR v, v = a random 0-7
# (+ 8 for a girl) set at the new game (sprites.py "Trainer card pictures"). User answer 2026-10-06: the card shows
# Brendan or May, so every boy avatar gets Brendan's battle still (front 0) and every girl avatar May's (front 1).
CARD = {'brendan': (0, list(range(16, 24)), list(range(0, 8))), 'may': (1, list(range(24, 32)), list(range(8, 16)))}

def write_cardpics():
    done = []
    for who, (front, ncgr, nclr) in CARD.items():
        folder = os.path.join(SA.SRC, 'cardpic', f'trainer-card-{who}')
        os.makedirs(folder, exist_ok=True)
        sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
            kind='cardpic', archive=40, ncgr=ncgr, nclr=nclr, from_front=front,
            note=f'Trainer card picture: {who.title()} (battle front {front} still) for every '
                 f'{"boy" if front == 0 else "girl"} avatar', made_by='b2tools/sprite_players.py'))
        done.append(folder)
    return done

OLD = os.path.join(ROOT, 'work', 'agents', 'sprites_players', 'old_art')   # the first-pass recolours, for comparison

def review():
    """screenshots/sprites/players_upgrade_review.png (this agent's scope): the intro pair beside the user's reference
    art and Nate / Rosa, the trainer card pictures, the battle backs (Sapphire / previous version / new / donor)."""
    from PIL import Image
    from b2files import arc_path, narc_entries
    def pic(rgba, scale=2):
        im = Image.fromarray(rgba.astype(np.uint8), 'RGBA')
        return im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    def pair(*ims, gap=16):
        W = sum(i.width for i in ims) + gap * (len(ims) - 1); H = max(i.height for i in ims)
        o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = 0
        for i in ims: o.alpha_composite(i, (x, H - i.height)); x += i.width + gap
        return o
    ref = os.path.join(ROOT, 'src', 'reference')
    def refpic(n):
        im = Image.open(os.path.join(ref, n)).convert('RGBA')
        return im.resize((int(im.width * 512 / im.height), 512), Image.LANCZOS)
    secs = []
    bm, mm = ref_intro('m'), ref_intro('f')
    secs.append(('Gender choice in the intro (a/1/6/8 model 22, 128 x 256 8 bpp): the user\'s official art, resampled '
                 'to Nate / Rosa\'s size and feet line, 256 colours', [
                     ('reference art (user)', pair(refpic('brendan_official.png'), refpic('may_official.png'))),
                     ('NEW (chosen / not)', pair(pic(bm), pic(darken(bm)), pic(mm), pic(darken(mm)))),
                     ('Black 2 (Nate, Rosa)', pair(pic(swan_rgba(SWAN['m'][0])), pic(swan_rgba(SWAN['f'][0]))))]))
    e40 = narc_entries(arc_path(SA.FILES, 40))
    def card(ents, v, scale=2):
        at, cols = sprites.nclr_colors_any(ents[v]); pal = np.array([sprites.bgr555_to_rgb(c) for c in cols], np.uint8)
        px = np.frombuffer(sprites.card_decode(ents[16 + v]), np.uint8).reshape(80, 80)
        return Image.fromarray(pal[px]).convert('RGBA').resize((80 * scale, 80 * scale), Image.NEAREST)   # (64-79)
    new40 = dict(enumerate(e40))
    for who, (front, ncgr, nclr) in CARD.items():
        new40.update(sprites.cardpic_import(os.path.join(SA.SRC, 'cardpic', f'trainer-card-{who}'), e40,
                                            os.path.join(SA.SRC, 'trainer', 'front', f'{front:03d}-{who}')))
    secs.append(('Trainer card picture (a/0/4/0): every boy avatar = Brendan, every girl avatar = May (the battle '
                 'front stills, copied at build time)', [
                     ('NEW', pair(card(new40, 0), card(new40, 8))),
                     ('Black 2 (16 random avatars)', pair(*[card(e40, v, 1) for v in range(16)], gap=4))]))
    tp = os.path.join(RUBY, 'trainers')
    for s_, who in ((0, 'brendan'), (1, 'may')):
        a = mcss_anim(72, (8 * s_ + 2, 8 * s_ + 3, 8 * s_ + 4))
        parts, static, rgbs, cells, meta = SA.tr_donor('back', s_)
        f = os.path.join(SA.SRC, 'trainer', 'back', f'{s_:03d}-{who}')
        rows = [('Sapphire', gen3_frames(os.path.join(tp, f'{who}_back.png'), 64, scale=2, frame_h=64)),
                ('NEW', multicell_strip(np.array(Image.open(os.path.join(f, 'parts.png'))), pal_of(f), a, 2))]
        if s_ == 1:
            prev = may_back_previous()
            if prev is not None:
                rows.insert(1, ('previous (helmet)', multicell_strip(prev, MB_PAL, a, 2)))
        rows.append(('Black 2 donor', multicell_strip(parts, SA.pal_dict(rgbs), a, 2)))
        secs.append((f'{who.title()} battle back (a/0/7/2 #{s_}): idle, ball up, wind-up, throw', rows))
    return review_sheet(os.path.join(SHOTS, 'players_upgrade_review.png'),
                        'sprites_players: intro gender pictures, trainer card, battle backs (b2tools/sprite_players.py)',
                        secs)

def may_back_previous():
    """The committed May back (before the bandana fix), from git, for the review sheet."""
    import subprocess
    from PIL import Image
    try:
        data = subprocess.run(['git', 'show', 'HEAD:src/sprites/trainer/back/001-may/parts.png'], cwd=ROOT,
                              capture_output=True, check=True).stdout
    except Exception:
        return None
    import io
    return np.array(Image.open(io.BytesIO(data)))

def write_backs():
    """Brendan's and May's battle backs only (the fronts belong to sprite_upgrade.py now)."""
    done = []
    parts, rgbs, out, cells = brendan_back()
    done.append(write_tr_art('back', 0, 'brendan', out, np.zeros((80, 80), np.uint8), BB_PAL,
                             'Brendan (player back), drawn from Sapphire', 'Nate back 0 (parts and throw animation)', cells))
    parts, rgbs, out, cells = may_back()
    done.append(write_tr_art('back', 1, 'may', out, np.zeros((80, 80), np.uint8), MB_PAL,
                             'May (player back), drawn from Sapphire', 'Rosa back 1 (parts and throw animation)', cells))
    return [os.path.basename(f) for f in done]

# Scope (lead, 2026-10-06): Brendan's and May's overworld sheets, their battle fronts, the player icons and Prof.
# Birch (overworld 104, intro professor) moved to b2tools/sprite_upgrade.py; the recipes that wrote them (brendan,
# may, birch, battle fronts, intro, icons) are kept below only as code and are not run, so they cannot overwrite
# that agent's art. This script now makes: the intro gender pictures, the trainer card folders, the battle backs.
RECIPES = {'swan': lambda: write_swan('m', ref_intro('m')) + write_swan('f', ref_intro('f')),
           'card': write_cardpics, 'backs': write_backs, 'review': review}

if __name__ == '__main__':
    for name in (sys.argv[1:] or list(RECIPES)):
        print(name, '->', RECIPES[name]())
