"""Surf traps and surf-start rules, Gen 3 against a built world (bridge_surf 2026-10-20).

    HOENN_VERSION=... python3 b2tools/surf_trap_check.py [WORLD] [--frames main,...] [--sim]

Two models of the same tiles, both without Fly, Teleport, Dig, Dive and Waterfall (going DOWN a waterfall is free in both:
a forced south current in Gen 3, hm_free's waterfall branch in Black 2):
  Gen 3   states (tile, currentElevation, previousElevation, surfing) from every warp tile, the rules of pokeemerald /
          pokeruby field_player_avatar.c + event_object_movement.c: walking (IsElevationMismatchAt, ObjectEventUpdate-
          Elevation: a 15 tile, new or old, changes nothing; 0 sets current only), surfing off land
          (IsPlayerFacingSurfableFishableWater: the water's elevation mismatches the CURRENT one and PlayerGetElevation()
          = previousElevation is 3), surfing (no mismatch: 0, 1, 15 tiles are passed, under bridges), landing
          (CanStopSurfing: a mismatching tile of elevation 3), ledges.
  Black 2 states (tile, height) from every door's approach tile, outdoor_check.py's rules (layers, the 20-unit step,
          CheckSurfHeightAllow 0 <= land - water < 20, CheckSurfExitEvent + NOLAND, ledges).
A TRAP is a state reachable from a start from which no start (warp / door approach tile) can be reached. Reported per
connected group of trapped tiles with the moves that enter it. Also listed: tiles where one game starts a surf and the
other refuses it (the surf-off rule), each with the heights. --sim: a world built before heights.py's NOSURF (step 12b):
the same tiles by the same rule (static_nosurf). On the v1.0.4-era world (bridges' world_base) it finds the reported trap:
Route 119's pocket north of the Weather Institute bridge, entered by surfing off the deck (8 over the water then).
Notes: notes/TERRAIN_WATER.md "Surf start and surf traps"."""
import os, sys, argparse
from collections import defaultdict, deque
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import outdoor_check as oc
from outdoor_check import DIRS, OPP, LEDGE, JUMP, WALL_SIDES, b2_land, b2_surf, b2_landing, _sap_blocked

S_DIR = {(0, 1): 's', (0, -1): 'n', (1, 0): 'e', (-1, 0): 'w'}
NOSURF = 0x2000         # b2tools/terrain/heights.py step 12b / patches/hm_free.py SurfStartTileType
WATER_CLASSES = {'water', 'deep_water', 'current_n', 'current_s', 'current_e', 'current_w', 'waterfall'}

def gen3(frame, S):
    """Gen 3 state graph: (starts, edges {state: [(state, how)]})."""
    warps = oc._warp_tiles(frame)
    WF = oc.mb('MB_WATERFALL')
    water = lambda b: b is not None and oc.surfable(b[5])
    walkable = lambda b: b is not None and not b[3]
    def mismatch(cur, b):
        return cur != 0 and b[4] not in (0, 15) and b[4] != cur
    def upd(cur, prev, ea, eb):
        if 15 in (ea, eb): return cur, prev
        return eb, (eb if eb not in (0, 15) else prev)
    starts, edges, seen, q = set(), defaultdict(list), set(), deque()
    for k in warps:
        s = S.get(k)
        if s is None or water(s): continue
        z = s[4] if s[4] not in (0, 15) else 3
        st = (k, z, z, 0); starts.add(st); seen.add(st); q.append(st)
    def push(a, st, how):
        edges[a].append((st, how))
        if st not in seen: seen.add(st); q.append(st)
    while q:
        st = q.popleft(); k, cur, prev, surf = st
        if k in warps and st not in starts:                               # (a warp: you leave; it is a start)
            starts.add(st); continue
        a = S.get(k)
        if a is None: continue
        for d, side in DIRS.items():
            n = (k[0] + d[0], k[1] + d[1]); b = S.get(n)
            if b is None: continue
            if _sap_blocked(a[5], side) or _sap_blocked(b[5], OPP[side]): continue
            if surf:
                if a[5] == WF and d != (0, 1): continue                  # (on a waterfall: carried south only)
                if b[5] == WF and d == (0, -1): continue                 # (up a waterfall: Waterfall)
                if n in warps: push(st, (n, 3, 3, 0), 'surf into warp'); continue
                if b[3]: continue
                if mismatch(1, b):
                    if b[4] == 3: push(st, (n, 3, 3, 0), 'land')      # CanStopSurfing
                    continue
                push(st, (n, 1, 1, 1), 'surf')
                continue
            if b[5] in JUMP and JUMP[b[5]] == d:
                k2 = (n[0] + d[0], n[1] + d[1]); c = S.get(k2)
                if walkable(c) and not water(c):
                    push(st, (k2,) + upd(cur, prev, a[4], c[4]) + (0,), 'ledge')
                continue
            if n in warps: push(st, (n, cur, prev, 0), 'warp'); continue
            if b[3]: continue
            if water(b):
                if mismatch(cur, b) and prev == 3 and b[5] != WF:
                    push(st, (n, 1, 1, 1), 'surf off')                    # IsPlayerFacingSurfableFishableWater
                continue
            if mismatch(cur, b): continue
            push(st, (n,) + upd(cur, prev, a[4], b[4]) + (0,), 'walk')
    return starts, edges

def black2(frame, sim=()):
    """Black 2 state graph on the built collision: (starts, edges {state: [(state, how)]}). States (tile, height)."""
    import world as W_
    front = lambda t, y: frame.rec(*t, W_._b2_front_y(y))
    sides = lambda r: WALL_SIDES.get(r[2], '') if r else ''
    starts, edges, seen, q = set(), defaultdict(list), set(), deque()
    def key(t, r): return (t, round(frame.y(*t, r), 2))
    for d, zid in oc._doors(frame):
        dx, dz = W_.DOOR_STEP.get(d.get('dir', 2), (0, 1))
        s = ((d['x'] - 8) // 16 + dx, (d['z'] - 8) // 16 + dz)
        r = frame.land(*s)
        if b2_land(r) and frame.y(*s, r) is not None:
            st = key(s, r); starts.add(st)
            if st not in seen: seen.add(st); q.append(st)
    def push(a, t, r, how):
        if frame.y(*t, r) is None: return
        st = key(t, r); edges[a].append((st, how))
        if st not in seen: seen.add(st); q.append(st)
    while q:
        st = q.popleft(); a, ya = st; ra = frame.rec(*a, ya)
        if ra is None: continue
        for d in DIRS:
            b = (a[0] + d[0], a[1] + d[1]); rb = frame.rec(*b, ya)
            if rb is None: continue
            if b2_surf(ra):
                if ra[2] == 0x40 and d != (0, 1): continue                # (on a waterfall: down only)
                if b2_landing(frame, a, b, front(b, ya)):
                    push(st, b, rb, 'land' if b2_land(rb) else 'land STUCK')
                    continue
                if b2_surf(rb):
                    if rb[2] == 0x40 and d == (0, -1): continue           # (Waterfall)
                    yb = frame.y(*b, rb)
                    if yb is not None and (abs(ya - yb) < 20 or 0x40 in (ra[2], rb[2])): push(st, b, rb, 'surf')
                continue
            if rb[2] in LEDGE and LEDGE[rb[2]] == d and b2_land(ra):
                c = (b[0] + d[0], b[1] + d[1]); rc = frame.rec(*c, ya)
                if b2_land(rc): push(st, c, rc, 'ledge')
                continue
            rf = front(b, ya)
            if b2_surf(rf):
                yf = frame.y(*b, rf)
                if ra[3] & NOSURF or a in sim: continue                    # (hm_free SurfStartTileType: Gen 3's rule)
                if yf is not None and 0 <= ya - yf < 20 and rf[2] != 0x40:
                    push(st, b, rb, 'surf off' if b2_surf(rb) else 'surf off STUCK')
                continue
            if not b2_land(rb) or not b2_land(ra): continue
            yb = frame.y(*b, rb)
            if yb is None or abs(ya - yb) >= 20: continue
            if DIRS[d] in sides(ra) or OPP[DIRS[d]] in sides(rb): continue
            push(st, b, rb, 'walk')
    return starts, edges

def traps(starts, edges):
    """States reached from the starts that reach no start: {state}, plus the entering edges."""
    reach = set(edges) | {t for v in edges.values() for t, _ in v} | set(starts)
    rev = defaultdict(list)
    for a, v in edges.items():
        for b, how in v: rev[b].append(a)
    co, q = set(starts), deque(starts)
    while q:
        b = q.popleft()
        for a in rev[b]:
            if a not in co: co.add(a); q.append(a)
    bad = reach - co
    entries = [(a, b, how) for a, v in edges.items() if a in co for b, how in v if b in bad]
    return bad, entries

def regions(tiles):
    tiles = set(tiles); out = []
    while tiles:
        k0 = min(tiles, key=lambda k: (k[1], k[0])); reg, st = {k0}, [k0]; tiles.discard(k0)
        while st:
            x, z = st.pop()
            for dx, dz in DIRS:
                n = (x + dx, z + dz)
                if n in tiles: tiles.discard(n); reg.add(n); st.append(n)
        out.append(reg)
    return out

def where(S, k):
    s = S.get(k)
    return f'{s[0]} ({s[1]},{s[2]}) world {k}' if s else f'world {k}'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('world', nargs='?')
    ap.add_argument('--frames', default='')
    ap.add_argument('--sim', action='store_true', help='refuse surf starts from the static NOSURF tiles (a world built before it)')
    a = ap.parse_args()
    wd = oc.wdir(a.world)
    total = 0
    for f in oc.frames(wd):
        if a.frames and f.name not in a.frames.split(','): continue
        if f.name.startswith('alt_'): continue
        S = oc.Sapphire(f)
        g_st, g_ed = gen3(f, S)
        b_st, b_ed = black2(f, static_nosurf(S) if a.sim else ())
        for game, (st, ed), tile in (('Gen 3', (g_st, g_ed), lambda s: s[0]), ('Black 2', (b_st, b_ed), lambda s: s[0])):
            bad, ent = traps(st, ed)
            for reg in regions({tile(s) for s in bad}):
                if not any(oc.in_only(f, *k) for k in reg): continue
                total += 1
                e = sorted({(tile(x), tile(y), h, (x[1] if game == 'Black 2' else x[1:])) for x, y, h in ent if tile(y) in reg})
                xs = [k[0] for k in reg]; zs = [k[1] for k in reg]
                hs = sorted({s[1] if game == 'Black 2' else s[1:] for s in bad if tile(s) in reg})[:8]
                other = g_st, g_ed if game == 'Black 2' else (b_st, b_ed)
                oreach = {s[0] for s in (g_ed if game == 'Black 2' else b_ed)} | {t[0] for v in (g_ed if game == 'Black 2' else b_ed).values() for t, _ in v}
                print(f'{f.name}: TRAP ({game}) {len(reg)} tiles from {where(S, min(reg, key=lambda k: (k[1], k[0])))} '
                      f'box x{min(xs)}-{max(xs)} z{min(zs)}-{max(zs)} maps {sorted({S.get(k)[0] for k in reg if S.get(k)})} '
                      f'states {hs}; {sum(k in oreach for k in reg)} of its tiles reached in the other game; '
                      f'entered by {[(p, q, h, y) for p, q, h, y in e[:6]]}{" ..." if len(e) > 6 else ""} ({len(e)} entries)')
        # surf starts one game allows and the other refuses (from tiles both games reach on foot)
        g_off = defaultdict(set); b_off = defaultdict(set)
        for s, v in g_ed.items():
            for t, how in v:
                if how == 'surf off': g_off[(s[0], t[0])].add(s[1:3])
        for s, v in b_ed.items():
            for t, how in v:
                if how.startswith('surf off'): b_off[(s[0], t[0])].add((s[1], t[1]))
        g_land = {s[0] for s in g_ed if not s[3]}; b_land = {s[0] for s in b_ed if b2_land(f.rec(s[0][0], s[0][1], s[1]))}
        for (k, n) in sorted(set(g_off) | set(b_off), key=lambda p: (p[0][1], p[0][0])):
            if not oc.in_only(f, *k): continue
            if (k, n) in g_off and (k, n) not in b_off and k in b_land:
                print(f'{f.name}: surf-off {where(S, k)} -> {n}: Gen 3 allows (elev {sorted(g_off[(k, n)])}), Black 2 '
                      f'refuses (heights {sorted({s[1] for s in b_ed if s[0] == k})} vs water {f.y(*n)})')
            elif (k, n) in b_off and (k, n) not in g_off and k in g_land:
                gz = sorted({s[1:3] for s in g_ed if s[0] == k and not s[3]})
                print(f'{f.name}: surf-off {where(S, k)} -> {n}: Black 2 allows ({sorted(b_off[(k, n)])}), Gen 3 refuses '
                      f'(standing (current, previous) elevation {gz}, water elevation {S.get(n)[4] if S.get(n) else None})')
    print('traps:', total)


def static_nosurf(S):
    """The static rule for b2tools/terrain/heights.py (NOSURF): walkable land tiles beside surf water where Gen 3's
    player can never start a surf (IsPlayerFacingSurfableFishableWater: previousElevation 3, the current one not 0).
    Elevation 3: allowed. 15 (bridges, walkways): allowed when the group of walkable 15 tiles touches walkable land of
    elevation 3 (the elevation the player carries onto it). 1 (railings: never on foot): no flag. Else (0, 2, 4-14): none."""
    water = lambda s: s is not None and s[6] in WATER_CLASSES      # (the plan's water: heights.py's cls(n) in WATER)
    land = lambda s: s is not None and not s[3] and not oc.surfable(s[5])
    nb = lambda k: [(k[0] + 1, k[1]), (k[0] - 1, k[1]), (k[0], k[1] + 1), (k[0], k[1] - 1)]
    out, comp_ok = {}, {}
    for k, s in S.t.items():
        if not land(s) or not any(water(S.get(n)) for n in nb(k)): continue
        e = s[4]
        if e in (3, 1): continue
        if e == 15:
            if k not in comp_ok:
                comp, st = {k}, [k]
                while st:
                    for n in nb(st.pop()):
                        b = S.get(n)
                        if n not in comp and land(b) and b[4] == 15: comp.add(n); st.append(n)
                carried = {S.get(n)[4] for p in comp for n in nb(p) if n not in comp and land(S.get(n))}
                for p in comp: comp_ok[p] = 3 in carried
            if comp_ok[k]: continue
        out[k] = e
    return out

if __name__ == '__main__':
    main()
