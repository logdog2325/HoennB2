// Gabby & Ty on Routes 111, 118 and 120 (Sapphire data/scripts/gabby_and_ty.inc; ch4 agent 2026-10-07). Shared code
// with labels: include it once in the BODY part of a route's scene file, after `#define GT_TEXT n` = the first of its
// 14 lines in that zone's text file (lines GT_TEXT+0 .. +13, in this order: Sapphire Route111_Text_1AC59E, 1AC7E4,
// 1ABED8, 1AC73B, 1AC5CA, 1AC820, 1ABF50, 1AC790, 1AC015, 1AC60B, 1AC3CF, 1AC40F, 1AC487, 1AC553).
//   Zone init (Sapphire OnTransition `call Route111_EventScript_1AE313`): VMCall Sub_GabbyTyUpdate
//   Gabby / Ty talked to: c4_gabby_ty TRAINER_GABBY_AND_TY_n, GT_GABBY or GT_TY, first (1 for Route 111's first pair)
// Black 2 gaps: Sapphire's interview data (the lead Pokémon, the last move, the battle trivia) come from gBattleResults,
// which Black 2 scripts cannot read: the "last time we battled ..." question is the plain one (trivia 0), and the quote
// from the last interview (Black 2's word picker stores none) is not repeated. The quote itself is Black 2's word picker
// (user decision 2026-10-07, nothing is broadcast).
#ifndef GABBY_TY_INC
#define GABBY_TY_INC
#include "scenes/ch4_lib.inc"
#define GT_AFTER_GABBY (GT_TEXT+0)
#define GT_AFTER_TY (GT_TEXT+1)
#define GT_INTRO1_GABBY (GT_TEXT+2)
#define GT_INTRO1_TY (GT_TEXT+3)
#define GT_NEEDTWO_GABBY (GT_TEXT+4)
#define GT_NEEDTWO_TY (GT_TEXT+5)
#define GT_INTRO_GABBY (GT_TEXT+6)
#define GT_INTRO_TY (GT_TEXT+7)
#define GT_ASK_FIRST (GT_TEXT+8)
#define GT_ASK_STRONGER (GT_TEXT+9)
#define GT_ASK_AGAIN (GT_TEXT+10)
#define GT_THANKS (GT_TEXT+11)
#define GT_CLINCHER (GT_TEXT+12)
#define GT_DONT_GIVE_UP (GT_TEXT+13)
#define GT_GABBY 0
#define GT_TY 1

// Sapphire's trainerbattle_double TRAINER_GABBY_AND_TY_n (the talked-to one's intro, "need two" line and after line),
// then the interview (Route111_EventScript_1AE5A2 for the first pair, 1AE60F for the others)
    .macro c4_gabby_ty trainer, who, first
    c4_talk
    h_goto_if_defeated \trainer, .Lgtafter\@
    h_goto_if_cannot_double .Lgtneed\@
    TrainerBGMPlayPush \trainer
    .if \first
    h_msgbox (GT_INTRO1_GABBY + \who)
    .else
    h_msgbox (GT_INTRO_GABBY + \who)
    .endif
    h_closemessage
    h_trainerbattle \trainer
    WorkSetConst C4_TMP2, \first
    VMJump Sub_GabbyTyInterview
.Lgtafter\@:
    h_msgbox (GT_AFTER_GABBY + \who)
    h_release
.Lgtneed\@:
    h_msgbox (GT_NEEDTWO_GABBY + \who)
    h_release
    .endm

Sub_GabbyTyInterview:                   // GabbyAndTyBeforeInterview (battleNum + 1) and the interview
    h_goto_if_eq VAR_GABBY_AND_TY_BATTLE_NUM, 255, L_GT_Counted
    h_addvar VAR_GABBY_AND_TY_BATTLE_NUM, 1
L_GT_Counted:
    ActorSetEyeToEye
    h_goto_if_eq C4_TMP2, 1, L_GT_AskFirst
    h_goto_if_set FLAG_GABBY_AND_TY_QUOTE, L_GT_HadQuote     // GabbyAndTyGetLastQuote
    h_yesno GT_ASK_STRONGER, C4_TMP                         // Route111_Text_1AC60B
    VMJump L_GT_Answer
L_GT_HadQuote:
    h_clearflag FLAG_GABBY_AND_TY_QUOTE                     // (the quote is used up, as Sapphire's)
    h_yesno GT_ASK_AGAIN, C4_TMP                            // trivia 0: Route111_Text_1AC3CF
    VMJump L_GT_Answer
L_GT_AskFirst:
    h_yesno GT_ASK_FIRST, C4_TMP                            // Route111_Text_1AC015
L_GT_Answer:                                                // Route111_EventScript_1AE6F3
    h_goto_if_no C4_TMP, L_GT_No
    h_msgbox GT_THANKS
    c4_easy_chat HLIB_RESULT
    WorkCmpConst HLIB_RESULT, 0
    VMJumpIf CMP_EQ, L_GT_No
    h_msgbox GT_CLINCHER
    h_setflag FLAG_GABBY_AND_TY_QUOTE                       // GabbyAndTyAfterInterview
    h_release
L_GT_No:
    h_msgbox GT_DONT_GIVE_UP
    h_release

// Route111_EventScript_1AE313 (= Route118/120's): where Gabby & Ty stand, from the number of battles
Sub_GabbyTyUpdate:
    TrainerFlagReset TRAINER_GABBY_AND_TY_6
    WorkSet C4_TMP, VAR_GABBY_AND_TY_BATTLE_NUM             // GabbyAndTyGetBattleNum: >= 6 -> n % 3 + 6
    WorkCmpConst C4_TMP, 6
    VMJumpIf CMP_LT, L_GTU_Switch
L_GTU_Mod:
    WorkCmpConst C4_TMP, 9
    VMJumpIf CMP_LT, L_GTU_Switch
    WorkSub C4_TMP, 3
    VMJump L_GTU_Mod
L_GTU_Switch:
    h_goto_if_eq C4_TMP, 0, L_GTU_0
    h_goto_if_eq C4_TMP, 1, L_GTU_1
    h_goto_if_eq C4_TMP, 2, L_GTU_2
    h_goto_if_eq C4_TMP, 3, L_GTU_3
    h_goto_if_eq C4_TMP, 4, L_GTU_4
    h_goto_if_eq C4_TMP, 5, L_GTU_5
    h_goto_if_eq C4_TMP, 6, L_GTU_6
    h_goto_if_eq C4_TMP, 7, L_GTU_7
    h_goto_if_eq C4_TMP, 8, L_GTU_8
    VMReturn
L_GTU_0:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE111_1
    VMReturn
L_GTU_1:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE118_1
    h_setflag FLAG_HIDE_GABBY_AND_TY_ROUTE111_1
    VMReturn
L_GTU_2:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE120_1
    h_setflag FLAG_HIDE_GABBY_AND_TY_ROUTE118_1
    VMReturn
L_GTU_3:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE111_2
    h_setflag FLAG_HIDE_GABBY_AND_TY_ROUTE120_1
    VMReturn
L_GTU_4:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE118_2
    h_setflag FLAG_HIDE_GABBY_AND_TY_ROUTE111_2
    VMReturn
L_GTU_5:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE120_2
    h_setflag FLAG_HIDE_GABBY_AND_TY_ROUTE118_2
    VMReturn
L_GTU_6:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE111_3
    h_setflag FLAG_HIDE_GABBY_AND_TY_ROUTE120_2
    VMReturn
L_GTU_7:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE118_3
    h_setflag FLAG_HIDE_GABBY_AND_TY_ROUTE111_3
    VMReturn
L_GTU_8:
    h_clearflag FLAG_HIDE_GABBY_AND_TY_ROUTE120_2
    h_setflag FLAG_HIDE_GABBY_AND_TY_ROUTE118_3
    VMReturn
#endif
