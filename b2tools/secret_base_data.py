"""Secret Bases and decorations: reads Gen 3's data (pokeruby, checked equal in pokeemerald) for everything else.

    python3 secret_base_data.py check          the versions agree? (decorations, layouts, spots)
    python3 secret_base_data.py sheet OUT.png  every decoration's picture on one sheet

Layouts, spots and the decoration table are the same in pokeruby and pokeemerald (`check`), so one set of data serves
Sapphire, Ruby and Emerald; the shops and gifts differ per version (notes/SECRET_BASES.md).
"""
import hashlib, json, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')
STYLES = [('RedCave', 'red_cave'), ('BrownCave', 'brown_cave'), ('BlueCave', 'blue_cave'), ('YellowCave', 'yellow_cave'),
          ('Tree', 'tree'), ('Shrub', 'shrub')]
SHAPES = {'DECORSHAPE_1x1': (1, 1), 'DECORSHAPE_2x1': (2, 1), 'DECORSHAPE_3x1': (3, 1), 'DECORSHAPE_4x2': (4, 2),
          'DECORSHAPE_2x2': (2, 2), 'DECORSHAPE_1x2': (1, 2), 'DECORSHAPE_1x3': (1, 3), 'DECORSHAPE_2x4': (2, 4),
          'DECORSHAPE_3x3': (3, 3), 'DECORSHAPE_3x2': (3, 2)}
CATS = ['DESK', 'CHAIR', 'PLANT', 'ORNAMENT', 'MAT', 'POSTER', 'DOLL', 'CUSHION']
PERMS = ['SOLID_FLOOR', 'PASS_FLOOR', 'BEHIND_FLOOR', 'NA_WALL', 'SOLID_MAT']


def constants(path):
    out = {}
    for m in re.finditer(r'#define\s+(\w+)\s+(\d+|0x[0-9a-fA-F]+)\s*$', open(path).read(), re.M):
        out[m.group(1)] = int(m.group(2), 0)
    return out


DECOR_IDS = constants(os.path.join(RUBY, 'include', 'constants', 'decorations.h'))


def _table(path):
    out = {}
    t = open(path).read()
    pat = r'\.id = (\w+),\s*\.name = (?:_\("([^"]*)"\)|(\w+)),\s*\.permission = (\w+),\s*\.shape = (\w+),' \
          r'\s*\.category = (\w+),\s*\.price = (\d+),\s*\.description = (\w+),\s*\.tiles = (\w+)'
    for m in re.finditer(pat, t):
        g = m.groups()
        out[g[0]] = dict(perm=g[3].replace('DECORPERM_', '').replace('SPRITE', 'SOLID_MAT'), shape=g[4],
                         cat=g[5].replace('DECORCAT_', ''), price=int(g[6]), gfx=g[8])
    return out


def _tile_arrays(path):
    out = {}
    for m in re.finditer(r'const u16 (DecorGfx_\w+)\[\] = \{(.*?)\};', open(path).read(), re.S):
        out[m.group(1)] = [v.strip() for v in m.group(2).replace('\n', ' ').split(',') if v.strip()]
    return out


def _names(path):
    """pokeemerald's header has the English names as _("..."); pokeruby's table in decoration.c is the same."""
    out = {}
    for m in re.finditer(r'\.id = (\w+),\s*\.name = _\("([^"]*)"\)', open(path).read()):
        out[m.group(1)] = m.group(2)
    return out


def decorations():
    """[121 dicts] by decoration id: name, perm, cat, price, w, h, tiles (metatile numbers), gfx (a doll's object)."""
    t = _table(os.path.join(EMERALD, 'src', 'data', 'decoration', 'header.h'))
    names = _names(os.path.join(EMERALD, 'src', 'data', 'decoration', 'header.h'))
    arrays = _tile_arrays(os.path.join(RUBY, 'src', 'decoration.c'))      # (numbers; pokeemerald's are named constants)
    out = [None] * 121
    for k, d in t.items():
        n = DECOR_IDS[k]
        w, h = SHAPES[d['shape']]
        vals = arrays[d['gfx']]
        obj = vals[0] if vals and vals[0].startswith('OBJ_EVENT_GFX') else None
        out[n] = dict(id=n, const=k, name=names[k], perm=d['perm'], cat=d['cat'], price=d['price'], w=w, h=h,
                      tiles=None if obj else [int(v, 0) for v in vals], obj=obj)
    assert all(out), [i for i, d in enumerate(out) if not d]
    return out


def check():
    a = _table(os.path.join(RUBY, 'src', 'data', 'decoration', 'decorations.h'))
    b = _table(os.path.join(EMERALD, 'src', 'data', 'decoration', 'header.h'))
    assert len(a) == len(b) == 121 and a == b, [k for k in b if a.get(k) != b[k]]
    ra, rb = _tile_arrays(os.path.join(RUBY, 'src', 'decoration.c')), _tile_arrays(os.path.join(EMERALD, 'src', 'data', 'decoration', 'tiles.h'))
    diffs = [k for k in rb if len(ra.get(k, ())) != len(rb[k])]
    assert not diffs, diffs
    print('decoration table and tile lists: equal in pokeruby and pokeemerald (121)')
    for rel in ('data/tilesets/secondary/secret_base/metatiles.bin', 'data/tilesets/secondary/secret_base/metatile_attributes.bin',
                'data/tilesets/primary/secret_base/metatiles.bin', 'data/tilesets/primary/secret_base/metatile_attributes.bin'):
        ha = hashlib.md5(open(os.path.join(RUBY, rel), 'rb').read()).hexdigest()
        hb = hashlib.md5(open(os.path.join(EMERALD, rel), 'rb').read()).hexdigest()
        print(rel, 'same' if ha == hb else 'DIFFERENT')
    return True


class Tileset:
    """Gen 3's secret base tilesets for one style (primary + the style's secondary tiles and palettes)."""

    def __init__(self, style='red_cave', root=RUBY):
        ts = os.path.join(root, 'data', 'tilesets')
        self.p = self._load(os.path.join(ts, 'primary', 'secret_base'), os.path.join(ts, 'primary', 'secret_base'))
        self.s = self._load(os.path.join(ts, 'secondary', 'secret_base', style), os.path.join(ts, 'secondary', 'secret_base'))
        self.pals = self.p['pals'][:6] + self.s['pals'][6:13] + self.p['pals'][13:]

    @staticmethod
    def _load(gfx, data):
        idx = np.array(Image.open(os.path.join(gfx, 'tiles.png')))
        if idx.max() > 15: idx = idx & 15
        h, w = idx.shape
        tiles = [idx[y * 8:y * 8 + 8, x * 8:x * 8 + 8] for y in range(h // 8) for x in range(w // 8)]
        pals = []
        for i in range(16):
            lines = open(os.path.join(gfx, 'palettes', f'{i:02d}.pal')).read().split('\n')[3:19]
            pals.append(np.array([[int(v) for v in l.split()] for l in lines if l.strip()], dtype=np.uint8))
        mt = np.frombuffer(open(os.path.join(data, 'metatiles.bin'), 'rb').read(), dtype='<u2').reshape(-1, 8)
        attr = np.frombuffer(open(os.path.join(data, 'metatile_attributes.bin'), 'rb').read(), dtype='<u2')
        return dict(tiles=tiles, pals=pals, mt=mt, attr=attr)

    def tile(self, t):
        if t < 512: return self.p['tiles'][t]
        t -= 512
        return self.s['tiles'][t] if t < len(self.s['tiles']) else np.zeros((8, 8), np.uint8)

    def attr(self, m):
        """The metatile's u16 attributes: behaviour in the low byte, layer type in the top nibble."""
        a = self.p['attr'] if m < 512 else self.s['attr']
        return int(a[m if m < 512 else m - 512])

    def render(self, m, layers=(0, 1)):
        """(16, 16, 4) RGBA of metatile m; colour 0 of every layer is transparent, as Gen 3 draws over its backdrop."""
        src = self.p['mt'] if m < 512 else self.s['mt']
        e_ = src[m if m < 512 else m - 512]
        out = np.zeros((16, 16, 4), np.uint8)
        for layer in layers:
            for q in range(4):
                e = int(e_[layer * 4 + q])
                t, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, (e >> 12) & 0xF
                px = self.tile(t)
                if hf: px = px[:, ::-1]
                if vf: px = px[::-1, :]
                rgb = self.pals[pal][px]
                mask = px != 0
                oy, ox = (q // 2) * 8, (q % 2) * 8
                reg = out[oy:oy + 8, ox:ox + 8]
                reg[mask, :3] = rgb[mask]
                reg[mask, 3] = 255
        return out


DOLL_PICS = None


def doll_picture(obj):
    """A doll's or cushion's picture: its object event's pic (graphics/object_events/pics/dolls or misc), RGBA."""
    global DOLL_PICS
    if DOLL_PICS is None:
        DOLL_PICS = {}
        info = open(os.path.join(EMERALD, 'src', 'data', 'object_events', 'object_event_graphics_info_pointers.h')).read()
        info_ptr = dict(re.findall(r'\[(OBJ_EVENT_GFX_\w+)\]\s*=\s*&(gObjectEventGraphicsInfo_\w+)', info))
        gi = open(os.path.join(EMERALD, 'src', 'data', 'object_events', 'object_event_graphics_info.h')).read()
        pt = dict(re.findall(r'(gObjectEventGraphicsInfo_\w+) = \{.*?\.paletteTag = (\w+).*?\.images = (\w+)', gi, re.S) and [])
        DOLL_PICS = dict(info_ptr=info_ptr, gi=gi)
    gname = DOLL_PICS['info_ptr'][obj]
    m = re.search(gname + r' = \{(.*?)\};', DOLL_PICS['gi'], re.S)
    body = m.group(1)
    tag = re.search(r'\.paletteTag = (\w+)', body).group(1)
    size = (int(re.search(r'\.width = (\d+)', body).group(1)), int(re.search(r'\.height = (\d+)', body).group(1)))
    pics = re.search(r'\.images = (\w+)', body).group(1)
    return dict(g=gname, tag=tag, size=size, pics=pics)


def decoration_image(d, ts=None):
    """RGBA numpy picture of a metatile decoration: rows top to bottom, as gDecorations' tile order."""
    ts = ts or TS()
    w, h = d['w'], d['h']
    out = np.zeros((h * 16, w * 16, 4), np.uint8)
    for i, m in enumerate(d['tiles']):
        y, x = i // w, i % w
        out[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = ts.render(0x200 + m)
    return out


_TS = {}


def TS(style='red_cave'):
    if style not in _TS: _TS[style] = Tileset(style)
    return _TS[style]


def sheet(path):
    from PIL import ImageDraw
    ds = decorations()
    cols = 12
    cell = 72
    rows = (len(ds) + cols - 1) // cols
    s = Image.new('RGB', (cols * cell, rows * (cell + 12)), (120, 120, 150))
    dr = ImageDraw.Draw(s)
    for i, d in enumerate(ds):
        x, y = (i % cols) * cell, (i // cols) * (cell + 12)
        dr.text((x + 1, y), f"{i} {d['name'][:9]}", fill=(255, 255, 0))
        if d['tiles']:
            im = Image.fromarray(decoration_image(d))
            s.paste(im, (x + 2, y + 12), im)
        else:
            dr.text((x + 2, y + 24), d['obj'][14:24], fill=(255, 200, 200))
    s.save(path)


if __name__ == '__main__':
    if sys.argv[1] == 'check': check()
    elif sys.argv[1] == 'sheet': sheet(sys.argv[2])


# ==== generated data ================================================================================================
# Zones, in the order of LAYOUTS (Red, Brown, Blue, Yellow cave, Tree, Shrub x 1-4). Chosen 2026-11-01: no Hoenn map or room,
# own entity file, no gimmick; none named by a zone-keyed table of the engine except the Reversal Mountain and Relic
# Passage zones' dust clouds' shard table (no wild data here, so no dust clouds). 506-508 have no camera box of their own
# (Emerald shares the same box of another same-sized room).
LAYOUTS = [f'SecretBase_{s}{i}' for s, _ in STYLES for i in range(1, 5)]
ZONES = [531, 532, 533, 534, 506, 535, 536, 537, 507, 538, 540, 541, 508, 542, 395, 445, 457, 504, 516, 517, 567, 568, 574, 584]
AREA_BASE, AREA_BEDROOM, PACK = 299, 300, 17       # free interior areas; both load prop pack 17 (a/2/2/6, a/1/7/5)
BEDROOMS = {391: ('LittlerootTown_BrendansHouse_2F', 1, 1), 393: ('LittlerootTown_MaysHouse_2F', 1, 1)}
RES_DECOR = 0x170                                  # a decoration's prop res id = RES_DECOR + its id
RES_FIXTURE = RES_DECOR + 121                      # then PC, one stone and one hole per style
RES_CURSOR = RES_FIXTURE + 1 + 6 * 2               # then the put-away cursor
MB = {k: v for k, v in ((a, int(b, 0)) for a, b in re.findall(r'#define (MB_\w+)\s+(0x[0-9A-Fa-f]+|\d+)',
                                                              open(os.path.join(RUBY, 'include', 'constants', 'metatile_behaviors.h')).read()))}
# Base tile kinds (the rules' metatile behaviours)
G_OTHER, G_NORMAL, G_WALL, G_HOLE, G_BLOCK, G_EDGE, G_CENTER = 0, 1, 2, 3, 4, 5, 6
# A decoration tile's kind: what its cell and step do
K = dict(PASS=0, SOLID=1, INTERACT=2, BALLOON=3, GLITTER=4, JUMP=5, SPIN=6, NOTE=7, DOOR=8, SLIDE=9, EDGE=10, CENTER=11,
         WALL_E=12, WALL_W=13, WALL_N=14, WALL_NE=15, WALL_NW=16, SAND=17)


def tile_kind(attr, perm):
    """(kind, layer != 0) of a decoration tile: sub_80FF1EC's collision, the behaviours' effects."""
    b, layer = attr & 0xFF, attr >> 12
    n = {v: k for k, v in MB.items()}.get(b, '')
    solid = n == 'MB_SECRET_BASE_IMPASSABLE' or (perm != 'PASS_FLOOR' and layer != 0)
    special = {'MB_SECRET_BASE_BALLOON': 'BALLOON', 'MB_SECRET_BASE_GLITTER_MAT': 'GLITTER', 'MB_SECRET_BASE_JUMP_MAT': 'JUMP',
               'MB_SECRET_BASE_SPIN_MAT': 'SPIN', 'MB_SECRET_BASE_MUSIC_NOTE_MAT': 'NOTE',
               'MB_SECRET_BASE_BREAKABLE_DOOR': 'DOOR', 'MB_SLIDE_SOUTH': 'SLIDE', 'MB_IMPASSABLE_EAST': 'WALL_E',
               'MB_IMPASSABLE_WEST': 'WALL_W', 'MB_IMPASSABLE_NORTH': 'WALL_N', 'MB_IMPASSABLE_NORTHEAST': 'WALL_NE',
               'MB_IMPASSABLE_NORTHWEST': 'WALL_NW', 'MB_IMPASSABLE_WEST_AND_EAST': 'WALL_E',
               'MB_SECRET_BASE_SHIELD_OR_TOY_TV': 'INTERACT', 'MB_SECRET_BASE_SAND_ORNAMENT': 'SAND',
               'MB_SECRET_BASE_LARGE_MAT_EDGE': 'EDGE', 'MB_LARGE_MAT_CENTER': 'CENTER'}.get(n)
    return (special or ('SOLID' if solid else 'PASS')), layer != 0, solid


def grid(mapname):
    """The rules' kinds of a Gen 3 map, row by row, and its size."""
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from gba import Repo, MetatileRenderer
    r = Repo(RUBY)
    mj = r.map_json(mapname)
    g, l = r.layout_grid(mj['layout'])
    mr = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
    H, W = g.shape
    rows, fix = [], []
    for y in range(H):
        row = []
        for x in range(W):
            m = int(g[y, x]) & 0x3FF
            b = mr.behavior(m)
            n = {v: k for k, v in MB.items()}.get(b, '')
            row.append({'MB_NORMAL': G_NORMAL, 'MB_SECRET_BASE_NORTH_WALL': G_WALL, 'MB_SECRET_BASE_HOLE': G_HOLE,
                        'MB_BLOCK_DECORATION': G_BLOCK, 'MB_SECRET_BASE_LARGE_MAT_EDGE': G_EDGE,
                        'MB_LARGE_MAT_CENTER': G_CENTER}.get(n, G_OTHER))
            if n == 'MB_SECRET_BASE_PC': fix.append(('pc', x, y))
            if n == 'MB_BLOCK_DECORATION': fix.append(('stone', x, y))
            if n == 'MB_SECRET_BASE_HOLE': fix.append(('hole', x, y))
        rows.append(row)
    return dict(w=W, h=H, rows=rows, fix=fix, warp=(mj['warp_events'][0]['x'], mj['warp_events'][0]['y']) if mj['warp_events'] else None,
                bg=mj.get('bg_events'))


def spots():
    """The 75 spots: map, tile, secret_base_id (layout * 10 + location), as data/maps/*/map.json."""
    out = []
    for name in sorted(os.listdir(os.path.join(RUBY, 'data', 'maps'))):
        p = os.path.join(RUBY, 'data', 'maps', name, 'map.json')
        if not os.path.exists(p): continue
        for b in (json.load(open(p)).get('bg_events') or []):
            if b.get('type') == 'secret_base':
                out.append(dict(map=name, x=b['x'], y=b['y'], id=SECRET_ID(b['secret_base_id'])))
    assert len(out) == 75
    return out


def SECRET_ID(name):
    """SECRET_BASE_RED_CAVE1_1 -> gCurrentSecretBaseId's number (layout index * 10 + location)."""
    c = constants(os.path.join(RUBY, 'include', 'constants', 'secret_bases.h'))
    return c[name]


def spot_type(n):
    """Gen 3's VAR_0x8007 kind by layout index (gUnknown_083D1358's rows): 1-4 caves, 5 tree, 6 shrub."""
    return n // 4 + 1 if n // 4 < 4 else (5 if n // 4 == 4 else 6)


def _spot_render(mr, m):
    """A metatile as a picture standing on the world's own tile: colour 0 of every layer transparent."""
    src = mr.p['mt'] if m < 512 else mr.s['mt']
    e_ = src[m if m < 512 else m - 512]
    out = np.zeros((16, 16, 4), np.uint8)
    for layer in range(2):
        for q in range(4):
            e = int(e_[layer * 4 + q])
            t_, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, (e >> 12) & 0xF
            px = mr.tile(t_)
            if hf: px = px[:, ::-1]
            if vf: px = px[::-1, :]
            mask = px != 0
            oy, ox = (q // 2) * 8, (q % 2) * 8
            reg = out[oy:oy + 8, ox:ox + 8]
            reg[mask, :3] = mr.pals[pal][px][mask]
            reg[mask, 3] = 255
    return out


def spot_kinds():
    """The spots' pictures: one kind per different pair of Gen 3 metatile pictures (closed, open).
    [(spot index -> kind)], [kind -> (closed RGBA, open RGBA)]."""
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from gba import Repo, MetatileRenderer
    r = Repo(RUBY)
    pairs = {0x26: 0x36, 0x27: 0x37, 0x1A0: 0x1A1, 0x1A8: 0x1A9, 0x1B0: 0x1B1, 0x208: 0x210, 0x271: 0x278}
    kinds, out, pics = {}, [], []
    for s in spots():
        mj = r.map_json(s['map'])
        g, l = r.layout_grid(mj['layout'])
        mr = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
        m = int(g[s['y'], s['x']]) & 0x3FF
        c, o = _spot_render(mr, m), _spot_render(mr, pairs[m])
        k = (c.tobytes(), o.tobytes())
        if k not in kinds:
            kinds[k] = len(pics)
            pics.append((c, o, m))
        out.append(kinds[k])
    return out, pics


def shops():
    """[(name, bp, [decoration ids], [bp prices])], every decoration shop of the three versions. The scripts name them."""
    def lst(decomp, map_, label):
        items = constants(os.path.join(decomp, 'include', 'constants', 'items.h'))
        t = open(os.path.join(decomp, 'data', 'maps', map_, 'scripts.inc')).read()
        i = re.search(r'^' + label + r':+', t, re.M).start()
        body = t[i:]
        out = []
        for line in body.split('\n')[1:]:
            m = re.match(r'\s*\.2byte (\w+)', line)
            if not m: break                     # (pokemartlistend, or the list's end)
            v = m.group(1)
            n = DECOR_IDS.get(v, items.get(v))
            if n is None: n = int(v, 0)
            if n == 0: break
            out.append(n)
        assert out, label
        return out
    SR = RUBY
    E_ = EMERALD
    def bp(name):
        t = open(os.path.join(E_, 'src', 'data', 'battle_frontier', 'battle_frontier_exchange_corner.h')).read()
        items = re.search(r'sFrontierExchangeCorner_' + name + r'\[\]\s*=\s*\{(.*?)\};', t, re.S).group(1)
        return [DECOR_IDS[v] for v in re.findall(r'DECOR_\w+', items)]
    def bp_prices(name):
        t = open(os.path.join(E_, 'data', 'maps', 'BattleFrontier_ExchangeServiceCorner', 'scripts.inc')).read()
        return t
    rows = [
        ('sr_slateport_dolls', False, lst(SR, 'SlateportCity', 'SlateportCity_PokemartDecor1_Dolls')),
        ('sr_slateport_1', False, lst(SR, 'SlateportCity', 'SlateportCity_PokemartDecor1')),
        ('sr_slateport_2', False, lst(SR, 'SlateportCity', 'SlateportCity_PokemartDecor2')),
        ('sr_fortree_desks', False, lst(SR, 'FortreeCity_DecorationShop', 'FortreeCity_DecorationShop_PokemartDecor_Desks')),
        ('sr_fortree_chairs', False, lst(SR, 'FortreeCity_DecorationShop', 'FortreeCity_DecorationShop_PokemartDecor_Chairs')),
        ('sr_flower', False, lst(SR, 'Route104_PrettyPetalFlowerShop', 'Route104_PrettyPetalFlowerShop_Items')),
        ('sr_5f_far_left', False, lst(SR, 'LilycoveCity_DepartmentStore_5F', 'LilycoveCity_DepartmentStore_5F_Pokemart_StatBoostersAndStones')),
        ('sr_5f_mid_left', False, lst(SR, 'LilycoveCity_DepartmentStore_5F', 'LilycoveCity_DepartmentStore_5F_Pokemart_Treasures')),
        ('sr_5f_mid_right', False, lst(SR, 'LilycoveCity_DepartmentStore_5F', 'LilycoveCity_DepartmentStore_5F_Pokemart_Vitamins')),
        ('sr_5f_far_right', False, lst(SR, 'LilycoveCity_DepartmentStore_5F', 'LilycoveCity_DepartmentStore_5F_Pokemart_VitaminsAndShards')),
        ('sr_rooftop', False, lst(SR, 'LilycoveCity_DepartmentStoreRooftop', 'LilycoveCity_DepartmentStoreRooftop_PokemartDecor_ClearOutSale')),
        ('em_slateport_dolls', False, lst(E_, 'SlateportCity', 'SlateportCity_PokemartDecor_Dolls')),
        ('em_slateport', False, lst(E_, 'SlateportCity', 'SlateportCity_PokemartDecor')),
        ('em_fortree_desks', False, lst(E_, 'FortreeCity_DecorationShop', 'FortreeCity_DecorationShop_PokemartDecor_Desks')),
        ('em_fortree_chairs', False, lst(E_, 'FortreeCity_DecorationShop', 'FortreeCity_DecorationShop_PokemartDecor_Chairs')),
        ('em_flower', False, lst(E_, 'Route104_PrettyPetalFlowerShop', 'Route104_PrettyPetalFlowerShop_Pokemart_Plants')),
        ('em_5f_dolls', False, lst(E_, 'LilycoveCity_DepartmentStore_5F', 'LilycoveCity_DepartmentStore_5F_Pokemart_Dolls')),
        ('em_5f_cushions', False, lst(E_, 'LilycoveCity_DepartmentStore_5F', 'LilycoveCity_DepartmentStore_5F_Pokemart_Cushions')),
        ('em_5f_posters', False, lst(E_, 'LilycoveCity_DepartmentStore_5F', 'LilycoveCity_DepartmentStore_5F_Pokemart_Posters')),
        ('em_5f_mats', False, lst(E_, 'LilycoveCity_DepartmentStore_5F', 'LilycoveCity_DepartmentStore_5F_Pokemart_Mats')),
        ('em_rooftop', False, lst(E_, 'LilycoveCity_DepartmentStoreRooftop', 'LilycoveCity_DepartmentStoreRooftop_PokemartDecor_ClearOutSale')),
        ('em_exchange_1', True, bp('Decor1')),
        ('em_exchange_2', True, bp('Decor2')),
    ]
    return rows


ENTRY = [(1, 3), (5, 9), (1, 3), (7, 13), (2, 3), (9, 2), (13, 4), (1, 2), (1, 3), (1, 2), (3, 15), (3, 14), (9, 3), (8, 7), (3, 6),
         (5, 9), (2, 3), (5, 6), (15, 3), (4, 10), (3, 3), (1, 2), (7, 8), (9, 6)]        # gUnknown_083D1374: PC-front tiles


def entry_table():
    """gUnknown_083D1374's rows are by layout: read them back and check our copy."""
    t = open(os.path.join(RUBY, 'src', 'secret_base.c')).read()
    m = re.search(r'gUnknown_083D1374\[\] = \{(.*?)\};', t, re.S)
    rows = re.findall(r'MAP_NUM\(MAP_SECRET_BASE_(\w+)\),\s*0,\s*(\d+),\s*(\d+)', m.group(1))
    assert [(int(a), int(b)) for _, a, b in rows] == ENTRY
    return rows


def header():
    """include/hoennb2/secret_base_data.h, the same for the three versions."""
    ds = decorations()
    ts = TS()
    tiles, recs = [], []
    for d in ds:
        start = len(tiles)
        if d['tiles']:
            for m in d['tiles']:
                k, lay, solid = tile_kind(ts.attr(0x200 + m), d['perm'])
                tiles.append(K[k] | (0x20 if lay else 0) | (0x40 if solid else 0) | (0x80 if m == 0x8C else 0))
        recs.append((d['price'], d['w'], d['h'], PERMS.index(d['perm']), CATS.index(d['cat']), start))
    entry_table()
    rows = [f'SB_LAYOUTS {len(LAYOUTS)}', 'SB_SPOTS 75']
    L = ['// Generated by HoennB2 b2tools/secret_base_data.py from pokeruby (checked equal in pokeemerald). Do not edit.',
         '#ifndef POKEBW2_HOENNB2_SECRET_BASE_DATA_H', '#define POKEBW2_HOENNB2_SECRET_BASE_DATA_H', '',
         f'#define SB_PACK {PACK}', f'#define SB_RES_DECOR {RES_DECOR:#x}', f'#define SB_RES_FIXTURE {RES_FIXTURE:#x}',
         f'#define SB_RES_CURSOR {RES_CURSOR:#x}', f'#define SB_LAYOUTS {len(LAYOUTS)}', '#define SB_SPOTS 75']
    gd, offs, fixes, rooms = [], [], [], []
    all_maps = [(n, z, 0, 0) for n, z in zip(LAYOUTS, ZONES)] + [(m, z, ox, oz) for z, (m, ox, oz) in BEDROOMS.items()]
    L.append(f'#define SB_ROOMS {len(all_maps)}')
    L += ['', '#endif', '']
    for i, (n, z, ox, oz) in enumerate(all_maps):
        g = grid(n)
        offs.append(len(gd))
        for r_ in g['rows']: gd += r_
        fx = []
        if i < len(LAYOUTS):
            style = i // 4
            for kind, x, y in g['fix']:
                fx.append((RES_FIXTURE + (0 if kind == 'pc' else 1 + style * 2 + (0 if kind == 'stone' else 1)), x, y))
        rooms.append((z, g['w'], g['h'], ox, oz, offs[-1], len(fixes), len(fx)))
        fixes += fx
    kinds, _ = spot_kinds()
    sp = spots()
    L += ['#ifdef SB_DATA_DEFINE', 'const SBDecor gSBDecor[121] = {']
    L += [f'    {{ {r[0]}, {r[1]}, {r[2]}, {r[3]}, {r[4]}, {r[5]} }}, // {i} {ds[i]["name"]}' for i, r in enumerate(recs)]
    L += ['};', '', f'const u8 gSBDecorTiles[{len(tiles)}] = {{']
    L += ['    ' + ', '.join(f'{v:#04x}' for v in tiles[i:i + 16]) + ',' for i in range(0, len(tiles), 16)]
    L += ['};', '', 'const SBRoom gSBRooms[SB_ROOMS] = {']
    L += [f'    {{ {r[0]}, {r[1]}, {r[2]}, {r[3]}, {r[4]}, {r[5]}, {r[6]}, {r[7]} }}, // {all_maps[i][0]}' for i, r in enumerate(rooms)]
    L += ['};', '', f'const SBFixture gSBFixtures[{max(1, len(fixes))}] = {{']
    L += [f'    {{ {r:#x}, {x}, {y} }},' for r, x, y in fixes]
    L += ['};', '', '// The tile in front of the PC (gUnknown_083D1374), the mat (the map\'s warp)', 'static const u8 gSBEntry[SB_LAYOUTS][4] = {']
    L += [f'    {{ {a}, {b}, {grid(n)["warp"][0]}, {grid(n)["warp"][1]} }},' for (a, b), n in zip(ENTRY, LAYOUTS)]
    L += ['};', '', 'static const u8 sSBSpotKind[SB_SPOTS] = {', '    ' + ', '.join(map(str, kinds)), '};', '#endif', '']
    L += ['#ifdef SB_DATA_GRID', f'static const u8 sSBGrid[{len(gd)}] = {{']
    L += ['    ' + ','.join(str(v) for v in gd[i:i + 40]) + ',' for i in range(0, len(gd), 40)]
    L += ['};', '', 'static const u8 sSBSpotIds[SB_SPOTS] = {', '    ' + ', '.join(str(s['id']) for s in sp), '};', '']
    # the shops
    sh = shops()
    items, prices, first = [], [], []
    bp_ = _bp_prices()
    for name, isbp, lst_ in sh:
        first.append(len(items))
        items += lst_
        prices += [bp_[i] if isbp else 0 for i in lst_]
    L += [f'static const u8 sSBShopItems[{len(items)}] = {{', '    ' + ', '.join(map(str, items)), '};', '',
          f'static const u16 sSBShopBP[{len(items)}] = {{', '    ' + ', '.join(map(str, prices)), '};', '',
          'typedef struct { u16 first; u8 count; u8 bp; } SBShop;', f'static const SBShop sSBShops[{len(sh)}] = {{']
    L += [f'    {{ {first[i]}, {len(s[2])}, {1 if s[1] else 0} }}, // {i} {s[0]}' for i, s in enumerate(sh)]
    z = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))
    L += ['};', '', '// A zone of each spot\'s map, for its place name (WordSetPlaceName)', 'static const u16 sSBSpotPlace[SB_SPOTS] = {',
          '    ' + ', '.join(str(z['maps'][s['map']]['zone']) for s in sp), '};', '#endif', '']
    return '\n'.join(L)


def _bp_prices():
    """Emerald's Exchange Service Corner prices: sFrontierExchangeCorner_Decor1/2's order with data/scripts' VAR_0x8008."""
    t = open(os.path.join(EMERALD, 'data', 'maps', 'BattleFrontier_ExchangeServiceCorner', 'scripts.inc')).read()
    out = {}
    for m in re.finditer(r'setorcopyvar VAR_0x8008, (\d+)|setvar VAR_0x8008, (\d+)\s*\n\s*(?:setorcopyvar|setvar) VAR_0x8009, (DECOR_\w+)', t):
        if m.group(3): out[DECOR_IDS[m.group(3)]] = int(m.group(2))
    assert out, 'no BP prices found'
    return out


# ==== the props: Gen 3's pictures on cards =============================================================================
WALL_OUT_Y, WALL_OUT_Z = 12, 8                     # a poster's quad, off the wall's face (screenshots/secret_bases/round2/2_full_base_mid.png)
CARD_RISE = 6                                      # units a card rises per row (HoennB2_SB's doll lift has the same)
OBJ_PALS = {'OBJ_EVENT_PAL_TAG_NPC_1': 'npc_1', 'OBJ_EVENT_PAL_TAG_NPC_2': 'npc_2', 'OBJ_EVENT_PAL_TAG_NPC_3': 'npc_3',
            'OBJ_EVENT_PAL_TAG_NPC_4': 'npc_4'}


def floor_free(style_a='red_cave', style_b='blue_cave'):
    """A metatile picture with the floor left out: Gen 3 draws a decoration's backdrop in the room's own floor, so the
    pixels that differ between two styles are floor, and the base's own floor shows through there."""
    a, b = TS(style_a), TS(style_b)

    def pic(m):
        x, y = a.render(m), b.render(m)
        out = x.copy()
        out[(x != y).any(axis=2), 3] = 0
        return out
    return pic


def decoration_rgba(d):
    """RGBA picture of a decoration: its metatiles without the floor, or a doll's object picture."""
    if d['tiles']:
        pic = floor_free()
        w, h = d['w'], d['h']
        out = np.zeros((h * 16, w * 16, 4), np.uint8)
        for i, m in enumerate(d['tiles']):
            y, x = i // w, i % w
            out[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = pic(0x200 + m)
        return out
    info = doll_picture(d['obj'])
    stem = re.sub(r'(?<!^)(?=[A-Z])', '_', re.sub(r'^gObjectEventGraphicsInfo_', '', info['g'])).lower()
    for sub in ('dolls', 'cushions'):
        p = os.path.join(EMERALD, 'graphics', 'object_events', 'pics', sub, stem + '.png')
        if os.path.exists(p): break
    idx = np.array(Image.open(p))
    pal = os.path.join(EMERALD, 'graphics', 'object_events', 'palettes', OBJ_PALS[info['tag']] + '.pal')
    rows = open(pal).read().split('\n')[3:19]
    cols = np.array([[int(v) for v in l.split()] for l in rows if l.strip()], dtype=np.uint8)
    out = np.zeros(idx.shape + (4,), np.uint8)
    out[..., :3] = cols[idx & 15]
    out[..., 3] = (idx != 0) * 255
    return out


def pow2(n):
    return next(s for s in (8, 16, 32, 64, 128) if s >= n)


def card_image(rgba):
    """The picture on the top-left of a power-of-two texture, transparent around."""
    h, w = rgba.shape[:2]
    tw, th = pow2(w), pow2(h)
    out = np.zeros((th, tw, 4), np.uint8)
    out[:h, :w] = rgba
    return out, w / tw, h / th


def build_model(name, rgba, kind, w_units, h_units):
    """A prop: origin on the floor at the footprint's south edge, centred. kind: flat (on the floor), card (leaning back so
    Gen 3's picture covers its footprint from the game's camera), wall (the wall tile's face), doll (upright).
    Returns (Model, texture RGBA)."""
    sys.path.insert(0, HERE)
    from dae import Model
    tex, u1, v1 = card_image(rgba)
    x0, x1 = -w_units / 2, w_units / 2
    m = Model(name)
    if kind == 'flat':
        y0, y1, z0, z1 = 0.5, 0.5, 0, -h_units
    elif kind == 'wall':
        # Towards the camera, along its ray (screen place unchanged): the cave and hedge walls bulge through a quad on their face
        y0, y1, z0, z1 = 1 + WALL_OUT_Y, 1 + h_units + WALL_OUT_Y, WALL_OUT_Z, WALL_OUT_Z - h_units
    elif kind == 'doll':
        y0, y1, z0, z1 = 0.5, 0.5 + h_units * 0.8, -4, -4 - h_units * 0.6
    else:
        y0, y1, z0, z1 = 0.5, 0.5 + h_units / 16 * CARD_RISE, 0, -h_units
    # v = 1 at the texture's top row (dae.py's convention, models_truck's door)
    m.quad(name, [(x0, y0, z0, 0, 1 - v1), (x1, y0, z0, u1, 1 - v1), (x1, y1, z1, u1, 1), (x0, y1, z1, 0, 1)])
    return m, tex


def draw_kind(d):
    if d['perm'] == 'NA_WALL': return 'wall'
    if d['perm'] == 'SOLID_MAT': return 'doll'
    if d['cat'] == 'MAT' or d['id'] == 33: return 'flat'        # mats and the solid board lie on the floor
    return 'card'


def build_models(out):
    """out/<name>.dae, <name>.png, batch.txt, palettes.txt, props.json: all 121 decorations, the fixtures and the cursor."""
    os.makedirs(out, exist_ok=True)
    props = []

    def add(res, name, rgba, kind, w, h):
        m, tex = build_model(name, rgba, kind, w, h)
        Image.fromarray(tex).save(os.path.join(out, name + '.png'))
        m.write(os.path.join(out, name + '.dae'), wrap={name: ('CLAMP', 'CLAMP')}, double_sided=(name,))
        props.append(dict(res=res, name=name, kind=kind))
    for d in decorations():
        if d['id'] == 0: continue
        rgba = decoration_rgba(d)
        if d['tiles']:
            add(RES_DECOR + d['id'], f"sbd_{d['id']}", rgba, draw_kind(d), d['w'] * 16, d['h'] * 16)
        else:
            add(RES_DECOR + d['id'], f"sbd_{d['id']}", rgba, 'doll', rgba.shape[1], rgba.shape[0])
    sys.path.insert(0, HERE)
    pc = TS().render(0x220)
    add(RES_FIXTURE, 'sbf_pc', pc, 'card', 16, 16)
    for s, (_, st) in enumerate(STYLES):
        ts = TS(st)
        pic = floor_free(st, STYLES[(s + 1) % 6][1])
        add(RES_FIXTURE + 1 + s * 2, f'sbf_stone{s}', ts.render(0x20E, layers=(1,)), 'flat', 16, 16)
        add(RES_FIXTURE + 2 + s * 2, f'sbf_hole{s}', ts.render(0x222), 'flat', 16, 16)
    frame = np.zeros((16, 16, 4), np.uint8)
    frame[[0, 1, 14, 15], :] = (248, 88, 40, 255)
    frame[:, [0, 1, 14, 15]] = (248, 88, 40, 255)
    add(RES_CURSOR, 'sbf_cursor', frame, 'flat', 16, 16)
    with open(os.path.join(out, 'batch.txt'), 'w') as f, open(os.path.join(out, 'palettes.txt'), 'w') as g:
        for p in props:
            f.write(f"{os.path.join(out, p['name'] + '.dae')} {os.path.join(out, p['name'] + '.nsbmd')}\n")
            g.write(f"{p['name']} {p['name']}_pl\n")
    json.dump(props, open(os.path.join(out, 'props.json'), 'w'), indent=0)
    return props


def rgba_source(name, img):
    """A parsed one-texture source for nsbtx.merge from an RGBA image: 16 colours, colour 0 transparent (format 3)."""
    import struct
    a = np.array(img)
    h, w = a.shape[:2]
    opaque = a[a[..., 3] > 0][:, :3]
    pil = Image.fromarray(a[..., :3] * (a[..., 3:] > 0))
    q = pil.quantize(colors=15, dither=Image.NONE) if len(np.unique(opaque, axis=0)) > 15 else None
    colours = {}
    idx = np.zeros((h, w), np.uint8)
    if q is None:
        for y in range(h):
            for x in range(w):
                if a[y, x, 3]:
                    c = tuple(int(v) for v in a[y, x, :3])      # (numpy's u8 would lose its bits in the shifts below)
                    idx[y, x] = colours.setdefault(c, len(colours) + 1)
        pal = [(0, 0, 0)] + list(colours)
    else:
        qi = np.array(q)
        p = q.getpalette()
        pal = [(0, 0, 0)] + [tuple(p[i * 3:i * 3 + 3]) for i in range(15)]
        idx = (qi + 1) * (a[..., 3] > 0)
    pal += [(0, 0, 0)] * (16 - len(pal))
    flat = idx.flatten().tolist()
    raw = bytes((flat[i] & 15) | ((flat[i + 1] & 15) << 4) for i in range(0, w * h, 2))
    pdata = b''.join(struct.pack('<H', (c[0] >> 3) | ((c[1] >> 3) << 5) | ((c[2] >> 3) << 10)) for c in pal)
    params = (((w // 8).bit_length() - 1) << 20) | (((h // 8).bit_length() - 1) << 23) | (3 << 26) | (1 << 29)
    return dict(texdata=raw, c_data=b'', c_idx=b'', pdata=pdata, pflag=0,
                texs=[(name, (params, 0x80000000 | w | (h << 11)))], pals=[(name + '_pl', (0, 0))])


# ==== the text bank ====================================================================================================
TEXT_FILE = os.path.join(ROOT, 'src', 'text', 'script', '0436_secret_bases.txt')
DEFS_FILE = os.path.join(ROOT, 'src', 'field_scripts', 'common', 'secret_base_lines.inc')
# name: Gen 3's words (.string text, pokeruby src/strings.c and data/text); {PLAYER}, {STR_VAR_n} as in Gen 3
LINES = [
    ('CANCEL', 'CANCEL$'), ('MORE', 'MORE...$'),
    ('PRICE', 'The price is ¥{STR_VAR_3}.$'), ('PRICE_BP', 'The price is {STR_VAR_3} BP.$'),
    # spots: data/text/secret_base_trainers.inc, data/text/secret_base.inc
    ('INDENT', "There's a small indent in the wall.$"),
    ('INDENT_USE', "There's a small indent in the wall.\\pUse the SECRET POWER?$"),
    ('USED', '{STR_VAR_1} used SECRET POWER!$'),
    ('CAVERN', 'Discovered a small cavern!$'),
    ('TREE', 'If some vines drop down, this tree can\nbe climbed.$'),
    ('TREE_USE', 'If some vines drop down, this tree can\nbe climbed.\\pUse the SECRET POWER?$'),
    ('VINE', 'A thick vine dropped down!$'),
    ('SHRUB', 'If this clump of grass can be moved,\nit might be possible to go inside.$'),
    ('SHRUB_USE', 'If this clump of grass can be moved,\nit might be possible to go inside.\\pUse the SECRET POWER?$'),
    ('ENTRANCE', 'Discovered a small entrance!$'),
    ('MAKE', 'Want to make your SECRET BASE here?$'),
    ('ONLY_ONE', 'You may only make one SECRET BASE.\\pWould you like to move from the SECRET\nBASE near {STR_VAR_1}?$'),
    ('RETURNED', 'All decorations and furniture in your\nSECRET BASE will be returned to your PC.\\pIs that okay?$'),
    ('MOVED', 'Moving completed.\\pWould you like to use the SECRET POWER?$'),
    # the PC
    ('BOOT', '{PLAYER} booted up the PC.$'), ('WHAT', 'What would you like to do?$'),
    ('PC', 'PC$'), ('DECORATION', 'DECORATION$'), ('PACK_UP', 'PACK UP$'), ('TURN_OFF', 'TURN OFF$'),
    ('DECORATE', 'DECORATE$'), ('PUT_AWAY', 'PUT AWAY$'), ('TOSS', 'TOSS$'),
    ('DESC_DECORATE', 'Put out the selected decoration item.$'),
    ('DESC_PUT_AWAY', 'Store the chosen decoration in the PC.$'),
    ('DESC_TOSS', 'Throw away unwanted decorations.$'),
    ('NO_DECORS', 'There are no decorations.$'),
    ('PLACE', 'Place it here?$'), ('CANT_PLACE', "It can't be placed here.$"),
    ('CANCEL_DECORATING', 'Cancel decorating?$'), ('IN_USE', 'This is in use already.$'),
    ('NO_MORE_16', 'No more decorations can be placed.\nThe most that can be placed are 16.$'),
    ('NO_MORE_12', 'No more decorations can be placed.\nThe most that can be placed are 12.$'),
    ('CANT_ROOM', "This decoration can't be placed in\nyour own room.$"),
    ('TOSS_IN_USE', "This decoration is in use.\nIt can't be thrown away.$"),
    ('DISCARD', 'This {STR_VAR_1} will be discarded.\nIs that okay?$'),
    ('THROWN', 'The decoration item was thrown away.$'),
    ('STOP_PUT_AWAY', 'Stop putting away decorations?$'),
    ('NO_DECOR', 'There is no decoration item here.$'),
    ('RETURN', 'Return this decoration to the PC?$'),
    ('DECOR_RETURNED', 'The decoration was returned to the PC.$'),
    ('NONE_IN_USE', 'There are no decorations in use.$'),
    # decorations that answer A
    ('SHIELD_SILVER', 'A shield of SILVER that marks winning\n50 times in a row at the BATTLE TOWER.$'),
    ('SHIELD_GOLD', 'A shield of GOLD that marks winning\n100 times in a row at the BATTLE TOWER.$'),
    ('TOY_TV', 'A realistic toy TV. It could be easily\nmistaken for the real thing.$'),
    ('SEEDOT_TV', 'A toy TV shaped like a SEEDOT.\nIt looks ready to roll away on its own...$'),
    ('SKITTY_TV', 'A toy TV shaped like a SKITTY.\nIt looks ready to stroll away...$'),
    # getting one
    ('OBTAINED', 'Obtained the {STR_VAR_2}!$'),
    ('NO_ROOM', "Too bad! There's no room left for\nanother {STR_VAR_2}...$"),
    ('TRANSFERRED', 'The {STR_VAR_2} was transferred\nto the PC.$'),
    ('SHOP_SURE', "{STR_VAR_1}, is it?\nThat'll be ¥{STR_VAR_3}. Do you want it?$"),
    ('SHOP_SURE_BP', '{STR_VAR_1}, is it?\nThat will be {STR_VAR_3} BP. Do you want it?$'),
    ('SHOP_HAVE_BP', 'You have {STR_VAR_3} BP.$'),
    ('SHOP_THANKS', "Thank you! I'll send it to your\nhome PC.$"),
    ('SHOP_MONEY', "You don't have enough money.$"),
    ('SHOP_BP', "I'm sorry, but you don't have enough\nBattle Points.$"),
    ('SHOP_FULL', 'The space for {STR_VAR_1} is full.$'),
]
LINE_BASE = 371                                     # after 121 names, 121 "in use" names, 121 descriptions, 8 categories


def text_lines():
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from gen3text import convert
    def c(s):
        s = s.replace('\n', '\\n').replace(' BP', ' \x04')
        s = s.replace('{STR_VAR_1}', '{0100:0}').replace('{STR_VAR_2}', '{0100:1}').replace('{STR_VAR_3}', '{0100:2}')
        s = s.replace('{PLAYER}', '{0100:0}')
        # gen3text keeps {0100:n}? it drops codes it doesn't know: protect them
        s = s.replace('{0100:0}', '\x01').replace('{0100:1}', '\x02').replace('{0100:2}', '\x03')
        r = convert(s)
        r = r[0] if isinstance(r, tuple) else r
        return r.replace('\x01', '{0100:0}').replace('\x02', '{0100:1}').replace('\x03', '{0100:2}').replace('\x04', 'BP')
    ds = decorations()
    desc = {}
    t = open(os.path.join(EMERALD, 'src', 'data', 'decoration', 'description.h')).read()
    for m in re.finditer(r'const u8 DecorDesc_(\w+)\[\] = _\((.*?)\);', t, re.S):
        desc[m.group(1)] = ''.join(re.findall(r'"([^"]*)"', m.group(2)))
    out = [c(d['name'] + '$') for d in ds]
    out += [c(d['name'] + ' *$') for d in ds]
    out += [c(desc[d['const'].replace('DECOR_', '') if d['id'] else 'SMALL_DESK'] + '$') for d in ds]
    out += [c(n + '$') for n in CATS]
    assert len(out) == LINE_BASE - 0, len(out)
    defs = ['// Generated by b2tools/secret_base_data.py text: lines of script text 436 (src/text/script/0436_secret_bases.txt)']
    for i, (name, s) in enumerate(LINES):
        out.append(c(s))
        defs.append(f'#define SBT_{name} {LINE_BASE + i}')
    return out, defs


def write_text():
    out, defs = text_lines()
    open(TEXT_FILE, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    os.makedirs(os.path.dirname(DEFS_FILE), exist_ok=True)
    open(DEFS_FILE, 'w').write('\n'.join(defs) + '\n')
    return len(out)


# ==== the rooms ========================================================================================================
# The look of each style: Black 2's cave (the d0 look, Wellspring Cave) with Gen 3's colours as vertex colours (recipe "tint"
# of models_cave.py), a wooden floor in the tree. Textures from set 332 and 349 go into area 299's own set.
# (brown and yellow: from Gen 3's floors, 168,160,127 and 180,180,109, over Black 2's cave; they looked the same before)
TINTS = {'red': ((1.0, 0.68, 0.60), None), 'brown': ((0.91, 0.97, 1.0), None), 'blue': ((0.62, 0.82, 1.0), None),
         'yellow': ((0.89, 1.0, 0.78), None), 'tree': ((0.50, 0.92, 0.50), ('m_b08_yuka', 349, 32, (1.0, 0.86, 0.68))),
         'shrub': ((0.62, 1.0, 0.50), (None, None, None, (1.0, 0.86, 0.60)))}
LOOK_OF = dict(zip(('red_cave', 'brown_cave', 'blue_cave', 'yellow_cave', 'tree', 'shrub'), TINTS))


def write_rooms():
    """data/cave_layouts/_looks.json's sb_*, data/cave_layouts/SecretBase_*.json, data/interiors/<zone>.json,
    data/hoenn_interiors.json's entries (music, places, the room tools)."""
    sys.path.insert(0, HERE)
    import zoneheaders
    hdr, _ = zoneheaders.load(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'))
    p = os.path.join(ROOT, 'data', 'cave_layouts', '_looks.json')
    looks = json.load(open(p))
    d0 = looks['d0']
    for name, (tint, floor) in TINTS.items():
        L = {k: v for k, v in d0.items() if k not in ('_doc', 'decals', 'rock1', 'rock2')}
        L['_doc'] = 'Secret Base look (b2tools/secret_base_data.py): d0 in Gen 3 colours, area 299 (a set of its own).'
        L.update(area=AREA_BASE, pack=PACK, tiers=2, tint=dict(default=list(tint)), decals=[], arch_clear_south=True)
        if floor:
            tex, src, size, col = floor
            if tex:
                L.update(floor=tex, floor_size=size, tex_sets={tex: src})
                L['tint'][tex] = list(col)
            else:
                L['tint'][L['floor']] = list(col)
        looks['sb_' + name] = L
    json.dump(looks, open(p, 'w'), indent=1, ensure_ascii=False)
    idx_p = os.path.join(ROOT, 'data', 'hoenn_interiors.json')
    idx = json.load(open(idx_p))
    for i, (n, z) in enumerate(zip(LAYOUTS, ZONES)):
        g = grid(n)
        style = STYLES[i // 4][1]
        tiles = {f'{x},{y}': 'floor' for kind, x, y in g['fix']}
        json.dump(dict(map=n, look='sb_' + LOOK_OF[style], tiles=tiles, boulder_models=False, decals=False),
                  open(os.path.join(ROOT, 'data', 'cave_layouts', n + '.json'), 'w'), indent=1)
        pc = [(x, y) for kind, x, y in g['fix'] if kind == 'pc'][0]
        cfg = dict(zone=z, room=n, cave=True, area=AREA_BASE, dark=False,
                   header=dict(map_type=16, npc_cache=24, weather_word=0, flags=0x4883, icon_word=hdr[391]['icon_word'],
                               place_display=1, bgm0=1018, bgm1=1018, bgm2=1018, bgm3=1018, place=86,
                               encounters=0x1FFF, enc_slot=6),
                   warps=[dict(at=list(g['warp']), to=[z, 256], what="MAP_DYNAMIC: back where the player came from (GameData's next zone)")],
                   triggers=[], npcs=[], signs=[dict(script=10736, at=list(pc), dir=0, what='the PC, facing north')],
                   what=f'{n}: Secret Base (b2tools/secret_base_data.py rooms, b2tools/models_cave.py); notes/SECRET_BASES.md')
        json.dump(cfg, open(os.path.join(ROOT, 'data', 'interiors', f'{z}.json'), 'w'), indent=1)
        h = hdr[z]
        mj = json.load(open(os.path.join(RUBY, 'data', 'maps', n, 'map.json')))
        idx['rooms'][n] = dict(zone=z, status='secret_base', scripts=h['scripts'], init_scripts=h['init_scripts'], text=h['text'],
                               entities=h['entities'], area=AREA_BASE, own_matrix=False, map_id=mj['id'], map_type=mj['map_type'],
                               entered_from=None, tilesets=['gTileset_SecretBase', 'gTileset_SecretBase' + STYLES[i // 4][0]],
                               size=[g['w'], g['h']], warps=[])
    json.dump(idx, open(idx_p, 'w'), indent=1, ensure_ascii=False)
    return len(LAYOUTS)


# ==== the spots on the routes ==========================================================================================
PIC_DIR = os.path.join(ROOT, 'src', 'sprites', 'berry_planting')
FIRST_PIC = 93                                     # after berry_planting_art.py's 93 pictures: SB_CODE_PIC = 0x0E00 + 93


def write_spots():
    """data/story/secret_bases.json (one actor per spot: uid 160 + its index, code 0x0D00 + its index, the resident section
    resolves it to its closed or open picture) and the pictures, appended to the berry trees' list (they share
    a/0/4/7 records, a/0/4/8 sheets and patches/berries.py's code range)."""
    import sprites
    sp = spots()
    kinds, pics = spot_kinds()
    objs = []
    for i, s in enumerate(sp):
        objs.append(dict(kind='npc', map=s['map'], at=[s['x'], s['y']], uid=160 + i, model=0x0D00 + i, dir=1, script=10735,
                         optional=True, y_from_reader=True, note=f"Secret Base spot {i} (Gen 3 id {s['id']}, picture kind {kinds[i]})"))
    json.dump(dict(_doc='Generated by b2tools/secret_base_data.py spots: the 75 Secret Base spots of Gen 3\'s maps (the same in '
                        'pokeruby and pokeemerald). notes/SECRET_BASES.md', objects=objs),
              open(os.path.join(ROOT, 'data', 'story', 'secret_bases.json'), 'w'), indent=1)
    pj_p = os.path.join(PIC_DIR, 'pictures.json')
    pj = json.load(open(pj_p))
    pj['pictures'] = pj['pictures'][:FIRST_PIC]
    for k, (c, o, m) in enumerate(pics):
        for state, rgba in (('closed', c), ('open', o)):
            name = f'{FIRST_PIC + len(pj["pictures"]) - FIRST_PIC:03d}-sb-{k}-{state}'
            d = os.path.join(PIC_DIR, name)
            os.makedirs(d, exist_ok=True)
            colours = [(0, 0, 0)]
            frame = np.zeros((32, 32), np.uint8)
            for y in range(16):
                for x in range(16):
                    if rgba[y, x, 3]:
                        col = tuple(int(v) for v in rgba[y, x, :3])
                        if col not in colours: colours.append(col)
            q = None
            if len(colours) > 16:
                im = Image.fromarray(rgba[..., :3]).quantize(colors=15, dither=Image.NONE)
                p_ = im.getpalette()
                colours = [(0, 0, 0)] + [tuple(p_[i * 3:i * 3 + 3]) for i in range(15)]
                q = np.array(im)
            for y in range(16):
                for x in range(16):
                    if rgba[y, x, 3]:
                        v = int(q[y, x]) + 1 if q is not None else colours.index(tuple(int(u) for u in rgba[y, x, :3]))
                        frame[16 + y, 8 + x] = v       # bottom = the tile's south edge, centred (as the berry trees)
            colours += [(0, 0, 0)] * (16 - len(colours))
            pim = Image.fromarray(frame, 'P')
            pim.putpalette([v for c_ in colours for v in c_] + [0] * (768 - 48))
            pim.save(os.path.join(d, 'frame_00.png'), transparency=0)
            sprites.write_pal(os.path.join(d, 'palette.pal'), colours)
            sprites.write_json(os.path.join(d, 'sprite.json'), dict(
                kind='overworld', frames=1, size=[32, 32], controller=4, textures=['t4x4x1.0'], palette='t4x4x1', name=name, stage=0,
                sapphire=f'metatile {m:#x} (gUnknown_083D1358 {state})', made_by='b2tools/secret_base_data.py spots'))
            pj['pictures'].append(dict(folder=name, stage=0, shadow=0))
    json.dump(pj, open(pj_p, 'w'), indent=1)
    return len(objs), len(pics)


if __name__ == '__main__' and sys.argv[1] == 'spots':
    print(write_spots())


if __name__ == '__main__' and sys.argv[1] == 'rooms':
    print(write_rooms(), 'rooms')


if __name__ == '__main__' and sys.argv[1] == 'text':
    print(write_text(), 'lines')


if __name__ == '__main__' and sys.argv[1] == 'models':
    print(len(build_models(sys.argv[2])), 'props in', sys.argv[2])
if __name__ == '__main__' and sys.argv[1] == 'header':
    open(sys.argv[2], 'w').write(header())
