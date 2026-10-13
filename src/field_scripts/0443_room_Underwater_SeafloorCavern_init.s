// Map scripts of Underwater_SeafloorCavern (zone 221): converter/gen_caves.py (dive agent). Field load (MapScript 3) and
// return (MapScript 4) = script 1: the underwater effect, as Black 2's Abyssal Ruins (0483.s). Chapter Ch10 added the zone init
// (= script 2: Sapphire's ON_TRANSITION). ---- story
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 2
    MapScript 3, 1
    MapScript 4, 1
    MapScriptsEnd
    .balign 4, 0
