"""Berry planting (HOENN_BERRY_PLANTING, notes/BERRY_PLANTING.md): the pictures of Gen 3's berry trees at every growth
stage, as one-frame Black 2 overworld sheets.

    python3 berry_planting_art.py            -> src/sprites/berry_planting/ (pictures.json + NNN-<name>/ folders)
    python3 berry_planting_art.py review     -> also screenshots/berry_planting/review.png

Source (the user's own decomp graphics, Sapphire's pixels 1:1, as models_objects.py berry_trees made the grown trees):
pokeruby graphics/object_events/pics/berry_trees/ and the object palettes. Gen 3 draws a tree (SetBerryTreeGraphics,
pokeemerald src/event_object_movement.c) with:
  - stage 1 PLANTED   dirt_pile.png frame 0 (16x16), the anim of BERRY_STAGE_PLANTED (sAnim_BerryTreeStage0: frame 0)
  - stage 2 SPROUTED  sprout.png frame 0 (16x16; the anim sways frames 1/2 of the pic table = sprout frames 0/1)
  - stage 3 TALLER    <tree>.png frame 0 (16x32; anim frames 3/4 = png frames 0/1)
  - stage 4 FLOWERING <tree>.png frame 2 (anim frames 5/6 = png frames 2/3)
  - stage 5 BERRIES   <tree>.png frame 4 (anim frames 7/8 = png frames 4/5; the frame the daily trees already show)
  each in OBJ palette slot gBerryTreePaletteSlotTablePointers[berry][stage - 1]: slot k (2-5) holds the field's palette
  k - 2 (pokeruby palettes/00-03.pal = pokeemerald npc_1-4.pal, checked identical). The tree picture of a berry is
  gBerryTreePicTablePointers[berry] (several berries share one: Bluk = Razz's, Enigma = Durin's, ...).
pokeemerald's tables, pictures and palettes are the same as pokeruby's (checked here: tables(); one set for all three
versions). Stage 0 (soft soil, no berry) is invisible in Gen 3 (the soil is the map's own tile, here the world's berry
soil decal): picture 0 is a blank frame, so the tree's actor stays talkable and solid but draws nothing.

Black 2 sheet: the Gen 3 frame centred and bottom-aligned in a 32x32 one-frame sheet (controller 4, as Black 2's Poke
Ball 0x6c / the gift box 208), its own 15 colours; the 16x32 frame's bottom = the tile's south edge, as the daily trees
(models_objects.py TREE_SCALE 1). b2tools/patches/berries.py appends one sheet + one object record per picture.
"""
import json, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ROOT, 'src', 'sprites', 'berry_planting')
NAMES = ['CHERI', 'CHESTO', 'PECHA', 'RAWST', 'ASPEAR', 'LEPPA', 'ORAN', 'PERSIM', 'LUM', 'SITRUS', 'FIGY', 'WIKI',
         'MAGO', 'AGUAV', 'IAPAPA', 'RAZZ', 'BLUK', 'NANAB', 'WEPEAR', 'PINAP', 'POMEG', 'KELPSY', 'QUALOT', 'HONDEW',
         'GREPA', 'TAMATO', 'CORNN', 'MAGOST', 'RABUTA', 'NOMEL', 'SPELON', 'PAMTRE', 'WATMEL', 'DURIN', 'BELUE',
         'LIECHI', 'GANLON', 'SALAC', 'PETAYA', 'APICOT', 'LANSAT', 'STARF', 'ENIGMA']   # Gen 3 berry 1-43 (gBerries)
STAGES = ['planted', 'sprouted', 'taller', 'flowering', 'berries']                    # BERRY_STAGE_* 1-5
TREE_FRAME = {3: 0, 4: 2, 5: 4}                                                       # stage -> <tree>.png frame


def tables(decomp):
    """{berry 0-42: (tree picture name, palette slots of stages 1-5)} from a decomp's berry_tree_graphics_tables.h."""
    tab = open(os.path.join(ROOT, 'external', decomp, 'src', 'data', 'object_events', 'berry_tree_graphics_tables.h')).read()

    def table(name, pat):
        body = tab.split(name)[1].split('};')[0]
        out, pos = {}, 0
        for line in body.split('\n'):
            m = re.search(pat, line)
            if not m: continue
            k = re.search(r'\[ITEM_(\w+)_BERRY - FIRST_BERRY_INDEX\]', line)     # pokeemerald: designated, pokeruby: in order
            out[NAMES.index(k.group(1)) if k else pos] = m.group(1)
            pos += 1
        return out
    pics = table('gBerryTreePicTablePointers[]', r'(?:gObjectEventPicTable_|sPicTable_)(\w+)BerryTree')
    slots = table('gBerryTreePaletteSlotTablePointers[]', r'gBerryTreePaletteSlotTable_(\w+)')
    st = {m.group(1): tuple(int(x) for x in m.group(2).split(','))
          for m in re.finditer(r'gBerryTreePaletteSlotTable_(\w+)\[\] = \{([^}]*)\}', tab)}
    out = {b: (pics[b], st[slots[b]]) for b in range(43)}
    assert all(len(v[1]) == 5 for v in out.values())
    return out


def palette(slot):
    """The 16 colours of OBJ palette slot 2-5 (pokeruby graphics/object_events/palettes/0<slot-2>.pal)."""
    lines = open(os.path.join(ROOT, 'external', 'pokeruby', 'graphics', 'object_events', 'palettes',
                              f'{slot - 2:02d}.pal')).read().split('\n')[3:19]
    return [tuple(int(v) for v in l.split()) for l in lines]


def gen3_frame(pic, stage):
    """The Gen 3 frame (index array, 16x16 or 16x32) of a picture at a stage."""
    d = os.path.join(ROOT, 'external', 'pokeruby', 'graphics', 'object_events', 'pics', 'berry_trees')
    if stage == 1: return np.array(Image.open(os.path.join(d, 'dirt_pile.png')))[:, 0:16]
    if stage == 2: return np.array(Image.open(os.path.join(d, 'sprout.png')))[:, 0:16]
    f = TREE_FRAME[stage]
    return np.array(Image.open(os.path.join(d, pic.lower() + '.png')))[:, 16 * f:16 * f + 16]


def pictures():
    """[{name, stage, pic, slot}] (index = picture number; 0 blank) and {berry 1-43: [picture of stage 1..5]}."""
    t = tables('pokeruby')
    assert t == tables('pokeemerald'), 'pokeemerald berry tree tables differ from pokeruby\'s: make one set per version'
    pics, index, by_berry = [dict(name='blank', stage=0, pic=None, slot=2)], {}, {}
    for b in range(43):
        tree, slots = t[b]
        row = []
        for stage in range(1, 6):
            key = ('dirt' if stage == 1 else 'sprout' if stage == 2 else tree, stage, slots[stage - 1])
            if key not in index:
                index[key] = len(pics)
                nm = key[0].lower() if stage < 3 else f'{tree.lower()}-{STAGES[stage - 1]}'
                pics.append(dict(name=nm, stage=stage, pic=None if stage < 3 else tree, slot=slots[stage - 1]))
            row.append(index[key])
        by_berry[b + 1] = row
    # one name per picture: the palette joins the name where a picture comes in two palettes
    seen = {}
    for p in pics: seen[p['name']] = seen.get(p['name'], 0) + 1
    for p in pics:
        if seen[p['name']] > 1: p['name'] += f'-p{p["slot"] - 2:02d}'
    return pics, by_berry


def build():
    sys.path.insert(0, HERE)
    import sprites
    pics, by_berry = pictures()
    os.makedirs(OUT, exist_ok=True)
    for i, p in enumerate(pics):
        frame = np.zeros((32, 32), np.uint8)
        if p['stage']:
            src = gen3_frame(p['pic'], p['stage'])
            h, w = src.shape
            frame[32 - h:32, (32 - w) // 2:(32 - w) // 2 + w] = src     # bottom = the tile's south edge, centred
        cols = palette(p['slot'])
        d = os.path.join(OUT, f'{i:03d}-{p["name"]}')
        os.makedirs(d, exist_ok=True)
        im = Image.fromarray(frame, 'P')
        im.putpalette([v for c in cols for v in c] + [0] * (768 - 48))
        im.save(os.path.join(d, 'frame_00.png'), transparency=0)
        sprites.write_pal(os.path.join(d, 'palette.pal'), cols)
        sprites.write_json(os.path.join(d, 'sprite.json'), dict(
            kind='overworld', frames=1, size=[32, 32], controller=4, textures=['t4x4x1.0'], palette='t4x4x1',
            name=p['name'], stage=p['stage'],
            sapphire=('blank (stage 0: soft soil, invisible in Gen 3)' if not p['stage'] else
                      f'pokeruby graphics/object_events/pics/berry_trees/'
                      f'{"dirt_pile" if p["stage"] == 1 else "sprout" if p["stage"] == 2 else p["pic"].lower()}.png '
                      f'frame {0 if p["stage"] < 3 else TREE_FRAME[p["stage"]]}, palette {p["slot"] - 2:02d}'),
            made_by='b2tools/berry_planting_art.py (Sapphire\'s pixels 1:1)'))
    json.dump({'_doc': 'Generated by b2tools/berry_planting_art.py: Gen 3 berry tree pictures (one-frame sheets, '
                       'b2tools/patches/berries.py appends them); berries: Gen 3 berry 1-43 -> picture of stages 1-5; '
                       'picture 0 = blank (stage 0, soft soil).',
               'pictures': [dict(folder=f'{i:03d}-{p["name"]}', stage=p['stage'], shadow=1 if p['stage'] >= 3 else 0)
                            for i, p in enumerate(pics)],
               'berries': {NAMES[b - 1]: row for b, row in by_berry.items()}},
              open(os.path.join(OUT, 'pictures.json'), 'w'), indent=1)
    return pics, by_berry


def review(pics, by_berry):
    """screenshots/berry_planting/review.png: each tree picture's stages (planted, sprouted, taller, flowering,
    berries) as Black 2 frames on grass-green, with the berries that use it."""
    from PIL import ImageDraw
    rows, seen = [], set()
    for b in range(1, 44):
        key = tuple(by_berry[b])
        if key in seen: continue
        seen.add(key)
        rows.append((', '.join(NAMES[c - 1].title() for c in range(1, 44) if tuple(by_berry[c]) == key), key))
    S = 2
    W, H = 220 + 5 * 36 * S, 8 + len(rows) * (32 * S + 6)
    img = Image.new('RGB', (W, H), (112, 168, 96))
    dr = ImageDraw.Draw(img)
    for r, (label, key) in enumerate(rows):
        y = 4 + r * (32 * S + 6)
        dr.text((4, y + 24), label[:34], fill=(255, 255, 255))
        for s, pi in enumerate(key):
            p = pics[pi]
            im = Image.open(os.path.join(OUT, f'{pi:03d}-{p["name"]}', 'frame_00.png')).convert('RGBA')
            im = im.resize((32 * S, 32 * S), Image.NEAREST)
            img.paste(im, (220 + s * 36 * S, y), im)
    d = os.path.join(ROOT, 'screenshots', 'berry_planting')
    os.makedirs(d, exist_ok=True)
    img.save(os.path.join(d, 'review.png'))
    return os.path.join(d, 'review.png')


if __name__ == '__main__':
    pics, by_berry = build()
    print(f'{len(pics)} pictures (1 blank, {sum(1 for p in pics if p["stage"] in (1, 2))} dirt/sprout, '
          f'{sum(1 for p in pics if p["stage"] >= 3)} tree stages) in {OUT}')
    if 'review' in sys.argv[1:]: print(review(pics, by_berry))
