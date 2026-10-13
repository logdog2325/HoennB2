// SootopolisCity_Gym_B1F (zone 24): gyms_league (b2tools/gyms_league_rooms.py): step triggers that warp like Sapphire's step-on warp tiles.
// Messages: src/text/script/0030_room_SootopolisCity_Gym_B1F.txt
#include "asm/field_script.inc"

    ScriptEntry Script_1
    ScriptEntriesEnd

Script_1:                                      // Sapphire warp 0 (11,22) -> SootopolisCity_Gym_1F warp 2 (11,22)
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript 10017                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore 23, 12, 0, 22, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
