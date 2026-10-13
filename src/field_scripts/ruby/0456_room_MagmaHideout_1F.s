// MagmaHideout_1F (zone 228): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_None
    ScriptEntry Story_MH1_Grunt1        // 2: object 1, the grunt at (13,19) (MagmaHideout_1F_EventScript_15D7CE)
    ScriptEntry Story_MH1_Grunt2        // 3: object 2, the grunt at (14,19) (MagmaHideout_1F_EventScript_15D7ED)
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (ruby_maps WP3 agent 2026-10-08: pokeruby data/maps/MagmaHideout_1F (map.json + scripts.inc, whose labels are
// AquaHideout_1F's: the Magma map only repeats them); generators keep everything from this line on). The same scenes as
// Sapphire's 0004_room_AquaHideout_1F.s (ch8b) with the Magma map's own objects (data/story/ruby/ruby_maps.json):
// the two grunts blocking the way in at (13,19)/(14,19) (uids 1/2, FLAG_HIDE_GRUNT_1/2_BLOCKING_HIDEOUT, set by the Slateport
// harbor scene) and the grunt at (20,3) (uid 3: eye-contact trainer, script 3004 = TRAINER_HIDEOUT_1F_GRUNT, whose Black 2 id
// holds GRUNT_28 in a Ruby build; pokeruby gives him no hide flag). Text lines 1-4 of
// src/text/script/ruby/0287_room_MagmaHideout_1F.txt ("Team Magma": pokeruby's {EVIL_TEAM} read as Ruby).
// Sapphire's OnTransition (SetupEvilTeamGfxIds) places nothing: the grunts' sprite code 293 shows Magma art in Ruby.
#include "scenes/ch8b_lib.inc"
#define T_Grunt1Before 1
#define T_Grunt1After 2
#define T_Grunt2Before 3
#define T_Grunt2After 4

Story_MH1_Grunt1:                       // MagmaHideout_1F_EventScript_15D7CE (= AquaHideout_1F_EventScript_15D7CE)
    c8b_talk
    h_goto_if_set FLAG_MT_PYRE_ORB_STOLEN, L_MH1_Grunt1After
    h_msgbox T_Grunt1Before             // What? What? What do you want with Team Magma? Our Boss isn't here! He's gone off to snatch something important!
    h_release
L_MH1_Grunt1After:
    h_msgbox T_Grunt1After              // ... Our Boss isn't here! He's gone off to jack a submarine!
    h_release

Story_MH1_Grunt2:                       // MagmaHideout_1F_EventScript_15D7ED
    c8b_talk
    h_goto_if_set FLAG_MT_PYRE_ORB_STOLEN, L_MH1_Grunt2After
    h_msgbox T_Grunt2Before             // ... Our Boss isn't here! He's on his way to Mt. Pyre on Route 122!
    h_release
L_MH1_Grunt2After:
    h_msgbox T_Grunt2After              // ... Our Boss isn't here! He's on his way to Slateport City!
    h_release
    .balign 4, 0
