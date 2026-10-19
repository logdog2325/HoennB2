// VictoryRoad_1F (zone 170): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch11 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch11
#include "hoenn_rematch.inc"    // Emerald's rematches (em_gym_rematch: nothing in Sapphire / Ruby)

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry V1_WallyTrigger0   // 4: step trigger (34,3) VAR_VICTORY_ROAD_1F_STATE 0: VictoryRoad_1F_EventScript_WallyTrigger0  // story:
    ScriptEntry V1_WallyTrigger1   // 5: step trigger (34,4): ..._WallyTrigger1  // story:
    ScriptEntry V1_WallyTrigger2   // 6: step trigger (34,5): ..._WallyTrigger2  // story:
    ScriptEntry V1_WallyPost       // 7: object 4 (Wally at the entrance fight): ..._WallyRematchPostBattle  // story:
    ScriptEntry V1_Wally           // 8: object 7 (Wally inside, after the Hall of Fame): ..._EventScript_Wally  // story:
    ScriptEntry V1_Init            // 9: zone init (1F's OnTransition: hide the entrance Wally once beaten; test start)  // story:
#ifdef HOENN_EMERALD
    ScriptEntry V1_EmFieldLoad     // 10: Emerald: every field load and return (0341 MapScript 3/4): the entrance Wally's standing spot  // story:
#endif
    ScriptEntriesEnd

Script_1:                                      // ladder down (21,32) -> VictoryRoad_B1F warp 5 (20,21)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 171, 28, 0, 21, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (42,38) -> VictoryRoad_B1F warp 2 (42,25)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 171, 50, 0, 25, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // ladder down (9,14) -> VictoryRoad_B1F warp 4 (8,3)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 171, 16, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch11, ch11 agent 2026-10-07; Sapphire data/maps/VictoryRoad_1F/scripts.inc; generators must keep
// everything from this line on; entries above marked "// story:")
// Scripts 4-9, text lines 1-4 (line 0 is the generator's). Room tiles = Sapphire tiles + (8,8). People (data/story/ch11.json,
// uid = Sapphire local id): Edgar 1, Hope 2, Albert 3 (eye-contact trainers: Black 2's global script 3000 + id), Wally at
// the entrance 4 (hidden by FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD), Wally inside 7 (FLAG_HIDE_WALLY_DEFEATED_VICTORY_ROAD, shown
// by the Hall of Fame). The item balls (5, 6) and the hidden Ultra Ball are the generators'.
// Black 2 difference: Sapphire's moveobjectoffscreen 4 (Wally vanishes after his line) is ActorDelete + the hide flag.
// EMERALD (emerald fidelity helper 2026-10-18; pokeemerald data/maps/VictoryRoad_1F/scripts.inc + map.json): the entrance
// battle is by the ENTRANCE. Triggers (2,23) / (3,23) (scripts 4 / 5; data/story/ch11.json "at_emerald", the third trigger
// "skip_emerald"); Wally (uid 4, Emerald's object at (12,25), FACE_DOWN, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD = Emerald's
// FLAG_HIDE_VICTORY_ROAD_ENTRANCE_WALLY) walks left 10 / 9 and up to the player, who turns down; after the battle he
// STAYS (no removeobject), VAR_VICTORY_ROAD_1F_STATE = 1 / 2 = which trigger, and he stands at (2,24) / (3,24) facing
// down until the Hall of Fame hides him (0114 HF_EmeraldFlags). pokeemerald's OnTransition setobjectxyperm is here
// V1_EmFieldLoad on every field load and return (ActorSetGPos by uid, as RusturfTunnel: no dependence on the order of
// the zone's people). The post-game Wally (uid 7) stays at the exit (31,9) with Emerald's rematches.
#define T_WallyNotGoingToLose 1
#define T_WallyPostEntrance 2
#define T_WallyIntro 3
#define T_WallyPostBattle 4
#define V1_WALLY_ENTRANCE 4
#define V1_WALLY_INSIDE 7

V1_Init:                                       // VictoryRoad_1F_OnTransition
#ifdef HOENN_TEST_CH11
    VMCall Test_Ch11Start                      // test builds only (scenes/ch11_test.inc)
#endif
#ifdef HOENN_EMERALD
    // Emerald's OnTransition hides no one: Wally stays at the entrance until the Hall of Fame. Before the battle he is
    // hidden (new game sets the flag; h_addobject clears it at the trigger, so a lost battle would leave him shown)
    h_call_if_eq VAR_VICTORY_ROAD_1F_STATE, 0, V1_HideWally
#else
    h_call_if_set FLAG_DEFEATED_WALLY_VICTORY_ROAD, V1_HideWally
#endif
    VMHalt
V1_HideWally:                                  // VictoryRoad_1F_EventScript_HideWally
    h_setflag FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    VMReturn

V1_WallyTrigger0:                              // VictoryRoad_1F_EventScript_WallyTrigger0 (player at (34,3))
#ifdef HOENN_EMERALD
    h_lock                                     // VictoryRoad_1F_EventScript_WallyBattleTrigger1 (player at (2,23))
    h_addobject V1_WALLY_ENTRANCE, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    h_applymovement V1_WALLY_ENTRANCE, Mv_V1_EmWallyApproachPlayer1
    h_waitmovement
    VMCall V1_EmEntranceBattle
    h_setvar VAR_VICTORY_ROAD_1F_STATE, 1      // (copyvar VAR_VICTORY_ROAD_1F_STATE, VAR_0x8008 = 1: he stands at (2,24))
    h_release
#endif
    h_lock
    h_addobject V1_WALLY_ENTRANCE, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    h_applymovement V1_WALLY_ENTRANCE, Mv_V1_WallyApproachPlayer0
    h_waitmovement
    VMJump V1_WallyApproachPlayer

V1_WallyTrigger1:                              // ..._WallyTrigger1 (34,4)
#ifdef HOENN_EMERALD
    h_lock                                     // VictoryRoad_1F_EventScript_WallyBattleTrigger2 (player at (3,23))
    h_addobject V1_WALLY_ENTRANCE, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    h_applymovement V1_WALLY_ENTRANCE, Mv_V1_EmWallyApproachPlayer2
    h_waitmovement
    VMCall V1_EmEntranceBattle
    h_setvar VAR_VICTORY_ROAD_1F_STATE, 2      // (= 2: he stands at (3,24))
    h_release
#endif
    h_lock
    h_addobject V1_WALLY_ENTRANCE, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    h_applymovement V1_WALLY_ENTRANCE, Mv_V1_WallyApproachPlayer1
    h_waitmovement
    VMJump V1_WallyApproachPlayer

V1_WallyTrigger2:                              // ..._WallyTrigger2 (34,5)
#ifdef HOENN_EMERALD
    VMJump V1_WallyTrigger1                    // (Emerald has two triggers: no trigger runs this script)
#endif
    h_lock
    h_addobject V1_WALLY_ENTRANCE, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    h_applymovement V1_WALLY_ENTRANCE, Mv_V1_WallyApproachPlayer2
    h_waitmovement
    VMJump V1_WallyApproachPlayer

V1_WallyApproachPlayer:                        // VictoryRoad_1F_EventScript_WallyApproachPlayer
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_buffer_player
    h_msgbox_actor T_WallyNotGoingToLose, V1_WALLY_ENTRANCE   // Wally: Hi! <player>! I bet you're surprised to see me here! ...
    h_closemessage
    h_trainerbattle TRAINER_WALLY_1                // (in battle: "Wow! <player>, you are strong, after all!")
    h_buffer_player
    h_msgbox_actor T_WallyPostEntrance, V1_WALLY_ENTRANCE     // Wally: I couldn't beat you today, <player>, but one of these days ...
    h_closemessage
    h_removeobject V1_WALLY_ENTRANCE, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD   // (clearflag + moveobjectoffscreen 4)
    h_setflag FLAG_DEFEATED_WALLY_VICTORY_ROAD
    h_setvar VAR_VICTORY_ROAD_1F_STATE, 1
    h_release

#ifdef HOENN_EMERALD
V1_EmEntranceBattle:                           // VictoryRoad_1F_EventScript_WallyEntranceBattle (to the copyvar)
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown    // (Emerald: Common_Movement_WalkInPlaceFasterDown)
    h_waitmovement
    h_buffer_player
    h_msgbox_actor T_WallyNotGoingToLose, V1_WALLY_ENTRANCE   // Wally: Hi! <player>! I bet you're surprised to see me here! ...
    h_closemessage
    h_trainerbattle TRAINER_WALLY_1                // TRAINER_WALLY_VR_1 (same id, Emerald's party; "Wow! <player>, you are strong, after all!")
    h_buffer_player
    h_msgbox_actor T_WallyPostEntrance, V1_WALLY_ENTRANCE     // Wally: I couldn't beat you today, <player>, but one of these days ...
    h_closemessage
    h_setflag FLAG_DEFEATED_WALLY_VICTORY_ROAD     // (his hide flag stays clear: clearflag FLAG_HIDE_VICTORY_ROAD_ENTRANCE_WALLY)
    VMReturn

V1_EmFieldLoad:                                // VictoryRoad_1F_OnTransition: SetEntranceWallyPos1 / 2 (setobjectxyperm + FACE_DOWN)
    h_goto_if_eq VAR_VICTORY_ROAD_1F_STATE, 1, L_V1_EmPos1
    h_goto_if_eq VAR_VICTORY_ROAD_1F_STATE, 2, L_V1_EmPos2
    VMHalt
L_V1_EmPos1:
    ActorSetGPos V1_WALLY_ENTRANCE, 2 + 8, 1, 24 + 8, 1      // (2,24) + the room origin (8,8), facing down (no actor: nothing);
                                                              // y in tiles: the raised floor is 16 units = 1 (0 sank him into it)
    VMHalt
L_V1_EmPos2:
    ActorSetGPos V1_WALLY_ENTRANCE, 3 + 8, 1, 24 + 8, 1      // (3,24)
    VMHalt
#endif

V1_WallyPost:                                  // VictoryRoad_1F_EventScript_WallyRematchPostBattle (MSGBOX_NPC)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_msgbox T_WallyPostEntrance
    h_release

V1_Wally:                                      // VictoryRoad_1F_EventScript_Wally (trainerbattle_single TRAINER_WALLY_3)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
#ifdef HOENN_EMERALD
    h_goto_if_defeated TRAINER_WALLY_3, L_V1_WallyAgain     // (Emerald: ExitWally, TRAINER_WALLY_VR_2 = this id)
#else
    h_goto_if_defeated TRAINER_WALLY_3, L_V1_WallyAfter
#endif
    h_msgbox T_WallyIntro                      // Wally: Hi! <player>! I've gotten stronger since that last time! ...
    h_closemessage
    h_trainerbattle TRAINER_WALLY_3            // (in battle: "Wow! <player>, you are strong, after all!")
    h_buffer_player
L_V1_WallyAfter:
    h_msgbox T_WallyPostBattle                 // Wally: I couldn't beat you this time, too... ... And challenge the Pokémon League!
    h_release
#ifdef HOENN_EMERALD
L_V1_WallyAgain:                               // VictoryRoad_1F_EventScript_RematchWally (ShouldTryRematchBattle): Emerald's
    em_gym_rematch TRAINER_WALLY_3, V1_WALLY_INSIDE   // tiers TRAINER_WALLY_VR_3-5, once a day (hoenn_rematch.inc)
    VMJump L_V1_WallyAfter
#endif

    .balign 4, 0
Mv_V1_WallyApproachPlayer0:                    // VictoryRoad_1F_Movement_WallyApproachPlayer0
    walk_up 9
    walk_right 2
    step_end
Mv_V1_WallyApproachPlayer1:
    walk_up 8
    walk_right 2
    step_end
Mv_V1_WallyApproachPlayer2:
    walk_up 7
    walk_right 2
    step_end
#ifdef HOENN_EMERALD
Mv_V1_EmWallyApproachPlayer1:                  // VictoryRoad_1F_Movement_WallyApproachPlayer1: (12,25) -> (2,24)
    walk_left 10
    walk_up
    step_end
Mv_V1_EmWallyApproachPlayer2:                  // ..._WallyApproachPlayer2: (12,25) -> (3,24)
    walk_left 9
    walk_up
    step_end
#endif

#include "common/movement.inc"
#include "scenes/ch11_test.inc"
