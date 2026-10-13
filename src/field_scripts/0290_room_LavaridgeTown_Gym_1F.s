// LavaridgeTown_Gym_1F (zone 145): gyms_league (b2tools/gyms_league_rooms.py): step triggers that warp like Sapphire's step-on warp tiles.
// Messages: src/text/script/0164_room_LavaridgeTown_Gym_1F.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntry Script_10
    ScriptEntry Script_11
    ScriptEntry Script_12
    ScriptEntry Script_13
    ScriptEntry Script_14
    ScriptEntry Script_15
    ScriptEntry Script_16
    ScriptEntry Script_17
    ScriptEntry Script_18
    ScriptEntry Script_19
    ScriptEntry Script_20
    ScriptEntry LG_Flannery     // 21: Flannery (LavaridgeTown_Gym_1F_EventScript_Flannery), ch5
    ScriptEntry LG_GymGuide     // 22: Gym guide (LavaridgeTown_Gym_1F_EventScript_GymGuide)
    ScriptEntry LG_Statue       // 23: statues (LeftGymStatue / RightGymStatue)
// >>> emerald_rooms lavaridge_entries (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
    ScriptEntry EL_Hole2            // 24: Emerald warp 2 (10,18) -> LavaridgeTown_Gym_B1F warp 0 (10,18)
    ScriptEntry EL_Hole3            // 25: Emerald warp 3 (8,9) -> LavaridgeTown_Gym_B1F warp 2 (8,9)
    ScriptEntry EL_Hole5            // 26: Emerald warp 5 (5,14) -> LavaridgeTown_Gym_B1F warp 3 (5,14)
    ScriptEntry EL_Hole6            // 27: Emerald warp 6 (0,17) -> LavaridgeTown_Gym_B1F warp 1 (0,17)
    ScriptEntry EL_Hole7            // 28: Emerald warp 7 (5,9) -> LavaridgeTown_Gym_B1F warp 5 (5,9)
    ScriptEntry EL_Hole8            // 29: Emerald warp 8 (2,15) -> LavaridgeTown_Gym_B1F warp 6 (2,15)
    ScriptEntry EL_Hole9            // 30: Emerald warp 9 (3,14) -> LavaridgeTown_Gym_B1F warp 7 (3,14)
    ScriptEntry EL_Hole10           // 31: Emerald warp 10 (1,14) -> LavaridgeTown_Gym_B1F warp 8 (1,14)
    ScriptEntry EL_Hole11           // 32: Emerald warp 11 (0,10) -> LavaridgeTown_Gym_B1F warp 9 (0,10)
    ScriptEntry EL_Hole12           // 33: Emerald warp 12 (3,10) -> LavaridgeTown_Gym_B1F warp 10 (3,10)
    ScriptEntry EL_Hole13           // 34: Emerald warp 13 (0,6) -> LavaridgeTown_Gym_B1F warp 11 (0,6)
    ScriptEntry EL_Hole15           // 35: Emerald warp 15 (5,6) -> LavaridgeTown_Gym_B1F warp 13 (5,6)
    ScriptEntry EL_Hole16           // 36: Emerald warp 16 (2,3) -> LavaridgeTown_Gym_B1F warp 14 (2,3)
    ScriptEntry EL_Hole17           // 37: Emerald warp 17 (5,2) -> LavaridgeTown_Gym_B1F warp 15 (5,2)
    ScriptEntry EL_Hole18           // 38: Emerald warp 18 (7,2) -> LavaridgeTown_Gym_B1F warp 16 (7,2)
    ScriptEntry EL_Hole19           // 39: Emerald warp 19 (8,6) -> LavaridgeTown_Gym_B1F warp 17 (8,6)
    ScriptEntry EL_Hole20           // 40: Emerald warp 20 (10,6) -> LavaridgeTown_Gym_B1F warp 18 (10,6)
    ScriptEntry EL_Hole22           // 41: Emerald warp 22 (12,3) -> LavaridgeTown_Gym_B1F warp 19 (12,3)
    ScriptEntry EL_Hole23           // 42: Emerald warp 23 (14,6) -> LavaridgeTown_Gym_B1F warp 21 (14,6)
    ScriptEntry EL_Hole25           // 43: Emerald warp 25 (12,12) -> LavaridgeTown_Gym_B1F warp 23 (12,12)
#endif
// <<< emerald_rooms lavaridge_entries
    ScriptEntriesEnd

Script_1:                                      // Sapphire warp 2 (3,21) -> LavaridgeTown_Gym_B1F warp 0 (3,21)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 4, 0, 22, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // Sapphire warp 3 (1,14) -> LavaridgeTown_Gym_B1F warp 2 (1,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 2, 0, 15, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // Sapphire warp 4 (6,14) -> LavaridgeTown_Gym_B1F warp 4 (6,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 7, 0, 15, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // Sapphire warp 5 (1,6) -> LavaridgeTown_Gym_B1F warp 3 (1,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 2, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // Sapphire warp 6 (9,2) -> LavaridgeTown_Gym_B1F warp 1 (9,2)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 10, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                      // Sapphire warp 7 (6,20) -> LavaridgeTown_Gym_B1F warp 5 (6,20)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 7, 0, 21, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:                                      // Sapphire warp 8 (0,23) -> LavaridgeTown_Gym_B1F warp 6 (0,23)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 1, 0, 24, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:                                      // Sapphire warp 9 (0,17) -> LavaridgeTown_Gym_B1F warp 7 (0,17)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 1, 0, 18, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:                                      // Sapphire warp 10 (4,17) -> LavaridgeTown_Gym_B1F warp 8 (4,17)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 5, 0, 18, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_10:                                      // Sapphire warp 11 (0,11) -> LavaridgeTown_Gym_B1F warp 9 (0,11)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 1, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:                                      // Sapphire warp 12 (4,12) -> LavaridgeTown_Gym_B1F warp 10 (4,12)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 5, 0, 13, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_12:                                      // Sapphire warp 13 (4,9) -> LavaridgeTown_Gym_B1F warp 11 (4,9)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 5, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_13:                                      // Sapphire warp 14 (0,2) -> LavaridgeTown_Gym_B1F warp 12 (0,2)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 1, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_14:                                      // Sapphire warp 15 (4,6) -> LavaridgeTown_Gym_B1F warp 13 (4,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 5, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_15:                                      // Sapphire warp 16 (4,2) -> LavaridgeTown_Gym_B1F warp 14 (4,2)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 5, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_16:                                      // Sapphire warp 17 (10,19) -> LavaridgeTown_Gym_B1F warp 15 (10,18)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 11, 0, 19, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_17:                                      // Sapphire warp 18 (10,14) -> LavaridgeTown_Gym_B1F warp 16 (10,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 11, 0, 15, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_18:                                      // Sapphire warp 19 (6,6) -> LavaridgeTown_Gym_B1F warp 17 (6,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 7, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_19:                                      // Sapphire warp 20 (6,2) -> LavaridgeTown_Gym_B1F warp 18 (6,2)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 7, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_20:                                      // Sapphire warp 21 (10,6) -> LavaridgeTown_Gym_B1F warp 19 (10,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 11, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0

// ---- story
// Chapter Ch5 (ch5 agent, 2026-10-07; Sapphire data/maps/LavaridgeTown_Gym_1F/scripts.inc): Flannery and the Heat Badge,
// TM50 Overheat, the guide, the statues. People and statues: data/story/ch5.json (uid = Sapphire local id): Flannery 1,
// the guide 6; Cole 2, Zane 3, Axle 4, Sadie 5 and Andy 7 are eye-contact trainers (Black 2's global trainer script
// 3000 + id). Sapphire buries them in the hot sand (MOVEMENT_TYPE_BURIED, sight 1: they jump out when you step next to
// them; Black 2 has no buried trainers): they stand, facing down, sight 1. The OnTransition temp vars only drive that.
// Text: src/text/script/0164_room_LavaridgeTown_Gym_1F.txt lines 0-8.
#define LG_FLANNERY 1

LG_Flannery:                                     // trainerbattle_single TRAINER_FLANNERY, ..., FlanneryDefeated, NO_MUSIC
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_defeated TRAINER_FLANNERY, L_LG_Rematch
    TrainerSayMessage TRAINER_FLANNERY, 0, LG_FLANNERY   // Welcome... No, wait. Puny Trainer, ...
    ActorMsgClose                                // (NO_MUSIC: no eye-contact music)
    h_trainerbattle TRAINER_FLANNERY             // (in battle: "Oh... I guess I was trying too hard... you deserve this.")
    h_buffer_player                              // LavaridgeTown_Gym_1F_EventScript_FlanneryDefeated
    SystemMsg 0, 2                               // <player> received the Heat Badge from Flannery.
    h_badge_fanfare                              // Common_EventScript_PlayGymBadgeFanfare
    MsgWinCloseAll
    h_msgbox_actor 1, LG_FLANNERY                // If you have a Heat Badge, all Pokémon up to Level 50 ... Strength ...
    h_closemessage
    h_setflag FLAG_DEFEATED_LAVARIDGE_GYM
    h_givebadge 4                                // setflag FLAG_BADGE04_GET
    h_addvar VAR_PETALBURG_GYM_STATE, 1
    h_goto_if_ne VAR_PETALBURG_GYM_STATE, 6, L_LG_GymTrainers
    h_clearflag FLAG_HIDE_PETALBURG_GYM_GUIDE    // Common_EventScript_ReadyPetalburgGymForBattle
    h_setflag FLAG_PETALBURG_MART_EXPANDED_ITEMS
L_LG_GymTrainers:
    h_set_gym_trainers 4                         // Cole, Axle, Andy, Zane, Sadie count as beaten
    h_setflag FLAG_HIDE_WALLY_WANDAS_HOUSE
    h_setvar VAR_LAVARIDGE_RIVAL_STATE, 1
L_LG_GiveOverheat:                               // LavaridgeTown_Gym_1F_EventScript_GiveOverheat
    h_giveitem ITEM_TM50
    h_goto_if_eq HLIB_RESULT, 0, L_LG_BagFull
    h_msgbox_actor 2, LG_FLANNERY                // That TM50 contains Overheat. ...
    h_setflag FLAG_RECEIVED_TM_OVERHEAT
    h_release
L_LG_BagFull:                                    // Common_EventScript_ShowBagIsFull
    h_msgbox_actor 8, LG_FLANNERY                // Too bad! The Bag is full...
    h_release
L_LG_Rematch:                                    // (already beaten)
    h_goto_if_unset FLAG_RECEIVED_TM_OVERHEAT, L_LG_GiveOverheat
    h_msgbox 3                                   // Your power reminds me of someone... You battle like Norman, ...
    h_release

LG_GymGuide:                                     // LavaridgeTown_Gym_1F_EventScript_GymGuide
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_DEFEATED_LAVARIDGE_GYM, L_LG_GuideVictory
    h_buffer_player
    h_msgbox 4                                   // Hey, how's it going, Champion-bound <player>? ...
    h_release
L_LG_GuideVictory:
    h_msgbox 5                                   // Yow! That was a scorching hot battle!
    h_release

LG_Statue:                                       // the statues (lockall; MSGBOX_DEFAULT)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_badge 4, L_LG_StatueCertified
    h_msgbox_info 6                              // Lavaridge Town Pokémon Gym
    h_closemessage
    h_release
L_LG_StatueCertified:
    h_buffer_player
    h_msgbox_info 7                              // Lavaridge Town Pokémon Gym / Flannery's Certified Trainers: <player>
    h_closemessage
    h_release
    .balign 4, 0

// >>> emerald_rooms lavaridge_warps (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
EL_Hole2:                                  // Emerald warp 2 (10,18) -> LavaridgeTown_Gym_B1F warp 0 (10,18)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 11, 0, 18, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole3:                                  // Emerald warp 3 (8,9) -> LavaridgeTown_Gym_B1F warp 2 (8,9)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 9, 0, 9, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole5:                                  // Emerald warp 5 (5,14) -> LavaridgeTown_Gym_B1F warp 3 (5,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 6, 0, 14, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole6:                                  // Emerald warp 6 (0,17) -> LavaridgeTown_Gym_B1F warp 1 (0,17)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 1, 0, 17, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole7:                                  // Emerald warp 7 (5,9) -> LavaridgeTown_Gym_B1F warp 5 (5,9)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 6, 0, 9, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole8:                                  // Emerald warp 8 (2,15) -> LavaridgeTown_Gym_B1F warp 6 (2,15)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 3, 0, 15, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole9:                                  // Emerald warp 9 (3,14) -> LavaridgeTown_Gym_B1F warp 7 (3,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 4, 0, 14, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole10:                                  // Emerald warp 10 (1,14) -> LavaridgeTown_Gym_B1F warp 8 (1,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 2, 0, 14, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole11:                                  // Emerald warp 11 (0,10) -> LavaridgeTown_Gym_B1F warp 9 (0,10)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 1, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole12:                                  // Emerald warp 12 (3,10) -> LavaridgeTown_Gym_B1F warp 10 (3,10)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 4, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole13:                                  // Emerald warp 13 (0,6) -> LavaridgeTown_Gym_B1F warp 11 (0,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 1, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole15:                                  // Emerald warp 15 (5,6) -> LavaridgeTown_Gym_B1F warp 13 (5,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 6, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole16:                                  // Emerald warp 16 (2,3) -> LavaridgeTown_Gym_B1F warp 14 (2,3)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 3, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole17:                                  // Emerald warp 17 (5,2) -> LavaridgeTown_Gym_B1F warp 15 (5,2)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 6, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole18:                                  // Emerald warp 18 (7,2) -> LavaridgeTown_Gym_B1F warp 16 (7,2)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 8, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole19:                                  // Emerald warp 19 (8,6) -> LavaridgeTown_Gym_B1F warp 17 (8,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 9, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole20:                                  // Emerald warp 20 (10,6) -> LavaridgeTown_Gym_B1F warp 18 (10,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 11, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole22:                                  // Emerald warp 22 (12,3) -> LavaridgeTown_Gym_B1F warp 19 (12,3)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 13, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole23:                                  // Emerald warp 23 (14,6) -> LavaridgeTown_Gym_B1F warp 21 (14,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 15, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Hole25:                                  // Emerald warp 25 (12,12) -> LavaridgeTown_Gym_B1F warp 23 (12,12)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 148, 13, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
#endif
// <<< emerald_rooms lavaridge_warps
