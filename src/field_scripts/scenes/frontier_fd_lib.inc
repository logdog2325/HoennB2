// The Battle Factory and the Battle Dome (frontier_factory_dome, 2026-10-12; notes/FRONTIER_FACTORY_DOME.md): the
// seven rooms' shared defines and macros. Pokémon Emerald NDS only. Include after hoenn_story.inc, hoenn_emerald.inc,
// hoenn_frontier.inc. Zone tile = Emerald tile + the room's origin (work/agents/frontier_factory_dome/tools/rooms.py).
#ifndef FRONTIER_FD_LIB_INC
#define FRONTIER_FD_LIB_INC
#include "frontier_fd_lines.h"
#include "scenes/battle_tower_lib.inc"          // bt_door_open / bt_door_close (door_h5_in), BT_DOOR

#define FD_F_LOBBY 408
#define FD_F_PRE 409
#define FD_F_ROOM 410
#define FD_D_LOBBY 411
#define FD_D_CORR 415
#define FD_D_PRE 416
#define FD_D_ROOM 417
#define FD_PLAYER 255
#define FD_T0 0x8032                            // scratch works (the Battle Tower's: never used at the same time)
#define FD_T1 0x8033
#define FD_T2 0x8034
#define FD_T3 0x8035
#define FD_STATE 0x4000                         // map-local: the lobby's "returned" check ran (0 after each zone init)
#define FD_OPP_GFX 0x4020                       // the opponent NPC's sprite (code 162 reads work 0x4020)
#define FD_FLAG_OPP 1094                        // FLAG_HIDE_BATTLE_TOWER_OPPONENT: hides our opponent NPC too (set again
                                                // before leaving: the tower's battle room expects it set)
#define FD_KEY_RENTS 85                         // frontier record keys (notes/FRONTIER.md 6)
#define FD_KEY_D_INFO 90
#define FD_FAC_STREAK_50 48                     // fr_streak(4, 0, 0) and its best, then Open Level (16 + 8f + 2l)
#define FD_DOME_STREAK_50 24                    // fr_streak(1, 0, 0) ...

// FrontierCmd sub, a, b, var: script command 505 (b2tools/patches/frontier_factory_dome.c FR_Cmd)
    .macro FrontierCmd sub, a=0, b=0, var=FD_T0
    FieldCommand 505
    .2byte \sub
    .2byte \a
    .2byte \b
    .2byte \var
    .endm
#define FC_HEAP_FREE 1
#define FC_F_GEN_RENTALS 10
#define FC_F_RENT 11                            // the screen: rent three of the six (var = 1)
#define FC_F_GEN_OPPONENT 12                    // var = 1: Noland
#define FC_F_OPP_TYPE 13                        // var = 0-17 (Gen 3 type), 18 none
#define FC_F_OPP_STYLE 14                       // var = 0-8
#define FC_F_SWAP 15                            // the screens: give one, take one (var = 1 swapped)
#define FC_F_KEEP_OPPONENT 16                   // the defeated opponent's three -> the swap list
#define FC_BRAIN_STATUS 17                      // a = facility: var = 0 none, 1 silver, 2 gold, 3/4 (both symbols)
#define FC_F_WON 18                             // the rents count after a win
#define FC_F_SET_SWAPPED 19
#define FC_F_INIT 20
#define FC_D_INIT 30
#define FC_D_OPPONENT 31                        // var = the round's opponent (0xFFFE Tucker)
#define FC_D_PICK2 32                           // the screen: two of the three; var = 1, var+1/+2 = the party slots
#define FC_D_TREE 33                            // a = 0 left half, 1 right half, 2 the player's half
#define FC_D_RESULT 34                          // a = 1 won (next round), 0 lost
#define FC_D_SET_PICKS 35                       // a, b = the two party slots
#define FC_D_WINNER 36                          // a = word slot: the last champion (var = 0xFFFF none, 1 the player)
#define FC_D_OPP_NAME 37                        // a = word slot: the next opponent's name
#define FC_D_OPP_SPECIES 38                     // a = 0-2: var = its species
#define FC_D_HISTORY 39                         // var = 0 first try, 1 never won, 2 broken streak, 3 champion
#define FC_WORD_LINE 40                         // a = word slot, b = line of the Factory battle room's text
#define FC_D_PREV_KIND 41                       // var = the last tournament's kind: doubles * 2 + Open Level
#define FC_B_PREP 50                            // a = facility: var = the opponent's sprite
#define FC_B_BATTLE 51
#define FC_B_RESULT 52                          // var = 1 won
#define FC_B_END 53                             // frees the Battle Subway work
#define FC_B_SPEECH 54                          // var = the greeting's line (0xFFFF: the Brain)
#define FC_B_NAME 55                            // a = word slot
#define FC_B_BRAIN_GOLD 56                      // var = 1 silver party, 2 gold

// a three-or-more choice list (Emerald's multichoice) at the top right: lines a.. of the zone's text
    .macro fd_menu3 var, l0, l1, l2
    ListMenu_AnchorTopRight 31, 6, 0, 1, \var
    ListMenuAdd \l0, 65535, 0
    ListMenuAdd \l1, 65535, 1
    ListMenuAdd \l2, 65535, 2
    ListMenuShow
    .endm
    .macro fd_say n, who                   // a line said by an actor (uid; 255 the player), then the window closes
    ActorMsg MSGFILE_SCRIPT, \n, \who, 0, 0
    LastKeyWait
    MsgWinCloseAll
    .endm
    .macro fd_status st                    // FR_STATUS = st
    fr_set FR_STATUS, \st
    .endm
// the player walked through a door (set_invisible) before the map change: visible again on arrival
    .macro fd_player_visible
    ActorCmdExec FD_PLAYER, FD_MvVisible\@
    ActorCmdWait
    VMJump .Lfdpv\@
    .balign 4, 0
FD_MvVisible\@:
    set_visible
    step_end
.Lfdpv\@:
    .endm
// leave a challenge room for the lobby (the challenge's status set before): the Subway work freed, the opponent flag
// left set, the lobby's returned-check runs on arrival
    .macro fd_to_lobby zone, x, z
    FrontierCmd FC_B_END
    FlagSet FD_FLAG_OPP
    h_warp_arrive \zone, \x, \z, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm
// Single / Double Battle challenges (FR_BATTLE_MODE, set by the attendant the player talked to): the lobby spot in
// front of that attendant, the streak of that mode
    .macro fd_to_lobby_m zone, x, z, xd, zd
    FrGet FR_BATTLE_MODE, FR_T0
    WorkCmpConst FR_T0, FRONTIER_MODE_DOUBLES
    VMJumpIf CMP_EQ, .Lfdtlm_d\@
    fd_to_lobby \zone, \x, \z
.Lfdtlm_d\@:
    fd_to_lobby \zone, \xd, \zd
    .endm
    .macro fd_streak_win fac
    FrGet FR_BATTLE_MODE, FR_T0
    WorkCmpConst FR_T0, FRONTIER_MODE_DOUBLES
    VMJumpIf CMP_EQ, .Lfdsw_d\@
    fr_streak_win \fac, FRONTIER_MODE_SINGLES
    VMJump .Lfdsw_end\@
.Lfdsw_d\@:
    fr_streak_win \fac, FRONTIER_MODE_DOUBLES
.Lfdsw_end\@:
    .endm
    .macro fd_rest_and_quit zone, x, z, xd, zd, saving, who
    FrGet FR_BATTLE_MODE, FR_T0
    WorkCmpConst FR_T0, FRONTIER_MODE_DOUBLES
    VMJumpIf CMP_EQ, .Lfdrq_d\@
    fr_rest_and_quit \zone, \x, \z, 0, \saving, \who
.Lfdrq_d\@:
    fr_rest_and_quit \zone, \xd, \zd, 0, \saving, \who
    .endm
// a scripted warp to another of our rooms whose script `script` runs on arrival (it starts on a black screen)
    .macro fd_to_room zone, x, z, dir, script, door=0     // door = 1: a door's handle is let go on the black screen
    FadeOutBlack
    RTReserveScript \script
    FadeWait
    .if \door
    BMReleaseHandle BT_DOOR
    .endif
    MapChangeCore \zone, \x, 0, \z, \dir
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm
#endif
