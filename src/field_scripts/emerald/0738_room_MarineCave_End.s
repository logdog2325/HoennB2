// MarineCave_End (zone 369, Emerald): converter/gen_caves_emerald.py from emerald/MarineCave_End (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // emerald_ch12_13
#include "hoenn_story.inc"  // emerald_ch12_13
#include "hoenn_version.inc"  // emerald_ch12_13: MODEL_KYOGRE

    ScriptEntry Script_None
    ScriptEntry MCE_Kyogre  // 2: trigger (9,26) while work MCE_TEMP_1 is 1 (MarineCave_End_EventScript_Kyogre)  // story:
    ScriptEntry MCE_Init  // 3: zone init (0739: MarineCave_End_OnTransition)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (Ch13 post-game, builder B8 emerald_ch12_13 2026-10-12; pokeemerald data/maps/MarineCave_End/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). Messages: src/text/script/emerald/0581_room_MarineCave_End.txt.
// Kyogre (data/story/emerald/e_ch13.json uid 1, pokeemerald (9,22), FACE_DOWN, Black 2's Kyogre model MODEL_KYOGRE, hidden by
// FLAG_HIDE_MARINE_CAVE_KYOGRE) stands at the cave's end while FLAG_DEFEATED_KYOGRE is not set; stepping on (9,26) (VAR_TEMP_1 = 1:
// the zone-local work MCE_TEMP_1, set by the zone init) brings it down to you: its cry, Emerald's legendary battle (Lv 70 ->
// MCE_LEVEL on the curve, as every legendary of this port). Emerald's outcomes: caught or beaten = FLAG_DEFEATED_KYOGRE and
// VAR_SHOULD_END_ABNORMAL_WEATHER 1 (the abnormal weather ends when you are back on its route:
// scenes/emerald/abnormal_weather.inc); ran = "The Kyogre flew away!", back on your next visit; lost = the whiteout.
// The zone init also runs the abnormal weather's cave rule (global AW_GLOBAL_CAVE_INIT in the init table, 0739).
#define T_LegendaryFlewAway 0           // gText_LegendaryFlewAway ({0100:1} = the species)
#define MCE_LEG 1                       // LOCALID_MARINE_CAVE_KYOGRE
#define MCE_TEMP_1 0x4001               // VAR_TEMP_1 (a zone-local work: cleared on every map change, as Emerald's)
#define MCE_LEVEL 78                    // Emerald 70 on the scaled curve (scenes/emerald/em_ch10_lib.inc EM_RAYQUAZA_LEVEL)

MCE_Init:                              // MarineCave_End_OnTransition: call_if_unset FLAG_DEFEATED_KYOGRE, ..._ShowKyogre
    h_goto_if_set FLAG_DEFEATED_KYOGRE, L_MCE_InitDone
    h_clearflag FLAG_HIDE_MARINE_CAVE_KYOGRE
    h_setvar MCE_TEMP_1, 1
L_MCE_InitDone:
    VMHalt

MCE_Kyogre:                             // MarineCave_End_EventScript_Kyogre
    h_lock
    h_applymovement 255, Mv_FaceUp
    h_waitmovement
    h_applymovement MCE_LEG, Mv_MCE_KyogreApproach
    h_waitmovement
    h_waitse
    h_playmoncry SPECIES_KYOGRE          // playmoncry SPECIES_KYOGRE, CRY_MODE_ENCOUNTER
    h_delay 40
    h_waitmoncry
    FlagSet FLAG_HIDE_MARINE_CAVE_KYOGRE            // (removeobject's flag: the object is gone after the battle, whatever happened)
    CallWildBattle SPECIES_KYOGRE, MCE_LEVEL, 1   // setwildbattle SPECIES_KYOGRE, 70 + BattleSetup_StartLegendaryBattle
    WildBattleIsVictory HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, L_MCE_NotLost
    CallWildLose                        // lost: the whiteout
    VMHalt
L_MCE_NotLost:
    ActorDelete MCE_LEG
    CallWildBattleEnd
    h_setvar MCE_TEMP_1, 0
    WildBattleGetResult HLIB_TMP        // 0 caught, 2 beaten, else ran (scenes/postgame_lib.inc pg_legend_battle)
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, L_MCE_Defeated
    WorkCmpConst HLIB_TMP, 2
    VMJumpIf CMP_EQ, L_MCE_Defeated
    WordSetPokeSpecies 1, SPECIES_KYOGRE   // MarineCave_End_EventScript_RanFromKyogre: Common_EventScript_LegendaryFlewAway
    SystemMsg T_LegendaryFlewAway, 2
    LastKeyWait
    MsgWinCloseAll
    h_release
L_MCE_Defeated:                         // caught (the fall-through) or MarineCave_End_EventScript_DefeatedKyogre
    h_setvar VAR_SHOULD_END_ABNORMAL_WEATHER, 1
    h_setflag FLAG_DEFEATED_KYOGRE
    h_release

    .balign 4, 0
Mv_MCE_KyogreApproach:                  // MarineCave_End_Movement_KyogreApproach (init_affine_anim, walk_*_affine: Kyogre grows as it comes)
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
