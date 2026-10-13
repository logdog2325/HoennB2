// ShoalCave_LowTideStairsRoom (zone 163): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
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
    ScriptEntry SS_Salt3  // 4: sign (11,11) + object  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder up (3,12) -> ShoalCave_LowTideInnerRoom warp 1 (38,15)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 146, 47, 0, 28, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder up (7,4) -> ShoalCave_LowTideInnerRoom warp 2 (42,4)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 146, 51, 4, 17, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // zone init: inside the cave (tide kept)
    MapReplaceSetEvent 8, 1, 0
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch9, ch9 agent 2026-10-07; Sapphire data/maps/ShoalCave_LowTideStairsRoom/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). Script 4, text lines 0-1 of 0221. Salt 3 at Sapphire (11,11): an object (uid 2) and a sign on the tile (data/story/ch9.json). Room tiles = Sapphire tiles.
#include "scenes/ch9_lib.inc"
#define T_NothingSalt 0
#define T_BagFull 1

SS_Salt3:                               // ShoalCave_LowTideStairsRoom_EventScript_15E3B7
    c9_shoal_pickup ITEM_SHOAL_SALT, FLAG_HIDE_TOOK_SHOAL_SALT_3, 2, T_NothingSalt, T_BagFull
    .balign 4, 0
