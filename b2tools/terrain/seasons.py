"""Black 2's seasonal ground decals and falling leaves on Hoenn's land (seasons2, user requests 2026-10-20: snow in
winter, autumn leaves; only for players who answered YES to Birch's seasons question, notes/SEASONS.md).

What Black 2 does (read from its own chunks and data, notes/SEASONS.md "Black 2's autumn and winter"):
  - Winter snow patches: `kisetu_yuki` decals (A5I3, 32x32: fully clear in its spring, summer and autumn sets, a soft
    snow blob in winter), one quad of one or two tiles square, flat 2 units over the ground, one image per quad, on
    about a tenth of the walkable ground of Route 6/7/19/20, Aspertia, Floccesy, Virbank, Driftveil, Mistralton, mostly
    at the foot of trees, ledges and fences (chunks 47-63, 279-296, 617-621). They are in the chunks all year; the
    season's texture set shows or hides them. kisetu_yuki is already in all four of area 2's sets (Hoenn's).
  - Autumn: Route 20's autumn chunks (a/0/1/0 season swaps 286-289 -> 290-293) add falling leaves: long thin ribbons
    of `54_ha01` (128x64, four rows of yellow leaves) across the chunk 40-80 units up, material `_ha01`, scrolled along
    the ribbon and stepped through the rows by Route 20's texture animation (a/0/6/8 file 47, area records 214-217:
    srt 47), plus leaf carpets (54ochiba01/b/c, walk-through piles: tile class 0x25, fldeff_ochiba). Black 2's flower
    decals (kisetu_hana) show fallen leaves in its autumn set.
Here (Hoenn): the same decals, placed by rule on Hoenn's grass and dirt paths (decals()), and Route 20's ribbons over
Hoenn's wooded cells (ribbons(); not in the warp-only maps, AREA2_ONLY). `_ha01` and `ochiba_h` (kisetu_hana's autumn leaves) are new names in Hoenn's sets:
the art in the autumn set, a clear 8x8 stand-in in the other three (patches/hoenn_textures.py SEASONAL); the autumn
area records get srt 47 (hoenn_textures autumn_leaves, standalone.seasonal_areas). With the seasons answer NO (always
summer) every decal draws nothing (clear texels are never drawn on the DS) and no tile's collision changes, so the
game plays and looks the same. Not copied: Black 2's walk-through leaf piles and snow footprints (tile classes 0x25
and 2) - a class is in the chunk all year and changes the battle terrain (GetTileEncountType 0x25 -> 17, 2 -> 2,
route floor 0x1f -> 0) in every season, also for players without seasons."""
import hashlib, os

CLASSES = set()
TEXTURES = {'kisetu_yuki': 3}                 # (Black 2's, already in area 2's four sets: merge keeps them as they are)
WRAP = {'kisetu_yuki': ('CLAMP', 'CLAMP'), 'ochiba_h': ('CLAMP', 'CLAMP'), '_ha01': ('WRAP', 'WRAP')}
# name -> (season it shows in: 0 spring .. 3 winter, Black 2 map texture set, texture there): renamed copies made by
# patches/hoenn_textures.py (clear in the other seasons)
SEASONAL = {'_ha01': (2, 216, '54_ha01'), 'ochiba_h': (2, 4, 'kisetu_hana')}
AREA2_ONLY = {'_ha01'}         # not in the warp-only maps' sets (patches/standalone.py: their texture VRAM; no ribbons
                               # there, world.py season_decals)

DECAL_Y = 2           # Black 2's (Route 6 chunk 53: y 2 over ground 0; Route 20: -54 over -56)
# maps without snow or leaves (Sapphire map names): the ash, the volcano, the hot springs, the tropical islands and the
# sea routes; the desert and the beaches are sand (no decals on sand anyway)
EXCLUDE = {'Route113', 'JaggedPass', 'MtChimney', 'FallarborTown', 'LavaridgeTown', 'SootopolisCity', 'MossdeepCity',
           'DewfordTown', 'PacifidlogTown', 'EverGrandeCity', 'SouthernIsland_Exterior', 'SouthernIsland_Interior',
           'FarawayIsland_Entrance', 'FarawayIsland_Interior', 'BirthIsland_Exterior', 'NavelRock_Exterior',
           'NavelRock_Top', 'SkyPillar_Outside', 'SkyPillar_Top', 'BattleFrontier_OutsideWest', 'BattleFrontier_OutsideEast',
           'BattleTower_Outside', 'Route105', 'Route106', 'Route107', 'Route108', 'Route109', 'Route122', 'Route124',
           'Route125', 'Route126', 'Route127', 'Route128', 'Route129', 'Route130', 'Route131', 'Route132', 'Route133',
           'Route134', 'MtPyre_Summit'}
GROUND = {'grass', 'path'}                    # plan classes that get decals (walkable)
NEAR_NOT = {'building', 'building_roof', 'door', 'sign', 'prop', 'sand_patch', 'flowers', 'bridge', 'stairs',
            'water_edge', 'cliff_top', 'long_grass', 'ash_grass', 'lava', 'puddle', 'bike_path', 'cave_entrance',
            'mountain'}   # their y 1-4 layers (a cave mouth's floor reaches 1 over the tile in front)
BLOCKERS = {'tree_top_l', 'tree_top_r', 'tree_bot', 'cut_tree', 'bush', 'fence', 'wall', 'rock', 'cliff', 'ledge_s',
            'ledge_e', 'ledge_w', 'ledge_n', 'ledge_cap', 'mountain'}
TREES = {'tree_top_l', 'tree_top_r', 'tree_bot', 'tree_tip', 'cut_tree'}
P_SNOW = (0.07, 0.30, 0.45)     # chance of a snow tile by its blocked neighbours (0, 1, 2+): about Black 2's tenth
P_LEAF = 0.30                   # chance of a leaf tile next to a tree
RIBBON_MIN_TREES = 140          # tree tiles in a cell (of 1024) for falling leaves (Route 20's chunks: 180-420)
RIBBON_LOW, RIBBON_SPAN = 60, 40   # ribbon heights over the cell's highest ground (Route 20: mostly 40-80 up)

def _rnd(*k):
    return int.from_bytes(hashlib.md5(repr(k).encode()).digest()[:4], 'little') / 2 ** 32

def draw(m, cell):
    return None                 # (world.py build_cell calls decals() and ribbons() with what they need)

def decals(m, cell, ok, near_tree, blocked_n, used=None):
    """Snow (kisetu_yuki) and leaf (ochiba_h) decals on one cell, at ground level (world.py lifts them by the tiles'
    heights). ok(tx, tz): a level, plain grass or path tile with nothing else drawn on it or beside it (world.py);
    near_tree(tx, tz): a tree within one tile; blocked_n(tx, tz): blocked neighbours (8). Leaves go next to trees
    (one tile each, one of kisetu_hana's four clusters, as Black 2's flower decals), snow elsewhere too (one or two
    tiles square, as Black 2's). Returns (snow tiles, leaf tiles)."""
    used = set() if used is None else used
    leaf = []
    X, Z = cell.X, cell.Z
    for tz in range(32):
        for tx in range(32):
            if (tx, tz) in used or not ok(tx, tz) or not near_tree(tx, tz): continue
            if _rnd('leaf', X + tx, Z + tz) >= P_LEAF: continue
            q = int(_rnd('leafq', X + tx, Z + tz) * 4)                 # which of the four 16x16 clusters
            u0, v0 = (q & 1) * 0.5, (q >> 1) * 0.5
            x0, x1, z0, z1 = cell.bc.ux(tx), cell.bc.ux(tx + 1), cell.bc.uz(tz), cell.bc.uz(tz + 1)
            m.quad('ochiba_h', [(x0, DECAL_Y, z1, u0, v0), (x1, DECAL_Y, z1, u0 + 0.5, v0),
                                (x1, DECAL_Y, z0, u0 + 0.5, v0 + 0.5), (x0, DECAL_Y, z0, u0, v0 + 0.5)])
            used.add((tx, tz)); leaf.append((tx, tz))
    snow = []
    for tz in range(32):
        for tx in range(32):
            if (tx, tz) in used or not ok(tx, tz): continue
            n = min(blocked_n(tx, tz), 2)
            if _rnd('snow', X + tx, Z + tz) >= P_SNOW[n]: continue
            sq = [(tx + dx, tz + dz) for dx in (0, 1) for dz in (0, 1)]
            big = (tx < 31 and tz < 31 and _rnd('snow2', X + tx, Z + tz) < 0.45
                   and all(t not in used and ok(*t) for t in sq))
            w = 2 if big else 1
            cell.bc.flat_decal(m, 'kisetu_yuki', tx, tz, w, w, DECAL_Y)
            for t in (sq if big else [(tx, tz)]): used.add(t); snow.append(t)
    return snow, leaf

# Route 20's falling leaves (Black 2 chunks 290-293, autumn): every _ha01 ribbon as (x, y over the chunk's ground, z,
# u, v) corners of its two triangles (data/season_ribbons.json, read from the chunks with apicula; ground = the median
# height of the chunk's grass). One of the four per wooded Hoenn cell (by its position).
_RIBBONS = None

def _ribbon_templates():
    global _RIBBONS
    if _RIBBONS is None:
        import json
        _RIBBONS = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'season_ribbons.json')))['chunks']
    return _RIBBONS

def _clip(poly, k, lim, keep_below):
    """Sutherland-Hodgman: the part of convex polygon poly (x, y, z, u, v corners) with coordinate k <= lim (or >=)."""
    inside = (lambda p: p[k] <= lim) if keep_below else (lambda p: p[k] >= lim)
    out = []
    for i, cur in enumerate(poly):
        prev = poly[i - 1]
        if inside(cur):
            if not inside(prev):
                f = (lim - prev[k]) / (cur[k] - prev[k]); out.append(tuple(a + (b - a) * f for a, b in zip(prev, cur)))
            out.append(cur)
        elif inside(prev):
            f = (lim - prev[k]) / (cur[k] - prev[k]); out.append(tuple(a + (b - a) * f for a, b in zip(prev, cur)))
    return out

def ribbons(tm, cell, top_y, n_trees):
    """Route 20's falling-leaf ribbons over a wooded cell (n_trees tree tiles, at least RIBBON_MIN_TREES): the template's
    each ribbon level at its own height, RIBBON_LOW..RIBBON_LOW + RIBBON_SPAN over top_y (the highest walkable or tree tile
    of the cell) in even steps (4-5 units: Route 20's sloping ribbons cross each other, here two never come closer than
    that), clear of every tree (canopy 23, top 46, cards 56: build_chunk), and cut at the cell's edges (Route 20's
    ribbons reach 40 units into the next chunk: here a neighbour's would cross them). Added to the trees' model (already at
    their heights). Returns the number of ribbon quads."""
    if n_trees < RIBBON_MIN_TREES: return 0
    temps = _ribbon_templates()
    t = temps[(cell.cx * 3 + cell.cz * 5) % len(temps)]
    n = len(t['tris']) // 2                     # (two triangles a ribbon)
    for i, tri in enumerate(t['tris']):
        y = top_y + RIBBON_LOW + (i // 2) * RIBBON_SPAN / max(1, n - 1)
        poly = [(x, y, z, u, v) for x, _, z, u, v in tri]
        for k in (0, 2):
            poly = _clip(poly, k, 256, True)
            poly = _clip(poly, k, -256, False) if poly else poly
        for j in range(1, len(poly) - 1):
            tm.tri('_ha01', [poly[0], poly[j], poly[j + 1]])
    return len(t['tris']) // 2
