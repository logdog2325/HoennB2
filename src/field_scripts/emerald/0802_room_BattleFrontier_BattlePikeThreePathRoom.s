// BattleFrontier_BattlePikeThreePathRoom (zone 401, Emerald only): pokeemerald
// data/maps/BattleFrontier_BattlePikeThreePathRoom + data/scripts/battle_pike.inc (frontier_pike 2026-10-12,
// notes/FRONTIER_PIKE.md). The three curtain doorways (2,3), (6,3), (10,3) are step triggers (Emerald's coord
// events); the room's choice (Emerald's odds) is frontier_pike.c's. Messages: src/text/script/emerald/0630_room_*.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pike_lib.inc"

#define PK_ATTENDANT 1                  // Emerald object 1 (4,10), facing right
#define PK_HINT_GIVER 2                 // LOCALID_PIKE_HINT_GIVER (8,5)

    ScriptEntry PKT_Attendant           // 1: _EventScript_Attendant
    ScriptEntry PKT_HintGiver           // 2: _EventScript_HintGiver
    ScriptEntry PKT_DoorLeft            // 3: _LeftRoomWarp (trigger (2,3))
    ScriptEntry PKT_DoorCenter          // 4: _CenterRoomWarp (6,3)
    ScriptEntry PKT_DoorRight           // 5: _RightRoomWarp (10,3)
    ScriptEntry PKT_Entered             // 6: _SetEnteredRoom (5-7,9)
    ScriptEntry PKT_NoTurningBack       // 7: _NoTurningBack (5-7,10)
    ScriptEntry PKT_State               // 8: ON_FRAME (condition PK_W_STATE 0)
    ScriptEntriesEnd

// ON_FRAME: VAR_TEMP_CHALLENGE_STATUS 0 -> frontier_getstatus: SAVING -> _WarpToLobby (a Continue after quitting
// without the save: the lobby disqualifies), PAUSED -> _ResumeChallenge; then VAR_TEMP_5 0 -> _SetHintRoom (Lucy's
// warning when she waits behind the next doorway)
PKT_State:
    WorkSetConst PK_W_STATE, 1
    ActorsPauseAll
    fr_get FR_STATUS, PK_T0
    h_goto_if_eq PK_T0, FR_ST_SAVING, L_PKT_ToLobby
    h_goto_if_ne PK_T0, FR_ST_PAUSED, L_PKT_Hint
    // _ResumeChallenge: "We've been awaiting your return…", pike_save CHALLENGE_STATUS_SAVING, PAUSED FALSE,
    // "Please do enjoy…", the challenge goes on (status 99)
    pk_print PKL_THREE_AWAITING, PK_ATTENDANT
    fr_set FR_STATUS, FR_ST_SAVING
    pk_set PKF_PAUSED, 0
    fr_save_quiet
    pk_say PKL_THREE_ENJOY, PK_ATTENDANT
    h_closemessage
    fr_set FR_STATUS, PK_ST_IN_CHALLENGE
L_PKT_Hint:
    EmPike PK_T0, PK_SET_HINT           // pike_sethintroom: TRUE = the Pike Queen is next
    h_goto_if_eq PK_T0, 0, L_PKT_StateEnd
    h_applymovement PK_HINT_GIVER, PKT_MvHintIn         // _GivePikeQueenHint
    h_waitmovement
    pk_say PKL_THREE_TERRIFYING, PK_HINT_GIVER
    h_closemessage
    h_applymovement PK_HINT_GIVER, PKT_MvHintBack
    h_waitmovement
L_PKT_StateEnd:
    h_release
L_PKT_ToLobby:                          // _WarpToLobby: warp MAP_BATTLE_FRONTIER_BATTLE_PIKE_LOBBY, 5, 6
    h_warp_arrive PK_LOBBY_ZONE, 5 + PK_OX, 6 + PK_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// _Attendant: "You are currently in the Nth room…", continue? / save and quit? / retire?
PKT_Attendant:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    fr_get FR_BATTLE_NUM, PK_T0
    WorkSetConst PK_T1, PKL_THREE_ROOM13
    h_goto_if_ge PK_T0, 13, L_PKT_Room
    WorkSetConst PK_T1, PKL_THREE_ROOM11
    h_goto_if_ge PK_T0, 11, L_PKT_Room
    WorkSetConst PK_T1, PKL_THREE_ROOM9
    h_goto_if_ge PK_T0, 9, L_PKT_Room
    WorkSetConst PK_T1, PKL_THREE_ROOM7
    h_goto_if_ge PK_T0, 7, L_PKT_Room
    WorkSetConst PK_T1, PKL_THREE_ROOM5
    h_goto_if_ge PK_T0, 5, L_PKT_Room
    WorkSetConst PK_T1, PKL_THREE_ROOM3
    h_goto_if_ge PK_T0, 3, L_PKT_Room
    WorkSetConst PK_T1, PKL_THREE_ROOM1
L_PKT_Room:
    ParentActorMsg MSGFILE_SCRIPT, PK_T1, 0, 0
    LastKeyWait
    h_yesno PKL_THREE_CONTINUE, PK_T0   // _AskContinueChallenge
    h_goto_if_yes PK_T0, L_PKT_Bye
    h_yesno PKL_THREE_SAVE_QUIT, PK_T0  // _AskSaveChallenge
    h_goto_if_yes PK_T0, L_PKT_Pause
    ParentActorMsg MSGFILE_SCRIPT, PKL_THREE_RETIRE, 0, 0   // _AskRetireChallenge: multichoicedefault YES/NO, NO first
    ListMenu_AnchorTopRight 31, 8, 1, 1, PK_T0  // (values 1 YES / 2 NO: B gives neither)
    ListMenuAdd PKL_THREE_M_YES, 65535, 1
    ListMenuAdd PKL_THREE_M_NO, 65535, 2
    ListMenuShow
    h_goto_if_eq PK_T0, 1, L_PKT_Retire
L_PKT_Bye:
    h_closemessage
    h_release
L_PKT_Pause:                            // _PauseChallenge: "I am saving your data…", pike_save PAUSED, the reset. A
    pk_set PKF_PAUSED, 1                // Continue starts here (the arrival tile, facing north), as Emerald's save of
    fr_rest_and_quit PK_THREE_ZONE, 6 + PK_OX, 10 + PK_OZ, 0, PKL_THREE_SAVING, PK_ATTENDANT   // the map view
L_PKT_Retire:                           // BattleFrontier_BattlePike_EventScript_Retire
    h_closemessage
    fr_set FR_STATUS, FR_ST_LOST
    h_warp_arrive PK_LOBBY_ZONE, 5 + PK_OX, 6 + PK_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// _HintGiver: pike_gethint (BRAIN: "a dreadful presence"); "difficult to choose?" YES -> which doorway, what it holds
PKT_HintGiver:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    EmPike PK_T0, PK_HINT_KIND
    h_goto_if_eq PK_T0, PIKE_HINT_BRAIN, L_PKT_Dreadful
    h_yesno PKL_THREE_DIFFICULT, PK_T1
    h_goto_if_yes PK_T1, L_PKT_Accept
    h_msgbox PKL_THREE_APOLOGIZE
    h_closemessage
    h_release
L_PKT_Accept:
    EmPike PK_T1, PK_HINT_ROOM
    WorkSetConst PK_T2, PKL_THREE_LEFT
    h_goto_if_eq PK_T1, PIKE_ROOM_LEFT, L_PKT_Which
    WorkSetConst PK_T2, PKL_THREE_CENTER
    h_goto_if_eq PK_T1, PIKE_ROOM_CENTER, L_PKT_Which
    WorkSetConst PK_T2, PKL_THREE_RIGHT
L_PKT_Which:
    ParentActorMsg MSGFILE_SCRIPT, PK_T2, 0, 0
    LastKeyWait
    WorkSetConst PK_T2, PKL_THREE_NOSTALGIA
    h_goto_if_eq PK_T0, PIKE_HINT_NOSTALGIA, L_PKT_Kind
    WorkSetConst PK_T2, PKL_THREE_WHISPER
    h_goto_if_eq PK_T0, PIKE_HINT_WHISPERING, L_PKT_Kind
    WorkSetConst PK_T2, PKL_THREE_AROMA
    h_goto_if_eq PK_T0, PIKE_HINT_POKEMON, L_PKT_Kind
    WorkSetConst PK_T2, PKL_THREE_PEOPLE
L_PKT_Kind:
    ParentActorMsg MSGFILE_SCRIPT, PK_T2, 0, 0
    LastKeyWait
    h_closemessage
    h_release
L_PKT_Dreadful:
    h_msgbox PKL_THREE_DREADFUL
    h_closemessage
    h_release

// _RoomWarp (VAR_0x8007 = the doorway): streak + 1, room number + 1, pike_setnextroom, the room by its type
PKT_DoorLeft:
    WorkSetConst PK_T0, PIKE_ROOM_LEFT
    VMJump L_PKT_RoomWarp
PKT_DoorCenter:
    WorkSetConst PK_T0, PIKE_ROOM_CENTER
    VMJump L_PKT_RoomWarp
PKT_DoorRight:
    WorkSetConst PK_T0, PIKE_ROOM_RIGHT
L_PKT_RoomWarp:
    ActorsPauseAll
    pk_streak_win
    pk_room_plus_one
    EmPike PK_T1, PK_NEXT_ROOM, PK_T0
    h_applymovement PK_PLAYER, PKT_MvHide
    h_waitmovement
    h_goto_if_eq PK_T1, PIKE_ROOM_WILD_MONS, L_PKT_Wild
    pk_curtain_warp PK_ROOM_ZONE, 4 + PK_OX, 7 + PK_OZ      // warpsilent MAP_..._ROOM_NORMAL, 4, 7
L_PKT_Wild:
    pk_curtain_warp PK_WILD_ZONE, 4 + PK_OX, 19 + PK_OZ     // warpsilent MAP_..._ROOM_WILD_MONS, 4, 19

PKT_Entered:                            // _SetEnteredRoom
    WorkSetConst PK_W_NO_TURN, 1
    WorkSetConst PK_W_ENTERED, 1
    VMHalt
PKT_NoTurningBack:                      // _NoTurningBack
    WorkSetConst PK_W_NO_TURN, 0
    WorkSetConst PK_W_ENTERED, 0
    ActorsPauseAll
    h_msgbox_info PKL_THREE_BLOCKED     // The path is blocked! And there is no turning back…
    h_closemessage
    h_release

    .balign 4, 0
PKT_MvHide:                             // BattleFrontier_BattlePikeRoom_Movement_HidePlayer
    set_invisible
    step_end
PKT_MvHintIn:                           // _Movement_HintGiverApproachPlayer
    walk_left 2
    walk_down 4
    step_end
PKT_MvHintBack:                         // _Movement_HintGiverReturnToPos
    walk_up 4
    walk_right 2
    face_down
    step_end
