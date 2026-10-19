// FallarborTown_BattleTentLobby (zone 520) map scripts (battle_tents): zone init = script 9 (Scott); the ON_FRAME
// table's "challenge status" check = the condition TT_STATE (map-local work 0x4000, 0 after each zone init) 0 -> script 8.
#include "asm/field_script.inc"

    MapScript 2, 9
    MapScriptConditions Conditions_FL
    MapScriptsEnd

Conditions_FL:
    MapScriptCondition 0x4000, 0, 8
    MapScriptConditionsEnd
    .balign 4, 0
