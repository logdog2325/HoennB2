"""Shops agent helper: b2tools/preview_interior.py writing only into work/agents/<agent>/interiors (never the shared
work/interiors), plus a gallery of single Black 2 interior models and a side-by-side Sapphire | ours sheet.

    python3 shops_preview.py room NAME [NAME ...]      -> work/agents/shops/interiors/NAME/preview.png
    python3 shops_preview.py models OUT.png name ...   -> one tile per Black 2 interior model (game camera + top)
    python3 shops_preview.py compare OUT.png NAME      -> Sapphire's map (left) next to our preview (right)
"""
import os, sys, math, json
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
AGENT = os.environ.get('HOENN_AGENT', 'shops')
OUT = os.path.join(ROOT, 'work', 'agents', AGENT, 'interiors')
import preview_interior as pi                                # noqa: E402
pi.OUT = OUT                                                 # preview + model cache in the agent's own copy


def model_tile(name, size=256):
    import models_interior as mi
    by_name, _ = mi.interior_models()
    res, pack, bmd = by_name[name]
    parts = pi.furniture_parts(res, pack)
    if not parts: return Image.new('RGB', (size * 2, size))
    P = np.concatenate([p[1].reshape(-1, 3) for p in parts])
    lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2
    span = max(hi - lo) + 8
    a = pi.render(parts, eye=(c[0], c[1] + span * 1.1, c[2] + span * 1.6), target=tuple(c), fov=40, W=size, H=size,
                  bg=(40, 40, 60))
    b = pi.render(parts, eye=(c[0], c[1] + span * 2.5, c[2] + 0.01), target=tuple(c), fov=40, W=size, H=size,
                  bg=(40, 40, 60))
    im = Image.new('RGB', (size * 2, size + 14)); im.paste(a, (0, 14)); im.paste(b, (size, 14))
    x0, x1, y0, y1, z0, z1 = mi.bmd_box(bmd)
    ImageDraw.Draw(im).text((2, 1), f'{name} res {res} pack {pack}  {x1 - x0:.0f}w x {y1 - y0:.0f}h x {z1 - z0:.0f}d',
                            fill=(255, 255, 0))
    return im


def models(out, names, cols=3):
    tiles = [model_tile(n) for n in names]
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (w * cols, h * rows))
    for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * w, (i // cols) * h))
    sheet.save(out)
    return out


def sapphire(name, scale=2):
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from gba import Repo, MetatileRenderer
    r = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    mj = r.map_json(name); g, l = r.layout_grid(mj['layout'])
    mr = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
    H, W = g.shape
    im = np.zeros((H * 16, W * 16, 3), np.uint8)
    for y in range(H):
        for x in range(W): im[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = mr.render(int(g[y, x]) & 0x3FF)[..., :3]
    img = Image.fromarray(im).resize((W * 16 * scale, H * 16 * scale), Image.NEAREST)
    d = ImageDraw.Draw(img)
    for o in mj.get('object_events', []):
        d.rectangle([o['x'] * 16 * scale + 4, o['y'] * 16 * scale + 4, (o['x'] + 1) * 16 * scale - 4,
                     (o['y'] + 1) * 16 * scale - 4], outline=(255, 0, 0), width=2)
    return img


def compare(out, name):
    p = pi.preview(name)
    a, b = sapphire(name), Image.open(p)
    h = max(a.height, b.height)
    im = Image.new('RGB', (a.width + b.width + 8, h), (30, 30, 30))
    im.paste(a, (0, 0)); im.paste(b, (a.width + 8, 0))
    im.save(out)
    return out


def b2_chunk(out, chunk_id, area, view=None):
    """Render one of Black 2's own map chunks (terrain + its building placements) with the area's textures, to see how
    Black 2 builds a room. view = [x0, z0, x1, z1] tiles to frame (default: the whole chunk)."""
    import subprocess, struct
    import b2files, models_interior as mi
    FILES = mi.FILES
    a = b2files.area(FILES, area)
    d = os.path.join(OUT, '_b2chunks', f'{chunk_id}_{area}')
    if not os.path.isdir(os.path.join(d, 'dae')):
        os.makedirs(d, exist_ok=True)
        _, secs = b2files.chunk(FILES, chunk_id)
        open(os.path.join(d, 'm.nsbmd'), 'wb').write(secs[0])
        open(os.path.join(d, 't.nsbtx'), 'wb').write(b2files.map_textures(FILES, a['texset']))
        subprocess.run([pi.APICULA, 'convert', os.path.join(d, 'm.nsbmd'), os.path.join(d, 't.nsbtx'), '-o',
                        os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True)
    daes = [os.path.join(d, 'dae', f) for f in os.listdir(os.path.join(d, 'dae')) if f.endswith('.dae')]
    parts = pi.parse(daes[0])
    packs = {r['res_id'] for r in b2files.building_pack(FILES, a['pack'], exterior=False)}
    _, by_res = mi.interior_models()
    for b in b2files.chunk_buildings(FILES, chunk_id):
        res = b['res_id']
        pack = a['pack'] if res in packs else by_res[res][1]
        parts += pi.placed(pi.furniture_parts(res, pack), (b['x'], b['y'], b['z']), b['rot'])
    x0, z0, x1, z1 = view or [0, 0, 32, 32]
    cx, cz = (x0 + x1) / 2 * 16 - 256, (z0 + z1) / 2 * 16 - 256
    span = max(x1 - x0, z1 - z0) * 16
    A = pi.render(parts, eye=(cx, span * 1.15, cz + span * 1.05), target=(cx, 0, cz + span * 0.08), fov=45)
    B = pi.render(parts, eye=(cx, span * 2.6, cz + 0.01), target=(cx, 0, cz), fov=40)
    im = Image.new('RGB', (1024, 384)); im.paste(A, (0, 0)); im.paste(B, (512, 0))
    im.save(out)
    return out



def texset_sheet(out, texset, only=None, scale=2):
    """All textures of a Black 2 map texture set (a/0/1/4 entry) in one labelled sheet."""
    import b2files, nsbtx, models_interior as mi
    texs = [(n, img) for n, img, _ in nsbtx.decode(b2files.map_textures(mi.FILES, texset)) if not only or any(o in n for o in only)]
    cols, cell = 8, 64 * scale
    rows = (len(texs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell, rows * (cell + 12)), (40, 40, 60))
    d = ImageDraw.Draw(sheet)
    for i, (n, img) in enumerate(texs):
        x, y = (i % cols) * cell, (i // cols) * (cell + 12)
        im = img.convert('RGBA'); w, h = im.size
        f = min(cell / w, cell / h, scale * 2)
        im = im.resize((max(1, int(w * f)), max(1, int(h * f))), Image.NEAREST)
        sheet.paste(im, (x, y + 12), im)
        d.text((x + 1, y), f'{n} {w}x{h}', fill=(255, 255, 0))
    sheet.save(out)
    return out


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'room':
        for n in args: print(pi.preview(n))
    elif cmd == 'texset': print(texset_sheet(args[0], int(args[1]), args[2:]))
    elif cmd == 'chunk': print(b2_chunk(args[0], int(args[1]), int(args[2]), [float(v) for v in args[3:7]] or None))
    elif cmd == 'models': print(models(args[0], args[1:]))
    elif cmd == 'compare': print(compare(args[0], args[1]))

