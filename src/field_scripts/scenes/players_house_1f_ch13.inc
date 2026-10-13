// Chapter Ch13's beat in the player's house 1F (Sapphire data/scripts/players_house.inc PlayersHouse_1F_EventScript_
// GetSSTicketAndSeeLatiTV and its movements; ch13 agent, 2026-10-07): after the Hall of Fame Dad (Norman) is home and brings
// the S.S. Ticket "that came from Mr. Briney". Included at the END of scenes/players_house_1f.inc (guarded), which defines
// HOUSE_BRENDAN, T(n) and the shared Mv_Exclaim; it needs no other library (the house files do not include hoenn_story.inc).
// Text (both houses' text files, lines T(24)-T(27), copied from Sapphire):
//   T(24) "Dad: Hm? Hey, it's <player>! ... This came to you from someone named Mr. Briney."
//   T(25) "Dad: Hm, a Ticket for a ferry? ... go to the Battle Tower. ..."
//   T(26) "I'd better get back to Petalburg Gym. Mom, thanks for looking after the house while I'm away."
//   T(27) "Mom: That Dad of yours... He should relax and stay a little longer."   (Mom's script 26, state 4)
// Script 30 is the map-script condition VAR_LITTLEROOT_HOUSES_STATE 3 (init files 0781 / 0785, Sapphire's OnFrame table of
// both houses): it runs when the player comes down the stairs from their room after the credits (the Hall of Fame wakes
// them up there, chapter Ch11). Sapphire runs it in either house by the player's gender; the rival's house is not a place
// Dad is in, so here it waits there until the player's own house is entered (no scene, no state change).
// The movements are Sapphire's own for a boy (Brendan's house) and a girl (May's house, mirrored): the player walks down
// three tiles from the stairs, Dad turns, "!", walks over, the lines, the S.S. Ticket, Dad steps back, leaves by the door.
// The lines of the second page ("I'd better get back to Petalburg Gym") are said while Dad stands one tile off.
#define CH13_NORMAN 5                                  // Dad's uid (data/interiors/390.json, 392.json; hidden by FLAG_HIDE_NORMAN_LITTLEROOT)
#ifdef HOENN_EMERALD
#include "scenes/emerald/players_house_1f_ch13.inc"    // Emerald's scene (emerald_ch11_gameclear): Mom's Lati news and colour question; replaces the rest of this file
#else

Script_30:                                       // PlayersHouse_1F_EventScript_GetSSTicketAndSeeLatiTV
    ActorsPauseAll
    TrainerCardGetSex 0x8030
#if HOUSE_BRENDAN
    WorkCmpConst 0x8030, 0                       // Brendan's house is the boy's own house
#else
    WorkCmpConst 0x8030, 1                       // May's is the girl's
#endif
    VMJumpIf CMP_EQ, L_C13_Mine
    FinishAllEvents                              // the rival's house: not the scene's place (see above)
    ActorsUnpauseAll
    VMHalt
L_C13_Mine:
    ActorCmdExec 255, Mv_C13_PlayerComesDown     // LittlerootTown_BrendansHouse_1F_Movement_1B6E49 / ..._1B6E54
    ActorCmdWait
    ActorCmdExec CH13_NORMAN, Mv_C13_DadFacesPlayer      // Common_Movement_FacePlayer
    ActorCmdWait
    ActorCmdExec CH13_NORMAN, Mv_Exclaim                 // SE_PIN + Common_Movement_ExclamationMark + Delay48
    ActorCmdWait
    VMSleep 10                                   // delay 20
    ActorCmdExec CH13_NORMAN, Mv_C13_DadComesOver        // ..._1B6E33 / ..._1B6E36
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(24), CH13_NORMAN, 0, 0    // Dad: Hm? Hey, it's <player>! ... from someone named Mr. Briney.
    LastKeyWait
    MsgWinCloseAll                               // (Black 2: the item script opens its own window)
    ItemCheckSpace ITEM_SS_TICKET, 1, 0x8031     // giveitem ITEM_SS_TICKET (hoenn_story.inc h_giveitem; no bag-full line in Sapphire)
    WorkCmpConst 0x8031, 0
    VMJumpIf CMP_EQ, L_C13_Given
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSetConst 0x8000, ITEM_SS_TICKET
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
L_C13_Given:
    ActorMsg MSGFILE_SCRIPT, T(25), CH13_NORMAN, 0, 0    // Dad: Hm, a Ticket for a ferry? ... no end to a Trainer's chosen path.
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec CH13_NORMAN, Mv_C13_DadStepsBack        // ..._1B6E39 / ..._1B6E3B
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, T(26), CH13_NORMAN, 0, 0    // I'd better get back to Petalburg Gym. Mom, thanks for ...
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Mv_C13_PlayerWatches               // ..._1B6E4F
    ActorCmdExec CH13_NORMAN, Mv_C13_DadLeaves           // ..._1B6E3D / ..._1B6E43
    ActorCmdWait
    SEPlay SEQ_SE_KAIDAN                         // SE_DOOR
    ActorDelete CH13_NORMAN
    FlagSet FLAG_HIDE_NORMAN_LITTLEROOT          // removeobject
    FlagSet FLAG_RECEIVED_SS_TICKET
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE, 4
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE_2, 4
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
#if HOUSE_BRENDAN
Mv_C13_PlayerComesDown:                          // delay_16, walk_down x3, walk_in_place_fastest_left
    Move 63, 1
    Move 13, 3
    Move 42, 1
    MoveEnd
Mv_C13_DadFacesPlayer:                           // Dad at (5,6), the player ends at (8,6)
    Move 3, 1
    MoveEnd
Mv_C13_DadComesOver:                             // walk_right x2
    Move 15, 2
    MoveEnd
Mv_C13_DadStepsBack:                             // walk_left
    Move 14, 1
    MoveEnd
Mv_C13_DadLeaves:                                // walk_down, walk_right x2, walk_down, delay_8
    Move 13, 1
    Move 15, 2
    Move 13, 1
    Move 62, 1
    MoveEnd
#else
Mv_C13_PlayerComesDown:                          // delay_16, walk_down x3, walk_in_place_fastest_right
    Move 63, 1
    Move 13, 3
    Move 43, 1
    MoveEnd
Mv_C13_DadFacesPlayer:                           // Dad at (5,6), the player ends at (2,6)
    Move 2, 1
    MoveEnd
Mv_C13_DadComesOver:                             // walk_left x2
    Move 14, 2
    MoveEnd
Mv_C13_DadStepsBack:                             // walk_right
    Move 15, 1
    MoveEnd
Mv_C13_DadLeaves:                                // walk_down, walk_left x2, walk_down, delay_8
    Move 13, 1
    Move 14, 2
    Move 13, 1
    Move 62, 1
    MoveEnd
#endif
Mv_C13_PlayerWatches:                            // delay_16 x3, walk_in_place_fastest_down
    Move 63, 3
    Move 41, 1
    MoveEnd
    .balign 4, 0
#endif
