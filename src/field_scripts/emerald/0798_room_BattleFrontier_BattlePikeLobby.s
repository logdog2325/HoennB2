// BattleFrontier_BattlePikeLobby (zone 399, Emerald only): Emerald's Battle Pike lobby (pokeemerald
// data/maps/BattleFrontier_BattlePikeLobby/scripts.inc; frontier_pike 2026-10-12, notes/FRONTIER_PIKE.md).
// The receptionist and the return to the lobby are frontier_core's lobby macros (src/include/hoenn_frontier.inc:
// Emerald's flow, its lobby text block = lines 0-22 of the room's text); the Pike's own steps are their hooks.
// Messages: src/text/script/emerald/0628_room_BattleFrontier_BattlePikeLobby.txt (converter/gen_frontier_pike.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pike_lib.inc"

#define PK_ATTENDANT 1                  // the receptionist (Emerald LOCALID_PIKE_LOBBY_ATTENDANT, (5,5))

    ScriptEntry PKL_Attendant           // 1: BattleFrontier_BattlePikeLobby_EventScript_Attendant
    ScriptEntry PKL_Hiker               // 2: _Hiker
    ScriptEntry PKL_Twin                // 3: _Twin
    ScriptEntry PKL_Beauty              // 4: _Beauty
    ScriptEntry PKL_Results             // 5: _ShowResults (sign (8,3))
    ScriptEntry PKL_Rules               // 6: _RulesBoard (sign (1,3))
    ScriptEntry PKL_State               // 7: ON_FRAME (map-script condition PK_W_STATE 0: the challenge's outcome)
    ScriptEntriesEnd

PKL_Attendant:
    fr_lobby_attendant FRONTIER_FACILITY_PIKE, FRONTIER_MODE_SINGLES, PKL_LOBBY_TB, L_PKL_Enter, 3, , Sub_PKL_Unpick, Sub_PKL_OnSave

// _SaveBeforeChallenge, before the save: pike_init, the streak goes on, the three first (frontier_setpartyorder:
// Black 2's party keeps all six, the battles take the first three), pike_savehelditems, not paused
Sub_PKL_OnSave:
    fr_get FR_LVL_MODE, PK_T0
    EmPike PK_T1, PK_INIT, PK_T0
    pk_set PKF_STREAK_ACTIVE, 1
    EmPike PK_T1, PK_PARTY_ORDER, 1
    EmPike PK_T1, PK_SAVE_ITEMS
    pk_set PKF_PAUSED, 0
    VMReturn
Sub_PKL_Unpick:                         // NO to the save, or the save refused: the party's order back
    EmPike PK_T1, PK_PARTY_ORDER, 0
    VMReturn

L_PKL_Enter:                            // after "Please step this way…": _WalkToCorridor, HealPlayerParty, the curtain,
    h_applymovement PK_ATTENDANT, PKL_MvAttendant       // warpsilent MAP_BATTLE_FRONTIER_BATTLE_PIKE_CORRIDOR, 6, 7
    h_applymovement PK_PLAYER, PKL_MvPlayer
    h_waitmovement
    h_heal
    pk_curtain_warp PK_CORRIDOR_ZONE, 6 + PK_OX, 7 + PK_OZ

PKL_Hiker:
    h_msgbox_npc PKL_LOBBY_HIKER
PKL_Twin:
    h_msgbox_npc PKL_LOBBY_TWIN
PKL_Beauty:
    h_msgbox_npc PKL_LOBBY_BEAUTY

// frontier_results FRONTIER_FACILITY_PIKE (ShowPikeResultsWindow): each level's rooms cleared (Current while its
// streak goes on, else Prev.), the record and the times cleared, as messages
PKL_Results:
    ActorsPauseAll
    WordSetPlayerName 0
    h_msgbox_info PKL_LOBBY_RES_TITLE
    fr_get FR_LVL_MODE, PK_T2           // (read both levels: the level mode is put back afterwards)
    fr_set FR_LVL_MODE, FR_LVL_50
    VMCall Sub_PKL_ResultNumbers
    h_goto_if_eq PK_T0, 0, L_PKL_Prev50
    h_msgbox_info PKL_LOBBY_RES_50_CUR
    VMJump L_PKL_Open
L_PKL_Prev50:
    h_msgbox_info PKL_LOBBY_RES_50_PREV
L_PKL_Open:
    fr_set FR_LVL_MODE, FR_LVL_OPEN
    VMCall Sub_PKL_ResultNumbers
    h_goto_if_eq PK_T0, 0, L_PKL_PrevOpen
    h_msgbox_info PKL_LOBBY_RES_OPEN_CUR
    VMJump L_PKL_ResEnd
L_PKL_PrevOpen:
    h_msgbox_info PKL_LOBBY_RES_OPEN_PREV
L_PKL_ResEnd:
    fr_set FR_LVL_MODE, PK_T2
    h_closemessage
    h_release
Sub_PKL_ResultNumbers:                  // words 1-3: streak, record, times cleared; PK_T0 = the streak goes on
    pk_get PKF_STREAK, PK_T1
    WordSetNumber 1, PK_T1, 4
    pk_get PKF_RECORD, PK_T1
    WordSetNumber 2, PK_T1, 4
    pk_get PKF_TOTAL, PK_T1
    WordSetNumber 3, PK_T1, 4
    pk_get PKF_STREAK_ACTIVE, PK_T0
    VMReturn

PKL_Rules:                              // _RulesBoard
    ActorsPauseAll
    h_msgbox_info PKL_LOBBY_RULES_LISTED
L_PKL_RulesMenu:                        // _ReadRulesBoard: multichoice 16, 4, MULTI_BATTLE_PIKE_RULES
    SystemMsg PKL_LOBBY_READ_WHICH, 2
    ListMenu_AnchorTopRight 31, 4, 0, 1, PK_T0
    ListMenuAdd PKL_LOBBY_M_RULE_BAG, 65535, 0
    ListMenuAdd PKL_LOBBY_M_RULE_ITEMS, 65535, 1
    ListMenuAdd PKL_LOBBY_M_RULE_ORDER, 65535, 2
    ListMenuAdd PKL_LOBBY_TB + FRT_MENU_EXIT, 65535, 3
    ListMenuShow
    h_goto_if_eq PK_T0, 0, L_PKL_RuleBag
    h_goto_if_eq PK_T0, 1, L_PKL_RuleItems
    h_goto_if_eq PK_T0, 2, L_PKL_RuleOrder
    h_closemessage
    h_release
L_PKL_RuleBag:
    h_msgbox_info PKL_LOBBY_RULE_BAG
    VMJump L_PKL_RulesMenu
L_PKL_RuleItems:
    h_msgbox_info PKL_LOBBY_RULE_ITEMS
    VMJump L_PKL_RulesMenu
L_PKL_RuleOrder:
    h_msgbox_info PKL_LOBBY_RULE_ORDER
    VMJump L_PKL_RulesMenu

// ON_FRAME VAR_TEMP_CHALLENGE_STATUS: frontier_getstatus -> _QuitWithoutSaving / _WonChallenge / _LostChallenge.
// frontier_core's fr_lobby_returned says the lines, pays Emerald's BP (+10 after Lucy: FR_BRAIN_BEATEN) and saves;
// the Pike's own steps are the hooks (held items back, the party's order back, the streak flags).
PKL_State:
    WorkSetConst PK_W_STATE, 1
    fr_lobby_returned FRONTIER_FACILITY_PIKE, FRONTIER_MODE_SINGLES, PKL_LOBBY_TB, PK_ATTENDANT, L_PKL_NoResume, Sub_PKL_Quit, Sub_PKL_Won, Sub_PKL_Lost
L_PKL_NoResume:                         // (the Pike resumes in its three-path room, never here)
    h_release

Sub_PKL_Quit:                           // _QuitWithoutSaving: HealPlayerParty, pike_resethelditems, streak 0, not active
    EmPike PK_T1, PK_RESTORE_ITEMS
    EmPike PK_T1, PK_PARTY_ORDER, 0
    h_heal
    pk_set PKF_STREAK, 0
    pk_set PKF_STREAK_ACTIVE, 0
    VMReturn
Sub_PKL_Won:                            // _WonChallenge: PIKE_DATA_TOTAL_STREAKS + 1, LoadPlayerParty, HealPlayerParty,
    pk_get PKF_TOTAL, PK_T1             // pike_resethelditems (the points and the save: the macro)
    WorkAdd PK_T1, 1
    pk_set PKF_TOTAL, PK_T1
    EmPike PK_T1, PK_RESTORE_ITEMS
    EmPike PK_T1, PK_PARTY_ORDER, 0
    h_heal
    VMReturn
Sub_PKL_Lost:                           // _LostChallenge: BATTLE_NUM 0, the streak ends, LoadPlayerParty, heal, items
    fr_set FR_BATTLE_NUM, 0
    pk_set PKF_STREAK_ACTIVE, 0
    EmPike PK_T1, PK_RESTORE_ITEMS
    EmPike PK_T1, PK_PARTY_ORDER, 0
    h_heal
    VMReturn

    .balign 4, 0
PKL_MvPlayer:                           // _Movement_PlayerWalkToCorridor (it runs on into the attendant's list)
    walk_up
PKL_MvAttendant:                        // _Movement_AttendantWalkToCorridor
    walk_up 2
    set_invisible
    step_end
