// BattleFrontier_BattlePalaceLobby (zone 466) map scripts (frontier_palace_arena): the ON_FRAME table's "challenge
// status" check = the condition PA_STATE (map-local work 0x4000, 0 after each zone init) 0 -> script 10.
#include "asm/field_script.inc"

    MapScriptConditions Conditions_PL
    MapScriptsEnd

Conditions_PL:
    MapScriptCondition 0x4000, 0, 10
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
