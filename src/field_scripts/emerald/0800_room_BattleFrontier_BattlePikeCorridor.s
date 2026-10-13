// BattleFrontier_BattlePikeCorridor (zone 400, Emerald only): pokeemerald data/maps/BattleFrontier_BattlePikeCorridor
// (frontier_pike 2026-10-12, notes/FRONTIER_PIKE.md). Reached only from the lobby's receptionist (the player arrives at
// Emerald (6,7)); script 1 is Emerald's ON_FRAME scene. Messages: src/text/script/emerald/0629_room_*.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pike_lib.inc"

#define PK_ATTENDANT 1                  // Emerald LOCALID_PIKE_CORRIDOR_ATTENDANT (6,6)

    ScriptEntry PKC_Enter               // 1: BattleFrontier_BattlePikeCorridor_EventScript_EnterCorridor
    ScriptEntry PKC_None                // 2: the attendant (no script in Emerald)
    ScriptEntriesEnd

PKC_None:
    VMHalt

PKC_Enter:
    WorkSetConst PK_W_STATE, 1
    ActorsPauseAll
    h_delay 16
    fr_set FR_BATTLE_NUM, 1             // frontier_set FRONTIER_DATA_BATTLE_NUM, 1
    pk_set PKF_HEAL_OFF, 1              // pike_nohealing TRUE (pike_cleartrainerids: PK_INIT's)
    h_applymovement PK_PLAYER, PKC_MvPlayerIn
    h_applymovement PK_ATTENDANT, PKC_MvAttendant
    h_waitmovement
    pk_say PKL_CORRIDOR_BEGUN, PK_ATTENDANT     // Your Battle Choice challenge has now begun…
    h_closemessage
    h_applymovement PK_PLAYER, PKC_MvPlayerOut
    h_waitmovement
    fr_set FR_STATUS, PK_ST_IN_CHALLENGE        // frontier_set FRONTIER_DATA_CHALLENGE_STATUS, 99
    pk_curtain_warp PK_THREE_ZONE, 6 + PK_OX, 10 + PK_OZ

    .balign 4, 0
PKC_MvPlayerIn:
    walk_up 2
    step_end
PKC_MvPlayerOut:
    walk_up 2
    set_invisible
    step_end
PKC_MvAttendant:
    walk_up 2
    walk_left
    face_down
    step_end
