"""gyms_league agent helper: render Black 2's own zones (all chunks of the zone's matrix, the area's map textures and
the chunk's building placements) with preview_interior's software renderer, to study how Black 2 builds gyms and
League rooms. Output in work/agents/gyms_league/b2view/.

    python3 gyms_league_view.py zone ZONE [--top]
    python3 gyms_league_view.py textures TEXSET        (dump a map texture set's PNGs)
"""
import os, sys, json, struct, subprocess, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b2files, zoneheaders, nsbtx
import preview_interior as pv
from models_interior import FILES

ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ROOT, 'work', 'agents', 'gyms_league', 'b2view')

def chunk_parts(chunk_id, texset):
    d = os.path.join(OUT, '_chunks', f'{chunk_id}_{texset}')
    if not os.path.isdir(os.path.join(d, 'dae')):
        os.makedirs(d, exist_ok=True)
        magic, secs = b2files.chunk(FILES, chunk_id)
        open(os.path.join(d, 'm.nsbmd'), 'wb').write(secs[0])
        open(os.path.join(d, 't.nsbtx'), 'wb').write(b2files.map_textures(FILES, texset))
        subprocess.run([pv.APICULA, 'convert', os.path.join(d, 'm.nsbmd'), os.path.join(d, 't.nsbtx'), '-o',
                        os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True)
    daes = [os.path.join(d, 'dae', f) for f in os.listdir(os.path.join(d, 'dae')) if f.endswith('.dae')]
    return pv.parse(daes[0]) if daes else []

def zone_parts(zone):
    hd, _ = zoneheaders.load(FILES)
    h = hd[zone]
    mat = b2files.narc_entries(b2files.arc_path(FILES, 9))[h['matrix']]
    fmt, _, w, hh = struct.unpack_from('<HHHH', mat, 0)
    ids = struct.unpack_from(f'<{w*hh}I', mat, 8)
    a = b2files.area(FILES, h['area'])
    parts = []
    pv.OUT = os.path.join(OUT)          # furniture model cache
    for k, cid in enumerate(ids):
        if cid == 0xFFFFFFFF: continue
        cx, cz = (k % w) * 512 + 256, (k // w) * 512 + 256
        for tp, P, UV, C in chunk_parts(cid, a['texset']):
            parts.append((tp, P + np.array([cx, 0, cz]), UV, C))
        if not a['exterior']:
            for b in b2files.chunk_buildings(FILES, cid):
                try:
                    fp = pv.furniture_parts(b['res_id'], a['pack'])
                except StopIteration:
                    continue
                parts += pv.placed(fp, (b['x'] + cx, b['y'], b['z'] + cz), b['rot'])
    return parts, (w, hh), h, a, ids

def view(zone, eye=None, target=None, size=(768, 576), fov=40, tag=''):
    parts, (w, hh), h, a, ids = zone_parts(zone)
    allp = np.concatenate([p[1].reshape(-1, 3) for p in parts])
    x0, x1 = np.percentile(allp[:, 0], [1, 99]); z0, z1 = np.percentile(allp[:, 2], [1, 99])
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    span = max(x1 - x0, z1 - z0)
    top = pv.render(parts, eye=(cx, span * 2.2, cz + 0.01), target=(cx, 0, cz), fov=fov, W=size[0], H=size[1])
    cam = pv.render(parts, eye=eye or (cx, span * 0.9, z1 + span * 0.6), target=target or (cx, 0, cz + span * 0.1),
                    fov=45, W=size[0], H=size[1])
    from PIL import Image
    im = Image.new('RGB', (size[0] * 2, size[1])); im.paste(cam, (0, 0)); im.paste(top, (size[0], 0))
    p = os.path.join(OUT, f'zone{zone}{tag}.png'); im.save(p)
    print(p, 'area', h['area'], a, 'matrix', h['matrix'], (w, hh), ids, 'bbox', (x0, x1, z0, z1))
    return p

def textures(ts):
    d = os.path.join(OUT, f'tex{ts}'); os.makedirs(d, exist_ok=True)
    for n, img, _ in nsbtx.decode(b2files.map_textures(FILES, ts)):
        img.save(os.path.join(d, n + '.png'))
    print(d)

if __name__ == '__main__':
    if sys.argv[1] == 'zone':
        for z in sys.argv[2:]: view(int(z))
    elif sys.argv[1] == 'textures':
        for t in sys.argv[2:]: textures(int(t))

def sheet(ts, cols=10, cell=96):
    """Contact sheet of a map texture set: every texture scaled into a cell, its name and size below."""
    from PIL import Image, ImageDraw
    texs = [(n, img) for n, img, _ in nsbtx.decode(b2files.map_textures(FILES, ts))]
    rows = (len(texs) + cols - 1) // cols
    im = Image.new('RGB', (cols * cell, rows * (cell + 24)), (60, 0, 60))
    d = ImageDraw.Draw(im)
    for k, (n, img) in enumerate(texs):
        x, y = (k % cols) * cell, (k // cols) * (cell + 24)
        t = img.convert('RGBA'); s = min(cell / t.width, cell / t.height)
        t = t.resize((max(1, int(t.width * s)), max(1, int(t.height * s))), Image.NEAREST)
        im.paste(t, (x, y), t)
        d.text((x + 2, y + cell), n[:15], fill=(255, 255, 255))
        d.text((x + 2, y + cell + 11), f'{img.width}x{img.height}', fill=(200, 200, 0))
    p = os.path.join(OUT, f'sheet{ts}.png'); im.save(p); print(p)

if __name__ == '__main__' and sys.argv[1] == 'sheet':
    for t in sys.argv[2:]: sheet(int(t))

def models_sheet(names=None, cell=160, cols=8, tag='all'):
    """Every interior building model (first pack holding it, with that pack's textures), rendered from the game's
    camera angle, with its name, res id, pack and footprint in tiles."""
    from PIL import Image, ImageDraw
    from models_interior import interior_models, bmd_box
    pv.OUT = OUT
    by_name, _ = interior_models()
    names = names or sorted(by_name, key=lambda n: by_name[n][0])
    tiles = []
    for n in names:
        res, pack, bmd = by_name[n]
        try: parts = pv.furniture_parts(res, pack)
        except Exception as e: parts = []
        b = bmd_box(bmd)
        if parts:
            allp = np.concatenate([p[1].reshape(-1, 3) for p in parts])
            lo, hi = allp.min(0), allp.max(0); c = (lo + hi) / 2; s = max(hi - lo) + 1
            img = pv.render(parts, eye=(c[0], c[1] + s * 0.9, c[2] + s * 1.1), target=tuple(c), fov=50, W=cell, H=cell)
        else:
            img = Image.new('RGB', (cell, cell))
        tiles.append((n, res, pack, b, img))
    rows = (len(tiles) + cols - 1) // cols
    im = Image.new('RGB', (cols * cell, rows * (cell + 26)), (40, 40, 60)); d = ImageDraw.Draw(im)
    for k, (n, res, pack, b, img) in enumerate(tiles):
        x, y = (k % cols) * cell, (k // cols) * (cell + 26)
        im.paste(img, (x, y))
        d.text((x + 2, y + cell), f'{n[:18]} r{res} p{pack}', fill=(255, 255, 255))
        d.text((x + 2, y + cell + 12), f'{(b[1]-b[0])/16:.1f}x{(b[5]-b[4])/16:.1f}t h{b[3]-b[2]:.0f}', fill=(200, 200, 0))
    p = os.path.join(OUT, f'models_{tag}.png'); im.save(p); print(p)

if __name__ == '__main__' and sys.argv[1] == 'models':
    models_sheet(sys.argv[2:] or None)

def room_preview(name, root=os.path.join(ROOT, 'work', 'agents', 'gyms_league', 'interiors'), sap=True):
    """preview_interior's two views of one of our rooms (terrain_all.dae for big rooms), next to Sapphire's render
    (screenshots/sapphire/<map>.png, left half) when it exists. -> <room dir>/preview.png"""
    from PIL import Image
    d = os.path.join(root, name)
    meta = json.load(open(os.path.join(d, 'room.json')))
    dae = os.path.join(d, 'terrain_all.dae') if os.path.exists(os.path.join(d, 'terrain_all.dae')) else os.path.join(d, 'terrain.dae')
    parts = pv.parse(dae)
    pv.OUT = root
    by_name = {m['name']: m for m in meta['models']}
    for f in meta['furniture']:
        mm = by_name[f['m']] if isinstance(f['m'], str) else next(m for m in meta['models'] if m['res'] == f['m'])
        parts += pv.placed(pv.furniture_parts(mm['res'], mm['pack']), f['pos'], f['rot'])
    ox, oz = meta['origin']; w, h = meta['size']
    cx = (ox + w / 2) * 16 - 256; cz = (oz + h / 2) * 16 - 256
    span = max(w, h) * 16
    H = 384 if h <= 2 * w else 640
    a = pv.render(parts, eye=(cx, span * 1.15, cz + span * 1.05), target=(cx, 0, cz + span * 0.08), fov=45, H=H)
    b = pv.render(parts, eye=(cx, span * 2.6, cz + 0.01), target=(cx, 0, cz), fov=40, H=H)
    ims = [a, b]
    sp = os.path.join(ROOT, 'screenshots', 'sapphire', meta['map'] + '.png')
    if sap and os.path.exists(sp):
        s = Image.open(sp); s = s.crop((0, 0, s.width // 2 - 16, s.height))
        k = min(H / s.height, 512 / s.width); s = s.resize((max(1, int(s.width * k)), max(1, int(s.height * k))))
        ims.insert(0, s)
    out = Image.new('RGB', (sum(i.width for i in ims) + 8 * (len(ims) - 1), H))
    x = 0
    for i in ims: out.paste(i, (x, 0)); x += i.width + 8
    p = os.path.join(d, 'preview.png'); out.save(p); print(p)
    return p

if __name__ == '__main__' and sys.argv[1] == 'room':
    for n in sys.argv[2:]: room_preview(n)

def pick(items, tag='pick', cell=128):
    """Zoomed sheet of chosen textures: items 'texset:name'."""
    from PIL import Image, ImageDraw
    cols = 8; rows = (len(items) + cols - 1) // cols
    im = Image.new('RGB', (cols * cell, rows * (cell + 14)), (60, 0, 60)); d = ImageDraw.Draw(im)
    cache = {}
    for k, it in enumerate(items):
        ts, n = it.split(':'); ts = int(ts)
        if ts not in cache: cache[ts] = {nn: img for nn, img, _ in nsbtx.decode(b2files.map_textures(FILES, ts))}
        img = cache[ts][n].convert('RGBA')
        # tile 2x2 to show repetition
        t = Image.new('RGBA', (img.width * 2, img.height * 2))
        for a in range(2):
            for b in range(2): t.paste(img, (a * img.width, b * img.height))
        s = min(cell / t.width, cell / t.height); t = t.resize((int(t.width * s), int(t.height * s)), Image.NEAREST)
        x, y = (k % cols) * cell, (k // cols) * (cell + 14)
        im.paste(t, (x, y), t); d.text((x + 2, y + cell), f'{ts}:{n}'[:20], fill=(255, 255, 255))
    p = os.path.join(OUT, f'{tag}.png'); im.save(p); print(p)

if __name__ == '__main__' and sys.argv[1] == 'pick':
    pick(sys.argv[3:], sys.argv[2])
