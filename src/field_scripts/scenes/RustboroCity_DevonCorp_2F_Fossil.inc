// Devon Corp 2F, the fossil scientist (Sapphire RustboroCity_DevonCorp_2F_EventScript_FossilScientist .. end of file):
// chapter Ch4's beat (Root/Claw Fossil from the Route 111 desert -> Lileep/Anorith), included by
// 1152_room_RustboroCity_DevonCorp_2F.s (Ch2's file) as script 5 (label DV2_FossilScientist; the scientist is uid 5,
// Sapphire object 5). ch4 agent 2026-10-07. Text: line 6 (Ch2's copy of his first line) and lines 7-14 of 0367.
// VAR_FOSSIL_RESURRECTION_STATE 1 -> 2 (ready) is Ch2's OnTransition / Sub_DV2_SetFossilReady, as Sapphire's.
#include "hoenn_key_items.h"
#define DVF_T_Develop 6         // RustboroCity_DevonCorp_2F_Text_DevelopDeviceToResurrectFossils (Ch2's line)
#define DVF_T_BringBack 7       // RustboroCity_DevonCorp_2F_Text_WantToBringFossilBackToLife
#define DVF_T_Handed 8          // RustboroCity_DevonCorp_2F_Text_HandedFossilToResearcher
#define DVF_T_IsThatSo 9        // RustboroCity_DevonCorp_2F_Text_OhIsThatSo
#define DVF_T_TakesTime 10      // RustboroCity_DevonCorp_2F_Text_FossilRegeneratorTakesTime
#define DVF_T_BroughtBack 11    // RustboroCity_DevonCorp_2F_Text_FossilizedMonBroughtBackToLife
#define DVF_T_Received 12       // RustboroCity_DevonCorp_2F_Text_ReceivedMonFromResearcher
#define DVF_T_Nickname 13       // gText_NicknameReceivedPokemon
#define DVF_T_TooMany 14        // RustboroCity_DevonCorp_2F_Text_TooManyPokemon
#define DVF_TMP 0x8037
#define DVF_SPECIES 0x8038

DV2_FossilScientist:                        // RustboroCity_DevonCorp_2F_EventScript_FossilScientist
    h_lock
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
#if (HOENN_TEST_CH4 + 0) == 3
    // TEST ONLY (scenes/ch4_test.inc): a Root Fossil and a second Pokémon for the revival test
    h_goto_if_set FLAG_RECEIVED_FOSSIL_MON, L_DVF_TestDone
    h_goto_if_ne VAR_FOSSIL_RESURRECTION_STATE, 0, L_DVF_TestDone
    h_checkitem ITEM_ROOT_FOSSIL, 1, DVF_TMP
    h_goto_if_eq DVF_TMP, 1, L_DVF_TestDone
    ItemAdd ITEM_ROOT_FOSSIL, 1, DVF_TMP
    h_getpartysize DVF_TMP
    h_goto_if_ne DVF_TMP, 0, L_DVF_TestDone
    PokePartyAdd DVF_TMP, SPECIES_SWAMPERT, 0, 100
L_DVF_TestDone:
#endif
    h_goto_if_eq VAR_FOSSIL_RESURRECTION_STATE, 2, L_DVF_Ready
    h_goto_if_eq VAR_FOSSIL_RESURRECTION_STATE, 1, L_DVF_Regenerating
    h_msgbox DVF_T_Develop
    h_checkitem ITEM_ROOT_FOSSIL, 1, DVF_TMP
    h_goto_if_eq DVF_TMP, 1, L_DVF_Root
    h_checkitem ITEM_CLAW_FOSSIL, 1, DVF_TMP
    h_goto_if_eq DVF_TMP, 1, L_DVF_Claw
    h_release
L_DVF_Root:                                 // RustboroCity_DevonCorp_2F_EventScript_NoticeRootFossil
    WorkSetConst DVF_SPECIES, ITEM_ROOT_FOSSIL
    VMJump L_DVF_Notice
L_DVF_Claw:                                 // RustboroCity_DevonCorp_2F_EventScript_NoticeClawFossil
    WorkSetConst DVF_SPECIES, ITEM_CLAW_FOSSIL
L_DVF_Notice:
    h_closemessage
    h_applymovement 5, Common_Movement_ExclamationMark
    h_waitmovement
    h_applymovement 5, Common_Movement_Delay48
    h_waitmovement
    h_yesno DVF_T_BringBack, DVF_TMP
    h_goto_if_no DVF_TMP, L_DVF_Decline
    WordSetItemName 1, DVF_SPECIES          // bufferitemname 0
    h_msgbox DVF_T_Handed
    ItemSub DVF_SPECIES, 1, DVF_TMP         // removeitem
    h_setvar VAR_FOSSIL_RESURRECTION_STATE, 1
    h_setvar VAR_WHICH_FOSSIL_REVIVED, 1
    h_goto_if_eq DVF_SPECIES, ITEM_ROOT_FOSSIL, L_DVF_Handed
    h_setvar VAR_WHICH_FOSSIL_REVIVED, 2
L_DVF_Handed:
    h_release
L_DVF_Decline:
    h_msgbox DVF_T_IsThatSo
    h_release
L_DVF_Regenerating:
    h_msgbox DVF_T_TakesTime
    h_release
L_DVF_Ready:                                // RustboroCity_DevonCorp_2F_EventScript_FossilMonReady
    WorkSetConst DVF_SPECIES, SPECIES_LILEEP
    h_goto_if_eq VAR_WHICH_FOSSIL_REVIVED, 1, L_DVF_Give
    WorkSetConst DVF_SPECIES, SPECIES_ANORITH
    h_goto_if_eq VAR_WHICH_FOSSIL_REVIVED, 2, L_DVF_Give
    h_release
L_DVF_Give:                                 // ..._LileepReady / _AnorithReady
    WordSetPokeSpecies 2, DVF_SPECIES       // bufferspeciesname 1
    h_msgbox DVF_T_BroughtBack
    h_getpartysize DVF_TMP
    h_goto_if_eq DVF_TMP, 6, L_DVF_TooMany
    h_setvar VAR_FOSSIL_RESURRECTION_STATE, 0
    h_setflag FLAG_RECEIVED_FOSSIL_MON
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    h_msgbox_info DVF_T_Received
    h_waitfanfare
    PokePartyAdd DVF_TMP, DVF_SPECIES, 0, 20     // givemon SPECIES_LILEEP / ANORITH, 20, ITEM_NONE
    h_closemessage
    h_yesno DVF_T_Nickname, DVF_TMP
    h_goto_if_no DVF_TMP, L_DVF_Done
    h_getpartysize DVF_TMP                  // the new one is the last party slot
    WorkSub DVF_TMP, 1
    h_name_received_mon DVF_TMP
L_DVF_Done:
    h_release
L_DVF_TooMany:
    h_msgbox DVF_T_TooMany
    h_release
#include "common/movement.inc"
