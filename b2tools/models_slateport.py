"""Slateport City's buildings: Sapphire's shapes and colours, Black 2 textures (group towns2, res 340-347, 354).

    python3 models_slateport.py ../work/buildings/slateport

Writes one .dae per model (+ the texture images they use, copied from the game's own building texture sets in
work/tex/extNN, palettes.txt and textures.txt). Also holds the geometry helpers models_mauville.py and
models_verdanturf.py use. The Pokemon Center / Mart are the shared res 0 / res 3 (models_oldale.py), the Contest
Hall is group towns3's res 362 (the same 5x5 Gen 3 hall as Fallarbor's).

Sapphire footprints (data/plans/SlateportCity.json; 'roof row' = the walk-behind row above the solid rows):
  house    4 wide, rows 17-19 + roof row (Name Rater's house; also the left half of house 2), door in column 1
  annex    6 wide, rows 42-44 + roof row, no door (the right half of house 2)
  fanclub  5 wide, rows 23-26 + roof row, chamfered corners, door in the middle (Pokemon Fan Club)
  museum   6 wide, rows 23-26, double door in the middle (Oceanic Museum)
  shipyard 8 wide, rows 33-38 + roof row, door in column 2 (Stern's Shipyard), the two dock frames east of it
  harbor   7 wide, rows 7-12, door in the middle (Harbor)
  awning   market entrance canopy, 5 tiles wide, posts on the row below the canopy (two in town)
  stall    market stall, green hip roof on two front posts (six in the market)
  statue   the white stone monument in the south plaza (prop tiles x 32-33, rows 52-54), res 354 (buildings_audit)
Origin = footprint centre on the ground, +z = front (south). Front walls sit at z = +20 (the 'front' value in
data/towns/SlateportCity.json), i.e. 4 units into the door tile as Black 2 places its buildings; walls over a door are
DOOR_WALL (38) high so Black 2's door models (y 32) stand under the eaves with wall over them (walls of 32-34 put the
eaves at 30-32, in front of the doors' tops: door_fix 2026-10-11, b2tools/door_check.py).

Size matters: every model of every town lives in the one exterior pack, which the game loads whole into the field
heap (a 376 KB pack 0 left the map black in a test, 344 KB loaded; notes/TOWNS_TOWNS2.md). So faces facing north
(never seen by Gen 5's fixed camera) are left out, and whole textures that repeat (roof tiles, panels) are drawn as
one polygon per face with the GPU repeating them (WRAP) instead of one polygon per repeat.
"""
import os, sys, math, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exterior_layers import separate
from dae import Model
import buildings as B
from buildings import Region, shadow, DOOR_WALL, pc_door_hood, cull_unseen

TEX = os.path.join(HERE, '..', 'work', 'tex')
UP, E, N = (0, 1, 0), (1, 0, 0), (0, 0, -1)
WRAPPED = set()

def tiled(tex, size):
    """A whole texture the GPU repeats (WRAP): one polygon per face, however many repeats."""
    r = Region(tex, size, 0, 0, size[0], size[1]); r.wrap = True; WRAPPED.add(tex)
    return r

# --- pack 0 (Nuvema/Accumula) and the slice's textures (already in pack 0's set) ---
MADO = Region('h_mado', (16, 16), 0, 0, 16, 16)                    # window glass
GLASS = Region('pc_win1', (16, 128), 1, 64, 15, 96)                # blue glass panel
CREST = Region('pc_win1', (16, 128), 0, 32, 16, 48)                # Poke Ball emblem
ORANGE_TILE = tiled('yane_001', (16, 64))                          # orange roof tiles (scalloped rows)
GREY = Region('gate_1', (64, 32), 24, 22, 64, 32)                  # grey concrete
BEIGE = Region('t06_h_03_a', (64, 64), 0, 0, 30, 14)               # beige siding (Oldale's walls)
YELLOW = Region('t06_h_03_a', (64, 64), 0, 24, 22, 54)             # plain warm beige
RIBS = Region('t06_h_03_a', (64, 64), 34, 18, 62, 54)              # orange corrugated roof
TRIM = Region('t06_h_03_a', (64, 64), 0, 56, 32, 62)               # brick-red band
WINDOW = Region('c14_h1_body', (64, 64), 38, 32, 62, 46)           # framed window (glass transparent)
POST = Region('c14_h1_body', (64, 64), 14, 24, 17, 56)             # wooden post
BEAM = Region('c14_h1_body', (64, 64), 36, 20, 64, 28)             # dark wood band
PLANKS = Region('c14_h1_body', (64, 64), 18, 0, 46, 18)            # vertical dark wood planks
SKIRT = Region('c14_h1_body', (64, 64), 36, 56, 64, 64)            # orange skirting
SHINGLE = Region('c14_h2_yane', (64, 64), 0, 16, 16, 32)           # tan shingles
SHINGLE_LT = Region('c14_h2_yane', (64, 64), 0, 0, 16, 16)         # light cream shingles
OLIVE = tiled('c4m_yane_001', (32, 64))                            # olive-green roof tiles
WHITE = Region('r4_b03_yane01', (64, 64), 2, 18, 14, 26)           # white panel
BLUE = Region('r4_b03_yane01', (64, 64), 4, 34, 60, 54)            # flat blue
VENT = Region('r4_b03_yane01', (64, 64), 24, 10, 60, 26)           # louvred vent
# --- new for towns2 (or shared with other groups) ---
PURPLE = tiled('c13_ho01b', (64, 64))                              # pack 54 (Virbank): muted purple roof panels
PINK = tiled('h2', (16, 64))                                       # pack 9 (Mistralton): pink roof tiles, eave row at the bottom
METAL = tiled('c4_bp01', (32, 32))                                 # pack 6 (Nimbasa theater): pale blue panels (also towns3)
GREEN_WALL = tiled('d5_conte01a', (64, 32))                        # pack 8 (Driftveil): green ribbed container, dark base
MINT = tiled('d5_conte01b', (32, 32))                              # pack 8 (Driftveil): light green panels
GOLD = Region('wbase_a', (32, 32), 4, 5, 32, 19)                   # pack 6 (Nimbasa): gold horizontal stripes, two
GOLD_REP = (512, 14)                                               # periods; plain across, so one cell per face width

SOURCES = {'h_mado': 'ext00', 'pc_win1': 'ext00', 'yane_001': 'ext00', 'gate_1': 'ext00', 'h_kage': 'ext00',
           't06_h_03_a': 'ext53', 'c14_h1_body': 'ext57', 'c14_h2_yane': 'ext57', 'c4m_yane_001': 'ext02',
           'r4_b03_yane01': 'ext05', 'c13_ho01b': 'ext54', 'h2': 'ext09', 'c4_bp01': 'ext06',
           'd5_conte01a': 'ext08', 'd5_conte01b': 'ext08', 'wbase_a': 'ext06'}

# ------------------------------------------------------------------------------------------------ geometry
def face(m, region, origin, u, v, outline, rep=None, color=(1, 1, 1)):
    """buildings.face, plus whole repeating textures (tiled()) as one polygon with uv = (s / rs, t / rt)."""
    if not getattr(region, 'wrap', False):
        return B.face(m, region, origin, u, v, outline, rep, color)
    rs, rt = rep or (region.w, region.h)
    s0 = math.floor(min(p[0] for p in outline) / rs + 1e-6); t0 = math.floor(min(p[1] for p in outline) / rt + 1e-6)
    verts = [tuple(origin[k] + s * u[k] + t * v[k] for k in range(3)) + (s / rs - s0, t / rt - t0) for s, t in outline]
    for k in range(1, len(verts) - 1):
        m.tri(region.tex, [verts[0], verts[k], verts[k + 1]], color)

def rect(m, region, origin, u, v, w, h, rep=None):
    face(m, region, origin, u, v, [(0, 0), (w, 0), (w, h), (0, h)], rep)

def decal(m, region, center, u, v, w, h):
    """One copy of the region stretched over w x h, centred on center."""
    o = [center[k] - u[k] * w / 2 - v[k] * h / 2 for k in range(3)]
    face(m, region, o, u, v, [(0, 0), (w, 0), (w, h), (0, h)], (w, h))

def slope(m, region, a, b, c, d, rep=None):
    """Planar roof face through a, b (lower edge, left to right seen from outside) and c, d (upper edge, right to
    left; c == d makes a triangle). Texture along the eave (u) and up the slope (v); rep (rs, None) fits one repeat
    to the slope's height."""
    u = [b[k] - a[k] for k in range(3)]; lu = math.sqrt(sum(x * x for x in u)); u = [x / lu for x in u]
    w = [d[k] - a[k] for k in range(3)]; dot = sum(w[k] * u[k] for k in range(3))
    v = [w[k] - dot * u[k] for k in range(3)]; lv = math.sqrt(sum(x * x for x in v)); v = [x / lv for x in v]
    to2d = lambda p: (sum((p[k] - a[k]) * u[k] for k in range(3)), sum((p[k] - a[k]) * v[k] for k in range(3)))
    pts = [to2d(p) for p in (a, b, c, d)]
    if c == d: pts = pts[:3]
    if rep and rep[1] is None: rep = (rep[0], max(p[1] for p in pts))
    face(m, region, a, u, v, pts, rep)

def gable_roof(m, region, x0, x1, z0, z1, y0, y1, rep=None, back=True):
    zc = (z0 + z1) / 2
    slope(m, region, (x0, y0, z1), (x1, y0, z1), (x1, y1, zc), (x0, y1, zc), rep)
    if back: slope(m, region, (x1, y0, z0), (x0, y0, z0), (x0, y1, zc), (x1, y1, zc), rep)

def hip_roof(m, region, x0, x1, z0, z1, y0, rx0, rx1, rz, y1, rep=None):
    A, Bq, C, D = (x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)
    R0, R1 = (rx0, y1, rz), (rx1, y1, rz)
    slope(m, region, A, Bq, R1, R0, rep); slope(m, region, C, D, R0, R1, rep)
    slope(m, region, Bq, C, R1, R1, rep); slope(m, region, D, A, R0, R0, rep)

def octagon(x0, x1, z0, z1, c):
    """Rectangle with chamfered corners, counter-clockwise seen from above (+z south): SW..SE..NE..NW."""
    return [(x0 + c, z1), (x1 - c, z1), (x1, z1 - c), (x1, z0 + c), (x1 - c, z0), (x0 + c, z0), (x0, z0 + c), (x0, z1 - c)]

def rectangle(x0, x1, z0, z1):
    return [(x0, z1), (x1, z1), (x1, z0), (x0, z0)]

def walls(m, region, pts, y0, y1, rep=None, north=False):
    """Outward-facing walls along a closed outline (order as octagon()); walls facing north are left out."""
    for (xa, za), (xb, zb) in zip(pts, pts[1:] + pts[:1]):
        L = math.hypot(xb - xa, zb - za)
        if L < 1e-6 or (not north and (xb - xa) / L < -0.3): continue      # outward normal z = dx / L
        rect(m, region, (xa, y0, za), ((xb - xa) / L, 0, (zb - za) / L), UP, L, y1 - y0, rep)

def box_walls(m, x0, x1, z0, z1, y0, y1, region, rep=None):
    walls(m, region, rectangle(x0, x1, z0, z1), y0, y1, rep)

def flat(m, region, pts, y, rep=None):
    """Upward-facing polygon (order as octagon())."""
    x0 = min(p[0] for p in pts); z1 = max(p[1] for p in pts)
    face(m, region, (x0, y, z1), E, N, [(px - x0, z1 - pz) for px, pz in pts], rep)

def frustum(m, region, outer, inner, y0, y1, rep=None):
    """Sloped ring from the outer outline at y0 up to the inner outline at y1 (same number of points)."""
    n = len(outer)
    for k in range(n):
        a, b, c, d = outer[k], outer[(k + 1) % n], inner[(k + 1) % n], inner[k]
        slope(m, region, (a[0], y0, a[1]), (b[0], y0, b[1]), (c[0], y1, c[1]), (d[0], y1, d[1]), rep)

def post(m, region, x, z, w, y0, y1):
    """Square post of width w (south, east and west sides)."""
    walls(m, region, rectangle(x - w / 2, x + w / 2, z - w / 2, z + w / 2), y0, y1, (w, y1 - y0))

def window(m, x, y, z, w=20, h=12):
    decal(m, MADO, (x, y, z + 0.15), E, UP, w - 2, h - 2)
    decal(m, WINDOW, (x, y, z + 0.3), E, UP, w, h)

def gable_ends(m, region, x0, x1, z0, z1, y, h, rep):
    """Triangles closing a gable roof whose ridge runs along x (above the side walls at x0 / x1)."""
    d = z1 - z0
    face(m, region, (x1, y, z1), (0, 0, -1), UP, [(0, 0), (d, 0), (d / 2, h)], rep)
    face(m, region, (x0, y, z0), (0, 0, 1), UP, [(0, 0), (d, 0), (d / 2, h)], rep)

def barrel(m, region, x0, x1, z0, z1, y0, h, segs=6, rs=16):
    """Rounded (half-ellipse) roof along x from the front eave (z1) over a crest h high to the back eave (z0), with
    end caps. For a tiled region: u repeats every rs along x, v runs from each eave (0) to the crest (1)."""
    zc, r = (z0 + z1) / 2, (z1 - z0) / 2
    pts = [(zc + r * math.cos(math.pi * k / segs), y0 + h * math.sin(math.pi * k / segs)) for k in range(segs + 1)]
    arc = [0.0]
    for (za, ya), (zb, yb) in zip(pts, pts[1:]): arc.append(arc[-1] + math.hypot(zb - za, yb - ya))
    half = arc[-1] / 2
    vv = [min(s, arc[-1] - s) / half for s in arc]
    for k in range(segs):
        (za, ya), (zb, yb) = pts[k], pts[k + 1]
        q = [(x0, ya, za, x0 / rs, vv[k]), (x1, ya, za, x1 / rs, vv[k]), (x1, yb, zb, x1 / rs, vv[k + 1]),
             (x0, yb, zb, x0 / rs, vv[k + 1])]
        m.quad(region.tex, q)
    for x, sgn in ((x1, 1), (x0, -1)):        # end caps (planar mapping)
        verts = [(x, y, z, z / rs, (y - y0) / h * 0.5) for z, y in pts]
        if sgn > 0: verts = verts[::-1]          # (pts are counter-clockwise seen from -x: both caps faced inwards
                                                 # and were culled, the Game Corner's roof open at its ends; map_gfx)
        for k in range(1, len(verts) - 1):
            m.tri(region.tex, [verts[0], verts[k], verts[k + 1]])

def gable_house(name, roof, wall, x0, x1, z0, z1, H, windows=(), roof_x=None, roof_z=4, ridge=16, posts=True,
                wall_rep=(30, 17), roof_rep=None):
    """Box walls (front at z1), gable roof (ridge along x), windows [(x, y)], wooden corner posts."""
    m = Model(name)
    rx0, rx1 = roof_x or (x0 - 3, x1 + 3)
    shadow(m, rx0 - 2, rx1 + 2, z0 - roof_z - 4, z1 + 8)
    box_walls(m, x0, x1, z0, z1, 0, H, wall, rep=wall_rep)
    gable_ends(m, wall, x0, x1, z0, z1, H, ridge * (z1 - z0) / (z1 - z0 + 2 * roof_z), wall_rep)
    gable_roof(m, roof, rx0, rx1, z0 - roof_z, z1 + roof_z, H - 2, H - 2 + ridge, rep=roof_rep)
    for wx, wy in windows: window(m, wx, wy, z1)
    if posts:
        for x in (x0 + 1.5, x1 - 1.5):
            rect(m, POST, (x - 1.5, 0, z1 + 0.25), E, UP, 3, H, rep=(3, H))
    return m

def write_models(out, models, sources=SOURCES):
    """Each model's DAE plus the texture images, palettes.txt and textures.txt next to them."""
    os.makedirs(out, exist_ok=True)
    used = set()
    for name, m in models.items():
        separate(m)        # layers >= 1 unit apart (melonDS flicker; b2tools/exterior_layers.py)
        cull_unseen(m)     # nothing the field camera never sees (pack 0 heap; buildings.cull_unseen)
        n = m.write(os.path.join(out, f'{name}.dae'),
                    wrap={t: ('WRAP', 'WRAP') if t in WRAPPED else ('CLAMP', 'CLAMP') for t in m.tris})
        used |= set(m.tris)
        print(f'{name}: {n} triangles, textures {sorted(m.tris)}')
    for t in sorted(used):
        shutil.copy(os.path.join(TEX, sources[t], t + '.png'), os.path.join(out, t + '.png'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in sorted(used)))
    open(os.path.join(out, 'textures.txt'), 'w').write(''.join(f'{sources[t]} {t}\n' for t in sorted(used)))

# ------------------------------------------------------------------------------------------------ models
def house():
    """Slateport house (4 wide): slate-purple gable roof, yellow siding, door in column 1, window right (res 340)."""
    return gable_house('sl_house', PURPLE, GOLD, -30, 30, -20, 20, DOOR_WALL, windows=[(14, 19)],
                       roof_x=(-33, 33), roof_rep=(32, 32), wall_rep=GOLD_REP)

def annex():
    """Right half of Slateport's house 2 (6 wide, no door): same build, two windows (res 341). The west roof edge
    meets the house's (the two models stand 80 units apart)."""
    return gable_house('sl_annex', PURPLE, GOLD, -46, 46, -20, 20, DOOR_WALL, windows=[(-24, 19), (8, 19)],
                       roof_x=(-47, 49), roof_rep=(32, 32), wall_rep=GOLD_REP)

def fanclub():
    """Pokemon Fan Club (5x4, chamfered): warm beige walls with windows, gold striped roof ring (Sapphire's
    yellow-striped roof) with a raised beige centre, small porch on two posts over the door (res 342)."""
    m = Model('sl_fanclub')
    X, Z0, Z1, H = 38, -32, 20, DOOR_WALL
    shadow(m, -44, 44, -38, 30)
    walls(m, YELLOW, octagon(-X, X, Z0, Z1, 8), 0, H, rep=(22, 34))
    rect(m, GREY, (-X + 8, 0, Z1 + 0.2), E, UP, 2 * X - 16, 4, rep=(60, 4))
    for wx in (-22, 22): window(m, wx, 19, Z1)
    for x in (-X + 8, -10, 10, X - 8):
        rect(m, POST, (x - 1.5, 0, Z1 + 0.3), E, UP, 3, H, rep=(3, H))
    out = octagon(-X - 4, X + 4, Z0 - 4, Z1 + 4, 10)
    inner = octagon(-X + 10, X - 10, Z0 + 8, Z1 - 12, 6)
    frustum(m, GOLD, out, inner, H - 1, H + 11, rep=GOLD_REP)
    walls(m, BEAM, inner, H + 11, H + 14, rep=(28, 3))
    flat(m, YELLOW, inner, H + 14, rep=(22, 30))
    # porch: sloping roof on two posts in front of the door, its front edge at the wall top (it was 4 lower and hid the
    # door's top half from the camera; door_fix)
    face(m, GOLD, (-14, H, Z1 + 12), E, (0, 0.45, -0.89), [(0, 0), (28, 0), (28, 13.4), (0, 13.4)], rep=GOLD_REP)
    for x in (-12, 12): post(m, POST, x, Z1 + 9, 3, 0, H)
    return m

def museum():
    """Oceanic Museum (6x4): green ribbed walls with a dark base, pale blue plinth, mint flat roof with a raised
    centre and four skylights, Black 2's sliding glass door in the middle (res 343), its arc's ends on the wall (door
    origin z 16) under a mint canopy following its curve (it stood 4-14 units out of 32-unit walls; door_fix)."""
    m = Model('sl_museum')
    X, Z0, Z1, H = 46, -32, 20, DOOR_WALL
    shadow(m, -52, 52, -38, 28)
    box_walls(m, -X, X, Z0, Z1, 0, H, GREEN_WALL, rep=(64, H))
    rect(m, METAL, (-X, 0, Z1 + 0.2), E, UP, 2 * X, 5, rep=(32, 32))
    for wx in (-30, 30): window(m, wx, 18, Z1)
    out = rectangle(-X - 3, X + 3, Z0 - 3, Z1 + 3)
    walls(m, MINT, out, H - 2, H + 3, rep=(32, 32))
    inner = rectangle(-X + 8, X - 8, Z0 + 8, Z1 - 10)
    frustum(m, MINT, out, inner, H + 3, H + 8, rep=(32, 32))
    flat(m, MINT, inner, H + 8, rep=(32, 32))
    for sx, sz in ((-8, -14), (8, -14), (-8, -2), (8, -2)):          # four skylights (Sapphire's roof windows)
        face(m, GLASS, (sx - 5, H + 8.4, sz + 5), E, N, [(0, 0), (10, 0), (10, 10), (0, 10)], rep=(10, 10))
    decal(m, CREST, (0, H + 1, Z1 + 3.3), E, UP, 10, 10)
    pc_door_hood(m, MINT, MINT, 0, Z1 - 4, 31, 35, band_rep=(32, 32))
    return m

def shipyard():
    """Stern's Shipyard (8x6): tall warehouse with dark plank walls, a beam band, a pale panelled roof with two
    louvred vents, and the two red-brown dock frames standing east of it (res 344)."""
    m = Model('sl_shipyard')
    X, Z0, Z1, H = 62, -62, 20, 40
    shadow(m, -68, 68, -68, 28)
    box_walls(m, -X, X, Z0, Z1, 0, H, PLANKS, rep=(31, 20))
    rect(m, BEAM, (-X, H - 6, Z1 + 0.2), E, UP, 2 * X, 6, rep=(62, 6))
    rect(m, GREY, (-X, 0, Z1 + 0.2), E, UP, 2 * X, 3, rep=(62, 3))
    out = rectangle(-X - 2, X + 2, Z0 - 2, Z1 + 2)
    inner = rectangle(-X + 6, X - 6, Z0 + 6, Z1 - 6)
    walls(m, GREY, out, H - 1, H + 3, rep=(64, 4))
    frustum(m, METAL, out, inner, H + 3, H + 7, rep=(32, 32))
    flat(m, METAL, inner, H + 7, rep=(32, 32))
    for vx in (-40, 40):                                              # the two dark vents on Sapphire's roof
        face(m, VENT, (vx - 10, H + 7.4, -46), E, N, [(0, 0), (20, 0), (20, 12), (0, 12)], rep=(20, 12))
    window(m, 30, 22, Z1, 22, 12)
    # dock frames (Sapphire's red-brown scaffolds east of the shipyard: tiles 32-33 x rows 34-35 and 37-38; their
    # legs stand on the solid rows 35 and 38, row 37 is walkable in Sapphire)
    for fz in (-24, 24):
        for fx in (X + 8, X + 26):
            post(m, PLANKS, fx, fz, 4, 0, 34)
        rect(m, BEAM, (X + 6, 28, fz + 2.1), E, UP, 22, 5, rep=(22, 5))
    return m

def harbor():
    """Harbor (7x6): pale blue panel walls with windows, tall orange corrugated gable roof (res 345)."""
    m = Model('sl_harbor')
    X, Z0, Z1, H = 54, -62, 20, 44          # (32: the eave at 30, under the door's top 32; door_fix 2026-10-11)
    shadow(m, -60, 60, -70, 28)
    box_walls(m, -X, X, Z0, Z1, 0, H, METAL, rep=(32, 32))
    rect(m, BLUE, (-X, 0, Z1 + 0.2), E, UP, 2 * X, 3, rep=(56, 3))
    for wx in (-34, -18, 18, 34): window(m, wx, 19, Z1, 14, 12)
    gable_ends(m, METAL, -X, X, Z0, Z1, H, 34 * (Z1 - Z0) / (Z1 - Z0 + 12), (32, 32))
    gable_roof(m, RIBS, -X - 4, X + 4, Z0 - 6, Z1 + 6, H - 2, H + 32, rep=(28, 36))
    decal(m, CREST, (0, H - 6, Z1 + 0.4), E, UP, 10, 10)
    return m

def awning():
    """Market entrance canopy: orange scalloped tiles on a low hip roof over two wooden posts. The posts stand on
    Sapphire's only solid tiles (the post row below the canopy), 2 tiles either side of the centre; the two canopy
    rows are walkable in Sapphire (walk-behind), so no posts there (res 346)."""
    m = Model('sl_awning')
    shadow(m, -34, 34, -22, 14)
    for x in (-32, 32):
        post(m, POST, x, 8, 3, 0, 26)
    hip_roof(m, ORANGE_TILE, -36, 36, -22, 12, 25, -20, 20, -5, 33, rep=(16, 32))
    rect(m, TRIM, (-36, 21, 12.1), E, UP, 72, 4, rep=(36, 4))
    return m

def stall():
    """Market stall: olive-green tiled hip roof on two wooden front posts (res 347), 3.5 tiles wide so one model
    fits Sapphire's 4-wide (left) and 3-wide (right) stalls. Sapphire's stall: two awning rows (walkable,
    walk-behind) over a row of posts and wares (solid) where the seller stands (Cook, Energy Guru, Effort Ribbon
    woman, clerks). Origin = the top edge of that row (data/towns/SlateportCity.json props).
    People on both sides must stay fully drawn (npc_limit 2026-10-07; the sellers were hidden under the old roof): the
    seller at z = +8 and anyone in the aisle row north of the awning rows (z = -40, the market's rows 40/44/48).
    Black 2 draws people as camera-facing quads (ov036 FldActSys_AddBlAct, BLACT_TYPE_FACE_CAMERA) at the depth of
    their feet, and the field camera looks down at 52.6 degrees (eye 185.7 up and 142.0 south of its target, read
    in Slateport), so a roof point (y, z) is behind the seller only if z < 8 - 1.307 y, and below the aisle person's
    feet on screen (not over them) only if z > -40 + 0.764 y. Both hold only for y < 23 between them: a low roof
    (eaves 13, ridge 20) over the two awning rows, ~1 unit of margin, its front edge at z = -10.5. On screen it fills
    Sapphire's two awning rows with the seller standing in front of it, as in Sapphire."""
    m = Model('sl_stall')
    shadow(m, -29, 29, -28.5, -10.5)
    for x in (-27, 27):
        post(m, POST, x, -11.5, 3, 0, 13)
    hip_roof(m, OLIVE, -30, 30, -28.5, -10.5, 13, -12, 12, -21.4, 20, rep=(32, 32))
    rect(m, BEAM, (-30, 11, -10.4), E, UP, 60, 2, rep=(60, 2))
    return m

def statue():
    """The white stone monument in the south plaza (Sapphire 0x246-0x25f on prop tiles x 32-33, rows 52-54, a lawn round
    it: a tiered lantern-like tower, round base, bulb, a drum with dark windows, a domed cap with a knob), which the
    ground module drew as a 12-unit plinth: six-sided tiers in white panel, 43 high; sloped faces the fixed camera
    never sees (their normal turned away from it) are left out (res 354; buildings_audit 2026-10-08)."""
    m = Model('sl_statue')
    BLACK = Region('r4_b03_yane01', (64, 64), 58, 0, 64, 6)
    CAM = (0, math.sin(math.radians(40)), math.cos(math.radians(40)))       # towards Black 2's camera
    def ring(r, n=6):
        a0 = 90 + 180 / n           # a flat edge facing +z, order as rectangle(): SW, SE, then round through the back
        return [(r * math.cos(math.radians(a0 - 360 * k / n)), r * math.sin(math.radians(a0 - 360 * k / n)))
                for k in range(n)]
    def tier(r0, r1, y0, y1):
        o, i = ring(r0), ring(r1)
        for k in range(6):
            a, b, c, d = o[k], o[(k + 1) % 6], i[(k + 1) % 6], i[k]
            A, Bq, C = (a[0], y0, a[1]), (b[0], y0, b[1]), (c[0], y1, c[1])
            u = [Bq[j] - A[j] for j in range(3)]; w = [C[j] - A[j] for j in range(3)]
            n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
            if sum(n[j] * CAM[j] for j in range(3)) <= 0: continue
            slope(m, WHITE, A, Bq, C, (d[0], y1, d[1]), (UW, UW))
    UW = 400
    shadow(m, -16, 16, -15, 15)
    walls(m, WHITE, ring(14), 0, 4, rep=(UW, UW))                  # base
    tier(14, 11, 4, 6)
    tier(12, 7, 6, 20)                                             # bulb
    tier(7, 10, 20, 23)                                            # (the neck flares into the drum)
    walls(m, WHITE, ring(10), 23, 32, rep=(UW, UW))                # drum with Sapphire's dark windows
    pts = ring(10)
    for i in (5, 0, 1):                                            # the three faces turned to the camera
        (xa, za), (xb, zb) = pts[i], pts[(i + 1) % 6]
        L = math.hypot(xb - xa, zb - za); mx, mz = (xa + xb) / 2, (za + zb) / 2; r = math.hypot(mx, mz)
        decal(m, BLACK, (mx + mx / r, 28, mz + mz / r), ((xb - xa) / L, 0, (zb - za) / L), UP, 4, 4)
    tier(11, 4, 32, 40)                                            # cap
    walls(m, WHITE, ring(3), 40, 43, rep=(UW, UW))                 # knob
    flat(m, WHITE, ring(3), 43, rep=(UW, UW))
    return m

def models():
    return {'house': house(), 'annex': annex(), 'fanclub': fanclub(), 'museum': museum(), 'shipyard': shipyard(),
            'harbor': harbor(), 'awning': awning(), 'stall': stall(), 'statue': statue()}

if __name__ == '__main__':
    write_models(sys.argv[1], models())
