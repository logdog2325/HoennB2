"""Build the Hoenn overworld on one matrix (decision 2026-10-06, notes/RESEARCH_WORLD.md option A).

    python3 world.py            -> work/world/ (cells, world.json); the hoenn_world patch installs it

1. Compose: every map listed in data/hoenn_world.json is placed on one global tile grid at its position from
   data/hoenn_world_layout.json (Sapphire's own connections), plus a margin. 'pad_north' inserts repeated rows above a
   map (Route 101's 12 extra rows); 'shift' moves a map (Littleroot follows Route 101). Plans come from
   data/plans/<Map>.json (converter/plan_map.py).
2. Cells: every 32x32 cell holding built tiles, plus a one-cell ring of forest around them, is built with the same
   geometry recipes as build_chunk.py (notes/GEN5_TERRAIN.md). Tiles that belong to no built map are forest; filler
   trees never cover map tiles and never stand directly south of a walkable map tile (Gen 5's camera).
3. Zones: a cell takes the zone of the map with most tiles in it (ring cells: of their busiest neighbour); every map
   has its own zone on its tiles in other zones' cells (zone_rects). Events use global tile coordinates and go to the
   zone of their tile (zone_of), i.e. their own map's zone.
"""
import os, sys, json, struct, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from dae import Model
import build_chunk as bc
import move_codes as MOVE_CODES
import version          # (HOENN_VERSION=emerald: Emerald's world from pokeemerald's maps, notes/EMERALD.md "Emerald's world")

OUT = version.world_dir()      # HOENN_WORLD_DIR (agents use their own dir), else work/world (work/world_emerald for Emerald)
import terrain
FEATURES = terrain.modules()
_ip = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'hoenn_interiors.json')
INTERIORS = {r['map_id']: r for r in version.load_json(_ip)['rooms'].values()} if os.path.exists(_ip) else {}   # by MAP_ id
HEIGHTS = next((f for f in FEATURES if hasattr(f, 'height_field')), None)   # terrain/heights.py: Hoenn's levels
HF = None                                       # its height field (main()); None = everything at y 0 as before
if HEIGHTS and hasattr(HEIGHTS, '_sapphire_grids') and not getattr(HEIGHTS._sapphire_grids, 'borders', False):
    _grids0 = HEIGHTS._sapphire_grids
    def _grids(maps, cfg):
        """heights.py's Sapphire grids plus a warp-only map's border tiles (compose_group: 'border'), which have
        Sapphire's border block metatile and no elevation (the main matrix's maps have none: unchanged there)."""
        elev, mtile, repo = _grids0(maps, cfg)
        for mp in maps.values():
            for k, v in mp.get('border', {}).items(): elev.setdefault(k, 0); mtile.setdefault(k, v)
        return elev, mtile, repo
    _grids.borders = True
    HEIGHTS._sapphire_grids = _grids

class Cell:
    """What a terrain module sees of one cell (b2tools/terrain/__init__.py)."""
    def __init__(self, cx, cz, world):
        self.cx, self.cz, self.X, self.Z, self.world, self.bc = cx, cz, cx * 32, cz * 32, world, bc
    def get(self, tx, tz):
        return self.world.get((self.X + tx, self.Z + tz))

WATER = {'water', 'deep_water', 'current_n', 'current_s', 'current_e', 'current_w', 'waterfall'}

def load():
    """Config for every connected Hoenn map: data/hoenn_zones.json gives zone/place/type, data/hoenn_world.json
    'maps' holds hand-made settings (door slots, building models, signs, NPCs) that override the defaults.
    'only' (optional list) limits the build to some maps."""
    # (Emerald: data/emerald/<same name>.json deep-merged over them, version.load_json; Sapphire/Ruby: the files as they are)
    cfg = version.load_json(os.path.join(ROOT, 'data', 'hoenn_world.json'))
    lay = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps']
    zones = version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps']
    # town settings from the building groups in use (data/towns/<Map>.json, "group" as in data/buildings/)
    import glob
    sys.path.insert(0, os.path.join(HERE, 'patches'))
    from area2_buildings import groups
    towns = sorted(glob.glob(os.path.join(ROOT, 'data', 'towns', '*.json')))
    if version.EMERALD:                 # (Emerald: data/towns/emerald/<Map>.json over a town's file, or a new map's own)
        towns += [f for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'towns', 'emerald', '*.json')))
                  if not os.path.exists(os.path.join(ROOT, 'data', 'towns', os.path.basename(f)))]
    for f in towns:
        t = version.load_json(f) if version.EMERALD else json.load(open(f))
        if t.get('prop_moves'): t = dict(t, props=moved_props(t.get('props', []), t['prop_moves']))
        if t.get('group') in groups() or t.get('group') == 'standalone':   # (standalone: warp-only maps' own pack)
            name = os.path.basename(f)[:-5]
            mc = cfg['maps'].setdefault(name, {})
            for k, v in t.items():
                if isinstance(v, dict): mc.setdefault(k, {}).update(v)
                elif k != 'group': mc[k] = v
    # generated simple signs/NPCs (converter/gen_map_content.py); hand-made settings win
    cp = os.path.join(ROOT, 'data', 'hoenn_content.json')
    if version.EMERALD:                 # (Emerald: data/emerald/hoenn_content.json in its place, whole: gen_map_content.py's
        cp = version.overlay_file(cp)   # Emerald run, pokeemerald's events and labels; S0-1, notes/EMERALD_STORY.md 2.4.1)
    if os.path.exists(cp):
        for name, c in json.load(open(cp))['maps'].items():
            mc = cfg['maps'].setdefault(name, {})
            for k in ('signs', 'npcs'):
                for label, v in c[k].items(): mc.setdefault(k, {}).setdefault(label, v)
    for name in lay:
        if name not in zones or (cfg.get('only') and name not in cfg['only']): continue
        z = zones[name]
        mc = cfg['maps'].setdefault(name, {})
        mc.setdefault('zone', z['zone'])
        mc.setdefault('kind', 'town' if z['type'] in ('MAP_TYPE_TOWN', 'MAP_TYPE_CITY') else 'route')
        mc.setdefault('floor', 'town' if mc['kind'] == 'town' else 'route')
        mc.setdefault('place', z['place'])
        for k in ('warps', 'buildings', 'signs', 'npcs', 'triggers'): mc.setdefault(k, {})
    # warp-only maps (data/hoenn_standalone.json): out of cfg['maps'] (the main matrix), into cfg['standalone']
    cfg['standalone'] = {}
    for g in standalone_cfg()['groups'].values():
        for name in g['maps']:
            mc = cfg['maps'].pop(name, {})
            if name not in zones: continue
            z = zones[name]
            mc.setdefault('zone', z['zone'])
            mc.setdefault('kind', 'town' if z['type'] in ('MAP_TYPE_TOWN', 'MAP_TYPE_CITY') else 'route')
            mc.setdefault('floor', 'town' if mc['kind'] == 'town' else 'route')
            mc.setdefault('place', z['place'])
            for k in ('warps', 'buildings', 'signs', 'npcs', 'triggers'): mc.setdefault(k, {})
            cfg['standalone'][name] = mc
    if cfg.get('map_order'):            # ties between maps follow this fixed order (data/hoenn_world.json _map_order_doc)
        rank = {n: i for i, n in enumerate(cfg['map_order'])}
        cfg['maps'] = dict(sorted(cfg['maps'].items(), key=lambda kv: rank.get(kv[0], len(rank))))
    return cfg, lay

def moved_props(props, moves):
    """A town file's props with an overlay's 'prop_moves' applied (data/towns/emerald/<Map>.json: Emerald moved a few of
    Sapphire's props, e.g. Rustboro's two lamps before Devon one row south): each move {res, at: [x, z], by: [dx, dz]} shifts
    the prop of that res at that origin, with its 'on', 'solid' and 'covers' tiles; a move that matches nothing stops."""
    out = [dict(p) for p in props]
    for mv in moves:
        hit = [p for p in out if p['res'] == mv['res'] and [p['x'], p['z']] == mv['at']]
        assert len(hit) == 1, f'prop_moves: {mv} matches {len(hit)} props'
        p, (dx, dz) = hit[0], mv['by']
        p['x'], p['z'] = p['x'] + dx, p['z'] + dz
        if 'on' in p: p['on'] = [p['on'][0] + dx, p['on'][1] + dz]
        if 'solid' in p: p['solid'] = [[x + dx, z + dz] for x, z in p['solid']]
        if 'covers' in p: p['covers'] = [[x0 + dx, z0 + dz, x1 + dx, z1 + dz] for x0, z0, x1, z1 in p['covers']]
    return out

def standalone_cfg():
    """data/hoenn_standalone.json: the warp-only outdoor maps and their own matrices (groups)."""
    p = os.path.join(ROOT, 'data', 'hoenn_standalone.json')
    return version.load_json(p) if os.path.exists(p) else {'groups': {}, 'margin': [12, 11, 8]}

def standalone_built():
    """Names of the standalone groups this build makes: HOENN_STANDALONE (env: 'all', 'none' or a comma list), else
    data/hoenn_standalone.json 'build' ('all' or a list), else none. Off, the main matrix is built exactly as before
    the warp-only maps existed (their doors on Routes 104/112 lead nowhere, as then): a/0/0/8 has no room for their
    chunks until build_rom.py's RESERVE[8] grows (and the base savestates are remade)."""
    sa = standalone_cfg()
    want = os.environ.get('HOENN_STANDALONE')
    if want is None: want = sa.get('build', [])
    if isinstance(want, str): want = list(sa['groups']) if want == 'all' else [g for g in want.split(',') if g and g != 'none']
    return [g for g in sa['groups'] if g in want]

def compose(cfg, lay, plans=None):
    """Global tile grid: world[(wx, wz)] = (map, class, walkable). Returns world, trees (global anchors), maps.
    plans: {map: plan file} instead of data/plans/<map>.json (build_alts: another layout of a map)."""
    M = cfg['margin_cells'] * 32
    world, trees, maps, tree_tiles = {}, set(), {}, set()
    for name, mc in cfg['maps'].items():
        plan = json.load(open((plans or {}).get(name) or version.plan_path(name)))
        L = lay[name]; pad = cfg.get('pad_north', {}).get(name, 0); sx, sz = cfg.get('shift', {}).get(name, [0, 0])
        ox, oz = L['tile_x'] + M + sx, L['tile_z'] + M + sz + pad      # world position of Sapphire's (0, 0)
        W, H = plan['size']
        rows = [(y, plan['tiles'][y], plan['walkable'][y]) for y in range(H)]
        rows += [(-pad + k, plan['tiles'][k % 2], plan['walkable'][k % 2]) for k in range(pad)]
        for y, tr, wr in rows:
            for x in range(W):
                key = (ox + x, oz + y)
                assert key not in world, f'{name} overlaps {world[key][0]} at {key}'
                world[key] = (name, tr[x], wr[x])
        for x, y in plan['trees']:
            # a tree on the edge between two maps can be in both plans (Route 115's bottom row and Rustboro's top
            # row): the first one placed wins, a second copy overlapping it z-fought (exterior sweep 2026-10-06)
            if any((ox + x + dx, oz + y + dz) in tree_tiles for dx in (0, 1) for dz in (0, 1)): continue
            trees.add((ox + x, oz + y)); tree_tiles.update((ox + x + dx, oz + y + dz) for dx in (0, 1) for dz in (0, 1))
            if y == 0:
                for k in range(1, pad // 2 + 1): trees.add((ox + x, oz - 2 * k))
        maps[name] = dict(ox=ox, oz=oz, plan=plan, cfg=mc, w=W, h=H)
    for name, mp in maps.items(): retile_map(world, name, mp)
    return world, trees, maps

def retile_map(world, name, mp):
    """A map's own 'retile' rules (its settings, e.g. data/towns/emerald/<Map>.json: Emerald's new structures that have
    no model yet drawn as rock or wall, never invisible): [{box: [x0, z0, x1, z1] | tiles: [[x, z]...], from: [classes],
    to: class, walkable (optional)}] in map tiles. No map of Sapphire's or Ruby's world has one."""
    for r in mp['cfg'].get('retile', []):
        if 'tiles' in r: ks = [(x, z) for x, z in r['tiles']]
        else:
            x0, z0, x1, z1 = r['box']; ks = [(x, z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)]
        for x, z in ks:
            k = (mp['ox'] + x, mp['oz'] + z); e = world.get(k)
            if e and e[0] == name and e[1] in r['from']: world[k] = (name, r['to'], r.get('walkable', e[2]))

def cells_needed(world):
    built = {}
    for (wx, wz), (name, _, _) in world.items():
        c = (wx // 32, wz // 32); built.setdefault(c, {}); built[c][name] = built[c].get(name, 0) + 1
    ring = {}
    for (cx, cz) in built:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = (cx + dx, cz + dz)
                if c not in built and c[0] >= 0 and c[1] >= 0:
                    ring.setdefault(c, []).append((cx, cz))
    return built, ring

def build_cell(m_name, cx, cz, world, trees, cfg_maps):
    """Terrain model, collision and the walkable grid of one cell."""
    m = Model(m_name)
    hy = (lambda tx, tz: HF.y(cx * 32 + tx, cz * 32 + tz)) if HF else (lambda tx, tz: 0)    # heights: tile height
    X, Z = cx * 32, cz * 32
    get = lambda tx, tz: world.get((X + tx, Z + tz))
    cell = Cell(cx, cz, world)
    # tiles whose ground surface is drawn by the path or a module itself (sand, decks, ...): no grass under them.
    # Black 2 cuts its ground there too (Nuvema chunk 0: michi01a/b at y 0 in holes of grass01ax, no layer under them);
    # a surface 0.5-1 unit over the grass flickers in melonDS (exterior sweep 2026-10-06, b2tools/exterior_check.py)
    # (buildings standing on a town's path ground: the path goes on under them, terrain/ground.py path_under; they
    # stood on squares of grass in Rustboro, Slateport, Mauville... overworld_polish 2026-10-08)
    p_under = GROUND_MOD.path_under(world) if GROUND_MOD and hasattr(GROUND_MOD, 'path_under') else set()
    on_path = lambda tx, tz: (get(tx, tz) or (0, 0))[1] == 'path' or (X + tx, Z + tz) in p_under
    on_pier = lambda tx, tz: bool(GROUND_MOD and hasattr(GROUND_MOD, 'paved_tile') and GROUND_MOD.paved_tile(world, X + tx, Z + tz))
    cover = {(tx, tz) for tz in range(32) for tx in range(32) if on_path(tx, tz)}
    if GROUP.get('path_as_ground'): cover = set()        # (a warp-only map whose paths are its ground: Sootopolis)
    cover |= {(tx, tz) for tz in range(32) for tx in range(32) if (get(tx, tz) or (0, 0))[1] == 'lava'}
    for f in FEATURES:
        if hasattr(f, 'ground_cover'): cover |= f.ground_cover(cell)
    if VOID: cover |= {(tx, tz) for tz in range(32) for tx in range(32) if (X + tx, Z + tz) in VOID}   # (nothing drawn)
    if not HF: bc.ground_heights(m, lambda tx, tz: 0, lambda tx, tz: None if (tx, tz) in cover else 'grass01ax')
    anchors = {(wx - X, wz - Z) for (wx, wz) in trees if wx // 32 == cx and wz // 32 == cz}
    covered = {(ax + dx, az + dz) for ax, az in anchors for dx in (0, 1) for dz in (0, 1)}
    walk_at = lambda wx, wz: (world.get((wx, wz)) or (None, None, False))[2]
    fillers = [f.filler for f in FEATURES if hasattr(f, 'filler')]    # a module's filler(world, wx, wz) -> class or None
    for wz in range(Z, Z + 32, 2):                       # forest filler on the global even grid
        for wx in range(X, X + 32, 2):
            sq = [(wx + dx, wz + dz) for dx in (0, 1) for dz in (0, 1)]
            if any(c in world or c in VOID for c in sq): continue
            if any(fl(world, *c) for fl in fillers for c in sq): continue    # filled by a module (e.g. sea), no tree
            if any((c[0] - X, c[1] - Z) in covered for c in sq): continue
            if walk_at(wx, wz - 1) or walk_at(wx + 1, wz - 1): continue    # keep the row south of walkable tiles open
            anchors.add((wx - X, wz - Z))
    # (dewford_fix 2026-10-12) that open row is blocked ground outside the map, drawn as the ground beside it: an
    # invisible wall where a town or route ends at the forest (the user: the bottom of Dewford's beach). It gets
    # Black 2's hedge (terrain/ground.py hedge, Striaton's: 16 units at its ridge, low enough that the player on the
    # map's last row stays in view, which the gap is for: DECISIONS 2026-10-06), one run per row and height
    if GROUND_MOD is not None:
        treed = {(ax + dx, az + dz) for ax, az in anchors for dx in (0, 1) for dz in (0, 1)}
        land_at = lambda wx, wz: (world.get((wx, wz)) or (None, None, False))[2] and world[(wx, wz)][1] not in WATER
        gap_at = lambda wx, wz: ((wx, wz) not in world and (wx, wz) not in VOID and land_at(wx, wz - 1)
                                 and not any(fl(world, wx, wz) for fl in fillers))     # (not the sea round the maps)
        gap = {}
        for tz in range(32):
            for tx in range(32):
                if (tx, tz) not in treed and gap_at(X + tx, Z + tz): gap.setdefault(tz, []).append(tx)
        on = lambda tx, tz, d: (tx == 0 and d < 0 or tx == 31 and d > 0) and gap_at(X + tx + d, Z + tz) \
            and (HF.y(X + tx + d, Z + tz) if HF else 0) == hy(tx, tz)      # (the hedge goes on in the next chunk)
        for tz, xs in gap.items():
            xs.sort(); run = [xs[0]]
            for x in xs[1:] + [None]:
                if x is not None and x == run[-1] + 1 and hy(x, tz) == hy(run[0], tz): run.append(x); continue
                GROUND_MOD.hedge(m, bc.ux(run[0]), bc.ux(run[-1] + 1), bc.uz(tz), bc.uz(tz + 1),
                                 ends=(not on(run[0], tz, -1), not on(run[-1], tz, 1)))
                if x is not None: run = [x]
    # Trees go into their own model, each row lifted as a whole to the lowest of its tiles (with heights): world.py's
    # lift moves every triangle by the height under its centre, which tore a tree standing on two levels in two
    # (outside the maps and in forest_fill's trees; exterior sweep 2026-10-06)
    tm = Model(m_name)
    th = lambda tx, tz, w=2, h=2: min(hy(tx + dx, tz + dz) for dx in range(w) for dz in range(h))
    # a tree's north-south card only where the ground round it is level (by a cliff it met the cliff's face)
    level = lambda tx, tz, w: len({hy(tx + i, tz + j) for i in range(-1, w + 1) for j in range(-1, w + 1)}) == 1
    # Sapphire's ash-covered trees in Black 2's snowy winter art (data/hoenn_ash.json, ash_tiles): a tree is snowy
    # when most of its four tiles are ash trees, or, outside the maps, ash forest; a row never mixes the two
    ashy = lambda tx, tz: (ASH_TREES or ASH_NEAR) and sum((X + tx + dx, Z + tz + dz) in ASH_TREES or
                                                          (X + tx + dx, Z + tz + dz) in ASH_NEAR
                                                          for dx in (0, 1) for dz in (0, 1)) >= 2
    # Mossdeep's trees: Black 2's Humilau palm (terrain/palms.py, user 2026-10-11), each on its 2x2 tiles
    palm = lambda tx, tz: PALMS is not None and PALMS.is_palm(world, X + tx, Z + tz)
    for tx, tz in sorted(a for a in anchors if palm(*a)):
        row = Model(m_name); PALMS.palm(row, bc.ux(tx + 1), bc.uz(tz + 1)); tm.extend(row, dy=th(tx, tz))
    anchors = {a for a in anchors if not palm(*a)}
    for tz in sorted({a[1] for a in anchors}):           # trees drawn as rows, as Black 2 draws forests
        xs = sorted(a[0] for a in anchors if a[1] == tz)
        run = [xs[0]]
        for x in xs[1:] + [None]:
            if x is not None and x == run[-1] + 2 and th(x, tz) == th(run[0], tz) and \
                    ashy(x, tz) == ashy(run[0], tz): run.append(x); continue
            row = Model(m_name); bc.tree_row(row, run[0], tz, len(run), cross=lambda k, r=run: level(r[k], tz, 2))
            if ashy(run[0], tz): ash_materials(row, ASH['trees'])
            tm.extend(row, dy=th(run[0], tz))
            if x is not None: run = [x]
    for (wx, wz), (lv, lift) in sorted(OVERLAP.items(), key=lambda kv: (kv[0][1], kv[0][0])):    # (overlap_fill)
        if wx // 32 != cx or wz // 32 != cz: continue
        tx, tz = wx - X, wz - Z
        row = Model(m_name)
        if palm(tx, tz): PALMS.palm(row, bc.ux(tx + 1), bc.uz(tz + 1), lift=lift, shadow=False)
        else: bc.tree_row(row, tx, tz, 1, lift=lift, card=2 * lv, shadow=False, cross=lambda k: level(tx, tz, 2))
        if ashy(tx, tz): ash_materials(row, ASH['trees'])
        tm.extend(row, dy=th(tx, tz))
    narrow = sorted((wz - Z, wx - X) for wx, wz in NARROW if wx // 32 == cx and wz // 32 == cz)   # (row, column)
    for tz, tx in [t for t in narrow if palm(t[1], t[0])]:      # (Mossdeep: a palm scaled evenly to its tile)
        row = Model(m_name); PALMS.palm(row, bc.ux(tx) + 8, bc.uz(tz) + 8, 0.5); tm.extend(row, dy=hy(tx, tz))
    narrow = [t for t in narrow if not palm(t[1], t[0])]
    nset = set(narrow)
    ash1 = lambda tx, tz: (X + tx, Z + tz) in ASH_TREES
    for tz, tx in narrow:                        # one-tile trees (forest_fill), a row per run of neighbours
        if (tz, tx - 1) in nset and hy(tx - 1, tz) == hy(tx, tz) and ash1(tx - 1, tz) == ash1(tx, tz): continue
        n = 1
        while (tz, tx + n) in nset and hy(tx + n, tz) == hy(tx, tz) and ash1(tx + n, tz) == ash1(tx, tz): n += 1
        sign = any((get(tx + k + d, tz) or (0, 0))[1] == 'sign' for k in range(n) for d in (-1, 1))
        row = Model(m_name); bc.narrow_tree_row(row, tx, bc.uz(tz + 1), n, cross=lambda k: level(tx + k, tz, 1),
                                                card=3 if sign else 0)   # (a sign's board reaches 5 into the tile)
        if ash1(tx, tz): ash_materials(row, ASH['trees'])
        tm.extend(row, dy=hy(tx, tz))
    is_path = lambda tx, tz: (world.get((X + tx, Z + tz)) or (None, None))[1] == 'path' or (X + tx, Z + tz) in p_under
    ledges, grass_rows = {}, {}
    for tz in range(32):
        for tx in range(32):
            e = get(tx, tz)
            if not e: continue
            c = e[1]
            if is_path(tx, tz) and not GROUP.get('path_as_ground') and not on_pier(tx, tz):   # (cover above; a ferry
                bc.path_tile(m, tx, tz, is_path, y=0)                             # pier or a paved town: ground.py paves it)
            elif c == 'lava':            # a warp-only map's lava (Mt. Chimney's crater): GROUP['lava'] (lava_tile)
                lava_tile(m, tx, tz, get)
            elif c == 'tall_grass': grass_rows.setdefault(tz, []).append(tx)
            elif c == 'ledge_s': ledges.setdefault(tz, []).append(tx)
            elif c == 'flowers': bc.flat_decal(m, 'hana01.1', tx, tz, 1, 1, 4)    # (Black 2: y 2) 2 over the shadows
            elif c == 'sand_patch':      # y 4 (Black 2: 3): 2 clear of the y-2 layer (tall grass, building/sign shadows)
                x0, z0 = bc.ux(tx), bc.uz(tz)
                m.quad('michi_hage', [(x0 - 8, 4, z0 + 24, 0, 0), (x0 + 24, 4, z0 + 24, 1, 0),
                                      (x0 + 24, 4, z0 - 8, 1, 1), (x0 - 8, 4, z0 - 8, 0, 1)])
    def runs(xs, tz=0):
        xs = sorted(xs); out = [[xs[0], xs[0]]]
        for x in xs[1:]:
            if x == out[-1][1] + 1 and hy(x, tz) == hy(x - 1, tz): out[-1][1] = x     # (heights: level runs only)
            else: out.append([x, x])
        return out
    for tz, xs in ledges.items():
        for x0, x1 in runs(xs, tz): bc.ledge_run(m, x0, x1, tz, get, hy)   # (no taper where the ledge goes on)
    bc.ledge_corners(m, get, hy)                         # Sapphire's ledge corner tiles
    for tz, xs in grass_rows.items():
        for x0, x1 in runs(xs, tz): bc.tall_grass_run(m, x0, x1, tz)
    if HF:                                               # heights: all of it on its tile's height
        HF.lift(m, cx, cz); mat = HF.material(cx, cz)
        if GROUP.get('ground'):          # a warp-only map's ground by tile class (data/hoenn_standalone.json 'ground')
            gm, mat0 = GROUP['ground'], mat
            mat = lambda tx, tz: None if mat0(tx, tz) is None else gm.get((get(tx, tz) or (0, ''))[1], gm.get('default', mat0(tx, tz)))
        bc.ground_heights(m, hy, lambda tx, tz: None if (tx, tz) in cover else mat(tx, tz))
    # a path-coloured floor 2 under the path (and 4 units under the ground beside it): melonDS showed the background
    # through 1-pixel cracks at the path's T-junctions (purple_lines 2026-10-13, build_chunk.path_cover)
    if not GROUP.get('path_as_ground'):
        slope = HF.slope if HF else ()
        drawn = lambda tx, tz: (get(tx, tz) is not None and is_path(tx, tz) and not on_pier(tx, tz)
                                and (X + tx, Z + tz) not in slope)
        flat = (lambda tx, tz: (tx, tz) not in cover and mat(tx, tz) is not None) if HF else (lambda tx, tz: (tx, tz) not in cover)
        bc.path_cover(m, drawn, flat, hy)
    m.extend(tm)                                         # (the trees, already at their heights)
    for f in FEATURES:
        if HF and f is not HEIGHTS:                         # heights: other modules draw at ground level, then rise
            sub = Model(m_name); f.draw(sub, cell); m.extend(HF.lift(sub, cx, cz))
        else: f.draw(m, cell)
    owner = {c: f for f in FEATURES for c in f.CLASSES}
    per = bytearray(struct.pack('<HH', 32, 32)); grid = []
    for tz in range(32):
        row = ''
        for tx in range(32):
            e = get(tx, tz)
            route = e is not None and cfg_maps[e[0]].get('floor') == 'route'
            c = e[1] if e else None
            ok = e is not None and e[2] and c not in ('sign', 'building', 'door') and c not in WATER
            if e is not None and e[2] and c in ('building', 'sign') and (X + tx, Z + tz) in OPEN_BLD: ok = True   # (see OPEN_BLD)
            custom = owner[c].collision(c, e, cell) if c in owner else None
            if (X + tx, Z + tz) in SOLID_AT: rec, ch = bc.SOLID, '#'     # a warp stands here (warp_spot)
            elif custom: rec, ch = custom
            elif c == 'ledge_s': rec, ch = bc.LEDGE_S, 'v'
            elif not ok: rec, ch = bc.SOLID, '#'
            elif c == 'tall_grass': rec, ch = bc.TALL_GRASS, 'g'
            elif route: rec, ch = (bc.ROUTE_PATH, ':') if c == 'path' else (bc.ROUTE_GRASS, '.')
            else: rec, ch = bc.WALK, '.'
            if HF: rec = HF.record(rec, X + tx, Z + tz)       # heights: the tile's height (or stairs slope)
            per += struct.pack('<HHHH', *rec); row += ch
        grid.append(row)
    # ash (ash_tiles): the ash grass's ground and all its tall-grass layers in winter art, the grass lips round the ash
    # ground snowy (a triangle goes by the tile under its centre)
    for tiles_, names in ((ASH_GRASS, ASH.get('ash_grass', {})), (ASH_LIP, ASH.get('lips', {}))):
        if not tiles_: continue
        for old, new in names.items():
            if old in GROUP.get('retex', {}): continue    # (a warp-only map's own stand-in wins: Mt. Chimney's red lips)
            tris = m.tris.get(old)
            if not tris: continue
            keep, moved = [], []
            for t in tris:
                mx = sum(v[0] for v in t) / 3; mz = sum(v[2] for v in t) / 3
                k = (X + int((mx + 256) // 16), Z + int((mz + 256) // 16))
                (moved if k in tiles_ else keep).append(t)
            if moved:
                m.tris.setdefault(new, []).extend(moved)
                if keep: m.tris[old] = keep
                else: del m.tris[old]
    for old, new in GROUP.get('retex', {}).items():     # a warp-only map's textures (data/hoenn_standalone.json 'retex')
        if old not in m.tris: continue
        tris = m.tris.pop(old)
        # (sweep_outdoor 2026-10-11) a tall face (yamagake01, one v repeat per started 64 units) on a stand-in with no
        # tall texture (Mt. Chimney's / Jagged Pass's out57_gake01a, 16 rows, the 2 bottom ones clear) goes on its
        # opaque rows per repeat, as heights.py's red-rock style does on Route 112 (_banded): renamed as it was, the
        # clear rows showed at every repeat's foot where two tiers meet (outdoor_check hole, Mt. Chimney 87 px)
        if old == 'yamagake01' and new == 'out57_gake01a':
            from terrain import heights as H_
            tris = [b for t in tris for b in H_._banded(t)]
        m.tris.setdefault(new, []).extend(tris)
    if VOID:            # nothing is drawn over a void tile: heights.py's cliff faces between void tiles of different
        # heights went on there (Sky Pillar top: a 32-unit face down the screen along x 7.5 and 18.5 from the sunken
        # band to the matrix edge, one triangle pair from row 17 to row 41; buildings_audit 2026-10-08). Triangles
        # over void tiles are cut on the tile grid and the pieces over void dropped; a piece whose centre lies on a
        # tile edge goes only when the tiles on both sides are void (faces on the floor's own rim stay).
        def near(u):                                   # the tile(s) a coordinate (cell units + 256) touches
            t = int(u // 16); f = u - t * 16
            return [t - 1, t] if f < 1 else [t, t + 1] if f > 15 else [t]
        def void_at(t):
            mx = sum(v[0] for v in t) / 3 + 256; mz = sum(v[2] for v in t) / 3 + 256
            return all((X + a, Z + b) in VOID for a in near(mx) for b in near(mz))
        def cut(t, k, at):                             # split a triangle by the plane coordinate k == at
            lerp = lambda p, q, f: tuple(p[i] + (q[i] - p[i]) * f if i < 5 else p[i] for i in range(len(p)))
            side = [v[k] < at for v in t]
            if all(side) or not any(side): return [t]
            for i in range(3):                         # the lone vertex on its side: rotate it first (keeps winding)
                if side[i] != side[(i + 1) % 3] and side[i] != side[(i + 2) % 3]: break
            a_, b_, c_ = t[i], t[(i + 1) % 3], t[(i + 2) % 3]
            ab = lerp(a_, b_, (at - a_[k]) / (b_[k] - a_[k])); ac = lerp(a_, c_, (at - a_[k]) / (c_[k] - a_[k]))
            return [[a_, ab, ac], [ab, b_, c_], [ab, c_, ac]]
        def tile_pieces(t):                            # pieces of t, none crossing a tile edge
            out = [t]
            for k in (0, 2):
                nxt = []
                for q in out:
                    lo, hi = min(v[k] for v in q), max(v[k] for v in q)
                    pieces = [q]
                    for g in range(int((lo + 256) // 16) + 1, int(-(-(hi + 256) // 16))):
                        pieces = [r for p_ in pieces for r in cut(p_, k, g * 16 - 256)]
                    nxt += pieces
                out = nxt
            return out
        for mat in list(m.tris):
            keep = []
            for t in m.tris[mat]:
                xs = [v[0] + 256 for v in t]; zs = [v[2] + 256 for v in t]
                touch = any((X + a, Z + b) in VOID for a in range(int(min(xs) // 16), int(max(xs) // 16) + 1)
                            for b in range(int(min(zs) // 16), int(max(zs) // 16) + 1))
                if not touch: keep.append(t); continue
                if not void_at(t) and len({int(x // 16) for x in xs}) == 1 and len({int(z // 16) for z in zs}) == 1:
                    keep.append(t); continue
                keep += [q for q in tile_pieces(t) if not void_at(q)]
            if keep: m.tris[mat] = keep
            else: del m.tris[mat]
    return m, bytes(per), grid

def lava_tile(m, tx, tz, get):
    """One lava tile of a warp-only map (Mt. Chimney's crater; data/hoenn_standalone.json 'lava', 'lava_top',
    'lava_bank', 'lava_shore'), the way Reversal Mountain lays its magma (chunks 723/726, map set 388): the lava
    (in81_magu00) 10 under the ground, the dark crust with holes (in81_magu01) 2 over it, and on every side that meets
    ground a bank (in81_mizuga1) sloping 4 down over 6 into the lava and a glowing shore strip (in81_mizugiwa) 2 wide
    at its foot; the banks are mitred where two meet. Black 2 lays them 62-66 and 56-58 round a 66 floor. The lava
    used to be one flat tile-sized quad level with the ground (hard stepped edges, no depth). Area 'srt_anim' scrolls
    magu00/magu01/mizugiwa as Reversal Mountain's (buildings_audit 2026-10-08). Drawing only: the tiles stay solid."""
    x0, z0 = bc.ux(tx), bc.uz(tz)
    L, top, bank, shore = GROUP['lava'], GROUP.get('lava_top'), GROUP.get('lava_bank'), GROUP.get('lava_shore')
    flat = lambda mat, y: m.quad(mat, [(x0, y, z0 + 16, x0 / 64, -(z0 + 16) / 64), (x0 + 16, y, z0 + 16, (x0 + 16) / 64, -(z0 + 16) / 64),
                                        (x0 + 16, y, z0, (x0 + 16) / 64, -z0 / 64), (x0, y, z0, x0 / 64, -z0 / 64)])
    if not bank:                                  # (the old flat lava)
        flat(L, 0); return
    flat(L, -10)
    if top: flat(top, -8)
    lava = lambda dx, dz: (get(tx + dx, tz + dz) or (0, ''))[1] == 'lava'
    sides = {s_: not lava(*d) for s_, d in (('n', (0, -1)), ('s', (0, 1)), ('w', (-1, 0)), ('e', (1, 0)))}
    R, D, W = 6, 4, 2                             # bank run, drop; shore width (6 + 2 = half a tile: banks on opposite
                                                  # sides of a 1-wide channel meet without overlapping)
    # each side: (outer edge a -> b along the side, inward unit vector, the sides at a's and b's ends)
    edges = {'n': ((x0, z0), (x0 + 16, z0), (0, 1), 'w', 'e'), 's': ((x0 + 16, z0 + 16), (x0, z0 + 16), (0, -1), 'e', 'w'),
             'w': ((x0, z0 + 16), (x0, z0), (1, 0), 's', 'n'), 'e': ((x0 + 16, z0), (x0 + 16, z0 + 16), (-1, 0), 'n', 's')}
    for s_, ((ax, az), (bx, bz), (ix, iz), ea, eb) in edges.items():
        if not sides[s_]: continue
        ux, uz = (bx - ax) / 16, (bz - az) / 16   # along the side, a -> b
        def at(d_in, along, y, u, v):            # a point d_in into the lava, `along` units from a
            return (ax + ux * along + ix * d_in, y, az + uz * along + iz * d_in, u, v)
        def strip(mat, d0, d1, y0, y1, v0, v1):
            m0, m1 = (d0 if sides[ea] else 0), (d1 if sides[ea] else 0)      # mitre at a corner with a bank
            n0, n1 = 16 - (d0 if sides[eb] else 0), 16 - (d1 if sides[eb] else 0)
            off = (ax * ux + az * uz) / 12              # (u from the position along the side: strips line up)
            m.quad(mat, [at(d1, m1, y1, off + m1 / 12, v1), at(d1, n1, y1, off + n1 / 12, v1),     # (inner edge first:
                         at(d0, n0, y0, off + n0 / 12, v0), at(d0, m0, y0, off + m0 / 12, v0)])    # faces up)
        strip(bank, 0, R, 0, -D, 1, 0)
        if shore: strip(shore, R, R + W, -D, -D, 1, 0)

TREE_PARTS = ('tree_bot', 'tree_top_l', 'tree_top_r')

# ---- Sapphire's ash in Black 2's snowy winter art (data/hoenn_ash.json) ----------------------------------------------
_ap = os.path.join(ROOT, 'data', 'hoenn_ash.json')
ASH = json.load(open(_ap)) if os.path.exists(_ap) else {}
ASH_TEX = {new: (int(ts), src) for new, (ts, src) in ASH.get('textures', {}).items()}   # snowy name -> (set, B2 name)
ASH_TREES, ASH_NEAR, ASH_GRASS = set(), set(), set()   # world tiles: ash tree tiles, ash forest outside maps, ash grass
ASH_GROUND, ASH_LIP = set(), set()     # world tiles whose ground is ash (snowy), tiles holding the grass lips round it
ASH_NOT_GROUND = ('path', 'sand', 'water', 'deep_water', 'waterfall')   # (drawn by their own modules, not ground)

def ash_tiles(world, maps):
    """The ash tiles of the maps data/hoenn_ash.json lists (in world, the world being built): tree tiles Sapphire
    draws in non-green colours (mean green - red of the metatile below max_green), ash grass tiles, and the tiles
    outside the maps within 4 of a map whose trees are (nearly) all ashy (world.py's forest there is snowy too)."""
    ASH_TREES.clear(); ASH_NEAR.clear(); ASH_GRASS.clear(); ASH_GROUND.clear(); ASH_LIP.clear()
    names = [n for n in maps if n in ASH.get('maps', [])]
    if not names: return
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from gba import world_repo, MetatileRenderer
    repo = world_repo()
    for name in names:
        mp = maps[name]
        g, lay = repo.layout_grid(repo.map_json(name)['layout'])
        mr = MetatileRenderer(repo, lay['primary_tileset'], lay['secondary_tileset'])
        green, n_tree, n_ash = {}, 0, 0
        tiles = [k for k, e in world.items() if e[0] == name]
        for k in tiles:
            c = world[k][1]
            if c == 'ash_grass': ASH_GRASS.add(k); ASH_GROUND.add(k)
            if c in ASH_NOT_GROUND: continue
            x, y = k[0] - mp['ox'], k[1] - mp['oz']
            if not (0 <= y < g.shape[0] and 0 <= x < g.shape[1]): continue
            mt = int(g[y, x]) & 0x3FF
            if mt not in green:
                px = mr.render(mt)[..., :3].reshape(-1, 3).astype(float).mean(0)
                green[mt] = px[1] - px[0]
            if green[mt] < ASH['max_green']: ASH_GROUND.add(k)
            if c not in TREE_PARTS + ('tree_tip',): continue
            n_tree += 1
            if green[mt] < ASH['max_green']: ASH_TREES.add(k); n_ash += 1
        if n_tree and n_ash >= 0.9 * n_tree:
            for wx, wz in tiles:
                for dz in range(-4, 5):
                    for dx in range(-4, 5):
                        if (wx + dx, wz + dz) not in world: ASH_NEAR.add((wx + dx, wz + dz))
        print(f'ash: {name}: {n_ash} of {n_tree} tree tiles ashy, {sum(1 for k in tiles if k in ASH_GRASS)} ash grass tiles, '
              f'{sum(1 for k in tiles if k in ASH_GROUND)} ash ground tiles')
    # (map_glitch_fix 2026-10-09) the ash lies on all of Sapphire's ash-grey ground, not only under the ash grass and the
    # trees: Route 113's lawn was Black 2's summer grass, so every ash-grass patch stood out as a grid of snow-capped
    # boxes on a white rectangle cut out of a green lawn, and the snowy trees stood on green grass. The ground of every
    # ash-coloured tile drawn as grass (and of the snowy forest outside an all-ash map) is the winter ground now, as
    # Black 2's own winter routes (Icirrus's set): white ground, olive tall grass with snow caps, snow on the grass lips.
    # Rocky ground keeps its rock (ash_ground); Sapphire's green grass (Route 113's east end) stays green
    # (the forest outside: snowy ground where the map tile nearest to it is ash ground: by Fallarbor's green grass the
    # snowy forest of Route 113's edge stood on a white rectangle)
    for wx, wz in ASH_NEAR:
        best = None
        for r in range(1, 5):
            ring = [(wx + dx, wz + dz) for dx in range(-r, r + 1) for dz in range(-r, r + 1) if max(abs(dx), abs(dz)) == r]
            hits = [k for k in ring if k in world]
            if hits: best = hits; break
        if best and sum(k in ASH_GROUND for k in best) * 2 >= len(best): ASH_GROUND.add((wx, wz))
    ASH_LIP.update((x + dx, z + dz) for x, z in ASH_GROUND for dx in (-1, 0, 1) for dz in (-1, 0, 1))

def ash_ground(F):
    """The ash ground's texture through the height field's per-tile ground material (build_chunk.ground_heights draws
    one texture per region of tiles, so the snowy ground gets its own quads; rocky ground stays rock)."""
    if F is None or not ASH.get('ground'): return
    for k in ASH_GROUND:
        if k not in F.mat: F.mat[k] = ASH['ground']

def ash_materials(m, names):
    """Rename a model's materials (Hoenn texture -> its snowy stand-in)."""
    for old, new in names.items():
        if old in m.tris: m.tris.setdefault(new, []).extend(m.tris.pop(old))
NEAR_STRUCTURE = ('building', 'door', 'bridge', 'stairs', 'sign', 'prop', 'other:big_tree')
NARROW = set()         # one-tile trees drawn by build_cell (world tiles), set by prepare() (overlap_fill)
OVERLAP = {}           # overlap_fill's overlapping 2x2 trees: anchor -> (level, lift)
GROUP = {}             # the standalone group being built (data/hoenn_standalone.json): its look options; {} = main
EXTRA_TEX = {}         # textures those options name -> Black 2 map texture set (a/0/1/4) they come from

def forest_fill(world, trees):
    """Sapphire's dense forests (Routes 104-123, Mt Chimney, Dewford, Mauville...) use tree metatiles that overlap row
    by row, so converter/plan_map.py finds no complete 2x2 tree there: their tree_bot tiles (1,690 on Route 119 alone)
    were drawn as plain grass. They are filled the way Black 2 fills its forests (and world.py the forest outside the
    maps): 2x2 round trees on the global even grid, then on any grid. Then (b2_trees 2026-10-11) a tile still left
    gets a whole 2x2 tree over a 2x2 window of forest tiles, overlapping the trees round it, as Black 2 overlaps and
    offsets its forest trees (Route 6 chunk 55; a squeezed one-tile tree there looked nothing like Black 2's): each
    such tree gets a level one above the highest tree it overlaps, its canopy and top lifted by build_chunk.overlap_lift
    and its cards moved 2 units per level (no two tree layers or cards closer than 2: depth fights), no shadow.
    Only tiles with no such window (a lone tree between walkable tiles) get a one-tile tree: Black 2's tree scaled
    evenly (build_chunk.NARROW_SCALE), never squeezed.
    Tiles next to a building, door, bridge, stairs, sign or prop are left alone (Fortree's tree houses are the town
    models' own trees and crowns), and so are the trunk tiles below Sapphire's one-tile tree tops (ground.py).
    -> (new 2x2 trees, tiles left, forest tiles, blocked tiles by a small structure for one-tile trees); overlap_fill
    places the overlapping trees once the heights are known."""
    covered = {(ax + dx, az + dz) for ax, az in trees for dx in (0, 1) for dz in (0, 1)}
    trunks = {(x, z + 1) for (x, z), e in world.items() if e[1] == 'other:tree_top_1wide'}
    covered |= trunks
    near = {(x + dx, z + dz) for (x, z), e in world.items() if e[1] in NEAR_STRUCTURE
            for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
    solid = {k for k, e in world.items() if e[1] in TREE_PARTS + ('tree_tip',) and not e[2] and k not in covered}
    todo = {k for k in solid - near if world[k][1] != 'tree_tip'}
    tips = solid - near - todo           # (blocked tree tips: overlapping or one-tile trees only, b2_trees 2026-10-11:
                                         # they showed open ground; not the 2x2 fill, whose trees level the heights)
    forest = (covered - trunks) | todo | tips   # (tiles a tree may stand over; not a one-tile tree's trunk: ground.py's)
    forest = {k for k in forest if not world.get(k, (0, 0, False))[2]}   # (nor a walkable tile: walk-behind tree tops)
    # blocked tree tiles by a structure: a one-tile tree (it stays on its tile), except by a big tree (its model has
    # its own crown there) and beside a Fortree tree house's side (its model is wider than Sapphire's footprint: a tree
    # card there lay 1 unit from its side wall, outdoor_check layer). (sweep_outdoor 2026-10-11: the rest of the tiles
    # round the tree houses get their tree: on stilts since map_glitch_fix the models hold no trees, and Sapphire's tree
    # tiles there were bare grass you could not walk on)
    houses = {(x + dx, z + dz) for (x, z), e in world.items() if e[1] == 'other:big_tree'
              for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
    houses |= {(x + dx, z) for (x, z), e in world.items()
               if e[0] == 'FortreeCity' and e[1] in ('building', 'building_roof', 'door') for dx in (-1, 1)}
    lone = (solid & near) - houses
    new = set()
    for even in (True, False):
        for x, z in sorted(todo, key=lambda k: (k[1], k[0])):
            if even and (x % 2 or z % 2): continue
            sq = [(x + dx, z + dz) for dx in (0, 1) for dz in (0, 1)]
            if all(s in todo for s in sq): new.add((x, z)); todo -= set(sq)
    return new, todo | tips, forest, lone

def overlap_fill(todo, forest, trees, hy=lambda wx, wz: 0, skip=lambda wx, wz: False):
    """forest_fill's second step, once the heights are known: a whole 2x2 tree over a 2x2 window of forest tiles of one
    height for every tile left (most left tiles first), overlapping the trees round it. Its level (cards moved 2 units
    per level) is one above the highest tree it overlaps; its lift (build_chunk.overlap_lift) keeps its canopy and top
    2 clear of the layers of every tree under it and of a cliff's faces and grass lips beside it.
    -> ({anchor: (level, lift)}, tiles still left for one-tile trees)."""
    todo = set(todo); over, level = {}, {}
    layers = {}                                    # tile -> absolute heights of the tree layers over it
    for ax, az in trees:
        base = min(hy(ax + i, az + j) for i in (0, 1) for j in (0, 1))
        for i in (0, 1):
            for j in (0, 1): layers.setdefault((ax + i, az + j), []).extend((base + 4, base + bc.R_CANOPY, base + bc.R_TOP))
    for x, z in sorted(todo, key=lambda k: (k[1], k[0])):
        if (x, z) not in todo: continue
        best = None
        for dz in (0, 1):
            for dx in (0, 1):
                sq = [(x - dx + i, z - dz + j) for j in (0, 1) for i in (0, 1)]
                if not all(s in forest for s in sq) or len({hy(*s) for s in sq}) > 1 or any(skip(*s) for s in sq): continue
                n = sum(s in todo for s in sq)
                if best is None or n > best[0]: best = (n, (x - dx, z - dz), sq)
        if best is None: continue
        _, a, sq = best
        base = hy(*sq[0])
        near = [y for s in sq for y in layers.get(s, ())]
        for hr in {hy(a[0] + i, a[1] + j) for j in range(-1, 3) for i in range(-1, 3)} - {base}:
            for t in range(min(base, hr), max(base, hr), 16):        # a cliff beside it: its faces' gentle parts and
                near += [t, t + 4, t + 12, t + 14, t + 16]           # grass lips (heights.py face profile 0-4-14-16)
        lift = bc.overlap_lift(base, near)
        over[a] = (1 + max(level.get(s, 0) for s in sq), lift)
        for s in sq:
            level[s] = over[a][0]
            layers.setdefault(s, []).extend((base + bc.R_CANOPY + lift, base + bc.R_TOP + lift))
        todo -= set(sq)
    return over, todo

def prepare(world, trees, maps, hcfg):
    """Dense forests, prop tiles and the height field of one composed world (the main matrix or a standalone group)."""
    global HF
    fill, left, forest, lone = forest_fill(world, trees)   # Sapphire's dense forests (see forest_fill)
    trees |= fill
    for mp in maps.values():          # map tiles a prop blocks ("solid", map tile coords; Littleroot's moving trucks)
        for pr in mp['cfg'].get('props', []):
            for x, z in pr.get('solid', []):
                k = (mp['ox'] + x, mp['oz'] + z); world[k] = world[k][:2] + (False,)
            # map tiles a town model stands on ([x0, z0, x1, z1] inclusive): the ground module's stand-ins for
            # Sapphire's props and awnings (plinths, plank canopies) are left out there, as they stood around the
            # model (Slateport's stalls and canopies, the shipyard's frames); walkable ones become path
            for x0, z0, x1, z1 in pr.get('covers', []):
                for z in range(z0, z1 + 1):
                    for x in range(x0, x1 + 1):
                        k = (mp['ox'] + x, mp['oz'] + z); e = world.get(k)
                        if e and e[1] in ('prop', 'other:market_awning'):
                            world[k] = (e[0], 'path' if e[2] else 'building', e[2])
    open_buildings(world, maps)
    HF = HEIGHTS.height_field(world, maps, hcfg, trees) if HEIGHTS else None
    over, narrow = overlap_fill(left, forest, trees, (lambda wx, wz: HF.y(wx, wz)) if HF else (lambda wx, wz: 0),
                                lambda wx, wz: PALMS is not None and PALMS.is_palm(world, wx, wz))   # (palms never overlap)
    # every blocked tile shows a tree (b2_trees 2026-10-11, user: the collision must match the look): the one-tile trees
    # by small structures, and a one-tile tree on the blocked crown tile of Sapphire's one-tile-wide trees too
    # (ground.py's tree stands on the trunk tile below it)
    narrow |= lone | {k for k, e in world.items() if e[1] == 'other:tree_top_1wide' and not e[2]}
    NARROW.clear(); NARROW.update(narrow); OVERLAP.clear(); OVERLAP.update(over)
    print(f'forest: {len(fill)} trees, {len(over)} overlapping trees and {len(narrow)} one-tile trees where Sapphire '
          f'draws dense forest')
    return HF

OPEN_BLD = set()       # world tiles labelled 'building' that stay walkable (open_buildings)
def open_buildings(world, maps):
    """Two kinds of 'building' tiles Black 2 drew wrong (outdoor sweep 2026-10-07):
    - building tiles Sapphire lets you walk on that no placed building's footprint covers (the Weather Institute's
      front steps on Route 119, the row its door is entered from: its door could not be reached) stay walkable
      (OPEN_BLD, build_cell); a footprint of a placed building (its town data names a model) stays solid (the
      model stands there: Gym fronts), and so do Sapphire's warp tiles;
    - roof rows over the sea (Pacifidlog's and Sootopolis's houses, Route 110's southern gate): Sapphire's roof tiles
      there are surf water (the house hides the surfer behind it); they were land you could walk on from a deck.
      Black 2's model stands on its footprint only, so these become water; so does the Safari Zone's pond tile under
      its Pokeblock feeder (a 'prop' tile of surf water: a plinth in the pond, its water 32 units below the rest)."""
    OPEN_BLD.clear()
    foot, warps = set(), set()
    for mp in maps.values():
        ox, oz, mc = mp['ox'], mp['oz'], mp['cfg']
        for b in mp['plan']['buildings']:
            if mc.get('buildings', {}).get(b['dest']):
                x0, y0, x1, y1 = b['footprint']
                foot |= {(ox + x, oz + y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
        warps |= {(ox + w['x'], oz + w['y']) for w in mp['plan']['warps']}
    for k, e in world.items():
        if e[1] == 'building' and e[2] and k not in foot and k not in warps: OPEN_BLD.add(k)
    if WATER_MOD:
        for k, e in list(world.items()):
            if e[1] in ('building_roof', 'prop') and e[2] and WATER_MOD.surfable(WATER_MOD.behaviour(e[0], *k)):
                world[k] = (e[0], 'water', e[2])

def open_uncovered(world, maps, placements, hgt, group=None):
    """(walkability 2026-10-11) Building and sign tiles Sapphire lets you walk on stay walkable where no placed model
    stands on them (OPEN_BLD). A placed building's whole Sapphire footprint was solid, but Black 2's models stand back
    from the door row beside their entrance (every Gym's door-row corners, the Battle Tower's front row) and a sign
    model stands on its own tile only (the tops of Sapphire's two-tile Gym signs): flat ground you could not walk on,
    'invisible walls' (b2tools/walk_diff.py OPEN). Tiles a model does cover keep their wall (the Route 110/111 gates,
    the glass workshop: Black 2's models are bigger). A model counts as standing on a tile when any of its faces rises
    more than 3.5 units over the tile's ground inside it (3 units in from its edges: walk_diff.py's rule); a model whose
    geometry cannot be read keeps the old rule (solid)."""
    cand = {k for k, e in world.items() if e[2] and e[1] in ('building', 'sign') and k not in OPEN_BLD}
    cand -= {(mp['ox'] + w['x'], mp['oz'] + w['y']) for mp in maps.values() for w in mp['plan']['warps']}
    if not cand: return 0
    try:
        import outdoor_check as oc
        import walk_diff as wd
    except Exception as ex:
        print(f'warning: open_uncovered: {ex}'); return 0
    frame = type('F', (), {'group': group})()
    pcs = wd.Pieces({k: [] for k in cand})
    unknown = set()
    for c, entries in placements.items():
        if not any(abs(c[0] - k[0] // 32) <= 1 and abs(c[1] - k[1] // 32) <= 1 for k in cand): continue
        for b in entries:
            x, y, z, rot = struct.unpack_from('<iiiH', b, 0); res = (b[14] << 8) | b[15]
            X, Y, Z = c[0] * 512 + 256 + x / 4096, y / 4096, c[1] * 512 + 256 - z / 4096
            parts = oc.placed_parts(frame, res, X, Y, Z, rot * 360 / 0x10000)
            if not parts: unknown.add((int(X // 16), int(Z // 16)))
            for n_, img, P, UV, A, owner in parts: pcs.add(n_, P)
    n = 0
    for k in sorted(cand):
        if any(abs(u[0] - k[0]) <= 3 and abs(u[1] - k[1]) <= 3 for u in unknown): continue
        if any(p[1] > hgt(*k) + wd.UP for p in pcs.pieces(k)): continue
        OPEN_BLD.add(k); n += 1
    return n

def new_zone():
    return dict(signs=[], npcs=[], warps={}, maps=[])

def zone_rects(maps, cells, pad=None):
    """Sub-cell zones (banner code patch, user decision 2026-10-06; every map: user decision 2026-10-07, zone_edges):
    Black 2 has one zone per 32x32 matrix cell (a cell takes the zone of the map with most tiles in it), so a map's
    tiles in another zone's cell were that zone's: its banner, music, wild Pokemon and people (Route 119's north end in
    Fortree's zone, Route 115's south end in Rustboro's, ...: 10,000 walkable tiles of 29 routes). Every map gets its
    own zone on all of its tiles in other zones' cells: one rectangle (map rectangle x cell) per such cell,
    [x0, z0, x1, z1, zone] in world tiles (inclusive; with the map's pad rows, pad = cfg 'pad_north'). patches/
    hoenn_world.py installs them as a table that the game's matrix zone lookup consults first
    (GetZoneIDAtMatrixXZWorld, ov012), so the swap (banner, BGM, entities, encounters) happens at Sapphire's map
    edges; zone_at() here and the converters (zone_of) use the same table, so every event of a map (doors, signs,
    people, trainers, items, triggers, wild tables) sits in the map's own zone. Maps never overlap (compose asserts
    it), so the rectangles don't either; tiles of no map (forest, open sea between maps) keep their cell's zone.
    (Before 2026-10-08 only the maps with a door in another zone's cell had them: Routes 104, 106, 112, 117, 124.)"""
    out = []
    for name, mp in maps.items():
        z = mp['cfg']['zone']
        p = (pad or {}).get(name, 0)
        x0, z0, x1, z1 = mp['ox'], mp['oz'] - p, mp['ox'] + mp['w'] - 1, mp['oz'] + mp['h'] - 1
        for cz in range(z0 // 32, z1 // 32 + 1):
            for cx in range(x0 // 32, x1 // 32 + 1):
                if cells.get((cx, cz)) not in (z, None):
                    out.append([max(x0, cx * 32), max(z0, cz * 32), min(x1, cx * 32 + 31), min(z1, cz * 32 + 31), z])
    return out

def zone_of(owner, wx, wz, rects=()):
    """Zone of world tile (wx, wz) as the game sees it: a zone_rects rectangle, else its cell's zone (owner: cell ->
    zone; world.json "zone_rects" for the converters)."""
    for x0, z0, x1, z1, z in rects:
        if x0 <= wx <= x1 and z0 <= wz <= z1: return z
    return owner.get((int(wx) // 32, int(wz) // 32))

def foreign_doors(zones, zone_at):
    """A door standing in another zone's cell (a zone covers whole cells, so a map's door can lie in a neighbour's
    cell: Granite Cave's mouth on Route 106 is in Dewford's, the Fiery Path's on Route 112 in Route 113's/Lavaridge's)
    is dead there: Black 2 only reads the warps of the zone the player is in (cave_builder, tested 2026-10-06). The
    cell's zone gets a copy ("foreign": true), appended after all of its own doors so no door index moves; rooms' and
    caves' exits point at the copy (converter/gen_caves.py, gen_interiors.py prefer it)."""
    copies = []
    for zid, z in zones.items():
        for d in z.get('doors', []):
            if d.get('foreign'): continue
            owner = zone_at((d['x'] - 8) // 16, (d['z'] - 8) // 16)
            if owner is not None and zid is not None and owner != zid: copies.append((owner, dict(d, foreign=True, home=zid)))
    for owner, d in copies: zones.setdefault(owner, new_zone()).setdefault('doors', []).append(d)

def sign_y(wx, wz, d, hgt, world):
    """y of a sign's BG event: the game reads it when the player's y is in [y - 2, y + 2) (ov012 CheckBGPositionMatchGrid),
    the player standing on a tile next to it (dir 0: south of it). Its own tile's ground height, unless no tile it is read
    from is at that height: then theirs (script_check 2026-10-08: Route 104's sign at world (75,306) stands at 0 below a ledge,
    read from 16; Route 115's at world (73,138), 16, read from 32), as story.py sign_y does for hidden items."""
    from collections import Counter
    own = hgt(wx, wz)
    sides = [(0, 1)] if d == 0 else [(0, 1), (0, -1), (1, 0), (-1, 0)]
    hs = [hgt(wx + a, wz + b) for a, b in sides if (world.get((wx + a, wz + b)) or (None, None, False))[2]]
    if not hs or any(-2 <= own - h < 2 for h in hs): return own
    return Counter(hs).most_common(1)[0][0]

HAND_MADE_EVENTS = {'LittlerootTown', 'Route101', 'OldaleTown'}   # converter/gen_map_content.py HAND_MADE (Emerald: map_events)

def map_events(name, mp, zones, put, hgt, zone_at, world):
    """Buildings, props, signs, NPCs, triggers, warps and fly point of one map into `zones` (by zone id)."""
    mc, plan, ox, oz = mp['cfg'], mp['plan'], mp['ox'], mp['oz']
    z = zones.setdefault(mc['zone'], new_zone())
    z['maps'].append(name); z['place'] = mc['place']; z['kind'] = mc['kind']
    if 'place_display' in mc: z['place_display'] = mc['place_display']    # place-name popup type (Route 101: none)
    sp = os.path.join(ROOT, 'data', 'sapphire', f'{name}.json')
    if version.EMERALD and name not in HAND_MADE_EVENTS:   # (Emerald: pokeemerald's events, the ones data/emerald/hoenn_content.json
        ep = os.path.join(ROOT, 'data', 'sapphire', 'emerald', f'{name}.json')   # names; the hand-made zones keep Sapphire's,
        if os.path.exists(ep): sp = ep                                         # whose settings name pokeruby's labels)
    sapphire = json.load(open(sp)) if os.path.exists(sp) else dict(signs=[], npcs=[])
    for b in plan['buildings']:
        bcfg = mc['buildings'].get(b['dest'])
        if not bcfg: continue
        x0, y0, x1, y1 = b['footprint']
        wx, wz = ox + (x0 + x1 + 1) / 2, oz + b['door'][1] + (4 - bcfg['front']) / 16
        put((int(wx) // 32, int(wz) // 32), bcfg['res'], wx, wz, y=hgt(ox + b['door'][0], oz + b['door'][1] + 1))
    for pr in mc.get('props', []):     # extra models placed by a town's settings: map tile coords (fractional)
        wx, wz = ox + pr['x'], oz + pr['z']
        # (on: the map tile whose height the model stands at, when not the one under its origin: Fortree's tree houses
        # stand on their walkway in front of the door, over the forest floor under the house; heights.STILTS)
        hx, hz = (ox + pr['on'][0], oz + pr['on'][1]) if 'on' in pr else (wx, wz)
        put((int(wx) // 32, int(wz) // 32), pr['res'], wx, wz, pr.get('rot', 0), pr.get('y', 0) + hgt(hx, hz))
    signed = set()                                      # (world tiles a sign model stands on)
    for s in sapphire['signs']:
        scfg = mc['signs'].get(s.get('script'))         # (hidden items etc. have no script here)
        if not scfg: continue
        wx, wz = ox + s['x'], oz + s['y']
        owner = zone_at(wx, wz)
        if owner != mc['zone']: print(f'warning: {name} sign at {wx, wz} lies in zone {owner}\'s cell')
        zones.setdefault(owner, new_zone())['signs'].append(
            dict(script=scfg['script'], cond=1, dir=scfg['dir'], rail=0, x=wx, z=wz, y=sign_y(wx, wz, scfg['dir'], hgt, world)))
        if 'model' in scfg: put((wx // 32, wz // 32), scfg['model'], wx + 0.5, wz + 0.5, y=hgt(wx, wz)); signed.add((wx, wz))
    if version.EMERALD:     # (emerald_world 2026-10-12) Emerald's signs stand where its own map has them; until its events
        # are ported (phase 3: data/sapphire/emerald), a solid sign tile that no sign above stands on gets Black 2's
        # signboard (res 152, the routes' and towns' sign) as scenery, never an invisible wall (b2tools/walk_diff.py OPEN)
        for y, row in enumerate(plan['tiles']):
            for x, c in enumerate(row):
                wx, wz = ox + x, oz + y
                if c != 'sign' or plan['walkable'][y][x] or (world.get((wx, wz)) or (0, ''))[1] != 'sign': continue
                if any((wx + dx, wz) in signed for dx in (-1, 0, 1)): continue
                put((wx // 32, wz // 32), 152, wx + 0.5, wz + 0.5, y=hgt(wx, wz)); signed.add((wx, wz))
    FACE = {'MOVEMENT_TYPE_FACE_LEFT': 2, 'MOVEMENT_TYPE_FACE_RIGHT': 3, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_UP': 0}
    for n in sapphire['npcs']:
        # settings by Sapphire script label, or "#<local id>" for objects without a script (Birch's chase)
        ncfg = mc['npcs'].get(f"#{n['local_id']}") or mc['npcs'].get(n['script'])
        if not ncfg: continue
        wander = {'MOVEMENT_TYPE_WANDER_AROUND': (3, 1, 1), 'MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT': (3, 1, 0)}.get(n['movement'])
        wx, wz = ox + n['x'], oz + n['y']
        npc = dict(model=ncfg['sprite'], script=ncfg['script'], flag=ncfg.get('flag', 0), move=wander[0] if wander else 0,
                   dir=ncfg.get('dir', FACE.get(n['movement'], 1)), areaw=n['range'][0] if wander and wander[1] else 0,
                   areah=n['range'][1] if wander and wander[2] else 0, x=wx, z=wz)
        mv = MOVE_CODES.npc(n['movement'], n['range'], n.get('gfx'))   # Sapphire's movement type -> Black 2's code (v165_fixes:
        if mv:                                             # look around, wander up/down / left/right, walk routes ...)
            npc.update(move=mv['move'], areaw=mv['areaw'], areah=mv['areah'])
            if 'dir' in mv and 'dir' not in ncfg: npc['dir'] = mv['dir']
        if 'uid' in ncfg: npc['uid'] = ncfg['uid']          # fixed actor id for scripts (ActorCmdExec etc.)
        if 'move' in ncfg: npc.update(move=ncfg['move'], areaw=0, areah=0)   # settings override Sapphire's (0 = stand)
        zones.setdefault(zone_at(wx, wz), new_zone())['npcs'].append(npc)
    for c in sapphire.get('coord_events', []):    # step triggers: Sapphire coord events with a var/value
        tcfg = mc.get('triggers', {}).get(c.get('script'))
        if not tcfg: continue
        wx, wz = ox + c['x'], oz + c['y']
        zones.setdefault(zone_at(wx, wz), new_zone()).setdefault('triggers', []).append(dict(
            script=tcfg['script'], value=tcfg['value'], work=int(str(tcfg['work']), 0), type=0, rail=0, x=wx, z=wz,
            w=1, h=1, y=hgt(wx, wz), unk=0))      # heights: a trigger fires within 2 units of its y (ov012 eventdata_system.c:849)
    for w in plan['warps']:
        if mp.get('standalone'):           # every warp of a warp-only map: a door in Sapphire's order (standalone_door)
            z.setdefault('doors', []).append(standalone_door(name, mp, w, hgt))
            continue
        slot = mc['warps'].get(w['dest'])
        room = INTERIORS.get(w['dest'])
        if slot is None and room and room['status'] in ('auto', 'b2', 'center', 'cave'):   # a door to a Hoenn interior: appended warp,
            wx, wz = ox + w['x'], oz + w['y']      # Black 2's door values (dir 2, type 3); the room's warps keep
            if sapphire_behaviour(name, w['x'], w['y']) == SHIP_STAIRS: wz -= 1    # (on the hull: see SHIP_STAIRS)
            arrow = {}
            if sapphire_behaviour(name, w['x'], w['y']) in ARROWS:   # an arrow warp (Lavaridge's Pokemon Center back door,
                (wx, wz), _, d, _ = warp_spot(name, mp, w)          # entered walking south): Black 2's walk-in warp on
                arrow = dict(dir=d, type=4)                          # the tile beyond the arrow (outdoor sweep 2026-10-07)
            z.setdefault('doors', []).append(dict(map=name, id=w['id'], dest_zone=room['zone'],  # Sapphire's order
                dest_warp=0 if room['status'] == 'b2' else int(w['dest_warp']), x=wx * 16 + 8, y=hgt(wx, wz) & 0xFFFF, z=wz * 16 + 8,
                **arrow, **({'parked': True} if room.get('doors_parked') else {})))
            # ("doors_parked", Emerald's Terra Cave: data/emerald/hoenn_interiors.json; emerald_caves 2026-10-12): the door
            # leads into the room but patches/hoenn_world.py parks it off the map; a zone init moves the one that is open
            # in (ObjInitWarpGPos index, x, y, z: Emerald's abnormal weather opens one of eight cave mouths at a time)
        elif slot is None and room and room['status'] == 'big' and os.path.exists(os.path.join(ROOT, 'data', 'interiors', f"{room['zone']}.json")):
            wx, wz = ox + w['x'], oz + w['y']      # a big room (several chunks, gyms_league): its door goes after
            z.setdefault('_big_doors', []).append(dict(map=name, id=w['id'], dest_zone=room['zone'],   # every other door,
                dest_warp=int(w['dest_warp']), x=wx * 16 + 8, y=hgt(wx, wz) & 0xFFFF, z=wz * 16 + 8))  # so no index moves
        elif slot is None and map_name(w['dest']) in STANDALONE:     # to a warp-only map: after every other door
            z.setdefault('_sa_doors', []).append(standalone_door(name, mp, w, hgt))
        elif slot is None and room and room['status'] == 'todo':    # (Emerald: a room not built yet, data/emerald/
            wx, wz = ox + w['x'], oz + w['y']                      # hoenn_interiors.json: a closed door, parked by
            z.setdefault('doors', []).append(dict(map=name, id=w['id'], dest_zone=None, dest_warp=None,   # hoenn_world.py,
                x=wx * 16 + 8, y=hgt(wx, wz) & 0xFFFF, z=wz * 16 + 8, unresolved=map_name(w['dest'])))   # in Sapphire's
            # order: Emerald's Battle Tents stand where the Contest Halls were (Slateport warp 3, Verdanturf 0, Fallarbor 1),
            # so every later door of the town keeps the index the shared rooms' exits name (b2tools/check_exits.py)
        if slot is not None and room and room['status'] in ('auto', 'center', 'big', 'cave'):   # a hand-made town's own
            z.setdefault('slot_doors', []).append(dict(map=name, id=w['id'], slot=slot,     # door slot (Oldale):
                dest_zone=room['zone'], dest_warp=int(w['dest_warp'])))                     # lead into the room
        if slot is None: continue
        z['warps'][slot] = [(ox + w['x']) * 16 + 8, hgt(ox + w['x'], oz + w['y']) & 0xFFFF, (oz + w['y']) * 16 + 8]   # (s16 in game)
    cx_, cz_ = ox + plan['size'][0] // 2, oz + plan['size'][1] // 2      # fly point: walkable tile near centre
    land = [k for k, v in world.items() if v[0] == name and v[2] and v[1] != 'sign' and v[1] not in WATER]
    best = min(land or [k for k, v in world.items() if v[0] == name],
               key=lambda k: abs(k[0] - cx_) + abs(k[1] - cz_))
    z['fly'] = list(best)

_PER = {}
def collision_y(d, lx, lz):
    """Height (units) of the collision plane at the centre of tile (lx, lz) of the cell written in directory d
    (ov036 FieldChunkAccessor_GetTerrainCore: y = -(nx*x - nz*z + d) / ny, x/z from the chunk centre), or None."""
    from terrain import heights as H                  # (Black 2's slope/offset tables; the module need not be enabled)
    if d not in _PER:
        p = os.path.join(d, 'collision.per')
        _PER[d] = open(p, 'rb').read() if os.path.exists(p) else None
    b = _PER[d]
    if b is None: return None
    a, i = struct.unpack_from('<HH', b, 4 + 8 * (lz * 32 + lx))
    if a & 3: return None                             # (two-triangle tiles: none on the overworld)
    nx, ny, nz = H.NORMALS[a >> 2]
    return -(nx * (lx * 16 - 248) - nz * (lz * 16 - 248) + H.OFFS[i]) / ny

DOOR_STEP = {2: (0, 1), 1: (0, -1), 3: (-1, 0), 4: (1, 0)}   # warp dir (walked into N/S/E/W) -> the tile walked from
def door_heights(zones, maps, cell_dir, alt_dir=None):
    """A door's y = the collision height of the tile the player walks in from. Black 2 fires a warp only within 2
    units of the player's y (ov012 eventdata_system.c CheckWarpPositionMatch; GetWarpIDByPlayerPos tests the tile in
    front at the player's own y) and puts an arriving player at the warp's y (GetGridWarpOutPos). The door tile's own
    height left the doors entered by surfing dead (the sea is 8 below its shore: Route 108's ship, Lilycove's cove,
    Route 120's Scorched Slab, Route 125's Shoal Cave) and Route 115's Meteor Falls mouth (its floor is a 32-unit
    plateau). Run after the cells are written: their collision is the truth. A door whose Sapphire warp tile lies
    outside its map (Slateport's harbour warp, x 40 of a 40-wide map: Sapphire never reaches it) keeps its y.
    cell_dir(cx, cz) -> cell directory; alt_dir(map, cx, cz) -> the same for a map whose doors exist only in another
    layout (alt_layouts: Route 131's Sky Pillar door is deep water until the post-game layout), or None."""
    for z in zones.values():
        for d in z.get('doors', []):
            mp = maps.get(d['map'])
            w = next((w for w in mp['plan']['warps'] if w['id'] == d['id']), None) if mp else None
            if w is None or not (0 <= w['x'] < mp['w'] and 0 <= w['y'] < mp['h']): continue
            dx, dz = DOOR_STEP.get(d.get('dir', 2), (0, 1))
            tx, tz = (d['x'] - 8) // 16 + dx, (d['z'] - 8) // 16 + dz
            cd = (alt_dir and alt_dir(d['map'], tx // 32, tz // 32)) or cell_dir(tx // 32, tz // 32)
            y = collision_y(cd, tx % 32, tz % 32) if cd else None
            if y is not None: d['y'] = round(y) & 0xFFFF
        for k, (x, y0, zz) in list(z['warps'].items()):        # hand-made towns' door slots: entered walking north
            tx, tz = (x - 8) // 16, (zz - 8) // 16 + 1
            cd = cell_dir(tx // 32, tz // 32)
            y = collision_y(cd, tx % 32, tz % 32) if cd else None
            if y is not None: z['warps'][k] = [x, round(y) & 0xFFFF, zz]

def park_spots(zones, cells, world):
    for zid, z in zones.items():          # where unused warp slots of the zone are parked: a solid tile it owns
        own = [c for c, zz in cells.items() if zz == zid]
        for c in own:
            blocked = lambda k: k not in world or not world[k][2] or world[k][1] in WATER
            spot = next(((c[0] * 32 + tx, c[1] * 32 + tz) for tz in range(32) for tx in range(32)
                         if blocked((c[0] * 32 + tx, c[1] * 32 + tz))), None)
            if spot: z['park'] = [spot[0] * 16 + 8, 0, spot[1] * 16 + 8]; break

def make_put(placements):
    def put(c, res, wx, wz, rot=0, y=0):  # wx, wz: world tile coordinates (fractional) of a model origin; rot in degrees
        lx, lz = (wx - c[0] * 32) * 16 - 256, (wz - c[1] * 32) * 16 - 256
        placements[c].append(struct.pack('<iiiH', round(lx * 4096), round(y * 4096), round(-lz * 4096),
                                         round(rot % 360 * 0x10000 / 360) & 0xFFFF) + bytes([res >> 8, res & 0xFF]))
    return put

def write_cell(d, m_name, c, world, trees, cfg_maps, placements, extra):
    """Build one cell into directory d: terrain.dae (+ texture images), collision.per, placements.bin, chunk.json."""
    texdir = os.path.join(ROOT, 'work', 'tex', 'area2')
    os.makedirs(d)
    m, per, grid = build_cell(m_name, c[0], c[1], world, trees, cfg_maps)
    for mat in m.tris:
        src = os.path.join(texdir, mat.replace('.', '_') + '.png')
        if os.path.exists(src): shutil.copy(src, os.path.join(d, mat + '.png'))
        else: feature_texture(mat).save(os.path.join(d, mat + '.png'))
    wraps = {t: w for f in FEATURES for t, w in getattr(f, 'WRAP', {}).items()}
    for k in ('lava_bank', 'lava_shore'):                 # (banks: repeat along the side, one image across)
        if GROUP.get(k): wraps[GROUP[k]] = ('WRAP', 'CLAMP')
    for old, new in GROUP.get('retex', {}).items():       # (a texture standing in for another keeps its wrap modes)
        if old in wraps: wraps[new] = wraps[old]
    for new, (_, src) in ASH_TEX.items():                 # (so does a snowy ash stand-in)
        if src in wraps: wraps[new] = wraps[src]
        elif src in ('kusa_ec1', 'kusa_ec2', 'kusa_ec3'): wraps[new] = ('WRAP', 'CLAMP')
    from nsbmd_fix import TREE_MATS                     # Black 2 lights every round-tree polygon as facing up
    m.normals = {t: (0, 1, 0) for t in TREE_MATS}       # (normal (0, 1, 0) in all its chunks), the cards too
    ntri = m.write(os.path.join(d, 'terrain.dae'), wrap=wraps | {t: ('WRAP', 'CLAMP') for t in m.tris if t in (
        'ki02ax', 'ki03ax', 'ki02c', 'ki03bx', 'ki03dx', 'michi01a', 'dansa01a', 'kusa_ec1', 'kusa_ec2', 'kusa_ec3')}
        | {'michi_hage': ('CLAMP', 'CLAMP')})
    open(os.path.join(d, 'collision.per'), 'wb').write(per)
    open(os.path.join(d, 'placements.bin'), 'wb').write(struct.pack('<I', len(placements[c])) + b''.join(placements[c]))
    json.dump(dict(cell=list(c), **extra, collision=grid, triangles=ntri), open(os.path.join(d, 'chunk.json'), 'w'), indent=1)
    return ntri

def main():
    global HF
    cfg, lay = load()
    world, trees, maps = compose(cfg, lay)
    for f in FEATURES:               # a module's retile(world, maps): Sapphire set pieces as other classes (terrain/ship.py)
        if hasattr(f, 'retile'): f.retile(world, maps)
    SOLID_AT.clear(); VOID.clear(); MAIN_NAMES.clear(); MAIN_NAMES.update(maps)
    for name, mp in maps.items():     # (doors to the warp-only maps: Black 2's warp tiles are solid, see warp_spot)
        for w in mp['plan']['warps']:
            if map_name(w['dest']) in STANDALONE: warp_spot(name, mp, w)
    HF = prepare(world, trees, maps, cfg)
    ash_tiles(world, maps); ash_ground(HF)
    hgt = lambda wx, wz: HF.y(int(wx), int(wz)) if HF else 0          # heights: ground height of a world tile
    built, ring = cells_needed(world)
    zone_of_map = {n: mc['zone'] for n, mc in cfg['maps'].items()}
    cells = {}
    kind = {n: mc.get('kind', 'route') for n, mc in cfg['maps'].items()}
    for c, counts in built.items():      # a town wins any cell it is in (banner, music, respawn), else most tiles
        towns = {n: k for n, k in counts.items() if kind.get(n) == 'town'}
        pick = towns or counts
        cells[c] = zone_of_map[max(pick, key=pick.get)]
    for c, nbrs in ring.items():
        best = max(nbrs, key=lambda n: sum(built[n].values()))
        cells[c] = cells[best]
    order = sorted(cells, key=lambda c: (c[1], c[0]))
    chunk_id = {c: cfg['first_chunk'] + i for i, c in enumerate(order)}
    W = max(c[0] for c in cells) + 1 + cfg['margin_cells']
    H = max(c[1] for c in cells) + 1 + cfg['margin_cells']
    W = max(W, lay_cells(lay, cfg)[0]); H = max(H, lay_cells(lay, cfg)[1])

    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(os.path.join(OUT, 'cells'))
    placements = {c: [] for c in order}
    zones = {}
    rects = zone_rects(maps, cells, cfg.get('pad_north'))   # sub-cell zones: every map's own zone up to its edges
    def zone_at(wx, wz): return zone_of(cells, wx, wz, rects)
    put = make_put(placements)
    for name, mp in maps.items():
        map_events(name, mp, zones, put, hgt, zone_at, world)
    for z in zones.values():              # big rooms' doors last (the other rooms' exits keep their door indices)
        if '_big_doors' in z: z.setdefault('doors', []).extend(z.pop('_big_doors'))
        if '_sa_doors' in z: z.setdefault('doors', []).extend(z.pop('_sa_doors'))    # then the warp-only maps'
    foreign_doors(zones, zone_at)
    park_spots(zones, cells, world)
    for c in order:     # building-model props drawn by terrain modules (ground.py: beach umbrellas), lifted like props
        for f in FEATURES:
            for res, wx, wz, rot, y in getattr(f, 'placements', lambda cell: [])(Cell(c[0], c[1], world)):
                put(c, res, wx, wz, rot, y + hgt(int(wx), int(wz)))
    n_open = open_uncovered(world, maps, placements, hgt)     # (building / sign tiles no model stands on: walkable)
    report = [f'warning: cell {c} has {len(p)} placements (a chunk holds 32; a building with a door counts 2)'
              for c, p in placements.items() if len(p) > 32] + [f'open_uncovered: {n_open} building/sign tiles walkable']
    for c in order:
        d = os.path.join(OUT, 'cells', f'{c[0]:02d}_{c[1]:02d}')
        ntri = write_cell(d, f'hoenn_{c[0]}_{c[1]}', c, world, trees, cfg['maps'], placements,
                          dict(chunk=chunk_id[c], zone=cells[c]))
        report.append(f'cell {c}: chunk {chunk_id[c]}, zone {cells[c]}, {ntri} triangles, {len(placements[c])} placements')
    cell_dir = lambda cx, cz: os.path.join(OUT, 'cells', f'{cx:02d}_{cz:02d}') if (cx, cz) in chunk_id else None
    alts = build_alts(cfg, lay, world, cells, chunk_id, rects)       # Route 131 after the game (alt_layouts)
    alt_at = {(a['map'], a['cx'], a['cz']): os.path.join(OUT, 'cells', a['dir']) for a in alts}
    door_heights(zones, maps, cell_dir, lambda name, cx, cz: alt_at.get((name, cx, cz)))
    standalone, sa_report = build_standalone(cfg, cfg['first_chunk'] + len(order), zones)
    nxt = max([chunk_id[c] for c in order] + [c['chunk'] for g in standalone for c in g['cells']]) + 1
    for a in alts: a['chunk'] = nxt; nxt += 1          # (after every other chunk: no chunk id moves)
    report += [f"alt cell ({a['cx']}, {a['cz']}): chunk {a['chunk']} for {a['base_chunk']} while map replace event "
               f"{a['event'] if a.get('event') is not None else hex(a.get('cond', 0))} is set ({a['map']} {a['layout']})" for a in alts]
    for g in standalone:                               # (a warp-only map's other layout, group_alts: after those)
        for a in g.get('alt_cells', []):
            a['chunk'] = nxt; nxt += 1
            report.append(f"{g['group']} alt cell ({a['cx']}, {a['cz']}): chunk {a['chunk']} for {a['base_chunk']} while "
                          f"map replace event {a['event']} is set ({a['map']} {a['layout']})")
    json.dump(dict(matrix=cfg['matrix'], width=W, height=H, area=cfg['area'],
                   cells=[dict(cx=c[0], cz=c[1], chunk=chunk_id[c], zone=cells[c]) for c in order],
                   zones={str(k): v for k, v in zones.items() if k is not None}, standalone=standalone,
                   **({'alt_cells': alts} if alts else {}), **({'zone_rects': rects} if rects else {})),
              open(os.path.join(OUT, 'world.json'), 'w'), indent=1)
    write_palettes(os.path.join(OUT, 'palettes.txt'))
    print(f'{len(order)} cells ({len(built)} with map tiles), matrix {W}x{H}, zones {sorted(z for z in zones if z)}')
    print('\n'.join(report + sa_report))

# ---- other layouts of a main-matrix map (data/hoenn_world.json "alt_layouts") ------------------------------------------
def build_alts(cfg, lay, world0, cells, chunk_id, rects=()):
    """Sapphire swaps a map's layout by script (setmaplayoutindex): Route 131 gets LAYOUT_UNKNOWN_MAP_08302970 (the Sky
    Pillar islet with its cave door, layout 320) in its OnTransition once FLAG_SYS_GAME_CLEAR is set. Black 2's way is
    its map replacement table (a/0/1/0, ov012 map_replace.c): an entry of kind 0 swaps one chunk id of a matrix for
    another while one of ten events is set (event uid i = work 0x4031+i == a fixed value; MapReplace_Patch runs when a
    matrix is loaded, MapReplaceSetEvent sets the work and can reload). So each alt layout builds the whole world again
    with the map's other plan (converter/plan_map.py with the layout) and every reader of Sapphire's map (heights,
    water, ground, the behaviours here) seeing that layout, and keeps the cells that come out different from the main
    ones (written to cells/alt_<map>_<cx>_<cz>; patches/hoenn_world.py appends them and the a/0/1/0 entries).
    The sea outside the maps stays the main world's (the swapped cells meet the main world's neighbours).
    Returns [dict(map, layout, event, cx, cz, base_chunk, dir)] ('chunk' is given by main())."""
    global HF
    import subprocess, io, contextlib
    from collections import defaultdict
    out, HF_main = [], HF
    for key, a in cfg.get('alt_layouts', {}).items():
        # (emerald_ch12_13 2026-10-12) several layouts of one map: entries "<Map>_<x>" naming their "map", each with
        # its own cells (alt_<key>_..) and a map replace condition "cond" instead of an event (Emerald's abnormal
        # weather: data/emerald/hoenn_world.json, patches/emerald_postgame.py); a plain entry's key is its map
        if key.startswith('_'): continue
        name = a.get('map', key)
        if name not in cfg['maps']: continue
        os.makedirs(os.path.join(OUT, 'alt_plans'), exist_ok=True)
        plan = os.path.join(OUT, 'alt_plans', f"{name}_{a['layout']}.json")
        subprocess.run([sys.executable, 'plan_map.py', os.path.join(ROOT, 'external', 'pokeruby'), name, a['layout'], plan],
                       cwd=os.path.join(ROOT, 'converter'), check=True, capture_output=True)
        fill = WATER_MOD._fill_cache.get(id(world0)) if WATER_MOD else None      # the main world's sea outside the maps
        log = io.StringIO()
        with sapphire_layout(name, a['layout']), contextlib.redirect_stdout(log):
            world, trees, maps = compose(cfg, lay, {name: plan})
            for f in FEATURES:
                if hasattr(f, 'retile'): f.retile(world, maps)
            for r in a.get('retile', []):   # Sapphire's art the plan classes can't say: the islet's rock is a mountain
                ox, oz = maps[name]['ox'], maps[name]['oz']                # ("box" + "from" classes, or "tiles")
                if 'tiles' in r: ks = [(ox + x, oz + z) for x, z in r['tiles']]
                else:
                    x0, z0, x1, z1 = r['box']
                    ks = [(ox + x, oz + z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)]
                for k in ks:
                    if k in world and world[k][1] in r['from']: world[k] = (name, r['to'], False)
            if WATER_MOD and fill is not None: WATER_MOD._fill_cache.clear(); WATER_MOD._fill_cache[id(world)] = fill
            if GROUND_MOD: getattr(GROUND_MOD, '_POS', {}).clear()     # (cell-keyed tile positions of the main world)
            HF = prepare(world, trees, maps, cfg)
            if HF_main and HF:          # tiles outside the maps keep the main world's heights: they take the nearest map
                def keep_main(k):          # (and its collision heights where it draws a tile otherwise: heights.coll_h)
                    HF.h[k] = HF_main.y(*k)
                    if k in getattr(HF_main, 'coll_h', {}): HF.coll_h[k] = HF_main.coll_h[k]
                    else: getattr(HF, 'coll_h', {}).pop(k, None)
                keys = set(HF_main.h) | set(HF.h) | set(getattr(HF_main, 'coll_h', {})) | set(getattr(HF, 'coll_h', {}))
                for k in keys:             # tile's, and the islet's raised rock at Route 131's north edge
                    if k not in world0: keep_main(k)   # lifted the open sea beyond it into walls
                if 'heights_box' in a:  # (postgame_maps) only this box of the map may change height: Route 103's cave
                    ox, oz = maps[name]['ox'], maps[name]['oz']; x0, z0, x1, z1 = a['heights_box']   # mouth's new shore
                    for k in keys:                            # moved heights.py's nearest-shore split of the sea west of
                        if world0.get(k, (None,))[0] == name and not (x0 <= k[0] - ox <= x1 and z0 <= k[1] - oz <= z1):
                            keep_main(k)                       # it by a few tiles (a step in the water elsewhere)
            ash_tiles(world, maps); ash_ground(HF)
            hgt = lambda wx, wz: HF.y(int(wx), int(wz)) if HF else 0
            near = {(x // 32 + dx, z // 32 + dz) for (x, z), e in world.items() if world0.get((x, z)) != e
                    for dx in (-1, 0, 1) for dz in (-1, 0, 1)} & set(chunk_id)
            placements = defaultdict(list); put = make_put(placements)
            zone_at = lambda wx, wz: zone_of(cells, wx, wz, rects)
            for n, mp in maps.items(): map_events(n, mp, {}, put, hgt, zone_at, world)
            for c in sorted(near, key=lambda c: (c[1], c[0])):
                for f in FEATURES:
                    for res, wx, wz, rot, y in getattr(f, 'placements', lambda cell: [])(Cell(c[0], c[1], world)):
                        put(c, res, wx, wz, rot, y + hgt(int(wx), int(wz)))
            for c in sorted(near, key=lambda c: (c[1], c[0])):
                m_name = f'hoenn_{c[0]}_{c[1]}'
                if WATER_MOD: getattr(WATER_MOD, '_HOLES', {}).pop(m_name, None)   # (holes are kept per model name)
                d = os.path.join(OUT, 'cells', f'alt_{key}_{c[0]:02d}_{c[1]:02d}')
                write_cell(d, m_name, c, world, trees, cfg['maps'], placements, dict(alt_of=chunk_id[c], zone=cells[c]))
                base = os.path.join(OUT, 'cells', f'{c[0]:02d}_{c[1]:02d}')
                if all(open(os.path.join(d, f), 'rb').read() == open(os.path.join(base, f), 'rb').read()
                       for f in ('terrain.dae', 'collision.per', 'placements.bin')):
                    shutil.rmtree(d); continue                         # (this cell is the same in both layouts)
                out.append(dict(map=name, layout=a['layout'], event=a.get('event'), cx=c[0], cz=c[1],
                                base_chunk=chunk_id[c], dir=os.path.basename(d), **({'cond': a['cond']} if 'cond' in a else {})))
                if WATER_MOD: getattr(WATER_MOD, '_HOLES', {}).pop(m_name, None)
        print(f"alt layout {key} {a['layout']}: cells {[(o['cx'], o['cz']) for o in out if o['layout'] == a['layout']]}")
    HF = HF_main
    return out

GROUND_MOD = next((f for f in FEATURES if f.__name__.endswith('ground')), None)
PALMS = next((f for f in FEATURES if f.__name__.endswith('palms')), None)     # terrain/palms.py: Mossdeep's palms

import contextlib as _ctx
@_ctx.contextmanager
def sapphire_layout(name, layout):
    """While it is open every reader of Sapphire's map `name` sees another of its layouts: gba.Repo.map_json (heights,
    ground, ash, the behaviours here) and water.py's own blockdata cache (its behaviour())."""
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    import gba
    orig = gba.Repo.map_json
    gba.Repo.map_json = lambda self, n, _o=orig: dict(_o(self, n), layout=layout) if n == name else _o(self, n)
    saved = [(_BEH, _BEH.pop(name, None))]
    if GROUND_MOD: saved.append((GROUND_MOD._SAP, GROUND_MOD._SAP.pop(name, None)))
    if WATER_MOD:
        WATER_MOD._load(); saved.append((WATER_MOD._grids, WATER_MOD._grids.pop(name, None)))
        # (through gba.Repo: a layout of data/hoenn_map_additions.json is a base layout + edits, not a file of its own)
        g, l = gba.world_repo().layout_grid(layout)
        for ts in (l['primary_tileset'], l['secondary_tileset']):
            if ts not in WATER_MOD._attrs: WATER_MOD._attrs[ts] = WATER_MOD._tileset_attrs(ts)
        WATER_MOD._grids[name] = (tuple(int(v) for v in g.reshape(-1)), l)
    try:
        yield
    finally:
        gba.Repo.map_json = orig
        for cache, old in saved:
            cache.pop(name, None)
            if old is not None: cache[name] = old

# ---- warp-only maps on their own matrices (data/hoenn_standalone.json) ----------------------------------------------
SOLID_AT = set()        # world tiles a warp stands on (Black 2's warp tiles are solid: its type-4 warps all sit on 01/81)
VOID = set()            # world tiles drawn as nothing (Sky Pillar's sky)
STANDALONE = {n for g in standalone_built() for n in standalone_cfg()['groups'][g]['maps']}   # maps built this run
MAIN_NAMES = set()
_MAPIDS = {}
def map_name(map_id):
    """pokeruby MAP_ id -> map folder name."""
    if not _MAPIDS:
        base = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps')
        for d in os.listdir(base):
            p = os.path.join(base, d, 'map.json')
            if os.path.exists(p): _MAPIDS[json.load(open(p))['id']] = d
        sys.path.insert(0, os.path.join(ROOT, 'converter'))       # (+ the event maps of other decomps:
        from gba import map_folders, world_map_folders              # data/hoenn_event_maps.json, events agent)
        for k, v in map_folders(os.path.join(ROOT, 'external', 'pokeruby')).items(): _MAPIDS.setdefault(k, v)
        if version.EMERALD:                                         # (+ Emerald's maps by their HoennB2 ids)
            for k, v in world_map_folders().items(): _MAPIDS.setdefault(k, v)
    return _MAPIDS.get(map_id, map_id)

_BEH = {}
def sapphire_behaviour(name, x, y):
    """Metatile behaviour name (MB_*) of Sapphire map `name` at map tile (x, y), or None outside it."""
    if name not in _BEH:
        sys.path.insert(0, os.path.join(ROOT, 'converter'))
        from gba import world_repo, MetatileRenderer
        import re
        repo = _BEH.setdefault('_repo', None) or world_repo()
        _BEH['_repo'] = repo
        if '_names' not in _BEH:
            _BEH['_names'] = {int(v, 0): k for k, v in re.findall(r'#define (MB_\w+)\s+(0x[0-9A-Fa-f]+|\d+)', open(
                os.path.join(ROOT, 'external', 'pokeruby', 'include', 'constants', 'metatile_behaviors.h')).read())}
        mj = repo.map_json(name); g, lay = repo.layout_grid(mj['layout'])
        _BEH[name] = (g, MetatileRenderer(repo, lay['primary_tileset'], lay['secondary_tileset']))
    g, mr = _BEH[name]
    if not (0 <= y < g.shape[0] and 0 <= x < g.shape[1]): return None
    return _BEH['_names'].get(mr.behavior(int(g[y, x]) & 0x3FF))

# Route 108's Abandoned Ship: Sapphire's stairs tile is a north arrow warp you stand on (MetatileBehavior_IsNorthArrowWarp)
# and walkable shallow water; Black 2's door goes on the hull tile north of it and the stairs tile stays the landing
# (terrain/ship.py), so a player leaving the ship on foot steps onto it, not onto the sea (ship_hideouts' finding)
SHIP_STAIRS = 'MB_STAIRS_OUTSIDE_ABANDONED_SHIP'
ARROWS = {'MB_NORTH_ARROW_WARP': ((0, -1), 2), 'MB_SOUTH_ARROW_WARP': ((0, 1), 1), 'MB_WATER_SOUTH_ARROW_WARP': ((0, 1), 1),
          'MB_WEST_ARROW_WARP': ((-1, 0), 4), 'MB_UNUSED_EAST_ARROW_WARP': ((1, 0), 3)}
def warp_spot(name, mp, w):
    """Where Black 2's warp for Sapphire warp w goes: (world tile of the warp, tile the player stands on, dir, arrow).
    Black 2's warps (type 3 doors, type 4 cave mouths/gates) sit on a solid tile and fire when the player walks into
    it (CheckWarpDirectionMatch, ov012 eventdata_system.c:210: dir 2 = walking north, 1 south, 4 west, 3 east; all its
    type-4 warps stand on 01/81 tiles [bytes]); arriving through one you step out of it (standalone_door). Sapphire's arrow warps are walkable
    tiles you stand on and press the arrow: the warp goes on the tile beyond (arrow = True). Doors (and Route 104's
    'deep south' warp into Petalburg Woods, entered walking south) are the warp tile itself, made solid (SOLID_AT)."""
    ox, oz = mp['ox'], mp['oz']
    beh = sapphire_behaviour(name, w['x'], w['y'])
    x, z = ox + w['x'], oz + w['y']
    if beh in ARROWS:
        (dx, dz), d = ARROWS[beh]
        return (x + dx, z + dz), (x, z), d, True
    SOLID_AT.add((x, z))
    if beh == 'MB_UNUSED_DEEP_SOUTH_WARP': return (x, z), (x, z - 1), 1, False
    return (x, z), (x, z + 1), 2, False

def standalone_door(name, mp, w, hgt):
    """The door dict (world.json zone 'doors') for Sapphire warp w of map `name`: to a room or cave (Black 2's door,
    type 3) or to another outdoor map (type 4, Black 2's route-to-route warp; resolved by patches/hoenn_world.py from
    to_map/to_id once every zone's door indices are known). Arriving through a type-4 warp puts you on its tile and
    walks you one step back out, against its direction [test: Petalburg Woods -> Route 104 (58,278), dir 2: you end on
    (58,279)], so an arrow warp's door on the tile beyond the arrow lands you on Sapphire's arrow tile."""
    (tx, tz), (sx, sz), d, arrow = warp_spot(name, mp, w)
    door = dict(map=name, id=w['id'], x=tx * 16 + 8, y=hgt(sx, sz) & 0xFFFF, z=tz * 16 + 8)
    room, dest = INTERIORS.get(w['dest']), map_name(w['dest'])
    if room and room['status'] in ('auto', 'b2', 'center', 'cave', 'big'):
        door.update(dest_zone=room['zone'], dest_warp=0 if room['status'] == 'b2' else int(w['dest_warp']), dir=2, type=3)
    elif str(w['dest']).startswith('B2_ZONE_'):    # a room of Black 2's own, by zone id: the PWT lobby (zone 192 warp 0,
        door.update(dest_zone=int(w['dest'][8:]), dest_warp=int(w['dest_warp']), dir=2, type=3)   # the island's PWT door,
        # data/hoenn_map_additions.json; battle_tower 2026-10-08)
    elif dest in STANDALONE or dest in MAIN_NAMES:
        door.update(dest_zone=None, dest_warp=None, to_map=dest, to_id=int(w['dest_warp']), dir=d, type=4)
    else:
        door.update(dest_zone=None, dest_warp=None, unresolved=dest)
    return door

def group_layout(g, sa):
    """Map origins inside the group's matrix and its size in cells: the walkable tiles plus 'margin' (what the
    camera sees), cut to whole cells; 'align' puts a group tile on a cell corner."""
    import math
    mh, mn, ms = g.get('margin', sa['margin'])
    plans = {n: json.load(open(version.plan_path(n))) for n in g['maps']}
    scenery = {'tree_bot', 'tree_top_l', 'tree_top_r', 'tree_tip', 'building', 'building_roof', 'mountain'}
    walk = [(gx + x, gz + y) for n, (gx, gz) in g['maps'].items() for y, row in enumerate(plans[n]['walkable'])
            for x, ok in enumerate(row) if ok and plans[n]['tiles'][y][x] not in scenery]
    x0, x1 = min(p[0] for p in walk) - mh, max(p[0] for p in walk) + mh
    z0, z1 = min(p[1] for p in walk) - mn, max(p[1] for p in walk) + ms
    if 'align' in g:
        offx = -x0 + (-(g['align'][0] - x0)) % 32
        offz = -z0 + (-(g['align'][1] - z0)) % 32
        cw, ch = math.ceil((x1 + offx + 1) / 32), math.ceil((z1 + offz + 1) / 32)
    else:
        cw, ch = math.ceil((x1 - x0 + 1) / 32), math.ceil((z1 - z0 + 1) / 32)
        offx = (cw * 32 - (x1 - x0 + 1)) // 2 - x0
        offz = (ch * 32 - (z1 - z0 + 1)) // 2 - z0
    return {n: (gx + offx, gz + offz) for n, (gx, gz) in g['maps'].items()}, plans, (cw, ch)

def compose_group(gname, g, sa, cfg, plans_over=None):
    """One standalone group as compose() does the main world: world[(x, z)] = (map, class, walkable) in the group's
    matrix tiles, trees, maps (with mp['standalone'] = True), the cells (all of the block) and the zone per cell.
    plans_over: {map: plan file} drawn instead of data/plans (group_alts: another layout; the group keeps the
    origins and size of its own plans)."""
    origins, plans, (cw, ch) = group_layout(g, sa)
    for n, p in (plans_over or {}).items(): plans[n] = json.load(open(p))
    world, trees, maps = {}, set(), {}
    inside = lambda k: 0 <= k[0] < cw * 32 and 0 <= k[1] < ch * 32
    retile, re_mt = g.get('retile', {}), {int(m, 16) for m in g.get('retile_metatiles', [])}
    for name, (ox, oz) in origins.items():
        plan = plans[name]; W, H = plan['size']
        grid = None
        if retile:
            sys.path.insert(0, os.path.join(ROOT, 'converter'))
            from gba import world_repo
            repo = world_repo(); grid = repo.layout_grid(repo.map_json(name)['layout'])[0]
        for y in range(H):
            for x in range(W):
                k = (ox + x, oz + y)
                if not inside(k): continue
                cls = plan['tiles'][y][x]
                if cls in retile and grid is not None and int(grid[y, x]) & 0x3FF in re_mt:
                    cls = retile[cls]
                if cls == 'void': VOID.add(k); continue
                world[k] = (name, cls, plan['walkable'][y][x])
        for x, y in plan['trees']:
            if all(inside((ox + x + dx, oz + y + dz)) for dx in (0, 1) for dz in (0, 1)): trees.add((ox + x, oz + y))
        maps[name] = dict(ox=ox, oz=oz, plan=plan, cfg=cfg['standalone'][name], w=W, h=H, standalone=True)
        retile_map(world, name, maps[name])
    if g.get('order'):              # (the order its maps put their doors into the zone: 'order', else 'maps' order)
        maps = {n: maps[n] for n in g['order'] + [n for n in maps if n not in g['order']]}
    border = g.get('border', 'forest')
    if border not in ('forest', 'void'):
        # the cells around the map as Sapphire's border blocks fill the screen beyond a map's edge: rock or sea,
        # unwalkable; heights.py raises rock like any cliff top (its Sapphire metatile: the layout's border block)
        import numpy as np
        sys.path.insert(0, os.path.join(ROOT, 'converter'))
        from gba import world_repo
        repo = world_repo()
        name0 = next(iter(origins))
        lay = repo.layouts[repo.map_json(name0)['layout']]
        blk = np.frombuffer(open(os.path.join(repo.root, lay['border_filepath']), 'rb').read(), dtype='<u2')
        ts = (lay['primary_tileset'], lay['secondary_tileset'])
        ox0, oz0 = origins[name0]
        bt = maps[name0].setdefault('border', {})
        for tz in range(ch * 32):
            for tx in range(cw * 32):
                k = (tx, tz)
                if k in world or k in VOID: continue
                world[k] = (name0, border, False)
                bt[k] = (ts, int(blk[((tz - oz0) & 1) * 2 + ((tx - ox0) & 1)]) & 0x3FF)
    elif border == 'void':
        for tz in range(ch * 32):
            for tx in range(cw * 32):
                if (tx, tz) not in world: VOID.add((tx, tz))
    cells = {}
    for cz in range(ch):
        for cx in range(cw):
            count = {}
            for tz in range(cz * 32, cz * 32 + 32):
                for tx in range(cx * 32, cx * 32 + 32):
                    e = world.get((tx, tz))
                    if e: count[e[0]] = count.get(e[0], 0) + 1
            n = max(count, key=count.get) if count else next(iter(origins))
            cells[(cx, cz)] = cfg['standalone'][n]['zone']
    return world, trees, maps, cells, (cw, ch)

def build_standalone(cfg, first_chunk, main_zones):
    """Every standalone group: its cells (cells/s_<group>_<cx>_<cz>/; identical cells, e.g. open forest or sea, share
    one chunk), zones (doors in Sapphire's order) and matrix entry for patches/hoenn_world.py."""
    global HF
    sa = standalone_cfg()
    out, report, seen, chunk = [], [], {}, first_chunk
    built = standalone_built()
    for gname, g in sa['groups'].items():
        if not all(n in cfg['standalone'] for n in g['maps']) or gname not in built: continue
        SOLID_AT.clear(); VOID.clear(); GROUP.clear(); GROUP.update(g)
        EXTRA_TEX.update({t: int(ts) for t, ts in g.get('textures', {}).items()})
        if WATER_MOD:          # the water module cuts the flat ground over water by texture name when a model is
            g0 = WATER_GROUND  # written: the group's stand-in ground textures are ground too
            WATER_MOD.GROUND = tuple(g0) + tuple(sorted((set(g.get('ground', {}).values()) |
                                                        {v for k, v in g.get('retex', {}).items() if k in g0}) - set(g0)))
        world, trees, maps, cells, (cw, ch) = compose_group(gname, g, sa, cfg)
        for f in FEATURES:           # (module retile hooks, as for the main matrix: the Safari Zone's bumpy slopes)
            if hasattr(f, 'retile'): f.retile(world, maps)
        register_origins(maps)
        for name, mp in maps.items():
            for w in mp['plan']['warps']: warp_spot(name, mp, w)      # (marks the solid warp tiles)
        HF = prepare(world, trees, maps, {})
        ash_tiles(world, maps); ash_ground(HF)
        if HF: lift_field(HF, world, cw, ch)
        if HF and g.get('clamp_south'):
            starts = [warp_spot(n, mp, w)[1] for n, mp in maps.items() for w in mp['plan']['warps']]
            clamp_south(HF, world, g['clamp_south'], starts)
        hgt = lambda wx, wz: HF.y(int(wx), int(wz)) if HF else 0
        order = sorted(cells, key=lambda c: (c[1], c[0]))
        placements = {c: [] for c in order}
        zones = {}
        zone_at = lambda wx, wz: cells.get((int(wx) // 32, int(wz) // 32))
        put = make_put(placements)
        for name, mp in maps.items():
            map_events(name, mp, zones, put, hgt, zone_at, world)
        park_spots(zones, cells, world)
        for c in order:
            for f in FEATURES:
                for res, wx, wz, rot, y in getattr(f, 'placements', lambda cell: [])(Cell(c[0], c[1], world)):
                    put(c, res, wx, wz, rot, y + hgt(int(wx), int(wz)))
        n_open = open_uncovered(world, maps, placements, hgt, gname)   # (building / sign tiles no model stands on)
        report += [f'warning: {gname} cell {c} has {len(p)} placements (a chunk holds 32)' for c, p in placements.items() if len(p) > 32]
        if n_open: report.append(f'{gname} open_uncovered: {n_open} building/sign tiles walkable')
        gcells = []
        for c in order:
            d = os.path.join(OUT, 'cells', f's_{gname}_{c[0]:02d}_{c[1]:02d}')
            m_name = f'hoenn_s_{gname}_{c[0]}_{c[1]}'
            ntri = write_cell(d, m_name, c, world, trees, maps_cfg(maps), placements, dict(group=gname, zone=cells[c]))
            # identical cells (open forest, sea, rock) share one chunk: the model's name is the only difference
            dae = os.path.join(d, 'terrain.dae')
            text = open(dae).read().replace(f'"{m_name}"', '"hoenn_s"')
            open(dae, 'w').write(text)
            import hashlib
            key = hashlib.sha1(b''.join(open(os.path.join(d, f), 'rb').read() for f in ('terrain.dae', 'collision.per',
                                                                                    'placements.bin'))).hexdigest()
            if key in seen:
                shutil.rmtree(d); cid, dname = seen[key]
            else:
                cid, dname = chunk, os.path.basename(d); seen[key] = (cid, dname); chunk += 1
            gcells.append(dict(cx=c[0], cz=c[1], chunk=cid, zone=cells[c], dir=dname))
            report.append(f'{gname} cell {c}: chunk {cid}, zone {cells[c]}, {ntri} triangles, {len(placements[c])} placements')
        gdir = {(g_['cx'], g_['cz']): os.path.join(OUT, 'cells', g_['dir']) for g_ in gcells}
        door_heights(zones, maps, lambda cx, cz: gdir.get((cx, cz)))
        galts = group_alts(gname, g, sa, cfg, gcells) if any(n in cfg.get('alt_layouts', {}) for n in g['maps']) else []
        for zid, z in zones.items():
            z['group'] = gname
            main_zones[zid] = z
        out.append(dict(group=gname, width=cw, height=ch, area=g.get('area', sa['area']), cells=gcells,
                        **({'srt_anim': g['srt_anim']} if 'srt_anim' in g else {}),
                        origins={n: [mp['ox'], mp['oz']] for n, mp in maps.items()},
                        effect=g.get('effect', sa.get('effect', 1)), bgm_zone=g.get('bgm_zone'),
                        textures={t: int(ts) for t, ts in g.get('textures', {}).items()},
                        **({'alt_cells': galts} if galts else {})))
        print(f'standalone {gname}: {cw}x{ch} cells, zones {sorted(zones)}')
    GROUP.clear(); ASH_TREES.clear(); ASH_NEAR.clear(); ASH_GRASS.clear(); ASH_GROUND.clear(); ASH_LIP.clear()
    if WATER_MOD: WATER_MOD.GROUND = WATER_GROUND
    return out, report

def group_alts(gname, g, sa, cfg, gcells):
    """Other layouts of a warp-only map: build_alts for a standalone group (an "alt_layouts" entry that names one of the
    group's maps; Emerald's Jagged Pass mouth, emerald_integrate 2026-10-12; Sapphire and Ruby have none, so nothing
    runs for them). The group is composed again with the map's other plan (same origins and size), built as
    build_standalone builds it, its heights kept outside 'heights_box' (map tiles, when given); the cells that differ
    from the group's own go to cells/s_<group>_alt_<map>_<cx>_<cz> and patches/hoenn_world.py swaps their chunks on the
    group's matrix (a/0/1/0 kind 0) while map replace event 'event' is set. Kind 0 swaps every use of a chunk in the
    matrix, so a cell whose chunk the group shares with another (identical cells) stops the build.
    Returns [dict(map, layout, event, cx, cz, base_chunk, dir)] ('chunk' is given by main())."""
    global HF
    import subprocess
    HF_base, out = HF, []
    base = {(c['cx'], c['cz']): c for c in gcells}
    uses = {}
    for c in gcells: uses[c['chunk']] = uses.get(c['chunk'], 0) + 1
    for name in g['maps']:
        a = cfg.get('alt_layouts', {}).get(name)
        if not a: continue
        os.makedirs(os.path.join(OUT, 'alt_plans'), exist_ok=True)
        plan = os.path.join(OUT, 'alt_plans', f"{name}_{a['layout']}.json")
        subprocess.run([sys.executable, 'plan_map.py', os.path.join(ROOT, 'external', 'pokeruby'), name, a['layout'], plan],
                       cwd=os.path.join(ROOT, 'converter'), check=True, capture_output=True)
        with sapphire_layout(name, a['layout']):
            SOLID_AT.clear(); VOID.clear()
            world, trees, maps, cells, (cw, ch) = compose_group(gname, g, sa, cfg, {name: plan})
            for f in FEATURES:
                if hasattr(f, 'retile'): f.retile(world, maps)
            register_origins(maps)
            for n, mp in maps.items():
                for w in mp['plan']['warps']: warp_spot(n, mp, w)
            if GROUND_MOD: getattr(GROUND_MOD, '_POS', {}).clear()
            HF = prepare(world, trees, maps, {})
            ash_tiles(world, maps); ash_ground(HF)
            if HF: lift_field(HF, world, cw, ch)
            if HF and g.get('clamp_south'):
                starts = [warp_spot(n, mp, w)[1] for n, mp in maps.items() for w in mp['plan']['warps']]
                clamp_south(HF, world, g['clamp_south'], starts)
            if HF and HF_base and 'heights_box' in a:      # only this box of the map may change height (as build_alts)
                ox, oz = maps[name]['ox'], maps[name]['oz']; x0, z0, x1, z1 = a['heights_box']
                keys = set(HF_base.h) | set(HF.h) | set(getattr(HF_base, 'coll_h', {})) | set(getattr(HF, 'coll_h', {}))
                for k in keys:
                    if x0 <= k[0] - ox <= x1 and z0 <= k[1] - oz <= z1: continue
                    HF.h[k] = HF_base.y(*k)
                    if k in getattr(HF_base, 'coll_h', {}): HF.coll_h[k] = HF_base.coll_h[k]
                    else: getattr(HF, 'coll_h', {}).pop(k, None)
            hgt = lambda wx, wz: HF.y(int(wx), int(wz)) if HF else 0
            order = sorted(cells, key=lambda c: (c[1], c[0]))
            placements = {c: [] for c in order}
            zones = {}
            zone_at = lambda wx, wz: cells.get((int(wx) // 32, int(wz) // 32))
            put = make_put(placements)
            for n, mp in maps.items():
                map_events(n, mp, zones, put, hgt, zone_at, world)
            park_spots(zones, cells, world)
            for c in order:
                for f in FEATURES:
                    for res, wx, wz, rot, y in getattr(f, 'placements', lambda cell: [])(Cell(c[0], c[1], world)):
                        put(c, res, wx, wz, rot, y + hgt(int(wx), int(wz)))
            open_uncovered(world, maps, placements, hgt, gname)
            for c in order:
                m_name = f'hoenn_s_{gname}_{c[0]}_{c[1]}'
                if WATER_MOD: getattr(WATER_MOD, '_HOLES', {}).pop(m_name, None)
                d = os.path.join(OUT, 'cells', f's_{gname}_alt_{name}_{c[0]:02d}_{c[1]:02d}')
                write_cell(d, m_name, c, world, trees, maps_cfg(maps), placements,
                           dict(group=gname, zone=cells[c], alt_of=base[c]['chunk']))
                dae = os.path.join(d, 'terrain.dae')            # (the group's cells are written as one model name)
                text = open(dae).read().replace(f'"{m_name}"', '"hoenn_s"')
                open(dae, 'w').write(text)
                if WATER_MOD: getattr(WATER_MOD, '_HOLES', {}).pop(m_name, None)
                bd = os.path.join(OUT, 'cells', base[c]['dir'])
                if all(open(os.path.join(d, f), 'rb').read() == open(os.path.join(bd, f), 'rb').read()
                       for f in ('terrain.dae', 'collision.per', 'placements.bin')):
                    shutil.rmtree(d); continue                   # (this cell is the same in both layouts)
                assert uses[base[c]['chunk']] == 1, (f'{gname} cell {c}: its chunk {base[c]["chunk"]} is shared by '
                                                     f'{uses[base[c]["chunk"]]} cells, a map replacement would swap them all')
                out.append(dict(map=name, layout=a['layout'], event=a['event'], cx=c[0], cz=c[1],
                                base_chunk=base[c]['chunk'], dir=os.path.basename(d)))
        print(f"alt layout {name} {a['layout']} (group {gname}): cells {[(o['cx'], o['cz']) for o in out if o['map'] == name]}")
    HF = HF_base
    return out

WATER_MOD = next((f for f in FEATURES if f.__name__.endswith('water') and hasattr(f, 'GROUND')), None)
WATER_GROUND = tuple(WATER_MOD.GROUND) if WATER_MOD else ()

def lift_field(F, world, cw, ch):
    """Stand a group's lowest walkable ground at y 0: heights.py anchors a map without sea at its biggest region's
    Sapphire level, which left Mt. Pyre's foot at -192 (the bottom of Black 2's flat height table, notes/GEN5_MAPS.md)
    and Mt. Chimney's at -80; the main matrix's ground lies at 0..160, and water needs a height 8 below its shore."""
    low = min((F.y(*k) for k, e in world.items() if e[2]), default=0)
    d = -(low // 16 * 16)
    if not d: return
    F.h = {(x, z): F.y(x, z) + d for z in range(ch * 32) for x in range(cw * 32)}
    F.slope = {k: (side, y0 + d, rise) for k, (side, y0, rise) in F.slope.items()}
    F.coll_h = {k: v + d for k, v in getattr(F, 'coll_h', {}).items()}   # (collision heights drawn otherwise rise too)
    print(f'heights: group raised by {d}')

def clamp_south(F, world, rows, starts=()):
    """Scenery that would stand in front of the camera (group option 'clamp_south'): an unwalkable tile less than
    `rows` rows south of walkable ground and higher than it is lowered to that ground's height. Sapphire draws a
    mountain top from above (Mt. Chimney: the slopes south of the station plaza go down); heights.py raises
    unwalkable rock and its trees as cliff tops, which put an 80-96 unit plateau of trees right in front of the
    camera south of the plaza (the player was hidden at the station door, tested). Black 2 never puts anything
    high just south of a walkway (its camera looks north at 40 degrees). Walkable tiles no warp reaches (Sapphire
    marks scattered rock tiles in Mt. Chimney's cliffs passable: an 80-unit pillar of them stood in front of the
    station door) count as scenery."""
    walk = {k for k, e in world.items() if e[2]}
    if starts:                                       # (only what the player can reach from the group's warps)
        from collections import deque
        seen = {s for s in starts if s in walk}; q = deque(seen)
        while q:
            x, z = q.popleft()
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in walk and n not in seen: seen.add(n); q.append(n)
        walk = seen
    low = {}
    for (x, z) in walk:
        if (x, z) in F.slope: continue
        for d in range(1, rows):
            k = (x, z + d)
            if k in walk or k not in world or world[k][1] in WATER or k in F.slope: continue
            h = F.y(x, z)
            if F.y(*k) > h and (k not in low or low[k] > h): low[k] = h
    rock = lambda k: world[k][1] in ('cliff', 'cliff_top', 'mountain') and not world[k][2]
    for k, h in low.items():
        # (walkability 2026-10-11: rock comes down to one level above the walkway, not to it: lowered all the way it lay
        # flat and blocked beside the path, an invisible wall - b2tools/walk_diff.py OPEN, heights.py 9d)
        F.h[k] = h + 16 if rock(k) and F.y(*k) >= h + 16 else h
    print(f'heights: {len(low)} scenery tiles south of walkways lowered')

def maps_cfg(maps):
    return {n: mp['cfg'] for n, mp in maps.items()}

def register_origins(maps):
    """Tell the terrain modules where the group's maps lie (they look Sapphire's metatile behaviours up by world tile:
    water.behaviour, ground.sapphire_behaviour, which only know the main matrix's maps by themselves)."""
    for f in FEATURES:
        if f.__name__.endswith('water'):
            f._load()
            for n, mp in maps.items(): f._origins[n] = (mp['ox'], mp['oz'], 0)
        if f.__name__.endswith('ground'):
            f.sapphire_behaviour(next(iter(maps)), -1, -1)
            if f._SAP.get('origins') is not None:
                for n, mp in maps.items(): f._SAP['origins'][n] = (mp['ox'], mp['oz'])

def standalone_frames(cfg):
    """[(group, world, maps, owner)] for the converters (gen_map_content, gen_encounters): every standalone group
    composed as build_standalone does, owner = zone per cell of the group's own matrix. All groups, built this run or
    not, so the generated content and encounter tables don't change with the build switch (standalone_built)."""
    sa = standalone_cfg(); out = []
    for gname, g in sa['groups'].items():
        if not all(n in cfg['standalone'] for n in g['maps']): continue
        SOLID_AT.clear(); VOID.clear()
        world, trees, maps, cells, _ = compose_group(gname, g, sa, cfg)
        out.append((gname, world, maps, dict(cells)))
    SOLID_AT.clear(); VOID.clear()
    return out

_tex_cache = {}
def feature_texture(name):
    """PNG image of a texture a terrain module takes from a Black 2 map texture set (for the DAE; the game binds
    textures by name from the area's set, see patches/hoenn_textures.py)."""
    import b2files, nsbtx
    src = name
    if name in ASH_TEX: ts, src = ASH_TEX[name]        # (a snowy stand-in: Black 2's texture of another name)
    else: ts = EXTRA_TEX.get(name) or next(f.TEXTURES[name] for f in FEATURES if name in getattr(f, 'TEXTURES', {}))
    if ts not in _tex_cache:
        files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
        btx = b2files.map_textures(files, ts) if isinstance(ts, int) else b2files.building_textures(files, int(ts[3:]))
        _tex_cache[ts] = {n: img for n, img, _ in nsbtx.decode(btx)}   # ('ext<N>': exterior building set a/1/7/4 N)
    return _tex_cache[ts][src]

def write_palettes(path):
    """Texture -> palette pairs for ToNsbmd: the slice's list plus every terrain module's textures."""
    lines = open(os.path.join(ROOT, 'data', 'palettes', 'area2_terrain.txt')).read().rstrip('\n').split('\n')
    for f in FEATURES:
        for t in getattr(f, 'TEXTURES', {}):
            lines.append(f"{t} {getattr(f, 'PALETTES', {}).get(t, t + '_pl')}")
    for t in sorted(EXTRA_TEX): lines.append(f'{t} {t}_pl')       # (standalone groups' textures: '_pl' checked there)
    for t in sorted(ASH_TEX): lines.append(f'{t} {t}_pl')         # (snowy ash, data/hoenn_ash.json)
    open(path, 'w').write('\n'.join(lines) + '\n')

def lay_cells(lay, cfg):
    M = cfg['margin_cells']
    mx = max((m['tile_x'] + m['w'] - 1) // 32 for m in lay.values())
    mz = max((m['tile_z'] + m['h'] - 1) // 32 for m in lay.values())
    return mx + 1 + 2 * M, mz + 1 + 2 * M

if __name__ == '__main__':
    main()
