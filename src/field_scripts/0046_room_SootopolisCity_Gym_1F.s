// SootopolisCity_Gym_1F (zone 23): gyms_league (b2tools/gyms_league_rooms.py): step triggers that warp like Sapphire's step-on warp tiles.
// Messages: src/text/script/0029_room_SootopolisCity_Gym_1F.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch10
#include "hoenn_tms.h"  // new_tms: ITEM_TM96 ...
#include "hoenn_trainers.h"  // ch10
#include "hoenn_key_items.h"  // ch10
#include "hoenn_story.inc"  // ch10
#include "hoenn_rematch.inc"    // Emerald's rematches (em_gym_rematch: nothing in Sapphire / Ruby)

    ScriptEntry Script_1
    ScriptEntry GY_Init  // 2: zone init (SootopolisCity_Gym_1F_OnTransition: VAR_ICE_STEP_COUNT 1)  // story:
    ScriptEntry GY_Wallace  // 3: object 1 (SootopolisCity_Gym_1F_EventScript_Wallace)  // story:
    ScriptEntry GY_Guide  // 4: object 2 (SootopolisCity_Gym_1F_EventScript_GymGuide)  // story:
    ScriptEntry GY_Statue  // 5: signs (6,24) / (10,24) (EventScript_LeftGymStatue / RightGymStatue)  // story:
    ScriptEntry GY_Link1  // 6: trigger (8,16): the first ramp (opens at 8 steps)  // story:
    ScriptEntry GY_Link2  // 7: trigger (8,11): the second ramp (28)  // story:
    ScriptEntry GY_Link3  // 8: trigger (8,5): the third ramp (69)  // story:
    ScriptEntry GY_Ice_3_6  // 9: thin ice (3,6)  // story:
    ScriptEntry GY_Ice_4_6  // 10: thin ice (4,6)  // story:
    ScriptEntry GY_Ice_5_6  // 11: thin ice (5,6)  // story:
    ScriptEntry GY_Ice_6_6  // 12: thin ice (6,6)  // story:
    ScriptEntry GY_Ice_7_6  // 13: thin ice (7,6)  // story:
    ScriptEntry GY_Ice_8_6  // 14: thin ice (8,6)  // story:
    ScriptEntry GY_Ice_9_6  // 15: thin ice (9,6)  // story:
    ScriptEntry GY_Ice_10_6  // 16: thin ice (10,6)  // story:
    ScriptEntry GY_Ice_11_6  // 17: thin ice (11,6)  // story:
    ScriptEntry GY_Ice_12_6  // 18: thin ice (12,6)  // story:
    ScriptEntry GY_Ice_13_6  // 19: thin ice (13,6)  // story:
    ScriptEntry GY_Ice_3_7  // 20: thin ice (3,7)  // story:
    ScriptEntry GY_Ice_4_7  // 21: thin ice (4,7)  // story:
    ScriptEntry GY_Ice_5_7  // 22: thin ice (5,7)  // story:
    ScriptEntry GY_Ice_6_7  // 23: thin ice (6,7)  // story:
    ScriptEntry GY_Ice_7_7  // 24: thin ice (7,7)  // story:
    ScriptEntry GY_Ice_9_7  // 25: thin ice (9,7)  // story:
    ScriptEntry GY_Ice_10_7  // 26: thin ice (10,7)  // story:
    ScriptEntry GY_Ice_11_7  // 27: thin ice (11,7)  // story:
    ScriptEntry GY_Ice_13_7  // 28: thin ice (13,7)  // story:
    ScriptEntry GY_Ice_3_8  // 29: thin ice (3,8)  // story:
    ScriptEntry GY_Ice_4_8  // 30: thin ice (4,8)  // story:
    ScriptEntry GY_Ice_5_8  // 31: thin ice (5,8)  // story:
    ScriptEntry GY_Ice_6_8  // 32: thin ice (6,8)  // story:
    ScriptEntry GY_Ice_7_8  // 33: thin ice (7,8)  // story:
    ScriptEntry GY_Ice_8_8  // 34: thin ice (8,8)  // story:
    ScriptEntry GY_Ice_9_8  // 35: thin ice (9,8)  // story:
    ScriptEntry GY_Ice_10_8  // 36: thin ice (10,8)  // story:
    ScriptEntry GY_Ice_11_8  // 37: thin ice (11,8)  // story:
    ScriptEntry GY_Ice_12_8  // 38: thin ice (12,8)  // story:
    ScriptEntry GY_Ice_13_8  // 39: thin ice (13,8)  // story:
    ScriptEntry GY_Ice_4_9  // 40: thin ice (4,9)  // story:
    ScriptEntry GY_Ice_5_9  // 41: thin ice (5,9)  // story:
    ScriptEntry GY_Ice_6_9  // 42: thin ice (6,9)  // story:
    ScriptEntry GY_Ice_7_9  // 43: thin ice (7,9)  // story:
    ScriptEntry GY_Ice_8_9  // 44: thin ice (8,9)  // story:
    ScriptEntry GY_Ice_9_9  // 45: thin ice (9,9)  // story:
    ScriptEntry GY_Ice_10_9  // 46: thin ice (10,9)  // story:
    ScriptEntry GY_Ice_12_9  // 47: thin ice (12,9)  // story:
    ScriptEntry GY_Ice_13_9  // 48: thin ice (13,9)  // story:
    ScriptEntry GY_Ice_5_12  // 49: thin ice (5,12)  // story:
    ScriptEntry GY_Ice_6_12  // 50: thin ice (6,12)  // story:
    ScriptEntry GY_Ice_7_12  // 51: thin ice (7,12)  // story:
    ScriptEntry GY_Ice_8_12  // 52: thin ice (8,12)  // story:
    ScriptEntry GY_Ice_9_12  // 53: thin ice (9,12)  // story:
    ScriptEntry GY_Ice_10_12  // 54: thin ice (10,12)  // story:
    ScriptEntry GY_Ice_11_12  // 55: thin ice (11,12)  // story:
    ScriptEntry GY_Ice_5_13  // 56: thin ice (5,13)  // story:
    ScriptEntry GY_Ice_7_13  // 57: thin ice (7,13)  // story:
    ScriptEntry GY_Ice_8_13  // 58: thin ice (8,13)  // story:
    ScriptEntry GY_Ice_9_13  // 59: thin ice (9,13)  // story:
    ScriptEntry GY_Ice_10_13  // 60: thin ice (10,13)  // story:
    ScriptEntry GY_Ice_11_13  // 61: thin ice (11,13)  // story:
    ScriptEntry GY_Ice_5_14  // 62: thin ice (5,14)  // story:
    ScriptEntry GY_Ice_6_14  // 63: thin ice (6,14)  // story:
    ScriptEntry GY_Ice_7_14  // 64: thin ice (7,14)  // story:
    ScriptEntry GY_Ice_8_14  // 65: thin ice (8,14)  // story:
    ScriptEntry GY_Ice_10_14  // 66: thin ice (10,14)  // story:
    ScriptEntry GY_Ice_11_14  // 67: thin ice (11,14)  // story:
    ScriptEntry GY_Ice_7_17  // 68: thin ice (7,17)  // story:
    ScriptEntry GY_Ice_8_17  // 69: thin ice (8,17)  // story:
    ScriptEntry GY_Ice_7_18  // 70: thin ice (7,18)  // story:
    ScriptEntry GY_Ice_8_18  // 71: thin ice (8,18)  // story:
    ScriptEntry GY_Ice_9_18  // 72: thin ice (9,18)  // story:
    ScriptEntry GY_Ice_8_19  // 73: thin ice (8,19)  // story:
    ScriptEntry GY_Ice_9_19  // 74: thin ice (9,19)  // story:
// >>> emerald_rooms sootopolis_entries (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
    ScriptEntry GY_EIce_8_7     // 75: thin ice (8,7) (Emerald only)
    ScriptEntry GY_EIce_3_9     // 76: thin ice (3,9) (Emerald only)
    ScriptEntry GY_EIce_9_14    // 77: thin ice (9,14) (Emerald only)
    ScriptEntry GY_EIce_9_17    // 78: thin ice (9,17) (Emerald only)
    ScriptEntry GY_EIce_7_19    // 79: thin ice (7,19) (Emerald only)
#endif
// <<< emerald_rooms sootopolis_entries
    ScriptEntriesEnd

Script_1:                                      // Sapphire warp 2 (11,22) -> SootopolisCity_Gym_B1F warp 0 (11,22)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 24, 12, 0, 18, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0

// ---- story (chapter Ch10, ch10 agent 2026-10-07; Sapphire data/maps/SootopolisCity_Gym_1F/scripts.inc; generators keep everything from
// this line on; entries above marked "// story:"). Messages: 0029_room_SootopolisCity_Gym_1F.txt
// Room tiles = Sapphire tiles + (1, 0); the B1F's = Sapphire + (1, -4) (room.json origins). People (data/story/ch10.json, uid = Sapphire local id): Wallace 1 (hidden by FLAG_HIDE_WALLACE_SOOTOPOLIS_GYM until the Kyogre battle), the guide 2, the statue plaques (6,24) / (10,24) (script GY_Statue).
// The ice floor (Sapphire field_tasks.c PerStepCallback_8069DD4, the gym's map scripts): 66 thin-ice tiles in three rooms. A first step cracks a tile (SE, VAR_ICE_STEP_COUNT + 1, the tile's bit in the row's temporary work 0x4001-0x400A: Sapphire's VAR_TEMP_1-A, one work per row, bit x-3), a step onto a cracked tile drops the player to the B1F (same tile) and the zone init sets VAR_ICE_STEP_COUNT 1 and clears the rows again on the way back. Reaching 8 / 28 / 69 opens the ice ramps (8,15-16) / (8,10-11) / (8,4-5) (the count goes up by one then, as Sapphire's unlock scripts); before that the lower ramp tile slides the player back onto the tile below (MB_SLIDE_SOUTH; that tile's own cracking applies).
// Black 2 gaps: the floor is a model, so a cracked tile does not change its picture and the ramps do not turn into stairs (only the sounds tell; proposal: crack and stairs decals after the story). The player cannot see the cracked tiles: remembering the path is the puzzle (as Sapphire, where the crack shows).
#include "scenes/ch10_lib.inc"
#define T_ReceivedRainBadge 1
#define T_ExplainRainBadgeTakeThis 2
#define T_ExplainWaterPulse 3
#define T_WallacePostBattle 4
#define T_GoGetFortreeBadge 5
#define T_GymGuideAdvice 6
#define T_GymGuidePostVictory 7
#define T_GymStatue 8
#define T_GymStatueCertified 9
#define T_BagFull 10
#define GY_WALLACE 1
#define GY_B1F_ZONE 24                  // SootopolisCity_Gym_B1F: room tiles = Sapphire + (1, -4)

GY_Init:                                // SootopolisCity_Gym_1F_OnTransition: setvar VAR_ICE_STEP_COUNT, 1 (and the rows' temporary works are fresh)
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc)
#endif
    h_setvar VAR_ICE_STEP_COUNT, 1
#ifdef HOENN_TEST_CH10_ICE
    h_setvar VAR_ICE_STEP_COUNT, 70     // test builds only: every ramp is open from the start (a test walks straight up to Wallace)
#endif
    h_setvar 0x4001, 0
    h_setvar 0x4002, 0
    h_setvar 0x4003, 0
    h_setvar 0x4004, 0
    h_setvar 0x4005, 0
    h_setvar 0x4006, 0
    h_setvar 0x4007, 0
    h_setvar 0x4008, 0
    h_setvar 0x4009, 0
    h_setvar 0x400A, 0
    VMHalt

GY_Wallace:                             // SootopolisCity_Gym_1F_EventScript_Wallace (trainerbattle_single ..., WallaceDefeated, NO_MUSIC)
    h_lock
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_defeated TRAINER_WALLACE, L_GY_AfterBattle
    TrainerSayMessage TRAINER_WALLACE, 0, GY_WALLACE   // Wallace: Allow me to formally introduce myself. ...
    ActorMsgClose                       // (NO_MUSIC: no eye-contact music)
    c10_trainerbattle TRAINER_WALLACE     // (in battle: Bravo. I realize now your authenticity and magnificence ...)
    WordSetPlayerName 0                 // SootopolisCity_Gym_1F_EventScript_WallaceDefeated
    SystemMsg T_ReceivedRainBadge, 2    // <player> received the Rain Badge from Wallace.
    h_badge_fanfare                     // Common_EventScript_PlayGymBadgeFanfare
    MsgWinCloseAll
    h_msgbox_actor T_ExplainRainBadgeTakeThis, GY_WALLACE  // Having that Badge assures you the full obedience of all your Pokémon ...
    h_closemessage
    h_setflag FLAG_DEFEATED_SOOTOPOLIS_GYM
    h_givebadge 8                       // setflag FLAG_BADGE08_GET
    h_set_gym_trainers 8                // setvar VAR_0x8008, 8 + Common_EventScript_SetGymTrainers
#ifdef HOENN_EMERALD
    VMCall Sub_GY_EmJuanDefeated        // Emerald: Juan (emerald_ch10)
    h_release
#endif
L_GY_GiveWaterPulse:                    // SootopolisCity_Gym_1F_EventScript_GiveWaterPulse2
    h_giveitem ITEM_TM97                // Gen 3 TM03 Water Pulse: the new TM97 (b2tools/patches/new_tms.py)
    h_goto_if_eq HLIB_RESULT, 0, L_GY_BagFull
    h_msgbox_actor T_ExplainWaterPulse, GY_WALLACE     // The TM I handed you contains Water Pulse. ...
    h_setflag FLAG_RECEIVED_TM_WATER_PULSE
    h_release
L_GY_AfterBattle:
    em_gym_rematch TRAINER_WALLACE, GY_WALLACE   // Emerald: Juan after the Hall of Fame, a rematch (hoenn_rematch.inc)
    h_goto_if_unset FLAG_RECEIVED_TM_WATER_PULSE, L_GY_GiveWaterPulse
    h_goto_if_no_badge 6, L_GY_GoGetFortree     // goto_if_unset FLAG_BADGE06_GET (the Feather Badge)
    h_msgbox_actor T_WallacePostBattle, GY_WALLACE  // Trainers who have gathered all the Gym Badges of Hoenn should make way for the ultimate destination. ...
    h_release
L_GY_GoGetFortree:                      // SootopolisCity_Gym_1F_EventScript_GoGetFortreeBadge
    h_msgbox_actor T_GoGetFortreeBadge, GY_WALLACE
    h_release
L_GY_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release

GY_Guide:                               // SootopolisCity_Gym_1F_EventScript_GymGuide
    c10_talk
    h_goto_if_set FLAG_DEFEATED_SOOTOPOLIS_GYM, L_GY_GuideVictory
    h_msgbox T_GymGuideAdvice           // Yo! How's it going, Champion-bound <player>? ...
    h_release
L_GY_GuideVictory:
    h_msgbox T_GymGuidePostVictory      // Yow! You've beaten even Wallace, ...
    h_release

GY_Statue:                              // SootopolisCity_Gym_1F_EventScript_LeftGymStatue / RightGymStatue (lockall; MSGBOX_DEFAULT)
    c10_lock
    h_goto_if_badge 8, L_GY_StatueCertified
    h_msgbox_info T_GymStatue           // Sootopolis City Pokémon Gym
    h_closemessage
    h_release
L_GY_StatueCertified:
    h_msgbox_info T_GymStatueCertified  // Sootopolis City Pokémon Gym / Wallace's Certified Trainers: <player>
    h_closemessage
    h_release

#ifdef HOENN_EMERALD
// Pokémon Emerald NDS (emerald_ch10, 2026-10-12): Juan is the Leader (pokeemerald SootopolisCity_Gym_1F_EventScript_Juan /
// _JuanDefeated): TRAINER_WALLACE is Juan's slot in Emerald's trainer data (emerald_data), object 1 is Juan (data/story/ch10.json
// model_emerald 276, no hide flag: Sootopolis keeps the Gym's door shut until Archie and Maxie leave), Emerald's lines in
// src/text/script/emerald/0029_*.txt (same rows; row 11 the PokéNav line, decision 3A: a plain message with the jingle).
#include "scenes/emerald/b1_common.inc"
#define T_RegisteredJuan 11
Sub_GY_EmJuanDefeated:                  // SootopolisCity_Gym_1F_EventScript_JuanDefeated after the Badge
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_RESIDENTS
    h_setflag FLAG_HIDE_STEVEN_SOOTOPOLIS               // FLAG_HIDE_SOOTOPOLIS_CITY_STEVEN
    h_setflag FLAG_HIDE_WALLACE_SOOTOPOLIS              // FLAG_HIDE_SOOTOPOLIS_CITY_WALLACE
    h_setvar VAR_SOOTOPOLIS_STATE, 6                    // VAR_SOOTOPOLIS_CITY_STATE
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_MAN_1
    h_giveitem ITEM_TM97                // SootopolisCity_Gym_1F_EventScript_GiveWaterPulse (Water Pulse: the new TM97)
    h_goto_if_eq HLIB_RESULT, 0, L_GY_EmBagFull
    h_msgbox_actor T_ExplainWaterPulse, GY_WALLACE
    h_setflag FLAG_RECEIVED_TM_WATER_PULSE
L_GY_EmRegister:
    h_closemessage
    h_delay 30
    h_playfanfare MUS_REGISTER_MATCH_CALL
    h_msgbox_info T_RegisteredJuan      // Registered Gym Leader Juan in the PokéNav.
    h_waitfanfare
    h_closemessage
    h_delay 30
    VMReturn
L_GY_EmBagFull:                         // Common_EventScript_BagIsFull (then the PokéNav line, as Emerald)
    h_bag_is_full T_BagFull
    VMJump L_GY_EmRegister
#endif

// ---- the ice floor ---------------------------------------------------------------------------------------------------
// one thin-ice tile: rowwork = the row's temporary work, mask = its bit; (bx, bz) = the same tile in the B1F's room tiles
    .macro gy_ice rowwork, mask, bx, bz
    ActorsPauseAll
    WorkSet C10_A, \rowwork
    WorkAnd C10_A, \mask
    WorkCmpConst C10_A, 0
    VMJumpIf CMP_NE, .Lgyfall\@
    WorkOr \rowwork, \mask             // the tile cracks (MB_THIN_ICE -> MB_CRACKED_ICE)
    VMJump GY_IceCracked
.Lgyfall\@:                             // a cracked tile: the player falls through (FallThroughIce: warphole B1F)
    VMCall GY_IceFallStart
    FadeOutBlack                        // Black 2's pattern for a scripted map change (fade, reserve the arrival script, wait): hm_free
    RTReserveScript 10017               // Script_18 fades in and unpauses on arrival, else the arrival zone's people are dead
    FadeWait
    MapChangeCore GY_B1F_ZONE, \bx, 0, \bz, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm

GY_IceCracked:                          // PerStepCallback_8069DD4 case 2 + the frame table (8 / 28 / 69 steps)
// >>> emerald_rooms sootopolis_cracked_jump (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
    VMJump GY_IceCrackedEm              // Emerald: 8 / 28 / 67
#endif
// <<< emerald_rooms sootopolis_cracked_jump
    WorkAdd VAR_ICE_STEP_COUNT, 1
    SEPlay C10_SE_ICE_CRACK
    WorkCmpConst VAR_ICE_STEP_COUNT, 8
    VMJumpIf CMP_EQ, GY_IceUnlock
    WorkCmpConst VAR_ICE_STEP_COUNT, 28
    VMJumpIf CMP_EQ, GY_IceUnlock
    WorkCmpConst VAR_ICE_STEP_COUNT, 69
    VMJumpIf CMP_EQ, GY_IceUnlock
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
GY_IceUnlock:                           // SootopolisCity_Gym_1F_EventScript_UnlockFirstStairs / Second / Third
    WorkAdd VAR_ICE_STEP_COUNT, 1
    VMSleep 20                          // delay 40
    SEPlay C10_SE_ICE_STAIRS
    VMSleep 10
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
GY_IceFallStart:                        // SootopolisCity_Gym_1F_EventScript_FallThroughIce: delay 20, the player vanishes, SE_FALL, delay 60
    VMSleep 10
    SEPlay C10_SE_ICE_BREAK
    VMSleep 10
    h_applymovement 255, Mv_GY_Vanish
    h_waitmovement
    SEPlay C10_SE_FALL
    VMSleep 30
    VMReturn

// the ice ramps (MB_SLIDE_SOUTH until the stairs open): the lower tile slides the player back onto the tile below
    .macro gy_link need, below
    WorkCmpConst VAR_ICE_STEP_COUNT, \need
    VMJumpIf CMP_GE, .Lgylo\@
    ActorsPauseAll
    h_applymovement 255, Mv_GY_SlideBack
    h_waitmovement
    VMJump \below
.Lgylo\@:
    VMHalt
    .endm
GY_Link1:
    gy_link 9, GY_Ice_8_17
GY_Link2:
    gy_link 29, GY_Ice_8_12
GY_Link3:
// >>> emerald_rooms sootopolis_link3 (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
    gy_link 68, GY_Ice_8_6              // Emerald: the third ramp opens at 67 (+1)
#endif
// <<< emerald_rooms sootopolis_link3
    gy_link 70, GY_Ice_8_6

GY_Ice_3_6:
    gy_ice 0x4001, 0x0001, 4, 2
GY_Ice_4_6:
    gy_ice 0x4001, 0x0002, 5, 2
GY_Ice_5_6:
    gy_ice 0x4001, 0x0004, 6, 2
GY_Ice_6_6:
    gy_ice 0x4001, 0x0008, 7, 2
GY_Ice_7_6:
    gy_ice 0x4001, 0x0010, 8, 2
GY_Ice_8_6:
    gy_ice 0x4001, 0x0020, 9, 2
GY_Ice_9_6:
    gy_ice 0x4001, 0x0040, 10, 2
GY_Ice_10_6:
    gy_ice 0x4001, 0x0080, 11, 2
GY_Ice_11_6:
    gy_ice 0x4001, 0x0100, 12, 2
GY_Ice_12_6:
    gy_ice 0x4001, 0x0200, 13, 2
GY_Ice_13_6:
    gy_ice 0x4001, 0x0400, 14, 2
GY_Ice_3_7:
    gy_ice 0x4002, 0x0001, 4, 3
GY_Ice_4_7:
    gy_ice 0x4002, 0x0002, 5, 3
GY_Ice_5_7:
    gy_ice 0x4002, 0x0004, 6, 3
GY_Ice_6_7:
    gy_ice 0x4002, 0x0008, 7, 3
GY_Ice_7_7:
    gy_ice 0x4002, 0x0010, 8, 3
GY_Ice_9_7:
    gy_ice 0x4002, 0x0040, 10, 3
GY_Ice_10_7:
    gy_ice 0x4002, 0x0080, 11, 3
GY_Ice_11_7:
    gy_ice 0x4002, 0x0100, 12, 3
GY_Ice_13_7:
    gy_ice 0x4002, 0x0400, 14, 3
GY_Ice_3_8:
    gy_ice 0x4003, 0x0001, 4, 4
GY_Ice_4_8:
    gy_ice 0x4003, 0x0002, 5, 4
GY_Ice_5_8:
    gy_ice 0x4003, 0x0004, 6, 4
GY_Ice_6_8:
    gy_ice 0x4003, 0x0008, 7, 4
GY_Ice_7_8:
    gy_ice 0x4003, 0x0010, 8, 4
GY_Ice_8_8:
    gy_ice 0x4003, 0x0020, 9, 4
GY_Ice_9_8:
    gy_ice 0x4003, 0x0040, 10, 4
GY_Ice_10_8:
    gy_ice 0x4003, 0x0080, 11, 4
GY_Ice_11_8:
    gy_ice 0x4003, 0x0100, 12, 4
GY_Ice_12_8:
    gy_ice 0x4003, 0x0200, 13, 4
GY_Ice_13_8:
    gy_ice 0x4003, 0x0400, 14, 4
GY_Ice_4_9:
    gy_ice 0x4004, 0x0002, 5, 5
GY_Ice_5_9:
    gy_ice 0x4004, 0x0004, 6, 5
GY_Ice_6_9:
    gy_ice 0x4004, 0x0008, 7, 5
GY_Ice_7_9:
    gy_ice 0x4004, 0x0010, 8, 5
GY_Ice_8_9:
    gy_ice 0x4004, 0x0020, 9, 5
GY_Ice_9_9:
    gy_ice 0x4004, 0x0040, 10, 5
GY_Ice_10_9:
    gy_ice 0x4004, 0x0080, 11, 5
GY_Ice_12_9:
    gy_ice 0x4004, 0x0200, 13, 5
GY_Ice_13_9:
    gy_ice 0x4004, 0x0400, 14, 5
GY_Ice_5_12:
    gy_ice 0x4005, 0x0004, 6, 8
GY_Ice_6_12:
    gy_ice 0x4005, 0x0008, 7, 8
GY_Ice_7_12:
    gy_ice 0x4005, 0x0010, 8, 8
GY_Ice_8_12:
    gy_ice 0x4005, 0x0020, 9, 8
GY_Ice_9_12:
    gy_ice 0x4005, 0x0040, 10, 8
GY_Ice_10_12:
    gy_ice 0x4005, 0x0080, 11, 8
GY_Ice_11_12:
    gy_ice 0x4005, 0x0100, 12, 8
GY_Ice_5_13:
    gy_ice 0x4006, 0x0004, 6, 9
GY_Ice_7_13:
    gy_ice 0x4006, 0x0010, 8, 9
GY_Ice_8_13:
    gy_ice 0x4006, 0x0020, 9, 9
GY_Ice_9_13:
    gy_ice 0x4006, 0x0040, 10, 9
GY_Ice_10_13:
    gy_ice 0x4006, 0x0080, 11, 9
GY_Ice_11_13:
    gy_ice 0x4006, 0x0100, 12, 9
GY_Ice_5_14:
    gy_ice 0x4007, 0x0004, 6, 10
GY_Ice_6_14:
    gy_ice 0x4007, 0x0008, 7, 10
GY_Ice_7_14:
    gy_ice 0x4007, 0x0010, 8, 10
GY_Ice_8_14:
    gy_ice 0x4007, 0x0020, 9, 10
GY_Ice_10_14:
    gy_ice 0x4007, 0x0080, 11, 10
GY_Ice_11_14:
    gy_ice 0x4007, 0x0100, 12, 10
GY_Ice_7_17:
    gy_ice 0x4008, 0x0010, 8, 13
GY_Ice_8_17:
    gy_ice 0x4008, 0x0020, 9, 13
GY_Ice_7_18:
    gy_ice 0x4009, 0x0010, 8, 14
GY_Ice_8_18:
    gy_ice 0x4009, 0x0020, 9, 14
GY_Ice_9_18:
    gy_ice 0x4009, 0x0040, 10, 14
GY_Ice_8_19:
    gy_ice 0x400A, 0x0020, 9, 15
GY_Ice_9_19:
    gy_ice 0x400A, 0x0040, 10, 15

    .balign 4, 0
Mv_GY_SlideBack:
    walk_fast_down
    step_end
    .balign 4, 0
Mv_GY_Vanish:                           // SootopolisCity_Gym_1F_Movement_FallThroughIce
    set_invisible
    step_end

#include "common/movement.inc"
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
    .balign 4, 0

// >>> emerald_rooms sootopolis_ice (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
GY_EIce_8_7:
    gy_ice 0x4002, 0x0020, 9, 3
GY_EIce_3_9:
    gy_ice 0x4004, 0x0001, 4, 5
GY_EIce_9_14:
    gy_ice 0x4007, 0x0040, 10, 10
GY_EIce_9_17:
    gy_ice 0x4008, 0x0040, 10, 13
GY_EIce_7_19:
    gy_ice 0x400A, 0x0010, 8, 15
GY_IceCrackedEm:                        // GY_IceCracked with Emerald's thresholds (OnFrame: 8 / 28 / 67)
    WorkAdd VAR_ICE_STEP_COUNT, 1
    SEPlay C10_SE_ICE_CRACK
    WorkCmpConst VAR_ICE_STEP_COUNT, 8
    VMJumpIf CMP_EQ, GY_IceUnlock
    WorkCmpConst VAR_ICE_STEP_COUNT, 28
    VMJumpIf CMP_EQ, GY_IceUnlock
    WorkCmpConst VAR_ICE_STEP_COUNT, 67
    VMJumpIf CMP_EQ, GY_IceUnlock
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
#endif
// <<< emerald_rooms sootopolis_ice
