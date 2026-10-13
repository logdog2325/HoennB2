"""Convert Hoenn maps from pokeruby into a classified grid for a Gen 5-style 3D rebuild."""
import sys, json; sys.path.insert(0, '.')
from gba import *
from collections import deque

r = Repo(sys.argv[1] if len(sys.argv) > 1 else '../pokeruby')
CHAIN = ['OldaleTown', 'Route101', 'LittlerootTown']  # north -> south, all offset 0
PAD = 4
NICE = {'OldaleTown': 'Oldale Town', 'Route101': 'Route 101', 'LittlerootTown': 'Littleroot Town'}

from classify import classify

rows, objs, regions, warps, signs = [], [], [], [], []
yoff = PAD
W = None
for name in CHAIN:
    mj = r.map_json(name); g, l = r.layout_grid(mj['layout'])
    mr = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
    H, W = g.shape
    for y in range(H):
        rows.append(['X'] * PAD + [classify(mr, g[y, x]) for x in range(W)] + ['X'] * PAD)
    regions.append(dict(name=NICE[name], y0=yoff, y1=yoff + H))
    for o in mj.get('object_events', []):
        objs.append(dict(x=o['x'] + PAD, y=o['y'] + yoff, gfx=o['graphics_id'].replace('OBJ_EVENT_GFX_', ''),
                         wander=o['movement_type'] == 'MOVEMENT_TYPE_WANDER_AROUND'))
    for w in mj.get('warp_events', []):
        warps.append(dict(x=w['x'] + PAD, y=w['y'] + yoff, dest=w['dest_map'].replace('MAP_', '')))
    for s in mj.get('bg_events', []):
        if s.get('type') == 'sign':
            signs.append(dict(x=s['x'] + PAD, y=s['y'] + yoff))
    yoff += H
Wt = W + 2 * PAD
rows = [['X'] * Wt for _ in range(PAD)] + rows + [['X'] * Wt for _ in range(PAD)]
Ht = len(rows)

# The last map's southern edge and the first's northern edge would continue to Route 103 / beyond;
# leave a gap in the padding where the road continues so the scene doesn't look sealed.
for x in range(PAD, PAD + W):
    if rows[PAD][x] in 'PG':
        for y in range(PAD): rows[y][x] = rows[PAD][x]

# Split 'B' into buildings (connected, >= 6 tiles) and props.
seen = [[False] * Wt for _ in range(Ht)]
buildings = []
for y in range(Ht):
    for x in range(Wt):
        if rows[y][x] != 'B' or seen[y][x]: continue
        q, comp = deque([(x, y)]), []
        seen[y][x] = True
        while q:
            cx, cy = q.popleft(); comp.append((cx, cy))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < Wt and 0 <= ny < Ht and not seen[ny][nx] and rows[ny][nx] == 'B':
                    seen[ny][nx] = True; q.append((nx, ny))
        xs = [c[0] for c in comp]; ys = [c[1] for c in comp]
        if len(comp) >= 6:
            bx, by, bw, bh = min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
            door = next((w for w in warps if bx <= w['x'] < bx + bw and by <= w['y'] < by + bh), None)
            dest = door['dest'] if door else ''
            kind = ('center' if 'POKEMON_CENTER' in dest else 'mart' if 'MART' in dest else
                    'lab' if 'LAB' in dest else 'house')
            buildings.append(dict(x=bx, y=by, w=bw, h=bh, kind=kind,
                                  door=[door['x'], door['y']] if door else None))
            for cx, cy in comp: rows[cy][cx] = 'H'
        else:
            for cx, cy in comp: rows[cy][cx] = 'O'

# Signs sit on prop tiles; mark them so the renderer draws a signpost instead of a crate.
for s in signs:
    if rows[s['y']][s['x']] in 'OH': rows[s['y']][s['x']] = 'N' if rows[s['y']][s['x']] == 'O' else 'H'

out = dict(w=Wt, h=Ht, rows=[''.join(rw) for rw in rows], buildings=buildings, objects=objs,
           regions=regions, signs=signs, source='pret/pokeruby (Sapphire map data)')
json.dump(out, open('hoenn_slice.json', 'w'), separators=(',', ':'))
print(Wt, Ht, len(buildings), [b['kind'] for b in buildings])
print('\n'.join(out['rows']))
