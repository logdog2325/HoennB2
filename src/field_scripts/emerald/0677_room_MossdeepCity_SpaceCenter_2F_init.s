// Map scripts of MossdeepCity_SpaceCenter_2F (zone 338), EMERALD ONLY (emerald_ch9_mirage 2026-10-12): pokeemerald's ON_TRANSITION (MoveCivilians,
// MoveDefeatedGrunts) = zone init = script 10 of 0676_room_MossdeepCity_SpaceCenter_2F.s; its ON_FRAME_TABLE (VAR_MOSSDEEP_SPACE_CENTER_STATE 1:
// the three grunts at the top of the stairs) = script 11.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 10
    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
    MapScriptCondition VAR_MOSSDEEP_SPACE_CENTER_STATE, 1, 11
    MapScriptConditionsEnd
    .balign 4, 0
