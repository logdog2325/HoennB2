"""General interior builder: a Sapphire room (pokeruby map) rebuilt as a Black 2 interior chunk (notes/INTERIORS.md).

    python3 models_interior.py [NAME ...]        (default: every data/interior_layouts/*.json except _*.json)

Input: data/interior_layouts/<NAME>.json (room recipe) + _styles.json (texture styles) + Sapphire's map (layout,
collision, warp events from external/pokeruby). Output: work/interiors/<NAME>/ terrain.dae (+ texture PNGs),
palettes.txt, collision.per, placements.bin, room.json. b2tools/rebuild_interiors.sh runs this and ToNsbmd --vcol;
b2tools/patches/interiors.py installs the room into a zone (data/interiors/<zone>.json).

Built the way Black 2 builds its own rooms (chunks 838, 977, 1049): floor at y -2, walls 50 high (y -2..48) standing
12 units north of the first floor row and 3 units outside the side columns, black wall caps 16 wide, no south wall
(the camera looks from the south) but a black floor lip down to y -18, a one-tile stone "genkan" notch below each exit
mat (decoration; the mat itself is the type-1 exit warp, as in Black 2 and Sapphire), shading baked into vertex colours (back wall 1.0 -> 0.81 at the top, side walls 0.48, floor strips along
the walls 0.81/0.84), the room in the top-left of an otherwise empty chunk (black around it).

Room recipe (all positions in Sapphire map tiles; x east, z south; tile (x, z) covers x..x+1, z..z+1):
  map          pokeruby map name (collision, size, warp events)
  decomp       the decomp of that map, a folder of external/ (default pokeruby; pokeemerald for Emerald-only rooms)
  style        name in _styles.json: floor / wall / genkan / black textures, each {tex, src (map texture set)}
  floor        tile rects [x0, z0, x1, z1] (inclusive) that have floor; walls follow the outline
  floor_extra  unit-precise rects [x0, z0, x1, z1] in tile units (floats, not expanded by the wall insets)
  holes        rects in tile units cut out of the floor (a stair_d01 opening)
  mats         rugs: {tex, src, rect: [x0, z0, x1, z1] tiles inclusive, border: texture fraction kept unstretched;
               uv: [u0, v0, u1, v1] one quad showing that part of the texture instead}
  furniture    {m: model name (interior packs a/2/2/6) or res: id, tile: [x, z] | tiles: [x0, z0, x1, z1] | at: [x, z]
               (footprint centre, tile units), rot: 0/90/180/270 (front faces south/east/north/west),
               wall: N/W/E (back against that wall), gap: units off the wall, n_edge/s_edge/w_edge/e_edge: put that
               side of the footprint on a tile line, y, dx, dz: units)
               lift: false keeps the piece at its y (otherwise it is lifted >= LAYER above a rug or piece under it);
               stair: [x, z] + dir N/S/E/W for stair_u01/stair_d01: placed on that warp tile as Black 2's houses place
               stairs (STAIR_MODELS: foot / top step on the approach edge, a recess in the walls, stair_d01's opening,
               45-degree collision planes); m may name a DERIVED_MODELS entry (a Black 2 model resized to a footprint)
  block        tiles to make solid although Sapphire's collision lets you on (bed heads: MB_IMPASSABLE_SOUTH_AND_NORTH)
  unblock      tiles to make walkable although Sapphire's collision blocks them: another state of a room Sapphire redraws
               with setmetatile (Mauville Gym's barriers: b2tools/gyms_league_rooms.py; story_fixups 2026-10-07)
  decals       flat pictures on the back wall: {tex, src, at: [x (tile units, centre)], y: bottom, w, h (units)}
  exits / stairs  override the ones found in Sapphire's warp events (exit mat tiles; stair tiles, entered from the south)
  origin       chunk tile of Sapphire tile (0, 0) (default: x 1, first floor row on chunk row 2)
  mirror_of    another recipe to mirror left-right (Sapphire's May house = Brendan house mirrored); keys given here win
  floor_tex    floor texture regions (part of the floor itself, no layering): {rect: [x0, z0, x1, z1] tiles inclusive |
               units: [x0, z0, x1, z1] tile units, tex, src, size (units per repeat, default 32), stretch (one texture
               over the region), rot (0/90/180/270, turns the texture), uv: [u, v] offset}; later entries win
  blocks       raised boxes standing on the floor (gym walls, rock ledges, pedestals): {rect | units | tiles: [[x, z]...],
               h (height in units), top: {tex, src, size}, side: {tex, src, u_size, v: [v0, v1], v_size}, shade_top,
               shade_s (south face), shade_we (side faces); "use": a name in the _styles files supplies defaults}.
               Only the faces the camera can see are drawn (top, south, west, east); collision stays Sapphire's
  open         tile rects [x0, z0, x1, z1] outside the floor where the room has no wall: the floor edge facing them
               gets only a black lip (walkways floating in the dark, as Black 2's League corridors); true = no walls at all
  ledges       true: Sapphire's jump tiles (MB_JUMP_*) become Black 2 ledge cells (jumped over in their direction)
  encounters   true: walkable tiles with Sapphire's wild-encounter behaviours get Black 2's encounter flag (0x84)
  raised / ramps / water   walkable tiles on a higher level, 45-degree sloped floors between levels, Black 2 surf
               water (ship_hideouts agent; the keys are described above Room.water_tiles)
  decals also take "uv" [u0, v0, u1, v1] (a part of an atlas texture) and "face_z" (a tile line: a block's face)
  inner_walls  {top: {tex, src, size}, side (default: the style's wall), h (default 50), h_low (16), near (3), max (2),
               dark (100), tiles / except}: Sapphire's thin walls between two floors of the room and light islands
               (inner_wall_tiles) become floor + a block with that top instead of walls with a black cap; tiles with a
               walkable tile < near tiles north of them are h_low high (the camera sees a player behind them); the
               blocks stand where the walls stood (12 units off the floor south, 3 beside) (sweep_rooms 2026-10-07)
  solid_y      [{y, tiles}]: solid tiles whose collision height is y (a table top under a Poke Ball: it stands on it)
  wall_rows    "keep": no bare_wall_tiles (the back wall stays 12 units north of the floor rects' first row)
  matrix       [w, h] chunks; default: as many as the room needs. A room bigger than one chunk (32x32 tiles incl. its
               walls) is spread over a w x h matrix of chunks the way Black 2's big interiors are (e.g. P2 Lab, zone 239:
               matrix 191 = 1x2 chunks 935/970, all loaded at once by an interior map type): the geometry is cut at the
               chunk edges, each chunk gets its own terrain/collision/placements (room.json "chunks", row-major)
Big rooms: output terrain.dae / collision.per / placements.bin = chunk 0 (as before) plus terrain_c<k>.dae, collision_c<k>.per,
placements_c<k>.bin for chunk k >= 1 (converted to terrain_c<k>.nsbmd here, with ToNsbmd --vcol) and terrain_all.dae
(the whole room, for previews). Zone tiles then run over the whole matrix (x = chunk x * 32 + tile).
"""
import os, sys, json, struct, math, glob
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import b2files, nsbtx                                      # noqa: E402
from dae import Model                                       # noqa: E402

FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
OUT = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
T = 16                                  # units per tile
BACK, SIDE = 12, 3                      # wall insets (Black 2 chunk 838)
FRONT_H = 18                            # blocks up to this height may reach the tile edge in front of a walkable tile
                                        # (camera 0: a person's sprite is drawn over geometry up to ~19 units there)
Y0, YW, YLIP = -2, 48, -18              # floor, wall top, bottom of the black lip
CAP = 16                                # black wall-top width
CORNER_H = 16                           # a side wall's first tile when a walkable tile is diagonally north of it
SHADE_BACK_WALL = (1.0, 0.81)           # bottom, top (chunk 977)
SHADE_SIDE_WALL = 0.48
SHADE_FLOOR_BACK, SHADE_FLOOR_SIDE = 0.81, 0.84
MB_SOUTH_ARROW_WARP, MB_NON_ANIMATED_DOOR = 0x65, 0x60
# Layered surfaces closer than this flicker in melonDS depending on the camera (z-fighting; DeSmuME hides it). Black 2
# keeps its rugs ~2 above the floor, so the builder lifts every rug ("mats") >= LAYER above the floor, any raised block
# top under it and every earlier rug it overlaps; keeps wall decals >= LAYER in front of the wall (and of earlier
# decals they overlap); lifts furniture standing on a rug or on another piece so its lowest face (shadow) is >= LAYER
# above that surface, and moves a floor cushion sideways off a neighbour's shadow (rooms_cleanup agent, 2026-10-06;
# recipes may still give larger y/gap values)
LAYER = 2
# Seams (small_fixes 2026-10-13, player report from a 3DS: a thin dashed diagonal line across Birch's lab floor, from
# the bottom-left to near the top-right). dae.Model.quad splits a quad into two triangles along its first-to-third-corner
# diagonal, and a room's floor is a few big quads (rects), so one long diagonal crosses the room. Real DS hardware (as
# melonDS) leaves 1-pixel gaps along such long, shallow shared edges, and the background showed through; DeSmuME's
# renderer closes them. Every flat surface of a room (floor, floor_tex regions, genkan, block tops: floor_quad) has a
# twin UNDER units below it, same texture and shade, split along the other diagonal: through a gap the camera sees the
# twin, whose own diagonal crosses the surface's at a single point. UNDER is 4 (the mist caves' crack cover): 2 put the
# twin level with the Pokémon Centers' stools and the Battle Tower's sofas, sunk 2 into the floor (rooms_check f). Only
# quads at least SEAM_W units wide get one: a narrower quad's diagonal is short or steep on screen (a few pixels at
# most), and the small pieces (Mt. Pyre's graves, Mossdeep Gym's tiles) would have added hundreds of triangles.
# (Outdoors the same family of cracks was fixed by an under-floor too: build_chunk.path_cover, purple_lines
# 2026-10-13; caves: models_cave seam_cover.)
UNDER, SEAM_W = 2 * LAYER, 2 * 16
# Stairs the way Black 2's houses build them (Nuvema 390/391, Aspertia 429/430, Striaton 828/829; rooms_cleanup agent):
# the warp tile is the first tile of the flight, the model's foot (stair_u01, rising toward its -x: foot x = +16) or the
# top edge of its steps (stair_d01, descending toward its +x: x = -16; its plate x < -16 lies hidden under the floor of
# the approach tile) on the warp tile's approach edge, its axis (model z = 0) through the tile centre, and the stair
# tiles' collision is a 45-degree plane (16 units a tile, 0 at the approach edge) so the player walks UP / DOWN the
# steps while the warp fades, instead of into them. Recipe furniture {"m": "stair_u01"/"stair_d01", "stair": [x, z]
# (Sapphire warp tile), "dir": "N"/"S"/"E"/"W" (the way the player walks into it, default N)}: position, rotation,
# the floor opening of stair_d01 and the planes come from that (placements, raster, collision).
STAIR_MODELS = {'stair_u01': ('up', 16.0), 'stair_d01': ('down', -16.0)}
import re as _re
MOUNTED = _re.compile(r'^(win|art|poster)\d')   # pieces hung on the wall (windows, pictures): bare_wall_tiles
STAIR_HOLE = (-16.0, 9.5, -14.5, 14.5)               # stair_d01's opening in model units (x0, x1, z0, z1): its shaft
DIRS = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
SLOPE_16 = {'N': 8, 'S': 14, 'E': 11, 'W': 16}       # MAP_HEIGHT_SLOPE_TABLE index of a plane rising 16/tile that way

def rot_pt(x, z, rot):
    """Model point (x, z) turned by a placement angle (as the game, rotate_box): (x c + z s, -x s + z c)."""
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    return x * c + z * s, -x * s + z * c

def stair_rot(kind, d):
    """Placement angle turning the model's walk-in direction (stair_u01: -x, up; stair_d01: +x, down) to DIRS[d]."""
    v = (-1, 0) if kind == 'up' else (1, 0)
    return next(r for r in (0, 90, 180, 270) if rot_pt(v[0], v[1], r) == DIRS[d])

def plane_cell(slope, cx, cy, cz):
    """Collision height fields (u16 a, u16 b) of a plane with MAP_HEIGHT_SLOPE_TABLE index `slope` through the
    chunk-centred point (cx, cy, cz) (b2tools/terrain/heights.py plane_record: overlay 36's tables)."""
    return heights().plane_record(slope, cx, cy, cz)

_heights = {}
def heights():
    """b2tools/terrain/heights.py (overlay 36's slope and offset tables), loaded once."""
    import importlib.util
    if not _heights:
        spec = importlib.util.spec_from_file_location('hoenn_heights', os.path.join(HERE, 'terrain', 'heights.py'))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); _heights['m'] = mod
    return _heights['m']

SAPPHIRE_TILE_TYPES = {0x80: 0xD4, 0xE5: 0xDF, 0x83: 0xD6}   # MB_COUNTER, MB_SHOP_SHELF, MB_PC -> Black 2 tile types
# Black 2 models resized to a Sapphire footprint (rooms_cleanup agent): name -> (Black 2 model, uniform scale, new res id).
# The copy is the Black 2 model byte for byte except its MDL0 position scale and box scale (NitroSystem draws every
# vertex times posScale: SBC POSSCALE), so it is Black 2's own art at another size. Res ids 300+ are free interior ids
# (Black 2's run 0..223, the truck door is 200; the field's res LUT has 512 entries). The room's built folder gets the
# .nsbmd (room.json models: file, base = the Black 2 res); patches/interiors.py installs it with the base's info record
# and the base pack's textures. table01 is 2.8 tiles wide (Black 2 gives it a 3x3 solid block); Sapphire's dining and
# round tables are 2x2 tiles, so table01_2x2 is table01 at 32/44.8 (2 tiles, 8.6 high: a low table, as Black 2's
# floor-cushion dining sets).
# The other copies: box02 (a stack of cardboard boxes, 1.6 x 1.9 tiles) on one tile, bed01 (1.56 tiles wide) on Sapphire's
# one-tile beds, table02 (2.66 tiles) on two-tile tables, pcdesk02 (3 tiles) on two-tile desks, Chargestone's electric
# floor d6_yuka_biri02 (1.5 tiles) on Mauville's one-tile barriers, shelf02 (a 2-tile glass cabinet) on one-tile cases,
# pc01 (1.4 tiles) in rows of one-tile machines (the Game Corner's slots), the Gym statue object02 (1.2 tiles) on its
# one tile, the bookshelf pcshelf01 (2.25 tiles) on Sapphire's two-tile bookshelves and shelf05 (1.25) on one tile,
# the TV tv01 (body 2.5 tiles) on a two-tile TV.
DERIVED_MODELS = {'table01_2x2': ('table01', 32 / 44.8, 300), 'box02_1': ('box02', 16 / 30.0, 301),
                  'bed01_1w': ('bed01', 0.72, 302), 'table02_2w': ('table02', 32 / 42.6, 303),
                  'pcdesk02_2': ('pcdesk02', 32 / 48.3, 304), 'd6_yuka_biri02_1': ('d6_yuka_biri02', 16 / 24.0, 305),
                  'shelf02_1': ('shelf02', 0.5, 306), 'pc01_1': ('pc01', 16 / 22.7, 307),
                  'object02_1': ('object02', 16 / 19.2, 308), 'pcshelf01_2': ('pcshelf01', 32 / 36.0, 309),
                  'shelf05_1': ('shelf05', 16 / 20.0, 310),
                  'tv01_2w': ('tv01', 32 / 40.0, 311),      # (sweep_rooms) Sapphire's 2-tile TV (the hideout's)
                  # (walkability 2026-10-11) Black 2's lab machine at FRONT_H high: a one-tile exhibit with people on
                  # the tiles in front of it (the Oceanic Museum's whirlpool experiment: a grunt's head was under it)
                  'machine01_s': ('machine01', 18 / 31.0, 318)}

def scaled_bmd(bmd, s):
    """A BMD0 with its model's posScale/invPosScale and box posScale/invPosScale multiplied by s / 1/s."""
    out = bytearray(bmd)
    nb = struct.unpack_from('<H', bmd, 0xE)[0]
    mdl = next(bo for bo in (struct.unpack_from('<I', bmd, 0x10 + 4 * k)[0] for k in range(nb)) if bmd[bo:bo + 4] == b'MDL0')
    for _, ent in nsbtx._dict(bmd, mdl + 8):
        info = mdl + struct.unpack_from('<I', ent, 0)[0] + 0x14
        for off, f in ((8, s), (12, 1 / s), (36, s), (40, 1 / s)):
            struct.pack_into('<i', out, info + off, round(struct.unpack_from('<i', bmd, info + off)[0] * f))
    return bytes(out)

# ------------------------------------------------------------------------------------------------ Black 2 models
_packs = {}
def interior_models():
    """{name: (res, pack, bmd)} and {res: (name, pack, bmd)} over all interior packs (first pack holding it)."""
    if not _packs:
        by_name, by_res = {}, {}
        for p in range(len(b2files.narc_entries(b2files.arc_path(FILES, 226)))):
            for r in b2files.building_pack(FILES, p, exterior=False):
                by_name.setdefault(r['name'], (r['res_id'], p, r['bmd']))
                by_res.setdefault(r['res_id'], (r['name'], p, r['bmd']))
        for name, (base, sc, res) in DERIVED_MODELS.items():
            _, pack, bmd = by_name[base]
            by_name[name] = (res, pack, scaled_bmd(bmd, sc)); by_res[res] = (name, pack, by_name[name][2])
        _packs['name'], _packs['res'] = by_name, by_res
    return _packs['name'], _packs['res']

def derived_by_res(res):
    """(base Black 2 res, scale) of a DERIVED_MODELS res id, else None."""
    for name, (base, sc, r) in DERIVED_MODELS.items():
        if r == res: return interior_models()[0][base][0], sc
    return None

def bmd_box(bmd):
    """Model bounding box (x0, x1, y0, y1, z0, z1) from the MDL0 model info (box test values * box scale)."""
    nb = struct.unpack_from('<H', bmd, 0xE)[0]
    mdl = next(bo for bo in (struct.unpack_from('<I', bmd, 0x10 + 4 * k)[0] for k in range(nb)) if bmd[bo:bo + 4] == b'MDL0')
    _, ent = nsbtx._dict(bmd, mdl + 8)[0]
    info = mdl + struct.unpack_from('<I', ent, 0)[0] + 0x14
    bx, by, bz, bw, bh, bd = struct.unpack_from('<6h', bmd, info + 24)
    s = struct.unpack_from('<i', bmd, info + 36)[0] / 4096 / 4096
    return bx * s, (bx + bw) * s, by * s, (by + bh) * s, bz * s, (bz + bd) * s

def rotate_box(box, rot):
    x0, x1, _, _, z0, z1 = box
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    pts = [(x * c + z * s, -x * s + z * c) for x in (x0, x1) for z in (z0, z1)]
    return min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)

# ------------------------------------------------------------------------------------------------ recipe
def load_recipe(name):
    r = json.load(open(os.path.join(LAYOUTS, name + '.json')))
    if 'decomp' in r: DECOMP_OF[r['map']] = r['decomp']   # a room of another decomp's map (frontier_pike 2026-10-12)
    if 'mirror_of' in r:
        base = load_recipe(r['mirror_of'])
        W = sapphire_map(r.get('map', base['map']))['w']
        m = mirror(base, W)
        m.update({k: v for k, v in r.items() if k != 'mirror_of'})
        r = m
    return r

def mirror(r, W):
    """Left-right mirror of a recipe for a map W tiles wide."""
    r = json.loads(json.dumps(r))
    tr = lambda q: [W - 1 - q[2], q[1], W - 1 - q[0], q[3]]          # inclusive tile rect
    ur = lambda q: [W - q[2], q[1], W - q[0], q[3]]                  # unit-precise rect in tile units
    r['floor'] = [tr(q) for q in r.get('floor', [])]
    r['floor_extra'] = [ur(q) for q in r.get('floor_extra', [])]
    r['holes'] = [ur(q) for q in r.get('holes', [])]
    for mt in r.get('mats', []): mt['rect'] = tr(mt['rect'])
    for f in r.get('furniture', []):
        if 'tile' in f: f['tile'] = [W - 1 - f['tile'][0], f['tile'][1]]
        if 'tiles' in f: f['tiles'] = tr(f['tiles'])
        if 'at' in f: f['at'] = [W - f['at'][0], f['at'][1]]
        if 'stair' in f: f['stair'] = [W - 1 - f['stair'][0], f['stair'][1]]
        if 'w_edge' in f or 'e_edge' in f:            # a footprint side on a tile line: west <-> east (rooms_cleanup:
            we, ee = f.pop('w_edge', None), f.pop('e_edge', None)    # May's 2F desk stood on her stairwell)
            if we is not None: f['e_edge'] = W - we
            if ee is not None: f['w_edge'] = W - ee
        if f.get('dir') in ('E', 'W'): f['dir'] = {'E': 'W', 'W': 'E'}[f['dir']]
        # a mirrored model can't be drawn, so turn it: front-facing furniture (left-right symmetric) turns -rot;
        # stairs (symmetric front-back, they rise along their own x) turn 180 - rot
        sym_z = 'stair' in str(f.get('m', ''))
        f['rot'] = f['mirror_rot'] if 'mirror_rot' in f else ((180 if sym_z else 360) - f.get('rot', 0)) % 360
        if f.get('wall') in ('W', 'E'): f['wall'] = {'W': 'E', 'E': 'W'}[f['wall']]
        if 'dx' in f: f['dx'] = -f['dx']
    for d in r.get('decals', []): d['at'] = [W - d['at'][0]] + d['at'][1:]
    for k in ('exits', 'stairs', 'block', 'unblock'):
        if k in r: r[k] = [[W - 1 - t[0], t[1]] for t in r[k]]
    if 'origin' in r: del r['origin']
    return r

_maps = {}
# recipe "decomp": the decomp folder in external/ whose map the room is (default pokeruby). Emerald-only rooms (the Battle
# Frontier's) read external/pokeemerald's map folder of that name (frontier_pike 2026-10-12); every older recipe has no
# such key, so it builds exactly as before
DECOMP_OF = {}
def map_source(name):
    """(decomp folder, map folder) of a recipe's "map": "<decomp>/<Folder>" names another decomp's map (Emerald's room
    variants: "pokeemerald/LittlerootTown_ProfessorBirchsLab", emerald_rooms 2026-10-12; the name, prefix included, is
    also room.json's "map", so the checkers read the same map); a plain name is pokeruby's (or the recipe's "decomp")."""
    if '/' in name: return tuple(name.split('/', 1))
    return DECOMP_OF.get(name, 'pokeruby'), name

def sapphire_map(name):
    """Size, walkable grid, metatile behaviours and warp events of a pokeruby map (or of the recipe's "decomp", or of
    the "<decomp>/<Folder>" map: map_source)."""
    if name not in _maps:
        from gba import Repo, MetatileRenderer
        dec, folder = map_source(name)
        repo = Repo(os.path.join(ROOT, 'external', dec))
        mj = repo.map_json(folder)
        g, l = repo.layout_grid(mj['layout'])
        mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
        H, W = g.shape
        walk = [[(int(g[z, x]) >> 10) & 3 == 0 for x in range(W)] for z in range(H)]
        beh = [[mr.behavior(int(g[z, x]) & 0x3FF) for x in range(W)] for z in range(H)]
        elev = [[(int(g[z, x]) >> 12) & 0xF for x in range(W)] for z in range(H)]
        _maps[name] = dict(w=W, h=H, walk=walk, beh=beh, elev=elev, warps=mj.get('warp_events', []),
                           objects=mj.get('object_events') or [])
    return _maps[name]

_lum = {}
def metatile_lum(name):
    """[z][x] mean brightness (0-255) of Sapphire's drawn metatile on each tile of a map (both layers; transparent
    pixels count as black, as the void around Sapphire's rooms)."""
    if name not in _lum:
        import numpy as np
        from gba import Repo, MetatileRenderer
        dec, folder = map_source(name)
        repo = Repo(os.path.join(ROOT, 'external', dec))
        mj = repo.map_json(folder)
        g, l = repo.layout_grid(mj['layout'])
        mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
        out = []
        for z in range(g.shape[0]):
            row = []
            for x in range(g.shape[1]):
                im = mr.render(int(g[z, x]) & 0x3FF).astype(np.float32)
                row.append(float((im[..., :3].mean(-1) * (im[..., 3] > 0)).mean()))
            out.append(row)
        _lum[name] = out
    return _lum[name]

def inner_wall_tiles(name, floor, max_thick=2, dark=100):
    """Sapphire tiles of a room's thin inner walls (recipe "inner_walls", sweep_rooms 2026-10-07): tiles with no floor
    that lie in a run of at most max_thick non-floor tiles with floor at both ends, north-south (a wall between two
    floors of one room: the Weather Institute's) or west-east (a partition: Dewford Hall's divider), and that Sapphire
    draws as a wall (its metatile brighter than `dark`; black void between separate rooms, like the Abandoned Ship's
    cabins, stays void). Also light islands of any size with only floor round them."""
    sm = sapphire_map(name); lum = metatile_lum(name)
    W, H = sm['w'], sm['h']
    def run_ok(x, z, dx, dz):
        a = b = 0
        while (x - dx * (a + 1), z - dz * (a + 1)) not in floor:
            a += 1
            if a >= max_thick or not (0 <= x - dx * (a + 1) < W and 0 <= z - dz * (a + 1) < H): return False
        while (x + dx * (b + 1), z + dz * (b + 1)) not in floor:
            b += 1
            if a + b + 1 > max_thick or not (0 <= x + dx * (b + 1) < W and 0 <= z + dz * (b + 1) < H): return False
        return a + b + 1 <= max_thick
    out = {(x, z) for z in range(H) for x in range(W) if (x, z) not in floor and lum[z][x] > dark
           and (run_ok(x, z, 0, 1) or run_ok(x, z, 1, 0))}
    # islands: light non-floor regions with floor all round them (not touching the map's edge), any size (the Abandoned
    # Ship's cabin blocks in the corridors, Sapphire draws their white tops)
    rest = {(x, z) for z in range(H) for x in range(W) if (x, z) not in floor and lum[z][x] > dark} - out
    while rest:
        st = [rest.pop()]; comp = set(st); edge = False; dark_nb = False
        while st:
            x, z = st.pop()
            if x in (0, W - 1) or z in (0, H - 1): edge = True
            for q in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if q in rest: rest.discard(q); comp.add(q); st.append(q)
                elif q not in floor and q not in comp and q not in out: dark_nb = True
        if not edge and not dark_nb: out |= comp
    return out

# ------------------------------------------------------------------------------------------------ geometry
class Room:
    def __init__(self, name):
        self.name = name
        self.r = r = load_recipe(name)
        self.sm = sm = sapphire_map(r['map'])
        self.styles = {}                    # _styles.json + one _styles_<group>.json per interiors agent (no shared edits)
        for f in sorted(glob.glob(os.path.join(LAYOUTS, '_styles*.json'))): self.styles.update(json.load(open(f)))
        self.style = self.styles[r['style']]
        self.W, self.H = sm['w'], sm['h']
        # warp spots: exit mats (genkan tile below each) and stairs/doors entered from the south
        inside = [w for w in sm['warps'] if 0 <= w['x'] < sm['w'] and 0 <= w['y'] < sm['h']]   # (some maps park warps outside)
        exits = r.get('exits') or [[w['x'], w['y']] for w in inside if sm['beh'][w['y']][w['x']] == MB_SOUTH_ARROW_WARP]
        stairs = r.get('stairs') or [[w['x'], w['y']] for w in inside if sm['beh'][w['y']][w['x']] == MB_NON_ANIMATED_DOOR]
        self.exits, self.stairs = [tuple(t) for t in exits], [tuple(t) for t in stairs]
        floor_tiles = set()
        for x0, z0, x1, z1 in r['floor']:
            floor_tiles |= {(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)}
        self.genkan = {(x, z + 1) for x, z in self.exits}
        # "inner_walls" (sweep_rooms 2026-10-07; opt-in): Sapphire's thin walls between two floors of one room (WI
        # partitions, hideout walls) become floor + a block with a light top (inner_wall_tiles), not walls with Black 2's
        # black cap (a black slab between the floors from the camera). Black 2's camera looks down at ~45 degrees, so a
        # block hides what stands up to its height behind it: tiles with a walkable tile less than "near" (3) tiles north
        # of them are "h_low" (16) high, so a player behind them stays in view (a 50-unit block hid the player in the
        # hidden floor's corridor, tested); the others (dividers off the back wall, the front of a cabin block) "h" (50)
        self.inner_tiles, self.inner_blocks = set(), []
        iw = r.get('inner_walls')
        if iw:
            self.inner_tiles = ({tuple(t) for t in iw['tiles']} if 'tiles' in iw else
                                inner_wall_tiles(r['map'], floor_tiles, iw.get('max', 2), iw.get('dark', 100)))
            self.inner_tiles -= {tuple(t) for t in iw.get('except', [])} | floor_tiles | self.genkan
            near = iw.get('near', 3)
            low = {(x, z) for x, z in self.inner_tiles
                   if any(0 <= z - k and sm['walk'][z - k][x] and (x, z - k) not in self.inner_tiles for k in range(1, near + 1))
                   # or diagonally north (a person beside its corner: a 50-unit block in front of them hid their head,
                   # indoor_check)
                   or any(0 <= z - 1 and 0 <= x + d < sm['w'] and sm['walk'][z - 1][x + d] and (x + d, z - 1) not in self.inner_tiles
                          for d in (-1, 1))}
            side = iw.get('side') or dict(self.style['wall'], v=self.style['wall'].get('v', [0, 1]))
            for tiles, h in ((self.inner_tiles - low, iw.get('h', YW - Y0)), (low, iw.get('h_low', 16))):
                if not tiles: continue
                v0, v1 = side.get('v') or [0, 1]                     # a low block shows the wall's lower part
                sd = dict(side) if h == YW - Y0 else dict(side, v=[v0, v0 + (v1 - v0) * h / (YW - Y0)])
                r['blocks'] = list(r.get('blocks', [])) + [dict(
                    tiles=sorted([list(t) for t in tiles]), h=h, top=iw['top'], side=sd,
                    shade_top=iw.get('shade_top', 1.0), shade_s=iw.get('shade_s', 0.8), shade_we=iw.get('shade_we', 0.55),
                    _what=f'inner walls (recipe "inner_walls"), {h} high')]
                self.inner_blocks.append(len(r['blocks']))           # its bgrid value (block index + 1)
        self.floor_tiles = floor_tiles | self.genkan | self.inner_tiles
        first = min(z for _, z in floor_tiles)
        self.ox, self.oz = r.get('origin', [1, 2 - first])
        # chunks: a room needs its tiles plus one tile of wall/lip around them (Black 2 rooms never touch the edge)
        need_w = (self.ox + max(x for x, _ in self.floor_tiles) + 2 + 31) // 32
        need_h = (self.oz + max(z for _, z in self.floor_tiles) + 2 + 31) // 32
        self.mw, self.mh = r.get('matrix', [max(1, need_w), max(1, need_h)])
        self.NX, self.NZ = 512 * self.mw, 512 * self.mh
        self.raster()
        self.bare = self.bare_wall_tiles()
        if self.bare:                         # (walkability 2026-10-11: see bare_wall_tiles)
            self.floor_tiles -= self.bare
            self.raster()

    def wall_row_front(self, cx, cz, f=None, box=None):
        """(walkability 2026-10-11) Local z where a piece against the back wall standing on Sapphire's lower wall row may
        bring its front: BACK (12) units north of the first walkable row south of it (the head rule FRONT_H, Black 2's
        own spacing), when bare_wall_tiles trims that room (else None). The piece stood back against the wall, its front
        up to a tile and more from the walkable row: the floor in front of it was bare and blocked (walk_diff OPEN)."""
        if not getattr(self, 'trim', False): return None
        x, z = int(math.floor(cx)), int(math.floor(cz))
        r, sm = self.r, self.sm
        unblocked = {tuple(t) for t in r.get('unblock', [])}; blocked = {tuple(t) for t in r.get('block', [])}
        for zz in (z, z + 1, z + 2):
            if 0 <= zz < self.H and 0 <= x < self.W and (sm['walk'][zz][x] or (x, zz) in unblocked) and (x, zz) not in blocked:
                if zz == z: return None
                front = self.lz(zz) - BACK
                if box is not None:                   # not into a person standing in front of it (a nurse at the
                    X0, X1, Z1 = box                   # healing machine, Mr. Sea at his drink machine) or a piece that
                                                       # does not stand against the wall (the Captain's ship-model stands)
                    cols = range(int(X0 // T) - self.ox - 1, int(-(-X1 // T)) - self.ox + 1)   # (and beside it)
                    if any(o['x'] in cols and z <= o['y'] <= zz for o in sm.get('objects', [])): return None
                    if any(i != id(f) and a0 < X1 and a1 > X0 and b1 > Z1 - 0.5 and b0 < front + 1
                           for i, a0, a1, b0, b1 in getattr(self, 'piece_boxes', [])): return None
                return front
        return None

    def bare_wall_tiles(self):
        """Sapphire draws its rooms' walls two tiles high: the back wall's lower row (row 1 in most rooms) and the side
        columns are solid wall tiles in front of which you stand. The recipes give those rows floor (furniture against
        the wall stands on them: its front 12 units from the walkable row, the head rule FRONT_H), so where nothing
        stands on them they were bare floor you could not step on, the wall a tile and more behind it: 'invisible walls'
        (b2tools/walk_diff.py OPEN: 993 such tiles in row 1 alone). Such a tile - solid in Sapphire, at the floor's back
        or side edge, the tile beyond it toward the room walkable, no furniture, block, person, warp or water on it - is
        no floor now: the wall stands where Black 2 stands it, 12 units (BACK) north of / 3 (SIDE) beside the walkable
        floor, and the collision stays Sapphire's. Recipe "wall_rows": "keep" turns this off (the Battle Tower rooms,
        pwt_tower's, keep theirs)."""
        r, sm = self.r, self.sm
        self.trim = not (r.get('wall_rows') == 'keep' or self.name.startswith('BattleTower_') or r.get('open'))
        self.piece_boxes = []                       # (id of the recipe piece, X0, X1, Z0, Z1) where it stood: wall_row_front
        self.walk_up = set()                        # Sapphire tiles of the lower wall row made walkable (option C, below)
        if not self.trim: return set()
        unblocked = {tuple(t) for t in r.get('unblock', [])}; blocked = {tuple(t) for t in r.get('block', [])}
        walk = lambda x, z: (0 <= z < self.H and 0 <= x < self.W and (sm['walk'][z][x] or (x, z) in unblocked)
                             and (x, z) not in blocked)
        keep = set(self.genkan) | set(self.inner_tiles) | set(self.exits) | set(self.stairs)
        keep |= {(w['x'], w['y']) for w in sm['warps']}
        keep |= {(o['x'], o['y']) for o in sm.get('objects', [])}
        for e in r.get('raised', []) + r.get('ramps', []):
            keep |= self.tile_set(e) if hasattr(self, 'tile_set') else set()
        keep |= self.water_draw_tiles() if r.get('water') else set()
        boxes = []                                  # (X0, X1, Z0, Z1) local units of what stands in the room
        for b in r.get('blocks', []):
            for X0, Z0, X1, Z1 in self.unit_rects(b):
                keep |= {(x, z) for x in range(int(X0 // T) - self.ox, int(-(-X1 // T)) - self.ox)
                         for z in range(int(Z0 // T) - self.oz, int(-(-Z1 // T)) - self.oz)}
                boxes.append((X0, X1, Z0, Z1))
        for d in r.get('decals', []):                # (a picture at a fixed z or on a block's face does not follow the wall)
            if 'z' in d or 'face_z' in d:
                cx = self.lx(d['at'][0]); boxes.append((cx - d['w'] / 2, cx + d['w'] / 2, -1e9, 1e9))
        cand = set()
        for x, z in self.floor_tiles:
            if (x, z) in keep or walk(x, z) or not (0 <= x < self.W and 0 <= z < self.H): continue
            if (x, z - 1) not in self.floor_tiles and (x, z + 1) in self.floor_tiles and walk(x, z + 1):
                cand.add((x, z))                                    # (a back tile: the room is south of it)
        # furniture where it stands now (as placements() puts it, before lift): a piece reaching into the tile keeps it
        by_name, by_res = interior_models()
        mounted = []
        for f in r.get('furniture', []):
            if 'res' in f: name = by_res[f['res']][0]; bmd = by_res[f['res']][2]
            else: name = f['m']; bmd = by_name[name][2]
            rot = f.get('rot', 0) % 360
            box = bmd_box(bmd)
            if box[3] - box[2] < 3.5 and not f.get('stair'): continue      # (flat: a rug's or shadow's height)
            mount = bool(MOUNTED.match(name)) and f.get('wall') == 'N'     # (hung on the wall: it goes with it)
            bx0, bx1, bz0, bz1 = rotate_box(box, rot)
            if 'at' in f: cx, cz = f['at']
            elif 'tiles' in f: cx, cz = (f['tiles'][0] + f['tiles'][2] + 1) / 2, (f['tiles'][1] + f['tiles'][3] + 1) / 2
            elif 'stair' in f: cx, cz = f['stair'][0] + 0.5, f['stair'][1] + 0.5
            else: cx, cz = f['tile'][0] + 0.5, f['tile'][1] + 0.5
            px = self.lx(cx) - (bx0 + bx1) / 2; pz = self.lz(cz) - (bz0 + bz1) / 2
            wall, gap = f.get('wall'), f.get('gap', 0)
            if wall == 'N': pz = self.wall_z(self.lx(cx), self.lz(cz)) + gap - bz0
            elif wall == 'W': px = self.wall_x(self.lx(cx), self.lz(cz), 'W') + gap - bx0
            elif wall == 'E': px = self.wall_x(self.lx(cx), self.lz(cz), 'E') - gap - bx1
            if 'w_edge' in f: px = self.lx(f['w_edge']) - bx0
            if 'e_edge' in f: px = self.lx(f['e_edge']) - bx1
            if 'n_edge' in f: pz = self.lz(f['n_edge']) - bz0
            if 's_edge' in f: pz = self.lz(f['s_edge']) - bz1
            px += f.get('dx', 0); pz += f.get('dz', 0)
            X0, X1, Z0, Z1 = px + bx0, px + bx1, pz + bz0, pz + bz1
            if 'stair' in f: X0, X1, Z0, Z1 = X0 - T, X1 + T, Z0 - T, Z1 + T       # (stairs: their recess too)
            if mount: mounted.append((X0 - 2, X1 + 2)); continue      # (2 more: no wall step right beside it)
            # (anything standing in front of the wall in the tile's column, the rows behind the tile too: moved forward,
            # the wall would hide it - Lavaridge Herb Shop's coolers stand in Sapphire's upper wall row)
            boxes.append((X0, X1, Z0, Z1))
            if wall != 'N': self.piece_boxes.append((id(f), X0, X1, Z0, Z1))   # (pieces against the wall move together)
        # (a piece reaching less than SIDE (3) units into a column does not keep it: the wall's step stands SIDE units
        # inside that column, beside the piece)
        cand = {(x, z) for x, z in cand if not any(X0 < self.lx(x + 1) - SIDE and X1 > self.lx(x) + SIDE and Z0 < self.lz(z + 1)
                                                   and Z1 > self.lz(z) - BACK + 0.5 for X0, X1, Z0, Z1 in boxes)}
        # whole back rows, runs from a room corner and runs of 3+ tiles between pieces: a shorter bare stretch between two
        # pieces brought forward stood out of the wall as a box (Sootopolis House3's window); a wall picture spans a run
        # or not
        def runs_of(tiles):
            out, by_z = [], {}
            for x, z in tiles: by_z.setdefault(z, []).append(x)
            for z, xs in by_z.items():
                xs = sorted(xs); a = xs[0]
                for i, x in enumerate(xs):
                    if i + 1 == len(xs) or xs[i + 1] != x + 1: out.append((z, a, x)); a = xs[i + 1] if i + 1 < len(xs) else a
            return out
        for _ in range(4):
            drop = set()
            for X0, X1 in mounted:
                cols = {x for x in range(self.W) if X0 < self.lx(x + 1) - 0.5 and X1 > self.lx(x) + 0.5}
                for z in {z for _, z in cand}:
                    hit = {x for x in cols if (x, z) in cand}
                    if hit and len(hit) < len(cols & {x for x in range(self.W) if (x, z) in self.floor_tiles}): drop |= {(x, z) for x in hit}
            back_rows = runs_of({(x, z) for x, z in self.floor_tiles if (x, z - 1) not in self.floor_tiles})
            for z, a, b in runs_of(cand - drop):
                seg = next(((sa, sb) for sz, sa, sb in back_rows if sz == z and sa <= a and b <= sb), None)
                if seg is None or (a != seg[0] and b != seg[1] and b - a + 1 < 3): drop |= {(x, z) for x in range(a, b + 1)}
            if not drop: break
            cand -= drop
        # (v165_fixes 2026-10-11, the user's option C) the back wall stays flat: a bare stretch trimmed BETWEEN two parts of
        # the back row that keep their wall line (pieces, a doorway; "bays": the wall stepped forward a tile at the window,
        # the pieces stood in recesses, 47 rooms, mostly houses: screenshots/sweep_rooms_v164/06_bay_*) keeps its floor
        # and Sapphire's solid lower wall row there becomes walkable (Room.collision, room.json "walk_up"): the player
        # walks right up to the window, one row more than Sapphire. Whole back rows and runs from a room corner stay
        # trimmed (the wall stays flat along the row / turns at the corner)
        back_rows = runs_of({(x, z) for x, z in self.floor_tiles if (x, z - 1) not in self.floor_tiles})
        for z, a, b in runs_of(cand) if cand else []:
            seg = next(((sa, sb) for sz, sa, sb in back_rows if sz == z and sa <= a and b <= sb), None)
            if seg is not None and a != seg[0] and b != seg[1]: self.walk_up |= {(x, z) for x in range(a, b + 1)}
        return cand - self.walk_up

    # Sapphire tile units <-> local units (local = chunk units from the chunk's top-left corner)
    def lx(self, tx): return (self.ox + tx) * T
    def lz(self, tz): return (self.oz + tz) * T

    def raster(self):
        """Floor as a 512x512 grid of unit cells: 0 none, 1 floor, 2 genkan, with a shade per cell."""
        import numpy as np
        kind = np.zeros((self.NZ, self.NX), np.uint8)    # [z, x]; one chunk = 512 x 512 (more for big rooms)
        shade = np.ones((self.NZ, self.NX), np.float32)
        ft = self.floor_tiles
        for (x, z) in sorted(ft):
            g = (x, z) in self.genkan
            X0, X1, Z0, Z1 = self.lx(x), self.lx(x + 1), self.lz(z), self.lz(z + 1)
            kind[Z0:Z1, X0:X1] = 2 if g else 1
            if g: continue
            n, w, e = (x, z - 1) not in ft, (x - 1, z) not in ft, (x + 1, z) not in ft
            if n:
                kind[Z0 - BACK:Z0, X0:X1] = 1; shade[Z0 - BACK:Z0 + 4, X0:X1] = SHADE_FLOOR_BACK
            if w:
                kind[Z0:Z1, X0 - SIDE:X0] = 1; shade[Z0:Z1, X0 - SIDE:X0 + 12] = np.minimum(shade[Z0:Z1, X0 - SIDE:X0 + 12], SHADE_FLOOR_SIDE)
            if e:
                kind[Z0:Z1, X1:X1 + SIDE] = 1
            if n and w:
                kind[Z0 - BACK:Z0, X0 - SIDE:X0] = 1; shade[Z0 - BACK:Z0, X0 - SIDE:X0] = SHADE_FLOOR_BACK
            if n and e:
                kind[Z0 - BACK:Z0, X1:X1 + SIDE] = 1; shade[Z0 - BACK:Z0, X1:X1 + SIDE] = SHADE_FLOOR_BACK
        for x0, z0, x1, z1 in self.r.get('floor_extra', []):
            kind[round(self.lz(z0)):round(self.lz(z1)), round(self.lx(x0)):round(self.lx(x1))] = 1
        # a "stair" piece stands in a recess of the room as big as the model (+1 unit): the walls go round it, so no
        # wall cuts through the steps (a wall through the top riser flickered) and stair_d01's shaft is all inside
        for f in self.r.get('furniture', []):
            if 'stair' in f and f.get('m') in STAIR_MODELS:
                rot, px, pz = self.stair_place(f)
                bx0, bx1, bz0, bz1 = rotate_box(bmd_box(interior_models()[0][f['m']][2]), rot)
                X0, X1 = max(int(math.floor(px + bx0)) - 1, 0), int(math.ceil(px + bx1)) + 1
                Z0, Z1 = max(int(math.floor(pz + bz0)) - 1, 0), int(math.ceil(pz + bz1)) + 1
                sub = kind[Z0:Z1, X0:X1]; sub[sub == 0] = 1
        self.holes = []
        holes = [(x0, z0, x1, z1) for x0, z0, x1, z1 in self.r.get('holes', [])]
        for f in self.r.get('furniture', []):                   # the opening of a stair_d01 placed by "stair"
            if 'stair' in f and STAIR_MODELS.get(f.get('m'), ('',))[0] == 'down':
                rot, px, pz = self.stair_place(f)
                a0, a1, b0, b1 = STAIR_HOLE
                pts = [rot_pt(x, z, rot) for x in (a0, a1) for z in (b0, b1)]
                holes.append(tuple(v / T for v in (px + min(p[0] for p in pts) - self.ox * T, pz + min(p[1] for p in pts) - self.oz * T,
                                                   px + max(p[0] for p in pts) - self.ox * T, pz + max(p[1] for p in pts) - self.oz * T)))
        for x0, z0, x1, z1 in holes:
            Z0, Z1, X0, X1 = round(self.lz(z0)), round(self.lz(z1)), round(self.lx(x0)), round(self.lx(x1))
            Z0 = max(Z0, int(np.argmax(kind[:, (X0 + X1) // 2] > 0)))          # only inside the room
            kind[Z0:Z1, X0:X1] = 3
            self.holes.append((X0, Z0, X1, Z1))
        # "water" (ship_hideouts agent): surf water tiles are openings in the floor like holes (no floor, no walls
        # round them); water() draws the water below the floor and its banks
        for x, z in sorted(self.water_draw_tiles() if (self.r.get('water') or {}).get('draw') is not False else ()):
            kind[self.lz(z):self.lz(z + 1), self.lx(x):self.lx(x + 1)] = 3      # ("draw": false: the floor stays)
        # floor texture regions (fmat: 0 = the style's floor, i + 1 = floor_tex[i]) and raised blocks (kind 4)
        fmat = np.zeros_like(kind, dtype=np.int16)
        for i, ft in enumerate(self.r.get('floor_tex', [])):
            X0, Z0, X1, Z1 = self.unit_rect(ft)
            sub = fmat[Z0:Z1, X0:X1]; sub[kind[Z0:Z1, X0:X1] == 1] = i + 1
        bgrid = np.zeros_like(kind, dtype=np.int16)
        for i, b in enumerate(self.r.get('blocks', [])):
            for X0, Z0, X1, Z1 in self.unit_rects(b):
                sub = bgrid[Z0:Z1, X0:X1]; sub[kind[Z0:Z1, X0:X1] > 0] = i + 1
        # "inner_walls": the block stands where Black 2 stands a wall: 12 units (BACK) north of the floor south of it and
        # 3 units (SIDE) off the floor beside it, so doors and furniture against it stay where the wall had them
        self.inner_mask = np.zeros(kind.shape, bool)          # the inner walls' block cells: furniture/decals stop there
        if self.inner_tiles:
            flo = self.floor_tiles - self.inner_tiles
            for x, z in self.inner_tiles:
                X0, X1, Z0, Z1 = self.lx(x), self.lx(x + 1), self.lz(z), self.lz(z + 1)
                cut = []
                if (x, z + 1) in flo: cut.append((Z1 - BACK, Z1, X0, X1))
                if (x - 1, z) in flo: cut.append((Z0, Z1, X0, X0 + SIDE))
                if (x + 1, z) in flo: cut.append((Z0, Z1, X1 - SIDE, X1))
                for a0, a1, b0, b1 in cut:
                    sub = bgrid[a0:a1, b0:b1]; sel = np.isin(sub, self.inner_blocks); sub[sel] = 0
                    kind[a0:a1, b0:b1][sel] = 1
            self.inner_mask = np.isin(bgrid, self.inner_blocks)
        # tall blocks (> FRONT_H) stand back BACK (12) units from a walkable floor tile south of them, as Black 2's walls
        # do: a person's camera-facing sprite leans back from their feet (at 18+ units a block reaching the tile edge
        # was drawn across the head of anyone standing south of it: Rustboro Flat2's dividers, the shipyard's planks;
        # indoor_check 2026-10-08, rooms_view.py kind m). Not under raised levels (their tops are walked on), not thin
        # "units" pieces (girders, poles), not inner walls (cut above); block "setback": false keeps the edge.
        raised = {tuple(t) for e in self.r.get('raised', []) for t in
                  (e['tiles'] if 'tiles' in e else [(x, z) for x in range(e['rect'][0], e['rect'][2] + 1)
                                                    for z in range(e['rect'][1], e['rect'][3] + 1)])}
        blocked = {tuple(t) for t in self.r.get('block', [])}; unblocked = {tuple(t) for t in self.r.get('unblock', [])}
        walk = lambda x, z: (0 <= z < self.H and 0 <= x < self.W and (self.sm['walk'][z][x] or (x, z) in unblocked)
                             and (x, z) not in blocked)
        # (sweep_rooms 2026-10-11) a raised level's edge tile nobody stands on (Sapphire solid, or a door's warp tile in
        # it) above a walkable tile of a level more than FRONT_H lower stands back too: the Abandoned Ship's deckhouse
        # front (32 above the lower deck) and bridge (52 above the upper deck) cut the player's body/head along the
        # decks (rooms_view m up to 177 px). The strip in front belongs to the level below (its block).
        raised_y = {tuple(t): e['y'] for e in self.r.get('raised', []) for t in
                    (e['tiles'] if 'tiles' in e else [(x, z) for x in range(e['rect'][0], e['rect'][2] + 1)
                                                      for z in range(e['rect'][1], e['rect'][3] + 1)])}
        warp_tiles = {(w['x'], w['y']) for w in self.sm['warps']}
        for i, b in enumerate(self.r.get('blocks', [])):
            if i + 1 in self.inner_blocks or 'units' in b or b.get('setback') is False: continue
            if self.block_style(b).get('h', 16) <= FRONT_H: continue
            tiles = ([tuple(t) for t in b['tiles']] if 'tiles' in b and b['tiles'] and isinstance(b['tiles'][0], (list, tuple))
                     else [(x, z) for x in range(b['rect'][0], b['rect'][2] + 1) for z in range(b['rect'][1], b['rect'][3] + 1)])
            edge = {}                                        # raised edges: (x, z) -> (lower block, someone below)
            for x, z in tiles:
                s = (x, z + 1)
                if (x, z) in raised or s in raised:
                    if (walk(x, z) and (x, z) not in warp_tiles) or s not in self.floor_tiles: continue
                    below = int(bgrid[self.lz(z + 1) + 1, self.lx(x) + 1])      # the lower level's block (0: the floor)
                    top = raised_y[(x, z)] if (x, z) in raised else self.block_style(b).get('h', 16)
                    low = raised_y[s] if s in raised else (self.block_style(self.r['blocks'][below - 1]).get('h', 16) if below else Y0)
                    if top - low > FRONT_H: edge[(x, z)] = (below, walk(*s))
                    continue
                if walk(x, z) or not walk(*s) or s in raised: continue
                if s not in self.floor_tiles: continue
                X0, X1, Z1 = self.lx(x), self.lx(x + 1), self.lz(z + 1)
                sub = bgrid[Z1 - BACK:Z1, X0:X1]; sel = sub == i + 1
                sub[sel] = 0; kind[Z1 - BACK:Z1, X0:X1][sel] = 1
            # a whole run of such an edge stands back when someone walks below any of it (the front stays one line over
            # the lower level's solid tiles and holes; the hull over the sea, where nobody stands, keeps its edge)
            for x, z in edge:
                run, k = [], x
                while (k - 1, z) in edge: k -= 1
                while (k, z) in edge: run.append(k); k += 1
                if not any(edge[(q, z)][1] for q in run): continue
                below = edge[(x, z)][0]
                X0, X1, Z1 = self.lx(x), self.lx(x + 1), self.lz(z + 1)
                sub = bgrid[Z1 - BACK:Z1, X0:X1]; sel = sub == i + 1
                sub[sel] = below
                if not below: kind[Z1 - BACK:Z1, X0:X1][sel] = 1
        kind[bgrid > 0] = 4
        self.kind, self.shade, self.fmat, self.bgrid = kind, shade, fmat, bgrid

    def unit_rects(self, e):
        """Local unit rects (X0, Z0, X1, Z1) of a recipe entry with rect (tiles, inclusive) / units (tile units) / tiles."""
        if 'tiles' in e and e['tiles'] and isinstance(e['tiles'][0], (list, tuple)):
            return [(self.lx(x), self.lz(z), self.lx(x + 1), self.lz(z + 1)) for x, z in e['tiles']]
        return [self.unit_rect(e)]

    def unit_rect(self, e):
        if 'units' in e:
            x0, z0, x1, z1 = e['units']
            return round(self.lx(x0)), round(self.lz(z0)), round(self.lx(x1)), round(self.lz(z1))
        x0, z0, x1, z1 = e['rect']
        return self.lx(x0), self.lz(z0), self.lx(x1 + 1), self.lz(z1 + 1)

    def rects(self, mask, values):
        """Greedy decomposition of mask cells into rectangles of equal value: [(x0, z0, x1, z1, value)]."""
        import numpy as np
        out = []
        NZ, NX = mask.shape
        used = np.zeros_like(mask, dtype=bool)
        zs, xs = np.nonzero(mask)
        for z in range(zs.min(), zs.max() + 1) if len(zs) else []:
            x = 0
            row = mask[z] & ~used[z]
            while x < NX:
                if not row[x]: x += 1; continue
                v = values[z, x]
                x1 = x
                while x1 < NX and row[x1] and values[z, x1] == v: x1 += 1
                z1 = z + 1
                while z1 < NZ and mask[z1, x:x1].all() and not used[z1, x:x1].any() and (values[z1, x:x1] == v).all(): z1 += 1
                used[z:z1, x:x1] = True
                out.append((x, z, x1, z1, float(v)))
                x = x1
        return out

    def edges(self, inside):
        """Boundary segments of a boolean cell mask: {'N': [(z, x0, x1)], 'S': [...], 'W': [(x, z0, z1)], 'E': [...]}.
        N = edge with the region to its south (a back wall), S = region to its north (the open front)."""
        import numpy as np
        out = {'N': [], 'S': [], 'W': [], 'E': []}
        pad = np.pad(inside, 1)
        for key, a, b in (('N', pad[1:-1, 1:-1], pad[:-2, 1:-1]), ('S', pad[1:-1, 1:-1], pad[2:, 1:-1])):
            m = a & ~b
            for z in range(m.shape[0]):
                xs = np.nonzero(m[z])[0]
                if not len(xs): continue
                start = prev = xs[0]
                for x in list(xs[1:]) + [None]:
                    if x is not None and x == prev + 1: prev = x; continue
                    out[key].append((z + (key == 'S'), int(start), int(prev) + 1))
                    if x is not None: start = prev = x
        for key, a, b in (('W', pad[1:-1, 1:-1], pad[1:-1, :-2]), ('E', pad[1:-1, 1:-1], pad[1:-1, 2:])):
            m = (a & ~b).T
            for x in range(m.shape[0]):
                zs = np.nonzero(m[x])[0]
                if not len(zs): continue
                start = prev = zs[0]
                for z in list(zs[1:]) + [None]:
                    if z is not None and z == prev + 1: prev = z; continue
                    out[key].append((x + (key == 'E'), int(start), int(prev) + 1))
                    if z is not None: start = prev = z
        return out

    def build_terrain(self):
        import numpy as np
        st = self.style
        m = Model(self.name)
        C = lambda v: (v - 256)                       # local units -> chunk-centred model units
        mat = lambda k: st[k]['tex']
        black = mat('black')
        # floor and genkan
        fl, gk = self.kind == 1, self.kind == 2
        fs = st['floor'].get('size', 32)
        fts = self.r.get('floor_tex', [])
        key = self.fmat.astype(np.float32) * 4 + self.shade            # shade < 4: one rect = one material + shade
        for x0, z0, x1, z1, k in self.rects(fl, key):
            fi = int(k // 4); s = k - fi * 4
            col = (s, s, s)
            if fi == 0:
                self.floor_quad(m, mat('floor'), [(C(x0), Y0, C(z1), x0 / fs, -z1 / fs, col), (C(x1), Y0, C(z1), x1 / fs, -z1 / fs, col),
                                                  (C(x1), Y0, C(z0), x1 / fs, -z0 / fs, col), (C(x0), Y0, C(z0), x0 / fs, -z0 / fs, col)])
            else:
                self.tex_quad_flat(m, fts[fi - 1], x0, z0, x1, z1, Y0, col)
        gs = st['genkan'].get('size', 16)
        for x0, z0, x1, z1, _ in self.rects(gk, self.kind):
            # fades to black toward the open south edge, like Black 2's entrances; "stretch": one texture per notch
            top, bot = (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)
            if st['genkan'].get('stretch'): u = lambda x: (x - x0) / (x1 - x0); v = lambda z: (z1 - z) / (z1 - z0)
            else: u = lambda x: x / gs; v = lambda z: -z / gs
            self.floor_quad(m, mat('genkan'), [(C(x0), Y0, C(z1), u(x0), v(z1), bot), (C(x1), Y0, C(z1), u(x1), v(z1), bot),
                                               (C(x1), Y0, C(z0), u(x1), v(z0), top), (C(x0), Y0, C(z0), u(x0), v(z0), top)])
        # walls (around floor + genkan; the genkan's sides are only lips)
        room = self.kind > 0                                  # floor, genkan and holes (no walls around a hole)
        e = self.edges(room)
        wall_u = st['wall'].get('u_size', 64)
        v0, v1 = st['wall'].get('v', [0, 1])
        lo, hi = SHADE_BACK_WALL
        def is_genkan_cell(x, z): return 0 <= x < self.NX and 0 <= z < self.NZ and self.kind[z, x] == 2
        # "open": outside tiles where the room has no wall (it floats in the black void there, as Black 2's League
        # walkways do): the floor's edge gets only a black lip
        opn = np.zeros(self.kind.shape, bool)
        if self.r.get('open') is True: opn[:] = True                  # no walls at all
        for t in (self.r.get('open') if isinstance(self.r.get('open'), list) else []):
            X0, Z0, X1, Z1 = self.unit_rect({'rect': t} if len(t) == 4 and all(isinstance(v, int) for v in t) else {'units': t})
            opn[max(Z0, 0):Z1, max(X0, 0):X1] = True
        def runs(flags, a0):
            """[(start, end, flag)] runs of equal flags, offset by a0."""
            out, k = [], 0
            while k < len(flags):
                j = k
                while j < len(flags) and flags[j] == flags[k]: j += 1
                out.append((a0 + k, a0 + j, bool(flags[k]))); k = j
            return out
        holes = self.doorway_spans()
        for z, xa, xb in e['N']:
            for x0, x1, is_open in runs(opn[z - 1, xa:xb] if z > 0 else np.zeros(xb - xa, bool), xa):
                if is_open: continue
                cb, ct = (lo,) * 3, (hi,) * 3
                pieces = [(x0, x1)]                           # the wall, less the doorways cut into it
                for hz, h0, h1 in holes:
                    if hz != z: continue
                    pieces = [q for a, b in pieces for q in (((a, b),) if h1 <= a or h0 >= b else ((a, h0), (h1, b)))
                              if q[1] - q[0] > 0]
                for a, b in pieces:
                    m.quad(mat('wall'), [(C(a), Y0, C(z), a / wall_u, v0, cb), (C(b), Y0, C(z), b / wall_u, v0, cb),
                                         (C(b), YW, C(z), b / wall_u, v1, ct), (C(a), YW, C(z), a / wall_u, v1, ct)])
                self.cap(m, black, C(x0), C(z) - CAP, C(x1), C(z))
        DD, DW = 2 * CAP, 8                                   # doorway recess: depth, extra width each side behind the wall
        for hz, h0, h1 in holes:                              # the doorway: a black recess behind the cut, roofed in black
            zb, zf = C(hz) - DD, C(hz)
            a0, a1 = C(h0) - DW, C(h1) + DW                   # the recess is wider than the cut: the swung halves stay inside
            blk = lambda pts: m.quad(black, [p + (0, 0) for p in pts], color=(0, 0, 0))
            blk([(a0, Y0, zb), (a1, Y0, zb), (a1, YW, zb), (a0, YW, zb)])                   # back
            zs = zf - 2                                       # the sides start behind the wall face (no line at it)
            blk([(a0, Y0, zs), (a0, Y0, zb), (a0, YW, zb), (a0, YW, zs)])                   # west side, facing east
            blk([(a1, Y0, zb), (a1, Y0, zs), (a1, YW, zs), (a1, YW, zb)])                   # east side, facing west
            blk([(C(h0), Y0, zf), (C(h1), Y0, zf), (C(h1), Y0, zs), (C(h0), Y0, zs)])       # floor in the cut
            blk([(a0, Y0, zs), (a1, Y0, zs), (a1, Y0, zb), (a0, Y0, zb)])                   # floor behind the wall
            blk([(a0, YW, zs), (a1, YW, zs), (a1, YW, zb), (a0, YW, zb)])                   # roof (the wall's cap covers the front)
            blk([(C(h0), Y0, zf), (C(h0), Y0, zs), (C(h0), YW, zs), (C(h0), YW, zf)])       # the cut's jambs, facing
            blk([(C(h1), Y0, zs), (C(h1), Y0, zf), (C(h1), YW, zf), (C(h1), YW, zs)])       # into the cut
            blk([(C(h0) - 2, YW, zf), (C(h1) + 2, YW, zf), (C(h1) + 2, YW + 32, zf), (C(h0) - 2, YW + 32, zf)])  # lintel
            # (over the black void: Black 2's wall goes on 32 above its door)
        segs = {'W': [], 'E': []}
        for key in ('W', 'E'):
            for x, za, zb in e[key]:
                ox_ = x - 1 if key == 'W' else x
                flags = opn[za:zb, ox_] if 0 <= ox_ < self.NX else np.zeros(zb - za, bool)
                for z0, z1, is_open in runs(flags, za):
                    if is_open:                                  # open side: black lip facing out of the room
                        self.lip_x(m, black, C(x), C(z0), C(z1), 'E' if key == 'W' else 'W')
                    else:
                        segs[key].append((x, z0, z1))
        for key in ('W', 'E'):
            for x, z0, z1 in segs[key]:
                cell_x = x if key == 'W' else x - 1
                if is_genkan_cell(cell_x, z0):                   # genkan side: a lip only
                    self.lip_x(m, black, C(x), C(z0), C(z1), key)
                    continue
                c = (SHADE_SIDE_WALL,) * 3
                xo = C(x) - CAP if key == 'W' else C(x) + CAP
                # a side wall that starts beside a walkable tile one row north (the floor narrows going south: Sapphire's
                # cabins, gym and hideout jogs) stands in front of a person on that tile, and its 50 units hid their head
                # from Black 2's camera: its first tile is CORNER_H high, as the low inner walls (indoor_check)
                zl = min(z0 + T, z1) if self.corner_low(key, x, z0) else z0
                for za, zb, yt in ((z0, zl, Y0 + CORNER_H), (zl, z1, YW)):
                    if zb <= za: continue
                    a, b = (zb, za) if key == 'W' else (za, zb)  # wall faces into the room
                    vt = v0 + (v1 - v0) * (yt - Y0) / (YW - Y0)
                    m.quad(mat('wall'), [(C(x), Y0, C(a), a / wall_u, v0, c), (C(x), Y0, C(b), b / wall_u, v0, c),
                                         (C(x), yt, C(b), b / wall_u, vt, c), (C(x), yt, C(a), a / wall_u, vt, c)])
                    m_cap_z0 = C(za) - (CAP if za == z0 and self.continues_north(x, z0, key) else 0)
                    if yt == YW: self.cap(m, black, min(xo, C(x)), m_cap_z0, max(xo, C(x)), C(zb))
                    else: m.quad(black, [(min(xo, C(x)), yt, C(zb), 0, 0), (max(xo, C(x)), yt, C(zb), 1, 0),
                                         (max(xo, C(x)), yt, m_cap_z0, 1, 1), (min(xo, C(x)), yt, m_cap_z0, 0, 1)], color=(0, 0, 0))
                # cut end of the wall where the floor ends in front (open south side)
                if not room[min(z1, self.NZ - 1), cell_x] if 0 <= cell_x < self.NX else True:
                    ye = YW if zl < z1 else Y0 + CORNER_H
                    m.quad(black, [(min(xo, C(x)), YLIP, C(z1), 0, 0), (max(xo, C(x)), YLIP, C(z1), 1, 0),
                                   (max(xo, C(x)), ye, C(z1), 1, 1), (min(xo, C(x)), ye, C(z1), 0, 1)], color=(0, 0, 0))
        for z, x0, x1 in e['S']:
            m.quad(black, [(C(x0), YLIP, C(z), 0, 0), (C(x1), YLIP, C(z), 1, 0), (C(x1), Y0, C(z), 1, 1), (C(x0), Y0, C(z), 0, 1)],
                   color=(0, 0, 0))
        # holes (stair_d01 openings): just no floor; the stair model brings its own shaft
        # rugs: 9-slice quads >= LAYER above the floor / the rugs and block tops under them (rug_heights)
        for mt, y in zip(self.r.get('mats', []), self.rug_heights()):
            self.rug(m, dict(mt, y=y))
        for d, gap in zip(self.r.get('decals', []), self.decal_gaps()):
            self.decal(m, dict(d, gap=gap))
        for i, b in enumerate(self.r.get('blocks', [])):
            self.block(m, i, b)
        for rp in self.r.get('ramps', []):                    # ship_hideouts agent: sloped floors between levels
            self.ramp(m, rp)
        if self.r.get('water'):
            self.water(m)
        self.model = m
        return m

    # ---- levels, ramps, water (ship_hideouts agent, 2026-10-06; recipe keys "raised", "ramps", "water") -----------
    # "raised": [{"rect"|"tiles": ..., "y": units}]: the walkable tiles there stand at collision height y (a flat plane,
    #   heights.py flat_index; the room's floor is at collision 0). The look is the recipe's: usually a "blocks" box of
    #   h = y under them (floor drawn 2 below its collision, as Black 2's rooms: block top Y0 + h = y - 2).
    # "ramps": [{"rect": [x0, z0, x1, z1] (tiles, inclusive), "rise": "N"|"S"|"E"|"W" (the way it climbs), "y0": collision
    #   height at its low edge, "tex": {tex, src, size (units per u repeat across), size_v (units per v repeat along)},
    #   "side": {tex, src, u_size}}]: 16 units of rise per tile (45 degrees, MAP_HEIGHT_SLOPE_TABLE 8/14/11/16 as the
    #   stair tiles), its walkable tiles get the slope's collision plane; drawn as one sloped quad (2 below the plane)
    #   with its two side faces down to the floor.
    # "water": {"tiles": [[x, z], ...] | "rect": [...] (default: every Sapphire surf-water tile), "tex": {tex, src, size},
    #   "bank": {tex, src, u_size}, "y": collision height (default -8), "solid": tiles drawn as water whose collision
    #   stays solid (water Sapphire blocks)}: Black 2's water cells (Wellspring Cave 486/487:
    #   class 0x3f, flags 0x16 with wild encounters / 0x12 without, 8 units below the shore; models_cave.py's tested
    #   values), an opaque water quad at that height and banks from it up to the floor on every edge to a non-water tile.
    #   (dive agent) "cell": [class, flags] replaces the water cell (Underwater rooms: [0x9C, 2], the Abyssal Ruins' swimmable
    #   cells, with "y": 0), "draw": false draws no water (the room's floor stays).
    SURF = {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x19, 0x22, 0x2A, 0x50, 0x51, 0x52, 0x53, 0x6C, 0x6D, 0x6F}
    SURF_ENC = {0x10, 0x11, 0x12, 0x15, 0x22, 0x2A}

    def water_tiles(self):
        """Sapphire tiles (x, z) of the recipe's "water" (none without the key)."""
        w = self.r.get('water')
        if not w: return set()
        if w.get('tiles'): return {tuple(t) for t in w['tiles']}
        if w.get('rect'):
            x0, z0, x1, z1 = w['rect']
            return {(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)}
        sm = self.sm
        return {(x, z) for z in range(self.H) for x in range(self.W) if sm['walk'][z][x] and sm['beh'][z][x] in self.SURF}

    def water_draw_tiles(self):
        """Tiles drawn as water: the surf tiles plus "water": {"solid": [[x, z], ...]} (water Sapphire blocks: drawn,
        collision stays solid)."""
        w = self.r.get('water') or {}
        return self.water_tiles() | {tuple(t) for t in w.get('solid', [])}

    def tile_set(self, e):
        """Sapphire tiles of a recipe entry with "rect" (inclusive) or "tiles"."""
        if 'tiles' in e: return {tuple(t) for t in e['tiles']}
        x0, z0, x1, z1 = e['rect']
        return {(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)}

    def ramp_geom(self, rp):
        """(tiles, rise dir, n tiles along the climb, low-edge index function) of a ramp entry."""
        x0, z0, x1, z1 = rp['rect']
        d = rp['rise']
        n = (z1 - z0 + 1) if d in 'NS' else (x1 - x0 + 1)
        k = {'N': lambda x, z: z1 - z, 'S': lambda x, z: z - z0, 'E': lambda x, z: x - x0, 'W': lambda x, z: x1 - x}[d]
        return self.tile_set(rp), d, n, k

    def ramp(self, m, rp):
        C = lambda v: v - 256
        x0, z0, x1, z1 = rp['rect']
        _, d, n, _ = self.ramp_geom(rp)
        X0, X1, Z0, Z1 = self.lx(x0), self.lx(x1 + 1), self.lz(z0), self.lz(z1 + 1)
        lo, hi = rp['y0'] - 2, rp['y0'] + 16 * n - 2
        # corner heights: (x, z) -> y
        hy = {'N': lambda X, Z: lo + (hi - lo) * (Z1 - Z) / (Z1 - Z0), 'S': lambda X, Z: lo + (hi - lo) * (Z - Z0) / (Z1 - Z0),
              'E': lambda X, Z: lo + (hi - lo) * (X - X0) / (X1 - X0), 'W': lambda X, Z: lo + (hi - lo) * (X1 - X) / (X1 - X0)}[d]
        t = rp['tex']; su = t.get('size', 32); sv = t.get('size_v', 16)
        def uv(X, Z):              # u across the climb, v along it (one v repeat per size_v units of climb)
            if d in 'NS': return X / su, ((Z1 - Z) if d == 'N' else (Z - Z0)) / sv
            return Z / su, ((X - X0) if d == 'E' else (X1 - X)) / sv
        pts = [(X0, Z1), (X1, Z1), (X1, Z0), (X0, Z0)]
        m.quad(t['tex'], [(C(X), hy(X, Z), C(Z)) + uv(X, Z) for X, Z in pts])
        s = rp.get('side')
        if not s: return
        us = s.get('u_size', 32); c = (rp.get('shade_side', 0.55),) * 3
        if d in 'NS':              # the west and east faces (trapezoids from the floor up to the slope)
            for X, face in ((X0, 'W'), (X1, 'E')):
                a, b = (Z0, Z1) if face == 'W' else (Z1, Z0)
                m.quad(s['tex'], [(C(X), Y0, C(a), a / us, 0, c), (C(X), Y0, C(b), b / us, 0, c),
                                  (C(X), hy(X, b), C(b), b / us, (hy(X, b) - Y0) / us, c),
                                  (C(X), hy(X, a), C(a), a / us, (hy(X, a) - Y0) / us, c)])
        else:                      # the south face (the camera never sees the north one)
            m.quad(s['tex'], [(C(X0), Y0, C(Z1), X0 / us, 0, c), (C(X1), Y0, C(Z1), X1 / us, 0, c),
                              (C(X1), hy(X1, Z1), C(Z1), X1 / us, (hy(X1, Z1) - Y0) / us, c),
                              (C(X0), hy(X0, Z1), C(Z1), X0 / us, (hy(X0, Z1) - Y0) / us, c)])

    def water(self, m):
        C = lambda v: v - 256
        w = self.r['water']
        if w.get('draw') is False: return                # (dive agent) collision only: an underwater room
        y = w.get('y', -8)
        tiles = self.water_draw_tiles()
        t = w['tex']; sz = t.get('size', 64)
        for x0, z0, x1, z1, _ in self.rects_of(tiles):
            X0, X1, Z0, Z1 = self.lx(x0) - 4, self.lx(x1 + 1) + 4, self.lz(z0) - 4, self.lz(z1 + 1) + 4
            m.quad(t['tex'], [(C(X0), y, C(Z1), X0 / sz, -Z1 / sz), (C(X1), y, C(Z1), X1 / sz, -Z1 / sz),
                              (C(X1), y, C(Z0), X1 / sz, -Z0 / sz), (C(X0), y, C(Z0), X0 / sz, -Z0 / sz)])
        b = w.get('bank')
        if not b: return
        us = b.get('u_size', 16)
        for x, z in sorted(tiles):
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, z + dz) in tiles: continue
                if dx: X = self.lx(x + (dx > 0)); a, b_ = (self.lz(z + 1), self.lz(z)) if dx < 0 else (self.lz(z), self.lz(z + 1))
                else: Z = self.lz(z + (dz > 0))
                c0, c1 = (0.77,) * 3, (1.0,) * 3
                if dx:             # faces the water (toward -dx)
                    m.quad(b['tex'], [(C(X), y, C(a), a / us, 0, c0), (C(X), y, C(b_), b_ / us, 0, c0),
                                      (C(X), Y0, C(b_), b_ / us, 1, c1), (C(X), Y0, C(a), a / us, 1, c1)])
                else:
                    a, b_ = (self.lx(x + 1), self.lx(x)) if dz > 0 else (self.lx(x), self.lx(x + 1))
                    m.quad(b['tex'], [(C(a), y, C(Z), a / us, 0, c0), (C(b_), y, C(Z), b_ / us, 0, c0),
                                      (C(b_), Y0, C(Z), b_ / us, 1, c1), (C(a), Y0, C(Z), a / us, 1, c1)])

    def rects_of(self, tiles):
        """Greedy rects (x0, z0, x1, z1, 0) inclusive over a set of Sapphire tiles."""
        import numpy as np
        if not tiles: return []
        xs = [t[0] for t in tiles]; zs = [t[1] for t in tiles]
        ox, oz = min(xs), min(zs)
        mask = np.zeros((max(zs) - oz + 1, max(xs) - ox + 1), bool)
        for x, z in tiles: mask[z - oz, x - ox] = True
        return [(x0 + ox, z0 + oz, x1 - 1 + ox, z1 - 1 + oz, 0) for x0, z0, x1, z1, _ in
                self.rects(mask, np.zeros(mask.shape, np.float32))]

    def tex_uv(self, ft, x, z, rect):
        """Texture coordinates of local point (x, z) in floor_tex / block-top entry ft (rect = its unit rect)."""
        X0, Z0, X1, Z1 = rect
        rot = ft.get('rot', 0) % 360
        if ft.get('stretch'):
            u, v = (x - X0) / max(1, X1 - X0), (Z1 - z) / max(1, Z1 - Z0)
            for _ in range(rot // 90): u, v = v, 1 - u
            return u, v
        su = ft.get('size', 32); sv = ft.get('size_v', su)
        du, dv = ft.get('uv', [0, 0])
        a, b = x, -z
        for _ in range(rot // 90): a, b = b, -a
        return a / su + du, b / sv + dv

    def tex_quad_flat(self, m, ft, x0, z0, x1, z1, y, col):
        C = lambda v: v - 256
        rect = self.unit_rect(ft) if ('rect' in ft or 'units' in ft) else (x0, z0, x1, z1)
        uv = lambda x, z: self.tex_uv(ft, x, z, rect)
        self.floor_quad(m, ft['tex'], [(C(x0), y, C(z1)) + uv(x0, z1) + (col,), (C(x1), y, C(z1)) + uv(x1, z1) + (col,),
                                       (C(x1), y, C(z0)) + uv(x1, z0) + (col,), (C(x0), y, C(z0)) + uv(x0, z0) + (col,)])

    def floor_quad(self, m, mat, verts):
        """A flat quad facing up (verts as dae.Model.quad, each with its colour) and its seam twin UNDER units below,
        split along the other diagonal (UNDER above; quads at least SEAM_W wide)."""
        m.quad(mat, verts)
        if max(v[0] for v in verts) - min(v[0] for v in verts) < SEAM_W: return
        a, b, c, d = [(v[0], v[1] - UNDER) + tuple(v[2:]) for v in verts]
        m.quad(mat, [b, c, d, a])

    def block_style(self, b):
        base = dict(self.styles.get(b['use'], {})) if 'use' in b else {}
        base.update({k: v for k, v in b.items() if k != 'use'})
        return base

    def block(self, m, i, b):
        """Raised box(es) of blocks[i]: top at floor + h, faces south / west / east (the camera never sees north faces)."""
        import numpy as np
        b = self.block_style(b)
        C = lambda v: v - 256
        mask = self.bgrid == i + 1
        if not mask.any(): return
        h = b.get('h', 16); yt = Y0 + h
        top, side = b['top'], b['side']
        st_, ss, sw = b.get('shade_top', 1.0), b.get('shade_s', 0.8), b.get('shade_we', 0.55)
        top_ = {k: v for k, v in top.items() if k not in ('rect', 'units')}     # stretch: once over each top rect
        for x0, z0, x1, z1, _ in self.rects(mask, np.zeros(mask.shape, np.float32)):
            self.tex_quad_flat(m, top_, x0, z0, x1, z1, yt, (st_,) * 3)
        e = self.edges(mask)
        us = side.get('u_size', 32); v0, v1 = side.get('v', [0, 1])
        vs = side.get('v_size')                                  # units per v repeat (default: once over the height)
        vt = (lambda y: v0 + (y - Y0) / vs) if vs else (lambda y: v0 + (v1 - v0) * (y - Y0) / h)
        for z, x0, x1 in e['S']:                                 # south face (faces +z)
            c = (ss,) * 3
            m.quad(side['tex'], [(C(x0), Y0, C(z), x0 / us, vt(Y0), c), (C(x1), Y0, C(z), x1 / us, vt(Y0), c),
                                 (C(x1), yt, C(z), x1 / us, vt(yt), c), (C(x0), yt, C(z), x0 / us, vt(yt), c)])
        if h < 0:                                                # a pit (h < 0: pools, tracks, drops): the camera
            c = (ss,) * 3                                        # sees its NORTH inner wall (facing south); without it
            for z, x0, x1 in e['N']:                             # the void showed there (indoor_check, kind p)
                m.quad(side['tex'], [(C(x1), Y0, C(z), x1 / us, vt(Y0), c), (C(x0), Y0, C(z), x0 / us, vt(Y0), c),
                                     (C(x0), yt, C(z), x0 / us, vt(yt), c), (C(x1), yt, C(z), x1 / us, vt(yt), c)])
        c = (sw,) * 3
        for x, z0, z1 in e['E']:                                 # east face (faces +x)
            m.quad(side['tex'], [(C(x), Y0, C(z1), -z1 / us, vt(Y0), c), (C(x), Y0, C(z0), -z0 / us, vt(Y0), c),
                                 (C(x), yt, C(z0), -z0 / us, vt(yt), c), (C(x), yt, C(z1), -z1 / us, vt(yt), c)])
        for x, z0, z1 in e['W']:                                 # west face (faces -x)
            m.quad(side['tex'], [(C(x), Y0, C(z0), z0 / us, vt(Y0), c), (C(x), Y0, C(z1), z1 / us, vt(Y0), c),
                                 (C(x), yt, C(z1), z1 / us, vt(yt), c), (C(x), yt, C(z0), z0 / us, vt(yt), c)])

    def corner_low(self, key, x, z0):
        """Whether the side wall segment at unit x starting at unit z0 begins right beside a walkable floor tile one row
        north of it (the tile diagonally north-west of a west wall's floor tile, north-east of an east wall's)."""
        if self.r.get('corner_walls') is False or z0 % T: return False
        tz = z0 // T - self.oz
        tx = (x + SIDE) // T - self.ox if key == 'W' else (x - SIDE) // T - 1 - self.ox
        q = (tx - 1 if key == 'W' else tx + 1, tz - 1)
        if q not in self.floor_tiles or not (0 <= q[1] < self.H and 0 <= q[0] < self.W): return False
        unblocked = {tuple(t) for t in self.r.get('unblock', [])}; blocked = {tuple(t) for t in self.r.get('block', [])}
        return bool(self.sm['walk'][q[1]][q[0]] or q in unblocked) and q not in blocked

    def continues_north(self, x, z0, key):
        """Whether a side wall's cap should reach over the back wall's cap (outer corner)."""
        cx = x if key == 'W' else x - 1
        return z0 > 0 and self.kind[z0 - 1, cx] == 0

    def cap(self, m, tex, x0, z0, x1, z1):
        m.quad(tex, [(x0, YW, z1, 0, 0), (x1, YW, z1, 1, 0), (x1, YW, z0, 1, 1), (x0, YW, z0, 0, 1)], color=(0, 0, 0))

    def lip_x(self, m, tex, x, z0, z1, key):
        a, b = (z1, z0) if key == 'W' else (z0, z1)
        m.quad(tex, [(x, YLIP, a, 0, 0), (x, YLIP, b, 1, 0), (x, Y0, b, 1, 1), (x, Y0, a, 0, 1)], color=(0, 0, 0))

    def rug(self, m, mt):
        x0, z0, x1, z1 = mt['rect']
        X0, X1, Z0, Z1 = self.lx(x0) - 256, self.lx(x1 + 1) - 256, self.lz(z0) - 256, self.lz(z1 + 1) - 256
        b = mt.get('border', 0.25)
        bu = mt.get('border_units', 8)
        xs = [X0, X0 + bu, X1 - bu, X1]; zs = [Z0, Z0 + bu, Z1 - bu, Z1]
        us = [0, b, 1 - b, 1]; vs = [1, 1 - b, b, 0]
        y = mt.get('y', -1)
        if 'uv' in mt:                                   # one quad showing a part of the texture [u0, v0, u1, v1]
            u0, va, u1, vb = mt['uv']                    # (Black 2's Center counter top: in02_pc's orange corner)
            m.quad(mt['tex'], [(X0, y, Z1, u0, va), (X1, y, Z1, u1, va), (X1, y, Z0, u1, vb), (X0, y, Z0, u0, vb)])
            return
        for i in range(3):
            for j in range(3):
                m.quad(mt['tex'], [(xs[i], y, zs[j + 1], us[i], vs[j + 1]), (xs[i + 1], y, zs[j + 1], us[i + 1], vs[j + 1]),
                                   (xs[i + 1], y, zs[j], us[i + 1], vs[j]), (xs[i], y, zs[j], us[i], vs[j])])

    def rug_rect(self, mt):
        """Local unit extents (X0, Z0, X1, Z1) of a rug as rug() draws it (a reversed rect turns the texture)."""
        x0, z0, x1, z1 = mt['rect']
        X = sorted((self.lx(x0), self.lx(x1 + 1))); Z = sorted((self.lz(z0), self.lz(z1 + 1)))
        return X[0], Z[0], X[1], Z[1]

    def rug_heights(self):
        """y of every rug: its recipe y (default -1), raised to >= LAYER above the floor, above every raised block top
        under it and above every earlier rug it overlaps (closer layers flicker in melonDS)."""
        if hasattr(self, '_rug_y'): return self._rug_y
        out, done = [], []
        for mt in self.r.get('mats', []):
            X0, Z0, X1, Z1 = R = self.rug_rect(mt)
            y = max(mt.get('y', -1), Y0 + LAYER)
            fl, ce = lambda q: int(math.floor(max(q, 0))), lambda q: int(math.ceil(max(q, 0)))   # a rug rect may end
            under = self.bgrid[fl(Z0):ce(Z1), fl(X0):ce(X1)]                   # inside a tile (indoor_check)
            for i in sorted(set(int(v) for v in under.flat if v)):
                y = max(y, Y0 + self.block_style(self.r['blocks'][i - 1]).get('h', 16) + LAYER)
            for (A0, B0, A1, B1), yo in done:                           # stacked rugs (a mat on a carpet)
                if min(X1, A1) - max(X0, A0) > 0.5 and min(Z1, B1) - max(Z0, B0) > 0.5 and abs(y - yo) < LAYER:
                    y = yo + LAYER
            out.append(y); done.append((R, y))
        self._rug_y = out
        return out

    def decal_gaps(self):
        """Distance of every wall decal from the wall: its recipe gap (default 0.5) raised to >= LAYER, and >= LAYER in
        front of an earlier decal it overlaps on the same wall."""
        out, done = [], []
        for d in self.r.get('decals', []):
            cx = self.lx(d['at'][0]); w, h = d['w'], d['h']; y0 = d.get('y', 16)
            wz = self.wall_z(cx, self.lz(d.get('z', self.floor_first_row(int(d['at'][0]))) + 0.5))
            g = max(d.get('gap', 0.5), LAYER)
            for (wz2, a0, a1, b0, b1), g2 in done:
                if wz2 == wz and min(cx + w / 2, a1) - max(cx - w / 2, a0) > 0.5 and min(y0 + h, b1) - max(y0, b0) > 0.5 \
                        and abs(g - g2) < LAYER:
                    g = g2 + LAYER
            out.append(g); done.append(((wz, cx - w / 2, cx + w / 2, y0, y0 + h), g))
        return out

    def doorway_spans(self):
        """[(wall z, x0, x1)] local units: the back-wall doorways of furniture {"wall": "N", "doorway": true} (pwt_tower,
        2026-10-11). Black 2's opening doors (door_h5_in: its open animation swings both halves back about 16 units, BCA0
        door_h5_in_op) stand in a dark recess of a taller wall (chunk 899, zone 384: wall face 9 units in front of the
        door, a black-textured recess 11 units behind it); in front of a plain wall their halves swing into the wall and
        the open door shows wall. Here the doorway is the door model's width cut out of the back wall, with a black recess
        behind it (2 x CAP deep, 8 units wider each side, roofed at the wall top) and a black lintel over the void: with
        the door 1 unit inside the cut and 1 lower (recipe gap -1, y -1) nothing of a swung half shows (tested in the
        emulator: Battle Tower lobby and corridor)."""
        out = []
        for f in self.r.get('furniture', []):
            if not f.get('doorway') or f.get('wall') != 'N': continue
            name = f.get('m') or interior_models()[1][f['res']][0]
            x0, x1, _, _, _, _ = bmd_box(interior_models()[0][name][2])
            cx = f['tile'][0] + 0.5 if 'tile' in f else (f['tiles'][0] + f['tiles'][2] + 1) / 2
            cz = f['tile'][1] + 0.5 if 'tile' in f else (f['tiles'][1] + f['tiles'][3] + 1) / 2
            mid, half = self.lx(cx) + f.get('dx', 0), (x1 - x0) / 2       # placements(): the box centred on the tile
            out.append((self.wall_z(self.lx(cx), self.lz(cz)), round(mid - half), round(mid + half)))
        return out

    def wall_z(self, lx_, lz_):
        """Local z of the back wall north of local point (lx_, lz_)."""
        z = int(lz_)
        while z > 0 and self.kind[z - 1, int(lx_)] in (1, 2, 3, 4) and not self.inner_mask[z - 1, int(lx_)]: z -= 1
        return z

    def wall_x(self, lx_, lz_, side):
        x = int(lx_)
        if side == 'W':
            while x > 0 and self.kind[int(lz_), x - 1] in (1, 2, 3, 4) and not self.inner_mask[int(lz_), x - 1]: x -= 1
            return x
        while x < self.NX - 1 and self.kind[int(lz_), x + 1] in (1, 2, 3, 4) and not self.inner_mask[int(lz_), x + 1]: x += 1
        return x + 1

    def decal(self, m, d):
        cx = self.lx(d['at'][0]); w, h = d['w'], d['h']
        cz = self.wall_z(cx, self.lz(d.get('z', self.floor_first_row(int(d['at'][0]))) + 0.5))
        y0 = d.get('y', 16)
        if 'face_z' in d: cz = self.lz(d['face_z'])        # ship_hideouts: on a plane at that tile line (a block's face)
        z = cz - 256 + d.get('gap', 0.5)
        u0, v0, u1, v1 = d.get('uv', [0, 0, 1, 1])         # ship_hideouts: a part of an atlas texture (default all)
        m.quad(d['tex'], [(cx - w / 2 - 256, y0, z, u0, v0), (cx + w / 2 - 256, y0, z, u1, v0),
                          (cx + w / 2 - 256, y0 + h, z, u1, v1), (cx - w / 2 - 256, y0 + h, z, u0, v1)])

    def floor_first_row(self, tx):
        return min([z for (x, z) in self.floor_tiles - self.inner_tiles if x == tx] or [z for (x, z) in self.floor_tiles if x == tx])

    # -------------------------------------------------------------------------------------------- furniture
    def stair_place(self, f):
        """(rot, px, pz) of a "stair" piece: local units of the model origin (see STAIR_MODELS)."""
        kind, ax = STAIR_MODELS[f['m']]
        d = f.get('dir', 'N'); dx, dz = DIRS[d]
        tx, tz = f['stair']
        rot = stair_rot(kind, d)
        ox_, oz_ = rot_pt(ax, 0, rot)
        return rot, self.lx(tx + 0.5 - dx * 0.5) - ox_, self.lz(tz + 0.5 - dz * 0.5) - oz_

    def stair_planes(self):
        """{zone tile: (u16 a, u16 b)}: the sloped collision planes of the "stair" pieces' tiles (the warp tile and the
        next one along the flight), 0 at the warp tile's approach edge, +-16 a tile, as Black 2's stair tiles."""
        out = {}
        for f in self.r.get('furniture', []):
            if 'stair' not in f or f.get('m') not in STAIR_MODELS: continue
            kind, _ = STAIR_MODELS[f['m']]
            d = f.get('dir', 'N'); dx, dz = DIRS[d]
            opp = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[d]
            slope = SLOPE_16[d] if kind == 'up' else SLOPE_16[opp]
            sign = 1 if kind == 'up' else -1
            for k in (0, 1):
                X, Z = self.ox + f['stair'][0] + k * dx, self.oz + f['stair'][1] + k * dz
                cx, cz = (X % 32) * T + 8 - 256, (Z % 32) * T + 8 - 256
                out[(X, Z)] = plane_cell(slope, cx, sign * (8 + 16 * k), cz)
        return out

    def lift(self, placed):
        """Keep every piece's lowest face (its shadow) >= LAYER above the surface it stands on: a rug under it (its
        final height, rug_heights) or another piece it is stacked on (that piece's top). A piece whose lowest face is
        already >= LAYER above, or more than 1 unit below (sunk into it on purpose), is left alone. Recipe "lift": false
        on a piece turns this off for it."""
        rugs = [(self.rug_rect(mt), y) for mt, y in zip(self.r.get('mats', []), self.rug_heights())]
        def over(a, b):                       # xz overlap of two (X0, X1, Z0, Z1) boxes, units
            return min(a[1], b[1]) - max(a[0], b[0]) > 0.5 and min(a[3], b[3]) - max(a[2], b[2]) > 0.5
        for p in sorted(placed, key=lambda p: p['y'] + p['y0']):
            if p['f'].get('lift') is False: continue
            base = p['y'] + p['y0']
            need = None
            for (X0, Z0, X1, Z1), yr in rugs:
                if over(p['box'], (X0, X1, Z0, Z1)) and yr - 1 <= base < yr + LAYER: need = max(need or -99, yr + LAYER)
            for q in placed:
                if q is p or not over(p['box'], q['box']): continue
                qb, qt = q['y'] + q['y0'], q['y'] + q['y1']
                if qb < base - 1 and qt - 1 <= base < qt + LAYER: need = max(need or -99, qt + LAYER)
            if need is not None and need > base: p['y'] += need - base
        # a flat piece (floor cushion) whose face lies within LAYER of a neighbour's shadow it overlaps moves sideways
        # off that shadow (at most 6 units, along the axis of the smaller overlap, away from the neighbour)
        for p in placed:
            if p['f'].get('lift') is False or p['y1'] - p['y0'] > 1.5: continue
            for q in placed:
                if q is p or abs((q['y'] + q['y0']) - (p['y'] + p['y0'])) >= LAYER or not over(p['box'], q['box']): continue
                a, b = p['box'], q['box']
                ox_, oz_ = min(a[1], b[1]) - max(a[0], b[0]), min(a[3], b[3]) - max(a[2], b[2])
                if min(ox_, oz_) + 0.5 > 6: continue
                if ox_ <= oz_:
                    d = (ox_ + 0.5) * (1 if (a[0] + a[1]) >= (b[0] + b[1]) else -1); p['px'] += d
                    p['box'] = (a[0] + d, a[1] + d, a[2], a[3])
                else:
                    d = (oz_ + 0.5) * (1 if (a[2] + a[3]) >= (b[2] + b[3]) else -1); p['pz'] += d
                    p['box'] = (a[0], a[1], a[2] + d, a[3] + d)

    def placements(self):
        by_name, by_res = interior_models()
        recs, models, placed = [], OrderedDict(), []
        for f in self.r.get('furniture', []):
            if 'res' in f: res = f['res']; name, pack, bmd = by_res[res]
            else: name = f['m']; res, pack, bmd = by_name[name]
            rot = f.get('rot', 0) % 360
            bx0, bx1, bz0, bz1 = rotate_box(bmd_box(bmd), rot)
            if 'at' in f: cx, cz = f['at']
            elif 'tiles' in f: cx, cz = (f['tiles'][0] + f['tiles'][2] + 1) / 2, (f['tiles'][1] + f['tiles'][3] + 1) / 2
            elif 'stair' in f: cx, cz = f['stair'][0] + 0.5, f['stair'][1] + 0.5
            else: cx, cz = f['tile'][0] + 0.5, f['tile'][1] + 0.5
            px = self.lx(cx) - (bx0 + bx1) / 2
            pz = self.lz(cz) - (bz0 + bz1) / 2
            wall, gap = f.get('wall'), f.get('gap', 0)
            if wall == 'N':
                pz = self.wall_z(self.lx(cx), self.lz(cz)) + gap - bz0
                front = None if MOUNTED.match(name) else self.wall_row_front(cx, cz, f, (px + bx0, px + bx1, pz + bz1))
                if front is not None and front - bz1 > pz: pz = front - bz1
            elif wall == 'W': px = self.wall_x(self.lx(cx), self.lz(cz), 'W') + gap - bx0
            elif wall == 'E': px = self.wall_x(self.lx(cx), self.lz(cz), 'E') - gap - bx1
            if 'w_edge' in f: px = self.lx(f['w_edge']) - bx0          # align a side of the footprint to a tile line
            if 'e_edge' in f: px = self.lx(f['e_edge']) - bx1
            if 'n_edge' in f: pz = self.lz(f['n_edge']) - bz0
            if 's_edge' in f: pz = self.lz(f['s_edge']) - bz1
            px += f.get('dx', 0); pz += f.get('dz', 0)
            if 'stair' in f and name in STAIR_MODELS:          # Black 2's stair placement (STAIR_MODELS)
                rot, px, pz = self.stair_place(f)
                bx0, bx1, bz0, bz1 = rotate_box(bmd_box(bmd), rot)
            y = f.get('y', 0)
            box = bmd_box(bmd)
            placed.append(dict(f=f, res=res, rot=rot, px=px, pz=pz, y=y, box=(px + bx0, px + bx1, pz + bz0, pz + bz1),
                               y0=box[2], y1=box[3]))
            models[res] = dict(res=res, name=name, pack=pack)
            if name in DERIVED_MODELS:                         # a resized Black 2 model: its file and base model
                models[res].update(file=name + '.nsbmd', base=by_name[DERIVED_MODELS[name][0]][0])
        self.lift(placed)
        for p in placed:
            px, pz, y, rot, res = p['px'], p['pz'], p['y'], p['rot'], p['res']
            ci = min(max(int(px // 512), 0), self.mw - 1); cj = min(max(int(pz // 512), 0), self.mh - 1)   # its chunk
            recs.append((cj * self.mw + ci, struct.pack('<iiiH', round((px - 256 - 512 * ci) * 4096), round(y * 4096),
                         round(-(pz - 256 - 512 * cj) * 4096), rot * 0x10000 // 360) + bytes([res >> 8, res & 0xFF])))
            p['f']['_pos'] = [px - 256, y, pz - 256]
            if 'stair' in p['f']: p['f']['_rot'] = rot
        self.models = list(models.values())
        self.chunk_placements = []
        for k in range(self.mw * self.mh):
            mine = [r for c, r in recs if c == k]
            # Black 2 places at most 32 models per chunk (facilities agent; ground's notes): refuse more
            assert len(mine) <= 32, f'{self.name}: chunk {k} has {len(mine)} furniture placements, Black 2 allows 32'
            self.chunk_placements.append(struct.pack('<I', len(mine)) + b''.join(mine))
        return self.chunk_placements[0]

    # -------------------------------------------------------------------------------------------- collision
    def collision(self):
        walk = set()
        sm = self.sm
        for z in range(self.H):
            for x in range(self.W):
                if (sm['walk'][z][x] or [x, z] in self.r.get('unblock', []) or (x, z) in self.walk_up) \
                        and (x, z) not in self.stairs and [x, z] not in self.r.get('block', []):
                    walk.add((self.ox + x, self.oz + z))
        self.walk_chunk = walk
        # "ledges": Sapphire's jump tiles (MB_JUMP_EAST/WEST/NORTH/SOUTH 0x38-0x3B) become Black 2 ledge cells (class
        # 0x72/0x73/0x74/0x75 = jump right/left/up/down, flags 1 = blocks walking onto it: Route 2's ledge cells)
        ledge = {}
        if self.r.get('ledges'):
            for z in range(self.H):
                for x in range(self.W):
                    b = sm['beh'][z][x]
                    if 0x38 <= b <= 0x3B: ledge[(self.ox + x, self.oz + z)] = {0x38: 0x72, 0x39: 0x73, 0x3A: 0x74, 0x3B: 0x75}[b]
        # Black 2 tile types on solid tiles (cell u16 0, 3, type, flags 1 as its Pokémon Center chunk 827): Sapphire's
        # counters 0xD4 (talk to the person across it), shop shelves 0xDF, PCs 0xD6 (ov036 MapTile_Is*,
        # SPECIAL_TILE_SCRIPTS 0x021ca844; tested by the shops and centers agents), plus the recipe's own
        # "attrs": [{"attr": "0xe2", "tiles": [[x, z], ...]}] and "classes": {"0xd4": [[x, z], ...]}
        for z in range(self.H):
            for x in range(self.W):
                t = SAPPHIRE_TILE_TYPES.get(sm['beh'][z][x])
                if t and (self.ox + x, self.oz + z) not in walk: ledge[(self.ox + x, self.oz + z)] = t
        for a in self.r.get('attrs', []):
            for x, z in a['tiles']: ledge[(self.ox + x, self.oz + z)] = int(str(a['attr']), 0)
        for t, tiles in self.r.get('classes', {}).items():
            for x, z in tiles: ledge[(self.ox + x, self.oz + z)] = int(str(t), 0)
        planes = {t: ab for t, ab in self.stair_planes().items() if t not in walk}   # stair tiles (solid, sloped)
        # "solid_y": [{"y": units, "tiles": [[x, z], ...]}] (walkability 2026-10-11): solid tiles at that collision height,
        # a table top: a person or Poke Ball standing there is drawn on the table (Black 2 snaps actors to their tile's
        # height; its own starter balls stand on tables so: zone 391, solid tiles at 8 with the balls' y 8)
        solid_h = {(self.ox + x, self.oz + z): e['y'] for e in self.r.get('solid_y', []) for x, z in e['tiles']}
        extra = self.level_cells(walk)          # "raised" / "ramps" / "water" (ship_hideouts; empty without them)
        # "encounters": true (caves_misc: Sky Pillar, New Mauville): walkable tiles with Sapphire's wild-encounter
        # behaviours get flags 0x84 (bit 2 = land encounters: ov036 FieldEncount_DecideTypeByTerrain; the class
        # only matters for double-battle grass), as models_cave.py's cave floors
        enc = {(self.ox + x, self.oz + z) for z in range(self.H) for x in range(self.W)
               if sm['beh'][z][x] in (0x02, 0x03, 0x08, 0x0B, 0x24)} if self.r.get('encounters') else set()
        # (walkability 2026-10-11) Sapphire's one-way walls (MB_IMPASSABLE_* 0x30-0x37: the Contest Halls' seat rows) and
        # its elevation rule (two walkable tiles of different elevations, neither 0/15: Mossdeep Gym's and the hideouts'
        # raised floors) keep tiles apart that Black 2 let you walk between (b2tools/walk_diff.py THROUGH, 93 moves):
        # Black 2's side walls (classes 0x51-0x58 on a walkable tile, TileExitBlockCheck_*, as heights.py step 9b
        # outdoors), on one of the two tiles (the one whose sides stay a class Black 2 has)
        self.side_walls = self.side_wall_classes(walk, ledge, planes, extra)
        self.chunk_collision = []
        for cj in range(self.mh):
            for ci in range(self.mw):
                per = bytearray(struct.pack('<HH', 32, 32))
                for z in range(32 * cj, 32 * cj + 32):
                    for x in range(32 * ci, 32 * ci + 32):
                        per += (struct.pack('<HHHH', *extra[(x, z)]) if (x, z) in extra else
                                struct.pack('<HHHH', *planes[(x, z)], 1, 0x81) if (x, z) in planes else
                                struct.pack('<HHHH', 0, 3, ledge[(x, z)], 1) if (x, z) in ledge else
                                struct.pack('<HHHH', 0, 3, self.side_walls.get((x, z), 0), 0x84 if (x, z) in enc else 0x80) if (x, z) in walk else
                                struct.pack('<HHHH', 0, heights().flat_index(solid_h[(x, z)]), 1, 0x81) if (x, z) in solid_h else
                                struct.pack('<HHHH', 0, 3, 1, 0x81))
                self.chunk_collision.append(bytes(per))
        return self.chunk_collision[0]

    def side_wall_classes(self, walk, special, planes, extra):
        """{zone tile: Black 2 side-wall class} for the plain walkable tiles Sapphire keeps apart (see collision)."""
        sm = self.sm
        if 'elev' not in sm: return {}
        G3_BLOCK = {0x30: 'e', 0x31: 'w', 0x32: 'n', 0x33: 's', 0x34: 'ne', 0x35: 'nw', 0x36: 'se', 0x37: 'sw'}
        OPP = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        CLS = {frozenset('e'): 0x51, frozenset('w'): 0x52, frozenset('n'): 0x53, frozenset('s'): 0x54,
               frozenset('ne'): 0x55, frozenset('nw'): 0x56, frozenset('se'): 0x57, frozenset('sw'): 0x58}
        plain = lambda t: t in walk and t not in special and t not in planes and t not in extra
        wet = self.water_tiles() if (self.r.get('water') or {}) and not (self.r.get('water') or {}).get('cell') else set()
        sides = {}
        for X, Z in sorted(walk):
            x, z = X - self.ox, Z - self.oz
            if not (0 <= x < self.W and 0 <= z < self.H): continue
            for d, (dx, dz) in (('e', (1, 0)), ('s', (0, 1))):       # each pair once
                nx, nz = x + dx, z + dz
                if (X + dx, Z + dz) not in walk or not (0 <= nx < self.W and 0 <= nz < self.H): continue
                e1, e2 = sm['elev'][z][x], sm['elev'][nz][nx]
                land = plain((X, Z)) and plain((X + dx, Z + dz))
                w1, w2 = (x, z) in wet, (nx, nz) in wet
                blocked = d in G3_BLOCK.get(sm['beh'][z][x], '') or OPP[d] in G3_BLOCK.get(sm['beh'][nz][nx], '') or \
                    (land and e1 not in (0, 15) and e2 not in (0, 15) and e1 != e2) or \
                    (w1 != w2 and (e2 if w1 else e1) not in (0, 1, 3, 15))   # (surfing on / landing: only from / onto
                                                                             # elevation 3, pokeruby sub_8058EF0)
                if not blocked: continue
                for t, side in (((X, Z), d), ((X + dx, Z + dz), OPP[d])):
                    want = frozenset(sides.get(t, set()) | {side})
                    if plain(t) and want in CLS: sides.setdefault(t, set()).add(side); break
        return {t: CLS[frozenset(v)] for t, v in sides.items()}

    def level_cells(self, walk):
        """{zone tile: (u16 a, u16 b, class, flags)} of the recipe's "raised" walkable tiles (flat plane at their y),
        "ramps" (slope planes) and "water" (Black 2 water cells); empty for a recipe without those keys."""
        out = {}
        if not any(k in self.r for k in ('raised', 'ramps', 'water')): return out
        H = heights()
        for e in self.r.get('raised', []):
            for x, z in sorted(self.tile_set(e)):
                if (self.ox + x, self.oz + z) in walk: out[(self.ox + x, self.oz + z)] = (0, H.flat_index(e['y']), 0, 0x80)
        for rp in self.r.get('ramps', []):
            tiles, d, n, k = self.ramp_geom(rp)
            for x, z in sorted(tiles):
                X, Z = self.ox + x, self.oz + z
                if (X, Z) not in walk: continue
                cx, cz = (X % 32) * T + 8 - 256, (Z % 32) * T + 8 - 256
                out[(X, Z)] = plane_cell(SLOPE_16[d], cx, rp['y0'] + 16 * k(x, z) + 8, cz) + (0, 0x80)
        if self.r.get('water'):
            y = self.r['water'].get('y', -8)
            cell = self.r['water'].get('cell')           # (dive agent) e.g. [0x9C, 2]: the Abyssal Ruins' swimmable
            for x, z in sorted(self.water_tiles()):      # cells for a flooded room the player dives in
                b = self.sm['beh'][z][x]
                out[(self.ox + x, self.oz + z)] = ((0, H.flat_index(y), int(str(cell[0]), 0), int(str(cell[1]), 0)) if cell else
                                                   (0, H.flat_index(y), 0x3F, 0x16 if b in self.SURF_ENC else 0x12))
        return out

    def camera(self):
        """Camera target box (world units) like Black 2's own rooms (a/1/0/9): x within the walkable tile centres
        +-45, z from the first row +6 to the last row -32 (a narrow room centres)."""
        xs = [x for x, _ in self.walk_chunk]; zs = [z for _, z in self.walk_chunk]
        x0, x1 = min(xs) * T + 8 + 45, max(xs) * T + 8 - 45
        z0, z1 = min(zs) * T + 8 + 6, max(zs) * T + 8 - 32
        if x0 > x1: x0 = x1 = (x0 + x1) // 2
        if z0 > z1: z0 = z1 = (z0 + z1) // 2
        return [x0, x1, z0, z1]

    def warp_spots(self):
        """Gen 5 warp records for Sapphire's warp tiles: exit mats -> type 1 on the mat tiles themselves (you arrive on
        the mat facing north and leave by pressing down on it, as in Sapphire and as Black 2's own mats work; the genkan
        notch below is only the look of Black 2's entrances); stairs/doors -> type 2 on the tile, entered walking north
        (dir 2 = its south side)."""
        spots = []
        rows = {}
        for x, z in sorted(self.exits): rows.setdefault(z, []).append(x)
        for z, xs in rows.items():
            run = [xs[0]]
            for x in xs[1:] + [None]:
                if x is not None and x == run[-1] + 1: run.append(x); continue
                spots.append(dict(kind='exit', tiles=[[t, z] for t in run], type=1, dir=1,
                                  x=self.ox + run[0], z=self.oz + z, w=len(run), h=1))
                if x is not None: run = [x]
        walk_in = {tuple(f['stair']): {'N': 2, 'S': 1, 'E': 3, 'W': 4}[f.get('dir', 'N')]     # a "stair" piece's
                   for f in self.r.get('furniture', []) if 'stair' in f}                       # walk-in direction
        for x, z in self.stairs:
            spots.append(dict(kind='stairs', tiles=[[x, z]], type=2, dir=walk_in.get((x, z), 2), x=self.ox + x, z=self.oz + z, w=1, h=1))
        return spots

# ------------------------------------------------------------------------------------------------ big rooms
def _clip(poly, axis, bound, keep_below):
    """Sutherland-Hodgman: keep the part of poly (vertices (x, y, z, u, v, (r, g, b))) with v[axis] <= bound
    (keep_below) or >= bound, interpolating every attribute on the cut."""
    out = []
    inside = (lambda p: p[axis] <= bound + 1e-6) if keep_below else (lambda p: p[axis] >= bound - 1e-6)
    for k, cur in enumerate(poly):
        prev = poly[k - 1]
        ci, pi = inside(cur), inside(prev)
        if ci != pi:
            t = (bound - prev[axis]) / (cur[axis] - prev[axis])
            lerp = lambda a, b: a + (b - a) * t
            out.append(tuple(lerp(prev[i], cur[i]) for i in range(5)) + (tuple(lerp(prev[5][i], cur[5][i]) for i in range(3)),))
        if ci: out.append(cur)
    return out

def split_chunks(m, mw, mh):
    """Cut a room model (chunk-0-centred units) at the chunk edges: one Model per matrix cell (row-major), each in
    its own chunk-centred units; None for a cell with no geometry. A face lying exactly on a chunk edge goes to the
    chunk east/south of it."""
    out = []
    for cj in range(mh):
        for ci in range(mw):
            lo_x, hi_x = 512 * ci - 256, 512 * ci + 256
            lo_z, hi_z = 512 * cj - 256, 512 * cj + 256
            sub = Model(f'{m.name}_c{cj * mw + ci}')
            for mat, tris in m.tris.items():
                for t in tris:
                    xs = [v[0] for v in t]; zs = [v[2] for v in t]
                    if max(xs) < lo_x or min(xs) > hi_x or max(zs) < lo_z or min(zs) > hi_z: continue
                    if (max(xs) == min(xs) == hi_x and ci < mw - 1) or (max(zs) == min(zs) == hi_z and cj < mh - 1): continue
                    poly = list(t)
                    for axis, bound, below in ((0, lo_x, False), (0, hi_x, True), (2, lo_z, False), (2, hi_z, True)):
                        poly = _clip(poly, axis, bound, below)
                        if len(poly) < 3: break
                    if len(poly) < 3: continue
                    poly = [(x - 512 * ci, y, z - 512 * cj, u, v, c) for x, y, z, u, v, c in poly]
                    for k in range(1, len(poly) - 1):
                        a, b, c_ = poly[0], poly[k], poly[k + 1]
                        area = (b[0] - a[0]) * (c_[2] - a[2]) - (b[2] - a[2]) * (c_[0] - a[0])
                        ext = max(abs(b[1] - a[1]), abs(c_[1] - a[1]))
                        if abs(area) < 1e-6 and ext < 1e-6: continue                       # degenerate sliver
                        sub.tri(mat, [a, b, c_])
            out.append(sub if sub.tris else None)
    return out

def convert_chunks(out, files):
    """terrain_c<k>.dae -> .nsbmd with CTRMapV's writer (ToNsbmd --vcol), as b2tools/rebuild_interiors.sh does for
    terrain.dae (the classes it compiles: HOENN_JAVA_DIR or work/java)."""
    import subprocess
    J = os.environ.get('HOENN_JAVA_DIR') or os.path.join(ROOT, 'work', 'java')
    if not os.path.exists(os.path.join(J, 'ToNsbmd.class')):
        print(f'  {out}: ToNsbmd not compiled in {J}: chunk models left as .dae (run b2tools/rebuild_interiors.sh)')
        return
    cp = ':'.join([J, os.path.join(ROOT, 'tools', 'CTRMap.jar'), os.path.join(ROOT, 'tools', 'ctrmap-plugins', 'CTRMapV-1.4.1.jar')])
    batch = os.path.join(out, 'chunks_batch.txt')
    open(batch, 'w').write(''.join(f'{os.path.join(out, f)}.dae {os.path.join(out, f)}.nsbmd\n' for f in files))
    r = subprocess.run(['java', '-Djava.awt.headless=true', '-cp', cp, 'ToNsbmd', '--vcol', '--batch', batch,
                        os.path.join(out, 'palettes.txt')], capture_output=True, text=True)
    if r.returncode: raise SystemExit(f'{out}: ToNsbmd failed: {r.stderr[-500:]}')

# ------------------------------------------------------------------------------------------------ output
def gen3_tile_image(name, x, z):
    """The map's own drawn Gen 3 metatile at (x, z), 2x nearest (32x32), as a room texture: Sapphire's art resized,
    nothing drawn (user 2026-10-14: Mauville Gym's floor switches were invisible: b2tools/gyms_league_rooms.py)."""
    import numpy as np
    from PIL import Image
    from gba import Repo, MetatileRenderer
    dec, folder = globals()['map_source'](name) if 'map_source' in globals() else ('pokeruby', name)
    repo = Repo(os.path.join(ROOT, 'external', dec))
    g, l = repo.layout_grid(repo.map_json(folder)['layout'])
    mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
    im = Image.fromarray(np.asarray(mr.render(int(g[z, x]) & 0x3FF), dtype=np.uint8), 'RGBA')
    return im.convert('RGB').resize((32, 32), Image.NEAREST)

def texture_sources(room):
    """{texture: source map texture set} for every material of the terrain model."""
    st = room.style
    src = {st[k]['tex']: st[k]['src'] for k in ('floor', 'wall', 'genkan', 'black')}
    for mt in room.r.get('mats', []): src[mt['tex']] = mt['src']
    for d in room.r.get('decals', []): src[d['tex']] = d['src']
    for ft in room.r.get('floor_tex', []):             # "gen3": [x, z]: the map's own drawn Gen 3 metatile there
        src[ft['tex']] = ('gen3', room.r['map'], *ft['gen3']) if 'gen3' in ft else ft['src']
    for b in room.r.get('blocks', []):
        b = room.block_style(b)
        for k in ('top', 'side'): src[b[k]['tex']] = b[k]['src']
    for rp in room.r.get('ramps', []):                   # ship_hideouts' keys
        for k in ('tex', 'side'):
            if rp.get(k): src[rp[k]['tex']] = rp[k]['src']
    if room.r.get('water'):
        for k in ('tex', 'bank'):
            if room.r['water'].get(k): src[room.r['water'][k]['tex']] = room.r['water'][k]['src']
    return src

def build(name, out_root=OUT):
    room = Room(name)
    out = os.path.join(out_root, name)
    os.makedirs(out, exist_ok=True)
    m = room.build_terrain()
    import models_cave_mist as MIST                  # mist rooms (Lavaridge Gym): the void stays black (final_check)
    mist = MIST.room_active(room)
    if mist: MIST.room_geometry(room, m)
    src = texture_sources(room)
    if mist: src[MIST.VOID] = 332
    images = {}
    for ts in sorted({v for v in src.values() if isinstance(v, int)}):
        images.update({n: img for n, img, _ in nsbtx.decode(b2files.map_textures(FILES, ts))
                       if n in src and src[n] == ts})
    for n, v in src.items():
        if isinstance(v, tuple) and v[0] == 'gen3': images[n] = gen3_tile_image(*v[1:])
    for mat in m.tris:
        images[mat].save(os.path.join(out, mat + '.png'))
    big = room.mw * room.mh > 1
    parts = split_chunks(m, room.mw, room.mh) if big else [m]
    if mist: parts = MIST.apron(room, parts)        # black walls / apron past the matrix's edges
    assert parts[0] is not None, f'{name}: chunk 0 of the matrix is empty (move the room with "origin")'
    parts[0].write(os.path.join(out, 'terrain.dae'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in m.tris))
    open(os.path.join(out, 'placements.bin'), 'wb').write(room.placements())
    for md in room.models:                        # resized Black 2 models (DERIVED_MODELS)
        if md['name'] in DERIVED_MODELS: open(os.path.join(out, md['file']), 'wb').write(interior_models()[0][md['name']][2])
    open(os.path.join(out, 'collision.per'), 'wb').write(room.collision())
    extra = {}
    if big:                                       # chunks 1.. of a big room, and the whole room for previews
        m.write(os.path.join(out, 'terrain_all.dae'))
        chunks, todo = [], []
        for k, part in enumerate(parts):
            if k == 0:
                chunks.append(dict(terrain='terrain.nsbmd', collision='collision.per', placements='placements.bin'))
                continue
            if part is None and not any(room.chunk_collision[k][4 + 8 * i + 4] == 0 for i in range(1024)):
                chunks.append(None); continue                          # nothing to draw, nothing to walk on
            if part is None:                                           # walkable but nothing drawn: a black quad
                part = Model(f'{name}_c{k}'); part.quad(room.style['black']['tex'], [(-1, -40, 1, 0, 0), (1, -40, 1, 1, 0), (1, -40, -1, 1, 1), (-1, -40, -1, 0, 1)], color=(0, 0, 0))
            part.write(os.path.join(out, f'terrain_c{k}.dae')); todo.append(f'terrain_c{k}')
            open(os.path.join(out, f'collision_c{k}.per'), 'wb').write(room.chunk_collision[k])
            open(os.path.join(out, f'placements_c{k}.bin'), 'wb').write(room.chunk_placements[k])
            chunks.append(dict(terrain=f'terrain_c{k}.nsbmd', collision=f'collision_c{k}.per', placements=f'placements_c{k}.bin'))
        convert_chunks(out, todo)
        extra = dict(matrix=[room.mw, room.mh], chunks=chunks)
    meta = dict(name=name, map=room.r['map'], origin=[room.ox, room.oz], size=[room.W, room.H],
                terrain='terrain.nsbmd', collision='collision.per', placements='placements.bin',
                map_textures={t: src[t] for t in m.tris}, models=room.models, camera=room.camera(),
                warp_spots=room.warp_spots(), fly=[room.ox + room.exits[0][0], room.oz + room.exits[0][1]] if room.exits
                else [room.ox + room.W // 2, room.oz + room.H // 2],
                furniture=[dict(m=f.get('m', f.get('res')), pos=f['_pos'], rot=f.get('_rot', f.get('rot', 0))) for f in room.r.get('furniture', [])],
                **extra)
    if room.walk_up: meta['walk_up'] = sorted([list(t) for t in room.walk_up], key=lambda t: (t[1], t[0]))   # (option C)
    json.dump(meta, open(os.path.join(out, 'room.json'), 'w'), indent=1)
    return meta, sum(len(t) for t in m.tris.values())

def main(names):
    names = names or sorted(os.path.basename(f)[:-5] for f in os.listdir(LAYOUTS) if f.endswith('.json') and not f.startswith('_'))
    for n in names:
        meta, tris = build(n)
        print(f'{n}: {tris} triangles, {len(meta["models"])} furniture models, origin {meta["origin"]}, '
              f'warps {[(s["kind"], s["x"], s["z"], s["w"]) for s in meta["warp_spots"]]} -> {os.path.join(OUT, n)}')

if __name__ == '__main__':
    main([a for a in sys.argv[1:]])
