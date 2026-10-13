// AquaHideout_1F (zone 2): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// furniture messages. Story scripts: add them after a line "// ---- story" (then this generator leaves the file
// alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_None
    ScriptEntry Story_AH1_Grunt1        // 2: object 1, the grunt at (13,11) (Ch8)
    ScriptEntry Story_AH1_Grunt2        // 3: object 2, the grunt at (14,11) (Ch8)
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch8 part 8b, ch8b agent 2026-10-07: Sapphire data/maps/AquaHideout_1F/scripts.inc; generators keep
// everything from this line on)
// The two grunts that block the way in (data/story/ch8b.json uids 1 and 2, hidden by FLAG_HIDE_GRUNT_1/2_BLOCKING_HIDEOUT,
// which the Slateport harbor scene sets) and the grunt at (20,4) (uid 3: eye-contact trainer TRAINER_GRUNT_1, script
// 3004, FLAG_HIDE_GRUNTS_HIDEOUTS). Text lines 1-4 of src/text/script/0005_room_AquaHideout_1F.txt. Sapphire's
// OnTransition (SetupEvilTeamGfxIds) places nothing here.
#include "scenes/ch8b_lib.inc"
#define T_Grunt1Before 1
#define T_Grunt1After 2
#define T_Grunt2Before 3
#define T_Grunt2After 4
#define T_Grunt1Magma 5                 // Emerald only (appended lines of src/text/script/emerald/0005_room_AquaHideout_1F.txt)
#define T_Grunt2Magma 6
// EMERALD (emerald_ch45_magma 2026-10-12; pokeemerald AquaHideout_1F_EventScript_HideoutEntranceGrunt1/2): the entrance guards give
// three hints. Before Mt. Pyre's summit: the Boss is away (Grunt 1) / on Route 122 (Grunt 2). After the old woman's Magma Emblem
// (FLAG_RECEIVED_RED_OR_BLUE_ORB): they ask where Team Magma's Hideout is / mention Mt. Chimney. After Groudon is awake in the
// Magma Hideout (FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT, builder B4): the Boss is in Slateport (Sapphire's "after" lines).
// Sapphire and Ruby switch on FLAG_MT_PYRE_ORB_STOLEN, which Emerald's Mt. Pyre scene does not set.

Story_AH1_Grunt1:                       // AquaHideout_1F_EventScript_15D7CE
    c8b_talk
#ifdef HOENN_EMERALD
    h_goto_if_set FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT, L_AH1_Grunt1After
    h_goto_if_set FLAG_RECEIVED_RED_OR_BLUE_ORB, L_AH1_Grunt1Magma
#else
    h_goto_if_set FLAG_MT_PYRE_ORB_STOLEN, L_AH1_Grunt1After
#endif
    h_msgbox T_Grunt1Before             // What? What? What do you want with Team Aqua? Our Boss isn't here! He's gone off to snatch something important!
    h_release
#ifdef HOENN_EMERALD
L_AH1_Grunt1Magma:
    h_msgbox T_Grunt1Magma              // What? What? Are you a Team Magma grunt? ... But where might their Hideout be?
    h_release
#endif
L_AH1_Grunt1After:
    h_msgbox T_Grunt1After              // ... Our Boss isn't here! He's gone off to jack a submarine!
    h_release

Story_AH1_Grunt2:                       // AquaHideout_1F_EventScript_15D7ED
    c8b_talk
#ifdef HOENN_EMERALD
    h_goto_if_set FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT, L_AH1_Grunt2After
    h_goto_if_set FLAG_RECEIVED_RED_OR_BLUE_ORB, L_AH1_Grunt2Magma
#else
    h_goto_if_set FLAG_MT_PYRE_ORB_STOLEN, L_AH1_Grunt2After
#endif
    h_msgbox T_Grunt2Before             // ... Our Boss isn't here! He's on his way to Mt. Pyre on Route 122!
    h_release
#ifdef HOENN_EMERALD
L_AH1_Grunt2Magma:
    h_msgbox T_Grunt2Magma              // What? What? Are you a Team Magma grunt? ... an awesome Pokémon at Mt. Chimney. But what is that Pokémon like?
    h_release
#endif
L_AH1_Grunt2After:
    h_msgbox T_Grunt2After              // ... Our Boss isn't here! He's on his way to Slateport City!
    h_release
    .balign 4, 0
