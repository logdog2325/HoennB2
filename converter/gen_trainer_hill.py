"""Pokémon Emerald's Trainer Hill for Pokémon Emerald NDS (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md) ->
data/emerald/trainer_hill.json: the four base-game modes (Normal, Variety, Unique, Expert), each 4 floors of two trainers
(their names, classes, speeches and three Pokémon each), the floors' 16x16 layouts (metatiles, collision), the trainers'
spots, facing and sight; the prize lists and the owner's rules. b2tools/patches/trainer_hill.py writes the battle data
into the ROM; the floor rooms' builder reads the layouts and spots.

    python3 gen_trainer_hill.py            (writes data/emerald/trainer_hill.json; --check: compare only)

Source (pokeemerald, English): src/data/battle_frontier/trainer_hill.h (sChallenge_* / sFloors_*: the JP-only Default
and e-Reader sets are left out), graphics/trainer_hill/maps_<mode>/floor_<n>/{metatiles,collision}.bin, the base floor
layouts LAYOUT_TRAINER_HILL_1F..4F (rows 0-4: the stairs), src/trainer_hill.c (prize lists, GetPrizeItemId's choice of
list, the time limits), include/constants/trainer_hill.h. Names, speeches, Black 2 classes and walking sprites as
converter/gen_frontier_emerald.py does for the Frontier's trainers (Frontier facility classes)."""
import os, re, sys, json, struct, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import gen_frontier_emerald as gfe  # noqa: E402
from gen3text import convert  # noqa: E402
gbt = gfe.gbt
EM, B2 = gfe.EM, gfe.B2
OUT = os.path.join(ROOT, 'data', 'emerald', 'trainer_hill.json')
MODES = ['Normal', 'Variety', 'Unique', 'Expert']
DIRS = {'DIR_SOUTH': 1, 'DIR_NORTH': 2, 'DIR_WEST': 3, 'DIR_EAST': 4}          # pokeemerald include/constants/global.h
B2_DIR = {1: 1, 2: 0, 3: 2, 4: 3}                                              # -> Black 2 (0 up, 1 down, 2 left, 3 right)
EV_KEYS = ['hpEV', 'attackEV', 'defenseEV', 'speedEV', 'spAttackEV', 'spDefenseEV']
IV_KEYS = ['hpIV', 'attackIV', 'defenseIV', 'speedIV', 'spAttackIV', 'spDefenseIV']


# ---- a small parser for C designated initializers ---------------------------------------------------------------
def _tokens(s):
    s = re.sub(r'//[^\n]*', '', s)
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace(): i += 1; continue
        if c in '{},=[]': yield c; i += 1; continue
        if c == '.': m = re.match(r'\.(\w+)', s[i:]); yield ('.', m.group(1)); i += m.end(); continue
        j, depth = i, 0                                     # a value: up to ',' or '}' outside parentheses / quotes
        while j < n:
            if s[j] == '"':
                j = s.index('"', j + 1) + 1; continue
            if s[j] == '(': depth += 1
            elif s[j] == ')': depth -= 1
            elif depth == 0 and s[j] in ',}]=': break
            j += 1
        yield s[i:j].strip(); i = j


def parse_init(s):
    toks = list(_tokens(s))
    pos = [0]
    def value():
        t = toks[pos[0]]
        if t == '{':
            pos[0] += 1
            items, named = [], {}
            while toks[pos[0]] != '}':
                t = toks[pos[0]]
                if isinstance(t, tuple):                     # .field = value
                    pos[0] += 2; named[t[1]] = value()
                elif t == '[':                               # [index] = value
                    idx = toks[pos[0] + 1]; pos[0] += 4; named[idx] = value()
                else:
                    items.append(value())
                if toks[pos[0]] == ',': pos[0] += 1
            pos[0] += 1
            return named if named else items
        pos[0] += 1
        return t
    return value()


def gtext(s):
    """_("NAME") / __("...") -> the string (Gen 3 text, before conversion)."""
    m = re.match(r'_+\("(.*)"\)', s)
    return m.group(1).rstrip(' $') if m else s


def floors_of(text, mode):
    m = re.search(rf'static const struct TrainerHillFloor sFloors_{mode}\[\] =\s*(\{{.*?\n\}});', text, re.S)
    return parse_init(m.group(1))


def num(v):
    return {'MAX_PER_STAT_IVS': 31, 'MAX_FRIENDSHIP': 255, 'TRUE': 1, 'FALSE': 0}.get(v, None) if not re.match(r'^(0x[0-9a-fA-F]+|\d+)$', v) else int(v, 0)


def two(expr, macro):
    a, b = re.match(rf'{macro}\((\w+),\s*(\w+)\)', expr).groups()
    return a, b


def main(check=False):
    import version
    text = gfe.src('src/data/battle_frontier/trainer_hill.h')
    hill_c = gfe.src('src/trainer_hill.c')
    b2_species = gbt.defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2_moves = gbt.defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    b2_items = gbt.defines(f'{B2}/include/constants/items.h', 'ITEM_')
    unknown = collections.Counter()
    import gen_items                                        # Gen 3 TMs -> Black 2's TM of the move (or HoennB2's new TMs)
    gi_items, gi_tms, gi_names, gi_notes = gen_items.b2_items(), gen_items.tm_items(), gen_items.emerald_tm_names(), []
    def item_id(name):
        if name == 'ITEM_NONE': return 0
        n = gen_items.map_item(gi_names.get(name, name), gi_items, gi_tms, gi_notes, [0, {}])
        if n is None: unknown[f'item {name}'] += 1; return 0
        return gi_items[n]
    def b2(table, name, alias, kind):
        n = alias.get(name, name)
        if n not in table: unknown[f'{kind} {name}'] += 1; return 0
        return table[n]
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
    for k in [k for k in ec if k.startswith('EC_POKEMON')]:
        ec.setdefault('EC_POKEMON_NATIONAL(' + k.split('(', 1)[1], ec[k])
    ow = gfe.ow_sprites()
    # Gen 3 abilities by slot (CreateBattleTowerMon: abilityNum; GetAbilityBySpecies falls back to the first when the
    # second is ABILITY_NONE) -> Black 2's ability ids by name
    abil3 = {n: re.findall(r'ABILITY_(\w+)', re.search(r'\.abilities = \{(.*?)\}', b).group(1))
             for n, b in re.findall(r'\[(SPECIES_\w+)\]\s*=\s*\n\s*\{(.*?)\n    \}', gfe.src('src/data/pokemon/species_info.h'), re.S)}
    b2_abil = gbt.defines(f'{B2}/include/constants/abilities.h', 'ABILITY_')
    def ability_id(species, num):
        a = abil3[species]
        name = a[num] if num < len(a) and a[num] != 'NONE' else a[0]
        name = {'LIGHTNING_ROD': 'LIGHTNINGROD'}.get(name, name)     # (Black 2's spelling)
        if f'ABILITY_{name}' not in b2_abil: unknown[f'ability {name}'] += 1; return 0
        return b2_abil[f'ABILITY_{name}']
    # the base layouts' first five rows (the stairs), as GenerateTrainerHillFloorLayout copies them
    sys.path.insert(0, HERE)
    from gba import Repo
    repo = Repo(EM)
    margin = {}
    for f in range(4):
        g, lay = repo.layout_grid(f'LAYOUT_TRAINER_HILL_{f + 1}F')
        margin[f] = dict(metatiles=[[int(g[y, x]) & 0x3FF for x in range(16)] for y in range(5)],
                         collision=[[(int(g[y, x]) >> 10) & 3 for x in range(16)] for y in range(5)],
                         tilesets=[lay['primary_tileset'], lay['secondary_tileset']])
    modes = []
    for mi, mode in enumerate(MODES):
        floors = []
        for fi, fl in sorted(floors_of(text, mode).items(), key=lambda kv: int(kv[0])):
            fi = int(fi)
            mp = fl['map']
            d = os.path.join(EM, 'graphics', 'trainer_hill', f'maps_{mode.lower()}', f'floor_{fi}')
            mt = open(os.path.join(d, 'metatiles.bin'), 'rb').read()
            col = struct.unpack('<16H', open(os.path.join(d, 'collision.bin'), 'rb').read())
            coords = [re.match(r'COORDS_XY\((\d+),\s*(\d+)\)', c).groups() for c in mp['trainerCoords']]
            dirs = two(mp['trainerDirections'], 'TRAINER_DIRS')
            ranges = two(mp['trainerRanges'], 'TRAINER_RANGE')
            trainers = []
            for ti in range(2):
                t = fl['trainers'][str(ti)]
                cls = t['facilityClass'].replace('FACILITY_CLASS_', '')
                pic = pics[cls]
                r = by_pic.get(pic)
                if r is None: raise SystemExit(f'{mode} floor {fi} trainer {ti}: picture {pic} has no Black 2 class')
                name, unk = convert(gtext(t['name']), expand=True)
                assert not unk, unk
                speech = {}
                for k in ('speechBefore', 'speechWin', 'speechLose', 'speechAfter'):
                    ws = [w if w not in ('-1', '0xFFFF') else 'EC_EMPTY_WORD' for w in t[k]]
                    missing = [w for w in ws if w != 'EC_EMPTY_WORD' and w not in ec]
                    if missing: unknown.update(f'word {w}' for w in missing)
                    speech[k] = gfe.speech_text(ws, ec)
                mons = []
                for slot in range(3 * ti, 3 * ti + 3):          # sTrainerPartySlots: trainer 0 slots 0-2, trainer 1 3-5
                    m = t['mons'][str(slot)]
                    assert isinstance(m, dict), (mode, fi, ti, slot, m)
                    nick, unk = convert(gtext(m['nickname']), expand=True)
                    moves = re.findall(r'MOVE_\w+', ' '.join(m['moves']))
                    item = m.get('heldItem', 'ITEM_NONE')
                    mons.append(dict(
                        species=m['species'], species_id=b2(b2_species, m['species'], gfe.SPECIES_ALIAS, 'species'),
                        item=item, item_id=item_id(item),
                        moves=moves, move_ids=[b2(b2_moves, x, gfe.MOVE_ALIAS, 'move') for x in moves],
                        evs=[num(m.get(k, '0')) for k in EV_KEYS], ivs=[num(m.get(k, '0')) for k in IV_KEYS],
                        ability=num(m.get('abilityNum', '0')), personality=num(m.get('personality', '0')),
                        ability_id=ability_id(m['species'], num(m.get('abilityNum', '0'))),
                        nature_id=num(m.get('personality', '0')) % 25,      # (Gen 3: the personality's nature)
                        nickname=nick, friendship=num(m.get('friendship', '0'))))
                x, y = int(coords[ti][0]), int(coords[ti][1])
                gfx, sprite = ow(cls)
                trainers.append(dict(name=name, facility_class=cls, pic=pic, b2_class=r['b2_class'], b2_class_name=r['name'],
                                     gfx=gfx, sprite=sprite, x=x, y=y + 5,     # (the floor's 16x16 part starts at row 5)
                                     dir=DIRS[dirs[ti]], b2_dir=B2_DIR[DIRS[dirs[ti]]], range=int(ranges[ti]),
                                     before=speech['speechBefore'], win=speech['speechWin'], lose=speech['speechLose'],
                                     after=speech['speechAfter'], mons=mons))
            grid = [[mt[16 * y + x] for x in range(16)] for y in range(16)]
            solid = [[(col[y] >> (15 - x)) & 1 for x in range(16)] for y in range(16)]
            floors.append(dict(floor=fi + 1, trainer_nums=[int(fl['trainerNum1']), int(fl['trainerNum2'])],
                               trainers=trainers, metatiles=margin[fi]['metatiles'] + [[v + 512 for v in row] for row in grid],
                               collision=margin[fi]['collision'] + solid))
        assert len(floors) == 4, (mode, len(floors))
        modes.append(dict(mode=mi, name=mode, floors=floors))
    # prizes (GetPrizeItemId): the list set by the sum of the trainer numbers / 256 % 2, the list by their xor % 10 (game
    # clear: always, the Hill opens after the Hall of Fame), Expert + 1; the prize by the minutes
    lists = {}
    for name, body in re.findall(r'static const u16 (sPrizeList\w+)\[\]\s*=\s*\{(.*?)\};', hill_c, re.S):
        lists[name] = re.findall(r'ITEM_\w+', body)
    sets = [re.findall(r'sPrizeList\w+', re.search(rf'sPrizeLists{k}\[[^\]]*\] =\s*\{{(.*?)\}};', hill_c, re.S).group(1)) for k in (1, 2)]
    for m in modes:
        nums = [n for f in m['floors'] for n in f['trainer_nums']]
        set_id = (sum(nums) // 256) % 2
        x = 0
        for n in nums: x ^= n & 0x1F
        li = x % 10
        if m['name'] == 'Expert': li = (li + 1) % 10
        prize = lists[sets[set_id][li]]
        m['prizes'] = prize
        m['prize_ids'] = [item_id(p) for p in prize]
        m['prize_list'] = sets[set_id][li]
    # the Entrance clerk's two Mart lists (TrainerHill_Entrance_Pokemart_Basic / _Expanded: FLAG_SYS_GAME_CLEAR)
    ent = open(os.path.join(EM, 'data', 'maps', 'TrainerHill_Entrance', 'scripts.inc'), encoding='utf-8').read()
    marts = {}
    for k in ('Basic', 'Expanded'):
        body = re.search(rf'TrainerHill_Entrance_Pokemart_{k}:\s*\n(.*?)pokemartlistend', ent, re.S).group(1)
        names = re.findall(r'ITEM_\w+', body)
        marts[k.lower()] = dict(items=names, ids=[item_id(n) for n in names])
    if unknown: raise SystemExit(f'not in Black 2 / not found: {dict(unknown)}')
    doc = ' '.join(__doc__.split('\n\n')[0].split()) + ' GENERATED by converter/gen_trainer_hill.py.'
    data = {'_doc': doc, 'max_time': 215999, 'prize_minutes': [12, 13, 14, 16, 18],
            'tilesets': margin[0]['tilesets'], 'marts': marts, 'modes': modes}
    out = json.dumps(data, indent=1, ensure_ascii=False)
    if check:
        old = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
        print('same' if old == out else 'DIFFERS'); return
    open(OUT, 'w', encoding='utf-8').write(out)
    print(f"{os.path.relpath(OUT, ROOT)}: " + '; '.join(
        f"{m['name']}: " + ', '.join(f"{f['floor']}F {f['trainers'][0]['name']} & {f['trainers'][1]['name']}" for f in m['floors'])
        + f" (prize {m['prizes'][0]})" for m in modes))


if __name__ == '__main__':
    main('--check' in sys.argv)
