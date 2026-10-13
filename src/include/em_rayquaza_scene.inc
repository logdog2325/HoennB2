// Emerald's Rayquaza cutscene (emerald_art, 2026-10-12; b2tools/patches/emerald_rayquaza_scene.py and .c): pokeemerald's
// special Script_DoRayquazaScene. Emerald builds only (script command 494 is Black 2's unused TrainerCardCmd_01EE in
// Sapphire and Ruby). Include after "asm/field_script.inc" and "hoenn_music.inc". Emits no code by itself.
//
//     FadeOutBlack                 (Emerald: fadescreenspeed FADE_TO_BLACK, 8 before the special; the screen is black)
//     FadeWait
//     em_rayquaza_scene 0          setvar VAR_0x8004, FALSE + special Script_DoRayquazaScene: the two legends' fight
//                                  (RAY_ANIM_DUO_FIGHT_PRE, then back)
//     em_rayquaza_scene 1          VAR_0x8004 TRUE: the fight, Rayquaza taking flight, coming down, charging, chasing
//                                  them away (RAY_ANIM_DUO_FIGHT ... RAY_ANIM_CHASES_AWAY)
//     FadeInBlack                  (Emerald's return to the field fades in)
//     FadeWait
// The field closes for the scene and opens again after it (Black 2's way of running a screen of its own, as its bag or
// its 3D demos); the scene ends on a black screen. End an event camera before (EvCameraRebind, EvCameraEnd) and start it
// again after: the field's camera is a new one when it opens. With the Hoenn music answer the scene plays and stops the
// music as Emerald's does (mus_rayquaza_appears in the second); with the Unova answer it leaves the music alone.
#ifndef EM_RAYQUAZA_SCENE_INC
#define EM_RAYQUAZA_SCENE_INC

    .macro EmRayquazaScene arg              // bits 0-2 animId, bit 6 that sequence only, bit 7 the Hoenn music answer
    FieldCommand 494
    .2byte \arg
    .endm

    .macro em_rayquaza_scene anim
    h_goto_if_hoenn_music .Lers_hoenn\@
    FieldClose
    EmRayquazaScene \anim
    VMJump .Lers_open\@
.Lers_hoenn\@:
    FieldClose
    EmRayquazaScene (\anim) | 0x80
.Lers_open\@:
    FieldOpen
    ActorsPauseAll                          // (the people the field brings back stand still, as before the scene)
    .endm
#endif
