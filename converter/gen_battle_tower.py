"""Sapphire's Battle Tower trainers and Pokémon sets -> data/battle_tower.json (battle_tower agent, 2026-10-08;
notes/BATTLE_TOWER.md). b2tools/patches/battle_tower.py writes them into Black 2's Battle Subway archives.

    python3 gen_battle_tower.py

Source (pokeruby, English): src/data/battle_tower/trainers.h (100 trainers: facility class, name, team flags, a greeting
of six easy-chat words), level_50_mons.h / level_100_mons.h (300 sets each: species, held item index, team flags, four
moves, EV spread flags, nature), src/battle_tower.c (sBattleTowerHeldItems, the pools of FillBattleTowerTrainerParty, the
fixed IVs, sMale/FemaleTrainerClasses + their overworld sprites), src/data/pokemon/trainer_class_lookups.h (class ->
picture), src/easy_chat_2.c sub_80EB544 (how a greeting prints: three rows of two words, a space after every word but
a row's last, a new line after row 1 and a scroll after row 2).

Sapphire's party rule (FillBattleTowerTrainerParty): trainer t draws from the sets [offset, offset + pool) of the level's
table, keeping only sets whose team flags contain all of t's (any set when t's flags are 0), with no two of the same
species or the same held item:  t < 20: sets 0-59, IV 6;  20-29: 30-89, IV 9;  30-39: 60-119, 12;  40-49: 90-149, 15;
50-59: 120-179, 18;  60-69: 150-209, 21;  70-79: 180-239, 31;  80-99: 200-299, 31.  Each trainer's candidate list here is
exactly that filtered pool, in table order (Black 2's records list the sets a trainer may use).

Black 2 names: species / moves / items by their constant names (aliases as converter/gen_trainers.py), trainer classes by
Sapphire's picture through data/hoenn_trainer_classes.json (the classes Hoenn's own trainers use), overworld sprites
through data/sprite_map.json. Text in Gen 5 capitalisation (gen3text.convert): names, and the greetings word by word
(easy-chat words are written in Black 2's easy-chat style: lower case, sentence capitals, no space before ! ? ...)."""
import os, re, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from gen3text import convert  # noqa: E402

RUBY = os.path.join(ROOT, 'external', 'pokeruby')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
OUT = os.path.join(ROOT, 'data', 'battle_tower.json')
ITEM_ALIAS = {'ITEM_STICK': 'ITEM_STICK'}
MOVE_ALIAS = {'MOVE_SELF_DESTRUCT': 'MOVE_SELFDESTRUCT', 'MOVE_SMOKESCREEN': 'MOVE_SMOKE_SCREEN'}
SPECIES_ALIAS = {}
# FillBattleTowerTrainerParty: (first trainer id of the tier, IV, set offset, pool size)
TIERS = [(0, 6, 0, 60), (20, 9, 30, 60), (30, 12, 60, 60), (40, 15, 90, 60), (50, 18, 120, 60), (60, 21, 150, 60),
         (70, 31, 180, 60), (80, 31, 200, 100)]
EV_ORDER = ['HP', 'ATTACK', 'DEFENSE', 'SPEED', 'SP_ATTACK', 'SP_DEFENSE']     # F_EV_SPREAD_* bits 0-5 (battle_tower.h)
# easy-chat words that attach to the word before them (Black 2's easy-chat sentences) and the ones that stay capitalised
PUNCT = {'!', '!!', '?', '?!', '!?', '…', '...', '-', '.', ','}

def defines(path, prefix):
    return {m.group(1): int(m.group(2), 0) for m in re.finditer(rf'#define\s+({prefix}\w+)\s+\(?(0x[0-9a-fA-F]+|\d+)', open(path).read())}

def enum(path, name_re):
    """Names of the first enum in path whose members match name_re, in order (value = index)."""
    src = open(path).read()
    return re.findall(rf'^\s*({name_re}),?', src, re.M)

def tier(t):
    return [x for x in TIERS if x[0] <= t][-1]

def load_mons(fname):
    out = []
    src = open(os.path.join(RUBY, 'src', 'data', 'battle_tower', fname)).read()
    for blk in re.findall(r'\{\s*\.species(.*?)\.nature = (\w+),\s*\}', src, re.S):
        body, nature = blk
        out.append(dict(
            species=re.search(r'= (SPECIES_\w+)', body).group(1),
            item=re.search(r'\.heldItem = (BATTLE_TOWER_ITEM_\w+)', body).group(1),
            team_flags=int(re.search(r'\.teamFlags = (0x[0-9A-Fa-f]+|\d+)', body).group(1), 0),
            moves=re.findall(r'(MOVE_\w+)', re.search(r'\.moves = \{(.*?)\}', body, re.S).group(1)),
            ev=sorted({b for b in re.findall(r'F_EV_SPREAD_(\w+)', re.search(r'\.evSpread = ([^,]*),', body).group(1))},
                      key=EV_ORDER.index),
            nature=nature))
    return out

def load_trainers():
    out = []
    src = open(os.path.join(RUBY, 'src', 'data', 'battle_tower', 'trainers.h')).read()
    for cls, name, flags, words in re.findall(r'\.trainerClass = FACILITY_CLASS_(\w+),\s*\.name = _\("(.*?)"\),\s*'
                                              r'\.teamFlags = (0x[0-9A-Fa-f]+|\d+),\s*\.greeting = \{(.*?)\}', src, re.S):
        out.append(dict(facility_class=cls, name=name, team_flags=int(flags, 0),
                        greeting=re.findall(r'EC_WORD_\w+|EC_POKEMON2?\(\w+\)|EC_MOVE2?\(\w+\)', words)))
    return out

def easy_chat_words():
    """EC_WORD_* -> Sapphire's English word (src/data/text/easy_chat/groups/<group>/words.h, index = the word's low 9
    bits within its group, include/constants/easy_chat.h)."""
    hdr = open(os.path.join(RUBY, 'include', 'constants', 'easy_chat.h')).read()
    groups = {int(v, 0): g for g, v in re.findall(r'#define EC_GROUP_(\w+)\s+(0x[0-9a-fA-F]+|\d+)', hdr)}
    words = {}
    gw = open(os.path.join(RUBY, 'src', 'data', 'text', 'easy_chat', 'group_words.h')).read()
    folders = re.findall(r'#include "groups/(\w+)/words.h"', gw)
    lists = {}
    for f in folders:
        s = open(os.path.join(RUBY, 'src', 'data', 'text', 'easy_chat', 'groups', f, 'words.h'), encoding='utf-8').read()
        m = re.search(r'#if ENGLISH(.*?)#elif', s, re.S) or re.search(r'(.*)', s, re.S)
        lists[f.upper()] = re.findall(r'"(.*?)\$"', m.group(1))
    status = set()
    for name, grp, idx in re.findall(r'#define (EC_WORD_\w+)\s+\(EC_GROUP_(\w+) << 9\) \| (0x[0-9a-fA-F]+|\d+)', hdr):
        if grp == 'STATUS': status.add(name)
        lst = lists.get(grp)
        if lst is not None and int(idx, 0) < len(lst): words[name] = lst[int(idx, 0)]
    # EC_POKEMON(X) / EC_MOVE(X): the Pokémon's / move's name; Black 2's own spelling (system texts 90 / 403, by the
    # Black 2 constant of the same name), so they read as Black 2 names them
    sp_names = open(f'{B2}/data/text/system/0090_species_names.txt', encoding='utf-8').read().split('\n')
    mv_names = open(f'{B2}/data/text/system/0403_move_names.txt', encoding='utf-8').read().split('\n')
    b2_species = defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2_moves = defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    # proper nouns among the words keep capitals in Black 2's style: abilities and types (Sapphire's "status" group,
    # Black 2's spelling from system texts 374 / 398, matched without spaces), weekdays, the Battle Tower
    proper = {re.sub(r'[^A-Z]', '', n.upper()): n for f in ('0374_ability_names.txt', '0398_type_names.txt')
              for n in open(f'{B2}/data/text/system/{f}', encoding='utf-8').read().split('\n') if n.strip()}
    for k, v in list(words.items()):
        key = re.sub(r'[^A-Z]', '', v)
        if v in ('BATTLE TOWER',) or v.endswith('DAY') and v not in ('DAY', 'TODAY', 'YESTERDAY', 'HOLIDAY', 'BIRTHDAY'):
            words[k] = '\x01' + ' '.join(w[0] + w[1:].lower() for w in v.split())
        elif key in proper and k in status:
            words[k] = '\x01' + proper[key]
    for kind, table, names in (('POKEMON', b2_species, sp_names), ('MOVE', b2_moves, mv_names)):
        for n, i in table.items():
            words[f'EC_{kind}({n.split("_", 1)[1]})'] = words[f'EC_{kind}2({n.split("_", 1)[1]})'] = '\x01' + names[i]
    return words

def greeting_text(words, ec):
    """Sapphire's sub_80EB544(dst, words, 2, 3) layout (rows of two words; \\n after row 1, \\l after row 2) with the
    words in Black 2's easy-chat style."""
    rows = [words[0:2], words[2:4], words[4:6]]
    out = []
    first = True
    for r, row in enumerate(rows):
        s = ''
        for w in row:
            if w == 'EC_WORD_NONE' or w not in ec: continue   # 0xFFFF: nothing (and no space)
            t = ec[w]
            if t.startswith('\x01'):                        # a Pokémon or move name, as Black 2 writes it
                s += t[1:] + ' '; first = False
                continue
            if t in PUNCT:
                s = s.rstrip() + t + ' '
                if t in ('!', '!!', '?', '?!', '!?', '.'): first = True
                continue
            low = t.lower() if t not in ('I', "I'M", "I'LL", "I'VE", 'I’M', 'I’LL', 'I’VE') else t[0] + t[1:].lower()
            low = re.sub(r"\bi(\b|')", lambda m: 'I' + m.group(1), low).replace('pokémon', 'Pokémon')
            if first: low = low[:1].upper() + low[1:]; first = False
            s += low + ' '
        out.append(s.rstrip())
    text = out[0] + '\\n' + out[1] + '\\l' + out[2]
    line, unknown = convert(text, expand=True)
    assert not unknown, unknown
    return line

def main():
    b2_species = defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2_moves = defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    b2_items = defines(f'{B2}/include/constants/items.h', 'ITEM_')
    held = re.findall(r'^\s*(ITEM_\w+),', re.search(r'sBattleTowerHeldItems\[\] =\s*\{(.*?)\};',
                      open(f'{RUBY}/src/battle_tower.c').read(), re.S).group(1), re.M)
    bt_items = enum(f'{RUBY}/include/battle_tower.h', r'BATTLE_TOWER_ITEM_\w+')
    assert len(held) == len(bt_items) == 63, (len(held), len(bt_items))
    unknown = collections.Counter()
    def b2(table, name, alias, kind):
        n = alias.get(name, name)
        if n not in table: unknown[f'{kind} {name}'] += 1; return 0
        return table[n]
    sets = {}
    for lv, fname in ((50, 'level_50_mons.h'), (100, 'level_100_mons.h')):
        mons = load_mons(fname)
        assert len(mons) == 300, (fname, len(mons))
        sets[lv] = [dict(m, species_id=b2(b2_species, m['species'], SPECIES_ALIAS, 'species'),
                         item_name=held[bt_items.index(m['item'])],
                         item_id=b2(b2_items, held[bt_items.index(m['item'])], ITEM_ALIAS, 'item'),
                         move_ids=[b2(b2_moves, x, MOVE_ALIAS, 'move') for x in m['moves']]) for m in mons]
    trainers = load_trainers()
    assert len(trainers) == 100, len(trainers)
    # facility class (= Sapphire trainer class index, include/constants/trainers.h) -> picture -> Black 2 class
    consts = re.findall(r'^\s*FACILITY_CLASS_(\w+),?\s*$', open(f'{RUBY}/include/constants/trainers.h').read(), re.M)
    pics = re.findall(r'TRAINER_PIC_(\w+),', open(f'{RUBY}/src/data/pokemon/trainer_class_lookups.h').read().split('gTrainerClassToNameIndex')[0])
    names_idx = re.findall(r'TRAINER_CLASS_(\w+),', open(f'{RUBY}/src/data/pokemon/trainer_class_lookups.h').read().split('gTrainerClassToNameIndex')[1])
    review = {r['sapphire_pic']: r for r in json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json')))['review']}
    sprite_map = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
    bt = open(f'{RUBY}/src/battle_tower.c').read()
    def table(name, pat):
        return re.findall(pat, re.search(rf'{name}\[\] =\s*\{{(.*?)\}};', bt, re.S).group(1))
    male, female = table('sMaleTrainerClasses', r'FACILITY_CLASS_(\w+)'), table('sFemaleTrainerClasses', r'FACILITY_CLASS_(\w+)')
    male_gfx, female_gfx = table('sMaleTrainerGfxIds', r'(OBJ_EVENT_GFX_\w+)'), table('sFemaleTrainerGfxIds', r'(OBJ_EVENT_GFX_\w+)')
    ec = easy_chat_words()
    out_tr = []
    for i, t in enumerate(trainers):
        c = consts.index(t['facility_class'])
        pic = pics[c]
        if pic not in review: raise SystemExit(f'trainer {i} {t["name"]}: Sapphire picture {pic} has no Black 2 class')
        gfx = (male_gfx[male.index(t['facility_class'])] if t['facility_class'] in male else
               female_gfx[female.index(t['facility_class'])] if t['facility_class'] in female else 'OBJ_EVENT_GFX_BOY_1')
        first, iv, off, pool = tier(i)
        cand = {lv: [k for k in range(off, off + pool) if t['team_flags'] == 0 or
                     (sets[lv][k]['team_flags'] & t['team_flags']) == t['team_flags']] for lv in (50, 100)}
        name, unk = convert(t['name'], expand=True)
        assert not unk
        out_tr.append(dict(index=i, name=name, facility_class=t['facility_class'], class_name_index=names_idx[c],
                           pic=pic, b2_class=review[pic]['b2_class'], b2_class_name=review[pic]['name'],
                           gfx=gfx, sprite=sprite_map[gfx]['code'], team_flags=t['team_flags'], iv=iv,
                           greeting_words=t['greeting'], greeting=greeting_text(t['greeting'], ec),
                           sets_50=cand[50], sets_100=cand[100]))
        for lv in (50, 100):
            # Sapphire picks 3 with different species and items: at least that many must exist
            sp = {sets[lv][k]['species'] for k in cand[lv]}
            assert len(sp) >= 3, (i, lv, len(cand[lv]))
    if unknown: raise SystemExit(f'not in Black 2: {dict(unknown)}')
    doc = __doc__.strip().split('\n\n')[0] + ' GENERATED by converter/gen_battle_tower.py.'
    json.dump({'_doc': doc, 'tiers': TIERS, 'ev_order': EV_ORDER, 'trainers': out_tr,
               'sets_50': [{k: m[k] for k in ('species', 'species_id', 'item_name', 'item_id', 'team_flags', 'moves',
                                              'move_ids', 'ev', 'nature')} for m in sets[50]],
               'sets_100': [{k: m[k] for k in ('species', 'species_id', 'item_name', 'item_id', 'team_flags', 'moves',
                                               'move_ids', 'ev', 'nature')} for m in sets[100]]},
              open(OUT, 'w'), indent=1, ensure_ascii=False)
    # Black 2's Battle Subway texts of trainer id t (b2tools/patches/battle_tower.py: Sapphire trainer k = ids k and
    # 100 + k): system 15 line t = the name; 376 line 3t = what the trainer says before the battle (Sapphire's greeting),
    # 3t + 1 / 3t + 2 = Black 2's in-battle win / lose lines (ov167 func_ov167_021d5700): Sapphire's tower trainers have
    # none, so they stay empty
    names, lines = {}, {}
    for t in out_tr:
        for tid in (t['index'], 100 + t['index']):
            names[str(tid)] = t['name']
            lines[str(3 * tid)] = t['greeting']
            lines[str(3 * tid + 1)] = ''
            lines[str(3 * tid + 2)] = ''
    json.dump({'_doc': 'Battle Tower trainers in Black 2\'s Battle Subway texts (system 15 names, 376 lines). GENERATED by '
                       'converter/gen_battle_tower.py.', 'system/0015.txt': names, 'system/0376.txt': lines},
              open(os.path.join(ROOT, 'src', 'text', 'overrides_battle_tower.json'), 'w'), indent=1, ensure_ascii=False)
    lens = [len(t['sets_50']) for t in out_tr] + [len(t['sets_100']) for t in out_tr]
    print(f'{len(out_tr)} trainers, 2 x 300 sets -> {os.path.relpath(OUT, ROOT)}; candidate lists {min(lens)}-{max(lens)} sets')

if __name__ == '__main__':
    main()
