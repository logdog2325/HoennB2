// Route 120's story (Sapphire data/maps/Route120/scripts.inc; chapter Ch7, ch7 agent 2026-10-07): Steven on the bridge,
// the invisible Kecleon and the Devon Scope, the Berry Master's friend, Gabby & Ty, the other four Kecleons, the Ancient
// Tomb entrance (a blocker rock until FLAG_REGI_DOORS_OPENED, as ch4/ch6 seal their Regi entrances).
// converter/gen_map_content.py includes this file twice in the generated zone file 0948_auto_Route120.s: the entries
// below are scripts 1-15, the generated signs/people follow. Text: src/text/scenes/Route120.txt (T_* below). People
// and triggers: data/story/ch7.json (outdoor uid = 100 + Sapphire local id). Map scripts: scenes/Route120_init.inc.
// Route 120's trainers (Colin, Robert, Carlos, Jenna, Brandon, Jennifer, Chip, Clarissa, Angelica) are placed by the
// trainers patch, Keigo and Tsunao (mountain / tree disguise in Sapphire) by data/story/ch7.json. (The far west strip,
// x 0-7 y 0-31 with Colin, was in Fortree's zone 16 until every map had its own zone up to its edges: zone_edges.)
// Not ported (Black 2's maps are 3D models: no setmetatile): Route120_MapScript1_151686 (ON_LOAD: the rock wall of the
// Ancient Tomb entrance = the blocker rock; the bridge tiles Kecleon0/1 that Steven's scene and the Devon Scope draw
// over the camouflaged Kecleon 2 (object 36, left out: the invisible Kecleon 30 stands there)), the weather by tile
// (Route120_EventScript_1516EA: rain / clouds / sun by the player's tile: Black 2's weather is per zone).
#ifdef SCENE_ENTRIES
    ScriptEntry R120_Init               // 1: Route120_MapScript1_1516DF (zone init)
    ScriptEntry R120_Beauty             // 2: object 23, Route120_EventScript_151739
    ScriptEntry R120_Steven             // 3: object 31, Route120_EventScript_151853
    ScriptEntry R120_Kecleon30          // 4: object 30, Route120_EventScript_151998
    ScriptEntry R120_Kecleon1           // 5: object 37, Route120_EventScript_Kecleon1
    ScriptEntry R120_Kecleon2           // 6: object 38, Route120_EventScript_Kecleon2
    ScriptEntry R120_Kecleon3           // 7: object 39, Route120_EventScript_Kecleon3
    ScriptEntry R120_Kecleon4           // 8: object 41, Route120_EventScript_Kecleon4
    ScriptEntry R120_Kecleon5           // 9: object 40, Route120_EventScript_Kecleon5
    ScriptEntry R120_HideKecleons       // 10: scene condition C7_KECLEON_HIDDEN 0 (MOVEMENT_TYPE_INVISIBLE)
    ScriptEntry R120_FieldLoad          // 11: field load / return: the Kecleons are hidden again
    ScriptEntry R120_Gabby1             // 12: object 18, Route120_EventScript_1AE4A2 (TRAINER_GABBY_AND_TY_3)
    ScriptEntry R120_Ty1                // 13: object 17, Route120_EventScript_1AE4C2
    ScriptEntry R120_Gabby2             // 14: object 19, Route120_EventScript_1AE562 (TRAINER_GABBY_AND_TY_6)
    ScriptEntry R120_Ty2                // 15: object 20, Route120_EventScript_1AE582
#else
#include "scenes/ch7_lib.inc"
#include "scenes/ch7_test.inc"

#define T_StevenIntro 0
#define T_StevenNo 1
#define T_StevenReady 2
#define T_StevenTrueStrength 3
#define T_StevenUsedScope 4
#define T_StevenAfter 5
#define T_StevenAfter2 6
#define T_BerryAsk 7
#define T_BerryYes 8
#define T_BerryNo 9
#define T_BerryGot 10
#define T_BerryDone 11
#define T_SomethingUnseeable 12
#define T_UnseeableUseDevonScope 13
#define T_UseDevonScopeMonAttacked 14
#define T_BagFull 15
#define T_GT0 16                        // Gabby & Ty: 14 lines from here (scenes/gabby_ty.inc's order)
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

#define R120_STEVEN 131                 // object 31 at (13,15) (FLAG_HIDE_STEVEN_ROUTE120)
#define R120_KECLEON 130                // object 30 at (12,16) (FLAG_HIDE_KECLEON_ROUTE120_1)
#define R120_K1 137                     // object 37 (FLAG_HIDE_KECLEON_ROUTE120_3)
#define R120_K2 138                     // object 38 (_4)
#define R120_K3 139                     // object 39 (_5)
#define R120_K4 141                     // object 41 (_6)
#define R120_K5 140                     // object 40 (_7)

R120_Init:                              // Route120_MapScript1_1516DF
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
#ifdef HOENN_TEST_CH7
    VMCall Test_Ch7Start
#endif
    VMCall Sub_GabbyTyUpdate            // call Route120_EventScript_1AE313
    h_keep_banner                       // the Kecleon scene below leaves the place-name banner shown
    VMHalt

R120_HideKecleons:
    h_keep_banner_end                   // (later scripts close the banner again, as in Black 2)
    h_setvar C7_KECLEON_HIDDEN, 1
    c7_hide_kecleon R120_KECLEON, FLAG_HIDE_KECLEON_ROUTE120_1
    c7_hide_kecleon R120_K1, FLAG_HIDE_KECLEON_ROUTE120_3
    c7_hide_kecleon R120_K2, FLAG_HIDE_KECLEON_ROUTE120_4
    c7_hide_kecleon R120_K3, FLAG_HIDE_KECLEON_ROUTE120_5
    c7_hide_kecleon R120_K4, FLAG_HIDE_KECLEON_ROUTE120_6
    c7_hide_kecleon R120_K5, FLAG_HIDE_KECLEON_ROUTE120_7
    h_waitmovement
    VMHalt

R120_FieldLoad:
    h_setvar C7_KECLEON_HIDDEN, 0
    VMHalt

// The Berry Master's friend: one of five Berries a day (dotimebasedevents + FLAG_DAILY_RECEIVED_BERRY_ROUTE120:
// Black 2's midnight reset). Sapphire picks it from the trainer ID's last digit (Figy 0/5, Wiki 1/6, Mago 2/7, Aguav
// 3/8, Iapapa 4/9; Black 2's scripts cannot read the trainer ID): here a random one of the five each day.
R120_Beauty:                            // Route120_EventScript_151739
    c7_talk
    h_goto_if_set FLAG_DAILY_RECEIVED_BERRY_ROUTE120, L_R120_BerryDone
    h_yesno T_BerryAsk, C7_TMP          // Give the case a shake, and out pops a Pokéblock... Do you understand?
    h_goto_if_no C7_TMP, L_R120_BerryNo
    h_msgbox T_BerryYes                 // Yes, yes. You understand what I mean. You should take this.
    VMJump L_R120_GiveBerry
L_R120_BerryNo:
    h_msgbox T_BerryNo                  // Oh... But it is important to make your own impressions, I guess...
L_R120_GiveBerry:
    h_random C7_TMP, 5                  // ITEM_FIGY_BERRY .. ITEM_IAPAPA_BERRY (Black 2 keeps Gen 3's berry order)
    WorkAdd C7_TMP, ITEM_FIGY_BERRY
    h_closemessage                      // (Black 2's item script opens its own window)
    c7_giveitem_var C7_TMP
    h_goto_if_eq HLIB_RESULT, 0, L_R120_BagFull
    h_setflag FLAG_DAILY_RECEIVED_BERRY_ROUTE120
    h_msgbox T_BerryGot                 // I think that Berry is rare. I hope you raise it with loving care.
    h_release
L_R120_BerryDone:
    h_msgbox T_BerryDone                // I'll get more Berries from the Berry Master.
    h_release
L_R120_BagFull:                         // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release

// Steven on the bridge (Route120_EventScript_151853, object 31): the Kecleon on the bridge is object 30
R120_Steven:
    c7_talk
    h_getplayerfacing C7_POS            // VAR_FACING: 0 up (Sapphire 2 = north), 2 left (Sapphire 3 = west)
    h_goto_if_set FLAG_NOT_READY_FOR_BATTLE_ROUTE120, L_R120_StevenAskAgain
    h_yesno T_StevenIntro, C7_TMP       // Steven: Hm? <player>, hi. ... are your Pokémon ready for battle?
    h_goto_if_no C7_TMP, L_R120_StevenNotReady
    VMJump L_R120_StevenBegins
L_R120_StevenAskAgain:                  // Route120_EventScript_151884
    h_yesno T_StevenReady, C7_TMP       // Steven: <player>, are your Pokémon ready for battle?
    h_goto_if_no C7_TMP, L_R120_StevenNotReady
L_R120_StevenBegins:                    // Route120_EventScript_15189D
    h_msgbox T_StevenTrueStrength       // Steven: <player>, show me your true power as a Trainer!
    h_closemessage
    h_goto_if_eq C7_POS, 0, L_R120_PlayerFaceLeft
    h_goto_if_eq C7_POS, 2, L_R120_PlayerStepDownLeft
    VMJump L_R120_KecleonScene
L_R120_PlayerFaceLeft:                  // Route120_EventScript_15197F
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    VMJump L_R120_KecleonScene
L_R120_PlayerStepDownLeft:              // Route120_EventScript_15198A
    h_applymovement 255, Mv_R120_PlayerDownLeft
    h_waitmovement
L_R120_KecleonScene:
    h_applymovement R120_STEVEN, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_delay 20
    h_buffer_player
    h_msgbox_actor T_StevenUsedScope, R120_STEVEN   // Steven used the Devon Scope. ... The startled Pokémon attacked!
    h_closemessage
    h_applymovement R120_KECLEON, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_applymovement R120_KECLEON, Mv_C7_KecleonAppears
    h_waitmovement
    h_playmoncry SPECIES_KECLEON        // waitse, playmoncry SPECIES_KECLEON, 2, delay 40, waitmoncry
    h_delay 40
    h_waitmoncry
    h_static_battle SPECIES_KECLEON, 30, FLAG_HIDE_KECLEON_ROUTE120_1, R120_KECLEON
    // Route120_EventScript_151908: after the battle (won, caught or run from)
    h_applymovement R120_STEVEN, Common_Movement_WalkInPlaceFastestDown
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_buffer_player
    h_msgbox_actor T_StevenAfter, R120_STEVEN   // Steven: I see... Your battle style is intriguing. ... Devon Scope.
    h_closemessage                      // (Black 2's item script opens its own window)
    h_giveitem ITEM_DEVON_SCOPE         // (Sapphire does not look at giveitem's result here)
    h_setflag FLAG_RECEIVED_DEVON_SCOPE
    h_msgbox_actor T_StevenAfter2, R120_STEVEN  // Steven: <player>. I enjoy seeing Pokémon and Trainers ...
    h_closemessage
    h_applymovement R120_STEVEN, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_delay 50
    c7_npc_fly_out R120_STEVEN, FLAG_HIDE_STEVEN_ROUTE120
    h_release
L_R120_StevenNotReady:                  // Route120_EventScript_151877
    h_msgbox T_StevenNo                 // Steven: No? I'll wait here, so you can get ready.
    h_setflag FLAG_NOT_READY_FOR_BATTLE_ROUTE120
    h_release

R120_Kecleon30:                         // Route120_EventScript_151998 (MSGBOX_NPC)
    c7_talk
    h_msgbox T_SomethingUnseeable
    h_release

R120_Kecleon1:
    c7_kecleon R120_K1, FLAG_HIDE_KECLEON_ROUTE120_3, T_SomethingUnseeable, T_UnseeableUseDevonScope, T_UseDevonScopeMonAttacked
R120_Kecleon2:
    c7_kecleon R120_K2, FLAG_HIDE_KECLEON_ROUTE120_4, T_SomethingUnseeable, T_UnseeableUseDevonScope, T_UseDevonScopeMonAttacked
R120_Kecleon3:
    c7_kecleon R120_K3, FLAG_HIDE_KECLEON_ROUTE120_5, T_SomethingUnseeable, T_UnseeableUseDevonScope, T_UseDevonScopeMonAttacked
R120_Kecleon4:
    c7_kecleon R120_K4, FLAG_HIDE_KECLEON_ROUTE120_6, T_SomethingUnseeable, T_UnseeableUseDevonScope, T_UseDevonScopeMonAttacked
R120_Kecleon5:
    c7_kecleon R120_K5, FLAG_HIDE_KECLEON_ROUTE120_7, T_SomethingUnseeable, T_UnseeableUseDevonScope, T_UseDevonScopeMonAttacked

// Gabby & Ty (data/scripts/gabby_and_ty.inc: one pair stands here at a time, Sub_GabbyTyUpdate)
R120_Gabby1:
    c4_gabby_ty TRAINER_GABBY_AND_TY_3, GT_GABBY, 0
R120_Ty1:
    c4_gabby_ty TRAINER_GABBY_AND_TY_3, GT_TY, 0
R120_Gabby2:
    c4_gabby_ty TRAINER_GABBY_AND_TY_6, GT_GABBY, 0
R120_Ty2:
    c4_gabby_ty TRAINER_GABBY_AND_TY_6, GT_TY, 0

    .balign 4, 0
Mv_R120_PlayerDownLeft:                 // Route120_Movement_151995
    walk_down
    walk_left
    step_end
#include "common/movement.inc"
#endif
