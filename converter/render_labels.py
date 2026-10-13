"""Render a Sapphire map with the class of every metatile written on it, from metatiles.json plus extra label files
(data/labels/*.json, {"tileset": {"id": "class"}}). For checking labels by eye.

    python3 render_labels.py ../external/pokeruby Route104 OUT.png [label files...]
"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw
from gba import Repo, MetatileRenderer

root, name, out = sys.argv[1], sys.argv[2], sys.argv[3]
here = os.path.dirname(os.path.abspath(__file__))
table = json.load(open(os.path.join(here, 'metatiles.json')))
for f in sys.argv[4:]:
    for ts, ids in json.load(open(f)).items():
        if ts.startswith('_'): continue
        table.setdefault(ts, {}).update(ids)
r = Repo(root)
mj = r.map_json(name); g, l = r.layout_grid(mj['layout'])
mr = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
H, W = g.shape
S = 2
img = Image.new('RGB', (W * 16 * S, H * 16 * S)); d = ImageDraw.Draw(img)
classes = {}
for y in range(H):
    for x in range(W):
        mt = int(g[y, x]) & 0x3FF
        ts = l['primary_tileset'] if mt < 512 else l['secondary_tileset']
        c = table.get(ts, {}).get(f'{mt:03x}', '?')
        img.paste(Image.fromarray(mr.render(mt)[..., :3]).resize((16 * S, 16 * S), Image.NEAREST), (x * 16 * S, y * 16 * S))
        key = c[:3]
        d.rectangle([x * 16 * S, y * 16 * S, x * 16 * S + 21, y * 16 * S + 9], fill=(0, 0, 0))
        d.text((x * 16 * S + 1, y * 16 * S - 1), key, fill=(255, 255, 0) if c != '?' else (255, 60, 60))
        classes[c] = classes.get(c, 0) + 1
img.save(out)
print(name, W, 'x', H, 'classes:', dict(sorted(classes.items(), key=lambda kv: -kv[1])))
