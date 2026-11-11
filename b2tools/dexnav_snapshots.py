"""The DexNav area view's snapshots (notes/DEXNAV.md; dexnav_art.py AREA): for every wild table (a/1/2/7 file) of the
version, a picture of its map drawn with Gen 3's own tiles and metatiles (Sapphire and Ruby: external/pokeruby,
Emerald: external/pokeemerald; converter/gba.py world_repo), cropped to the panel (15 x 9.5 metatiles), with the places
where the C puts each species' icon: on tiles of its kind (land: Gen 3's wild-encounter tiles that aren't water, such as
tall grass, a cave's floor, the desert's sand; water: its surfable encounter tiles), spread out.

The crop: the panel-sized window of the map with the most such tiles for the table's groups (data/dexnav_snapshots.json
"crops" can name one), centred when the map is smaller than the panel (its border metatiles around it). A map whose
groups live too far apart for one window (Route 111: its deep sand and its pond) gets two bands from the data, shown as
two views: 6 + 3 metatile rows with an 8-pixel frame bar between them (the panel border's colours, a tile row of its
own), so the join reads as a frame, not a cut. A group whose
map has no tile of its kind at all (Mirage Island's land on Route 130, Shoal Cave's high-tide water in its low-tide
rooms) needs a "stand_ins" entry there: its icons stand on walkable tiles. The build stops on a table that has a group
with fewer places on its own tiles than species, unless the data says otherwise.

File (uncompressed, read in 2 KB parts; dexnav_screen.c DnSnapFile), little-endian:
  u32 magic "DNS1"; u16 tileCount (at characters charBase..); u16 lineCount (at palette lines lineBase..);
  u8 landPlaces; u8 waterPlaces; u8 flags (1: the no-wild-Pokémon panel); u8 pad;
  u8 places[17][2] (icon centres in screen pixels: land 0-11, then water 0-4); u16 pad;
  u32 tiles; u32 palette (lineCount x 32 B); u32 map (30 x 19 entries for the panel, BG 6 tiles 1-30 x 1-19)
"""
import json, os, re, struct, sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import version  # noqa: E402
import dexnav_art as DA  # noqa: E402

SNAP_MAGIC = 0x31534E44             # "DNS1"
MW, MH = 15, 10                      # the crop in metatiles (its last row half shown)
BAND_ROWS = 9                        # two bands: 9 full rows and the divider fill the panel (16 * 9 + 8 = 152)
DIVIDER = 8                          # the frame bar between two bands: a tile row of its own (one character)
DIVIDER_ROWS = [DA.OR_EDGE, DA.CREAM, DA.OR, DA.OR, DA.OR, DA.OR, DA.CREAM, DA.OR_EDGE]
MAX_LAND, MAX_WATER = 12, 5          # include/hoennb2/dexnav.h DEXNAV_MAX_LAND / _WATER
PANEL = DA.PANEL
AVOID = [(0, 0, 104, 22), (208, 8, 232, 24), DA.STRIP]     # the tab, the crown, the name's strip
ENC_TABLE = 8 + 56 * 4               # a/1/2/7 (patches/hoenn_pokedex.py): rates, then 56 slots of 4 B
GRASS_SLOTS, SURF_SLOTS = range(0, 12), range(36, 41)
DATA = os.path.join(ROOT, 'data', 'dexnav_snapshots.json')


# ---- Gen 3's tiles -----------------------------------------------------------------------------------------------
_FLAGS = {}


def tile_flags():
    """Gen 3's sTileBitAttributes of the version's decomp: [behavior] -> 1 wild encounters | 2 surfable."""
    root = version.decomp()
    if root in _FLAGS:
        return _FLAGS[root]
    src = open(os.path.join(root, 'src', 'metatile_behavior.c')).read()
    flags = [0] * 256
    hdr = open(os.path.join(root, 'include', 'constants', 'metatile_behaviors.h')).read()
    if 'TILE_ATTRIBUTES(' in src:            # pokeruby: one entry per behavior, in order
        body = src[src.index('sTileBitAttributes'):]
        body = body[:body.index('};')]
        for i, (unused, surf, wild) in enumerate(re.findall(r'TILE_ATTRIBUTES\((\w+), (\w+), (\w+)\)', body)):
            flags[i] = (wild == 'TRUE') | (surf == 'TRUE') << 1
    else:                                    # pokeemerald: [MB_X] = TILE_FLAG_... entries
        values, v = {}, 0
        for n, val in re.findall(r'^\s*(MB_\w+)\s*(?:=\s*(\w+))?,', hdr[hdr.find('{'):], re.M):
            v = int(val, 0) if val else v
            values[n] = v
            v += 1
        for n, f in re.findall(r'\[(MB_\w+)\]\s*=\s*([^,\n]+)', src):
            flags[values[n]] = ('HAS_ENCOUNTERS' in f) | ('SURFABLE' in f) << 1
    _FLAGS[root] = flags
    return flags


_REPO = []


def repo():
    if not _REPO:
        import gba
        _REPO.append(gba.world_repo())
    return _REPO[0]


def overrides():
    return version.load_json(DATA) if os.path.exists(DATA) else {}


class Area:
    """A map cropped to the panel, its kinds (1 land, 2 water, 3 other walkable, 0 blocked) and the icons' places. The
    map sits in its border blocks (PAD around it), so a crop may reach past its edges."""
    PAD = 16

    def __init__(self, name, nland, nwater):
        import gba
        r = repo()
        ov = overrides()
        self.name = name
        folder = name if self._has(r, name) else re.sub(r'_\d+$', '', name)
        mj = r.map_json(folder)
        grid, lay = r.layout_grid(mj['layout'])
        self.mr = gba.MetatileRenderer(r, lay['primary_tileset'], lay['secondary_tileset'])
        border = np.frombuffer(open(os.path.join(r.root, lay['border_filepath']), 'rb').read(), dtype='<u2')
        bw = 2 if len(border) == 4 else int(round(len(border) ** 0.5))
        border = border.reshape(-1, bw)
        h, w = grid.shape
        pad = self.PAD
        P = np.zeros((h + 2 * pad, w + 2 * pad), np.int64)
        for y in range(P.shape[0]):
            for x in range(P.shape[1]):
                my, mx = y - pad, x - pad
                P[y, x] = grid[my, mx] if (0 <= my < h and 0 <= mx < w) else border[my % border.shape[0], mx % border.shape[1]]
        flags = tile_flags()
        K = np.zeros(P.shape, np.int8)
        beh = {}
        for y in range(P.shape[0]):
            for x in range(P.shape[1]):
                m = int(P[y, x])
                if (m & 0x3FF) not in beh:
                    beh[m & 0x3FF] = flags[self.mr.behavior(m & 0x3FF)]
                f = beh[m & 0x3FF]
                K[y, x] = 2 if f == 3 else 1 if f == 1 else 3 if (m >> 10) & 3 == 0 else 0
        inner = K[pad:pad + h, pad:pad + w]
        self.K, self.map_size = K, (w, h)
        stand = set(ov.get('stand_ins', {}).get(name, ()))
        self.stand_in = {1: 'land' in stand, 2: 'water' in stand}
        for k, kind in ((1, 'land'), (2, 'water')):
            if kind in stand:
                assert not (inner == k).any(), f'dexnav_snapshots.json: {name} has {kind} tiles of its own: no stand-in'
        self.row_y = [PANEL[1] + 16 * r for r in range(MH)]       # each crop row's top on the screen
        self.mask = self._mask()
        crop = ov.get('crops', {}).get(name)
        if crop:                     # [x, y] (the map's metatiles, may be past its edges), or bands [[x, y, rows], ...]
            bands = [crop + [MH]] if isinstance(crop[0], int) else crop
            if len(bands) > 1:       # two views, a frame bar between them (DIVIDER px): 9 full rows fill the panel
                assert len(bands) == 2 and sum(b[2] for b in bands) == BAND_ROWS, \
                    f'dexnav_snapshots.json: {name}: two bands of {BAND_ROWS} rows in all'
                n = bands[0][2]
                self.row_y = [PANEL[1] + 16 * r + (DIVIDER if r >= n else 0) for r in range(BAND_ROWS)]
                self.divider = PANEL[1] + 16 * n
                self.mask = self._mask()
            else:
                assert bands[0][2] == MH, f'dexnav_snapshots.json: {name}: a crop is {MH} rows'
        else:                        # (a side smaller than the panel: centred on it)
            oy, ox = self._best(K, pad, h, w, nland, nwater, centred=(h < MH, w < MW))
            bands = [[ox, oy, MH]]
        self.bands = bands
        rows_b, rows_k = [], []                # (band i's row k: the map's row y_i + k)
        for bx, by, n in bands:
            for k in range(n):
                rows_b.append(P[by + pad + k, bx + pad:bx + pad + MW])
                rows_k.append(K[by + pad + k, bx + pad:bx + pad + MW])
        self.blocks, self.kinds = np.array(rows_b), np.array(rows_k)
        self.ox, self.oy = bands[0][0], bands[0][1]

    divider = None

    def _mask(self):
        mask = np.zeros((len(self.row_y), MW), bool)
        for y in range(len(self.row_y)):
            for x in range(MW):
                mask[y, x] = self.free(*self.centre(x, y))
        return mask

    def _best(self, K, pad, h, w, nland, nwater, centred=(False, False)):
        """(y, x): the window with a place for every species first, then the most room, then the most central."""
        from numpy.lib.stride_tricks import sliding_window_view as win
        ys = [(h - MH) // 2] if centred[0] else range(0, h - MH + 1)
        xs = [(w - MW) // 2] if centred[1] else range(0, w - MW + 1)
        best = None
        cnts = {k: (win(K == k, (MH, MW)) & self.mask).sum(axis=(2, 3)) for k in (1, 2, 3)}
        for y in ys:
            for x in xs:
                s = 0.0
                for k, n in ((1, nland), (2, nwater)):
                    if n:
                        c = cnts[3 if self.stand_in[k] else k][y + pad, x + pad]
                        s += 10 * min(c, n) / n + min(c, 5 * n) / (5 * n)
                s -= 0.002 * (abs(x + MW / 2 - w / 2) + abs(y + MH / 2 - h / 2))
                if best is None or s > best[0]:
                    best = (s, y, x)
        return best[1], best[2]

    @staticmethod
    def _has(r, name):
        try:
            r.map_json(name)
            return True
        except Exception:
            return False

    def centre(self, x, y):
        """The icon's centre for the crop's metatile (x, y): its feet on the tile."""
        return PANEL[0] + x * 16 + 8, self.row_y[y] + 8 - 6

    @staticmethod
    def free(cx, cy):
        if not (PANEL[0] + 14 <= cx <= PANEL[2] - 14 and PANEL[1] + 12 <= cy <= PANEL[3] - 16):
            return False
        return not any(x0 - 14 <= cx <= x1 + 14 and y0 - 14 <= cy <= y1 + 14 for x0, y0, x1, y1 in AVOID)

    def kind_at(self, x, y):
        return int(self.kinds[y, x])

    def image(self):
        img = np.zeros((MH * 16, MW * 16, 3), np.uint8)
        for y in range(len(self.row_y)):
            top = self.row_y[y] - PANEL[1]
            for x in range(MW):
                tile = self.mr.render(int(self.blocks[y, x]) & 0x3FF)[..., :3]
                img[top:top + 16, x * 16:x * 16 + 16] = tile[:max(0, min(16, img.shape[0] - top))]
        v = np.round(img.astype(np.int32) * 31 / 255).astype(np.int32)
        img = ((v << 3) | (v >> 2)).astype(np.uint8)
        if self.divider is not None:            # the frame bar between the two views (the panel border's colours)
            top = self.divider - PANEL[1]
            for k, c in enumerate(DIVIDER_ROWS):
                img[top + k, :] = DA.c555(c)
        return img

    def places(self, n, k, taken):
        """(places, how many stand on the group's own tiles): n icon centres, farthest point from the others."""
        want = 3 if self.stand_in[k] else k
        cand, extra = [], []
        for y in range(len(self.row_y)):
            for x in range(MW):
                if not self.mask[y, x]:
                    continue
                kk = self.kind_at(x, y)
                c = self.centre(x, y)
                if kk == want:
                    cand.append(c)
                elif kk == 3:
                    extra.append(c)
        out, own = [], 0
        base = cand or extra
        if not base:
            return out, 0
        mean = (sum(c[0] for c in base) / len(base), sum(c[1] for c in base) / len(base))
        for _ in range(n):
            pool = [c for c in cand if c not in out and c not in taken]
            mine = bool(pool)
            if not pool:
                pool = sorted((c for c in extra if c not in out and c not in taken),
                              key=lambda c: min(((c[0] - b[0]) ** 2 + (c[1] - b[1]) ** 2 for b in cand), default=0))[:6]
            if not pool:
                break
            if not out and not taken:
                pick = min(pool, key=lambda c: (c[0] - mean[0]) ** 2 + (c[1] - mean[1]) ** 2)
            else:
                pick = max(pool, key=lambda c: min((c[0] - o[0]) ** 2 + (c[1] - o[1]) ** 2 for o in out + taken))
            out.append(pick)
            own += mine
        return out, own


# ---- the version's wild tables ----------------------------------------------------------------------------------
def map_of_files():
    """{a/1/2/7 file: the map its table belongs to} (data/hoenn_encounters.json, the version's overlay included); a file
    of several maps: the first."""
    enc = version.load_json(os.path.join(ROOT, 'data', 'hoenn_encounters.json'))
    out = {}
    for name, f in enc.items():
        if not name.startswith('_') and isinstance(f, int):
            out.setdefault(f, name)
    return out


def _table_counts(data):
    """(land species, water species) of an a/1/2/7 file, the most of its seasons (dexnav.c BuildList's rule: the grass
    group if its rate isn't 0, then surfing's; each species once)."""
    n = len(data) // ENC_TABLE
    land = water = 0
    for s in range(max(n, 1)):
        t = data[ENC_TABLE * s:ENC_TABLE * (s + 1)]
        if len(t) < ENC_TABLE:
            break
        def species(slots, rate):
            if not t[rate]:
                return set()
            return {struct.unpack_from('<H', t, 8 + 4 * k)[0] for k in slots} - {0}
        land = max(land, len({v & 0x7FF for v in species(GRASS_SLOTS, 0)}))
        water = max(water, len({v & 0x7FF for v in species(SURF_SLOTS, 3)}))
    return land, water


def counts_built(files):
    """{file: (land, water)} of the built a/1/2/7 for the version's wild files (post-game twins counted with theirs)."""
    import narcio
    enc = narcio.load(files, 127)
    twins = {}
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('pg_enc', os.path.join(HERE, 'patches', 'postgame_encounters.py'))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        twins = dict(m.pairs())
    except Exception as e:                       # (no post-game tables in this tree)
        print('dexnav_snapshots: no post-game twins:', str(e)[:80])
    out = {}
    for f in map_of_files():
        if f >= len(enc):
            continue
        l, w = _table_counts(enc[f])
        if f in twins and twins[f] < len(enc):
            l2, w2 = _table_counts(enc[twins[f]])
            l, w = max(l, l2), max(w, w2)
        out[f] = (min(l, MAX_LAND), min(w, MAX_WATER))
    return out


def counts_source():
    """{file: (land, water)} from the version's src/encounters/*.s (without a build; a post-game twin counts for its
    map's file)."""
    out = {}
    for p in version.overlay(os.path.join(ROOT, 'src', 'encounters'), '*.s'):
        head = open(p).read(600)
        m = re.search(r'encounter file (\d+)', head)
        if not m:
            continue
        f = int(m.group(1))
        twin = re.search(r'post-game twin \(encounter file \d+\) of \w+ \(file (\d+)\)', head)
        if twin:                                 # (counted with its map's file)
            f = int(twin.group(1))
        group, rates, sp = None, {}, {'Grass': set(), 'Surf': set()}
        for line in open(p):
            line = line.strip()
            r = re.match(r'EncounterRates (.*)', line)
            if r:
                rates = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', r.group(1))}
            g = re.match(r'(\w+)Encounters$', line)
            if g:
                group = g.group(1)
                continue
            e = re.match(r'Encounter (SPECIES_\w+),', line)
            if e and group in sp:
                sp[group].add(e.group(1))
        land = len(sp['Grass']) if rates.get('grass') else 0
        water = len(sp['Surf']) if rates.get('surf') else 0
        l0, w0 = out.get(f, (0, 0))
        out[f] = (max(l0, min(land, MAX_LAND)), max(w0, min(water, MAX_WATER)))
    return out


# ---- packing ------------------------------------------------------------------------------------------------------
def reduce_colours(tiles, line_limit):
    """Merge the nearest colours until the tiles fit line_limit lines (15 colours a tile and a line): (tiles, merges)."""
    merges = 0
    while True:
        lines = DA.Lines(line_limit)
        if all(len(c) <= 15 and lines.place(c) is not None for _, c in tiles.values()):
            return tiles, merges
        use = Counter(c for rows, _ in tiles.values() for row in rows for c in row if c is not None)
        cols = list(use)
        best = min(((sum((a - b) ** 2 for a, b in zip(cols[i], cols[j])), cols[i], cols[j])
                    for i in range(len(cols)) for j in range(i + 1, len(cols))))
        _, a, b = best
        keep, drop = (a, b) if use[a] >= use[b] else (b, a)
        tiles = {k: (tuple(tuple(keep if c == drop else c for c in row) for row in rows),
                     {keep if c == drop else c for c in cs}) for k, (rows, cs) in tiles.items()}
        merges += 1


def pack(img, land, water, char_base, line_base, flags=0):
    """(file bytes, report) of a panel picture (152 x 240 RGB) and its places."""
    lay = DA.layer(False)
    lay[PANEL[1]:PANEL[3], PANEL[0]:PANEL[2]] = img[:PANEL[3] - PANEL[1], :PANEL[2] - PANEL[0]]
    tiles = DA.tiles_of(lay, (1, 1, 31, 20))
    tiles, merges = reduce_colours(tiles, DA.ART_LINES - line_base)
    sheet = DA.Sheet(base=char_base, line_base=line_base)
    placed = sheet.add(tiles)
    entries = sheet.finish()
    m = [0] * (30 * 19)
    for (tx, ty), i in placed:
        m[(ty - 1) * 30 + tx - 1] = entries[i]
    places = list(land[:MAX_LAND]) + [(0, 0)] * (MAX_LAND - len(land[:MAX_LAND])) + \
        list(water[:MAX_WATER]) + [(0, 0)] * (MAX_WATER - len(water[:MAX_WATER]))
    HEADER = 60
    tile_bytes = sheet.tile_bytes()
    pal = b''.join(struct.pack('<16H', *[DA.A._rgb555(c) for c in line]) for line in sheet.palette())
    tiles_off = HEADER
    pal_off = tiles_off + len(tile_bytes)
    map_off = pal_off + len(pal)
    head = struct.pack('<IHHBBBB', SNAP_MAGIC, sheet.count, len(sheet.order), len(land[:MAX_LAND]),
                       len(water[:MAX_WATER]), flags, 0)
    head += bytes(v for p in places for v in p) + bytes(2) + struct.pack('<III', tiles_off, pal_off, map_off)
    assert len(head) == HEADER, len(head)
    data = head + tile_bytes + pal + struct.pack(f'<{len(m)}H', *m)
    return data, dict(tiles=sheet.count, lines=len(sheet.order), merges=merges, size=len(data))


def snapshot(name, nland, nwater):
    """(Area, land places, water places, own land, own water)."""
    a = Area(name, nland, nwater)
    land, own_l = a.places(MAX_LAND, 1, []) if nland else ([], 0)
    water, own_w = a.places(MAX_WATER, 2, land) if nwater else ([], 0)
    return a, land, water, own_l, own_w


def build(char_base, line_base, counts):
    """[(file, bytes, report)] of every table with a land or water group, and the no-wild panel's (file None, first);
    stops the build (SystemExit) on a table whose groups lack places on their own tiles."""
    out = []
    none, rep = pack(DA.none_panel(), [], [], char_base, line_base, flags=1)
    out.append((None, none, dict(rep, map='(no wild Pokémon)')))
    bad = []
    maps = map_of_files()
    for f in sorted(counts):
        nl, nw = counts[f]
        if not nl and not nw:
            continue
        name = maps[f]
        a, land, water, own_l, own_w = snapshot(name, nl, nw)
        short = [f'{kind}: {own} of {n} on its own tiles' for kind, own, n, k in
                 (('land', own_l, nl, 1), ('water', own_w, nw, 2)) if own < n and not a.stand_in[k]]
        if short:
            bad.append(f'{name} (file {f}, crop {a.bands}): ' + '; '.join(short))
        data, rep = pack(a.image(), land, water, char_base, line_base)
        out.append((f, data, dict(rep, map=name, land=nl, water=nw, crop=a.bands, own=(own_l, own_w),
                                  stand_in=[k for k, v in (('land', a.stand_in[1]), ('water', a.stand_in[2])) if v])))
    if bad:
        raise SystemExit('dexnav: these wild tables have too few places on their own tiles for their species '
                         '(data/dexnav_snapshots.json: a "crops" window, or a "stand_ins" group if the map has no such '
                         'tile):\n  ' + '\n  '.join(bad))
    return out


if __name__ == '__main__':
    counts = counts_source()
    print(version.NAME, len([c for c in counts.values() if any(c)]), 'tables with land or water species')
    for f, data, rep in build(83, 2, counts):
        print(f, rep)
