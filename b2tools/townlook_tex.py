"""Town look pass textures (town_look 2026-11-09): work/tex/townlook.nsbtx and its images in work/tex/townlook/.

    python3 townlook_tex.py            (the town model scripts that use them call build() first; idempotent)

Building textures go into pack 0's texture set by name (patches/area2_buildings.py: data/buildings/<group>.json
"textures": ["townlook", <name>, <name>_pl]), and a merge keeps the first texture of a name, so:
- RENAMED: Black 2 textures under our own names (pack 0's own set, Accumula's, has a 'kabe_001' and a 'kabe_002' of
  its own: other images). Copied byte for byte.
- CROPS: one tileable piece of a Black 2 atlas as a texture of its own, so a roof face can be ONE polygon with the
  hardware repeating it (WRAP) at Black 2's texel size, instead of an atlas region cut into a cell per repeat (pack 0
  is read whole into the field heap: ~28 B a triangle). Re-encoded as a 16-colour texture (nsbtx.image_source); the
  source images have no more than 16 colours, so no pixel changes.
"""
import os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TEX = os.path.join(HERE, '..', 'work', 'tex')

RENAMED = {'rus_stone': ('ext05', 'kabe_002'),        # Route 4's stone building: arched windows over ashlar (Rustboro)
           'rus_greywin': ('ext05', 'kabe_001')}      # Route 4's grey storey of dark windows (Rustboro)
CROPS = {   # name -> (set, texture, (x0, y0, x1, y1)): power-of-two pieces that tile both ways
    'tl_redtile': ('ext53', 't06_h_01_a', (0, 15, 64, 31)),    # Floccesy's red roof: two rows of tiles (Petalburg)
    'tl_shingle': ('ext57', 'c14_h2_yane', (0, 16, 16, 32)),   # Humilau's tan shingles, two rows (Lilycove)
}

def build():
    import nsbtx
    from PIL import Image
    os.makedirs(os.path.join(TEX, 'townlook'), exist_ok=True)
    srcs, adds = {}, []
    for new, (setname, name) in sorted(RENAMED.items()):
        src = srcs.setdefault(setname, open(os.path.join(TEX, setname + '.nsbtx'), 'rb').read())
        adds.append((src, name, name + '_pl', new, new + '_pl'))
        shutil.copy(os.path.join(TEX, setname, name + '.png'), os.path.join(TEX, 'townlook', new + '.png'))
    for new, (setname, name, box) in sorted(CROPS.items()):
        im = Image.open(os.path.join(TEX, setname, name + '.png')).convert('RGBA').crop(box)
        assert len(set(im.getdata())) <= 16, (new, 'more than 16 colours')
        im.save(os.path.join(TEX, 'townlook', new + '.png'))
        adds.append((nsbtx.image_source(new, im), new, new + '_pl'))
    base = srcs[sorted(srcs)[0]]
    out = nsbtx.merge(base, adds, drop=[n for n, _ in nsbtx._parse(base)['texs']])
    open(os.path.join(TEX, 'townlook.nsbtx'), 'wb').write(out)
    return out

if __name__ == '__main__':
    b = build(); print('work/tex/townlook.nsbtx', len(b), 'B')
