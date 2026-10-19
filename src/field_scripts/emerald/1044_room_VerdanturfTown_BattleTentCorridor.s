// VerdanturfTown_BattleTentCorridor (zone 522; Emerald only): the walk from the lobby to the battle room (pokeemerald
// data/maps/VerdanturfTown_BattleTentCorridor/scripts.inc; battle_tents, 2026-10-18). Reached only by script 1 from the
// lobby: the attendant walks the player up to the door (2,1). Room origin (1,0).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/battle_tents_lib.inc"

    ScriptEntry VC_Enter                // 1: OnFrame EnterCorridor
    ScriptEntry VC_None                 // 2: the attendant (no talk script in Emerald)
    ScriptEntriesEnd

VC_None:
    VMHalt

VC_Enter:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement 1, VC_MvToDoor
    h_applymovement TT_PLAYER, VC_MvToDoor
    h_waitmovement
    bt_door_open TT_CX(2), TT_CZ(1)     // opendoor 2, 1
    h_applymovement 1, VC_MvAttendantIn
    h_applymovement TT_PLAYER, VC_MvPlayerIn
    h_waitmovement
    fd_to_room TT_V_ROOM, TT_VRX(2), TT_VRZ(8), 0, 1, 1   // warp ..._BATTLE_ROOM (the stand-in's (2,8))

    .balign 4, 0
VC_MvToDoor:                            // Movement_WalkToDoor
    walk_up 4
    step_end
VC_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up
    set_invisible
    step_end
VC_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 2
    set_invisible
    step_end
