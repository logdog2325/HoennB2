// Post-game additions (postgame_scripts, 2026-10-07; notes/POSTGAME.md): shared macros and defines. No labels.
// The roamers' code is b2tools/patches/roamers.py / roamers.c (needs the `roamers` patch in the build's patch list): it
// gives Black 2's two unused roamer script commands new handlers.
#ifndef POSTGAME_LIB_INC
#define POSTGAME_LIB_INC

// roamer k = roamers.py ROAMERS: 0 Latias (Sapphire Lv 40), 1 Raikou, 2 Entei, 3 Suicune, 4 Articuno, 5 Zapdos,
// 6 Moltres (FRLG Lv 50); levels on data/level_scaling.json's curve (44 / 55)
#define PG_LATIAS 0
#define PG_RAIKOU 1
#define PG_MOLTRES 6
#define PG_RANDOM_LOC 0xFF

// Sapphire's InitRoamer for roamer k (full HP, a new Pokémon; loc 0-19 = a row of Sapphire's sRoamerLocations, Route 110,
// 111, 117-134; PG_RANDOM_LOC = Sapphire's random start). Command 434 (BW1's roamer command, unused by Black 2).
    .macro pg_roamer_start k, loc=PG_RANDOM_LOC
    FieldCommand 434
    .2byte \k
    .2byte \loc
    .endm
// var = 0 when roamer k is not roaming (not started, caught or knocked out), else its location + 1 (command 435)
    .macro pg_roamer_get var, k
    FieldCommand 435
    .2byte \var
    .2byte \k
    .endm

// a talking NPC (lock, the talk sound, face the player): Black 2's NPC pattern (hoenn_story.inc h_lock + h_faceplayer)
    .macro pg_talk
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    .endm

// Emerald's static legendary (setwildbattle + BattleSetup_StartLegendaryBattle + the outcome), as the events agent's
// ev_legend_battle (scenes/events_lib.inc): caught -> caught + hide flags; knocked out -> defeated + hide flags and "The
// X flew away!"; ran -> the line only (it is there again next time); lost -> whiteout.
    .macro pg_legend_battle species, level, uid, hide, caught, defeated, flew
    CallWildBattle \species, \level, 1
    WildBattleIsVictory HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, .Lpglb_won\@
    CallWildLose
    VMHalt
.Lpglb_won\@:
    ActorDelete \uid
    CallWildBattleEnd
    WildBattleGetResult HLIB_TMP
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_NE, .Lpglb_notcaught\@
    FlagSet \caught
    FlagSet \hide
    VMJump .Lpglb_done\@
.Lpglb_notcaught\@:
    WorkCmpConst HLIB_TMP, 2
    VMJumpIf CMP_NE, .Lpglb_ran\@
    FlagSet \defeated
    FlagSet \hide
.Lpglb_ran\@:
    WordSetPokeSpecies 1, \species
    SystemMsg \flew, 2
    LastKeyWait
    MsgWinCloseAll
.Lpglb_done\@:
    .endm

// levels (data/level_scaling.json's curve, as every static legendary of this port): Jirachi 5 (Wishmaker Jirachi, the
// R/S bonus disc's) -> 5; Celebi 10 (Ageto Celebi, the Colosseum bonus disc's) -> 10
#define PG_JIRACHI_LEVEL 5
#define PG_CELEBI_LEVEL 10
#endif
