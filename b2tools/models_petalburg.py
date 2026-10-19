"""Petalburg City's buildings, and the generic Pokémon Gym every Hoenn town uses: Sapphire's shapes, Black 2 textures.

    python3 models_petalburg.py ../work/buildings/petalburg

Writes gym.dae (res 320, the generic Gym exterior, shared by every town), wally.dae (res 321, Wally's house, 5 wide)
and house.dae (res 322, the General-tileset house, 4 wide), plus texture images, palettes.txt and textures.txt.

Footprints are Sapphire's (data/plans/PetalburgCity.json; notes/TOWNS_TOWNS1.md): Gym 6x5 tiles with the door half a
tile right of the footprint centre (+8 units, column 3 in every Sapphire Gym), Wally's house 5x4 (door in the middle), houses 4x4 incl. the walk-behind
roof row (door half a tile left of centre). Origin = footprint centre on the ground, +z = front (south); the front
wall stands 4 units into the door tile (world.py places it with "front" = the front wall's z).
"""
import os, sys, math, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exterior_layers import separate
from dae import Model
from buildings import Region, rect, decal, box_walls, hip_roof, gable_roof, face, slope, shadow, DOOR_WALL, pc_door_hood, cull_unseen, dark_doorway

TEX = os.path.join(HERE, '..', 'work', 'tex')
UP, E, S = (0, 1, 0), (1, 0, 0), (0, 0, 1)
UW = 400          # 'repeat' wider than any face: a region that is uniform along u is stretched, not cut

# --- pack 0 / slice textures (already in the Hoenn building texture set) ---
WHITE = Region('r4_b03_yane01', (64, 64), 2, 18, 14, 26)       # light grey-white wall (Route 4 building)
BLUE = Region('r4_b03_yane01', (64, 64), 4, 34, 60, 54)        # flat blue panel
SMALL_WIN = Region('r4_b03_yane01', (64, 64), 4, 7, 17, 18)    # blue window in a grey frame
PANEL = Region('r4_b03_yane01', (64, 64), 11, 57, 33, 64)      # white sign board with grey studs
CREST = Region('pc_win1', (16, 128), 0, 32, 16, 48)            # Poké Ball emblem (transparent surround)
GLASS = Region('pc_win1', (16, 128), 1, 64, 15, 96)            # blue glass panel
POST = Region('c14_h1_body', (64, 64), 14, 24, 17, 56)         # wooden post (Humilau)
WINDOW = Region('c14_h1_body', (64, 64), 38, 32, 62, 46)       # framed window, glass transparent
BASE = Region('c14_h1_body', (64, 64), 36, 56, 64, 64)         # orange skirting
BEAM = Region('c14_h1_body', (64, 64), 36, 20, 64, 28)         # dark wood band
MADO = Region('h_mado', (16, 16), 0, 0, 16, 16)                # window glass
# --- new for this group ---
GYM_ROOF = Region('yane_001', (16, 64), 0, 0, 16, 64)          # orange roof tiles (Nuvema/Accumula, pack 0): Ruby and
                                                               # Sapphire's orange Gym roof (user, 2026-10-09; was tan)
ROOF_RED = Region('t06_h_01_a', (64, 64), 0, 7, 64, 31)        # red roof tiles in rows (Floccesy, pack 53)
RIDGE = Region('t06_h_01_a', (64, 64), 0, 3, 64, 7)            # cream ridge band above the tiles
CREAM = Region('t06_h_01_a', (64, 64), 35, 47, 50, 62)         # cream-yellow wall

SOURCES = {'r4_b03_yane01': 'ext05', 'pc_win1': 'ext00', 'c14_h1_body': 'ext57', 'h_mado': 'ext00', 'h_kage': 'ext00',
           'sand_tex001': 'ext01', 't06_h_01_a': 'ext53', 'yane_001': 'ext00'}

WRAPPED = set()   # textures drawn whole and repeated by the hardware (WRAP), so a face needs no cutting

def wface(m, tex, origin, u_axis, v_axis, outline, rep):
    """A planar face showing a whole texture repeated every rep = (rs, rt) units, as one polygon (WRAP mode); far
    fewer triangles than buildings.face, which cuts faces at every repeat of an atlas region."""
    verts = [tuple(origin[k] + s * u_axis[k] + t * v_axis[k] for k in range(3)) + (s / rep[0], t / rep[1])
             for s, t in outline]
    for k in range(1, len(verts) - 1):
        m.tri(tex, [verts[0], verts[k], verts[k + 1]])
    WRAPPED.add(tex)

def wslope(m, tex, a, b, c, d, rep):
    """buildings.slope for a whole wrapped texture (u along the eave a->b, v up the slope)."""
    u = [b[k] - a[k] for k in range(3)]; lu = math.sqrt(sum(x * x for x in u)); u = [x / lu for x in u]
    w = [d[k] - a[k] for k in range(3)]; dot = sum(w[k] * u[k] for k in range(3))
    v = [w[k] - dot * u[k] for k in range(3)]; lv = math.sqrt(sum(x * x for x in v)); v = [x / lv for x in v]
    to2d = lambda p: (sum((p[k] - a[k]) * u[k] for k in range(3)), sum((p[k] - a[k]) * v[k] for k in range(3)))
    pts = [to2d(p) for p in (a, b, c, d)]
    if c == d: pts = pts[:3]
    wface(m, tex, a, u, v, pts, rep)

def wgable(m, tex, x0, x1, z0, z1, y0, y1, rep):
    zc = (z0 + z1) / 2
    wslope(m, tex, (x0, y0, z1), (x1, y0, z1), (x1, y1, zc), (x0, y1, zc), rep)
    wslope(m, tex, (x1, y0, z0), (x0, y0, z0), (x0, y1, zc), (x1, y1, zc), rep)

def whip(m, tex, x0, x1, z0, z1, y0, rx0, rx1, rz, y1, rep):
    """buildings.hip_roof for a whole wrapped texture (one polygon per roof face)."""
    A, B, C, D = (x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)
    R0, R1 = (rx0, y1, rz), (rx1, y1, rz)
    wslope(m, tex, A, B, R1, R0, rep); wslope(m, tex, C, D, R0, R1, rep)
    wslope(m, tex, B, C, R1, R1, rep); wslope(m, tex, D, A, R0, R0, rep)

def window(m, x, y, z, w=20, h=11):
    decal(m, MADO, (x, y, z + 1.0), E, UP, w, h)            # glass 1 unit out, frame 2 (nearer flickers)
    decal(m, WINDOW, (x, y, z + 2.0), E, UP, w + 2, h + 2)

def gym():
    """Sapphire's Pokémon Gym (Petalburg/Rustboro/Dewford share it): a wide, low block with a tan roof, white-blue
    walls with a band of windows, the Poké Ball crest and a sign board on the left, and a glass-fronted entrance
    porch with angled sides around the door (door centre x = +8). Footprint 6x5 tiles: x -48..48, front F = 24.
    Walls DOOR_WALL (38) high, the porch 36, and the game's curved sliding door (door_pc 93, origin x 8, z 20: its arc's
    ends on the porch front) under a canopy following its curve, as Black 2's own Center holds it. The porch was 23 and
    the door stood 4-14 units out in front of it, its top against the roof (door_fix 2026-10-11)."""
    m = Model('hoenn_gym')
    F, B = 24, -54                     # porch front (4 units into the door tile) / back wall
    FM = F - 8                         # main front wall, set back behind the porch
    G = DOOR_WALL                      # main walls
    shadow(m, -52, 52, B - 4, F + 6)
    # main block
    box_walls(m, -46, 46, B, FM, 0, G, WHITE, rep=(UW, 8), sides='sew')
    for z, sides in ((FM + 1.0, 's'),):
        rect(m, BLUE, (-46, 0, z), E, UP, 92, 3, rep=(UW, 3))           # blue skirting
        rect(m, BLUE, (-46, G - 7, z), E, UP, 92, 2, rep=(UW, 2))       # blue stripe under the eave
        rect(m, BLUE, (-46, 8, z), E, UP, 92, 1.5, rep=(UW, 1.5))       # thin stripe (Sapphire's banded wall)
    for x in (47, -47):                                             # same bands on the sides
        d = (0, 0, -1) if x > 0 else (0, 0, 1)
        z0 = FM if x > 0 else B
        rect(m, BLUE, (x, 0, z0), d, UP, FM - B, 3, rep=(UW, 3))
        rect(m, BLUE, (x, G - 7, z0), d, UP, FM - B, 2, rep=(UW, 2))
    for x in (-36, -22, 36):                                            # window band (two left, one right)
        decal(m, SMALL_WIN, (x, 19, FM + 1.0), E, UP, 12, 8)
    decal(m, CREST, (-38, 15, FM + 2.0), E, UP, 9, 9)                   # Poké Ball crest
    decal(m, PANEL, (-23, 15, FM + 2.0), E, UP, 18, 6)                  # sign board ("GYM" in Sapphire)
    # roof: low hip, orange tiles, overhanging the walls
    whip(m, 'yane_001', -49, 49, B - 3, FM + 3, G, -30, 30, (B + FM) / 2, G + 10, rep=(16, 32))
    # entrance porch: trapezoid, wider at the back; door (game model, 26 wide) in the front face
    bl, br, fl, fr = (-14, FM), (30, FM), (-6, F), (22, F)
    H = G - 2
    rect(m, WHITE, (fl[0], 0, F), E, UP, fr[0] - fl[0], H, rep=(UW, 8))                 # front face
    slope(m, WHITE, (fr[0], 0, F), (br[0], 0, FM), (br[0], H, FM), (fr[0], H, F), rep=(UW, 8))   # right side
    slope(m, WHITE, (bl[0], 0, FM), (fl[0], 0, F), (fl[0], H, F), (bl[0], H, FM), rep=(UW, 8))   # left side
    # glass strips on the angled sides

    for (xa, za), (xb, zb) in (((fr[0], F), (br[0], FM)), ((bl[0], FM), (fl[0], F))):
        ln = math.hypot(xb - xa, zb - za); ux, uz = (xb - xa) / ln, (zb - za) / ln
        nx, nz = uz, -ux                                                 # outward normal (right-hand)
        cx, cz = (xa + xb) / 2 + nx * 1.0, (za + zb) / 2 + nz * 1.0
        decal(m, GLASS, (cx, 11, cz), (ux, 0, uz), UP, 7, 14)
    rect(m, BLUE, (fl[0], H - 2, F + 1.0), E, UP, fr[0] - fl[0], 2, rep=(UW, 2))      # blue lintel band
    pc_door_hood(m, WHITE, BLUE, 8, F - 4, 31, 34, band_rep=(UW, 8))  # canopy over the door
    # porch roof: flat orange slab with a little overhang, meeting the main roof's eave
    top = [(fl[0] - 2, F + 2), (fr[0] + 2, F + 2), (br[0] + 2, FM - 4), (bl[0] - 2, FM - 4)]
    wface(m, 'yane_001', (0, H + 1, 0), E, (0, 0, -1), [(x, -z) for x, z in top], (16, 32))
    rect(m, WHITE, (fl[0] - 2, H, F + 2), E, UP, fr[0] - fl[0] + 4, 1, rep=(UW, 1))    # slab edge
    return m

def house(width, door_dx, windows):
    """Sapphire's General-tileset house (Petalburg; also used by other towns): red tiled gable roof with a cream
    ridge band, cream walls with wooden posts at the corners and beside the door, framed windows.
    width in tiles (4 or 5); door_dx = door centre relative to the footprint centre; windows = their x centres.
    The front wall is DOOR_WALL - 1 (37) high so the front eave clears Black 2's door model (260, y 32): with walls of
    27 the eave came down to 24.5, through the door's top (door_fix 2026-10-11). The back wall stays 27, the back slope
    steeper: the house is no taller behind than before and people standing behind it stay in view (Petalburg)."""
    m = Model(f'gen_house{width}')
    hw = width * 8 - 4                 # half wall width (4 units in from the footprint edge)
    F, B = 20, -22
    shadow(m, -hw - 6, hw + 6, B - 6, F + 8)
    eave, eave_b, rise = DOOR_WALL - 1, 27, 10      # front / back eave, ridge over the front eave
    zc, yr = (F + B) / 2, eave + rise
    rect(m, CREAM, (-hw, 0, F), E, UP, 2 * hw, eave, rep=(UW, eave))
    rect(m, BASE, (-hw, 0, F + 1.0), E, UP, 2 * hw, 3, rep=(UW, 3))
    rect(m, BEAM, (-hw, eave - 3, F + 1.0), E, UP, 2 * hw, 3, rep=(UW, 3))
    for x in (-hw + 1.5, door_dx - 10, door_dx + 10, hw - 1.5):
        rect(m, POST, (x - 1.5, 0, F + 2.0), E, UP, 3, eave, rep=(3, 32))
    for x in windows:
        window(m, x, 18, F, 18, 11)        # frames clear of the posts
    # side walls with their gable ends (cream) up to the roof
    D = F - B
    face(m, CREAM, (hw, 0, F), (0, 0, -1), UP, [(0, 0), (D, 0), (D, eave_b), (F - zc, yr), (0, eave)], rep=(UW, 37))
    face(m, CREAM, (-hw, 0, B), (0, 0, 1), UP, [(0, 0), (D, 0), (D, eave), (zc - B, yr), (0, eave_b)], rep=(UW, 37))
    ox, oz = hw + 3, 4                 # roof overhang
    kf, kb = (yr - eave) / (F - zc), (yr - eave_b) / (zc - B)       # pitches (the slopes continue the gables' edges)
    slope(m, ROOF_RED, (-ox, eave - oz * kf, F + oz), (ox, eave - oz * kf, F + oz), (ox, yr, zc), (-ox, yr, zc), rep=(64, 24))
    slope(m, ROOF_RED, (ox, eave_b - oz * kb, B - oz), (-ox, eave_b - oz * kb, B - oz), (-ox, yr, zc), (ox, yr, zc), rep=(64, 24))
    # ridge band: a thin cream strip on each slope just below the ridge
    for sgn, k in ((1, kf), (-1, kb)):
        z1 = zc + sgn * 5; y1 = yr - 5 * k
        a, b = (-ox, y1 + 1.0, z1), (ox, y1 + 1.0, z1)
        c, d = (ox, yr + 1.0, zc), (-ox, yr + 1.0, zc)
        if sgn > 0: slope(m, RIDGE, a, b, c, d, rep=(UW, 6))
        else: slope(m, RIDGE, b, a, d, c, rep=(UW, 6))
    return m

MODELS = {'gym': gym, 'wally': lambda: house(5, 0, (-22, 22)), 'house': lambda: house(4, -8, (14.5,))}

def write(out, models, sources):
    os.makedirs(out, exist_ok=True)
    used = set()
    for name, m in models.items():
        separate(m)        # layers >= 1 unit apart (melonDS flicker; b2tools/exterior_layers.py)
        dark_doorway(m, out, name, lambda t: os.path.join(TEX, sources[t], t + '.png') if t in sources else None)
        cull_unseen(m)     # nothing the field camera never sees (pack 0 heap; buildings.cull_unseen)
        n = m.write(os.path.join(out, f'{name}.dae'), wrap={t: ('WRAP', 'WRAP') if t in WRAPPED else ('CLAMP', 'CLAMP') for t in m.tris})
        used |= {t for t in m.tris if m.tris[t]}
        print(f'{name}: {n} triangles, textures {sorted(t for t in m.tris if m.tris[t])}')
    for t in sorted(used):
        shutil.copy(os.path.join(TEX, sources[t], t + '.png'), os.path.join(out, t + '.png'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in sorted(used)))
    open(os.path.join(out, 'textures.txt'), 'w').write(''.join(f'{sources[t]} {t}\n' for t in sorted(used)))

def main(out):
    write(out, {k: f() for k, f in MODELS.items()}, SOURCES)

if __name__ == '__main__':
    main(sys.argv[1])
