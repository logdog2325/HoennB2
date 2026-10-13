"""Preview a built interior room without the emulator: renders work/interiors/<NAME>/terrain.dae with its furniture
(Black 2's building models, converted with tools/apicula into work/interiors/_models/) from the game's camera angle and
from above. A tiny software rasteriser (perspective-correct textures, z-buffer, alpha test); for checking layouts by
eye, not exact.

    python3 preview_interior.py NAME [NAME ...]        -> work/interiors/NAME/preview.png
"""

import os, re, sys, math, json
import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET

NS = '{http://www.collada.org/2005/11/COLLADASchema}'

def parse(path):
    root = ET.parse(path).getroot()
    d = os.path.dirname(path)
    imgs = {i.get('id'): i.find(NS + 'init_from').text for i in root.iter(NS + 'image')}
    eff_img = {}
    for e in root.iter(NS + 'effect'):
        surf = e.find('.//' + NS + 'surface/' + NS + 'init_from')
        eff_img[e.get('id')] = imgs.get(surf.text) if surf is not None else None
    mat_img = {}
    for m in root.iter(NS + 'material'):
        ie = m.find(NS + 'instance_effect').get('url')[1:]
        mat_img[m.get('id')] = eff_img.get(ie)
    out = []
    for g in root.iter(NS + 'geometry'):
        mesh = g.find(NS + 'mesh')
        src = {}
        for s in mesh.findall(NS + 'source'):
            fa = s.find(NS + 'float_array')
            stride = int(s.find('.//' + NS + 'accessor').get('stride', '1'))
            src[s.get('id')] = np.array([float(v) for v in fa.text.split()]).reshape(-1, stride)
        vin = {}
        vtx = mesh.find(NS + 'vertices')
        for i in vtx.findall(NS + 'input'):
            vin[i.get('semantic')] = src[i.get('source')[1:]]
        for prim in list(mesh.findall(NS + 'triangles')) + list(mesh.findall(NS + 'polylist')):
            inputs = prim.findall(NS + 'input')
            nin = max(int(i.get('offset')) for i in inputs) + 1
            sem = {}
            for i in inputs:
                s = i.get('semantic'); o = int(i.get('offset'))
                if s == 'VERTEX':
                    for k, v in vin.items(): sem[k] = (v, o)
                else: sem[s] = (src[i.get('source')[1:]], o)
            p = np.array([int(v) for v in prim.find(NS + 'p').text.split()]).reshape(-1, nin)
            if prim.tag == NS + 'polylist':
                vc = [int(v) for v in prim.find(NS + 'vcount').text.split()]
            else:
                vc = [3] * (len(p) // 3)
            tris = []; k = 0
            for n in vc:
                poly = list(range(k, k + n)); k += n
                for j in range(1, n - 1): tris.append([poly[0], poly[j], poly[j + 1]])
            tris = np.array(tris)
            P = sem['POSITION'][0][p[tris, sem['POSITION'][1]]]
            UV = sem['TEXCOORD'][0][p[tris, sem['TEXCOORD'][1]]] if 'TEXCOORD' in sem else np.zeros(P.shape[:2] + (2,))
            C = sem['COLOR'][0][p[tris, sem['COLOR'][1]]][..., :3] if 'COLOR' in sem else np.ones(P.shape)
            im = mat_img.get(prim.get('material'))
            if im is None:
                # our dae.py: material symbol -> instance_material target
                pass
            out.append((os.path.join(d, im) if im else None, P, UV, C))
    return out

_tex = {}
def tex(path):
    if path not in _tex:
        _tex[path] = np.asarray(Image.open(path).convert('RGBA')).astype(np.float32) if path and os.path.exists(path) else None
    return _tex[path]

def look(eye, target):
    f = np.array(target, float) - eye; f /= np.linalg.norm(f)
    up = np.array([0, 1.0, 0])
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return np.stack([r, u, -f])

def render(parts, eye, target, fov=30, W=512, H=384, bg=(0, 0, 0)):
    R = look(np.array(eye, float), target)
    eye = np.array(eye, float)
    fy = (H / 2) / math.tan(math.radians(fov) / 2)
    img = np.zeros((H, W, 3), np.float32); img[:] = bg
    zb = np.full((H, W), np.inf)
    for tp, P, UV, C, *xf in parts:
        if xf: P = xf[0](P)
        T = tex(tp)
        cam = (P - eye) @ R.T                     # (N,3,3)
        z = -cam[..., 2]
        ok = (z > 1).all(axis=1)
        sx = W / 2 + fy * cam[..., 0] / np.maximum(z, 1e-3)
        sy = H / 2 - fy * cam[..., 1] / np.maximum(z, 1e-3)
        for t in np.nonzero(ok)[0]:
            x0, x1 = int(max(0, math.floor(sx[t].min()))), int(min(W - 1, math.ceil(sx[t].max())))
            y0, y1 = int(max(0, math.floor(sy[t].min()))), int(min(H - 1, math.ceil(sy[t].max())))
            if x1 < x0 or y1 < y0: continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            (ax, bx, cx), (ay, by, cy) = sx[t], sy[t]
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-9: continue
            w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
            w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
            if not m.any(): continue
            iz = 1 / z[t]
            q = w0 * iz[0] + w1 * iz[1] + w2 * iz[2]
            depth = 1 / q
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            m &= depth < sub
            if not m.any(): continue
            u = (w0 * UV[t, 0, 0] * iz[0] + w1 * UV[t, 1, 0] * iz[1] + w2 * UV[t, 2, 0] * iz[2]) / q
            v = (w0 * UV[t, 0, 1] * iz[0] + w1 * UV[t, 1, 1] * iz[1] + w2 * UV[t, 2, 1] * iz[2]) / q
            col = (w0[..., None] * C[t, 0] + w1[..., None] * C[t, 1] + w2[..., None] * C[t, 2])
            if T is not None:
                th, tw = T.shape[:2]
                tx = np.floor(u * tw).astype(int) % tw
                ty = np.floor((1 - v) * th).astype(int) % th
                s = T[ty, tx]
                m &= s[..., 3] > 100
                rgb = s[..., :3] * col
            else:
                rgb = 255 * col
            reg = img[y0:y1 + 1, x0:x1 + 1]
            reg[m] = rgb[m]
            sub[m] = depth[m]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
APICULA = os.path.join(ROOT, 'tools', 'apicula', 'bin', 'apicula')

def furniture_parts(res, pack):
    """Parsed DAE parts of interior model res (with its pack's textures), converted once by apicula."""
    import subprocess
    sys.path.insert(0, HERE)
    import b2files
    from models_interior import derived_by_res
    d = derived_by_res(res)                 # a resized Black 2 model (models_interior.py DERIVED_MODELS): the base, scaled
    if d: return [(tp, P * d[1], UV, C) for tp, P, UV, C in furniture_parts(d[0], pack)]
    from models_interior import FILES
    d = os.path.join(OUT, '_models', f'{pack}_{res}')
    if not os.path.isdir(d):
        os.makedirs(d)
        r = next(x for x in b2files.building_pack(FILES, pack, exterior=False) if x['res_id'] == res)
        open(os.path.join(d, 'm.nsbmd'), 'wb').write(r['bmd'])
        open(os.path.join(d, 't.nsbtx'), 'wb').write(b2files.building_textures(FILES, pack, exterior=False))
        subprocess.run([APICULA, 'convert', os.path.join(d, 'm.nsbmd'), os.path.join(d, 't.nsbtx'), '-o',
                        os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True)
    daes = [f for f in os.listdir(os.path.join(d, 'dae'))] if os.path.isdir(os.path.join(d, 'dae')) else []
    daes = [os.path.join(d, 'dae', f) for f in daes if f.endswith('.dae')]
    return parse(daes[0]) if daes else []

def placed(parts, pos, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return [(tp, P @ R.T + np.array(pos), UV, C) for tp, P, UV, C in parts]

def preview(name):
    d = os.path.join(OUT, name)
    meta = json.load(open(os.path.join(d, 'room.json')))
    parts = parse(os.path.join(d, 'terrain.dae'))
    packs = {m['res']: m['pack'] for m in meta['models']}
    names = {m['res']: m['name'] for m in meta['models']}
    by_name = {v: k for k, v in names.items()}
    for f in meta['furniture']:
        res = f['m'] if isinstance(f['m'], int) else by_name[f['m']]
        parts += placed(furniture_parts(res, packs[res]), f['pos'], f['rot'])
    allp = np.concatenate([p[1].reshape(-1, 3) for p in parts])
    ox, oz = meta['origin']; w, h = meta['size']
    cx = (ox + w / 2) * 16 - 256; cz = (oz + h / 2) * 16 - 256
    span = max(w, h) * 16
    a = render(parts, eye=(cx, span * 1.15, cz + span * 1.05), target=(cx, 0, cz + span * 0.08), fov=45)
    b = render(parts, eye=(cx, span * 2.6, cz + 0.01), target=(cx, 0, cz), fov=40)
    from PIL import Image
    im = Image.new('RGB', (1024, 384)); im.paste(a, (0, 0)); im.paste(b, (512, 0))
    im.save(os.path.join(d, 'preview.png'))
    return os.path.join(d, 'preview.png')

if __name__ == '__main__':
    import json
    for n in sys.argv[1:]: print(preview(n))
