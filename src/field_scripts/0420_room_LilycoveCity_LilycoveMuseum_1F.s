// LilycoveCity_LilycoveMuseum_1F (zone 210): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0269_room_LilycoveCity_LilycoveMuseum_1F.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch8a
#include "hoenn_trainers.h"  // ch8a
#include "hoenn_story.inc"  // ch8a
#include "scenes/ch8a_lib.inc"  // ch8a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntry Script_10
    ScriptEntry Script_11
    ScriptEntry Script_12
    ScriptEntry Script_13
    ScriptEntry Script_14
    ScriptEntry Script_15
    ScriptEntry Script_16
    ScriptEntry Script_17
    ScriptEntry Script_18
    ScriptEntry Script_19
    ScriptEntry Script_20
    ScriptEntry Script_21
    ScriptEntry MU1_Curator             // 22: object 2 (the Curator)  // story:
    ScriptEntry MU1_Woman2              // 23: object 7 (hidden: PATRON_1)  // story:
    ScriptEntry MU1_Artist2             // 24: object 8 (hidden: PATRON_4)  // story:
    ScriptEntry MU1_FatMan              // 25: object 9 (hidden: TOURISTS)  // story:
    ScriptEntry MU1_PsychicM            // 26: object 10 (hidden: PATRON_3)  // story:
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 1, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 2, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 3, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 4, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 5, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 6, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 7, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 8, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_10:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 9, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 10, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_12:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 11, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_13:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 12, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_14:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 13, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_15:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 14, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_16:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 15, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_17:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 16, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_18:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 17, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_19:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 18, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_20:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 19, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_21:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 20, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/LilycoveCity_LilycoveMuseum_1F/scripts.inc. The Curator takes the player up to the exhibit hall
// (2F) once they say they like paintings (removeobject 2 hides him on 1F: FLAG_HIDE_LILYCOVE_MUSEUM_CURATOR); the four
// visitors appear as contest paintings are added to 2F (Contests are decided later: they stay hidden). The greeter,
// the paintings and the other visitors are the generator's. People: data/story/ch8a.json. Lines 21-31 of the text file.
#define T_ImCurator 21
#define T_SawIt 22
#define T_NotYet 23
#define T_NotDisturb 24
#define T_InterestInPaintings 25
#define T_HonoredYouVisit 26
#define T_ComeWithMe 27
#define T_NewPaintings 28
#define T_CuratorCheerful 29
#define T_AimToSee 30
#define T_TouristDestination 31
MU1_Curator:                                // ..._EventScript_Curator (lockall)
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye                        // Common_Movement_FacePlayer
    ParentActorMsg MSGFILE_SCRIPT, T_ImCurator, 0, 0
    ListMenu_AnchorTopRight 31, 9, 0, 1, C8_SEL      // multichoice 20, 8, 16, 1: Saw it / Not yet
    ListMenuAdd T_SawIt, 65535, 1
    ListMenuAdd T_NotYet, 65535, 2
    ListMenuShow
    MsgWinCloseAll
    WorkCmpConst C8_SEL, 1
    VMJumpIf CMP_EQ, L_MU1_SawPaintings
    h_msgbox T_NotDisturb                   // ..._EventScript_NotYet (MSGBOX_NPC)
    h_release
L_MU1_SawPaintings:
    h_yesno T_InterestInPaintings, C8_A
    h_goto_if_no C8_A, L_MU1_NotInterested
    h_msgbox T_ComeWithMe                   // ..._EventScript_InterestedInPaintings
    h_closemessage
    h_applymovement 2, Mv_MU1_CuratorEnterStairs
    h_waitmovement
    h_removeobject 2, FLAG_HIDE_LILYCOVE_MUSEUM_CURATOR
    h_getplayerfacing C8_B                  // switch VAR_FACING: the way the player faced the Curator
    h_goto_if_eq C8_B, 2, L_MU1_FollowWest
    h_goto_if_eq C8_B, 3, L_MU1_FollowEast
    h_applymovement 255, Mv_MU1_FollowNorth
    VMJump L_MU1_Follow
L_MU1_FollowWest:
    h_applymovement 255, Mv_MU1_FollowWest
    VMJump L_MU1_Follow
L_MU1_FollowEast:
    h_applymovement 255, Mv_MU1_FollowEast
L_MU1_Follow:
    h_waitmovement
    h_warpsilent 211, 12, 9, 0               // warp MAP_LILYCOVE_CITY_LILYCOVE_MUSEUM_2F, 255, 11, 8 (its OnFrame scene follows)
    VMHalt
L_MU1_NotInterested:                        // ..._EventScript_NotInterested
    h_msgbox T_HonoredYouVisit
    h_release

MU1_Woman2:
    h_msgbox_npc T_NewPaintings
MU1_PsychicM:
    h_msgbox_npc T_CuratorCheerful
MU1_FatMan:
    h_msgbox_npc T_TouristDestination
MU1_Artist2:                                // MSGBOX_NPC, then lockall + Common_Movement_FaceOriginalDirection
    c3_say_turn_back T_AimToSee, 8, 0

    .balign 4, 0
Mv_MU1_CuratorEnterStairs:
    walk_up
    step_end
Mv_MU1_FollowNorth:
    walk_up
    walk_up
    step_end
Mv_MU1_FollowWest:
    walk_left
    walk_up
    step_end
Mv_MU1_FollowEast:
    walk_right
    walk_up
    step_end
    .balign 4, 0
