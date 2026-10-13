// The player's / rival's house, 1F (Sapphire LittlerootTown_BrendansHouse_1F / MaysHouse_1F and data/scripts/
// players_house.inc). Included by zone 390 (Brendan's house: #define HOUSE_BRENDAN 1) and 392 (May's: HOUSE_BRENDAN 0)
// with T_BASE = the first of this file's message lines in the zone's text file (T(n) below, list in notes/OPENING.md).
// The two houses are mirror images: a boy lives in Brendan's, a girl in May's; the other house is the rival's.
// Zone tiles = Sapphire tiles + (1, 0) (notes/INTERIORS.md). Actors: Mom 1, Machokes 2/3, rival's mom 4 (Sapphire ids).
// Scripts: 20 moving in (reserved by Littleroot's arrival), 21 go set the clock (state 5), 22 TV report (state 6),
// 23 rival's mom meets you, 24 zone init, 25 "aren't you interested in your room" (mat trigger), 26 Mom,
// 27/28 Machokes, 29 rival's mom (its branches after the rival left: chapter Ch1, T(16)/T(17)); 19 the Running Shoes
// manual on the table (chapter Ch1, T(18)); in 26: Ch6's Amulet Coin (scenes/players_house_1f_ch6.inc, T(19)-T(21))
// and Mom's rest + heal (chapter Ch1, T(22)/T(23)); chapter Ch13: script 30 (Dad brings the S.S. Ticket, state 3) and
// Mom's post-game line (state 4) in scenes/players_house_1f_ch13.inc, T(24)-T(27).

#include "hoenn.h"
#include "hoenn_trainers.h"                     // (TRAINER_GABBY_AND_TY_1: the TV report's song)
#define T(n) (T_BASE + (n))
#ifdef HOENN_EMERALD
#define MOVER_SPECIES SPECIES_VIGOROTH          // Emerald's movers are Vigoroth (the sheet stays Black 2's worker)
#else
#define MOVER_SPECIES SPECIES_MACHOKE
#endif
#if HOUSE_BRENDAN
#define MOM_DOOR_X 10           // Sapphire (9,8), beside the entrance mat
#define MOM_STAIRS_X 9          // Sapphire (8,4), below the stairs
#define MOM_TV_X 5              // Sapphire (4,5)
#define HOUSES_VAR VAR_LITTLEROOT_HOUSES_STATE
#define ZONE_2F 391
#define MOVER2_TEXT T(14)    // actor 2 carries a box here ("Gwagwah gwah..."), actor 3 faces away
#define MOVER3_TEXT T(13)
#define STAIRS_2F_X 8           // 2F stairs Sapphire (7,1); you arrive one tile below
#else
#define MOM_DOOR_X 2            // Sapphire (1,8)
#define MOM_STAIRS_X 3          // Sapphire (2,4)
#define MOM_TV_X 7              // Sapphire (6,5)
#define HOUSES_VAR VAR_LITTLEROOT_HOUSES_STATE_2
#define ZONE_2F 393
#define MOVER2_TEXT T(13)    // in May's house actor 2 faces away ("Gyao..."), actor 3 carries the box
#define MOVER3_TEXT T(14)
#define STAIRS_2F_X 2           // Sapphire (1,1)
#endif

Script_20:                                       // PlayersHouse_1F_EventScript_EnterHouseMovingIn (reserved: black)
    ActorsPauseAll
    FadeInBlack
    FadeWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(0), 1, 0, 0        // "Mom: See, <player>? Isn't it nice in here, too?"
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 1, Mv_MomFaceEntrance
    ActorCmdWait
    ActorCmdExec 255, Mv_FaceMomAtDoor
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, T(1), 1, 0, 0        // "The mover's Pokémon do all the work ... Don't forget to set it!"
    LastKeyWait
    MsgWinCloseAll
    WorkSetConst VAR_LITTLEROOT_INTRO_STATE, 4
    ActorCmdExec 255, Mv_WalkUp
    ActorCmdExec 1, Mv_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_21:                                       // ..._1F_EventScript_GoUpstairsToSetClock (state 5)
    ActorsPauseAll
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(3), 1, 0, 0        // "Mom: <player>. Go set the clock in your room, honey."
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Mv_WalkUp
    ActorCmdExec 1, Mv_WalkUp
    ActorCmdWait
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 22
    FadeWait
    MapChangeCore ZONE_2F, STAIRS_2F_X, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_22:                                       // PlayersHouse_1F_EventScript_PetalburgGymReport (state 6)
    ActorsPauseAll
    ActorCmdExec 1, Mv_FaceTowardStairsSide
    ActorCmdWait
    ActorCmdExec 1, Mv_Exclaim
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(4), 1, 0, 0        // "Mom: Oh! <player>, <player>! Quick! Come quickly!"
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Mv_PlayerToTV
    ActorCmdWait
    TrainerBGMPlay TRAINER_GABBY_AND_TY_1        // playbgm MUS_ENCOUNTER_INTERVIEWER (music_fix, Discord): the encounter
                                                 // song of Gabby & Ty's class (Interviewer). Hoenn music: Sapphire's
                                                 // interviewer theme; Unova: the class's Black 2 song (as on the routes)
    ActorMsg MSGFILE_SCRIPT, T(5), 1, 0, 0        // "Mom: Look! It's Petalburg Gym! Maybe Dad will be on!"
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 1, Mv_MomMakeRoom
    ActorCmdWait
    ActorCmdExec 255, Mv_PlayerStepToTV
    ActorCmdWait
    ActorCmdExec 255, Mv_FaceUp
    ActorCmdWait
    InfoMsg T(6), 2                              // "Interviewer: ...We brought you this report from in front of Petalburg Gym."
    LastKeyWait
    InfoMsgClose_0039
    BGMChangeMap                                 // fadedefaultbgm: the report is over (music_fix)
    VMSleep 18
    ActorCmdExec 255, Mv_FaceMomAtTV
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, T(7), 1, 0, 0        // "Mom: Oh... It's over. ..."
    LastKeyWait
    MsgWinCloseAll
    ActorMsg MSGFILE_SCRIPT, T(8), 1, 0, 0        // "Oh, yes. One of Dad's friends lives in town. ..."
    LastKeyWait
    MsgWinCloseAll
    WorkSetConst 0x4001, 1                       // Sapphire VAR_TEMP_1 ("See you, honey!"; map-local work)
    ActorCmdExec 1, Mv_MomBackFromTV
    ActorCmdWait
    WorkSetConst VAR_LITTLEROOT_INTRO_STATE, 7
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_23:                                       // ..._1F_EventScript_YoureNewNeighbor (the rival's house)
    ActorsPauseAll
    ActorCmdExec 4, Mv_Exclaim
    ActorCmdWait
    ActorCmdExec 255, Mv_FaceRivalMom
    ActorCmdExec 4, Mv_RivalMomApproach
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(11), 4, 0, 0       // "Oh, hello. And you are? ... Our <son/daughter> is upstairs, I think."
    LastKeyWait
    MsgWinCloseAll
    FlagSet FLAG_MET_RIVAL_MOM
    WorkSetConst HOUSES_VAR, 2
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_24:                                       // zone init (Sapphire OnTransition): where Mom stands
    VMStackPush VAR_LITTLEROOT_INTRO_STATE
    VMStackPushConst 3
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_InitNot3
    ObjInitNPCGPos 0, 0, MOM_DOOR_X, 0, 8          // (index in the NPC list: Mom is first)
L_InitNot3:
    VMStackPush VAR_LITTLEROOT_INTRO_STATE
    VMStackPushConst 5
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_InitNot5
    ObjInitNPCGPos 0, 0, MOM_STAIRS_X, 0, 4
L_InitNot5:
    VMStackPush VAR_LITTLEROOT_INTRO_STATE
    VMStackPushConst 6
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_InitNot6
    ObjInitNPCGPos 0, 0, MOM_TV_X, 0, 5
L_InitNot6:
    VMHalt

Script_25:                                       // ..._1F_EventScript_GoSeeRoom (mat trigger, state 4)
    ActorsPauseAll
    ActorCmdExec 1, Mv_MomFaceEntrance
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(2), 1, 0, 0        // "Mom: Well, <player>? Aren't you interested in seeing your very own room?"
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 1, Mv_FaceUp
    ActorCmdExec 255, Mv_WalkUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_26:                                       // Mom (Sapphire ..._1F_EventScript_1B6BE9, the parts so far;
    ActorsPauseAll                               //   VAR_LITTLEROOT_HOUSES_STATE 4 "Dad should stay longer" is Ch13's)
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    WordSetPlayerName 0
#if __has_include("scenes/players_house_1f_events.inc")
#include "scenes/players_house_1f_events.inc"       // (events agent) after the S.S. Ticket: Mom gives the Eon Ticket (T(28)-T(29))
#endif
#if __has_include("scenes/players_house_1f_ch13.inc") && !defined(HOENN_EMERALD)   // (Emerald: Mom says it inside the scene, then talks as usual)
    WorkCmpConst VAR_LITTLEROOT_HOUSES_STATE, 4     // chapter Ch13: after the S.S. Ticket scene, until you leave the house
    VMJumpIf CMP_EQ, L_MomDadStays                  //   (Sapphire checks both houses' vars)
    WorkCmpConst VAR_LITTLEROOT_HOUSES_STATE_2, 4
    VMJumpIf CMP_EQ, L_MomDadStays
#endif
#define CH6_MOM_REST L_MomRest
#define CH6_MOM_T 19
#include "scenes/players_house_1f_ch6.inc"          // chapter Ch6: the Amulet Coin once you have Dad's Badge (T(19)-T(21))
    VMStackPushFlag FLAG_RESCUED_BIRCH            // goto_if_set FLAG_RESCUED_BIRCH, 1B6C72 (chapter Ch1: Mom lets you
    VMStackPushConst 1                            //   rest at home once you have your Pokémon)
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_MomRest
    VMStackPush 0x4001
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_MomNotSeeYou
    ParentActorMsg MSGFILE_SCRIPT, T(9), 0, 0     // "Mom: See you, honey!"
    VMJump L_MomTalkDone
L_MomNotSeeYou:
    VMStackPush VAR_LITTLEROOT_INTRO_STATE
    VMStackPushConst 7
    VMStackCmp CMP_GE
    VMJumpIf CMP_STACK, L_MomNice
    ParentActorMsg MSGFILE_SCRIPT, T(10), 0, 0    // "Mom: Did you introduce yourself to Prof. Birch?"
    VMJump L_MomTalkDone
L_MomNice:
    ParentActorMsg MSGFILE_SCRIPT, T(0), 0, 0     // "Mom: See, <player>? Isn't it nice in here, too?"
L_MomTalkDone:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#if __has_include("scenes/players_house_1f_ch13.inc") && !defined(HOENN_EMERALD)
L_MomDadStays:                                   // 1B6C33 (chapter Ch13): PlayersHouse_1F_Text_DadShouldStayLonger
    ParentActorMsg MSGFILE_SCRIPT, T(27), 0, 0    // Mom: That Dad of yours... He should relax and stay a little longer.
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
L_MomRest:                                       // 1B6C72 + 1B6C8A (chapter Ch1)
    ParentActorMsg MSGFILE_SCRIPT, T(22), 0, 0    // Mom: How are you doing, <player>? ... I think you should rest a bit.
    LastKeyWait
    MsgWinCloseAll
    FadeEx 3, 0, 16, 2                           // Common_EventScript_OutOfCenterPartyHeal: Black 2's own out-of-center
    FadeExWait                                   //   heal (b2:0522.s:47-53, hoenn_story.inc h_heal_party_fade)
    PokePartyRecoverAll
    MEPlay SEQ_ME_ASA
    MEWait
    FadeEx 3, 16, 0, 2
    FadeExWait
    ParentActorMsg MSGFILE_SCRIPT, T(23), 0, 0    // Mom: Take care, honey! (incrementgamestat GAME_STAT_RESTED_AT_HOME:
    LastKeyWait                                  //   no such record in Black 2)
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_27:                                       // mover, actor 2 (Sapphire's Machoke)
    ActorsPauseAll
    ActorSetEyeToEye
    PokeVoicePlay MOVER_SPECIES, 0
    ParentActorMsg MSGFILE_SCRIPT, MOVER2_TEXT, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_28:                                       // mover, actor 3
    ActorsPauseAll
    ActorSetEyeToEye
    PokeVoicePlay MOVER_SPECIES, 0
    ParentActorMsg MSGFILE_SCRIPT, MOVER3_TEXT, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_19:                                       // the Running Shoes manual (chapter Ch1): Sapphire ..._1F_EventScript_
    VMStackPushFlag FLAG_RECEIVED_RUNNING_SHOES  // CheckShowShoesManual puts a book on the table (setmetatile
    VMStackPushConst 1                           // BookOnTable) in your own house once you have the shoes, and facing
    VMStackCmp CMP_EQ                            // it reads S_RunningShoesManual (MSGBOX_SIGN). Black 2's rooms have no
    VMJumpIf CMP_STACK, L_ShoesManualNone        // metatiles to swap: the table tile is a sign (data/story/ch1.json)
    TrainerCardGetSex 0x8000                     // that reads the manual then; no book is shown.
#if HOUSE_BRENDAN
    WorkCmpConst 0x8000, 0                       // Brendan's house is a boy's own house
#else
    WorkCmpConst 0x8000, 1                       // May's house is a girl's
#endif
    VMJumpIf CMP_NE, L_ShoesManualNone
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign T(18), 2                        // It's the instruction booklet for the Running Shoes. ...
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
L_ShoesManualNone:
    VMHalt

#ifndef HOENN_EMERALD                           // Emerald: scenes/emerald/players_house_1f.inc has its own Script_29
Script_29:                                       // rival's mom (Sapphire RivalsHouse_1F_EventScript_RivalMom; the
    ActorsPauseAll                               // branches after the rival left are chapter Ch1's)
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    WordSetPlayerName 0
    VMStackPushFlag FLAG_DEFEATED_RIVAL_ROUTE103
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_RivalMomGoHome          // (jumps when the comparison is false: the flag is set)
    VMStackPushFlag FLAG_RIVAL_LEFT_FOR_ROUTE103
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_RivalMomOut
    VMStackPush VAR_LITTLEROOT_RIVAL_STATE
    VMStackPushConst 3
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_RivalMomUpstairs        // (jumps when the state is not 3)
    ParentActorMsg MSGFILE_SCRIPT, T(17), 0, 0    // "Where has my husband gone? ... He might be at his Lab."
    VMJump L_RivalMomDone
L_RivalMomGoHome:
    ParentActorMsg MSGFILE_SCRIPT, T(16), 0, 0    // "I think it's wonderful for people to travel with Pokémon. ..."
    VMJump L_RivalMomDone
L_RivalMomOut:
    ParentActorMsg MSGFILE_SCRIPT, T(15), 0, 0    // "Oh, <rival> has gone out somewhere. ..."
    VMJump L_RivalMomDone
L_RivalMomUpstairs:
    ParentActorMsg MSGFILE_SCRIPT, T(12), 0, 0    // "Our <son/daughter> is upstairs, I think."
L_RivalMomDone:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif

    .balign 4, 0                                 // movement lists are read as words (Black 2 aligns them too)
Mv_WalkUp:
    Move 12, 1
    MoveEnd

Mv_FaceUp:
    Move 0, 1
    MoveEnd

Mv_Exclaim:                                      // "!" then delay 48 (Sapphire Common_Movement_ExclamationMark + Delay48)
    Move 75, 1
    Move 63, 3
    MoveEnd

#if HOUSE_BRENDAN
Mv_MomFaceEntrance:                              // Mom beside the mat faces the player on it
    Move 2, 1
    MoveEnd
Mv_FaceMomAtDoor:
    Move 3, 1
    MoveEnd
Mv_FaceTowardStairsSide:                         // Mom at the TV turns right, toward the stairs
    Move 3, 1
    MoveEnd
Mv_PlayerToTV:                                   // from below the stairs: down x2, left x3 (Sapphire 1B6CCC)
    Move 13, 2
    Move 14, 3
    MoveEnd
Mv_MomMakeRoom:                                  // walk_left, face right (1B6BDB)
    Move 14, 1
    Move 3, 1
    MoveEnd
Mv_PlayerStepToTV:
    Move 14, 1
    MoveEnd
Mv_FaceMomAtTV:
    Move 2, 1
    MoveEnd
Mv_MomBackFromTV:                                // walk_left, walk_down, face right (1B6BE1)
    Move 14, 1
    Move 13, 1
    Move 3, 1
    MoveEnd
Mv_FaceRivalMom:
    Move 2, 1
    MoveEnd
Mv_RivalMomApproach:                             // walk_down, walk_right x5
    Move 13, 1
    Move 15, 5
    MoveEnd
#else
Mv_MomFaceEntrance:
    Move 3, 1
    MoveEnd
Mv_FaceMomAtDoor:
    Move 2, 1
    MoveEnd
Mv_FaceTowardStairsSide:
    Move 2, 1
    MoveEnd
Mv_PlayerToTV:                                   // down x2, right x3 (1B6CD4)
    Move 13, 2
    Move 15, 3
    MoveEnd
Mv_MomMakeRoom:                                  // walk_right, face left (1B6BDE)
    Move 15, 1
    Move 2, 1
    MoveEnd
Mv_PlayerStepToTV:
    Move 15, 1
    MoveEnd
Mv_FaceMomAtTV:
    Move 3, 1
    MoveEnd
Mv_MomBackFromTV:                                // walk_right, walk_down, face left (1B6BE5)
    Move 15, 1
    Move 13, 1
    Move 2, 1
    MoveEnd
Mv_FaceRivalMom:
    Move 3, 1
    MoveEnd
Mv_RivalMomApproach:                             // walk_down, walk_left x5
    Move 13, 1
    Move 14, 5
    MoveEnd
#endif
    .balign 4, 0
#if __has_include("scenes/players_house_1f_ch13.inc")
#include "scenes/players_house_1f_ch13.inc"          // chapter Ch13: script 30 (Dad brings the S.S. Ticket), T(24)-T(27)
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald/players_house_1f.inc"         // Emerald (emerald_ch0_3): the rival's introduction, the sibling, the rival's mom
#endif
