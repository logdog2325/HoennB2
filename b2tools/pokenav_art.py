"""The PokéNav's art, contact list and text, one set per version (notes/POKENAV.md; patches/pokenav.py puts them in the ROM,
the decomp's src/hoennb2/pokenav/pokenav_local.h reads them). The PokéNav is a mode of the touch screen: bank H, 32 KB.

Art: Gen 3's own pixels at 1:1, from external/pokeruby/graphics (Sapphire, Ruby) and external/pokeemerald/graphics
(Emerald). GBA screens are 30 x 20 tiles and the DS's 32 x 24, so a map sits two tiles lower, with its first and last rows
repeated when it is a background. One LZ file per view (menu, condition, trainers, trainer details, ribbon list, ribbon grid),
loaded when that view opens: its own tiles, a 16-line palette, up to three 32 x 24 maps (BG 5-7) and "pieces": rectangles of map
entries the C draws by itself (buttons, cursors, ribbons). Gen 3 draws those with sprites; here they are BG tiles, so the app
needs no OBJ VRAM. Palette lines: 0-8 art, 9-13 the ribbon icons, 14 the Pokémon's sprite, 15 the text.

    python3 b2tools/pokenav_art.py [OUT_DIR]     previews of every view and the sizes, for HOENN_VERSION
"""
import os, re, struct, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import version, b2decomp  # noqa: E402

RUBY = os.path.join(ROOT, 'external', 'pokeruby')
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')
MAGIC = 0x56414E50          # "PNAV"
W, H = 32, 24
CHAR_LIMIT = 0x6000 // 32                       # the BGs' maps start at 0x6000 of the 32 KB
MAP_SHIFT = 2               # rows
GRID_ART_LINES = 9          # the grid view: 0-8, then the ribbons 9-13
ART_LINES = 14              # the others: 0-13; 14 the sprite, 15 the text
RIBBON_LINE = 9
TEXT_LINE = 15
TEXT_COLORS = [(0, 0, 0), (66, 66, 66), (205, 205, 205), (250, 250, 240)]   # 0 clear, 1 text, 2 shadow, 3 the lists' panel
VIEWS = ['menu', 'condition', 'trainers', 'trainer_detail', 'ribbon_list', 'ribbon_grid']
# The tiles of each view's windows and sprite (src/hoennb2/pokenav: Pnav_NewWindow, Pnav_NewMonWindow), after its art
WINDOW_TILES = {'menu': 25 * 2, 'condition': 12 * 4 + 10 * 11 + 144, 'trainers': 15 * 16 + 8 * 2, 'trainer_detail': 28 * 17,
                'ribbon_list': 15 * 16 + 8 * 2, 'ribbon_grid': 15 * 3 + 30 * 6 + 144}
# The pieces every view has (pokenav_local.h PNAV_PIECE_*); after them the menu's buttons or the grid's ribbons
P_HEADER, P_CURSOR, P_READY, P_SPARKLE, P_GRID_CURSOR, P_REST = range(6)


def is_emerald():
    return version.OVERLAY == 'emerald'


# ---- reading Gen 3's graphics -----------------------------------------------------------------------------------------
def png_tiles(path):
    """[8 x 8 rows of colour indices] of an indexed PNG, in reading order (a greyscale PNG holds 4-bit values << 4)."""
    from PIL import Image
    im = Image.open(path)
    w, h = im.size
    px = im.load()
    shift = 4 if im.mode == 'L' else 0
    return [tuple(tuple(px[c * 8 + x, r * 8 + y] >> shift & 15 for x in range(8)) for y in range(8))
            for r in range(h // 8) for c in range(w // 8)]


def png_palette(path):
    from PIL import Image
    p = Image.open(path).getpalette()
    return [tuple(p[i * 3:i * 3 + 3]) for i in range(16)]


def jasc(path):
    v = open(path).read().split()
    return [tuple(int(x) for x in v[3 + 3 * i:6 + 3 * i]) for i in range(int(v[2]))]


def binpal(path):
    d = open(path, 'rb').read()
    return [((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3) for c in struct.unpack(f'<{len(d) // 2}H', d)]


def read_map(path):
    d = open(path, 'rb').read()
    return list(struct.unpack(f'<{len(d) // 2}H', d))


class Layer:
    """A map as rows of (tile pixels or None, h flip, v flip, 16-colour palette)."""
    def __init__(self):
        self.rows = [[None] * W for _ in range(H)]


def gba_layer(tiles, map_path, palette, offset=0, fill=False, width=32):
    """Layer of a GBA tilemap. palette: 16 colours, or {map palette number: 16 colours}; offset: the tile number of the
    PNG's first tile in that map; fill: a background, whose edge rows are repeated into the DS's extra rows."""
    m = read_map(map_path)
    out = Layer()
    for r in range(len(m) // width):
        if r + MAP_SHIFT >= H:
            break
        for c in range(min(width, W)):
            e = m[r * width + c]
            t = (e & 0x3FF) - offset
            if 0 <= t < len(tiles):
                pal = palette[e >> 12] if isinstance(palette, dict) else palette
                out.rows[r + MAP_SHIFT][c] = (tiles[t], e >> 10 & 1, e >> 11 & 1, pal)
    if fill:
        # The DS's extra rows: the background of the map's first and last rows (their first tile), and the columns a GBA
        # map leaves empty past its 30 as the last it has
        last = max(r for r in range(H) if any(out.rows[r]))
        for r in range(MAP_SHIFT):
            out.rows[r] = [out.rows[MAP_SHIFT][0]] * W
        for r in range(last + 1, H):
            out.rows[r] = [out.rows[last][0]] * W
        blank = lambda cell: cell is None or not any(any(p) for p in cell[0])
        for r in range(H):
            for c in range(30, W):
                if blank(out.rows[r][c]):
                    out.rows[r][c] = out.rows[r][29]
    return out


def nine_slice(src, x0, y0, x1, y1, dx0, dy0, dx1, dy1, clear_outside=False):
    """A box of Gen 3's art (its corners, edges and middle, tiles x0..x1, y0..y1 of src) at another size.
    clear_outside: the colour of its corners' outermost pixel becomes clear on the edge tiles (a box that sits half a tile
    inside its tiles on a background of another colour)."""
    out = Layer()
    outer = src.rows[y0][x0][0][0][0] if clear_outside else None
    for r in range(dy0, dy1 + 1):
        sr = y0 if r == dy0 else y1 if r == dy1 else y0 + 1
        for c in range(dx0, dx1 + 1):
            sc = x0 if c == dx0 else x1 if c == dx1 else x0 + 1
            cell = src.rows[sr][sc]
            if clear_outside and cell and (r in (dy0, dy1) or c in (dx0, dx1)):
                t = tuple(tuple(0 if v == outer else v for v in row) for row in cell[0])
                cell = (t,) + cell[1:]
            out.rows[r][c] = cell
    return out


def erase(layer, x0, y0, x1, y1, cell):
    for r in range(y0, y1 + 1):
        for c in range(x0, x1 + 1):
            layer.rows[r][c] = cell


def bounds(layer):
    """(x0, y0, x1, y1) of what a layer holds."""
    cells = [(c, r) for r in range(H) for c in range(W) if layer.rows[r][c] and any(any(p) for p in layer.rows[r][c][0])]
    return min(c for c, _ in cells), min(r for _, r in cells), max(c for c, _ in cells), max(r for _, r in cells)


def piece_of(tiles, palette, width, height, first=0, stride=None):
    """A piece: rows of (tile, 0, 0, palette) of `height` rows of `width` tiles, from tile `first` of a sheet whose rows
    are `stride` tiles apart (default: consecutive)."""
    stride = stride or width
    return [[(tiles[first + r * stride + c], 0, 0, palette) for c in range(width)] for r in range(height)]


def button_piece(path):
    """A menu button: Gen 3's four 32 x 16 sprites, one after the other: 16 x 2 tiles."""
    t = png_tiles(path)
    pal = png_palette(path)
    return [[(t[s * 8 + r * 4 + c], 0, 0, pal) for s in range(4) for c in range(4)] for r in range(2)]


def header_piece(path):
    """A left header, 64 x 64 in Emerald: two 64 x 32 sprites side by side. pokeruby's are 64 x 48: 64 x 32 and two 32 x 16."""
    t = png_tiles(path)
    pal = png_palette(path)
    if len(t) == 64:
        return [[(t[r * 8 + c], 0, 0, pal) for c in range(8)] + [(t[32 + r * 8 + c], 0, 0, pal) for c in range(8)]
                for r in range(4)]
    return _ruby_header(t, pal)


def _ruby_header(t, pal):
    """pokeruby's header: a 64 x 32 banner whose text goes on in two 32 x 16 sprites: the second holds the top of the last
    letters, the first the bottom 3 rows of them (their sprites overlap by pixels, not tiles). BG tiles can't, so those
    letters are put together on the banner's own colours, 32 pixels longer, and cut into tiles again."""
    px = [[0] * 128 for _ in range(32)]
    sheet = lambda i, x, y: t[i][y][x]                                  # tile i, pixel x, y
    for y in range(32):
        for x in range(64):
            px[y][x] = sheet(y // 8 * 8 + x // 8, x % 8, y % 8)
    plain = [px[y][3] for y in range(32)]                               # a column of the banner with no letter on it
    letters = {v for y in range(32) for v in px[y][:64]} - set(plain)   # the letters' colours
    top = [[sheet(32 + 4 + y // 8 * 8 + x // 8, x % 8, y % 8) for x in range(32)] for y in range(16)]
    low = [[sheet(32 + y // 8 * 8 + x // 8, x % 8, y % 8) for x in range(32)] for y in range(16)]
    rows = lambda img: [y for y in range(16) if any(v in letters for v in img[y])]
    first = next(y for y in range(32) if any(v in letters for v in px[y][:64]))
    cols = [x for x in range(32) if any(v in letters for y in range(16) for v in [top[y][x]])] if rows(top) else []
    end = 64 + (max(cols) + 3 if cols else 0)
    for x in range(64, end + 2):
        for y in range(32):
            px[y][x] = plain[y]
    for x in (end, end + 1):                                            # the banner's end, in its shadow's colour
        for y in range(32):
            if plain[y]:
                px[y][x] = plain[max(y for y in range(32) if plain[y])]
    if rows(top):
        ta = rows(top)[0]
        for y in rows(top):
            for x in range(32):
                if top[y][x] in letters:
                    px[first + y - ta][64 + x] = top[y][x]
        lows = rows(low)
        y0 = first + len(rows(top))
        for k, y in enumerate(lows[:len(lows)]):
            for x in range(32):
                if low[y][x] in letters:
                    px[y0 + k][64 + x] = low[y][x]
    tiles = [tuple(tuple(px[r * 8 + y][c * 8 + x] for x in range(8)) for y in range(8)) for r in range(4) for c in range(16)]
    return [[(tiles[r * 16 + c], 0, 0, pal) for c in range(16)] for r in range(4)]


def ribbon_pieces():
    """(the 12 small icons: a half mirrored, 2 x 2 tiles; the 12 big ones, 4 x 4; the 5 ribbon palettes, Cool to Tough)."""
    if is_emerald():
        g = os.path.join(EMERALD, 'graphics', 'pokenav', 'ribbons')
        small, big = png_tiles(os.path.join(g, 'icons.png')), png_tiles(os.path.join(g, 'icons_big.png'))
        pals = [jasc(os.path.join(g, f'icons{i}.pal')) for i in range(1, 6)]
    else:
        g = os.path.join(RUBY, 'graphics', 'misc')
        small, big = png_tiles(os.path.join(g, 'ribbons_half.png')), png_tiles(os.path.join(g, 'ribbons_full.png'))
        pals = [jasc(os.path.join(g, f'ribbons_{n}.pal')) for n in 'cool beauty cute smart tough'.split()]
    p0 = pals[0]
    sm = [[[(small[i * 2 + r], 0, 0, p0), (small[i * 2 + r], 1, 0, p0)] for r in range(2)] for i in range(12)]
    if is_emerald():
        bg = [piece_of(big, p0, 4, 4, first=i * 16) for i in range(12)]
    else:                                                       # pokeruby's: the left half, 16 x 32 an icon, mirrored
        bg = [[[(big[i * 8 + r * 2], 0, 0, p0), (big[i * 8 + r * 2 + 1], 0, 0, p0),
                (big[i * 8 + r * 2 + 1], 1, 0, p0), (big[i * 8 + r * 2], 1, 0, p0)] for r in range(4)] for i in range(12)]
    return sm, bg, pals


def gen3_ribbon_table():
    """[(icon, palette)] of Gen 3's 32 ribbons: champion, the 20 contest ribbons, winning, victory, artist, effort, the 7
    gift ribbons (pokeruby gPokenavRibbonsIconGfx; pokeemerald sRibbonGfxData has the same)."""
    if is_emerald():
        t = open(os.path.join(EMERALD, 'src', 'pokenav_ribbons_summary.c')).read()
        names = re.findall(r'^\s+(RIBBONGFX_\w+),?\s*$', t, re.M)
        rows = re.findall(r'\[\w+_RIBBON\w*\]\s*=\s*\{\s*(RIBBONGFX_\w+),\s*TO_PAL_OFFSET\(PALTAG_RIBBON_ICONS_(\d)\)', t)
        out = [(names.index(g), int(p) - 1) for g, p in rows]
    else:
        t = open(os.path.join(RUBY, 'src', 'pokenav_before.c')).read()
        body = t[t.index('gPokenavRibbonsIconGfx[][2]'):]
        body = body[:body.index('};')]
        out = [(int(a), int(b)) for a, b in re.findall(r'\{(\d+), (\d+)\}', body)]
    assert len(out) == 32, len(out)
    return out


def black2_ribbon_icons():
    """[(icon, palette line)] of Black 2's 80 ribbons, in src/ov207/ribbon.c's order: the Gen 3 ones their own picture, Gen
    4's contest ribbons the picture of the same rank and category, the others (never given in Hoenn) the first gift picture."""
    g3 = gen3_ribbon_table()
    idx = {0: 0}                                                      # Champion
    for i in range(20):
        idx[2 + i] = 1 + i                                            # the contest ribbons
        idx[22 + i] = 1 + i                                           # Gen 4's
    idx.update({42: 21, 43: 22, 50: 23, 51: 24, 76: 25, 77: 26, 78: 27, 65: 28, 66: 29, 67: 30, 68: 31})
    return [(g3[idx.get(i, 25)][0], RIBBON_LINE + g3[idx.get(i, 25)][1]) for i in range(80)]


# ---- the views --------------------------------------------------------------------------------------------------------
def views():
    """{view: dict(top=[front, mid, back], bottom=[front, mid, back], pieces=[...])}"""
    sm, big, ribbon_pals = ribbon_pieces()
    if is_emerald():
        g = os.path.join(EMERALD, 'graphics', 'pokenav')
        p = lambda *a: os.path.join(g, *a)
        dots = gba_layer(png_tiles(p('bg_dots.png')), p('bg_dots.bin'), png_palette(p('bg_dots.png')), fill=True)
        device = gba_layer(png_tiles(p('device_outline.png')), p('device_outline_map.bin'), png_palette(p('device_outline.png')))
        band = gba_layer(png_tiles(p('header.png')), p('header.bin'), png_palette(p('header.png')))
        message = gba_layer(png_tiles(p('message.png')), p('message.bin'), png_palette(p('message.png')))
        graph = gba_layer(png_tiles(p('condition', 'graph.png')), p('condition', 'graph.bin'),
                          png_palette(p('condition', 'graph.png')), fill=True)
        results = gba_layer(png_tiles(p('condition', 'search_results.png')), p('condition', 'search_results.bin'),
                            png_palette(p('condition', 'search_results.png')), fill=True)
        ribbon_list = gba_layer(png_tiles(p('ribbons', 'list_bg.png')), p('ribbons', 'list_bg.bin'),
                                png_palette(p('ribbons', 'list_bg.png')), fill=True)
        grid = gba_layer(png_tiles(p('ribbons', 'summary_bg.png')), p('ribbons', 'summary_bg.bin'),
                         png_palette(p('ribbons', 'summary_bg.png')), fill=True)
        contacts = gba_layer(png_tiles(p('match_call', 'ui.png')), p('match_call', 'ui.bin'),
                             png_palette(p('match_call', 'ui.png')), offset=128, fill=True)
        box_src, box, clear = message, (2, 18, 27, 21), False
        hdr = lambda n: header_piece(p('left_headers', n + '.png'))
        h_menu, h_cond, h_tr, h_rib = hdr('main_menu'), hdr('condition'), hdr('match_call'), hdr('ribbons')
        buttons = [button_piece(p('options', n + '.png')) for n in 'hoenn_map condition match_call ribbons switch_off'.split()]
        ball = png_tiles(p('condition', 'pokeball.png'))
        ball = piece_of(ball, png_palette(p('condition', 'pokeball.png')), 2, 2)
        ready_t = png_tiles(p('match_call', 'pokeball.png'))
        ready = piece_of(ready_t, png_palette(p('match_call', 'pokeball.png')), 1, 2)
        spark_path, cursor_path = p('condition', 'sparkle.png'), p('region_map', 'cursor_small.png')
        polygon = jasc(p('condition', 'graph_data.pal'))[1]
    else:
        g = os.path.join(RUBY, 'graphics', 'pokenav')
        u = os.path.join(RUBY, 'graphics', 'unknown')
        p = lambda *a: os.path.join(g, *a)
        bg_tiles = png_tiles(p('83E005C.png')) + png_tiles(p('outline.png'))     # VRAM + 0x8000: this tile, then the outline
        dots = gba_layer(bg_tiles, p('83E007C.bin'), {3: jasc(p('83E003C.pal'))}, fill=True)
        device = gba_layer(bg_tiles, p('outline_map.bin'), {4: png_palette(p('outline.png'))})
        band = Layer()
        view_tiles = png_tiles(p('ribbon_view.png'))
        view_pal = binpal(p('ribbon_view.pal.bin'))
        grid = gba_layer(view_tiles, os.path.join(u, 'unknown_E9FBA0.bin'), view_pal, offset=-1 + 1, fill=True)
        graph = gba_layer(png_tiles(p('condition_view.png')), p('condition_screen.bin'),
                          png_palette(p('condition_view.png')), offset=640, fill=True)
        results = gba_layer(png_tiles(p('condition_search2.png')), os.path.join(u, 'unknown_E9FC64.bin'),
                            png_palette(p('condition_search2.png')), fill=True)
        ribbon_list = contacts = results
        box_src, box, clear = grid, (11, 14, 28, 19), True                       # the summary's cream box (+ the 2-row shift)
        message = nine_slice(box_src, *box, 2, 18, 29, 21, clear)
        hdr = lambda n: header_piece(p(n + '.png'))
        h_menu, h_tr, h_rib = hdr('mainmenu'), hdr('trainereyes'), hdr('ribbons')
        h_cond = header_piece(p('condition_menu_header.png'))
        buttons = [button_piece(p(n + '.png')) for n in 'menu_hoennmap menu_condition menu_eyes menu_ribbons menu_off'.split()]
        ball = piece_of(png_tiles(p('pokeball.png')), png_palette(p('pokeball.png')), 2, 2)
        ready = []                                                               # no rematches in Sapphire and Ruby
        spark_path, cursor_path = p('sparkle.png'), p('cursor_small.png')
        polygon = jasc(p('83E0254.pal'))[1]        # the graph's own line (gUnknown_083E0254, loaded at 0x30)
    spark = piece_of(png_tiles(spark_path), png_palette(spark_path), 2, 2, first=3 * 4)
    frame = piece_of(png_tiles(cursor_path), png_palette(cursor_path), 2, 2)
    detail_box = nine_slice(box_src, *box, 1, 3, 30, 21, clear)
    ribbon_box = nine_slice(box_src, *box, 0, 15, 31, 22, clear)   # (Black 2's longest description: 44 characters)
    # The grid: Gen 3's frame without its panel and box, whose places the sprite and the wider box take
    back = grid.rows[2][0]
    erase(grid, 0, 5, 10, 23, back)
    erase(grid, 0, 14, 31, 23, back)
    common = lambda header=None, cursor=None, rdy=None, sparkle=None, grid_cursor=None: [header, cursor, rdy, sparkle, grid_cursor]
    return polygon, ribbon_pals, {
        # (+ the DexNav's button, the sixth, b2tools/dexnav_art.py; the C shows it once the player has the DexNav)
        'menu': dict(layers=[message, device, dots], pieces=common(h_menu) + buttons + [_dexnav_button()]),
        'condition': dict(layers=[None, None, graph], pieces=common(h_cond, None, None, spark)),
        'trainers': dict(layers=[None, None, contacts], pieces=common(h_tr, ball, ready)),
        'trainer_detail': dict(layers=[detail_box, device, dots], pieces=common()),
        'ribbon_list': dict(layers=[None, None, ribbon_list], pieces=common(h_rib, ball)),
        'ribbon_grid': dict(layers=[ribbon_box, None, grid], pieces=common(h_rib, None, None, None, frame) + sm + big),
    }


def _dexnav_button():
    import dexnav_art
    return dexnav_art.pokenav_menu_button()


class Packer:
    """The tile sheet of all views (tile 0 blank, a tile and its flips share a character), and each view's palette lines."""
    def __init__(self):
        self.tiles, self.index = [], {}
        self.add(tuple((0,) * 8 for _ in range(8)))

    def add(self, t):
        for hf, vf in ((0, 0), (1, 0), (0, 1), (1, 1)):
            f = tuple(tuple(row[::-1]) if hf else row for row in (t[::-1] if vf else t))
            if f in self.index:
                return self.index[f], hf, vf
        self.index[t] = len(self.tiles)
        self.tiles.append(t)
        return self.index[t], 0, 0

    def blob(self):
        out = bytearray()
        for t in self.tiles:
            for row in t:
                for x in range(0, 8, 2):
                    out.append(row[x] | row[x + 1] << 4)
        return bytes(out)


def _entry(packer, lines, cell, limit):
    if cell is None or not any(any(p) for p in cell[0]):
        return 0
    t, hf, vf = packer.add(cell[0])
    pal = tuple(tuple(c) for c in cell[3])
    if pal not in lines:
        lines[pal] = len(lines)
        assert len(lines) <= limit, f'more than {limit} palette lines in a view'
    return t | (hf ^ cell[1]) << 10 | (vf ^ cell[2]) << 11 | lines[pal] << 12


def _rgb555(c):
    return (c[0] >> 3) | (c[1] >> 3) << 5 | (c[2] >> 3) << 10


def pack():
    """{view: dict(packer, pal, maps, pieces, lines)}, each view with its own tiles."""
    polygon, ribbon_pals, vs = views()
    packed = {}
    for name in VIEWS:
        v = vs[name]
        packer = Packer()
        lines = {}
        limit = GRID_ART_LINES if name == 'ribbon_grid' else ART_LINES
        maps = []
        for layer in v['layers']:
            maps.append(None if layer is None else [_entry(packer, lines, layer.rows[r][c], limit) for r in range(H) for c in range(W)])
        pieces = []
        for pc in v['pieces']:
            pieces.append((len(pc[0]), len(pc), [_entry(packer, lines, cell, limit) for row in pc for cell in row]) if pc else (0, 0, []))
        pal = [[(0, 0, 0)] * 16 for _ in range(16)]
        for colors, line in lines.items():
            pal[line] = list(colors) + [(0, 0, 0)] * (16 - len(colors))
        if name == 'ribbon_grid':
            for i, rp in enumerate(ribbon_pals):
                pal[RIBBON_LINE + i] = list(rp) + [(0, 0, 0)] * (16 - len(rp))
        pal[TEXT_LINE] = TEXT_COLORS + [polygon] + [(0, 0, 0)] * 11
        if name != 'menu':
            pal[0][0] = TEXT_COLORS[3]                  # the backdrop: the inside of the lists' panels, behind their cursors
        assert len(packer.tiles) + WINDOW_TILES[name] <= CHAR_LIMIT, \
            f'{name}: {len(packer.tiles)} tiles + {WINDOW_TILES[name]} of windows > {CHAR_LIMIT}'
        packed[name] = dict(packer=packer, pal=pal, maps=maps, pieces=pieces, lines=len(lines))
    return packed


def contacts_and_text():
    """(contact table rows, the file's text lines, rematch ids) for this version."""
    import gen3text
    conv = lambda s: gen3text.convert(s)[0].replace('Pokénav', 'PokéNav')    # ("POKéNAV." with its full stop misses SPECIAL)
    if is_emerald():
        s = open(os.path.join(EMERALD, 'src', 'strings.c'), encoding='utf-8').read()
    else:
        s = open(os.path.join(RUBY, 'src', 'strings.c'), encoding='utf-8').read()
    def string(name):
        m = re.search(r'\b' + name + r'\[\]\s*=\s*_\("(.*?)"\);', s)
        assert m, name
        return re.sub(r'\{CLEAR 0\}', '', m.group(1))
    lines = []
    if is_emerald():
        lines += [conv(string(n)) for n in ('gText_CheckMapOfHoenn', 'gText_CheckPokemonInDetail', 'gText_CallRegisteredTrainer',
                                            'gText_CheckObtainedRibbons', 'gText_PutAwayPokenav', 'gText_NoRibbonWinners',
                                            'gText_NoTrainersRegistered')]
        lines[2] = 'Check registered Trainers.'     # (Emerald's says "Call": calling is left out, notes/POKENAV.md)
    else:
        lines += [conv(string(n)) for n in ('PCText_CheckMap', 'PCText_CheckPoke', 'PCText_CheckTrainer', 'PCText_CheckRibbons',
                                            'PCText_PutAwayNav', 'PCText_NoRibbonWin', 'PCText_NoTrainers')]
    # Black 2's own ⑭ ⑮ are the sex marks of its Pokémon names (text 90)
    lines += ['Lv.', '⑭', '⑮', 'Strategy', 'Trainer’s Pokémon', 'Self-Introduction', 'Wants a rematch!', 'Ribbons']
    assert len(lines) == 15
    names = _system_text('0382_trainer_names')
    classes = _system_text('0383_trainer_class_names')
    rows = []

    def add(flag, trainer, name, cls, place, check=None, gym=0, row=0xFF, rematch_id=0xFFFF, sex=2, has_check=True):
        base = len(lines)
        check = check or ['', '', '', '']
        lines.extend([name, cls, place] + [conv(c) for c in check])
        rows.append(dict(flag=flag, trainer=trainer, base=base, rematch_id=rematch_id, gym=gym, row=row, sex=sex,
                         check=has_check))

    place = _map_section_namer()
    if is_emerald():
        rm = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_rematch.json')))
        tr = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_trainers.json')))
        tr = tr.get('trainers', tr)
        data = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_trainer_data.json')))['trainers']
        msg = open(os.path.join(EMERALD, 'src', 'data', 'text', 'match_call_messages.h'), encoding='utf-8').read()
        flavor = {m[0]: [m[1]] for m in re.findall(r'gText_MatchCall(\w+?)_Strategy\[\]\s*=\s*_\("(.*?)"\)', msg)}
        for key in flavor:
            for part in ('Pokemon', 'Intro1', 'Intro2'):
                flavor[key].append(re.search(rf'gText_MatchCall{key}_{part}\[\]\s*=\s*_\("(.*?)"\)', msg).group(1))
        by_name = {k.rsplit('_', 1)[1].upper(): v for k, v in flavor.items()}
        by_name['NORMAN'] = by_name['DAD']
        flag = lambda n: _hoenn_h(n)
        desc = lambda n: conv(string(f'gText_{n}MatchCallDesc').replace('{PKMN}', 'POKéMON'))
        cname = lambda n: conv(string(f'gText_{n}MatchCallName'))
        rowof = {r['row']: (i, r) for i, r in enumerate(rm['rows'])}
        # Emerald's named contacts first, in sMatchCallHeaders' order. Registration flags: Emerald's FLAG_ENABLE_* are not
        # in this port (its "registered" moments are messages), so each uses the story flag of that moment
        add(flag('FLAG_RECEIVED_POKENAV'), 0xFFFF, cname('MrStone'), desc('MrStone'), 'Rustboro City', has_check=False)
        add(flag('FLAG_DELIVERED_DEVON_GOODS'), 0xFFFF, conv(string('gText_ProfBirchMatchCallName')),
            conv(string('gText_ProfBirchMatchCallDesc').replace('{PKMN}', 'POKéMON')), 'Littleroot Town',
            has_check=False)
        add(flag('FLAG_REGISTER_RIVAL_POKENAV'), 0xFFFF, 'May', desc('MayBrendan'), 'Littleroot Town', sex=0, has_check=False)
        add(flag('FLAG_REGISTER_RIVAL_POKENAV'), 0xFFFF, 'Brendan', desc('MayBrendan'), 'Littleroot Town', sex=1, has_check=False)
        i, r = rowof['REMATCH_WALLY_VR']
        add(0xFFFF, tr['TRAINER_WALLY_MAUVILLE'], 'Wally', desc('Wally'), 'Verdanturf Town', by_name['WALLY'],
            gym=r['gym'], row=i, rematch_id=r['b2_id'])
        i, r = rowof['REMATCH_NORMAN']
        add(flag('FLAG_DEFEATED_RIVAL_ROUTE_104'), 0xFFFF, cname('Norman'), desc('Norman'), 'Petalburg City', by_name['NORMAN'], gym=r['gym'], row=i,
            rematch_id=r['b2_id'])
        add(flag('FLAG_RECEIVED_POKENAV'), 0xFFFF, cname('Mom'), desc('Mom'), 'Littleroot Town', has_check=False)
        add(flag('FLAG_DELIVERED_STEVEN_LETTER'), 0xFFFF, cname('Steven'), desc('Steven'), '', has_check=False)
        add(flag('FLAG_DELIVERED_DEVON_GOODS'), 0xFFFF, cname('Scott'), desc('Scott'), '', has_check=False)
        for n, key in (('Roxanne', 'REMATCH_ROXANNE'), ('Brawly', 'REMATCH_BRAWLY'), ('Wattson', 'REMATCH_WATTSON'),
                       ('Flannery', 'REMATCH_FLANNERY'), ('Winona', 'REMATCH_WINONA'), ('TateLiza', 'REMATCH_TATE_AND_LIZA'),
                       ('Juan', 'REMATCH_JUAN')):
            i, r = rowof[key]
            who = 'TATEANDLIZA' if n == 'TateLiza' else n.upper()
            add(0xFFFF, r['b2_id'], names[r['b2_id']], desc(n), place(r['map']), by_name[who], gym=r['gym'], row=i,
                rematch_id=r['b2_id'])
        for n in ('Sidney', 'Phoebe', 'Glacia', 'Drake'):
            b = tr[f'TRAINER_{n.upper()}']
            add(0xFFFF, b, names[b], desc('EliteFour'), 'Ever Grande City', by_name[n.upper()])
        b = tr['TRAINER_WALLACE']
        add(0xFFFF, b, names[b], desc('Champion'), 'Ever Grande City', by_name['WALLACE'])
        # Then the 64 route trainers, in gRematchTable's order, which the check-page lines have too
        route = [(i, r) for i, r in enumerate(rm['rows']) if r['gym'] == 0]
        keys = list(flavor)
        assert len(route) == 64, len(route)
        for (i, r), key in zip(route, keys):
            first = r['first'].replace('TRAINER_', '').rsplit('_', 1)[0].replace('_', '')
            assert key.rsplit('_', 1)[1].upper() == first or first == 'KIRAANDDAN', (key, r['first'])
            b = r['b2_id']
            add(0xFFFF, b, names[b], classes[data[r['first']]['b2_class']], place(r['map']), flavor[key], gym=0, row=i, rematch_id=b)
    else:
        tr = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainers.json'))
        tr = tr.get('trainers', tr)
        data = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers']
        src = open(os.path.join(RUBY, 'src', 'battle_setup.c'), encoding='utf-8').read()
        body = src[src.index('const struct TrainerEyeTrainer gTrainerEyeTrainers[]'):]
        eye = re.findall(r'\{\{?\s*(TRAINER_\w+?),.*?\}?,?\s*MAP_GROUP\((\w+)\)', body[:body.index('};')], re.S)
        d = open(os.path.join(RUBY, 'src', 'data', 'text', 'trainer_eye_descriptions_en.h'), encoding='utf-8').read()
        table = re.findall(r'^\s+(TrainerEyeDescription_\w+),', d[d.index('gTrainerEyeDescriptions'):], re.M)
        assert len(eye) == 56 <= len(table), (len(eye), len(table))     # (the table goes on: its rows are unused)
        for (first, mp), key in zip(eye, table):
            m = re.search(key + r'\[\] = _\(\s*(.*?)\);', d, re.S)
            text = ''.join(re.findall(r'"(.*?)"', m.group(1)))
            parts = text.split('$')
            assert len(parts) == 4, parts
            b = tr[first]
            add(0xFFFF, b, names[b], classes[data[first]['b2_class']], place(mp), parts)
    return rows, lines


def _system_text(stem):
    """Lines (without the compressed mark) of our system text file for this version: as the game shows them."""
    num = stem[:4]
    for d in ([os.path.join(ROOT, 'src', 'text', 'system', version.OVERLAY)] if version.OVERLAY else []) + \
            [os.path.join(ROOT, 'src', 'text', 'system')]:
        p = os.path.join(d, stem + '.txt')
        if os.path.exists(p):
            return [l[2:] if l.startswith('\\c') else l for l in open(p, encoding='utf-8').read().split('\n')]
    raise SystemExit(f'no {stem} ({num})')


def _map_section_namer():
    """MAP_ROUTE118 -> "Route 118": the map's region map section, as town_map.py names places (data/maps/*/map.json)."""
    base = EMERALD if is_emerald() else RUBY
    table = {}
    root = os.path.join(base, 'data', 'maps')
    for d in os.listdir(root):
        p = os.path.join(root, d, 'map.json')
        if os.path.exists(p):
            j = json.load(open(p))
            table[j['id']] = j['region_map_section']
    words = {'ROUTE': 'Route'}

    def name(map_id):
        sec = table[map_id].replace('MAPSEC_', '')
        return ' '.join(words.get(w, w.capitalize() if not w.isdigit() else w) for w in sec.split('_'))
    return name


def _hoenn_h(name):
    m = re.search(rf'^#define {name}\s+(\w+)', open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read(), re.M)
    assert m, f'{name} is not in src/include/hoenn.h'
    return int(m.group(1), 0)


def view_bytes(view, v):
    """A view's file (pokenav_local.h PnavViewFile), before compression."""
    HEADER = 4 + 2 + 2 + 4 + 4 + 12 + 4 + 4
    body = bytearray()

    def at(data, align=4):
        while (HEADER + len(body)) % align:
            body.append(0)
        pos = HEADER + len(body)
        body.extend(data)
        return pos
    tiles = at(v['packer'].blob())
    pal = at(struct.pack('<256H', *[_rgb555(c) for line in v['pal'] for c in line]))
    maps = [at(struct.pack(f'<{W * H}H', *m)) if m else 0 for m in v['maps']]
    rows = [(at(struct.pack(f'<{len(e)}H', *e), 2) if e else 0, w, h) for w, h, e in v['pieces']]
    table = at(b''.join(struct.pack('<IBBH', o, w, h, 0) for o, w, h in rows))
    return struct.pack('<IHHII3III', MAGIC, view, len(v['packer'].tiles), tiles, pal, *maps, table, len(rows)) + bytes(body)


def data_bytes(rows, icons):
    """The contacts and the ribbons' icons (pokenav_local.h PnavData)."""
    if is_emerald():
        done = [_hoenn_h(f'VAR_EM_REMATCH_DONE_{i}') for i in range(5)]
        ids = [_hoenn_h('FLAG_DAILY_EM_REMATCHES'), _hoenn_h('FLAG_SYS_GAME_CLEAR'),
               _hoenn_h('FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON'), _hoenn_h('VAR_EM_REMATCH_LEADERS'),
               _hoenn_h('VAR_EM_REMATCH_POSTGAME')]
    else:
        done, ids = [0] * 5, [0] * 5
    HEADER = 4 + 2 + 2 + 4 + 4 + 2 * 12
    contacts = b''.join(struct.pack('<HHHHBBBB', r['flag'], r['trainer'], r['base'], r['rematch_id'] & 0xFFFF, r['gym'],
                                    r['row'], r['sex'], int(r['check'])) for r in rows)
    ribbons = b''.join(struct.pack('<BB', i, p) for i, p in icons)
    ver = {'': 0, 'ruby': 1, 'emerald': 2}[version.OVERLAY or '']
    head = struct.pack('<IHHII12H', MAGIC, ver, len(rows), HEADER, HEADER + len(contacts), _hoenn_h('FLAG_SYS_RIBBON_GET'), *ids,
                       *done, 0)
    return head + contacts + ribbons


def file_bytes():
    """([each view's file, uncompressed], the data file, the text file's lines, a report)."""
    packed = pack()
    rows, lines = contacts_and_text()
    views_out = [view_bytes(i, packed[name]) for i, name in enumerate(VIEWS)]
    data = data_bytes(rows, black2_ribbon_icons())
    return views_out, data, lines, dict(contacts=len(rows), lines=len(lines),
                                        views={n: (len(packed[n]['packer'].tiles), WINDOW_TILES[n], packed[n]['lines'], len(f))
                                               for n, f in zip(VIEWS, views_out)})


def preview(out):
    """A PNG per view: the top screen above the touch screen, with the pieces in the C's places."""
    from PIL import Image
    polygon, ribbon_pals, vs = views()

    def draw(img, layer, oy):
        px = img.load()
        for r in range(H):
            for c in range(W):
                cell = layer.rows[r][c] if isinstance(layer, Layer) else None
                if cell:
                    _cell(px, cell, c * 8, oy + r * 8)

    def _cell(px, cell, x, y):
        t, hf, vf, pal = cell
        for yy in range(8):
            row = t[7 - yy if vf else yy]
            for xx in range(8):
                v = row[7 - xx if hf else xx]
                if v and x + xx < 256:
                    px[x + xx, y + yy] = tuple(pal[v])

    def put(img, piece, x, y, oy):
        px = img.load()
        for r, row in enumerate(piece):
            for c, cell in enumerate(row):
                _cell(px, cell, (x + c) * 8, oy + (y + r) * 8)

    for name in VIEWS:
        v = vs[name]
        img = Image.new('RGB', (256, 192), (250, 250, 240) if name != 'menu' else (0, 0, 0))
        for layer in reversed(v['layers']):
            if layer is not None:
                draw(img, layer, 0)
        p = v['pieces']
        if p[P_HEADER]:
            put(img, p[P_HEADER], 0, 2, 0)
        if name == 'menu':
            for i, b in enumerate(p[P_REST:]):
                put(img, b, 15 if i == 0 else 16, 4 + i * 3, 0)
        elif name == 'ribbon_grid':
            for i in range(12):
                put(img, p[P_REST + i], 11 + i % 9 * 2, 6 + i // 9 * 2, 0)
            put(img, p[P_REST + 12 + 1], 28, 2, 0)
            put(img, p[P_GRID_CURSOR], 11, 6, 0)
        elif name == 'condition':
            put(img, p[P_SPARKLE], 4, 12, 0)
        elif p[P_CURSOR]:
            put(img, p[P_CURSOR], 13, 3, 0)
            if p[P_READY]:
                put(img, p[P_READY], 29, 3, 0)
        img.save(os.path.join(out, f'{version.OVERLAY or "sapphire"}_{name}.png'))


if __name__ == '__main__':
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    preview(d)
    print(file_bytes()[3])
