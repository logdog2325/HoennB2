// BattleFrontier_BattleFactoryLobby (zone 408) map scripts (frontier_factory_dome): the ON_FRAME table's
// "challenge status" check = the condition FD_STATE (map-local work 0x4000, 0 after each zone init) 0 -> script 8.
#include "asm/field_script.inc"

    MapScriptConditions Conditions_FL
    MapScriptsEnd

Conditions_FL:
    MapScriptCondition 0x4000, 0, 8
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
