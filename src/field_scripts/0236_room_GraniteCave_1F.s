// GraniteCave_1F (zone 118): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"
// Story (chapter Ch2, Sapphire data/maps/GraniteCave_1F/scripts.inc) after the "// ---- story" line: script 3 (the
// hiker, uid 1 in data/story/ch2.json), text 0137 lines 0-1.

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry GC1_Hiker           // 3: GraniteCave_1F_EventScript_15CBA7 (HM05 Flash)
    ScriptEntriesEnd

Script_1:                                      // ladder down (35,3) -> GraniteCave_B1F warp 0 (25,13)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 124, 25, 0, 13, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (17,11) -> GraniteCave_B1F warp 1 (4,21)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 124, 4, 0, 21, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story

GC1_Hiker:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_HM05, L_GC1_HikerAgain
    h_msgbox 0                      // Hey, you. It gets awfully dark ahead. ...Steven... knew how to use Flash...
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_TM70            // Sapphire's HM05 Flash = Black 2's Flash TM70 (notes/RESEARCH_EXPSHARE_HM.md)
    h_setflag FLAG_RECEIVED_HM05
L_GC1_HikerAgain:
    h_msgbox 1                      // Teach that hidden move Flash to a Pokémon and use it. ...
    h_release
    .balign 4, 0
