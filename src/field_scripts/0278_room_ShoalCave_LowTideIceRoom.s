// ShoalCave_LowTideIceRoom (zone 139): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntriesEnd

Script_1:                                      // ladder up (17,10) -> ShoalCave_LowTideLowerRoom warp 3 (28,11)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 162, 28, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // zone init: inside the cave (tide kept)
    MapReplaceSetEvent 8, 1, 0
    VMHalt
    .balign 4, 0
