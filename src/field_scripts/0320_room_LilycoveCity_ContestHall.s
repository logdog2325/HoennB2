// LilycoveCity_ContestHall (zone 160): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0218_room_LilycoveCity_ContestHall.txt
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
    ScriptEntry Script_22
    ScriptEntry Script_23
    ScriptEntry Script_24
    ScriptEntry Script_25
    ScriptEntry Script_26
    ScriptEntry Script_27
    ScriptEntry Script_28
    ScriptEntry Script_29
    ScriptEntry Script_30
    ScriptEntry Script_31
    ScriptEntry Script_32
    ScriptEntry Script_33
    ScriptEntry Script_34
    ScriptEntry Script_35
    ScriptEntry Script_36
    ScriptEntry CH_Woman29              // 37: object 29 (the mother of a contestant)  // story:
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
    ActorCmdExec 4, Movement_FaceDown
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
    ActorCmdExec 5, Movement_FaceDown
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
    ActorCmdExec 6, Movement_FaceUp
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
    ActorCmdExec 7, Movement_FaceUp
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
    ActorCmdExec 8, Movement_FaceUp
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
    ActorCmdExec 9, Movement_FaceUp
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
    ActorCmdExec 11, Movement_FaceLeft
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
    ActorCmdExec 12, Movement_FaceRight
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
    ActorCmdExec 13, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_13:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 12, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 14, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_14:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 13, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 15, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_15:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 14, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 16, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_16:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 15, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 17, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_17:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 16, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 18, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_18:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 17, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 19, Movement_FaceRight
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_19:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 18, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 20, Movement_FaceLeft
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_20:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 19, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 21, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_21:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 20, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 22, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_22:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 21, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 23, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_23:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 22, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 24, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_24:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 23, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 25, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_25:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 24, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 26, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_26:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 25, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 27, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_27:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 26, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 28, Movement_FaceUp
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_28:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 27, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 30, Movement_FaceDown
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_29:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 28, 0, 0
    LastKeyWait
    ActorMsgClose
    ActorCmdExec 31, Movement_FaceLeft
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_30:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 29, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_31:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 30, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_32:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 31, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_33:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 32, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_34:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 33, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_35:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 34, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_36:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 35, 2
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

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/LilycoveCity_ContestHall/scripts.inc: the spectators are the specials agent's (above); this is the
// one that looks at you and turns back after a pause. No Contest runs here (decided later). Line 36 of the text file.
#define T_Mother 36
CH_Woman29:                                 // LilycoveCity_ContestHall_EventScript_1592C0 (lockall, FacePlayer, delay 25)
    c3_talk
    h_delay 25
    h_turnobject 29, 3                       // FaceOriginalDirection: object 29 faces right
    h_msgbox_info T_Mother
    h_release
    .balign 4, 0
