"""Walkability diff (walkability agent, 2026-10-11): every built map's walkable tiles against Sapphire's, and our blocked
tiles that look open. One report over the towns, routes, other outdoor maps, interiors, caves and Dive maps.

    python3 b2tools/walk_diff.py [--world WORLD] [--rooms ROOMS] [--rom ROM] [--families town,route,...] [--maps A,B]
                                 [--summary] [--all] [--json OUT]

WORLD: a world.py output (default $HOENN_WORLD_DIR or work/world); ROOMS: the built rooms and caves (default
$HOENN_INTERIORS_DIR or work/interiors); ROM: a built ROM whose zone people mark tiles where someone stands (default
work/rom/hoenn.nds; '-' = none). Read-only: nothing is written except --json.

Sapphire's side is pokeruby's own map (external/pokeruby: map.bin collision bits 10-11, elevation bits 12-15, metatile
behaviours: ledges MB_JUMP_*, water, one-way walls MB_IMPASSABLE_*, doors), placed with the offsets the builders use
(outdoors: world.py's layout origin + margin + shift + pad rows, outdoor_check.frames; rooms and caves: room.json
"origin"). Who reaches what comes from the existing checkers' movement models, so the rules stay the same in one place:
outdoor_check.check_walk (Sapphire: every warp, ledges, surfing, the elevation rule; Black 2: every door's approach
tile, the 20-unit step, side walls 0x51-0x58, ledges, surfing, landings) and caves_check.check_walk (rooms and caves
both, with two collision layers, ice, waterfalls and swimming for the Dive maps).

Families: town (*City, *Town), route (Route*), outdoor (the other outdoor maps: warp-only groups, event islands, other
layouts), interior (data/interior_layouts), cave (data/cave_layouts), dive (cave recipes with "underwater").

Kinds (per tile, in Sapphire map tiles; the zone/world tile in brackets):
  INVISIBLE  walkable in Sapphire and reached there, but blocked in ours: the tile is solid, cut off, or the step into it
             from a tile both reach is refused (height step, side wall)
  THROUGH    blocked in Sapphire, walkable in ours (reached from our doors), or a step Sapphire refuses that we allow
  WATER / LEDGE / LANDING   surf water, ledge direction and surf landings that differ (outdoor_check's kinds)
  OPEN       our tile is blocked, a tile we walk on is next to it, and nothing is drawn there: inside the tile (3 units in
             from its edges) every surface is floor within -6 .. +3.5 units of the neighbour's floor, at least half of
             it covered, no water/black void texture, nothing standing up (tree, wall, model, fence, rock, lip >= 3.5),
             nobody standing on it (the ROM's zone people) and no warp there
Intended differences are listed apart ('intended: why'), not counted as open: outdoor_check's ACCEPT list (Black 2
buildings that are larger, the one-layer Cycling Road, Mirage Island's rim...), room recipes' "block"/"unblock"
(notes/INTERIORS.md), the WALK list below, and OPEN tiles where Sapphire draws the same floor (Sapphire's own invisible
wall: its metatile's colours are all the walkable neighbours' colours).
"""
import os, sys, re, json, math, struct, argparse
from collections import defaultdict, Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches')); sys.path.insert(0, os.path.join(ROOT, 'converter'))

T = 16
INNER = 3.0                           # units in from a tile's near/side edges: what is drawn inside the tile (not its neighbours')
FAR = 0.5                             # units in from its far edge
UP, DOWN = 3.5, 6.0                   # floor band around the neighbour's floor: a ledge lip is 4, water 8 below
# (sweep_outdoor 2026-10-11) + the caves' water (d0_miz / d0_miz2, the d0 and in51 looks) and Ruby's lava (in81_magu00/01):
# Kyogre's pool, Navel Rock's pool and Room 9's lava were counted as floor
WATER_TEX = re.compile(r'(zanami|mizu|kawa0|ike0|umi|water|taki|asase|diving|deep|sea_\w*wave|seaweed|d0_miz|magu)', re.I)
VOID_TEX = re.compile(r'(^black|^kuro|void|cloud)', re.I)
OBJ_TEX = re.compile(r'(saku|iwa|rock|kabe|hei_|fence|ki0[0-4][ab]|ki03|stone_|pole|post)', re.I)   # objects drawn even when flat
GRASS_TEX = re.compile(r'^(kusa_ec|ue_grass|nagakusa)')        # tall grass layers (2/6/8 up) and tufts read as floor
LIP_TEX = re.compile(r'(gake1_|dansa01)')                       # cliff / ledge lips: an edge is drawn there
# the caves' rock tops (looks d0 / in81 / in51 in data/cave_layouts/_looks.json 'top', and their lips): half or less the
# brightness of the look's floor (d0yuka_002 51,59,48 vs d0yuka_001 123,103,82)
ROCK_TOP_TEX = re.compile(r'^(d0yuka_002|in81_yuka02|in51_futa|d0gake_\w+|in81_gake\w*|in51_gake\w*)$')
FAMILIES = ['town', 'route', 'outdoor', 'interior', 'cave', 'dive']
_ROOM_REPO = {}
# where the blocked tile lies seen from the walkable tile next to it (walkable - blocked)
SIDE = {(0, 1): 'back', (0, -1): 'front', (1, 0): 'west', (-1, 0): 'east'}

# Intended differences found by this checker and kept on purpose (family regex, kind regex, line regex, why)
WALK = [
    ('interior', 'INVISIBLE|THROUGH', r'recipe block', "the room recipe's 'block' list: bed heads and other tiles Sapphire "
     "closes with a one-way wall Black 2 has no matching cell for (notes/INTERIORS.md recipe keys)"),
    ('interior', 'THROUGH', r'recipe unblock', "the room recipe's 'unblock' list: another state of the room Sapphire redraws "
     "with setmetatile (Mauville Gym's barriers)"),
    ('interior', 'THROUGH', r'back-wall strip', "the user's option C (2026-10-11): where a bare stretch of the back wall's "
     "lower row lies between pieces, the wall stays flat and the strip in front of it is walkable, one row more than "
     "Sapphire (models_interior.bare_wall_tiles, room.json 'walk_up')"),
    ('interior', 'THROUGH', r'^BattleTower_BattleRoom \(4, 1\): THROUGH move \(4, 1\) -> \(5, 1\)',
     "the Battle Tower's Battle Room is played by script only (src/field_scripts/0030_room_BattleTower_BattleRoom.s: "
     "the player is paused from the arrival to the warp or reset): (4,1) is the opponent's door (Sapphire "
     "MB_ANIMATED_DOOR, no warp) and (5,1) the opponent's own tile; nobody free walks there (Emerald v1.1 list)"),
]


def family_of(name, kind):
    if kind in ('interior', 'cave', 'dive'): return kind
    if re.search(r'(City|Town)(_|$)', name): return 'town'
    if name.startswith('Route'): return 'route'
    return 'outdoor'


# ------------------------------------------------------------------------------------------------- geometry
def clip(poly, lo, hi):
    """Clip a polygon [(x, y, z)] to the xz box lo..hi (Sutherland-Hodgman, y interpolated)."""
    for axis, bound, keep_below in ((0, lo[0], False), (0, hi[0], True), (2, lo[1], False), (2, hi[1], True)):
        if not poly: return poly
        out = []
        for i in range(len(poly)):
            a, b = poly[i - 1], poly[i]
            ina = a[axis] <= bound if keep_below else a[axis] >= bound
            inb = b[axis] <= bound if keep_below else b[axis] >= bound
            if inb:
                if not ina: out.append(_cut(a, b, axis, bound))
                out.append(b)
            elif ina: out.append(_cut(a, b, axis, bound))
        poly = out
    return poly

def _cut(a, b, axis, bound):
    t = (bound - a[axis]) / (b[axis] - a[axis])
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

def area_xz(poly):
    if len(poly) < 3: return 0.0
    return abs(sum(poly[i - 1][0] * poly[i][2] - poly[i][0] * poly[i - 1][2] for i in range(len(poly)))) / 2


class Pieces:
    """What is drawn inside candidate tiles: {tile: [(polygon, |ny|, tex)]} from triangles in zone units (x east,
    z south, y up; tile (x, z) spans x*16 .. x*16+16), each clipped to the tile less FAR on every side."""
    def __init__(self, cand):
        self.cand = set(cand)
        self.by = defaultdict(list)
        if not self.cand: return
        xs = [t[0] for t in self.cand]; zs = [t[1] for t in self.cand]
        self.x0, self.z0 = min(xs) - 1, min(zs) - 1
        W, H = max(xs) - self.x0 + 3, max(zs) - self.z0 + 3
        g = np.zeros((H + 1, W + 1), np.int32)
        for x, z in self.cand: g[z - self.z0 + 1, x - self.x0 + 1] = 1
        self.I = g.cumsum(0).cumsum(1)                 # integral image: any candidate in a tile window
        self.W, self.H = W, H

    def add(self, tex, P):
        """P: (N, 3, 3) triangles of one texture."""
        if not self.cand or len(P) == 0: return
        P = np.asarray(P, float)
        mn, mx = P.min(1), P.max(1)
        tx0 = np.floor((mn[:, 0] + FAR) / T).astype(int) - self.x0; tx1 = np.floor((mx[:, 0] - FAR) / T).astype(int) - self.x0
        tz0 = np.floor((mn[:, 2] + FAR) / T).astype(int) - self.z0; tz1 = np.floor((mx[:, 2] - FAR) / T).astype(int) - self.z0
        a0, a1 = np.clip(tx0, 0, self.W - 1), np.clip(tx1, -1, self.W - 1)
        b0, b1 = np.clip(tz0, 0, self.H - 1), np.clip(tz1, -1, self.H - 1)
        ok = (a1 >= a0) & (b1 >= b0)
        I = self.I
        s = np.zeros(len(P), np.int64)
        s[ok] = (I[b1[ok] + 1, a1[ok] + 1] - I[b0[ok], a1[ok] + 1] - I[b1[ok] + 1, a0[ok]] + I[b0[ok], a0[ok]])
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        ln = np.linalg.norm(n, axis=1); ny = np.abs(n[:, 1]) / np.where(ln > 0, ln, 1)
        for i in np.nonzero(s > 0)[0]:
            tri = [tuple(p) for p in P[i]]
            for tz in range(b0[i], b1[i] + 1):
                for tx in range(a0[i], a1[i] + 1):
                    t = (tx + self.x0, tz + self.z0)
                    if t not in self.cand: continue
                    q = clip(tri, (t[0] * T + FAR, t[1] * T + FAR), (t[0] * T + T - FAR, t[1] * T + T - FAR))
                    if q: self.by[t].append((q, float(ny[i]), tex))

    def region(self, t, side):
        """xz box of tile t to look at from a walkable neighbour on `side` (SIDE: where the tile lies seen from the
        neighbour): INNER in from the near edge and the two lateral edges (what stands there may be the neighbours'),
        FAR from the far edge (anything standing in the tile counts, as far back as its far edge)."""
        X0, Z0 = t[0] * T, t[1] * T
        x0, x1, z0, z1 = X0 + INNER, X0 + T - INNER, Z0 + INNER, Z0 + T - INNER
        if side == 'back': z0 = Z0 + FAR            # (the tile north of the walkable one: its far edge is north)
        elif side == 'front': z1 = Z0 + T - FAR
        elif side == 'west': x0 = X0 + FAR
        elif side == 'east': x1 = X0 + T - FAR
        return (x0, z0), (x1, z1)

    def pieces(self, t, side=None):
        """[(ymin, ymax, |ny|, tex, area)] of what is drawn in tile t's region seen from `side`."""
        lo, hi = self.region(t, side)
        out = []
        for q, ny, tex in self.by.get(t, []):
            r = clip(q, lo, hi)
            if not r: continue
            ys = [p[1] for p in r]
            out.append((min(ys), max(ys), ny, tex, area_xz(r)))
        return out

    def look(self, t, F, side=None):
        """('open' | 'void' | 'drawn: what') of tile t seen from a floor at y F on `side`."""
        ps = self.pieces(t, side)
        if not ps: return 'void'
        (x0, z0), (x1, z1) = self.region(t, side)
        full = (x1 - x0) * (z1 - z0)
        for ymin, ymax, ny, tex, area in sorted(ps, key=lambda p: -p[1]):
            if GRASS_TEX.match(tex) and ny > 0.9 and ymax <= F + 9: continue    # (tall grass layers)
            if OBJ_TEX.search(tex): return f'drawn: {tex}'
            if ymin > F + UP: return f'drawn: {tex} at {ymin - F:+.0f}'          # roofs, plateaus, table tops
            if ny < 0.95 and ymax >= F + 3: return f'drawn: {tex} up to {ymax - F:+.0f}'   # uprights and lips
            if ny < 0.7 and ymin < F - DOWN: return f'drawn: {tex} down to {ymin - F:+.0f}'  # a face going down
        lip = sum(p[4] for p in ps if LIP_TEX.search(p[3]) and p[2] < 0.999 and p[0] < F - 1)
        if lip > 0.3 * full: return 'drawn: a cliff / ledge lip (an edge)'
        floor = [p for p in ps if p[2] >= 0.7 and p[0] >= F - DOWN]
        wet = sum(p[4] for p in floor if WATER_TEX.search(p[3]) or VOID_TEX.search(p[3]))
        dry = sum(p[4] for p in floor) - wet
        if wet > 0.3 * full: return 'drawn: water/void'
        if dry < 0.5 * full:
            low = [p for p in ps if p[2] >= 0.7 and p[1] < F - DOWN]
            return f'drawn: lower ground ({min(p[0] for p in low) - F:+.0f})' if low else 'void'
        return 'open'

    def floor_tex(self, t):
        c = Counter()
        for p in self.pieces(t):
            if p[2] > 0.7: c[p[3]] += p[4]
        return ','.join(k for k, _ in c.most_common(2))


# -------------------------------------------------------------------------------------------- Sapphire's look
_REND = {}
def sapphire_image(repo, name, layout, x, y):
    """RGB (16,16,3) of Sapphire's metatile at (x, y), None outside."""
    key = (name, layout)
    if key not in _REND:
        from gba import MetatileRenderer
        mj = repo.map_json(name)
        g, lay = repo.layout_grid(layout or mj['layout'])
        _REND[key] = (g, MetatileRenderer(repo, lay['primary_tileset'], lay['secondary_tileset']))
    g, mr = _REND[key]
    if not (0 <= y < g.shape[0] and 0 <= x < g.shape[1]): return None
    return mr.render(int(g[y, x]) & 0x3FF)[:, :, :3]

def sapphire_plain(repo, name, layout, s, nbrs):
    """Whether Sapphire draws its blocked tile s with only the colours of its walkable neighbours (floor)."""
    a = sapphire_image(repo, name, layout, *s)
    if a is None: return False
    cols = set()
    for n in nbrs:
        b = sapphire_image(repo, name, layout, *n)
        if b is not None: cols |= {tuple(c) for c in b.reshape(-1, 3)}
    if not cols: return False
    px = [tuple(c) for c in a.reshape(-1, 3)]
    return sum(c in cols for c in px) >= 0.97 * len(px)


# ------------------------------------------------------------------------------------------------ the people
class People:
    """Tiles where the ROM's zone entities put a person or object (any flag), per zone."""
    def __init__(self, rom):
        self.at = defaultdict(set)
        if not rom or rom == '-' or not os.path.exists(rom): self.ok = False; return
        import script_check as SC
        self.rom = SC.Rom(rom)
        self.ok = True
        self._done = {}

    def zone(self, z):
        if not self.ok: return set()
        if z not in self._done:
            try: self._done[z] = {(n['x'], n['z']) for n in self.rom.entities(z)['npcs']}
            except Exception: self._done[z] = set()
        return self._done[z]


# ------------------------------------------------------------------------------------------------------ report
class Report:
    def __init__(self):
        self.rows = []                   # dict(family, map, kind, at, where, msg, why)

    def add(self, family, mapname, kind, at, where, msg, why=None):
        if why is None:
            line = f'{mapname} {at}: {kind} {msg}'
            why = next((w for fam, k, rx, w in WALK if re.match(f'({fam})$', family) and re.match(f'({k})$', kind)
                        and re.search(rx, line)), None)
        self.rows.append(dict(family=family, map=mapname, kind=kind, at=at, where=where, msg=msg, why=why))


# ------------------------------------------------------------------------------------------------------ outdoor
def outdoor(wd, report, people, only_maps=None, families=None):
    import outdoor_check as oc
    import caves_check as cc
    for f in oc.frames(wd):
        out = []
        S = oc.Sapphire(f)
        oc.check_walk(f, out, S)
        reach_s, reach_b, states = f.reach
        for kind, msg, where in out:
            msg = re.sub(r'np\.int64\((-?\d+)\)', r'\1', str(msg))
            m = re.match(r'(\w+) \((-?\d+),(-?\d+)\)', msg)
            name = m.group(1) if m else 'outside'
            fam = family_of(name, 'outdoor')
            if (families and fam not in families) or (only_maps and name not in only_maps): continue
            at = (int(m.group(2)), int(m.group(3))) if m else None
            k = ('LANDING' if 'surf landing' in msg else 'LEDGE' if 'ledge' in msg.split(':', 1)[-1][:40] else
                 'WATER' if 'surf water' in msg else
                 'INVISIBLE' if ('solid in Black 2' in msg or 'cut off in Black 2' in msg or
                                 ('Sapphire allows' in msg and 'Black 2 blocks' in msg)) else 'THROUGH')
            n = int(re.search(r': (\d+) tiles reachable', msg).group(1)) if 'cut off' in msg else 1
            why = oc.accepted(f.name, kind, msg)
            report.add(fam, name, k, at, f'{f.name} world {where}', (f'[{n} tiles] ' if n > 1 else '') + msg.split(': ', 1)[-1], why)
        # OPEN: blocked tiles next to a tile Black 2 walks on, with nothing drawn
        warps = oc._warp_tiles(f)
        doors = {((d['x'] - 8) // 16, (d['z'] - 8) // 16) for d, z in oc._doors(f)}
        cand = defaultdict(list)
        for k in reach_b:
            r = f.land(*k)                     # (a two-layer tile: its land layer; outdoor_check Frame.rec / land)
            if not oc.b2_land(r): continue
            y = f.y(*k, r)
            for d in oc.DIRS:
                n = (k[0] + d[0], k[1] + d[1])
                rn = f.rec(*n, y)
                if rn is None or not oc.in_only(f, *n) or oc.b2_land(rn) or oc.b2_surf(rn) or rn[2] in oc.LEDGE: continue
                if n in warps or n in doors: continue
                cand[n].append((k, y))
        if not cand: continue
        pcs = Pieces(cand)
        cells = sorted({(t[0] // 32 + dx, t[1] // 32 + dz) for t in cand for dx in (-1, 0, 1) for dz in (-1, 0, 1)} & set(f.cells))
        for c in cells:
            for tex, P, UV, C in cc.read_dae(os.path.join(f.cells[c], 'terrain.dae')):
                pcs.add(tex, P + np.array([c[0] * 512 + 256, 0, c[1] * 512 + 256]))
            for res, X, Y, Z, rot in f.placements(c):
                for n_, img, P, UV, A, owner in oc.placed_parts(f, res, X, Y, Z, rot):
                    pcs.add(f'{n_}@res{res}', P)
        zones = zone_lookup(f)
        repo = oc.repo()
        for t in sorted(cand, key=lambda t: (t[1], t[0])):
            s = S.get(t)
            name = s[0] if s else 'outside'
            fam = family_of(name, 'outdoor')
            if (families and fam not in families) or (only_maps and name not in only_maps): continue
            looks = [(k, y, pcs.look(t, y, SIDE[(k[0] - t[0], k[1] - t[1])])) for k, y in cand[t] if y is not None]
            op = [(k, y) for k, y, l in looks if l == 'open']
            if not op: continue
            z = zones(t)
            if t in people.zone(z): continue
            r = f.rec(*t)
            at = (s[1], s[2]) if s else None
            why = None
            if s:
                nb = [S.get(k) for k, y in op]
                nb = [(q[1], q[2]) for q in nb if q and q[0] == s[0]]
                layout = None
                if getattr(f, 'alt_plans', {}).get(s[0]):
                    layout = os.path.basename(f.alt_plans[s[0]])[len(s[0]) + 1:-5]
                sap = 'walkable' if (not s[3]) else 'solid'
                if s[3] and nb and sapphire_plain(repo, s[0], layout, (s[1], s[2]), nb):
                    why = "Sapphire's own invisible wall: it draws the same floor there and blocks it"
                if not s[3] and all(not any(z == 0 or s[4] in (0, 15) or s[4] == z for z in states.get(k, ()))
                                    for k, y in op):
                    why = ("Sapphire's own wall: walkable there only at another elevation (its elevation rule refuses the "
                           "step from this side)")
                detail = (f'blocked (class {r[2]:#x} flags {r[3]:#x}), floor drawn ({pcs.floor_tex(t)}), next to {op[0][0]}; '
                          f'Sapphire {sap} ({s[6]}, {oc.mb_name(s[5])})')
            else:
                detail = f'blocked (class {r[2]:#x} flags {r[3]:#x}), floor drawn ({pcs.floor_tex(t)}), outside every map'
                if S.get((t[0], t[1] - 1)) is not None:
                    why = ("DECISIONS 2026-10-06: the forest outside a map starts one row below its south edge (--south-gap 1: "
                           "Gen 5's camera would hide the player behind trees directly south)")
            report.add(fam, name, 'OPEN', at, f'{f.name} world {t}', detail, why)

def zone_lookup(f):
    W = f.world
    if f.group is None:
        owner = {(c['cx'], c['cz']): c['zone'] for c in W['cells']}; rects = W.get('zone_rects', [])
    else:
        owner = {(c['cx'], c['cz']): c['zone'] for c in next(g for g in W['standalone'] if g['group'] == f.group)['cells']}
        rects = []
    return lambda t: next((zz for x0, z0, x1, z1, zz in rects if x0 <= t[0] <= x1 and z0 <= t[1] <= z1),
                          owner.get((t[0] // 32, t[1] // 32)))


# ------------------------------------------------------------------------------------------------ rooms and caves
def rooms_and_caves(rooms_dir, report, people, only_maps=None, families=None):
    import caves_check as cc
    import models_cave as MC
    import models_interior as mi
    import rooms_check as rc
    import preview_interior as pv
    import version
    pv.OUT = os.environ.get('WALK_DIFF_MODELS') or rooms_dir
    cfgs = {}
    zone_of_room = {}
    for fn in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json'):
        j = json.load(open(fn))
        if j.get('room'):
            cfgs[j['room']] = j
            zone_of_room[j['room']] = int(j['zone'])
    story = cc.load_story()
    em = version.variants() if version.is_emerald() else {}
    if em:                              # (emerald_rooms) Emerald: a room variant is walked with its room's zone json and
        for room, v in em.items():      # story objects (as Emerald places them); the rooms it replaces are not walked
            if room in cfgs: cfgs[v], zone_of_room[v] = cfgs[room], zone_of_room[room]
        story = [o for o in (version.version_object(o) for o in story) if o is not None]
        story = [dict(o, map=em[o['map']]) if o.get('map') in em else o for o in story]
    caves = sorted(x[:-5] for x in os.listdir(MC.LAYOUTS) if x.endswith('.json') and not x.startswith('_'))
    rooms = sorted(x[:-5] for x in os.listdir(mi.LAYOUTS) if x.endswith('.json') and not x.startswith('_'))
    falls = cc.falls_into(rooms_dir, caves)
    names = [(n, 'cave') for n in caves] + [(n, 'interior') for n in rooms if n not in caves]
    for name, kind in names:
        if only_maps and name not in only_maps: continue
        if not os.path.exists(os.path.join(rooms_dir, name, 'room.json')): continue
        if em and (name in em or not version.room_in_version(name)): continue      # (emerald_rooms) not in Emerald's ROM
        if not em and '_Emerald' in name and not version.room_in_version(name): continue   # (Emerald's variants)
        try:
            if kind == 'cave':
                c = cc.Cave(rooms_dir, name, cfgs, story)
                fam = 'dive' if c.underwater else 'cave'
            else:
                c = RoomGrid(rooms_dir, name, cfgs, story)
                fam = 'interior'
        except Exception as ex:
            report.add(kind, name, '!', None, name, f'cannot read: {type(ex).__name__}: {ex}')
            continue
        if families and fam not in families: continue
        try:
            one_room(c, fam, report, people, zone_of_room.get(c.alt_of or name), falls.get(c.alt_of or name, ()))
        except Exception as ex:
            import traceback; traceback.print_exc()
            report.add(fam, name, '!', None, name, f'failed: {type(ex).__name__}: {ex}')


class RoomGrid:
    """A built room read as caves_check.Cave reads a cave (its movement models work on any room)."""
    def __new__(cls, rooms_dir, name, cfgs, story):
        import caves_check as cc
        import models_cave as MC
        import models_interior as mi
        c = cc.Cave.__new__(cc.Cave)
        c.name, c.dir = name, rooms_dir
        c.d = os.path.join(rooms_dir, name)
        c.meta = json.load(open(os.path.join(c.d, 'room.json')))
        c.recipe = mi.load_recipe(name)
        c.alt_of = None
        c.sm = MC.sapphire(c.meta['map'], c.recipe.get('layout'))
        c.ox, c.oz = c.meta['origin']
        c.W, c.H = c.sm['w'], c.sm['h']
        c.cfg = cfgs.get(name)
        c.story = [o for o in story if o.get('map') == name]
        c.look = {}
        c.out = []
        c.underwater = False
        c.c0, c.c1 = {}, {}
        mw, mh = c.meta.get('matrix', [1, 1])
        chunks = c.meta.get('chunks') or [dict(collision=c.meta['collision'], collision1=c.meta.get('collision1'))]
        for k, ch in enumerate(chunks):
            if ch is None: continue
            ci, cj = k % mw, k // mw
            for key, dst in (('collision', c.c0), ('collision1', c.c1)):
                if not ch.get(key): continue
                per = open(os.path.join(c.d, ch[key]), 'rb').read()
                for i in range(1024):
                    dst[(ci * 32 + i % 32, cj * 32 + i // 32)] = struct.unpack_from('<HHHH', per, 4 + 8 * i)
        c.mw, c.mh = mw, mh
        c._tris = None
        c.is_room = True
        return c


def one_room(c, fam, report, people, zone, falls):
    import caves_check as cc
    import preview_interior as pv
    sm = c.sm
    G, B = cc.check_walk(c, falls)
    rec = getattr(c, 'recipe', {}) or {}
    block = {tuple(t) for t in rec.get('block', [])}
    unblock = {tuple(t) for t in rec.get('unblock', [])}
    walk_up = {tuple(t) for t in (getattr(c, 'meta', None) or {}).get('walk_up', [])}   # (option C: back-wall strip)
    # the same tiles check_walk leaves out (doors, arches, mud tops, waterfalls, ledges)
    G3_DOORS = cc.G3_DOORS
    door_tiles = {(w['x'], w['y']) for w in sm['warps'] if c.inside((w['x'], w['y'])) and sm['beh'][w['y']][w['x']] in G3_DOORS}
    arch_tiles = {c.sap((s['x'], s['z'])) for s in c.meta.get('warp_spots', []) if s['kind'] in ('exit', 'door')}
    mud_top = {(x, z) for z in range(c.H) for x in range(c.W) if sm['beh'][z][x] == cc.G3_MUD
               and not (z > 0 and sm['beh'][z - 1][x] == cc.G3_MUD)}
    falls_t = {c.sap(t) for t, cl in c.c0.items() if cl[2] == cc.WATERFALL}
    ledges = {c.sap(t) for t, cl in c.c0.items() if cl[2] in cc.LEDGE}
    skip = door_tiles | arch_tiles | mud_top | falls_t | ledges
    warp_tiles = {(w['x'], w['y']) for w in sm['warps']}
    name = c.name
    if c.underwater:
        g3 = set(G); b2 = set(B)
        for s in sorted(g3 - b2 - skip, key=lambda t: (t[1], t[0])):
            report.add(fam, name, 'INVISIBLE', s, f'zone tile {c.zt(s)}', 'Sapphire swims there, ours cannot' + cell_txt(c, s))
        for s in sorted(b2 - g3 - skip, key=lambda t: (t[1], t[0])):
            report.add(fam, name, 'THROUGH', s, f'zone tile {c.zt(s)}', 'ours swims there, Sapphire cannot' + cell_txt(c, s))
    else:
        for s in sorted(set(G) - set(B) - skip - warp_tiles, key=lambda t: (t[1], t[0])):
            how = 'solid' if not c.walkable(c.zt(s)) else 'cut off'
            note = ' (recipe block)' if s in block else ''
            report.add(fam, name, 'INVISIBLE', s, f'zone tile {c.zt(s)}', f'Sapphire reaches it, ours does not: {how}{cell_txt(c, s)}{note}')
        for s in sorted(set(B) - set(G) - skip - warp_tiles, key=lambda t: (t[1], t[0])):
            note = ' (recipe unblock)' if s in unblock else ' (back-wall strip)' if s in walk_up else ''
            if c.inside(s) and sm['walk'][s[1]][s[0]]:       # walkable in Sapphire too, only not reached from its warps
                report.add(fam, name, 'REACH', s, f'zone tile {c.zt(s)}', 'walkable in both; Sapphire reaches it only in '
                           'another state of the map or by script (not from its warps)' + note,
                           "a reachability difference, not a wall: walkable in both games")
                continue
            sap = f'solid, behaviour {sm["beh"][s[1]][s[0]]:#x}' if c.inside(s) else 'outside the map'
            report.add(fam, name, 'THROUGH', s, f'zone tile {c.zt(s)}', f'ours reaches it, Sapphire does not ({sap}){note}')
    for kind, ln in c.out:
        if kind != 'w' or not ln.split(': (w) ', 1)[1].startswith('move'): continue
        msg = ln.split(': (w) ', 1)[1]
        m = re.match(r'move \((\d+), (\d+)\) -> \((\d+), (\d+)\)', msg)
        s = (int(m.group(1)), int(m.group(2))) if m else None
        n = (int(m.group(3)), int(m.group(4))) if m else None
        k = 'INVISIBLE' if 'Sapphire walks it, Black 2 does not' in msg else 'THROUGH'
        if n in warp_tiles or s in warp_tiles: continue
        why = None
        if n in block or s in block: why = "a step into the room recipe's 'block' tiles"
        elif n in unblock or s in unblock: why = "a step into the room recipe's 'unblock' tiles"
        elif n in walk_up or s in walk_up: why = "a step onto the back-wall strip (the user's option C)"
        report.add(fam, name, k, s, f'zone tile {c.zt(s) if s else "?"}', msg, why)
    # OPEN
    Bz = {c.zt(s): v for s, v in B.items()}
    cand = defaultdict(list)
    for t, states in Bz.items():
        for (y, mode) in states:
            if mode != 'land': continue
            for dx, dz in cc.STEP.values():
                n = (t[0] + dx, t[1] + dz)
                if n not in c.c0 or c.walkable(n): continue
                cl = c.c0[n]
                if cl[2] in cc.LEDGE or cl[2] in cc.WATER or cl[2] == cc.WATERFALL: continue
                s = c.sap(n)
                if s in warp_tiles or s in skip: continue
                cand[n].append((t, y))
    if not cand: return
    pcs = Pieces(cand)
    off = np.array([256, 0, 256])
    for tex, P, UV, C in c.tris:
        pcs.add(tex, P + off)
    res = {m['name']: (m['res'], m['pack']) for m in c.meta.get('models', [])}
    for fu in c.meta.get('furniture', []):
        rid, pack = (fu['m'], next((m['pack'] for m in c.meta['models'] if m['res'] == fu['m']), None)) \
            if isinstance(fu['m'], int) else res.get(fu['m'], (None, None))
        if rid is None: continue
        try: parts = pv.placed(pv.furniture_parts(rid, pack), fu['pos'], fu.get('rot', 0))
        except Exception: continue
        for tp, P, UV, C in parts:
            pcs.add(f'{fu["m"]}:{os.path.basename(tp or "-")[:-4]}', P + off)
    here = people.zone(zone) if zone is not None else set()
    from gba import Repo            # (rooms and caves are built from Sapphire's maps in every version: pokeruby's own,
    repo = _ROOM_REPO.setdefault('r', Repo(os.path.join(ROOT, 'external', 'pokeruby')))    # not Emerald's view)
    sm_name = sm['name']
    if '/' in sm_name:             # (emerald_rooms) a room built from another decomp's map ("pokeemerald/<Folder>", or
        dec, sm_name = sm_name.split('/', 1)            # emerald_caves' "emerald/<Map>": the Emerald view)
        repo = _ROOM_REPO.setdefault(dec, Repo(os.path.join(ROOT, 'external', 'pokeruby'), emerald=True) if dec == 'emerald'
                                     else Repo(os.path.join(ROOT, 'external', dec)))
    layout = rec.get('layout')
    walk_z = defaultdict(list)                    # walkable zone tiles per column (the room's front edge)
    for t in Bz: walk_z[t[0]].append(t[1])
    exits = {(x, z) for sp in c.meta.get('warp_spots', []) if sp['kind'] == 'exit' for x, z in sp.get('tiles', [[sp['x'], sp['z']]])}
    for t in sorted(cand, key=lambda t: (t[1], t[0])):
        op = [(k, y) for k, y in cand[t] if pcs.look(t, y, SIDE[(k[0] - t[0], k[1] - t[1])]) == 'open']
        if not op or t in here: continue
        s = c.sap(t)
        cl = c.c0[t]
        why = None
        nb = [c.sap(k) for k, y in op]
        side = SIDE[(op[0][0][0] - t[0], op[0][0][1] - t[1])]
        inside = c.inside(s)
        if not inside:
            sap = 'outside the map'
        else:
            sap = 'walkable' if sm['walk'][s[1]][s[0]] else f'solid (behaviour {sm["beh"][s[1]][s[0]]:#x})'
            if not sm['walk'][s[1]][s[0]] and sapphire_plain(repo, sm_name, layout, s, [n for n in nb if c.inside(n)]):
                why = "Sapphire's own invisible wall: it draws the same floor there and blocks it"
        if s in block: why = why or "the room recipe's 'block' list"
        if fam == 'interior' and all(SIDE[(k[0] - t[0], k[1] - t[1])] == 'front' for k, y in op) \
                and not any(z > t[1] for z in walk_z.get(t[0], [])):
            why = why or ("the room's front edge: Black 2's rooms end in a floor strip south of the last walkable row "
                          "before the black lip (1,467 such tiles in Black 2's own 372 one-chunk rooms)")
        if any((t[0], t[1] - 1) == e for e in exits):
            why = why or "Black 2's stone genkan notch below the exit mat (models_interior.py, as Black 2's rooms)"
        ftex = [x for x in pcs.floor_tex(t).split(',') if x]
        if fam == 'cave' and ftex and all(ROCK_TOP_TEX.match(x) or WATER_TEX.search(x) for x in ftex) \
                and any(ROCK_TOP_TEX.match(x) for x in ftex):
            why = why or ("a flat rock top in the cave's dark rock texture, level with the floor beside it (the border tile "
                          "Sapphire blocks at a raised floor's edge or a rock band's foot): drawn, and it reads as rock, as every "
                          "rock top of the cave (sweep_outdoor 2026-10-11, screenshots/sweep_outdoor/caves)")
        report.add(fam, name, 'OPEN', s, f'zone tile {t}', f'blocked (class {cl[2]:#x}), floor drawn ({pcs.floor_tex(t)}), '
                   f'{side} side of {nb[0]}; Sapphire {sap}', why)

def cell_txt(c, s):
    t = c.zt(s)
    cl = c.c0.get(t)
    return f' (our cell class {cl[2]:#x} flags {cl[3]:#x})' if cl else ''


# ------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default=os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'))
    ap.add_argument('--rooms', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--rom', default=os.path.join(ROOT, 'work', 'rom', 'hoenn.nds'))
    ap.add_argument('--families', default=','.join(FAMILIES))
    ap.add_argument('--maps', default='')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--all', action='store_true', help='also list the intended differences')
    ap.add_argument('--json')
    a = ap.parse_args()
    fams = set(a.families.split(','))
    only = set(a.maps.split(',')) - {''} or None
    os.environ['HOENN_WORLD_DIR'] = os.path.abspath(a.world)
    os.environ['HOENN_INTERIORS_DIR'] = os.path.abspath(a.rooms)
    people = People(a.rom)
    rep = Report()
    if fams & {'town', 'route', 'outdoor'}:
        outdoor(os.path.abspath(a.world), rep, people, only, fams)
    if fams & {'interior', 'cave', 'dive'}:
        rooms_and_caves(os.path.abspath(a.rooms), rep, people, only, fams)
    rows = rep.rows
    if not a.summary:
        for r in sorted(rows, key=lambda r: (FAMILIES.index(r['family']) if r['family'] in FAMILIES else 9, r['map'],
                                             r['kind'], r['at'] or (0, 0))):
            if r['why'] and not a.all: continue
            print(f"{r['family']} {r['map']} {r['at']} [{r['where']}]: {r['kind']} {r['msg']}"
                  + (f"  [intended: {r['why']}]" if r['why'] else ''))
    kinds = ['INVISIBLE', 'THROUGH', 'OPEN', 'WATER', 'LEDGE', 'LANDING', '!']
    print('summary (open | intended) by family:')
    for fam in FAMILIES:
        o = Counter(r['kind'] for r in rows if r['family'] == fam and not r['why'])
        i = Counter(r['kind'] for r in rows if r['family'] == fam and r['why'])
        if fam not in fams: continue
        print(f'  {fam:9s} ' + '  '.join(f'{k} {o.get(k, 0)}|{i.get(k, 0)}' for k in kinds if o.get(k) or i.get(k) or k in ('INVISIBLE', 'THROUGH', 'OPEN')))
    tot = Counter(r['kind'] for r in rows if not r['why'])
    print('total open:', ', '.join(f'{k} {tot[k]}' for k in kinds if tot[k]) or 'none',
          '| intended:', sum(1 for r in rows if r['why']))
    if a.json:
        json.dump(rows, open(a.json, 'w'), indent=0, default=list)

if __name__ == '__main__':
    main()
