"""Pokémon Emerald's Battle Frontier data for Pokémon Emerald NDS (frontier_factory_dome, 2026-10-12;
notes/FRONTIER_FACTORY_DOME.md) -> data/emerald/frontier.json. b2tools/patches/frontier_factory_dome.py writes it into
Black 2's Battle Subway set archive (arc 211, files 1000 on) and its C code reads it there.

    python3 gen_frontier_emerald.py            (writes data/emerald/frontier.json; --check: compare only)

Source (pokeemerald, English):
  src/data/battle_frontier/battle_frontier_mons.h      gBattleFrontierMons: 882 sets (species, 4 moves, held item index,
                                                        EV spread flags, nature)
  src/battle_tower.c                                    gBattleFrontierHeldItems (the index -> item), sFrontierTrainerIdRanges
                                                        / ...Hard (GetRandomScaledFrontierTrainerId)
  src/data/battle_frontier/battle_frontier_trainers.h  gBattleFrontierTrainers: 300 trainers (facility class, name, the
                                                        three easy-chat speeches, their set list)
  src/data/battle_frontier/battle_frontier_trainer_mons.h  the set lists (macros of FRONTIER_MON_* ids)
  src/data/pokemon/trainer_class_lookups.h              gFacilityClassToPicIndex (facility class -> trainer picture)
  src/battle_factory.c                                  sInitialRentalMonRanges, sFixedIVTable, the battle-style move lists
  src/battle_dome.c                                     GetDomeTrainerMonIvs, GetTypeEffectivenessPoints' inputs
  src/frontier_util.c                                   sFrontierBrainsMons (Tucker's two parties)
  src/data/pokemon/species_info.h, src/data/battle_moves.h, src/battle_main.c gTypeEffectiveness: Gen 3 types, abilities,
                                                        base stats, move types and power, the type chart (the Dome's
                                                        NPC-vs-NPC result and its opponents' choice of two)

Black 2 names: species / moves / items by constant name (as converter/gen_battle_tower.py); trainer classes by
Emerald's picture through data/hoenn_trainer_classes.json + data/emerald/ (version.load_json, "emerald_pics"; its
"sprite" is the class's battle picture). The overworld sprite (the opponent walking into the battle room, the Dome's
bracket) is Emerald's own: src/battle_tower.c gTowerMale/FemaleTrainerGfxIds by facility class (OBJ_EVENT_GFX_BOY_1
for the rest, GetBattleFacilityTrainerGfxId), its Black 2 object code from data/sprite_map.json (+ data/emerald/), the
renamed people by pokeruby's name of the same picture (IMG_ALIAS, as converter/gen_frontier_pike.py). Text in Gen 5 capitalisation (gen3text.convert); the
speeches word by word as gen_battle_tower.greeting_text (Sapphire's easy-chat words, the same English words)."""
import os, re, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
from gen3text import convert  # noqa: E402
import gen_battle_tower as gbt  # noqa: E402

EM = os.path.join(ROOT, 'external', 'pokeemerald')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
OUT = os.path.join(ROOT, 'data', 'emerald', 'frontier.json')
GEN3_TYPES = ['NORMAL', 'FIGHTING', 'FLYING', 'POISON', 'GROUND', 'ROCK', 'BUG', 'GHOST', 'STEEL', 'MYSTERY', 'FIRE',
              'WATER', 'GRASS', 'ELECTRIC', 'PSYCHIC', 'ICE', 'DRAGON', 'DARK']
EV_ORDER = gbt.EV_ORDER
SPECIES_ALIAS = {'SPECIES_NIDORAN_F': 'SPECIES_NIDORAN_F', 'SPECIES_NIDORAN_M': 'SPECIES_NIDORAN_M'}
MOVE_ALIAS = dict(gbt.MOVE_ALIAS, MOVE_SOFT_BOILED='MOVE_SOFTBOILED')
ITEM_ALIAS = {}
IMG_ALIAS = {'POKEFAN_F': 'WOMAN_2', 'NINJA_BOY': 'LITTLE_BOY_1', 'LITTLE_BOY': 'LITTLE_BOY_2', 'LITTLE_GIRL': 'LITTLE_GIRL_2',
             'LINK_RECEPTIONIST': 'WOMAN_6', 'POKEFAN_M': 'MAN_3', 'RS_LITTLE_BOY': 'LITTLE_BOY_3', 'GAMEBOY_KID': 'BOY_5',
             'EXPERT_M': 'OLD_MAN_1', 'OLD_WOMAN': 'OLD_WOMAN_1', 'EXPERT_F': 'OLD_WOMAN_2', 'RICH_BOY': 'BOY_4', 'TWIN': 'LITTLE_GIRL_1'}
NATURES = ['NATURE_HARDY', 'NATURE_LONELY', 'NATURE_BRAVE', 'NATURE_ADAMANT', 'NATURE_NAUGHTY', 'NATURE_BOLD',
           'NATURE_DOCILE', 'NATURE_RELAXED', 'NATURE_IMPISH', 'NATURE_LAX', 'NATURE_TIMID', 'NATURE_HASTY',
           'NATURE_SERIOUS', 'NATURE_JOLLY', 'NATURE_NAIVE', 'NATURE_MODEST', 'NATURE_MILD', 'NATURE_QUIET',
           'NATURE_BASHFUL', 'NATURE_RASH', 'NATURE_CALM', 'NATURE_GENTLE', 'NATURE_SASSY', 'NATURE_CAREFUL',
           'NATURE_QUIRKY']   # (b2tools/patches/battle_tower.py NATURES: Gen 3 and Black 2 share the order)

def src(path):
    return open(os.path.join(EM, path), encoding='utf-8').read()

def defines(path, prefix):
    return {m.group(1): int(m.group(2), 0) for m in re.finditer(rf'#define\s+({prefix}\w*)\s+\(?(0x[0-9a-fA-F]+|\d+)\)?',
                                                                open(path).read())}

def block(text, name):
    m = re.search(rf'{name}\[[^\]]*\]\s*=\s*\{{(.*?)\n\}};', text, re.S)
    assert m, name
    return m.group(1)

def load_sets():
    body = block(src('src/data/battle_frontier/battle_frontier_mons.h'), 'gBattleFrontierMons')
    out = []
    for name, b in re.findall(r'\[(FRONTIER_MON_\w+)\]\s*=\s*\{(.*?)\n    \}', body, re.S):
        out.append(dict(id_name=name,
                        species=re.search(r'\.species = (SPECIES_\w+)', b).group(1),
                        moves=re.findall(r'(MOVE_\w+)', re.search(r'\.moves = \{(.*?)\}', b, re.S).group(1)),
                        item_index=re.search(r'\.itemTableId = (BATTLE_FRONTIER_ITEM_\w+)', b).group(1),
                        ev=sorted(set(re.findall(r'F_EV_SPREAD_(\w+)', re.search(r'\.evSpread = ([^\n]*)', b).group(1))),
                                  key=EV_ORDER.index),
                        nature=re.search(r'\.nature = (NATURE_\w+)', b).group(1)))
    ids = defines(os.path.join(EM, 'include', 'constants', 'battle_frontier_mons.h'), 'FRONTIER_MON_')
    assert [ids[s['id_name']] for s in out] == list(range(len(out))) and len(out) == 882, len(out)
    return out, ids

def held_items():
    bt = src('src/battle_tower.c')
    pairs = re.findall(r'\[(BATTLE_FRONTIER_ITEM_\w+)\]\s*=\s*(ITEM_\w+)', block(bt, 'gBattleFrontierHeldItems'))
    return dict(pairs)

def ranges(name):
    bt = src('src/battle_tower.c')
    tr = defines(os.path.join(EM, 'include', 'constants', 'battle_frontier_trainers.h'), 'FRONTIER_TRAINER_')
    return [[tr[a], tr[b]] for a, b in re.findall(r'\{(FRONTIER_TRAINER_\w+),\s*(FRONTIER_TRAINER_\w+)\}',
                                                     re.search(rf'{name}\[\]\[2\] =\s*\{{(.*?)\}};', bt, re.S).group(1))]

def load_trainers(mon_ids):
    tsrc = src('src/data/battle_frontier/battle_frontier_trainers.h')
    # the set lists use function-like macros (FRONTIER_MONS_BUG_CATCHER_1_EXTRA(a, b) with ##): the C preprocessor
    # expands them (clang -E, as pokeemerald's build), then every list is plain numbers
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as t:
        c = os.path.join(t, 'x.c')
        open(c, 'w').write('typedef unsigned short u16;\n#include "constants/battle_frontier_mons.h"\n'
                           '#include "data/battle_frontier/battle_frontier_trainer_mons.h"\n')
        pre = subprocess.run(['/opt/homebrew/opt/llvm/bin/clang', '-E', '-P', '-I', os.path.join(EM, 'include'),
                              '-I', os.path.join(EM, 'src'), c], capture_output=True, text=True, check=True).stdout
    sets = {}
    for name, body in re.findall(r'(gBattleFrontierTrainerMons_\w+)\[\]\s*=\s*\{(.*?)\};', pre, re.S):
        vals = [int(x, 0) for x in re.findall(r'-?\b(?:0x[0-9a-fA-F]+|\d+)\b', body)]
        sets[name] = [v for v in vals if 0 <= v < 882]
    out = []
    for cls, name, before, win, lose, mset in re.findall(
            r'\.facilityClass = FACILITY_CLASS_(\w+),\s*\.trainerName = _\("(.*?)"\),\s*\.speechBefore = \{(.*?)\},\s*'
            r'\.speechWin = \{(.*?)\},\s*\.speechLose = \{(.*?)\},\s*\.monSet = (\w+)', tsrc, re.S):
        w = lambda s: re.findall(r'EC_WORD_\w+|EC_EMPTY_WORD|EC_POKEMON2?\(\w+\)|EC_MOVE2?\(\w+\)', s)
        out.append(dict(facility_class=cls, name=name, before=w(before), win=w(win), lose=w(lose), mon_set_name=mset,
                        mon_set=sets[mset]))
    assert len(out) == 300, len(out)
    return out

def factory_tables(mon_ids):
    bf = src('src/battle_factory.c')
    rng = re.findall(r'\{(FRONTIER_MON\w*|NUM_FRONTIER_MONS - 1),\s*(FRONTIER_MON\w*|NUM_FRONTIER_MONS - 1)\}',
                     re.search(r'sInitialRentalMonRanges\[\]\[2\] =\s*\{(.*?)\};', bf, re.S).group(1))
    ids = dict(mon_ids); ids['NUM_FRONTIER_MONS - 1'] = 881
    ids['FRONTIER_MONS_HIGH_TIER'] = defines(os.path.join(EM, 'include', 'constants', 'battle_frontier_mons.h'), 'FRONTIER_MONS_HIGH_TIER')['FRONTIER_MONS_HIGH_TIER']
    ivs = [[int(a), int(b)] for a, b in re.findall(r'\{(\d+), (\d+)\}', re.search(r'sFixedIVTable\[\]\[2\] =\s*\{(.*?)\};', bf, re.S).group(1))]
    styles = []
    for lst in ('sMoves_TotalPreparation', 'sMoves_SlowAndSteady', 'sMoves_Endurance', 'sMoves_HighRiskHighReturn',
                'sMoves_WeakeningTheFoe', 'sMoves_ImpossibleToPredict', 'sMoves_DependsOnTheBattlesFlow'):
        styles.append([m for m in re.findall(r'MOVE_\w+', re.search(rf'{lst}\[\] =\s*\{{(.*?)\}};', bf, re.S).group(1))
                       if m != 'MOVE_NONE'])
    req = [int(x) for x in re.findall(r'= (\d+),', re.search(r'sRequiredMoveCounts\[[^\]]*\] =\s*\{(.*?)\};', bf, re.S).group(1))]
    return [[ids[a], ids[b]] for a, b in rng], ivs, styles, req

def gen3_species_info():
    body = src('src/data/pokemon/species_info.h')
    out = {}
    for name, b in re.findall(r'\[(SPECIES_\w+)\]\s*=\s*\n\s*\{(.*?)\n    \}', body, re.S):
        stats = [int(re.search(rf'\.{k}\s*=\s*(\d+)', b).group(1)) for k in
                 ('baseHP', 'baseAttack', 'baseDefense', 'baseSpeed', 'baseSpAttack', 'baseSpDefense')]
        types = re.search(r'\.types = \{\s*TYPE_(\w+),\s*TYPE_(\w+)\s*\}', b).groups()
        ab = re.search(r'\.abilities = \{\s*ABILITY_(\w+),', b).group(1)
        out[name] = dict(stats=stats, types=[GEN3_TYPES.index(t) for t in types], ability0=ab)
    return out

def gen3_moves():
    body = src('src/data/battle_moves.h')
    out = {}
    for name, b in re.findall(r'\[(MOVE_\w+)\]\s*=\s*\n\s*\{(.*?)\n    \}', body, re.S):
        out[name] = dict(power=int(re.search(r'\.power = (\d+)', b).group(1)), type=GEN3_TYPES.index(re.search(r'\.type = TYPE_(\w+)', b).group(1)))
    return out

def type_chart():
    body = re.search(r'gTypeEffectiveness\[\d+\] =\s*\{(.*?)\};', src('src/battle_main.c'), re.S).group(1)
    mul = {'TYPE_MUL_NO_EFFECT': 0, 'TYPE_MUL_NOT_EFFECTIVE': 5, 'TYPE_MUL_NORMAL': 10, 'TYPE_MUL_SUPER_EFFECTIVE': 20}
    out = []
    for a, d, m in re.findall(r'TYPE_(\w+), TYPE_(\w+), (TYPE_MUL_\w+)', body):
        if a in ('FORESIGHT', 'ENDTABLE'): continue     # the marker row (GetTypeEffectivenessPoints skips it, reads the rest)
        out.append([GEN3_TYPES.index(a), GEN3_TYPES.index(d), mul[m]])
    return out

def tucker():
    fu = src('src/frontier_util.c')
    dome = re.search(r'\[FRONTIER_FACILITY_DOME\] =\s*\{(.*?)\n    \},\n    \[FRONTIER_FACILITY_PALACE\]', fu, re.S).group(1)
    mons = []
    for b in re.findall(r'\{\s*\.species = (.*?)\n            \}', dome, re.S):
        mons.append(dict(species=re.match(r'(SPECIES_\w+)', b).group(1), item=re.search(r'\.heldItem = (ITEM_\w+)', b).group(1),
                         iv=re.search(r'\.fixedIV = (\w+)', b).group(1), nature=re.search(r'\.nature = (NATURE_\w+)', b).group(1),
                         evs=[int(x) for x in re.search(r'\.evs = \{(.*?)\}', b).group(1).split(',')],
                         moves=re.findall(r'MOVE_\w+', re.search(r'\.moves = \{(.*?)\}', b).group(1))))
    assert len(mons) == 6, len(mons)
    for m in mons: m['iv'] = 31 if m['iv'] == 'MAX_PER_STAT_IVS' else int(m['iv'])
    return {'silver': mons[:3], 'gold': mons[3:]}

def ow_sprites():
    """facility class -> (OBJ_EVENT_GFX_*, Black 2 object code): GetBattleFacilityTrainerGfxId's tables."""
    import version
    bt = src('src/battle_tower.c')
    def table(name, pat):
        return re.findall(pat, re.search(rf'{name}\[\w*\] =\s*\{{(.*?)\}};', bt, re.S).group(1))
    gfx = dict(zip(table('gTowerMaleFacilityClasses', r'FACILITY_CLASS_(\w+)'), table('gTowerMaleTrainerGfxIds', r'(OBJ_EVENT_GFX_\w+)')))
    gfx.update(zip(table('gTowerFemaleFacilityClasses', r'FACILITY_CLASS_(\w+)'), table('gTowerFemaleTrainerGfxIds', r'(OBJ_EVENT_GFX_\w+)')))
    smap = version.load_json(os.path.join(ROOT, 'data', 'sprite_map.json'))
    def code(g):
        n = g.replace('OBJ_EVENT_GFX_', '')
        for k in (g, 'OBJ_EVENT_GFX_' + IMG_ALIAS.get(n, n)):
            if k in smap: return smap[k]['code']
        raise SystemExit(f'no Black 2 sprite for {g}')
    return lambda cls: (gfx.get(cls, 'OBJ_EVENT_GFX_BOY_1'), code(gfx.get(cls, 'OBJ_EVENT_GFX_BOY_1')))

def speech_text(words, ec):
    """Emerald's FrontierSpeechToString (src/battle_tower.c): the six words as two rows of three; when that is wider
    than the message box (204 px, here: a row of more than 30 characters), as three rows of two with a scroll after the
    second (Sapphire's layout, gen_battle_tower.greeting_text). Words in Black 2's easy-chat style (greeting_text's)."""
    def rows(cols):
        out, first = [], True
        for r in range(0, 6, cols):
            s = ''
            for w in words[r:r + cols]:
                if w in ('EC_EMPTY_WORD', 'EC_WORD_NONE') or w not in ec: continue
                t = ec[w]
                if t.startswith('\x01'): s += t[1:] + ' '; first = False; continue
                if t in gbt.PUNCT:
                    s = s.rstrip() + t + ' '
                    if t in ('!', '!!', '?', '?!', '!?', '.'): first = True
                    continue
                low = t.lower() if t not in ('I', "I'M", "I'LL", "I'VE", 'I’M', 'I’LL', 'I’VE') else t[0] + t[1:].lower()
                low = re.sub(r"\bi(\b|')", lambda m: 'I' + m.group(1), low).replace('pokémon', 'Pokémon')
                if first: low = low[:1].upper() + low[1:]; first = False
                s += low + ' '
            out.append(s.rstrip())
        return out
    r = rows(3)
    text = r[0] + '\\n' + r[1] if max(len(x) for x in r) <= 30 else (lambda q: q[0] + '\\n' + q[1] + '\\l' + q[2])(rows(2))
    line, unknown = convert(text, expand=True)
    assert not unknown, unknown
    return line

def main(check=False):
    import version
    b2_species = gbt.defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2_moves = gbt.defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    b2_items = gbt.defines(f'{B2}/include/constants/items.h', 'ITEM_')
    unknown = collections.Counter()
    def b2(table, name, alias, kind):
        n = alias.get(name, name)
        if n not in table: unknown[f'{kind} {name}'] += 1; return 0
        return table[n]
    sets, mon_ids = load_sets()
    items = held_items()
    info, moves = gen3_species_info(), gen3_moves()
    fr_ranges, fixed_iv, style_lists, style_req = factory_tables(mon_ids)
    style_of = {m: k + 1 for k, lst in enumerate(style_lists) for m in lst}   # FACTORY_STYLE_* (1-7), first list wins
    out_sets = []
    for s in sets:
        sp = info[s['species']]
        mt = [moves[m]['type'] if moves[m]['power'] else 255 for m in s['moves']] + [255] * (4 - len(s['moves']))
        out_sets.append(dict(
            species=s['species'], species_id=b2(b2_species, s['species'], SPECIES_ALIAS, 'species'),
            moves=s['moves'], move_ids=[b2(b2_moves, m, MOVE_ALIAS, 'move') for m in s['moves']],
            item=items[s['item_index']], item_id=b2(b2_items, items[s['item_index']], ITEM_ALIAS, 'item') if items[s['item_index']] != 'ITEM_NONE' else 0,
            ev=s['ev'], nature=s['nature'], nature_id=NATURES.index(s['nature']),
            types=sp['types'], levitate=sp['ability0'] == 'LEVITATE', wonder_guard=sp['ability0'] == 'WONDER_GUARD',
            stat_sum10=sum(sp['stats']) // 10, move_types=mt[:4],
            styles=[style_of.get(m, 0) for m in s['moves']] + [0] * (4 - len(s['moves']))))
    # trainers: facility class -> picture -> Black 2 class (the Emerald trainer-class review)
    pics = dict(re.findall(r'\[FACILITY_CLASS_(\w+)\] = TRAINER_PIC_(\w+)', block(src('src/data/pokemon/trainer_class_lookups.h'), 'gFacilityClassToPicIndex')))
    review = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json'))['review']
    by_pic = {}
    for r in review:
        for p in r.get('emerald_pics', [r['sapphire_pic']]): by_pic.setdefault(p, r)
    ec = gbt.easy_chat_words()
    ec['EC_WORD_CRUSH'] = 'CRUSH'          # Emerald's own word (its "events" group; pokeruby has none)
    for em_name, b2_name in (('SOFT_BOILED', 'SOFTBOILED'), ('SMOKESCREEN', 'SMOKE_SCREEN'), ('SELF_DESTRUCT', 'SELFDESTRUCT')):
        for k in ('EC_MOVE', 'EC_MOVE2'): ec[f'{k}({em_name})'] = ec[f'{k}({b2_name})']
    out_tr = []
    ow = ow_sprites()
    for i, t in enumerate(load_trainers(mon_ids)):
        pic = pics[t['facility_class']]
        r = by_pic.get(pic)
        if r is None: raise SystemExit(f'trainer {i} {t["name"]}: Emerald picture {pic} has no Black 2 class')
        name, unk = convert(t['name'], expand=True)
        assert not unk, unk
        missing = [w for w in t['before'] + t['win'] + t['lose'] if w != 'EC_EMPTY_WORD' and w not in ec]
        if missing: unknown.update(f'word {w}' for w in missing)
        speech = lambda ws: speech_text(ws, ec)
        out_tr.append(dict(index=i, name=name, facility_class=t['facility_class'], pic=pic, b2_class=r['b2_class'],
                           b2_class_name=r['name'], gfx=ow(t['facility_class'])[0], sprite=ow(t['facility_class'])[1], before=speech(t['before']), win=speech(t['win']),
                           lose=speech(t['lose']), mon_set_name=t['mon_set_name'], mon_set=t['mon_set']))
        assert len({out_sets[k]['species'] for k in t['mon_set']}) >= 3, (i, t['name'])
    tk = tucker()
    for side in tk.values():
        for m in side:
            m.update(species_id=b2(b2_species, m['species'], SPECIES_ALIAS, 'species'), item_id=b2(b2_items, m['item'], ITEM_ALIAS, 'item'),
                     nature_id=NATURES.index(m['nature']), move_ids=[b2(b2_moves, x, MOVE_ALIAS, 'move') for x in m['moves']])
            sp = info[m['species']]
            m.update(types=sp['types'], levitate=sp['ability0'] == 'LEVITATE', wonder_guard=sp['ability0'] == 'WONDER_GUARD',
                     stat_sum10=sum(sp['stats']) // 10,
                     move_types=[moves[x]['type'] if moves[x]['power'] else 255 for x in m['moves']],
                     styles=[style_of.get(x, 0) for x in m['moves']])
    if unknown: raise SystemExit(f'not in Black 2 / not found: {dict(unknown)}')
    hi = defines(os.path.join(EM, 'include', 'constants', 'battle_frontier_mons.h'), 'FRONTIER_MONS_HIGH_TIER')['FRONTIER_MONS_HIGH_TIER']
    unown = [k for k, s in enumerate(out_sets) if s['species'] == 'SPECIES_UNOWN']
    doc = ' '.join(__doc__.split('\n\n')[0].split()) + ' GENERATED by converter/gen_frontier_emerald.py.'
    data = {'_doc': doc, 'gen3_types': GEN3_TYPES, 'ev_order': EV_ORDER,
            'trainer_ranges': ranges('sFrontierTrainerIdRanges'), 'trainer_ranges_hard': ranges('sFrontierTrainerIdRangesHard'),
            'factory_ranges': fr_ranges, 'factory_fixed_iv': fixed_iv, 'factory_style_moves': style_lists,
            'factory_style_required': style_req, 'high_tier': hi, 'unown_sets': unown,
            'dome_iv_limits': [[99, 3], [119, 6], [139, 9], [159, 12], [179, 15], [199, 18], [219, 21], [299, 31]],
            'type_chart': type_chart(), 'tucker': tk, 'sets': out_sets, 'trainers': out_tr}
    text = json.dumps(data, indent=1, ensure_ascii=False)
    if check:
        old = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
        print('same' if old == text else 'DIFFERS'); return
    open(OUT, 'w', encoding='utf-8').write(text)
    print(f'{len(out_sets)} sets, {len(out_tr)} trainers, Tucker 2 x 3 -> {os.path.relpath(OUT, ROOT)}; '
          f'set lists {min(len(t["mon_set"]) for t in out_tr)}-{max(len(t["mon_set"]) for t in out_tr)}')

if __name__ == '__main__':
    main('--check' in sys.argv)
