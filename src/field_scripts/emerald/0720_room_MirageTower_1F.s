// MirageTower_1F (zone 360, Emerald): converter/gen_caves_emerald.py from emerald/MirageTower_1F (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"  // emerald_ch9_mirage

    ScriptEntry Script_1
    ScriptEntry MT1_Init  // 2: zone init (MirageTower_1F_OnTransition)  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder up (15,2) -> MirageTower_2F warp 1 (15,2)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 361, 15, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (builder B6 emerald_ch9_mirage 2026-10-12; pokeemerald data/maps/MirageTower_1F/scripts.inc; generators keep everything from this line on;
// entries above marked "// story:"). Zone init = script 2 (0721 init): pokeemerald's OnTransition sets FLAG_ENTERED_MIRAGE_TOWER, FLAG_FORCE_MIRAGE_TOWER_VISIBLE
// (Route 111 shows the tower on every visit from now on, until Route 112's zone init clears it) and FLAG_LANDMARK_MIRAGE_TOWER (the Pokédex's area page: no
// such flag here, nothing reads it). Scripts of the upper floors: 0726 (the fossils and the collapse).
MT1_Init:                               // MirageTower_1F_OnTransition
    h_setflag FLAG_FORCE_MIRAGE_TOWER_VISIBLE
    VMHalt
    .balign 4, 0
