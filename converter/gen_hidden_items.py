"""Sapphire's hidden items as Black 2 hidden items (S_common: obtain_item.inc EventScript_HiddenItem).

    python3 gen_hidden_items.py   -> data/hoenn_hidden_items.json (registry), src/field_scripts/1241_hidden_items.s,
                                     data/story/hidden_items.json (the signs, placed by b2tools/patches/story.py)

Black 2's hidden items (checked in its zone entities and script file 1241): a sign entity with cond 2, dir 4 and script
7999 + n (global ids 8000-8212 = file 1241 Script_1-213, GLOBAL_SCRIPT_TABLE). Script_n sets 0x8000 = item,
0x8001 = count, 0x8002 = flag 2819 + n and calls global 2811 (file 1238 Script_12), which gives the item ("found"),
sets the flag and plays the jingle; the game no longer offers a sign whose hidden-item flag is set. Flags 2820-3032
belong to hidden items only (no new-game script sets them; data/story_ids.json).
Each Sapphire hidden item (data/maps/*/map.json bg_events type hidden_item: x, y, item, flag FLAG_HIDDEN_ITEM_*) gets a
slot n (1-213, fixed once given: data/hoenn_hidden_items.json) and Black 2's item (converter/gen_items.py's names and
TM table; key items: converter/gen_key_items.py). Its sign goes on the Sapphire tile ("map" + "at", as every story object); maps not built yet are skipped by
the story patch ("optional") and placed once they are. Slots no Hoenn item uses keep Black 2's script.
The story patch also rewrites Black 2's hidden-item table (ov012 HIDDEN_ITEMS: zone and tile per slot, for the
Itemfinder, and "respawns daily" off: Sapphire's hidden items are found once): b2tools/patches/story.py.

Daily berry spots (user decision 2026-10-06, notes/DECISIONS.md: each Sapphire berry tree spot gives its berry once a
day; no planting or watering) go in the same file: berry spot k = Script_(213 + k), global id 8212 + k (still in the
8000-8799 range of file 1241), a plain sign (cond 0) on the tree's tile (data/story/berry_spots.json). Its berry is the
one Sapphire's new game plants there (data/scripts/new_game.inc setberrytree), its count Sapphire's yield of an
unwatered tree (gBerries minYield); trees Sapphire leaves empty (soil to plant in) get no spot. Picked spots are bits of
six saved works (VAR_BERRY_PICKED_0-5, S_common's reserved works; 14 bits each: script arguments of 0x4000 and up
are read as work numbers); the first pick of a day (FLAG_DAILY_BERRY_SPOTS
clear: Black 2 clears flags 2720-2819 at midnight, EventWork_ResetDailyFlags) clears all six. Lines: Sapphire's
berry_tree.inc text (with Black 2's plural item names), appended to script text 208 (file 1241's message file,
GLOBAL_SCRIPT_TABLE {8000, 8799, 1241, 3, 208}): src/text/script/0208_*.txt.
"""
import os, re, json, glob
from gen_items import b2_items, tm_items, map_item
from gen_key_items import TABLE as KEY_ITEMS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
SLOTS = 213

BERRY_BASE = 213                       # berry spot k = Script_(BERRY_BASE + k) of file 1241, global id 7999 + that
ZONE_INIT_CALL, ZONE_INIT_MAP = 85, 86   # Script_(213 + 85/86) = global 8297 / 8298: the tree zones' new-day reset
TREE_UID = 400                         # berry spot k's tree = NPC uid 400 + k in its zone (data/story/berry_spots.json)
BERRY_TEXT = 28                        # first appended line of script text 208 (Black 2's file has lines 0-27)
# Sapphire berry_tree.inc text (pokeruby data/text/berry_tree.inc), "{STR_VAR_1} BERRIES" -> word 1 = Black 2's plural
# item name ("Oran Berries"), STR_VAR_2 -> word 2 (the count), PLAYER -> word 0
BERRY_LINES = [
    "It\u2019s soft, loamy soil.",                                                          # Route102_Text_1A16B6
    "There are {0100:2} {0100:1}!{be01}\\nDo you want to pick the\\n{0100:1}?",          # Route102_Text_1A17C0
    "{0100:0} picked the {0100:2} {0100:1}.",                                                # Route102_Text_1A17FD
    "{0100:0} put away the {0100:1}\\nin the Bag\u2019s Berries Pocket.{be01}\\nThe soil returned to its soft and\\n"
    "loamy state.",                                                                           # Route102_Text_1A181A
    "The Bag\u2019s Berries Pocket is full.{be01}\\nThe {0100:1} couldn\u2019t be taken.",  # Route102_Text_1A1881
    "{0100:0} left the {0100:1}\\nunpicked.",                                                # Route102_Text_1A18C5
]

# ---- berry planting (HOENN_BERRY_PLANTING, user goal 2026-10-18; notes/BERRY_PLANTING.md) ----------------------------
# Gen 3's real berry trees instead of the daily spots, behind the switch: every Gen 3 berry tree (soft soil included) is
# one actor, uid PLANT_UID - its index on its map, object code PLANT_VCODE + Gen 3 tree id (b2tools/patches/berries.c turns it
# into the picture of the tree's berry and stage when the actor is made), script global 7999 + PLANT_SCRIPT (file 1241
# Script_300, src/field_scripts/common/berry_planting.inc). Per version, from its own decomp: the trees' maps and tiles
# (data/maps/*/map.json berry tree objects) and the berries Gen 3's new game plants (data/scripts/new_game.inc
# setberrytree): Sapphire and Ruby pokeruby, Emerald pokeemerald (its Route 115 trees stand one tile east).
# Writes data/hoenn_berry_trees.json (Emerald: data/emerald/hoenn_berry_trees.json; read by patches/berries.py),
# data/story/berries/berry_trees.json (Emerald: data/story/berries/emerald/; patches/story.py places it instead of
# data/story/berry_spots.json when the switch is on) and src/text/berries/overrides_berry_planting.json (the lines,
# appended to script text 208 after the daily ones: patches/text.py packs them only with the switch).
PLANT_SCRIPT = 300                     # Script_300 = global 8299
PLANT_UID = 250                        # actor uid = 250 - the tree's index on its map (Black 2's actor save keeps a uid
                                       # in 8 bits: 400 + k came back as 144 + k after Continue; 233-250 are free)
PLANT_VCODE = 0x0F00                   # object code = 0x0F00 + tree id (berries.c VCODE_BASE, b2tools/npc_check.py)
PLANT_TEXT = BERRY_TEXT + len(BERRY_LINES)   # 34: berry_planting_defs.inc BT_T_WANTPLANT
MIRAGE_FLAG = 'FLAG_BERRY_TREE_PICKED_73'    # Mirage Island's Liechi tree: hidden while the island is away (Route130.inc)
# Sapphire's berry_tree.inc text (Ruby's = Sapphire's; Emerald's the same lines), Black 2's item names for
# {STR_VAR_1} [BERRY] ("Oran Berry"), line breaks for Black 2's window
PLANT_LINES = [
    "It’s soft, loamy soil.\\nWant to plant a Berry?",                       # Route102_Text_1A16CD
    "{0100:0} planted one {0100:1}\\nin the soft, loamy soil.",                  # Route102_Text_1A16FB
    "One {0100:1} was planted here.",                                            # Route102_Text_1A172C
    "{0100:1} has sprouted.",                                                     # Route102_Text_1A174B
    "This {0100:1} plant\\nis growing taller.",                                  # Route102_Text_1A175C
    "These {0100:1} flowers\\nare blooming cutely.",                             # Route102_Text_1A177D + 1A17B0
    "These {0100:1} flowers\\nare blooming prettily.",                           # + 1A17B7
    "These {0100:1} flowers\\nare blooming very beautifully.",                   # + 1A179F
    "Want to water the {0100:1}\\nwith the Wailmer Pail?",                       # Route102_Text_1A18E6
    "{0100:0} watered the {0100:1}.",                                            # Route102_Text_1A1912
    "The plant seems to be delighted.",                                          # Route102_Text_1A1925
    "The {0100:1} can’t be planted\\nhere.",                                # (Black 2's Bag lists every item)
]
BERRY_NAMES = ['CHERI', 'CHESTO', 'PECHA', 'RAWST', 'ASPEAR', 'LEPPA', 'ORAN', 'PERSIM', 'LUM', 'SITRUS', 'FIGY', 'WIKI',
               'MAGO', 'AGUAV', 'IAPAPA', 'RAZZ', 'BLUK', 'NANAB', 'WEPEAR', 'PINAP', 'POMEG', 'KELPSY', 'QUALOT',
               'HONDEW', 'GREPA', 'TAMATO', 'CORNN', 'MAGOST', 'RABUTA', 'NOMEL', 'SPELON', 'PAMTRE', 'WATMEL', 'DURIN',
               'BELUE', 'LIECHI', 'GANLON', 'SALAC', 'PETAYA', 'APICOT', 'LANSAT', 'STARF', 'ENIGMA']   # Gen 3 berry 1-43

def planting_trees(decomp, hoenn=lambda m: m):
    """{tree id: (map, [x, y], Gen 3 berry name or None)}: a decomp's berry tree objects and its new game's berries."""
    root = os.path.join(ROOT, 'external', decomp)
    consts = {}
    bh = os.path.join(root, 'include', 'constants', 'berry.h')
    if os.path.exists(bh):
        consts = {k: int(v) for k, v in re.findall(r'#define (BERRY_TREE_\w+)\s+(\d+)', open(bh).read())}
    tid = lambda v: v if isinstance(v, int) else consts[v] if v in consts else int(v, 0)
    planted = {tid(t): b for t, b in re.findall(r'setberrytree (\w+),\s*ITEM_TO_BERRY\(ITEM_(\w+)_BERRY\)',
                                                 open(os.path.join(root, 'data', 'scripts', 'new_game.inc')).read())}
    out = {}
    for f in sorted(glob.glob(os.path.join(root, 'data', 'maps', '*', 'map.json'))):
        m = json.load(open(f))
        for o in m.get('object_events') or []:
            if 'BERRY_TREE' in o['graphics_id']:
                t = tid(o['trainer_sight_or_berry_tree_id'])
                assert t not in out and 0 < t < 128, (decomp, t)
                out[t] = (hoenn(m['name']), [o['x'], o['y']], planted.get(t))
    assert set(planted) <= set(out), set(planted) - set(out)
    return dict(sorted(out.items()))

def text_of(files, name):
    return next(t for p, t in files.items() if p.endswith(name))

def planting_files(trees, version_name, items):
    """{path: text} of the registry, the story objects and the text lines."""
    sub = '' if version_name == 'sapphire' else version_name + '/'
    reg = {str(t): dict(map=mp, at=at, berry=f'ITEM_{b}_BERRY' if b else None,
                        number=BERRY_NAMES.index(b) + 1 if b else 0,
                        item=items[f'ITEM_{b}_BERRY'] if b else 0) for t, (mp, at, b) in trees.items()}
    index = {}
    for t, (mp, at, b) in trees.items(): index[t] = sum(1 for u, v in trees.items() if v[0] == mp and u < t)
    assert max(index.values()) < 18
    objs = [dict(kind='npc', map=mp, at=at, uid=PLANT_UID - index[t], model=PLANT_VCODE + t, dir=1,
                 script=7999 + PLANT_SCRIPT, optional=True,
                 note=f'berry tree {t}' + (f' ({b.title()} at new game)' if b else ' (soft soil)'),
                 **({'flag': MIRAGE_FLAG} if mp == 'Route130' else {}))
            for t, (mp, at, b) in trees.items()]
    assert sum(1 for o in objs if 'flag' in o) == 1, 'one tree on Mirage Island'
    b2 = os.path.basename(glob.glob(os.path.join(ROOT, 'src', 'text', 'script', '0208_*.txt'))[0])
    text = {'_doc': 'Generated by converter/gen_hidden_items.py: berry planting\'s lines (Sapphire\'s berry_tree.inc), '
                    'appended to script text 208 after the daily berry lines; b2tools/patches/text.py adds them only '
                    'with HOENN_BERRY_PLANTING=1 (src/field_scripts/common/berry_planting_defs.inc BT_T_*).',
            f'script/{b2}': {str(PLANT_TEXT + i): (l.encode().decode('unicode_escape') if '\\u' in l else l)
                             for i, l in enumerate(PLANT_LINES)}}
    return {
        os.path.join(ROOT, 'data', sub, 'hoenn_berry_trees.json'): json.dumps(
            {'_doc': f'Generated by converter/gen_hidden_items.py: {version_name.title()}\'s Gen 3 berry trees for berry '
                     'planting (HOENN_BERRY_PLANTING): Gen 3 tree id -> map, tile, the berry its new game plants '
                     '(fully grown; null = soft soil), Gen 3 berry number, Black 2 item. b2tools/patches/berries.py '
                     'reads it (the new-game trees of the save).', 'trees': reg}, indent=1) + '\n',
        os.path.join(ROOT, 'data', 'story', 'berries', sub, 'berry_trees.json'): json.dumps(
            {'_doc': 'Generated by converter/gen_hidden_items.py: berry planting\'s tree actors (uid 250 - index on the map, '
                     'object code 0x0F00 + tree id = the tree\'s picture, b2tools/patches/berries.c; script global 8299). '
                     'b2tools/patches/story.py places them instead of data/story/berry_spots.json when '
                     'HOENN_BERRY_PLANTING=1.', 'objects': objs}, indent=1) + '\n',
        os.path.join(ROOT, 'src', 'text', 'berries', 'overrides_berry_planting.json'):
            json.dumps(text, indent=1, ensure_ascii=False) + '\n',
    }

def berry_spots(items):
    """[(spot k, map, (x, y), tree id, B2 item, count)]: every Sapphire berry tree with a berry at new game."""
    planted = {int(t): b for t, b in re.findall(r'setberrytree (\d+), ITEM_TO_BERRY\((ITEM_\w+)\)',
                                               open(f'{RUBY}/data/scripts/new_game.inc').read())}
    src = open(f'{RUBY}/src/berry.c').read()
    min_yield = {n: int(lo) for n, hi, lo in re.findall(r'\.name = NAME_(\w+)_BERRY,.*?\.maxYield = (\d+),\s*\.minYield = (\d+)',
                                                        src, re.S)}
    trees = []
    for f in sorted(glob.glob(f'{RUBY}/data/maps/*/map.json')):
        m = json.load(open(f))
        for o in m.get('object_events') or []:
            if 'BERRY_TREE' in o['graphics_id']:
                trees.append((int(o['trainer_sight_or_berry_tree_id'], 0) if isinstance(o['trainer_sight_or_berry_tree_id'], str)
                              else o['trainer_sight_or_berry_tree_id'], m['name'], (o['x'], o['y'])))
    reg_path = os.path.join(ROOT, 'data', 'hoenn_berry_spots.json')
    old = json.load(open(reg_path))['spots'] if os.path.exists(reg_path) else {}
    used = {v['k'] for v in old.values()}
    out, nxt = {}, 1
    for tid, mp, at in sorted(trees):
        if tid not in planted: continue                     # soil Sapphire leaves empty: nothing grows without planting
        item = planted[tid]
        key = f'tree_{tid}'
        if key in old: k = old[key]['k']
        else:
            while nxt in used: nxt += 1
            k = nxt; used.add(k)
        assert k <= 84, 'six works hold 84 spots (14 bits each: a value of 0x4000 or more reads as a work number)'
        out[key] = dict(k=k, map=mp, at=list(at), tree=tid, item=item, count=min_yield[item[5:-6]],
                        script=7999 + BERRY_BASE + k, work=f'VAR_BERRY_PICKED_{(k - 1) // 14}', mask=1 << ((k - 1) % 14))
    json.dump({'_doc': 'Generated by converter/gen_hidden_items.py: daily berry spots (Sapphire berry tree id -> spot k, '
                       'FIXED once given: the picked bits are saved).', 'spots': dict(sorted(out.items(), key=lambda kv: kv[1]['k']))},
              open(reg_path, 'w'), indent=1)
    objs = [dict(kind='sign', map=v['map'], at=v['at'], script=v['script'], cond=0, dir=4, optional=True,
                 note=f'{key} {v["item"]} x{v["count"]}') for key, v in sorted(out.items(), key=lambda kv: kv[1]['k'])]
    # the trees (user decision 2026-10-08): Sapphire's grown tree of the spot's berry (b2tools/models_objects.py
    # berry_trees -> data/berry_tree_sprites.json: object code + facing), hidden by FLAG_BERRY_TREE_PICKED_<k> while picked
    # today; talking to it runs the spot's script (the sign under it still answers once the tree is gone)
    sprites = json.load(open(os.path.join(ROOT, 'data', 'berry_tree_sprites.json')))['trees']
    objs += [dict(kind='npc', map=v['map'], at=v['at'], uid=TREE_UID + v['k'], model=sprites[v['item']][0],
                  dir=sprites[v['item']][1], script=v['script'], flag=f'FLAG_BERRY_TREE_PICKED_{v["k"]:02d}', optional=True,
                  note=f'{key} tree ({v["item"]})') for key, v in sorted(out.items(), key=lambda kv: kv[1]['k'])]
    json.dump({'_doc': 'Generated by converter/gen_hidden_items.py: Sapphire\'s berry tree spots as daily berry spots '
                       '(plain signs, global script 7999+213+k); placed by b2tools/patches/story.py.', 'objects': objs},
              open(os.path.join(ROOT, 'data', 'story', 'berry_spots.json'), 'w'), indent=1)
    # the lines, appended to Black 2's script text 208
    b2 = glob.glob(f'{B2}/data/text/script/0208_*.txt')[0]
    lines = open(b2, encoding='utf-8').read().rstrip('\n').split('\n')
    assert len(lines) == BERRY_TEXT, len(lines)
    open(os.path.join(ROOT, 'src', 'text', 'script', os.path.basename(b2)), 'w', encoding='utf-8').write(
        '\n'.join(lines + [l.encode().decode('unicode_escape') if '\\u' in l else l for l in BERRY_LINES]) + '\n')
    return sorted(out.values(), key=lambda v: v['k'])

def berry_scripts(spots, items):
    t = BERRY_TEXT
    entries = ''.join(f'    ScriptEntry Script_{BERRY_BASE + v["k"]}\n' for v in spots)
    assert [v['k'] for v in spots] == list(range(1, len(spots) + 1)) and len(spots) < ZONE_INIT_CALL
    entries += ''.join(f'    ScriptEntry {"Script_" + str(BERRY_BASE + k) if k >= ZONE_INIT_CALL else "L_BerryNoSpot"}\n'
                       for k in range(len(spots) + 1, ZONE_INIT_MAP + 1))       # (spots 81-84: none yet)
    entries += (f'#ifdef HOENN_BERRY_PLANTING                    // berry planting (notes/BERRY_PLANTING.md): global {7999 + PLANT_SCRIPT}\n'
                f'    ScriptEntry Script_{PLANT_SCRIPT}                         // = every tree (data/story/berries/berry_trees.json)\n'
                '#endif\n')
    body = ['', '// ---- daily berry spots (converter/gen_hidden_items.py; data/hoenn_berry_spots.json) ----', '']
    for v in spots:
        flag = f'FLAG_BERRY_TREE_PICKED_{v["k"]:02d}'
        body += [f'Script_{BERRY_BASE + v["k"]}:                    // {v["map"]} {tuple(v["at"])}: Sapphire tree {v["tree"]}',
                 '    ActorsPauseAll',
                 f'    WorkSetConst 0x8000, {items[v["item"]]}       // {v["item"]}',
                 f'    WorkSetConst 0x8001, {v["count"]}',
                 '    WorkSetConst 0x8012, 0                         // 1 = the tree stands here (its flag clear)',
                 f'    VMStackPushFlag {flag}',
                 '    VMStackPushConst 0',
                 '    VMStackCmp CMP_EQ',
                 f'    VMJumpIf CMP_STACK, L_BerryNoTree{v["k"]}     // (jumps when the comparison is false: flag set)',
                 '    WorkSetConst 0x8012, 1',
                 f'L_BerryNoTree{v["k"]}:',
                 '    VMCall L_BerryNewDay',
                 f'    WorkSet 0x8002, {v["work"]}',
                 f'    WorkAnd 0x8002, {v["mask"]}',
                 '    WorkCmpConst 0x8002, 0',
                 '    VMJumpIf CMP_NE, L_BerryLoamy',
                 '    VMCall L_BerryPick',
                 '    WorkCmpConst 0x8010, 1',
                 '    VMJumpIf CMP_NE, L_BerryEnd',
                 f'    WorkOr {v["work"]}, {v["mask"]}',
                 f'    FlagSet {flag}                    // the tree is gone until the next day',
                 '    WorkCmpConst 0x8012, 1',
                 '    VMJumpIf CMP_NE, L_BerryEnd',
                 f'    ActorDelete {TREE_UID + v["k"]}',
                 '    VMJump L_BerryEnd', '']
    body += ['L_BerryNewDay:                                  // the first pick of a day clears yesterday\'s picks',
             '    VMStackPushFlag FLAG_DAILY_BERRY_SPOTS',
             '    VMStackPushConst 0',
             '    VMStackCmp CMP_EQ',
             '    VMJumpIf CMP_STACK, L_BerryNewDayDone          // (jumps when the comparison is false: flag set)',
             '    FlagSet FLAG_DAILY_BERRY_SPOTS'] + \
            [f'    WorkSetConst VAR_BERRY_PICKED_{i}, 0' for i in range(6)] + \
            [f'    FlagReset FLAG_BERRY_TREE_PICKED_{v["k"]:02d}' for v in spots] + \
            ['L_BerryNewDayDone:', '    VMReturn', '',
             f'Script_{BERRY_BASE + ZONE_INIT_CALL}:              // global {7999 + BERRY_BASE + ZONE_INIT_CALL}: RTCallGlobal from a tree zone\'s own init',
             '#ifdef HOENN_BERRY_PLANTING',
             '    BerryCmd BT_OP_UPDATE, 0                       // (berry planting: the trees grow by the clock)',
             '#else',
             '    VMCall L_BerryNewDay                           // (a new day: every tree grows back before the zone spawns)',
             '#endif',
             '    RTEndGlobal',
             '    VMHalt',
             f'Script_{BERRY_BASE + ZONE_INIT_MAP}:              // global {7999 + BERRY_BASE + ZONE_INIT_MAP}: the init (MapScript 2) of a tree zone without one',
             '#ifdef HOENN_BERRY_PLANTING',
             '    BerryCmd BT_OP_UPDATE, 0',
             '#else',
             '    VMCall L_BerryNewDay',
             '#endif',
             '    VMHalt',
             'L_BerryNoSpot:',
             '    VMHalt', '',
             'L_BerryLoamy:',
             f'    SystemMsg {t}, 2                            // "It\'s soft, loamy soil."',
             '    LastKeyWait',
             'L_BerryEnd:',
             '    InfoMsgClose',
             '    FinishAllEvents',
             '    ActorsUnpauseAll',
             '    VMHalt', '',
             'L_BerryPick:                                    // 0x8000 item, 0x8001 count -> 0x8010 = 1 picked',
             '    WordSetPlayerName 0',
             '    WordSetItemNameEx 1, 0x8000, 2, 0             // plural ("Oran Berries")',
             '    WordSetNumber 2, 0x8001, 1',
             f'    SystemMsg {t + 1}, 2',
             '    YesNoWin 0x8010',
             '    WorkCmpConst 0x8010, 0                         // 0 = YES',
             '    VMJumpIf CMP_EQ, L_BerryYes',
             f'    SystemMsg {t + 5}, 2                            // left unpicked',
             '    LastKeyWait',
             '    WorkSetConst 0x8010, 0',
             '    VMReturn',
             'L_BerryYes:',
             '    ItemCheckSpace 0x8000, 0x8001, 0x8011',
             '    WorkCmpConst 0x8011, 0',
             '    VMJumpIf CMP_NE, L_BerryRoom',
             f'    SystemMsg {t + 4}, 2                            // pocket full',
             '    LastKeyWait',
             '    WorkSetConst 0x8010, 0',
             '    VMReturn',
             'L_BerryRoom:',
             '    ItemAdd 0x8000, 0x8001, 0x8011',
             '    MEPlay SEQ_ME_KINOMI                           // MUS_OBTAIN_BERRY',
             f'    SystemMsg {t + 2}, 2',
             '    MEWait',
             '    LastKeyWait',
             f'    SystemMsg {t + 3}, 2',
             '    LastKeyWait',
             '    WorkSetConst 0x8010, 1',
             '    VMReturn',
             '#ifdef HOENN_BERRY_PLANTING                      // berry planting: Script_300 (src/field_scripts/common/)',
             '#include "common/berry_planting.inc"',
             '#endif',
             '    .balign 4, 0']
    return entries, '\n'.join(body) + '\n'

def main():
    items, tms = b2_items(), tm_items()
    found = []
    for f in sorted(glob.glob(f'{RUBY}/data/maps/*/map.json')):
        m = json.load(open(f))
        for b in m.get('bg_events') or []:
            if b.get('type') == 'hidden_item':
                found.append(dict(map=m['name'], x=b['x'], y=b['y'], item=b['item'], flag=b['flag']))
    reg_path = os.path.join(ROOT, 'data', 'hoenn_hidden_items.json')
    old = json.load(open(reg_path))['items'] if os.path.exists(reg_path) else {}
    used = {v['n'] for v in old.values()}
    notes, mail_i, out, nxt = [], [0, {}], {}, 1
    for h in found:
        b2 = KEY_ITEMS[h['item']][0] if h['item'] in KEY_ITEMS else map_item(h['item'], items, tms, notes, mail_i)
        if not b2: continue
        if h['flag'] in old: n = old[h['flag']]['n']
        else:
            while nxt in used: nxt += 1
            n = nxt; used.add(n)
        assert n <= SLOTS, f'more hidden items than Black 2 slots ({SLOTS})'
        out[h['flag']] = dict(n=n, map=h['map'], at=[h['x'], h['y']], sapphire=h['item'], item=b2,
                              script=7999 + n, flag=2819 + n)
    json.dump({'_doc': __doc__.strip().split('\n\n')[0], 'items': dict(sorted(out.items(), key=lambda kv: kv[1]['n'])),
               'notes': notes}, open(reg_path, 'w'), indent=1)
    # script file 1241 = Black 2's own, with our slots' item (count 1, as Sapphire's hidden items)
    s = open(f'{B2}/data/field_scripts/1241.s').read()
    by_n = {v['n']: v for v in out.values()}
    def fix(m):
        n = int(m.group(1)); body = m.group(2)
        if n not in by_n: return m.group(0)
        v = by_n[n]
        body = re.sub(r'WorkSet 0x8000, \w+', f'WorkSet 0x8000, {items[v["item"]]}', body, count=1)
        body = re.sub(r'WorkSet 0x8001, \w+', 'WorkSet 0x8001, 1', body, count=1)
        assert f'WorkSet 0x8002, {v["flag"]}' in body, (n, body)
        return f'Script_{n}:{body}'
    s = re.sub(r'^Script_(\d+):((?:\n(?!Script_|L_).*)*)', fix, s, flags=re.M)
    head = ('// Black 2\'s hidden-item scripts (file 1241, global 8000-8212) with Sapphire\'s hidden items in the slots of\n'
            '// data/hoenn_hidden_items.json. Generated by converter/gen_hidden_items.py from external/pokebw2/data/'
            'field_scripts/1241.s.\n')
    open(os.path.join(ROOT, 'src', 'field_scripts', '1241_hidden_items.s'), 'w').write(head + s)
    objs = [dict(kind='sign', map=v['map'], at=v['at'], script=v['script'], cond=2, dir=4, optional=True,
                 hidden_slot=v['n'], note=f'{k} {v["sapphire"]}') for k, v in sorted(out.items(), key=lambda kv: kv[1]['n'])]
    os.makedirs(os.path.join(ROOT, 'data', 'story'), exist_ok=True)
    json.dump({'_doc': 'Generated by converter/gen_hidden_items.py: Sapphire\'s hidden items (Black 2 hidden-item signs, '
                       'global script 7999+n); placed by b2tools/patches/story.py, maps not built yet are skipped.',
               'objects': objs}, open(os.path.join(ROOT, 'data', 'story', 'hidden_items.json'), 'w'), indent=1)
    berries = berry_spots(items)
    entries, body = berry_scripts(berries, items)
    s = s.replace('    ScriptEntry Script_213\n', '    ScriptEntry Script_213\n' + entries, 1)
    s = s.replace('#include "asm/field_script.inc"\n', '#include "asm/field_script.inc"\n#include "hoenn.h"\n'
                  '#ifdef HOENN_BERRY_PLANTING\n#include "common/berry_planting_defs.inc"\n#endif\n', 1)
    s = s.rstrip('\n') + '\n' + body
    open(os.path.join(ROOT, 'src', 'field_scripts', '1241_hidden_items.s'), 'w').write(head + s)
    print(f'{len(berries)} berry spots (global {8213}-{8212 + len(berries)})')
    plant = planting_files(planting_trees('pokeruby'), 'sapphire', items)
    for path, text in plant.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path) or open(path, encoding='utf-8').read() != text: open(path, 'w', encoding='utf-8').write(text)
    print(f'berry planting: {len(json.loads(text_of(plant, "hoenn_berry_trees.json"))["trees"])} trees (data/hoenn_berry_trees.json)')
    print(f'{len(out)} hidden items in {len({v["map"] for v in out.values()})} maps, slots 1-{max(used)}; notes:', *notes,
          sep='\n  ')

# ---- Emerald (HOENN_VERSION=emerald python3 gen_hidden_items.py [--check]; emerald_data 2026-10-12, EMERALD-1) ----
# pokeemerald's hidden items (data/maps/*/map.json bg_events, the same format and flag names as pokeruby's): one with a
# Sapphire hidden item's flag (or on its tile) takes that item's slot n (flag 2819 + n, global script 7999 + n); the
# others get free slots (1-213). Writes data/emerald/hoenn_hidden_items.json (registry by flag, deep-merged over
# Sapphire's), src/field_scripts/emerald/1241_hidden_items.s (Sapphire's file 1241 with Emerald's items in the slots;
# its berry spots stay Sapphire's) and data/story/emerald/hidden_items.json (Emerald's signs, replacing Sapphire's file:
# "map" = the HoennB2 map Emerald's map plays; maps not built are skipped by the story patch, "optional").
def main_emerald():
    import sys
    from gen_items import emerald_maps, emerald_tm_names, _write_or_check, EMERALD
    check = '--check' in sys.argv[1:]
    items, tms = b2_items(), tm_items()
    tmn = emerald_tm_names()
    hoenn, built, only = emerald_maps()
    sap = json.load(open(os.path.join(ROOT, 'data', 'hoenn_hidden_items.json')))['items']
    sap_at = {(v['map'], tuple(v['at'])): k for k, v in sap.items()}
    reg_path = os.path.join(ROOT, 'data', 'emerald', 'hoenn_hidden_items.json')
    old = json.load(open(reg_path))['items'] if os.path.exists(reg_path) else {}
    used = {v['n'] for v in sap.values()} | {v['n'] for v in old.values()}
    found = []
    for f in sorted(glob.glob(f'{EMERALD}/data/maps/*/map.json')):
        m = json.load(open(f))
        for b in m.get('bg_events') or []:
            if b.get('type') == 'hidden_item':
                found.append(dict(map=os.path.basename(os.path.dirname(f)), x=b['x'], y=b['y'], item=b['item'], flag=b['flag']))
    notes, mail_i, out, nxt = [], [0, {}], {}, 1
    for h in found:
        name = tmn.get(h['item'], h['item'])
        b2 = KEY_ITEMS[name][0] if name in KEY_ITEMS else map_item(name, items, tms, notes, mail_i)
        if not b2: continue
        hm = hoenn(h['map'])
        twin = h['flag'] if h['flag'] in sap else sap_at.get((hm, (h['x'], h['y'])))
        if twin: n = sap[twin]['n']
        elif h['flag'] in old: n = old[h['flag']]['n']
        else:
            while nxt in used: nxt += 1
            n = nxt; used.add(n)
        assert n <= SLOTS, f'more hidden items than Black 2 slots ({SLOTS})'
        out[h['flag']] = dict(n=n, map=hm, emerald_map=h['map'], at=[h['x'], h['y']], emerald=h['item'], item=b2,
                              script=7999 + n, flag=2819 + n, sapphire_twin=twin,
                              moved=bool(twin and (sap[twin]['map'], sap[twin]['at']) != (hm, [h['x'], h['y']])),
                              built=hm in built, emerald_only_map=h['map'] in only)
    dup = [n for n in {v['n'] for v in out.values()} if sum(1 for v in out.values() if v['n'] == n) > 1]
    assert not dup, dup
    gone = sorted(k for k in sap if k not in {v['sapphire_twin'] for v in out.values()})
    want = {reg_path: json.dumps({
        '_doc': 'Emerald overlay of data/hoenn_hidden_items.json (version.load_json deep merge), written by '
                'converter/gen_hidden_items.py with HOENN_VERSION=emerald: pokeemerald\'s hidden items by flag; one with a '
                'Sapphire item\'s flag or tile (sapphire_twin; moved = on another tile) keeps its slot n, the others have '
                'free slots. map = the HoennB2 map, built = this build has it. sapphire_only: Sapphire\'s that Emerald '
                'does not have (not placed in Emerald: data/story/emerald/hidden_items.json replaces the signs).',
        'items': dict(sorted(out.items(), key=lambda kv: kv[1]['n'])), 'sapphire_only': gone, 'notes': sorted(set(notes))},
        indent=1) + '\n'}
    s = open(os.path.join(ROOT, 'src', 'field_scripts', '1241_hidden_items.s')).read()
    by_n = {v['n']: v for v in out.values()}
    def fix(m):
        n = int(m.group(1)); body = m.group(2)
        if n not in by_n or n > SLOTS: return m.group(0)
        v = by_n[n]
        body = re.sub(r'WorkSet 0x8000, \w+', f'WorkSet 0x8000, {items[v["item"]]}', body, count=1)
        body = re.sub(r'WorkSet 0x8001, \w+', 'WorkSet 0x8001, 1', body, count=1)
        assert f'WorkSet 0x8002, {v["flag"]}' in body, (n, body)
        return f'Script_{n}:{body}'
    s = re.sub(r'^Script_(\d+):((?:\n(?!Script_|L_).*)*)', fix, s, flags=re.M)
    s = ('// Emerald (HOENN_VERSION=emerald, converter/gen_hidden_items.py): Sapphire\'s file with the hidden items of '
         'data/emerald/hoenn_hidden_items.json in their slots.\n' + s)
    want[os.path.join(ROOT, 'src', 'field_scripts', 'emerald', '1241_hidden_items.s')] = s
    objs = [dict(kind='sign', map=v['map'], at=v['at'], script=v['script'], cond=2, dir=4, optional=True,
                 hidden_slot=v['n'], note=f'{k} {v["emerald"]}') for k, v in sorted(out.items(), key=lambda kv: kv[1]['n'])]
    want[os.path.join(ROOT, 'data', 'story', 'emerald', 'hidden_items.json')] = json.dumps(
        {'_doc': 'Generated by converter/gen_hidden_items.py (HOENN_VERSION=emerald): Emerald\'s hidden items (Black 2 '
                 'hidden-item signs, global script 7999+n), replacing data/story/hidden_items.json in an Emerald build; '
                 'placed by b2tools/patches/story.py, maps not built yet are skipped.', 'objects': objs}, indent=1) + '\n'
    unbuilt = sorted(f'{v["emerald_map"]} ({v["at"][0]},{v["at"][1]}) {v["emerald"]}' for v in out.values() if not v['built'])
    print(f'Emerald hidden items: {len(out)} ({sum(1 for v in out.values() if v["sapphire_twin"] and not v["moved"])} as in '
          f'Sapphire, {sum(1 for v in out.values() if v["moved"])} moved, '
          f'{sum(1 for v in out.values() if not v["sapphire_twin"])} new); Sapphire\'s Emerald does not have: {len(gone)} '
          f'{gone}; slots used up to {max(used)} of {SLOTS}')
    print(f'  on maps this build does not have ({len(unbuilt)}): ' + '; '.join(unbuilt))
    if notes: print('  notes: ' + '; '.join(sorted(set(notes))))
    trees = planting_trees('pokeemerald', lambda m: hoenn(m) or m)
    plant = planting_files(trees, 'emerald', items)
    plant.pop(os.path.join(ROOT, 'src', 'text', 'berries', 'overrides_berry_planting.json'))   # (shared: Sapphire's run writes it)
    want.update(plant)
    print(f'berry planting: {len(trees)} Emerald trees (data/emerald/hoenn_berry_trees.json)')
    _write_or_check(want, check)

if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import version
    main_emerald() if version.is_emerald() else main()
