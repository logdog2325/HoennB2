"""Lavaridge Town's buildings: Sapphire's shapes and colours, Black 2 textures (group towns3, res 363).

    python3 models_lavaridge.py ../work/buildings/lavaridge

Writes house.dae (res 363: the Herb Shop and the house next to it, which Sapphire draws as two identical red-roofed
4x4 houses side by side), the texture images it uses, palettes.txt and textures.txt. The Pokémon Center, Mart and
Gym are shared models (res 0, 3, 320).

Sapphire footprint (data/plans/LavaridgeTown.json): the two houses form one 8x4 block (x 11-18, rows 12-15, doors at
(12,15) and (16,15)); each house is 4x4 with its door in column 1. Origin = one house's footprint centre on the
ground, +z = front; front wall at z = +20 (4 units into the door tile).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, rect, decal, box_walls, gable_roof, face, shadow, DOOR_WALL
from models_fallarbor import write_models

UP, E = (0, 1, 0), (1, 0, 0)
F = (64, 64)
# pack 53 (Floccesy Ranch barn): red corrugated roof (ridges parallel to the eave, like Sapphire's Lavaridge roofs),
# tan board wall with dark wooden posts and beam (Sapphire: tan walls in a dark timber frame), light boards
RED = Region('d22_farm01_1', F, 0, 0, 64, 36)
TAN = Region('d22_farm01_1', F, 5, 39, 59, 57)
POST = Region('d22_farm01_1', F, 0, 37, 4, 58)
BEAM = Region('d22_farm01_1', F, 4, 36, 60, 39)
BOARD = Region('d22_farm01_1', F, 0, 58, 64, 64)
# pack 57 / pack 0: framed window and glass (as Littleroot's and Oldale's houses)
WINDOW = Region('c14_h1_body', F, 38, 32, 62, 46)
MADO = Region('h_mado', (16, 16), 0, 0, 16, 16)

SOURCES = {'d22_farm01_1': 'ext53', 'c14_h1_body': 'ext57', 'h_mado': 'ext00', 'h_kage': 'ext00'}

def house():
    """Lavaridge house: tan board walls in a dark timber frame, red corrugated gable roof with a light fascia, door
    left of centre (column 1, door model drawn by the game), framed window right. Walls 40 high and the front eave 5
    units out: the eave and its fascia board were at 29.5-32, 7 units out, over the door's top (y 32) (door_fix)."""
    m = Model('lv_house')
    shadow(m, -34, 34, -26, 28)
    X, Z0, Z1, H = 28, -18, 20, DOOR_WALL + 2
    box_walls(m, -X, X, Z0, Z1, 0, H, TAN, rep=(54, H / 2), sides='sew')   # (no back wall: never seen)
    rect(m, BOARD, (-X, 0, Z1 + 1.0), E, UP, 2 * X, 3, rep=(32, 3))
    rect(m, BEAM, (-X, H - 3, Z1 + 1.0), E, UP, 2 * X, 3, rep=(56, 3))
    for x in (-X, 1.5, X - 3):                       # timber posts: corners, between door and window
        rect(m, POST, (x, 0, Z1 + 1.5), E, UP, 3, H, rep=(3, H))
    for z in (Z1 - 3, Z0):                            # side posts at the corners
        rect(m, POST, (X + 1.0, 0, z + 3), (0, 0, -1), UP, 3, H, rep=(3, H))
        rect(m, POST, (-X - 1.0, 0, z), (0, 0, 1), UP, 3, H, rep=(3, H))
    decal(m, MADO, (14, 18, Z1 + 1.0), E, UP, 18, 10)
    decal(m, WINDOW, (14, 18, Z1 + 2.0), E, UP, 20, 12)
    tri = [(0, 0), (Z1 - Z0, 0), ((Z1 - Z0) / 2, 14)]
    face(m, TAN, (X, H, Z1), (0, 0, -1), UP, tri, rep=(54, 17))     # gable ends
    face(m, TAN, (-X, H, Z0), (0, 0, 1), UP, tri, rep=(54, 17))
    gable_roof(m, RED, -31, 31, -25, 25, H - 2, H + 16, rep=(64, 30))
    rect(m, BOARD, (-31, H - 4.5, 25.1), E, UP, 62, 2.5, rep=(32, 2.5))  # light fascia board along the front eave
    return m

def models():
    return {'house': house()}

if __name__ == '__main__':
    write_models(sys.argv[1], models(), SOURCES)
