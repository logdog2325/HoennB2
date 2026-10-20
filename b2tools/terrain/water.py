"""Hoenn's water: sea, ponds, deep water, currents, waterfalls, shoals, puddles and shore pieces, built the way Black 2
builds its own. notes/TERRAIN_WATER.md has every recipe with its evidence; the short version:

Collision (Black 2's .per records, the user's dump; tile-class code in overlay 36):
- sea 0x3f flags 0x16 (Route 1/13/17, Undella), pond 0x3d flags 0x56 (Route 3, Striaton): both IsTileSurfWater
  (ov036 0x021a2cb0: 0x3d/0x3e/0x3f/0x42/0x43), flag 0x02 = surfable; 8 units below the land next to them
  (Route 3: 0 / -8, Route 1 and 17: -16 / -24, Undella: -80 / -88).
- waterfall 0x40 flags 0x13 (Route 11 chunk 72, Route 14; IsTileWaterfall ov036 0x021a2c10).
- shoals (Sapphire's MB_SHALLOW_WATER): class 0x17 flags 0x10 at the sea's own height (Undella, Route 13, Humilau);
  puddles (MB_PUDDLE, Lavaridge's hot springs): class 0x14 flags 0x40 at ground height (Route 6, Pinwheel Forest).
- deep water (no Dive in Gen 5): surfable sea that looks darker; currents: Black 2's own current classes 0x94-0x97
  (Route 17/18), tested in the emulator (see CURRENT below).
Geometry (chunks dumped with apicula; model units, land at y 0):
- sea: sea_mizu1 twice, a translucent copy (material "sea_mizu1_1", alpha 16/31) 3 below the water's collision
  height over an opaque one 16 below it (Route 1 chunk 2 uses Hoenn's own texture set 3; Undella Bay chunk 247).
- pond: ike01 (alpha 12/31) at the collision height over an opaque mizu_sita2 floor 24 below (Route 3 chunk 15).
- banks: gake1_1 grass lip from the land edge down 8 in half a tile, then shore01 to 12 below (Route 3 chunk 15);
  beaches: wet sand sea_simi.1 sloping into the water, sea_zanami foam over it, a sea_zanami2 band on the water
  (Route 1 chunk 2, Undella Bay chunk 247); around shoals a 1-tile sea_zanami2 band on the sea (Undella Bay).
- shoals: flat sea_asase02 at the water's collision height (Undella Bay chunk 247); puddles: mizutama01 decal laid
  as corner/edge/centre pieces of its one image (Route 6 chunk 53, Pinwheel Forest chunk 21).
- deep water: the dark blue of Undella's dive-spot art (sea_diving) between the two sea layers.
- waterfall: kawa01b sheet, kawa01a side streaks, taki_shibu.1 spray (Route 11 chunk 72); flat until the heights
  module gives the river above it its own level.
Animation: area 2's summer record (3) names SRT 0 and pattern 0. SRT 0 scrolls the materials named ike01,
mizu_sita2, shore01, sea_mizu1, sea_mizu1_1, sea_zanami, sea_zanami2, sea_asase02, sea_gake02, kawa01a, kawa01b
(+ kawa01b_1/_2), ue_grass01; pattern 0 swaps the images of sea_simi.1, kawa_fuchi.1, taki_sakai.1, kawa_nose.1,
taki_shibu.1, hana01.1. Hoenn's water uses those exact names, so it moves with no area-table change.

Which tile is what comes from Sapphire itself (pokeruby blockdata + metatile_attributes.bin + sTileBitAttributes).

dae.py has no material alpha and binds each material to the texture of the same name, so this module hooks
dae.Model.write (once, for every model written while it is enabled): the second sea layer is kept inside material
sea_mizu1 with a marker vertex colour (so heights.py's lift/extend and world.py's texture copy see only real texture
names) and is split out into material sea_mizu1_1 bound to texture sea_mizu1 when the DAE is written; ALPHA
materials get RGBA vertex colours + <transparent opaque="A_ONE"> (CTRMap's importer writes that as the material's
polygon alpha: ike01 -> 12/31, sea_mizu1_1 -> 16/31, checked by converting our .nsbmd back with apicula); the flat
ground under water tiles is cut out at write time, so it also works when heights.py draws the ground.
"""
import os, re, json, struct, shutil, sys, math
from collections import deque, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
POKERUBY = os.path.join(ROOT, 'external', 'pokeruby')
if not any(os.path.abspath(p) == os.path.abspath(os.path.join(ROOT, 'b2tools')) for p in sys.path):
    sys.path.append(os.path.join(ROOT, 'b2tools'))     # (appended: never shadows another folder's module)
import version                     # noqa: E402  (HOENN_VERSION=emerald: Emerald's maps through gba.world_repo)
_EMERALD = version.EMERALD

CLASSES = {'water', 'deep_water', 'current_n', 'current_s', 'current_e', 'current_w', 'waterfall', 'puddle',
           'water_edge'}
SURFACE = {'water', 'deep_water', 'current_n', 'current_s', 'current_e', 'current_w', 'waterfall'}

# texture -> Black 2 map texture set it comes from. All but two are already in Hoenn's set 3 (area 2 summer) and cost
# nothing (hoenn_textures merges only missing ones); sea_asase02 (Route 13 summer, set 67) and sea_diving (Undella
# Bay summer, set 71) add 72 + 160 bytes.
TEXTURES = {t: 3 for t in ('ike01', 'mizu_sita2', 'shore01', 'gake1_1', 'sea_mizu1', 'sea_simi.1', 'sea_zanami',
                           'sea_zanami2', 'sea_jimen', 'kawa01a', 'kawa01b', 'taki_shibu.1', 'mizutama01')}
TEXTURES.update({'sea_asase02': 67, 'sea_diving': 71})
TEXTURES.update({'sea_gake01': 3, 'gake1_0': 3})     # (rock banks under water-entrance cave mouths: in set 3, 0 bytes)
# wrap modes as in Black 2's materials (texImageParam repeat bits of the same materials in chunks 2, 15, 53, 72, 247)
WRAP = {'gake1_1': ('WRAP', 'CLAMP'), 'shore01': ('WRAP', 'CLAMP'), 'sea_simi.1': ('WRAP', 'CLAMP'),
        'sea_zanami2': ('WRAP', 'CLAMP'), 'taki_shibu.1': ('WRAP', 'CLAMP'), 'kawa01a': ('CLAMP', 'WRAP'),
        'sea_diving': ('CLAMP', 'CLAMP'), 'mizutama01': ('CLAMP', 'CLAMP'), 'sea_gake01': ('WRAP', 'CLAMP')}
ALPHA = {'ike01': 12, 'sea_mizu1_1': 16}        # material alpha (0-31): Route 3 chunk 15, Route 1 chunk 2
ALIAS = {'sea_mizu1_1': 'sea_mizu1'}            # material name -> texture (Black 2's second sea layer)
MARK = (1.0, 1.0, 0.9961)                       # vertex colour of triangles that belong to the ALIAS material

# ---- collision records (inclination, height index, class, flags), copied from Black 2's own .per data ----------
H_GROUND, H_WATER = 3, 61                       # height table (overlay 36): index 3 = y 0, index 61 = y -8
SEA = (0, H_WATER, 0x003F, 0x0016)              # Route 1 chunk 2, Route 13 chunk 90, Route 17, Undella Bay
POND = (0, H_WATER, 0x003D, 0x0056)             # Route 3 chunks 15/16, Striaton chunk 11
FALL = (0, H_WATER, 0x0040, 0x0013)             # Route 11 chunk 72, Route 14 chunk 95 (IsTileWaterfall: class 0x40)
WATER_SOLID = (0, H_WATER, 0x0001, 0x0081)      # unsurfable water: Black 2's wall record, at the water's height
SHOAL = (0, H_WATER, 0x0017, 0x0010)            # walkable shallows at the sea's height: Undella, Route 13, Humilau
PUDDLE = (0, H_GROUND, 0x0014, 0x0040)          # walkable puddle at ground height: Route 6 chunk 53, Pinwheel 21
BEACH = (0, H_GROUND, 0x0019, 0x0088)           # beach sand: Undella Town chunk 94, Route 17 chunk 26
SOLID = (0, H_GROUND, 0x0001, 0x0081)
# Currents: Black 2's Route 17/18 sea has classes 0x94-0x97 (flags 0x02, at the sea's height) in one-way lanes next
# to its sea_nagare01 current art. Emulator test (scratch ROM, Route 104's sea turned into each class): a surfer on
# 0x95 is carried west, on 0x96 north, on 0x97 south, one tile after another until the first tile that is not a
# current; 0x94 is east by the lanes' layout (Hoenn has no east currents). The carry does not stop at solid tiles: the
# 0x95 test ended inside the rock tile after the lane. So a current tile whose next tile downstream is not open
# surfable water stays plain sea (the player stops on it, as Sapphire stops you in front of a rock).
# HOENN_WATER_CURRENTS=0 turns them all into plain sea.
CURRENT = {'current_e': 0x94, 'current_w': 0x95, 'current_n': 0x96, 'current_s': 0x97}
FLOW = {'current_e': (1, 0), 'current_w': (-1, 0), 'current_n': (0, -1), 'current_s': (0, 1)}
USE_CURRENTS = os.environ.get('HOENN_WATER_CURRENTS', '1') != '0'

# ---- heights of the layers (model units; land is y 0) -----------------------------------------------------------
Y_WATER = -8                                    # collision height of surfable water and shoals
Y_POND, Y_POND_FLOOR = -8, -32                  # ike01 at the collision height, mizu_sita2 24 below (Route 3)
Y_SEA, Y_SEA_DEEP = -11, -24                    # translucent sea 3 below, opaque sea 16 below (Route 1, Undella)
Y_DIVE = -14                                    # dark dive-spot art between them (Undella Bay: -94 vs -91 / -104)
Y_PUDDLE = 2                                    # Black 2 lays it on the ground (y 0, depth-equal); 1 above flickered in
                                                # melonDS, 2 is Black 2's own decal spacing (flowers)
DIVE_UV = (0.84, 0.78)                          # a texel of sea_diving's dark blue band (08395a)

# ---- Sapphire's tile behaviours ----------------------------------------------------------------------------------
MB_POND, MB_WATERFALL, MB_PUDDLE, MB_SHALLOW, MB_SAND, MB_HOT_SPRING = 0x10, 0x13, 0x16, 0x17, 0x21, 0x28
MB_SHIP_STAIRS = 0x1B     # MB_STAIRS_OUTSIDE_ABANDONED_SHIP: Sapphire counts it as shallow flowing water
                          # (MetatileBehavior_IsShallowFlowingWater); Route 108's landing (terrain/ship.py)
_layouts = _attrs = _surf = _origins = _grids = None
_pos_cache, _fill_cache = {}, {}

def _surf_table():
    """sTileBitAttributes (pokeruby src/metatile_behavior.c): bit 1 = MetatileBehavior_IsSurfableWaterOrUnderwater."""
    src = open(os.path.join(POKERUBY, 'src', 'metatile_behavior.c')).read()
    body = src[src.index('sTileBitAttributes[]'):]
    body = body[:body.index('};')]
    return [m.group(2) == 'TRUE' for m in re.finditer(r'TILE_ATTRIBUTES\((\w+),\s*(\w+),\s*(\w+)\)', body)]

def _tileset_attrs(sym):
    if _EMERALD:                   # (Emerald's world: its own tilesets, through the Emerald view)
        sys.path.insert(0, os.path.join(ROOT, 'converter'))
        from gba import world_repo
        d = open(os.path.join(world_repo(POKERUBY).tileset_dir(sym), 'metatile_attributes.bin'), 'rb').read()
        return struct.unpack(f'<{len(d) // 2}H', d)
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', sym.replace('gTileset_', '')).lower()
    for kind in ('primary', 'secondary'):
        p = os.path.join(POKERUBY, 'data', 'tilesets', kind, name, 'metatile_attributes.bin')
        if os.path.exists(p):
            d = open(p, 'rb').read()
            return struct.unpack(f'<{len(d) // 2}H', d)
    raise FileNotFoundError(sym)

def _load():
    global _layouts, _attrs, _surf, _origins, _grids
    if _origins is not None: return
    _layouts = {l['id']: l for l in json.load(open(os.path.join(POKERUBY, 'data', 'layouts', 'layouts.json')))['layouts']
                if 'id' in l}
    _attrs, _grids, _surf = {}, {}, _surf_table()
    cfg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world.json')))
    lay = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps']
    M = cfg['margin_cells'] * 32
    _origins = {}
    for name, L in lay.items():          # same placement as world.compose
        pad = cfg.get('pad_north', {}).get(name, 0); sx, sz = cfg.get('shift', {}).get(name, [0, 0])
        _origins[name] = (L['tile_x'] + M + sx, L['tile_z'] + M + sz + pad, pad)

def _event_grid(name):
    """_grids/_attrs of a map of another pret decomp (Emerald's event islands), read through converter/gba.py's Repo
    (its layout paths are absolute, its tilesets namespaced 'emerald:gTileset_X'); behaviour numbers are the same.
    HOENN_VERSION=emerald: every map, through the Emerald view (gba.world_repo; a cropped layout's grid row by row)."""
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from gba import Repo, world_repo
    repo = world_repo(POKERUBY) if _EMERALD else Repo(POKERUBY); mj = repo.map_json(name); l = repo.layouts[mj['layout']]
    if _EMERALD:
        g = repo.layout_grid(mj['layout'])[0]
        raw = g.astype('<u2').tobytes()
    else:
        raw = open(os.path.join(POKERUBY, l['blockdata_filepath']), 'rb').read()
    for ts in (l['primary_tileset'], l['secondary_tileset']):
        if ts not in _attrs:
            d = open(os.path.join(repo.tileset_dir(ts), 'metatile_attributes.bin'), 'rb').read()
            _attrs[ts] = struct.unpack(f'<{len(d) // 2}H', d)
    _grids[name] = (struct.unpack(f'<{len(raw) // 2}H', raw), l)

def behaviour(name, wx, wz):
    """Sapphire metatile behaviour of world tile (wx, wz) of map `name` (None if unknown)."""
    _load()
    if name not in _origins: return None
    if name not in _grids:
        if _EMERALD or not os.path.exists(os.path.join(POKERUBY, 'data', 'maps', name, 'map.json')):
            _event_grid(name)            # (an event map of another decomp: data/hoenn_event_maps.json, events agent)
        else:
            mj = json.load(open(os.path.join(POKERUBY, 'data', 'maps', name, 'map.json')))
            l = _layouts[mj['layout']]
            raw = open(os.path.join(POKERUBY, l['blockdata_filepath']), 'rb').read()
            for ts in (l['primary_tileset'], l['secondary_tileset']):
                if ts not in _attrs: _attrs[ts] = _tileset_attrs(ts)
            _grids[name] = (struct.unpack(f'<{len(raw) // 2}H', raw), l)
    grid, l = _grids[name]
    ox, oz, pad = _origins[name]
    x, y = wx - ox, wz - oz
    if y < 0: y = (y + pad) % 2                  # Route 101's padding rows repeat its first two rows
    if not (0 <= x < l['width'] and 0 <= y < l['height']): return None
    m = grid[y * l['width'] + x] & 0x3FF
    a = _attrs[l['primary_tileset']] if m < 512 else _attrs[l['secondary_tileset']]
    i = m if m < 512 else m - 512
    return a[i] & 0xFF if i < len(a) else None

def surfable(beh):
    _load()
    return beh is not None and beh < len(_surf) and _surf[beh]

# ---- what each tile is -------------------------------------------------------------------------------------------
try:                                             # (set once: ground.py is optional)
    import terrain as _terrain
    _ground = next((m for m in _terrain.modules() if m.__name__.endswith('ground')), None)
except Exception:
    _ground = None

def look(world, wx, wz):
    """'pond' | 'sea' | 'deep' | 'fall' | 'current' (water surface, 8 below the land), 'shoal' (walkable shallows at
    the water's height), 'puddle' or 'sand' (drawn on the ground), or None (not water)."""
    e = world.get((wx, wz))
    if e is None:
        return 'sea' if filler(world, wx, wz) else None
    name, cls, walk = e
    if cls in WET_PROPS and not walk:
        return 'sea' if _in_water(world, wx, wz) else None
    hm = sys.modules.get('terrain.heights')                       # (a small sea rock mass: a rock card in the sea)
    if hm is not None and getattr(hm, 'FIELD', None) is not None and (wx, wz) in hm.FIELD.card_tiles(): return 'sea'
    if cls not in CLASSES:
        if _ground is not None:                  # a bridge deck or Cycling Road over water: copy the water next to it
            t = _ground.water_under(world, wx, wz)
            if t is not None: return look(world, *t)
        return None
    beh = behaviour(name, wx, wz)
    if cls == 'puddle': return 'shoal' if beh in (MB_SHALLOW, MB_SHIP_STAIRS) else 'puddle'
    if cls == 'water_edge':
        if surfable(beh): return 'sea'
        return {MB_SHALLOW: 'shoal', MB_SAND: 'sand'}.get(beh)
    if cls == 'waterfall': return 'fall'
    if cls == 'deep_water': return 'deep'
    if cls.startswith('current'): return 'current'
    if beh != MB_POND and any(behaviour(name, wx + dx, wz + dz) == MB_POND and (world.get((wx + dx, wz + dz)) or (0, 0))[1]
                              in SURFACE for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
        return 'pond'    # a pond tile with another behaviour (Route 120's MB_ROUTE120_NORTH_BRIDGE_1 under its bridge) drew
                         # as one square of sea in the pond (exterior sweep 2026-10-06)
    return 'pond' if beh == MB_POND else 'sea'

WET_PROPS = {'rock'}         # boulders in the sea (Route 103, 105...): water is drawn under them, their module draws the rock

def _in_water(world, wx, wz):
    """A solid prop tile stands in water when it touches surface water and no walkable land (4-neighbours)."""
    wet = False
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = world.get((wx + dx, wz + dz))
        if n is None: wet = wet or bool(filler(world, wx + dx, wz + dz)); continue
        if n[1] in SURFACE: wet = True
        elif n[2] and n[1] not in WET_PROPS: return False
    return wet

def _positions(world):
    if id(world) not in _pos_cache:
        _pos_cache.clear()
        _pos_cache[id(world)] = {id(v): k for k, v in world.items()}
    return _pos_cache[id(world)]

def collision(cls, tile, cell):
    """Collision record of one of this module's tiles (Black 2's own values, see the table at the top)."""
    wx, wz = _positions(cell.world)[id(tile)]
    r = _collision(cls, tile, wx, wz, cell.world)
    if r is None or r[0][1] != H_WATER: return r
    h = sys.modules.get('terrain.heights')          # heights.py re-heights only ground-level records: water follows
    F = getattr(h, 'FIELD', None) if h else None    # the level it gives the water body (its surface is 8 below)
    y = getattr(F, 'coll_h', {}).get((wx, wz), F.y(wx, wz)) if F is not None else 0   # (a height drawn otherwise
    foot = _fall_foot(cell.world, F, h, wx, wz, r[0], y) if F is not None else None    #  keeps its collision)
    if foot is not None:
        a, _, c, f = r[0]
        return (a, foot, c, f), r[1]
    if not y: return r
    a, _, c, f = r[0]
    return (a, h.flat_index(y + Y_WATER), c, f), r[1]

def _fall_foot(world, F, h, wx, wz, rec, y):
    """(artisan_surf 2026-10-20) Height index for the surf water right below a waterfall's 0x40 row when it stands level
    with the water above the falls, else None. ov036 CheckAutoTileEvents (0x02182890) [code] starts the descent
    (script 10015) only when the surfer's y - the water above the 0x40 row - is HIGHER than the tile 2 ahead (`ble`
    at 0x02182946). Where heights.py levels both rivers by their shores at one height (Battle Frontier East: the
    Palace pond's falls, the way to Artisan Cave B1F; Route 119 north of the Weather Institute bridge) a surfer could
    not go down, which Gen 3 always allows (MB_WATERFALL is a forced south current). That foot tile's collision goes to
    the highest flat height just under the water above (7.85 under 8.00): the descent runs, nothing drawn changes.
    Only the level case: falls whose foot water stands higher than their top (Ever Grande, Route 114's by Meteor Falls)
    are a heights matter, not a small offset."""
    if rec[2] not in (0x3F, 0x3D): return None
    me, up, top = world.get((wx, wz)), world.get((wx, wz - 1)), world.get((wx, wz - 2))
    if me and me[1] == 'waterfall' and me[2]: return None              # (a column tile above the 0x40 row: upper water)
    if not (up and up[1] == 'waterfall' and up[2]): return None       # (the 0x40 row: a column's bottom tile, _collision)
    if not (top and top[1] in SURFACE and top[2]): return None
    ch = getattr(F, 'coll_h', {})
    above = ch.get((wx, wz - 2), F.y(wx, wz - 2)) + Y_WATER
    if abs(y + Y_WATER - above) >= 1: return None
    ny = h.NORMALS[0][1]
    under = [(-d / ny, i) for i, d in enumerate(h.OFFS) if above - 1 < -d / ny < above - 0.05]
    return max(under)[1] if under else None

def _collision(cls, tile, wx, wz, world):
    name, _, walk = tile
    beh = behaviour(name, wx, wz)
    if cls == 'puddle':
        if not walk: return SOLID, '#'
        return (SHOAL, 'p') if beh in (MB_SHALLOW, MB_SHIP_STAIRS) else (PUDDLE, 'p')
    if cls == 'water_edge':
        if not walk: return SOLID, '#'
        if surfable(beh): return SEA, '~'
        if beh == MB_SHALLOW: return SHOAL, 'p'
        if beh == MB_SAND: return BEACH, '.'
        return None                                  # plain walkable ground (world.py's floor record)
    if not walk: return WATER_SOLID, '#'             # Sapphire blocks it (map borders, unsurfable water)
    if cls == 'waterfall':
        # Black 2's waterfall is ONE row of class 0x40 (Route 11 chunk 72, Route 14 chunks 95-98): Waterfall
        # (FieldWaterfallTCB) carries the surfer 2 tiles, over that row onto the water beyond. Sapphire's are columns
        # of 3-8 rows: a surfer carried 2 tiles landed on the next 0x40 tile and stuck there (blocked all round, and A
        # does nothing on a waterfall tile) - Ever Grande's 8-row waterfall, the way to the Pokemon League [test]. So
        # only a column's bottom row is 0x40; the rows above are the water above the falls (outdoor sweep 2026-10-07).
        below = world.get((wx, wz + 1))
        if not (below and below[1] == 'waterfall' and below[2]): return FALL, 'W'
        z = wz - 1
        while (world.get((wx, z)) or (0, None))[1] == 'waterfall': z -= 1
        top = world.get((wx, z))
        return (POND, '~') if top and top[1] in SURFACE and behaviour(top[0], wx, z) == MB_POND else (SEA, '~')
    if beh == MB_POND: return POND, '~'
    if cls in CURRENT and USE_CURRENTS:
        dx, dz = FLOW[cls]
        n = world.get((wx + dx, wz + dz))           # downstream: the carry must end in open water
        if n and n[2] and n[1] in SURFACE and n[1] != 'waterfall' and behaviour(n[0], wx + dx, wz + dz) != MB_POND:
            return (0, H_WATER, CURRENT[cls], 0x0002), '~'     # (map char: navgrid reads 'v' as a ledge)
    return SEA, '~'

# ---- sea outside the maps (world.py asks filler() for tiles that belong to no map) --------------------------------
FILL_RADIUS = 128            # > the 1-cell ring world.py builds around the maps (63 tiles across, 126 corner to corner)

def filler(world, wx, wz):
    """'water' for a tile outside every map whose nearest map tile is surface water (open sea between and around the
    sea routes), else None (world.py's forest). Its collision stays solid: Sapphire's map borders can't be crossed."""
    if id(world) not in _fill_cache:
        _fill_cache.clear()
        _fill_cache[id(world)] = _fill(world)
    return 'water' if (wx, wz) in _fill_cache[id(world)] else None

def _fill(world):
    """Multi-source BFS from every map tile over the tiles outside the maps; each outside tile takes the kind of the
    map tile that reaches it first (within FILL_RADIUS)."""
    wet = {}
    q = deque()
    for k, (name, cls, walk) in world.items():
        x, z = k
        if any((x + dx, z + dz) not in world for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            wet[k] = (cls in SURFACE, 0); q.append(k)
    out = set()
    while q:
        k = q.popleft()
        w, d = wet[k]
        if d >= FILL_RADIUS: continue
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (k[0] + dx, k[1] + dz)
            if n in world or n in wet: continue
            wet[n] = (w, d + 1); q.append(n)
            if w: out.add(n)
    return out

# ---- geometry ----------------------------------------------------------------------------------------------------
HOLE = {'pond', 'sea', 'deep', 'fall', 'current', 'shoal'}     # below the land: the ground over them is cut away
OPEN = {'sea', 'deep', 'current', 'fall'}                     # sea surface (two sea_mizu1 layers)
U = lambda t: t * 16 - 256                       # tile coordinate -> model units (chunk centred on the origin)

# bank profiles: layers of (material, [(t, y, v), ...]) with t = distance into the water tile from the land edge.
# v is the DAE's (image bottom = 0); apicula's glTF dumps show 1 - v.
# Route 3 pond bank (chunk 15): gake1_1 from the edge (y 0) to half a tile (y -8), shore01 on to 3/4 tile (y -12)
BANK = [('gake1_1', [(0.0, 0, 1.0), (0.5, -8, 0.0)]),
        ('shore01', [(0.5, -8, 1.0), (0.75, -12, 0.0)])]
# Undella Bay beach (chunk 247), squeezed into the water tile (Black 2 slopes the last sand tile instead; Hoenn's sand
# tiles stay flat and walkable): wet sand slope, foam over it, sea_zanami2 band on the water
BEACH_BANK = [('sea_simi.1', [(0.0, 0, 1.0), (0.75, -9, 0.0)]),
              ('sea_zanami', [(0.06, 2.5, 1.0), (0.875, -7, 0.66)]),       # (Black 2: from y +1, 1.2 over the wet
              ('sea_zanami2', [(0.75, -7, 1.0), (1.0, -7, 0.0)])]          #  sand; now 2+ along its normal)
# on a shoal or a pond the band would lie 1 unit over their surface (-8): left out there
BEACH_BANK_STILL = BEACH_BANK[:2]
# Undella Bay shoals: a 1-tile sea_zanami2 band on the sea all around them, level with the shallows
SHOAL_BAND = [('sea_zanami2', [(0.0, -7.5, 1.0), (1.0, -7.5, 0.0)])]
SANDY = {'sand', 'sand_patch'}
# under the rock of a cave mouth entered from water (terrain/cave_mouth.py rock_shore; cave_mouths agent 2026-10-07):
# sea - Black 2's rocky waterline (Route 1 chunk 3, the sea cliff's foot: sea_gake01 from 1 over the land at its edge
# to 2 over it 5 units out, then down to the water's collision height 11 units out, v 1 -> 0.69 -> 0); pond - the
# pond bank with the rock lip (gake1_0, as heights.py lips rock tops) instead of the grass one (Black 2's ponds are
# all grass-banked: Route 3 chunks 15/16, Striaton 11)
ROCK_SEA_BANK = [('sea_gake01', [(0.0, 1, 1.0), (0.3125, 2, 0.69), (0.6875, -8, 0.0)])]
ROCK_POND_BANK = [('gake1_0', [(0.0, 0, 1.0), (0.5, -8, 0.0)]), ('shore01', [(0.5, -8, 1.0), (0.75, -12, 0.0)])]

# the ferry piers' straight stone sides (terrain/ground.py pier_tiles): Accumula's stone wall face (t02_kabe01, the
# top 14 of its 64 rows, as the walls' faces) from the pier's edge straight down into the water
PIER_BANK = [('t02_kabe01', [(0.0, 0, 1.0), (0.01, -14, 1 - 14 / 64)])]

def _bank_for(world, wx, wz, water=None):
    """The bank profile where water tile of look `water` meets land tile (wx, wz)."""
    if _ground is not None and hasattr(_ground, 'pier_tile') and _ground.pier_tile(world, wx, wz): return PIER_BANK
    cm = sys.modules.get('terrain.cave_mouth')
    if cm is not None and (wx, wz) in cm.rock_shore(world): return ROCK_SEA_BANK
    # the sea's rock masses (heights.sea_rock_masses) and Dewford's rock corner: the sea bank with the rock lip (as the
    # grass shores' BANK, gake1_0 for gake1_1). Black 2's rocky waterline (sea_gake01) has a ragged clear top row that
    # stands over its own cliff's foot; at the edge of a flat rock top it showed the sea through it (a blue dotted line)
    hm = sys.modules.get('terrain.heights')
    F = getattr(hm, 'FIELD', None) if hm is not None else None
    if F is not None and ((wx, wz) in F.rock_bank or (wx, wz) in F.rock): return ROCK_POND_BANK   # (and every rock
    #   cliff Sapphire draws in rock colours: a grass lip along it showed as mint-green slivers by the sea rocks)
    k = look(world, wx, wz)
    if k in ('sand', 'shoal'): return BEACH_BANK
    e = world.get((wx, wz))
    if e and e[1] in SANDY:
        # a pond meets sand-coloured ground without Sapphire's footprints (MB_SAND: beach sand; else a path, ground.py
        # collision) with the grass bank, as the rest of its rim (Black 2's ponds are all grass-banked), not with a
        # beach's wet-sand slope and foam (small_fixes 2026-10-13, player report: Petalburg's pond under the path showed
        # a raised face of water; also Route 111's pond under the path at (12-13, 105); all three versions)
        if water == 'pond' and behaviour(e[0], wx, wz) != MB_SAND: return BANK
        return BEACH_BANK
    return BANK

class _Geo:
    """Polygons in tile coordinates (fx, fz) of the cell, emitted to the model facing up."""
    def __init__(self, m):
        self.m = m
    def poly(self, mat, pts):
        """pts: [(fx, y, fz, u, v)], a convex polygon; fanned into triangles, wound so the face points up."""
        vs = [(U(fx), y, U(fz), u, v) for fx, y, fz, u, v in pts]
        if len(vs) < 3: return
        (ax, ay, az) = vs[0][:3]
        ny = 0.0
        for i in range(1, len(vs) - 1):        # orientation from the polygon's area normal (y component)
            (px, _, pz), (qx, _, qz) = vs[i][:3], vs[i + 1][:3]
            ny += (pz - az) * (qx - ax) - (px - ax) * (qz - az)
        if abs(ny) < 1e-9: return
        if ny < 0: vs = vs[::-1]
        for i in range(1, len(vs) - 1):
            tri = [vs[0], vs[i], vs[i + 1]]
            if mat in ALIAS: self.m.tri(ALIAS[mat], tri, MARK)        # split out again when written (_write)
            else: self.m.tri(mat, tri)

def _height_of():
    """Tile height from heights.py when it is enabled (its Field, set by height_field()), else None."""
    h = sys.modules.get('terrain.heights')
    F = getattr(h, 'FIELD', None) if h else None
    return F.y if F is not None and hasattr(F, 'y') else None

def draw(m, cell):
    world = cell.world
    X, Z = cell.X, cell.Z
    looks = {}
    for tz in range(-3, 35):
        for tx in range(-3, 35):
            k = look(world, X + tx, Z + tz)
            if k: looks[(tx, tz)] = k
    inside = {p: k for p, k in looks.items() if 0 <= p[0] < 32 and 0 <= p[1] < 32}
    _SEAMS.pop(m.name, None)             # (a model name is reused: chunk_fit's rebuild, other layouts' cells)
    if not inside: return
    g = _Geo(m)
    drawn = {}                           # (material, final height) -> tiles: flat() records them for _seam_layers
    holes = {p for p, k in inside.items() if k in HOLE}
    if holes: _HOLES.setdefault(m.name, set()).update(holes)     # ground over them is cut when the model is written
    wet = lambda p: looks.get(p) in HOLE
    hgt = _height_of()

    # surfaces: one quad per rectangle of tiles (Black 2 draws one big quad per chunk), texture fixed to the world grid;
    # with heights.py, rectangles never span two water levels (its lift raises each triangle by one tile's height)
    H = (lambda p: hgt(X + p[0], Z + p[1])) if hgt else (lambda p: 0)
    # water under a deck lies at the level of the water it continues (a pier standing high over its water: Mr. Briney's
    # jetty on Route 104 is 24 over his cove), not at the deck's own height (world.py lifts by the deck's tile)
    under = {}
    if _ground is not None and hgt:
        for p in looks:          # (the cell's own tiles for its sheets; the ones round it for _seam_layers' reach)
            e = world.get((X + p[0], Z + p[1]))
            if e and e[1] not in CLASSES and _ground.water_under(world, X + p[0], Z + p[1]) is not None:
                lo = [H(n) for n in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1))
                      if looks.get(n) in HOLE and (world.get((X + n[0], Z + n[1])) or (0, 0))[1] in CLASSES]
                if lo and min(lo) < H(p): under[p] = min(lo)        # (the lowest water beside it)
    def flat(mat, tiles, y, rep, uv=None, src=None):
        """src: the water tiles a grown floor came from. Its other tiles (under the banks) lie at the nearest water
        tile's level, not their own: world.py lifts every triangle by the height of its tile, so a floor under a
        bank 16 or 32 units higher stood in the bank, and a view through the water's translucent sheet towards the
        bank missed every opaque layer (black in the game; exterior sweep 2026-10-06, exterior_check.py viewholes)."""
        target, extra = {}, {}
        if src:
            for p in tiles:
                near = [H((p[0] + dx, p[1] + dz)) for dx in range(-2, 3) for dz in range(-2, 3)
                        if (p[0] + dx, p[1] + dz) in src]
                if not near: continue
                lo = min(min(near), H(p))                         # (never above lower land beside it)
                if p not in src: target[p] = lo
                elif lo < H(p): extra[p] = lo        # water beside a lower water body: a second floor at that level
        groups = {}
        for p in tiles:
            own = H(p); groups.setdefault((own, target.get(p, under.get(p, own))), set()).add(p)
        for p, lo in extra.items(): groups.setdefault((H(p), lo), set()).add(p)
        for (own, t), part in groups.items():
            if mat in SEAM_SHEET or mat in SEAM_FLOOR:
                drawn.setdefault((mat, y + t), set()).update(part)    # (final height: seam layers below)
            for x0, z0, x1, z1 in _rects(part):
                c = [uv] * 4 if uv else [(x0 / rep, -z1 / rep), (x1 / rep, -z1 / rep), (x1 / rep, -z0 / rep), (x0 / rep, -z0 / rep)]
                yy = y + t - own                     # (world.py adds `own` back)
                g.poly(mat, [(x0, yy, z1) + c[0], (x1, yy, z1) + c[1], (x1, yy, z0) + c[2], (x0, yy, z0) + c[3]])
    def grow(tiles, r):
        return {(x + dx, z + dz) for x, z in tiles for dx in range(-r, r + 1) for dz in range(-r, r + 1)}
    group = lambda *ks: {p for p in holes if inside[p] in ks}
    pond, sea, deep, fall, shoal = group('pond'), group('sea', 'current'), group('deep'), group('fall'), group('shoal')
    if pond:
        flat('ike01', pond, Y_POND, 2)
        flat('mizu_sita2', grow(pond, 2) - sea - deep - shoal, Y_POND_FLOOR, 8, src=pond)   # reaches under the banks (Route 3)
    if sea or deep or fall or shoal:
        flat('sea_mizu1_1', sea | deep | fall | shoal, Y_SEA, 4)
        # (under deep water too: a view through the sea's upper sheet next to it reached the floor under the deep tile)
        flat('sea_mizu1', grow(sea | fall | shoal | deep, 2) - pond, Y_SEA_DEEP, 4, src=sea | fall | shoal | deep)
    if deep:
        flat('sea_diving', deep, Y_DIVE, 1, uv=DIVE_UV)          # flat dark blue of the dive-spot ring (Undella)
    if shoal:
        # (shallows Sapphire draws as sand - the flats round Route 124/125/127's rocks: Black 2's beach sand at the
        #  shallows' height, the shoal band's foam round them as round the others; overworld_polish 2026-10-08)
        hm = sys.modules.get('terrain.heights'); HFd = getattr(hm, 'FIELD', None) if hm is not None else None
        rocky = (HFd.sea_rock | HFd.card_tiles()) if HFd is not None else set()
        sandy = {p for p in shoal if _ground is not None and any((X + p[0] + dx, Z + p[1] + dz) in rocky for dx, dz in
                                                                 ((1, 0), (-1, 0), (0, 1), (0, -1)))
                 and _ground.sandy_tile(world, X + p[0], Z + p[1])}     # (the sand rings round the rock islands only:
        #                                                                   beside a beach's own slope it showed as dashes)
        flat('sea_asase02', shoal - sandy, Y_WATER, 1)           # shallows at the water's height (Undella, Route 13)
        flat('sea_jimen', sandy, Y_WATER, 1)
    if fall:
        _waterfall(g, fall, looks)
    _puddles(g, {p for p, k in inside.items() if k == 'puddle'}, lambda p: looks.get(p) == 'puddle')
    flat('sea_jimen', {p for p, k in inside.items() if k == 'sand'}, 0, 1)    # sand with water drawn on it (ground_cover)
    T = lambda p: under.get(p, H(p))
    seams = _seam_layers(drawn, looks, H, T, world, X, Z)

    # edges of every water tile: a bank where it meets land (profile of that land), a sea_zanami2 band where open sea
    # meets a shoal. Collinear edges merge into one strip (Black 2's banks are long strips); a strip end next to
    # another edge of the same tile is mitred, and land touching only a corner gets a chamfer (Route 3).
    def edge(p, q):
        """What the edge of water tile p towards neighbour q is: a profile, or None."""
        if not wet(q):
            prof = _bank_for(world, X + q[0], Z + q[1], looks.get(p))
            if prof is ROCK_SEA_BANK and looks.get(p) != 'sea': return ROCK_POND_BANK if looks.get(p) == 'pond' else BANK
            return BEACH_BANK_STILL if prof is BEACH_BANK and looks.get(p) in ('shoal', 'pond') else prof
        if looks.get(q) == 'shoal' and looks.get(p) in OPEN: return SHOAL_BAND
        return None
    segs, banks = {}, []
    def plain_bank(p, q):        # (_bank_seams: water and land on their own, no deck, bridge or road over either)
        e = world.get((X + p[0], Z + p[1]))
        if e is not None and e[1] not in CLASSES and e[1] not in WET_PROPS: return False
        return _ground is None or not hasattr(_ground, 'water_under') or _ground.water_under(world, X + q[0], Z + q[1]) is None
    for (tx, tz) in holes:
        kind = {d: edge((tx, tz), (tx + dx, tz + dz)) for d, (dx, dz) in SIDES.items()}
        for d, (dx, dz) in SIDES.items():
            prof = kind[d]
            if prof is None: continue
            lo, hi = ('W', 'E') if d in 'NS' else ('N', 'S')
            line = {'N': tz, 'S': tz + 1, 'W': tx, 'E': tx + 1}[d]
            a = tx if d in 'NS' else tz
            opp = kind[{'N': 'S', 'S': 'N', 'W': 'E', 'E': 'W'}[d]]
            scale = 0.5 / 0.75 if opp is not None and prof is not SHOAL_BAND else 1.0    # 1-tile channels
            segs.setdefault((d, line, id(prof), scale), []).append([a, a + 1, kind[lo] is not None, kind[hi] is not None, prof])
            if prof is not SHOAL_BAND and prof is not PIER_BANK and plain_bank((tx, tz), (tx + dx, tz + dz)):
                banks.append((d, line, a, scale, (tx, tz), (tx + dx, tz + dz)))
        for cx, cz in ((0, 0), (1, 0), (0, 1), (1, 1)):
            if kind['W' if cx == 0 else 'E'] is not None or kind['N' if cz == 0 else 'S'] is not None: continue
            ex, ez = (-1 if cx == 0 else 1), (-1 if cz == 0 else 1)
            prof = edge((tx, tz), (tx + ex, tz + ez))
            # (a shoal band on one side already covers the whole tile: a band corner over it z-fought, 0 apart;
            # Route 108's bow tile between two diagonal shoals, world_fixes 2026-10-06)
            if prof is SHOAL_BAND and any(v is SHOAL_BAND for v in kind.values()): continue
            if prof is not None: _chamfer(g, tx, tz, cx, cz, prof)
    for (d, line, _, scale), lst in segs.items():
        lst.sort(key=lambda s: s[0])
        merged = [lst[0]]
        for sg in lst[1:]:
            last = merged[-1]
            if sg[0] == last[1] and not last[3] and not sg[2]: last[1], last[3] = sg[1], sg[3]
            else: merged.append(sg)
        for a, b, mlo, mhi, prof in merged:
            _strip(g, d, line, a, b, mlo, mhi, prof, scale)
    for mat, tris in _bank_seams(banks, H, X, Z).items(): seams.setdefault(mat, []).extend(tris)
    if seams: _SEAMS[m.name] = seams     # (added when the model is written: after heights' lift and tjunction.fix)

def ground_cover(cell):
    """Cell tiles whose ground this module draws at ground level itself (beach sand with water drawn on it,
    sea_jimen): world.py leaves its grass out there (no layer 0.25 over the grass: that flickered in melonDS)."""
    world = cell.world
    return {(tx, tz) for tz in range(32) for tx in range(32) if look(world, cell.X + tx, cell.Z + tz) == 'sand'}

SIDES = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}

def _rects(tiles):
    """Cover a set of tiles with rectangles (x0, z0, x1, z1): row runs, stacked while the next row has the same run."""
    rows = {}
    for x, z in tiles: rows.setdefault(z, []).append(x)
    runs = {}
    for z, xs in rows.items():
        xs.sort(); s = xs[0]
        for a, b in zip(xs, xs[1:] + [None]):
            if b != a + 1: runs.setdefault(z, set()).add((s, a + 1)); s = b
    out = []
    for z in sorted(runs):
        for r in sorted(runs[z]):
            z1 = z + 1
            while r in runs.get(z1, ()): runs[z1].discard(r); z1 += 1
            out.append((r[0], z, r[1], z1))
    return out

# ---- seam layers (water_seams 2026-10-19) ---------------------------------------------------------------------------
# Discord 2026-10-19 (Emerald, "Oldale Town"): thin light lines across a pond (Petalburg City's in melonDS; Route
# 102's east pond by Oldale, world tiles x 158-163, z 302-306, the same; all versions; notes/TERRAIN_WATER.md "Water
# seams", which also has the grass slivers over the water: cut_ground_now). The DS (melonDS, hardware) rasterizes every
# polygon from its own whole-pixel edges, so 1-pixel cracks open along edges inside a surface: at T-junctions, and
# even where two polygons share an edge (the ground's under-floor, world.py, cracks 2026-10-18). Through a crack in the
# translucent pond sheet (ike01, alpha 12/31) the light pond floor shows unblended (the light lines); through one in
# an opaque floor (mizu_sita2, sea_mizu1) the sky. That pond also has the cell border x = 160 through it: the two
# cells' sheets meet there with a T-junction tjunction.fix cannot see (it works per cell: (160, 304) is a vertex of
# cell (5, 9) only). So, as the ground has its under-floor:
# - every translucent sheet (ike01, sea_mizu1_1) gets a second sheet of the same material in the same plane: one quad
#   over each connected body of water (its bounding box, reaching SEAM_REACH tiles into the next cell, the diagonal the
#   other way). It shows only where the first sheet has a crack: the DS never blends a translucent pixel over a
#   translucent pixel of the same polygon ID (melonDS PlotTranslucentPixel; GBATEK), and both sheets of a material
#   carry one fixed ID in every chunk (nsbmd_fix.water_materials; CTRMap's writer numbered them by material index,
#   which also blended twice along cell borders);
# - every opaque floor (mizu_sita2, sea_mizu1) gets a second floor SEAM_DROP lower, one quad per body likewise;
# - every line where a bank's top meets the land's ground gets a strip of that ground under it (_bank_seams).
# All of them in pieces at most 4 times as long as wide, cut at half tiles (_square_pieces). And the ground over the
# water is cut before tjunction.fix (cut_ground_now): its fans had left grass slivers over the water, lines DeSmuME
# shows too.
# A bounding box is used only where all its other tiles hide the layer (land at or over the water's own level for a
# sheet; something opaque at least 2 over it for a floor); else (water of another level in the box) the box's tiles
# that do, as column rectangles (flat() lays rows, whose inner edges run along x: these cross them only at points), the
# ones holding the body. The layers are added when the model is written (the write hook below): after
# heights.py's lift (they carry their final heights) and after tjunction.fix (they are not split).
SEAM_SHEET = {'ike01': (Y_POND, 2, ('pond',)), 'sea_mizu1_1': (Y_SEA, 4, ('sea', 'current', 'deep', 'fall', 'shoal'))}
SEAM_FLOOR = {'mizu_sita2': 8, 'sea_mizu1': 4}       # (texture repeat in tiles, as flat())
SEAM_DROP = 4                                        # (the ground's under-floor is 4 under the ground too)
SEAM_REACH = 2
SEAM_ASPECT = 4                                      # (_square_pieces: longest piece for its width)
_SEAMS = {}                                          # model name -> {material: [triangle]} (final model coordinates)
_built = {}                                          # id(world) -> cells world.py builds (_seam_layers)

def _components(tiles):
    left, out = set(tiles), []
    while left:
        stack = [left.pop()]; comp = set(stack)
        while stack:
            x, z = stack.pop()
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in left: left.discard(n); comp.add(n); stack.append(n)
        out.append(comp)
    return out

def _seam_layers(drawn, looks, H, T, world, X, Z):
    """{material: [triangle]} of one cell's seam layers (above): drawn = {(material, final height): tiles} from
    draw()'s flat(); H(p) the land height of cell tile p, T(p) the level of the water there (its surface 8 below)."""
    out = {}
    R = SEAM_REACH
    if id(world) not in _built:                      # (cells world.py builds: map tiles and a ring of one round them)
        _built.clear()
        have = {(x // 32, z // 32) for x, z in world}
        _built[id(world)] = {(cx + dx, cz + dz) for cx, cz in have for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
    built = lambda q: ((X + q[0]) // 32, (Z + q[1]) // 32) in _built[id(world)]   # (no sheet past the world's edge)
    def top(q):                                      # the highest opaque surface at tile q (land, or a water floor)
        k = looks.get(q)
        if k in HOLE: return T(q) + (Y_POND_FLOOR if k == 'pond' else Y_SEA_DEEP)
        return H(q)
    for (mat, y), tiles in sorted(drawn.items()):
        if mat in SEAM_SHEET:
            ys, rep, kinds = SEAM_SHEET[mat]
            lvl, yy = y - ys, y
            # (a neighbour cell's tiles of this body, the water under a deck by its own level: a pier's row in it)
            same = set(tiles) | {q for q, k in looks.items() if k in kinds and not (0 <= q[0] < 32 and 0 <= q[1] < 32)
                                 and -R <= q[0] < 32 + R and -R <= q[1] < 32 + R and T(q) == lvl and built(q)}
            ok = lambda q: q in same or (looks.get(q) not in HOLE and H(q) >= lvl and built(q))
        elif mat in SEAM_FLOOR:
            rep, yy = SEAM_FLOOR[mat], y - SEAM_DROP
            same = {q for q in tiles if built(q)}
            ok = lambda q: q in same or (top(q) >= yy + 2 and built(q))
        else:
            continue
        for comp in _components(same):
            if mat in SEAM_SHEET and not any(0 <= q[0] < 32 and 0 <= q[1] < 32 for q in comp): continue
            x0, x1 = min(q[0] for q in comp), max(q[0] for q in comp) + 1
            z0, z1 = min(q[1] for q in comp), max(q[1] for q in comp) + 1
            box = {(x, z) for x in range(x0, x1) for z in range(z0, z1)}
            valid = {q for q in box if ok(q)}
            if len(valid) == len(box):
                rects = [(x0, z0, x1, z1)]
            else:                                    # (water of another level in the box: Route 119's falls)
                rects = [(a0, b0, a1, b1) for b0, a0, b1, a1 in _rects({(z, x) for x, z in valid})
                         if any((x, z) in comp for x in range(a0, a1) for z in range(b0, b1))]
            for r in rects:
                for a0, b0, a1, b1 in _square_pieces(*r):
                    P = lambda x, z: (U(x), yy, U(z), x / rep, -z / rep, (1.0, 1.0, 1.0))
                    A, B, C, D = P(a1, b1), P(a1, b0), P(a0, b0), P(a0, b1)   # (diagonal A-C: flat()'s quads run D-B)
                    out.setdefault(mat, []).extend([[A, B, C], [A, C, D]])
    return out

def _square_pieces(x0, z0, x1, z1):
    """A seam rectangle in pieces at most SEAM_ASPECT times as long as wide, cut at half tiles: a long thin quad's
    diagonal runs within a pixel of the edges beside it for a long way (a crack in both layers can meet there); a
    stubbier piece's crosses them more steeply, and its own cuts never lie on the sheets' tile-aligned edges."""
    w, h = x1 - x0, z1 - z0
    if max(w, h) <= SEAM_ASPECT * min(w, h) or min(w, h) <= 0: return [(x0, z0, x1, z1)]
    long0, long1, n = (x0, x1, math.ceil(w / h / SEAM_ASPECT)) if w > h else (z0, z1, math.ceil(h / w / SEAM_ASPECT))
    cuts = sorted(c for c in {math.floor(long0 + (long1 - long0) * k / n) + 0.5 for k in range(1, n)} if long0 < c < long1)
    edges = [long0] + cuts + [long1]
    return [(a, z0, b, z1) if w > h else (x0, a, x1, b) for a, b in zip(edges, edges[1:])]

BANK_SEAM = (0.875, 0.125, 6)     # (tiles under the land, tiles under the bank's slope, units under the land)

def _bank_seams(banks, H, X, Z):
    """{material: [triangle]}: a strip of the land's ground under every line where a bank's top meets the ground, or a
    cliff's foot where the land stands higher (banks: (side, line, a, scale, water tile, land tile) per tile edge, from
    draw()). The ground ends on that line and so does the cracks fix's under-floor 4 under it (world.py), so the DS's
    crack along it showed the pond floor or the sea far below. The strip lies 6 under the water's land level (2 under
    that under-floor), from 14 units inside the land (still in the land's own tile) to 2 under the bank's slope (the
    slopes drop 16 a tile, 12 on a beach: still 2+ over it there; a 1-tile channel's squeezed slope: scaled), over the
    water's sheets (8 and 11 under the land) and under everything you see; in pieces at most 4 tiles long, so no
    diagonal runs along the line (_square_pieces)."""
    hm = sys.modules.get('terrain.heights')
    F = getattr(hm, 'FIELD', None) if hm is not None else None
    def ground(q):                                   # the land's ground texture (world.py: HF.material), None: stairs
        w = (X + q[0], Z + q[1])
        if F is None: return 'grass01ax'
        return None if w in getattr(F, 'slope', ()) else getattr(F, 'mat', {}).get(w, 'grass01ax')
    land, under_bank, drop = BANK_SEAM
    runs = {}
    for d, line, a, scale, p, q in banks:
        mat = ground(q)
        if mat is None or H(q) < H(p): continue      # (land under the water's level: no bank top meets it; land over
        #                                               it: the bank's top meets a cliff's foot, the strip lies under it)
        runs.setdefault((d, line, scale, H(p), mat), []).append(a)
    out = {}
    for (d, line, scale, h, mat), xs in runs.items():
        inward = {'N': 1, 'S': -1, 'W': 1, 'E': -1}[d]
        xs.sort(); spans = [[xs[0], xs[0] + 1]]
        for a in xs[1:]:
            if a == spans[-1][1]: spans[-1][1] = a + 1
            else: spans.append([a, a + 1])
        for s0, s1 in [(a, b) for r0, r1 in spans for a, _, b, _ in _square_pieces(r0, 0, r1, land + under_bank)]:
            pts = []                                 # (pieces at most 4 tiles long, cut at half tiles: _square_pieces)
            for s, t in ((s0, -land), (s1, -land), (s1, under_bank * scale), (s0, under_bank * scale)):
                fx, fz = (s, line + inward * t) if d in 'NS' else (line + inward * t, s)
                pts.append((U(fx), h - drop, U(fz), fx / 4, -fz / 4, (1.0, 1.0, 1.0)))     # (ground UVs: build_chunk)
            (ax, _, az), (bx, _, bz), (cx, _, cz) = [v[:3] for v in pts[:3]]
            if (bz - az) * (cx - ax) - (bx - ax) * (cz - az) < 0: pts = pts[::-1]          # (face up, as _Geo.poly)
            out.setdefault(mat, []).extend([[pts[0], pts[1], pts[2]], [pts[0], pts[2], pts[3]]])
    return out

def _strip(g, d, line, a, b, mlo, mhi, prof, scale):
    """Bank along an edge line: each profile layer as quads between consecutive (t, y, v) points, t measured into the
    water from the line; an end next to another edge of the tile is mitred along the diagonal (picture-frame corner)."""
    inward = {'N': 1, 'S': -1, 'W': 1, 'E': -1}[d]
    pt = (lambda s, t: (s, line + inward * t)) if d in 'NS' else (lambda s, t: (line + inward * t, s))
    for mat, pts in prof:
        pts = [(t * scale, y, v) for t, y, v in pts]
        for (t0, y0, v0), (t1, y1, v1) in zip(pts, pts[1:]):
            l0, l1 = a + (t0 if mlo else 0), a + (t1 if mlo else 0)
            h0, h1 = b - (t0 if mhi else 0), b - (t1 if mhi else 0)
            if h0 <= l0 + 1e-6 and h1 <= l1 + 1e-6: continue
            poly = []
            for s, t, y, v in ((l0, t0, y0, v0), (h0, t0, y0, v0), (h1, t1, y1, v1), (l1, t1, y1, v1)):
                fx, fz = pt(s, t)
                poly.append((fx, y, fz, s, v))
            g.poly(mat, _dedupe(poly))

def _chamfer(g, tx, tz, cx, cz, prof):
    """Bank around a land corner that touches the water tile only diagonally: each layer as the band between two
    diagonal lines at distance t0 and t1 from the corner (Route 3 chunk 15)."""
    if prof is PIER_BANK: return                 # (a straight stone side: no chamfer, it would smear the wall's image)
    px, pz = tx + cx, tz + cz
    sx, sz = (1 if cx == 0 else -1), (1 if cz == 0 else -1)
    for mat, pts in prof:
        for (t0, y0, v0), (t1, y1, v1) in zip(pts, pts[1:]):
            poly = [(px + sx * t0, y0, pz, 0.0, v0), (px, y0, pz + sz * t0, 1.0, v0),
                    (px, y1, pz + sz * t1, 1.0, v1), (px + sx * t1, y1, pz, 0.0, v1)]
            g.poly(mat, _dedupe(poly))

def _dedupe(poly):
    out = []
    for p in poly:
        if not out or max(abs(p[0] - out[-1][0]), abs(p[1] - out[-1][1]), abs(p[2] - out[-1][2])) > 1e-6:
            out.append(p)
    if len(out) > 1 and max(abs(out[0][0] - out[-1][0]), abs(out[0][1] - out[-1][1]), abs(out[0][2] - out[-1][2])) < 1e-6:
        out.pop()
    return out

def _waterfall(g, fall, looks):
    """Waterfall tiles, flat for now (Route 11 chunk 72's pieces laid on the water): kawa01b sheet flowing south
    (v falls downstream, scrolled by SRT 0), kawa01a streaks along the sides, taki_shibu.1 spray where it meets the
    water below."""
    for tx, tz in sorted(fall):
        g.poly('kawa01b', [(tx, -7.5, tz + 1, tx, -tz - 1), (tx + 1, -7.5, tz + 1, tx + 1, -tz - 1),
                           (tx + 1, -7.5, tz, tx + 1, -tz), (tx, -7.5, tz, tx, -tz)])
        # (side streaks 2 over the sheet: 0.5 apart they flickered)
        for dx in (-1, 1):
            if looks.get((tx + dx, tz)) == 'fall': continue
            x_out, x_in = (tx, tx + 0.5) if dx < 0 else (tx + 1, tx + 0.5)
            g.poly('kawa01a', [(x_out, -5.5, tz + 1, 0, -tz - 1), (x_in, -5.5, tz + 1, 1, -tz - 1),
                               (x_in, -5.5, tz, 1, -tz), (x_out, -5.5, tz, 0, -tz)])
        if looks.get((tx, tz + 1)) in ('sea', 'pond', 'deep', 'current', 'shoal'):
            g.poly('taki_shibu.1', [(tx, -7, tz + 1.5, tx, 0), (tx + 1, -7, tz + 1.5, tx + 1, 0),
                                    (tx + 1, -7, tz + 1, tx + 1, 1), (tx, -7, tz + 1, tx, 1)])

def _puddles(g, tiles, is_puddle):
    """Puddles as Black 2 lays mizutama01 (Route 6 chunk 53, Pinwheel Forest chunk 21): every tile in four quarters;
    a quarter with no puddle beside it on either side takes the image's rounded top-left corner (image u, t 0-0.47),
    one with puddle on one side the straight rim of the image's right half (u 1 at the rim to 0.53 inside, t 0-0.5
    along it), one inside the puddle the plain middle (0.5, 0.5). Image t runs down, so the DAE's v = 1 - t."""
    for tx, tz in tiles:
        for sx in (0, 1):
            for sz in (0, 1):
                ox, oz = tx + sx, tz + sz                  # the tile corner this quarter touches
                cx, cz = tx + 0.5, tz + 0.5
                h = is_puddle((tx + (1 if sx else -1), tz))
                v = is_puddle((tx, tz + (1 if sz else -1)))
                def uv(x, z):
                    dx, dz = abs(x - ox) / 0.5, abs(z - oz) / 0.5      # 0 at the tile corner, 1 at the tile centre
                    if h and v: u, t = 0.5, 0.5
                    elif not h and not v: u, t = 0.47 * dx, 0.47 * dz
                    elif h: u, t = 1 - 0.47 * dz, 0.5 * dx           # rim along the north/south side
                    else: u, t = 1 - 0.47 * dx, 0.5 * dz             # rim along the west/east side
                    return u, 1 - t
                pts = [(ox, oz), (cx, oz), (cx, cz), (ox, cz)]
                g.poly('mizutama01', [(x, Y_PUDDLE, z) + uv(x, z) for x, z in pts])

# ---- ground cut, second sea layer and material alpha when a model is written --------------------------------------
_HOLES = {}                  # model name -> cell tiles whose ground must go (world.py names a cell's models alike)
GROUND = ('grass01ax', 'gake_michi')     # flat ground textures of build_chunk.ground / ground_heights (4-tile repeat)

def cut_ground_now(m):
    """(water_seams 2026-10-19) The ground cut (_cut_ground) on model m now rather than when it is written: world.py
    write_cell calls it before tjunction.fix. The cut reads each flat ground triangle's tiles by rounding its corners to
    the tile grid, which holds for ground_heights' rectangles but not for the fans tjunction.fix makes of them (centroid
    corners): Route 102's pond kept a ground fan (160,305)-(173,305)-(170,304.67) whose rounded rows were empty, a sliver
    of grass at the land's height over the water, drawn as a thin light line along the lower part's north bank (DeSmuME
    and melonDS). Cut first, the splits also see the real edges round the water."""
    holes = _HOLES.pop(m.name, None)
    if holes: _cut_ground(m, holes)

def _cut_ground(m, holes):
    """Remove the flat ground over water tiles: drop every flat ground triangle that overlaps one and re-lay the dry
    tiles of its block with 1-tile-high quads at the same height (same texture mapping as build_chunk.ground)."""
    for mat in GROUND:
        tris = m.tris.get(mat)
        if not tris: continue
        keep, cut = [], set()
        for t in tris:
            if max(v[1] for v in t) - min(v[1] for v in t) > 1e-6: keep.append(t); continue     # flat ground only
            xs = [(v[0] + 256) / 16 for v in t]; zs = [(v[2] + 256) / 16 for v in t]
            x0, x1, z0, z1 = int(round(min(xs))), int(round(max(xs))), int(round(min(zs))), int(round(max(zs)))
            if any((x, z) in holes for x in range(x0, x1) for z in range(z0, z1)): cut.add((x0, z0, x1, z1, t[0][1]))
            else: keep.append(t)
        m.tris[mat] = keep
        done = set()
        for x0, z0, x1, z1, y in sorted(cut):
            for tz in range(z0, z1):
                xs = [x for x in range(x0, x1) if (x, tz) not in holes and (x, tz, y) not in done]
                done.update((x, tz, y) for x in xs)
                run = []
                for x in xs + [None]:
                    if run and (x is None or x != run[-1] + 1):
                        a, b = run[0], run[-1] + 1
                        m.quad(mat, [(U(a), y, U(tz + 1), a / 4, -(tz + 1) / 4), (U(b), y, U(tz + 1), b / 4, -(tz + 1) / 4),
                                     (U(b), y, U(tz), b / 4, -tz / 4), (U(a), y, U(tz), a / 4, -tz / 4)])
                        run = []
                    if x is not None: run.append(x)
        if not m.tris[mat]: del m.tris[mat]

def _marked(t):
    return all(abs(v[5][2] - MARK[2]) < 1e-6 and abs(v[5][0] - MARK[0]) < 1e-6 for v in t)

def _install_write_hook():
    try:
        import dae
    except ImportError:                          # imported without b2tools on the path (e.g. a texture-only patch)
        return
    if getattr(dae.Model, '_water_hook', False): return
    orig = dae.Model.write
    def write(self, path, wrap=None, double_sided=()):
        holes = _HOLES.get(self.name)
        if holes: _cut_ground(self, holes)
        moved = {}
        for alias, base in ALIAS.items():
            tris = self.tris.get(base)
            if not tris: continue
            mv = [t for t in tris if _marked(t)]
            if not mv: continue
            self.tris[base] = [t for t in tris if not _marked(t)]
            moved[alias] = [[tuple(v[:5]) + ((1.0, 1.0, 1.0),) for v in t] for t in mv]
        if moved:                                    # the alias material right after its base (Black 2's order)
            new = OrderedDict()
            for k, v in self.tris.items():
                if v: new[k] = v
                for a, b in ALIAS.items():
                    if b == k and a in moved: new[a] = moved[a]
            self.tris = new
        added = {}                                   # the seam layers (_seam_layers), for this write only
        for mat, tris in (_SEAMS.get(self.name) or {}).items():
            if self.tris.get(mat): self.tris[mat].extend(tris); added[mat] = len(tris)
        try:
            n = orig(self, path, wrap=wrap, double_sided=double_sided)
            mats = [(k, len(v)) for k, v in self.tris.items()]
            if any(k in ALPHA or k in ALIAS for k, _ in mats): _patch_dae(path, mats)
        finally:
            for mat, k in added.items(): del self.tris[mat][len(self.tris[mat]) - k:]
        return n
    dae.Model.write = write
    dae.Model._water_hook = True

def _patch_dae(path, mats):
    s = open(path).read()
    names = [k for k, _ in mats]
    for alias, base in ALIAS.items():
        if alias not in names: continue
        if f'<image id="{base}">' in s:
            s = s.replace(f'    <image id="{alias}"><init_from>{alias}.png</init_from></image>\n', '')
        else:
            s = s.replace(f'<image id="{alias}"><init_from>{alias}.png</init_from>', f'<image id="{base}"><init_from>{base}.png</init_from>')
            _copy_image(base, os.path.dirname(path))
        i = s.index(f'name="{alias}">\n      <profile_COMMON>')
        j = s.index(f'<init_from>{alias}</init_from>', i)
        s = s[:j] + f'<init_from>{base}</init_from>' + s[j + len(f'<init_from>{alias}</init_from>'):]
    used = [k for k in ALPHA if k in names]
    if used:
        for k in used:
            i = s.index(f'name="{k}">\n      <profile_COMMON>')
            j = s.index('<transparent>', i)
            s = s[:j] + '<transparent opaque="A_ONE">' + s[j + len('<transparent>'):]
        alpha = []
        for k, ntri in mats: alpha += [ALPHA.get(k, 31) / 31] * (3 * ntri)
        mo = re.search(r'<float_array id="colors-array" count="(\d+)">([^<]*)</float_array>', s)
        vals = mo.group(2).split()
        assert len(vals) == 3 * len(alpha), (len(vals), len(alpha))
        fmt = lambda v: f'{v:.4f}'.rstrip('0').rstrip('.') if v != int(v) else str(int(v))
        rgba = ' '.join(f'{vals[3 * i]} {vals[3 * i + 1]} {vals[3 * i + 2]} {fmt(a)}' for i, a in enumerate(alpha))
        s = s[:mo.start()] + f'<float_array id="colors-array" count="{4 * len(alpha)}">{rgba}</float_array>' + s[mo.end():]
        s = s.replace(f'<accessor source="#colors-array" count="{len(alpha)}" stride="3"><param name="R" type="float"/>'
                      f'<param name="G" type="float"/><param name="B" type="float"/></accessor>',
                      f'<accessor source="#colors-array" count="{len(alpha)}" stride="4"><param name="R" type="float"/>'
                      f'<param name="G" type="float"/><param name="B" type="float"/><param name="A" type="float"/></accessor>')
    open(path, 'w').write(s)

def _copy_image(name, out_dir):
    dst = os.path.join(out_dir, name + '.png')
    if os.path.exists(dst): return
    src = os.path.join(ROOT, 'work', 'tex', 'area2', name.replace('.', '_') + '.png')
    if os.path.exists(src): shutil.copy(src, dst); return
    sys.path.insert(0, os.path.join(HERE, '..'))
    import b2files, nsbtx
    files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    for n, img, _ in nsbtx.decode(b2files.map_textures(files, TEXTURES[name])):
        if n == name: img.save(dst); return

_install_write_hook()
