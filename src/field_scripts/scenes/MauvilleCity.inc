// Mauville City's story (Sapphire data/maps/MauvilleCity/scripts.inc; chapter Ch3 part 3b, ch3b agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in 0812_auto_MauvilleCity.s: the entries below are scripts 1-5,
// the generated signs/people follow. Text: src/text/scenes/MauvilleCity.txt (lines T_* below; chapter Ch6 appends its
// Wattson lines after line 14). People: data/story/ch3b.json (uid = 100 + Sapphire local id). Map scripts:
// scenes/MauvilleCity_init.inc. Route 117's Day-Care Man is in scenes/Route117.inc (Route 117's own zone 437 since the
// banner code patch, world.json "zone_rects").
// Chapter Ch6's beat in this file (notes/STORY_CHAPTERS.md): Wattson outside the Gym (Basement Key, New Mauville,
// TM24) is script 5: write it in scenes/MauvilleCity_Ch6.inc (label Ch6_Wattson; text after line 14 of
// MauvilleCity.txt), it is picked up automatically. Wattson's object (uid 108) is in data/story/ch3b.json, hidden by
// FLAG_HIDE_WATTSON_MAUVILLE (set at new game) until Petalburg's Gym clears it.
#ifdef SCENE_ENTRIES
    ScriptEntry MC_Init                 // 1: MauvilleCity_OnTransition (zone init)
    ScriptEntry MC_SchoolKidM           // 2: object 5
    ScriptEntry MC_WallysUncle          // 3: object 7
    ScriptEntry MC_Wally                // 4: object 6
    ScriptEntry Ch6_Wattson             // 5: object 8 (chapter Ch6)
#else
#include "scenes/ch3b_lib.inc"

#define T_ExplainTV 0
#define T_BeenCheckingTV 1
#define T_UnclePeppy 2
#define T_UncleCanYouBattle 3
#define T_WallyChallengeGym 4
#define T_UnclePushingIt 5
#define T_WallyBeatAnyone 6
#define T_WallyWillYouBattle 7
#define T_WallyPleaseBattle 8
#define T_WallyUncleWontKnow 9
#define T_WallyHereICome 10
#define T_WallyGoBack 11
#define T_WallyThankYou 12
#define T_UncleNoNeed 13
#define T_UncleVisitUs 14

#define MC_WALLY 106                    // object 6 (FLAG_HIDE_WALLY_MAUVILLE)
#define MC_UNCLE 107                    // object 7 (FLAG_HIDE_WALLY_FATHER_MAUVILLE)
#define MC_X(x) (248+(x))               // Mauville's Sapphire tile -> world tile (b2tools/world.py offsets)
#define MC_Z(z) (200+(z))

MC_Init:                                // MauvilleCity_OnTransition
    h_setflag FLAG_VISITED_MAUVILLE_CITY
    h_clearflag FLAG_HIDE_OCEANIC_MUSEUM_VISITORS
    h_setflag FLAG_SYS_TV_START
    h_clearflag FLAG_MAUVILLE_GYM_BARRIERS_STATE
    h_setvar VAR_MAUVILLE_GYM_STATE, 0
    h_goto_if_unset FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON, L_MC_InitDone
    h_clearflag FLAG_HIDE_WATTSON_MAUVILLE_GYM   // MauvilleCity_EventScript_MoveWattsonBackToGym
    h_setflag FLAG_HIDE_WATTSON_MAUVILLE
L_MC_InitDone:
#ifdef HOENN_EMERALD
    h_clearflag FLAG_EM_MIRAGE_TOWER_KEEP           // (2026-10-18) a walk north into Route 111 rolls the Mirage Tower again (scenes/emerald/Route111_Mirage.inc)
#endif
#ifdef HOENN_TEST_CH3B
    VMCall Test_Ch3bStart
#endif
    VMHalt

MC_SchoolKidM:                          // MauvilleCity_EventScript_SchoolKidM
    c3_talk
    h_goto_if_set FLAG_TV_EXPLAINED, L_MC_TVExplained
    h_msgbox T_ExplainTV                // Hi, do you check out TV at all? ...
    h_setflag FLAG_TV_EXPLAINED
    h_release
L_MC_TVExplained:
    h_msgbox T_BeenCheckingTV
    h_release

MC_WallysUncle:                         // MauvilleCity_EventScript_WallysUncle
    c3_talk
    h_goto_if_set FLAG_DECLINED_WALLY_BATTLE_MAUVILLE, L_MC_UncleAskBattle
    h_msgbox T_UnclePeppy               // Uncle: It's because of Pokémon that this boy's got more pep...
    VMJump L_MC_UncleTurnBack
L_MC_UncleAskBattle:
    h_buffer_player
    h_msgbox T_UncleCanYouBattle        // Uncle: <player>, was it? On Wally's behalf...
L_MC_UncleTurnBack:
    h_closemessage
    h_turnobject MC_UNCLE, 2            // Common_Movement_FaceOriginalDirection (FACE_LEFT)
    h_release

MC_Wally:                               // MauvilleCity_EventScript_Wally (lockall)
    h_lock
    h_buffer_player
    h_goto_if_set FLAG_DECLINED_WALLY_BATTLE_MAUVILLE, L_MC_WallyAgain
    h_applymovement MC_WALLY, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_msgbox_actor T_WallyChallengeGym, MC_WALLY        // Wally: Aww, Uncle, please? ...
    h_msgbox_actor T_UnclePushingIt, MC_UNCLE           // Uncle: Now hold on, Wally. ...
    h_msgbox_actor T_WallyBeatAnyone, MC_WALLY          // Wally: I'm not pushing it. ...
    h_closemessage
    h_faceplayer                                        // Common_Movement_FacePlayer
    h_applymovement MC_WALLY, Mv_MC_Notice              // SE_PIN, "!", delay_48
    h_waitmovement
    h_yesno_actor T_WallyWillYouBattle, MC_WALLY, C3B_A // Wally: Oh! Hi, <player>! ... will you have a battle with me?
    VMJump L_MC_BattlePrompt
L_MC_WallyAgain:                        // MauvilleCity_EventScript_WallyRequestBattleAgain
    h_faceplayer
    h_yesno_actor T_WallyPleaseBattle, MC_WALLY, C3B_A
L_MC_BattlePrompt:                      // MauvilleCity_EventScript_BattleWallyPrompt
    h_goto_if_no C3B_A, L_MC_DeclineBattle
    h_msgbox_actor T_WallyHereICome, MC_WALLY           // MauvilleCity_EventScript_BattleWally
    h_closemessage
    h_trainerbattle TRAINER_WALLY_2                     // (in battle: "Wally: ... I lost...")
    h_applymovement MC_WALLY, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_msgbox_actor T_WallyGoBack, MC_WALLY              // Wally: Uncle... I'll go back to Verdanturf...
    h_closemessage
    h_faceplayer
    h_buffer_player
    h_msgbox_actor T_WallyThankYou, MC_WALLY            // <player>, thank you. Being a Trainer is tough, isn't it? ...
    h_closemessage
    h_applymovement MC_WALLY, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_msgbox_actor T_UncleNoNeed, MC_UNCLE              // Uncle: Wally, there's no need to be so down on yourself. ...
    h_closemessage
    h_getplayerfacing C3B_A             // VAR_FACING: 2 north (the player below Wally), 4 east (west of him)
    h_goto_if_eq C3B_A, 3, L_MC_ExitEast
    h_applymovement MC_WALLY, Mv_MC_WallyExitNorth1     // MauvilleCity_EventScript_WallyAndUncleExitNorth
    h_applymovement MC_UNCLE, Mv_MC_UncleExitNorth1
    h_waitmovement
    h_applymovement MC_WALLY, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 30
    h_applymovement MC_UNCLE, Mv_MC_UncleApproachNorth
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_buffer_player
    h_msgbox_actor T_UncleVisitUs, MC_UNCLE             // Uncle: <player>, it just dawned on me ...
    h_closemessage
    h_applymovement MC_WALLY, Mv_MC_WallyExit2
    h_applymovement MC_UNCLE, Mv_MC_UncleExitNorth2
    h_waitmovement
    VMJump L_MC_DefeatedWally
L_MC_ExitEast:                          // MauvilleCity_EventScript_WallyAndUncleExitEast
    h_applymovement MC_WALLY, Mv_MC_WallyExitEast1
    h_applymovement MC_UNCLE, Mv_MC_UncleExitEast1
    h_waitmovement
    h_applymovement MC_WALLY, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 30
    h_applymovement MC_UNCLE, Mv_MC_UncleApproachEast
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_buffer_player
    h_msgbox_actor T_UncleVisitUs, MC_UNCLE
    h_closemessage
    h_applymovement MC_WALLY, Mv_MC_WallyExit2
    h_applymovement MC_UNCLE, Mv_MC_UncleExitEast2
    h_waitmovement
L_MC_DefeatedWally:                     // MauvilleCity_EventScript_DefeatedWally
    h_removeobject MC_WALLY, FLAG_HIDE_WALLY_MAUVILLE
    h_removeobject MC_UNCLE, FLAG_HIDE_WALLY_FATHER_MAUVILLE
    h_clearflag FLAG_HIDE_WALLY_WANDAS_HOUSE
    h_clearflag FLAG_HIDE_WALLY_FATHER_WANDAS_HOUSE
    h_setflag FLAG_DEFEATED_WALLY_MAUVILLE
#ifdef HOENN_EMERALD                    // Emerald (emerald_ch0_3): Scott watched the match (scenes/emerald/MauvilleCity.inc)
    VMCall Sub_Em_MC_Scott
#endif
    h_release
L_MC_DeclineBattle:                     // MauvilleCity_EventScript_DeclineWallyBattle
    h_setflag FLAG_DECLINED_WALLY_BATTLE_MAUVILLE
    h_buffer_player
    h_msgbox_actor T_WallyUncleWontKnow, MC_WALLY       // Wally: Oh... If you won't battle me, <player>...
    h_release

#if __has_include("scenes/MauvilleCity_Ch6.inc")
#include "scenes/MauvilleCity_Ch6.inc"
#else
Ch6_Wattson:                            // MauvilleCity_EventScript_Wattson: chapter Ch6's beat (hidden until then)
    h_lock
    h_release
#endif

    .balign 4, 0
Mv_MC_Notice:                           // Common_Movement_ExclamationMark + Common_Movement_Delay48
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_MC_WallyExitNorth1:                  // MauvilleCity_Movement_WallyExitNorth1
    walk_left 2
    walk_down 2
    walk_left
    step_end
Mv_MC_WallyExitEast1:                   // MauvilleCity_Movement_WallyExitEast1
    walk_down 2
    walk_left 3
    step_end
Mv_MC_WallyExit2:                       // MauvilleCity_Movement_WallyExitNorth2 / WallyExitEast2
    delay_16 2
    walk_left 8
    step_end
Mv_MC_UncleExitNorth1:                  // MauvilleCity_Movement_WallysUncleExitNorth1
    walk_left 3
    walk_down 2
    step_end
Mv_MC_UncleExitEast1:                   // MauvilleCity_Movement_WallysUncleExitEast1
    walk_left
    walk_down 2
    walk_left 2
    step_end
Mv_MC_UncleApproachNorth:               // MauvilleCity_Movement_WallysUncleApproachPlayerNorth
    walk_right 2
    walk_in_place_fastest_up
    step_end
Mv_MC_UncleApproachEast:                // MauvilleCity_Movement_WallysUncleApproachPlayerEast
    walk_right
    walk_up
    step_end
Mv_MC_UncleExitNorth2:                  // MauvilleCity_Movement_WallysUncleExitNorth2
    walk_left 8
    step_end
Mv_MC_UncleExitEast2:                   // MauvilleCity_Movement_WallysUncleExitEast2
    walk_down
    walk_left 8
    step_end
#include "common/movement.inc"
#include "scenes/ch3b_test.inc"
#ifdef HOENN_EMERALD
#include "scenes/emerald/MauvilleCity.inc"
#endif
#endif
