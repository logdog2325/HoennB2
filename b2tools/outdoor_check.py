"""Outdoor glitch sweep (sweep_outdoor agent, 2026-10-07): static checks over a built overworld (world.py output: the
connected world's cells, the warp-only maps' groups, the other layouts' cells), one line per finding.

    python3 outdoor_check.py [WORLD] [--kinds k1,k2] [--frames main,PetalburgWoods,...] [--rom ROM] [--summary]

WORLD defaults to $HOENN_WORLD_DIR or work/world. A frame is one matrix: 'main' (the connected world), each
standalone group (data/hoenn_standalone.json) and 'alt_<map>' (world.json alt_cells over the main world; only its own
cells are checked). Kinds (what the player would see; exterior_check.py / ledge_check.py hold the older tools):
  place  a chunk with more than 32 building placements (a door counts 2: ov036 field_g3d_mapper.c propCapacity1 0x20,
         field_buildmodel.c:161-173)
  size   a chunk (WB container: terrain.nsbmd + collision.per + placements.bin) over 110,600 B (needs terrain.nsbmd)
  tex    a terrain material whose image is missing, has no palette pair, or that is not a texture the area's set gets;
         a building model (placed) whose material has no image; stretched texels (a triangle's texels per unit along
         one axis more than 6x off the material's median)
  layer  same-facing terrain surfaces < 2 units apart (melonDS depth-fights them), terrain vs a building < 2, two
         pieces of one building model < 1 (Black 2's own models keep >= 1; b2tools/exterior_layers.py)
  cull   back faces the game camera sees: a camera-angle render (40 degrees, yaw -20/0/+20) without back-face culling
         where the nearest surface is a back face (culled in the game: you see through it)
  hole   nothing drawn where the camera looks (camera-angle render with culling; clear colour = black)
  bld    a Sapphire door (MB_*DOOR*) to a room with no building model over it; a placed model's door off its warp tile;
         solid Sapphire building/roof/door tiles that no model covers as the camera sees it (door-less buildings)
  door   a door warp whose y is more than 2 from its approach tile's height (Black 2 fires warps within 2 units:
         ov012 eventdata_system.c CheckWarpPositionMatch), whose approach tile is not walkable, whose own tile is
         walkable, or a Sapphire warp with no door in its zone
  walk   collision vs Sapphire: a land tile walkable in one game and not the other; a move between two walkable tiles
         that Sapphire allows (elevation rule, from every reachable (tile, elevation) state) and Black 2 blocks
         (height step >= 20 units: ov012 field_actor_tool.c:490-525, side walls 0x51-0x58) or the reverse; ledges
         that jump another way; surfable water that is not surf water in Black 2 or the reverse; surf landings one
         game allows and the other refuses (Sapphire: elevation 3; Black 2: b2_landing)
  ent    (--rom) a person, item, sign or trigger of an outdoor zone on a solid tile, in a building's footprint, or
         outside the zone's cells
  zone   walkable tiles of a map in another zone (banner, music, people and wild Pokemon change inside the map)
"""
import os, sys, json, math, struct, argparse
from collections import defaultdict, Counter, deque
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import exterior_check as ec
ec.CACHE = os.environ.get('OUTDOOR_CHECK_CACHE') or os.path.join(ROOT, 'work', 'check_models')   # (retail pack-0 DAEs, apicula)
CHUNK_LIMIT = 110600
SURF_CLASSES = {0x3d, 0x3e, 0x3f, 0x42, 0x43, 0x40, 0x94, 0x95, 0x96, 0x97}
WALL_SIDES = {0x51: 'e', 0x52: 'w', 0x53: 'n', 0x54: 's', 0x55: 'ne', 0x56: 'nw', 0x57: 'se', 0x58: 'sw'}
LEDGE = {0x72: (1, 0), 0x73: (-1, 0), 0x74: (0, -1), 0x75: (0, 1)}
DIRS = {(1, 0): 'e', (-1, 0): 'w', (0, -1): 'n', (0, 1): 's'}
OPP = {'e': 'w', 'w': 'e', 'n': 's', 's': 'n'}

def wdir(arg=None):
    return arg or os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')

# ------------------------------------------------------------------------------------------------------- frames
class Frame:
    """One matrix of the built world: cells {(cx, cz): directory}, its maps (name -> origin, plan) and zones."""
    def __init__(self, name, wd, cells, maps, only=None, group=None):
        self.name, self.wd, self.cells, self.maps, self.group = name, wd, cells, maps, group
        self.only = only or set(cells)                   # cells to check (alt frames: the swapped ones)
        self._per, self._pl = {}, {}

    def per(self, c):
        if c not in self._per:
            d = self.cells.get(c)
            self._per[c] = open(os.path.join(d, 'collision.per'), 'rb').read() if d else None
        return self._per[c]

    def rec(self, wx, wz):
        """(a, b, class, flags) of a world tile, None outside the built cells."""
        b = self.per((wx // 32, wz // 32))
        if b is None: return None
        return struct.unpack_from('<HHHH', b, 4 + 8 * ((wz % 32) * 32 + wx % 32))

    def y(self, wx, wz):
        """Collision height at a tile's centre (units), None outside."""
        from terrain import heights as H
        r = self.rec(wx, wz)
        if r is None: return None
        a, i = r[0], r[1]
        if a & 3: return None
        nx, ny, nz = H.NORMALS[a >> 2]
        lx, lz = wx % 32, wz % 32
        return -(nx * (lx * 16 - 248) - nz * (lz * 16 - 248) + H.OFFS[i]) / ny

    def placements(self, c):
        if c not in self._pl:
            d = self.cells[c]
            b = open(os.path.join(d, 'placements.bin'), 'rb').read()
            out = []
            for i in range(struct.unpack_from('<I', b, 0)[0]):
                x, y, z, rot = struct.unpack_from('<iiiH', b, 4 + 16 * i)
                res = (b[4 + 16 * i + 14] << 8) | b[4 + 16 * i + 15]
                out.append((res, c[0] * 512 + 256 + x / 4096, y / 4096, c[1] * 512 + 256 - z / 4096, rot * 360 / 0x10000))
            self._pl[c] = out
        return self._pl[c]

    def terrain(self, c):
        d = self.cells[c]
        return [(n, img, P + np.array([c[0] * 512 + 256, 0, c[1] * 512 + 256]), UV, A, f'cell{c[0]}_{c[1]}')
                for n, img, P, UV, A in ec.load_dae(os.path.join(d, 'terrain.dae'))]

    def parts(self, cs, buildings=True):
        out = []
        for c in cs:
            if c not in self.cells: continue
            out += self.terrain(c)
            if buildings:
                for res, X, Y, Z, rot in self.placements(c): out += placed_parts(self, res, X, Y, Z, rot)
        return out

_STANDALONE_REG = {}
def registry(frame):
    """res -> model record for the frame's building pack: pack 0 (main), pack 0 + data/buildings/standalone.json
    (warp-only groups: patches/standalone.py builds their pack from both)."""
    reg = ec.registry()
    if frame.group is None: return reg
    if not _STANDALONE_REG:
        _STANDALONE_REG.update(reg)
        p = os.path.join(ROOT, 'data', 'buildings', 'standalone.json')
        mdir = os.environ.get('HOENN_STANDALONE_BUILDINGS') or os.path.join(ROOT, 'work', 'buildings', 'standalone')
        for m in json.load(open(p))['models'] if os.path.exists(p) else []:
            _STANDALONE_REG[m['res']] = dict(retail=False, dae=os.path.join(mdir, os.path.basename(m['model'])[:-5] + 'dae'),
                                             door=m['door'], dx=m['dx'], dz=m['dz'], what=m.get('what', m['model']), group='standalone')
    return _STANDALONE_REG

_PARTS = {}
def model_parts(frame, res):
    key = (frame.group is not None, res)
    if key in _PARTS: return _PARTS[key]
    r = registry(frame).get(res)
    if r is None: _PARTS[key] = []; return []
    path = r['dae'] if not r['retail'] else ec._retail_dae(res, r['bmd'])
    _PARTS[key] = ec.load_dae(path) if path and os.path.exists(path) else []
    return _PARTS[key]

def placed_parts(frame, res, X, Y, Z, rot, with_door=True):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    out = [(n, img, P @ R.T + np.array([X, Y, Z]), UV, A, f'res{res}') for n, img, P, UV, A in model_parts(frame, res)]
    r = registry(frame).get(res)
    if with_door and r and r['door'] not in (None, 0xFFFF):
        off = R @ np.array([r['dx'], 0, r['dz']])
        out += [(n, img, P @ R.T + np.array([X, Y, Z]) + off, UV, A, f'door{r["door"]}@res{res}')
                for n, img, P, UV, A in model_parts(frame, r['door'])]
    return out

_RETILE = {}
def retiled(name, plan):
    """The plan as world.py builds it: a map's own 'retile' rules (world.py retile_map; Emerald's stand-ins for its new
    structures, data/towns/emerald) applied to its tile classes. Plans of maps without rules (every Sapphire/Ruby map)
    are returned as they are."""
    import world as W_
    if 'cfg' not in _RETILE:
        cfg, _ = W_.load()
        _RETILE['cfg'] = {n: mc.get('retile') for d in (cfg['maps'], cfg['standalone']) for n, mc in d.items() if mc.get('retile')}
    rules = _RETILE['cfg'].get(name)
    if not rules: return plan
    world = {(x, y): (name, c, plan['walkable'][y][x]) for y, row in enumerate(plan['tiles']) for x, c in enumerate(row)}
    W_.retile_map(world, name, dict(ox=0, oz=0, cfg={'retile': rules}))
    return dict(plan, tiles=[[world[(x, y)][1] for x in range(len(row))] for y, row in enumerate(plan['tiles'])],
                walkable=[[world[(x, y)][2] for x in range(len(row))] for y, row in enumerate(plan['tiles'])])

def frames(wd):
    """[Frame] of a built world: main, each standalone group, each alt layout."""
    import world as W_
    import version                # (HOENN_VERSION=emerald: Emerald's plans and settings, notes/EMERALD.md "Emerald's world")
    W = json.load(open(os.path.join(wd, 'world.json')))
    cfg = version.load_json(os.path.join(ROOT, 'data', 'hoenn_world.json'))
    lay = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps']
    M = cfg['margin_cells'] * 32
    maps = {}
    for name, L in lay.items():
        p = version.plan_path(name)
        if not os.path.exists(p) or name in W_.STANDALONE: continue
        if not any(name in z.get('maps', []) for z in W['zones'].values()): continue
        pad = cfg.get('pad_north', {}).get(name, 0); sx, sz = cfg.get('shift', {}).get(name, [0, 0])
        maps[name] = dict(ox=L['tile_x'] + M + sx, oz=L['tile_z'] + M + sz + pad, pad=pad, plan=retiled(name, json.load(open(p))))
    main = {(c['cx'], c['cz']): os.path.join(wd, 'cells', f"{c['cx']:02d}_{c['cz']:02d}") for c in W['cells']}
    out = [Frame('main', wd, main, maps)]
    for g in W.get('standalone', []):
        gm = {n: dict(ox=o[0], oz=o[1], pad=0, plan=retiled(n, json.load(open(version.plan_path(n)))))
              for n, o in g['origins'].items()}
        gcells = {(c['cx'], c['cz']): os.path.join(wd, 'cells', c['dir']) for c in g['cells']}
        out.append(Frame(g['group'], wd, gcells, gm, group=g['group']))
        # (emerald_polish_outdoor 2026-10-12) a warp-only group's other layout (world.py group_alts: Emerald's open Jagged
        # Pass mouth; Sapphire and Ruby have none) as its own frame 'alt_<map>', only its swapped cells checked
        galts = defaultdict(dict)
        for a in g.get('alt_cells', []): galts[a['map']][(a['cx'], a['cz'])] = os.path.join(wd, 'cells', a['dir'])
        for name, cs in galts.items():
            cells = dict(gcells); cells.update(cs)
            f = Frame(f'alt_{name}', wd, cells, gm, only=set(cs), group=g['group'])
            f.alt_plans = {name: os.path.join(wd, 'alt_plans', next(p for p in os.listdir(os.path.join(wd, 'alt_plans')) if p.startswith(name + '_')))}
            f.maps = dict(gm); f.maps[name] = dict(gm[name], plan=json.load(open(f.alt_plans[name])))
            out.append(f)
    alts = defaultdict(dict)
    for a in W.get('alt_cells', []): alts[a['map']][(a['cx'], a['cz'])] = os.path.join(wd, 'cells', a['dir'])
    for name, cs in alts.items():
        cells = dict(main); cells.update(cs)
        f = Frame(f'alt_{name}', wd, cells, maps, only=set(cs))
        f.alt_plans = {name: os.path.join(wd, 'alt_plans', next(p for p in os.listdir(os.path.join(wd, 'alt_plans')) if p.startswith(name + '_')))}
        f.maps = dict(maps); f.maps[name] = dict(maps[name], plan=json.load(open(f.alt_plans[name])))
        out.append(f)
    for f in out: f.world = W
    return out

# --------------------------------------------------------------------------------------------- Sapphire per tile
_REPO = {}
def repo():
    if 'r' not in _REPO:
        sys.path.insert(0, os.path.join(ROOT, 'converter'))
        from gba import world_repo              # (Repo(pokeruby); HOENN_VERSION=emerald: Emerald's maps)
        _REPO['r'] = world_repo()
    return _REPO['r']

_BEHS = {}
def behaviours(name, layout=None):
    """Numeric metatile behaviour grid (H, W) of a Sapphire map (its own or another layout)."""
    key = (name, layout)
    if key not in _BEHS:
        r = repo(); mj = r.map_json(name)
        from gba import MetatileRenderer
        g, lay = r.layout_grid(layout or mj['layout'])
        mr = MetatileRenderer(r, lay['primary_tileset'], lay['secondary_tileset'])
        cache = {}
        B = np.zeros(g.shape, int)
        for y in range(g.shape[0]):
            for x in range(g.shape[1]):
                m = int(g[y, x]) & 0x3FF
                if m not in cache: cache[m] = mr.behavior(m)
                B[y, x] = cache[m]
        _BEHS[key] = B
    return _BEHS[key]

_NAMES = {}
def mb(name):
    if not _NAMES:
        import re
        src = open(os.path.join(ROOT, 'external', 'pokeruby', 'include', 'constants', 'metatile_behaviors.h')).read()
        for k, v in re.findall(r'#define (MB_\w+)\s+(0x[0-9A-Fa-f]+|\d+)', src): _NAMES[k] = int(v, 0)
    return _NAMES[name]

def mb_name(v):
    mb('MB_NORMAL')
    return next((k for k, x in _NAMES.items() if x == v), hex(v))

_SURF = []
def surfable(b):
    if not _SURF:
        from terrain import water
        _SURF.extend(water._surf_table())
    return b < len(_SURF) and _SURF[b]

class Sapphire:
    """Sapphire's tiles of a frame by world tile: (map, x, y, solid, elevation, behaviour)."""
    def __init__(self, frame):
        self.t = {}
        for name, mp in frame.maps.items():
            plan = mp['plan']; W, H = plan['size']
            layout = None
            if getattr(frame, 'alt_plans', {}).get(name):
                layout = os.path.basename(frame.alt_plans[name])[len(name) + 1:-5]
            B = behaviours(name, layout)
            rows = [(y, y) for y in range(H)] + [(-mp['pad'] + k, k % 2) for k in range(mp['pad'])]
            for y, src in rows:
                for x in range(W):
                    self.t[(mp['ox'] + x, mp['oz'] + y)] = (name, x, src, not plan['walkable'][src][x],
                                                           plan['elevation'][src][x], int(B[src, x]), plan['tiles'][src][x])
    def get(self, k): return self.t.get(k)

# ------------------------------------------------------------------------------------------------------ helpers
def tile_cells(frame):
    return sorted(frame.only)

def in_only(frame, wx, wz):
    return (wx // 32, wz // 32) in frame.only

def b2_land(r):
    return r is not None and not (r[3] & 1) and r[2] not in SURF_CLASSES

NOLAND = 0x4000         # b2tools/terrain/heights.py step 12 / patches/hm_free.py SurfLandingTileType

def b2_landing(frame, a, b):
    """Black 2 lets a surfer on tile a land on tile b (final_check 2026-10-08, ov036 CheckSurfExitEvent 0x02182cd4): the
    tile in the key's direction - or the one beyond it when that is a shore (class 0x41/0x44, MapTile_IsSurfEdge) - must
    have neither flag bit 0 (solid) nor bit 1 (surfable, CheckSurfBeginTiles); no actor in the way (func_ov036_02182fdc).
    There is NO height test (unlike walking's 20 units, ActorRouteCollCheckCore, and surfing off land, 0 <= land - water
    < 20, CheckSurfHeightAllow 0x0219ab30): a surfer climbs onto any deck; Black 2's own maps keep every landable tile
    next to surf water 0, 4 or 8 units above it (1,121 cells in a/0/0/8). hm_free's SurfLandingTileType also refuses a
    tile with NOLAND (Sapphire's elevation rule, heights.py step 12)."""
    rb = frame.rec(*b)
    return rb is not None and not (rb[3] & (3 | NOLAND)) and rb[2] not in SURF_CLASSES

def b2_surf(r):
    """Surf water (and Black 2's waterfall tiles, class 0x40 flags 0x13 as in Route 11 chunk 72: climbed with Waterfall)."""
    return r is not None and (r[2] == 0x40 or (not (r[3] & 1) and r[2] in SURF_CLASSES))

# --------------------------------------------------------------------------------------------------------- place
def check_place(frame, out):
    for c in tile_cells(frame):
        n = 0
        for res, X, Y, Z, rot in frame.placements(c):
            r = registry(frame).get(res)
            n += 2 if r and r['door'] not in (None, 0xFFFF) else 1
        if n > 32: out.append(('place', f'cell {c}: {n} placement slots (limit 32)', c))

# ---------------------------------------------------------------------------------------------------------- size
def check_size(frame, out):
    for c in tile_cells(frame):
        d = frame.cells[c]
        p = os.path.join(d, 'terrain.nsbmd')
        if not os.path.exists(p): out.append(('size', f'cell {c}: no terrain.nsbmd (ToNsbmd not run)', c)); continue
        n = 20 + sum(os.path.getsize(os.path.join(d, f)) for f in ('terrain.nsbmd', 'collision.per', 'placements.bin'))
        if n > CHUNK_LIMIT: out.append(('size', f'cell {c}: chunk {n} B (limit {CHUNK_LIMIT})', c))

# ---------------------------------------------------------------------------------------------------------- walk
JUMP = {0x38: (1, 0), 0x39: (-1, 0), 0x3A: (0, -1), 0x3B: (0, 1)}       # MB_JUMP_EAST/WEST/NORTH/SOUTH
def _sap_blocked(beh, side):
    """Sapphire's directional walls (metatile_behavior.c Is<Side>Blocked)."""
    return beh in {'e': {0x30, 0x34, 0x36, 0xC1, 0xBE}, 'w': {0x31, 0x35, 0x37, 0xC1, 0xBE},
                   'n': {0x32, 0x34, 0x35, 0xC0}, 's': {0x33, 0x36, 0x37, 0xC0}}[side]

def _warp_tiles(frame):
    """Sapphire warp tiles of the frame's maps (world tiles)."""
    out = set()
    for name, mp in frame.maps.items():
        for w in mp['plan']['warps']:
            out.add((mp['ox'] + w['x'], mp['oz'] + w['y']))
    return out

def _doors(frame):
    """The frame's door warps (world.json zones' doors of its maps): [(door dict, zone id)]."""
    out = []
    for zid, z in frame.world['zones'].items():
        if (z.get('group') or None) != frame.group: continue
        for d in z.get('doors', []):
            if d.get('foreign') or d['map'] not in frame.maps: continue
            out.append((d, zid))
    return out

def check_walk(frame, out, S=None):
    S = S or Sapphire(frame)
    warps = _warp_tiles(frame)
    sap_walk = lambda k: (lambda s: s is not None and not s[3] and not surfable(s[5]) and s[5] not in JUMP)(S.get(k))
    sap_water = lambda k: (lambda s: s is not None and not s[3] and surfable(s[5]))(S.get(k))
    # Sapphire: reachable (tile, z) states from every warp tile, on foot, jumping ledges, surfing (HMs ignored)
    seen, q = set(), deque()
    for k in warps:
        s = S.get(k)
        if s is None or surfable(s[5]): continue          # (a warp in open water: Route 131's Sky Pillar door)
        z = s[4] if s[4] not in (0, 15) else 3
        seen.add((k, z)); q.append((k, z))
    def push(st):
        if st not in seen: seen.add(st); q.append(st)
    while q:
        (x, z0), z = q.popleft()
        a = S.get((x, z0))
        if a is None: continue
        on_water = sap_water((x, z0))
        for (dx, dz), side in DIRS.items():
            k = (x + dx, z0 + dz); b = S.get(k)
            if b is None: continue
            if _sap_blocked(a[5], side) or _sap_blocked(b[5], OPP[side]): continue
            if b[5] in JUMP and JUMP[b[5]] == (dx, dz) and not on_water:
                k2 = (x + 2 * dx, z0 + 2 * dz)
                if sap_walk(k2): push((k2, z if 15 in (S.get(k2)[4], a[4]) else S.get(k2)[4]))
                continue
            if b[3] and k not in warps: continue
            if sap_water(k):
                push((k, 1)); continue
            if on_water:                          # landing: only onto elevation 3 (pokeruby field_player_avatar.c
                # CheckForObjectEventCollision -> sub_8058EF0: an elevation mismatch, the tile's elevation 3, no object;
                # 0 and 1 never mismatch the surfer's 1: it moves on; final_check 2026-10-08: piers of elevation 4,
                # e.g. Mr. Briney's jetty, are no landing)
                if (sap_walk(k) and b[4] in (0, 1, 3)) or k in warps:   # (z: the tile's 1 or 3; 0 keeps the surfer's 1)
                    push((k, (3 if b[4] == 3 else 1) if k not in warps else (3 if b[4] in (0, 15) else b[4])))
                continue
            if not sap_walk(k) and k not in warps: continue
            if z != 0 and b[4] not in (0, 15) and b[4] != z: continue
            # pokeruby ObjectEventUpdateZCoord: the new tile's elevation (0 too: from a 0 tile any level is open),
            # unchanged when the new or the old tile is 15 (bridges)
            push((k, z if 15 in (b[4], a[4]) else b[4]))
    reach_s = {k for k, z in seen}
    states = defaultdict(set)
    for k, z in seen: states[k].add(z)
    # Black 2: reachable tiles from the doors' approach tiles (on foot, ledges, surfing within 20 units)
    import world as W_
    starts = []
    for d, zid in _doors(frame):
        dx, dz = W_.DOOR_STEP.get(d.get('dir', 2), (0, 1))
        starts.append(((d['x'] - 8) // 16 + dx, (d['z'] - 8) // 16 + dz))
    def sides(r): return WALL_SIDES.get(r[2], '') if r else ''
    def b2_move(a, b, d):
        ra, rb = frame.rec(*a), frame.rec(*b)
        if not b2_land(rb) or not (b2_land(ra) or b2_surf(ra)): return False
        if b2_surf(ra): return b2_landing(frame, a, b)  # (dismount: see b2_landing)
        ya, yb = frame.y(*a), frame.y(*b)
        if ya is None or yb is None or abs(ya - yb) >= 20: return False
        return DIRS[d] not in sides(ra) and OPP[DIRS[d]] not in sides(rb)
    reach_b, q = set(), deque()
    for s in starts:
        if b2_land(frame.rec(*s)): reach_b.add(s); q.append(s)
    while q:
        a = q.popleft(); ra = frame.rec(*a)
        for d in DIRS:
            b = (a[0] + d[0], a[1] + d[1]); rb = frame.rec(*b)
            if rb is None or b in reach_b: continue
            if rb[2] in LEDGE and LEDGE[rb[2]] == d and b2_land(ra):
                c = (b[0] + d[0], b[1] + d[1])
                if b2_land(frame.rec(*c)) and c not in reach_b: reach_b.add(c); q.append(c)
                continue
            if b2_surf(rb):
                ya, yb = frame.y(*a), frame.y(*b)
                if ya is None or yb is None: continue
                if (b2_surf(ra) and (abs(ya - yb) < 20 or 0x40 in (ra[2], rb[2]))) or (not b2_surf(ra) and 0 <= ya - yb < 20):
                    reach_b.add(b); q.append(b)     # (surfing: the 20-unit step rule too; waterfalls: climbed)
                continue
            if b2_move(a, b, d): reach_b.add(b); q.append(b)
    only = lambda k: in_only(frame, *k)
    frame.reach = (reach_s, reach_b, states)
    # tiles
    for k, s in sorted(S.t.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if not only(k) or k in warps: continue
        r = frame.rec(*k)
        if r is None: continue
        name, x, y = s[0], s[1], s[2]
        where = f'{name} ({x},{y}) world {k}'
        if s[5] in JUMP:
            want = {(1, 0): 0x72, (-1, 0): 0x73, (0, -1): 0x74, (0, 1): 0x75}[JUMP[s[5]]]
            if r[2] != want and k in reach_s | reach_b:
                out.append(('walk', f'{where}: Sapphire ledge {mb_name(s[5])}, Black 2 class {r[2]:#x} flags {r[3]:#x}', k))
            continue
        if sap_walk(k) and k in reach_s and not b2_land(r):
            out.append(('walk', f'{where}: walkable in Sapphire ({s[6]}, {mb_name(s[5])}), solid in Black 2 '
                                f'(class {r[2]:#x} flags {r[3]:#x})', k))
        elif b2_land(r) and k in reach_b and not sap_walk(k):
            what = 'water' if sap_water(k) else 'solid'
            out.append(('walk', f'{where}: walkable in Black 2, {what} in Sapphire ({s[6]}, {mb_name(s[5])})', k))
        elif sap_water(k) and k in reach_s and not b2_surf(r) and s[5] != mb('MB_WATERFALL'):
            out.append(('walk', f'{where}: surf water in Sapphire ({mb_name(s[5])}), not in Black 2 (class {r[2]:#x} '
                                f'flags {r[3]:#x})', k))
        elif b2_surf(r) and k in reach_b and not sap_water(k):
            out.append(('walk', f'{where}: surf water in Black 2, not in Sapphire ({s[6]}, {mb_name(s[5])})', k))
    # reachable in Sapphire, walkable/surfable in Black 2 too, but Black 2 never gets there (cut off by a solid tile,
    # a height step, a railing, a ledge the wrong way): grouped into regions
    cut = {k for k in reach_s if only(k) and k not in reach_b and k not in warps and
           ((sap_walk(k) and b2_land(frame.rec(*k))) or (sap_water(k) and b2_surf(frame.rec(*k))))}
    while cut:
        k0 = min(cut, key=lambda k: (k[1], k[0])); reg, q2 = {k0}, [k0]; cut.discard(k0)
        while q2:
            x, z = q2.pop()
            for dx, dz in DIRS:
                n = (x + dx, z + dz)
                if n in cut: cut.discard(n); reg.add(n); q2.append(n)
        s = S.get(k0)
        edge = sorted({(x + dx, z + dz) for x, z in reg for dx, dz in DIRS if (x + dx, z + dz) not in reg and
                       (x + dx, z + dz) in reach_s})[:6]
        edge = [(e, 'B2 reached' if e in reach_b else 'B2 %s' % ('land' if b2_land(frame.rec(*e)) else 'surf' if
                 b2_surf(frame.rec(*e)) else 'solid'), 'S ' + mb_name(S.get(e)[5])) for e in edge]
        out.append(('walk', f'{s[0]} ({s[1]},{s[2]}) world {k0}: {len(reg)} tiles reachable in Sapphire are cut off in '
                            f'Black 2 ({sum(1 for k in reg if sap_water(k))} water; next to reached tiles {edge})', k0))
    # tiles outside every map that Black 2 lets you walk on
    for k in sorted(reach_b, key=lambda k: (k[1], k[0])):
        if k not in S.t and only(k): out.append(('walk', f'world {k}: walkable in Black 2 outside every map', k))
    # moves between tiles walkable in both games
    for k in sorted(reach_s & reach_b, key=lambda k: (k[1], k[0])):
        if not only(k) or not sap_walk(k) or not b2_land(frame.rec(*k)): continue
        a = S.get(k)
        for d, side in DIRS.items():
            n = (k[0] + d[0], k[1] + d[1])
            b = S.get(n)
            if b is None or n in warps or not sap_walk(n) or not b2_land(frame.rec(*n)): continue
            sap = not (_sap_blocked(a[5], side) or _sap_blocked(b[5], OPP[side])) and \
                any(z == 0 or b[4] in (0, 15) or b[4] == z for z in states[k])
            b2 = b2_move(k, n, d)
            if sap != b2:
                out.append(('walk', f'{a[0]} ({a[1]},{a[2]}) -> {side} world {k}->{n}: Sapphire '
                                    f'{"allows" if sap else "blocks"} (elev {sorted(states[k])}->{b[4]}), Black 2 '
                                    f'{"allows" if b2 else "blocks"} (y {frame.y(*k):.0f}->{frame.y(*n):.0f}, '
                                    f'sides {sides(frame.rec(*k)) or "-"}/{sides(frame.rec(*n)) or "-"})', k))

    # surf landings (final_check 2026-10-08): from a water tile both games surf on, onto a tile both walk on
    for k in sorted((reach_s | reach_b), key=lambda k: (k[1], k[0])):
        if not only(k) or not sap_water(k) or not b2_surf(frame.rec(*k)): continue
        for d, side in DIRS.items():
            n = (k[0] + d[0], k[1] + d[1])
            b = S.get(n); rn = frame.rec(*n)
            if b is None or n in warps or not sap_walk(n) or not b2_land(rn) or rn[2] in (0x41, 0x44): continue
            sap = b[4] in (0, 1, 3) and not (_sap_blocked(S.get(k)[5], side) or _sap_blocked(b[5], OPP[side]))
            b2 = b2_landing(frame, k, n)
            if sap != b2:
                out.append(('walk', f'{b[0]} ({b[1]},{b[2]}) world {n}: surf landing from {k} ({side}): Sapphire '
                                    f'{"allows" if sap else "blocks"} (elevation {b[4]}), Black 2 '
                                    f'{"allows" if b2 else "blocks"} (step {frame.y(*n) - frame.y(*k):.0f}: water y '
                                    f'{frame.y(*k):.0f} -> {frame.y(*n):.0f}, class {rn[2]:#x} flags {rn[3]:#x})', n))

# ----------------------------------------------------------------------------------------------------------- bld
MOUTH_TEX = ('doukutu01', 'out57_doukutu')
def check_bld(frame, out):
    """Sapphire's door warps against the models: an animated door (MB_ANIMATED_DOOR: a building's door) needs a
    placed model whose door model (registry door res at origin + (dx, dz)) stands on the warp tile; a non-animated
    door (caves, gates) needs a cave mouth (doukutu01 terrain) or a placed model over the tile."""
    doors_at = {}
    models_at = defaultdict(list)
    door_res = {r['door'] for r in registry(frame).values() if r.get('door') not in (None, 0xFFFF)}
    for c in frame.cells:
        for res, X, Y, Z, rot in frame.placements(c):
            r = registry(frame).get(res)
            P = [p[2] for p in model_parts(frame, res)]
            P = np.concatenate(P).reshape(-1, 3) if P else None
            if P is not None:
                cs, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
                xs = X + P[:, 0] * cs + P[:, 2] * sn; zs = Z - P[:, 0] * sn + P[:, 2] * cs
                for tx in range(int(xs.min() // 16), int((xs.max() - 1e-3) // 16) + 1):
                    for tz in range(int(zs.min() // 16), int((zs.max() - 1e-3) // 16) + 1):
                        models_at[(tx, tz)].append(res)
            if res in door_res and P is not None and len(P):         # a door model placed by itself (a second door)
                doors_at[(int((X + (P[:, 0].min() + P[:, 0].max()) / 2) // 16), int(Z // 16))] = res
            if r and r['door'] not in (None, 0xFFFF):
                cs, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
                dxw, dzw = r['dx'] * cs + r['dz'] * sn, -r['dx'] * sn + r['dz'] * cs
                DP = [p[2] for p in model_parts(frame, r['door'])]
                cx = (np.concatenate(DP).reshape(-1, 3)[:, 0].min() + np.concatenate(DP).reshape(-1, 3)[:, 0].max()) / 2 if DP else 0
                doors_at[(int((X + dxw + cx) // 16), int((Z + dzw) // 16))] = res
    mouths = set()
    for c in frame.cells:
        if not any(abs(c[0] - o[0]) <= 1 and abs(c[1] - o[1]) <= 1 for o in frame.only): continue
        for n, img, P, UV, A, src in frame.terrain(c):
            if n not in MOUTH_TEX: continue
            for t in P:
                m = t.mean(0); mouths.add((int(m[0] // 16), int(m[2] // 16)))
    for name, mp in frame.maps.items():
        B = behaviours(name, os.path.basename(frame.alt_plans[name])[len(name) + 1:-5] if name in getattr(frame, 'alt_plans', {}) else None)
        for w in mp['plan']['warps']:
            t = (mp['ox'] + w['x'], mp['oz'] + w['y'])
            if not in_only(frame, *t) or not (0 <= w['y'] < B.shape[0] and 0 <= w['x'] < B.shape[1]): continue
            beh = int(B[w['y'], w['x']])
            where = f'{name} warp {w["id"]} ({w["x"]},{w["y"]}) world {t} to {w["dest"]}'
            if beh == mb('MB_ANIMATED_DOOR'):
                if t in doors_at: continue
                near = [d for d in doors_at if abs(d[0] - t[0]) + abs(d[1] - t[1]) <= 1]
                if near: out.append(('bld', f'{where}: door model at {near[0]} (res {doors_at[near[0]]}), not on the warp tile', t))
                elif models_at.get(t): out.append(('bld', f'{where}: building res {models_at[t]} over it but no door model', t))
                else: out.append(('bld', f'{where}: no building model (Sapphire draws a house door here)', t))
            elif beh == mb('MB_NON_ANIMATED_DOOR'):
                if t in mouths or models_at.get(t) or models_at.get((t[0], t[1] - 1)) or \
                        any((t[0] + dx, t[1] + dz) in mouths for dx in (-1, 0, 1) for dz in (-1, 0, 1)):   # (a doorway in
                    # the model's front: Fortree's tree houses stand on the row north of their door tiles)
                    continue
                out.append(('bld', f'{where}: no cave mouth or building model (Sapphire: non-animated door)', t))
    # door-less buildings (buildings_audit 2026-10-08: Route 118's house stood invisible, a solid 4x3 patch of grass):
    # Sapphire building / roof / door tiles that are solid in Black 2 and that no placed model covers as the camera sees
    # it (a model point h units up hides the ground h * cot(40 degrees) further north: a dome's knob tile, a tall
    # building's roof row), per connected group
    seen_at = set()
    cot = 1 / math.tan(math.radians(40))
    for c in frame.cells:
        for res, X, Y, Z, rot in frame.placements(c):
            P = [p[2] for p in model_parts(frame, res)]
            if not P: continue
            P = np.concatenate(P).reshape(-1, 3)
            cs, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            xs = X + P[:, 0] * cs + P[:, 2] * sn; zs = Z - P[:, 0] * sn + P[:, 2] * cs
            zv = zs - np.maximum(P[:, 1], 0) * cot
            for tx in range(int(xs.min() // 16), int((xs.max() - 1e-3) // 16) + 1):
                for tz in range(int(min(zv.min(), zs.min()) // 16), int((zs.max() - 1e-3) // 16) + 1):
                    seen_at.add((tx, tz))
    for name, mp in frame.maps.items():
        if frame.name.startswith('alt_') and name not in getattr(frame, 'alt_plans', {}): continue
        T = mp['plan']['tiles']; ox, oz = mp['ox'], mp['oz']
        bad = set()
        for y in range(len(T)):
            for x in range(len(T[0])):
                t = (ox + x, oz + y)
                if T[y][x] not in ('building', 'building_roof', 'door') or not in_only(frame, *t) or t in seen_at: continue
                r = frame.rec(*t)
                if r is not None and r[3] & 1: bad.add((x, y))
        seen = set()
        for s in sorted(bad, key=lambda p: (p[1], p[0])):
            if s in seen: continue
            comp, q = [], deque([s]); seen.add(s)
            while q:
                x, y = q.popleft(); comp.append((x, y))
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if n in bad and n not in seen: seen.add(n); q.append(n)
            xs = [p[0] for p in comp]; ys = [p[1] for p in comp]
            out.append(('bld', f'{name} ({min(xs)}-{max(xs)},{min(ys)}-{max(ys)}): {len(comp)} solid Sapphire building '
                               f'tiles no model covers (an invisible building?)', (ox + min(xs), oz + min(ys))))

# ---------------------------------------------------------------------------------------------------------- door
def s16(v): return v - 0x10000 if v >= 0x8000 else v

def check_door(frame, out, S=None):
    """Every door warp of the frame's zones (world.json doors, hand-made towns' slots) against the built collision,
    and every Sapphire warp of its maps against the doors."""
    import world as W_
    S = S or Sapphire(frame)
    have = set()
    for d, zid in _doors(frame):
        have.add((d['map'], d['id']))
        t = ((d['x'] - 8) // 16, (d['z'] - 8) // 16)
        if not in_only(frame, *t): continue
        dx, dz = W_.DOOR_STEP.get(d.get('dir', 2), (0, 1))
        a = (t[0] + dx, t[1] + dz)
        rt, ra = frame.rec(*t), frame.rec(*a)
        where = f"zone {zid} {d['map']} warp {d['id']} at {t} (dir {d.get('dir', 2)}, type {d.get('type', 3)})"
        mp = frame.maps.get(d['map']); w = next((w for w in mp['plan']['warps'] if w['id'] == d['id']), None) if mp else None
        outside = w is not None and not (0 <= w['x'] < mp['plan']['size'][0] and 0 <= w['y'] < mp['plan']['size'][1])
        if ra is None: out.append(('door', f'{where}: approach tile {a} outside the built cells', t)); continue
        if not (b2_land(ra) or b2_surf(ra)):
            out.append(('door', f'{where}: approach tile {a} is solid (class {ra[2]:#x} flags {ra[3]:#x})'
                                + (' [Sapphire tile outside its map]' if outside else ''), t))
        ya = frame.y(*a)
        if ya is not None and abs(s16(d['y']) - ya) > 2:
            out.append(('door', f'{where}: y {s16(d["y"])} vs approach tile {a} at {ya:.1f}'
                                + (' [Sapphire tile outside its map]' if outside else ''), t))
        if rt is not None and (b2_land(rt) or b2_surf(rt)):
            out.append(('door', f'{where}: the warp tile itself is walkable (Black 2 warps stand on solid tiles)', t))
        if d.get('unresolved'):
            out.append(('door', f'{where}: leads nowhere (unresolved {d["unresolved"]})', t))
    for zid, z in frame.world['zones'].items():
        if (z.get('group') or None) != frame.group: continue
        for d in z.get('slot_doors', []): have.add((d['map'], d['id']))
        for k, (x, y, zz) in z.get('warps', {}).items():
            t = ((x - 8) // 16, (zz - 8) // 16); a = (t[0], t[1] + 1)
            if not in_only(frame, *t) or frame.rec(*a) is None: continue
            ya = frame.y(*a)
            if not b2_land(frame.rec(*a)):
                out.append(('door', f'zone {zid} warp slot {k} at {t}: approach tile {a} is solid', t))
            if ya is not None and abs(s16(y) - ya) > 2:
                out.append(('door', f'zone {zid} warp slot {k} at {t}: y {s16(y)} vs approach tile at {ya:.1f}', t))
    for name, mp in frame.maps.items():
        for w in mp['plan']['warps']:
            t = (mp['ox'] + w['x'], mp['oz'] + w['y'])
            if (name, w['id']) not in have and in_only(frame, *t):
                out.append(('door', f'{name} Sapphire warp {w["id"]} at {t} to {w["dest"]}: no door in its zone', t))

# ---------------------------------------------------------------------------------------------------------- zone
def check_zone(frame, out):
    """Walkable/surfable tiles of a map whose zone (world.json zone_rects, else the cell's zone) is another map's:
    the banner, music, people and wild Pokemon change there, inside the map (Sapphire changes them at map edges).
    Since every map has its own zone rectangles (world.py zone_rects, zone_edges 2026-10-08) there should be none."""
    W = frame.world
    owner = {}
    for c in (W['cells'] if frame.group is None else next(g for g in W['standalone'] if g['group'] == frame.group)['cells']):
        owner[(c['cx'], c['cz'])] = c['zone']
    rects = W.get('zone_rects', []) if frame.group is None else []
    zone_of_map = {}
    for zid, z in W['zones'].items():
        if (z.get('group') or None) != frame.group: continue
        for m in z.get('maps', []): zone_of_map[m] = int(zid)
    map_of_zone = {v: k for k, v in zone_of_map.items()}
    bad = defaultdict(list)
    for name, mp in frame.maps.items():
        W_, H_ = mp['plan']['size']
        for y in range(-mp['pad'], H_):
            for x in range(W_):
                k = (mp['ox'] + x, mp['oz'] + y)
                if not in_only(frame, *k): continue
                r = frame.rec(*k)
                if not (b2_land(r) or b2_surf(r)): continue
                z = next((zz for x0, z0, x1, z1, zz in rects if x0 <= k[0] <= x1 and z0 <= k[1] <= z1), owner.get((k[0] // 32, k[1] // 32)))
                if z != zone_of_map.get(name): bad[(name, z)].append(k)
    for (name, z), ks in sorted(bad.items(), key=lambda kv: -len(kv[1])):
        ks.sort(key=lambda k: (k[1], k[0]))
        out.append(('zone', f'{name}: {len(ks)} walkable tiles in zone {z} ({map_of_zone.get(z, "?")}), e.g. {ks[:3]}', ks[0]))

# ----------------------------------------------------------------------------------------------------------- tex
_TEXSETS = {}
def texture_names(frame):
    """(terrain texture names, building texture names) the frame's area gets: map set 3 + the terrain modules'
    TEXTURES + data/hoenn_ash.json (patches/hoenn_textures.py) [+ the group's 'textures', patches/standalone.py];
    building set 0 + the enabled registries' textures [+ data/buildings/standalone.json's textures.txt]."""
    key = frame.group
    if key in _TEXSETS: return _TEXSETS[key]
    import nsbtx, b2files, terrain
    from area2_buildings import groups
    F = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    tn = {n for n, _ in nsbtx._parse(b2files.map_textures(F, 3))['texs']}
    for f in terrain.modules(): tn |= set(getattr(f, 'TEXTURES', {}))
    ap = os.path.join(ROOT, 'data', 'hoenn_ash.json')
    if os.path.exists(ap): tn |= set(json.load(open(ap)).get('textures', {}))
    bn = {n for n, _ in nsbtx._parse(b2files.building_textures(F, 0))['texs']}
    for g in groups():
        bn |= {t[1] for t in json.load(open(os.path.join(ROOT, 'data', 'buildings', f'{g}.json'))).get('textures', [])}
    if frame.group is not None:
        import version
        sa = version.load_json(os.path.join(ROOT, 'data', 'hoenn_standalone.json'))['groups'].get(frame.group, {})
        tn |= set(sa.get('textures', {}))
        mdir = os.environ.get('HOENN_STANDALONE_BUILDINGS') or os.path.join(ROOT, 'work', 'buildings', 'standalone')
        tl = os.path.join(mdir, 'textures.txt')
        if os.path.exists(tl): bn |= {l.split()[1] for l in open(tl) if len(l.split()) > 1}
    _TEXSETS[key] = (tn, bn)
    return _TEXSETS[key]

STRETCH_OK = {'kawa01b', 'kawa01a', 'sea_diving', 'doukutu01', 'out57_doukutu', 'kaidan01a', 'out57_kaidan'}
def check_tex(frame, out):
    tn, bn = texture_names(frame)
    seen = set()
    stats = defaultdict(list)                       # material -> [(texels/unit major, minor, tile)]
    for c in tile_cells(frame):
        for n, img, P, UV, A, src in frame.terrain(c):
            tname = os.path.splitext(os.path.basename(img))[0].replace('_', '.') if img else n
            tname = n if n in tn else (tname if tname in tn else os.path.splitext(os.path.basename(img))[0] if img else n)
            if tname not in tn and (n, 'terrain') not in seen:
                seen.add((n, 'terrain')); out.append(('tex', f'terrain material {n} (cell {c}) is not in the area\'s texture set (draws white)', (c[0] * 32, c[1] * 32)))
            if img is None or not os.path.exists(img):
                if (n, 'img') not in seen: seen.add((n, 'img')); out.append(('tex', f'terrain material {n} (cell {c}) has no image', (c[0] * 32, c[1] * 32)))
                continue
            T = ec._tex(img); th, tw = T.shape[:2]
            e1, e2 = P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]
            d1, d2 = (UV[:, 1] - UV[:, 0]) * [tw, th], (UV[:, 2] - UV[:, 0]) * [tw, th]
            for t in range(len(P)):
                # surface basis: e1 and its perpendicular in the triangle's plane
                L1 = np.linalg.norm(e1[t]); nrm = np.cross(e1[t], e2[t]); An = np.linalg.norm(nrm)
                if L1 < 1e-6 or An < 1e-6: continue
                b1 = e1[t] / L1; b2 = np.cross(nrm / An, b1)
                S = np.array([[L1, 0], [np.dot(e2[t], b1), np.dot(e2[t], b2)]])      # rows: e1, e2 in (b1, b2)
                Tm = np.array([d1[t], d2[t]])                                         # rows: texel deltas
                try: J = np.linalg.solve(S, Tm)                                       # texels per unit along b1, b2
                except np.linalg.LinAlgError: continue
                sv = np.linalg.svd(J, compute_uv=False)
                m = P[t].mean(0)
                stats[n].append((sv[0], sv[1], (int(m[0] // 16), int(m[2] // 16)), src))
        for res, X, Y, Z, rot in frame.placements(c):
            if registry(frame).get(res, {}).get('retail'): continue       # (Black 2's own models: their own textures)
            for n, img, P, UV, A in model_parts(frame, res):
                if n not in bn and (n, res) not in seen:
                    seen.add((n, res)); out.append(('tex', f'building res {res} material {n} is not in the building texture set', (int(X // 16), int(Z // 16))))
    for n, rows in stats.items():
        if n in STRETCH_OK: continue
        a = np.array([[r[0], r[1]] for r in rows])
        med = np.median(a[:, 0])
        bad = [r for r in rows if r[1] < 1e-3 * med and r[0] > 0.02 * med]     # a whole texel row smeared over the face
        stretched = [r for r in rows if r[0] > 1e-6 and r[1] > 1e-6 and (r[0] > 6 * med or r[1] < med / 6)]
        for kind, lst in (('smeared (one texel line)', bad), ('stretched', stretched)):
            if not lst: continue
            tiles = sorted({r[2] for r in lst})
            out.append(('tex', f'{n}: {len(lst)} triangles {kind} (median {med:.2f} texels/unit; e.g. {lst[0][0]:.2f}/{lst[0][1]:.3f}), tiles {tiles[:6]}', tiles[0]))

# ----------------------------------------------------------------------------------------------- geometry checks
def near_walk(frame):
    """Tiles the game camera can show: within 8 columns / 7 rows of a tile Black 2 lets you stand or surf on."""
    if getattr(frame, '_near', None) is None:
        walk = set()
        for c in frame.cells:
            b = frame.per(c)
            for i in range(1024):
                a, h, cls, fl = struct.unpack_from('<HHHH', b, 4 + 8 * i)
                r = (a, h, cls, fl)
                if b2_land(r) or b2_surf(r): walk.add((c[0] * 32 + i % 32, c[1] * 32 + i // 32))
        near = set()
        for x, z in walk:
            for dz in range(-7, 8):
                for dx in range(-8, 9): near.add((x + dx, z + dz))
        frame._near = near
    return frame._near

DOOR_RES = set()
def layer_pairs(parts, found, step=2.0, span=None, limit=2.0):
    """exterior_check.layer_pairs, keyed by (mat a, mat b, kind) where kind tells the sources apart: 'terrain',
    'terrain/building', 'model' (two pieces of one placed model), 'model/door' (a model and its own door model),
    'buildings' (two placements)."""
    if not parts: return found
    P, UV, Mi, Si, A, mats, srcs = ec.flatten(parts)
    N = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    L = np.linalg.norm(N, axis=1); ok = L > 1e-6
    N[ok] /= L[ok][:, None]
    dom = np.argmax(np.abs(N), axis=1)
    for ax in (0, 1, 2):
        sel = np.nonzero(ok & (dom == ax))[0]
        if not len(sel): continue
        a, b = ec.AXES[ax]
        off = {1: (0.7, 1.3), 2: (0.7, 1.1), 0: (1.3, 1.1)}[ax]
        P2 = P[sel][:, :, [a, b]]
        rows = []
        for t, ii, jj, w0, w1, w2 in ec._raster(P2, step, off):
            T = sel[t]
            xs = ii * step + off[0]; ys = jj * step + off[1]
            if span:
                x0, z0, x1, z1 = span
                if ax == 1: keep = (xs >= x0) & (xs < x1) & (ys >= z0) & (ys < z1)
                elif ax == 2: keep = (xs >= x0) & (xs < x1)
                else: keep = (xs >= z0) & (xs < z1)
            else: keep = np.ones(len(xs), bool)
            if not keep.any(): continue
            val = w0 * P[T, 0, ax] + w1 * P[T, 1, ax] + w2 * P[T, 2, ax]
            rows.append(np.stack([ii[keep].astype(float), jj[keep].astype(float), val[keep], np.full(keep.sum(), T, float)], 1))
        if not rows: continue
        R = np.concatenate(rows)
        key = R[:, 0] * 1e6 + R[:, 1]
        order = np.lexsort((R[:, 2], key))
        R, key = R[order], key[order]
        same = key[1:] == key[:-1]
        ta, tb = R[:-1, 3].astype(int), R[1:, 3].astype(int)
        gap = (R[1:, 2] - R[:-1, 2]) * np.minimum(np.abs(N[ta, ax]), np.abs(N[tb, ax]))
        facing = (N[ta] * N[tb]).sum(1) > 0.98
        hit = same & facing & (gap < limit - 0.01) & (ta != tb)
        for i in np.nonzero(hit)[0]:
            A_, B_ = ta[i], tb[i]
            sa, sb = srcs[Si[A_]], srcs[Si[B_]]
            ba, bb = sa.startswith(('res', 'door')), sb.startswith(('res', 'door'))
            if not ba and not bb: kind = 'terrain'
            elif ba != bb: kind = 'terrain/building'
            elif sa == sb: kind = 'model'
            elif sa.split('@')[-1] == sb.split('@')[-1] or any(x.split('#')[0][3:].isdigit() and
                                                              int(x.split('#')[0][3:]) in DOOR_RES for x in (sa, sb)):
                kind = 'model/door'      # (a model and its door, or a door model placed by itself: a second door)
            else: kind = 'buildings'
            if kind in ('model', 'model/door') and gap[i] >= 0.99: continue     # Black 2's own models: >= 1
            ma, mb_ = sorted([mats[Mi[A_]], mats[Mi[B_]]])
            f = found.setdefault((ma, mb_, kind), [0, 99.0, [], set()])
            f[0] += 1; f[1] = min(f[1], gap[i])
            pos = [0, 0, 0]; pos[a] = R[i, 0] * step + off[0]; pos[b] = R[i, 1] * step + off[1]; pos[ax] = R[i, 2]
            if len(f[2]) < 400: f[2].append(tuple(round(p, 1) for p in pos))
            f[3].update({sa, sb})
    return found

def check_layer(frame, out):
    """Same-facing overlapping surfaces closer than 2 units over each checked cell (with the buildings of the cells
    around it reaching in); a model's own pieces and its door model only below 1 (Black 2's own models keep >= 1)."""
    found = {}
    near = near_walk(frame)
    DOOR_RES.clear(); DOOR_RES.update(r['door'] for r in registry(frame).values() if r.get('door') not in (None, 0xFFFF))
    for c in tile_cells(frame):
        x0, z0 = c[0] * 512, c[1] * 512
        parts = frame.terrain(c)
        for c2 in frame.cells:
            if abs(c2[0] - c[0]) > 1 or abs(c2[1] - c[1]) > 1: continue
            for res, X, Y, Z, rot in frame.placements(c2):
                if x0 - 200 < X < x0 + 712 and z0 - 200 < Z < z0 + 712:
                    parts += [q[:5] + (q[5] + f'#{X:.0f},{Z:.0f}',) for q in placed_parts(frame, res, X, Y, Z, rot)]
        layer_pairs(parts, found, 2.0, (x0, z0, x0 + 512, z0 + 512))
    for (ma, mb_, kind), (n, gap, pos, srcs) in sorted(found.items(), key=lambda kv: -kv[1][0]):
        pos = [p for p in pos if (int(p[0]) // 16, int(p[2]) // 16) in near]
        if not pos: continue
        bsrc = sorted(x for x in srcs if x.startswith(('res', 'door')))
        tiles = sorted({(int(p[0]) // 16, int(p[2]) // 16) for p in pos})
        out.append(('layer', f'{kind}: {ma} / {mb_}: min gap {gap:.2f}, {len(pos)} samples, tiles {tiles[:6]}'
                             + (f' [{", ".join(bsrc[:3])}]' if bsrc else ''), tiles[0]))

def _raster_view(parts, box, scale, pitch, yaw, height=None):
    """Camera-angle orthographic raster of parts (world units) over box (x0, z0, x1, z1), the view turned by yaw
    degrees about y: per pixel the nearest surface of any facing (depth, triangle, back face?) and the nearest front
    face (depth). Alpha-tested texels (alpha <= 100) let the view through, translucent materials are skipped."""
    x0, z0, x1, z1 = box
    p, q = math.radians(pitch), math.radians(yaw)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    def view(P):
        X, Z = P[..., 0] - cx, P[..., 2] - cz
        xr = X * math.cos(q) - Z * math.sin(q); zr = X * math.sin(q) + Z * math.cos(q)
        sy = -P[..., 1] * math.cos(p) + zr * math.sin(p)
        dep = -P[..., 1] * math.sin(p) - zr * math.cos(p)
        return xr, sy, dep
    hw, hz = (x1 - x0) / 2, (z1 - z0) / 2
    Y0, Y1 = -hz * math.sin(p) - 160 * math.cos(p), hz * math.sin(p) + 40 * math.cos(p)
    W, H = int(2 * hw * scale), int((Y1 - Y0) * scale)
    dany = np.full((H, W), np.inf); tany = np.full((H, W), -1, int); back = np.zeros((H, W), bool)
    dfront = np.full((H, W), np.inf)
    fwd = np.array([math.sin(q) * math.cos(p) * 0, -math.sin(p), -math.cos(p)])   # (view space: looking north, down)
    tris = []
    for pi, (n, tp, P, UV, A, src) in enumerate(parts):
        if not (A >= 0.99).all(): continue
        T = ec._tex(tp)
        xs, ys, dep = view(P)
        Pv = np.stack([xs, P[..., 1], (P[..., 0] - cx) * math.sin(q) + (P[..., 2] - cz) * math.cos(q)], -1)
        N = np.cross(Pv[:, 1] - Pv[:, 0], Pv[:, 2] - Pv[:, 0])
        towards = N[:, 1] * math.sin(p) + N[:, 2] * math.cos(p)
        for t in range(len(P)):
            if abs(towards[t]) < 1e-6 * max(1.0, np.linalg.norm(N[t])): continue     # edge-on
            sx, sy = (xs[t] + hw) * scale, (ys[t] - Y0) * scale
            i0, i1 = max(0, math.floor(sx.min())), min(W - 1, math.ceil(sx.max()))
            j0, j1 = max(0, math.floor(sy.min())), min(H - 1, math.ceil(sy.max()))
            if i1 < i0 or j1 < j0: continue
            ii, jj = np.meshgrid(np.arange(i0, i1 + 1) + 0.5, np.arange(j0, j1 + 1) + 0.5)
            (ax, bx, cx_), (ay, by, cy) = sx, sy
            den = (by - cy) * (ax - cx_) + (cx_ - bx) * (ay - cy)
            if abs(den) < 1e-9: continue
            w0 = ((by - cy) * (ii - cx_) + (cx_ - bx) * (jj - cy)) / den
            w1 = ((cy - ay) * (ii - cx_) + (ax - cx_) * (jj - cy)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
            if not m.any(): continue
            if T is not None:
                u = w0 * UV[t, 0, 0] + w1 * UV[t, 1, 0] + w2 * UV[t, 2, 0]
                v = w0 * UV[t, 0, 1] + w1 * UV[t, 1, 1] + w2 * UV[t, 2, 1]
                th, tw = T.shape[:2]
                m &= T[np.floor((1 - v) * th).astype(int) % th, np.floor(u * tw).astype(int) % tw][..., 3] > 100
                if not m.any(): continue
            d = w0 * dep[t, 0] + w1 * dep[t, 1] + w2 * dep[t, 2]
            k = len(tris); tris.append((pi, t))
            sub = dany[j0:j1 + 1, i0:i1 + 1]
            hit = m & (d < sub - 0.05)
            sub[hit] = d[hit]; tany[j0:j1 + 1, i0:i1 + 1][hit] = k
            back[j0:j1 + 1, i0:i1 + 1][hit] = towards[t] < 0
            if towards[t] > 0:
                subf = dfront[j0:j1 + 1, i0:i1 + 1]; hf = m & (d < subf); subf[hf] = d[hf]
    # world point of each pixel on the nearest surface (or y = 0 for empty pixels)
    jj, ii = np.mgrid[0:H, 0:W]
    sxw = (ii + 0.5) / scale - hw; syw = (jj + 0.5) / scale + Y0
    d = np.where(np.isfinite(dany), dany, np.nan)
    y = np.where(np.isfinite(d), -sxw * 0 - (syw * math.cos(p) + d * math.sin(p)), 0.0)
    zr = np.where(np.isfinite(d), syw * math.sin(p) - d * math.cos(p), syw / math.sin(p))
    wx = sxw * math.cos(q) + zr * math.sin(q) + cx
    wz = -sxw * math.sin(q) + zr * math.cos(q) + cz
    if height is not None:            # empty pixels: where the ray meets the collision heights (not y 0)
        e = ~np.isfinite(dany)
        yy = np.zeros(e.sum())
        for _ in range(4):
            zr_ = (syw[e] + yy * math.cos(p)) / math.sin(p)
            wx_ = sxw[e] * math.cos(q) + zr_ * math.sin(q) + cx; wz_ = -sxw[e] * math.sin(q) + zr_ * math.cos(q) + cz
            yy = np.array([height(int(a // 16), int(b // 16), y0) for a, b, y0 in zip(wx_, wz_, yy)])
        wx[e], wz[e] = wx_, wz_
    return dict(dany=dany, tany=tany, back=back, dfront=dfront, wx=wx, wz=wz, y=y, tris=tris)

def check_view(frame, out, yaws=(-20, 0, 20), scale=0.5):
    """cull + hole: per 2x2 block of checked cells, a camera-angle raster of the block and the cells around it."""
    near = near_walk(frame)
    def hgt(tx, tz, last):
        y = frame.y(tx, tz) if (tx // 32, tz // 32) in frame.cells else None
        return last if y is None else y
    blocks = sorted({(c[0] // 2, c[1] // 2) for c in tile_cells(frame)})
    cull, hole = defaultdict(lambda: [0, set(), set()]), defaultdict(lambda: [0, set()])
    for bx, bz in blocks:
        cells = [(bx * 2 + dx, bz * 2 + dz) for dx in range(-1, 3) for dz in range(-1, 4)]
        parts = frame.parts([c for c in cells if c in frame.cells])
        for i, q in enumerate(parts): parts[i] = q[:5] + (q[5],)
        box = (bx * 1024, bz * 1024, bx * 1024 + 1024, bz * 1024 + 1024)
        for yaw in yaws:
            R = _raster_view(parts, (box[0] - 64, box[1], box[2] + 64, box[3]), scale, ec.CAM_PITCH, yaw, hgt)
            tx = np.floor(R['wx'] / 16).astype(int); tz = np.floor(R['wz'] / 16).astype(int)
            mine = np.zeros(tx.shape, bool)
            for c in tile_cells(frame):
                if c[0] // 2 == bx and c[1] // 2 == bz: mine |= (tx // 32 == c[0]) & (tz // 32 == c[1])
            visible = mine & np.array([[(a, b) in near for a, b in zip(ra, rb)] for ra, rb in zip(tx, tz)])
            bad = visible & R['back']
            for j, i in zip(*np.nonzero(bad)):
                pi, t = R['tris'][R['tany'][j, i]]
                key = (parts[pi][0], parts[pi][5].split('#')[0])
                cull[key][0] += 1; cull[key][1].add((tx[j, i], tz[j, i])); cull[key][2].add(yaw)
            empty = visible & ~np.isfinite(R['dfront'])
            for j, i in zip(*np.nonzero(empty)):
                hole[(tx[j, i] // 32, tz[j, i] // 32)][0] += 1; hole[(tx[j, i] // 32, tz[j, i] // 32)][1].add((tx[j, i], tz[j, i]))
    for (mat, src), (n, tiles, yw) in sorted(cull.items(), key=lambda kv: -kv[1][0]):
        tiles = sorted(tiles)
        out.append(('cull', f'{mat} ({src}): back faces seen on {n} pixels (yaw {sorted(yw)}), tiles {tiles[:6]}', tiles[0]))
    for c, (n, tiles) in sorted(hole.items()):
        tiles = sorted(tiles)
        out.append(('hole', f'cell {c}: nothing drawn on {n} pixels, tiles {tiles[:8]}', tiles[0]))

# ----------------------------------------------------------------------------------------------------------- ent
ROM_FILES = None
def check_ent(frame, out):
    """(--rom FILES_DIR or ROM.nds) The zones' people/items/triggers/signs as the ROM has them (a/1/2/6: world.json's,
    the generated content, trainers, story objects): a person or item on a tile Black 2 does not let you stand on, or on
    another zone's tile (the game spawns a zone's people only while you are in it)."""
    if not ROM_FILES: return
    import narcio, zoneheaders
    from zones import parse_entities
    headers, _ = zoneheaders.load(ROM_FILES)
    ents = narcio.load(ROM_FILES, 126)
    W = frame.world
    if frame.group is None:
        owner = {(c['cx'], c['cz']): c['zone'] for c in W['cells']}; rects = W.get('zone_rects', [])
    else:
        owner = {(c['cx'], c['cz']): c['zone'] for c in next(g for g in W['standalone'] if g['group'] == frame.group)['cells']}
        rects = []
    zone_at = lambda x, z: next((zz for x0, z0, x1, z1, zz in rects if x0 <= x <= x1 and z0 <= z <= z1), owner.get((x // 32, z // 32)))
    warps = _warp_tiles(frame)
    done = set()
    for zid, z in W['zones'].items():
        if (z.get('group') or None) != frame.group: continue
        e = headers[int(zid)]['entities']
        if e in done: continue
        done.add(e)
        ent, _ = parse_entities(ents[e])
        for n in ent['npcs']:
            t = (n['x'], n['z'])
            if not in_only(frame, *t): continue
            r = frame.rec(*t)
            where = f"zone {zid} person uid {n['uid']} (sprite {n['model']}, script {n['script']}) at {t}"
            if r is None: out.append(('ent', f'{where}: outside the built cells', t)); continue
            if not (b2_land(r) or b2_surf(r)):
                warp = ' (a Sapphire warp tile)' if t in warps else ''
                out.append(('ent', f'{where}: on a tile you cannot stand on (class {r[2]:#x} flags {r[3]:#x}){warp}', t))
            zz = zone_at(*t)
            if zz is not None and zz != int(zid):
                out.append(('ent', f'{where}: stands in zone {zz}\'s tiles (only spawned while you are in zone {zid})', t))

# ----------------------------------------------------------------------------------------------- by design
# Findings that are known and kept on purpose (frame regex, kind, message regex, why). They are counted apart
# ('accepted'); everything else is open.
ACCEPT = [
    ('main', 'walk', r'Route110 .*(fence|other:bridge_support|cliff), MB_(WARP_OR_BRIDGE|NORMAL|OCEAN_WATER)\)|Route110 .*surf water in '
     r'Sapphire \(MB_OCEAN_WATER\), not in Black 2|Route110 \(23,81\).*cut off',
     'the Cycling Road is one layer: its railings stand on the sea under it (Sapphire surfs under it; '
     'notes/TERRAIN_GROUND.md "Surfing under bridges")'),
    ('.*', 'walk', r'walkable in Sapphire \((building|sign), MB_NORMAL\), solid in Black 2',
     'a placed building model stands there (Gym fronts, the Battle Tower: Sapphire walks behind the 2D roof)'),
    ('.*', 'walk', r'1 tiles reachable in Sapphire are cut off.*MB_(ANIMATED|NON_ANIMATED)_DOOR',
     'a tile inside a building footprint behind its door (Sapphire draws it as roof)'),
    ('main', 'walk', r'FortreeCity \((33|34),14\) -> [ew]',
     "Fortree's tree-top walkway crosses over the path below it at (398-401, 74); one layer here, the crossing is the "
     "path's (16 under the west walkway, 32 under the east one, which its stairs reach)"),
    ('main', 'walk', r'FortreeCity \(18,10\).*cut off|MossdeepCity \(34,7\).*cut off|Route112 \(11,35\).*cave_entrance|'
     r'DewfordTown \(11,15\).*sign|Route120 \(13,17\).*ROUTE120_NORTH_BRIDGE',
     'single tiles Sapphire draws behind a Gym, a sign or a cave mouth (walk-behind tiles), and the tile of Route 120\'s '
     'event bridge (water until its script)'),
    ('SootopolisCity', 'walk', r'SootopolisCity \((44|45),10\)',
     "a one-tile nook at the foot of Sootopolis's crater rim (Sapphire elevation 0), 104 under the rim path"),
    ('.*', 'tex', r'^(gake1_[01]|gake1_1_y|out57_gake1_0|c8_gake1_w|michi01a|hashi02a|gake01a|out57_gake01a|c8_gake01w2|yamagake01): \d+ triangles '
     r'smeared', 'flat corner pieces of a lip / path fringe / deck lattice that sit on one texel row (the row that meets '
     'the ground, so they read as ground); faces: a few corner-fan slivers (yamagake01: the sea rocks heights.py 9d '
     'raises beside sandbars, walkability 2026-10-11)'),
    ('.*', 'tex', r'^(sea_zanami|mizutama01|hashi02a): \d+ triangles stretched',
     "water.py's foam-band corners and puddle centres take one texel on purpose (notes/TERRAIN_WATER.md); deck ends"),
    ('.*', 'layer', r'^buildings: h_kage\w* / h_kage\w*: ',
     "two Black 2 ground shadows (h_kage, flat under its own building and sign models) meeting where Sapphire puts "
     "buildings or signs side by side: the same dark texels on both"),
    ('BirthIsland_Exterior|NavelRock_Exterior', 'door|walk', r'(HARBOR|cut off|warp 0 at)',
     "the islands' harbour rooms are not built: their doors stay parked (a sailor stands in front) and the player arrives "
     "by the ferry's scripted landing (events agent: data/story/events.json, events_lib.inc)"),
    ('.*', 'layer', r'^terrain: ki04bx / ki04dx: ',
     "Black 2's own palm (Humilau chunk 300, terrain/palms.py): its crown fans ki04bx and ki04dx lie under 2 apart there too"),
    ('.*', 'cull', r'^nagakusa01b ',
     "Black 2's own long grass (Route 7 chunk 60, the recipe ground.py copies) has single-sided fringe blades facing "
     "away from the camera too (89 of its 312 nagakusa01b triangles)"),
    ('.*', 'ent', r'on a tile you cannot stand on .*\(a Sapphire warp tile\)',
     "story actors on a door or cave-mouth tile: the Regi caves' sealing rocks (sprite 206) on their mouths, people who "
     "step out of a door in a scene (the Winstrates, the rival at Lavaridge's Gym)"),
    ('main|SouthernIsland_Interior', 'ent', r'zone 317 person uid 1[01] |zone 112 person uid 102 ',
     "Route 101's rescue-scene actors on the ledge row (they run there in the opening, tested); Southern Island's "
     "Lati@s on its Sapphire spot (talked to, never walked past)"),
    ('main', 'door', r'SlateportCity warp 9|Route131 warp 0 |MAP_MAGMA_HIDEOUT_1F|LittlerootTown Sapphire warp [012] ',
     "Slateport's harbour warp lies outside its map; Route 131's Sky Pillar door exists in the post-game layout; "
     "Lilycove's Magma Hideout warp is Ruby's; Littleroot's houses use hand-made warp slots"),
    ('main', 'door', r'zone 326 Route103 warp 0 ',
     "Route 103's Altering Cave door (Emerald's, data/hoenn_map_additions.json) exists in the post-game layout (alt_Route103, "
     "map replace event 7); before, it stands on the cliff with the sea 8 below in front and never fires, as Route 131's"),
    ('alt_Route130', 'walk', r'Route130 \((3[5-9]|4[0-8]),2\) |Route130 \((30|53),6\) ',
     "Mirage Island's north rim (row 2, and two corners) made cliff faces (data/hoenn_world.json alt_layouts Route130 "
     "retile): Sapphire's flat top meets the sea there and Gen 3 would land a surfer on it; Black 2's island is a raised "
     "plateau (its south stairs climb one level a row), reached by the stairs, as Sapphire draws it"),
    ('.*', 'cull', r'^(ki0[234]ax\w*|saku01a|t2_saku01|nagakusa01[ab]) .*yaw \[(-20|20|-20, 20)\]\)',
     "Black 2's own single-sided uprights (tree crossing planes, fences: Route 6 chunks 53/55, Route 1/3 chunks 3/13) "
     "seen from the side of the screen; the round tree's and the palm's (ki04ax) cards are drawn from both sides in the game "
     "(nsbmd_fix.tree_materials), which this render does not know"),
    ('.*', 'cull', r'\(res(0|2|3|5|6|21|24|26|93|101|151|152|153|154|164|165|236|259|260|261)\)',
     "Black 2's own building/sign/door models (single-sided as in Unova)"),
    ('SkyPillar_Top|NavelRock_Top', 'hole', r'.', "the sky around the top of Sky Pillar / Navel Rock is drawn as nothing "
     "(world.py VOID, data/hoenn_standalone.json border 'void'); since 2026-10-08 Black 2's clouds fill it (res 483-487)"),
    ('.*', 'bld', r'(Route104 warp [4-7] .*PETALBURG_WOODS|Route112 warp [23] .*JAGGED_PASS|(Southern|Faraway)Island_\w+ warp [01] '
     r').*non-animated door',
     'open entrances (a path into the woods, Jagged Pass, the island forest): no building in Sapphire either (checked '
     'one by one against Sapphire by buildings_audit 2026-10-08; Sky Pillar top\'s doorway was a door in a wall: res 482)'),
    ('main', 'bld', r'^FortreeCity \((30-34,2-4|34-34,4-4|9-12,3-3|15-19,3-3|23-27,3-3|10-14,13-14|35-39,13-14)\): .*no model covers',
     "Fortree's tree houses (towns4 res 364/365) stand on the rows north of their door tiles: their door rows are the "
     "deck in front of the house, as every building's door row in front of its wall (checked in DeSmuME, "
     "screenshots/buildings_audit/). Since map_glitch_fix (2026-10-09) the houses stand at their door row's south edge as "
     "models_fortree.py meant; left: House 4's east platform tile (34,4), the walkway's end beside its rails"),
    ('main', 'bld', r'^Route108 \(27-32,3-5\): .*no model covers',
     "the Abandoned Ship: drawn into Route 108's terrain by terrain/ship.py, not a building model"),
    ('SkyPillar_Top', 'bld', r'^SkyPillar_Top \(0-26,19-23\): .*no model covers',
     "the tower's outer wall below the top floor: void tiles (world.py VOID, data/hoenn_standalone.json retile building "
     "-> void); the tower's face going down into Black 2's clouds is a model (standalone res 485/486)"),
]

# Emerald's world only (emerald_world 2026-10-12, notes/EMERALD.md "Emerald's world"): what its outdoor build leaves on
# purpose until the rooms, models and story of later phases exist
_EMERALD_ROOMS = (r'(?i:(terra_?cave|mirage_?tower|trainer_?hill|battle_?tent|battle_?frontier|artisan_?cave|'
                  r'mystery_?events_?house|magma_?hideout_1f_emerald))')
ACCEPT_EMERALD = [
    ('.*', 'door', _EMERALD_ROOMS + r'.*|.*(no door in its zone|leads nowhere \(unresolved) .*' + _EMERALD_ROOMS,
     "Emerald's new doors stay closed until their rooms are built (data/emerald/hoenn_interiors.json status todo): "
     "Battle Tents, Trainer Hill and the Frontier's facilities closed by decisions 1A/2, the Mystery Events House left "
     "out (decision 5), Terra Cave, Mirage Tower, Magma Hideout, Artisan Cave: rooms of phase 2 (notes/EMERALD.md work list)"),
    ('BattleTower_Outside', 'door', r'warp 9 at .*approach tile .* is solid',
     "the Battle Frontier's Reception Gate's north door (26,61) is entered walking south from the island; it stays closed "
     "with the gate (no room yet)"),
    ('main', 'walk', r'MossdeepCity \(6[1-6],[2-5]\) .*walkable in Sapphire \(water, MB_NORMAL\)',
     "Emerald's rocket gantries and rocket drawn over the sea north of the Space Center (collision 0 but MB_NORMAL: "
     "no surf water, Gen 3 lands nobody there); solid sea here until the Space Center's model has its rocket"),
    ('JaggedPass|alt_JaggedPass', 'walk', r'JaggedPass \(16,17\) ',
     "the Magma Hideout's mouth over its door (16,18): shut in the sealed layout; in the open one (alt_JaggedPass, "
     "emerald_polish_outdoor) pokeemerald's map.bin leaves the mouth's top tile passable (reached only by a step north "
     "off the door's own warp tile), while its OpenMagmaHideout script sets it impassable (setmetatile 16, 17, ..., "
     "TRUE): here it is the mouth's rock"),
]
import version as _version
if _version.EMERALD: ACCEPT += ACCEPT_EMERALD

def accepted(frame, kind, msg):
    import re
    return next((why for fr, k, rx, why in ACCEPT if re.match('(' + k + ')$', kind) and re.match('(' + fr + ')$', frame)
                 and re.search(rx, msg)), None)

# ------------------------------------------------------------------------------------------------------- driver
KINDS = ['place', 'size', 'walk', 'door', 'bld', 'zone', 'tex', 'layer', 'view']
CHECKS = {'place': check_place, 'size': check_size, 'walk': check_walk, 'door': check_door, 'bld': check_bld,
          'layer': check_layer, 'view': check_view, 'zone': check_zone, 'tex': check_tex, 'ent': check_ent}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('world', nargs='?')
    ap.add_argument('--kinds', default=','.join(KINDS))
    ap.add_argument('--frames', default='')
    ap.add_argument('--rom')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--all', action='store_true', help='also print the accepted (by design) findings')
    a = ap.parse_args()
    wd = wdir(a.world)
    want = a.kinds.split(',')
    global ROM_FILES
    if a.rom:
        ROM_FILES = a.rom if os.path.isdir(a.rom) else None
        if not ROM_FILES: sys.exit('--rom: give a build files directory (work/agents/X/rom/files)')
        if 'ent' not in want: want.append('ent')
    fs = [f for f in frames(wd) if not a.frames or f.name in a.frames.split(',')]
    total, acc = Counter(), Counter()
    for f in fs:
        out = []
        for k in want:
            if k in CHECKS: CHECKS[k](f, out)
        for kind, msg, where in out:
            import re
            msg = re.sub(r'np\.int64\((-?\d+)\)', r'\1', str(msg))
            why = accepted(f.name, kind, msg)
            if why: acc[kind] += 1
            else: total[(kind, f.name)] += 1
            if not a.summary and (not why or a.all): print(f'{f.name}: ({kind}) {msg}' + (f'  [accepted: {why}]' if why else ''))
    by_kind = Counter()
    for (kind, fname), n in total.items(): by_kind[kind] += n
    shown = [x for k in want for x in (('cull', 'hole') if k == 'view' else (k,))]
    print('summary (open):', ', '.join(f'{k} {by_kind.get(k, 0)}' for k in shown), '| accepted (by design):',
          ', '.join(f'{k} {acc[k]}' for k in shown if acc[k]) or 'none', '| open by frame:',
          ', '.join(f'{fn}:{k}={n}' for (k, fn), n in sorted(total.items())))

if __name__ == '__main__':
    main()
