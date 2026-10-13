"""Verdanturf Town's buildings: Sapphire's shapes and colours, Black 2 textures (group towns2, res 352-353).

    python3 models_verdanturf.py ../work/buildings/verdanturf

Sapphire footprints (data/plans/VerdanturfTown.json): the Friendship Rater's house and the house in the east are
4 wide (rows 12-14 / 13-15 + roof row, door in column 1), Wanda's house is 5 wide (rows 12-14 + roof row, door in the
middle). All three have Sapphire's Verdanturf look: a big flat green roof slab over a yellow fascia, beige walls
with wooden pillars, windows beside a pale blue door. The Contest Hall is group towns3's res 362, the Pokemon
Center / Mart the shared res 0 / res 3.
Origin = footprint centre on the ground, +z = front; front walls at z = +20 (data/towns/VerdanturfTown.json 'front').
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import shadow, DOOR_WALL
from models_slateport import (UP, E, BEIGE, POST, GOLD, GOLD_REP, MINT, rect, box_walls, window, walls, flat, frustum,
                              rectangle, write_models)

def flat_roof_house(name, X, windows, pillars):
    """Beige walls (front at z = 20, back at -16), wooden pillars, yellow fascia, flat mint-green roof slab."""
    m = Model(name)
    Z0, Z1, H = -16, 20, DOOR_WALL           # (33: the fascia at 32, 6 units out, hid the door's top; door_fix)
    shadow(m, -X - 6, X + 6, -24, 30)
    box_walls(m, -X, X, Z0, Z1, 0, H, BEIGE, rep=(X, 16.5))
    for wx in windows: window(m, wx, 17, Z1)
    for x in pillars:
        rect(m, POST, (x - 2, 0, Z1 + 0.25), E, UP, 4, H, rep=(4, H))
    out = rectangle(-X - 4, X + 4, Z0 - 4, Z1 + 6)
    walls(m, GOLD, out, H - 1, H + 5, rep=GOLD_REP)                      # yellow fascia (Sapphire's)
    walls(m, MINT, out, H + 5, H + 8, rep=(32, 32))                      # slab edge
    inner = rectangle(-X - 1, X + 1, Z0 - 1, Z1 + 3)
    frustum(m, MINT, out, inner, H + 8, H + 10, rep=(32, 32))
    flat(m, MINT, inner, H + 10, rep=(32, 32))
    return m

def house():
    """4-wide house (Friendship Rater's, and the house in the east): door in column 1, window right (res 352)."""
    return flat_roof_house('vt_house', 30, windows=[14], pillars=(-28, 1, 28))

def wanda():
    """Wanda's house (5 wide): door in the middle, a window either side (res 353)."""
    return flat_roof_house('vt_wanda', 38, windows=[-22, 22], pillars=(-36, -11, 11, 36))

def models():
    return {'house': house(), 'wanda': wanda()}

if __name__ == '__main__':
    write_models(sys.argv[1], models())
