// CaveOfOrigin_B4F (zone 103, Emerald): converter/gen_caves_emerald.py from emerald/CaveOfOrigin_B4F (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// CaveOfOrigin_B4F (zone 103): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch10
#include "hoenn_key_items.h"  // ch10
#include "hoenn_story.inc"  // ch10
#include "hoenn_version.inc"  // ruby_scenes: version-neutral names (SPECIES_GROUDON_OR_KYOGRE, ITEM_RED_OR_BLUE_ORB)

    ScriptEntry Script_1
    ScriptEntry B4_Init  // 2: zone init (MapScript1_15DDC5: CaveOfOrigin_EventScript_DisableTriggers once the legend is calmed)  // story:
    ScriptEntry B4_Kyogre  // 3: trigger (9,13) VAR_CAVE_OF_ORIGIN_B4F_STATE 0 (CaveOfOrigin_B4F_EventScript_15DDD7)  // story:
    ScriptEntry B4_Cry  // 4: triggers (13,9) and (5,9) VAR_TEMP_5 0 (CaveOfOrigin_EventScript_LegendaryCry)  // story:
    ScriptEntry COB_Wallace  // 5: object 1 (CaveOfOrigin_B1F_EventScript_Wallace; Emerald, emerald_ch10)  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder up (9,3) -> CaveOfOrigin_1F warp 1 (14,5)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 95, 14, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch10, ch10 agent 2026-10-07; Sapphire data/maps/CaveOfOrigin_B4F/scripts.inc; generators keep everything from
// this line on; entries above marked "// story:"). Messages: 0120_room_CaveOfOrigin_B4F.txt
// RUBY (ruby_scenes, 2026-10-08; pokeruby's .ifdef SAPPHIRE blocks of this map): the same scene event for event with Groudon (SPECIES_GROUDON_OR_KYOGRE;
// data/story/ch10.json "model_ruby" 4512), the Red Orb (the text lines, src/text/script/ruby/0120_*.txt, same line numbers: "<player>'s Red Orb suddenly
// began glowing!" / "Groudon appears to have settled into sleep again...") and the Ruby layout (setmaplayoutindex 313: data/cave_layouts/CaveOfOrigin_B4F_Ruby.json,
// WP3; only the water pool is drawn as lava, no collision change). The glow is red in Ruby, blue in Sapphire (VAR_RESULT 2 / 3 of sub_80818A4): Black 2 has
// no coloured screen flash, both are the one white flash.
// Kyogre (Black 2's overworld Pokémon sprite code 4511) sleeps at (9,10) until the player steps on (9,13) (VAR_CAVE_OF_ORIGIN_B4F_STATE 0). Battle: Black 2's legendary encounter (CallWildBattle species, level, 1; as Black 2's Latios/Latias scripts), at the scaled level 49 (Sapphire 45: data/level_scaling.json). The result: Black 2 reports 0 caught, 1/2 fainted or fled: Sapphire's "settled into sleep again" line (GetBattleOutcome 1 = won) is shown for both 1 and 2. Black 2 gaps: the glow task (sub_80818A4/FC) is one white flash, the affine "rising" movement is a slow step, the sparkle field effect is the flash; setweather NONE needs nothing (no weather underground; Kyogre's rain ends with FLAG_SYS_WEATHER_CTRL cleared below: the `weather` patch).
#include "scenes/ch10_lib.inc"
#define T_BlueOrbGlowing 0
#define T_KyogreSettled 1
#define B4_KYOGRE 1
#define B4_KYOGRE_LEVEL 49              // Sapphire 45, scaled (data/level_scaling.json)

B4_Init:                                // CaveOfOrigin_B4F_MapScript1_15DDC5
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc)
#endif
    h_goto_if_unset FLAG_LEGENDARY_BATTLE_COMPLETED, L_B4_InitDone
    h_setvar C10_TEMP_1, 1
    h_setvar C10_TEMP_2, 1
    h_setvar 0x4003, 1
    h_setvar 0x4004, 1
    h_setvar C10_TEMP_5, 1
L_B4_InitDone:
    VMHalt

B4_Cry:                                 // CaveOfOrigin_EventScript_LegendaryCry
    c10_lock
    h_waitse
    h_playmoncry SPECIES_GROUDON_OR_KYOGRE
    h_waitmoncry
    h_setvar C10_TEMP_5, 1
    h_release

B4_Kyogre:                              // CaveOfOrigin_B4F_EventScript_15DDD7
    c10_lock
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_info T_BlueOrbGlowing      // <player>'s Blue Orb suddenly began glowing!
    h_closemessage
    SEPlay C10_SE_DETECT                // setweather NONE; SE_M_DETECT; the sparkle at (9,13)
    h_delay 30
    SEPlay C10_SE_ORB                   // SE_ORB; the blue glow (sub_80818A4)
    FadeOutWhiteQ
    FadeWait
    FadeInWhiteQ
    FadeWait
    h_applymovement B4_KYOGRE, Mv_B4_KyogreComes
    h_waitmovement
    h_delay 60
    h_waitse
    h_playmoncry SPECIES_GROUDON_OR_KYOGRE
    h_delay 40
    h_waitmoncry
    FlagSet FLAG_HIDE_LEGEND_MON_CAVE_OF_ORIGIN     // (FLAG_SYS_CTRL_OBJ_DELETE: the object is gone after the battle whatever happened)
    CallWildBattle SPECIES_GROUDON_OR_KYOGRE, B4_KYOGRE_LEVEL, 1   // setwildbattle SPECIES_GROUDON_OR_KYOGRE, 45 + ScrSpecial_StartGroudonKyogreBattle
    WildBattleIsVictory C10_A
    WorkCmpConst C10_A, 1
    VMJumpIf CMP_EQ, L_B4_Continue
    CallWildLose
    VMHalt
L_B4_Continue:
    ActorDelete B4_KYOGRE
    CallWildBattleEnd
    WildBattleGetResult C10_A
    WorkCmpConst C10_A, 0
    VMJumpIf CMP_EQ, L_B4_Caught        // caught: no line
    h_msgbox_info T_KyogreSettled       // Kyogre appears to have settled into sleep again...
    h_closemessage
L_B4_Caught:
    h_setflag FLAG_HIDE_WALLACE_SOOTOPOLIS
    h_setflag FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_1
    h_setflag FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_2
    h_clearflag FLAG_HIDE_WALLACE_SOOTOPOLIS_GYM
    h_setvar VAR_CAVE_OF_ORIGIN_B4F_STATE, 1
    h_setflag FLAG_LEGENDARY_BATTLE_COMPLETED
    h_clearflag FLAG_HIDE_SOOTOPOLIS_RESIDENTS
    h_clearflag FLAG_SYS_WEATHER_CTRL   // the downpour ends (the `weather` patch reads this flag)
    h_setvar VAR_MT_PYRE_STATE, 2
    h_clearflag FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_release

// ---- Emerald (emerald_ch10, 2026-10-12): Emerald's B1F is this room and has no legend (data/story/ch10.json: Sapphire's Kyogre
// and its three triggers are skip_emerald); Wallace waits here and asks where Rayquaza is (pokeemerald
// CaveOfOrigin_B1F_EventScript_Wallace: the MULTI_WHERES_RAYQUAZA loop; only "Sky Pillar" ends it). Text lines 2-11 of
// src/text/script/emerald/0120_room_CaveOfOrigin_B4F.txt; Wallace = uid 1 (data/story/emerald/e_ch10.json).
#define T_WallaceStory 2
#define T_WhereIsRayquaza 3
#define T_ButWereInCaveOfOrigin 4
#define T_OldLadyDidntMentionThat 5
#define T_CantYouRememberSomehow 6
#define T_WellHeadToSkyPillar 7
#define T_ChoiceCaveOfOrigin 8
#define T_ChoiceMtPyre 9
#define T_ChoiceSkyPillar 10
#define T_ChoiceDontRemember 11
#define COB_WALLACE 1
COB_Wallace:                            // CaveOfOrigin_B1F_EventScript_Wallace (lock, faceplayer)
    c10_talk
    h_msgbox T_WallaceStory             // Ah, so you are <player>? ... no clue as to Rayquaza's whereabouts...
    h_closemessage
    h_applymovement COB_WALLACE, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_delay 60
    h_applymovement COB_WALLACE, Common_Movement_ExclamationMark    // (playse SE_PIN: the balloon has its own sound)
    h_waitmovement
    h_applymovement COB_WALLACE, Common_Movement_Delay48
    h_waitmovement
    h_delay 30
    ActorSetEyeToEye                    // Common_Movement_FacePlayer
    ActorMsg MSGFILE_SCRIPT, T_WhereIsRayquaza, COB_WALLACE, 0, 0   // message + waitmessage: the list comes under it
L_COB_Ask:                              // CaveOfOrigin_B1F_EventScript_WheresRayquaza (multichoice 0, 0, MULTI_WHERES_RAYQUAZA)
    ListMenu_AnchorTopLeft 1, 1, 0, 1, C10_SEL
    ListMenuAdd T_ChoiceCaveOfOrigin, 65535, 0
    ListMenuAdd T_ChoiceMtPyre, 65535, 1
    ListMenuAdd T_ChoiceSkyPillar, 65535, 2
    ListMenuAdd T_ChoiceDontRemember, 65535, 3
    ListMenuShow
    h_goto_if_eq C10_SEL, 0, L_COB_AtCave
    h_goto_if_eq C10_SEL, 1, L_COB_AtPyre
    h_goto_if_eq C10_SEL, 2, L_COB_AtSkyPillar
    ActorMsg MSGFILE_SCRIPT, T_CantYouRememberSomehow, COB_WALLACE, 0, 0     // "Don't remember" (or B)
    VMJump L_COB_Ask
L_COB_AtCave:
    ActorMsg MSGFILE_SCRIPT, T_ButWereInCaveOfOrigin, COB_WALLACE, 0, 0
    VMJump L_COB_Ask
L_COB_AtPyre:
    ActorMsg MSGFILE_SCRIPT, T_OldLadyDidntMentionThat, COB_WALLACE, 0, 0
    VMJump L_COB_Ask
L_COB_AtSkyPillar:                      // CaveOfOrigin_B1F_EventScript_AtSkyPillar
    h_msgbox_actor T_WellHeadToSkyPillar, COB_WALLACE
    h_closemessage
    SEPlay SE_EXIT
    FadeOutBlack                        // fadescreenspeed FADE_TO_BLACK, 4
    FadeWait
    h_setflag FLAG_WALLACE_GOES_TO_SKY_PILLAR
    h_setvar VAR_SOOTOPOLIS_STATE, 3    // VAR_SOOTOPOLIS_CITY_STATE (scenes/emerald/SootopolisCity.inc)
    h_removeobject COB_WALLACE, FLAG_HIDE_CAVE_OF_ORIGIN_B1F_WALLACE
    h_clearflag FLAG_HIDE_SKY_PILLAR_WALLACE
    FadeInBlack
    FadeWait
    h_release

    .balign 4, 0
Mv_B4_KyogreComes:                      // CaveOfOrigin_B4F_Movement_15DE7D (affine growing walk down)
    walk_slow_down
    delay_16 2
    walk_slow_down
    step_end

#include "common/movement.inc"
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
    .balign 4, 0
