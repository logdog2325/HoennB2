// A Trainer Hill floor (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md): the body of the four floors' scripts
// (src/field_scripts/emerald/1088/1090/1092/1094_room_TrainerHill_nF.s define TH_FLOOR 1-4 and include this).
// pokeemerald data/maps/TrainerHill_1F/scripts.inc (the floors' shared map scripts), data/scripts/trainer_hill.inc
// (TrainerHill_EventScript_TrainerBattle) and src/trainer_hill.c.
//
// NPCs: uid u = 1 + 2 * mode + i (i = the floor's trainer 0 / 1 of that mode; each mode's room places its two, map-local
// flag 0x20 + u hides the other modes'); script u. Their words are the floor text's lines 100 + 5 * (u - 1) + 0-4 (name,
// speechBefore, speechWin, speechLose, speechAfter: b2tools/trainer_hill_text.py).
// The per-step check (trainer_hill.c TH_Step: Black 2's TrainerEye on the NPC's facing and Emerald's sight range,
// p0) starts script 11 with works TH_W_A / _SA / _DA (the trainer, its steps, its facing) and TH_W_B / _SB / _DB (a
// second trainer who sees the player at the same time: a double battle against both, as Emerald's
// CheckForTrainersWantingBattle; 0 none).

    ScriptEntry THF_Tr1                 // 1-8: the trainers (TrainerHill_EventScript_TrainerBattle)
    ScriptEntry THF_Tr2
    ScriptEntry THF_Tr3
    ScriptEntry THF_Tr4
    ScriptEntry THF_Tr5
    ScriptEntry THF_Tr6
    ScriptEntry THF_Tr7
    ScriptEntry THF_Tr8
    ScriptEntry THF_Timer               // 9: the challenge-time display (EventScript_TrainerHillTimer)
    ScriptEntry THF_Init                // 10: zone init (MapScript 2): the mode's layout and trainers
    ScriptEntry THF_Spotted             // 11: a trainer saw the player (trainer_hill.c TH_Step)
    ScriptEntriesEnd

THF_Tr1:
    WorkSetConst TH_W_A, 1
    VMJump L_THF_Talk
THF_Tr2:
    WorkSetConst TH_W_A, 2
    VMJump L_THF_Talk
THF_Tr3:
    WorkSetConst TH_W_A, 3
    VMJump L_THF_Talk
THF_Tr4:
    WorkSetConst TH_W_A, 4
    VMJump L_THF_Talk
THF_Tr5:
    WorkSetConst TH_W_A, 5
    VMJump L_THF_Talk
THF_Tr6:
    WorkSetConst TH_W_A, 6
    VMJump L_THF_Talk
THF_Tr7:
    WorkSetConst TH_W_A, 7
    VMJump L_THF_Talk
THF_Tr8:
    WorkSetConst TH_W_A, 8
L_THF_Talk:                             // talked to: beaten -> speechAfter (trainerhill_postbattletext), else it battles
    h_lock                              // alone (TRAINER_BATTLE_HILL with no approaching trainer: a single battle)
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    WorkSetConst TH_W_B, 0
    WorkSet TH_T0, TH_W_A
    ThHill TH_OP_BEATEN, TH_T0
    h_goto_if_eq TH_T0, 0, L_THF_Greet
    WorkSet TH_T0, TH_W_A
    ThHill TH_OP_LINE | 4, TH_T0        // speechAfter
    ActorMsg MSGFILE_SCRIPT, TH_T0, TH_W_A, 0, 0
    LastKeyWait
    h_closemessage
    h_release

THF_Timer:                              // trainerhill_gettime: "<m> min. <s>.<hh> sec."
    h_lock
    SEPlay SEQ_SE_MESSAGE
    ThHill TH_OP_TIME_WORDS | 1, TH_T0
    h_msgbox_info 0
    h_closemessage
    h_release

THF_Init:
    th_floor_init TH_FLOOR

// ---- spotted: "!", the walk up, the greeting; a second trainer does the same; then the battle
THF_Spotted:
    ActorsPauseAll
    h_applymovement TH_W_A, THF_MvExclaim
    h_waitmovement
L_THF_ApproachA:
    h_goto_if_eq TH_W_SA, 0, L_THF_FacedA
    VMCall Sub_THF_StepA
    WorkSub TH_W_SA, 1
    VMJump L_THF_ApproachA
L_THF_FacedA:                           // the player turns to the trainer (against its facing)
    WorkSet TH_T3, TH_W_DA
    VMCall Sub_THF_FacePlayer
    h_goto_if_eq TH_W_B, 0, L_THF_Greet
    h_applymovement TH_W_B, THF_MvExclaim
    h_waitmovement
L_THF_ApproachB:
    h_goto_if_eq TH_W_SB, 0, L_THF_FacedB
    VMCall Sub_THF_StepB
    WorkSub TH_W_SB, 1
    VMJump L_THF_ApproachB
L_THF_FacedB:
L_THF_Greet:                            // speechBefore (one, or both: A then B)
    WorkSet TH_T0, TH_W_A
    ThHill TH_OP_LINE | 1, TH_T0
    ActorMsg MSGFILE_SCRIPT, TH_T0, TH_W_A, 0, 0
    LastKeyWait
    h_closemessage
    h_goto_if_eq TH_W_B, 0, L_THF_Battle
    WorkSet TH_T3, TH_W_DB
    VMCall Sub_THF_FacePlayer
    WorkSet TH_T0, TH_W_B
    ThHill TH_OP_LINE | 1, TH_T0
    ActorMsg MSGFILE_SCRIPT, TH_T0, TH_W_B, 0, 0
    LastKeyWait
    h_closemessage
L_THF_Battle:                           // the floor trainers' parties at the player's highest level, no experience
    ThHill TH_OP_BATTLE, TH_T0          // (trainer_hill.c TH_LoadTrainer); a loss goes on (no whiteout)
    h_goto_if_ne TH_W_B, 0, L_THF_Double
    CallTrainerBattle TH_TR_A, 0, 1
    VMJump L_THF_Result
L_THF_Double:
    CallTrainerBattle TH_TR_A, TH_TR_B, 1
L_THF_Result:
    CallTrainerBattleEnd
    TrainerBattleIsVictory TH_T1
    h_goto_if_ne TH_T1, 1, L_THF_Lost
    ThHill TH_OP_WON, TH_T0             // SetHillTrainerFlag (both, in a double)
    h_release
L_THF_Lost:                             // TrainerHill_1F_EventScript_Lost: the winner's speechWin (Emerald shows it in the
    WorkSet TH_T0, TH_W_A               // battle), every trainer flag set, hasLost; to the counter (9,6)
    ThHill TH_OP_LINE | 2, TH_T0
    ActorMsg MSGFILE_SCRIPT, TH_T0, TH_W_A, 0, 0
    LastKeyWait
    h_closemessage
    ThHill TH_OP_LOST, TH_T0
    h_warp_arrive TH_Z_ENTRANCE, TH_EX(9), TH_EZ(6), 3      // warp MAP_TRAINER_HILL_ENTRANCE, 9, 6 (facing the counter)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Sub_THF_StepA:
    h_call_if_eq TH_W_DA, 0, Sub_THF_UpA
    h_call_if_eq TH_W_DA, 1, Sub_THF_DownA
    h_call_if_eq TH_W_DA, 2, Sub_THF_LeftA
    h_call_if_eq TH_W_DA, 3, Sub_THF_RightA
    VMReturn
Sub_THF_StepB:
    h_call_if_eq TH_W_DB, 0, Sub_THF_UpB
    h_call_if_eq TH_W_DB, 1, Sub_THF_DownB
    h_call_if_eq TH_W_DB, 2, Sub_THF_LeftB
    h_call_if_eq TH_W_DB, 3, Sub_THF_RightB
    VMReturn
Sub_THF_UpA:
    h_applymovement TH_W_A, THF_MvUp
    h_waitmovement
    VMReturn
Sub_THF_DownA:
    h_applymovement TH_W_A, THF_MvDown
    h_waitmovement
    VMReturn
Sub_THF_LeftA:
    h_applymovement TH_W_A, THF_MvLeft
    h_waitmovement
    VMReturn
Sub_THF_RightA:
    h_applymovement TH_W_A, THF_MvRight
    h_waitmovement
    VMReturn
Sub_THF_UpB:
    h_applymovement TH_W_B, THF_MvUp
    h_waitmovement
    VMReturn
Sub_THF_DownB:
    h_applymovement TH_W_B, THF_MvDown
    h_waitmovement
    VMReturn
Sub_THF_LeftB:
    h_applymovement TH_W_B, THF_MvLeft
    h_waitmovement
    VMReturn
Sub_THF_RightB:
    h_applymovement TH_W_B, THF_MvRight
    h_waitmovement
    VMReturn
Sub_THF_FacePlayer:                     // TH_T3 = the trainer's facing: the player faces the other way
    h_call_if_eq TH_T3, 0, Sub_THF_FaceDown
    h_call_if_eq TH_T3, 1, Sub_THF_FaceUp
    h_call_if_eq TH_T3, 2, Sub_THF_FaceRight
    h_call_if_eq TH_T3, 3, Sub_THF_FaceLeft
    VMReturn
Sub_THF_FaceUp:
    h_turnobject TH_PLAYER, 0
    VMReturn
Sub_THF_FaceDown:
    h_turnobject TH_PLAYER, 1
    VMReturn
Sub_THF_FaceLeft:
    h_turnobject TH_PLAYER, 2
    VMReturn
Sub_THF_FaceRight:
    h_turnobject TH_PLAYER, 3
    VMReturn

    .balign 4, 0
THF_MvExclaim:
    emote_exclamation_mark
    step_end
    .balign 4, 0
THF_MvUp:
    walk_up
    step_end
    .balign 4, 0
THF_MvDown:
    walk_down
    step_end
    .balign 4, 0
THF_MvLeft:
    walk_left
    step_end
    .balign 4, 0
THF_MvRight:
    walk_right
    step_end
