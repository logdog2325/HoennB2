// AquaHideout_B1F (zone 5): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// Messages: src/text/script/0008_room_AquaHideout_B1F.txt
// furniture messages. Story scripts: add them after a line "// ---- story" (then this generator leaves the file
// alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Story_AH1B_Electrode1   // 3: object 6, the Electrode at (16,9) disguised as an item (Ch8)
    ScriptEntry Story_AH1B_Electrode2   // 4: object 8, the Electrode at (16,10) (Ch8)
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

// ---- story (chapter Ch8 part 8b, ch8b agent 2026-10-07: Sapphire data/maps/AquaHideout_B1F/scripts.inc +
// data/scripts/static_pokemon.inc; generators keep everything from this line on)
// The two Electrodes that look like item balls (data/story/ch8b.json uids 6 and 8, item-ball model, hidden by
// FLAG_HIDE_ELECTRODE_1/2_HIDEOUT) and the three grunts (uids 1, 2, 4: eye-contact trainers TRAINER_GRUNT_2, _3, _26,
// scripts 3005, 3006, 3042, FLAG_HIDE_GRUNTS_HIDEOUTS). No text lines. Sapphire's ON_RESUME (removeobject
// VAR_LAST_TALKED when FLAG_SYS_CTRL_OBJ_DELETE) is h_static_battle's own ActorDelete; OnTransition places nothing.
#include "scenes/ch8b_lib.inc"
#define AH1B_ELECTRODE1 6
#define AH1B_ELECTRODE2 8

Story_AH1B_Electrode1:                  // Hideout_B1F_EventScript_Electrode1
    c8b_talk
    h_playmoncry SPECIES_ELECTRODE      // setwildbattle ELECTRODE 30; waitse; playmoncry; delay 40; waitmoncry
    h_delay 40
    h_waitmoncry
    h_static_battle SPECIES_ELECTRODE, 30, FLAG_HIDE_ELECTRODE_1_HIDEOUT, AH1B_ELECTRODE1
    h_release

Story_AH1B_Electrode2:                  // Hideout_B1F_EventScript_Electrode2
    c8b_talk
    h_playmoncry SPECIES_ELECTRODE
    h_delay 40
    h_waitmoncry
    h_static_battle SPECIES_ELECTRODE, 30, FLAG_HIDE_ELECTRODE_2_HIDEOUT, AH1B_ELECTRODE2
    h_release
    .balign 4, 0
