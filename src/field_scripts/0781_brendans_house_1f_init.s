// Map scripts of brendans house 1f (init file 0781; installed by b2tools/patches/interiors.py).
// Sapphire OnTransition -> MapScript 2 (zone init); OnFrame table -> MapScriptConditions (scene on entering).
// State 3 (moving in) is not here: Littleroot's arrival reserves script 20 directly (the map change needs it).
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 24
    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
    MapScriptCondition VAR_LITTLEROOT_INTRO_STATE, 5, 21
    MapScriptCondition VAR_LITTLEROOT_INTRO_STATE, 6, 22
    MapScriptCondition VAR_LITTLEROOT_HOUSES_STATE, 1, 23
#if __has_include("scenes/players_house_1f_ch13.inc")
    MapScriptCondition VAR_LITTLEROOT_HOUSES_STATE, 3, 30   // chapter Ch13: Dad brings the S.S. Ticket (Sapphire: this var in both houses)
#endif
    MapScriptConditionsEnd
    .balign 4, 0
