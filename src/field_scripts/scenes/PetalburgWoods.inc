// Petalburg Woods' story (Sapphire data/maps/PetalburgWoods/scripts.inc; chapter Ch1): the Devon researcher and the
// Team Aqua grunt, the Miracle Seed. converter/gen_map_content.py includes this file twice in the generated zone file
// 0074_auto_PetalburgWoods.s: the entries below become scripts 1-4, the generated signs/people follow. Text:
// src/text/scenes/PetalburgWoods.txt (lines 0-12). Map scripts: scenes/PetalburgWoods_init.inc. Story objects
// (data/story/ch1.json, uid 100 + Sapphire local id): grunt 103, researcher 104, girl 113; the two triggers.
// Zone tiles = Sapphire tiles + (23, 12) (the woods' own matrix, world.json "standalone" origins).
// Sapphire's grunt is OBJ_EVENT_GFX_VAR_1 (Common_EventScript_SetupEvilTeamGfxIds: Aqua in Sapphire): the Aqua grunt
// model is placed directly (notes/STORY_COMMON.md).
#ifdef SCENE_ENTRIES
    ScriptEntry PW_Init             // 1: PetalburgWoods_OnTransition (zone init): nothing left to do
    ScriptEntry PW_SceneLeft        // 2: trigger (26,23) PetalburgWoods_EventScript_15CCA8
    ScriptEntry PW_SceneRight       // 3: trigger (27,23) PetalburgWoods_EventScript_15CD42
    ScriptEntry PW_MiracleSeed      // 4: girl (PetalburgWoods_EventScript_15CEDC), Miracle Seed
#if __has_include("scenes/PetalburgWoods_Postgame.inc")
#include "scenes/PetalburgWoods_Postgame.inc"   // 5: post-game Celebi
#endif
#else
#define PW_GRUNT 103
#define PW_DEVON 104
#ifndef TRAINER_PETALBURG_WOODS_GRUNT
#define TRAINER_PETALBURG_WOODS_GRUNT TRAINER_GRUNT_9   /* Sapphire's alias (pokeruby constants/version.inc) */
#endif

PW_Init:                            // Common_EventScript_SetupEvilTeamGfxIds (the Aqua model is placed directly)
#if __has_include("scenes/PetalburgWoods_Postgame.inc")
    VMCall PG_PW_Init               // post-game: Celebi shown (scenes/PetalburgWoods_Postgame.inc)
#endif
    VMHalt

PW_SceneLeft:                       // the player came up at (26,23), below the researcher (26,20)
    h_lock
    VMCall Sub_PW_Search
    h_applymovement PW_DEVON, Mv_PW_DevonApproachLeft
    h_waitmovement
    h_msgbox_actor 1, PW_DEVON      // Hello, have you seen any Pokémon called Shroomish around here? ...
    h_closemessage
    h_playbgm MUS_EVIL_TEAM
    h_applymovement PW_GRUNT, Mv_PW_GruntArrive
    h_waitmovement
    h_msgbox_actor 2, PW_GRUNT      // I was going to ambush you, but you had to dawdle in Petalburg Woods ...
    h_closemessage
    h_applymovement PW_GRUNT, Mv_PW_GruntDownLeft
    h_waitmovement
    h_applymovement PW_DEVON, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor 3, PW_GRUNT      // You! Devon Researcher! Hand over those papers!
    h_closemessage
    h_applymovement PW_DEVON, Mv_PW_DevonHideLeft
    h_waitmovement
    h_msgbox_actor 4, PW_DEVON      // Aiyeeeh! You're a Pokémon Trainer, aren't you? ...
    h_applymovement PW_GRUNT, Mv_PW_GruntStep
    h_waitmovement
    h_msgbox_actor 5, PW_GRUNT      // Hunh? What do you think you're doing? ... Come on and battle me!
    h_closemessage
    h_trainerbattle TRAINER_PETALBURG_WOODS_GRUNT   // (in battle: "You're kidding me! You're tough!")
    h_applymovement PW_GRUNT, Mv_PW_GruntBackUp
    h_waitmovement
    VMCall Sub_PW_Thanks
    h_applymovement PW_DEVON, Mv_PW_DevonLeaveLeft
    h_waitmovement
    VMJump L_PW_End

PW_SceneRight:                      // the player came up at (27,23)
    h_lock
    VMCall Sub_PW_Search
    h_applymovement PW_DEVON, Mv_PW_DevonApproachRight
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor 1, PW_DEVON
    h_closemessage
    h_playbgm MUS_EVIL_TEAM
    h_applymovement PW_GRUNT, Mv_PW_GruntArrive
    h_waitmovement
    h_msgbox_actor 2, PW_GRUNT
    h_closemessage
    h_applymovement PW_GRUNT, Mv_PW_GruntDownRight
    h_waitmovement
    h_applymovement PW_DEVON, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor 3, PW_GRUNT
    h_closemessage
    h_applymovement PW_DEVON, Mv_PW_DevonHideRight
    h_waitmovement
    h_msgbox_actor 4, PW_DEVON
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor 5, PW_GRUNT
    h_closemessage
    h_trainerbattle TRAINER_PETALBURG_WOODS_GRUNT
    h_applymovement PW_GRUNT, Mv_PW_GruntBackUp
    h_waitmovement
    VMCall Sub_PW_Thanks
    h_applymovement PW_DEVON, Mv_PW_DevonLeaveRight
    h_waitmovement
L_PW_End:                           // PetalburgWoods_EventScript_15CE69
    h_removeobject PW_DEVON, FLAG_HIDE_DEVON_PETALBURG_WOODS
    h_setvar VAR_PETALBURG_WOODS_STATE, 1
    h_release

Sub_PW_Search:                      // PetalburgWoods_EventScript_15CDE6
    h_applymovement PW_DEVON, Mv_PW_DevonLookAround
    h_waitmovement
    h_msgbox_actor 0, PW_DEVON      // Hmmm... Not a one to be found...
    h_closemessage
    VMReturn

Sub_PW_Thanks:                      // PetalburgWoods_EventScript_15CDFA
    h_msgbox_actor 6, PW_GRUNT      // Grrr... You've got some nerve meddling with Team Aqua! ...
    h_closemessage
    h_applymovement PW_GRUNT, Mv_PW_GruntRunAway
    h_waitmovement
    h_removeobject PW_GRUNT, FLAG_HIDE_EVIL_TEAM_PETALBURG_WOODS
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_msgbox_actor 7, PW_DEVON      // Whew... That was awfully close! ... I'll give you a Great Ball as my thanks!
    h_closemessage
    h_giveitem ITEM_GREAT_BALL
    h_goto_if_ne HLIB_RESULT, 0, L_PW_Given
    h_msgbox_actor 8, PW_DEVON      // You're loaded with items. I can't give you this Great Ball.
L_PW_Given:
    h_msgbox_actor 9, PW_DEVON      // Didn't that Team Aqua thug say they were after something in Rustboro, too?
    h_applymovement PW_DEVON, Mv_PW_DevonCrisis
    h_waitmovement
    h_msgbox_actor 10, PW_DEVON     // Uh-oh! It's a crisis! I can't be wasting time!
    h_closemessage
    VMReturn

PW_MiracleSeed:                     // PetalburgWoods_EventScript_15CEDC (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_MIRACLE_SEED, L_PW_SeedGiven
    h_msgbox 11                     // Oh, neat! That's the Badge from Rustboro Gym! ...
    h_closemessage
    h_giveitem ITEM_MIRACLE_SEED
    h_goto_if_eq HLIB_RESULT, 0, L_PW_SeedDone
    h_setflag FLAG_RECEIVED_MIRACLE_SEED
L_PW_SeedDone:
    h_release
L_PW_SeedGiven:
    h_msgbox 12                     // It's a Miracle Seed. ...
    h_release

    .balign 4, 0
Mv_PW_DevonLookAround:              // PetalburgWoods_Movement_15CE73
    face_up
    delay_16
    face_right
    delay_16
    face_left
    delay_16
    face_down
    delay_16
    face_right
    delay_16
    face_up
    delay_16
    step_end
Mv_PW_DevonApproachLeft:            // 15CE89: delay_16, face_player (the player is south of him), walk_down x2
    delay_16
    face_down
    walk_down 2
    step_end
Mv_PW_DevonApproachRight:           // 15CE8E: delay_16, face_player (east: the player is at (27,23)), walk_down x3,
    delay_16                        //   walk_in_place_fastest_right
    face_right
    walk_down 3
    walk_in_place_fastest_right
    step_end
Mv_PW_DevonLeaveLeft:               // 15CE80
    walk_fast_right
    walk_fast_up 7
    step_end
Mv_PW_DevonLeaveRight:              // 15CE95
    walk_fast_left
    walk_fast_up 7
    step_end
Mv_PW_DevonHideLeft:                // 15CE9E
    walk_fast_right
    walk_fast_down 2
    walk_fast_left
    walk_in_place_fastest_up
    step_end
Mv_PW_DevonHideRight:               // 15CEA4
    walk_fast_down
    walk_fast_right
    walk_in_place_fastest_up
    step_end
Mv_PW_DevonCrisis:                  // 15CEA8
    walk_in_place_fastest_down
    delay_16 5
    face_up
    step_end
Mv_PW_GruntDownLeft:                // 15CEB0
    walk_fast_down 2
    step_end
Mv_PW_GruntBackUp:                  // 15CEB3
    lock_facing_direction
    walk_up
    unlock_facing_direction
    step_end
Mv_PW_GruntRunAway:                 // 15CEB7
    walk_fast_up 5
    delay_16 2
    step_end
Mv_PW_GruntDownRight:               // 15CEBF
    walk_fast_down 3
    step_end
Mv_PW_GruntArrive:                  // 15CEC3
    walk_down 2
    delay_16 2
    step_end
Mv_PW_GruntStep:                    // 15CEC8
    walk_down
    step_end
#if __has_include("scenes/PetalburgWoods_Postgame.inc")
#include "scenes/PetalburgWoods_Postgame.inc"   // post-game Celebi: PG_PW_Init, PG_PW_Celebi
#endif
#include "common/movement.inc"
#endif
