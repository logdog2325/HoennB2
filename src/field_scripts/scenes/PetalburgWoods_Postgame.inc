// Celebi in Petalburg Woods (postgame_scripts, 2026-10-07; user request: a post-game encounter in Petalburg Woods).
// Sapphire has no Celebi (it came on the Pokémon Colosseum bonus disc, Ageto Celebi Lv 10): a static legendary as
// Emerald's (its Mew / Lugia: the cry, then the battle; "The X flew away!" when knocked out), shown once the National Dex
// is there (Celebi is not in the Hoenn Pokédex). Black 2's own Celebi overworld sprite (4380), standing in the clearing
// north-east of the woods, behind the Miracle Seed girl: Sapphire tile (36,4) (data/story/postgame.json, uid 150).
// Included twice by scenes/PetalburgWoods.inc (guarded): the entry (script 5, after Ch1's four) and the body;
// PG_PW_Init is called by Ch1's zone init (PW_Init). Text: line 13 of src/text/scenes/PetalburgWoods.txt.
#ifdef SCENE_ENTRIES
    ScriptEntry PG_PW_Celebi        // 5: Celebi (post-game, data/story/postgame.json uid 150)
#else
#include "scenes/postgame_lib.inc"
#define PGPW_CELEBI 150
#define PGPW_T_FLEW 13

PG_PW_Init:                         // Emerald's TryShow...: shown unless caught or knocked out, once the National Dex is there
    FlagSet FLAG_HIDE_CELEBI
    PokeDexHaveNational HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_PGPW_InitDone
    h_goto_if_set FLAG_CAUGHT_CELEBI, L_PGPW_InitDone
    h_goto_if_set FLAG_DEFEATED_CELEBI, L_PGPW_InitDone
    FlagReset FLAG_HIDE_CELEBI
L_PGPW_InitDone:
    VMReturn

PG_PW_Celebi:                       // (Emerald FarawayIsland_Interior_EventScript_Mew's shape: lock, faceplayer, cry, battle)
    h_lock
    h_faceplayer
    h_playmoncry SPECIES_CELEBI
    h_waitmoncry
    h_delay 40
    pg_legend_battle SPECIES_CELEBI, PG_CELEBI_LEVEL, PGPW_CELEBI, FLAG_HIDE_CELEBI, FLAG_CAUGHT_CELEBI, FLAG_DEFEATED_CELEBI, PGPW_T_FLEW
    h_release
#endif
