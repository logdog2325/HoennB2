// Chapter 8 part 8a helpers (ch8a agent, 2026-10-07: Lilycove City and its buildings): macros and script works only
// (no code). Include after "hoenn_story.inc". Builds on ch3a's scenes/ch3_lib.inc (c3_talk, c3_say_turn_back,
// c3_mart_sub, c3_lead_mon; works 0x8032-0x8036).
#ifndef CH8A_LIB_INC
#define CH8A_LIB_INC
#include "scenes/ch3_lib.inc"

// script works of 8a's scripts (0x8030/0x8031 = hoenn_story.inc, 0x8032-0x8036 = ch3_lib.inc)
#define C8_A 0x8037
#define C8_B 0x8038
#define C8_C 0x8039
#define C8_D 0x803A
#define C8_SEL 0x803B
#define C8_E 0x803C
#define C8_F 0x803D
#define C8_G 0x803E
#define C8_H 0x803F

// giveitem VAR (the item is in a work: the Berry gentleman's random Berry, the lottery prize): h_giveitem with the item
// read from the work (WorkSet reads a work; WorkSetConst would store its number). HLIB_RESULT 1 given, 0 Bag full.
    .macro c8_giveitem_var var, count=1
    ItemCheckSpace \var, \count, HLIB_RESULT
    WorkCmpConst HLIB_RESULT, 0
    VMJumpIf CMP_EQ, .Lc8gi\@
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, \var
    WorkSetConst 0x8001, \count
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
.Lc8gi\@:
    .endm

// a whole lockall + MSGBOX_DEFAULT + releaseall script of a person who does not turn to the player
    .macro c8_say_noturn n
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0
    LastKeyWait
    h_release
    .endm

// lock + faceplayer + one line + release (MSGBOX_DEFAULT after lock/faceplayer)
    .macro c8_say n
    c3_talk
    h_msgbox \n
    h_release
    .endm

// the same, branching on a flag: line \nset when the flag is set, else \nunset
    .macro c8_say_if_set flag, nset, nunset
    c3_talk
    h_goto_if_set \flag, .Lc8s\@
    h_msgbox \nunset
    h_release
.Lc8s\@:
    h_msgbox \nset
    h_release
    .endm

// ... and on a badge
    .macro c8_say_if_badge badge, nhas, nnot
    c3_talk
    h_goto_if_badge \badge, .Lc8b\@
    h_msgbox \nnot
    h_release
.Lc8b\@:
    h_msgbox \nhas
    h_release
    .endm

// a Pokémon that cries and says its line (lock, faceplayer, waitse, playmoncry, msgbox, waitmoncry, release)
    .macro c8_mon_cry species, n
    c3_talk
    SEWait
    h_playmoncry \species
    h_msgbox \n
    h_waitmoncry
    h_release
    .endm

// dofieldeffect FLDEFF_NPCFLY_OUT + removeobject (the rival leaving Lilycove): Black 2's unused "Alder flies off" effect
// (ov036 s019D_PlayAlderFlyEffect, FieldCommand 413; ch7 uses it for Steven too), then the object is removed with its
// hide flag. C8_G = the actor's uid.
    .macro c8_npc_fly_out uid, flag
    FadeOutBlack                        // Black 2's only NPC fly-off (ov036 s019D) is its fixed "Alder flies off" cut-in:
    FadeWait                            // the red-haired Alder rides a Braviary across the screen (fixes_v151 test), an
    h_removeobject \uid, \flag           // Unova character in a Hoenn scene, so the leaver fades out instead (lead,
    FadeInBlack                         // 2026-10-08)
    FadeWait
    .endm
#endif
