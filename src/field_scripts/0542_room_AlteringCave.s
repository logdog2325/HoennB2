// AlteringCave (zone 271): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Story_AC_Init        // story: 1: zone init (Emerald AlteringCave_OnTransition)
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (postgame_maps 2026-10-07: Emerald data/maps/AlteringCave/scripts.inc). Zone init of zone 271 and of its eight
// copies (data/interiors/271.json "variants": the same entity file, so the same map scripts; 0543_room_AlteringCave_init.s):
// Emerald's OnTransition sets FLAG_LANDMARK_ALTERING_CAVE. Here the flag also starts the cave's daily table rotation
// (src/field_scripts/scenes/Route103_AlteringCave.inc): Zubat (Emerald's own table) on the first visit, then the next of
// Emerald's nine tables each new day.
Story_AC_Init:
    FlagSet FLAG_LANDMARK_ALTERING_CAVE
    VMHalt
    .balign 4, 0
