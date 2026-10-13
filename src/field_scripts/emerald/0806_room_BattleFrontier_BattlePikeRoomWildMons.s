// BattleFrontier_BattlePikeRoomWildMons (zone 403, Emerald only): the wild Pokémon room (pokeemerald
// data/maps/BattleFrontier_BattlePikeRoomWildMons + data/scripts/battle_pike.inc; frontier_pike 2026-10-12,
// notes/FRONTIER_PIKE.md). Every step in it is Emerald's StandardWildEncounter for this layout (frontier_pike.c
// PK_CheckEncounter: encounter rate 10, Stench / Illuminate / Cleanse Tag), which starts script 3: the Pokémon of
// gBattlePike_1-4 by the streak, at Emerald's level, with its Pike moves (PK_EncSetupNormal), no experience.
// Messages: src/text/script/emerald/0632_room_*.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pike_lib.inc"

    ScriptEntry PKW_Exit                // 1: _EventScript_Exit (trigger (4,3))
    ScriptEntry PKW_Entered             // 2: _SetEnteredRoom (3-5,18)
    ScriptEntry PKW_Battle              // 3: a wild Pokémon (frontier_pike.py WILD_SCRIPT)
    ScriptEntry PKW_NoTurningBack       // 4: _NoTurningBack (3-5,19)
    ScriptEntriesEnd

// TryGenerateBattlePikeWildMon + BattleSetup_StartBattlePikeWildBattle; ON_RESUME: lost or drew -> _WarpToLobbyLost
PKW_Battle:
    ActorsPauseAll
    EmPike PK_T0, PK_WILD               // the species (0: Keen Eye / Intimidate kept it away), level in PK_W_WILD_LV
    h_goto_if_eq PK_T0, 0, L_PKW_None
    CallWildBattle PK_T0, PK_W_WILD_LV, 0x100           // (0x100: no experience, Black 2's own flag)
    CallWildBattleEnd
    EmPike PK_T1, PK_ALL_FAINTED        // lost or drew: none of the three can battle
    h_goto_if_ne PK_T1, 0, L_PKW_Lost
L_PKW_None:
    h_release
L_PKW_Lost:                             // _WarpToLobbyLost
    fr_set FR_STATUS, FR_ST_LOST
    h_warp_arrive PK_LOBBY_ZONE, 5 + PK_OX, 6 + PK_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// _Exit: pike_exitwildmonroom, pike_ispartyfullhealth -> pike_nohealing, streak + 1, room + 1, the next room
PKW_Exit:
    ActorsPauseAll
    EmPike PK_T0, PK_FULL_HEALTH
    pk_set PKF_HEAL_OFF, PK_T0
    pk_streak_win
    pk_room_plus_one
    EmPike PK_T0, PK_IS_FINAL
    h_applymovement PK_PLAYER, PKW_MvHide
    h_waitmovement
    h_goto_if_eq PK_T0, 1, L_PKW_Final
    pk_curtain_warp PK_THREE_ZONE, 6 + PK_OX, 10 + PK_OZ
L_PKW_Final:
    pk_curtain_warp PK_FINAL_ZONE, 2 + PK_FINAL_OX, 7 + PK_FINAL_OZ

PKW_Entered:
    WorkSetConst PK_W_NO_TURN, 1
    WorkSetConst PK_W_ENTERED, 1
    VMHalt
PKW_NoTurningBack:
    WorkSetConst PK_W_NO_TURN, 0
    WorkSetConst PK_W_ENTERED, 0
    ActorsPauseAll
    h_msgbox_info PKL_WILD_BLOCKED
    h_closemessage
    h_release

    .balign 4, 0
PKW_MvHide:
    set_invisible
    step_end
