// Secret Bases and decorations (notes/SECRET_BASES.md), global scripts 10735-: Black 2's file 1281 / text 436, script
// plugin 9's (the PWT's "Boss Trainer" lines), which no Hoenn zone starts. pokeruby data/scripts/secret_base.inc,
// shared_secret_base.inc, data/maps/*; the specials are sub-commands of the extension command 0x15F (common/secret_base_defs.inc).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "common/secret_base_defs.inc"
#include "common/secret_base_lines.inc"

    ScriptEntry Script_Spot         // 10735: a spot actor (data/story/secret_bases.json)
    ScriptEntry Script_PC           // 10736: the base's PC
    ScriptEntry Script_Answer       // 10737: shield, toy TV, sand ornament (Black 2's tile class 0xd7)
    ScriptEntry Script_RoomDecor    // 10738: the bedroom PC's Decoration
    ScriptEntry Script_Shop         // 10739: 0x8010 = the shop's list
    ScriptEntry Script_Give         // 10740: 0x8010 = the decoration; 0x8012 = 1 given
    ScriptEntry Script_First        // 10741: the first visit, reserved by the overlay
    ScriptEntry Script_Jump         // 10742: the jump mat
    ScriptEntry Script_Spin         // 10743: the spin mat
    ScriptEntry Script_Leave        // 10744: (reserved)
    ScriptEntry Script_HasRoom      // 10745: 0x8010 = the decoration; 0x8012 = 1 it fits
    ScriptEntriesEnd

    .macro sb_ifeq var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_EQ, \label
    .endm
    .macro sb_ifne var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_NE, \label
    .endm
    .macro sb_end
    MsgWinCloseAll
    SBCmd SB_OP_UNLOAD, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm

// ---- the spot: gUnknown_081A2C51 ------------------------------------------------------------------------------------
Script_Spot:
    ActorsPauseAll
    SBCmd SB_OP_SPOT, 0
    sb_ifeq SB_W_RES, 0, L_SpotEnd                // BG_EVENT_SECRET_BASE: only facing north
    sb_ifeq SB_W_D, 1, L_SpotEnterOwn
    sb_ifeq SB_W_D, 2, L_SpotMove
    sb_ifeq SB_W_C, 6, L_SpotNoMove
L_SpotAsk:
    WordSetPartyPokeName 0, SB_W_C
    sb_ifeq SB_W_B, 5, L_AskTree
    sb_ifeq SB_W_B, 6, L_AskShrub
    SystemMsg SBT_INDENT_USE, 2
    VMJump L_AskYesNo
L_AskTree:
    SystemMsg SBT_TREE_USE, 2
    VMJump L_AskYesNo
L_AskShrub:
    SystemMsg SBT_SHRUB_USE, 2
L_AskYesNo:
    YesNoWin SB_W_LIST
    sb_ifne SB_W_LIST, 0, L_SpotEnd
L_SpotUse:
    WordSetPartyPokeName 0, SB_W_C
    SystemMsg SBT_USED, 2
    InfoMsgClose
    PlayHMCutInEffect SB_W_C
    sb_ifeq SB_W_B, 5, L_FoundTree
    sb_ifeq SB_W_B, 6, L_FoundShrub
    SystemMsg SBT_CAVERN, 2
    VMJump L_Found
L_FoundTree:
    SystemMsg SBT_VINE, 2
    VMJump L_Found
L_FoundShrub:
    SystemMsg SBT_ENTRANCE, 2
L_Found:
    LastKeyWait
    InfoMsgClose
    FieldSetNextZoneHere                          // saved_warp2_set: back here on the way out
    SEPlay SEQ_SE_FLD_21
    FadeOutBlack
    FadeWait
    SBCmd SB_OP_UNLOAD, 0
    SBCmd SB_OP_ENTER, 1                          // a first visit: "Want to make your Secret Base here?"
    VMHalt

L_SpotEnterOwn:                                   // gUnknown_081A2E14: into the player's own base
    FieldSetNextZoneHere
    SEPlay SEQ_SE_FLD_21
    FadeOutBlack
    RTReserveScript 10017                         // the arrival fades in (h_warp_arrive's pattern)
    FadeWait
    SBCmd SB_OP_UNLOAD, 0
    SBCmd SB_OP_ENTER, 0
    VMHalt

L_SpotNoMove:
    sb_ifeq SB_W_B, 5, L_NoMoveTree
    sb_ifeq SB_W_B, 6, L_NoMoveShrub
    SystemMsg SBT_INDENT, 2
    VMJump L_NoMoveEnd
L_NoMoveTree:
    SystemMsg SBT_TREE, 2
    VMJump L_NoMoveEnd
L_NoMoveShrub:
    SystemMsg SBT_SHRUB, 2
L_NoMoveEnd:
    LastKeyWait
L_SpotEnd:
    sb_end

L_SpotMove:                                       // AskToMoveSecretBase
    sb_ifeq SB_W_C, 6, L_SpotNoMove
    VMStackPush SB_W_A
    SBCmd SB_OP_BASE_PLACE_WORD, 0
    WordSetPlaceName 0, SB_W_A
    VMStackPop SB_W_A
    SystemMsg SBT_ONLY_ONE, 2
    YesNoWin SB_W_LIST
    sb_ifne SB_W_LIST, 0, L_SpotEnd
    SystemMsg SBT_RETURNED, 2
    YesNoWin SB_W_LIST
    sb_ifne SB_W_LIST, 0, L_SpotEnd
    InfoMsgClose
    FadeOutBlackQ
    FadeWait
    SBCmd SB_OP_MOVE_OUT, 0
    FadeInBlackQ
    FadeWait
    SystemMsg SBT_MOVED, 2
    YesNoWin SB_W_LIST
    sb_ifne SB_W_LIST, 0, L_SpotEnd
    VMJump L_SpotUse

// ---- the first visit: SecretBase_EventScript_FirstEntrance ------------------------------------------------------------
Script_First:
    ActorsPauseAll
    FadeInBlack                                   // (reserved instead of 10017: the entry's fade-out ends here)
    FadeWait
    h_applymovement 255, L_WalkUp2
    h_waitmovement
    SystemMsg SBT_MAKE, 2
    YesNoWin SB_W_LIST
    InfoMsgClose
    sb_ifne SB_W_LIST, 0, L_FirstNo
    SBCmd SB_OP_MAKE, 0                           // sub_80BBC78: to the tile in front of the PC
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    SBCmd SB_OP_UNLOAD, 0
    SBCmd SB_OP_ENTER, 2
    VMHalt
L_FirstNo:
    SEPlay SEQ_SE_FLD_21                          // sub_80BC440: back outside
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    SBCmd SB_OP_LEAVE, 0
    SBCmd SB_OP_UNLOAD, 0
    VMHalt

    .balign 4, 0
L_WalkUp2:
    walk_up 2
    step_end

// ---- the base's PC: SecretBase_EventScript_PC -------------------------------------------------------------------------
Script_PC:
    ActorsPauseAll
    SEPlay SEQ_SE_PC_LOGIN
    WordSetPlayerName 0
    SystemMsg SBT_BOOT, 2
    LastKeyWait
L_PCMain:
    SystemMsg SBT_WHAT, 2
    ListMenu_AnchorTopLeft 1, 1, 0, 1, SB_W_LIST
    ListMenuAdd SBT_DECORATION, 0xffff, 0
    ListMenuAdd SBT_PACK_UP, 0xffff, 1
    ListMenuAdd SBT_TURN_OFF, 0xffff, 2
    ListMenuShow
    sb_ifeq SB_W_LIST, 0, L_PCDecoration
    sb_ifeq SB_W_LIST, 1, L_PCPackUp
    SEPlay SEQ_SE_PC_LOGOFF
    sb_end
L_PCPackUp:                                       // SecretBase_EventScript_PCPackUp
    SystemMsg SBT_RETURNED, 2
    YesNoWin SB_W_LIST
    sb_ifne SB_W_LIST, 0, L_PCMain
    InfoMsgClose
    SBCmd SB_OP_MOVE_OUT, 0                       // MoveOutOfSecretBase: out by the way the player came in
    SEPlay SEQ_SE_FLD_21
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    SBCmd SB_OP_LEAVE, 0
    VMHalt
L_PCDecoration:
    VMCall L_DecorationMenu
    VMJump L_PCMain

// ---- the bedroom's PC: its Decoration entry ---------------------------------------------------------------------------
Script_RoomDecor:                                 // SB_W_RES = 1: the caller opens Black 2's PC; 0: nothing more
    SEPlay SEQ_SE_PC_LOGIN                        // (Black 2's own PC says "<player> booted up the PC.")
L_RoomMain:
    SystemMsg SBT_WHAT, 2
    ListMenu_AnchorTopLeft 1, 1, 0, 1, SB_W_LIST
    ListMenuAdd SBT_PC, 0xffff, 0
    ListMenuAdd SBT_DECORATION, 0xffff, 1
    ListMenuAdd SBT_TURN_OFF, 0xffff, 2
    ListMenuShow
    sb_ifeq SB_W_LIST, 0, L_RoomPC
    sb_ifeq SB_W_LIST, 1, L_RoomDecor
    SEPlay SEQ_SE_PC_LOGOFF
    WorkSetConst SB_W_RES, 0
    VMJump L_RoomEnd
L_RoomDecor:
    VMCall L_DecorationMenu
    VMJump L_RoomMain
L_RoomPC:
    WorkSetConst SB_W_RES, 1
L_RoomEnd:
    MsgWinCloseAll
    VMStackPush SB_W_RES
    SBCmd SB_OP_UNLOAD, 0
    VMStackPop SB_W_RES
    RTEndGlobal

// ---- the Decoration menu: decoration.c ------------------------------------------------------------------------------
L_DecorationMenu:
    SystemMsg SBT_WHAT, 2
    ListMenu_AnchorTopLeft 1, 1, 0, 1, SB_W_LIST
    ListMenuAdd SBT_DECORATE, SBT_DESC_DECORATE, 0
    ListMenuAdd SBT_PUT_AWAY, SBT_DESC_PUT_AWAY, 1
    ListMenuAdd SBT_TOSS, SBT_DESC_TOSS, 2
    ListMenuAdd SBT_CANCEL, 0xffff, 3
    ListMenuShow
    sb_ifeq SB_W_LIST, 0, L_Decorate
    sb_ifeq SB_W_LIST, 1, L_PutAway
    sb_ifeq SB_W_LIST, 2, L_Toss
    VMReturn

L_ChooseCategory:                                 // SB_W_B = the category, 0xfff1 cancelled
    SystemMsg SBT_WHAT, 2
    ListMenu_AnchorTopLeft 1, 1, 0, 1, SB_W_B
    SBCmd SB_OP_CATEGORIES, 0
    ListMenuShow
    VMReturn

L_ChooseItem:                                     // SB_W_LIST = the slot, 0xfff1 cancelled, 0xfffe B. A window for the
    SystemMsg SBT_WHAT, 2                         // descriptions must be open: the previous line's
L_ChooseItemList:
    ListMenu_AnchorTopLeft 1, 1, 0, 1, SB_W_LIST
    SBCmd SB_OP_ITEMS, SB_W_B
    sb_ifeq SB_W_RES, 0, L_ChooseItemNone
    ListMenuShow
    sb_ifeq SB_W_LIST, 0xfff0, L_ChooseItemList   // More...
    VMReturn
L_ChooseItemNone:
    ListMenuShow                                  // (only Cancel)
    WorkSetConst SB_W_LIST, 0xfff1
    SystemMsg SBT_NO_DECORS, 2
    LastKeyWait
    VMReturn

L_Decorate:
    VMCall L_ChooseCategory
    sb_ifeq SB_W_B, 0xfff1, L_DecorationMenu
    sb_ifeq SB_W_B, 0xfffe, L_DecorationMenu
    SBCmd SB_OP_CANT_ROOM, SB_W_B
    sb_ifeq SB_W_RES, 1, L_DecorateCantRoom
L_DecorateItem:
    VMCall L_ChooseItem
    sb_ifeq SB_W_LIST, 0xfff1, L_Decorate
    sb_ifeq SB_W_LIST, 0xfffe, L_Decorate
    SBCmd SB_OP_SLOT_CHECK, SB_W_LIST
    sb_ifeq SB_W_RES, 3, L_DecorateFull
    sb_ifne SB_W_RES, 0, L_DecorateInUse
    // the cursor: sub_80FF5AC. Its model comes in with the field
    InfoMsgClose
    SBCmd SB_OP_PLACE_BEGIN, SB_W_ARG
    FadeOutBlackQ
    FadeWait
    FieldClose
    FieldOpen
    FadeInBlackQ
    FadeWait
L_DecorateCursor:
    SBCmd SB_OP_CURSOR, SB_W_ARG
    sb_ifeq SB_W_RES, 0, L_DecorateCancel
    SBCmd SB_OP_CAN_PLACE, 0
    sb_ifeq SB_W_RES, 0, L_DecorateCant
    SystemMsg SBT_PLACE, 2
    YesNoWin SB_W_LIST
    InfoMsgClose
    sb_ifne SB_W_LIST, 0, L_DecorateCursor
    SBCmd SB_OP_PLACE, 0
    VMJump L_DecorateDone
L_DecorateCant:
    SEPlay SEQ_SE_BEEP
    SystemMsg SBT_CANT_PLACE, 2
    LastKeyWait
    InfoMsgClose
    VMJump L_DecorateCursor
L_DecorateCancel:
    SystemMsg SBT_CANCEL_DECORATING, 2
    YesNoWin SB_W_LIST
    InfoMsgClose
    sb_ifne SB_W_LIST, 0, L_DecorateCursor
L_DecorateDone:
    SBCmd SB_OP_CURSOR_END, 0
    FadeOutBlackQ
    FadeWait
    FieldClose
    FieldOpen
    FadeInBlackQ
    FadeWait
    VMJump L_DecorationMenu
L_DecorateCantRoom:
    SystemMsg SBT_CANT_ROOM, 2
    LastKeyWait
    VMJump L_Decorate
L_DecorateInUse:
    SystemMsg SBT_IN_USE, 2
    LastKeyWait
    VMJump L_DecorateItem
L_DecorateFull:
    SBCmd SB_OP_ROOM_MAX, 0
    sb_ifeq SB_W_RES, 12, L_DecorateFull12
    SystemMsg SBT_NO_MORE_16, 2
    LastKeyWait
    VMJump L_DecorateItem
L_DecorateFull12:
    SystemMsg SBT_NO_MORE_12, 2
    LastKeyWait
    VMJump L_DecorateItem

L_PutAway:                                        // sub_8100A0C
    SBCmd SB_OP_PUTAWAY_BEGIN, 0
    sb_ifeq SB_W_RES, 0, L_PutAwayNone
    InfoMsgClose
L_PutAwayCursor:
    SBCmd SB_OP_CURSOR, 0
    sb_ifeq SB_W_RES, 0, L_PutAwayStop
    SBCmd SB_OP_PUTAWAY_AT, 0
    sb_ifeq SB_W_ARG, 0, L_PutAwayNothing
    SystemMsg SBT_RETURN, 2
    YesNoWin SB_W_LIST
    InfoMsgClose
    sb_ifne SB_W_LIST, 0, L_PutAwayCursor
    SBCmd SB_OP_PUTAWAY, 0
    SBCmd SB_OP_CURSOR_END, 0
    FadeOutBlackQ
    FadeWait
    FieldClose
    FieldOpen
    FadeInBlackQ
    FadeWait
    SystemMsg SBT_DECOR_RETURNED, 2
    LastKeyWait
    VMJump L_PutAway
L_PutAwayNothing:
    SystemMsg SBT_NO_DECOR, 2
    LastKeyWait
    InfoMsgClose
    VMJump L_PutAwayCursor
L_PutAwayStop:
    SystemMsg SBT_STOP_PUT_AWAY, 2
    YesNoWin SB_W_LIST
    InfoMsgClose
    sb_ifne SB_W_LIST, 0, L_PutAwayCursor
    SBCmd SB_OP_CURSOR_END, 0
    VMJump L_DecorationMenu
L_PutAwayNone:
    SystemMsg SBT_NONE_IN_USE, 2
    LastKeyWait
    VMJump L_DecorationMenu

L_Toss:                                           // sub_8101700
    VMCall L_ChooseCategory
    sb_ifeq SB_W_B, 0xfff1, L_DecorationMenu
    sb_ifeq SB_W_B, 0xfffe, L_DecorationMenu
L_TossItem:
    VMCall L_ChooseItem
    sb_ifeq SB_W_LIST, 0xfff1, L_Toss
    sb_ifeq SB_W_LIST, 0xfffe, L_Toss
    SBCmd SB_OP_SLOT_CHECK, SB_W_LIST
    sb_ifeq SB_W_RES, 1, L_TossInUse
    sb_ifeq SB_W_RES, 2, L_TossInUse
    SBCmd SB_OP_WORD, 0
    SystemMsg SBT_DISCARD, 2
    YesNoWin SB_W_D
    sb_ifne SB_W_D, 0, L_TossItem
    SBCmd SB_OP_TOSS, SB_W_LIST
    SystemMsg SBT_THROWN, 2
    LastKeyWait
    VMJump L_TossItem
L_TossInUse:
    SystemMsg SBT_TOSS_IN_USE, 2
    LastKeyWait
    VMJump L_TossItem

// ---- decorations that answer A: SecretBase_EventScript_SandOrnament, ShieldOrToyTV ---------------------------------------
Script_Answer:
    ActorsPauseAll
    SBCmd SB_OP_AT_FRONT, 0
    sb_ifeq SB_W_RES, 5, L_Sand
    sb_ifeq SB_W_ARG, 42, L_Silver
    sb_ifeq SB_W_ARG, 43, L_Gold
    sb_ifeq SB_W_RES, 3, L_SeedotTV
    sb_ifeq SB_W_RES, 4, L_SkittyTV
    sb_ifeq SB_W_RES, 2, L_ToyTV
    sb_end
L_Silver:
    SystemMsg SBT_SHIELD_SILVER, 2
    VMJump L_AnswerEnd
L_Gold:
    SystemMsg SBT_SHIELD_GOLD, 2
    VMJump L_AnswerEnd
L_ToyTV:
    SystemMsg SBT_TOY_TV, 2
    VMJump L_AnswerEnd
L_SeedotTV:
    SystemMsg SBT_SEEDOT_TV, 2
    VMJump L_AnswerEnd
L_SkittyTV:
    SystemMsg SBT_SKITTY_TV, 2
L_AnswerEnd:
    LastKeyWait
    sb_end
L_Sand:                                           // FLDEFF_SAND_PILLAR: it crumbles until the next visit
    SEPlay SEQ_SE_FLD_15
    SBCmd SB_OP_HIDE_FRONT, 0
    sb_end

// ---- the mats: fldeff_decoration.c ---------------------------------------------------------------------------------------
Script_Jump:
    ActorsPauseAll
    h_getplayerfacing SB_W_LIST
    sb_ifeq SB_W_LIST, 0, L_JumpN
    sb_ifeq SB_W_LIST, 1, L_JumpS
    sb_ifeq SB_W_LIST, 2, L_JumpW
    h_applymovement 255, L_MoveJumpE
    VMJump L_MatEnd
L_JumpN:
    h_applymovement 255, L_MoveJumpN
    VMJump L_MatEnd
L_JumpS:
    h_applymovement 255, L_MoveJumpS
    VMJump L_MatEnd
L_JumpW:
    h_applymovement 255, L_MoveJumpW
    VMJump L_MatEnd
Script_Spin:
    ActorsPauseAll
    h_applymovement 255, L_MoveSpin
L_MatEnd:
    h_waitmovement
    sb_end
Script_Leave:
    VMHalt

    .balign 4, 0
L_MoveJumpN:
    jump_in_place_up
    step_end
    .balign 4, 0
L_MoveJumpS:
    jump_in_place_down
    step_end
    .balign 4, 0
L_MoveJumpW:
    jump_in_place_left
    step_end
    .balign 4, 0
L_MoveJumpE:
    jump_in_place_right
    step_end
    .balign 4, 0
L_MoveSpin:
    face_down
    face_left
    face_up
    face_right
    face_down
    step_end

// ---- a shop: pokemartdecoration ---------------------------------------------------------------------------------------
Script_Shop:
    WorkSet SB_W_C, 0x8010                        // the shop's list
L_ShopMenu:
    SBCmd SB_OP_SHOP_IS_BP, SB_W_C
    sb_ifeq SB_W_RES, 1, L_ShopList
    MoneyWinDisp 31, 1
L_ShopList:
    SBCmd SB_OP_SHOP_IS_BP, SB_W_C
    sb_ifeq SB_W_RES, 1, L_ShopListBP
    SystemMsg SBT_WHAT, 2
    VMJump L_ShopListGo
L_ShopListBP:
    SBCmd SB_OP_BP_WORD, 0
    SystemMsg SBT_SHOP_HAVE_BP, 2
L_ShopListGo:
    ListMenu_AnchorTopLeft 1, 1, 0, 1, SB_W_LIST
    SBCmd SB_OP_SHOP, SB_W_C
    ListMenuShow
    sb_ifeq SB_W_LIST, 0xfff1, L_ShopEnd
    sb_ifeq SB_W_LIST, 0xfffe, L_ShopEnd
    WorkSet SB_W_ARG, SB_W_LIST
    SBCmd SB_OP_WORD, 0
    SBCmd SB_OP_PRICE, SB_W_C
    WordSetNumber 2, SB_W_A, 5
    SBCmd SB_OP_SHOP_IS_BP, SB_W_C
    sb_ifeq SB_W_RES, 1, L_ShopSureBP
    SystemMsg SBT_SHOP_SURE, 2
    VMJump L_ShopSure
L_ShopSureBP:
    SystemMsg SBT_SHOP_SURE_BP, 2
L_ShopSure:
    YesNoWin SB_W_D
    sb_ifne SB_W_D, 0, L_ShopList
    SBCmd SB_OP_HAS_ROOM, 0
    sb_ifeq SB_W_RES, 0, L_ShopFull
    SBCmd SB_OP_SHOP_IS_BP, SB_W_C
    sb_ifeq SB_W_RES, 1, L_ShopPayBP
    MoneyCheck SB_W_RES, SB_W_A
    sb_ifeq SB_W_RES, 0, L_ShopPoor
    MoneySub SB_W_A
    MoneyWinUpdate
    VMJump L_ShopPaid
L_ShopPayBP:
    SBCmd SB_OP_BP_PAY, SB_W_A
    sb_ifeq SB_W_RES, 0, L_ShopPoorBP
L_ShopPaid:
    SBCmd SB_OP_GIVE, 0
    SEPlay SEQ_SE_FLD_05
    SystemMsg SBT_SHOP_THANKS, 2
    LastKeyWait
    VMJump L_ShopList
L_ShopFull:
    SystemMsg SBT_SHOP_FULL, 2
    LastKeyWait
    VMJump L_ShopList
L_ShopPoor:
    SystemMsg SBT_SHOP_MONEY, 2
    LastKeyWait
    VMJump L_ShopList
L_ShopPoorBP:
    SystemMsg SBT_SHOP_BP, 2
    LastKeyWait
    VMJump L_ShopList
L_ShopEnd:
    SBCmd SB_OP_SHOP_IS_BP, SB_W_C
    sb_ifeq SB_W_RES, 1, L_ShopEndBP
    MoneyWinClose
L_ShopEndBP:
    InfoMsgClose
    SBCmd SB_OP_UNLOAD, 0
    RTEndGlobal

// ---- givedecoration: Std_ObtainDecoration -------------------------------------------------------------------------------
Script_Give:
    SBCmd SB_OP_GIVE, 0
    WorkSet SB_W_LIST, SB_W_RES
    SBCmd SB_OP_WORD, 1
    sb_ifeq SB_W_LIST, 0, L_GiveNoRoom
    MEPlay SEQ_ME_ITEM
    SystemMsg SBT_OBTAINED, 2
    MEWait
    LastKeyWait
    SystemMsg SBT_TRANSFERRED, 2
    LastKeyWait
    VMJump L_GiveEnd
L_GiveNoRoom:
    SystemMsg SBT_NO_ROOM, 2
    LastKeyWait
L_GiveEnd:
    InfoMsgClose
    WorkSet SB_W_RES, SB_W_LIST
    SBCmd SB_OP_UNLOAD, 0
    RTEndGlobal

Script_HasRoom:
    SBCmd SB_OP_HAS_ROOM, 0
    SBCmd SB_OP_UNLOAD, 0
    RTEndGlobal
