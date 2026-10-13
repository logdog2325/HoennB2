"""Cave builder: a Sapphire cave map (pokeruby) rebuilt as Black 2 cave chunks, the way Black 2 builds its own caves
(notes/CAVES.md). Writes the same outputs as models_interior.py, so b2tools/patches/interiors.py installs a cave like
any room (data/interiors/<zone>.json "room": <Map>, written by converter/gen_caves.py).

    python3 models_cave.py [MAP ...]          (default: every data/cave_layouts/<Map>.json)
    -> $HOENN_INTERIORS_DIR/<Map>/ (default work/interiors/<Map>/): terrain.dae (+ texture PNGs), palettes.txt,
       collision.per, placements.bin, room.json; caves bigger than one chunk also terrain_c<k>.dae/.nsbmd,
       collision_c<k>.per, placements_c<k>.bin and terrain_all.dae (as models_interior.py's big rooms)

What is copied from Black 2 (chunks of area 332: Wellspring Cave 486-491, Seaside Cave 630-632, Victory Road 788;
area 388: Reversal Mountain 719-741; numbers from tracing their triangles, notes/CAVES.md):
- floor: one texture, 4 tiles per repeat (d0yuka_001), vertex colour 1.0;
- rock: every non-walkable tile is rock that rises from the walkable floor in TIERS of 16 units. Each tier is a sloped
  face one tile deep with Black 2's profile (height 0 / 4 / 14 / 16 at 0 / 6 / 10 / 16 units from the floor edge:
  bottom band d0gake_001 (on floor) or d0gake_001b (on a rock top), v 0..0.44; middle band d0gake_001b, v 0.44..1; lip
  d0gake_002b (top is rock) or d0gake_002 (top is walkable floor), v 0..1; 32 units per u repeat; vertex colour 0.77 at
  the bottom and top edges, 1.0 inside), then a 16-unit flat rock top (d0yuka_002, colour 0.77), then the next tier.
  Black 2's outer walls have 2 tiers (32 high) in every direction (also the south side, facing away from the camera);
  past the last lip a 16-unit rim (d0gake_heri, v 0..1, colour 1) and black beyond (the same texture, colour 0).
  The rock surface is the lower envelope of every walkable tile's profile cone (Chebyshev distance), sampled on a
  lattice at 0/6/10/16 units inside each tile: straight walls come out exactly as Black 2's, outer corners get a
  diagonal crease, narrow rock bands a ridge, and floors at different heights a cliff with a floor lip;
- ledges (Sapphire MB_JUMP_*): Black 2's low ridge d0dan_001 (Wellspring chunk 486 row 7): steep side (8->6 units,
  0->4 high, v 0..0.62) toward the landing, gentle side 8 units down to 2 units into the take-off tile (v 0.62..1);
  collision classes 0x72-0x75 (flags 1), both sides the same height, as Black 2's cave ledges;
- exits (Sapphire's arrow warps / doors): Black 2's cave arch, copied triangle for triangle from Victory Road chunk
  788 (d0ana_001 frame + d0ana_002 tunnel, the bright 001b/002b versions when the warp leads outdoors), standing on
  the warp tile, which is solid and carries a type-4 warp walked into (Black 2's own cave exits: 788 warp (13,30)
  type 4 dir 1; Wellspring 324 warp 0 type 4);
- rocks: free-standing Sapphire boulders (tileset table data/cave_tiles.json) become Black 2's own building models
  drock02 (1x1) / drock01 (2x2) from the area's pack (as Black 2 scatters them, max 32 models per chunk);
- ladders: Black 2 caves have no ladders (only 3x3-tile stair models, too big for Sapphire's 1-tile ladders): a down
  ladder is a 1-tile pit with Black 2's terrain stairs (d0kaidan_01, 45 degrees, 32 units per u, 8 per v, as
  Wellspring's), an up ladder the same stairs climbing into a 1-tile notch of the rock face; the tile keeps
  Sapphire's walkability and a step trigger warps (converter/gen_caves.py; Lavaridge's tested pattern);
- cracked floors: the look's rubble decal (d29_gake3) over them, falls by step trigger (gen_caves.py);
- levels (recipe "levels"): stair runs become slope tiles (heights.py plane records), steps between floors get rock
  faces, walkable neighbours Sapphire keeps apart side walls;
- water (Sapphire's surfable behaviours): Wellspring's cave water (d0_miz/d0_miz2/d0mizu_gake, class 0x3f at -8);
- Reversal Mountain (look in81): its own wall textures, arches per wall (chunks 723/738/740), rocks drawn as terrain.

Recipe data/cave_layouts/<Map>.json (every key optional except "map"):
  map        pokeruby map
  look       a look in data/cave_layouts/_looks.json (default: by the map's secondary tileset)
  look_over  {key: value} over the look's keys (e.g. Ruby's lava pools: water/water_top/water_bank textures from
             another set through "tex_sets", "water_top_size" units per repeat of the top layer, default 16)
  origin     zone tile of Sapphire tile (0, 0) (default [0, 0]: zone tile = Sapphire tile)
  matrix     [w, h] chunks (default: as many as the map needs)
  tiers      rock tiers (default: the look's, 2)
  levels     {"<elevation>": height in units} for walkable tiles (default: every walkable tile at 0); elevation 0/15
             tiles take the level of a walkable neighbour
  tiles      {"x,y": kind} overrides the classification: floor, rock, boulder, ledge_e/w/n/s, ramp_n/s/e/w
  ladders    {"x,y": "up"|"down"} (default: data/cave_tiles.json, else the destination's floor number)
  decals     false: no floor/rock-top decals
  boulder_models  false: boulders stay rock (no drock models)
The classification of each Sapphire tile (walkable/blocked, behaviour, metatile) is in Cave.classify; the recipe and
the per-tileset table only correct what Sapphire's data can't say (which blocked metatiles are loose boulders).
"""
import os, sys, json, struct, math, subprocess, hashlib
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import b2files, nsbtx                                        # noqa: E402
import models_cave_levels as LEVELS                          # noqa: E402  (heights, stairs, bridges, waterfalls)
import models_cave_misc as MISC                              # noqa: E402  (shallow water, ice: caves_misc)
import models_cave_uw as UW                                  # noqa: E402  (underwater maps: dive agent)
import models_cave_mist as MIST                              # noqa: E402  (mist caves: underwater_polish)
from dae import Model                                         # noqa: E402

FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
LAYOUTS = os.path.join(ROOT, 'data', 'cave_layouts')
TILES = os.path.join(ROOT, 'data', 'cave_tiles.json')
OUT = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
APICULA = os.path.join(ROOT, 'tools', 'apicula', 'bin', 'apicula')
T = 16                                   # units per tile
LAT = (0, 6, 10)                         # lattice lines inside a tile = Black 2's wall profile breakpoints
EDGE, MID = 0.77, 1.0                    # Black 2's vertex colours at a tier's bottom/top edge and inside
JUMP = {0x38: 'e', 0x39: 'w', 0x3A: 'n', 0x3B: 's'}             # Sapphire MB_JUMP_EAST/WEST/NORTH/SOUTH
LEDGE_CLASS = {'e': 0x72, 'w': 0x73, 'n': 0x74, 's': 0x75}      # Black 2 ledge cells (ov036 MapTile_IsLedgeR/L/U/D)
DIRWALL = {0x30: 'e', 0x31: 'w', 0x32: 'n', 0x33: 's', 0x34: 'ne', 0x35: 'nw', 0x36: 'se', 0x37: 'sw'}
WALL_CLASS = {'e': 0x51, 'w': 0x52, 'n': 0x53, 's': 0x54, 'ne': 0x55, 'nw': 0x56, 'se': 0x57, 'sw': 0x58}
ARROW = {0x65: 's', 0x64: 'n', 0x62: 'e', 0x63: 'w'}             # Sapphire arrow warps: the way out
ARROW[0x1C] = 's'      # MB_SHOAL_CAVE_ENTRANCE: a south arrow warp in shallow water (MetatileBehavior_IsSouthArrowWarp)
ARROW[0x6D] = 's'      # MB_WATER_SOUTH_ARROW_WARP (Scorched Slab, caves_east): surfing south into the cave mouth
WARP_DIR = {'s': 1, 'n': 2, 'e': 3, 'w': 4}                      # Black 2 warp direction (ov012 CheckWarpDirectionMatch)
STEP = {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}
ENCOUNTER_BEH = {0x02, 0x03, 0x08, 0x0B, 0x24}                  # Gen 3 tiles with the encounter attribute
MB_LADDER, MB_DOOR, MB_CRACKED, MB_HOLE, MB_SLOPE = 0x61, 0x60, 0xD2, 0x66, 0xD0
# Gen 3 surfable behaviours (pokeruby sTileBitAttributes bit 1) and which of them have wild encounters (bit 0)
SURF = {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x19, 0x22, 0x2A, 0x50, 0x51, 0x52, 0x53, 0x6C, 0x6D, 0x6F}
SURF_ENC = {0x10, 0x11, 0x12, 0x15, 0x22, 0x2A}
MB_WATERFALL = 0x13

def load_json(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else default

# ------------------------------------------------------------------------------------------------ Sapphire data
_maps = {}
def sapphire(name, layout=None):
    """Grids of a pokeruby map: walk, beh, elev, mt (metatile id, secondary + 0x200), plus its events and header.
    layout: another pokeruby layout for the grids (recipe "layout": Shoal Cave's high tide, caves_misc); events stay
    the map's."""
    key = (name, layout) if layout else name
    if key not in _maps:
        from gba import Repo, MetatileRenderer
        # "<decomp>/<Folder>": another decomp's map (an Emerald room variant's room.json "map", models_interior.map_source;
        # emerald_rooms 2026-10-12); plain names are pokeruby's as before
        dec, folder = name.split('/', 1) if '/' in name else ('pokeruby', name)
        # "emerald/<Map>" (emerald_caves 2026-10-12): Emerald's map as Emerald's world reads it (converter/gba.py Repo(...,
        # emerald=True): HoennB2 names and MAP_ ids, so warps name HoennB2's maps; layouts are pokeemerald's)
        repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'), emerald=True) if dec == 'emerald' else \
            Repo(os.path.join(ROOT, 'external', dec))
        mj = repo.map_json(folder)
        g, l = repo.layout_grid(layout or mj['layout'])
        mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
        H, W = g.shape
        v = [[int(g[z, x]) for x in range(W)] for z in range(H)]
        _maps[key] = dict(name=name, w=W, h=H, json=mj, tilesets=[l['primary_tileset'], l['secondary_tileset']],
                           walk=[[(c >> 10) & 3 == 0 for c in row] for row in v],
                           elev=[[c >> 12 for c in row] for row in v],
                           mt=[[c & 0x3FF for c in row] for row in v],
                           beh=[[mr.behavior(c & 0x3FF) for c in row] for row in v],
                           warps=mj.get('warp_events') or [], objects=mj.get('object_events') or [],
                           bgs=mj.get('bg_events') or [], coords=mj.get('coord_events') or [])
    return _maps[key]

_EM = {}
def emerald_dest_name(dest_id):
    """HoennB2 name of a MAP_ id of Emerald's world (an "emerald/<Map>" cave's warps; emerald_caves 2026-10-12)."""
    if 'names' not in _EM:
        from gba import Repo, map_folders
        v = Repo(os.path.join(ROOT, 'external', 'pokeruby'), emerald=True)
        _EM['repo'] = v
        _EM['names'] = {v.hoenn_id(eid): v.hoenn_name(f) for eid, f in map_folders(v.root).items()}
        for k, f in map_folders(os.path.join(ROOT, 'external', 'pokeruby')).items(): _EM['names'].setdefault(k, f)
    return _EM['names'].get(dest_id, dest_id)

def emerald_dest_outside(name):
    """An arch of an "emerald/<Map>" cave leads outdoors: the destination's map type in Emerald's world (MAP_DYNAMIC, a
    return to where you came from: Terra Cave's mouth, outdoors)."""
    if name == 'MAP_DYNAMIC': return True
    emerald_dest_name('MAP_NONE')
    try: mt = _EM['repo'].map_json(name)['map_type']
    except (FileNotFoundError, KeyError): mt = ''
    return mt not in ('MAP_TYPE_UNDERGROUND', 'MAP_TYPE_INDOOR', 'MAP_TYPE_SECRET_BASE', 'MAP_TYPE_UNDERWATER')

def floor_number(name):
    """1F -> 1, B1F -> -1, 2F -> 2 ... from a map name (None if it has no floor)."""
    import re
    m = re.search(r'_(B?)(\d+)F', name)
    return None if not m else (-int(m.group(2)) if m.group(1) else int(m.group(2)))

# ------------------------------------------------------------------------------------------------ Black 2 data
_tex = {}
def set_images(ts):
    if ts not in _tex: _tex[ts] = {n: img for n, img, _ in nsbtx.decode(b2files.map_textures(FILES, ts))}
    return _tex[ts]

_models = {}
def pack_models(pack):
    """{name: (res, bmd)} of an interior building pack."""
    if pack not in _models:
        _models[pack] = {r['name']: (r['res_id'], r['bmd']) for r in b2files.building_pack(FILES, pack, exterior=False)}
    return _models[pack]

_templates = {}
def template(spec, cache_root):
    """Triangles of a Black 2 chunk (converted once with apicula, cached in <cache_root>/_cave_templates) whose
    material is in spec['materials'] and whose centre lies in spec['box'] (x0, x1, z0, z1, chunk-corner units),
    moved so spec['anchor'] (x, z) is the origin: [(material, [(x, y, z, u, v, (r, g, b)) x3])]."""
    key = json.dumps(spec, sort_keys=True)
    if key in _templates: return _templates[key]
    sys.path.insert(0, HERE)
    import preview_interior as pv
    d = os.path.join(cache_root, '_cave_templates', f'{spec["chunk"]}_{spec["set"]}')
    if not os.path.isdir(os.path.join(d, 'dae')):
        os.makedirs(d, exist_ok=True)
        _, secs = b2files.chunk(FILES, spec['chunk'])
        open(os.path.join(d, 'm.nsbmd'), 'wb').write(secs[0])
        open(os.path.join(d, 't.nsbtx'), 'wb').write(b2files.map_textures(FILES, spec['set']))
        subprocess.run([APICULA, 'convert', os.path.join(d, 'm.nsbmd'), os.path.join(d, 't.nsbtx'), '-o',
                        os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True, check=True)
    dae = next(os.path.join(d, 'dae', f) for f in os.listdir(os.path.join(d, 'dae')) if f.endswith('.dae'))
    x0, x1, z0, z1 = spec['box']; ax, az = spec['anchor']
    out = []
    for tp, P, UV, C in pv.parse(dae):
        mat = os.path.basename(tp)[:-4] if tp else None
        if mat not in spec['materials']: continue
        for t in range(len(P)):
            cx, cz = P[t][:, 0].mean() + 256, P[t][:, 2].mean() + 256
            if not (x0 <= cx <= x1 and z0 <= cz <= z1): continue
            # apicula's glTF/DAE v is 1 - ours (notes/TERRAIN_WATER.md); its DAE keeps the game's v (checked on floors)
            out.append((mat, [(P[t][k][0] + 256 - ax, P[t][k][1], P[t][k][2] + 256 - az, UV[t][k][0], UV[t][k][1],
                               tuple(float(c) for c in C[t][k][:3])) for k in range(3)]))
    _templates[key] = out
    return out

# ------------------------------------------------------------------------------------------------ profile
def face_y(r):
    """Height of Black 2's wall profile r units (0..16) from the floor edge."""
    return 4 * r / 6 if r <= 6 else 4 + 10 * (r - 6) / 4 if r <= 10 else 14 + 2 * (r - 10) / 6

def prof(d, tiers):
    """Height above its floor of a rock point d units (Chebyshev) from a walkable tile: tiers of a 16-unit face and
    a 16-unit flat top, capped after the last face."""
    import numpy as np
    k = np.floor(d / 32.0); r = d - 32 * k
    face = np.where(r <= 6, 4 * r / 6, np.where(r <= 10, 4 + 10 * (r - 6) / 4, 14 + 2 * (r - 10) / 6))
    h = 16 * k + np.where(r < 16, face, 16.0)
    return np.where(k >= tiers, 16.0 * tiers, h)

def slope_len(r):
    """Length along Black 2's wall profile (face_y) from the foot to profile position r (0..16)."""
    r = min(16.0, max(0.0, r))
    return (min(r, 6) * math.hypot(1, 4 / 6) + max(0.0, min(r, 10) - 6) * math.hypot(1, 10 / 4) +
            max(0.0, r - 10) * math.hypot(1, 2 / 6))
SLOPE_TIER = slope_len(16)

def shade(r, edge=EDGE):
    """Vertex colour at profile position r (0..16) of a tier: the look's edge colour (0.77 Wellspring, 0.74 Reversal
    Mountain) at the edges, 1.0 inside (Black 2's)."""
    if r <= 6: return edge + (MID - edge) * r / 6
    if r <= 10: return MID
    return MID + (edge - MID) * min(r - 10, 6) / 6

def band_v(band, r):
    if band == 'A': return 0.44 * r / 6
    if band == 'B': return 0.44 + 0.56 * (r - 6) / 4
    return (r - 10) / 6

# ------------------------------------------------------------------------------------------------ the cave
class Cave:
    def __init__(self, name, recipe=None):
        self.name = name
        self.r = r = recipe if recipe is not None else load_json(os.path.join(LAYOUTS, name + '.json'), {'map': name})
        self.sm = sm = sapphire(r.get('map', name), r.get('layout'))
        looks = load_json(os.path.join(LAYOUTS, '_looks.json'))
        look = r.get('look') or looks['_by_tileset'].get(sm['tilesets'][1], 'd0')
        self.look_name, self.look = look, looks[look]
        if r.get('look_over'):             # recipe keys over the look's (ruby_maps: Ruby's lava pools, notes/RUBY.md)
            self.look = dict(self.look, **r['look_over'])
        self.tiers = r.get('tiers', self.look.get('tiers', 2))
        self.emerald = sm['name'].startswith('emerald/')     # (emerald_caves: Emerald's view, its own tileset table)
        self.table = (load_json(TILES, {}) or {}).get(('emerald_view:' if self.emerald else '') + sm['tilesets'][1], {})
        self.W, self.H = sm['w'], sm['h']
        self.ox, self.oz = r.get('origin', [0, 0])
        self.mw, self.mh = r.get('matrix', [max(1, (self.ox + self.W + 31) // 32), max(1, (self.oz + self.H + 31) // 32)])
        self.NXT, self.NZT = 32 * self.mw, 32 * self.mh
        self.notes = []
        self.classify()

    # ---- Sapphire tile -> kind ---------------------------------------------------------------------------------
    def ids(self, key):
        return {int(str(v), 0) for v in self.table.get(key, [])}

    def classify(self):
        """kind per Sapphire tile: floor, rock, boulder, ledge, arch (solid exit tile with Black 2's cave arch),
        pit (ladder down), plus 'special' on walkable tiles: ladder_up/ladder_down, exit, cracked, slope."""
        sm, W, H = self.sm, self.W, self.H
        walk, beh, mt = sm['walk'], sm['beh'], sm['mt']
        inside = lambda x, z: 0 <= x < W and 0 <= z < H
        kind = [['floor' if walk[z][x] else 'rock' for x in range(W)] for z in range(H)]
        special, ledge_dir, wall_dirs = {}, {}, {}
        boulders = self.ids('boulder')
        over = {tuple(map(int, k.split(','))): v for k, v in self.r.get('tiles', {}).items()}
        for z in range(H):
            for x in range(W):
                b = beh[z][x]
                if (x, z) in over:
                    k = over[(x, z)]
                    if k.startswith('ledge_'): kind[z][x] = 'ledge'; ledge_dir[(x, z)] = k[-1]
                    elif k.startswith('ramp_'): kind[z][x] = 'floor'; self.ramp_over = getattr(self, 'ramp_over', {}); self.ramp_over[(x, z)] = k[-1]
                    else: kind[z][x] = k
                    continue
                if not walk[z][x] and b in JUMP:
                    d = JUMP[b]; dx, dz = STEP[d]
                    # a real ledge: you can stand behind it and land beyond it (Sapphire's jumps ignore the ledge
                    # tile's own collision bit); otherwise it is only rock drawn like a ledge (Rusturf's outcrops)
                    if inside(x - dx, z - dz) and walk[z - dz][x - dx] and inside(x + dx, z + dz) and walk[z + dz][x + dx]:
                        kind[z][x] = 'ledge'; ledge_dir[(x, z)] = d
                elif not walk[z][x] and mt[z][x] in boulders and self.r.get('boulder_models', True):
                    if any(inside(x + a, z + c) and walk[z + c][x + a] for a, c in STEP.values()):
                        kind[z][x] = 'boulder'
                if walk[z][x] and b in SURF and (x, z) not in over:
                    kind[z][x] = 'water'                 # surf water (Gen 3 collision 0, elevation 1)
                elif walk[z][x]:
                    if b == MB_LADDER: special[(x, z)] = 'ladder'
                    elif b in ARROW: special[(x, z)] = 'exit'
                    elif b == MB_CRACKED: special[(x, z)] = 'cracked'
                    elif b == MB_HOLE: special[(x, z)] = 'hole'
                    elif b == MB_SLOPE: special[(x, z)] = 'slope'
                    elif b in DIRWALL: wall_dirs[(x, z)] = DIRWALL[b]
        # muddy slopes (MB_MUDDY_SLOPE, Granite Cave B1F): you slide down them and can't climb them without the Mach
        # Bike, so the top tile of each run becomes a south ledge (jumped over from above, a wall from below)
        for (x, z), s in list(special.items()):
            if s == 'slope' and special.get((x, z - 1)) != 'slope':
                kind[z][x] = 'ledge'; ledge_dir[(x, z)] = 's'
        self.kind, self.special, self.ledge_dir, self.wall_dirs = kind, special, ledge_dir, wall_dirs
        # warps: each Sapphire warp event -> a Black 2 warp spot (zone tile + type/dir) and what the tiles look like
        ladders = {tuple(map(int, k.split(','))): v for k, v in self.r.get('ladders', {}).items()}
        up_ids, down_ids = self.ids('ladder_up'), self.ids('ladder_down')
        self.spots, self.arches, self.ladders = [], [], {}
        for i, w in enumerate(sm['warps']):
            x, z = w['x'], w['y']
            dest = w['dest_map']
            if not inside(x, z):
                self.spots.append(dict(index=i, kind='outside', tiles=[[x, z]], x=self.ox + x, z=self.oz + z, type=2, dir=0, w=1, h=1)); continue
            b = beh[z][x]
            if b == MB_LADDER and walk[z][x]:
                way = ladders.get((x, z))
                if way is None and mt[z][x] in up_ids: way = 'up'
                if way is None and mt[z][x] in down_ids: way = 'down'
                if way is None:
                    a, c = floor_number(sm['name']), floor_number(self.dest_name(dest))
                    way = 'up' if (a is not None and c is not None and c > a) else 'down'
                self.ladders[(x, z)] = way
                if way == 'down': kind[z][x] = 'pit'
                # arrival spot only (dir 0 matches no walking direction): the step trigger does the warp
                self.spots.append(dict(index=i, kind='ladder_' + way, tiles=[[x, z]], x=self.ox + x, z=self.oz + z,
                                       type=2, dir=0, w=1, h=1, step=True))
            elif b in ARROW:
                d = ARROW[b]; dx, dz = STEP[d]
                ax, az = x + dx, z + dz
                if inside(ax, az): kind[az][ax] = 'arch'
                self.arches.append(dict(x=ax, z=az, face=d, to_outside=self.dest_outside(dest)))
                self.spots.append(dict(index=i, kind='exit', tiles=[[x, z]], x=self.ox + ax, z=self.oz + az,
                                       type=4, dir=WARP_DIR[d], w=1, h=1))
            elif b == MB_DOOR:
                # a doorway in the back wall (Steven's room): the tile becomes the arch, walked into northwards
                kind[z][x] = 'arch'
                self.arches.append(dict(x=x, z=z, face='n', to_outside=self.dest_outside(dest)))
                self.spots.append(dict(index=i, kind='door', tiles=[[x, z]], x=self.ox + x, z=self.oz + z,
                                       type=4, dir=WARP_DIR['n'], w=1, h=1))
            else:   # any other warp tile: an arrival/step spot on the tile itself
                self.spots.append(dict(index=i, kind='tile', tiles=[[x, z]], x=self.ox + x, z=self.oz + z,
                                       type=2, dir=0 if walk[z][x] else 2, w=1, h=1))
        # links (recipe "links": [{"side": "s"/"n", "x": [x0, x1], "to": MAP}], final_check 2026-10-08): Sapphire's map
        # connections between two maps of this builder (Underwater3's south edge = Underwater4's north edge, "down"/"up")
        # as one type-4 warp as wide as the trench on the row past the map's edge (inside the matrix: the recipe's
        # origin leaves that row), walked into: a diver's warps fire on bumping a wall (FieldPlayerGrid_UpdateSurfBrake
        # -> CheckWarpAtHitWall, front tile), the arrival walks one step in, and a wide warp keeps the column
        # (ZoneWarp_CalcPosWeightBitsGrid / GetGridWarpOutPos, eventdata_system.c). converter/gen_caves.py appends them
        # after Sapphire's warps; no spot index (they are not Sapphire warp events).
        for k, ln in enumerate(self.r.get('links', [])):
            x0, x1 = ln['x']; side = ln['side']
            assert side in ('n', 's'), f'{self.name}: link side {side}'
            zz = -1 if side == 'n' else H
            assert 0 <= self.oz + zz < self.NZT, f'{self.name}: link row {zz} outside the matrix (recipe "origin")'
            self.spots.append(dict(index=None, kind='link', link=k, tiles=[[x, zz] for x in range(x0, x1 + 1)],
                                   x=self.ox + x0, z=self.oz + zz, type=4, dir=WARP_DIR[side], w=x1 - x0 + 1, h=1))
        # floor heights
        lv = {int(k): v for k, v in self.r.get('levels', {}).items()}
        self.fy = {}
        for z in range(H):
            for x in range(W):
                if kind[z][x] != 'rock' and kind[z][x] != 'arch':
                    e = sm['elev'][z][x]
                    self.fy[(x, z)] = lv.get(e, 0) if lv else 0
        if lv:              # transition elevations (0/15) take a neighbour's level
            for (x, z), y in list(self.fy.items()):
                if sm['elev'][z][x] in (0, 15):
                    n = [lv[sm['elev'][z + c][x + a]] for a, c in STEP.values() if inside(x + a, z + c)
                         and sm['elev'][z + c][x + a] in lv]
                    if n: self.fy[(x, z)] = max(n)
                    # a loose boulder (blocks, nobody stands on it) stands on the level most of its neighbours have, the
                    # lower at a tie: by the highest, an ice crystal in Shoal Cave's ice room stood on a 16-unit
                    # platform with open sides over the ice (sweep_caves)
                    if n and kind[z][x] == 'boulder':
                        from collections import Counter as _C
                        cnt = _C(n); top = max(cnt.values())
                        self.fy[(x, z)] = min(v for v, k_ in cnt.items() if k_ == top)
        self.water_levels()
        self.ramps = {}     # (x, z) -> (side it rises toward, height at its low edge, at its high edge)
        if LEVELS.active(self.r): LEVELS.levels(self)       # recipe heights/ramps/bridges/waterfalls (caves_east)
        self.find_ramps(lv)
        self.level_walls = self.find_level_walls()
        if MISC.active(self.r): MISC.classify(self)         # shallow water, ice (caves_misc)
        if UW.active(self.r): UW.classify(self)             # underwater maps (dive agent)

    def water_levels(self):
        """Surf water as Black 2's caves have it (Wellspring Cave 486/487: collision class 0x3f flags 0x16 at 8 below
        the floor, waterfall 0x40): every water tile takes the level of its nearest shore (a walkable non-water tile,
        breadth first, so pools at different levels each follow their own banks); self.wy = water collision height,
        self.fy = the shore level (what the rock rises from)."""
        from collections import deque
        W, H = self.W, self.H
        self.wy = {}
        water = {(x, z) for z in range(H) for x in range(W) if self.kind[z][x] == 'water'}
        if not water: return
        q = deque((t, self.fy[t]) for t in self.fy if self.kind[t[1]][t[0]] == 'floor')
        seen = {t for t, _ in q}
        while q:
            (x, z), y = q.popleft()
            for a, c in STEP.values():
                n = (x + a, z + c)
                if n in water and n not in seen:
                    seen.add(n); self.fy[n] = y; self.wy[n] = y - 8; q.append((n, y))
        for t in water - seen: self.fy[t] = 0; self.wy[t] = -8
        # one surface per connected body of water: the lowest shore's (a lake touching shores at two heights was split
        # into water 16 units apart with no wall between: the background showed at the step, Shoal Cave's entrance at
        # high tide; Gen 3 lets a surfer land only on elevation 3, the low shore, anyway; sweep_caves)
        done = set()
        for t0 in sorted(water):
            if t0 in done: continue
            body, st = {t0}, [t0]
            while st:
                t = st.pop()
                for a, c in STEP.values():
                    n = (t[0] + a, t[1] + c)
                    if n in water and n not in body: body.add(n); st.append(n)
            done |= body
            low = min(self.wy[t] for t in body)
            for t in body: self.wy[t] = low

    def find_ramps(self, lv):
        """Stairs between two levels, as Black 2 builds them (slope tiles of 8/16/32 units per tile, notes
        TERRAIN_HEIGHTS.md; an actor steps between tiles < 20 units apart): a straight run of walkable Sapphire
        elevation-0 tiles whose two ends touch walkable tiles of two different levels becomes a ramp when the height
        difference divided by the run length is 8, 16 or 32. Recipe "tiles": "ramp_n"/"ramp_s"/"ramp_e"/"ramp_w"
        forces a one-tile 16-unit ramp rising toward that side from the tile's own level."""
        sm, W, H = self.sm, self.W, self.H
        walk = lambda x, z: 0 <= x < W and 0 <= z < H and sm['walk'][z][x] and self.kind[z][x] == 'floor'
        for (x, z), side in getattr(self, 'ramp_over', {}).items():
            y = self.fy.get((x, z), 0); self.ramps[(x, z)] = (side, y, y + 16)
        if not lv: return
        level = lambda x, z: lv.get(sm['elev'][z][x])
        stair = lambda x, z: walk(x, z) and sm['elev'][z][x] == 0 and (x, z) not in self.ramps
        for axis in ('ns', 'ew'):
            lines = range(W) if axis == 'ns' else range(H)
            for line in lines:
                n_along = H if axis == 'ns' else W
                at = (lambda i: (line, i)) if axis == 'ns' else (lambda i: (i, line))
                i = 0
                while i < n_along:
                    if not stair(*at(i)): i += 1; continue
                    j = i
                    while j + 1 < n_along and stair(*at(j + 1)): j += 1
                    a, b = at(i - 1), at(j + 1)            # north/west end, south/east end
                    if walk(*a) and walk(*b) and level(*a) is not None and level(*b) is not None and level(*a) != level(*b):
                        la, lb, n = level(*a), level(*b), j - i + 1
                        diff = abs(la - lb)
                        # per-tile rises from the low end: all equal when that is a Black 2 slope (8/16/32 per tile),
                        # else 8-unit slopes from the low end and flat landings at the top level (16 over 3 tiles:
                        # 8, 8, 0)
                        if diff / n in (8, 16, 32): rises = [diff / n] * n
                        elif diff % 8 == 0 and diff // 8 <= n: rises = [8] * (diff // 8) + [0] * (n - diff // 8)
                        else: rises = None
                        if rises:
                            hi_first = la > lb             # rising toward north/west
                            side = ('n' if hi_first else 's') if axis == 'ns' else ('w' if hi_first else 'e')
                            order = [at(i + k) for k in range(n)]
                            if hi_first: order.reverse()   # from the low end
                            y = min(la, lb)
                            for t, r_ in zip(order, rises):
                                if t not in self.ramps:
                                    if r_: self.ramps[t] = (side, y, y + r_); self.fy[t] = y + r_ / 2
                                    else: self.fy[t] = y
                                y += r_
                        else: self.notes.append(f'stairs {at(i)}..{at(j)}: {diff} units over {n} tiles (no Black 2 slope): flat')
                    i = j + 1

    def find_level_walls(self):
        """Walkable neighbours on different levels that Sapphire keeps apart (elevations differ, neither is 0/15,
        neither a ramp): a cliff face between them and, when they are < 20 units apart (Black 2 would let the
        player step), side walls (classes 0x51-0x58) on both tiles. {(x, z): set of blocked sides}."""
        sm, out = self.sm, defaultdict(set)
        for (x, z), y in self.fy.items():
            if self.kind[z][x] != 'floor': continue
            for d, (dx, dz) in (('e', (1, 0)), ('s', (0, 1))):
                n = (x + dx, z + dz)
                if n not in self.fy or self.kind[n[1]][n[0]] != 'floor': continue
                if n in self.ramps or (x, z) in self.ramps: continue
                e0, e1 = sm['elev'][z][x], sm['elev'][n[1]][n[0]]
                if e0 == e1 or e0 in (0, 15) or e1 in (0, 15): continue
                if abs(self.fy[n] - y) < 20:
                    out[(x, z)].add(d); out[n].add({'e': 'w', 's': 'n'}[d])
        # land next to surf water that Gen 3 keeps apart: you start and stop surfing only from/onto elevation 3
        # (field_player_avatar.c); a raised walkway beside water < 20 units above it let Black 2's player climb out
        # onto it (Shoal Cave's entrance at high tide; sweep_caves). Not beside a bridge's water (its deck is there).
        under = set(getattr(self, 'under', {})) | set(getattr(self, 'deck', {}))
        for (x, z), y in self.fy.items():
            if self.kind[z][x] != 'floor' or not sm['walk'][z][x] or sm['elev'][z][x] in (0, 3, 15): continue
            if (x, z) in self.ramps or (x, z) in under: continue
            if self.r.get('shoals') and sm['beh'][z][x] in MISC.SHOAL: continue     # (wading water: models_cave_misc)
            for d, (dx, dz) in STEP.items():
                n = (x + dx, z + dz)
                if n not in self.wy or n in under or self.kind[n[1]][n[0]] != 'water': continue
                if abs(self.wy[n] - y) < 20: out[(x, z)].add(d)
        return dict(out)

    def dest_name(self, dest_id):
        if getattr(self, 'emerald', False): return emerald_dest_name(dest_id)
        folders = getattr(Cave, '_folders', None)
        if folders is None:
            folders = {}
            base = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps')
            for d in os.listdir(base):
                p = os.path.join(base, d, 'map.json')
                if os.path.exists(p): folders[json.load(open(p))['id']] = d
            from gba import map_folders               # (+ the event maps of other decomps, data/hoenn_event_maps.json)
            for k, v in map_folders(os.path.join(ROOT, 'external', 'pokeruby')).items(): folders.setdefault(k, v)
            Cave._folders = folders
        return folders.get(dest_id, dest_id)

    def dest_outside(self, dest_id):
        name = self.dest_name(dest_id)
        if getattr(self, 'emerald', False): return emerald_dest_outside(name)
        from gba import map_json_path, event_maps
        p = map_json_path(os.path.join(ROOT, 'external', 'pokeruby'), name)
        mt = json.load(open(p))['map_type'] if os.path.exists(p) else ''
        if name in event_maps():          # Emerald calls its island exteriors indoor maps: ours are outdoor (hoenn_zones)
            zones = load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'), {}).get('maps', {})
            if name in zones: return True
        return mt not in ('MAP_TYPE_UNDERGROUND', 'MAP_TYPE_INDOOR', 'MAP_TYPE_SECRET_BASE')

    # ---- coordinates -------------------------------------------------------------------------------------------
    def lx(self, sx): return (self.ox + sx) * T            # Sapphire tile -> local units (chunk-0 corner)
    def lz(self, sz): return (self.oz + sz) * T

    def source_tiles(self):
        """Tiles the rock rises from: everything with a floor (walkable or drawn as floor), with its height."""
        return {(x, z): y for (x, z), y in self.fy.items() if self.kind[z][x] in ('floor', 'boulder', 'ledge', 'pit', 'water')}

    # ---- the rock lattice --------------------------------------------------------------------------------------
    def lattice(self):
        import numpy as np
        if LEVELS.active(self.r): return LEVELS.lattice(self)   # floors at several heights (caves_east)
        if self.look.get('outline') == 'diag': return self.lattice_diag()   # (the underwater look: map_glitch_fix)
        nx, nz = self.W * 3 + 1, self.H * 3 + 1
        LX = np.array([self.lx(0) + 16 * (i // 3) + LAT[i % 3] for i in range(nx)], float)
        LZ = np.array([self.lz(0) + 16 * (j // 3) + LAT[j % 3] for j in range(nz)], float)
        BIG = 1e9
        Hh = np.full((nz, nx), BIG); D = np.full((nz, nx), BIG); top_floor = np.zeros((nz, nx), bool)
        reach = 32 * self.tiers + 48
        if self.look.get('no_void'): reach = 16 * (self.W + self.H)     # tops over the whole map (dive agent)
        rt = int(math.ceil(reach / 16)) + 1
        for (x, z), y in self.source_tiles().items():
            i0, i1 = max(0, (x - rt) * 3), min(nx, (x + rt + 1) * 3 + 1)
            j0, j1 = max(0, (z - rt) * 3), min(nz, (z + rt + 1) * 3 + 1)
            cx, cz = self.lx(x) + 8, self.lz(z) + 8
            dx = np.maximum(0, np.abs(LX[i0:i1] - cx) - 8)
            dz = np.maximum(0, np.abs(LZ[j0:j1] - cz) - 8)
            d = np.maximum(dx[None, :], dz[:, None])
            h = y + prof(d, self.tiers)
            sub_h, sub_d = Hh[j0:j1, i0:i1], D[j0:j1, i0:i1]
            better = (h < sub_h - 1e-6) | ((np.abs(h - sub_h) <= 1e-6) & (d < sub_d))
            sub_h[better] = h[better]; sub_d[better] = d[better]
            top_floor[j0:j1, i0:i1] |= (d == 0) & (np.abs(h - Hh[j0:j1, i0:i1]) < 1e-6)
        self.LX, self.LZ, self.Hh, self.D, self.on_floor = LX, LZ, Hh, D, top_floor

    # look 'outline': 'diag' (the underwater look; map_glitch_fix 2026-10-09). The trench walls followed Sapphire's
    # walkable tile grid in right-angle steps (Chebyshev distance: every height contour a square-cornered copy of the
    # tile outline, 88% of Underwater1's wall edge on the axes, 127 right-angle corners): "stepped wall pieces". Black 2's
    # seabeds have free outlines (Abyssal Ruins chunk 555, the Marine Tube's chunks 310-315), and Sapphire's own trench
    # corner metatiles cut the corner tiles diagonally. Here the distance is L1 (45-degree contours) and every rock
    # tile whose two side neighbours and diagonal neighbour are floor loses a right-angle wedge at that corner (legs
    # 16 when it is the tile's only such corner, else 10; the floor is drawn in it, flat_rect): the stairs of 90-degree
    # corners become 45-degree walls. Drawing only: collision reads Sapphire's walk grid, walkable tiles stay as they are.
    def wedges(self, src):
        out, near_arch = [], {(a['x'] + i, a['z'] + j) for a in self.arches for i in (-1, 0, 1) for j in (-1, 0, 1)}
        for z in range(self.H):
            for x in range(self.W):
                if (x, z) in src or self.kind[z][x] != 'rock' or (x, z) in near_arch: continue
                cs = [(ex, ez) for ex in (1, -1) for ez in (1, -1)
                      if (x + ex, z) in src and (x, z + ez) in src and (x + ex, z + ez) in src]
                for ex, ez in cs:
                    out.append((self.lx(x) + (16 if ex > 0 else 0), self.lz(z) + (16 if ez > 0 else 0), -ex, -ez,
                                16 if len(cs) == 1 else 10, src[(x + ex, z + ez)]))
        return out

    def dist_diag(self, X, Z):
        """(L1 distance to the nearest floor tile or wedge, that floor's height) at points X, Z (numpy arrays)."""
        import numpy as np
        D = np.full(X.shape, 1e9); Y = np.zeros(X.shape)
        for (cx, cz, y) in self.diag_src:
            d = np.maximum(0, np.abs(X - cx) - 8) + np.maximum(0, np.abs(Z - cz) - 8)
            b = d < D; D[b] = d[b]; Y[b] = y
        for Xc, Zc, sx, sz, c, y in self.diag_wedges:
            u = (X - Xc) * sx; v = (Z - Zc) * sz
            qu, qv = np.maximum(u, 0), np.maximum(v, 0)
            d = (qu - u) + (qv - v) + np.maximum(0, qu + qv - c)
            b = d < D; D[b] = d[b]; Y[b] = y
        return D, Y

    def lattice_diag(self):
        import numpy as np
        nx, nz = self.W * 3 + 1, self.H * 3 + 1
        LX = np.array([self.lx(0) + 16 * (i // 3) + LAT[i % 3] for i in range(nx)], float)
        LZ = np.array([self.lz(0) + 16 * (j // 3) + LAT[j % 3] for j in range(nz)], float)
        src = self.source_tiles()
        self.diag_src = [(self.lx(x) + 8, self.lz(z) + 8, y) for (x, z), y in src.items()]
        self.diag_wedges = self.wedges(src)
        GX, GZ = np.meshgrid(LX, LZ)
        D, Y = self.dist_diag(GX, GZ)
        self.LX, self.LZ, self.Hh, self.D, self.on_floor = LX, LZ, Y + prof(D, self.tiers), D, D < 1e-6

    def height_at(self, X, Z):
        import numpy as np
        D, Y = self.dist_diag(np.array([X], float), np.array([Z], float))
        return float(Y[0] + prof(D, self.tiers)[0])

    # ---- geometry ----------------------------------------------------------------------------------------------
    def build_terrain(self):
        import numpy as np
        L = self.look
        m = Model(self.name)
        self.m = m
        self.lattice()
        C = lambda v: v - 256
        floors = self.source_tiles()
        drawn_floor = {t for t in floors if self.kind[t[1]][t[0]] in ('floor', 'boulder', 'ledge') and t not in self.ramps}
        if MISC.active(self.r): drawn_floor -= MISC.own_floor(self)   # drawn by MISC.geometry (caves_misc)
        if LEVELS.active(self.r): drawn_floor -= LEVELS.own_floor(self)   # plank decks: LEVELS.geometry (caves_east)
        # cut-outs: tiles where other geometry replaces the rock (arches, ladder notches)
        cut = set()
        self.cut_clip = {}        # arch neighbours: their rock is drawn up to the arch's tunnel only (rock_cells)
        for a in self.arches:
            for k in (-1, 0, 1):
                ox_, oz_ = {'s': (k, 0), 'n': (k, 0), 'e': (0, k), 'w': (0, k)}[a['face']]
                cut.add((a['x'] + ox_, a['z'] + oz_))
                if k and L.get('arch_sides', True):
                    # Black 2 runs the wall's faces up to the tunnel's sides, 16 units from the arch's middle (chunk
                    # 788): behind the frame's transparent texels there is rock, not the background (sweep_caves)
                    if a['face'] in 'ns': self.cut_clip[(a['x'] + ox_, a['z'] + oz_)] = (0, self.lx(a['x']) + 8 + 16 * k, k > 0)
                    else: self.cut_clip[(a['x'] + ox_, a['z'] + oz_)] = (2, self.lz(a['z']) + 8 + 16 * k, k > 0)
        for (x, z), way in self.ladders.items():
            if way == 'up' and 0 <= z - 1 and self.kind[z - 1][x] == 'rock':
                # (emerald_polish_caves 2026-10-12, all versions since v16.7: a ladder whose top tile stands free, floor
                # beside or behind it - Mirage Tower 2F's ladder leans on nothing, Victory Road B1F (42,25), Navel Rock's
                # ladder rooms - keeps that tile as rock and gets the short flight: the notch cut into a lone tile stood
                # as a hollow black box on the floor)
                src_ = self.source_tiles()
                if any(t in src_ for t in ((x - 1, z - 1), (x + 1, z - 1), (x, z - 2))): continue
                cut.add((x, z - 1))
        self.cut = cut
        # floor: rectangles of tiles at one height
        fs = L.get('floor_size', 64)
        fc = (L.get('floor_color', 1.0),) * 3              # Reversal Mountain's floors are baked darker (~0.87)
        by_y = defaultdict(set)
        for t in drawn_floor: by_y[floors[t]].add(t)
        self.foot_cells = {}                                # lattice cells with floor under a wall's foot: height
        foot = self.foot_region(by_y, floors) if L.get('foot_floor', True) else {}
        for y, tiles in by_y.items():
            if y in foot:                                   # floor tiles + the walls' feet, on the lattice's grid
                for i0, j0, i1, j1 in rects(foot[y]):
                    X0, X1, Z0, Z1 = self.LX[i0], self.LX[i1 + 1], self.LZ[j0], self.LZ[j1 + 1]
                    m.quad(L['floor'], [(C(X0), y, C(Z1), X0 / fs, -Z1 / fs), (C(X1), y, C(Z1), X1 / fs, -Z1 / fs),
                                        (C(X1), y, C(Z0), X1 / fs, -Z0 / fs), (C(X0), y, C(Z0), X0 / fs, -Z0 / fs)], color=fc)
                continue
            for x0, z0, x1, z1 in rects(tiles):
                X0, X1, Z0, Z1 = self.lx(x0), self.lx(x1 + 1), self.lz(z0), self.lz(z1 + 1)
                m.quad(L['floor'], [(C(X0), y, C(Z1), X0 / fs, -Z1 / fs), (C(X1), y, C(Z1), X1 / fs, -Z1 / fs),
                                    (C(X1), y, C(Z0), X1 / fs, -Z0 / fs), (C(X0), y, C(Z0), X0 / fs, -Z0 / fs)], color=fc)
        self.rock_cells()
        self.ledges()
        self.walls_dir()
        for t, r in self.ramps.items(): self.ramp(t, *r)
        self.steps(drawn_floor | set(self.ramps))
        self.skirts(drawn_floor | set(self.ramps))
        falls = getattr(self, 'falls', {})
        if self.wy: self.skirts({t for t in self.wy if t not in falls}, water=True)   # (below the water's banks)
        if self.wy: self.water()
        for a in self.arches: self.arch(a)
        for (x, z), way in self.ladders.items(): (self.ladder_up if way == 'up' else self.ladder_down)(x, z)
        if self.r.get('decals', True): self.decals(drawn_floor)
        self.cracked_floor()
        if L.get('rock_sprites'): self.rock_sprites()
        if LEVELS.active(self.r): LEVELS.geometry(self)     # bridge decks, waterfall sheets
        if MISC.active(self.r): MISC.geometry(self)         # shallow water, ice (caves_misc)
        if UW.active(self.r): UW.geometry(self)             # seaweed / light decals (dive agent)
        if MIST.active(self): MIST.geometry(self)           # mist caves: black void, crack cover (underwater_polish)
        if self.r.get('seam_cover', True): self.seam_cover(by_y, foot)   # T-junction cover (emerald_polish_caves, v16.7;
        # recipe "seam_cover": false where a chunk would pass Black 2's 110,600-byte buffer: Victory Road B1F)
        return m

    def seam_cover(self, by_y, foot):
        """(emerald_polish_caves 2026-10-12; Emerald first, all versions since v16.7) The DS leaves single pixels open where one merged floor or
        rock-top rectangle's corner touches the middle of another's edge (T-junctions); the black background showed
        through as dots across every floor (Terra Cave, Cave of Origin B1F) and thin lines over the rock (Desert
        Underpass). Under each floor a second copy 2 units down, merged column-wise (the floor is merged row-wise, so
        the two layers' seams cross instead of lining up), and under each flat rock top a copy 4 units down (the mist
        caves' crack cover, models_cave_mist, which already does it there). Hidden everywhere else by the layer above
        (caves_check f: >= 1.95 apart)."""
        L, m = self.look, self.m
        if UW.active(self.r): return                      # (the underwater look has its own backdrop: models_cave_uw)
        C = lambda v: v - 256
        fs, fc = L.get('floor_size', 64), (L.get('floor_color', 1.0),) * 3
        for y, tiles in by_y.items():
            yb = y - 2
            if y in foot:
                for j0, i0, j1, i1 in rects({(j, i) for (i, j) in foot[y]}):
                    X0, X1, Z0, Z1 = self.LX[i0], self.LX[i1 + 1], self.LZ[j0], self.LZ[j1 + 1]
                    m.quad(L['floor'], [(C(X0), yb, C(Z1), X0 / fs, -Z1 / fs), (C(X1), yb, C(Z1), X1 / fs, -Z1 / fs),
                                        (C(X1), yb, C(Z0), X1 / fs, -Z0 / fs), (C(X0), yb, C(Z0), X0 / fs, -Z0 / fs)], color=fc)
            else:
                for z0, x0, z1, x1 in rects({(z, x) for (x, z) in tiles}):
                    X0, X1, Z0, Z1 = self.lx(x0), self.lx(x1 + 1), self.lz(z0), self.lz(z1 + 1)
                    m.quad(L['floor'], [(C(X0), yb, C(Z1), X0 / fs, -Z1 / fs), (C(X1), yb, C(Z1), X1 / fs, -Z1 / fs),
                                        (C(X1), yb, C(Z0), X1 / fs, -Z0 / fs), (C(X0), yb, C(Z0), X0 / fs, -Z0 / fs)], color=fc)
        if MIST.active(self) or L.get('outline') == 'diag' or L.get('no_void'): return
        H = self.Hh; nz, nx = H.shape
        floors = self.source_tiles()
        tmax = 32 * self.tiers + 16
        by_h = defaultdict(set)
        for j in range(nz - 1):
            for i in range(nx - 1):
                if (i // 3, j // 3) in floors or (i // 3, j // 3) in self.cut: continue
                hs = (H[j, i], H[j, i + 1], H[j + 1, i], H[j + 1, i + 1])
                if max(hs) > 1e8 or max(hs) - min(hs) > 1e-6: continue
                ds = (self.D[j, i], self.D[j, i + 1], self.D[j + 1, i], self.D[j + 1, i + 1])
                if min(ds) < 16 - 1e-6 or min(ds) >= tmax - 1e-6: continue   # (floor cells, the first face band; the rim)
                by_h[round(hs[0], 3)].add((i, j))
        s, col = L.get('top_size', 16), (L.get('top_color', EDGE),) * 3
        for h, cells in by_h.items():
            y = h - 4
            for i0, j0, i1, j1 in rects(cells):
                X0, X1, Z0, Z1 = self.LX[i0], self.LX[i1 + 1], self.LZ[j0], self.LZ[j1 + 1]
                m.quad(L['top'], [(C(X0), y, C(Z1), X0 / s, -Z1 / s, col), (C(X1), y, C(Z1), X1 / s, -Z1 / s, col),
                                  (C(X1), y, C(Z0), X1 / s, -Z0 / s, col), (C(X0), y, C(Z0), X0 / s, -Z0 / s, col)])

    def foot_region(self, by_y, floors):
        """Black 2 draws the floor on under a wall's foot (Wellspring 486: every d0gake_001 face lies over d0yuka_001):
        face_low's bottom texel rows are transparent (d0gake_001, in81_gake_b, in51_gake1), and without a floor under
        them the background showed through along every wall's foot (sweep_caves). {height: lattice cells (i, j)}: the
        cells of the drawn floor tiles at that height and the rock cells of their walls' first band (within 6 units of
        such a tile, every corner between the floor's height and 4 above it: the wall rises from that floor), merged
        into rectangles by the caller (one floor drawing, no extra faces per wall)."""
        H = self.Hh; nzl, nxl = H.shape
        out = defaultdict(set)
        for y, tiles in by_y.items():
            for (x, z) in tiles:
                for a in range(3):
                    for b in range(3): out[y].add((3 * x + a, 3 * z + b))
        tile_y = {t: y for y, tiles in by_y.items() for t in tiles}
        for j in range(nzl - 1):
            for i in range(nxl - 1):
                tx, tz = i // 3, j // 3
                if (tx, tz) in floors or (tx, tz) in self.cut: continue
                hs = (H[j, i], H[j, i + 1], H[j + 1, i], H[j + 1, i + 1])
                if max(hs) > 1e8: continue
                a, b = i % 3, j % 3                          # the cell within its tile: 0 = 0..6, 1 = 6..10, 2 = 10..16
                dxs = [-1] if a == 0 else [1] if a == 2 else []
                dzs = [-1] if b == 0 else [1] if b == 2 else []
                cand = [(tx + dx, tz) for dx in dxs] + [(tx, tz + dz) for dz in dzs] + [(tx + dx, tz + dz) for dx in dxs for dz in dzs]
                for n in cand:
                    y = tile_y.get(n)
                    if y is None: continue
                    if min(hs) >= y - 0.01 and min(hs) <= y + 0.01 and y + 0.01 < max(hs) <= y + 4.01:   # (rising)
                        out[y].add((i, j)); self.foot_cells[(i, j)] = y; break
        return out

    def in_foot_cell(self, t):
        """The floor height Cave.foot_region drew under the lattice cell of a triangle (local x, z), or None."""
        import numpy as np
        cx, cz = sum(p[0] for p in t) / 3, sum(p[2] for p in t) / 3
        i = int(np.searchsorted(self.LX, cx)) - 1; j = int(np.searchsorted(self.LZ, cz)) - 1
        return getattr(self, 'foot_cells', {}).get((i, j))

    def all_foot_cells(self, t):
        """Whether every lattice cell a triangle (local x, z) overlaps has the floor Cave.foot_region drew (a merged
        strip of a wall's foot may run past the cells it drew)."""
        import numpy as np
        xs, zs = [p[0] for p in t], [p[2] for p in t]
        i0 = int(np.searchsorted(self.LX, min(xs) + 1e-6)) - 1; i1 = int(np.searchsorted(self.LX, max(xs) - 1e-6)) - 1
        j0 = int(np.searchsorted(self.LZ, min(zs) + 1e-6)) - 1; j1 = int(np.searchsorted(self.LZ, max(zs) - 1e-6)) - 1
        fc = getattr(self, 'foot_cells', {})
        return all((i, j) in fc for i in range(i0, i1 + 1) for j in range(j0, j1 + 1))

    def rock_cells(self):
        """Faces, rock tops and the rim/void from the lattice, merged into strips where planar."""
        import numpy as np
        L, Hh, D, LX, LZ = self.look, self.Hh, self.D, self.LX, self.LZ
        nz, nx = Hh.shape
        tmax = 32 * self.tiers + 16                       # profile distance where the last lip ends
        rd = L.get('rim_depth', 16)                       # rim width past the last lip (Wellspring 16, Reversal Mtn 8)
        floors = self.source_tiles()
        cells = {}
        for j in range(nz - 1):
            for i in range(nx - 1):
                tx, tz = i // 3, j // 3
                clip = getattr(self, 'cut_clip', {}).get((tx, tz))
                if (tx, tz) in floors or ((tx, tz) in self.cut and clip is None): continue
                hs = (Hh[j, i], Hh[j, i + 1], Hh[j + 1, i], Hh[j + 1, i + 1])
                ds = (D[j, i], D[j, i + 1], D[j + 1, i], D[j + 1, i + 1])
                if max(hs) > 1e8: continue                  # nothing walkable anywhere near: no geometry
                if min(ds) >= tmax - 1e-6 and L.get('no_void'):   # (dive agent: the seabed has no edge)
                    key = ('top', round(max(hs), 3))
                elif min(ds) >= tmax - 1e-6:
                    key = ('rim', ) + tuple(round(min(1.0, (d - tmax) / rd), 3) if d <= tmax + rd + 1e-6 else 2.0 for d in ds) \
                          + tuple(round(h, 3) for h in hs)
                elif max(hs) - min(hs) < 1e-6:
                    key = ('top', round(hs[0], 3))
                else:
                    key = ('face', ) + tuple(round(h, 3) for h in hs) + tuple(round(d, 3) for d in ds)
                if clip is not None: key = key + (('clip', i, j),)  # (one cell each, not merged with others)
                cells[(i, j)] = key
        done = set()
        real_m = self.m
        for (i, j), key in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            if (i, j) in done: continue
            clip = getattr(self, 'cut_clip', {}).get((i // 3, j // 3)) if isinstance(key[-1], tuple) else None
            self.m = _ClipModel(real_m, *clip) if clip else real_m
            try: self._rock_cell(i, j, key, cells, done)
            finally: self.m = real_m

    def _rock_cell(self, i, j, key, cells, done):
        """One cell of the lattice, merged with equal neighbours (rock_cells)."""
        LX, LZ, Hh, D = self.LX, self.LZ, self.Hh, self.D
        if True:
            if key[0] in ('top', 'rim') and (key[0] == 'top' or self.flat_key(key)):
                # flat: grow a rectangle of equal keys
                i1 = i
                while (i1 + 1, j) in cells and cells[(i1 + 1, j)] == key and (i1 + 1, j) not in done: i1 += 1
                j1 = j
                while all((k, j1 + 1) in cells and cells[(k, j1 + 1)] == key and (k, j1 + 1) not in done for k in range(i, i1 + 1)): j1 += 1
                for a in range(i, i1 + 1):
                    for b in range(j, j1 + 1): done.add((a, b))
                self.flat_rect(key, LX[i], LX[i1 + 1], LZ[j], LZ[j1 + 1], Hh[j, i], D[j, i])
                return
            hs = key_h(key)
            # straight strips: heights vary along z only (north/south faces) -> run along x, and vice versa
            if abs(hs[0] - hs[1]) < 1e-6 and abs(hs[2] - hs[3]) < 1e-6:
                i1 = i
                while (i1 + 1, j) in cells and cells[(i1 + 1, j)] == key and (i1 + 1, j) not in done: i1 += 1
                for a in range(i, i1 + 1): done.add((a, j))
                self.cell_quad(key, i, j, i1 + 1, j + 1)
            elif abs(hs[0] - hs[2]) < 1e-6 and abs(hs[1] - hs[3]) < 1e-6:
                j1 = j
                while (i, j1 + 1) in cells and cells[(i, j1 + 1)] == key and (i, j1 + 1) not in done: j1 += 1
                for b in range(j, j1 + 1): done.add((i, b))
                self.cell_quad(key, i, j, i + 1, j1 + 1)
            else:
                done.add((i, j))
                self.cell_quad(key, i, j, i + 1, j + 1)

    @staticmethod
    def flat_key(key):
        hs = key_h(key)
        return max(hs) - min(hs) < 1e-6 and len(set(key[1:5])) == 1

    def flat_rect(self, key, X0, X1, Z0, Z1, h, d):
        L = self.look
        C = lambda v: v - 256
        if key[0] == 'top' and L.get('outline') == 'diag' and d < 1e-6:     # (a wedge cut into a rock tile: floor)
            fs, fc = L.get('floor_size', 64), (L.get('floor_color', 1.0),) * 3
            self.m.quad(L['floor'], [(C(X0), h, C(Z1), X0 / fs, -Z1 / fs), (C(X1), h, C(Z1), X1 / fs, -Z1 / fs),
                                     (C(X1), h, C(Z0), X1 / fs, -Z0 / fs), (C(X0), h, C(Z0), X0 / fs, -Z0 / fs)], color=fc)
        elif key[0] == 'top':
            s, col = L.get('top_size', 16), (L.get('top_color', EDGE),) * 3
            self.m.quad(L['top'], [(C(X0), h, C(Z1), X0 / s, -Z1 / s, col), (C(X1), h, C(Z1), X1 / s, -Z1 / s, col),
                                   (C(X1), h, C(Z0), X1 / s, -Z0 / s, col), (C(X0), h, C(Z0), X0 / s, -Z0 / s, col)])
        else:                                          # the rim (v < 1 runs) or the black beyond (2.0: colour 0)
            v = min(1.0, key[1]); col = (L.get('rim_color', 1.0),) * 3 if key[1] <= 1 else (0.0,) * 3
            s = 16
            self.m.quad(L['rim'], [(C(X0), h, C(Z1), X0 / s, v, col), (C(X1), h, C(Z1), X1 / s, v, col),
                                   (C(X1), h, C(Z0), X1 / s, v, col), (C(X0), h, C(Z0), X0 / s, v, col)])

    def cell_quad(self, key, i0, j0, i1, j1):
        """A (merged) lattice cell of a face or rim: two triangles split along the crease (equal-height diagonal)."""
        LX, LZ, Hh, D = self.LX, self.LZ, self.Hh, self.D
        if key[0] == 'face' and getattr(self, 'DB', None) is not None: D = self.DB   # bands by the lower face at ties
        pts = {(a, b): (LX[a], Hh[b, a], LZ[b], D[b, a]) for a in (i0, i1) for b in (j0, j1)}
        p00, p10, p01, p11 = pts[(i0, j0)], pts[(i1, j0)], pts[(i0, j1)], pts[(i1, j1)]
        if key[0] == 'face' and self.look.get('outline') == 'diag':
            # (the diagonal whose midpoint matches the wall's height at the cell's centre: the equal-height diagonal ran
            # across a corner's crease and left a flat ledge in every wall corner, 588 in Underwater1)
            hc = self.height_at((LX[i0] + LX[i1]) / 2, (LZ[j0] + LZ[j1]) / 2)
            first = abs((p00[1] + p11[1]) / 2 - hc) <= abs((p10[1] + p01[1]) / 2 - hc)
        else: first = abs(p00[1] - p11[1]) <= abs(p10[1] - p01[1])
        if first: tris = [(p00, p10, p11), (p00, p11, p01)]
        else: tris = [(p00, p10, p01), (p10, p11, p01)]
        if LEVELS.active(self.r) and LEVELS.steep_cell(self, key, tris): return   # a cliff between levels
        for t in tris: self.face_tri(key[0], t)

    def face_tri(self, kind, t):
        L = self.look
        C = lambda v: v - 256
        tmax = 32 * self.tiers + 16
        rd = L.get('rim_depth', 16)
        (x0, y0, z0, d0), (x1, y1, z1, d1), (x2, y2, z2, d2) = t
        # make it face up (counter-clockwise seen from above): the lattice is a height field
        ny = (z1 - z0) * (x2 - x0) - (x1 - x0) * (z2 - z0)
        if ny < 0: t = (t[0], t[2], t[1]); (x0, y0, z0, d0), (x1, y1, z1, d1), (x2, y2, z2, d2) = t
        if kind == 'rim':
            # u along the rim: x on north/south rims, z where the rim runs north-south (v grows with x there: u by x
            # smeared the texture into streaks on east/west rims; sweep_caves)
            ddx = (d1 - d0) * (z2 - z0) - (d2 - d0) * (z1 - z0)
            ddz = (d2 - d0) * (x1 - x0) - (d1 - d0) * (x2 - x0)
            along_z = abs(ddx) > abs(ddz) + 1e-6
            verts = []
            for x, y, z, d in t:
                v = min(1.0, max(0.0, (d - tmax) / rd)); c = L.get('rim_color', 1.0) if d <= tmax + rd + 1e-6 else 0.0
                verts.append((C(x), y, C(z), (z if along_z else x) / 16, v, (c, c, c)))
            self.m.tri(L['rim'], verts); return
        # face: orientation from the gradient, band from the profile position
        ds = [p[3] for p in t]
        k = math.floor(min(ds) / 32 + 1e-6)
        rs = [d - 32 * k for d in ds]
        rmean = sum(rs) / 3
        band = 'A' if rmean < 6 else 'B' if rmean < 10 else 'C'
        if band == 'A': tex = L['face_low'] if k == 0 else L['face_low_rock']
        elif band == 'B': tex = L['face_mid']
        else:
            # (a vertex at or past its tier's top on a walkable floor's edge: Black 2's floor lip d0gake_002 (chunk 488).
            # The test was "exactly at the top" (16), but a lower floor two or more tiles deep ties the profile at 16 for
            # every distance 16-32, the lattice keeps the larger distance (models_cave_levels DB), and raised floors
            # got the dark rock lip: a flat slab with a hard edge, Meteor Falls 1F_1R's platform; map_glitch_fix 2026-10-09)
            top_floor = any(self.on_floor_at(p[0], p[2]) for p in t if p[3] - 32 * k >= 16 - 1e-6)
            tex = L['lip_floor'] if top_floor else L['lip_rock']
        flat = max(y0, y1, y2) - min(y0, y1, y2) < 1e-6
        fy_cell = self.in_foot_cell(t)
        if flat and fy_cell is not None and abs(y0 - fy_cell) < 0.01 and not isinstance(self.m, _ClipModel):
            return                                            # (the floor Cave.foot_region drew is there)
        if flat and k == 0 and all(abs(r) < 1e-6 for r in rs):
            # a flat crease triangle at the floor's own height (an inner corner between floors): floor (sweep_caves)
            fs, fc = L.get('floor_size', 64), (L.get('floor_color', 1.0),) * 3
            self.m.tri(L['floor'], [(C(x), y, C(z), x / fs, -z / fs, fc) for x, y, z, d in t]); return
        if band == 'A' and k == 0 and L.get('foot_floor', True):
            # Black 2 draws the floor on under a wall's foot (Wellspring 486: every d0gake_001 face lies over d0yuka_001;
            # sweep_caves): face_low's bottom texel rows are transparent (d0gake_001, in81_gake_b, in51_gake1), and
            # without a floor under them the background showed through along every wall's foot
            yb = min(y - face_y(min(16.0, max(0.0, r))) for (x, y, z, d), r in zip(t, rs))
            fs, fc = L.get('floor_size', 64), (L.get('floor_color', 1.0),) * 3
            if isinstance(self.m, _ClipModel) or not self.all_foot_cells(t):   # (Cave.foot_region drew most of them)
                self.m.tri(L['floor'], [(C(x), yb, C(z), x / fs, -z / fs, fc) for x, y, z, d in t])
        # horizontal gradient of the plane -> which way it faces
        ax, ay, az = x1 - x0, y1 - y0, z1 - z0
        bx, by, bz = x2 - x0, y2 - y0, z2 - z0
        nx_, ny_, nz_ = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
        us = L.get('face_u', 32)
        if max(y0, y1, y2) - min(y0, y1, y2) < 1e-6:
            # a flat triangle of a crease cell (where two walls' profiles meet): a tier's top (r 16) gets the rock top,
            # others the band's texture mapped flat; the band's own v is one value there and smeared one texel row
            # over the whole triangle (sweep_caves)
            if all(abs(r - 16) < 1e-6 for r in rs) or (L.get('outline') == 'diag' and all(r >= 16 - 1e-6 for r in rs)):
                s_, col = L.get('top_size', 16), (L.get('top_color', EDGE),) * 3
                self.m.tri(L['top'], [(C(x), y, C(z), x / s_, -z / s_, col) for x, y, z, d in t]); return
            # (v with u's density: a face texture's height over its width times face_u units; both moved by whole
            # repeats to near 0, the DS keeps texture coordinates within +-2048 texels)
            img = set_images(L.get('tex_sets', {}).get(tex, L['set']))[tex]
            vs_ = us * img.size[1] / img.size[0]
            uv = [(x / us, -z / vs_) for x, y, z, d in t]
            ku, kv = math.floor(min(a for a, b in uv)), math.floor(min(b for a, b in uv))
            self.m.tri(tex, [(C(x), y, C(z), a - ku, b - kv, (shade(min(16.0, max(0.0, r)), L.get('edge', EDGE)),) * 3)
                             for ((x, y, z, d), r), (a, b) in zip(zip(t, rs), uv)]); return
        if L.get('face_uv'):
            # look 'face_uv' [u units, v units] (one wall texture for every band, the underwater look; map_glitch_fix
            # 2026-10-09): v by the distance up the wall's slope, so the texture keeps one density from foot to lip. By
            # bands the top band packed the whole 64-texel texture into 6 units of slope (10 texels a unit against 3-4
            # below): a streaky rim that read as a separate piece along every wall's top
            fu, fv = L['face_uv']
            verts = []
            for (x, y, z, d), r in zip(t, rs):
                r = min(16.0, max(0.0, r))
                u = ((x if nz_ > 0 else -x) if abs(nz_) >= abs(nx_) else (-z if nx_ > 0 else z)) / fu
                c = shade(r, L.get('edge', EDGE))
                verts.append((C(x), y, C(z), u, (slope_len(r) + SLOPE_TIER * k) / fv, (c, c, c)))
            self.m.tri(L['face_mid'], verts); return
        verts = []
        for (x, y, z, d), r in zip(t, rs):
            r = min(16.0, max(0.0, r))
            if abs(nz_) >= abs(nx_): u = (x if nz_ > 0 else -x) / us
            else: u = (-z if nx_ > 0 else z) / us
            # (the floor lip at full colour, as Black 2's d0gake_002 in chunks 486/488/630/788; the rock's edge shading
            # darkened it to 0.77 at the floor's edge)
            c = MID if tex == L['lip_floor'] and L['lip_floor'] != L['lip_rock'] else shade(r, L.get('edge', EDGE))
            verts.append((C(x), y, C(z), u, band_v(band, r), (c, c, c)))
        # a band's v grows with the height on a tier's face; where a triangle's vertices take their distances from
        # different floors (between levels) it did not (one texel row smeared down a 16-unit drop): drawn as a cliff,
        # the middle face texture by height, as LEVELS.steep_cell (sweep_caves)
        if any(abs(a[1] - b[1]) > 1 and (b[4] - a[4]) / (b[1] - a[1]) <= 1e-6 for a in verts for b in verts if a is not b) \
                or any(not -0.01 <= v[4] <= 1.01 for v in verts):        # (or a band's v past its own 0..1: two tiers)
            lo, hi = min(v[1] for v in verts), max(v[1] for v in verts)
            e = L.get('edge', EDGE)
            verts = [(v[0], v[1], v[2], v[3], v[1] / 16, ((e + (1 - e) * (v[1] - lo) / (hi - lo)),) * 3) for v in verts]
            tex = L['face_mid']
        self.m.tri(tex, verts)

    def on_floor_at(self, x, z):
        import numpy as np
        i = int(np.argmin(np.abs(self.LX - x))); j = int(np.argmin(np.abs(self.LZ - z)))
        return bool(self.on_floor[j, i])

    # ---- ledges (Black 2's d0dan ridge) ------------------------------------------------------------------------
    def ledges(self):
        runs = defaultdict(list)                         # (dir, line) -> positions along the run
        for (x, z), d in self.ledge_dir.items():
            if d in 'ns': runs[(d, z)].append(x)
            else: runs[(d, x)].append(z)
        for (d, line), ps in runs.items():
            ps.sort(); start = prev = ps[0]
            for p in ps[1:] + [None]:
                if p is not None and p == prev + 1: prev = p; continue
                self.ridge(d, line, start, prev)
                if p is not None: start = prev = p

    def ridge(self, d, line, a0, a1, steep=(8, 6), gentle=-2, height=4, edge=None):
        """Black 2's ledge ridge (Wellspring chunk 486 row 7) for a run of ledge tiles a0..a1 jumping toward d.
        Across-coordinate q is measured from the take-off edge toward the landing: gentle foot at q=-2 (v 1), peak at
        q=+6 (y 4, v 0.62), steep foot at q=+8 (v 0)."""
        L = self.look
        C = lambda v: v - 256
        y = self.fy.get((a0, line) if d in 'ns' else (line, a0), 0)
        sgn = {'n': -1, 's': 1, 'e': 1, 'w': -1}[d]
        if edge is None:    # take-off edge of the ledge tiles (the side you jump from)
            edge = (self.lz(line) if d == 's' else self.lz(line + 1)) if d in 'ns' else (self.lx(line) if d == 'e' else self.lx(line + 1))
        q = lambda off: edge + sgn * off
        lo = (self.lx(a0) if d in 'ns' else self.lz(a0)); hi = (self.lx(a1 + 1) if d in 'ns' else self.lz(a1 + 1))
        prof_pts = [(q(gentle), 0.0, 1.0), (q(steep[1]), float(height), 0.62), (q(steep[0]), 0.0, 0.0)]
        def P(along, across, h, v):
            x, z = (along, across) if d in 'ns' else (across, along)
            return (C(x), y + h, C(z), along / 16, v)
        tap = 8                                          # the peak line stops 8 units short of the run ends
        for (q0, h0, v0), (q1, h1, v1) in zip(prof_pts, prof_pts[1:]):
            a_lo0, a_hi0 = (lo + tap, hi - tap) if h0 > 0 else (lo, hi)
            a_lo1, a_hi1 = (lo + tap, hi - tap) if h1 > 0 else (lo, hi)
            quad = [P(a_lo0, q0, h0, v0), P(a_hi0, q0, h0, v0), P(a_hi1, q1, h1, v1), P(a_lo1, q1, h1, v1)]
            for tri in ([quad[0], quad[1], quad[2]], [quad[0], quad[2], quad[3]]):
                if up_facing(tri): self.m.tri(L['ledge'], tri)
                else: self.m.tri(L['ledge'], [tri[0], tri[2], tri[1]])
        # end caps: the triangle under the peak's taper at both ends
        for end, inward in ((lo, 1), (hi, -1)):
            cap = [P(end, q(gentle), 0, 1.0), P(end + inward * tap, q(steep[1]), height, 0.62), P(end, q(steep[0]), 0, 0.0)]
            self.m.tri(L['ledge'], cap if up_facing(cap) else [cap[0], cap[2], cap[1]])

    def walls_dir(self):
        """Sapphire's one-sided walls on walkable tiles (MB_IMPASSABLE_*): the same low ridge along the blocked edge."""
        for (x, z), ds in self.wall_dirs.items():
            for d in ds:
                if d in 'ns':
                    edge = self.lz(z) if d == 'n' else self.lz(z + 1)
                    self.ridge('n' if d == 'n' else 's', z, x, x, edge=edge, steep=(4, 2), gentle=-4)
                else:
                    edge = self.lx(x) if d == 'w' else self.lx(x + 1)
                    self.ridge('w' if d == 'w' else 'e', x, z, z, edge=edge, steep=(4, 2), gentle=-4)

    # ---- water ------------------------------------------------------------------------------------------------------
    def water(self):
        """Black 2's cave water (Wellspring Cave 486): an opaque bottom (look "water", d0_miz, 64 units per repeat)
        at the collision height (shore - 8), reaching 4 units under the banks; a sparkle layer ("water_top",
        d0_miz2, 16 per repeat, 1-bit alpha) 4 above it; banks ("water_bank", d0mizu_gake) from the shore down to the
        bottom on every edge to a non-water tile."""
        L = self.look
        assert L.get('water'), f'{self.name}: look {self.look_name} has no water textures'
        C = lambda v: v - 256
        by = defaultdict(set)
        falls = getattr(self, 'falls', {})                  # waterfall drops: drawn by LEVELS.geometry
        for t, y in self.wy.items():
            if t not in falls: by[y].add(t)
        for y, tiles in by.items():
            for x0, z0, x1, z1 in rects(tiles):
                X0, X1, Z0, Z1 = self.lx(x0), self.lx(x1 + 1), self.lz(z0), self.lz(z1 + 1)
                for tex, yy, sz, grow in ((L['water'], y, 64, 4), (L['water_top'], y + 4, L.get('water_top_size', 16), 0)):
                    a0, a1, b0, b1 = X0 - grow, X1 + grow, Z0 - grow, Z1 + grow
                    self.m.quad(tex, [(C(a0), yy, C(b1), a0 / sz, -b1 / sz), (C(a1), yy, C(b1), a1 / sz, -b1 / sz),
                                      (C(a1), yy, C(b0), a1 / sz, -b0 / sz), (C(a0), yy, C(b0), a0 / sz, -b0 / sz)])
        for (x, z), y in self.wy.items():
            if (x, z) in falls: continue
            top = self.fy[(x, z)]
            for dx, dz in STEP.values():
                n = (x + dx, z + dz)
                if n in self.wy: continue
                if dx: p = ((self.lx(x + (dx > 0)), self.lz(z)), (self.lx(x + (dx > 0)), self.lz(z + 1)))
                else: p = ((self.lx(x), self.lz(z + (dz > 0))), (self.lx(x + 1), self.lz(z + (dz > 0))))
                self.vwall(L['water_bank'], p[0], p[1], y, top, 0.77, 1.0, face=(-dx, -dz))   # (seen from the water)

    # ---- levels: ramps, cliffs between walkable tiles --------------------------------------------------------------
    def ramp(self, t, side, lo, hi):
        """A slope tile with the look's stairs texture (Black 2's terrain stairs: u along the climb, 32 units per
        repeat, v across, 8 units per repeat, as Wellspring 486's d0kaidan_01)."""
        L = self.look
        C = lambda v: v - 256
        x, z = t
        X0, X1, Z0, Z1 = self.lx(x), self.lx(x + 1), self.lz(z), self.lz(z + 1)
        def h(px, pz):                                   # height at a corner
            f = {'n': (Z1 - pz) / 16, 's': (pz - Z0) / 16, 'w': (X1 - px) / 16, 'e': (px - X0) / 16}[side]
            return lo + (hi - lo) * f
        def uv(px, pz):
            along = {'n': Z1 - pz, 's': pz - Z0, 'w': X1 - px, 'e': px - X0}[side]
            across = px if side in 'ns' else pz
            return along / 32, across / 8
        q = [(X0, Z1), (X1, Z1), (X1, Z0), (X0, Z0)]
        verts = [(C(px), h(px, pz), C(pz)) + uv(px, pz) for px, pz in q]
        for tri in ([verts[0], verts[1], verts[2]], [verts[0], verts[2], verts[3]]):
            self.m.tri(L['stairs'], tri if up_facing(tri) else [tri[0], tri[2], tri[1]])

    def surface_y(self, t, px, pz):
        """Height of tile t's walking surface at local point (px, pz): a ramp's plane, else its floor height."""
        if t in self.ramps:
            side, lo, hi = self.ramps[t]
            X0, Z0 = self.lx(t[0]), self.lz(t[1])
            f = {'n': (Z0 + 16 - pz) / 16, 's': (pz - Z0) / 16, 'w': (X0 + 16 - px) / 16, 'e': (px - X0) / 16}[side]
            return lo + (hi - lo) * f
        return self.fy[t]

    def steps(self, tiles):
        """Vertical rock faces where two neighbouring floor/ramp tiles meet at different heights (a cliff between
        levels that Sapphire draws on the tiles themselves, the sides of a ramp, a bridge's edge): the look's mid face
        texture (16 units per v), edge colour, both windings. Collision is separate (find_level_walls)."""
        L = self.look
        C = lambda v: v - 256
        e = (L.get('edge', EDGE),) * 3
        for (x, z) in sorted(tiles):
            for dx, dz in ((1, 0), (0, 1)):
                n = (x + dx, z + dz)
                if n not in tiles: continue
                if dx: p0, p1 = (self.lx(x + 1), self.lz(z)), (self.lx(x + 1), self.lz(z + 1))
                else: p0, p1 = (self.lx(x), self.lz(z + 1)), (self.lx(x + 1), self.lz(z + 1))
                a0, a1 = self.surface_y((x, z), *p0), self.surface_y((x, z), *p1)
                b0, b1 = self.surface_y(n, *p0), self.surface_y(n, *p1)
                if abs(a0 - b0) < 0.5 and abs(a1 - b1) < 0.5: continue
                u0, u1 = (p0[0] + p0[1]) / 32, (p1[0] + p1[1]) / 32
                q = [(C(p0[0]), a0, C(p0[1]), u0, a0 / 16, e), (C(p1[0]), a1, C(p1[1]), u1, a1 / 16, e),
                     (C(p1[0]), b1, C(p1[1]), u1, b1 / 16, e), (C(p0[0]), b0, C(p0[1]), u0, b0 / 16, e)]
                # only the side facing the lower tile (the DS culls back faces), none facing north (never seen from the
                # camera): both sides doubled the faces (sweep_caves: chunk size)
                lower_n = (b0 + b1) < (a0 + a1)                   # the neighbour (east/south) is the lower tile
                fx, fz = (dx, dz) if lower_n else (-dx, -dz)
                if (fx, fz) == (0, -1): continue
                for tri in ([q[0], q[1], q[2]], [q[0], q[2], q[3]]):
                    if len({(round(v[0], 3), round(v[1], 3), round(v[2], 3)) for v in tri}) < 3: continue
                    (ax_, ay_, az_), (bx_, by_, bz_), (cx_, cy_, cz_) = [v[:3] for v in tri]
                    nx_ = (by_ - ay_) * (cz_ - az_) - (bz_ - az_) * (cy_ - ay_)
                    nz_ = (bx_ - ax_) * (cy_ - ay_) - (by_ - ay_) * (cx_ - ax_)
                    self.m.tri(L['face_mid'], tri if nx_ * fx + nz_ * fz > 0 else [tri[0], tri[2], tri[1]])

    def skirts(self, tiles, water=False, heights=None):
        """Rock faces under the edges of floors and ramps where the rock lattice beside them lies lower than their
        surface: with floors at several heights the rock beside a raised floor can rise from a lower floor or a ramp
        (the lattice rises from a ramp tile's middle height), and the background showed through under the raised
        floor's edge and beside every ramp's upper half (Meteor Falls, Shoal Cave, Victory Road; sweep_caves). The
        look's middle face texture (16 units per v, 32 per u), edge colour, both windings, as steps(). A cave on one
        level gets none (its lattice meets every floor edge at the floor's own height)."""
        L = self.look
        C = lambda v: v - 256
        e = (L.get('edge', EDGE),) * 3
        src = self.source_tiles()
        nzl, nxl = self.Hh.shape
        for (x, z) in sorted(tiles):
            for d, (dx, dz) in STEP.items():
                n = (x + dx, z + dz)
                if n in tiles or n in src or n in self.cut or not (0 <= n[0] < self.W and 0 <= n[1] < self.H): continue
                # (under a north edge: behind the floor itself, except past its corner where the rock beside it dips
                # (Shoal Cave's ice room): drawn facing south, into the tile, where the camera can see it)
                fx, fz = (0, 1) if d == 'n' else (dx, dz)
                if d in 'ew':
                    i = 3 * (x + (dx > 0)); pts = [(i, 3 * z + k) for k in range(4)]
                else:
                    j = 3 * (z + (dz > 0)); pts = [(3 * x + k, j) for k in range(4)]
                if any(not (0 <= i_ < nxl and 0 <= j_ < nzl) for i_, j_ in pts): continue
                P = [(self.LX[i_], self.LZ[j_], self.Hh[j_, i_]) for i_, j_ in pts]
                if any(h > 1e8 for _, _, h in P): continue
                for (xa, za, la), (xb, zb, lb) in zip(P, P[1:]):
                    # the tile's own surface along its edge (a ramp's plane, else its floor height; water: the foot of
                    # its bank, models_cave.water)
                    if heights is not None: sa = sb = heights[(x, z)]   # (a plank chasm's floor: LEVELS.geometry)
                    elif water: sa = sb = self.wy[(x, z)]
                    else: sa, sb = self.surface_y((x, z), min(max(xa, self.lx(x)), self.lx(x + 1) - 1e-6), min(max(za, self.lz(z)), self.lz(z + 1) - 1e-6)), \
                                   self.surface_y((x, z), min(max(xb, self.lx(x)), self.lx(x + 1) - 1e-6), min(max(zb, self.lz(z)), self.lz(z + 1) - 1e-6))
                    if la >= sa - 0.01 and lb >= sb - 0.01: continue
                    ba, bb = min(la, sa), min(lb, sb)
                    u0, u1 = (xa + za) / 32, (xb + zb) / 32
                    q = [(C(xa), ba, C(za), u0, ba / 16, e), (C(xb), bb, C(zb), u1, bb / 16, e),
                         (C(xb), sb, C(zb), u1, sb / 16, e), (C(xa), sa, C(za), u0, sa / 16, e)]
                    for tri in ([q[0], q[1], q[2]], [q[0], q[2], q[3]]):
                        if len({(round(v[0], 3), round(v[1], 3), round(v[2], 3)) for v in tri}) < 3: continue   # (a point)
                        (ax_, ay_, az_), (bx_, by_, bz_), (cx_, cy_, cz_) = [v[:3] for v in tri]
                        nx_ = (by_ - ay_) * (cz_ - az_) - (bz_ - az_) * (cy_ - ay_)
                        nz_ = (bx_ - ax_) * (cy_ - ay_) - (by_ - ay_) * (cx_ - ax_)
                        self.m.tri(L['face_mid'], tri if nx_ * fx + nz_ * fz > 0 else [tri[0], tri[2], tri[1]])   # (facing out)

    # ---- exits: Black 2's cave arch -----------------------------------------------------------------------------
    def arch(self, a):
        L = self.look
        src = L.get('arch_' + a['face']) or L['arch']     # a look may copy Black 2's own arch per wall ("arch_s" ...)
        spec = dict(src, set=L['set'])
        tris = template(spec, OUT)
        # the template's own facing (Victory Road 788's arch is in a south wall; Reversal Mountain 723's in a west wall,
        # "into": "w"): turned to the south-wall convention first
        pre = {'s': lambda x_, z_: (x_, z_), 'n': lambda x_, z_: (-x_, -z_), 'w': lambda x_, z_: (z_, -x_),
               'e': lambda x_, z_: (-z_, x_)}[src.get('into', 's')]
        # textures: "outside" swaps an inside template to the bright version when the warp leads outdoors, "inside"
        # swaps an outside template (copied from an exit to the open air) back to the dark one
        swap = src.get('outside', {}) if a['to_outside'] else src.get('inside', {})
        x, z = a['x'], a['z']
        y = self.fy.get((x - STEP[a['face']][0], z - STEP[a['face']][1]), 0)
        # anchor: the middle of the floor-side edge of the arch tile; the template stands on a south wall (+z = into it)
        ax = {'s': self.lx(x) + 8, 'n': self.lx(x) + 8, 'e': self.lx(x), 'w': self.lx(x + 1)}[a['face']]
        az = {'s': self.lz(z), 'n': self.lz(z + 1), 'e': self.lz(z) + 8, 'w': self.lz(z) + 8}[a['face']]
        rot = {'s': lambda dx, dz: (dx, dz), 'n': lambda dx, dz: (-dx, -dz),
               'e': lambda dx, dz: (dz, -dx), 'w': lambda dx, dz: (-dz, dx)}[a['face']]
        by = src.get('base_y', 0)   # (the Black 2 chunk's floor height in front of the arch: chunk 740's is 32)
        if by: tris = [(mat_, [(vx_, vy_ - by) + tuple(rest_) for vx_, vy_, *rest_ in vs_]) for mat_, vs_ in tris]
        for mat, verts in tris:
            out = []
            # a flat piece lying less than 2 units over the floor (chunk 738's light spill in81_ana02b, 1 unit up) is
            # lifted to 2, Black 2's decal spacing: it z-fought with our floor in melonDS (sweep_caves)
            lift = 2.0 if all(abs(p[1] - verts[0][1]) < 1e-6 for p in verts) and 0 < verts[0][1] < 1.95 else None
            for vx, vy, vz, u, v, c in verts:
                dx, dz = rot(*pre(vx, vz))
                X_, Z_ = ax + dx, az + dz
                # (emerald_polish_caves 2026-10-12, all versions since v16.7: the template reaches 34 units into the
                # wall; at an exit on the map's last rows its tunnel, roof and the outside version's white ground hung
                # past the map's edge as a box over the black - Terra Cave's entrance, Fiery Path: pressed onto the edge)
                X_ = min(max(X_, self.lx(0)), self.lx(self.W)); Z_ = min(max(Z_, self.lz(0)), self.lz(self.H))
                out.append((X_ - 256, (lift if lift is not None else vy) + y, Z_ - 256, u, v, c))
            if len({(round(p[0], 3), round(p[2], 3), round(p[1], 3)) for p in out}) < 3: continue
            self.m.tri(swap.get(mat, mat), out)

    # ---- ladders -------------------------------------------------------------------------------------------------
    def stairs_quad(self, x0, x1, z0, z1, y_south, y_north, color=(1.0, 1.0, 1.0)):
        """Black 2's terrain stairs (d0kaidan_01, Wellspring 486): a ramp, u along the climb (32 units per repeat),
        v across (8 units per repeat)."""
        L = self.look
        C = lambda v: v - 256
        quad = [(C(x0), y_south, C(z1), (z1 - z0) / 32, x0 / 8, color), (C(x1), y_south, C(z1), (z1 - z0) / 32, x1 / 8, color),
                (C(x1), y_north, C(z0), 0, x1 / 8, color), (C(x0), y_north, C(z0), 0, x0 / 8, color)]
        for tri in ([quad[0], quad[1], quad[2]], [quad[0], quad[2], quad[3]]):
            self.m.tri(L['stairs'], tri if up_facing(tri) else [tri[0], tri[2], tri[1]])

    def vwall(self, tex, p0, p1, y0, y1, c0, c1, us=32, face=None):
        """A vertical wall from p0 to p1 (local x, z), y0..y1, colours c0 (bottom) / c1 (top); drawn both ways, or with
        face = (dx, dz) only the side facing that way (the DS culls back faces), none when that is north (the camera
        never sees a north-facing wall; sweep_caves: halves banks' size, chunk 0 of Meteor Falls was over the buffer)."""
        if face == (0, -1): return
        C = lambda v: v - 256
        (xa, za), (xb, zb) = p0, p1
        la, lb = (xa + za) / us, (xb + zb) / us
        q = [(C(xa), y0, C(za), la, 0, (c0,) * 3), (C(xb), y0, C(zb), lb, 0, (c0,) * 3),
             (C(xb), y1, C(zb), lb, 1, (c1,) * 3), (C(xa), y1, C(za), la, 1, (c1,) * 3)]
        fwd = face is None or (-(zb - za) * face[0] + (xb - xa) * face[1]) * (y1 - y0) > 0   # winding (q0,q1,q2)'s normal
        if fwd: self.m.tri(tex, [q[0], q[1], q[2]]); self.m.tri(tex, [q[0], q[2], q[3]])
        if face is None or not fwd: self.m.tri(tex, [q[0], q[2], q[1]]); self.m.tri(tex, [q[0], q[3], q[2]])

    def ladder_down(self, x, z):
        """A 1-tile pit: stairs from the south edge down to -24 at the north edge, walls fading to black."""
        L = self.look
        y = self.fy.get((x, z), 0)
        X0, X1, Z0, Z1 = self.lx(x), self.lx(x + 1), self.lz(z), self.lz(z + 1)
        self.stairs_quad(X0 + 2, X1 - 2, Z0 + 2, Z1, y, y - 24)
        self.vwall(L['face_mid'], (X0 + 2, Z0 + 2), (X0 + 2, Z1), y - 26, y, 0.0, EDGE)
        self.vwall(L['face_mid'], (X1 - 2, Z0 + 2), (X1 - 2, Z1), y - 26, y, 0.0, EDGE)
        self.vwall(L['face_mid'], (X0 + 2, Z0 + 2), (X1 - 2, Z0 + 2), y - 26, y, 0.0, EDGE)
        # floor frame around the pit (2-unit rim) so the hole sits inside the tile
        C = lambda v: v - 256
        fs = L.get('floor_size', 64)
        fc = (L.get('floor_color', 1.0),) * 3
        for a0, b0, a1, b1 in ((X0, Z0, X1, Z0 + 2), (X0, Z0 + 2, X0 + 2, Z1), (X1 - 2, Z0 + 2, X1, Z1)):
            self.m.quad(L['floor'], [(C(a0), y, C(b1), a0 / fs, -b1 / fs), (C(a1), y, C(b1), a1 / fs, -b1 / fs),
                                     (C(a1), y, C(b0), a1 / fs, -b0 / fs), (C(a0), y, C(b0), a0 / fs, -b0 / fs)], color=fc)

    def ladder_up(self, x, z):
        """Stairs climbing north out of the ladder tile into a 1-tile notch of the rock face (when there is rock),
        dark at the top."""
        L = self.look
        y = self.fy.get((x, z), 0)
        X0, X1 = self.lx(x), self.lx(x + 1)
        Zn = self.lz(z)                                   # the ladder tile's north edge
        top = y + 16 * self.tiers
        if (x, z - 1) in self.cut:
            self.ladder_up_notch(x, z, y, X0, X1, Zn)
        else:                                             # no rock behind: a short flight on the tile itself
            self.stairs_quad(X0 + 3, X1 - 3, Zn + 4, Zn + 14, y, y + 6)

    def ladder_up_notch(self, x, z, y, X0, X1, Zn):
        """(emerald_polish_caves 2026-10-12; Emerald first, all versions since v16.7) The up ladder's notch shaped by the rock around it. The
        notch's walls stood 2 tiers high (y .. y + 32) and its black back wall on the rock top 20 units behind, but the
        rock beside a ladder rises by Black 2's profile (16 at the first tier's top, 32 only 3 tiles in): every notch
        stood out of the wall as a box with a black lid (Cave of Origin B1F, Victory Road B1F/B2F, Mirage Tower 3F).
        Now the stairs climb the cut tile to the first tier's top, the side walls fill between the stairs and the rock
        beside them (its own lattice heights on the tile's edges, so they meet), a dark back wall only where the rock
        behind the stairs' top is higher."""
        L = self.look
        C = lambda v: v - 256
        self.stairs_quad(X0, X1, Zn - 16, Zn, y, y + 16, color=(0.6, 0.6, 0.6))
        Hh, LZ = self.Hh, self.LZ
        js = [3 * (z - 1) + k for k in range(4)]             # lattice rows Zn - 16 .. Zn (the cut tile)
        stair = lambda Z: y + (Zn - Z)                        # the stairs' surface: 16 over 16 units
        for i in (3 * x, 3 * (x + 1)):
            X = self.LX[i]
            for ja, jb in zip(js, js[1:]):
                za, zb = LZ[ja], LZ[jb]
                ha, hb = Hh[ja, i], Hh[jb, i]
                if max(ha, hb) > 1e8: continue
                sa, sb = stair(za), stair(zb)
                if max(abs(ha - sa), abs(hb - sb)) < 0.25: continue
                lo_a, hi_a, lo_b, hi_b = min(ha, sa), max(ha, sa), min(hb, sb), max(hb, sb)
                c = (EDGE,) * 3
                q = [(C(X), lo_a, C(za), za / 32, 0, c), (C(X), lo_b, C(zb), zb / 32, 0, c),
                     (C(X), hi_b, C(zb), zb / 32, (hi_b - lo_b) / 16, c), (C(X), hi_a, C(za), za / 32, (hi_a - lo_a) / 16, c)]
                for tri in ([q[0], q[1], q[2]], [q[0], q[2], q[3]], [q[0], q[2], q[1]], [q[0], q[3], q[2]]):
                    if len({(round(v[1], 3), round(v[2], 3)) for v in tri}) == 3: self.m.tri(L['face_mid'], tri)   # (no slivers)
        jb = js[0]                                            # the rock behind the stairs' top (Zn - 16)
        hback = max(Hh[jb, 3 * x], Hh[jb, 3 * x + 1], Hh[jb, 3 * x + 2], Hh[jb, 3 * (x + 1)])
        if y + 16 + 0.25 < hback < 1e8:
            self.vwall(L['rim'], (X0, Zn - 16), (X1, Zn - 16), y + 16, hback, 0.0, 0.0)

    # ---- decals --------------------------------------------------------------------------------------------------
    def decals(self, floor_tiles):
        """Black 2's dirt patches on the floor (d0yuka_op1 32x32, op2 16x16, 2 units above it: chunk 486) and moss on
        rock tops (d0koke01, 3 above), at hashed positions so every build is the same."""
        L = self.look
        C = lambda v: v - 256
        def hit(x, z, salt, p):
            h = hashlib.md5(f'{self.name}:{x}:{z}:{salt}'.encode()).digest()
            return h[0] / 256 < p, (h[1] % 8) - 4, (h[2] % 8) - 4
        # one decal per tile, none in front of an arch (its template's tunnel floor lies on the tiles before it): two
        # decals at one height on one tile, or a decal on an arch's floor, z-fought in melonDS (sweep_caves)
        taken = {(a['x'] + i, a['z'] + j) for a in self.arches for i in range(-3, 4) for j in range(-3, 4)}
        for name, size, p in L.get('decals', []):
            n = size // 16
            for (x, z) in sorted(floor_tiles):
                if self.kind[z][x] != 'floor' or self.special.get((x, z)) or (x, z) in self.wall_dirs: continue
                if any((x + a, z + b) not in floor_tiles or self.kind[z + b][x + a] != 'floor' or self.fy.get((x + a, z + b)) != self.fy[(x, z)]
                       or self.special.get((x + a, z + b)) for a in range(n) for b in range(n)): continue
                ok, jx, jz = hit(x, z, name, p)
                if not ok: continue
                if any((x + a, z + b) in taken for a in range(n) for b in range(n)): continue
                taken |= {(x + a, z + b) for a in range(n) for b in range(n)}
                y = self.fy[(x, z)] + 2
                X0, Z0 = self.lx(x), self.lz(z)
                X1, Z1 = X0 + size, Z0 + size
                self.m.quad(name, [(C(X0), y, C(Z1), 0, 0), (C(X1), y, C(Z1), 1, 0), (C(X1), y, C(Z0), 1, 1), (C(X0), y, C(Z0), 0, 1)])

    # ---- cracked floors -------------------------------------------------------------------------------------------
    def cracked_floor(self):
        """Sapphire's cracked floor / hole tiles (MB_CRACKED_FLOOR 0xD2, MB_CRACKED_FLOOR_HOLE 0x66): Black 2 has no
        cracked floor, so they are marked with the look's rubble texture ("cracked": [texture, units per repeat];
        Wellspring's set has Clay Tunnel's pebbles d29_gake3) tiled over them 2 units above the floor, as Black 2's
        own floor decals (d0yuka_op1, chunk 486)."""
        L = self.look
        if not L.get('cracked'): return
        tex, size = L['cracked']
        C = lambda v: v - 256
        tiles = sorted(t for t, s_ in self.special.items() if s_ in ('cracked', 'hole'))
        for x, z in tiles:
            y = self.fy.get((x, z), 0) + 2
            X0, X1, Z0, Z1 = self.lx(x), self.lx(x + 1), self.lz(z), self.lz(z + 1)
            self.m.quad(tex, [(C(X0), y, C(Z1), X0 / size, -Z1 / size), (C(X1), y, C(Z1), X1 / size, -Z1 / size),
                              (C(X1), y, C(Z0), X1 / size, -Z0 / size), (C(X0), y, C(Z0), X0 / size, -Z0 / size)])

    # ---- rocks drawn in the terrain (Reversal Mountain) ---------------------------------------------------------
    def rock_sprites(self):
        """Looks whose Black 2 cave draws its loose rocks in the terrain, not as building models (Reversal Mountain
        723: a slanted in81_drock1 quad, the 2x2 ones with an in81_drock2 shadow): the look's "rock_sprites"
        {"1": template (one tile, anchored at the tile centre), "2": template (2x2, anchored at the square's centre)}
        are copied onto Sapphire's boulder tiles like the drock models (2x2 squares first)."""
        L = self.look
        spec = L['rock_sprites']
        bould = {(x, z) for z in range(self.H) for x in range(self.W) if self.kind[z][x] == 'boulder'}
        def put(key, px, pz, y):
            for mat, verts in template(dict(spec[key], set=L['set']), OUT):
                self.m.tri(mat, [(px + vx - 256, vy + y, pz + vz - 256, u, v, c) for vx, vy, vz, u, v, c in verts])
        if '2' in spec:
            for (x, z) in sorted(bould):
                sq = [(x, z), (x + 1, z), (x, z + 1), (x + 1, z + 1)]
                if all(t in bould for t in sq):
                    put('2', self.lx(x + 1), self.lz(z + 1), self.fy.get((x, z), 0)); bould -= set(sq)
        for (x, z) in sorted(bould):
            put('1', self.lx(x) + 8, self.lz(z) + 8, self.fy.get((x, z), 0))

# ------------------------------------------------------------------------------------------------ helpers
class _ClipModel:
    """A model proxy that keeps only the part of each triangle on one side of a vertical plane (axis 0 = x, 2 = z, at
    local units `at`, keep the side beyond it when `above`), as rock beside an arch's tunnel (Cave.rock_cells)."""
    def __init__(self, m, axis, at, above):
        self.real, self.axis, self.at, self.above = m, axis, at - 256, above
    def tri(self, mat, verts, color=(1.0, 1.0, 1.0)):
        from models_interior import _clip
        poly = [tuple(v[:5]) + (tuple(v[5]) if len(v) > 5 else color,) for v in verts]
        poly = _clip(poly, self.axis, self.at, not self.above)
        for k in range(1, len(poly) - 1):
            t = [poly[0], poly[k], poly[k + 1]]
            if abs((t[1][0] - t[0][0]) * (t[2][2] - t[0][2]) - (t[1][2] - t[0][2]) * (t[2][0] - t[0][0])) < 1e-6 and \
               max(abs(t[1][1] - t[0][1]), abs(t[2][1] - t[0][1])) < 1e-6: continue          # (a sliver)
            self.real.tri(mat, t)
    def quad(self, mat, verts, color=(1.0, 1.0, 1.0)):
        a, b, c, d = verts
        self.tri(mat, [a, b, c], color); self.tri(mat, [a, c, d], color)

def key_h(key):
    if key[0] == 'face': return key[1:5]
    if key[0] == 'rim': return key[5:9]
    return (key[1],) * 4

def up_facing(tri):
    """Whether a triangle is counter-clockwise seen from above (its normal points up), as the DAE writer winds."""
    (x0, _, z0), (x1, _, z1), (x2, _, z2) = [(v[0], v[1], v[2]) for v in tri]
    return (z1 - z0) * (x2 - x0) - (x1 - x0) * (z2 - z0) >= 0

def rects(tiles):
    """Greedy rectangles (x0, z0, x1, z1 inclusive) covering a set of tiles."""
    tiles = set(tiles); out = []
    for z, x in sorted((z, x) for x, z in tiles):
        if (x, z) not in tiles: continue
        x1 = x
        while (x1 + 1, z) in tiles: x1 += 1
        z1 = z
        while all((a, z1 + 1) in tiles for a in range(x, x1 + 1)): z1 += 1
        for a in range(x, x1 + 1):
            for b in range(z, z1 + 1): tiles.discard((a, b))
        out.append((x, z, x1, z1))
    return out

# ------------------------------------------------------------------------------------------------ models, collision
def cave_placements(cave):
    """Black 2's loose cave rocks on Sapphire's boulder tiles: drock01 (2x2, Black 2 puts it on a tile corner) where
    four boulder tiles form a square, drock02 (1x1, tile centre) on the rest; [(chunk index, record, model info)]."""
    L = cave.look
    if not L.get('rock1'): return [], []
    models = pack_models(L['pack'])
    bould = {(x, z) for z in range(cave.H) for x in range(cave.W) if cave.kind[z][x] == 'boulder'}
    out, used = [], {}
    def put(name, px, pz, y):
        res = models[name][0]
        ci = min(max(int(px // 512), 0), cave.mw - 1); cj = min(max(int(pz // 512), 0), cave.mh - 1)
        out.append((cj * cave.mw + ci, struct.pack('<iiiH', round((px - 256 - 512 * ci) * 4096), round(y * 4096),
                    round(-(pz - 256 - 512 * cj) * 4096), 0) + bytes([res >> 8, res & 0xFF]), (px - 256, y, pz - 256, name)))
        used[res] = dict(res=res, name=name, pack=L['pack'])
    if L.get('rock2'):
        for (x, z) in sorted(bould):
            sq = [(x, z), (x + 1, z), (x, z + 1), (x + 1, z + 1)]
            if all(t in bould for t in sq):
                put(L['rock2'], cave.lx(x + 1), cave.lz(z + 1), cave.fy.get((x, z), 0))
                bould -= set(sq)
    for (x, z) in sorted(bould):
        put(L['rock1'], cave.lx(x) + 8, cave.lz(z) + 8, cave.fy.get((x, z), 0))
    return out, list(used.values())

def centre_uv(m, sizes=None):
    """Each material's texture coordinates in one chunk model moved by whole repeats so that they centre on 0 (the
    textures repeat: nothing changes on screen). The DS stores them as signed 16-bit 1/16 texels (+-2048 texels): the
    builder's coordinates grow with the distance from chunk 0's corner, and a face straddling 2048 texels in a far
    chunk wrapped at one vertex and drew a smear (Underwater1 chunk 7's coral at 2240 texels; sweep_caves). A copy of
    the model is returned; terrain_all.dae keeps the original coordinates.
    sizes {texture: (w, h)} (Emerald caves only, emerald_polish_caves 2026-10-12): after that, a triangle with a vertex
    still past +-2048 texels is moved on its own by whole repeats to near 0 (dae.py writes every texture WRAP/WRAP, one
    index per vertex). Face u runs +x on north walls and -x on south walls, so a chunk 1,500+ units from chunk 0's corner
    (the Desert Underpass's chunks 3-4) holds u from -2400 to +2300 texels and no single shift fits it: 18 smeared faces."""
    out = Model(m.name)
    for mat, tris in m.tris.items():
        us = [v[3] for t in tris for v in t]; vs = [v[4] for t in tris for v in t]
        ku, kv = round(sum(us) / len(us)), round(sum(vs) / len(vs))
        out.tris[mat] = [[(x, y, z, u - ku, v - kv, c) for x, y, z, u, v, c in t] for t in tris] if (ku or kv) else tris
        if sizes and mat in sizes:
            w, h = sizes[mat]
            far = lambda t: any(abs(v[3] * w) >= 2047 or abs(v[4] * h) >= 2047 for v in t)
            fix = lambda t: (lambda a, b: [(x, y, z, u - a, v - b, c) for x, y, z, u, v, c in t])(
                round(sum(v[3] for v in t) / 3), round(sum(v[4] for v in t) / 3))
            if any(far(t) for t in out.tris[mat]):
                out.tris[mat] = [fix(t) if far(t) else t for t in out.tris[mat]]
    return out

def flat_record(y):
    if y == 0: return 3                                   # MAP_HEIGHT_OFFSET_TABLE[3] = 0 (models_interior's cells)
    from terrain.heights import flat_index
    return flat_index(y)

def cave_collision(cave):
    """Collision cells (u16 0, u16 height index, u16 class, u16 flags) per zone tile, as Black 2's caves: walkable
    0x0a/0x84 (cave floor; flags bit 2 = wild encounters, ov036 FieldEncount_DecideTypeByTerrain) or 0x0a/0x80 where
    Sapphire has no encounters, ledges 0x72-0x75 / flags 1, one-sided walls 0x51-0x58, everything else 0x01/0x81."""
    sm = cave.sm
    cells = {}
    for z in range(cave.H):
        for x in range(cave.W):
            k = cave.kind[z][x]; y = cave.fy.get((x, z), 0)
            zx, zz = cave.ox + x, cave.oz + z
            if k == 'ledge':
                cells[(zx, zz)] = (0, flat_record(y), LEDGE_CLASS[cave.ledge_dir[(x, z)]], 0x1)
            elif k == 'water':                           # Wellspring's cave water: 0x3f / 0x16 (0x12 without encounters)
                b_ = sm['beh'][z][x]
                cls, fl = (0x40, 0x13) if b_ == MB_WATERFALL else (0x3F, 0x16 if b_ in SURF_ENC else 0x12)
                cells[(zx, zz)] = (0, flat_record(cave.wy[(x, z)]), cls, fl)
            elif (x, z) in cave.ramps:                   # a slope tile (heights.py's plane records)
                from terrain.heights import plane_record, SLOPES
                side, lo, hi = cave.ramps[(x, z)]
                a, b = plane_record(SLOPES[(side, round(hi - lo))], (zx % 32) * 16 + 8 - 256, (lo + hi) / 2, (zz % 32) * 16 + 8 - 256)
                # wild encounters as on Sapphire's tile (its stairs are MB_CAVE 0x08); Black 2's own sloped floor cells
                # carry 0x84 too (Reversal Mountain, zone 539, chunk 723: plane record + 0x0a/0x84) (wild_tables 2026-10-08)
                enc = sm['beh'][z][x] in ENCOUNTER_BEH and not cave.special.get((x, z))
                cells[(zx, zz)] = (a, b, 0x0A, 0x84 if enc else 0x80)
            elif sm['walk'][z][x] and k in ('floor', 'pit'):
                enc = sm['beh'][z][x] in ENCOUNTER_BEH and not cave.special.get((x, z))
                sides = set(cave.wall_dirs.get((x, z), '')) | cave.level_walls.get((x, z), set())
                key = ''.join(sorted(sides, key='nsew'.index))
                cls = WALL_CLASS.get(key, 0x0A) if sides else 0x0A
                if sides and key not in WALL_CLASS: cave.notes.append(f'({x},{z}): walls {key} have no Black 2 class (one per tile: e/w/n/s/ne/nw/se/sw)')
                cells[(zx, zz)] = (0, flat_record(y), cls, 0x84 if enc else 0x80)
    if MISC.active(cave.r): MISC.collision(cave, cells, flat_record)   # shoal / ice cells (caves_misc)
    if UW.active(cave.r): UW.collision(cave, cells, flat_record)       # swimmable cells (dive agent)
    cells1 = (LEVELS.collision(cave, cells, flat_record, SURF_ENC, land_enc=lambda t: sm['beh'][t[1]][t[0]] in ENCOUNTER_BEH
                               and not cave.special.get(t)) if LEVELS.active(cave.r) else None)   # caves_east (+ wild_tables)
    near = {}
    for (x, z), y in cave.fy.items(): near[(cave.ox + x, cave.oz + z)] = y
    out = []
    for cj in range(cave.mh):
        for ci in range(cave.mw):
            per = bytearray(struct.pack('<HH', 32, 32))
            for zz in range(32 * cj, 32 * cj + 32):
                for zx in range(32 * ci, 32 * ci + 32):
                    if (zx, zz) in cells:
                        a, idx, cls, fl = cells[(zx, zz)]
                        per += struct.pack('<HHHH', a, idx, cls, fl)
                    else:
                        per += struct.pack('<HHHH', 0, flat_record(near.get((zx, zz), 0)), 1, 0x81)
            out.append(bytes(per))
    cave.walk_tiles = {t for t, c in cells.items() if c[2] not in LEDGE_CLASS.values()}
    cave.coll1 = LEVELS.serialize(cave, cells1, near, flat_record) if cells1 else None   # second layer: bridges
    return out

def spot_y(cave, s):
    """{"y": height} of a warp spot on a raised level (warps fire within 2 units of their y): the floor the player
    stands on (the arch's floor-side tile, the ladder tile); {} at height 0, so level-less caves are unchanged."""
    x, z = s['tiles'][0]
    y = cave.fy.get((x, z), 0)
    if s.get('kind') == 'door' and (x, z) not in cave.fy:
        y = cave.fy.get((x, z + 1), 0)  # a doorway (its tile is the arch): the floor in front of it (caves_east)
        if (x, z + 1) in cave.wy and 0 <= z + 1 < cave.H and cave.kind[z + 1][x] == 'water':
            y = cave.wy[(x, z + 1)]     # ... or the water in front of it, surfed into (Seafloor Cavern Room6; sweep_caves)
    if (x, z) in cave.wy and 0 <= z < cave.H and 0 <= x < cave.W and cave.kind[z][x] == 'water':
        y = cave.wy[(x, z)]       # a warp the player surfs into (Scorched Slab): the water's height (caves_east)
    y = MISC.approach_y(cave, (x, z + 1) if s.get('kind') == 'door' and (x, z) not in cave.fy else (x, z), y)   # a shoal (caves_misc)
    return {'y': y} if y else {}

def cave_camera(cave):
    """Camera target box (a/1/0/9, world units): Black 2's caves let the camera follow over the whole matrix and a
    little past it (Victory Road 591: -8..520 x -40..568 for one chunk; Wellspring 324: 8..600 x -104..536)."""
    return [-8, 512 * cave.mw + 8, -40, 512 * cave.mh + 56]

# ------------------------------------------------------------------------------------------------ output
def build(name, out_root=OUT, recipe=None):
    import models_interior as MI
    cave = Cave(name, recipe)
    out = os.path.join(out_root, name)
    os.makedirs(out, exist_ok=True)
    m = cave.build_terrain()
    L = cave.look
    tex_set = lambda t: L.get('tex_sets', {}).get(t, L['set'])        # (dive agent: a look may borrow textures)
    for mat in m.tris:
        images = set_images(tex_set(mat))
        assert mat in images, f'{name}: texture {mat} is not in map texture set {tex_set(mat)}'
        images[mat].save(os.path.join(out, mat + '.png'))
    big = cave.mw * cave.mh > 1
    parts = MI.split_chunks(m, cave.mw, cave.mh) if big else [m]
    if MIST.active(cave): parts = MIST.apron(cave, parts)   # mist caves: the void past the matrix (underwater_polish)
    assert parts[0] is not None, f'{name}: chunk 0 of the matrix is empty (move the map with "origin")'
    sizes = ({t: set_images(tex_set(t))[t].size for t in m.tris} if getattr(cave, 'emerald', False) else None)   # (Emerald only)
    parts = [centre_uv(p_, sizes) if p_ is not None else None for p_ in parts]
    parts[0].write(os.path.join(out, 'terrain.dae'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in m.tris))
    recs, models = cave_placements(cave)
    chunk_pl = []
    for k in range(cave.mw * cave.mh):
        mine = [r for c, r, _ in recs if c == k]
        assert len(mine) <= 32, f'{name}: chunk {k} has {len(mine)} rock models, Black 2 allows 32 (set "boulder_models": false)'
        chunk_pl.append(struct.pack('<I', len(mine)) + b''.join(mine))
    coll = cave_collision(cave)
    open(os.path.join(out, 'placements.bin'), 'wb').write(chunk_pl[0])
    open(os.path.join(out, 'collision.per'), 'wb').write(coll[0])
    extra = {}
    if big:
        m.write(os.path.join(out, 'terrain_all.dae'))
        chunks, todo = [], []
        for k, part in enumerate(parts):
            if k == 0:
                chunks.append(dict(terrain='terrain.nsbmd', collision='collision.per', placements='placements.bin')); continue
            walkable = any(coll[k][4 + 8 * i + 4] != 1 for i in range(1024))
            if part is None and not walkable: chunks.append(None); continue
            if part is None:
                part = Model(f'{name}_c{k}')
                part.quad(L['rim'], [(-1, -40, 1, 0, 0), (1, -40, 1, 1, 0), (1, -40, -1, 1, 1), (-1, -40, -1, 0, 1)], color=(0, 0, 0))
            part.write(os.path.join(out, f'terrain_c{k}.dae')); todo.append(f'terrain_c{k}')
            open(os.path.join(out, f'collision_c{k}.per'), 'wb').write(coll[k])
            open(os.path.join(out, f'placements_c{k}.bin'), 'wb').write(chunk_pl[k])
            chunks.append(dict(terrain=f'terrain_c{k}.nsbmd', collision=f'collision_c{k}.per', placements=f'placements_c{k}.bin'))
        MI.convert_chunks(out, todo)
        extra = dict(matrix=[cave.mw, cave.mh], chunks=chunks)
    first_exit = next((s for s in cave.spots if s['kind'] in ('exit', 'door')), None)
    fly = ([cave.ox + first_exit['tiles'][0][0], cave.oz + first_exit['tiles'][0][1]] if first_exit else
           [cave.ox + cave.W // 2, cave.oz + cave.H // 2])
    meta = dict(name=name, map=cave.sm['name'], cave=True, look=cave.look_name, area=L['area'], origin=[cave.ox, cave.oz],
                size=[cave.W, cave.H], terrain='terrain.nsbmd', collision='collision.per', placements='placements.bin',
                map_textures={t: tex_set(t) for t in m.tris}, models=models, camera=cave_camera(cave),
                warp_spots=[dict({k: v for k, v in s.items() if k != 'index'}, **spot_y(cave, s)) for s in cave.spots], fly=fly,
                ladders={f'{x},{z}': w for (x, z), w in cave.ladders.items()},
                cracked=sorted([list(t) for t, s in cave.special.items() if s in ('cracked', 'hole')]),
                dark=bool(cave.sm['json'].get('requires_flash')),
                furniture=[dict(m=n, pos=[px, y, pz], rot=0) for _, _, (px, y, pz, n) in recs],
                notes=cave.notes, **extra)
    LEVELS.write_layer1(cave, out, meta)                   # collision1*.per: walk-under bridges ('GC' chunks)
    json.dump(meta, open(os.path.join(out, 'room.json'), 'w'), indent=1)
    return meta, sum(len(t) for t in m.tris.values())

def preview(name, spots=None, out_root=OUT):
    """Software render (preview_interior's rasteriser) of a built cave: the whole cave from above and game-like
    views (camera ~45 degrees from the south) at the given Sapphire tiles (default: every warp tile) ->
    <out>/<name>/preview.png."""
    import preview_interior as pv
    from PIL import Image
    d = os.path.join(out_root, name)
    meta = json.load(open(os.path.join(d, 'room.json')))
    dae = os.path.join(d, 'terrain_all.dae' if os.path.exists(os.path.join(d, 'terrain_all.dae')) else 'terrain.dae')
    parts = pv.parse(dae)
    pv.OUT = out_root
    pack = json.load(open(os.path.join(LAYOUTS, '_looks.json')))[meta['look']].get('pack')
    res = {mm['name']: mm['res'] for mm in meta['models']}
    for f in meta['furniture']:
        parts += pv.placed(pv.furniture_parts(res[f['m']], pack), f['pos'], f['rot'])
    ox, oz = meta['origin']; W, H = meta['size']
    pts = spots or [tuple(s['tiles'][0]) for s in meta['warp_spots']]
    views = []
    for sx, sz in pts:
        x, z = (ox + sx) * 16 + 8 - 256, (oz + sz) * 16 + 8 - 256
        views.append(pv.render(parts, eye=(x, 230, z + 200), target=(x, 0, z), fov=40, W=384, H=288))
    cx, cz = (ox + W / 2) * 16 - 256, (oz + H / 2) * 16 - 256
    span = max(W, H) * 16
    top = pv.render(parts, eye=(cx, span * 1.3, cz + span * 0.55), target=(cx, 0, cz + span * 0.05), fov=50, W=768, H=576)
    cols = 2
    rows = (len(views) + cols - 1) // cols
    sheet = Image.new('RGB', (768 + 384 * cols, max(576, 288 * rows)))
    sheet.paste(top, (0, 0))
    for i, v in enumerate(views): sheet.paste(v, (768 + 384 * (i % cols), 288 * (i // cols)))
    p = os.path.join(d, 'preview.png'); sheet.save(p)
    return p

def main(names):
    if names and names[0] == '--preview':
        for n in names[1:]: print(preview(n))
        return
    names = names or sorted(f[:-5] for f in os.listdir(LAYOUTS) if f.endswith('.json') and not f.startswith('_'))
    for n in names:
        meta, tris = build(n)
        print(f'{n}: {tris} triangles, look {meta["look"]}, matrix {meta.get("matrix", [1, 1])}, '
              f'{len(meta["furniture"])} rocks, warps {[(s["kind"], s["x"], s["z"]) for s in meta["warp_spots"]]} -> {os.path.join(OUT, n)}')

if __name__ == '__main__':
    main(sys.argv[1:])
