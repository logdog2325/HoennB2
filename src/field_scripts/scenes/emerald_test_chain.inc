// Pokémon Emerald NDS: the Emerald-only part of the chapter test start states (emerald_s0 2026-10-12; notes/EMERALD_STORY.md
// S0-6). Test builds only: every chapter test kit (scenes/ch*_test.inc, HOENN_TEST_CH<n>) sets Sapphire's chain of flags,
// badges and items, then, in an Emerald build, `em_test_chain AT` adds what Emerald's chapters before that point set
// that Sapphire has no id for. AT = chapter x 10 (+1 for a chapter's second part): 20 = the start of Ch2, 31 = Ch3b
// (Mauville), 81 = Ch8b, 120 = Ch12, 130 = the post-game. Only ids that exist (src/include/hoenn.h, group Emerald) are set;
// each Emerald chapter builder adds its own beats here when it claims their ids (python3 converter/gen_story_ids.py
// --claim Emerald NAME ...), in pokeemerald's order, so the next chapter's test start includes them.
// Sources (pokeemerald data/maps/*/scripts.inc): Scott: PetalburgCity:525-540 (VAR_SCOTT_STATE 1, encounter 1),
// RustboroCity_PokemonSchool:166-189 (+1 met, +1 after the Stone Badge), RustboroCity_DevonCorp_3F:55 (school Scott hidden),
// SlateportCity:82 (+1), MauvilleCity:157 (+1), Route119:152 (+1) and :466 (the Fortree call, +1), LilycoveCity_CoveLilyMotel_2F:58
// (+1, met), SlateportCity_Harbor:64 (motel Scott hidden), MossdeepCity:256 (+1), MossdeepCity_SpaceCenter_2F:289 (Mossdeep
// Scott hidden), EverGrandeCity_PokemonCenter_1F:40 (+1, met) and EverGrandeCity_SidneysRoom:9-10 (met, hidden). Each
// Scott object is removed by its scene (removeobject sets its hide flag), so the flags of the places passed are set.
// The Battle Tent / Match Call parts (Verdanturf, Fallarbor, Scott's calls as calls) are left out (decisions 2 and 3A).
#ifndef EMERALD_TEST_CHAIN_INC
#define EMERALD_TEST_CHAIN_INC

    .macro em_test_chain at
    .if \at >= 20                           // Ch1 done: Scott in Petalburg and twice at the Pokémon School
    h_setvar VAR_SCOTT_PETALBURG_ENCOUNTER, 1
    h_setflag FLAG_HIDE_PETALBURG_CITY_SCOTT
    h_setflag FLAG_MET_SCOTT_RUSTBORO
    h_setflag FLAG_MET_SCOTT_AFTER_OBTAINING_STONE_BADGE
    h_setvar VAR_SCOTT_STATE, 3
    .endif
    .if \at >= 30                           // Ch2 done: Mr. Stone's scene hides the school's Scott
    h_setflag FLAG_HIDE_RUSTBORO_CITY_POKEMON_SCHOOL_SCOTT
    .endif
    .if \at >= 31                           // Ch3a done: Scott outside the museum in Slateport
    h_setflag FLAG_HIDE_SLATEPORT_CITY_SCOTT
    h_setvar VAR_SCOTT_STATE, 4
    .endif
    .if \at >= 40                           // Ch3 done: Scott in Mauville after the Wally battle
    h_setflag FLAG_HIDE_MAUVILLE_CITY_SCOTT
    h_setvar VAR_SCOTT_STATE, 5
    .endif
    .if \at >= 80                           // Ch7 done: Scott on Route 119 and his Fortree message
    h_setflag FLAG_HIDE_ROUTE_119_SCOTT
    h_setvar VAR_SCOTT_STATE, 7
    .endif
    .if \at >= 81                           // Ch8a done: Scott in the Cove Lily Motel
    h_setflag FLAG_MET_SCOTT_IN_LILYCOVE
    h_setvar VAR_SCOTT_STATE, 8
    .endif
    .if \at >= 90                           // Ch8 done: the Slateport harbor scene hides the motel's Scott
    h_setflag FLAG_HIDE_LILYCOVE_MOTEL_SCOTT
    // the Magma Hideout's end (0718_room_MagmaHideout_4F.s MH4F_Maxie, emerald_ch8_hideout; pokeemerald MagmaHideout_4F:53-64): Groudon
    // awake and gone, Maxie, the grunts and Tabitha hidden, Maxie beaten (Slateport's own state is the shared kits')
    h_setflag FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT
    h_setflag FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS
    h_setflag FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON
    h_setflag FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON_ASLEEP
    h_settrainerflag 403                    // TRAINER_MAXIE_MAGMA_HIDEOUT (hoenn_trainers_emerald.h; not every kit includes hoenn_version.inc)
    .endif
    .if \at >= 100                          // Ch9 done: Scott in Mossdeep; the Space Center win hides him
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SCOTT
    h_setvar VAR_SCOTT_STATE, 9
    // the Space Center won and Steven's Dive (emerald/0676 SC2_Steven, 0678 SH_StevenGivesDive; emerald_ch9_mirage; pokeemerald
    // MossdeepCity_SpaceCenter_2F_EventScript_DefeatedMaxieTabitha and MossdeepCity_StevensHouse_EventScript_StevenGivesDive)
    h_setvar VAR_MOSSDEEP_CITY_STATE, 3
    h_setvar VAR_MOSSDEEP_SPACE_CENTER_STATE, 3
    h_setflag FLAG_DEFEATED_MAGMA_SPACE_CENTER
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_1F_TEAM_MAGMA
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_1F_STEVEN
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_STEVEN
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_MAGMA_NOTE
    h_clearflag FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_STEVEN
    h_setvar VAR_STEVENS_HOUSE_STATE, 2
    h_setflag FLAG_RECEIVED_HM08
    h_setflag FLAG_OMIT_DIVE_FROM_STEVEN_LETTER
    h_setflag FLAG_HIDE_SEAFLOOR_CAVERN_ENTRANCE_AQUA_GRUNT
    .endif
    .if \at >= 130                          // Ch11 done: Scott in the Ever Grande Pokémon Center (gone once you meet Sidney)
    h_setflag FLAG_MET_SCOTT_IN_EVERGRANDE
    h_setflag FLAG_HIDE_EVER_GRANDE_POKEMON_CENTER_1F_SCOTT
    h_setvar VAR_SCOTT_STATE, 10
    h_setflag FLAG_IS_CHAMPION              // the Hall of Fame's Emerald lines (0114 HF_EmeraldFlags, emerald_ch11_gameclear)
    h_setvar VAR_FOSSIL_MANIAC_STATE, 1
    h_setflag FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD
    h_clearflag FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_INVISIBLE_NINJA_BOY
    h_setflag FLAG_HIDE_SAFARI_ZONE_SOUTH_CONSTRUCTION_WORKERS
    h_clearflag FLAG_HIDE_SAFARI_ZONE_SOUTH_EAST_EXPANSION
    h_setflag FLAG_HIDE_LILYCOVE_CITY_RIVAL
    .endif
    .endm

#endif
