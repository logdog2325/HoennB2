"""Walkers check (v165_fixes 2026-10-11): every Sapphire walker (MOVEMENT_TYPE_WALK_SEQUENCE_*, WALK_*_AND_*) walked in
Gen 3 on Sapphire's map and in Black 2 on a built ROM's collision, step by step, and compared. Read-only.

    python3 b2tools/loop_check.py ROM [--rooms ROOMS] [--steps N] [--verbose]      (HOENN_VERSION=ruby for a Ruby ROM)

Sapphire (pokeruby src/event_object_movement.c): MovementType_WalkSequence*_Step1 (the third leg ends level with the
start on its axis) + MoveNextDirectionInSequence (back at the start on the fourth leg: the first leg; next tile outside
the range: next leg; any other collision: walk in place), MovementType_WalkBackAndForth (start -> edge -> start ...);
collision GetCollisionAtCoords: range (0 = no limit), map collision bits, MB_IMPASSABLE_* one-way walls of the tile it
leaves and the one it enters, elevation mismatch (the object's elevation vs the tile's, 0/15 match all), other objects.
Black 2 (pokebw2 src/ov012/field_actor_tool.c ActorRouteCollCheckCore; b2tools/move_codes.py for the codes): walk area
(spawn +- areaW/areaH, 0xFFFF no limit), MapTile_BlocksCollision (flags bit 0) and the side-wall classes 0x51-0x58 of the
tile it leaves / enters, a height step >= 20 units, other actors (their spawn tiles), the same leg rules.
Other people count where they spawn (both games); hidden-by-flag people too (a state where they show).

Findings (one line each): 'path'  the Black 2 walk differs from Sapphire's (tiles in Sapphire coordinates), 'stuck'  it
walks in place on a wall (not a person) in Black 2, 'warp'  its path crosses a warp tile or the tile in front of a door,
'trap'  the player standing on its next tile has no other way out (a dead end it walks into), 'missing'  a Sapphire
walker not found in the ROM with a walk code at its tile (a room or map not built, or a scripted mover), 'mirror'  a
walker whose Black 2 route is Sapphire's mirrored (UP_LEFT_RIGHT_DOWN: move_codes.py).
"""
import os, sys, json, struct, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location('npc_check_tool', os.path.join(HERE, 'npc_check.py'))
NC = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(NC)
import zoneheaders
from zones import parse_entities
from terrain import heights as H
import move_codes as MC
import version

V = {0: (0, -1), 1: (0, 1), 2: (-1, 0), 3: (1, 0)}           # Black 2 / our direction numbers: up down left right
NAME = {0: 'U', 1: 'D', 2: 'L', 3: 'R'}
OPP = {0: 1, 1: 0, 2: 3, 3: 2}
SIDE = {0: 'n', 1: 's', 2: 'w', 3: 'e'}
WALL_SIDES = {0x51: 'e', 0x52: 'w', 0x53: 'n', 0x54: 's', 0x55: 'ne', 0x56: 'nw', 0x57: 'se', 0x58: 'sw'}
G3_BLOCK = {0x30: 'e', 0x31: 'w', 0x32: 'n', 0x33: 's', 0x34: 'ne', 0x35: 'nw', 0x36: 'se', 0x37: 'sw'}
SURF = {0x3d, 0x3e, 0x3f, 0x42, 0x43, 0x40, 0x94, 0x95, 0x96, 0x97}
# Gen 3's third-leg axis per route (pokeruby MovementType_WalkSequence*_Step1: idx 2 ends when x / y is the start's)
AXIS = {'UP_RIGHT_LEFT_DOWN': 'x', 'LEFT_DOWN_UP_RIGHT': 'y', 'UP_LEFT_RIGHT_DOWN': 'x', 'RIGHT_DOWN_UP_LEFT': 'y',
        'LEFT_UP_DOWN_RIGHT': 'y', 'DOWN_RIGHT_LEFT_UP': 'x', 'RIGHT_UP_DOWN_LEFT': 'y', 'DOWN_LEFT_RIGHT_UP': 'x',
        'UP_LEFT_DOWN_RIGHT': 'y', 'DOWN_RIGHT_UP_LEFT': 'y', 'LEFT_DOWN_RIGHT_UP': 'x', 'RIGHT_UP_LEFT_DOWN': 'x',
        'UP_RIGHT_DOWN_LEFT': 'y', 'DOWN_LEFT_UP_RIGHT': 'y', 'LEFT_UP_RIGHT_DOWN': 'x', 'RIGHT_DOWN_LEFT_UP': 'x'}
DIRN = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3}


def route_of(name):
    """(four directions, third-leg axis) of a route (a Gen 3 WALK_SEQUENCE_ name; Black 2 code c walks
    move_codes.SEQUENCES[c - 21])."""
    return [DIRN[w] for w in name.split('_')], AXIS.get(name)


def walk(start, route, d0, area, blocked, steps):
    """Positions of a walker for `steps` steps (route: a WALK_SEQUENCE_ name, or None = back and forth from d0):
    blocked(pos, d) -> None | 'range' | reason."""
    pos, out, stuck = start, [start], []
    if route is None:
        cur, idx = d0, 0
        for _ in range(steps):
            if idx and pos == start: idx = 0; cur = OPP[cur]
            c = blocked(pos, cur)
            if c == 'range':
                idx += 1; cur = OPP[cur]; c = blocked(pos, cur)
            if c: stuck.append((pos, NAME[cur], c))
            else: pos = (pos[0] + V[cur][0], pos[1] + V[cur][1])
            out.append(pos)
        return out, stuck
    route, axis = route_of(route)
    idx = 0
    for _ in range(steps):
        if idx == 2 and axis and (pos[0] == start[0] if axis == 'x' else pos[1] == start[1]): idx = 3
        if idx == 3 and pos == start: idx = 0
        d = route[idx]; c = blocked(pos, d)
        if c == 'range':
            idx += 1
            if idx > 3: stuck.append((pos, 'leg 5', 'route runs past its fourth leg')); break
            d = route[idx]; c = blocked(pos, d)
        if c: stuck.append((pos, NAME[d], c))
        else: pos = (pos[0] + V[d][0], pos[1] + V[d][1])
        out.append(pos)
    return out, stuck


def cycle(ps):
    """The repeating part of a position list (from its second half)."""
    tail = ps[len(ps) // 2:]
    for n in range(1, len(tail) // 2 + 1):
        if all(tail[i] == tail[i + n] for i in range(len(tail) - n)): return tail[:n]
    return tail


# ------------------------------------------------------------------------------------------------- Black 2 (ROM)
class Rom:
    def __init__(self, path):
        f = NC.Files(path)
        self.hdr = zoneheaders.parse(f.narc(12)[0])
        self.matrices, self.chunks, self.ents = f.narc(9), f.narc(8), f.narc(126)
        self._lay, self._ent = {}, {}

    def entities(self, zone):
        e = self.hdr[zone]['entities']
        if e not in self._ent: self._ent[e] = parse_entities(self.ents[e])[0]
        return self._ent[e]

    def recs(self, matrix, x, z):
        """[(a, b, class, flags)] layer records of a tile (empty outside the matrix / no chunk)."""
        if x < 0 or z < 0: return []
        key = (matrix, x // 32, z // 32)
        if key not in self._lay:
            d = self.matrices[matrix]
            fmt, _, w, h = struct.unpack_from('<HHHH', d, 0)
            cx, cz = x // 32, z // 32
            out = []
            if cx < w and cz < h:
                c = struct.unpack_from('<I', d, 8 + 4 * (cz * w + cx))[0]
                if c != 0xFFFFFFFF:
                    blob = self.chunks[c]
                    n = struct.unpack_from('<H', blob, 2)[0]
                    offs = struct.unpack_from('<%dI' % (n + 1), blob, 4)
                    secs = [blob[offs[i]:offs[i + 1]] for i in range(n)]
                    out = [secs[1]] if blob[:2] == b'WB' else [secs[1], secs[2]] if blob[:2] == b'GC' else []
            self._lay[key] = out
        res = []
        for L in self._lay[key]:
            r = struct.unpack_from('<HHI', L, 4 + 8 * ((z % 32) * 32 + x % 32))
            res.append((r[0], r[1], r[2] & 0xFFFF, r[2] >> 16))
        return res

    @staticmethod
    def y(r, x, z):
        a, i = r[0], r[1]
        if a & 3: return None
        nx, ny, nz = H.NORMALS[a >> 2]
        return -(nx * ((x % 32) * 16 - 248) - nz * ((z % 32) * 16 - 248) + H.OFFS[i]) / ny


def pick(rom, m, p, y):
    best, bd = None, 1e9
    for r in rom.recs(m, *p):
        yy = Rom.y(r, *p); yy = y if yy is None else yy
        if abs(yy - y) < bd: bd, best = abs(yy - y), (r, yy)
    return best


def b2_blocker(rom, m, start, area, others, y0):
    state = {'y': y0}
    def blocked(p, d):
        n = (p[0] + V[d][0], p[1] + V[d][1])
        aw, ah = area
        if (aw != 0xFFFF and abs(n[0] - start[0]) > aw) or (ah != 0xFFFF and abs(n[1] - start[1]) > ah): return 'range'
        cur = pick(rom, m, p, state['y'])
        nxt = pick(rom, m, n, state['y'])
        if nxt is None: return 'no map'
        rb, yb = nxt
        if rb[3] & 1: return f'solid (class {rb[2]:#x})'
        if cur and SIDE[d] in WALL_SIDES.get(cur[0][2], ''): return f'side wall {cur[0][2]:#x} of its tile'
        if SIDE[OPP[d]] in WALL_SIDES.get(rb[2], ''): return f'side wall {rb[2]:#x}'
        if abs(yb - state['y']) >= 20: return f'height step {yb - state["y"]:+.0f}'
        if n in others: return 'person ' + others[n]
        state['y'] = yb
        return None
    return blocked


# ------------------------------------------------------------------------------------------------- Sapphire
_maps = {}
def sapphire(name):
    if name not in _maps:
        import models_interior as mi
        sm = dict(mi.sapphire_map(name))
        _maps[name] = sm
    return _maps[name]


def g3_blocker(sm, start, rng, elev, others):
    W, Hh = sm['w'], sm['h']
    state = {'e': elev}
    def blocked(p, d):
        n = (p[0] + V[d][0], p[1] + V[d][1])
        rx, ry = rng
        if (rx and abs(n[0] - start[0]) > rx) or (ry and abs(n[1] - start[1]) > ry): return 'range'
        if not (0 <= n[0] < W and 0 <= n[1] < Hh): return 'outside the map'
        if not sm['walk'][n[1]][n[0]]: return 'solid'
        if SIDE[d] in G3_BLOCK.get(sm['beh'][p[1]][p[0]], ''): return 'one-way wall (its tile)'
        if SIDE[OPP[d]] in G3_BLOCK.get(sm['beh'][n[1]][n[0]], ''): return 'one-way wall'
        te = sm['elev'][n[1]][n[0]]
        if state['e'] != 0 and te not in (0, 15) and te != state['e']: return f'elevation {te} vs {state["e"]}'
        if n in others: return 'object ' + others[n]
        if te not in (0, 15): state['e'] = te
        return None
    return blocked


# ------------------------------------------------------------------------------------------------- main
def walkers():
    """Sapphire's walkers: (map, local id, object) for every pokeruby map in this version."""
    out = []
    for d in sorted(os.listdir(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps'))):
        f = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', d, 'map.json')
        if not os.path.exists(f): continue
        j = json.load(open(f))
        for i, o in enumerate(j.get('object_events') or [], 1):
            if MC.walk(o.get('movement_type', ''), (o.get('movement_range_x', 0), o.get('movement_range_y', 0))):
                out.append((j['name'], i, o))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--rooms', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--steps', type=int, default=240)
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    rom = Rom(a.rom)
    L = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps']
    I = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    main_matrix = None
    by_tile = {}                                   # (matrix, x, z) -> [(zone, npc index, npc)]
    for zone, h in enumerate(rom.hdr):
        try: e = rom.entities(zone)
        except Exception: continue
        for i, n in enumerate(e['npcs']): by_tile.setdefault((h['matrix'], n['x'], n['z']), []).append((zone, i, n))
    findings, counts = [], {}
    def say(kind, who, msg):
        findings.append(f'{who}: ({kind}) {msg}'); counts[kind] = counts.get(kind, 0) + 1
    ok = 0
    for mp, lid, o in walkers():
        mv = o['movement_type'][14:]
        rng = (int(o.get('movement_range_x', 0)), int(o.get('movement_range_y', 0)))
        who = f'{mp} #{lid} {o["graphics_id"][14:]} {mv} {rng[0]}x{rng[1]}'
        if mp in L:
            if main_matrix is None:
                z0 = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'][mp]['zone']
                main_matrix = rom.hdr[z0]['matrix']
            m, ox, oz = main_matrix, L[mp]['tile_x'] + 32, L[mp]['tile_z'] + 32
        elif mp in I and os.path.exists(os.path.join(a.rooms, mp, 'room.json')) and version.room_in_version(mp):
            m = rom.hdr[I[mp]['zone']]['matrix']
            ox, oz = json.load(open(os.path.join(a.rooms, mp, 'room.json')))['origin']
        else:
            say('missing', who, 'map or room not built in this version'); continue
        here = [(z, i, n) for z, i, n in by_tile.get((m, ox + o['x'], oz + o['y']), []) if 20 <= n['move'] <= 44]
        if not here:
            other = by_tile.get((m, ox + o['x'], oz + o['y']), [])
            say('missing', who, f'no walker at zone tile ({ox + o["x"]}, {oz + o["y"]})' +
                (f': there: move {[n["move"] for _, _, n in other]}' if other else ': nobody there'))
            continue
        zone, idx, n = here[0]
        want = MC.walk(o['movement_type'], rng)
        if (n['move'], n['dir'], n['areaw'], n['areah']) != (want['move'], want['dir'], want['areaw'], want['areah']):
            say('path', who, f'zone {zone} npc {idx}: move {n["move"]} dir {n["dir"]} area {n["areaw"]}x{n["areah"]}, '
                f'move_codes says {want}')
        # Black 2
        others = {}
        for (mm, x, z), lst in by_tile.items():
            if mm != m: continue
            for zz, j, nn in lst:
                if (zz, j) != (zone, idx) and (x, z) != (n['x'], n['z']): others[(x, z)] = f'zone {zz} npc {j} (uid {nn["uid"]})'
        start = (n['x'], n['z'])
        y0 = pick(rom, m, start, 0)
        y0 = y0[1] if y0 else 0
        best = None
        for r in rom.recs(m, *start):                  # the layer it stands on: the one nearest the ground it spawns on
            yy = Rom.y(r, *start)
            if yy is not None and not (r[3] & 1): best = yy if best is None or abs(yy) < abs(best) else best
        b2route = None if n['move'] == 20 else MC.SEQUENCES[n['move'] - 21]
        b2p, b2s = walk(start, b2route, n['dir'], (n['areaw'], n['areah']),
                        b2_blocker(rom, m, start, (n['areaw'], n['areah']), others, best if best is not None else y0), a.steps)
        # Sapphire
        sm = sapphire(mp)
        objs = {(ob['x'], ob['y']): f'#{k} {ob["graphics_id"][14:]}' for k, ob in enumerate(sm['objects'], 1) if k != lid}
        g3route = mv[14:] if mv.startswith('WALK_SEQUENCE_') else None
        g3p, g3s = walk((o['x'], o['y']), g3route, want['dir'], rng,
                        g3_blocker(sm, (o['x'], o['y']), rng, int(o.get('elevation', 3)), objs), a.steps)
        b2c = [(x - ox, z - oz) for x, z in cycle(b2p)]
        g3c = cycle(g3p)
        mirror = g3route == 'UP_LEFT_RIGHT_DOWN'        # (Black 2's 25 is broken: code 21 walks Sapphire's route mirrored)
        if mirror: g3c = [(2 * o['x'] - x, y) for x, y in g3c]
        if sorted(set(b2c)) != sorted(set(g3c)) or len(b2c) != len(g3c):
            say('path', who, f'Black 2 walks {len(b2c)} steps over {sorted(set(b2c))}, Sapphire {len(g3c)} over {sorted(set(g3c))}'
                + (f'; Black 2 blocked at {b2s[:3]}' if b2s else '') + (f'; Sapphire blocked at {g3s[:3]}' if g3s else ''))
        else:
            ok += 1
            if mirror: say('mirror', who, f'walks Sapphire\'s route mirrored left-right (code 21; Black 2\'s 25 is broken): {sorted(set(b2c))}')
        walls = [s for s in b2s if not s[2].startswith('person')]
        if walls: say('stuck', who, f'walks in place at {[(x - ox, z - oz) for (x, z), _, _ in walls[:3]]}: {walls[0][1]} {walls[0][2]}')
        # warps and doors on its path
        tiles = set(b2c)
        ws = rom.entities(zone)['warps']
        for k, w in enumerate(ws):
            wt = {(w['tile_x'] + i - ox, w['tile_z'] + j - oz) for i in range(max(1, w['w'])) for j in range(max(1, w['h']))}
            front = {(x, y + 1) for x, y in wt} if w.get('type') == 3 else set()
            if tiles & (wt | front): say('warp', who, f'its path {sorted(tiles & (wt | front))} crosses warp {k} of zone {zone} (or the tile in front of its door)')
        # traps: the player on its next tile with no other way out
        cyc = cycle(b2p)
        player_ok = lambda p: any(not (r[3] & 1) for r in rom.recs(m, *p)) and p not in others
        for q, p in zip(cyc, cyc[1:] + cyc[:1]):
            if q == p: continue
            exits = [(p[0] + dx, p[1] + dz) for dx, dz in V.values() if (p[0] + dx, p[1] + dz) != q]
            if not any(player_ok(t) for t in exits):
                say('trap', who, f'the player on {(p[0] - ox, p[1] - oz)} (its next tile from {(q[0] - ox, q[1] - oz)}) has no other way out')
        if a.verbose:
            print(f'{who}: zone {zone} move {n["move"]} dir {n["dir"]} area {n["areaw"]}x{n["areah"]}: Black 2 {b2c}')
    # wanderers (codes 3/4/5, v165_fixes audit): the tiles each can reach inside its area in Black 2 against Sapphire's,
    # warps / door fronts inside it
    import move_audit as MA
    where = MA.locator(rom, a.rooms, os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'))
    wander_n = wander_same = 0
    for mp, lid, o in MA.objects():
        mt = o.get('movement_type', '')
        if 'WANDER' not in mt: continue
        w = where(mp)
        here = [(z, n) for z, i, n in by_tile.get((w[0], w[1] + o['x'], w[2] + o['y']), [])] if w else []
        here = [(z, n) for z, n in here if n['move'] in (3, 4, 5)]
        if not here: continue
        zone, n = here[0]; m, ox, oz = w
        wander_n += 1
        rng = (int(o.get('movement_range_x', 0)), int(o.get('movement_range_y', 0)))
        who = f'{mp} #{lid} {o["graphics_id"][14:]} {mt[14:]} {rng[0]}x{rng[1]}'
        others = {(x, z): 'npc' for (mm, x, z), lst in by_tile.items() if mm == m and (x, z) != (n['x'], n['z'])}
        dirs = {3: (0, 1, 2, 3), 4: (0, 1), 5: (2, 3)}[n['move']]
        start = (n['x'], n['z'])
        def reach(blocked):
            seen, todo = {start}, [start]
            while todo:
                p = todo.pop()
                for d in dirs:
                    q = (p[0] + V[d][0], p[1] + V[d][1])
                    if q not in seen and not blocked(p, d): seen.add(q); todo.append(q)
            return seen
        y0 = next((Rom.y(r, *start) for r in rom.recs(m, *start) if not r[3] & 1 and Rom.y(r, *start) is not None), 0)
        b2 = {(x - ox, z - oz) for x, z in reach(b2_blocker(rom, m, start, (n['areaw'], n['areah']), others, y0))}
        sm = sapphire(mp)
        objs = {(ob['x'], ob['y']): 'obj' for k, ob in enumerate(sm['objects'], 1) if k != lid}
        g3start = (o['x'], o['y'])
        def g3reach():
            blk = g3_blocker(sm, g3start, rng, int(o.get('elevation', 3)), objs)
            seen, todo = {g3start}, [g3start]
            while todo:
                p = todo.pop()
                for d in dirs:
                    q = (p[0] + V[d][0], p[1] + V[d][1])
                    if q not in seen and not blk(p, d): seen.add(q); todo.append(q)
            return seen
        g3 = g3reach()
        if b2 == g3: wander_same += 1
        else:
            extra, miss = sorted(b2 - g3), sorted(g3 - b2)
            say('wander', who, f'zone {zone} move {n["move"]} area {n["areaw"]}x{n["areah"]}: Black 2 reaches {len(b2)} tiles, '
                f'Sapphire {len(g3)}' + (f'; only Black 2: {extra[:6]}' if extra else '') + (f'; only Sapphire: {miss[:6]}' if miss else ''))
        for k, wp in enumerate(rom.entities(zone)['warps']):
            wt = {(wp['tile_x'] + i - ox, wp['tile_z'] + j - oz) for i in range(max(1, wp['w'])) for j in range(max(1, wp['h']))}
            front = {(x, y + 1) for x, y in wt} if wp.get('type') == 3 else set()
            if b2 & (wt | front): say('warp', who, f'wanders onto {sorted(b2 & (wt | front))}: warp {k} of zone {zone} or the tile in front of its door')
    for f in findings: print(f)
    print(f'walkers: {len(walkers())}, same path as Sapphire: {ok}; wanderers: {wander_n}, same area as Sapphire: {wander_same}; findings: {counts}')


if __name__ == '__main__':
    main()
