// MagmaHideout_4F (zone 359, Emerald): converter/gen_caves_emerald.py from emerald/MagmaHideout_4F (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // emerald_ch8_hideout
#include "hoenn_story.inc"  // emerald_ch8_hideout
#include "hoenn_version.inc"  // emerald_ch8_hideout: TRAINER_MAXIE_MAGMA_HIDEOUT (Emerald's names)

    ScriptEntry Script_None
    ScriptEntry MH4F_Maxie  // 2: object 6, Maxie (MagmaHideout_4F_EventScript_Maxie): the awakening scene  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch8, builder B4 emerald_ch8_hideout 2026-10-12; pokeemerald data/maps/MagmaHideout_4F/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). Messages: 0571_room_MagmaHideout_4F.txt (src/text/script/emerald).
// Template: SeafloorCavern_Room9's Archie scene (0380_room_SeafloorCavern_Room9.s): the same Orb, glow, two shakes and Groudon that leaves.
// People (data/story/emerald/e_ch8_hideout.json; uid = pokeemerald's local id): Groudon awake 1 (hidden by FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON,
// a new-game flag) and asleep 7 (FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON_ASLEEP), both at (16,17), Black 2's Groudon model 4512 (the object swap is
// the awakening); the three grunts 2-4 and Tabitha 5 (eye-contact trainers: Black 2's global trainer scripts 3000 + id, no script here;
// the grunts' lines are trainer messages); Maxie 6 at (16,21), who runs this scene when you talk to him; the Max Revive's ball is 8.
// The scene's last lines (pokeemerald :53-57) arm Slateport, which Sapphire's Mt. Pyre scene did: VAR_SLATEPORT_STATE 1 (Emerald's
// VAR_SLATEPORT_CITY_STATE) + Stern and Gabby & Ty appear + VAR_SLATEPORT_HARBOR_STATE 1 (the Aqua escape); FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT
// (Aqua Hideout 1F's guards read it); FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS hides Maxie, the grunts and Tabitha (their hide flag; every grunt of the
// other rooms has it, so the hideout is empty afterwards).
// Black 2 gaps (as Room 9): the orb's coloured glow (DoOrbEffect / FadeOutOrbEffect) and the sparkle (dofieldeffectsparkle) are one white flash
// (FadeOutWhiteQ / FadeInWhiteQ) and the two sounds; the long glow delay (150) is skipped; slide_up is a quick walk; the sounds and the
// awakening jingle are guesses (scenes/ch10_lib.inc C10_SE_*, SEQ_BGM_E_LEGEND_BORN_B: the same as Room 9's).
#include "scenes/ch10_lib.inc"
#include "scenes/em_magma_lib.inc"
#define T_MaxieAwakenGroudon 0          // MagmaHideout_4F_Text_MaxieAwakenGroudon
#define T_MaxieWhatsWrong 1             // MagmaHideout_4F_Text_MaxieGroudonWhatsWrong
#define T_MaxieOhItWasYou 2             // MagmaHideout_4F_Text_MaxieOhItWasYou
#define T_MaxieGoingAfterGroudon 3      // MagmaHideout_4F_Text_MaxieImGoingAfterGroudon
#define MH4F_GROUDON 1                  // LOCALID_MAGMA_HIDEOUT_4F_GROUDON (awake)
#define MH4F_GRUNT_1 2
#define MH4F_GRUNT_2 3
#define MH4F_GRUNT_3 4
#define MH4F_TABITHA 5
#define MH4F_MAXIE 6
#define MH4F_GROUDON_ASLEEP 7           // LOCALID_MAGMA_HIDEOUT_4F_GROUDON_SLEEPING

MH4F_Maxie:                             // MagmaHideout_4F_EventScript_Maxie (lockall: he does not turn to you yet, he speaks to Groudon)
    c10_lock
    em_bgm_magma                        // playbgm MUS_ENCOUNTER_MAGMA, FALSE
    h_msgbox_actor T_MaxieAwakenGroudon, MH4F_MAXIE    // Maxie: Groudon... Nothing could awaken you ... Show me the full extent of your power!
    h_closemessage
    h_delay 20
    SEPlay C10_SE_DETECT                // SE_M_DETECT + dofieldeffectsparkle 18, 42
    h_delay 40
    BGMPlay SEQ_BGM_E_LEGEND_BORN_B     // MUS_AWAKEN_LEGEND [guess]
    SEPlay C10_SE_ORB                   // SE_ORB
    FadeOutWhiteQ                       // special DoOrbEffect: the glow, one white flash
    FadeWait
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_removeobject MH4F_GROUDON_ASLEEP, FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON_ASLEEP
    h_addobject MH4F_GROUDON, FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON
    h_delay 60
    FadeInWhiteQ                        // special FadeOutOrbEffect
    FadeWait
    h_applymovement MH4F_GROUDON, Mv_MH4F_GroudonApproach
    h_waitmovement
    c10_shake 4                         // setvar 8004 1 / 8005 1 / 8006 8 / 8007 5; special ShakeCamera
    h_applymovement MH4F_GROUDON, Mv_MH4F_GroudonExit
    h_waitmovement
    h_removeobject MH4F_GROUDON, FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON
    h_delay 4
    c10_shake 8                         // setvar 8004 2 / 8005 2
    h_delay 30
    h_applymovement MH4F_MAXIE, Mv_MH4F_MaxieLookAround
    h_waitmovement
    h_msgbox_actor T_MaxieWhatsWrong, MH4F_MAXIE       // Maxie: Groudon! What's wrong? Wasn't the Blue Orb the key? Groudon! Where have you gone...
    h_closemessage
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 30
    h_faceplayer                        // Common_Movement_FacePlayer
    h_msgbox_actor T_MaxieOhItWasYou, MH4F_MAXIE       // Maxie: Oh, so it was you? ... You must have pulled a cheap stunt!
    h_closemessage
    h_trainerbattle TRAINER_MAXIE_MAGMA_HIDEOUT        // trainerbattle_no_intro; the defeat line is the trainer's own
    h_msgbox_actor T_MaxieGoingAfterGroudon, MH4F_MAXIE    // Maxie: There has to be some reason why Groudon fled... I am going after Groudon, so this is where we part!
    h_closemessage
    h_clearflag FLAG_HIDE_STERN_SLATEPORT              // Captain Stern and Gabby & Ty appear in Slateport
    h_clearflag FLAG_HIDE_GABBY_AND_TY_SLATEPORT
    h_setvar VAR_SLATEPORT_STATE, 1                    // VAR_SLATEPORT_CITY_STATE
    h_setflag FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT
    h_setvar VAR_SLATEPORT_HARBOR_STATE, 1
    h_fadescreen_black
    h_removeobject MH4F_MAXIE, FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS
    h_removeobject MH4F_GRUNT_1, FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS
    h_removeobject MH4F_GRUNT_2, FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS
    h_removeobject MH4F_GRUNT_3, FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS
    h_removeobject MH4F_TABITHA, FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS
    h_setflag FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS
    h_fadescreen_from_black
    h_release

    .balign 4, 0
Mv_MH4F_GroudonApproach:                // MagmaHideout_4F_Movement_GroudonApproach (= Room 9's Mv_R9_KyogreRises)
    delay_16 2
    walk_slow_down
    delay_16 3
    walk_slow_down
    delay_16 3
    step_end
    .balign 4, 0
Mv_MH4F_GroudonExit:                    // MagmaHideout_4F_Movement_GroudonExit (slide_up x2: Black 2 has no slide, a quick walk)
    walk_fast_up 2
    step_end
    .balign 4, 0
Mv_MH4F_MaxieLookAround:                // MagmaHideout_4F_Movement_MaxieLookAround
    face_left
    delay_16
    face_right
    delay_16
    face_left
    delay_16
    face_right
    delay_16
    face_up
    delay_16 2
    step_end
    .balign 4, 0
#include "common/movement.inc"
    .balign 4, 0
