// Route110_SeasideCyclingRoadNorthEntrance (zone 510): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0332_room_Route110_SeasideCyclingRoadNorthEntrance.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch3b
#include "hoenn_story.inc"  // ch3b
#include "scenes/ch3b_lib.inc"  // ch3b

    ScriptEntry Script_1
    ScriptEntry NG_Enter         // 2: trigger (7,4) VAR_TEMP_1 0, Route110_SeasideCyclingRoadNorthEntrance_EventScript_1634F7  // story:
    ScriptEntry NG_Leave         // 3: trigger (5,4) VAR_TEMP_1 1  // story:
    ScriptEntriesEnd

Script_1:                                      // mart_employee (7,2), Sapphire Route110_SeasideCyclingRoadNorthEntrance_EventScript_1634EB
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch3 part 3b, ch3b agent 2026-10-07: Sapphire data/maps/Route110_SeasideCyclingRoadNorthEntrance/scripts.inc;
// generators must keep everything from this line on; entries above marked "// story:"). The two step triggers in front
// of the gatesman are in data/story/ch3b.json (Sapphire's VAR_TEMP_1 = map-local work 0x4001: Black 2 clears works
// 0x4000-0x401F on every zone change, as Gen 3 its VAR_TEMP_*); text line 1 of the room's file (line 0 is the
// gatesman's). GetPlayerAvatarBike = Black 2's PlayerGetExState (1 = riding: its own scripts get the player off the
// bike with it, 0072.s/0124.s). FLAG_SYS_CYCLING_ROAD is kept as Sapphire sets it, with no engine effect in Black 2
// (Sapphire's C keeps you from getting off the bike on Cycling Road). The Mach Bike's Cycling Road challenge
// (VAR_CYCLING_CHALLENGE_STATE) cannot be timed in Black 2 (scenes/Route110.inc), so it is never started here.
#define T_NoBike 1
#define VAR_GATE_TEMP_1 0x4001

NG_Enter:                      // heading onto Cycling Road (lockall)
    h_lock
    PlayerGetExState C3B_A
    h_goto_if_ne C3B_A, 1, L_NG_NoBike
    h_setflag FLAG_SYS_CYCLING_ROAD
    h_setvar VAR_GATE_TEMP_1, 1
    h_release
L_NG_NoBike:                   // "You don't have a bike!"
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info T_NoBike          // Sorry, you can't walk on Cycling Road. It's too dangerous. Please come back with a Bike.
    h_closemessage
    h_applymovement 255, Mv_NG_StepBack
    h_waitmovement
    h_release

NG_Leave:                      // heading back off Cycling Road
    h_lock
    h_clearflag FLAG_SYS_CYCLING_ROAD
    h_setvar VAR_GATE_TEMP_1, 0
    h_release

    .balign 4, 0
Mv_NG_StepBack:
    walk_left
    step_end
