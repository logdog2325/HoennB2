// FieryPath (zone 117): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch4
#include "hoenn_story.inc"  // ch4
#include "scenes/ch4_lib.inc"  // ch4

    ScriptEntry Script_None
    ScriptEntry FP_Init                 // 2: FieryPath_OnTransition (zone init, 0235_room_FieryPath_init.s)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch4, ch4 agent 2026-10-07: Sapphire data/maps/FieryPath/scripts.inc; the cave builder leaves this part alone).
FP_Init:                                    // FieryPath_MapScript1_15D31E
    h_setflag FLAG_LANDMARK_FIERY_PATH
    VMHalt
    .balign 4, 0
