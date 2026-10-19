"""Community sprites (user 2026-10-11: "free to use with credit, we just need to credit the authors"; authors in
src/sprites/community/incoming/CREDITS.md and release/CREDITS.md "Sprites"): the sheets are cut, placed and
palette-indexed onto Black 2's own sprite layouts. No pixel is drawn, resized or recoloured, with three exceptions the
user approved or that the DS format itself forces:
  - the grunt sheet exists only as a JPEG: every pixel is snapped to its sprite's true colours, found from the clean
    (flat) areas of that sprite (user approved; before/after in screenshots/sprites/community_grunts_jpeg.png);
  - near-identical colours (no channel more than NEAR apart, e.g. (214,153,110) and (215,154,111), which the DS's
    5-bit colour mostly cannot tell apart anyway) count as one colour; every such merge is printed by `analyze`;
  - Wally's front (hyo-oppa; the page allows edits with credit; the user asked for the fewest, closest merges):
    FRONT_MERGES, shown in screenshots/wally_sprite/wally_front_merges.png.
A sheet that still needs more than Black 2's 15 colours (+ clear), or a frame bigger than Black 2's frame, is
reported and NOT installed (the brief: "report it rather than altering the art").

    python3 sprite_community.py analyze          sizes and colour counts of every planned Black 2 sheet / picture
    python3 sprite_community.py build [part ...]  write the installable parts into src/sprites_gen5/ (the Gen 5 set;
                                                 patches/sprites.py installs it over src/sprites with HOENN_SPRITES_GEN5=1)
    python3 sprite_community.py review           screenshots/sprites/community_review.png (+ the grunts' JPEG image)

Placement (overworld): Black 2's frame layouts per object code (brendan_plan, may_plan, npc_plan) were checked on
Nate's and Rosa's sheets (notes/RESEARCH_STORY_SPRITES.md 5.1). In a row of the community sheet the frames keep the
sheet's own vertical placement (the artist's bob); horizontally each frame is registered to the row's standing frame by
its head (the hair/hat rows match). The standing frame's feet go on Black 2's feet row (30; surf 28, the sitting frames
end higher) and its centre on column 16, moved up when a step's foot would leave the frame. Frames of other actions
(item, throw, fishing in its 64x64 frame ...) are registered by the head to the walking frame of the same direction, so
the head does not jump between animations. Black 2 frames a sheet has no picture for take its nearest frames (listed
in brendan_plan's notes): balance left/right = the walking frames, the throw's last frame = the ball raised again.

Result (2026-10-11, `analyze`): installable = Brendan's 9 overworld sheets (hyo-oppa; the bike sheet only with the one
EXTRA_MERGES colour), Brendan's battle front (the sheet's front; the GIF has 20 colours) and back (frames 1, 3, 4 of 5:
Nate's back sprite has room for three poses), Maxie's battle front (joojishibuki), the four grunt overworlds (JPEG).
Not installable without changing the art (reported to the user): May (Luckygirl88: overworld frames up to 37 rows tall
for Black 2's 32x32 frame and 23-29 colours per sheet, no surf frames, front 42 and back 36 colours), Maxie's overworld
(17 colours), Archie's overworld (PurpleZaffre, 19 colours).
Second batch (DiegoWT's packs, downloaded by the user): May's overworld (240-248: walk, run, bike, surf, fishing; item /
throw from her "use HM" frames, balance and action5 = walking frames; the bike with one EXTRA_MERGES colour and the
pedalling sheet's stills) and Archie's overworld (353; Ruby's 303 copies it). May's battle front/back stay classic.
Third batch (2026-10-12, `build wally`): Wally's battle front (127, hyo-oppa's trainer collection, on layout 108 like
Brendan's; 19 colours: one pair the DS shows as one, three closest pairs merged, FRONT_MERGES, reported) and his
overworld (87, CalculusNova's walking frames without the backpack, 14 colours, wally_plan).
Fourth batch (2026-10-12, `build birch`): Prof. Birch's overworld (104, every Birch object; Wolfang62's Pokemon
Essentials sheet at 2x, placed as DiegoWT's Archie; 16 colours: one pair merged, EXTRA_MERGES[104], reported).
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import sprites, mcss  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

INCOMING = os.path.join(ROOT, 'src', 'sprites', 'community', 'incoming')
SRC = os.path.join(ROOT, 'src', 'sprites')            # the classic (Gen 3-based) set: read only here
GEN5 = os.path.join(ROOT, 'src', 'sprites_gen5')      # this tool's output: the Gen 5 (community) set, same layout;
                                                      # patches/sprites.py lays it over src/sprites when HOENN_SPRITES_GEN5=1
SHOTS = os.path.join(ROOT, 'screenshots', 'sprites')
FILES = sprites.SRC_FILES
NEAR = 10                     # colours closer than this in every channel count as one (see above)

SHEETS = {
    'brendan': dict(file='brendan_sheet_hyo-oppa.png', author='hyo-oppa', bg='alpha'),
    'may': dict(file='may_oras_sheet_Luckygirl88.png', author='Luckygirl88', bg='white'),
    'maxie': dict(file='maxie_sheet_joojishibuki.png', author='joojishibuki', bg=[(237, 28, 36), (154, 12, 19)]),
    'archie': dict(file='archie_sheet_PurpleZaffre.png', author='PurpleZaffre', bg='alpha', scale=2),
    'grunts': dict(file='aqua_magma_grunts_Kimmylube_AzureAquarian.jpg', author='Kimmylube, AzureAquarian', bg='jpeg'),
    # DiegoWT's packs (downloaded by the user 2026-10-11, commit 8bb14be): Pokemon Essentials sheets at 2x (every
    # visible 2x2 block one colour; only clear pixels differ), rows down, left, right, up
    **{f'may_{k}': dict(file=f'may_oras_DiegoWT/trProtag_Girl{v}.png', author='DiegoWT (Zailens commissioned)',
                        bg='alpha', scale=2)
       for k, v in (('walk', 'Walk'), ('run', 'Run'), ('bike', 'Bike'), ('bikeidle', 'BikeIdle'), ('surf', 'Surf'),
                    ('fish', 'Fish_offset'), ('hm', 'UseHM'))},
    'archie_d': dict(file='archie_oras_DiegoWT.png', author='DiegoWT (Kyledove commissioned)', bg='alpha', scale=2),
    # third batch (downloaded by the user 2026-10-12): hyo-oppa's DS-style trainer collection (Wally's front only) and
    # CalculusNova's Wally overworld sheet (Gen 3-sized 16x32 cells on a teal background)
    'trainers_hyo': dict(file='trainer_collection_hyo-oppa.png', author='hyo-oppa', bg='alpha'),
    'wally': dict(file='wally_sheet_CalculusNova.png', author='CalculusNova', bg=[(115, 197, 165)]),
    # fourth batch (2026-10-12): Wolfang62's Prof. Birch, a Pokemon Essentials sheet at 2x (64x64 cells, rows down,
    # left, right, up); each cell is an exact 2x upscale, but the down / up rows' 2x2 blocks start one pixel in
    # (cell=64: checked per cell, see sheet())
    'birch': dict(file='birch_sheet_Wolfang62.png', author='Wolfang62', bg='alpha', scale=2, cell=64),
    # fifth batch (user 2026-10-17): Kymotonian and Klein Studio's Wally, a Pokemon Essentials sheet at 2x (64x64 cells,
    # rows down, left, right, up; cell (1,0) starts one pixel down), replacing CalculusNova's Gen 3-sized Wally as NEW
    'wally_kk': dict(file='wally_sheet_Kymotonian_KleinStudio.png', author='Kymotonian, Klein Studio', bg='alpha', scale=2, cell=64),
}

# ------------------------------------------------------------------------------------------------ frames on the sheets
# A frame = (x0, y0, x1, y1) on the sheet (pixels inside, end exclusive; Archie's in his 2x sheet's 1x pixels), with
# an optional third item flags: 'm' = mirrored. Rows: (stand, step, step) as Black 2 orders them.

# Brendan (hyo-oppa). Walk rows are (step, stand, step) on the sheet; run rows the same; listed here stand first.
B = {
    'walk': {'down': [(26, 4, 43, 29), (7, 3, 24, 30), (45, 3, 62, 30)],
             'left': [(28, 34, 46, 57), (7, 33, 24, 56), (49, 34, 67, 58)],
             'up': [(27, 61, 44, 84), (6, 61, 23, 86), (49, 61, 66, 86)],
             'right': [(25, 89, 43, 112), (5, 89, 22, 112), (46, 89, 64, 113)]},
    'run': {'up': [(114, 5, 131, 27), (95, 5, 112, 30), (133, 5, 150, 30)],
            'left': [(114, 33, 132, 55), (92, 33, 109, 56), (133, 33, 154, 57)],
            'down': [(114, 57, 131, 80), (92, 58, 112, 83), (133, 57, 154, 83)],
            'right': [(112, 86, 130, 108), (91, 86, 109, 109), (134, 86, 151, 109)]},
    'surf': {'up': [(183, 5, 200, 28)], 'left': [(205, 6, 223, 28)], 'down': [(225, 5, 242, 28)],
             'right': [(244, 6, 262, 28)]},
    # bike: a still frame per direction, then the pedalling frames (down/up 4, left/right 3)
    'bike': {'down': [(37, 120, 54, 147), (6, 148, 23, 175), (26, 148, 43, 175), (45, 148, 62, 175), (64, 148, 81, 175)],
             'left': [(34, 178, 55, 202), (12, 204, 32, 229), (35, 204, 55, 229), (58, 204, 78, 229)],
             'up': [(37, 232, 54, 257), (8, 261, 25, 286), (27, 261, 44, 286), (46, 261, 63, 286), (65, 261, 82, 286)],
             'right': [(34, 290, 55, 314), (12, 317, 32, 342), (34, 317, 54, 342), (57, 317, 77, 342)]},
    # fishing, Black 2's order: up = rod to the side x2, rod forward x2; down / left = rod raised x2, line out x2
    'fish': {'down': [(333, 7, 351, 33), (368, 5, 385, 33), (401, 3, 418, 33), (435, 2, 452, 33)],
             'up': [(332, 45, 356, 67), (366, 46, 391, 67), (400, 40, 418, 67), (435, 38, 452, 67)],
             'left': [(334, 77, 354, 101), (370, 77, 391, 101), (396, 77, 426, 101), (430, 78, 461, 101)],
             'right': [(330, 111, 350, 135), (361, 111, 382, 135), (394, 111, 424, 135), (427, 112, 458, 135)]},
    'arms_out': {'up': [(183, 40, 200, 64), (202, 40, 219, 63), (221, 40, 238, 64)],
                 'down': [(183, 67, 200, 93), (202, 67, 219, 92), (221, 67, 238, 93)]},
    'front_extra': [(255, 40, 272, 65), (279, 42, 296, 65)],
    'turn_up': [(182, 103, 199, 126), (202, 103, 220, 126), (223, 103, 240, 126), (243, 102, 260, 125),
                (263, 102, 280, 126), (283, 102, 300, 125)],
    'ball_back': [(100, 202, 122, 225), (135, 201, 157, 225), (170, 201, 192, 225), (207, 202, 228, 225),
                  (243, 202, 263, 225), (282, 202, 302, 226), (319, 204, 336, 226), (353, 203, 370, 226)],
    'ball_front': [(105, 236, 122, 260), (139, 237, 154, 260), (172, 234, 192, 260), (203, 234, 224, 261)],
    'ball_side': [(286, 236, 304, 260), (319, 238, 339, 260), (354, 237, 373, 260)],
    'item_front': [(105, 269, 122, 293), (139, 270, 154, 293), (172, 267, 193, 293), (203, 267, 225, 294),
                   (236, 267, 258, 294)],
    'item_side': [(284, 270, 302, 294), (317, 272, 337, 294), (351, 271, 370, 294)],
    'front': (388, 226, 422, 294),
    # back throw: five 79-pixel frames side by side (the figures' left edges of frames 3-5 sit exactly 79 apart),
    # bottom = the frames' bottom edge (row 364)
    'back': dict(grid_x0=75, pitch=79, bottom=364, frames=[(103, 303, 150, 364), (162, 306, 221, 364),
                                                          (233, 304, 298, 364), (312, 305, 379, 364),
                                                          (391, 309, 458, 364)]),
}

# May (Luckygirl88): drawn on Black 2's own layout (Rosa's sheets), rows stand first.
M = {
    'walk': {'down': [(62, 4, 86, 35), (90, 4, 114, 36), (123, 4, 147, 36)],
             'up': [(61, 48, 87, 82), (94, 47, 120, 82), (124, 47, 150, 82)],
             'left': [(65, 84, 90, 115), (98, 83, 123, 115), (131, 83, 156, 115)],
             'right': [(61, 120, 86, 152), (94, 120, 119, 152), (127, 121, 152, 152)]},
    'run': {'down': [(68, 159, 91, 186), (96, 159, 119, 187), (122, 160, 145, 188)],
            'left': [(65, 196, 90, 225), (98, 194, 124, 225), (131, 194, 156, 225)],
            'right': [(68, 233, 93, 264), (100, 233, 126, 264), (134, 235, 159, 264)],
            'up': [(65, 271, 91, 305), (98, 269, 124, 306), (131, 269, 157, 306)]},
    'bike': {'down': [(170, 1, 194, 33), (203, 1, 227, 33), (233, 2, 257, 33)],
             'left': [(171, 33, 196, 66), (203, 32, 228, 66), (235, 34, 260, 66)],
             'right': [(171, 73, 196, 105), (203, 71, 228, 105), (235, 72, 260, 105)],
             'up': [(174, 109, 200, 144), (206, 109, 232, 144), (238, 109, 264, 144)],
             'still': [(172, 146, 198, 181), (205, 149, 229, 181), (238, 148, 264, 180), (269, 148, 295, 180)]},
    'fish': {'down': [(185, 194, 209, 231), (217, 197, 241, 227), (247, 196, 271, 228), (279, 197, 305, 231)],
             'up': [(182, 236, 210, 268), (218, 236, 246, 268), (254, 235, 280, 268), (285, 233, 311, 265)],
             'left': [(178, 277, 213, 307), (222, 276, 247, 307), (254, 275, 279, 306), (283, 273, 317, 303)]},
    'balance': {'up': [(307, 3, 333, 37), (341, 3, 367, 37), (373, 3, 399, 36), (402, 3, 428, 36)],
                'down': [(309, 41, 333, 72), (340, 41, 364, 72), (370, 43, 394, 74), (404, 43, 428, 74)],
                'left': [(309, 79, 334, 109), (340, 80, 365, 109), (375, 78, 400, 109), (408, 77, 433, 109)],
                'right': [(305, 113, 330, 145), (338, 114, 363, 145), (373, 116, 398, 145), (404, 115, 429, 145)]},
    'item': [(323, 156, 347, 184), (355, 154, 381, 186)],
    'throw': [(398, 156, 424, 181), (430, 151, 454, 182), (461, 151, 488, 183), (497, 152, 525, 183)],
    'action2': [(326, 192, 350, 223), (357, 196, 383, 223)],
    'action5': [(407, 192, 432, 223), (440, 192, 465, 223), (468, 192, 494, 223), (500, 190, 526, 223),
                (532, 192, 558, 223)],
    'heads': [(583, 11, 606, 46), (580, 51, 606, 76), (584, 78, 609, 101), (583, 103, 608, 124), (583, 128, 607, 149),
              (583, 156, 607, 177), (584, 182, 609, 203), (582, 207, 608, 226)],
    'front': (11, 6, 45, 75),
    'back': dict(bodies=[(640, 11, 687, 115), (704, 2, 766, 115), (770, 28, 847, 112)],
                 arms=[(866, 45, 912, 70), (871, 84, 885, 114), (890, 82, 906, 113), (928, 43, 952, 83),
                       (960, 43, 991, 82)]),
}

# Maxie (joojishibuki): front + 12 overworld frames (rows down, up, left, right; stand first).
X = {
    'front': (18, 32, 58, 110),
    'walk': {'down': [(82, 9, 100, 37), (109, 7, 127, 37), (135, 7, 153, 37)],
             'up': [(82, 43, 100, 71), (109, 43, 127, 73), (136, 42, 154, 72)],
             'left': [(84, 79, 100, 107), (111, 78, 127, 107), (137, 78, 153, 107)],
             'right': [(82, 113, 98, 141), (109, 113, 125, 142), (135, 112, 151, 141)]},
}

# Archie (PurpleZaffre): 4 rows (down, left, right, up) x 4 frames (stand, step, stand, step) in 32x32 cells at 1x.
A = {'walk': {d: [(32 * c, 32 * r, 32 * c + 32, 32 * r + 32) for c in (0, 1, 3)]
              for r, d in enumerate(('down', 'left', 'right', 'up'))}}

# Grunts (Kimmylube / AzureAquarian; JPEG, bounding boxes found on the JPEG): per grunt rows up (back), down
# (front), side (facing right) x (stand, step, step); left = the side row mirrored (as Black 2's 7-frame sheets show
# their right side in the engine).
G = {
    'aqua-grunt-m': {'up': [(10, 3, 31, 29), (42, 2, 63, 29), (74, 2, 95, 29)],
                     'down': [(10, 35, 32, 61), (42, 34, 64, 61), (74, 34, 96, 61)],
                     'right': [(10, 69, 29, 95), (42, 68, 61, 95), (74, 68, 93, 95)]},
    'aqua-grunt-f': {'up': [(11, 100, 31, 126), (40, 99, 60, 126), (76, 99, 95, 126)],
                     'down': [(13, 129, 33, 158), (44, 128, 65, 158), (77, 128, 97, 158)],
                     'right': [(8, 163, 30, 189), (39, 162, 62, 189), (73, 162, 94, 189)]},
    'magma-grunt-m': {'up': [(128, 4, 146, 30), (160, 2, 178, 30), (193, 2, 211, 30)],
                      'down': [(128, 34, 146, 62), (160, 33, 178, 62), (192, 33, 210, 62)],
                      'right': [(127, 66, 144, 94), (159, 65, 176, 94), (191, 65, 208, 94)]},
    'magma-grunt-f': {'up': [(126, 96, 144, 125), (159, 95, 177, 125), (192, 94, 210, 125)],
                      'down': [(128, 129, 146, 158), (159, 127, 178, 157), (192, 127, 211, 157)],
                      'right': [(123, 163, 145, 191), (154, 162, 177, 191), (188, 162, 209, 191)]},
}
GRUNT_CODES = {'aqua-grunt-m': 293, 'aqua-grunt-f': 294, 'magma-grunt-m': 302, 'magma-grunt-f': 192}

# Wally. Front: hyo-oppa's trainer collection, top row, third figure (31x67). Overworld: CalculusNova's sheet, the
# walking block without the backpack (top left; Sapphire's own Wally has none): 16x32 cells, columns down, up, side
# (facing left, as Gen 3's), rows stand, step, step; right = the side column mirrored (as Gen 3 shows it).
WALLY_CELLS = {d: [(x, y, x + 16, y + 32) for y in (6, 41, 76)] for d, x in (('down', 43), ('up', 62), ('left', 81))}
WALLY = {'front': (95, 6, 126, 86), 'walk': WALLY_CELLS}

# ------------------------------------------------------------------------------------------------ loading the sheets

_sheets = {}
def sheet(name):
    """RGBA array of a sheet with its background clear (alpha 0) and every other pixel opaque."""
    if name in _sheets:
        return _sheets[name]
    from PIL import Image
    spec = SHEETS[name]
    a = np.array(Image.open(os.path.join(INCOMING, spec['file'])).convert('RGBA')).copy()
    bg = spec['bg']
    if bg == 'alpha':
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    elif bg == 'white':                      # white around the figures = clear; white inside an outline stays
        a[..., 3] = np.where(_outside(np.all(a[..., :3] == 255, -1)), 0, 255)
    elif bg == 'jpeg':
        pass                                 # handled per sprite by jpeg_sprite()
    else:
        m = np.zeros(a.shape[:2], bool)
        for c in bg:
            m |= np.all(a[..., :3] == c, -1)
        a[..., 3] = np.where(m, 0, 255)
    a[a[..., 3] == 0] = 0                    # clear pixels: their colour does not matter
    if spec.get('scale'):                    # an exact integer upscale (every k x k block one colour): back to 1x
        k = spec['scale']
        if spec.get('cell'):                 # per cell, its k x k blocks may start up to k-1 pixels in (each cell's
            n = spec['cell']                 # figure clear at its edges, so every block keeps one sample: lossless)
            for y in range(0, a.shape[0], n):
                for x in range(0, a.shape[1], n):
                    assert any(_upscaled(a[y:y + n, x:x + n], k, oy, ox) for oy in range(k) for ox in range(k)), \
                        (name, y, x)
        else:
            assert _upscaled(a, k), name
        a = a[::k, ::k].copy()
    a[a[..., 3] == 0] = 0
    _sheets[name] = a
    return a

def _upscaled(a, k, oy=0, ox=0):
    """True if RGBA a, moved (oy, ox) pixels down / right onto a clear canvas of whole k x k blocks, is made of
    one-colour k x k blocks (i.e. an exact k-times upscale whose blocks start oy / ox pixels in)."""
    H, W = a.shape[:2]
    p = np.zeros(((H + oy + k - 1) // k * k, (W + ox + k - 1) // k * k, 4), a.dtype)
    p[oy:oy + H, ox:ox + W] = a
    return bool((p.reshape(p.shape[0] // k, k, p.shape[1] // k, k, 4) == p[::k, ::k][:, None, :, None]).all())

def _outside(m):
    """Pixels of mask m connected (4-way) to the picture's border through m."""
    from collections import deque
    H, W = m.shape
    out = np.zeros_like(m)
    q = deque()
    for y in range(H):
        for x in (0, W - 1):
            if m[y, x] and not out[y, x]: out[y, x] = True; q.append((y, x))
    for x in range(W):
        for y in (0, H - 1):
            if m[y, x] and not out[y, x]: out[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True; q.append((ny, nx))
    return out

def crop(name, r):
    """RGBA crop of frame r = (x0, y0, x1, y1[, flags]) with only the figure that lies in the rectangle: pixels of
    figures that only reach into it from outside (their larger part outside) are dropped."""
    a = sheet(name)
    x0, y0, x1, y1 = r[:4]
    c = a[y0:y1, x0:x1].copy()
    lab, n = _label(c[..., 3] > 0)
    if n > 1:
        sizes = np.bincount(lab.ravel())[1:]
        main = int(np.argmax(sizes)) + 1
        ys, xs = np.nonzero(lab == main)
        my0, my1, mx0, mx1 = ys.min() - 3, ys.max() + 3, xs.min() - 3, xs.max() + 3
        H, W = lab.shape
        for k in range(1, n + 1):
            ys, xs = np.nonzero(lab == k)
            border = ys.min() == 0 or xs.min() == 0 or ys.max() == H - 1 or xs.max() == W - 1
            inside = ((ys >= my0) & (ys <= my1) & (xs >= mx0) & (xs <= mx1)).mean()
            if k != main and border and inside < 0.5:
                c[lab == k] = 0
    if len(r) > 4 and 'm' in r[4]:
        c = c[:, ::-1].copy()
    return c

def _label(m):
    """8-connected components of mask m: (labels, count)."""
    from collections import deque
    H, W = m.shape
    lab = np.zeros((H, W), int)
    n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        n += 1
        lab[y, x] = n
        q = deque([(y, x)])
        while q:
            cy, cx = q.popleft()
            for ny in (cy - 1, cy, cy + 1):
                for nx in (cx - 1, cx, cx + 1):
                    if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n; q.append((ny, nx))
    return lab, n

def colours_of(arrs):
    """{rgb: count} over RGBA crops."""
    from collections import Counter
    c = Counter()
    for a in arrs:
        c.update(map(tuple, a[a[..., 3] > 0][:, :3].tolist()))
    return c

def merge_near(counts, near=NEAR):
    """(map rgb -> representative rgb, [merged groups]): colours no channel more than `near` apart join the group of
    their most used member (union of chains)."""
    cols = sorted(counts, key=lambda c: -counts[c])
    parent = {c: c for c in cols}
    def find(c):
        while parent[c] != c:
            parent[c] = parent[parent[c]]; c = parent[c]
        return c
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            if max(abs(a[k] - b[k]) for k in range(3)) <= near:
                ra, rb = find(a), find(b)
                if ra != rb:
                    if counts[ra] >= counts[rb]: parent[rb] = ra
                    else: parent[ra] = rb
    groups = {}
    for c in cols:
        groups.setdefault(find(c), []).append(c)
    rep = {}
    for root, members in groups.items():
        best = max(members, key=lambda c: counts[c])
        for c in members:
            rep[c] = best
    return rep, [sorted(m, key=lambda c: -counts[c]) for m in groups.values() if len(m) > 1]

# ------------------------------------------------------------------------------------------------ placement

def _bbox(c):
    ys, xs = np.nonzero(c[..., 3])
    return ys.min(), xs.min(), ys.max() + 1, xs.max() + 1

def head_match(ref, refpos, c, dy=None, rows=10, span=8):
    """Position (y, x) for crop c whose head (top `rows` rows of the figure) best matches crop `ref` placed at refpos
    = (y, x). With dy given, only x is searched (the sheet's own vertical placement)."""
    ry0 = _bbox(ref)[0]
    cy0 = _bbox(c)[0]
    best = None
    dys = [dy] if dy is not None else range(-span, span + 1)
    for d in dys:
        for dx in range(-span, span + 1):
            # c at (refpos[0] + d, refpos[1] + dx): compare the overlap of both heads
            score = 0
            top = min(refpos[0] + ry0, refpos[0] + d + cy0)
            for y in range(top, top + rows):
                ya, yb = y - refpos[0], y - refpos[0] - d
                if not (0 <= ya < ref.shape[0] and 0 <= yb < c.shape[0]):
                    continue
                for x in range(max(0, dx), min(ref.shape[1], c.shape[1] + dx)):
                    pa, pb = ref[ya, x], c[yb, x - dx]
                    if pa[3] and pb[3]:
                        score += 2 if tuple(pa[:3]) == tuple(pb[:3]) else -1
                    elif pa[3] or pb[3]:
                        score -= 1
            key = (score, -abs(dx), -abs(d))
            if best is None or key > best[0]:
                best = (key, refpos[0] + d, refpos[1] + dx)
    return best[1], best[2]

def paste(canvas, c, y, x, what=''):
    """Paste crop c at (y, x) into an RGBA canvas; returns the number of figure pixels that fall outside."""
    H, W = canvas.shape[:2]
    ys, xs = np.nonzero(c[..., 3])
    Y, X = ys + y, xs + x
    ok = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
    canvas[Y[ok], X[ok]] = c[ys[ok], xs[ok]]
    return int((~ok).sum())

def place_group(name, rects, size=32, feet=30, cx=16, ref_pos=None, ref=None):
    """Frames of one direction: [(canvas RGBA, lost pixels, (y, x))], the first = the reference (stand), its feet on
    row `feet` and centred on column `cx` (moved up if a step frame would end below the frame's last row). ref/ref_pos:
    register the reference by its head to another frame instead (e.g. fishing to the walking frame). Frames of the same
    sheet row as the reference keep the sheet's vertical placement; others are registered by the head."""
    crops = [crop(name, r) for r in rects]
    r0 = crops[0]
    by0, bx0, by1, bx1 = _bbox(r0)
    if ref is None:
        pos0 = (feet - (by1 - 1), int(round(cx - (bx0 + bx1) / 2)))
    else:
        pos0 = head_match(ref, ref_pos, r0)
    poss = []
    for k, (r, c) in enumerate(zip(rects, crops)):
        if k == 0:
            pos = pos0
        elif r[1] < rects[0][3] and rects[0][1] < r[3]:       # same sheet row
            pos = head_match(r0, pos0, c, dy=r[1] - rects[0][1])
        else:
            pos = head_match(r0, pos0, c)
        poss.append(pos)
    if ref is None:                                           # keep every frame inside (a step's foot may go lower)
        low = max(p[0] + _bbox(c)[2] - 1 for p, c in zip(poss, crops))
        if low > size - 1 - (size - 32) // 2:
            poss = [(p[0] - (low - (size - 1)), p[1]) for p in poss]
    out = []
    for pos, c in zip(poss, crops):
        cv = np.zeros((size, size, 4), np.uint8)
        lost = paste(cv, c, *pos)
        out.append((cv, lost, pos))
    return out

# ------------------------------------------------------------------------------------------------ Black 2 sheet plans
DIRS = ('up', 'down', 'left', 'right')          # Black 2's direction order in every sheet

def _shift(cv, dy, dx, size):
    out = np.zeros((size, size, 4), np.uint8)
    lost = paste(out, cv, dy, dx)
    return out, lost

def brendan_plan():
    """{code: (name, [(RGBA frame, lost pixels, source note)])} for Nate's codes 231-239 (Black 2's layouts)."""
    n = 'brendan'
    walk = {d: place_group(n, B['walk'][d]) for d in DIRS}
    run = {d: place_group(n, B['run'][d]) for d in DIRS}
    def frames(g, note):
        return [(cv, lost, note) for cv, lost, _ in g]
    plan = {}
    plan[231] = ('walk-run', sum((frames(walk[d], f'walk {d}') for d in DIRS), []) +
                 sum((frames(run[d], f'run {d}') for d in DIRS), []))
    bk = B['bike']
    order = {'up': [2, 1, 4], 'down': [2, 1, 4], 'left': [2, 1, 3], 'right': [1, 2, 3]}   # (stand, step, step)
    bike = {d: place_group(n, [bk[d][i] for i in order[d]]) for d in DIRS}
    still = {d: place_group(n, [bk[d][0]])[0] for d in DIRS}
    plan[232] = ('bike', sum((frames(bike[d], f'bike {d}') for d in DIRS), []) +
                 [(still[d][0], still[d][1], f'bike still {d}') for d in DIRS])
    plan[233] = ('surf', [(*place_group(n, B['surf'][d], feet=28)[0][:2], f'surf {d}') for d in DIRS])
    def reg(rects, d, note, size=32):
        """frames of one sheet row registered by the head to the walking stand frame of direction d"""
        cv0, _, pos0 = walk[d][0]
        ref = crop(n, B['walk'][d][0])
        off = (size - 32) // 2
        g = place_group(n, rects, size=size, ref=ref, ref_pos=(pos0[0] + off, pos0[1] + off))
        return [(cv, lost, note) for cv, lost, _ in g]
    itf, bf, tu = B['item_front'], B['ball_front'], B['turn_up']
    plan[234] = ('item', reg([itf[0], itf[3]], 'down', 'item: stand, item raised'))
    plan[235] = ('action2', reg([itf[0], B['front_extra'][1]], 'down', 'action2: stand, hands in front'))
    a5 = reg([(*tu[0][:4], 'm'), (*tu[1][:4], 'm')], 'left', 'action5: turning (mirrored)') + \
        reg([tu[2], tu[3], tu[4]], 'up', 'action5: back')
    plan[236] = ('action5', a5)
    plan[237] = ('throw', reg([bf[0], bf[2], bf[3], bf[3]], 'down', 'throw: stand, ball, raised, raised (no throw frame)'))
    ao = B['arms_out']
    bal = []
    for d in DIRS:
        if d in ao:
            g = reg([ao[d][0], ao[d][1], ao[d][0], ao[d][2]], d, f'balance {d}')
        else:                                          # no side frames on the sheet: the walking frames stand in
            g = [(walk[d][i][0], walk[d][i][1], f'balance {d}: walking frame (none on the sheet)') for i in (0, 1, 0, 2)]
        bal += g
    plan[238] = ('balance', bal)
    fi = B['fish']
    plan[239] = ('fishing', reg(fi['up'], 'up', 'fish up', 64) + reg(fi['down'], 'down', 'fish down', 64) +
                 reg(fi['left'], 'left', 'fish left', 64))
    return plan

def npc_plan(name, rows, mirror_left=False):
    """12 frames (up, down, left, right x stand, step, step) of a type-3 NPC sheet."""
    out = []
    for d in DIRS:
        rects = rows[d] if d in rows else [(*r[:4], 'm') for r in rows['right']]
        out += [(cv, lost, f'{d}' + (' (right mirrored)' if d not in rows else '')) for cv, lost, _ in
                place_group(name, rects)]
    return out

def wally_plan():
    """Wally's 12 frames (CalculusNova): every 16x32 cell is the artist's own frame registration, so cells are placed
    whole (Gen 3's one-pixel step bob kept, as Sapphire's own Wally has it), with one offset for the sheet: the down
    standing frame's feet on row 30, centred on column 16 (npc_plan's standing placement). Right = left mirrored."""
    rows = WALLY['walk']
    y0, x0, y1, x1 = _bbox(crop('wally', rows['down'][0]))
    dy, dx = 30 - (y1 - 1), int(round(16 - (x0 + x1) / 2))
    out = []
    for d in DIRS:
        rects = rows[d] if d in rows else [(*r[:4], 'm') for r in rows['left']]
        for r in rects:
            cv = np.zeros((32, 32, 4), np.uint8)
            out.append((cv, paste(cv, crop('wally', r), dy, dx), d + (' (left mirrored)' if d not in rows else '')))
    return out

# ------------------------------------------------------------------------------------------------ review sheets

def _donor_frames(code):
    table = sprites.ow_table(FILES)
    sh, rec = sprites.ow_sheet_of(FILES, code, table)
    btx = narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS))[sh]
    frames, pname, pal = sprites.btx_decode(btx)
    rgb = [sprites.bgr555_to_rgb(c) for c in pal]
    out = []
    for _, w, h, px in frames:
        a = np.frombuffer(bytes(px), np.uint8).reshape(h, w)
        im = np.zeros((h, w, 4), np.uint8)
        for i in range(1, 16):
            im[a == i] = (*rgb[i], 255)
        out.append(im)
    return out, dict(sheet=sh, controller=rec['spriteControllerType'], textures=[f[0] for f in frames], palette=pname,
                     size=[frames[0][1], frames[0][2]])

def review_rows(rows, path, scale=3, bg=(120, 200, 120, 255)):
    """rows = [(label, [RGBA arrays])] -> one PNG (frames boxed)."""
    from PIL import Image, ImageDraw
    pad = 4
    W = max(sum(a.shape[1] + pad for a in ims) for _, ims in rows) + 2 * pad
    H = sum(max(a.shape[0] for a in ims) + 14 + pad for _, ims in rows) + pad
    out = Image.new('RGBA', (W, H), bg)
    d = ImageDraw.Draw(out)
    y = pad
    for label, ims in rows:
        d.text((pad, y), label, fill=(0, 0, 0, 255))
        y += 12
        x = pad
        for a in ims:
            d.rectangle((x - 1, y - 1, x + a.shape[1], y + a.shape[0]), outline=(90, 150, 90, 255))
            out.alpha_composite(Image.fromarray(a), (x, y))
            x += a.shape[1] + pad
        y += max(a.shape[0] for a in ims) + pad
    out = out.resize((W * scale, H * scale), Image.NEAREST)
    out.save(path)
    return path

# ------------------------------------------------------------------------------------------------ colours

def index_frames(frames, near=NEAR, max_colours=15):
    """RGBA frames -> (index arrays, 16 RGB colours (0 = clear), merges, colour count). The palette is the frames' own
    colours (near-identical ones counted once, see NEAR), most used first. Raises ValueError when more than
    max_colours remain (Black 2's 4 bpp limit: report, never reduce)."""
    counts = colours_of(frames)
    rep, merges = merge_near(counts, near)
    reps = {}
    for c, n in counts.items():
        reps[rep[c]] = reps.get(rep[c], 0) + n
    if len(reps) > max_colours:
        raise ValueError(f'{len(reps)} colours (Black 2 allows {max_colours})')
    order = sorted(reps, key=lambda c: -reps[c])
    idx = {c: i + 1 for i, c in enumerate(order)}
    pal = [(0, 0, 0)] + order + [(0, 0, 0)] * (15 - len(order))
    out = []
    for f in frames:
        a = np.zeros(f.shape[:2], np.uint8)
        ys, xs = np.nonzero(f[..., 3])
        for y, x in zip(ys, xs):
            a[y, x] = idx[rep[tuple(int(v) for v in f[y, x, :3])]]
        out.append(a)
    return out, pal, merges, len(reps)

def colour_report(frames, near=NEAR):
    counts = colours_of(frames)
    rep, merges = merge_near(counts, near)
    return len(counts), len(set(rep.values())), merges

def may_plan():
    """Luckygirl88's May on Rosa's layouts (240-248): {code: (name, frames)}; frames that do not fit lose pixels."""
    n = 'may'
    out = {}
    walk = {d: place_group(n, M['walk'][d]) for d in DIRS}
    run = {d: place_group(n, M['run'][d]) for d in DIRS}
    out[240] = ('walk-run', [f for d in DIRS for f in walk[d]] + [f for d in DIRS for f in run[d]])
    out[241] = ('bike', [f for d in DIRS for f in place_group(n, M['bike'][d])] +
                [place_group(n, [r])[0] for r in M['bike']['still']])
    out[243] = ('item', place_group(n, M['item']))
    out[244] = ('action2', place_group(n, M['action2']))
    out[245] = ('action5', place_group(n, M['action5'][:2]) + place_group(n, M['action5'][2:]))
    out[246] = ('throw', place_group(n, M['throw']))
    out[247] = ('balance', [f for d in DIRS for f in place_group(n, M['balance'][d])])
    out[248] = ('fishing', [f for d in ('up', 'down', 'left') for f in place_group(n, M['fish'][d], size=64, feet=46, cx=32)])
    return out

# ------------------------------------------------------------------------------------------------ the grunts' JPEG
JPEG_BG_LUMA = 200        # background = near-white pixels (lighter than this, nearly grey) reached from the frame's border
JPEG_BG_SAT = 30          # (max - min channel below this); the outline and the figure's light colours stop it
JPEG_CLEAN = 18           # a pixel is "clean" when its 3x3 neighbours differ by at most this in every channel
JPEG_RADIUS = 26          # clean colours within this distance are one true colour
JPEG_MIN_SUPPORT = 4      # a true colour needs this many clean pixels

def _luma(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114

def jpeg_frames(grunt, margin=2):
    """The grunt's 9 frames as RGB crops (margin around the boxes) with a figure mask each."""
    from PIL import Image
    a = np.array(Image.open(os.path.join(INCOMING, SHEETS['grunts']['file'])).convert('RGB')).astype(int)
    out = []
    for d in ('up', 'down', 'right'):
        for (x0, y0, x1, y1) in G[grunt][d]:
            c = a[max(0, y0 - margin):y1 + margin, max(0, x0 - margin):x1 + margin]
            fig = ~_outside((_luma(c) > JPEG_BG_LUMA) & (c.max(-1) - c.min(-1) < JPEG_BG_SAT))
            lab, n = _label(fig)
            if n > 1:                                    # keep the figure, drop bits of neighbouring frames
                sizes = np.bincount(lab.ravel())[1:]
                fig = lab == int(np.argmax(sizes)) + 1
            out.append((d, c, fig))
    return out

def _lab(rgb):
    """sRGB (0-255, ... x 3) -> CIE Lab (D65)."""
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

JPEG_R = 9.0              # Lab radius of one true colour
JPEG_MIN_WEIGHT = 0.0     # (diagnostics)

def jpeg_palette(frames, k_max=15):
    """The true colours of one sprite (its 9 frames). Every figure pixel is weighted by how flat its surroundings are
    (JPEG blur smears edges; flat areas keep the real colour). Modes of that weighted colour density (in Lab, radius
    JPEG_R) are taken strongest first, each removing the pixels around it; a mode's colour is the median of its
    flattest pixels. At most 15 (Black 2's limit). Returns (colours, weights)."""
    px, wt = [], []
    for _, c, m in frames:
        H, W = m.shape
        for y in range(H):
            for x in range(W):
                if not m[y, x]:
                    continue
                y0, y1, x0, x1 = max(0, y - 1), min(H, y + 2), max(0, x - 1), min(W, x + 2)
                nb = c[y0:y1, x0:x1][m[y0:y1, x0:x1]]
                spread = np.abs(nb - c[y, x]).max()
                px.append(c[y, x]); wt.append(1.0 / (1.0 + spread / 20.0) ** 2)
    RGB = np.array(px, float); w = np.array(wt); L = _lab(RGB)
    D = np.sqrt(((L[:, None] - L[None]) ** 2).sum(-1))
    alive = np.ones(len(L), bool)
    modes = []
    while alive.any() and len(modes) < k_max:
        dens = ((D <= JPEG_R) & alive[None]).astype(float) @ (w * alive)
        dens[~alive] = -1
        i = int(np.argmax(dens))
        centre = L[i]
        for _ in range(10):                                      # mean shift
            sel = alive & (np.sqrt(((L - centre) ** 2).sum(-1)) <= JPEG_R)
            centre = (L[sel] * w[sel, None]).sum(0) / w[sel].sum()
        sel = alive & (np.sqrt(((L - centre) ** 2).sum(-1)) <= JPEG_R)
        weight = float(w[sel].sum())
        if weight < JPEG_MIN_WEIGHT:
            break
        flat = sel & (w >= np.quantile(w[sel], 0.5))
        modes.append((tuple(int(round(v)) for v in np.median(RGB[flat], 0)), round(weight, 1)))
        alive &= np.sqrt(((L - centre) ** 2).sum(-1)) > JPEG_R
    return [m_[0] for m_ in modes], [m_[1] for m_ in modes]

def jpeg_snap(grunt):
    """{direction: [RGBA crops]} of a grunt with every figure pixel snapped to its nearest true colour, the palette,
    and the cluster supports (for the report)."""
    frames = jpeg_frames(grunt)
    pal, support = jpeg_palette(frames)
    P = np.array(pal)
    out = {}
    for d, c, m in frames:
        dist = ((c[:, :, None, :] - P[None, None]) ** 2).sum(-1)
        k = dist.argmin(-1)
        rgba = np.zeros(c.shape[:2] + (4,), np.uint8)
        rgba[..., :3] = P[k]
        rgba[..., 3] = np.where(m, 255, 0)
        rgba[~m] = 0
        out.setdefault(d, []).append(rgba)
    return out, pal, support

def jpeg_review(path, scale=6):
    """Before (the JPEG, each grunt's 9 frames) / after (snapped, clear background shown green) at `scale`x, with the
    true colours found."""
    from PIL import Image, ImageDraw
    rows = []
    for g in G:
        fr = jpeg_frames(g)
        snapped, pal, sup = jpeg_snap(g)
        before = [np.dstack([c.astype(np.uint8), np.full(c.shape[:2], 255, np.uint8)]) for _, c, _ in fr]
        after = [a for d in ('up', 'down', 'right') for a in snapped[d]]
        rows.append((g, before, after, pal))
    cw = max(c.shape[1] for _, b, _, _ in rows for c in b) + 2
    ch = max(c.shape[0] for _, b, _, _ in rows for c in b) + 2
    W = 9 * cw * 2 + 30
    H = len(rows) * (ch + 22) + 10
    out = Image.new('RGBA', (W * scale, H * scale), (60, 60, 60, 255))
    d = ImageDraw.Draw(out)
    y = 4
    for g, before, after, pal in rows:
        d.text((4 * scale, y * scale), f'{g}: JPEG (left)  /  snapped to its {len(pal)} true colours (right)',
               fill=(255, 255, 255, 255))
        for i, c in enumerate(pal):
            d.rectangle(((W - 16 * 8 + i * 8) * scale, y * scale, (W - 16 * 8 + i * 8 + 7) * scale, (y + 7) * scale),
                        fill=(*c, 255))
        y += 10
        for k, (b, a) in enumerate(zip(before, after)):
            x = k * cw
            out.alpha_composite(Image.fromarray(b).resize((b.shape[1] * scale, b.shape[0] * scale), Image.NEAREST),
                                (x * scale, y * scale))
            bg = Image.new('RGBA', (a.shape[1], a.shape[0]), (120, 200, 120, 255))
            bg.alpha_composite(Image.fromarray(a))
            out.alpha_composite(bg.resize((a.shape[1] * scale, a.shape[0] * scale), Image.NEAREST),
                                ((9 * cw + 20 + x) * scale, y * scale))
        y += ch + 12
    out.save(path)
    return path

# ------------------------------------------------------------------------------------------------ writing src/sprites
# One colour beyond Black 2's 15 that only the merge below resolves (REPORTED to the user, not silent): Brendan's bike
# up/down frames use a lighter skin tone (223,165,123) on 30 pixels next to (214,153,110) (1-2 DS colour steps apart).
# DiegoWT's May bike sheet (16 colours): a gold (200,152,56) on 12 pixels next to her hair's (208,152,72).
# Changed pixels: screenshots/sprites/community_bike_merges.png
# Wolfang62's Birch (16 colours; the page allows edits with credit): the single closest pair by the near-identical
# measure (NEAR: largest channel difference, 13; 1-2 DS colour steps) is a brown (96,56,51) on 6 pixels (one shadow
# pixel at the hand in each side frame) and the hair's (88,64,64); merged into the more used one. (In CIE Lab the two
# dark hair browns (64,48,48) / (88,64,64) are a little closer, but merging them would recolour 439 pixels: the hair
# loses its dark shading.) Before/after: screenshots/birch_sprite/birch_overworld_review.png
EXTRA_MERGES = {87: {(207, 150, 111): (208, 152, 112), (255, 209, 182): (248, 208, 184), (209, 147, 104): (208, 152, 112), (248, 248, 248): (239, 237, 252), (71, 47, 47): (56, 40, 56), (197, 197, 205): (194, 192, 223), (64, 64, 88): (56, 40, 56), (48, 45, 87): (56, 40, 56)},   # Wally (Kymotonian/Klein Studio): 23 colours -> 15, the 8 closest pairs (user approved 2026-10-17, edits allowed)
                232: {(223, 165, 123): (214, 153, 110)}, 241: {(200, 152, 56): (208, 152, 72)},
                104: {(96, 56, 51): (88, 64, 64)}}

def _merge_extra(frames, code):
    m = EXTRA_MERGES.get(code)
    if not m:
        return frames
    out = []
    for f in frames:
        f = f.copy()
        for a, b in m.items():
            sel = np.all(f[..., :3] == a, -1) & (f[..., 3] > 0)
            f[sel, :3] = b
        out.append(f)
    return out

def _replace_folder(kind_dir, n, keep):
    import sprite_upgrade as U
    U._replace_folder(kind_dir, n, keep)

def write_overworld(code, name, frames, note, source):
    """Indexed frames + palette + sprite.json for object code `code` (same sheet layout as Black 2's)."""
    don, meta = _donor_frames(code)
    assert len(frames) == len(don) and frames[0].shape[:2] == don[0].shape[:2], (code, len(frames), len(don))
    frames = _merge_extra(frames, code)
    idx, pal, merges, n = index_frames(frames)
    kind_dir = os.path.join(GEN5, 'overworld')
    folder = os.path.join(kind_dir, f'{code:03d}-{name}')
    _replace_folder(kind_dir, code, folder)
    os.makedirs(folder, exist_ok=True)                  # frame_NN.png are overwritten (Black 2's frame count)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    w, h = meta['size']
    for i, a in enumerate(idx):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), a.tobytes(), w, h, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='overworld', code=code, sheet=meta['sheet'], frames=len(idx), size=meta['size'],
        controller=meta['controller'], textures=meta['textures'], palette=meta['palette'], name=name, note=note,
        source=source, colours=n, merged_colours=[[list(c) for c in g] for g in merges],
        made_by='b2tools/sprite_community.py'))
    return folder, n, merges

BRENDAN_NAMES = {231: 'walk-run', 232: 'bike', 233: 'surf', 234: 'item', 235: 'action2', 236: 'action5', 237: 'throw',
                 238: 'balance', 239: 'fishing'}

def build_brendan_ow():
    done = []
    for code, (name, fr) in brendan_plan().items():
        assert all(l == 0 for _, l, _ in fr), (code, [l for _, l, _ in fr])
        folder, n, merges = write_overworld(code, f'brendan-{name}', [f for f, _, _ in fr],
                                            f'Brendan (player), {name}',
                                            f"community: {SHEETS['brendan']['file']} by hyo-oppa")
        done.append(f'{os.path.relpath(folder, ROOT)} ({n} colours)')
    return done

def build_grunts_ow():
    done = []
    for g, code in GRUNT_CODES.items():
        snapped, pal, sup = jpeg_snap(g)
        rows = {d: [f for f in snapped[d]] for d in snapped}
        frames = []
        for d in DIRS:
            if d in rows:
                crops = rows[d]
            else:
                crops = [f[:, ::-1].copy() for f in rows['right']]
            frames += [cv for cv, _, _ in place_crops(crops, [r[1] for r in G[g]['right' if d == 'left' else d]])]
        folder, n, merges = write_overworld(code, g, frames, f'Team {g.split("-")[0].title()} grunt '
                                            f'({g[-1].upper()})', f"community: {SHEETS['grunts']['file']} by "
                                            f"Kimmylube / AzureAquarian (JPEG snapped to its {len(pal)} true colours)")
        done.append(f'{os.path.relpath(folder, ROOT)} ({n} colours)')
    return done

def place_crops(crops, ys, size=32, feet=30, cx=16):
    """place_group for crops already cut (the JPEG's): same rules (sheet rows keep the sheet's vertical placement)."""
    r0 = crops[0]
    by0, bx0, by1, bx1 = _bbox(r0)
    pos0 = (feet - (by1 - 1), int(round(cx - (bx0 + bx1) / 2)))
    poss = [pos0] + [head_match(r0, pos0, c, dy=y - ys[0]) for c, y in zip(crops[1:], ys[1:])]
    low = max(p[0] + _bbox(c)[2] - 1 for p, c in zip(poss, crops))
    if low > size - 1:
        poss = [(p[0] - (low - (size - 1)), p[1]) for p in poss]
    out = []
    for pos, c in zip(poss, crops):
        cv = np.zeros((size, size, 4), np.uint8)
        out.append((cv, paste(cv, c, *pos), pos))
    return out

# ------------------------------------------------------------------------------------------------ battle fronts
FRONTS = {   # slot: (sheet, rect, name, note, layout candidates (Black 2 front sprites whose parts and intro gesture
             # the picture is cut onto; the first that shows every pixel is used), or 'still')
    # (Nate's own sprite 0 garbles the picture: his intro is a crouching turn drawn with other parts; Maxie on 108,
    # his current layout, loses 2 pixels of the head) -- both checked frame by frame
    0: ('brendan', B['front'], 'brendan', 'Brendan (rival battles, Hall of Fame)', [108]),
    148: ('maxie', X['front'], 'maxie', 'Maxie (Team Magma leader)', [51]),
    # Wally on the layout of hyo-oppa's Brendan (and of the classic Wally): same placement and size, so both stand alike
    127: ('trainers_hyo', WALLY['front'], 'wally', 'Wally', [108]),
}

# Colours merged in a front picture beyond the near-identical ones (REPORTED to the user, not silent; the page allows
# edits with credit). Wally (hyo-oppa) has 19 colours; the DS's 5-bit colour shows (66,82,120) and (66,82,121) as one
# (the NEAR merge), leaving 18 for Black 2's 15: the three closest pairs on the DS (CIE Lab distance, as _lab) are
# merged, each into the more used colour (fewest pixels changed): a 2-pixel lavender into the coat's light blue (dE 11.0),
# a 1-pixel brown into the hand's shadow brown (dE 11.4), the 32 near-white pixels (eye, collar, ball, shoes) into the
# trousers' light grey (dE 13.6). Before/after: screenshots/wally_sprite/wally_front_merges.png
FRONT_MERGES = {127: {(189, 181, 215): (158, 169, 195), (146, 98, 62): (182, 125, 83), (233, 233, 249): (214, 218, 210)}}

def _merge_front(rgba, slot):
    m = FRONT_MERGES.get(slot)
    if not m:
        return rgba
    rgba = rgba.copy()
    for a, b in m.items():
        sel = np.all(rgba[..., :3] == a, -1) & (rgba[..., 3] > 0)
        assert sel.any(), (slot, a)
        rgba[sel, :3] = b
    return rgba

def front_still(sheet_name, rect):
    """80x80 RGBA still: the sheet's picture, feet on row 78 (as Black 2's), centred."""
    c = crop(sheet_name, rect)
    y0, x0, y1, x1 = _bbox(c)
    c = c[y0:y1, x0:x1]
    assert c.shape[0] <= 80 and c.shape[1] <= 80, f'{sheet_name} front {c.shape[:2]} is bigger than 80x80'
    out = np.zeros((80, 80, 4), np.uint8)
    paste(out, c, 79 - c.shape[0], (80 - c.shape[1]) // 2)
    return out

def front_sprite(slot, layout):
    """(still 80x80 indices, parts 128x256, palette, report) on Black 2 front sprite `layout`'s parts."""
    import sprite_upgrade as U
    sheet_name, rect, name, note, _ = FRONTS[slot]
    rgba = _merge_front(front_still(sheet_name, rect), slot)
    (still,), pal, merges, n = index_frames([rgba])
    dparts, dstill, dpal, sp = U.tr_donor(layout)
    off = mcss.still_offset(sp, dparts, dstill)
    W, H = mcss.CANVAS
    ys, xs = np.nonzero(still)
    whole, partsm = mcss.coverage(sp, dparts)
    def lost(dx, dy):
        X_, Y_ = xs + off[0] + dx, ys + off[1] + dy
        ok = (X_ >= 0) & (X_ < W) & (Y_ >= 0) & (Y_ < H)
        return (int((~ok).sum() + (~whole[Y_[ok], X_[ok]]).sum()), int((~ok).sum() + (~partsm[Y_[ok], X_[ok]]).sum()))
    shifts = sorted(((dx, dy) for dx in range(-12, 13) for dy in range(-4, 3)), key=lambda d: abs(d[0]) + abs(d[1]))
    dx, dy = min(shifts, key=lambda d: lost(*d))
    fig = np.zeros((H, W), np.uint8)
    fig[ys + off[1] + dy, xs + off[0] + dx] = still[ys, xs]
    # the outline colour for under-painting: the darkest colour
    outline = int(np.argmin([sum(c) if i else 999 for i, c in enumerate(pal)]))
    parts, rep = mcss.distribute(sp, dparts, fig, outline)
    rep = dict(rep, shift=(dx, dy), colours=n, merges=merges)
    return still, parts, pal, rep, sp

def write_front(slot):
    import sprite_upgrade as U
    sheet_name, rect, name, note, layouts = FRONTS[slot]
    for layout in layouts:
        still, parts, pal, rep, sp = front_sprite(slot, layout)
        if not rep['lost_in_whole'] and not rep['lost_in_parts']:
            break
    else:
        raise SystemExit(f'{name}: no layout shows every pixel ({rep})')
    kind_dir = os.path.join(GEN5, 'trainer', 'front')
    folder = os.path.join(kind_dir, f'{slot:03d}-{name}')
    _replace_folder(kind_dir, slot, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), parts.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), still.tobytes(), 80, 80, pal)
    meta = dict(kind='trainer', side='front', sprite=slot, archive=sprites.ARC_TR['front'], files=sprites.tr_files(slot),
                name=name, note=note, source=f"community: {SHEETS[sheet_name]['file']} by {SHEETS[sheet_name]['author']}",
                layout=f'parts and animations of Black 2 front sprite {layout}', colours=rep['colours'],
                merged_colours=[[list(c) for c in g] for g in rep['merges']], made_by='b2tools/sprite_community.py')
    if slot in FRONT_MERGES:
        meta['extra_merges'] = [[list(a), list(b)] for a, b in FRONT_MERGES[slot].items()]
    if layout != slot:
        meta['mcss_from'] = layout
    sprites.write_json(os.path.join(folder, 'sprite.json'), meta)
    return folder, layout, rep

# ------------------------------------------------------------------------------------------------ Brendan's back
# hyo-oppa's five Gen 4-style back frames (stand, arm back, arm raised, throw, follow-through) on Nate's back sprite 0
# (cells 0 48x128, 1 24x72, 2 32x56, 3 40x48, 4 64x128, 5 88x112), as whole-figure poses
# (sprite_upgrade_player_backs.py's method: cells keep their texture rectangles, multi-cell nodes are re-pointed):
#   standing (frame 1)   = cell 0 in multi-cells 0 and 1 (the slide-in and the throw's first 20 ticks)
#   arm raised (frame 3) = cells 4 + 1 in multi-cell 2 (65 wide: one pixel more than cell 4)
#   throw (frame 4)      = cell 5 in multi-cells 3 and 4 (multi-cell 3 has one node: the throw shows 8 ticks earlier)
# Frames 2 and 5 have no texture room left (each pose needs its own cells). Cells 2, 3 cleared. The sheet's own frame
# grid (79 px apart, bottom edge row 364) keeps the poses' relative placement; the bottom edge = the screen's edge.
BACK_POSES = [(0, [0], [(0, 0, None), (0, 1, 0), (1, 0, None), (1, 1, 0)]),
              (2, [4, 1], [(2, 0, 4), (2, 1, 1)]),
              (3, [5], [(3, 0, 5), (4, 0, 5)])]
BACK_CLEAR, BACK_BLANK_SEQ = [2, 3], 3

def brendan_back_figures(sp, tex):
    """Canvas pictures (RGBA) of the three poses, Nate's head centre over Brendan's standing head."""
    spec = B['back']
    H, W = mcss.CANVAS[::-1]
    d = mcss.render(sp, tex, 0, 0)
    dy0 = int(np.nonzero(d.any(1))[0][0])
    dcols = np.nonzero(d[dy0:dy0 + 20].any(0))[0]
    out = []
    for k, cells, nodes in BACK_POSES:
        r = spec['frames'][k]
        c = crop('brendan', r)
        gx = spec['grid_x0'] + spec['pitch'] * k               # the frame's left edge on the sheet
        out.append((c, r[0] - gx, r[1] - spec['bottom']))      # crop, x in its frame, y above the bottom edge
    c0, fx0, fy0 = out[0]
    ys, xs = np.nonzero(c0[..., 3])
    hcols = xs[ys < ys.min() + 20]
    dx = int(round((dcols.min() + dcols.max()) / 2 - (hcols.min() + hcols.max()) / 2)) - fx0
    figs = []
    for c, fx, fy in out:
        cv = np.zeros((H, W, 4), np.uint8)
        lost = paste(cv, c, mcss.ORIGIN[1] + fy, dx + fx)
        assert lost == 0
        figs.append(cv)
    return figs

def write_brendan_back():
    import sprite_upgrade_player_backs as P
    slot = 0
    e, tex, dpal, sp = P.donor(slot)
    figs = brendan_back_figures(sp, tex)
    idx, pal, merges, n = index_frames(figs)
    O = mcss.ORIGIN
    new = np.zeros_like(tex)
    edits, lost = [], 0
    for (k, cells, nodes), fig in zip(BACK_POSES, idx):
        qs = {ci: P.quad(sp, ci) for ci in cells}
        corners = P.place(fig, [(qs[ci][2] - qs[ci][0], qs[ci][3] - qs[ci][1]) for ci in cells])
        own = np.zeros(fig.shape, bool)
        node_xy = {}
        for ci, (cx, cy) in zip(cells, corners):
            qx0, qy0, _, _ = qs[ci]
            nx, ny = cx - O[0] - qx0, cy - O[1] - qy0
            node_xy[ci] = (nx, ny)
            X_, Y_, Uu, V = mcss.cell_pixels(sp.cells[ci], (0, 1, 1, nx, ny))
            X_ = X_ + O[0]; Y_ = Y_ + O[1]
            ok = (X_ >= 0) & (X_ < fig.shape[1]) & (Y_ >= 0) & (Y_ < fig.shape[0])
            mine = np.zeros(len(X_), bool)
            mine[ok] = ~own[Y_[ok], X_[ok]]
            val = np.zeros(len(X_), np.uint8)
            val[mine] = fig[Y_[mine], X_[mine]]
            new[V, Uu] = val
            own[Y_[mine], X_[mine]] = True
        lost += int(((fig != 0) & ~own).sum())
        for mc, node, ci in nodes:
            if ci is None:
                edits.append(dict(mc=mc, node=node, seq=BACK_BLANK_SEQ))
            else:
                edits.append(dict(mc=mc, node=node, seq=P.seq_of(sp, ci), x=int(node_xy[ci][0]), y=int(node_xy[ci][1])))
    for ci in BACK_CLEAR:
        for (x, y, w, h, u, v, hf, vf) in sp.cells[ci]:
            new[v:v + h, u:u + w] = 0
    assert lost == 0, f'brendan back: {lost} pixels outside every cell'
    kind_dir = os.path.join(GEN5, 'trainer', 'back')
    folder = os.path.join(kind_dir, f'{slot:03d}-brendan')
    _replace_folder(kind_dir, slot, folder)
    os.makedirs(folder, exist_ok=True)
    _, _, still = sprites.tr_decode_image(e[8 * slot], 'static')
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), new.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), bytes(still), 80, 80, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='trainer', side='back', sprite=slot, archive=sprites.ARC_TR['back'], files=sprites.tr_files(slot),
        name='brendan', note='Brendan (player back)', source=f"community: {SHEETS['brendan']['file']} by hyo-oppa "
        '(back frames 1, 3, 4 of 5)', layout='cells, quads and throw timing of Black 2 back sprite 0; whole-figure poses',
        colours=n, merged_colours=[[list(c) for c in g] for g in merges], node_edits=edits, still_multicells=[2, 3, 4],
        made_by='b2tools/sprite_community.py'))
    e2 = list(e)
    e2[8 * slot + 4] = mcss.set_nodes(e[8 * slot + 4], edits)
    e2[8 * slot + 5] = mcss.still_translations(e[8 * slot + 5], 1, [2, 3, 4])
    return folder, (mcss.Sprite(e2, 8 * slot), new, pal)

# ------------------------------------------------------------------------------------------------ main

def analyze():
    """Every planned sheet / picture: size fit and colour count (Black 2: 15 + clear); what is installable."""
    lines = []
    def row(what, frames, lost=None):
        rgb, merged, merges = colour_report(frames)
        ok = merged <= 15 and not lost
        lines.append(f"{'OK  ' if ok else 'OVER'} {what}: {rgb} colours, {merged} after near-identical merges"
                     + (f', {lost} pixels outside the frame' if lost else '') + (f' merges {merges}' if merges else ''))
    for code, (name, fr) in brendan_plan().items():
        row(f'Brendan {code} {name}', _merge_extra([f for f, _, _ in fr], code), sum(l for _, l, _ in fr))
    for code, (name, fr) in may_plan().items():
        row(f'May {code + 0} {name}', [f for f, _, _ in fr], sum(l for _, l, _ in fr))
    lines.append('OVER May 242 surf: no sitting (surf) frames on the sheet (8 head-only frames at its right edge)')
    row('May front', [crop('may', M['front'])])
    row('May back (3 bodies + 5 arm parts)', [crop('may', r) for r in M['back']['bodies'] + M['back']['arms']])
    row('Maxie overworld 303 (Ruby 353)', [f for f, _, _ in npc_plan('maxie', X['walk'])])
    row('Maxie front 148', [crop('maxie', X['front'])])
    row('Archie overworld 353 (Ruby 303)', [f for f, _, _ in npc_plan('archie', A['walk'])])
    row('Brendan front (sheet)', [crop('brendan', B['front'])])
    row('Wally front 127 (hyo-oppa, as drawn)', [crop('trainers_hyo', WALLY['front'])])
    row('Wally front 127 (with FRONT_MERGES)', [_merge_front(crop('trainers_hyo', WALLY['front']), 127)])
    fr = wally_plan()
    row('Wally overworld 87 (CalculusNova)', [f for f, _, _ in fr], sum(l for _, l, _ in fr))
    fr = ess_walk_plan('birch')
    row('Birch overworld 104 (Wolfang62, as drawn)', [f for f, _, _ in fr], sum(l for _, l, _ in fr))
    row('Birch overworld 104 (with EXTRA_MERGES)', _merge_extra([f for f, _, _ in fr], 104))
    from PIL import Image
    g = Image.open(os.path.join(INCOMING, 'brendan_front_hyo-oppa.gif'))
    gf = []
    for i in range(g.n_frames):
        g.seek(i); gf.append(np.array(g.convert('RGBA')))
    row(f'Brendan front GIF ({len(gf)} frames)', gf)
    import sprite_upgrade_player_backs as P
    e, tex, dpal, sp = P.donor(0)
    row('Brendan back (frames 1, 3, 4)', brendan_back_figures(sp, tex))
    for gname in G:
        snapped, pal, sup = jpeg_snap(gname)
        lines.append(f'OK   grunt {gname}: JPEG snapped to {len(pal)} true colours')
    return lines

MAY_NAMES = {240: 'walk-run', 241: 'bike', 242: 'surf', 243: 'item', 244: 'action2', 245: 'action5', 246: 'throw',
             247: 'balance', 248: 'fishing'}

def build_may_ow():
    done = []
    src = "community: src/sprites/community/incoming/may_oras_DiegoWT/ by DiegoWT (Zailens commissioned)"
    for code, (name, fr) in may_d_plan().items():
        assert all(l == 0 for _, l, _ in fr), (code, [l for _, l, _ in fr])
        folder, n, merges = write_overworld(code, f'may-{name}', [f for f, _, _ in fr], f'May (player), {name}',
                                            src + ': ' + '; '.join(sorted({t for _, _, t in fr})))
        done.append(f'{os.path.relpath(folder, ROOT)} ({n} colours)')
    return done

def build_archie_ow():
    fr = archie_d_plan()
    assert all(l == 0 for _, l, _ in fr)
    folder, n, merges = write_overworld(353, 'archie', [f for f, _, _ in fr], 'Archie (Team Aqua leader)',
                                        "community: src/sprites/community/incoming/archie_oras_DiegoWT.png by DiegoWT "
                                        "(Kyledove commissioned)")
    return [f'{os.path.relpath(folder, ROOT)} ({n} colours)']

def build_wally_ow():
    fr = ess_walk_plan('wally_kk')
    assert all(l == 0 for _, l, _ in fr)
    folder, n, merges = write_overworld(87, 'wally', [f for f, _, _ in fr], 'Wally',
                                        "community: src/sprites/community/incoming/wally_sheet_Kymotonian_KleinStudio.png "
                                        "by Kymotonian and Klein Studio (8 colour pairs merged: EXTRA_MERGES[87])")
    return [f'{os.path.relpath(folder, ROOT)} ({n} colours)']

def build_birch_ow():
    fr = ess_walk_plan('birch')
    assert all(l == 0 for _, l, _ in fr)
    folder, n, merges = write_overworld(104, 'prof-birch', [f for f, _, _ in fr], 'Prof. Birch (every Birch object)',
                                        "community: src/sprites/community/incoming/birch_sheet_Wolfang62.png by "
                                        "Wolfang62 (one colour merged: EXTRA_MERGES[104])")
    return [f'{os.path.relpath(folder, ROOT)} ({n} colours)']

def merges_review(path):
    """The extra-merged sheets (EXTRA_MERGES): every frame as drawn / as installed, changed pixels in magenta, 6x."""
    plans = {232: brendan_plan()[232][1], 241: may_d_plan()[241][1]}
    rows = []
    for code, fr in plans.items():
        before = [f for f, _, _ in fr]
        after = _merge_extra(before, code)
        marked = []
        for b, a in zip(before, after):
            m = a.copy()
            m[np.any(a != b, -1)] = (255, 0, 255, 255)
            marked.append(m)
        n = sum(int(np.any(a != b, -1).sum()) for a, b in zip(after, before))
        rows.append((f'{code}: as drawn', before))
        rows.append((f'{code}: changed pixels (magenta), {n} in all: ' + ', '.join(f'{k} -> {v}' for k, v in
                                                                            EXTRA_MERGES[code].items()), marked))
    return review_rows(rows, path, scale=6)

def build(parts):
    out = []
    if 'brendan' in parts:
        out += build_brendan_ow()
        f, lay, rep = write_front(0)
        out.append(f'{os.path.relpath(f, ROOT)} on layout {lay} ({rep["colours"]} colours)')
        f, _ = write_brendan_back()
        out.append(os.path.relpath(f, ROOT))
    if 'maxie' in parts:
        f, lay, rep = write_front(148)
        out.append(f'{os.path.relpath(f, ROOT)} on layout {lay} ({rep["colours"]} colours)')
    if 'grunts' in parts:
        out += build_grunts_ow()
    if 'may' in parts:
        out += build_may_ow()
    if 'archie' in parts:
        out += build_archie_ow()
    if 'wally' in parts:
        f, lay, rep = write_front(127)
        out.append(f'{os.path.relpath(f, ROOT)} on layout {lay} ({rep["colours"]} colours, shift {rep["shift"]})')
        out += build_wally_ow()
    if 'birch' in parts:
        out += build_birch_ow()
    return out


def _folder_frames(folder):
    """RGBA frames of an installed overworld folder (or the HEAD version with git=True)."""
    from PIL import Image
    meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
    out = []
    for i in range(meta['frames']):
        out.append(np.array(Image.open(os.path.join(folder, f'frame_{i:02d}.png')).convert('RGBA')))
    return out

def _git_frames(rel, n):
    import subprocess, io
    from PIL import Image
    out = []
    for i in range(n):
        try:
            data = subprocess.run(['git', 'show', f'HEAD:{rel}/frame_{i:02d}.png'], cwd=ROOT, capture_output=True,
                                  check=True).stdout
        except Exception:
            return None
        im = Image.open(io.BytesIO(data))
        a = np.array(im.convert('RGBA'))
        a[np.array(im) == 0] = 0                     # index 0 = clear
        out.append(a)
    return out

def _trainer_png(rel, name, git=False):
    import subprocess, io
    from PIL import Image
    if git:
        data = subprocess.run(['git', 'show', f'HEAD:{rel}/{name}'], cwd=ROOT, capture_output=True, check=True).stdout
        im = Image.open(io.BytesIO(data))
    else:
        im = Image.open(os.path.join(ROOT, rel, name))
    a = np.array(im.convert('RGBA'))
    a[np.array(im) == 0] = 0
    return a

def review(path=None):
    """screenshots/sprites/community_review.png: per installed sheet Black 2's own / the current (HEAD) / the new art;
    and community_grunts_jpeg.png (the JPEG before/after)."""
    import mcss as _m
    import sprite_upgrade as U
    rows = []
    for code in list(BRENDAN_NAMES) + list(MAY_NAMES) + list(GRUNT_CODES.values()) + [353, 87, 104]:
        folder = [os.path.join(GEN5, 'overworld', d) for d in os.listdir(os.path.join(GEN5, 'overworld'))
                  if d.split('-')[0] == f'{code:03d}'][0]
        rel = os.path.relpath(os.path.join(SRC, 'overworld', os.path.basename(folder)), ROOT)
        new = _folder_frames(folder)
        don, _ = _donor_frames(code)
        rows.append((f'{code} Black 2', don))
        old = _git_frames(rel, len(new))
        if old:
            rows.append((f'{code} classic (src/sprites)', old))
        rows.append((f'{code} NEW {os.path.basename(folder)}', new))
    os.makedirs(SHOTS, exist_ok=True)
    p1 = review_rows(rows, path or os.path.join(SHOTS, 'community_review.png'), scale=3)
    rows = []
    for slot, rel in ((0, 'src/sprites_gen5/trainer/front/000-brendan'), (148, 'src/sprites_gen5/trainer/front/148-maxie'),
                      (127, 'src/sprites_gen5/trainer/front/127-wally')):
        old = _trainer_png(rel.replace('sprites_gen5', 'sprites'), 'static.png', git=True)
        new = _trainer_png(rel, 'static.png')
        meta = sprites.read_json(os.path.join(ROOT, rel, 'sprite.json'))
        lay = meta.get('mcss_from', slot)
        e = narc_entries(arc_path(FILES, sprites.ARC_TR['front']))
        sp = _m.Sprite(e, 8 * lay)
        from PIL import Image
        parts = np.array(Image.open(os.path.join(ROOT, rel, 'parts.png')))
        pal = sprites.read_pal(os.path.join(ROOT, rel, 'palette.pal'))
        T = sp.length(0)
        anim = [np.array(U.rgba(_m.render(sp, parts, 0, t), pal))[30:150, 40:160] for t in range(0, T, max(1, T // 8))]
        rows.append((f'front {slot}: classic still / NEW still / NEW intro gesture (layout {lay})', [old, new] + anim))
    import sprite_upgrade_player_backs as P
    folder, (sp2, tex, pal) = None, (None, None, None)
    e = narc_entries(arc_path(FILES, sprites.ARC_TR['back']))
    meta = sprites.read_json(os.path.join(GEN5, 'trainer', 'back', '000-brendan', 'sprite.json'))
    e2 = list(e)
    e2[4] = _m.set_nodes(e[4], meta['node_edits'])
    e2[5] = _m.still_translations(e[5], 1, meta['still_multicells'])
    sp2 = _m.Sprite(e2, 0)
    from PIL import Image
    tex = np.array(Image.open(os.path.join(GEN5, 'trainer', 'back', '000-brendan', 'parts.png')))
    pal = sprites.read_pal(os.path.join(GEN5, 'trainer', 'back', '000-brendan', 'palette.pal'))
    ticks = [(0, 0), (1, 10), (1, 25), (1, 36), (1, 45), (1, 99)]
    rows.append(('back 0 NEW: standing, then the throw at ticks 10, 25, 36, 45, 99 (screen edge = bottom)',
                 [np.array(U.rgba(_m.render(sp2, tex, an, t), pal))[:_m.ORIGIN[1], 24:-24] for an, t in ticks]))
    p2 = review_rows(rows, os.path.join(SHOTS, 'community_review_battle.png'), scale=2)
    p3 = jpeg_review(os.path.join(SHOTS, 'community_grunts_jpeg.png'), scale=6)
    return [os.path.relpath(p, ROOT) for p in (p1, p2, p3)]


# ------------------------------------------------------------------------------------------------ DiegoWT's sheets
# Pokemon Essentials layout (1x after the 2x check): rows down, left, right, up; 4 columns (stand, step, stand, step;
# surf / bike idle: one picture repeated). Every cell is the artist's own frame registration, so cells are placed
# whole: a 32x32 cell is Black 2's frame moved by one offset per sheet (the walking stand frame's feet on row 30); the
# fishing cells (48x40, "_offset") stand on the same bottom-centre as a 32x32 cell (Essentials anchors a frame at its
# bottom-centre), inside Black 2's 64x64 fishing frame (the 32x32 frame's place there: 16 in from the left and top).
ROW = {'down': 0, 'left': 1, 'right': 2, 'up': 3}

def ess_cell(name, d, c, cw=32, ch=32):
    a = sheet(name)
    r = ROW[d]
    return a[ch * r:ch * r + ch, cw * c:cw * c + cw].copy()

def ess_place(cell, size=32, dy=0):
    """A cell (bottom-centre anchored) in a Black 2 frame of `size`; returns (frame, lost pixels)."""
    ch, cw = cell.shape[:2]
    base = (size - 32) // 2                                  # the 32x32 frame's place inside a 64x64 one
    out = np.zeros((size, size, 4), np.uint8)
    lost = paste(out, cell, base + 32 - ch + dy, base + 16 - cw // 2)
    return out, lost

def ess_feet_dy(name='may_walk'):
    """Offset that puts the walking down-stand frame's feet on Black 2's row 30."""
    return 30 - (_bbox(ess_cell(name, 'down', 0))[2] - 1)

def may_d_plan():
    """{code: (name, [(frame, lost, note)])}: DiegoWT's May on Rosa's codes 240-248."""
    dy = ess_feet_dy('may_walk')
    def F(name, d, c, note, size=32, cw=32, ch=32, flip=False):
        cell = ess_cell(name, d, c, cw, ch)
        if flip:
            cell = cell[:, ::-1].copy()
        fr, lost = ess_place(cell, size, dy)
        return fr, lost, note
    def walkset(name, label):
        return [F(name, d, c, f'{label} {d}') for d in DIRS for c in (0, 1, 3)]
    plan = {240: ('walk-run', walkset('may_walk', 'walk') + walkset('may_run', 'run'))}
    stills = [F(BIKE_STILLS, d, 0, f'bike still {d} ({BIKE_STILLS})') for d in DIRS]
    plan[241] = ('bike', walkset('may_bike', 'bike') + stills)
    plan[242] = ('surf', [F('may_surf', d, 0, f'surf {d}') for d in DIRS])
    stand = F('may_walk', 'down', 0, 'stand (walking frame)')
    plan[243] = ('item', [stand, F('may_hm', 'down', 2, 'item raised (use HM)')])
    plan[244] = ('action2', [stand, F('may_hm', 'down', 0, 'hands in front (use HM)')])
    plan[245] = ('action5', [F('may_walk', 'left', 0, 'left (walking frame)')] * 2 +
                 [F('may_walk', 'up', 0, 'up (walking frame)')] * 3)
    plan[246] = ('throw', [stand, F('may_hm', 'down', 0, 'ball (use HM)'), F('may_hm', 'down', 2, 'raised (use HM)'),
                           F('may_hm', 'down', 3, 'throw (use HM)')])
    plan[247] = ('balance', [F('may_walk', d, c, f'balance {d} (walking frame)') for d in DIRS for c in (0, 1, 0, 3)])
    fish = []
    for d in ('up', 'down', 'left'):                         # Black 2: up side x2, forward x2; down/left raised x2, out x2
        # the fishing cells are not anchored like the walking ones (the figure sits 16 rows higher in its 48x40
        # cell, in game): each direction's row is registered by the head to the walking stand frame (as Brendan's)
        walk = ess_cell('may_walk', d, 0)
        cells = [ess_cell('may_fish', d, c, 48, 40) for c in (2, 3, 0, 1)]
        y, x = head_match(walk, (16 + dy, 16), cells[0], span=20)
        for c in cells:
            fr = np.zeros((64, 64, 4), np.uint8)
            fish.append((fr, paste(fr, c, y, x), f'fish {d} (head-registered to the walking frame)'))
    plan[248] = ('fishing', fish)
    return plan

# The bike's four still frames: the bike idle sheet would need three colours merged (18 with the pedalling frames), so
# the pedalling sheet's first frame per direction stands still instead (16 colours: one merge, EXTRA_MERGES[241])
BIKE_STILLS = 'may_bike'

def ess_walk_plan(name):
    """12 frames (up, down, left, right x stand, step, step) of an Essentials walking sheet: columns 0, 1, 3."""
    dy = ess_feet_dy(name)
    out = []
    for d in DIRS:
        for c in (0, 1, 3):
            fr, lost = ess_place(ess_cell(name, d, c), 32, dy)
            out.append((fr, lost, f'{d}'))
    return out

def archie_d_plan():
    return ess_walk_plan('archie_d')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'analyze'
    if cmd == 'analyze':
        print('\n'.join(analyze()))
    elif cmd == 'build':
        print('\n'.join(build(sys.argv[2:] or ['brendan', 'maxie', 'grunts', 'may', 'archie', 'wally', 'birch'])))
    elif cmd == 'review':
        print(review(*sys.argv[2:3]))
