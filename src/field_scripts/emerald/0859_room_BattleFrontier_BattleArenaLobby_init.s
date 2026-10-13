// BattleFrontier_BattleArenaLobby (zone 429) map scripts (frontier_palace_arena): the ON_FRAME table's "challenge
// status" check = the condition PA_STATE (map-local work 0x4000, 0 after each zone init) 0 -> script 8.
#include "asm/field_script.inc"

    MapScriptConditions Conditions_AL
    MapScriptsEnd

Conditions_AL:
    MapScriptCondition 0x4000, 0, 8
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
