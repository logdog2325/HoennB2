// Chapter Ch8's beat (part 8a) in the rival's room, 2F (Sapphire data/scripts/players_house.inc
// RivalsHouse_2F_EventScript_RivalPostLilycove .. MayWhereShouldIGoNext): once the rival fought the player in Lilycove
// (FLAG_MET_RIVAL_LILYCOVE) they are at home checking the Pokédex. Included at the start of Script_21 of
// scenes/players_house_2f.inc (after ActorsPauseAll, where Sapphire has `goto_if_set FLAG_MET_RIVAL_LILYCOVE`), in both
// houses (Brendan's room 391, May's room 393: the same lines of each house's own text file). Plain Black 2 commands
// (the house files do not include hoenn_story.inc). T(4) = "Just checking my Pokédex", T(5) = "Where should I go next".
// Falls through to the first meeting when the Lilycove battle has not happened.
    VMStackPushFlag FLAG_MET_RIVAL_LILYCOVE
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Ch8_NotAtLilycove          // goto_if_set: jumps when the comparison is false
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye                                 // Common_Movement_FacePlayer
    VMStackPushFlag FLAG_MET_RIVAL_IN_HOUSE_AFTER_LILYCOVE
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Ch8_FirstTalk
    ActorMsg MSGFILE_SCRIPT, T(5), 1, 0, 0           // ...WhereShouldIGoNext
    VMJump L_Ch8_Said
L_Ch8_FirstTalk:
    ActorMsg MSGFILE_SCRIPT, T(4), 1, 0, 0           // ...JustCheckingMyPokedex
L_Ch8_Said:
    LastKeyWait
    MsgWinCloseAll
    FlagSet FLAG_MET_RIVAL_IN_HOUSE_AFTER_LILYCOVE
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_Ch8_NotAtLilycove:
