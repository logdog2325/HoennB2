"""Turn one Sapphire map into a build plan for Black 2 (data/plans/<Map>.json).

    python3 plan_map.py ../external/pokeruby LittlerootTown
    python3 plan_map.py ../external/pokeruby Route131 LAYOUT_UNKNOWN_MAP_08302970 OUT.json   (another layout of the
        map, with the map's own events, written to OUT.json: b2tools/world.py "alt_layouts", Route 131 after the game)

Uses converter/metatiles.json (hand-checked ids) first; tiles with the collision bit that belong to a building
(warp-door inside, >= 6 connected tiles) become building footprints. Anything not covered is listed under
"unclassified" so it can be added to the table instead of guessed.
"""
import sys, json, os
from collections import deque
from gba import Repo, world_repo


root, name = sys.argv[1], sys.argv[2]
alt_layout, alt_out = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else (None, None)
r = world_repo(root)           # (HOENN_VERSION=emerald: Emerald's map of that name, converter/gba.py world_repo)
here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(here, '..', 'b2tools'))
import version
table = json.load(open(os.path.join(here, 'metatiles.json')))
# labels from the Phase A workflow (data/labels/<tileset>.json, verified); hand-checked metatiles.json wins on overlap
import glob
for f in sorted(glob.glob(os.path.join(here, '..', 'data', 'labels', 'gTileset_*.json')) +
               glob.glob(os.path.join(here, '..', 'data', 'labels', 'emerald_*.json'))):   # (event maps' tilesets)
    for ts, ids in json.load(open(f)).items():
        if ts.startswith('_'): continue
        for k, v in ids.items(): table.setdefault(ts, {}).setdefault(k, v)
# Emerald's world (emerald_world 2026-10-12): pokeemerald's own tilesets (plain names) take only Emerald's labels,
# data/labels/emerald/: carry_<tileset>.json (converter/emerald_labels.py: Sapphire's label where the metatile is
# Sapphire's, drawn the same or standing where Sapphire has it) under <tileset>.json (labelled by eye, wins)
EMERALD_TABLE = {}
if version.is_emerald():
    ed = os.path.join(here, '..', 'data', 'labels', 'emerald')
    for f in sorted(glob.glob(os.path.join(ed, 'carry_*.json'))) + sorted(f for f in glob.glob(os.path.join(ed, '*.json'))
                                                                           if not os.path.basename(f).startswith('carry_')):
        for ts, ids in json.load(open(f)).items():
            if not ts.startswith('_'): EMERALD_TABLE.setdefault(ts, {}).update(ids)
mj = r.map_json(name); grid, layout = r.layout_grid(alt_layout or mj['layout'])
H, W = grid.shape
prim, sec = layout['primary_tileset'], layout['secondary_tileset']

_same = {}
def same_as_ruby(ts, m):
    """An event map's namespaced tileset ('emerald:gTileset_General', converter/gba.py): True when metatile m behaves as
    Ruby's same tileset's m and is drawn the same (Emerald's General retouched some art: grass, trees, flowers differ in
    under 200 of 256 pixels; a metatile replaced by other art differs in all of them): Ruby's label then holds."""
    if ':' not in ts: return False
    if ts not in _same:
        import numpy as np
        from gba import MetatileRenderer
        try:
            rr = Repo(os.path.join(here, '..', 'external', 'pokeruby'))
            pr, se = (p.split(':', 1)[1] for p in (prim, sec))
            _same[ts] = (MetatileRenderer(r, prim, sec), MetatileRenderer(rr, pr, se), np)
        except FileNotFoundError:
            _same[ts] = None
    if not _same[ts]: return False
    me, mr, np = _same[ts]
    diff = (np.abs(me.render(m)[..., :3].astype(int) - mr.render(m)[..., :3].astype(int)).sum(-1) > 0).sum()
    return bool(diff < 200 and me.behavior(m) == mr.behavior(m))

def lookup(m):
    ts = prim if m < 0x200 else sec
    if r.emerald and ':' not in ts: return EMERALD_TABLE.get(ts, {}).get(f'{m:03x}')
    c = table.get(ts, {}).get(f'{m:03x}')
    if c is None and same_as_ruby(ts, m):     # (events agent) an Emerald metatile identical to Ruby's: Ruby's label
        c = table.get(ts.split(':', 1)[1], {}).get(f'{m:03x}')
    return c

cls = [[None] * W for _ in range(H)]
solid = [[bool((int(grid[y, x]) >> 10) & 3) for x in range(W)] for y in range(H)]
unclassified = {}
for y in range(H):
    for x in range(W):
        m = int(grid[y, x]) & 0x3FF
        c = lookup(m)
        if c is None:
            c = 'blocked' if solid[y][x] else 'unknown'
            unclassified.setdefault(f'{m:03x}', []).append([x, y])
        cls[y][x] = c

# buildings: connected solid building tiles (labelled building/door/building_roof, or unlisted 'blocked') that
# contain a warp, plus the non-solid roof rows above
BUILDING = ('blocked', 'building', 'door', 'building_roof')
is_bld = lambda x, y: solid[y][x] and cls[y][x] in BUILDING
warps = mj.get('warp_events', [])
seen = set(); buildings = []
for y in range(H):
    for x in range(W):
        if not is_bld(x, y) or (x, y) in seen: continue
        comp, q = [], deque([(x, y)]); seen.add((x, y))
        while q:
            cx, cy = q.popleft(); comp.append((cx, cy))
            for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and is_bld(nx, ny):
                    seen.add((nx, ny)); q.append((nx, ny))
        xs = [c[0] for c in comp]; ys = [c[1] for c in comp]
        door = next((w for w in warps if (w['x'], w['y']) in set(comp)), None)
        if door is None or len(comp) < 6:
            continue
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        # roof rows: unlisted, non-solid tiles directly above the footprint
        roof = 0
        while y0 - roof - 1 >= 0 and all(cls[y0 - roof - 1][cx] in ('unknown', 'building_roof', 'building')
                                         and not solid[y0 - roof - 1][cx] for cx in range(x0, x1 + 1)):
            roof += 1
        for cx, cy in comp: cls[cy][cx] = 'building'
        for ry in range(y0 - roof, y0):
            for cx in range(x0, x1 + 1): cls[ry][cx] = 'building_roof'
        dest = door['dest_map']
        kind = ('center' if 'POKEMON_CENTER' in dest else 'mart' if 'MART' in dest else
                'lab' if 'LAB' in dest else 'house')
        buildings.append(dict(kind=kind, footprint=[x0, y0, x1, y1], roof_rows=roof, door=[door['x'], door['y']],
                              dest=dest, metatiles=[[f'{int(grid[cy, cx]) & 0x3FF:03x}' for cx in range(x0, x1 + 1)]
                                                    for cy in range(y0 - roof, y1 + 1)]))

trees = []
for y in range(H):
    for x in range(W - 1):
        if cls[y][x] == 'tree_top_l' and cls[y][x + 1] == 'tree_top_r':
            trees.append([x, y])
for x in range(W - 1):  # trees whose top half is above the map edge
    if cls[0][x] == 'tree_bot' and cls[0][x + 1] == 'tree_bot' and not any(t == [x, -1] for t in trees) \
            and (x == 0 or [x - 1, -1] not in trees):
        trees.append([x, -1])
tips_below = [[x, H] for x in range(W - 1) if cls[H - 1][x] == 'tree_tip' and cls[H - 1][x + 1] == 'tree_tip' and x % 2 == 0]

left = {k: v for k, v in unclassified.items() if any(cls[y][x] in ('unknown', 'blocked') for x, y in v)}
elev_grid = [[(int(grid[y, x]) >> 12) & 0xF for x in range(W)] for y in range(H)]
if mj.get('_decomp'):
    # (events agent) Emerald's event islands mark much of their walkable ground "any level" (elevation 0: Faraway
    # Island's forest, its puddles and the paths between them) where Ruby uses it only for stairs and bridges: b2tools/
    # terrain/heights.py then splits one level into regions it can't join (it joins regions only across two Sapphire
    # levels) and stood the forest 64 units below its own path (tested: the player could not step on). Here such a tile
    # takes the most common elevation of its walkable neighbours (repeated until stable); stairs and bridges keep 0.
    from collections import Counter
    changed = True
    while changed:
        changed = False
        for y in range(H):
            for x in range(W):
                if solid[y][x] or elev_grid[y][x] != 0 or cls[y][x] in ('stairs', 'bridge'): continue
                c = Counter(elev_grid[ny][nx] for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                            if 0 <= nx < W and 0 <= ny < H and not solid[ny][nx] and elev_grid[ny][nx] not in (0, 15))
                if c: elev_grid[y][x] = c.most_common(1)[0][0]; changed = True
plan = dict(map=name, size=[W, H], tilesets=[prim, sec],
            tiles=[[cls[y][x] for x in range(W)] for y in range(H)],
            walkable=[[not solid[y][x] for x in range(W)] for y in range(H)],
            # Sapphire's elevation per tile (blockdata bits 12-15): 0 = any-level transition (stairs), 1 = water/surf
            # level, 3 = ground, 4+ = higher ground, 15 = bridge (both levels); used by b2tools/terrain/heights.py
            elevation=elev_grid,
            trees=trees, trees_below_edge=tips_below, buildings=buildings,
            signs=[dict(x=b['x'], y=b['y'], script=b.get('script')) for b in mj.get('bg_events', []) if b.get('type') == 'sign'],
            warps=[dict(id=i, x=w['x'], y=w['y'], dest=w['dest_map'], dest_warp=w['dest_warp_id']) for i, w in enumerate(warps)],
            connections=mj.get('connections'), unclassified=left)
out = alt_out or (version.plan_path(name) if r.emerald else os.path.join(here, '..', 'data', 'plans', f'{name}.json'))
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
json.dump(plan, open(out, 'w'), indent=1)
print(f'{name}: {W}x{H}, {len(trees)} trees (+{len(tips_below)} below the edge), {len(buildings)} buildings '
      f'{[(b["kind"], b["footprint"], b["door"]) for b in buildings]}, unclassified {list(left)}')
for row in plan['tiles']:
    print(''.join({'grass': '.', 'flowers': '*', 'sign': 'S', 'sand_patch': 's', 'tree_tip': ',', 'tree_top_l': 'T',
                   'tree_top_r': 't', 'tree_bot': 'b', 'building': 'B', 'building_roof': 'R', 'path': ':', 'tall_grass': 'g', 'ledge_s': 'v', 'ledge_cap': '#'}.get(c, '?') for c in row))
