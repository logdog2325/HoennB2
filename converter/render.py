"""Render pokeruby maps as images, next to the converter's classification, to check it by eye.

Usage: python3 render.py ../external/pokeruby LittlerootTown Route101 OldaleTown
Writes ../screenshots/sapphire/<Map>.png: left = the real Sapphire map, right = the same map tinted by
export.py's class letters, with warps (W), signs (S) and NPCs (N) marked on both.
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
from gba import Repo, MetatileRenderer
from classify import classify

COLORS = {  # class letter -> tint
    'G': (90, 200, 90), 'P': (230, 210, 150), 'T': (20, 120, 40), 'L': (200, 120, 40), 'W': (60, 120, 230),
    'S': (240, 230, 120), 'X': (10, 70, 20), 'B': (200, 60, 200), 'F': (240, 80, 120),
}

def render_map(r, name, out_dir):
    mj = r.map_json(name)
    g, l = r.layout_grid(mj['layout'])
    mr = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
    H, W = g.shape
    real = np.zeros((H * 16, W * 16, 3), np.uint8)
    cls = np.zeros_like(real)
    letters = []
    for y in range(H):
        row = ''
        for x in range(W):
            px = mr.render(int(g[y, x]) & 0x3FF)[..., :3]
            real[y*16:y*16+16, x*16:x*16+16] = px
            c = classify(mr, g[y, x])
            row += c
            tint = np.array(COLORS.get(c, (255, 255, 255)), np.float32)
            cls[y*16:y*16+16, x*16:x*16+16] = (px * 0.35 + tint * 0.65).astype(np.uint8)
        letters.append(row)
    imgs = [Image.fromarray(real), Image.fromarray(cls)]
    for im in imgs:
        d = ImageDraw.Draw(im)
        for x in range(W + 1): d.line([(x*16, 0), (x*16, H*16)], fill=(0, 0, 0), width=1) if im is imgs[1] else None
        for kind, evs, col in (('W', mj.get('warp_events', []), (255, 255, 255)),
                               ('S', [b for b in mj.get('bg_events', []) if b.get('type') == 'sign'], (255, 255, 0)),
                               ('N', mj.get('object_events', []), (255, 60, 60))):
            for e in evs:
                x, y = e['x'] * 16, e['y'] * 16
                d.rectangle([x, y, x + 15, y + 15], outline=col, width=2)
                d.text((x + 4, y + 2), kind, fill=col)
    for y, row in enumerate(letters):
        d = ImageDraw.Draw(imgs[1])
        for x, c in enumerate(row):
            d.text((x * 16 + 5, y * 16 + 3), c, fill=(0, 0, 0))
    scale = 2
    out = Image.new('RGB', (W * 16 * 2 + 16, H * 16), (40, 40, 40))
    out.paste(imgs[0], (0, 0)); out.paste(imgs[1], (W * 16 + 16, 0))
    out = out.resize((out.width * scale, out.height * scale), Image.NEAREST)
    os.makedirs(out_dir, exist_ok=True)
    path = f'{out_dir}/{name}.png'
    out.save(path)
    return path, W, H, letters

if __name__ == '__main__':
    r = Repo(sys.argv[1])
    for name in sys.argv[2:]:
        path, W, H, _ = render_map(r, name, os.path.join(os.path.dirname(__file__), '..', 'screenshots', 'sapphire'))
        print(f'{name}: {W}x{H} -> {path}')
