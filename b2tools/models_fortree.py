"""Fortree City's tree houses: Sapphire's shapes and colours, Black 2 textures (group towns3, res 364-365).

    python3 models_fortree.py ../work/buildings/fortree

Writes treehouse.dae (res 364: five of Fortree's six tree houses) and treehouse_tall.dae (res 365: House 4, whose
door is one row higher, with log rails beside the extra deck row), the texture images, palettes.txt and textures.txt.
The Pokémon Center, Mart and Gym are shared models (res 0, 3, 320).

Sapphire's tree house (metatiles 224-237 of gTileset_Fortree, screenshots: notes/TOWNS_TOWNS3.md): a log platform
about 4 tiles wide (yellow stacked logs), a small brown cabin set into its back with a dark open doorway in the middle
and shutters either side, a leafy crown on top (3 tiles wide), and in front of the door the walkway row with the rope
bridges and the ladder. Black 2 has no tree houses, so it is built from Black 2's wooden-house, bush and plank textures.

Origin = centre of the door column at the SOUTH edge of the door row (the north edge of the walkway), on the ground:
world.py lifts a prop to the height of the tile under its origin, so once the heights module raises Fortree's
walkways (+16/+32, notes/TERRAIN_HEIGHTS.md) the house stands on its walkway's level. The walkways run over the forest
floor on posts (heights.STILTS, 2026-10-09), so the platform has a plank rim and stands on stilts down to the floor
(STILT reaches below the deepest floor; the rest of a stilt is in the ground). The cabin's front wall is 4 units
into the door tile (z = -12), as Black 2 places its buildings. The walkway rows themselves (plan class 'bridge') are the
ground module's plank decks, so the model's platform stops at the door row's south edge (z = 0).

The doorway is part of the model (Sapphire's tree-house doors are open doorways, metatile behaviour 0x60 non-animated
door), so the pack record has no door model (0xFFFF).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, rect, decal, box_walls, face, shadow
from models_fallarbor import write_models
from models_oldale import round_roof

UP, E, S = (0, 1, 0), (1, 0, 0), (0, 0, 1)
DECK_Y = 2.0          # (1.0 lay 1 unit over the ground: flicker in melonDS; exterior sweep 2026-10-06)
RIM = 6.0             # the platform's rim reaches 6 under the walkway's deck (8 under the platform), as its side face
STILT = 40.0          # stilts reach 40 under the walkway: the floor is 16 under it (32 at the Decoration Shop), the rest is
                      # in the ground
# pack 57 (Humilau's wooden houses): orange horizontal boards (Sapphire's cabin is brown boards), dark vertical boards
# for the corner posts, black for the doorway
LOGS = Region('c14_h2_kabe', (64, 64), 14, 26, 28, 56)
POSTS = Region('c14_h1_body', (64, 64), 17, 0, 48, 20)
DARK = Region('c14_h1_body', (64, 64), 60, 1, 64, 11)
# pack 0 (Nuvema/Accumula): leafy bush (the crown) and a louvred brown shutter
LEAVES = Region('plant_tex4', (32, 32), 0, 0, 32, 32)
LEAVES_DARK = Region('plant_tex4', (32, 32), 0, 16, 32, 32)
SHUTTER = Region('t2_buil1', (64, 64), 42, 4, 54, 28)
# pack 53 (Floccesy Ranch barn): light planks, for the platform and the stacked-log wings (Sapphire's yellow logs)
PLANK = Region('d22_farm01_1', (64, 64), 0, 58, 64, 64)

SOURCES = {'c14_h2_kabe': 'ext57', 'c14_h1_body': 'ext57', 'plant_tex4': 'ext00', 't2_buil1': 'ext00',
           'h_kage': 'ext00', 'd22_farm01_1': 'ext53'}

def log_block(m, x0, x1, z0, z1, h):
    """A low wall of stacked logs (Sapphire's yellow log wings beside the cabin): planks repeating every 4 units up the
    sides, flat plank top."""
    box_walls(m, x0, x1, z0, z1, 0, h, PLANK, rep=(32, 4))
    face(m, PLANK, (x0, h, z1), E, (0, 0, -1), [(0, 0), (x1 - x0, 0), (x1 - x0, z1 - z0), (0, z1 - z0)], rep=(32, 4))

def treehouse(tall=False):
    m = Model('ft_treehouse')
    X, Z0, Z1, H = 20, -40, -12, 30         # cabin: 2.5 tiles wide, front wall 4 units into the door tile
    PX, PZ0 = 31, -46                       # platform: ~4 tiles wide, from behind the cabin to the door row's south edge
    face(m, PLANK, (-PX, DECK_Y, 0), E, (0, 0, -1), [(0, 0), (2 * PX, 0), (2 * PX, -PZ0), (0, -PZ0)], rep=(32, 4))
    # the platform's plank rim, as deep as the walkway's own side face (ground.py draw_decks: 8 units), and the stilts it
    # stands on: the walkways run 16 over the forest floor (32 at the Decoration Shop), heights.STILTS (map_glitch_fix
    # 2026-10-09; the house stood on an earth bank's edge before, its roof over the bank's cliff)
    box_walls(m, -PX, PX, PZ0, 0.1, -RIM, DECK_Y, PLANK, rep=(64, RIM + DECK_Y), sides='sew')
    for x in (-PX + 3, PX - 3):                          # stilts at the corners (the back ones show only their sides)
        box_walls(m, x - 2, x + 2, -6, -2, -STILT, -RIM, POSTS, rep=(6, STILT), sides='sew')
        box_walls(m, x - 2, x + 2, PZ0 + 2, PZ0 + 6, -STILT, -RIM, POSTS, rep=(6, STILT), sides='ew')
    box_walls(m, PX - 4, PX - 1, PZ0 + 6, -6, -RIM - 5, -RIM - 2, POSTS, rep=(6, 3), sides='e')    # side braces
    box_walls(m, -PX + 1, -PX + 4, PZ0 + 6, -6, -RIM - 5, -RIM - 2, POSTS, rep=(6, 3), sides='w')
    shadow(m, -X - 4, X + 4, Z0 - 4, Z1 + 4, y=DECK_Y + 4.0)    # (2 over the trees' shadows at 4, 4 over the deck)
    # cabin, with dark corner posts, open doorway and two shutters
    box_walls(m, -X, X, Z0, Z1, DECK_Y, H, LOGS, rep=(14, 30))
    for x in (-X - 3, X):
        box_walls(m, x, x + 3, Z1 - 3, Z1 + 0.5, DECK_Y, H, POSTS, rep=(6, 20))
    decal(m, DARK, (0, DECK_Y + 11, Z1 + 0.6), E, UP, 13, 22)
    for x in (-12, 12):
        decal(m, SHUTTER, (x, DECK_Y + 15, Z1 + 0.6), E, UP, 7, 13)
    # stacked-log wings either side of the cabin (on the house 4 one they run on beside the extra deck row as rails)
    for sgn in (-1, 1):
        a, b = sorted((sgn * (X + 3), sgn * PX))
        log_block(m, a, b, Z0, Z1 + 2, 12)
        if tall:
            a, b = sorted((sgn * 24, sgn * PX))
            log_block(m, a, b, -2, 16, 9)
    # leafy crown on the roof (3 tiles wide)
    box_walls(m, -24, 24, Z0 - 4, Z1 - 2, H - 2, H + 4, LEAVES_DARK, rep=(32, 10))
    round_roof(m, LEAVES, -26, 26, Z0 - 7, Z1 + 3, H + 2, 18, segs=6, rep=(30, 29))
    return m

def models():
    return {'treehouse': treehouse(), 'treehouse_tall': treehouse(tall=True)}

if __name__ == '__main__':
    write_models(sys.argv[1], models(), SOURCES)
