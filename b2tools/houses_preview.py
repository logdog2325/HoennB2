"""houses agent helper: b2tools/preview_interior.py on the agent's own room copy (work/agents/houses/interiors, or
$HOENN_INTERIORS_DIR), so the shared work/interiors is never written. Also a furniture gallery and a side-by-side
proof image (Sapphire's map | our room).

    python3 houses_preview.py NAME [NAME ...]           -> <rooms>/NAME/preview.png
    python3 houses_preview.py --side OUT.png NAME ...    Sapphire render left, preview right, one row per room
    python3 houses_preview.py --gallery OUT.png MODEL ...  Black 2 interior models (name or res id), front + top view
"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'converter'))
import preview_interior as pv

pv.OUT = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'agents', 'houses', 'interiors')

def sapphire(name, sc=2):
    from gba import Repo, MetatileRenderer
    r = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    mj = r.map_json(name); g, l = r.layout_grid(mj['layout'])
    mr = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
    H, W = g.shape
    im = Image.new('RGB', (W * 16, H * 16))
    for y in range(H):
        for x in range(W):
            im.paste(Image.fromarray(mr.render(int(g[y, x]) & 0x3FF)[..., :3]), (x * 16, y * 16))
    d = ImageDraw.Draw(im)
    for e in mj.get('object_events', []):
        d.rectangle([e['x'] * 16 + 3, e['y'] * 16 + 3, e['x'] * 16 + 12, e['y'] * 16 + 12], outline=(255, 40, 40))
    return im.resize((W * 16 * sc, H * 16 * sc), Image.NEAREST)

def side(out, names, sc=2):
    rows = []
    for n in names:
        p = pv.preview(n)
        a, b = sapphire(n, sc), Image.open(p)
        if sc < 2: b = b.resize((b.width * 3 // 4, b.height * 3 // 4))
        h = max(a.height, b.height)
        row = Image.new('RGB', (a.width + 8 + b.width, h + 14), (30, 30, 30))
        row.paste(a, (0, 14)); row.paste(b, (a.width + 8, 14))
        ImageDraw.Draw(row).text((2, 1), n, fill=(255, 255, 255))
        rows.append(row)
    W = max(r.width for r in rows); H = sum(r.height for r in rows)
    im = Image.new('RGB', (W, H), (30, 30, 30)); y = 0
    for r in rows: im.paste(r, (0, y)); y += r.height
    im.save(out); print(out, im.size)

def gallery(out, models):
    from models_interior import interior_models
    by_name, by_res = interior_models()
    tiles = []
    for m in models:
        if m.isdigit(): res = int(m); name, pack, _ = by_res[res]
        else: name = m; res, pack, _ = by_name[name]
        parts = pv.furniture_parts(res, pack)
        if not parts: continue
        P = np.concatenate([p[1].reshape(-1, 3) for p in parts])
        c = (P.min(0) + P.max(0)) / 2; span = max(P.max(0) - P.min(0)) + 8
        a = pv.render(parts, eye=(c[0], c[1] + span * 0.9, c[2] + span * 1.6), target=tuple(c), fov=40, W=200, H=200, bg=(70, 70, 90))
        b = pv.render(parts, eye=(c[0], c[1] + span * 2.5, c[2] + 0.01), target=tuple(c), fov=40, W=200, H=200, bg=(70, 70, 90))
        t = Image.new('RGB', (400, 216), (30, 30, 30)); t.paste(a, (0, 16)); t.paste(b, (200, 16))
        x0, y0, z0 = P.min(0); x1, y1, z1 = P.max(0)
        ImageDraw.Draw(t).text((2, 2), f'{res} {name} p{pack}  {x1 - x0:.0f}x{y1 - y0:.0f}x{z1 - z0:.0f} (x,y,z)  front=+z', fill=(255, 255, 0))
        tiles.append(t)
    cols = 3; rows = (len(tiles) + cols - 1) // cols
    im = Image.new('RGB', (cols * 400, rows * 216), (30, 30, 30))
    for i, t in enumerate(tiles): im.paste(t, ((i % cols) * 400, (i // cols) * 216))
    im.save(out); print(out, im.size)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--gallery': gallery(a[1], a[2:])
    elif a and a[0] == '--side': side(a[1], a[2:])
    elif a and a[0] == '--side1': side(a[1], a[2:], 1)
    else:
        for n in a: print(pv.preview(n))
