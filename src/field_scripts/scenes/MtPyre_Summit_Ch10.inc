// Mt. Pyre's summit after Kyogre was calmed (Sapphire data/maps/MtPyre_Summit/scripts.inc, labels 15D64A .. 15D774; chapter Ch10,
// ch10 agent 2026-10-07). Included by scenes/MtPyre_Summit.inc (ch8b's file, scripts 6-8 = the state-2 triggers and
// Ch10_Pyre_OldWomanReturn = the old woman's branch of FLAG_LEGENDARY_BATTLE_COMPLETED). Text: lines 8-12 of
// src/text/scenes/MtPyre_Summit.txt (T10_* below). The person: Archie (uid 102, FLAG_HIDE_LEADER_MT_PYRE_SUMMIT, cleared by the
// Cave of Origin's Kyogre scene), the old woman (uid 103). The player's trigger tile = C8B_POS 0/1/2 for x = 22/23/24.
#define T10_ReturnedRedOrb 8
#define T10_WhatsThat 9
#define T10_HandedOver 10
#define T10_YesTwoOrbs 11
#define T10_ArchieReturns 12

Ch10_Pyre_OldWomanReturn:               // MtPyre_Summit_EventScript_15D64A (c8b_talk done: she faces the player)
    h_yesno T10_ReturnedRedOrb, C8B_SEL     // That man, he returned the Red Orb. Are you going to return the Blue Orb to its rightful place, too?
    h_goto_if_yes C8B_SEL, L_P10_Return
L_P10_Refused:                          // MtPyre_Summit_EventScript_15D69B
    h_yesno T10_WhatsThat, C8B_SEL      // What's that?! If the balance is not restored, there is no telling what could happen. ...
    h_goto_if_yes C8B_SEL, L_P10_Return
    VMJump L_P10_Refused
L_P10_Return:                           // MtPyre_Summit_EventScript_15D669
    h_closemessage                      // (Black 2: the yes/no bubble is closed before the info window)
    h_handover_item ITEM_RED_OR_BLUE_ORB, T10_HandedOver   // <player> handed over the Blue Orb (Ruby: the Red Orb). (Common_EventScript_PlayerHandedOverTheItem)
    h_applymovement MPS_OLDWOMAN, Mv_P10_FaceUp
    h_waitmovement
    h_delay 40
    h_faceplayer                        // Common_Movement_FacePlayer
    h_delay 10
    h_msgbox T10_YesTwoOrbs             // Yes... The two Orbs should remain here. It is how it should be for the good of all Hoenn...
    h_setflag FLAG_RETURNED_RED_OR_BLUE_ORB
    h_release

Ch10_Pyre_Trigger0:                     // MtPyre_Summit_EventScript_15D6CE: the player came up on (22,7)
    h_setvar C8B_POS, 0
    VMJump L_P10_Scene
Ch10_Pyre_Trigger1:                     // 15D6DA: (23,7)
    h_setvar C8B_POS, 1
    VMJump L_P10_Scene
Ch10_Pyre_Trigger2:                     // 15D6E6: (24,7)
    h_setvar C8B_POS, 2
L_P10_Scene:                            // MtPyre_Summit_EventScript_15D6F2: Archie returns the Red Orb
    h_lock
    WordSetPlayerName 0
    h_applymovement 255, Mv_MPS_PlayerUp
    h_waitmovement
    h_applymovement MPS_ARCHIE, Mv_MPS_ArchieFaceDown
    h_waitmovement
    h_delay 50
    h_call_if_eq C8B_POS, 0, L_P10_ArchieLeft
    h_call_if_eq C8B_POS, 2, L_P10_ArchieRight
    h_msgbox_actor T10_ArchieReturns, MPS_ARCHIE    // Archie: You... So you stopped Kyogre... So I have come to return the Red Orb... Farewell...
    h_closemessage
    h_call_if_eq C8B_POS, 0, L_P10_LeaveRight
    h_call_if_eq C8B_POS, 1, L_P10_LeaveRight
    h_call_if_eq C8B_POS, 2, L_P10_LeaveLeft
    h_removeobject MPS_ARCHIE, FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_setvar VAR_MT_PYRE_STATE, 3
    h_release
L_P10_ArchieLeft:                       // MtPyre_Summit_EventScript_15D75E
    h_applymovement MPS_ARCHIE, Mv_MPS_ArchieLeft
    h_waitmovement
    VMReturn
L_P10_ArchieRight:                      // MtPyre_Summit_EventScript_15D774
    h_applymovement MPS_ARCHIE, Mv_MPS_ArchieRight
    h_waitmovement
    VMReturn
L_P10_LeaveRight:                       // MtPyre_Summit_EventScript_15D77F / 15D78A
    h_applymovement MPS_ARCHIE, Mv_P10_LeaveRight
    h_waitmovement
    VMReturn
L_P10_LeaveLeft:                        // MtPyre_Summit_EventScript_15D795
    h_applymovement MPS_ARCHIE, Mv_P10_LeaveLeft
    h_waitmovement
    VMReturn

    .balign 4, 0
Mv_P10_FaceUp:
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
Mv_P10_LeaveRight:                      // MtPyre_Summit_Movement_15D7A7 / _15D7B0
    walk_right
    walk_down 7
    step_end
    .balign 4, 0
Mv_P10_LeaveLeft:                       // MtPyre_Summit_Movement_15D7B9
    walk_left
    walk_down 7
    step_end
