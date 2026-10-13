// LavaridgeTown_Gym_B1F (zone 148): gyms_league (b2tools/gyms_league_rooms.py): step triggers that warp like Sapphire's step-on warp tiles.
// Messages: src/text/script/0167_room_LavaridgeTown_Gym_B1F.txt
#include "asm/field_script.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
// >>> emerald_rooms lavaridge_entries (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
    ScriptEntry EL_Vent0            // 7: Emerald warp 0 (10,18) -> LavaridgeTown_Gym_1F warp 2 (10,18)
    ScriptEntry EL_Vent1            // 8: Emerald warp 1 (0,17) -> LavaridgeTown_Gym_1F warp 6 (0,17)
    ScriptEntry EL_Vent2            // 9: Emerald warp 2 (8,9) -> LavaridgeTown_Gym_1F warp 3 (8,9)
    ScriptEntry EL_Vent3            // 10: Emerald warp 3 (5,14) -> LavaridgeTown_Gym_1F warp 5 (5,14)
    ScriptEntry EL_Vent4            // 11: Emerald warp 4 (4,18) -> LavaridgeTown_Gym_1F warp 4 (4,18)
    ScriptEntry EL_Vent8            // 12: Emerald warp 8 (1,14) -> LavaridgeTown_Gym_1F warp 10 (1,14)
    ScriptEntry EL_Vent9            // 13: Emerald warp 9 (0,10) -> LavaridgeTown_Gym_1F warp 11 (0,10)
    ScriptEntry EL_Vent11           // 14: Emerald warp 11 (0,6) -> LavaridgeTown_Gym_1F warp 13 (0,6)
    ScriptEntry EL_Vent12           // 15: Emerald warp 12 (3,6) -> LavaridgeTown_Gym_1F warp 14 (3,6)
    ScriptEntry EL_Vent14           // 16: Emerald warp 14 (2,3) -> LavaridgeTown_Gym_1F warp 16 (2,3)
    ScriptEntry EL_Vent16           // 17: Emerald warp 16 (7,2) -> LavaridgeTown_Gym_1F warp 18 (7,2)
    ScriptEntry EL_Vent19           // 18: Emerald warp 19 (12,3) -> LavaridgeTown_Gym_1F warp 22 (12,3)
    ScriptEntry EL_Vent20           // 19: Emerald warp 20 (4,16) -> LavaridgeTown_Gym_1F warp 21 (4,16)
    ScriptEntry EL_Vent22           // 20: Emerald warp 22 (13,17) -> LavaridgeTown_Gym_1F warp 24 (13,17)
    ScriptEntry EL_Vent23           // 21: Emerald warp 23 (12,12) -> LavaridgeTown_Gym_1F warp 25 (12,12)
#endif
// <<< emerald_rooms lavaridge_entries
    ScriptEntriesEnd

Script_1:                                      // Sapphire warp 0 (3,21) -> LavaridgeTown_Gym_1F warp 2 (3,21)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 4, 0, 22, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // Sapphire warp 1 (9,2) -> LavaridgeTown_Gym_1F warp 6 (9,2)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 10, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // Sapphire warp 2 (1,14) -> LavaridgeTown_Gym_1F warp 3 (1,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 2, 0, 15, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // Sapphire warp 3 (1,6) -> LavaridgeTown_Gym_1F warp 5 (1,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 2, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // Sapphire warp 4 (6,14) -> LavaridgeTown_Gym_1F warp 4 (6,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 7, 0, 15, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                      // Sapphire warp 5 (6,20) -> LavaridgeTown_Gym_1F warp 7 (6,20)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 7, 0, 21, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0

// ---- story (emerald_rooms: the Emerald build's own scripts below; generators keep everything from this line on)

// >>> emerald_rooms lavaridge_warps (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
EL_Vent0:                                  // Emerald warp 0 (10,18) -> LavaridgeTown_Gym_1F warp 2 (10,18)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 11, 0, 18, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent1:                                  // Emerald warp 1 (0,17) -> LavaridgeTown_Gym_1F warp 6 (0,17)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 1, 0, 17, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent2:                                  // Emerald warp 2 (8,9) -> LavaridgeTown_Gym_1F warp 3 (8,9)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 9, 0, 9, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent3:                                  // Emerald warp 3 (5,14) -> LavaridgeTown_Gym_1F warp 5 (5,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 6, 0, 14, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent4:                                  // Emerald warp 4 (4,18) -> LavaridgeTown_Gym_1F warp 4 (4,18)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 5, 0, 18, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent8:                                  // Emerald warp 8 (1,14) -> LavaridgeTown_Gym_1F warp 10 (1,14)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 2, 0, 14, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent9:                                  // Emerald warp 9 (0,10) -> LavaridgeTown_Gym_1F warp 11 (0,10)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 1, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent11:                                  // Emerald warp 11 (0,6) -> LavaridgeTown_Gym_1F warp 13 (0,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 1, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent12:                                  // Emerald warp 12 (3,6) -> LavaridgeTown_Gym_1F warp 14 (3,6)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 4, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent14:                                  // Emerald warp 14 (2,3) -> LavaridgeTown_Gym_1F warp 16 (2,3)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 3, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent16:                                  // Emerald warp 16 (7,2) -> LavaridgeTown_Gym_1F warp 18 (7,2)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 8, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent19:                                  // Emerald warp 19 (12,3) -> LavaridgeTown_Gym_1F warp 22 (12,3)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 13, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent20:                                  // Emerald warp 20 (4,16) -> LavaridgeTown_Gym_1F warp 21 (4,16)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 5, 0, 16, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent22:                                  // Emerald warp 22 (13,17) -> LavaridgeTown_Gym_1F warp 24 (13,17)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 14, 0, 17, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Vent23:                                  // Emerald warp 23 (12,12) -> LavaridgeTown_Gym_1F warp 25 (12,12)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 145, 13, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
#endif
// <<< emerald_rooms lavaridge_warps
