// BattleFrontier_Lounge2 (zone 476; header scripts 952 -> own file 2088), Pokémon Emerald NDS only (frontier_lounges,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_Lounge2/scripts.inc: the Frontier Maniac, his three followers, a
// triathlete. The Maniac's news (ShowFrontierManiacMessage): the day's facility (VAR_FRONTIER_MANIAC_FACILITY,
// FRONTIER_MANIAC_* 0-9: Tower singles / doubles / multis / link, Dome, Factory, Palace, Arena, Pike, Pyramid; it moves
// on each day, hoenn_frontier.inc fr_lounge_new_day) and one of its three lines by the better of its Lv. 50 / Open Level
// current streaks against Emerald's sFrontierManiacStreakThresholds. Streaks: the record area's current streaks
// (singles; notes/FRONTIER.md 2.2); the Battle Tower's = VAR_BT_LAST_STREAK_LV50 / LV100 (the tower's current streak,
// Black 2's Subway count, as its lobby stores it). This port's tower has no doubles / multi rooms: those three
// facilities read streak 0 (their first line).
// The room: data/interior_layouts/BattleFrontier_Lounge2.json, people data/interiors/emerald/476.json (uid = script =
// Emerald's local id). Messages: src/text/script/emerald/0607_room_BattleFrontier_Lounge2.txt (lounge_rooms.py): 0-5
// the people, 6-15 "the hottest" per facility (Emerald's STR_VAR_1 filled in), 16-45 the news (3 per facility).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"

#define T_Intro 0
#define T_SwingBy 1
#define T_Hot 6
#define T_News 16
#define FM_A 0x8020
#define FM_B 0x8021
#define FM_S 0x8022                     // the streak the news is chosen by

    .macro fm_news f, t1, t2            // sFrontierManiacMessages[f][i]: i = how many of the two thresholds FM_S passes
    WorkCmpConst FM_S, \t1
    VMJumpIf CMP_LE, .Lfn0\@
    WorkCmpConst FM_S, \t2
    VMJumpIf CMP_LE, .Lfn1\@
    h_msgbox T_News+3*(\f)+2
    h_release
.Lfn1\@:
    h_msgbox T_News+3*(\f)+1
    h_release
.Lfn0\@:
    h_msgbox T_News+3*(\f)
    h_release
    .endm

    .macro fm_rec f, fac, t1, t2        // a facility of the record area: its singles current streak, the better level
    h_msgbox T_Hot+\f
    FrGet FR_STREAKS+8*(\fac),FM_A
    FrGet FR_STREAKS+8*(\fac)+2,FM_B
    VMCall Sub_FM_Max
    fm_news \f, \t1, \t2
    .endm

    ScriptEntry FM_Maniac               // 1: BattleFrontier_Lounge2_EventScript_FrontierManiac (8,4)
    ScriptEntry FM_Maniac1              // 2: _Maniac1
    ScriptEntry FM_Maniac2              // 3: _Maniac2
    ScriptEntry FM_Triathlete           // 4: _TriathleteF
    ScriptEntry FM_Maniac3              // 5: _Maniac3
    ScriptEntriesEnd

FM_Maniac:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    fr_lounge_new_day
    h_goto_if_set FLAG_MET_BATTLE_FRONTIER_MANIAC, L_FM_Met
    h_setflag FLAG_MET_BATTLE_FRONTIER_MANIAC
    h_msgbox T_Intro
    VMJump L_FM_Advice
L_FM_Met:
    h_msgbox T_SwingBy
L_FM_Advice:
    .irp f, 0,1,2,3,4,5,6,7,8,9
    WorkCmpConst VAR_FRONTIER_MANIAC_FACILITY, \f
    VMJumpIf CMP_EQ, L_FM_Hot\f
    .endr
    WorkSetConst VAR_FRONTIER_MANIAC_FACILITY, 0
L_FM_Hot0:
    h_msgbox T_Hot+0
    WorkSet FM_A, VAR_BT_LAST_STREAK_LV50       // towerWinStreaks[SINGLES][LV50 / OPEN]
    WorkSet FM_B, VAR_BT_LAST_STREAK_LV100
    VMCall Sub_FM_Max
    fm_news 0, 21, 56
    .irp f, 1,2,3
L_FM_Hot\f:
    h_msgbox T_Hot+\f
    WorkSetConst FM_S, 0                        // no tower doubles / multis here
    fm_news \f, 255, 255
    .endr
L_FM_Hot4:                                      // Dome: tournaments won (FRONTIER_FACILITY_DOME 1)
    fm_rec 4, 1, 2, 4
L_FM_Hot5:                                      // Factory (4)
    fm_rec 5, 4, 7, 21
L_FM_Hot6:                                      // Palace (2)
    fm_rec 6, 2, 7, 21
L_FM_Hot7:                                      // Arena (3)
    fm_rec 7, 3, 14, 28
L_FM_Hot8:                                      // Pike (5): rooms cleared; Emerald's 112 kept (its own bug note)
    fm_rec 8, 5, 13, 112
L_FM_Hot9:                                      // Pyramid (6)
    fm_rec 9, 6, 7, 56

Sub_FM_Max:                                     // FM_S = max(FM_A, FM_B)
    WorkSet FM_S, FM_A
    WorkCmpWork FM_B, FM_A
    VMJumpIf CMP_LE, L_FM_MaxEnd
    WorkSet FM_S, FM_B
L_FM_MaxEnd:
    VMReturn

FM_Maniac1:                                     // lock, msgbox, release (no faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox 2
    h_closemessage
    h_release

FM_Maniac2:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox 3
    h_closemessage
    h_release

FM_Maniac3:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox 4
    h_closemessage
    h_release

FM_Triathlete:
    h_msgbox_npc 5

    .balign 4, 0
