// Underwater_SeafloorCavern (zone 221): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch10
#include "hoenn_key_items.h"  // ch10
#include "hoenn_story.inc"  // ch10

    ScriptEntry Script_1
    ScriptEntry UW_Init  // 2: zone init (Underwater_SeafloorCavern_MapScript1_15D9AE: FLAG_LANDMARK_SEAFLOOR_CAVERN, the submarine's interaction)  // story:
    ScriptEntry UW_Submarine  // 3: signs (5..8,4) (Underwater_SeafloorCavern_EventScript_15DA3F)  // story:
    ScriptEntriesEnd

Script_1:                                      // field load / return: the underwater effect (Abyssal Ruins script plugin, b2tools/patches/dive.py lists this zone)
    AbyssalRuinsCmd_StartUnderwaterEffect
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch10, ch10 agent 2026-10-07; Sapphire data/maps/Underwater_SeafloorCavern/scripts.inc; generators keep everything from
// this line on; entries above marked "// story:"). Messages: 0280_room_Underwater_SeafloorCavern.txt
// The stolen submarine "Submarine Explorer 1" (Sapphire: four invisible objects on the hull tiles (5..8,4), hidden by FLAG_HIDE_UNDERWATER_SUBMARINE_INTERACTION once the legend escaped, when the submarine's tiles turn into rock) is four signs on those tiles whose script checks the flag. Black 2 gaps: the submarine is not drawn (the underwater room is built from Sapphire's walkable tiles) and the rock wall after the legend escaped (setmetatile) is not swapped.
#include "scenes/ch10_lib.inc"
#define T_SubmarineExplorer1 0
UW_Init:                                // Underwater_SeafloorCavern_MapScript1_15D9AE
    h_setflag FLAG_LANDMARK_SEAFLOOR_CAVERN
    h_goto_if_unset FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, L_UW_InitDone
    h_setflag FLAG_HIDE_UNDERWATER_SUBMARINE_INTERACTION
L_UW_InitDone:
    VMHalt

UW_Submarine:                           // Underwater_SeafloorCavern_EventScript_15DA3F
    c10_lock
    h_goto_if_set FLAG_HIDE_UNDERWATER_SUBMARINE_INTERACTION, L_UW_Gone
    h_msgbox_info T_SubmarineExplorer1  // "Submarine Explorer 1" is painted on the hull. This is the submarine Team Aqua stole in Slateport! ...
    h_closemessage
L_UW_Gone:
    h_release
    .balign 4, 0
