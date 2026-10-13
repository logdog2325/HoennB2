// BattleFrontier_BattlePalaceBattleRoom (zone 468; Emerald only): the Battle Hall (pokeemerald
// data/maps/BattleFrontier_BattlePalaceBattleRoom/scripts.inc; frontier_palace_arena, 2026-10-12). Reached only by
// script 1 from the corridor. The battle is Black 2's Battle Subway battle with the Palace's rules
// (b2tools/patches/frontier_palace_arena.c: the Pokémon choose their moves by Nature). Room origin (1,0). Emerald keeps
// the camera still with a stand-in player object; here the player walks in from the stand-in's spot (1,9) (the camera
// follows). Spenser walks in with his Dusclops and Azurill (objects 4, 5).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pa_lib.inc"

#define PB_OPP 2                        // the opponent (Emerald LOCALID_PALACE_BATTLE_OPPONENT)
#define PB_ATT 3                        // the attendant
#define PB_DUSCLOPS 4
#define PB_AZURILL 5

    ScriptEntry PB_Enter                // 1: OnFrame EnterRoom
    ScriptEntry PB_None                 // 2: the opponent, the attendant, Spenser's Pokémon
    ScriptEntriesEnd

PB_None:
    VMHalt

PB_Enter:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement PA_PLAYER, PB_MvPlayerIn
    h_waitmovement
    fr_get FR_BATTLE_NUM, FD_T1
    h_goto_if_eq FD_T1, 0, L_PB_Next
    h_applymovement PA_PLAYER, PB_MvFaceUp      // PlayerReturnToChallenge (a resumed challenge)
    h_applymovement PB_ATT, PB_MvFaceDown
    h_waitmovement
    VMJump L_PB_Ask

L_PB_Next:                              // NextOpponentEnter: tower_setopponent, the walk in, palace_getopponentintro
    FrontierPA PA_NEXT_OPPONENT, FRONTIER_FACILITY_PALACE, 0, FD_T1
    WorkSet PA_OPP_GFX, FD_T1
    h_addobject PB_OPP, PA_FLAG_OPP
    h_applymovement PB_OPP, PB_MvOpponentIn
    h_waitmovement
    FrontierPA PA_GREETING, FRONTIER_FACILITY_PALACE, 0, FD_T1
    fd_say FD_T1, PB_OPP
    VMCall Sub_PB_Battle
    h_goto_if_eq FD_T1, 1, L_PB_Won
L_PB_Lost:                              // WarpToLobbyLost (in front of the attendant of the challenge's mode)
    fd_status FR_ST_LOST
L_PB_ToLobby:
    FrGet FR_BATTLE_MODE, FR_T0
    h_goto_if_eq FR_T0, FRONTIER_MODE_DOUBLES, L_PB_ToLobbyD
    pa_to_lobby PA_P_LOBBY, 6, 5        // warp MAP_BATTLE_FRONTIER_BATTLE_PALACE_LOBBY, 5, 7
L_PB_ToLobbyD:
    pa_to_lobby PA_P_LOBBY, 20, 5       // ... 19, 7

L_PB_Won:                               // DefeatedOpponent: the streak, the battle number
    pa_streak_win FRONTIER_FACILITY_PALACE
    WorkSetConst FD_T1, 1
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    h_goto_if_ge FD_T1, 7, L_PB_Seven
    h_applymovement PB_OPP, PB_MvOpponentOut
    h_waitmovement
    h_removeobject PB_OPP, PA_FLAG_OPP
    h_applymovement PA_PLAYER, PB_MvFaceUp
    h_applymovement PB_ATT, PB_MvFaceDown
    h_waitmovement
    ActorMsg MSGFILE_SCRIPT, PA_PALACEBATTLEROOM_RESTORE, PB_ATT, 0, 0
    LastKeyWait
    MEPlay MUS_HEAL
    MEWait
    MsgWinCloseAll
    h_heal
L_PB_Ask:                               // AskReadyForOpponent
    FrontierPA PA_BRAIN_STATUS, FRONTIER_FACILITY_PALACE, 0, FD_T3
    h_goto_if_ne FD_T3, 0, L_PB_MavenNext
    fr_get FR_BATTLE_NUM, FD_T1
    WorkAdd FD_T1, PA_PALACEBATTLEROOM_READY_2 - 1
    ActorMsg MSGFILE_SCRIPT, FD_T1, PB_ATT, 0, 0
L_PB_Menu:
    fd_menu3 FD_T2, PA_PALACEBATTLEROOM_MENU_GO_ON, PA_PALACEBATTLEROOM_MENU_REST, PA_PALACEBATTLEROOM_MENU_RETIRE
    MsgWinCloseAll
    h_goto_if_eq FD_T2, 0, L_PB_GoOn
    h_goto_if_eq FD_T2, 1, L_PB_Rest
    h_goto_if_eq FD_T2, 2, L_PB_Retire
    VMJump L_PB_Ask
L_PB_GoOn:                              // ContinueChallenge
    h_applymovement PA_PLAYER, PB_MvFaceRight
    h_applymovement PB_ATT, PB_MvFaceRight
    h_waitmovement
    h_goto_if_ne FD_T3, 0, L_PB_Spenser
    VMJump L_PB_Next
L_PB_Rest:                              // AskPauseChallenge -> PauseChallenge (save, then the soft reset)
    h_yesno_actor PA_PALACEBATTLEROOM_SAVE_QUIT, PB_ATT, FD_T1
    h_goto_if_no FD_T1, L_PB_Ask
    FlagSet PA_FLAG_OPP
    FrGet FR_BATTLE_MODE, FR_T0
    h_goto_if_eq FR_T0, FRONTIER_MODE_DOUBLES, L_PB_RestD
    fr_rest_and_quit PA_P_LOBBY, 6, 5, 0, PA_PALACEBATTLEROOM_SAVING, PB_ATT
L_PB_RestD:
    fr_rest_and_quit PA_P_LOBBY, 20, 5, 0, PA_PALACEBATTLEROOM_SAVING, PB_ATT
L_PB_Retire:                            // AskRetireChallenge
    h_yesno_actor PA_PALACEBATTLEROOM_RETIRE, PB_ATT, FD_T1
    h_goto_if_no FD_T1, L_PB_Ask
    VMJump L_PB_Lost
L_PB_Seven:                             // WarpToLobbyWon
    fd_status FR_ST_WON
    VMJump L_PB_ToLobby

L_PB_MavenNext:                         // MavenUpNext: "challenging the Palace Maven", then ready?
    h_msgbox_actor PA_PALACEBATTLEROOM_MAVEN_NEXT, PB_ATT
    ActorMsg MSGFILE_SCRIPT, PA_PALACEBATTLEROOM_MAVEN_READY, PB_ATT, 0, 0
    VMJump L_PB_Menu

L_PB_Spenser:                           // BattleSpenser
    FrontierPA PA_NEXT_OPPONENT, FRONTIER_FACILITY_PALACE, 0, FD_T1    // (the Brain: Spenser's walking sprite)
    WorkSet PA_OPP_GFX, FD_T1
    h_msgbox_actor PA_PALACEBATTLEROOM_MAVEN_ARRIVES, PB_ATT
    MsgWinCloseAll
    h_addobject PB_DUSCLOPS, PA_FLAG_OPP
    h_addobject PB_AZURILL, PA_FLAG_OPP
    h_addobject PB_OPP, PA_FLAG_OPP
    h_applymovement PB_DUSCLOPS, PB_MvDusclopsIn
    h_applymovement PB_AZURILL, PB_MvAzurillIn
    h_applymovement PB_OPP, PB_MvSpenserIn
    h_waitmovement
    h_goto_if_eq FD_T3, 2, L_PB_IntroGold
    h_goto_if_eq FD_T3, 3, L_PB_Silver
    h_goto_if_eq FD_T3, 4, L_PB_Gold
    FrontierPA PA_HEARD, FRONTIER_FACILITY_PALACE, 1, FD_T1
    h_goto_if_ne FD_T1, 0, L_PB_Silver
    fd_say PA_PALACEBATTLEROOM_SPENSER_INTRO, PB_OPP
L_PB_Silver:
    fd_say PA_PALACEBATTLEROOM_SPENSER_PROVE, PB_OPP
    VMCall Sub_PB_BrainBattle
    fr_symbol_get FRONTIER_FACILITY_PALACE, FD_T2
    h_goto_if_ne FD_T2, 0, L_PB_BrainDone
    fd_say PA_PALACEBATTLEROOM_SPENSER_POST_SILVER, PB_OPP
    h_applymovement PA_PLAYER, PB_MvFaceUp
    h_applymovement PB_ATT, PB_MvFaceDown
    h_waitmovement
    h_msgbox_actor PA_PALACEBATTLEROOM_PASS, PB_ATT
    MEPlay FR_ME_OBTAIN_SYMBOL
    h_buffer_player
    h_msgbox_info PA_PALACEBATTLEROOM_GOT_SILVER
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_PALACE, 0
    h_applymovement PA_PLAYER, PB_MvFaceRight
    h_applymovement PB_ATT, PB_MvFaceRight
    h_waitmovement
    fd_say PA_PALACEBATTLEROOM_SPENSER_NEXT, PB_OPP
    VMJump L_PB_BrainDone
L_PB_IntroGold:
    FrontierPA PA_HEARD, FRONTIER_FACILITY_PALACE, 1, FD_T1
    h_goto_if_ne FD_T1, 0, L_PB_Gold
    fd_say PA_PALACEBATTLEROOM_SPENSER_GOLD_INTRO, PB_OPP
L_PB_Gold:
    fd_say PA_PALACEBATTLEROOM_SPENSER_KAAAH, PB_OPP
    VMCall Sub_PB_BrainBattle
    fr_symbol_get FRONTIER_FACILITY_PALACE, FD_T2
    h_goto_if_eq FD_T2, 2, L_PB_BrainDone
    fd_say PA_PALACEBATTLEROOM_SPENSER_POST_GOLD, PB_OPP
    h_applymovement PA_PLAYER, PB_MvFaceUp
    h_applymovement PB_ATT, PB_MvFaceDown
    h_waitmovement
    h_msgbox_actor PA_PALACEBATTLEROOM_PASS2, PB_ATT
    MEPlay FR_ME_OBTAIN_SYMBOL
    h_buffer_player
    h_msgbox_info PA_PALACEBATTLEROOM_GOT_GOLD
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_PALACE, 1
    h_applymovement PA_PLAYER, PB_MvFaceRight
    h_applymovement PB_ATT, PB_MvFaceRight
    h_waitmovement
    fd_say PA_PALACEBATTLEROOM_SPENSER_LAST, PB_OPP
L_PB_BrainDone:                         // DefeatedSpenser: palace_incrementstreak, then the lobby (won, the Brain line)
    fr_set FR_BRAIN_BEATEN, 1
    fr_streak_win FRONTIER_FACILITY_PALACE, FRONTIER_MODE_SINGLES    // (Spenser: singles only)
    WorkSetConst FD_T1, 1
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    VMJump L_PB_Seven

Sub_PB_Battle:                          // DoPalaceBattle: healed, the battle; FD_T1 = 1 won
    h_heal
    FrontierPA PA_BATTLE, FRONTIER_FACILITY_PALACE, 0, FD_T1
    h_heal
    VMReturn
Sub_PB_BrainBattle:                     // (lost: back to the lobby)
    VMCall Sub_PB_Battle
    h_goto_if_ne FD_T1, 1, L_PB_Lost
    VMReturn

    .balign 4, 0
PB_MvPlayerIn:                          // Movement_PlayerEnterRoom (from the stand-in's spot)
    walk_up 4
    face_right
    step_end
PB_MvFaceUp:
    face_up
    step_end
PB_MvFaceDown:
    face_down
    step_end
PB_MvFaceRight:
    face_right
    step_end
PB_MvOpponentIn:                        // Movement_OpponentEnter
    walk_down 4
    face_left
    step_end
PB_MvOpponentOut:                       // Movement_OpponentExit
    walk_up 4
    step_end
PB_MvDusclopsIn:                        // Movement_DusclopsEnter
    delay_16 2
    walk_down
    walk_right
    walk_down
    walk_in_place_fastest_left
    step_end
PB_MvAzurillIn:                         // Movement_AzurillEnter
    walk_fast_down
    walk_fast_right
    walk_fast_down 5
    walk_in_place_fastest_left
    delay_16
    step_end
PB_MvSpenserIn:                         // Movement_SpenserEnter
    delay_16 7
    walk_slow_down 4
    face_left
    step_end
