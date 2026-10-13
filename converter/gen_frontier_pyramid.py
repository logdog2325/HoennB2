"""Emerald's Battle Pyramid data -> data/emerald/frontier_pyramid.json (frontier_pyramid, 2026-10-12; notes/FRONTIER_PYRAMID.md).
b2tools/patches/frontier_pyramid.py packs it for the Pyramid's engine (b2tools/patches/frontier_pyramid.c) in an
Emerald build; the three rooms' texts go to src/text/script/emerald/ and their line numbers to
src/field_scripts/scenes/frontier_pyramid_lines.inc.

    python3 gen_frontier_pyramid.py         (reads external/pokeemerald and data/emerald/frontier_pike.json only)

Sources (pokeemerald): src/battle_pyramid.c (floor templates and their odds, the pick-up items and their odds, the
bordered squares, the trainers' hint text groups and hint types, the light), the 16 squares
data/layouts/BattlePyramidSquareNN/map.bin (8x8 metatiles: walls = collision, the exit metatile 0x28E) and their maps'
object events (where trainers and item balls may stand), src/data/battle_frontier/battle_pyramid_*_wild_mons.h (the 20
rounds' wild Pokemon), src/data/wild_encounters.json gBattlePyramid_1-7 (each floor's rate and land slots: the slot's
placeholder species = the index in the round's table + 1), src/frontier_util.c (Brandon's parties, his streaks),
src/battle_tower.c (the Frontier trainer ranges), the Pyramid maps' and data/text texts. The 300 Frontier trainers
(names, classes, sprites, greetings, defeat lines, sets) are frontier_pike's (data/emerald/frontier_pike.json)."""
import os, re, sys, json, struct
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
os.environ['HOENN_VERSION'] = 'emerald'
from gen3text import convert  # noqa: E402
import gen_battle_tower as gbt  # noqa: E402

EM = os.path.join(ROOT, 'external', 'pokeemerald')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
OUT = os.path.join(ROOT, 'data', 'emerald', 'frontier_pyramid.json')
PIKE = os.path.join(ROOT, 'data', 'emerald', 'frontier_pike.json')
MOVE_ALIAS = {'MOVE_SELF_DESTRUCT': 'MOVE_SELFDESTRUCT', 'MOVE_SMOKESCREEN': 'MOVE_SMOKE_SCREEN', 'MOVE_SOFT_BOILED': 'MOVE_SOFTBOILED'}
ITEM_ALIAS = {}
NATURES = ['HARDY', 'LONELY', 'BRAVE', 'ADAMANT', 'NAUGHTY', 'BOLD', 'DOCILE', 'RELAXED', 'IMPISH', 'LAX', 'TIMID', 'HASTY',
           'SERIOUS', 'JOLLY', 'NAIVE', 'MODEST', 'MILD', 'QUIET', 'BASHFUL', 'RASH', 'CALM', 'GENTLE', 'SASSY', 'CAREFUL',
           'QUIRKY']
EXIT_METATILE, FLOOR_METATILE = 0x28E, 0x28D
OBJ_POS = {'OBJ_POSITIONS_UNIFORM': 0, 'OBJ_POSITIONS_IN_AND_NEAR_ENTRANCE': 1, 'OBJ_POSITIONS_IN_AND_NEAR_EXIT': 2,
           'OBJ_POSITIONS_NEAR_ENTRANCE': 3, 'OBJ_POSITIONS_NEAR_EXIT': 4}
HINTS = {'HINT_EXIT_DIRECTION': 0, 'HINT_REMAINING_ITEMS': 1, 'HINT_REMAINING_TRAINERS': 2,
         'HINT_EXIT_SHORT_REMAINING_TRAINERS': 3, 'HINT_EXIT_SHORT_REMAINING_ITEMS': 4,
         'HINT_EXIT_MEDIUM_REMAINING_TRAINERS': 5, 'HINT_EXIT_MEDIUM_REMAINING_ITEMS': 6,
         'HINT_EXIT_FAR_REMAINING_TRAINERS': 7, 'HINT_EXIT_FAR_REMAINING_ITEMS': 8}
NUMBERS = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight']

def em(*p):
    return open(os.path.join(EM, *p), encoding='utf-8').read()

def block(src, name):
    m = re.search(rf'{re.escape(name)}\s*(?:\[[^\]]*\])*\s*=\s*\{{(.*?)\n\}};', src, re.S)
    assert m, name
    return m.group(1)

def nums(s):
    return [int(x, 0) for x in re.findall(r'-?(?:0x[0-9a-fA-F]+|\d+)', s)]

def squares():
    """The 16 squares: walls (8 rows of 8: '#' wall, '.' floor), the exit metatile's tile, the object events (x, y,
    'trainer' / 'item', Black 2 move code + facing, sight) in their map.json order (Emerald's placement scans them in
    that order)."""
    import move_codes
    lay = {l['id']: l for l in json.load(open(os.path.join(EM, 'data', 'layouts', 'layouts.json')))['layouts'] if 'id' in l}
    out = []
    for i in range(1, 17):
        l = lay[f'LAYOUT_BATTLE_PYRAMID_SQUARE{i:02d}']
        assert (l['width'], l['height']) == (8, 8)
        raw = open(os.path.join(EM, l['blockdata_filepath']), 'rb').read()
        v = struct.unpack('<64H', raw)
        walls, exit_ = [], None
        for y in range(8):
            row = ''
            for x in range(8):
                c = v[y * 8 + x]
                mt, coll = c & 0x3FF, (c >> 10) & 3
                if mt == EXIT_METATILE: exit_ = [x, y]
                row += '#' if coll else '.'
            walls.append(row)
        assert exit_ is not None, i
        mj = json.load(open(os.path.join(EM, 'data', 'maps', f'BattlePyramidSquare{i:02d}', 'map.json')))
        objs = []
        for o in mj['object_events']:
            item = o['graphics_id'] == 'OBJ_EVENT_GFX_ITEM_BALL'
            mv = move_codes.npc(o['movement_type'].replace('MOVEMENT_TYPE_', ''), (o['movement_range_x'], o['movement_range_y']))
            objs.append(dict(x=o['x'], y=o['y'], kind='item' if item else 'trainer',
                             move=0 if item else mv['move'], dir=mv.get('dir', 1) if not item else 1,
                             sight=0 if item else int(o['trainer_sight_or_berry_tree_id']),
                             movement=o['movement_type']))
            assert walls[o['y']][o['x']] == '.', (i, o)
        out.append(dict(name=f'BattlePyramidSquare{i:02d}', walls=walls, exit=exit_, objects=objs))
    return out

def pyramid_c():
    s = em('src', 'battle_pyramid.c')
    tpl = []
    for body in re.findall(r'\{\s*(\.numItems.*?)\n    \}', block(s, 'static const struct PyramidFloorTemplate sPyramidFloorTemplates'), re.S):
        d = dict(re.findall(r'\.(\w+) = (\{[^}]*\}|[^,\n]+)', body))
        tpl.append(dict(num_items=int(d['numItems']), num_trainers=int(d['numTrainers']),
                        item_positions=OBJ_POS[d['itemPositions']], trainer_positions=OBJ_POS[d['trainerPositions']],
                        run_multiplier=int(d['runMultiplier']), layout_offsets=nums(d['layoutOffsets'])))
    assert len(tpl) == 16 and all(len(t['layout_offsets']) == 8 for t in tpl)
    opts = [nums(r) for r in re.findall(r'\{([^{}]*)\}', block(s, 'static const u8 sPyramidFloorTemplateOptions'))]
    offs = nums(block(s, 'static const u8 sFloorTemplateOffsets'))
    b2i = gbt.defines(f'{B2}/include/constants/items.h', 'ITEM_')
    def items(name):
        rows = [re.findall(r'ITEM_\w+', r) for r in re.findall(r'\{([^{}]*)\}', block(s, name))]
        assert len(rows) == 20 and all(len(r) == 10 for r in rows)
        return [[b2i[ITEM_ALIAS.get(x, x)] for x in r] for r in rows], rows
    lv50, lv50n = items('static const u16 sPickupItemsLvl50')
    lvopen, _ = items('static const u16 sPickupItemsLvlOpen')
    slots = [nums(r) for r in re.findall(r'\{([^{}]*)\}', block(s, 'static const u8 sPickupItemSlots'))]
    slot_offs = nums(block(s, 'static const u8 sPickupItemOffsets'))
    bordered = [[x & 0xFF for x in nums(r)] for r in re.findall(r'\{([^{}]*)\}', block(s, 'static const u8 sBorderedSquareIds'))]
    groups = {c: g for c, g in re.findall(r'\{FACILITY_CLASS_(\w+),\s*(\d+)\}', block(s, 'static const u8 sTrainerTextGroups'))}
    hint_types = [HINTS[h] for h in re.findall(r'HINT_\w+', block(s, 'static const u8 sHintTextTypes'))]
    assert len(slots) == 63 and len(bordered) == 16 and len(hint_types) == 8 and len(opts) == 34
    return dict(templates=tpl, template_options=opts, template_offsets=offs, pickup_50=lv50, pickup_open=lvopen,
                pickup_slots=slots, pickup_offsets=slot_offs, bordered=bordered,
                text_groups={k: int(v) for k, v in groups.items()}, hint_types=hint_types,
                start_items=[b2i['ITEM_HYPER_POTION'], b2i['ITEM_ETHER']]), lv50n

def wild():
    b2s = gbt.defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2m = gbt.defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    out = {}
    for key, fn, arr in (('50', 'battle_pyramid_level_50_wild_mons.h', 'sLevel50WildMons_Round'),
                         ('open', 'battle_pyramid_open_level_wild_mons.h', 'sOpenLevelWildMons_Round')):
        s = em('src', 'data', 'battle_frontier', fn)
        rounds = []
        for r in range(1, 21):
            body = re.search(rf'{arr}{r}\[\] =\s*\{{(.*?)\n\}};', s, re.S).group(1)
            mons = []
            for sp, lv, ab, mv in re.findall(r'\.species = SPECIES_(\w+),\s*\.lvl = (\d+),\s*\.abilityNum = (\w+),\s*\.moves = \{(.*?)\}', body, re.S):
                mvs = re.findall(r'MOVE_\w+', mv)
                mons.append(dict(species=sp, species_id=b2s['SPECIES_' + sp], lvl=int(lv),
                                 ability=2 if ab == 'ABILITY_RANDOM' else int(ab),
                                 moves=mvs, move_ids=[0 if x == 'MOVE_NONE' else b2m[MOVE_ALIAS.get(x, x)] for x in mvs]))
            assert len(mons) == 8, (key, r, len(mons))
            rounds.append(mons)
        out[key] = rounds
    ptr = em('src', 'data', 'battle_frontier', 'battle_pyramid_level_50_wild_mons.h')
    assert 'sLevel50WildMons_Round20' in ptr
    enc = json.load(open(os.path.join(EM, 'src', 'data', 'wild_encounters.json')))
    order = ['BULBASAUR', 'IVYSAUR', 'VENUSAUR', 'CHARMANDER', 'CHARMELEON', 'CHARIZARD', 'SQUIRTLE', 'WARTORTLE']
    floors = {}
    for g in enc['wild_encounter_groups']:
        for e in g['encounters']:
            m = re.match(r'gBattlePyramid_(\d)$', e.get('base_label', ''))
            if m:
                lm = e['land_mons']
                floors[int(m.group(1))] = dict(rate=lm['encounter_rate'], slots=[order.index(x['species'][8:]) for x in lm['mons']],
                                               level=lm['mons'][0]['min_level'])
    assert sorted(floors) == list(range(1, 8)) and all(len(f['slots']) == 12 for f in floors.values())
    return out, [floors[i] for i in range(1, 8)]

def brandon():
    b2s = gbt.defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2m = gbt.defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    b2i = gbt.defines(f'{B2}/include/constants/items.h', 'ITEM_')
    s = em('src', 'frontier_util.c')
    mons = s[s.index('sFrontierBrainsMons[]'):]
    body = re.search(r'\[FRONTIER_FACILITY_PYRAMID\] =\s*\{(.*?)\n\};', mons, re.S).group(1)
    parties = []
    for sym in re.split(r'// (?:Silver|Gold) Symbol\.', body)[1:]:
        mons = []
        for sp, item, iv, nat, evs, mv in re.findall(r'\.species = SPECIES_(\w+),\s*\.heldItem = (ITEM_\w+),\s*\.fixedIV = (\w+),\s*'
                                                     r'\.nature = NATURE_(\w+),\s*\.evs = \{(.*?)\},\s*\.moves = \{(.*?)\}', sym, re.S):
            mvs = re.findall(r'MOVE_\w+', mv)
            mons.append(dict(species=sp, species_id=b2s['SPECIES_' + sp], item=item, item_id=b2i[ITEM_ALIAS.get(item, item)],
                             iv=31 if iv == 'MAX_PER_STAT_IVS' else int(iv), nature=NATURES.index(nat),
                             evs=[int(x) for x in evs.split(',')], moves=mvs, move_ids=[b2m[MOVE_ALIAS.get(x, x)] for x in mvs]))
        assert len(mons) == 3
        parties.append(mons)
    assert len(parties) == 2
    streaks = nums(re.search(r'\[FRONTIER_FACILITY_PYRAMID\] = \{([^}]*)\}', s).group(1))
    assert streaks == [21, 70, 35, 0], streaks
    return parties, streaks

def trainer_ranges():
    s = em('src', 'battle_tower.c')
    names = {k: i for i, k in enumerate(re.findall(r'\[(FRONTIER_TRAINER_\w+)\] = \{', em('src', 'data', 'battle_frontier', 'battle_frontier_trainers.h')))}
    def rng(name):
        return [[names[a], names[b]] for a, b in re.findall(r'\{(FRONTIER_TRAINER_\w+),\s*(FRONTIER_TRAINER_\w+)\}', block(s, name))]
    return rng('static const u16 sFrontierTrainerIdRanges'), rng('static const u16 sFrontierTrainerIdRangesHard')

# -------------------------------------------------------------------------------------------------------- texts
P = 'BattleFrontier_BattlePyramid'
LOBBY_ROLES = dict(TAKE='EmbarkOnChallenge', STEP='ShowYouIntoPyramid', DIDNT_SAVE='DidntSaveBeforeQuittingTakeBag',
                   WON='YouveConqueredPyramid', LOST='DisappointingHereIsBag', RESUME='ShowYouIntoPyramid',
                   GOODBYE='AwaitFutureChallenge')
LOBBY = [   # after the lobby text block (frontier_core's 23 lines)
    ('HOLD_BAG', 'WeWillHoldBagForSafekeeping'), ('TAKE_PREV_BAG', 'PleaseTakePreviousBattleBag'),
    ('TAKE_NEW_BAG', 'PleaseTakeThisBattleBag'), ('EXCHANGED', 'ExchangedBagForBattleBag'), ('STEP_PANEL', 'StepOnFloorPanel'),
    ('HOLDING_CANT_TAKE', 'MonHoldingItemCannotTake'), ('HELD_MOVED', 'HeldItemsMovedToBag'),
    ('BAG_CANT_HOLD', 'BagCannotHoldPickItemsToKeep'), ('LEAST_ONE_HOLDING', 'LeastOneMonHoldingItem'),
    ('PICK_TO_KEEP', 'PickItemsToKeep'), ('RETURNED_HELD', 'ReturnedEverythingMonsHeld'), ('BAG_KEPT', 'UsedBattleBagWillBeKept'),
    ('NEXT_CHALLENGE', 'LookForwardToNextChallenge'), ('MISFORTUNES', 'TellYouWhatMisfortunesAwait'), ('AAH', 'Aah'),
    ('HINT_PARALYSIS', 'HintParalysis'), ('HINT_POISON', 'HintPoison'), ('HINT_BURN', 'HintBurn'), ('HINT_PP', 'HintPPWaste'),
    ('HINT_LEVITATE', 'HintLevitate'), ('HINT_TRAP', 'HintTrapAbility'), ('HINT_ICE', 'HintIce'), ('HINT_EXPLOSION', 'HintExplosion'),
    ('HINT_PSYCHIC', 'HintPsychic'), ('HINT_ROCK', 'HintRock'), ('HINT_FIGHTING', 'HintFighting'), ('HINT_WEATHER', 'HintWeather'),
    ('HINT_BUG', 'HintBug'), ('HINT_DARK', 'HintDark'), ('HINT_WATER', 'HintWater'), ('HINT_GHOST', 'HintGhost'),
    ('HINT_STEEL', 'HintSteel'), ('HINT_FLYING_DRAGON', 'HintFlyingDragon'), ('HINT_STONE', 'HintStoneEvolve'),
    ('HINT_NORMAL', 'HintNormal'), ('BELIEVE', 'BelieveMyFortunesOrNot'), ('WOMAN', 'TrainersNoticeRunning'),
    ('FAT_MAN', 'LostLotOfItems'), ('RULES_LISTED', 'RulesAreListed'), ('READ_WHICH', 'ReadWhichHeading'),
    ('RULE_MONS', 'ExplainMonRules'), ('RULE_TRAINERS', 'ExplainTrainerRules'), ('RULE_MAZE', 'ExplainMazeRules'),
    ('RULE_BAG', 'ExplainBagRules'),
    ('M_RULE_MONS', '=Pokémon'), ('M_RULE_TRAINERS', '=Trainers'), ('M_RULE_MAZE', '=Maze'), ('M_RULE_BAG', '=Battle Bag'),
    ('M_EXIT', '=Exit'),
    # Emerald's party menu refuses a Pokemon that holds an item in this lobby (GetBattleEntryEligibility): Black 2's
    # pick screen has no such rule, so the attendant checks the picks afterwards with Emerald's own words
    ('CANT_PARTICIPATE', '!gText_PkmnCantParticipate'),
    # the results board (Emerald's frontier_results window, ShowPyramidResultsWindow) as messages
    ('RES_TITLE', "={0100:0}’s Battle Quest Results"),
    ('RES_50_CUR', "=Lv. 50  Current: Floors cleared: {0100:1}\\nRecord: Floors cleared: {0100:2}"),
    ('RES_50_PREV', "=Lv. 50  Prev.: Floors cleared: {0100:1}\\nRecord: Floors cleared: {0100:2}"),
    ('RES_OPEN_CUR', "=Open Lv.  Current: Floors cleared: {0100:1}\\nRecord: Floors cleared: {0100:2}"),
    ('RES_OPEN_PREV', "=Open Lv.  Prev.: Floors cleared: {0100:1}\\nRecord: Floors cleared: {0100:2}"),
]
TOP = [
    ('SUMMIT', 'ReachedSummitUpYouGo'), ('CONQUERED', 'PlayerConqueredPyramid'), ('CHIEF_HERE', 'ChiefBeatYouHere'),
    ('EXPLORATIONS', 'ExplorationsAreGrandestAdventure'), ('IM_BRANDON', 'ImPyramidKingBrandon'),
    ('BRING_COURAGE', 'BringCourageToOurBattle'), ('PASS_PLEASE', 'BrandonFrontierPassPlease'),
    ('RECEIVED_SYMBOL', 'ReceivedBraveSymbol'), ('NEXT_MEETING', 'LookForwardToNextMeeting'),
    ('RETURNED', 'BrandonYouveReturned'), ('OFF_METER', 'MyCourageIsOffMeter'), ('EVERYTHING', 'EverythingYouHave'),
    ('REMARKABLE', 'BrandonRemarkableHaveThis'), ('GOLDEN', 'BraveSymbolTookGoldenShine'), ('FAREWELL', 'FarewellForNow'),
    ('STEP_FORWARD', 'StepForwardWhenReady'),
]

def write_texts(trainers, groups_of):
    from gen_trainers import load_texts
    import frontier_text
    tx = load_texts(EM)
    def cv(label):
        raw = tx[label] if label in tx else frontier_text.strings_c(label).replace('{PAUSE_UNTIL_PRESS}', '')
        raw = raw.replace('{STR_VAR_1} ineligible', ' are ineligible')
        raw = raw.replace('{STR_VAR_1}', '\x01').replace('{STR_VAR_2}', '\x02').replace('{STR_VAR_3}', '\x03')
        line, unknown = convert(raw, expand=True)
        assert not unknown, (label, unknown)
        return line.replace('\x01', '{0100:1}').replace('\x02', '{0100:2}').replace('\x03', '{0100:3}')
    defs = ['// The Battle Pyramid rooms\' text lines (src/text/script/emerald/0559/0600/0649_room_*.txt). GENERATED by',
            '// converter/gen_frontier_pyramid.py (write_texts): do not edit.', '#ifndef FRONTIER_PYRAMID_LINES_INC',
            '#define FRONTIER_PYRAMID_LINES_INC']
    files = {}
    # ---- the lobby (text 559): frontier_core's lobby block, then the lines above
    lob = [t for _, _, t in frontier_text.lobby_block(P + 'Lobby', LOBBY_ROLES)]
    defs.append('#define PYL_LOBBY_TB 0')
    for name, label in LOBBY:
        if label.startswith('='): line = label[1:]
        elif label.startswith('!'): line = cv(label[1:])
        else: line = cv(f'{P}Lobby_Text_{label}')
        defs.append(f'#define PYL_LOBBY_{name} {len(lob)}')
        lob.append(line)
    files[559] = (P + 'Lobby', lob)
    # ---- a floor (text 600): the hints by text group (6 x (4 exit directions, 9 item counts, 8 trainer counts)), the
    # finding / Bag lines, the rest / retire questions, the 300 Frontier trainers' greetings and defeat lines
    fl = []
    defs.append(f'#define PYL_FLOOR_HINTS {len(fl)}      /* + 21 * group: 0-3 exit up/left/right/down, 4-12 items 0-8, 13-20 trainers 0-7 */')
    for g in range(1, 7):
        for d in ('Up', 'Left', 'Right', 'Down'): fl.append(cv(f'BattlePyramid_Text_ExitHint{d}{g}'))
        for n in range(9): fl.append(cv(f'BattlePyramid_Text_{NUMBERS[n]}ItemsRemaining{g}' if n != 1 else f'BattlePyramid_Text_OneItemRemaining{g}'))
        for n in range(8): fl.append(cv(f'BattlePyramid_Text_{NUMBERS[n]}TrainersRemaining{g}'))
    for name, label in (('FOUND', 'gText_PlayerFoundOneItem'), ('PUT_AWAY', 'gText_PlayerPutItemInBag'),
                        ('OBTAINED', 'gText_ObtainedTheItem'), ('BAG_FULL', 'gText_TooBadBagIsFull'),
                        ('CONFIRM_REST', 'gText_BattlePyramidConfirmRest'), ('CONFIRM_RETIRE', 'gText_BattlePyramidConfirmRetire')):
        defs.append(f'#define PYL_FLOOR_{name} {len(fl)}')
        fl.append(cv(label))
    for name, line in (('M_REST', 'Rest'), ('M_RETIRE', 'Retire'), ('M_CANCEL', 'Cancel'),
                       ('FLOOR_NAME', 'Battle Pyramid\\n{0100:1}'), ('SAVING', 'Saving…\\nDon’t turn off the power.')):
        defs.append(f'#define PYL_FLOOR_{name} {len(fl)}')
        fl.append(line)
    defs.append(f'#define PYL_FLOOR_INTRO {len(fl)}')
    fl += [t['intro'] for t in trainers]
    defs.append(f'#define PYL_FLOOR_LOSE {len(fl)}')
    fl += [t['lose'] for t in trainers]
    defs.append(f'#define PYL_FLOOR_BRANDON_LOSE {len(fl)}     /* + 0 silver, 1 gold (what Brandon says when beaten) */')
    for lab in ('gText_BrandonDefeatSilver', 'gText_BrandonDefeatGold'): fl.append(cv(lab))
    files[600] = (P + 'Floor', fl)
    # ---- the top (text 649)
    top = []
    for name, label in TOP:
        defs.append(f'#define PYL_TOP_{name} {len(top)}')
        top.append(cv(f'{P}Top_Text_{label}'))
    for name, label in (('CONFIRM_REST', 'gText_BattlePyramidConfirmRest'), ('CONFIRM_RETIRE', 'gText_BattlePyramidConfirmRetire')):
        defs.append(f'#define PYL_TOP_{name} {len(top)}')
        top.append(cv(label))
    for name, line in (('M_REST', 'Rest'), ('M_RETIRE', 'Retire'), ('M_CANCEL', 'Cancel'), ('SAVING', 'Saving…\\nDon’t turn off the power.')):
        defs.append(f'#define PYL_TOP_{name} {len(top)}')
        top.append(line)
    defs.append(f'#define PYL_TOP_BRANDON_LOSE {len(top)}')
    for lab in ('gText_BrandonDefeatSilver', 'gText_BrandonDefeatGold'): top.append(cv(lab))
    files[649] = (P + 'Top', top)
    defs.append('#endif')
    for num, (room, lines) in files.items():
        path = os.path.join(ROOT, 'src', 'text', 'script', 'emerald', f'{num:04d}_room_{room}.txt')
        open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    open(os.path.join(ROOT, 'src', 'field_scripts', 'scenes', 'frontier_pyramid_lines.inc'), 'w', encoding='utf-8').write('\n'.join(defs) + '\n')
    return {n: len(l) for n, (_, l) in files.items()}

def main():
    pike = json.load(open(PIKE, encoding='utf-8'))
    trainers = pike['trainers']
    sq = squares()
    tables, item_names = pyramid_c()
    wm, floors = wild()
    br, streaks = brandon()
    rng, hard = trainer_ranges()
    groups = tables['text_groups']
    tgroup = [groups.get(t['facility_class'], 0) for t in trainers]
    counts = write_texts(trainers, groups)
    doc = __doc__.strip().split('\n\n')[0] + ' GENERATED by converter/gen_frontier_pyramid.py.'
    json.dump(dict(_doc=doc, squares=sq, **tables, wild=wm, wild_floors=floors, brandon=br, brain_streaks=streaks,
                   trainer_ranges=rng, trainer_ranges_hard=hard, trainer_text_group=tgroup,
                   pickup_names_round1=item_names[0]),
              open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'{len(sq)} squares, {len(tables["templates"])} floor templates, wild 2 x {len(wm["50"])} rounds, Brandon '
          f'{[m["species"] for p in br for m in p]}, texts {counts} -> {os.path.relpath(OUT, ROOT)}')

if __name__ == '__main__':
    main()
