// Version aliases for scene files (pokeruby constants/version.inc; notes/RUBY.md "WP0 layout", ruby_infra 2026-10-08).
// patches/scripts.py assembles every field script with -D HOENN_SAPPHIRE, -D HOENN_RUBY or -D HOENN_EMERALD (and
// HOENN_VERSION_ID 1 / 2 / 3, the decomps' GAME_VERSION / VERSION_EMERALD) from HOENN_VERSION (b2tools/version.py).
// A scene branches with
//     #ifdef HOENN_RUBY ... #else ... #endif
// and keeps its ScriptEntry list identical in Sapphire and Ruby (only bodies branch). Include after "hoenn.h".
// Emerald (notes/EMERALD.md) takes the #else (Sapphire) branch everywhere until its story is ported (phase 3): an
// Emerald-only branch is `#ifdef HOENN_EMERALD`, put before the Ruby/Sapphire test; Emerald-only ScriptEntry lines go
// at the end of a scene's list under `#ifdef HOENN_EMERALD` (converter/gen_map_content.py counts each version's list
// through the preprocessor: notes/EMERALD_STORY.md S0-2).
// The Black 2 field-model codes (a/2/0/8 records) are the ones b2tools/version.py's _TABLE names for patches/story.py.
// Trainers keep their Sapphire constants (TRAINER_MATT_2 ...): in Ruby the same Black 2 trainer id holds the Ruby twin
// (converter/gen_trainers.py, WP1); the readable aliases below name the role.
#ifndef HOENN_VERSION_INC
#define HOENN_VERSION_INC

#if !defined(HOENN_RUBY) && !defined(HOENN_SAPPHIRE) && !defined(HOENN_EMERALD)
#error "assemble field scripts through b2tools/patches/scripts.py (it passes -D HOENN_SAPPHIRE, HOENN_RUBY or HOENN_EMERALD)"
#endif

#ifdef HOENN_EMERALD
// Emerald (emerald_s0 2026-10-12, notes/EMERALD_STORY.md S0-5; pokeemerald's scripts). Both teams and both legendaries:
// Team Aqua wakes Kyogre at the Seafloor Cavern (Sapphire's flow there: Room 9, Route 128), Team Magma wakes Groudon in
// the Magma Hideout. The shared names keep their Sapphire meaning (the Seafloor / Cave of Origin legendary, Southern
// Island's Lati, the orb the shared scenes hand over), so every shared scene assembles unchanged; Emerald's own scenes
// use the explicit names.
#define SPECIES_GROUDON_OR_KYOGRE   SPECIES_KYOGRE      // the one Team Aqua wakes (Seafloor Cavern Room 9)
#define MODEL_GROUDON_OR_KYOGRE     4511
#define MODEL_KYOGRE                4511                // Black 2 field models (a/2/0/8 records, version.py _TABLE)
#define MODEL_GROUDON               4512                // Magma Hideout 4F, Sootopolis, Terra Cave
#define MODEL_RAYQUAZA              4513                // Sky Pillar Top, Sootopolis
// Lati by colour (pokeemerald data/scripts/players_house.inc:443-446, src/roamer.c CreateInitialRoamerMon): after the
// Hall of Fame Mom asks which colour the TV showed; VAR_ROAMER_POKEMON 0 (Red) = Latias roams and Latios waits on
// Southern Island, 1 (Blue) = Latios roams and Latias waits (data/maps/SouthernIsland_Interior/scripts.inc:17-18).
// The shared names are the island one for 0 (Sapphire's arrangement, also what an Emerald save has until the colour
// scene exists); the _IF_BLUE names are the island one for 1 (SouthernIsland_Interior.inc tests the var: Ch13).
#define SPECIES_LATIAS_OR_LATIOS    SPECIES_LATIOS
#define MODEL_LATIAS_OR_LATIOS      4510
#define SPECIES_LATI_ISLAND_IF_BLUE SPECIES_LATIAS
#define MODEL_LATI_ISLAND_IF_BLUE   4509
// Orbs (pokeemerald MtPyre_Summit, MagmaHideout_4F, SootopolisCity): Archie takes the Red Orb at Mt. Pyre (as in
// Sapphire), Maxie has the Blue Orb in the Magma Hideout; the old lady gives the player the Magma Emblem instead of an
// orb (and sets FLAG_RECEIVED_RED_OR_BLUE_ORB), and the two leaders bring both orbs back. ITEM_RED_OR_BLUE_ORB stays
// Sapphire's Blue Orb for the shared scenes and test kits that still hand it over (ch8b_test.inc, ch10_test.inc,
// MtPyre_Summit_Ch10.inc) until their Emerald branches replace them (Ch8 / Ch10). ITEM_MAGMA_EMBLEM (Mt. Pyre's old woman, Jagged
// Pass) is Black 2's Magma Stone, a Gen 4 key item no Black 2 script gives, renamed in an Emerald build by
// src/text/emerald/overrides_magma_emblem.json (emerald_ch45_magma 2026-10-12).
#define ITEM_MAGMA_EMBLEM           ITEM_MAGMA_STONE    // 458
#define ITEM_RED_OR_BLUE_ORB        ITEM_BLUE_ORB
#define ITEM_ORB_OF_AQUA            ITEM_RED_ORB        // the orb Archie takes at Mt. Pyre
#define ITEM_ORB_OF_MAGMA           ITEM_BLUE_ORB       // the orb Maxie holds in the Magma Hideout
#elif defined(HOENN_RUBY)
#define SPECIES_GROUDON_OR_KYOGRE   SPECIES_GROUDON
#define SPECIES_LATIAS_OR_LATIOS    SPECIES_LATIAS      // Southern Island (the roamer is the other one)
#define ITEM_RED_OR_BLUE_ORB        ITEM_RED_ORB
#define MODEL_GROUDON_OR_KYOGRE     4512                // Black 2 field model of the legendary
#define MODEL_LATIAS_OR_LATIOS      4509
#else
#define SPECIES_GROUDON_OR_KYOGRE   SPECIES_KYOGRE
#define SPECIES_LATIAS_OR_LATIOS    SPECIES_LATIOS
#define ITEM_RED_OR_BLUE_ORB        ITEM_BLUE_ORB
#define MODEL_GROUDON_OR_KYOGRE     4511
#define MODEL_LATIAS_OR_LATIOS      4510
#endif

// pokeruby constants/version.inc trainer aliases: the trainer that plays the role.
#ifdef HOENN_EMERALD
// Emerald: pokeemerald's trainer of that place (src/include/hoenn_trainers_emerald.h, converter/gen_trainers.py; every
// Emerald name there is a Black 2 id: a trainer in a slot Emerald shares with Sapphire kept Sapphire's id). 25 roles are
// the same Black 2 id as Sapphire's (only the readable name differs); the three Mt. Chimney roles are Team Magma's
// people, who have ids of their own (Sapphire's ids 45 / 31 / 134 hold Zander, a Seafloor grunt and Leah in Emerald):
// a shared scene reaches Emerald's trainer only through these role names (scenes/MtChimney.inc names TRAINER_ARCHIE_3
// directly today: the Ch5 builder switches it to TRAINER_MT_CHIMNEY_GRUNT_3). Emerald-only trainers have no role
// name: scenes use pokeemerald's (TRAINER_GRUNT_MT_CHIMNEY_1, TRAINER_MAXIE_MAGMA_HIDEOUT, ...).
#include "hoenn_trainers_emerald.h"
#define TRAINER_PETALBURG_WOODS_GRUNT        TRAINER_GRUNT_PETALBURG_WOODS       // = TRAINER_GRUNT_9's id (19)
#define TRAINER_RUSTURF_TUNNEL_GRUNT         TRAINER_GRUNT_RUSTURF_TUNNEL        // = TRAINER_GRUNT_15's (32)
#define TRAINER_MUSEUM_2F_GRUNT_1            TRAINER_GRUNT_MUSEUM_1              // = TRAINER_GRUNT_19's (36)
#define TRAINER_MUSEUM_2F_GRUNT_2            TRAINER_GRUNT_MUSEUM_2              // = TRAINER_GRUNT_20's (37)
#define TRAINER_514                          TRAINER_HECTOR                      // = TRAINER_HECTOR_1's (640)
#define TRAINER_MT_CHIMNEY_GRUNT_1           TRAINER_TABITHA_MT_CHIMNEY          // object 3 (Sapphire: Matt)
#define TRAINER_MT_CHIMNEY_GRUNT_2           TRAINER_GRUNT_MT_CHIMNEY_2          // object 22 (Sapphire: Grunt 13; Emerald (9,16))
#define TRAINER_HIDEOUT_1F_GRUNT             TRAINER_GRUNT_AQUA_HIDEOUT_1        // = TRAINER_GRUNT_1's (4)
#define TRAINER_HIDEOUT_B1F_GRUNT_1          TRAINER_GRUNT_AQUA_HIDEOUT_2        // = TRAINER_GRUNT_2's (5)
#define TRAINER_HIDEOUT_B1F_GRUNT_2          TRAINER_GRUNT_AQUA_HIDEOUT_3        // = TRAINER_GRUNT_3's (6)
#define TRAINER_HIDEOUT_B1F_GRUNT_3          TRAINER_GRUNT_AQUA_HIDEOUT_5        // = TRAINER_GRUNT_26's (42)
#define TRAINER_HIDEOUT_B2F_GRUNT_1          TRAINER_MATT                        // = TRAINER_MATT_1's (44)
#define TRAINER_HIDEOUT_B2F_GRUNT_2          TRAINER_GRUNT_AQUA_HIDEOUT_4        // = TRAINER_GRUNT_4's (10)
#define TRAINER_HIDEOUT_B2F_GRUNT_3          TRAINER_GRUNT_AQUA_HIDEOUT_6        // = TRAINER_GRUNT_27's (43)
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_1      TRAINER_GRUNT_SEAFLOOR_CAVERN_1     // = TRAINER_GRUNT_5's (11)
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_2      TRAINER_GRUNT_SEAFLOOR_CAVERN_2     // = TRAINER_GRUNT_6's (12)
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_3      TRAINER_SHELLY_SEAFLOOR_CAVERN      // = TRAINER_SHELLY_2's (47)
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_4      TRAINER_GRUNT_SEAFLOOR_CAVERN_3     // = TRAINER_GRUNT_7's (16)
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_5      TRAINER_ARCHIE                      // = TRAINER_ARCHIE_2's (133)
#define TRAINER_MT_CHIMNEY_GRUNT_3           TRAINER_MAXIE_MT_CHIMNEY            // the leader battle (Sapphire: Archie 3)
#define TRAINER_MT_PYRE_SUMMIT_GRUNT_1       TRAINER_GRUNT_MT_PYRE_1             // = TRAINER_GRUNT_22's (38)
#define TRAINER_MT_PYRE_SUMMIT_GRUNT_2       TRAINER_GRUNT_MT_PYRE_2             // = TRAINER_GRUNT_23's (39)
#define TRAINER_MT_PYRE_SUMMIT_GRUNT_3       TRAINER_GRUNT_MT_PYRE_3             // = TRAINER_GRUNT_24's (40)
#define TRAINER_WEATHER_INSTITUTE_GRUNT_1    TRAINER_GRUNT_WEATHER_INST_1        // = TRAINER_GRUNT_16's (33)
#define TRAINER_WEATHER_INSTITUTE_GRUNT_2    TRAINER_GRUNT_WEATHER_INST_4        // = TRAINER_GRUNT_25's (41)
#define TRAINER_WEATHER_INSTITUTE_GRUNT_3    TRAINER_GRUNT_WEATHER_INST_2        // = TRAINER_GRUNT_17's (34)
#define TRAINER_WEATHER_INSTITUTE_GRUNT_4    TRAINER_GRUNT_WEATHER_INST_3        // = TRAINER_GRUNT_18's (35)
#define TRAINER_WEATHER_INSTITUTE_GRUNT_5    TRAINER_SHELLY_WEATHER_INSTITUTE    // = TRAINER_SHELLY_1's (46)
// Same Black 2 id, role swapped by gen_trainers (no alias needed): TRAINER_WALLACE (396) is Juan (TRAINER_JUAN_1),
// TRAINER_STEVEN (457) is Champion Wallace (TRAINER_WALLACE_EMERALD).
#else
// Sapphire and Ruby: the Sapphire constant whose Black 2 id plays the role in both versions
#define TRAINER_PETALBURG_WOODS_GRUNT        TRAINER_GRUNT_9
#define TRAINER_RUSTURF_TUNNEL_GRUNT         TRAINER_GRUNT_15
#define TRAINER_MUSEUM_2F_GRUNT_1            TRAINER_GRUNT_19
#define TRAINER_MUSEUM_2F_GRUNT_2            TRAINER_GRUNT_20
#define TRAINER_514                          TRAINER_HECTOR_1
#define TRAINER_MT_CHIMNEY_GRUNT_1           TRAINER_MATT_2
#define TRAINER_MT_CHIMNEY_GRUNT_2           TRAINER_GRUNT_13
#define TRAINER_HIDEOUT_1F_GRUNT             TRAINER_GRUNT_1
#define TRAINER_HIDEOUT_B1F_GRUNT_1          TRAINER_GRUNT_2
#define TRAINER_HIDEOUT_B1F_GRUNT_2          TRAINER_GRUNT_3
#define TRAINER_HIDEOUT_B1F_GRUNT_3          TRAINER_GRUNT_26
#define TRAINER_HIDEOUT_B2F_GRUNT_1          TRAINER_MATT_1
#define TRAINER_HIDEOUT_B2F_GRUNT_2          TRAINER_GRUNT_4
#define TRAINER_HIDEOUT_B2F_GRUNT_3          TRAINER_GRUNT_27
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_1      TRAINER_GRUNT_5
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_2      TRAINER_GRUNT_6
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_3      TRAINER_SHELLY_2
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_4      TRAINER_GRUNT_7
#define TRAINER_SEAFLOOR_CAVERN_GRUNT_5      TRAINER_ARCHIE_2
#define TRAINER_MT_CHIMNEY_GRUNT_3           TRAINER_ARCHIE_3
#define TRAINER_MT_PYRE_SUMMIT_GRUNT_1       TRAINER_GRUNT_22
#define TRAINER_MT_PYRE_SUMMIT_GRUNT_2       TRAINER_GRUNT_23
#define TRAINER_MT_PYRE_SUMMIT_GRUNT_3       TRAINER_GRUNT_24
#define TRAINER_WEATHER_INSTITUTE_GRUNT_1    TRAINER_GRUNT_16
#define TRAINER_WEATHER_INSTITUTE_GRUNT_2    TRAINER_GRUNT_25
#define TRAINER_WEATHER_INSTITUTE_GRUNT_3    TRAINER_GRUNT_17
#define TRAINER_WEATHER_INSTITUTE_GRUNT_4    TRAINER_GRUNT_18
#define TRAINER_WEATHER_INSTITUTE_GRUNT_5    TRAINER_SHELLY_1
#endif

#endif
