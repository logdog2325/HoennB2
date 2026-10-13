// BattleFrontier_BattlePikeRoomFinal (zone 404, Emerald only): the goal room (pokeemerald
// data/maps/BattleFrontier_BattlePikeRoomFinal; frontier_pike 2026-10-12, notes/FRONTIER_PIKE.md). Its origin is
// (1, -2). Messages: src/text/script/emerald/0633_room_*.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pike_lib.inc"

#define PK_ATTENDANT 1                  // LOCALID_PIKE_FINAL_ROOM_ATTENDANT (2,4)

    ScriptEntry PKF_Enter               // 1: ON_FRAME _EnterRoom (condition PK_W_STATE 0)
    ScriptEntry PKF_None                // 2: the attendant (no script in Emerald)
    ScriptEntriesEnd

PKF_None:
    VMHalt

PKF_Enter:
    WorkSetConst PK_W_STATE, 1
    ActorsPauseAll
    h_delay 16
    h_applymovement PK_ATTENDANT, PKF_MvIn
    h_waitmovement
    fr_set FR_STATUS, FR_ST_WON         // frontier_set FRONTIER_DATA_CHALLENGE_STATUS, CHALLENGE_STATUS_WON
    pk_say PKL_FINAL_CONGRATS, PK_ATTENDANT     // Congratulations… Now, this way, please…
    h_closemessage
    h_warp_arrive PK_LOBBY_ZONE, 5 + PK_OX, 6 + PK_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
PKF_MvIn:                               // _Movement_AttendantApproachPlayer
    walk_down 2
    step_end
