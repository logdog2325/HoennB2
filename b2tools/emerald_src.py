"""Emerald's own graphics, read from the pokeemerald decomp and checked byte for byte against the user's own Emerald
dump (roms/emerald_original.gba, BPEE, SHA-1 f3ae0881..., read-only; notes/DECISIONS.md 2026-10-11). Nothing is
downloaded and nothing is drawn: this module only reads.

    python3 emerald_src.py verify        every picture, map and palette the Emerald art tools use, found in the dump

What pokeemerald's build does with each file (Makefile / graphics_file_rules.mk, tools/gbagfx), reproduced here:
- `.4bpp` of an indexed PNG: 8x8 tiles, two pixels per byte (low nibble first). With `-mwidth W -mheight H` the PNG is
  read as W x H-tile metatiles (left to right, then down), the tiles of each metatile row-major; without, the whole
  PNG's tiles row-major. The object-event frames (16x32 = 2x4 tiles, 32x32 = 4x4) are such metatiles.
- `.8bpp`: one byte per pixel, same tile order.
- `.gbapal` of a JASC .pal: each 8-bit channel / 8 into BGR555 (gbagfx), little-endian u16s.
- `.lz`: GBA LZ77 (header 0x10 + u24 size); pokeemerald's compressor output differs from Game Freak's, so a
  compressed file is checked by decompressing every LZ77 stream in the dump with the right size header and comparing.
"""
import hashlib, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
PEM = os.path.join(ROOT, 'external', 'pokeemerald')
ROM_PATH = os.path.join(ROOT, 'roms', 'emerald_original.gba')
ROM_SHA1 = 'f3ae088181bf583e55daf962a92bb46f4f1d07b7'

_rom = {}
def rom():
    if 'd' not in _rom:
        d = open(ROM_PATH, 'rb').read()
        assert hashlib.sha1(d).hexdigest() == ROM_SHA1, 'roms/emerald_original.gba is not the user\'s BPEE dump'
        _rom['d'] = d
    return _rom['d']

# ---------------------------------------------------------------------------------------------------- files

def png_indices(path):
    """(index array rows (list of bytes), width, height, 16- or 256-entry RGB palette of the PNG)."""
    from PIL import Image
    im = Image.open(path)
    assert im.mode == 'P', f'{path}: not indexed'
    p = im.getpalette()
    return im.tobytes(), im.size[0], im.size[1], [tuple(p[3 * i:3 * i + 3]) for i in range(len(p) // 3)]

def jasc(path):
    """A JASC .pal's colours as gbagfx builds the .gbapal: 8-bit value // 8 per channel, shown as 8-bit RGB (c << 3 |
    c >> 2, as the DS tools in b2tools show 5-bit colours)."""
    vals = open(os.path.join(PEM, path) if not os.path.isabs(path) else path).read().split()
    n = int(vals[2])
    out = []
    for i in range(n):
        c5 = [int(vals[3 + 3 * i + j]) // 8 for j in range(3)]
        out.append(tuple((c << 3) | (c >> 2) for c in c5))
    return out

def gbapal(path):
    vals = open(os.path.join(PEM, path) if not os.path.isabs(path) else path).read().split()
    n = int(vals[2])
    return b''.join(struct.pack('<H', sum((int(vals[3 + 3 * i + j]) // 8) << (5 * j) for j in range(3)))
                    for i in range(n))

def tiles_of(pix, w, h, mw=None, mh=None):
    """[64-pixel tiles] in gbagfx order (metatiles mw x mh tiles if given)."""
    tw, th = w // 8, h // 8
    mw, mh = mw or tw, mh or th
    out = []
    for my in range(th // mh):
        for mx in range(tw // mw):
            for ty in range(mh):
                for tx in range(mw):
                    x0, y0 = (mx * mw + tx) * 8, (my * mh + ty) * 8
                    out.append(bytes(pix[(y0 + y) * w + x0 + x] for y in range(8) for x in range(8)))
    return out

def to4bpp(tiles):
    return b''.join(bytes((t[i] & 15) | (t[i + 1] & 15) << 4 for i in range(0, 64, 2)) for t in tiles)

def to8bpp(tiles):
    return b''.join(tiles)

def png_4bpp(path, mw=None, mh=None, bpp=4):
    pix, w, h, _ = png_indices(os.path.join(PEM, path))
    t = tiles_of(pix, w, h, mw, mh)
    return to4bpp(t) if bpp == 4 else to8bpp(t)

# ---------------------------------------------------------------------------------------------------- the dump

def lz77_decompress(d, pos=0, limit=None):
    """GBA LZ77 (type 0x10) at d[pos:]; None if the stream is not valid."""
    if d[pos] != 0x10:
        return None
    size = d[pos + 1] | d[pos + 2] << 8 | d[pos + 3] << 16
    if limit and size != limit:
        return None
    p, out = pos + 4, bytearray()
    try:
        while len(out) < size:
            flags = d[p]; p += 1
            for bit in range(8):
                if len(out) >= size: break
                if flags & (0x80 >> bit):
                    x = d[p] << 8 | d[p + 1]; p += 2
                    n, disp = (x >> 12) + 3, (x & 0xfff) + 1
                    if disp > len(out): return None
                    for _ in range(n): out.append(out[-disp])
                else:
                    out.append(d[p]); p += 1
    except IndexError:
        return None
    return bytes(out[:size])

def find_raw(data):
    """GBA addresses (0x08xxxxxx) of `data` in the dump (every occurrence)."""
    d, out, i = rom(), [], 0
    while True:
        i = d.find(data, i)
        if i < 0: return out
        out.append(0x08000000 + i); i += 1

def find_lz(data):
    """GBA addresses of LZ77 streams in the dump that decompress to exactly `data`."""
    d = rom()
    head = bytes([0x10, len(data) & 0xff, len(data) >> 8 & 0xff, len(data) >> 16 & 0xff])
    out, i = [], 0
    while True:
        i = d.find(head, i)
        if i < 0: return out
        if i % 4 == 0 and lz77_decompress(d, i, len(data)) == data:
            out.append(0x08000000 + i)
        i += 1

# ---------------------------------------------------------------------------------------------------- object events

class Emerald:
    """pokeemerald's object-event tables: graphics id -> (palette, pic table) -> frames (as converter/sprite_sheet.py
    does for pokeruby; pokeemerald names them sPicTable_* / gObjectEventPal_* and builds them with INCGFX_*)."""
    def __init__(self, root=PEM):
        self.root = root
        src = lambda p: open(os.path.join(root, p), encoding='utf-8').read()
        self.info_of = dict(re.findall(r'\[(OBJ_EVENT_GFX_\w+)\]\s*=\s*&(gObjectEventGraphicsInfo_\w+)',
                                       src('src/data/object_events/object_event_graphics_info_pointers.h')))
        self.info = {}
        for m in re.finditer(r'(gObjectEventGraphicsInfo_\w+) = \{(.*?)\};',
                             src('src/data/object_events/object_event_graphics_info.h'), re.S):
            body = m.group(2)
            self.info[m.group(1)] = dict(palette_tag=re.search(r'\.paletteTag = (\w+)', body).group(1),
                                         images=re.search(r'\.images = (\w+)', body).group(1))
        self.pic_table = {}
        for m in re.finditer(r'(sPicTable_\w+)\[\] = \{(.*?)\};', src('src/data/object_events/object_event_pic_tables.h'), re.S):
            fr = re.findall(r'overworld_frame\((\w+),\s*(\d+),\s*(\d+),\s*(\d+)\)', m.group(2))
            self.pic_table[m.group(1)] = [(f[0], int(f[1]), int(f[2]), int(f[3])) for f in fr]
        gfx = src('src/data/object_events/object_event_graphics.h')
        self.pic_file = {k: (v, a) for k, v, a in
                         re.findall(r'(gObjectEventPic_\w+)\[\] = INCGFX_U32\("([^"]+)", "\.4bpp"(?:, "([^"]*)")?\)', gfx)}
        self.pal_file = dict(re.findall(r'(gObjectEventPal_\w+)\[\] = INCGFX_U16\("([^"]+)", "\.gbapal"\)', gfx))
        mv = src('src/event_object_movement.c')
        self.tag_pal = {t: p for p, t in re.findall(r'\{(gObjectEventPal_\w+),\s*(OBJ_EVENT_PAL_TAG_\w+)\}', mv)}

    def frames(self, gfx):
        """([frames as 2D index arrays], 16 RGB colours (the game's 5-bit colours), [(pic, png path)])."""
        import numpy as np
        from PIL import Image
        info = self.info[self.info_of[gfx]]
        pal = jasc(self.pal_file[self.tag_pal[info['palette_tag']]])
        out, used = [], []
        for pic, w, h, k in self.pic_table[info['images']]:
            path, _ = self.pic_file[pic]
            png = Image.open(os.path.join(self.root, path))
            fw, fh = w * 8, h * 8; per_row = max(1, png.width // fw)
            box = (k % per_row * fw, k // per_row * fh, k % per_row * fw + fw, k // per_row * fh + fh)
            out.append(np.array(png.crop(box)).astype(np.uint8))
            if (pic, path) not in used: used.append((pic, path))
        return out, (pal + [(0, 0, 0)] * 16)[:16], used

    def verify(self, gfx):
        """[(what, [addresses])] for the pictures and palette of a graphics id (raw 4bpp, as the game stores them)."""
        info = self.info[self.info_of[gfx]]
        res = []
        for pic, (path, args) in [(p, self.pic_file[p]) for p, _ in
                                  [(q, None) for q in dict.fromkeys(f[0] for f in self.pic_table[info['images']])]]:
            mw = mh = None
            if args:
                m = re.search(r'-mwidth (\d+) -mheight (\d+)', args)
                if m: mw, mh = int(m.group(1)), int(m.group(2))
            res.append((path, find_raw(png_4bpp(path, mw, mh))))
        pf = self.pal_file[self.tag_pal[info['palette_tag']]]
        res.append((pf, find_raw(gbapal(pf))))
        return res

_E = {}
def emerald():
    if 'e' not in _E:
        _E['e'] = Emerald()
    return _E['e']

# ---------------------------------------------------------------------------------------------------- trainer pictures

def png_pal(path):
    """The 16 colours gbagfx's `.gbapal` takes from an indexed PNG (8-bit // 8), as 8-bit RGB, and the bytes."""
    _, _, _, ppal = png_indices(os.path.join(PEM, path))
    c5 = [[v // 8 for v in rgb] for rgb in ppal[:16]]
    return [tuple((c << 3) | (c >> 2) for c in c) for c in c5], \
        b''.join(struct.pack('<H', c[0] | c[1] << 5 | c[2] << 10) for c in c5)

def trainer_pic(side, name, pal=None):
    """(64 x 64*n index array, 16 RGB) of graphics/trainers/{front,back}_pics/<name>.png with the palette the game
    loads (gTrainerPalette_*): palettes/<pal>.pal, or 'png:<path>' = that PNG's own palette (Steven's back uses his
    front picture's: back_pic_tables.h gTrainerBackPicPaletteTable, graphics/trainers.h gTrainerPalette_Steven)."""
    import numpy as np
    pix, w, h, ppal = png_indices(os.path.join(PEM, 'graphics', 'trainers', f'{side}_pics', f'{name}.png'))
    if pal and pal.startswith('png:'):
        cols = png_pal(pal[4:])[0]
    elif pal:
        cols = jasc(os.path.join('graphics', 'trainers', 'palettes', f'{pal}.pal'))
    else:
        cols = png_pal(os.path.join('graphics', 'trainers', f'{side}_pics', f'{name}.png'))[0]
    return np.frombuffer(pix, np.uint8).reshape(h, w).copy(), (cols + [(0, 0, 0)] * 16)[:16]

def verify_trainer(side, name, pal=None):
    path = os.path.join('graphics', 'trainers', f'{side}_pics', f'{name}.png')
    data = png_4bpp(path)
    res = [(path, find_lz(data) if side == 'front' else find_raw(data))]
    if pal and pal.startswith('png:'):
        res.append((pal + ' palette', find_lz(png_pal(pal[4:])[1])))
    elif pal:
        pp = os.path.join('graphics', 'trainers', 'palettes', f'{pal}.pal')
        res.append((pp, find_lz(gbapal(pp))))
    return res

# ---------------------------------------------------------------------------------------------------- title screen

STEVEN_PAL = 'png:graphics/trainers/front_pics/steven.png'

TITLE = os.path.join('graphics', 'title_screen')

def verify_title():
    """Emerald's title scene files (src/title_screen.c, src/graphics.c): Rayquaza and the clouds (4bpp, LZ), their
    maps (LZ), the palette (pokemon_logo 224 colours + rayquaza_and_clouds 16 = gTitleScreenBgPalettes, raw)."""
    out = []
    for f in ('rayquaza.png', 'clouds.png'):
        out.append((f, find_lz(png_4bpp(os.path.join(TITLE, f)))))
    for f in ('rayquaza.bin', 'clouds.bin'):
        out.append((f, find_lz(open(os.path.join(PEM, TITLE, f), 'rb').read())))
    out.append(('pokemon_logo.png (8bpp)', find_lz(png_4bpp(os.path.join(TITLE, 'pokemon_logo.png'), bpp=8))))
    out.append(('pokemon_logo.bin', find_lz(open(os.path.join(PEM, TITLE, 'pokemon_logo.bin'), 'rb').read())))
    out.append(('emerald_version.png (8bpp, 8x4 metatiles)',
                find_lz(png_4bpp(os.path.join(TITLE, 'emerald_version.png'), 8, 4, bpp=8))))
    out.append(('emerald_version.png palette', find_raw(png_pal(os.path.join(TITLE, 'emerald_version.png'))[1])))
    out.append(('press_start.png (4bpp, 4x1 metatiles, 48 tiles)',
                find_lz(png_4bpp(os.path.join(TITLE, 'press_start.png'), 4, 1)[:48 * 32])))
    out.append(('press_start.png palette', find_raw(png_pal(os.path.join(TITLE, 'press_start.png'))[1])))
    out.append(('logo_shine.png', find_lz(png_4bpp(os.path.join(TITLE, 'logo_shine.png')))))
    logo = gbapal(os.path.join(TITLE, 'pokemon_logo.pal'))[:224 * 2]
    rc = gbapal(os.path.join(TITLE, 'rayquaza_and_clouds.pal'))
    out.append(('pokemon_logo.pal[:224] + rayquaza_and_clouds.pal (gTitleScreenBgPalettes)', find_raw(logo + rc)))
    return out

def verify(report=print):
    bad = 0
    e = emerald()
    groups = [('title scene', verify_title())]
    for who in ('BRENDAN', 'MAY'):
        for s in ('NORMAL', 'MACH_BIKE', 'SURFING', 'FIELD_MOVE', 'FISHING'):
            groups.append((f'{who} {s}', e.verify(f'OBJ_EVENT_GFX_{who}_{s}')))
    groups.append(('Brendan front', verify_trainer('front', 'brendan', 'brendan')))
    groups.append(('May front', verify_trainer('front', 'may', 'may')))
    groups.append(('Brendan back', verify_trainer('back', 'brendan', 'brendan')))
    groups.append(('May back', verify_trainer('back', 'may', 'may')))
    groups.append(('Steven back', verify_trainer('back', 'steven', STEVEN_PAL)))
    for title, res in groups:
        for what, where in res:
            ok = bool(where)
            bad += not ok
            report(f'{"ok " if ok else "MISSING"} {title}: {what} at {", ".join(f"{a:#09x}" for a in where) or "-"}')
    return bad

if __name__ == '__main__':
    if sys.argv[1:2] == ['verify']:
        n = verify()
        print('all found in the dump' if n == 0 else f'{n} not found')
        sys.exit(1 if n else 0)
    print(__doc__)
