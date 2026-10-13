"""Dewford Town's buildings: Sapphire's shapes, Black 2 textures.

    python3 models_dewford.py ../work/buildings/dewford

Writes hall.dae (res 330, Dewford Hall, 5x4, door in the middle) and house.dae (res 331, the island houses, 4x4,
door half a tile left of centre): white plaster walls between wooden posts, a blue tiled gable roof with deep eaves
and a dark ridge beam, a window right of the door (Sapphire's Dewford tileset). The Gym is the generic res 320
(models_petalburg.py), the Pokémon Center res 0. Origin = footprint centre on the ground, +z = front; front wall 4
units into the door tile.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, rect, decal, box_walls, gable_roof, face, slope, shadow, DOOR_WALL
from models_petalburg import write, window, wgable, wface, UP, E, POST, BASE, BEAM, UW

PLASTER = Region('c14_h1_body', (64, 64), 0, 30, 14, 56)       # white boards (Humilau, as Littleroot)
KAWARA = Region('nsyane', (16, 32), 0, 0, 16, 32)              # blue roof tiles (Virbank's school, pack 54)
SOURCES = {'c14_h1_body': 'ext57', 'h_mado': 'ext00', 'h_kage': 'ext00', 'nsyane': 'ext54'}

def house(width, door_dx, windows, name):
    m = Model(name)
    hw = width * 8 - 4
    F, B = 20, -22
    eave, rise = DOOR_WALL + 1, 13     # deep eaves 3 units under the wall top: they must clear the door model (236,
                                       # y 33); with eave 27 they came down to 24 (door_fix 2026-10-11)
    shadow(m, -hw - 7, hw + 7, B - 7, F + 9)
    box_walls(m, -hw, hw, B, F, 0, eave, PLASTER, rep=(UW, 26), sides='sew')
    rect(m, BASE, (-hw, 0, F + 1.0), E, UP, 2 * hw, 3, rep=(UW, 3))
    rect(m, BEAM, (-hw, eave - 4, F + 1.0), E, UP, 2 * hw, 4, rep=(UW, 4))
    for x in (-hw + 1.5, door_dx - 10, door_dx + 10, hw - 1.5):
        rect(m, POST, (x - 1.5, 0, F + 2.0), E, UP, 3, eave, rep=(3, 32))
    for x in windows:
        window(m, x, 18, F, 16, 10)
    # gable ends: plaster triangles with a dark beam across
    zc = (F + B) / 2
    for x, d, z0 in ((hw, (0, 0, -1), F), (-hw, (0, 0, 1), B)):
        face(m, PLASTER, (x, eave, z0), d, UP, [(0, 0), (F - B, 0), ((F - B) / 2, rise)], rep=(UW, 26))
    k = rise / (F - zc)
    ox, oz = hw + 5, 5                 # deep eaves
    wgable(m, 'nsyane', -ox, ox, B - oz, F + oz, eave - oz * k, eave + rise, rep=(16, 32))
    # ridge beam (dark wood) along the top
    yr = eave + rise
    box_walls(m, -ox - 1, ox + 1, zc - 2, zc + 2, yr - 1, yr + 2.5, BEAM, rep=(UW, 4), sides='nsew')
    face(m, BEAM, (0, yr + 2.5, 0), E, (0, 0, -1), [(-ox - 1, -(zc + 2)), (ox + 1, -(zc + 2)), (ox + 1, -(zc - 2)), (-ox - 1, -(zc - 2))], rep=(UW, 4))
    return m

MODELS = {'hall': lambda: house(5, 0, (21,), 'dew_hall'), 'house': lambda: house(4, -8, (13,), 'dew_house')}

def main(out):
    write(out, {k: f() for k, f in MODELS.items()}, SOURCES)

if __name__ == '__main__':
    main(sys.argv[1])
