"""ship_hideouts agent: the Abandoned Ship (9 rooms) and the Aqua / Magma Hideouts rebuilt from Sapphire with Black 2's
own ship interiors (notes/INTERIORS.md, section "The Abandoned Ship and the hideouts"). Writes, for every room of the family:

  data/interior_layouts/<Map>.json                  the recipe for b2tools/models_interior.py (no "_auto": ours)
  data/interior_layouts/_styles_ship_hideouts.json  the texture styles and block styles below
  data/interiors/<zone>.json                        zone, room, area, header, warps in Sapphire's order, item balls,
                                                    simple people and signs (no "auto": ours)
  src/field_scripts/<scripts>_room_<Map>.s          simple people / signs (one message each, Sapphire's text);
  src/text/script/<text>_room_<Map>.txt             story scripts go after a line "// ---- story" (then the file is kept)
  src/encounters/<file>_cave_<Map>.s                Sapphire's wild table (converter/gen_caves.py's encounters(): the file
                                                    allocated in data/hoenn_encounters.json)

    python3 ship_hideouts_rooms.py [Map ...]          (default: every room below; the Magma Hideout's zone files only
                                                       with --magma or HOENN_VERSION=ruby: Sapphire has no door to it;
                                                       they go to the Ruby overlays data/interiors/ruby/,
                                                       src/field_scripts/ruby/, src/text/script/ruby/, notes/RUBY.md
                                                       "WP0 layout", and their exit names Lilycove's one hideout door)

Looks (Black 2 areas; their building packs already hold the furniture, their texture sets the textures):
  Abandoned Ship = the Royal Unova cruise ship (area 337, texture set 337, pack 55): dark wood corridor floor
    maq_rm03, white/blue wall maq_rm05, red cabin carpet maq_rs05, cabin_door models,
    portholes / lifebuoys (atlases maq_pt01 / maq_pt11), beds, chairs, tables, trash bins.
  Hideouts = the Plasma Frigate (area 379, texture set 379, pack 76): metal floors and walls, Black 2's warp panels
    (warp01/02 models + type-5 warps, as zones 553/559/575-578 do), consoles (pc01). The Team Plasma emblems of that
    set (in77b_m02, in77p_m01/m02) are never used.
Shapes follow Sapphire tile for tile: the floor is Sapphire's walkable tiles plus its furniture tiles; walls follow the
outline; collision is Sapphire's (models_interior.py); doors are Sapphire's warp tiles.
"""
import os, sys, json, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches')); sys.path.insert(0, os.path.join(ROOT, 'converter'))
from models_interior import FILES
import version  # noqa: E402  (Ruby-only rooms of data/versions.json -> the ruby/ overlays; door aliases)
import move_codes as MOVE_CODES                       # noqa: E402  (v165_fixes)

LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
ZONES = os.path.join(ROOT, 'data', 'interiors')
STORY_MARK = '// ---- story'
SHIP_AREA, HIDEOUT_AREA = 337, 379            # Royal Unova (zone 52), Plasma Frigate (zones 553-583)
TEMPLATE = 553                                # header fields of the Plasma Frigate's rooms (map type 16, indoor
                                              # transition, battle background 9, Escape Rope allowed)
BGM_SHIP = 0x4a9                              # SEQ_BGM_SW_D_25: the Strange House (Black 2's haunted house; Sapphire's
                                              # Abandoned Ship theme is its eerie piece)
BGM_HIDEOUT = 0x4aa                           # SEQ_BGM_SW_D_27_F_AJITO: the Plasma Frigate ("AJITO" = hideout, as
                                              # Sapphire's MUS_AQUA_MAGMA_HIDEOUT, MUS_AJITO)
MODEL_ITEM = 110

def T(ts, tex, **k): return dict(tex=tex, src=ts, **k)

def rooms_registry():
    return json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']

# ------------------------------------------------------------------------------------------------ styles
STYLES = {
    '_doc': 'ship_hideouts agent (b2tools/ship_hideouts_rooms.py writes this file): the Abandoned Ship in Black 2\'s '
            'Royal Unova cruise ship (texture set 337), the Aqua and Magma Hideouts in the Plasma Frigate (set 379); '
            'block styles for the ship\'s deck.',
    'sh_corridor': dict(_doc='Royal Unova corridor (chunk 931): dark wood planks, white wall with blue stripes',
                        floor=T(337, 'maq_rm03', size=32), wall=T(337, 'maq_rm05', u_size=32),
                        genkan=T(337, 'maq_rm04', size=32), black=T(285, 'black')),
    'sh_cabin': dict(_doc='Royal Unova cabin (chunks 948-950): red patterned carpet, the corridor\'s white wall (maq_rs01a, Royal Unova\'s cabin wall, is an atlas)',
                     floor=T(337, 'maq_rs05', size=16), wall=T(337, 'maq_rm05', u_size=32),
                     genkan=T(337, 'maq_rm04', size=32), black=T(285, 'black')),
    'sh_office': dict(_doc='the captain\'s office: Royal Unova blue cabin carpet, white wall with windows (maq_rm08)',
                      floor=T(337, 'maq_rs06', size=16), wall=T(337, 'maq_rm08', u_size=32),
                      genkan=T(337, 'maq_rm04', size=32), black=T(285, 'black')),
    'sh_deck': dict(_doc='the deck: wood planks (the floor under the holes), sea = Royal Unova\'s set\'s water',
                    floor=T(337, 'maq_rm03', size=32), wall=T(337, 'maq_rm05', u_size=32),
                    genkan=T(337, 'd0_miz', size=16), black=T(285, 'black')),
    'hd_metal': dict(_doc='Plasma Frigate corridor (chunks 696/697): riveted metal floor, grey panel wall',
                     floor=T(379, 'in77k_yuka1', size=32), wall=T(379, 'in77k_kabe1', u_size=16),
                     genkan=T(379, 'in77k_yuka2', size=16), black=T(285, 'black')),
    # block styles (recipes' "blocks" via "use")
    'sh_hull': dict(top=T(337, 'maq_rm03', size=32), side=T(337, 'maq_rm05', u_size=32, v=[0, 1], v_size=48),
                    shade_top=1.0, shade_s=0.85, shade_we=0.6),
    'sh_house': dict(top=T(285, 'black'), side=T(337, 'maq_rm05', u_size=32, v=[0, 1], v_size=48),
                     shade_top=0.0, shade_s=0.9, shade_we=0.6),
    'sh_rail': dict(top=T(337, 'maq_rm10', size=8), side=T(337, 'maq_rm10', u_size=8, v=[0, 1], v_size=8),
                    shade_top=0.9, shade_s=0.9, shade_we=0.7),
    'sh_funnel': dict(top=T(285, 'black'), side=T(337, 'fs_room7', u_size=8, v=[0, 1], v_size=8),
                      shade_top=0.0, shade_s=1.0, shade_we=0.7),
    'sh_pipe': dict(top=T(337, 'fs_room8', size=8), side=T(337, 'fs_room8', u_size=8, v=[0, 1], v_size=8),
                    shade_top=0.8, shade_s=0.75, shade_we=0.55),
}

# ------------------------------------------------------------------------------------------------ Sapphire helpers
def smap(name):
    import models_cave as MC
    return MC.sapphire(name)

def walkable(name):
    sm = smap(name)
    return {(x, z) for z in range(sm['h']) for x in range(sm['w']) if sm['walk'][z][x]}

def tiles_with(name, mts):
    sm = smap(name)
    return sorted((x, z) for z in range(sm['h']) for x in range(sm['w']) if sm['mt'][z][x] in mts)

def row_rects(tiles):
    """Inclusive tile rects, one per run of a row (the builder's "floor" format)."""
    out = []
    for z in sorted({t[1] for t in tiles}):
        xs = sorted(x for x, zz in tiles if zz == z)
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1: prev = x; continue
            out.append([start, z, prev, z])
            if x is not None: start = prev = x
    return out

# ------------------------------------------------------------------------------------------------ the ship's tiles
# gTileset_Ship metatile ids (secondary + 0x200) as drawn in Sapphire's ship maps (work/agents/ship_hideouts/labels)
SHIP_BED_L = (0x250, 0x251, 0x258, 0x259)       # bed, 2x2, headboard along the back wall (left-hand cabins)
SHIP_BED_R = (0x254, 0x255, 0x25C, 0x25D)       # the same bed against a right-hand wall
SHIP_TABLE = (0x256, 0x257, 0x25E, 0x25F)       # round table, 2x2
SHIP_DESK = (0x299, 0x29A, 0x2A0, 0x2A2)         # writing desk, 2x2, against the back wall (the hidden floor's cabins;
                                                 # sweep_rooms 2026-10-07: was left out of the floor, a black hole)
SHIP_TRASH = 0x262                               # trash can (MB_TRASH_CAN: "It's empty.")
SHIP_CHAIRS = (0x260, 0x261)                     # chairs Sapphire lets you walk over
SHIP_BUOY = (0x24A, 0x24C)                       # lifebuoy on a cabin's back wall (row 1 of the cabin)
# Sapphire's broken-wall blobs 0x2AA-0x2AD: not floor; inner-wall blocks (ship_room, walkability 2026-10-11)
SHIP_BLOBS = (0x2AA, 0x2AB, 0x2AC, 0x2AD)
SHIP_INNER = dict(top=T(337, 'fs_room8', size=16))   # light-topped inner-wall blocks (models_interior "inner_walls")
SHIP_DOOR_INSIDE = (0x2AE, 0x2AF)                # the dark inside of an open door (walkable but never reached)

ITEM_TEXT = {}                                   # Sapphire's texts and scripts (gen_map_content.ruby_scripts), loaded once

def ship_floor(name, extra=()):
    """Sapphire's walkable tiles + its furniture tiles, minus the inside of open doors."""
    sm = smap(name)
    fl = walkable(name) - set(tiles_with(name, SHIP_DOOR_INSIDE)) - set(doors(name))   # doors: in the wall, not alcoves
    fl |= set(tiles_with(name, SHIP_BED_L + SHIP_BED_R + SHIP_TABLE + SHIP_DESK + (SHIP_TRASH,)))
    return fl | set(map(tuple, extra))

def ship_furniture(name):
    """Black 2 pieces for Sapphire's ship furniture (Royal Unova's own: bed01, table01 at 2x2, dust01, chushion01)."""
    sm = smap(name); out = []
    for x, z in tiles_with(name, (SHIP_BED_L[0], SHIP_BED_R[0])):
        out.append(dict(m='bed01', tiles=[x, z, x + 1, z + 1], wall='N', gap=1, _what='Sapphire bed (2x2)'))
    for x, z in tiles_with(name, (SHIP_TABLE[0],)):
        out.append(dict(m='table01_2x2', tiles=[x, z, x + 1, z + 1], _what='Sapphire round table (2x2)'))
    for x, z in tiles_with(name, (SHIP_DESK[0],)):
        out.append(dict(m='table02_2w', tiles=[x, z, x + 1, z + 1], wall='N', gap=2, _what='Sapphire writing desk (2x2)'))
    for x, z in tiles_with(name, (SHIP_TRASH,)):
        out.append(dict(m='dust01', tile=[x, z], _what='trash can'))
    for x, z in tiles_with(name, SHIP_CHAIRS):
        out.append(dict(m='chushion01', tile=[x, z], _what='Sapphire chair (walkable): a floor cushion, Black 2\'s seat '
                                                          'on walkable tiles'))
    return out

def ship_decals(name, porthole_rows=(0,), buoys=True, lamps=()):
    """Wall pictures: portholes along a corridor's hull wall, lifebuoys on cabin walls, wall lamps."""
    out = []
    # portholes: Sapphire draws them on the hull wall's 0x211 and 0x2b0 tiles (row 1 of a corridor)
    for x, z in tiles_with(name, (0x2B0, 0x211)) if porthole_rows else []:
        out.append(dict(tex='maq_pt01', src=337, at=[x + 0.5], z=z + 1, y=20, w=14, h=14, uv=[0, 0.5, 0.5, 1],
                        _what='porthole (Royal Unova\'s maq_pt01, its porthole quarter)'))
    if buoys:
        for x, z in tiles_with(name, SHIP_BUOY):
            out.append(dict(tex='maq_pt11', src=337, at=[x + 0.5], z=z + 1, y=18, w=13, h=13, uv=[0, 0.5, 0.5, 1],
                            _what='lifebuoy (maq_pt11, its lifebuoy quarter)'))
    for x, z in lamps:
        out.append(dict(tex='maq_rm_lt', src=337, at=[x + 0.5], z=z, y=22, w=14, h=14, _what='wall lamp (chunk 931)'))
    return out

def doors(name):
    """Door tiles of a ship room (Sapphire MB_NON_ANIMATED_DOOR 0x60 / MB_ANIMATED_DOOR 0x69 warps): stairs-like spots
    (solid, walked into northwards) with Royal Unova's cabin door model against the wall in front of them."""
    sm = smap(name); out = []
    for w in sm['warps']:
        x, z = w['x'], w['y']
        if sm['beh'][z][x] in (0x60, 0x69): out.append((x, z))
    return out

def door_models(name, tiles, y=0, face_z=None):
    return [dict(m='cabin_door', tile=[x, z + 1], wall='N', gap=0.5, y=y, lift=False,
                 _what=f'door ({x},{z}): Royal Unova\'s cabin door') for x, z in tiles]

def exit_mats(name):
    """Black 2's door mat (in70_mat1, set 351, as the rooms_cleanup agent gave the Gyms) on every run of Sapphire's
    exit tiles (MB_SOUTH_ARROW_WARP): Sapphire draws a white mat there."""
    sm = smap(name)
    tiles = {(w['x'], w['y']) for w in sm['warps'] if 0 <= w['y'] < sm['h'] and sm['beh'][w['y']][w['x']] == 0x65}
    return [dict(tex='in70_mat1', src=351, border=0.25, border_units=3, y=0, rect=r, _what='exit mat')
            for r in row_rects(tiles)]

# ------------------------------------------------------------------------------------------------ rooms
ROOMS = {}

def ship_room(name, style, **k):
    """A ship room: floor = Sapphire's walkable + furniture tiles (+ extra), furniture from its tiles."""
    sm = smap(name)
    fl = ship_floor(name, k.get('extra_floor', ()))
    fl -= set(map(tuple, k.get('not_floor', ())))
    dr = doors(name)
    stairs = dr + [tuple(t) for t in k.get('stair_tiles', ())]
    recipe = dict(_doc=f'ship_hideouts: {name} (Sapphire {sm["json"]["id"]}) in Black 2\'s Royal Unova (set 337). '
                       f'Generated by b2tools/ship_hideouts_rooms.py; edit that script, not this file.',
                  map=name, style=style, floor=row_rects(fl), stairs=[list(t) for t in stairs],
                  block=[list(t) for t in sorted(set(tiles_with(name, SHIP_DOOR_INSIDE)) & walkable(name))],
                  furniture=ship_furniture(name) + door_models(name, [d for d in dr if d not in k.get('no_door_model', ())])
                  + k.get('furniture', []),
                  decals=ship_decals(name, lamps=k.get('lamps', ())) + k.get('decals', []))
    for key in ('origin', 'mats', 'water', 'open', 'blocks', 'raised', 'ramps', 'floor_tex', 'holes', 'matrix', 'inner_walls'):
        if key in k: recipe[key] = k[key]
    # (walkability 2026-10-11) Sapphire's broken-wall blobs on the cabin and corridor walls (SHIP_BLOBS): left out of the
    # floor, the walls stepped in round each one, a black notch with a full-height wall south of the tile north of it
    # that hid the player's head there (rooms_view m, 'the Abandoned Ship's void gaps between cabins', notes/
    # INTERIORS.md). They are inner-wall blocks now (light top, 16 high next to the walkable floor north of them)
    blobs = set(tiles_with(name, SHIP_BLOBS)) - fl
    if blobs and not (k.get('water') or {}).get('cell'):     # (not the flooded rooms one dives in)
        import models_interior as MI
        iw = dict(recipe.get('inner_walls') or SHIP_INNER)
        auto = set(map(tuple, iw['tiles'])) if 'tiles' in iw else (MI.inner_wall_tiles(name, fl) if 'inner_walls' in recipe else set())
        iw['tiles'] = sorted(map(list, auto | blobs))
        iw['_what'] = f'models_interior.inner_wall_tiles + the broken-wall blobs {sorted(blobs)}'
        recipe['inner_walls'] = iw
    if not recipe['block']: del recipe['block']
    recipe['mats'] = recipe.get('mats', []) + exit_mats(name)
    ROOMS[name] = dict(recipe=recipe, area=SHIP_AREA, kind='ship', **{a: k[a] for a in ('warp_y', 'warp_at', 'header') if a in k})

# ---- the cabins ----------------------------------------------------------------------------------------------
ship_room('AbandonedShip_Rooms_1F', 'sh_cabin')
ship_room('AbandonedShip_Rooms2_1F', 'sh_cabin')
ship_room('AbandonedShip_Rooms_B1F', 'sh_cabin',
          water=dict(tex=T(337, 'd0_miz', size=32), bank=T(337, 'd0_mizgiwa', u_size=16)))
ship_room('AbandonedShip_Rooms2_B1F', 'sh_cabin')
ship_room('AbandonedShip_Room_B1F', 'sh_cabin')

# ---- the corridors: doors in the cabin blocks' faces, stairs down/up at the arrow warps --------------------------
# Corridors 1F: Sapphire's east-arrow tiles (5,2) and (16,2) lead down; the stairs (6,2)/(17,2) are the warp spots
# (sweep_rooms 2026-10-07) the cabin blocks in the corridors and other walls Sapphire draws white (not its black gaps
# between cabins) are light-topped blocks, not walls round a black hole: models_interior "inner_walls"
ship_room('AbandonedShip_Corridors_1F', 'sh_corridor', stair_tiles=[(6, 2), (17, 2)], inner_walls=SHIP_INNER,
          furniture=[dict(m='stair_d01', stair=[6, 2], dir='E', _what='stairs down (Sapphire (5,2) east arrow)'),
                     dict(m='stair_d01', stair=[17, 2], dir='E', _what='stairs down (Sapphire (16,2) east arrow)')],
          warp_at={(5, 2): (6, 2), (16, 2): (17, 2)})
ship_room('AbandonedShip_Corridors_B1F', 'sh_corridor', stair_tiles=[(1, 2), (9, 2)], inner_walls=SHIP_INNER,
          furniture=[dict(m='stair_u01', stair=[1, 2], dir='E', _what='stairs up (Sapphire (0,2) east arrow)'),
                     dict(m='stair_u01', stair=[9, 2], dir='E', _what='stairs up (Sapphire (8,2) east arrow)')],
          warp_at={(0, 2): (1, 2), (8, 2): (9, 2)})
# ---- the captain's office (gTileset_Facility) ---------------------------------------------------------------------
def office():
    name = 'AbandonedShip_CaptainsOffice'
    fl = {(x, z) for x in range(9) for z in range(1, 7)}           # rows 1-6: the back row holds the consoles
    recipe = dict(_doc='ship_hideouts: the captain\'s office (Sapphire MAP_ABANDONED_SHIP_CAPTAINS_OFFICE) in Royal Unova\'s '
                       'cabin look (set 337). Generated by b2tools/ship_hideouts_rooms.py; edit that script, not this file.',
                  map=name, style='sh_office', floor=row_rects(fl), mats=exit_mats(name),
                  furniture=[dict(m='pc01', tiles=[3, 1, 4, 1], wall='N', gap=1, _what='Sapphire console (3-4,1-2)'),
                             dict(m='shelf05', tile=[5, 1], wall='N', gap=1, _what='Sapphire monitor (5-6,1)'),
                             dict(m='shelf04', tile=[6, 1], wall='N', gap=1, _what='Sapphire gadget (6,1)'),
                             dict(m='shelf02', tiles=[7, 1, 8, 1], wall='N', gap=1, _what='Sapphire ship model (7-8,1-2): glass case'),
                             dict(m='desk02', tile=[7, 2], _what='Sapphire ship model\'s stand (7,2)'),
                             dict(m='desk02', tile=[8, 2], _what='Sapphire ship model\'s stand (8,2)'),
                             dict(m='shelf04', tile=[0, 3], wall='W', gap=1, rot=90, _what='Sapphire locker (0,3-4)'),
                             dict(m='shelf04', tile=[0, 4], wall='W', gap=1, rot=90, _what='Sapphire locker (0,3-4)'),
                             dict(m='table01_2x2', tiles=[3, 5, 4, 6], _what='Sapphire chart table (blueprint)')],
                  decals=[])
    recipe['furniture'].append(dict(m='win01', tiles=[0, 1, 2, 1], wall='N', gap=0.5, _what='Sapphire\'s windows (0-2,0-1)'))
    ROOMS[name] = dict(recipe=recipe, area=SHIP_AREA, kind='ship')
office()

# ---- the deck ------------------------------------------------------------------------------------------------------
def deck():
    """The deck on two levels plus the dock (Sapphire draws the ship's superstructure in its 3/4 view; elevation is 3
    everywhere): dock (row 15) at collision 16, the gangway (13-14, 13-14) a ramp up to the lower deck (rows 10-12) at
    48, the stairs (10-11, 8-9) a ramp up to the upper deck (rows 6-7 on the deckhouse roof) at 80; the deckhouse front
    (rows 8-9) with the doors (8,9) and (13,9), the bridge (9-13, 3-5) with the captain's door (12,5). Levels are
    multiples of 16 (script warps, MapChangeCore, place the player in 16-unit levels). Sea = the floor
    (Royal Unova's set's water) at the bottom. Collision is Sapphire's walkability at those heights."""
    name = 'AbandonedShip_Deck'
    W, H = 23, 21
    allt = {(x, z) for x in range(W) for z in range(H)}
    sm = smap(name)
    holes_hi = [t for t in tiles_with(name, (0x3C8,)) if t[1] < 8]
    holes_lo = [t for t in tiles_with(name, (0x3C8,)) if t[1] >= 10]
    gang = {(13, 13), (14, 13), (13, 14), (14, 14)}
    dock = {(13, 15), (14, 15)}
    stairs = {(10, 8), (11, 8), (10, 9), (11, 9)}
    lower = {(x, z) for x in range(W) for z in range(10, 13)} - set(holes_lo)
    upper = {(x, z) for x in range(W) for z in range(0, 10)} - stairs - set(holes_hi)
    bridge = {(x, z) for x in range(9, 14) for z in range(3, 6)}
    upper -= bridge
    blocks = [dict(use='sh_hull', tiles=sorted(map(list, lower)), h=48, _what='lower deck (collision 48), the hull below'),
              dict(use='sh_hull', tiles=sorted(map(list, upper)), h=80, _what='upper deck (80), the deckhouse front below'),
              dict(use='sh_house', tiles=sorted(map(list, bridge)), h=132, _what='the bridge (captain\'s office)'),
              dict(use='sh_hull', tiles=sorted(map(list, dock)), h=16, _what='the dock at the gangway (16)'),
              dict(use='sh_house', tiles=sorted(map(list, holes_lo)), h=47, _what='holes in the lower deck (black, 1 below it)'),
              dict(use='sh_house', tiles=sorted(map(list, holes_hi)), h=79, _what='holes in the upper deck'),
              # Sapphire's railings, funnels and pipes on the upper deck
              dict(use='sh_rail', units=[0, 7.6, 10, 7.85], h=90, _what='railing (0-9,7)'),
              dict(use='sh_rail', units=[0, 3.6, 2, 3.85], h=90, _what='railing (0-1,3)'),
              dict(use='sh_rail', units=[14, 5.6, 23, 5.85], h=90, _what='railing (14-22,5)'),
              dict(use='sh_rail', units=[0, 12.6, 12, 12.85], h=58, _what='railing (0-11,12) at the hull'),
              dict(use='sh_rail', units=[15, 12.6, 23, 12.85], h=58, _what='railing (15-22,12) at the hull'),
              dict(use='sh_funnel', units=[5.1, 0.3, 6.9, 4.9], h=128, _what='funnel (5-6,0-4)'),
              dict(use='sh_funnel', units=[16.1, 1.3, 17.9, 4.9], h=124, _what='funnel (16-17,1-4)'),
              dict(use='sh_funnel', units=[20.1, 2.3, 20.9, 4.9], h=112, _what='funnel (20,2-4)'),
              dict(use='sh_pipe', units=[3.3, 0, 3.7, 7], h=118, _what='pipe (3,0-6)'),
              dict(use='sh_pipe', units=[14.3, 0, 14.7, 7], h=118, _what='pipe (14,0-6)')]
    fl = allt
    recipe = dict(_doc='ship_hideouts: the Abandoned Ship\'s deck (Sapphire MAP_ABANDONED_SHIP_DECK) on two levels in '
                       'Royal Unova\'s art (set 337); see deck() in b2tools/ship_hideouts_rooms.py (generated: edit that '
                       'script, not this file).',
                  map=name, style='sh_deck', floor=row_rects(fl), open=True, mats=exit_mats(name),
                  stairs=[[13, 9], [8, 9], [12, 5]],
                  floor_tex=[dict(rect=[0, 13, 22, 20], tex='d0_miz', src=337, size=32, _what='the sea')],
                  blocks=blocks,
                  raised=[dict(tiles=sorted(map(list, dock)), y=16), dict(tiles=sorted(map(list, lower)), y=48),
                          dict(tiles=sorted(map(list, upper)), y=80)],
                  ramps=[dict(rect=[13, 13, 14, 14], rise='N', y0=16, tex=T(337, 'maq_slope_a', size=32, size_v=16),
                              side=T(337, 'maq_rm05', u_size=32), _what='gangway (Sapphire stairs 13-14,12-15)'),
                         dict(rect=[10, 8, 11, 9], rise='N', y0=48, tex=T(337, 'maq_slope_a', size=32, size_v=16),
                              side=T(337, 'maq_rm05', u_size=32), _what='stairs to the upper deck (10-11,8-9)')],
                  # (sweep_rooms 2026-10-11) the deckhouse front and the bridge stand BACK (12) units north of the deck
                  # in front of them (models_interior.Room.raster: a raised level's edge above a walkable tile more
                  # than FRONT_H lower), as Black 2's walls: at the tile edge they cut the player's body and head along
                  # the decks (rooms_view m up to 177 px). The doors, portholes and lamps on them go with them.
                  furniture=[dict(m='cabin_door', tile=[13, 10], n_edge=10, dz=0.5 - 12, y=46, lift=False, _what='door (13,9)'),
                             dict(m='cabin_door', tile=[8, 10], n_edge=10, dz=0.5 - 12, y=46, lift=False, _what='door (8,9)'),
                             dict(m='cabin_door', tile=[12, 6], n_edge=6, dz=0.5 - 12, y=78, lift=False, _what='captain\'s door (12,5)')],
                  decals=[dict(tex='maq_pt01', src=337, at=[x + 0.5], face_z=10 - 12 / 16, y=58, w=12, h=12, uv=[0, 0.5, 0.5, 1],
                               _what='porthole on the deckhouse front') for x in (4, 6, 16, 18, 20, 22)]
                  + [dict(tex='maq_rm_lt', src=337, at=[x + 0.5], face_z=10 - 12 / 16, y=60, w=12, h=12, _what='lamp')
                     for x in (9, 12)])
    ROOMS[name] = dict(recipe=recipe, area=SHIP_AREA, kind='ship',
                       level={**{f'{x},{z}': 80 for x, z in upper | {(12, 5)}},
                              **{f'{x},{z}': 48 for x, z in lower | {(13, 9), (8, 9)}}, **{f'{x},{z}': 16 for x, z in dock}})
deck()

# ------------------------------------------------------------------------------------------------ the hideouts
# gTileset_Facility metatile ids (secondary + 0x200) of Sapphire's hideout furniture (work/agents/ship_hideouts/labels);
# a non-walkable tile not listed here is wall (the room's outline follows it)
FAC_TANK = {0x288, 0x289, 0x290, 0x291}                          # tank machine (2x2 + its walkable top)
FAC_BIGTANK = {0x23B, 0x23C, 0x23D, 0x23E, 0x243, 0x244, 0x245, 0x246, 0x24B, 0x24C, 0x24D, 0x24E, 0x255, 0x256}
FAC_SERVER = {0x263, 0x264}                                      # foot of a tall machine standing against the wall
FAC_CONSOLE = {0x248, 0x249, 0x24A}                              # 2x1 computer desk (0x248: the left half of Magma
                                                                 # B1F's desk without a computer, (37,18); check_ruby
                                                                 # 2026-10-08: was wall, the right half a desk turned
                                                                 # along z over (38,17)/(38,19))
FAC_TABLE = {0x20C, 0x20D, 0x214, 0x215, 0x3F0, 0x3F1, 0x3F8, 0x3F9}   # 2x2 tables with blueprints (MB_BLUEPRINT)
FAC_TRASH = {0x205}
FAC_DISPLAY = {0x216, 0x217, 0x3EA}                              # ship model / aquarium foot: glass cases
FAC_TV = {0x3C3, 0x3C5, 0x3F3, 0x3F4}
FAC_CRATE = {0x21F, 0x227, 0x22F, 0x237, 0x3DA, 0x3DB, 0x3DC, 0x3DD}
FAC_CHAIR = {0x3E1, 0x3E8}
FAC_RAIL = {0x269, 0x260, 0x268, 0x2A4, 0x2AC, 0x25D, 0x25E, 0x265, 0x266, 0x286, 0x2A6, 0x2AA, 0x295, 0x296, 0x279,
            0x28E, 0x262, 0x26A, 0x297}
FAC_BANK = {0x073, 0x074, 0x075, 0x07B, 0x07C, 0x07D, 0x089, 0x091, 0x276, 0x277, 0x27E, 0x27F, 0x06B, 0x06D, 0x093,
            0x094, 0x09B, 0x09C}                                 # rocky pool banks (Magma: the pit's edges)
FAC_BAND = {0x379, 0x2E3, 0x378, 0x37A}                          # Magma 1F: the terrace walls between walkways
FAC_PAD = 0x2DF                                                  # MB_AQUA_HIDEOUT_WARP
FAC_STOOL = {0x21D, 0x3E9}                                       # walkable stools / chairs
FAC_CARPET = {0x202, 0x203, 0x240, 0x241, 0x242, 0x21D, 0x3E9}   # teal hexagon carpet (0x240: Magma B1F (37,17))
FAC_LAB = {0x3E5, 0x3E6, 0x3ED, 0x3EE, 0x3FB, 0x3FC, 0x3FA, 0x3FD, 0x380, 0x381}
FAC_PIER = {0x29D, 0x2AD}                                        # wooden piers (Aqua 1F)
FAC_STEPS = {0x0AF, 0x0CF}                                       # steps (into the pool / between terraces)
FAC_SAND = {0x071, 0x06C, 0x0BE, 0x0BF}                          # Magma 1F: the dry pit
# wall-mounted machines in the wall row above the floor: a Plasma Frigate panel on the wall over their width
FAC_WALLMACH = {0x230: 'in77q_pc01', 0x231: 'in77q_pc01', 0x232: 'in77q_pc01', 0x223: 'in77meka1', 0x224: 'in77meka1',
                0x21B: 'in77meka1', 0x21C: 'in77meka1', 0x2D4: 'in77meka2', 0x2D5: 'in77meka2', 0x253: 'in77q_meka1',
                0x254: 'in77q_meka1', 0x25B: 'in77q_meka1', 0x25C: 'in77q_meka1', 0x3E3: 'in77g_moni2'}

STYLES.update({
    'hd_aqua': dict(_doc='Aqua Hideout in the Plasma Frigate (set 379): blue-grey deck plates, blue pipe wall',
                    floor=T(379, 'in77s_yuka1', size=32), wall=T(379, 'in77p_kabe1', u_size=32),
                    genkan=T(379, 'in77k_yuka2', size=16), black=T(285, 'black')),
    'hd_magma': dict(_doc='Magma Hideout in the Plasma Frigate (set 379): riveted brown-grey plates, white panel wall',
                     floor=T(379, 'in77k_yuka1', size=32), wall=T(379, 'in77room_02', u_size=64),
                     genkan=T(379, 'in77k_yuka2', size=16), black=T(285, 'black')),
    'hd_rail': dict(top=T(379, 'in77p_pa2', size=16), side=T(379, 'in77q_ami1', u_size=16, v=[0, 1], v_size=16),
                    shade_top=0.9, shade_s=0.9, shade_we=0.7),
    'hd_rim': dict(top=T(379, 'in77p_pa2', size=16), side=T(379, 'in77p_pa2', u_size=16, v=[0, 1], v_size=16),
                   shade_top=0.8, shade_s=0.7, shade_we=0.6),
    'hd_band': dict(top=T(379, 'in77p_pa2', size=16), side=T(379, 'in77i_kabe1', u_size=16, v=[0, 1], v_size=32),
                    shade_top=0.9, shade_s=0.85, shade_we=0.6),
})

def _groups(tiles):
    """4-connected groups of a tile set."""
    tiles = set(tiles); out = []
    while tiles:
        st = [tiles.pop()]; grp = set(st)
        while st:
            x, z = st.pop()
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in tiles: tiles.discard(n); grp.add(n); st.append(n)
        out.append(grp)
    return out

def components(tiles):
    """4-connected groups of tiles -> [(x0, z0, x1, z1)] bounding boxes."""
    tiles = set(tiles); out = []
    while tiles:
        st = [tiles.pop()]; grp = set(st)
        while st:
            x, z = st.pop()
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in tiles: tiles.discard(n); grp.add(n); st.append(n)
        xs = [t[0] for t in grp]; zs = [t[1] for t in grp]
        out.append((min(xs), min(zs), max(xs), max(zs)))
    return sorted(out, key=lambda b: (b[1], b[0]))

def hideout(name, kind, extra_furniture=(), **k):
    """A hideout room: floor = Sapphire's walkable tiles + its furniture, rails, banks and water; Black 2 models for the
    furniture, low rail/rim boxes, water (surf tiles; blocked water drawn), warp panels (Black 2's warp02/warp01 model
    on each MB_AQUA_HIDEOUT_WARP tile + a type-5 warp, as the Plasma Frigate does), doors = stairs spots with a dark
    doorway on the wall, wall machines = Plasma Frigate panels."""
    sm = smap(name); W, H = sm['w'], sm['h']
    mt = lambda x, z: sm['mt'][z][x]
    walk = walkable(name)
    def where(ids): return {(x, z) for z in range(H) for x in range(W) if mt(x, z) in ids and (x, z) not in walk}
    surf = {(x, z) for (x, z) in walk if sm['beh'][z][x] in __import__('models_interior').Room.SURF}
    wsolid = {(x, z) for z in range(H) for x in range(W) if (x, z) not in walk
              and sm['beh'][z][x] in __import__('models_interior').Room.SURF}
    furn = {}
    for key, ids in (('tank', FAC_TANK), ('bigtank', FAC_BIGTANK), ('server', FAC_SERVER), ('console', FAC_CONSOLE),
                     ('table', FAC_TABLE), ('trash', FAC_TRASH), ('display', FAC_DISPLAY), ('tv', FAC_TV),
                     ('crate', FAC_CRATE), ('chair', FAC_CHAIR), ('rail', FAC_RAIL),
                     ('bank', FAC_BANK | set(k.get('banks', ()))),
                     ('band', FAC_BAND if kind == 'magma' else set())):
        furn[key] = where(ids)
    # a wall machine standing free in the room (floor north of it too, e.g. B2F's console between two tanks) is a
    # machine on the floor, not a pillar of wall
    furn['freemach'] = {(x, z) for z in range(1, H) for x in range(W) if (x, z) not in walk and mt(x, z) in FAC_WALLMACH
                        and (x, z - 1) in walk and (x, z + 1) in walk and sm['elev'][z - 1][x] == 3}
    fl = set(walk) | wsolid
    # walkable crumbs Sapphire leaves in its wall art (elevation-0 tiles in Magma B1F's top rows, Aqua B2F (30-32,0)):
    # small groups with no warp and no object are not floor (they can't be reached; their collision stays Sapphire's)
    marks = {(w['x'], w['y']) for w in sm['warps']} | {(o['x'], o['y']) for o in sm['objects']}
    for g in [set(c) for c in _groups(walk)]:
        if len(g) < 6 and not (g & marks): fl -= g
    for v in furn.values(): fl |= v
    # doors: Sapphire's door warps (MB_NON_ANIMATED_DOOR) in the back walls
    dr = [(w['x'], w['y']) for w in sm['warps'] if sm['beh'][w['y']][w['x']] == 0x60]
    fl -= set(dr)
    pads = [(w['x'], w['y']) for w in sm['warps'] if sm['beh'][w['y']][w['x']] == 0x67]
    sapphire_exit = [(w['x'], w['y']) for w in sm['warps'] if sm['beh'][w['y']][w['x']] == 0x6D or
                     (sm['beh'][w['y']][w['x']] in __import__('models_interior').Room.SURF and w['y'] >= H - 4)]
    fl -= set(k.get('not_floor', ()))
    F = []
    def put(m, what, **kw): F.append(dict(m=m, _what=what, **kw))
    def against_wall(x0, z0, x1):
        return all((x, z0 - 1) not in fl for x in range(x0, x1 + 1))
    for b in components(furn['tank']):
        put('machine_l02', 'Sapphire tank machine (2x2)', tiles=list(b))
    for b in components(furn['bigtank']):
        put('machine_l02', 'Sapphire round tank', tiles=list(b), **({'wall': 'N', 'gap': 1} if against_wall(b[0], b[1], b[2]) else {}))
    for x, z in sorted(furn['server']):
        put('machine02', 'Sapphire tall machine (its foot)', tile=[x, z], **({'wall': 'N', 'gap': 1} if against_wall(x, z, x) else {}))
    for x, z in sorted(furn['freemach']): put('machine01', 'Sapphire console standing in the room', tile=[x, z])
    for b in components(furn['console']):       # pcdesk02 runs along its z: turned for a desk 2 tiles wide (sweep_rooms:
        put('pcdesk02_2', 'Sapphire computer desk (2x1)', tiles=list(b), **({'rot': 90} if b[2] > b[0] else {}))   # it lay across 3 rows)
    for b in components(furn['table']):
        put('table01_2x2', 'Sapphire table with a blueprint (2x2)', tiles=list(b))
    for x, z in sorted(furn['trash']): put('dust01', 'trash can', tile=[x, z])
    for b in components(furn['display']):       # Black 2's 2-tile glass cabinet (shelf02) on a 2-wide display
        put('shelf02' if b[2] > b[0] else 'shelf02_1', 'Sapphire display (ship model / aquarium)', tiles=list(b),
            **({'wall': 'N', 'gap': 1} if against_wall(b[0], b[1], b[2]) else {}))
    for b in components(furn['tv']): put('tv01_2w' if b[2] - b[0] == 1 else 'tv01', 'Sapphire TV', tiles=list(b))   # (2 tiles: tv01 is 2.5)
    cr = furn['crate']                          # crates: a box02 stack per 2x2 of crates, from the bottom row up;
    if k.get('crates_as_wall'):                 # a room over Black 2's 32 models per chunk: its crates are wall
        fl -= cr; cr = set()
    for x0, z0, x1, z1 in components(cr):       # a leftover row/column against a wall becomes wall, others d5box01
        for z in range(z1, z0 - 1, -2):         # (Black 2 places at most 32 models per chunk)
            for x in range(x0, x1 + 1, 2):
                blk = {(x, z - 1), (x + 1, z - 1), (x, z), (x + 1, z)}
                if blk <= cr: put('box02', 'Sapphire crates (2x2)', tiles=[x, z - 1, x + 1, z]); continue
                for t in sorted(blk & cr):
                    tx, tz = t
                    walled = (tx, tz - 1) not in fl or (tx - 1, tz) not in fl or (tx + 1, tz) not in fl
                    if walled and (t[0] == x1 or tz == z0): fl.discard(t)
                    else: put('d5box01', 'Sapphire crate', tile=list(t))
    for x, z in sorted(furn['chair']): put('chair01', 'Sapphire chair', tile=[x, z])
    # (Sapphire's walkable stools get no model: B1F would pass Black 2's 32 models per chunk)
    pad_model = 'warp02' if kind == 'aqua' else 'warp01'
    for x, z in pads:                           # 1 up: >= 2 units over a neighbouring crate's shadow (melonDS flicker)
        put(pad_model, 'warp panel (Sapphire MB_AQUA_HIDEOUT_WARP)', tile=[x, z], y=1)
    F += list(extra_furniture)
    blocks = []
    if furn['rail']: blocks.append(dict(use='hd_rail', tiles=sorted(map(list, furn['rail'])), h=12, _what='railings'))
    if furn['bank']: blocks.append(dict(use='hd_rim', tiles=sorted(map(list, furn['bank'])), h=4, _what='pool banks'))
    if furn['band']: blocks.append(dict(use='hd_band', tiles=sorted(map(list, furn['band'])), h=20, _what='terrace walls'))
    ftex = []
    for ids, tex, what in ((FAC_CARPET, T(379, 'in77q_yuka1', size=32), 'carpet'), (FAC_LAB, T(379, 'in77room_01', size=16), 'lab floor'),
                           (FAC_PIER, T(379, 'in77k_yuka3', size=16), 'pier'), (FAC_STEPS, T(379, 'in77_kaidan', size=16), 'steps'),
                           (FAC_SAND, T(379, 'd0yuka_001', size=64), 'dry pit')):
        tl = {t for t in walk if mt(*t) in ids}
        for x0, z, x1, _ in row_rects(tl):
            ftex.append(dict(rect=[x0, z, x1, z], _what=what, **tex))
    # wall panels: runs of wall-mounted machines in the wall row right above the floor
    decals = []
    runs = collections.defaultdict(list)
    for (x, z) in fl:
        if (x, z - 1) not in fl and 0 <= z - 1 and mt(x, z - 1) in FAC_WALLMACH:
            runs[(z, FAC_WALLMACH[mt(x, z - 1)])].append(x)
    for (z, tex), xs in sorted(runs.items()):
        for x0, _, x1, _ in row_rects({(x, z) for x in xs}):
            decals.append(dict(tex=tex, src=379, at=[(x0 + x1 + 1) / 2], z=z, y=6, w=16 * (x1 - x0 + 1) - 2, h=26,
                               _what='wall machine (Plasma Frigate panel)'))
    for x, z in dr:
        decals.append(dict(tex='black', src=285, at=[x + 0.5], z=z + 1, y=-2, w=18, h=34, _what=f'doorway ({x},{z})'))
    style = 'hd_aqua' if kind == 'aqua' else 'hd_magma'
    recipe = dict(_doc=f'ship_hideouts: {name} (Sapphire {sm["json"]["id"]}) in Black 2\'s Plasma Frigate (set 379). '
                       f'Generated by b2tools/ship_hideouts_rooms.py; edit that script, not this file.',
                  map=name, style=style, floor=row_rects(fl), stairs=[list(t) for t in dr],
                  furniture=F, decals=decals)
    if blocks: recipe['blocks'] = blocks
    if ftex: recipe['floor_tex'] = ftex
    if surf or wsolid:
        recipe['water'] = dict(tiles=sorted(map(list, surf)), solid=sorted(map(list, wsolid)), tex=T(379, 'd0_miz', size=32),
                               bank=T(379, 'd0_mizgiwa', u_size=16))
    for key in ('origin', 'matrix'):
        if key in k: recipe[key] = k[key]
    # (emerald_polish_caves 2026-10-12, v16.7) tiles Sapphire's furniture fills but our smaller Black 2 models leave as
    # bare floor (walk_diff OPEN: invisible walls in front of and beside them) are walkable
    if k.get('unblock'): recipe['unblock'] = sorted(map(list, k['unblock']))
    # (sweep_rooms 2026-10-07) Sapphire's thin hideout walls between two corridors/rooms are drawn as light-topped
    # blocks (models_interior "inner_walls"), not walls with Black 2's black cap (black slabs between the floors)
    recipe['inner_walls'] = dict(top=T(379, 'in77room_01', size=16))
    # (check_ruby 2026-10-08) a wall tile where a thin wall meets another one (Magma B1F (18,17)-(18,18): the partition
    # x=18 meets the 2-row wall east of it) has an inner-wall tile, not floor, on one side, so the builder's rule
    # (models_interior.inner_wall_tiles) leaves it black between the light blocks: such tiles join the inner walls
    # (the same rule again with the first pass's tiles counted as floor, as rooms_check_more (h) does). Only rooms that
    # have one get an explicit tile list ("tiles": the builder's own result + these); the others keep the rule.
    import models_interior as MI
    inner = MI.inner_wall_tiles(name, fl)
    extra = set()
    while True:
        more = MI.inner_wall_tiles(name, fl | inner | extra) - inner - extra - fl
        if not more: break
        extra |= more
    if extra:
        recipe['inner_walls']['tiles'] = sorted(map(list, inner | extra))
        recipe['inner_walls']['_what'] = f'models_interior.inner_wall_tiles + the junction tiles {sorted(extra)}'
    level = {f'{x},{z}': -8 for x, z in surf}
    wk = {}
    for i, w in enumerate(sm['warps']):
        t = (w['x'], w['y'])
        if t in pads: wk[i] = dict(type=5, dir=0)
        elif t in surf: wk[i] = dict(type=1, dir=1)        # surf south out of the hideout (MB_WATER_SOUTH_ARROW_WARP)
    ROOMS[name] = dict(recipe=recipe, area=HIDEOUT_AREA, kind=kind, level=level, warp_kind=wk)

hideout('AquaHideout_1F', 'aqua')
# (emerald_polish_caves 2026-10-12, v16.7) B1F's display cases (15-16,8), the TV's stand (18-19,9), the counter (23,8)
# and the round tank's west/south/east rim (29,8-10), (30-31,11), (32,9-10): floor drawn, blocked (walk_diff OPEN 11)
hideout('AquaHideout_B1F', 'aqua', unblock=[(15, 8), (16, 8), (18, 9), (19, 9), (23, 8), (29, 8), (29, 9), (29, 10),
                                            (30, 11), (31, 11), (32, 9), (32, 10)])
hideout('AquaHideout_B2F', 'aqua')
hideout('MagmaHideout_1F', 'magma')
# (check_ruby 2026-10-08) B1F's three rock mounds in the east panel grid (rows 6-8, 10-12, 14-16): their north/south
# edges (0x3E2, 0x26D, 0x26F top, 0x079 front) are banks like their west/east ends (FAC_BANK: 4-unit rims), not
# 16-unit inner-wall blocks whose faces stood 0.97 units from the warp panels' rings (warp01 reaches 3 units into the
# tile south of its panel: melonDS flicker). Only here: Aqua 1F / Magma 1F use 0x26D/0x26F along their south walls.
hideout('MagmaHideout_B1F', 'magma', crates_as_wall=True, banks={0x3E2, 0x26D, 0x26F, 0x079})
hideout('MagmaHideout_B2F', 'magma')
ROOMS['AquaHideout_1F'].update(first=True)
for n in ('AquaHideout_B1F', 'AquaHideout_B2F'): ROOMS[n]['parent'] = 2
ROOMS['MagmaHideout_1F'].update(first=True)
for n in ('MagmaHideout_B1F', 'MagmaHideout_B2F'): ROOMS[n]['parent'] = 228

PLACE = {'ship': 65, 'aqua': 69, 'magma': 91}       # system text 0109 lines (data/hoenn_zones.json places; Ruby's Magma Hideout:
# Emerald's own line 91 "Magma Hideout", in every version since the link work, so a Ruby catch shows its real place
# in Sapphire and Emerald too; Gen 3 Ruby shared Sapphire's line, 69, user 2026-10-18 optional fixes)

# ------------------------------------------------------------------------------------------------ zone files
_door = {}
def door_index():
    """(outdoor map, Sapphire warp id) -> (zone, Black 2 warp index): converter/gen_caves.py's door_index over the world
    of this build (HOENN_WORLD_DIR, else work/world), plus the doors of big rooms world.py appends after every other
    door once their zone json exists (when that world predates them; gyms_league_rooms.door_index's rule)."""
    if _door: return _door
    import narcio, zoneheaders
    from zones import parse_entities
    wd = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    if not os.path.exists(os.path.join(wd, 'world.json')): return _door      # first pass of a build: no world yet
    world = json.load(open(os.path.join(wd, 'world.json')))
    rooms = rooms_registry()
    headers, _ = zoneheaders.load(FILES)
    ents = narcio.load(FILES, 126)
    for zid, z in world['zones'].items():
        base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
        doors = [(d['map'], d['id']) for d in z.get('doors', [])]
        for k, d in enumerate(z.get('doors', [])):
            if d.get('foreign') or (d['map'], d['id']) not in _door: _door[(d['map'], d['id'])] = (int(zid), base + k)
        for d in z.get('slot_doors', []): _door[(d['map'], d['id'])] = (int(zid), d['slot'])
    return _door

def header(name, kind, encounters=None, first=False, parent=None):
    """Zone header fields: the Plasma Frigate room's (TEMPLATE) with the family's music, Sapphire's place name, the
    place banner on the family's first room (Black 2 shows it on a place's first zone only: Strange House 462 / 510),
    parent = that first room's zone (as Black 2's 553 -> 552), the wild table if Sapphire has one."""
    import zoneheaders
    hd, _ = zoneheaders.load(FILES)
    t = hd[TEMPLATE]
    out = {k: t[k] for k in ('map_type', 'npc_cache', 'weather_word', 'flags', 'icon_word')}
    bgm = BGM_SHIP if kind == 'ship' else BGM_HIDEOUT
    out.update(bgm0=bgm, bgm1=bgm, bgm2=bgm, bgm3=bgm, place=PLACE[kind], place_display=1 if first else 0)
    if parent is not None: out['parent'] = parent
    out.update(encounters=encounters if encounters is not None else 0x1FFF, enc_slot=2 if encounters is not None else 6)
    return out

def sapphire_text():
    if 'text' not in ITEM_TEXT:
        from gen_map_content import ruby_scripts
        ITEM_TEXT['text'], ITEM_TEXT['scripts'] = ruby_scripts()
    return ITEM_TEXT['text'], ITEM_TEXT['scripts']

BEHAVIOUR_SIGNS = {0xE4: ('It\'s empty.', 'trash can (Sapphire MB_TRASH_CAN, EventScript_EmptyTrashCan)'),
                   0xE6: ('A blueprint of some sort?\\nIt\'s too complicated!', 'blueprint (MB_BLUEPRINT, EventScript_Blueprint)')}

def objects(name, level):
    """npcs, signs, messages, script blocks and the story list of a room: item balls (global item scripts), simple
    people and signs with one Sapphire message, Sapphire's behaviour messages (trash cans, blueprints) as signs."""
    from gen3text import convert
    from gen_map_content import simple_message
    from gen_interiors import npc_block, sign_block
    text, scripts = sapphire_text()
    sm = smap(name)
    balls = json.load(open(os.path.join(ROOT, 'data', 'hoenn_items.json')))['balls']
    sprites = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
    npcs, signs, msgs, blocks, story = [], [], [], [], []
    ly = lambda x, z: ({'y': level[f'{x},{z}']} if level.get(f'{x},{z}') else {})
    for lid, o in enumerate(sm['objects'], 1):
        g, at = o['graphics_id'], [o['x'], o['y']]
        if g == 'OBJ_EVENT_GFX_ITEM_BALL' and o['script'] in balls:
            b = balls[o['script']]
            npcs.append(dict(uid=lid, model=MODEL_ITEM, script=b['script'], flag=b['flag'], dir=1, at=at,
                             what=f'item ball {b["item"]}', **ly(*at))); continue
        if o.get('trainer_type', 'TRAINER_TYPE_NONE') not in ('TRAINER_TYPE_NONE', '0', 0):
            story.append(f'trainer {g} ({o["x"]},{o["y"]}) {o["script"]}'); continue
        if str(o.get('flag', '0')) not in ('0', ''):
            story.append(f'story object {g} ({o["x"]},{o["y"]}) {o["script"]} hide flag {o["flag"]}'); continue
        code = (sprites.get(g) or {}).get('code')
        label = simple_message(o['script'], text, scripts) if code else None
        if not label or convert(text[label])[1]:
            story.append(f'person {g} ({o["x"]},{o["y"]}) {o["script"]}: not one message / no sprite'); continue
        msgs.append(convert(text[label])[0]); blocks.append(npc_block(len(blocks) + 1, len(msgs) - 1))
        face = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2,
                'MOVEMENT_TYPE_FACE_RIGHT': 3}.get(o['movement_type'], 1)
        n = dict(uid=lid, model=code, script=len(blocks), dir=face, at=at, what=f'{g} {o["script"]}', **ly(*at))
        n.update(MOVE_CODES.room_npc(o))     # Sapphire's movement type as Black 2's code (b2tools/move_codes.py)
        npcs.append(n)
    for b in sm['bgs']:
        if b.get('type') == 'hidden_item':
            story.append(f'hidden item {b["item"]} ({b["x"]},{b["y"]}) {b["flag"]}'); continue
        if b.get('type') != 'sign' or not b.get('script'): continue
        label = simple_message(b['script'], text, scripts)
        if not label or convert(text[label])[1]: story.append(f'sign ({b["x"]},{b["y"]}) {b["script"]}'); continue
        msgs.append(convert(text[label])[0]); blocks.append(sign_block(len(blocks) + 1, len(msgs) - 1))
        signs.append(dict(script=len(blocks), at=[b['x'], b['y']], dir=0 if b.get('player_facing_dir', '').endswith('NORTH') else 4,
                          **ly(b['x'], b['y'])))
    for beh, (line, what) in BEHAVIOUR_SIGNS.items():
        tiles = [(x, z) for z in range(sm['h']) for x in range(sm['w']) if sm['beh'][z][x] == beh and not sm['walk'][z][x]]
        if not tiles: continue
        msgs.append(convert(line)[0]); blocks.append(sign_block(len(blocks) + 1, len(msgs) - 1))
        for x, z in tiles: signs.append(dict(script=len(blocks), at=[x, z], dir=4, what=what, **ly(x, z)))
    for e in sm['coords']:
        story.append(f'coord event ({e["x"]},{e["y"]}) {e.get("script")} var {e.get("var")}={e.get("var_value")}')
    return npcs, signs, msgs, blocks, story

def ruby_only(name):
    return not version.room_in_version(name, 'sapphire')

def out_dir(d, name):
    """d, or its ruby/ overlay for a room only Ruby installs (data/versions.json "rooms")."""
    if not ruby_only(name): return d
    os.makedirs(os.path.join(d, 'ruby'), exist_ok=True)
    return os.path.join(d, 'ruby')

def warps(name, cfg, family):
    """One warp per Sapphire warp event, in Sapphire's order, on its own tile (the builder's spot gives type/dir:
    exit mats type 1, doors/stairs type 2 walked into); arrow stairs use the stair tile (cfg warp_at); heights on
    raised levels (cfg level). A Ruby-only room's exit to an outdoor warp that Ruby plays with another door
    (data/versions.json doors "as_warp": Lilycove's warp 14 is door 6's) leads to that door."""
    rooms = rooms_registry()
    sm = smap(name)
    out, unresolved = [], []
    for i, w in enumerate(sm['warps']):
        dest = re.sub(r'^MAP_', '', w['dest_map']); dw = int(w['dest_warp_id'])
        dest = next((n for n in rooms if rooms[n]['map_id'] == w['dest_map']), None) or \
               next((n for n in _folders() if _folders()[n] == w['dest_map']), dest)
        to = door_index().get(version.door_alias(dest, dw, 'ruby') if ruby_only(name) else (dest, dw))
        if to is None and dest in family: to = (rooms[dest]['zone'], dw)
        what = f'Sapphire warp {i} ({w["x"]},{w["y"]}) -> {dest} {dw}'
        if to is None: unresolved.append(what); to = (rooms[name]['zone'], 0); what += ' (not built: this room\'s warp 0)'
        at = cfg.get('warp_at', {}).get((w['x'], w['y']), (w['x'], w['y']))
        e = dict(at=list(at), tile_only=True, to=list(to), what=what)
        y = cfg.get('level', {}).get(f'{at[0]},{at[1]}')
        if y: e['y'] = y
        e.update(cfg.get('warp_kind', {}).get(i, {}))
        out.append(e)
    return out, unresolved

_fold = {}
def _folders():
    if not _fold:
        base = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps')
        for d in os.listdir(base):
            p = os.path.join(base, d, 'map.json')
            if os.path.exists(p): _fold[d] = json.load(open(p))['id']
    return _fold

def write_room(name, family, report):
    r = ROOMS[name]; reg = rooms_registry()[name]; zone = reg['zone']
    json.dump(r['recipe'], open(os.path.join(LAYOUTS, name + '.json'), 'w'), indent=1)
    level = r.get('level', {})
    npcs, signs, msgs, blocks, story = objects(name, level)
    enc = None
    import gen_caves
    if gen_caves.sapphire_table(name):
        regf = json.load(open(os.path.join(ROOT, 'data', 'hoenn_encounters.json')))
        assert name in regf, f'{name}: no encounter file allocated (gen_caves.py --allocate)'
        enc = gen_caves.encounters(name, zone, dict(regf), report)
    first = r.get('first', False)
    ws, unresolved = warps(name, r, family)
    zj = dict(zone=zone, room=name, area=r['area'],
              header=header(name, r['kind'], enc, first=first, parent=r.get('parent', zone if first else None)),
              warps=ws, npcs=npcs, signs=signs, triggers=r.get('triggers', []),
              scripts=reg['scripts'], init_scripts=reg['init_scripts'], text=reg['text'],
              what=f'ship_hideouts: {name} (b2tools/ship_hideouts_rooms.py); story: ' + ' | '.join(story))
    if not reg.get('own_files'):
        for k in ('scripts', 'init_scripts', 'text'): del zj[k]
    json.dump(zj, open(os.path.join(out_dir(ZONES, name), f'{zone}.json'), 'w'), indent=1, ensure_ascii=False)
    # scripts and text
    sp = os.path.join(out_dir(os.path.join(ROOT, 'src', 'field_scripts'), name), f'{reg["scripts"]:04d}_room_{name}.s')
    extra = r.get('script_blocks', [])
    allb = blocks + extra
    entries = ''.join(f'    ScriptEntry Script_{i}\n' for i in range(1, len(allb) + 1)) or '    ScriptEntry Script_None\n'
    src = (f'// {name} (zone {zone}): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire\'s\n'
           f'// furniture messages. Story scripts: add them after a line "{STORY_MARK}" (this generator keeps everything\n'
           f'// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.\n'
           + (f'// Messages: src/text/script/{"ruby/" if ruby_only(name) else ""}{reg["text"]:04d}_room_{name}.txt\n' if msgs else '')
           + '#include "asm/field_script.inc"\n#include "hoenn.h"\n\n' + entries + '    ScriptEntriesEnd\n\n'
           + ('\n'.join(allb) if allb else 'Script_None:\n    VMHalt\n') + '    .balign 4, 0\n')
    from story_merge import write_room_script, write_room_text      # a story agent's part (after STORY_MARK) stays
    if msgs:
        w = write_room_text(os.path.join(out_dir(os.path.join(ROOT, 'src', 'text', 'script'), name), f'{reg["text"]:04d}_room_{name}.txt'), msgs, sp)
        if w: report.append(w)
    if write_room_script(sp, src) != 'written': report.append(f'{name}: {sp} has story scripts: merged (kept)')
    report.append(f'{name}: zone {zone}, {len(ws)} warps ({len(unresolved)} unresolved), {len(npcs)} objects, '
                  f'{len(signs)} signs, encounters {enc}')
    for u in unresolved: report.append(f'  unresolved: {u}')
    for s in story: report.append(f'  story: {s}')

SHIP = [n for n in ROOMS if n.startswith('AbandonedShip')]
ROOMS['AbandonedShip_Deck'].update(first=True)
for n in SHIP:
    if n != 'AbandonedShip_Deck': ROOMS[n]['parent'] = 74

def main(args):
    if version.is_emerald():           # (Emerald's own hideout rooms: TODO EMERALD-2 in notes/EMERALD.md)
        print('Emerald: no rooms of its own here yet; the shared rooms are a Sapphire run\'s'); return
    magma = '--magma' in args or version.is_ruby()
    names = [a for a in args if not a.startswith('--')] or sorted(ROOMS)
    json.dump(STYLES, open(os.path.join(LAYOUTS, '_styles_ship_hideouts.json'), 'w'), indent=1)
    family = set(ROOMS)
    report = []
    if '--recipes' in args:            # only the room recipes (zone files, scripts and texts left as they are)
        for n in names:
            json.dump(ROOMS[n]['recipe'], open(os.path.join(LAYOUTS, n + '.json'), 'w'), indent=1)
            report.append(f'{n}: recipe')
        print('\n'.join(report)); return
    for n in names:
        if version.is_ruby() and not ruby_only(n):      # Ruby writes only its own rooms (shared ones: a Sapphire run)
            report.append(f'{n}: shared with Sapphire, not written in a Ruby run'); continue
        if n.startswith('MagmaHideout') and not magma:
            json.dump(ROOMS[n]['recipe'], open(os.path.join(LAYOUTS, n + '.json'), 'w'), indent=1)
            report.append(f'{n}: recipe only (zone files with --magma)'); continue
        write_room(n, family, report)
    print('\n'.join(report))

if __name__ == '__main__':
    main(sys.argv[1:])
