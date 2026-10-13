"""Ever Grande City's Pokemon League: Sapphire's shape and colours, Black 2 textures (group towns5, res 409).

    python3 models_evergrande.py ../work/buildings/evergrande

Sapphire footprint (data/plans/EverGrandeCity.json): x 13-23, rows 0-5 (the map's top rows: the building rises out of
the cliff), door (18,5) in the middle. Look (screenshots/sapphire crop, notes/TOWNS_TOWNS5.md): a tall orange-brown
block with rows of blue windows, cream towers at both ends standing a little forward, and an entrance porch: four grey
columns under a curved cream canopy with the Poke Ball emblem, a glass double door. The Pokemon Center is the shared
res 0. Origin = footprint centre on the ground, +z = front; the front wall at z = +20 (4 units into the door tile).

Textures (all already in the Hoenn building set): t2_buil1 (pack 0, Accumula's brick block: window rows over orange
brick, the window panes transparent with glass h_mado 1 unit behind), t06_h_03_a (slice: plain warm beige), gate_1 and
pc_win1 (pack 0: grey concrete, Poke Ball emblem). Door: Black 2's sliding glass door (res 93), centred (dx 0).
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import shadow, pc_door_hood
from models_slateport import UP, E, N, face, rect, decal, walls, flat, rectangle, post, tiled, write_models
from models_routes import SOURCES, CREST, GREY, YELLOW, UW, F

BRICK = tiled('t2_buil1', (64, 64))       # window band (top half) over orange brick (bottom half)
GLASSW = tiled('h_mado', (16, 16))        # glass seen through the window holes

def league():
    """Pokemon League (11x6): 72-unit block x -72..72, cream end towers x +-(72..88), porch on four columns (res 409)."""
    m = Model('eg_league')
    X, Z0, H = 72, -60, 72
    shadow(m, -92, 92, -66, 40)
    # glass planes 1 unit behind the brick walls (south, east, west), then the walls with their window holes
    for d, wall in ((1.0, GLASSW), (0.0, BRICK)):
        rep = (16, 16) if wall is GLASSW else (48, 36)
        face(m, wall, (-X, 0, F - d), E, UP, [(0, 0), (2 * X, 0), (2 * X, H), (0, H)], rep)
    flat(m, GREY, rectangle(-X, X, Z0, F), H, rep=(UW, 40))
    # end towers (cream), standing 4 units forward, a little taller than the block
    for x0, x1 in ((-88, -X), (X, 88)):
        walls(m, YELLOW, rectangle(x0, x1, Z0, F + 4), 0, H + 6, rep=(UW, 40))
        flat(m, YELLOW, rectangle(x0, x1, Z0, F + 4), H + 6, rep=(UW, UW))
        for y in (24, 48):                                            # Sapphire's light/dark bands on the towers
            rect(m, GREY, (x0, y, F + 5.0), E, UP, x1 - x0, 2, rep=(UW, 2))
    # porch: curved cream canopy (front edge an arc) on four grey columns, emblem in the middle
    arc = [(44 * math.sin(math.radians(a)), F + 6 + 10 * math.cos(math.radians(a))) for a in range(-90, 91, 30)]
    poly = arc + [(44, F - 2), (-44, F - 2)]                            # rectangle() order: south edge west -> east
    walls(m, YELLOW, poly, 40, 47, rep=(UW, 7))
    flat(m, YELLOW, poly, 47, rep=(UW, UW))
    decal(m, CREST, (0, 43.5, F + 16.6), E, UP, 9, 9)
    for x in (-36, -20, 20, 36):
        post(m, GREY, x, F + 10, 5, 0, 40)
    # the game's curved sliding door (door_pc 93, origin z 16: its arc's ends on the wall) under its own canopy, as
    # Black 2's Center holds it (it stood 4-14 units out with only the porch roof high over it; door_fix 2026-10-11)
    pc_door_hood(m, YELLOW, GREY, 0, F - 4, 31, 35, band_rep=(UW, 7))
    return m

def models():
    return {'league': league()}

if __name__ == '__main__':
    write_models(sys.argv[1], models(), SOURCES)
