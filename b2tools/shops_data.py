"""Shops agent: Sapphire's Poké Mart item lists as Black 2 shop lists -> data/hoenn_shops.json (installed by the build
patch b2tools/patches/shops.py).

    python3 shops_data.py

How Black 2's shops work (read in its code and data, 2026-10-06):
- A clerk script sets 0x8000 = shop id, 0x8001 = greeting (1 = "Welcome! May I help you?", 2 = the TM department's
  greeting) and calls global script 10110 (data/field_scripts/1247.s: Buy/Sell/Quit menu, then CallFriendlyShopBuy).
- ShopUI_Init / ShopUI_LoadPokeMartItems (ov036 0x021abf4c / 0x021ac724, b2tools/armdis.py): id 255 = the standard
  clerk, list file BADGE_SHOP_DAT_IDS[badges] (files 0-5); ids 239-254 are BP / special shops; any other id k reads
  list file k + 6. List files are NARC a/2/8/2 (u16 item ids), their item counts are bytes of a/2/8/3 file 0 (one per
  list file). a/2/8/2 has 80 files: 0-5 badge lists, 6-31 Black 2's specialty lists (ids 0-25), 32-79 empty.
- Prices are Black 2's own item prices.

Fixed archive size: the game keeps the ROM's file table in RAM, so a savestate made with an a/2/8/2 of another size
reads at most the old size (notes/TESTING.md). a/2/8/2 is not one of build_rom.py's padded (RESERVE) archives, so the
patch keeps it at exactly its original 1300 bytes: Sapphire's 21 lists take Black 2's specialty slots (ids 0-25), each
Hoenn Pokémon Center's second clerk (Black 2's Center scripts, ids in ID_FOR) gets its own town's Sapphire Mart list,
unused ids get a one-item list. Badge lists 0-5 stay Black 2's.
"""
import os, re, sys, json, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'converter'))
RUBY = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps')

# (Sapphire map, pokemart label) per shop id. Ids used by the second clerk of a Hoenn Pokémon Center (Black 2's own
# Center scripts: Oldale 796 -> 0, EverGrande 16 -> 1, Fallarbor 82 -> 3, Fortree 130 -> 4, Lavaridge 198 -> 5,
# Lilycove 218 -> 6, Mauville 230 -> 7, Mossdeep 244 -> 8, Pacifidlog 814 -> 11, Petalburg 826 -> 12,
# Rustboro 850 / Dewford 2 -> 13, Slateport 870 -> 21, Verdanturf 908 -> 22, Sootopolis 886 -> 24) hold that town's list.
SHOPS = {
    0: ('OldaleTown_Mart', 'OldaleTown_Mart_Pokemart_Expanded'),
    1: ('OldaleTown_Mart', 'OldaleTown_Mart_Pokemart_Basic'),
    2: ('PetalburgCity_Mart', 'PetalburgCity_Mart_Pokemart_Basic'),
    3: ('FallarborTown_Mart', 'FallarborTown_Mart_Items'),
    4: ('FortreeCity_Mart', 'FortreeCity_Mart_Items'),
    5: ('LavaridgeTown_Mart', 'LavaridgeTown_Mart_Pokemart'),
    6: ('LilycoveCity_DepartmentStore_2F', 'LilycoveCity_DepartmentStore_2F_Pokemart1'),
    7: ('MauvilleCity_Mart', 'MauvilleCity_Mart_Pokemart'),
    8: ('MossdeepCity_Mart', 'MossdeepCity_Mart_Pokemart'),
    9: ('RustboroCity_Mart', 'RustboroCity_Mart_Pokemart_Basic'),
    10: ('LilycoveCity_DepartmentStore_2F', 'LilycoveCity_DepartmentStore_2F_Pokemart2'),
    11: ('LavaridgeTown_HerbShop', 'LavaridgeTown_HerbShop_Pokemart'),
    12: ('PetalburgCity_Mart', 'PetalburgCity_Mart_Pokemart_Expanded'),
    13: ('RustboroCity_Mart', 'RustboroCity_Mart_Pokemart_Expanded'),
    14: ('LilycoveCity_DepartmentStore_3F', 'LilycoveCity_DepartmentStore_3F_Pokemart_Vitamins'),
    15: ('LilycoveCity_DepartmentStore_3F', 'LilycoveCity_DepartmentStore_3F_Pokemart_StatBoosters'),
    16: ('LilycoveCity_DepartmentStore_4F', 'LilycoveCity_DepartmentStore_4F_Pokemart_AttackTMs'),
    17: ('LilycoveCity_DepartmentStore_4F', 'LilycoveCity_DepartmentStore_4F_Pokemart_DefenseTMs'),
    18: ('SlateportCity', 'SlateportCity_Pokemart_EnergyGuru'),      # Slateport Market (ch3a, scenes/SlateportCity.inc)
    19: ('SlateportCity', 'SlateportCity_Pokemart_PowerTMs'),
    20: ('EverGrandeCity_PokemonLeague', 'EverGrandeCity_PokemonLeague_Items'),   # the League clerk (ch11, scripts 0154)
    21: ('SlateportCity_Mart', 'SlateportCity_Mart_Pokemart'),
    22: ('VerdanturfTown_Mart', 'VerdanturfTown_Mart_Pokemart'),
    24: ('SootopolisCity_Mart', 'SootopolisCity_Mart_Pokemart'),
}
FILLER = 'ITEM_POTION'          # ids 23, 25: no Sapphire list and no Hoenn Center uses them
ID_FOR = {lab: i for i, (_, lab) in SHOPS.items()}


def sapphire_list(m, label):
    s = open(os.path.join(RUBY, m, 'scripts.inc')).read()
    blk = s.split(label + '::', 1)[1]
    items = []
    for line in blk.splitlines()[1:]:
        mm = re.match(r'\s*\.2byte (\w+)', line)
        if not mm: continue
        if mm.group(1) == 'ITEM_NONE': break
        items.append(mm.group(1))
    return items


def main():
    from gen_items import b2_items, tm_items, map_item
    items, tms = b2_items(), tm_items()
    # Gen 3 mail -> the Gen 5 mail converter/gen_items.py already chose (data/hoenn_items.json notes)
    notes0 = json.load(open(os.path.join(ROOT, 'data', 'hoenn_items.json')))['notes']
    mail = dict(re.match(r'(ITEM_\w+_MAIL): Gen 3 mail; stand-in (ITEM_\w+)', n).groups() for n in notes0 if 'Gen 3 mail' in n)
    out, notes = {}, []
    for i in range(26):
        if i in SHOPS:
            m, lab = SHOPS[i]
            src = sapphire_list(m, lab)
            b2 = []
            for it in src:
                b = mail.get(it) or map_item(it, items, tms, notes, [0, {}])
                if b in mail.values() and it not in mail: notes.append(f'{it}: mail stand-in {b}')
                if b: b2.append(b)
                else: notes.append(f'{lab}: {it} has no Black 2 item, left out')
                if it in mail: notes.append(f'{lab}: {it} -> {b} (Gen 3 mail, same stand-in as the item balls)')
            out[str(i)] = dict(map=m, label=lab, sapphire=src, items=b2, ids=[items[b] for b in b2])
        else:
            out[str(i)] = dict(map=None, label='filler (no Sapphire list, no Hoenn Center uses this id)',
                               items=[FILLER], ids=[items[FILLER]])
    doc = __doc__.strip()
    json.dump({'_doc': doc, 'shops': out, 'notes': sorted(set(notes))},
              open(os.path.join(ROOT, 'data', 'hoenn_shops.json'), 'w'), indent=1, ensure_ascii=False)
    for i, s in out.items(): print(i, s['label'], len(s['items']), ' '.join(x[5:] for x in s['items']))
    print('\n'.join(sorted(set(notes))))


# ---- Emerald (HOENN_VERSION=emerald python3 shops_data.py [--check]; emerald_data 2026-10-12, EMERALD-1) ----
# The same shop ids (the same marts and Center clerks: shops_rooms.py and the Center scripts keep them), each with the
# list pokeemerald's mart of that place sells; written to data/emerald/hoenn_shops.json, only the ids whose list differs
# (version.load_json deep-merges it; "label" stays Sapphire's, the list's identity for trade_evos, "emerald_label" is
# pokeemerald's). Measured: every list is the same as Sapphire's (only pokeemerald's TM names differ), so the overlay
# holds none; b2tools/patches/shops.py and trade_evos.py read data/hoenn_shops.json with json.load: switch them to
# version.load_json if an Emerald list ever differs. Emerald's marts on maps this build does not have (Battle Frontier,
# Trainer Hill: closed at first, decisions 1A/2) are listed for later; ids 23 and 25 (fillers) are free for them.
EMERALD_MAPS = os.path.join(ROOT, 'external', 'pokeemerald', 'data', 'maps')
EMERALD_LABEL = {   # Sapphire label -> (pokeemerald map, label) where pokeemerald renamed them; else the same names
    'FallarborTown_Mart_Items': ('FallarborTown_Mart', 'FallarborTown_Mart_Pokemart'),
    'FortreeCity_Mart_Items': ('FortreeCity_Mart', 'FortreeCity_Mart_Pokemart'),
    'EverGrandeCity_PokemonLeague_Items': ('EverGrandeCity_PokemonLeague_1F', 'EverGrandeCity_PokemonLeague_1F_Pokemart'),
}


def emerald_list(m, label):
    """pokeemerald's list: `.2byte ITEM_X` lines up to `pokemartlistend` (or ITEM_NONE)."""
    s = open(os.path.join(EMERALD_MAPS, m, 'scripts.inc')).read()
    blk = s.split(label + ':', 1)[1]
    items = []
    for line in blk.splitlines()[1:]:
        if line.strip().startswith('pokemartlistend'): break
        mm = re.match(r'\s*\.2byte (\w+)', line)
        if not mm: continue
        if mm.group(1) == 'ITEM_NONE': break
        items.append(mm.group(1))
    return items


def main_emerald():
    import glob
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import narcio
    from narc import write_narc
    from gen_items import b2_items, tm_items, map_item, emerald_tm_names, _write_or_check
    check = '--check' in sys.argv[1:]
    items, tms = b2_items(), tm_items()
    tmn = emerald_tm_names()
    sap = json.load(open(os.path.join(ROOT, 'data', 'hoenn_shops.json')))['shops']
    notes0 = json.load(open(os.path.join(ROOT, 'data', 'hoenn_items.json')))['notes']
    mail = dict(re.match(r'(ITEM_\w+_MAIL): Gen 3 mail; stand-in (ITEM_\w+)', n).groups() for n in notes0 if 'Gen 3 mail' in n)
    out, notes, lists = {}, [], {}
    for i, (m, lab) in SHOPS.items():
        em, elab = EMERALD_LABEL.get(lab, (m, lab))
        src = emerald_list(em, elab)
        b2 = []
        for it in src:
            b = mail.get(it) or map_item(tmn.get(it, it), items, tms, notes, [0, {}])
            if b: b2.append(b)
            else: notes.append(f'{elab}: {it} has no Black 2 item, left out')
        lists[i] = [items[b] for b in b2]
        e = dict(map=m, label=lab, emerald_map=em, emerald_label=elab, emerald=src, items=b2, ids=lists[i])
        if b2 != sap[str(i)]['items']: out[str(i)] = dict(sap[str(i)], **e)
    # a/2/8/2 keeps Black 2's size (patches/shops.py): the lists packed as the patch packs them
    files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    from b2files import arc_path
    arc = narcio.load(files, 282)
    size0 = os.path.getsize(arc_path(files, 282))
    for k, sh in sap.items():
        ids = lists.get(int(k), sh['ids'])
        arc[int(k) + 6] = struct.pack(f'<{len(ids)}H', *ids)
    size = len(write_narc(arc))
    assert size <= size0, f'Emerald shop lists: a/2/8/2 would be {size} bytes, over Black 2\'s {size0}'
    seen = {(EMERALD_LABEL.get(lab, (m, lab))[1]) for m, lab in SHOPS.values()}
    later = []
    for f in sorted(glob.glob(os.path.join(EMERALD_MAPS, '*', 'scripts.inc'))):
        for lab in re.findall(r'\bpokemart (\w+)', open(f).read()):
            if lab not in seen and lab not in later: later.append(lab)
    doc = ('Emerald overlay of data/hoenn_shops.json (version.load_json deep merge), written by b2tools/shops_data.py with '
           'HOENN_VERSION=emerald: the shop ids whose pokeemerald list differs from Sapphire\'s (label = Sapphire\'s, the '
           'same mart; emerald_label = pokeemerald\'s). later: pokeemerald marts on maps this build does not have.')
    want = {os.path.join(ROOT, 'data', 'emerald', 'hoenn_shops.json'): json.dumps(
        {'_doc': doc, 'shops': out, 'later': later, 'notes': sorted(set(notes))}, indent=1, ensure_ascii=False) + '\n'}
    for i, sh in out.items():
        print(f'{i} {sh["emerald_label"]}: {" ".join(x[5:] for x in sh["items"])}\n   (Sapphire: {" ".join(x[5:] for x in sap[i]["items"])})')
    print(f'{len(out)} of {len(SHOPS)} lists differ in Emerald; a/2/8/2 {size} of {size0} bytes; later (maps not built): {later}')
    if notes: print('notes: ' + '; '.join(sorted(set(notes))))
    _write_or_check(want, check)


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import version
    main_emerald() if version.is_emerald() else main()
