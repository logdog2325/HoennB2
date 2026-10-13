"""Sapphire's moving truck (pokeruby OBJ_EVENT_GFX_TRUCK), parked in Littleroot for the opening, in Black 2 art.

    python3 models_truck_ext.py ../work/buildings/truck_ext

Writes truck.dae (+ the texture images it uses, palettes.txt, textures.txt); rebuild_slice.sh converts it with
ToNsbmd. Registered as exterior pack-0 res 460 in data/buildings/slice.json with info type 11 (event prop, like
c09gate_main / tt_train01), so a script can hide it with BMSetVisible 8, x, z, 0 (8 = type 11 after the game's
FieldPropResInfo_GetTypeConv). Placed twice by data/hoenn_world.json (LittlerootTown "props").

Size from Sapphire's 48x48 sprite: 46 units long (cab 14 + box 31), 20 deep (the sprite's top face is about one tile;
the prop sits centred on the player's row), box top at 36. Origin = centre of the ground footprint; the cab points west (-x) and the open back faces east (+x), towards the tile where the player
steps out (Sapphire (3,10) / (12,10)). Black 2 textures only:
- cargo box: Driftveil's shipping container (pack 8 d5_conte02b ribs, d5_conte02a doors), rear doors swung open
  flat against the sides;
- cab: white train panels (pack 33 lb_body_a2), windscreen and side windows from the train's glass (lb_win_c.1);
- wheels and undercarriage: the train's wheel (lb_tire, the wheel disc and its dark surround);
- ground shadow: pack 0's h_kage, as the houses.
Textures not already in pack 0's set are merged into it losslessly (slice.json "textures", nsbtx.merge).
"""
import os, sys, math
from exterior_layers import separate
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model
from buildings import Region, rect, decal, box_walls, face, shadow

ROOT = os.path.join(HERE, '..')
TEX = os.path.join(ROOT, 'work', 'tex')
FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
SETS = {'ext08': 8, 'ext33': 33, 'ext00': 0}       # building texture sets (a/1/7/4 entries) the textures come from

RIBS = Region('d5_conte02b', (32, 32), 0, 0, 32, 32)          # container side, rust-red ribs
DOOR = Region('d5_conte02a', (64, 32), 32, 0, 48, 28)          # one container door: ribs and a lock bar
WHITE = Region('lb_body_a2', (64, 64), 3, 2, 61, 28)           # plain white train panel
DOORPANEL = Region('lb_body_a2', (64, 64), 32, 32, 64, 64)     # framed white panel (cab door)
SKIRT = Region('lb_body_a2', (64, 64), 0, 40, 32, 64)          # white fading into a grey band (cab front, bumper)
GLASS1 = Region('lb_win_c.1', (32, 16), 0, 0, 16, 16)          # one framed dark pane
GLASS2 = Region('lb_win_c.1', (32, 16), 0, 0, 32, 16)          # two panes (windscreen)
DARK = Region('lb_tire', (64, 32), 48, 16, 64, 32)             # dark undercarriage
WHEEL_C, WHEEL_R = (24, 11.5), 14                              # lb_tire: wheel hub centre and radius in pixels
SOURCES = {'d5_conte02a': 'ext08', 'd5_conte02b': 'ext08', 'lb_body_a2': 'ext33', 'lb_win_c.1': 'ext33',
           'lb_tire': 'ext33', 'h_kage': 'ext00'}

UP, E, S, W, N = (0, 1, 0), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, 0, -1)
X0, X1 = -23, 23            # front of the cab, back of the box
HD = 10                     # half the box's depth (z)
CAB = (-23, -9, -(HD - 1), HD - 1)    # x0, x1, z0, z1
BOX = (-8, 23, -HD, HD)
Y_BODY, Y_CAB, Y_BOX = 10, 28, 36
WHEEL_Y, WHEEL_RAD, AXLES = 5, 5, (-16, 14)

def wheel(m, x, side):
    """One wheel at axle x on the south (side=1) or north (side=-1) side: a disc with the train's wheel image and a
    dark tread; the disc stands 0.5 outside the cab's side."""
    z_out, z_in, n = side * (HD - 0.5), side * (HD - 3.5), 12
    pts = [(x + WHEEL_RAD * math.cos(2 * math.pi * k / n), WHEEL_Y + WHEEL_RAD * math.sin(2 * math.pi * k / n)) for k in range(n)]
    uv = lambda px, py: ((WHEEL_C[0] + (px - x) / WHEEL_RAD * WHEEL_R) / 64, 1 - (WHEEL_C[1] - (py - WHEEL_Y) / WHEEL_RAD * WHEEL_R) / 32)
    for k in range(1, n - 1):
        tri = [pts[0], pts[k], pts[k + 1]] if side > 0 else [pts[0], pts[k + 1], pts[k]]
        m.tri('lb_tire', [(px, py, z_out, *uv(px, py)) for px, py in tri])
    for k in range(n):                      # tread: quads around the rim, facing outwards
        (ax, ay), (bx, by) = pts[k], pts[(k + 1) % n]
        q = [(ax, ay, z_in), (bx, by, z_in), (bx, by, z_out), (ax, ay, z_out)]
        if side < 0: q = q[::-1]
        m.quad('lb_tire', [(*p, u, v) for p, (u, v) in zip(q, [(48 / 64, 0.5), (1, 0.5), (1, 0), (48 / 64, 0)])])

def side_face(m, region, z, facing, pts, rep):
    """Planar polygon in the plane z, facing +z (facing=1) or -z; pts = [(x, y)] counter-clockwise seen from +z."""
    if facing > 0: face(m, region, (0, 0, z), E, UP, pts, rep)
    else: face(m, region, (0, 0, z), W, UP, [(-x, y) for x, y in pts[::-1]], rep)

def cab_side(m, z, facing):
    """Cab side at z: white in front, a framed door panel with a window, a pillar following the raked windscreen."""
    x0, x1 = CAB[0], CAB[1]
    side_face(m, WHITE, z, facing, [(x0, Y_BODY), (-17, Y_BODY), (-17, 18), (x0, 18)], (14, 12))
    side_face(m, WHITE, z, facing, [(x0, 18), (-17, 18), (-17, Y_CAB), (x0 + 5, Y_CAB)], (14, 12))
    side_face(m, DOORPANEL, z, facing, [(-17, Y_BODY), (x1, Y_BODY), (x1, Y_CAB), (-17, Y_CAB)], (x1 + 17, Y_CAB - Y_BODY))
    decal(m, GLASS1, ((-17 + x1) / 2, 22.5, z + facing * 1.0), E if facing > 0 else W, UP, 6.5, 7.5)   # door window

def build():
    m = Model('truck_ext')
    shadow(m, X0 - 3, X1 + 3, -(HD + 3), HD + 3, y=2.0)        # 2 under the flower decals (now y 4) and 2 over the ground
    # undercarriage, front bumper and rear step
    box_walls(m, X0 + 2, X1 - 1, -(HD - 3.5), HD - 3.5, 4, Y_BODY + 0.5, DARK, rep=(16, 16))
    box_walls(m, X0 - 0.5, X0 + 2, -(HD - 1), HD - 1, 4, Y_BODY, DARK, rep=(16, 16), sides='nsw')
    box_walls(m, X1 - 2, X1 + 0.5, -(HD - 1), HD - 1, 4, 7, DARK, rep=(16, 16), sides='nse')
    rect(m, DARK, (X1 - 2, 7, HD - 1), E, N, 2.5, 2 * (HD - 1), rep=(16, 16))
    for ax in AXLES:
        for side in (1, -1): wheel(m, ax, side)
    # cab: sides, front (white skirt below a raked windscreen), roof, back
    x0, x1, z0, z1 = CAB
    cab_side(m, z1, 1); cab_side(m, z0, -1)
    rect(m, SKIRT, (x0, Y_BODY, z0), S, UP, z1 - z0, 8, rep=(z1 - z0, 8))
    hood = math.hypot(5, Y_CAB - 18)
    face(m, GLASS2, (x0, 18, z0), S, (5 / hood, (Y_CAB - 18) / hood, 0), [(0, 0), (z1 - z0, 0), (z1 - z0, hood), (0, hood)],
         rep=(z1 - z0, hood))
    rect(m, WHITE, (x0 + 5, Y_CAB, z1), E, N, x1 - x0 - 5, z1 - z0, rep=(14, 22))
    rect(m, WHITE, (x1, Y_BODY, z1), N, UP, z1 - z0, Y_CAB - Y_BODY, rep=(14, 22))
    # cargo box: container ribs outside, open back (dark inside), rear doors swung open flat against the sides
    bx0, bx1, bz0, bz1 = BOX
    box_walls(m, bx0, bx1, bz0, bz1, Y_BODY + 0.5, Y_BOX, RIBS, rep=(32, 32), sides='nsw')
    rect(m, RIBS, (bx0, Y_BOX, bz1), E, N, bx1 - bx0, bz1 - bz0, rep=(32, 32))
    t = 1.0                                             # wall thickness at the open back
    ix0, iz0, iz1, iy0, iy1 = bx0 + t, bz0 + t, bz1 - t, Y_BODY + 0.5 + t, Y_BOX - t
    for y0, y1, z0_, z1_ in ((Y_BODY + 0.5, iy0, bz0, bz1), (iy1, Y_BOX, bz0, bz1), (iy0, iy1, bz0, iz0), (iy0, iy1, iz1, bz1)):
        rect(m, RIBS, (bx1, y0, z1_), N, UP, z1_ - z0_, y1 - y0, rep=(32, 32))     # rim of the opening, facing east
    rect(m, DARK, (ix0, iy0, iz1), E, N, bx1 - ix0, iz1 - iz0, rep=(16, 16))       # floor
    rect(m, DARK, (ix0, iy1, iz0), E, S, bx1 - ix0, iz1 - iz0, rep=(16, 16))       # ceiling (faces down)
    rect(m, DARK, (ix0, iy0, iz0), E, UP, bx1 - ix0, iy1 - iy0, rep=(16, 16))      # inner north wall
    rect(m, DARK, (bx1, iy0, iz1), W, UP, bx1 - ix0, iy1 - iy0, rep=(16, 16))      # inner south wall
    rect(m, DARK, (ix0, iy0, iz1), N, UP, iz1 - iz0, iy1 - iy0, rep=(16, 16))      # inner front wall
    dw = (bz1 - bz0) / 2                                                            # door width: half the box
    rect(m, DOOR, (bx1 - dw, Y_BODY + 1, bz1 + 1), E, UP, dw, Y_BOX - Y_BODY - 1.5, rep=(dw, Y_BOX - Y_BODY - 1.5))
    rect(m, DOOR, (bx1, Y_BODY + 1, bz0 - 1), W, UP, dw, Y_BOX - Y_BODY - 1.5, rep=(dw, Y_BOX - Y_BODY - 1.5))
    return m

def texture_images(names):
    """PNG images of the textures, decoded from the game's own building texture sets (exact sizes, for ToNsbmd);
    also makes sure work/tex has the sets the slice's texture merge reads (work/tex/extNN.nsbtx, palNN.txt)."""
    import b2files, nsbtx
    out = {}
    for setname in sorted({SOURCES[n] for n in names}):
        p = os.path.join(TEX, setname + '.nsbtx')
        if not os.path.exists(p):
            data = b2files.building_textures(FILES, SETS[setname])
            open(p, 'wb').write(data)
            pairs = set().union(*(nsbtx.material_pairs(x['bmd']) for x in b2files.building_pack(FILES, SETS[setname])))
            open(os.path.join(TEX, 'pal' + setname[3:] + '.txt'), 'w').write(''.join(f'{t} {q}\n' for t, q in sorted(pairs, key=str) if t and q))
        out.update({n: img for n, img, _ in nsbtx.decode(open(p, 'rb').read()) if n in names})
    return out

def main(out):
    os.makedirs(out, exist_ok=True)
    m = build()
    separate(m)            # layers >= 1 unit apart (melonDS flicker; b2tools/exterior_layers.py)
    clamp = {t: ('CLAMP', 'CLAMP') for t in m.tris}
    n = m.write(os.path.join(out, 'truck.dae'), wrap=clamp)
    used = sorted(m.tris)
    for t, img in texture_images(used).items():
        img.save(os.path.join(out, t + '.png'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in used))
    open(os.path.join(out, 'textures.txt'), 'w').write(''.join(f'{SOURCES[t]} {t}\n' for t in used))
    print(f'truck: {n} triangles, textures {used}')

if __name__ == '__main__':
    main(sys.argv[1])
