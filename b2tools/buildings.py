"""Gen 3-shaped buildings built from Black 2 textures (pure Python geometry -> .dae -> ToNsbmd).

Units: Black 2 model units, 16 per tile. Origin = centre of the building's ground footprint, y up, +z = south
(the side facing the camera, where the door is).

A Region is a rectangle of pixels inside one texture atlas. Faces are tiled with a region at a given world size per
repeat, by cutting the face into cells and clipping each cell to the face outline, so atlases never need wrapping.
"""
import math
from dae import Model

class Region:
    def __init__(self, tex, size, x0, y0, x1, y1):
        self.tex, (self.tw, self.th) = tex, size
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

    def uv(self, fu, fv):
        """fu, fv in 0..1 across the region (fv = 0 at the region's bottom edge) -> texture uv (v up)."""
        px = self.x0 + fu * (self.x1 - self.x0)
        py = self.y1 - fv * (self.y1 - self.y0)
        return px / self.tw, 1 - py / self.th

    @property
    def w(self): return self.x1 - self.x0
    @property
    def h(self): return self.y1 - self.y0

def _clip(poly, axis, value, keep_greater):
    """Sutherland-Hodgman clip of a 2D polygon [(s, t)] against s or t = value."""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ina = (a[axis] >= value) if keep_greater else (a[axis] <= value)
        inb = (b[axis] >= value) if keep_greater else (b[axis] <= value)
        if ina: out.append(a)
        if ina != inb:
            t = (value - a[axis]) / (b[axis] - a[axis])
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out

def face(m, region, origin, u_axis, v_axis, outline, rep=None, color=(1, 1, 1)):
    """Emit a planar face. origin + s*u_axis + t*v_axis spans the plane; outline = [(s, t)] counter-clockwise as seen
    from the front (normal = u x v). The region repeats every rep = (rs, rt) world units (default: its pixel size,
    i.e. 1 texel per unit, Black 2's usual density)."""
    rs, rt = rep or (region.w, region.h)
    ss = [p[0] for p in outline]; ts = [p[1] for p in outline]
    s0, s1, t0, t1 = min(ss), max(ss), min(ts), max(ts)
    i = math.floor(s0 / rs)
    while i * rs < s1 - 1e-6:
        j = math.floor(t0 / rt)
        while j * rt < t1 - 1e-6:
            cell = outline
            cell = _clip(cell, 0, i * rs, True); cell = _clip(cell, 0, (i + 1) * rs, False)
            cell = _clip(cell, 1, j * rt, True); cell = _clip(cell, 1, (j + 1) * rt, False)
            if len(cell) >= 3:
                verts = []
                for s, t in cell:
                    p = [origin[k] + s * u_axis[k] + t * v_axis[k] for k in range(3)]
                    verts.append((*p, *region.uv((s - i * rs) / rs, (t - j * rt) / rt)))
                for k in range(1, len(verts) - 1):
                    m.tri(region.tex, [verts[0], verts[k], verts[k + 1]], color)
            j += 1
        i += 1

def rect(m, region, origin, u_axis, v_axis, w, h, rep=None, color=(1, 1, 1)):
    face(m, region, origin, u_axis, v_axis, [(0, 0), (w, 0), (w, h), (0, h)], rep, color)

def decal(m, region, center, u_axis, v_axis, w, h, color=(1, 1, 1)):
    """One copy of the region stretched over w x h, centred on center (for windows, signs, vents)."""
    o = [center[k] - u_axis[k] * w / 2 - v_axis[k] * h / 2 for k in range(3)]
    face(m, region, o, u_axis, v_axis, [(0, 0), (w, 0), (w, h), (0, h)], (w, h), color)

def box_walls(m, x0, x1, z0, z1, y0, y1, region, rep=None, sides='nsew'):
    """Four outward-facing walls of an axis-aligned box."""
    up = (0, 1, 0)
    if 's' in sides: rect(m, region, (x0, y0, z1), (1, 0, 0), up, x1 - x0, y1 - y0, rep)   # front, faces +z
    if 'n' in sides: rect(m, region, (x1, y0, z0), (-1, 0, 0), up, x1 - x0, y1 - y0, rep)  # back, faces -z
    if 'e' in sides: rect(m, region, (x1, y0, z1), (0, 0, -1), up, z1 - z0, y1 - y0, rep)  # faces +x
    if 'w' in sides: rect(m, region, (x0, y0, z0), (0, 0, 1), up, z1 - z0, y1 - y0, rep)   # faces -x

def slope(m, region, a, b, c, d, rep=None):
    """A planar roof face through corners a, b (lower edge, left to right seen from outside) and c, d (upper edge,
    right to left); c may equal d (triangle). Texture runs along the eave (u) and up the slope (v)."""
    u = [b[k] - a[k] for k in range(3)]; lu = math.sqrt(sum(x * x for x in u)); u = [x / lu for x in u]
    # v = component of (d - a) perpendicular to u, i.e. straight up the slope
    w = [d[k] - a[k] for k in range(3)]; dot = sum(w[k] * u[k] for k in range(3))
    v = [w[k] - dot * u[k] for k in range(3)]; lv = math.sqrt(sum(x * x for x in v)); v = [x / lv for x in v]
    to2d = lambda p: (sum((p[k] - a[k]) * u[k] for k in range(3)), sum((p[k] - a[k]) * v[k] for k in range(3)))
    pts = [to2d(p) for p in (a, b, c, d)]
    if c == d: pts = pts[:3]
    face(m, region, a, u, v, pts, rep)

def hip_roof(m, region, x0, x1, z0, z1, y0, ridge_x0, ridge_x1, ridge_z, y1, rep=None):
    """Hip roof: eave rectangle at y0, ridge from (ridge_x0, y1, ridge_z) to (ridge_x1, y1, ridge_z)."""
    A, B, C, D = (x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)
    R0, R1 = (ridge_x0, y1, ridge_z), (ridge_x1, y1, ridge_z)
    slope(m, region, A, B, R1, R0, rep)        # front (south)
    slope(m, region, C, D, R0, R1, rep)        # back (north)
    slope(m, region, B, C, R1, R1, rep)        # east end
    slope(m, region, D, A, R0, R0, rep)        # west end

def skirt_roof(m, region, outer, inner, y0, y1, rep=None):
    """A sloped ring (lower roof of a two-storey house): outer rectangle at y0 up to inner rectangle at y1."""
    (ox0, ox1, oz0, oz1), (ix0, ix1, iz0, iz1) = outer, inner
    o = [(ox0, y0, oz1), (ox1, y0, oz1), (ox1, y0, oz0), (ox0, y0, oz0)]
    i = [(ix0, y1, iz1), (ix1, y1, iz1), (ix1, y1, iz0), (ix0, y1, iz0)]
    for k in range(4):
        slope(m, region, o[k], o[(k + 1) % 4], i[(k + 1) % 4], i[k], rep)

def gable_roof(m, region, x0, x1, z0, z1, y0, y1, rep=None):
    """Gable roof with the ridge along x at z = (z0+z1)/2."""
    zc = (z0 + z1) / 2
    slope(m, region, (x0, y0, z1), (x1, y0, z1), (x1, y1, zc), (x0, y1, zc), rep)   # front
    slope(m, region, (x1, y0, z0), (x0, y0, z0), (x0, y1, zc), (x1, y1, zc), rep)   # back

def shadow(m, x0, x1, z0, z1, y=2.0):
    """Soft ground shadow under a building (pack 0's translucent h_kage, as Black 2's own houses use: at y 1.8-2.3;
    closer to the ground it flickers against it on hardware/melonDS, 2026-10-06)."""
    r = Region('h_kage', (8, 8), 0, 0, 8, 8)
    face(m, r, (x0, y, z1), (1, 0, 0), (0, 0, -1), [(0, 0), (x1 - x0, 0), (x1 - x0, z1 - z0), (0, z1 - z0)],
         (x1 - x0, z1 - z0))

# ----------------------------------------------------------------------------------------------- the game's doors
# Black 2's door models (pack res, drawn by the game at the building origin + (dx, dy, dz), field_buildmodel.c
# FieldPropSystem_CheckCreateDoorReq): door_n_01-03 (259-261) and door_t1_01 (164) are a plate 18 wide from y 6 to 32,
# its face 2 units in front of the door origin; door_t1_02 (165, 236) y 4 to 33; the Pokemon Center's curved sliding
# door_pc (93) y 2.9 to 29.8, 26.4 wide and bulging 13.8 forward (apicula bounds). Black 2's houses carry 2-6 units of
# wall over these doors and keep eaves, awnings and skirt roofs above them (b2tools/door_check.py b2). Ours had walls of
# 22-34 with eaves at 22-32 right in front of the doors: the doors stood in the roof (door_fix, 2026-10-11).
DOOR_TOP = {259: 32, 260: 32, 261: 32, 164: 32, 165: 33, 236: 33, 93: 29.8, 101: 30.1}
DOOR_WALL = 38            # wall height that holds a 32/33-unit house door with Black 2's lintel over it
PC_DOOR_ARC = [(-13.2, 4.2), (-10.2, 9.6), (-4.9, 13.0), (0.0, 13.8), (4.9, 13.0), (10.2, 9.6), (13.2, 4.2)]
PC_DOOR_BACK = 4.2        # door_pc's arc ends stand 4.2 in front of its origin: dz = front wall z - 4 sets them on the wall

def pc_door_hood(m, band, cap, ox, oz, y0=31.0, y1=36.0, out=1.5, band_rep=None):
    """Canopy over the curved sliding door (door_pc, res 93) whose origin is (ox, oz): a band following the door's arc
    `out` units outside it from y0 to y1 and a flat cap at y1 back to the arc's ends (on the wall), as Black 2's own
    Pokemon Center holds this door under its vestibule's canopy. band, cap: Regions; the cap is one copy of its region
    stretched over it and each band segment one cell (16 triangles in all: pack 0 is loaded whole into the field heap)."""
    pts = arc_offset(ox, oz, out)
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        L = math.hypot(xb - xa, zb - za)
        rect(m, band, (xa, y0, za), ((xb - xa) / L, 0, (zb - za) / L), (0, 1, 0), L, y1 - y0,
             (max(L, (band_rep or (L, 0))[0]), max(y1 - y0, (band_rep or (0, y1 - y0))[1])))
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    z0, z1 = min(p[1] for p in pts), max(p[1] for p in pts)
    face(m, cap, (x0, y1, 0), (1, 0, 0), (0, 0, -1), [(px - x0, -pz) for px, pz in pts], (x1 - x0, z1 - z0 + 1))

def arc_offset(ox, oz, out):
    """door_pc's front arc (left to right) at door origin (ox, oz), pushed `out` units outwards (vertex normals);
    the two ends stay on the line z = oz + PC_DOOR_BACK (the wall)."""
    P = [(ox + x, oz + z) for x, z in PC_DOOR_ARC]
    res = []
    for i, (x, z) in enumerate(P):
        a = P[max(i - 1, 0)]; b = P[min(i + 1, len(P) - 1)]
        tx, tz = b[0] - a[0], b[1] - a[1]; L = math.hypot(tx, tz)
        nx, nz = tz / L, -tx / L                          # outward (right of the left-to-right tangent: +z side)
        if nz < 0: nx, nz = -nx, -nz
        res.append((x + nx * out, z + nz * out))
    res[0] = (res[0][0], oz + PC_DOOR_BACK); res[-1] = (res[-1][0], oz + PC_DOOR_BACK)
    return res

# ------------------------------------------------------------------------------------------- faces the camera never sees
# Black 2's field camera looks north and down and never turns in Hoenn (no script uses EvCameraMoveTo; the zone camera is
# fixed): from the player's spot its eye is 185.7 up and 142 south (notes/NPC_LIMIT.md), so a building is seen from
# 40-60 degrees above the horizon, up to ~25 degrees to either side at the screen's edges. Pack 0 is read whole into the
# field heap, which the menu save shares (patches/area2_buildings.py save_headroom), so a pack-0 model keeps no triangle
# that faces away from every such view: north-facing walls, undersides, the back of a pipe (door_fix 2026-10-11).
_VIEWS = [(math.sin(math.radians(y)) * math.cos(math.radians(p)), math.sin(math.radians(p)),
           math.cos(math.radians(y)) * math.cos(math.radians(p))) for p in range(30, 71, 5) for y in range(-35, 36, 5)]

def cull_unseen(m, margin=0.02):
    """Drop the triangles of model m that face away from every view of the field camera (sampled 30-70 degrees down,
    35 degrees to either side: wider than the game's). Returns how many were dropped."""
    n = 0
    for mat in list(m.tris):
        keep = []
        for t in m.tris[mat]:
            a, b, c = t[0][:3], t[1][:3], t[2][:3]
            u = (b[0] - a[0], b[1] - a[1], b[2] - a[2]); v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
            N = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            L = math.sqrt(N[0] ** 2 + N[1] ** 2 + N[2] ** 2)
            if L < 1e-9: n += 1; continue                       # (degenerate: nothing to draw)
            if max((N[0] * w[0] + N[1] * w[1] + N[2] * w[2]) / L for w in _VIEWS) > margin: keep.append(t)
            else: n += 1
        if keep: m.tris[mat] = keep
        else: del m.tris[mat]
    return n

# --------------------------------------------------------------------------------------------------- dark doorways
# User 2026-10-18: "make sure when doors open it looks black so it looks like your entering a house and not just walking
# through walls". Black 2's door models open into the building (door_op / door_cl, 8 frames: the two BCA0 animations in
# the door's pack-0 info record, read with apicula): door_n_01-03 (259-261), door_t1_01/02 (164, 165), door_t2_h (236)
# and r34_door1 (101) swing 90 degrees inwards about a vertical hinge at their origin (the plate's right edge) while
# moving 3.5 back, so the whole plate (x -17..1 or -18..2) opens; door_pc (93) slides its two halves 62 degrees apart
# round the arc's centre (the door origin), opening the arc's middle (x -12.2..12.2). Behind the door Black 2's
# buildings have a hole in the front wall and a box about 16 deep drawn with one dark texel of a texture they already
# use (t2_build01, res 3: hole x -32..-13.9, y 3..37, box z 16..32 in t2_buil2's (41, 41, 41); pc_01, res 0: hole
# x -13.9..14.3, y 3.2..28.9 behind door_pc, box 16.3 deep in pc_kabe02's (33, 33, 33)), so an open door shows darkness.
# Ours had a solid wall behind every door: an opening door showed the wall ("walking through walls").
#
# door_recess() gives our models the same darkness for the price pack 0 can pay (it is read whole into the field heap,
# which the menu save shares: patches/area2_buildings.py save_headroom; a hole and Black 2's box cost ~600 B a model,
# 32 KB for the 52 door models, more than the save's margin; ToNsbmd writes ~28 B a triangle): ONE dark quad (2
# triangles, ~64 B) in a dark texel of one of the model's own textures (no new material: ~300 B), uniform like Black 2's
# box, so it looks the same from the camera:
#   'plane'  a dark quad between the wall and the door, 2 units (exterior_layers.MIN_GAP) from both: the door must stand
#            4 or more in front of its wall. The Center's door_pc does (its arc stands 9.8 out); the house doors stand
#            at dz = wall + 2 (data/buildings, dark doorways 2026-10-18; they were 0-1 unit nearer the wall).
#   'hole'   the doors with glass (164, 165, 236: their pane h_mado stands 1 behind to 0 in front of the plate's origin,
#            seen through the window, so the quad cannot stand in front of it): the hole is cut out of the wall (wall
#            cells merged back into rectangles first: fewest new triangles) and the quad stands in it, or 2+ units
#            behind the pane when the pane is nearer the wall than that (then a little bigger, for rays through the hole).
# The quad is as big as the CLOSED door hides from every view of the field camera (DOOR_VIEWS: rays sx = dx/dz,
# sy = dy/dz towards the eye, 185.7 up and 142 south of the player, notes/NPC_LIMIT.md: sy 0.55 with the door at the
# top of the screen, ~1 with the player at the door, 1.6 with the player 3 tiles behind the door's wall, 2.0 with 4;
# sx up to 1.0 at the screen's edges), together with what stands in front of it (canopies, posts, eaves): no dark rim
# shows round a closed door (exterior_check.py doors). Sampled every 0.5 unit; the largest such rectangle. A
# 'plane' quad keeps clear of every face between the wall and the door; a 'hole' takes them away with the wall. The
# open doorway is then 51-84% dark (the rest: a thin frame of wall the closed door's parallax needs; Black 2's own hole
# is bigger than its door, which its awning and the sunk plate hide).
DOOR_PARTS = {        # the closed door's opaque faces (door coordinates, quads counter-clockwise from the front)
    'plate': [((-17, 6, 2), (1, 6, 2), (1, 32, 2), (-17, 32, 2)), ((1, 6, 2), (1, 6, -2), (1, 32, -2), (1, 32, 2))],
    't1_01': [((-17, 6, 2), (1, 6, 2), (1, 32, 2), (-17, 32, 2)), ((1, 6, 2), (1, 6, -2), (1, 32, -2), (1, 32, 2)),
              ((-16, 6, -1), (0, 6, -1), (0, 32, -1), (-16, 32, -1))],          # (its window's glass: h_mado behind)
    't1_02': [((-18, 4, 2), (2, 4, 2), (2, 33, 2), (-18, 33, 2)), ((2, 4, 2), (2, 4, -1), (2, 33, -1), (2, 33, 2)),
              ((-16.3, 4, 0), (0.1, 4, 0), (0.1, 30.1, 0), (-16.3, 30.1, 0))],
    'r34': [((-20, 3.1, 1.9), (0, 3.1, 1.9), (0, 30.1, 1.9), (-20, 30.1, 1.9)),
            ((0, 3.1, 1.9), (0, 3.1, -0.2), (0, 30.1, -0.2), (0, 30.1, 1.9)),
            ((-20, 3.1, -0.2), (-20, 3.1, 1.9), (-20, 30.1, 1.9), (-20, 30.1, -0.2)),
            ((-20, 30.1, 1.9), (0, 30.1, 1.9), (0, 30.1, -0.2), (-20, 30.1, -0.2))],
    'pc': [((x0, 2.9, z0), (x1, 2.9, z1), (x1, 29.8, z1), (x0, 29.8, z0))
           for (x0, z0), (x1, z1) in zip(PC_DOOR_ARC, PC_DOOR_ARC[1:])],
}
DOOR_SHAPE = {259: 'plate', 260: 'plate', 261: 'plate', 164: 't1_01', 165: 't1_02', 236: 't1_02', 101: 'r34', 93: 'pc'}
DOOR_ZFACES = {'plate': (2.0,), 't1_01': (2.0, -1.0), 't1_02': (2.0, 0.0), 'r34': (1.9,), 'pc': (13.0,)}   # (its faces
                      # that face the camera within 11 degrees, exterior_check's layers rule: the arc's middle for door_pc)
DOOR_GLASS = {'t1_01', 't1_02'}
LAYER_GAP = 2.0            # exterior_layers.MIN_GAP
DOOR_VIEWS = [(sx / 8.0, sy) for sx in range(-8, 9, 2) for sy in (0.55, 0.7, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0)] + \
             [(sx / 8.0, sy) for sx in range(-7, 8, 2) for sy in (0.62, 0.92, 1.22, 1.62, 1.87)]   # (dense: gaps between a door
                                                     # and a post in front of it show only over a few degrees)
DARK_MAX = 60              # a texel this dark (largest channel) counts as darkness (Black 2's: 33-41)
DARK_FALLBACK = ('pc_kabe02', 'ext00', 38, 19)   # Black 2's Center recess texel, in pack 0's set (a new material: ~300 B)
HOLE_STEP = 0.5

def door_plane(door, dz, wall):
    """('plane' or 'hole', z of the dark quad) for door `door` at dz in front of a wall at z = wall (see above)."""
    shape = DOOR_SHAPE[door]
    zf = [dz + z for z in DOOR_ZFACES[shape]]
    if shape not in DOOR_GLASS and min(zf) >= wall + 2 * LAYER_GAP - 1e-6: return 'plane', wall + LAYER_GAP
    if min(zf) >= wall + LAYER_GAP - 1e-6: return 'hole', wall
    return 'hole', min(wall - LAYER_GAP, min(zf) - LAYER_GAP)

_DOOR_RECORDS = {}
def door_record(out, name):
    """(door, dx, dz) of model <out>/<name> from the registries data/buildings/*.json (model work/buildings/<town>/<name>
    .nsbmd, town = the out directory's name), or (65535, 0, 0) when no registry places it."""
    import os, json, glob
    if not _DOOR_RECORDS:
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        for f in sorted(glob.glob(os.path.join(root, 'data', 'buildings', '*.json'))):
            for r in json.load(open(f)).get('models', []):
                key = tuple(r['model'][:-len('.nsbmd')].split('/')[-2:])
                rec = (r['door'], r['dx'], r['dz'])
                assert _DOOR_RECORDS.get(key, rec) == rec, f'{key}: two door records {_DOOR_RECORDS[key]} / {rec}'
                _DOOR_RECORDS[key] = rec
    return _DOOR_RECORDS.get((os.path.basename(os.path.normpath(out)), name), (0xFFFF, 0, 0))

def _tri_n(P):
    u = [P[1][k] - P[0][k] for k in range(3)]; v = [P[2][k] - P[0][k] for k in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    return (n[0] / L, n[1] / L, n[2] / L) if L > 1e-9 else None

def _clip_attr(poly, axis, value, keep_greater):
    """Sutherland-Hodgman clip of a polygon of flat vertex lists [x, y, z, u, v, r, g, b] against coordinate `axis`
    = value; every attribute is interpolated along the cut edges (exact for a planar triangle's affine uv/colour)."""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ina = a[axis] >= value if keep_greater else a[axis] <= value
        inb = b[axis] >= value if keep_greater else b[axis] <= value
        if ina: out.append(a)
        if ina != inb:
            t = (value - a[axis]) / (b[axis] - a[axis])
            out.append([a[k] + t * (b[k] - a[k]) for k in range(len(a))])
    return out

def _outside_box(poly, box):
    """The pieces of convex polygon poly outside box (x0, x1, y0, y1, z0, z1): up to six convex polygons."""
    x0, x1, y0, y1, z0, z1 = box
    out = [_clip_attr(poly, 0, x0, False), _clip_attr(poly, 0, x1, True)]
    mid = _clip_attr(_clip_attr(poly, 0, x0, True), 0, x1, False)
    out += [_clip_attr(mid, 1, y0, False), _clip_attr(mid, 1, y1, True)]
    mid = _clip_attr(_clip_attr(mid, 1, y0, True), 1, y1, False)
    out += [_clip_attr(mid, 2, z0, False), _clip_attr(mid, 2, z1, True)]
    return [p for p in out if len(p) >= 3]

def _poly_area(p):
    s = [0.0, 0.0, 0.0]
    for i in range(1, len(p) - 1):
        u = [p[i][k] - p[0][k] for k in range(3)]; v = [p[i + 1][k] - p[0][k] for k in range(3)]
        s[0] += u[1] * v[2] - u[2] * v[1]; s[1] += u[2] * v[0] - u[0] * v[2]; s[2] += u[0] * v[1] - u[1] * v[0]
    return math.sqrt(s[0] ** 2 + s[1] ** 2 + s[2] ** 2) / 2

def _inside_open(t, box, eps=1e-4):
    """Does triangle t (vertex tuples) reach into the open box (not only touch its faces)?"""
    for k in range(3):
        lo, hi = min(v[k] for v in t), max(v[k] for v in t)
        if hi <= box[2 * k] + eps or lo >= box[2 * k + 1] - eps: return False
    return True

def _flat(v): return list(v[:5]) + list(v[5])
def _unflat(v): return tuple(v[:5]) + (tuple(v[5:8]),)

def _rect_cell(t1, t2):
    """If triangles t1, t2 (same material) together are one axis-aligned rectangle facing +z with one affine texture
    mapping and one colour (a face() cell): (x0, x1, y0, y1, z, f) with f(x, y) -> vertex; else None."""
    P = {tuple(round(c, 5) for c in v[:3]) for v in list(t1) + list(t2)}
    if len(P) != 4 or len({p[2] for p in P}) != 1: return None
    xs, ys = sorted({p[0] for p in P}), sorted({p[1] for p in P})
    if len(xs) != 2 or len(ys) != 2 or t1[0][5] != t2[0][5]: return None
    if len({v[5] for v in list(t1) + list(t2)}) != 1: return None
    n = _tri_n(t1)
    if not n or n[2] < 0.999 or (_tri_n(t2) or (0, 0, 0))[2] < 0.999: return None
    (ax, ay, _, au, av, _), (bx, by, _, bu, bv, _), (cx, cy, _, cu, cv, _) = t1
    den = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
    if abs(den) < 1e-9: return None
    def f(x, y):                                  # the affine uv map of t1 at (x, y)
        s = ((x - ax) * (cy - ay) - (cx - ax) * (y - ay)) / den
        r = ((bx - ax) * (y - ay) - (x - ax) * (by - ay)) / den
        return (x, y, t1[0][2], au + s * (bu - au) + r * (cu - au), av + s * (bv - av) + r * (cv - av), t1[0][5])
    if any(abs(f(v[0], v[1])[3] - v[3]) > 1e-4 or abs(f(v[0], v[1])[4] - v[4]) > 1e-4 for v in t2): return None
    return xs[0], xs[1], ys[0], ys[1], t1[0][2], f

def _cut_box(tris, box):
    """Triangles [(x, y, z, u, v, (r, g, b))] with everything inside box removed. A face() cell (two triangles making
    one rectangle) keeps up to four rectangles round the box (2 triangles each); other triangles are clipped one by one
    (up to six convex pieces each)."""
    keep, hit = [], []
    for t in tris: (hit if _inside_open(t, box) else keep).append(t)
    used = set()
    for i in range(len(hit)):
        if i in used: continue
        for j in range(i + 1, len(hit)):
            if j in used: continue
            c = _rect_cell(hit[i], hit[j])
            if c is None: continue
            x0, x1, y0, y1, z, f = c
            bx0, bx1, by0, by1 = max(x0, box[0]), min(x1, box[1]), max(y0, box[2]), min(y1, box[3])
            for rx0, rx1, ry0, ry1 in ((x0, bx0, y0, y1), (bx1, x1, y0, y1), (bx0, bx1, y0, by0), (bx0, bx1, by1, y1)):
                if rx1 - rx0 > 1e-4 and ry1 - ry0 > 1e-4:
                    q = [f(rx0, ry0), f(rx1, ry0), f(rx1, ry1), f(rx0, ry1)]
                    keep += [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]
            used |= {i, j}
            break
    for i, t in enumerate(hit):
        if i in used: continue
        for p in _outside_box([_flat(v) for v in t], box):
            if _poly_area(p) < 1e-4: continue
            for k in range(1, len(p) - 1):
                tri = [p[0], p[k], p[k + 1]]
                if _poly_area(tri) >= 1e-5: keep.append([_unflat(v) for v in tri])
    return keep

_IMAGES = {}
def _rgba(path):
    if path not in _IMAGES:
        import os
        import numpy as np
        from PIL import Image
        _IMAGES[path] = np.asarray(Image.open(path).convert('RGBA')).astype(int) if path and os.path.exists(path) else None
    return _IMAGES[path]

def _dark_texel(img):
    """(value, x, y) of the darkest opaque texel of an RGBA array, preferring one whose 3x3 neighbourhood is dark too."""
    import numpy as np
    lum = img[..., :3].max(-1) + (img[..., 3] < 255) * 1000
    pad = np.pad(lum, 1, mode='edge')
    nb = np.max([pad[1 + dy:1 + dy + lum.shape[0], 1 + dx:1 + dx + lum.shape[1]] for dy in (-1, 0, 1) for dx in (-1, 0, 1)], 0)
    score = np.where(nb <= DARK_MAX, lum, lum + 500)
    j, i = np.unravel_index(np.argmin(score), score.shape)
    return int(lum[j, i]), int(i), int(j)

def _opaque(img, uvs):
    """Are the texels under these uvs (vertices, edge midpoints, centre) all opaque? (alpha-tested crests, lattices
    and the translucent ground shadow are no occluders)"""
    if img is None: return True
    h, w = img.shape[:2]
    pts = list(uvs) + [((uvs[a][0] + uvs[b][0]) / 2, (uvs[a][1] + uvs[b][1]) / 2) for a, b in ((0, 1), (1, 2), (2, 0))]
    pts.append((sum(p[0] for p in uvs) / 3, sum(p[1] for p in uvs) / 3))
    for u, v in pts:
        x = min(int((u % 1.0) * w), w - 1); y = min(int(((1 - v) % 1.0) * h), h - 1)
        if img[y, x, 3] < 250: return False
    return True

def _ray_t(O, D, T):
    """Line O + t D (R,3) against triangles T (N,3,3): t (R,N) of the crossing (any sign), inf where none."""
    import numpy as np
    out = np.full((len(O), len(T)), np.inf)
    if not len(T): return out
    v0, e1, e2 = T[:, 0], T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
    for i in range(0, len(O), 512):
        o, d = O[i:i + 512, None, :], D[i:i + 512, None, :]
        p = np.cross(d, e2[None]); det = (e1[None] * p).sum(-1)
        ok = np.abs(det) > 1e-9
        inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        s = o - v0[None]
        u = (s * p).sum(-1) * inv
        q = np.cross(s, e1[None])
        v = (d * q).sum(-1) * inv
        t = (e2[None] * q).sum(-1) * inv
        hit = ok & (u >= -1e-6) & (v >= -1e-6) & (u + v <= 1 + 1e-6)
        out[i:i + 512] = np.where(hit, t, np.inf)
    return out

def _largest_rect(ok):
    """(r0, r1, c0, c1) of the largest all-True rectangle of a 2D bool array (inclusive), or None."""
    best, H = None, [0] * ok.shape[1]
    for r in range(ok.shape[0]):
        H = [H[c] + 1 if ok[r, c] else 0 for c in range(ok.shape[1])]
        stack = []
        for c in range(len(H) + 1):
            h = H[c] if c < len(H) else 0
            start = c
            while stack and stack[-1][1] >= h:
                s, sh = stack.pop()
                area = sh * (c - s)
                if sh and (best is None or area > best[0]): best = (area, r - sh + 1, r, s, c - 1)
                start = s
            stack.append((start, h))
    return best[1:] if best else None

def door_wall(m, door, dx, dz):
    """z of the wall door `door` at (dx, dz) stands in: the nearest surface of m facing the camera behind the door's
    front, at the door's centre (None: none)."""
    quads = DOOR_PARTS[DOOR_SHAPE[door]]
    cx = dx + (min(p[0] for q in quads for p in q) + max(p[0] for q in quads for p in q)) / 2
    cy = (min(p[1] for q in quads for p in q) + max(p[1] for q in quads for p in q)) / 2
    wall = None
    for mat, ts in m.tris.items():
        for t in ts:
            n = _tri_n(t)
            if not n or n[2] < 0.999: continue
            z = sum(v[2] for v in t) / 3
            if z >= dz + max(DOOR_ZFACES[DOOR_SHAPE[door]]) - 0.5 or (wall is not None and z <= wall): continue
            (ax, ay), (bx, by), (qx, qy) = [(v[0], v[1]) for v in t]
            den = (by - qy) * (ax - qx) + (qx - bx) * (ay - qy)
            if abs(den) < 1e-9: continue
            w0 = ((by - qy) * (cx - qx) + (qx - bx) * (cy - qy)) / den
            w1 = ((qy - ay) * (cx - qx) + (ax - qx) * (cy - qy)) / den
            if min(w0, w1, 1 - w0 - w1) >= -1e-6: wall = z
    return wall

def door_recess(m, door, dx, dz, image, min_size=(6.0, 8.0)):
    """The dark doorway behind door model `door` drawn at (dx, 0, dz) of model m (see above). image(texture) -> png
    path of a texture of m (None if unknown). Run after exterior_layers.separate (nothing moves the quad) and before
    cull_unseen. Returns dict(mode, wall, z, quad=(x0, x1, y0, y1), texel=(material, x, y, value)) or None (no door
    model, no wall behind it, or too little of it hidden)."""
    import numpy as np
    if door in (None, 0xFFFF) or door not in DOOR_SHAPE: return None
    quads = [[(x + dx, y, z + dz) for x, y, z in q] for q in DOOR_PARTS[DOOR_SHAPE[door]]]
    dtris = [t for q in quads for t in ([q[0], q[1], q[2]], [q[0], q[2], q[3]])]
    allp = [p for q in quads for p in q]
    X0, X1 = min(p[0] for p in allp), max(p[0] for p in allp)
    Y1 = max(p[1] for p in allp); zfront = max(p[2] for p in allp)
    wall = door_wall(m, door, dx, dz)
    if wall is None: return None
    mode, zd = door_plane(door, dz, wall)
    zq = zd if mode == 'plane' else wall                 # where the closed door must hide it: the quad, or the hole
    back = wall - zd if mode == 'hole' else 0.0          # (a quad behind the hole: rays go this far into it)
    floor = 0.0 if not back else 2.0 + back * max(sy for _, sy in DOOR_VIEWS) + 0.1   # (and stay over the ground shadow)
    zcut = zfront - 0.01
    # what hides it: the door, and the model's opaque faces in front of zq that face the eye, without the ones in the
    # door's box (cut away below where the quad comes)
    bdoor = (X0, X1, floor, Y1, zd - LAYER_GAP + 0.01, zcut)
    occ = []
    for mat, ts in m.tris.items():
        img = _rgba(image(mat)) if image else None
        for t in _cut_box([t for t in ts if max(v[2] for v in t) > zq + 1e-3], bdoor):
            if _tri_n(t) and _opaque(img, [v[3:5] for v in t]): occ.append([v[:3] for v in t])
    T = np.array(occ + dtris, float).reshape(-1, 3, 3)
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    is_door = np.arange(len(T)) >= len(occ)
    xs = np.arange(X0, X1 + 1e-6, HOLE_STEP); ys = np.arange(floor, Y1 + 1e-6, HOLE_STEP)
    gx, gy = np.meshgrid(xs, ys)
    # (sampled a hair off the grid: a ray exactly along the seam of two faces would find neither)
    Q = np.stack([gx.ravel() + 0.0137, gy.ravel() + 0.0071, np.full(gx.size, zq)], 1)
    covered = np.ones(len(Q), bool)
    for sx, sy in DOOR_VIEWS:
        d = np.array([sx, sy, 1.0])
        t = _ray_t(Q, np.repeat(d[None], len(Q), 0), T)
        valid = ((N @ d) > 1e-9)[None] & np.where(is_door[None], t > -back - 1e-3, t > 1e-4)
        covered &= (valid & np.isfinite(t)).any(1)
    if mode == 'plane':     # the quad keeps clear of every face between the wall and the door (nothing to cut: 2 triangles)
        free = np.ones(len(Q), bool)
        for ts in m.tris.values():
            for t in ts:
                P = np.array([v[:3] for v in t], float)
                if P[:, 2].max() <= wall + 0.01 or P[:, 2].min() >= zcut: continue
                n = np.cross(P[1] - P[0], P[2] - P[0])
                if abs(n[2]) < 0.05 * np.linalg.norm(n):        # (an upright face: its footprint, a hair wider)
                    lo, hi = P.min(0) - 0.25, P.max(0) + 0.25
                    free &= ~((Q[:, 0] >= lo[0]) & (Q[:, 0] <= hi[0]) & (Q[:, 1] >= lo[1]) & (Q[:, 1] <= hi[1]))
                    continue
                (ax, ay), (bx, by), (qx, qy) = P[:, :2]
                den = (by - qy) * (ax - qx) + (qx - bx) * (ay - qy)
                w0 = ((by - qy) * (Q[:, 0] - qx) + (qx - bx) * (Q[:, 1] - qy)) / den
                w1 = ((qy - ay) * (Q[:, 0] - qx) + (ax - qx) * (Q[:, 1] - qy)) / den
                free &= ~((w0 >= -0.02) & (w1 >= -0.02) & (1 - w0 - w1 >= -0.02))
        covered &= free
    rect = _largest_rect(covered.reshape(gx.shape))
    if rect is None: return None
    r0, r1, c0, c1 = rect
    hx0, hx1, hy0, hy1 = float(xs[c0]), float(xs[c1]), float(ys[r0]), float(ys[r1])
    if hx1 - hx0 < min_size[0] or hy1 - hy0 < min_size[1]: return None
    # cut away what stands in it (the wall, for a hole), then the quad: the darkest texel of the model's own textures
    box = (hx0, hx1, hy0, hy1, zd - LAYER_GAP + 0.01, zcut)
    for mat in list(m.tris):
        m.tris[mat] = _cut_box(m.tris[mat], box)
        if not m.tris[mat]: del m.tris[mat]
    best = None
    for mat in m.tris:
        img = _rgba(image(mat)) if image and mat != 'h_kage' else None
        if img is None: continue
        val, i, j = _dark_texel(img)
        if val <= DARK_MAX and (best is None or val < best[3]): best = (mat, i, j, val, img.shape)
    if best is None:
        img = _rgba(image(DARK_FALLBACK[0])) if image else None
        best = (DARK_FALLBACK[0], DARK_FALLBACK[2], DARK_FALLBACK[3], None, img.shape if img is not None else (32, 64))
    mat, i, j, val, (h, w) = best[0], best[1], best[2], best[3], best[4][:2]
    u, v = (i + 0.5) / w, 1 - (j + 0.5) / h
    sx = max(abs(a) for a, _ in DOOR_VIEWS); sy = max(b for _, b in DOOR_VIEWS)
    qx0, qx1, qy0 = hx0 - back * sx, hx1 + back * sx, hy0 - back * sy      # (a quad behind a hole: what rays reach)
    m.quad(mat, [(qx0, qy0, zd, u, v), (qx1, qy0, zd, u, v), (qx1, hy1, zd, u, v), (qx0, hy1, zd, u, v)])
    return dict(mode=mode, wall=wall, z=zd, quad=(qx0, qx1, qy0, hy1), hole=(hx0, hx1, hy0, hy1), texel=(mat, i, j, val))

RECESS_LOG = {}            # (town, model name) -> door_recess's result (for the checks)
def dark_doorway(m, out, name, image):
    """door_recess for model <out>/<name> with its door record from data/buildings (no record or no door: nothing)."""
    import os
    door, dx, dz = door_record(out, name)
    r = door_recess(m, door, dx, dz, image)
    RECESS_LOG[(os.path.basename(os.path.normpath(out)), name)] = r
    return r
