"""Mauville City's buildings: Sapphire's shapes and colours, Black 2 textures (group towns2, res 348-351).

    python3 models_mauville.py ../work/buildings/mauville

Sapphire footprints (data/plans/MauvilleCity.json):
  bikeshop   5 wide, rows 2-5, door in column 1 (Rydel's Cycles): pink gable roof, yellow siding, wooden pillars
  gamecorner 7 wide, rows 11-13 + roof row, door in the middle: pink barrel roof with two rows of small windows, glass
             front, pink porch round the door
  house1     9 wide, rows 12-14 (+ row 15 for the right part) + roof row: Mauville house 1 (5 wide, grey walls,
             pink roof, door in column 1) with the door-less annex east of it (4 wide, one row deeper, yellow walls,
             flat grey roof with vents)
  house      4 wide, rows 12-14 + roof row, door in column 1 (house 2, beside the Mart)
The Gym is group towns1's generic res 320, the Pokemon Center / Mart the shared res 0 / res 3.
Origin = footprint centre on the ground, +z = front; front walls at z = +20 (data/towns/MauvilleCity.json 'front').
Geometry helpers and textures: models_slateport.py.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import shadow, DOOR_WALL, pc_door_hood
from models_slateport import (UP, E, N, PINK, GOLD, GOLD_REP, GREY, POST, BEAM, GLASS, CREST, VENT, TRIM, face, rect,
                              decal, window, walls, flat, rectangle, box_walls, gable_house, gable_ends, gable_roof,
                              barrel, write_models)

def bikeshop():
    """Rydel's Cycles (5x4): pink gable roof, yellow siding, wooden pillars, window right of the door (res 348)."""
    m = gable_house('mv_bikeshop', PINK, GOLD, -38, 38, -32, 20, DOOR_WALL, windows=[(16, 19)], roof_x=(-41, 41),
                    roof_rep=(16, None), ridge=18, wall_rep=GOLD_REP)
    for x in (0, 30):
        rect(m, POST, (x - 1.5, 0, 20.25), E, UP, 3, DOOR_WALL, rep=(3, DOOR_WALL))
    return m

def gamecorner():
    """Game Corner (7x3): glass front with a pink porch round the door, pink barrel roof with two rows of small
    windows along the top (res 349)."""
    m = Model('mv_gamecorner')
    X, Z0, Z1, H = 54, -16, 20, 32
    shadow(m, -60, 60, -24, 30)
    rect(m, PINK, (X, 0, Z1), (0, 0, -1), UP, Z1 - Z0, H, rep=(16, 64))   # east side
    rect(m, PINK, (-X, 0, Z0), (0, 0, 1), UP, Z1 - Z0, H, rep=(16, 64))   # west side
    rect(m, PINK, (-X, 0, Z1), E, UP, 2 * X, 4, rep=(16, 64))          # front base
    rect(m, PINK, (-X, H - 4, Z1), E, UP, 2 * X, 4, rep=(16, 64))      # front lintel
    for x0, x1 in ((-X, -16), (16, X)):                                # glass either side of the entrance
        rect(m, GLASS, (x0, 4, Z1), E, UP, x1 - x0, H - 8, rep=(19, 24))
        for x in (x0 + (x1 - x0) / 3, x0 + 2 * (x1 - x0) / 3):
            rect(m, BEAM, (x - 1, 4, Z1 + 0.2), E, UP, 2, H - 8, rep=(2, H - 8))
    rect(m, PINK, (-16, 4, Z1), E, UP, 32, H - 8, rep=(16, 64))
    # porch: two pink pillars and a band standing proud of the front, Poke Ball emblem on it
    for side in (-1, 1):
        x = side * 15
        walls(m, PINK, rectangle(x - 2, x + 2, Z1, Z1 + 4), 0, H + 4, rep=(4, 64))
    rect(m, PINK, (-17, H, Z1 + 4), E, UP, 34, 8, rep=(16, 64))
    face(m, PINK, (-17, H + 8, Z1 + 4), E, (0, 0.5, -0.87), [(0, 0), (34, 0), (34, 5), (0, 5)], rep=(16, 64))
    decal(m, CREST, (0, H + 4, Z1 + 4.3), E, UP, 8, 8)
    # canopy over the game's curved sliding door (door_pc 93, its arc's ends on the porch front at z 24): the door
    # stood 10 units out in front of the porch band with nothing over it (door_fix 2026-10-11)
    pc_door_hood(m, PINK, PINK, 0, Z1, H - 1, H + 2, band_rep=(16, 64))
    # barrel roof over the whole box, then a row of small windows near the crest
    z0, z1, h = Z0 - 6, Z1 + 4, 22
    barrel(m, PINK, -X - 3, X + 3, z0, z1, H - 2, h, segs=6)
    zc, r, t = (z0 + z1) / 2, (z1 - z0) / 2, math.radians(62)
    pz, py = zc + r * math.cos(t), H - 2 + h * math.sin(t)
    tz, ty = -r * math.sin(t), h * math.cos(t)
    ln = math.hypot(tz, ty); tz, ty = tz / ln, ty / ln
    nz, ny = -ty, tz
    if nz < 0: nz, ny = -nz, -ny
    for deg in (62, 38):                                               # two rows, as Sapphire's
        t = math.radians(deg)
        pz, py = zc + r * math.cos(t), H - 2 + h * math.sin(t)
        tz, ty = -r * math.sin(t), h * math.cos(t)
        ln = math.hypot(tz, ty); tz, ty = tz / ln, ty / ln
        nz, ny = -ty, tz
        if nz < 0: nz, ny = -nz, -ny
        for x in range(-44, 45, 11):
            decal(m, GLASS, (x, py + ny * 0.5, pz + nz * 0.5), E, (0, ty, tz), 7, 5)
    return m

def house1():
    """Mauville house 1 with its annex (9 wide): left part grey walls, pink gable roof, door in column 1, window;
    right part (no door) one row deeper, yellow walls, flat grey roof with vents (res 350)."""
    m = Model('mv_house1')
    H = DOOR_WALL                    # (34: the eave at 32, at the door's top; door_fix 2026-10-11)
    shadow(m, -76, 74, -24, 44)
    # left: the house (tiles 31-35 -> x -72..+8)
    rect(m, GREY, (-70, 0, -16), (0, 0, 1), UP, 36, H, rep=(36, 17))      # west side
    rect(m, GREY, (-70, 0, 20), E, UP, 76, H, rep=(38, 17))              # front
    window(m, -16, 19, 20)
    for x in (-68.5, -32, 4.5):
        rect(m, POST, (x - 1.5, 0, 20.25), E, UP, 3, H, rep=(3, H))
    gable_ends(m, GREY, -70, 6, -16, 20, H, 16 * 36 / 44, (36, 17))
    gable_roof(m, PINK, -73, 7, -20, 24, H - 2, H + 14, rep=(16, None))
    # right: the annex (tiles 36-39 -> x +8..+72), front one row further south
    box_walls(m, 7, 70, -16, 36, 0, H + 2, GOLD, rep=GOLD_REP)
    rect(m, TRIM, (7, 0, 36.2), E, UP, 63, 3, rep=(63, 3))
    for wx in (32, 48): window(m, wx, 19, 36, 14, 12)
    out = rectangle(5, 72, -18, 38)
    walls(m, GREY, out, H + 1, H + 5, rep=(64, 4))
    flat(m, GREY, out, H + 5, rep=(34, 28))
    for vx, vz in ((24, 10), (52, 10), (24, -6), (52, -6)):          # Sapphire's grid of roof panels
        face(m, VENT, (vx - 11, H + 5.3, vz + 6), E, N, [(0, 0), (22, 0), (22, 12), (0, 12)], rep=(22, 12))
    return m

def house():
    """Mauville house 2 (4 wide): pink gable roof, yellow siding, door in column 1, window right (res 351)."""
    return gable_house('mv_house', PINK, GOLD, -30, 30, -16, 20, DOOR_WALL, windows=[(14, 19)], roof_x=(-33, 33),
                       roof_rep=(16, None), wall_rep=GOLD_REP)

def models():
    return {'bikeshop': bikeshop(), 'gamecorner': gamecorner(), 'house1': house1(), 'house': house()}

if __name__ == '__main__':
    write_models(sys.argv[1], models())
