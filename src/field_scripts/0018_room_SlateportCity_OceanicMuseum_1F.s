// SlateportCity_OceanicMuseum_1F (zone 9): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0015_room_SlateportCity_OceanicMuseum_1F.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch3a
#include "hoenn_trainers.h"  // ch3a
#include "hoenn_story.inc"  // ch3a
#include "scenes/ch3_lib.inc"  // ch3a

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
    ScriptEntry Story_M1_PayFeeLeft     // 16: step trigger (9,7) VAR_SLATEPORT_MUSEUM_1F_STATE 0  // story:
    ScriptEntry Story_M1_PayFeeRight    // 17: step trigger (10,7)  // story:
    ScriptEntry Story_M1_Grunt1         // 18: object 5  // story:
    ScriptEntry Story_M1_Grunt2         // 19: object 4  // story:
    ScriptEntry Story_M1_Grunt3         // 20: object 2  // story:
    ScriptEntry Story_M1_Grunt4         // 21: object 3  // story:
    ScriptEntry Story_M1_Grunt5         // 22: object 6  // story:
    ScriptEntry Story_M1_Grunt6         // 23: object 8  // story:
    ScriptEntry Story_M1_Patron1        // 24: object 9  // story:
    ScriptEntry Story_M1_Patron2        // 25: object 10  // story:
    ScriptEntry Story_M1_Patron3        // 26: object 11  // story:
    ScriptEntry Story_M1_Patron4        // 27: object 12  // story:
    ScriptEntry Story_M1_FamiliarGrunt  // 28: object 13  // story:
    ScriptEntry Story_M1_Reporter       // 29: object 14  // story:
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
    SystemMsg 2, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 3, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 4, 2
    LastKeyWait
    MsgWinCloseAll
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
    .balign 4, 0

// ---- story (chapter Ch3 part 3a, ch3a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/SlateportCity_OceanicMuseum_1F/scripts.inc + event_scripts.s's SlateportCity_OceanicMuseum_1F_*
// (the TV reporter). People and triggers: data/story/ch3a.json (uid = Sapphire local id). Map scripts: none needed
// (Sapphire's only sets the Aqua sprites, placed directly here). Lines 15-36 of the text file.
#define T_PleaseEnjoyYourself 0
#define T_WouldYouLikeToEnter 15
#define T_NotEnoughMoney 16
#define T_CatchUp 17
#define T_Grunt1 18
#define T_Grunt2 19
#define T_Grunt3 20
#define T_Grunt4 21
#define T_Grunt5 22
#define T_Grunt6 23
#define T_Patron1 24
#define T_Patron2 25
#define T_Patron3 26
#define T_Patron4 27
#define T_RememberMe 28
#define T_ScrewedUp 29
#define T_HaveToTake 30
#define T_RepFirst 31
#define T_RepAgain 32
#define T_RepYes 33
#define T_RepNo 34
#define T_RepStory 35
#define T_RepGotStory 36
#define M1_ATTENDANT_LEFT 1                 // the two "Please enjoy yourself." attendants (Sapphire objects 1, 7)
#define M1_ATTENDANT_RIGHT 7
#define M1_FAMILIAR_GRUNT 13

Story_M1_PayFeeLeft:                        // ..._EventScript_PayEntranceFeeLeft (lockall: no one is talked to)
    ActorsPauseAll
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    WorkSetConst C3_SEL, M1_ATTENDANT_LEFT  // the attendant on that side says the lines
    VMJump L_M1_PayFee
Story_M1_PayFeeRight:                       // ..._EventScript_PayEntranceFeeRight
    ActorsPauseAll
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    WorkSetConst C3_SEL, M1_ATTENDANT_RIGHT
L_M1_PayFee:                                // ..._EventScript_PayEntranceFee
    MoneyWinDisp 31, 1                      // showmoneybox (Black 2's money window, as 0010.s)
    h_yesno_actor T_WouldYouLikeToEnter, C3_SEL, C3_TMP
    h_goto_if_yes C3_TMP, L_M1_CheckMoney
    MsgWinCloseAll
    MoneyWinClose
L_M1_PushBack:
    h_applymovement 255, Mv_M1_PushPlayerBack
    h_waitmovement
    h_release
L_M1_CheckMoney:                            // ..._EventScript_CheckMoneyForFee
    MoneyCheck C3_TMP, 50
    h_goto_if_eq C3_TMP, 0, L_M1_NotEnoughMoney
    MoneySub 50
    MoneyWinUpdate
    h_msgbox_actor T_PleaseEnjoyYourself, C3_SEL
    h_setvar VAR_SLATEPORT_MUSEUM_1F_STATE, 1
    MoneyWinClose
    h_release
L_M1_NotEnoughMoney:
    h_goto_if_unset FLAG_DELIVERED_DEVON_GOODS, L_M1_AllowAnyway
    h_msgbox_actor T_NotEnoughMoney, C3_SEL
    MsgWinCloseAll
    MoneyWinClose
    VMJump L_M1_PushBack
L_M1_AllowAnyway:                           // ..._EventScript_AllowEntranceAnyway ("you're with that group?")
    h_msgbox_actor T_CatchUp, C3_SEL
    h_setvar VAR_SLATEPORT_MUSEUM_1F_STATE, 1
    MoneyWinClose
    h_release

Story_M1_Grunt1:                            // the Aqua grunts in the Museum (FLAG_HIDE_EVIL_TEAM_OCEANIC_MUSEUM)
    h_msgbox_npc T_Grunt1
Story_M1_Grunt2:
    h_msgbox_npc T_Grunt2
Story_M1_Grunt3:
    h_msgbox_npc T_Grunt3
Story_M1_Grunt4:                            // MSGBOX_SIGN: he keeps looking at the exhibit
    h_msgbox_sign T_Grunt4
Story_M1_Grunt5:
    h_msgbox_npc T_Grunt5
Story_M1_Grunt6:
    h_msgbox_npc T_Grunt6

Story_M1_Patron1:                           // visitors (FLAG_HIDE_OCEANIC_MUSEUM_VISITORS: after Mauville)
    h_msgbox_npc T_Patron1
Story_M1_Patron2:
    h_msgbox_npc T_Patron2
Story_M1_Patron3:
    h_msgbox_npc T_Patron3
Story_M1_Patron4:
    h_msgbox_npc T_Patron4

Story_M1_FamiliarGrunt:                     // ..._EventScript_FamiliarGrunt: the Rusturf Tunnel grunt, TM46 Thief
    c3_talk
    h_delay 8
    h_applymovement M1_FAMILIAR_GRUNT, Common_Movement_ExclamationMark   // playse SE_PIN: the "!" plays its own
    h_waitmovement
    h_applymovement M1_FAMILIAR_GRUNT, Common_Movement_Delay48
    h_waitmovement
    h_msgbox T_RememberMe
    h_closemessage
    h_giveitem ITEM_TM46, 1                 // ITEM_TM46_THIEF (Gen 5's TM46 is Thief too)
    h_goto_if_eq HLIB_RESULT, 0, L_M1_NoRoomForThief
    h_setflag FLAG_RECEIVED_TM46
    h_msgbox T_ScrewedUp
    h_closemessage
    h_getplayerfacing C3_TMP                // VAR_FACING 2 (north) = Black 2 0
    h_goto_if_eq C3_TMP, 0, L_M1_GruntExitNorth
    h_applymovement M1_FAMILIAR_GRUNT, Mv_M1_FamiliarGruntExit
    VMJump L_M1_GruntExit
L_M1_GruntExitNorth:
    h_applymovement M1_FAMILIAR_GRUNT, Mv_M1_FamiliarGruntExitNorth
L_M1_GruntExit:
    h_waitmovement
    h_playse SE_EXIT
    h_removeobject M1_FAMILIAR_GRUNT, FLAG_HIDE_SCARED_GRUNT_OCEANIC_MUSEUM
    h_release
L_M1_NoRoomForThief:
    h_msgbox T_HaveToTake
    h_release

// The TV reporter (event_scripts.s SlateportCity_OceanicMuseum_1F_EventScript_1ADEE0, the "Recent Happenings" show).
// Black 2 has no TV shows: Sapphire's Easy Chat screen is Black 2's word picker (CallPhraseSelect 4, the one its quiz
// uses: nothing is stored), and the recorded show stays pending for good (FLAG_TV_SHOW_RECENT_HAPPENINGS_PENDING =
// special InterviewBefore's answer).
Story_M1_Reporter:
    c3_talk
    h_goto_if_set FLAG_TV_SHOW_RECENT_HAPPENINGS_PENDING, L_M1_RepGotStory
    h_goto_if_set FLAG_OCEANIC_MUSEUM_MET_REPORTER, L_M1_RepAgain
    h_setflag FLAG_OCEANIC_MUSEUM_MET_REPORTER
    h_yesno T_RepFirst, C3_TMP
    VMJump L_M1_RepAnswer
L_M1_RepAgain:
    h_yesno T_RepAgain, C3_TMP
L_M1_RepAnswer:
    h_goto_if_no C3_TMP, L_M1_RepNo
    h_msgbox T_RepYes
    c3_easy_chat C3_SEL                     // Common_EventScript_ShowEasyChatScreen
    h_goto_if_ne C3_SEL, 1, L_M1_RepNo
    h_msgbox T_RepStory
    h_setflag FLAG_TV_SHOW_RECENT_HAPPENINGS_PENDING     // special InterviewAfter
    h_release
L_M1_RepNo:
    h_msgbox T_RepNo
    h_release
L_M1_RepGotStory:
    h_msgbox T_RepGotStory
    h_release

    .balign 4, 0
Mv_M1_PushPlayerBack:                       // ..._Movement_PushPlayerBackFromCounter
    walk_down
    step_end
Mv_M1_FamiliarGruntExit:
    face_down
    walk_fast_down 4
    delay_8
    step_end
Mv_M1_FamiliarGruntExitNorth:
    walk_fast_right
    walk_fast_down 4
    delay_8
    step_end
#include "common/movement.inc"
    .balign 4, 0
