// Map scripts of ShoalCave_LowTideInnerRoom (zone 146): converter/gen_caves.py (caves_misc). Zone init (MapScript 2) =
// script 4: marks "inside the cave" and keeps the tide. Story map scripts: add a line "// ---- story" (then this file
// is left alone) and add them to the table.
#include "asm/field_script.inc"
#include "hoenn.h"

// ---- story (chapter Ch9, ch9 agent 2026-10-07): the zone init is script 11 of 0292_room_ShoalCave_LowTideInnerRoom.s (the
// two salt piles are hidden at high tide, then it runs the generator's script 4).
    MapScript 2, 11
    MapScriptsEnd
    .balign 4, 0
