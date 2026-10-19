// TrainerHill_Entrance (zone 543) map scripts (battle_tents): zone init = script 9 (TH_ACTIVE, work 0x4001, for the
// counter trigger); the ON_FRAME table's ExitChallenge = the condition TH_STATE (work 0x4000, 0 after each zone init) 0
// -> script 8.
#include "asm/field_script.inc"

    MapScript 2, 9
    MapScriptConditions Conditions_TE
    MapScriptsEnd

Conditions_TE:
    MapScriptCondition 0x4000, 0, 8
    MapScriptConditionsEnd
    .balign 4, 0
