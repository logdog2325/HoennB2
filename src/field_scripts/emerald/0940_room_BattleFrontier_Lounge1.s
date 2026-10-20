// BattleFrontier_Lounge1 (zone 470; header scripts 940 -> own file 2086), Pokémon Emerald NDS only (frontier_lounges,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_Lounge1/scripts.inc: the Pokémon Breeder who rates a Pokémon's
// potential (BufferVarsForIVRater: the total of its IVs and its best stat), and two boys. The IVs are read with Black 2's
// own IV judge command (PokePartyGetIV slot, which, var: 0 the total, 1 the highest, 2-7 HP, Attack, Defense, Speed,
// Sp. Atk, Sp. Def; Black 2's Judge, b2 field script 1255). Emerald's tie rule for the best stat (an equal IV later in
// HP, Atk, Def, Speed, SpAtk, SpDef order replaces it on a coin flip) is kept.
// The room: data/interior_layouts/BattleFrontier_Lounge1.json, people data/interiors/emerald/470.json (uid = script =
// Emerald's local id). Messages: src/text/script/emerald/0196_room_BattleFrontier_Lounge1.txt
// (work/agents/frontier_lounges/tools/lounge_rooms.py: pokeemerald's words).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

#define T_Intro 0                       // For 70 years I have raised Pokémon! ...
#define T_LetsLook 1                    // Ah, youngster! Do your Pokémon's abilities intrigue you? ...
#define T_Egg 2                         // An expert I am, but even I can't tell anything about an unhatched Pokémon! ...
#define T_NoTime 3                      // What? You have no time for my advice? ...
#define T_Total 4                       // 4-7: average / better than average / impressive / outstanding
#define T_Best 8                        // 8-13: the best aspect is its HP / Attack / Defense / Speed / Sp. Atk / Sp. Def
#define T_Value 14                      // 14-17: relatively good / quite impressive / outstanding / flawless
#define BR_OK 0x8020                    // CallPokeSelect: 1 = a Pokémon picked
#define BR_SLOT 0x8021                  //   its party slot (Emerald's VAR_0x8004)
#define BR_V 0x8022
#define BR_BEST 0x8023                  // VAR_0x8007: the best IV
#define BR_STAT 0x8024                  // VAR_0x8006: its stat (STAT_HP 0 ... STAT_SPDEF 5)
#define BR_R 0x8025

    ScriptEntry BR_Breeder              // 1: BattleFrontier_Lounge1_EventScript_Breeder (OLD_MAN (0,6))
    ScriptEntry BR_Boy1                 // 2: BattleFrontier_Lounge1_EventScript_Boy1 (BOY_3)
    ScriptEntry BR_Boy2                 // 3: BattleFrontier_Lounge1_EventScript_Boy2 (BOY_2)
    ScriptEntriesEnd

    .macro br_stat stat, which          // BufferVarsForIVRater's loop step for stat `stat` (IV judge field `which`)
    PokePartyGetIV BR_SLOT, \which, BR_V
    WorkCmpWork BR_V, BR_BEST
    VMJumpIf CMP_GT, .Lbrp\@
    WorkCmpWork BR_V, BR_BEST
    VMJumpIf CMP_NE, .Lbrn\@
    Random BR_R, 2                      // equal: Random() & 1 picks it
    WorkCmpConst BR_R, 0
    VMJumpIf CMP_EQ, .Lbrn\@
.Lbrp\@:
    WorkSet BR_BEST, BR_V
    WorkSetConst BR_STAT, \stat
.Lbrn\@:
    .endm

BR_Breeder:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_MET_BATTLE_FRONTIER_BREEDER, L_BR_Met
    h_msgbox T_Intro
    VMJump L_BR_Choose0
L_BR_Met:
    h_msgbox T_LetsLook
L_BR_Choose0:
    h_setflag FLAG_MET_BATTLE_FRONTIER_BREEDER
L_BR_Choose:                            // ChooseMonToShowBreeder
    h_closemessage
    WorkSetConst BR_OK, 0
    WorkSetConst BR_SLOT, 0
    CallPokeSelect 0, BR_OK, BR_SLOT, 0
    h_goto_if_ne BR_OK, 1, L_BR_Cancel
    PokePartyIsEgg BR_V, BR_SLOT
    h_goto_if_eq BR_V, 1, L_BR_Egg
    PokePartyGetIV BR_SLOT, 0, BR_V     // VAR_0x8005: the sum of its IVs
    h_goto_if_le BR_V, 90, L_BR_T0      // average of 15
    h_goto_if_le BR_V, 120, L_BR_T1     // average of 20
    h_goto_if_le BR_V, 150, L_BR_T2     // average of 25
    h_msgbox T_Total+3
    VMJump L_BR_Stat
L_BR_T0:
    h_msgbox T_Total+0
    VMJump L_BR_Stat
L_BR_T1:
    h_msgbox T_Total+1
    VMJump L_BR_Stat
L_BR_T2:
    h_msgbox T_Total+2
L_BR_Stat:                              // the highest IV stat (Emerald's order and tie rule)
    PokePartyGetIV BR_SLOT, 2, BR_BEST
    WorkSetConst BR_STAT, 0
    br_stat 1, 3                        // Attack
    br_stat 2, 4                        // Defense
    br_stat 3, 5                        // Speed
    br_stat 4, 6                        // Sp. Atk
    br_stat 5, 7                        // Sp. Def
    h_goto_if_eq BR_STAT, 0, L_BR_S0
    h_goto_if_eq BR_STAT, 1, L_BR_S1
    h_goto_if_eq BR_STAT, 2, L_BR_S2
    h_goto_if_eq BR_STAT, 3, L_BR_S3
    h_goto_if_eq BR_STAT, 4, L_BR_S4
    h_msgbox T_Best+5
    VMJump L_BR_Value
L_BR_S0:
    h_msgbox T_Best+0
    VMJump L_BR_Value
L_BR_S1:
    h_msgbox T_Best+1
    VMJump L_BR_Value
L_BR_S2:
    h_msgbox T_Best+2
    VMJump L_BR_Value
L_BR_S3:
    h_msgbox T_Best+3
    VMJump L_BR_Value
L_BR_S4:
    h_msgbox T_Best+4
L_BR_Value:                             // the highest IV's value
    h_goto_if_le BR_BEST, 15, L_BR_V0
    h_goto_if_le BR_BEST, 25, L_BR_V1
    h_goto_if_le BR_BEST, 30, L_BR_V2
    h_msgbox T_Value+3
    VMJump L_BR_End
L_BR_V0:
    h_msgbox T_Value+0
    VMJump L_BR_End
L_BR_V1:
    h_msgbox T_Value+1
    VMJump L_BR_End
L_BR_V2:
    h_msgbox T_Value+2
L_BR_End:
    WorkSetConst BR_OK, 0
    WorkSetConst BR_SLOT, 0
    h_release
L_BR_Egg:                               // ShowEggToBreeder: the line, then the party again
    h_msgbox T_Egg
    VMJump L_BR_Choose
L_BR_Cancel:
    h_msgbox T_NoTime
    h_release

BR_Boy1:
    h_msgbox_npc 18

BR_Boy2:
    h_msgbox_npc 19

    .balign 4, 0
