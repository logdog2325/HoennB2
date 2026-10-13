// RusturfTunnel (zone 134): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
// Story (chapter Ch2, Sapphire data/maps/RusturfTunnel/scripts.inc): scripts 1-8, text 0153 lines 0-8; people and
// triggers in data/story/ch2.json (uids = Sapphire local ids; room origin (0,0): zone tile = Sapphire tile); map
// scripts in 0269. Chapter Ch3's beat (Rock Smash opens the tunnel: Wanda and her boyfriend, HM04) goes in
// scenes/RusturfTunnel_Ch3.inc (its scripts are numbered after these) and scenes/RusturfTunnel_Ch3_init.inc.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
#include "hoenn_story.inc"

    ScriptEntry RT_FieldLoad        // 1: RusturfTunnel_MapScript1_15C762 (OnTransition; here on every field load)
    ScriptEntry RT_Girlfriend       // 2: RusturfTunnel_EventScript_15C782
    ScriptEntry RT_Boyfriend        // 3: RusturfTunnel_EventScript_15C799
    ScriptEntry RT_GruntFlee        // 4: RusturfTunnel_EventScript_15C9AB, triggers (9,4)/(9,5) VAR_RUSTURF_TUNNEL_STATE 2
    ScriptEntry RT_Peeko            // 5: RusturfTunnel_EventScript_15C9D7
    ScriptEntry RT_Grunt            // 6: RusturfTunnel_EventScript_15C9EA (the Devon Goods)
    ScriptEntry RT_None             // 7: Mr. Briney (Sapphire script 0x0)
    ScriptEntry RT_ZoneInit         // 8: zone init
#define SCENE_ENTRIES
#include "scenes/RusturfTunnel_Ch3.inc"
#undef SCENE_ENTRIES
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story
#define RT_BOYFRIEND 1
#define RT_BRINEY 5
#define RT_GRUNT 6
#define RT_PEEKO 7
#define RT_GIRLFRIEND 10
#define FLAG_RT_TEMP_1 0x5A         // FLAG_TEMP_1 (map-local: flags 0-0x63 reset on every zone change)

RT_ZoneInit:                        // Common_EventScript_SetupEvilTeamGfxIds: the grunt is an Aqua model already
RT_None:
    VMHalt

// OnTransition: VAR_RUSTURF_TUNNEL_STATE 2 -> setobjectxyperm 7 (Peeko), 13, 4 and 6 (grunt), 13, 5. Black 2 moves
// the live actors on every field load and return (MapScript 3 and 4: actors exist then, the screen is still dark),
// so the people keep Sapphire's spots (14,4)/(14,5) in the entity list.
RT_FieldLoad:
    h_goto_if_ne VAR_RUSTURF_TUNNEL_STATE, 2, L_RT_FieldLoadDone
    ActorSetGPos RT_PEEKO, 13, 0, 4, 2
    ActorSetGPos RT_GRUNT, 13, 0, 5, 2
L_RT_FieldLoadDone:
    VMHalt

RT_Girlfriend:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 8                      // On the other side of this rock... My boyfriend is there...
    h_closemessage
    h_turnobject RT_GIRLFRIEND, 2   // Common_Movement_FaceOriginalDirection (MOVEMENT_TYPE_FACE_LEFT)
    h_release

RT_Boyfriend:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RT_TEMP_1, L_RT_BoyfriendAgain
    h_setflag FLAG_RT_TEMP_1
    h_msgbox 6                      // ... ... Why can't they keep digging?...
    h_closemessage
    h_turnobject RT_BOYFRIEND, 3    // (MOVEMENT_TYPE_FACE_RIGHT)
    h_release
L_RT_BoyfriendAgain:
    h_msgbox 7                      // To get from Rustboro to Verdanturf, you need to go to Dewford...
    h_closemessage
    h_turnobject RT_BOYFRIEND, 3
    h_release

RT_GruntFlee:                       // the grunt sees you coming (VAR_RUSTURF_TUNNEL_STATE 2)
    h_lock
    h_msgbox_actor 0, RT_GRUNT      // What, are you coming? Come and get some, then!
    h_closemessage
    h_applymovement RT_GRUNT, Mv_RT_StepBack
    h_applymovement RT_PEEKO, Mv_RT_StepBack
    h_waitmovement
    h_setvar VAR_RUSTURF_TUNNEL_STATE, 3
    h_release

RT_Peeko:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_waitse
    h_playmoncry SPECIES_WINGULL
    h_msgbox 1                      // Peeko: Pii pihyoh!
    h_waitmoncry
    h_release

RT_Grunt:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_playbgm MUS_EVIL_TEAM
    h_msgbox 2                      // Grah, keelhaul it all! ...So you want to battle me?
    h_closemessage
    h_trainerbattle TRAINER_GRUNT_15    // Sapphire TRAINER_RUSTURF_TUNNEL_GRUNT (constants/version.inc)
    h_msgbox_actor 3, RT_GRUNT      // This is plain not right... You want it back that badly? ...
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_DEVON_GOODS
    h_closemessage
    h_applymovement 255, Mv_RT_PlayerMakeWay
    h_applymovement RT_GRUNT, Mv_RT_GruntRunAway
    h_waitmovement
    h_removeobject RT_GRUNT, FLAG_HIDE_GRUNT_RUSTURF_TUNNEL
    h_delay 50
    h_addobject RT_BRINEY, FLAG_HIDE_BRINEY_RUSTURF_TUNNEL
    h_applymovement RT_BRINEY, Mv_RT_BrineyArrive
    h_waitmovement
    h_applymovement 255, Mv_RT_PlayerStepDown
    h_applymovement RT_BRINEY, Mv_RT_BrineyToPeeko
    h_waitmovement
    h_msgbox_actor 4, RT_BRINEY     // Peeko! Am I glad to see you're safe!
    h_closemessage
    h_turnobject RT_BRINEY, 1       // Common_Movement_FacePlayer (the player is just below him)
    ActorMsg MSGFILE_SCRIPT, 5, RT_BRINEY, 0, 0   // Peeko owes her life to you! ...Peeko: Pihyoh!
    h_waitse
    h_playmoncry SPECIES_WINGULL
    LastKeyWait
    h_waitmoncry
    h_closemessage
    h_applymovement RT_BRINEY, Mv_RT_BrineyLeave
    h_applymovement RT_PEEKO, Mv_RT_PeekoLeave
    h_waitmovement
    h_removeobject RT_BRINEY, FLAG_HIDE_BRINEY_RUSTURF_TUNNEL
    h_removeobject RT_PEEKO, FLAG_HIDE_PEEKO_RUSTURF_TUNNEL
    h_clearflag FLAG_DEVON_GOODS_STOLEN
    h_setflag FLAG_RECOVERED_DEVON_GOODS
    h_setvar VAR_RUSTBORO_STATE, 4
    h_setvar VAR_BRINEY_HOUSE_STATE, 1
    h_setflag FLAG_HIDE_BRINEY_ROUTE116
    h_fadedefaultbgm                // (Sapphire's playbgm MUS_EVIL_TEAM, FALSE ends with the map)
    h_release

#include "scenes/RusturfTunnel_Ch3.inc"

    .balign 4, 0
Mv_RT_StepBack:                     // RusturfTunnel_Movement_15C9D3
    lock_facing_direction
    walk_right
    unlock_facing_direction
    step_end
Mv_RT_PlayerMakeWay:                // RusturfTunnel_Movement_15CA99
    face_down
    lock_facing_direction
    walk_up
    unlock_facing_direction
    walk_in_place_fastest_left
    step_end
Mv_RT_PlayerStepDown:               // RusturfTunnel_Movement_15CA9F
    walk_down
    walk_in_place_fastest_up
    step_end
Mv_RT_GruntRunAway:                 // RusturfTunnel_Movement_15CAA2
    walk_fast_left 9
    step_end
Mv_RT_BrineyArrive:                 // RusturfTunnel_Movement_15CAAC
    walk_right 7
    step_end
Mv_RT_BrineyLeave:                  // RusturfTunnel_Movement_15CAB4
    walk_left 11
    step_end
Mv_RT_BrineyToPeeko:                // RusturfTunnel_Movement_15CAC0
    delay_16
    walk_right
    step_end
Mv_RT_PeekoLeave:                   // RusturfTunnel_Movement_15CAC3
    walk_left 9
    step_end
    .balign 4, 0
