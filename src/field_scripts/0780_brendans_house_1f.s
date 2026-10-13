// Brendan's house 1F (zone 390). Room: data/interior_layouts/, people and signs: data/interiors/390.json.
// Messages: src/text/script/0619_brendans_house_1f.txt (Sapphire's text, Gen 5 capitalisation).
// Actors = Sapphire local ids: 1 Mom (script 26), 2/3 the movers (Machoke in Sapphire; 27, 28), 4 the rival's mom (29),
// 5 Norman (5). Scripts 20-31 are the lead's story scenes; 26-29 hold the simple Sapphire lines as placeholders until then.
// Map scripts (zone init) are the lead's src/field_scripts/07NN_*_init.s; Black 2's own init tables only call free stubs.
// VMJumpIf CMP_STACK jumps when the comparison is FALSE.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntry Script_10
    ScriptEntry Script_11
    ScriptEntry Script_12
    ScriptEntry Script_13
    ScriptEntry Script_14
    ScriptEntry Script_15
    ScriptEntry Script_16
    ScriptEntry Script_17
    ScriptEntry Script_18
    ScriptEntry Script_19
    ScriptEntry Script_20
    ScriptEntry Script_21
    ScriptEntry Script_22
    ScriptEntry Script_23
    ScriptEntry Script_24
    ScriptEntry Script_25
    ScriptEntry Script_26
    ScriptEntry Script_27
    ScriptEntry Script_28
    ScriptEntry Script_29
    ScriptEntry Script_30
    ScriptEntry Script_31
    ScriptEntriesEnd

Script_1:
Script_2:                      // the blackout at home (script_check 2026-10-08). Black 2's EventBattleLose (ov012
    ActorsPauseAll              // event_battle_lose.c) runs local script 2 of the respawn zone instead of the Centers'
    TrainerCardGetSex 0x8030    // global 2001 when IsReturnLocationNonLeaguePokeCen is FALSE, which it is for the
    WorkCmpConst 0x8030, 1      // new game's respawn point, this room (RESPAWN_ZONE_INFO 0: zone 390 (6,8)). A VMHalt
    VMJumpIf CMP_EQ, L_BlackoutMay  // here left the screen black for good after any battle lost before a Pokémon Center
    PokePartyRecoverAll         // or after the Hall of Fame (h_setrespawn 1). Sapphire's whiteout heals the party and
    FadeInBlack                 // shows the player at home with no line (overworld.c DoWhiteOut).
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_BlackoutMay:                  // a girl's home is May's house (Sapphire: HEAL_LOCATION_LITTLEROOT_TOWN_MAYS_HOUSE_2F):
    FadeOutBlack                // on to the same tile there (the rooms mirror each other); its script 2 heals and
    RTReserveScript 2           // fades in (0784_mays_house_1f.s), still on the black screen of the blackout
    FadeWait
    MapChangeCore 392, 6, 0, 8, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:
Script_4:
    VMHalt                      // free

Script_5:                      // Norman: no script in Sapphire; turns to face you
    ActorsPauseAll
    ActorSetEyeToEye
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                      // TV (sign, read facing north)
    ActorsPauseAll
#if __has_include("scenes/players_house_1f_postgame.inc")
    VMCall Sub_PG_TVNews        // post-game: Sapphire's Lati news after the Hall of Fame (scenes/players_house_1f_postgame.inc)
    WorkCmpConst 0x8030, 1      // (1: the news was shown)
    VMJumpIf CMP_EQ, L_TVDone
#endif
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 4, 2
    LastKeyWait
    MsgWinCloseAll
L_TVDone:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

#ifndef HOENN_EMERALD            // Emerald: scenes/emerald/players_house_1f.inc defines 7-10 (the rival's meeting, the sibling)
Script_7:
Script_8:
Script_9:
Script_10:
#endif
Script_11:
Script_12:
Script_13:
Script_14:
Script_15:
Script_16:
Script_17:
Script_18:
    VMHalt                      // free
// Script_19: the Running Shoes manual (chapter Ch1), in scenes/players_house_1f.inc

#if !__has_include("scenes/players_house_1f_ch13.inc")
Script_30:                      // Ch13: the S.S. Ticket scene is scenes/players_house_1f_ch13.inc (included by players_house_1f.inc)
#endif
Script_31:
    VMHalt

#define T_BASE 5
#define HOUSE_BRENDAN 1
#include "scenes/players_house_1f.inc"
#if __has_include("scenes/players_house_1f_postgame.inc")
#include "scenes/players_house_1f_postgame.inc"
#endif
