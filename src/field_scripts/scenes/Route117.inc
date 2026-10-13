// Route 117's story (Sapphire data/maps/Route117/scripts.inc and data/scripts/day_care.inc; chapter Ch3 part 3b, ch3b
// agent 2026-10-07): the Day-Care Man. converter/gen_map_content.py includes this file twice in the generated zone file
// of Route 117 (zone 437): the entry below is script 1, the generated signs/people follow. Text:
// src/text/scenes/Route117.txt (lines T_* below). His object and the three Day Care Pokémon: data/story/ch3b.json
// (uid = 100 + Sapphire local id; zone 437 given directly: their tiles lie in Mauville's matrix cell, which the banner
// code patch gives to Route 117, world.json "zone_rects"). The cut tree (uid 115) runs Black 2's global Cut script.
// No map scripts: Sapphire's Route117_MapScript1_150D40 (ON_TRANSITION) moves the Day-Care Man to the fence, (47,6),
// while an Egg waits (FLAG_PENDING_DAYCARE_EGG). Black 2 keeps the Egg state itself (DayCareCheckSpawnFlag), and that
// command may not run in a zone-init or field-load script (ov012 EVCMD_PERM_TABLE: level 0 only; a forbidden command
// hangs the game: notes/STORY_COMMON.md "Notes"), so he stays at (47,4).
#ifdef SCENE_ENTRIES
    ScriptEntry R117_DayCareMan         // 1: object 3, Route117_EventScript_1B222D
#else
#include "scenes/ch3b_lib.inc"

#define T_DCManIntro 0
#define T_DCManEgg 1
#define T_DCManReallyKeep 2
#define T_DCManKeepIt 3
#define T_DCManNoRoom 4
#define T_DCManReceivedEgg 5
#define T_DCManTakeCare 6
#define T_DCManOneMon 7
#define T_DCManTwoMons 8
#define T_DCVeryWell 9
#define T_DCAlong 10
#define T_DCDontLike 11
#define T_DCPlayOther 12

// GetDaycareState: 1 an Egg is waiting, 2 one Pokémon, 3 two, else 0. Black 2's own Day Care (global 1232 Script_1, the
// Route 3 man) gives the commands: DayCareCheckSpawnFlag (an Egg waiting), DayCareGetPkmCount, DayCareBreed
// (GiveEggFromDaycare), DayCareResetSeed (RejectEggFromDayCare), DayCareCalcEggSpawnChance (the compatibility score:
// Black 2's 70/50/20/0, 88/80/40 with its Oval Charm). Sapphire's mail check (DaycareMonReceivedMail) has no Black 2
// counterpart: left out.
R117_DayCareMan:
    c3_talk
    DayCareCheckSpawnFlag C3B_A
    h_goto_if_eq C3B_A, 1, L_R117_DCEgg
    DayCareGetPkmCount C3B_A
    h_goto_if_eq C3B_A, 1, L_R117_DCOneMon
    h_goto_if_eq C3B_A, 2, L_R117_DCTwoMons
    h_msgbox T_DCManIntro               // I'm the Day-Care Man. ...
    h_release
L_R117_DCEgg:                           // Route117_EventScript_1B2262
    h_yesno T_DCManEgg, C3B_A           // Ah, it's you! ... Your Pokémon had an Egg! ... You do want it, yes?
    h_goto_if_yes C3B_A, L_R117_DCTakeEgg
    h_yesno T_DCManReallyKeep, C3B_A    // I really will keep it. You do want this, yes?
    h_goto_if_yes C3B_A, L_R117_DCTakeEgg
    h_msgbox T_DCManKeepIt              // Well then, I'll keep it. Thanks!
    DayCareResetSeed                    // clearflag FLAG_PENDING_DAYCARE_EGG + special RejectEggFromDayCare
    h_release
L_R117_DCTakeEgg:                       // Route117_EventScript_1B2298
    h_getpartysize C3B_A
    h_goto_if_ne C3B_A, 6, L_R117_DCGiveEgg
    h_msgbox T_DCManNoRoom              // You have no room for it... Come back when you've made room.
    h_release
L_R117_DCGiveEgg:                       // Route117_EventScript_1B22B2
    h_closemessage
    h_buffer_player
    SystemMsg T_DCManReceivedEgg, 2     // message: <player> received the Egg from the Day-Care Man.
    h_playfanfare MUS_LEVEL_UP
    h_waitfanfare
    LastKeyWait
    MsgWinCloseAll
    DayCareBreed                        // special GiveEggFromDaycare (clears Black 2's Egg-waiting state)
    h_msgbox T_DCManTakeCare            // Take good care of it.
    h_release
L_R117_DCOneMon:                        // Route117_EventScript_1B22E7 (GetDaycareMonNicknames)
    WordSetDaycarePokeName 1, 0
    h_msgbox T_DCManOneMon              // Ah, it's you! Good to see you. Your <mon>'s doing fine.
    h_release
L_R117_DCTwoMons:                       // Route117_EventScript_1B22FE
    WordSetDaycarePokeName 1, 0
    WordSetDaycarePokeName 2, 1
    h_msgbox T_DCManTwoMons             // Ah, it's you! Your <mon> and <mon> are doing fine.
    DayCareCalcEggSpawnChance C3B_A     // SetDaycareCompatibilityString + ShowFieldMessageStringVar4
    h_goto_if_eq C3B_A, 70, L_R117_DCVeryWell
    h_goto_if_eq C3B_A, 88, L_R117_DCVeryWell
    h_goto_if_eq C3B_A, 50, L_R117_DCAlong
    h_goto_if_eq C3B_A, 80, L_R117_DCAlong
    h_goto_if_eq C3B_A, 0, L_R117_DCPlayOther
    h_msgbox T_DCDontLike               // The two don't seem to like each other much.
    h_release
L_R117_DCVeryWell:
    h_msgbox T_DCVeryWell
    h_release
L_R117_DCAlong:
    h_msgbox T_DCAlong
    h_release
L_R117_DCPlayOther:
    h_msgbox T_DCPlayOther
    h_release
    .balign 4, 0
#endif
