// SlateportCity_ContestHall (zone 594): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0350_room_SlateportCity_ContestHall.txt
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
    ScriptEntry Story_CH_Sailor         // 15: object 13 (TM41 Torment)  // story:
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
    ActorCmdExec 3, Movement_FaceDown
    ActorCmdWait
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
    ActorCmdExec 4, Movement_FaceDown
    ActorCmdWait
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
    ActorCmdExec 5, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 5, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 6, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 6, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 7, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 7, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 8, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 8, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 9, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_10:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 9, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 10, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 10, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 11, Movement_FaceRight
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_12:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 11, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 12, Movement_FaceLeft
    ActorCmdWait
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
    .balign 4, 0
Movement_FaceUp:
    Move 0, 1
    MoveEnd
Movement_FaceDown:
    Move 1, 1
    MoveEnd
Movement_FaceLeft:
    Move 2, 1
    MoveEnd
Movement_FaceRight:
    Move 3, 1
    MoveEnd
    .balign 4, 0

// ---- story (chapter Ch3 part 3a, ch3a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/SlateportCity_ContestHall/scripts.inc: the sailor with TM41 (SlateportCity_ContestHall_EventScript_15555E).
// The hall's other people are the generated ones above. data/story/ch3a.json. Lines 14-16 of the text file.
#define T_TormentGive 14
#define T_TormentAfter 15
#define T_BagFull 16

Story_CH_Sailor:
    c3_talk
    h_goto_if_set FLAG_RECEIVED_TM41, L_CH_ReceivedTM41
    h_msgbox T_TormentGive
    h_closemessage
    h_giveitem ITEM_TM41, 1                 // ITEM_TM41_TORMENT (Gen 5's TM41 is Torment too)
    h_goto_if_eq HLIB_RESULT, 0, L_CH_BagFull
    h_setflag FLAG_RECEIVED_TM41
    h_msgbox T_TormentAfter
    h_release
L_CH_ReceivedTM41:
    h_msgbox T_TormentAfter
    h_release
L_CH_BagFull:                               // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release
    .balign 4, 0
