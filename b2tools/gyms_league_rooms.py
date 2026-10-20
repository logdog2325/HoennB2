"""gyms_league agent: the eight Gyms, the Elite Four rooms, their corridors and the Champion's room, rebuilt from
Sapphire (notes/INTERIORS.md, notes/INTERIORS_PLAN.md). Writes, for every room of the family:

  data/interior_layouts/<Map>.json        the recipe for b2tools/models_interior.py (no "_auto": ours)
  data/interior_layouts/_styles_gyms_league.json   the texture styles and block styles below
  data/interiors/<zone>.json              zone, room, area, parent, music, warps in Sapphire's order (no "auto": ours)

    python3 gyms_league_rooms.py [Map ...]          (default: all 20)

Shapes, walls, furniture spots, statues and doors follow Sapphire's map (layout, collision, warp events, bg events);
the art is Black 2's: each room uses the Black 2 Gym / Elite Four area whose texture set and building pack fit it
(textures of other Black 2 map texture sets are merged in by the installer). People: the Gym Leaders, Elite Four,
trainers, Gym guides and the statues' plaques (badge checks) are story scripts and wait for the story phase.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
from models_interior import sapphire_map, FILES

LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
ZONES = os.path.join(ROOT, 'data', 'interiors')
BGM_GYM, BGM_LEAGUE = 1062, 1072        # SEQ_BGM_GYM (Aspertia Gym, zone 489), SEQ_BGM_POKEMON_LEAGUE (zones 140-144)

def T(ts, tex, **k): return dict(tex=tex, src=ts, **k)

# ------------------------------------------------------------------------------------------------ styles
STYLES = {
    '_doc': 'gyms_league agent (b2tools/gyms_league_rooms.py writes this file): texture styles of the Gyms and the '
            'Pokemon League rooms (Black 2 map texture sets), and block styles (raised walls, rails, pillars) used by '
            'recipes\' "blocks" via "use".',
    # rooms ------------------------------------------------------------------------------------------------------
    'gl_league': dict(_doc='Ever Grande corridors (Elite Four set 334, Marshal\'s tower): grey frame floor, riveted metal wall',
                      floor=T(334, 'gra_yuka01', size=16), wall=T(334, 'gra_ami04', u_size=32),
                      genkan=T(334, 'gra_iriguti', stretch=True), black=T(285, 'black')),
    'gl_sidney': dict(_doc='Sidney (dark): Grimsley\'s room (set 333): red-brown boards, red curtain wall',
                      floor=T(333, 'c09_04_16', size=32), wall=T(333, 'c09_04_3', u_size=32),
                      genkan=T(333, 'aku_iriguti', stretch=True), black=T(285, 'black')),
    'gl_phoebe': dict(_doc='Phoebe (ghost): Shauntal\'s library (set 315): purple diamond floor, bookshelf wall',
                      floor=T(315, 'gos_yuka01', size=16), wall=T(315, 'gos_book01', u_size=64),
                      genkan=T(315, 'gos_iriguti', stretch=True), black=T(285, 'black')),
    'gl_glacia': dict(_doc='Glacia (ice): Cold Storage ice (set 292): ice floor, ice wall',
                      floor=T(292, 'd5ice_yuka', size=32), wall=T(292, 'd5_kabe', u_size=64),
                      genkan=T(292, 'd5_dyuka01', stretch=True), black=T(285, 'black')),
    'gl_drake': dict(_doc='Drake (dragon): Drayden\'s Opelucid Gym stone (set 312): grey flagstones, dark blue stone wall',
                     floor=T(312, 'sw_gym08_01', size=64), wall=T(312, 'sw_gym08_03', u_size=64),
                     genkan=T(312, 'sw_gym08_02', stretch=True), black=T(285, 'black')),
    'gl_champion': dict(_doc='Champion: Iris\'s room (set 319): beige marble floor, gold frieze wall',
                        floor=T(319, 'in38_tile03', size=64), wall=T(319, 'in38_sode01', u_size=32),
                        genkan=T(319, 'in38_tile05', stretch=True), black=T(285, 'black')),
    'gl_rustboro': dict(_doc='Rustboro (rock): tan cobblestones (exterior set 258), grey rock wall (Driftveil Gym 308)',
                        floor=T(258, 'gake_futa', size=64), wall=T(308, 'in27gake2', u_size=64),
                        genkan=T(258, 'michi01b', stretch=True), black=T(285, 'black')),
    'gl_dewford': dict(_doc='Dewford (fighting, dark): Marshal\'s grey frame floor (set 334)',
                       floor=T(334, 'gra_yuka01', size=16), wall=T(334, 'gra_ami04', u_size=32),
                       genkan=T(334, 'gra_iriguti', stretch=True), black=T(285, 'black')),
    'gl_mauville': dict(_doc='Mauville (electric): Elesa\'s Nimbasa Gym (set 304): white stage floor, striped wall',
                        floor=T(304, 'c4g_stage1', size=16), wall=T(304, 'c4g_kabe02', u_size=16),
                        genkan=T(304, 'c4g_mat', stretch=True), black=T(285, 'black')),
    'gl_lavaridge': dict(_doc='Lavaridge (fire): sand floor (258), Reversal Mountain lava rock (set 388)',
                         floor=T(258, 'out65_zimen1', size=64), wall=T(388, 'in81_gake_g', u_size=32),
                         genkan=T(258, 'michi01b', stretch=True), black=T(285, 'black')),
    'gl_lavaridge_b1': dict(_doc='Lavaridge B1F: darker sand cave', floor=T(388, 'in81_yuka01', size=64),
                            wall=T(388, 'in81_gake_g', u_size=32), genkan=T(258, 'michi01b', stretch=True),
                            black=T(285, 'black')),
    'gl_petalburg': dict(_doc='Petalburg (normal): Aspertia Gym\'s school (set 286): light wood floor, cream panels',
                         floor=T(286, 'in05_yuka2', size=16), wall=T(286, 'in05_sch_ka3', u_size=16),
                         genkan=T(286, 'in05_genkan', stretch=True), black=T(285, 'black')),
    'gl_fortree': dict(_doc='Fortree (flying): Skyla\'s turf (Mistralton Gym 309)', floor=T(309, 'gym06_asiba2', size=16),
                       wall=T(309, 'gym06_kabe2', u_size=32), genkan=T(309, 'gym06_iriguti', stretch=True),
                       black=T(285, 'black')),
    'gl_mossdeep': dict(_doc='Mossdeep (psychic): Caitlin\'s starry floor and white stone (set 335)',
                        floor=T(335, 'esp_hoshi01', size=128), wall=T(335, 'esp_kabe01', u_size=32),
                        genkan=T(335, 'esp_colum1', stretch=True), black=T(285, 'black')),
    'gl_sootopolis': dict(_doc='Sootopolis 1F: beige entrance tiles (Humilau Gym 389, as Sapphire\'s), Cold Storage ice wall (292)',
                          floor=T(389, 'in82_zimen5', size=16), wall=T(292, 'd5_kabe', u_size=64),
                          genkan=T(292, 'd5_yukamat', stretch=True), black=T(285, 'black')),
    'gl_sootopolis_b1': dict(_doc='Sootopolis B1F: Icirrus ice cave (set 311): snow floor, ice cliff wall',
                             floor=T(311, 'in30_yuka02', size=64), wall=T(311, 'ice_gake01', u_size=32),
                             genkan=T(311, 'in30_yuka03', stretch=True), black=T(285, 'black')),
    # blocks -----------------------------------------------------------------------------------------------------
    'gl_rail': dict(_doc='League stair rail (Sapphire\'s orange rails): Marshal\'s blue/orange handrail', h=10,
                    top=T(334, 'gra_tesuri01', size=8), side=T(334, 'gra_tesuri01', u_size=8, v_size=8)),
    'gl_rock': dict(_doc='Rustboro rock walls: brown cliff faces, dirt top (18 high: taller ones crossed the head of a person standing south of them, indoor_check)', h=18,
                    top=T(308, 'in27yuka001', size=64), side=T(308, 'd0gake_001', u_size=16, v_size=16)),
    'gl_rock_low': dict(_doc='Roxanne\'s dais edge', h=8, top=T(258, 'michi01b', size=16),
                        side=T(258, 'gake1_1', u_size=16, v=[0, 1])),
    'gl_dewford_wall': dict(_doc='Dewford maze walls: light frame tops, purple-grey faces', h=16,
                            top=T(334, 'gra_stage04', size=16), side=T(334, 'gra_chu02', u_size=32, v_size=32)),
    'gl_mauville_wall': dict(_doc='Mauville wall blocks (18 high, indoor_check)', h=18, top=T(304, 'c4g_yuka02', size=16),
                             side=T(304, 'c4g_kabe02', u_size=16)),
    'gl_mauville_pole': dict(_doc='Mauville electric poles (Sapphire\'s white coil posts; 20 high, indoor_check)', h=20,
                             top=T(304, 'c4g_stage1', size=16), side=T(304, 'c4g_stage1b', u_size=16, v_size=16)),
    'gl_lava_band': dict(_doc='Lavaridge band walls (Sapphire\'s red zigzag walls)', h=20,
                         top=T(388, 'in81_yuka02', size=16), side=T(388, 'in81_gake_g', u_size=32)),
    'gl_lava_pillar': dict(_doc='Lavaridge yellow pillars', h=24, top=T(388, 'in81_magu02', size=16),
                           side=T(388, 'in81_magu03', u_size=16)),
    'gl_lava_ledge': dict(_doc='Lavaridge B1F ledges', h=6, top=T(388, 'in81_yuka02', size=16),
                          side=T(388, 'in81_gake_g', u_size=32, v=[0, 0.3])),
    'gl_petalburg_wall': dict(_doc='Petalburg room back wall', h=40, top=T(285, 'black'), side=T(286, 'in05_sch_ka3', u_size=16)),
    'gl_fortree_post': dict(_doc='Fortree wooden posts (Sapphire\'s yellow log pillars): Humilau Gym planks (389); 18 high, indoor_check', h=18,
                            top=T(389, 'in82_zimen2', size=32), side=T(389, 'in82_zimen2', u_size=32, v_size=32)),
    'gl_fortree_ledge': dict(_doc='Fortree ledges', h=6, top=T(309, 'gym06_asiba2', size=16),
                             side=T(258, 'gake1_1', u_size=16, v=[0, 1])),
    'gl_mossdeep_wall': dict(_doc='Mossdeep thin white walls', h=14, top=T(335, 'esp_colum1', size=64),
                             side=T(335, 'esp_kabe01', u_size=32, v_size=64)),
    'gl_e4_pillar_sidney': dict(h=44, top=T(285, 'black'), side=T(333, 'aku_kabe01', u_size=32)),
    'gl_e4_pillar_phoebe': dict(h=44, top=T(285, 'black'), side=T(315, 'gos_tana01', u_size=32)),
    'gl_e4_pillar_glacia': dict(h=44, top=T(285, 'black'), side=T(292, 'd5ice_yuka2', u_size=32)),
    'gl_e4_pillar_drake': dict(h=44, top=T(285, 'black'), side=T(312, 'sw_gym08_04', u_size=16)),
    'gl_fountain': dict(_doc='Sootopolis fountain basins: Humilau Gym water', h=8, top=T(389, 'in82_mizu1', size=32),
                        side=T(292, 'd5_kabe', u_size=64, v=[0, 0.2])),
    'gl_ice_cliff': dict(_doc='Sootopolis B1F rock: Icirrus ice cliffs (18 high, indoor_check)', h=18, top=T(311, 'in30_yuka03', size=16),
                         side=T(311, 'ice_gake01', u_size=32)),
    'gl_ice_wall': dict(_doc='Sootopolis inner walls (18 high, indoor_check)', h=18, top=T(292, 'd5_dyuka01', size=32),
                        side=T(292, 'd5_kabe', u_size=64)),
}

# ------------------------------------------------------------------------------------------------ helpers
def walk(name):
    return sapphire_map(name)['walk']

def solid_in(name, rect, skip=()):
    """Solid (non-walkable) tiles of map name inside rect (inclusive), minus skip."""
    w = walk(name); x0, z0, x1, z1 = rect
    return [[x, z] for z in range(z0, z1 + 1) for x in range(x0, x1 + 1) if not w[z][x] and [x, z] not in [list(s) for s in skip]]

def bg(name, kind='sign', script=''):
    j = json.load(open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', name, 'map.json')))
    return [[b['x'], b['y']] for b in j.get('bg_events', []) if b.get('type') == kind and script in str(b.get('script'))]

def beh_tiles(name, behs):
    sm = sapphire_map(name)
    return [[x, z] for z in range(sm['h']) for x in range(sm['w']) if sm['beh'][z][x] in behs]

def statues(name, model='object02_1'):          # object02 at one tile (rooms_cleanup: it reached into the walls)
    """Sapphire's Gym statues (the GymStatue signs) become Black 2 statues on their base tile; a statue whose head
    tile (north of it) is solid in Sapphire stands between the two tiles, as Sapphire draws it."""
    w = walk(name)
    return [dict(m=model, tile=[x, z]) if z == 0 or w[z - 1][x] else dict(m=model, at=[x + 0.5, z]) for x, z in bg(name, script='GymStatue')]

def statue_heads(name):
    w = walk(name)
    return [[x, z - 1] for x, z in bg(name, script='GymStatue') if z > 0 and not w[z - 1][x]]

# ------------------------------------------------------------------------------------------------ warps
_door = {}
def door_index():
    """(outdoor map, Sapphire warp id) -> (zone, Black 2 warp index) as gen_interiors computes it, plus the doors of
    big rooms that world.py appends after all other doors (gyms_league) when work/world predates that."""
    if _door: return _door
    import narcio, zoneheaders
    from zones import parse_entities
    world = json.load(open(os.path.join(os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'), 'world.json')))
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    headers, _ = zoneheaders.load(FILES)
    ents = narcio.load(FILES, 126)
    for zid, z in world['zones'].items():
        base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
        doors = [(d['map'], d['id']) for d in z.get('doors', [])]
        for name, r in sorted(rooms.items(), key=lambda kv: kv[0]):
            if r['status'] != 'big': continue
            for w in r['warps']:
                if w['dest'] in z['maps'] and (w['dest'], w['dest_warp']) not in doors:
                    doors.append((w['dest'], w['dest_warp']))
        for k, d in enumerate(doors):              # a door's copy in the zone of the cell it stands in wins (world.py
            if k < len(z.get('doors', [])) and z['doors'][k].get('foreign') or d not in _door:   # foreign_doors)
                _door[d] = (int(zid), base + k)
    return _door

ARRIVAL_SCRIPT = 10017             # global script (b2tools/patches/hm_free.py Script_18): FadeInBlack on arrival
STEP_ON = (0x68, 0x29, 0x61)       # Lavaridge holes (1F), steam vents (B1F), ladders: fire when stepped on in Sapphire

def warp_kind(name, x, z):
    """Black 2 warp type/dir for a Sapphire warp tile (None: the builder's warp spot decides: exit mats, stairs/doors).
    A walkable tile that Sapphire never fires (behaviour 0: you only arrive there; the room closes behind you) gets
    dir 0, which no move direction matches (ov012 CheckWarpDirectionMatch), so it is an arrival spot only."""
    sm = sapphire_map(name)
    b, ok = sm['beh'][z][x], sm['walk'][z][x]
    if b in (0x65, 0x60): return None
    if b in STEP_ON: return dict(type=2, dir=0)     # an arrival spot; a step trigger does the warp (step_triggers)
    if ok: return dict(type=2, dir=0)
    return dict(type=2, dir=2)         # a door tile in a wall: walk into it northwards

def warps(name, zone):
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    out = []
    for i, w in enumerate(rooms[name]['warps']):
        dest, dw = w['dest'], w['dest_warp']
        to = door_index().get((dest, dw))
        if to is None and dest in rooms:
            st = rooms[dest]['status']
            to = (rooms[dest]['zone'], 0 if st == 'b2' else dw) if st in ('auto', 'big', 'b2', 'hand') else None
        what = f'Sapphire warp {i} -> {dest} {dw}'
        if to is None: to = (zone, 0); what += ' (not built yet: points at this room\'s warp 0)'
        out.append(dict(at=[w['x'], w['y']], tile_only=True, to=list(to), what=what, **(warp_kind(name, w['x'], w['y']) or {})))
    return out

_origins = {}
def origin(name):
    """Zone tile of Sapphire tile (0, 0) in a room (the builder's origin), from its recipe."""
    if name not in _origins:
        from models_interior import Room
        r = Room(name); _origins[name] = (r.ox, r.oz)
    return _origins[name]

def step_triggers(name, zone):
    """Sapphire warps that fire when stepped on (Lavaridge's holes and vents, ladders): Black 2's type-1 warps only fire
    when the player bumps out of them (tested: stepping onto one does nothing), so each becomes a step trigger
    (workId 0 = always, ov012 FindTriggerAtPosGrid) whose script warps to the destination tile (MapChangeCore)."""
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    sm = sapphire_map(name)
    trig, blocks = [], []
    for i, w in enumerate(rooms[name]['warps']):
        if sm['beh'][w['y']][w['x']] not in STEP_ON: continue
        dest = rooms[w['dest']]
        dw = dest['warps'][w['dest_warp']]
        ox, oz = origin(w['dest'])
        blocks.append((f'Sapphire warp {i} ({w["x"]},{w["y"]}) -> {w["dest"]} warp {w["dest_warp"]} ({dw["x"]},{dw["y"]})',
                       dest['zone'], dw['x'] + ox, dw['y'] + oz))
        trig.append(dict(script=len(blocks), var=0, value=0, at=[w['x'], w['y']]))
    return trig, blocks

def write_scripts(name, blocks):
    r = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms'][name]
    # the fade pattern of Black 2's own scripted map changes, with the global arrival script 10017 (hm_free Script_18):
    # without it the arrival zone's people are dead (no talk, no trainer sight; ch5, tested on Lavaridge's holes)
    body = ''.join(f"""Script_{k}:                                      // {what}
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript {ARRIVAL_SCRIPT}                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore {z}, {x}, 0, {y}, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

""" for k, (what, z, x, y) in enumerate(blocks, 1))
    entries = ''.join(f'    ScriptEntry Script_{k}\n' for k in range(1, len(blocks) + 1)) or '    ScriptEntry Script_None\n'
    src = (f'// {name} (zone {r["zone"]}): gyms_league (b2tools/gyms_league_rooms.py): step triggers that warp like '
           f'Sapphire\'s step-on warp tiles.\n// Messages: src/text/script/{r["text"]:04d}_room_{name}.txt\n'
           f'#include "asm/field_script.inc"\n\n{entries}    ScriptEntriesEnd\n\n'
           + (body if blocks else 'Script_None:\n    VMHalt\n') + '    .balign 4, 0\n')
    from story_merge import write_room_script                       # a story agent's part (after "// ---- story") stays
    write_room_script(os.path.join(ROOT, 'src', 'field_scripts', f'{r["scripts"]:04d}_room_{name}.s'), src)

# ------------------------------------------------------------------------------------------------ rooms
ROOMS = {}
GYM_MAT = dict(tex='in70_mat1', src=351, border=0.25, border_units=3, y=0)   # Black 2's door mat (Littleroot's houses)

def exit_mats(name, recipe):
    """Sapphire draws a mat on a Gym's exit tiles (its south-arrow warps): the same mat in Black 2's art (rooms_cleanup)."""
    import models_interior as mi
    sm = mi.sapphire_map(name)
    tiles = sorted((w['x'], w['y']) for w in sm['warps'] if 0 <= w['y'] < sm['h'] and 0 <= w['x'] < sm['w']
                   and sm['beh'][w['y']][w['x']] == mi.MB_SOUTH_ARROW_WARP)
    if not tiles or recipe.get('mats'): return recipe
    xs = [x for x, _ in tiles]
    return dict(recipe, mats=[dict(GYM_MAT, rect=[min(xs), tiles[0][1], max(xs), tiles[0][1]], _what='exit mat (Sapphire\'s Gym entrance mat)')])

def room(name, zone, area, parent, recipe, bgm=BGM_GYM, battle_bg=None, story=(), alts=()):
    """alts: [(recipe name, recipe, map replace event)]: other layouts of the room, installed through the zone's
    "alt_rooms" (b2tools/patches/interiors.py: their chunks on a matrix of their own, loaded instead of the room's while
    the event is set)."""
    if bgm == BGM_GYM: recipe = exit_mats(name, recipe)
    alts = [(n, exit_mats(name, r) if bgm == BGM_GYM else r, e) for n, r, e in alts]
    ROOMS[name] = dict(zone=zone, area=area, parent=parent, recipe=recipe, bgm=bgm, battle_bg=battle_bg, story=list(story),
                       alts=alts)

# ---- Ever Grande: corridors (11x13; Corridor 4 11x34) -------------------------------------------------------
def corridor(name, h):
    last = h - 1
    return dict(_doc=f'gyms_league: Ever Grande corridor ({name}): landing along the back wall with the door (5,2) to the '
                     f'next room, the staircase x 4-6 between rails (x 3 and 7) floating in the dark (Sapphire: dark void '
                     f'with lamps), arrival at its foot (row {last}).',
                map=name, style='gl_league', floor=[[0, 3, 10, 4], [3, 5, 7, last]],
                open=[[0, 5, 2, last], [8, 5, 10, last]],
                floor_tex=[T(334, 'gra_stage04', rect=[0, 3, 10, 4], size=16),
                           T(304, 'c4g_kaidan1', rect=[4, 5, 6, last], size=32, size_v=16),
                           T(334, 'gra_stage01', rect=[3, 5, 3, last], size=32), T(334, 'gra_stage01', rect=[7, 5, 7, last], size=32)],
                blocks=[dict(use='gl_rail', units=[3.35, 5.0, 3.85, last + 1.0]),
                        dict(use='gl_rail', units=[7.15, 5.0, 7.65, last + 1.0])],
                furniture=[dict(m='door_h5_in', tile=[5, 3], wall='N')])

for nm, zn in (('EverGrandeCity_Corridor1', 35), ('EverGrandeCity_Corridor2', 36), ('EverGrandeCity_Corridor3', 42),
               ('EverGrandeCity_Corridor5', 47)):
    room(nm, zn, 334, 412, corridor(nm, 13), bgm=BGM_LEAGUE)
room('EverGrandeCity_Corridor4', 43, 334, 412, corridor('EverGrandeCity_Corridor4', 34), bgm=BGM_LEAGUE)

# ---- Elite Four rooms (13x14) ---------------------------------------------------------------------------------
def e4(name, style, pillar, battle, center, extra=()):
    """Sapphire's Elite Four room: walkable rows 3-11 (pillars x 0-1 / 11-12 at rows 4-8), entrance x 5-7 rows 12-13,
    the door to the next corridor at (6,2) in the back wall; the battle square around the member at (6,5)."""
    return dict(_doc=f'gyms_league: {name}: Sapphire\'s room shape (pillars at the sides, battle square, entrance '
                     f'passage), door to the next corridor on the back wall.',
                map=name, style=style, floor=[[0, 3, 12, 11], [5, 12, 7, 13]],
                floor_tex=[battle, center] + list(extra),
                blocks=[dict(use=pillar, rect=[0, 4, 1, 8]), dict(use=pillar, rect=[11, 4, 12, 8])],
                furniture=[dict(m='door_h5_in', tile=[6, 3], wall='N')])

room('EverGrandeCity_SidneysRoom', 79, 333, 412,
     e4('EverGrandeCity_SidneysRoom', 'gl_sidney', 'gl_e4_pillar_sidney', T(333, 'c09_04_2', rect=[4, 4, 8, 8], size=32),
        T(333, 'c09_04_13', rect=[5, 5, 7, 7], size=32)), bgm=BGM_LEAGUE, battle_bg=13,
     story=['Sidney (6,5): Elite Four battle, then opens the door (6,2) and closes the entrance (setmetatile)'])
room('EverGrandeCity_PhoebesRoom', 123, 315, 412,
     e4('EverGrandeCity_PhoebesRoom', 'gl_phoebe', 'gl_e4_pillar_phoebe', T(315, 'gos_kaidan01', rect=[4, 4, 8, 8], size=32),
        T(315, 'gos_book03', rect=[6, 6, 6, 6], stretch=True)), bgm=BGM_LEAGUE, battle_bg=11,
     story=['Phoebe (6,5): Elite Four battle, door (6,2)'])
room('EverGrandeCity_GlaciasRoom', 53, 292, 412,
     e4('EverGrandeCity_GlaciasRoom', 'gl_glacia', 'gl_e4_pillar_glacia', T(292, 'd5_dyuka01', rect=[4, 4, 8, 8], size=32),
        T(292, 'd5_yukamat', rect=[5, 5, 7, 7], size=8)), bgm=BGM_LEAGUE, battle_bg=14,
     story=['Glacia (6,5): Elite Four battle, door (6,2)'])
room('EverGrandeCity_DrakesRoom', 51, 312, 412,
     e4('EverGrandeCity_DrakesRoom', 'gl_drake', 'gl_e4_pillar_drake', T(312, 'sw_gym08_02', rect=[4, 4, 8, 8], size=64),
        T(312, 'sw_gym08_zou', rect=[5, 5, 7, 7], stretch=True)), bgm=BGM_LEAGUE, battle_bg=12,
     story=['Drake (6,5): Elite Four battle, door (6,2)'])

# ---- Champion (13x13): octagon, stairs up from the entrance -------------------------------------------------
def champion():
    n = 'EverGrandeCity_ChampionsRoom'
    return dict(_doc='gyms_league: the Champion\'s octagonal room (Sapphire\'s walkable octagon rows 3-9), the stairs '
                     'x 5-7 rows 10-12 up from Corridor 4, the door to the Hall of Fame at (6,2).',
                map=n, style='gl_champion', open=[[0, 3, 12, 12]],
                floor=[[5, 3, 7, 3], [4, 4, 8, 4], [3, 5, 9, 5], [2, 6, 10, 7], [3, 8, 9, 8], [4, 9, 8, 9], [5, 10, 7, 12]],
                floor_tex=[T(319, 'in38_kaidan', rect=[5, 10, 7, 12], size=16, size_v=32),
                           T(319, 'in38_yuka2', rect=[5, 5, 7, 7], stretch=True)],
                furniture=[dict(m='door_h5_in', tile=[6, 3], wall='N')])
room('EverGrandeCity_ChampionsRoom', 34, 319, 412, champion(), bgm=BGM_LEAGUE, battle_bg=16,
     story=['Steven (6,5): Champion battle, then the walk to the Hall of Fame (door (6,2))',
            'rival (6,12, FLAG_HIDE_RIVAL_CHAMPIONS_ROOM) and Prof. Birch (6,12, FLAG_HIDE_BIRCH_CHAMPIONS_ROOM): after the battle'])

# ---- Rustboro Gym (11x19) --------------------------------------------------------------------------------------
def rustboro():
    n = 'RustboroCity_Gym'
    st = bg(n, script='GymStatue')
    return dict(_doc='gyms_league: Rustboro Gym: Roxanne\'s sand dais (rows 2-3), the rock walls of Sapphire\'s maze as '
                     'raised rock blocks, two Gym statues by the entrance.',
                map=n, style='gl_rustboro', floor=[[0, 2, 10, 18]],
                floor_tex=[T(258, 'michi01b', rect=[1, 2, 9, 3], size=16)],
                blocks=[dict(use='gl_rock', tiles=solid_in(n, [0, 2, 10, 16], skip=st))],
                furniture=statues(n))
room('RustboroCity_Gym', 583, 308, 113, rustboro(),
     story=['Roxanne (5,2), trainers Josh (7,12) and Tommy (3,7), Gym guide (3,17), statue plaques (2,17)/(8,17)'])

# ---- Dewford Gym (18x28): dark maze -----------------------------------------------------------------------------
def dewford():
    n = 'DewfordTown_Gym'
    sm = sapphire_map(n); w = sm['walk']
    st = bg(n, script='GymStatue') + statue_heads(n)
    walls = []
    for z in range(sm['h']):
        for x in range(sm['w']):
            if w[z][x] or [x, z] in st: continue
            if any(0 <= x + dx < sm['w'] and 0 <= z + dz < sm['h'] and w[z + dz][x + dx]
                   for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
                walls.append([x, z])
    floor = [[x, z, x, z] for z in range(sm['h']) for x in range(sm['w']) if w[z][x] or [x, z] in walls or [x, z] in st]
    return dict(_doc='gyms_league: Dewford Gym: Sapphire\'s maze corridors floating in the dark (no outer walls), '
                     'every wall tile next to a corridor a low wall block; four Gym statues.',
                map=n, style='gl_dewford', floor=floor, open=True,
                blocks=[dict(use='gl_dewford_wall', tiles=walls)], furniture=statues(n))
room('DewfordTown_Gym', 25, 334, 465, dewford(),
     story=['Brawly (14,4), trainers Hideki (2,17), Tessa (1,10), Laura (12,24), Gym guide (5,24), statue plaques',
            'the darkness that lifts as trainers are beaten (Sapphire: flash radius per defeated trainer)'])

# ---- Mauville Gym (10x21) ---------------------------------------------------------------------------------------
# Sapphire redraws the barriers with setmetatile, collision included (field_specials.c MauvilleGymSpecial2: every
# switch swaps green and red beams; MauvilleGymSpecial3: all off once Wattson is beaten), so the room has three layouts:
# the map as drawn, "alt" (Special2 on it: FLAG_MAUVILLE_GYM_BARRIERS_STATE set) and "off" (Special3). Black 2 swaps a
# room's whole matrix with a map replacement (a/0/1/0 kind 1, as Shoal Cave's tides): MauvilleCity_Gym_Alt and
# MauvilleCity_Gym_Off are built like the room with their beams, installed through the zone's "alt_rooms" with map
# replace events 3 (work 0x4034) and 4 (work 0x4035) (data/story_ids.json WORK_MAP_REPLACE_3/4; Black 2's own entries of
# those events patch matrices 9 and 0, which no Hoenn zone uses, and only Unova scripts of replaced zones set them).
# The room's zone init picks the layout (src/field_scripts/0478_room_MauvilleCity_Gym.s MG_SHOW_LAYOUT). story_fixups.
MG_EVENT_ALT, MG_EVENT_OFF = 3, 4
MG_SAPPHIRE = dict(floor=0x21A, gh1_off=0x230, gh1_on=0x220, gh2_off=0x231, gh2_on=0x221, gh3_off=0x238, gh3_on=0x228,
                   gh4_off=0x239, gh4_on=0x229, gv1_on=0x240, gv2_on=0x248, pb_off=0x243, pb_on=0x242, pt_off=0x251,
                   pt_on=0x250, rh1_off=0x232, rh1_on=0x222, rh2_off=0x233, rh2_on=0x223, rh3_off=0x23A, rh3_on=0x22A,
                   rh4_off=0x23B, rh4_on=0x22B, rv1_on=0x241, rv2_on=0x249)

def mauville_states():
    """{state: {(x, z): solid}} of Sapphire's barrier tiles (map tiles; the specials' loops cover x 0-8, z 5-16, in the
    map's order, tile changes seen by later tiles as in Sapphire): 'normal', 'alt', 'off'."""
    from gba import Repo
    M = MG_SAPPHIRE
    repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    g, _ = repo.layout_grid(repo.map_json('MauvilleCity_Gym')['layout'])
    t0 = {(x, z): (int(g[z, x]) & 0x3FF, (int(g[z, x]) >> 10) & 3 != 0) for z in range(g.shape[0]) for x in range(g.shape[1])}
    def run(t, table, floor_rule):
        t = dict(t)
        for z in range(5, 17):
            for x in range(0, 9):
                m = t[(x, z)][0]
                if floor_rule and m == M['floor']:
                    t[(x, z)] = (M['gv2_on'], True) if t[(x, z - 1)][0] == M['gv1_on'] else (M['rv2_on'], True)
                elif m in table: t[(x, z)] = table[m]
        return t
    off = lambda k: (M[k], False)
    on = lambda k: (M[k], True)
    special3 = {M[c + 'h%d_on' % i]: off(c + 'h%d_off' % i) for c in 'gr' for i in (1, 2, 3, 4)}
    special3.update({M['gv1_on']: on('pb_on'), M['rv1_on']: on('pb_off'), M['gv2_on']: off('floor'),
                     M['rv2_on']: off('floor'), M['pt_on']: off('pt_off')})
    special2 = dict(special3)
    special2.update({M[c + 'h%d_off' % i]: (on if i > 2 else off)(c + 'h%d_on' % i) for c in 'gr' for i in (1, 2, 3, 4)})
    special2.update({M['pb_on']: on('gv1_on'), M['pb_off']: on('rv1_on'), M['pt_off']: on('pt_on')})
    states = dict(normal=t0, alt=run(t0, special2, True), off=run(t0, special3, False))
    return {k: {xz: v[1] for xz, v in t.items()} for k, t in states.items()}

MG_SWITCHES = [(0, 9), (8, 11), (4, 15)]      # Sapphire's switch tiles (0478 script entries 5-7)
def mauville(state='normal'):
    n = 'MauvilleCity_Gym'
    st = mauville_states()
    toggles = sorted((xz for xz in st['normal'] if len({st[k][xz] for k in st}) > 1), key=lambda t: (t[1], t[0]))   # tiles whose collision changes (row by row)
    poles = [[3, 2], [4, 2], [5, 2], [6, 2], [3, 8], [6, 8], [3, 11], [6, 11], [0, 11], [3, 14], [6, 14]]
    beams = [[x, z] for x, z in toggles if st[state][(x, z)]]          # normal: (4,8) (5,8) (3,9) (3,10) (6,12) (6,13) (4,14) (5,14)
    walls = [t for t in solid_in(n, [0, 8, 9, 17]) if t not in poles and tuple(t) not in toggles]
    r = dict(_doc='gyms_league: Mauville Gym: Sapphire\'s cross-shaped room, electric poles (the four along the '
                  'back wall and the barrier posts), the barrier tiles as Black 2 electric floor (Chargestone '
                  'Cave\'s), grey wall blocks; two Gym statues.',
             map=n, style='gl_mauville', floor=[[3, 2, 6, 7], [0, 8, 9, 17], [2, 18, 7, 20]],
             blocks=[dict(use='gl_mauville_pole', units=[x + 0.25, z + 0.3, x + 0.75, z + 0.8]) for x, z in poles] +
                    [dict(use='gl_mauville_wall', tiles=walls)],
             furniture=[dict(m='d6_yuka_biri02_1', tile=t) for t in beams] + statues(n),   # one tile (rooms_cleanup)
             # the floor switches, drawn with Sapphire's own switch metatile (they were invisible: user report 2026-10-14)
             floor_tex=[dict(tex=f'g3sw_{x}_{z}', gen3=[x, z], rect=[x, z, x, z], stretch=True) for x, z in MG_SWITCHES])
    if state != 'normal':
        r['_doc'] += (f' Layout "{state}" (story_fixups): Sapphire\'s MauvilleGymSpecial' + ('2 (every switch swaps the '
                      'beams)' if state == 'alt' else '3 (every beam off: Wattson beaten)') + ', loaded instead of the room '
                      'by map replace event ' + str(MG_EVENT_ALT if state == 'alt' else MG_EVENT_OFF) + '.')
        r['alt_of'] = n
        blk = [[x, z] for x, z in toggles if st[state][(x, z)] and not st['normal'][(x, z)]]
        unb = [[x, z] for x, z in toggles if not st[state][(x, z)] and st['normal'][(x, z)]]
        if blk: r['block'] = blk
        if unb: r['unblock'] = unb
    return r
room('MauvilleCity_Gym', 239, 304, 406, mauville(),
     story=['Wattson (4,3, FLAG_HIDE_WATTSON_MAUVILLE_GYM), trainers Shawn, Vivian, Ben, Kirk, Gym guide (7,20), plaques',
            'the barrier switches: stepping on a switch swaps the barriers (Sapphire setmetatile + collision)'],
     alts=[('MauvilleCity_Gym_Alt', mauville('alt'), MG_EVENT_ALT), ('MauvilleCity_Gym_Off', mauville('off'), MG_EVENT_OFF)])

# ---- Lavaridge Gym 1F / B1F (11x24) ----------------------------------------------------------------------------
HOLE = T(388, 'in81_ana02', stretch=True)
def lavaridge_1f():
    n = 'LavaridgeTown_Gym_1F'
    holes = beh_tiles(n, (0x68,))
    pillar = [[5, z] for z in range(1, 24) if [5, z] not in ([5, 7], [5, 15])]
    return dict(_doc='gyms_league: Lavaridge Gym 1F: three bands of sand behind red-rock walls (rows 7 and 15), the '
                     'pillar x 5, the sand holes you drop through (Sapphire\'s 0x68 warp tiles) as dark holes; statues.',
                map=n, style='gl_lavaridge', floor=[[0, 1, 10, 23]],
                floor_tex=[dict(HOLE, rect=[x, z, x, z]) for x, z in holes],
                blocks=[dict(use='gl_lava_band', rect=[0, 7, 10, 7]), dict(use='gl_lava_band', rect=[0, 15, 10, 15]),
                        dict(use='gl_lava_pillar', units=[5.2, 1.0, 5.8, 7.0]), dict(use='gl_lava_pillar', units=[5.2, 8.0, 5.8, 15.0]),
                        dict(use='gl_lava_pillar', units=[5.2, 16.0, 5.8, 24.0])],
                furniture=statues(n))
def lavaridge_b1f():
    n = 'LavaridgeTown_Gym_B1F'
    jets = beh_tiles(n, (0x29,))
    ledges = beh_tiles(n, (0x3B,))
    return dict(_doc='gyms_league: Lavaridge Gym B1F: sand cave under 1F, rock walls (row 4, columns x 2/5/8, row 19), '
                     'Sapphire\'s ledges (rows 12 and 19, jumped down), the steam vents that blow you back up (0x29).',
                map=n, style='gl_lavaridge', floor=[[0, 1, 10, 23]], ledges=True,
                floor_tex=[T(388, 'in81_magu06', rect=[x, z, x, z], stretch=True) for x, z in jets],
                blocks=[dict(use='gl_lava_band', tiles=[t for t in solid_in(n, [0, 4, 10, 19]) if t not in ledges]),
                        dict(use='gl_lava_ledge', tiles=ledges)])
room('LavaridgeTown_Gym_1F', 145, 388, 62, lavaridge_1f(),
     story=['Flannery (8,10), buried trainers Cole, Zane, Axle, Sadie, Andy (TRAINER_TYPE_BURIED: pop out of the sand), '
            'Gym guide (6,23), statue plaques (6,17)/(10,17)',
            'falling through the holes (Sapphire: fall animation; here plain warps)'])
room('LavaridgeTown_Gym_B1F', 148, 388, 62, lavaridge_b1f(),
     story=['the steam jets that throw you up to 1F (Sapphire: jet animation; here plain warps on the vent tiles)'])

# ---- Petalburg Gym (9x112, four chunks): nine rooms ------------------------------------------------------------
PETAL_ROOMS = [2, 15, 28, 41, 54, 67, 80, 93, 106]      # first floor row of each room (6 rows each)
def petalburg():
    n = 'PetalburgCity_Gym'
    sm = sapphire_map(n)
    doors = [[w['x'], w['y']] for w in sm['warps'] if not sm['walk'][w['y']][w['x']]]
    mats = [T(286, 'in05_mat2', rect=[1, r + 1, 7, r + 4], size=16) for r in PETAL_ROOMS[1:-1]]
    return dict(_doc='gyms_league: Petalburg Gym: Sapphire\'s nine rooms stacked in one tall map (1x4 chunks): each room '
                     'six rows of wood floor with a training mat, the doors to the next rooms on its back wall '
                     '(Sapphire\'s door tiles), Norman\'s room on top, two statues in the entrance room.',
                map=n, style='gl_petalburg', floor=[[0, r, 8, r + 5] for r in PETAL_ROOMS],
                floor_tex=mats + [T(286, 'in05_mat1', rect=[3, 4, 5, 6], stretch=True)],
                furniture=[dict(m='door_pwood01', tile=[x, z + 1], wall='N') for x, z in doors] + statues(n))
room('PetalburgCity_Gym', 452, 286, 439, petalburg(),
     story=['Norman (4,3), the six trainers (4,16/29/42/55/68/81/94), Wally\'s tutorial and Norman\'s first talk '
            '(VAR_PETALBURG_GYM_STATE), Gym guide (3,109), statue plaques',
            'the doors open only after the room\'s trainer is beaten (Sapphire: setmetatile to MB_PETALBURG_GYM_DOOR); '
            'here every door is open'])

# ---- Fortree Gym (20x25) --------------------------------------------------------------------------------------
def fortree():
    n = 'FortreeCity_Gym'
    st = bg(n, script='GymStatue')
    ledges = beh_tiles(n, (0x3B,))
    posts = [t for t in solid_in(n, [0, 1, 19, 23], skip=st) if t not in ledges]
    return dict(_doc='gyms_league: Fortree Gym: Sapphire\'s grass paths between the wooden posts (every solid tile a '
                     'post block), the ledges of the left lane (rows 9/13/17, jumped down), Winona\'s nook top-left; statues.',
                map=n, style='gl_fortree', floor=[[0, 1, 19, 24]], ledges=True,
                blocks=[dict(use='gl_fortree_post', tiles=posts), dict(use='gl_fortree_ledge', tiles=ledges)],
                furniture=statues(n))
room('FortreeCity_Gym', 119, 309, 16, fortree(),
     story=['Winona (4,1), trainers Jared, Terrell, Kylee, Will, Gym guide (2,19), statue plaques',
            'the rotating gates (Gen 3 rotating_gate.c): b2tools/patches/rotating_gates.c (zone 119) + the arm actors of '
            'data/story/fortree_gates.json (fortree_gates 2026-10-20)'])

# ---- Mossdeep Gym (20x30) -------------------------------------------------------------------------------------
def mossdeep():
    n = 'MossdeepCity_Gym'
    sm = sapphire_map(n)
    st = bg(n)                                    # statues and the four switches stand on solid tiles: no wall there
    arrows = {0x44: 0, 0x40: 0, 0x45: 180, 0x41: 180, 0x46: 270, 0x42: 270, 0x47: 90, 0x43: 90}   # east west north south
    ft = []
    for z in range(sm['h']):
        for x in range(sm['w']):
            b = sm['beh'][z][x]
            if b in arrows: ft.append(T(258, 'out_65_dai2', rect=[x, z, x, z], stretch=True, rot=arrows[b]))
            elif b == 0x48: ft.append(T(304, 'c4g_mat', rect=[x, z, x, z], stretch=True))
            elif b == 0x67: ft.append(T(334, 'gra_light02', rect=[x, z, x, z], stretch=True))   # Sapphire's pad (12,3)
    walls = solid_in(n, [0, 2, 19, 28], skip=st)
    return dict(_doc='gyms_league: Mossdeep Gym: Sapphire\'s maze of thin white walls on the starry floor, the spin '
                     'tiles (MB_WALK/SLIDE_*) as arrows, the stop tiles, the warp pad (12,3); statues.',
                map=n, style='gl_mossdeep', floor=[[0, 2, 19, 29]], floor_tex=ft,
                blocks=[dict(use='gl_mossdeep_wall', tiles=walls)],
                furniture=statues(n) + [dict(m='machine02', tile=t) for t in bg(n, script='Switch')])
room('MossdeepCity_Gym', 322, 335, 107, mossdeep(),
     story=['Tate & Liza (8,3)/(9,3), trainers Preston, Fritz, Maura, Samantha, Virgil, Hannah, Gym guide (8,29), plaques',
            'the spin tiles (Sapphire MB_WALK_*/MB_SLIDE_*: forced movement until a stop tile) and the four switches '
            '(2,7)/(8,10)/(17,15)/(5,24) that turn them: Black 2 has no such tile class, needs scripts or code'])

# ---- Sootopolis Gym 1F / B1F (17x26) ---------------------------------------------------------------------------
SOOTO_ROOMS = [[3, 6, 13, 9], [5, 12, 11, 14], [7, 17, 9, 19]]
SOOTO_LINKS = [[8, 4, 8, 5], [8, 10, 8, 11], [8, 15, 8, 16], [8, 20, 8, 21]]
def sootopolis_1f():
    n = 'SootopolisCity_Gym_1F'
    ice = beh_tiles(n, (0x26, 0x27))
    rocks = [t for r in SOOTO_ROOMS for t in solid_in(n, r)]
    stat = [list(t) for t in bg(n, script='GymStatue')]      # (sweep_rooms) no ice block under the statues: their sides
    walls = [t for t in solid_in(n, [3, 2, 13, 25]) if t not in rocks and t[1] > 2 and t not in stat]   # flickered on it
    return dict(_doc='gyms_league: Sootopolis Gym 1F: entrance hall (rows 22-25) with statues and the ladder down '
                     '(11,22), the three ice rooms (Sapphire\'s thin ice) linked by ice ramps, Wallace\'s dais between '
                     'the two fountains at the top (rows 2-3); the thick walls between the rooms are raised ice blocks '
                     '(tall room walls there would hide the player in the room behind).',
                map=n, style='gl_sootopolis', floor=[[3, 2, 13, 25]],
                floor_tex=[T(292, 'd5ice_yuka', rect=[x, z, x, z], size=32) for x, z in ice] +
                          [T(292, 'd5ice_yuka2', rect=r, size=32) for r in SOOTO_LINKS[:3]] +
                          [T(292, 'd5kaidan1', rect=SOOTO_LINKS[3], size=16), T(315, 'gos_hasigo01', rect=[11, 22, 11, 22], stretch=True)],
                blocks=[dict(use='gl_fountain', rect=[4, 2, 6, 2]), dict(use='gl_fountain', rect=[10, 2, 12, 2]),
                        dict(use='gl_ice_wall', tiles=walls)],
                decals=[T(389, 'in82_hunsui1', at=[5.0], y=6, w=32, h=42, gap=2), T(389, 'in82_hunsui1', at=[12.0], y=6, w=32, h=42, gap=2)],
                furniture=[dict(m='d6stone02', tile=t) for t in rocks] + statues(n))
def sootopolis_b1f():
    n = 'SootopolisCity_Gym_B1F'
    return dict(_doc='gyms_league: Sootopolis Gym B1F: the snowy ice cave under the ice rooms (same room shapes as 1F, '
                     'the rock between them raised ice-cliff blocks), the ladder up at (11,22).',
                map=n, style='gl_sootopolis_b1', floor=[[3, 6, 13, 25]],
                floor_tex=[T(292, 'd5ice_yuka2', rect=r, size=32) for r in SOOTO_LINKS] +
                          [T(315, 'gos_hasigo01', rect=[11, 22, 11, 22], stretch=True)],
                blocks=[dict(use='gl_ice_cliff', tiles=solid_in(n, [3, 6, 13, 25]))])
room('SootopolisCity_Gym_1F', 23, 292, 319, sootopolis_1f(),
     story=['Wallace (8,2, FLAG_HIDE_WALLACE_SOOTOPOLIS_GYM), Gym guide (7,24), statue plaques (6,24)/(10,24)',
            'the thin ice (MB_THIN_ICE -> MB_CRACKED_ICE -> hole: you fall to B1F) and the sliding ice ramps (MB_SLIDE_SOUTH)',
            'the exit: Sootopolis City is not built yet (its warp points back at this room)'])
room('SootopolisCity_Gym_B1F', 24, 292, 319, sootopolis_b1f(),
     story=['trainers Andrea, Connie, Brianna, Bridget, Tiffany, Marissa, Crissy, Olivia'])

# ------------------------------------------------------------------------------------------------ write
def write(name):
    r = ROOMS[name]
    json.dump(r['recipe'], open(os.path.join(LAYOUTS, name + '.json'), 'w'), indent=1)
    for an, ar, _ in r['alts']: json.dump(ar, open(os.path.join(LAYOUTS, an + '.json'), 'w'), indent=1)
    zj = dict(zone=r['zone'], room=name, area=r['area'], bgm=r['bgm'],
              what=f'gyms_league: {name} (b2tools/gyms_league_rooms.py); story phase: ' + ' | '.join(r['story']))
    if r['parent'] is not None: zj['parent'] = r['parent']
    if r['battle_bg'] is not None: zj['battle_bg'] = r['battle_bg']
    trig, blocks = step_triggers(name, r['zone'])
    zj.update(warps=warps(name, r['zone']), npcs=[], signs=[], triggers=trig)
    if r['alts']: zj['alt_rooms'] = [dict(room=an, event=e) for an, _, e in r['alts']]
    json.dump(zj, open(os.path.join(ZONES, f'{r["zone"]}.json'), 'w'), indent=1, ensure_ascii=False)
    if blocks: write_scripts(name, blocks)

if __name__ == '__main__':
    json.dump(STYLES, open(os.path.join(LAYOUTS, '_styles_gyms_league.json'), 'w'), indent=1)
    for n in [a for a in sys.argv[1:] if not a.startswith('--')] or sorted(ROOMS):
        if '--recipes' in sys.argv:       # only the recipes (and their other layouts); zone jsons and scripts as they are
            json.dump(ROOMS[n]['recipe'], open(os.path.join(LAYOUTS, n + '.json'), 'w'), indent=1)
            for an, ar, _ in ROOMS[n]['alts']: json.dump(ar, open(os.path.join(LAYOUTS, an + '.json'), 'w'), indent=1)
            print(n, 'recipe'); continue
        write(n)
        print(n, ROOMS[n]['zone'], 'area', ROOMS[n]['area'])
