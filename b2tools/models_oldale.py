"""Oldale Town's buildings: Sapphire's shapes, Black 2 textures.

    python3 models_oldale.py ../work/buildings/oldale

Writes center.dae, mart.dae, house.dae (+ texture images, palettes.txt, textures.txt). Footprints are Sapphire's:
4x3 tiles for all four buildings (Center, Mart, two houses). Origin = footprint centre on the ground, +z = front.
Doors (drawn by the game from the building pack): Center/Mart use Black 2's sliding Pokémon Center door, houses
Accumula's house door; all are half a tile left of centre, as in Sapphire.
"""
import os, sys, math, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exterior_layers import separate
from dae import Model
from buildings import Region, rect, decal, box_walls, gable_roof, face, shadow, DOOR_WALL, pc_door_hood, cull_unseen

TEX = os.path.join(HERE, '..', 'work', 'tex')
# pack 0 (Nuvema/Accumula): Black 2's own Pokémon Center textures
RED = Region('pc_kabe02', (64, 32), 0, 2, 14, 20)          # red roof panel with a dark seam
RED_EAVE = Region('pc_kabe02', (64, 32), 8, 22, 56, 32)    # red band
CREST = Region('pc_win1', (16, 128), 0, 32, 16, 48)        # Poké Ball emblem (transparent surround)
GLASS = Region('pc_win1', (16, 128), 1, 64, 15, 96)        # blue glass panel
# pack 5 (Route 4): white walls and a flat blue panel, for the Mart's roof
WHITE = Region('r4_b03_yane01', (64, 64), 2, 18, 14, 26)
BLUE = Region('r4_b03_yane01', (64, 64), 4, 34, 60, 54)
# pack 53 (Floccesy): beige siding and orange ribbed roof for Oldale's houses
BEIGE = Region('t06_h_03_a', (64, 64), 0, 0, 30, 14)
ORANGE = Region('t06_h_03_a', (64, 64), 34, 18, 62, 54)
# pack 57 (Humilau): framed window (as Littleroot's houses)
WINDOW = Region('c14_h1_body', (64, 64), 38, 32, 62, 46)
MADO = Region('h_mado', (16, 16), 0, 0, 16, 16)

SOURCES = {'pc_kabe02': 'ext00', 'pc_win1': 'ext00', 'h_kage': 'ext00', 'h_mado': 'ext00',
           'r4_b03_yane01': 'ext05', 't06_h_03_a': 'ext53', 'c14_h1_body': 'ext57'}
UP, E = (0, 1, 0), (1, 0, 0)

def round_roof(m, region, x0, x1, z0, z1, y0, h, segs=8, rep=(14, 18), y_back=None):
    """Rounded roof: half-ellipse from the front eave (z1, y0) over a crown h high to the back eave (z0, y_back, default
    y0; a lower back eave tilts the roof, its base rising from back to front), extruded along x, with flat end caps.
    Texture runs along x (u) and over the curve (v)."""
    zc, r = (z0 + z1) / 2, (z1 - z0) / 2
    yb = y0 if y_back is None else y_back
    base = lambda z: yb + (y0 - yb) * (z - z0) / (z1 - z0)
    pts = [(zc + r * math.cos(math.pi * k / segs), base(zc + r * math.cos(math.pi * k / segs)) + h * math.sin(math.pi * k / segs))
           for k in range(segs + 1)]
    arc = 0.0
    for (za, ya), (zb, yb) in zip(pts, pts[1:]):
        seg = math.hypot(zb - za, yb - ya)
        # quad from the lower edge (za) to the upper edge (zb), seen from outside
        u_axis = (1, 0, 0)
        v_axis = (0, (yb - ya) / seg, (zb - za) / seg)
        origin = (x0, ya - arc * v_axis[1], za - arc * v_axis[2])   # so t = arc .. arc+seg lands on this segment
        face(m, region, origin, u_axis, v_axis, [(0, arc), (x1 - x0, arc), (x1 - x0, arc + seg), (0, arc + seg)], rep)
        arc += seg
    for x, sgn in ((x1, 1), (x0, -1)):       # end caps
        outline = [(z, y) for z, y in pts]
        verts = [(x, y, z) for z, y in outline]
        # pts run from the front eave over the crown to the back eave: counter-clockwise seen from -x, so the +x cap
        # takes them reversed (both caps faced into the roof and were culled: the roof was open at both ends, seen
        # through from the side of a Center/Mart; map_gfx 2026-10-11)
        if sgn > 0: verts = verts[::-1]
        for k in range(1, len(verts) - 1):
            a, b, c = verts[0], verts[k], verts[k + 1]
            uv = lambda p: region.uv(((p[2] - z0) / (z1 - z0)), (p[1] - base(p[2])) / h)
            m.tri(region.tex, [(*a, *uv(a)), (*b, *uv(b)), (*c, *uv(c))])
    return pts

def crest_on_roof(m, y0, h, z0, z1, t_deg=58, size=22, y_back=None):
    """Poké Ball emblem lying on the front of a round roof (tangent to the curve), as on Sapphire's buildings."""
    t = math.radians(t_deg); zc, r = (z0 + z1) / 2, (z1 - z0) / 2
    k = 0 if y_back is None else (y0 - y_back) / (z1 - z0)   # (a tilted roof's base rises k per unit towards the front)
    yb = y0 - k * (z1 - z0)
    pz = zc + r * math.cos(t); py = yb + k * (pz - z0) + h * math.sin(t)
    tz, ty = -r * math.sin(t), h * math.cos(t) - k * r * math.sin(t)   # tangent (up the roof)
    ln = math.hypot(tz, ty); tz, ty = tz / ln, ty / ln
    nz, ny = -ty, tz                                          # outward normal
    if nz < 0: nz, ny = -nz, -ny
    centre = (0, py + ny * 2.0, pz + nz * 2.0)               # 2 units off the roof (nearer flickers)
    decal(m, CREST, centre, E, (0, ty, tz), size, size)

def poke_building(roof_region, roof_rep):
    """Sapphire's Pokémon Center / Mart shape: white box, glass front, rounded roof with the Poké Ball crest. The front
    wall is 36 high and the game's curved sliding door (door_pc, 93; door origin x -8, z 16: its arc's ends on the wall)
    stands in it under a white canopy following its curve, below the eave, as Black 2's own Center holds it and as
    every house holds its door; the door stood 4-14 units out from 22-unit walls with its top against the roof
    (door_fix 2026-10-11). The roof tilts: its back eave stays at 22 and the crown 12 over the base, so the Center is
    no taller behind than before and people standing behind it stay in view (Mauville's Mart)."""
    m = Model('poke_building')
    G, GB, RH = 36, 22, 12                     # front eave, back eave, crown over the (tilted) base
    yb = lambda z: GB + (G - GB) * (z + 24) / 48          # the roof's base line (eaves at z -24 / +24)
    shadow(m, -36, 36, -28, 30)
    rect(m, WHITE, (-30, 0, 20), E, UP, 60, G, rep=(12, 9))                       # front wall
    side = [(0, 0), (40, 0), (40, yb(-20)), (0, yb(20))]                           # side walls up to the roof's base
    face(m, WHITE, (30, 0, 20), (0, 0, -1), UP, side, rep=(12, 9))
    face(m, WHITE, (-30, 0, -20), (0, 0, 1), UP, [(0, 0), (40, 0), (40, yb(20)), (0, yb(-20))], rep=(12, 9))
    for x in (12.5, 24):                                       # glass panes right of the door (its arc: x -21.2..5.2)
        decal(m, GLASS, (x, 15, 21.0), E, UP, 10, 22)     # 1 unit out (nearer flickers)
    band = RED_EAVE if roof_region is RED else BLUE           # eave band, left and right of the door's canopy
    rect(m, band, (-32, G - 2, 22.2), E, UP, 9, 4, rep=(48, 4))
    rect(m, band, (7, G - 2, 22.2), E, UP, 25, 4, rep=(48, 4))
    pc_door_hood(m, WHITE, WHITE, -8, 16, 31, 35, band_rep=(12, 9))
    round_roof(m, roof_region, -32, 32, -24, 24, G, RH, rep=roof_rep, y_back=GB)
    crest_on_roof(m, G, RH, -24, 24, y_back=GB)
    return m

def house():
    """Oldale house: beige siding, orange ribbed gable roof, door left of centre, window right. Walls DOOR_WALL (38)
    high so the eave clears Black 2's door model (236, y 33); they were 24, the eave at 22 (door_fix 2026-10-11)."""
    m = Model('oldale_house')
    G = DOOR_WALL
    shadow(m, -34, 34, -26, 28)
    box_walls(m, -28, 28, -20, 20, 0, G, BEIGE, rep=(30, 14), sides='sew')
    decal(m, MADO, (13, 18, 21.0), E, UP, 18, 10)        # 1 and 2 units out (nearer layers flicker)
    decal(m, WINDOW, (13, 18, 22.0), E, UP, 20, 12)
    face(m, BEIGE, (28, G, 20), (0, 0, -1), UP, [(0, 0), (40, 0), (20, 14)], rep=(30, 14))
    face(m, BEIGE, (-28, G, -20), (0, 0, 1), UP, [(0, 0), (40, 0), (20, 14)], rep=(30, 14))
    gable_roof(m, ORANGE, -32, 32, -26, 26, G - 2, G + 16, rep=(28, 36))
    return m

def main(out):
    os.makedirs(out, exist_ok=True)
    models = {'center': poke_building(RED, (14, 18)), 'mart': poke_building(BLUE, (56, 20)), 'house': house()}
    used = set()
    for name, m in models.items():
        separate(m)        # layers >= 1 unit apart (melonDS flicker; b2tools/exterior_layers.py)
        cull_unseen(m)     # nothing the field camera never sees (pack 0 heap; buildings.cull_unseen)
        n = m.write(os.path.join(out, f'{name}.dae'), wrap={t: ('CLAMP', 'CLAMP') for t in m.tris})
        used |= set(m.tris)
        print(f'{name}: {n} triangles, textures {sorted(m.tris)}')
    for t in sorted(used):
        shutil.copy(os.path.join(TEX, SOURCES[t], t + '.png'), os.path.join(out, t + '.png'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in sorted(used)))
    open(os.path.join(out, 'textures.txt'), 'w').write(''.join(f'{SOURCES[t]} {t}\n' for t in sorted(used)))

if __name__ == '__main__':
    main(sys.argv[1])
