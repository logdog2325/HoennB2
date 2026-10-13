"""Levels for the cave builder (caves_east, 2026-10-06; notes/CAVES.md "Levels, bridges, waterfalls"): terraces
(height seeds), explicit stairs, walk-under bridges (Black 2's second collision layer: 'GC' chunks) and waterfalls
(Black 2's one-row waterfall). Called from b2tools/models_cave.py at four hooks (Cave.classify, Cave.build_terrain,
cave_collision, build); every feature is switched on by its own recipe key, so recipes without them build exactly
as before.

Recipe keys (data/cave_layouts/<Map>.json):
  heights     {"x,y": height}: the connected region of tiles around Sapphire tile (x, y) gets that floor height
              (walkable tiles of the same Sapphire elevation, not crossing stairs/ramps or elevation 0/15 tiles; on a
              water tile: the connected water, not crossing waterfalls, gets that shore level = water 8 below it).
              Black 2's caves step 16 units per tile of rock between floors (Victory Road chunk 780: floors 0 and 16
              with one rock tile between them); the rock lattice reaches 16 per tier (face 16 + top 16), so floors
              N tiers apart need ~2N-1 tiles of rock between them.
  ramps       [[x0, y0, x1, y1, "n"|"s"|"e"|"w"], ...]: stairs: the tiles of the rectangle become slope tiles rising
              toward that side, from the tile before the run to the tile after it (8/16/32 units per tile, or 8-unit
              slopes and flat landings, as models_cave.find_ramps). Elevation-0 stair runs between two heights become
              ramps by themselves (find_ramps, but with the real heights of their ends).
  bridges     true: Sapphire's walk-under bridges (walkable elevation-15 tiles with a higher floor on one axis and a
              lower floor or water on the other) get two collision layers (below).
  waterfalls  true: Sapphire's waterfall columns (MB_WATERFALL, flowing south) become Black 2 waterfalls (below).

Black 2's bridges [code][bytes]: a 'GC' chunk holds two terrain layers (ov036 FieldChunkAccessor_GC_GetTerrain);
FieldG3DMapper_GetTerrain (src/ov036/field_g3d_mapper.c) takes the valid layer whose height is nearest the actor's,
ties to layer 0. Seaside Cave chunk 631 (set 332, the d0 look's): layer 1 = layer 0 except under the bridge, where
layer 0 is the corridor below (y 0) and layer 1 the deck (y 48, class 0x0a); Victory Road 780: the deck in layer 1
(y 0) with its railings = blocked cells at deck height in layer 1 beside it, the canyon (y -40) in layer 0.
Here: layer 0 at a bridge tile = the floor or water below; layer 1 = the deck (class 0x0a, 0x80) at the higher
floor's height; the lower tiles beside the deck (railings) get a blocked layer-1 cell at deck height, the higher
floor tiles at the deck's ends a blocked layer-0 cell at the lower height (so nobody below climbs out at the ends,
the 16-unit steps being under the actors' 20-unit step limit). Deck geometry traced on chunk 631: d_hashi01 at the
deck height, 32 units per u along the bridge, v 0.1..0.9 over the deck's tiles and 0..0.1 / 0.9..1 over 4 units of
overhang on each side; 8-unit side faces (vertex colour 0.45).

Black 2's waterfalls [bytes][test]: one tile row of class 0x40 (flags 0x13, blocked) between two water levels
(Route 11 chunk 72: upper water 72, waterfall cell 32, lower water -8); Waterfall (FieldWaterfallTCB, ov036
0x021bad9c) moves the surfer 2 tiles, up when the water 2 tiles ahead is higher (tested in a cave: (8,15) -> (8,13)).
Sapphire's columns are 3-6 tiles, so the bottom tile of each column becomes the 0x40 cell (at the middle height)
and the tiles above it upper water (class 0x3f); the drop is drawn on the bottom tile as a steep sheet of the
look's "waterfall" texture from the upper to the lower water.
"""
import struct
from collections import defaultdict

STEP = {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}
MB_WATERFALL = 0x13
KEYS = ('heights', 'ramps', 'bridges', 'waterfalls', 'pools', 'void', 'wall_decals')
CHASM = 32            # a plank bridge's chasm: its rock falls this far below the deck

def active(r):
    return any(k in r for k in KEYS)

def _coords(k):
    return tuple(int(v) for v in k.split(','))

# ------------------------------------------------------------------------------------------------ classify hook
def levels(c):
    """After the floor/water heights of models_cave (levels, transitions, water BFS), before find_ramps."""
    r, sm, W, H = c.r, c.sm, c.W, c.H
    elev, beh = sm['elev'], sm['beh']
    inside = lambda x, z: 0 <= x < W and 0 <= z < H
    c.deck, c.rails, c.lift, c.under, c.falls, c.fall_body = {}, {}, {}, {}, {}, set()
    c.plank, c.pool = set(), set()
    # void (recipe "void": [[x0, y0, x1, y1]]): walkable filler Sapphire draws between rooms (e.g. the dark band of the
    # sealed chambers, collision 0 but unreachable) -> rock
    for x0, z0, x1, z1 in r.get('void', []):
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                if c.kind[z][x] != 'arch':
                    c.kind[z][x] = 'rock'; c.fy.pop((x, z), None); c.wy.pop((x, z), None); c.special.pop((x, z), None)
    ramp_side = {}
    for x0, z0, x1, z1, side in r.get('ramps', []):
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1): ramp_side[(x, z)] = side
    is_water = lambda t: c.kind[t[1]][t[0]] == 'water'
    falls = {t for t in c.wy if beh[t[1]][t[0]] == MB_WATERFALL} if r.get('waterfalls') else set()
    # ---- height seeds: flood the region around each seed
    seeded = set()
    for k, h in r.get('heights', {}).items():
        s = _coords(k)
        assert s in c.fy, f'{c.name}: height seed {s} is not a floor or water tile'
        water, e0 = is_water(s), elev[s[1]][s[0]]
        stack, seen = [s], {s}
        while stack:
            t = stack.pop()
            c.fy[t] = h; seeded.add(t)
            if water: c.wy[t] = h - 8
            for dx, dz in STEP.values():
                n = (t[0] + dx, t[1] + dz)
                if n in seen or n not in c.fy or n in ramp_side or n in falls: continue
                if water != is_water(n): continue
                if not water and (elev[n[1]][n[0]] in (0, 15) or elev[n[1]][n[0]] != e0): continue
                seen.add(n); stack.append(n)
    # floors no seed reached that only touch seeded water (a shore of a raised pool, e.g. Meteor Falls 1F_1R (6,9) and
    # (16,9) beside the upper pool): the pool's shore height; they stayed at "levels" and were 88 units below it, out
    # of reach (sweep_caves)
    if r.get('heights'):
        lone = [t for t in c.fy if not is_water(t) and t not in seeded and t not in ramp_side and elev[t[1]][t[0]] not in (0, 15)]
        done = set()
        for t0 in lone:
            if t0 in done: continue
            comp, st = {t0}, [t0]
            while st:
                t = st.pop()
                for dx, dz in STEP.values():
                    n = (t[0] + dx, t[1] + dz)
                    if n in comp or n not in c.fy or is_water(n) or elev[n[1]][n[0]] != elev[t0[1]][t0[0]]: continue
                    comp.add(n); st.append(n)
            done |= comp
            nb = {(t[0] + dx, t[1] + dz) for t in comp for dx, dz in STEP.values()} - comp
            land = [n for n in nb if n in c.fy and not is_water(n)]
            water = [n for n in nb if n in c.fy and is_water(n) and n in seeded]
            if land or not water or any(t in seeded for t in comp): continue
            shore = max(c.fy[n] for n in water)
            for t in comp: c.fy[t] = shore
            c.notes.append(f'floor {min(comp)}..{max(comp)}: only beside the pool seeded {shore}: {shore}')
    # transition tiles (elevation 0/15, not stairs): the highest neighbour that is not one
    if r.get('heights'):
        for (x, z) in list(c.fy):
            if is_water((x, z)) or (x, z) in ramp_side or elev[z][x] not in (0, 15): continue
            n = [c.fy[(x + a, z + b)] for a, b in STEP.values() if (x + a, z + b) in c.fy and not is_water((x + a, z + b))
                 and elev[z + b][x + a] not in (0, 15)]
            if n: c.fy[(x, z)] = max(n)
    # ---- explicit stairs
    lines = defaultdict(list)
    for t, side in ramp_side.items():
        lines[(side, t[0] if side in 'ns' else t[1])].append(t)
    runs = []
    for (side, _), ts in lines.items():
        dx, dz = STEP[side]
        ts.sort(key=lambda t: t[0] * dx + t[1] * dz)            # from the low end (opposite the rise) upward
        cur = [ts[0]]
        for t in ts[1:]:
            if t == (cur[-1][0] + dx, cur[-1][1] + dz): cur.append(t)
            else: runs.append((side, cur)); cur = [t]
        runs.append((side, cur))
    for side, ts in runs:
        dx, dz = STEP[side]
        lo_t, hi_t = (ts[0][0] - dx, ts[0][1] - dz), (ts[-1][0] + dx, ts[-1][1] + dz)
        if lo_t not in c.fy or hi_t not in c.fy:
            c.notes.append(f'ramp {ts[0]}..{ts[-1]}: no floor beyond its ends'); continue
        _ramp_run(c, ts, side, c.fy[lo_t], c.fy[hi_t])
    # ---- elevation-0 stair runs between two heights (find_ramps with the real heights)
    if r.get('heights'):
        walk = lambda t: inside(*t) and sm['walk'][t[1]][t[0]] and c.kind[t[1]][t[0]] == 'floor'
        stair = lambda t: walk(t) and elev[t[1]][t[0]] == 0 and t not in c.ramps
        for side, (dx, dz) in (('s', (0, 1)), ('e', (1, 0))):
            for t0 in [t for t in sorted(c.fy) if stair(t) and not stair((t[0] - dx, t[1] - dz))]:
                run = [t0]
                while stair((run[-1][0] + dx, run[-1][1] + dz)): run.append((run[-1][0] + dx, run[-1][1] + dz))
                a, b = (t0[0] - dx, t0[1] - dz), (run[-1][0] + dx, run[-1][1] + dz)
                if not (walk(a) and walk(b)) or elev[a[1]][a[0]] in (0, 15) or elev[b[1]][b[0]] in (0, 15): continue
                if c.fy[a] == c.fy[b]: continue
                if c.fy[a] > c.fy[b]:      # rising toward north/west: from the south/east end
                    _ramp_run(c, run[::-1], 'n' if side == 's' else 'w', c.fy[b], c.fy[a])
                else:
                    _ramp_run(c, run, side, c.fy[a], c.fy[b])
    if r.get('bridges'): _bridges(c)
    if falls: _waterfalls(c, falls)
    if r.get('bridges'):
        # Sapphire's plank bridges (data/cave_tiles.json "bridge" metatiles on walkable tiles): a deck over a chasm
        ids = {int(str(v), 0) for v in c.table.get('bridge', [])}
        c.plank = {t for t in c.fy if sm['walk'][t[1]][t[0]] and sm['mt'][t[1]][t[0]] in ids and t not in c.deck
                   and c.kind[t[1]][t[0]] == 'floor' and t not in c.ramps}
    # pools (recipe "pools": [[x0, y0, x1, y1]]): blocked tiles drawn as still water (Sapphire's unsurfable water,
    # e.g. Kyogre's pool), solid at the water's height as Black 2's walls. [x0, y0, x1, y1, {"metatiles": [ids]}]: the
    # blocked tiles of those metatiles instead of the surfable behaviours (Ruby's lava pools, whose behaviours are plain
    # floor; ruby_maps, drawn with the recipe's look_over textures)
    for p in r.get('pools', []):
        from models_cave import SURF
        x0, z0, x1, z1 = p[:4]
        mts = {int(str(v), 0) for v in p[4]['metatiles']} if len(p) > 4 else None
        tiles = {(x, z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1) if c.kind[z][x] == 'rock'
                 and (sm['mt'][z][x] in mts if mts is not None else beh[z][x] in SURF)}
        shore = [c.fy[(x + a, z + b)] for x, z in tiles for a, b in STEP.values() if (x + a, z + b) in c.fy
                 and (x + a, z + b) not in tiles and c.kind[z + b][x + a] != 'water']
        y = max(shore) if shore else 0
        for x, z in tiles:
            c.kind[z][x] = 'water'; c.fy[(x, z)] = y; c.wy[(x, z)] = y - 8; c.pool.add((x, z))

def _ramp_run(c, ts, side, lo, hi):
    """Tiles ts (from the low end) rising toward side from lo to hi: Black 2 slopes of 8/16/32 per tile, or 8-unit
    slopes and flat landings at the top (models_cave.find_ramps)."""
    n, diff = len(ts), hi - lo
    if diff <= 0:
        c.notes.append(f'ramp {ts[0]}..{ts[-1]} toward {side}: {lo} -> {hi} does not rise'); return
    if diff / n in (8, 16, 32): rises = [diff / n] * n
    elif diff % 8 == 0 and diff // 8 <= n: rises = [8] * int(diff // 8) + [0] * (n - int(diff // 8))
    elif diff % 16 == 0 and diff // 16 <= n: rises = [16] * int(diff // 16) + [0] * (n - int(diff // 16))
    else:
        c.notes.append(f'ramp {ts[0]}..{ts[-1]}: {diff} units over {n} tiles (no Black 2 slope): flat'); return
    y = lo
    for t, rr in zip(ts, rises):
        if rr: c.ramps[t] = (side, y, y + rr); c.fy[t] = y + rr / 2
        else: c.fy[t] = y
        y += rr

def _bridges(c):
    sm, W, H = c.sm, c.W, c.H
    elev = sm['elev']
    deckable = lambda t: t in c.fy and elev[t[1]][t[0]] == 15 and sm['walk'][t[1]][t[0]] and c.kind[t[1]][t[0]] == 'floor' \
        and t not in c.ramps
    seen = set()
    for t0 in sorted(c.fy):
        if t0 in seen or not deckable(t0): continue
        comp, stack = {t0}, [t0]
        while stack:
            t = stack.pop()
            for dx, dz in STEP.values():
                n = (t[0] + dx, t[1] + dz)
                if n not in comp and deckable(n): comp.add(n); stack.append(n)
        seen |= comp
        nb = []                                  # (direction, tile, height, water?)
        for t in comp:
            for d, (dx, dz) in STEP.items():
                n = (t[0] + dx, t[1] + dz)
                if n in comp or n not in c.fy: continue
                w = c.kind[n[1]][n[0]] == 'water'
                nb.append((d, n, c.fy[n], w))
        if not nb: continue
        hi = max(h for d, n, h, w in nb if not w) if any(not w for _, _, _, w in nb) else None
        low = [x for x in nb if x[3]] or [x for x in nb if x[2] < (hi if hi is not None else 0)]
        if hi is None or not low:
            continue
        lo = min(x[2] for x in low)
        if hi - lo < 1: continue
        his = [d for d, n, h, w in nb if not w and h == hi]
        axis = 'ew' if sum(d in 'ew' for d in his) >= sum(d in 'ns' for d in his) else 'ns'
        water = any(x[3] for x in low)
        wy = min(c.wy[x[1]] for x in low if x[3]) if water else None
        for t in comp:
            c.deck[t] = hi
            c.fy[t] = lo
            if water:
                c.kind[t[1]][t[0]] = 'water'; c.wy[t] = wy; c.under[t] = 'water'
            else: c.under[t] = 'floor'
        for d, n, h, w in nb:
            if (d in 'ns') == (axis == 'ew'):     # beside the deck: the lower level -> railing at deck height
                if h < hi or w: c.rails[n] = hi
            elif h == hi and not w:               # the deck's ends: the higher floor -> blocked below
                c.lift[n] = lo
        c.notes.append(f'bridge {min(comp)}..{max(comp)}: deck {hi} ({axis}) over {"water" if water else "floor"} {lo}')

def _waterfalls(c, falls):
    """Each waterfall column (flowing south): its bottom tile -> Black 2's 0x40 cell at the middle height, the
    tiles above it -> upper water."""
    by_x = defaultdict(list)
    for x, z in falls: by_x[x].append(z)
    for x, zs in by_x.items():
        zs.sort()
        runs, cur = [], [zs[0]]
        for z in zs[1:]:
            if z == cur[-1] + 1: cur.append(z)
            else: runs.append(cur); cur = [z]
        runs.append(cur)
        for run in runs:
            top, bot = (x, run[0] - 1), (x, run[-1] + 1)
            up = c.wy.get(top); low = c.wy.get(bot)
            if up is None or low is None or up <= low:
                c.notes.append(f'waterfall ({x},{run[0]})..({x},{run[-1]}): water above {up} / below {low}: left flat'); continue
            for z in run[:-1]:
                c.wy[(x, z)] = up; c.fy[(x, z)] = up + 8; c.fall_body.add((x, z))
            b = (x, run[-1])
            c.falls[b] = (up, low)
            c.wy[b] = 8 * round((up + low) / 16); c.fy[b] = up + 8          # (a height the offset table has)

# ------------------------------------------------------------------------------------------------ geometry hook
def geometry(c):
    """Bridge decks and waterfall sheets (after models_cave draws everything else)."""
    L = c.look
    C = lambda v: v - 256
    decks = set(c.deck) | set(getattr(c, 'plank', ()))
    if decks:
        tex = L.get('bridge')
        assert tex, f'{c.name}: look {c.look_name} has no "bridge" texture'
        top = lambda t: c.deck.get(t, c.fy[t])
        for comp in _components(decks):
            xs = [t[0] for t in comp]; zs = [t[1] for t in comp]
            ew = (max(xs) - min(xs)) >= (max(zs) - min(zs))      # the walking axis: the longer side
            if ew: B0, B1 = c.lz(min(zs)), c.lz(max(zs) + 1)
            else: B0, B1 = c.lx(min(xs)), c.lx(max(xs) + 1)
            span = B1 - B0
            def P(a, b, y, col):
                v = 0.1 + 0.8 * (b - B0) / span if B0 <= b <= B1 else (0.0 if b < B0 else 1.0)
                x, z = (a, b) if ew else (b, a)
                return (C(x), y, C(z), a / 32, v, (col,) * 3)
            pieces = defaultdict(list)                          # (piece, across, height) -> [(a0, a1)]: tiles side
            for t in comp:                                      # by side merge into one quad (sweep_caves: size)
                hi = top(t)
                a0, a1 = (c.lx(t[0]), c.lx(t[0] + 1)) if ew else (c.lz(t[1]), c.lz(t[1] + 1))
                b0, b1 = (c.lz(t[1]), c.lz(t[1] + 1)) if ew else (c.lx(t[0]), c.lx(t[0] + 1))
                lo_n, hi_n = ((t[0], t[1] - 1), (t[0], t[1] + 1)) if ew else ((t[0] - 1, t[1]), (t[0] + 1, t[1]))
                ea, eb = ((t[0] - 1, t[1]), (t[0] + 1, t[1])) if ew else ((t[0], t[1] - 1), (t[0], t[1] + 1))
                # into the abutments (2 units), unless the abutment is floor drawn at the deck's height: the overlap
                # was coplanar with it and z-fought in melonDS (sweep_caves)
                flush = lambda n_: n_ in c.fy and c.kind[n_[1]][n_[0]] in ('floor', 'boulder', 'ledge') and n_ not in c.deck and n_ not in decks \
                    and abs(c.fy[n_] - hi) < 0.5
                if ea not in comp and not flush(ea): a0 -= 2
                if eb not in comp and not flush(eb): a1 += 2
                bs = [b0, b1]
                if lo_n not in comp and not flush(lo_n): bs = [b0 - 4] + bs   # 4 units of overhang on the open sides
                if hi_n not in comp and not flush(hi_n): bs = bs + [b1 + 4]   # (not over floor at its own height)
                for b_a, b_b in zip(bs, bs[1:]): pieces[('top', b_a, b_b, hi)].append((a0, a1))
                for side, n_, b in ((0, lo_n, b0 - 4), (1, hi_n, b1 + 4)):
                    if n_ in comp or flush(n_): continue        # 8-unit side faces
                    pieces[('side', side, b, hi)].append((a0, a1))
            for (kind, p1, p2, hi), spans in pieces.items():
                spans.sort(); runs = [list(spans[0])]
                for a0, a1 in spans[1:]:
                    if abs(a0 - runs[-1][1]) < 1e-6: runs[-1][1] = a1
                    else: runs.append([a0, a1])
                for a0, a1 in runs:
                    if kind == 'top':
                        _quad_up(c.m, tex, [P(a0, p2, hi, 1.0), P(a1, p2, hi, 1.0), P(a1, p1, hi, 1.0), P(a0, p1, hi, 1.0)])
                        continue
                    # the side facing out (away from the deck), none facing north (the camera never sees it): both
                    # windings doubled them (sweep_caves: chunk size)
                    out = (-1 if p1 == 0 else 1)
                    if ew and out < 0: continue
                    q = [P(a0, p2, hi, 0.45), P(a1, p2, hi, 0.45), P(a1, p2, hi - 8, 0.45), P(a0, p2, hi - 8, 0.45)]
                    q = [(v[0], v[1], v[2], v[3], 0.94 if v[1] < hi else 1.0, v[5]) for v in q]
                    for tri in ([q[0], q[1], q[2]], [q[0], q[2], q[3]]):
                        (ax_, ay_, az_), (bx_, by_, bz_), (cx_, cy_, cz_) = [v[:3] for v in tri]
                        nx_ = (by_ - ay_) * (cz_ - az_) - (bz_ - az_) * (cy_ - ay_)
                        nz_ = (bx_ - ax_) * (cy_ - ay_) - (by_ - ay_) * (cx_ - ax_)
                        n_out = nz_ * out if ew else nx_ * out
                        c.m.tri(tex, tri if n_out > 0 else [tri[0], tri[2], tri[1]])
        # the chasm's walls under the ends of a plank bridge: from the chasm up to the floor beyond (also the floor or
        # water under a walk-under deck next to it: the background showed between the chasm and that corridor;
        # sweep_caves)
        for t in getattr(c, 'plank', ()):
            for d, (dx, dz) in STEP.items():
                n = (t[0] + dx, t[1] + dz)
                if n in c.plank or n not in c.fy or c.kind[n[1]][n[0]] not in ('floor', 'water'): continue
                y_n = c.wy[n] if c.kind[n[1]][n[0]] == 'water' else c.fy[n]
                if dx: p0, p1 = (c.lx(t[0] + (dx > 0)), c.lz(t[1])), (c.lx(t[0] + (dx > 0)), c.lz(t[1] + 1))
                else: p0, p1 = (c.lx(t[0]), c.lz(t[1] + (dz > 0))), (c.lx(t[0] + 1), c.lz(t[1] + (dz > 0)))
                bottom = c.fy[t] - CHASM
                if y_n > bottom + 0.01: c.vwall(L['face_mid'], p0, p1, bottom, y_n, 0.0, L.get('edge', 0.77))
                else:   # the neighbour lies lower (a corridor under a deck beside the chasm): from it (its bank's top
                        # when water: the bank is drawn below) up to the chasm's bottom, seen from that side
                    lo = c.fy[n] if c.kind[n[1]][n[0]] == 'water' else y_n
                    if bottom - lo > 0.01:
                        c.vwall(L['face_mid'], p0, p1, lo, bottom, L.get('edge', 0.77), 0.3, face=(dx, dz))
        # the chasm's bottom under the planks, dark (nothing was drawn there: the background showed between and under
        # the planks; Black 2's own canyon under Victory Road 780's deck has a floor at -40; sweep_caves)
        for comp in _components(set(getattr(c, 'plank', ()))):
            for x0, z0, x1, z1 in __import__('models_cave').rects(comp):
                y = min(c.fy[t] for t in comp) - CHASM
                X0, X1, Z0, Z1 = c.lx(x0), c.lx(x1 + 1), c.lz(z0), c.lz(z1 + 1)
                fs = L.get('floor_size', 64)
                _quad_up(c.m, L['floor'], [(C(X0), y, C(Z1), X0 / fs, -Z1 / fs, (0.25,) * 3), (C(X1), y, C(Z1), X1 / fs, -Z1 / fs, (0.25,) * 3),
                                           (C(X1), y, C(Z0), X1 / fs, -Z0 / fs, (0.25,) * 3), (C(X0), y, C(Z0), X0 / fs, -Z0 / fs, (0.25,) * 3)])
        # the rock beside the chasm where it lies lower than the chasm's floor (a deck's corridor at the corner beside
        # it pulls the rock down): rock faces from it up to the chasm's floor (Shoal Cave's inner room; sweep_caves)
        if getattr(c, 'plank', None):
            c.skirts(set(c.plank), heights={t: c.fy[t] - CHASM for t in c.plank})
    for t, lo in c.lift.items():                               # under a deck's end over water: the abutment's face
        for d, (dx, dz) in STEP.items():
            n = (t[0] + dx, t[1] + dz)
            if c.under.get(n) != 'water': continue
            if dx: p0, p1 = (c.lx(t[0] + (dx > 0)), c.lz(t[1])), (c.lx(t[0] + (dx > 0)), c.lz(t[1] + 1))
            else: p0, p1 = (c.lx(t[0]), c.lz(t[1] + (dz > 0))), (c.lx(t[0] + 1), c.lz(t[1] + (dz > 0)))
            # (from the water's bank top: models_cave.water draws the bank below it, in the same plane; sweep_caves)
            c.vwall(L['face_mid'], p0, p1, max(c.wy[n], c.fy.get(n, c.wy[n])), c.fy[t], L.get('edge', 0.77), L.get('edge', 0.77))
    # wall decals (recipe "wall_decals": [{"at": [x, y], "w": tiles, "tex": name, "h": units, "tier": 0|1|"top"}]): a panel on
    # the rock face north of floor tile (x, y) .. (x + w - 1, y), facing south, in front of the face's steep middle band
    # (5 units from the face's foot, 3.5 .. 3.5 + h above it; tier 1 = the second face, 32 units further back and 16
    # up; "top": a slab standing on the wall's top behind a door's arch): e.g. the sealed chambers' braille wall as Black 2's d29_door1 stone panel (its regi chambers' set)
    for d in c.r.get('wall_decals', []):
        x, z = d['at']; w = d.get('w', 1); h = d.get('h', 12); tier = d.get('tier', 0)
        if tier == 'top':        # a slab standing on the wall's top, its foot 36 units back (behind a door's arch)
            y0 = c.fy.get((x, z), 0) + 16 * c.tiers; Z = c.lz(z) - 36
        else:
            y0 = c.fy.get((x, z), 0) + 3.5 + 16 * tier
            Z = c.lz(z) - 5 - 32 * tier                     # tier 1: the second face
        X0, X1 = c.lx(x), c.lx(x + w)
        q = [(C(X0), y0, C(Z), 0.0, 0.0), (C(X1), y0, C(Z), 1.0, 0.0), (C(X1), y0 + h, C(Z), 1.0, 1.0), (C(X0), y0 + h, C(Z), 0.0, 1.0)]
        c.m.tri(d['tex'], [q[0], q[1], q[2]]); c.m.tri(d['tex'], [q[0], q[2], q[3]])
    if c.falls:
        tex = L.get('waterfall') or L['water']
        size = L.get('waterfall_size', 64)
        for (x, z), (up, low) in c.falls.items():
            X0, X1, Z0, Z1 = c.lx(x), c.lx(x + 1), c.lz(z), c.lz(z + 1)
            yt, yb = up + 4, low + 4                           # the sparkle layer's height above each pool
            # the sheet: from the upper water at the tile's north edge down to the lower water at its south edge;
            # u across (x), v down the fall (the look's water texture, animated by the area's SRT)
            q = [(C(X0), yb, C(Z1), X0 / size, (Z1 - Z0 + up - low) / size), (C(X1), yb, C(Z1), X1 / size, (Z1 - Z0 + up - low) / size),
                 (C(X1), yt, C(Z0), X1 / size, 0.0), (C(X0), yt, C(Z0), X0 / size, 0.0)]
            _quad_up(c.m, tex, q)
            # the rock beside the drop: from the sheet up to the rock lattice on the tile's east/west edge (the
            # lattice rises from the upper level there: the background showed between it and the sheet; sweep_caves)
            nzl, nxl = c.Hh.shape
            for dx in (-1, 1):
                n = (x + dx, z)
                if n in c.fy and c.kind[n[1]][n[0]] in ('water', 'floor'): continue
                i = 3 * (x + (dx > 0))
                if not 0 <= i < nxl: continue
                pts = [(c.LZ[j], c.Hh[j, i]) for j in range(3 * z, 3 * z + 4) if 0 <= j < nzl]
                X = X0 if dx < 0 else X1
                for (za, ha), (zb, hb) in zip(pts, pts[1:]):
                    sa, sb = yt + (yb - yt) * (za - Z0) / (Z1 - Z0), yt + (yb - yt) * (zb - Z0) / (Z1 - Z0)
                    if ha > 1e8 or hb > 1e8 or (ha <= sa + 0.01 and hb <= sb + 0.01): continue
                    e = L.get('edge', 0.77)
                    w = [(C(X), sa, C(za), (za + X) / 32, sa / 16, (e,) * 3), (C(X), sb, C(zb), (zb + X) / 32, sb / 16, (e,) * 3),
                         (C(X), max(hb, sb), C(zb), (zb + X) / 32, max(hb, sb) / 16, (1.0,) * 3), (C(X), max(ha, sa), C(za), (za + X) / 32, max(ha, sa) / 16, (1.0,) * 3)]
                    for tri in ([w[0], w[1], w[2]], [w[0], w[2], w[3]]):
                        if len({(round(v[1], 3), round(v[2], 3)) for v in tri}) < 3: continue
                        (ax_, ay_, az_), (bx_, by_, bz_), (cx_, cy_, cz_) = [v[:3] for v in tri]
                        nx_ = (by_ - ay_) * (cz_ - az_) - (bz_ - az_) * (cy_ - ay_)
                        c.m.tri(L['face_mid'], tri if nx_ * -dx > 0 else [tri[0], tri[2], tri[1]])   # (facing the drop)
            streaks = L.get('waterfall_streaks')              # falling drops over the sheet (animated)
            if streaks:
                # 2.2 units in front of the sheet along its normal (it was 1.2-1.3: z-fighting in melonDS; sweep_caves)
                ln = ((yt - yb) ** 2 + (Z1 - Z0) ** 2) ** 0.5
                ny_, nz_ = 2.2 * (Z1 - Z0) / ln, 2.2 * (yt - yb) / ln
                # d0sizuku (16x128) is an atlas: Black 2 maps only texels 13-16 (the falling drop) onto 2-unit-wide strips,
                # 64 texels per 78 units, v rising up the strip (Wellspring chunk 788), and texels 0-10 (the splash) onto
                # floor triangles. Texel column 11 is a solid grey-tan line Black 2 never shows: the whole texture once
                # per tile drew it as a vertical line on every tile of the fall (map_gfx 2026-10-11). So: strips
                # mapped exactly as Black 2's, three per tile, each starting at its own point of the drop's cycle
                for k, sx in enumerate((3.0, 8.5, 13.5)):
                    xa, xb = X0 + sx - 1, X0 + sx + 1
                    ph = ((x * 7 + z * 13 + k * 5) % 16) / 16
                    q2 = [(C(xa), yb + ny_, C(Z1) + nz_, 13 / 16, ph), (C(xb), yb + ny_, C(Z1) + nz_, 1.0, ph),
                          (C(xb), yt + ny_, C(Z0) + nz_, 1.0, ph + ln * 0.5 / 78), (C(xa), yt + ny_, C(Z0) + nz_, 13 / 16, ph + ln * 0.5 / 78)]
                    _quad_up(c.m, streaks, q2)
            foam = L.get('waterfall_foam')
            if foam:                                           # white water where it lands
                # 2 over the pool's sparkle layer (it was 1: z-fighting; sweep_caves)
                q = [(C(X0), yb + 2, C(Z1 + 8), X0 / 16, 1.0), (C(X1), yb + 2, C(Z1 + 8), X1 / 16, 1.0),
                     (C(X1), yb + 2, C(Z1 - 2), X1 / 16, 0.0), (C(X0), yb + 2, C(Z1 - 2), X0 / 16, 0.0)]
                _quad_up(c.m, foam, q)

def _quad_up(m, tex, q):
    from models_cave import up_facing
    for tri in ([q[0], q[1], q[2]], [q[0], q[2], q[3]]):
        m.tri(tex, tri if up_facing(tri) else [tri[0], tri[2], tri[1]])

def _components(tiles):
    out, seen = [], set()
    for t0 in sorted(tiles):
        if t0 in seen: continue
        comp, stack = {t0}, [t0]
        while stack:
            t = stack.pop()
            for dx, dz in STEP.values():
                n = (t[0] + dx, t[1] + dz)
                if n in tiles and n not in comp: comp.add(n); stack.append(n)
        seen |= comp; out.append(comp)
    return out

# ------------------------------------------------------------------------------------------------ collision hook
def collision(c, cells, flat_record, surf_enc, land_enc=None):
    """Adjust layer-0 cells (zone tile -> (a, height index, class, flags)) for waterfalls and bridges; returns the
    layer-1 cells (None without bridges). land_enc(tile) (wild_tables 2026-10-08): True where Sapphire's tile starts
    wild battles (MB_CAVE ...): the floor under a bridge and the bridge's deck then get flags 0x84 (both: Gen 3 tests the
    tile's behaviour whatever the player's height); None = 0x80 as before."""
    fl_land = lambda t: 0x84 if land_enc and land_enc(t) else 0x80
    sm = c.sm
    for t in getattr(c, 'fall_body', ()):
        cells[(c.ox + t[0], c.oz + t[1])] = (0, flat_record(c.wy[t]), 0x3F, 0x12)
    for t, (up, low) in getattr(c, 'falls', {}).items():
        cells[(c.ox + t[0], c.oz + t[1])] = (0, flat_record(c.wy[t]), 0x40, 0x13)
    for t in getattr(c, 'pool', ()):
        cells[(c.ox + t[0], c.oz + t[1])] = (0, flat_record(c.wy[t]), 0x01, 0x81)
    if not getattr(c, 'deck', None): return None
    for t, under in c.under.items():
        z = (c.ox + t[0], c.oz + t[1])
        if under == 'water':
            enc = any(sm['beh'][t[1] + b][t[0] + a] in surf_enc for a, b in STEP.values()
                      if 0 <= t[0] + a < c.W and 0 <= t[1] + b < c.H and c.kind[t[1] + b][t[0] + a] == 'water')
            cells[z] = (0, flat_record(c.wy[t]), 0x3F, 0x16 if enc else 0x12)
        else:
            cells[z] = (0, flat_record(c.fy[t]), 0x0A, fl_land(t))
    layer1 = dict(cells)
    for t, lo in c.lift.items():
        cells[(c.ox + t[0], c.oz + t[1])] = (0, flat_record(lo), 0x01, 0x81)
    for t, hi in c.deck.items():
        layer1[(c.ox + t[0], c.oz + t[1])] = (0, flat_record(hi), 0x0A, fl_land(t))
    for t, hi in c.rails.items():
        layer1[(c.ox + t[0], c.oz + t[1])] = (0, flat_record(hi), 0x01, 0x81)
    return layer1

def serialize(c, cells, near, flat_record):
    """Per-chunk .per bytes of a cell dict (as models_cave.cave_collision)."""
    out = []
    for cj in range(c.mh):
        for ci in range(c.mw):
            per = bytearray(struct.pack('<HH', 32, 32))
            for zz in range(32 * cj, 32 * cj + 32):
                for zx in range(32 * ci, 32 * ci + 32):
                    if (zx, zz) in cells: per += struct.pack('<HHHH', *cells[(zx, zz)])
                    else: per += struct.pack('<HHHH', 0, flat_record(near.get((zx, zz), 0)), 1, 0x81)
            out.append(bytes(per))
    return out

# ------------------------------------------------------------------------------------------------ output hook
def write_layer1(c, out, meta):
    """collision1.per / collision1_c<k>.per next to the cave's other files, named in room.json (meta)."""
    import os
    layer = getattr(c, 'coll1', None)
    if not layer: return
    open(os.path.join(out, 'collision1.per'), 'wb').write(layer[0])
    meta['collision1'] = 'collision1.per'
    for k, ch in enumerate(meta.get('chunks') or []):
        if not ch: continue
        if k == 0: ch['collision1'] = 'collision1.per'; continue
        open(os.path.join(out, f'collision1_c{k}.per'), 'wb').write(layer[k])
        ch['collision1'] = f'collision1_c{k}.per'

# ------------------------------------------------------------------------------------------------ lattice hook
def lattice(c):
    """models_cave.Cave.lattice for floors at several heights. The rock is still the lower envelope of every floor
    tile's tiered profile (Black 2's walls), but at each lattice point only floors at most `cliff` units (recipe,
    default 16 = one tier) below the nearest floor take part: a floor far below no longer pulls the rock down beside a
    higher one (the rock beside a raised pool or a waterfall channel rises from that pool), and where the two meet the
    rock steps up within one lattice cell (a steep cliff). One-level caves come out exactly as models_cave's lattice."""
    import numpy as np
    from models_cave import LAT, prof
    nx, nz = c.W * 3 + 1, c.H * 3 + 1
    LX = np.array([c.lx(0) + 16 * (i // 3) + LAT[i % 3] for i in range(nx)], float)
    LZ = np.array([c.lz(0) + 16 * (j // 3) + LAT[j % 3] for j in range(nz)], float)
    BIG = 1e9
    # recipe 'reach' (check_postgame 2026-10-07; default unchanged, so every other cave builds as before): how far a
    # floor's capped profile counts. Past the default reach a lower floor no longer caps the rock beside a higher one, so
    # a corner far from the low floors but within reach of a raised one rose to the raised floor's full tiers alone: a
    # lone rock pillar in the black (Altering Cave (31,3)-(31,5), seen from its raised NE room)
    reach = c.r.get('reach', 32 * c.tiers + 48)
    rt = int(np.ceil(reach / 16)) + 1
    src = c.source_tiles()
    plank = set(getattr(c, 'plank', ()))
    for t in plank:                                       # under a plank bridge: a chasm
        if t in src: src[t] -= CHASM
    tol = c.r.get('cliff', 16)
    def boxes():
        for (x, z), y in src.items():
            i0, i1 = max(0, (x - rt) * 3), min(nx, (x + rt + 1) * 3 + 1)
            j0, j1 = max(0, (z - rt) * 3), min(nz, (z + rt + 1) * 3 + 1)
            cx, cz = c.lx(x) + 8, c.lz(z) + 8
            dx = np.maximum(0, np.abs(LX[i0:i1] - cx) - 8)
            dz = np.maximum(0, np.abs(LZ[j0:j1] - cz) - 8)
            yield (x, z) in plank, y, i0, i1, j0, j1, np.maximum(dx[None, :], dz[:, None])
    # pass 1: the nearest floor's height at each point (ties: the lower); NDR: the nearest floor that is no chasm
    ND = np.full((nz, nx), BIG); NY = np.full((nz, nx), BIG); NDR = np.full((nz, nx), BIG)
    for pl, y, i0, i1, j0, j1, d in boxes():
        sd, sy = ND[j0:j1, i0:i1], NY[j0:j1, i0:i1]
        better = (d < sd - 1e-6) | ((np.abs(d - sd) <= 1e-6) & (y < sy))
        sd[better] = d[better]; sy[better] = y
        if not pl: np.minimum(NDR[j0:j1, i0:i1], d, out=NDR[j0:j1, i0:i1])
    # pass 2: lower envelope over the floors no more than `tol` below the nearest one. (sweep_outdoor 2026-10-11) A
    # chasm under a plank bridge takes part, within a tile (16 units) of a real floor, only where it is nearer than that
    # floor (farther out it shapes the rock as before): its profile's flat top
    # (chasm + 16) lay level with a corridor beside it, so the rock tile between them was a flat strip at the
    # corridor's height, blocked (Victory Road 1F/B1F: 30 'invisible walls', walk_diff OPEN); now that rock rises
    # from the corridor and drops into the chasm behind its ridge, as Sapphire's rock face below the bridge. Within one
    # lattice cell (6 units) of a deck the chasm always counts: a rock top there lay in the deck's plane under its
    # overhang (caves_check f: d0yuka_002 / d_hashi01 0 units apart)
    Hh = np.full((nz, nx), BIG); D = np.full((nz, nx), BIG); top_floor = np.zeros((nz, nx), bool)
    DB = np.full((nz, nx), BIG)
    for pl, y, i0, i1, j0, j1, d in boxes():
        ok = y >= NY[j0:j1, i0:i1] - tol - 1e-6
        if pl:      # (only within a tile of a real floor; next to the deck always: under its 4-unit overhang)
            ndr = NDR[j0:j1, i0:i1]
            ok &= (d < ndr - 1e-6) | (d <= 6 + 1e-6) | (ndr > 16 + 1e-6)
        h = np.where(ok, y + prof(d, c.tiers), BIG)
        sub_h, sub_d, sub_b = Hh[j0:j1, i0:i1], D[j0:j1, i0:i1], DB[j0:j1, i0:i1]
        lower, tie = h < sub_h - 1e-6, np.abs(h - sub_h) <= 1e-6
        # DB: the same envelope, but at ties the larger d (a higher floor's edge where a lower floor's face reaches its
        # height is that face's lip): the face bands are chosen by it (models_cave.cell_quad). By D (the smaller d) the
        # cell under a higher floor's edge was taken for a wall foot and drawn with face_low's transparent bottom rows
        # (sweep_caves); D still decides rim and void
        sub_b[tie & (d > sub_b)] = d[tie & (d > sub_b)]; sub_b[lower] = d[lower]
        better = lower | (tie & (d < sub_d))
        sub_h[better] = h[better]; sub_d[better] = d[better]
        top_floor[j0:j1, i0:i1] |= (d == 0) & (np.abs(h - Hh[j0:j1, i0:i1]) < 1e-6)
    c.LX, c.LZ, c.Hh, c.D, c.on_floor, c.DB = LX, LZ, Hh, D, top_floor, DB
    # pass 3 (map_glitch_fix 2026-10-09): the rock beside a drawn floor tile never lies below that floor's own edge. A
    # lower floor or water touching the floor's corner pulled the rock's points along the edge down (inside `tol`): the
    # floor hung out past the rock as a slab with a vertical skirt under it (Meteor Falls 1F_1R's platform at (12,17),
    # over the pool). A point that is also on a lower floor's or water's own edge keeps the envelope (one point cannot be
    # at both heights; raising those opened holes)
    src = c.source_tiles()
    drawn = {t: y for t, y in src.items() if c.kind[t[1]][t[0]] in ('floor', 'boulder', 'ledge') and t not in c.ramps
             and t not in getattr(c, 'plank', ()) and t not in getattr(c, 'deck', {})}
    rock = lambda t: 0 <= t[0] < c.W and 0 <= t[1] < c.H and t not in src and t not in getattr(c, 'cut', set())
    for (x, z), y in drawn.items():
        for i in range(3 * x, 3 * x + 4):
            for j in range(3 * z, 3 * z + 4):
                if not (i in (3 * x, 3 * x + 3) or j in (3 * z, 3 * z + 3)): continue
                if not (0 <= i < nx and 0 <= j < nz) or Hh[j, i] > 1e8 or Hh[j, i] >= y - 1e-6: continue
                around = [(a, b) for a in ([i // 3 - 1, i // 3] if i % 3 == 0 else [i // 3])
                          for b in ([j // 3 - 1, j // 3] if j % 3 == 0 else [j // 3])]
                if not any(rock(t) for t in around) or any(t in src and src[t] < y - 1e-6 for t in around): continue
                Hh[j, i] = y; D[j, i] = 0; DB[j, i] = max(DB[j, i], 16.0); top_floor[j, i] = True

def steep_cell(c, key, tris):
    """A lattice cell where the rock steps from one level's walls to a higher level's (LEVELS.lattice): Black 2's
    tier bands would stretch over the whole step, so it is drawn with the look's middle face texture repeating every
    16 units of height (v) and 32 units along the cliff (u), at the edge colour below and full colour above."""
    if key[0] != 'face': return False
    ys = [p[1] for t in tris for p in t]
    if max(ys) - min(ys) <= 17: return False
    L = c.look
    C = lambda v: v - 256
    us = L.get('face_u', 32)
    e = L.get('edge', 0.77)
    for t in tris:
        (x0, y0, z0, _), (x1, y1, z1, _), (x2, y2, z2, _) = t
        ny = (z1 - z0) * (x2 - x0) - (x1 - x0) * (z2 - z0)
        if ny < 0: t = (t[0], t[2], t[1]); (x0, y0, z0, _), (x1, y1, z1, _), (x2, y2, z2, _) = t
        ax, ay, az = x1 - x0, y1 - y0, z1 - z0
        bx, by, bz = x2 - x0, y2 - y0, z2 - z0
        nx_, nz_ = ay * bz - az * by, ax * by - ay * bx
        lo, hi = min(ys), max(ys)
        if max(y0, y1, y2) - min(y0, y1, y2) < 1e-6:
            # a flat triangle of the cliff cell: the rock top (v = y/16 was one texel row smeared over it; sweep_caves)
            s_, col = L.get('top_size', 16), (L.get('top_color', 0.77),) * 3
            c.m.tri(L['top'], [(C(x), y, C(z), x / s_, -z / s_, col) for x, y, z, d in t]); continue
        verts = []
        for x, y, z, d in t:
            u = ((x if nz_ > 0 else -x) if abs(nz_) >= abs(nx_) else (-z if nx_ > 0 else z)) / us
            col = e + (1.0 - e) * (y - lo) / (hi - lo)
            verts.append((C(x), y, C(z), u, y / 16, (col,) * 3))
        c.m.tri(L['face_mid'], verts)
    return True

def own_floor(c):
    """Tiles models_cave must not draw a floor on: plank bridges (their deck is drawn by geometry)."""
    return set(getattr(c, 'plank', ()))
