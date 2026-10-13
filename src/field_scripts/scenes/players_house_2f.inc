// The player's / rival's room, 2F (Sapphire LittlerootTown_BrendansHouse_2F / MaysHouse_2F, data/scripts/
// players_house.inc). Included by zone 391 (Brendan's room: #define HOUSE_BRENDAN 1) and 393 (May's: 0), with T_BASE.
// Zone tiles = Sapphire tiles + (1, 1). Actors: the rival 1, Mom 14 (Sapphire ids).
// Scripts: 20 wall clock (sets it; Mom comes up), 21 the rival, 22 arrival from the 1F push (reserved: fade in),
// 24 zone init.

#include "hoenn.h"
#include "hoenn_music.inc"                       // (the rival's encounter song)
#define T(n) (T_BASE + (n))
#if HOUSE_BRENDAN
#define RIVAL_SONG MUS_HOENN_ENCOUNTER_BRENDAN   // Sapphire RivalsHouse_2F: playbgm MUS_ENCOUNTER_BRENDAN, TRUE
#define RIVAL_X 2               // rival (Brendan) at his notebook, Sapphire (1,2)
#define RIVAL_HIDE_FLAG FLAG_HIDE_BRENDAN_UPSTAIRS
#define AROUND_DIR 2            // the player faces left (stands right of the rival): the rival walks around
#else
#define RIVAL_SONG MUS_HOENN_ENCOUNTER_MAY       // playbgm MUS_ENCOUNTER_MAY, TRUE
#define RIVAL_X 8               // May at her notebook, Sapphire (7,2)
#define RIVAL_HIDE_FLAG FLAG_HIDE_MAY_UPSTAIRS
#define AROUND_DIR 3
#endif

Script_20:                                       // ..._2F_EventScript_1B69EB: the wall clock
    ActorsPauseAll
    VMStackPushFlag FLAG_SET_WALL_CLOCK
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_ClockDone              // already set (Sapphire shows the clock; Black 2 has no clock screen)
    SEPlay SEQ_SE_MESSAGE
    InfoMsg T(0), 2                              // "The clock is stopped... Better set it and start it!"
    LastKeyWait
    InfoMsgClose_0039
    FadeOutBlack                                 // (Sapphire's clock-setting screen: Black 2 keeps the DS's real time)
    FadeWait
    SEPlay SEQ_SE_DECIDE1
    VMSleep 30
    FadeInBlack
    FadeWait
    VMSleep 15
    WorkSetConst VAR_LITTLEROOT_INTRO_STATE, 6
    FlagSet FLAG_SET_WALL_CLOCK
    FlagSet FLAG_HIDE_MACHOKE_MOVER_1
    FlagSet FLAG_HIDE_MACHOKE_MOVER_2
    FlagReset FLAG_HIDE_MOM_UPSTAIRS
    ActorAdd 14
    ActorCmdExec 14, Mv_MomUpstairsApproach
    ActorCmdWait
    ActorCmdExec 255, Mv_FaceMom
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(1), 14, 0, 0       // "Mom: <player>, how do you like your new room? ..."
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 14, Mv_MomUpstairsLeave
    ActorCmdWait
    SEPlay SEQ_SE_KAIDAN
    ActorDelete 14
    FlagSet FLAG_HIDE_MOM_UPSTAIRS
L_ClockDone:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

#ifndef HOENN_EMERALD                           // Emerald: scenes/emerald/players_house_2f.inc (the Poké Ball, the rival's talk)
Script_21:                                       // ..._2F_EventScript_152A9D: meeting the rival
    ActorsPauseAll
#if __has_include("scenes/players_house_2f_ch8.inc")
#include "scenes/players_house_2f_ch8.inc"           // chapter Ch8 (8a): the rival at home after the Lilycove battle
#endif
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(2), 1, 0, 0        // "Pokémon fully restored! Items ready, and... Huh?"
    LastKeyWait
    MsgWinCloseAll
    BGMPlay RIVAL_SONG                           // (music_fix, Discord: was missing; Unova music: Black 2's E_HUE)
    ActorSetEyeToEye
    ActorCmdExec 1, Mv_Exclaim
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, T(3), 1, 0, 0        // "Huh? Who... Who are you? ..." / "Hey! You... Who are you? ..."
    LastKeyWait
    MsgWinCloseAll
    PlayerGetDir 0x8000
    VMStackPush 0x8000
    VMStackPushConst AROUND_DIR
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_RivalStraight
    ActorCmdExec 1, Mv_RivalAroundToStairs
    VMJump L_RivalWalking
L_RivalStraight:
    ActorCmdExec 1, Mv_RivalToStairs
L_RivalWalking:
    ActorCmdWait
    SEPlay SEQ_SE_KAIDAN
    ActorDelete 1
    FlagSet RIVAL_HIDE_FLAG
    WorkSetConst VAR_LITTLEROOT_RIVAL_STATE, 3
    WorkSetConst VAR_LITTLEROOT_STATE, 1
    BGMChangeMap                                 // savebgm 0 + fadedefaultbgm
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif

Script_22:                                       // reserved after Mom sends the player upstairs (1F script 21)
    FadeInBlack
    FadeWait
    VMHalt

Script_24:                                       // zone init (Sapphire OnTransition)
    VMStackPush VAR_LITTLEROOT_INTRO_STATE
    VMStackPushConst 4
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Init2FNot4
    WorkSetConst VAR_LITTLEROOT_INTRO_STATE, 5
L_Init2FNot4:
    ObjInitNPCGPos 0, 0, RIVAL_X, 0, 3           // RivalCheckingNotebook (index 0 = the rival; until the Route 103 battle)
#ifdef HOENN_EMERALD
    VMCall Sub_Em_2FInit                         // Emerald: ready to meet the rival, the rival at the PC (scenes/emerald/players_house_2f.inc)
#endif
    VMHalt

    .balign 4, 0                                 // movement lists are read as words (Black 2 aligns them too)
Mv_Exclaim:
    Move 75, 1
    Move 63, 3
    MoveEnd

#if HOUSE_BRENDAN
Mv_MomUpstairsApproach:                          // delay_8, walk_down, face left, delay_16, delay_8, walk_left (1B6AA2)
    Move 62, 1
    Move 13, 1
    Move 2, 1
    Move 63, 1
    Move 62, 1
    Move 14, 1
    MoveEnd
Mv_FaceMom:
    Move 3, 1
    MoveEnd
Mv_MomUpstairsLeave:                             // walk_right, walk_up, delay_8 (1B6AA9)
    Move 15, 1
    Move 12, 1
    Move 62, 1
    MoveEnd
Mv_RivalToStairs:                                // Brendan: right x6, up, delay_8 (152C30)
    Move 15, 6
    Move 12, 1
    Move 62, 1
    MoveEnd
Mv_RivalAroundToStairs:                          // down, right x6, up x2, delay_8 (152C25)
    Move 13, 1
    Move 15, 6
    Move 12, 2
    Move 62, 1
    MoveEnd
#else
Mv_MomUpstairsApproach:                          // delay_8, walk_down, face right, delay_16, delay_8, walk_right (1B6AAD)
    Move 62, 1
    Move 13, 1
    Move 3, 1
    Move 63, 1
    Move 62, 1
    Move 15, 1
    MoveEnd
Mv_FaceMom:
    Move 2, 1
    MoveEnd
Mv_MomUpstairsLeave:                             // walk_left, walk_up, delay_8 (1B6AB4)
    Move 14, 1
    Move 12, 1
    Move 62, 1
    MoveEnd
Mv_RivalToStairs:                                // May: left x6, up, delay_8 (152C1C)
    Move 14, 6
    Move 12, 1
    Move 62, 1
    MoveEnd
Mv_RivalAroundToStairs:                          // down, left x6, up x2, delay_8 (152C11)
    Move 13, 1
    Move 14, 6
    Move 12, 2
    Move 62, 1
    MoveEnd
#endif
    .balign 4, 0
#ifdef HOENN_EMERALD
#include "scenes/emerald/players_house_2f.inc"         // Emerald (emerald_ch0_3): the rival's Poké Ball meeting, the rival at home
#endif
