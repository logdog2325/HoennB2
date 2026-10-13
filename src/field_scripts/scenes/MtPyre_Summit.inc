// Mt. Pyre's summit (Sapphire data/maps/MtPyre_Summit/scripts.inc + data/scripts/magma_summit.inc, Sapphire branches;
// chapter Ch8 part 8b, ch8b agent 2026-10-07). converter/gen_map_content.py includes this file twice in the generated
// zone file 0058_auto_MtPyre_Summit.s: the entries below are scripts 1-8. Text: src/text/scenes/MtPyre_Summit.txt
// (T_* below). People and triggers: data/story/ch8b.json (outdoor uid = 100 + Sapphire local id; the map's own matrix,
// standalone group MtPyre_Summit): the old man (101), Archie (102, FLAG_HIDE_LEADER_MT_PYRE_SUMMIT), the old woman
// (103), the three Aqua grunts (104-106: eye-contact trainers TRAINER_GRUNT_22-24, FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT) and
// the triggers. Sapphire's OnTransition (SetupEvilTeamGfxIds) and the fog (WEATHER_FOG_1 of the map) need nothing here.
// CH10 (Kyogre, notes/STORY_HANDOFFS.md): entries 6-8 are the state-2 triggers (Archie returns the Red Orb, scripts
// 15D6CE/15D6DA/15D6E6) and Ch10_Pyre_OldWomanReturn is the old woman's branch of FLAG_LEGENDARY_BATTLE_COMPLETED
// (15D64A: handing back the Blue Orb): write them in scenes/MtPyre_Summit_Ch10.inc (picked up automatically; text
// lines from 8 on of src/text/scenes/MtPyre_Summit.txt; Archie is uid 102, hidden by FLAG_HIDE_LEADER_MT_PYRE_SUMMIT,
// the old woman uid 103, the old man 101; the player's trigger tile is C8B_POS 0/1/2 for x = 22/23/24).
// EMERALD (emerald_ch45_magma 2026-10-12): the same entries 1-8 with other bodies (scenes/MtPyre_Summit_Em.inc: Archie takes the Red
// Orb, the old woman gives the Magma Emblem, and in state 2 Archie and Maxie return both Orbs) and Emerald's zone init as entry 9
// (the leaders' places in state 2). Text: src/text/scenes/emerald/MtPyre_Summit.txt.
#ifdef SCENE_ENTRIES
    ScriptEntry MPS_OldMan              // 1: object 1 (MtPyre_Summit_EventScript_15D5EF)
    ScriptEntry MPS_OldWoman            // 2: object 3 (15D623)
    ScriptEntry MPS_Trigger0            // 3: trigger (22,7) VAR_MT_PYRE_STATE 0 (15D4BD)
    ScriptEntry MPS_Trigger1            // 4: trigger (23,7) (15D4C9)
    ScriptEntry MPS_Trigger2            // 5: trigger (24,7) (15D4D5)
    ScriptEntry Ch10_Pyre_Trigger0      // 6: trigger (22,7) VAR_MT_PYRE_STATE 2 (Ch10: 15D6CE)
    ScriptEntry Ch10_Pyre_Trigger1      // 7: trigger (23,7) (Ch10: 15D6DA)
    ScriptEntry Ch10_Pyre_Trigger2      // 8: trigger (24,7) (Ch10: 15D6E6)
#ifdef HOENN_EMERALD
    ScriptEntry MPS_EmInit              // 9: Emerald: MtPyre_Summit_OnTransition (zone init; Emerald's triggers 6-8 stand at y = 9)
#endif
#else
#include "scenes/ch8b_lib.inc"
#include "hoenn_version.inc"             // ruby_scenes: ITEM_RED_OR_BLUE_ORB (Sapphire: the Blue Orb, Ruby: the Red Orb)

#define T_Archie 0
#define T_OldWomanOrb 1
#define T_OldWomanBlueRed 2
#define T_OldWomanKyogre 3
#define T_OldWomanSpirit 4
#define T_OldManAsk 5
#define T_OldManTale 6
#define T_OldManFine 7

#define MPS_OLDMAN 101
#define MPS_ARCHIE 102
#define MPS_OLDWOMAN 103
#define MPS_GRUNT1 104
#define MPS_GRUNT2 105
#define MPS_GRUNT3 106
#define MPS_GRUNT4 108                  // Emerald only (data/story/emerald/e_ch8.json)

#ifdef HOENN_EMERALD
#include "scenes/MtPyre_Summit_Em.inc"
#else
MPS_OldMan:                             // MtPyre_Summit_EventScript_15D5EF: the tale of the two Orbs
    c8b_talk
    h_yesno T_OldManAsk, C8B_SEL        // Mt. Pyre is where we calm the spirits of Pokemon that have passed on... Will you hear out my tale?
    h_goto_if_yes C8B_SEL, L_MPS_Tale
    h_msgbox T_OldManFine               // I see... Well, that, too, is fine...
    h_release
L_MPS_Tale:
    h_msgbox T_OldManTale               // It happened long, long ago...
    h_release

MPS_OldWoman:                           // MtPyre_Summit_EventScript_15D623
    c8b_talk
    h_goto_if_set FLAG_RETURNED_RED_OR_BLUE_ORB, L_MPS_Returned
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, Ch10_Pyre_OldWomanReturn
    h_goto_if_set FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, L_MPS_Awoken
    h_msgbox T_OldWomanBlueRed          // The Blue Orb you have been entrusted with and the stolen Red Orb... must never be apart...
    h_release
L_MPS_Awoken:                           // MtPyre_Summit_EventScript_15D6BA
    h_msgbox T_OldWomanKyogre           // So... Kyogre has awoken... The wondrous Orb that is said to have becalmed the raging Kyogre...
    h_release
L_MPS_Returned:                         // MtPyre_Summit_EventScript_15D6C4
    h_msgbox T_OldWomanSpirit           // The spirit of the sea... That is what Kyogre is said to be in Pokemon form...
    h_release

MPS_Trigger0:                           // the player came up on (22,7): Archie steps left to face them
    h_setvar C8B_POS, 0
    VMJump L_MPS_Scene
MPS_Trigger1:                           // (23,7): Archie is right in front
    h_setvar C8B_POS, 1
    VMJump L_MPS_Scene
MPS_Trigger2:                           // (24,7)
    h_setvar C8B_POS, 2
L_MPS_Scene:                            // MtPyre_Summit_EventScript_15D4E1: Archie takes the Red Orb
    h_lock
    h_applymovement 255, Mv_MPS_PlayerUp
    h_waitmovement
    h_applymovement MPS_ARCHIE, Mv_MPS_ArchieFaceDown
    h_waitmovement
    h_delay 50
    h_call_if_eq C8B_POS, 0, L_MPS_ArchieLeft
    h_call_if_eq C8B_POS, 2, L_MPS_ArchieRight
    h_msgbox_actor T_Archie, MPS_ARCHIE         // Archie: Not you again... The Red Orb that rested atop Mt. Pyre... I, Archie, claim it as mine! ... It's Slateport next!
    h_closemessage
    h_fadescreen_black
    h_removeobject MPS_ARCHIE, FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_removeobject MPS_GRUNT1, FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT
    h_removeobject MPS_GRUNT2, FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT
    h_removeobject MPS_GRUNT3, FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT
    h_fadescreen_from_black
    h_delay 20
    h_setflag FLAG_MT_PYRE_ORB_STOLEN           // MtPyre_Summit_EventScript_15D57A: the Slateport scene is armed
    h_setvar VAR_SLATEPORT_STATE, 1
    h_clearflag FLAG_HIDE_STERN_SLATEPORT
    h_clearflag FLAG_HIDE_GABBY_AND_TY_SLATEPORT
    h_setvar VAR_SLATEPORT_HARBOR_STATE, 1
    h_setvar VAR_MT_PYRE_STATE, 1
    h_call_if_eq C8B_POS, 0, L_MPS_WomanLeft
    h_call_if_eq C8B_POS, 1, L_MPS_WomanMiddle
    h_call_if_eq C8B_POS, 2, L_MPS_WomanRight
    h_msgbox_actor T_OldWomanOrb, MPS_OLDWOMAN  // Oh, no... This cannot happen... How could they take the Red Orb? ... You take the remaining Blue Orb.
    h_closemessage
    h_giveitem ITEM_RED_OR_BLUE_ORB             // Sapphire: the Blue Orb (the old woman keeps it for the player), Ruby: the Red Orb (hoenn_version.inc)
    h_setflag FLAG_RECEIVED_RED_OR_BLUE_ORB
    h_release

L_MPS_ArchieLeft:                       // MtPyre_Summit_EventScript_15D593
    h_applymovement MPS_ARCHIE, Mv_MPS_ArchieLeft
    h_waitmovement
    VMReturn
L_MPS_ArchieRight:                      // MtPyre_Summit_EventScript_15D59F
    h_applymovement MPS_ARCHIE, Mv_MPS_ArchieRight
    h_waitmovement
    VMReturn
L_MPS_WomanLeft:                        // MtPyre_Summit_EventScript_15D5AA
    h_applymovement MPS_OLDWOMAN, Mv_MPS_WomanLeft
    h_waitmovement
    h_applymovement 255, Mv_MPS_PlayerRight
    h_waitmovement
    VMReturn
L_MPS_WomanMiddle:                      // MtPyre_Summit_EventScript_15D5BF
    h_applymovement MPS_OLDWOMAN, Mv_MPS_WomanMiddle
    h_waitmovement
    VMReturn
L_MPS_WomanRight:                       // MtPyre_Summit_EventScript_15D5CA
    h_applymovement MPS_OLDWOMAN, Mv_MPS_WomanRight
    h_waitmovement
    h_applymovement 255, Mv_MPS_PlayerLeft
    h_waitmovement
    VMReturn

    .balign 4, 0
Mv_MPS_PlayerUp:
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
Mv_MPS_PlayerRight:
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_MPS_PlayerLeft:
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
Mv_MPS_ArchieFaceDown:
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_MPS_ArchieLeft:                      // MtPyre_Summit_Movement_15D5E9
    walk_left
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_MPS_ArchieRight:                     // MtPyre_Summit_Movement_15D5EC
    walk_right
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_MPS_WomanLeft:                       // MtPyre_Summit_Movement_15D5DF
    walk_down 2
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
Mv_MPS_WomanMiddle:                     // MtPyre_Summit_Movement_15D5E3
    walk_down
    step_end
    .balign 4, 0
Mv_MPS_WomanRight:                      // MtPyre_Summit_Movement_15D5E5
    walk_down 2
    walk_in_place_fastest_right
    step_end

#if __has_include("scenes/MtPyre_Summit_Ch10.inc")
#include "scenes/MtPyre_Summit_Ch10.inc"
#else
Ch10_Pyre_OldWomanReturn:               // stand-in until Ch10 (15D64A: the Blue Orb goes back to the old woman)
    h_release
Ch10_Pyre_Trigger0:                     // stand-ins until Ch10 (15D6CE/15D6DA/15D6E6: Archie returns the Red Orb)
Ch10_Pyre_Trigger1:
Ch10_Pyre_Trigger2:
    VMHalt
#endif
#endif
#endif
