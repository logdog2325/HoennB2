"""Build one Black 2 map chunk (32x32 tiles) from a Sapphire plan (data/plans/<Map>.json).

    python3 build_chunk.py LittlerootTown --offset 6,0 --cell 24,23 --out ../work/chunks/littleroot

Writes to --out:
  terrain.dae   Gen 5 terrain built the way Black 2 builds its own (see notes/GEN5_TERRAIN.md):
                grass01ax ground, hana01.1 flowers, michi_hage sand patches, ki02* trees; area 2 texture names
  collision.per 32x32 permission grid (8 bytes per tile), values copied from Nuvema's own tiles
  chunk.json    tile -> world mapping, building/sign placements and warp positions for the event patch

--offset is where the Sapphire map's (0,0) lands inside the chunk; every tile outside the map is forest.
--cell is the chunk's position in matrix 0 (for world coordinates of events).
"""
import os, sys, json, struct, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dae import Model

T = 16            # units per tile
HALF = 256        # chunk is centred on the origin

# collision tiles copied from Nuvema (chunk 0): (inclination, height index, class, flags)
WALK = (0, 3, 0x0000, 0x0080)       # plain floor at ground height (y = 0)            (Nuvema)
SOLID = (0, 3, 0x0001, 0x0081)      # wall / out of bounds / tree / building          (Nuvema)
ROUTE_GRASS = (0, 3, 0x001F, 0x0080)  # route floor                                   (Route 1)
ROUTE_PATH = (0, 3, 0x0003, 0x0080)   # route sand path                               (Route 1)
TALL_GRASS = (0, 3, 0x0004, 0x0024)   # tall grass, single battles, encounter flag    (Route 1)
LEDGE_S = (0, 3, 0x0075, 0x0001)      # ledge, jump south (down the screen)           (Route 2)

def ux(tx): return tx * T - HALF            # tile column -> model x (west edge of the tile)
def uz(tz): return tz * T - HALF            # tile row -> model z (north edge; z grows southward)

def ground(m, size=32):
    """Grass over the whole chunk, 4x4-tile quads, texture repeating every 4 tiles (as in Nuvema)."""
    for tz in range(0, size, 4):
        for tx in range(0, size, 4):
            x0, x1, z0, z1 = ux(tx), ux(tx + 4), uz(tz), uz(tz + 4)
            m.quad('grass01ax', [(x0, 0, z1, tx / 4, -(tz + 4) / 4), (x1, 0, z1, (tx + 4) / 4, -(tz + 4) / 4),
                                 (x1, 0, z0, (tx + 4) / 4, -tz / 4), (x0, 0, z0, tx / 4, -tz / 4)])

def flat_decal(m, mat, tx, tz, w, h, y):
    x0, x1, z0, z1 = ux(tx), ux(tx + w), uz(tz), uz(tz + h)
    m.quad(mat, [(x0, y, z1, 0, 0), (x1, y, z1, 1, 0), (x1, y, z0, 1, 1), (x0, y, z0, 0, 1)])

R_SIDE, R_CANOPY, R_TOP = 56, 23, 46   # Black 2's round tree (ki03): card top, canopy and top layer heights (Black 2's
                                        # top is at 46.3; 46 keeps it 2 under ground 48 up, as outdoor_check's layer rule)
def overlap_lift(base, near):
    """world.overlap_fill's overlapping trees: the lift (4 or more) that keeps the tree's canopy and top (base + 23 / 46
    + lift) 2 or more units from every tree layer under it (near: absolute heights) and from the 16-unit ground levels
    (depth fights)."""
    for lift in range(4, 64):
        ys = (base + R_CANOPY + lift, base + R_TOP + lift)
        if all(abs(y - n) >= 2 for y in ys for n in near) and all(abs(y - 16 * round(y / 16)) >= 2 for y in ys):
            return lift
    return 64

def tree_row(m, tx, tz, n, kind='round', lift=0, card=0, shadow=True, cross=None):
    """n side-by-side 2x2-tile trees starting at tile (tx, tz), drawn as strips the way Black 2 draws forest rows
    (one shadow / side / canopy / top quad per row, texture repeating once per tree).
    round (ki03, Route 6): shadow ki02c y3 (drawn at 4, see below), side image ki03ax y3-56 through the trees' middle
                           facing south, and one ki03ax card north-south through every tree's centre (all 96 Black 2
                           chunks with this tree cross every tree, not only a row's ends), canopy ki03bx y23, top ki03dx
                           y46 (Black 2: 46.3, see R_TOP). The cards are drawn from both sides and every part is lit as if it faced up (Black 2:
                           normal (0, 1, 0) on every tree polygon, material ki03ax "Cull: None"; world.py write_cell
                           and nsbmd_fix.tree_materials), so the sides are as bright as the canopy, as in Black 2.
    pine  (ki02, Nuvema):  shadow ki02c y3, side image ki02ax y3-72 facing south, canopy ki02bx y26, top ki02dx y60
    lift / card / shadow (world.overlap_fill's overlapping trees): the tree raised by lift, its cards moved card units
    south / east (never in the same plane as an overlapped tree's card: depth fights), no shadow (the trees it overlaps
    shade the ground; a lifted shadow met the tall-grass layers). cross(k): False leaves tree k's north-south card out
    (world.py: a tree by a cliff, where the card met the cliff's face)."""
    side, canopy, top, h_side, h_can, h_top = (('ki03ax', 'ki03bx', 'ki03dx', R_SIDE, R_CANOPY, R_TOP) if kind == 'round'
                                               else ('ki02ax', 'ki02bx', 'ki02dx', 72, 26, 60))
    x0, x1, z0, z1, zc = ux(tx), ux(tx + 2 * n), uz(tz), uz(tz + 2), uz(tz + 1)
    flat = lambda mat, y: m.quad(mat, [(x0, y, z1, 0, 0), (x1, y, z1, n, 0), (x1, y, z0, n, 1), (x0, y, z0, 0, 1)])
    if shadow: flat('ki02c', 4)   # (Black 2: y 3) 2 clear of the y-2 and y-6 tall-grass layers that reach into tree tiles
    y0, y1, zc = 3 + lift, h_side + lift, zc + card
    m.quad(side, [(x0, y0, zc, 0, 0), (x1, y0, zc, n, 0), (x1, y1, zc, n, 1), (x0, y1, zc, 0, 1)])
    if kind == 'round':
        for k in range(n):
            if cross and not cross(k): continue
            xc = ux(tx + 1 + 2 * k) + card
            m.quad(side, [(xc, y0, z1, 1, 0), (xc, y0, z0, 0, 0), (xc, y1, z0, 0, 1), (xc, y1, z1, 1, 1)])   # (u south as Black 2)
    flat(canopy, h_can + lift)
    flat(top, h_top + lift)

NARROW_SCALE = 0.5     # one-tile trees: Black 2's round tree scaled evenly to one tile (Black 2 has no narrow tree)

def narrow_tree_row(m, tx, zb, n, h=NARROW_SCALE, w=None, cross=None, card=0):
    """n side-by-side one-tile-wide round trees (ki03, tree_row's layers), the first on tile column tx, standing on the
    line z = zb (model units), one tile deep: Sapphire's one-tile-wide trees (Routes 111-123, Lavaridge) and the lone
    trees of its dense forests that no whole tree fits (world.forest_fill). One quad per layer for the whole row, the
    texture once per tree (as tree_row), so neighbours never overlap (per-tile trees 1.25 tiles wide z-fought where
    they met). Black 2's tree scaled evenly: w = 32 x h wide and deep (it was 16 wide and 0.8 high: Black 2's art
    squeezed to 40% of its width, b2_trees 2026-10-11)."""
    w = w or 32 * h
    x0, x1 = ux(tx) + 8 - w / 2, ux(tx + n - 1) + 8 + w / 2
    z0, z1, zc = zb - w, zb, zb - w / 2 + card     # (card: the south card moved, world.py: beside a sign's board)
    flat = lambda mat, y: m.quad(mat, [(x0, y, z1, 0, 0), (x1, y, z1, n, 0), (x1, y, z0, n, 1), (x0, y, z0, 0, 1)])
    flat('ki02c', 4)
    m.quad('ki03ax', [(x0, 3, zc, 0, 0), (x1, 3, zc, n, 0), (x1, R_SIDE * h, zc, n, 1), (x0, R_SIDE * h, zc, 0, 1)])
    for k in range(n):                       # (a north-south card through every tree, as tree_row)
        if cross and not cross(k): continue
        xc = ux(tx + k) + 8
        m.quad('ki03ax', [(xc, 3, z1, 1, 0), (xc, 3, z0, 0, 0), (xc, R_SIDE * h, z0, 0, 1), (xc, R_SIDE * h, z1, 1, 1)])
    flat('ki03bx', R_CANOPY * h - 1.5)    # (1.5 under the even scale: 2 clear of tall grass at 8 and grass lips at 12)
    flat('ki03dx', R_TOP * h)

def path_tile(m, tx, tz, is_path, y=2.0):
    """One sand-path tile, Black 2 style (Nuvema/Route 2): tiles with grass within one tile get michi01a, the fringe
    strip, whose v runs from 1 at the grass edge to 0 one tile into the path; deeper tiles get plain michi01b.
    Border tiles are split into 2x2 quads and every corner point takes v from its distance to the nearest grass
    tile (straight edges, rounded outer corners). y = 2 keeps the path above the grass: 0.5 flickered in melonDS (per-triangle depth fight;
    Black 2 never layers surfaces closer than 2 units, 2026-10-06)."""
    x0, z0 = ux(tx), uz(tz)
    grass = [(tx + dx, tz + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if not is_path(tx + dx, tz + dz)]
    if not grass:
        m.quad('michi01b', [(x0, y, z0 + 16, x0 / 16, -(z0 + 16) / 16), (x0 + 16, y, z0 + 16, (x0 + 16) / 16, -(z0 + 16) / 16),
                            (x0 + 16, y, z0, (x0 + 16) / 16, -z0 / 16), (x0, y, z0, x0 / 16, -z0 / 16)])
        return
    def v_at(x, z):     # distance (tiles) from point to the nearest grass tile, as fringe v (1 at the edge)
        d = 1.0
        for gx, gz in grass:
            rx0, rz0 = ux(gx), uz(gz)
            dx = max(rx0 - x, 0, x - (rx0 + 16)); dz = max(rz0 - z, 0, z - (rz0 + 16))
            d = min(d, (dx * dx + dz * dz) ** 0.5 / 16)
        return 1 - d
    pt = lambda x, z: (x, y, z, (x + z) / 32, v_at(x, z))
    for qx in (0, 8):
        for qz in (0, 8):
            a, b = x0 + qx, z0 + qz
            m.quad('michi01a', [pt(a, b + 8), pt(a + 8, b + 8), pt(a + 8, b), pt(a, b)])

def tall_grass_run(m, tx0, tx1, tz):
    """Route 1's tall grass over tiles tx0..tx1 of one row: three stacked leaf layers (kusa_ec3 y2, kusa_ec2 y6,
    kusa_ec1 y8), nudged 2 units south, texture repeating once per tile (one quad per layer per run, as Route 1)."""
    for mat, y in (('kusa_ec3', 2), ('kusa_ec2', 6), ('kusa_ec1', 8)):
        x0, x1, z0, z1 = ux(tx0), ux(tx1 + 1), uz(tz) + 2, uz(tz + 1) + 2
        n = tx1 + 1 - tx0
        m.quad(mat, [(x0, y, z1, 0, 0), (x1, y, z1, n, 0), (x1, y, z0, n, 1), (x0, y, z0, 0, 1)])

def ledge_run(m, tx0, tx1, tz, get=None, hy=None, open_ends=(False, False)):
    """A south-facing ledge over tiles tx0..tx1 of row tz, copied from Route 2: an earth lip (dansa01a) rising from
    z+0.38 to 4 units high at z+0.88 and dropping to the ground at z+1, tapered over the end tiles.
    With get/hy (the cell's tile lookup and tile heights, world.py) an end where the ledge goes on is not tapered
    (_open_end): the lip runs at full height to the tile edge."""
    if get is not None:
        open_ends = (_open_end(get, hy, 'ledge_s', (tx0, tz), (tx0 - 1, tz)),
                     _open_end(get, hy, 'ledge_s', (tx1, tz), (tx1 + 1, tz)))
    t = lambda v: v * T - HALF
    za, zb, zc = t(tz + 0.38), t(tz + 0.88), t(tz + 1.0)
    xa, xb = t(tx0 + (0 if open_ends[0] else 1)), t(tx1 + (1 if open_ends[1] else 0))
    if xb > xa:
        u0, u1 = 0, (xb - xa) / 16      # east -> west, so both faces wind counter-clockwise from above, as Route 2's
        # (chunk 6: (80,0,-202) (64,0,-202) (64,4,-194) (80,4,-194)); west -> east faced down and the game culled it
        m.quad('dansa01a', [(xb, 0, za, u1, 1), (xa, 0, za, u0, 1), (xa, 4, zb, u0, 0.5), (xb, 4, zb, u1, 0.5)])
        m.quad('dansa01a', [(xb, 4, zb, u1, 0.5), (xa, 4, zb, u0, 0.5), (xa, 0, zc, u0, 0), (xb, 0, zc, u1, 0)])
    for x_edge, sgn, is_open in ((xa, -1, open_ends[0]), (xb, 1, open_ends[1])):  # end caps fan over the end tile
        if is_open: continue
        tip = (x_edge + sgn * 8, 4, t(tz + 0.75)); far = (x_edge + sgn * 12, 0, t(tz + 0.75))
        back = (x_edge + sgn * 16, 0, t(tz + 0.25))
        m.tri('dansa01a', [(x_edge, 0, za, 0, 1), (x_edge, 4, zb, 0, 0.5), (*tip, 0.5, 0.5)][::sgn])
        m.tri('dansa01a', [(*tip, 0.5, 0.5), (x_edge, 4, zb, 0, 0.5), (x_edge, 0, zc, 0, 0)][::sgn])
        m.tri('dansa01a', [(*tip, 0.5, 0.5), (x_edge, 0, zc, 0, 0), (*far, 1, 0)][::sgn])
        m.tri('dansa01a', [(*back, 1, 0.75), (x_edge, 0, za, 0, 1), (*tip, 0.5, 0.5)][::sgn])
        m.tri('dansa01a', [(*back, 1, 0.75), (*tip, 0.5, 0.5), (*far, 1, 0)][::sgn])

def ledge_run_ew(m, tx, tz0, tz1, east=True, get=None, hy=None):
    """An east- or west-facing ledge over tiles tz0..tz1 of column tx: the south ledge above turned a quarter turn, as
    Black 2 builds its side ledges (Route 20 chunk 286 jumps east: lip rising from x+0.38 to 4 units at x+0.88 and
    dropping at x+1; Route 19 chunk 282 jumps west: the mirror image). v is the south ledge's, as there: 1 at the
    back, 0.5 on the crest, 0 at the foot (apicula DAE of chunks 286 / 282; it was 1 - v, the texture upside down).
    get/hy: as ledge_run (no taper where the ledge goes on)."""
    kind = 'ledge_e' if east else 'ledge_w'
    ends = ((_open_end(get, hy, kind, (tx, tz0), (tx, tz0 - 1)), _open_end(get, hy, kind, (tx, tz1), (tx, tz1 + 1)))
            if get else (False, False))
    tmp = Model('ledge')
    ledge_run(tmp, tz0, tz1, tx, open_ends=ends)   # built along x at row tx, then x and z swap (and mirror for west)
    cx = tx * T - HALF
    for tri in tmp.tris.get('dansa01a', []):
        vs = []
        for x, y, z, u, v, c in tri:
            nx_, nz_ = (z, x) if east else (2 * cx + T - z, x)
            vs.append((nx_, y, nz_, -u if east else u, v, c))
        (ax, ay, az), (bx, by, bz), (qx, qy, qz) = [p[:3] for p in vs]
        if (bz - az) * (qx - ax) - (bx - ax) * (qz - az) < 0: vs = vs[::-1]     # keep the lip's faces pointing up
        m.tri('dansa01a', vs)

def _open_end(get, hy, kind, end, beyond):
    """Does the ledge go on past a run's end tile? Into the next cell at the same level (runs are drawn per cell, so a
    ledge across a chunk border tapered to nothing on both sides of it: 14 places), or into a corner tile."""
    nxt = get(*beyond)
    if nxt and nxt[1] == kind and hy(*beyond) == hy(*end): return True
    return bool(ledge_joins(get, hy, *beyond))

# A lip crossing a tile edge, as (axis, crest, low): the profile runs across z (axis 1, the lip runs along x) or x
# (axis 0); crest = where its top is in the tile (0..1), low = the side it is jumped down to (+1 / -1). The back is
# 0.5 behind the crest, the foot 0.12 beyond it (ledge_run's z+0.38 / 0.88 / 1.0).
_LIP = {'ledge_s': (1, 0.88, 1), 'ledge_e': (0, 0.88, 1), 'ledge_w': (0, 0.12, -1)}
_EDGE = {'w': (-1, 0), 'e': (1, 0), 'n': (0, -1), 's': (0, 1)}

def ledge_joins(get, hy, tx, tz):
    """Sapphire draws its ledges round corners through corner tiles (class ledge_cap: metatiles 0x06e / 0x08e, solid,
    no jump). Black 2 has no corner piece: at its one overworld corner (Route 23, chunk 309 tile (12, 20)) both lips
    just taper and a tree stands on the corner tile. So the corner is drawn as Black 2's own lip turned round it with a
    mitre (ledge_corners). For the ledge_cap tile (tx, tz) of get (cell-local, any range; hy = tile heights):
    ((edge, lip), (edge, lip), outer) for the two lips that meet there - edge 'w'/'e' for the lip that runs along x,
    'n'/'s' for the one along z, lip as _LIP, outer = the high ground's corner is convex - or None (no corner tile, a
    plain end, more lips, lips that disagree on the low side, or a corner off the ledges' level). Corner tiles side by
    side (Sapphire's steps: Route 101 (6,6)-(6,7), Route 118) join through each other; the lip between two of them
    faces whichever way makes every corner of the group agree."""
    if get is None or (get(tx, tz) or (0, 0))[1] != 'ledge_cap': return None
    group, todo = {(tx, tz)}, [(tx, tz)]
    while todo:
        x, z = todo.pop()
        for dx, dz in _EDGE.values():
            k = (x + dx, z + dz)
            if k not in group and (get(*k) or (0, 0))[1] == 'ledge_cap':
                group.add(k); todo.append(k)
                if len(group) > 8: return None
    level = hy(tx, tz)
    ports, links = {}, []                      # ports[tile][edge] = lip, or link index; links[i] = axis of that lip
    for c in sorted(group):
        if hy(*c) != level: return None
        ports[c] = {}
        for edge, (dx, dz) in _EDGE.items():
            k = (c[0] + dx, c[1] + dz)
            if k in group:
                back = ports.get(k, {}).get({'w': 'e', 'e': 'w', 'n': 's', 's': 'n'}[edge])
                if back is None: links.append(1 if edge in 'we' else 0); back = len(links) - 1
                ports[c][edge] = back
                continue
            lip = _LIP.get((get(*k) or (0, 0))[1])
            if lip and lip[0] == (1 if edge in 'we' else 0):     # a lip that crosses this edge
                if hy(*k) != level: return None
                ports[c][edge] = lip
        if len(ports[c]) != 2 or len([e for e in ports[c] if e in 'we']) != 1: return None
    import itertools
    for choice in itertools.product(((0.88, 1), (0.12, -1)), repeat=len(links)):
        out = {}
        for c, p in ports.items():
            lips = ((e, (links[v], *choice[v]) if isinstance(v, int) else v) for e, v in p.items())
            (ea, la), (eb, lb) = sorted(lips, key=lambda q: q[0] not in 'we')      # the lip along x first
            toward_a, toward_b = la[2] * _EDGE[eb][1], lb[2] * _EDGE[ea][0]   # low side . the other lip's direction
            if toward_a * toward_b <= 0: break                               # one faces the other lip, one away
            out[c] = ((ea, la), (eb, lb), toward_a < 0)
        else:
            return out[(tx, tz)]
    return None

def _clip(poly, g):
    """The part of convex polygon poly (tuples x, y, z, u, v) where the linear function g(point) >= 0."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        gp, gq = g(p), g(q)
        if gp >= -1e-9: out.append(p)
        if (gp >= -1e-9) != (gq >= -1e-9):
            f = gp / (gp - gq)
            out.append(tuple(a + f * (b - a) for a, b in zip(p, q)))
    return out

def ledge_corners(m, get, hy, size=32):
    """The corner tiles of the cell (ledge_joins): both lips run on at full height into the tile and meet on its
    diagonal (a mitre through the crests' crossing: the lip's profile is the same on both sides of it), drawn at y 0
    like ledge_run (world.py lifts them to the tile's height, which ledge_joins checked is the ledges')."""
    for tz in range(size):
        for tx in range(size):
            j = ledge_joins(get, hy, tx, tz)
            if not j: continue
            (_, la), (_, lb), outer = j
            off = lambda lip, px, pz: lip[2] * ((pz if lip[0] else px) - lip[1])   # signed distance past the crest
            for lip, keep in ((la, 1), (lb, -1)):
                axis, crest, low = lip
                back, foot = crest - 0.5 * low, crest + 0.12 * low
                def pt(p, q, y, v):          # p across the lip, q along it (tile units), as the runs' u and v
                    px, pz = (q, p) if axis else (p, q)
                    return (px, y, pz, q if axis else (-q if low > 0 else q), v)
                g = lambda P: (keep if outer else -keep) * (off(la, P[0], P[2]) - off(lb, P[0], P[2]))
                for quad in ([pt(back, 0, 0, 1), pt(back, 1, 0, 1), pt(crest, 1, 4, 0.5), pt(crest, 0, 4, 0.5)],
                             [pt(crest, 0, 4, 0.5), pt(crest, 1, 4, 0.5), pt(foot, 1, 0, 0), pt(foot, 0, 0, 0)]):
                    poly = _clip(quad, g)
                    for i in range(1, len(poly) - 1):
                        tri = [(ux(tx) + T * px, y, uz(tz) + T * pz, u, v) for px, y, pz, u, v in
                               (poly[0], poly[i], poly[i + 1])]
                        (ax, _, az), (bx, _, bz), (qx, _, qz) = [p[:3] for p in tri]
                        ny = (bz - az) * (qx - ax) - (bx - ax) * (qz - az)
                        if abs(ny) < 1e-6: continue
                        m.tri('dansa01a', tri if ny > 0 else tri[::-1])     # wound face-up (back faces are culled)

def ground_heights(m, height, material=None, size=32, most=32):
    """ground() on uneven land: each tile's ground at its height (height(tx, tz) -> units) in its material
    (material(tx, tz) -> texture name, default grass01ax, None = no ground there; 64x64 textures repeating every 4
    tiles, UVs as ground()). Equal neighbours merge into rectangles of at most `most` x `most` tiles (rows first,
    then identical rows; Black 2's own ground polygons span up to a whole chunk, e.g. Route 1 chunk 2)."""
    mat = material or (lambda tx, tz: 'grass01ax')
    key = lambda tx, tz: (height(tx, tz), mat(tx, tz))
    def quad(tx, tx1, tz, tz1, h, t):
        m.quad(t, [(ux(tx), h, uz(tz1), tx / 4, -tz1 / 4), (ux(tx1), h, uz(tz1), tx1 / 4, -tz1 / 4),
                   (ux(tx1), h, uz(tz), tx1 / 4, -tz / 4), (ux(tx), h, uz(tz), tx / 4, -tz / 4)])
    open_ = {}                       # (x0, x1, key) -> first row of a rectangle still growing downwards
    for tz in range(size + 1):
        runs = []
        tx = 0
        while tz < size and tx < size:
            k = key(tx, tz); tx1 = tx + 1
            while tx1 < size and key(tx1, tz) == k and tx1 - tx < most and tx1 % most: tx1 += 1
            runs.append((tx, tx1, k)); tx = tx1
        nxt = {}
        for r in runs:
            if r in open_ and tz - open_[r] < most and tz % most: nxt[r] = open_.pop(r)
            else: nxt[r] = tz
        for (x0, x1, (h, t)), z0 in open_.items():
            if t: quad(x0, x1, z0, tz, h, t)
        open_ = nxt

def path_cover(m, path, ground, height, size=32, drop=2, mat='michi01b'):
    """A floor of path texture `drop` units under the path tiles (path(tx, tz), also asked past the cell's edge), going
    on 4 units under the ground beside them (ground(tx, tz): this cell's tiles drawn as flat ground) and cut 4 units
    back where the neighbour is anything else (water, a drop, a module's surface: never seen from outside).
    (purple_lines 2026-10-13, Discord: flickering purple lines on Oldale's path in melonDS.) path_tile's 8-unit
    fringe corners lie in the middle of a plain tile's edge or of a merged ground rectangle's edge (T-junctions); the
    DS rasterizes from whole-pixel corners, so melonDS (as the hardware) opens 1-pixel cracks along those edges that
    show the background (purple at night) and move with the camera; DeSmuME's renderer closes them. Through a crack the
    camera now sees this floor, as the caves' seam cover (models_cave.py seam_cover). Merged into rectangles."""
    on = {}
    for tz in range(size):
        for tx in range(size):
            h = height(tx, tz)
            near = lambda dx, dz: height(tx + dx, tz + dz) == h
            edge = lambda dx, dz: {(i, j) for i in range(4) for j in range(4)
                                   if (dx, i) in ((-1, 0), (1, 3)) or (dz, j) in ((-1, 0), (1, 3))}
            sides = ((-1, 0), (1, 0), (0, -1), (0, 1))
            if path(tx, tz):
                q = {(i, j) for i in range(4) for j in range(4)}
                for dx, dz in sides:
                    n = (tx + dx, tz + dz)
                    if not (near(dx, dz) and (path(*n) or 0 <= n[0] < size and 0 <= n[1] < size and ground(*n))):
                        q -= edge(dx, dz)
            elif ground(tx, tz):
                q = set()
                for dx, dz in sides:
                    if near(dx, dz) and path(tx + dx, tz + dz): q |= edge(dx, dz)
            else: continue
            for i, j in q: on[(tx * 4 + i, tz * 4 + j)] = h
    n = size * 4
    def quad(i0, i1, j0, j1, h):
        x0, x1, z0, z1 = ux(0) + 4 * i0, ux(0) + 4 * i1, uz(0) + 4 * j0, uz(0) + 4 * j1
        m.quad(mat, [(x0, h - drop, z1, x0 / 16, -z1 / 16), (x1, h - drop, z1, x1 / 16, -z1 / 16),
                     (x1, h - drop, z0, x1 / 16, -z0 / 16), (x0, h - drop, z0, x0 / 16, -z0 / 16)])
    open_ = {}                       # (i0, i1, h) -> first row of a rectangle still growing southwards
    for j in range(n + 1):
        runs, i = [], 0
        while j < n and i < n:
            if (i, j) not in on: i += 1; continue
            h = on[(i, j)]; i1 = i + 1
            while (i1, j) in on and on[(i1, j)] == h: i1 += 1
            runs.append((i, i1, h)); i = i1
        nxt = {r: open_.pop(r) if r in open_ else j for r in runs}
        for (i0, i1, h), j0 in open_.items(): quad(i0, i1, j0, j, h)
        open_ = nxt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', help="plan name in data/plans, or 'forest' for a chunk that is all trees"); ap.add_argument('--offset', default='6,0'); ap.add_argument('--cell', default='24,23')
    ap.add_argument('--out', required=True)
    ap.add_argument('--route', action='store_true', help='route floor (Route 1 values) instead of town floor')
    ap.add_argument('--extend-north', type=int, default=0,
                    help='extra rows north of the map (even), repeating its first two rows; used to stretch Route 101')
    ap.add_argument('--south-gap', type=int, default=1,
                    help='rows of plain (blocked) grass between the map south edge and the forest outside it. '
                         'The Gen 5 camera looks from the south, so trees right below walkable tiles hide the player.')
    a = ap.parse_args()
    plan = (dict(size=[0, 0], tiles=[], walkable=[], trees=[], trees_below_edge=[], warps=[], signs=[], buildings=[])
            if a.plan == 'forest' else json.load(open(os.path.join(HERE, '..', 'data', 'plans', f'{a.plan}.json'))))
    ox, oz = map(int, a.offset.split(',')); cx, cz = map(int, a.cell.split(','))
    W, H = plan['size']
    tiles = plan['tiles']; walk = plan['walkable']
    N = a.extend_north
    if N:  # Sapphire row 0 stays at chunk row oz; rows oz-N..oz-1 repeat Sapphire rows 0-1
        assert N % 2 == 0 and oz >= N
        tiles = [tiles[k % 2] for k in range(N)] + tiles
        walk = [walk[k % 2] for k in range(N)] + walk
        plan['trees'] = [[x, y - 2 * k] for x, y in plan['trees'] if y == 0 for k in range(1, N // 2 + 1)] + plan['trees']
    top = oz - N                     # chunk row of tiles[0]
    inside = lambda tx, tz: 0 <= tx - ox < W and 0 <= tz - top < H + N
    cell = lambda tx, tz: tiles[tz - top][tx - ox]

    m = Model(a.plan.lower())
    ground(m)
    occupied = set(); trees = set()
    def place_tree(tx, tz):
        trees.add((tx, tz))
        for dx in (0, 1):
            for dz in (0, 1): occupied.add((tx + dx, tz + dz))
    # Sapphire's own trees (anchor = top-left of the 2x2), then the ones whose top is just below the map edge
    for x, y in plan['trees']:
        place_tree(x + ox, y + oz)
    for x, y in plan['trees_below_edge']:
        if y + oz + a.south_gap + 1 < 32:     # skip trees that would fall into the next chunk
            place_tree(x + ox, y + oz + a.south_gap)
    south = oz + H + a.south_gap      # first forest row below the map
    # forest everywhere outside the map, on the same 2-tile grid as Sapphire's trees
    rows = list(range(-1, oz + H, 2)) + list(range(south, 32, 2))
    for tz in rows:
        for tx in range(0, 32, 2):
            cells = [(tx + dx, tz + dz) for dx in (0, 1) for dz in (0, 1)]
            if any(c in occupied for c in cells): continue
            if all(not inside(*c) for c in cells if 0 <= c[1] < 32):
                place_tree(tx, tz)
    for tz in sorted({t[1] for t in trees}):           # draw trees as rows of side-by-side trees
        xs = sorted(t[0] for t in trees if t[1] == tz)
        run = [xs[0]]
        for x in xs[1:] + [None]:
            if x is not None and x == run[-1] + 2: run.append(x); continue
            tree_row(m, run[0], tz, len(run))
            if x is not None: run = [x]
    is_path = lambda tx, tz: inside(tx, tz) and cell(tx, tz) == 'path'
    ledges = {}; grass_rows = {}
    # decals and ground features
    for y in range(H + N):
        for x in range(W):
            c = tiles[y][x]; tx, tz = x + ox, y + top
            if c == 'path':
                path_tile(m, tx, tz, is_path)
            elif c == 'tall_grass':
                grass_rows.setdefault(tz, []).append(tx)
            elif c == 'ledge_s':
                ledges.setdefault(tz, []).append(tx)
            if c == 'flowers':
                flat_decal(m, 'hana01.1', tx, tz, 1, 1, 2)
            elif c == 'sand_patch':
                m.quad('michi_hage', [(ux(tx) - 8, 3, uz(tz) + 24, 0, 0), (ux(tx) + 24, 3, uz(tz) + 24, 1, 0),
                                      (ux(tx) + 24, 3, uz(tz) - 8, 1, 1), (ux(tx) - 8, 3, uz(tz) - 8, 0, 1)])
    def runs(xs):
        xs = sorted(xs); out = [[xs[0], xs[0]]]
        for x in xs[1:]:
            if x == out[-1][1] + 1: out[-1][1] = x
            else: out.append([x, x])
        return out
    for tz, xs in ledges.items():            # one lip per run of adjacent ledge tiles
        for x0, x1 in runs(xs): ledge_run(m, x0, x1, tz)
    for tz, xs in grass_rows.items():        # one quad per layer per run of tall grass
        for x0, x1 in runs(xs): tall_grass_run(m, x0, x1, tz)
    os.makedirs(a.out, exist_ok=True)
    # CTRMap's importer reads each texture's image from beside the .dae (its size sets the texture matrix), so copy
    # the area's real texture images there under their exact game names (apicula writes '.' as '_').
    import shutil
    texdir = os.path.join(HERE, '..', 'work', 'tex', 'area2')
    for mat in m.tris:
        shutil.copy(os.path.join(texdir, mat.replace('.', '_') + '.png'), os.path.join(a.out, mat + '.png'))
    ntri = m.write(os.path.join(a.out, 'terrain.dae'),
                   wrap={'ki02ax': ('WRAP', 'CLAMP'), 'ki03ax': ('WRAP', 'CLAMP'), 'ki02c': ('WRAP', 'CLAMP'),
                         'ki03bx': ('WRAP', 'CLAMP'), 'ki03dx': ('WRAP', 'CLAMP'), 'michi_hage': ('CLAMP', 'CLAMP'),
                         'michi01a': ('WRAP', 'CLAMP'), 'dansa01a': ('WRAP', 'CLAMP'),
                         'kusa_ec1': ('WRAP', 'CLAMP'), 'kusa_ec2': ('WRAP', 'CLAMP'), 'kusa_ec3': ('WRAP', 'CLAMP')})

    # collision
    per = bytearray(struct.pack('<HH', 32, 32))
    grid = []
    for tz in range(32):
        row = ''
        for tx in range(32):
            c = cell(tx, tz) if inside(tx, tz) else None
            ok = c is not None and walk[tz - top][tx - ox] and c not in ('sign', 'building')
            if c == 'ledge_s':
                rec, ch = LEDGE_S, 'v'
            elif not ok:
                rec, ch = SOLID, '#'
            elif c == 'tall_grass':
                rec, ch = TALL_GRASS, 'g'
            elif a.route:
                rec, ch = (ROUTE_PATH, ':') if c == 'path' else (ROUTE_GRASS, '.')
            else:
                rec, ch = WALK, '.'
            per += struct.pack('<HHHH', *rec)
            row += ch
        grid.append(row)

    open(os.path.join(a.out, 'collision.per'), 'wb').write(per)

    # events and placements, in world units (tile*16+8) for entities and chunk-relative units for buildings
    gx = lambda tx: (cx * 32 + tx) * T + 8
    gz = lambda tz: (cz * 32 + tz) * T + 8
    info = dict(plan=a.plan, offset=[ox, oz], cell=[cx, cz], triangles=ntri, extend_north=N,
                warps=[dict(w, world=[gx(w['x'] + ox), 0, gz(w['y'] + oz)], tile=[(cx * 32 + w['x'] + ox), (cz * 32 + w['y'] + oz)])
                       for w in plan['warps']],
                signs=[dict(s, tile=[cx * 32 + s['x'] + ox, cz * 32 + s['y'] + oz]) for s in plan['signs']],
                buildings=[dict(b, chunk_tiles=[b['footprint'][0] + ox, b['footprint'][1] + oz, b['footprint'][2] + ox, b['footprint'][3] + oz],
                                door_tile=[b['door'][0] + ox, b['door'][1] + oz]) for b in plan['buildings']],
                collision=grid)
    json.dump(info, open(os.path.join(a.out, 'chunk.json'), 'w'), indent=1)
    print(f'{a.plan}: {ntri} triangles, {sum(r.count(".") for r in grid)} walkable tiles -> {a.out}')
    print('\n'.join(grid))

if __name__ == '__main__':
    main()
