"""Rustboro City's buildings: Sapphire's shapes, Black 2 textures.

    python3 models_rustboro.py ../work/buildings/rustboro

Writes (res ids in data/buildings/towns1.json; footprints in notes/TOWNS_TOWNS1.md):
  grey5.dae   res 323  grey house with a corrugated roof, 5x5 (House 1 and House 2)
  flat1.dae   res 324  tan flat-roofed block, 9x6, two storeys, roof vent (Flat 1)
  school.dae  res 325  tan flat-roofed block, 7x5, roof vent (Trainer's School)
  cutter.dae  res 326  tan flat-roofed block, 5x5, roof vent (Cutter's house)
  house3.dae  res 327  tan flat-roofed block, 6x5, door half a tile left of centre (House 3)
  flat2.dae   res 328  tall grey block, 7x9, four storeys (Flat 2)
  annex.dae   res 332  door-less grey block, 4x8, two storeys (east of the fountain; placed as a prop)
  devon.dae   res 329  Devon Corporation: tan stone, a central tower with the doors and two lower wings, 10x9
  lamp.dae    res 333  street lamp, 1x1 (Sapphire's Rustboro lamps; placed as props)
The Gym is the generic res 320 (models_petalburg.py), the Center res 0 and the Mart res 3 (models_oldale.py), the
fountain Black 2's own pack-0 fountain (res 24).
Origin = footprint centre on the ground (Devon: centre of its tower front), +z = front; front wall 4 units into the
door tile.
"""
import os, sys, math, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, rect, decal, box_walls, gable_roof, face, slope, shadow, DOOR_WALL, pc_door_hood
from models_petalburg import write, wface, wgable, UP, E, CREST, UW, PANEL, WRAPPED

# new textures for this group (see notes/TOWNS_TOWNS1.md)
FLATROOF = Region('sand_tex001', (32, 32), 0, 0, 32, 32)       # tan tiles in a grid (Striaton sand, pack 1)
TAN = Region('c1sch001', (64, 64), 45, 9, 63, 26)               # plain tan stone (Striaton school, pack 1)
CORNICE = Region('c1sch001', (64, 64), 0, 0, 44, 6)             # light stone cornice
FRIEZE = Region('c1sch001', (64, 64), 0, 7, 44, 19)             # stone brick band
BALUSTER = Region('c1sch001', (64, 64), 0, 21, 24, 36)          # grey balustrade (transparent gaps)
GREY = Region('bill_kabe', (32, 32), 0, 9, 28, 18)              # grey building wall (Mistralton, pack 9)
DARKWIN = Region('c8w_001', (32, 32), 0, 6, 32, 30)             # dark window with a light sill (Opelucid, pack 12)
DARK = Region('c8w_001', (32, 32), 0, 0, 32, 8)                 # black
# pack 0 / slice textures
STRIPES = Region('r4_b03_yane01', (64, 64), 2, 20, 14, 27)      # light grey with a dark lower edge: corrugated metal when repeated
WHITE = Region('r4_b03_yane01', (64, 64), 2, 18, 14, 26)
SOURCES = {'sand_tex001': 'ext01', 'c1sch001': 'ext01', 'bill_kabe': 'ext09', 'c8w_001': 'ext12',
           'r4_b03_yane01': 'ext05', 'pc_win1': 'ext00', 'h_kage': 'ext00'}

def win(m, x, y, z, w=12, h=8):
    decal(m, DARKWIN, (x, y, z + 1.0), E, UP, w, h)

def flat_roof(m, x0, x1, z0, z1, y, rim=2):
    """Flat roof: tiled top at y + rim inside a raised cornice rim (Sapphire's flat roofs with an edge)."""
    wface(m, 'sand_tex001', (0, y + rim - 0.5, 0), E, (0, 0, -1), [(x0, -z1), (x1, -z1), (x1, -z0), (x0, -z0)], (32, 32))
    box_walls(m, x0 - 1, x1 + 1, z0 - 1, z1 + 1, y, y + rim, CORNICE, rep=(UW, rim), sides='sew')
    # rim tops (thin light strips around the edge)
    for a, b in (((x0 - 1, z1 + 1), (x1 + 1, z1 - 1)), ((x0 - 1, z0 + 1), (x1 + 1, z0 - 1)),
                 ((x0 - 1, z1 + 1), (x0 + 1, z0 - 1)), ((x1 - 1, z1 + 1), (x1 + 1, z0 - 1))):
        face(m, CORNICE, (0, y + rim, 0), E, (0, 0, -1), [(a[0], -a[1]), (b[0], -a[1]), (b[0], -b[1]), (a[0], -b[1])], rep=(UW, UW))

def vent(m, x, z, y):
    """Sapphire's rooftop vent box (corner of the flat roof)."""
    box_walls(m, x - 6, x + 6, z - 6, z + 6, y, y + 6, GREY, rep=(28, 9))
    face(m, GREY, (0, y + 6, 0), E, (0, 0, -1), [(x - 6, -(z + 6)), (x + 6, -(z + 6)), (x + 6, -(z - 6)), (x - 6, -(z - 6))], rep=(28, 9))
    face(m, DARK, (0, y + 7, 0), E, (0, 0, -1), [(x - 4, -(z + 4)), (x + 4, -(z + 4)), (x + 4, -(z - 4)), (x - 4, -(z - 4))], rep=(32, 32))  # opening

def tan_block(name, width, rows, door_dx, storeys, windows, vent_at=None):
    """Tan stone block with a flat tiled roof (Flat 1, School, Cutter's, House 3). width/rows = Sapphire footprint in
    tiles incl. the walk-behind roof row; windows = [(x, storey)] window centres.
    The ground storey is 36 high (frieze or storey band above it): Black 2's door model (261) reaches y 32; the frieze
    was at 24-30 and a storey band at 18-20, across the door (door_fix 2026-10-11)."""
    m = Model(name)
    hw = width * 8 - 3
    F = 20
    B = F - (rows * 16 - 4) + 6
    H = 24 + 16 * storeys
    shadow(m, -hw - 4, hw + 4, B - 4, F + 6)
    box_walls(m, -hw, hw, B, F, 0, H, TAN, rep=(UW, 25.5), sides='sew')
    rect(m, FRIEZE, (-hw, H - 6, F + 1.0), E, UP, 2 * hw, 6, rep=(44, 6))
    for k in range(1, storeys):
        rect(m, FRIEZE, (-hw, 20 + 16 * k, F + 1.0), E, UP, 2 * hw, 2, rep=(44, 2))
    for x, s in windows:
        win(m, x, 18 if s == 0 else 28 + 16 * s, F)
    flat_roof(m, -hw, hw, B, F, H)
    if vent_at: vent(m, hw - 10, B + 10, H + 2)
    return m

def grey5():
    """Grey house with a low corrugated metal roof, two dark windows (House 1, House 2): 5x5."""
    m = Model('rus_grey5')
    hw, F, B, H = 37, 20, -42, DOOR_WALL      # (H 26: the eave at 25.5 under the door's top 32; door_fix 2026-10-11)
    shadow(m, -hw - 4, hw + 4, B - 4, F + 6)
    box_walls(m, -hw, hw, B, F, 0, H, GREY, rep=(UW, 13.5), sides='sew')
    for x in (-18, 18):
        win(m, x, 18, F, 12, 9)
    rect(m, DARK, (-hw, 0, F + 1.0), E, UP, 2 * hw, 1.5, rep=(UW, 1.5))
    zc = (F + B) / 2
    for x, d, z0 in ((hw, (0, 0, -1), F), (-hw, (0, 0, 1), B)):
        face(m, GREY, (x, H, z0), d, UP, [(0, 0), (F - B, 0), ((F - B) / 2, 6)], rep=(28, 9))
    gable_roof(m, STRIPES, -hw - 2, hw + 2, B - 3, F + 3, H - 0.5, H + 6, rep=(UW, 8))
    return m

def grey_block(name, width, rows, H, cols, levels, skip=()):
    """Tall grey block with a corrugated roof (Sapphire's Rustboro flats): width/rows = footprint in tiles incl. the
    walk-behind roof row, H = wall height, windows at x in cols on each y in levels (skip: (x, y) left out)."""
    m = Model(name)
    hw, F = width * 8 - 3, 20
    B = F - (rows * 16 - 4) + 6
    shadow(m, -hw - 4, hw + 4, B - 4, F + 8)
    box_walls(m, -hw, hw, B, F, 0, H, GREY, rep=(UW, 13.5), sides='sew')
    for y in levels:
        for x in cols:
            if (x, y) not in skip: win(m, x, y, F, 12, 9)
    rect(m, DARK, (-hw, 0, F + 1.0), E, UP, 2 * hw, 1.5, rep=(UW, 1.5))
    gable_roof(m, STRIPES, -hw - 2, hw + 2, B - 3, F + 3, H - 0.5, H + 8, rep=(UW, 8))
    for x, d, z0 in ((hw, (0, 0, -1), F), (-hw, (0, 0, 1), B)):
        face(m, GREY, (x, H, z0), d, UP, [(0, 0), (F - B, 0), ((F - B) / 2, 8)], rep=(28, 9))
    return m

def flat2():
    """Flat 2: 7x9, four storeys of three windows (the door, 1.5 tiles left of centre, replaces the first one)."""
    return grey_block('rus_flat2', 7, 9, 70, (-28, 0, 28), (12, 27, 42, 57), skip={(-28, 12)})

def annex():
    """The door-less grey block east of the fountain (Sapphire x 31-34, rows 39-46 incl. the walk-behind roof row):
    two storeys of two windows. Placed as a prop."""
    return grey_block('rus_annex', 4, 8, 58, (-11, 11), (16, 36))

def devon():
    """Devon Corporation (no plan footprint: its doors are walkable in Sapphire, so it is placed as a prop at the
    tower front). Central tower x -32..32 (tiles 10-13) reaching the door row, three storeys of columns, a roof
    terrace with a parapet; wings x -80..-32 and 32..80 (tiles 7-9, 14-16) ending one row further north. The game's
    curved sliding door (door_pc 93, origin x 0, z 0: its arc's ends on the tower front) stands under a canopy
    following its curve (it stood 4-14 units out of the wall, under nothing; door_fix 2026-10-11)."""
    m = Model('rus_devon')
    F = 4                                # tower front: 4 units into the door row (origin = door row's north edge)
    FW = F - 16                          # wings' front (one row north)
    B = F - 8 * 16 - 4 + 6               # back: footprint starts 8 rows above the door row
    shadow(m, -84, 84, B - 4, F + 6)
    # wings: two storeys + roof terrace
    for x0, x1 in ((-78, -33), (33, 78)):
        box_walls(m, x0, x1, B, FW, 0, 46, TAN, rep=(UW, 23), sides='sew')
        for k, y in enumerate((14, 30)):
            rect(m, FRIEZE, (x0, y + 8, FW + 1.0), E, UP, x1 - x0, 3, rep=(44, 3))
            for x in (x0 + 12, x1 - 12):
                win(m, x, y, FW, 6, 10)
        rect(m, FRIEZE, (x0, 40, FW + 1.0), E, UP, x1 - x0, 6, rep=(44, 6))
        flat_roof(m, x0, x1, B, FW, 46, 3)
    # central tower: three storeys, columns on the front, arched entrance (the game draws the door at x 0)
    box_walls(m, -32, 32, B, F, 0, 62, TAN, rep=(UW, 31), sides='sew')
    for y in (18, 34, 50):
        if y < 30:                                               # (left and right of the door's arc, x -13.2..13.2)
            rect(m, FRIEZE, (-32, y, F + 1.0), E, UP, 17, 3, rep=(44, 3)); rect(m, FRIEZE, (15, y, F + 1.0), E, UP, 17, 3, rep=(44, 3))
        else: rect(m, FRIEZE, (-32, y, F + 1.0), E, UP, 64, 3, rep=(44, 3))
    for x in (-26, -9, 9, 26):                                   # columns (cornice stone strips)
        rect(m, CORNICE, (x - 2, 18, F + 2.0), E, UP, 4, 40, rep=(4, 40))
    for x in (-17.5, 0, 17.5):
        for y in (26, 42):
            win(m, x, y, F, 8, 10)
    rect(m, FRIEZE, (-32, 56, F + 1.0), E, UP, 64, 6, rep=(44, 6))
    flat_roof(m, -32, 32, B, F, 62, 3)
    pc_door_hood(m, CORNICE, CORNICE, 0, F - 4, 31, 34, band_rep=(UW, 3))
    # Devon emblem on the tower's crown (Sapphire draws a logo there): Poké Ball crest stand-in is not Devon's,
    # so the crown stays plain stone.
    return m

def lamp():
    """Rustboro street lamp: dark post on a small base, a light glass lantern on top (seen from Gen 5's raised camera
    mostly from above, so its top is light too) and a small dark finial (1 tile; Sapphire's lamp is 2 tiles tall,
    the upper one walk-behind)."""
    m = Model('rus_lamp')
    shadow(m, -5, 5, -4, 5)
    box_walls(m, -3, 3, -3, 3, 0, 3, GREY, rep=(28, 9))
    face(m, GREY, (0, 3, 0), E, (0, 0, -1), [(-3, -3), (3, -3), (3, 3), (-3, 3)], rep=(28, 9))
    box_walls(m, -1, 1, -1, 1, 3, 25, DARK, rep=(32, 32))
    box_walls(m, -4, 4, -4, 4, 25, 26.5, DARK, rep=(32, 8))            # lantern seat
    box_walls(m, -3.5, 3.5, -3.5, 3.5, 26.5, 33, WHITE, rep=(12, 8))     # lantern (white-grey glass)
    face(m, WHITE, (0, 33, 0), E, (0, 0, -1), [(-3.5, -3.5), (3.5, -3.5), (3.5, 3.5), (-3.5, 3.5)], rep=(12, 8))
    box_walls(m, -1.5, 1.5, -1.5, 1.5, 33, 35, DARK, rep=(32, 8))      # finial
    face(m, DARK, (0, 35, 0), E, (0, 0, -1), [(-1.5, -1.5), (1.5, -1.5), (1.5, 1.5), (-1.5, 1.5)], rep=(32, 8))
    return m

# ------------------------------------------------------------------------------------------------------------------
# Town look pass (town_look, 2026-11-09; tools in work/agents/town_look/tools): Black 2's proportions. Black 2's buildings stand about
# as tall as they are deep (height/depth 0.8-1.5, median ~1.1: b2tools exports of packs 0/1/5/9/12/16/52/53/57); these
# stood at 0.5-0.74 (Devon 0.5, Flat 2 0.56, the School 0.68), a big flat roof over a low wall from the field camera.
# Upper storeys are now ~28 units (Black 2's c8/c1/r4 buildings: 24-32; the player is ~32), the ground storey 36 over
# the 32-unit door. Whole storeys are one quad each with a WRAP texture of Black 2 facades (2 triangles: pack 0 is read
# whole into the field heap, ~28 B a triangle): Route 4's stone building kabe_002 (ext05: arched windows between
# pilasters over ashlar, Rustboro's tan stone) and kabe_001 (ext05: a grey storey of dark windows over a light sill,
# Rustboro's grey blocks). The rear rows keep the old height where people walk behind (walk-behind roof rows, streets
# north of a block): the camera hides no more of them than before (work/agents/town_look/tools/occl.py).
STONE, GREYF = 'rus_stone', 'rus_greywin'
# (ext05's kabe_002 / kabe_001 under our own names: pack 0's own set, Accumula's, already has a 'kabe_001' and a
# 'kabe_002' of its own - other images - and a merge keeps the first texture of a name, so the models drew those. The
# renamed copies go into work/tex/townlook.nsbtx (+ work/tex/townlook/*.png), written by townlook_textures() below.)
TOWNLOOK_TEX = {STONE: ('ext05', 'kabe_002'), GREYF: ('ext05', 'kabe_001')}
SOURCES.update({STONE: 'townlook', GREYF: 'townlook'})

def townlook_textures():
    """work/tex/townlook.nsbtx (+ work/tex/townlook/*.png): b2tools/townlook_tex.py (TOWNLOOK_TEX's renamed copies
    and the other town look textures)."""
    import townlook_tex
    assert all(townlook_tex.RENAMED.get(k) == v for k, v in TOWNLOOK_TEX.items())
    townlook_tex.build()
# Every detail of a model in its own facade texture (a material costs ~300 B of pack 0, a triangle ~28 B): kabe_002's
# rows 0-5 (light edge + olive cornice), its arch interiors (dark), its light ashlar joints (rows 62-63, uniform);
# kabe_001's plain band (rows 0-6) and dark band (rows 28-31).
K2_CORNICE = Region(STONE, (64, 64), 0, 0, 64, 6)
K2_LIGHT = Region(STONE, (64, 64), 0, 62, 64, 64)
K2_DARK = Region(STONE, (64, 64), 9, 12, 15, 21)
K2_ASHLAR = Region(STONE, (64, 64), 0, 32, 64, 64)
K1_GREY = Region(GREYF, (64, 64), 0, 0, 64, 6)
K1_DARK = Region(GREYF, (64, 64), 0, 28, 64, 32)
K1_WIN = Region(GREYF, (64, 64), 8, 9, 16, 14)
GROUND, STOREY = 36, 28                                          # ground storey over the door, upper storeys

def wband(m, tex, pa, pb, y0, y1, v0, v1, per, u0=0.0):
    """One vertical quad from ground point pa to pb (x, z; left to right as you face the wall from outside) between
    y0 and y1, showing rows v0..v1 (uv, v up) of a whole wrapped texture repeated every `per` units along the wall."""
    L = math.hypot(pb[0] - pa[0], pb[1] - pa[1]); u1 = u0 + L / per
    m.quad(tex, [(pa[0], y0, pa[1], u0, v0), (pb[0], y0, pb[1], u1, v0), (pb[0], y1, pb[1], u1, v1), (pa[0], y1, pa[1], u0, v1)])
    WRAPPED.add(tex)

def walls3(m, tex, x0, x1, z0, z1, y0, y1, v0, v1, per, sides='sew'):
    """wband on the front (s), east and west walls of a box (the north wall faces away from the camera)."""
    if 's' in sides: wband(m, tex, (x0, z1), (x1, z1), y0, y1, v0, v1, per)
    if 'e' in sides: wband(m, tex, (x1, z1), (x1, z0), y0, y1, v0, v1, per)
    if 'w' in sides: wband(m, tex, (x0, z0), (x0, z1), y0, y1, v0, v1, per)

def top(m, region, x0, x1, z0, z1, y):
    face(m, region, (0, y, 0), E, (0, 0, -1), [(x0, -z1), (x1, -z1), (x1, -z0), (x0, -z0)], rep=(UW, UW))

def coping(m, x0, x1, z0, z1, y, h=3, band=K2_CORNICE, cap=K2_LIGHT):
    """A cornice band round the top of the walls (front and sides) and its top strips (cap)."""
    box_walls(m, x0 - 1, x1 + 1, z0 - 1, z1 + 1, y, y + h, band, rep=(UW, h), sides='sew')
    for a, b in (((x0 - 1, z1 + 1), (x1 + 1, z1 - 1)), ((x0 - 1, z1 + 1), (x0 + 1, z0 - 1)), ((x1 - 1, z1 + 1), (x1 + 1, z0 - 1))):
        face(m, cap, (0, y + h, 0), E, (0, 0, -1), [(a[0], -a[1]), (b[0], -a[1]), (b[0], -b[1]), (a[0], -b[1])], rep=(UW, UW))

def roof_slab(m, x0, x1, z0, z1, y):
    wface(m, 'sand_tex001', (0, y, 0), E, (0, 0, -1), [(x0, -z1), (x1, -z1), (x1, -z0), (x0, -z0)], (32, 32))

def roof_box(m, x, z, y, w, d, h, side, cap, front=None, fw=None, fh=None):
    """A box on a roof (vent housing, air-conditioning unit, roof-access hut): sides of `side`, a top of `cap`, and a
    dark opening/grille `front` (fw x fh) on its south face."""
    box_walls(m, x - w / 2, x + w / 2, z - d / 2, z + d / 2, y, y + h, side, rep=(UW, h), sides='sew')
    top(m, cap, x - w / 2, x + w / 2, z - d / 2, z + d / 2, y + h)
    if front: decal(m, front, (x, y + (fh or h) / 2 + 0.5, z + d / 2 + 1.0), E, UP, fw or w - 4, fh or h - 2)

def stone_mass(m, x0, x1, z0, z1, storeys, sides='sew', base=True, y0=0):
    """Rustboro's tan stone: an ashlar ground storey (kabe_002's lower half) and `storeys` storeys of arched windows
    (its upper half); returns the wall top."""
    y = y0
    if base:
        walls3(m, STONE, x0, x1, z0, z1, y, y + GROUND, 0.0, 0.5, 64, sides); y += GROUND
    for _ in range(storeys):
        walls3(m, STONE, x0, x1, z0, z1, y, y + STOREY, 0.5, 1.0, 56, sides); y += STOREY
    return y

def grey_mass(m, x0, x1, z0, z1, storeys, first=GROUND, h=24, sides='sew', y0=0):
    """Rustboro's grey blocks: a ground storey `first` high and `storeys` storeys of h, each kabe_001's upper half
    (dark windows over a light sill and a dark band; a window a tile)."""
    walls3(m, GREYF, x0, x1, z0, z1, y0, y0 + first, 0.5, 1.0, 64 * first / 32, sides)
    y = y0 + first
    for _ in range(storeys):
        walls3(m, GREYF, x0, x1, z0, z1, y, y + h, 0.5, 1.0, 48, sides); y += h
    return y

def stone_block(name, width, rows, storeys, back_rows=1, back_storeys=None, vent_at=True, hut=False, ac=None):
    """A tan stone block (Flat 1, the School, Cutter's house, House 3): `storeys` storeys over the ground storey on the
    front part; the last `back_rows` footprint rows (the walk-behind roof row; a street or garden lies behind every
    one) `back_storeys` storeys, no higher than before, so the camera hides no more of what lies behind."""
    m = Model(name)
    hw = width * 8 - 3
    F = 20
    B = F - (rows * 16 - 4) + 6
    BF = B + back_rows * 16 + 2                       # the front part's back wall
    back_storeys = storeys - 1 if back_storeys is None else back_storeys
    shadow(m, -hw - 4, hw + 4, B - 4, F + 6)
    t = stone_mass(m, -hw, hw, BF, F, storeys)
    coping(m, -hw, hw, BF, F, t)
    roof_slab(m, -hw, hw, BF, F, t + 1.5)
    if back_rows:
        bt = stone_mass(m, -hw + 2, hw - 2, B, BF, back_storeys, sides='ew')
        coping(m, -hw + 2, hw - 2, B, BF, bt)
        roof_slab(m, -hw + 2, hw - 2, B, BF, bt + 1.5)
    if vent_at: roof_box(m, hw - 12, BF + 12, t + 1.5, 12, 12, 6, K2_ASHLAR, K2_LIGHT, K2_DARK, 8, 3)
    if hut: roof_box(m, -hw + 16, BF + 14, t + 1.5, 14, 12, 12, K2_ASHLAR, K2_LIGHT, K2_DARK, 5, 9)
    if ac: roof_box(m, ac[0], ac[1], t + 1.5, 12, 8, 7, K2_LIGHT, K2_LIGHT, K2_DARK, 9, 4)
    return m

def school2():
    """The Trainer's School, 7x5: two storeys (arched windows over the ashlar ground storey) at the front, the rear
    row (walk-behind roof row; the garden and House 2's door behind) one storey; a raised central bay, 4 units proud,
    over the entrance (the door: dx 8 = the bay's centre), an oriel on the upper storey; a roof unit and a vent."""
    m = stone_block('rus_school', 7, 5, 1, back_rows=1, back_storeys=0, vent_at=True, ac=(-30, -12))
    t = GROUND + STOREY
    bx0, bx1, bz = -8, 24, 24          # (an oriel over the ground storey: the door at dz 22 stays in front of its wall)
    walls3(m, STONE, bx0, bx1, 6, bz, GROUND, t + 10, 0.5, 1.0, 56)
    rect(m, K2_CORNICE, (bx0, GROUND - 3, bz), E, UP, bx1 - bx0, 3, rep=(UW, 3))    # its sill course
    coping(m, bx0, bx1, 6, bz, t + 10)
    roof_slab(m, bx0, bx1, 6, bz, t + 11.5)
    return m

def flat1b():
    """Flat 1, 9x6 (incl. the walk-behind roof row): two storeys over the ashlar ground storey at the front, the rear
    row the ground storey only (a street behind); a roof-access hut, a vent and a roof unit."""
    return stone_block('rus_flat1', 9, 6, 2, back_rows=1, back_storeys=0, vent_at=True, hut=True, ac=(8, -2))

def grey_house2():
    """Grey house, 5x5 (House 1, House 2): a ground storey and one upper storey of kabe_001 windows under a low
    corrugated roof; the rear (walk-behind roof row) keeps the old eave height."""
    m = Model('rus_grey5')
    hw, F, B = 37, 20, -42
    BF = B + 18
    shadow(m, -hw - 4, hw + 4, B - 4, F + 6)
    t = grey_mass(m, -hw, hw, BF, F, 1)
    rect(m, K1_DARK, (-hw, 0, F + 1.0), E, UP, 2 * hw, 1.5, rep=(UW, 1.5))
    gable_roof(m, STRIPES, -hw - 2, hw + 2, BF - 3, F + 3, t - 0.5, t + 7, rep=(UW, 8))
    for x, d, z0 in ((hw, (0, 0, -1), F), (-hw, (0, 0, 1), BF)):
        face(m, K1_GREY, (x, t, z0), d, UP, [(0, 0), (F - BF, 0), ((F - BF) / 2, 7)], rep=(UW, UW))
    bt = grey_mass(m, -hw + 2, hw - 2, B, BF, 0, first=DOOR_WALL, sides='ew')
    gable_roof(m, STRIPES, -hw, hw, B - 3, BF + 2, bt - 0.5, bt + 5, rep=(UW, 8))
    return m

def grey_tower(name, width, rows, storeys, back_rows, back_storeys):
    """Rustboro's tall grey blocks (Flat 2, the annex): storeys of kabe_001 windows, a parapet, a flat roof and a
    corrugated roof house; the rear rows lower (a street runs behind both)."""
    m = Model(name)
    hw, F = width * 8 - 3, 20
    B = F - (rows * 16 - 4) + 6
    BF = B + back_rows * 16 + 2
    shadow(m, -hw - 4, hw + 4, B - 4, F + 8)
    t = grey_mass(m, -hw, hw, BF, F, storeys)
    rect(m, K1_DARK, (-hw, 0, F + 1.0), E, UP, 2 * hw, 1.5, rep=(UW, 1.5))
    coping(m, -hw, hw, BF, F, t, 3, K1_DARK, K1_GREY)
    top(m, K1_GREY, -hw, hw, BF, F, t + 1.5)
    rz0, rz1 = BF + 6, F - 12
    gable_roof(m, STRIPES, -hw * 0.6, hw * 0.6, rz0, rz1, t + 1.5, t + 9, rep=(UW, 8))      # roof house
    for x, d, z0 in ((hw * 0.6, (0, 0, -1), rz1), (-hw * 0.6, (0, 0, 1), rz0)):
        face(m, K1_GREY, (x, t + 1.5, z0), d, UP, [(0, 0), (rz1 - rz0, 0), ((rz1 - rz0) / 2, 7.5)], rep=(UW, UW))
    if back_rows:
        bt = grey_mass(m, -hw + 2, hw - 2, B, BF, back_storeys, sides='ew')
        gable_roof(m, STRIPES, -hw, hw, B - 3, BF + 2, bt - 0.5, bt + 6, rep=(UW, 8))
    return m

def devon2():
    """Devon Corporation (prop at the tower front, as before): tan stone, the wings three storeys of arched windows
    over the ashlar ground storey, the central tower four and a narrower attic storey, the doors under the curved
    canopy; roof units on the wings. Behind it only Sapphire's unreachable grass strip and the river."""
    m = Model('rus_devon')
    F = 4
    FW = F - 16
    B = F - 8 * 16 - 4 + 6
    shadow(m, -84, 84, B - 4, F + 6)
    BB = B + 3 * 16 + 2                 # the last three rows: the old heights (the river and grass strip behind)
    for x0, x1 in ((-78, -33), (33, 78)):
        t = stone_mass(m, x0, x1, BB, FW, 2)
        coping(m, x0, x1, BB, FW, t)
        roof_slab(m, x0, x1, BB, FW, t + 1.5)
        roof_box(m, (x0 + x1) / 2, FW - 24, t + 1.5, 12, 8, 7, K2_LIGHT, K2_LIGHT, K2_DARK, 9, 4)
        bt = stone_mass(m, x0 + 2, x1 - 2, B, BB, 0, sides='ew')
        coping(m, x0 + 2, x1 - 2, B, BB, bt)
        roof_slab(m, x0 + 2, x1 - 2, B, BB, bt + 1.5)
    t = stone_mass(m, -32, 32, BB, F, 3)
    coping(m, -32, 32, BB, F, t)
    roof_slab(m, -32, 32, BB, F, t + 1.5)
    bt = stone_mass(m, -30, 30, B, BB, 1, sides='ew')
    coping(m, -30, 30, B, BB, bt)
    roof_slab(m, -30, 30, B, BB, bt + 1.5)
    walls3(m, STONE, -20, 20, BB + 4, F - 6, t + 1.5, t + 17.5, 0.5, 1.0, 56)              # attic storey
    coping(m, -20, 20, BB + 4, F - 6, t + 17.5)
    roof_slab(m, -20, 20, BB + 4, F - 6, t + 19)
    pc_door_hood(m, K2_CORNICE, K2_LIGHT, 0, F - 4, 31, 34, band_rep=(UW, 3))
    return m

def annex2():
    return grey_tower('rus_annex', 4, 8, 2, back_rows=2, back_storeys=1)

def flat2b():
    """Flat 2, 7x9: three storeys of windows over the ground storey (the door stands over a window), the rear two
    rows one (a street behind)."""
    return grey_tower('rus_flat2', 7, 9, 3, back_rows=2, back_storeys=1)

MODELS_OLD = {
    'grey5': grey5,
    'flat1': lambda: tan_block('rus_flat1', 9, 6, 0, 2, [(-48, 0), (-28, 0), (28, 0), (48, 0), (-48, 1), (-28, 1), (28, 1), (48, 1)], True),
    'school': lambda: tan_block('rus_school', 7, 5, 0, 1, [(-36, 0), (-20, 0), (20, 0), (36, 0)], True),
    'cutter': lambda: tan_block('rus_cutter', 5, 5, 0, 1, [(-22, 0), (22, 0)], True),
    'house3': lambda: tan_block('rus_house3', 6, 5, -8, 1, [(-26, 0), (12, 0), (28, 0)]),
    'flat2': flat2,
    'annex': annex,
    'devon': devon,
    'lamp': lamp,
}
MODELS = {
    'grey5': grey_house2,
    'flat1': flat1b,
    'school': school2,
    'cutter': lambda: stone_block('rus_cutter', 5, 5, 1, back_rows=1, back_storeys=0),
    'house3': lambda: stone_block('rus_house3', 6, 5, 1, back_rows=1, back_storeys=0, vent_at=False, ac=(-20, -8)),
    'flat2': flat2b,
    'annex': annex2,
    'devon': devon2,
    'lamp': lamp,
}
if os.environ.get('HOENN_RUSTBORO_OLD'): MODELS = MODELS_OLD

def main(out):
    townlook_textures()
    write(out, {k: f() for k, f in MODELS.items()}, SOURCES)

if __name__ == '__main__':
    main(sys.argv[1])
