// BattleFrontier_BattlePyramidLobby (zone 347, Emerald only): Emerald's Battle Pyramid lobby (pokeemerald
// data/maps/BattleFrontier_BattlePyramidLobby/scripts.inc; frontier_pyramid 2026-10-12, notes/FRONTIER_PYRAMID.md).
// The receptionist and the return to the lobby are frontier_core's lobby macros (src/include/hoenn_frontier.inc:
// Emerald's flow, its lobby text block = lines 0-22 of the room's text); the Pyramid's own steps are their hooks: the
// held-item rule of the picks, the Battle Bag exchanged at the floor panel, the bag returned and the Battle Bag kept or
// lost. The fortune teller (the hint giver), the results and rules boards, the two people.
// Messages: src/text/script/emerald/0559_room_BattleFrontier_BattlePyramidLobby.txt (converter/gen_frontier_pyramid.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pyramid_lib.inc"

#define PY_ATTENDANT 1                  // LOCALID_PYRAMID_LOBBY_ATTENDANT (7,12)
#define PYL_HINT_NPC 2                  // LOCALID_PYRAMID_LOBBY_HINT_GIVER (14,13)

    // frontier_pike's command 290 op 21 (PK_PARTY_ORDER, a = 1 the picks first / 0 back): the three first in the party
    .macro py_party_order apply
    FieldCommand 290
    .2byte PY_T3
    .2byte 21
    .2byte \apply
    .2byte 0
    .endm

    ScriptEntry PYL_Attendant           // 1: _Attendant
    ScriptEntry PYL_HintGiver           // 2: _HintGiver
    ScriptEntry PYL_Woman               // 3: _Woman
    ScriptEntry PYL_FatMan              // 4: _FatMan
    ScriptEntry PYL_Results             // 5: _ShowResults (sign (5,12))
    ScriptEntry PYL_Rules               // 6: _RulesBoard (sign (1,12))
    ScriptEntry PYL_State               // 7: ON_FRAME (map-script condition PY_W_STATE 0: the challenge's outcome)
    ScriptEntriesEnd

PYL_Attendant:
    fr_lobby_attendant FRONTIER_FACILITY_PYRAMID, FRONTIER_MODE_SINGLES, PYL_LOBBY_TB, L_PYL_Enter, 3, Sub_PYL_Pick, Sub_PYL_Unpick, Sub_PYL_OnSave

// the pick: Emerald's lobby takes no Pokemon holding an item (CheckPartyIneligibility's Pyramid case, the party menu's
// GetBattleEntryEligibility); FR_T0 = the level mode; FR_T1 = 1 picked, 0 not
Sub_PYL_Pick:
    EmPyr PY_T0, PY_ELIGIBLE, FR_T0
    h_goto_if_ge PY_T0, 3, L_PYL_PickOk
    FrGet FR_GET_BANNED_NAMES | 1, FR_T3
    WorkCmpConst FR_T0, FR_LVL_50
    VMJumpIf CMP_NE, L_PYL_NotEnoughOpen
    h_msgbox PYL_LOBBY_TB + FRT_NOT_ENOUGH_50
    WorkSetConst FR_T1, 0
    VMReturn
L_PYL_NotEnoughOpen:
    h_msgbox PYL_LOBBY_TB + FRT_NOT_ENOUGH_OPEN
    WorkSetConst FR_T1, 0
    VMReturn
L_PYL_PickOk:
    h_msgbox PYL_LOBBY_TB + FRT_CHOOSE
    h_closemessage
L_PYL_PickAgain:
    fr_pick_party 3, L_PYL_PickCancel
    EmPyr PY_T0, PY_PICKS_HOLD
    h_goto_if_eq PY_T0, 0, L_PYL_Picked
    h_msgbox_info PYL_LOBBY_CANT_PARTICIPATE
    h_closemessage
    VMJump L_PYL_PickAgain
L_PYL_Picked:
    WorkSetConst FR_T1, 1
    VMReturn
L_PYL_PickCancel:
    WorkSetConst FR_T1, 0
    VMReturn

// _SaveBeforeChallenge, before the save: pyramid_init, the streak goes on, pyramid_seedfloor, pyramid_settrainers,
// the three first in the party (frontier_setpartyorder: Black 2's party keeps all six, the battles take the first three)
Sub_PYL_OnSave:
    fr_get FR_LVL_MODE, PY_T0
    EmPyr PY_T1, PY_INIT, PY_T0
    EmPyr PY_T1, PY_SET_STREAK_ACTIVE, 1
    EmPyr PY_T1, PY_SEED
    EmPyr PY_T1, PY_ARRIVAL, 0
    py_party_order 1
    VMReturn
Sub_PYL_Unpick:                         // NO to the save, or the save refused: the party's order back
    py_party_order 0
    VMReturn

// _EnterChallenge (after "I will now show you into the Battle Pyramid"): _WalkToPanelAndReceiveBag, HealPlayerParty,
// warp MAP_BATTLE_FRONTIER_BATTLE_PYRAMID_FLOOR (the floor puts the player on its entrance)
L_PYL_Enter:
    h_closemessage
    h_applymovement PY_ATTENDANT, PYL_MvAttendantToPanel
    h_applymovement PY_PLAYER, PYL_MvPlayerToPanel
    h_waitmovement
    WordSetPlayerName 0
    h_msgbox_actor PYL_LOBBY_HOLD_BAG, PY_ATTENDANT
    EmPyr PY_T0, PY_GET, PYF_STREAK
    h_goto_if_eq PY_T0, 0, L_PYL_NewBag
    h_msgbox_actor PYL_LOBBY_TAKE_PREV_BAG, PY_ATTENDANT
    VMJump L_PYL_Exchange
L_PYL_NewBag:
    h_msgbox_actor PYL_LOBBY_TAKE_NEW_BAG, PY_ATTENDANT
L_PYL_Exchange:
    ActorMsg MSGFILE_SCRIPT, PYL_LOBBY_EXCHANGED, PY_ATTENDANT, 0, 0
    SEPlay SEQ_SE_SAVE                  // (Emerald: SE_EXP_MAX)
    SEWait
    LastKeyWait
    h_msgbox_actor PYL_LOBBY_STEP_PANEL, PY_ATTENDANT
    h_closemessage
    h_applymovement PY_ATTENDANT, PYL_MvAttendantAside
    h_waitmovement
    h_applymovement PY_PLAYER, PYL_MvPlayerOnPanel
    h_waitmovement
    fr_set FR_STATUS, PY_ST_IN_CHALLENGE
    h_heal
    EmPyr PY_T0, PY_GET, PYF_FLOOR      // (a resumed challenge may have rested on the top)
    h_goto_if_eq PY_T0, 7, L_PYL_ToTop
    h_warp_arrive PY_FLOOR_ZONE, 1, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_PYL_ToTop:
    h_warp_arrive PY_TOP_ZONE, 17 + PY_TOP_OX, 17 + PY_TOP_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

PYL_Woman:
    h_msgbox_npc PYL_LOBBY_WOMAN
PYL_FatMan:
    h_msgbox_npc PYL_LOBBY_FAT_MAN

// _HintGiver: the fortune of the level chosen (GetBattlePyramidHint: the round = floors cleared / 7, of 20)
PYL_HintGiver:
    h_lock
    h_faceplayer
    h_msgbox PYL_LOBBY_MISFORTUNES
    ListMenu_AnchorTopRight 31, 6, 0, 1, PY_T0
    ListMenuAdd PYL_LOBBY_TB + FRT_MENU_LV50, 65535, 0
    ListMenuAdd PYL_LOBBY_TB + FRT_MENU_OPEN, 65535, 1
    ListMenuShow
    h_goto_if_gt PY_T0, 1, L_PYL_HintEnd
    h_msgbox PYL_LOBBY_AAH
    EmPyr PY_T1, PY_HINT_GIVER, PY_T0
    WorkAdd PY_T1, PYL_LOBBY_HINT_PARALYSIS
    h_msgbox PY_T1
L_PYL_HintEnd:
    h_msgbox PYL_LOBBY_BELIEVE
    h_closemessage
    h_release

// frontier_results FRONTIER_FACILITY_PYRAMID (ShowPyramidResultsWindow): each level's floors cleared (Current while its
// streak goes on, else Prev.) and the record, as messages
PYL_Results:
    ActorsPauseAll
    WordSetPlayerName 0
    h_msgbox_info PYL_LOBBY_RES_TITLE
    fr_get FR_LVL_MODE, PY_T2
    fr_set FR_LVL_MODE, FR_LVL_50
    VMCall Sub_PYL_ResultNumbers
    h_goto_if_eq PY_T0, 0, L_PYL_Prev50
    h_msgbox_info PYL_LOBBY_RES_50_CUR
    VMJump L_PYL_Open
L_PYL_Prev50:
    h_msgbox_info PYL_LOBBY_RES_50_PREV
L_PYL_Open:
    fr_set FR_LVL_MODE, FR_LVL_OPEN
    VMCall Sub_PYL_ResultNumbers
    h_goto_if_eq PY_T0, 0, L_PYL_PrevOpen
    h_msgbox_info PYL_LOBBY_RES_OPEN_CUR
    VMJump L_PYL_ResEnd
L_PYL_PrevOpen:
    h_msgbox_info PYL_LOBBY_RES_OPEN_PREV
L_PYL_ResEnd:
    fr_set FR_LVL_MODE, PY_T2
    h_closemessage
    h_release
Sub_PYL_ResultNumbers:                  // words 1-2: floors cleared, record; PY_T0 = the streak goes on
    EmPyr PY_T1, PY_GET, PYF_STREAK
    WordSetNumber 1, PY_T1, 4
    EmPyr PY_T1, PY_GET, PYF_RECORD
    WordSetNumber 2, PY_T1, 4
    EmPyr PY_T0, PY_STREAK_ACTIVE
    VMReturn

PYL_Rules:                              // _RulesBoard
    ActorsPauseAll
    h_msgbox_info PYL_LOBBY_RULES_LISTED
L_PYL_RulesMenu:                        // _ReadRulesBoard: multichoice MULTI_BATTLE_PYRAMID_RULES
    SystemMsg PYL_LOBBY_READ_WHICH, 2
    ListMenu_AnchorTopRight 31, 4, 0, 1, PY_T0
    ListMenuAdd PYL_LOBBY_M_RULE_MONS, 65535, 0
    ListMenuAdd PYL_LOBBY_M_RULE_TRAINERS, 65535, 1
    ListMenuAdd PYL_LOBBY_M_RULE_MAZE, 65535, 2
    ListMenuAdd PYL_LOBBY_M_RULE_BAG, 65535, 3
    ListMenuAdd PYL_LOBBY_M_EXIT, 65535, 4
    ListMenuShow
    h_goto_if_eq PY_T0, 0, L_PYL_RuleMons
    h_goto_if_eq PY_T0, 1, L_PYL_RuleTrainers
    h_goto_if_eq PY_T0, 2, L_PYL_RuleMaze
    h_goto_if_eq PY_T0, 3, L_PYL_RuleBag
    h_closemessage
    h_release
L_PYL_RuleMons:
    h_msgbox_info PYL_LOBBY_RULE_MONS
    VMJump L_PYL_RulesMenu
L_PYL_RuleTrainers:
    h_msgbox_info PYL_LOBBY_RULE_TRAINERS
    VMJump L_PYL_RulesMenu
L_PYL_RuleMaze:
    h_msgbox_info PYL_LOBBY_RULE_MAZE
    VMJump L_PYL_RulesMenu
L_PYL_RuleBag:
    h_msgbox_info PYL_LOBBY_RULE_BAG
    VMJump L_PYL_RulesMenu

// ON_FRAME VAR_TEMP_CHALLENGE_STATUS: frontier_getstatus -> _QuitWithoutSaving / _ResumeChallenge / _WonChallenge /
// _LostChallenge. frontier_core's fr_lobby_returned says the lines, pays Emerald's BP (+10 after Brandon) and saves;
// the Pyramid's own steps are the hooks (the player's Bag back, the Battle Bag kept or lost, the party's order back).
PYL_State:
    WorkSetConst PY_W_STATE, 1
    fr_lobby_returned FRONTIER_FACILITY_PYRAMID, FRONTIER_MODE_SINGLES, PYL_LOBBY_TB, PY_ATTENDANT, L_PYL_Resume, Sub_PYL_Quit, Sub_PYL_Won, Sub_PYL_Lost
L_PYL_Resume:                           // _ResumeChallenge -> _EnterChallenge: back to where the player rested
    py_party_order 1
    VMJump L_PYL_Enter

Sub_PYL_Quit:                           // _QuitWithoutSaving: the Battle Bag is lost, the streak ends
    EmPyr PY_T1, PY_HELD_TO_BAG
    EmPyr PY_T1, PY_END, 1
    EmPyr PY_T1, PY_SET_STREAK_ACTIVE, 0
    EmPyr PY_T1, PY_UNLOAD
    py_party_order 0
    h_heal
    WordSetPlayerName 0                 // (2026-10-18) "<player> got the Bag back." in the library's didn't-save line
    VMReturn
Sub_PYL_Won:                            // _WonChallenge: the three's held items into the Battle Bag, LoadPlayerParty,
    EmPyr PY_T1, PY_HELD_TO_BAG         // pyramid_clearhelditems, HealPlayerParty, "The Battle Bag you used will be kept"
    EmPyr PY_T1, PY_END, 0
    EmPyr PY_T1, PY_UNLOAD
    py_party_order 0
    h_heal
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, PYL_LOBBY_BAG_KEPT, PY_ATTENDANT, 0, 0
    SEPlay SEQ_SE_SAVE
    SEWait
    LastKeyWait
    VMReturn
Sub_PYL_Lost:                           // _LostChallenge: LoadPlayerParty, pyramid_clearhelditems, HealPlayerParty; the
    EmPyr PY_T1, PY_HELD_TO_BAG         // streak ends and the Battle Bag is lost (InitPyramidBagItems next time)
    EmPyr PY_T1, PY_END, 1
    EmPyr PY_T1, PY_SET_STREAK_ACTIVE, 0
    EmPyr PY_T1, PY_UNLOAD
    py_party_order 0
    h_heal
    WordSetPlayerName 0                 // (2026-10-18) "<player> got the Bag back." in the library's lost line
    VMReturn

    .balign 4, 0
PYL_MvAttendantToPanel:                 // _AttendantWalkToPanel
    walk_up 7
    face_down
    step_end
    .balign 4, 0
PYL_MvPlayerToPanel:
    walk_up 7
    step_end
    .balign 4, 0
PYL_MvAttendantAside:
    walk_right
    face_left
    step_end
    .balign 4, 0
PYL_MvPlayerOnPanel:
    walk_up 2
    step_end
