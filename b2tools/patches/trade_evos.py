"""Trade evolutions made in-game (trade_evos agent, 2026-10-07): data/trade_evos.json into Black 2's evolution table, item
data and one Hoenn shop list. Data only (no code); every archive keeps its size, so the ROM layout and the savestates
are unchanged. Must run after `shops` (it appends to a list that patch writes).

How Black 2 evolves (read in its code, arm9 CheckEvolveSpecies 0x02020788, b2tools/armdis.py; constants in the decomp's
include/constants/pokemon.h, which match the code):
- Evolution table a/0/1/9: one 42-byte file per species record, 7 x {u16 method, u16 param, u16 species}.
- CheckEvolveSpecies(party, pkm, mode, arg, ...) switches on mode:
  0 level-up (after a battle, Rare Candy): methods 1-4, 9-16, 19-28 (EVO_METHOD_LEVEL 4: level >= param;
    EVO_METHOD_SPECIES_IN_PARTY 22: CheckSpeciesInParty(party, param), no level needed; Mantyke uses it);
  1 trade (ov033 fld_trade.c): only EVO_METHOD_TRADE 5, TRADE_WITH_ITEM 6 (held item == param), TRADE_WITH_SPECIES 7
    (Karrablast 588 / Shelmet 616 hard-coded, param 0);
  2/3 an item used from the Bag (party screen / event_field_proclink.c script_evo): EVO_METHOD_ITEM 8 (item == param),
    ITEM_MALE 17, ITEM_FEMALE 18.
  So a trade-with-item evolution becomes EVO_METHOD_ITEM with the same item: used from the Bag like a stone.
- An Everstone (hold effect 64) stops every mode but 3 (Kadabra excepted, as in Black 2).

How the Bag makes a stone usable (ov142 func_ov142_0219a4d0, the Bag's Use; item params from PML_ItemGetParam
0x02026820 and PML_ItemGetBattleStat 0x020268d4; notes/RESEARCH_EXPSHARE_HM.md for the record layout):
- item data a/0/2/4, 36 bytes per item: +0xA field use (param 6: non-zero adds "Use" to the Bag's item menu),
  +0xC party use (param 14: 1 = the bytes from +0x10 are party-use flags), +0x11 bit 3 = param 29 "evolve".
- Use: GetItemParam(item, 29) == 1 -> Bag result 12 -> party screen mode 16 (the evolution-item screen, as stones),
  then script_evo -> CheckEvolveSpecies mode 3 with the item -> the evolution scene.
- Every evolution stone (Fire/Water/Thunder/Leaf/Moon/Sun/Shiny/Dusk/Dawn, Oval Stone) has +0xA = 20, +0xC = 1,
  +0x11 = 0x08 and +8 bit 5 = 0 (Give/Toss allowed). The trade items have 0/0/0 and the same +8, so they get the
  stones' three values and stay holdable (hold effect +2/+3, Fling +5/+6, pocket and sort bytes unchanged).

Shop (a/2/8/2 list file id + 6, its count in a/2/8/3 file 0; b2tools/shops_data.py): the items Hoenn has no other
source for are appended to data/trade_evos.json's shop list. a/2/8/2 keeps its original 1300 bytes (shops.py)."""
import os, re, sys, json, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
VANILLA = os.path.join(DECOMP, 'build', 'b2_us', 'files')
ARC_EVO, ARC_ITEM, ARC_SHOP, ARC_SHOP_COUNT = 19, 24, 282, 283
STONES = ('ITEM_FIRE_STONE', 'ITEM_WATER_STONE', 'ITEM_THUNDERSTONE', 'ITEM_LEAF_STONE', 'ITEM_MOON_STONE',
          'ITEM_SUN_STONE', 'ITEM_SHINY_STONE', 'ITEM_DUSK_STONE', 'ITEM_DAWN_STONE')


def defines(path, prefix):
    out = {}
    for m in re.finditer(r'^#define (' + prefix + r'\w+) (\d+)\b', open(path).read(), re.M):
        out[m.group(1)] = int(m.group(2))
    return out


def constants():
    inc = os.path.join(DECOMP, 'include', 'constants')
    c = defines(os.path.join(inc, 'pokemon.h'), 'EVO_METHOD_')
    c.update(defines(os.path.join(inc, 'items.h'), 'ITEM_'))
    c.update(defines(os.path.join(inc, 'species.h'), 'SPECIES_'))
    return c


def entries_of(rec):
    return [e for e in (struct.unpack_from('<3H', rec, 6 * k) for k in range(len(rec) // 6)) if any(e)]


def pack(entries):
    assert len(entries) <= 7, entries
    return b''.join(struct.pack('<3H', *e) for e in entries) + bytes(6 * (7 - len(entries)))


def table(data, C):
    """data/trade_evos.json's evolutions as {species: [(method, param, target)]}."""
    val = lambda v: v if isinstance(v, int) else C[v]
    return {C[sp]: [tuple(val(v) for v in e) for e in lst] for sp, lst in data['evolutions'].items()}


def stone_use(items, C):
    """The item-data values every evolution stone has (+0xA field use, +0xC party use, +0x11 flags), read from Black 2."""
    vals = {(items[C[s]][0xA], items[C[s]][0xC], items[C[s]][0x11]) for s in STONES}
    assert len(vals) == 1, f'evolution stones differ in their item data: {vals}'
    field, party, flags = vals.pop()
    assert party == 1 and flags == 0x08, (field, party, flags)
    return field, party, flags


def _pad_to(path, size):
    """Grow the NARC's GMIF (last section) with zero bytes to `size` (as shops.py / build_rom.pad_archives)."""
    data = bytearray(open(path, 'rb').read())
    assert len(data) <= size, f'{path}: {len(data)} bytes, over its fixed size {size}'
    off = struct.unpack_from('<H', data, 0xC)[0]
    for _ in range(2):
        off += struct.unpack_from('<I', data, off + 4)[0]
    assert data[off:off + 4] == b'GMIF'
    extra = size - len(data)
    struct.pack_into('<I', data, off + 4, struct.unpack_from('<I', data, off + 4)[0] + extra)
    struct.pack_into('<I', data, 8, size)
    open(path, 'wb').write(bytes(data) + bytes(extra))


def apply(files):
    sys.path.insert(0, os.path.join(HERE, '..'))
    import narcio
    from b2files import arc_path
    data = json.load(open(os.path.join(ROOT, 'data', 'trade_evos.json')))
    C = constants()
    trade = {C['EVO_METHOD_TRADE'], C['EVO_METHOD_TRADE_WITH_ITEM'], C['EVO_METHOD_TRADE_WITH_SPECIES']}
    new = table(data, C)
    out = []

    # 1. evolutions: exactly the species with a trade method in Black 2's table, other evolutions kept
    vanilla = narcio.load(VANILLA, ARC_EVO)
    evo = narcio.load(files, ARC_EVO)
    traders = {i for i, rec in enumerate(vanilla) if any(m in trade for m, _, _ in entries_of(rec))}
    assert traders == set(new), f'trade species not covered: {sorted(traders - set(new))}, ' \
                                f'not trade species: {sorted(set(new) - traders)}'
    for sp, lst in new.items():
        kept = [e for e in entries_of(vanilla[sp]) if e[0] not in trade]
        assert all(e in lst for e in kept), f'species {sp}: a non-trade evolution was lost: {kept} vs {lst}'
        assert not any(e[0] in trade for e in lst), f'species {sp}: still a trade method'
        assert evo[sp] in (vanilla[sp], pack(lst)), f'species {sp}: evolution file changed by another patch'
        evo[sp] = pack(lst)
    narcio.save(files, ARC_EVO, evo)
    out.append(f'{len(new)} species')

    # 2. items an EVO_METHOD_ITEM evolution uses: the Bag "Use" of an evolution stone
    items = narcio.load(files, ARC_ITEM)
    field, party, flags = stone_use(items, C)
    used = sorted({p for lst in new.values() for m, p, _ in lst if m == C['EVO_METHOD_ITEM']})
    changed = []
    for it in used:
        d = bytearray(items[it])
        if (d[0xA], d[0xC], d[0x11] & flags) == (field, party, flags):
            continue                                   # a stone already (Water Stone), or patched before
        assert d[0xA] == 0 and d[0xC] == 0 and not any(d[0x10:]), f'item {it}: unexpected item data {d.hex()}'
        assert not d[8] & 0x20, f'item {it}: not holdable'
        d[0xA], d[0xC], d[0x11] = field, party, flags
        items[it] = bytes(d)
        changed.append(it)
    narcio.save(files, ARC_ITEM, items)
    out.append(f'Bag use like a stone: items {changed}')

    # 3. the shop list (after the shops patch)
    shop = data['shop']
    f = shop['id'] + 6
    lists, counts = narcio.load(files, ARC_SHOP), narcio.load(files, ARC_SHOP_COUNT)
    sapphire = json.load(open(os.path.join(ROOT, 'data', 'hoenn_shops.json')))['shops'][str(shop['id'])]
    assert sapphire['label'] == shop['label'], (sapphire['label'], shop['label'])
    add = [C[x] for x in shop['add']]
    cur = list(struct.unpack(f'<{len(lists[f]) // 2}H', lists[f]))
    assert counts[0][f] == len(cur), (counts[0][f], len(cur))
    if cur == sapphire['ids']:
        cur += add
    elif cur != sapphire['ids'] + add:
        raise SystemExit(f'trade_evos: shop list {shop["id"]} is not Sapphire\'s {shop["label"]}: put trade_evos '
                         f'after shops in the patch list')
    lists[f] = struct.pack(f'<{len(cur)}H', *cur)
    cnt = bytearray(counts[0]); cnt[f] = len(cur); counts[0] = bytes(cnt)
    narcio.save(files, ARC_SHOP, lists); narcio.save(files, ARC_SHOP_COUNT, counts)
    size0 = os.path.getsize(arc_path(VANILLA, ARC_SHOP))
    _pad_to(arc_path(files, ARC_SHOP), size0)
    out.append(f'shop {shop["id"]} ({shop["label"]}) + items {add}')
    return 'trade evolutions: ' + '; '.join(out)
