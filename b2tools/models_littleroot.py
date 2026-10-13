"""Littleroot Town's buildings: Sapphire's shapes and layout, Black 2 textures.

    python3 models_littleroot.py ../work/buildings/littleroot

Writes house_l.dae (Brendan's, door right of centre), house_r.dae (May's, mirrored), lab.dae, the texture images they
use (copied from the game's own building texture sets in work/tex/extNN), palettes.txt, and textures.txt (which
texture comes from which set, for the area's building texture file).

Sizes come from Sapphire's footprints (notes/ASSET_INVENTORY.md): houses 5x4 tiles, lab 7x4 tiles. Origin = centre of
the footprint on the ground; +z is the front (south).
"""
import os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exterior_layers import separate
from dae import Model
from buildings import Region, rect, decal, box_walls, hip_roof, skirt_roof, gable_roof, face, shadow, DOOR_WALL, cull_unseen

TEX = os.path.join(HERE, '..', 'work', 'tex')
H57 = (64, 64)
# Humilau City (pack 57): Japanese-style wooden houses, the closest Gen 5 match to Littleroot's houses
SHINGLE = Region('c14_h2_yane', H57, 0, 16, 16, 32)      # tan roof shingles
PLASTER = Region('c14_h1_body', H57, 0, 30, 14, 56)      # white boards
BEAM = Region('c14_h1_body', H57, 36, 20, 64, 28)        # dark wood band
POST = Region('c14_h1_body', H57, 14, 24, 17, 56)        # wooden post
WINDOW = Region('c14_h1_body', H57, 38, 32, 62, 46)      # framed window, glass is transparent
BASE = Region('c14_h1_body', H57, 36, 56, 64, 64)        # orange skirting
VENT = Region('c14_h1_body', H57, 0, 24, 14, 30)         # light grey bands
# pack 0 (Nuvema): glass and shadow; pack 2: green roof tiles for the lab
GLASS = Region('h_mado', (16, 16), 0, 0, 16, 16)
GREEN = Region('c4m_yane_001', (32, 64), 0, 0, 32, 64)

SOURCES = {'c14_h2_yane': 'ext57', 'c14_h1_body': 'ext57', 'h_mado': 'ext00', 'h_kage': 'ext00', 'c4m_yane_001': 'ext02'}
UP, E, S = (0, 1, 0), (1, 0, 0), (0, 0, 1)

def window(m, x, y, z):
    decal(m, GLASS, (x, y, z + 1.0), E, UP, 20, 11)      # 1 and 2 units out: Black 2's windows stand ~1.5 out of
    decal(m, WINDOW, (x, y, z + 2.0), E, UP, 22, 13)     # the wall; nearer layers flicker on hardware/melonDS

def house(door_dx):
    """Littleroot house. door_dx = door centre relative to the footprint centre (+16 left house, -16 right house).
    The ground floor is DOOR_WALL (38) high: Black 2's door model (164) reaches y 32 and the skirt roof must start
    above it (it started at 28: the door stood in the roof; door_fix 2026-10-11)."""
    m = Model('lr_house')
    G = DOOR_WALL                        # ground floor wall height
    shadow(m, -42, 42, -34, 36)
    # ground floor
    box_walls(m, -36, 36, -26, 26, 0, G, PLASTER, rep=(14, 26), sides='sew')   # (no back walls: the camera never
                                                                                 # sees them; pack 0 heap)
    rect(m, BASE, (-36, 0, 26.2), E, UP, 72, 4, rep=(28, 4))
    rect(m, BEAM, (-36, G - 4, 26.2), E, UP, 72, 4, rep=(28, 4))
    for x in (-35, door_dx - 11, door_dx + 11, 35):
        rect(m, POST, (x - 1.5, 0, 26.25), E, UP, 3, G, rep=(3, 32))
    window(m, -door_dx * 0.9, 19, 26)
    # lower roof (wide skirt) and upper floor
    skirt_roof(m, SHINGLE, (-42, 42, -32, 32), (-26, 26, -16, 16), G - 2, G + 10, rep=(16, 16))
    box_walls(m, -26, 26, -16, 16, G + 8, G + 22, PLASTER, rep=(14, 26), sides='sew')
    rect(m, BEAM, (-26, G + 19, 16.2), E, UP, 52, 3, rep=(28, 3))
    # upper roof
    hip_roof(m, SHINGLE, -32, 32, -22, 22, G + 20, -12, 12, 0, G + 36, rep=(16, 16))
    return m

def lab():
    """Prof. Birch's lab: long gable roof with a rooftop vent, two windows left of the door. Walls DOOR_WALL (38) high
    so the roof's eave clears Black 2's door model (165, y 33); it was at 28 (door_fix 2026-10-11)."""
    m = Model('lr_lab')
    G = DOOR_WALL
    shadow(m, -58, 58, -34, 36)
    box_walls(m, -52, 52, -26, 26, 0, G, PLASTER, rep=(14, 26), sides='sew')   # (no back wall: never seen)
    rect(m, BASE, (-52, 0, 26.2), E, UP, 104, 4, rep=(28, 4))
    rect(m, BEAM, (-52, G - 4, 26.2), E, UP, 104, 4, rep=(28, 4))
    for x in (-51, 5, 27, 51):
        rect(m, POST, (x - 1.5, 0, 26.25), E, UP, 3, G, rep=(3, 32))
    for x in (-34, -12):
        window(m, x, 19, 26)
    # gable ends (plaster triangles above the side walls)
    face(m, PLASTER, (52, G, 26), (0, 0, -1), UP, [(0, 0), (52, 0), (26, 22)], rep=(14, 26))
    face(m, PLASTER, (-52, G, -26), (0, 0, 1), UP, [(0, 0), (52, 0), (26, 22)], rep=(14, 26))
    gable_roof(m, GREEN, -58, 58, -32, 32, G - 2, G + 24, rep=(32, 64))
    # rooftop vent (Sapphire's grey box on the roof, front-left)
    box_walls(m, -36, -20, -10, 4, G + 14, G + 28, VENT, rep=(14, 6))
    face(m, VENT, (-36, G + 28, 4), E, (0, 0, -1), [(0, 0), (16, 0), (16, 14), (0, 14)], rep=(14, 6))
    return m

def main(out):
    os.makedirs(out, exist_ok=True)
    models = {'house_l': house(16), 'house_r': house(-16), 'lab': lab()}
    used = set()
    for name, m in models.items():
        separate(m)        # layers >= 1 unit apart (melonDS flicker; b2tools/exterior_layers.py)
        cull_unseen(m)     # nothing the field camera never sees (pack 0 heap; buildings.cull_unseen)
        n = m.write(os.path.join(out, f'{name}.dae'), wrap={t: ('CLAMP', 'CLAMP') for t in m.tris})
        used |= set(m.tris)
        print(f'{name}: {n} triangles, textures {sorted(m.tris)}')
    pairs = []
    for t in sorted(used):
        shutil.copy(os.path.join(TEX, SOURCES[t], t + '.png'), os.path.join(out, t + '.png'))
        pairs.append(f'{t} {t}_pl')
    open(os.path.join(out, 'palettes.txt'), 'w').write('\n'.join(pairs) + '\n')
    open(os.path.join(out, 'textures.txt'), 'w').write(''.join(f'{SOURCES[t]} {t}\n' for t in sorted(used)))

if __name__ == '__main__':
    main(sys.argv[1])
