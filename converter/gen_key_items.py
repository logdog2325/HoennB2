"""Sapphire's key items as Black 2 items (S_common; notes/STORY_COMMON.md "Key items").

    python3 gen_key_items.py              table + header + data/hoenn_key_items.json (with the item text)
    python3 gen_key_items.py --install    also writes src/text/overrides_key_items.json, which the text patch packs.
        Install it together with new base savestates: the longer item texts move the message files after 0063 inside
        a/0/0/2, whose table the game reads at boot, so savestates made before read later system texts (place names,
        the nickname screen ...) at stale offsets and hang (tested 2026-10-07: black screen at a nickname screen).

Every key item a Sapphire script gives, checks or takes (pokeruby src/data/items_en.h, POCKET_KEY_ITEMS) gets a Black 2
item id. Black 2 already has some with the same meaning (S.S. Ticket, rods, Coin Case, Basement/Storage Key, Red/Blue
Orb, fossils, Contest Pass; its Bicycle and Dowsing Machine do what the Mach Bike and Itemfinder do). The rest go on
Gen 4 key items Black 2 carries but no Black 2 script gives (checked: no item command or work argument in
external/pokebw2/data/field_scripts names them), picked for a fitting icon (render: arm9 ITEM_GRAPHICS_CHARS_AND_PAL
0x02090d50 -> a/0/2/5). Black 2 gave the Bicycle and the Dowsing Machine on Unova maps that Hoenn replaced.
Each mapped item gets Sapphire's name (Gen 5 capitals) and Sapphire's description (gen3text) in the item text files:
system 0064 (name), 0481 (with article), 0482 (plural), 0063 (description), line = item id.

Writes:
  src/include/hoenn_key_items.h          #define ITEM_<Sapphire name> <Black 2 item> (only names Black 2 lacks)
  data/hoenn_key_items.json              the table and the item text lines ("text")
  src/text/overrides_key_items.json      --install only: the item text lines (b2tools/patches/text.py merges
                                         src/text/overrides_*.json)
"""
import os, re, sys, json
from gen3text import convert

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
B2 = os.path.join(ROOT, 'external', 'pokebw2')

# Sapphire item -> (Black 2 item, Sapphire's name in Gen 5 capitals, how)
#   same   = Black 2's item with the same meaning (name already right or only respelled)
#   reuse  = an unused Black 2 key item renamed (icon in the comment)
#   decide = needs the user
TABLE = {
    'ITEM_MACH_BIKE':      ('ITEM_BICYCLE',      'Mach Bike',      'same'),    # Black 2's bike: rides (field use 4)
    'ITEM_ACRO_BIKE':      (None,                None,             'not given'),  # one bike (user, notes/DECISIONS.md)
    'ITEM_COIN_CASE':      ('ITEM_COIN_CASE',    'Coin Case',      'same'),
    'ITEM_ITEMFINDER':     ('ITEM_DOWSING_MCHN', 'Itemfinder',     'same'),    # Black 2's Itemfinder (field use 0x19)
    'ITEM_OLD_ROD':        ('ITEM_OLD_ROD',      'Old Rod',        'same'),    # no field use in Black 2's data (notes)
    'ITEM_GOOD_ROD':       ('ITEM_GOOD_ROD',     'Good Rod',       'same'),    # no field use in Black 2's data (notes)
    'ITEM_SUPER_ROD':      ('ITEM_SUPER_ROD',    'Super Rod',      'same'),
    'ITEM_SS_TICKET':      ('ITEM_SS_TICKET',    'S.S. Ticket',    'same'),
    'ITEM_CONTEST_PASS':   ('ITEM_CONTEST_PASS', 'Contest Pass',   'same'),
    'ITEM_WAILMER_PAIL':   ('ITEM_SPRAYDUCK',    'Wailmer Pail',   'reuse'),   # watering can
    'ITEM_DEVON_GOODS':    ('ITEM_PARCEL',       'Devon Goods',    'reuse'),   # parcel (chapters already use it)
    'ITEM_SOOT_SACK':      ('ITEM_LOOT_SACK',    'Soot Sack',      'reuse'),   # sack
    'ITEM_BASEMENT_KEY':   ('ITEM_BASEMENT_KEY', 'Basement Key',   'same'),
    'ITEM_POKEBLOCK_CASE': ('ITEM_POFFIN_CASE',  'Pokéblock Case', 'reuse'),   # case (chapters already use it)
    'ITEM_LETTER':         ('ITEM_OAKS_LETTER',  'Letter',         'reuse'),   # envelope
    'ITEM_EON_TICKET':     ('ITEM_LIBERTY_PASS', 'Eon Ticket',     'reuse'),   # ticket (Black 2's island-event pass)
    'ITEM_RED_ORB':        ('ITEM_RED_ORB',      'Red Orb',        'same'),
    'ITEM_BLUE_ORB':       ('ITEM_BLUE_ORB',     'Blue Orb',       'same'),
    'ITEM_SCANNER':        ('ITEM_MACHINE_PART', 'Scanner',        'reuse'),   # grey device
    'ITEM_GO_GOGGLES':     ('ITEM_EXPLORER_KIT', 'Go-Goggles',     'reuse'),   # explorer's helmet and bag (no goggles icon)
    'ITEM_METEORITE':      ('ITEM_ENIGMA_STONE', 'Meteorite',      'reuse'),   # rock
    'ITEM_ROOM_1_KEY':     ('ITEM_SUITE_KEY',    'Rm. 1 Key',      'reuse'),   # key
    'ITEM_ROOM_2_KEY':     ('ITEM_WORKS_KEY',    'Rm. 2 Key',      'reuse'),   # key
    'ITEM_ROOM_4_KEY':     ('ITEM_SECRET_KEY',   'Rm. 4 Key',      'reuse'),   # key
    'ITEM_ROOM_6_KEY':     ('ITEM_CARD_KEY',     'Rm. 6 Key',      'reuse'),   # card key (no fourth key icon)
    'ITEM_STORAGE_KEY':    ('ITEM_STORAGE_KEY',  'Storage Key',    'same'),
    'ITEM_ROOT_FOSSIL':    ('ITEM_ROOT_FOSSIL',  'Root Fossil',    'same'),
    'ITEM_CLAW_FOSSIL':    ('ITEM_CLAW_FOSSIL',  'Claw Fossil',    'same'),
    'ITEM_DEVON_SCOPE':    ('ITEM_POKE_RADAR',   'Devon Scope',    'reuse'),   # Pokémon-finding device
}

# Not Sapphire items, but things Sapphire gives that Black 2 keeps as items (user decision 2026-10-06): the PokéNav
# is Black 2's Xtransceiver (one item per player gender: h_give_pokenav), named and described from Mr. Stone's words
# (pokeruby RustboroCity_DevonCorp_3F_Text_MrStoneExplainPokenav); no longer in the new-game Bag (story patch).
EXTRA = {
    'ITEM_POKENAV':        ('ITEM_XTRANSCEIVER_MALE',   'PokéNav', 'reuse'),
    'ITEM_POKENAV_FEMALE': ('ITEM_XTRANSCEIVER_FEMALE', 'PokéNav', 'reuse'),
}
POKENAV_DESC = 'A Pokémon Navigator, an indispensable\\ntool for any Trainer on an adventure.\\nIt has a map of the Hoenn region.'

# Emerald's event tickets (events agent, 2026-10-07: in-game events instead of Mystery Gift; notes/EVENTS.md): Emerald's
# names (Gen 5 capitals) and descriptions (pokeemerald src/data/text/item_descriptions.h), on Gen 4 key items Black 2
# carries but no Black 2 script gives, picked for the icon and with no field use in Black 2's item data (a/0/2/4 byte 10
# = 0: no "Use" in the Bag; the Town Map (442) would open Unova's map): an old brown book for the Old Sea Map, Coupon 3
# (cream) and Coupon 2 (green) tickets for the Mystic and Aurora Tickets. The Eon Ticket is Sapphire's (TABLE).
EVENT = {
    'ITEM_OLD_SEA_MAP':    ('ITEM_JOURNAL',  'Old Sea Map',   'sOldSeaMapDesc'),
    'ITEM_MYSTIC_TICKET':  ('ITEM_COUPON_3', 'Mystic Ticket', 'sMysticTicketDesc'),
    'ITEM_AURORA_TICKET':  ('ITEM_COUPON_2', 'Aurora Ticket', 'sAuroraTicketDesc'),
}
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')

def main():
    b2 = {k: int(v) for k, v in re.findall(r'#define (ITEM_\w+)\s+(\d+)', open(f'{B2}/include/constants/items.h').read())}
    items = open(f'{RUBY}/src/data/items_en.h', encoding='utf-8').read()
    descs = open(f'{RUBY}/src/data/item_descriptions_en.h', encoding='utf-8').read()
    keys = []
    for m in re.finditer(r'\{\s*\.name = _\("([^"]*)"\),\s*\.itemId = (ITEM_\w+),(.*?)\n    \}', items, re.S):
        if 'POCKET_KEY_ITEMS' in m.group(3):
            keys.append((m.group(2), re.search(r'\.description = (\w+)', m.group(3)).group(1)))
    missing = [k for k, _ in keys if k not in TABLE]
    if missing: raise SystemExit(f'key items without a Black 2 item: {missing}')
    text = {f: {} for f in ('system/0064_item_names.txt', 'system/0481_item_names_with_article.txt',
                            'system/0482_item_names_plural.txt', 'system/0063_scrcmd_resort_shop_scrcmd_bsubway.txt')}
    table, header = {}, []
    for sap, desc_sym in keys:
        item, name, how = TABLE[sap]
        if item is None:                                  # not given in this port: no define, no text
            table[sap] = dict(b2_item=None, id=None, how=how, name=None, description=None); continue
        n = b2[item]
        raw = ''.join(re.findall(r'"(.*?)"', re.search(r'%s\[\] = _\((.*?)\);' % desc_sym, descs, re.S).group(1)))
        desc = convert(raw, expand=True)[0]
        table[sap] = dict(b2_item=item, id=n, how=how, name=name, description=desc if name else None)
        if sap not in b2: header.append(f'#define {sap:<22} {item:<20} // {n} {how}')
        if name:   # (an item two Sapphire items share gets the first one's text)
            text['system/0064_item_names.txt'][str(n)] = name
            art = 'an' if name[0] in 'AEIOU' else 'a'
            text['system/0481_item_names_with_article.txt'][str(n)] = f'{{bd01}}{art} {{ff00:255}}{name}'
            text['system/0482_item_names_plural.txt'][str(n)] = name if name.endswith('s') else name + 's'
            text['system/0063_scrcmd_resort_shop_scrcmd_bsubway.txt'][str(n)] = desc
    for sap, (item, name, how) in EXTRA.items():
        n = b2[item]
        table[sap] = dict(b2_item=item, id=n, how=how, name=name, description=POKENAV_DESC)
        header.append(f'#define {sap:<22} {item:<20} // {n} {how}')
        text['system/0064_item_names.txt'][str(n)] = name
        text['system/0481_item_names_with_article.txt'][str(n)] = f'{{bd01}}a {{ff00:255}}{name}'
        text['system/0482_item_names_plural.txt'][str(n)] = name + 's'
        text['system/0063_scrcmd_resort_shop_scrcmd_bsubway.txt'][str(n)] = POKENAV_DESC
    edescs = open(f'{EMERALD}/src/data/text/item_descriptions.h', encoding='utf-8').read() if os.path.isdir(EMERALD) else ''
    for sap, (item, name, desc_sym) in EVENT.items():
        if not edescs: break                                 # (pokeemerald not cloned: the event tickets are left out)
        n = b2[item]
        raw = ''.join(re.findall(r'"(.*?)"', re.search(r'%s\[\] = _\((.*?)\);' % desc_sym, edescs, re.S).group(1)))
        desc = convert(raw.replace('\\n', '\\n'), expand=True)[0]
        table[sap] = dict(b2_item=item, id=n, how='reuse (Emerald event ticket)', name=name, description=desc)
        header.append(f'#define {sap:<22} {item:<20} // {n} reuse (Emerald event ticket)')
        text['system/0064_item_names.txt'][str(n)] = name
        text['system/0481_item_names_with_article.txt'][str(n)] = f'{{bd01}}{"an" if name[0] in "AEIOU" else "a"} {{ff00:255}}{name}'
        text['system/0482_item_names_plural.txt'][str(n)] = name + 's'
        text['system/0063_scrcmd_resort_shop_scrcmd_bsubway.txt'][str(n)] = desc
    header.append('// ITEM_ACRO_BIKE: not given (one bike: Rydel gives ITEM_MACH_BIKE = Black 2\'s Bicycle; notes/DECISIONS.md)')
    open(os.path.join(ROOT, 'src', 'include', 'hoenn_key_items.h'), 'w').write(
        '// Sapphire key items -> Black 2 items. GENERATED by converter/gen_key_items.py (table and reasons there;\n'
        '// notes/STORY_COMMON.md "Key items"). Sapphire names that Black 2 has with the same meaning (ITEM_SS_TICKET,\n'
        '// ITEM_OLD_ROD, ITEM_STORAGE_KEY, ...) are Black 2\'s own constants: no define.\n'
        '#pragma once\n' + '\n'.join(header) + '\n')
    if '--install' in sys.argv:
        json.dump(dict(_doc='Generated by converter/gen_key_items.py --install: item text lines (system file -> '
                            '{line: text}), merged by b2tools/patches/text.py over the decomp text.', **text),
                  open(os.path.join(ROOT, 'src', 'text', 'overrides_key_items.json'), 'w', encoding='utf-8'), indent=1,
                  ensure_ascii=False)
    json.dump(dict(_doc='Generated by converter/gen_key_items.py: Sapphire key item -> Black 2 item; "text" = the item '
                        'text lines --install puts in src/text/overrides_key_items.json.', items=table, text=text),
              open(os.path.join(ROOT, 'data', 'hoenn_key_items.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'{len(table)} key items: {sum(1 for t in table.values() if t["how"] == "same")} same, '
          f'{sum(1 for t in table.values() if t["how"] == "reuse")} reused, '
          f'{sum(1 for t in table.values() if t["how"] == "not given")} not given; {len(header) - 1} defines')

if __name__ == '__main__':
    main()
