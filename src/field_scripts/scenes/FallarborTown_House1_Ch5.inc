// Chapter 5's beat in Prof. Cozmo's house (Sapphire FallarborTown_CozmosHouse_EventScript_PlayerHasMeteorite ..
// GaveMeteorite; ch5 agent 2026-10-07): the Meteorite from Mt. Chimney for TM27 Return. Included (body only) by Ch4's
// 0194_room_FallarborTown_House1.s after its story code, with `#define CH5_COZMO_TEXT n` before it: n = the first of
// this beat's 6 lines in src/text/script/0108_room_FallarborTown_House1.txt (copied from
// src/text/scenes/FallarborTown_House1_Ch5.txt, in order). Ch4's Cozmo script (talked to: h_lock, h_faceplayer done,
// actor uid 1) jumps here: FLAG_RECEIVED_TM_RETURN set -> Ch5_CozmoGaveMeteorite; ITEM_METEORITE in the Bag ->
// Ch5_CozmoMeteorite. Ch4's lines used here: CH5_COZMO_TEXT-5 MeteoriteWillNeverBeMineNow, CH5_COZMO_TEXT-1
// ReallyGoingToHelpMyResearch (ch4: lines 1-5 of 0108, this beat's from 6).
#ifndef CH5_COZMO_TEXT
#define CH5_COZMO_TEXT 6
#endif
#include "hoenn_key_items.h"
#define C5C_T_NeverMine (CH5_COZMO_TEXT-5)      // (Ch4's line) Prof. Cozmo: Oh... I never should have let myself ...
#define C5C_T_HelpResearch (CH5_COZMO_TEXT-1)   // (Ch4's line) Prof. Cozmo: Oh, I can't believe it. ...
#define C5C_T_IsThat (CH5_COZMO_TEXT+0)
#define C5C_T_MayIHave (CH5_COZMO_TEXT+1)
#define C5C_T_PleaseUse (CH5_COZMO_TEXT+2)
#define C5C_T_Crushed (CH5_COZMO_TEXT+3)
#define C5C_T_HandedOver (CH5_COZMO_TEXT+4)
#define C5C_T_BagFull (CH5_COZMO_TEXT+5)
#define C5C_TEMP_2 0x5C                         // FLAG_TEMP_2 (map-local: flags 0-0x63 reset on every zone change)

Ch5_CozmoMeteorite:                             // FallarborTown_CozmosHouse_EventScript_PlayerHasMeteorite
    h_goto_if_set C5C_TEMP_2, L_C5C_Ask
    h_msgbox C5C_T_NeverMine                    // FallarborTown_CozmosHouse_EventScript_NoticeMeteorite
    h_yesno C5C_T_IsThat, HLIB_TMP              // Oh! Hah? That item... Could it be? ... in exchange for this TM?
    VMJump L_C5C_Answer
L_C5C_Ask:                                      // FallarborTown_CozmosHouse_EventScript_AskForMeteorite
    h_yesno C5C_T_MayIHave, HLIB_TMP            // Prof. Cozmo: Please, may I have that Meteorite? ...
L_C5C_Answer:
    h_goto_if_no HLIB_TMP, L_C5C_Decline
    h_msgbox C5C_T_PleaseUse                    // Prof. Cozmo: This TM, it represents my feeling of gratitude. ...
    h_closemessage
    h_giveitem ITEM_TM27                        // TM27 Return
    h_goto_if_eq HLIB_RESULT, 0, L_C5C_BagFull
    h_handover_item ITEM_METEORITE, C5C_T_HandedOver    // Common_EventScript_PlayerHandedOverTheItem
    h_setflag FLAG_RECEIVED_TM_RETURN
    h_msgbox C5C_T_HelpResearch
    h_release
L_C5C_BagFull:                                  // Common_EventScript_ShowBagIsFull
    h_msgbox C5C_T_BagFull
    h_release
L_C5C_Decline:                                  // FallarborTown_CozmosHouse_EventScript_DeclineGiveMeteorite
    h_setflag C5C_TEMP_2
    h_msgbox C5C_T_Crushed                      // Prof. Cozmo: Oh, but... I'm crushed with disappointment...
    h_release

Ch5_CozmoGaveMeteorite:                         // FallarborTown_CozmosHouse_EventScript_GaveMeteorite
    h_msgbox C5C_T_HelpResearch
    h_release
