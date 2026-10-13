// Petalburg City's story (Sapphire data/maps/PetalburgCity/scripts.inc; chapter Ch1). converter/gen_map_content.py
// includes this file twice in the generated zone file 0878_auto_PetalburgCity.s: the entries below become scripts
// 1-8, the generated signs/people follow. Text: src/text/scenes/PetalburgCity.txt, lines 0-7. Map scripts:
// scenes/PetalburgCity_init.inc. Story NPCs and triggers: data/story/ch1.json (uid = 100 + Sapphire local id).
// Zone tiles = Sapphire tiles + (88, 290). The gym boy (Sapphire object 9, PetalburgCity_EventScript_GymBoy) is a
// generated NPC: the zone's 4th (index 3 = uid 3 in work/world/world.json zone 439: gentleman, two item balls, him).
#ifdef SCENE_ENTRIES
    ScriptEntry Story_Init          // 1: PetalburgCity_OnTransition (zone init)
    ScriptEntry Story_WallyTutorial // 2: PetalburgCity_EventScript_WallyTutorial (OnFrame: VAR_PETALBURG_STATE 2)
    ScriptEntry Story_ShowGym0      // 3: trigger (8,10) PetalburgCity_EventScript_ShowGymToPlayer0
    ScriptEntry Story_ShowGym1      // 4: trigger (8,11)
    ScriptEntry Story_ShowGym2      // 5: trigger (8,12)
    ScriptEntry Story_ShowGym3      // 6: trigger (8,13)
    ScriptEntry Story_Boy           // 7: boy by the pond (PetalburgCity_EventScript_Boy)
    ScriptEntry Story_WallysMom     // 8: Wally's mom (PetalburgCity_EventScript_WallysMom)
#ifdef HOENN_EMERALD                // Emerald-only entries go last (notes/EMERALD_STORY.md 2.4.1); bodies: scenes/emerald/PetalburgCity.inc
    ScriptEntry Em_PB_Scott         // 9: Scott0-3, one 1x4 trigger at x = 4 (Ch1)
    ScriptEntry Em_PB_WalkToWallysHouse // 10: OnFrame VAR_PETALBURG_STATE 4, Wally's father leads the player home (Ch6)
#endif
#else
#define PB_WALLY 102
#define PB_BOY 103
#define PB_GYMBOY 3                 // generated NPC: uid = its index in the zone's NPC list
#define PB_GYMBOY_INDEX 3

Story_Init:                         // PetalburgCity_OnTransition
    h_setflag FLAG_VISITED_PETALBURG_CITY
    h_goto_if_ne VAR_PETALBURG_STATE, 0, L_PB_InitDone
    ObjInitNPCGPos PB_GYMBOY_INDEX, 1, 93, 0, 301   // MoveGymBoyToWestEntrance: (5,11)
L_PB_InitDone:                      // (state 2: savebgm MUS_FOLLOW_ME; the tutorial plays it itself)
    VMHalt

Story_WallyTutorial:                // the player and Wally arrive from the Gym (VAR_PETALBURG_STATE 2)
    h_lock
    FadeInBlack                     // (the Gym's scripted warp leaves the screen black: Black 2's map change
    FadeWait                        //  fades in only through the arrival scene)
    h_setflag FLAG_HIDE_MAP_NAME_POPUP
    h_zone_hold                     // the walk ends 6 tiles into Route 102 (its zone since zone_edges): Petalburg's zone
                                    // stays (Sapphire keeps Petalburg's objects); the warp to the Gym ends the hold
    h_playbgm MUS_FOLLOW_ME         // (Sapphire keeps the Gym's MUS_FOLLOW_ME across the warp)
    h_applymovement PB_WALLY, Mv_PB_TutorialWally
    h_applymovement 255, Mv_PB_TutorialPlayer
    h_waitmovement
    h_buffer_player
    h_msgbox_actor 5, PB_WALLY      // Wally: <player>... Pokémon hide in tall grass like this ... ...Whoa!
    h_closemessage
    CallCaptureDemo                 // ScrSpecial_StartWallyTutorialBattle: Black 2's catching demo with Wally's
    CallWildBattleEnd               // Zigzagoon and a wild Ralts (b2tools/patches/capture_demo.py), as b2:0874.s
    PokeDexRegist 0, SPECIES_RALTS  // Sapphire's tutorial battle marks Ralts as seen; Black 2's capture demo does not (hoenn_pokedex)
    h_msgbox_actor 6, PB_WALLY      // Wally: I did it... It's my... My Pokémon!
    h_applymovement PB_WALLY, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_buffer_player
    h_msgbox_actor 7, PB_WALLY      // <player>, thank you! Let's go back to the Gym!
    h_closemessage
    h_clearflag FLAG_HIDE_MAP_NAME_POPUP
    h_setvar VAR_PETALBURG_STATE, 3
    h_fadedefaultbgm
    h_clearflag FLAG_DONT_TRANSITION_MUSIC
    h_setvar VAR_PETALBURG_GYM_STATE, 1
    h_warpsilent 452, 5, 108, 0     // warp MAP_PETALBURG_CITY_GYM (4,108) (room tile + (1,0)), facing north
    h_release                       //   (the Gym's OnWarp turns the player north)

Story_ShowGym0:                     // PetalburgCity_EventScript_ShowGymToPlayer0..3: the gym boy stops you
    h_lock
    h_setvar 0x8008, 0
    VMJump L_PB_ShowGym
Story_ShowGym1:
    h_lock
    h_setvar 0x8008, 1
    VMJump L_PB_ShowGym
Story_ShowGym2:
    h_lock
    h_setvar 0x8008, 2
    VMJump L_PB_ShowGym
Story_ShowGym3:
    h_lock
    h_setvar 0x8008, 3
L_PB_ShowGym:                       // PetalburgCity_EventScript_ShowGymToPlayer
    h_turnobject PB_GYMBOY, 3       // Common_Movement_FacePlayer: the player is east of him (x 8 vs 5)
    h_playbgm MUS_FOLLOW_ME
    h_applymovement PB_GYMBOY, Common_Movement_ExclamationMark   // (playse SE_PIN: the balloon has its sound)
    h_waitmovement
    h_applymovement PB_GYMBOY, Common_Movement_Delay48
    h_waitmovement
    h_goto_if_eq 0x8008, 1, L_PB_Approach1
    h_goto_if_eq 0x8008, 2, L_PB_Approach2
    h_goto_if_eq 0x8008, 3, L_PB_Approach3
    h_applymovement PB_GYMBOY, Mv_PB_BoyApproach0
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    VMJump L_PB_Approached
L_PB_Approach1:
    h_applymovement PB_GYMBOY, Mv_PB_BoyApproach1
    VMJump L_PB_Approached
L_PB_Approach2:
    h_applymovement PB_GYMBOY, Mv_PB_BoyApproach2
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    VMJump L_PB_Approached
L_PB_Approach3:
    h_applymovement PB_GYMBOY, Mv_PB_BoyApproach3
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
L_PB_Approached:
    h_waitmovement
    h_msgbox_actor 0, PB_GYMBOY     // Hiya! Are you maybe... A rookie Trainer? ...
    h_closemessage
    h_goto_if_eq 0x8008, 1, L_PB_Lead1
    h_goto_if_eq 0x8008, 2, L_PB_Lead2
    h_goto_if_eq 0x8008, 3, L_PB_Lead3
    h_applymovement PB_GYMBOY, Mv_PB_BoyToGym0
    h_applymovement 255, Mv_PB_PlayerToGym0
    VMJump L_PB_AtGym
L_PB_Lead1:
    h_applymovement PB_GYMBOY, Mv_PB_BoyToGym1
    h_applymovement 255, Mv_PB_PlayerToGym1
    VMJump L_PB_AtGym
L_PB_Lead2:
    h_applymovement PB_GYMBOY, Mv_PB_BoyToGym2
    h_applymovement 255, Mv_PB_PlayerToGym2
    VMJump L_PB_AtGym
L_PB_Lead3:
    h_applymovement PB_GYMBOY, Mv_PB_BoyToGym3
    h_applymovement 255, Mv_PB_PlayerToGym3
L_PB_AtGym:
    h_waitmovement
    h_msgbox_actor 1, PB_GYMBOY     // See? This is Petalburg City's Gym.
    h_applymovement PB_GYMBOY, Common_Movement_WalkInPlaceFastestRight
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_msgbox_actor 2, PB_GYMBOY     // This is the Gym's sign. ...
    h_closemessage
    h_applymovement PB_GYMBOY, Mv_PB_BoyWalkAway
    h_waitmovement
    h_fadedefaultbgm
    h_release

Story_Boy:                          // PetalburgCity_EventScript_Boy
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 3                      // My face is reflected in the water. ...
    h_closemessage
    h_turnobject PB_BOY, 1          // Common_Movement_FaceOriginalDirection (FACE_DOWN)
    h_release

Story_WallysMom:                    // PetalburgCity_EventScript_WallysMom (MSGBOX_NPC)
    h_msgbox_npc 4                  // Where has our Wally gone? ...

    .balign 4, 0
Mv_PB_TutorialPlayer:               // PetalburgCity_Movement_WallyTutorialPlayer: from (15,9), where Sapphire's door
    delay_8                         // exit leaves the player (the Gym's warp lands there), along row 17 to (35,15)
    walk_down 8
    walk_right 20
    walk_up 2
    walk_in_place_fastest_right
    step_end
Mv_PB_TutorialWally:                // PetalburgCity_Movement_WallyTutorialWally: (15,10) to (36,15), right of the player
    delay_8
    walk_down 7
    walk_right 20
    walk_up 2
    walk_right
    delay_16
    walk_in_place_fastest_up
    delay_16 2
    walk_in_place_fastest_right
    step_end
Mv_PB_BoyApproach0:
    walk_right 3
    walk_in_place_fastest_up
    step_end
Mv_PB_BoyApproach1:
    walk_right 2
    step_end
Mv_PB_BoyApproach2:
    walk_right 3
    walk_in_place_fastest_down
    step_end
Mv_PB_BoyApproach3:
    walk_down
    walk_right 3
    walk_in_place_fastest_down
    step_end
Mv_PB_BoyToGym0:
    walk_right 7
    walk_up
    walk_right
    walk_in_place_fastest_up
    step_end
Mv_PB_BoyToGym1:
    walk_down
    walk_right 8
    walk_up 2
    walk_right
    walk_in_place_fastest_up
    step_end
Mv_PB_BoyToGym2:
    walk_right 7
    walk_up
    walk_right
    walk_in_place_fastest_up
    step_end
Mv_PB_BoyToGym3:
    walk_right 7
    walk_up 2
    walk_right
    walk_in_place_fastest_up
    step_end
Mv_PB_BoyWalkAway:
    walk_down
    walk_left 11
    step_end
Mv_PB_PlayerToGym0:
    walk_down
    walk_right 7
    walk_up
    step_end
Mv_PB_PlayerToGym1:
    delay_16 2
    walk_down
    walk_right 7
    walk_up 2
    step_end
Mv_PB_PlayerToGym2:
    walk_up
    walk_right 7
    walk_up
    step_end
Mv_PB_PlayerToGym3:
    walk_up
    walk_right 7
    walk_up 2
    step_end
#ifdef HOENN_EMERALD
#include "scenes/emerald/PetalburgCity.inc"
#endif
#include "common/movement.inc"
#endif
