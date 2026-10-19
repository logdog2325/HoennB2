// Route 111's story (Sapphire data/maps/Route111/scripts.inc + data/scripts/gabby_and_ty.inc, secret_power_tm.inc;
// chapter Ch4, ch4 agent 2026-10-07). converter/gen_map_content.py includes this file twice in the zone's generated
// script file (zone 370): the entries below are scripts 1-14, the generated signs/people follow. Text:
// src/text/scenes/Route111.txt (lines T_* below). People, fossils, rocks, triggers: data/story/ch4.json (outdoor uid =
// 100 + Sapphire local id). Map scripts: scenes/Route111_init.inc (zone init = script 1).
// Black 2 gaps (ch4 report): the desert's weather and music switches (Sapphire's setweather/fadenewbgm triggers and
// OnTransition sandstorm area) are not done: Black 2 has one weather per zone and no script weather command it uses
// (FieldSetWeather is never used by Black 2, ov012 0x021611e0, not decompiled); the Desert Ruins wall
// (FLAG_REGI_DOORS_OPENED, setmetatile on load) waits for the Desert Ruins room (Ch12, not built).
#include "hoenn_tms.h"  // new_tms: ITEM_TM96 ... (#pragma once: this file is included twice)
#ifdef SCENE_ENTRIES
    ScriptEntry R111_Init                   // 1: Route111_OnTransition (zone init)
    ScriptEntry R111_Victor                 // 2: object 1 (Winstrate family)
    ScriptEntry R111_RootFossil             // 3: object 34
    ScriptEntry R111_ClawFossil             // 4: object 35
    ScriptEntry R111_BerryGirl              // 5: object 17
    ScriptEntry R111_SandstormSouth         // 6: triggers (11-14,61) (Route111_EventScript_150116)
    ScriptEntry R111_SandstormWest          // 7: triggers (12,44)-(18,38) (Route111_EventScript_150122)
    ScriptEntry R111_SecretPowerMan         // 8: object 33
    ScriptEntry R111_Gabby1                 // 9: object 14
    ScriptEntry R111_Ty1                    // 10: object 13
    ScriptEntry R111_Gabby2                 // 11: object 21
    ScriptEntry R111_Ty2                    // 12: object 22
    ScriptEntry R111_Gabby3                 // 13: object 23
    ScriptEntry R111_Ty3                    // 14: object 24
#ifdef HOENN_EMERALD
    ScriptEntry R111_EmCollapse             // 15: map-script condition VAR_MIRAGE_TOWER_STATE 1 (Route111_EventScript_MirageTowerDisappear)
    ScriptEntry R111_EmRedraw               // 16: the seam trigger (work 0x4004 == 1): the Mirage Tower's cells redrawn
#endif
#else
#include "scenes/ch4_lib.inc"

// text lines (src/text/scenes/Route111.txt; work/agents/ch4/tools/gentext.py writes them from these comments)
#define T_RootFossilAsk 0       // Route111_Text_16FA54
#define T_LeftRoot 1            // Route111_Text_16FACE
#define T_ClawFossilAsk 2       // Route111_Text_16FAED
#define T_LeftClaw 3            // Route111_Text_16FB67
#define T_BerryGive 4           // Route111_Text_1C56F0
#define T_BerryAfter 5          // Route111_Text_1C5781
#define T_BerryDone 6           // Route111_Text_1C57D2
#define T_Sandstorm 7           // Route111_Text_1A0F93
#define T_VictorAsk 8           // Route111_Text_16F705
#define T_VictorNo 9            // Route111_Text_16F785
#define T_VictorYes 10          // Route111_Text_16F7B3
#define T_VictorFound 11        // Route111_Text_16F7FF
#define T_VictoriaIntro 12      // Route111_Text_16F82D
#define T_VictoriaFound 13      // Route111_Text_16F8D5
#define T_ViviIntro 14          // Route111_Text_16F90E
#define T_ViviCry 15            // Route111_Text_16F96C
#define T_VickyIntro 16         // Route111_Text_16F991
#define T_VickyAfter 17         // Route111_Text_16FA22
#define T_SPAsk 18              // Route111_Text_1A3520
#define T_SPNo 19               // Route111_Text_1A37B5
#define T_SPExplain 20          // Route111_Text_1A35C5
#define T_SPNoRoom 21           // Route111_Text_1A37F6
#define T_BagFull 22            // Text_TooBadBagIsFull
#define T_GT0 23                // Route111_Text_1AC59E
#define T_GT1 24                // Route111_Text_1AC7E4
#define T_GT2 25                // Route111_Text_1ABED8
#define T_GT3 26                // Route111_Text_1AC73B
#define T_GT4 27                // Route111_Text_1AC5CA
#define T_GT5 28                // Route111_Text_1AC820
#define T_GT6 29                // Route111_Text_1ABF50
#define T_GT7 30                // Route111_Text_1AC790
#define T_GT8 31                // Route111_Text_1AC015
#define T_GT9 32                // Route111_Text_1AC60B
#define T_GT10 33               // Route111_Text_1AC3CF
#define T_GT11 34               // Route111_Text_1AC40F
#define T_GT12 35               // Route111_Text_1AC487
#define T_GT13 36               // Route111_Text_1AC553
#define GT_TEXT T_GT0
#include "scenes/gabby_ty.inc"           // Gabby & Ty (shared with Ch7's Routes 118/120)

#define R111_X(x) (248+(x))     // Sapphire tile -> world tile (b2tools/world.py: Route111 at 216,28 + the 32-tile margin)
#define R111_Z(z) (60+(z))
#define R111_TEMP_3 0x4003      // Sapphire VAR_TEMP_3 (a map-local work: Black 2 clears 0x4000-0x401F on zone init)

R111_Init:                                  // Route111_OnTransition
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
#ifdef HOENN_EMERALD
    VMCall R111_EmMirage                    // SetMirageTowerVisibility + the layout (scenes/emerald/Route111_Mirage.inc)
#endif
#ifdef HOENN_TEST_CH4
    VMCall Test_Ch4Start
#endif
    VMCall Sub_GabbyTyUpdate                // call Route111_EventScript_1AE313
    h_goto_if_not_defeated TRAINER_VICKY, L_R111_ResetWinstrates
    VMHalt
L_R111_ResetWinstrates:                     // Route111_EventScript_15000D: a lost gauntlet starts again
    h_clearflag FLAG_HIDE_VICTOR_WINSTRATE
    h_setflag FLAG_HIDE_VICTORIA_WINSTRATE
    h_setflag FLAG_HIDE_VIVI_WINSTRATE
    h_setflag FLAG_HIDE_VICKI_WINSTRATE
    TrainerFlagReset TRAINER_VICTOR
    TrainerFlagReset TRAINER_VICTORIA
    TrainerFlagReset TRAINER_VIVI
    VMHalt

// ---- the desert: the Go-Goggles (Ch5 gives them) --------------------------------------------------------------------
R111_SandstormSouth:                        // Route111_EventScript_150116 (VAR_0x8004 = 1: back down)
    h_lock
    WorkSetConst C4_TMP2, 1
    VMJump L_R111_Sandstorm
R111_SandstormWest:                         // Route111_EventScript_150122 (VAR_0x8004 = 2: back left)
    h_lock
    WorkSetConst C4_TMP2, 2
L_R111_Sandstorm:                           // Route111_EventScript_15013A
    h_checkitem ITEM_GO_GOGGLES, 1, C4_TMP
    h_goto_if_eq C4_TMP, 0, L_R111_NoGoggles
    WorkSetConst R111_TEMP_3, 1
    h_release
L_R111_NoGoggles:                           // Route111_EventScript_150151
    h_msgbox_info T_Sandstorm
    h_closemessage
    h_goto_if_eq C4_TMP2, 2, L_R111_BackLeft
    h_applymovement 255, Mv_R111_WalkDown
    h_waitmovement
    h_release
L_R111_BackLeft:
    h_applymovement 255, Mv_R111_WalkLeft
    h_waitmovement
    h_release

// ---- the fossils (after the Go-Goggles) -----------------------------------------------------------------------------
R111_RootFossil:                            // Route111_EventScript_150023
    h_lock
    c4_yesno_info T_RootFossilAsk, C4_TMP
    h_goto_if_no C4_TMP, L_R111_LeaveRoot
    h_closemessage
    h_giveitem ITEM_ROOT_FOSSIL
    h_closemessage
    h_setflag FLAG_HIDE_ROOT_FOSSIL
    h_setflag FLAG_HIDE_CLAW_FOSSIL
    ActorDelete 134                         // removeobject 34
    h_delay 30
    h_applymovement 135, Mv_R111_FossilSinks
    h_waitmovement
    ActorDelete 135                         // removeobject 35
    h_release
L_R111_LeaveRoot:
    WordSetPlayerName 0
    h_msgbox_info T_LeftRoot
    h_release

R111_ClawFossil:                            // Route111_EventScript_150069
    h_lock
    c4_yesno_info T_ClawFossilAsk, C4_TMP
    h_goto_if_no C4_TMP, L_R111_LeaveClaw
    h_closemessage
    h_giveitem ITEM_CLAW_FOSSIL
    h_closemessage
    h_setflag FLAG_HIDE_CLAW_FOSSIL
    h_setflag FLAG_HIDE_ROOT_FOSSIL
    ActorDelete 135
    h_delay 30
    h_applymovement 134, Mv_R111_FossilSinks
    h_waitmovement
    ActorDelete 134
    h_release
L_R111_LeaveClaw:
    WordSetPlayerName 0
    h_msgbox_info T_LeftClaw
    h_release

// ---- the berry girl (daily Razz Berry) ------------------------------------------------------------------------------
R111_BerryGirl:                             // Route111_EventScript_1500C5 (dotimebasedevents: Black 2 resets the
    c4_talk                                 // daily flag itself at midnight)
    h_goto_if_set FLAG_DAILY_RECEIVED_BERRY_ROUTE111, L_R111_BerryDone
    h_msgbox T_BerryGive
    h_closemessage                          // (Black 2: the item script opens its own window)
    h_giveitem ITEM_RAZZ_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_R111_BagFull
    h_setflag FLAG_DAILY_RECEIVED_BERRY_ROUTE111
    h_msgbox T_BerryAfter                   // (GetPlayerBigGuyGirlString: the line has no {STR_VAR})
    h_release
L_R111_BerryDone:
    h_msgbox T_BerryDone
    h_release
L_R111_BagFull:
    h_bag_is_full T_BagFull
    h_release

// ---- the Winstrate family (Macho Brace: their house, room 554) ------------------------------------------------------
R111_Victor:                                // Route111_EventScript_1501D1
    c4_talk
    h_setflag FLAG_LANDMARK_WINSTRATE_FAMILY
    h_yesno T_VictorAsk, C4_TMP
    h_goto_if_yes C4_TMP, L_R111_Gauntlet
    h_msgbox T_VictorNo
    h_release
L_R111_Gauntlet:                            // Route111_EventScript_1501F3
    h_msgbox T_VictorYes
    h_closemessage
    h_trainerbattle TRAINER_VICTOR
    h_applymovement 101, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    c4_opendoor R111_X(13), R111_Z(113)
    h_msgbox_actor T_VictorFound, 101
    h_closemessage
    h_applymovement 101, Mv_R111_IntoHouse
    h_waitmovement
    h_removeobject 101, FLAG_HIDE_VICTOR_WINSTRATE
    c4_closedoor
    VMSleep 24                              // Route111_Movement_15035B: delay_16 x 3
    c4_opendoor R111_X(13), R111_Z(113)
    h_addobject 102, FLAG_HIDE_VICTORIA_WINSTRATE
    h_applymovement 102, Mv_R111_OutOfHouse
    h_waitmovement
    c4_closedoor
    h_msgbox_actor T_VictoriaIntro, 102
    h_closemessage
    h_trainerbattle TRAINER_VICTORIA
    h_applymovement 102, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    c4_opendoor R111_X(13), R111_Z(113)
    h_msgbox_actor T_VictoriaFound, 102
    h_closemessage
    h_applymovement 102, Mv_R111_IntoHouse
    h_waitmovement
    h_removeobject 102, FLAG_HIDE_VICTORIA_WINSTRATE
    c4_closedoor
    VMSleep 24
    c4_opendoor R111_X(13), R111_Z(113)
    h_addobject 103, FLAG_HIDE_VIVI_WINSTRATE
    h_applymovement 103, Mv_R111_OutOfHouse
    h_waitmovement
    c4_closedoor
    h_msgbox_actor T_ViviIntro, 103
    h_closemessage
    h_trainerbattle TRAINER_VIVI
    h_applymovement 103, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    c4_opendoor R111_X(13), R111_Z(113)
    h_msgbox_actor T_ViviCry, 103
    h_closemessage
    h_applymovement 103, Mv_R111_IntoHouse
    h_waitmovement
    h_removeobject 103, FLAG_HIDE_VIVI_WINSTRATE
    c4_closedoor
    VMSleep 24
    c4_opendoor R111_X(13), R111_Z(113)
    h_addobject 104, FLAG_HIDE_VICKI_WINSTRATE
    h_applymovement 104, Mv_R111_OutOfHouse
    h_waitmovement
    c4_closedoor
    h_msgbox_actor T_VickyIntro, 104
    h_closemessage
    h_trainerbattle TRAINER_VICKY
    h_msgbox_actor T_VickyAfter, 104
    h_closemessage
    h_applymovement 104, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    c4_opendoor R111_X(13), R111_Z(113)
    h_applymovement 104, Mv_R111_IntoHouse
    h_waitmovement
    h_removeobject 104, FLAG_HIDE_VICKI_WINSTRATE
    c4_closedoor
    h_release

// ---- the Secret Power man (TM43: Secret Power is no Gen 5 TM; Black 2's TM43 stands in, as converter/gen_items.py) --
R111_SecretPowerMan:                        // Route111_EventScript_1A3858 (data/scripts/secret_power_tm.inc)
    c4_talk
    h_yesno T_SPAsk, C4_TMP
    h_goto_if_yes C4_TMP, L_R111_SPGive
    h_msgbox T_SPNo
    h_release
L_R111_SPGive:
    h_closemessage
    h_giveitem ITEM_TM102               // Gen 3 TM43 Secret Power: the new TM102 (b2tools/patches/new_tms.py)
    h_goto_if_eq HLIB_RESULT, 0, L_R111_SPNoRoom
    h_msgbox T_SPExplain
    h_closemessage
    h_setflag FLAG_RECEIVED_SECRET_POWER
    h_clearflag FLAG_HIDE_TM_SALESMAN_SLATEPORT
    h_getplayerfacing C4_TMP                // VAR_FACING west/east (Black 2 2/3) or north (0): his way out;
    h_goto_if_eq C4_TMP, 1, L_R111_SPGone   // facing south: he just goes (as Sapphire)
    h_goto_if_eq C4_TMP, 0, L_R111_SPNorth
    h_applymovement 133, Mv_R111_SPLeave1
    h_waitmovement
    VMJump L_R111_SPGone
L_R111_SPNorth:
    h_applymovement 133, Mv_R111_SPLeave2
    h_waitmovement
L_R111_SPGone:
    h_removeobject 133, FLAG_HIDE_SECRET_POWER_MAN
    h_release
L_R111_SPNoRoom:
    h_msgbox T_SPNoRoom
    h_release

// ---- Gabby & Ty (scenes/gabby_ty.inc) -------------------------------------------------------------------------------
R111_Gabby1:                                // Route111_EventScript_1AE422
    c4_gabby_ty TRAINER_GABBY_AND_TY_1, GT_GABBY, 1
R111_Ty1:                                   // Route111_EventScript_1AE442
    c4_gabby_ty TRAINER_GABBY_AND_TY_1, GT_TY, 1
R111_Gabby2:                                // Route111_EventScript_1AE4E2
    c4_gabby_ty TRAINER_GABBY_AND_TY_4, GT_GABBY, 0
R111_Ty2:                                   // Route111_EventScript_1AE502
    c4_gabby_ty TRAINER_GABBY_AND_TY_4, GT_TY, 0
R111_Gabby3:                                // Route111_EventScript_1AE562
    c4_gabby_ty TRAINER_GABBY_AND_TY_6, GT_GABBY, 0
R111_Ty3:                                   // Route111_EventScript_1AE582
    c4_gabby_ty TRAINER_GABBY_AND_TY_6, GT_TY, 0

#ifdef HOENN_EMERALD
#include "scenes/emerald/Route111_Mirage.inc"   // Emerald's Mirage Tower (emerald_ch9_mirage): scripts 15-16 above, R111_EmMirage
#endif
#include "scenes/ch4_test.inc"

    .balign 4, 0
Mv_R111_WalkDown:
    walk_down
    step_end
Mv_R111_WalkLeft:
    walk_left
    step_end
Mv_R111_FossilSinks:                        // Route111_Movement_1500AF
    set_visible
    delay_4
    set_invisible
    delay_4
    set_visible
    delay_4
    set_invisible
    delay_4
    set_visible
    delay_8
    set_invisible
    delay_8
    set_visible
    delay_8
    set_invisible
    delay_8
    set_visible
    delay_16
    set_invisible
    delay_16
    set_visible
    step_end
Mv_R111_IntoHouse:                          // Route111_Movement_150356
    walk_in_place_fastest_up
    walk_up
    step_end
Mv_R111_OutOfHouse:                         // Route111_Movement_150359
    walk_down
    step_end
Mv_R111_SPLeave1:                           // Route111_Movement_1A38E3
    walk_down 5
    walk_left 4
    walk_down 2
    step_end
Mv_R111_SPLeave2:                           // Route111_Movement_1A38EF
    walk_left
    walk_down 5
    walk_left 3
    walk_down 2
    step_end
#include "common/movement.inc"
#endif
