"""The DexNav's art and text (notes/DEXNAV.md; patches/dexnav.py puts them in the ROM, the decomp's
src/hoennb2/dexnav/dexnav_screen.c reads them). Omega Ruby / Alpha Sapphire's look (the user picked it 2026-11-09 from
screenshots/dexnav/mockups, variant A), drawn by us: ORAS's pictures were a style reference only, none of their pixels
are here. Black 2's font draws the labels into the art; Black 2's Pokémon and type icons are the sprites.

The touch screen (the field's, or a page of the PokéNav) has three views, each loaded whole when it shows (bank H, 32 KB:
the three BGs 4 text, 5 front, 6 art share characters 0-767, their maps above):
- AREA: the place's map (a snapshot of its Gen 3 map, b2tools/dexnav_snapshots.py, in the panel), the PokéNav Plus-like
  orange frame, the "DexNav" tab, the bottom bar with POKéNAV (the field) or the back button (the PokéNav's page); pieces
  the C draws: a "?" for a species not seen yet, the crown (every species of the place caught), the message box;
- FOUND (an icon tapped): the species in a teal ring (its icon at double size, an affine sprite), Name, Type (Black 2's
  type icons), Search Level, SEARCH and back; the stripes' palette goes from grey to orange with the search level
  (the file has the grey lines too);
- HIDDEN (while the search's Pokémon hides): its silhouette in the ring on a radar, Level, First Move, Ability,
  Potential (stars = perfect IVs) and Search Level, "!" for an egg move or a hidden ability; pieces: the stars, the "!".
Sprites (in the AREA file): the red search ring over the searched species (double size, affine) and the teal cursor of
the PokéNav's page (keys), two frames each (the icons' cell layout); their palette and the silhouettes'.

File (each view, uncompressed: the C reads it in 2 KB parts, so HEAPID_FIELD_MENU never holds it whole), little-endian,
offsets from the file's start (dexnav_screen.c DnViewFile):
  u32 magic "DNV1"; u16 tileCount; u16 lineCount; u32 tiles; u32 palette (16 lines x 16 colours, line 15 the text's);
  u32 artMap; u32 frontMap (32 x 24 each); u32 pieces (DnPiece table {u32 entries (from `pieces`), u8 w, h, x, y}, then
  the entries); u16 pieceCount; u16 piecesSize; u32 greyPalette (FOUND: the palette at search level 0, else 0);
  u16 windowChar (the windows' first character: past the art, and in AREA past every snapshot's); u16 pad;
  u32 objChars (AREA: ring then cursor, 0x400 each, else 0); u32 objPalettes (AREA: 2 OBJ palettes, else 0)

    python3 b2tools/dexnav_art.py [OUT_DIR]     the views' pictures and sizes, for HOENN_VERSION
"""
import math, os, struct, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pokenav_art as A  # noqa: E402
import version  # noqa: E402

W, H = 32, 24
CHAR_LIMIT = 0x6000 // 32               # characters 0-767 for the three BGs (the maps from 0x6000)
TEXT_LINE = 15
ART_LINES = 15                          # palette lines 0-14 for art, 15 the text windows'
VIEW_MAGIC = 0x31564E44                 # "DNV1" (dexnav_screen.c DNAV_VIEW_MAGIC)
VIEWS = ['area', 'found', 'hidden']     # the order in a/0/0/8 (gHoennB2DexNav->viewFile + index)

# The text file's lines (dexnav_screen.c TXT_*; 18: the PokéNav menu's description, pokenav.c DEXNAV_TXT_PNAV_DESC).
# Every line is NEW: 0-18 approved by the user 2026-11-09, 19-34 (the ORAS look's labels and lines) approved 2026-11-09.
# A line break inside a line is the two characters \n.
TEXT = [
    'DexNav',
    'Grass',
    'Cave',
    'Water',
    'Search Lv.',
    'Chain',
    'Tap a Pokémon to look for it.',
    'It’s hiding nearby! Sneak up on it.',
    'Nothing could be found here.',
    'It ran off! Move more slowly.',
    'Go surfing to look for this one.',
    'It isn’t found on the water.',
    'You haven’t seen this Pokémon yet.',
    'No wild Pokémon live here.',
    'It got away...',
    'Pick a Pokémon to search again!',
    '?????',
    'Lv.',
    'Find Pokémon hiding in this area.',
    'Found Pokémon',
    'Hidden Pokémon',
    'Name',
    'Type',
    'Search Level',
    'Level',
    'First Move',
    'Ability',
    'Potential',
    'Sneak up on it!',
    'There are Pokémon here you\\nhaven’t caught yet!',
    'Almost done! Just a few left\\nto catch here!',
    'Well done! You’ve caught\\nevery Pokémon here!',
    '???',
    'SEARCH',
    'POKéNAV',
]
T_TITLE, T_FOUND, T_HIDDEN, T_NAME, T_TYPE, T_SEARCH_LEVEL, T_LEVEL, T_FIRST_MOVE, T_ABILITY, T_POTENTIAL, T_SNEAK = \
    0, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28
T_SEARCH, T_POKENAV = 33, 34


def text_lines():
    return list(TEXT)


# ---- layout (dexnav_screen.c has the same numbers) ----------------------------------------------------------------
PANEL = (8, 8, 248, 160)            # the area's panel: tiles 1-30 x 1-19 (the snapshot)
PANEL_TILES = (1, 1, 30, 19)
STRIP = (128, 136, 248, 156)        # the dark strip under the place's name (window 0, brightness down on BG 6)
AREA_WINDOWS = {'name': (16, 17, 14, 2), 'message': (3, 15, 26, 4)}
FOUND_WINDOWS = {'level': (28, 0, 3, 2), 'name': (1, 6, 12, 2)}
HIDDEN_WINDOWS = {'level': (28, 0, 3, 2), 'lv': (1, 10, 9, 2), 'move': (0, 16, 12, 2), 'ability': (19, 16, 12, 2)}
WINDOWS = {'area': AREA_WINDOWS, 'found': FOUND_WINDOWS, 'hidden': HIDDEN_WINDOWS}
# Pieces (name, tiles x, y, w, h) in each view's order (dexnav_screen.c PIECE_*)
AREA_PIECES = [('question', 0, 0, 2, 2), ('crown', 26, 1, 3, 2), ('message', 2, 14, 28, 6), ('pokenav', 1, 21, 13, 3),
               ('back', 28, 21, 3, 3)]
HIDDEN_PIECES = [('star_on', 23, 11, 2, 2), ('star_off', 23, 11, 2, 2), ('excl', 0, 13, 2, 2)]
PIECES = {'area': AREA_PIECES, 'found': [], 'hidden': HIDDEN_PIECES}
STAR_TILES = [(23, 11), (25, 11), (27, 11)]        # Hidden: the three stars (under Potential's line)
EXCL_TILES = {'move': (0, 13), 'ability': (22, 13)}  # Hidden: "!" by First Move, by Ability
RING_CENTRE = {'found': (128, 92), 'hidden': (128, 96)}

# ---- colours (ours, in ORAS's spirit) -----------------------------------------------------------------------------
OR, OR_LT, OR_EDGE = (240, 136, 32), (248, 168, 72), (128, 56, 16)
CREAM = (248, 224, 176)
TAB, TAB_HI, TAB_EDGE = (48, 48, 56), (104, 104, 112), (16, 16, 24)
WHITE, DARK, GREY, LGREY = (248, 248, 248), (40, 40, 48), (128, 128, 136), (200, 200, 208)
BAR, BAR_HI, BAR_DK, BAR_EDGE = (208, 208, 216), (240, 240, 248), (160, 160, 176), (88, 88, 104)
GR, GR_DK, GR_LT, GR_LINE = (56, 176, 80), (24, 112, 48), (128, 224, 120), (96, 216, 104)
BL, BL_DK, BL_LT = (48, 120, 216), (24, 64, 152), (128, 184, 248)
TE, TE_DK, TE_LT = (56, 192, 176), (24, 128, 120), (144, 232, 216)
RD, RD_DK, RD_LT = (216, 48, 40), (144, 24, 24), (248, 112, 96)
GOLD, GOLD_DK, GOLD_LT, GOLD_EDGE = (248, 192, 40), (200, 128, 24), (255, 240, 160), (112, 64, 16)
RADAR_LINE = (88, 24, 16)
# palette line 15 (the windows): 1 white, 2 dark, 3 light grey, 4 green (dexnav_screen.c COLOR_*)
TEXT_COLORS = [(0, 0, 0), WHITE, DARK, LGREY, GR_LT]
SILHOUETTE = (49, 49, 65)


def c555(c):
    """The colour the DS shows for an 8-bit RGB."""
    return tuple((round(v * 31 / 255) << 3) | (round(v * 31 / 255) >> 2) for v in c[:3])


# ---- Black 2's font -----------------------------------------------------------------------------------------------
_FONT = None


def _font():
    global _FONT
    if _FONT is None:
        import b2font
        _FONT = b2font.load(0)
    return _FONT


def glyph(ch):
    f = _font()
    d = f.d
    fw, fh = d[f.pglp], d[f.pglp + 1]
    g = f.cmap.get(ord(ch), f.alter)
    cell = d[f.pglp + 8 + g * f.cellsize:f.pglp + 8 + (g + 1) * f.cellsize]
    bits = ''.join(format(b, '08b') for b in cell[3:])
    px = [[int(bits[(y * fw + x) * 2:(y * fw + x) * 2 + 2], 2) for x in range(fw)] for y in range(fh)]
    return px, cell[2]


def text_width(s):
    return sum(glyph(c)[1] for c in s)


# ---- drawing ------------------------------------------------------------------------------------------------------
def layer(alpha):
    return np.zeros((192, 256, 4 if alpha else 3), np.uint8)


def put(lay, x, y, c):
    if 0 <= x < lay.shape[1] and 0 <= y < lay.shape[0]:
        lay[y, x, :3] = c555(c)
        if lay.shape[2] == 4:
            lay[y, x, 3] = 255


def fill(lay, x0, y0, x1, y1, c):
    lay[y0:y1, x0:x1, :3] = c555(c)
    if lay.shape[2] == 4:
        lay[y0:y1, x0:x1, 3] = 255


def inside_round(x, y, x0, y0, x1, y1, r):
    if not (x0 <= x < x1 and y0 <= y < y1):
        return False
    cx = min(max(x + 0.5, x0 + r), x1 - r)
    cy = min(max(y + 0.5, y0 + r), y1 - r)
    return (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r


def round_rect(lay, x0, y0, x1, y1, r, fillc, edge=None, ew=1, hi=None):
    for y in range(max(y0, 0), min(y1, lay.shape[0])):
        for x in range(max(x0, 0), min(x1, lay.shape[1])):
            if not inside_round(x, y, x0, y0, x1, y1, r):
                continue
            c = fillc
            if edge and not inside_round(x, y, x0 + ew, y0 + ew, x1 - ew, y1 - ew, max(r - ew, 0)):
                c = edge
            elif hi and not inside_round(x, y - 1, x0 + ew, y0 + ew, x1 - ew, y1 - ew, max(r - ew, 0)):
                c = hi
            put(lay, x, y, c)


def text(lay, x, y, s, fg, sh=None, align='left'):
    if align == 'right':
        x -= text_width(s)
    elif align == 'center':
        x -= text_width(s) // 2
    for ch in s:
        px, adv = glyph(ch)
        for gy, row in enumerate(px):
            for gx, v in enumerate(row):
                if v == 1:
                    put(lay, x + gx, y + gy, fg)
                elif v == 2 and sh is not None:
                    put(lay, x + gx, y + gy, sh)
        x += adv
    return x


def ring(lay, cx, cy, r0, r1, c, segs=None, gap=0.0, c2=None):
    for y in range(int(cy - r1 - 1), int(cy + r1 + 2)):
        for x in range(int(cx - r1 - 1), int(cx + r1 + 2)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if not (r0 <= d < r1):
                continue
            col = c
            if segs:
                a = (math.atan2(y + 0.5 - cy, x + 0.5 - cx) + 2 * math.pi) % (2 * math.pi)
                k = a / (2 * math.pi / segs)
                if (k - int(k)) * (2 * math.pi / segs) < gap:
                    continue
                if c2 and int(k) % 2:
                    col = c2
            put(lay, x, y, col)


def logo(lay, x, y):
    """A small PokéNav mark (ours): a red rounded square with a white ring and dot."""
    round_rect(lay, x, y, x + 14, y + 14, 4, RD, edge=RD_DK)
    ring(lay, x + 7, y + 7, 3.0, 5.0, WHITE)
    fill(lay, x + 6, y + 6, x + 8, y + 8, WHITE)


def title_tab(lay, s, width):
    round_rect(lay, -8, -8, width, 22, 7, TAB, edge=TAB_EDGE, hi=TAB_HI)
    logo(lay, 5, 4)
    text(lay, 24, 4, s, WHITE, TAB_EDGE)


def pill(lay, x0, y0, x1, y1, label, base, dk, lt):
    round_rect(lay, x0, y0, x1, y1, (y1 - y0) // 2, base, edge=dk, ew=2, hi=lt)
    text(lay, (x0 + x1) // 2, y0 + (y1 - y0 - 12) // 2 - 1, label, WHITE, dk, align='center')


def back_button(lay, x, y):
    """ORAS's round return button, ours: a blue disc with a white bent arrow."""
    for yy in range(y, y + 24):
        for xx in range(x, x + 24):
            d = math.hypot(xx + 0.5 - (x + 12), yy + 0.5 - (y + 12))
            if d < 12:
                put(lay, xx, yy, BL_DK if d >= 10.5 else BL_LT if yy < y + 8 and 8 < d < 10.5 else BL)
    for i in range(9):
        put(lay, x + 7 + i, y + 9, WHITE); put(lay, x + 7 + i, y + 10, WHITE)
    for j in range(7):
        put(lay, x + 15, y + 9 + j, WHITE); put(lay, x + 16, y + 9 + j, WHITE)
    for k in range(4):
        for j in range(-k, k + 2):
            put(lay, x + 5 + k, y + 9 + j, WHITE)


def bar(lay, y0):
    """The bottom bar (ORAS's app bar, ours): a light metal strip with a dark top edge."""
    fill(lay, 0, y0, 256, 192, BAR)
    fill(lay, 0, y0, 256, y0 + 1, BAR_EDGE)
    fill(lay, 0, y0 + 1, 256, y0 + 2, BAR_HI)
    fill(lay, 0, 190, 256, 192, BAR_DK)


def stripes(lay, y0, y1, c1, c2):
    for y in range(y0, y1):
        for x in range(256):
            put(lay, x, y, c2 if (x + y) % 8 < 3 else c1)


def panel_frame(front):
    """The panel's rounded frame on BG 5: orange outside the corners, a dark edge, a cream inner line."""
    x0, y0, x1, y1 = PANEL
    for y in range(y0 - 3, y1 + 3):
        for x in range(x0 - 3, x1 + 3):
            inn = inside_round(x, y, x0, y0, x1, y1, 6)
            out = inside_round(x, y, x0 - 3, y0 - 3, x1 + 3, y1 + 3, 9)
            if out and not inn:
                put(front, x, y, CREAM if inside_round(x, y, x0 - 2, y0 - 2, x1 + 2, y1 + 2, 8) and
                    inside_round(x, y, x0 - 1, y0 - 1, x1 + 1, y1 + 1, 7) else OR_EDGE)
            elif not inn and x0 <= x < x1 and y0 <= y < y1:
                put(front, x, y, OR)


def question(lay, cx, cy):
    """A species not seen yet (ours): a dark bubble with a white "?"."""
    round_rect(lay, cx - 8, cy - 8, cx + 8, cy + 8, 7, (56, 56, 72), edge=(24, 24, 32), hi=(96, 96, 112))
    text(lay, cx, cy - 7, '?', WHITE, (24, 24, 32), align='center')


CROWN = ['....G......G......G....', '...GLG....GLG....GLG...', '...GYG....GYG....GYG...', '..GYYYG..GYYYG..GYYYG..',
         '..GYYYYGGYYYYYGGYYYYG..', '.GYYYYYYYYYRYYYYYYYYYG.', '.GYYYYYYYYRRRYYYYYYYYG.', '.GYYYYYYYYYRYYYYYYYYYG.',
         '.GDDDDDDDDDDDDDDDDDDDG.', '.GLLLLLLLLLLLLLLLLLLLG.', '.GDDDDDDDDDDDDDDDDDDDG.', '..GGGGGGGGGGGGGGGGGGG..']
STAR = ['......O......', '.....OYO.....', '.....OYO.....', '....OYYYO....', 'OOOOOYYYOOOOO', '.OYYYYYYYYYO.',
        '..OYYYYYYYO..', '...OYYYYYO...', '...OYYOYYO...', '..OYYO.OYYO..', '..OYO...OYO..', '.OO.......OO.']


def sprite_rows(lay, x, y, rows, cmap):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in cmap:
                put(lay, x + i, y + j, cmap[ch])


def excl(lay, x, y):
    """ORAS's "!" badge, ours: a red disc with a white "!"."""
    for yy in range(14):
        for xx in range(14):
            d = math.hypot(xx + 0.5 - 7, yy + 0.5 - 7)
            if d < 7:
                put(lay, x + xx, y + yy, RD_DK if d >= 6 else RD)
    fill(lay, x + 6, y + 3, x + 8, y + 8, WHITE)
    fill(lay, x + 6, y + 9, x + 8, y + 11, WHITE)


def underline(lay, x0, x1, y):
    """ORAS's green label line, ours: a bright line with a few darker dashes at its end."""
    for x in range(x0, x1):
        put(lay, x, y, GR_LINE)
    for k, x in enumerate(range(x1 - 30, x1, 6)):
        fill(lay, x, y - 3 - (k % 2) * 2, x + 3, y - 1, GR_DK if k % 2 else GR)


# ---- the views ----------------------------------------------------------------------------------------------------
def _piece_layer(draw):
    lay = layer(True)
    draw(lay)
    return lay


def area_view():
    """(art, front, {piece: layer}): the frame, tab and bar; the panel left empty for the snapshot."""
    art, front = layer(False), layer(True)
    stripes(art, 0, 192, OR, OR_LT)
    art[PANEL[1]:PANEL[3], PANEL[0]:PANEL[2]] = 0          # the snapshot's (map entries 0 here)
    bar(art, 160)
    panel_frame(front)
    title_tab(front, TEXT[T_TITLE], 104)
    pieces = {
        'question': _piece_layer(lambda l: question(l, 8, 8)),
        'crown': _piece_layer(lambda l: sprite_rows(l, 26 * 8, 8 + 2, CROWN,
                                                    {'G': GOLD_EDGE, 'Y': GOLD, 'L': GOLD_LT, 'D': GOLD_DK, 'R': RD})),
        'message': _piece_layer(lambda l: round_rect(l, 16, 114, 240, 156, 6, WHITE, edge=GREY)),
        'pokenav': _piece_layer(lambda l: pill(l, 8, 168, 112, 190, TEXT[T_POKENAV], BL, BL_DK, BL_LT)),
        'back': _piece_layer(lambda l: back_button(l, 224, 168)),
    }
    return art, front, pieces


def found_view(grey=False):
    """FOUND, in orange (search level 50 and more) or grey (0): (art, front, {})."""
    art, front = layer(False), layer(True)
    mix = (lambda a, b: a) if grey else (lambda a, b: b)
    c1, c2, band = mix((150, 150, 150), OR), mix((180, 180, 180), OR_LT), mix((168, 168, 168), (248, 160, 64))
    stripes(art, 0, 192, c1, c2)
    for y in range(24, 160):
        if abs(y - 92) / 68 < 0.6:
            for x in range(256):
                if (x + y) % 8 >= 3:
                    put(art, x, y, band)
    bar(art, 168)
    cx, cy = RING_CENTRE['found']
    ring(art, cx, cy, 42, 50, TE, segs=12, gap=0.10, c2=TE_LT)
    ring(art, cx, cy, 50, 52, TE_DK)
    ring(art, cx, cy, 39, 42, TE_DK, segs=24, gap=0.12)
    title_tab(front, TEXT[T_FOUND], 128)
    text(front, 150, 4, TEXT[T_SEARCH_LEVEL], WHITE, TAB_EDGE)
    underline(front, 140, 250, 21)
    text(front, 8, 30, TEXT[T_NAME], WHITE, OR_EDGE)
    underline(front, 4, 112, 46)
    text(front, 186, 30, TEXT[T_TYPE], WHITE, OR_EDGE)
    underline(front, 180, 252, 46)
    pill(front, 70, 166, 186, 190, TEXT[T_SEARCH], GR, GR_DK, GR_LT)
    back_button(front, 224, 168)
    return art, front, {}


def hidden_view():
    art, front = layer(False), layer(True)
    cx, cy = RING_CENTRE['hidden']
    for y in range(192):
        for x in range(256):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            k = min(d / 150, 1)
            base = [int(a + (b - a) * k) for a, b in zip((232, 104, 24), (96, 24, 16))]
            if int(d) // 6 % 2:
                base = [max(0, v - 14) for v in base]
            put(art, x, y, (base[0] // 16 * 16, base[1] // 16 * 16, base[2] // 16 * 16))
    for r in (64, 88, 112):
        ring(art, cx, cy, r, r + 2, RADAR_LINE)
    for a in range(0, 360, 30):
        for k in range(8):
            put(art, int(cx + (54 + k) * math.cos(math.radians(a))), int(cy + (54 + k) * math.sin(math.radians(a))), RADAR_LINE)
    ring(art, cx, cy, 40, 48, TE, segs=12, gap=0.10, c2=TE_LT)
    ring(art, cx, cy, 48, 50, TE_DK)
    bar(art, 168)
    title_tab(front, TEXT[T_HIDDEN], 128)
    text(front, 150, 4, TEXT[T_SEARCH_LEVEL], WHITE, TAB_EDGE)
    underline(front, 140, 250, 21)
    text(front, 6, 64, TEXT[T_LEVEL], WHITE, RADAR_LINE); underline(front, 2, 84, 80)
    text(front, 20, 110, TEXT[T_FIRST_MOVE], WHITE, RADAR_LINE); underline(front, 2, 96, 126)
    text(front, 186, 64, TEXT[T_POTENTIAL], WHITE, RADAR_LINE); underline(front, 176, 254, 80)
    text(front, 192, 110, TEXT[T_ABILITY], WHITE, RADAR_LINE); underline(front, 160, 254, 126)
    back_button(front, 224, 168)
    text(front, 10, 173, TEXT[T_SNEAK], DARK, LGREY)
    on = {'O': GOLD_EDGE, 'Y': GOLD}
    off = {'O': (72, 72, 80), 'Y': (120, 120, 128)}
    x0, y0 = STAR_TILES[0]
    pieces = {
        'star_on': _piece_layer(lambda l: sprite_rows(l, x0 * 8 + 1, y0 * 8 + 1, STAR, on)),
        'star_off': _piece_layer(lambda l: sprite_rows(l, x0 * 8 + 1, y0 * 8 + 1, STAR, off)),
        'excl': _piece_layer(lambda l: excl(l, EXCL_TILES['move'][0] * 8 + 2, EXCL_TILES['move'][1] * 8 + 1)),
    }
    return art, front, pieces


def none_panel():
    """The panel of a place with no wild Pokémon (a snapshot of its own, dexnav_snapshots.py): red, a Poké Ball mark, and
    its line (TEXT 13) drawn in: a town costs no text printing on the way in (each letter would be a card read)."""
    img = np.zeros((PANEL[3] - PANEL[1], PANEL[2] - PANEL[0], 3), np.uint8)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            sx, sy = x + PANEL[0], y + PANEL[1]
            img[y, x] = c555(RD_LT if (sx - sy) % 16 < 3 else RD)
            d = math.hypot(sx + 0.5 - 128, sy + 0.5 - 74)
            if 34 <= d < 40 or (abs(sy + 0.5 - 74) < 3 and d < 40) or 10 <= d < 15:
                img[y, x] = c555((240, 136, 120))
    lay = layer(True)
    text(lay, 128, 128, TEXT[13], WHITE, RD_DK, align='center')
    m = lay[PANEL[1]:PANEL[3], PANEL[0]:PANEL[2], 3] > 0
    img[m] = lay[PANEL[1]:PANEL[3], PANEL[0]:PANEL[2], :3][m]
    return img


# ---- sprites --------------------------------------------------------------------------------------------------------
UI_PALETTE = [(0, 0, 0), RD, RD_LT, RD_DK, TE_LT, TE_DK, TE]


def _ring_frame(r0, r1, inner, segs, idx):
    """32 x 32 colour indices of a ring (UI_PALETTE)."""
    px = [[0] * 32 for _ in range(32)]
    for y in range(32):
        for x in range(32):
            d = math.hypot(x + 0.5 - 16, y + 0.5 - 16)
            if r0 <= d < r1:
                if segs:
                    a = (math.atan2(y + 0.5 - 16, x + 0.5 - 16) + 2 * math.pi) % (2 * math.pi)
                    k = a / (2 * math.pi / segs)
                    if (k - int(k)) * (2 * math.pi / segs) < 0.18:
                        continue
                    px[y][x] = idx[0] if int(k) % 2 == 0 else idx[1]
                else:
                    px[y][x] = idx[0]
            elif r1 <= d < r1 + inner:
                px[y][x] = idx[2]
    return px


def _cells(frames):
    out = bytearray()
    for px in frames:
        for ty in range(4):
            for tx in range(4):
                for y in range(8):
                    row = px[ty * 8 + y][tx * 8:tx * 8 + 8]
                    for x in range(0, 8, 2):
                        out.append(row[x] | row[x + 1] << 4)
    return bytes(out)


def obj_chars():
    """The search ring (red, shown at double size: affine) and the PokéNav page's cursor (teal), two frames each (they
    pulse), the icons' cell layout (32 x 32, 16 characters a frame, row by row)."""
    ring_ = _cells([_ring_frame(11, 14, 1, 8, (1, 2, 3)), _ring_frame(10.5, 13.5, 1, 8, (1, 2, 3))])
    cursor = _cells([_ring_frame(13, 15.5, 1, 0, (4, 4, 5)), _ring_frame(12.5, 15, 1, 0, (4, 4, 5))])
    return ring_ + cursor


def obj_palettes():
    ui = UI_PALETTE + [(0, 0, 0)] * (16 - len(UI_PALETTE))
    sil = [(0, 0, 0)] + [SILHOUETTE] * 15
    return struct.pack('<32H', *[A._rgb555(c) for c in ui + sil])


# ---- packing --------------------------------------------------------------------------------------------------------
class Lines:
    """Palette lines, each up to 15 colours (0 is clear), shared by tiles whose colours fit."""
    def __init__(self, limit, first=0):
        self.lines, self.limit, self.first = [], limit, first

    def place(self, colors):
        colors = set(colors)
        assert len(colors) <= 15, f'a tile of {len(colors)} colours'
        for i, line in enumerate(self.lines):
            if colors <= line:
                return i
        for i, line in enumerate(self.lines):
            if len(line | colors) <= 15:
                line |= colors
                return i
        if len(self.lines) >= self.limit:
            return None
        self.lines.append(set(colors))
        return len(self.lines) - 1


def tiles_of(lay, region=None):
    """{(tx, ty): (8 x 8 colours or None, colour set)} of a layer's tiles with something on them."""
    out = {}
    x0, y0, x1, y1 = region or (0, 0, W, H)
    alpha = lay.shape[2] == 4
    for ty in range(y0, y1):
        for tx in range(x0, x1):
            blk = lay[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8]
            if alpha:
                if not blk[..., 3].any():
                    continue
                rows = tuple(tuple(tuple(int(v) for v in p[:3]) if p[3] else None for p in row) for row in blk)
            else:
                if not blk.any():
                    continue
                rows = tuple(tuple(tuple(int(v) for v in p) for p in row) for row in blk)
            out[(tx, ty)] = (rows, {c for row in rows for c in row if c is not None})
    return out


class Sheet:
    """Characters (a tile and its flips share one; 0 the blank) and palette lines of one load, from char `base`."""
    def __init__(self, base=1, line_base=0, line_limit=ART_LINES):
        self.packer = A.Packer()            # (its tile 0 is the blank one)
        self.base, self.line_base = base, line_base
        self.lines = Lines(line_limit - line_base)
        self.placed = []

    def add(self, tiles):
        """tiles: tiles_of(); returns a list of (key, placed index) to resolve once every tile is in."""
        out = []
        for key, (rows, cols) in tiles.items():
            li = self.lines.place(cols)
            assert li is not None, f'out of palette lines ({self.lines.limit} from line {self.line_base})'
            self.placed.append((rows, li))
            out.append((key, len(self.placed) - 1))
        return out

    def finish(self):
        """The entries of every placed tile (character | flips | line), in placing order."""
        order = [sorted(line) for line in self.lines.lines]
        self.order = order
        entries = []
        for rows, li in self.placed:
            t = tuple(tuple(0 if c is None else 1 + order[li].index(c) for c in row) for row in rows)
            n, hf, vf = self.packer.add(t)
            entries.append(((n - 1 + self.base) if n else 0) | hf << 10 | vf << 11 | (li + self.line_base) << 12)
        return entries

    def tile_bytes(self):
        return self.packer.blob()[32:]       # (without the blank one: character 0 is always blank)

    def palette(self):
        return [[(0, 0, 0)] + o + [(0, 0, 0)] * (15 - len(o)) for o in self.order]

    @property
    def count(self):
        return len(self.packer.tiles) - 1


def _map(entries_of, placed, region=(0, 0, W, H)):
    m = [0] * (W * H)
    for (tx, ty), i in placed:
        m[ty * W + tx] = entries_of[i]
    return m


def pack_view(name, grey_layers=None):
    """(file bytes, report) of a view."""
    art, front, pieces = {'area': area_view, 'found': found_view, 'hidden': hidden_view}[name]()
    spec = PIECES[name]
    sheet = Sheet()
    p_art = sheet.add(tiles_of(art))
    p_front = sheet.add(tiles_of(front))
    p_pieces = {}
    for pname, x, y, w, h in spec:
        lay = pieces[pname]
        if pname == 'question':
            region = (0, 0, 2, 2)
        else:
            region = (x, y, x + w, y + h)
        p_pieces[pname] = (sheet.add(tiles_of(lay, region)), region)
    entries = sheet.finish()
    art_map = _map(entries, p_art)
    front_map = _map(entries, p_front)
    piece_entries = []
    for pname, x, y, w, h in spec:
        placed, (rx0, ry0, rx1, ry1) = p_pieces[pname]
        e = [0] * (w * h)
        for (tx, ty), i in placed:
            e[(ty - ry0) * w + (tx - rx0)] = entries[i]
        piece_entries.append((pname, w, h, x, y, e))
    palette = sheet.palette()
    pal = [[(0, 0, 0)] * 16 for _ in range(16)]
    for i, line in enumerate(palette):
        pal[i] = line
    pal[TEXT_LINE] = TEXT_COLORS + [(0, 0, 0)] * (16 - len(TEXT_COLORS))
    pal[0][0] = c555(OR)                    # the backdrop (behind a clear pixel)
    grey = None
    if name == 'found':                     # the same picture in grey: each orange colour's grey twin
        gart, gfront, _ = found_view(grey=True)
        twin = {}
        for la, lb in ((art, gart), (front, gfront)):
            a = la[..., :3].reshape(-1, 3); b = lb[..., :3].reshape(-1, 3)
            for ca, cb in zip(map(tuple, a), map(tuple, b)):
                twin.setdefault(tuple(int(v) for v in ca), tuple(int(v) for v in cb))
        grey = [[twin.get(c, c) for c in line] for line in pal]
    return dict(name=name, sheet=sheet, art_map=art_map, front_map=front_map, pieces=piece_entries, palette=pal,
                grey=grey, lines=len(palette), tiles=sheet.count,
                windows=sum(w * h for _, _, w, h in WINDOWS[name].values()))


def view_file(v, window_char):
    """The view's bytes (the layout in this file's docstring)."""
    HEADER = 48
    body = bytearray()

    def at(data):
        while (HEADER + len(body)) % 4:
            body.append(0)
        pos = HEADER + len(body)
        body.extend(data)
        return pos
    tiles = at(v['sheet'].tile_bytes())
    pal = at(struct.pack('<256H', *[A._rgb555(c) for line in v['palette'] for c in line]))
    art = at(struct.pack('<768H', *v['art_map']))
    front = at(struct.pack('<768H', *v['front_map']))
    table, ent = bytearray(), bytearray()
    for pname, w, h, x, y, e in v['pieces']:
        table += struct.pack('<IBBBB', 8 * len(v['pieces']) + len(ent), w, h, x, y)
        ent += struct.pack(f'<{len(e)}H', *e)
    block = bytes(table + ent)
    pieces = at(block) if block else 0
    grey = at(struct.pack('<256H', *[A._rgb555(c) for line in v['grey'] for c in line])) if v['grey'] else 0
    objc = at(obj_chars()) if v['name'] == 'area' else 0
    objp = at(obj_palettes()) if v['name'] == 'area' else 0
    head = struct.pack('<IHHIIIIIHHIHHII', VIEW_MAGIC, v['tiles'], v['lines'], tiles, pal, art, front, pieces,
                       len(v['pieces']), len(block), grey, window_char, 0, objc, objp)
    assert len(head) == HEADER, len(head)
    return head + bytes(body)


# ---- the PokéNav menu's DEXNAV button (Gen 3's own button, its letters; pokenav_art.py's menu view) -----------------
GLYPHS_E_EXTRA = {
    'K': ['#...#', '#..#.', '#.#..', '##...', '##...', '#.#..', '#..#.', '#...#', '#...#'],
    'V': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
    'X': ['#...#', '#...#', '.#.#.', '.#.#.', '..#..', '.#.#.', '.#.#.', '#...#', '#...#'],
    'é': ['...#.', '..#..', '.....', '.###.', '#...#', '#####', '#....', '#...#', '.###.'],
}
GLYPHS_R_EXTRA = {
    'K': ['#...#', '#...#', '#..#.', '#.#..', '##...', '##...', '#.#..', '#..#.', '#...#', '#...#', '#...#'],
    'V': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..', '..#..'],
    'X': ['#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..', '.#.#.', '.#.#.', '#...#', '#...#', '#...#'],
    'é': ['...#.', '..#..', '.....', '.....', '.###.', '#...#', '#...#', '#####', '#....', '#...#', '.###.'],
    'L': ['#....'] * 10 + ['#####'],
}


def _paths():
    if A.is_emerald():
        g = os.path.join(A.EMERALD, 'graphics', 'pokenav')
    else:
        g = os.path.join(A.RUBY, 'graphics', 'pokenav')
    return lambda *a: os.path.join(g, *a)


def _button_pixels(path):
    pc = A.button_piece(path)
    px = [[0] * 128 for _ in range(16)]
    for r, row in enumerate(pc):
        for c, (t, hf, vf, pal) in enumerate(row):
            for y in range(8):
                for x in range(8):
                    px[r * 8 + y][c * 8 + x] = t[y][x]
    return px, list(pc[0][0][3])


def _white_shadow(px, pal):
    import collections
    used = {px[y][x] for y in range(2, 14) for x in range(16, 128)}
    white = max(used, key=lambda i: (sum(pal[i]), -i))
    right = collections.Counter(px[y][x + 1] for y in range(2, 14) for x in range(16, 127)
                                if px[y][x] == white and px[y][x + 1] != white)
    return white, right.most_common(1)[0][0]


def _letters(path, text_):
    px, pal = _button_pixels(path)
    white, _ = _white_shadow(px, pal)
    rows = [y for y in range(16) if any(px[y][x] == white for x in range(16, 128))]
    if not rows:
        return {}, None
    cols = [x for x in range(16, 128) if any(px[y][x] == white for y in rows)]
    runs, cur = [], []
    for x in cols:
        if cur and x != cur[-1] + 1:
            runs.append(cur)
            cur = []
        cur.append(x)
    if cur:
        runs.append(cur)
    out = {}
    for ch, run in zip([c for c in text_ if c != ' '], runs):
        out.setdefault(ch, [''.join('#' if px[y][x] == white else '.' for x in run) for y in range(rows[0], rows[-1] + 1)])
    return out, rows[0]


def alphabet():
    p = _paths()
    if A.is_emerald():
        sets = [('options/hoenn_map', 'HOENN MAP'), ('options/search', 'SEARCH'), ('options/cancel', 'CANCEL'),
                ('options/party', 'PARTY'), ('options/switch_off', 'SWITCH OFF'), ('options/condition', 'CONDITION'),
                ('options/match_call', 'MATCH CALL'), ('options/ribbons', 'RIBBONS')]
        extra = GLYPHS_E_EXTRA
    else:
        sets = [('menu_hoennmap', 'HOENN MAP'), ('menu_off', 'SWITCH OFF'), ('menu_condition', 'CONDITION'),
                ('menu_eyes', "TRAINER'S EYES"), ('menu_ribbons', 'RIBBONS')]
        extra = GLYPHS_R_EXTRA
    glyphs, top = {}, None
    for name, label in sets:
        path = p(*name.split('/')) + '.png'
        if not os.path.exists(path):
            continue
        g, t = _letters(path, label.replace("'", ''))
        top = t if top is None and t is not None else top
        for k, v in g.items():
            glyphs.setdefault(k, v)
    for k, v in extra.items():
        glyphs.setdefault(k, v)
    return glyphs, top


def label_button(template, label):
    """A 16 x 2 tile piece: Gen 3's button with its label replaced (its letters, 6 pixels apart, a space 3)."""
    px, pal = _button_pixels(template)
    white, shadow = _white_shadow(px, pal)
    glyphs, top = alphabet()
    clean = [row[127] for row in px]
    for y in range(16):
        for x in range(15, 128):
            px[y][x] = clean[y]
    x = 16
    for ch in label:
        if ch == ' ':
            x += 3
            continue
        g = glyphs[ch.upper() if ch != 'é' else ch]
        for gy, row in enumerate(g):
            for gx, c in enumerate(row):
                if c == '#':
                    px[top + gy][x + gx] = white
        x += 6
    lit = {(y, xx) for y in range(16) for xx in range(15, 128) if px[y][xx] == white}
    for y, xx in lit:
        for dy, dx in ((0, 1), (1, 0)):
            if (y + dy, xx + dx) not in lit and y + dy < 16 and xx + dx < 128:
                px[y + dy][xx + dx] = shadow
    h, w = 2, 16
    return [[(tuple(tuple(px[r * 8 + y][c * 8 + x] for x in range(8)) for y in range(8)), 0, 0, pal) for c in range(w)]
            for r in range(h)]


def pokenav_menu_button():
    """The PokéNav menu's sixth button, DEXNAV (pokenav_art.views() 'menu': after Gen 3's five)."""
    p = _paths()
    return label_button(p('options', 'hoenn_map.png') if A.is_emerald() else p('menu_hoennmap.png'), 'DEXNAV')


# ---- previews -------------------------------------------------------------------------------------------------------
def render(v, art_extra=None, show=()):
    """RGB of a packed view as the C draws it (art map, front map, the named pieces at their places)."""
    tiles = [np.zeros((8, 8), np.uint8)] + [np.array(t, np.uint8) for t in v['sheet'].packer.tiles[1:]]
    pal = v['palette']
    img = np.zeros((192, 256, 3), np.uint8)
    img[:] = pal[0][0]

    def draw(m):
        for i, e in enumerate(m):
            if e & 0x3FF == 0:
                continue
            n, hf, vf, li = e & 0x3FF, e >> 10 & 1, e >> 11 & 1, e >> 12
            t = tiles[n - v['sheet'].base + 1] if n >= v['sheet'].base else tiles[0]
            if hf: t = t[:, ::-1]
            if vf: t = t[::-1, :]
            ty, tx = divmod(i, W)
            for y in range(8):
                for x in range(8):
                    if t[y, x]:
                        img[ty * 8 + y, tx * 8 + x] = pal[li][t[y, x]]
    draw(v['art_map'])
    if art_extra is not None:
        m = art_extra > 0
        img[m] = art_extra[m]
    draw(v['front_map'])
    for pname, w, h, x, y, e in v['pieces']:
        if pname in show:
            m = [0] * (W * H)
            for r in range(h):
                for c in range(w):
                    if x + c < W and y + r < H:
                        m[(y + r) * W + x + c] = e[r * w + c]
            draw(m)
    return img


if __name__ == '__main__':
    from PIL import Image
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for n in VIEWS:
        v = pack_view(n)
        Image.fromarray(render(v, show=[p[0] for p in PIECES[n] if p[0] != 'question'])).resize((512, 384)).save(
            os.path.join(out, f'dexnav_{n}_{version.OVERLAY or "sapphire"}.png'))
        print(n, v['tiles'], 'characters,', v['lines'], 'palette lines,', v['windows'], 'window characters')
