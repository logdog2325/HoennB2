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
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, rect, decal, box_walls, gable_roof, face, slope, shadow, DOOR_WALL, pc_door_hood
from models_petalburg import write, wface, wgable, UP, E, CREST, UW

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

MODELS = {
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

def main(out):
    write(out, {k: f() for k, f in MODELS.items()}, SOURCES)

if __name__ == '__main__':
    main(sys.argv[1])
