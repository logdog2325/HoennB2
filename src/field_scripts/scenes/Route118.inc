// Route 118's story (Sapphire data/maps/Route118/scripts.inc; chapter Ch7, ch7 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file 0892_auto_Route118.s: the entries
// below are scripts 1-11, the generated signs/people follow. Text: src/text/scenes/Route118.txt (T_* below). People
// and triggers: data/story/ch7.json (outdoor uid = 100 + Sapphire local id). Map scripts: scenes/Route118_init.inc
// (zone init = script 1). Trainers: the trainers patch (eye contact); Route 118's east end (x 64-79: Perry, an item
// ball) is Route 118's zone too since every map has its own zone up to its edges (it was Route 123's zone 154 while a
// zone covered whole 32x32 cells; zone_edges 2026-10-08). Gabby & Ty: ch4's shared scenes/gabby_ty.inc.
#ifdef SCENE_ENTRIES
    ScriptEntry R118_Init               // 1: Route118_MapScript1_150F2E (zone init)
    ScriptEntry R118_GoodRodFisherman   // 2: object 13, Route118_EventScript_150F34
    ScriptEntry R118_StevenLeft         // 3: trigger (43,11) VAR_ROUTE118_STATE 0, Route118_EventScript_150FAE
    ScriptEntry R118_StevenMiddle       // 4: trigger (44,11), Route118_EventScript_150FCE
    ScriptEntry R118_StevenRight        // 5: trigger (45,11), Route118_EventScript_150FE4
    ScriptEntry R118_Gabby1             // 6: object 5, Route118_EventScript_1AE462 (TRAINER_GABBY_AND_TY_2)
    ScriptEntry R118_Ty1                // 7: object 6, Route118_EventScript_1AE482
    ScriptEntry R118_Gabby2             // 8: object 8, Route118_EventScript_1AE522 (TRAINER_GABBY_AND_TY_5)
    ScriptEntry R118_Ty2                // 9: object 9, Route118_EventScript_1AE542
    ScriptEntry R118_Gabby3             // 10: object 10, Route118_EventScript_1AE562 (TRAINER_GABBY_AND_TY_6)
    ScriptEntry R118_Ty3                // 11: object 11, Route118_EventScript_1AE582
#else
#include "scenes/ch7_lib.inc"
#include "scenes/ch7_test.inc"

#define T_StevenHi 0
#define T_GoodRodAgree 1
#define T_GoodRodTake 2
#define T_GoodRodTryLuck 3
#define T_GoodRodDontLike 4
#define T_GoodRodTryCatching 5
#define T_GT0 6                         // Gabby & Ty: 14 lines from here (scenes/gabby_ty.inc's order)
#define GT_TEXT T_GT0
#if __has_include("scenes/gabby_ty.inc")
#include "scenes/gabby_ty.inc"         // ch4's shared Gabby & Ty code (the interview, Sub_GabbyTyUpdate)
#else                                   // (fallback while ch4's file is not committed: the intro line only)
#define GT_GABBY 0
#define GT_TY 1
    .macro c4_gabby_ty trainer, who, first
    h_msgbox_npc (GT_TEXT + 2 + \who)
    .endm
Sub_GabbyTyUpdate:
    VMReturn
#endif

#define R118_STEVEN 119                 // object 19 at (44,7) (FLAG_HIDE_STEVEN_ROUTE118)

R118_Init:                              // Route118_MapScript1_150F2E
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
#ifdef HOENN_TEST_CH7
    VMCall Test_Ch7Start
#endif
    VMCall Sub_GabbyTyUpdate            // call Route118_EventScript_1AE313
    VMHalt

R118_GoodRodFisherman:                  // Route118_EventScript_150F34
    c7_talk
    h_goto_if_set FLAG_RECEIVED_GOOD_ROD, L_R118_GotGoodRod
    h_yesno T_GoodRodAgree, C7_TMP      // Hmm! A Good Rod is really good! Wouldn't you agree?
    h_goto_if_no C7_TMP, L_R118_DontLikeFishing
    h_msgbox T_GoodRodTake              // Hmm! We're of identical minds! Hmm! Take this Good Rod!
    h_closemessage
    h_giveitem ITEM_GOOD_ROD            // (Sapphire does not look at giveitem's result here)
    h_setflag FLAG_RECEIVED_GOOD_ROD
    h_msgbox T_GoodRodTryLuck           // Wherever there's water, try your luck at fishing.
    h_release
L_R118_DontLikeFishing:
    h_msgbox T_GoodRodDontLike
    h_release
L_R118_GotGoodRod:
    h_msgbox T_GoodRodTryCatching
    h_release

// Steven on the ledge above the path (Route118_EventScript_151004)
R118_StevenLeft:
    h_lock
    h_setvar C7_POS, 0                  // VAR_0x8008 0: the player is on (43,11)
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_applymovement R118_STEVEN, Mv_R118_StevenLeft
    h_waitmovement
    VMJump L_R118_Steven
R118_StevenMiddle:
    h_lock
    h_setvar C7_POS, 1                  // (44,11)
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    VMJump L_R118_Steven
R118_StevenRight:
    h_lock
    h_setvar C7_POS, 2                  // (45,11)
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_applymovement R118_STEVEN, Mv_R118_StevenRight
    h_waitmovement
L_R118_Steven:
    h_playse SE_LEDGE
    h_applymovement R118_STEVEN, Mv_R118_StevenJumpDown
    h_waitmovement
    h_delay 30
    h_buffer_player
    h_msgbox_actor T_StevenHi, R118_STEVEN  // Steven: Hi! You're that Trainer I met in Dewford! ...
    h_closemessage
    h_goto_if_eq C7_POS, 1, L_R118_StevenLeavesMiddle
    h_goto_if_eq C7_POS, 2, L_R118_StevenLeavesRight
    h_applymovement R118_STEVEN, Mv_R118_StevenLeaves10
    VMJump L_R118_StevenLeaves
L_R118_StevenLeavesMiddle:
    h_applymovement R118_STEVEN, Mv_R118_StevenLeaves9
    VMJump L_R118_StevenLeaves
L_R118_StevenLeavesRight:
    h_applymovement R118_STEVEN, Mv_R118_StevenLeaves8
L_R118_StevenLeaves:
    h_waitmovement
    h_setvar VAR_ROUTE118_STATE, 1
    h_removeobject R118_STEVEN, FLAG_HIDE_STEVEN_ROUTE118
    h_release

// Gabby & Ty (data/scripts/gabby_and_ty.inc: one pair stands here at a time, Sub_GabbyTyUpdate)
R118_Gabby1:
    c4_gabby_ty TRAINER_GABBY_AND_TY_2, GT_GABBY, 0
R118_Ty1:
    c4_gabby_ty TRAINER_GABBY_AND_TY_2, GT_TY, 0
R118_Gabby2:
    c4_gabby_ty TRAINER_GABBY_AND_TY_5, GT_GABBY, 0
R118_Ty2:
    c4_gabby_ty TRAINER_GABBY_AND_TY_5, GT_TY, 0
R118_Gabby3:
    c4_gabby_ty TRAINER_GABBY_AND_TY_6, GT_GABBY, 0
R118_Ty3:
    c4_gabby_ty TRAINER_GABBY_AND_TY_6, GT_TY, 0

    .balign 4, 0
Mv_R118_StevenLeft:                     // Route118_Movement_151069
    walk_left
    step_end
Mv_R118_StevenRight:                    // Route118_Movement_15106B
    walk_right
    step_end
Mv_R118_StevenJumpDown:                 // Route118_Movement_15106D: off the ledge, toward the player
    jump_2_down
    delay_16
    walk_down
    step_end
Mv_R118_StevenLeaves10:                 // Route118_Movement_151071
    walk_right 10
    step_end
Mv_R118_StevenLeaves9:                  // Route118_Movement_15107C
    walk_right 9
    step_end
Mv_R118_StevenLeaves8:                  // Route118_Movement_151086
    walk_right 8
    step_end
#include "common/movement.inc"
#endif
