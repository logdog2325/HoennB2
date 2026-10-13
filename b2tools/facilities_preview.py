"""The facilities interiors agent's preview helper (notes/INTERIORS_PLAN.md): b2tools/preview_interior.py pointed at the
agent's own room builds (work/agents/<agent>/interiors), so previews and the model cache never land in work/interiors.

    python3 facilities_preview.py NAME [NAME ...]            -> work/agents/facilities/interiors/NAME/preview.png
    python3 facilities_preview.py --models PACK:RES ...      -> contact sheet of Black 2 interior models (scratch)
    python3 facilities_preview.py --side NAME OUT.png        -> Sapphire's map (left) next to the room's preview
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import preview_interior as pv

AGENT = os.environ.get('HOENN_AGENT', 'facilities')
pv.OUT = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(pv.ROOT, 'work', 'agents', AGENT, 'interiors')

def model_sheet(specs, out, cell=160):
    """One cell per Black 2 interior model 'pack:res' (seen from the game's camera angle), name underneath."""
    import numpy as np
    from PIL import Image, ImageDraw
    import b2files
    from models_interior import FILES, bmd_box
    cols = 6
    rows = (len(specs) + cols - 1) // cols
    sheet = Image.new('RGB', (cell * cols, (cell + 14) * rows), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, spec in enumerate(specs):
        pack, res = map(int, spec.split(':'))
        r = next(x for x in b2files.building_pack(FILES, pack, exterior=False) if x['res_id'] == res)
        parts = pv.furniture_parts(res, pack)
        x0, x1, y0, y1, z0, z1 = bmd_box(r['bmd'])
        span = max(x1 - x0, y1 - y0, z1 - z0, 8)
        cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
        img = pv.render(parts, eye=(cx, cy + span * 1.3, cz + span * 1.6), target=(cx, cy, cz), fov=40,
                        W=cell, H=cell, bg=(70, 70, 70)) if parts else Image.new('RGB', (cell, cell))
        X, Y = cell * (i % cols), (cell + 14) * (i // cols)
        sheet.paste(img, (X, Y))
        d.text((X + 2, Y + cell), f"{r['name']} {pack}:{res} {x1-x0:.0f}x{z1-z0:.0f}x{y1-y0:.0f}", fill=(255, 255, 255))
    sheet.save(out)
    return out

def big_preview(name, W=1024, H=576):
    """The room from the game's side of the room (south, above), filling the image; furniture included."""
    import json
    d = os.path.join(pv.OUT, name)
    meta = json.load(open(os.path.join(d, 'room.json')))
    parts = pv.parse(os.path.join(d, 'terrain.dae'))
    by_name = {m['name']: m['res'] for m in meta['models']}
    packs = {m['res']: m['pack'] for m in meta['models']}
    for f in meta['furniture']:
        res = f['m'] if isinstance(f['m'], int) else by_name[f['m']]
        parts += pv.placed(pv.furniture_parts(res, packs[res]), f['pos'], f['rot'])
    ox, oz = meta['origin']; w, h = meta['size']
    cx = (ox + w / 2) * 16 - 256; cz = (oz + h / 2) * 16 - 256
    span = max(w * 16 / 1.6, h * 16)
    img = pv.render(parts, eye=(cx, span * 1.05, cz + span * 1.0), target=(cx, 0, cz + span * 0.06), fov=42, W=W, H=H)
    img.save(os.path.join(d, 'preview_big.png'))
    return img

def side_by_side(name, out):
    """Sapphire's map render (screenshots/sapphire/<map>.png, left half) next to the room's preview."""
    import json
    from PIL import Image
    meta = json.load(open(os.path.join(pv.OUT, name, 'room.json')))
    sap = Image.open(os.path.join(pv.ROOT, 'screenshots', 'sapphire', meta['map'] + '.png'))
    w, h = meta['size']
    sap = sap.crop((0, 0, w * 32, h * 32))
    pre = big_preview(name)
    k = pre.height / sap.height
    sap = sap.resize((max(1, int(sap.width * k)), pre.height))
    if sap.width > 900: sap = sap.resize((900, int(sap.height * 900 / sap.width)))
    im = Image.new('RGB', (sap.width + 8 + pre.width, pre.height), (20, 20, 20))
    im.paste(sap, (0, 0)); im.paste(pre, (sap.width + 8, 0))
    im.save(out)
    return out

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--models':
        print(model_sheet(a[2:], a[1]))
    elif a and a[0] == '--side':
        print(side_by_side(a[1], a[2]))
    else:
        for n in a: print(pv.preview(n))
