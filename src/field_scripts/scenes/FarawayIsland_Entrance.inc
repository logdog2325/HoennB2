// Faraway Island's beach (Emerald data/maps/FarawayIsland_Entrance/scripts.inc; events agent, 2026-10-07; notes/EVENTS.md).
// Included twice by the generated zone file (zone 158, a warp-only map; the generated sign follows): entries 1-4.
// Text: src/text/scenes/FarawayIsland_Entrance.txt (Emerald's lines, word for word). Story objects: data/story/events.json
// (the ferry sailor uid 101; the S.S. Tidal, object 2, has no Black 2 sprite). You arrive with the Old Sea Map from
// Lilycove's harbor (scenes/LilycoveCity_Harbor_Ch13.inc). Emerald's three weather triggers (SetCloudsWeather /
// ClearWeather at (9,18), (10,20), (22,9): sunny clouds over the forest) are not ported: Black 2 has no cloud weather.
#ifdef SCENE_ENTRIES
    ScriptEntry FE_Arrive               // 1: the ferry's landing (reserved by Lilycove's harbor: EV_ARRIVE_SCRIPT)
    ScriptEntry FE_Init                 // 2: FarawayIsland_Entrance_OnTransition (zone init)
    ScriptEntry FE_Sailor               // 3: FarawayIsland_Entrance_EventScript_Sailor
    ScriptEntry FE_Sign                 // 4: FarawayIsland_Entrance_EventScript_Sign, sign (3,32)
#else
#include "scenes/events_lib.inc"
#define FE_SAILOR 101

FE_Arrive:                              // warp MAP_FARAWAY_ISLAND_ENTRANCE, 13, 38: facing the sailor at (13,39)
    ch2_land
    h_release

FE_Init:                                // FarawayIsland_Entrance_OnTransition
    h_setflag FLAG_ARRIVED_ON_FARAWAY_ISLAND
    VMHalt

FE_Sailor:                              // FarawayIsland_Entrance_EventScript_Sailor
    ev_island_sailor FE_SAILOR, 0, 1, 2 // Capt. Briney can be so maddeningly fickle... Do you want to return to Lilycove?

FE_Sign:                                // FarawayIsland_Entrance_EventScript_Sign (MSGBOX_SIGN)
    h_msgbox_sign 3
#endif
