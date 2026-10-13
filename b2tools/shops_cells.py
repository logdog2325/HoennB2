"""Shops agent stand-in for a builder feature: Black 2 tile attributes in a room's collision (collision.per).

    python3 shops_cells.py NAME [NAME ...]      (rewrites work/agents/$HOENN_AGENT/interiors/NAME/collision.per)

Black 2's collision cell is u16 0, u16 3, u16 attribute, u16 flags: walkable (0, 3, 0, 0x80), solid (0, 3, 1, 0x81),
and special solid tiles (0, 3, ATTR, 0x01) that the field code acts on (ov036 MapTile_Is*, SPECIAL_TILE_SCRIPTS at
0x021ca844; read with b2tools/armdis.py; Black 2's Pokémon Center chunk 827 uses them around its counters):
  0xD4 reception counter: FindActorForInteraction talks to the person on the far side (Sapphire MB_COUNTER)
  0xD6 PC (global script 10090), 0xD8 TV (10530), 0xE2 vending machine (10400: Fresh Water / Soda Pop / Lemonade)
  0xDF / 0xE0 / 0xE1 "assortment" shelves: script 2505-2507 (file 1237): "The shelves are jammed with vibrant Pokémon
  goods." (Sapphire MB_SHOP_SHELF: "The shelves brim with all sorts of Pokémon merchandise.")
models_interior.py writes only walkable/solid. Until it can (see the shops agent's report: map Sapphire behaviours
to these attributes, plus a recipe key "attrs"), this rewrites the cells of a built room in the agent's own copy:
Sapphire behaviours by SAPPHIRE_TO_B2, then the recipe's "attrs": [{"attr": "0xe2", "tiles": [[x, y], ...]}].
"""
import os, sys, json, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import models_interior as mi                                    # noqa: E402

SAPPHIRE_TO_B2 = {0x80: 0xD4,      # MB_COUNTER -> reception counter
                  0xE5: 0xDF,      # MB_SHOP_SHELF -> assortment A
                  0x83: 0xD6}      # MB_PC -> PC
OUT = os.path.join(ROOT, 'work', 'agents', os.environ.get('HOENN_AGENT', 'shops'), 'interiors')


def cells(name):
    """{chunk tile (x, z): attribute} for a room."""
    r = mi.load_recipe(name)
    sm = mi.sapphire_map(r['map'])
    meta = json.load(open(os.path.join(OUT, name, 'room.json')))
    ox, oz = meta['origin']
    out = {}
    for z in range(sm['h']):
        for x in range(sm['w']):
            b = sm['beh'][z][x]
            if b in SAPPHIRE_TO_B2 and not sm['walk'][z][x]: out[(ox + x, oz + z)] = SAPPHIRE_TO_B2[b]
    for a in r.get('attrs', []):
        for x, z in a['tiles']: out[(ox + x, oz + z)] = int(a['attr'], 0) if isinstance(a['attr'], str) else a['attr']
    return out


def apply(name):
    p = os.path.join(OUT, name, 'collision.per')
    per = bytearray(open(p, 'rb').read())
    w, h = struct.unpack_from('<HH', per, 0)
    c = cells(name)
    for (x, z), attr in c.items():
        o = 4 + 8 * (z * w + x)
        cur = struct.unpack_from('<HHHH', per, o)
        assert cur[3] & 1, f'{name}: tile ({x},{z}) is walkable, not given attribute {attr:#x}'
        struct.pack_into('<HHHH', per, o, 0, 3, attr, 0x01)
    open(p, 'wb').write(per)
    return c


if __name__ == '__main__':
    for n in sys.argv[1:]:
        c = apply(n)
        print(n, {f'{a:#x}': sum(1 for v in c.values() if v == a) for a in sorted(set(c.values()))})
