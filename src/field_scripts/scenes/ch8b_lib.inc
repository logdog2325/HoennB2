// Chapter 8 part 8b helpers (ch8b, 2026-10-07): macros and works only (no code until used). Include after
// "hoenn_story.inc".
#ifndef CH8B_LIB_INC
#define CH8B_LIB_INC
#include "hoenn_key_items.h"

// script works (HLIB_TMP/HLIB_RESULT are 0x8030/0x8031, other chapters' helpers use 0x8032-0x803C and are not combined
// with these in one script)
#define C8B_A 0x8037
#define C8B_B 0x8038
#define C8B_C 0x8039
#define C8B_POS 0x803A                  // Sapphire VAR_0x8008 of the trigger scenes (which trigger tile)
#define C8B_SEL 0x803B

#define TYPE_GRASS 11                   // Black 2's type numbers (include/constants/types.h; Gen 3's are not the same)

// lock + faceplayer of a talked-to person, as Black 2's NPC scripts start (ActorsPauseAll, talk sound, face)
    .macro c8b_talk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    .endm

// msgbox X, MSGBOX_SIGN said by an object (the grunts, a statue): lockall, the line, releaseall
    .macro c8b_obj_sign n
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm

// special IsGrassTypeInParty: var = 1 when a non-Egg party Pokémon has the Grass type (Sapphire: field_specials.c)
    .macro c8b_is_grass_in_party var
    WorkSetConst \var, 0
    PokePartyGetCount C8B_B, 0
    WorkSetConst C8B_A, 0
.Lc8g_loop\@:
    WorkCmpWork C8B_A, C8B_B
    VMJumpIf CMP_GE, .Lc8g_end\@
    PokePartyIsEgg HLIB_TMP, C8B_A
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_NE, .Lc8g_next\@
    WorkSetConst C8B_C, 0
    WorkSetConst C8B_SEL, 0
    PokePartyGetTypes C8B_C, C8B_SEL, C8B_A
    WorkCmpConst C8B_C, TYPE_GRASS
    VMJumpIf CMP_EQ, .Lc8g_yes\@
    WorkCmpConst C8B_SEL, TYPE_GRASS
    VMJumpIf CMP_EQ, .Lc8g_yes\@
.Lc8g_next\@:
    WorkAdd C8B_A, 1
    VMJump .Lc8g_loop\@
.Lc8g_yes\@:
    WorkSetConst \var, 1
.Lc8g_end\@:
    .endm

// giveitem VAR_RESULT (the item id in a work): HLIB_RESULT 1 given, 0 no room (h_giveitem takes a constant only)
    .macro c8b_giveitem_var var
    ItemCheckSpace \var, 1, HLIB_RESULT
    WorkCmpConst HLIB_RESULT, 0
    VMJumpIf CMP_EQ, .Lc8giv\@
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, \var
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
.Lc8giv\@:
    .endm

// Common_EventScript_ShowEasyChatScreen: Black 2's word picker (the quiz's, zone 0234: CallPhraseSelect 4 between
// FieldClose and FieldOpen; user decision 2026-10-07). ok = 1 when two words were picked (Sapphire's VAR_RESULT 1),
// w1/w2 = the two word ids.
    .macro c8b_phrase ok, w1, w2
    MsgWinCloseAll
    FadeOutBlackQ
    FadeWait
    FieldClose
    CallPhraseSelect 4, \w1, \w2, \ok
    FieldOpen
    FadeInBlackQ
    FadeWait
    .endm

// special ExitSafariMode: Black 2 has no Safari mode, so the game ends by taking back every Safari Ball left in the Bag
// (they were handed out at the entrance as the Safari Game's balls)
    .macro c8b_take_safari_balls
    ItemGetCount ITEM_SAFARI_BALL, C8B_A
    WorkCmpConst C8B_A, 0
    VMJumpIf CMP_EQ, .Lc8tb\@
    ItemSub ITEM_SAFARI_BALL, C8B_A, C8B_B
.Lc8tb\@:
    .endm
#endif
