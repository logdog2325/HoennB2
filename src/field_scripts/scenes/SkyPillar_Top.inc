// Sky Pillar Top's story (Sapphire data/maps/SkyPillar_Top/scripts.inc; chapter Ch13, ch13 agent 2026-10-07): Rayquaza.
// Included twice by the generated zone file (zone 108, a standalone map): the entry below becomes script 1. Story object
// (data/story/ch13.json): Rayquaza (uid 101, Black 2's Rayquaza overworld sprite, hidden by FLAG_HIDE_RAYQUAZA which is
// not set at new game) at (14,6). No map scripts (Sapphire's ON_RESUME removes Rayquaza after the battle: ActorDelete does).
// Pokémon Emerald NDS (emerald_ch10, 2026-10-12): Emerald's Rayquaza sleeps here from the start, wakes when the player
// steps on (14,9) and flies to Sootopolis; afterwards it waits here and can be caught (pokeemerald
// data/maps/SkyPillar_Top/scripts.inc): its own entries 1-3 and bodies below (Sapphire's post-game Rayquaza, data/story/ch13.json,
// is skip_emerald). Text: src/text/scenes/emerald/SkyPillar_Top.txt. Objects: data/story/emerald/e_ch10.json (the sleeping
// Rayquaza uid 101 at (14,7), the still one uid 102 at (14,6), the trigger (14,9)). Map scripts: scenes/SkyPillar_Top_init.inc.
// Emerald's clean layout of the top (LAYOUT_SKY_PILLAR_TOP_CLEAN) while VAR_SKY_PILLAR_STATE < 2: map replace event SPT_EVENT
// (data/emerald/hoenn_world.json alt_layouts SkyPillar_Top), set or cleared by the zone init on every entry.
#if defined(SCENE_ENTRIES) && defined(HOENN_EMERALD)
    ScriptEntry SPT_Init                // 1: SkyPillar_Top_OnTransition (zone init)
    ScriptEntry SPT_Rayquaza            // 2: object 2 (SkyPillar_Top_EventScript_Rayquaza)
    ScriptEntry SPT_AwakenRayquaza      // 3: trigger (14,9) VAR_SKY_PILLAR_RAYQUAZA_CRY_DONE 0 (SkyPillar_Top_EventScript_AwakenRayquaza)
#elif defined(HOENN_EMERALD)
#include "scenes/ch10_lib.inc"
#include "scenes/emerald/em_ch10_lib.inc"
#define T_RayquazaFlewOff 0
#define T_LegendaryFlewAway 1
#define SPT_X(x) (18+(x))               // pokeemerald tile -> tile of the warp-only map's own matrix (b2tools/world.py)
#define SPT_Z(z) (24+(z))
#define SPT_RAYQUAZA_SLEEPING 101       // object 1 (LOCALID_RAYQUAZA_SLEEPING)
#define SPT_RAYQUAZA 102                // object 2 (OBJ_EVENT_GFX_RAYQUAZA_STILL)
#define SPT_EVENT 1                     // map replace event of the clean top: shared with Sootopolis' legends layout (both on
                                        // during the crisis) and Jagged Pass's mouth (scenes/emerald/SootopolisCity.inc SE_EVENT)

SPT_Init:                               // SkyPillar_Top_OnTransition
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc)
#endif
    h_goto_if_lt VAR_SKY_PILLAR_STATE, 2, L_SPT_Clean
    h_goto_if_set FLAG_DEFEATED_RAYQUAZA, L_SPT_Cracked     // TryShowRayquaza
    h_clearflag FLAG_HIDE_SKY_PILLAR_TOP_RAYQUAZA_STILL
L_SPT_Cracked:                          // the map's own (cracked) layout
    MapReplaceIsEventSet SPT_EVENT, 0x8000
    h_goto_if_eq 0x8000, 0, L_SPT_InitDone
    MapReplaceSetEvent SPT_EVENT, 0, 1  // (the zone's matrix is loaded already: reload it, as the floors' SPF_Init)
    VMHalt
L_SPT_Clean:                            // SetCleanLayout: setmaplayoutindex LAYOUT_SKY_PILLAR_TOP_CLEAN
    MapReplaceIsEventSet SPT_EVENT, 0x8000
    h_goto_if_eq 0x8000, 1, L_SPT_InitDone
    MapReplaceSetEvent SPT_EVENT, 1, 1
L_SPT_InitDone:
    VMHalt

SPT_Rayquaza:                           // SkyPillar_Top_EventScript_Rayquaza (lockall: no faceplayer)
    c10_lock
    h_waitse
    h_playmoncry SPECIES_RAYQUAZA
    h_delay 40
    h_waitmoncry
    CallWildBattle SPECIES_RAYQUAZA, EM_RAYQUAZA_LEVEL, 1   // setwildbattle SPECIES_RAYQUAZA, 70 + BattleSetup_StartLegendaryBattle
    WildBattleIsVictory HLIB_TMP        // 0 = lost: the whiteout (Rayquaza stays for the next visit)
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, L_SPT_Over
    CallWildLose
    VMHalt
L_SPT_Over:                             // (FLAG_SYS_CTRL_OBJ_DELETE / removeobject VAR_LAST_TALKED: gone after the battle)
    ActorDelete SPT_RAYQUAZA
    CallWildBattleEnd
    h_setflag FLAG_HIDE_SKY_PILLAR_TOP_RAYQUAZA_STILL
    WildBattleGetResult HLIB_TMP        // (ov012 GetWildBattleResultByCombined: 0 caught, 2 knocked out, 1 ran)
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, L_SPT_Ran
    h_setflag FLAG_DEFEATED_RAYQUAZA    // caught or knocked out (DefeatedRayquaza: no line)
    h_release
L_SPT_Ran:                              // RanFromRayquaza: "The Rayquaza flew away!"; it is back next time (the zone init)
    WordSetPokeSpecies 1, SPECIES_RAYQUAZA
    h_msgbox_info T_LegendaryFlewAway
    h_closemessage
    h_release

SPT_AwakenRayquaza:                     // SkyPillar_Top_EventScript_AwakenRayquaza
    c10_lock
    BGMFadeOut 30                       // fadeoutbgm 1
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp   // Common_Movement_FaceUp
    h_waitmovement
    em_camera_start                     // SpawnCameraObject, _Movement_CameraPanUp (3 slow tiles), RemoveCameraObject
    em_camera_to SPT_X(14), SPT_Z(6), 0, 48
    h_applymovement SPT_RAYQUAZA_SLEEPING, Mv_SPT_RayquazaStir
    h_waitmovement
    h_waitse
    h_playmoncry SPECIES_RAYQUAZA
    em_shake_at SPT_X(14), SPT_Z(6), 0, 8, 2            // ShakeCamera 1, 1, 8 shakes, delay 3
    h_waitse
    h_playmoncry SPECIES_RAYQUAZA
    em_shake_at SPT_X(14), SPT_Z(6), 0, 8, 4            // ShakeCamera 1, 2, 8 shakes, delay 5
    h_waitmoncry
    h_applymovement SPT_RAYQUAZA_SLEEPING, Mv_SPT_RayquazaFlyOff
    h_waitmovement
    h_removeobject SPT_RAYQUAZA_SLEEPING, FLAG_HIDE_SKY_PILLAR_TOP_RAYQUAZA
    h_msgbox_info T_RayquazaFlewOff     // The awakened Rayquaza flew off...
    h_closemessage
    h_delay 20
    BGMChangeMap                        // fadeinbgm 1
    em_camera_end 48                    // _Movement_CameraPanDown
    h_setvar VAR_SOOTOPOLIS_STATE, 5    // VAR_SOOTOPOLIS_CITY_STATE
    h_setvar VAR_SKY_PILLAR_STATE, 1
    h_setvar VAR_SKY_PILLAR_RAYQUAZA_CRY_DONE, 1
    h_release

    .balign 4, 0
Mv_SPT_RayquazaStir:                    // SkyPillar_Top_Movement_RayquazaStir (Emerald's Rayquaza frames: coiled, mouth open,
    delay_16                            // awake; Black 2's Rayquaza turns)
    walk_in_place_fast_left
    delay_16 5
    walk_in_place_left
    delay_16
    walk_in_place_right
    delay_16 6
    step_end
    .balign 4, 0
Mv_SPT_RayquazaFlyOff:                  // SkyPillar_Top_Movement_RayquazaFlyOff (walk_faster_up + slide_up x6)
    delay_16
    walk_in_place_down
    delay_8
    walk_in_place_right
    delay_8
    walk_fastest_up 7
    step_end

#include "common/movement.inc"
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
#elif defined(SCENE_ENTRIES)
    ScriptEntry SP_Rayquaza             // 1: SkyPillar_Top_EventScript_15F316
#else
#include "scenes/ch13_lib.inc"
#define SP_RAYQUAZA 101
#define SP_RAYQUAZA_LEVEL 78            // Sapphire 70 on the scaled curve (data/level_scaling.json)

SP_Rayquaza:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_waitse
    h_playmoncry SPECIES_RAYQUAZA
    h_delay 40
    h_waitmoncry
    h_setflag FLAG_HIDE_RAYQUAZA
    ch13_legend_battle SPECIES_RAYQUAZA, SP_RAYQUAZA_LEVEL, SP_RAYQUAZA
    h_release
    .balign 4, 0
#endif
