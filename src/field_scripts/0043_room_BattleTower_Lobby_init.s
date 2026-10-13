// BattleTower_Lobby (zone 21) map scripts (battle_tower agent, 2026-10-08): Sapphire's ON_RESUME / ON_TRANSITION =
// the zone init (script 9: the award man), ON_FRAME_TABLE VAR_TEMP_0 0 = the condition on BT_STATE (map-local work
// 0x4000, 0 after each zone init and in every save the tower makes) -> script 8 (the challenge's outcome).
#include "asm/field_script.inc"

    MapScript 2, 9
    MapScriptConditions Conditions_BTL
    MapScriptsEnd

Conditions_BTL:
    MapScriptCondition 0x4000, 0, 8
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
