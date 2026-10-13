// Pokémon Center nurse (centers agent): Sapphire's flow (pokeruby data/scripts/pkmn_center_nurse.inc,
// Common_EventScript_PkmnCenterNurse) and words, with Black 2's own heal sequence (global script 2100 =
// external/pokebw2/data/field_scripts/1231.s Script_1): the player hands the Balls over, the nurse turns to the healing
// machine (pcmachine01, found by PokecenPlayHealingSequence within 5 tiles of the player), PokePartyRecoverAll, the
// Balls come back, the nurse bows. Black 2's extras (birthday, Trainer Card "the usual") are left out.
// The including file's text starts with the five nurse lines (b2tools/centers_rooms.py NURSE_TEXT):
//   0 welcome + "Would you like to rest your Pokémon?", 1 "Okay, I'll take...", 2 "Thank you for waiting...",
//   3 "We hope to see you again!", 4 Pokérus.
// Flags: 101 = Black 2's own "Pokérus explained" (1231.s), as Sapphire's FLAG_POKERUS_EXPLAINED.
// Sapphire's nurse faces left to the machine on her left; 0x8011 = the actor talked to.
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0       // welcome, rest your Pokémon?
    YesNoWin 0x8000
    WorkCmpConst 0x8000, 0                       // 0 = yes
    VMJumpIf CMP_EQ, L_NurseHeal
    ParentActorMsg MSGFILE_SCRIPT, 3, 0, 0       // no: "We hope to see you again!"
    LastKeyWait
    ActorMsgClose
    VMJump L_NurseEnd

L_NurseHeal:
    ActorMsgClose
    PlayerSetSpecialSequence 64                  // the player hands the Balls over (Black 2)
    ActorCmdExec 255, Movement_NursePlayerGive
    ActorCmdWait
    PlayerSetSpecialSequence 8
    ActorCmdExec 255, Movement_NursePlayerFaceUp
    ActorCmdWait
    ParentActorMsg MSGFILE_SCRIPT, 1, 0, 0       // "Okay, I'll take your Pokémon for a few seconds."
    ActorCmdExec 0x8011, Movement_NurseFaceMachine
    ActorCmdWait
    PokePartyGetCount 0x8001, 1
    PokecenPlayHealingSequence 0x8001
    ActorCmdExec 0x8011, Movement_NurseFaceDown
    ActorCmdWait
    PokePartyRecoverAll
    RecordAdd 11, 1                              // Black 2's "Pokémon Center used" record (Sapphire GAME_STAT_USED_POKECENTER)
    ActorMsgClose
    PlayerSetSpecialSequence 64                  // the Balls come back
    ActorCmdExec 255, Movement_NursePlayerTake
    ActorCmdWait
    PlayerSetSpecialSequence 8
    PokePartyCheckPokerus 0x8002
    WorkCmpConst 0x8002, 1
    VMJumpIf CMP_NE, L_NurseReturn
    FlagGet 101, 0x8003
    WorkCmpConst 0x8003, 0
    VMJumpIf CMP_NE, L_NurseReturn
    FlagSet 101
    ParentActorMsg MSGFILE_SCRIPT, 4, 0, 0       // Pokérus (instead of the thanks, as Sapphire)
    LastKeyWait
    ActorMsgClose
    VMJump L_NurseEnd

L_NurseReturn:
    ParentActorMsg MSGFILE_SCRIPT, 2, 0, 0       // "Thank you for waiting..."
    ActorCmdExec 0x8011, Movement_NurseBow
    ActorCmdWait
    ParentActorMsg MSGFILE_SCRIPT, 3, 0, 0       // "We hope to see you again!"
    LastKeyWait
    ActorMsgClose

L_NurseEnd:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

Movement_NurseBow:                               // Black 2's bow (1231.s Movement_0594)
    Move 100, 1
    Move 62, 1
    MoveEnd

Movement_NursePlayerGive:                        // 1231.s Movement_05A0
    Move 102, 1
    MoveEnd

Movement_NursePlayerFaceUp:                      // 1231.s Movement_05A8
    Move 0, 1
    MoveEnd

Movement_NursePlayerTake:                        // 1231.s Movement_05B0
    Move 104, 1
    MoveEnd

Movement_NurseFaceMachine:                       // face left: the machine is on her left (Sapphire)
    Move 2, 1
    MoveEnd

Movement_NurseFaceDown:
    Move 1, 1
    MoveEnd
