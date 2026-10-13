// BattleFrontier_BattleDomeLobby (zone 411) map scripts (frontier_factory_dome): zone init -> script 10 (test builds'
// party only); the ON_FRAME table's challenge-status check = the condition FD_STATE (map-local work 0x4000) 0 -> script 9.
#include "asm/field_script.inc"

    MapScript 2, 10
    MapScriptConditions Conditions_DL
    MapScriptsEnd

Conditions_DL:
    MapScriptCondition 0x4000, 0, 9
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
