"""Emerald's changed rooms (emerald_rooms, 2026-10-12; notes/EMERALD.md "Rooms (emerald_rooms)").

    python3 emerald_rooms.py            write every Emerald room variant below (rerun after editing this file)
    python3 emerald_rooms.py --check    only say what would change

Emerald redraws some of the rooms Sapphire and Ruby share (data/versions.json maps.emerald.ground). Each one here gets an
Emerald variant built from pokeemerald's own map: a recipe data/interior_layouts/<Room>_Emerald.json whose "map" is
"pokeemerald/<Emerald folder>" (models_interior.map_source), installed instead of the Sapphire room in an Emerald build
only (data/versions.json room_variants.emerald; the variant itself is listed in "rooms" as Emerald's, so Sapphire's and
Ruby's builds and checkers never see it). Other layouts of a room (the Lab's table) are "alt_rooms" of the zone in the
Emerald overlay of its zone json (data/interiors/emerald/<zone>.json), loaded by a map replace event.

People, signs and warps: a variant keeps the Sapphire room's origin (zone tile = map tile + origin) where Emerald's
content stands where Sapphire's does, so the zone json, the story objects and the scripts' tiles stay right. Where
Emerald moved something, this script writes the Emerald overlay of the zone json (positions in Emerald's map tiles) and
"at_emerald" on the story objects it moves (patches/story.py version_keys); Sapphire never reads either.

Writes (all Emerald-only):
  data/interior_layouts/<Room>_Emerald*.json      the variants' recipes
  data/interiors/emerald/<zone>.json              zone jsons whose people/warps Emerald moves, and the Lab's alt room
  data/versions.json                              room_variants.emerald and rooms (the variants: "emerald")
"""
import os, sys, json, copy, argparse, re

os.environ['HOENN_VERSION'] = 'emerald'     # (this script writes Emerald's files only; version.load_json reads Emerald's overlays)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'converter')); sys.path.insert(0, os.path.join(HERE, 'patches'))
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
ZONES = os.path.join(ROOT, 'data', 'interiors')
EM = 'pokeemerald/'
DOC = 'emerald_rooms (b2tools/emerald_rooms.py writes this file: edit the script and rerun). '

def recipe(name):
    return json.load(open(os.path.join(LAYOUTS, name + '.json')))

def zone_json(zone):
    return json.load(open(os.path.join(ZONES, f'{zone}.json')))

def emerald_folder(name):
    import version
    return version.decomp_map(name, 'emerald')

def at_tile(f):
    """The Sapphire tile a furniture entry is keyed by (tile, first tile of tiles, stair, or the floor of at)."""
    if 'tile' in f: return tuple(f['tile'])
    if 'tiles' in f: return tuple(f['tiles'][:2])
    if 'stair' in f: return tuple(f['stair'])
    if 'at' in f: return (int(f['at'][0]), int(f['at'][1]))
    return None

def drop(r, tiles, model=None):
    """Remove the furniture keyed at these tiles (optionally only of that model)."""
    tiles = {tuple(t) for t in tiles}
    n = len(r['furniture'])
    r['furniture'] = [f for f in r['furniture'] if not (at_tile(f) in tiles and (model is None or f.get('m') == model))]
    assert len(r['furniture']) < n, (r.get('map'), tiles, model)
    return r

def variant(base, doc, **edits):
    """The Emerald recipe of Sapphire room `base`: its recipe on pokeemerald's map, with edits."""
    r = copy.deepcopy(recipe(base))
    r['_doc'] = DOC + doc + ' Sapphire recipe: ' + base + '.json. ' + r.get('_doc', '')
    r['map'] = EM + emerald_folder(base)
    r.update(edits)
    return r

# ------------------------------------------------------------------------------------------------ the rooms
OUT = {}            # recipe name -> recipe
VARIANTS = {}       # Sapphire room -> Emerald variant
OVERLAYS = {}       # zone -> zone json (Emerald overlay)

# ---- Prof. Birch's Lab (13x13, zone 396) ---------------------------------------------------------------------------
# pokeemerald LAYOUT_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB: Sapphire's two chairs (12,2) (12,3) facing west and the
# side table (12,4) are three chairs facing south at (11,2) (12,2) (12,3) ((11,2) solid, (12,4) walkable).
# LAYOUT_..._WITH_TABLE (the Johto starters, states >= 4): the boxes (9,3)-(10,4) are gone, a white table stands on
# (8,4)-(10,4) (all three solid) with the three Poke Balls on it.
LAB = 'LittlerootTown_ProfessorBirchsLab'
LAB_EVENT = 4       # map replace event 4 (work 0x4035), shared with Mauville Gym's "barriers off" layout: both rooms set
                    # it on every load (MG_SHOW_LAYOUT; EM_LabJohtoInit), and each of them is the only zone of its matrix
def lab():
    r = variant(LAB, "Emerald's Lab: three chairs facing south at (11,2) (12,2) (12,3), no side table at (12,4).")
    drop(r, [(12, 2), (12, 3), (12, 4)])
    r['furniture'] += [dict(m='chair01', tile=[x, z], _what="chair (Emerald's, facing south)") for x, z in ((11, 2), (12, 2), (12, 3))]
    OUT[LAB + '_Emerald'] = r
    t = copy.deepcopy(r)
    t['_doc'] = (DOC + "Emerald's Lab with the table for the Johto starters (LAYOUT_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB_"
                 "WITH_TABLE): the boxes at (9,4) (10,4) gone, a low table on (8,4)-(10,4) whose top the three Poke Balls "
                 f"stand on (solid_y). Loaded instead of {LAB}_Emerald while map replace event {LAB_EVENT} is set "
                 "(scenes/emerald/BirchLab_JohtoStarters.inc EM_LabJohtoInit: states >= 4).")
    t['alt_of'] = LAB
    drop(t, [(9, 4), (10, 4)], 'box02_1')
    t['furniture'].append(dict(m='desk01', at=[9.5, 4.5], rot=90, _what="Emerald's table for the Johto starters' balls (8-10,4)"))
    t['block'] = t.get('block', []) + [[8, 4]]
    t['solid_y'] = [dict(y=11, tiles=[[8, 4], [9, 4], [10, 4]], _what="the three balls stand on the table (desk01, top 11)")]
    OUT[LAB + '_Emerald_Table'] = t
    VARIANTS[LAB] = LAB + '_Emerald'
    z = zone_json(396)
    z['_doc'] = (DOC + "Emerald's overlay of 396.json (same people, signs and warps): the Lab's table layout as an alt "
                 "room. " + z.get('_doc', ''))
    z['alt_rooms'] = [dict(room=LAB + '_Emerald_Table', event=LAB_EVENT)]
    OVERLAYS[396] = z

lab()

# ---- small changes on Sapphire's room shape (same size, same people's tiles: the zone json stays Sapphire's) ----------
def simple():
    # Slateport Fan Club (14x11): Emerald drops Sapphire's one-way walls (MB_IMPASSABLE_EAST/WEST) at (3,6) (3,7)
    # (10,6) (10,7) in front of the two sofas: the builder's side-wall classes follow Emerald's map.
    VARIANTS['SlateportCity_PokemonFanClub'] = n = 'SlateportCity_PokemonFanClub_Emerald'
    OUT[n] = variant('SlateportCity_PokemonFanClub', "Emerald's Fan Club: no one-way walls at (3,6) (3,7) (10,6) (10,7) "
                     "(Sapphire's MB_IMPASSABLE_EAST/WEST beside the sofas).")
    # Devon Corp 3F (19x9): the same, at (5,4) (5,5) (17,4) (17,5)
    VARIANTS['RustboroCity_DevonCorp_3F'] = n = 'RustboroCity_DevonCorp_3F_Emerald'
    OUT[n] = variant('RustboroCity_DevonCorp_3F', "Emerald's Devon 3F: no one-way walls at (5,4) (5,5) (17,4) (17,5).")
    # Devon Corp 1F (19x9): two display cases in the reception alcove, (3,1)-(3,2) and (8,1)-(8,2) (pokeemerald's bg
    # events ProductsDisplay / RocksMetalDisplay on (3,2) (8,2), both tiles solid now): Black 2's white display cabinet
    VARIANTS['RustboroCity_DevonCorp_1F'] = n = 'RustboroCity_DevonCorp_1F_Emerald'
    r = variant('RustboroCity_DevonCorp_1F', "Emerald's Devon 1F: two display cases at (3,2) and (8,2) (Devon's products, "
                "rocks and metal) in the reception alcove.")
    r['furniture'] += [dict(m='machine02', tile=[3, 2], _what="Emerald's products display (3,1)-(3,2)"),
                       dict(m='machine02', tile=[8, 2], _what="Emerald's rocks and metal display (8,1)-(8,2)")]
    OUT[n] = r
    # Rustboro Flat 1 2F (14x8): the doll collector's room: Sapphire's blue rug (8-12, 3-6) is an orange rug on (7-11, 4-7)
    # with a small table (9,5)-(9,6) in its middle (both tiles solid; the dolls around it are people)
    VARIANTS['RustboroCity_Flat1_2F'] = n = 'RustboroCity_Flat1_2F_Emerald'
    r = variant('RustboroCity_Flat1_2F', "Emerald's Flat 1 2F: an orange rug on (7-11, 4-7) with a small table (9,5)-(9,6) "
                "for the doll collection (Sapphire: a blue rug on (8-12, 3-6)).")
    r['mats'] = [dict(tex='m_h06_mat', src=347, rect=[7, 4, 11, 7], border=0.25, border_units=6, y=0,
                      _what="Emerald's orange rug (Black 2's orange rug m_h06_mat)")]
    r['furniture'].append(dict(m='table02_2w', tiles=[9, 5, 9, 6], rot=90, _what="Emerald's small table on the rug (9,5)-(9,6)"))
    OUT[n] = r
    # May's 2F (9x8): Emerald's rug is pink (Sapphire's red); the doll on the shelf (5,1) is another Pokemon (not drawn by
    # this port: Black 2 has no doll models). The recipe is Brendan's 2F mirrored, as Sapphire's.
    VARIANTS['LittlerootTown_MaysHouse_2F'] = n = 'LittlerootTown_MaysHouse_2F_Emerald'
    r = variant('LittlerootTown_MaysHouse_2F', "Emerald's May's room: a pink rug (Sapphire's is red).")
    base = recipe('LittlerootTown_BrendansHouse_2F')          # (a "mats" given here is not mirrored: May's rug is (1-4, 3-6))
    assert [m['rect'] for m in base['mats']] == [[4, 3, 7, 6]]
    r['mats'] = [dict(base['mats'][0], rect=[1, 3, 4, 6], tex='b02_mat1', src=282, _what="Emerald's pink rug (Black 2's pink mat b02_mat1)")]
    OUT[n] = r

simple()

# ---- Pokemon Center 2F (Emerald LAYOUT_POKEMON_CENTER_2F, 14x10; every Center and the League's new 2F) -------------------
# Emerald's Cable Club floor: three booths along one counter (row 3) between pillars at x 3 (rows 0-2), 8 and 12 (rows
# 0-3): the Wireless Club (attendant (2,2)), the Union Room (attendant (6,2), its door (5,1)) and the Direct Corner
# (attendant (10,2), the Trade Center's door (9,1)); the PC on the counter row (3,3); the two record machines (8,4)
# (12,4); the escalator down at the left wall (warp (1,6), entered walking west); plants and seats along row 9.
# Sapphire's (14x9): booths at x 4-5 / 7-8 / 10-11 between pillars x 3/6/9/12, the escalator at (1,5).
CENTER_2F = ['DewfordTown', 'EverGrandeCity', 'FallarborTown', 'FortreeCity', 'LavaridgeTown', 'LilycoveCity', 'MauvilleCity',
             'MossdeepCity', 'OldaleTown', 'PacifidlogTown', 'PetalburgCity', 'RustboroCity', 'SlateportCity', 'SootopolisCity',
             'VerdanturfTown']
COUNTER_TOP = dict(tex='in02_pc', src=283, uv=[0.0625, 0.95, 0.1875, 0.55], border=0, border_units=0, y=14)
def center_2f(map_name, doc):
    T = lambda x, z, m, **k: dict(m=m, tile=[x, z], **k)
    r = dict(_doc=DOC + doc + " Emerald's Pokemon Center 2F (pokeemerald LAYOUT_POKEMON_CENTER_2F, 14x10) in the look of "
             "Sapphire's (OldaleTown_PokemonCenter_2F.json, the centers agent's master): one counter along row 3 with three "
             "booths between the orange pillars (x 3 rows 1-2, x 8 and 12 rows 1-3; cells left out of the floor, walled in, "
             "orange tops): the Wireless Club (attendant (2,2)), the Union Room (attendant (6,2), door (5,1)) and the Direct "
             "Corner (attendant (10,2), the Trade Center door (9,1)); the PC on the counter row (3,3, tile class 0xd6); the "
             "record machines (8,4) (12,4); the escalator down at the left wall (warp 1,6, entered walking west); plants "
             "and seats along row 9.",
             map=EM + map_name, style='center',
             floor=[[0, 1, 2, 9], [4, 1, 7, 9], [9, 1, 11, 9], [13, 1, 13, 9], [3, 3, 3, 9], [8, 4, 8, 9], [12, 4, 12, 9]],
             stairs=[[1, 6]], block=[[0, 5], [1, 5], [0, 7], [1, 7]],
             classes={'0xd4': [[2, 3], [6, 3], [10, 3]], '0xd6': [[3, 3]]},
             mats=[dict(tex='in76en_kabe1', src=378, rect=rc, border=0, border_units=0, y=50, _what='orange top on the pillar')
                   for rc in ([3, 1, 3, 2], [8, 1, 8, 3], [12, 1, 12, 3])] +
                  [dict(COUNTER_TOP, rect=[x0, 3, x1, 2.90625], _what='counter top (as Sapphire\'s 2F)')
                   for x0, x1 in ((0, 1), (4, 5), (6, 7), (10, 11))],
             furniture=[dict(m='shelf03', tiles=[0, 3, 1, 3], y=-4, _what='Wireless Club counter (sunk 4: top 12)'),
                        T(2, 3, 'desk02', _what='Wireless Club counter in front of the attendant (top 12)'),
                        T(3, 3, 'pc01', _what='PC on the counter row (Emerald MB_PC, tile class 0xd6)'),
                        dict(m='shelf03', tiles=[4, 3, 5, 3], y=-4, _what='Union Room counter'),
                        dict(m='shelf03', tiles=[6, 3, 7, 3], y=-4, _what='Union Room counter'),
                        T(9, 3, 'desk02', _what='Direct Corner counter end'),
                        dict(m='shelf03', tiles=[10, 3, 11, 3], y=-4, _what='Direct Corner counter'),
                        T(8, 4, 'machine02', _what='record machine (Emerald MB_WIRELESS_BOX_RESULTS)'),
                        T(12, 4, 'machine02', _what='record machine (Emerald MB_CABLE_BOX_RESULTS_2)'),
                        T(5, 1, 'cabin_door', wall='N', gap=2, _what='door to the Union Room (Emerald warp 1)'),
                        T(9, 1, 'cabin_door', wall='N', gap=2, _what='door to the Trade Center (Emerald warp 2)'),
                        dict(m='stair_d01', stair=[1, 6], dir='W', _what='escalator down (warp tile 1,6, entered walking west)')] +
                       [T(x, 9, 'plant01', _what='plant') for x in (5, 6, 9, 10)] +
                       [T(x, 9, 'chushion01', _what='yellow seat') for x in (3, 7, 12)] +
                       [T(x, 9, 'pcchair01', y=-12, _what='red seat (sunk to a cushion)') for x in (8, 11)])
    return r

C2F_MOVE = {(4, 2): (2, 2), (7, 2): (6, 2), (10, 2): (10, 2),          # the three attendants, left to right
            (6, 7): (8, 8),                                           # Mauville's youngster (pokeemerald's place)
            (10, 6): (11, 7)}                                         # Mossdeep's woman
C2F_WARPS = [(1, 6), (5, 1), (9, 1), (12, 1), (0, 0)]   # Sapphire's warps 0-4: escalator, Colosseum -> the Union Room door,
                                                        # Trade Center; Record Corner and Double Battle Colosseum: none in
                                                        # Emerald (left out below)
def centers():
    import glob
    zones = {}
    for f in glob.glob(os.path.join(ZONES, '*.json')):
        c = json.load(open(f))
        if c.get('room', '').endswith('_PokemonCenter_2F'): zones[c['room']] = c
    for town in CENTER_2F:
        base = town + '_PokemonCenter_2F'
        n = base + '_Emerald'
        OUT[n] = center_2f(base, f"{town}'s Pokemon Center 2F in Emerald.")
        VARIANTS[base] = n
        z = copy.deepcopy(zones[base])
        z['_doc'] = (DOC + f"Emerald's overlay of {z['zone']}.json: the people and warps on Emerald's Center 2F (tiles of "
                     f"pokeemerald's map, room {n}): the three attendants at (2,2) (6,2) (10,2), the escalator at (1,6), "
                     "the link-room doors (5,1) (9,1). Their scripts are Sapphire's (the apologies of the Colosseum / Trade "
                     "Center / Record Corner attendants; Emerald's are the Wireless Club / Union Room / Direct Corner).")
        for npc in z['npcs']:
            old = tuple(npc['at']); npc['at'] = list(C2F_MOVE[old])
            if old != C2F_MOVE[old]: npc['_what'] = npc.get('_what', '') + f' (Emerald: at {C2F_MOVE[old]}, Sapphire {old})'
        assert len(z['warps']) == len(C2F_WARPS), base
        for w, at in zip(z['warps'], C2F_WARPS): w['at'] = list(at)
        z['warps'] = z['warps'][:3]       # (the Record Corner and Double Battle Colosseum: no door in Emerald; nothing warps
                                          #  to their indices 3 / 4: the Cable Club rooms are not built)
        OVERLAYS[z['zone']] = z

centers()

# ---- Pokemon League 1F (19x12) and Emerald's new 2F --------------------------------------------------------------------
# Emerald's lobby gets an escalator up to the 2F at the left wall (warp (1,7), MB_UP_ESCALATOR, drawn on (0-1, 6-8)), so
# the left plants move to (1,11) (2,11) and the left glass table with its seats two rows down: table (3-4, 10-11), seats
# (3,9) (5,10) (5,11). The 2F (14x10) is Emerald's Pokemon Center 2F (a new room, zone LEAGUE_2F_ZONE).
LEAGUE = 'EverGrandeCity_PokemonLeague'
LEAGUE_2F = 'EverGrandeCity_PokemonLeague_2F'
def league():
    n = LEAGUE + '_Emerald'
    r = variant(LEAGUE, "Emerald's League lobby: the escalator up to the 2F at the left wall (warp 1,7), the left plants at "
                "(1,11) (2,11), the left glass table at (3-4, 10-11) with seats (3,9) (5,10) (5,11).")
    drop(r, [(0, 7), (1, 7)], 'plant01')
    drop(r, [(3, 8)], 'table01_2x2')
    drop(r, [(2, 8), (2, 9), (5, 9), (4, 10)], 'chushion01')
    r['furniture'] += [dict(m='plant01', tile=[1, 11], _what='plant (Emerald)'), dict(m='plant01', tile=[2, 11], _what='plant (Emerald)'),
                       dict(m='table01_2x2', tiles=[3, 10, 4, 11], _what='glass table (Emerald: two rows further south)')] + \
                      [dict(m='chushion01', tile=t, _what='seat (walkable)') for t in ([3, 9], [5, 10], [5, 11])] + \
                      [dict(m='stair_u01', stair=[1, 7], dir='W', _what='escalator up to the 2F (warp tile 1,7, rises west into the wall)')]
    # "stairs" replaces the warp tiles models_interior finds by itself (Sapphire's recipe gives none: the door tiles
    # (9,1) (10,1), MB_NON_ANIMATED_DOOR), so the Elite Four door is listed again with the escalator. Without it the door
    # tiles were plain floor: Black 2's warps 2/3 fire only when the player walks into a solid tile, so the player stepped
    # onto the door and nothing happened (Emerald v1.1 "can't get into the Pokemon League", league_door 2026-10-19).
    r['stairs'] = [[9, 1], [10, 1], [1, 7]]         # pokeemerald warps 2/3 (the Elite Four door) and 4 (the escalator)
    r['block'] = [[0, 6], [1, 6], [0, 8], [1, 8]]
    OUT[n] = r
    VARIANTS[LEAGUE] = n
    em = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_interiors.json')))['rooms'][LEAGUE_2F]
    z2 = em['zone']
    z = zone_json(77)
    z['_doc'] = (DOC + "Emerald's overlay of 77.json: Sapphire's warps 0-3 and warp 4, Emerald's escalator up to the "
                 f"League's 2F (zone {z2}). " + z.get('_doc', ''))
    z['warps'].append(dict(at=[1, 7], tile_only=True, to=[z2, 0], type=2, dir=4,
                           what=f"Emerald warp 4 -> {LEAGUE_2F} 0 (escalator, entered walking west)"))
    OVERLAYS[77] = z
    # the 2F: a new room
    OUT[LEAGUE_2F] = center_2f(LEAGUE_2F, "Emerald's Pokemon League 2F (Emerald-only room, zone %d)." % z2)
    import zoneheaders
    headers, _ = zoneheaders.load(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'))
    c66 = zone_json(66)
    OVERLAYS[z2] = dict(_doc=DOC + f"Emerald's Pokemon League 2F (zone {z2}, claimed in data/emerald/hoenn_interiors.json; "
                        f"room {LEAGUE_2F}): the three Cable Club attendants (Sapphire's apology scripts, as the Centers' 2F), "
                        "the escalator down to the lobby (77 warp 4), the Union Room / Trade Center doors (rooms not built: "
                        "back to this room's warp 0). Place name: the League lobby's (zone 77), music: the Pokemon Center's.",
                        zone=z2, room=LEAGUE_2F, area=283,
                        header=dict(parent=412, place=headers[77]['place'], bgm0=1060, bgm1=1060, bgm2=1060, bgm3=1060),
                        warps=[dict(at=[1, 6], tile_only=True, to=[77, 4], type=2, dir=4, what='Emerald warp 0 -> the League lobby (77) warp 4 (escalator, entered walking west)'),
                               dict(at=[5, 1], tile_only=True, to=[z2, 0], what='Emerald warp 1 -> Union Room (not built: this room\'s warp 0)'),
                               dict(at=[9, 1], tile_only=True, to=[z2, 0], what='Emerald warp 2 -> Trade Center (not built: this room\'s warp 0)')],
                        npcs=[dict(n, at=list(C2F_MOVE[tuple(n['at'])]), _what=f"Cable Club attendant (Emerald {tuple(C2F_MOVE[tuple(n['at'])])}), "
                                   "Sapphire's apology script") for n in c66['npcs']],
                        signs=[], parent=412)
    SCRIPTS.append((em, LEAGUE_2F, 'EverGrandeCity_PokemonCenter_2F'))

SCRIPTS = []        # (claimed room entry, room, Sapphire room whose script and text it copies)
league()

def overlay(zone, room, doc, warps=None, npcs=None, signs=None, drop_signs=()):
    """Emerald overlay of a zone json: warps {index: Emerald tile}, npcs {uid: Emerald tile}, signs {Sapphire tile:
    Emerald tile}, drop_signs: Sapphire tiles of signs Emerald has no such thing at."""
    z = zone_json(zone)
    assert z['room'] == room, (zone, z['room'], room)
    z['_doc'] = DOC + f"Emerald's overlay of {zone}.json (positions in the tiles of {room}'s Emerald variant): " + doc + \
        ' ' + z.get('_doc', '')
    for i, at in (warps or {}).items(): z['warps'][i]['at'] = list(at)
    for n in z.get('npcs', []):
        if n['uid'] in (npcs or {}):
            n['_what'] = n.get('_what', n.get('what', '')) + f" (Emerald: {tuple(npcs[n['uid']])}, Sapphire {tuple(n['at'])})"
            n['at'] = list(npcs[n['uid']])
    z['signs'] = [s for s in z.get('signs', []) if tuple(s['at']) not in set(drop_signs)]
    for s in z['signs']:
        if tuple(s['at']) in (signs or {}): s['at'] = list(signs[tuple(s['at'])])
    OVERLAYS[zone] = z
    return z

STORY_SET = {}      # (story file, map, uid | Sapphire tile) -> {key: Emerald value}: "<key>_emerald" of story objects a layout
                    # change moves (people by uid, signs and triggers by their Sapphire tile)
SCRIPT_BLOCKS = []  # (script file, block name, where, text): #ifdef HOENN_EMERALD blocks in shared room scripts (write_blocks)
STORY_SKIP = set()  # (story file, map, uid | Sapphire tile): "skip_emerald" (Emerald has no such object there)
STORY_NEW = []      # Emerald-only objects of the rooms' own puzzles: data/story/emerald/e_rooms.json

# ---- the other changed rooms ------------------------------------------------------------------------------------------
def others():
    # Lilycove Dept. Store elevator (Emerald 5x6, Sapphire 4x6): one more column on the east side; door, mat, warps and
    # the attendant (0,5) stay where Sapphire has them
    VARIANTS['LilycoveCity_DepartmentStoreElevator'] = n = 'LilycoveCity_DepartmentStoreElevator_Emerald'
    OUT[n] = variant('LilycoveCity_DepartmentStoreElevator', "Emerald's Dept. Store elevator: one tile wider (5x6).",
                     floor=[[0, 2, 4, 5]])
    # Battle Tower elevator car (Emerald 5x7): the same, the back-wall window one tile wider
    VARIANTS['BattleTower_Elevator'] = n = 'BattleTower_Elevator_Emerald'
    r = variant('BattleTower_Elevator', "Emerald's Battle Tower elevator car: one tile wider (5x7); the shaft window "
                "over the five tiles; pokeemerald's empty column (0, 0-2) above the car stays solid.",
                floor=[[0, 3, 4, 6]], block=[[0, 0], [0, 1], [0, 2]])
    for d in r['decals']:
        if d['at'][0] == 2.0:
            d['at'] = [2.5]
            if d['w'] == 58:
                d['w'] = 74; d['uv'] = [d['uv'][0], d['uv'][1], d['uv'][2] * 74 / 58, d['uv'][3]]
            else: d['w'] = 80
        elif d['at'][0] > 3: d['at'] = [4.88]
    OUT[n] = r
    # Battle Tower lobby (Emerald 25x10, Sapphire 14x9): four reception booths (singles, doubles, multis, link multis:
    # receptionists (6,5) (10,5) (14,5) (18,5), the counters' arms on x 4, 8, 12, 16, 20 rows 2-5, fronts beside each
    # receptionist on row 5), a door to the elevator behind each booth ((6,1) the singles' warp; (10,1) (14,1) (18,1)
    # Emerald's scripts warp through), the PC (22,1), plants at the bottom corners, the exit (12-13, 9). The singles booth,
    # its door and the receptionist's walk to it stand on Sapphire's tiles (0042's scripts are unchanged).
    VARIANTS['BattleTower_Lobby'] = n = 'BattleTower_Lobby_Emerald'
    base = recipe('BattleTower_Lobby')
    door = next(f for f in base['furniture'] if f['m'] == 'door_h5_in')
    furn = [dict(door, tile=[x, 1], _what=f"door to the elevator ({['singles: Sapphire warp 2', 'doubles', 'multis', 'link multis'][k]})")
            for k, x in enumerate((6, 10, 14, 18))]
    furn.append(dict(m='pc01', tile=[22, 1], wall='N', _what='PC'))
    for k, x in enumerate((4, 8, 12, 16, 20)):
        furn += [dict(m='shelf03', tiles=[x, 2, x, 3], rot=90, _what='counter arm'), dict(m='shelf03', tiles=[x, 4, x, 5], rot=90, _what='counter arm')]
    for c in (6, 10, 14, 18):
        furn.append(dict(m='desk02', tile=[c - 1, 5], _what='counter front'))
        furn.append(dict(m='desk02', tile=[c + 1, 5], _what='counter front'))
    furn += [dict(m='plant01', tile=[x, 9]) for x in (0, 1, 23, 24)]
    OUT[n] = dict(_doc=DOC + "Emerald's Battle Tower lobby (pokeemerald BattleFrontier_BattleTowerLobby, 25x10) in the look of "
                  "Sapphire's (BattleTower_Lobby.json, sp_battle): four reception booths along the back wall (counter arms on "
                  "x 4/8/12/16/20 rows 2-5, fronts beside each receptionist's tile (6/10/14/18, 5)), Black 2's blue double "
                  "door into the elevator behind each ((6,1) is the singles' warp, as Sapphire's), the PC (22,1), plants in "
                  "the bottom corners, the exit mat (12-13, 9).",
                  map=EM + 'BattleFrontier_BattleTowerLobby', style=base['style'], origin=[1, 1], floor=[[0, 1, 24, 9]],
                  stairs=[[6, 1]], mats=[dict(base['mats'][0], rect=[12, 9, 13, 9])], furniture=furn)
    overlay(21, 'BattleTower_Lobby', "the exits (12,9) (13,9); MAN_5 (12,3: a counter in Emerald) at Emerald's MAN_4 (23,5), "
            "the woman, the boy and the reporter at Emerald's places (17,8) (15,9) (11,9); the records terminal's sign on the "
            "singles counter (5,5) (Sapphire's (3,5) is floor in Emerald). The doubles / multis / link multis receptionists "
            "(10,5) (14,5) (18,5) are not placed.",
            warps={0: (12, 9), 1: (13, 9)}, npcs={2: (23, 5), 3: (17, 8), 4: (15, 9), 5: (11, 9)}, signs={(3, 5): (5, 5)})
    # Mossdeep Game Corner 1F (Emerald 12x10, its own tileset): Emerald's wireless minigame lounge in the house of R/S's
    # e-Reader trainer: a counter (2-8, 3) with two men behind it ((4,2) (6,2)) and the doorway (5,1) behind them, the two
    # record boards (0,1) (1,1), the PC (10,1), two glass tables (2-3, 6-7) (7-8, 6-7) with seats, the exit (5-6, 9). The
    # basement warp (Emerald (2,0), a wall tile: reached only by the link attendants) keeps the old man's zone init, which
    # moves it off the map.
    VARIANTS['MossdeepCity_GameCorner_1F'] = n = 'MossdeepCity_GameCorner_1F_Emerald'
    T = lambda x, z, m, **k: dict(m=m, tile=[x, z], **k)
    OUT[n] = dict(_doc=DOC + "Emerald's Mossdeep Game Corner 1F (pokeemerald MossdeepCity_GameCorner_1F, 12x10: the wireless "
                  "minigame lounge) in Black 2's house look (Sapphire's room: houses_wood): the counter (2-8, 3) with the "
                  "doorway (5,1) behind it, the record boards (0,1) (1,1), the PC (10,1), two glass tables with seats, the "
                  "exit (5-6, 9).",
                  map=EM + 'MossdeepCity_GameCorner_1F', style='houses_wood', origin=[1, 1], floor=[[0, 1, 11, 9]],
                  block=[[5, 0], [5, 1], [5, 2], [10, 0]],        # (walkable in pokeemerald's map, behind the counter /
                                                                  #  above the PC: no way to them)
                  classes={'0xd6': [[10, 1]]},
                  mats=[dict(tex='in70_mat1', src=351, rect=[5, 9, 6, 9], border=0.25, border_units=3, y=0, _what='exit mat')],
                  furniture=[T(2, 3, 'desk02', _what='counter end'), dict(m='shelf03', tiles=[3, 3, 4, 3], _what='counter'),
                             T(5, 3, 'desk02', _what='counter gate'), dict(m='shelf03', tiles=[6, 3, 7, 3], _what='counter'),
                             T(8, 3, 'desk02', _what='counter end'),
                             dict(m='pcshelf01_2', tiles=[2, 1, 3, 1], wall='N', _what='shelves behind the counter'),
                             T(5, 1, 'door_pwood01', wall='N', _what='doorway behind the counter (no warp)'),
                             dict(m='pcshelf01_2', tiles=[7, 1, 8, 1], wall='N', _what='shelves behind the counter'),
                             T(0, 1, 'art01', wall='N', gap=2, y=18, _what='Dodrio Berry Picking record board'),
                             T(1, 1, 'art01', wall='N', gap=2, y=18, _what='Pokemon Jump record board'),
                             T(10, 1, 'pc01', wall='N', _what='PC (Emerald MB_PC, tile class 0xd6)'),
                             dict(m='table01_2x2', tiles=[2, 6, 3, 7], _what='glass table'),
                             dict(m='table01_2x2', tiles=[7, 6, 8, 7], _what='glass table')] +
                            [T(x, z, 'chushion01', _what='seat (walkable)') for x, z in ((2, 5), (3, 5), (1, 6), (1, 7),
                                                                                         (7, 5), (8, 5), (9, 6), (9, 7))])
    overlay(277, 'MossdeepCity_GameCorner_1F', "the exits (5,9) (6,9), the basement warp on Emerald's (2,0) (the zone init "
            "moves it off the map, as in Sapphire); no locked-door sign (Emerald moved it into the wall, out of reach) and no "
            "bookshelves (Sapphire's (9,1) (10,1)). Emerald's two link men (4,2) (6,2) and the record "
            "boards' signs are not placed (link features).",
            warps={0: (5, 9), 1: (6, 9), 2: (2, 0)}, drop_signs=[(3, 1), (9, 1), (10, 1)])
    # Lilycove Contest Lobby (Emerald 31x12, Sapphire 23x12): Sapphire's reception part 8 tiles further east (counter
    # (11-18, 2-3), doors (9,1) (21,1), PC (19,1), exit (14-15, 11)), six contest winners' portraits (3/5/7, 1) and
    # (23/25/27, 1) and the Berry Blender records (30,1), four Berry Blenders (23,5) (27,5) (23,9) (27,9) on the east side,
    # the sofas along both side walls (x 0 and 30, rows 6-7 and 9-10)
    VARIANTS['LilycoveCity_ContestLobby'] = n = 'LilycoveCity_ContestLobby_Emerald'
    base = recipe('LilycoveCity_ContestLobby')
    F = {f['_what']: f for f in base['furniture']}
    cdoor = next(f for f in base['furniture'] if f['m'] == 'cabin_door_r')
    art = next(f for f in base['furniture'] if f['m'] == 'art01')
    sofa_w = [f for f in base['furniture'] if f['m'] == 'chair03' and f.get('wall') == 'W'][0]
    sofa_e = [f for f in base['furniture'] if f['m'] == 'chair03' and f.get('wall') == 'E'][0]
    furn = [dict(cdoor, tile=[9, 1], _what='door to the hall (Sapphire warp 2)'), dict(cdoor, tile=[21, 1], _what='door to the hall (Sapphire warp 3)'),
            dict(m='shelf03', tiles=[11, 2, 11, 3], rot=270, _what='counter, west side'),
            dict(m='table02', tiles=[12, 3, 14, 3], _what='counter, front'), dict(m='table02', tiles=[15, 3, 17, 3], _what='counter, front'),
            dict(m='shelf03', tiles=[18, 2, 18, 3], rot=90, _what='counter, east side'),
            dict(m='pc01', tile=[19, 1], wall='N', _what='PC')]
    furn += [dict(art, tile=[x, 1], _what='contest winner portrait') for x in (3, 5, 7, 23, 25, 27)]
    furn.append(dict(art, tile=[30, 1], _what='Berry Blender records'))
    for x, z in ((23, 5), (27, 5), (23, 9), (27, 9)):
        furn += [dict(m='desk02', tile=[x, z], _what='Berry Blender (table)'), dict(m='mball01', tile=[x, z], _what='Berry Blender (top)')]
    furn += [dict(sofa_w, tile=[0, z]) for z in (6, 7, 9, 10)] + [dict(sofa_e, tile=[30, z]) for z in (6, 7, 9, 10)]
    OUT[n] = dict(_doc=DOC + "Emerald's Lilycove Contest Lobby (31x12) in the look of Sapphire's (LilycoveCity_ContestLobby.json, "
                  "sp_theater): the reception part 8 tiles further east than Sapphire's (counter 11-18, doors (9,1) (21,1), "
                  "PC (19,1), exit (14-15, 11)), six contest winners' portraits and the Berry Blender records board on the "
                  "back wall, four Berry Blenders on the east side, the sofas along both side walls.",
                  map=EM + 'LilycoveCity_ContestLobby', style=base['style'], origin=[1, 1], floor=[[0, 1, 30, 11]],
                  floor_extra=[[-0.75, 6, 0, 11], [31, 6, 31.75, 11]],
                  mats=[dict(base['mats'][0], rect=[14, 11, 15, 11])],
                  decals=[dict(d, at=[x]) for d, x in zip(base['decals'], (12.0, 17.0, 1.0, 29.0))], furniture=furn)
    overlay(161, 'LilycoveCity_ContestLobby', "the exits (14,11) (15,11), the doors to the hall (9,1) (21,1); the people at "
            "Emerald's places of the same people (pokeemerald's local ids): black belt (18,8), artist (3,4), boy (23,8), "
            "fisherman (5,6), fat man (0,8).",
            warps={0: (14, 11), 1: (15, 11), 2: (9, 1), 3: (21, 1)}, npcs={5: (18, 8), 7: (3, 4), 9: (23, 8), 12: (5, 6), 13: (0, 8)})
    for uid, at in {1: (14, 2), 2: (15, 2), 6: (4, 9), 10: (28, 9), 14: (8, 7)}.items():
        STORY_SET[('ch8a.json', 'LilycoveCity_ContestLobby', uid)] = dict(at=list(at))

others()

# ---- Trick House puzzle 1 (15x22): Emerald's own maze on Sapphire's grid ----------------------------------------------
# The same building rules as Sapphire's recipe (Route110_TrickHousePuzzle1.json): the long fence rows 6, 10, 14, 18 are
# low wooden bars (desk01 per three tiles, desk02 for the rest), every other solid tile of the maze a low plank box
# (8 high), row 2 (0-11) Sapphire's wall shelf; the scroll (Emerald (3,16)) a one-tile table. Puzzles 2-8 are built in
# no version (their doors are closed), so nothing of Emerald's changes there is built.
def trick_house():
    import models_interior as mi
    name = 'Route110_TrickHousePuzzle1'
    base = recipe(name)
    sm = mi.sapphire_map(EM + name)
    solid = {(x, z) for z in range(sm['h']) for x in range(sm['w']) if not sm['walk'][z][x]}
    scroll = (3, 16)
    furn = []
    for z in (6, 10, 14, 18):
        x = 0
        while x < sm['w']:
            if (x, z) not in solid: x += 1; continue
            x1 = x
            while (x1 + 1, z) in solid: x1 += 1
            while x1 - x + 1 >= 3:
                furn.append(dict(m='desk01', rot=90, tiles=[x, z, x + 2, z], _what='fence')); x += 3
            while x <= x1:
                furn.append(dict(m='desk02', tile=[x, z], _what='fence')); x += 1
    furn.append(next(f for f in base['furniture'] if f['m'] == 'cabin_door'))
    furn.append(dict(m='desk02', tile=list(scroll), _what='the scroll (Emerald sign 3,16): a one-tile table'))
    boxes = sorted([list(t) for t in solid if 3 <= t[1] <= 21 and t[1] not in (6, 10, 14, 18) and t != scroll] +
                   [[x, 2] for x in range(12)])
    r = copy.deepcopy(base)
    r['_doc'] = (DOC + "Emerald's Trick House puzzle 1 (pokeemerald's maze, same size) built by the rules of Sapphire's "
                 "recipe: fence rows 6/10/14/18 as low wooden bars, the other solid tiles low plank boxes, the scroll (3,16) "
                 "a one-tile table. " + base['_doc'])
    r['map'] = EM + name
    r['furniture'] = furn
    r['blocks'] = [dict(base['blocks'][0], tiles=boxes)]
    n = name + '_Emerald'
    OUT[n] = r; VARIANTS[name] = n
    z = overlay(552, name, "Emerald's Orange Mail ball at (9,4) (data/emerald/hoenn_items.json n 167, script 7166, flag 1266; "
                "Sapphire's ball (9,12) is not Emerald's). The scroll's sign and the three trainers (Sally (14,20), Eddie "
                "(14,8), Robin (2,15)) and the Cut trees are story (not placed, as in Sapphire).")
    em_items = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_items.json')))
    it = em_items['balls']['Route110_TrickHousePuzzle1_EventScript_ItemOrangeMail']
    for npc in z['npcs']:
        if npc.get('model') == 110:
            npc.update(at=list(it['at']), script=it['script'], flag=it['flag'],
                       _what=f"item ball: Emerald's Orange Mail (data/emerald/hoenn_items.json n {it['n']}; Sapphire's ball was at {tuple(npc['at'])})")

trick_house()

import emerald_gyms                 # noqa: E402  (the eight Gyms: their rooms, people and puzzles)
emerald_gyms.build(sys.modules[__name__])

def write_scripts(check):
    """A new room's zone script and text: the Sapphire room's (same people, same lines), in the Emerald overlays."""
    import glob
    for em, name, like in SCRIPTS:
        src = glob.glob(os.path.join(ROOT, 'src', 'field_scripts', f'*_room_{like}.s'))[0]
        txt = glob.glob(os.path.join(ROOT, 'src', 'text', 'script', f'*_room_{like}.txt'))[0]
        s = open(src, encoding='utf-8').read().split('\n')
        s = [f"// {name} (zone {em['zone']}, Emerald only): emerald_rooms (b2tools/emerald_rooms.py writes this file: edit the",
             f"// generator), a copy of {os.path.basename(src)}'s people scripts. Room: data/interior_layouts/{name}.json,",
             f"// people/warps: data/interiors/emerald/{em['zone']}.json. Messages: src/text/script/emerald/{em['text']:04d}_room_{name}.txt."] + \
            [ln for ln in s if not ln.startswith('//')]
        write_text(os.path.join(ROOT, 'src', 'field_scripts', 'emerald', f"{em['scripts']:04d}_room_{name}.s"), '\n'.join(s), check)
        write_text(os.path.join(ROOT, 'src', 'text', 'script', 'emerald', f"{em['text']:04d}_room_{name}.txt"),
                   open(txt, encoding='utf-8').read(), check)

def write_story(check):
    """"at_emerald" / "skip_emerald" on the story objects of the shared data/story files (Sapphire's builds read neither:
    patches/story.py version_keys), written without reformatting the file; the Emerald-only objects in
    data/story/emerald/e_rooms.json."""
    import collections
    by_file = collections.defaultdict(dict)
    for (f, m, key), kv in STORY_SET.items(): by_file[f][(m, key)] = ('set', kv)
    for (f, m, key) in STORY_SKIP: by_file[f][(m, key)] = ('skip', True)
    for f, want in sorted(by_file.items()):
        p = os.path.join(ROOT, 'data', 'story', f)
        s = open(p, encoding='utf-8').read(); j = json.loads(s)
        fmt = [(ea, nl) for ea in (False, True) for nl in ('', '\n') if json.dumps(j, indent=1, ensure_ascii=ea) + nl == s]
        def key(o): return (o.get('map'), o['uid'] if o.get('kind', 'npc') == 'npc' and 'uid' in o else tuple(o.get('at', ())))
        def apply(o, what, v):                  # (only the keys named here: other agents' "_emerald" keys stay)
            if what == 'set':
                for k, val in v.items():
                    if o.get(k) != val: o[k + '_emerald'] = val
                    else: o.pop(k + '_emerald', None)
            else:
                o['skip_emerald'] = True
                for k in ('at', 'dir', 'move', 'p0', 'map'): o.pop(k + '_emerald', None)   # (left over from an older run)
        found = set()
        for o in j['objects']:
            k = key(o)
            if k not in want: continue
            found.add(k); apply(o, *want[k])
        assert found == set(want), (f, set(want) - found)
        if fmt:
            new = json.dumps(j, indent=1, ensure_ascii=fmt[0][0]) + fmt[0][1]
        else:                                   # one object per line (ch1.json): edit those lines only
            lines = s.split('\n'); objs = iter(j['objects'])
            for i, ln in enumerate(lines):
                st = ln.strip().rstrip(',')
                if not (st.startswith('{') and st.endswith('}') and '"kind"' in st): continue
                o = json.loads(st); k = key(o)
                if k not in want: continue
                apply(o, *want[k])
                lines[i] = ln[:len(ln) - len(ln.lstrip())] + json.dumps(o, ensure_ascii=False) + (',' if ln.rstrip().endswith(',') else '')
            new = '\n'.join(lines)
            assert json.loads(new) == j, f
        write_text(p, new, check)
    if STORY_NEW:
        write_json(os.path.join(ROOT, 'data', 'story', 'emerald', 'e_rooms.json'),
                   dict(_doc=DOC + "Emerald-only story objects of the rooms Emerald changed (their puzzles: b2tools/emerald_rooms.py). "
                        "Positions: Emerald's map tiles of the room (the variant's).", objects=STORY_NEW), check)

EM_KEYS = ('at', 'dir', 'move', 'p0', 'map', 'skip', 'script', 'flag')   # the "_emerald" keys this script owns

MARK_A, MARK_B = '// >>> emerald_rooms', '// <<< emerald_rooms'
def write_blocks(check):
    """SCRIPT_BLOCKS into their files: every old emerald_rooms block is taken out first, then each block is put in again
    ('table': before the ScriptEntry table's ScriptEntriesEnd; 'end': at the end of the file; ('after', regex): after the
    first line matching regex). The blocks are #ifdef HOENN_EMERALD: Sapphire's and Ruby's assembly is unchanged."""
    import collections
    by = collections.defaultdict(list)
    for path, name, where, text in SCRIPT_BLOCKS: by[path].append((name, where, text))
    for path, blocks in by.items():
        s = open(path, encoding='utf-8').read()
        s = re.sub(r'(?m)^[ \t]*' + re.escape(MARK_A) + r' .*\n(?:.*\n)*?[ \t]*' + re.escape(MARK_B) + r' .*\n', '', s)
        lines = s.split('\n')
        for name, where, text in blocks:
            blk = [f'{MARK_A} {name} (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)'] + \
                  text.rstrip('\n').split('\n') + [f'{MARK_B} {name}']
            if where == 'table':
                i = next(k for k, l in enumerate(lines) if l.strip().startswith('ScriptEntriesEnd'))
            elif where == 'end':
                while lines and lines[-1] == '': lines.pop()
                if not any(l.strip().startswith('// ---- story') for l in lines):   # (a generated file: a story line keeps
                    lines += ['', '// ---- story (emerald_rooms: the Emerald build\'s own scripts below; generators keep '
                              'everything from this line on)']                     #  this part when its generator reruns)
                i = len(lines); blk = [''] + blk + ['']
            else:
                i = next(k for k, l in enumerate(lines) if re.search(where[1], l)) + 1
            lines[i:i] = blk
        new = '\n'.join(lines)
        if not new.endswith('\n'): new += '\n'
        write_text(path, new, check)

def write_text(p, s, check):
    old = open(p, encoding='utf-8').read() if os.path.exists(p) else None
    if old == s: return
    print(('would write ' if check else 'wrote ') + os.path.relpath(p, ROOT))
    if not check: open(p, 'w', encoding='utf-8').write(s)

# ------------------------------------------------------------------------------------------------ write
def write_json(p, d, check):
    s = json.dumps(d, indent=1, ensure_ascii=False) + '\n'
    old = open(p, encoding='utf-8').read() if os.path.exists(p) else None
    if old == s: return False
    print(('would write ' if check else 'wrote ') + os.path.relpath(p, ROOT))
    if not check:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(s)
    return True

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); a = ap.parse_args()
    for n, r in OUT.items(): write_json(os.path.join(LAYOUTS, n + '.json'), r, a.check)
    for zone, z in OVERLAYS.items(): write_json(os.path.join(ZONES, 'emerald', f'{zone}.json'), z, a.check)
    write_scripts(a.check)
    write_story(a.check)
    write_blocks(a.check)
    p = os.path.join(ROOT, 'data', 'versions.json')
    v = json.load(open(p, encoding='utf-8'))          # (read just before writing: other agents edit this file too)
    rv = v.setdefault('room_variants', {}).setdefault('emerald', {})
    rv.update(VARIANTS)
    for n in OUT: v['rooms'][n] = 'emerald'
    s = json.dumps(v, indent=1) + '\n'
    if s != open(p, encoding='utf-8').read():
        print(('would update ' if a.check else 'updated ') + 'data/versions.json (room_variants.emerald, rooms)')
        if not a.check: open(p, 'w', encoding='utf-8').write(s)

if __name__ == '__main__':
    main()
