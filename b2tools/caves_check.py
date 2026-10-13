"""Static checker for the built caves and underwater maps (sweep_caves agent, 2026-10-07; notes/CAVES.md "Cave checks"),
the cave counterpart of b2tools/rooms_check.py.

    python3 caves_check.py [--dir ROOMS] [--kinds abcefhistwx] [--summary] [--verbose] [MAP ...]

Reads what b2tools/models_cave.py built (ROOMS/<Map>/room.json, collision*.per, terrain*.dae, *.nsbmd; default
HOENN_INTERIORS_DIR or work/interiors), Sapphire's map (pokeruby, the recipe's "layout" for Shoal Cave's high tide),
data/interiors/<zone>.json, the story objects (data/story/*.json) and the field scripts (MapChangeCore of the ladders
and falls). Every map with a recipe in data/cave_layouts (default: all of them). One line per finding:
"MAP: (kind) detail"; --summary counts them by kind.

Kinds (what the player sees or does in the game):
  a  ladders, ledges, ramps: a ladder tile without its step trigger or its pit/stairs, a ledge whose take-off or landing
     tile is not walkable or not level with it (Black 2's cave ledges keep both sides at one height), a slope tile
     whose low/high edge misses the floor before/after it by more than 2 units
  b  rock models / rock sprites reaching more than 2 units into a walkable tile (you appear to walk through them)
  c  people and objects (the zone json's and the story agents') on solid tiles or off the map
  e  events vs heights: a warp fires when the player's y is within 2 units of its y (CheckWarpPositionMatch: the tile in
     front for a walk-in warp), a step trigger on its own tile, a sign (BG event, CheckBGPositionMatchGrid: -2 .. +2)
     from the tile you read it from; a walk-in warp whose step-out tile is not walkable; MapChangeCore arrivals
     (ladders, cracked floors) on a tile that is not walkable or not at the level the script gives
  f  layered surfaces < 1.95 units apart (melonDS z-fighting): same-facing overlapping faces, not the internal layers
     of one Black 2 template (arch, rock sprites) or model
  h  holes: the background seen through the terrain from the game's camera (orthographic views at 35/45/55 degrees,
     yaw -20/0/+20, back faces culled as the DS does, alpha-tested textures), at least 6 pixels at 2 pixels per unit,
     not next to the Sapphire map's edge (the rock ends there in black, as Black 2's chunks) or a Black 2 arch frame
  i  item balls, Strength boulders, breakable rocks Sapphire's player can reach (stand next to) and Black 2's cannot
  s  chunk files (terrain + collision layers + placements + container) over Black 2's 110,600-byte chunk buffer
  t  textures: an image missing next to the model, a stretched or smeared face (texels per unit more than 3x off the
     texture's usual density in some direction), texture coordinates past the DS's +-2048 texels in a chunk
  w  walkability vs Sapphire: tiles one game's player reaches and the other's doesn't (from every warp, with Surf and
     Waterfall; Gen 3's collision/elevation/ledge/ice rules vs Black 2's: blocked cells, steps < 20 units, side walls,
     ledges, two layers, water, waterfalls, ice), and single moves between tiles both reach allowed in one game only
  x  darkness: Sapphire's requires_flash vs room.json / the zone json's "dark" and its header (the dark cave header)
"""
import os, sys, re, json, glob, math, struct, argparse
from collections import defaultdict, Counter, deque
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches')); sys.path.insert(0, os.path.join(ROOT, 'converter'))
import models_cave as MC                                          # noqa: E402
import version  # noqa: E402  (HOENN_VERSION=ruby: the ruby/ overlays of data/interiors, data/story; notes/RUBY.md)

T = 16
GAP = 1.95
CHUNK_MAX = 110600
STEP = {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}
OPP = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
DIR_OF = {v: k for k, v in STEP.items()}
WARP_VEC = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}       # Black 2 warp dir -> the way the player walks in
# Black 2 collision classes (models_cave.py, models_cave_levels/misc/uw.py, terrain/heights.py)
WATER = {0x3F, 0x94, 0x95, 0x96, 0x97}
WATERFALL, UNDERWATER = 0x40, 0x9C
LEDGE = {0x72: 'e', 0x73: 'w', 0x74: 'n', 0x75: 's'}
WALLS = {0x51: 'e', 0x52: 'w', 0x53: 'n', 0x54: 's', 0x55: 'ne', 0x56: 'nw', 0x57: 'se', 0x58: 'sw'}
ICE = {0x10, 0x18}                                                  # IsTileSlidingIce (ov036 0x021a2c48)
# Sapphire (pokeruby) behaviours
G3_SURF = MC.SURF | {0x70, 0x71, 0x72, 0x73}
G3_JUMP = {0x38: (1, 0), 0x39: (-1, 0), 0x3A: (0, -1), 0x3B: (0, 1)}
G3_BLOCK = {0x30: 'e', 0x31: 'w', 0x32: 'n', 0x33: 's', 0x34: 'ne', 0x35: 'nw', 0x36: 'se', 0x37: 'sw'}
G3_ICE, G3_WATERFALL, G3_MUD = 0x20, 0x13, 0xD0
G3_DOORS = {0x60, 0x6C}                                             # MB_ANIMATED_DOOR, MB_WATER_DOOR: arches in Black 2

def _heights():
    import models_interior as mi
    return mi.heights()

# ------------------------------------------------------------------------------------------------ fast DAE reader
_dae = {}
def read_dae(path):
    """[(texture, P (N,3,3), UV (N,3,2), C (N,3,3))] of a DAE written by b2tools/dae.py (one index per vertex)."""
    if path in _dae: return _dae[path]
    s = open(path).read()
    arr = lambda name: np.fromstring(re.search(rf'<float_array id="{name}-array"[^>]*>([^<]*)<', s).group(1), sep=' ')
    pos, uv, col = arr('positions').reshape(-1, 3), arr('texcoords').reshape(-1, 2), arr('colors').reshape(-1, 3)
    names = dict(re.findall(r'<material id="(material\d+)" name="([^"]+)"', s))
    out = []
    for mat, p in re.findall(r'<triangles material="(material\d+)"[^>]*>.*?<p>([^<]*)</p>', s, re.S):
        idx = np.fromstring(p, sep=' ', dtype=np.int64).reshape(-1, 4)[:, 0].reshape(-1, 3)
        out.append((names[mat], pos[idx], uv[idx], col[idx]))
    _dae[path] = out
    return out

# ------------------------------------------------------------------------------------------------ one built cave
class Cave:
    def __init__(self, rooms_dir, name, cfgs, story):
        self.name, self.dir = name, rooms_dir
        self.d = os.path.join(rooms_dir, name)
        self.meta = json.load(open(os.path.join(self.d, 'room.json')))
        self.recipe = MC.load_json(os.path.join(MC.LAYOUTS, name + '.json'), {}) or {}
        self.alt_of = self.recipe.get('alt_of')
        self.sm = MC.sapphire(self.recipe.get('map', name), self.recipe.get('layout'))
        self.ox, self.oz = self.meta['origin']
        self.W, self.H = self.sm['w'], self.sm['h']
        self.cfg = cfgs.get(self.alt_of or name)
        self.story = [o for o in story if o.get('map') == (self.alt_of or name)]
        self.look = json.load(open(os.path.join(MC.LAYOUTS, '_looks.json')))[self.meta['look']]
        self.out = []
        self.underwater = bool(self.recipe.get('underwater'))
        # collision: {zone tile: (a, b, class, flags)} for layer 0 and layer 1 (bridges)
        self.c0, self.c1 = {}, {}
        mw, mh = self.meta.get('matrix', [1, 1])
        chunks = self.meta.get('chunks') or [dict(collision=self.meta['collision'], collision1=self.meta.get('collision1'))]
        for k, c in enumerate(chunks):
            if c is None: continue
            ci, cj = k % mw, k // mw
            for key, dst in (('collision', self.c0), ('collision1', self.c1)):
                if not c.get(key): continue
                per = open(os.path.join(self.d, c[key]), 'rb').read()
                for i in range(1024):
                    dst[(ci * 32 + i % 32, cj * 32 + i // 32)] = struct.unpack_from('<HHHH', per, 4 + 8 * i)
        self.mw, self.mh = mw, mh
        self._tris = None

    def say(self, kind, msg): self.out.append((kind, f'{self.name}: ({kind}) {msg}'))
    def zt(self, s): return (s[0] + self.ox, s[1] + self.oz)
    def sap(self, t): return (t[0] - self.ox, t[1] - self.oz)
    def inside(self, s): return 0 <= s[0] < self.W and 0 <= s[1] < self.H

    @property
    def tris(self):
        """Terrain triangles in chunk-0-centred units (zone units - 256)."""
        if self._tris is None:
            f = os.path.join(self.d, 'terrain_all.dae')
            self._tris = read_dae(f if os.path.exists(f) else os.path.join(self.d, 'terrain.dae'))
        return self._tris

    # ---- collision ------------------------------------------------------------------------------------------
    def y_of(self, c, t):
        """Height of cell c at the centre of zone tile t (the plane of its slope/offset record)."""
        h = _heights()
        nx, ny, nz = h.NORMALS[c[0] >> 2]; d = h.OFFS[c[1]]
        cx, cz = (t[0] % 32) * 16 + 8 - 256, (t[1] % 32) * 16 + 8 - 256
        return -(nx * cx - nz * cz + d) / ny

    def cell(self, t, y=None):
        """(cell, height) at zone tile t for an actor at height y: the layer whose height is nearest (ties: layer 0),
        as FieldG3DMapper_GetTerrain."""
        c0 = self.c0.get(t)
        if c0 is None: return None, None
        y0 = self.y_of(c0, t)
        c1 = self.c1.get(t)
        if c1 is None or c1 == c0 or y is None: return c0, y0
        y1 = self.y_of(c1, t)
        return (c1, y1) if abs(y1 - y) < abs(y0 - y) else (c0, y0)

    def heights_at(self, t):
        out = []
        for L in (self.c0, self.c1):
            c = L.get(t)
            if c is not None and not c[3] & 1: out.append(self.y_of(c, t))
        return out

    def walkable(self, t):
        return any(not L[t][3] & 1 for L in (self.c0, self.c1) if t in L)

    # ---- Black 2 movement (the player) ------------------------------------------------------------------------
    def b2_steps(self, state, slide=True):
        """[(direction, (tile, height, mode), why)] of the player's moves from state (zone tile, height, mode
        land/surf/dive); why = None when allowed, else the reason it is not (for the move comparison)."""
        t, y, mode = state
        cur, _ = self.cell(t, y)
        out = []
        for d, (dx, dz) in STEP.items():
            n = (t[0] + dx, t[1] + dz)
            c, cy = self.cell(n, y)
            if c is None: out.append((d, None, 'outside the map')); continue
            if cur is not None and d in WALLS.get(cur[2], ''): out.append((d, None, f'side wall {cur[2]:#x} here')); continue
            if OPP[d] in WALLS.get(c[2], ''): out.append((d, None, f'side wall {c[2]:#x} there')); continue
            cls, fl = c[2], c[3]
            if mode == 'land' and LEDGE.get(cls) == d:
                n2 = (n[0] + dx, n[1] + dz)
                c2, y2 = self.cell(n2, y)
                if c2 is None or c2[3] & 1 or c2[2] in WATER or c2[2] == WATERFALL:
                    out.append((d, None, 'ledge with nothing to land on')); continue
                out.append((d, (n2, y2, 'land'), None)); continue
            if mode == 'surf' and cls == WATERFALL and d in 'ns':
                n2 = (n[0] + dx, n[1] + dz)
                c2, y2 = self.cell(n2, y)
                if c2 is not None and c2[2] in WATER and not c2[3] & 1 and ((d == 'n' and y2 > y) or (d == 's' and y2 < y)):
                    out.append((d, (n2, y2, 'surf'), None)); continue
                out.append((d, None, 'waterfall without water beyond')); continue
            if fl & 1: out.append((d, None, f'blocked cell {cls:#x}')); continue
            if abs(cy - y) >= 20: out.append((d, None, f'step of {abs(cy - y):.0f} units')); continue
            water = cls in WATER
            if mode == 'dive':
                if cls != UNDERWATER: out.append((d, None, f'not swimmable ({cls:#x})')); continue
                out.append((d, (n, cy, 'dive'), None)); continue
            if cls == UNDERWATER: out.append((d, None, 'underwater cell')); continue
            if mode == 'land' and water: out.append((d, (n, cy, 'surf'), None)); continue
            nm = 'surf' if water else 'land'
            if cls in ICE and nm == 'land' and slide:               # slide on until the next move is not possible
                cur_t, cur_y = n, cy
                for _ in range(64):
                    nxt = [s for dd, s, why in self.b2_steps((cur_t, cur_y, 'land'), False) if dd == d and s and s[2] == 'land'
                           and s[0] == (cur_t[0] + dx, cur_t[1] + dz)]
                    cc, _ = self.cell(cur_t, cur_y)
                    if not nxt or cc is None or cc[2] not in ICE: break
                    cur_t, cur_y = nxt[0][0], nxt[0][1]
                out.append((d, (cur_t, cur_y, 'land'), None)); continue
            out.append((d, (n, cy, nm), None))
        return out

    def b2_reach(self, starts):
        """{zone tile: set of (height, mode)} reached from starts [(zone tile, height)]."""
        seen = defaultdict(set); q = deque()
        for t, y in starts:
            c, cy = self.cell(t, y)
            if c is None: continue
            mode = 'dive' if c[2] == UNDERWATER else 'surf' if c[2] in WATER else 'land'
            st = (t, round(cy, 1), mode)
            if st[1:] not in seen[t]: seen[t].add(st[1:]); q.append(st)
        while q:
            s = q.popleft()
            for d, n, why in self.b2_steps(s):
                if n is None: continue
                n = (n[0], round(n[1], 1), n[2])
                if n[1:] not in seen[n[0]]: seen[n[0]].add(n[1:]); q.append(n)
        return seen

    # ---- Sapphire movement (pokeruby's rules, as work/agents/caves_misc/tools/sapreach.py) -------------------------
    def g3_steps(self, state):
        sm = self.sm
        (x, z), e = state
        walk = lambda t: self.inside(t) and sm['walk'][t[1]][t[0]]
        elev = lambda t: sm['elev'][t[1]][t[0]]
        beh = lambda t: sm['beh'][t[1]][t[0]]
        can_enter = lambda e_, t: e_ == 0 or elev(t) in (0, 15) or elev(t) == e_
        new_e = lambda e_, cur, t: e_ if (elev(t) == 15 or elev(cur) == 15) else elev(t)
        out = []
        for d, (dx, dz) in STEP.items():
            cur, t = (x, z), (x + dx, z + dz)
            if not self.inside(t): out.append((d, None, 'off the map')); continue
            # (a door tile warps the moment you step on it; arriving you walk out south: the door's upper half, walkable
            # in Lavaridge's tileset, is never reached - Emerald's Magma Hideout; emerald_polish_caves 2026-10-12)
            if beh(cur) == 0x60 and d != 's': out.append((d, None, 'door')); continue
            if not walk(t) and G3_JUMP.get(beh(t)) == (dx, dz):
                t2 = (t[0] + dx, t[1] + dz)
                if walk(t2) and can_enter(e, t2): out.append((d, (t2, new_e(e, cur, t2)), None))
                else: out.append((d, None, 'ledge'))
                continue
            if not walk(t): out.append((d, None, f'collision (behaviour {beh(t):#x})')); continue
            if d in G3_BLOCK.get(beh(cur), '') or OPP[d] in G3_BLOCK.get(beh(t), ''):
                out.append((d, None, 'one-way wall')); continue
            if not can_enter(e, t):
                if e == 3 and beh(t) in G3_SURF: ne = elev(t)                         # start surfing
                elif e == 1 and beh(cur) in G3_SURF | {0} and elev(t) == 3 and beh(t) not in G3_SURF: ne = 3   # land
                else: out.append((d, None, f'elevation {e} -> {elev(t)}')); continue
            else: ne = new_e(e, cur, t)
            while beh(t) == G3_ICE:
                t2 = (t[0] + dx, t[1] + dz)
                if not walk(t2) or not can_enter(ne, t2) or d in G3_BLOCK.get(beh(t), '') or OPP[d] in G3_BLOCK.get(beh(t2), ''): break
                ne = new_e(ne, t, t2); t = t2
            out.append((d, (t, ne), None))
        return out

    def g3_reach(self, starts):
        seen = defaultdict(set); q = deque()
        for t, e in starts:
            if e not in seen[t]: seen[t].add(e); q.append((t, e))
        while q:
            s = q.popleft()
            for d, n, why in self.g3_steps(s):
                if n is None: continue
                if n[1] not in seen[n[0]]: seen[n[0]].add(n[1]); q.append(n)
        return seen

    # ---- starts: Sapphire's warp tiles (+ fall landings), both games ----------------------------------------------
    def starts(self, falls_in):
        sm = self.sm
        tiles = [(w['x'], w['y']) for w in sm['warps'] if self.inside((w['x'], w['y']))] + list(falls_in)
        tiles += [tuple(o['at']) for o in self.story if o.get('kind') == 'arrive']
        g3, b2 = [], []
        for s in tiles:
            if not self.inside(s): continue
            g3.append((s, sm['elev'][s[1]][s[0]]))
            t = self.zt(s)
            hs = self.heights_at(t)
            if hs: b2 += [(t, h) for h in hs]
            else:                                       # a door / arch tile: the tile in front of it
                for dx, dz in STEP.values():
                    n = (t[0] + dx, t[1] + dz)
                    for h in self.heights_at(n): b2.append((n, h))
                    if sm['beh'][s[1]][s[0]] == 0x60 and (dx, dz) != (0, 1): continue   # (a door: out south only)
                    if (s[0] + dx, s[1] + dz) and self.inside((s[0] + dx, s[1] + dz)) and sm['walk'][s[1] + dz][s[0] + dx]:
                        g3.append(((s[0] + dx, s[1] + dz), sm['elev'][s[1] + dz][s[0] + dx]))
        return g3, b2


# ------------------------------------------------------------------------------------------------ checks
def check_walk(c, falls_in):
    """(w) and (i). Returns (Sapphire reach, Black 2 reach in Sapphire tiles)."""
    sm = c.sm
    door_tiles = {(w['x'], w['y']) for w in sm['warps'] if c.inside((w['x'], w['y'])) and sm['beh'][w['y']][w['x']] in G3_DOORS}
    arch_tiles = {c.sap((s['x'], s['z'])) for s in c.meta['warp_spots'] if s['kind'] in ('exit', 'door')}
    mud_top = {(x, z) for z in range(c.H) for x in range(c.W) if sm['beh'][z][x] == G3_MUD
               and not (z > 0 and sm['beh'][z - 1][x] == G3_MUD)}
    falls = {c.sap(t) for t, cc in c.c0.items() if cc[2] == WATERFALL}
    ledges = {c.sap(t) for t, cc in c.c0.items() if cc[2] in LEDGE}
    skip = door_tiles | arch_tiles | mud_top | falls | ledges
    if c.underwater:
        # underwater: no warps lead to most trenches (Dive comes from the surface above every tile): compare tiles
        g3 = {(x, z) for z in range(c.H) for x in range(c.W) if sm['walk'][z][x]}
        b2 = {c.sap(t) for t, cc in c.c0.items() if cc[2] == UNDERWATER and not cc[3] & 1}
        for kind, tiles in (('Sapphire swims there, Black 2 cannot', g3 - b2 - skip), ('Black 2 swims there, Sapphire cannot', b2 - g3 - skip)):
            for comp in components(tiles):
                c.say('w', f'{len(comp)} tile(s) {kind}: {fmt_tiles(comp)}')
        return {t: {0} for t in g3}, {t: {(0, 'dive')} for t in b2}
    g3s, b2s = c.starts(falls_in)
    G = c.g3_reach(g3s)
    Bz = c.b2_reach(b2s)
    B = {c.sap(t): v for t, v in Bz.items()}
    for kind, tiles in (('Sapphire reaches, Black 2 does not', set(G) - set(B) - skip),
                        ('Black 2 reaches, Sapphire does not', set(B) - set(G) - skip)):
        for comp in components(tiles):
            c.say('w', f'{len(comp)} tile(s) {kind}: {fmt_tiles(comp)}{why_b2(c, comp, B)}')
    # single moves between tiles both reach
    both = (set(G) & set(B)) - skip
    seen = set()
    for s in sorted(both):
        ga = {d for e in G[s] for d, n, why in c.g3_steps((s, e)) if n is not None}
        gwhy = {d: why for e in G[s] for d, n, why in c.g3_steps((s, e)) if n is None}
        t = c.zt(s)
        ba, bwhy = set(), {}
        for (y, mode) in Bz[t]:
            for d, n, why in c.b2_steps((t, y, mode)):
                if n is not None: ba.add(d)
                else: bwhy.setdefault(d, why)
        for d in 'nsew':
            dx, dz = STEP[d]
            nb = (s[0] + dx, s[1] + dz)
            if nb in skip or (nb not in both and (d in ga) == (d in ba)): continue
            # jumps / waterfalls land two tiles away: the tile beyond must be one both reach
            if (d in ga) != (d in ba):
                key = tuple(sorted([s, nb])) + (d in ga,)
                if key in seen: continue
                seen.add(key)
                if d in ga: c.say('w', f'move {s} -> {nb}: Sapphire walks it, Black 2 does not ({bwhy.get(d, "?")})')
                else: c.say('w', f'move {s} -> {nb}: Black 2 walks it, Sapphire does not ({gwhy.get(d, "?")})')
    return G, B

def why_b2(c, comp, B):
    """A hint for a region one game reaches: what the Black 2 cells there are."""
    t = c.zt(sorted(comp)[0])
    cc = c.c0.get(t)
    if cc is None: return ''
    return f' (Black 2 cell at {sorted(comp)[0]}: class {cc[2]:#x} flags {cc[3]:#x} y {c.y_of(cc, t):.0f})'

def components(tiles):
    tiles = set(tiles); out = []
    while tiles:
        t0 = tiles.pop(); comp = {t0}; st = [t0]
        while st:
            t = st.pop()
            for dx, dz in STEP.values():
                n = (t[0] + dx, t[1] + dz)
                if n in tiles: tiles.discard(n); comp.add(n); st.append(n)
        out.append(comp)
    return sorted(out, key=lambda c: min(c))

def fmt_tiles(comp, k=6):
    s = sorted(comp, key=lambda t: (t[1], t[0]))
    return ' '.join(f'({x},{z})' for x, z in s[:k]) + (' ...' if len(s) > k else '')

def check_objects(c, G, B):
    """(c) objects on solid tiles, (i) objects Sapphire reaches and Black 2 doesn't."""
    objs = []
    for n in (c.cfg or {}).get('npcs', []):
        if 'at' in n: objs.append((tuple(n['at']), n.get('what') or f'uid {n.get("uid")} model {n.get("model")}', n))
    for o in c.story:
        if o.get('kind') == 'npc' and 'at' in o: objs.append((tuple(o['at']), f'story {o.get("what", "")[:50]}', o))
    for s, what, n in objs:
        t = c.zt(s)
        if not c.inside(s): c.say('c', f'{what} at {s} is off the map'); continue
        if not c.walkable(t) and c.sm['walk'][s[1]][s[0]]:          # (Sapphire's own objects on its blocked tiles,
            cc = c.c0.get(t)                                            # e.g. Kyogre in its pool, stay as they are)
            c.say('c', f'{what} at {s} stands on a solid tile (class {cc[2]:#x})' if cc else f'{what} at {s} is outside the collision')
        if any(k in what for k in ('item ball', 'boulder', 'rock')) and not c.underwater:
            nb = [(s[0] + dx, s[1] + dz) for dx, dz in STEP.values()]
            g = any(x in G for x in nb + [s]); b = any(x in B for x in nb)
            if g and not b: c.say('i', f'{what} at {s}: Sapphire\'s player reaches it, Black 2\'s cannot stand next to it')

def check_events(c, rooms, built):
    """(e) warps, triggers, signs vs the heights the player has there; MapChangeCore arrivals."""
    cfg = c.cfg or {}
    spots = {tuple(t): s for s in c.meta['warp_spots'] for t in s['tiles']}
    for i, w in enumerate(cfg.get('warps', [])):
        if 'at' not in w: continue
        s = tuple(w['at']); sp = spots.get(s)
        if sp is None: c.say('e', f'warp {i} at {s}: no warp spot there'); continue
        if not c.inside(s): continue
        typ, d = w.get('type', sp['type']), w.get('dir', sp['dir'])
        wy = w.get('y', sp.get('y', 0))
        t = (sp['x'], sp['z'])
        if typ == 4 and d in WARP_VEC:
            v = WARP_VEC[d]; ap = (t[0] - v[0], t[1] - v[1])
            hs = c.heights_at(ap)
            if not hs: c.say('e', f'warp {i} ({sp["kind"]} at {s}): the tile in front of it, {c.sap(ap)}, is not walkable'); continue
            if not any(abs(h - wy) <= 2 for h in hs):
                c.say('e', f'warp {i} ({sp["kind"]} at {s}): y {wy} but the tile in front of it is at {", ".join(f"{h:.1f}" for h in hs)}: it never fires')
        elif sp.get('step') or sp['kind'].startswith('ladder'):
            hs = c.heights_at(t)
            if not hs: c.say('e', f'warp {i} ({sp["kind"]} at {s}): its tile is not walkable (arrival)')
    # step triggers (the zone json's and the story agents'): fire within 2 units of their y on their own tile
    tide = (MC.load_json(os.path.join(MC.LAYOUTS, (c.alt_of or c.name) + '.json'), {}) or {}).get('tide') or {}
    tide_var = 0x4031 + tide['event'] if tide.get('event') is not None else None
    # (a trigger conditioned on the tide's work only fires in the layout it was made for: the low tide's)
    trig = [(t_, f'trigger script {t_["script"]}') for t_ in cfg.get('triggers', []) if not (c.alt_of and t_.get('var') == tide_var)]
    trig += [(o, f'story trigger {o.get("what", "")[:40]}') for o in c.story if o.get('kind') == 'trigger']
    def story_y(o):
        """A story object's y as b2tools/patches/story.py gives it in a cave (cave_y: the floor it is on / read from)."""
        if 'y' in o or o.get('kind') not in ('trigger', 'sign'): return o.get('y', 0)
        import story as SP
        return SP.cave_y(c.dir, c.alt_of or c.name, o['at'][0] + c.ox, o['at'][1] + c.oz, o) or 0
    for t_, what in trig:
        if 'at' not in t_: continue
        y = story_y(t_) if t_ in c.story else t_.get('y', 0); y = y - 0x10000 if y >= 0x8000 else y
        for a in range(t_.get('w', 1)):
            for b in range(t_.get('h', 1)):
                s = (t_['at'][0] + a, t_['at'][1] + b); t = c.zt(s)
                hs = c.heights_at(t)
                if not hs: c.say('e', f'{what} at {s}: on a tile you cannot stand on'); continue
                if not any(abs(h - y) <= 2 for h in hs):
                    c.say('e', f'{what} at {s}: y {y}, the tile is at {", ".join(f"{h:.1f}" for h in hs)}: it never fires')
    # signs: read from the tile in front (dir 0 = facing north: from the south; else any side)
    signs = [(s_, f'sign script {s_["script"]}') for s_ in cfg.get('signs', [])]
    signs += [(o, f'story sign {o.get("what", "")[:40]}') for o in c.story if o.get('kind') == 'sign']
    for s_, what in signs:
        if 'at' not in s_: continue
        y = story_y(s_) if s_ in c.story else s_.get('y', 0); y = y - 0x10000 if y >= 0x8000 else y
        s = tuple(s_['at']); t = c.zt(s)
        if not c.inside(s): continue                               # Sapphire's leftover off-map signs (Meteor Falls)
        sides = [(0, 1)] if s_.get('dir', 4) == 0 else list(STEP.values()) + [(0, 0)]
        hs = [h for dx, dz in sides for h in c.heights_at((t[0] + dx, t[1] + dz))]
        if not hs: c.say('e', f'{what} at {s}: no walkable tile to read it from'); continue
        if not any(-2 <= y - h < 2 for h in hs):
            c.say('e', f'{what} at {s}: y {y}, read from heights {", ".join(sorted({f"{h:.1f}" for h in hs}))}: never readable')
    # MapChangeCore arrivals of this cave's step scripts (ladders, falls) in the destination maps
    r = rooms.get(c.alt_of or c.name)
    if not r or c.alt_of: return
    sp = os.path.join(ROOT, 'src', 'field_scripts', f'{r["scripts"]:04d}_room_{c.alt_of or c.name}.s')
    if not os.path.exists(sp): return
    zone_room = {v['zone']: k for k, v in rooms.items()}
    for m in re.finditer(r'MapChangeCore\s+(\d+),\s*(\d+),\s*(-?\d+),\s*(\d+)', open(sp).read()):
        z, x, ly, zz = map(int, m.groups())
        dn = zone_room.get(z)
        dc = built(dn) if dn else None
        if dc is None: continue
        t = (x, zz); hs = dc.heights_at(t)
        if not hs: c.say('e', f'MapChangeCore {z}, {x}, {ly}, {zz} ({dn} {dc.sap(t)}): arrives on a tile you cannot stand on'); continue
        # the player lands on the layer nearest the level given (CheckRecalcActorY snaps it to that layer's height:
        # tested, Shoal Cave's stairs-room ladder lands at 0 on the inner room's tile at 8); a problem only when that
        # layer is not one you can stand on (a bridge's other layer)
        cells = [(L[t], dc.y_of(L[t], t)) for L in (dc.c0, dc.c1) if t in L]
        cell, y = min(cells, key=lambda cy: abs(cy[1] - 16 * ly))
        if cell[3] & 1:
            c.say('e', f'MapChangeCore {z}, {x}, {ly}, {zz} ({dn} {dc.sap(t)}): level {ly} = y {16 * ly} lands on the layer at {y:.1f}, which is blocked')

def check_features(c):
    """(a) ladders, ledges, ramps."""
    cfg = c.cfg or {}
    trig = {tuple(t_['at']) for t_ in cfg.get('triggers', []) if 'at' in t_}
    trig |= {tuple(o['at']) for o in c.story if o.get('kind') == 'trigger' and 'at' in o}   # (a story agent's ladder)
    for k, way in c.meta.get('ladders', {}).items():
        s = tuple(map(int, k.split(','))); t = c.zt(s)
        if s not in trig: c.say('a', f'ladder {way} at {s}: no step trigger on it')
        if not c.heights_at(t): c.say('a', f'ladder {way} at {s}: its tile is not walkable')
        X0, Z0 = t[0] * T - 256, t[1] * T - 256
        y = (c.heights_at(t) or [0])[0]
        stairs = [P for tex, P, UV, C in c.tris if tex == c.look.get('stairs') for P in P
                  if P[:, 0].min() >= X0 - 1 and P[:, 0].max() <= X0 + 17 and P[:, 2].min() >= Z0 - 21 and P[:, 2].max() <= Z0 + 17]
        if not stairs: c.say('a', f'ladder {way} at {s}: no stairs drawn on it')
    for t, cc in sorted(c.c0.items()):
        if cc[2] not in LEDGE: continue
        d = LEDGE[cc[2]]; dx, dz = STEP[d]
        y = c.y_of(cc, t)
        back, land = (t[0] - dx, t[1] - dz), (t[0] + dx, t[1] + dz)
        for what, u in (('take-off', back), ('landing', land)):
            hs = c.heights_at(u)
            uc = c.c0.get(u)
            if not hs: c.say('a', f'ledge {c.sap(t)} (jump {d}): its {what} tile {c.sap(u)} is not walkable')
            elif what == 'take-off' and uc is not None and uc[0] >> 2: pass   # (a slope tile: the jump works from it,
                                                                          # tested on Victory Road B2F (40,19) -> (40,21))
            elif not any(abs(h - y) <= 2 for h in hs):
                c.say('a', f'ledge {c.sap(t)} (jump {d}): its {what} tile {c.sap(u)} is at {hs[0]:.0f}, the ledge at {y:.0f}')
    # slope tiles: their plane's low/high edge meets the floor before/after (the neighbours along the climb)
    h = _heights()
    for t, cc in sorted(c.c0.items()):
        if cc[0] >> 2 == 0 or cc[3] & 1: continue
        nx, ny, nz = h.NORMALS[cc[0] >> 2]; dd = h.OFFS[cc[1]]
        py = lambda X, Z: -(nx * ((X % 512) - 256) - nz * ((Z % 512) - 256) + dd) / ny
        cx, cz = t[0] * T + 8, t[1] * T + 8
        climb = 'ew' if abs(nx) > abs(nz) else 'ns'
        for d, (dx, dz) in STEP.items():
            if d not in climb: continue
            n = (t[0] + dx, t[1] + dz)
            edge = py(cx + dx * 7.99, cz + dz * 7.99)
            hs = c.heights_at(n)
            if not hs: continue
            nc = c.c0.get(n)
            if nc is not None and nc[2] == 0x17: continue      # (a shoal: wading water drawn 4 below its floor)
            if nc is not None and nc[0] >> 2:                  # slope next to slope: compare the planes at the edge
                nnx, nny, nnz = h.NORMALS[nc[0] >> 2]; nd = h.OFFS[nc[1]]
                other = -(nnx * (((cx + dx * 8.01) % 512) - 256) - nnz * (((cz + dz * 8.01) % 512) - 256) + nd) / nny
            else: other = min(hs, key=lambda v: abs(v - edge))
            if abs(other - edge) > 2 and abs(other - edge) < 20:
                c.say('a', f'slope tile {c.sap(t)}: its {d} edge is at {edge:.1f}, the tile beyond {c.sap(n)} at {other:.1f} (a step)')

def check_models(c):
    """(b) rock models and rock sprites over walkable tiles."""
    import preview_interior as pv
    pv.OUT = os.environ.get('CAVES_CHECK_MODELS') or c.dir
    res = {m['name']: (m['res'], m['pack']) for m in c.meta['models']}
    pieces = []
    for f in c.meta['furniture']:
        rid, pack = res[f['m']]
        parts = pv.placed(pv.furniture_parts(rid, pack), f['pos'], f.get('rot', 0))
        base = f['pos'][1]
        pts = [P for tp, P, UV, C in parts for P in P if P[:, 1].max() > base + 3 and P[:, 1].min() < base + 20]
        pieces.append((f['m'], f['pos'], pts))
    spr = set()
    for key in (c.look.get('rock_sprites') or {}).values(): spr |= set(key['materials'])
    if spr:
        pts = [P for tex, P, UV, C in c.tris if tex in spr for P in P if P[:, 1].max() - P[:, 1].min() > 1 or True]
        pieces.append(('rock sprite', None, pts))
    for name, pos, pts in pieces:
        hit = defaultdict(float)
        for P in pts:
            xs, zs = P[:, 0] + 256, P[:, 2] + 256
            for tx in range(int(xs.min() // T), int(xs.max() // T) + 1):
                for tz in range(int(zs.min() // T), int(zs.max() // T) + 1):
                    if not c.walkable((tx, tz)): continue
                    # how far the triangle's footprint reaches into the tile (clip its bbox)
                    ix = min(xs.max(), tx * T + 16) - max(xs.min(), tx * T); iz = min(zs.max(), tz * T + 16) - max(zs.min(), tz * T)
                    if ix > 2 and iz > 2 and tri_area_in(P, tx, tz) > 4: hit[(tx, tz)] = max(hit[(tx, tz)], min(ix, iz))
        for t, depth in sorted(hit.items()):
            c.say('b', f'{name}{" at " + str([round(v) for v in pos]) if pos else ""} reaches {depth:.0f} units into walkable tile {c.sap(t)}')

def tri_area_in(P, tx, tz):
    """Area (top view) of triangle P inside zone tile (tx, tz)."""
    import rooms_check as rc
    q = [(float(p[0] + 256), float(p[2] + 256)) for p in P]
    box = [(tx * T, tz * T), (tx * T + T, tz * T), (tx * T + T, tz * T + T)], [(tx * T, tz * T), (tx * T + T, tz * T + T), (tx * T, tz * T + T)]
    return sum(rc._overlap(q, list(b)) for b in box)

def check_layers(c, verbose=False):
    """(f) same-facing overlapping faces < GAP apart."""
    import rooms_check as rc
    tmpl = set()
    for key in ('arch', 'arch_s', 'arch_n', 'arch_e', 'arch_w'):
        a = c.look.get(key)
        if a: tmpl |= set(a['materials']) | set(a.get('outside', {}).values()) | set(a.get('inside', {}).values())
    for key in (c.look.get('rock_sprites') or {}).values(): tmpl |= set(key['materials'])
    F = []
    for tex, P, UV, C in c.tris:
        owner = 'A' if tex in tmpl else 'T'
        for t in P: F.append((owner, tex, t))
    buckets = defaultdict(list)
    for owner, tex, t in F:
        n = np.cross(t[1] - t[0], t[2] - t[0]); l = np.linalg.norm(n)
        if l < 0.1: continue
        n = n / l
        if not (n[1] > 0.3 or n[2] > 0.3 or abs(n[0]) > 0.7): continue
        key = tuple(np.round(n, 2))
        buckets[key].append((owner, tex, t))
    hits = {}
    for key, items in buckets.items():
        nk = np.array(key) / np.linalg.norm(key)
        u = np.cross(nk, [0, 1, 0] if abs(nk[1]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u); v = np.cross(nk, u)
        D = [float(nk @ it[2].mean(0)) for it in items]
        P2 = [[(float(p @ u), float(p @ v)) for p in it[2]] for it in items]
        box = [(min(p[0] for p in q), max(p[0] for p in q), min(p[1] for p in q), max(p[1] for p in q)) for q in P2]
        grid = defaultdict(list)
        for i, b in enumerate(box):
            for gx in range(int(b[0] // 16), int(b[1] // 16) + 1):
                for gy in range(int(b[2] // 16), int(b[3] // 16) + 1): grid[(gx, gy)].append(i)
        done = set()
        for cell, ids in grid.items():
            ids = sorted(ids, key=lambda i: D[i])
            for a_ in range(len(ids)):
                i = ids[a_]
                for b_ in range(a_ + 1, len(ids)):
                    j = ids[b_]
                    dd = D[j] - D[i]
                    if dd >= GAP - 1e-3: break
                    if (i, j) in done: continue
                    done.add((i, j))
                    oi, ti, _ = items[i]; oj, tj, _ = items[j]
                    if oi == 'A' and oj == 'A': continue                   # one Black 2 template's own layers
                    if ti == tj and abs(dd) < 1e-3: continue               # one surface split in triangles
                    if 'kage' in ti and 'kage' in tj: continue
                    bi, bj = box[i], box[j]
                    if bi[1] <= bj[0] or bj[1] <= bi[0] or bi[3] <= bj[2] or bj[3] <= bi[2]: continue
                    if min(min(bi[1], bj[1]) - max(bi[0], bj[0]), min(bi[3], bj[3]) - max(bi[2], bj[2])) < 0.75: continue
                    a = rc._overlap(P2[i], P2[j])
                    if a < 0.5: continue
                    k = tuple(sorted([ti, tj])) + (round(abs(dd), 2), key)
                    if k not in hits: hits[k] = [0.0, items[i][2].mean(0)]
                    hits[k][0] += a
    for (ta, tb, dd, key), (a, where) in sorted(hits.items(), key=lambda kv: -kv[1][0]):
        if a < 2.0: continue
        facing = 'up' if key[1] > 0.9 else ('south' if key[2] > 0.9 else 'side')
        t = (int((where[0] + 256) // T), int((where[2] + 256) // T))
        c.say('f', f'{ta} and {tb} are {dd} units apart (facing {facing}), {a:.0f} sq units overlap, e.g. at {c.sap(t)}')

_alpha = {}
def opaque_mask(path):
    """Texel mask (rows from the top) of an image's opaque texels (alpha > 100, as preview_interior's alpha test), or
    None when every texel is opaque."""
    if path not in _alpha:
        from PIL import Image
        a = np.asarray(Image.open(path).convert('RGBA'))[..., 3] > 100 if os.path.exists(path) else None
        _alpha[path] = None if a is None or a.all() else a
    return _alpha[path]

def check_holes(c, verbose=False, scale=2.0, views=((35, -20), (35, 0), (35, 20), (45, -20), (45, 0), (45, 20), (55, -20), (55, 0), (55, 20)),
                dump=None):
    """(h) background visible through the terrain from the game camera: every front face (the DS culls back faces)
    drawn orthographically along the camera's direction with its texture's alpha test (transparent texels let the
    background through, e.g. the ragged foot of a wall face); background pixels the faces enclose (not connected to the
    picture's border) are holes. A hole next to faces lying outside the Sapphire map (beyond its edge: Black 2's own
    caves end in black there) is not counted."""
    from PIL import Image, ImageDraw
    items = [(tex, P, UV, opaque_mask(os.path.join(c.d, tex + '.png'))) for tex, P, UV, C in c.tris]
    tmpl = templates(c)
    arch_tiles = {(s['x'] + a, s['z'] + b) for s in c.meta['warp_spots'] if s['kind'] in ('exit', 'door')
                  for a in (-1, 0, 1) for b in (-1, 0, 1)}
    allP = np.concatenate([P for _, P, _, _ in items])
    owner = np.concatenate([np.full(len(P), i) for i, (_, P, _, _) in enumerate(items)])
    allUV = np.concatenate([UV for _, _, UV, _ in items])
    mapx0, mapz0 = c.ox * T - 256, c.oz * T - 256
    mapx1, mapz1 = mapx0 + c.W * T, mapz0 + c.H * T
    found = {}
    for elev, yaw in views:
        e, a = math.radians(elev), math.radians(yaw)
        ca, sa = math.cos(a), math.sin(a)
        X = allP[..., 0] * ca - allP[..., 2] * sa
        Z = allP[..., 0] * sa + allP[..., 2] * ca
        Y = allP[..., 1]
        S = Y * math.cos(e) - Z * math.sin(e)
        DEP = -Y * math.sin(e) - Z * math.cos(e)
        e1 = np.stack([X[:, 1] - X[:, 0], Y[:, 1] - Y[:, 0], Z[:, 1] - Z[:, 0]], -1)
        e2 = np.stack([X[:, 2] - X[:, 0], Y[:, 2] - Y[:, 0], Z[:, 2] - Z[:, 0]], -1)
        n = np.cross(e1, e2)
        front = n[:, 1] * math.sin(e) + n[:, 2] * math.cos(e) > 1e-6
        x0, x1, s0, s1 = X.min(), X.max(), S.min(), S.max()
        Wd, Hd = int((x1 - x0) * scale) + 5, int((s1 - s0) * scale) + 5
        img = Image.new('L', (Wd, Hd), 0); dr = ImageDraw.Draw(img)
        px = (X - x0) * scale + 2; py = (s1 - S) * scale + 2
        alpha_tris = []
        for k in np.nonzero(front)[0]:
            if items[owner[k]][3] is not None: alpha_tris.append(k); continue
            dr.polygon([(px[k, 0], py[k, 0]), (px[k, 1], py[k, 1]), (px[k, 2], py[k, 2])], fill=255, outline=255)
        cov = np.asarray(img).copy()                           # (outline: PIL's fill leaves pixels between neighbours)
        for k in alpha_tris:                          # alpha-tested faces, pixel by pixel
            mask = items[owner[k]][3]; th, tw = mask.shape
            xa, xb = int(max(0, math.floor(px[k].min()))), int(min(Wd - 1, math.ceil(px[k].max())))
            ya, yb = int(max(0, math.floor(py[k].min()))), int(min(Hd - 1, math.ceil(py[k].max())))
            gx, gy = np.meshgrid(np.arange(xa, xb + 1) + 0.5, np.arange(ya, yb + 1) + 0.5)
            (ax_, bx_, cx_), (ay_, by_, cy_) = px[k], py[k]
            den = (by_ - cy_) * (ax_ - cx_) + (cx_ - bx_) * (ay_ - cy_)
            if abs(den) < 1e-9: continue
            w0 = ((by_ - cy_) * (gx - cx_) + (cx_ - bx_) * (gy - cy_)) / den
            w1 = ((cy_ - ay_) * (gx - cx_) + (ax_ - cx_) * (gy - cy_)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
            uv = allUV[k]
            u = w0 * uv[0, 0] + w1 * uv[1, 0] + w2 * uv[2, 0]; v = w0 * uv[0, 1] + w1 * uv[1, 1] + w2 * uv[2, 1]
            tx = np.floor(u * tw).astype(int) % tw; ty = np.floor((1 - v) * th).astype(int) % th
            m &= mask[ty, tx]
            sub = cov[ya:yb + 1, xa:xb + 1]; sub[m] = 255
        img = Image.fromarray(np.pad(cov, 1)).copy()           # (a writable image: fromarray's is read-only)
        ImageDraw.floodfill(img, (0, 0), 128)
        hole = np.asarray(img)[1:-1, 1:-1] == 0
        if dump: Image.fromarray(np.where(hole, 255, np.asarray(img)[1:-1, 1:-1] // 2).astype(np.uint8)).save(f'{dump}_{elev}_{yaw}.png')
        if not hole.any(): continue
        ys, xs = np.nonzero(hole)
        cen_x, cen_s = px.mean(1), py.mean(1)
        for comp in pixel_components(set(zip(ys.tolist(), xs.tolist()))):
            if len(comp) < 6: continue                                # (smaller: sub-texel slivers of the sampling)
            cy = sum(p[0] for p in comp) / len(comp); cx = sum(p[1] for p in comp) / len(comp)
            # the front-most face whose picture touches the hole: where in the world it is
            r = 3
            near = np.nonzero(front & (px.min(1) <= cx + r) & (px.max(1) >= cx - r) & (py.min(1) <= cy + r) & (py.max(1) >= cy - r))[0]
            if not len(near): continue
            k = near[np.argmin(DEP[near].mean(1))]
            if items[owner[k]][0] in tmpl: continue                   # Black 2's own arch frame over the void (chunk 788)
            wx, wy, wz = allP[k].mean(0)
            # where the view ray through the hole is at that face's height: within a tile of the Sapphire map's edge
            # or past it, it is the void beyond the map (the rock ends there in black, as past the edge of Black 2's
            # own cave chunks), not a hole
            Xh = (cx - 2) / scale + x0; Sh = s1 - (cy - 2) / scale
            Zr = (wy * math.cos(e) - Sh) / math.sin(e)
            hx, hz = Xh * ca + Zr * sa, -Xh * sa + Zr * ca
            outside = not (mapx0 + 16 <= hx <= mapx1 - 16 and mapz0 + 16 <= hz <= mapz1 - 16) or \
                      not (mapx0 + 16 <= wx <= mapx1 - 16 and mapz0 + 16 <= wz <= mapz1 - 16)
            if outside: continue
            if (int((hx + 256) // T), int((hz + 256) // T)) in arch_tiles: continue   # through an arch's tunnel: black, by
                                                                                        # design (Black 2's own template)
            t = (int((wx + 256) // T), int((wz + 256) // T))
            key = (t, items[owner[k]][0])
            if key not in found or found[key][0] < len(comp): found[key] = (len(comp), elev, yaw, round(float(wy)))
    for (t, tex), (n, elev, yaw, y) in sorted(found.items()):
        c.say('h', f'hole of {n} px (view {elev} deg, yaw {yaw}) at {tex} near {c.sap(t)} y {y}: the background shows through')

def pixel_components(px):
    out = []
    while px:
        p0 = px.pop(); comp = [p0]; st = [p0]
        while st:
            y, x = st.pop()
            for q in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if q in px: px.discard(q); comp.append(q); st.append(q)
        out.append(comp)
    return out

def templates(c):
    """Materials copied from Black 2 chunks (arches, rock sprites): their own layers and transparency are Black 2's."""
    out = set()
    for key in ('arch', 'arch_s', 'arch_n', 'arch_e', 'arch_w'):
        a = c.look.get(key)
        if a: out |= set(a['materials']) | set(a.get('outside', {}).values()) | set(a.get('inside', {}).values())
    for key in (c.look.get('rock_sprites') or {}).values(): out |= set(key['materials'])
    return out

def check_textures(c):
    """(t) missing images, stretched faces, texture coordinates out of the DS's range."""
    from PIL import Image
    tmpl = set()
    for key in ('arch', 'arch_s', 'arch_n', 'arch_e', 'arch_w'):
        a = c.look.get(key)
        if a: tmpl |= set(a['materials']) | set(a.get('outside', {}).values()) | set(a.get('inside', {}).values())
    for key in (c.look.get('rock_sprites') or {}).values(): tmpl |= set(key['materials'])
    sizes = {}
    for tex in {t for t, *_ in c.tris}:
        p = os.path.join(c.d, tex + '.png')
        if not os.path.exists(p): c.say('t', f'texture {tex}: no image next to the model'); continue
        sizes[tex] = Image.open(p).size
    pal = open(os.path.join(c.d, 'palettes.txt')).read().split()
    for tex in sizes:
        if tex not in pal: c.say('t', f'texture {tex}: not in palettes.txt')
    # density per face: singular values of the texel-space Jacobian
    stats = defaultdict(list)
    for tex, P, UV, C in c.tris:
        if tex not in sizes or tex in tmpl or tex == c.look.get('bridge'): continue   # (the deck's 8-unit sides: Black 2's
        w, h = sizes[tex]                                                                   #  own mapping, chunk 631)
        e1 = P[:, 1] - P[:, 0]; e2 = P[:, 2] - P[:, 0]
        n = np.cross(e1, e2); area = np.linalg.norm(n, axis=1)
        ok = (area > 1.0) & (C.reshape(len(C), -1).min(1) > 0.05)   # (faces fading to black: no texture shows)
        a_ = e1 / np.maximum(np.linalg.norm(e1, axis=1, keepdims=True), 1e-9)
        b_ = np.cross(n / np.maximum(area[:, None], 1e-9), a_)
        x1 = np.einsum('ij,ij->i', e1, a_); y1 = np.einsum('ij,ij->i', e1, b_)
        x2 = np.einsum('ij,ij->i', e2, a_); y2 = np.einsum('ij,ij->i', e2, b_)
        du1 = (UV[:, 1, 0] - UV[:, 0, 0]) * w; dv1 = (UV[:, 1, 1] - UV[:, 0, 1]) * h
        du2 = (UV[:, 2, 0] - UV[:, 0, 0]) * w; dv2 = (UV[:, 2, 1] - UV[:, 0, 1]) * h
        det = x1 * y2 - x2 * y1
        for k in np.nonzero(ok & (np.abs(det) > 1e-6))[0]:
            M = np.array([[x1[k], x2[k]], [y1[k], y2[k]]])
            J = np.array([[du1[k], du2[k]], [dv1[k], dv2[k]]]) @ np.linalg.inv(M)
            sv = np.linalg.svd(J, compute_uv=False)
            stats[tex].append((sv[0], sv[1], k, P[k]))
    for tex, rows in stats.items():
        med = float(np.median([r[0] for r in rows] + [r[1] for r in rows]))
        bad = [r for r in rows if r[1] < med / 3 or r[0] > med * 3]
        if bad:
            worst = max(bad, key=lambda r: max(r[0] / med, med / max(r[1], 1e-6)))
            P = worst[3]; t = (int((P[:, 0].mean() + 256) // T), int((P[:, 2].mean() + 256) // T))
            c.say('t', f'texture {tex}: {len(bad)} of {len(rows)} faces stretched (texels per unit {worst[1]:.2f}..{worst[0]:.2f}, '
                       f'usual {med:.2f}), e.g. at {c.sap(t)} y {P[:, 1].mean():.0f}')
    # texture coordinates per chunk model (the DS stores them as s16 1/16 texels)
    for f in sorted(glob.glob(os.path.join(c.d, 'terrain*.dae'))):
        if f.endswith('terrain_all.dae'): continue
        for tex, P, UV, C in read_dae(f):
            if tex not in sizes: continue
            w, h = sizes[tex]
            # the DS keeps texture coordinates as s16 1/16 texels: a face whose vertices wrap differently is smeared
            # (all vertices past +-2048 texels wrap by a whole number of repeats: no change on screen)
            bad = 0
            for axis, size in ((0, w), (1, h)):
                raw = np.round(UV[..., axis] * size * 16).astype(np.int64)
                wrapped = ((raw + 32768) % 65536) - 32768
                sh = wrapped - raw
                bad += int((sh.max(1) != sh.min(1)).sum())
            if bad:
                mu, mv = float(np.abs(UV[..., 0]).max() * w), float(np.abs(UV[..., 1]).max() * h)
                c.say('t', f'{os.path.basename(f)}: texture {tex}: {bad} faces straddle the DS\'s texture coordinate limit '
                           f'(+-2048 texels, coordinates reach {max(mu, mv):.0f}): smeared')

def check_sizes(c):
    """(s) chunk files over the chunk buffer."""
    chunks = c.meta.get('chunks') or [dict(terrain=c.meta['terrain'], collision=c.meta['collision'],
                                           collision1=c.meta.get('collision1'), placements=c.meta['placements'])]
    for k, ch in enumerate(chunks):
        if not ch: continue
        files = [os.path.join(c.d, ch[x]) for x in ('terrain', 'collision', 'collision1', 'placements') if ch.get(x)]
        if k == 0 and not ch.get('collision1') and c.meta.get('collision1'): files.append(os.path.join(c.d, c.meta['collision1']))
        missing = [f for f in files if not os.path.exists(f)]
        if missing: c.say('s', f'chunk {k}: {", ".join(os.path.basename(f) for f in missing)} not built'); continue
        size = sum(os.path.getsize(f) for f in files) + 8 + 8 * len(files)
        if size > CHUNK_MAX: c.say('s', f'chunk {k}: {size} bytes, over the {CHUNK_MAX}-byte chunk buffer (the game hangs)')

def check_dark(c):
    want = bool(c.sm['json'].get('requires_flash'))
    if bool(c.meta.get('dark')) != want: c.say('x', f'room.json dark {c.meta.get("dark")}, Sapphire requires_flash {want}')
    if c.cfg is not None and bool(c.cfg.get('dark')) != want: c.say('x', f'zone json dark {c.cfg.get("dark")}, Sapphire requires_flash {want}')

# ------------------------------------------------------------------------------------------------ main
def load_story():
    out = []
    for p in version.overlay(os.path.join(ROOT, 'data', 'story'), '*.json'):
        try: out += json.load(open(p)).get('objects', [])
        except Exception: pass
    return out

def falls_into(rooms_dir, names):
    """{map: Sapphire tiles you land on from a cracked floor above (same x, y)}."""
    import gen_caves as GC
    out = defaultdict(set)
    fold = GC.folders()
    for n in names:
        p = os.path.join(rooms_dir, n, 'room.json')
        if not os.path.exists(p): continue
        m = json.load(open(p))
        if not m.get('cracked'): continue
        hw = GC.hole_warp(m['map']); dest = fold.get(hw)
        if dest: out[dest] |= {tuple(t) for t in m['cracked']}
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--kinds', default='abcefhistwx'); ap.add_argument('--summary', action='store_true')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('maps', nargs='*')
    a = ap.parse_args()
    d = os.path.abspath(a.dir)
    os.environ['HOENN_INTERIORS_DIR'] = d
    names = a.maps or sorted(f[:-5] for f in os.listdir(MC.LAYOUTS) if f.endswith('.json') and not f.startswith('_')
                             and os.path.exists(os.path.join(d, f[:-5], 'room.json')))
    cfgs = {}
    for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json'):
        j = json.load(open(f))
        if j.get('room'): cfgs[j['room']] = j
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    story = load_story()
    all_caves = sorted(f[:-5] for f in os.listdir(MC.LAYOUTS) if f.endswith('.json') and not f.startswith('_'))
    falls = falls_into(d, all_caves)
    cache = {}
    def built(n):
        if n not in cache:
            try: cache[n] = Cave(d, n, cfgs, story) if os.path.exists(os.path.join(d, n, 'room.json')) else None
            except Exception as ex: print(f'{n}: (!) cannot read: {type(ex).__name__}: {ex}'); cache[n] = None
        return cache[n]
    out = []
    for n in names:
        c = built(n)
        if c is None: continue
        G = B = {}
        steps = [('x', lambda: check_dark(c)), ('s', lambda: check_sizes(c)), ('t', lambda: check_textures(c)),
                 ('a', lambda: check_features(c)), ('e', lambda: check_events(c, rooms, built)),
                 ('b', lambda: check_models(c)), ('f', lambda: check_layers(c, a.verbose)), ('h', lambda: check_holes(c, a.verbose))]
        for k, fn in steps:
            if k in a.kinds:
                try: fn()
                except Exception as ex:
                    import traceback; traceback.print_exc()
                    c.say('!', f'check {k} failed: {type(ex).__name__}: {ex}')
        if set('wic') & set(a.kinds):
            try:
                G, B = check_walk(c, falls.get(c.alt_of or n, ()))
                if not set('w') & set(a.kinds): c.out = [o for o in c.out if o[0] != 'w']
                check_objects(c, G, B)
            except Exception as ex:
                import traceback; traceback.print_exc()
                c.say('!', f'check w failed: {type(ex).__name__}: {ex}')
        out += [o for o in c.out if o[0] in a.kinds or o[0] == '!']
        if not a.summary:
            for _, ln in c.out:
                if _ in a.kinds or _ == '!': print(ln, flush=True)
    if a.summary:
        cnt = Counter(k for k, _ in out)
        maps = defaultdict(set)
        for k, ln in out: maps[k].add(ln.split(':')[0])
        for k in sorted(cnt): print(f'{k}: {cnt[k]} findings in {len(maps[k])} maps')
        print(f'total: {len(out)} findings in {len({ln.split(":")[0] for _, ln in out})} of {len(names)} maps')

if __name__ == '__main__':
    main()
