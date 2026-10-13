// TerraCave_End (zone 366, Emerald): converter/gen_caves_emerald.py from emerald/TerraCave_End (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // emerald_ch12_13
#include "hoenn_story.inc"  // emerald_ch12_13
#include "hoenn_version.inc"  // emerald_ch12_13: MODEL_GROUDON

    ScriptEntry Script_None
    ScriptEntry TCE_Groudon  // 2: trigger (17,26) while work TCE_TEMP_1 is 1 (TerraCave_End_EventScript_Groudon)  // story:
    ScriptEntry TCE_Init  // 3: zone init (0733: TerraCave_End_OnTransition)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (Ch13 post-game, builder B8 emerald_ch12_13 2026-10-12; pokeemerald data/maps/TerraCave_End/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). Messages: src/text/script/emerald/0578_room_TerraCave_End.txt.
// Groudon (data/story/emerald/e_ch13.json uid 1, pokeemerald (17,22), FACE_DOWN, Black 2's Groudon model MODEL_GROUDON, hidden by
// FLAG_HIDE_TERRA_CAVE_GROUDON) stands at the cave's end while FLAG_DEFEATED_GROUDON is not set; stepping on (17,26) (VAR_TEMP_1 = 1:
// the zone-local work TCE_TEMP_1, set by the zone init) brings it down to you: its cry, Emerald's legendary battle (Lv 70 ->
// TCE_LEVEL on the curve, as every legendary of this port). Emerald's outcomes: caught or beaten = FLAG_DEFEATED_GROUDON and
// VAR_SHOULD_END_ABNORMAL_WEATHER 1 (the abnormal weather ends when you are back on its route:
// scenes/emerald/abnormal_weather.inc); ran = "The Groudon flew away!", back on your next visit; lost = the whiteout.
// The zone init also runs the abnormal weather's cave rule (global AW_GLOBAL_CAVE_INIT in the init table, 0733).
#define T_LegendaryFlewAway 0           // gText_LegendaryFlewAway ({0100:1} = the species)
#define TCE_LEG 1                       // LOCALID_TERRA_CAVE_GROUDON
#define TCE_TEMP_1 0x4001               // VAR_TEMP_1 (a zone-local work: cleared on every map change, as Emerald's)
#define TCE_LEVEL 78                    // Emerald 70 on the scaled curve (scenes/emerald/em_ch10_lib.inc EM_RAYQUAZA_LEVEL)

TCE_Init:                              // TerraCave_End_OnTransition: call_if_unset FLAG_DEFEATED_GROUDON, ..._ShowGroudon
    h_goto_if_set FLAG_DEFEATED_GROUDON, L_TCE_InitDone
    h_clearflag FLAG_HIDE_TERRA_CAVE_GROUDON
    h_setvar TCE_TEMP_1, 1
L_TCE_InitDone:
    VMHalt

TCE_Groudon:                             // TerraCave_End_EventScript_Groudon
    h_lock
    h_applymovement 255, Mv_FaceUp
    h_waitmovement
    h_applymovement TCE_LEG, Mv_TCE_GroudonApproach
    h_waitmovement
    h_waitse
    h_playmoncry SPECIES_GROUDON          // playmoncry SPECIES_GROUDON, CRY_MODE_ENCOUNTER
    h_delay 40
    h_waitmoncry
    FlagSet FLAG_HIDE_TERRA_CAVE_GROUDON            // (removeobject's flag: the object is gone after the battle, whatever happened)
    CallWildBattle SPECIES_GROUDON, TCE_LEVEL, 1   // setwildbattle SPECIES_GROUDON, 70 + BattleSetup_StartLegendaryBattle
    WildBattleIsVictory HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, L_TCE_NotLost
    CallWildLose                        // lost: the whiteout
    VMHalt
L_TCE_NotLost:
    ActorDelete TCE_LEG
    CallWildBattleEnd
    h_setvar TCE_TEMP_1, 0
    WildBattleGetResult HLIB_TMP        // 0 caught, 2 beaten, else ran (scenes/postgame_lib.inc pg_legend_battle)
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, L_TCE_Defeated
    WorkCmpConst HLIB_TMP, 2
    VMJumpIf CMP_EQ, L_TCE_Defeated
    WordSetPokeSpecies 1, SPECIES_GROUDON   // TerraCave_End_EventScript_RanFromGroudon: Common_EventScript_LegendaryFlewAway
    SystemMsg T_LegendaryFlewAway, 2
    LastKeyWait
    MsgWinCloseAll
    h_release
L_TCE_Defeated:                         // caught (the fall-through) or TerraCave_End_EventScript_DefeatedGroudon
    h_setvar VAR_SHOULD_END_ABNORMAL_WEATHER, 1
    h_setflag FLAG_DEFEATED_GROUDON
    h_release

    .balign 4, 0
Mv_TCE_GroudonApproach:                  // TerraCave_End_Movement_GroudonApproach (init_affine_anim, walk_*_affine: Groudon grows as it comes)
    walk_down
    delay_16 2
    walk_down
    delay_16 2
    walk_down
    step_end
Mv_FaceUp:
    face_up
    step_end
#include "common/movement.inc"
