// ArtisanCave_B1F (zone 373, Emerald): converter/gen_caves_emerald.py from emerald/ArtisanCave_B1F (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntriesEnd

Script_1:                                      // ladder up (38,5) -> ArtisanCave_1F warp 1 (6,5)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 372, 6, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
