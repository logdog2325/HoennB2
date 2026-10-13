"""HMs not required (decision 2026-10-06; notes/RESEARCH_EXPSHARE_HM.md).

Obstacles stay. As in Sapphire, a field move outside battle needs the Hoenn badge (pokeruby src/pokemon_menu.c:154-159,
728: field move i needs FLAG_BADGE01_GET + i; the tree/rock/boulder scripts check it first), and then a party Pokémon
that knows it OR the move's machine in the Bag. Badge index = Hoenn gym number - 1 (TrainerCardAddBadge in our gym
scripts).

    move        machine (Black 2 item id)   badge
    Cut         HM01 420                    0 Stone
    Flash       TM70 397                    1 Knuckle
    Rock Smash  TM94 619                    2 Dynamo
    Strength    HM04 423                    3 Heat
    Surf        HM03 422                    4 Balance
    Fly         HM02 421                    5 Feather
    Dive        HM06 425                    6 Mind
    Waterfall   HM05 424                    7 Rain

Data (apply):
 - a/0/5/6 entry 1243 = the global scripts 10000-10089 (GLOBAL_SCRIPT_TABLE entry 45, ov012 0x0216af98; messages
   a/0/0/3 file 433), rebuilt from the decomp's data/field_scripts/1243.s with: talk scripts 10000 (boulder), 10002
   (water), 10004 (tree), 10006 (waterfall), 10011 (dive) checking the badge, then a Pokémon, then the machine (the
   item path shows the player's name, no cut-in); new script 10016 = Rock Smash rock (Black 2 has none). Dive (dive
   agent): Sapphire's lines (DIVE_TEXT), and 10011/10012 surface when the player is diving (PlayerGetExState 3):
   FieldSetNextZone from the dive works + CallDiving 1 (b2tools/patches/dive.py fills the works). The
   party-menu scripts (10001, 10003, ...) are unchanged: the party menu itself is gated (below).
 - Rock Smash text: src/text/script/0433.txt (Black 2's file + Sapphire's three lines, ids 34-36). This patch installs
   it itself the way `text` does, so the patch order doesn't matter.
Code (apply_code; every site checked against the decomp's build bytes):
 - Party menu: ov165 0x0219d654 `bl CheckAllowHidenEvent` -> `bl HoennCheckHiden`: Cut, Surf, Waterfall, Strength,
   Fly, Flash and Dive return 2 without their badge, which the menu already answers with its own message 0x39 "This
   can't be used until a new Badge is obtained." (system text 178). Teleport, Dig, Sweet Scent, Chatter: unchanged.
 - arm9 PML_MoveIsHM 0x02026b18 -> `movs r0, #0; bx lr`: HM moves can be forgotten everywhere (move-forget screens
   ov207/ov287, the trade check in ov194 via doesPkmHaveTmMove).
 - ov036 CheckFieldEnvInteraction 0x02182ede: the "nobody knows Surf" branch -> nop, so facing surfable water always
   runs script 10002, which decides.
 - ov036 CheckAutoTileEvents 0x02182902: the "nobody knows Waterfall" branch -> nop: surfing down a waterfall needs no
   move and no badge, as in Sapphire (MB_WATERFALL is a forced south current, pokeruby
   src/field_player_avatar.c:137-157).
 - Flash: ov035 GameData_UpdateFlashStatus 0x0217e76e `bl FieldStatus_CheckFlashUsed` -> `bl HoennFlashUsed`: a dark
   zone is lit on entry when Flash was used OR TM70 + Knuckle Badge.
 - Surf landing (final_check 2026-10-08): ov036 CheckSurfExitEvent (0x02182cd4, from FieldEventProvider_Grid_CheckForEvent)
   lands a surfer on the tile in the key's direction (or the one beyond a shore, class 0x41/0x44) when its flags have
   neither bit 0 (solid) nor bit 1 (surfable) and no actor stands there - with no height or elevation test, so a surfer
   climbed onto Mr. Briney's jetty and Mossdeep's north bank (24 units up) and the Route 119/120 bridge decks, which
   Sapphire refuses (pokeruby field_player_avatar.c sub_8058EF0: only onto elevation 3). Black 2's own maps never need a
   rule: every landable tile next to surf water in a/0/0/8 is 0, 4 or 8 units above it (1,121 cells). Its two
   `bl GetTileTypeAtPos` (0x02182d14, 0x02182d40) -> `bl SurfLandingTileType`: the tile type with the solid flag added
   when the tile carries NOLAND (flag 0x4000, set by b2tools/terrain/heights.py step 12 on walkable tiles beside surf
   water whose Sapphire elevation is not 0, 1 or 3). Code in ITCM after hoenn_world's ZoneLookup (the same arena move),
   before roamers.
 - Fly: the Town Map key item opens in fly mode when HM02 + Feather Badge (ov012 0x0215bfdc), and picking a town from
   it flies like the party menu's Fly (ov012 0x0215c01e-0x0215c029).
 The new arm9 code goes in 0x02005080-0x02005123 (unreferenced SDK version strings; exp_share.py uses
 0x02005050-0x0200507f) and its badge table in the 16 zero bytes at 0x02005030 (unreferenced padding before them).

Test switch (test builds only): HOENN_TEST_HM=1 replaces Littleroot's scripts (778) and NPCs (zone 389) with a cut tree,
a boulder and a breakable rock, gives a test party (Torchic knows Rock Smash and Flash) and the machines, turns on the
field menu's POKEMON entry (flag 2401, set by Black 2's starter script 0854), makes Littleroot dark (a/1/4/9), and the
town sign gives all 8 badges. List the patch after `scripts` and `hoenn_world`.
"""
import os, re, struct, sys, subprocess, tempfile, importlib.util

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
LLVM = '/opt/homebrew/opt/llvm/bin'
_spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp_share.py'))
_es = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_es)
Thumb, _patch, _load, _save = _es.Thumb, _es._patch, _es._load, _es._save

# move: (machine item, badge index)
FIELD_MOVES = {
    'CUT': (420, 0), 'FLASH': (397, 1), 'ROCK_SMASH': (619, 2), 'STRENGTH': (423, 3),
    'SURF': (422, 4), 'FLY': (421, 5), 'DIVE': (425, 6), 'WATERFALL': (424, 7),
}
SCRIPT_FILE, MSG_FILE = 1243, 433
ROCK_SMASH_TEXT = [                       # Sapphire: pokeruby data/field_move_scripts.inc:117-122, Gen 5 capitalisation
    'This rock appears to be breakable.\\nWould you like to use Rock Smash?',
    '{0102:0} used Rock Smash!{be01}',
    "It's a rugged rock, but a Pokémon\\nmay be able to smash it.",
]

DIVE_TEXT = [                             # Sapphire: pokeruby data/field_move_scripts.inc:273-289 (dive agent)
    'The sea is deep here. A Pokémon may be\\nable to go underwater here.',
    'The sea is deep here.\\nWould you like to use Dive?',
    '{0102:0} used Dive.{be01}',
    'Light is filtering down from above.\\nA Pokémon may be able to surface here.',
    'Light is filtering down from above.\\nWould you like to use Dive?',
]
DIVE_MSG = ('MSG_DIVE_CANNOT', 'MSG_DIVE_PROMPT', 'MSG_DIVE_USED', 'MSG_DIVE_UP_CANNOT', 'MSG_DIVE_UP_PROMPT')

HM_SCRIPTS = r'''
// Global scripts 10000-10089 (a/0/5/6 entry 1243), Black 2's data/field_scripts/1243.s with the item path added
// (b2tools/patches/hm_free.py). Messages: a/0/0/3 file 433.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1    // 10000 boulder (talk)
    ScriptEntry Script_2    // 10001 Strength from the party menu
    ScriptEntry Script_3    // 10002 water (talk)
    ScriptEntry Script_4    // 10003 Surf from the party menu
    ScriptEntry Script_5    // 10004 cut tree (talk)
    ScriptEntry Script_6    // 10005 Cut from the party menu
    ScriptEntry Script_7    // 10006 waterfall (talk)
    ScriptEntry Script_8    // 10007 Waterfall from the party menu
    ScriptEntry Script_9    // 10008 Flash from the party menu
    ScriptEntry Script_10   // 10009 Teleport
    ScriptEntry Script_11   // 10010 Dig
    ScriptEntry Script_12   // 10011 dive spot (talk)
    ScriptEntry Script_13   // 10012 Dive from the party menu
    ScriptEntry Script_14   // 10013 Abyssal Ruins Flash
    ScriptEntry Script_15   // 10014 Abyssal Ruins Strength
    ScriptEntry Script_16   // 10015 surfing down a waterfall
    ScriptEntry Script_17   // 10016 breakable rock (talk) -- new
    ScriptEntry Script_18   // 10017 arrival fade-in after a scripted map change (story_fixups) -- new
    ScriptEntriesEnd
    WorkSetConst 0x8020, 0

L_0048:
    // "{move} can't be used if you have someone with you."
    SystemMsg 33, 2
    LastKeyWait
    InfoMsgClose
    VMReturn

Movement_0054:
    Move 162, 1
    MoveEnd

L_005C:
    PlayerSetSpecialSequence 128
    ActorCmdExec 255, Movement_0054
    ActorCmdWait
    VMReturn

L_006C:
    PlayerSetSpecialSequence 8
    VMReturn

// ---- item path helpers ---------------------------------------------------------------------------------------------
// In: 0x8030 machine item, 0x8031 badge index, 0x8032 move. Out: 0x8010 = party slot of a Pokémon that knows the move
// (0-5), 6 = no Pokémon but the machine in the Bag, 7 = can't. As in Sapphire, the badge is always required first.
// Uses 0x8033.
L_HMAccess:
    TrainerCardHasBadge 0x8033, 0x8031
    VMStackPush 0x8033
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_HMAccess_No           // (jumps when the comparison is false: no badge)
    PokePartyHasMoveAny 0x8010, 0x8032
    VMStackPush 0x8010
    VMStackPushConst 6
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_HMAccess_End          // a Pokémon knows it
    ItemCheckAmount 0x8030, 1, 0x8033
    VMStackPush 0x8033
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_HMAccess_No
    VMReturn
L_HMAccess_No:
    WorkSetConst 0x8010, 7
L_HMAccess_End:
    VMReturn

// Word 0 = the Pokémon's nickname (0x8010 < 6) or the player's name
L_HMUserName:
    VMStackPush 0x8010
    VMStackPushConst 6
    VMStackCmp CMP_LT
    VMJumpIf CMP_STACK, L_HMUserName_Player
    WordSetPartyPokeName 0, 0x8010
    VMReturn
L_HMUserName_Player:
    WordSetPlayerName 0
    VMReturn

// The Pokémon cut-in, only when a Pokémon is used
L_HMCutIn:
    VMStackPush 0x8010
    VMStackPushConst 6
    VMStackCmp CMP_LT
    VMJumpIf CMP_STACK, L_HMCutIn_End
    PlayHMCutInEffect 0x8010
L_HMCutIn_End:
    VMReturn

// 0x8034 = the party slot for CallWaterfall: the Pokémon's, or 0 on the item path (as script 10015 does)
L_HMSlotOrZero:
    WorkSetConst 0x8034, 0
    VMStackPush 0x8010
    VMStackPushConst 6
    VMStackCmp CMP_LT
    VMJumpIf CMP_STACK, L_HMSlotOrZero_End
    WorkGet 0x8034, 0x8010
L_HMSlotOrZero_End:
    VMReturn

// 0x8010 == 7 (no way to use the move) -> stack TRUE
L_IsBlocked:
    VMStackPush 0x8010
    VMStackPushConst 7
    VMStackCmp CMP_EQ
    VMReturn

// ---- 10000: boulder ------------------------------------------------------------------------------------------------
Script_1:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    FlagGet 2404, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_009D
    VMCall L_00ED
    VMJump L_00E7

L_009D:
    WorkSetConst 0x8030, HM_STRENGTH_ITEM
    WorkSetConst 0x8031, HM_STRENGTH_BADGE
    WorkSetConst 0x8032, MOVE_STRENGTH
    VMCall L_HMAccess
    VMStackPush 0x8010
    VMStackPushConst 7
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_00C2
    VMCall L_00F9
    VMJump L_00E7

L_00C2:
    // "It's a big boulder, but a Pokémon may be able to push it aside. Would you like to use Strength?"
    SystemMsg 6, 2
    YesNoWin 0x8033
    InfoMsgClose
    VMStackPush 0x8033
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_00E7
    VMCall L_0105

L_00E7:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_00ED:
    // "Strength made it possible to move boulders around."
    SystemMsg 9, 2
    LastKeyWait
    InfoMsgClose
    VMReturn

L_00F9:
    // "It's a big boulder, but a Pokémon may be able to push it aside."
    SystemMsg 8, 2
    LastKeyWait
    InfoMsgClose
    VMReturn

L_0105:
    FlagSet 2404
    Cmd_01DD 1, 70, 0
    VMCall L_HMUserName
    // "{user} used Strength!"
    SystemMsg 10, 2
    InfoMsgClose
    VMCall L_005C
    VMCall L_HMCutIn
    VMCall L_006C
    VMStackPush 0x8010
    VMStackPushConst 6
    VMStackCmp CMP_LT
    VMJumpIf CMP_STACK, L_0105_Item
    // "{Pokémon}'s Strength made it possible to move boulders around!"
    SystemMsg 11, 2
    VMJump L_0105_Done
L_0105_Item:
    // "Strength made it possible to move boulders around."
    SystemMsg 9, 2
L_0105_Done:
    LastKeyWait
    InfoMsgClose
    VMReturn

// ---- 10001: Strength from the party menu (unchanged) ---------------------------------------------------------------
Script_2:
    ActorsPauseAll
    FlagGet 2404, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0173
    VMCall L_00ED
    VMJump L_01A6

L_0173:
    FlagSet 2404
    Cmd_01DD 1, 70, 0
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 10, 2
    InfoMsgClose
    VMCall L_005C
    PlayHMCutInEffect 0x8000
    VMCall L_006C
    SystemMsg 11, 2
    LastKeyWait
    InfoMsgClose

L_01A6:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- 10002: water ---------------------------------------------------------------------------------------------------
// Black 2 only ran this when a Pokémon knew Surf (ov036 CheckFieldEnvInteraction, patched); with neither a Pokémon
// nor HM03 + badge nothing happens, as in Sapphire.
Script_3:
    ActorsPauseAll
    WorkSetConst 0x8030, HM_SURF_ITEM
    WorkSetConst 0x8031, HM_SURF_BADGE
    WorkSetConst 0x8032, MOVE_SURF
    VMCall L_HMAccess
    VMStackPush 0x8010
    VMStackPushConst 7
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_01D7
    VMJump L_0220

L_01D7:
    SEPlay SEQ_SE_MESSAGE
    VMStackPushFlag 2406
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_01FB
    WordSetMoveName 0, MOVE_SURF
    VMCall L_0048
    VMJump L_0220

L_01FB:
    // "The water is a deep blue... Would you like to surf on it?"
    SystemMsg 13, 2
    YesNoWin 0x8033
    InfoMsgClose
    VMStackPush 0x8033
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0220
    VMCall L_0232

L_0220:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_0232:
    VMCall L_HMUserName
    // "{user} used Surf!"
    SystemMsg 14, 2
    InfoMsgClose
    VMCall L_005C
    VMCall L_HMCutIn
    PlayerSetSpecialSequence 1
    CallSurf
    Cmd_01DD 1, 57, 0
    VMReturn

// ---- 10003: Surf from the party menu (unchanged) -------------------------------------------------------------------
Script_4:
    ActorsPauseAll
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 14, 2
    InfoMsgClose
    VMCall L_005C
    PlayHMCutInEffect 0x8000
    VMCall L_006C
    CallSurf
    Cmd_01DD 1, 57, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- 10004: cut tree ------------------------------------------------------------------------------------------------
Script_5:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    WorkSetConst 0x8030, HM_CUT_ITEM
    WorkSetConst 0x8031, HM_CUT_BADGE
    WorkSetConst 0x8032, MOVE_CUT
    VMCall L_HMAccess
    VMStackPush 0x8010
    VMStackPushConst 7
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_02BF
    VMCall L_02F0
    VMJump L_02EA

L_02BF:
    // "This tree looks like it can be cut down! Would you like to cut it?"
    SystemMsg 0, 2
    YesNoWin 0x8033
    VMStackPush 0x8033
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_02E8
    VMCall L_02FC
    VMJump L_02EA

L_02E8:
    InfoMsgClose

L_02EA:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_02F0:
    // "This tree looks like it can be cut down!"
    SystemMsg 2, 2
    LastKeyWait
    InfoMsgClose
    VMReturn

L_02FC:
    VMCall L_HMUserName
    // "{user} used Cut!"
    SystemMsg 1, 2
    InfoMsgClose
    VMCall L_005C
    VMCall L_HMCutIn
    VMCall L_006C
    CallCut
    Cmd_01DD 1, 15, 0
    VMSleep 3
    ActorDelete 0x8011
    SEPlay SEQ_SE_FLD_02
    VMSleep 1
    VMReturn

// ---- 10005: Cut from the party menu (unchanged) --------------------------------------------------------------------
Script_6:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 1, 2
    InfoMsgClose
    VMCall L_005C
    PlayHMCutInEffect 0x8000
    VMCall L_006C
    CallCut
    Cmd_01DD 1, 15, 0
    VMSleep 3
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8023, 0
    PlayerGetActorInFront 0x8022, 0x8023
    VMStackPush 0x8023
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_039B
    ActorDelete 0x8022

L_039B:
    WorkSetConst 0x8023, 0
    WorkSetConst 0x8022, 0
    SEPlay SEQ_SE_FLD_02
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- 10006: waterfall (going up) ------------------------------------------------------------------------------------
Script_7:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    WorkSetConst 0x8030, HM_WATERFALL_ITEM
    WorkSetConst 0x8031, HM_WATERFALL_BADGE
    WorkSetConst 0x8032, MOVE_WATERFALL
    VMCall L_HMAccess
    VMStackPush 0x8010
    VMStackPushConst 7
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_03DC
    VMCall L_042B
    VMJump L_0425

L_03DC:
    VMStackPushFlag 2406
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0400
    WordSetMoveName 0, MOVE_WATERFALL
    VMCall L_0048
    VMJump L_0425

L_0400:
    // "It's a large waterfall. Would you like to use Waterfall?"
    SystemMsg 23, 2
    YesNoWin 0x8033
    InfoMsgClose
    VMStackPush 0x8033
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0425
    VMCall L_0437

L_0425:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_042B:
    // "A wall of water is crashing down with a mighty roar."
    SystemMsg 25, 2
    LastKeyWait
    InfoMsgClose
    VMReturn

L_0437:
    VMCall L_HMUserName
    VMCall L_HMSlotOrZero
    // "{user} used Waterfall!"
    SystemMsg 24, 2
    InfoMsgClose
    VMCall L_005C
    VMCall L_HMCutIn
    VMCall L_006C
    CallWaterfall 0x8034
    Cmd_01DD 1, 127, 0
    VMReturn

// ---- 10007-10010 (unchanged) ----------------------------------------------------------------------------------------
Script_8:
    ActorsPauseAll
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 24, 2
    InfoMsgClose
    PlayHMCutInEffect 0x8000
    CallWaterfall 0x8000
    Cmd_01DD 1, 127, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_16:
    ActorsPauseAll
    CallWaterfall 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:
    ActorsPauseAll
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 27, 2
    InfoMsgClose
    VMCall L_005C
    PlayHMCutInEffect 0x8000
    VMCall L_006C
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_10:
    ActorsPauseAll
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 28, 2
    InfoMsgClose
    VMCall L_005C
    PlayHMCutInEffect 0x8000
    VMCall L_006C
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:
    ActorsPauseAll
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 29, 2
    InfoMsgClose
    VMCall L_005C
    PlayHMCutInEffect 0x8000
    VMCall L_006C
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- 10011: dive spot -----------------------------------------------------------------------------------------------
Script_12:
    ActorsPauseAll
    WorkSetConst 0x8030, HM_DIVE_ITEM
    WorkSetConst 0x8031, HM_DIVE_BADGE
    WorkSetConst 0x8032, MOVE_DIVE
    VMCall L_HMAccess
    PlayerGetExState 0x8035                     // 3 = diving: this is a spot to surface from (dive agent)
    VMStackPush 0x8010
    VMStackPushConst 7
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_053F
    WorkCmpConst 0x8035, 3
    VMJumpIf CMP_EQ, L_DiveUpCannot
    // Sapphire: "The sea is deep here. A Pokémon may be able to go underwater here."
    SystemMsg MSG_DIVE_CANNOT, 2
    LastKeyWait
    InfoMsgClose
    VMJump L_0599

L_DiveUpCannot:
    // Sapphire: "Light is filtering down from above. A Pokémon may be able to surface here."
    SystemMsg MSG_DIVE_UP_CANNOT, 2
    LastKeyWait
    InfoMsgClose
    VMJump L_0599

L_053F:
    VMStackPushFlag 2406
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0563
    WordSetMoveName 0, MOVE_DIVE
    VMCall L_0048
    VMJump L_0599

L_0563:
    WorkCmpConst 0x8035, 3
    VMJumpIf CMP_EQ, L_DiveUpPrompt
    // Sapphire: "The sea is deep here. Would you like to use Dive?"
    SystemMsg MSG_DIVE_PROMPT, 2
    VMJump L_DiveAsk
L_DiveUpPrompt:
    // Sapphire: "Light is filtering down from above. Would you like to use Dive?"
    SystemMsg MSG_DIVE_UP_PROMPT, 2
L_DiveAsk:
    YesNoWin 0x8033
    InfoMsgClose
    VMStackPush 0x8033
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0599
    VMCall L_HMUserName
    VMCall L_059F

L_0599:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_059F:
    // Sapphire: "{user} used Dive."
    SystemMsg MSG_DIVE_USED, 2
    InfoMsgClose
    PlayerGetExState 0x8035
    WorkCmpConst 0x8035, 3
    VMJumpIf CMP_EQ, L_DiveUp
    VMCall L_005C
    VMCall L_HMCutIn
    VMCall L_006C
    CallDiving 0
    Cmd_01DD 1, 291, 0
    VMReturn

// Surfacing (dive agent): Black 2's own surfacing is a script (Abyssal Ruins 0482.s Script_3: FieldSetNextZone, then
// CallDiving 1); where to comes from the dive table (b2tools/patches/dive.py), which the A-button / party-menu check
// (GetAbyssalRuinsDiveZoneID) has just looked up: the zone and tile of the surface above this spot
L_DiveUp:
    VMCall L_HMCutIn
    FieldSetNextZone VAR_HOENN_DIVE_ZONE, 0, VAR_HOENN_DIVE_X, 0, VAR_HOENN_DIVE_Z
    CallDiving 1
    VMReturn

// ---- 10012: Dive from the party menu (the Pokémon is in 0x8000) ----------------------------------------------------
Script_13:
    ActorsPauseAll
    WordSetPartyPokeName 0, 0x8000
    WorkGet 0x8010, 0x8000
    VMCall L_059F
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- 10013/10014: Abyssal Ruins (unchanged) -------------------------------------------------------------------------
Script_14:
    ActorsPauseAll
    FlagGet 215, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0616
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 27, 2
    InfoMsgClose
    VMCall L_005C
    PlayHMCutInEffect 0x8000
    VMCall L_006C

L_0616:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_15:
    ActorsPauseAll
    FlagGet 214, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0654
    WordSetPartyPokeName 0, 0x8000
    SystemMsg 10, 2
    InfoMsgClose
    VMCall L_005C
    PlayHMCutInEffect 0x8000
    VMCall L_006C

L_0654:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- 10016: breakable rock (new; Sapphire S_BreakableRock) ---------------------------------------------------------
// Black 2 has no Rock Smash field effect: the rock just disappears with a sound. Sapphire's rock-smash wild battles
// (ScrSpecial_RockSmashWildEncounter) are not done here.
Script_17:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    WorkSetConst 0x8030, HM_ROCK_SMASH_ITEM
    WorkSetConst 0x8031, HM_ROCK_SMASH_BADGE
    WorkSetConst 0x8032, MOVE_ROCK_SMASH
    VMCall L_HMAccess
    VMStackPush 0x8010
    VMStackPushConst 7
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_RS_Can
    // "It's a rugged rock, but a Pokémon may be able to smash it."
    SystemMsg MSG_RS_CANNOT, 2
    LastKeyWait
    InfoMsgClose
    VMJump L_RS_End

L_RS_Can:
    // "This rock appears to be breakable. Would you like to use Rock Smash?"
    SystemMsg MSG_RS_PROMPT, 2
    YesNoWin 0x8033
    InfoMsgClose
    VMStackPush 0x8033
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_RS_End
    VMCall L_HMUserName
    // "{user} used Rock Smash!"
    SystemMsg MSG_RS_USED, 2
    InfoMsgClose
    VMCall L_005C
    VMCall L_HMCutIn
    VMCall L_006C
    VMSleep 3
    ActorDelete 0x8011
    SEPlay SEQ_SE_FLD_02
    VMSleep 1

L_RS_End:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- 10017: arrival fade-in (new; story_fixups 2026-10-07) ----------------------------------------------------------
// A scripted map change (MapChangeCore) from a step trigger leaves the arrival zone's people dead (no talk, no trainer
// sight; the Gym guide of Lavaridge after a hole, Wattson after a barrier redraw; ch5, tested) unless it follows
// Black 2's own pattern: ActorsPauseAll, FadeOutBlack, RTReserveScript <script of the arrival zone>, FadeWait,
// MapChangeCore ..., and the reserved script fades back in (0240.s, 0926.s, 0904.s). RTReserveScript takes any script
// id, so this global one serves every room: generated ladders, holes, cracked floors (gyms_league_rooms.py,
// converter/gen_caves.py: ARRIVAL_SCRIPT) and the Mauville Gym's redraw reserve it.
Script_18:
    ActorsPauseAll
    FadeInBlack
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
'''

def _assemble(source, defines):
    with tempfile.TemporaryDirectory() as t:
        src, o, b = os.path.join(t, 'x.s'), os.path.join(t, 'x.o'), os.path.join(t, 'x.bin')
        open(src, 'w').write(source)
        args = [f'-D{k}={v}' for k, v in defines.items()]
        subprocess.run([f'{LLVM}/clang', '--target=armv5te-none-eabi', '-x', 'assembler-with-cpp', '-c', *args,
                        '-I', f'{DECOMP}/include', '-I', f'{DECOMP}/lib/nitro/include',
                        '-I', os.path.join(ROOT, 'src', 'include'), '-D', 'BLACK2', '-o', o, src], check=True, cwd=DECOMP)
        subprocess.run([f'{LLVM}/llvm-objcopy', '-O', 'binary', o, b], check=True)
        return open(b, 'rb').read()

def _rock_smash_ids(files=None):
    """Ids of the three Rock Smash lines in src/text/script/0433.txt; installs the file when `files` is given."""
    if files:
        _es.install_text(files, 'script', MSG_FILE)
    return [_es.message_id('script', MSG_FILE, t) for t in ROCK_SMASH_TEXT]

def apply(files):
    import narcio
    ids = _rock_smash_ids(files)
    defines = {f'HM_{m}_ITEM': item for m, (item, badge) in FIELD_MOVES.items()}
    defines.update({f'HM_{m}_BADGE': badge for m, (item, badge) in FIELD_MOVES.items()})
    defines.update(MSG_RS_PROMPT=ids[0], MSG_RS_USED=ids[1], MSG_RS_CANNOT=ids[2])
    defines.update({k: _es.message_id('script', MSG_FILE, t) for k, t in zip(DIVE_MSG, DIVE_TEXT)})
    entries = narcio.load(files, 56)
    entries[SCRIPT_FILE] = _assemble(HM_SCRIPTS, defines)
    narcio.save(files, 56, entries)
    done = f'scripts {SCRIPT_FILE} ({len(entries[SCRIPT_FILE])} B, 10000-10017), Rock Smash text {ids} (src/text)'
    if os.environ.get('HOENN_TEST_HM'):
        _test_setup(files); done += ', TEST setup in Littleroot'
    return done

# ---- code ------------------------------------------------------------------------------------------------------------
ARM9, OV012, OV035, OV036, OV165 = 0x02004000, 0x021503C0, 0x0217C940, 0x0217F600, 0x02199A00  # overlays.yaml
HELPERS = (0x02005080, 0x02005124)        # arm9: unreferenced SDK version strings (exp_share.py has 0x02005050-7f)
BADGE_TABLE = (0x02005030, 0x02005040)    # arm9: 16 unreferenced zero bytes just before them
SaveControl_GetInstance, SaveControl_GetBlockPtr = 0x020072FC, 0x02007448
BagSave_CheckAmount, getTrainerGameInfoAddress, isBadgeObtained = 0x02008474, 0x0200C838, 0x0200C97C
FieldStatus_CheckFlashUsed, GetZoneFlagsEnableFlyFrom = 0x02019330, 0x020189CC
CheckAllowHidenEvent, PARTY_MENU_HIDEN_CHECK = 0x021593FC, 0x0219D654   # ov012; its only call, in ov165
BLOCK_BAG = 0x19                           # GameData_Create: gameData->bag = SaveControl_GetBlockPtr(save, 0x19)
FIELD_APP_BAG = 2
# hidden-move kinds (ov012 HIDEN_EVENTS_NORMAL order, hiden_event.c:20-32) that need a badge; the rest (6 Teleport,
# 7 Dig, 8 Sweet Scent, 9 Chatter) need none, as in Sapphire
HIDEN_KIND_MOVE = {0: 'CUT', 1: 'SURF', 2: 'WATERFALL', 3: 'STRENGTH', 4: 'FLY', 5: 'FLASH', 10: 'DIVE'}

def badge_table():
    return bytes(FIELD_MOVES[HIDEN_KIND_MOVE[k]][1] if k in HIDEN_KIND_MOVE else 0xFF for k in range(11))

def helpers():
    """HoennHasItemAndBadge(item, badge), HoennFlashUsed(status), HoennTownMapMode(input), HoennCheckHiden(kind, ctx)."""
    t = Thumb(HELPERS[0])
    # BOOL HoennHasItemAndBadge(u16 item, u32 badge): the trainer card has the badge, and item == 0 or the bag holds it
    t.label('has'); t.push([4, 5, 6])
    t.mov(4, 0); t.mov(5, 1)
    t.bl(SaveControl_GetInstance); t.mov(6, 0)
    t.bl(getTrainerGameInfoAddress)                                 # = getTrainerCardDataBlkAddress(gameData)
    t.mov(1, 5); t.bl(isBadgeObtained)
    t.cmp(0, 0); t.beq('has_end')
    t.cmp(4, 0); t.beq('has_end')                                   # badge only (r0 = 1)
    t.mov(0, 6); t.movs(1, BLOCK_BAG); t.bl(SaveControl_GetBlockPtr)
    t.mov(1, 4); t.movs(2, 1); t.bl(BagSave_CheckAmount)            # (bag, item, 1, heap: unused)
    t.label('has_end'); t.pop([4, 5, 6])
    # BOOL HoennFlashUsed(FieldStatus *status): Flash used in this zone, or TM70 + Knuckle Badge
    t.label('flash'); t.push([4])
    t.bl(FieldStatus_CheckFlashUsed)
    t.cmp(0, 0); t.bne('flash_end')
    t.ldr_lit(0, 'tm70'); t.movs(1, FIELD_MOVES['FLASH'][1])
    t.bl_label('has')
    t.label('flash_end'); t.pop([4])
    # u32 HoennTownMapMode(FieldAppCallInput *input): 0 = fly mode (party Fly, or the bag's Town Map with HM02 + Feather
    # Badge), else view mode; returns with the flags of `cmp r0, #0` (the caller branches on them)
    # Called only from func_ov012_0215bf8c, where r4 = the TownMapParam (zoneId at +8, already set).
    t.label('townmap'); t.push([4, 5])
    t.ldrh_off(5, 4, 8)                                             # param->zoneId
    t.ldr_off(4, 0, 16)                                             # input->appId
    t.cmp(4, 0); t.beq('tm_end')
    t.cmp(4, FIELD_APP_BAG); t.bne('tm_end')
    t.mov(0, 5); t.bl(GetZoneFlagsEnableFlyFrom)                    # the party menu's Fly checks this too
    t.cmp(0, 0); t.beq('tm_end')
    t.ldr_lit(0, 'hm02'); t.movs(1, FIELD_MOVES['FLY'][1])
    t.bl_label('has')
    t.cmp(0, 1); t.bne('tm_end')
    t.movs(4, 0)
    t.label('tm_end'); t.mov(0, 4); t.cmp(0, 0); t.pop([4, 5])
    # u32 HoennCheckHiden(u32 kind, ctx): the party menu's field-move check; 2 = "This can't be used until a new Badge
    # is obtained." when the kind's badge is missing, else Black 2's CheckAllowHidenEvent(kind, ctx)
    t.label('hiden'); t.push([4, 5])
    t.mov(4, 0); t.mov(5, 1)
    t.ldr_lit(1, 'badges'); t.ldrb_rr(1, 1, 0)                      # kinds are 0-10 here (option id - 11)
    t.cmp(1, 0xFF); t.beq('hv')
    t.movs(0, 0); t.bl_label('has')                                 # badge only
    t.cmp(0, 0); t.bne('hv')
    t.movs(0, 2); t.pop([4, 5])
    t.label('hv'); t.mov(0, 4); t.mov(1, 5); t.bl(CheckAllowHidenEvent)
    t.pop([4, 5])
    t.word('tm70', FIELD_MOVES['FLASH'][0])
    t.word('hm02', FIELD_MOVES['FLY'][0])
    t.word('badges', BADGE_TABLE[0])
    code = t.assemble()
    assert len(code) <= HELPERS[1] - HELPERS[0], len(code)
    return code, {k: t.labels[k] for k in ('has', 'flash', 'townmap', 'hiden')}

def _bl(src, dst):
    off = dst - (src + 4)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)

# ---- surf landing (final_check 2026-10-08; see the docstring) --------------------------------------------------------
ITCM_BASE, ARENA_ITCM_LIT = 0x01FF8000, 0x0207B400          # (patches/hoenn_world.py: the ITCM autoload and its arena)
GetTileTypeAtPos, FieldG3DMapper_GetTerrain = 0x021A29D0, 0x02185170
SURF_EXIT_TILE_CALLS = (0x02182D14, 0x02182D40)            # ov036 CheckSurfExitEvent
NOLAND = 0x4000                                             # b2tools/terrain/heights.py (collision flag, u32 bit 30)

def surf_landing(base):
    """u32 SurfLandingTileType(FieldG3DMapper *mapper, const VecFx32 *pos): GetTileTypeAtPos (MapTerrainBuf: tileType
    at +8; 0xFFFFFFFF where there is no terrain), with the solid flag (bit 16) added when the tile has NOLAND."""
    t = Thumb(base)
    t.push([3]); t.h(0xB084)                                    # push {r3, lr} (8-byte stack, as the original); sub sp, #16
    t.h(0xAA00)                                                 # add r2, sp, #0
    t.bl(FieldG3DMapper_GetTerrain)
    t.cmp(0, 1); t.bne('fail')
    t.ldr_sp(0, 8)                                              # tileType
    t.ldr_lit(1, 'noland'); t.tst(0, 1); t.beq('done')
    t.movs(1, 1); t.lsls(1, 1, 16); t.orrs(0, 1)                # solid: no landing there
    t.label('done'); t.h(0xB004); t.pop([3])                    # add sp, #16; pop {r3, pc}
    t.label('fail'); t.movs(0, 0); t.h(0x43C0)                  # 0xFFFFFFFF (mvns r0, r0), as GetTileTypeAtPos
    t.h(0xB004); t.pop([3])
    t.word('noland', NOLAND << 16)
    return t.assemble()

def apply_surf_landing(code):
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    assert re.search(r'^bss_size: 0$', text, re.M), 'ITCM autoload has a bss'
    base = ITCM_BASE + size
    path9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, f'ITCM arena literal {struct.unpack_from("<I", arm9, lit)[0]:#x} != {base:#x}'
    blob = surf_landing(base)
    end = (base + len(blob) + 31) & ~31
    struct.pack_into('<I', arm9, lit, end); _save(path9, arm9)
    path, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(path, bytes(itcm) + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    path, d = _load(code, 'arm9_ov036.bin')
    for at in SURF_EXIT_TILE_CALLS:
        _patch(d, OV036, at, _bl(at, GetTileTypeAtPos), _bl(at, base), 'CheckSurfExitEvent tile type')
    _save(path, d)
    return f'surf landing: SurfLandingTileType {len(blob)} B at {base:#x} (ITCM arena from {end:#x})'

def apply_code(code):
    vanilla = os.path.join(DECOMP, 'build', 'b2_us', 'build')
    # arm9: PML_MoveIsHM -> return FALSE; helpers in the SDK strings, badge table in the zero bytes before them
    path, d = _load(code, 'arm9.bin')
    _patch(d, ARM9, 0x02026B18, bytes.fromhex('084a0023'), bytes.fromhex('00207047'), 'PML_MoveIsHM')
    blob, at = helpers()
    lo, hi = HELPERS
    orig = open(os.path.join(vanilla, 'arm9.bin'), 'rb').read()
    assert b'[SDK+' in orig[lo - ARM9:hi - ARM9]                    # the decomp's bytes: version strings
    _patch(d, ARM9, lo, orig[lo - ARM9:hi - ARM9], blob + bytes(hi - lo - len(blob)), 'SDK strings -> HM helpers')
    tlo, thi = BADGE_TABLE
    assert orig[tlo - ARM9:thi - ARM9] == bytes(thi - tlo)          # zero padding
    _patch(d, ARM9, tlo, bytes(thi - tlo), badge_table() + bytes(thi - tlo - 11), 'zero bytes -> badge table')
    _save(path, d)
    # ov165: the party menu's field moves need their badge
    path, d = _load(code, 'arm9_ov165.bin')
    _patch(d, OV165, PARTY_MENU_HIDEN_CHECK, _bl(PARTY_MENU_HIDEN_CHECK, CheckAllowHidenEvent),
           _bl(PARTY_MENU_HIDEN_CHECK, at['hiden']), 'party menu field-move check')
    _save(path, d)
    # ov036: Surf prompt and waterfall descent no longer need a Pokémon that knows the move
    path, d = _load(code, 'arm9_ov036.bin')
    _patch(d, OV036, 0x02182EDE, bytes.fromhex('02d0'), bytes.fromhex('c046'), 'CheckFieldEnvInteraction Surf')
    _patch(d, OV036, 0x02182902, bytes.fromhex('29d0'), bytes.fromhex('c046'), 'CheckAutoTileEvents Waterfall')
    _save(path, d)
    # ov035: Flash
    path, d = _load(code, 'arm9_ov035.bin')
    _patch(d, OV035, 0x0217E76E, _bl(0x0217E76E, FieldStatus_CheckFlashUsed), _bl(0x0217E76E, at['flash']),
           'GameData_UpdateFlashStatus')
    _save(path, d)
    # ov012: Fly from the Town Map
    path, d = _load(code, 'arm9_ov012.bin')
    _patch(d, OV012, 0x0215BFDC, bytes.fromhex('00690028'), _bl(0x0215BFDC, at['townmap']), 'town map mode')
    # bag branch of the town map result: keep the param in r1 (result in r2) and send result 2 to the party branch's
    # "cmp r2, #2" at 0x0215c048 (fly to param->zoneId); 0 = back to the bag, 1 = close stay as they were
    _patch(d, OV012, 0x0215C01E, bytes.fromhex('4968' '0029' '02d0' '0129' '04d0' '05e0'),
           bytes.fromhex('4a68' '002a' '02d0' '012a' '04d0' '0ee0'), 'town map result (bag)')
    _save(path, d)
    landing = apply_surf_landing(code)
    return (f'{landing}; PML_MoveIsHM -> FALSE; helpers at {lo:#x} ({len(blob)}/{hi - lo} B: has {at["has"]:#x}, flash '
            f'{at["flash"]:#x}, townmap {at["townmap"]:#x}, hiden {at["hiden"]:#x}); badge table {badge_table().hex()} at '
            f'{tlo:#x}; party menu gated; Surf/Waterfall party checks off; Flash and Town Map Fly hooks')

# ---- test setup (HOENN_TEST_HM=1) ------------------------------------------------------------------------------------
TEST_SCRIPT = r'''
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
    // TEST ONLY: the town sign gives all 8 badges
    ActorsPauseAll
    TrainerCardAddBadge 0
    TrainerCardAddBadge 1
    TrainerCardAddBadge 2
    TrainerCardAddBadge 3
    TrainerCardAddBadge 4
    TrainerCardAddBadge 5
    TrainerCardAddBadge 6
    TrainerCardAddBadge 7
    SEPlay SEQ_SE_MESSAGE
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
Script_2:
Script_3:
Script_4:
Script_5:
Script_6:
Script_7:
Script_8:
    VMHalt
Script_9:
    // TEST ONLY (HOENN_TEST_HM): Littleroot's map-load script gives a test party and the machines once
    PokePartyGetCount 0x8000, 0
    VMStackPush 0x8000
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Done
    PokePartyAdd 0x8001, SPECIES_TREECKO, 0, 5
    PokePartyAdd 0x8001, SPECIES_TORCHIC, 0, 5
    PokePartyLearnMove 0, 2, MOVE_SURF          // Treecko: Pound, Leer, Surf, Absorb (an HM in a full move set)
    PokePartyLearnMove 0, 3, MOVE_ABSORB
    PokePartyLearnMove 1, 2, MOVE_ROCK_SMASH    // Torchic knows Rock Smash (script 10016) and Flash (party menu)
    PokePartyLearnMove 1, 3, MOVE_FLASH
    FlagSet 2401                                // Black 2's "has a Pokémon" flag: the field menu shows POKEMON
    ItemAdd ITEM_HM01, 1, 0x8001
    ItemAdd ITEM_HM04, 1, 0x8001
    ItemAdd ITEM_TM70, 1, 0x8001
    ItemAdd ITEM_HM02, 1, 0x8001
    ItemAdd ITEM_TOWN_MAP, 1, 0x8001
L_Done:
    VMHalt
    .balign 4, 0
'''

def _test_setup(files):
    import narcio
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    from zones import parse_entities, build_entities, zone_headers
    entries = narcio.load(files, 56)
    entries[778] = _assemble(TEST_SCRIPT, {})
    narcio.save(files, 56, entries)
    # Littleroot's three NPCs -> a cut tree (model 0x6c, script 10004), a boulder (0x2005, 10000) and a rock (0x2003,
    # 10016), standing still (move 0)
    ents = narcio.load(files, 126)
    idx = zone_headers()[389]['entities']
    e, _ = parse_entities(ents[idx])
    for npc, model, script in zip(e['npcs'], (0x2005, 0x6C, 0x2003), (10000, 10004, 10016)):
        npc.update(model=model, script=script, move=0)
    ents[idx] = build_entities(e, ents[idx])
    narcio.save(files, 126, ents)
    # Littleroot dark (zone flash table a/1/4/9: {u16 zone, u16 flags}, flags 1 = dark until Flash)
    fl = narcio.load(files, 149)
    if struct.pack('<HH', 389, 1) not in fl[0]:
        fl[0] = fl[0] + struct.pack('<HH', 389, 1)
    narcio.save(files, 149, fl)
