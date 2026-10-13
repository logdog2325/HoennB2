// Test start for the town_map agent (test builds only: HOENN_TEST_CHTM=1, usually with HOENN_TEST_WARP=563,6,7;
// 2026-10-08, b2tools/patches/town_map.py, notes/TOWN_MAP.md). Littleroot's town sign (stand at (183,366) facing north)
// runs Test_TM_Setup, then the sign's test warp (tests overwrite the warp's constants and TM_STAGE_SENTINEL in an APFS
// clone of the ROM, as b2tools/room_look.py does, so one build reaches every place):
//  0x7A01  the Town Map, HM02, the eight Badges, a Lv 50 Swellow that knows Fly, every town visited (FLAG_VISITED_*)
//  0x7A02  the same + the game cleared and the Battle Tower / Southern Island landmarks (the post-game icons)
//  0x7A03  only the Town Map (no Badges, no town visited: the view-only map and the hidden icons)
//  0x7A04  0x7A01 + the Pokédex with Swellow and Zigzagoon caught (its area page draws the town map's art)
// Never assembled into normal builds.
#ifdef HOENN_TEST_CHTM
#ifndef TOWN_MAP_TEST_INC
#define TOWN_MAP_TEST_INC
#define TM_STAGE 0x8004
Test_TM_Setup:
    h_setvar TM_STAGE, 0x7A01               // TM_STAGE_SENTINEL
    ItemCheckAmount ITEM_TOWN_MAP, 1, HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_TM_Done      // once
    ItemAdd ITEM_TOWN_MAP, 1, HLIB_TMP
    h_goto_if_eq TM_STAGE, 0x7A03, L_TM_Done
    FlagSet 2401                            // FLAG_SYS_POKEMON_GET (the field menu shows POKEMON)
    FlagSet 2403                            // FLAG_SYS_B_DASH
    ItemAdd ITEM_HM02, 1, HLIB_TMP
    PokePartyAdd HLIB_TMP, SPECIES_SWELLOW, 0, 50
    PokePartyLearnMove 0, 0, MOVE_FLY
    TrainerCardAddBadge 0
    TrainerCardAddBadge 1
    TrainerCardAddBadge 2
    TrainerCardAddBadge 3
    TrainerCardAddBadge 4
    TrainerCardAddBadge 5
    TrainerCardAddBadge 6
    TrainerCardAddBadge 7
    FlagSet FLAG_VISITED_LITTLEROOT_TOWN
    FlagSet FLAG_VISITED_OLDALE_TOWN
    FlagSet FLAG_VISITED_DEWFORD_TOWN
    FlagSet FLAG_VISITED_LAVARIDGE_TOWN
    FlagSet FLAG_VISITED_FALLARBOR_TOWN
    FlagSet FLAG_VISITED_VERDANTURF_TOWN
    FlagSet FLAG_VISITED_PACIFIDLOG_TOWN
    FlagSet FLAG_VISITED_PETALBURG_CITY
    FlagSet FLAG_VISITED_SLATEPORT_CITY
    FlagSet FLAG_VISITED_MAUVILLE_CITY
    FlagSet FLAG_VISITED_RUSTBORO_CITY
    FlagSet FLAG_VISITED_FORTREE_CITY
    FlagSet FLAG_VISITED_LILYCOVE_CITY
    FlagSet FLAG_VISITED_MOSSDEEP_CITY
    FlagSet FLAG_VISITED_SOOTOPOLIS_CITY
    FlagSet FLAG_VISITED_EVER_GRANDE_CITY
    h_goto_if_eq TM_STAGE, 0x7A05, L_TM_DexArea
    h_goto_if_eq TM_STAGE, 0x7A06, L_TM_DexArea
    h_goto_if_ne TM_STAGE, 0x7A04, L_TM_NoDex
    FlagSet 2402                            // has the Pokédex (Black 2; LittlerootTown_ch1.inc)
    PokeDexRegist 1, SPECIES_SWELLOW
    PokeDexRegist 1, SPECIES_ZIGZAGOON
L_TM_NoDex:
    h_goto_if_ne TM_STAGE, 0x7A02, L_TM_Done
    FlagSet FLAG_SYS_GAME_CLEAR
    FlagSet FLAG_LANDMARK_BATTLE_TOWER
    FlagSet FLAG_LANDMARK_SOUTHERN_ISLAND
L_TM_Done:
    VMReturn
// 0x7A05 (dex_area, the Pokédex AREA page): 0x7A01 + the Pokédex; caught (party): Zigzagoon (routes), Tentacool
// (water), Geodude (caves), the version's roamer; seen: Wingull, Zubat, Magikarp, Wynaut, Kyogre, Raikou, Entei; the
// version's roamer roams at location 0 (Route 110) and Raikou at location 9, Entei does not; the National Dex
L_TM_DexArea:
    FlagSet 2402
    ItemAdd ITEM_POKE_BALL, 20, HLIB_TMP     // (a catch: the entry screen's page flip)
    PokePartyAdd HLIB_TMP, SPECIES_ZIGZAGOON, 0, 5
    PokePartyAdd HLIB_TMP, SPECIES_TENTACOOL, 0, 5
    PokePartyAdd HLIB_TMP, SPECIES_GEODUDE, 0, 5
#ifdef HOENN_RUBY
    PokePartyAdd HLIB_TMP, SPECIES_LATIOS, 0, 40
#else
    PokePartyAdd HLIB_TMP, SPECIES_LATIAS, 0, 40
#endif
    PokeDexRegist 0, SPECIES_WINGULL
    PokeDexRegist 0, SPECIES_ZUBAT
    PokeDexRegist 0, SPECIES_MAGIKARP
    PokeDexRegist 0, SPECIES_WYNAUT
    PokeDexRegist 0, SPECIES_KYOGRE
    PokeDexRegist 0, SPECIES_RAIKOU
    PokeDexRegist 0, SPECIES_ENTEI
    FieldCommand 434                        // pg_roamer_start 0, 0 (scenes/postgame_lib.inc)
    .2byte 0
    .2byte 0
    FieldCommand 434                        // pg_roamer_start 1, 9
    .2byte 1
    .2byte 9
    PokeDexGiveNational
    h_goto_if_ne TM_STAGE, 0x7A06, L_TM_Done
    // 0x7A06 (Habitat list): 0x7A05 + every Habitat list place visited, HM03 and the Super Rod (the list's surfing
    // and fishing kinds come with the next zone entry: b2tools/patches/hoenn_pokedex.py HabitatDiscover)
    WorkSet VAR_HABITAT_VISITED_0, 0xFFFF
    WorkSet VAR_HABITAT_VISITED_1, 0xFFFF
    WorkSet VAR_HABITAT_VISITED_2, 0xFFFF
    WorkSet VAR_HABITAT_VISITED_3, 0xFFFF
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    ItemAdd ITEM_SUPER_ROD, 1, HLIB_TMP
    VMReturn
#endif
#endif
