// Navel Rock, outside (Emerald data/maps/NavelRock_Exterior + NavelRock_Harbor's sailor; events agent, 2026-10-07;
// notes/EVENTS.md). Included twice by the generated zone file (zone 232, a warp-only map): entries 1-2. Text:
// src/text/scenes/NavelRock_Exterior.txt. The ferry sailor: data/story/events.json (uid 101). The harbour room
// (NavelRock_Harbor) is not built: the ferry docks at the dock's end (10,18), where Emerald's harbour door is.
// The cave (NavelRock_Entrance ... NavelRock_Bottom, NavelRock_Top) is Emerald's: data/cave_layouts/NavelRock_*.json.
#ifdef SCENE_ENTRIES
    ScriptEntry NE_Arrive               // 1: the ferry's landing (reserved by Lilycove's harbor: EV_ARRIVE_SCRIPT)
    ScriptEntry NE_Sailor               // 2: NavelRock_Harbor_EventScript_Sailor
#else
#include "scenes/events_lib.inc"
#define NE_SAILOR 101

NE_Arrive:                              // warp MAP_NAVEL_ROCK_HARBOR, 8, 4 -> the dock's end (10,17), facing the sailor
    ch2_land
    h_release

NE_Sailor:                              // NavelRock_Harbor_EventScript_Sailor
    ev_island_sailor NE_SAILOR, 0, 1, 2 // Did... Did you hear that? ... Do you think we should leave?
#endif
