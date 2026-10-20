// May's house 1F (zone 392). Room: data/interior_layouts/, people and signs: data/interiors/392.json.
// Messages: src/text/script/0621_mays_house_1f.txt (Sapphire's text, Gen 5 capitalisation).
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
    VMHalt                      // free

Script_2:                      // a girl's blackout at home (script_check 2026-10-08), unused since littleroot2 (2026-10-19):
    ActorsPauseAll              // Brendan's house's script 2 (RESPAWN_ZONE_INFO 0) now sends a girl to her bedroom (2F)
    PokePartyRecoverAll         // as Gen 3; kept as it was (heal, fade in)
    FadeInBlack
    FadeWait
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
#define HOUSE_BRENDAN 0
#include "scenes/players_house_1f.inc"
#if __has_include("scenes/players_house_1f_postgame.inc")
#include "scenes/players_house_1f_postgame.inc"
#endif
