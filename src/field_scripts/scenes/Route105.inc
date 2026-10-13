// Route 105's story (Sapphire data/maps/Route105/scripts.inc; chapter Ch6, ch6 agent 2026-10-07). converter/
// gen_map_content.py includes this file twice in the generated zone file 0662_auto_Route105.s: the entries below become
// scripts 1-2, the generated people and signs follow. Map scripts: scenes/Route105_init.inc. The Surf trainers are placed
// by the trainers patch (eye contact), not scripted here.
//
// Sapphire's OnLoad (Route105_MapScript1_14F29E) closes the Island Cave's mouth, (9,19)-(9,20), with rock wall metatiles
// until FLAG_REGI_DOORS_OPENED (the Sealed Chamber, chapter Ch12). Here the mouth's door warp (index 3 of the zone's warps)
// is off the map until then, and a Black 2 rock stands in front of the door (data/story/ch6.json uid 150, hidden by
// the flag: Black 2's own 1x1 rock model 206).
#ifdef SCENE_ENTRIES
    ScriptEntry R105_Init                   // 1: Route105_MapScript1_14F29E (zone init)
    ScriptEntry R105_Rock                   // 2: the rock in the Island Cave's mouth (uid 150): nothing happens
#else
R105_Init:
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_REGI_DOORS_OPENED, L_R105_Open
    ObjInitWarpGPos 3, 0, 0, 0              // the Island Cave's door is sealed (the zone's 4th warp: after the cell's three room doors)
L_R105_Open:
    VMHalt
R105_Rock:
    h_lock
    h_release
    .balign 4, 0
#include "scenes/ch6_test.inc"
#endif
