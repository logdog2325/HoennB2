// BattleFrontier_Lounge3 (zone 477; header scripts 954 -> own file 2090), Pokémon Emerald NDS only (frontier_lounges,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_Lounge3/scripts.inc: the Gambler and his group. With at least three
// Silver Symbols he asks you to take the day's challenge (VAR_FRONTIER_GAMBLER_CHALLENGE, 12 of them; it moves on each
// day, hoenn_frontier.inc fr_lounge_new_day) for him and to spot him 5, 10 or 15 BP (Black 2's BP purse, the BP window).
// The bet is settled where Emerald settles it (GetChallengeStatus -> FrontierGamblerSetWonOrLost): when a lobby sees that
// challenge end (hoenn_frontier.inc fr_gambler_settle, in fr_lobby_returned and the Battle Tower lobby). Won: twice the
// stake back. VAR_FRONTIER_GAMBLER_CODE = the challenge as FR_FACILITY | FR_BATTLE_MODE << 3 (sFrontierChallenges); this
// port's Battle Tower has single battles only, so a bet on its double or multi rooms is settled by its single battles.
// The room: data/interior_layouts/BattleFrontier_Lounge3.json, people data/interiors/emerald/477.json (uid = script =
// Emerald's local id). Messages: src/text/script/emerald/0608_room_BattleFrontier_Lounge3.txt (lounge_rooms.py): 0-16
// the lines, 17-20 the bet menu, 21-32 "what I'm looking for" per challenge, 33-44 "get to ... pronto!" per challenge.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"

#define T_Busy 0
#define T_Explain 1
#define T_HowAbout 2
#define T_Spot 3
#define T_HowMuch 4
#define T_NotEnough 5
#define T_Thanks 6
#define T_NiceTry 7
#define T_Champ 8
#define T_Obtained 9                    // {player} obtained {N} Battle Points.
#define T_ThinkOfMe 10
#define T_NotInterested 11
#define T_Oh 12
#define T_Menu 17                       // 5 BP, 10 BP, 15 BP, EXIT
#define T_Look 21
#define T_Go 33
#define GB_STATE VAR_FRONTIER_GAMBLER_STATE     // FRONTIER_GAMBLER_WAITING 0, PLACED_BET 1, WON 2, LOST 3
#define GB_V 0x8020
#define GB_N 0x8021
#define GB_A 0x8022                     // the stake (VAR_0x8008)
#define GB_B 0x8023
#define GB_GAMBLER 1

    .macro gb_code c, fac, mode         // Sub_GB_Code's case c
L_GB_Code\c:
    WorkSetConst VAR_FRONTIER_GAMBLER_CODE, (\fac)|((\mode)<<3)
    VMReturn
    .endm

    ScriptEntry GB_Gambler              // 1: BattleFrontier_Lounge3_EventScript_Gambler (HIKER (4,6), facing up)
    ScriptEntry GB_FatMan               // 2: _FatMan (facing down)
    ScriptEntry GB_Woman                // 3: _Woman (facing right)
    ScriptEntry GB_PokefanF             // 4: _PokefanF (facing left)
    ScriptEntry GB_Man                  // 5: _Man
    ScriptEntriesEnd

GB_Gambler:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    fr_lounge_new_day
    h_goto_if_set FLAG_MET_BATTLE_FRONTIER_GAMBLER, L_GB_Met
    WorkSetConst GB_N, 0                // CountSilverSymbols (a Gold Symbol's facility has its Silver too)
    .irp f, 0,1,2,3,4,5,6
    FrGet FR_GET_SYMBOL|\f,GB_V
    WorkCmpConst GB_V, 0
    VMJumpIf CMP_EQ, L_GB_Count\f
    WorkAdd GB_N, 1
L_GB_Count\f:
    .endr
    h_goto_if_le GB_N, 2, L_GB_NotEnoughSymbols
    h_setflag FLAG_MET_BATTLE_FRONTIER_GAMBLER
    h_msgbox T_Explain
L_GB_Ask:                               // AskToEnterChallenge: ShowFrontierGamblerLookingMessage
    WorkSet VAR_FRONTIER_GAMBLER_SET_CHALLENGE, VAR_FRONTIER_GAMBLER_CHALLENGE
    VMCall Sub_GB_Look
    h_yesno T_HowAbout, GB_V
    h_goto_if_no GB_V, L_GB_Decline
    h_yesno T_Spot, GB_V
    h_goto_if_no GB_V, L_GB_Decline
    fr_bp_window                        // ShowBattlePointsWindow
L_GB_Menu:                              // ChooseBetAmount (MULTI_FRONTIER_GAMBLER_BET)
    ParentActorMsg MSGFILE_SCRIPT, T_HowMuch, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, GB_V
    ListMenuAdd T_Menu+0, 65535, 0
    ListMenuAdd T_Menu+1, 65535, 1
    ListMenuAdd T_Menu+2, 65535, 2
    ListMenuAdd T_Menu+3, 65535, 3
    ListMenuShow
    WorkCmpConst GB_V, 2
    VMJumpIf CMP_GT, L_GB_CancelBet     // EXIT or B
    WorkSet VAR_FRONTIER_GAMBLER_AMOUNT_BET, GB_V
    WorkSet GB_A, GB_V                  // BET_AMOUNT_5 / 10 / 15
    WorkAdd GB_A, 1
    WorkMul GB_A, 5
    fr_bp GB_B                          // GetFrontierBattlePoints
    WorkCmpWork GB_B, GB_A
    VMJumpIf CMP_GE, L_GB_Place
    h_msgbox T_NotEnough
    VMJump L_GB_Menu
L_GB_Place:                             // PlaceBet
    fr_take_bp GB_A, GB_V
    h_setvar GB_STATE, 1
    VMCall Sub_GB_Code
    fr_bp_window                        // UpdateBattlePointsWindow
    SEPlay SE_SHOP
    h_msgbox T_Thanks
    VMCall Sub_GB_Go                    // FinishBet: ShowFrontierGamblerGoMessage
    MoneyWinClose                       // CloseBattlePointsWindow
    h_release
L_GB_CancelBet:
    MoneyWinClose
L_GB_Decline:
    h_msgbox T_NotInterested
    h_release

L_GB_NotEnoughSymbols:
    h_msgbox T_Busy
    h_closemessage
    h_turnobject GB_GAMBLER, 0          // FaceOriginalDirection (up)
    h_release

L_GB_Met:                               // AlreadyMetGambler
    h_msgbox T_Oh
    h_goto_if_ge GB_STATE, 1, L_GB_Check
    VMJump L_GB_Ask
L_GB_Check:                             // CheckBetResults
    h_goto_if_eq GB_STATE, 1, L_GB_NotAttempted
    h_goto_if_eq GB_STATE, 2, L_GB_Won
    h_msgbox T_NiceTry                  // LostChallenge
    h_setvar GB_STATE, 0
    h_release
L_GB_Won:                               // WonChallenge: the stake twice (RewardBet5 / 10 / 15)
    h_msgbox T_Champ
    WorkSet GB_A, VAR_FRONTIER_GAMBLER_AMOUNT_BET
    WorkAdd GB_A, 1
    WorkMul GB_A, 10
    h_buffer_player
    WordSetNumber 1, GB_A, 2
    MEPlay FR_ME_OBTAIN_BP              // MSGBOX_GETPOINTS
    h_msgbox T_Obtained
    MEWait
    fr_add_bp GB_A                      // GiveFrontierBattlePoints
    h_msgbox T_ThinkOfMe
    h_setvar GB_STATE, 0
    h_release
L_GB_NotAttempted:                      // ChallengeNotAttempted
    VMCall Sub_GB_Go
    h_release

Sub_GB_Look:                            // sFrontierGamblerLookingMessages[VAR_FRONTIER_GAMBLER_SET_CHALLENGE]
    .irp c, 1,2,3,4,5,6,7,8,9,10,11
    WorkCmpConst VAR_FRONTIER_GAMBLER_SET_CHALLENGE, \c
    VMJumpIf CMP_EQ, L_GB_Look\c
    .endr
    h_msgbox T_Look+0
    VMReturn
    .irp c, 1,2,3,4,5,6,7,8,9,10,11
L_GB_Look\c:
    h_msgbox T_Look+\c
    VMReturn
    .endr

Sub_GB_Go:                              // sFrontierGamblerGoMessages[VAR_FRONTIER_GAMBLER_SET_CHALLENGE]
    .irp c, 1,2,3,4,5,6,7,8,9,10,11
    WorkCmpConst VAR_FRONTIER_GAMBLER_SET_CHALLENGE, \c
    VMJumpIf CMP_EQ, L_GB_Go\c
    .endr
    h_msgbox T_Go+0
    VMReturn
    .irp c, 1,2,3,4,5,6,7,8,9,10,11
L_GB_Go\c:
    h_msgbox T_Go+\c
    VMReturn
    .endr

// sFrontierChallenges[challenge] as FR_FACILITY | FR_BATTLE_MODE << 3: Tower singles / doubles / multis (all three the
// tower's single battles here), Dome singles / doubles, Factory singles / doubles, Palace singles / doubles, Arena, Pike,
// Pyramid
Sub_GB_Code:
    .irp c, 1,2,3,4,5,6,7,8,9,10,11
    WorkCmpConst VAR_FRONTIER_GAMBLER_SET_CHALLENGE, \c
    VMJumpIf CMP_EQ, L_GB_Code\c
    .endr
    WorkSetConst VAR_FRONTIER_GAMBLER_CODE, FRONTIER_FACILITY_TOWER
    VMReturn
    gb_code 1, FRONTIER_FACILITY_TOWER, FRONTIER_MODE_SINGLES
    gb_code 2, FRONTIER_FACILITY_TOWER, FRONTIER_MODE_SINGLES
    gb_code 3, FRONTIER_FACILITY_DOME, FRONTIER_MODE_SINGLES
    gb_code 4, FRONTIER_FACILITY_DOME, FRONTIER_MODE_DOUBLES
    gb_code 5, FRONTIER_FACILITY_FACTORY, FRONTIER_MODE_SINGLES
    gb_code 6, FRONTIER_FACILITY_FACTORY, FRONTIER_MODE_DOUBLES
    gb_code 7, FRONTIER_FACILITY_PALACE, FRONTIER_MODE_SINGLES
    gb_code 8, FRONTIER_FACILITY_PALACE, FRONTIER_MODE_DOUBLES
    gb_code 9, FRONTIER_FACILITY_ARENA, FRONTIER_MODE_SINGLES
    gb_code 10, FRONTIER_FACILITY_PIKE, FRONTIER_MODE_SINGLES
    gb_code 11, FRONTIER_FACILITY_PYRAMID, FRONTIER_MODE_SINGLES

GB_FatMan:                              // lock, faceplayer, msgbox, FaceOriginalDirection
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 14
    h_closemessage
    h_turnobject 2, 1
    h_release

GB_Woman:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 13
    h_closemessage
    h_turnobject 3, 3
    h_release

GB_PokefanF:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 15
    h_closemessage
    h_turnobject 4, 2
    h_release

GB_Man:
    h_msgbox_npc 16

    .balign 4, 0
