"""Buildings that stand on Hoenn's routes: Sapphire's shapes and colours, Black 2 textures (group towns5, res 400-408,
410-413; Ever Grande's Pokemon League is models_evergrande.py, res 409).

    python3 models_routes.py ../work/buildings/routes

Writes one .dae per model (+ the texture images, palettes.txt, textures.txt). Every texture is one the Hoenn
building set already holds (pack 0's own, the slice's, or groups towns1-3's): +0 B with towns1-3 in, +8 KB alone.
Geometry helpers (whole textures repeated by the GPU, no north-facing walls) come from models_slateport.py.

Sapphire footprints (data/plans/<Map>.json; x = tiles, rows; 'roof row' = walk-behind row above the solid rows):
  briney      Route 104 Mr. Briney's cottage: x 15-19, rows 48-50 + roof row 47, door (17,50) in the middle;
              brown thatched roof, blue-and-white band under the eave, straw-screen front on wooden posts
  flowershop  Route 104 Pretty Petal flower shop: x 3-8, rows 15-18, door (5,18) in column 2; salmon roof with a red
              eave band, green siding, pink-and-white striped awning over the door, windows with flower boxes
  seashore    Route 109 Seashore House: x 10-14, rows 3-5 + roof row 2, door (12,5) in the middle; purple roof,
              orange plank walls, a window either side of the door
  gate        Route 110 Seaside Cycling Road north/south entrance: x 14-19, rows 12-16 (south: x 15-20, rows 84-88),
              doors in columns 1 and 4; yellow brick walls, flat grey roof with a grid of panels (the Mauville
              tileset building towns2 made Mauville's annex from)
  trickhouse  Route 110 Trick House: x 9-13, rows 61-66, door (11,66) in the middle; pink two-tier roof, grey walls
              with gold ornament panels
  winstrate   Route 111 Winstrate family's house: x 11-15, rows 110-113 + roof row 109, door in the middle; as gate
  cablecar    Route 112 cable car station: x 27-30 (+ the sloped east wing x 31-32), rows 23-27, double door (28,27)
              (29,27); orange ribbed roof, white walls, the blue cable car pylon 4.5 tiles west (prop tiles x 24)
  weather     Route 119 Weather Institute: x 1-11, rows 26-32, door (6,32); glass body with rounded ends, beige ribbed
              roof with two round turrets, entrance porch on four grey columns
  safari      Route 121 Safari Zone entrance: x 35-39, rows 0-5, door (37,5) in the middle; grey walls, flat beige
              roof, green planting either side of the glass door
  glassworks  Route 113 glass workshop: x 32-35, rows 2-5, door (33,5) in column 1; Fallarbor's house (towns3 res
              360: olive siding, window with an orange awning) under Sapphire's ash-grey roof
  house118    Route 118 house by the water: x 0-3, rows 15-17 + roof row 14, no door; pink roof, yellow siding, two
              posts, a window in column 2 (Mauville's house 2 without its door; buildings_audit 2026-10-08)
  pylon_mid   Route 112 cable car pylon on the prop tiles x 12, rows 19-21, cable east to the station's (res 412)
  pylon_top   Route 112 cable car pylon on the prop tiles x 4, rows 15-17, cable on west off the map (res 413)
The General-tileset red-roof houses on routes 111, 114, 116, 117, 119, 123, 124 are towns1's res 322 (4 wide) and 321
(5 wide), Route 114's Fossil Maniac's house is towns3's res 360: same Sapphire metatiles (notes/TOWNS_TOWNS5.md).
Origin = footprint centre on the ground, +z = front (south); front walls at z = +20 ('front' in data/towns/), 4 units
into the door tile as Black 2 places its buildings. Walls >= 34 high so Black 2's door models (y 6..32) fit under them.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, shadow, DOOR_WALL, pc_door_hood
from models_slateport import (UP, E, N, face, rect, decal, walls, flat, rectangle, box_walls, gable_roof, gable_ends,
                              frustum, post, slope, tiled, write_models)

# --- pack 0's own textures (Nuvema/Accumula, a/1/7/4 entry 0) ---
MADO = Region('h_mado', (16, 16), 0, 0, 16, 16)                    # window glass
GLASS = Region('pc_win1', (16, 128), 1, 64, 15, 96)                # blue glass panel
CREST = Region('pc_win1', (16, 128), 0, 32, 16, 48)                # Poke Ball emblem
GREY = Region('gate_1', (64, 32), 24, 22, 64, 32)                  # grey concrete
ORANGE_TILE = tiled('yane_001', (16, 64))                          # orange roof tiles
LEAVES = tiled('plant_tex4', (32, 32))                             # leafy planting
# --- the slice's (data/buildings/slice.json) ---
WINDOW = Region('c14_h1_body', (64, 64), 38, 32, 62, 46)           # framed window (glass transparent)
POST = Region('c14_h1_body', (64, 64), 14, 24, 17, 56)             # wooden post
BEAM = Region('c14_h1_body', (64, 64), 36, 20, 64, 28)             # dark wood band
PLANKS = Region('c14_h1_body', (64, 64), 18, 0, 46, 18)            # vertical dark wood planks (thatch)
SHINGLE = Region('c14_h2_yane', (64, 64), 0, 16, 16, 32)           # grey-tan shingles
SHINGLE_LT = Region('c14_h2_yane', (64, 64), 0, 0, 16, 16)         # light cream shingles
WHITE = Region('r4_b03_yane01', (64, 64), 2, 18, 14, 26)           # white panel
BLUE = Region('r4_b03_yane01', (64, 64), 4, 34, 60, 54)            # flat blue
SMALL_WIN = Region('r4_b03_yane01', (64, 64), 4, 7, 17, 18)        # blue window in a grey frame
BLACK = Region('r4_b03_yane01', (64, 64), 58, 0, 64, 6)            # black
BEIGE = Region('t06_h_03_a', (64, 64), 0, 0, 30, 14)               # beige siding (horizontal lines)
YELLOW = Region('t06_h_03_a', (64, 64), 0, 24, 22, 54)             # plain warm beige
RIBS = Region('t06_h_03_a', (64, 64), 34, 18, 62, 54)              # orange corrugated roof
TRIM = Region('t06_h_03_a', (64, 64), 0, 56, 32, 62)               # brick-red band
# --- groups towns1-3 (merged by this group's registry too, so it stands alone) ---
GOLD = Region('wbase_a', (32, 32), 4, 5, 32, 19)                   # towns2: gold horizontal stripes
GOLD_REP = (512, 14)                                               # uniform across: one cell per face width
PINK = tiled('h2', (16, 64))                                       # towns2: pink roof tiles
PURPLE = tiled('c13_ho01b', (64, 64))                              # towns2: purple roof panels
METAL = tiled('c4_bp01', (32, 32))                                 # towns2/3: pale blue panels
LIME = Region('rr_misel1_02', (32, 64), 0, 1, 32, 31)              # towns3: green siding
LIME_TRIM = Region('rr_misel1_02', (32, 64), 0, 31, 16, 34)        # towns3: tan band under the siding
BOARDS = Region('c14_h2_kabe', (64, 64), 16, 28, 28, 62)           # towns3: orange plank boards
TAN = tiled('sand_tex001', (32, 32))                               # towns1: tan grain (the Gym roof)

SOURCES = {'h_mado': 'ext00', 'pc_win1': 'ext00', 'gate_1': 'ext00', 'yane_001': 'ext00', 'plant_tex4': 'ext00',
           'h_kage': 'ext00', 't2_buil1': 'ext00', 'c14_h1_body': 'ext57', 'c14_h2_yane': 'ext57',
           'r4_b03_yane01': 'ext05', 't06_h_03_a': 'ext53', 'wbase_a': 'ext06', 'h2': 'ext09', 'c13_ho01b': 'ext54',
           'c4_bp01': 'ext06', 'rr_misel1_02': 'ext59', 'c14_h2_kabe': 'ext57', 'sand_tex001': 'ext01'}
UW = 400          # a 'repeat' wider than any face: a region uniform along u is stretched, not cut
F = 20            # front wall z (data/towns/<Map>.json 'front')

# ------------------------------------------------------------------------------------------------ helpers
def window(m, x, y, z, w=18, h=11):
    """Framed window: glass 1 unit and frame 2 units off the wall (nearer layers flicker on hardware/melonDS)."""
    decal(m, MADO, (x, y, z + 1.0), E, UP, w, h)
    decal(m, WINDOW, (x, y, z + 2.0), E, UP, w + 2, h + 2)

def vbox(m, region, x0, x1, z0, z1, y0, y1, rep):
    """South, east and west walls with the region turned a quarter (its horizontal stripes run vertically)."""
    H = y1 - y0
    face(m, region, (x1, y0, z1), UP, (-1, 0, 0), [(0, 0), (H, 0), (H, x1 - x0), (0, x1 - x0)], rep)   # south
    face(m, region, (x1, y0, z0), UP, (0, 0, 1), [(0, 0), (H, 0), (H, z1 - z0), (0, z1 - z0)], rep)    # east
    face(m, region, (x0, y0, z1), UP, (0, 0, -1), [(0, 0), (H, 0), (H, z1 - z0), (0, z1 - z0)], rep)   # west

def stripes(m, regions, x0, x1, n, y0, y1, z, rep=None, slope_out=0.0):
    """A band of n vertical stripes alternating between regions, from (x0, y0) to (x1, y1) facing south at z.
    slope_out > 0 tilts it into an awning: the bottom edge stands that much further south."""
    w = (x1 - x0) / n
    h = math.hypot(y1 - y0, slope_out)
    v = (0, (y1 - y0) / h, -slope_out / h)
    for k in range(n):
        reg = regions[k % len(regions)]
        face(m, reg, (x0 + k * w, y0, z + slope_out), E, v, [(0, 0), (w, 0), (w, h), (0, h)], rep or (w, h))

def roof_band(m, region, x0, x1, zr, yr, k, width, rep):
    """A strip lying on both slopes of a gable roof just below the ridge (ridge at z = zr, y = yr; pitch k = rise per
    unit of run), lifted 0.6 units off the roof."""
    d = width / math.sqrt(1 + k * k)
    for sgn in (1, -1):
        za, ya = zr + sgn * d, yr - d * k
        if sgn > 0:
            slope(m, region, (x0, ya + 0.6, za), (x1, ya + 0.6, za), (x1, yr + 0.6, zr), (x0, yr + 0.6, zr), rep)
        else:
            slope(m, region, (x1, ya + 0.6, za), (x0, ya + 0.6, za), (x0, yr + 0.6, zr), (x1, yr + 0.6, zr), rep)

def ring(xc, zc, rx, rz, n):
    """n-sided polygon round (xc, zc) with a flat south edge, in rectangle()'s order (SW, SE, NE, NW: the angle
    decreases with +z south)."""
    a0 = 90 + 180 / n
    return [(xc + rx * math.cos(math.radians(a0 - 360 * k / n)), zc + rz * math.sin(math.radians(a0 - 360 * k / n)))
            for k in range(n)]

# ------------------------------------------------------------------------------------------------ models
def briney():
    """Mr. Briney's cottage (5x4): brown thatched gable roof with a cream ridge, blue band hanging from the eave,
    yellow straw-screen walls on dark posts; door (Black 2's brown door_normal02, res 260) in the middle (res 400)."""
    m = Model('rt_briney')
    X, Z0, H = 38, -20, DOOR_WALL + 4       # (34: the eave at 31 and its band down to 24, 6 units out, over the door's
                                            # top at 32: door_fix 2026-10-11)
    shadow(m, -44, 44, -30, 28)
    vbox(m, GOLD, -X, X, Z0, F, 0, H, (512, 21))
    rect(m, BEAM, (-X, 0, F + 1.0), E, UP, 2 * X, 3, rep=(UW, 3))
    for x in (-X + 1.5, -11, 11, X - 1.5):
        rect(m, POST, (x - 1.5, 0, F + 2.5), E, UP, 3, H, rep=(3, 32))
    zr, yr = -3.0, H + 22                                   # ridge (a little behind the middle: deep front slope)
    gable_ends(m, PLANKS, -X, X, Z0, F, H, 15, (UW, UW))
    slope(m, PLANKS, (-X - 4, H - 3, F + 6), (X + 4, H - 3, F + 6), (X + 4, yr, zr), (-X - 4, yr, zr), (42, 36))
    slope(m, PLANKS, (X + 4, H - 3, Z0 - 8), (-X - 4, H - 3, Z0 - 8), (-X - 4, yr, zr), (X + 4, yr, zr), (42, 36))
    roof_band(m, SHINGLE_LT, -X - 4, X + 4, zr, yr, (yr - H + 3) / (F + 6 - zr), 7, (44, 8))
    # blue band with a white edge hanging from the front eave (Sapphire's striped band under the thatch)
    rect(m, BLUE, (-X - 4, H - 6, F + 6.2), E, UP, 2 * X + 8, 3, rep=(UW, 6))
    rect(m, WHITE, (-X - 4, H - 7, F + 6.4), E, UP, 2 * X + 8, 1.5, rep=(UW, 8))
    return m

def flowershop():
    """Pretty Petal flower shop (6x4): green siding, salmon tiled gable roof with a red eave band, pink-and-white
    striped awning over the door (column 2, centre x -8) and the window beside it, flower boxes (res 401)."""
    m = Model('rt_flowershop')
    X, Z0, H = 46, -20, DOOR_WALL + 4       # (34: the awning over the door came down to 24, 8 units out: door_fix)
    shadow(m, -52, 52, -30, 30)
    box_walls(m, -X, X, Z0, F, 0, H, LIME, rep=(46, 34))
    rect(m, LIME_TRIM, (-X, 0, F + 1.0), E, UP, 2 * X, 3, rep=(UW, 3))
    gable_ends(m, LIME, -X, X, Z0, F, H, 13, (46, 34))
    for x, w in ((-37, 10), (20, 14), (36, 14)):
        window(m, x, 18, F, w, 11)
        rect(m, LEAVES, (x - w / 2 - 1, 6, F + 2.5), E, UP, w + 2, 6, rep=(16, 8))      # flower box
    for x in (-19, 3):                                                                 # posts by the door
        rect(m, YELLOW, (x - 1.5, 0, F + 1.5), E, UP, 3, H - 6, rep=(3, 30))
    stripes(m, [PINK, WHITE], -32, 16, 6, H - 6, H - 1, F + 0.6, slope_out=6)     # awning (over the door's top)
    stripes(m, [PINK, WHITE], -32, 16, 6, H - 8, H - 6, F + 6.6)                        # its valance
    gable_roof(m, ORANGE_TILE, -X - 4, X + 4, Z0 - 6, F + 6, H - 2, H + 16, rep=(16, 32))
    rect(m, TRIM, (-X - 4, H - 6, F + 6.2), E, UP, 2 * X + 8, 4, rep=(32, 4))           # red eave band
    return m

def seashore():
    """Seashore House (5x4): purple gable roof with a light ridge band, orange plank walls on wooden posts, a window
    either side of the door (middle, res 260) (res 402)."""
    m = Model('rt_seashore')
    X, Z0, H = 38, -20, DOOR_WALL           # (34: the eave at 32, 5 units out, over the door's top: door_fix)
    shadow(m, -44, 44, -30, 28)
    box_walls(m, -X, X, Z0, F, 0, H, BOARDS, rep=(19, H))
    gable_ends(m, BOARDS, -X, X, Z0, F, H, 15, (UW, UW))
    rect(m, BEAM, (-X, 0, F + 1.0), E, UP, 2 * X, 3, rep=(UW, 3))
    for x in (-X + 1.5, -11, 11, X - 1.5):
        rect(m, POST, (x - 1.5, 0, F + 2.5), E, UP, 3, H, rep=(3, H))
    for x in (-24, 24):
        window(m, x, 18, F, 16, 11)
    zr, yr = -2.0, H + 18
    slope(m, PURPLE, (-X - 4, H - 2, F + 5), (X + 4, H - 2, F + 5), (X + 4, yr, zr), (-X - 4, yr, zr), (32, 32))
    slope(m, PURPLE, (X + 4, H - 2, Z0 - 7), (-X - 4, H - 2, Z0 - 7), (-X - 4, yr, zr), (X + 4, yr, zr), (32, 32))
    roof_band(m, WHITE, -X - 4, X + 4, zr, yr, (yr - H + 2) / (F + 5 - zr), 5, (UW, 8))
    return m

def flat_house(name, X, Z0, H, windows):
    """Mauville-tileset building (gate, Winstrate house): yellow brick walls on a red base, flat roof with a grey rim
    round a grid of panels (Sapphire's light grid of roof squares), as towns2's Mauville annex."""
    m = Model(name)
    shadow(m, -X - 6, X + 6, Z0 - 6, F + 8)
    box_walls(m, -X, X, Z0, F, 0, H, GOLD, rep=GOLD_REP)
    rect(m, TRIM, (-X, 0, F + 1.0), E, UP, 2 * X, 3, rep=(UW, 3))
    for x in windows:
        window(m, x, 20, F, 13, 12)
    out = rectangle(-X - 2, X + 2, Z0 - 2, F + 2)
    walls(m, GREY, out, H - 1, H + 4, rep=(UW, 5))
    flat(m, GREY, out, H + 4, rep=(UW, UW))
    face(m, METAL, (-X + 6, H + 4.4, F - 6), E, N, [(0, 0), (2 * X - 12, 0), (2 * X - 12, F - Z0 - 12), (0, F - Z0 - 12)],
         rep=(16, 16))
    return m

def gate():
    """Seaside Cycling Road entrance (6x5, doors in columns 1 and 4: the record's door at x -24, the second door is a
    door_normal03 (261) prop in data/towns/Route110.json) (res 403)."""
    return flat_house('rt_gate', 46, -44, 34, (-8, 8))

def winstrate():
    """Winstrate family's house (5x5, door in the middle, a window either side) (res 405)."""
    return flat_house('rt_winstrate', 38, -44, 34, (-18, 18))

def trickhouse():
    """Trick House (5x6): grey ground floor with gold ornament panels and windows under a wide pink skirt roof, a
    narrower grey upper floor with a pink gable roof; door (res 261) in the middle (res 404)."""
    m = Model('rt_trickhouse')
    X, Z0, H = 38, -40, DOOR_WALL           # (34: the skirt roof at 32, 5 units out, over the door's top: door_fix)
    shadow(m, -44, 44, -52, 28)
    box_walls(m, -X, X, Z0, F, 0, H, GREY, rep=(UW, 17))
    for x in (-31, 31):
        decal(m, GOLD, (x, 16, F + 1.0), UP, (-1, 0, 0), 22, 8)      # gold panels by the corners (turned)
    for x in (-18, 18):
        window(m, x, 19, F, 12, 12)
    frustum(m, PINK, rectangle(-X - 5, X + 5, Z0 - 5, F + 5), rectangle(-24, 24, -34, 0), H - 2, H + 12, rep=(16, 32))
    U0, U1 = H + 10, H + 26                                            # upper floor
    box_walls(m, -22, 22, -34, 0, U0, U1, GREY, rep=(UW, 16))
    for x in (-12, 12):
        decal(m, GOLD, (x, U0 + 8, 1.0), UP, (-1, 0, 0), 12, 6)
    window(m, 0, U0 + 8, 0, 10, 9)
    gable_ends(m, GREY, -22, 22, -34, 0, U1, 12, (UW, UW))
    gable_roof(m, PINK, -26, 26, -39, 5, U1 - 2, U1 + 14, rep=(16, 32))
    return m

def cablecar():
    """Cable car station (4 wide + sloped east wing): white walls with a window band and a beige lintel over
    Sapphire's two door tiles (doors: the record's door_normal03 on the west tile, a res 261 prop on the east one),
    orange ribbed gable roof, a lower east wing with a roof sloping down to the east, and the blue cable car pylon 4.5
    tiles west with its cable (res 406)."""
    m = Model('rt_cablecar')
    X, Z0, H = 30, -44, 36
    shadow(m, -36, 66, -52, 28)
    box_walls(m, -X, X, Z0, F, 0, H, WHITE, rep=(UW, 18))
    rect(m, LIME_TRIM, (-X, 0, F + 1.0), E, UP, 2 * X, 3, rep=(UW, 3))
    rect(m, YELLOW, (-20, 33, F + 1.0), E, UP, 40, 3, rep=(UW, 3))   # lintel over the doors
    gable_ends(m, WHITE, -X, X, Z0, F, H, 16, (UW, UW))
    gable_roof(m, RIBS, -X - 3, X + 3, Z0 - 4, F + 4, H - 2, H + 16, rep=(42, 40))
    # east wing: lower box, roof sloping down to the east (Sapphire's slanted right side)
    box_walls(m, X, 60, -28, F, 0, 24, WHITE, rep=(UW, 24))
    for z in (-14, 4):
        decal(m, SMALL_WIN, (60.8, 14, z), (0, 0, -1), UP, 10, 8)
    slope(m, RIBS, (63, 22, F + 3), (63, 22, -31), (X, H + 1, -31), (X, H + 1, F + 3), (42, 40))
    # pylon (Sapphire's prop tiles x 24, rows 24-26: base 4.5 tiles west of the origin, on row 26). The station stands on
    # the heights module's 80-unit block and the pylon's tiles on the ground below it (y 0): its post reaches down the
    # 80 units (it hung in the air; buildings_audit 2026-10-08). Its cable west is the next pylon's (res 412)
    tower(m, -72, 6, -80, 46)
    box_walls(m, -80, -64, 3, 9, 44, 48, BLUE, rep=(16, 4))
    flat(m, BLUE, rectangle(-80, -64, 3, 9), 48, rep=(16, 6))
    cable(m, (-66, 46, 6), (-31, 47, -10))
    return m

def cable(m, a, b, w=1.5):
    """A cable from a to b (a the west end: the strip faces south), w units high, as the station's."""
    L = math.dist(a, b)
    face(m, GREY, a, tuple((b[k] - a[k]) / L for k in range(3)), UP, [(0, 0), (L, 0), (L, w), (0, w)], rep=(UW, 2))

def tower(m, x, z, y0, y1):
    """A pylon's mast from y0 to y1: 12 units square at the foot narrowing to 4 at the top (a 46-unit post read as a
    stick at 100+ units, the camera's perspective leaning it at the screen's edges)."""
    frustum(m, BLUE, rectangle(x - 6, x + 6, z - 6, z + 6), rectangle(x - 2, x + 2, z - 2, z + 2), y0, y1, rep=(UW, UW))   # (flat blue: stretched)

def pylon(H, east=None, west=None):
    """A cable car pylon as the station's (blue post 4 wide, cross beam 16 wide at the top) H units high, with its cable
    east to the next pylon's west beam end (`east`, relative to this origin) and west to `west`."""
    m = Model('rt_pylon')
    tower(m, 0, 0, 0, H - 2)
    box_walls(m, -8, 8, -3, 3, H - 2, H + 2, BLUE, rep=(16, 4))
    flat(m, BLUE, rectangle(-8, 8, -3, 3), H + 2, rep=(16, 6))
    if east: cable(m, (6, H, 0), east)
    if west: cable(m, west, (-6, H, 0))
    return m

# Route 112's cable car line (Sapphire: the station's pylon at x 24, rows 24-26, then the prop tiles x 12, rows 19-21
# and x 4, rows 15-17, the cable off the map's west edge towards Mt. Chimney; the ground module drew plinths there).
# Heights in the built world: the station block 80 (its pylon's beam 126), the ground 0 at x 12, 48 at x 4. The cable
# rises in one straight line from the station's pylon (126) to the x 4 pylon (150) and on to the map edge, so the x 12
# pylon is 140 high and the x 4 one 102 (Black 2's cable car pylons are tall; buildings_audit 2026-10-08). Origins:
# the pylon's bottom tile at x + 0.5, row + 0.375 (as the station's), world units from the built world:
# station pylon beam west end (3712, 126, 1702); x 12 pylon (3528, 0, 1622); x 4 pylon (3400, 48, 1558); map edge x 3328
def pylon_mid():
    """Route 112 cable car pylon on the prop tiles x 12, rows 19-21 (res 412)."""
    return pylon(140, east=(3714 - 3528, 126, 1702 - 1622))

def pylon_top():
    """Route 112 cable car pylon on the prop tiles x 4, rows 15-17, with the cable on west off the map (res 413)."""
    H = 150 - 48
    return pylon(H, east=(3528 - 6 - 3400, 140 - 48, 1622 - 1558), west=(-72, H + 4, -36))

def weather():
    """Weather Institute (11x7): two-storey glass body with rounded ends (pale blue panels, white band), beige
    fascia, flat beige roof with a raised ribbed middle, two round turrets with dark tops at the ends; entrance porch:
    grey frame round the door (res 261) under a beige canopy on four grey columns (res 407)."""
    m = Model('rt_weather')
    H = 44
    shadow(m, -84, 84, -60, 26)
    body = [(-64, 8), (64, 8)] + [(64 + 24 * math.sin(math.radians(a)), -24 + 32 * math.cos(math.radians(a)))
                                  for a in (45, 90, 135)] + [(64, -56), (-64, -56)] + \
           [(-64 - 24 * math.sin(math.radians(a)), -24 - 32 * math.cos(math.radians(a))) for a in (45, 90, 135)]
    walls(m, METAL, body, 0, H, rep=(32, 22))
    grow = lambda pts, d: [(x * (1 + d / 88), (z + 24) * (1 + d / 32) - 24) for x, z in pts]
    walls(m, WHITE, grow(body, 0.8), 21, 23, rep=(UW, 2))
    rim = grow(body, 2)
    walls(m, YELLOW, rim, H - 2, H + 3, rep=(UW, 5))
    flat(m, BEIGE, rim, H + 3, rep=(UW, 40))
    frustum(m, BEIGE, rectangle(-46, 46, -50, 0), rectangle(-34, 34, -40, -10), H + 3, H + 10, rep=(UW, 14))
    flat(m, BEIGE, rectangle(-34, 34, -40, -10), H + 10, rep=(UW, 14))
    for cx in (-66, 66):                                               # turrets over the rounded ends
        tower = ring(cx, -26, 15, 15, 6)
        walls(m, YELLOW, tower, H + 3, H + 16, rep=(UW, 14))
        flat(m, YELLOW, tower, H + 16, rep=(UW, UW))
        flat(m, BLACK, ring(cx, -26, 9, 9, 6), H + 16.4, rep=(UW, UW))
    # entrance porch (front row 32: x 3-9 solid in Sapphire), door in the middle
    box_walls(m, -22, 22, 0, F, 0, 34, GREY, rep=(UW, 34))
    for x in (-15, 15):
        decal(m, GLASS, (x, 17, F + 1.0), E, UP, 8, 26)
    canopy = rectangle(-44, 44, 2, F + 6)
    walls(m, GREY, canopy, 34, 38, rep=(UW, 4))
    flat(m, BEIGE, canopy, 38, rep=(UW, 14))
    for x in (-35, -13, 13, 35):
        post(m, GREY, x, F + 3, 5, 0, 34)
    return m

def safari():
    """Safari Zone entrance (5x6): grey walls with two windows, flat beige roof inside a grey rim, a grey canopy over
    Black 2's sliding glass door (res 93, middle), green planting either side along the base (res 408)."""
    m = Model('rt_safari')
    X, Z0, H = 38, -58, 36
    shadow(m, -44, 44, -64, 30)
    box_walls(m, -X, X, Z0, F, 0, H, GREY, rep=(UW, 18))
    for x in (-26, 26):
        decal(m, SMALL_WIN, (x, 24, F + 1.0), E, UP, 14, 11)
        rect(m, LEAVES, (x - 12, 0, F + 1.0), E, UP, 24, 9, rep=(16, 9))
    for x in (-15, 15):
        rect(m, WHITE, (x - 1.5, 0, F + 1.2), E, UP, 3, 30, rep=(UW, 8))
    # canopy following the game's curved sliding door (door_pc 93, origin z 16: its arc's ends on the wall); the flat
    # canopy's edge was at 30-33 and 7 units out, and the door stood 4-14 units out through it (door_fix 2026-10-11)
    pc_door_hood(m, GREY, WHITE, 0, F - 4, 31, 34, band_rep=(UW, 3))
    out = rectangle(-X - 2, X + 2, Z0 - 2, F + 2)
    walls(m, GREY, out, H - 1, H + 4, rep=(UW, 5))
    flat(m, GREY, out, H + 4, rep=(UW, UW))
    face(m, BEIGE, (-X + 4, H + 4.4, F - 4), E, N, [(0, 0), (2 * X - 8, 0), (2 * X - 8, F - Z0 - 8), (0, F - Z0 - 8)],
         rep=(UW, 14))
    return m

def glassworks():
    """Glass workshop (4x4): Fallarbor's house (towns3, models_fallarbor.house: olive siding, framed window with an
    orange awning right of the door in column 1, door_t2_h res 236) with Sapphire's ash-covered grey shingle roof
    (res 410)."""
    import models_fallarbor as fa
    m = Model('rt_glassworks')
    shadow(m, -34, 34, -26, 28)
    H = DOOR_WALL                           # (as Fallarbor's house: door_fix 2026-10-11)
    from buildings import box_walls as bwalls, rect as brect, gable_roof as bgable, face as bface
    bwalls(m, -28, 28, -20, 20, 0, H, fa.OLIVE, rep=(56, 34), sides='sew')
    brect(m, fa.OLIVE_TRIM, (-28, 0, 21.0), E, UP, 56, 2, rep=(16, 2))
    fa.window(m, 13, 17, 20)
    tri = [(0, 0), (40, 0), (20, 14)]
    bface(m, fa.OLIVE, (28, H, 20), (0, 0, -1), UP, tri, rep=(UW, UW))
    bface(m, fa.OLIVE, (-28, H, -20), (0, 0, 1), UP, tri, rep=(UW, UW))
    bgable(m, SHINGLE, -32, 32, -26, 26, H - 2, H + 16, rep=(32, 16))
    return m

def house118():
    """Route 118's door-less house by the water (Sapphire x 0-3, rows 15-17 + roof row 14, Mauville tileset 0x283-0x29d:
    the roof of Mauville's houses over yellow siding, two wooden posts, a window in column 2, no door): Mauville house
    2's build (towns2 res 351: pink gable roof, gold siding) without a door, posts and window where Sapphire draws them
    (res 411; buildings_audit 2026-10-08: it stood invisible, a solid 4x3 patch of grass)."""
    m = Model('rt_house118')
    X, Z0, H = 30, -16, 34
    shadow(m, -35, 35, -24, 28)
    box_walls(m, -X, X, Z0, F, 0, H, GOLD, rep=GOLD_REP)
    gable_ends(m, GOLD, -X, X, Z0, F, H, 16 * (F - Z0) / (F - Z0 + 8), GOLD_REP)
    gable_roof(m, PINK, -X - 3, X + 3, Z0 - 4, F + 4, H - 2, H + 14, rep=(16, None))
    window(m, 8, 19, F)                                 # Sapphire's window: column 2
    for x in (-24, 20):                                 # Sapphire's posts: column 0 and the west half of column 3
        rect(m, POST, (x - 1.5, 0, F + 0.25), E, UP, 3, H, rep=(3, 32))
    return m

def models():
    return {'briney': briney(), 'flowershop': flowershop(), 'seashore': seashore(), 'gate': gate(),
            'trickhouse': trickhouse(), 'winstrate': winstrate(), 'cablecar': cablecar(), 'weather': weather(),
            'safari': safari(), 'glassworks': glassworks(), 'house118': house118(), 'pylon_mid': pylon_mid(),
            'pylon_top': pylon_top()}

if __name__ == '__main__':
    write_models(sys.argv[1], models(), SOURCES)
