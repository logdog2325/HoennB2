// Champion's room map scripts (Sapphire EverGrandeCity_ChampionsRoom_MapScripts: ON_TRANSITION -> zone init = script 2 of
// 0068_room_EverGrandeCity_ChampionsRoom.s; OnFrame VAR_TEMP_1 0 = script 3: Steven, the rival, Birch, the Hall of Fame).
// The OnWarp turn north is not needed: the scene walks the player up. Chapter Ch11, ch11 agent 2026-10-07.
// b2tools/patches/interiors.py installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 2
    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
    MapScriptCondition 0x4001, 0, 3             // VAR_TEMP_1 0
    MapScriptConditionsEnd
    .balign 4, 0
