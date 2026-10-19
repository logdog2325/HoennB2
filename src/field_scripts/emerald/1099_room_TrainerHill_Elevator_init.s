// TrainerHill_Elevator (zone 549) map scripts (battle_tents): Emerald's ON_FRAME VAR_TEMP_4 0 = the condition work
// 0x4000 (0 after each zone init) 0 -> script 2 (EnterElevator).
#include "asm/field_script.inc"

    MapScriptConditions Conditions_TV
    MapScriptsEnd

Conditions_TV:
    MapScriptCondition 0x4000, 0, 2
    MapScriptConditionsEnd
    .balign 4, 0
