// ShoalCave_LowTideInnerRoom (zone 146): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch9
#include "hoenn_key_items.h"  // ch9
#include "hoenn_story.inc"  // ch9

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry SI_Salt1  // 5: sign (31,8) + object  // story:
    ScriptEntry SI_Salt2  // 6: sign (14,26) + object  // story:
    ScriptEntry SI_Shell1  // 7: sign (41,20) + object  // story:
    ScriptEntry SI_Shell2  // 8: sign (41,10) + object  // story:
    ScriptEntry SI_Shell3  // 9: sign (6,9) + object  // story:
    ScriptEntry SI_Shell4  // 10: sign (16,13) + object  // story:
    ScriptEntry SI_Init  // 11: zone init (OnTransition/OnLoad, then script 4)  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder down (38,15) -> ShoalCave_LowTideStairsRoom warp 0 (3,12)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 163, 3, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (42,4) -> ShoalCave_LowTideStairsRoom warp 1 (7,4)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 163, 7, 4, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // ladder down (19,14) -> ShoalCave_LowTideLowerRoom warp 0 (7,2)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 162, 7, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // zone init: inside the cave (tide kept)
    MapReplaceSetEvent 8, 1, 0
    MapReplaceIsEventSet 9, 0x8002
    WorkCmpConst 0x8002, 0
    VMJumpIf CMP_EQ, L_TideDone
    ObjInitWarpGPos 0, 0, 0, 0
    ObjInitWarpGPos 1, 0, 0, 0
    ObjInitWarpGPos 4, 0, 0, 0
    ObjInitWarpGPos 5, 0, 0, 0
L_TideDone:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch9, ch9 agent 2026-10-07; Sapphire data/maps/ShoalCave_LowTideInnerRoom/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). Scripts 5-11, text lines 0-2 of 0165. Salt 1 (31,8) and
// salt 2 (14,26), shells 1-4 (41,20) (41,10) (6,9) (16,13): a Poké Ball object (uid 2-7, hidden by FLAG_HIDE_TOOK_SHOAL_*) and
// a sign on the same tile, both running the pickup script (data/story/ch9.json). Room tiles = Sapphire tiles + (9, 13).
// Sapphire draws the salt piles only at low tide (OnLoad: not FLAG_SYS_SHOAL_TIDE): at high tide the two salt objects are
// moved off the map by the zone init (script 11, which then runs the generator's script 4: the tide).
#include "scenes/ch9_lib.inc"
#define T_NothingShell 0
#define T_NothingSalt 1
#define T_BagFull 2

SI_Salt1:                               // ShoalCave_LowTideInnerRoom_EventScript_15E329
    c9_shoal_pickup ITEM_SHOAL_SALT, FLAG_HIDE_TOOK_SHOAL_SALT_1, 2, T_NothingSalt, T_BagFull
SI_Salt2:                               // ..._EventScript_15E365
    c9_shoal_pickup ITEM_SHOAL_SALT, FLAG_HIDE_TOOK_SHOAL_SALT_2, 3, T_NothingSalt, T_BagFull
SI_Shell1:                              // ..._EventScript_15E257
    c9_shoal_pickup ITEM_SHOAL_SHELL, FLAG_HIDE_TOOK_SHOAL_SHELL_1, 4, T_NothingShell, T_BagFull
SI_Shell2:                              // ..._EventScript_15E293
    c9_shoal_pickup ITEM_SHOAL_SHELL, FLAG_HIDE_TOOK_SHOAL_SHELL_2, 5, T_NothingShell, T_BagFull
SI_Shell3:                              // ..._EventScript_15E2C5
    c9_shoal_pickup ITEM_SHOAL_SHELL, FLAG_HIDE_TOOK_SHOAL_SHELL_3, 6, T_NothingShell, T_BagFull
SI_Shell4:                              // ..._EventScript_15E2F7
    c9_shoal_pickup ITEM_SHOAL_SHELL, FLAG_HIDE_TOOK_SHOAL_SHELL_4, 7, T_NothingShell, T_BagFull

SI_Init:                                // ShoalCave_LowTideInnerRoom_MapScript1_15E1B3 (OnLoad: the piles) + the generator's script 4
    MapReplaceIsEventSet 9, C9_A        // 1 = high tide
    h_goto_if_eq C9_A, 0, L_SI_LowTide
    ObjInitNPCGPos 1, 1, 0, 0, 0        // salt 1 (object index 1: after the Rare Candy ball) off the map
    ObjInitNPCGPos 2, 1, 0, 0, 0        // salt 2
L_SI_LowTide:
    VMJump Script_4
    .balign 4, 0
