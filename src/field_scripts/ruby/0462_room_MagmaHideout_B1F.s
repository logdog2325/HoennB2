// MagmaHideout_B1F (zone 231): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// Messages: src/text/script/ruby/0290_room_MagmaHideout_B1F.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Story_MH1B_Electrode1   // 3: object 6, the Electrode at (27,10) disguised as an item (Hideout_B1F_EventScript_Electrode1)
    ScriptEntry Story_MH1B_Electrode2   // 4: object 8, the Electrode at (27,11) (Hideout_B1F_EventScript_Electrode2)
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 0, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 1, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (ruby_maps WP3 agent 2026-10-08: pokeruby data/maps/MagmaHideout_B1F (map.json + scripts.inc) and
// data/scripts/static_pokemon.inc; generators keep everything from this line on). As Sapphire's 0010_room_AquaHideout_B1F.s
// (ch8b) with the Magma map's objects (data/story/ruby/ruby_maps.json): the two Electrodes that look like item balls at
// (27,10)/(27,11) (uids 6 and 8, hidden by FLAG_HIDE_ELECTRODE_1/2_HIDEOUT) and the three grunts (uids 1, 2, 3: eye-contact
// trainers TRAINER_HIDEOUT_B1F_GRUNT_1/2/3 = scripts 3005, 3006, 3042, the Black 2 ids that hold GRUNT_29/30/53 in a Ruby
// build; pokeruby gives them no hide flag). The three real item balls (26,10) Master Ball, (26,11) Nugget, (14,18) Max Elixir
// are the room generator's (data/interiors/ruby/231.json). No text lines. Sapphire's ON_RESUME (removeobject VAR_LAST_TALKED
// when FLAG_SYS_CTRL_OBJ_DELETE) is h_static_battle's own ActorDelete.
#include "scenes/ch8b_lib.inc"
#define MH1B_ELECTRODE1 6
#define MH1B_ELECTRODE2 8
#define MH1B_ELECTRODE_LEVEL 32             // Gen 3's 30 on the scaled curve (data/level_scaling.json; user decision
                                        //   2026-10-19: the static battles follow the curve)

Story_MH1B_Electrode1:                  // Hideout_B1F_EventScript_Electrode1
    c8b_talk
    h_playmoncry SPECIES_ELECTRODE      // setwildbattle ELECTRODE 30; waitse; playmoncry; delay 40; waitmoncry
    h_delay 40
    h_waitmoncry
    h_static_battle SPECIES_ELECTRODE, MH1B_ELECTRODE_LEVEL, FLAG_HIDE_ELECTRODE_1_HIDEOUT, MH1B_ELECTRODE1
    h_release

Story_MH1B_Electrode2:                  // Hideout_B1F_EventScript_Electrode2
    c8b_talk
    h_playmoncry SPECIES_ELECTRODE
    h_delay 40
    h_waitmoncry
    h_static_battle SPECIES_ELECTRODE, MH1B_ELECTRODE_LEVEL, FLAG_HIDE_ELECTRODE_2_HIDEOUT, MH1B_ELECTRODE2
    h_release
    .balign 4, 0
