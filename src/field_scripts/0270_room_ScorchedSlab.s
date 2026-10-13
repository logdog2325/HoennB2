// ScorchedSlab (zone 135): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"  // ch7

    ScriptEntry Script_None
    ScriptEntry SS_Init  // 2: ScorchedSlab_MapScript1_15F2A3 (zone init)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch7, ch7 agent 2026-10-07; Sapphire data/maps/ScorchedSlab/scripts.inc: only the ON_TRANSITION landmark
// flag; the item ball (TM11) is placed by converter/gen_items.py). Script 2 = the zone init of 0271_room_ScorchedSlab_init.s.
SS_Init:
    h_setflag FLAG_LANDMARK_SCORCHED_SLAB
    VMHalt
    .balign 4, 0
