// AquaHideout_B2F (zone 10): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// Messages: src/text/script/0016_room_AquaHideout_B2F.txt
// furniture messages. Story scripts: add them after a line "// ---- story" (then this generator leaves the file
// alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Story_AH2_MattNotice    // 2: triggers (28,16) and (28,17), VAR_TEMP_1 0 (Ch8)
    ScriptEntry Story_AH2_Matt          // 3: object 1, Matt at (23,19) (Ch8)
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

// ---- story (chapter Ch8 part 8b, ch8b agent 2026-10-07: Sapphire data/maps/AquaHideout_B2F/scripts.inc; generators keep
// everything from this line on)
// Matt (data/story/ch8b.json uid 1, model 88 = Matt's own sheet) notices you at the two trigger tiles, fights you when
// spoken to and then lets the submarine go: FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE and FLAG_HIDE_GRUNTS_LILYCOVE (the five
// cove grunts of Lilycove, ch8a's) are set at the end. The grunts at (23,10) and (10,6) are eye-contact trainers
// (uids 2 and 5: TRAINER_GRUNT_4, _27, scripts 3010, 3043); the submarine shadow (object 4: Sapphire's shadow as a 3D
// object, missing_objects 2026-10-08) leaves four tiles west while Matt looks after it, as Sapphire's Movement_15D958.
// Text lines 1-2 of src/text/script/0016_room_AquaHideout_B2F.txt.
#include "scenes/ch8b_lib.inc"
#define T_MattToying 1
#define T_MattBossGone 2
#define AH2_MATT 1
#define AH2_SUB 4                       // the submarine shadow (3D object 0x2000, data/story/missing_objects.json)

Story_AH2_MattNotice:                   // AquaHideout_B2F_EventScript_15D8BD
    h_lock
    h_applymovement AH2_MATT, Mv_AH2_Exclaim
    h_waitmovement
    h_turnobject AH2_MATT, 3            // Common_Movement_FacePlayer (the player is to the east of him)
    h_setvar 0x4001, 1                  // VAR_TEMP_1
    h_release

Story_AH2_Matt:                         // AquaHideout_B2F_EventScript_15D8E1
    c8b_talk
    h_goto_if_defeated TRAINER_MATT_1, L_AH2_MattAfter
    h_trainer_intro TRAINER_MATT_1, AH2_MATT    // Hehehe... Got here already, did you? We underestimated you! ... I'm going to pulverize you!
    h_trainerbattle TRAINER_MATT_1              // (in battle: "Hehehe... So, I lost, too...")
    h_turnobject AH2_MATT, 2                    // AquaHideout_B2F_EventScript_15D8FD
    h_delay 20
    h_faceplayer
    h_msgbox T_MattToying               // Hehehe! While I was toying with you, our Boss got through his preparations!
    h_closemessage
    h_turnobject AH2_MATT, 2
    h_applymovement AH2_SUB, Mv_AH2_SubLeaves   // the submarine shadow (object 4, VAR_0x8009) leaves four tiles west
    h_waitmovement
    h_removeobject AH2_SUB, FLAG_HIDE_SUBMARINE_SHADOW_HIDEOUT
    h_delay 20
    h_faceplayer
    h_msgbox T_MattBossGone             // Hehehe! Our Boss has already gone on his way to some cave under the sea! ...
    h_setflag FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE
    h_setflag FLAG_HIDE_GRUNTS_LILYCOVE
    h_release
L_AH2_MattAfter:
    h_msgbox T_MattBossGone
    h_release

    .balign 4, 0
Mv_AH2_SubLeaves:                       // AquaHideout_B2F_Movement_15D958
    walk_left 4
    step_end
    .balign 4, 0
Mv_AH2_Exclaim:
    emote_exclamation_mark
    step_end
    .balign 4, 0
