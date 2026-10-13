// Birth Island (Emerald data/maps/BirthIsland_Exterior/scripts.inc + BirthIsland_Harbor's sailor; events agent,
// 2026-10-07; notes/EVENTS.md). Included twice by the generated zone file (zone 195, a warp-only map): entries 1-4.
// Text: src/text/scenes/BirthIsland_Exterior.txt (Emerald's lines). Story objects (data/story/events.json): the triangle
// (uid 101, Emerald's OBJ_EVENT_GFX_DEOXYS_TRIANGLE: Black 2 has no such object; its white stone sphere 144 stands in),
// Deoxys (uid 102, Black 2's Deoxys overworld sprite 4515, hidden by FLAG_HIDE_DEOXYS) and the ferry sailor (uid 103).
// The harbour (BirthIsland_Harbor, the S.S. Tidal's landing room) is not built: the ferry docks at the dock's end, where
// Emerald's harbour door is (15,24), and the sailor waits there, as at Southern Island.
// The triangle puzzle is Emerald's own (field_specials.c DoDeoxysRockInteraction): each time you talk to the triangle it
// moves on to the next of eleven places (sDeoxysRockCoords); if you took more steps since the last time than the shortest
// way (sStoneMaxStepCounts: 4, 8, 8, 8, 4, 4, 4, 6, 3, 3) it goes back to the start. Steps are Black 2's own pedometer
// (PedometerStart / PedometerGet: PlayerSave_BeginStepCounter / GetStepCounter, the counter of Black 2's Mienfoo walk
// errand 0940.s): Emerald counts the steps on this island only (IncrementBirthIslandRockStepCount); here every step counts,
// and the island is left only by the ferry, which resets the puzzle anyway (OnTransition). Not ported: the rock's 11
// colours (Black 2's stone has one), its slide (it jumps to its next place), the rock's shatter effect (the camera shakes
// and it is gone), MUS_RG_ENCOUNTER_DEOXYS (the battle music follows).
#ifdef SCENE_ENTRIES
    ScriptEntry BE_Arrive               // 1: the ferry's landing (reserved by Lilycove's harbor: EV_ARRIVE_SCRIPT)
    ScriptEntry BE_Init                 // 2: BirthIsland_Exterior_OnTransition (zone init)
    ScriptEntry BE_Triangle             // 3: BirthIsland_Exterior_EventScript_Triangle
    ScriptEntry BE_Sailor               // 4: BirthIsland_Harbor_EventScript_Sailor
#else
#include "scenes/events_lib.inc"
#define BE_ROCK 101
#define BE_DEOXYS 102
#define BE_SAILOR 103
#define BE_GY 3                         // the island top's grid height (48 units: ActorSetGPos takes 16-unit levels)
#define BE_STEPS 0x8032                 // Emerald's VAR_DEOXYS_ROCK_STEP_COUNT, read from the pedometer
#define BE_SE_MOVE SEQ_SE_FLD_29        // SE_RG_DEOXYS_MOVE [guess: ch10's "Orb's glow"]
#define BE_SE_FAIL SEQ_SE_FLD_28        // SE_M_CONFUSE_RAY [guess]
#define BE_SE_SHATTER SEQ_SE_FLD_126    // the rock shatters (FLDEFF_DESTROY_DEOXYS_ROCK's quake) [guess: ch10's quake]

BE_Arrive:                              // warp MAP_BIRTH_ISLAND_HARBOR, 8, 4 -> the dock's end (15,23), facing the sailor
    ch2_land
    h_release

BE_Init:                                // BirthIsland_Exterior_OnTransition
    h_setvar VAR_DEOXYS_ROCK_LEVEL, 0
    h_setflag FLAG_HIDE_DEOXYS          // (Emerald's new game sets it: Deoxys only comes when the puzzle is solved)
    h_goto_if_unset FLAG_BATTLED_DEOXYS, L_BE_TryShow
    h_setflag FLAG_HIDE_BIRTH_ISLAND_DEOXYS_TRIANGLE   // BirthIsland_Exterior_EventScript_HideDeoxysAndPuzzle
    VMHalt
L_BE_TryShow:                           // BirthIsland_Exterior_EventScript_TryShowDeoxysPuzzle
    h_goto_if_set FLAG_DEFEATED_DEOXYS, L_BE_InitDone
    h_clearflag FLAG_HIDE_BIRTH_ISLAND_DEOXYS_TRIANGLE
    h_clearflag FLAG_DEOXYS_ROCK_COMPLETE
L_BE_InitDone:
    VMHalt

BE_Triangle:                            // BirthIsland_Exterior_EventScript_Triangle + special DoDeoxysRockInteraction
    h_lock
    h_goto_if_set FLAG_DEOXYS_ROCK_COMPLETE, L_BE_End   // DEOXYS_ROCK_COMPLETE
    PedometerGet BE_STEPS
#if HOENN_TEST_CH13_EVENTS == 3
    h_setvar BE_STEPS, 0                // test builds only: no step limit (the harness's steps are not exact)
#endif
    PedometerStart                      // VarSet(VAR_DEOXYS_ROCK_STEP_COUNT, 0)
    VMJump L_BE_CheckSteps
L_BE_Progress:
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 10, L_BE_Solved
    WorkAdd VAR_DEOXYS_ROCK_LEVEL, 1
    SEPlay BE_SE_MOVE                   // DEOXYS_ROCK_PROGRESSED
    VMCall L_BE_MoveRock
    h_waitse
L_BE_End:
    h_release
L_BE_Failed:                            // DEOXYS_ROCK_FAILED: back to the start
    h_setvar VAR_DEOXYS_ROCK_LEVEL, 0
    SEPlay BE_SE_FAIL
    h_delay 30
    VMCall L_BE_MoveRock
    h_waitse
    h_release
L_BE_Solved:                            // DEOXYS_ROCK_SOLVED -> BirthIsland_Exterior_EventScript_Deoxys
    h_setflag FLAG_DEOXYS_ROCK_COMPLETE
    PedometerEnd
    h_waitse
    SEPlay BE_SE_SHATTER                // dofieldeffect FLDEFF_DESTROY_DEOXYS_ROCK: the camera shakes, the rock is gone
    EvCameraShake 2, 0, 3, 8, 1, 0, 1, 5
    VMSleep 24
    h_removeobject BE_ROCK, FLAG_HIDE_BIRTH_ISLAND_DEOXYS_TRIANGLE
    h_delay 30
    h_addobject BE_DEOXYS, FLAG_HIDE_DEOXYS
    h_applymovement BE_DEOXYS, Mv_BE_DeoxysApproach
    h_waitmovement
    h_waitse
    h_playmoncry SPECIES_DEOXYS
    h_delay 40
    h_waitmoncry
    ev_legend_battle SPECIES_DEOXYS, EV_DEOXYS_LEVEL, BE_DEOXYS, FLAG_HIDE_DEOXYS, FLAG_BATTLED_DEOXYS, FLAG_DEFEATED_DEOXYS, 3
    h_release

BE_Sailor:                              // BirthIsland_Harbor_EventScript_Sailor
    ev_island_sailor BE_SAILOR, 0, 1, 2 // What an oddly shaped island, eh? Do you want to return to Lilycove?

#include "scenes/BirthIsland_Exterior_rock.inc"

    .balign 4, 0
Mv_BE_DeoxysApproach:                   // BirthIsland_Exterior_Movement_DeoxysApproach (7 x walk_slow_down from (15,3);
    walk_slow_down 4                    // here from (15,6): the top's tree stands in the way of a walking actor)
    step_end
    .balign 4, 0
#endif
