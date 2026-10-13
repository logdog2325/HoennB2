// CaveOfOrigin_B2F (zone 101): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch10
#include "hoenn_key_items.h"  // ch10
#include "hoenn_story.inc"  // ch10

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry CO_Init  // 3: zone init (CaveOfOrigin_EventScript_DisableTriggers after the legend)  // story:
    ScriptEntry CO_Shake1  // 4: trigger VAR_TEMP_1 0 (CaveOfOrigin_EventScript_Shake1)  // story:
    ScriptEntry CO_Shake2  // 5: trigger VAR_TEMP_2 0 (CaveOfOrigin_EventScript_Shake2)  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder up (5,10) -> CaveOfOrigin_B1F warp 1 (5,11)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 100, 5, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (8,14) -> CaveOfOrigin_B3F warp 0 (7,14)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 102, 7, 0, 14, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch10, ch10 agent 2026-10-07; Sapphire data/maps/CaveOfOrigin_B2F/scripts.inc; generators keep everything from
// this line on; entries above marked "// story:"). Messages: -
// The cave shakes when the player first crosses the marked tiles (Sapphire: setvar VAR_TEMP_n, ShakeCamera; Black 2: EvCameraShake); after Kyogre is calmed the zone init marks the triggers used (VAR_TEMP_1-5 = 1, Black 2 temporary works 0x4001-0x4005).
#include "scenes/ch10_lib.inc"
CO_Init:                                // MapScript1 (ON_TRANSITION): CaveOfOrigin_EventScript_DisableTriggers once Kyogre is calmed
    h_goto_if_unset FLAG_LEGENDARY_BATTLE_COMPLETED, L_CO_InitDone
    h_setvar C10_TEMP_1, 1
    h_setvar C10_TEMP_2, 1
    h_setvar 0x4003, 1
    h_setvar 0x4004, 1
    h_setvar C10_TEMP_5, 1
L_CO_InitDone:
    VMHalt
CO_Shake1:                              // CaveOfOrigin_EventScript_Shake1
    c10_lock
    h_setvar C10_TEMP_1, 1
    c10_shake 4
    h_release
CO_Shake2:                              // CaveOfOrigin_EventScript_Shake2
    c10_lock
    h_setvar C10_TEMP_2, 1
    c10_shake 4
    h_release
    .balign 4, 0
