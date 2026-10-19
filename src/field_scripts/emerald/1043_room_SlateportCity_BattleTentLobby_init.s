// SlateportCity_BattleTentLobby (zone 521) map scripts (battle_tents): the ON_FRAME table's "challenge status" check =
// the condition TT_STATE (map-local work 0x4000, 0 after each zone init) 0 -> script 8.
#include "asm/field_script.inc"

    MapScriptConditions Conditions_SL
    MapScriptsEnd

Conditions_SL:
    MapScriptCondition 0x4000, 0, 8
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
