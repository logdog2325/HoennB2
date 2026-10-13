// TerraCave_End's map scripts (zone 366, Emerald; emerald_ch12_13 2026-10-12): the zone init = script 3 of 0732_room_TerraCave_End.s
// (TerraCave_End_OnTransition: Groudon there while not caught / beaten) and the abnormal weather's cave rule (global
// AW_GLOBAL_CAVE_INIT, scenes/emerald/abnormal_weather.inc: its 1000 steps over in here = its end pending).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "scenes/emerald/abnormal_weather.inc"

    MapScript 2, 3
    MapScript 2, AW_GLOBAL_CAVE_INIT
    MapScriptsEnd
    .balign 4, 0
