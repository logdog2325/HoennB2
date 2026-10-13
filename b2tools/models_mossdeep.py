"""Mossdeep City's buildings (group towns4): Sapphire's shapes and colours, Black 2 textures.

    python3 models_mossdeep.py ../work/buildings/mossdeep

Writes house.dae (res 386: Mossdeep's stone house with a two-tier kawara roof, 4 wide: Houses 1-4 and Steven's
house), gamecorner.dae (387: the same house 5 wide and one row deeper, Sapphire's MOSSDEEP_CITY_GAME_CORNER_1F) and
space.dae (388: Mossdeep Space Center), plus texture images, palettes.txt, textures.txt. The Gym is the shared Gen 3
Gym (res 320, group towns1): Sapphire's Mossdeep Gym uses exactly Petalburg's gym metatiles (data/plans).

Footprints are Sapphire's (data/plans/MossdeepCity.json). Origin = footprint centre on the ground, +z = front; the
front wall F stands 4 units into the door tile. Helpers: models_lilycove.py.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, rect, decal, box_walls, face, slope, gable_roof, skirt_roof, shadow, DOOR_WALL, pc_door_hood
from models_lilycove import (UP, E, UW, GLASS, CREST, GREY, WHITE, PURE, DARK, wrect, wface, flat, walls, polygon,
                             wfrustum, write_models)

# pack 48 (Abundant Shrine): Japanese roof tiles (rows of round tiles with their end caps), slate, white plaster
KAWARA = Region('en_sekia1', (64, 64), 0, 0, 32, 42)            # tile rows down the slope, end caps at the eave
SLATE = Region('en_sekia1', (64, 64), 33, 1, 39, 40)            # dark slate blue (window)
PLASTER = Region('en_sekia1', (64, 64), 42, 14, 60, 30)         # white plaster: the ridge band and window sills
PALE = Region('en_sekia1', (64, 64), 41, 1, 63, 11)             # pale grey band under the upper roof
# pack 10 (Icirrus): light beige stone wall, Sapphire's Mossdeep walls
STONE = Region('c7h2_1', (32, 64), 0, 0, 32, 29)
# pack 8 (Driftveil): green glass office front; its window grid = the Space Center's walls, its framed pane = the roof
WINGRID = Region('c5_rb_03_w1', (32, 64), 0, 33, 32, 64)
ROOFPANE = Region('c5_rb_03_w1', (32, 64), 0, 0, 32, 32)
FRAME = Region('c5_rb_03_w1', (32, 64), 2, 34, 30, 36)          # dark green frame: base and floor bands

def stone_house(width, door_dx, windows, depth_rows=4):
    """Mossdeep house: beige stone walls, dark window with a white sill, two-tier roof of brown kawara tiles (a
    skirt roof all round, an upper gable with a white ridge band over a pale band). Game door 260 (orange)."""
    m = Model(f'md_house{width}')
    hw = width * 8 - 4
    F = 20; B = (F - 4) - (depth_rows - 1) * 16 + 10      # back wall 10 units in front of the footprint's north edge
    eave = DOOR_WALL                                         # the game's door 260 reaches y 32 (34 put the skirt
                                                             # roof's edge at 32, 6 out, over it; door_fix)
    shadow(m, -hw - 6, hw + 6, B - 6, F + 8)
    box_walls(m, -hw, hw, B, F, 0, eave, STONE, rep=(36, 34), sides='sew')
    for x in windows:
        decal(m, SLATE, (x, 19, F + 1.0), E, UP, 16, 10)
        decal(m, PLASTER, (x, 13, F + 1.5), E, UP, 18, 2)
    # skirt roof all round, then the upper storey and its gable roof
    ix0, ix1, iz0, iz1 = -hw + 8, hw - 8, B + 8, F - 12
    skirt_roof(m, KAWARA, (-hw - 5, hw + 5, B - 5, F + 6), (ix0, ix1, iz0, iz1), eave - 2, eave + 10, rep=(24, 24))
    box_walls(m, ix0, ix1, iz0, iz1, eave + 8, eave + 16, PALE, rep=(UW, 10), sides='sew')
    zc, top = (iz0 + iz1) / 2, eave + 30
    face(m, PALE, (ix1, eave + 16, iz1), (0, 0, -1), UP, [(0, 0), (iz1 - iz0, 0), ((iz1 - iz0) / 2, top - 2 - eave - 16)], rep=(UW, 10))
    face(m, PALE, (ix0, eave + 16, iz0), (0, 0, 1), UP, [(0, 0), (iz1 - iz0, 0), ((iz1 - iz0) / 2, top - 2 - eave - 16)], rep=(UW, 10))
    gable_roof(m, KAWARA, ix0 - 4, ix1 + 4, iz0 - 4, iz1 + 4, eave + 14, top, rep=(24, 24))
    k = (top - eave - 14) / (iz1 + 4 - zc)
    for sgn in (1, -1):                                             # white ridge band
        z1 = zc + sgn * 4; y1 = top - 4 * k
        a, b = (ix0 - 4, y1 + 0.8, z1), (ix1 + 4, y1 + 0.8, z1)
        c, d = (ix1 + 4, top + 0.8, zc), (ix0 - 4, top + 0.8, zc)
        if sgn > 0: slope(m, PLASTER, a, b, c, d, rep=(18, 4))
        else: slope(m, PLASTER, b, a, d, c, rep=(18, 4))
    return m

def dish(m, x, z, y, r):
    """Satellite dish on the roof: a shallow white bowl on a short grey stand, tilted towards the sky."""
    box_walls(m, x - 2, x + 2, z - 2, z + 2, y, y + 6, GREY, rep=(UW, 6))
    outer = polygon(x, z, r, 6); inner = polygon(x, z, r * 0.3, 6)
    ring_up = [(px, pz) for px, pz in outer]
    from models_lilycove import ring
    ring(m, PURE, ring_up, inner, y + 10, y + 6, rep=(UW, UW))      # bowl: rim high, centre low (inside faces up)
    flat(m, PURE, inner, y + 6.2, rep=(UW, UW))

def space_center():
    """Mossdeep Space Center (9 wide, rows 6-13, door in the middle): a tall block of green glass in a grid of dark
    green frames, a projecting glass stair tower in the middle over the entrance (game door 93), a green pane roof
    with two satellite dishes."""
    m = Model('md_space')
    hw, F, B, H = 68, 20, -86, 92
    shadow(m, -hw - 6, hw + 6, B - 6, F + 8)
    box_walls(m, -hw, hw, B, F, 0, H, WINGRID, rep=(34, 46), sides='sew')
    for y in (0, 46, H - 4):                                        # floor bands
        rect(m, FRAME, (-hw, y, F + 1.0), E, UP, 2 * hw, 4, rep=(UW, 4))
        rect(m, FRAME, (hw + 1.0, y, F), (0, 0, -1), UP, F - B, 4, rep=(UW, 4))
        rect(m, FRAME, (-hw - 1.0, y, B), (0, 0, 1), UP, F - B, 4, rep=(UW, 4))
    # glass stair tower: x -14..14, 4 units proud of the front, full height
    T = F + 4
    rect(m, GLASS, (-14, 34, T), E, UP, 28, H - 30, rep=(14, 20))
    rect(m, GLASS, (14, 34, T), (0, 0, -1), UP, 4, H - 30, rep=(4, 16))
    rect(m, GLASS, (-14, 34, F), (0, 0, 1), UP, 4, H - 30, rep=(4, 16))
    flat(m, GREY, [(-14, T), (14, T), (14, F), (-14, F)], H + 4, rep=(40, 10))
    # entrance: grey frame around the door, crest above it; the game's curved sliding door (door_pc 93, origin z 20:
    # its arc's ends on the frame's front) under a grey canopy following its curve. The door stood 10 units out of the
    # frame with its top in front of the lintel (door_fix 2026-10-11)
    rect(m, GREY, (-18, 0, T), E, UP, 4, 32, rep=(4, 32)); rect(m, GREY, (14, 0, T), E, UP, 4, 32, rep=(4, 32))
    rect(m, GREY, (-18, 30, T), E, UP, 36, 6, rep=(36, 4))
    rect(m, GREY, (18, 0, T), (0, 0, -1), UP, 4, 36, rep=(4, 34)); rect(m, GREY, (-18, 0, F), (0, 0, 1), UP, 4, 36, rep=(4, 34))
    flat(m, GREY, [(-18, T), (18, T), (18, F), (-18, F)], 36, rep=(36, 4))
    pc_door_hood(m, GREY, GREY, 0, T - 4, 31, 35, band_rep=(36, 4))
    # roof: green panes, grey rim, two dishes
    flat(m, ROOFPANE, [(-hw, F), (hw, F), (hw, B), (-hw, B)], H, rep=(46, 54))
    rect(m, GREY, (-hw - 1, H - 2, F + 1.0), E, UP, 2 * hw + 2, 4, rep=(40, 4))
    for x in (-40, 40):
        dish(m, x, -62, H, 14)
    return m

def models():
    return {'house': stone_house(4, -8, (14,)), 'gamecorner': stone_house(5, -16, (6, 24), depth_rows=5),
            'space': space_center()}

if __name__ == '__main__':
    write_models(sys.argv[1], models())
