"""TEST ONLY: the music test kit (music_check, notes/MUSIC.md "Tests"). Never in a release build.

Like test_sweep_kit.py: the kit is appended to Littleroot's real script file (0778) and only ScriptEntry 1 (the town
sign, read facing north at (183,366)) points at it, so the rest of Littleroot works. The sign's script first sleeps 60
frames: during that wait the test harness (work/agents/music_check/scripts/music_test.py) rewrites, in the copy of
the script in RAM, the placeholder words 0x3A5A-0x3A62 below (each is unique in the file), so one ROM does every test:

    mode 0 (default)  warp: MapChangeCore zone, x, y, z (placeholders 0x3A5A, 0x3A5B, 0x3A5D, 0x3A5C)
    mode 1            wild battle: CallWildBattle species (0x3A61), level (0x3A62)
    mode 2            trainer: TrainerBGMPlayPush trainer (0x3A61) (the "trainer spotted you" music), 240 frames,
                      then the battle (CallTrainerBattle) and its end
    mode 3            the game clear (CallGameClear 0: Hall of Fame record, save, credits, THE END)
    mode 4            MEPlay 0x3A61 + MEWait
    mode 5            egg hatching: PokePartyAddEgg species (0x3A61), 120 frames (the harness sets the egg's hatch
                      counter, its friendship, to 0), then Black 2's hatch (CallEggHatch, as global script 1234)

Every mode first gives (Sub_Kit): a party when the party is empty (Mudkip Lv 100, Torchic Lv 15), the 8 badges, HM01-HM06,
TM70, TM94, the Bicycle, 10 Ultra Balls (music_more's after-capture test), and switches the Gen 6 Exp. Share on (FLAG_EXP_SHARE_ON 2058, exp_share.py), so a wild battle
won by the Mudkip lifts the Torchic past 16: Combusken's evolution.

    MUSIC_PATCHES="fairy hoenn_music test_music_kit" work/agents/music_check/build.sh   (after scripts and hm_free)
"""
import os, struct, importlib.util

_d = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('hm_free_mk', os.path.join(_d, 'hm_free.py'))
_hm = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_hm)

KIT = r'''
#include "asm/field_script.inc"
    ScriptEntry Script_1
    ScriptEntriesEnd
Script_1:
    ActorsPauseAll
    VMSleep 60                                  // the harness rewrites the placeholders now
    WorkSetConst 0x8004, 0x3A60                 // mode
    WorkSetConst 0x8005, 0x3A61                 // species / trainer / ME
    WorkSetConst 0x8006, 0x3A62                 // level
    VMCall Sub_Kit
    WorkCmpConst 0x8004, 1
    VMJumpIf CMP_EQ, L_Wild
    WorkCmpConst 0x8004, 2
    VMJumpIf CMP_EQ, L_Trainer
    WorkCmpConst 0x8004, 3
    VMJumpIf CMP_EQ, L_Clear
    WorkCmpConst 0x8004, 4
    VMJumpIf CMP_EQ, L_ME
    WorkCmpConst 0x8004, 5
    VMJumpIf CMP_EQ, L_Egg
    MapChangeCore 0x3A5A, 0x3A5B, 0x3A5D, 0x3A5C, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_Wild:
    CallWildBattle 0x8005, 0x8006, 0
    WildBattleIsVictory 0x8007
    CallWildBattleEnd
    ActorsUnpauseAll
    VMHalt
L_Trainer:
    TrainerBGMPlayPush 0x8005
    VMSleep 240
    CallTrainerBattle 0x8005, 0, 0
    TrainerBattleIsVictory 0x8007
    CallTrainerBattleEnd
    ActorsUnpauseAll
    VMHalt
L_Clear:
    CallGameClear 0
    VMHalt
L_ME:
    MEPlay 0x8005
    MEWait
    ActorsUnpauseAll
    VMHalt
L_Egg:
    PokePartyAddEgg 0x8007, 0x8005, 0
    VMSleep 120                                 // the harness zeroes the egg's hatch counter now
    WorkSetConst 0x8020, 0
    CallEggHatch 0x8020
    WorkSetConst 0x8020, 0
    ActorsUnpauseAll
    VMHalt
Sub_Kit:
    PokePartyGetCount 0x8000, 0
    WorkCmpConst 0x8000, 0
    VMJumpIf CMP_NE, L_HasParty
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 100
    PokePartyAdd 0x8001, SPECIES_TORCHIC, 0, 15
L_HasParty:
    FlagSet 2401
    FlagSet 2058
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
    ItemAdd ITEM_BICYCLE, 1, 0x8001
    ItemAdd ITEM_ULTRA_BALL, 10, 0x8001
    VMReturn
    .balign 4, 0
'''

# the placeholder words the harness looks for (each must occur once in the kit)
PLACEHOLDERS = dict(mode=0x3A60, arg=0x3A61, level=0x3A62, zone=0x3A5A, x=0x3A5B, y=0x3A5D, z=0x3A5C)


def apply(files):
    import narcio
    blob = _hm._assemble(KIT, {})
    for k, v in PLACEHOLDERS.items():
        assert blob.count(struct.pack('<H', v)) == 1, f'test_music_kit: placeholder {k} not unique'
    entries = narcio.load(files, 56)
    data = bytearray(entries[778])
    while len(data) % 4: data.append(0)
    base = len(data)
    kit1 = 4 + struct.unpack_from('<i', blob, 0)[0]
    data += blob
    struct.pack_into('<i', data, 0, base + kit1 - 4)          # Littleroot's entry 1 (the town sign) -> the kit
    entries[778] = bytes(data)
    narcio.save(files, 56, entries)
    return f'TEST ONLY: Littleroot town sign = the music test kit ({len(blob)} B at {base} of script 778)'
