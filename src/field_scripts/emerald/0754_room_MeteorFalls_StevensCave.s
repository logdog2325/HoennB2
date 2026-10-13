// MeteorFalls_StevensCave (zone 377, Emerald): converter/gen_caves_emerald.py from emerald/MeteorFalls_StevensCave (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // emerald_ch12_13
#include "hoenn_story.inc"  // emerald_ch12_13
#include "hoenn_version.inc"  // emerald_ch12_13: TRAINER_STEVEN_EMERALD

    ScriptEntry Script_None
    ScriptEntry SC_Steven  // 2: object 1, Steven (MeteorFalls_StevensCave_EventScript_Steven)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (Ch13 post-game, builder B8 emerald_ch12_13 2026-10-12; pokeemerald data/maps/MeteorFalls_StevensCave/scripts.inc;
// generators keep everything from this line on; entries above marked "// story:"). Messages: src/text/script/emerald/
// 0589_room_MeteorFalls_StevensCave.txt. Steven (data/story/emerald/e_ch13.json uid 1, pokeemerald (19,3), FACE_UP, Black 2's
// Steven model 287) is Emerald's post-game boss: TRAINER_STEVEN (#804) = TRAINER_STEVEN_EMERALD here (Black 2 id 607, Emerald's
// party at levels on the curve, emerald_data). Emerald's rule: beaten once, he only talks afterwards (FLAG_DEFEATED_METEOR_FALLS_STEVEN,
// set after the win); lost = Black 2's whiteout, the battle is there again next time (no rematches: decision 3A, Emerald has
// none for him either). The cave opens after the game (Meteor Falls 1F's rock, emerald_caves).
#define T_ShouldKnowHowGoodIAm 0        // MeteorFalls_StevensCave_Text_ShouldKnowHowGoodIAmExpectWorst
#define T_MyPredictionCameTrue 1        // MeteorFalls_StevensCave_Text_MyPredictionCameTrue
#define SC_STEVEN 1                     // LOCALID_METEOR_FALLS_STEVEN

SC_Steven:                              // MeteorFalls_StevensCave_EventScript_Steven
    h_lock
    h_goto_if_set FLAG_DEFEATED_METEOR_FALLS_STEVEN, L_SC_Defeated
    h_waitse
    h_applymovement SC_STEVEN, Common_Movement_ExclamationMark   // playse SE_PIN + "!" (the "!" plays its own)
    h_waitmovement
    h_applymovement SC_STEVEN, Common_Movement_Delay48
    h_waitmovement
    h_faceplayer                        // Common_Movement_FacePlayer
    h_buffer_player
    h_msgbox T_ShouldKnowHowGoodIAm     // Steven: Oh, wow, <player>. I'm amazed you knew where to find me. ... expect the worst!
    h_closemessage
    h_trainerbattle TRAINER_STEVEN_EMERALD   // trainerbattle_no_intro (in battle: "You... I had no idea you'd become so strong...")
    h_msgbox T_MyPredictionCameTrue     // Steven: Come to think of it, ever since our paths first crossed ... couldn't tell you that.
    h_setflag FLAG_DEFEATED_METEOR_FALLS_STEVEN
    h_release
L_SC_Defeated:                          // MeteorFalls_StevensCave_EventScript_Defeated
    h_faceplayer
    h_msgbox T_MyPredictionCameTrue
    h_release
    .balign 4, 0
#include "common/movement.inc"
