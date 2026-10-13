// Route 112's story (Sapphire data/maps/Route112/scripts.inc; chapter Ch4, ch4 agent 2026-10-07). Scripts 1-3 of the
// zone's generated script file (zone 374); the generated signs/people follow. Text: src/text/scenes/Route112.txt.
// The two Aqua grunts blocking the Cable Car (hidden by FLAG_HIDE_GRUNTS_BLOCKING_CABLE_CAR once Team Aqua leaves
// Meteor Falls): data/story/ch4.json uids 101/106. Map scripts: scenes/Route112_init.inc. The Cable Car station
// (room 555) is chapter Ch5's (ch5 agent).
#ifdef SCENE_ENTRIES
    ScriptEntry R112_Init                   // 1: Route112_OnTransition (zone init)
    ScriptEntry R112_Grunt1                 // 2: object 1
    ScriptEntry R112_Grunt2                 // 3: object 6
#else
#define T_GruntLate 0           // Route112_Text_16FDF0
#define T_GruntCableCar 1       // Route112_Text_16FE3E

R112_Init:                                  // Route112_MapScript1_150508 (SetupEvilTeamGfxIds: the Aqua models are placed)
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
    h_setvar VAR_JAGGED_PASS_ASH_WEATHER, 0
#ifdef HOENN_EMERALD
    h_clearflag FLAG_FORCE_MIRAGE_TOWER_VISIBLE     // Emerald's OnTransition also clears it: the Mirage Tower shows only on some visits again (scenes/emerald/Route111_Mirage.inc)
#endif
    VMHalt
R112_Grunt1:                                // Route112_EventScript_150513
#ifdef HOENN_EMERALD
    VMJump R112_MagmaTalk                   // Emerald: both grunts run the same script (Route112_EventScript_MagmaGrunts)
#else
    h_msgbox_npc T_GruntLate
#endif
R112_Grunt2:                                // Route112_EventScript_15051C
#ifdef HOENN_EMERALD
    VMJump R112_MagmaTalk
#else
    h_msgbox_npc T_GruntCableCar
#endif
#ifdef HOENN_EMERALD
// EMERALD (emerald_ch45_magma 2026-10-12; pokeemerald Route112_EventScript_MagmaGrunts, lockall): talking to either Magma
// grunt makes the two of them talk to each other, one line each, turning to face the other (uid 101 = LOCALID_ROUTE112_GRUNT_1
// at (26,30), 106 = GRUNT_2 at (27,30); both face up again after each line). The models are Magma's (data/story/ch4.json
// "model_emerald"), the four lines Emerald's (src/text/scenes/emerald/Route112.txt T_* above, the file's lines 0-3).
#define R112_GRUNT_1 101
#define R112_GRUNT_2 106
#define T_LeaderAwaken 0
#define T_NeedMeteorite 1
#define T_CrewToFallarbor 2
#define T_CantLetAnyonePass 3
R112_MagmaTalk:
    h_lock
    h_delay 40
    h_applymovement R112_GRUNT_1, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 20
    h_msgbox_actor T_LeaderAwaken, R112_GRUNT_1     // Hey, man, is our leader really going to awaken that thing?
    h_closemessage
    h_turnobject R112_GRUNT_1, 0                    // Common_Movement_FaceOriginalDirection
    h_delay 40
    h_applymovement R112_GRUNT_2, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_delay 20
    h_msgbox_actor T_NeedMeteorite, R112_GRUNT_2    // Sounds like it, yeah. But I heard we need a Meteorite to do it.
    h_closemessage
    h_turnobject R112_GRUNT_2, 0
    h_delay 40
    h_applymovement R112_GRUNT_1, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 20
    h_msgbox_actor T_CrewToFallarbor, R112_GRUNT_1  // Oh, I get it now. That's why the rest of the crew went out to Fallarbor.
    h_closemessage
    h_turnobject R112_GRUNT_1, 0
    h_delay 40
    h_applymovement R112_GRUNT_2, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_delay 20
    h_msgbox_actor T_CantLetAnyonePass, R112_GRUNT_2    // You got it. And until they come back, we're not to let anyone pass, right.
    h_closemessage
    h_turnobject R112_GRUNT_2, 0
    h_release
#endif
    .balign 4, 0
#ifdef HOENN_EMERALD
#include "common/movement.inc"
#endif
#endif
