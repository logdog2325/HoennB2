"""Shallow water and sliding ice for the cave builder (caves_misc agent, 2026-10-06; notes/CAVES.md "Shoal Cave: tides,
shallow water, ice"). Called from b2tools/models_cave.py at three hooks (end of Cave.classify, Cave.build_terrain,
cave_collision); every feature is switched on by its own recipe key, so recipes without them build exactly as before.

Recipe keys (data/cave_layouts/<Map>.json):
  shoals  true: Sapphire's shallow water (MB_SHALLOW_WATER 0x17, MB_SHOAL_CAVE_ENTRANCE 0x1C: walkable, splashing)
          -> Black 2's shoal cells: class 0x17, flags 0x10 (Undella Bay chunk 247, Route 13 86/87/90: the wading
          ripple, notes/TERRAIN_WATER.md) [bytes][test on Route 124], here SHOAL_DEPTH units below the tile's floor
          height. Black 2's caves have no shallow-water art: the bottom is the look's floor texture darkened
          ("shoal_color"), with the look's sparkle layer ("water_top", Wellspring's d0_miz2) 2 units above it and the
          look's bank texture ("water_bank") on every edge to a tile that is not a shoal.
  ice     true: MB_ICE (0x20, Sapphire slides you until something stops you) -> Black 2's sliding ice: class 0x18,
          flags 0x80 (IsTileSlidingIce, ov036 0x021a2c48: classes 0x10 / 0x18 make FieldPlayerGrid_GetConstMoveType
          slide the player; Icirrus City zone 114, chunks 865/944/945, uses 0x18/0x80) [code][bytes], drawn with the
          look's "ice" texture ("ice_size" units per repeat) instead of its floor.
The tile keeps its Sapphire walkability and floor height (the rock still rises from it); only its cell and its floor
drawing change.
"""
from collections import defaultdict

SHOAL = {0x17, 0x1C}
MB_ICE = 0x20
SHOAL_DEPTH = 4
KEYS = ('shoals', 'ice')
STEP = {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}

def active(r):
    return any(r.get(k) for k in KEYS)

# ------------------------------------------------------------------------------------------------ classify hook
def classify(c):
    """Walkable floor tiles with Sapphire's shallow-water / ice behaviours (after levels, ramps and walls)."""
    c.shoal, c.ice = set(), set()
    for (x, z) in sorted(c.fy):
        if c.kind[z][x] != 'floor' or not c.sm['walk'][z][x] or (x, z) in c.ramps: continue
        b = c.sm['beh'][z][x]
        if c.r.get('shoals') and b in SHOAL: c.shoal.add((x, z))
        elif c.r.get('ice') and b == MB_ICE: c.ice.add((x, z))
    for t in sorted(c.shoal | c.ice):
        if c.level_walls.get(t) or c.wall_dirs.get(t):
            c.notes.append(f'{t}: shoal/ice tile with side walls (its walls are dropped)')

def own_floor(c):
    """Tiles whose floor this module draws (models_cave leaves them out of its floor rectangles and decals)."""
    return getattr(c, 'shoal', set()) | getattr(c, 'ice', set())

# ------------------------------------------------------------------------------------------------ geometry hook
def geometry(c):
    from models_cave import rects
    L = c.look
    C = lambda v: v - 256
    def flat(tex, tiles_by_y, size, color=1.0, dy=0.0):
        for y, tiles in tiles_by_y.items():
            for x0, z0, x1, z1 in rects(tiles):
                X0, X1, Z0, Z1 = c.lx(x0), c.lx(x1 + 1), c.lz(z0), c.lz(z1 + 1)
                c.m.quad(tex, [(C(X0), y + dy, C(Z1), X0 / size, -Z1 / size), (C(X1), y + dy, C(Z1), X1 / size, -Z1 / size),
                               (C(X1), y + dy, C(Z0), X1 / size, -Z0 / size), (C(X0), y + dy, C(Z0), X0 / size, -Z0 / size)],
                         color=(color,) * 3)
    if c.ice:
        assert L.get('ice'), f'{c.name}: look {c.look_name} has no "ice" texture'
        by = defaultdict(set)
        for t in c.ice: by[c.fy[t]].add(t)
        flat(L['ice'], by, L.get('ice_size', 64), L.get('ice_color', 1.0))
    if c.shoal:
        by = defaultdict(set)
        for t in c.shoal: by[c.fy[t]].add(t)
        flat(L.get('shoal_floor', L['floor']), by, L.get('floor_size', 64), L.get('shoal_color', 0.8), -SHOAL_DEPTH)
        if L.get('water_top'): flat(L['water_top'], by, 16, 1.0, -SHOAL_DEPTH + 2)
        bank = L.get('water_bank') or L['face_mid']
        for (x, z) in sorted(c.shoal):
            top = c.fy[(x, z)]
            for dx, dz in STEP.values():
                n = (x + dx, z + dz)
                if n in c.shoal: continue
                if dx: p = ((c.lx(x + (dx > 0)), c.lz(z)), (c.lx(x + (dx > 0)), c.lz(z + 1)))
                else: p = ((c.lx(x), c.lz(z + (dz > 0))), (c.lx(x + 1), c.lz(z + (dz > 0))))
                c.vwall(bank, p[0], p[1], top - SHOAL_DEPTH, max(top, c.fy.get(n, top)) if n in c.fy and c.kind[n[1]][n[0]] != 'water' else top,
                        0.77, 1.0)

def approach_y(c, t, y):
    """Height of a warp/trigger whose approach tile is t (y = that tile's floor): a shoal is walked SHOAL_DEPTH below
    its floor (Black 2 fires a warp/trigger only within 2 units of its y: CheckWarpPositionMatch, eventdata_system.c;
    Shoal Cave's exit arch at y 0 never fired from the shoal at -4.4)."""
    return y - SHOAL_DEPTH if t in getattr(c, 'shoal', ()) else y

# ------------------------------------------------------------------------------------------------ collision hook
def collision(c, cells, flat_record):
    """Shoal / ice cells (zone tile -> (a, height index, class, flags)), after models_cave filled the walkable ones."""
    for t in sorted(getattr(c, 'shoal', ())):
        z = (c.ox + t[0], c.oz + t[1])
        if z in cells: cells[z] = (0, flat_record(c.fy[t] - SHOAL_DEPTH), 0x17, 0x10)
    for t in sorted(getattr(c, 'ice', ())):
        z = (c.ox + t[0], c.oz + t[1])
        if z in cells: cells[z] = (0, flat_record(c.fy[t]), 0x18, 0x80)
