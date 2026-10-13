// ShoalCave_LowTideLowerRoom (zone 162): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch9
#include "hoenn_key_items.h"  // ch9
#include "hoenn_story.inc"  // ch9

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry SL_Salt4  // 4: sign (18,2) + object  // story:
    ScriptEntry SL_BlackBelt  // 5: object 2 (the Black Belt)  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder up (7,2) -> ShoalCave_LowTideInnerRoom warp 3 (19,14)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 146, 28, 3, 27, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (28,11) -> ShoalCave_LowTideIceRoom warp 0 (17,10)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 139, 17, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // zone init: inside the cave (tide kept)
    MapReplaceSetEvent 8, 1, 0
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch9, ch9 agent 2026-10-07; Sapphire data/maps/ShoalCave_LowTideLowerRoom/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). Scripts 4-5, text lines 0-3 of 0220. Salt 4 at Sapphire (18,2)
// (an object uid 3 and a sign on the tile) and the Black Belt (uid 2, (11,4)) are in data/story/ch9.json.
#include "scenes/ch9_lib.inc"
#define T_NothingSalt 0
#define T_FocusBand 1
#define T_Everything 2
#define T_BagFull 3

SL_Salt4:                               // ShoalCave_LowTideLowerRoom_EventScript_15E413
    c9_shoal_pickup ITEM_SHOAL_SALT, FLAG_HIDE_TOOK_SHOAL_SALT_4, 3, T_NothingSalt, T_BagFull

SL_BlackBelt:                           // ShoalCave_LowTideLowerRoom_EventScript_15E44F
    c9_talk
    h_goto_if_set FLAG_RECEIVED_FOCUS_BAND, L_SL_ReceivedFocusBand
    h_msgbox T_FocusBand                // The penetrating cold around these parts is an impediment to training. ...
    h_closemessage                      // (Black 2: the item script opens its own window)
    h_giveitem ITEM_FOCUS_BAND
    h_goto_if_eq HLIB_RESULT, 0, L_SL_BagFull
    h_setflag FLAG_RECEIVED_FOCUS_BAND
    h_release
L_SL_ReceivedFocusBand:
    h_msgbox T_Everything               // Everything starts with focus!
    h_release
L_SL_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release
    .balign 4, 0
