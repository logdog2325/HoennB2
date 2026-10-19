// The three Battle Tents (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md): the nine rooms' shared defines and macros.
// Pokémon Emerald NDS only. Include after hoenn_story.inc, hoenn_emerald.inc, hoenn_frontier.inc.
// pokeemerald src/battle_tent.c and data/maps/{Verdanturf,Fallarbor}Town_BattleTent*, SlateportCity_BattleTent*: three
// battles against the tent's own trainers (at the level of the player's highest of the three, at least 30), then the
// tent's prize. Verdanturf = the Battle Palace's rules (frontier_palace_arena.c, tent mode), Fallarbor = the Battle
// Arena's, Slateport = the Battle Factory's rentals (frontier_factory_dome.c, tent mode).
// Zone tile = Emerald tile + the room's origin (work/agents/battle_tents/tools/rooms_tents.py).
#ifndef BATTLE_TENTS_LIB_INC
#define BATTLE_TENTS_LIB_INC
#include "battle_tents_lines.h"
#include "scenes/frontier_pa_lib.inc"          // FrontierPA, PA_*, pa_to_lobby; with frontier_fd_lib.inc: FrontierCmd,
                                               // fd_say, fd_menu3, fd_to_room, fd_player_visible, FD_T0-3, bt_door_*

// ---- zones (data/emerald/hoenn_interiors.json, claimed by battle_tents) and the rooms' origins -------------------
#define TT_V_LOBBY 519
#define TT_F_LOBBY 520
#define TT_S_LOBBY 521
#define TT_V_CORR 522
#define TT_F_CORR 523
#define TT_S_CORR 524
#define TT_V_ROOM 525
#define TT_F_ROOM 526
#define TT_S_ROOM 527
#define TT_LOBBY_OX 1                          // the three lobbies (LAYOUT_BATTLE_TENT_LOBBY)
#define TT_LOBBY_OZ 0
#define TT_CORR_OX 1                           // the three corridors (LAYOUT_BATTLE_TENT_CORRIDOR)
#define TT_CORR_OZ 0
#define TT_V_ROOM_OX 1                         // Verdanturf's battle room
#define TT_V_ROOM_OZ 0
#define TT_ROOM_OX 1                           // Fallarbor's and Slateport's (LAYOUT_BATTLE_TENT_BATTLE_ROOM)
#define TT_ROOM_OZ 0
#define TT_LX(x) ((x) + TT_LOBBY_OX)
#define TT_LZ(z) ((z) + TT_LOBBY_OZ)
#define TT_CX(x) ((x) + TT_CORR_OX)
#define TT_CZ(z) ((z) + TT_CORR_OZ)
#define TT_VRX(x) ((x) + TT_V_ROOM_OX)
#define TT_VRZ(z) ((z) + TT_V_ROOM_OZ)
#define TT_RX(x) ((x) + TT_ROOM_OX)
#define TT_RZ(z) ((z) + TT_ROOM_OZ)

// ---- FR_FACILITY of a tent challenge (Emerald keeps VAR_FRONTIER_FACILITY = the Frontier facility whose rules the tent
// uses; here the tents have numbers of their own so no Frontier lobby takes a tent challenge for its own)
#define TENT_FAC_VERDANTURF 8
#define TENT_FAC_FALLARBOR 9
#define TENT_FAC_SLATEPORT 10
// the engines' facility arguments: FrontierPA (frontier_palace_arena.c FAC_TENT | the rules) and FrontierCmd
#define TT_PA_VERDANTURF (FRONTIER_FACILITY_PALACE | 0x10)
#define TT_PA_FALLARBOR (FRONTIER_FACILITY_ARENA | 0x10)
#define TT_FC_SLATEPORT 0x14                   // frontier_factory_dome.c FAC_TENT_SLATEPORT
#define TC_T_INIT 60                           // FrontierCmd: the Slateport tent (frontier_factory_dome.c)
#define TC_T_GEN_RENTALS 61
#define TC_T_RENT 62
#define TC_T_GEN_OPPONENT 63
#define TC_T_SWAP 64
#define TC_T_KEEP_OPPONENT 65

// ---- record key 15 (battle_tents, notes/FRONTIER.md 6): bit 0/1/2 the Verdanturf/Fallarbor/Slateport prize waiting
// (Emerald's verdanturfTentPrize...: each tent's prize list has one item), bit 8/9 Scott met in the Verdanturf/Fallarbor
// tent (Emerald's FLAG_MET_SCOTT_IN_VERDANTURF / _FALLARBOR)
#define TENT_KEY 15
#define TENT_PRIZE_BIT(fac) (1 << ((fac) - TENT_FAC_VERDANTURF))
#define TENT_SCOTT_V 0x100
#define TENT_SCOTT_F 0x200
#define TT_STATE 0x4000                        // map-local: the lobby's "returned" check ran (0 after each zone init)
#define TT_FLAG_SCOTT 16                       // map-local flag 0x10: Scott hidden (the lobby's zone init sets it)
#define TT_PLAYER 255

// ---- the tent lobby block: the first lines of every lobby's text (b2tools/battle_tents_text.py LOBBY_ROLES)
#define TT_WELCOME 0
#define TT_TAKE 1
#define TT_EXPLAIN 2
#define TT_NOT_ENOUGH 3
#define TT_CHOOSE 4
#define TT_SAVE_BEFORE 5
#define TT_STEP 6
#define TT_GOODBYE 7
#define TT_DIDNT_SAVE 8
#define TT_WON 9
#define TT_WON_SAVE 10
#define TT_PRIZE 11
#define TT_RECEIVED 12
#define TT_NO_ROOM 13
#define TT_LOST 14
#define TT_RESUME 15
#define TT_RESUME_SAVE 16
#define TT_GOODBYE2 17
#define TT_MENU_CHALLENGE 18
#define TT_MENU_INFO 19
#define TT_MENU_EXIT 20

// key 15's bits
    .macro tt_key_test mask, var        // var = key 15 & mask
    FrGet TENT_KEY, \var
    WorkAnd \var, \mask
    .endm
    .macro tt_key_set mask
    FrGet TENT_KEY, FR_T3
    WorkOr FR_T3, \mask
    FrOp FR_OP_SET | TENT_KEY, FR_T3
    .endm
    .macro tt_key_clear mask
    FrGet TENT_KEY, FR_T3
    WorkAnd FR_T3, 0xFFFF ^ (\mask)
    FrOp FR_OP_SET | TENT_KEY, FR_T3
    .endm

// The tent's attendant (pokeemerald <Tent>_BattleTentLobby_EventScript_Attendant): a prize still waiting is given first;
// welcome; CHALLENGE / INFO / EXIT; the eligibility check and the pick of three (pick = 3: Verdanturf, Fallarbor:
// Emerald's ChoosePartyForBattleFrontier at Open Level, no level limit; pick = 0: Slateport's rentals come in the next
// room); "save before?" YES/NO; the save; "now follow me"; then `enter` (the walk through the door). `init` (a label,
// VMCall'ed just before the save) starts the challenge's engine state; `prize` = the zone's prize-giving code (it shows
// TT_WON first).
    .macro tent_attendant fac, enter, init, prize, pick=3
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    tt_key_test TENT_PRIZE_BIT(\fac), FR_T0
    WorkCmpConst FR_T0, 0
    VMJumpIf CMP_NE, .Ltta_prize\@
    h_msgbox TT_WELCOME
.Ltta_ask\@:
    ParentActorMsg MSGFILE_SCRIPT, TT_TAKE, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, FR_T0
    ListMenuAdd TT_MENU_CHALLENGE, 65535, 0
    ListMenuAdd TT_MENU_INFO, 65535, 1
    ListMenuAdd TT_MENU_EXIT, 65535, 2
    ListMenuShow
    WorkCmpConst FR_T0, 0
    VMJumpIf CMP_EQ, .Ltta_try\@
    WorkCmpConst FR_T0, 1
    VMJumpIf CMP_NE, .Ltta_cancel\@
    h_msgbox TT_EXPLAIN
    VMJump .Ltta_ask\@
.Ltta_try\@:
    .if \pick
    WorkSetConst FR_T2, FR_LVL_OPEN     // (Emerald: VAR_RESULT 2 = the tent: no level limit, as Open Level)
    fr_check_party FR_T2, FR_T1
    WorkCmpConst FR_T1, \pick
    VMJumpIf CMP_LT, .Ltta_ineligible\@
    h_msgbox TT_CHOOSE
    h_closemessage
    WorkSetConst FR_PICK, 0x20 | (\pick)  // emerald_mech's EmPickParty: the Frontier's rules, no level limit
    EmPickParty FR_PICK
    WorkCmpConst FR_PICK, \pick
    VMJumpIf CMP_NE, .Ltta_cancel\@
    FrOp FR_OP_SAVE_PICKS, FR_PICK
    .endif
    h_yesno TT_SAVE_BEFORE, FR_T1
    h_goto_if_no FR_T1, .Ltta_cancel\@
    fr_set FR_FACILITY, \fac
    fr_set FR_BATTLE_MODE, FRONTIER_MODE_SINGLES
    fr_set FR_BATTLE_NUM, 0
    VMCall \init
    fr_set FR_STATUS, FR_ST_SAVING
    fr_set FR_BRAIN_BEATEN, 0
    h_closemessage
    fr_save_game FR_T1
    WorkCmpConst FR_T1, 0
    VMJumpIf CMP_EQ, .Ltta_saved\@
    fr_set FR_STATUS, FR_ST_NONE
    VMJump .Ltta_cancel\@
.Ltta_ineligible\@:
    FrGet FR_GET_BANNED_NAMES | 1, FR_T3    // word 1: "Eggs{0100:1} ineligible." (frontier_core)
    h_msgbox TT_NOT_ENOUGH
    h_closemessage
    h_release
.Ltta_cancel\@:
    h_msgbox TT_GOODBYE
    h_closemessage
    h_release
.Ltta_saved\@:
    h_msgbox TT_STEP
    h_closemessage
    VMJump \enter
.Ltta_prize\@:                          // PrizeWaiting: "3-win streak", then the prize
    h_msgbox TT_WON
    VMJump \prize
    .endm

// The lobby's state on arrival (Emerald's OnFrame table): this tent's FR_STATUS -> quit without saving (disqualified),
// won (the line, the prize waiting, saved, then `prize`), lost (saved, goodbye), paused (the "waiting for you" line(s),
// FR_STATUS back to SAVING, saved, then `resume`: the walk in again). `who` = the attendant's uid. resume2 = 1: the
// Verdanturf lobby's two resume lines (WeHaveBeenWaiting, then MustSaveBeforeChallenge).
    .macro tent_returned fac, who, resume, prize, resume2=0
    WorkSetConst TT_STATE, 1
    h_lock
    FrGet FR_FACILITY, FR_T0
    WorkCmpConst FR_T0, \fac
    VMJumpIf CMP_NE, .Lttr_end\@
    FrGet FR_STATUS, FR_T1
    WorkCmpConst FR_T1, FR_ST_SAVING
    VMJumpIf CMP_EQ, .Lttr_quit\@
    WorkCmpConst FR_T1, FR_ST_WON
    VMJumpIf CMP_EQ, .Lttr_won\@
    WorkCmpConst FR_T1, FR_ST_LOST
    VMJumpIf CMP_EQ, .Lttr_lost\@
    WorkCmpConst FR_T1, FR_ST_PAUSED
    VMJumpIf CMP_EQ, .Lttr_resume\@
.Lttr_end\@:
    h_release
.Lttr_quit\@:                           // QuitWithoutSaving
    h_msgbox_actor TT_DIDNT_SAVE, \who
    fr_set FR_STATUS, FR_ST_NONE
    h_closemessage
    h_release
.Lttr_won\@:                            // WonChallenge: the prize is set (and saved) before it is given
    h_msgbox_actor TT_WON, \who
    ActorMsg MSGFILE_SCRIPT, TT_WON_SAVE, \who, 0, 0
    tt_key_set TENT_PRIZE_BIT(\fac)
    fr_set FR_STATUS, FR_ST_NONE
    fr_save_quiet
    h_closemessage
    VMJump \prize
.Lttr_lost\@:                           // LostChallenge
    ActorMsg MSGFILE_SCRIPT, TT_LOST, \who, 0, 0
    fr_set FR_STATUS, FR_ST_NONE
    fr_save_quiet
    h_msgbox_actor TT_GOODBYE2, \who
    h_closemessage
    h_release
.Lttr_resume\@:                         // ResumeChallenge
    .if \resume2
    h_msgbox_actor TT_RESUME, \who
    ActorMsg MSGFILE_SCRIPT, TT_RESUME_SAVE, \who, 0, 0
    .else
    ActorMsg MSGFILE_SCRIPT, TT_RESUME, \who, 0, 0
    .endif
    fr_set FR_STATUS, FR_ST_SAVING
    fr_save_quiet
    h_closemessage
    VMJump \resume
    .endm

// GivePrize (Give<Tent>Prize): "we present you with this prize", the item if the Bag has room ("{player} received the
// prize X." + Emerald's MUS_OBTAIN_ITEM), else "no room" and the prize keeps waiting (key 15); then the goodbye.
    .macro tent_give_prize fac, who, item
    h_msgbox_actor TT_PRIZE, \who
    ItemCheckSpace \item, 1, FR_T1
    WorkCmpConst FR_T1, 0
    VMJumpIf CMP_EQ, .Lttp_full\@
    ItemAdd \item, 1, FR_T1
    tt_key_clear TENT_PRIZE_BIT(\fac)
    h_closemessage
    h_buffer_player
    WordSetItemName 1, \item
    MEPlay MUS_OBTAIN_ITEM
    h_msgbox_info TT_RECEIVED
    MEWait
    h_closemessage
    h_msgbox_actor TT_GOODBYE2, \who
    h_closemessage
    h_release
.Lttp_full\@:
    h_msgbox_actor TT_NO_ROOM, \who
    h_closemessage
    h_release
    .endm

// a scripted walk from a challenge room back to the lobby, in front of the attendant (Emerald: warp <Lobby>, 6, 6)
    .macro tt_to_lobby zone
    pa_to_lobby \zone, TT_LX(6), TT_LZ(6)
    .endm
#endif
