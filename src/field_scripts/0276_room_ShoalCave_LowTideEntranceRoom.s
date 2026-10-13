// ShoalCave_LowTideEntranceRoom (zone 138): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch9
#include "hoenn_key_items.h"  // ch9
#include "hoenn_story.inc"  // ch9

    ScriptEntry Script_1
    ScriptEntry SE_OldMan  // 2: object 2 (the old man)  // story:
    ScriptEntriesEnd

Script_1:                                      // zone init: the tide (Sapphire UpdateShoalTideFlag)
    MapReplaceIsEventSet 8, 0x8002
    MapReplaceSetEvent 8, 0, 0
    WorkCmpConst 0x8002, 1
    VMJumpIf CMP_EQ, L_TideKept
    RTCGetTime 0x8000, 0x8001
    WorkCmpConst 0x8000, 3
    VMJumpIf CMP_LT, L_TideHigh
    WorkCmpConst 0x8000, 9
    VMJumpIf CMP_LT, L_TideLow
    WorkCmpConst 0x8000, 15
    VMJumpIf CMP_LT, L_TideHigh
    WorkCmpConst 0x8000, 21
    VMJumpIf CMP_LT, L_TideLow
L_TideHigh:
    FlagSet FLAG_SYS_SHOAL_TIDE
    MapReplaceSetEvent 9, 1, 1
    VMJump L_TideKept
L_TideLow:
    FlagReset FLAG_SYS_SHOAL_TIDE
    MapReplaceSetEvent 9, 0, 1
L_TideKept:
    MapReplaceIsEventSet 9, 0x8002
    WorkCmpConst 0x8002, 0
    VMJumpIf CMP_EQ, L_TideDone
    ObjInitWarpGPos 1, 0, 0, 0
L_TideDone:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch9, ch9 agent 2026-10-07; Sapphire data/maps/ShoalCave_LowTideEntranceRoom/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). Script 2, text lines 0-7 of 0157. The old man (uid 2, (18,15))
// is in data/story/ch9.json. The tide (OnTransition) is the generator's script 1.
// Shoal Salt and Shoal Shells come back every day: Sapphire's FLAG_SYS_SHOAL_ITEM is SET by each new day (SetShoalItemFlag)
// and the old man's script (dotimebasedevents) clears it and the 8 FLAG_HIDE_TOOK_SHOAL_*. Black 2 clears the flags of
// 2720-2819 at midnight, so the flag is turned round: FLAG_DAILY_SHOAL_ITEMS_RESET CLEAR = a new day = reset now.
#include "scenes/ch9_lib.inc"
#define T_Planning 0
#define T_BringFour 1
#define T_OhHey 2
#define T_AllRighty 3
#define T_HaveAPokemonHold 4
#define T_OhIsThatSo 5
#define T_NoSpace 6
#define T_BagFull 7

SE_OldMan:                              // ShoalCave_LowTideEntranceRoom_EventScript_15E076
    c9_talk
    h_call_if_unset FLAG_DAILY_SHOAL_ITEMS_RESET, SE_ResetShoalItems     // call_if_set FLAG_SYS_SHOAL_ITEM, ..._EventScript_15E176
    h_checkitem ITEM_SHOAL_SALT, 4, C9_A
    h_goto_if_eq C9_A, 0, L_SE_NotEnough
    h_checkitem ITEM_SHOAL_SHELL, 4, C9_A
    h_goto_if_eq C9_A, 0, L_SE_NotEnough
    h_yesno T_OhHey, C9_B               // Oh, hey! Shoal Salt and Shoal Shells! And enough of them, too! ...
    h_goto_if_no C9_B, L_SE_Declined
    h_checkitemspace ITEM_SHELL_BELL, 1, C9_A
    h_goto_if_ne C9_A, 0, L_SE_Fits
    h_checkitem ITEM_SHOAL_SALT, 5, C9_A    // ..._EventScript_15E106: no room for the Shell Bell. With only 4 of the Salt (or the
    h_goto_if_eq C9_A, 0, L_SE_Fits         // Shells) the trade frees that slot; with 5 or more of both it frees none
    h_checkitem ITEM_SHOAL_SHELL, 5, C9_A
    h_goto_if_eq C9_A, 0, L_SE_Fits
    VMJump L_SE_NoSpace
L_SE_Fits:
    h_msgbox T_AllRighty                // All righty, then! I'll make you a Shell Bell right away. ... There! Done!
    h_removeitem ITEM_SHOAL_SALT, 4, HLIB_TMP
    h_removeitem ITEM_SHOAL_SHELL, 4, HLIB_TMP
    h_closemessage                      // (Black 2: the item script opens its own window)
    h_giveitem ITEM_SHELL_BELL
    h_goto_if_eq HLIB_RESULT, 0, L_SE_BagFull
    h_msgbox T_HaveAPokemonHold         // Have a Pokémon hold on to that. It'll love it, that's for certain. ...
    h_release
L_SE_NoSpace:                           // ..._EventScript_15E12E
    h_msgbox T_NoSpace                  // You don't have space in your Bag if I were to make it for you. ...
    h_release
L_SE_NotEnough:                         // ..._EventScript_15E138
    h_checkitem ITEM_SHOAL_SALT, 1, C9_A
    h_goto_if_eq C9_A, 1, L_SE_BringFour
    h_checkitem ITEM_SHOAL_SHELL, 1, C9_A
    h_goto_if_eq C9_A, 1, L_SE_BringFour
    h_msgbox T_Planning                 // Are you planning on going deep in there? How about bringing me back some Shoal Salt and Shoal Shells? ...
    h_release
L_SE_BringFour:                         // ..._EventScript_15E162
    h_msgbox T_BringFour                // If you bring me four each of the Shoal Salt and Shoal Shells, I can make you a Shell Bell... ...
    h_release
L_SE_Declined:                          // ..._EventScript_15E16C
    h_msgbox T_OhIsThatSo               // Oh... Is that so... I wanted to make a Shell Bell...
    h_release
L_SE_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release

SE_ResetShoalItems:                     // ..._EventScript_15E176
    h_setflag FLAG_DAILY_SHOAL_ITEMS_RESET
    h_clearflag FLAG_HIDE_TOOK_SHOAL_SALT_1
    h_clearflag FLAG_HIDE_TOOK_SHOAL_SALT_2
    h_clearflag FLAG_HIDE_TOOK_SHOAL_SALT_3
    h_clearflag FLAG_HIDE_TOOK_SHOAL_SALT_4
    h_clearflag FLAG_HIDE_TOOK_SHOAL_SHELL_1
    h_clearflag FLAG_HIDE_TOOK_SHOAL_SHELL_2
    h_clearflag FLAG_HIDE_TOOK_SHOAL_SHELL_3
    h_clearflag FLAG_HIDE_TOOK_SHOAL_SHELL_4
    VMReturn
    .balign 4, 0
