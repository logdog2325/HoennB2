// Map scripts of PetalburgCity_Gym (zone 452; installed by b2tools/patches/interiors.py), chapter Ch1:
// Sapphire OnTransition -> MapScript 2 (zone init) = script 2; OnFrame VAR_PETALBURG_GYM_STATE 1 -> script 3 (the
// return from Wally's tutorial). OnWarp (turn the player north) is the warp's own direction (Petalburg's script 2).
// OnLoad (the rooms' doors) belongs to chapter Ch6.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 2
    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
    MapScriptCondition VAR_PETALBURG_GYM_STATE, 1, 3
    MapScriptConditionsEnd
    .balign 4, 0
