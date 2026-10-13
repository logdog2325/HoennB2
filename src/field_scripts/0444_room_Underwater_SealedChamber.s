// Underwater_SealedChamber (zone 222): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_1
    ScriptEntry Story_US_GoUp   // 2: braille (12,43)  // story:
    ScriptEntriesEnd

Script_1:                                      // field load / return: the underwater effect (Abyssal Ruins script plugin, b2tools/patches/dive.py lists this zone)
    AbyssalRuinsCmd_StartUnderwaterEffect
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12, ch6 agent: Sapphire data/maps/Underwater_SealedChamber/scripts.inc; generators keep everything
// from this line on). The braille on the sea floor (data/story/ch12.json, (12,43)): shown as plain text. The dive warps
// (ON_DIVE_WARP) are the dive patch's. Text: 0281_room_Underwater_SealedChamber.txt.
Story_US_GoUp:                              // Underwater_SealedChamber_EventScript_15F0B8
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info 0                         // Go up here.
    h_closemessage
    h_release
    .balign 4, 0
