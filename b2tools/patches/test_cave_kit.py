"""TEST ONLY (caves_east, 2026-10-06): a field-move kit for cave tests. Never in a release build.

Littleroot's town sign (script file 778, Script_1; the scripts of the rest of Littleroot are replaced by VMHalt, as
hm_free.py's HOENN_TEST_HM setup does) gives, once per press:
  - a Lv 50 Mudkip if the party is empty (a wild battle with an empty party hangs) + flag 2401 (the field menu's
    POKEMON entry, set by Black 2's starter script);
  - all 8 badges and the field-move machines (HM01-HM06, TM70 Flash, TM94 Rock Smash): with hm_free.py every field
    move then works without a Pokémon that knows it;
then warps to HOENN_TEST_WARP=zone,x,z (HOENN_TEST_WARP_Y=level in 16-unit steps for a raised arrival tile);
the second sign (174,369, read facing north) does the same and warps to HOENN_TEST_WARP2 (HOENN_TEST_WARP2_Y).

    HOENN_TEST_WARP=128,8,20 ... python3 build_rom.py --clean ... scripts ... hm_free ... test_cave_kit
List it after `scripts` and `hm_free`. From work/emu/base_after_rival.dst, b2tools/cave_test.py's SIGN reads the sign.
"""
import os, importlib.util

_spec = importlib.util.spec_from_file_location('hm_free_', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hm_free.py'))
_hm = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_hm)

KIT = r'''
#include "asm/field_script.inc"
    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntriesEnd
Script_1:
    // TEST ONLY (test_cave_kit): party, badges, machines, then the test warp
    ActorsPauseAll
    PokePartyGetCount 0x8000, 0
    VMStackPush 0x8000
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_HasParty              // (jumps when the comparison is false)
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 50
L_HasParty:
    FlagSet 2401
    TrainerCardAddBadge 0
    TrainerCardAddBadge 1
    TrainerCardAddBadge 2
    TrainerCardAddBadge 3
    TrainerCardAddBadge 4
    TrainerCardAddBadge 5
    TrainerCardAddBadge 6
    TrainerCardAddBadge 7
    ItemAdd ITEM_HM01, 1, 0x8001
    ItemAdd ITEM_HM02, 1, 0x8001
    ItemAdd ITEM_HM03, 1, 0x8001
    ItemAdd ITEM_HM04, 1, 0x8001
    ItemAdd ITEM_HM05, 1, 0x8001
    ItemAdd ITEM_HM06, 1, 0x8001
    ItemAdd ITEM_TM70, 1, 0x8001
    ItemAdd ITEM_TM94, 1, 0x8001
    SEPlay SEQ_SE_MESSAGE
    MapChangeCore TEST_WARP_ZONE, TEST_WARP_X, TEST_WARP_Y, TEST_WARP_Z, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
Script_4:
    // TEST ONLY: the second Littleroot sign (174,369): the same kit, then HOENN_TEST_WARP2
    ActorsPauseAll
    VMCall Sub_Kit
    MapChangeCore TEST_WARP2_ZONE, TEST_WARP2_X, TEST_WARP2_Y, TEST_WARP2_Z, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
Sub_Kit:
    PokePartyGetCount 0x8000, 0
    VMStackPush 0x8000
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_HasParty2
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 50
L_HasParty2:
    FlagSet 2401
    TrainerCardAddBadge 0
    TrainerCardAddBadge 1
    TrainerCardAddBadge 2
    TrainerCardAddBadge 3
    TrainerCardAddBadge 4
    TrainerCardAddBadge 5
    TrainerCardAddBadge 6
    TrainerCardAddBadge 7
    ItemAdd ITEM_HM01, 1, 0x8001
    ItemAdd ITEM_HM02, 1, 0x8001
    ItemAdd ITEM_HM03, 1, 0x8001
    ItemAdd ITEM_HM04, 1, 0x8001
    ItemAdd ITEM_HM05, 1, 0x8001
    ItemAdd ITEM_HM06, 1, 0x8001
    ItemAdd ITEM_TM70, 1, 0x8001
    ItemAdd ITEM_TM94, 1, 0x8001
    SEPlay SEQ_SE_MESSAGE
    VMReturn
Script_2:
Script_3:
Script_5:
Script_6:
Script_7:
Script_8:
Script_9:
    VMHalt
    .balign 4, 0
'''

def apply(files):
    import narcio
    zone, x, z = os.environ.get('HOENN_TEST_WARP', '389,183,365').split(',')
    zone2, x2, z2 = os.environ.get('HOENN_TEST_WARP2', '389,183,365').split(',')
    entries = narcio.load(files, 56)
    entries[778] = _hm._assemble(KIT, dict(TEST_WARP_ZONE=zone, TEST_WARP_X=x, TEST_WARP_Z=z,
                                           TEST_WARP_Y=os.environ.get('HOENN_TEST_WARP_Y', '0'),
                                           TEST_WARP2_ZONE=zone2, TEST_WARP2_X=x2, TEST_WARP2_Z=z2,
                                           TEST_WARP2_Y=os.environ.get('HOENN_TEST_WARP2_Y', '0')))
    narcio.save(files, 56, entries)
    return f'TEST ONLY: Littleroot sign = field-move kit + warp to {zone},{x},{z}'
