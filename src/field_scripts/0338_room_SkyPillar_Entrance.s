// SkyPillar_Entrance (zone 169): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch13 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch13

    ScriptEntry Script_None
    ScriptEntry Story_SPE_Init   // 2: zone init (0339)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch13, ch13 agent 2026-10-07: Sapphire data/maps/SkyPillar_Entrance/scripts.inc; generators keep everything
// from this line on; entries above marked "// story:"). Sapphire's ON_TRANSITION only sets the landmark flag. Map scripts:
// 0339_room_SkyPillar_Entrance_init.s. The door from Route 131 (the post-game islet) and the climb are the map builders'.
Story_SPE_Init:                         // SkyPillar_Entrance_MapScript1_15F2C3
    h_setflag FLAG_LANDMARK_SKY_PILLAR
    VMHalt
    .balign 4, 0
