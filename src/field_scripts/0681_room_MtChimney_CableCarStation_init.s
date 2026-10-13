// MtChimney_CableCarStation's map scripts (Sapphire MtChimney_CableCarStation_MapScripts: ON_TRANSITION -> zone init = script 4 of
// 0680_room_MtChimney_CableCarStation.s; ON_FRAME_TABLE VAR_CABLE_CAR_STATION_STATE 1 = script 3, the arrival:
// the ride reserves it with RTReserveScript, Black 2's way to start a scene on a scripted warp). Chapter Ch5,
// ch5 2026-10-07. b2tools/patches/interiors.py installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 4
    MapScriptsEnd
    .balign 4, 0
