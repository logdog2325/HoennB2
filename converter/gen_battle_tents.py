"""Pokémon Emerald's three Battle Tents for Pokémon Emerald NDS (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md) ->
data/emerald/battle_tents.json. b2tools/patches/frontier_factory_dome.py writes it into Black 2's Battle Subway set
archive (arc 211, the 'TENT' file after the Factory/Dome engine) and the Palace/Arena and Factory engines read it there.

    python3 gen_battle_tents.py            (writes data/emerald/battle_tents.json; --check: compare only)

Source (pokeemerald, English):
  src/data/battle_frontier/battle_tent.h    gSlateportBattleTentMons (70 sets), gVerdanturfBattleTentMons (45),
                                             gFallarborBattleTentMons (45): species, 4 moves, held item index, EV spread
                                             flags, nature; the three tents' 30 trainers each (facility class, name, the
                                             three easy-chat speeches, their set list)
  include/constants/battle_tent.h           TENT_MIN_LEVEL (30), TENT_STAGES_PER_CHALLENGE (3)
  src/battle_tent.c                          the prizes (sVerdanturfTentRewards, sFallarborTentRewards,
                                             sSlateportTentRewards)
Everything else (Black 2 names, held item table, trainer pictures and classes, walking sprites, the speeches' wording) is
converter/gen_frontier_emerald.py's, so a tent trainer looks and speaks as a Frontier trainer of the same class."""
import os, re, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import gen_frontier_emerald as gfe  # noqa: E402
from gen3text import convert  # noqa: E402
gbt = gfe.gbt

EM, B2 = gfe.EM, gfe.B2
OUT = os.path.join(ROOT, 'data', 'emerald', 'battle_tents.json')
# tent -> (pokeemerald prefix, Frontier facility whose rules it uses, the reward table in battle_tent.c)
TENTS = {'verdanturf': ('Verdanturf', 'PALACE', 'sVerdanturfTentRewards'),
         'fallarbor': ('Fallarbor', 'ARENA', 'sFallarborTentRewards'),
         'slateport': ('Slateport', 'FACTORY', 'sSlateportTentRewards')}
FACILITY = {'PALACE': 2, 'ARENA': 3, 'FACTORY': 4}


def load_sets(prefix, text, ids):
    body = gfe.block(text, f'g{prefix}BattleTentMons')
    out = []
    for name, b in re.findall(r'\[(\w+_TENT_MON_\w+)\]\s*=\s*\{(.*?)\n    \}', body, re.S):
        out.append(dict(id_name=name,
                        species=re.search(r'\.species = (SPECIES_\w+)', b).group(1),
                        moves=re.findall(r'(MOVE_\w+)', re.search(r'\.moves = \{(.*?)\}', b, re.S).group(1)),
                        item_index=re.search(r'\.itemTableId = (BATTLE_FRONTIER_ITEM_\w+)', b).group(1),
                        ev=sorted(set(re.findall(r'F_EV_SPREAD_(\w+)', re.search(r'\.evSpread = ([^\n]*)', b).group(1))),
                                  key=gfe.EV_ORDER.index),
                        nature=re.search(r'\.nature = (NATURE_\w+)', b).group(1)))
    assert [ids[s['id_name']] for s in out] == list(range(len(out))), prefix
    return out


def words(s):
    """The six speech words in order; Emerald's -1 (EC_EMPTY_WORD, 0xFFFF) keeps its place."""
    return ['EC_EMPTY_WORD' if w == '-1' else w
            for w in re.findall(r'EC_WORD_\w+|EC_EMPTY_WORD|EC_POKEMON(?:2|_NATIONAL)?\(\w+\)|EC_MOVE2?\(\w+\)|-1\b', s)]


def load_trainers(prefix, text, ids):
    lists = {name: [ids[m] for m in re.findall(r'\w+_TENT_MON_\w+', body)]
             for name, body in re.findall(rf'const u16 (g{prefix}BattleTentTrainerMons_\w+)\[\]\s*=\s*\{{(.*?)\}};', text, re.S)}
    body = gfe.block(text, f'g{prefix}BattleTentTrainers')
    out = []
    for cls, name, before, win, lose, mset in re.findall(
            r'\.facilityClass = FACILITY_CLASS_(\w+),\s*\.trainerName = _\("(.*?)"\),\s*\.speechBefore = \{(.*?)\},\s*'
            r'\.speechWin = \{(.*?)\},\s*\.speechLose = \{(.*?)\},\s*\.monSet = (\w+)', body, re.S):
        out.append(dict(facility_class=cls, name=name, before=words(before), win=words(win), lose=words(lose),
                        mon_set_name=mset, mon_set=lists[mset]))
    for t in out: assert len(t['before']) == len(t['win']) == len(t['lose']) == 6, t
    return out


def main(check=False):
    import version
    text = gfe.src('src/data/battle_frontier/battle_tent.h')
    ids = gfe.defines(os.path.join(EM, 'include', 'constants', 'battle_tent_mons.h'), '')
    consts = gfe.defines(os.path.join(EM, 'include', 'constants', 'battle_tent.h'), 'TENT_')
    n_tr = gfe.defines(os.path.join(EM, 'include', 'constants', 'battle_tent_trainers.h'), 'NUM_BATTLE_TENT_TRAINERS')['NUM_BATTLE_TENT_TRAINERS']
    tent_c = gfe.src('src/battle_tent.c')
    b2_species = gbt.defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2_moves = gbt.defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    b2_items = gbt.defines(f'{B2}/include/constants/items.h', 'ITEM_')
    unknown = collections.Counter()
    def b2(table, name, alias, kind):
        n = alias.get(name, name)
        if n not in table: unknown[f'{kind} {name}'] += 1; return 0
        return table[n]
    items = gfe.held_items()
    pics = dict(re.findall(r'\[FACILITY_CLASS_(\w+)\] = TRAINER_PIC_(\w+)',
                           gfe.block(gfe.src('src/data/pokemon/trainer_class_lookups.h'), 'gFacilityClassToPicIndex')))
    review = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json'))['review']
    by_pic = {}
    for r in review:
        for p in r.get('emerald_pics', [r['sapphire_pic']]): by_pic.setdefault(p, r)
    ec = gbt.easy_chat_words()
    ec['EC_WORD_CRUSH'] = 'CRUSH'
    for em_name, b2_name in (('SOFT_BOILED', 'SOFTBOILED'), ('SMOKESCREEN', 'SMOKE_SCREEN'), ('SELF_DESTRUCT', 'SELFDESTRUCT')):
        for k in ('EC_MOVE', 'EC_MOVE2'): ec[f'{k}({em_name})'] = ec[f'{k}({b2_name})']
    for k in [k for k in ec if k.startswith('EC_POKEMON')]:     # EC_POKEMON_NATIONAL(X): the species' name, as the others
        ec.setdefault('EC_POKEMON_NATIONAL(' + k.split('(', 1)[1], ec[k])
    ow = gfe.ow_sprites()
    tents = {}
    for key, (prefix, fac, rewards) in TENTS.items():
        sets = load_sets(prefix, text, ids)
        out_sets = []
        for s in sets:
            item = items[s['item_index']]
            out_sets.append(dict(
                species=s['species'], species_id=b2(b2_species, s['species'], gfe.SPECIES_ALIAS, 'species'),
                moves=s['moves'], move_ids=[b2(b2_moves, m, gfe.MOVE_ALIAS, 'move') for m in s['moves']],
                item=item, item_id=b2(b2_items, item, gfe.ITEM_ALIAS, 'item') if item != 'ITEM_NONE' else 0,
                ev=s['ev'], nature=s['nature'], nature_id=gfe.NATURES.index(s['nature'])))
        out_tr = []
        for i, t in enumerate(load_trainers(prefix, text, ids)):
            pic = pics[t['facility_class']]
            r = by_pic.get(pic)
            if r is None: raise SystemExit(f'{key} trainer {i} {t["name"]}: Emerald picture {pic} has no Black 2 class')
            name, unk = convert(t['name'], expand=True)
            assert not unk, unk
            missing = [w for w in t['before'] + t['win'] + t['lose'] if w != 'EC_EMPTY_WORD' and w not in ec]
            if missing: unknown.update(f'word {w}' for w in missing)
            speech = lambda ws: gfe.speech_text(ws, ec)
            gfx, sprite = ow(t['facility_class'])
            out_tr.append(dict(index=i, name=name, facility_class=t['facility_class'], pic=pic, b2_class=r['b2_class'],
                               b2_class_name=r['name'], gfx=gfx, sprite=sprite, before=speech(t['before']),
                               win=speech(t['win']), lose=speech(t['lose']), mon_set_name=t['mon_set_name'],
                               mon_set=t['mon_set']))
        assert len(out_tr) == n_tr, (key, len(out_tr))
        prize = re.findall(r'ITEM_\w+', re.search(rf'{rewards}\[\]\s*=\s*\{{(.*?)\}};', tent_c, re.S).group(1))
        tents[key] = dict(emerald=prefix, rules=fac, facility=FACILITY[fac], prizes=prize,
                          prize_ids=[b2(b2_items, p, gfe.ITEM_ALIAS, 'item') for p in prize],
                          sets=out_sets, trainers=out_tr)
    if unknown: raise SystemExit(f'not in Black 2 / not found: {dict(unknown)}')
    doc = ' '.join(__doc__.split('\n\n')[0].split()) + ' GENERATED by converter/gen_battle_tents.py.'
    data = {'_doc': doc, 'min_level': consts['TENT_MIN_LEVEL'], 'stages': consts['TENT_STAGES_PER_CHALLENGE'],
            'tents': tents}
    out = json.dumps(data, indent=1, ensure_ascii=False)
    if check:
        old = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
        print('same' if old == out else 'DIFFERS'); return
    open(OUT, 'w', encoding='utf-8').write(out)
    print(f"{os.path.relpath(OUT, ROOT)}: " + ', '.join(f"{k} {len(v['sets'])} sets / {len(v['trainers'])} trainers / prize "
                                                      f"{v['prizes']}" for k, v in tents.items())
          + f"; min level {data['min_level']}, {data['stages']} battles")


if __name__ == '__main__':
    main('--check' in sys.argv)
