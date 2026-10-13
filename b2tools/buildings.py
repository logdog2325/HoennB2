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
