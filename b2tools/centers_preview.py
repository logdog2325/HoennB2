"""Preview tools of the centers agent (Pokémon Centers, notes/INTERIORS.md): b2tools/preview_interior.py's renderer
pointed at the agent's own room builds (work/agents/centers/interiors) and model cache, so nothing is written to
work/interiors.

    python3 centers_preview.py room NAME [NAME ...]      -> work/agents/centers/interiors/NAME/preview.png
    python3 centers_preview.py sheet OUT.png m1,m2,...   -> contact sheet of Black 2 interior models
    python3 centers_preview.py b2 OUT.png [CHUNK PACK TEXSET]  -> Black 2's own Pokémon Center (chunk 827, pack 1,
                                                            texture set 283) with its furniture
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
AGENT = os.path.join(ROOT, 'work', 'agents', 'centers')
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw
import preview_interior as pv

pv.OUT = os.path.join(AGENT, 'interiors')          # rooms + the furniture model cache (_models) of this agent

def sheet(out, names):
    import models_interior as mi
    by_name, _ = mi.interior_models()
    tiles = []
    for n in names:
        res, pack, _bmd = by_name[n]
        parts = pv.furniture_parts(res, pack)
        allp = np.concatenate([p[1].reshape(-1, 3) for p in parts])
        c = (allp.min(0) + allp.max(0)) / 2; s = max(np.ptp(allp, 0).max(), 16)
        im = pv.render(parts, eye=(c[0], c[1] + s, c[2] + s * 1.6), target=tuple(c), fov=45, W=200, H=170, bg=(60, 60, 70))
        ImageDraw.Draw(im).text((3, 3), n, fill=(255, 255, 0))
        tiles.append(im)
    cols = 6
    img = Image.new('RGB', (200 * cols, 170 * ((len(tiles) + cols - 1) // cols)))
    for i, t in enumerate(tiles): img.paste(t, ((i % cols) * 200, (i // cols) * 170))
    img.save(out)

def b2(out, chunk=827, pack=1, texset=283):
    import subprocess, b2files
    from models_interior import FILES
    d = os.path.join(AGENT, f'b2chunk_{chunk}')
    if not os.path.isdir(os.path.join(d, 'dae')):
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 't.nsbmd'), 'wb').write(b2files.chunk(FILES, chunk)[1][0])
        open(os.path.join(d, 'tex.nsbtx'), 'wb').write(b2files.map_textures(FILES, texset))
        subprocess.run([pv.APICULA, 'convert', os.path.join(d, 't.nsbmd'), os.path.join(d, 'tex.nsbtx'), '-o',
                        os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True, check=True)
    dae = next(f for f in os.listdir(os.path.join(d, 'dae')) if f.endswith('.dae'))
    parts = pv.parse(os.path.join(d, 'dae', dae))
    for b in b2files.chunk_buildings(FILES, chunk):
        parts += pv.placed(pv.furniture_parts(b['res_id'], pack), (b['x'], b['y'], b['z']), b['rot'])
    cx, cz, span = 7 * 16 - 248, 10 * 16 - 256, 320
    a = pv.render(parts, eye=(cx, span * 0.9, cz + span * 0.85), target=(cx, 0, cz + 20), fov=45, W=768, H=576)
    b = pv.render(parts, eye=(cx, span * 2.0, cz + 0.01), target=(cx, 0, cz), fov=40, W=768, H=576)
    img = Image.new('RGB', (1536, 576)); img.paste(a, (0, 0)); img.paste(b, (768, 0)); img.save(out)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'room':
        for n in sys.argv[2:]: print(pv.preview(n))
    elif cmd == 'sheet': sheet(sys.argv[2], sys.argv[3].split(','))
    elif cmd == 'b2': b2(sys.argv[2], *map(int, sys.argv[3:]))
