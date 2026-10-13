// SkyPillar_3F (zone 166): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_None
#ifdef HOENN_EMERALD
    ScriptEntry SPF_Init  // 2: zone init (Emerald: the cracked floor after Rayquaza, emerald_ch10)  // story:
#endif
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (Pokémon Emerald NDS, emerald_ch10 2026-10-12; generators keep everything from this line on and the entry above
// marked "// story:"). Emerald only: pokeemerald SkyPillar_3F_OnTransition shows the clean floor while VAR_SKY_PILLAR_STATE < 2
// (until Rayquaza has been to Sootopolis). In an Emerald build the clean floor is this room's variant (SkyPillar_3F_Emerald)
// and Sapphire's cracked room its other layout (data/interiors/emerald/166.json alt_rooms: map replace event 3, shared with
// Mauville Gym, whose zone init sets it too: b2tools/emerald_caves_rooms.py). Map script: src/field_scripts/emerald/
// 0333_room_SkyPillar_3F_init.s (zone init = script 2).
#ifdef HOENN_EMERALD
#include "hoenn_story.inc"
SPF_Init:
    MapReplaceIsEventSet 3, 0x8000
    h_goto_if_ge VAR_SKY_PILLAR_STATE, 2, L_SPF_Cracked
    h_goto_if_eq 0x8000, 0, L_SPF_Done
    MapReplaceSetEvent 3, 0, 1          // the clean floor (the zone's matrix is loaded already: reload it)
    VMHalt
L_SPF_Cracked:
    h_goto_if_eq 0x8000, 1, L_SPF_Done
    MapReplaceSetEvent 3, 1, 1          // Sapphire's cracked floor
L_SPF_Done:
    VMHalt
    .balign 4, 0
#endif
