// Pokémon Emerald NDS: Emerald's rematches (emerald_rematch, 2026-10-18; notes/EMERALD_REMATCH.md). Include after
// "asm/field_script.inc", "hoenn.h" and "hoenn_story.inc". Emits no code by itself; in a Sapphire or Ruby build the
// macros below are empty (the build is byte-identical without them).
//
// The rematch table, the 292 rematch slots (each tier's record and party) and the script command are Emerald's only:
// data/emerald/hoenn_rematch.json (converter/gen_trainers.py), b2tools/patches/emerald_rematch.py / .c. Route trainers
// rematch through Black 2's global trainer script (src/field_scripts/emerald/1239_global_trainers.s); the Gym Leaders'
// scripts call em_gym_rematch where they handle an already beaten Leader, and so does Wally's post-game script at
// Victory Road's exit (0340_room_VictoryRoad_1F.s: a post-game row, tiers in turn as a Leader's).

#ifndef HOENN_REMATCH_INC
#define HOENN_REMATCH_INC

// ---- the script command (b2tools/patches/emerald_rematch.c EM_RmCmd; command 299, Black 2's unused BMAnmPlayInv) -----
//     EmRematch var, op, arg          arg: a number or a work
#define RM_QUERY    0   // arg = the first battle's trainer id: var = RM_NONE / RM_SINGLE / RM_DOUBLE / RM_POST
#define RM_ARM      1   // arg = trainer id: the next battle with it (and Tate's partner Liza) loads today's tier
#define RM_DISARM   2   // right after the battle, won or lost
#define RM_WON      3   // arg = trainer id: fought today; a Gym Leader's next tier
#define RM_MSGBASE  4   // arg = TrainerGetMessageTypes' intro type: var = RM_MSG_INTRO, or RM_MSG_INTRO2 for type 7
                        // (the second NPC of a pair)
#define RM_NONE     0   // no rematch now (fewer than 5 badges; a Leader before the Hall of Fame): the usual line
#define RM_SINGLE   1   // a rematch, a single battle
#define RM_DOUBLE   2   // a rematch, a double battle (two Pokémon able to battle needed)
#define RM_POST     3   // fought today (or a Leader whose next tier waits for Wattson's job): the after-rematch line

// message types of the first battle's trainer (converter/gen_trainers.py REMATCH_MSG)
#define RM_MSG_INTRO   100
#define RM_MSG_POST    101
#define RM_MSG_CANNOT  102
#define RM_MSG_DEFEAT  103      // in battle (emerald_rematch.c swaps it for type 1 while the rematch is fought)
#define RM_MSG_INTRO2  104      // the second NPC of a pair: 104 intro, 105 after, 106 "you need two Pokémon"

    .macro EmRematch var, op, arg
    FieldCommand 299
    .2byte \var
    .2byte \op
    .2byte \arg
    .endm

// A Gym Leader already beaten (put it first where the Leader's script handles that): after the Hall of Fame, once a
// day, Emerald's rematch team (tiers 2-5 in turn; tiers 3-5 after Wattson's New Mauville job, as Emerald). The Leader
// says Emerald's rematch line, then YES / NO; a double battle needs two Pokémon (Emerald's "need two" line). Won: the
// after-rematch line. Lost: the whiteout. Ends the script unless there is no rematch now (falls through).
//     em_gym_rematch TRAINER_ROXANNE, RG_ROXANNE
//     em_gym_rematch TRAINER_TATE, MG_TATE, TRAINER_LIZA      (Tate & Liza: both fought together, as their first battle)
    .macro em_gym_rematch id, actor, id2=0
#ifdef HOENN_EMERALD
    EmRematch HLIB_TMP, RM_QUERY, \id
    WorkCmpConst HLIB_TMP, RM_NONE
    VMJumpIf CMP_EQ, .Lemrm_none\@
    WordSetPlayerName 0
    WorkCmpConst HLIB_TMP, RM_POST
    VMJumpIf CMP_EQ, .Lemrm_post\@
    WorkCmpConst HLIB_TMP, RM_DOUBLE
    VMJumpIf CMP_NE, .Lemrm_ask\@
    PokePartyGetCount HLIB_TMP, 2
    WorkCmpConst HLIB_TMP, 2
    VMJumpIf CMP_GE, .Lemrm_ask\@
    TrainerSayMessage \id, RM_MSG_CANNOT, \actor
    VMJump .Lemrm_wait\@
.Lemrm_ask\@:
    TrainerSayMessage \id, RM_MSG_INTRO, \actor
    YesNoWin HLIB_RESULT
    ActorMsgClose
    WorkCmpConst HLIB_RESULT, 0
    VMJumpIf CMP_NE, .Lemrm_end\@
    EmRematch HLIB_TMP, RM_ARM, \id
    CallTrainerBattle \id, \id2, 0
    EmRematch HLIB_TMP, RM_DISARM, 0
    TrainerBattleIsVictory HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, .Lemrm_won\@
    CallTrainerLose
    VMHalt
.Lemrm_won\@:
    CallTrainerBattleEnd
    EmRematch HLIB_TMP, RM_WON, \id
    WordSetPlayerName 0
.Lemrm_post\@:
    TrainerSayMessage \id, RM_MSG_POST, \actor
.Lemrm_wait\@:
    LastKeyWait
    ActorMsgClose
.Lemrm_end\@:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
.Lemrm_none\@:
#endif
    .endm

#endif
