"""Close the 1-pixel cracks between ground polygons (Discord 2026-10-18: purple/blue lines across Slateport's square and
"all over the world while walking"; melonDS and the hardware, not DeSmuME).

The DS rasterizes every polygon from its own whole-pixel corners. Where a polygon's corner lies in the middle of a
neighbour's edge (a T-junction: merged ground rectangles next to per-row path, paving and fringe quads), the two
rasterized edges don't meet exactly and a 1-pixel crack opens along that edge, showing the background (purple/blue at
night) and moving with the camera. The v16.9 fix (build_chunk.path_cover, purple_lines 2026-10-13) put a floor under the
path tiles only; paved towns (ground.draw_paving), sand, grass rectangles and module edges kept theirs.

fix(m) removes the T-junctions themselves: every triangle edge that has another vertex of the cell's terrain lying on it
(inside the edge, in 3D) is split there, so both sides of every shared edge have the same vertices. The triangle is
re-triangulated from the opposite corner (points on one edge) or from its centroid (points on several edges);
texture coordinates and colours are interpolated, positions are the shared vertex's own. Nothing moves, no layer is
added (b2tools/exterior_layers.py's 2-unit rule is untouched); the cost is a few more triangles per cell.

    python3 tjunction.py WORLD_DIR [cx_cz ...]     (report: T-junctions per cell in a built world, before/after fix)
"""
import math
from collections import defaultdict

EPS = 0.05          # a vertex this close to an edge (model units) lies on it
GRID = 16.0         # spatial hash cell (one tile)


def _key(p):
    return (round(p[0], 3), round(p[1], 3), round(p[2], 3))


def _points(m):
    """Unique vertex positions of model m and a spatial hash (x, z cells) over them."""
    pts = {}
    for tris in m.tris.values():
        for t in tris:
            for v in t: pts[_key(v)] = (v[0], v[1], v[2])
    grid = defaultdict(list)
    for p in pts.values():
        grid[(math.floor(p[0] / GRID), math.floor(p[2] / GRID))].append(p)
    return grid


def _on_edge(grid, a, b):
    """Vertices strictly inside segment a-b (3D, within EPS), as [(s, p)] sorted by s."""
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    L2 = dx * dx + dy * dy + dz * dz
    if L2 < 1e-6: return []
    out = []
    x0, x1 = sorted((a[0], b[0])); z0, z1 = sorted((a[2], b[2]))
    for gx in range(math.floor((x0 - EPS) / GRID), math.floor((x1 + EPS) / GRID) + 1):
        for gz in range(math.floor((z0 - EPS) / GRID), math.floor((z1 + EPS) / GRID) + 1):
            for p in grid.get((gx, gz), ()):
                if not (x0 - EPS <= p[0] <= x1 + EPS and z0 - EPS <= p[2] <= z1 + EPS): continue
                s = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy + (p[2] - a[2]) * dz) / L2
                if s <= 1e-4 or s >= 1 - 1e-4: continue
                cx, cy, cz = a[0] + s * dx - p[0], a[1] + s * dy - p[1], a[2] + s * dz - p[2]
                if cx * cx + cy * cy + cz * cz < EPS * EPS: out.append((s, p))
    out.sort()
    dedup = []
    for s, p in out:
        if not dedup or abs(s - dedup[-1][0]) * math.sqrt(L2) > 1e-3: dedup.append((s, p))
    return dedup


def _lerp(va, vb, s, p):
    """Vertex at fraction s from va to vb, placed exactly at p: uv and colour interpolated."""
    ca, cb = va[5], vb[5]
    return (p[0], p[1], p[2], va[3] + s * (vb[3] - va[3]), va[4] + s * (vb[4] - va[4]),
            tuple(ca[i] + s * (cb[i] - ca[i]) for i in range(len(ca))))


def _flat(t, ny_min=0.7):
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = [v[:3] for v in t]
    ux, uy, uz, vx, vy, vz = x1 - x0, y1 - y0, z1 - z0, x2 - x0, y2 - y0, z2 - z0
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    L = math.sqrt(nx * nx + ny * ny + nz * nz)
    return L > 1e-9 and abs(ny) / L > ny_min


def fix(m, skip=(), flat_only=True):
    """Split every triangle edge of model m at the terrain vertices lying on it (in place). skip: materials left alone
    (and not used as split points), e.g. alpha cards that never share an edge with the ground. flat_only: only the
    ground (triangles within ~45 degrees of horizontal) is split, at the ground's own vertices: the cracks players see
    are on the ground, and the cliffs' and walls' T-junctions would cost as many triangles again (world_rel: 50,111
    ground T-junctions -> 267 for +15% triangles; everything: +23%). Returns (edges split, triangles added)."""
    work = {k: v for k, v in m.tris.items() if k not in skip}
    if flat_only:
        rest = {k: [t for t in v if not _flat(t)] for k, v in work.items()}
        work = {k: [t for t in v if _flat(t)] for k, v in work.items()}
        s, a = fix(type('M', (), {'tris': work})(), (), False)
        for k in work: m.tris[k] = work[k] + rest[k]
        return s, a
    if not work: return 0, 0
    tmp = type('M', (), {})(); tmp.tris = work
    grid = _points(tmp)
    split = added = 0
    for mat, tris in work.items():
        out = []
        for t in tris:
            extra = [_on_edge(grid, t[e], t[(e + 1) % 3]) for e in range(3)]
            n = sum(len(x) for x in extra)
            if not n:
                out.append(t); continue
            split += sum(1 for x in extra if x)
            edges = [e for e in range(3) if extra[e]]
            if len(edges) == 1:              # fan from the opposite corner
                e = edges[0]
                a, b, c = t[e], t[(e + 1) % 3], t[(e + 2) % 3]
                chain = [a] + [_lerp(a, b, s, p) for s, p in extra[e]] + [b]
                for i in range(len(chain) - 1):
                    out.append([chain[i], chain[i + 1], c])
                added += len(chain) - 2
            else:                            # fan from the centroid
                poly = []
                for e in range(3):
                    a, b = t[e], t[(e + 1) % 3]
                    poly.append(a)
                    poly += [_lerp(a, b, s, p) for s, p in extra[e]]
                k = len(t[0][5])
                ctr = tuple(sum(v[i] for v in t) / 3 for i in range(5)) + (tuple(sum(v[5][i] for v in t) / 3 for i in range(k)),)
                for i in range(len(poly)):
                    out.append([poly[i], poly[(i + 1) % len(poly)], ctr])
                added += len(poly) - 1
        m.tris[mat] = out
    return split, added


def count(m, skip=()):
    """T-junctions of model m: (triangle edge, vertex inside it) pairs."""
    work = {k: v for k, v in m.tris.items() if k not in skip}
    tmp = type('M', (), {})(); tmp.tris = work
    grid = _points(tmp)
    return sum(len(_on_edge(grid, t[e], t[(e + 1) % 3])) for tris in work.values() for t in tris for e in range(3))


def _load(path):
    """A built terrain.dae as a dae.Model-like object (white vertex colours)."""
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from exterior_check import load_dae
    m = type('M', (), {})(); m.tris = {}
    for mat, img, P, UV, A in load_dae(path):
        m.tris.setdefault(mat, []).extend(
            [[(float(P[i][j][0]), float(P[i][j][1]), float(P[i][j][2]), float(UV[i][j][0]), float(UV[i][j][1]), (1.0, 1.0, 1.0))
              for j in range(3)] for i in range(len(P))])
    return m


if __name__ == '__main__':
    import os, sys, glob, time
    wd = sys.argv[1]
    cells = sys.argv[2:] or sorted(os.path.basename(d) for d in glob.glob(os.path.join(wd, 'cells', '*')))
    tot_b = tot_a = tot_t = tot_n = 0
    for c in cells:
        p = os.path.join(wd, 'cells', c, 'terrain.dae')
        if not os.path.exists(p): continue
        m = _load(p)
        nt = sum(len(v) for v in m.tris.values())
        t0 = time.time(); b = count(m); s, a = fix(m); after = count(m)
        tot_b += b; tot_a += after; tot_t += a; tot_n += nt
        if len(cells) <= 12 or b: print(f'{c}: {nt} tris, T-junctions {b} -> {after}, +{a} tris ({time.time() - t0:.1f}s)')
    print(f'total: T-junctions {tot_b} -> {tot_a}; triangles {tot_n} -> {tot_n + tot_t} (+{100 * tot_t / max(tot_n, 1):.1f}%)')
