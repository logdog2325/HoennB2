// BattleFrontier_BattlePikeRoomFinal map scripts (frontier_pike, Emerald only): Emerald's ON_FRAME table = the condition PK_W_STATE (map-local work
// 0x4000, 0 after every map change) 0 -> script 1 (the room's scene, run once per visit).
#include "asm/field_script.inc"

    MapScriptConditions Conditions_PK
    MapScriptsEnd

Conditions_PK:
    MapScriptCondition 0x4000, 0, 1
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
