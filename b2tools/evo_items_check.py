"""Static sweep of the evolutions (evo_items, 2026-11-01): for each version, every item an evolution method of Black 2's
table a/0/1/9 needs (as our build has it: data/trade_evos.json over Black 2's) and where the player can get it, and every
evolution that can't happen for another reason. No ROM needed: it reads the data and scripts the build is made from.

    python3 b2tools/evo_items_check.py              [--verbose]
    python3 b2tools/evo_items_check.py --shop DIR   only check the built shop files of a files/ tree (a/2/8/2, a/2/8/3)

Exit code 1 if a needed item has no source in a version (or the shop files are wrong).

Sources, per version:
- ball, hidden: data/hoenn_items.json, data/hoenn_hidden_items.json (Emerald: its overlays, minus their sapphire_only);
- mart: data/hoenn_shops.json (with Emerald's overlay and "extra" marts), Trainer Hill's marts, data/trade_evos.json's list;
- bp: Black 2's own BP clerks in the PWT lobby (ov036 BP_SHOP_ITEMS_NORMAL / _TMS, src/field_scripts/0384_pwt_lobby.s;
  the PWT's door is on the Battle Tower island, data/hoenn_map_additions.json), the Exchange Service Corner's (Emerald);
- script: a script that gives the item (src/field_scripts, version overlays; lines that only name it are listed apart);
- prize: Battle Tent and Trainer Hill prize lists (Emerald), the Battle Tower's (script VAR_BT_PRIZE, counted as script);
- wild: a species in the version's wild tables (src/encounters, overlays) holding it (personal a/0/1/6 +0xC, +0xE, +0x10);
- trade: an in-game trade's held item (b2tools/patches/trades.py's tables; none holds an evolution item).
Not counted: trainers' held items, the Battle Pyramid's items (they stay in the Pyramid), Pickup."""
import os, re, sys, glob, json, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import narcio
from b2files import arc_path

BASE_FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
INC = os.path.join(ROOT, 'external', 'pokebw2', 'include', 'constants')
VERSIONS = ('sapphire', 'ruby', 'emerald')
GIVE = re.compile(r'\b(h_giveitem|ItemAdd|WorkSetConst\s+VAR_BT_PRIZE|h_give\w*|giveitem)\b')


def defines(name, prefix):
    return {m.group(1): int(m.group(2)) for m in re.finditer(r'^#define (' + prefix + r'\w+)\s+(\d+)\b',
                                                             open(os.path.join(INC, name)).read(), re.M)}


ITEMS, SPECIES, METHODS = defines('items.h', 'ITEM_'), defines('species.h', 'SPECIES_'), defines('pokemon.h', 'EVO_METHOD_')
ITEM_NAME = {}
for k, v in ITEMS.items(): ITEM_NAME.setdefault(v, k)
SP_NAME = {}
for k, v in SPECIES.items(): SP_NAME.setdefault(v, k)
METHOD_NAME = {v: k[len('EVO_METHOD_'):] for k, v in METHODS.items()}
ITEM_METHODS = {METHODS[k] for k in ('EVO_METHOD_ITEM', 'EVO_METHOD_ITEM_MALE', 'EVO_METHOD_ITEM_FEMALE',
                                     'EVO_METHOD_HELD_ITEM_DAY', 'EVO_METHOD_HELD_ITEM_NIGHT')}
TRADE_METHODS = {METHODS[k] for k in ('EVO_METHOD_TRADE', 'EVO_METHOD_TRADE_WITH_ITEM', 'EVO_METHOD_TRADE_WITH_SPECIES')}


def entries_of(rec):
    return [e for e in (struct.unpack_from('<3H', rec, 6 * k) for k in range(len(rec) // 6)) if any(e)]


def evolution_table():
    """{species: [(method, param, target)]}: Black 2's table with data/trade_evos.json's lists, as patches/trade_evos.py
    writes it (nothing else writes a/0/1/9)."""
    d = json.load(open(os.path.join(ROOT, 'data', 'trade_evos.json')))
    C = dict(ITEMS, **SPECIES, **METHODS)
    val = lambda v: v if isinstance(v, int) else C[v]
    evo = {i: entries_of(rec) for i, rec in enumerate(narcio.load(BASE_FILES, 19))}
    for sp, lst in d['evolutions'].items():
        i = C[sp]
        keep = [e for e in evo[i] if e[0] in TRADE_METHODS] if d.get('keep_trade_methods') else []
        evo[i] = [tuple(val(v) for v in e) for e in lst] + keep
    return evo


def data_json(name, ver):
    """(entries dict, key) of a per-version items file; Emerald's overlay replaces Sapphire's list minus sapphire_only."""
    base = json.load(open(os.path.join(ROOT, 'data', name)))
    key = 'balls' if 'balls' in base else 'items'
    out = dict(base[key])
    if ver == 'emerald':
        over = json.load(open(os.path.join(ROOT, 'data', 'emerald', name)))
        out.update(over[key])
        for k in over.get('sapphire_only', []) + over.get('unused_scripts', []): out.pop(k, None)
    return out


def overlay_files(d, pattern, ver):
    """The version's files of a folder with <version>/ overlays (as version.overlay), by the four-digit file number."""
    out = {}
    for p in sorted(glob.glob(os.path.join(d, pattern))): out[os.path.basename(p)[:4]] = p
    if ver != 'sapphire':
        for p in sorted(glob.glob(os.path.join(d, ver, pattern))): out[os.path.basename(p)[:4]] = p
    return out


def script_mentions(ver):
    """{item name: [(file, line no, line)]} of every line naming an item in the version's field scripts. Shared scene files
    can hold a version's own blocks: `--verbose` lists the lines, for items whose only source is a script."""
    d = os.path.join(ROOT, 'src', 'field_scripts')
    files = list(overlay_files(d, '*.s', ver).values())
    for sub in ('scenes', 'common', 'centers'):
        files += sorted(glob.glob(os.path.join(d, sub, '*.inc'))) + sorted(glob.glob(os.path.join(d, sub, '*.s')))
        if ver != 'sapphire':
            files += sorted(glob.glob(os.path.join(d, sub, ver, '*.inc'))) + sorted(glob.glob(os.path.join(d, ver, sub, '*.inc')))
    out = {}
    for p in files:
        if 'test' in os.path.basename(p): continue      # test-only scenes (ch7_test.inc ...) are not in a release
        text = open(p, encoding='utf-8', errors='replace').read()
        for n, line in enumerate(text.splitlines(), 1):
            code = line.split('//', 1)[0]
            for m in re.finditer(r'\bITEM_[A-Z0-9_]+\b', code):
                out.setdefault(m.group(0), []).append((os.path.relpath(p, ROOT), n, code.strip()))
    return out


def wild_species(ver):
    """Species in the wild tables a Hoenn map of the version uses."""
    maps = json.load(open(os.path.join(ROOT, 'data', 'hoenn_encounters.json')))
    used = {v for k, v in maps.items() if isinstance(v, int)}
    if ver == 'emerald':
        over = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_encounters.json')))
        used |= {v for k, v in over.items() if isinstance(v, int)}
    files = overlay_files(os.path.join(ROOT, 'src', 'encounters'), '*.s', ver)
    out = {}
    for num, p in files.items():
        if int(num) not in used: continue
        for sp in re.findall(r'\bSPECIES_[A-Z0-9_]+\b', open(p).read()):
            out.setdefault(sp, set()).add(os.path.basename(p)[5:-2])
    for sp in rock_smash_species(ver): out.setdefault(sp, set()).add('Rock Smash')
    return out


def rock_smash_species(ver):
    """Rock Smash's wild Pokémon (patches/hm_free.py rock_smash_wild_asm reads the decomp's tables, not src/encounters)."""
    repo = 'pokeemerald' if ver == 'emerald' else 'pokeruby'
    wild = json.load(open(os.path.join(ROOT, 'external', repo, 'src', 'data', 'wild_encounters.json')))
    suffix = '' if ver == 'emerald' else '_' + ver.capitalize()
    return {m['species'] for g in wild['wild_encounter_groups'] for e in g['encounters']
            if 'rock_smash_mons' in e and e['base_label'].endswith(suffix) for m in e['rock_smash_mons']['mons']}


def wild_held():
    """{item id: [(species id, slot)]}; slot 0 = 50%, 1 = 5%, 2 = 1%."""
    out = {}
    for i, rec in enumerate(narcio.load(BASE_FILES, 16)[:650]):
        if len(rec) < 0x12: continue
        for slot, off in enumerate((0xC, 0xE, 0x10)):
            it = struct.unpack_from('<H', rec, off)[0]
            if it: out.setdefault(it, []).append((i, slot))
    return out


def bp_lists():
    """Black 2's own BP clerks (scrcmd_shop.c): the PWT lobby's. {item name: BP}."""
    src = open(os.path.join(ROOT, 'external', 'pokebw2_new', 'src', 'ov036', 'scrcmd_shop.c')).read()
    out = {}
    for name in ('BP_SHOP_ITEMS_NORMAL', 'BP_SHOP_ITEMS_TMS'):
        blk = src.split(f'static const ShopItem {name}[] = {{', 1)[1].split('};', 1)[0]
        for it, price in re.findall(r'\{\s*(ITEM_\w+),\s*(\d+)\s*\}', blk):
            out[it] = int(price)
    return out


def exchange_corner():
    """The Exchange Service Corner's lists (Emerald), as patches/frontier_core.py reads them."""
    d = os.path.join(ROOT, 'external', 'pokeemerald', 'data', 'maps', 'BattleFrontier_ExchangeServiceCorner', 'scripts.inc')
    return set(re.findall(r'\bITEM_[A-Z0-9_]+\b', open(d).read())) if os.path.exists(d) else set()


def prize_lists(ver):
    """{item name: where} of the Emerald facilities' prize lists that leave the facility."""
    out = {}
    if ver != 'emerald': return out
    tents = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'battle_tents.json')))['tents']
    for name, t in tents.items():
        for it in t['prizes']: out.setdefault(it, f'{name} tent prize')
    hill = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'trainer_hill.json')))
    for m in hill['modes']:
        for it in m['prizes']: out.setdefault(it, f'Trainer Hill {m["name"]} prize')
    return out


def shop_lists(ver):
    """{item name: [where]} of the Marts of the version, data/trade_evos.json's list apart."""
    base = json.load(open(os.path.join(ROOT, 'data', 'hoenn_shops.json')))['shops']
    out = {}
    lists = {k: v for k, v in base.items()}
    if ver == 'emerald':
        over = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_shops.json')))
        lists.update(over['shops'])
        lists.update({k: dict(v, label=v['emerald_label']) for k, v in over['extra'].items()})
        hill = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'trainer_hill.json')))['marts']
        for key, m in hill.items():
            for it in m['items']: out.setdefault(it, []).append(f'Trainer Hill mart {key}')
    for k, s in lists.items():
        for it in s['items']: out.setdefault(it, []).append(f'shop {k} {s["label"]}')
    for f, ids in enumerate(narcio.load(BASE_FILES, 282)[:6]):       # the standard clerk's badge lists
        for it in struct.unpack(f'<{len(ids) // 2}H', ids): out.setdefault(ITEM_NAME[it], []).append(f'badge list {f}')
    return out


def trades(ver):
    """The version's in-game trades as patches/trades.py has them: {species offered (name): held item id}."""
    src = open(os.path.join(HERE, 'patches', 'trades.py')).read()
    blk = src.split('EMERALD_TRADES = {' if ver == 'emerald' else 'SAPPHIRE_TRADES = {', 1)[1].split('\n}', 1)[0]
    held = {k: v for k, v in ITEMS.items()}
    out = {}
    for m in re.finditer(r'species=(SPECIES_\w+).*?item=(\w+)', blk, re.S):
        out[m.group(1)] = 0 if m.group(2) == '0' else held.get(m.group(2), -1)
    return out


def reachable(ver, wild, evo):
    """Species the player can own without link trades: wild, gifts/statics/starters named by the scripts, in-game trades
    and everything their evolution families give (evolving forward, breeding back to the family's first stage)."""
    scripts = overlay_files(os.path.join(ROOT, 'src', 'field_scripts'), '*.s', ver)
    start = set(wild)
    start |= set(trades(ver))
    gift = re.compile(r'\b(PokePartyAdd\w*|\w*Wild\w*|\w*Egg\w*|\w*_battle|WorkSetConst DVF_SPECIES)\b[^\n]*?\b(SPECIES_[A-Z0-9_]+)')
    for p in list(scripts.values()) + glob.glob(os.path.join(ROOT, 'src', 'field_scripts', 'scenes', '*.inc')):
        if 'test' in os.path.basename(p): continue
        for m in gift.finditer(open(p, encoding='utf-8', errors='replace').read()):
            start.add(m.group(2))
    ids = {SPECIES[s] for s in start if s in SPECIES}
    parent = {}
    for sp, lst in evo.items():
        for m, _, t in lst:
            if t: parent.setdefault(t, sp)
    changed = True
    while changed:
        changed = False
        for sp in list(ids):
            for m, _, t in evo.get(sp, []):
                if t and t not in ids: ids.add(t); changed = True
            if sp in parent and parent[sp] not in ids: ids.add(parent[sp]); changed = True
    return ids


def check_shop(files, base=BASE_FILES):
    """The built shop files (files/a/2/8/2, a/2/8/3) of a version: the Lilycove 3F right clerk's list (shop id 15, list file
    21) and its Fairy twin (list file 79) with every item of data/trade_evos.json; every count right; 45 entries at most
    (ShopUIWork.entries[45], ov036 scrcmd_shop.c); the sold items' prices. Returns the errors."""
    shop = json.load(open(os.path.join(ROOT, 'data', 'trade_evos.json')))['shop']
    lists, counts = narcio.load(files, 282), narcio.load(files, 283)
    prices = {i: struct.unpack_from('<H', rec, 0)[0] * 10 for i, rec in enumerate(narcio.load(base, 24))}   # ITEM_PARAM_PRICE
    sapphire = json.load(open(os.path.join(ROOT, 'data', 'hoenn_shops.json')))['shops'][str(shop['id'])]['ids']
    want = sapphire + [ITEMS[x] for x in shop['add']]
    errors = []
    for f, ids in enumerate(lists):
        if f >= 6 and counts[0][f] != len(ids) // 2:
            errors.append(f'list file {f}: count {counts[0][f]}, {len(ids) // 2} items in the file')
    for f, tail, what in ((shop['id'] + 6, [], 'Lilycove 3F right clerk'), (79, None, 'the same with the Fairy type on')):
        got = list(struct.unpack(f'<{len(lists[f]) // 2}H', lists[f]))
        if tail is None: got, extra = got[:len(want)], got[len(want):]
        if got != want: errors.append(f'list file {f}: {got}, wanted {want}')
        if counts[0][f] > 45: errors.append(f'list file {f}: {counts[0][f]} items, over the shop screen\'s 45')
        print(f'  list file {f} ({what}): {counts[0][f]} items, shop screen maximum 45, 7 rows shown (scrolls)')
    for x in shop['add']:
        print(f'    {x[5:]:14} {prices[ITEMS[x]]:6} P')
        if not prices[ITEMS[x]]: errors.append(f'{x}: no price')
    print(f'  a/2/8/2: {os.path.getsize(arc_path(files, 282))} bytes, {len(lists)} files')
    return errors


def main():
    args = sys.argv[1:]
    verbose = '--verbose' in args
    if '--shop' in args:
        errors = check_shop(args[args.index('--shop') + 1])
        for e in errors: print('BAD', e)
        print('shop files OK' if not errors else f'{len(errors)} errors')
        return 1 if errors else 0
    evo = evolution_table()
    need = {}
    for sp, lst in evo.items():
        for m, p, t in lst:
            if m in ITEM_METHODS and p:
                need.setdefault(p, []).append((sp, m, t))
    held = wild_held()
    bp = bp_lists()
    fail = False
    gives = {}
    for ver in VERSIONS:
        balls = data_json('hoenn_items.json', ver)
        hidden = data_json('hoenn_hidden_items.json', ver)
        shops = shop_lists(ver)
        wild = wild_species(ver)
        scr = script_mentions(ver)
        prizes = prize_lists(ver)
        add = set(json.load(open(os.path.join(ROOT, 'data', 'trade_evos.json')))['shop']['add'])
        exch = exchange_corner() if ver == 'emerald' else set()
        reach = reachable(ver, wild, evo)
        print(f'==== {ver}: {len(wild)} wild species, {len(reach)} species reachable without link trades')
        missing = []
        for it in sorted(need, key=lambda i: ITEM_NAME[i]):
            name = ITEM_NAME[it]
            src = []
            src += [f'ball {k}' for k, b in balls.items() if b['item'] == name]
            src += [f'hidden {b.get("map")} {b.get("at")}' for k, b in hidden.items() if b['item'] == name]
            src += [f'mart {w}' for w in shops.get(name, [])]
            if name in add: src.append('Lilycove 3F (trade_evos shop list)')
            given = [x for x in scr.get(name, []) if GIVE.search(x[2])]
            src += [f'script {f}:{n}' for f, n, _ in given]
            if name in prizes: src.append(prizes[name])
            if name in exch: src.append('Exchange Service Corner (BP)')
            if name in bp: src.append(f'PWT BP clerk ({bp[name]} BP)')
            wild_src = [(SP_NAME[s], slot) for s, slot in held.get(it, []) if SP_NAME.get(s) in wild]
            src += [f'wild {s} holds it ({("50%", "5%", "1%")[slot]})' for s, slot in wild_src]
            src += [f'in-game trade {sp}' for sp, h in trades(ver).items() if h == it]
            users = ', '.join(f'{SP_NAME[s][8:]}->{SP_NAME[t][8:]}{"" if s in reach else " (not reachable)"}' for s, _, t in need[it])
            real = [x for x in src if not x.startswith('PWT')]
            tag = 'MISSING' if not src else ('only BP' if not real else 'ok')
            if not src: missing.append(name); fail = True
            print(f'  {tag:8} {name[5:]:16} for {users}')
            if verbose or tag != 'ok':
                for x in src[:8]: print(f'             {x}')
                other = [x for x in scr.get(name, []) if not GIVE.search(x[2])]
                for f, n, line in other[:6]: print(f'             (names it: {f}:{n}: {line})')
            elif src:
                print(f'             {src[0]}' + (f' (+{len(src) - 1} more)' if len(src) > 1 else ''))
        print(f'  missing in {ver}: {[m[5:] for m in missing]}')
        gives[ver] = missing
        print(f'  other evolutions in {ver}:')
        for sp, lst in sorted(evo.items()):
            for m, p, t in lst:
                if m in TRADE_METHODS: continue
                if SP_NAME.get(sp) is None: continue
                nm = METHOD_NAME.get(m, m)
                if nm in ('SPECIES_IN_PARTY', 'KNOWS_MOVE', 'BEAUTY', 'LEVEL_MAGNETIC_FIELD', 'LEVEL_MOSS_ROCK', 'LEVEL_ICE_ROCK', 'SHEDINJA'):
                    extra = ''
                    if nm == 'SPECIES_IN_PARTY': extra = f' needs {SP_NAME.get(p, p)}{"" if p in reach else " (not reachable)"}'
                    print(f'    {nm:22} {SP_NAME[sp][8:]}->{SP_NAME.get(t, t)}{extra}{"" if sp in reach else " [not reachable]"}')
        no = sorted(SP_NAME[s][8:] for s, lst in evo.items() if lst and s not in reach and s in SP_NAME and s < 650
                    and any(m in ITEM_METHODS for m, _, _ in lst))
        print(f'  evolvers by item that are not reachable without link trades in {ver}: {no}')
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
