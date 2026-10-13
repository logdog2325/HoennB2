"""Render contact sheets of a tileset's metatiles that Sapphire's outdoor maps use, for labelling.

    python3 metatile_sheet.py ../external/pokeruby gTileset_Mauville OUT_DIR [--all]

Each cell: the metatile at 4x, its id, behaviour byte, collision values seen in maps, use count and one example
map/position. Only metatiles not yet in metatiles.json are drawn unless --all. Pages of 48 (OUT_DIR/<tileset>_NN.png),
plus OUT_DIR/<tileset>.json listing the same facts for every id on the pages.
"""
import sys, os, json, collections
import numpy as np
from PIL import Image, ImageDraw
from gba import Repo, MetatileRenderer

root, tileset, out = sys.argv[1], sys.argv[2], sys.argv[3]
show_all = '--all' in sys.argv
here = os.path.dirname(os.path.abspath(__file__))
r = Repo(root)
table = json.load(open(os.path.join(here, 'metatiles.json')))
maps = json.load(open(os.path.join(here, '..', 'data', 'hoenn_maps.json')))
outdoor = [m for m in maps if m['type'] in ('MAP_TYPE_TOWN', 'MAP_TYPE_CITY', 'MAP_TYPE_ROUTE', 'MAP_TYPE_6')]
facts = collections.defaultdict(lambda: dict(uses=0, collision=set(), elevation=set(), example=None, pair=None))
for m in outdoor:
    if tileset not in (m['primary'], m['secondary']): continue
    mj = r.map_json(m['name']); g, l = r.layout_grid(mj['layout'])
    for y in range(g.shape[0]):
        for x in range(g.shape[1]):
            v = int(g[y, x]); mt = v & 0x3FF
            ts = l['primary_tileset'] if mt < 512 else l['secondary_tileset']
            if ts != tileset: continue
            f = facts[mt]; f['uses'] += 1; f['collision'].add((v >> 10) & 3); f['elevation'].add((v >> 12) & 0xF)
            if f['example'] is None: f['example'] = f"{m['name']} ({x},{y})"; f['pair'] = (l['primary_tileset'], l['secondary_tileset'])
ids = sorted(k for k in facts if show_all or f'{k:03x}' not in table.get(tileset, {}))
os.makedirs(out, exist_ok=True)
renderers = {}
info = {}
for page in range(0, len(ids), 48):
    chunk = ids[page:page + 48]
    sheet = Image.new('RGB', (8 * 150, 6 * 120), (40, 40, 40)); d = ImageDraw.Draw(sheet)
    for i, mt in enumerate(chunk):
        f = facts[mt]
        if f['pair'] not in renderers: renderers[f['pair']] = MetatileRenderer(r, *f['pair'])
        mr = renderers[f['pair']]
        im = Image.fromarray(mr.render(mt)[..., :3]).resize((64, 64), Image.NEAREST)
        x0, y0 = (i % 8) * 150, (i // 8) * 120
        sheet.paste(im, (x0 + 4, y0 + 4))
        b = mr.behavior(mt)
        d.text((x0 + 72, y0 + 4), f'{mt:03x}', fill=(255, 255, 0))
        d.text((x0 + 72, y0 + 18), f'beh {b:02x}', fill=(255, 255, 255))
        d.text((x0 + 72, y0 + 32), f'col {sorted(f["collision"])}', fill=(255, 255, 255))
        d.text((x0 + 72, y0 + 46), f'n={f["uses"]}', fill=(200, 200, 200))
        d.text((x0 + 4, y0 + 72), f['example'][:26], fill=(170, 170, 170))
        info[f'{mt:03x}'] = dict(behavior=f'{b:02x}', collision=sorted(f['collision']), elevation=sorted(f['elevation']),
                                 uses=f['uses'], example=f['example'])
    sheet.save(os.path.join(out, f'{tileset}_{page // 48:02d}.png'))
json.dump(info, open(os.path.join(out, f'{tileset}.json'), 'w'), indent=1)
print(f'{tileset}: {len(ids)} metatiles on {(len(ids) + 47) // 48} pages -> {out}')
