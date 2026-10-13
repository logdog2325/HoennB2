// EverGrandeCity_GlaciasRoom's map scripts (Sapphire EverGrandeCity_GlaciasRoom_MapScripts: ON_LOAD / ON_FRAME_TABLE -> zone init = script 3 of
// 0106_room_EverGrandeCity_GlaciasRoom.s; OnFrame VAR_ELITE_4_STATE 2 = script 4: walk in, the entrance closes). The OnWarp turn north
// (VAR_TEMP_1 0) is not needed: the walk-in script walks the player up. Chapter Ch11, ch11 agent 2026-10-07.
// b2tools/patches/interiors.py installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 3
    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
    MapScriptCondition VAR_ELITE_4_STATE, 2, 4
    MapScriptConditionsEnd
    .balign 4, 0
