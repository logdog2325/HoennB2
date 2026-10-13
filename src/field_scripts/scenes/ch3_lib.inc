// Chapter 3 helpers (ch3a, 2026-10-07): macros only (no code until used). Include after "hoenn_story.inc".
#ifndef CH3_LIB_INC
#define CH3_LIB_INC

// Key items Black 2 has no copy of (ITEM_DEVON_GOODS = ITEM_PARCEL, ITEM_POKEBLOCK_CASE = ITEM_POFFIN_CASE, renamed):
// the central table (story_infra, converter/gen_key_items.py)
#include "hoenn_key_items.h"

// script works of these helpers (HLIB_TMP/HLIB_RESULT are 0x8030/0x8031)
#define C3_LEAD 0x8032                  // party slot of the lead Pokémon (c3_lead_mon)
#define C3_TMP 0x8033
#define C3_TMP2 0x8034
#define C3_SEL 0x8035
#define C3_SHOP 0x8036

// lock + faceplayer of a talked-to person, as Black 2's NPC scripts start (ActorsPauseAll, talk sound, face)
    .macro c3_talk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    .endm

// Sapphire's GetLeadMonIndex (bufferleadmonspeciesname, the fan club's and Effort Ribbon's "lead Pokémon"): the first
// party Pokémon that is not an Egg -> C3_LEAD (0 if none). Black 2's PokePartyGetMemberByType 2 would also skip fainted
// ones, so the slots are walked here.
    .macro c3_lead_mon
    PokePartyGetCount C3_TMP2, 0
    WorkSetConst C3_LEAD, 0
.Lc3lm\@:
    WorkCmpWork C3_LEAD, C3_TMP2
    VMJumpIf CMP_GE, .Lc3none\@
    PokePartyIsEgg C3_TMP, C3_LEAD
    WorkCmpConst C3_TMP, 0
    VMJumpIf CMP_EQ, .Lc3done\@
    WorkAdd C3_LEAD, 1
    VMJump .Lc3lm\@
.Lc3none\@:
    WorkSetConst C3_LEAD, 0
.Lc3done\@:
    .endm

// Sapphire's `pokemart LIST` after its greeting (src/shop.c, MART_TYPE_0): the Buy / Sell / Quit menu, and "Is there
// anything else I can help you with?" after buying or selling. Black 2's own pieces as its shop script uses them
// (global 1247: ListMenu_AnchorTopRight, CallFriendlyShopBuy, CallBag 0 between FieldClose/FieldOpen). The menu sits at
// row 9 (1247 uses row 1): Sapphire's greetings are longer than Black 2's and a top balloon would be covered.
// The greeting is already in the talked-to person's window; C3_SHOP = the shop list id (data/hoenn_shops.json).
// tbuy/tsell/tquit/tagain = the zone's lines "Buy", "Sell", "Quit", "Is there anything else...".
    .macro c3_mart_sub label, tbuy, tsell, tquit, tagain
\label:
.Lc3menu\@:
    ListMenu_AnchorTopRight 31, 9, 0, 1, C3_SEL
    ListMenuAdd \tbuy, 65535, 1
    ListMenuAdd \tsell, 65535, 2
    ListMenuAdd \tquit, 65535, 0
    ListMenuShow
    WorkCmpConst C3_SEL, 1
    VMJumpIf CMP_EQ, .Lc3buy\@
    WorkCmpConst C3_SEL, 2
    VMJumpIf CMP_EQ, .Lc3sell\@
    VMReturn
.Lc3buy\@:
    ActorMsgClose
    CallFriendlyShopBuy C3_SHOP, C3_TMP
    VMJump .Lc3again\@
.Lc3sell\@:
    FadeOutBlackQ
    FadeWait
    ActorMsgClose
    FieldClose
    CallBag 0, C3_TMP, C3_TMP2
    FieldOpen
    FadeInBlackQ
    FadeWait
.Lc3again\@:
    ParentActorMsg MSGFILE_SCRIPT, \tagain, 0, 0
    VMJump .Lc3menu\@
    .endm

// a person that says one line and turns back (msgbox MSGBOX_DEFAULT, closemessage, Common_Movement_FaceOriginalDirection)
    .macro c3_say_turn_back n, uid, dir
    c3_talk
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0
    LastKeyWait
    ActorMsgClose
    h_turnobject \uid, \dir
    h_release
    .endm
// Common_EventScript_ShowEasyChatScreen (a TV interview's answer): Black 2 has no Easy Chat sentences for TV shows;
// its closest is the word picker of its own quiz (zone 0234: CallPhraseSelect 4 between FieldClose and FieldOpen),
// which stores nothing. ok = 1 when a word was picked (Sapphire's VAR_RESULT 1), else 0.
    .macro c3_easy_chat ok
    MsgWinCloseAll
    FadeOutBlackQ
    FadeWait
    FieldClose
    CallPhraseSelect 4, C3_TMP, C3_TMP2, \ok
    FieldOpen
    FadeInBlackQ
    FadeWait
    .endm
#endif
