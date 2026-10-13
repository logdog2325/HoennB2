"""Fallarbor Town's buildings: Sapphire's shapes and colours, Black 2 textures (group towns3, res 360-362).

    python3 models_fallarbor.py ../work/buildings/fallarbor

Writes house.dae (res 360), house_pipes.dae (res 361, Prof. Cozmo's house with the two roof pipes), contest.dae
(res 362, Contest Hall), the texture images they use (copied from the game's own building texture sets in
work/tex/extNN), palettes.txt and textures.txt (which texture comes from which set). The Pokémon Center and Mart are
the shared res 0 / res 3 (models_oldale.py).

Sapphire footprints (data/plans/FallarborTown.json): houses 4x4 tiles (door in column 1), Contest Hall 5x5 (door in
the middle). Origin = footprint centre on the ground, +z = front (south); the front wall is at z = +20 (the 'front'
value in data/towns/FallarborTown.json), so it sits 4 units into the door tile as Black 2 places its buildings.
"""
import os, sys, math, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exterior_layers import separate
from dae import Model
from buildings import Region, rect, decal, box_walls, gable_roof, face, shadow, slope, DOOR_WALL, cull_unseen

TEX = os.path.join(HERE, '..', 'work', 'tex')
UP, E = (0, 1, 0), (1, 0, 0)
# pack 59 (Join Avenue shop fronts): olive-green siding, the colour of Sapphire's Fallarbor walls
OLIVE = Region('rr_misel1_02', (32, 64), 0, 1, 32, 31)
OLIVE_TRIM = Region('rr_misel1_02', (32, 64), 0, 31, 16, 34)     # tan band under the siding
# pack 0 (Nuvema/Accumula): orange roof tiles (rows parallel to the eave, like Sapphire's striped roof), glass,
# Poké Ball crest, grey metal, white
ROOF = Region('yane_001', (16, 64), 0, 0, 16, 64)
AWNING = Region('yane_001', (16, 64), 0, 0, 16, 16)
MADO = Region('h_mado', (16, 16), 0, 0, 16, 16)
CREST = Region('pc_win1', (16, 128), 0, 32, 16, 48)
GREY = Region('gate_1', (64, 32), 24, 22, 64, 32)
# pack 57 (Humilau): framed window, as Littleroot's and Oldale's houses
WINDOW = Region('c14_h1_body', (64, 64), 38, 32, 62, 46)
# pack 4 (Virbank): the coral-red trailer siding (Sapphire's Contest Hall walls are this red), plain and a lighter
# panel for the door pillars; pack 6 (Nimbasa's Musical theater): pale blue panels for the roof (Sapphire's roof is a
# pale blue-grey studded plate)
WALL_RED = Region('trailer_01a', (32, 64), 17, 30, 31, 40)
PILLAR = Region('trailer_01a', (32, 64), 2, 16, 14, 28)
PANEL = Region('c4_bp01', (32, 32), 0, 0, 32, 32)
# pack 5 (Route 4): flat blue and white panels (the Mart's), for the Contest Hall's base stripe and bunting
BLUE = Region('r4_b03_yane01', (64, 64), 4, 34, 60, 54)
WHITE = Region('r4_b03_yane01', (64, 64), 2, 18, 14, 26)

SOURCES = {'rr_misel1_02': 'ext59', 'yane_001': 'ext00', 'h_mado': 'ext00', 'pc_win1': 'ext00', 'gate_1': 'ext00',
           'h_kage': 'ext00', 'c14_h1_body': 'ext57', 'trailer_01a': 'ext04', 'c4_bp01': 'ext06',
           'r4_b03_yane01': 'ext05'}

def prism(m, region, x, z, r, y0, y1, sides=8, rep=None):
    """Upright n-sided prism (a pipe), outward faces only."""
    pts = [(x + r * math.cos(2 * math.pi * (k + 0.5) / sides), z + r * math.sin(2 * math.pi * (k + 0.5) / sides))
           for k in range(sides)]
    w = 2 * r * math.sin(math.pi / sides)
    for (xa, za), (xb, zb) in zip(pts, pts[1:] + pts[:1]):
        # counter-clockwise seen from outside: from b to a along the ring (ring runs counter-clockwise seen from above
        # with +z south, so outward faces go from the later point to the earlier one)
        u = ((xa - xb) / w, 0, (za - zb) / w)
        rect(m, region, (xb, y0, zb), u, UP, w, y1 - y0, rep or (w, y1 - y0))

def cap(m, region, x, z, r, y, sides=8):
    """Flat top of a prism, one copy of the region."""
    pts = [(x + r * math.cos(2 * math.pi * (k + 0.5) / sides), z + r * math.sin(2 * math.pi * (k + 0.5) / sides))
           for k in range(sides)]
    face(m, region, (x - r, y, z + r), E, (0, 0, -1), [(px - (x - r), (z + r) - pz) for px, pz in pts[::-1]],
         (2 * r, 2 * r))

def window(m, x, y, z):
    decal(m, MADO, (x, y, z + 1.0), E, UP, 18, 10)      # 1 and 2 units out (nearer layers flicker)
    decal(m, WINDOW, (x, y, z + 2.0), E, UP, 20, 12)
    # small orange awning over the window (Sapphire's window has an orange top)
    face(m, AWNING, (x - 11, y + 7, z + 4), E, (0, 0.6, -0.8), [(0, 0), (22, 0), (22, 5), (0, 5)], (16, 5))

def house(pipes=False):
    """Fallarbor house: olive siding, orange tiled gable roof, door left of centre (column 1), window right. Walls are
    DOOR_WALL (38) high so Black 2's 33-unit door model (res 236) stands under the eave, which overhangs 6 units (at
    34 the eave came down to 32, in front of the door's top; door_fix 2026-10-11)."""
    m = Model('fa_house')
    shadow(m, -34, 34, -26, 28)
    H = DOOR_WALL
    box_walls(m, -28, 28, -20, 20, 0, H, OLIVE, rep=(32, 34), sides='sew')   # (no back wall: never seen)
    rect(m, OLIVE_TRIM, (-28, 0, 21.0), E, UP, 56, 2, rep=(16, 2))
    window(m, 13, 17, 20)
    tri = [(0, 0), (40, 0), (20, 14)]
    face(m, OLIVE, (28, H, 20), (0, 0, -1), UP, tri, rep=(32, 34))       # gable ends
    face(m, OLIVE, (-28, H, -20), (0, 0, 1), UP, tri, rep=(32, 34))
    gable_roof(m, ROOF, -32, 32, -26, 26, H - 2, H + 16, rep=(16, 30))
    if pipes:
        # Prof. Cozmo's house: two pipes standing behind the ridge, right half (Sapphire tiles (7,13), (8,13))
        for x in (7, 19):
            prism(m, OLIVE, x, -9, 3.5, H + 6, H + 26)
            prism(m, GREY, x, -9, 4.2, H + 23, H + 27)
            cap(m, GREY, x, -9, 4.2, H + 27)
    return m

def octagon(x0, x1, z0, z1, c):
    """Outline (counter-clockwise seen from above, +z south) of a rectangle with chamfered corners."""
    return [(x0 + c, z1), (x1 - c, z1), (x1, z1 - c), (x1, z0 + c), (x1 - c, z0), (x0 + c, z0), (x0, z0 + c), (x0, z1 - c)]

def contest_hall():
    """Contest Hall (5x5): coral-red walls on a blue-and-white base stripe, white bunting, lighter pillars by the
    sliding door, grey fascia, low chamfered roof of pale blue panels, Poké Ball emblem over the door."""
    m = Model('fa_contest')
    shadow(m, -44, 44, -42, 30)
    X, Z0, Z1, H = 38, -36, 20, 34
    box_walls(m, -X, X, Z0, Z1, 0, H, WALL_RED, rep=(14, 11.33), sides='sew')   # (no back wall: never seen)
    rect(m, BLUE, (-X, 0, Z1 + 1.0), E, UP, 2 * X, 3, rep=(28, 3))
    rect(m, WHITE, (-X, 3, Z1 + 1.0), E, UP, 2 * X, 1, rep=(12, 1))
    rect(m, BLUE, (X + 1.0, 0, Z1), (0, 0, -1), UP, Z1 - Z0, 3, rep=(28, 3))
    rect(m, BLUE, (-X - 1.0, 0, Z0), (0, 0, 1), UP, Z1 - Z0, 3, rep=(28, 3))
    for x in (-19, 13):                    # pillars either side of the door
        rect(m, PILLAR, (x, 4, Z1 + 1.5), E, UP, 6, H - 4, rep=(6, 10))
    for x0 in (-36, -28, -20, 20, 28):     # bunting: white pennants along the top of the front wall
        face(m, WHITE, (x0, H - 7, Z1 + 2.0), E, UP, [(4, 0), (7, 6), (1, 6)], rep=(12, 8))
    # fascia band and chamfered roof
    F0, F1 = H, H + 5
    out = octagon(-X - 2, X + 2, Z0 - 2, Z1 + 2, 6)
    for (xa, za), (xb, zb) in zip(out, out[1:] + out[:1]):
        L = math.hypot(xb - xa, zb - za)
        rect(m, GREY, (xa, F0, za), ((xb - xa) / L, 0, (zb - za) / L), UP, L, F1 - F0, rep=(40, 5))
    inner = octagon(-X + 6, X - 6, Z0 + 6, Z1 - 8, 6)
    top = F1 + 8
    for k in range(8):                      # sloped ring from the fascia up to the flat top
        a, b = out[k], out[(k + 1) % 8]
        c, d = inner[(k + 1) % 8], inner[k]
        slope(m, PANEL, (a[0], F1, a[1]), (b[0], F1, b[1]), (c[0], top, c[1]), (d[0], top, d[1]), rep=(24, 12))
    x0, z1 = inner[7][0], inner[0][1]
    face(m, PANEL, (x0, top, z1), E, (0, 0, -1), [(px - x0, z1 - pz) for px, pz in inner], rep=(24, 24))
    # emblem plate over the door, on the fascia
    decal(m, CREST, (0, F1 + 3, Z1 + 1.5), E, (0, 0.8, -0.6), 12, 12)
    return m

def write_models(out, models, sources):
    """Write each model's DAE plus the texture images, palettes.txt and textures.txt next to them."""
    os.makedirs(out, exist_ok=True)
    used = set()
    for name, m in models.items():
        separate(m)        # layers >= 1 unit apart (melonDS flicker; b2tools/exterior_layers.py)
        cull_unseen(m)     # nothing the field camera never sees (pack 0 heap; buildings.cull_unseen)
        n = m.write(os.path.join(out, f'{name}.dae'), wrap={t: ('CLAMP', 'CLAMP') for t in m.tris})
        used |= set(m.tris)
        print(f'{name}: {n} triangles, textures {sorted(m.tris)}')
    for t in sorted(used):
        shutil.copy(os.path.join(TEX, sources[t], t + '.png'), os.path.join(out, t + '.png'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in sorted(used)))
    open(os.path.join(out, 'textures.txt'), 'w').write(''.join(f'{sources[t]} {t}\n' for t in sorted(used)))

def models():
    return {'house': house(), 'house_pipes': house(pipes=True), 'contest': contest_hall()}

if __name__ == '__main__':
    write_models(sys.argv[1], models(), SOURCES)
