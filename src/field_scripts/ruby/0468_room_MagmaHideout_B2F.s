// MagmaHideout_B2F (zone 234): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// Messages: src/text/script/ruby/0293_room_MagmaHideout_B2F.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"
#include "hoenn_version.inc"

    ScriptEntry Script_1
    ScriptEntry Story_MH2_Notice        // 2: triggers (4..7,16), VAR_TEMP_1 0 (MagmaHideout_B2F_EventScript_15D8BD)  // story:
    ScriptEntry Story_MH2_Tabitha       // 3: object 1, Tabitha at (8,19) (MagmaHideout_B2F_EventScript_15D8E1)  // story:
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
    .balign 4, 0

// ---- story (ruby_scenes WP2 agent 2026-10-08: pokeruby data/maps/MagmaHideout_B2F/scripts.inc = AquaHideout_B2F's labels
// (the Magma map only repeats them) with every .ifdef SAPPHIRE block read as Ruby; generators keep everything from this line on)
// Not a Groudon scene: Ruby's B2F is the same submarine escape as Sapphire's AquaHideout_B2F (scenes of ch8b in
// 0020_room_AquaHideout_B2F.s), with Tabitha (TRAINER_HIDEOUT_B2F_GRUNT_1 = Black 2's id of TRAINER_MATT_1, which holds
// Tabitha in a Ruby build) and the Magma map's own geometry. Differences to Sapphire's scene (all of them):
//  - Tabitha stands at (8,19) facing right (Sapphire: Matt at (23,19) facing left); the trigger tiles are (4..7,16) (Sapphire (28,16) and (28,17));
//    the notice scene turns her UP to the player (Common_Movement_WalkInPlaceFastestUp; Sapphire: FacePlayer);
//  - after the battle she turns RIGHT (Sapphire: left) and the submarine shadow (object 3, VAR_0x8009; Sapphire object 4) leaves
//    four tiles to the RIGHT (Movement_15D95D; Sapphire walks left): Sapphire's shadow as a 3D object (missing_objects 2026-10-08);
//  - the two grunts (data/story/ruby/ruby_scenes.json: (31,11) walking, sight 3, and (13,3) facing left, sight 4) are eye-contact
//    trainers on the same Black 2 ids as the Aqua ones (scripts 3010 and 3043: TRAINER_GRUNT_4 / _27 hold GRUNT_31 / _54 in Ruby).
// Text: lines 1-2 of src/text/script/ruby/0293_room_MagmaHideout_B2F.txt (the same two lines as 0016_room_AquaHideout_B2F.txt: they
// name no team); Tabitha's intro, defeat and after lines are the trainer table's (converter/gen_trainers.py, WP1).
#include "scenes/ch8b_lib.inc"
#define T_TabithaToying 1
#define T_TabithaBossGone 2
#define MH2_TABITHA 1
#define MH2_SUB 3                       // the submarine shadow (3D object 0x2000, data/story/missing_objects.json)

Story_MH2_Notice:                       // MagmaHideout_B2F_EventScript_15D8BD
    h_lock
    h_applymovement MH2_TABITHA, Mv_MH2_Exclaim
    h_waitmovement
    h_turnobject MH2_TABITHA, 0         // Common_Movement_WalkInPlaceFastestUp (Sapphire: FacePlayer; the player is north of her)
    h_setvar 0x4001, 1                  // VAR_TEMP_1
    h_release

Story_MH2_Tabitha:                      // MagmaHideout_B2F_EventScript_15D8E1
    c8b_talk
    h_goto_if_defeated TRAINER_HIDEOUT_B2F_GRUNT_1, L_MH2_TabithaAfter
    h_trainer_intro TRAINER_HIDEOUT_B2F_GRUNT_1, MH2_TABITHA   // Hehehe... Got here already, did you? We underestimated you! ... I'm going to pulverize you!
    h_trainerbattle TRAINER_HIDEOUT_B2F_GRUNT_1                // (in battle: "Hehehe... So, I lost, too...")
    h_turnobject MH2_TABITHA, 3         // MagmaHideout_B2F_EventScript_15D8FD (VAR_0x8009 3): WalkInPlaceFastestRight
    h_delay 20
    h_faceplayer
    h_msgbox T_TabithaToying            // Hehehe! While I was toying with you, our Boss got through his preparations!
    h_closemessage
    h_turnobject MH2_TABITHA, 3
    h_applymovement MH2_SUB, Mv_MH2_SubLeaves   // the submarine shadow (object 3, VAR_0x8009) leaves four tiles east
    h_waitmovement
    h_removeobject MH2_SUB, FLAG_HIDE_SUBMARINE_SHADOW_HIDEOUT
    h_delay 20
    h_faceplayer
    h_msgbox T_TabithaBossGone          // Hehehe! Our Boss has already gone on his way to some cave under the sea! ...
    h_setflag FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE
    h_setflag FLAG_HIDE_GRUNTS_LILYCOVE
    h_release
L_MH2_TabithaAfter:
    h_msgbox T_TabithaBossGone
    h_release

    .balign 4, 0
Mv_MH2_SubLeaves:                       // MagmaHideout_B2F (AquaHideout_B2F_Movement_15D95D)
    walk_right 4
    step_end
    .balign 4, 0
Mv_MH2_Exclaim:
    emote_exclamation_mark
    step_end
    .balign 4, 0
