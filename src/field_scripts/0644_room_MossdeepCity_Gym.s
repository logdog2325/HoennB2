// MossdeepCity_Gym (zone 322, big room by the gyms_league agent): chapter Ch9 (Sapphire data/maps/MossdeepCity_Gym/
// scripts.inc): Tate and Liza, the Mind Badge and TM04, the guide, the statues, the four floor switches and the warp
// pad that sends you back to the entrance. Messages: src/text/script/0521_room_MossdeepCity_Gym.txt. Map scripts: 0645
// (none: the switch flags are cleared by Mossdeep City's zone init, as Sapphire's MossdeepCity_OnTransition does).
// Room tiles = Sapphire tiles + (1, 0) (room.json origin). People (data/story/ch9.json, uid = Sapphire local id): Tate
// 1 and Liza 9 (both run script 1), the guide 8, Preston 2, Fritz 3, Maura 4, Samantha 5, Virgil 6 and Hannah 7
// (Black 2 eye-contact trainers: global script 3000 + id), the statues' plaques (7,27) / (11,27) (script 3), the
// switches (2,7) (8,10) (17,15) (5,24) (scripts 4-7) and the warp pad's step trigger (12,3) (script 8).
// Tate and Liza are two trainers fought together (user choice; notes/STORY_PORTING.md section 5): h_trainerbattle_two.
// Not here: the conveyor belts. Sapphire's Gym floor is a maze of arrow tiles (MB_WALK_* / MB_SLIDE_*) that carry the
// player and that the four switches turn (setmetatile + DrawWholeMapView); the room builder draws the arrows but Black
// 2 has no such tile class, so the floor is walkable everywhere the maze is open (notes/INTERIORS.md). The switches
// still toggle FLAG_MOSSDEEP_GYM_SWITCH_1-4 (cleared by every entry into the city) and click, nothing turns.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
#include "hoenn_story.inc"

    ScriptEntry MG_TateAndLiza          // 1: MossdeepCity_Gym_EventScript_TateAndLiza (objects 1 and 9)
    ScriptEntry MG_GymGuide             // 2: MossdeepCity_Gym_EventScript_GymGuide (object 8)
    ScriptEntry MG_GymStatue            // 3: MossdeepCity_Gym_EventScript_LeftGymStatue / RightGymStatue
    ScriptEntry MG_Switch1              // 4: MossdeepCity_Gym_EventScript_Switch1 (sign (2,7))
    ScriptEntry MG_Switch2              // 5: Switch2 (sign (8,10))
    ScriptEntry MG_Switch3              // 6: Switch3 (sign (17,15))
    ScriptEntry MG_Switch4              // 7: Switch4 (sign (5,24))
    ScriptEntry MG_WarpToEntrance       // 8: MossdeepCity_Gym_EventScript_WarpToEntrance (coord (12,3))
// >>> emerald_rooms mossdeep_entries (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
    ScriptEntry EMG_SwitchYellow    // 9: Yellow floor switch(es) [(2, 21), (3, 30)] (Emerald only)
    ScriptEntry EMG_SwitchBlue      // 10: Blue floor switch(es) [(8, 10), (6, 7)] (Emerald only)
    ScriptEntry EMG_SwitchGreen     // 11: Green floor switch(es) [(15, 34)] (Emerald only)
    ScriptEntry EMG_SwitchPurple    // 12: Purple floor switch(es) [(23, 24), (23, 21)] (Emerald only)
    ScriptEntry EMG_SwitchRed       // 13: Red floor switch(es) [(8, 6)] (Emerald only)
    ScriptEntry EMG_Pad2            // 14: warp pad (Emerald only)
    ScriptEntry EMG_Pad3            // 15: warp pad (Emerald only)
    ScriptEntry EMG_Pad4            // 16: warp pad (Emerald only)
    ScriptEntry EMG_Pad5            // 17: warp pad (Emerald only)
    ScriptEntry EMG_Pad6            // 18: warp pad (Emerald only)
    ScriptEntry EMG_Pad7            // 19: warp pad (Emerald only)
    ScriptEntry EMG_Pad8            // 20: warp pad (Emerald only)
    ScriptEntry EMG_Pad9            // 21: warp pad (Emerald only)
    ScriptEntry EMG_Pad10           // 22: warp pad (Emerald only)
    ScriptEntry EMG_Pad11           // 23: warp pad (Emerald only)
    ScriptEntry EMG_Pad12           // 24: warp pad (Emerald only)
    ScriptEntry EMG_Pad13           // 25: warp pad (Emerald only)
#endif
// <<< emerald_rooms mossdeep_entries
    ScriptEntriesEnd

#define T_ReceivedMindBadge 0
#define T_ExplainMindBadgeTakeThis 1
#define T_ExplainCalmMind 2
#define T_GymGuideAdvice 3
#define T_GymGuidePostVictory 4
#define T_GymStatue 5
#define T_GymStatueCertified 6
#define T_BagFull 7
#define T_TateAndLizaPostBattle 8
#define MG_TATE 1
#define MG_GUIDE 8
#define MG_ENTRANCE_X 15                // Sapphire (14,29) + the room origin (1,0)
#define MG_ENTRANCE_Z 29
// >>> emerald_rooms mossdeep_entrance (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
#undef MG_ENTRANCE_X
#undef MG_ENTRANCE_Z
#define MG_ENTRANCE_X 8                // Emerald (7,30) + the room origin
#define MG_ENTRANCE_Z 32
#endif
// <<< emerald_rooms mossdeep_entrance

MG_TateAndLiza:                         // trainerbattle_double TRAINER_TATE_AND_LIZA, ..., NO_MUSIC
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_defeated TRAINER_TATE, L_MG_AfterBattle    // both flags are set together: the script after the battle
    h_goto_if_cannot_double L_MG_NeedTwoMons
    TrainerSayMessage TRAINER_TATE, 0, MG_TATE           // Tate: Hehehe... Were you surprised? ... Liza: Can you beat it?
    ActorMsgClose                                        // (NO_MUSIC: no eye-contact music)
    h_trainerbattle_two TRAINER_TATE, TRAINER_LIZA       // (in battle: "Tate: What?! Our combination... Liza: Was shattered!" ...)
    h_buffer_player                                      // MossdeepCity_Gym_EventScript_TateAndLizaDefeated
    SystemMsg T_ReceivedMindBadge, 2                     // <player> received the Mind Badge from Liza and Tate.
    h_badge_fanfare                                      // Common_EventScript_PlayGymBadgeFanfare
    MsgWinCloseAll
    h_msgbox_actor T_ExplainMindBadgeTakeThis, MG_TATE   // Tate: The Mind Badge enhances the Sp. Atk and Sp. Def ...
    h_closemessage
    h_setflag FLAG_DEFEATED_MOSSDEEP_GYM
    h_givebadge 7                                        // setflag FLAG_BADGE07_GET
    h_clearflag FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD      // Mr. Briney joins Dock at the Slateport shipyard
    h_clearflag FLAG_UNKNOWN_393
    h_set_gym_trainers 7                                 // Preston, Virgil, Fritz, Hannah, Samantha and Maura count as beaten
    h_clearflag FLAG_HIDE_WORKERS_SLATEPORT_HARBOR
#ifdef HOENN_EMERALD
    // EMERALD (emerald_ch9_mirage 2026-10-12; pokeemerald MossdeepCity_Gym_EventScript_TateAndLizaDefeated): Team Magma moves in on the
    // Space Center: Maxie and four grunts in town, the grunts of 1F and 2F (scenes/emerald/MossdeepCity_Magma.inc, emerald/0670, 0676)
    h_clearflag FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_clearflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_1F_TEAM_MAGMA
    h_clearflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA
    h_clearflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_STEVEN
    h_setvar VAR_MOSSDEEP_CITY_STATE, 1
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_1F_STEVEN
    h_setvar VAR_MOSSDEEP_SPACE_CENTER_STATE, 1
#endif
L_MG_GiveCalmMind:                      // MossdeepCity_Gym_EventScript_GiveCalmMind2
    h_giveitem ITEM_TM04                // TM04 Calm Mind (Black 2's TM04 is Calm Mind too)
    h_goto_if_eq HLIB_RESULT, 0, L_MG_BagFull
    h_msgbox_actor T_ExplainCalmMind, MG_TATE   // Tate: That TM04 contains... Liza: Calm Mind! ...
    h_setflag FLAG_RECEIVED_TM_CALM_MIND
    h_release
L_MG_AfterBattle:
    h_goto_if_unset FLAG_RECEIVED_TM_CALM_MIND, L_MG_GiveCalmMind
    h_msgbox_actor T_TateAndLizaPostBattle, MG_TATE      // Tate: Looks like the bond between you and your Pokémon ...
    h_release
L_MG_NeedTwoMons:
    TrainerSayMessage TRAINER_TATE, 6, MG_TATE           // Tate: Oops, you have only one... Liza: Pokémon that can battle. ...
    LastKeyWait
    ActorMsgClose
    h_release
L_MG_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release

MG_GymGuide:                            // MossdeepCity_Gym_EventScript_GymGuide
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_set FLAG_DEFEATED_MOSSDEEP_GYM, L_MG_GuideVictory
    h_msgbox T_GymGuideAdvice           // Yo, how's it going, Champion-bound {PLAYER}? ...
    h_release
L_MG_GuideVictory:
    h_msgbox T_GymGuidePostVictory      // Wow, you're astounding! You're one great Trainer!
    h_release

MG_GymStatue:                           // MossdeepCity_Gym_EventScript_LeftGymStatue / RightGymStatue (lockall; MSGBOX_DEFAULT)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_badge 7, L_MG_StatueCertified
    h_msgbox_info T_GymStatue           // Mossdeep City Pokémon Gym
    h_closemessage
    h_release
L_MG_StatueCertified:
    h_buffer_player
    h_msgbox_info T_GymStatueCertified  // Mossdeep City Pokémon Gym / Liza And Tate's Certified Trainers: {PLAYER}
    h_closemessage
    h_release

// The four floor switches: Sapphire's Switch1-4 toggle their flag, wait delay_16 x 2 (MossdeepCity_Gym_Movement_
// WaitAfterSwitchUse), turn two arrows and the switch tile (setmetatile: not possible here, see the top), redraw, click.
MG_Switch1:                             // MossdeepCity_Gym_EventScript_Switch1 (lockall)
    h_lock
    h_goto_if_set FLAG_MOSSDEEP_GYM_SWITCH_1, L_MG_ClearSwitch1
    h_setflag FLAG_MOSSDEEP_GYM_SWITCH_1
    VMSleep 16                          // delay_16 delay_16 (Gen 3 frames: 32 / 2)
    SEPlay SEQ_SE_DECIDE1               // SE_CLICK
    h_release
L_MG_ClearSwitch1:                      // MossdeepCity_Gym_EventScript_ClearSwitch1
    h_clearflag FLAG_MOSSDEEP_GYM_SWITCH_1
    VMSleep 16
    SEPlay SEQ_SE_DECIDE1
    h_release

MG_Switch2:                             // MossdeepCity_Gym_EventScript_Switch2
    h_lock
    h_goto_if_set FLAG_MOSSDEEP_GYM_SWITCH_2, L_MG_ClearSwitch2
    h_setflag FLAG_MOSSDEEP_GYM_SWITCH_2
    VMSleep 16
    SEPlay SEQ_SE_DECIDE1
    h_release
L_MG_ClearSwitch2:
    h_clearflag FLAG_MOSSDEEP_GYM_SWITCH_2
    VMSleep 16
    SEPlay SEQ_SE_DECIDE1
    h_release

MG_Switch3:                             // MossdeepCity_Gym_EventScript_Switch3
    h_lock
    h_goto_if_set FLAG_MOSSDEEP_GYM_SWITCH_3, L_MG_ClearSwitch3
    h_setflag FLAG_MOSSDEEP_GYM_SWITCH_3
    VMSleep 16
    SEPlay SEQ_SE_DECIDE1
    h_release
L_MG_ClearSwitch3:
    h_clearflag FLAG_MOSSDEEP_GYM_SWITCH_3
    VMSleep 16
    SEPlay SEQ_SE_DECIDE1
    h_release

MG_Switch4:                             // MossdeepCity_Gym_EventScript_Switch4
    h_lock
    h_goto_if_set FLAG_MOSSDEEP_GYM_SWITCH_4, L_MG_ClearSwitch4
    h_setflag FLAG_MOSSDEEP_GYM_SWITCH_4
    VMSleep 16
    SEPlay SEQ_SE_DECIDE1
    h_release
L_MG_ClearSwitch4:
    h_clearflag FLAG_MOSSDEEP_GYM_SWITCH_4
    VMSleep 16
    SEPlay SEQ_SE_DECIDE1
    h_release

MG_WarpToEntrance:                      // MossdeepCity_Gym_EventScript_WarpToEntrance: warpteleport MAP_MOSSDEEP_CITY_GYM, 255, 14, 29
    h_lock                              // (a map change to the same zone hangs on black in Black 2: the player is set down
    SEPlay SEQ_SE_KAIDAN                //  on the entrance tile behind a fade, as Black 2's own scripts do: 0014.s Script_16)
    h_fadescreen_black
    ActorSetGPos 255, MG_ENTRANCE_X, 0, MG_ENTRANCE_Z, 0
    h_fadescreen_from_black
    h_release
    .balign 4, 0

// ---- story (emerald_rooms: the Emerald build's own scripts below; generators keep everything from this line on)

// >>> emerald_rooms mossdeep_puzzle (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
EMG_SwitchYellow:                     // MossdeepCity_Gym_EventScript_YellowFloorSwitch (rotating tiles, color 0)
    ActorsPauseAll
    SEPlay SEQ_SE_FLD_127
    VMSleep 8
    WorkCmpConst 0x4011, 0
    VMJumpIf CMP_EQ, L_EMG_Yellow0
    WorkCmpConst 0x4011, 1
    VMJumpIf CMP_EQ, L_EMG_Yellow1
    WorkCmpConst 0x4011, 2
    VMJumpIf CMP_EQ, L_EMG_Yellow2
    WorkCmpConst 0x4011, 3
    VMJumpIf CMP_EQ, L_EMG_Yellow3
    VMJump L_EMG_YellowEnd
L_EMG_Yellow0:
    ActorCmdExec 2, Mv_EMG_right_right            // (1,30) -> right, then faces right
    ActorCmdExec 3, Mv_EMG_left_left            // (5,20) -> left, then faces left
    ActorCmdExec 4, Mv_EMG_down_left            // (4,29) -> down, then faces left
    ActorCmdExec 10, Mv_EMG_up_right            // (2,30) -> up, then faces right
    ActorCmdExec 11, Mv_EMG_down_right            // (1,29) -> down, then faces right
    ActorCmdExec 12, Mv_EMG_right_right            // (4,30) -> right, then faces right
    ActorCmdExec 13, Mv_EMG_left_right            // (5,29) -> left, then faces right
    ActorCmdExec 14, Mv_EMG_up_right            // (5,21) -> up, then faces right
    ActorCmdWait
    WorkSetConst 0x4011, 1
    VMJump L_EMG_YellowEnd
L_EMG_Yellow1:
    ActorCmdExec 2, Mv_EMG_up_up            // (2,30) -> up, then faces up
    ActorCmdExec 3, Mv_EMG_down_down            // (4,20) -> down, then faces down
    ActorCmdExec 4, Mv_EMG_right_down            // (4,30) -> right, then faces down
    ActorCmdExec 10, Mv_EMG_left_up            // (2,29) -> left, then faces up
    ActorCmdExec 11, Mv_EMG_right_up            // (1,30) -> right, then faces up
    ActorCmdExec 12, Mv_EMG_up_up            // (5,30) -> up, then faces up
    ActorCmdExec 13, Mv_EMG_down_up            // (4,29) -> down, then faces up
    ActorCmdExec 14, Mv_EMG_left_up            // (5,20) -> left, then faces up
    ActorCmdWait
    WorkSetConst 0x4011, 2
    VMJump L_EMG_YellowEnd
L_EMG_Yellow2:
    ActorCmdExec 2, Mv_EMG_left_left            // (2,29) -> left, then faces left
    ActorCmdExec 3, Mv_EMG_right_right            // (4,21) -> right, then faces right
    ActorCmdExec 4, Mv_EMG_up_right            // (5,30) -> up, then faces right
    ActorCmdExec 10, Mv_EMG_down_left            // (1,29) -> down, then faces left
    ActorCmdExec 11, Mv_EMG_up_left            // (2,30) -> up, then faces left
    ActorCmdExec 12, Mv_EMG_left_left            // (5,29) -> left, then faces left
    ActorCmdExec 13, Mv_EMG_right_left            // (4,30) -> right, then faces left
    ActorCmdExec 14, Mv_EMG_down_left            // (4,20) -> down, then faces left
    ActorCmdWait
    WorkSetConst 0x4011, 3
    VMJump L_EMG_YellowEnd
L_EMG_Yellow3:
    ActorCmdExec 2, Mv_EMG_down_down            // (1,29) -> down, then faces down
    ActorCmdExec 3, Mv_EMG_up_up            // (5,21) -> up, then faces up
    ActorCmdExec 4, Mv_EMG_left_up            // (5,29) -> left, then faces up
    ActorCmdExec 10, Mv_EMG_right_down            // (1,30) -> right, then faces down
    ActorCmdExec 11, Mv_EMG_left_down            // (2,29) -> left, then faces down
    ActorCmdExec 12, Mv_EMG_down_down            // (4,29) -> down, then faces down
    ActorCmdExec 13, Mv_EMG_up_down            // (5,30) -> up, then faces down
    ActorCmdExec 14, Mv_EMG_right_down            // (4,21) -> right, then faces down
    ActorCmdWait
    WorkSetConst 0x4011, 0
    VMJump L_EMG_YellowEnd
L_EMG_YellowEnd:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EMG_SwitchBlue:                     // MossdeepCity_Gym_EventScript_BlueFloorSwitch (rotating tiles, color 1)
    ActorsPauseAll
    SEPlay SEQ_SE_FLD_127
    VMSleep 8
    WorkCmpConst 0x4012, 0
    VMJumpIf CMP_EQ, L_EMG_Blue0
    WorkCmpConst 0x4012, 1
    VMJumpIf CMP_EQ, L_EMG_Blue1
    WorkCmpConst 0x4012, 2
    VMJumpIf CMP_EQ, L_EMG_Blue2
    WorkCmpConst 0x4012, 3
    VMJumpIf CMP_EQ, L_EMG_Blue3
    VMJump L_EMG_BlueEnd
L_EMG_Blue0:
    ActorCmdExec 6, Mv_EMG_right_right            // (6,9) -> right, then faces right
    ActorCmdExec 15, Mv_EMG_up_right            // (7,9) -> up, then faces right
    ActorCmdExec 16, Mv_EMG_left_right            // (10,8) -> left, then faces right
    ActorCmdExec 17, Mv_EMG_down_left            // (9,8) -> down, then faces left
    ActorCmdWait
    WorkSetConst 0x4012, 1
    VMJump L_EMG_BlueEnd
L_EMG_Blue1:
    ActorCmdExec 6, Mv_EMG_up_up            // (7,9) -> up, then faces up
    ActorCmdExec 15, Mv_EMG_left_up            // (7,8) -> left, then faces up
    ActorCmdExec 16, Mv_EMG_down_up            // (9,8) -> down, then faces up
    ActorCmdExec 17, Mv_EMG_right_down            // (9,9) -> right, then faces down
    ActorCmdWait
    WorkSetConst 0x4012, 2
    VMJump L_EMG_BlueEnd
L_EMG_Blue2:
    ActorCmdExec 6, Mv_EMG_left_left            // (7,8) -> left, then faces left
    ActorCmdExec 15, Mv_EMG_down_left            // (6,8) -> down, then faces left
    ActorCmdExec 16, Mv_EMG_right_left            // (9,9) -> right, then faces left
    ActorCmdExec 17, Mv_EMG_up_right            // (10,9) -> up, then faces right
    ActorCmdWait
    WorkSetConst 0x4012, 3
    VMJump L_EMG_BlueEnd
L_EMG_Blue3:
    ActorCmdExec 6, Mv_EMG_down_down            // (6,8) -> down, then faces down
    ActorCmdExec 15, Mv_EMG_right_down            // (6,9) -> right, then faces down
    ActorCmdExec 16, Mv_EMG_up_down            // (10,9) -> up, then faces down
    ActorCmdExec 17, Mv_EMG_left_up            // (10,8) -> left, then faces up
    ActorCmdWait
    WorkSetConst 0x4012, 0
    VMJump L_EMG_BlueEnd
L_EMG_BlueEnd:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EMG_SwitchGreen:                     // MossdeepCity_Gym_EventScript_GreenFloorSwitch (rotating tiles, color 2)
    ActorsPauseAll
    SEPlay SEQ_SE_FLD_127
    VMSleep 8
    WorkCmpConst 0x4013, 0
    VMJumpIf CMP_EQ, L_EMG_Green0
    WorkCmpConst 0x4013, 1
    VMJumpIf CMP_EQ, L_EMG_Green1
    WorkCmpConst 0x4013, 2
    VMJumpIf CMP_EQ, L_EMG_Green2
    WorkCmpConst 0x4013, 3
    VMJumpIf CMP_EQ, L_EMG_Green3
    VMJump L_EMG_GreenEnd
L_EMG_Green0:
    ActorCmdExec 22, Mv_EMG_right_right            // (11,34) -> right, then faces right
    ActorCmdExec 23, Mv_EMG_left_right            // (12,33) -> left, then faces right
    ActorCmdExec 24, Mv_EMG_up_right            // (12,34) -> up, then faces right
    ActorCmdWait
    WorkSetConst 0x4013, 1
    VMJump L_EMG_GreenEnd
L_EMG_Green1:
    ActorCmdExec 22, Mv_EMG_up_up            // (12,34) -> up, then faces up
    ActorCmdExec 23, Mv_EMG_down_up            // (11,33) -> down, then faces up
    ActorCmdExec 24, Mv_EMG_left_up            // (12,33) -> left, then faces up
    ActorCmdWait
    WorkSetConst 0x4013, 2
    VMJump L_EMG_GreenEnd
L_EMG_Green2:
    ActorCmdExec 22, Mv_EMG_left_left            // (12,33) -> left, then faces left
    ActorCmdExec 23, Mv_EMG_right_left            // (11,34) -> right, then faces left
    ActorCmdExec 24, Mv_EMG_down_left            // (11,33) -> down, then faces left
    ActorCmdWait
    WorkSetConst 0x4013, 3
    VMJump L_EMG_GreenEnd
L_EMG_Green3:
    ActorCmdExec 22, Mv_EMG_down_down            // (11,33) -> down, then faces down
    ActorCmdExec 23, Mv_EMG_up_down            // (12,34) -> up, then faces down
    ActorCmdExec 24, Mv_EMG_right_down            // (11,34) -> right, then faces down
    ActorCmdWait
    WorkSetConst 0x4013, 0
    VMJump L_EMG_GreenEnd
L_EMG_GreenEnd:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EMG_SwitchPurple:                     // MossdeepCity_Gym_EventScript_PurpleFloorSwitch (rotating tiles, color 3)
    ActorsPauseAll
    SEPlay SEQ_SE_FLD_127
    VMSleep 8
    WorkCmpConst 0x4014, 0
    VMJumpIf CMP_EQ, L_EMG_Purple0
    WorkCmpConst 0x4014, 1
    VMJumpIf CMP_EQ, L_EMG_Purple1
    WorkCmpConst 0x4014, 2
    VMJumpIf CMP_EQ, L_EMG_Purple2
    WorkCmpConst 0x4014, 3
    VMJumpIf CMP_EQ, L_EMG_Purple3
    VMJump L_EMG_PurpleEnd
L_EMG_Purple0:
    ActorCmdExec 25, Mv_EMG_down_left            // (22,25) -> down, then faces left
    ActorCmdExec 26, Mv_EMG_up_right            // (23,26) -> up, then faces right
    ActorCmdExec 28, Mv_EMG_up_right            // (22,23) -> up, then faces right
    ActorCmdExec 29, Mv_EMG_right_right            // (21,23) -> right, then faces right
    ActorCmdExec 30, Mv_EMG_down_right            // (21,22) -> down, then faces right
    ActorCmdExec 31, Mv_EMG_left_right            // (22,22) -> left, then faces right
    ActorCmdExec 32, Mv_EMG_left_left            // (25,22) -> left, then faces left
    ActorCmdExec 33, Mv_EMG_down_right            // (24,22) -> down, then faces right
    ActorCmdExec 34, Mv_EMG_right_right            // (24,23) -> right, then faces right
    ActorCmdExec 36, Mv_EMG_left_right            // (23,25) -> left, then faces right
    ActorCmdWait
    WorkSetConst 0x4014, 1
    VMJump L_EMG_PurpleEnd
L_EMG_Purple1:
    ActorCmdExec 25, Mv_EMG_right_down            // (22,26) -> right, then faces down
    ActorCmdExec 26, Mv_EMG_left_up            // (23,25) -> left, then faces up
    ActorCmdExec 28, Mv_EMG_left_up            // (22,22) -> left, then faces up
    ActorCmdExec 29, Mv_EMG_up_up            // (22,23) -> up, then faces up
    ActorCmdExec 30, Mv_EMG_right_up            // (21,23) -> right, then faces up
    ActorCmdExec 31, Mv_EMG_down_up            // (21,22) -> down, then faces up
    ActorCmdExec 32, Mv_EMG_down_down            // (24,22) -> down, then faces down
    ActorCmdExec 33, Mv_EMG_right_up            // (24,23) -> right, then faces up
    ActorCmdExec 34, Mv_EMG_up_up            // (25,23) -> up, then faces up
    ActorCmdExec 36, Mv_EMG_down_up            // (22,25) -> down, then faces up
    ActorCmdWait
    WorkSetConst 0x4014, 2
    VMJump L_EMG_PurpleEnd
L_EMG_Purple2:
    ActorCmdExec 25, Mv_EMG_up_right            // (23,26) -> up, then faces right
    ActorCmdExec 26, Mv_EMG_down_left            // (22,25) -> down, then faces left
    ActorCmdExec 28, Mv_EMG_down_left            // (21,22) -> down, then faces left
    ActorCmdExec 29, Mv_EMG_left_left            // (22,22) -> left, then faces left
    ActorCmdExec 30, Mv_EMG_up_left            // (22,23) -> up, then faces left
    ActorCmdExec 31, Mv_EMG_right_left            // (21,23) -> right, then faces left
    ActorCmdExec 32, Mv_EMG_right_right            // (24,23) -> right, then faces right
    ActorCmdExec 33, Mv_EMG_up_left            // (25,23) -> up, then faces left
    ActorCmdExec 34, Mv_EMG_left_left            // (25,22) -> left, then faces left
    ActorCmdExec 36, Mv_EMG_right_left            // (22,26) -> right, then faces left
    ActorCmdWait
    WorkSetConst 0x4014, 3
    VMJump L_EMG_PurpleEnd
L_EMG_Purple3:
    ActorCmdExec 25, Mv_EMG_left_up            // (23,25) -> left, then faces up
    ActorCmdExec 26, Mv_EMG_right_down            // (22,26) -> right, then faces down
    ActorCmdExec 28, Mv_EMG_right_down            // (21,23) -> right, then faces down
    ActorCmdExec 29, Mv_EMG_down_down            // (21,22) -> down, then faces down
    ActorCmdExec 30, Mv_EMG_left_down            // (22,22) -> left, then faces down
    ActorCmdExec 31, Mv_EMG_up_down            // (22,23) -> up, then faces down
    ActorCmdExec 32, Mv_EMG_up_up            // (25,23) -> up, then faces up
    ActorCmdExec 33, Mv_EMG_left_down            // (25,22) -> left, then faces down
    ActorCmdExec 34, Mv_EMG_down_down            // (24,22) -> down, then faces down
    ActorCmdExec 36, Mv_EMG_up_down            // (23,26) -> up, then faces down
    ActorCmdWait
    WorkSetConst 0x4014, 0
    VMJump L_EMG_PurpleEnd
L_EMG_PurpleEnd:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EMG_SwitchRed:                     // MossdeepCity_Gym_EventScript_RedFloorSwitch (rotating tiles, color 4)
    ActorsPauseAll
    SEPlay SEQ_SE_FLD_127
    VMSleep 8
    WorkCmpConst 0x4015, 0
    VMJumpIf CMP_EQ, L_EMG_Red0
    WorkCmpConst 0x4015, 1
    VMJumpIf CMP_EQ, L_EMG_Red1
    WorkCmpConst 0x4015, 2
    VMJumpIf CMP_EQ, L_EMG_Red2
    WorkCmpConst 0x4015, 3
    VMJumpIf CMP_EQ, L_EMG_Red3
    VMJump L_EMG_RedEnd
L_EMG_Red0:
    ActorCmdExec 18, Mv_EMG_left_up            // (7,5) -> left, then faces up
    ActorCmdExec 19, Mv_EMG_right_right            // (6,6) -> right, then faces right
    ActorCmdExec 20, Mv_EMG_left_right            // (12,5) -> left, then faces right
    ActorCmdExec 21, Mv_EMG_down_right            // (11,5) -> down, then faces right
    ActorCmdExec 35, Mv_EMG_down_right            // (6,5) -> down, then faces right
    ActorCmdWait
    WorkSetConst 0x4015, 1
    VMJump L_EMG_RedEnd
L_EMG_Red1:
    ActorCmdExec 18, Mv_EMG_down_left            // (6,5) -> down, then faces left
    ActorCmdExec 19, Mv_EMG_up_up            // (7,6) -> up, then faces up
    ActorCmdExec 20, Mv_EMG_down_up            // (11,5) -> down, then faces up
    ActorCmdExec 21, Mv_EMG_right_up            // (11,6) -> right, then faces up
    ActorCmdExec 35, Mv_EMG_right_up            // (6,6) -> right, then faces up
    ActorCmdWait
    WorkSetConst 0x4015, 2
    VMJump L_EMG_RedEnd
L_EMG_Red2:
    ActorCmdExec 18, Mv_EMG_right_down            // (6,6) -> right, then faces down
    ActorCmdExec 19, Mv_EMG_left_left            // (7,5) -> left, then faces left
    ActorCmdExec 20, Mv_EMG_right_left            // (11,6) -> right, then faces left
    ActorCmdExec 21, Mv_EMG_up_left            // (12,6) -> up, then faces left
    ActorCmdExec 35, Mv_EMG_up_left            // (7,6) -> up, then faces left
    ActorCmdWait
    WorkSetConst 0x4015, 3
    VMJump L_EMG_RedEnd
L_EMG_Red3:
    ActorCmdExec 18, Mv_EMG_up_right            // (7,6) -> up, then faces right
    ActorCmdExec 19, Mv_EMG_down_down            // (6,5) -> down, then faces down
    ActorCmdExec 20, Mv_EMG_up_down            // (12,6) -> up, then faces down
    ActorCmdExec 21, Mv_EMG_left_down            // (12,5) -> left, then faces down
    ActorCmdExec 35, Mv_EMG_left_down            // (7,5) -> left, then faces down
    ActorCmdWait
    WorkSetConst 0x4015, 0
    VMJump L_EMG_RedEnd
L_EMG_RedEnd:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EMG_Pad2:                          // warp pad (3,28) -> (1,23) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 2, 0, 25, 1
    h_fadescreen_from_black
    h_release

EMG_Pad3:                          // warp pad (1,23) -> (3,28) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 4, 0, 30, 1
    h_fadescreen_from_black
    h_release

EMG_Pad4:                          // warp pad (7,18) -> (8,12) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 9, 0, 14, 1
    h_fadescreen_from_black
    h_release

EMG_Pad5:                          // warp pad (8,12) -> (7,18) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 8, 0, 20, 1
    h_fadescreen_from_black
    h_release

EMG_Pad6:                          // warp pad (9,18) -> (23,20) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 24, 0, 22, 1
    h_fadescreen_from_black
    h_release

EMG_Pad7:                          // warp pad (23,20) -> (9,18) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 10, 0, 20, 1
    h_fadescreen_from_black
    h_release

EMG_Pad8:                          // warp pad (1,33) -> (20,24) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 21, 0, 26, 1
    h_fadescreen_from_black
    h_release

EMG_Pad9:                          // warp pad (20,24) -> (1,33) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 2, 0, 35, 1
    h_fadescreen_from_black
    h_release

EMG_Pad10:                          // warp pad (11,3) -> (11,35) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 12, 0, 37, 1
    h_fadescreen_from_black
    h_release

EMG_Pad11:                          // warp pad (11,35) -> (11,3) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 12, 0, 5, 1
    h_fadescreen_from_black
    h_release

EMG_Pad12:                          // warp pad (13,32) -> (21,10) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 22, 0, 12, 1
    h_fadescreen_from_black
    h_release

EMG_Pad13:                          // warp pad (21,10) -> (13,32) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, 14, 0, 34, 1
    h_fadescreen_from_black
    h_release
    .balign 4, 0
Mv_EMG_down_down:
    lock_facing_direction
    walk_down
    unlock_facing_direction
    face_down
    step_end
    .balign 4, 0
Mv_EMG_down_left:
    lock_facing_direction
    walk_down
    unlock_facing_direction
    face_left
    step_end
    .balign 4, 0
Mv_EMG_down_right:
    lock_facing_direction
    walk_down
    unlock_facing_direction
    face_right
    step_end
    .balign 4, 0
Mv_EMG_down_up:
    lock_facing_direction
    walk_down
    unlock_facing_direction
    face_up
    step_end
    .balign 4, 0
Mv_EMG_left_down:
    lock_facing_direction
    walk_left
    unlock_facing_direction
    face_down
    step_end
    .balign 4, 0
Mv_EMG_left_left:
    lock_facing_direction
    walk_left
    unlock_facing_direction
    face_left
    step_end
    .balign 4, 0
Mv_EMG_left_right:
    lock_facing_direction
    walk_left
    unlock_facing_direction
    face_right
    step_end
    .balign 4, 0
Mv_EMG_left_up:
    lock_facing_direction
    walk_left
    unlock_facing_direction
    face_up
    step_end
    .balign 4, 0
Mv_EMG_right_down:
    lock_facing_direction
    walk_right
    unlock_facing_direction
    face_down
    step_end
    .balign 4, 0
Mv_EMG_right_left:
    lock_facing_direction
    walk_right
    unlock_facing_direction
    face_left
    step_end
    .balign 4, 0
Mv_EMG_right_right:
    lock_facing_direction
    walk_right
    unlock_facing_direction
    face_right
    step_end
    .balign 4, 0
Mv_EMG_right_up:
    lock_facing_direction
    walk_right
    unlock_facing_direction
    face_up
    step_end
    .balign 4, 0
Mv_EMG_up_down:
    lock_facing_direction
    walk_up
    unlock_facing_direction
    face_down
    step_end
    .balign 4, 0
Mv_EMG_up_left:
    lock_facing_direction
    walk_up
    unlock_facing_direction
    face_left
    step_end
    .balign 4, 0
Mv_EMG_up_right:
    lock_facing_direction
    walk_up
    unlock_facing_direction
    face_right
    step_end
    .balign 4, 0
Mv_EMG_up_up:
    lock_facing_direction
    walk_up
    unlock_facing_direction
    face_up
    step_end
    .balign 4, 0
#endif
// <<< emerald_rooms mossdeep_puzzle
