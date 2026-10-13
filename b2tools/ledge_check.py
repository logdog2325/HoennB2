"""Static check of every jump ledge in a built world: is its lip drawn, and wound so the game doesn't cull it?

    python3 ledge_check.py [WORLD]        WORLD defaults to $HOENN_WORLD_DIR or work/world

For every ledge tile in the cells' collision (chunk.json: 'v' jump south, '>' east, '<' west) it samples the lip's
crest (the tile centre line, 0.6-0.8 of the way across the tile in the jump direction) and looks for dansa01a
triangles of the cell's terrain.dae over each sample. Black 2 draws its ledges single-sided with back faces culled
(apicula info on chunks 6 / 286: dansa01a "Cull: Backfacing"), and so does our NSBMD writer; every one of Black 2's
lip polygons is wound with its normal up (counter-clockwise seen from above). So a sample counts as drawn only when
a triangle over it has its normal up. (Some up-facing cap triangles face north, away from the camera, in Black 2's
chunks too; they are the cap's far side.) Prints per map: ledge tiles drawn / culled (only down-facing triangles
over the crest: invisible in the game) / missing (nothing over it), then the bad tiles in world coordinates.

Corners: Sapphire's corner tiles (class ledge_cap, data/plans + the main layout) that build_chunk.ledge_joins joins
must carry both lips at full height: the crest is sampled on both sides of the edges the lips cross (the run's end
must not taper to it) and where the two crests cross, and has to stand 4 units over the tile's height (collision.per).
Corner tiles ledge_joins leaves alone (plain ends, lips that disagree on the low side, other levels) are listed.
Seams: where a ledge goes on from one tile to the next at the same level (also across a chunk border, where the
runs are drawn per cell), the crest must stay at full height across the shared edge.
Exit status 1 when a ledge tile is not drawn, a corner has a gap or a seam dips.
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exterior_check import load_dae, map_box
import build_chunk as bc

KIND = {'v': 'south', '>': 'east', '<': 'west'}

def samples(ch, tx, tz):
    x0, z0 = tx * 16 - 256, tz * 16 - 256          # model units (chunk-centred, as terrain.dae)
    fs = (0.6, 0.7, 0.8)
    if ch == 'v': return [(x0 + 8, z0 + 16 * f) for f in fs]
    if ch == '>': return [(x0 + 16 * f, z0 + 8) for f in fs]
    return [(x0 + 16 * (1 - f), z0 + 8) for f in fs]

_TRIS = {}
def _tris(wd, cx, cz):
    """Face-up dansa01a triangles of a cell, projected on xz, for point-in-triangle tests (model units)."""
    if (cx, cz) not in _TRIS:
        P = [P for n, img, P, UV, A in load_dae(os.path.join(wd, 'cells', f'{cx:02d}_{cz:02d}', 'terrain.dae'))
             if n == 'dansa01a']
        P = np.concatenate(P) if P else np.zeros((0, 3, 3))
        N = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        A, B, C = P[:, 0][:, [0, 2]], P[:, 1][:, [0, 2]], P[:, 2][:, [0, 2]]
        den = (B[:, 1] - C[:, 1]) * (A[:, 0] - C[:, 0]) + (C[:, 0] - B[:, 0]) * (A[:, 1] - C[:, 1])
        _TRIS[(cx, cz)] = (P, N[:, 1] > 1e-6, A, B, C, np.where(np.abs(den) > 1e-9, den, 1), np.abs(den) > 1e-9)
    return _TRIS[(cx, cz)]

def crest_y(wd, X, Z):
    """Highest face-up ledge surface over world point (X, Z) (world units), or None."""
    cx, cz = int(X // 512), int(Z // 512)
    if not os.path.exists(os.path.join(wd, 'cells', f'{cx:02d}_{cz:02d}', 'terrain.dae')): return None
    P, front, A, B, C, den, ok = _tris(wd, cx, cz)
    x, z = X - cx * 512 - 256, Z - cz * 512 - 256
    w0 = ((B[:, 1] - C[:, 1]) * (x - C[:, 0]) + (C[:, 0] - B[:, 0]) * (z - C[:, 1])) / den
    w1 = ((C[:, 1] - A[:, 1]) * (x - C[:, 0]) + (A[:, 0] - C[:, 0]) * (z - C[:, 1])) / den
    w2 = 1 - w0 - w1
    over = ok & front & (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
    if not over.any(): return None
    return float((w0 * P[:, 0, 1] + w1 * P[:, 1, 1] + w2 * P[:, 2, 1])[over].max())

_PER = {}
def tile_height(wd, wx, wz):
    """A tile's flat collision height (collision.per, heights.py's tables), None for slopes / unbuilt cells."""
    import struct
    from terrain.heights import OFFS
    k = (wx // 32, wz // 32)
    if k not in _PER:
        p = os.path.join(wd, 'cells', f'{k[0]:02d}_{k[1]:02d}', 'collision.per')
        _PER[k] = open(p, 'rb').read() if os.path.exists(p) else None
    if _PER[k] is None: return None
    a, b, cls, flags = struct.unpack_from('<HHHH', _PER[k], 4 + 8 * ((wz % 32) * 32 + wx % 32))
    return -OFFS[b] / 4094 if a == 0 else None

def plan_world():
    """{(world tile): (map, class, walkable)} of the main layout's maps, placed as world.py places them."""
    cfg = json.load(open(os.path.join(HERE, '..', 'data', 'hoenn_world.json')))
    W = {}
    for name in json.load(open(os.path.join(HERE, '..', 'data', 'hoenn_world_layout.json')))['main']['maps']:
        p = os.path.join(HERE, '..', 'data', 'plans', f'{name}.json')
        if not os.path.exists(p): continue
        x0, z0, _, _ = map_box(name)
        z0 += cfg.get('pad_north', {}).get(name, 0)
        d = json.load(open(p))
        for z, row in enumerate(d['tiles']):
            for x, c in enumerate(row): W[(x0 + x, z0 + z)] = (name, c, d['walkable'][z][x])
    return W

_CREST = {'v': (1, 0.88), '>': (0, 0.88), '<': (0, 0.12)}      # axis across which the profile runs, crest

def seams(wd):
    """(ok, dips): neighbouring tiles of one ledge at one level whose shared edge has the crest below full height."""
    world = json.load(open(os.path.join(wd, 'world.json')))
    grid = {}
    for c in world['cells']:
        g = json.load(open(os.path.join(wd, 'cells', f"{c['cx']:02d}_{c['cz']:02d}", 'chunk.json')))['collision']
        for tz, row in enumerate(g):
            for tx, ch in enumerate(row):
                if ch in _CREST: grid[(c['cx'] * 32 + tx, c['cz'] * 32 + tz)] = ch
    ok, dips = 0, []
    for (wx, wz), ch in sorted(grid.items()):
        axis, crest = _CREST[ch]
        nxt = (wx + 1, wz) if axis else (wx, wz + 1)            # the next tile along the ledge
        if grid.get(nxt) != ch or tile_height(wd, wx, wz) != tile_height(wd, *nxt): continue
        want = tile_height(wd, wx, wz) + 4
        pts = [(1 + d, crest) if axis else (crest, 1 + d) for d in (-0.01, 0.01)]    # at the edge (caps taper inwards)
        ys = [crest_y(wd, (wx + px) * 16, (wz + pz) * 16) for px, pz in pts]
        if all(y is not None and abs(y - want) < 0.6 for y in ys): ok += 1
        else: dips.append((KIND[ch], wx, wz, nxt[0], nxt[1]))
    return ok, dips

def corners(wd):
    """(joined, gaps, left alone) corner tiles of the built cells: lists of (map, world x, world z)."""
    W = plan_world()
    get = lambda x, z: W.get((x, z))
    hy = lambda x, z: tile_height(wd, x, z)
    joined, gaps, left = [], [], []
    for (wx, wz), e in sorted(W.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if e[1] != 'ledge_cap' or hy(wx, wz) is None: continue
        j = bc.ledge_joins(get, hy, wx, wz)
        if not j: left.append((e[0], wx, wz)); continue
        (ea, la), (eb, lb), outer = j
        want = hy(wx, wz) + 4
        pts = [(lb[1], la[1])]                                # where the crests cross (x, z in the tile)
        for edge, (axis, crest, low) in ((ea, la), (eb, lb)):
            q0, inward = (0, 1) if edge in 'wn' else (1, -1)
            for dq in (-0.01, 0.03):                           # at the edge (the run must not taper to it), inside
                q = q0 + inward * dq
                pts.append((q, crest) if axis else (crest, q))
        ys = [crest_y(wd, (wx + px) * 16, (wz + pz) * 16) for px, pz in pts]
        (joined if all(y is not None and abs(y - want) < 0.6 for y in ys) else gaps).append((e[0], wx, wz))
    return joined, gaps, left

def check(wd):
    world = json.load(open(os.path.join(wd, 'world.json')))
    per_map, bad = {}, []
    boxes = {}                                      # Sapphire map -> its world tile box (main layout)
    for m in json.load(open(os.path.join(HERE, '..', 'data', 'hoenn_world_layout.json')))['main']['maps']:
        try: boxes[m] = map_box(m)
        except (KeyError, FileNotFoundError): pass
    for c in world['cells']:
        cx, cz = c['cx'], c['cz']
        d = os.path.join(wd, 'cells', f'{cx:02d}_{cz:02d}')
        grid = json.load(open(os.path.join(d, 'chunk.json')))['collision']
        tiles = [(ch, tx, tz) for tz, row in enumerate(grid) for tx, ch in enumerate(row) if ch in KIND]
        if not tiles: continue
        P = [P for n, img, P, UV, A in load_dae(os.path.join(d, 'terrain.dae')) if n == 'dansa01a']
        P = np.concatenate(P) if P else np.zeros((0, 3, 3))
        N = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        front = N[:, 1] > 1e-6                     # wound counter-clockwise seen from above
        A, B, C = P[:, 0][:, [0, 2]], P[:, 1][:, [0, 2]], P[:, 2][:, [0, 2]]
        den = (B[:, 1] - C[:, 1]) * (A[:, 0] - C[:, 0]) + (C[:, 0] - B[:, 0]) * (A[:, 1] - C[:, 1])
        ok_den = np.abs(den) > 1e-9
        den = np.where(ok_den, den, 1)
        zone = world['zones'].get(str(c['zone']), {})
        cell_name = '/'.join(zone.get('maps', [])) or f"zone {c['zone']}"
        for ch, tx, tz in tiles:
            wx, wz = cx * 32 + tx, cz * 32 + tz
            name = next((m for m, (x0, z0, x1, z1) in boxes.items() if x0 <= wx < x1 and z0 <= wz < z1), cell_name)
            state = 'drawn'
            for x, z in samples(ch, tx, tz):
                w0 = ((B[:, 1] - C[:, 1]) * (x - C[:, 0]) + (C[:, 0] - B[:, 0]) * (z - C[:, 1])) / den
                w1 = ((C[:, 1] - A[:, 1]) * (x - C[:, 0]) + (A[:, 0] - C[:, 0]) * (z - C[:, 1])) / den
                over = ok_den & (w0 >= -1e-6) & (w1 >= -1e-6) & (1 - w0 - w1 >= -1e-6)
                if not over.any(): state = 'missing'; break
                if not (over & front).any(): state = 'culled'
            s = per_map.setdefault(name, {'drawn': 0, 'culled': 0, 'missing': 0})
            s[state] += 1
            if state != 'drawn': bad.append((name, KIND[ch], wx, wz, state))
    return per_map, bad

if __name__ == '__main__':
    wd = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('HOENN_WORLD_DIR') or os.path.join(HERE, '..', 'work', 'world')
    per_map, bad = check(wd)
    tot = {k: sum(s[k] for s in per_map.values()) for k in ('drawn', 'culled', 'missing')}
    print(f"ledge tiles: {tot['drawn']} drawn, {tot['culled']} culled (down-facing only), {tot['missing']} missing")
    for name, s in sorted(per_map.items()):
        print(f"  {name:40s} {s['drawn']:4d} drawn {s['culled']:4d} culled {s['missing']:4d} missing")
    for b in bad: print('  bad:', *b)
    ok, dips = seams(wd)
    print(f"seams between ledge tiles: {ok} at full height, {len(dips)} dip")
    for d in dips: print('  dip:', *d)
    joined, gaps, left = corners(wd)
    print(f"corner tiles: {len(joined)} joined, {len(gaps)} with a gap, {len(left)} left alone (plain ends, lips that "
          f"disagree on the low side, other levels)")
    for g in gaps: print('  gap:', *g)
    if left: print('  left alone:', ', '.join(f'{n} ({x},{z})' for n, x, z in left))
    sys.exit(1 if bad or gaps or dips else 0)
