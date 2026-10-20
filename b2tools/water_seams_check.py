"""Water seams check (water_seams 2026-10-19; terrain/water.py _seam_layers): the DS opens 1-pixel cracks along the
edges inside a surface (T-junctions, and even shared edges), so every edge inside a water sheet (ike01, sea_mizu1_1)
or floor (mizu_sita2, sea_mizu1) must lie inside another polygon of the same layer: a polygon of the same material in
the same plane (a sheet: the seam sheet, or the next cell's sheet reaching over the border; the DS draws no
translucent pixel over one of the same polygon ID, nsbmd_fix.water_materials) or, for a floor, SEAM_DROP under it.
Cells are read with their 8 neighbours (the main matrix; other frames' cells alone).

    python3 water_seams_check.py WORLD [--before WORLD0] [cx_cz ...]

Per cell and material: the length of edges inside the layer (both sides covered), how much of it is backed (a
polygon of the layer or the one under it holds the point EPS clear of its own edges), and the T-junctions (a vertex
inside another triangle's edge of the same layer, across cells too). With --before (the same world built without the
seam layers): the area the new layers add where nothing opaque covers it (water or floor showing where it did not).
"""
import os, sys, glob, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exterior_check import load_dae

SHEETS = ('ike01', 'sea_mizu1_1')
FLOORS = ('mizu_sita2', 'sea_mizu1')
DROP = 4.0            # water.py SEAM_DROP
EPS = 2.0             # a crack point is backed when a polygon holds it this far (about 2 pixels) inside its edges
STEP = 1.0            # edge sample spacing
SEE_THROUGH = set(SHEETS)
_alpha_cache = {}

def _see_through(d, mat):
    """Materials that do not hide what is under them: the translucent sheets and textures with clear texels."""
    if mat in SEE_THROUGH: return True
    p = os.path.join(d, mat + '.png')
    if p not in _alpha_cache:
        try:
            from PIL import Image
            im = Image.open(p)
            _alpha_cache[p] = im.mode in ('RGBA', 'LA', 'P') and np.array(im.convert('RGBA'))[:, :, 3].min() < 255
        except Exception:
            _alpha_cache[p] = False
    return _alpha_cache[p]

class Cells:
    def __init__(self, wd):
        self.wd = wd; self._c = {}
        self.names = sorted(os.path.basename(x) for x in glob.glob(os.path.join(wd, 'cells', '*')))
    def get(self, name):
        """{material: P (N,3,3) in world units} of a cell directory (main cells at their matrix position)."""
        if name not in self._c:
            p = os.path.join(self.wd, 'cells', name, 'terrain.dae')
            out = {}
            if os.path.exists(p):
                parts = name.split('_')
                cx, cz = (int(parts[0]), int(parts[1])) if len(parts) == 2 and all(s.isdigit() for s in parts) else (0, 0)
                for mat, img, P, UV, A in load_dae(p):
                    Q = np.array(P, float).copy()
                    Q[:, :, 0] += 256 + cx * 512; Q[:, :, 2] += 256 + cz * 512
                    out[mat] = np.concatenate([out[mat], Q]) if mat in out else Q
            self._c[name] = out
        return self._c[name]
    def around(self, name):
        parts = name.split('_')
        if not (len(parts) == 2 and all(s.isdigit() for s in parts)): return [name]
        cx, cz = int(parts[0]), int(parts[1])
        return [f'{cx + dx:02d}_{cz + dz:02d}' for dz in (-1, 0, 1) for dx in (-1, 0, 1)
                if f'{cx + dx:02d}_{cz + dz:02d}' in self.names]

def _ccw(T):
    """Triangles (K,3,2) wound counter-clockwise (in x, z)."""
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    cr = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    T = T.copy(); T[cr < 0] = T[cr < 0][:, ::-1]
    return T[np.abs(cr) > 1e-9]

def _inside(pts, T, margin):
    """For points (M,2) and ccw triangles (K,3,2): a point lies inside some triangle with every edge >= margin away."""
    if not len(T) or not len(pts): return np.zeros(len(pts), bool)
    out = np.zeros(len(pts), bool)
    e0, e1 = T, np.roll(T, -1, axis=1)
    d = e1 - e0; L = np.maximum(np.linalg.norm(d, axis=2), 1e-9)
    for i in range(0, len(pts), 1500):
        p = pts[i:i + 1500][:, None, None, :]
        s = (d[None, :, :, 0] * (p[..., 1] - e0[None, :, :, 1]) - d[None, :, :, 1] * (p[..., 0] - e0[None, :, :, 0])) / L[None]
        out[i:i + 1500] = (s >= margin).all(2).any(1)
    return out

def _plane(P, y, tol=0.01):
    return P[(np.abs(P[:, :, 1] - y) < tol).all(1)] if len(P) else P

def _levels(P):
    flat = (np.ptp(P[:, :, 1], axis=1) < 0.01)
    return sorted(set(np.round(P[flat][:, 0, 1], 2)))

LINE = 16.0           # an unbacked run this long (units, a tile) is a line; shorter ones are dashes and points where two
                      # layers' edges cross (at a point, or at a shallow angle)
BANK_TOPS = ('gake1_1', 'gake1_0', 'sea_simi.1', 'sea_gake01')     # first layers of water.py's bank profiles

def _samples(own, segments=False):
    """Edge samples of triangles own (N,3,3) (or segments (N,2,3)): per edge an array of points (x, z) and the edge's
    unit normal."""
    out = []
    for t in own:
        for k in range(1 if segments else 3):
            a, b = t[k][[0, 2]], t[(k + 1) % len(t)][[0, 2]]
            L = float(np.hypot(*(b - a)))
            if L < 1e-6: continue
            n = max(int(L / STEP), 1)
            s = (np.arange(1, n) / n)[:, None] if n > 1 else np.array([[0.5]])
            out.append((a + s * (b - a), np.array([-(b - a)[1] / L, (b - a)[0] / L])))
    return out

def _runs(edges, inner_of, ok_of):
    """(inner length, unbacked length, unbacked line length, line count) over the edges' samples."""
    inner = bad = line = 0.0; nl = 0
    for (pts, nrm), inn, ok in zip(edges, inner_of, ok_of):
        inner += inn.sum() * STEP
        miss = inn & ~ok
        bad += miss.sum() * STEP
        r = 0
        for m in list(miss) + [False]:
            if m: r += 1
            else:
                if r * STEP > LINE: line += r * STEP; nl += 1
                r = 0
    return inner, bad, line, nl

def check_cell(cells, name, before=None):
    me = cells.get(name)
    near = [cells.get(n) for n in cells.around(name)]
    was = before.get(name) if before is not None else None
    rows = []
    for mat in SHEETS + FLOORS:
        if mat not in me: continue
        allP = np.concatenate([c[mat] for c in near if mat in c])
        for y in _levels(me[mat]):
            if was is not None and mat in FLOORS and (mat not in was or y not in _levels(was[mat])): continue  # (a seam floor)
            S = _ccw(_plane(allP, y)[:, :, [0, 2]])
            back = S if mat in SHEETS else np.concatenate([S, _ccw(_plane(allP, y - DROP)[:, :, [0, 2]])])
            edges = _samples(_plane(me[mat], y))
            if not edges: continue
            inner_of = [_inside(p + 0.3 * n, S, 0) & _inside(p - 0.3 * n, S, 0) for p, n in edges]
            ok_of = [_inside(p, back, EPS) for p, n in edges]
            # T-junctions: a vertex of the layer inside another of its triangles' edges (any cell)
            V = np.unique(np.round(S.reshape(-1, 2), 3), axis=0)
            tj = 0
            for t in _plane(me[mat], y)[:, :, [0, 2]]:
                for k in range(3):
                    a, b = t[k], t[(k + 1) % 3]
                    d = b - a; L2 = float(d @ d)
                    if L2 < 1e-6: continue
                    s = ((V - a) @ d) / L2
                    cr = np.abs(d[0] * (V[:, 1] - a[1]) - d[1] * (V[:, 0] - a[0])) / math.sqrt(L2)
                    tj += int(((s > 1e-4) & (s < 1 - 1e-4) & (cr < 0.05)).sum())
            inner, bad, line, nl = _runs(edges, inner_of, ok_of)
            rows.append(dict(cell=name, mat=mat, y=y, inner=inner, unbacked=bad, line=line, lines=nl, tj=tj))
    # bank tops: the top edge of a bank's first layer (where it meets the land's ground) needs an opaque surface
    # 1-8 under it, 1 unit clear of its own edges on both sides (water.py _bank_seams' strip)
    for mat in BANK_TOPS:
        if mat not in me: continue
        tops = []
        sheets = np.concatenate([c[m2] for c in near for m2 in SHEETS if m2 in c] or [np.zeros((0, 3, 3))])
        for t in me[mat]:
            ys = t[:, 1]; top = ys.max()
            if np.ptp(ys) < 0.5: continue                       # (a flat piece: not a slope)
            for k in range(3):
                a, b = t[k], t[(k + 1) % 3]
                if not (abs(a[1] - top) < 1e-3 and abs(b[1] - top) < 1e-3): continue
                # (a water bank, not a cliff's lip: a water sheet 7-12 under the top, 10 units down the slope)
                c = t[(k + 2) % 3]; mid = (a + b) / 2; dvec = (c - mid)[[0, 2]]
                L = np.linalg.norm(dvec)
                if L < 1e-6: continue
                probe = mid[[0, 2]] + dvec / L * 10
                lev = sheets[(sheets[:, 0, 1] <= top - 7) & (sheets[:, 0, 1] >= top - 12)]
                if len(lev) and _inside(probe[None], _ccw(lev[:, :, [0, 2]]), 0)[0]: tops.append((a, b, top))
        if not tops: continue
        opaque = []
        for c in near:
            for m2, P in c.items():
                if m2 in SHEETS or m2 in FLOORS or _see_through(os.path.join(cells.wd, 'cells', name), m2): continue
                flat = P[np.ptp(P[:, :, 1], axis=1) < 0.01]
                if len(flat): opaque.append(flat)
        opaque = np.concatenate(opaque) if opaque else np.zeros((0, 3, 3))
        inner = bad = line = 0.0; nl = 0
        for top in sorted({round(t[2], 2) for t in tops}):
            under = _ccw(opaque[(opaque[:, 0, 1] <= top - 1) & (opaque[:, 0, 1] >= top - 8)][:, :, [0, 2]])
            edges = _samples(np.array([[a, b] for a, b, y in tops if round(y, 2) == top]), segments=True)
            inner_of = [np.ones(len(p), bool) for p, n in edges]
            ok_of = [_inside(p, under, 1.0) for p, n in edges]
            r = _runs(edges, inner_of, ok_of)
            inner += r[0]; bad += r[1]; line += r[2]; nl += r[3]
        rows.append(dict(cell=name, mat=mat + ' (bank top)', y=None, inner=inner, unbacked=bad, line=line, lines=nl, tj=0))
    rows.append(_ground_over_water(cells, name, me))
    return rows, _exposed(cells, name, me, near, before)

GROUND = ('grass01ax', 'gake_michi')       # water.py GROUND: flat ground that must not lie over water
SURF = {0x3d, 0x3e, 0x3f, 0x40, 0x42, 0x43, 0x94, 0x95, 0x96, 0x97, 0x17}

def _ground_over_water(cells, name, me):
    """Flat ground triangles (GROUND) over a surf-water tile of the cell's collision (more than 0.5 unit^2 inside the
    tile): water.py cuts the ground there (cut_ground_now). Reported as 'unbacked' area, 'lines' = triangles."""
    from exterior_layers import _clip, _area
    parts = name.split('_')
    if not (len(parts) == 2 and all(x.isdigit() for x in parts)): return dict(cell=name, mat='ground over water', y=None,
                                                                              inner=0, unbacked=0, line=0, lines=0, tj=0)
    cx, cz = int(parts[0]), int(parts[1])
    b = open(os.path.join(cells.wd, 'cells', name, 'collision.per'), 'rb').read()
    import struct
    wet = {(tx, tz) for tz in range(32) for tx in range(32)
           if struct.unpack_from('<HHHH', b, 4 + 8 * (tz * 32 + tx))[2] in SURF}
    # (the water's collision height on each wet tile (MAP_HEIGHT_OFFSET_TABLE, terrain/heights.py): ground over it at
    # the land's height (8 over it) counts; water.py's bank strips (2 over it, _bank_seams) reach over the tile on purpose)
    from terrain import heights as HT
    ny = HT.NORMALS[0][1]
    sheet = {(tx, tz): -HT.OFFS[struct.unpack_from('<HHHH', b, 4 + 8 * (tz * 32 + tx))[1]] / ny for tx, tz in wet}
    bad = area = 0
    for mat in GROUND:
        if mat not in me: continue
        for t in me[mat]:
            if np.ptp(t[:, 1]) > 0.01: continue
            tri = [((v[0] - cx * 512) / 16, (v[2] - cz * 512) / 16) for v in t]      # (cell tile units)
            x0, x1 = int(min(p[0] for p in tri)), int(max(p[0] for p in tri))
            z0, z1 = int(min(p[1] for p in tri)), int(max(p[1] for p in tri))
            a = 0.0
            for tx in range(max(x0, 0), min(x1, 31) + 1):
                for tz in range(max(z0, 0), min(z1, 31) + 1):
                    if (tx, tz) not in wet or t[0, 1] < sheet.get((tx, tz), -1e9) + 6.5: continue
                    poly = tri if (tri[1][0] - tri[0][0]) * (tri[2][1] - tri[0][1]) - (tri[1][1] - tri[0][1]) * (tri[2][0] - tri[0][0]) > 0 else tri[::-1]
                    sq = [(tx + .05, tz + .05), (tx + .95, tz + .05), (tx + .95, tz + .95), (tx + .05, tz + .95)]
                    for k in range(4):
                        poly = _clip(poly, sq[k], sq[(k + 1) % 4]) if poly else poly
                    a += _area(poly) * 256 if poly and len(poly) >= 3 else 0
            if a > 0.5: bad += 1; area += a
    return dict(cell=name, mat='ground over water', y=None, inner=0, unbacked=area, line=area, lines=bad, tj=0)

def _exposed(cells, name, me, near, before):
    exposed = []
    if before is not None:
        b_near = [before.get(n) for n in before.around(name)]
        for mat in SHEETS + FLOORS + GROUND:          # (GROUND: water.py's bank strips under the land)
            if mat not in me: continue
            for y in _levels(me[mat]):
                own = _ccw(_plane(me[mat], y)[:, :, [0, 2]])
                b_all = [c[mat] for c in b_near if mat in c]
                was = _ccw(_plane(np.concatenate(b_all), y)[:, :, [0, 2]]) if b_all else np.zeros((0, 3, 2))
                # grid points (4 units) of the layer that the same layer before did not cover
                lo, hi = own.reshape(-1, 2).min(0), own.reshape(-1, 2).max(0)
                gx = np.arange(math.floor(lo[0] / 4) * 4 + 2, hi[0], 4); gz = np.arange(math.floor(lo[1] / 4) * 4 + 2, hi[1], 4)
                G = np.stack(np.meshgrid(gx, gz), -1).reshape(-1, 2)
                G = G[_inside(G, own, 0.01)]
                G = G[~_inside(G, was, -0.01)]
                if not len(G): continue
                hidden = np.zeros(len(G), bool)
                d = os.path.join(cells.wd, 'cells', name)
                for c in near:
                    for m2, P in c.items():
                        if _see_through(d, m2): continue
                        sel = P[(P[:, :, 1].min(1) > y + 0.5) | (P[:, :, 1].max(1) > y + 0.5)]
                        if not len(sel): continue
                        T3 = sel
                        # (the surface must be over the point: interpolate its height there)
                        T2 = _ccw(T3[:, :, [0, 2]])
                        if not len(T2): continue
                        hit = _inside(G[~hidden], T2, -0.01)     # (a point on a shared edge is covered)
                        idx = np.nonzero(~hidden)[0][hit]
                        hidden[idx] = True      # (approximation: any opaque triangle reaching over y + 0.5 there)
                if (~hidden).any():
                    exposed.append(dict(cell=name, mat=mat, y=y, area=float((~hidden).sum() * 16),
                                        at=[tuple(np.round(p / 16, 1)) for p in G[~hidden][:4]]))
    return exposed

if __name__ == '__main__':
    args = sys.argv[1:]
    bw = None
    if '--before' in args:
        i = args.index('--before'); bw = Cells(args[i + 1]); del args[i:i + 2]
    cells = Cells(args[0])
    names = args[1:] or cells.names
    tot = {}
    for n in names:
        rows, exposed = check_cell(cells, n, bw)
        for r in rows:
            t = tot.setdefault(r['mat'], [0, 0, 0, 0, 0])
            t[0] += r['inner']; t[1] += r['unbacked']; t[2] += r['line']; t[3] += r['lines']; t[4] += r['tj']
            if r['lines'] or len(names) <= 4:
                print(f"{n} {r['mat']} y {r['y']}: inner edges {r['inner']:.0f}, unbacked {r['unbacked']:.0f} "
                      f"({r['lines']} lines, {r['line']:.0f}), T-junctions {r['tj']}")
        for e in exposed:
            print(f"EXPOSED {n} {e['mat']} y {e['y']}: {e['area']:.0f} units^2 at tiles {e['at']}")
    for mat, (a, b, c, k, tj) in tot.items():
        print(f'total {mat}: inner edge length {a:.0f}, unbacked {b:.0f} ({100 * b / max(a, 1):.1f}%), '
              f'of it lines (runs > {LINE:.0f} units) {c:.0f} in {k}, T-junctions {tj}')
