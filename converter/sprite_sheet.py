"""Contact sheets of overworld sprites, for choosing Black 2 object codes for Sapphire's NPCs (data/sprite_map.json).

    python3 sprite_sheet.py b2 FIRST LAST OUT.png [--cols N] [--scale N]   Black 2 object codes FIRST..LAST
    python3 sprite_sheet.py sapphire OUT.png [--scale N]                   every graphics id pokeruby's maps use
    python3 sprite_sheet.py review [MAP.json] [OUT.png]                    Sapphire sprite next to the chosen code
                                                                           (default data/sprite_map.json ->
                                                                           screenshots/sprite_map.png)
Read-only; nothing is written except the PNG.

Black 2 (files: external/pokebw2/build/b2_us/files, or $B2_FILES)
  Object code -> record in a/0/4/7 as GetIndexOfObjID (arm9 0x0200fe34): 0-376 -> code, 0x1000-0x126B (Pokemon)
  -> code - 0xE87, 0x2000-0x200A -> code - 0x1C1B (b2tools/sprites.py obj_record / ow_table). The record's res1 is
  the file in a/0/4/8, decoded with b2tools/nsbtx.py.
  entityType 1 = BTX0 billboard sheet, one texture per frame. The cell shows the front (facing down, standing)
  frame, chosen by spriteControllerType from looking at the sheets (FRONT_FRAME): 2 (7 frames: up, up-step, down,
  down-step, left x3) and 15 (9 frames) -> 2; 3 (12 frames, 3 per direction), 1 (player, 24) and the other walking
  sets with back frames first -> 3; 13/14 (Pokemon, 6/8 frames) -> 2; 5 (surf) -> 1; one-frame objects and the
  rest -> 0.
  entityType 2 = BMD0 3D object (0x2000-0x200A): the cell shows the model's textures, marked "3D".
  entityType 0 = no picture (res1 0; the WKOBJCODE codes 162-177 and codes used for invisible NPCs), drawn as an
  empty cell marked "none".
  Pokemon codes are labelled with their species from a/2/0/8 (LZ11; u16 species, sex, form, objCode records).

Sapphire (external/pokeruby)
  graphics_id (include/constants/event_objects.h) -> gObjectEventGraphicsInfo_* (object_event_graphics_info_pointers.h)
  -> .images pic table + .paletteTag (object_event_graphics_info.h) -> first frame overworld_frame(pic, w, h, k)
  (object_event_pic_tables.h, berry_tree_graphics_tables.h; frame 0 faces down; berry trees show frame 7, the grown
  tree, because their frame 0 is the empty dirt pile) -> pic PNG (object_event_graphics.h, .4bpp -> .png; frames laid
  left to right) coloured with the palette of the tag (sObjectEventSpritePalettes in src/event_object_movement.c ->
  graphics/object_events/palettes/NN.pal); the PNG's own palette when the tag has none.
  OBJ_EVENT_GFX_VAR_0..F have no picture (the game reads the real id from a var at run time).
"""
import sys, os, re, json, glob, struct, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
B2_FILES = os.environ.get('B2_FILES', os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'))
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import nsbtx  # noqa: E402
from sprites import ow_table, obj_record, lz11_decompress  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

BG = (112, 144, 160, 255)
# spriteControllerType -> frame that faces down standing (looked up on the sheets; walk sets put the back view first)
FRONT_FRAME = {1: 3, 2: 2, 3: 3, 5: 1, 6: 3, 13: 2, 14: 2, 15: 2, 16: 3, 17: 3, 18: 3, 19: 3, 20: 3, 21: 3, 27: 3,
               28: 3, 29: 3, 30: 3, 31: 3, 32: 2}

# ---------------------------------------------------------------------------------------------------- Black 2

class B2:
    def __init__(self, files=B2_FILES):
        self.table = ow_table(files)
        self.sheets = narc_entries(arc_path(files, 48))
        self.species = {}
        names = {}
        for line in open(os.path.join(ROOT, 'external', 'pokebw2', 'include', 'constants', 'species.h')):
            m = re.match(r'#define SPECIES_(\w+)\s+(\d+)\s*$', line)
            if m: names[int(m.group(2))] = m.group(1)
        d = narc_entries(arc_path(files, 208))[0]
        d = lz11_decompress(d) if d[0] == 0x11 else d
        for i in range(len(d) // 8):
            sp, sex, form, code = struct.unpack_from('<HHHH', d, 8 * i)
            self.species[code] = names.get(sp, str(sp)) + ('' if sex == 2 else ' ' + 'MF'[sex]) + (f' f{form}' if form else '')

    def record(self, code):
        return self.table[obj_record(code)]

    def frames(self, code):
        """[PIL RGBA image] of every frame (billboards) or texture (3D objects); [] when the code has no picture."""
        r = self.record(code)
        if r['entityType'] == 0: return []
        return [img for _, img, _ in nsbtx.decode(self.sheets[r['res1']])]

    def front(self, code):
        """(image, kind) with kind 'sprite', '3D' or 'none'."""
        r = self.record(code); ims = self.frames(code)
        if not ims: return None, 'none'
        if r['entityType'] != 1:
            w = sum(i.width for i in ims[:3]); h = max(i.height for i in ims[:3])
            out = Image.new('RGBA', (w, h)); x = 0
            for i in ims[:3]: out.alpha_composite(i, (x, 0)); x += i.width
            return out, '3D'
        k = FRONT_FRAME.get(r['spriteControllerType'], 0)
        return ims[k if k < len(ims) else 0], 'sprite'

    def label(self, code):
        return self.species.get(code, '')

# ---------------------------------------------------------------------------------------------------- Sapphire

class Sapphire:
    def __init__(self, root=RUBY):
        self.root = root
        src = lambda p: open(os.path.join(root, p), encoding='utf-8').read()
        self.ids = {m.group(1): int(m.group(2)) for m in
                    re.finditer(r'#define (OBJ_EVENT_GFX_\w+)\s+(\d+)', src('include/constants/event_objects.h'))}
        self.info_of = dict(re.findall(r'\[(OBJ_EVENT_GFX_\w+)\]\s*=\s*&(gObjectEventGraphicsInfo_\w+)',
                                       src('src/data/object_events/object_event_graphics_info_pointers.h')))
        self.info = {}
        for m in re.finditer(r'(gObjectEventGraphicsInfo_\w+) = \{(.*?)\};', src('src/data/object_events/object_event_graphics_info.h'), re.S):
            body = m.group(2)
            self.info[m.group(1)] = dict(palette_tag=int(re.search(r'\.paletteTag = (\w+)', body).group(1), 0),
                                         images=re.search(r'\.images = (\w+)', body).group(1))
        self.pic_table = {}
        for path in ('object_event_pic_tables.h', 'berry_tree_graphics_tables.h'):
            for m in re.finditer(r'(gObjectEventPicTable_\w+)\[\] = \{(.*?)\};', src('src/data/object_events/' + path), re.S):
                fr = re.findall(r'overworld_frame\((\w+),\s*(\d+),\s*(\d+),\s*(\d+)\)', m.group(2))
                self.pic_table[m.group(1)] = [(f[0], int(f[1]), int(f[2]), int(f[3])) for f in fr]
        gfx = src('src/data/object_events/object_event_graphics.h')
        pics = gfx + src('src/field_special_scene.c')      # the moving box's picture and palette 19 are there
        self.pic_file = {k: v.replace('.4bpp', '.png') for k, v in
                         re.findall(r'(gObjectEventPic_\w+)\[\] = INCBIN_U32\("([^"]+)"\)', pics)}
        self.pal_file = {k: v.replace('.gbapal', '.pal') for k, v in
                         re.findall(r'(gObjectEventPalette\d+)\[\] = INCBIN_U16\("([^"]+)"\)', pics)}
        mv = src('src/event_object_movement.c')
        tags = {k: int(v, 0) for k, v in re.findall(r'#define (OBJ_EVENT_PAL_TAG_\w+)\s+(0x[0-9A-Fa-f]+)', mv)}
        self.tag_pal = {tags[t]: p for p, t in re.findall(r'\{(gObjectEventPalette\d+),\s*(OBJ_EVENT_PAL_TAG_\w+)\}', mv)}

    def used(self):
        """Counter of graphics_id over every object_event in data/maps/*/map.json, and {id: set of maps}."""
        c = collections.Counter(); maps = collections.defaultdict(set)
        for f in glob.glob(os.path.join(self.root, 'data', 'maps', '*', 'map.json')):
            m = json.load(open(f))
            for o in m.get('object_events') or []:
                c[o['graphics_id']] += 1; maps[o['graphics_id']].add(m['name'])
        return c, maps

    def front(self, gfx):
        """PIL RGBA image of the id's first frame (faces down), or None for the VAR ids."""
        info = self.info.get(self.info_of.get(gfx))
        if info is None: return None
        table = self.pic_table[info['images']]
        # frame 0 faces down; a berry tree's frame 0 is the empty dirt pile, so show the grown tree (frame 7)
        pic, w, h, k = table[7] if 'BerryTree' in info['images'] else table[0]
        png = Image.open(os.path.join(self.root, self.pic_file[pic]))
        idx = png.convert('P') if png.mode != 'P' else png
        fw, fh = w * 8, h * 8; per_row = max(1, png.width // fw)
        box = (k % per_row * fw, k // per_row * fh, k % per_row * fw + fw, k // per_row * fh + fh)
        frame = idx.crop(box)
        pal = self.tag_pal.get(info['palette_tag'])
        if pal:
            vals = open(os.path.join(self.root, self.pal_file[pal])).read().split()
            n = int(vals[2]); rgb = [int(v) for v in vals[3:3 + 3 * n]]
            frame.putpalette(rgb + [0] * (768 - len(rgb)))
        data = frame.tobytes(); rgba = frame.convert('RGBA'); px = rgba.load()
        for i, v in enumerate(data):
            if v == 0: px[i % fw, i // fw] = (0, 0, 0, 0)
        return rgba

# ---------------------------------------------------------------------------------------------------- drawing

def fit(img, size, scale=2):
    """The image at `scale`x (same scale for every sprite, so sizes compare), shrunk only if it overflows the box."""
    if img is None: return None
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    if img.width > size or img.height > size:
        s = min(size / img.width, size / img.height)
        img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.NEAREST)
    return img

def paste_center(dst, img, x, y, w, h):
    if img is not None:
        dst.alpha_composite(img, (x + (w - img.width) // 2, y + (h - img.height) // 2))

def grid(cells, cols, cell, label_h=22, title=None):
    """cells: [(image or None, [label lines])] -> PIL image."""
    rows = (len(cells) + cols - 1) // cols
    top = 16 if title else 0
    W = cols * (cell + 4) + 4; H = top + rows * (cell + label_h + 4) + 4
    out = Image.new('RGBA', (W, H), (48, 48, 48, 255)); d = ImageDraw.Draw(out)
    if title: d.text((4, 2), title, fill=(255, 255, 255, 255))
    for i, (img, lines) in enumerate(cells):
        x = 4 + i % cols * (cell + 4); y = top + 4 + i // cols * (cell + label_h + 4)
        d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=BG)
        paste_center(out, img, x, y, cell, cell)
        for j, t in enumerate(lines[:2]):
            d.text((x + 1, y + cell + 1 + 10 * j), t[:cell // 6], fill=(255, 255, 255, 255))
    return out

def sheet_b2(first, last, out_path, cols=20, scale=2):
    b2 = B2(); cells = []
    for code in range(first, last + 1):
        img, kind = b2.front(code)
        lab = b2.label(code) or ('' if kind == 'sprite' else kind)
        cells.append((fit(img, 32 * scale, scale), [str(code), lab]))
    grid(cells, cols, 32 * scale, title=f'Black 2 object codes {first}-{last} (front frame)').convert('RGB').save(out_path)
    print(out_path, len(cells), 'codes')

def sheet_sapphire(out_path, cols=12, scale=2):
    s = Sapphire(); used, _ = s.used(); cells = []
    for gfx in sorted(used, key=lambda g: (s.ids.get(g, 999), g)):
        name = gfx.replace('OBJ_EVENT_GFX_', '')
        img = s.front(gfx)
        cells.append((fit(img, 32 * scale, scale), [name, f'x{used[gfx]}' + ('' if img else ' (var)')]))
    grid(cells, cols, 32 * scale, title=f'Sapphire graphics ids used in data/maps ({len(used)} ids, '
                                         f'{sum(used.values())} objects)').convert('RGB').save(out_path)
    print(out_path, len(cells), 'ids')

def sheet_review(map_path, out_path, cols=6, scale=2):
    """Each entry: Sapphire's picture | chosen Black 2 front frame, with id, code, name and S (stand-in) / - (null)."""
    s = Sapphire(); b2 = B2(); used, _ = s.used()
    m = json.load(open(map_path)); keys = [k for k in m if not k.startswith('_')]
    keys.sort(key=lambda g: (s.ids.get(g, 999), g))
    cell = 32 * scale; pw = 2 * cell + 6; ph = cell + 36
    rows = (len(keys) + cols - 1) // cols
    W = cols * (pw + 6) + 6; H = 20 + rows * (ph + 6) + 6
    out = Image.new('RGBA', (W, H), (48, 48, 48, 255)); d = ImageDraw.Draw(out)
    d.text((6, 4), 'Sapphire (left) -> Black 2 (right).  [S] = stand-in, [-] = null.  '
                   'Black 2 front frame; 3D objects show their textures.', fill=(255, 255, 255, 255))
    colour = {'match': (60, 140, 70, 255), 'stand_in': (190, 120, 30, 255), 'null': (150, 50, 50, 255)}
    for i, g in enumerate(keys):
        e = m[g]; x = 6 + i % cols * (pw + 6); y = 20 + i // cols * (ph + 6)
        kind = 'null' if e.get('code') is None else ('stand_in' if e.get('stand_in') else 'match')
        d.rectangle((x - 2, y - 2, x + pw + 1, y + ph + 1), fill=colour[kind])
        d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=BG)
        d.rectangle((x + cell + 6, y, x + 2 * cell + 5, y + cell - 1), fill=BG)
        paste_center(out, fit(s.front(g), cell, scale), x, y, cell, cell)
        if e.get('code') is not None:
            img, kind3d = b2.front(e['code'])
            paste_center(out, fit(img, cell, scale), x + cell + 6, y, cell, cell)
            if kind3d == '3D': d.text((x + cell + 8, y + 1), '3D model', fill=(255, 255, 255, 255))
        tag = {'match': '', 'stand_in': ' [S]', 'null': ' [-]'}[kind]
        d.text((x + 1, y + cell + 2), g.replace('OBJ_EVENT_GFX_', '')[:22], fill=(255, 255, 255, 255))
        d.text((x + 1, y + cell + 13), (f"{e['code']} " if e.get('code') is not None else '') + (e.get('b2') or '')[:18] + tag,
               fill=(255, 255, 255, 255))
        d.text((x + 1, y + cell + 24), f'x{used.get(g, 0)}', fill=(220, 220, 220, 255))
    out.convert('RGB').save(out_path)
    print(out_path, len(keys), 'entries')

def main(argv):
    opt = lambda name, default: int(argv[argv.index(name) + 1]) if name in argv else default
    pos = [a for i, a in enumerate(argv) if not a.startswith('--') and (i == 0 or not argv[i - 1].startswith('--'))]
    if not pos or pos[0] in ('-h', 'help'):
        print(__doc__); return
    if pos[0] == 'b2':
        sheet_b2(int(pos[1], 0), int(pos[2], 0), pos[3], opt('--cols', 20), opt('--scale', 2))
    elif pos[0] == 'sapphire':
        sheet_sapphire(pos[1], opt('--cols', 12), opt('--scale', 2))
    elif pos[0] == 'review':
        sheet_review(pos[1] if len(pos) > 1 else os.path.join(ROOT, 'data', 'sprite_map.json'),
                     pos[2] if len(pos) > 2 else os.path.join(ROOT, 'screenshots', 'sprite_map.png'),
                     opt('--cols', 6), opt('--scale', 2))
    else:
        sys.exit(__doc__)

if __name__ == '__main__':
    main(sys.argv[1:])
