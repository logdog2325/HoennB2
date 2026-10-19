"""Lilycove City's buildings (group towns4): Sapphire's shapes and colours, Black 2 textures.

    python3 models_lilycove.py ../work/buildings/lilycove

Writes house.dae (res 380: Lilycove's blue-roofed house, 4 wide), fanclub.dae (381: the same house 5 wide, door in
the middle), dept.dae (382: Department Store), contest.dae (383: the big Contest Hall), museum.dae (384: Lilycove
Museum, placed as a prop: its doorway is walkable in Sapphire, so plan_map.py finds no footprint), motel.dae (385: Cove
Lily Motel), plus the texture images, palettes.txt and textures.txt (notes/TOWNS_TOWNS4.md).

Footprints are Sapphire's (data/plans/LilycoveCity.json). Units: 16 per tile; origin = footprint centre on the ground,
+z = front (south); the front wall F stands 4 units into the door tile (world.py places a building with "front" = F).
The helpers below (rotated regions, wrapped faces, prisms, cones) are shared by models_mossdeep.py and
models_pacifidlog.py.
"""
import os, sys, math, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exterior_layers import separate
from dae import Model
from buildings import Region, rect, decal, box_walls, face, slope, gable_roof, hip_roof, skirt_roof, shadow, DOOR_WALL, pc_door_hood, cull_unseen, dark_doorway

TEX = os.path.join(HERE, '..', 'work', 'tex')
UP, E = (0, 1, 0), (1, 0, 0)
UW = 400            # a 'repeat' wider than any face: a region uniform along u is stretched, not cut

class RotRegion(Region):
    """A region turned 90 degrees: the face's u (along a wall or eave) runs down the texture's y, its v (up the wall
    or slope) along the texture's x. Used to turn horizontal panel bands into vertical roof ribs."""
    def uv(self, fu, fv):
        px = self.x0 + fv * (self.x1 - self.x0)
        py = self.y0 + fu * (self.y1 - self.y0)
        return px / self.tw, 1 - py / self.th

# ---- textures already in pack 0's set or the slice's (cost nothing) -------------------------------------------------
WHITE = Region('r4_b03_yane01', (64, 64), 2, 18, 14, 26)        # light grey-white wall (Route 4 building, slice)
PURE = Region('r4_b03_yane01', (64, 64), 2.5, 17.25, 13.5, 17.75)   # its pure white line (inset), stretched: plain white
BLUE = Region('r4_b03_yane01', (64, 64), 4, 34, 60, 54)         # flat blue
SMALL_WIN = Region('r4_b03_yane01', (64, 64), 4, 7, 17, 18)     # blue window in a grey frame
STUDS = Region('r4_b03_yane01', (64, 64), 12, 58, 32, 63)       # white board with grey studs
DARK = Region('r4_b03_yane01', (64, 64), 58, 1, 63, 7)          # black
CREST = Region('pc_win1', (16, 128), 0, 32, 16, 48)             # Poké Ball emblem (transparent surround)
GLASS = Region('pc_win1', (16, 128), 1, 64, 15, 96)             # blue glass panel
MADO = Region('h_mado', (16, 16), 0, 0, 16, 16)                 # window glass
GREY = Region('gate_1', (64, 32), 24, 22, 64, 32)               # grey concrete
AWNING = Region('yane_001', (16, 64), 0, 0, 16, 16)             # orange tiles (Accumula roof)
WINDOW = Region('c14_h1_body', (64, 64), 38, 32, 62, 46)        # framed window, glass transparent (Humilau, slice)
POST = Region('c14_h1_body', (64, 64), 14, 24, 17, 56)          # wooden post
BEAM = Region('c14_h1_body', (64, 64), 36, 20, 64, 28)          # dark wood band
SKIRTING = Region('c14_h1_body', (64, 64), 36, 56, 64, 64)      # orange skirting
LATTICE = Region('c14_h1_body', (64, 64), 18, 0, 46, 18)        # vertical dark wood planks
SHINGLE = Region('c14_h2_yane', (64, 64), 0, 16, 16, 32)        # tan shingles (Littleroot's roofs)
SHINGLE_LT = Region('c14_h2_yane', (64, 64), 0, 0, 16, 16)      # cream shingles
# ---- new for this group -------------------------------------------------------------------------------------------
# pack 8 (Driftveil warehouse): periwinkle panel with horizontal bands; turned 90 degrees = Sapphire's ribbed blue roof
RIBS = RotRegion('d5whouse1a', (32, 16), 0, 0, 27, 16)
RIDGE = Region('d5whouse1a', (32, 16), 0, 7, 27, 10)            # its light band: the roof's ridge cap
# pack 6 (Nimbasa's Musical theater): pale blue panels = Sapphire's pale blue studded plates (Contest Hall roof,
# Department Store walls); pack 4 (Virbank trailer): coral red walls and pillars (also used by towns3's Contest Hall)
PANEL = Region('c4_bp01', (32, 32), 0, 0, 32, 32)
WALL_RED = Region('trailer_01a', (32, 64), 17, 30, 31, 40)
PILLAR = Region('trailer_01a', (32, 64), 2, 16, 14, 28)
SLATE = Region('en_sekia1', (64, 64), 33, 1, 39, 40)            # pack 48: dark slate blue (also Mossdeep's windows)

SOURCES = {'r4_b03_yane01': 'ext05', 'pc_win1': 'ext00', 'h_mado': 'ext00', 'h_kage': 'ext00', 'gate_1': 'ext00',
           'yane_001': 'ext00', 'c14_h1_body': 'ext57', 'c14_h2_yane': 'ext57', 'd5whouse1a': 'ext08',
           'c4_bp01': 'ext06', 'trailer_01a': 'ext04', 'plant_tex4': 'ext00', 'en_sekia1': 'ext48', 'c7h2_1': 'ext10',
           'c5_rb_03_w1': 'ext08'}

# ---- helpers --------------------------------------------------------------------------------------------------------
WRAPPED = set()     # textures drawn whole and repeated by the hardware (WRAP): one polygon per face

def wface(m, tex, origin, u_axis, v_axis, outline, rep, offset=(0, 0)):
    """Planar face showing a whole texture repeated every rep = (rs, rt) units (WRAP mode), one polygon."""
    verts = [tuple(origin[k] + s * u_axis[k] + t * v_axis[k] for k in range(3)) + (s / rep[0] + offset[0], t / rep[1] + offset[1])
             for s, t in outline]
    for k in range(1, len(verts) - 1):
        m.tri(tex, [verts[0], verts[k], verts[k + 1]])
    WRAPPED.add(tex)

def wrect(m, tex, origin, u_axis, v_axis, w, h, rep):
    wface(m, tex, origin, u_axis, v_axis, [(0, 0), (w, 0), (w, h), (0, h)], rep)

def flat(m, region, pts, y, rep=None):
    """Horizontal face (facing up) through pts [(x, z)] counter-clockwise seen from above with +z south."""
    face(m, region, (0, y, 0), E, (0, 0, -1), [(x, -z) for x, z in pts], rep)

def walls(m, region, pts, y0, y1, rep=None):
    """Upright faces along the closed outline pts [(x, z)] (clockwise seen from above with +z south, i.e. going from
    the front-left corner to the right along the front), facing outwards."""
    for (xa, za), (xb, zb) in zip(pts, pts[1:] + pts[:1]):
        L = math.hypot(xb - xa, zb - za)
        if L < 1e-6: continue
        rect(m, region, (xa, y0, za), ((xb - xa) / L, 0, (zb - za) / L), UP, L, y1 - y0, rep)

def octagon(x0, x1, z0, z1, c, cb=None):
    """Rectangle with chamfered corners (c at the front, cb at the back), front-left corner first, going right."""
    cb = c if cb is None else cb
    return [(x0 + c, z1), (x1 - c, z1), (x1, z1 - c), (x1, z0 + cb), (x1 - cb, z0), (x0 + cb, z0), (x0, z0 + cb), (x0, z1 - c)]

def ring(m, region, outer, inner, y0, y1, rep):
    """Sloped band from the outline outer at y0 up to the outline inner at y1 (same number of points)."""
    n = len(outer)
    for k in range(n):
        a, b = outer[k], outer[(k + 1) % n]
        c, d = inner[(k + 1) % n], inner[k]
        if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-6: continue
        slope(m, region, (a[0], y0, a[1]), (b[0], y0, b[1]), (c[0], y1, c[1]), (d[0], y1, d[1]), rep)

def polygon(cx, cz, r, n, phase=0.5):
    """Regular n-gon around (cx, cz), r = distance to the corners; with phase 0.5 an edge faces +z (the front).
    Same order as octagon(): front-left corner first, then along the front to the right (walls() faces outwards)."""
    out = []
    for k in range(n):
        a = math.pi / 2 + 2 * math.pi * (k + phase) / n
        out.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return [out[0]] + out[:0:-1]

def wfrustum(m, tex, outer, inner, y0, y1, rep_u, offset_v=0.0):
    """Like ring() for a whole wrapped texture: one band of the texture (v 0 at the bottom, 1 at the top) per call."""
    n = len(outer)
    for k in range(n):
        a, b = outer[k], outer[(k + 1) % n]
        c, d = inner[(k + 1) % n], inner[k]
        la = math.hypot(b[0] - a[0], b[1] - a[1])
        verts = [(a[0], y0, a[1], 0, offset_v), (b[0], y0, b[1], la / rep_u, offset_v),
                 (c[0], y1, c[1], la / rep_u, offset_v + 1), (d[0], y1, d[1], 0, offset_v + 1)]
        m.tri(tex, [verts[0], verts[1], verts[2]]); m.tri(tex, [verts[0], verts[2], verts[3]])
    WRAPPED.add(tex)

def wslope(m, tex, a, b, c, d, rep):
    """buildings.slope for a whole wrapped texture (u along the eave a->b, v up the slope), one polygon."""
    u = [b[k] - a[k] for k in range(3)]; lu = math.sqrt(sum(x * x for x in u)); u = [x / lu for x in u]
    w = [d[k] - a[k] for k in range(3)]; dot = sum(w[k] * u[k] for k in range(3))
    v = [w[k] - dot * u[k] for k in range(3)]; lv = math.sqrt(sum(x * x for x in v)); v = [x / lv for x in v]
    to2d = lambda p: (sum((p[k] - a[k]) * u[k] for k in range(3)), sum((p[k] - a[k]) * v[k] for k in range(3)))
    pts = [to2d(p) for p in (a, b, c, d)]
    if c == d: pts = pts[:3]
    wface(m, tex, a, u, v, pts, rep)

def wring(m, tex, outer, inner, y0, y1, rep):
    """ring() for a whole wrapped texture."""
    n = len(outer)
    for k in range(n):
        a, b = outer[k], outer[(k + 1) % n]
        c, d = inner[(k + 1) % n], inner[k]
        if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-6: continue
        wslope(m, tex, (a[0], y0, a[1]), (b[0], y0, b[1]), (c[0], y1, c[1]), (d[0], y1, d[1]), rep)

def wflat(m, tex, pts, y, rep):
    wface(m, tex, (0, y, 0), E, (0, 0, -1), [(x, -z) for x, z in pts], rep)

def window(m, x, y, z, w=16, h=12):
    decal(m, SMALL_WIN, (x, y, z + 1.0), E, UP, w, h)      # 1 unit out: nearer layers flicker on hardware/melonDS

def framed_window(m, x, y, z, w=18, h=11):
    decal(m, MADO, (x, y, z + 1.0), E, UP, w, h)
    decal(m, WINDOW, (x, y, z + 2.0), E, UP, w + 2, h + 2)

def gable_ends(m, region, hw, z0, z1, y, top, rep):
    """Wall triangles under a gable roof (ridge along x) at x = +-hw."""
    face(m, region, (hw, y, z1), (0, 0, -1), UP, [(0, 0), (z1 - z0, 0), ((z1 - z0) / 2, top - y)], rep)
    face(m, region, (-hw, y, z0), (0, 0, 1), UP, [(0, 0), (z1 - z0, 0), ((z1 - z0) / 2, top - y)], rep)

def write_models(out, models, sources=SOURCES):
    """Each model's DAE plus the texture images it uses, palettes.txt and textures.txt (for the registry)."""
    os.makedirs(out, exist_ok=True)
    used = set()
    for name, m in models.items():
        separate(m)        # layers >= 1 unit apart (melonDS flicker; b2tools/exterior_layers.py)
        dark_doorway(m, out, name, lambda t: os.path.join(TEX, sources[t], t + '.png') if t in sources else None)
        cull_unseen(m)     # nothing the field camera never sees (pack 0 heap; buildings.cull_unseen)
        n = m.write(os.path.join(out, f'{name}.dae'),
                    wrap={t: ('WRAP', 'WRAP') if t in WRAPPED else ('CLAMP', 'CLAMP') for t in m.tris})
        used |= {t for t in m.tris if m.tris[t]}
        print(f'{name}: {n} triangles, textures {sorted(t for t in m.tris if m.tris[t])}')
    for t in sorted(used):
        shutil.copy(os.path.join(TEX, sources[t], t + '.png'), os.path.join(out, t + '.png'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in sorted(used)))
    open(os.path.join(out, 'textures.txt'), 'w').write(''.join(f'{sources[t]} {t}\n' for t in sorted(used)))

# ---- Lilycove's buildings -------------------------------------------------------------------------------------------
def blue_house(width, door_dx, windows):
    """Lilycove house: lavender-white walls on a blue base, blue pillars either side of the door, blue-framed
    windows, tall gable roof of blue ribs (Sapphire's ribs run down the roof) with a light ridge cap.
    width in tiles (4: houses, 5: Pokémon Trainer Fan Club); door_dx = door centre from the footprint centre."""
    m = Model(f'ly_house{width}')
    hw = width * 8 - 4
    F, B, eave = 20, -24, DOOR_WALL + 1      # the game's doors 259-261 reach y 32 (apicula bounds: 6..32); the roof's
                                             # eave, 3 lower and 4 out, came to 31 with walls of 34 (door_fix)
    shadow(m, -hw - 6, hw + 6, B - 6, F + 8)
    box_walls(m, -hw, hw, B, F, 0, eave, WHITE, rep=(UW, 17), sides='sew')
    rect(m, BLUE, (-hw, 0, F + 1.0), E, UP, 2 * hw, 3, rep=(UW, 3))
    rect(m, BLUE, (hw + 1.0, 0, F), (0, 0, -1), UP, F - B, 3, rep=(UW, 3))
    rect(m, BLUE, (-hw - 1.0, 0, B), (0, 0, 1), UP, F - B, 3, rep=(UW, 3))
    for x in (door_dx - 13, door_dx + 9):                          # blue pillars framing the door (door is 18 wide)
        rect(m, BLUE, (x, 0, F + 1.5), E, UP, 4, eave, rep=(4, UW))
    for x in (-hw + 0.5, hw - 3.5):                                # blue corner posts
        rect(m, BLUE, (x, 0, F + 1.5), E, UP, 3, eave, rep=(3, UW))
    for x in windows:
        window(m, x, 18, F, 16, 12)
    # roof: gable, ridge along x, ribs down the slope
    zc, top = (F + B) / 2, eave + 22
    gable_ends(m, WHITE, hw, B, F, eave, top - 2, rep=(UW, 17))
    gable_roof(m, RIBS, -hw - 3, hw + 3, B - 4, F + 4, eave - 3, top, rep=(9, 40))
    k = (top - (eave - 3)) / (F + 4 - zc)
    for sgn in (1, -1):                                            # ridge cap: a light strip either side of the ridge
        z1 = zc + sgn * 4; y1 = top - 4 * k
        a, b = (-hw - 3, y1 + 0.8, z1), (hw + 3, y1 + 0.8, z1)
        c, d = (hw + 3, top + 0.8, zc), (-hw - 3, top + 0.8, zc)
        if sgn > 0: slope(m, RIDGE, a, b, c, d, rep=(27, 3))
        else: slope(m, RIDGE, b, a, d, c, rep=(27, 3))
    return m

def dept_store():
    """Lilycove Department Store (9 wide, 7 rows; Sapphire draws it past the map's north edge): a tall block of pale
    blue studded panels, a grid of blue windows, the Poké Ball emblem over the glass entrance (game door 93) with a
    grey canopy, shop windows under orange awnings either side, grey parapet."""
    m = Model('ly_dept')
    hw, F, B, H = 68, 20, -78, 104
    shadow(m, -hw - 6, hw + 6, B - 6, F + 8)
    for pts, rep in (([(-hw, F), (hw, F)], (32, 32)), ([(hw, F), (hw, B)], (32, 32)), ([(-hw, B), (-hw, F)], (32, 32))):
        (xa, za), (xb, zb) = pts
        L = math.hypot(xb - xa, zb - za)
        wrect(m, 'c4_bp01', (xa, 0, za), ((xb - xa) / L, 0, (zb - za) / L), UP, L, H, rep)
    rect(m, GREY, (-hw, 0, F + 1.0), E, UP, hw - 15, 4, rep=(40, 4))                 # base (left and right of the door)
    rect(m, GREY, (15, 0, F + 1.0), E, UP, hw - 15, 4, rep=(40, 4))
    rect(m, GREY, (hw + 1.0, 0, F), (0, 0, -1), UP, F - B, 4, rep=(40, 4))
    rect(m, GREY, (-hw - 1.0, 0, B), (0, 0, 1), UP, F - B, 4, rep=(40, 4))
    for y in (46, 68, 90):                                                         # window grid
        for x in (-46, 0, 46):
            if (x, y) == (0, 46):
                decal(m, CREST, (0, 46, F + 1.5), E, UP, 22, 22)                     # emblem above the entrance
            else:
                window(m, x, y, F, 14, 12)
    # entrance: glass panels beside the door, a grey canopy following the game's curved sliding door (door_pc 93,
    # origin z 16: its arc's ends on the wall); the flat canopy was at 28-31 and the door stood 4-14 units out, its top
    # through the canopy's edge (door_fix 2026-10-11)
    for x in (-17, 17):
        decal(m, GLASS, (x, 13, F + 1.0), E, UP, 6, 24)
    pc_door_hood(m, WHITE, GREY, 0, F - 4, 31, 35, band_rep=(UW, 4))
    # shop windows with orange awnings
    for x in (-56, -38, 38, 56):
        decal(m, GLASS, (x, 12, F + 1.0), E, UP, 13, 14)
        slope(m, AWNING, (x - 8, 20, F + 7), (x + 8, 20, F + 7), (x + 8, 25, F + 0.5), (x - 8, 25, F + 0.5), rep=(16, 8))
    # roof: flat, grey parapet
    wflat(m, 'c4_bp01', [(-hw, F), (hw, F), (hw, B), (-hw, B)], H, rep=(32, 32))
    rect(m, WHITE, (-hw - 1, H - 3, F + 1.0), E, UP, 2 * hw + 2, 4, rep=(UW, 4))
    return m

def contest_hall():
    """Lilycove Contest Hall (7 wide, 6 rows + a walk-behind roof row): low coral-red walls with darker pillars and
    white bunting, blue/white base stripe, grey fascia, and a big pale blue studded roof with chamfered corners
    rising to a wide flat top; the game's glass sliding door (93) in the middle, the emblem over it."""
    m = Model('ly_contest')
    hw, F, B, H = 52, 20, -72, DOOR_WALL     # door 93 reaches y 30, its canopy 35 (walls of 32: door_fix)
    shadow(m, -hw - 6, hw + 6, B - 6, F + 8)
    plan = octagon(-hw, hw, B, F, 10, 6)
    walls(m, WALL_RED, plan, 0, H, rep=(28, UW))
    for x0, x1 in ((-hw + 10, -15), (15, hw - 10)):                                   # base stripes, beside the door
        rect(m, BLUE, (x0, 0, F + 1.0), E, UP, x1 - x0, 3, rep=(UW, 3))
        rect(m, WHITE, (x0, 3, F + 1.0), E, UP, x1 - x0, 1, rep=(UW, 1))
    for x in (-hw + 10, -30, -18, 14, 26, hw - 14):                               # pillars along the front
        rect(m, PILLAR, (x, 4, F + 1.5), E, UP, 4, H - 4, rep=(4, 10))
    for x0 in list(range(-hw + 12, -15, 6)) + list(range(16, hw - 12, 6)):           # bunting
        face(m, WHITE, (x0, H - 7, F + 2.0), E, UP, [(2.5, 0), (5, 5), (0, 5)], rep=(12, 8))
    # fascia band and the studded roof
    F0, F1 = H, H + 5
    out = octagon(-hw - 2, hw + 2, B - 2, F + 2, 11, 7)
    walls(m, GREY, out, F0, F1, rep=(40, 5))
    inner = octagon(-hw + 8, hw - 8, B + 8, F - 10, 8, 5)
    top = F1 + 12
    wring(m, 'c4_bp01', out, inner, F1, top, rep=(24, 12))
    wflat(m, 'c4_bp01', inner, top, rep=(24, 24))
    decal(m, CREST, (0, F1 + 3, F + 2.5), E, (0, 0.8, -0.6), 12, 12)
    pc_door_hood(m, WHITE, GREY, 0, F - 4, 31, 35, band_rep=(UW, 4))
    return m

def museum():
    """Lilycove Museum (prop; footprint x 7-16, rows 2-6, the upper block over rows 0-3, entrance x 11-12): white
    neoclassical wings with square columns and windows on a blue base, flat studded roofs, a taller central block
    behind with its own colonnade, and a recessed dark doorway (the door row is 5; the stairs below are terrain).
    Origin at x 12.0 (footprint centre), z 7.0 (the south edge of row 6); placed at map tile (12.0, 6.98)."""
    m = Model('ly_museum')
    hw, F, B, H = 77, -2, -78, 34
    shadow(m, -hw - 4, hw + 4, B - 4, F + 4)
    ex, eb = 16, -28                                     # entrance recess: x -16..16, back (door plane) at z -28
    # wings (front faces either side of the entrance) and sides
    rect(m, PURE, (-hw, 0, F), E, UP, hw - ex, H, rep=(UW, UW))
    rect(m, PURE, (ex, 0, F), E, UP, hw - ex, H, rep=(UW, UW))
    rect(m, PURE, (hw, 0, F), (0, 0, -1), UP, F - B, H, rep=(UW, UW))
    rect(m, PURE, (-hw, 0, B), (0, 0, 1), UP, F - B, H, rep=(UW, UW))
    for x0, x1 in ((-hw, -ex), (ex, hw)):
        rect(m, BLUE, (x0, 0, F + 1.0), E, UP, x1 - x0, 5, rep=(UW, 5))
        rect(m, BLUE, (x0, 9, F + 1.0), E, UP, x1 - x0, 1.5, rep=(UW, 1.5))
        for k in range(4):                               # columns and windows between them
            cx = x0 + 5 + k * (x1 - x0 - 10) / 3
            box_walls(m, cx - 2.5, cx + 2.5, F, F + 4, 10, H - 4, PURE, rep=(UW, UW), sides='sew')
            if k < 3:
                window(m, cx + (x1 - x0 - 10) / 6, 20, F, 14, 11)
    # entrance recess: side walls, dark doorway, white lintel board above
    rect(m, PURE, (-ex, 0, eb), (0, 0, 1), UP, F - eb, H, rep=(UW, UW))
    rect(m, PURE, (ex, 0, F), (0, 0, -1), UP, F - eb, H, rep=(UW, UW))
    rect(m, PURE, (-ex, 26, eb), E, UP, 2 * ex, H - 26, rep=(UW, UW))
    rect(m, DARK, (-ex, 0, eb), E, UP, 2 * ex, 26, rep=(UW, UW))
    rect(m, PURE, (-ex - 2, 26, F + 0.5), E, UP, 2 * ex + 4, H + 6 - 26, rep=(UW, UW))
    decal(m, STUDS, (0, 32, F + 1.5), E, UP, 26, 7)
    for x in (-ex - 1.5, ex + 1.5):                      # entrance pillars
        box_walls(m, x - 2.5, x + 2.5, F, F + 4, 0, H, PURE, rep=(UW, UW), sides='sew')
    # wing roofs: flat studded plates with a white rim
    for x0, x1 in ((-hw - 2, -ex), (ex, hw + 2)):
        flat(m, STUDS, [(x0, F + 2), (x1, F + 2), (x1, B - 2), (x0, B - 2)], H, rep=(40, 20))
        rect(m, PURE, (x0, H - 2, F + 2), E, UP, x1 - x0, 3, rep=(UW, 3))
    flat(m, STUDS, [(-ex, F + 2), (ex, F + 2), (ex, eb), (-ex, eb)], H + 6, rep=(40, 20))
    # central upper block (x 9-14 in Sapphire): colonnade front at z -30, roof at 66
    cw, cf, cb, ch = 50, -32, -80, 66
    box_walls(m, -cw, cw, cb, cf, H, ch, PURE, rep=(UW, UW), sides='sew')
    rect(m, BLUE, (-cw, H + 2, cf + 1.0), E, UP, 2 * cw, 3, rep=(UW, 3))
    for k in range(6):
        cx = -cw + 5 + k * (2 * cw - 10) / 5
        box_walls(m, cx - 2.5, cx + 2.5, cf, cf + 4, H + 5, ch - 4, PURE, rep=(UW, UW), sides='sew')
        if k < 5:
            window(m, cx + (2 * cw - 10) / 10, H + 18, cf, 12, 11)
    flat(m, STUDS, [(-cw - 2, cf + 2), (cw + 2, cf + 2), (cw + 2, cb - 2), (-cw - 2, cb - 2)], ch, rep=(40, 20))
    rect(m, PURE, (-cw - 2, ch - 2, cf + 2), E, UP, 2 * cw + 4, 3, rep=(UW, 3))
    return m

def motel():
    """Cove Lily Motel (6 wide, rows 20-24): Littleroot-style two-tier roof of tan shingles, timber posts and beam,
    pale panel walls with framed windows right of the door (game door 260, column 1)."""
    m = Model('ly_motel')
    hw, F, B, eave = 44, 20, -26, DOOR_WALL   # (34: the skirt roof came down to 32, 6 out, over the door; door_fix)
    door = -24
    shadow(m, -hw - 6, hw + 6, B - 6, F + 8)
    box_walls(m, -hw, hw, B, F, 0, eave, WHITE, rep=(UW, 17), sides='sew')
    rect(m, SKIRTING, (-hw, 0, F + 1.0), E, UP, 2 * hw, 3, rep=(28, 3))
    rect(m, BEAM, (-hw, eave - 3, F + 1.0), E, UP, 2 * hw, 3, rep=(28, 3))
    for x in (-hw + 1.5, door - 11, door + 11, 14, hw - 1.5):
        rect(m, POST, (x - 1.5, 0, F + 2.0), E, UP, 3, eave, rep=(3, UW))
    for x in (2, 30):
        framed_window(m, x, 19, F, 14, 10)
    # lower roof (skirt) and the upper floor
    skirt_roof(m, SHINGLE, (-hw - 6, hw + 6, B - 6, F + 6), (-hw + 12, hw - 12, B + 8, F - 12), eave - 2, eave + 12, rep=(24, 24))
    box_walls(m, -hw + 12, hw - 12, B + 8, F - 12, eave + 10, eave + 22, WHITE, rep=(UW, UW), sides='sew')
    rect(m, BEAM, (-hw + 12, eave + 10, F - 12 + 1.0), E, UP, 2 * hw - 24, 3, rep=(28, 3))
    decal(m, SLATE, (0, eave + 16, F - 12 + 1.0), E, UP, 2 * hw - 36, 4)           # Sapphire's dark window band
    hip_roof(m, SHINGLE, -hw + 6, hw - 6, B + 2, F - 6, eave + 20, -hw + 26, hw - 26, (B + F) / 2 - 4, eave + 36, rep=(24, 24))
    return m

def beacon():
    """The small white harbour light on the cape east of the beach (Sapphire 'prop' tiles 61,33-34): a white post
    with a waisted middle and a yellow lamp on top. Prop on the lower tile (origin = its centre), no door."""
    m = Model('ly_beacon')
    shadow(m, -8, 8, -7, 9)
    LAMP = Region('c5_rb_03_w1', (32, 64), 21, 0, 31, 2)       # yellow (pack 8's window frame)
    hexa = lambda r: polygon(0, 0, r, 6)
    walls(m, PURE, hexa(6), 0, 6, rep=(UW, UW))                    # base
    flat(m, PURE, hexa(6), 6, rep=(UW, UW))
    walls(m, PURE, hexa(3), 6, 14, rep=(UW, UW))                   # waist
    walls(m, PURE, hexa(6.5), 14, 22, rep=(UW, UW))                # upper body
    flat(m, PURE, hexa(6.5), 22, rep=(UW, UW))
    walls(m, LAMP, hexa(4), 22, 28, rep=(UW, UW))                  # lamp
    flat(m, LAMP, hexa(4), 28, rep=(UW, UW))
    return m

def models():
    return {'beacon': beacon(), 'house': blue_house(4, -8, (14,)), 'fanclub': blue_house(5, 0, (-23, 23)), 'dept': dept_store(),
            'contest': contest_hall(), 'museum': museum(), 'motel': motel()}

if __name__ == '__main__':
    write_models(sys.argv[1], models())
