"""Route planning across maps: connected regions of each matrix (on foot, or also by surf) joined by warps.

    legs = plan(g, target_zone, (x, z), surf=False)   ->  [('warp', zone, idx), ..., ('walk', zone, (x, z))]
    travel(g, target_zone, (x, z))                    ->  walks it (re-plans after each failure)
Regions ignore ledge direction and people (the walker re-plans with the real rules)."""
import heapq, os, pickle
from collections import deque
from pt import *
import romdata as R

CACHE = os.path.join(LOG, 'regions')
os.makedirs(CACHE, exist_ok=True)
_WARPS = {}
_REG = {}


def zone_warps(z):
    if z not in _WARPS:
        ws = rom().entities(z)['warps']
        out = []
        for i, w in enumerate(ws):
            same = [v for v in ws if (v['tile_x'], v['tile_z']) == (w['tile_x'], w['tile_z']) and v['dest_zone'] != w['dest_zone']]
            if same: continue                      # parked warp
            if w['tile_x'] <= 0 and w['tile_z'] <= 0 or w['tile_x'] >= 4000 or w['tile_z'] >= 4000: continue
            if w['dest_zone'] >= len(rom().hdr): continue
            out.append((i, w))
        _WARPS[z] = out
    return _WARPS[z]


_MZ = None
def matrix_zones(m):
    global _MZ
    if _MZ is None:
        _MZ = {}
        for z, h in enumerate(rom().hdr): _MZ.setdefault(h['matrix'], []).append(z)
    return _MZ.get(m, [])


def walkable(grid, t, surf):
    for r in grid.rec(*t):
        if R.land(r) or (surf and R.surf(r)): return True
    return False


def regions(m, surf):
    """{tile: region id} of matrix m (flood fill, height steps < 20, ledges both ways, surf water when surf)."""
    key = (m, surf)
    if key in _REG: return _REG[key]
    p = os.path.join(CACHE, f'm{m}_{int(surf)}.pkl')
    if os.path.exists(p):
        _REG[key] = pickle.load(open(p, 'rb')); return _REG[key]
    z = matrix_zones(m)[0]
    grid = rom().grid(z)
    lab = {}
    nid = 0
    for cz in range(grid.h):
        for cx in range(grid.w):
            if not grid.layers(cx, cz): continue
            for lz in range(32):
                for lx in range(32):
                    t = (cx * 32 + lx, cz * 32 + lz)
                    if t in lab or not walkable(grid, t, surf): continue
                    lab[t] = nid; q = deque([t])
                    while q:
                        a = q.popleft()
                        ya = [R.Grid.y(r, *a) for r in grid.rec(*a)]
                        for d in DIRK:
                            b = (a[0] + d[0], a[1] + d[1])
                            if b in lab: continue
                            rb = grid.rec(*b)
                            if not rb: continue
                            if any(r[2] in R.LEDGE for r in rb):           # a ledge: lands one further
                                c = (b[0] + d[0], b[1] + d[1])
                                if c not in lab and walkable(grid, c, surf): lab[c] = nid; q.append(c)
                                continue
                            if not walkable(grid, b, surf): continue
                            yb = [R.Grid.y(r, *b) for r in rb]
                            okh = any(abs((u or 0) - (v or 0)) < 20 or u is None or v is None for u in ya for v in yb)
                            water = surf and (any(R.surf(r) for r in rb) or any(R.surf(r) for r in grid.rec(*a)))
                            if okh or water:
                                lab[b] = nid; q.append(b)
                    nid += 1
    _REG[key] = lab
    pickle.dump(lab, open(p, 'wb'))
    return lab


def approach_tiles(grid, w):
    tiles = [(w['tile_x'] + a, w['tile_z'] + b) for a in range(w['w']) for b in range(w['h'])]
    out = []
    for t in tiles:
        out.append(t)
        out += [(t[0] + dx, t[1] + dz) for dx, dz in ((0, 1), (0, -1), (-1, 0), (1, 0))]
    return out


def arrival(dz, dw):
    ws = rom().entities(dz)['warps']
    if dw >= len(ws): return None
    w = ws[dw]
    grid = rom().grid(dz)
    t = (w['tile_x'], w['tile_z'])
    if any(R.land(r) for r in grid.rec(*t)): return t
    for dx, dz_ in ((0, 1), (0, -1), (-1, 0), (1, 0)):
        c = (t[0] + dx, t[1] + dz_)
        if any(R.land(r) for r in grid.rec(*c)): return c
    return t


def plan(g, tz, tt, surf=False):
    """Fewest warps from the player to tile tt of zone tz."""
    m0 = rom().hdr[g.zone()]['matrix']; mt = rom().hdr[tz]['matrix']
    reg0 = regions(m0, surf)
    start = (m0, reg0.get(g.tile()))
    goal = (mt, regions(mt, surf).get(tuple(tt)))
    if goal[1] is None: return None
    dist = {start: 0}; prev = {start: None}
    pq = [(0, start)]
    while pq:
        c, node = heapq.heappop(pq)
        if node == goal: break
        if c > dist.get(node, 1e9): continue
        m, rid = node
        reg = regions(m, surf)
        for z in matrix_zones(m):
            grid = rom().grid(z)
            for i, w in zone_warps(z):
                if not any(reg.get(t) == rid for t in approach_tiles(grid, w)): continue
                a = arrival(w['dest_zone'], w['dest_warp'])
                if a is None: continue
                m2 = rom().hdr[w['dest_zone']]['matrix']
                r2 = regions(m2, surf).get(a)
                if r2 is None: continue
                nn = (m2, r2)
                if c + 1 < dist.get(nn, 1e9):
                    dist[nn] = c + 1; prev[nn] = (node, ('warp', z, i)); heapq.heappush(pq, (c + 1, nn))
            if not surf: continue
            for rec in dives().get(z, []):
                src = next((t for t in rec['tiles'] if reg.get(t) == rid), None)
                if src is None: continue
                a = (rec['ax'], rec['az']) if rec['flags'] & 1 else (src[0] + rec['ax'], src[1] + rec['az'])
                m2 = rom().hdr[rec['dest']]['matrix']
                r2 = regions(m2, surf).get(a)
                if r2 is None:
                    for dx, dz_ in ((0, 1), (0, -1), (-1, 0), (1, 0)):
                        r2 = regions(m2, surf).get((a[0] + dx, a[1] + dz_))
                        if r2 is not None: break
                if r2 is None: continue
                nn = (m2, r2)
                if c + 2 < dist.get(nn, 1e9):
                    dist[nn] = c + 2; prev[nn] = (node, ('dive', z, src)); heapq.heappush(pq, (c + 2, nn))
    if goal not in prev: return None
    legs = [('walk', tz, tuple(tt))]
    n = goal
    while prev[n]:
        n, leg = prev[n]; legs.insert(0, leg)
    return legs


def travel(g, tz, tt, surf=None, tries=6):
    surf = g.can_surf if surf is None else surf
    for _ in range(tries):
        if g.zone() == tz and g.tile() == tuple(tt): return True
        legs = plan(g, tz, tuple(tt), surf=surf)
        if legs is None:
            g.note(f'travel: no plan to zone {tz} {tt} from {g.zone()} {g.tile()}'); return False
        g.note(f'travel plan: {legs}')
        for kind, z, a in legs:
            if kind == 'walk':
                r = g.go(*a, tries=12)
                if r is not True: break
            elif kind == 'dive':
                if not dive_at(g, a):
                    g.note(f'travel: dive at {a} in {z} failed'); break
            else:
                w = rom().entities(z)['warps'][a]
                if g.zone() != z:
                    tgt = arrival_near(g, z, w)
                    if tgt: g.go(*tgt, tries=12)
                z0 = g.zone()
                if not g.warp(a) or g.zone() == z0:
                    g.note(f'travel: warp {a} of {z} failed'); break
                g.adv()
        else:
            continue
    return g.zone() == tz and g.tile() == tuple(tt)


_DIVES = None
def dives():
    global _DIVES
    if _DIVES is None:
        import divetable
        _DIVES = divetable.table()
    return _DIVES


def dive_at(g, tile):
    """Stand (surf / swim) on tile and dive or surface with A + yes. True when the zone changed."""
    z0 = g.zone()
    if g.go(*tile, tries=12) is not True: return False
    g.press('A', 4, 20)
    g.adv(answers=['yes'])
    for _ in range(80):
        if g.zone() != z0 and g.field(): break
        g.run(10)
    g.wait_idle()
    return g.zone() != z0


def arrival_near(g, z, w):
    grid = rom().grid(z)
    for t in approach_tiles(grid, w):
        if any(R.land(r) for r in grid.rec(*t)): return t
    return None
