"""TEST ONLY (trade_evos agent): Littleroot's town sign (stand at (183,366), face north) gives, with an empty party, a test
party and the items of the trade-evolution tests (patches/trade_evos.py); with a party, it opens the Lilycove Dept.
Store 3F right clerk's list (shop 15) instead. Run after `scripts`: it reassembles script file 0778 from a copy of
src/field_scripts/0778_littleroot_town.s with a jump at the top of Script_1 (the shared source is not touched)."""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'src', 'field_scripts', '0778_littleroot_town.s')
HOOK = 'Script_1:\n    ActorsPauseAll\n'

TEST = r'''
// ---- test_trade_evos (test only) ----
Test_TradeEvos:
    PokePartyGetCount 0x8000, 0
    VMStackPush 0x8000
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TestTradeEvosShop     // (jumps when the comparison is false: a party already)
    PokePartyAdd 0x8010, SPECIES_KADABRA, 0, 25
    PokePartyAdd 0x8010, SPECIES_ONIX, 0, 30
    PokePartyAdd 0x8010, SPECIES_POLIWHIRL, 0, 30
    PokePartyAdd 0x8010, SPECIES_KARRABLAST, 0, 30
    PokePartyAdd 0x8010, SPECIES_SHELMET, 0, 30
    PokePartyAdd 0x8010, SPECIES_SEADRA, 0, 30
    ItemAdd ITEM_RARE_CANDY, 9, 0x8010
    ItemAdd ITEM_METAL_COAT, 1, 0x8010
    ItemAdd ITEM_KINGS_ROCK, 1, 0x8010
    ItemAdd ITEM_DRAGON_SCALE, 1, 0x8010
    ItemAdd ITEM_PRISM_SCALE, 1, 0x8010
    SEPlay SEQ_SE_MESSAGE
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_TestTradeEvosShop:
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 15                          // LilycoveCity_DepartmentStore_3F_Pokemart_StatBoosters
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
'''


def apply(files):
    sys.path.insert(0, os.path.join(HERE, '..'))
    import narcio
    spec = importlib.util.spec_from_file_location('scripts_patch', os.path.join(HERE, 'scripts.py'))
    scripts = importlib.util.module_from_spec(spec); spec.loader.exec_module(scripts)
    src = open(SRC, encoding='utf-8').read()
    assert src.count(HOOK) == 1, 'Script_1 of 0778 changed: update test_trade_evos.HOOK'
    src = src.replace(HOOK, HOOK + '    VMJump Test_TradeEvos\n', 1) + TEST
    out = os.path.join(ROOT, 'work', 'agents', 'trade_evos', 'test_0778.s')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(src)
    entries = narcio.load(files, 56)
    entries[778] = scripts.assemble(out)
    narcio.save(files, 56, entries)
    return f'test: Littleroot town sign gives the trade-evolution test party/items, then opens shop 15 ({len(entries[778])} B)'
