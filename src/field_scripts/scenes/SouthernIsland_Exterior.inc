// Southern Island Exterior's story (Sapphire data/maps/SouthernIsland_Exterior/scripts.inc; chapter Ch13, ch13 agent
// 2026-10-07). Included twice by the generated zone file (zone 111, a standalone map; the generated sign follows): the
// entries below become scripts 1-3. Text: src/text/scenes/SouthernIsland_Exterior.txt (lines 0-2). Story objects: the
// ferry sailor (uid 101, data/story/ch13.json; the S.S. Tidal, object 2, has no Black 2 sprite). Map scripts:
// scenes/SouthernIsland_Exterior_init.inc. You get here with the Eon Ticket from Lilycove's harbor (scenes/
// LilycoveCity_Harbor_Ch13.inc).
#ifdef SCENE_ENTRIES
    ScriptEntry SI_Init                 // 1: SouthernIsland_Exterior_MapScript1_160ADC (zone init)
    ScriptEntry SI_Sailor               // 2: SouthernIsland_Exterior_EventScript_160AE0
    ScriptEntry SI_Arrive               // 3: the landing of the ferry (reserved by Lilycove's harbor)
#else
#include "scenes/ch13_lib.inc"
#define SI_SAILOR 101
#define SI_LILYCOVE_ZONE 203            // LilycoveCity_Harbor (room origin (1, -2))

SI_Init:                                // SouthernIsland_Exterior_MapScript1_160ADC
    h_setflag FLAG_LANDMARK_SOUTHERN_ISLAND
    VMHalt

SI_Sailor:                              // SouthernIsland_Exterior_EventScript_160AE0
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_yesno 0, HLIB_TMP                 // Aye, mate, there's nothing here to see or do on this forgettable island. ...sail back to Lilycove?
    h_goto_if_no HLIB_TMP, L_SI_Stay
    h_msgbox 1                          // Aye, right, then! Sail home we will!
    ch13_board_island SI_SAILOR
    h_sail_ferry SI_LILYCOVE_ZONE, 8 + 1, 11 - 2, 0, 6     // warp MAP_LILYCOVE_CITY_HARBOR, 255, 8, 11 (script 6 of the room file)
    h_release
L_SI_Stay:
    h_msgbox 2                          // Aye, right, as you like, then.
    h_release

SI_Arrive:                              // the player stands at (13,22), facing the sailor at (13,23)
    ch2_land
    h_release
#endif
