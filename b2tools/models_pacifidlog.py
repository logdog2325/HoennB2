"""Pacifidlog Town's buildings (group towns4): Sapphire's shapes and colours, Black 2 textures.

    python3 models_pacifidlog.py ../work/buildings/pacifidlog

Writes hut.dae (res 389: Pacifidlog's round log hut with a layered green thatch roof, 3 wide, door in the middle: all
five houses) plus texture images, palettes.txt, textures.txt. The Pokémon Center is the shared res 0. The log rafts and
bridges around the huts are terrain (plan classes cliff_top / bridge), not buildings.

Footprints are Sapphire's (data/plans/PacifidlogTown.json): 3 wide, 2 solid rows plus a walk-behind roof row.
Origin = footprint centre on the ground, +z = front; the front face F = 20 stands 4 units into the door tile.
Helpers: models_lilycove.py.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, rect, face, shadow, DOOR_WALL
from models_lilycove import (UP, E, UW, LATTICE, POST, SHINGLE_LT, BEAM, flat, walls, polygon, ring, wfrustum,
                             write_models)

def hut():
    """Octagonal hut of dark vertical planks with wooden corner posts and a beam under the eave, a roof of three
    scalloped layers of green leaves (pack 0's plant_tex4: Sapphire's olive thatch is layered the same way) and a
    small cream knob on top. Game door 260 in the front face. Walls DOOR_WALL (38) high: at 34 the thatch's lowest
    layer started at 30, 8 units out, and hid the door's top third (door_fix 2026-10-11)."""
    m = Model('pa_hut')
    zc, ap = -1, 21                                   # centre and apothem: front face at z = 20
    R = ap / math.cos(math.pi / 8)
    shadow(m, -26, 26, zc - 26, zc + 28)
    wall = polygon(0, zc, R, 8)
    G = DOOR_WALL
    walls(m, LATTICE, wall, 0, G, rep=(18, 34))            # the game's door 260 reaches y 32
    walls(m, BEAM, polygon(0, zc, R + 0.6, 8), G - 3, G, rep=(UW, 3))
    for x, z in wall:                                 # corner posts
        a = math.atan2(z - zc, x)
        ox, oz = math.cos(a) * 0.8, math.sin(a) * 0.8
        tx, tz = math.sin(a), -math.cos(a)            # tangent (u x up = outward normal)
        rect(m, POST, (x + ox - tx * 1.5, 0, z + oz - tz * 1.5), (tx, 0, tz), UP, 3, G, rep=(3, UW))
    # thatch: three overlapping layers, then a small cap and the knob
    d = G - 30
    layers = [(32, 30, 22, 42), (25, 39, 14, 51), (17, 48, 6, 60)]
    for r0, y0, r1, y1 in layers:
        wfrustum(m, 'plant_tex4', polygon(0, zc, r0, 8), polygon(0, zc, r1, 8), y0 + d, y1 + d, rep_u=24)
    wfrustum(m, 'plant_tex4', polygon(0, zc, 7, 8), polygon(0, zc, 0.5, 8), 58 + d, 63 + d, rep_u=12)
    knob = polygon(0, zc, 3.5, 8)
    walls(m, SHINGLE_LT, knob, 62 + d, 67 + d, rep=(8, 8))
    flat(m, SHINGLE_LT, knob, 67 + d, rep=(8, 8))
    return m

def models():
    return {'hut': hut()}

if __name__ == '__main__':
    write_models(sys.argv[1], models())
