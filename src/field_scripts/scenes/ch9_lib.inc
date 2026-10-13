// Chapter 9 helpers (ch9 agent, 2026-10-07): Mossdeep, Routes 124-127, Shoal Cave, the Treasure Hunter. Macros only (no
// code until used); the code labels at the end are assembled once per file (include guard, C9_DAYS asks for the day-of-
// year routine). Include after "hoenn_story.inc" in the BODY part of a scene file (or after the ScriptEntry table of a
// room file).
#ifndef CH9_LIB_INC
#define CH9_LIB_INC
#include "hoenn_key_items.h"

// script works of these helpers (HLIB_* 0x8030/31, ch3 0x8032-36, ch4 0x8037-39, ch7 0x803A-3D): 0x8040-0x8047
#define C9_A 0x8040
#define C9_B 0x8041
#define C9_C 0x8042
#define C9_D 0x8043
#define C9_MONTH 0x8044
#define C9_DAY 0x8045
#define C9_TODAY 0x8046
#define C9_ELAPSED 0x8047

// lock + faceplayer of a talked-to person (Black 2's NPC script start; {0100:0} = the player's name in the lines)
    .macro c9_talk
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    .endm

// lock without facing (objects, signs): the message sound as every Black 2 NPC script
    .macro c9_lock
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    .endm

// a Pokémon that cries and says its line (lock, faceplayer, waitse, playmoncry, msgbox, waitmoncry, release)
    .macro c9_mon_cry species, n
    c9_talk
    h_playmoncry \species
    h_msgbox \n
    h_waitmoncry
    h_release
    .endm

// giveitem VAR_0x8004 (the item id in a work): HLIB_RESULT 1 given, 0 no room (h_giveitem takes a constant only)
    .macro c9_giveitem_var var
    ItemCheckSpace \var, 1, HLIB_RESULT
    WorkCmpConst HLIB_RESULT, 0
    VMJumpIf CMP_EQ, .Lc9giv\@
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, \var
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
.Lc9giv\@:
    .endm

// Shoal Cave's salt and shells (the bg events of Sapphire's inner, stairs and lower rooms: giveitem, setmetatile of the
// small pile / stone, FLAG_HIDE_TOOK_SHOAL_*). Black 2 draws no such tile: the spot is a Poké Ball object (model 110)
// hidden by the same flag, and a sign on the same tile for Sapphire's "nothing here now" line. Both run this script.
    .macro c9_shoal_pickup item, flag, uid, tnothing, tbag
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set \flag, .Lc9spA\@
    h_giveitem \item
    h_goto_if_eq HLIB_RESULT, 0, .Lc9spB\@
    h_removeobject \uid, \flag
    h_release
.Lc9spA\@:
    h_msgbox_info \tnothing
    h_closemessage
    h_release
.Lc9spB\@:
    h_msgbox_info \tbag
    h_closemessage
    h_release
    .endm

#ifdef C9_DAYS
// Day of the year (1-366) into C9_TODAY: Black 2's scripts only read the date (RTCGetDate), as ch6's Pacifidlog TM
// (0828_room_PacifidlogTown_House2.s H2_Days). Elapsed days between two such numbers: add 365 when the year turned.
C9_TodayOfYear:
    RTCGetDate C9_MONTH, C9_DAY
    WorkSetConst C9_TODAY, 0
    h_goto_if_lt C9_MONTH, 2, L_C9_Sum
    h_addvar C9_TODAY, 31                   // January
    h_goto_if_lt C9_MONTH, 3, L_C9_Sum
    h_addvar C9_TODAY, 28
    h_goto_if_lt C9_MONTH, 4, L_C9_Sum
    h_addvar C9_TODAY, 31
    h_goto_if_lt C9_MONTH, 5, L_C9_Sum
    h_addvar C9_TODAY, 30
    h_goto_if_lt C9_MONTH, 6, L_C9_Sum
    h_addvar C9_TODAY, 31
    h_goto_if_lt C9_MONTH, 7, L_C9_Sum
    h_addvar C9_TODAY, 30
    h_goto_if_lt C9_MONTH, 8, L_C9_Sum
    h_addvar C9_TODAY, 31
    h_goto_if_lt C9_MONTH, 9, L_C9_Sum
    h_addvar C9_TODAY, 31
    h_goto_if_lt C9_MONTH, 10, L_C9_Sum
    h_addvar C9_TODAY, 30
    h_goto_if_lt C9_MONTH, 11, L_C9_Sum
    h_addvar C9_TODAY, 31
    h_goto_if_lt C9_MONTH, 12, L_C9_Sum
    h_addvar C9_TODAY, 30
L_C9_Sum:
    WorkAdd C9_TODAY, C9_DAY
    VMReturn
#endif
#endif
