// Mt. Pyre's summit, EMERALD's bodies (emerald_ch45_magma 2026-10-12; pokeemerald data/maps/MtPyre_Summit/scripts.inc). Included by
// scenes/MtPyre_Summit.inc under #ifdef HOENN_EMERALD in place of the Sapphire bodies (the same entries, 1-8, plus Emerald's
// zone init as entry 9): the nine labels below are the ones its ScriptEntry list names. Text: src/text/scenes/emerald/MtPyre_Summit.txt
// (same indices as Sapphire's file for the lines both have; T_* in MtPyre_Summit.inc, MPE_T_* here).
// What Emerald does differently from Sapphire here:
//  * Archie takes the RED ORB in front of you (Maxie of Team Magma got the Blue Orb first); the old woman gives you the MAGMA EMBLEM
//    (a key item: ITEM_MAGMA_EMBLEM = Black 2's Magma Stone, src/include/hoenn_version.inc), left behind by Team Magma, instead of
//    an Orb; it opens the Jagged Pass hideout (scenes/JaggedPass.inc).
//  * four Aqua grunts (the fourth is TRAINER_GRUNT_MT_PYRE_4, data/story/emerald/e_ch8.json), all removed by Archie's exit.
//  * the Slateport scene is NOT armed here (Sapphire's FLAG_MT_PYRE_ORB_STOLEN, VAR_SLATEPORT_STATE 1, Stern / Gabby & Ty and
//    VAR_SLATEPORT_HARBOR_STATE 1): Emerald does it at the end of the Magma Hideout (MagmaHideout_4F, builder B4: work list in
//    notes/EMERALD_STORY.md "Magma Hideout work list").
//  * the three state-2 triggers (two rows lower, y = 9): Archie AND Maxie return the Orbs (VAR_MT_PYRE_STATE 2 -> 3). Ch10 (Sootopolis,
//    FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE) sets the state and clears both hide flags; the old woman needs no handing back.
//  * the old man tells a new tale after Sootopolis (FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE).
//  * playbgm MUS_ENCOUNTER_AQUA / fadedefaultbgm around Archie's exit.
// NPC indices of ObjInitNPCGPos (zone 29's NPC list in data/story order: the old man 0, Archie 1, the old woman 2, the grunts 3-5,
// then data/story/emerald/e_ch8.json: Maxie 6, the fourth grunt 7).
#include "scenes/em_magma_lib.inc"
#define MPE_T_OrbsReturned 8            // "The two men who took the ORBS came back to return them" (Sapphire's T10_ReturnedRedOrb slot)
#define MPE_T_MaxieSilence 12           // "MAXIE: <player>... ..." (Sapphire's T10_ArchieReturns slot)
#define MPE_T_NewLegend 13              // appended lines
#define MPE_T_HoennTrio 14
#define MPE_ARCHIE_IDX 1
#define MPE_MAXIE_IDX 6
#define MPE_MAXIE 107                   // uid
// zone tiles of the summit's own matrix (standalone group MtPyre_Summit, b2tools/world.py: the map sits at (24, 14))
#define MPE_X0 24
#define MPE_Z0 14

#ifdef HOENN_TEST_CH8B
#include "scenes/ch8b_test.inc"          // test builds only: HOENN_TEST_CH8B=1/2 as the chapter's kit; 3 = also Sootopolis over (state 2)
#endif
MPS_EmInit:                             // MtPyre_Summit_OnTransition: state 2, Archie and Maxie stand side by side
#ifdef HOENN_TEST_CH8B
    VMCall Test_Ch8bStart
#if (HOENN_TEST_CH8B + 0) >= 3
    h_setvar VAR_MT_PYRE_STATE, 2
    h_clearflag FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_clearflag FLAG_HIDE_MT_PYRE_SUMMIT_MAXIE
    h_setflag FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE
#endif
#endif
    h_goto_if_ne VAR_MT_PYRE_STATE, 2, L_MPE_InitDone
    h_setobjectxyperm MPE_MAXIE_IDX, MPE_X0 + 23, MPE_Z0 + 6, 0
    h_setobjectxyperm MPE_ARCHIE_IDX, MPE_X0 + 22, MPE_Z0 + 6, 0
L_MPE_InitDone:
    VMHalt

MPS_OldMan:                             // MtPyre_Summit_EventScript_OldMan
    c8b_talk
    h_goto_if_set FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE, L_MPE_OldManNew
    h_yesno T_OldManAsk, C8B_SEL        // Mt. Pyre is where we calm the spirits of Pokémon that have passed on... Will you hear out my tale?
    h_goto_if_yes C8B_SEL, L_MPE_Tale
L_MPE_Decline:
    h_msgbox T_OldManFine               // I see... Well, that, too, is fine...
    h_release
L_MPE_Tale:
    h_msgbox T_OldManTale               // It happened long, long ago...
    h_release
L_MPE_OldManNew:
    h_yesno MPE_T_NewLegend, C8B_SEL    // It is my role to pass on the legends of Hoenn... Have you the time to hear the new legend of Hoenn?
    h_goto_if_no C8B_SEL, L_MPE_Decline
    h_msgbox MPE_T_HoennTrio
    h_release

MPS_OldWoman:                           // MtPyre_Summit_EventScript_OldLady
    c8b_talk
    h_goto_if_set FLAG_RETURNED_RED_OR_BLUE_ORB, L_MPE_Returned
    h_goto_if_lt VAR_MT_PYRE_STATE, 3, L_MPE_NotReturned
    h_msgbox MPE_T_OrbsReturned         // The two men who took the Orbs came back to return them on their own. ...
    h_setflag FLAG_RETURNED_RED_OR_BLUE_ORB
    h_release
L_MPE_NotReturned:
    h_goto_if_set FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, L_MPE_Awake      // FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN
    h_msgbox T_OldWomanBlueRed          // The Blue Orb and Red Orb taken by those sinister men... They must never be apart...
    h_release
L_MPE_Awake:
    h_msgbox T_OldWomanKyogre           // Oh, my goodness... You say that both Groudon and Kyogre have been awakened? ...
    h_release
L_MPE_Returned:
    h_msgbox T_OldWomanSpirit           // The embodiments of the land, sea, and the sky... That is said to be the identities of the super-ancient Pokémon...
    h_release

MPS_Trigger0:                           // MtPyre_Summit_EventScript_TeamAquaTrigger0 (the player came up on (22,7))
    h_setvar C8B_POS, 0
    VMJump L_MPE_Scene
MPS_Trigger1:
    h_setvar C8B_POS, 1
    VMJump L_MPE_Scene
MPS_Trigger2:
    h_setvar C8B_POS, 2
L_MPE_Scene:                            // MtPyre_Summit_EventScript_TeamAquaExits: Archie has the Red Orb, the old woman gives the Emblem
    h_lock
    em_bgm_aqua                         // playbgm MUS_ENCOUNTER_AQUA
    h_applymovement 255, MPE_Mv_PlayerUp
    h_waitmovement
    h_applymovement MPS_ARCHIE, MPE_Mv_ArchieFaceDown
    h_waitmovement
    h_delay 50
    h_call_if_eq C8B_POS, 0, L_MPE_ArchieLeft
    h_call_if_eq C8B_POS, 2, L_MPE_ArchieRight
    h_msgbox_actor T_Archie, MPS_ARCHIE // Archie: Team Magma's Maxie got ahead of us, but we also got what we wanted. The Red Orb ... We're pulling out!
    h_closemessage
    h_fadescreen_black
    h_removeobject MPS_ARCHIE, FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_removeobject MPS_GRUNT1, FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT
    h_removeobject MPS_GRUNT2, FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT
    h_removeobject MPS_GRUNT3, FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT
    h_removeobject MPS_GRUNT4, FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT
    h_fadedefaultbgm
    h_fadescreen_from_black
    h_delay 20
    h_setvar VAR_MT_PYRE_STATE, 1
    h_call_if_eq C8B_POS, 0, L_MPE_WomanLeft
    h_call_if_eq C8B_POS, 1, L_MPE_WomanMiddle
    h_call_if_eq C8B_POS, 2, L_MPE_WomanRight
    h_msgbox_actor T_OldWomanOrb, MPS_OLDWOMAN  // Oh, no... This cannot happen... Not only the Blue Orb, but even the Red Orb has been taken... Well, in their haste, they left this behind. ...
    h_closemessage
    h_giveitem ITEM_MAGMA_EMBLEM
    h_setflag FLAG_RECEIVED_RED_OR_BLUE_ORB
    h_setflag FLAG_HIDE_JAGGED_PASS_MAGMA_GUARD    // the Jagged Pass guard leaves his post with the Emblem gone
    h_release

L_MPE_ArchieLeft:                       // MtPyre_Summit_Movement_ArchieFacePlayer0
    h_applymovement MPS_ARCHIE, MPE_Mv_ArchieLeft
    h_waitmovement
    VMReturn
L_MPE_ArchieRight:                      // ... Player2
    h_applymovement MPS_ARCHIE, MPE_Mv_ArchieRight
    h_waitmovement
    VMReturn
L_MPE_WomanLeft:                        // MtPyre_Summit_EventScript_OldLadyApproachPlayer0
    h_applymovement MPS_OLDWOMAN, MPE_Mv_WomanLeft
    h_waitmovement
    h_applymovement 255, MPE_Mv_PlayerRight
    h_waitmovement
    VMReturn
L_MPE_WomanMiddle:
    h_applymovement MPS_OLDWOMAN, MPE_Mv_WomanMiddle
    h_waitmovement
    VMReturn
L_MPE_WomanRight:
    h_applymovement MPS_OLDWOMAN, MPE_Mv_WomanRight
    h_waitmovement
    h_applymovement 255, MPE_Mv_PlayerLeft
    h_waitmovement
    VMReturn

// ---- state 2: Archie and Maxie bring both Orbs back (MtPyre_Summit_EventScript_ArchieMaxieReturnOrbs) ----------------------------
Ch10_Pyre_Trigger0:                     // the player came up on (22,9)
    h_setvar C8B_POS, 0
    VMJump L_MPE_Return
Ch10_Pyre_Trigger1:                     // (23,9)
    h_setvar C8B_POS, 1
    VMJump L_MPE_Return
Ch10_Pyre_Trigger2:                     // (24,9)
    h_setvar C8B_POS, 2
L_MPE_Return:
    h_lock
    WordSetPlayerName 0
    h_applymovement 255, MPE_Mv_PlayerUp
    h_waitmovement
    h_delay 60
    h_call_if_eq C8B_POS, 0, L_MPE_Exit0    // the two leaders walk past the player, down the mountain
    h_call_if_eq C8B_POS, 1, L_MPE_Exit1
    h_call_if_eq C8B_POS, 2, L_MPE_Exit2
    h_applymovement MPE_MAXIE, Common_Movement_ExclamationMark      // playse SE_PIN + "!": Maxie notices the player
    h_waitmovement
    h_applymovement MPE_MAXIE, Common_Movement_Delay48
    h_waitmovement
    h_delay 30
    h_call_if_eq C8B_POS, 0, L_MPE_MaxieToPlayer0
    h_call_if_eq C8B_POS, 1, L_MPE_MaxieToPlayer1
    h_call_if_eq C8B_POS, 2, L_MPE_MaxieToPlayer2
    h_msgbox_actor MPE_T_MaxieSilence, MPE_MAXIE    // MAXIE: <player>... ... ... ... ... ...
    h_closemessage
    h_call_if_eq C8B_POS, 0, L_MPE_MaxieToArchie0
    h_call_if_eq C8B_POS, 1, L_MPE_MaxieToArchie1
    h_call_if_eq C8B_POS, 2, L_MPE_MaxieToArchie1
    h_applymovement MPS_ARCHIE, MPE_Mv_ArchieFaceMaxie
    h_waitmovement
    h_delay 30
    h_applymovement MPS_ARCHIE, MPE_Mv_LeaderExit
    h_applymovement MPE_MAXIE, MPE_Mv_LeaderExit
    h_waitmovement
    h_removeobject MPS_ARCHIE, FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_removeobject MPE_MAXIE, FLAG_HIDE_MT_PYRE_SUMMIT_MAXIE
    h_setvar VAR_MT_PYRE_STATE, 3
    h_release

L_MPE_Exit0:                            // MtPyre_Summit_EventScript_ArchieMaxieBeginExit0 (the player steps left out of the way)
    h_applymovement 255, MPE_Mv_PlayerWatch0
    h_applymovement MPS_ARCHIE, MPE_Mv_LeaderExit
    h_applymovement MPE_MAXIE, MPE_Mv_LeaderExit
    h_waitmovement
    VMReturn
L_MPE_Exit1:                            // (steps right)
    h_applymovement 255, MPE_Mv_PlayerWatch1
    h_applymovement MPS_ARCHIE, MPE_Mv_LeaderExit
    h_applymovement MPE_MAXIE, MPE_Mv_LeaderExit
    h_waitmovement
    VMReturn
L_MPE_Exit2:
    h_applymovement 255, MPE_Mv_PlayerWatch2
    h_applymovement MPS_ARCHIE, MPE_Mv_LeaderExit
    h_applymovement MPE_MAXIE, MPE_Mv_LeaderExit
    h_waitmovement
    VMReturn
L_MPE_MaxieToPlayer0:                   // MtPyre_Summit_EventScript_MaxieApproachPlayer0
    h_applymovement 255, MPE_Mv_PlayerFaceMaxie0
    h_applymovement MPS_ARCHIE, MPE_Mv_ArchieWatchMaxie
    h_applymovement MPE_MAXIE, MPE_Mv_MaxieToPlayer0
    h_waitmovement
    VMReturn
L_MPE_MaxieToPlayer1:
    h_applymovement 255, MPE_Mv_PlayerFaceMaxie
    h_applymovement MPS_ARCHIE, MPE_Mv_ArchieWatchMaxie
    h_applymovement MPE_MAXIE, MPE_Mv_MaxieToPlayer1
    h_waitmovement
    VMReturn
L_MPE_MaxieToPlayer2:
    h_applymovement 255, MPE_Mv_PlayerFaceMaxie
    h_applymovement MPS_ARCHIE, MPE_Mv_ArchieWatchMaxie
    h_applymovement MPE_MAXIE, MPE_Mv_MaxieToPlayer1    // (the same steps as position 1 in pokeemerald)
    h_waitmovement
    VMReturn
L_MPE_MaxieToArchie0:                   // MtPyre_Summit_EventScript_MaxieApproachArchie0
    h_applymovement 255, MPE_Mv_PlayerWatchMaxie
    h_applymovement MPE_MAXIE, MPE_Mv_MaxieToArchie0
    h_waitmovement
    VMReturn
L_MPE_MaxieToArchie1:                   // ... Archie1 / Archie2
    h_applymovement 255, MPE_Mv_PlayerWatchMaxie
    h_applymovement MPE_MAXIE, MPE_Mv_MaxieToArchie1
    h_waitmovement
    VMReturn

    .balign 4, 0
MPE_Mv_PlayerUp:
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
MPE_Mv_PlayerRight:
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
MPE_Mv_PlayerLeft:
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
MPE_Mv_ArchieFaceDown:
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
MPE_Mv_ArchieLeft:                      // MtPyre_Summit_Movement_ArchieFacePlayer0
    walk_left
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
MPE_Mv_ArchieRight:                     // ... FacePlayer2
    walk_right
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
MPE_Mv_WomanLeft:                       // MtPyre_Summit_Movement_OldLadyApproachPlayer0
    walk_down 2
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
MPE_Mv_WomanMiddle:
    walk_down
    step_end
    .balign 4, 0
MPE_Mv_WomanRight:
    walk_down 2
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
MPE_Mv_LeaderExit:                      // MtPyre_Summit_Movement_ArchieExit / MaxieExit
    walk_down 6
    step_end
    .balign 4, 0
MPE_Mv_PlayerWatch0:                    // MtPyre_Summit_Movement_PlayerWatchArchieMaxieExit0
    delay_16
    delay_8
    walk_left
    walk_in_place_fastest_right
    delay_16
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
MPE_Mv_PlayerWatch1:
    delay_16
    delay_8
    walk_right
    walk_in_place_fastest_left
    delay_16
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
MPE_Mv_PlayerWatch2:
    delay_16
    delay_8
    walk_in_place_fastest_left
    delay_16
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
MPE_Mv_PlayerFaceMaxie0:                // MtPyre_Summit_Movement_PlayerFaceMaxie0
    delay_16 2
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
MPE_Mv_PlayerFaceMaxie:
    delay_16 2
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
MPE_Mv_MaxieToPlayer0:                  // MtPyre_Summit_Movement_MaxieApproachPlayer0
    walk_up 3
    walk_left
    step_end
    .balign 4, 0
MPE_Mv_MaxieToPlayer1:                  // ... Player1 / Player2
    walk_up 3
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
MPE_Mv_ArchieWatchMaxie:
    delay_16
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
MPE_Mv_PlayerWatchMaxie:
    delay_16
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
MPE_Mv_MaxieToArchie0:                  // MtPyre_Summit_Movement_MaxieApproachArchie0
    walk_down
    walk_right
    walk_down 2
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
MPE_Mv_MaxieToArchie1:                  // ... Archie1 / Archie2
    walk_down 3
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
MPE_Mv_ArchieFaceMaxie:                 // applywaitmovement ARCHIE, WalkInPlaceFasterRight
    walk_in_place_fastest_right
    step_end
#include "common/movement.inc"
