"""Ground terrain module: sand, ash grass, long grass, Cycling Road, bridges, fences, walls, bushes, rocks, props and
Hoenn's special props, each built the way Black 2 builds the closest thing it has (evidence: notes/TERRAIN_GROUND.md).

Interface: b2tools/terrain/__init__.py (CLASSES, TEXTURES, WRAP, draw, collision) plus two hooks that other code has
to call (notes/TERRAIN_GROUND.md, "Integration"): placements(cell), Black 2 building models from pack 0 placed as props
(Route 109's parasols), and water_under(world, wx, wz), which tells the water module which bridge/Cycling Road tiles
stand over water so it draws the water under them.

Units: chunk model units, 16 per tile, tile t spans t*16-256 .. t*16-240; y up; +z south (towards the camera).
UVs follow the Blender/OpenGL convention the existing recipes use (v = 0 at the bottom of an image).
"""
import math, sys
import numpy as np

# ------------------------------------------------------------------------------------------------- classes, textures
OTHER = ['berry_soil', 'market_awning', 'beach_umbrella', 'beach_chair', 'beach_mat', 'big_tree', 'tree_top_1wide',
         'archway', 'acro_bike_rail', 'acro_bike_rail_support', 'acro_bike_stepping_stone', 'forest_entrance',
         'bridge_support']
CLASSES = {'sand', 'ash_grass', 'long_grass', 'bike_path', 'bridge', 'fence', 'wall', 'bush', 'rock', 'prop'} | \
          {'other:' + o for o in OTHER}

# name -> Black 2 map texture set (a/0/1/4) it is copied from. Set 3 (area 2 summer) is Hoenn's base set, so those
# entries add nothing; they are listed so world.py writes their palette pairs for ToNsbmd. The three from other sets
# add 2.7 KB (hoenn_textures prints the total).
TEXTURES = {
    'nagakusa01a': 39, 'nagakusa01b': 39,        # Route 7 summer (chunks 60-62): Black 2's very tall grass, top/sides
    'c8k_grass01ax': 267,                        # frozen Opelucid (chunks 352-359): grey-green grass, for ash
    'sabaku01': 22,                              # Route 4 summer (chunks 29-37): desert sand, for Route 111
    'sea_jimen': 3, 'iwa01': 3, 'hashi01a': 3, 'hashi02a': 3, 'plant01': 3, 'saku01a': 3, 't2_saku01': 3,
    't02_kabe01': 3, 't02michi_b': 3, 't02michi_c': 3, 't02_ki_sita': 3, 'nagaisu': 3, 'ki03ax': 3, 'ki03bx': 3, 'ki03dx': 3,
    'ki02c': 3, 'kusa_ec1': 3, 'kusa_ec2': 3, 'kusa_ec3': 3, 'kusa_ec1s': 3, 'kusa_ec2s': 3,
    # Black 2's rocks (overworld_polish 2026-10-08): the images of its rock models rock_01/02 and searock_01/02, which
    # are in every exterior building texture set (a/1/7/4; 32x32, 16 colours, colour 0 clear): 'ext46' as terrain/ship.py
    'rock01': 'ext46', 'searock1.1': 'ext46',
}
WRAP = {'nagakusa01b': ('WRAP', 'CLAMP'), 't02_ki_sita': ('CLAMP', 'CLAMP'), 'kusa_ec1s': ('WRAP', 'CLAMP'),
        'kusa_ec2s': ('WRAP', 'CLAMP'), 'rock01': ('CLAMP', 'CLAMP'), 'searock1.1': ('CLAMP', 'CLAMP')}
# Hoenn's long grass: 'nagakusa' = Black 2's own very tall grass (Route 7: a raised mat that hides the player's legs,
# like Sapphire's long grass); 'dark' = Black 2's dark (double-battle) grass, Route 1's tall-grass layers in kusa_ec1s/
# kusa_ec2s (Route 22 chunk 302; no extra texture bytes). HOENN_LONG_GRASS=dark switches.
import os as _os
LONG_GRASS = _os.environ.get('HOENN_LONG_GRASS', 'nagakusa')
BEACH_PROPS = ('other:beach_umbrella', 'other:beach_chair', 'other:beach_mat')   # on Route 109's sand
DESERT_MAPS = {'Route111'}     # sand drawn as Black 2's desert (sabaku01) with Route 4's sand collision
ROCKS = _os.environ.get('HOENN_ROCKS', 'cards')     # 'cards' = Black 2's rock models' cards (draw_rocks); 'iwa' = iwa01 boulders

T, HALF = 16, 256
def X(t): return t * T - HALF
def Z(t): return t * T - HALF

WATER = {'water', 'deep_water', 'current_n', 'current_s', 'current_e', 'current_w', 'waterfall', 'water_edge',
         'puddle', 'seaweed'}
SURFACE = {'water', 'deep_water', 'current_n', 'current_s', 'current_e', 'current_w', 'waterfall'}   # surfable

# collision records (inclination, height index, class, flags); height index 3 = y 0, as build_chunk.py. Values are
# read from Black 2's own .per sections (notes/TERRAIN_GROUND.md has the per-chunk counts).
SOLID = (0, 3, 0x0001, 0x0081)
FLOOR = (0, 3, 0x0000, 0x0080)        # plain floor: town floor (Nuvema), Route 8 bridge (chunk 69), Route 14 bridge (95)
ROUTE = (0, 3, 0x001F, 0x0080)        # route floor (Route 1)
TALL_GRASS = (0, 3, 0x0004, 0x0024)   # Route 1 tall grass (single battles, encounters)
BEACH = (0, 3, 0x0019, 0x0088)        # beach sand: Undella (chunks 93/94), Route 13 (87), Humilau/Route 22 (300/302)
DESERT_SAND = (0, 3, 0x000B, 0x0088)  # Route 4 sand (chunks 32, 35)
DEEP_SAND = (0, 3, 0x000C, 0x000C)    # Route 4 deep sand (chunks 32, 35), flags 0x04 like tall grass's 0x24
SAND_PATH = (0, 3, 0x0003, 0x0080)    # route sand path (Route 1); also Route 3's wooden bridge deck (chunks 15/16)

# fences: Black 2's white wooden fence (saku01a, Route 1/3) on routes and towns, Accumula's metal railing (t2_saku01)
# in cities and along the Cycling Road
METAL_FENCE_MAPS = {'RustboroCity', 'SlateportCity', 'LilycoveCity', 'MauvilleCity', 'MossdeepCity', 'SootopolisCity',
                    'EverGrandeCity', 'BattleTower_Outside', 'SouthernIsland_Exterior', 'MtChimney'}

# ----------------------------------------------------------------------------------------------------- geometry helpers
def _cross(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    return (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)

def face(m, mat, verts, normal):
    """Quad or triangle whose winding makes its face normal point along `normal` (the side that faces the camera)."""
    n = _cross(verts[0], verts[1], verts[2])
    if n[0] * normal[0] + n[1] * normal[1] + n[2] * normal[2] < 0: verts = verts[::-1]
    (m.quad if len(verts) == 4 else m.tri)(mat, verts)

def both(m, mat, verts):
    """Thin vertical plane seen from either side (Black 2's fences are single planes)."""
    m.quad(mat, verts); m.quad(mat, verts[::-1])

UP, SOUTH, NORTH, EAST, WEST = (0, 1, 0), (0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0)

def flat(m, mat, x0, z0, x1, z1, y, uv=None):
    """Horizontal quad; uv(x, z) -> (u, v) per corner (default: one repeat per tile, u = x, v = -z in tiles)."""
    uv = uv or (lambda x, z: (x / T, -z / T))
    face(m, mat, [(x0, y, z1, *uv(x0, z1)), (x1, y, z1, *uv(x1, z1)), (x1, y, z0, *uv(x1, z0)), (x0, y, z0, *uv(x0, z0))], UP)

def runs(xs):
    xs = sorted(xs); out = []
    for x in xs:
        if out and x == out[-1][1] + 1: out[-1][1] = x
        else: out.append([x, x])
    return out

# ------------------------------------------------------------------------------------------------------- cell context
class Ctx:
    def __init__(self, cell):
        self.cell = cell
    def cls(self, tx, tz):
        e = self.cell.get(tx, tz)
        return e[1] if e else None
    def walk(self, tx, tz):
        e = self.cell.get(tx, tz)
        return bool(e and e[2])
    def map(self, tx, tz):
        e = self.cell.get(tx, tz)
        return e[0] if e else None
    def tiles(self, c):
        return [(tx, tz) for tz in range(32) for tx in range(32) if self.cls(tx, tz) == c]

# ---------------------------------------------------------------------------------------------------------- recipes
def draw_sand(m, k):
    """Sand as a flat ground plane repeating once per tile (u = x, v = -z), just above the grass sheet like paths:
    sea_jimen, Black 2's beach ground (Nuvema chunk 0, Route 13 chunk 87, Undella chunks 93/94), except Route 111's
    desert, which gets sabaku01, Black 2's desert floor (Route 4 / Desert Resort chunks 29-37). Route 109's beach
    umbrellas, chairs and mats stand on the same sand."""
    rows = {}
    under = sand_under(k.cell.world)
    for tx, tz in [t for c in ('sand',) + BEACH_PROPS for t in k.tiles(c)] + \
                  [(tx, tz) for tz in range(32) for tx in range(32) if (k.cell.X + tx, k.cell.Z + tz) in under]:
        mat = 'sabaku01' if k.map(tx, tz) in DESERT_MAPS else 'sea_jimen'
        rows.setdefault((tz, mat), []).append(tx)
    for (tz, mat), xs in rows.items():     # y 0 in the ground's place (ground_cover): 0.5 over it flickered
        for a, b in runs(xs): flat(m, mat, X(a), Z(tz), X(b + 1), Z(tz + 1), 0)

# Sand under what stands on sand (overworld_polish 2026-10-08): Dewford's houses, Gym and trees and Route 109's Seashore
# House stood on squares of grass in a sand town (world.py draws grass under every tile no module covers). Sapphire's
# buildings, trees and rocks there stand on its beach sand. A building / roof / door / sign tile gets sand when sand is
# the most common ground in the 5x5 tiles round it; a tree or rock tile when its own Sapphire metatile shows sand round
# the trunk or rock (>= 12 sand-coloured pixels: Dewford's trees 22-52, Route 104's 0).
UNDER_BY_NEIGHBOURS = {'building', 'building_roof', 'door', 'sign'}
UNDER_BY_PIXELS = {'tree_bot', 'tree_tip', 'tree_top_l', 'tree_top_r', 'rock'}
GROUNDS = {'grass', 'tall_grass', 'flowers', 'long_grass', 'ash_grass', 'bike_path', 'stairs'}
_UNDER = {}
def ground_under(world):
    """World tile -> 'sand' or 'path' for buildings, trees and rocks that stand on sand or on a town's path ground
    (cached per world dict). Buildings take the most common ground of the 5x5 tiles round them (sand, path, or grass:
    left to world.py), the inner tiles of a footprint the ground of the footprint tiles next to them; trees and rocks
    sand when their own Sapphire metatile shows sand round them."""
    if id(world) in _UNDER: return _UNDER[id(world)]
    sandy = set(('sand',) + BEACH_PROPS)
    out = {}
    for (wx, wz), e in world.items():
        if e[1] in UNDER_BY_NEIGHBOURS:
            n = {'sand': 0, 'path': 0, 'grass': 0, 'deck': 0}
            wet = 0
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    c = (world.get((wx + dx, wz + dz)) or (None, None))[1]
                    if c in sandy: n['sand'] += 1
                    elif c == 'path': n['path'] += 1
                    elif c in GROUNDS: n['grass'] += 1
                    elif c in DECKS: n['deck'] += 1
                    wet += c in SURFACE
            if wet < 5: n['deck'] = 0      # (decks only out on the water: Pacifidlog, not Fortree's walkways in the trees)
            best = max(n, key=n.get)
            if best != 'grass' and n[best] >= 3 and n[best] > n['grass']: out[(wx, wz)] = best
        elif e[1] in UNDER_BY_PIXELS:
            if e[1] == 'rock' and not any((world.get(n) or (0, 0, 0))[2] and world[n][1] not in WATER for n in
                                          ((wx + 1, wz), (wx - 1, wz), (wx, wz + 1), (wx, wz - 1))):
                continue            # (a rock in the sea: water.py draws the water under it)
            px = sapphire_pixels(e[0], wx, wz)
            if px is not None and ((px[:, 0] > 190) & (px[:, 1] > 160) & (px[:, 2] < 190) & (px[:, 0] >= px[:, 1]) &
                                   (px[:, 1] - px[:, 2] > 50)).sum() >= 12:
                out[(wx, wz)] = 'sand'
    # (dewford_fix 2026-10-12) the rock at a cave mouth's foot that lies at the ground's level (the door row beside the
    # opening, under terrain/cave_mouth.py's frame, and the row beside the approach tile) takes the approach's sand:
    # world.py's grass showed there as green strips round Granite Cave's mouth on Route 106's beach
    H = sys.modules.get('terrain.heights'); F = getattr(H, 'FIELD', None) if H else None
    if F is not None:
        from . import cave_mouth as cm
        for x, y in cm.find(world):
            ap = (x, y + 1)
            if (world.get(ap) or (0, 0))[1] not in sandy: continue
            for dx in range(-cm.SPAN, cm.SPAN + 1):
                for k in ((x + dx, y), (x + dx, y + 1)):
                    e = world.get(k)
                    if e and not e[2] and e[1] in ('cliff', 'cliff_top', 'mountain') and F.y(*k) == F.y(*ap):
                        out[k] = 'sand'
            # (emerald_polish_outdoor 2026-10-12, v16.7) the door tile too: Black 2's mouth floor (cave_mouth.py, doukutu01's
            # light front edge) has transparent notches, and the door tile's ground under them was grass: a green edge
            # at the front of every mouth on sand (Route 111's Desert Ruins, Granite Cave on Route 106's beach)
            if F.y(x, y) == F.y(*ap): out[(x, y)] = 'sand'
    for _ in range(4):          # (a building's inner tiles: next to a footprint tile with a ground, no other ground)
        for (wx, wz), e in world.items():
            if e[1] not in UNDER_BY_NEIGHBOURS or (wx, wz) in out: continue
            nb = [(wx + 1, wz), (wx - 1, wz), (wx, wz + 1), (wx, wz - 1)]
            if any((world.get(n) or (None, None))[1] in GROUNDS for n in nb): continue
            g = [out[n] for n in nb if n in out and world[n][1] in UNDER_BY_NEIGHBOURS]
            if g: out[(wx, wz)] = g[0]
    _UNDER.clear(); _UNDER[id(world)] = out
    return out

_UNDER_SETS = {}
def _under_set(world, kind):
    key = (id(world), kind)
    if key not in _UNDER_SETS:
        if len(_UNDER_SETS) > 12: _UNDER_SETS.clear()
        _UNDER_SETS[key] = {k for k, v in ground_under(world).items() if v == kind}
    return _UNDER_SETS[key]

def sand_under(world):
    """World tiles of buildings, trees and rocks that stand on sand (draw_sand lays it), and the forest round a town
    whose trees stand on sand (ring_sand)."""
    key = (id(world), 'sand+ring')
    if key not in _UNDER_SETS: _UNDER_SETS[key] = _under_set(world, 'sand') | ring_sand(world)
    return _UNDER_SETS[key]

# the forest outside the maps round a town whose edge trees stand on sand (Dewford's south and east rings of trees: the
# map's trees on sand, the ring's on grass, a straight line between them) stands on sand too, out to RING tiles
RING_SAND_MAPS, RING = {'DewfordTown'}, 4
_RING = {}
def ring_sand(world):
    if id(world) in _RING: return _RING[id(world)]
    wm = sys.modules.get('terrain.water')
    base = _under_set(world, 'sand')
    out = set()
    for (wx, wz) in base:
        if world[(wx, wz)][0] not in RING_SAND_MAPS or not world[(wx, wz)][1].startswith('tree'): continue
        for dx in range(-RING, RING + 1):
            for dz in range(-RING, RING + 1):
                k = (wx + dx, wz + dz)
                if k in world or k in out: continue
                if wm is not None and wm.filler(world, *k): continue          # (the sea round the island)
                out.add(k)
    _RING.clear(); _RING[id(world)] = out
    return out

def deck_under(world):
    """World tiles of buildings that stand on decks over the water (Pacifidlog's houses on its log walkways, Sapphire's
    rafts: Black 2's Humilau stands its houses on its wooden walkways): drawn as deck (draw_decks), water under them."""
    return _under_set(world, 'deck')

def path_under(world):
    """World tiles of buildings that stand on a town's path ground (world.py draws them as path tiles)."""
    return _under_set(world, 'path')

def sandy_tile(world, wx, wz, need=96):
    """Sapphire draws this tile mostly as beach sand (>= `need` of its 256 pixels sand-coloured): Route 127's / 124's /
    125's shallows round their rocks are sand-coloured flats in Sapphire."""
    e = world.get((wx, wz))
    px = sapphire_pixels(e[0], wx, wz) if e else None
    return px is not None and int(((px[:, 0] > 190) & (px[:, 1] > 160) & (px[:, 2] < 190) & (px[:, 0] >= px[:, 1]) &
                                   (px[:, 1] - px[:, 2] > 50)).sum()) >= need

def sapphire_pixels(name, wx, wz):
    """RGB pixels (256 x 3) of Sapphire's metatile at world tile (wx, wz) of map `name`, or None."""
    if sapphire_behaviour(name, wx, wz) is None: return None      # (loads the map's grid; None outside it)
    if ('px', name) not in _SAP:
        from gba import MetatileRenderer
        r = _SAP['repo']; l = r.layout_grid(r.map_json(name)['layout'])[1]
        _SAP[('px', name)] = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
    g, _ = _SAP[name]
    ox, oz = _SAP['origins'][name]
    x, y = wx - ox, wz - oz
    if y < 0: y = y % 2
    return _SAP[('px', name)].render(int(g[y, x]) & 0x3FF)[..., :3].reshape(-1, 3).astype(int)

def draw_ash(m, k):
    """Ash-covered tall grass (Route 113, Jagged Pass; Sapphire MB_ASHGRASS has wild encounters). Black 2 has no ash:
    the ground under it is frozen Opelucid's pale grass (c8k_grass01ax, 64x64, repeating every 4 tiles like
    grass01ax), with Route 1's tall grass on top (build_chunk.tall_grass_run)."""
    rows = {}
    for tx, tz in k.tiles('ash_grass'): rows.setdefault(tz, []).append(tx)
    for tz, xs in rows.items():
        for a, b in runs(xs):
            flat(m, 'c8k_grass01ax', X(a), Z(tz), X(b + 1), Z(tz + 1), 0, lambda x, z: ((x + HALF) / 64, -(z + HALF) / 64))
            k.cell.bc.tall_grass_run(m, a, b, tz)

def draw_dark_grass(m, k):
    """LONG_GRASS = 'dark': Black 2's dark (double-battle) grass, Route 22 chunk 302: Route 1's three tall-grass layers
    with the dark leaves, kusa_ec3 at y 2, kusa_ec2s at y 6, kusa_ec1s at y 9, nudged 2 units south."""
    rows = {}
    for tx, tz in k.tiles('long_grass'): rows.setdefault(tz, []).append(tx)
    for tz, xs in rows.items():
        for a, b in runs(xs):
            for mat, y in (('kusa_ec3', 2), ('kusa_ec2s', 6), ('kusa_ec1s', 9)):
                n = b + 1 - a
                face(m, mat, [(X(a), y, Z(tz + 1) + 2, 0, 0), (X(b + 1), y, Z(tz + 1) + 2, n, 0),
                              (X(b + 1), y, Z(tz) + 2, n, 1), (X(a), y, Z(tz) + 2, 0, 1)], UP)

def draw_long_grass(m, k):
    """Hoenn's long grass (Route 119/120) as Black 2's very tall grass (Route 7, chunk 60): a raised mat of grass whose top
    (nagakusa01a) is at y 16, inset 4 units on the west/east borders and 7.5 on the north border; its sides
    (nagakusa01b, v 0..0.5) slope from y 2 at the tile edge to the top (north/west/east) or stand vertical (south),
    and a fringe of blades (v 0.5..1) rises 8 more units: leaning out on the north, in on the south, upright W/E."""
    LG = lambda tx, tz: k.cls(tx, tz) == 'long_grass'
    H0, H1, H2 = 2, 16, 24
    IW, IN = 4, 7.5
    tiles = k.tiles('long_grass')
    rows = {}
    for tx, tz in tiles: rows.setdefault(tz, []).append(tx)
    for tz, xs in rows.items():
        for a, b in runs(xs):
            xa = X(a) + (IW if not LG(a - 1, tz) else 0); xb = X(b + 1) - (IW if not LG(b + 1, tz) else 0)
            # top, split where the north border changes
            seg = []
            for tx in range(a, b + 1):
                nb = not LG(tx, tz - 1)
                if seg and seg[-1][2] == nb: seg[-1][1] = tx
                else: seg.append([tx, tx, nb])
            for s0, s1, nb in seg:
                x0 = max(X(s0), xa); x1 = min(X(s1 + 1), xb); z0 = Z(tz) + (IN if nb else 0)
                flat(m, 'nagakusa01a', x0, z0, x1, Z(tz + 1), H1)
                if nb:      # north slope + leaning fringe
                    xs0, xs1 = X(s0), X(s1 + 1)
                    face(m, 'nagakusa01b', [(xs0, H0, Z(tz), 0, 0), (xs1, H0, Z(tz), (xs1 - xs0) / T, 0),
                                            (x1, H1, z0, (x1 - xs0) / T, 0.5), (x0, H1, z0, (x0 - xs0) / T, 0.5)], (0, 1, -1))
                    face(m, 'nagakusa01b', [(x0, H1, z0, 0, 0.5), (x1, H1, z0, (x1 - x0) / T, 0.5),
                                            (x1, H2, z0 - 3.5, (x1 - x0) / T, 1), (x0, H2, z0 - 3.5, 0, 1)], SOUTH)
            # south face + fringe where the tile below is not long grass
            sb = [tx for tx in range(a, b + 1) if not LG(tx, tz + 1)]
            for s0, s1 in runs(sb) if sb else []:
                x0 = max(X(s0), xa); x1 = min(X(s1 + 1), xb); xb0, xb1 = X(s0), X(s1 + 1); z1 = Z(tz + 1)
                face(m, 'nagakusa01b', [(xb0, H0, z1, 0, 0), (xb1, H0, z1, (xb1 - xb0) / T, 0),
                                        (x1, H1, z1, (x1 - xb0) / T, 0.5), (x0, H1, z1, (x0 - xb0) / T, 0.5)], SOUTH)
                face(m, 'nagakusa01b', [(x0, H1, z1, 0, 0.5), (x1, H1, z1, (x1 - x0) / T, 0.5),
                                        (x1, H2, z1 - 4, (x1 - x0) / T, 1), (x0, H2, z1 - 4, 0, 1)], SOUTH)
    # west / east slopes + upright fringe, per column run
    for side, dx in (('W', -1), ('E', 1)):
        cols = {}
        for tx, tz in tiles:
            if not LG(tx + dx, tz): cols.setdefault(tx, []).append(tz)
        for tx, zs in cols.items():
            for a, b in runs(zs):
                xe = X(tx) if dx < 0 else X(tx + 1); xi = xe - dx * IW
                za = Z(a) + (IN if not LG(tx, a - 1) else 0); zb = Z(b + 1)
                n = (dx, 1, 0)
                face(m, 'nagakusa01b', [(xe, H0, Z(a), 0, 0), (xe, H0, zb, (zb - Z(a)) / T, 0),
                                        (xi, H1, zb, (zb - Z(a)) / T, 0.5), (xi, H1, za, (za - Z(a)) / T, 0.5)], n)
                for nn in ((dx, 0, 0), (-dx, 0, 0)):
                    face(m, 'nagakusa01b', [(xi, H1, za, 0, 0.5), (xi, H1, zb, (zb - za) / T, 0.5),
                                            (xi, H2, zb, (zb - za) / T, 1), (xi, H2, za, 0, 1)], nn)

def _deck_dir(k, tx, tz, members):
    """'ns' if the deck runs north-south at this tile (more deck or walkable land north/south than east/west, or
    water on its east/west sides), else 'ew'."""
    link = lambda x, z: k.cls(x, z) in members or (k.walk(x, z) and k.cls(x, z) not in WATER)
    ns = link(tx, tz - 1) + link(tx, tz + 1); ew = link(tx - 1, tz) + link(tx + 1, tz)
    if ns != ew: return 'ns' if ns > ew else 'ew'
    wet_ns = sum(k.cls(tx, tz + d) in WATER for d in (-1, 1)); wet_ew = sum(k.cls(tx + d, tz) in WATER for d in (-1, 1))
    return 'ns' if wet_ew > wet_ns else 'ew'

def _road_edge(k, tx, tz):
    """A Cycling Road railing (fence next to the road deck or its supports): the deck continues under it."""
    return k.cls(tx, tz) == 'fence' and any(k.cls(tx + dx, tz + dz) in ('bike_path', 'other:bridge_support')
                                            for dx in (-1, 0, 1) for dz in (-1, 0, 1))

def draw_road_rails(m, k):
    """(walkability 2026-10-11) The Cycling Road's support tiles beside its deck over land (Sapphire's blue side strip
    and pillars, solid): Black 2's metal railing (Accumula's t2_saku01) through the tile, along the road. With no deck
    (draw_decks) they were bare grass beside the road you could not step on (b2tools/walk_diff.py OPEN). So do the
    ones beside walkable ground level with them (by Route 110's south gate, whose east side heights.py lifts to its
    west door's level)."""
    F = getattr(sys.modules.get('terrain.heights'), 'FIELD', None)
    y = lambda tx, tz: F.y(k.cell.X + tx, k.cell.Z + tz) if F else 0
    road = lambda tx, tz, t: k.cls(tx, tz) == 'bike_path' or (
        k.walk(tx, tz) and k.cls(tx, tz) not in ('other:bridge_support', 'fence') and F is not None and y(tx, tz) == y(*t))
    for tx, tz in k.tiles('other:bridge_support'):
        if water_under(k.cell.world, k.cell.X + tx, k.cell.Z + tz) is not None: continue   # (solid, collision())
        t = (tx, tz)
        ns, ew = road(tx - 1, tz, t) or road(tx + 1, tz, t), road(tx, tz - 1, t) or road(tx, tz + 1, t)
        if ns and ew:      # (a corner: one line, along the road, else east-west: crossed, their top strips z-fought)
            ns = k.cls(tx - 1, tz) == 'bike_path' or k.cls(tx + 1, tz) == 'bike_path'; ew = not ns
        if ns: _fence_line(m, 't2_saku01', (X(tx) + 8, Z(tz)), (X(tx) + 8, Z(tz + 1)))
        if ew: _fence_line(m, 't2_saku01', (X(tx), Z(tz) + 8), (X(tx + 1), Z(tz) + 8))

def draw_decks(m, k):
    """Wooden bridges and piers (class bridge): hashi01a as Black 2's plank bridges over water (Route 3 chunks 15/16,
    Route 14 chunk 95): the deck at the land's height, planks across it (u 0.34..0.97), one repeat per tile along it
    (v), and a side face down to 8 units below the deck (u 0.34 at the deck to 0.22 at the bottom) on edges that do
    not continue into deck or walkable land. (Route 3 spans u 0.34..0.97 over half its 3-tile width, mirrored; Hoenn's
    decks are mostly 1-2 tiles wide, so here it is one span per tile.)
    Cycling Road (bike_path and the railing tiles beside it): hashi02a, Route 8's concrete bridge (chunk 69): a plain
    deck sampled from the image's deck column (u 0.97, v one repeat per tile) and the same 8-unit side face. The road's
    supports (other:bridge_support, Sapphire's strip of bridge side and pillars below the road's edge) get no deck: in
    3D that side is the deck's side face, and the tile below it is water (water_under) or ground, solid as in Sapphire.
    Decks are at y 0 in the ground's place (ground_cover: no grass under them; at y 1 over the grass they flickered in
    melonDS); the player walks at y 0 as on Black 2's own bridges (height index 3). Quads are merged along the deck's
    length (one per run)."""
    y = 0.0
    for mat in ('hashi01a', 'hashi02a'):
        if mat == 'hashi01a':
            du = deck_under(k.cell.world)
            member = lambda tx, tz: k.cls(tx, tz) == 'bridge' or (k.cell.X + tx, k.cell.Z + tz) in du
            members = {'bridge'}
        else:
            member = lambda tx, tz: k.cls(tx, tz) in ('bike_path', 'other:acro_bike_rail') or _road_edge(k, tx, tz)
            members = {'bike_path'}
        tiles = [(tx, tz) for tz in range(32) for tx in range(32) if member(tx, tz)]
        if not tiles: continue
        # (bridges 2026-10-18) a raised plank bridge's runs end where its height steps: world.py's lift cut a run over
        # several heights into one piece per tile (+80 triangles on Route 120's south bridge)
        Fh = getattr(sys.modules.get('terrain.heights'), 'FIELD', None)
        up = getattr(Fh, 'raised_decks', ())
        hy_ = lambda tx, tz: Fh.y(k.cell.X + tx, k.cell.Z + tz)
        def runs_h(vals, at):
            out = []
            for a, b in runs(vals):
                if not any((k.cell.X + at(v)[0], k.cell.Z + at(v)[1]) in up for v in range(a, b + 1)):
                    out.append((a, b)); continue
                s0 = a
                for v in range(a + 1, b + 2):
                    if v > b or hy_(*at(v)) != hy_(*at(s0)): out.append((s0, v - 1)); s0 = v
            return out
        rows, cols = {}, {}
        for tx, tz in tiles:
            if mat == 'hashi02a' or _deck_dir(k, tx, tz, members) == 'ew': rows.setdefault(tz, []).append(tx)
            else: cols.setdefault(tx, []).append(tz)
        for tz, xs in rows.items():
            for a, b in runs_h(xs, lambda v, tz=tz: (v, tz)):
                if mat == 'hashi02a':
                    flat(m, mat, X(a), Z(tz), X(b + 1), Z(tz + 1), y, lambda x, z: (0.97, (x + HALF) / T))
                else:
                    z0 = Z(tz)
                    flat(m, mat, X(a), Z(tz), X(b + 1), Z(tz + 1), y, lambda x, z: (0.34 + 0.63 * (z - z0) / T, (x + HALF) / T))
        for tx, zs in cols.items():
            for a, b in runs_h(zs, lambda v, tx=tx: (tx, v)):
                x0 = X(tx)
                flat(m, mat, X(tx), Z(a), X(tx + 1), Z(b + 1), y, lambda x, z: (0.34 + 0.63 * (x - x0) / T, -(z + HALF) / T))
        def open_edge(tx, tz, dx, dz):
            if member(tx + dx, tz + dz): return False
            if k.cls(tx, tz) == 'other:acro_bike_rail':      # a rail's side only over water (a post's tile with water
                n = k.cls(tx + dx, tz + dz)                   # under it): over lower land heights.py draws the face
                return n in WATER or (n == 'other:acro_bike_rail_support' and
                                      water_under(k.cell.world, k.cell.X + tx + dx, k.cell.Z + tz + dz) is not None)
            return not (mat == 'hashi01a' and k.cls(tx + dx, tz + dz) not in WATER and k.walk(tx + dx, tz + dz))
        tset = set(tiles)
        # (a side face on a tile's south/east edge is lifted by the tile beyond it, where its centre falls: over a lower
        # floor - a walkway on posts, heights.STILTS - it sank into the ground. Those stand a hair inside their deck)
        H_ = sys.modules.get('terrain.heights'); stilts = getattr(getattr(H_, 'FIELD', None), 'stilt_decks', ())
        # (bridges 2026-10-18: so do a raised plank bridge's, heights.py raise_bridges: its south faces over the water
        # stood 32 units down at the water's level, by its posts. jetty 2026-10-18: and any plank deck's face over a tile
        # of another height - Mr. Briney's jetty on Route 104, 16 over the sea: its south faces stood at the sea's level,
        # 1 unit behind its posts, exterior_check layers hashi01a / hashi01a; Lavaridge's and Route 119's south bridge
        # had faces sunk or floating 8-16 units. The Cycling Road's concrete faces (hashi02a) are left where they were:
        # over land they stand in the rock faces heights.py draws up to the road, buried where they sank)
        def inset(tx, tz, dx=0, dz=0):
            p = (k.cell.X + tx, k.cell.Z + tz)
            if p in stilts or p in up: return 0.05
            Fh_ = getattr(H_, 'FIELD', None)
            return 0.05 if (mat == 'hashi01a' and (dx or dz) and Fh_ is not None
                            and Fh_.y(p[0] + dx, p[1] + dz) != Fh_.y(*p)) else 0
        for dz, n in ((-1, NORTH), (1, SOUTH)):
            er = {}
            for tx, tz in tiles:
                if open_edge(tx, tz, 0, dz): er.setdefault((tz, inset(tx, tz, 0, max(dz, 0))), []).append(tx)
            for (tz, ins), xs in er.items():
                for a, b in runs_h(xs, lambda v, tz=tz: (v, tz)):
                    z = Z(tz) if dz < 0 else Z(tz + 1) - ins; L = b + 1 - a
                    face(m, mat, [(X(a), y, z, 0.34, 0), (X(b + 1), y, z, 0.34, L), (X(b + 1), y - 8, z, 0.22, L), (X(a), y - 8, z, 0.22, 0)], n)
        for dx, n in ((-1, WEST), (1, EAST)):
            ec = {}
            for tx, tz in tiles:
                if open_edge(tx, tz, dx, 0): ec.setdefault((tx, inset(tx, tz, max(dx, 0), 0)), []).append(tz)
            for (tx, ins), zs in ec.items():
                for a, b in runs_h(zs, lambda v, tx=tx: (tx, v)):
                    x = X(tx) if dx < 0 else X(tx + 1) - ins; L = b + 1 - a
                    face(m, mat, [(x, y, Z(a), 0.34, 0), (x, y, Z(b + 1), 0.34, L), (x, y - 8, Z(b + 1), 0.22, L), (x, y - 8, Z(a), 0.22, 0)], n)
        if mat == 'hashi01a': pier_posts(m, k, tiles, open_edge); stilt_floor(m, k, tiles); deck_risers(m, k, tiles)

def bridge_posts(k, tiles):
    """(bridges 2026-10-18) Posts of a raised plank bridge (heights.py raise_bridges) for pier_posts to draw: under the
    open edges of its span over the water, at tile boundaries every 4 tiles counted from the span's middle (none on a
    span of 5: B1 stands between its rock abutments), not at every tile as a pier's - a row of posts there read as a
    fence, and a surfer passing under goes between them (its sprite is two tiles wide). -> {(x, z, drop)}"""
    H = sys.modules.get('terrain.heights'); F = getattr(H, 'FIELD', None) if H else None
    raised = getattr(F, 'raised_decks', ()) if F is not None else ()
    if not raised: return set()
    world, cx, cz = k.cell.world, k.cell.X, k.cell.Z
    span = lambda p: p in raised and water_under(world, *p) is not None
    open_ = lambda p: (world.get(p) or (0, 0))[1] in SURFACE
    out = set()
    for tx, tz in tiles:
        p = (cx + tx, cz + tz)
        if not span(p): continue
        for along, side in (((1, 0), (0, 1)), ((1, 0), (0, -1)), ((0, 1), (1, 0)), ((0, 1), (-1, 0))):
            if not open_((p[0] + side[0], p[1] + side[1])): continue
            a = 0                                           # (the run of span tiles along this edge, p its a-th)
            while span((p[0] - along[0] * (a + 1), p[1] - along[1] * (a + 1))): a += 1
            n = a + 1
            while span((p[0] + along[0] * (n - a), p[1] + along[1] * (n - a))): n += 1
            i = a                                           # (the boundary on p's west / north side: i of 0..n)
            if not (0 < i < n and abs((i - n / 2) / 4 - round((i - n / 2) / 4)) < 1e-9): continue
            t = water_under(world, *p)
            drop = F.y(*p) - F.y(*t)
            if along == (1, 0): px, pz = X(tx), (Z(tz + 1) - 3 if side[1] > 0 else Z(tz) + 3)
            else: pz, px = Z(tz), (X(tx + 1) - 3 if side[0] > 0 else X(tx) + 3)
            out.add((px, pz, drop))
    return out

def deck_risers(m, k, tiles):
    """(bridges 2026-10-18) A raised plank bridge (heights.py raise_bridges, F.raised_decks) steps from its banks up to
    its span: where a deck tile stands higher than the walkable tile beside it (the bank, a lower step) a wooden riser
    of the planks' dark side band (u 0.34 at the top to 0.22 at the foot, as the deck's side faces) closes the step,
    facing the lower tile, a hair inside the deck tile so world.py lifts it by the deck's height (heights.py draws no
    rock skirt there). North-facing risers are left out (Black 2's camera looks north: never seen)."""
    F = getattr(sys.modules.get('terrain.heights'), 'FIELD', None)
    raised = getattr(F, 'raised_decks', ()) if F is not None else ()
    if not raised: return
    cx, cz = k.cell.X, k.cell.Z
    for tx, tz in tiles:
        p = (cx + tx, cz + tz)
        if p not in raised: continue
        for dx, dz, n in ((0, 1, SOUTH), (-1, 0, WEST), (1, 0, EAST)):
            q = (p[0] + dx, p[1] + dz)
            d = F.y(*p) - F.y(*q)
            if q not in F.walk or q in F.slope or d < 0.5: continue
            if dz: z = Z(tz + 1) - 0.05; a, b = (X(tx), z), (X(tx + 1), z)
            else: x = X(tx) + 0.05 if dx < 0 else X(tx + 1) - 0.05; a, b = (x, Z(tz)), (x, Z(tz + 1))
            face(m, 'hashi01a', [(a[0], 0, a[1], 0.34, 0), (b[0], 0, b[1], 0.34, 1), (b[0], -d, b[1], 0.22, 1),
                                 (a[0], -d, a[1], 0.22, 0)], n)

POSTED_DECKS = {'PacifidlogTown', 'DewfordTown'}   # (walkways and boat docks at the land's level on posts, as Humilau's)
def stilt_floor(m, k, tiles):
    """The forest floor under a walkway on posts (heights.STILTS, Fortree; map_glitch_fix 2026-10-09): the floor's own
    ground (the texture and height of the lowest floor tile beside the deck), seen under the deck between its posts.
    world.py draws no ground under a deck tile (ground_cover)."""
    H = sys.modules.get('terrain.heights'); F = getattr(H, 'FIELD', None) if H else None
    stilts = getattr(F, 'stilt_decks', ()) if F else ()
    if not stilts: return
    cx, cz = k.cell.X, k.cell.Z
    for tx, tz in tiles:
        p = (cx + tx, cz + tz)
        if p not in stilts: continue
        floor = [(F.y(p[0] + dx, p[1] + dz), (p[0] + dx, p[1] + dz)) for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                 if (dx or dz) and (p[0] + dx, p[1] + dz) in getattr(F, 'stilt_ground', ())]
        if not floor: continue
        h, q = min(floor)
        flat(m, F.mat.get(q, 'grass01ax'), X(tx), Z(tz), X(tx + 1), Z(tz + 1), h - F.y(*p),
             lambda x, z: ((x + HALF) / 64, -(z + HALF) / 64))
def pier_posts(m, k, tiles, open_edge):
    """A wooden deck standing high over the water (Mr. Briney's jetty on Route 104: the plateau's height, 24 over his
    cove) gets posts from under its 8-unit side face down into the water at the corners of its open edges, of the same
    planks' dark side (u 0.22..0.28), as the archway's posts (overworld_polish 2026-10-08). Decks at the land's own
    level over water 8 below (every other bridge) need none: the side face reaches the water."""
    H = sys.modules.get('terrain.heights'); F = getattr(H, 'FIELD', None) if H else None
    if F is None: return
    cx, cz = k.cell.X, k.cell.Z
    corners = set()
    stilts = getattr(F, 'stilt_decks', ())
    for tx, tz in tiles:
        if (cx + tx, cz + tz) in stilts:                  # a walkway on posts over the forest floor (heights.STILTS,
            lows = [F.y(cx + tx + dx, cz + tz + dz) for dx, dz in ((0, 1), (-1, 0), (1, 0), (0, -1))   # Fortree): posts
                    if open_edge(tx, tz, dx, dz)]          # down to the floor beside it, on every other tile
            drop = F.y(cx + tx, cz + tz) - min(lows) if lows else 0
            if drop < 12 or (cx + tx + cz + tz) % 2: continue
            for dx, dz in ((0, 1), (-1, 0), (1, 0)):
                if not open_edge(tx, tz, dx, dz): continue
                if dz: corners |= {(X(tx) + 3, Z(tz + 1) - 3, drop - 13), (X(tx + 1) - 3, Z(tz + 1) - 3, drop - 13)}
                else:
                    xe = X(tx) + 3 if dx < 0 else X(tx + 1) - 3
                    corners |= {(xe, Z(tz) + 3, drop - 13), (xe, Z(tz + 1) - 3, drop - 13)}
            continue                                      # (drop - 13: y1 = -drop - 14 + 13, 1 into the floor)
        if (cx + tx, cz + tz) in getattr(F, 'raised_decks', ()): continue     # (a raised bridge: bridge_posts)
        t = water_under(k.cell.world, cx + tx, cz + tz)
        if t is None: continue
        drop = F.y(cx + tx, cz + tz) - F.y(*t)            # deck over its water tile (the water's surface 11 below that)
        if drop < 8 and k.map(tx, tz) not in POSTED_DECKS: continue
        for dx, dz in ((0, 1), (-1, 0), (1, 0)):
            if not open_edge(tx, tz, dx, dz): continue
            if dz: corners |= {(X(tx) + 3, Z(tz + 1) - 3, drop), (X(tx + 1) - 3, Z(tz + 1) - 3, drop)}
            else:
                xe = X(tx) + 3 if dx < 0 else X(tx + 1) - 3
                corners |= {(xe, Z(tz) + 3, drop), (xe, Z(tz + 1) - 3, drop)}
    corners |= bridge_posts(k, tiles)
    for px, pz, drop in corners:
        y0, y1 = -8, -drop - 14                           # (into the water: its sheet lies 11 under the water's height)
        v = (y0 - y1) / 16                                # (the side band u 0.22..0.34 across, one texel a unit up)
        for verts, n in (([(px - 2, y0, pz + 2, 0.22, 0), (px + 2, y0, pz + 2, 0.34, 0), (px + 2, y1, pz + 2, 0.34, v), (px - 2, y1, pz + 2, 0.22, v)], SOUTH),
                         ([(px - 2, y0, pz - 2, 0.22, 0), (px - 2, y0, pz + 2, 0.34, 0), (px - 2, y1, pz + 2, 0.34, v), (px - 2, y1, pz - 2, 0.22, v)], WEST),
                         ([(px + 2, y0, pz - 2, 0.22, 0), (px + 2, y0, pz + 2, 0.34, 0), (px + 2, y1, pz + 2, 0.34, v), (px + 2, y1, pz - 2, 0.22, v)], EAST)):
            face(m, 'hashi01a', verts, n)

def draw_fences(m, k):
    """Fences as Black 2 builds them (saku01a on Route 1/3, chunks 3 and 13; t2_saku01 in Accumula, chunk 5): one
    upright plane on the fence line from y 2 to 20 (u 0..0.5 bottom to top, v two repeats per tile along the line), a
    bottom strip at y 3 (u 0.5..0.75) and a top rail at y 14.5 (u 0.75..1), both 10 units wide. Lines run through
    tile centres and join neighbouring fence tiles; a walkable fence tile (railing drawn on the north half of the
    tile in Sapphire) gets its line 2 units inside its north edge."""
    F = lambda tx, tz: k.cls(tx, tz) == 'fence'
    tiles = k.tiles('fence')
    metal = lambda tx, tz: k.map(tx, tz) in METAL_FENCE_MAPS or any(
        k.cls(tx + dx, tz + dz) in ('bike_path', 'other:bridge_support') for dx in (-1, 0, 1) for dz in (-1, 0, 1))
    def line_z(tx, tz): return Z(tz) + (2 if _fence_walkable(k, tx, tz) else 8)
    # horizontal segments: half-tile pieces from each tile centre towards fence neighbours east/west
    for want_metal in (False, True):
        mat = 't2_saku01' if want_metal else 'saku01a'
        hs, vs = {}, {}
        for tx, tz in tiles:
            if metal(tx, tz) != want_metal: continue
            e, w, n, s = F(tx + 1, tz), F(tx - 1, tz), F(tx, tz - 1), F(tx, tz + 1)
            if not (e or w or n or s): e = w = True          # lone post: a short east-west piece
            if not (e or w) and _fence_walkable(k, tx, tz): e = w = True
            zc = line_z(tx, tz)
            if e: hs.setdefault(zc, set()).add(2 * tx + 1)
            if w: hs.setdefault(zc, set()).add(2 * tx)
            if (n or s) and not _fence_walkable(k, tx, tz):
                xc = X(tx) + 8
                if n: vs.setdefault(xc, set()).add(2 * tz)
                if s: vs.setdefault(xc, set()).add(2 * tz + 1)
        hlines = [(zc, a * 8 - HALF, (b + 1) * 8 - HALF) for zc, halves in hs.items() for a, b in runs(halves)]
        for zc, xa, xb in hlines:
            _fence_line(m, mat, (xa, zc), (xb, zc))
        for xc, halves in vs.items():
            for a, b in runs(halves):
                za, zb = a * 8 - HALF, (b + 1) * 8 - HALF
                # where an east-west fence meets or crosses this one, its strips already cover the 10x10 square:
                # the north-south strips leave it out (the two coplanar strips z-fought there)
                cuts = [(zc - 5, zc + 5) for zc, xa, xb in hlines if xa - 5 <= xc <= xb + 5 and za - 5 <= zc <= zb + 5]
                _fence_line(m, mat, (xc, za), (xc, zb), cuts)

def _fence_walkable(k, tx, tz):
    return k.walk(tx, tz) and k.map(tx, tz) != 'Route110'

def _fence_line(m, mat, p0, p1, cuts=()):
    (xa, za), (xb, zb) = p0, p1
    L = math.hypot(xb - xa, zb - za) / T
    plane = [(xa, 2, za, 0, 0), (xb, 2, zb, 0, -2 * L), (xb, 20, zb, 0.5, -2 * L), (xa, 20, za, 0.5, 0)]
    if za == zb: face(m, mat, plane, SOUTH)          # an east-west fence is only ever seen from the south
    else: both(m, mat, plane)
    px, pz = (0, 5) if za == zb else (5, 0)            # strips 10 units wide across the line
    # pieces of the line the strips cover: all of it, less the cut intervals (along z; north-south lines only)
    pieces = [(za, zb)]
    for c0, c1 in sorted(cuts):
        pieces = [q for a, b in pieces for q in ((a, min(b, c0)), (max(a, c1), b)) if q[1] - q[0] > 0.01]
    for y, u0, u1 in ((3, 0.5, 0.75), (14.5, 0.75, 1.0)):
        for z0, z1 in (pieces if xa == xb else [(za, zb)]):
            if xa == xb: q0, q1, v0, v1 = (xa, z0), (xb, z1), -2 * (z0 - za) / T, -2 * (z1 - za) / T
            else: q0, q1, v0, v1 = (xa, za), (xb, zb), 0, -2 * L
            face(m, mat, [(q0[0] - px, y, q0[1] - pz, u0, v0), (q1[0] - px, y, q1[1] - pz, u0, v1),
                          (q1[0] + px, y, q1[1] + pz, u1, v1), (q0[0] + px, y, q0[1] + pz, u1, v0)], UP)

def face_tile(k, tx, tz):
    """True when heights.py draws a cliff face in this (solid) tile: a non-stair 8-neighbour stands higher (its rule
    for face tiles; step 9 brings a solid tile next to lower walkable ground down to it, so it holds the face)."""
    F = getattr(sys.modules.get('terrain.heights'), 'FIELD', None)
    if F is None: return False
    wx, wz = k.cell.X + tx, k.cell.Z + tz
    if (wx, wz) in F.noface: return False     # (sweep_outdoor 2026-10-11: flat beside raised rock, heights.py 9d: the
    h = F.y(wx, wz)                           #  prop's plinth / the wall block stands on it, the skirt behind)
    return any(F.y(wx + dx, wz + dz) > h + 1 and (wx + dx, wz + dz) not in F.slope
               for dx in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dz)

# Ferry piers (overworld_polish 2026-10-08): the Battle Tower's and Southern Island's S.S. Tidal piers are Sapphire's
# stone pier - a walkway of path tiles ending in two rows of wall tiles, the pier's front face over the water. They
# stood on grass banks and rock (the island's land) with a 16-unit stone block (draw_walls) across their front. Black 2's
# harbour piers (Castelia, Undella) are paved decks with straight stone sides into the sea: the walkway and its front
# rows are paved with Accumula's stone (t02michi_b, as the walls' tops) at the walkway's height, and water.py gives
# their water edges a vertical stone side (t02_kabe01, PIER_BANK). Drawing only.
PIER_MAPS = {'BattleTower_Outside', 'SouthernIsland_Exterior'}
PIER_CLASSES = {'path', 'wall', 'stairs', 'bridge', 'fence'}
_PIER = {}
def pier_tiles(world):
    """World tiles of the ferry piers: the PIER_MAPS' path/wall tiles 4-connected to a wall tile that touches water."""
    if id(world) in _PIER: return _PIER[id(world)]
    cls_at = lambda p: (world.get(p) or (None, None))[1]
    nb = lambda p: [(p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)]
    seeds = [p for p, e in world.items() if e[0] in PIER_MAPS and e[1] == 'wall' and any(cls_at(n) in WATER for n in nb(p))]
    out, q = set(seeds), list(seeds)
    while q:
        p = q.pop()
        for n in nb(p):
            e = world.get(n)
            if e and e[0] in PIER_MAPS and e[1] in PIER_CLASSES and n not in out: out.add(n); q.append(n)
    _PIER.clear(); _PIER[id(world)] = out
    return out

def pier_tile(world, wx, wz): return (wx, wz) in pier_tiles(world)

# Paved towns (overworld_polish 2026-10-08): Sapphire paves Rustboro (cream cobble, pale grey-blue roads), Slateport
# (grey cobble, white stone) and Mauville (pale paving); their path tiles were Black 2's dirt path (michi01a/b). Black 2's
# paved town of the same set is Accumula (chunk 5): square stone slabs t02michi_b (cobble and plazas) and plain stone
# t02michi_c (the pale roads), both in Hoenn's set 3 (0 bytes). Picked per tile from Sapphire's metatile colour; the
# buildings standing on the paving (path_under) take the slabs. world.py leaves these path tiles to draw_paving.
PAVED_MAPS = {'RustboroCity', 'SlateportCity', 'MauvilleCity'}
if 'version' in sys.modules and sys.modules['version'].EMERALD:   # (Emerald's world, emerald_world 2026-10-12: the Battle
    PAVED_MAPS = PAVED_MAPS | {'BattleTower_Outside', 'BattleFrontier_OutsideEast'}   # Frontier island's pale paving;
    METAL_FENCE_MAPS = METAL_FENCE_MAPS | {'BattleFrontier_OutsideEast'}            # its east half's railings as the west's;
    PIER_MAPS = PIER_MAPS - {'BattleTower_Outside'}   # its plaza walls join the ferry pier's: the pier rule paved them flat)
_PAVED = {}
def paved_tiles(world):
    """World tile -> paving texture for the paved towns' path tiles and the buildings standing on them."""
    if id(world) in _PAVED: return _PAVED[id(world)]
    out = {}
    pu = path_under(world)
    for (wx, wz), e in world.items():
        if e[0] not in PAVED_MAPS or not (e[1] == 'path' or (wx, wz) in pu): continue
        tex = 't02michi_b'
        px = sapphire_pixels(e[0], wx, wz) if e[1] == 'path' else None
        if px is not None:
            r, g, b = np.median(px, 0)
            if g >= 208 and b >= 208 and b >= r - 12: tex = 't02michi_c'   # (the pale roads and white stone: blue-grey or
            # white. Emerald's Rustboro cobble is pale too but cream, 238,238,213: slabs, as Sapphire's 205,205,164; #9 2026-10-18)
        out[(wx, wz)] = tex
    # (the lamp posts, signs and stall props standing in the paving, 3+ sides paved: on the slabs, not on grass squares)
    for (wx, wz), e in world.items():
        if e[0] in PAVED_MAPS and e[1] in ('prop', 'sign', 'fence', 'other:market_awning') and (wx, wz) not in out and \
                sum(n in out for n in ((wx + 1, wz), (wx - 1, wz), (wx, wz + 1), (wx, wz - 1))) >= 3:
            out[(wx, wz)] = 't02michi_b'
    _PAVED.clear(); _PAVED[id(world)] = out
    return out

def paved_tile(world, wx, wz):
    """A path tile world.py leaves to this module: a ferry pier or a paved town's paving."""
    return (wx, wz) in pier_tiles(world) or (wx, wz) in paved_tiles(world)

def draw_paving(m, k):
    """The paved towns' paving (paved_tiles), one repeat per 2 tiles as Accumula's."""
    pt = paved_tiles(k.cell.world)
    rows = {}
    for tz in range(32):
        for tx in range(32):
            t = pt.get((k.cell.X + tx, k.cell.Z + tz))
            if t: rows.setdefault((tz, t), []).append(tx)
    for (tz, t), xs in rows.items():
        for a, b in runs(xs):
            n = 32 if t == 't02michi_b' else 16                     # (t02michi_b 32x32, t02michi_c 16x16: a texel a unit)
            flat(m, t, X(a), Z(tz), X(b + 1), Z(tz + 1), 0, lambda x, z: ((x + HALF) / n, -(z + HALF) / n))

def draw_pier(m, k):
    """Paving on the ferry piers' walkway and front rows (pier_tiles), at the walkway's height."""
    pt = pier_tiles(k.cell.world)
    rows = {}
    for tz in range(32):
        for tx in range(32):
            if (k.cell.X + tx, k.cell.Z + tz) in pt and k.cls(tx, tz) in ('path', 'wall', 'fence'): rows.setdefault(tz, []).append(tx)
    for tz, xs in rows.items():
        for a, b in runs(xs):
            flat(m, 't02michi_b', X(a), Z(tz), X(b + 1), Z(tz + 1), 0, lambda x, z: ((x + HALF) / 32, -(z + HALF) / 32))
    # Sapphire's white railing along the pier's front (its solid wall tiles south of the walkway, and across the end of
    # the gangway): Black 2's metal railing (Accumula's t2_saku01, draw_fences) along the tile centres. Paved only, the
    # front rows read as more pier you could not walk on (walkability 2026-10-11, b2tools/walk_diff.py OPEN)
    rail = {}
    for tz in range(32):
        for tx in range(32):
            if (k.cell.X + tx, k.cell.Z + tz) in pt and k.cls(tx, tz) == 'wall' and not k.walk(tx, tz) and \
                    k.walk(tx, tz - 1) and k.cls(tx, tz - 1) in PIER_CLASSES:
                rail.setdefault(tz, []).append(tx)
    for tz, xs in rail.items():
        for a, b in runs(xs):
            _fence_line(m, 't2_saku01', (X(a), Z(tz) + 8), (X(b + 1), Z(tz) + 8))

def draw_walls(m, k):
    """Walls: Accumula's stone retaining wall (t02_kabe01 faces, chunk 5; its top band carries the coping) as a solid
    block one tile high, topped with Accumula's paving (t02michi_b). Faces only where the next tile is not wall.
    A wall tile that holds a cliff face (face_tile: the foot of a higher terrace; Sootopolis's rims, Ever Grande, Sky
    Pillar's top) is that face: a block drawn there too stood in the same plane as the face and depth-fought it
    (outdoor sweep 2026-10-07, outdoor_check.py layer)."""
    W = lambda tx, tz: k.cls(tx, tz) == 'wall' and not face_tile(k, tx, tz) and not pier_tile(k.cell.world, k.cell.X + tx, k.cell.Z + tz)
    H = 16
    v0 = 1 - H / 64            # t02_kabe01 is 32x64: map the wall's 16 units to the image's top 16 rows
    tiles = [t for t in k.tiles('wall') if W(*t)]
    rows = {}
    for tx, tz in tiles: rows.setdefault(tz, []).append(tx)
    for tz, xs in rows.items():
        for a, b in runs(xs):
            flat(m, 't02michi_b', X(a), Z(tz), X(b + 1), Z(tz + 1), H, lambda x, z: ((x + HALF) / 32, -(z + HALF) / 32))
        for dz, n in ((1, SOUTH),):      # north faces point away from Gen 5's camera
            open_ = [tx for tx in xs if not W(tx, tz + dz)]
            for a, b in runs(open_) if open_ else []:
                z = Z(tz) if dz < 0 else Z(tz + 1)
                face(m, 't02_kabe01', [(X(a), 0, z, 0, v0), (X(b + 1), 0, z, b + 1 - a, v0),
                                       (X(b + 1), H, z, b + 1 - a, 1), (X(a), H, z, 0, 1)], n)
    for dx, n in ((-1, WEST), (1, EAST)):
        cols = {}
        for tx, tz in tiles:
            if not W(tx + dx, tz): cols.setdefault(tx, []).append(tz)
        for tx, zs in cols.items():
            for a, b in runs(zs):
                x = X(tx) if dx < 0 else X(tx + 1)
                face(m, 't02_kabe01', [(x, 0, Z(a), 0, v0), (x, 0, Z(b + 1), b + 1 - a, v0),
                                       (x, H, Z(b + 1), b + 1 - a, 1), (x, H, Z(a), 0, 1)], n)

def hedge(m, x0, x1, z0, z1, mat='plant01', ends=(True, True)):
    """Striaton's hedge (plant01, chunk 11): a leafy box 3 units inside the tile (y 2..12, sides u 0.66..1 from top to
    bottom) under a gable of leaves (eaves y 12 at the tile edges, ridge y 16 along the middle; slopes u 0.56..0.28 and
    0.28..0, v one repeat per tile along the hedge) with triangular ends (u 0.47..0.56). ends (west, east): False where
    the hedge goes on in the next chunk (no end there; dewford_fix 2026-10-12)."""
    L = (x1 - x0) / T; zm = (z0 + z1) / 2; zi0, zi1 = z0 + 3, z1 - 3
    xi0, xi1 = (x0 + 2 if ends[0] else x0), (x1 - 2 if ends[1] else x1)
    face(m, mat, [(x0, 12, z0, 0.56, 0), (x1, 12, z0, 0.56, -L), (xi1, 16, zm, 0.28, -L), (xi0, 16, zm, 0.28, 0)], (0, 1, -1))
    face(m, mat, [(xi0, 16, zm, 0.28, 0), (xi1, 16, zm, 0.28, -L), (x1, 12, z1, 0.0, -L), (x0, 12, z1, 0.0, 0)], (0, 1, 1))
    for z, n in ((zi1, SOUTH),):
        face(m, mat, [(xi0, 2, z, 1.0, 0), (xi1, 2, z, 1.0, -L), (xi1, 12, z, 0.66, -L), (xi0, 12, z, 0.66, 0)], n)
    for x, xi, n, end in ((x0, xi0, WEST, ends[0]), (x1, xi1, EAST, ends[1])):
        if not end: continue
        face(m, mat, [(x, 12, z0, 0.56, 0.94), (x, 12, z1, 0.56, 0.06), (xi, 16, zm, 0.47, 0.5)], n)
        face(m, mat, [(xi, 2, zi0, 1.0, 1), (xi, 2, zi1, 1.0, 0), (xi, 12, zi1, 0.66, 0), (xi, 12, zi0, 0.66, 1)], n)

def draw_bushes(m, k):
    """Solid bush tiles: Striaton's hedge per east-west run. Walkable bush tiles (Petalburg's walk-behind hedge tops)
    get nothing: the hedge below already rises over them, as in Sapphire."""
    rows = {}
    for tx, tz in k.tiles('bush'):
        if not k.walk(tx, tz): rows.setdefault(tz, []).append(tx)
    for tz, xs in rows.items():
        for a, b in runs(xs): hedge(m, X(a), X(b + 1), Z(tz), Z(tz + 1))

# Black 2's terrain boulder (iwa01), the same mesh in chunks 35 (Route 4), 48 (Driftveil), 95 (Route 14), 300/302
# (Humilau, Route 22): octagonal base radius 28 at the ground, square top +-10 at 22 units; sides v 0..0.5, top v 0.5..1.
_IWA = [((-10, 22, 10, 2.25, .5), (-14, 0, 28, 2, 0), (14, 0, 28, 4, 0), (10, 22, 10, 3.75, .5)),
        ((-14, 0, -28, 4, 0), (-10, 22, -10, 3.75, .5), (10, 22, -10, 2.25, .5), (14, 0, -28, 2, 0)),
        ((-10, 22, 10, -1, .5), (10, 22, 10, -1, 1), (10, 22, -10, -2, 1), (-10, 22, -10, -2, .5)),
        ((28, 0, -14, 4, 0), (10, 22, -10, 3.75, .5), (10, 22, 10, 2.25, .5), (28, 0, 14, 2, 0)),
        ((-28, 0, -14, 2, 0), (-28, 0, 14, 4, 0), (-10, 22, 10, 3.75, .5), (-10, 22, -10, 2.25, .5)),
        ((14, 0, -28, 1, 0), (10, 22, -10, .5, .5), (28, 0, -14, 0, 0)),
        ((-10, 22, 10, .5, .5), (-28, 0, 14, 0, 0), (-14, 0, 28, 1, 0)),
        ((10, 22, 10, .5, .5), (14, 0, 28, 0, 0), (28, 0, 14, 1, 0)),
        ((-28, 0, -14, 1, 0), (-10, 22, -10, .5, .5), (-14, 0, -28, 0, 0))]

def boulder(m, cx, cz, size, wet=False, height=22, skip=()):
    """iwa01 boulder centred at (cx, cz), its base octagon `size` units across. Faces that point away from Gen 5's
    camera (the north slope and the two northern corner triangles; the camera looks north and down) are left out:
    10 of the 14 triangles. In water the slopes continue 8 units further down (base at y -8) so the boulder meets
    a water surface drawn below the ground."""
    s = size / 56; f = 8 / height if wet else 0
    for i, poly in enumerate(_IWA):
        if all(p[2] <= -10 for p in poly) and any(p[1] == 0 for p in poly): continue      # north-facing
        if i in skip: continue
        vs = []
        for x, y, z, u, v in poly:
            if y == 0:      # base vertex: extend along its slope edge (from the top corner it joins) by f
                tx_, tz_ = 10 * (1 if x > 0 else -1), 10 * (1 if z > 0 else -1)
                x, z = x + (x - tx_) * f, z + (z - tz_) * f
                vs.append((cx + x * s, -8 if wet else 0, cz + z * s, u, v))
            else:
                vs.append((cx + x * s, y * height / 22, cz + z * s, u, v))
        c = (sum(p[0] for p in vs) / len(vs) - cx, 0, sum(p[2] for p in vs) / len(vs) - cz)
        n = (c[0], 1, c[2]) if any(p[1] <= 0 for p in vs) else UP
        face(m, 'iwa01', vs, n)

# --------------------------------------------------------------------- Sapphire metatile behaviours (optional input)
_SAP = {}
def sapphire_behaviour(name, wx, wz):
    """Metatile behaviour byte (pokeruby include/constants/metatile_behaviors.h) of the Sapphire tile at global tile
    (wx, wz) of map `name`, read from external/pokeruby (layout blockdata + metatile_attributes.bin), or None if
    pokeruby is not there. Map origins as world.py composes them (layout + margin + shift + pad_north)."""
    import os, json, struct
    root = os.path.join(os.path.dirname(__file__), '..', '..')
    if 'origins' not in _SAP:
        try:
            cfg = json.load(open(os.path.join(root, 'data', 'hoenn_world.json')))
            lay = json.load(open(os.path.join(root, 'data', 'hoenn_world_layout.json')))['main']['maps']
            M = cfg['margin_cells'] * 32
            _SAP['origins'] = {n: (L['tile_x'] + M + cfg.get('shift', {}).get(n, [0, 0])[0],
                                   L['tile_z'] + M + cfg.get('shift', {}).get(n, [0, 0])[1] + cfg.get('pad_north', {}).get(n, 0))
                               for n, L in lay.items()}
            import sys
            sys.path.insert(0, os.path.join(root, 'converter'))
            from gba import world_repo        # (Repo(pokeruby); HOENN_VERSION=emerald: Emerald's maps)
            _SAP['repo'] = world_repo(os.path.join(root, 'external', 'pokeruby'))
        except Exception:
            _SAP['origins'] = None
    if not _SAP['origins'] or name not in _SAP['origins']: return None
    if name not in _SAP:
        try:
            r = _SAP['repo']; g, l = r.layout_grid(r.map_json(name)['layout'])
            attrs = []
            for ts in (l['primary_tileset'], l['secondary_tileset']):
                d = open(os.path.join(r.tileset_dir(ts), 'metatile_attributes.bin'), 'rb').read()
                attrs.append(struct.unpack(f'<{len(d) // 2}H', d))
            _SAP[name] = (g, attrs)
        except Exception:
            _SAP[name] = None
    if _SAP[name] is None: return None
    g, attrs = _SAP[name]
    ox, oz = _SAP['origins'][name]
    x, y = wx - ox, wz - oz
    if y < 0: y = y % 2                       # Route 101's padded rows repeat its first two rows
    if not (0 <= y < g.shape[0] and 0 <= x < g.shape[1]): return None
    mt = int(g[y, x]) & 0x3FF
    a = attrs[0] if mt < 512 else attrs[1]; i = mt if mt < 512 else mt - 512
    return a[i] & 0xFF if i < len(a) else None

MB_SAND, MB_DEEP_SAND, MB_LONG_GRASS_SOUTH_EDGE = 0x21, 0x06, 0x09

# ------------------------------------------------------------------------------------- world-wide groupings (cached)
_CACHE = {}
def _world_groups(world):
    """Rock boulders (2x2 where four rock tiles make a square, else 1x1, greedy in global raster order) and
    connected groups of the multi-tile props, computed once per world dict."""
    key = id(world)
    if key in _CACHE: return _CACHE[key]
    by = {}
    for p, e in world.items():
        if e[1] in ('rock', 'other:big_tree', 'other:beach_umbrella', 'other:archway', 'other:market_awning'):
            by.setdefault(e[1], set()).add(p)
    rocks = []
    H = sys.modules.get('terrain.heights'); F = getattr(H, 'FIELD', None) if H else None
    rset = by.get('rock', set()) - (F.card_tiles() if F is not None else set()); used = set()   # (a card mass's own
    #   rock tiles: its one card covers them, heights.raise_sea_rock)
    hy = (lambda p: F.y(*p)) if F is not None else (lambda p: 0)
    for (x, z) in sorted(rset, key=lambda p: (p[1], p[0])):
        if (x, z) in used: continue
        sq = [(x, z), (x + 1, z), (x, z + 1), (x + 1, z + 1)]
        # (a 2x2 card only over tiles drawn at one height: world.py lifts each tile's piece by its own height)
        if all(s in rset and s not in used for s in sq) and len({hy(s) for s in sq}) == 1:
            used |= set(sq); rocks.append((x, z, 2))
        else:
            used.add((x, z)); rocks.append((x, z, 1))
    comps = {}
    for c in ('other:big_tree', 'other:beach_umbrella', 'other:archway', 'other:market_awning'):
        left = set(by.get(c, set())); out = []
        while left:
            st = [left.pop()]; comp = set(st)
            while st:
                x, z = st.pop()
                for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                    if n in left: left.discard(n); comp.add(n); st.append(n)
            out.append(comp)
        comps[c] = out
    _CACHE.clear(); _CACHE[key] = (rocks, comps)
    return _CACHE[key]

def _in_cell(cell, wx, wz): return wx // 32 == cell.cx and wz // 32 == cell.cz

# Black 2's own rocks (overworld_polish 2026-10-08): Black 2 does not build its route and sea rocks into the terrain
# but places four tiny models, one textured card each, leaning back 45 degrees towards Gen 5's camera (exterior pack 0
# res 21 rock_01, 258 rock_02, 54 searock_01, 55 searock_02; apicula DAEs of retail pack 0): rock_01 / searock_01 a
# 32x24 card from (+-16, 2, 16) up to (+-16, 26, -8), rock_02 / searock_02 a 16x8 one from (+-8, 2, 8) to (+-8, 10, -8),
# uv (0,0) (1,0) at the foot, (1,1) (0,1) at the top, texture rock01 (brown rock) or searock1.1 (grey rock in a ring of
# foam, the first of its four frames). Placed on land at the ground's height and in the sea at the water's collision
# height (Route 1 chunk 2: searock_01 at y -24 over water at -24, land -16; Undella Bay chunk 247: -88 / -88; rock_01 on
# Route 1's land at -16), the 32-unit ones centred on a tile corner (2x2 tiles), the 16-unit ones on a tile centre
# (chunk_buildings of chunks 2, 23, 247, 300). Undella Bay lines its rock walls up from rows of searock_01 32 apart.
# Hoenn has ~8,000 rock tiles (up to 72 groups a cell), more than the 32 placements a chunk allows, so the cards are
# drawn into the terrain with the same geometry and images (iwa01 boulders before: tall tan cones in the sea).
CARDS = {2: ((16, 2, 16), (16, 26, -8)), 1: ((8, 2, 8), (8, 10, -8))}

def rock_card(m, cx, cz, n, wet, base=0, scale=1.0):
    """Black 2's rock_01/02 (searock_01/02 when wet) card centred at (cx, cz), base = height of its placement; scale
    for the big rocks (a 3x3 mass: 1.5)."""
    (a, y0, z0), (_, y1, z1) = CARDS[2 if n >= 2 else 1]
    a, y0, z0, y1, z1 = a * scale, y0 * scale, z0 * scale, y1 * scale, z1 * scale
    mat = 'searock1.1' if wet else 'rock01'
    face(m, mat, [(cx - a, base + y0, cz + z0, 0, 0), (cx + a, base + y0, cz + z0, 1, 0), (cx + a, base + y1, cz + z1, 1, 1),
                  (cx - a, base + y1, cz + z1, 0, 1)], (0, 0.7071, 0.7071))

def rock_wet(world, wx, wz, n=1):
    """Whether the rock group of n x n tiles from (wx, wz) stands in the water (its card is Black 2's sea rock, at the
    water's level 8 under the ground). (dewford_fix 2026-10-12) A rock with land beside it (a walkable tile that is not
    water) and no water drawn under any of its tiles (water.py look: the water module draws the sea under a rock only
    when no land touches it; ground_under lays the land's sand or grass there) is a land rock, on the ground. Any water
    tile in the ring round it, diagonals included, made it a sea rock before: a beach rock a tile from the waterline
    stood 8 units down in the sand, a grey sliver poking out (Route 106's Stardust rock by the fisherman). Other rocks
    keep that test (rocks in shallows, rows of rocks in the sea)."""
    tiles = [(wx + dx, wz + dz) for dx in range(n) for dz in range(n)]
    wm = sys.modules.get('terrain.water')
    if wm is not None and any(wm.look(world, *t) == 'sea' for t in tiles): return True
    ring = [(x, z) for x in range(wx - 1, wx + n + 1) for z in range(wz - 1, wz + n + 1) if (x, z) not in tiles]
    side = [(x, z) for x, z in ring if wx <= x < wx + n or wz <= z < wz + n]
    if any((world.get(k) or (0, 0, False))[2] and world[k][1] not in WATER for k in side): return False
    return any((world.get(k) or (0, None))[1] in WATER for k in ring)

def draw_rocks(m, k):
    """Every rock (Sapphire's 2x2 boulders and sea rocks, and single-tile rocks) as Black 2's rock card (rock_card):
    2x2 groups as rock_01 / searock_01, single tiles as rock_02 / searock_02."""
    rocks, _ = _world_groups(k.cell.world)
    H = sys.modules.get('terrain.heights'); F = getattr(H, 'FIELD', None) if H else None
    for comp in (F.card_mass if F is not None and ROCKS == 'cards' else []):     # Sapphire's big pointed sea rocks
        wx0, wz0 = comp[0]                                                     # (heights.py card_mass): one card the
        if not _in_cell(k.cell, wx0, wz0): continue                            # mass's size, in the water
        xs, zs = [p[0] for p in comp], [p[1] for p in comp]
        n = max(max(xs) - min(xs) + 1, max(zs) - min(zs) + 1)
        cx = X(min(xs) - k.cell.X) + 8 * (max(xs) - min(xs) + 1); cz = Z(min(zs) - k.cell.Z) + 8 * (max(zs) - min(zs) + 1)
        # (sweep_outdoor 2026-10-11: as one piece at the mass's height. The card leans north over the shoal tiles
        # behind the mass; world.py's per-tile lift raised those parts by the shoals' height: the peak floated apart
        # from its base, a hollow ring between them - Route 125's big rock by Shoal Cave)
        tmp = type(m)(m.name)
        rock_card(tmp, cx, cz, 2, True, -8, scale=n / 2)
        _as_one(m, tmp, k.cell, comp)
    if ROCKS == 'cards':
        for wx, wz, n in rocks:
            if not _in_cell(k.cell, wx, wz): continue
            tx, tz = wx - k.cell.X, wz - k.cell.Z
            wet = rock_wet(k.cell.world, wx, wz, n)
            rock_card(m, X(tx) + 8 * n, Z(tz) + 8 * n, n, wet, -8 if wet else 0)
        return
    rock = lambda x, z: (k.cell.world.get((x, z)) or (None, None))[1] == 'rock'
    for wx, wz, n in rocks:
        if not _in_cell(k.cell, wx, wz): continue
        tx, tz = wx - k.cell.X, wz - k.cell.Z
        wet = any(k.cls(tx + dx, tz + dz) in WATER for dx in range(-1, n + 1) for dz in range(-1, n + 1))
        # faces that a neighbouring rock hides (Sapphire's sea routes are lined with rows of rocks): south slope 0,
        # east 3, west 4, south-west corner 6, south-east corner 7 (_IWA order)
        w_ = all(rock(wx - 1, wz + i) for i in range(n)); e_ = all(rock(wx + n, wz + i) for i in range(n))
        s_ = all(rock(wx + i, wz + n) for i in range(n))
        skip = {i for i, hid in ((0, s_), (3, e_), (4, w_), (6, w_ and s_), (7, e_ and s_)) if hid}
        boulder(m, X(tx) + 8 * n, Z(tz) + 8 * n, 16 * n + (2 if n == 2 else 0), wet, 22 if n == 2 else 14, skip)

def round_tree(m, cx, zb, w, h=1.0):
    """Black 2's round tree (ki03, Route 6; build_chunk.tree_row) centred at x cx with its base row ending at z zb,
    w units across (32 for a normal 2x2 tree), heights scaled by h."""
    x0, x1, z0, z1 = cx - w / 2, cx + w / 2, zb - w, zb
    zc = (z0 + z1) / 2
    sq = lambda mat, y: face(m, mat, [(x0, y, z1, 0, 0), (x1, y, z1, 1, 0), (x1, y, z0, 1, 1), (x0, y, z0, 0, 1)], UP)
    sq('ki02c', 4)          # as build_chunk.tree_row (2 clear of the tall-grass layers)
    for verts in ([(x0, 3, zc, 0, 0), (x1, 3, zc, 1, 0), (x1, 56 * h, zc, 1, 1), (x0, 56 * h, zc, 0, 1)],
                  [(cx, 3, z1, 1, 0), (cx, 3, z0, 0, 0), (cx, 56 * h, z0, 0, 1), (cx, 56 * h, z1, 1, 1)]):
        m.quad('ki03ax', verts)     # (one face: the cards are drawn from both sides, nsbmd_fix.tree_materials)
    sq('ki03bx', 23 * h); sq('ki03dx', 46 * h)

def draw_trees(m, k):
    """other:big_tree (Fortree 3x2 canopy on a 1-wide trunk, Mossdeep 3x3): one round tree as wide as the group,
    centred on it, base on its south row, heights x1.5. other:tree_top_1wide: the crown of a 1-tile-wide tree whose
    trunk is the tile below: a round tree 1.25 tiles across, base on the tile below."""
    _, comps = _world_groups(k.cell.world)
    for comp in comps['other:big_tree']:
        xs = [p[0] for p in comp]; zs = [p[1] for p in comp]
        ax, az = min(xs), max(zs)
        if not _in_cell(k.cell, ax, az): continue
        w = (max(xs) - min(xs) + 1) * T
        tmp = type(m)(m.name)
        P = sys.modules.get('terrain.palms')
        if P and P.is_palm(k.cell.world, ax, az):     # Mossdeep: Black 2's Humilau palm, as wide as the group
            P.palm(tmp, X(min(xs) - k.cell.X) + w / 2, Z(max(zs) - k.cell.Z + 1) - w / 2, w / 32)
        else: round_tree(tmp, X(min(xs) - k.cell.X) + w / 2, Z(max(zs) - k.cell.Z + 1), w, 1.5)
        _as_one(m, tmp, k.cell, comp)
    rows = {}               # one row of narrow trees per run (per-tile trees 20 wide overlapped and z-fought)
    for tx, tz in k.tiles('other:tree_top_1wide'): rows.setdefault(tz, []).append(tx)
    for tz, xs in rows.items():
        for a, b in runs(xs):
            tmp = type(m)(m.name)
            k.cell.bc.narrow_tree_row(tmp, a, Z(tz + 2), b + 1 - a)   # (Black 2's tree scaled evenly to a tile)
            _as_one(m, tmp, k.cell, [(k.cell.X + x, k.cell.Z + z) for x in range(a, b + 1) for z in (tz, tz + 1)])

def _as_one(m, tmp, cell, tiles):
    """Add tmp's triangles to m so that, after world.py's lift (each triangle by the height of the tile under its
    centre), the whole object stands at the lowest height of its world tiles: a tree on two levels was torn in two
    (exterior sweep 2026-10-06). Without the heights module this is a plain copy."""
    import sys
    h = sys.modules.get('terrain.heights')
    F = getattr(h, 'FIELD', None) if h else None
    if F is None: m.extend(tmp); return
    base = min(F.y(*t) for t in tiles)
    for mat, tris in tmp.tris.items():
        for t in tris:
            for lift, piece in F.pieces(t, cell.X, cell.Z):      # (the pieces world.py's lift will raise)
                m.tris.setdefault(mat, []).append([(x, y + base - lift, z, u, v, c) for x, y, z, u, v, c in piece])

def draw_props(m, k):
    """prop: Sapphire's town objects (lamps, fountains, statues, stall counters, boat hulls, gravestones...) have no
    single Black 2 equivalent; each east-west run of solid prop tiles gets a low stone plinth (Accumula wall stone
    t02_kabe01 sides, paving t02michi_b top, 12 units high, 2 units inside the tiles) so it reads as an obstacle;
    walk-behind prop tops get nothing. Town agents can replace them with models (data/towns props)."""
    rows = {}
    # (+ Slateport's stall posts, the solid awning tiles in front of a stall: the stall's counter beside its seller;
    # walkability 2026-10-11: bare paving you could not walk on)
    for tx, tz in list(k.tiles('prop')) + list(k.tiles('other:market_awning')):   # (not on a tile that holds a
        if not k.walk(tx, tz) and not face_tile(k, tx, tz): rows.setdefault(tz, []).append(tx)   # cliff face: draw_walls)
    rows = {tz: sorted(set(xs)) for tz, xs in rows.items()}
    for tz, xs in rows.items():
        for a, b in runs(xs):
            x0, x1, z0, z1 = X(a) + 2, X(b + 1) - 2, Z(tz) + 2, Z(tz + 1) - 2
            L = (x1 - x0) / T
            flat(m, 't02michi_b', x0, z0, x1, z1, 12, lambda x, z: ((x + HALF) / 32, -(z + HALF) / 32))
            face(m, 't02_kabe01', [(x0, 0, z1, 0, .8), (x1, 0, z1, L, .8), (x1, 12, z1, L, 1), (x0, 12, z1, 0, 1)], SOUTH)
            for x, n in ((x0, WEST), (x1, EAST)):
                face(m, 't02_kabe01', [(x, 0, z0, 0, .8), (x, 0, z1, .75, .8), (x, 12, z1, .75, 1), (x, 12, z0, 0, 1)], n)

def draw_other(m, k):
    # berry soil: Accumula's tree pit (t02_ki_sita, soil in a stone frame, chunk 5), one per tile
    for tx, tz in k.tiles('other:berry_soil'):
        flat(m, 't02_ki_sita', X(tx), Z(tz), X(tx + 1), Z(tz + 1), 0, lambda x, z: ((x - X(tx)) / T, 1 - (z - Z(tz)) / T))
    # beach chairs: a wooden lounger (Accumula's bench slats, nagaisu) per vertical run, back raised at the north end
    for c, back in (('other:beach_chair', 10), ('other:beach_mat', 1)):
        cols = {}
        for tx, tz in k.tiles(c): cols.setdefault(tx, []).append(tz)
        for tx, zs in cols.items():
            for a, b in runs(zs):
                x0, x1, z0, z1 = X(tx) + 3, X(tx + 1) - 3, Z(a) + 2, Z(b + 1) - 2
                zm = z0 + 12 if back > 1 else z0
                face(m, 'nagaisu', [(x0, 3, z1, 0, 0), (x1, 3, z1, 1, 0), (x1, 3, zm, 1, 0.6), (x0, 3, zm, 0, 0.6)], UP)
                if back > 1:
                    face(m, 'nagaisu', [(x0, 3, zm, 0, 0.6), (x1, 3, zm, 1, 0.6), (x1, 3 + back, z0, 1, 1), (x0, 3 + back, z0, 0, 1)], (0, 1, 1))
    # Acro Bike rails (Route 119, the Safari Zone) are walked now: concrete decks (draw_decks, the white of Sapphire's
    # rails); Sapphire's posts below them (the support tiles) are thin pillars of the deck's grey side (hashi02a u
    # 0.22..0.34) from under the deck's 8-unit side face down into the water (drawn under them: water_under)
    for tx, tz in k.tiles('other:acro_bike_rail_support'):
        if k.cls(tx, tz - 1) != 'other:acro_bike_rail' or water_under(k.cell.world, k.cell.X + tx, k.cell.Z + tz) is None:
            continue                 # (over land, e.g. the Safari Zone's, heights.py's cliff face stands there)
        x0, z0 = X(tx) + 6, Z(tz) + 2
        face(m, 'hashi02a', [(x0, -8, z0, 0.34, 0), (x0 + 4, -8, z0, 0.34, 0.25), (x0 + 4, -40, z0, 0.22, 0.25),
                              (x0, -40, z0, 0.22, 0)], SOUTH)
    # bumpy slopes (Jagged Pass, the Safari Zone): Sapphire's round stones, low enough to walk over (3 units: a stone
    # path through the ledge band, as Black 2 leaves a gap in its own ledge lines where a path goes up)
    for tx, tz in k.tiles('other:acro_bike_stepping_stone'):
        boulder(m, X(tx) + 8, Z(tz) + 8, 14, False, 3)
    # archway (Ever Grande): an open pergola of Black 2's bridge planks: wooden posts on the solid ends, a beam along
    # the front and back at y 32..40 and one 5-unit slat per tile column between them, so a player walking under it
    # stays visible between the slats (Gen 5's camera looks down from the south)
    _, comps = _world_groups(k.cell.world)
    for comp in comps['other:archway']:
        xs = [p[0] for p in comp]; zs = [p[1] for p in comp]
        if not _in_cell(k.cell, min(xs), min(zs)): continue
        ox, oz = k.cell.X, k.cell.Z
        x0, x1, z0, z1 = X(min(xs) - ox), X(max(xs) - ox + 1), Z(min(zs) - oz), Z(max(zs) - oz + 1)
        L = (x1 - x0) / T
        for zb in (z0, z1 - 4):
            flat(m, 'hashi01a', x0, zb, x1, zb + 4, 40, lambda x, z: (0.34 + 0.63 * (z - zb) / 4, (x + HALF) / T))
            face(m, 'hashi01a', [(x0, 32, zb + 4, 0.34, 0), (x1, 32, zb + 4, 0.34, L), (x1, 40, zb + 4, 0.22, L), (x0, 40, zb + 4, 0.22, 0)], SOUTH)
        for wx in range(min(xs), max(xs) + 1):
            xc = X(wx - ox) + 8
            flat(m, 'hashi01a', xc - 2.5, z0 + 4, xc + 2.5, z1 - 4, 41, lambda x, z: (0.34 + 0.63 * (x - xc + 2.5) / 5, -(z + HALF) / T))
        for (wx, wz) in comp:
            if world_walk(k.cell, wx, wz): continue
            px, pz = X(wx - ox) + 8, Z(wz - oz) + 8
            for verts, n in (([(px - 3, 0, pz + 3, 0.22, 0), (px + 3, 0, pz + 3, 0.28, 0), (px + 3, 32, pz + 3, 0.28, 2), (px - 3, 32, pz + 3, 0.22, 2)], SOUTH),
                             ([(px - 3, 0, pz - 3, 0.22, 0), (px - 3, 0, pz + 3, 0.28, 0), (px - 3, 32, pz + 3, 0.28, 2), (px - 3, 32, pz - 3, 0.22, 2)], WEST),
                             ([(px + 3, 0, pz - 3, 0.22, 0), (px + 3, 0, pz + 3, 0.28, 0), (px + 3, 32, pz + 3, 0.28, 2), (px + 3, 32, pz - 3, 0.22, 2)], EAST)):
                face(m, 'hashi01a', verts, n)
    # market awnings (Slateport): a plank canopy at y 30 over each stall's awning tiles, front edge facing south
    for comp in comps['other:market_awning']:
        xs = [p[0] for p in comp]; zs = [p[1] for p in comp]
        if not _in_cell(k.cell, min(xs), min(zs)): continue
        ox, oz = k.cell.X, k.cell.Z
        for (wx, wz) in comp:
            if not world_walk(k.cell, wx, wz): continue          # (a solid one is a stall post: draw_props' counter)
            x0, x1, z0, z1 = X(wx - ox), X(wx - ox + 1), Z(wz - oz), Z(wz - oz + 1)
            face(m, 'hashi01a', [(x0, 26, z1, 0.34, 0), (x1, 26, z1, 0.97, 0), (x1, 32, z0, 0.97, 1), (x0, 32, z0, 0.34, 1)], (0, 1, 1))
            if (wx, wz + 1) not in comp or not world_walk(k.cell, wx, wz + 1):
                face(m, 'hashi01a', [(x0, 22, z1, 0.22, 0), (x1, 22, z1, 0.22, 1), (x1, 26, z1, 0.28, 1), (x0, 26, z1, 0.28, 0)], SOUTH)

def world_walk(cell, wx, wz):
    e = cell.world.get((wx, wz))
    return bool(e and e[2])

def ground_cover(cell):
    """Cell tiles whose ground this module draws itself at ground level (opaque: sand, desert, ash ground, decks and
    the Cycling Road with its railings, berry soil): world.py leaves its grass out there, as Black 2 cuts its ground
    under paths (Nuvema chunk 0). Layers 0.25-1 unit over the grass flickered in melonDS."""
    k = Ctx(cell)
    out = set()
    for tz in range(32):
        for tx in range(32):
            c = k.cls(tx, tz)
            if c in ('sand', 'ash_grass', 'bridge', 'bike_path', 'other:acro_bike_rail', 'other:berry_soil') + BEACH_PROPS or _road_edge(k, tx, tz):
                out.add((tx, tz))
            elif (cell.X + tx, cell.Z + tz) in sand_under(cell.world) or (cell.X + tx, cell.Z + tz) in deck_under(cell.world) or \
                    (c in ('path', 'wall', 'fence') and pier_tile(cell.world, cell.X + tx, cell.Z + tz)) or \
                    (cell.X + tx, cell.Z + tz) in paved_tiles(cell.world):
                out.add((tx, tz))           # (a building, tree or rock standing on sand: draw_sand)
            elif c == 'other:acro_bike_rail_support' and water_under(cell.world, cell.X + tx, cell.Z + tz):
                out.add((tx, tz))           # (a rail's posts standing in the water, as Sapphire draws them)
    return out

def draw(m, cell):
    k = Ctx(cell)
    present = {k.cls(tx, tz) for tz in range(32) for tx in range(32)} & CLASSES
    draw_sand(m, k)                  # (also the sand under buildings, trees and rocks on sand: sand_under)
    draw_pier(m, k)
    draw_paving(m, k)
    if 'ash_grass' in present: draw_ash(m, k)
    if 'long_grass' in present: (draw_dark_grass if LONG_GRASS == 'dark' else draw_long_grass)(m, k)
    if present & {'bridge', 'bike_path', 'other:bridge_support', 'other:acro_bike_rail'} or 'fence' in present: draw_decks(m, k)
    if 'fence' in present: draw_fences(m, k)
    if 'other:bridge_support' in present: draw_road_rails(m, k)
    if 'wall' in present: draw_walls(m, k)
    if 'bush' in present: draw_bushes(m, k)
    if present & {'prop', 'other:market_awning'}: draw_props(m, k)
    draw_rocks(m, k)
    draw_trees(m, k)
    if present & {'other:' + o for o in OTHER}: draw_other(m, k)

# ------------------------------------------------------------------------------------- water under decks (for water.py)
DECKS = {'bridge'}
ACRO = {'other:acro_bike_rail', 'other:acro_bike_stepping_stone'}   # Sapphire's Acro Bike tiles, walked (collision)

def retile(world, maps):
    """world.py hook (after compose): a column of Sapphire's bumpy slopes that joins two levels (the walkable tiles
    beyond its ends at different Sapphire elevations: the Safari Zone's northeast, a 32-unit climb) becomes stairs,
    which heights.py builds as Black 2's 45-degree steps (kaidan01a, the way Black 2 climbs a level); a column within
    one level (all of Jagged Pass's: its ledge bands keep level) stays a stepping-stone path."""
    stones = {k for k, e in world.items() if e[1] == 'other:acro_bike_stepping_stone'}
    done = set()
    for k in sorted(stones):
        if k in done: continue
        comp, todo = set(), [k]
        while todo:
            p = todo.pop()
            if p in comp or p not in stones: continue
            comp.add(p); todo += [(p[0] + dx, p[1] + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        done |= comp
        name = world[k][0]; mp = maps.get(name)
        if mp is None: continue
        def elev(p):
            x, y = p[0] - mp['ox'], p[1] - mp['oz']
            if (p in world and world[p][2] and p not in comp and 0 <= y < mp['h'] and 0 <= x < mp['w']):
                return mp['plan']['elevation'][y][x]
        xs = {p[0] for p in comp}
        ends = [elev((x, z)) for x in xs for z in (min(p[1] for p in comp) - 1, max(p[1] for p in comp) + 1)]
        ends = {e for e in ends if e not in (None, 0, 15)}
        if len(ends) > 1:
            for p in comp: world[p] = (world[p][0], 'stairs', True)
RAIL = {'other:acro_bike_rail', 'other:acro_bike_rail_support'}
ROAD = {'bike_path', 'other:bridge_support'}

def water_under(world, wx, wz):
    """For the water module: a world tile of a bridge deck or of the Cycling Road (with its supports and railings) that
    stands over water returns the position of a water tile next to it (whose look the deck tile should copy), else
    None. A deck tile touching walkable land is a bridge end (ground under it, as Black 2's bridges rest on the bank);
    otherwise it is over water when a 4-neighbour is surface water, or (inside a wide deck or a junction) when going
    straight out in two or more directions the first tile past the deck is water. Black 2 draws its bridges the same
    way: the deck at the land's height, water continuing 8 units below it (Route 3 chunk 15, Route 14 chunk 95)."""
    e = world.get((wx, wz))
    if not e: return None
    cls_at = lambda x, z: (world.get((x, z)) or (None, None))[1]
    on_road = lambda x, z: cls_at(x, z) in ROAD or (cls_at(x, z) == 'fence' and any(
        cls_at(x + dx, z + dz) in ROAD for dx in (-1, 0, 1) for dz in (-1, 0, 1)))
    du = deck_under(world)
    if e[1] in DECKS or (wx, wz) in du: member = lambda x, z: cls_at(x, z) in DECKS or (x, z) in du
    elif e[1] in RAIL: member = lambda x, z: cls_at(x, z) in RAIL     # (walked rails and their posts: water under them)
    elif on_road(wx, wz): member = on_road
    else: return None
    land = lambda x, z: bool(world.get((x, z)) and world[(x, z)][2]) and cls_at(x, z) not in WATER
    wet, far = None, []
    for dx, dz in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        x, z = wx + dx, wz + dz
        if member(x, z):
            for _ in range(8):                  # straight out past the deck
                x, z = x + dx, z + dz
                if not member(x, z): break
            if cls_at(x, z) in SURFACE: far.append((x, z))
        elif land(x, z): return None
        elif cls_at(x, z) in SURFACE: wet = wet or (x, z)
    return wet or (far[0] if len(far) >= 2 else None)

# ------------------------------------------------------------------------------------------------------- collision
_POS = {}
def _pos(cell, tile):
    """Cell-local position of a tile tuple (world.py passes the tuple, not its position; tuples are unique per tile)."""
    key = (cell.cx, cell.cz)
    if key not in _POS:
        _POS.clear(); _POS[key] = {id(cell.get(tx, tz)): (tx, tz) for tz in range(32) for tx in range(32) if cell.get(tx, tz)}
    return _POS[key].get(id(tile))

_KIND = {}
def is_town(name):
    """Town/city maps get Black 2's town floor (0x00), routes the route floor, as world.py does (hoenn_zones.json)."""
    if not _KIND:
        import os, json
        p = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hoenn_zones.json')
        _KIND.update({n: z['type'] in ('MAP_TYPE_TOWN', 'MAP_TYPE_CITY') for n, z in json.load(open(p))['maps'].items()})
    return _KIND.get(name, False)

def walk_floor(name):
    return FLOOR if is_town(name) else ROUTE

def collision(cls, tile, cell):
    name, c, walkable = tile
    if c == 'sand' or c in BEACH_PROPS:
        if not walkable: return SOLID, '#'
        p = _pos(cell, tile)
        beh = sapphire_behaviour(name, cell.X + p[0], cell.Z + p[1]) if p else None
        if name in DESERT_MAPS:     # Route 4's desert: deep sand where Sapphire has encounters (MB_UNUSED_DEEP_SAND)
            return (DEEP_SAND, 'g') if beh == MB_DEEP_SAND else (DESERT_SAND, 's')
        if beh == MB_SAND or beh is None: return BEACH, 's' # Sapphire's MB_SAND (footprints): beach sand
        return (FLOOR if is_town(name) else SAND_PATH), ':' # sand-coloured ground without footprints (beh 0x00)
    if c == 'ash_grass':
        return (TALL_GRASS, 'g') if walkable else (SOLID, '#')   # MB_ASHGRASS has wild encounters in Sapphire
    if c == 'long_grass':
        if not walkable: return SOLID, '#'
        p = _pos(cell, tile)
        if p and sapphire_behaviour(name, cell.X + p[0], cell.Z + p[1]) == MB_LONG_GRASS_SOUTH_EDGE:
            return ROUTE, ':'       # Sapphire's long-grass south edge (0x09) has no wild encounters
        return TALL_GRASS, 'g'
    if c in ('bike_path',):
        return (FLOOR, '=') if walkable else (SOLID, '#')
    if c == 'bridge':
        # Black 2's bridges over water are plain floor at the land's height: Route 3's wooden bridge 0x03 (chunks
        # 15/16), Route 14's 0x00 (chunk 95), Route 8's concrete one 0x00 (chunk 69); no exit-block classes (those are
        # only on the Humilau / Route 22 piers, chunks 300/302). So surfers can land on a deck and surf off it again.
        if not walkable: return SOLID, '#'
        return (FLOOR if is_town(name) else SAND_PATH), '='
    if c == 'fence':
        p = _pos(cell, tile)
        if walkable and name != 'Route110' and p: return walk_floor(name), '.'
        return SOLID, '#'
    if c in ACRO:
        # One bike, no Acro Bike (user decision 2026-10-07): Sapphire's Acro-only tiles (rails and bumpy slopes, which
        # pokeruby field_player_avatar.c check_acro_bike_metatile closes to a player on foot) are walked: a rail is a
        # deck like Black 2's bridges (plain floor at the deck's height: Route 8's concrete bridge 0x00, Route 3's
        # wooden one 0x03), a bumpy slope a stepping-stone path through its ledge band (route floor)
        if not walkable: return SOLID, '#'
        return ((FLOOR if is_town(name) else SAND_PATH), '=') if c == 'other:acro_bike_rail' else (walk_floor(name), '.')
    if c in ('wall', 'other:bridge_support', 'other:acro_bike_rail_support'):
        return SOLID, '#'
    # rock, bush, prop, the forest entrance and the other props keep Sapphire's own collision bit
    return (walk_floor(name), '.') if walkable else (SOLID, '#')

# ------------------------------------------------------------------------------------------------------ placements
# Black 2 building models already in exterior pack 0 (no pack budget used): res id -> name
O_PARASOL, O_CHAIR = 26, 25

def placements(cell):
    """Building-model props for this cell: [(res, wx, wz, rot_degrees, y)], world tile coordinates (fractional) of
    the model origin, the same convention as world.py's put(). Beach umbrellas: pack 0's o_parasol_01 (res 26, the
    parasol Black 2 places in chunks 18 and 835) at the centre of each umbrella's 2x3-tile group (13 on Route 109, all in
    cell (8, 12); a chunk holds at most 32 placements, notes/TERRAIN_GROUND.md)."""
    _, comps = _world_groups(cell.world)
    out = []
    for comp in comps['other:beach_umbrella']:
        xs = [p[0] for p in comp]; zs = [p[1] for p in comp]
        wx, wz = (min(xs) + max(xs) + 1) / 2, (min(zs) + max(zs) + 1) / 2
        if int(wx) // 32 == cell.cx and int(wz) // 32 == cell.cz:
            out.append((O_PARASOL, wx, wz, 0, 0))
    return out
