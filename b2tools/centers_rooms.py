"""Pokémon Centers (centers agent, notes/INTERIORS.md): every Hoenn Pokémon Center 1F/2F (status "center" in
data/hoenn_interiors.json) in Sapphire's Gen 3 layout, with Sapphire's people.

    python3 centers_rooms.py             write the rooms: recipe copies, zone jsons, script and text files (below)
    python3 centers_rooms.py classes     tile classes into the built rooms' collision.per (see classes())
    CENTERS_TEST_BLACKOUT=1 python3 centers_rooms.py    agent tests only, in HOENN_TEST_WARP builds: every 1F
                                        magazine shelf starts a wild battle you lose (Mewtwo Lv 100: blackout test),
                                        Oldale's map opens a town menu (b2tools/centers_test.py "@Town"); rerun
                                        without it before committing

Writes (all owned by the centers agent):
  data/interior_layouts/<Town>_PokemonCenter_1F/2F.json   copies of the two masters OldaleTown_PokemonCenter_1F/2F
                                        (hand-made; Lavaridge 1F = the 1F master with its back door, see lavaridge())
  data/interiors/<zone>.json            room, Sapphire's warps in Sapphire's order (one per warp tile), people, signs
  src/field_scripts/SSSS_room_<Map>.s   (+ IIII_room_<Map>_init.s where a map script is needed)
  src/text/script/TTTT_room_<Map>.txt   Sapphire's words, Gen 5 capitalisation (converter/gen3text.py)
  SSSS/IIII/TTTT = the zone's numbers in data/hoenn_interiors.json for now (lead, 2026-10-06: new files only, never
  Black 2's own; at integration the lead moves every room's files to new ids at the end of the archives)

Everything a Center does:
  - nurse: src/field_scripts/centers/nurse.inc (Sapphire's words, Black 2's heal sequence and healing machine);
  - PC: the pc01 model on a tile of class 0xd6 (MapTile_IsPC) runs Black 2's PC (global script 10090);
  - talking to the nurse over the counter: tile class 0xd4 (MapTile_IsReceptionCounter) in front of her;
  - blackout: Black 2 returns you to tile (7,12) of the last Center zone entered (ov012 RESPAWN_ZONE_INFO), so the
    1F rooms put the tile in front of the nurse there (recipe origin (0,8)); b2tools/patches/centers.py points each
    record's main zone at its Hoenn town (Teleport, Escape Rope after a blackout).

Story flags that hoenn.h does not define yet: the scripts use #ifdef and behave as at the start of the game
(as the shops agent's scripts do), so they assemble now and switch on when the lead adds the names to hoenn.h.
"""
import os, sys, json, re, glob, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'converter'))
RUBY = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps')
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
OUT_S, OUT_T = os.path.join(ROOT, 'src', 'field_scripts'), os.path.join(ROOT, 'src', 'text', 'script')
ROOMS_DIR = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'agents', 'centers', 'interiors')

ALL = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
ROOMS = {n: r for n, r in ALL.items() if r['status'] == 'center'}
ZONES = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
SPRITES = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
MASTER_1F, MASTER_2F = 'OldaleTown_PokemonCenter_1F', 'OldaleTown_PokemonCenter_2F'
AREA = 283                                   # Black 2's Pokémon Center interior area (pack 1 has the Center furniture)

def hoenn_defines():
    out = {}
    for line in open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')):
        m = re.match(r'#define\s+(\w+)\s+(0x[0-9A-Fa-f]+|\d+)', line)
        if m: out[m.group(1)] = int(m.group(2), 0)
    return out
DEFS = hoenn_defines()

# ------------------------------------------------------------------------------------------------ text
_text = {}
def sapphire_text():
    if not _text:
        from gen_map_content import ruby_scripts
        _text['t'], _text['s'] = ruby_scripts()
    return _text['t']

FIX = {   # Gen 3 codes the converter drops, and text that ruby_scripts() reads wrong
    'LavaridgeTown_PokemonCenter_1F_Text_HotSpringCanInvigorate': [('RED {POKEBLOCK}', 'RED POKéBLOCK')],
    'VerdanturfTown_PokemonCenter_1F_Text_TrainerIsntQualifiedIf': [('{POKEBLOCK}S', 'POKéBLOCKS')],
    'FallarborTown_PokemonCenter_1F_Text_LanetteGreeting': [('{KUN}', '')],
    'OldaleTown_PokemonCenter_1F_Text_PokemonCentersAreGreat': [('POKéMON CENTERS', 'POKéMON CENTERs')],
    # both revisions' lines are read; Sapphire (REVISION >= 1 in our dump's build) says RECORD CORNER
    'OldaleTown_PokemonCenter_2F_Text_1A45FE': [('RECORD CORNER.\\pRECORD CENTER.\\p', 'RECORD CORNER.\\p')],
}

def msg(label):
    from gen3text import convert
    s = sapphire_text()[label]
    for a, b in FIX.get(label, []):
        assert a in s, (label, a)
        s = s.replace(a, b)
    out, unknown = convert(s)
    assert not unknown, (label, unknown)
    return out.replace('Pokémon CenterS', 'Pokémon Centers')

NURSE_TEXT = ['gText_NurseJoy_Welcome', 'gText_NurseJoy_OkayIllTakeYourPokemon', 'gText_NurseJoy_ThankYouForWaiting',
              'gText_NurseJoy_WeHopeToSeeYouAgain', 'gText_NurseJoy_Pokerus']
BOOKSHELF = 'Text_PokemonCenterBookshelf'        # Sapphire MB_POKEMON_CENTER_BOOKSHELF (data/text/check_furniture.inc)
# Sapphire's MB_REGION_MAP: its line for looking at a Hoenn wall map (the player's room), then the map screen
# (region_map below: Black 2's town map, b2tools/patches/town_map.py)
REGION_MAP = 'Common_Text_LookCloserAtMap'

# ------------------------------------------------------------------------------------------------ json helpers
def dumps(o, ind=0):
    """Compact JSON: short lists and small dicts on one line."""
    pad = ' ' * ind
    if isinstance(o, dict):
        one = json.dumps(o, ensure_ascii=False)
        if len(one) + ind < 118 and not any(isinstance(v, (dict, list)) and len(json.dumps(v)) > 60 for v in o.values()):
            return one
        items = [f'{pad} {json.dumps(k)}: {dumps(v, ind + 1).lstrip()}' for k, v in o.items()]
        return '{\n' + ',\n'.join(items) + f'\n{pad}}}'
    if isinstance(o, list):
        one = json.dumps(o, ensure_ascii=False)
        if len(one) + ind < 118: return one
        return '[\n' + ',\n'.join(f'{pad} {dumps(v, ind + 1).lstrip()}' for v in o) + f'\n{pad}]'
    return json.dumps(o, ensure_ascii=False)

def write(path, text):
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
    if old != text:
        open(path, 'w', encoding='utf-8').write(text)
        return True
    return False

# ------------------------------------------------------------------------------------------------ recipes
def lavaridge(r):
    """Lavaridge's 1F (LAYOUT_LAVARIDGE_TOWN_POKEMON_CENTER_1F): a back door to the hot springs at (2,1) between two
    plants instead of the magazine shelf, and its two seats stacked at (1,3)/(1,4)."""
    r = json.loads(json.dumps(r))
    r['stairs'] = r['stairs'] + [[2, 1]]
    fur = [f for f in r['furniture'] if f['m'] != 'pcshelf01' and f.get('tile') not in ([1, 3], [2, 3])]
    fur += [{"m": "plant01", "tile": [3, 1], "wall": "N", "_what": "plant right of the back door"},
            {"m": "cabin_door", "at": [2.5, 1.5], "wall": "N", "gap": 2, "_what": "back door to the hot springs (warp tile 2,1, entered walking north)"},
            {"m": "pcchair01", "tile": [1, 3], "y": -12, "_what": "red seat"},
            {"m": "chushion01", "tile": [1, 4], "_what": "yellow seat"}]
    r['furniture'] = fur
    return r

def write_recipes():
    changed = []
    masters = {k: json.load(open(os.path.join(LAYOUTS, k + '.json'))) for k in (MASTER_1F, MASTER_2F)}
    for name in sorted(ROOMS):
        if name in masters: continue
        m = MASTER_1F if name.endswith('_1F') else MASTER_2F
        r = {'_doc': f'Copy of {m}, written by b2tools/centers_rooms.py: edit the master and rerun.', 'map': name}
        r.update({k: v for k, v in masters[m].items() if k not in ('_doc', 'map')})
        if name == 'LavaridgeTown_PokemonCenter_1F':
            r = lavaridge(r); r['_doc'] = ' '.join(lavaridge.__doc__.split()) + ' ' + r['_doc']
        if write(os.path.join(LAYOUTS, name + '.json'), dumps(r) + '\n'): changed.append(name)
    return changed

# ------------------------------------------------------------------------------------------------ warps
_doors = {}
def door_warp(town, warp_id):
    """(zone, Black 2 warp index) of the outdoor door warp for Sapphire's (town, warp id), as converter/gen_interiors.py
    resolves it: a door the town config gives one of Black 2's own warp slots keeps that slot (data/hoenn_world.json
    "warps"); the rest are world.json's appended "doors" after the zone's Black 2 warps."""
    if not _doors:
        import narcio, zoneheaders
        from zones import parse_entities
        sys.path.insert(0, os.path.join(HERE, 'patches'))
        files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
        headers, _ = zoneheaders.load(files); ents = narcio.load(files, 126)
        world = json.load(open(os.path.join(os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'), 'world.json')))
        cfg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world.json')))['maps']
        for zid, z in world['zones'].items():
            base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
            for k, d in enumerate(z.get('doors', [])): _doors[(d['map'], d['id'])] = (int(zid), base + k)
        slots = {}
        for t, c in cfg.items():
            for dest, slot in c.get('warps', {}).items(): slots[(t, dest)] = slot
        _doors['slots'] = slots
    rj = json.load(open(os.path.join(RUBY, town, 'map.json')))
    w = rj['warp_events'][warp_id]
    slot = _doors['slots'].get((town, w['dest_map']))
    if slot is not None: return (ZONES[town]['zone'], slot)
    return _doors.get((town, warp_id))

def map_id_name(map_const):
    return next((n for n, r in ALL.items() if r.get('map_id') == map_const), None)

UNRESOLVED = []

def warps_of(name):
    r = ROOMS[name]; out = []
    beh = __import__('models_interior').sapphire_map(name)['beh']
    for i, w in enumerate(r['warps']):
        dest, dw = w['dest'], w['dest_warp']
        if dest in ZONES: to = door_warp(dest, dw); what = f'Sapphire warp {i} -> {dest} {dw}'
        elif dest in ALL: to = (ALL[dest]['zone'], dw if ALL[dest]['status'] == 'center' else 0); what = f'Sapphire warp {i} -> {dest} {dw}'
        else: to = None
        if to is None:       # the town is not in the built world yet (Sootopolis): the room's own warp 0, as
            to = (r['zone'], 0); what += ' (NOT BUILT YET: points at this room\'s warp 0)'   # gen_interiors does
            UNRESOLVED.append(f'{name} warp {i} -> {dest} {dw}')
        e = dict(at=[w['x'], w['y']], tile_only=True, to=list(to), what=what)
        b = beh[w['y']][w['x']] if 0 <= w['y'] < len(beh) and 0 <= w['x'] < len(beh[0]) else None
        if b in (0x6A, 0x6B):                    # escalators at the left wall: entered walking west (warp dir 4)
            e.update(type=2, dir=4, what=what + ' (escalator, entered walking west)')
        elif ALL.get(dest, {}).get('status') == 'link':
            e['what'] = what + ' (Cable Club door: a solid tile, reached only by script in Sapphire)'
        out.append(e)
    return out

# ------------------------------------------------------------------------------------------------ people
import move_codes as MOVE_CODES                       # noqa: E402  (v165_fixes)
FACE = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2, 'MOVEMENT_TYPE_FACE_RIGHT': 3}
# Black 2 move codes: b2tools/move_codes.py (15 always face down: Black 2's nurses)
MAUVILLE_MEN = [   # Sapphire's Mauville old man (data/scripts/mauville_man.inc): first line; overworld sprite (b2tools/sprite_unique.py, one drawing in 5 palettes)
    ('Bard', 'gTextBard_HiImTheBard', 328), ('Hipster', 'gTextHipster_TheyCallMeTheHipster', 329),
    ('Trader', 'gTextTrader_Introduction', 334), ('Storyteller', 'gTextStoryteller_Introduction', 335),
    ('Giddy', 'gTextGiddy_Introduction', 336)]

def npc_entry(lid, o, model, script, **kw):
    n = dict(uid=lid, model=model, script=script, dir=FACE.get(o['movement_type'], 1), at=[o['x'], o['y']])
    n.update(MOVE_CODES.room_npc(o))     # Sapphire's movement type as Black 2's code (b2tools/move_codes.py; v165_fixes:
                                         # wander up/down / left/right are Black 2's 4 / 5, not 3 with one axis fixed)
    n.update(kw)
    n['_what'] = f"{o['graphics_id'][14:].lower()} ({o['x']},{o['y']}), Sapphire {o['script']}"
    return n

class File:
    """One zone's script file + text file under construction."""
    def __init__(self, name, nurse):
        self.name = name; self.blocks = []; self.msgs = []; self.notes = []
        if nurse: self.msgs += [msg(l) for l in NURSE_TEXT]
    def text(self, label_or_text, raw=False):
        t = label_or_text if raw else msg(label_or_text)
        if t in self.msgs: return self.msgs.index(t)
        self.msgs.append(t); return len(self.msgs) - 1
    def add(self, body, comment):
        self.blocks.append((comment, body)); return len(self.blocks)

def talk(f, m):                              # Black 2's NPC message pattern (as gen_interiors.npc_block)
    return f"""    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, {m}, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def sign(f, m):
    return f"""    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg {m}, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def region_map(f, m):
    """The wall map (Sapphire EventScript_RegionMap: msgbox Common_Text_LookCloserAtMap, fadescreen FADE_TO_BLACK, special
    FieldShowRegionMap, waitstate): the line, then Black 2's town map through CallPlaceSelect (the script command of
    Black 2's own town-map call, 1280.s; b2tools/patches/town_map.py opens it in view mode in a zone without Fly)."""
    return f"""    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg {m}, 2
    LastKeyWait
    MsgWinCloseAll
    FadeOutBlackQ
    FadeWait
    CallPlaceSelect 0x8000, 0x8001
    FadeInBlackQ
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def choose(f, flag, if_set, if_unset, test=None):
    """Talk script showing if_set when FLAG is set, else if_unset (Sapphire goto_if_set); a flag hoenn.h lacks
    assembles as unset (#ifdef), like the start of the game. test: own assembly that sets 0x8000 (1 = set)."""
    a, b = f.text(if_set), f.text(if_unset)
    k = len(f.blocks) + 1
    get = test or f'    FlagGet {flag}, 0x8000\n'
    cond = f"""{get}    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_{k}_Set
"""
    if not test: cond = f'#ifdef {flag}\n{cond}#endif\n'
    return f"""    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
{cond}    ParentActorMsg MSGFILE_SCRIPT, {b}, 0, 0
    VMJump L_{k}_End
L_{k}_Set:
    ParentActorMsg MSGFILE_SCRIPT, {a}, 0, 0
L_{k}_End:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def petalburg_woman(f):
    """Sapphire: the types talk, then (IsStarterInParty: the starter species itself, VAR_STARTER_MON) its type."""
    a = f.text('PetalburgCity_PokemonCenter_1F_Text_ManyTypesOfPokemon')
    t = [f.text('PetalburgCity_PokemonCenter_1F_Text_TreeckoIsGrassType'),
         f.text('PetalburgCity_PokemonCenter_1F_Text_TorchicIsFireType'),
         f.text('PetalburgCity_PokemonCenter_1F_Text_MudkipIsWaterType')]
    k = len(f.blocks) + 1
    out = f"""    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, {a}, 0, 0
    LastKeyWait
"""
    for i, sp in enumerate(('SPECIES_TREECKO', 'SPECIES_TORCHIC', 'SPECIES_MUDKIP')):
        out += f"""    WorkCmpConst VAR_STARTER_MON, {i}
    VMJumpIf CMP_NE, L_{k}_Not{i}
    PokePartyGetCountBySpecies {sp}, 0x8000
    WorkCmpConst 0x8000, 0
    VMJumpIf CMP_EQ, L_{k}_End
    ParentActorMsg MSGFILE_SCRIPT, {t[i]}, 0, 0
    LastKeyWait
    VMJump L_{k}_End
L_{k}_Not{i}:
"""
    return out + f"""L_{k}_End:
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def lanette(f, lid):
    """Sapphire: greeting, then she walks out (path by the side the player talks from), the door sound, removeobject
    (sets her hide flag) and clearflag FLAG_HIDE_LANETTE (her house on Route 114)."""
    g = f.text('FallarborTown_PokemonCenter_1F_Text_LanetteGreeting')
    k = len(f.blocks) + 1
    hide = ('#ifdef FLAG_HIDE_LANETTE_FALLARBOR\n    FlagSet FLAG_HIDE_LANETTE_FALLARBOR\n#endif\n'
            '#ifdef FLAG_HIDE_LANETTE\n    FlagReset FLAG_HIDE_LANETTE\n#endif\n')
    f.movements.append(f"""Movement_LanetteExitNorth:                       // Sapphire: right, down x2, left x4, down x4
    Move 15, 1
    Move 13, 2
    Move 14, 4
    Move 13, 4
    MoveEnd

Movement_LanetteExitWest:                        // Sapphire: down x2, left x3, down x4
    Move 13, 2
    Move 14, 3
    Move 13, 4
    MoveEnd
""")
    return f"""    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, {g}, 0, 0
    LastKeyWait
    ActorMsgClose
    PlayerGetDir 0x8000                          // 0 up (talking from her south), 2 left (from her east)
    WorkCmpConst 0x8000, 2
    VMJumpIf CMP_EQ, L_{k}_West
    ActorCmdExec {lid}, Movement_LanetteExitNorth
    VMJump L_{k}_Walk
L_{k}_West:
    ActorCmdExec {lid}, Movement_LanetteExitWest
L_{k}_Walk:
    ActorCmdWait
    ActorDelete {lid}
{hide}    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def mauville_man(f):
    """Sapphire picks the man from the player's trainer id (trainer id % 10 / 2, pokeruby mauville_man.c); Black 2's
    scripts can't read the trainer id, so VAR_MAUVILLE_OLD_MAN (hoenn.h: 0 not chosen, 1-5 Bard/Hipster/Trader/
    Storyteller/Giddy) is set at random once per save, by the map script when the Center loads (or here, if 0). The map
    script sets his sprite from it (object code 162 reads work 0x4020); his first line follows it too."""
    lines = [f.text(l) for _, l, _ in MAUVILLE_MEN]
    k = len(f.blocks) + 1
    out = f"""    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
#ifdef VAR_MAUVILLE_OLD_MAN
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 0         // not chosen yet (the map script normally has): choose now
    VMJumpIf CMP_NE, L_{k}_Chosen
    Random 0x8000, 5                             // 0-4, as Black 2's own scripts use it (0048.s Script_1)
    WorkSet VAR_MAUVILLE_OLD_MAN, 0x8000
    WorkAdd VAR_MAUVILLE_OLD_MAN, 1
L_{k}_Chosen:
"""
    for i in range(1, 5):
        out += f'    WorkCmpConst VAR_MAUVILLE_OLD_MAN, {i + 1}\n    VMJumpIf CMP_EQ, L_{k}_{MAUVILLE_MEN[i][0]}\n'
    out += f'#endif\n    ParentActorMsg MSGFILE_SCRIPT, {lines[0]}, 0, 0\n    VMJump L_{k}_End\n'
    for i in range(1, 5):
        out += f'L_{k}_{MAUVILLE_MEN[i][0]}:\n    ParentActorMsg MSGFILE_SCRIPT, {lines[i]}, 0, 0\n    VMJump L_{k}_End\n'
    return out + f"""L_{k}_End:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def mauville_init():
    out = """#ifdef VAR_MAUVILLE_OLD_MAN
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 0
    VMJumpIf CMP_NE, L_ManChosen
    Random 0x8000, 5
    WorkSet VAR_MAUVILLE_OLD_MAN, 0x8000
    WorkAdd VAR_MAUVILLE_OLD_MAN, 1                // 1 Bard .. 5 Giddy
L_ManChosen:
"""
    for i in range(1, 5):
        out += f'    WorkCmpConst VAR_MAUVILLE_OLD_MAN, {i + 1}\n    VMJumpIf CMP_EQ, L_Gfx{MAUVILLE_MEN[i][0]}\n'
    out += f'#endif\n    WorkSetConst 0x4020, {MAUVILLE_MEN[0][2]}           // the Bard\'s stand-in\n    VMHalt\n'
    for _, (nm, _, code) in enumerate(MAUVILLE_MEN[1:]):
        out += f'L_Gfx{nm}:\n    WorkSetConst 0x4020, {code}\n    VMHalt\n'
    return out

# Sapphire 2F attendants (data/scripts/cable_club.inc): before the Pokédex (Colosseum, Trade Center) or a visit to
# Mauville (Record Corner) they apologise; afterwards they invite you into the Cable Club, which this game cannot
# offer (no link rooms; Black 2's Union Room and Wi-Fi counters need its own warp-pad props, see the report): they
# keep their apology.
ATTENDANT = {   # Sapphire script -> (line before, gate flag, room)
    '1A3EA6': ('OldaleTown_PokemonCenter_2F_Text_1A13DF', 'FLAG_SYS_POKEDEX_GET', 'Colosseum'),
    '1A40CC': ('OldaleTown_PokemonCenter_2F_Text_1A141C', 'FLAG_SYS_POKEDEX_GET', 'Trade Center'),
    '1A41FB': ('OldaleTown_PokemonCenter_2F_Text_1A145C', 'FLAG_VISITED_MAUVILLE_CITY', 'Record Corner'),
}

def attendant_of(script):
    """The cable_club.inc routine a Center's 2F attendant script calls."""
    s = _text.get('s') or (sapphire_text() and _text['s'])
    body = ' '.join(s.get(script, []))
    if not body:      # two labels on one address (Pacifidlog's 2F uses Verdanturf's): the other label has the lines
        suffix = script.split('_EventScript_')[-1]
        body = ' '.join(' '.join(v) for k, v in s.items() if k.endswith('_EventScript_' + suffix))
    m = re.search(r'EventScript_(1A3EA6|1A40CC|1A41FB)', body)
    return m.group(1) if m else None

def person(f, name, lid, o):
    """(npc json entry, script number) for Sapphire object o; adds its script to f."""
    s, gfx = o['script'], o['graphics_id']
    code = (SPRITES.get(gfx) or {}).get('code')
    t = sapphire_text(); scripts = _text['s']
    if gfx == 'OBJ_EVENT_GFX_NURSE':
        n = f.add('#include "centers/nurse.inc"\n', f"nurse (7,2), Sapphire {s}: heals (Black 2's sequence)")
        return npc_entry(lid, o, 78, n, move=15)
    if s == 'MauvilleCity_PokemonCenter_1F_EventScript_1AE744':
        n = f.add(mauville_man(f), "Mauville's old man (Bard/Hipster/Trader/Storyteller/Giddy): first line only")
        f.init = mauville_init()
        f.notes.append('old man: Bard song (Easy Chat lyrics), Hipster words, Trader decorations, Storyteller tales, Giddy questions')
        return npc_entry(lid, o, 162, n)
    if s == 'FallarborTown_PokemonCenter_1F_EventScript_Lanette':
        n = f.add(lanette(f, lid), 'Lanette at the PC: greeting, walks out, her house on Route 114 opens')
        flag = DEFS.get('FLAG_HIDE_LANETTE_FALLARBOR', 0)
        if not flag: f.notes.append('Lanette: FLAG_HIDE_LANETTE_FALLARBOR / FLAG_HIDE_LANETTE not in hoenn.h yet (she comes back on re-entry)')
        return npc_entry(lid, o, code, n, flag=flag)
    if s == 'PetalburgCity_PokemonCenter_1F_EventScript_Woman':
        n = f.add(petalburg_woman(f), 'types talk + the starter\'s type (Sapphire IsStarterInParty)')
        return npc_entry(lid, o, code, n)
    if s == 'PetalburgCity_PokemonCenter_1F_EventScript_1B1B14':
        flag = 'FLAG_SYS_CHAT_USED'
        n = f.add(choose(f, flag, 'PetalburgCity_PokemonCenter_1F_Text_1B202F', 'PetalburgCity_PokemonCenter_1F_Text_1B1C97'),
                  'Mystery Event Club man: his greeting (the profile is Easy Chat, which Black 2 lacks)')
        f.notes.append('Mystery Event Club man: profile (Easy Chat) and the secret phrase that sets FLAG_SYS_EXDATA_ENABLE')
        return npc_entry(lid, o, code, n)
    if s == 'OldaleTown_PokemonCenter_1F_EventScript_Girl':
        n = f.add(choose(f, 'FLAG_SYS_POKEDEX_GET', 'OldaleTown_PokemonCenter_1F_Text_TradedInCableClub',
                         'OldaleTown_PokemonCenter_1F_Text_CableClubNotAvailable'), 'Cable Club talk (Pokédex)')
        return npc_entry(lid, o, code, n)
    if s == 'LilycoveCity_PokemonCenter_1F_EventScript_Maniac':
        n = f.add(choose(f, None, 'LilycoveCity_PokemonCenter_1F_Text_HaventSeenRottenScoundrels',
                         'LilycoveCity_PokemonCenter_1F_Text_HeardAboutRottenScoundrels',
                         test='    TrainerCardHasBadge 0x8000, 6                // Sapphire FLAG_BADGE07_GET (Mind Badge)\n'),
                  'Team Aqua talk (seventh badge)')
        return npc_entry(lid, o, code, n)
    if s in ('SootopolisCity_PokemonCenter_1F_EventScript_Gentleman', 'SootopolisCity_PokemonCenter_1F_EventScript_Woman'):
        late, calm = (('SootopolisCity_PokemonCenter_1F_Text_EveryoneTakenRefuge', 'SootopolisCity_PokemonCenter_1F_Text_WallaceToughestInHoenn')
                      if 'Gentleman' in s else ('SootopolisCity_PokemonCenter_1F_Text_ImReallyScared', 'SootopolisCity_PokemonCenter_1F_Text_AlwaysBeFriendsWithPokemon'))
        test = ('#if defined(FLAG_LEGENDARY_BATTLE_COMPLETED) && defined(FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN)\n'
                '    FlagGet FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, 0x8000   // set while the legend is loose ...\n'
                '    FlagGet FLAG_LEGENDARY_BATTLE_COMPLETED, 0x8001\n'
                f'    WorkCmpConst 0x8001, 1\n    VMJumpIf CMP_NE, L_SootoTest{lid}\n    WorkSetConst 0x8000, 0                     // ... until it is calmed\n'
                f'L_SootoTest{lid}:\n#else\n    WorkSetConst 0x8000, 0\n#endif\n')
        n = f.add(choose(f, None, late, calm, test=test), 'the weather crisis talk (Groudon/Kyogre awake)')
        return npc_entry(lid, o, code, n)
    lib = attendant_of(s)
    if lib:
        before, flag, room = ATTENDANT[lib]
        n = f.add(talk(f, f.text(before)), f'{room} attendant (Cable Club): Sapphire\'s apology')
        f.notes.append(f'{room} attendant: link play (Cable Club {room}; after {flag} Sapphire invites you in)')
        return npc_entry(lid, o, 79, n)
    label = __import__('gen_map_content').simple_message(s, t, scripts)
    assert label and code, (name, s, gfx)
    n = f.add(talk(f, f.text(label)), f"{gfx[14:].lower()}: {label.split('_Text_')[1]}")
    return npc_entry(lid, o, code, n)

# ------------------------------------------------------------------------------------------------ rooms
def test_menu(f):
    """Agent test only (CENTERS_TEST_BLACKOUT=1 and a HOENN_TEST_WARP build): Oldale's map lists the towns; the pick
    warps to the tile below that town's Center door (walk in: after a script warp, A does nothing until a door)."""
    sys.path.insert(0, os.path.join(HERE, 'patches'))
    import centers
    out = '#ifdef HOENN_TEST_WARP\n    ActorsPauseAll\n    ListMenu_AnchorTopRight 31, 1, 0, 1, 0x8000\n'
    goes = []
    for z, (town, tz) in sorted(centers.center_towns().items(), key=lambda kv: kv[1][0]):
        t = centers.door_tile(town, tz, z)
        if not t: continue
        i = len(goes)
        out += f'    ListMenuAdd {f.text(town, raw=True)}, 65535, {i}\n'
        goes.append(f'L_TestGo{i}:\n    MapChangeCore {tz}, {t[0]}, 0, {t[1]}, 1\n    FinishAllEvents\n    ActorsUnpauseAll\n    VMHalt\n')
    out += '    ListMenuShow\n'
    for i in range(len(goes)): out += f'    WorkCmpConst 0x8000, {i}\n    VMJumpIf CMP_EQ, L_TestGo{i}\n'
    out += '    FinishAllEvents\n    ActorsUnpauseAll\n    VMHalt\n' + ''.join(goes) + '#endif\n'
    return out

_bgm = {}
def header_override(name, tz):
    """Zone header fields this room needs and the interiors patch does not set yet (request to the lead: apply a
    json "header" dict to the zone header last): every Center is named after its Hoenn town (13 of Black 2's Center
    zones carry an Unova town's parent/place), and the 2F (a house header via "parent") plays the Center music."""
    out = dict(parent=tz['zone'], place=tz['place'])
    if name.endswith('_2F'):
        if not _bgm:
            import zoneheaders
            h = zoneheaders.load(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'))[0][ALL[MASTER_1F]['zone']]
            _bgm.update({k: h[k] for k in ('bgm0', 'bgm1', 'bgm2', 'bgm3')})     # SEQ_BGM_POKECEN (Black 2's Centers)
        out.update(_bgm)
    return out

def build_room(name):
    r = ROOMS[name]; zone = r['zone']
    town = name.split('_PokemonCenter')[0]
    j = json.load(open(os.path.join(RUBY, name, 'map.json')))
    f = File(name, name.endswith('_1F')); f.movements = []; f.init = None
    npcs = []
    for lid, o in enumerate(j['object_events'], 1):
        npcs.append(person(f, name, lid, o))
    signs = []
    if name.endswith('_1F'):
        if name != 'LavaridgeTown_PokemonCenter_1F':
            body = sign(f, f.text(BOOKSHELF))
            if os.environ.get('CENTERS_TEST_BLACKOUT'):      # agent test only: the shelf makes you black out
                body = ('#ifdef HOENN_TEST_WARP\n    ActorsPauseAll\n    CallWildBattle 150, 100, 1\n    WildBattleIsVictory 0x8010\n'
                        '    WorkCmpConst 0x8010, 1\n    VMJumpIf CMP_EQ, L_TestWon\n    CallWildLose\nL_TestWon:\n    CallWildBattleEnd\n'
                        '    FinishAllEvents\n    ActorsUnpauseAll\n    VMHalt\n#endif\n' + body)
            n = f.add(body, 'magazine shelf (Sapphire MB_POKEMON_CENTER_BOOKSHELF)')
            signs += [dict(script=n, at=[2, 1], dir=0), dict(script=n, at=[3, 1], dir=0)]
        body = region_map(f, f.text(REGION_MAP))
        if os.environ.get('CENTERS_TEST_BLACKOUT') and name == MASTER_1F:   # agent test only: a town menu that
            body = test_menu(f) + body                                     # puts you below each Center's door
        n = f.add(body, 'Hoenn map (Sapphire MB_REGION_MAP opens the map screen)')
        signs += [dict(script=n, at=[11, 1], dir=0), dict(script=n, at=[12, 1], dir=0)]
    # Sapphire's OnTransition of nine Centers: call Common_EventScript_UpdateBrineyLocation (story_infra, 2026-10-07):
    # Mr. Briney's whereabouts (src/field_scripts/common/briney.inc), first thing in the zone init
    briney = 'UpdateBrineyLocation' in open(os.path.join(RUBY, name, 'scripts.inc')).read()
    if briney:
        f.init = ('    VMCall Sub_UpdateBrineyLocation                // Sapphire: call Common_EventScript_UpdateBrineyLocation\n'
                  + (f.init or '    VMHalt\n'))
    tz = ZONES[town]
    cfg = dict(zone=zone, room=name, area=AREA,
               what=f'{name}: centers agent (b2tools/centers_rooms.py); recipe data/interior_layouts/{name}.json',
               header=header_override(name, tz),
               warps=warps_of(name), npcs=npcs, signs=signs)
    if name.endswith('_2F'): cfg['parent'] = tz['zone']      # interiors.py: a house header named after the town
    # files
    old = glob.glob(os.path.join(OUT_S, f"{r['scripts']:04d}_*.s")) + glob.glob(os.path.join(OUT_S, f"{r['init_scripts']:04d}_*.s")) \
        + glob.glob(os.path.join(OUT_T, f"{r['text']:04d}_*.txt"))
    for p in old:
        if not os.path.basename(p).split('_', 1)[1].startswith('room_'):
            raise SystemExit(f'{p} is not ours')
    sname = os.path.join(OUT_S, f"{r['scripts']:04d}_room_{name}.s")
    entries = ''.join(f'    ScriptEntry Script_{i}\n' for i in range(1, len(f.blocks) + 1 + (1 if f.init else 0)))
    body = ''.join(f'Script_{i}:                                    // {c}\n{b}\n' for i, (c, b) in enumerate(f.blocks, 1))
    if f.init:
        body += (f'Script_{len(f.blocks) + 1}:                                    // map script (zone init): '
                 + ('Mr. Briney\'s whereabouts' if briney else '') + (', ' if briney and 'Mauville' in name else '')
                 + ('the old man\'s sprite' if 'Mauville' in name else '') + f'\n{f.init}\n')
    src = (f'// {name} (zone {zone}): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the\n'
           f'// generator). Room: data/interior_layouts/{name}.json, people/signs/warps: data/interiors/{zone}.json.\n'
           f"// Messages: src/text/script/{r['text']:04d}_room_{name}.txt (Sapphire's words, Gen 5 capitalisation).\n"
           f'// Actors = Sapphire local ids. The PC is the pc01 model on a 0xd6 tile (Black 2 runs its PC script itself).\n'
           '#include "asm/field_script.inc"\n#include "hoenn.h"\n' + ('#include "hoenn_story.inc"\n' if briney else '') + '\n'
           + entries + '    ScriptEntriesEnd\n\n' + body
           + ('    .balign 4, 0\n\n' + '\n'.join(f.movements) if f.movements else '') + '    .balign 4, 0\n'
           + ('#include "common/briney.inc"\n' if briney else ''))
    files = {sname: src, os.path.join(OUT_T, f"{r['text']:04d}_room_{name}.txt"): '\n'.join(f.msgs) + '\n'}
    if f.init:
        files[os.path.join(OUT_S, f"{r['init_scripts']:04d}_room_{name}_init.s")] = (
            f'// Map scripts of {name} (zone {zone}; installed by b2tools/patches/interiors.py): zone init = script '
            f'{len(f.blocks) + 1}\n// (before the people appear: Mr. Briney\'s whereabouts / the old man\'s sprite).\n#include "asm/field_script.inc"\n\n'
            f'    MapScript 2, {len(f.blocks) + 1}\n    MapScriptsEnd\n    .balign 4, 0\n')
    for p in old:
        if p not in files:
            import shutil; shutil.move(p, os.path.join(os.path.expanduser('~/.Trash'), os.path.basename(p)))
    from story_merge import write_room_script, write_room_text      # a story agent's part (after "// ---- story") stays
    for p, t in files.items():
        if p == sname: write_room_script(p, t)
        elif p.endswith('.txt') and p.startswith(OUT_T): write_room_text(p, t.rstrip('\n').split('\n'), sname)
        else: write(p, t)
    write(os.path.join(ROOT, 'data', 'interiors', f'{zone}.json'), dumps(cfg) + '\n')
    return f.notes

# ------------------------------------------------------------------------------------------------ tile classes
def classes():
    """Recipe key "classes": {"0xd4": [[x, z], ...]} -> those tiles' cells in the built collision.per get that tile
    class (u32 at +4: class | flags << 16; solid stays solid). Black 2: 0xd4 reception counter (talk across it),
    0xd6 PC. Until b2tools/models_interior.py writes them itself (lead), run after building the rooms."""
    done = []
    for name in sorted(ROOMS):
        r = __import__('models_interior').load_recipe(name)
        cl = r.get('classes')
        p = os.path.join(ROOMS_DIR, name, 'collision.per')
        if not cl or not os.path.exists(p): continue
        meta = json.load(open(os.path.join(ROOMS_DIR, name, 'room.json')))
        ox, oz = meta['origin']
        per = bytearray(open(p, 'rb').read())
        for c, tiles in cl.items():
            for x, z in tiles:
                at = 4 + 8 * ((oz + z) * 32 + ox + x) + 4
                v = struct.unpack_from('<I', per, at)[0]
                struct.pack_into('<I', per, at, (v & 0xFFFF0000) | int(c, 0))
        open(p, 'wb').write(per)
        done.append(name)
    return done

def main(args):
    if args and args[0] == 'classes':
        print('tile classes:', ', '.join(classes()) or 'none (build the rooms first)'); return
    sys.path.insert(0, os.path.join(HERE, 'patches'))
    print('recipes written:', ', '.join(write_recipes()) or 'none changed')
    notes = {}
    for name in sorted(ROOMS):
        notes[name] = build_room(name)
    for n, l in notes.items():
        for x in l:
            if 'attendant' not in x: print(f'{n}: missing: {x}')      # (the 45 Cable Club attendants: by design)
    for u in UNRESOLVED: print('unresolved warp:', u)

if __name__ == '__main__':
    main(sys.argv[1:])
