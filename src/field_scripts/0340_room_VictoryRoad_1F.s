// VictoryRoad_1F (zone 170): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch11 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch11

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry V1_WallyTrigger0   // 4: step trigger (34,3) VAR_VICTORY_ROAD_1F_STATE 0: VictoryRoad_1F_EventScript_WallyTrigger0  // story:
    ScriptEntry V1_WallyTrigger1   // 5: step trigger (34,4): ..._WallyTrigger1  // story:
    ScriptEntry V1_WallyTrigger2   // 6: step trigger (34,5): ..._WallyTrigger2  // story:
    ScriptEntry V1_WallyPost       // 7: object 4 (Wally at the entrance fight): ..._WallyRematchPostBattle  // story:
    ScriptEntry V1_Wally           // 8: object 7 (Wally inside, after the Hall of Fame): ..._EventScript_Wally  // story:
    ScriptEntry V1_Init            // 9: zone init (1F's OnTransition: hide the entrance Wally once beaten; test start)  // story:
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
    h_call_if_set FLAG_DEFEATED_WALLY_VICTORY_ROAD, V1_HideWally
    VMHalt
V1_HideWally:                                  // VictoryRoad_1F_EventScript_HideWally
    h_setflag FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    VMReturn

V1_WallyTrigger0:                              // VictoryRoad_1F_EventScript_WallyTrigger0 (player at (34,3))
    h_lock
    h_addobject V1_WALLY_ENTRANCE, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    h_applymovement V1_WALLY_ENTRANCE, Mv_V1_WallyApproachPlayer0
    h_waitmovement
    VMJump V1_WallyApproachPlayer

V1_WallyTrigger1:                              // ..._WallyTrigger1 (34,4)
    h_lock
    h_addobject V1_WALLY_ENTRANCE, FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    h_applymovement V1_WALLY_ENTRANCE, Mv_V1_WallyApproachPlayer1
    h_waitmovement
    VMJump V1_WallyApproachPlayer

V1_WallyTrigger2:                              // ..._WallyTrigger2 (34,5)
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
    h_goto_if_defeated TRAINER_WALLY_3, L_V1_WallyAfter
    h_msgbox T_WallyIntro                      // Wally: Hi! <player>! I've gotten stronger since that last time! ...
    h_closemessage
    h_trainerbattle TRAINER_WALLY_3            // (in battle: "Wow! <player>, you are strong, after all!")
    h_buffer_player
L_V1_WallyAfter:
    h_msgbox T_WallyPostBattle                 // Wally: I couldn't beat you this time, too... ... And challenge the Pokémon League!
    h_release

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

#include "common/movement.inc"
#include "scenes/ch11_test.inc"
