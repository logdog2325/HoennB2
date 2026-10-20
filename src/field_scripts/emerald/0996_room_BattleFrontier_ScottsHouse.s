// BattleFrontier_ScottsHouse (zone 498; header scripts 996 -> own file 2096), Pokémon Emerald NDS only (frontier_lounges,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_ScottsHouse/scripts.inc: Scott. First visit: his welcome and 1-4
// Battle Points by how often you met him on the journey (VAR_SCOTT_STATE 13 / >= 9 / >= 6 / else). Later: the Lansat
// Berry for all seven Silver Symbols, the Starf Berry for all seven Gold Symbols (FR_SYMBOLS, notes/FRONTIER.md 2.2), the
// Silver / Gold Shield for 50 / 100 Battle Tower wins in a row (Lv. 50 or Open Level: VAR_BT_LAST_STREAK_LV50 / LV100,
// the tower's current streak), else one of three random lines. The shields are decorations, which Black 2 does not have:
// as the Battle Tower lobby's award man does (0042_room_BattleTower_Lobby.s), Scott says his lines and the shield's flag
// is set, no item is given. FLAG_TEMP_2/3/4 = map-local flags 0x22-0x24 (Black 2 clears 0-0x63 on every map change).
// The room: data/interior_layouts/BattleFrontier_ScottsHouse.json, people data/interiors/emerald/498.json.
// Messages: src/text/script/emerald/0298_room_BattleFrontier_ScottsHouse.txt (lounge_rooms.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"

#define T_Welcome 0
#define T_Effort 1
#define T_Memento 2
#define T_ObtainedBP 3                  // {player} obtained {N} Battle Point(s).
#define T_ExplainBP 4
#define T_ExpectingGreat 5
#define T_WhyISeek 6
#define T_MetBrain 7
#define T_WildMons 8
#define T_AllSilver 9
#define T_AllGold 10
#define T_SoGlad 11
#define T_BerryFull 12
#define T_Beat50 13
#define T_Beat100 14
#define T_EvenGreater 15
#define T_ComeBack 16
#define SH_SCOTT 1
#define SH_TEMP_2 0x22                  // FLAG_TEMP_2: Battle Points given this visit
#define SH_TEMP_3 0x23                  // FLAG_TEMP_3: a shield given this visit
#define SH_TEMP_4 0x24                  // FLAG_TEMP_4: a Berry given this visit
#define SH_V 0x8020
#define SH_BP 0x8021

    ScriptEntry SH_Scott                // 1: BattleFrontier_ScottsHouse_EventScript_Scott (2,3)
    ScriptEntriesEnd

SH_Scott:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set SH_TEMP_4, L_SH_GivenBerry
    h_goto_if_set SH_TEMP_3, L_SH_GivenShield
    h_goto_if_set SH_TEMP_2, L_SH_GivenBP
    h_goto_if_unset FLAG_SCOTT_GIVES_BATTLE_POINTS, L_SH_Welcome      // CheckGiveItems
    h_goto_if_unset FLAG_COLLECTED_ALL_SILVER_SYMBOLS, L_SH_CheckSilver
    h_goto_if_unset FLAG_COLLECTED_ALL_GOLD_SYMBOLS, L_SH_CheckGold
L_SH_CheckShield:
    h_goto_if_unset FLAG_RECEIVED_SILVER_SHIELD, L_SH_CheckSilverShield
    h_goto_if_unset FLAG_RECEIVED_GOLD_SHIELD, L_SH_CheckGoldShield
L_SH_Random:                            // RandomComment
    h_random SH_V, 3
    h_goto_if_eq SH_V, 1, L_SH_Brain
    h_goto_if_eq SH_V, 2, L_SH_Cave
    h_msgbox T_WhyISeek
    h_release
L_SH_Brain:
    h_msgbox T_MetBrain
    h_release
L_SH_Cave:
    h_msgbox T_WildMons
    h_release

L_SH_CheckSilver:                       // all seven Silver Symbols (a Gold Symbol's facility has its Silver too)
    .irp f, 0,1,2,3,4,5,6
    FrGet FR_GET_SYMBOL|\f,SH_V
    h_goto_if_eq SH_V, 0, L_SH_CheckShield
    .endr
    h_msgbox T_AllSilver
    h_closemessage
    h_giveitem ITEM_LANSAT_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_SH_BerryFull
    h_setflag FLAG_COLLECTED_ALL_SILVER_SYMBOLS
    h_setflag SH_TEMP_4
    h_release

L_SH_CheckGold:                         // all seven Gold Symbols
    .irp f, 0,1,2,3,4,5,6
    FrGet FR_GET_SYMBOL|\f,SH_V
    h_goto_if_ne SH_V, 2, L_SH_CheckShield
    .endr
    h_msgbox T_AllGold
    h_closemessage
    h_giveitem ITEM_STARF_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_SH_BerryFull
    h_setflag FLAG_COLLECTED_ALL_GOLD_SYMBOLS
    h_setflag SH_TEMP_4
    h_release

L_SH_BerryFull:
    h_msgbox T_BerryFull
    h_release

L_SH_GivenBerry:
    h_msgbox T_SoGlad
    h_release

L_SH_CheckSilverShield:                 // 50 Battle Tower wins in a row, Lv. 50 or Open Level
    h_goto_if_ge VAR_BT_LAST_STREAK_LV50, 50, L_SH_SilverShield
    h_goto_if_ge VAR_BT_LAST_STREAK_LV100, 50, L_SH_SilverShield
    VMJump L_SH_Random
L_SH_SilverShield:
    h_msgbox T_Beat50
    h_setflag FLAG_RECEIVED_SILVER_SHIELD   // givedecoration DECOR_SILVER_SHIELD: no decorations in Black 2
    h_setflag SH_TEMP_3
    VMJump L_SH_GivenShield
L_SH_CheckGoldShield:
    h_goto_if_ge VAR_BT_LAST_STREAK_LV50, 100, L_SH_GoldShield
    h_goto_if_ge VAR_BT_LAST_STREAK_LV100, 100, L_SH_GoldShield
    VMJump L_SH_Random
L_SH_GoldShield:
    h_msgbox T_Beat100
    h_setflag FLAG_RECEIVED_GOLD_SHIELD     // givedecoration DECOR_GOLD_SHIELD
    h_setflag SH_TEMP_3
L_SH_GivenShield:
    h_msgbox T_EvenGreater
    h_release

L_SH_GivenBP:
    h_msgbox T_ExpectingGreat
    h_release

L_SH_Welcome:                           // WelcomeToFrontier
    h_buffer_player
    h_msgbox T_Welcome
    h_closemessage
    h_delay 30
    h_getplayerfacing SH_V              // Scott looks the way the player faces (away from the player)
    h_goto_if_eq SH_V, 0, L_SH_AwayN
    h_goto_if_eq SH_V, 1, L_SH_AwayS
    h_goto_if_eq SH_V, 2, L_SH_AwayW
    h_turnobject SH_SCOTT, 3
    VMJump L_SH_Away
L_SH_AwayN:
    h_turnobject SH_SCOTT, 0
    VMJump L_SH_Away
L_SH_AwayS:
    h_turnobject SH_SCOTT, 1
    VMJump L_SH_Away
L_SH_AwayW:
    h_turnobject SH_SCOTT, 2
L_SH_Away:
    h_msgbox T_Effort
    h_faceplayer                        // Common_Movement_FacePlayer
    h_buffer_player
    h_msgbox T_Memento
    WorkSetConst SH_BP, 1
    h_goto_if_eq VAR_SCOTT_STATE, 13, L_SH_BP4
    h_goto_if_ge VAR_SCOTT_STATE, 9, L_SH_BP3
    h_goto_if_ge VAR_SCOTT_STATE, 6, L_SH_BP2
    VMJump L_SH_GiveBP
L_SH_BP4:
    WorkSetConst SH_BP, 4
    VMJump L_SH_GiveBP
L_SH_BP3:
    WorkSetConst SH_BP, 3
    VMJump L_SH_GiveBP
L_SH_BP2:
    WorkSetConst SH_BP, 2
L_SH_GiveBP:                            // GiveBattlePoints
    fr_add_bp SH_BP
    h_buffer_player
    WordSetNumber 1, SH_BP, 1
    MEPlay FR_ME_OBTAIN_BP              // MSGBOX_GETPOINTS
    h_msgbox T_ObtainedBP
    MEWait
    h_msgbox T_ExplainBP
    h_setflag FLAG_SCOTT_GIVES_BATTLE_POINTS
    h_setflag SH_TEMP_2
    h_release

    .balign 4, 0
