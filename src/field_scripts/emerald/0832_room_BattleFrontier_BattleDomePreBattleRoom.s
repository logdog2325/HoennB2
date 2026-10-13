// BattleFrontier_BattleDomePreBattleRoom (zone 416; Emerald only): the waiting room between the matches (pokeemerald
// data/maps/BattleFrontier_BattleDomePreBattleRoom/scripts.inc; frontier_factory_dome, 2026-10-12). Reached only by
// script: 1 from the corridor (a new or resumed tournament), 3 back from a won match. Emerald's menu OPPONENT /
// TOURNEY TREE / READY TO START / REST / RETIRE: the opponent's card is one line here (its name and its three
// Pokémon), the tree is Black 2's PWT bracket screen, one half (8 trainers) at a time, the player's half first.
// Room origin (1,0).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_fd_lib.inc"

    ScriptEntry DP_Enter                // 1: OnFrame EnterRoom (VAR_0x8006 0)
    ScriptEntry DP_None                 // 2: the attendant
    ScriptEntry DP_Return               // 3: ReturnFromBattle (VAR_0x8006 1)
    ScriptEntriesEnd

DP_None:
    VMHalt

DP_Enter:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement FD_PLAYER, DP_MvPlayerIn
    h_waitmovement
    VMJump L_DP_Ask

DP_Return:                              // "Thank you for competing! I'll restore your Pokémon" + the round's results
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement FD_PLAYER, DP_MvPlayerIn
    h_waitmovement
    ActorMsg MSGFILE_SCRIPT, FD_DOMEPREBATTLEROOM_RESTORE, 1, 0, 0
    LastKeyWait
    MEPlay MUS_HEAL
    MEWait
    MsgWinCloseAll
    h_heal
    fr_get FR_BATTLE_NUM, FD_T1
    WorkAdd FD_T1, FD_DOMEPREBATTLEROOM_COMPLETE_1 - 1
    fd_say FD_T1, 1
    FrontierCmd FC_D_TREE, 2            // dome_showstatictourneytree (the player's half)

L_DP_Ask:                               // AskReadyForNextRound
    FrontierCmd FC_BRAIN_STATUS, FRONTIER_FACILITY_DOME, 0, FD_T2
    fr_get FR_BATTLE_NUM, FD_T1
    h_goto_if_ne FD_T1, 3, L_DP_AskRound
    FrGet FD_KEY_D_INFO, FD_T3          // Tucker is in this tournament (bit 4) and the final is next
    WorkCmpConst FD_T3, 16
    VMJumpIf CMP_LT, L_DP_AskRound
    h_goto_if_eq FD_T2, 2, L_DP_AskTuckerGold
    h_goto_if_eq FD_T2, 4, L_DP_AskTuckerGold
    ActorMsg MSGFILE_SCRIPT, FD_DOMEPREBATTLEROOM_TUCKER_SILVER, 1, 0, 0
    VMJump L_DP_Menu
L_DP_AskTuckerGold:
    ActorMsg MSGFILE_SCRIPT, FD_DOMEPREBATTLEROOM_TUCKER_GOLD, 1, 0, 0
    VMJump L_DP_Menu
L_DP_AskRound:
    WorkAdd FD_T1, FD_DOMEPREBATTLEROOM_READY_0
    ActorMsg MSGFILE_SCRIPT, FD_T1, 1, 0, 0
L_DP_Menu:                              // (row 6: below the speech balloon, as fd_menu3; at row 0 the list's frame
    ListMenu_AnchorTopRight 31, 6, 0, 1, FD_T0  // stayed on screen under the next balloon)
    ListMenuAdd FD_DOMEPREBATTLEROOM_MENU_OPPONENT, 65535, 0
    ListMenuAdd FD_DOMEPREBATTLEROOM_MENU_TREE, 65535, 1
    ListMenuAdd FD_DOMEPREBATTLEROOM_MENU_READY, 65535, 2
    ListMenuAdd FD_DOMEPREBATTLEROOM_MENU_REST, 65535, 3
    ListMenuAdd FD_DOMEPREBATTLEROOM_MENU_RETIRE, 65535, 4
    ListMenuShow
    MsgWinCloseAll
    h_goto_if_eq FD_T0, 0, L_DP_Opponent
    h_goto_if_eq FD_T0, 1, L_DP_Tree
    h_goto_if_eq FD_T0, 2, L_DP_Ready
    h_goto_if_eq FD_T0, 3, L_DP_Rest
    h_goto_if_eq FD_T0, 4, L_DP_Retire
    VMJump L_DP_Ask

L_DP_Opponent:                          // ShowOpponentInfo: Emerald's card as a line (the trainer's three Pokémon)
    h_buffer_player
    FrontierCmd FC_D_OPP_NAME, 1, 0, FD_T1
    fd_say FD_DOMEPREBATTLEROOM_NEXT_OPPONENT, 1
    FrontierCmd FC_D_OPP_SPECIES, 0, 0, FD_T1
    WordSetPokeSpecies 2, FD_T1
    FrontierCmd FC_D_OPP_SPECIES, 1, 0, FD_T1
    WordSetPokeSpecies 3, FD_T1
    FrontierCmd FC_D_OPP_SPECIES, 2, 0, FD_T1
    WordSetPokeSpecies 4, FD_T1
    FrontierCmd FC_D_OPP_NAME, 1, 0, FD_T1
    fd_say FD_DOMEPREBATTLEROOM_OPP_MONS, 1
    VMJump L_DP_Ask

L_DP_Tree:                              // ShowTourneyTree: the round, then both halves
    fr_get FR_BATTLE_NUM, FD_T1
    WorkAdd FD_T1, FD_DOMEPREBATTLEROOM_IN_ROUND_0
    fd_say FD_T1, 1
    FrontierCmd FC_D_TREE, 2
    FrontierCmd FC_D_TREE, 3
    VMJump L_DP_Ask

L_DP_Ready:                             // ContinueChallenge: pick two of the three (ChoosePartyForBattleFrontier)
    fd_say FD_DOMEPREBATTLEROOM_CHOOSE_TWO, 1
    FrontierCmd FC_D_PICK2, 0, 0, FR_PICK
    h_goto_if_ne FR_PICK, 1, L_DP_Ask
    FrontierCmd FC_D_SET_PICKS, FR_PICK + 1, FR_PICK + 2
    FrontierCmd FC_D_OPPONENT, 0, 0, FD_T1  // dome_setopponent (+ the two it sends: GetDomeTrainerSelectedMons)
    fd_say FD_DOMEPREBATTLEROOM_THIS_WAY, 1
    h_applymovement 1, DP_MvAttendantAside
    h_waitmovement
    h_applymovement FD_PLAYER, DP_MvPlayerToDoor
    h_waitmovement
    bt_door_open 6, 1                   // opendoor 5, 1
    h_applymovement FD_PLAYER, DP_MvPlayerIn2
    h_waitmovement
    fd_to_room FD_D_ROOM, 5, 8, 0, 1, 1 // warp MAP_BATTLE_FRONTIER_BATTLE_DOME_BATTLE_ROOM (the player's walk-in spot)

L_DP_Rest:                              // AskPauseChallenge
    h_yesno_actor FD_DOMEPREBATTLEROOM_SAVE_QUIT, 1, FD_T1
    MsgWinCloseAll
    h_goto_if_no FD_T1, L_DP_Ask
    fd_rest_and_quit FD_D_LOBBY, 6, 9, 18, 9, FD_DOMEPREBATTLEROOM_SAVING, 1
L_DP_Retire:                            // AskRetireChallenge -> dome_resolvewinners DOME_PLAYER_RETIRED, lost
    h_yesno_actor FD_DOMEPREBATTLEROOM_RETIRE, 1, FD_T1
    MsgWinCloseAll
    h_goto_if_no FD_T1, L_DP_Ask
    FrontierCmd FC_D_RESULT, 0
    fd_status FR_ST_LOST
    fd_to_lobby_m FD_D_LOBBY, 6, 9, 18, 9

    .balign 4, 0
DP_MvPlayerIn:                          // Movement_PlayerEnter
    walk_up 4
    step_end
DP_MvAttendantAside:                    // Movement_AttendantMoveAside
    walk_right
    face_left
    step_end
DP_MvPlayerToDoor:                      // Movement_PlayerWalkToDoor
    walk_up
    step_end
DP_MvPlayerIn2:                         // Movement_PlayerEnterDoor
    walk_up
    step_end
