// NavelRock_Bottom (zone 225): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry EV_NB_Lugia             // 2: object 1 (NavelRock_Bottom_EventScript_Lugia)  // story:
    ScriptEntry EV_NB_Init              // 3: NavelRock_Bottom_OnTransition (zone init, 0451_room_NavelRock_Bottom_init.s)  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder up (14,19) -> NavelRock_Down11 warp 0 (5,5)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 264, 5, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (events agent, 2026-10-07: Emerald data/maps/NavelRock_Bottom/scripts.inc; generators keep everything from this
// line on; entries above marked "// story:"). Lugia: data/story/events.json (uid 1, Black 2's own Lugia overworld sprite 4378,
// hidden by FLAG_HIDE_LUGIA). Text: src/text/script/0284_room_NavelRock_Bottom.txt (line 0). Emerald's ShakeCamera twice with
// SE_THUNDERSTORM_STOP = Black 2's EvCameraShake with a quake sound [guess]. Map scripts: 0451_room_NavelRock_Bottom_init.s.
#include "hoenn_story.inc"
#include "scenes/events_lib.inc"
#define NB_LUGIA 1
#define NB_SE_THUNDER SEQ_SE_FLD_126            // SE_THUNDERSTORM_STOP [guess: the quake sound ch10 uses]

EV_NB_Init:                                     // NavelRock_Bottom_OnTransition
    h_goto_if_unset FLAG_CAUGHT_LUGIA, L_NB_TryShow
    h_setflag FLAG_HIDE_LUGIA                   // NavelRock_Bottom_EventScript_HideLugia
    VMHalt
L_NB_TryShow:                                   // NavelRock_Bottom_EventScript_TryShowLugia
    h_goto_if_set FLAG_DEFEATED_LUGIA, L_NB_InitDone
    h_clearflag FLAG_HIDE_LUGIA
L_NB_InitDone:
    VMHalt

EV_NB_Lugia:                                    // NavelRock_Bottom_EventScript_Lugia
    h_lock
    h_faceplayer
    h_waitse
    h_delay 20
    SEPlay NB_SE_THUNDER
    EvCameraShake 3, 0, 4, 8, 1, 0, 1, 2        // special ShakeCamera (horizontal 3, 4 shakes, delay 2)
    VMSleep 15
    SEPlay NB_SE_THUNDER
    EvCameraShake 3, 0, 4, 8, 1, 0, 1, 2
    VMSleep 15
    h_delay 50
    h_waitse
    h_playmoncry SPECIES_LUGIA
    h_waitmoncry
    h_delay 20
    ev_legend_battle SPECIES_LUGIA, EV_LUGIA_LEVEL, NB_LUGIA, FLAG_HIDE_LUGIA, FLAG_CAUGHT_LUGIA, FLAG_DEFEATED_LUGIA, 0
    h_release
    .balign 4, 0
