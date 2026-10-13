// Rustboro City's story (Sapphire data/maps/RustboroCity/scripts.inc; chapter Ch2, notes/STORY_PORTING.md).
// converter/gen_map_content.py includes this file twice in the generated zone file 0226_auto_RustboroCity.s: the
// entries below become scripts 1-24, the generated signs/people follow. Text: src/text/scenes/RustboroCity.txt.
// Story objects (uid 150 + Sapphire local id, kept from when zone 113 also held Route 104's north end):
// data/story/ch2.json. Map scripts: scenes/RustboroCity_init.inc.
#ifdef SCENE_ENTRIES
    ScriptEntry RB_Init             // 1: RustboroCity_OnTransition (zone init)
    ScriptEntry RB_FatMan           // 2: RustboroCity_EventScript_FatMan
    ScriptEntry RB_Man1             // 3: RustboroCity_EventScript_Man1
    ScriptEntry RB_Boy2             // 4: RustboroCity_EventScript_Boy2
    ScriptEntry RB_LittleBoy        // 5: RustboroCity_EventScript_LittleBoy
    ScriptEntry RB_LittleGirl       // 6: RustboroCity_EventScript_LittleGirl
    ScriptEntry RB_StolenGoods0     // 7: StolenGoodsTrigger0 (23,20), VAR_RUSTBORO_STATE 1
    ScriptEntry RB_StolenGoods1     // 8: StolenGoodsTrigger1 (23,21)
    ScriptEntry RB_StolenGoods2     // 9: StolenGoodsTrigger2 (23,22)
    ScriptEntry RB_StolenGoods3     // 10: StolenGoodsTrigger3 (23,23)
    ScriptEntry RB_StolenGoods4     // 11: StolenGoodsTrigger4 (23,24)
    ScriptEntry RB_HelpGoods0       // 12: HelpGetGoodsTrigger0 (30,9), VAR_RUSTBORO_STATE 2
    ScriptEntry RB_HelpGoods1       // 13: HelpGetGoodsTrigger1 (29,10)
    ScriptEntry RB_HelpGoods2       // 14: HelpGetGoodsTrigger2 (30,11)
    ScriptEntry RB_HelpGoods3       // 15: HelpGetGoodsTrigger3 (30,12)
    ScriptEntry RB_ReturnGoods0     // 16: ReturnGoodsTrigger0 (30,9), VAR_RUSTBORO_STATE 4
    ScriptEntry RB_ReturnGoods1     // 17: ReturnGoodsTrigger1 (31,10)
    ScriptEntry RB_ReturnGoods2     // 18: ReturnGoodsTrigger2 (30,11)
    ScriptEntry RB_ReturnGoods3     // 19: ReturnGoodsTrigger3 (30,12)
    ScriptEntry RB_DevonEmployee1   // 20: RustboroCity_EventScript_DevonEmployee1
    ScriptEntry RB_Rival            // 21: RustboroCity_EventScript_RivalEncounter
    ScriptEntry RB_GymSign          // 22: RustboroCity_EventScript_GymSign (sign; its text label also holds the
                                    //     unreachable Devon branch office sign, so the generator left it out)
    ScriptEntry RB_None             // 23: the grunt (Sapphire script 0x0: nothing when talked to)
    ScriptEntry RB_TestStart        // 24: HOENN_TEST_CH2 only (OnFrame scene while VAR_RUSTBORO_STATE is 0)
#ifdef HOENN_EMERALD                // Emerald-only entries go last (notes/EMERALD_STORY.md 2.4.1); bodies: scenes/emerald/RustboroCity.inc
    ScriptEntry Em_RB_RivalTrigger  // 25: RivalTrigger0-7, one 1x8 trigger (12-19, 53) while VAR_RUSTBORO_STATE is 7 (Ch2)
#endif
#else
#include "hoenn_key_items.h"
#define RB_EMPLOYEE 159             // Sapphire object 9 (FLAG_HIDE_DEVON_RUSTBORO), (30,10)
#define RB_GRUNT 160                // object 10, Team Aqua grunt (FLAG_HIDE_GRUNT_RUSTBORO), (13,21)
#define RB_RIVAL 164                // object 14 (FLAG_HIDE_RIVAL_RUSTBORO), RIVAL_GFX
#define RB_LITTLEBOY 157
#define RB_LITTLEGIRL 158
#define RB_X 48                     // zone tile = Sapphire tile + (48, 180) (world.py offset of RustboroCity)
#define RB_Z 180

RB_Init:                            // RustboroCity_OnTransition
    h_setflag FLAG_VISITED_RUSTBORO_CITY
    h_setup_rival_gfx               // Common_EventScript_SetupRivalGfxId (SetupEvilTeamGfxIds: Aqua models placed)
    VMHalt

RB_None:
    VMHalt

RB_FatMan:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_DEVON_GOODS_STOLEN, L_RB_FatManSawGrunt
    h_msgbox 0                      // The Devon Corporation... We all just shorten it to Devon.
    h_release
L_RB_FatManSawGrunt:
    h_msgbox 1                      // Hm? A sneaky-looking man?
    h_release

RB_Man1:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_badge 1, L_RB_Man1HaveBadge
    h_msgbox 2                      // Have you taken the Pokémon Gym challenge?
    h_release
L_RB_Man1HaveBadge:
    h_msgbox 3                      // Hey, that's Rustboro's Gym Badge!
    h_release

RB_Boy2:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_POKENAV, L_RB_Boy2BrineyLeftTunnel
    h_msgbox 4                      // ...He goes for walks in the tunnel every so often.
    h_release
L_RB_Boy2BrineyLeftTunnel:
    h_msgbox 5                      // ...he must really love that Peeko.
    h_release

RB_LittleBoy:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 6                      // If a Pokémon gains experience in battles...
    h_turnobject RB_LITTLEBOY, 3    // Common_Movement_FaceOriginalDirection (MOVEMENT_TYPE_FACE_RIGHT)
    h_release

RB_LittleGirl:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 7                      // A Pokémon changes shape?
    h_turnobject RB_LITTLEGIRL, 2   // (MOVEMENT_TYPE_FACE_LEFT)
    h_release

RB_GymSign:
    h_msgbox_sign 19

// ---- the Devon Goods are stolen (VAR_RUSTBORO_STATE 1, set by Roxanne) ----------------------------------------
// Sapphire puts the employee at (14,21) first (setobjectxyperm 9, 14, 21) and back at (30,10) after the chase; Black 2
// moves the live actor (ActorSetGPos) and the entity keeps (30,10). The trigger number (VAR_0x8004) is never read.
RB_StolenGoods0:
RB_StolenGoods1:
RB_StolenGoods2:
RB_StolenGoods3:
RB_StolenGoods4:
    h_lock
    h_msgbox_info 8                 // Get out! Out of the way!
    h_closemessage
    h_addobject RB_GRUNT, FLAG_HIDE_GRUNT_RUSTBORO
    h_addobject RB_EMPLOYEE, FLAG_HIDE_DEVON_RUSTBORO
    ActorSetGPos RB_EMPLOYEE, RB_X + 14, 0, RB_Z + 21, 3
    h_applymovement RB_GRUNT, Mv_RB_GruntEscape
    h_waitmovement
    h_removeobject RB_GRUNT, FLAG_HIDE_GRUNT_RUSTBORO
    h_applymovement RB_EMPLOYEE, Mv_RB_EmployeeChaseGrunt1
    h_waitmovement
    h_msgbox_actor 9, RB_EMPLOYEE   // Wait! Pleeeaaase! Don't take my Goods!
    h_closemessage
    h_applymovement RB_EMPLOYEE, Mv_RB_EmployeeChaseGrunt2
    h_waitmovement
    h_removeobject RB_EMPLOYEE, FLAG_HIDE_DEVON_RUSTBORO
    h_clearflag FLAG_HIDE_DEVON_RUSTBORO
    ActorAdd RB_EMPLOYEE            // back at (30,10) (Gen 3 spawns him there when that spot comes into view)
    h_setflag FLAG_DEVON_GOODS_STOLEN
    h_setvar VAR_RUSTBORO_STATE, 2
    h_setvar VAR_RUSTURF_TUNNEL_STATE, 2
    h_setvar VAR_ROUTE116_STATE, 1
    h_clearflag FLAG_HIDE_BRINEY_ROUTE116
    h_clearflag FLAG_HIDE_PEEKO_RUSTURF_TUNNEL
    h_clearflag FLAG_HIDE_GRUNT_RUSTURF_TUNNEL
    h_setflag FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE
    h_setflag FLAG_HIDE_PEEKO_BRINEY_HOUSE
    h_release

// ---- the employee asks for help (VAR_RUSTBORO_STATE 2) ---------------------------------------------------------
RB_HelpGoods0:                      // player above him
    h_lock
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    VMJump L_RB_AskToGetGoods
RB_HelpGoods1:                      // left of him
    h_lock
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    VMJump L_RB_AskToGetGoods
RB_HelpGoods2:                      // below him
    h_lock
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    VMJump L_RB_AskToGetGoods
RB_HelpGoods3:                      // two below him: he steps down
    h_lock
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    h_applymovement RB_EMPLOYEE, Mv_RB_EmployeeApproachPlayerDown
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
L_RB_AskToGetGoods:                 // RustboroCity_EventScript_EmployeeAskToGetGoods
    h_setflag FLAG_UNKNOWN_9F
    h_setvar VAR_RUSTBORO_STATE, 3
    h_msgbox_actor 10, RB_EMPLOYEE  // Oh, it's you! ... Help me! I was robbed by Team Aqua!
    h_release

Sub_RB_EmployeeNotice:              // playse SE_PIN + ExclamationMark (its own sound in Black 2) + Delay48
    h_applymovement RB_EMPLOYEE, Common_Movement_ExclamationMark
    h_waitmovement
    h_applymovement RB_EMPLOYEE, Common_Movement_Delay48
    h_waitmovement
    VMReturn

RB_DevonEmployee1:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECOVERED_DEVON_GOODS, L_RB_ReturnGoodsSpokeToEmployee
    h_msgbox 11                     // That shady character, I think he took off towards the tunnel over there.
    h_release
L_RB_ReturnGoodsSpokeToEmployee:    // VAR_TEMP_1 = 4: he turns left
    h_waitse
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    VMJump L_RB_ReturnGoods

// ---- the Devon Goods come back (VAR_RUSTBORO_STATE 4, set in Rusturf Tunnel) -----------------------------------
RB_ReturnGoods0:                    // above him
    h_lock
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    VMJump L_RB_ReturnGoods
RB_ReturnGoods1:                    // right of him
    h_lock
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    VMJump L_RB_ReturnGoods
RB_ReturnGoods2:                    // below him
    h_lock
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    VMJump L_RB_ReturnGoods
RB_ReturnGoods3:                    // two below him
    h_lock
    h_applymovement RB_EMPLOYEE, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    VMCall Sub_RB_EmployeeNotice
    h_applymovement RB_EMPLOYEE, Mv_RB_EmployeeApproachPlayerDown
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
L_RB_ReturnGoods:                   // RustboroCity_EventScript_ReturnGoods
    h_msgbox_actor 12, RB_EMPLOYEE  // Oh! How did it go? ... I'll give you another Great Ball!
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_GREAT_BALL
    h_goto_if_ne HLIB_RESULT, 0, L_RB_GaveBall
    h_msgbox_actor 13, RB_EMPLOYEE  // Your Bag's full. I can't give you this Great Ball.
L_RB_GaveBall:
    h_msgbox_actor 14, RB_EMPLOYEE  // Excuse me, please! Please come with me!
    h_closemessage
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_HIDE_DEVON_RUSTBORO
    h_setvar VAR_RUSTBORO_STATE, 5
    h_delay 30
    // warp MAP_RUSTBORO_CITY_DEVON_CORP_3F, 255, 2, 2: zone 577 (room origin (1,0)), facing right (its OnWarp); the
    // 3F arrival script (1154 Script_3) fades in and meets the President
    h_warp_scene 577, 3, 2, 3, 3
    h_release

// ---- the rival (FLAG_HIDE_RIVAL_RUSTBORO cleared by Mr. Stone) ---------------------------------------------------
#ifndef HOENN_EMERALD               // Emerald: the rival battle, scenes/emerald/RustboroCity.inc
RB_Rival:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_set FLAG_MET_RIVAL_RUSTBORO, L_RB_BrineyHint
    h_setflag FLAG_MET_RIVAL_RUSTBORO
    h_msgbox_gendered 15, 16, RB_RIVAL  // May / Brendan: how's your Pokédex coming along?
    h_release
L_RB_BrineyHint:
    h_msgbox_gendered 17, 18, RB_RIVAL  // May / Brendan: by the way, I passed Mr. Briney in Petalburg Woods.
    h_release
#endif

// ---- HOENN_TEST_CH2 (test builds only): the chapter's start state (scenes/ch2_test.inc), from this map's OnFrame
// table (RustboroCity_init.inc) while VAR_RUSTBORO_STATE is 0
RB_TestStart:
#ifdef HOENN_TEST_CH2
    h_lock
    VMCall Sub_Ch2TestStart
    h_release
#include "scenes/ch2_test.inc"
#endif
    VMHalt

    .balign 4, 0
Mv_RB_GruntEscape:                  // RustboroCity_Movement_GruntEscape: (13,21) to (20,12), up the street the
    walk_fastest_right 2            // employee chases him on (x 20); 7 here had him run up x 22 through (22,16)
    walk_fast_right 5
    walk_fast_up 9
    step_end
Mv_RB_EmployeeChaseGrunt1:
    walk_right 6
    walk_in_place_fastest_up
    step_end
Mv_RB_EmployeeChaseGrunt2:
    walk_up 7
    step_end
Mv_RB_EmployeeApproachPlayerDown:
    walk_down
    step_end
#ifdef HOENN_EMERALD
#include "scenes/emerald/RustboroCity.inc"
#endif
#include "common/movement.inc"
#endif
