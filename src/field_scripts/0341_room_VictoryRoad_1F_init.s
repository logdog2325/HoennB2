// Victory Road 1F's map scripts (Sapphire VictoryRoad_1F_MapScripts: ON_TRANSITION -> zone init = script 9 of
// 0340_room_VictoryRoad_1F.s: hides the entrance Wally once he is beaten). Chapter Ch11, ch11 agent 2026-10-07.
// Emerald (2026-10-18): field load / return = script 10 (Emerald's entrance Wally stays standing by the entrance).
// b2tools/patches/interiors.py installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 9
#ifdef HOENN_EMERALD
    MapScript 3, 10                         // Emerald: the entrance Wally's standing spot (2,24) / (3,24) after his battle,
    MapScript 4, 10                         // on every field load and return (pokeemerald's OnTransition setobjectxyperm)
#endif
    MapScriptsEnd
    .balign 4, 0
