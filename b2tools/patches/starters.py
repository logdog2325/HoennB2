"""Hoenn's starters on Black 2's starter screen (overlay 316, `callPoke3Select`).

Code: the three species it shows (silhouette, name, cry) are a table at arm9_ov316.bin 0x2C14 (data_ov316_0219fa94:
Snivy 495, Tepig 498, Oshawott 501; notes/RESEARCH_STORY_SPRITES.md section 3). Treecko 252, Torchic 255, Mudkip 258
— left/middle/right like Birch's Bag (grass/fire/water, which also matches the screen's own captions). The script
gives the Pokémon itself (src/field_scripts/0634_route_101.s Script_14).

Files (a/2/0/2, the screen's own archive; b2tools/psel_art.py): the coloured picture shown when a ball is picked is
not taken from the table but stored per ball (Snivy/Tepig/Oshawott) -> Treecko/Torchic/Mudkip's Black 2 front
stills at 2x with their palettes; Bianca, who holds the case on the bottom screen, is taken out of the 3D scene
(the case and the room stay). Same file sizes, so the ROM layout and the savestates are unchanged."""
import os, sys

AT = 0x2C14
OLD = bytes.fromhex('ef01f201f501')
NEW = bytes.fromhex('fc00ff000201')

def apply_code(code):
    path = os.path.join(code, 'arm9_ov316.bin')
    data = bytearray(open(path, 'rb').read())
    assert data[AT:AT + 6] in (OLD, NEW), data[AT:AT + 6].hex()
    data[AT:AT + 6] = NEW
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)
    return 'starter screen: Treecko, Torchic, Mudkip'

def apply(files):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    import narcio, psel_art
    psel = narcio.load(files, psel_art.ARC_PSEL)
    new = psel_art.hoenn_entries(psel, narcio.load(files, psel_art.ARC_POKEGRA))
    for k, v in new.items(): psel[k] = v
    narcio.save(files, psel_art.ARC_PSEL, psel)
    return f'starter screen art: Treecko/Torchic/Mudkip pictures, no Bianca (a/2/0/2 files {sorted(new)})'
