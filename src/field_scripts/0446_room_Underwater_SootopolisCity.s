// Underwater_SootopolisCity (zone 223): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntriesEnd

Script_1:                                      // field load / return: the underwater effect (Abyssal Ruins script plugin, b2tools/patches/dive.py lists this zone)
    AbyssalRuinsCmd_StartUnderwaterEffect
    VMHalt
    .balign 4, 0
