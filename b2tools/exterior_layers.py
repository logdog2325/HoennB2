"""Pull apart coplanar layers inside a building model before it is written (exterior sweep, 2026-10-06).

    from exterior_layers import separate
    separate(m)            # m: dae.Model; moves the front one of every pair of parallel, overlapping pieces

Our town models put windows, frames, posts, bands and caps 0-0.85 units in front of the walls and roofs they sit on
(b2tools/exterior_check.py found 100+ such pairs in 40 models). Pieces that close depth-fight in melonDS. Black 2's
own building models keep such layers about 1 unit apart and more (pack 0-6: 29 pairs at exactly 1.0, most others
1.0-1.9; measured with exterior_check.layer_pairs on apicula conversions), so MIN_GAP is 1.0 here; the terrain keeps
2 units (its polygons are chunk-sized).

A piece = triangles of one material in one plane that share vertices. For every pair of pieces facing the same way
whose projections overlap, the one in front (along their normal; the smaller one when they are level) moves out
until it is MIN_GAP clear of the one behind; pieces in front of a moved piece follow (chains like wall, glass,
frame). Vertices of other faces that touch a moved piece move with it (a post's sides stretch to its front face), so
no gaps open. Texture coordinates stay, nothing is added or removed."""
import math

MIN_GAP = 1.0
MAX_PUSH = 6.0

def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def _clip(poly, a, b):
    """Keep the part of convex polygon poly left of the directed line a -> b (2D)."""
    out = []
    side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        sp, sq = side(p), side(q)
        if sp >= 0: out.append(p)
        if (sp >= 0) != (sq >= 0):
            t = sp / (sp - sq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out

def _area(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly)))) / 2 if len(poly) >= 3 else 0.0

def _overlap(t1, t2):
    """Overlap area of two 2D triangles."""
    def ccw(t): return t if (t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) - (t[1][1] - t[0][1]) * (t[2][0] - t[0][0]) >= 0 else t[::-1]
    t1, t2 = ccw(t1), ccw(t2)
    poly = list(t1)
    for i in range(3):
        poly = _clip(poly, t2[i], t2[(i + 1) % 3])
        if not poly: return 0.0
    return _area(poly)

def separate(m, min_gap=MIN_GAP, max_push=MAX_PUSH, report=None, rounds=4):
    """Move overlapping parallel pieces of model m apart (in place), again until nothing moves (a pushed piece can
    meet one that was in front of it). Returns the number of pieces moved."""
    total = 0
    for _ in range(rounds):
        n = _separate(m, min_gap, max_push)
        total += n
        if not n: break
    if report is not None and total: report.append(f'{m.name}: {total} pieces moved apart')
    return total

def _separate(m, min_gap, max_push):
    tri = []                                         # (material, index, normal, offset, points)
    for mat, ts in m.tris.items():
        for i, t in enumerate(ts):
            P = [tuple(v[:3]) for v in t]
            n = _cross(_sub(P[1], P[0]), _sub(P[2], P[0])); L = math.sqrt(_dot(n, n))
            if L < 1e-6: continue
            n = (n[0] / L, n[1] / L, n[2] / L)
            tri.append((mat, i, n, _dot(n, P[0]), P))
    # pieces: union-find over same-material, same-plane triangles sharing a vertex
    parent = list(range(len(tri)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    by_vertex = {}
    for k, (mat, i, n, d, P) in enumerate(tri):
        for p in P: by_vertex.setdefault((mat, tuple(round(c, 3) for c in p)), []).append(k)
    for ks in by_vertex.values():
        for k in ks[1:]:
            a, b = tri[ks[0]], tri[k]
            if _dot(a[2], b[2]) > 0.999 and abs(a[3] - b[3]) < 0.01: parent[find(k)] = find(ks[0])
    pieces = {}
    for k in range(len(tri)): pieces.setdefault(find(k), []).append(k)
    pieces = list(pieces.values())
    def basis(n):
        u = _cross(n, (0, 1, 0)) if abs(n[1]) < 0.9 else _cross(n, (1, 0, 0))
        L = math.sqrt(_dot(u, u)); u = (u[0] / L, u[1] / L, u[2] / L)
        return u, _cross(n, u)
    info = []
    for ks in pieces:
        n = tri[ks[0]][2]; d = sum(tri[k][3] for k in ks) / len(ks)
        area = sum(math.sqrt(_dot(*(2 * [_cross(_sub(tri[k][4][1], tri[k][4][0]), _sub(tri[k][4][2], tri[k][4][0]))]))) / 2 for k in ks)
        info.append(dict(ks=ks, n=n, d=d, area=area, shift=0.0))
    # pairs that overlap: same facing, closer than min_gap where they overlap (measured at the corners of each
    # overlap polygon along the back piece's normal, so slightly tilted pieces are judged where they meet)
    def overlap_poly(t1, t2):
        def ccw(t): return t if (t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) - (t[1][1] - t[0][1]) * (t[2][0] - t[0][0]) >= 0 else t[::-1]
        poly = list(ccw(t1)); t2 = ccw(t2)
        for i in range(3):
            poly = _clip(poly, t2[i], t2[(i + 1) % 3])
            if not poly: return []
        return poly if _area(poly) > 0.5 else []
    behind = {a: [] for a in range(len(info))}
    gaps = {}
    for a in range(len(info)):
        A = info[a]
        u, v = basis(A['n'])
        ta = [[(_dot(p, u), _dot(p, v)) for p in tri[k][4]] for k in A['ks']]
        for b in range(len(info)):
            if a == b: continue
            B = info[b]
            nn = _dot(A['n'], B['n'])
            if nn < 0.98: continue
            tb = [[(_dot(p, u), _dot(p, v)) for p in tri[k][4]] for k in B['ks']]
            g = None
            for x in ta:
                for y in tb:
                    for (pu, pv) in overlap_poly(x, y):
                        q = tuple(A['d'] * A['n'][i] + pu * u[i] + pv * v[i] for i in range(3))
                        t = (B['d'] - _dot(B['n'], q)) / nn          # from A's plane to B's along A's normal
                        g = t if g is None else min(g, t)
            if g is None or not (-1e-3 <= g < min_gap): continue
            if abs(g) <= 1e-3 and (B['area'], b) >= (A['area'], a): continue    # level: the smaller one is in front
            behind[b].append(a); gaps[(a, b)] = g
    # push front pieces out, nearest first, so chains (wall, glass, frame) stack up
    def depth(b, seen=()):
        return 0 if not behind[b] else 1 + max(depth(a, seen + (b,)) for a in behind[b] if a not in seen + (b,))
    moved = 0
    for b in sorted(range(len(info)), key=depth):
        need = 0.0
        for a in behind[b]:
            need = max(need, info[a]['shift'] + min_gap - gaps[(a, b)])
        if need > 1e-6:
            info[b]['shift'] = min(need, max_push); moved += 1
    # apply: a moved piece's own vertices, and the touching vertices of faces that are not parallel to it
    moves = {}
    for P in info:
        if P['shift'] <= 0: continue
        dv = tuple(c * P['shift'] for c in P['n'])
        for k in P['ks']:
            for p in tri[k][4]: moves.setdefault(tuple(round(c, 3) for c in p), (dv, P['n']))
    if not moves: return 0
    piece_of = {}
    for pi, P in enumerate(info):
        for k in P['ks']: piece_of[(tri[k][0], tri[k][1])] = pi
    for mat, ts in m.tris.items():
        for i, t in enumerate(ts):
            pi = piece_of.get((mat, i))
            if pi is None: continue
            P = info[pi]
            new = []
            for v in t:
                if P['shift'] > 0:
                    dv = tuple(c * P['shift'] for c in P['n'])
                else:
                    mv = moves.get(tuple(round(c, 3) for c in v[:3]))
                    dv = mv[0] if mv and abs(_dot(P['n'], mv[1])) < 0.5 else (0, 0, 0)
                new.append((v[0] + dv[0], v[1] + dv[1], v[2] + dv[2]) + tuple(v[3:]))
            ts[i] = new
    return moved
