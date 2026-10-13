"""Buildings of Hoenn's warp-only outdoor maps (b2tools/world.py standalone groups, data/hoenn_standalone.json):
Sapphire's shapes, Black 2's own textures. They go into the warp-only maps' own exterior pack (patches/standalone.py;
registry data/buildings/standalone.json), not pack 0.

    python3 models_standalone.py ../work/buildings/standalone

Writes one .dae per model plus its texture images (decoded from the user's dump, b2files/nsbtx), palettes.txt and
textures.txt; rebuild with ToNsbmd like the town models (b2tools/rebuild_slice.sh's loop).

  dome      470  Sootopolis dome house (3 wide): cream octagonal drum, dark grey panelled dome with a knob (Houses 1,
                 3, 4 and the door-less domes of the city)
  block     471  Sootopolis block house (3 wide): cream block, grey-green grid window over the door, flat roof
                 (Houses 2, 5-8 and the door-less blocks)
  origin    472  Cave of Origin entrance in Sootopolis's crater wall (5 wide): white stone gateway, dark doorway
  btower    473  Battle Tower (13 wide): glass middle tower, brick wings, white entrance arch (Black 2's PWT glass)
  safari    474  Safari Zone entrance seen from inside the zone (10 wide, door in column 2): grey walls, flat beige
                 roof, as Route 121's side (towns5 res 408)
  station   475  Mt. Chimney cable car station: Route 112's station (towns5 res 406, models_routes.cablecar)
                 mirrored, wing to the west, without its pylon
  pylon     476  Mt. Chimney's cable car pylon with the cable west to the station and east down the mountain
  pillar    477  Sky Pillar, the tower's foot on Sky Pillar Outside (5 wide): dark brick tower, dark doorway
  grave     478  Mt. Pyre gravestone: grey upright stone on a low base (user choice: grey, notes/DECISIONS.md)
  altar     479  Mt. Pyre summit: the orb altar (Sapphire metatiles 0x32a-0x32e), grey stone
  post      480  Mt. Pyre summit: the two round stones by the stairs (0x32b)
  harbour   481  Emerald's harbour at the end of Birth Island's and Navel Rock's docks: white shed, orange ribbed roof,
                 orange cranes either side (buildings_audit 2026-10-08)
  spdoor    482  Sky Pillar's top: the doorway down to 5F in the wall band (dark arch, pale stone jambs)
  spsky_*   483-486  Sky Pillar's top, one per cell (nw, ne, sw, se): the tower's face under the south parapet, a stone
                 curb round the other edges, Black 2's sea of clouds (o23_cloud_a, map set 90) 200 under the floor
  navel     487  Navel Rock's summit: the rock down from its edge, the clouds under it
  pwt       488  The PWT's entrance on the Battle Tower island (3 wide, door in the middle): grey panel walls with the
                 red and blue crest banners, a glass dome behind a crest screen, two lattice masts with floodlights
                 (Black 2's PWT dome textures c5_wbt_*, pack 55; battle_tower 2026-10-08)

Units: 16 per tile; origin = footprint centre on the ground, +z = front (south); front walls at z = +20 (the 'front'
in data/towns/<Map>.json; world.py puts it 4 units into the door tile). Walls >= 34 high so Black 2's door models
(y 6..32) fit under them. Door models (data/buildings/standalone.json): 259-261 span x -17..1 around their origin
(dx = door tile centre - footprint centre + 8), door_pc 93 x -13..13 (dx = door tile centre - footprint centre).
"""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, shadow, pc_door_hood
from exterior_layers import separate
from models_slateport import (UP, E, N, face, rect, decal, walls, flat, rectangle, box_walls, gable_roof, frustum,
                              post, slope, tiled, WRAPPED, gable_ends)

ROOT = os.path.join(HERE, '..')
FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
UW = 400          # a 'repeat' wider than any face: a region uniform along u is stretched, not cut
F = 20            # front wall z

# --- textures (Black 2 exterior building sets a/1/7/4, 'extNN'; map sets a/0/1/4, 'mapNNN') ---
# pack 0 (in every exterior pack's set): glass, concrete, shadows
MADO = Region('h_mado', (16, 16), 0, 0, 16, 16)                    # window glass
GLASS = Region('pc_win1', (16, 128), 1, 64, 15, 96)                # blue glass panel
GREY = Region('gate_1', (64, 32), 24, 22, 64, 32)                  # grey concrete
# pack 17: cream walls and grey-green grid windows (Sapphire's Sootopolis houses)
CREAM = Region('sth03_1', (32, 128), 2, 36, 7, 54)                 # plain cream wall
CREAM_TRIM = Region('sth03_1', (32, 128), 0, 56, 32, 58)           # beige line under it
GRID = Region('sth02_1', (64, 64), 1, 1, 23, 29)                   # grid window, 4 x 4 panes in a grey-green frame
# pack 21: dark slate panels (domes), brick (Sky Pillar), pale stone blocks (gateways, graves)
SLATE = tiled('un_buil06', (16, 16))                               # dark grey panels
BRICK_DARK = tiled('vtou_2kabe3', (32, 32))                        # dark brown brick
STONE = tiled('vtou_kabe01', (32, 32))                             # pale grey stone blocks
# pack 52 (Aspertia gym): red brick
BRICK_RED = Region('c12_gym_02', (32, 64), 0, 0, 32, 32)
# pack 0 / the towns' (models_routes): white panel, beige roof, small windows
WHITE = Region('r4_b03_yane01', (64, 64), 2, 18, 14, 26)           # white panel
SMALL_WIN = Region('r4_b03_yane01', (64, 64), 4, 7, 17, 18)        # blue window in a grey frame
BLACK = Region('r4_b03_yane01', (64, 64), 58, 0, 64, 6)            # black
BEIGE = Region('t06_h_03_a', (64, 64), 0, 0, 30, 14)               # beige siding (horizontal lines)
LEAVES = tiled('plant_tex4', (32, 32))                             # leafy planting
BLUE = Region('r4_b03_yane01', (64, 64), 4, 34, 60, 54)            # flat blue
# Black 2's sea of clouds (map set 90, chunk 521: a round stone tower top 340 units over a cloud layer of this texture at
# 1 repeat per 256 units, and chunk 542's rooftop over the same clouds); the summits' own stone and rock (map set 3)
CLOUD = tiled('o23_cloud_a', (128, 128))
PAVING = tiled('t02michi_b', (32, 32))                             # Sky Pillar top's parapet top (ground.py walls)
WALL_STONE = tiled('t02_kabe01', (32, 32))                         # and its sides
CLIFF = tiled('yamagake01', (16, 32))                              # Black 2's cliff face (heights.py)
SKIRT = Region('c14_h1_body', (64, 64), 38, 56, 64, 64)            # orange skirting (the slice's; the harbour's cranes;
                                                                   # from x 38: column 37 is transparent)

SOURCES = {'h_mado': 'ext00', 'pc_win1': 'ext00', 'gate_1': 'ext00', 'h_kage': 'ext00', 'plant_tex4': 'ext00',
           'sth03_1': 'ext17', 'sth02_1': 'ext17', 'un_buil06': 'ext21', 'vtou_2kabe3': 'ext21',
           'vtou_kabe01': 'ext21', 'c12_gym_02': 'ext52', 'r4_b03_yane01': 'ext05', 't06_h_03_a': 'ext53',
           'yane_001': 'ext00', 'c14_h1_body': 'ext57', 'rr_misel1_02': 'ext59',
           'o23_cloud_a': 'map90', 't02_kabe01': 'map3', 't02michi_b': 'map3', 'yamagake01': 'map3',
           'c5_wbt_02': 'ext55', 'c5_wbt_04': 'ext55', 'c5_wbt_05': 'ext55', 'c5_wbt_06': 'ext55', 'c5_wbt_07': 'ext55'}

# ------------------------------------------------------------------------------------------------ helpers
def polygon(cx, cz, r, n):
    """Regular n-gon round (cx, cz), r = corner distance, a flat edge facing +z, in rectangle()'s order (SW, SE,
    then round through the back): the angle decreases from the front-left corner."""
    a0 = 90 + 180 / n
    return [(cx + r * math.cos(math.radians(a0 - 360 * k / n)), cz + r * math.sin(math.radians(a0 - 360 * k / n)))
            for k in range(n)]

def mirror_x(m):
    """The model mirrored east-west (x -> -x), triangles turned round so they still face outwards."""
    out = Model(m.name)
    for mat, tris in m.tris.items():
        for t in tris:
            out.tris.setdefault(mat, []).append([(-x, y, z, u, v, c) for x, y, z, u, v, c in reversed(t)])
    return out

def dome(m, region, cx, cz, r, y0, h, n=8, steps=4, rep=(16, 16)):
    """A dome over the n-gon of corner radius r at y0, h high: rings on a quarter circle."""
    prev = polygon(cx, cz, r, n); py = y0
    for k in range(1, steps + 1):
        a = math.radians(90 * k / steps)
        rr, yy = r * math.cos(a), y0 + h * math.sin(a)
        if k == steps:
            for i in range(n):          # the cap: triangles to the top point
                a_, b_ = prev[i], prev[(i + 1) % n]
                slope(m, region, (a_[0], py, a_[1]), (b_[0], py, b_[1]), (cx, yy, cz), (cx, yy, cz), rep)
        else:
            cur = polygon(cx, cz, rr, n)
            frustum(m, region, prev, cur, py, yy, rep)
            prev, py = cur, yy

# ------------------------------------------------------------------------------------------------ Sootopolis
def soot_dome():
    """Sootopolis dome house (Sapphire metatiles 0x208-0x21f: a round cream house under a dark grey dome with a knob;
    3 wide): an octagonal cream drum (flat front face for the door), a beige line at the eaves, the dome in dark slate
    panels, a grey knob and ball on top. Door 261 (grey) in the middle."""
    m = Model('sa_dome')
    R = 25                                   # corner radius: flats 23 from the centre, front face 19 wide
    cz = F - R * math.cos(math.radians(22.5))
    oct_ = polygon(0, cz, R, 8)
    shadow(m, -26, 26, cz - 24, F + 6)
    walls(m, CREAM, oct_, 0, 36, rep=(UW, UW))
    walls(m, GREY, polygon(0, cz, R + 0.8, 8), 0, 3, rep=(UW, 3))
    walls(m, CREAM_TRIM, polygon(0, cz, R + 0.8, 8), 34, 36, rep=(UW, 2))
    dome(m, SLATE, 0, cz, R + 1, 36, 20, rep=(12, 12))
    knob = polygon(0, cz, 3, 6)
    walls(m, GREY, knob, 55, 62, rep=(UW, 7))
    dome(m, GREY, 0, cz, 4.5, 62, 4, n=6, steps=2, rep=(UW, UW))
    return m

def soot_block():
    """Sootopolis block house (metatiles 0x24b-0x24d, 0x20d-0x20f, 0x225/0x227: a cream block with a big grid window
    over the door; 3 wide): cream walls 52 high, the grid window 1 unit out above the door, a beige line, a flat
    cream roof inside a grey rim. Door 261 in the middle."""
    m = Model('sa_block')
    X, Z0, H = 22, -18, 52
    shadow(m, -X - 4, X + 4, Z0 - 4, F + 6)
    box_walls(m, -X, X, Z0, F, 0, H, CREAM, rep=(UW, UW))
    rect(m, GREY, (-X, 0, F + 1.0), E, UP, 2 * X, 3, rep=(UW, 3))
    decal(m, GRID, (0, 43, F + 1.0), E, UP, 30, 14)
    rect(m, CREAM_TRIM, (-X, 34, F + 1.0), E, UP, 2 * X, 2, rep=(UW, 2))
    rim = rectangle(-X - 1, X + 1, Z0 - 1, F + 1)
    walls(m, GREY, rim, H, H + 3, rep=(UW, 3))
    flat(m, GREY, rim, H + 3, rep=(UW, UW))
    face(m, CREAM, (-X + 2, H + 3.6, F - 2), E, N, [(0, 0), (2 * X - 4, 0), (2 * X - 4, F - Z0 - 4), (0, F - Z0 - 4)],
         rep=(UW, UW))
    return m

def origin_gate():
    """Cave of Origin entrance (Sapphire 0x220-0x253 round the warp (31,16); 5 wide, in the crater wall): two pale
    stone pillars with a lintel framing the cave mouth the heights module draws in the face (no door model)."""
    m = Model('sa_origin')
    shadow(m, -36, 36, -6, F + 6)
    for x in (-30, 18):                                          # pillars x -30..-18 and 18..30 (Sapphire's frame
        walls(m, STONE, rectangle(x, x + 12, F - 40, F), 0, 44, rep=(32, 32))   # columns 29 and 33, rows 16-18)
        flat(m, STONE, rectangle(x, x + 12, F - 40, F), 44, rep=(32, 32))
    walls(m, STONE, rectangle(-34, 34, F - 44, F - 30), 44, 54, rep=(32, 32))           # lintel over the doorway
    flat(m, STONE, rectangle(-34, 34, F - 44, F - 30), 54, rep=(32, 32))
    return m

# ------------------------------------------------------------------------------------------------ Battle Tower
def btower():
    """Battle Tower (BattleTower_Outside x 8-20, rows 0-8, door (14,8) in the middle): Sapphire's tower is a tall
    glass middle with red brick wings and a white arched porch. Here: two brick wings 72 high with cream corner
    piers and a cream cornice, the glass middle tower 120 high framed in cream, a white arch over Black 2's sliding
    door (93)."""
    m = Model('sa_btower')
    Z0 = -108
    shadow(m, -106, 106, Z0 - 6, F + 8)
    for x0, x1 in ((-100, -36), (36, 100)):                       # wings
        box_walls(m, x0, x1, Z0 + 12, F - 8, 0, 72, BRICK_RED, rep=(32, 32))
        for x in (x0, x1 - 6):
            walls(m, CREAM, rectangle(x, x + 6, F - 14, F - 8), 0, 74, rep=(UW, UW))
        rim = rectangle(x0 - 2, x1 + 2, Z0 + 10, F - 6)
        walls(m, CREAM, rim, 72, 78, rep=(UW, UW))
        flat(m, GREY, rim, 78, rep=(UW, UW))
    # middle tower: glass in a cream frame, two storeys of frames
    box_walls(m, -36, 36, Z0, F, 0, 120, CREAM, rep=(UW, UW))
    for x0 in (-30, 4):
        rect(m, GLASS, (x0, 40, F + 1.0), E, UP, 26, 76, rep=(13, 19))
    for y in (78,):
        rect(m, CREAM, (-36, y, F + 2.0), E, UP, 72, 4, rep=(UW, 4))
    rim = rectangle(-38, 38, Z0 - 2, F + 2)
    walls(m, GREY, rim, 120, 126, rep=(UW, 6))
    flat(m, GREY, rim, 126, rep=(UW, UW))
    # porch: white arch on two piers over the door. The game's curved sliding door (93, origin z 16: its arc's ends on
    # the wall, its front 0.2 behind the arch's face) stands under the arch, which comes down to 31 over it; the door
    # stood 4 units out in front of the arch, its top below the arch's foot at 34 (door_fix 2026-10-11)
    for x in (-22, 16):
        walls(m, WHITE, rectangle(x, x + 6, F, F + 10), 0, 31, rep=(UW, UW))
    face(m, WHITE, (-22, 0, F + 10), E, UP, [(0, 31), (44, 31), (44, 46), (0, 46)], rep=(UW, UW))
    flat(m, WHITE, rectangle(-22, 22, F, F + 10), 46, rep=(UW, UW))
    return m

# ------------------------------------------------------------------------------------------------ Safari Zone
def safari_inside():
    """Safari Zone entrance seen from inside (SafariZone_Southeast x 30-39, rows 29-33, door (32,33) in column 2):
    grey walls with a row of windows, flat beige roof in a grey rim, a grey canopy over Black 2's sliding door (93)
    40 units left of the centre (Route 121's side is towns5 res 408, models_routes.safari, the same building)."""
    m = Model('sa_safari')
    X, Z0, H, D = 80, -36, 36, -40
    shadow(m, -X - 6, X + 6, Z0 - 6, F + 8)
    box_walls(m, -X, X, Z0, F, 0, H, GREY, rep=(UW, 18))
    for x in (-8, 14, 36, 58):
        decal(m, SMALL_WIN, (x, 22, F + 1.0), E, UP, 14, 11)
    for x in (-66,):
        rect(m, LEAVES, (x - 10, 0, F + 1.0), E, UP, 20, 9, rep=(16, 9))
    for x in (D - 15, D + 15):
        rect(m, WHITE, (x - 1.5, 0, F + 1.2), E, UP, 3, 30, rep=(UW, 8))
    # canopy following the game's curved sliding door (door_pc 93, origin (D, 16): its arc's ends on the wall), as
    # Route 121's side (models_routes.safari; door_fix 2026-10-11)
    pc_door_hood(m, GREY, WHITE, D, F - 4, 31, 34, band_rep=(UW, 3))
    out = rectangle(-X - 2, X + 2, Z0 - 2, F + 2)
    walls(m, GREY, out, H - 1, H + 4, rep=(UW, 5))
    flat(m, GREY, out, H + 4, rep=(UW, UW))
    face(m, BEIGE, (-X + 4, H + 4.4, F - 4), E, N, [(0, 0), (2 * X - 8, 0), (2 * X - 8, F - Z0 - 8), (0, F - Z0 - 8)],
         rep=(UW, 14))
    return m

# ------------------------------------------------------------------------------------------------ Mt. Chimney
def station():
    """Mt. Chimney's cable car station: Sapphire draws Route 112's station mirrored (wing to the west of the two door
    tiles, cable to the east). models_routes.cablecar() mirrored east-west without its pylon and cable (placed
    separately: pylon()). Origin between the two door tiles like res 406; the record's door model (261) sits on the
    west door tile, a door 261 prop on the east one (data/towns/MtChimney.json)."""
    import models_routes as mr
    src = mr.cablecar()
    keep = Model('sa_station')
    for mat, tris in src.tris.items():
        for t in tris:
            if min(v[0] for v in t) < -36 and max(v[0] for v in t) < -36 + 1e-6 and mat != 'h_kage': continue
            if any(v[0] < -60 for v in t) and mat != 'h_kage': continue      # (the pylon and cable west of x -60)
            keep.tris.setdefault(mat, []).append(t)
    return mirror_x(keep)

def pylon():
    """The cable car pylon (Sapphire prop tiles (28, 33-35)): blue post 46 high with a cross beam, the cable west to
    the station's roof (8.5 tiles) and east down the mountain to the map edge, as models_routes.cablecar()'s."""
    import models_routes as mr
    m = Model('sa_pylon')
    post(m, mr.BLUE, 0, 0, 4, 0, 46)
    box_walls(m, -8, 8, -3, 3, 44, 48, mr.BLUE, rep=(16, 4))
    flat(m, mr.BLUE, rectangle(-8, 8, -3, 3), 48, rep=(16, 6))
    for a, b in (((-6, 46, 0), (-136, 47, -16)), ((6, 46, 0), (190, 20, 0))):
        L = math.dist(a, b)
        face(m, mr.GREY, a, tuple((b[k] - a[k]) / L for k in range(3)), UP, [(0, 0), (L, 0), (L, 1.5), (0, 1.5)],
             rep=(UW, 2))
    return m

# ------------------------------------------------------------------------------------------------ Sky Pillar
def pillar():
    """Sky Pillar's foot (SkyPillar_Outside x 12-16, rows 0-5, door (14,5) in the middle; the tower rises off the
    map): an octagonal dark brick tower 76 across and 160 high (the camera sees its lower part), a pale stone plinth,
    a dark arched doorway (no door model: a cave-like opening, the warp leads to the cave-built 1F)."""
    m = Model('sa_pillar')
    R = 40
    cz = F - R * math.cos(math.radians(22.5))
    shadow(m, -42, 42, cz - 40, F + 6)
    walls(m, BRICK_DARK, polygon(0, cz, R, 8), 0, 160, rep=(32, 32))
    walls(m, STONE, polygon(0, cz, R + 1.5, 8), 0, 8, rep=(32, 32))
    for y in (60, 120):
        walls(m, STONE, polygon(0, cz, R + 1.5, 8), y, y + 4, rep=(32, 32))
    arch = [(-10 + 20 * k / 8, 30 + 6 * math.sin(math.pi * k / 8)) for k in range(9)]
    face(m, BLACK, (0, 0, F + 1.0), E, UP, [(-10, 0), (10, 0)] + arch[::-1], rep=(UW, UW))
    return m

# ------------------------------------------------------------------------------------------------ Mt. Pyre
def grave():
    """Mt. Pyre gravestone (Sapphire metatiles 0x324/0x325, one tile, solid): an upright grey stone 10 wide, 4 deep,
    16 high with a rounded top on a 14 x 8 base 3 high (grey: user choice, notes/DECISIONS.md)."""
    m = Model('sa_grave')
    shadow(m, -8, 8, -5, 6)
    walls(m, GREY, rectangle(-7, 7, -4, 4), 0, 3, rep=(UW, 3), north=True)
    flat(m, GREY, rectangle(-7, 7, -4, 4), 3, rep=(UW, UW))
    top = [(-5 + 10 * k / 6, 16 + 3 * math.sin(math.pi * k / 6)) for k in range(7)]
    outline = [(-5, 3), (5, 3)] + top[::-1]               # (symmetric: the same outline faces back with u = -x)
    face(m, STONE, (0, 0, 2), E, UP, outline, rep=(32, 32))
    face(m, STONE, (0, 0, -2), (-1, 0, 0), UP, outline, rep=(32, 32))
    rect(m, STONE, (5, 3, 2), (0, 0, -1), UP, 4, 13, rep=(32, 32))       # east side
    rect(m, STONE, (-5, 3, -2), (0, 0, 1), UP, 4, 13, rep=(32, 32))      # west side
    for k in range(6):                                            # rounded top
        (xa, ya), (xb, yb) = top[k], top[k + 1]
        slope(m, STONE, (xb, yb, -2), (xa, ya, -2), (xa, ya, 2), (xb, yb, 2), rep=(32, 32))
    return m

def altar():
    """Mt. Pyre summit's altar (Sapphire 0x32a-0x32e at (22-24, 2-4)): a grey stone table 3 tiles wide on a step,
    with the round stone where the orbs rest."""
    m = Model('sa_altar')
    shadow(m, -26, 26, -26, 22)
    walls(m, GREY, rectangle(-24, 24, -22, 18), 0, 4, rep=(UW, 4), north=True)
    flat(m, GREY, rectangle(-24, 24, -22, 18), 4, rep=(UW, UW))
    walls(m, STONE, rectangle(-16, 16, -14, 8), 4, 18, rep=(32, 32))
    flat(m, STONE, rectangle(-16, 16, -14, 8), 18, rep=(32, 32))
    dome(m, GREY, 0, -3, 7, 18, 6, n=8, steps=3, rep=(UW, UW))
    return m

def stone_post():
    """Mt. Pyre summit's two round stones by the stairs (Sapphire 0x32b at (21,8) and (25,8)): a short octagonal
    grey stone 10 high with a rounded top."""
    m = Model('sa_post')
    shadow(m, -7, 7, -6, 7)
    walls(m, STONE, polygon(0, 0, 6, 8), 0, 8, rep=(32, 32))
    dome(m, STONE, 0, 0, 6, 8, 4, n=8, steps=2, rep=(32, 32))
    return m

# ------------------------------------------------------------------------------------------------ output
# ------------------------------------------------------------------------------------------------ buildings_audit
def harbour():
    """Emerald's harbour at the end of the dock of Birth Island (x 12-18, rows 24-28) and Navel Rock (x 7-13, rows
    18-22) (Emerald gTileset_Dewford 0x352-0x377, labelled water in data/labels/emerald_islands.json: solid sea, and
    nothing was drawn there): a white shed over the sea, orange ribbed gable roof, three dark windows and the orange
    crest on its front, light blue bands, two orange cranes on grey stands either side, a white plate where the dock
    meets it. Origin = the middle of the body (column 15 / 10, row 27 / 21) at the sea's collision height (-8); the
    dock top is +8. Low on purpose (eaves 16 over the dock, ridge 32): it stands south of the dock's end, between the
    camera and the player and the ferry sailor there. No door model: the harbour room is not built, the ferry lands
    on the dock (notes/EVENTS.md); its warp tile stays parked (res 481; buildings_audit 2026-10-08)."""
    import models_routes as mr
    m = Model('sa_harbour')
    X, Z0, Z1, H = 40, -24, 28, 26
    box_walls(m, -X, X, Z0, Z1, -4, H, WHITE, rep=(UW, UW))
    for y0, y1 in ((4, 6), (8, 9)):                                   # Sapphire's light blue bands
        rect(m, BLUE, (-X, y0, Z1 + 1.0), E, UP, 2 * X, y1 - y0, rep=(UW, UW))
    for x in (-24, 0, 24):                                            # windows under the eave
        decal(m, BLACK, (x, 19, Z1 + 1.0), E, UP, 14, 5)
    face(m, mr.TRIM, (-7, 9, Z1 + 2.0), E, UP, [(0, 7), (7, 0), (14, 7)], rep=(UW, UW))   # the crest (point down)
    gable_ends(m, WHITE, -X, X, Z0, Z1, H, 16 * (Z1 - Z0) / (Z1 - Z0 + 8), (UW, UW))
    gable_roof(m, mr.RIBS, -X - 3, X + 3, Z0 - 4, Z1 + 4, H - 2, H + 14, rep=(28, 40))
    flat(m, WHITE, rectangle(-24, 24, Z0 - 8, Z0), 8, rep=(UW, UW))   # the plate at the dock's end (dock top = 8)
    for s in (-1, 1):                                                 # cranes: Sapphire's columns 12 and 18
        xc = 52 * s
        for zc in (-12, 16):
            box_walls(m, xc - 6, xc + 6, zc - 5, zc + 5, -4, 6, GREY, rep=(UW, UW))
            flat(m, GREY, rectangle(xc - 6, xc + 6, zc - 5, zc + 5), 6, rep=(UW, UW))
            for x in (xc - 4, xc + 4):
                post(m, SKIRT, x, zc, 2, 6, 30)
            box_walls(m, xc - 6, xc + 6, zc - 1.5, zc + 1.5, 28, 31, SKIRT, rep=(UW, UW))
            flat(m, SKIRT, rectangle(xc - 6, xc + 6, zc - 1.5, zc + 1.5), 31, rep=(UW, UW))
            for a, b in (((xc - 4, 7, zc + 1.6), (xc + 4, 28, zc + 1.6)), ((xc + 4, 7, zc + 2.8), (xc - 4, 28, zc + 2.8))):
                L = math.dist(a, b); d = tuple((b[k] - a[k]) / L for k in range(3))   # (u x v = +z: faces south)
                face(m, SKIRT, a, d, (-d[1], d[0], 0), [(0, 0), (L, 0), (L, 1.5), (0, 1.5)], rep=(UW, UW))
    return m

def spdoor():
    """Sky Pillar's top: the doorway down to 5F in the wall band (SkyPillar_Top (16,14), Sapphire metatile 0x2a2: a dark
    arched door in a light frame), which nothing drew (the warp sat in a plain wall). The heights module's cliff face
    there leans back: it rises from the north edge of row 15 (y 0) to 8 units further north at y 28 (yamagake01; its
    lip c8_gake1_w to y 32). So the doorway leans with it: a dark arch 3 units in front of the face (terrain vs a
    building >= 2, outdoor_check 'layer'; the face is not quite planar) between two pale stone jambs 5 units proud,
    under a lintel. Origin = the foot of the face at the door tile's centre, y 0 (res 482; buildings_audit 2026-10-08)."""
    m = Model('sa_spdoor')
    arch = [(-9 + 18 * i / 8, 20 + 5 * math.sin(math.pi * i / 8)) for i in range(9)]
    face(m, BLACK, (0, 0, 3.0), E, (0, 28 / math.hypot(28, 8), -8 / math.hypot(28, 8)),
         [(-9, 0), (9, 0)] + [(x, y * math.hypot(28, 8) / 28) for x, y in arch[::-1]], rep=(UW, UW))
    lean = (0, 28 / math.hypot(28, 8), -8 / math.hypot(28, 8))       # up the face
    L = lambda y: y * math.hypot(28, 8) / 28                         # height -> length along the face
    for x0, x1 in ((-13, -9), (9, 13)):                              # jambs: front 5 units proud, sides back to the face
        face(m, STONE, (x0, 0, 5.0), E, lean, [(0, 0), (x1 - x0, 0), (x1 - x0, L(26)), (0, L(26))], rep=(32, 32))
        face(m, STONE, (x1, 0, 5.0), (0, 0, -1), lean, [(0, 0), (5, 0), (5, L(26)), (0, L(26))], rep=(32, 32))
        face(m, STONE, (x0, 0, 0.0), (0, 0, 1), lean, [(0, 0), (5, 0), (5, L(26)), (0, L(26))], rep=(32, 32))
    face(m, STONE, (-14, L(25) * lean[1], 5.5 + L(25) * lean[2]), E, lean, [(0, 0), (28, 0), (28, L(5)), (0, L(5))],
         rep=(32, 32))                                               # lintel
    return m

# Sky Pillar's top and Navel Rock's top (buildings_audit 2026-10-08, polish): the summits floated in the clear colour (a
# flat light blue). Black 2's own high places stand over a sea of clouds: chunk 521 (map set 90: a round stone tower top
# whose cloud layer, texture o23_cloud_a at one repeat per 256 units, lies 340 units below its floor) and chunk 542 (a
# rooftop over the same clouds). Black 2 draws only the buildings of the chunks loaded round the player, so every cell
# of a summit's matrix gets its own model (its own cloud sheet, the tower pieces inside the cell), placed on a floor
# tile of that cell; the cloud sheets of neighbouring cells lie 4 units apart (the highest one loaded shows) and take
# their texture coordinates from the summit's map position, so they line up.
GROUP_ORIGIN = {'SkyPillar_Top': (18, 23), 'NavelRock_Top': (3, 2)}    # world.json "standalone" origins (map tile 0, 0)

def cloud_sheet(m, ox, oz, y):
    """A flat sheet of Black 2's clouds 1,600 x 1,600 units round (0, y, 0) of a model whose origin is map tile
    position (ox, oz); 4 x 4 squares; texture coordinates from the map position (one repeat per 256 units)."""
    S = 400
    for i in range(4):
        for j in range(4):
            x0, z0 = -800 + S * i, -1000 + S * j            # (north reaches further: the camera looks north, down)
            q = [(x0, z0 + S), (x0 + S, z0 + S), (x0 + S, z0), (x0, z0)]
            v = [(x, y, z, (x + ox * 16) / 256, -(z + oz * 16) / 256) for x, z in q]
            m.tri(CLOUD.tex, [v[0], v[1], v[2]]); m.tri(CLOUD.tex, [v[0], v[2], v[3]])

def _cells_of(full, mapname, pieces, depth):
    """Split a model made in map units (x = map x * 16, z = map row * 16, y over the summit's floor) by the cell
    (32 x 32 world tiles) each triangle's centre lies in; {name: Model} with each piece moved to its own origin
    pieces[name] = (cell, (map x, map row)) and a cloud sheet under it, sheets 4 units apart."""
    gx, gz = GROUP_ORIGIN[mapname]
    out = {}
    for k, (name, (cell, (ox, oz))) in enumerate(pieces.items()):
        m = Model('sa_' + name)
        for mat, tris in full.tris.items():
            for t in tris:
                cx = sum(v[0] for v in t) / 3 / 16 + gx; cz = sum(v[2] for v in t) / 3 / 16 + gz
                if (int(cx // 32), int(cz // 32)) != cell: continue
                m.tris.setdefault(mat, []).append([(v[0] - ox * 16, v[1], v[2] - oz * 16) + tuple(v[3:]) for v in t])
        cloud_sheet(m, ox, oz, depth - 4 * k)
        out[name] = m
    return out

def sky_pillar_top():
    """Sky Pillar's top as the top of a tower, res 483-486, one model per cell: under the south parapet (map row 19.0;
    the floor is 32 high at x 0-6 and 19-26, 0 in the sunken middle x 7-18) the tower's face goes down into the clouds
    in the tower foot's dark brick (res 477) with its pale stone bands and a row of dark windows; a low curb of the
    parapet's own stone (t02_kabe01 sides, t02michi_b top) runs just outside the floor's west, east and north edges
    (rows 3-12 and 15-17 on the sides: the wall band and the parapet have their blocks there); clouds 200 under the
    upper floor. Nothing stands on a tile: the collision is the map's, unchanged."""
    full = Model('sptop')
    zf = 19 * 16                                   # the parapet's south face
    for x0, x1, top in ((0, 7, 0), (7, 14, -32), (14, 19, -32), (19, 27, 0)):    # (split at the cells' edge, x 14)
        rect(full, BRICK_DARK, (x0 * 16, -240, zf), E, UP, (x1 - x0) * 16, top + 240, rep=(32, 32))
        for y in (-60, -140):
            rect(full, STONE, (x0 * 16, y, zf + 1.0), E, UP, (x1 - x0) * 16, 4, rep=(32, 32))
    for x in range(1, 27, 3): decal(full, BLACK, (x * 16 + 8, -100, zf + 1.0), E, UP, 6, 16)
    H, T, zn = 6, 3, 3 * 16
    for x0, x1 in ((-T, 14 * 16), (14 * 16, 27 * 16 + T)):     # north curb (its south face and top)
        rect(full, WALL_STONE, (x0, 0, zn), E, UP, x1 - x0, H, rep=(32, 32))
        flat(full, PAVING, rectangle(x0, x1, zn - T, zn), H, rep=(32, 32))
    for r0, r1 in ((3, 9), (9, 13), (15, 18)):     # west and east curbs (split at the cells' edge, row 9)
        z0, z1 = r0 * 16, r1 * 16
        face(full, WALL_STONE, (0, 0, z1), (0, 0, -1), UP, [(0, 0), (z1 - z0, 0), (z1 - z0, H), (0, H)], rep=(32, 32))
        flat(full, PAVING, rectangle(-T, 0, z0, z1), H, rep=(32, 32))
        face(full, WALL_STONE, (27 * 16, 0, z0), (0, 0, 1), UP, [(0, 0), (z1 - z0, 0), (z1 - z0, H), (0, H)], rep=(32, 32))
        flat(full, PAVING, rectangle(27 * 16, 27 * 16 + T, z0, z1), H, rep=(32, 32))
    # (map tiles of the upper floor, 32 high, one per cell: world tile = map + (18, 23), cells of 32 tiles)
    pieces = {'spsky_nw': ((0, 0), (5.5, 5.5)), 'spsky_ne': ((1, 0), (20.5, 5.5)),
              'spsky_sw': ((0, 1), (5.5, 11.5)), 'spsky_se': ((1, 1), (22.5, 11.5))}
    return _cells_of(full, 'SkyPillar_Top', pieces, -200)

def navel_top():
    """Navel Rock's summit as the top of the rock, res 487 (its matrix is one cell): the summit's floor (map x 9-16,
    rows 9-24 with chamfered ends, y 0) sat on nothing; the rock goes straight down from its edge into the clouds (Black 2's cliff face
    yamagake01, as the terrain's), clouds 200 under the floor."""
    full = Model('navel')
    top = [(10, 24), (15, 24), (15, 22), (16, 22), (16, 11), (15, 11), (15, 10), (14, 10), (14, 9), (11, 9), (11, 10),
           (10, 10), (10, 11), (9, 11), (9, 22), (10, 22)]    # the floor's own outline (map tiles; SW, round by the east)
    walls(full, CLIFF, [(x * 16, z * 16) for x, z in top], -240, 0, rep=(32, 32))
    return _cells_of(full, 'NavelRock_Top', {'navel': ((0, 0), (12.5, 16.5))}, -200)

# ------------------------------------------------------------------------------------------------ the PWT's entrance
# Black 2's PWT dome (zone 191's plaza; pack 55 res 330, c5_wbt_01) is dressed in [bytes]: grey wall panels with a pale
# pillar and a yellow foot (c5_wbt_04), steel lattice (c5_wbt_02, cut out), blue glass panes in a grey frame
# (c5_wbt_05), the red and the blue crest banner (c5_wbt_06: each half of the texture is half a banner, the crest's
# centre on column 0 / 32: mirrored there), floodlights (c5_wbt_07)
WBT_PANEL = tiled('c5_wbt_04', (32, 64))
WBT_PALE = Region('c5_wbt_04', (32, 64), 24, 6, 30, 54)            # the pale pillar
WBT_GLASS = tiled('c5_wbt_05', (16, 16))
WBT_TRUSS = tiled('c5_wbt_02', (32, 32))
WBT_LAMPS = Region('c5_wbt_07', (32, 32), 0, 1, 32, 11)            # two floodlights on a bar
WBT_LAMP = Region('c5_wbt_07', (32, 32), 1, 13, 19, 31)            # one big floodlight

def crest_banner(m, c, w, y0, y1, x, y, z, bw, bh):
    """A crest banner bw x bh, centred on x with its foot at y, on the plane z facing south: texel columns c - w..c of
    c5_wbt_06 mirrored about column c (the crest's centre: 0 red, 32 blue), rows y0..y1."""
    out = c + w if c == 0 else c - w
    for x0, (a, b) in ((x - bw / 2, (out, c)), (x, (c, out))):
        face(m, Region('c5_wbt_06', (32, 64), a, y0, b, y1), (x0, y, z), E, UP,
             [(0, 0), (bw / 2, 0), (bw / 2, bh), (0, bh)], (bw / 2, bh))

def pwt():
    """The PWT's entrance on the Battle Tower island (BattleTower_Outside x 19-21, rows 10-12, door (20,12) in the
    middle: data/hoenn_map_additions.json; the user's decision 2026-10-08), a small hall in the PWT dome's dress: grey
    panel walls 36 high, the red and the blue crest banner either side of Black 2's curved sliding door (93, an arc of
    radius 13.9 about the wall line) under pale jambs and a curved glass canopy, a glass dome on the flat roof behind a
    screen board with the blue crest and a floodlight bar, two lattice masts with a floodlight each at the back corners
    (the PWT's light towers). It keeps inside its footprint (x -24..24, z -16..32): the Bug Catcher wanders on the
    lawn right west of it (res 488; battle_tower 2026-10-08)."""
    m = Model('sa_pwt')
    X, Z0, H = 22, -14, 36
    shadow(m, -24, 24, Z0 - 2, F + 8)
    box_walls(m, -X, X, Z0, F, 0, H, WBT_PANEL, rep=(22, H))
    rim = rectangle(-X - 1, X + 1, Z0 - 1, F + 1)
    walls(m, GREY, rim, H - 1, H + 2, rep=(UW, 3))
    flat(m, GREY, rim, H + 2, rep=(UW, UW))
    crest_banner(m, 0, 9, 6, 58, -19, 5, F + 1.0, 5, 24)          # red, west of the door
    crest_banner(m, 32, 9, 6, 58, 19, 5, F + 1.0, 5, 24)          # blue, east
    for x0 in (-16.5, 13.5):                                      # door jambs
        walls(m, WBT_PALE, rectangle(x0, x0 + 3, F, F + 3), 0, 30, rep=(UW, UW))     # (up to the canopy)
    arc = [(15 * math.cos(math.radians(a)), F + 15 * math.sin(math.radians(a))) for a in range(150, 0, -30)]
    canopy = [(-16.5, F), (-16.5, F + 3)] + arc + [(16.5, F + 3), (16.5, F)]
    walls(m, WBT_PALE, canopy, 30, 33, rep=(UW, UW))
    flat(m, WBT_GLASS, canopy, 33, rep=(10, 10))
    dome(m, WBT_GLASS, 0, 1, 16.5, H + 2, 18, rep=(10, 10))
    bx, bz0, bz1, top = 14, F - 2, F + 2, H + 14                 # the screen board
    box_walls(m, -bx, bx, bz0, bz1, H + 2, top, WBT_PALE, rep=(UW, UW))
    flat(m, GREY, rectangle(-bx, bx, bz0, bz1), top, rep=(UW, UW))
    crest_banner(m, 32, 12, 8, 56, 0, H + 3.5, bz1 + 1.0, 22, 7.5)
    decal(m, WBT_LAMPS, (0, top - 1.6, bz1 + 1.0), E, UP, 22, 2.6)
    for xc in (-18, 18):                                          # light masts
        rect(m, WBT_TRUSS, (xc - 2.5, H + 2, -5.5), E, UP, 5, 24, rep=(5, 8))     # (one plane, as the dome's)
        box_walls(m, xc - 3.5, xc + 3.5, -11, -5, H + 26, H + 31, GREY, rep=(UW, UW))
        flat(m, GREY, rectangle(xc - 3.5, xc + 3.5, -11, -5), H + 31, rep=(UW, UW))
        decal(m, WBT_LAMP, (xc, H + 28.5, -4.0), E, UP, 5, 5)
    return m

def models():
    return {'dome': soot_dome(), 'block': soot_block(), 'origin': origin_gate(), 'btower': btower(),
            'safari': safari_inside(), 'station': station(), 'pylon': pylon(), 'pillar': pillar(), 'grave': grave(),
            'altar': altar(), 'post': stone_post(), 'harbour': harbour(), 'spdoor': spdoor(), **sky_pillar_top(),
            **navel_top(), 'pwt': pwt()}

def texture_png(tex, setname, out):
    """Decode texture tex of Black 2 set setname ('extNN' building set, 'mapNNN' map set) into out/tex.png."""
    import b2files, nsbtx
    data = b2files.building_textures(FILES, int(setname[3:])) if setname.startswith('ext') else \
        b2files.map_textures(FILES, int(setname[3:]))
    for n, img, _ in nsbtx.decode(data):
        if n == tex: img.save(os.path.join(out, tex + '.png')); return
    raise SystemExit(f'{tex} is not in {setname}')

def write_models(out, ms):
    os.makedirs(out, exist_ok=True)
    used = set()
    for name, m in ms.items():
        separate(m)        # layers >= 1 unit apart (melonDS flicker; b2tools/exterior_layers.py)
        n = m.write(os.path.join(out, f'{name}.dae'),
                    wrap={t: ('WRAP', 'WRAP') if t in WRAPPED else ('CLAMP', 'CLAMP') for t in m.tris})
        used |= set(m.tris)
        print(f'{name}: {n} triangles, textures {sorted(m.tris)}')
    for t in sorted(used): texture_png(t, SOURCES[t], out)
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in sorted(used)))
    open(os.path.join(out, 'textures.txt'), 'w').write(''.join(f'{SOURCES[t]} {t}\n' for t in sorted(used)))

if __name__ == '__main__':
    write_models(sys.argv[1], models())
