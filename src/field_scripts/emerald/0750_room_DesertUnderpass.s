// DesertUnderpass (zone 375, Emerald): converter/gen_caves_emerald.py from emerald/DesertUnderpass (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_key_items.h"  // emerald_ch9_mirage
#include "hoenn_story.inc"  // emerald_ch9_mirage

    ScriptEntry Script_None
    ScriptEntry DU_Fossil  // 2: object 1, the fossil (DesertUnderpass_EventScript_Fossil)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (builder B6 emerald_ch9_mirage 2026-10-12; pokeemerald data/maps/DesertUnderpass/scripts.inc; generators keep everything from this line on; entries above
// marked "// story:"). The fossil at the far east end (data/story/emerald/e_ch9_mirage.json, uid 1, hidden by FLAG_HIDE_DESERT_UNDERPASS_FOSSIL: new-game flag, cleared by the
// Mirage Tower's collapse scene on Route 111) is the one you did not take there: the Claw Fossil after the Root Fossil, the Root Fossil after the Claw Fossil. Text
// (0587): the bag-full line only (pokeemerald gives it without looking at the bag; here a full bag leaves the fossil).
#define T_BagFull 0
#define DU_FOSSIL 1

DU_Fossil:                              // DesertUnderpass_EventScript_Fossil (lock, faceplayer)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    h_goto_if_set FLAG_CHOSE_ROOT_FOSSIL, L_DU_GiveClaw
    h_goto_if_set FLAG_CHOSE_CLAW_FOSSIL, L_DU_GiveRoot
    h_release
L_DU_GiveClaw:                          // DesertUnderpass_EventScript_GiveClawFossil
    h_giveitem ITEM_CLAW_FOSSIL
    h_goto_if_eq HLIB_RESULT, 0, L_DU_BagFull
    h_removeobject DU_FOSSIL, FLAG_HIDE_DESERT_UNDERPASS_FOSSIL
    h_release
L_DU_GiveRoot:                          // DesertUnderpass_EventScript_GiveRootFossil
    h_giveitem ITEM_ROOT_FOSSIL
    h_goto_if_eq HLIB_RESULT, 0, L_DU_BagFull
    h_removeobject DU_FOSSIL, FLAG_HIDE_DESERT_UNDERPASS_FOSSIL
    h_release
L_DU_BagFull:
    h_bag_is_full T_BagFull
    h_release
    .balign 4, 0
