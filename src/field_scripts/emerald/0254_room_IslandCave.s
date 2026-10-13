// IslandCave (zone 127), Emerald build only (emerald_ch12_13, 2026-10-12): the Sapphire room's scripts
// (src/field_scripts/0254_room_IslandCave.s, chapter Ch12 by the ch6 agent: cave_builder's head + its story) with
// Emerald's puzzle (the lap). The room, its braille signs, Regice and the door are Sapphire's (data/story/ch12.json;
// Emerald's map is the same); the lap's step triggers are data/story/emerald/e_ch12.json. Story script numbers 1-5 are
// the shared file's; 6-42 are Emerald's.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_IC_Regice   // 2: object 1 (Regice)  // story:
    ScriptEntry Story_IC_Braille   // 3: braille (8,20)  // story:
    ScriptEntry Story_IC_BrailleSide   // 4: braille (7,20) (9,20)  // story:
    ScriptEntry Story_IC_Init   // 5: zone init (0255)  // story:
    ScriptEntry IC_OffPath   // 6: step triggers on the floor inside the lap: off the wall  // story:
    ScriptEntry IC_Path0   // 7: step trigger (4, 21): lap tile 0 (sRegicePathCoords[0])  // story:
    ScriptEntry IC_Path1   // 8: step trigger (5, 21): lap tile 1 (sRegicePathCoords[1])  // story:
    ScriptEntry IC_Path2   // 9: step trigger (6, 21): lap tile 2 (sRegicePathCoords[2])  // story:
    ScriptEntry IC_Path3   // 10: step trigger (7, 21): lap tile 3 (sRegicePathCoords[3])  // story:
    ScriptEntry IC_Path4   // 11: step trigger (8, 21): lap tile 4 (sRegicePathCoords[4])  // story:
    ScriptEntry IC_Path5   // 12: step trigger (9, 21): lap tile 5 (sRegicePathCoords[5])  // story:
    ScriptEntry IC_Path6   // 13: step trigger (10, 21): lap tile 6 (sRegicePathCoords[6])  // story:
    ScriptEntry IC_Path7   // 14: step trigger (11, 21): lap tile 7 (sRegicePathCoords[7])  // story:
    ScriptEntry IC_Path8   // 15: step trigger (12, 21): lap tile 8 (sRegicePathCoords[8])  // story:
    ScriptEntry IC_Path9   // 16: step trigger (12, 22): lap tile 9 (sRegicePathCoords[9])  // story:
    ScriptEntry IC_Path10   // 17: step trigger (12, 23): lap tile 10 (sRegicePathCoords[10])  // story:
    ScriptEntry IC_Path11   // 18: step trigger (13, 23): lap tile 11 (sRegicePathCoords[11])  // story:
    ScriptEntry IC_Path12   // 19: step trigger (13, 24): lap tile 12 (sRegicePathCoords[12])  // story:
    ScriptEntry IC_Path13   // 20: step trigger (13, 25): lap tile 13 (sRegicePathCoords[13])  // story:
    ScriptEntry IC_Path14   // 21: step trigger (13, 26): lap tile 14 (sRegicePathCoords[14])  // story:
    ScriptEntry IC_Path15   // 22: step trigger (13, 27): lap tile 15 (sRegicePathCoords[15])  // story:
    ScriptEntry IC_Path16   // 23: step trigger (12, 27): lap tile 16 (sRegicePathCoords[16])  // story:
    ScriptEntry IC_Path17   // 24: step trigger (12, 28): lap tile 17 (sRegicePathCoords[17])  // story:
    ScriptEntry IC_Path18   // 25: step trigger (4, 29): lap tile 18 (sRegicePathCoords[18])  // story:
    ScriptEntry IC_Path19   // 26: step trigger (5, 29): lap tile 19 (sRegicePathCoords[19])  // story:
    ScriptEntry IC_Path20   // 27: step trigger (6, 29): lap tile 20 (sRegicePathCoords[20])  // story:
    ScriptEntry IC_Path21   // 28: step trigger (7, 29): lap tile 21 (sRegicePathCoords[21])  // story:
    ScriptEntry IC_Path22   // 29: step trigger (8, 29): lap tile 22 (sRegicePathCoords[22])  // story:
    ScriptEntry IC_Path23   // 30: step trigger (9, 29): lap tile 23 (sRegicePathCoords[23])  // story:
    ScriptEntry IC_Path24   // 31: step trigger (10, 29): lap tile 24 (sRegicePathCoords[24])  // story:
    ScriptEntry IC_Path25   // 32: step trigger (11, 29): lap tile 25 (sRegicePathCoords[25])  // story:
    ScriptEntry IC_Path26   // 33: step trigger (12, 29): lap tile 26 (sRegicePathCoords[26])  // story:
    ScriptEntry IC_Path27   // 34: step trigger (4, 28): lap tile 27 (sRegicePathCoords[27])  // story:
    ScriptEntry IC_Path28   // 35: step trigger (4, 27): lap tile 28 (sRegicePathCoords[28])  // story:
    ScriptEntry IC_Path29   // 36: step trigger (3, 27): lap tile 29 (sRegicePathCoords[29])  // story:
    ScriptEntry IC_Path30   // 37: step trigger (3, 26): lap tile 30 (sRegicePathCoords[30])  // story:
    ScriptEntry IC_Path31   // 38: step trigger (3, 25): lap tile 31 (sRegicePathCoords[31])  // story:
    ScriptEntry IC_Path32   // 39: step trigger (3, 24): lap tile 32 (sRegicePathCoords[32])  // story:
    ScriptEntry IC_Path33   // 40: step trigger (3, 23): lap tile 33 (sRegicePathCoords[33])  // story:
    ScriptEntry IC_Path34   // 41: step trigger (4, 23): lap tile 34 (sRegicePathCoords[34])  // story:
    ScriptEntry IC_Path35   // 42: step trigger (4, 22): lap tile 35 (sRegicePathCoords[35])  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12; Emerald: pokeemerald data/maps/IslandCave/scripts.inc + src/braille_puzzles.c
// ShouldDoBrailleRegicePuzzle). Regice (data/story/ch12.json, uid 1, FLAG_HIDE_REGICE), the braille signs, the lap.
// Emerald: reading the braille ("Stay close to the wall. Run around one lap.") starts the puzzle (FLAG_TEMP_REGICE_PUZZLE_
// STARTED) and marks the tile you stand on; every step then marks one of the 36 tiles along the wall (sRegicePathCoords,
// bits in VAR_REGICE_STEPS_1-3); a step anywhere else fails it (FLAG_TEMP_REGICE_PUZZLE_FAILED: read the braille again,
// the marks are cleared); back on (8,21) with all 36 marked, the door (8,20) opens (FLAG_SYS_BRAILLE_REGICE_COMPLETED =
// this port's FLAG_SYS_BRAILLE_WAIT id, Emerald's flag in its place). Here: zone-local works (cleared on every map
// change, as Emerald's TEMP flags; Emerald clears its step vars on entering the cave) IC_STATE (0 = not started or
// failed, 1 = started, 2 = solved) and IC_STEPS_0-2 (12 lap tiles each, bit i % 12 of IC_STEPS_(i / 12)); the step
// triggers fire only while IC_STATE is 1: one per lap tile (scripts 7-42, which marks it; tile 4 = (8,21) also checks the
// lap) and three rectangles over the floor inside the lap (script 6: failed). The door's warp (index 1) is off the map
// until it opens. Text: src/text/script/emerald/0146_room_IslandCave.txt (Emerald's braille).
#include "scenes/ch12_lib.inc"
#define FLAG_SYS_BRAILLE_REGICE_COMPLETED FLAG_SYS_BRAILLE_WAIT
#define T_BRAILLE 0
#define T_BIGHOLE 1
#define IC_DOOR_WARP 1
#define IC_STATE 0x4001                 // (data/story/emerald/e_ch12.json: the triggers' work)
#define IC_STEPS_0 0x4002
#define IC_STEPS_1 0x4003
#define IC_STEPS_2 0x4004
#define IC_PX 0x8038                    // (scratch works)
#define IC_PZ 0x8039

Story_IC_Regice:                            // IslandCave_EventScript_Regice (Regice Lv 40)
    h_regi_battle SPECIES_REGICE, FLAG_HIDE_REGICE, 1
Story_IC_Braille:                           // IslandCave_EventScript_CaveEntranceMiddle (read from (8,21) = lap tile 4)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_BRAILLE_REGICE_COMPLETED, L_IC_BigHole
    VMCall L_IC_ClearIfFailed
    h_msgbox_info T_BRAILLE                 // braillemsgbox IslandCave_Braille_RunLapAroundWall
    h_closemessage
    WorkSetConst IC_STATE, 1                // setflag FLAG_TEMP_REGICE_PUZZLE_STARTED
    WorkOr IC_STEPS_0, 0x10                 // special ShouldDoBrailleRegicePuzzle: the tile you stand on
    h_release
L_IC_BigHole:
    h_msgbox_info T_BIGHOLE                 // gText_BigHoleInTheWall
    h_closemessage
    h_release
Story_IC_BrailleSide:                       // IslandCave_EventScript_CaveEntranceSide: read from (7,21) = lap tile 3 or
    h_lock                                  // (9,21) = lap tile 5 (the room's origin is (0,0): its tiles are the zone's)
    SEPlay SEQ_SE_MESSAGE
    VMCall L_IC_ClearIfFailed
    h_msgbox_info T_BRAILLE                 // braillemsgbox IslandCave_Braille_RunLapAroundWall
    h_closemessage
    h_goto_if_set FLAG_SYS_BRAILLE_REGICE_COMPLETED, L_IC_SideDone
    WorkSetConst IC_STATE, 1                // setflag FLAG_TEMP_REGICE_PUZZLE_STARTED
    PlayerGetGPos IC_PX, IC_PZ              // special ShouldDoBrailleRegicePuzzle: the tile you stand on
    h_goto_if_eq IC_PX, 7, L_IC_SideLeft
    WorkOr IC_STEPS_0, 0x20                 // (9,21)
    VMJump L_IC_SideDone
L_IC_SideLeft:
    WorkOr IC_STEPS_0, 0x8                  // (7,21)
L_IC_SideDone:
    h_release
L_IC_ClearIfFailed:                         // call_if_set FLAG_TEMP_REGICE_PUZZLE_FAILED, IslandCave_EventScript_ClearSteps
    h_goto_if_ne IC_STATE, 0, L_IC_KeepSteps    // (not started yet: the works are 0 since the map loaded)
    WorkSetConst IC_STEPS_0, 0
    WorkSetConst IC_STEPS_1, 0
    WorkSetConst IC_STEPS_2, 0
L_IC_KeepSteps:
    VMReturn
IC_OffPath:                                 // a step off the lap: FlagSet(FAILED), FlagClear(STARTED)
    WorkSetConst IC_STATE, 0
    VMHalt
IC_Path0:
    WorkOr IC_STEPS_0, 0x1
    VMJump L_IC_PathDone
IC_Path1:
    WorkOr IC_STEPS_0, 0x2
    VMJump L_IC_PathDone
IC_Path2:
    WorkOr IC_STEPS_0, 0x4
    VMJump L_IC_PathDone
IC_Path3:
    WorkOr IC_STEPS_0, 0x8
    VMJump L_IC_PathDone
IC_Path4:
    WorkOr IC_STEPS_0, 0x10
    VMJump L_IC_CheckLap
IC_Path5:
    WorkOr IC_STEPS_0, 0x20
    VMJump L_IC_PathDone
IC_Path6:
    WorkOr IC_STEPS_0, 0x40
    VMJump L_IC_PathDone
IC_Path7:
    WorkOr IC_STEPS_0, 0x80
    VMJump L_IC_PathDone
IC_Path8:
    WorkOr IC_STEPS_0, 0x100
    VMJump L_IC_PathDone
IC_Path9:
    WorkOr IC_STEPS_0, 0x200
    VMJump L_IC_PathDone
IC_Path10:
    WorkOr IC_STEPS_0, 0x400
    VMJump L_IC_PathDone
IC_Path11:
    WorkOr IC_STEPS_0, 0x800
    VMJump L_IC_PathDone
IC_Path12:
    WorkOr IC_STEPS_1, 0x1
    VMJump L_IC_PathDone
IC_Path13:
    WorkOr IC_STEPS_1, 0x2
    VMJump L_IC_PathDone
IC_Path14:
    WorkOr IC_STEPS_1, 0x4
    VMJump L_IC_PathDone
IC_Path15:
    WorkOr IC_STEPS_1, 0x8
    VMJump L_IC_PathDone
IC_Path16:
    WorkOr IC_STEPS_1, 0x10
    VMJump L_IC_PathDone
IC_Path17:
    WorkOr IC_STEPS_1, 0x20
    VMJump L_IC_PathDone
IC_Path18:
    WorkOr IC_STEPS_1, 0x40
    VMJump L_IC_PathDone
IC_Path19:
    WorkOr IC_STEPS_1, 0x80
    VMJump L_IC_PathDone
IC_Path20:
    WorkOr IC_STEPS_1, 0x100
    VMJump L_IC_PathDone
IC_Path21:
    WorkOr IC_STEPS_1, 0x200
    VMJump L_IC_PathDone
IC_Path22:
    WorkOr IC_STEPS_1, 0x400
    VMJump L_IC_PathDone
IC_Path23:
    WorkOr IC_STEPS_1, 0x800
    VMJump L_IC_PathDone
IC_Path24:
    WorkOr IC_STEPS_2, 0x1
    VMJump L_IC_PathDone
IC_Path25:
    WorkOr IC_STEPS_2, 0x2
    VMJump L_IC_PathDone
IC_Path26:
    WorkOr IC_STEPS_2, 0x4
    VMJump L_IC_PathDone
IC_Path27:
    WorkOr IC_STEPS_2, 0x8
    VMJump L_IC_PathDone
IC_Path28:
    WorkOr IC_STEPS_2, 0x10
    VMJump L_IC_PathDone
IC_Path29:
    WorkOr IC_STEPS_2, 0x20
    VMJump L_IC_PathDone
IC_Path30:
    WorkOr IC_STEPS_2, 0x40
    VMJump L_IC_PathDone
IC_Path31:
    WorkOr IC_STEPS_2, 0x80
    VMJump L_IC_PathDone
IC_Path32:
    WorkOr IC_STEPS_2, 0x100
    VMJump L_IC_PathDone
IC_Path33:
    WorkOr IC_STEPS_2, 0x200
    VMJump L_IC_PathDone
IC_Path34:
    WorkOr IC_STEPS_2, 0x400
    VMJump L_IC_PathDone
IC_Path35:
    WorkOr IC_STEPS_2, 0x800
    VMJump L_IC_PathDone
L_IC_CheckLap:                              // all 36 marked (16 + 16 + 4 bits there; 12 + 12 + 12 here) and on (8,21)
    h_goto_if_ne IC_STEPS_0, 0xfff, L_IC_PathDone
    h_goto_if_ne IC_STEPS_1, 0xfff, L_IC_PathDone
    h_goto_if_ne IC_STEPS_2, 0xfff, L_IC_PathDone
    h_lock                                  // IslandCave_EventScript_OpenRegiEntrance
    h_playse CH12_BANG                      // playse SE_BANG (after the setmetatile lines)
    ObjInitWarpGPos IC_DOOR_WARP, 8, 0, 20  // the door opens
    h_setflag FLAG_SYS_BRAILLE_REGICE_COMPLETED
    WorkSetConst IC_STATE, 2                // (solved: the triggers stop)
    h_release
L_IC_PathDone:
    VMHalt
Story_IC_Init:                              // OnResume, OnLoad, OnTransition
    h_setflag FLAG_LANDMARK_ISLAND_CAVE
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_SYS_BRAILLE_REGICE_COMPLETED, L_IC_InitDone
    ObjInitWarpGPos IC_DOOR_WARP, 0, 0, 0   // the door is covered (IslandCave_EventScript_HideRegiEntrance)
L_IC_InitDone:
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
