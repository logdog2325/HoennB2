// MeteorFalls_1F_1R (zone 128): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// Messages: src/text/script/0147_room_MeteorFalls_1F_1R.txt
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch4
#include "hoenn_story.inc"  // ch4
#include "scenes/ch4_lib.inc"  // ch4

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry MF_TeamsScene           // 3: trigger (14,18) VAR_METEOR_FALLS_STATE 0 (MeteorFalls_1F_1R_EventScript_15C49C)  // story:
    ScriptEntry MF_ProfCozmo            // 4: object 10 (MeteorFalls_1F_1R_EventScript_15C656)  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder down (5,4) -> MeteorFalls_B1F_1R warp 4 (3,23)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 130, 3, 2, 23, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 0, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch4, ch4 agent 2026-10-07: Sapphire data/maps/MeteorFalls_1F_1R/scripts.inc; the cave builder leaves this
// part alone). Team Aqua takes the Meteorite, Team Magma (Maxie) chases them; Prof. Cozmo. People and the trigger:
// data/story/ch4.json (uid = Sapphire local id: 5/6 Aqua grunts, 7 Maxie, 8/9 Magma grunts, 10 Cozmo). Text lines
// 1-10 (line 0 is the generated sign's). Sapphire's speakers are plain message boxes; here the balloon comes from the
// person speaking (Maxie's "Hold it right there" from off-screen: a plain window).
// EMERALD (emerald_ch45_magma 2026-10-12; pokeemerald MeteorFalls_1F_1R_EventScript_MagmaStealsMeteoriteScene): Team Magma
// steals the Meteorite and Archie's Team Aqua chases them: Ruby's flow, so the same objects with swapped models
// (data/story/ch4.json "model_emerald": 5/6 Magma grunts, 7 Archie, 8/9 Aqua grunts), Emerald's text
// (src/text/script/emerald/0147_room_MeteorFalls_1F_1R.txt, same line indices), its encounter songs and its movement lists
// (Archie, the Aqua grunts and the Magma grunts leave 7 tiles, not 8; the player ends facing right).
#ifdef HOENN_EMERALD
#include "scenes/em_magma_lib.inc"
#endif
#define T_WithThisMeteorite 1   // MeteorFalls_1F_1R_Text_193237
#define T_GetInTheWay 2         // MeteorFalls_1F_1R_Text_193268
#define T_HoldIt 3              // MeteorFalls_1F_1R_Text_1932C5
#define T_EvenMagma 4           // MeteorFalls_1F_1R_Text_193320
#define T_IAmMaxie 5            // MeteorFalls_1F_1R_Text_1933EC
#define T_GiveChase 6           // MeteorFalls_1F_1R_Text_193720
#define T_MustHurry 7           // MeteorFalls_1F_1R_Text_193747
#define T_KeepAnEye 8           // MeteorFalls_1F_1R_Text_1937AA
#define T_CozmoFirst 9          // MeteorFalls_1F_1R_Text_1937EB
#define T_CozmoAgain 10         // MeteorFalls_1F_1R_Text_19396A

MF_TeamsScene:                              // MeteorFalls_1F_1R_EventScript_15C49C
    h_lock
#ifdef HOENN_EMERALD
    em_bgm_magma                            // playbgm MUS_ENCOUNTER_MAGMA
#endif
    WordSetPlayerName 0
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_delay 30
    h_applymovement 5, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_msgbox_actor T_WithThisMeteorite, 5
    h_closemessage
    h_applymovement 5, Common_Movement_WalkInPlaceFastestUp
    h_applymovement 6, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_applymovement 5, Common_Movement_ExclamationMark     // (the "!" plays its own sound: no SE_PIN)
    h_waitmovement
    h_applymovement 5, Common_Movement_Delay48
    h_waitmovement
    h_msgbox_actor T_GetInTheWay, 5
    h_closemessage
    h_applymovement 5, Mv_MF_GruntSteps
    h_waitmovement
    h_msgbox_info T_HoldIt
    h_closemessage
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_applymovement 5, Common_Movement_WalkInPlaceFastestLeft
    h_applymovement 6, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_addobject 7, FLAG_HIDE_OTHER_TEAM_METEOR_FALLS_1F
    h_addobject 8, FLAG_HIDE_OTHER_TEAM_METEOR_FALLS_1F
    h_addobject 9, FLAG_HIDE_OTHER_TEAM_METEOR_FALLS_1F
#ifdef HOENN_EMERALD
    em_bgm_aqua                             // playbgm MUS_ENCOUNTER_AQUA
#endif
    h_applymovement 7, Mv_MF_MaxieArrives
    h_applymovement 8, Mv_MF_MagmaArrives
    h_applymovement 9, Mv_MF_MagmaArrives
    h_waitmovement
    h_applymovement 5, Common_Movement_WalkInPlaceFastestLeft
    h_applymovement 6, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_EvenMagma, 5
    h_closemessage
    h_applymovement 255, Mv_MF_PlayerStepsBack
    h_applymovement 5, Mv_MF_Grunt5Escapes
    h_applymovement 6, Mv_MF_Grunt6Escapes
    h_waitmovement
    h_removeobject 5, FLAG_HIDE_GRUNTS_METEOR_FALLS_1F
    h_removeobject 6, FLAG_HIDE_GRUNTS_METEOR_FALLS_1F
    h_applymovement 7, Mv_MF_MaxieToPlayer
    h_waitmovement
    h_msgbox_actor T_IAmMaxie, 7            // (.ifdef SAPPHIRE: MeteorFalls_1F_1R_Text_1933EC)
    h_closemessage
    h_applymovement 8, Mv_MF_Magma8Up
    h_applymovement 9, Mv_MF_Magma9Up
    h_waitmovement
    h_msgbox_actor T_GiveChase, 8
    h_applymovement 7, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_msgbox_actor T_MustHurry, 7
    h_applymovement 7, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_KeepAnEye, 7
    h_closemessage
    h_applymovement 7, Mv_MF_MaxieLeaves
    h_applymovement 8, Mv_MF_Magma8Leaves
    h_applymovement 9, Mv_MF_Magma9Leaves
    h_waitmovement
#ifdef HOENN_EMERALD
    h_fadedefaultbgm
#endif
    h_removeobject 7, FLAG_HIDE_OTHER_TEAM_METEOR_FALLS_1F
    h_removeobject 8, FLAG_HIDE_OTHER_TEAM_METEOR_FALLS_1F
    h_removeobject 9, FLAG_HIDE_OTHER_TEAM_METEOR_FALLS_1F
    h_setflag FLAG_HIDE_GRUNTS_BLOCKING_CABLE_CAR
    h_setvar VAR_METEOR_FALLS_STATE, 1
    h_release

MF_ProfCozmo:                               // MeteorFalls_1F_1R_EventScript_15C656
    c4_talk
    h_goto_if_set FLAG_MET_PROF_COSMO, L_MF_CozmoAgain
    h_setflag FLAG_MET_PROF_COSMO
    h_msgbox T_CozmoFirst
    h_release
L_MF_CozmoAgain:
    h_msgbox T_CozmoAgain
    h_release

    .balign 4, 0
Mv_MF_GruntSteps:                           // MeteorFalls_1F_1R_Movement_15C5EE
    walk_right 2
#ifdef HOENN_EMERALD
    walk_in_place_fastest_up                // MeteorFalls_1F_1R_Movement_MagmaGruntApproachPlayer
#endif
    step_end
Mv_MF_Grunt5Escapes:                        // MeteorFalls_1F_1R_Movement_15C5F1
    walk_fast_up 2
#ifdef HOENN_EMERALD
    walk_fast_right 7
#else
    walk_fast_right 8
#endif
    step_end
Mv_MF_Grunt6Escapes:                        // MeteorFalls_1F_1R_Movement_15C5FC
    walk_fast_up 3
#ifdef HOENN_EMERALD
    walk_fast_right 7
#else
    walk_fast_right 8
#endif
    step_end
Mv_MF_MaxieArrives:                         // MeteorFalls_1F_1R_Movement_15C608
    walk_right 6
    step_end
Mv_MF_MagmaArrives:                         // MeteorFalls_1F_1R_Movement_15C60F / 15C617
    delay_16 2
    walk_right 5
    step_end
Mv_MF_MaxieLeaves:                          // MeteorFalls_1F_1R_Movement_15C61F
#ifdef HOENN_EMERALD
    walk_right 7
#else
    walk_right 8
#endif
    step_end
Mv_MF_MaxieToPlayer:                        // MeteorFalls_1F_1R_Movement_15C628
    walk_right 2
    walk_up 2
    walk_in_place_fastest_left
    step_end
Mv_MF_Magma8Leaves:                         // MeteorFalls_1F_1R_Movement_15C62E
    walk_up 2
#ifdef HOENN_EMERALD
    walk_right 7
#else
    walk_right 8
#endif
    step_end
Mv_MF_Magma8Up:                             // MeteorFalls_1F_1R_Movement_15C639
    walk_right 3
    walk_in_place_fastest_up
    step_end
Mv_MF_Magma9Leaves:                         // MeteorFalls_1F_1R_Movement_15C63E
    walk_up 3
#ifdef HOENN_EMERALD
    walk_right 7
#else
    walk_right 8
#endif
    step_end
Mv_MF_Magma9Up:                             // MeteorFalls_1F_1R_Movement_15C64A
    walk_right 3
    walk_in_place_fastest_up
    step_end
Mv_MF_PlayerStepsBack:                      // MeteorFalls_1F_1R_Movement_15C64F
    walk_in_place_fastest_down
    delay_4
    walk_in_place_fastest_right
    lock_facing_direction
    walk_left
    unlock_facing_direction
#ifdef HOENN_EMERALD
    face_right
#endif
    step_end
#include "common/movement.inc"
