// MeteorFalls_1F_2R (zone 129): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// Messages: src/text/script/0148_room_MeteorFalls_1F_2R.txt
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntriesEnd

Script_1:                                      // ladder down (4,14) -> MeteorFalls_B1F_1R warp 0 (5,6)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 130, 5, 1, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (7,20) -> MeteorFalls_B1F_1R warp 1 (7,11)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 130, 7, 2, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // ladder down (21,23) -> MeteorFalls_B1F_1R warp 2 (18,15)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 130, 18, 1, 15, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 0, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
