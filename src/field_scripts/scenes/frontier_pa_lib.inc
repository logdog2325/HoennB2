// The Battle Palace and the Battle Arena (frontier_palace_arena, 2026-10-12; notes/FRONTIER_PALACE_ARENA.md): the six
// rooms' shared defines and macros. Pokémon Emerald NDS only. Include after hoenn_story.inc, hoenn_emerald.inc,
// hoenn_frontier.inc. Zone tile = Emerald tile + the room's origin (work/agents/frontier_palace_arena/tools/rooms.py):
// Palace lobby / corridor (1,-2), Palace battle room (1,0), Arena rooms (1,-1).
#ifndef FRONTIER_PA_LIB_INC
#define FRONTIER_PA_LIB_INC
#include "frontier_pa_lines.h"
#include "scenes/frontier_fd_lib.inc"          // fd_say, fd_status, fd_player_visible, fd_to_room, fd_menu3, FD_T0-3
#include "scenes/battle_tower_lib.inc"         // bt_door_open / bt_door_close, BT_DOOR

#define PA_P_LOBBY 466
#define PA_P_CORR 467
#define PA_P_ROOM 468
#define PA_A_LOBBY 429
#define PA_A_CORR 431
#define PA_A_ROOM 433
#define PA_PLAYER 255
#define PA_STATE 0x4000                         // map-local: the lobby's "returned" check ran (0 after each zone init)
#define PA_OPP_GFX 0x4020                       // the opponent NPC's sprite (code 162 reads work 0x4020)
#define PA_FLAG_OPP 1094                        // FLAG_HIDE_BATTLE_TOWER_OPPONENT (as the Factory's; set again on leaving)
#define PA_PAL_STREAK_50 32                     // fr_streak(2, 0, 0) and its best, then Open Level, then doubles (+4)
#define PA_ARE_STREAK_50 40                     // fr_streak(3, 0, 0) ...
#define PA_KEY_OPP 9                            // record key 9: the opponent (frontier_palace_arena.c K_PA_OPP)

// FrontierPA var, sub, a, b: script command 291 (b2tools/patches/frontier_palace_arena.c PA_Cmd; args var + 8 any)
    .macro FrontierPA sub, a=0, b=0, var=FD_T0
    FieldCommand 291
    .2byte \var
    .2byte \sub
    .2byte \a
    .2byte \b
    .2byte 0, 0, 0, 0, 0
    .endm
#define PA_RANDOM 1                             // a = n: var = 0 .. n-1
#define PA_INIT 10                              // a new challenge: nobody met yet
#define PA_NEXT_OPPONENT 11                     // a = facility: the next opponent (or the Brain); var = its walking sprite
#define PA_BRAIN_STATUS 12                      // a = facility: var = 0 none, 1 silver, 2 gold, 3 / 4 (both symbols)
#define PA_GREETING 13                          // var = the greeting's line in the battle room's text (0xFFFF: the Brain)
#define PA_NAME 14                              // a = facility, b = word slot: the opponent's name
#define PA_BATTLE 15                            // a = facility: the battle; var = 1 won, 0 lost
#define PA_HEARD 16                             // a = facility, b = 1 to mark: var = the Brain's first speech was heard

// leave a challenge room for the lobby (the challenge's status set before): the opponent flag left set, the lobby's
// returned-check runs on arrival
    .macro pa_to_lobby zone, x, z
    FlagSet PA_FLAG_OPP
    h_warp_arrive \zone, \x, \z, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm
// the Palace's Single / Double Battle challenges: the lobby spot in front of that attendant, the streak of that mode
    .macro pa_streak_win fac
    FrGet FR_BATTLE_MODE, FR_T0
    WorkCmpConst FR_T0, FRONTIER_MODE_DOUBLES
    VMJumpIf CMP_EQ, .Lpasw_d\@
    fr_streak_win \fac, FRONTIER_MODE_SINGLES
    VMJump .Lpasw_end\@
.Lpasw_d\@:
    fr_streak_win \fac, FRONTIER_MODE_DOUBLES
.Lpasw_end\@:
    .endm
// a results line: word 0 the player, 1-4 the Lv. 50 current / record, Open Level current / record from record key `key`
    .macro pa_results key, line
    h_lock
    h_buffer_player
    FrGet \key, FD_T0
    WordSetNumber 1, FD_T0, 4
    FrGet \key + 1, FD_T0
    WordSetNumber 2, FD_T0, 4
    FrGet \key + 2, FD_T0
    WordSetNumber 3, FD_T0, 4
    FrGet \key + 3, FD_T0
    WordSetNumber 4, FD_T0, 4
    h_msgbox_info \line
    h_release
    .endm
#endif
