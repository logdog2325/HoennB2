// Route 131's story (Sapphire data/maps/Route131/scripts.inc). converter/gen_map_content.py includes this file twice
// in the generated zone file 0888_auto_Route131.s: the entry below becomes script 1, the generated people follow.
// Map scripts: scenes/Route131_init.inc.
//
// Sapphire's OnTransition (Route131_MapScript1_152444) swaps in layout 320 (the Sky Pillar islet with its cave door,
// (36,6)) once FLAG_SYS_GAME_CLEAR is set. Here the islet's cells are Black 2 map replacements (b2tools/world.py
// build_alts, data/hoenn_world.json "alt_layouts", patches/hoenn_world.py): their chunks replace Route 131's while
// map replace event 7 is set (work 0x4038 == 0x408, data/story_ids.json WORK_MAP_REPLACE_7_SKY_PILLAR). Black 2
// patches a matrix when it loads (ov035 event_mapchange.c FieldMapControl_LoadZone -> MapMatrix_Patch), so the
// game-clear scene must run `MapReplaceSetEvent 7, 1, 0` where it sets FLAG_SYS_GAME_CLEAR; this zone init does the
// same (and reloads the matrix, as Shoal Cave's tide) when the player comes into Route 131 by a warp.
#ifdef SCENE_ENTRIES
    ScriptEntry Story_Init          // 1: Route131_MapScript1_152444 (zone init)
#else
#define R131_MAP_REPLACE_SKY_PILLAR 7

Story_Init:
#ifdef HOENN_TEST_GAME_CLEAR
    FlagSet FLAG_SYS_GAME_CLEAR     // TEST ONLY (HOENN_TEST_GAME_CLEAR=1): as if the game were cleared
#endif
#ifndef HOENN_EMERALD
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_R131_Done
#endif                                  // Emerald (emerald_ch10, 2026-10-12): Route131_OnTransition swaps in LAYOUT_ROUTE131_SKY_PILLAR
    MapReplaceIsEventSet R131_MAP_REPLACE_SKY_PILLAR, 0x8000   // always: the Sky Pillar is part of the story (Route 103's
                                        // zone init takes event 7 off again before the game is clear: Route103_AlteringCave.inc)
    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_R131_Done
    MapReplaceSetEvent R131_MAP_REPLACE_SKY_PILLAR, 1, 1
L_R131_Done:
    VMHalt
#endif
