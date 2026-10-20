// BattleFrontier_ReceptionGate map scripts (frontier_sp 2026-10-20, Emerald only): Emerald's ON_FRAME table = the condition
// RG_W_STATE (map-local work 0x4000, 0 after every map change) 0 -> script 6 of 0906_room_BattleFrontier_ReceptionGate.s
// (the first visit's scene; it sets the work, then plays only while FLAG_HIDE_BATTLE_FRONTIER_RECEPTION_GATE_SCOTT is clear).
#include "asm/field_script.inc"

    MapScriptConditions Conditions_RG
    MapScriptsEnd

Conditions_RG:
    MapScriptCondition 0x4000, 0, 6
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
