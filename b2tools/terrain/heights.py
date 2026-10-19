"""Hoenn's height levels: raised ground, cliff faces, cliff tops, stairs, east/west ledges, mountains, cave mouths
(notes/TERRAIN_HEIGHTS.md has the mechanism and the evidence for every recipe).

How Black 2 does heights (decomp, the user's chunks, the emulator):
- every collision tile is a plane: y = -(nx*x - nz*z + d) / ny, normal from MAP_HEIGHT_SLOPE_TABLE and d from
  MAP_HEIGHT_OFFSET_TABLE (overlay 36), x/z relative to the chunk centre (FieldChunkAccessor_GetTerrainCore);
- an actor may step onto a tile whose height differs from its own by less than 20 units
  (ActorRouteCollCheckCore, bw2/src/ov012/field_actor_tool.c), so stairs are 45-degree slope tiles (16 per tile);
- cliffs stand in solid tiles at the LOW height next to the high ground (Route 1 chunk 2, Route 20 chunk 287,
  Route 19 chunk 282); classes 0x51-0x58 wall off sides of a walkable tile (TileExitBlockCheck_*, ov036);
- side ledges are the south ledge turned 90 degrees: classes 0x72 (jump east) / 0x73 (jump west), flags 0x0001,
  same height on both sides (Route 20 chunk 286, Route 19 chunk 282).

How Hoenn's levels are found (Sapphire's own data: data/plans 'elevation' = pokeruby blockdata bits 12-15):
- walkable regions of one Sapphire elevation are flat: 3 = level 0, 4 = +16, 5 = +32 ...; elevation 0/15 tiles join
  their neighbours, and where they join two levels those stand level (Gen 3 walks across: no cliff there);
- heights per region come from constraints, strongest first: stairs between two elevations keep that difference,
  junctions keep level, ledges keep level (both sides), stairs inside one elevation climb one level a row to the
  north; regions on the sea stay at Sapphire's level (the sea stays level); contradictions are dropped (F.notes);
- unwalkable cliff tops and mountains (what a 2x2 block covers) rise a level above the ground at their rim
  (mountains in terraces three tiles deep), cliff tiles take the lowest height next to them and hold the face,
  water takes its nearest shore's height;
- walkable neighbours that Sapphire keeps apart (elevation mismatch) but that end up < 20 units apart get side walls.

Module interface: b2tools/terrain/__init__.py, plus height_field(world, maps, cfg, trees) which world.py calls once
(the returned Field gives every tile's height, collision records, ground textures and the lift for other modules).
"""
import os, sys, json, struct
from collections import deque, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')

CLASSES = {'cliff', 'cliff_top', 'stairs', 'ledge_e', 'ledge_w', 'ledge_cap', 'mountain', 'cave_entrance',
           'cracked_floor', 'mud'}
# every texture is already in Hoenn's map set (a/0/1/4 entry 3, area 2 summer): listing them costs 0 bytes
TEXTURES = {t: 3 for t in ('gake01a', 'gake1_0', 'gake1_1', 'gake_michi', 'yamagake01', 'kaidan01a', 'doukutu01',
                           'dansa01a', 'gake_futa')}
WRAP = {'gake01a': ('WRAP', 'CLAMP'), 'gake1_0': ('WRAP', 'CLAMP'), 'gake1_1': ('WRAP', 'CLAMP'),
        'yamagake01': ('WRAP', 'WRAP'), 'kaidan01a': ('CLAMP', 'WRAP'), 'doukutu01': ('CLAMP', 'WRAP'),
        'dansa01a': ('WRAP', 'CLAMP'), 'gake_michi': ('WRAP', 'WRAP'), 'gake_futa': ('WRAP', 'WRAP')}

# Rock styles (2026-10-07, user choice): Sapphire's red volcanic rock - the own metatiles of gTileset_Lavaridge on
# Route 112's mountain (Fiery Path, the cable car, Mt. Chimney's slopes) and round Lavaridge - in Black 2's red rock of
# Reversal Mountain's outside (zone 461, chunks 298/246, summer set 227): faces out57_gake01a, rock lips out57_gake1_0,
# rock tops out57_futa, rock ground out57_yuka01, cave mouth out57_doukutu (the same stand-ins as Jagged Pass's and
# Mt. Chimney's 'retex', data/hoenn_standalone.json). Its cliffs are stacked 16-unit tiers (12-unit face, v 0..1 with
# 2 transparent foot rows, + 4-unit lip; no tall-wall texture [bytes]): a tall face (yamagake01 elsewhere) is
# out57_gake01a in 16-unit bands of its opaque rows. Grass lips (gake1_1) and stairs stay as they are (green tops;
# Sapphire's stairs there are grey stone). The warp-only Jagged Pass / Mt. Chimney already have their whole group
# retextured (not listed here).
STYLES = {'red': dict(tileset='gTileset_Lavaridge', maps={'Route112', 'LavaridgeTown'},
                      tex={'gake01a': 'out57_gake01a', 'gake1_0': 'out57_gake1_0', 'gake_futa': 'out57_futa',
                           'gake_michi': 'out57_yuka01', 'yamagake01': 'out57_gake01a', 'doukutu01': 'out57_doukutu'})}
TEXTURES.update({t: 227 for t in ('out57_gake01a', 'out57_gake1_0', 'out57_futa', 'out57_yuka01', 'out57_doukutu')})
WRAP.update({'out57_gake01a': WRAP['gake01a'], 'out57_gake1_0': WRAP['gake1_0'], 'out57_futa': WRAP['gake_futa'],
             'out57_yuka01': WRAP['gake_michi'], 'out57_doukutu': WRAP['doukutu01']})

LEVEL = 16                        # units per Sapphire elevation step (= one row of Gen 3 cliff face, one 45-degree stair)
WATER = {'water', 'deep_water', 'current_n', 'current_s', 'current_e', 'current_w', 'waterfall'}
NOLAND = 0x4000     # collision flag (u32 bit 30): no surf landing here (hm_free.py SurfLandingTileType; no Black 2 code
                    # tests flag bits 9-14: ov036's GetTileFlags users test 0x01/0x02/0x04/0x08/0x20/0x40/0x100)
BLOCK = WATER | {'sign', 'building', 'door'}
CONNECT = {'stairs', 'mud'}                       # walkable tiles that join two levels (slope tiles)
LEDGES = {'ledge_s', 'ledge_n', 'ledge_e', 'ledge_w'}
FACE = {'cliff', 'cave_entrance'}                 # rock faces: take the low side's height and hold the profile
HIGHLAND = {'cliff_top', 'mountain'}              # unwalkable plateau / mountain scenery
JUMP = {'ledge_s': (0, 1), 'ledge_n': (0, -1), 'ledge_e': (1, 0), 'ledge_w': (-1, 0)}
# Maps whose plank walkways (class bridge) run through the tree tops on posts (map_glitch_fix 2026-10-09): Fortree, Sapphire's
# tree-house town (its walkways and tree houses at elevation 4 over the forest floor, ladders down). The walkways and their
# ladders keep their heights (collision unchanged) but no longer lend them to the solid tiles round them (step 7): the
# forest, the clearings and the tree houses' tiles stand on the forest floor, the decks on posts over it (ground.py
# pier_posts, open_under). Before, the solid tiles took the walkway's height: every walkway was an earth bank with grass
# cliffs, and the tree houses (models_fortree.py) stood on those banks' edges, their roofs over the cliff faces
STILTS = {'FortreeCity'}

# ---- Black 2's height tables (overlay 36 of the user's dump; symbols from the decomp's config) --------------------
OV36 = os.path.join(ROOT, 'external', 'pokebw2', 'extract', 'b2_us', 'arm9_overlays', 'ov036.bin')
OV36_BASE, SLOPE_TABLE, OFFSET_TABLE = 0x0217f600, 0x021d2a04, 0x021d3174    # .text start, MAP_HEIGHT_*_TABLE
_ov = open(OV36, 'rb').read()
OFFS = struct.unpack_from('<1285i', _ov, OFFSET_TABLE - OV36_BASE)
_sl = struct.unpack_from('<951h', _ov, SLOPE_TABLE - OV36_BASE)
NORMALS = [_sl[i * 3:i * 3 + 3] for i in range(317)]
# slope table index for a plane rising `rise` units per tile towards a side (checked: B2 stairs use 8 (Accumula,
# north) and 11 (Route 19, east); 26.6/63.4-degree ones for 8/32 per tile)
SLOPES = {('n', 16): 8, ('n', 8): 20, ('n', 32): 32, ('s', 16): 14, ('s', 8): 6, ('s', 32): 33,
          ('e', 16): 11, ('e', 8): 1, ('e', 32): 30, ('w', 16): 16, ('w', 8): 7, ('w', 32): 31}

def plane_record(slope, x, y, z):
    """(u16 a, u16 b) of a collision tile whose plane has slope index `slope` and passes through chunk-centred point
    (x, y, z): the offset index whose d gives that plane (y = -(nx*x - nz*z + d)/ny, GetTerrainCore)."""
    nx, ny, nz = NORMALS[slope]
    d = -(nx * x - nz * z + ny * y)
    best = min(range(len(OFFS)), key=lambda i: abs(OFFS[i] - d))
    assert abs(OFFS[best] - d) / ny < 0.75, f'no height offset for slope {slope} through {x, y, z}'
    return slope << 2, best

_flat = {}
def flat_index(y):
    if y not in _flat: _flat[y] = plane_record(0, 0, y, 0)[1]
    return _flat[y]

# tile classes that wall off sides of a walkable tile (ov036 TileExitBlockCheck_Up/Down/Left/Right, 0x021a2d58..)
WALL_CLASS = {frozenset('e'): 0x51, frozenset('w'): 0x52, frozenset('n'): 0x53, frozenset('s'): 0x54,
              frozenset('ne'): 0x55, frozenset('nw'): 0x56, frozenset('se'): 0x57, frozenset('sw'): 0x58}

# ---- Sapphire data -----------------------------------------------------------------------------------------------
def _sapphire_grids(maps, cfg):
    """Per world tile: Sapphire elevation and (tilesets, metatile) - from the plan's 'elevation' (converter/plan_map.py)
    or, for plans made before it had one, pokeruby's blockdata directly."""
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from gba import world_repo
    repo = world_repo()            # (Repo(pokeruby); HOENN_VERSION=emerald: Emerald's maps, converter/gba.py world_repo)
    elev, mtile = {}, {}
    for name, mp in maps.items():
        plan, ox, oz = mp['plan'], mp['ox'], mp['oz']
        mj = repo.map_json(name); g, lay = repo.layout_grid(mj['layout'])
        E = plan.get('elevation') or [[(int(v) >> 12) & 15 for v in row] for row in g]
        ts = (lay['primary_tileset'], lay['secondary_tileset'])
        H, W = plan['size'][1], plan['size'][0]
        pad = cfg.get('pad_north', {}).get(name, 0)
        for y, src in [(y, y) for y in range(H)] + [(-pad + k, k % 2) for k in range(pad)]:
            for x in range(W):
                elev[(ox + x, oz + y)] = E[src][x]
                mtile[(ox + x, oz + y)] = (ts, int(g[src, x]) & 0x3FF)
        for k, v in mp.get('border', {}).items():      # a warp-only map's border tiles (world.py compose_group):
            elev.setdefault(k, 0); mtile.setdefault(k, v)  # Sapphire's border block metatile, no elevation
    return elev, mtile, repo

_colour = {}
def _rocky(repo, ts, m):
    """True when Sapphire draws this metatile in rock/earth colours (brown cliff tops), False for green ones."""
    if (ts, m) not in _colour:
        from gba import MetatileRenderer
        r = _colour.setdefault(('r',) + ts, None) or MetatileRenderer(repo, *ts)
        _colour[('r',) + ts] = r
        px = r.render(m)[..., :3].reshape(-1, 3).astype(float).mean(0)
        _colour[(ts, m)] = not (px[1] > px[0] + 6 and px[1] > px[2])
    return _colour[(ts, m)]

SEA_ROCK = {'cliff', 'cliff_top', 'mountain'}
TERRACES = int(os.environ.get('HOENN_SEA_ROCK_TERRACES', '1'))   # levels the sea's rock masses rise (raise_sea_rock;
# a second terrace 4 tiles in left 1-25 px cracks at its diagonal corners in the camera views, outdoor_check view)
SHALLOWS = {'puddle', 'water_edge'}               # (shoals: Route 127's reefs stand in them)
def sea_rock_masses(world):
    """Tiles of the 4-connected masses of cliff / cliff-top / mountain tiles that touch surface water and no land:
    every neighbour outside the mass is water, a shoal, a rock or an unwalkable tile (walkable cliff tops inside a mass
    count as the mass: Sapphire marks some passable, but nothing reaches them)."""
    out, seen = set(), set()
    for k0, e0 in world.items():
        if k0 in seen or e0[1] not in SEA_ROCK: continue
        comp, q, ok, wet = [k0], deque([k0]), True, False
        seen.add(k0)
        while q:
            x, z = q.popleft()
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                en = world.get(n)
                if en is None: continue
                if en[1] in SEA_ROCK:
                    if n not in seen: seen.add(n); q.append(n); comp.append(n)
                elif en[1] in WATER or en[1] in SHALLOWS: wet = True
                elif en[2] and en[1] not in ('rock', 'sand'): ok = False     # (a beach round the rock is no land:
                #   Route 127's island, pink rock in a sand ring, was a grass field)
        if ok and wet: out.update(comp)
    return out

def raise_sea_rock(F, world, nb):
    """The sea's rock masses rise as Sapphire's rock piles do: the rim (tiles touching anything outside the mass) keeps
    its height and holds the faces, the tiles inside rise a level over the water's tile height, and one more every three
    tiles further in (at most three levels: a 3x3 pile is a peak over its centre, the reefs of Routes 124-127 terraced
    masses; never lower than they were). The water around keeps its level. Drawing only: the
    collision records keep the heights the tiles had (F.coll_h, Field.record), so collision.per does not change."""
    left = set(F.sea_rock)
    while left:
        comp, q = set(), deque([left.pop()])
        while q:
            p = q.popleft(); comp.add(p)
            for n in nb(p):
                if n in left: left.discard(n); q.append(n)
        water = [F.y(*n) for p in comp for n in nb(p) if n not in comp and (world.get(n) or (0, 0))[1] in WATER | SHALLOWS]
        if not water: continue
        base = min(water)
        # small masses (Sapphire's big pointed sea rocks, 2x2 to 4x4 tiles) between waters at most a level apart are
        # Black 2's searock card, scaled to the mass (terrain/ground.py draw_rocks), standing in the water (F.card_mass,
        # drawn at the water's level by lower_rocks): no rock block
        xs, zs = [p[0] for p in comp], [p[1] for p in comp]
        if len(comp) <= 12 and max(xs) - min(xs) < 4 and max(zs) - min(zs) < 4 and max(water) - base <= LEVEL:
            # (sweep_outdoor 2026-10-11) Sapphire's rock-class tiles at the mass's corners, inside its box, are the same
            # big rock (Route 125's at (22-25, 29-32)): they join the card instead of drawing four small rock cards
            # through it, one of them with a rock face block
            box = lambda n: min(xs) <= n[0] <= max(xs) and min(zs) <= n[1] <= max(zs)
            comp |= {n for p in list(comp) for n in nb(p) if box(n) and (world.get(n) or (0, 'x', 1))[1] == 'rock'
                     and not world[n][2]}
            F.card_mass.append(sorted(comp)); F.sea_rock -= comp; F.rock_bank -= comp; continue
        if max(water) - base > LEVEL: continue      # (a mass in a wall between two seas far apart - Route 125's east
                                                    #  side, 0 and 96 - keeps its heights: raised it left gaps)
        dist, q = {}, deque()
        for p in comp:
            if any(n not in comp for n in nb(p)): dist[p] = 0; q.append(p)
        while q:                          # (8-neighbour distance: terraces with square corners; 4-neighbour steps
            p = q.popleft()               #  left a row of dark notches along every diagonal terrace edge)
            for n in [(p[0] + dx, p[1] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dz]:
                if n in comp and n not in dist: dist[n] = dist[p] + 1; q.append(n)
        # walkable tiles a player could step onto from outside (from a shoal or a surf dismount, through walkable tiles
        # of the mass) keep their height: only what nothing reaches is drawn raised
        door, q = set(), deque(p for p in comp if p in F.walk and any(
            n not in comp and ((world.get(n) or (0, 0, 0))[2] or (world.get(n) or (0, 0))[1] in WATER) for n in nb(p)))
        while q:
            p = q.popleft()
            if p in door: continue
            door.add(p); q.extend(n for n in nb(p) if n in comp and n in F.walk and n not in door)
        if door: continue           # (a top a surfer can land on stays where it is: raised round it, it was a pit)
        for p in comp:
            d, was = dist.get(p, 0), F.y(*p)
            if d: F.h[p] = max(was, base + LEVEL * min(1 + (d - 1) // 3, TERRACES))
            if F.y(*p) != was: F.coll_h[p] = was        # (drawing only: the collision keeps its height)
        for p in comp:
            if not F.h.get(p): F.h.pop(p, None)

# Raised corners Sapphire draws with a cliff but no elevation (its tiles are trees, elevation 0, so the solver leaves
# them at the ground's height): map -> boxes (x0, z0, x1, z1) of tiles that rise a level, drawing only (F.coll_h).
# Dewford's corner across the channel from the dock: trees on a sand top behind a brown cliff (x 13, rows 6-7) in
# Sapphire, a grove at the town's height with a grass rim before (overworld_polish 2026-10-08).
RAISED = {'DewfordTown': [(14, 0, 19, 5), (17, 6, 19, 6)]}
SANDY_TOPS = set(RAISED)

def raise_corners(F, world, maps, repo, mtile):
    """RAISED: the boxes' unwalkable non-face tiles rise LEVEL (drawn only); the face tiles round them are rock (rock
    lip gake1_0, face gake01a, rocky ground at their foot and a rocky waterline: F.rock_bank)."""
    for name, boxes in RAISED.items():
        mp = maps.get(name)
        if mp is None: continue
        top = set()
        for x0, z0, x1, z1 in boxes:
            for z in range(z0, z1 + 1):
                for x in range(x0, x1 + 1):
                    k = (mp['ox'] + x, mp['oz'] + z)
                    if k in world and k not in F.walk and world[k][1] not in FACE: top.add(k)
        for k in top:
            was = F.y(*k); F.h[k] = was + LEVEL; F.coll_h[k] = was; F.rock.add(k)
        for k in {(x + dx, z + dz) for x, z in top for dx in (-1, 0, 1) for dz in (-1, 0, 1)}:
            if (world.get(k) or (0, 0))[1] in FACE: F.rock.add(k); F.mat[k] = 'gake_michi'; F.rock_bank.add(k)

def lower_rocks(F, world, maps, nb):
    """Sea rocks stood at the level of the water on one side of them; where a line of them parts two water levels
    (Route 104's rocks between the open sea and the channel along its beach) half the line stood high, the step's rock
    face fell into the low half's tiles and cut Black 2's rock cards (terrain/ground.py rock_card), and a 2x2 card over
    both halves was torn in two by world.py's per-tile lift. Now every group of touching sea rocks is drawn at the
    lowest level of the water round it and holds no face (F.noface): the step is the rock skirt on its edges towards the
    higher water, behind the cards. Also the small sea rock masses drawn as one card (F.card_mass) and a deck's
    unwalkable end tiles (drawn as the deck). Drawing only (F.coll_h keeps the collision)."""
    rock = {k for k, e in world.items() if e[1] == 'rock' and not e[2]}
    def drawn_at(k, y):
        if F.y(*k) == y: return
        F.coll_h.setdefault(k, F.y(*k)); F.h[k] = y
        if not y: del F.h[k]
    sea = F.sea_rock | F.card_tiles()
    # (only rocks standing in the sea: a rock touching land or a cliff - Route 125's rocky arc round Shoal Cave, rocks
    # on a ridge - keeps its height: lowered it left holes in the ridge; a jetty beside one is no land: Mr. Briney's
    # rocks under his jetty's west end)
    afloat = lambda k: all(n not in world or n in rock or n in sea or world[n][1] in WATER | SHALLOWS | {'bridge'}
                           for n in nb(k))
    for comp in _components(rock, nb):
        out = [n for p in comp for n in nb(p) if n not in rock and n in world]
        lows = [F.y(*n) for n in out if world[n][1] in WATER]
        if not lows or max(lows + [F.y(*k) for k in comp]) - min(lows) > LEVEL: continue   # (one level at most: Route
        for k in comp:                                                                     #  125's 96-unit sea wall)
            if afloat(k): drawn_at(k, min(lows)); F.noface.add(k)
    for comp in F.card_mass:              # (small sea rock masses: water under the card, at the lowest level round them)
        lows = [F.y(*n) for p in comp for n in nb(p) if n not in comp and (world.get(n) or (0, 0))[1] in WATER]
        for k in comp:
            if lows: drawn_at(k, min(lows))
            F.noface.add(k)
    # a deck's unwalkable end tiles (Mr. Briney's jetty's west end, x 11) stood at the ground's height under the deck's
    # level, holding a rock face: drawn as the deck they belong to (the highest deck tile beside them)
    for k, e in world.items():
        if e[2] or e[1] != 'bridge': continue
        hs = [F.y(*n) for n in nb(k) if n in F.decks]
        if hs and max(hs) > F.y(*k):
            drawn_at(k, max(hs)); F.noface.add(k); F.decks.add(k)

def _emerald():
    v = sys.modules.get('version')
    return bool(v is not None and getattr(v, 'EMERALD', False))
# (emerald_polish_outdoor 2026-10-12) Emerald's maps whose glitches steps 9a' / 9c'' / 10 fix: the rules are general, but
# they are applied only where each change was checked (camera renders, outdoor_check, walk_diff); elsewhere they would
# also move other maps' rocks (Routes 111/114-116/120, Lilycove, Ever Grande: 43 tiles in Emerald's world), unchecked
# (9d's row behind a mouth applies to every version and map since v16.7)
POLISH_MAPS = {'Route103', 'JaggedPass'}

def _sandy(repo, ts, m):
    """True when Sapphire's metatile shows >= 12 pixels of beach sand (Dewford's (222, 205, 131))."""
    if ('s', ts, m) not in _colour:
        from gba import MetatileRenderer
        r = _colour.setdefault(('r',) + ts, None) or MetatileRenderer(repo, *ts)
        _colour[('r',) + ts] = r
        px = r.render(m)[..., :3].reshape(-1, 3).astype(int)
        _colour[('s', ts, m)] = int(((px[:, 0] > 190) & (px[:, 1] > 160) & (px[:, 2] < 190) & (px[:, 0] >= px[:, 1]) &
                                     (px[:, 1] - px[:, 2] > 50)).sum()) >= 12
    return _colour[('s', ts, m)]

# ---- the height field --------------------------------------------------------------------------------------------
class Field:
    """Heights of every world tile (units), slopes of stairs, surfaces of cliff tops. Tiles outside maps are 0."""
    def __init__(self):
        self.h, self.slope, self.rock, self.walk, self.kind, self.floor = {}, {}, set(), set(), {}, {}
        self.rocktop, self.mat, self.walls = set(), {}, {}
        self.style = {}                  # tile -> rock style name (STYLES)
        self.sea_rock = set()            # tiles of the rock masses standing in the sea (sea_rock_masses)
        self.coll_h = {}                 # tile -> collision height where the drawn height differs (raise_sea_rock)
        self.rock_bank = set()           # land tiles whose water banks are Black 2's rocky waterline (water.py)
        self.noface = set()              # tiles that never hold a cliff profile (lower_rocks: skirts instead)
        self.card_mass = []              # small sea rock masses drawn as one Black 2 rock card (tile lists)
        self.decks, self.wet = set(), set()   # walkable deck tiles; unwalkable water tiles (4b)
        self.deck_water = {}             # deck tile -> stands over water (ground.water_under), memo for _Lattice
        self.noland = set()              # walkable tiles a surfer may not land on (step 12; collision flag NOLAND)
        self.stilt_decks = set()         # walkways on posts over the forest floor (STILTS: Fortree), step 7
        self.stilt_ground = set()        # the floor tiles round them: no face, no skirt up to the deck (open_under)
        self.notes = []

    def y(self, wx, wz):
        return self.h.get((wx, wz), 0)

    def card_tiles(self):
        if getattr(self, '_ct', (None,))[0] is not self.card_mass:
            self._ct = (self.card_mass, {k for comp in self.card_mass for k in comp})
        return self._ct[1]

    def record(self, rec, wx, wz):
        """A collision record moved to this tile's height (and slope); records already set by heights stay."""
        a, b, cls, flags = rec
        if (wx, wz) in self.slope and not flags & 1:
            side, y0, rise = self.slope[(wx, wz)]
            if rise:
                lx, lz = (wx % 32) * 16 - 256 + 8, (wz % 32) * 16 - 256 + 8
                a, b = plane_record(SLOPES[(side, abs(rise))], lx, self.y(wx, wz), lz)
                return (a, b, cls, flags)
        if (wx, wz) in self.walls and cls in (0x00, 0x1F, 0x03) and not flags & 1:
            cls = WALL_CLASS.get(frozenset(self.walls[(wx, wz)]), cls)
        if (wx, wz) in self.noland and not flags & 1:
            flags |= NOLAND
        # (sweep_outdoor 2026-10-11: surf water, ponds, falls, shoals and currents are the water module's records at the
        # water's own height; one at exactly y 0 - water leveled 8 over its lower shore, 4b - is not a ground record)
        if a == 0 and b == flat_index(0) and cls not in (0x3F, 0x3D, 0x40, 0x17, 0x94, 0x95, 0x96, 0x97):
            return (0, flat_index(self.coll_h.get((wx, wz), self.y(wx, wz))), cls, flags)
        return (a, b, cls, flags)

    def material(self, cx, cz):
        """Ground texture of a cell's tiles for build_chunk.ground_heights (step 10 of height_field): rocky ground or
        grass; None under stairs (the steps are the surface there)."""
        X, Z = cx * 32, cz * 32
        return lambda tx, tz: None if (X + tx, Z + tz) in self.slope else self.mat.get((X + tx, Z + tz), 'grass01ax')

    def lift(self, model, cx, cz):
        """Raise geometry another module drew at ground level: every triangle by the height of the tile under its
        centre (water, sand and props on raised ground follow the land). A triangle over tiles of different heights
        is cut at the tile edges and each piece raised by its own tile (a whole run of sand, deck, wall or hedge
        raised by one tile's height tore diagonally across a height step; exterior sweep 2026-10-06)."""
        X, Z = cx * 32, cz * 32
        for mat, tris in model.tris.items():
            out = []
            for t in tris:
                for h, piece in self.pieces(t, X, Z):
                    out.append([(x, y + h, z, u, v, c) for x, y, z, u, v, c in piece] if h else piece)
            model.tris[mat] = out
        return model

    def pieces(self, t, X, Z):
        """[(height, triangle)] for triangle t (model units of the cell at world tile X, Z): t itself with the height
        of the tile under its centre when the tiles it covers stand level, else its parts per tile."""
        mx = sum(v[0] for v in t) / 3; mz = sum(v[2] for v in t) / 3
        hc = self.y(X + int((mx + 256) // 16), Z + int((mz + 256) // 16))
        xs = [v[0] for v in t]; zs = [v[2] for v in t]
        tx0, tx1 = int((min(xs) + 256) // 16), int((max(xs) + 256 - 1e-6) // 16)
        tz0, tz1 = int((min(zs) + 256) // 16), int((max(zs) + 256 - 1e-6) // 16)
        tx1, tz1 = max(tx0, tx1), max(tz0, tz1)
        if tx0 == tx1 and tz0 == tz1: return [(hc, t)]
        hs = {(a, b): self.y(X + a, Z + b) for a in range(tx0, tx1 + 1) for b in range(tz0, tz1 + 1)}
        if len(set(hs.values())) == 1: return [(hc, t)]
        out = []
        for (a, b), h in hs.items():
            poly = [tuple(v[:5]) + tuple(v[5]) for v in t]
            for axis, value, keep in ((0, a * 16 - 256, True), (0, a * 16 - 240, False),
                                      (2, b * 16 - 256, True), (2, b * 16 - 240, False)):
                if min(p[axis] for p in poly) >= value - 1e-6 if keep else max(p[axis] for p in poly) <= value + 1e-6:
                    continue
                poly = _clip_axis(poly, axis, value, keep)
                if len(poly) < 3: break
            if len(poly) < 3: continue
            for i in range(1, len(poly) - 1):
                tri = [poly[0], poly[i], poly[i + 1]]
                (ax, ay, az), (bx, by, bz), (qx, qy, qz) = [p[:3] for p in tri]
                n = ((by - ay) * (qz - az) - (bz - az) * (qy - ay), (bz - az) * (qx - ax) - (bx - ax) * (qz - az),
                     (bx - ax) * (qy - ay) - (by - ay) * (qx - ax))
                if n[0] ** 2 + n[1] ** 2 + n[2] ** 2 < 1e-6: continue
                out.append((h, [(p[0], p[1], p[2], p[3], p[4], tuple(p[5:])) for p in tri]))
        return out

def _clip_axis(poly, axis, value, keep_greater):
    """Sutherland-Hodgman clip of a polygon of flat vertex tuples (x, y, z, u, v, colour...) at x or z = value."""
    out = []
    inside = (lambda p: p[axis] >= value - 1e-9) if keep_greater else (lambda p: p[axis] <= value + 1e-9)
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        if inside(p): out.append(p)
        if inside(p) != inside(q):
            f = (value - p[axis]) / (q[axis] - p[axis])
            out.append(tuple(a + f * (b - a) for a, b in zip(p, q)))
    return out

FIELD = None

def _components(tiles, nb):
    seen, out = set(), []
    for k in sorted(tiles):
        if k in seen: continue
        comp, q = [], deque([k]); seen.add(k)
        while q:
            p = q.popleft(); comp.append(p)
            for n in nb(p):
                if n in tiles and n not in seen: seen.add(n); q.append(n)
        out.append(comp)
    return out

def height_field(world, maps, cfg, trees=()):
    """Compute every tile's height from Sapphire's elevation and structure (see the module doc)."""
    global FIELD
    F = Field(); FIELD = F
    elev, mtile, repo = _sapphire_grids(maps, cfg)
    F.elev = elev                # (Sapphire's elevation per world tile: world.py bridge_layers, surf_under 2026-10-17)
    for name, mp in maps.items(): F.floor[name] = mp['cfg'].get('floor', 'route')
    cls = lambda k: world[k][1] if k in world else None
    # (Sapphire marks 41 scattered tiles of Route 126's crater wall passable; they are unreachable rock: solid here)
    # (jump ledges count as walkable: Sapphire's side ledges carry the collision bit but are jumped over)
    walk = {k for k, e in world.items() if (e[2] or e[1] in LEDGES) and e[1] not in BLOCK
            and e[1] not in ('cave_entrance', 'ledge_cap', 'mountain')}
    F.walk = walk
    for k, e in world.items():
        if e[1] in HIGHLAND | FACE and _rocky(repo, *mtile[k]):
            F.rock.add(k)
            if e[1] in HIGHLAND: F.rocktop.add(k)
    # Rocks in the sea (overworld_polish 2026-10-08): a mass of cliff / cliff-top tiles standing in the water, reached
    # from no land (Sapphire's pink rock piles and reefs on the sea routes, round Pacifidlog, Mossdeep, Lilycove) was
    # drawn as a grass plateau when its metatiles came out greenish: it is brown rock in Sapphire. Drawn as Black 2's
    # rock (the 'mountain' style the big sea rocks and Route 131's islet already use: rock top gake_michi, rock lip
    # gake1_0, face yamagake01). Drawing only: the tiles keep their class, walkability and heights.
    F.sea_rock = sea_rock_masses(world)
    F.rock_bank = set(F.sea_rock)
    for k in F.sea_rock:
        F.rock.add(k)
        if world[k][1] in HIGHLAND: F.rocktop.add(k)
    N4 = ((0, -1), (1, 0), (0, 1), (-1, 0))
    nb = lambda k: [(k[0] + dx, k[1] + dz) for dx, dz in N4]
    lvl = lambda e: max(e - 3, 0) if 1 <= e <= 14 else None

    # 1. regions: walkable tiles joined across equal Sapphire levels. Tiles at elevation 0/15 (Sapphire's "any level")
    #    that touch regions of one level join them; where they touch several levels they are a junction: Sapphire
    #    walks straight across, so those regions must stand at one height (Route 120's path, Lilycove's lawn: two
    #    elevations, no cliff between them - the elevation only orders sprites there)
    core = {k for k in walk if cls(k) not in CONNECT | LEDGES and lvl(elev[k]) is not None}
    region, rlvl = {}, []
    for k in sorted(core):
        if k in region: continue
        r = len(rlvl); rlvl.append(lvl(elev[k])); region[k] = r; q = deque([k])
        while q:
            p = q.popleft()
            for n in nb(p):
                if n in core and n not in region and lvl(elev[n]) == rlvl[r]: region[n] = r; q.append(n)
    wildset = {k for k in walk if cls(k) not in CONNECT | LEDGES and k not in core}
    junctions = []
    warp_at = {(mp['ox'] + w['x'] + dx, mp['oz'] + w['y'] + dz) for mp in maps.values() for w in mp['plan']['warps']
               for dx, dz in ((0, 0),) + N4}         # (warp tiles and their approaches: reached by a warp, see 2.)
    for comp in _components(wildset, nb):
        touch = Counter(region[n] for p in comp for n in nb(p) if n in region)
        if not touch:
            r = len(rlvl); rlvl.append(0)
        else:
            r = touch.most_common(1)[0][0]
            if len({rlvl[t] for t in touch}) > 1: junctions.append(sorted(touch))
        for p in comp: region[p] = r

    # 2. stairs / muddy slopes: which regions they join. Heights per region come from constraints, strongest first:
    #    stairs between two Sapphire levels keep that difference; stairs inside one level climb one level a row to
    #    the north (Gen 3 draws them in a cliff band; its elevation only matters where levels overlap); junctions
    #    keep their regions level. A constraint that contradicts earlier ones is dropped (listed in F.notes).
    conn = {k for k in walk if cls(k) in CONNECT}
    stair_info = []
    fixed, structural = [], []
    for comp in _components(conn, nb):
        cs = set(comp)
        side = {s: Counter(region[(p[0] + dx, p[1] + dz)] for p in comp if (p[0] + dx, p[1] + dz) not in cs
                           and (p[0] + dx, p[1] + dz) in region) for s, (dx, dz) in zip('nesw', N4)}
        top = lambda s: side[s].most_common(1)[0][0] if side[s] else None
        if top('n') is not None and top('s') is not None: axis, lo, hi = 'z', top('s'), top('n')
        elif top('w') is not None and top('e') is not None: axis, lo, hi = 'x', top('w'), top('e')
        else: axis, lo, hi = 'z', None, None
        steps = len({p[1] for p in comp}) if axis == 'z' else len({p[0] for p in comp})
        mud = cls(comp[0]) == 'mud'
        stair_info.append((comp, axis, lo, hi, steps, mud))
        if lo is None or lo == hi: continue
        if rlvl[lo] != rlvl[hi]: fixed.append((hi, lo, LEVEL * (rlvl[hi] - rlvl[lo]), comp[0]))
        elif axis == 'z': structural.append((hi, lo, LEVEL * (1 if mud else steps), comp[0]))
    parent, off = list(range(len(rlvl))), [0] * len(rlvl)       # weighted union-find: off = height - parent's
    def find(r):
        path = []
        while parent[r] != r: path.append(r); r = parent[r]
        for p in reversed(path):                                 # compress: offsets straight to the root
            if parent[p] != r: off[p] += off[parent[p]]; parent[p] = r
        return r, (off[path[0]] if path else 0)
    def union(a, b, d, why):                                     # height(a) - height(b) = d
        (ra, oa), (rb, ob) = find(a), find(b)
        if ra == rb:
            if oa - ob != d: F.notes.append(f'{why}: wants {d}, regions already {oa - ob} apart (kept)')
            return
        parent[rb], off[rb] = ra, oa - d - ob
    # Regions on the sea (water bodies over 400 tiles; rivers above a waterfall are separate bodies) stay at
    # Sapphire's level, so the sea stays level; stairs move the land they lead to. Ledges have the same height on
    # both sides (Black 2's own).
    G = len(rlvl); parent.append(G); off.append(0)               # G: the ground; height(G) = 0
    wetmaps = {}
    for comp in _components({k for k, e in world.items() if e[1] in WATER and e[1] != 'waterfall'}, nb):
        if len(comp) >= 400:
            for p in comp:
                for n in nb(p):
                    if n in region: wetmaps[region[n]] = True
    for r in range(G):
        if r in wetmaps: union(r, G, LEVEL * rlvl[r], 'anchor')
    ledge_pairs = []
    for k in walk:
        if cls(k) in JUMP:
            dx, dz = JUMP[cls(k)]
            a, b = (k[0] - dx, k[1] - dz), (k[0] + dx, k[1] + dz)
            if a in region and b in region: ledge_pairs.append((region[a], region[b], k))
    for a, b, d, at in fixed: union(a, b, d, f'stairs at {at}')
    for touch in junctions:
        for t in touch[1:]: union(touch[0], t, 0, f'junction of regions {touch}')
    for a, b, at in ledge_pairs: union(a, b, 0, f'ledge at {at}')
    for a, b, d, at in structural: union(a, b, d, f'stairs at {at}')
    size = Counter(region.values())
    # a group still floating that shares a pond, river or lake with a placed one stands level with it (exterior
    # sweep 2026-10-06): e.g. Petalburg's grass strip south of its west pond, cut off by trees, stood at Sapphire's
    # level 0 while Petalburg stands at +16, so the pond stepped 16 units in the middle. The biggest shore region
    # goes first; groups already placed keep their heights (union only joins groups that are still separate)
    # (bridges 2026-10-18) ...and the water on both sides of a surf-under plank bridge (Sapphire's walkable
    # elevation-15 bridge tiles over surf water, Routes 119/120: a surfer passes under them, raise_bridges) is one
    # body: Route 120's south bridge parted its river, and the strip north of it (two secret-base caves) took the
    # bridge's level, 32 over the river's south bank, where Sapphire has both at elevation 3
    span = {k for k in walk if cls(k) == 'bridge' and elev.get(k) == 15 and world[k][0] not in STILTS
            and any(n in world and world[n][2] and cls(n) in ('water', 'deep_water') for n in nb(k))}
    for comp in _components({k for k, e in world.items() if e[1] in WATER and e[1] != 'waterfall'} | span, nb):
        if len(comp) >= 400: continue                            # the sea: its shores are anchored above
        shore = sorted({region[n] for p in comp for n in nb(p) if n in region and cls(n) != 'bridge'},
                       key=lambda r: -size[r])
        placed = [r for r in shore if find(r)[0] == find(G)[0]]
        if not placed:    # (else a bridge over it: Route 120's strip at the Scorched Slab, across its pond from the
            # bridge, floated at Sapphire's level 0, 32 under the bridge: the pond stepped 32 and the cave could not be
            # reached; outdoor sweep 2026-10-07)
            decks = sorted({region[n] for p in comp for n in nb(p) if n in region and cls(n) == 'bridge'}, key=lambda r: -size[r])
            placed = [r for r in decks if find(r)[0] == find(G)[0]]
        for r in shore:
            if placed and find(r)[0] != find(G)[0]: union(placed[0], r, 0, f'shore of the water at {comp[0]}')
    # any group still floating stands where its biggest region's Sapphire level puts it - unless it is walled in
    # (map_glitch_fix 2026-10-09: no water beside it, no warp on it, no stairs, ledge or junction to other ground: nobody
    # reaches it) and that level is two or more levels off the land round it: then it keeps Sapphire's level difference
    # to the nearest placed region instead. Such patches (walk-behind tiles among trees, the trunk tile under Fortree's
    # big trees, the grass behind Fortree's Gym) stood at their absolute level inside towns and routes the stairs lift
    # to 32-96, and step 7 sank the trees and rock round them too: pits with cliff faces, Fortree's 96 deep under its
    # tree houses, Route 113's under the ash grass, Route 112's round the cable car. (One level off they stay: there the
    # absolute level is the land's own, Mossdeep's forest)
    rid = {}
    for k, r in region.items(): rid.setdefault(r, []).append(k)
    def nearest_placed(rs, limit=4):
        tiles_ = [k for r_ in rs for k in rid.get(r_, ())]
        seen_, q = set(tiles_), deque((k, 0) for k in tiles_)
        while q:
            p, d = q.popleft()
            for n in nb(p):
                if n in seen_ or n not in world or cls(n) in WATER: continue
                seen_.add(n)
                if n in region and find(region[n])[0] == find(G)[0]: return region[n]
                if n not in region and d + 1 < limit: q.append((n, d + 1))
        return None
    for r in sorted(range(G), key=lambda r: -size[r]):
        if find(r)[0] == find(G)[0]: continue
        root = find(r)[0]
        group = [r_ for r_ in range(G) if find(r_)[0] == root]
        ts = [k for r_ in group for k in rid.get(r_, ())]
        near = None
        if not any(cls(n) in WATER for t in ts for n in nb(t) + [t]) and not any(t in warp_at for t in ts):
            near = nearest_placed(group)
        if near is not None:
            # (a patch of Sapphire "any level" tiles only (elevation 0/15) takes its neighbour's level)
            d = 0 if all(elev.get(t) in (0, 15) for t in ts) else LEVEL * (rlvl[near] - rlvl[r])
            want = find(near)[1] - find(G)[1] - d                      # (union: height(near) - height(r) = d)
            if abs(want - LEVEL * rlvl[r]) >= 2 * LEVEL:
                union(near, r, d, f'walled-in region at {rid[r][0]}'); continue
        union(r, G, LEVEL * rlvl[r], 'anchor')
    rh = [find(r)[1] - find(G)[1] for r in range(G)]
    # (walkability 2026-10-11, door_fix's finding) a building stands level (step 8: at its door's front tile), so two
    # doors in one wall into one room need their front tiles at one height. Route 110's south Cycling Road gate: the
    # east door's ground (cut off by the fence) is tied only by the stairs up to the Cycling Road, whose deck a junction
    # keeps level with the west door's ground, so it stood 16 lower and the door half under the gate's base. The
    # smaller region takes the other's height when only stairs tie it (no junction or ledge): those stairs go flat
    fronts, tied = {}, {r for t in junctions for r in t} | {r for a, b, _ in ledge_pairs for r in (a, b)}
    for mp in maps.values():
        for w in mp['plan']['warps']:
            k = (mp['ox'] + w['x'], mp['oz'] + w['y'] + 1)
            if k in region: fronts.setdefault((w['dest'], k[1]), []).append(k)
    for _, ks in sorted(fronts.items()):
        ks.sort()
        for a, b in zip(ks, ks[1:]):
            ra, rb = region[a], region[b]
            if b[0] - a[0] > 6 or rh[ra] == rh[rb]: continue
            small, big = sorted((ra, rb), key=lambda r: size[r])
            if small in tied or size[small] > 200:
                F.notes.append(f'doors of one building at {a}, {b}: {rh[ra]} and {rh[rb]} (kept)'); continue
            F.notes.append(f'doors of one building at {a}, {b}: region at {rid[small][0]} {rh[small]} -> {rh[big]}')
            rh[small] = rh[big]
    for k, r in region.items(): F.h[k] = rh[r]
    F.regions = (region, rlvl, rh)                               # (for checks)

    # 3. slope tiles: from the low region's height to the high one's, evenly per row (8/16/32 a row)
    for comp, axis, lo, hi, steps, mud in stair_info:
        if lo is None:
            r = next((region[n] for p in comp for n in nb(p) if n in region), None)
            for p in comp: F.h[p] = rh[r] if r is not None else 0
            continue
        y0, y1 = rh[lo], rh[hi]
        # a slope too short for its climb (more than 16 a row) is one Black 2 cannot walk: an actor steps only 19 units
        # (ov012 field_actor_tool.c:490-525), and 32 a row stopped the climb halfway - the Safari Zone's mud slope into
        # its northwest, 64 units over 2 rows (outdoor sweep 2026-10-07). It takes in the walkable rows beyond its ends
        # (in its own columns), one at a time at either end, until 16 a row is enough
        blocked = lambda steps: abs(y1 - y0) / (2 if steps == 1 else steps) >= 20     # (centre to centre, ends: half)
        if axis == 'z' and blocked(steps):
            cs, cols = set(comp), sorted({p[0] for p in comp})
            end = {'s': max(p[1] for p in comp), 'n': min(p[1] for p in comp)}
            for side in 'sn' * 4:
                if not blocked(steps) and abs(y1 - y0) <= 16 * steps: break
                z = end[side] + (1 if side == 's' else -1)
                row = [(x, z) for x in cols]
                if all(p in walk and p not in F.slope and p not in cs and cls(p) not in LEDGES | CONNECT for p in row):
                    comp = comp + row; cs.update(row); end[side] = z; steps += 1
                    F.notes.append(f'stairs at {comp[0]}: row {z} joins the slope ({abs(y1 - y0)} over {steps} rows)')
        rise = (y1 - y0) / steps
        ok = min((0, 8, 16, 32), key=lambda v: abs(abs(rise) - v))
        if ok != abs(rise): F.notes.append(f'stairs at {comp[0]}: {y1 - y0} over {steps} rows, using {ok} a row')
        rise = ok if rise >= 0 else -ok
        if axis == 'z':
            south = max(p[1] for p in comp)
            for p in comp:
                i = south - p[1]
                F.slope[p] = ('n', y0 + rise * i, rise) if rise >= 0 else ('s', y0 + rise * (i + 1), -rise)
                F.h[p] = round(y0 + rise * (i + 0.5))
        else:
            west = min(p[0] for p in comp)
            for p in comp:
                i = p[0] - west
                F.slope[p] = ('e', y0 + rise * i, rise) if rise >= 0 else ('w', y0 + rise * (i + 1), -rise)
                F.h[p] = round(y0 + rise * (i + 0.5))
        for p in comp: F.kind[p] = 'mud' if mud else 'stairs'

    # 3b. a bridge whose two banks the constraints left more than 16 apart (Route 120's bridge east of Fortree: banks
    #     64 apart, a 64-unit wall in the deck; Route 119's by the Weather Institute: 32) steps from one bank's height to
    #     the other's in steps of 16 spread along it, so it can be crossed (an actor steps at most 19 units, ov012
    #     field_actor_tool.c:490-525); Sapphire's bridges join their banks (outdoor sweep 2026-10-07)
    for comp in _components({k for k in walk if cls(k) == 'bridge'}, nb):
        xs, zs = [p[0] for p in comp], [p[1] for p in comp]
        ew = max(xs) - min(xs) >= max(zs) - min(zs)
        axis, lo_, hi_ = (0, min(xs), max(xs)) if ew else (1, min(zs), max(zs))
        def bank(end, d):
            hs = [F.h[n] for p in comp if p[axis] == end for n in [((p[0] + d, p[1]) if ew else (p[0], p[1] + d))]
                  if n in walk and n in F.h and cls(n) != 'bridge' and n not in F.slope]
            return Counter(hs).most_common(1)[0][0] if hs else None
        h0, h1 = bank(lo_, -1), bank(hi_, 1)
        if h0 is None or h1 is None or abs(h1 - h0) <= 16: continue
        n = hi_ - lo_ + 1
        # the part over the water (Sapphire elevation 15) stays at one height as near the lower bank as the dry deck
        # at the ends allows (surfers land on it and surf off it: the water beside it is leveled to its shores); the
        # dry end tiles step 16 at a time to their banks. Too few dry tiles: the whole deck steps along its length
        wet_col = {i: all(elev.get(p) == 15 for p in comp if p[axis] - lo_ == i) for i in range(n)}
        dry_lo = next((i for i in range(n) if wet_col[i]), n); dry_hi = next((i for i in range(n) if wet_col[n - 1 - i]), n)
        lo_h, hi_h = sorted((h0, h1)); H = None
        for cand in range(lo_h, hi_h + 1, 16):
            if max(0, abs(cand - h0) // 16 - 1) <= dry_lo and max(0, abs(h1 - cand) // 16 - 1) <= dry_hi and \
                    dry_lo + dry_hi < n: H = cand; break
        for p in comp:
            i = p[axis] - lo_
            if H is None: F.h[p] = h0 + round((h1 - h0) * (i + 1) / (n + 1) / 16) * 16
            elif i < dry_lo: F.h[p] = h0 + max(-abs(H - h0), min(abs(H - h0), 16 * (i + 1))) * (1 if H >= h0 else -1)
            elif n - 1 - i < dry_hi: F.h[p] = h1 + max(-abs(H - h1), min(abs(H - h1), 16 * (n - i))) * (1 if H >= h1 else -1)
            else: F.h[p] = H
        F.notes.append(f'bridge at {min(comp)}: banks {h0} and {h1}, deck {"at " + str(H) if H is not None else "steps"}'
                       f' by 16 at its ends')

    # 4. ledges sit at the height of the side they are jumped from (else the landing side, else the walkable ground
    #    beside them: Route 112's ledge lines run between trees)
    todo = sorted(k for k in walk if cls(k) in JUMP and k not in F.h)
    for _ in range(4):
        left = []
        for k in todo:
            dx, dz = JUMP[cls(k)]
            src, dst = (k[0] - dx, k[1] - dz), (k[0] + dx, k[1] + dz)
            side = [F.h[n] for n in nb(k) if n in F.h and (n in region or n in F.slope or cls(n) in JUMP)]
            if src in region and src in F.h: F.h[k] = F.h[src]
            elif dst in region and dst in F.h: F.h[k] = F.h[dst]        # (not a walled-in patch's: scenery, step 2)
            elif side: F.h[k] = Counter(side).most_common(1)[0][0]
            else: left.append(k)
        todo = left
    for k in todo: F.h[k] = 0

    # 4b. water lies at the height of its nearest shore (ties: the lower): the sea at its beaches' level, ponds on
    #     plateaus up there, and a river whose banks Gen 3 drew at two levels steps between them halfway (the step
    #     gets a rock face like any other); the surface itself is the water module's, lifted to this height
    wet = {k for k, e in world.items() if e[1] in WATER and k not in walk} - set(F.h)
    # ... except a body of water whose surf shores all stand at one height (outdoor sweep 2026-10-07): it lies at that
    # height. Sapphire starts surfing only from elevation 3 (pokeruby IsPlayerFacingSurfableFishableWater wants
    # PlayerGetZCoord() == 3), so shores at other elevations (cliff-top lips, a plateau's edge) are not surf shores;
    # by nearest shore they split a lake in two at a 16-32 unit step (Route 120's lake and the Scorched Slab pond,
    # Routes 119/125/128, Mossdeep, the Safari Zone): a skirt facing away from the camera (a gap) and, at 32, a step
    # surfers cannot cross (ov012 field_actor_tool.c:490-525). Bodies whose surf shores stand at several heights keep
    # the halfway steps (one level would put some surf shore 24+ units over the water, too high to start surfing).
    # (bridge decks count as surf shores: one layer here, a surfer lands on a deck and surfs off its other side,
    # notes/TERRAIN_GROUND.md; Route 119's river north of its bridge is reached that way)
    deck = lambda n: cls(n) in ('bridge', 'bike_path') or str(cls(n)).startswith('other:acro')
    # (a pier - a deck reached from land at one end only - at Sapphire elevation 4+ is no surf shore either: on it
    # PlayerGetZCoord() is 4+. Mr. Briney's jetty on Route 104 (elevation 4) split his cove from the sea south of it at a
    # 16-unit step across the open water, a rock bank right under the jetty and his boat; overworld_polish 2026-10-08.
    # Bridges with land at both ends keep counting: Route 119's river is reached over its bridge, and its waterfall
    # needs the river's level)
    decks = {k for k in walk if deck(k)}
    pier = set()
    for comp in _components(decks, nb):
        land = {n for p in comp for n in nb(p) if n in walk and n not in decks}
        if len(_components(land, lambda p: [n for n in nb(p) if n in walk and n not in decks])) == 1: pier |= set(comp)
    F.decks, F.wet = decks, wet
    fall_row = lambda k: cls(k) == 'waterfall' and cls((k[0], k[1] + 1)) != 'waterfall'   # (water.py: the 0x40 row)
    level_water = set()                 # (one level between two shores: step 9 leaves it alone)
    for comp in _components({k for k in wet if not fall_row(k)}, nb):
        surf = {F.h[n] for p in comp for n in nb(p)
                if n in walk and n not in F.slope and n in F.h and ((deck(n) and (n not in pier or elev.get(n) in (0, 3, 15))) or elev.get(n) == 3)}
        # (bridges 2026-10-18) a surf-under span (step 2) is a shore only within one level of the water's other shores:
        # a surfer passes under it now (raise_bridges), and 2+ levels over them it split Route 120's south river at a
        # 32-unit step the surfer could not climb (Sapphire: one body of elevation 1)
        own = {F.h[n] for p in comp for n in nb(p) if n in span and n in F.h}
        rest = {F.h[n] for p in comp for n in nb(p) if n not in span and n in walk and n not in F.slope and n in F.h
                and ((deck(n) and (n not in pier or elev.get(n) in (0, 3, 15))) or elev.get(n) == 3)}
        if own and rest and max(abs(a - b) for a in own for b in rest) > LEVEL: surf = rest
        if len(surf) == 1:
            h0 = surf.pop()
            for p in comp: F.h[p] = h0
        elif surf and max(surf) - min(surf) <= LEVEL and len(comp) >= 100:
            # (sweep_outdoor 2026-10-11) surf shores at two heights one level apart: one level for the whole body, its
            # surface (h - 8) flush with the lower shore and 16 under the higher one - both under Black 2's 20-unit surf
            # start (CheckSurfHeightAllow) - not the halfway step, a sand-coloured wall across open water (Route 103's
            # east sea, split down the middle between Oldale's side at 16 and the east beach at 0). Open water only (100+
            # tiles): a pond's banks are drawn from the water's level and a 16-unit shore stood 8 over its bank (Route
            # 120's Scorched Slab pond: the background showed through, outdoor_check hole)
            h0 = min(surf) + LEVEL // 2
            for p in comp: F.h[p] = h0; level_water.add(p)
            F.notes.append(f'water at {min(comp)}: {len(comp)} tiles, shores {sorted(surf)}, one level {h0 - 8}')
    todo = wet - set(F.h)               # (waterfalls, shoreless water: the nearest height as before, lower on ties)
    dist, q = {}, deque()
    for h0, p in sorted((F.h.get(n, 0), p) for p in todo for n in nb(p) if (n in walk and n not in F.slope)
                        or (n in wet and n not in todo)):
        if p not in dist: dist[p] = 0; F.h[p] = h0; q.append(p)
    while q:
        p = q.popleft()
        for n in nb(p):
            if n in todo and n not in dist: dist[n] = dist[p] + 1; F.h[n] = F.h[p]; q.append(n)
    # water with no shore (strips behind a line of sea rocks at a map's edge, Route 115's west sea) lies at the level of
    # the nearest water past the rocks, not at 0: at 0 it stood 16 over Route 115's sea, the rocks between them
    # stepping up and down in cliff fragments (outdoor sweep 2026-10-07)
    left = todo - set(dist)
    lv = {p: F.h[p] for p in wet if p in F.h and p not in left}
    q = deque(sorted(lv, key=lambda p: (lv[p], p)))
    while q and left:
        p = q.popleft()
        for n in nb(p):
            if n in lv or not (n in wet or cls(n) == 'rock'): continue
            lv[n] = lv[p]; q.append(n)                   # (through rocks too)
            if n in left: F.h[n] = lv[n]; left.discard(n)
    for p in left: F.h[p] = 0

    # 5. highland: unwalkable cliff tops and mountains, one level above the ground around them (mountains rise in
    #    two-tile terraces); inner plateaus stack on the plateau south of their cliff band (Gen 3 faces look south)
    hl = {k for k, e in world.items() if e[1] in HIGHLAND and k not in walk}
    # (walkability 2026-10-11) Sapphire's cliff tiles that touch no walkable or other ground (only cliff / cliff-top /
    # mountain round them: the inner rows of a cliff band two or more rows deep, Ever Grande's and Route 111's mountain
    # masses) are rock above the ground too. As faces (step 6) they took the lowest height next to them and were drawn
    # as flat ground level with the path beside them, blocked: 'invisible walls' (b2tools/walk_diff.py OPEN, 1,700
    # tiles). Only the rim row next to the ground stays a face tile and holds the face up to them.
    rockish = HIGHLAND | FACE - {'cave_entrance'}
    hl |= {k for k, e in world.items() if e[1] in FACE - {'cave_entrance'} and k not in walk
           and all(cls(n) in rockish and n not in walk for n in nb(k))}
    # only what a 2x2 block of highland covers rises (an opening): single rocks, spurs and one-tile ridges stay down,
    # so the masses get calm outlines and few faces (each face costs triangles, and chunks must stay < 110,600 B)
    hl = {(x + dx, z + dz) for x, z in hl if all((x + a, z + b) in hl for a in (0, 1) for b in (0, 1))
          for dx in (0, 1) for dz in (0, 1)}
    hcomp, hid = [], {}
    for k in sorted(hl):
        if k in hid: continue
        i = len(hcomp); comp, q = [], deque([k]); hid[k] = i
        while q:
            p = q.popleft(); comp.append(p)
            for n in nb(p):
                if n in hl and n not in hid: hid[n] = i; q.append(n)
        hcomp.append(comp)
    def across(p, d, limit=3):           # first non-cliff tile from p in direction d, through at most `limit` cliffs
        x, z = p
        for _ in range(limit + 1):
            x, z = x + d[0], z + d[1]
            if cls((x, z)) not in FACE or (x, z) in walk: return (x, z)
        return None
    # per tile: the height of the nearest walkable ground at the plateau's rim (through at most 3 cliff tiles),
    # spread inwards (ties: the higher), so one big mountain mass rises a level above whatever lies at its foot
    tbase, below = {}, [set() for _ in hcomp]
    q = deque()
    for i, comp in enumerate(hcomp):
        for p in comp:
            for d in N4:
                n = across(p, d)
                if n is None or n in hl and hid[n] == i: continue
                if n in walk and n not in F.slope: tbase[p] = max(tbase.get(p, -999), F.h.get(n, 0))
                elif n in hl and d == (0, 1): below[i].add(hid[n])
    q = deque(sorted(tbase, key=lambda p: -tbase[p]))
    while q:
        p = q.popleft()
        for n in nb(p):
            if n in hid and hid[n] == hid[p] and n not in tbase: tbase[n] = tbase[p]; q.append(n)
    hh = [None] * len(hcomp)
    for _ in range(4):                    # plateaus with no ground at their rim stack on the one south of them
        for i in range(len(hcomp)):
            if any(p in tbase for p in hcomp[i][:1]): continue
            known = [hh[j] if hh[j] is not None else max(tbase.get(p, 0) for p in hcomp[j]) + LEVEL
                     for j in below[i] if hh[j] is not None or hcomp[j][0] in tbase]
            if known and hh[i] is None: hh[i] = max(known) + LEVEL
    for i, comp in enumerate(hcomp):
        tile_h = lambda p: tbase[p] + LEVEL if p in tbase else (hh[i] if hh[i] is not None else LEVEL)
        mountain = Counter(cls(p) for p in comp)['mountain'] > len(comp) // 2
        if mountain:                      # terraces: one more level three tiles in from the edge (at most two)
            dist, q = {}, deque()
            for p in comp:
                if any(n not in hid or hid[n] != i for n in nb(p)): dist[p] = 0; q.append(p)
            while q:
                p = q.popleft()
                for n in nb(p):
                    if n in hid and hid[n] == i and n not in dist: dist[n] = dist[p] + 1; q.append(n)
            for p in comp: F.h[p] = tile_h(p) + LEVEL * min(dist.get(p, 0) // 3, 2); F.kind[p] = 'mountain'
        else:
            for p in comp: F.h[p] = tile_h(p)

    for p in F.sea_rock: F.kind.setdefault(p, 'mountain')      # (the sea's rock masses: yamagake01 faces)

    # 6. cliff faces: the lowest height found next to the cliff band (within 3 tiles through it)
    for k, e in world.items():
        if e[1] in FACE and k not in walk and k not in F.h:
            best, q, seen_ = None, deque([(k, 0)]), {k}
            while q:
                p, d = q.popleft()
                for n in nb(p):
                    if n in seen_: continue
                    seen_.add(n)
                    if cls(n) in FACE and n not in walk:
                        if d < 3: q.append((n, d + 1))
                    elif n in F.h and n not in F.slope:
                        best = F.h[n] if best is None else min(best, F.h[n])
            if best is not None: F.h[k] = best

    # 7. everything else in the maps (trees, buildings, water, rocks, fences...): the nearest height, lower wins ties
    todo = {k for k in world if k not in F.h}
    stilt = lambda k: world[k][0] in STILTS and (cls(k) == 'bridge' or k in F.slope)    # (walkways on posts, ladders)
    F.stilt_decks = {k for k in walk if world[k][0] in STILTS and cls(k) == 'bridge'}
    for sources in ([k for k in F.h if not stilt(k)], list(F.h)):     # (then anything only a walkway reaches)
        q = deque(k for _, k in sorted((F.h[k], k) for k in sources))
        while q:
            p = q.popleft()
            for n in nb(p):
                if n in todo:
                    todo.discard(n); F.h[n] = F.h[p]; q.append(n)

    # 8. whole objects stand level: buildings at their door's front tile, trees at their lowest tile
    for name, mp in maps.items():
        ox, oz = mp['ox'], mp['oz']
        for b in mp['plan']['buildings']:
            x0, y0, x1, y1 = b['footprint']
            hb = F.y(ox + b['door'][0], oz + b['door'][1] + 1)
            for y in range(y0 - b.get('roof_rows', 0), y1 + 1):
                for x in range(x0, x1 + 1):
                    # (walkable tiles in the footprint's box keep their region's height: plan_map.py merged Fortree's
                    # Center with tree house 1 and the walkway in front of it, x 4-12 rows 1-6, and pulled the walkway's
                    # west end 16 down to the Center's door: a step in the walkway and house 1 below its neighbours)
                    k = (ox + x, oz + y)
                    if k in world and not (k in walk and cls(k) not in ('building_roof', 'building', 'door')): F.h[k] = hb
    def level_trees():                    # (walkable tree tops keep their ground's height)
        for ax, az in trees:
            cells_ = [(ax + dx, az + dz) for dx in (0, 1) for dz in (0, 1) if (ax + dx, az + dz) in world
                      and (ax + dx, az + dz) not in walk]
            if cells_:
                lo = min(F.y(*c) for c in cells_)
                for c in cells_: F.h[c] = lo
    level_trees()

    # 9. a face may never stand on a walkable tile: solid tiles next to lower walkable ground come down to it and
    #    hold the face themselves (Black 2's cliff tiles are the low side, e.g. Route 19 chunk 282 row 3)
    lower = {}
    for k in world:
        if k in walk or k in level_water: continue
        lows = [F.y(*n) if n not in F.slope else min(F.slope[n][1], F.slope[n][1] + F.slope[n][2]) for n in nb(k)
                if n in walk and cls(n) not in LEDGES]
        if lows and min(lows) < F.y(*k): lower[k] = min(lows)
    F.h.update(lower)
    level_trees()
    F.h = {k: v for k, v in F.h.items() if v}
    # (STILTS: the floor tiles beside a walkway on posts that stand lower than it hold no face up to it, open_under)
    F.stilt_ground = {n for k in F.stilt_decks for n in ((k[0] + dx, k[1] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1))
                      if n in world and n not in walk and cls(n) not in WATER and F.y(*n) < F.y(*k)}
    raise_sea_rock(F, world, nb)
    raise_corners(F, world, maps, repo, mtile)
    lower_rocks(F, world, maps, nb)
    if _emerald():
        # 9a'. (emerald_polish_outdoor 2026-10-12, Emerald only) a boulder tile by the water standing lower than every
        #     boulder tile beside it (one corner of a 2x2 rock against a cliff whose foot row is a level down: Emerald's
        #     Route 103 (40,6), lower_rocks keeps rocks touching a cliff at their height) was a face tile: a ring of rock
        #     lip round a flat tan square in the sea, and its rock card was drawn as four small ones. It is drawn at its
        #     boulder's height (F.coll_h keeps the collision)
        rk = {k for k, e in world.items() if e[1] == 'rock' and not e[2]}
        for k in sorted(k for k in rk if world[k][0] in POLISH_MAPS):
            rn = [n for n in nb(k) if n in rk]
            if rn and all(F.y(*n) > F.y(*k) for n in rn) and any(cls(n) in WATER for n in nb(k)):
                F.coll_h.setdefault(k, F.y(*k)); F.h[k] = min(F.y(*n) for n in rn); F.noface.add(k)
                F.notes.append(f"9a': boulder tile {k} drawn at its boulder's height {F.h[k]}")
    # 9c. berry soil is solid, but a tree stands on it (an NPC, drawn at its tile's collision height): never below its
    #     walkable neighbours, so the cliff face goes to the cliff tiles beyond it (final_check 2026-10-08: Route 119's
    #     (8-9,23) and Route 120's (9-10,92) soil had come down to the cliff below: their trees stood 16 / 32 units
    #     under the ground, Route 120's two invisible [test])
    for k in world:
        if cls(k) != 'other:berry_soil' or k in walk: continue
        ws = [n for n in nb(k) if n in walk and n not in F.slope and cls(n) not in LEDGES]
        ws = [F.y(*n) for n in ws if elev.get(n) == elev.get(k)] or [F.y(*n) for n in ws]   # (its own Sapphire level first)
        if ws and F.y(*k) < max(ws): F.h[k] = max(ws)
    # 9c'. (v166_fixes 2026-10-12) a hedge stands on the ground it grows on: a run of solid bush tiles whose walkable
    #     neighbours all stand at one height above it rises to that height, so the cliff face goes to the cliff tiles
    #     beyond it. Step 7 gave such a run the cliff foot's height when it touched the cliff band (lower wins ties):
    #     the Battle Tower island's (17-19,15)/(19-20,14) stood 32 units down inside the cliff, the hedge's top poking
    #     out of the face as a green strip (screenshots/v166); the same at Ever Grande's two runs beside the League stairs
    #     (23-24,24-25 / 28-29,24-25) and Route 119's (3-4,88). A run beside ground at two heights keeps its height
    F.bush_raised = []
    for comp in _components({k for k in world if cls(k) == 'bush' and k not in walk}, nb):
        ws = {F.y(*n) for p in comp for n in nb(p) if n in walk and n not in F.slope and cls(n) not in LEDGES}
        if len(ws) != 1: continue
        h = min(ws)
        if all(F.y(*p) <= h for p in comp) and any(F.y(*p) < h for p in comp):
            F.bush_raised += [(p, F.y(*p), h) for p in sorted(comp) if F.y(*p) < h]
            for p in comp: F.h[p] = h
    if F.bush_raised: F.notes.append(f"9c': bush tiles raised to their ground: {[(p, a, b) for p, a, b in F.bush_raised]}")
    if _emerald():
        # 9c''. (emerald_polish_outdoor 2026-10-12, Emerald only) a boulder stands on the ground it lies on, as the hedges
        #     of 9c': a run of solid rock tiles whose walkable neighbours (not ledges) all stand at one height above it is
        #     drawn at that height. Step 7 gave Emerald's Jagged Pass boulder at (18,15), at the corner of the upper path
        #     where ledges go down east and south, the lower ground's height: it stood in a pit 16 deep beside the Magma
        #     Hideout's mouth, ringed by rock faces (the odd rock piece by the mouth). Drawing only (F.coll_h)
        up = []
        for comp in _components({k for k in world if cls(k) == 'rock' and k not in walk and k not in F.noface
                                 and world[k][0] in POLISH_MAPS}, nb):
            ws = {F.y(*n) for p in comp for n in nb(p) if n in walk and n not in F.slope and cls(n) not in LEDGES}
            if len(ws) != 1: continue
            h = min(ws)
            if all(F.y(*p) <= h for p in comp) and any(F.y(*p) < h for p in comp):
                for p in comp:
                    if F.y(*p) < h: up.append((p, F.y(*p), h)); F.coll_h.setdefault(p, F.y(*p)); F.h[p] = h
        if up: F.notes.append(f"9c'': boulder tiles raised to their ground: {up}")

    # 9d. exposed rock (walkability 2026-10-11): an unwalkable cliff / cliff-top / mountain tile level with a walkable
    #     tile beside it that holds no face (nothing higher round it: the outer column of a narrow cliff band, a one-tile
    #     spur, a ridge between two paths at one level) was drawn as flat ground there, blocked: an invisible wall
    #     (b2tools/walk_diff.py OPEN). It rises a level (drawing only, F.coll_h keeps the collision), so it stands up as
    #     rock with the skirt (gake01a / yamagake01) towards the path, as Black 2's rock ridges (Route 23 chunk 309)
    ROCKY_CLS = {'cliff', 'cliff_top', 'mountain'}
    N8 = [(dx, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dz]
    flat_walk = lambda n: n in walk and n not in F.slope and cls(n) not in LEDGES
    # (dewford_fix 2026-10-12) ...except the rock beside a cave mouth's door on the door row: terrain/cave_mouth.py
    # stands the mouth's frame there, on the ground, and raises the rock behind it itself (Black 2's 2-tier mouth). Raised
    # here it stood in front of the frame as a flat-topped block a level high (Granite Cave's mouth on Route 106)
    from . import cave_mouth as _cm
    mouth_row = {(x + dx, y) for x, y in _cm.find(world) for dx in range(-_cm.SPAN, _cm.SPAN + 1)}
    # (emerald_polish_outdoor 2026-10-12; every version since v16.7) ...and the row behind the door over the opening's
    # width: the mouth raises it itself (tier 1) and cuts the south half of its faces for the opening; raised here,
    # world.py's ground of those tiles came up to tier 1 under the cut and showed as two flat light squares in the
    # opening's top corners (Route 111's Desert Ruins, Route 120, Lilycove's cove)
    mouth_row |= {(x + dx, y - 1) for x, y in _cm.find(world)
                  for dx in range(-_cm.span(world, (x, y)), _cm.span(world, (x, y)) + 1) if dx}
    exposed = [k for k, e in world.items() if e[1] in ROCKY_CLS and k not in walk and k not in F.noface and k not in F.slope
               and k not in mouth_row
               and any(flat_walk(n) and abs(F.y(*n) - F.y(*k)) < 1 for n in nb(k))
               and not any((k[0] + dx, k[1] + dz) in world and (k[0] + dx, k[1] + dz) not in F.slope
                           and F.y(k[0] + dx, k[1] + dz) > F.y(*k) + 0.5 for dx, dz in N8)]   # (draw: no face up to a slope)
    # (each exposed tile with the flat rock behind it at its height: the whole flat mass rises, so only its outline
    # gets faces - raising the rim alone ringed every mass with skirts on both sides, +47,000 triangles)
    flat_rock = lambda k: (k in world and world[k][1] in ROCKY_CLS and k not in walk and k not in F.noface and k not in F.slope
                           and k not in mouth_row and not any((k[0] + dx, k[1] + dz) in world and (k[0] + dx, k[1] + dz) not in F.slope
                                       and F.y(k[0] + dx, k[1] + dz) > F.y(*k) + 0.5 for dx, dz in N8))
    raise_, q = set(exposed), deque(exposed)
    while q:
        p = q.popleft()
        for n in nb(p):
            if n not in raise_ and flat_rock(n) and abs(F.y(*n) - F.y(*p)) < 1: raise_.add(n); q.append(n)
    # (sweep_outdoor 2026-10-11) trees, boulders and bushes embedded in the raised mass (no walkable tile beside them, at
    # the mass's height) rise with it: they stood in pits one level deep, the tree or rock inside (Mt. Chimney's and Jagged
    # Pass's ash trees, Mt. Pyre's boulders). Next to a path they stay at the path's height (and keep their face)
    MASS_CLS = {'tree_bot', 'tree_top_l', 'tree_top_r', 'tree_tip', 'other:tree_top_1wide', 'rock', 'bush'}
    inner = lambda n: (n in world and n not in raise_ and n not in walk and n not in F.slope and n not in F.noface
                       and n not in F.wet and n not in F.decks and cls(n) in MASS_CLS
                       and not any(m in walk for m in nb(n)))
    grow, emb = True, Counter()
    while grow:
        grow = False
        for n in {m for k in raise_ for m in nb(k)}:
            up = [m for m in nb(n) if m in raise_ and abs(F.y(*m) - F.y(*n)) < 1]
            # (embedded in the mass: rock of it on two sides, or raised on all four - a forest's edge along a mass, rock
            # on one side, stays down)
            if inner(n) and (sum(cls(m) in ROCKY_CLS for m in up) >= 2 or len(up) == 4) \
                    and not any((n[0] + dx, n[1] + dz) in world and (n[0] + dx, n[1] + dz) not in F.slope
                                and (n[0] + dx, n[1] + dz) not in raise_
                                and F.y(n[0] + dx, n[1] + dz) > F.y(*n) + 0.5 for dx, dz in N8):
                raise_.add(n); grow = True; emb[cls(n)] += 1
    if emb: F.notes.append(f'9d: raised with their rock mass: {dict(emb)}')
    pre = {k: F.y(*k) for k in raise_}
    for k in raise_:
        was = F.y(*k); F.coll_h.setdefault(k, was); F.h[k] = was + LEVEL
    F.exposed_rock = raise_
    # (sweep_outdoor 2026-10-11) an unwalkable tile that is not rock (a grave, a building's footprint, a sign, a boulder)
    # and had nothing higher round it became a face tile next to the raised rock: its surface rose to the rock's top
    # over the tile and buried what stands on it (Mt. Pyre's graves 12 units deep, Sootopolis's carved houses, the
    # rock face through their walls: outdoor_check layer). It stays flat at its height (noface): the skirt up to the
    # rock stands at its edge, as beside a path. Trees keep the face (a skirt at the tile edge lay in the plane of the
    # tree's crossed images: outdoor_check layer gake01a / ki03ax, gap 0)
    TREE_CLS = {'tree_bot', 'tree_top_l', 'tree_top_r', 'tree_tip', 'other:big_tree', 'other:tree_top_1wide'}
    nf = Counter()
    for k in raise_:
        for dx, dz in N8:
            n = (k[0] + dx, k[1] + dz)
            if (n not in world or n in raise_ or n in walk or n in F.slope or n in F.noface or cls(n) in ROCKY_CLS | FACE
                    or cls(n) in LEDGES | {'ledge_cap'} or cls(n) in TREE_CLS or n in F.wet or n in F.decks): continue
            hn = F.y(*n)
            if any(pre.get(m, F.y(*m) if m in world else hn) > hn + 0.5 or m in F.decks
                   for m in ((n[0] + a, n[1] + b) for a, b in N8)): continue      # (a face before the raise: kept)
            F.noface.add(n); nf[cls(n)] += 1
    if nf: F.notes.append(f'9d: flat beside the raised rock (no face): {dict(nf)}')

    # 9e. (sweep_outdoor 2026-10-11) a lava pool (a warp-only map's 'lava' tiles: Mt. Chimney's crater, retiled from
    #     Sapphire's mountain metatiles) is one surface: its tiles took the nearest heights of the rock round them
    #     (72 / 81 / 88 / 92), so rock steps ran across the lava diagonally. Each pool lies at its lowest tile's height
    #     (drawing only: lava is solid, F.coll_h keeps the collision)
    for comp in _components({k for k in world if cls(k) == 'lava'}, nb):
        lo = min(F.y(*k) for k in comp)
        for k in comp:
            if F.y(*k) != lo: F.coll_h.setdefault(k, F.y(*k)); F.h[k] = lo
            F.noface.add(k)

    # 9b. Sapphire keeps two elevations apart even where nothing is drawn between them (a cliff top's edge row, a
    #     raised lawn); Black 2 lets an actor step up to 19 units (ActorRouteCollCheckCore), so such neighbours
    #     closer than 20 get a side wall: Black 2's one-way tile classes 0x51-0x58 (TileExitBlockCheck_*, ov036)
    for k in walk:
        if k in F.slope or cls(k) in LEDGES: continue
        for s_, (dx, dz) in zip('nesw', N4):
            n = (k[0] + dx, k[1] + dz)
            if n not in walk or n in F.slope or cls(n) in LEDGES: continue
            if elev[k] in (0, 15) or elev[n] in (0, 15) or elev[k] == elev[n]: continue
            if abs(F.y(*k) - F.y(*n)) < 20: F.walls.setdefault(k, set()).add(s_)

    # 10. ground texture per level region (4-connected tiles of one height): Black 2's rocky ground (gake_michi,
    #     Driftveil chunk 48) where most of the region is drawn as brown rock in Sapphire, grass elsewhere; one
    #     choice per region keeps Gen 3's mixed brown/green tiles from becoming a checkerboard
    for comp in _components(set(world) - set(F.slope), lambda k: [n for n in nb(k) if F.y(*n) == F.y(*k)]):
        if sum(p in F.rocktop or p in F.rock for p in comp) * 2 > len(comp):
            for p in comp: F.mat[p] = 'gake_michi'
        elif _emerald():
            # (emerald_polish_outdoor 2026-10-12, Emerald only) rock with no walkable tile beside it, by the sea at the
            # sea's level: the water's tiles (and the sea rocks and shore trees the water joins to it) outvoted the rock
            # and its tops were grass (Emerald's Route 103: the west end of the mountain over the sea, x 38-41, a grass
            # corner on pink rock). Each piece of land in the region (4-connected without the water) decides by its own
            # majority, and only its rock-coloured tiles take the rocky ground. (Not in v16.7: on every map it would turn
            # 1,594 sea-side rock tiles of 30 Sapphire maps rocky, unreviewed; Sapphire's own corner is listed as open)
            land = {p for p in comp if cls(p) not in WATER | SHALLOWS and world[p][0] in POLISH_MAPS}
            for sub in (_components(land, nb) if len(land) < len(comp) else ()):
                if any(p in walk for p in sub) or sum(p in F.rocktop or p in F.rock for p in sub) * 2 <= len(sub): continue
                for p in sub:
                    if p in F.rock or p in F.rocktop: F.mat[p] = 'gake_michi'
    for p in F.sea_rock: F.mat[p] = 'gake_michi'          # (the sea's rock masses: rock tops, sea_rock_masses)

    # 10b. rock style (STYLES): the tiles of the listed maps that Sapphire draws with the style tileset's own rock
    #      metatiles, then a majority filter over each rock tile's rock neighbours (no single odd tile where Gen 3 mixes
    #      its tilesets' rock); their rocky ground takes the style's ground texture (world.py draws ground by tile)
    rocky = {k for k, (ts, mt) in mtile.items() if k in world and _rocky(repo, ts, mt)}
    styled = {}
    for k in rocky:
        ts, mt = mtile[k]
        for name, st in STYLES.items():
            if ts[1] == st['tileset'] and mt >= 512 and world[k][0] in st['maps']: styled[k] = name
    if styled:
        near = {(k[0] + dx, k[1] + dz) for k in styled for dx in (-1, 0, 1) for dz in (-1, 0, 1)} & rocky
        for k in near:
            nbrs = [styled.get(n) for n in ((k[0] + dx, k[1] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dz)
                    if n in rocky]
            name, n = Counter(nbrs).most_common(1)[0] if nbrs else (None, 0)
            v = name if n >= 5 and n * 2 > len(nbrs) else styled.get(k)
            if v: F.style[k] = v
        for k, name in F.style.items():
            if F.mat.get(k) == 'gake_michi': F.mat[k] = STYLES[name]['tex']['gake_michi']

    # 11. tiles outside the maps (world.py's forest and the water module's sea around them) stand at the height of
    #     the nearest map tile, found by the same multi-source search as water.py's filler (so the outside sea takes
    #     its water's level): at 0 they put a cliff up to 96 units high and its tree-high skirts along every raised
    #     map's edge, and the forest there stood a level lower than the trees inside the map (exterior sweep 2026-10-06)
    src, q = {}, deque()
    for k, e in world.items():
        x, z = k
        if any((x + dx, z + dz) not in world for dx, dz in N4):
            src[k] = (F.h.get(k, 0) if k in F.wet else F.coll_h.get(k, F.h.get(k, 0)) // LEVEL * LEVEL, 0); q.append(k)   # (a stair's mid height: the level
            # below; heights drawn differently from the collision (F.coll_h) leave the tiles outside the maps alone;
            # water keeps its own level outside the map too: water leveled 8 over its lower shore (4b) met the sea
            # past the map's edge at an 8-unit step)
    while q:
        k = q.popleft()
        h0, d = src[k]
        if d >= 128: continue
        for dx, dz in N4:
            n = (k[0] + dx, k[1] + dz)
            if n in world or n in src: continue
            src[n] = (h0, d + 1); q.append(n)
            if h0: F.h[n] = h0
    # 11b. raised plank bridges (bridges 2026-10-18): Routes 119/120's decks over surf water stand high enough over it
    #     for a surfer to pass under them, hidden (raise_bridges); last, so every height above (the water's level from
    #     its shores, the faces, the exposed rock) is what it was with the decks at their banks' level
    raise_bridges(F, world, walk, elev, cls, nb)

    # 12. surf landing (final_check 2026-10-08): Sapphire lands a surfer only on elevation 3 (pokeruby
    #     field_player_avatar.c sub_8058EF0: an elevation mismatch with the surfer's 1 onto a tile of elevation 3; 0 and
    #     1 never mismatch, the surfer moves on); Black 2 lands it on any tile that is not solid or surfable, at any
    #     height (ov036 CheckSurfExitEvent). The walkable tiles beside surf water at another elevation (Mr. Briney's
    #     jetty and Mossdeep's north bank, 24 units up; Routes 119/120's bridge decks and raised banks) carry NOLAND,
    #     which b2tools/patches/hm_free.py SurfLandingTileType turns into "solid" for the landing check only
    F.noland = {k for k in walk if cls(k) not in WATER and elev.get(k) not in (0, 1, 3)
                and any(cls(n) in WATER for n in nb(k))}
    print(f'heights: {len(F.slope)} stair/slope tiles, {len(F.walls)} walled tiles, {len(F.noland)} no-landing tiles, {len(F.notes)} notes')
    for n in F.notes: print('heights:', n)
    return F

RAISE_CLEAR = 32     # a raised plank bridge's deck over the surf height of its water, at least (raise_bridges)
SURF_Y = -8          # a surfer's height under its water tile's (water.py Y_WATER)

def raise_bridges(F, world, walk, elev, cls, nb):
    """(bridges 2026-10-18) Gen 3 surfs under Routes 119/120's plank bridges (a walkable elevation-15 span over surf
    water: elevation 15 keeps the mover's elevation, so a surfer passes under while a walker crosses on top). Ours stood
    at their banks' level, 8 over the water's surf height: no two-layer setting both passes a surfer and hides it (the
    deck needs ~32 over the surfer: surf_under2 2026-10-18, 31.4 under Route 110's road showed nothing, 24 the hat) and
    a deeper water under the deck loses the step in from the open water beside it (20 units, ActorRouteCollCheckCore).
    So the deck is raised: the span (its columns of elevation-15 tiles) to a height D at least RAISE_CLEAR over the
    surfer (the water's surf height U, kept: no dip going under), the dry end tiles between it and each bank step 16
    at a time from the bank (Black 2's limit is 20; as step 3b's steps) and run flat on to D (even steps of 5-11 lifted
    Route 120's east end tile to 91, and the cliff tile behind it, 2 under the bank, read as open ground: walk_diff
    OPEN). D is the higher bank's height when that is
    enough and reachable from the other bank, else the lowest multiple of 16 that works. Black 2 reads the tile in front
    of the player at its grid height (16 * int(y / 16), world.py _b2_front_y): a walker on the end tile next to the
    span must still find the deck there, not the water layer under it (else the bike's tests and surfing off read the
    water), so D is raised until it does. world.py bridge_layers then gives the span two layers (water at U, the deck
    at D) and its ends a solid layer under them; ground.py draws the deck, wooden risers at its steps (F.raised_decks)
    and posts into the water (pier_posts); water.py draws the water under the deck at its own level, heights.draw rock
    faces up to the dry end tiles (abutments) and no face from the water up to the span (open_under).
    Fortree's walkways (STILTS) and decks over land or with no bank at an end (piers) are left alone."""
    F.raised_decks = set()
    front = lambda y: 16 * int(y / 16)                       # (world.py _b2_front_y)
    deck_side = lambda y, U, D: abs(y - D) + 0.5 < abs(y - U)   # (y picks the deck's layer: world.py _b2_pick)
    for comp in _components({k for k in walk if cls(k) == 'bridge' and world[k][0] not in STILTS}, nb):
        span = {k for k in comp if elev.get(k) == 15}
        water = {n for k in span for n in nb(k) if n in world and world[n][2] and cls(n) in ('water', 'deep_water')}
        if not span or not water: continue
        xs, zs = [p[0] for p in comp], [p[1] for p in comp]
        ew = max(xs) - min(xs) >= max(zs) - min(zs)
        axis = 0 if ew else 1
        lo_, hi_ = min(p[axis] for p in comp), max(p[axis] for p in comp)
        n = hi_ - lo_ + 1
        col = lambda i: [p for p in comp if p[axis] - lo_ == i]
        wet = [i for i in range(n) if col(i) and all(p in span for p in col(i))]
        if not wet or any(i not in wet for i in range(wet[0], wet[-1] + 1)) or any(not col(i) for i in range(n)):
            F.notes.append(f'bridge at {min(comp)}: not raised (its span is not one run of whole columns)'); continue
        def bank(end, d):
            hs = [F.y(*q) for p in col(end) for q in [((p[0] + d, p[1]) if ew else (p[0], p[1] + d))]
                  if q in walk and cls(q) != 'bridge' and q not in F.slope and cls(q) not in WATER]
            return Counter(hs).most_common(1)[0][0] if hs else None
        h0, h1 = bank(0, -1), bank(n - 1, 1)
        if h0 is None or h1 is None:
            F.notes.append(f'bridge at {min(comp)}: not raised (no bank at an end)'); continue
        dry_lo, dry_hi = wet[0], n - 1 - wet[-1]
        U = min(F.y(*q) for q in water) + SURF_Y
        def profile(D):
            """column -> height for a span at D, or None when a step is over 16 or a walker next to it reads water."""
            out = {i: D for i in wet}
            step = lambda h, k: h + max(-abs(D - h), min(abs(D - h), 16 * k)) * (1 if D >= h else -1)
            for i in range(dry_lo): out[i] = step(h0, i + 1)
            for j in range(dry_hi): out[n - 1 - j] = step(h1, j + 1)
            seq = [h0] + [out[i] for i in range(n)] + [h1]
            if any(abs(a - b) > 16 for a, b in zip(seq, seq[1:])): return None
            for L in (seq[wet[0]], seq[wet[-1] + 2]):            # (the end tile or bank next to the span)
                if not (deck_side(L, U, D) and deck_side(front(L), U, D)): return None
            return out
        need = U + RAISE_CLEAR
        top = max(h0, h1)
        tries = ([top] if top >= need else []) + list(range(-(-need // 16) * 16, need + 16 * (n + 2), 16))
        D = next((d for d in tries if profile(d)), None)
        if D is None:
            F.notes.append(f'bridge at {min(comp)}: not raised (no deck height {RAISE_CLEAR} over its water works)'); continue
        hs = profile(D)
        for p in comp:
            F.h[p] = hs[p[axis] - lo_]; F.coll_h.pop(p, None)
        F.raised_decks |= set(comp)
        F.notes.append(f'bridge at {min(comp)}: surf-under span at {D} over surf water at {U} (banks {h0} and {h1}, '
                       f'end tiles {[hs[i] for i in range(n) if i not in wet]})')

# ---- geometry ------------------------------------------------------------------------------------------------------
# Black 2's cliff (Route 1 chunk 2, Route 20 chunk 287, Route 19 chunk 282): the face stands in the LOW tile next to
# the high ground; its lip (gake1_1 under grass, gake1_0 under rock) rolls 4 units down over the first half tile and
# the face (gake01a; yamagake01 on tall walls) drops to the low ground over the second half; outer corners are a lip
# triangle and a face fan in the diagonal tile; straight stretches are one strip per run.
# Here every face tile gets a 3x3 lattice of heights (corners, edge middles, centre: 8 units apart) from the higher
# tiles touching it - their height on the shared edge/corner, LIP lower one lattice step in, the tile's own height
# beyond - and is drawn as 4 sub-quads. Neighbouring tiles compute the same heights for shared points, and where two
# tiles still disagree along an edge (steps between flat tiles, stairs sides, faces of different heights) a vertical
# skirt closes the gap, so the terrain has no holes. Flat ground itself is world.py's (build_chunk.ground_heights).
LIP = 4
MERGE_SKIRTS = True      # (one wall per straight run: T-junctions with the lattice faces beside it left 1-pixel cracks)
TALL = 24                        # faces higher than this use Black 2's tall wall texture (yamagake01, Route 19)
# Route 19 chunk 282 stretches yamagake01 (16x32) once over its 60-unit wall: one repeat per started 64 units
TALL_REPEAT = lambda h: h / max(1, -(-h // 64))
GAKE_FOOT = 1 / 6                 # gake01a's v starts at 1/7 up: its bottom 2 of 16 texel rows are transparent at the tile ends

class _Lattice:
    """Face-tile lattices and edge heights around one cell (memoised per cell)."""
    def __init__(self, F):
        self.F, self.memo, self.world = F, {}, {}

    def face(self, k):
        """Unwalkable, not a slope, and lower than a (non-slope) 8-neighbour: holds a cliff profile."""
        F = self.F
        if k in F.walk or k in F.slope or k in F.noface: return False
        h = F.y(*k)
        return any(F.y(k[0] + dx, k[1] + dz) > h and (k[0] + dx, k[1] + dz) not in F.slope and
                   not self.open_under(k, (k[0] + dx, k[1] + dz))
                   for dx in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dz)

    def water_step(self, k, q):
        """k a sea rock drawn at the lower water's level (lower_rocks, card masses) beside q, water higher than it: no
        rock skirt between them (it stood 11 over the higher water's surface as a brown bar behind the rock card); the
        higher water's sheets end at the rock."""
        F = self.F
        return k in F.noface and q in F.wet and F.y(*k) < F.y(*q) <= F.y(*k) + LEVEL

    def open_under(self, k, q):
        """Water k beside a deck q higher than it: open water under a pier (posts and the water, terrain/ground.py
        pier_posts and water.py), no rock face from the deck down to the water. Likewise the forest floor k beside a
        walkway on posts q (STILTS)."""
        F = self.F
        if q in F.stilt_decks and k in F.stilt_ground: return True     # (a walkway on posts over the forest floor)
        if q not in F.decks or (k not in F.wet and k not in F.noface): return False
        if q not in F.deck_water:                  # (a deck end resting on its bank keeps the bank under it)
            g = sys.modules.get('terrain.ground')
            F.deck_water[q] = bool(g and g.water_under(self.world, *q) is not None)
        return F.deck_water[q]

    def surf(self, k, i, j):
        """Height of tile k's surface at its lattice point (i, j) (0..2 from its west/north edge)."""
        F = self.F
        if k in F.slope:
            side, y0, r = F.slope[k]
            d = {'n': j, 's': 2 - j, 'w': i, 'e': 2 - i}[side] * 8
            return y0 + r * (16 - d) / 16
        if self.face(k): return self.lattice(k)[j][i]
        return F.y(*k)

    def lattice(self, k):
        if k in self.memo: return self.memo[k]
        F = self.F
        L = F.y(*k)
        v = [[None] * 3 for _ in range(3)]
        src = set()
        for j in range(3):
            for i in range(3):
                if i == 1 and j == 1: continue
                best = None
                # tiles touching this boundary point (besides k): offsets -1/0 per axis on the edges
                for dx in ((-1, 0) if i == 0 else (0, 1) if i == 2 else (0,)):
                    for dz in ((-1, 0) if j == 0 else (0, 1) if j == 2 else (0,)):
                        q = (k[0] + dx, k[1] + dz)
                        if q == k or q in F.slope or F.y(*q) <= L or self.open_under(k, q): continue
                        hq = self.surf(q, i - 2 * dx, j - 2 * dz)
                        if best is None or hq > best: best = hq
                if best is not None and best > L: v[j][i] = best; src.add((i, j))
        for j in range(3):
            for i in range(3):
                if v[j][i] is not None: continue
                c = [v[b][a] - min(LIP, (v[b][a] - L) / 4) for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                     if (a, b) in src]
                v[j][i] = max(c) if c else L
        self.memo[k] = v
        return v

    def edge(self, k, side):
        """Heights of tile k's surface at the 3 lattice points of one side, west->east / north->south."""
        pts = {'n': [(0, 0), (1, 0), (2, 0)], 's': [(0, 2), (1, 2), (2, 2)],
               'w': [(0, 0), (0, 1), (0, 2)], 'e': [(2, 0), (2, 1), (2, 2)]}[side]
        return [self.surf(k, i, j) for i, j in pts]

def _riser(F, hi, lo):
    """A raised plank bridge's deck tile hi standing over the walkable tile lo beside it (its bank, a lower step):
    terrain/ground.py deck_risers closes that step with planks, no rock skirt here (raise_bridges)."""
    return hi in getattr(F, 'raised_decks', ()) and lo in F.walk and lo not in F.slope and F.y(*hi) > F.y(*lo) + 0.5

_LAT = {}
def _lat(F):
    if id(F) not in _LAT: _LAT.clear(); _LAT[id(F)] = _Lattice(F)
    return _LAT[id(F)]

def _uv_face(p, n, ymin, ymax, tall):
    """Face texture coordinates: u along the wall (to the viewer's right), v up the wall (1 = top)."""
    x, y, z = p
    if abs(n[2]) >= abs(n[0]): u = x / 16 if n[2] > 0 else -x / 16
    else: u = -z / 16 if n[0] > 0 else z / 16
    v = (y - ymin) / TALL_REPEAT(ymax - ymin) if tall else (y - ymin) / max(ymax - ymin, 1e-3)
    return u, v

def _normal(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    return (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)

def _emit(m, pts, lip_tex, top, face_tex):
    """One terrain triangle of a face tile (points (x, y, z) wound to face up/out): lip if it lies in the top LIP
    units of the tile's profile, else face."""
    ys = [p[1] for p in pts]
    n = _normal(*pts)
    # (walkability 2026-10-11) a face turned away from every Black 2 field camera (they look north and down, 30 to 53
    # degrees - Slateport's 52.6 - and cull back faces: the north sides of raised rock) is never drawn; it only cost
    # triangles. Tested against a camera 65 degrees down, the steepest it could be seen from
    ln = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
    if ln > 0 and (0.906 * n[1] + 0.423 * n[2]) / ln < -0.05: return
    if min(ys) >= top - LIP - 0.01:
        ymax = max(ys)
        m.tri(lip_tex, [(x, y, z, _uv_face((x, y, z), n, 0, 1, False)[0], 1 - (ymax - y) / LIP) for x, y, z in pts])
    else:
        lo, hi = min(ys), max(ys)
        tall = hi - lo > TALL
        tex = 'yamagake01' if tall else face_tex
        if tex == 'gake01a': lo -= (hi - lo) * GAKE_FOOT     # (its transparent foot rows: see _skirt)
        m.tri(tex, [(x, y, z) + _uv_face((x, y, z), n, lo, hi, tall) for x, y, z in pts])

def _skirt(m, p0, p1, a, b, toward_b, tex):
    """Vertical wall along the edge p0 -> p1 (model (x, z)) where the surfaces on its two sides disagree: a and b are
    the two sides' heights at the edge's 3 lattice points; the wall faces the lower side (toward_b = unit (x, z)
    direction from the a side to the b side)."""
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    for (q0, q1), (a0, a1), (b0, b1) in (((p0, mid), a[:2], b[:2]), ((mid, p1), a[1:], b[1:])):
        if abs(a0 - b0) < 0.01 and abs(a1 - b1) < 0.01: continue
        hi0, hi1, lo0, lo1 = max(a0, b0), max(a1, b1), min(a0, b0), min(a1, b1)
        down = toward_b if (a0 + a1) >= (b0 + b1) else (-toward_b[0], -toward_b[1])
        lo, hi = min(lo0, lo1), max(hi0, hi1)
        tall = hi - lo > TALL and tex != 'kaidan01a'
        # (walkability 2026-10-11) gake01a's two bottom texel rows are transparent at the tile ends: the void showed
        # through as a blue line at the foot of the raised rock (outdoor_check hole). Its v starts at 1/7 (GAKE_FOOT)
        sink = (hi - lo) * GAKE_FOOT if tex == 'gake01a' and not tall else 0.0
        def P(q, y, s):
            if tex == 'kaidan01a': return (q[0], y, q[1], 0.09 * (y - lo) / max(hi - lo, 1e-3), s)
            u = (q[0] * down[1] - q[1] * down[0]) / 16
            return (q[0], y, q[1], u, (y - lo) / TALL_REPEAT(hi - lo) if tall else (y - lo + sink) / max(hi - lo + sink, 1e-3))
        pts = [P(q0, lo0, 0), P(q1, lo1, 0.5), P(q1, hi1, 0.5), P(q0, hi0, 0)]
        pts = [p for i, p in enumerate(pts) if abs(p[1] - pts[i - 1][1]) > 0.01 or p[0] != pts[i - 1][0] or p[2] != pts[i - 1][2]]
        if len(pts) < 3: continue
        n = _normal(*[p[:3] for p in pts[:3]])
        if n[0] * down[0] + n[2] * down[1] < 0: pts = pts[::-1]
        t = 'yamagake01' if tall else tex
        if len(pts) == 3: m.tri(t, pts)
        else: m.quad(t, pts)

def _stairs(m, x0, z0, up, y0, rise, n=1):
    """A run of n stair tiles (kaidan01a, steps 16 units apart as in Accumula chunk 5 / Route 20 chunk 287) rising
    `rise` towards side `up` from y0 at the opposite edge; the run extends along the edge (east for n/s, south
    for e/w)."""
    L = 16 * n
    def P(a, d, y, u, v):      # a along the step edge, d depth from the top edge
        x, z = {'n': (x0 + a, z0 + d), 's': (x0 + L - a, z0 + 16 - d), 'w': (x0 + d, z0 + L - a),
                'e': (x0 + 16 - d, z0 + a)}[up]
        return (x, y, z, u, v)
    v0, v1 = -y0 * 3 / 16, -(y0 + rise) * 3 / 16
    m.quad('kaidan01a', [P(0, 16, y0, 0.12, v0), P(L, 16, y0, 0.12 + n * 0.88, v0),
                         P(L, 0, y0 + rise, 0.12 + n * 0.88, v1), P(0, 0, y0 + rise, 0.12, v1)])

def draw(m, cell):
    if FIELD is None: return
    from . import cave_mouth          # cliffs are drawn with the rock around each cave mouth raised (drawing only)
    F = cave_mouth.drawn(FIELD, cell.world)
    skip = getattr(F, 'skip', None)   # (the faces a mouth's opening replaces)
    bc = cell.bc
    X, Z = cell.X, cell.Z
    lat = _lat(F); lat.world = cell.world
    hy = lambda tx, tz: F.y(X + tx, Z + tz)
    # 1. face tiles: lattice sub-quads; straight, planar sub-quads merge into strips (one strip per run)
    xs_runs, zs_runs = {}, {}
    for tz in range(32):
        for tx in range(32):
            k = (X + tx, Z + tz)
            if not lat.face(k): continue
            v = lat.lattice(k); L = F.y(*k); top = max(max(r) for r in v)
            hi_n = max(((X + tx + dx, Z + tz + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)),
                       key=lambda q: F.y(*q))
            # (a step between two water levels, or up to a sea rock, is rock: a reef, not a grass bank; overworld_polish)
            rocky = hi_n in F.rock or hi_n in F.rocktop or (cell.world.get(hi_n) or (0, 0))[1] in WATER | {'rock'}
            lip = 'gake1_0' if rocky else 'gake1_1'
            face_tex = 'yamagake01' if F.kind.get(hi_n) == 'mountain' else 'gake01a'
            x0, z0 = bc.ux(tx), bc.uz(tz)
            for j in range(2):
                for i in range(2):
                    if skip and skip(k, j): continue
                    hNW, hNE, hSE, hSW = v[j][i], v[j][i + 1], v[j + 1][i + 1], v[j + 1][i]
                    if max(hNW, hNE, hSE, hSW) - L < 0.01: continue          # on the ground: world.py draws it
                    sx, sz = 2 * tx + i, 2 * tz + j
                    key = (lip, face_tex, top)
                    if abs(hNW - hNE) < 0.01 and abs(hSW - hSE) < 0.01:
                        xs_runs.setdefault((sz, hNW, hSW) + key, []).append(sx); continue
                    if abs(hNW - hSW) < 0.01 and abs(hNE - hSE) < 0.01:
                        zs_runs.setdefault((sx, hNW, hNE) + key, []).append(sz); continue
                    a, b = x0 + 8 * i, z0 + 8 * j
                    NW, NE, SE, SW = (a, hNW, b), (a + 8, hNE, b), (a + 8, hSE, b + 8), (a, hSW, b + 8)
                    if abs(hNW - hSE) <= abs(hNE - hSW): tris = [(SW, SE, NW), (SE, NE, NW)]
                    else: tris = [(SW, SE, NE), (SW, NE, NW)]
                    for t in tris:
                        # a half on the ground is the ground (world.py draws it there): a second copy z-fights
                        if all(abs(p[1] - L) < 0.01 for p in t): continue
                        _emit(m, t, lip, top, face_tex)
    def runs(xs):
        xs = sorted(xs); out = [[xs[0], xs[0]]]
        for x in xs[1:]:
            if x == out[-1][1] + 1: out[-1][1] = x
            else: out.append([x, x])
        return out
    for (sz, hN, hS, lip, face_tex, top), xs in xs_runs.items():
        for s0, s1 in runs(xs):
            a0, a1, b = s0 * 8 - 256, s1 * 8 + 8 - 256, sz * 8 - 256
            NW, NE, SE, SW = (a0, hN, b), (a1, hN, b), (a1, hS, b + 8), (a0, hS, b + 8)
            for t in [(SW, SE, NE), (SW, NE, NW)]: _emit(m, t, lip, top, face_tex)
    for (sx, hW, hE, lip, face_tex, top), zs in zs_runs.items():
        for s0, s1 in runs(zs):
            b0, b1, a = s0 * 8 - 256, s1 * 8 + 8 - 256, sx * 8 - 256
            NW, NE, SE, SW = (a, hW, b0), (a + 8, hE, b0), (a + 8, hE, b1), (a, hW, b1)
            for t in [(SW, SE, NE), (SW, NE, NW)]: _emit(m, t, lip, top, face_tex)
    # 2. skirts: every tile edge on the north/west side of this cell's tiles (incl. the cell's own north/west border).
    #    (walkability 2026-10-11) A skirt facing north (its south side higher) is never drawn: Black 2's camera looks
    #    north and culls back faces, so it only cost triangles; flat skirts along a straight line join into one wall
    #    per run (the rock heights.py 9d raises beside paths gave +47,000 triangles of one-tile skirts)
    skirt_runs = {}
    for tz in range(32):
        for tx in range(32):
            k = (X + tx, Z + tz)
            x0, z0 = bc.ux(tx), bc.uz(tz)
            for side, q, p0, p1, toward in (('n', (k[0], k[1] - 1), (x0, z0), (x0 + 16, z0), (0, 1)),
                                            ('w', (k[0] - 1, k[1]), (x0, z0), (x0, z0 + 16), (1, 0))):
                a = lat.edge(q, 's' if side == 'n' else 'e')     # the neighbour's side (north / west of the edge)
                b = lat.edge(k, side)
                if max(abs(p - r) for p, r in zip(a, b)) < 0.01: continue
                if lat.open_under(k, q) or lat.open_under(q, k): continue    # (a pier over its water: open under)
                if lat.water_step(k, q) or lat.water_step(q, k): continue    # (sea rocks parting two water levels)
                if _riser(F, k, q) or _riser(F, q, k): continue      # (a raised bridge's step: ground.py's wooden riser)
                if side == 'n' and min(b) >= max(a) - 0.01: continue           # (faces north: culled, never seen)
                upper_slope = (q in F.slope and sum(a) > sum(b)) or (k in F.slope and sum(b) > sum(a))
                tex = 'kaidan01a' if upper_slope else 'gake01a'
                if MERGE_SKIRTS and tex == 'gake01a' and max(a) - min(a) < 0.01 and max(b) - min(b) < 0.01:
                    line = z0 if side == 'n' else x0
                    along = x0 if side == 'n' else z0
                    skirt_runs.setdefault((side, line, round(a[0], 2), round(b[0], 2)), []).append(along)
                    continue
                _skirt(m, p0, p1, a, b, toward, tex)
    for (side, line, av, bv), starts in skirt_runs.items():
        starts = sorted(starts); run = [starts[0], starts[0]]
        for st in starts[1:] + [None]:
            if st is not None and abs(st - run[1] - 16) < 0.01: run[1] = st; continue
            if side == 'n': p0, p1, toward = (run[0], line), (run[1] + 16, line), (0, 1)
            else: p0, p1, toward = (line, run[0]), (line, run[1] + 16), (1, 0)
            _skirt(m, p0, p1, (av, av, av), (bv, bv, bv), toward, 'gake01a')
            if st is not None: run = [st, st]
    # 3. stairs (Accumula chunk 5, Route 20 chunk 287), one quad per tile
    done = set()
    for tz in range(32):
        for tx in range(32):
            k = (X + tx, Z + tz)
            if k not in F.slope or k in done: continue
            side, y0, rise = F.slope[k]
            d = (1, 0) if side in 'ns' else (0, 1)
            n = 1
            while (tx + d[0] * n < 32 and tz + d[1] * n < 32 and
                   F.slope.get((k[0] + d[0] * n, k[1] + d[1] * n)) == (side, y0, rise)): n += 1
            for s in range(n):
                done.add((k[0] + d[0] * s, k[1] + d[1] * s))
                _stairs(m, bc.ux(tx + d[0] * s), bc.uz(tz + d[1] * s), side, y0, rise)
    # 4. side ledges, one lip per run of tiles in a column (Route 20 / Route 19 recipes, b2tools/build_chunk.py)
    get = lambda tx, tz: cell.get(tx, tz)
    for kind, east in (('ledge_e', True), ('ledge_w', False)):
        for tx in range(32):
            run = []
            for tz in range(33):
                e = get(tx, tz) if tz < 32 else None
                if e and e[1] == kind and (not run or hy(tx, tz) == hy(tx, run[0])): run.append(tz); continue
                if run:
                    tmp = type(m)('ledge'); bc.ledge_run_ew(tmp, tx, run[0], run[-1], east, get, hy)
                    m.extend(tmp, dy=hy(tx, run[0]))
                run = [tz] if e and e[1] == kind else []
    # 5. cave mouths: Black 2's mouth in its 2-tier rock (terrain/cave_mouth.py)
    cave_mouth.draw(m, cell, F)
    # 6. rock styles: the rock textures of styled tiles (whatever drew them so far: world.py's ground, this module)
    _restyle(m, cell, F)

def _style_pieces(t, style, X, Z):
    """[(style or None, triangle)] of triangle t (model units of the cell at world tile X, Z): t whole when the tiles
    it covers share one style, else its parts per tile (Field.pieces' clipping). A wall standing on a tile edge
    belongs to the tile behind it (its face points away from it)."""
    P = [v[:3] for v in t]
    n = _normal(*P); ln = (n[0] ** 2 + n[2] ** 2) ** 0.5
    nx, nz = (n[0] / ln * 0.5, n[2] / ln * 0.5) if ln > 1e-6 and abs(n[1]) < 0.7 * (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 else (0, 0)
    xs = [p[0] - nx for p in P]; zs = [p[2] - nz for p in P]
    tx0, tx1 = int((min(xs) + 256) // 16), int((max(xs) + 256 - 1e-6) // 16)
    tz0, tz1 = int((min(zs) + 256) // 16), int((max(zs) + 256 - 1e-6) // 16)
    tx1, tz1 = max(tx0, tx1), max(tz0, tz1)
    tiles = {(a, b): style.get((X + a, Z + b)) for a in range(tx0, tx1 + 1) for b in range(tz0, tz1 + 1)}
    if len(set(tiles.values())) == 1: return [(next(iter(tiles.values())), t)]
    flat_x, flat_z = max(xs) - min(xs) < 1e-6, max(zs) - min(zs) < 1e-6
    out = []
    for (a, b), st in tiles.items():
        poly = [tuple(v[:5]) + tuple(v[5]) for v in t]
        for axis, value, keep in ((0, a * 16 - 256 + nx, True), (0, a * 16 - 240 + nx, False),
                                  (2, b * 16 - 256 + nz, True), (2, b * 16 - 240 + nz, False)):
            if (axis == 0 and flat_x) or (axis == 2 and flat_z): continue
            if min(p[axis] for p in poly) >= value - 1e-6 if keep else max(p[axis] for p in poly) <= value + 1e-6:
                continue
            poly = _clip_axis(poly, axis, value, keep)
            if len(poly) < 3: break
        if len(poly) < 3: continue
        for i in range(1, len(poly) - 1):
            tri = [poly[0], poly[i], poly[i + 1]]
            q = _normal(*[p[:3] for p in tri])
            if q[0] ** 2 + q[1] ** 2 + q[2] ** 2 < 1e-6: continue
            out.append((st, [(p[0], p[1], p[2], p[3], p[4], tuple(p[5:])) for p in tri]))
    return out

def _banded(t):
    """A tall face triangle (yamagake01: v 0..1 per repeat, one repeat per started 64 units, TALL_REPEAT) on
    out57_gake01a's opaque rows: each repeat's v 0..1 becomes 0.125..1 (the face's 2 bottom rows are transparent:
    Reversal Mountain has no tall-wall texture, its cliffs are 16-unit tiers of that face). Cut only where a triangle
    crosses a repeat (walls over 64 units): 16-unit tiers cut chunks (6,3)/(7,3) to 135 KB, over the 110,600 limit."""
    vs = [v[4] for v in t]
    out = []
    for k in range(int(min(vs) // 1), max(int(min(vs) // 1) + 1, int(-(-max(vs) // 1)))):
        poly = [tuple(v[:5]) + tuple(v[5]) for v in t]
        for value, keep in ((k, True), (k + 1, False)):
            if min(p[4] for p in poly) >= value - 1e-6 if keep else max(p[4] for p in poly) <= value + 1e-6: continue
            poly = _clip_axis(poly, 4, value, keep)
            if len(poly) < 3: break
        if len(poly) < 3: continue
        poly = [p[:4] + (0.125 + 0.875 * min(1.0, max(0.0, p[4] - k)),) + p[5:] for p in poly]
        for i in range(1, len(poly) - 1):
            tri = [poly[0], poly[i], poly[i + 1]]
            q = _normal(*[p[:3] for p in tri])
            if q[0] ** 2 + q[1] ** 2 + q[2] ** 2 < 1e-6: continue
            out.append([(p[0], p[1], p[2], p[3], p[4], tuple(p[5:])) for p in tri])
    return out

def _restyle(m, cell, F):
    """Rename the rock textures of this cell's styled tiles (STYLES), cutting triangles at the style's edge."""
    style = getattr(F, 'style', None)
    X, Z = cell.X, cell.Z
    if not style or not any((X + a, Z + b) in style for a in range(-1, 33) for b in range(-1, 33)): return
    for mat in [t for t in list(m.tris) if t != 'gake_michi' and any(t in st['tex'] for st in STYLES.values())]:
        keep, moved = [], {}
        for t in m.tris[mat]:
            for st, piece in _style_pieces(t, style, X, Z):
                new = STYLES[st]['tex'].get(mat) if st else None
                if new is None: keep.append(piece); continue
                moved.setdefault(new, []).extend(_banded(piece) if mat == 'yamagake01' else [piece])
        if keep: m.tris[mat] = keep
        else: del m.tris[mat]
        for new, tris in moved.items(): m.tris.setdefault(new, []).extend(tris)

def collision(cls, tile, cell):
    """Black 2 records for this module's classes (heights are added by Field.record)."""
    floor = (FIELD.floor.get(tile[0], 'route') if FIELD else 'route')
    walkable = (0, 3, 0x001F, 0x0080) if floor == 'route' else (0, 3, 0x0000, 0x0080)
    SOLID = (0, 3, 0x0001, 0x0081)
    if cls == 'ledge_e': return (0, 3, 0x0072, 0x0001), '>'      # MapTile_IsLedgeR; Route 20 chunk 286
    if cls == 'ledge_w': return (0, 3, 0x0073, 0x0001), '<'      # MapTile_IsLedgeL; Route 19 chunk 282
    if cls in ('stairs', 'mud'): return ((0, 3, 0x0000, 0x0080), '.') if tile[2] else (SOLID, '#')   # B2 stairs
    if cls in ('cave_entrance', 'ledge_cap', 'mountain') or not tile[2]: return SOLID, '#'
    return walkable, '.'
