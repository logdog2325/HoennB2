"""Emerald's Battle Pike data -> data/emerald/frontier_pike.json (frontier_pike, 2026-10-12; notes/FRONTIER_PIKE.md).
b2tools/patches/frontier_pike.py packs it for the Pike's code (b2tools/patches/frontier_pike.c) in an Emerald build.

    python3 gen_frontier_pike.py            (reads external/pokeemerald only; writes the json and the Pike's room texts)

Sources (pokeemerald): src/data/battle_frontier/battle_frontier_trainers.h (300 Frontier trainers: facility class,
name, the six easy-chat words said before a battle, the list of sets they draw from), battle_frontier_trainer_mons.h
(those lists, written with FRONTIER_MONS_* macros), battle_frontier_mons.h (882 sets: species, four moves, held item
of gBattleFrontierHeldItems, EV spread flags, nature), src/battle_tower.c (gBattleFrontierHeldItems, the facility
classes' overworld sprites gTowerMale/FemaleFacilityClasses + GfxIds), src/frontier_util.c (sFrontierBrainsMons: Lucy's
silver and gold parties), src/battle_pike.c (the wild Pokémon of the Pike's wild room, the 25 people of the empty room
and their 42 easy-chat lines), src/data/pokemon/trainer_class_lookups.h (facility class -> trainer picture), the easy
chat word lists (include/constants/easy_chat.h, src/data/easy_chat/easy_chat_group_*.h) and the Pike's maps' texts.

Black 2 names: species / moves / items by their constant names (Gen 3 numbers = Black 2's), trainer classes by
Emerald's picture through data/hoenn_trainer_classes.json + data/emerald/ (the classes Hoenn's own trainers use, as
converter/gen_battle_tower.py does for Sapphire's tower), overworld sprites through data/sprite_map.json (pokeemerald's
renamed people matched to pokeruby's by their picture, IMG_ALIAS). Text in Gen 5 capitalisation (gen3text.convert);
easy-chat lines word by word in Black 2's easy-chat style (gen_battle_tower.py's rules), three words a row and two rows as
Emerald's FrontierSpeechToString (two words a row, three rows, when a row would be too wide)."""
import os, re, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
os.environ['HOENN_VERSION'] = 'emerald'
import version  # noqa: E402
from gen3text import convert  # noqa: E402
import gen_battle_tower as gbt  # noqa: E402

EM = os.path.join(ROOT, 'external', 'pokeemerald')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
OUT = os.path.join(ROOT, 'data', 'emerald', 'frontier_pike.json')
MOVE_ALIAS = {'MOVE_SELF_DESTRUCT': 'MOVE_SELFDESTRUCT', 'MOVE_SMOKESCREEN': 'MOVE_SMOKE_SCREEN', 'MOVE_SOFT_BOILED': 'MOVE_SOFTBOILED'}
ITEM_ALIAS = {}
SPECIES_ALIAS = {}
EV_ORDER = ['HP', 'ATTACK', 'DEFENSE', 'SPEED', 'SP_ATTACK', 'SP_DEFENSE']    # F_EV_SPREAD_* bits 0-5 (= Black 2's set order)
NATURES = ['HARDY', 'LONELY', 'BRAVE', 'ADAMANT', 'NAUGHTY', 'BOLD', 'DOCILE', 'RELAXED', 'IMPISH', 'LAX', 'TIMID', 'HASTY',
           'SERIOUS', 'JOLLY', 'NAIVE', 'MODEST', 'MILD', 'QUIET', 'BASHFUL', 'RASH', 'CALM', 'GENTLE', 'SASSY', 'CAREFUL',
           'QUIRKY']                                       # pokeemerald include/constants/pokemon.h order = Black 2's
# pokeemerald people renamed since pokeruby: the same picture (pixel for pixel, checked) under pokeruby's name, or the
# nearest one where Emerald redrew it (EXPERT_M, OLD_WOMAN)
IMG_ALIAS = {'POKEFAN_F': 'WOMAN_2', 'NINJA_BOY': 'LITTLE_BOY_1', 'LITTLE_BOY': 'LITTLE_BOY_2', 'LITTLE_GIRL': 'LITTLE_GIRL_2',
             'LINK_RECEPTIONIST': 'WOMAN_6', 'POKEFAN_M': 'MAN_3', 'RS_LITTLE_BOY': 'LITTLE_BOY_3', 'GAMEBOY_KID': 'BOY_5',
             'EXPERT_M': 'OLD_MAN_1', 'OLD_WOMAN': 'OLD_WOMAN_1', 'EXPERT_F': 'OLD_WOMAN_2', 'RICH_BOY': 'BOY_4', 'TWIN': 'LITTLE_GIRL_1'}
# Black 2's field Pokémon (a/2/0/8: species, sex, form, object code; checked in the table): Emerald's status room Pokémon
POKEMON_OBJ = {'KIRLIA': 4410, 'DUSCLOPS': 4485}
HIGH_TIER = 849                                            # FRONTIER_MONS_HIGH_TIER: sets past it only above level 50

def defines(path, prefix):
    return gbt.defines(path, prefix)

def em(*p):
    return open(os.path.join(EM, *p), encoding='utf-8').read()

def sapphire_name(gfx):
    """pokeemerald OBJ_EVENT_GFX_X -> data/sprite_map.json code (pokeruby's name of the same picture)."""
    smap = version.load_json(os.path.join(ROOT, 'data', 'sprite_map.json'))
    n = gfx.replace('OBJ_EVENT_GFX_', '')
    for k in (gfx, 'OBJ_EVENT_GFX_' + IMG_ALIAS.get(n, n)):
        if k in smap: return smap[k]['code'], k
    raise SystemExit(f'no Black 2 sprite for {gfx}')

def easy_chat():
    """EC_WORD_* (and EC_MOVE/EC_POKEMON(X)) -> Emerald's English word; Pokémon / moves in Black 2's spelling."""
    hdr = em('include', 'constants', 'easy_chat.h')
    words = {}
    texts = {}
    for f in os.listdir(os.path.join(EM, 'src', 'data', 'easy_chat')):
        if not f.startswith('easy_chat_group_'): continue
        s = em('src', 'data', 'easy_chat', f)
        texts.update(dict(re.findall(r'const u8 (gEasyChatWord_\w+)\[\] = _\("(.*?)"\);', s)))
        for w, t in re.findall(r'\[EC_INDEX\((EC_WORD_\w+)\)\]\s*=\s*\{\s*\.text = (gEasyChatWord_\w+)', s):
            words[w] = t
    out = {w: texts[t] for w, t in words.items() if t in texts}
    status = set(re.findall(r'#define (EC_WORD_\w+)\s+\(\(EC_GROUP_STATUS << EC_MASK_BITS\)', hdr))
    sp_names = open(f'{B2}/data/text/system/0090_species_names.txt', encoding='utf-8').read().split('\n')
    mv_names = open(f'{B2}/data/text/system/0403_move_names.txt', encoding='utf-8').read().split('\n')
    proper = {re.sub(r'[^A-Z]', '', n.upper()): n for f in ('0374_ability_names.txt', '0398_type_names.txt')
              for n in open(f'{B2}/data/text/system/{f}', encoding='utf-8').read().split('\n') if n.strip()}
    for k, v in list(out.items()):
        key = re.sub(r'[^A-Z]', '', v)
        if v.endswith('DAY') and v not in ('DAY', 'TODAY', 'YESTERDAY', 'HOLIDAY', 'BIRTHDAY'):
            out[k] = '\x01' + v[0] + v[1:].lower()
        elif key in proper and k in status:
            out[k] = '\x01' + proper[key]
    for kind, table, names in (('POKEMON', defines(f'{B2}/include/constants/species.h', 'SPECIES_'), sp_names),
                               ('MOVE', defines(f'{B2}/include/constants/moves.h', 'MOVE_'), mv_names)):
        for n, i in table.items():
            out[f'EC_{kind}({n.split("_", 1)[1]})'] = out[f'EC_{kind}2({n.split("_", 1)[1]})'] = '\x01' + names[i]
    return out

def speech(words, ec, cols=3):
    """Emerald's FrontierSpeechToString(words): ConvertEasyChatWordsToString(dst, words, 3, 2) (rows of three, a new
    line after row 1); two words a row in three rows (a scroll after row 2) when a row is too wide (Emerald: 204 px; here
    over 30 characters)."""
    rows = [words[i:i + cols] for i in range(0, 6, cols)]
    out, first = [], True
    for row in rows:
        s = ''
        for w in row:
            if w == 'EC_EMPTY_WORD' or w not in ec: continue        # (EC_WORD_NONE is the word "none")
            t = ec[w]
            if t.startswith('\x01'):
                s += t[1:] + ' '; first = False
                continue
            if t in gbt.PUNCT:
                s = s.rstrip() + t + ' '
                if t in ('!', '!!', '?', '?!', '!?', '.'): first = True
                continue
            low = t.lower() if t not in ('I', "I'M", "I'LL", "I'VE", "I'D") else t[0] + t[1:].lower()
            low = re.sub(r"\bi(\b|')", lambda m: 'I' + m.group(1), low).replace('pokémon', 'Pokémon').replace('pokemon', 'Pokémon')
            if first: low = low[:1].upper() + low[1:]; first = False
            s += low + ' '
        out.append(s.rstrip())
    if cols == 3 and max(len(r) for r in out) > 30:
        return speech(words, ec, 2)
    text = out[0] + ('\\n' + out[1] if len(out) > 1 else '') + ('\\l' + out[2] if len(out) > 2 else '')
    line, unknown = convert(text, expand=True)
    assert not unknown, unknown
    return line

def frontier_mon_ids():
    return {n: int(v) for n, v in re.findall(r'#define (FRONTIER_MON_\w+)\s+(\d+)', em('include', 'constants', 'battle_frontier_mons.h'))}

def load_sets(b2s, b2m, b2i, unknown):
    ids = frontier_mon_ids()
    held = re.findall(r'\[(BATTLE_FRONTIER_ITEM_\w+)\]\s*=\s*(ITEM_\w+)', re.search(r'gBattleFrontierHeldItems\[\] =\s*\{(.*?)\};', em('src', 'battle_tower.c'), re.S).group(1))
    held = dict(held)
    sets = {}
    for name, body in re.findall(r'\[(FRONTIER_MON_\w+)\] = \{(.*?)\n    \}', em('src', 'data', 'battle_frontier', 'battle_frontier_mons.h'), re.S):
        sp = re.search(r'\.species = (SPECIES_\w+)', body).group(1)
        mv = re.findall(r'(MOVE_\w+)', re.search(r'\.moves = \{(.*?)\}', body).group(1))
        it = held[re.search(r'\.itemTableId = (\w+)', body).group(1)]
        ev = re.findall(r'F_EV_SPREAD_(\w+)', re.search(r'\.evSpread = ([^\n]*)', body).group(1))
        nat = re.search(r'\.nature = NATURE_(\w+)', body).group(1)
        def b2(table, n, alias, kind):
            n2 = alias.get(n, n)
            if n2 not in table: unknown[f'{kind} {n}'] += 1; return 0
            return table[n2]
        sets[ids[name]] = dict(name=name, species=sp, species_id=b2(b2s, sp, SPECIES_ALIAS, 'species'),
                               moves=mv, move_ids=[0 if m == 'MOVE_NONE' else b2(b2m, m, MOVE_ALIAS, 'move') for m in mv],
                               item=it, item_id=0 if it == 'ITEM_NONE' else b2(b2i, it, ITEM_ALIAS, 'item'),
                               ev=sum(1 << EV_ORDER.index(e) for e in ev), nature=NATURES.index(nat))
    assert sorted(sets) == list(range(len(sets))), 'frontier mon ids not contiguous'
    return [sets[i] for i in range(len(sets))], ids

def load_trainer_lists(ids):
    """gBattleFrontierTrainerMons_* (macros with ## pasting): run through the C preprocessor (clang -E), as the build does."""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as t:
        f = os.path.join(t, 'x.c')
        open(f, 'w').write('#include "constants/battle_frontier_mons.h"\ntypedef unsigned short u16;\n'
                           '#include "data/battle_frontier/battle_frontier_trainer_mons.h"\n')
        out = subprocess.run(['/opt/homebrew/opt/llvm/bin/clang', '-E', '-P', '-I', os.path.join(EM, 'include'),
                              '-I', os.path.join(EM, 'src'), f], capture_output=True, text=True, check=True).stdout
    lists = {}
    for name, body in re.findall(r'gBattleFrontierTrainerMons_(\w+)\[\] =\s*\{(.*?)\};', out, re.S):
        vals = [int(x, 0) for x in re.findall(r'-?(?:0x[0-9a-fA-F]+|\d+)', body)]
        lists[name] = [v for v in vals if v not in (-1, 0xFFFF)]
    assert lists and all(max(v) < len(ids) for v in lists.values())
    return lists

def facility_tables():
    bt = em('src', 'battle_tower.c')
    def table(name, pat):
        return re.findall(pat, re.search(rf'{name}\[\w*\] =\s*\{{(.*?)\}};', bt, re.S).group(1))
    male = table('gTowerMaleFacilityClasses', r'FACILITY_CLASS_(\w+)'); female = table('gTowerFemaleFacilityClasses', r'FACILITY_CLASS_(\w+)')
    mg = table('gTowerMaleTrainerGfxIds', r'(OBJ_EVENT_GFX_\w+)'); fg = table('gTowerFemaleTrainerGfxIds', r'(OBJ_EVENT_GFX_\w+)')
    gfx = dict(zip(male, mg)); gfx.update(zip(female, fg))
    pics = dict(re.findall(r'\[FACILITY_CLASS_(\w+)\]\s*=\s*TRAINER_PIC_(\w+)', em('src', 'data', 'pokemon', 'trainer_class_lookups.h').split('gFacilityClassToTrainerClass')[0]))
    return gfx, pics

def b2_class_of_pic():
    review = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json'))['review']
    out = {}
    for r in review:
        for p in r.get('emerald_pics', []) + [r['sapphire_pic']]:
            out.setdefault(p, (r['b2_class'], r['name']))
    return out

def pike_c():
    s = em('src', 'battle_pike.c')
    wild = {}
    for lv, arr in (('50', 'sLvl50'), ('open', 'sLvlOpen')):
        tabs = []
        for k in range(1, 5):
            body = re.search(rf'{arr}_Mons{k}\[\] =\s*\{{(.*?)\n\}};', s, re.S).group(1)
            mons = []
            for sp, delta, mv in re.findall(r'\.species = SPECIES_(\w+),\s*\.levelDelta = (\d+),\s*\.moves = \{(.*?)\}', body, re.S):
                mons.append(dict(species=sp, delta=int(delta), moves=re.findall(r'MOVE_\w+', mv)))
            assert len(mons) == 3
            tabs.append(mons)
        wild[lv] = tabs
    npcs = [dict(gfx=g, speech=[int(a), int(b), int(c)]) for g, a, b, c in re.findall(
        r'\.graphicsId = (OBJ_EVENT_GFX_\w+),\s*\.speechId1 = (\d+),\s*\.speechId2 = (\d+),\s*\.speechId3 = (\d+)', s)]
    assert len(npcs) == 25, len(npcs)
    body = re.search(r'sNPCSpeeches\[\]\[EASY_CHAT_BATTLE_WORDS_COUNT\] =\s*\{(.*?)\n\};', s, re.S).group(1)
    speeches = [re.findall(r'EC_WORD_\w+|EC_EMPTY_WORD|EC_MOVE2?\(\w+\)|EC_POKEMON2?\(\w+\)', row) for row in re.findall(r'\{(.*?)\}', body)]
    assert len(speeches) == 42 and all(len(x) == 6 for x in speeches), len(speeches)
    return wild, npcs, speeches

def lucy():
    s = em('src', 'frontier_util.c')
    body = re.search(r'\[FRONTIER_FACILITY_PIKE\] =\s*\{(.*?)\n    \[FRONTIER_FACILITY_PYRAMID\]', s, re.S).group(1)
    parties = []
    for sym in re.split(r'// (?:Silver|Gold) Symbol\.', body)[1:]:
        mons = []
        for sp, item, iv, nat, evs, mv in re.findall(r'\.species = SPECIES_(\w+),\s*\.heldItem = (ITEM_\w+),\s*\.fixedIV = (\w+),\s*'
                                                     r'\.nature = NATURE_(\w+),\s*\.evs = \{(.*?)\},\s*\.moves = \{(.*?)\}', sym, re.S):
            mons.append(dict(species=sp, item=item, iv=31 if iv == 'MAX_PER_STAT_IVS' else int(iv), nature=NATURES.index(nat),
                             evs=[int(x) for x in evs.split(',')], moves=re.findall(r'MOVE_\w+', mv)))
        assert len(mons) == 3, sym[:200]
        parties.append(mons)
    assert len(parties) == 2
    return parties

def main():
    b2s = defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2m = defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    b2i = defines(f'{B2}/include/constants/items.h', 'ITEM_')
    unknown = collections.Counter()
    sets, ids = load_sets(b2s, b2m, b2i, unknown)
    lists = load_trainer_lists(ids)
    ec = easy_chat()
    gfx_of, pic_of = facility_tables()
    cls_of = b2_class_of_pic()
    trainers = []
    src = em('src', 'data', 'battle_frontier', 'battle_frontier_trainers.h')
    for key, cls, name, before, lose, monset in re.findall(r'\[(FRONTIER_TRAINER_\w+)\] = \{\s*\.facilityClass = FACILITY_CLASS_(\w+),\s*'
                                                     r'\.trainerName = _\("(.*?)"\),\s*\.speechBefore = \{(.*?)\},.*?'
                                                     r'\.speechLose = \{(.*?)\},\s*'
                                                     r'\.monSet = gBattleFrontierTrainerMons_(\w+)', src, re.S):
        pic = pic_of[cls]
        if pic not in cls_of: raise SystemExit(f'{key}: Emerald picture {pic} has no Black 2 class')
        code, sname = sapphire_name(gfx_of.get(cls, 'OBJ_EVENT_GFX_BOY_1'))
        nm, unk = convert(name, expand=True)
        assert not unk
        words = re.findall(r'EC_WORD_\w+|EC_EMPTY_WORD|EC_MOVE2?\(\w+\)|EC_POKEMON2?\(\w+\)', before)
        lwords = re.findall(r'EC_WORD_\w+|EC_EMPTY_WORD|EC_MOVE2?\(\w+\)|EC_POKEMON2?\(\w+\)', lose)
        trainers.append(dict(key=key, name=nm, facility_class=cls, pic=pic, b2_class=cls_of[pic][0], b2_class_name=cls_of[pic][1],
                             gfx=gfx_of.get(cls), sprite=code, sprite_name=sname, intro=speech(words, ec), lose=speech(lwords, ec), sets=lists[monset]))
    assert len(trainers) == 300, len(trainers)
    wild, npcs, speeches = pike_c()
    for lv in wild.values():
        for tab in lv:
            for m in tab:
                m['species_id'] = b2s['SPECIES_' + m['species']]
                m['move_ids'] = [b2m[MOVE_ALIAS.get(x, x)] for x in m['moves']]
    for n in npcs:
        n['sprite'], n['sprite_name'] = sapphire_name(n['gfx'])
    lu = lucy()
    for party in lu:
        for m in party:
            m['species_id'] = b2s['SPECIES_' + m['species']]
            m['item_id'] = b2i[ITEM_ALIAS.get(m['item'], m['item'])]
            m['move_ids'] = [b2m[MOVE_ALIAS.get(x, x)] for x in m['moves']]
    if unknown: raise SystemExit(f'not in Black 2: {dict(unknown)}')
    for i, t in enumerate(trainers):        # Emerald draws 3 with different species and items: at least 3 species
        assert len({sets[k]['species'] for k in t['sets']}) >= 3, (i, t['name'])
        assert len({sets[k]['species'] for k in t['sets'] if k <= HIGH_TIER}) >= 3, ('lv50', i, t['name'])
    doc = __doc__.strip().split('\n\n')[0] + ' GENERATED by converter/gen_frontier_pike.py.'
    json.dump({'_doc': doc, 'high_tier': HIGH_TIER, 'ev_order': EV_ORDER, 'pokemon_obj': POKEMON_OBJ,
               'trainers': trainers, 'sets': sets, 'lucy': lu, 'wild': wild,
               'npcs': npcs, 'npc_speech': [speech(w, ec) for w in speeches]},
              open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    write_room_texts(trainers, [speech(w, ec) for w in speeches])
    lens = [len(t['sets']) for t in trainers]
    print(f'{len(trainers)} trainers ({len(set(t["b2_class"] for t in trainers))} Black 2 classes), {len(sets)} sets, '
          f'lists {min(lens)}-{max(lens)} ({sum(lens)} entries) -> {os.path.relpath(OUT, ROOT)}')

# ---------------------------------------------------------------------------------------------------- the rooms' texts
# Each Pike room's text file (src/text/script/emerald/NNNN_room_<map>.txt, NNNN = the zone's Black 2 text number; the
# build writes it at the room's own number, data/emerald/hoenn_interiors.json own_text) lists these lines in this order; src/field_scripts/scenes/frontier_pike_lines.inc names
# their numbers (PKL_<room>_<name>). Emerald's texts word for word (gen3text.convert); "=" lines are written here (menu
# entries in Black 2's capitalisation, the results board, lines Emerald builds from pieces).
P = 'BattleFrontier_BattlePike'
ROOMS = [
 ('LOBBY', 628, 'BattleFrontier_BattlePikeLobby', [
  # lines 0-22: frontier_core's lobby text block (hoenn_frontier.inc FRT_*, b2tools/frontier_text.py lobby_block)
  ('HIKER', P + 'Lobby_Text_OneRoomAwayFromGoal'), ('TWIN', P + 'Lobby_Text_NeverHadToBattleTrainer'),
  ('BEAUTY', P + 'Lobby_Text_ThinkAbilitiesUsefulHere'), ('RULES_LISTED', P + 'Lobby_Text_RulesAreListed'),
  ('READ_WHICH', P + 'Lobby_Text_ReadWhichHeading'), ('RULE_BAG', P + 'Lobby_Text_ExplainPokenavBagRules'),
  ('RULE_ITEMS', P + 'Lobby_Text_ExplainHeldItemRules'), ('RULE_ORDER', P + 'Lobby_Text_ExplainMonOrderRules'),
  ('M_RULE_BAG', '=PokéNav and Bag'), ('M_RULE_ITEMS', '=Held Items'),
  ('M_RULE_ORDER', '=Pokémon Order'),
  # the results board (Emerald's frontier_results window, ShowPikeResultsWindow) as messages: the title, then each
  # level's rooms cleared (Current while its streak goes on, else Prev.), record and times cleared in words 1-3
  ('RES_TITLE', "={0100:0}’s Battle Choice Results"),
  ('RES_50_CUR', "=Lv. 50  Current: Rooms cleared: {0100:1}\\nRecord: Rooms cleared: {0100:2}{be00}\\nTotal: Times cleared: {0100:3}"),
  ('RES_50_PREV', "=Lv. 50  Prev.: Rooms cleared: {0100:1}\\nRecord: Rooms cleared: {0100:2}{be00}\\nTotal: Times cleared: {0100:3}"),
  ('RES_OPEN_CUR', "=Open Lv.  Current: Rooms cleared: {0100:1}\\nRecord: Rooms cleared: {0100:2}{be00}\\nTotal: Times cleared: {0100:3}"),
  ('RES_OPEN_PREV', "=Open Lv.  Prev.: Rooms cleared: {0100:1}\\nRecord: Rooms cleared: {0100:2}{be00}\\nTotal: Times cleared: {0100:3}"),
 ]),
 ('CORRIDOR', 629, 'BattleFrontier_BattlePikeCorridor', [('BEGUN', P + 'Corridor_Text_YourChallengeHasBegun')]),
 ('THREE', 630, 'BattleFrontier_BattlePikeThreePathRoom', [
  ('ROOM1', P + 'ThreePathRoom_Text_CurrentlyInRoom1'), ('ROOM3', P + 'ThreePathRoom_Text_CurrentlyInRoom3'),
  ('ROOM5', P + 'ThreePathRoom_Text_CurrentlyInRoom5'), ('ROOM7', P + 'ThreePathRoom_Text_CurrentlyInRoom7'),
  ('ROOM9', P + 'ThreePathRoom_Text_CurrentlyInRoom9'), ('ROOM11', P + 'ThreePathRoom_Text_CurrentlyInRoom11'),
  ('ROOM13', P + 'ThreePathRoom_Text_CurrentlyInRoom13'),
  ('CONTINUE', P + 'ThreePathRoom_Text_ContinueWithChallenge'), ('SAVE_QUIT', P + 'ThreePathRoom_Text_SaveChallengeAndQuit'),
  ('RETIRE', P + 'ThreePathRoom_Text_RetireFromChallenge'), ('AWAITING', P + 'ThreePathRoom_Text_AwaitingReturnSaveBeforeResume'),
  ('ENJOY', P + 'ThreePathRoom_Text_PleaseEnjoyChallenge'), ('SAVING', P + 'ThreePathRoom_Text_SavingYourData'),
  ('BLOCKED', P + '_Text_PathBlockedNoTurningBack'), ('DIFFICULT', P + 'ThreePathRoom_Text_FindingItDifficultToChoose'),
  ('APOLOGIZE', P + 'ThreePathRoom_Text_ApologizeForImpertinence'), ('RIGHT', P + 'ThreePathRoom_Text_SomethingAboutRightPath'),
  ('CENTER', P + 'ThreePathRoom_Text_SomethingAboutCenterPath'), ('LEFT', P + 'ThreePathRoom_Text_SomethingAboutLeftPath'),
  ('AROMA', P + 'ThreePathRoom_Text_AromaOfPokemon'), ('PEOPLE', P + 'ThreePathRoom_Text_PresenceOfPeople'),
  ('WHISPER', P + 'ThreePathRoom_Text_HeardWhispering'), ('NOSTALGIA', P + 'ThreePathRoom_Text_WaveOfNostaliga'),
  ('TERRIFYING', P + 'ThreePathRoom_Text_TerrifyingEvent'), ('DREADFUL', P + 'ThreePathRoom_Text_DreadfulPresence'),
  ('M_YES', '=Yes'), ('M_NO', '=No'),
 ]),
 ('ROOM', 631, 'BattleFrontier_BattlePikeRoomNormal', [
  ('FULL_HEAL', 'WillRestoreToFullHealth'), ('ENJOY', 'EnjoyRestOfChallenge'), ('HEAL_ONE', 'WillRestoreOneMon'),
  ('FAREWELL', 'BestOfLuckFarewell'), ('WATCH_OUT', 'WatchOut'), ('KIRLIA_STOP', 'KirliaStop'),
  ('DUSCLOPS_STOP', 'DusclopsStop'), ('K_TOXIC', 'KirliaUsedToxic'), ('K_HYPNOSIS', 'KirliaUsedHypnosis'),
  ('K_TWAVE', 'KirliaUsedThunderWave'), ('K_WISP', 'KirliaUsedWillOWisp'), ('D_WISP', 'DusclopsUsedWillOWisp'),
  ('D_ICE', 'DusclopsUsedIceBeam'), ('ENOUGH', 'ThatsEnough'), ('SORRY_KIRLIA', 'ApologizeForKirlia'),
  ('SORRY_DUSCLOPS', 'ApologizeForDusclops'), ('STARTLED', 'AttacksWhenStartled'), ('HOPE_FINE', 'ApologizeHopeMonsAreFine'),
  ('SILENCE', 'Silence'), ('TOUGH', 'BattleSomewhatToughTrainer'), ('RESTORE', 'RestoreToFullHealth'),
  ('ENJOY2', 'EnjoyRestOfChallenge2'), ('QUEEN', 'ImThePikeQueen'), ('USED_UP_LUCK', 'HopeYouDidntUseUpLuck'),
  ('SHOW_PASS', 'LucyShowMeFrontierPass'), ('LUCK_SYMBOL', 'ReceivedLuckSymbol'), ('DISAPPEAR', 'AllThereIsDisappear'),
  ('YOU_AGAIN', 'LucyYouAgain'), ('COME_ON', 'NowComeOn'), ('PASS', 'LucyFrontierPass'),
  ('GOLDEN', 'LuckSymbolTookGoldenShine'), ('NOT_FORGET', 'IWontForget'), ('NO_HEAL', 'ChoseRoomNoHeal'),
  ('HEAL_ONE_Q', 'ChoseRoomHealOne'), ('HEAL_TWO_Q', 'ChoseRoomHealTwo'), ('FETCH', 'ShallFetchOurMaster'),
  ('HEAL_TWO', 'WillRestoreTwoMons'), ('BLOCKED', '!' + P + '_Text_PathBlockedNoTurningBack'),
 ]),
 ('WILD', 632, 'BattleFrontier_BattlePikeRoomWildMons', [('BLOCKED', P + '_Text_PathBlockedNoTurningBack')]),
 ('FINAL', 633, 'BattleFrontier_BattlePikeRoomFinal', [('CONGRATS', P + 'RoomFinal_Text_CongratsThisWayPlease')]),
]

def write_room_texts(trainers, speeches):
    from gen_trainers import load_texts
    tx = load_texts(EM)
    defs = ['// The Battle Pike rooms\' text lines (src/text/script/emerald/0628-0633_room_*.txt). GENERATED by',
            '// converter/gen_frontier_pike.py (write_room_texts): do not edit.', '#ifndef FRONTIER_PIKE_LINES_INC',
            '#define FRONTIER_PIKE_LINES_INC']
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import frontier_text
    for key, num, room, lines in ROOMS:
        out = []
        if key == 'LOBBY':                  # frontier_core's lobby block first (fr_lobby_attendant / fr_lobby_returned)
            defs.append('#define PKL_LOBBY_TB 0')
            out += [t for _, _, t in frontier_text.lobby_block(room)]   # (word 1 of the "not enough" lines: frontier_core's banned names)
        for name, label in lines:
            if label.startswith('='): line = label[1:]
            else:
                if label.startswith('!'): label = label[1:]
                elif room.endswith('RoomNormal') and not label.startswith(P) and not label.startswith('BattleFrontier_Text'):
                    label = P + 'RoomNormal_Text_' + label
                raw = tx[label]
                raw = raw.replace('{STR_VAR_1} ineligible', ' are ineligible')     # (CheckPartyIneligibility's " are")
                raw = raw.replace('{STR_VAR_1}', '\x00')                          # the BP amount: word 1
                line, unknown = convert(raw, expand=True)
                assert not unknown, (label, unknown)
                line = line.replace('\x00', '{0100:1}')
            defs.append(f'#define PKL_{key}_{name} {len(out)}')
            out.append(line)
        if key == 'ROOM':                     # the Frontier trainers' greetings (by trainer index) and the people's lines
            defs.append(f'#define PKL_ROOM_INTRO {len(out)}')
            out += [t['intro'] for t in trainers]
            defs.append(f'#define PKL_ROOM_SPEECH {len(out)}')
            out += speeches
            # in battle: what a Frontier trainer says when beaten (Emerald's speechLose, FRONTIER_PLAYER_WON_TEXT) and
            # Lucy's (gText_LucyDefeatSilver / _Gold): frontier_pike.c PK_TrainerMsgLoad
            defs.append(f'#define PKL_ROOM_LOSE {len(out)}')
            out += [t['lose'] for t in trainers]
            defs.append(f'#define PKL_ROOM_LUCY_LOSE {len(out)}')
            for lab in ('gText_LucyDefeatSilver', 'gText_LucyDefeatGold'):
                line, unknown = convert(tx[lab], expand=True); assert not unknown
                out.append(line)
        path = os.path.join(ROOT, 'src', 'text', 'script', 'emerald', f'{num:04d}_room_{room}.txt')
        open(path, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    defs.append('#endif')
    open(os.path.join(ROOT, 'src', 'field_scripts', 'scenes', 'frontier_pike_lines.inc'), 'w', encoding='utf-8').write('\n'.join(defs) + '\n')
    return len(ROOMS)

if __name__ == '__main__':
    main()
