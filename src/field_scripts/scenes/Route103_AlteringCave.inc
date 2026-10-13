// Route 103's door to Emerald's Altering Cave (postgame_maps, 2026-10-07): called from Route 103's zone init
// (scenes/Route103.inc Story_Init, guarded), code only (no ScriptEntry, no text).
//
// Emerald: Route103_OnLoad opens the cave mouth at (45,5)/(45,6) once FLAG_SYS_GAME_CLEAR is set; Altering Cave's wild
// Pokémon are one of nine tables (gAlteringCave1-9, src/wild_encounter.c) picked by VAR_ALTERING_CAVE_WILD_SET, which only
// Mystery Gift changes (data/scripts/gift_altering_cave.inc: +1, wrapping after the ninth). Here:
// - the mouth: Route 103's post-game layout (data/hoenn_map_additions.json LAYOUT_ROUTE103_ALTERING_CAVE, the mouth at
//   Sapphire's (47,6)) as map replace event 7, set with FLAG_SYS_GAME_CLEAR by the game-clear scene
//   (scenes/ch13_gameclear.inc, as Route 131's Sky Pillar islet); this zone init sets it too, as Route 131's does.
// - the tables: Black 2 has one wild table per zone header, so the cave is zone 271 (table 1) plus eight copies of it
//   (data/cave_layouts/AlteringCave.json "variants": same room, entities and scripts, tables 2-9; installed by
//   b2tools/patches/interiors.py). The door is Black 2's dynamic warp (dest id 0x100 = GameData's next zone, ov035
//   EventMapChangeWarp_CreateFromEntity; data/hoenn_map_additions.json), and this sets the next zone to the copy of the
//   day, arriving where the cave's exit puts you ((18,22), facing up). The table rotates by day instead of by gift:
//   Zubat (Emerald's own, VAR_ALTERING_CAVE_WILD_SET 0) until the first visit (the cave's zone init sets Emerald's
//   FLAG_LANDMARK_ALTERING_CAVE), then one step on in Emerald's order (Mareep, Pineco, Houndour, Teddiursa, Aipom,
//   Shuckle, Stantler, Smeargle, Zubat ...) on each new day (FLAG_DAILY_ALTERING_CAVE: Black 2's midnight reset) that
//   the player passes through Route 103's zone.
// The next zone is saved with the game (EventFieldContinue reads it after loading a save), so a save made in Route 103
// keeps the door working; Black 2's other users of the next zone (the Union Room, Dive, the PWT, the Hall of Fame's
// continue spot with flag 2405) set it themselves right before they need it.
// Test switch (HOENN_TEST_CHPM_ALTERING=n, 1-9): the game counts as cleared, the mouth is there on a warp into Route 103
// (HOENN_TEST_WARP=326,217,287: Sapphire (49,7), east of the mouth) and table n is today's.
#ifndef ROUTE103_ALTERING_CAVE_INC
#define ROUTE103_ALTERING_CAVE_INC
#define AC_MAP_REPLACE_GAME_CLEAR 7     /* map replace event 7 (work 0x4038 == 0x408): the game-clear layouts */
#define AC_X 18                         /* the cave's arrival tile (zone tiles = Emerald's, origin (0,0)), level 0 */
#define AC_Y 0
#define AC_Z 22
#define AC_DOOR_WARP 7                  /* Emerald: the door's index in Route 103's zone (326: Black 2's 7 warps, then this
                                           door; read in the built ROM, emerald_ch12_13) */

    .macro ac_next_zone table, zone
    h_goto_if_ne VAR_ALTERING_CAVE_WILD_SET, \table, .Lac\@
    FieldSetNextZone \zone, 1, AC_X, AC_Y, AC_Z
    VMReturn
.Lac\@:
    .endm

Sub_AC_Door:
#ifdef HOENN_TEST_CHPM_ALTERING
    FlagSet FLAG_SYS_GAME_CLEAR                          // TEST ONLY
#endif
#ifdef HOENN_EMERALD
    // Emerald (emerald_ch10, 2026-10-12): Route 131's zone init sets event 7 for the whole game (Emerald's Sky Pillar islet is
    // always there), so before the game is clear this zone takes it off again (Route 103 keeps its sealed mouth)
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_AC_Clear
    // (emerald_ch12_13) Emerald's map has land in front of the sealed mouth (Sapphire's has the sea): the door is parked
    // off the map until the game is clear (as Jagged Pass's JP_HIDEOUT_WARP); walking into the rock warped into zone 0
    ObjInitWarpGPos AC_DOOR_WARP, 0, 0, 0
    MapReplaceIsEventSet AC_MAP_REPLACE_GAME_CLEAR, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_AC_Ret
    MapReplaceSetEvent AC_MAP_REPLACE_GAME_CLEAR, 0, 1
    VMJump L_AC_Ret
L_AC_Clear:
#endif
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_AC_Ret
    MapReplaceIsEventSet AC_MAP_REPLACE_GAME_CLEAR, HLIB_TMP     // (a warp into Route 103: the matrix is reloaded before
    h_goto_if_eq HLIB_TMP, 1, L_AC_Open                          // the field is built, as Route 131's zone init)
    MapReplaceSetEvent AC_MAP_REPLACE_GAME_CLEAR, 1, 1
L_AC_Open:
    h_goto_if_set FLAG_DAILY_ALTERING_CAVE, L_AC_Pick
    FlagSet FLAG_DAILY_ALTERING_CAVE
    h_goto_if_unset FLAG_LANDMARK_ALTERING_CAVE, L_AC_Pick
    WorkAdd VAR_ALTERING_CAVE_WILD_SET, 1
    h_goto_if_lt VAR_ALTERING_CAVE_WILD_SET, 9, L_AC_Pick
    WorkSetConst VAR_ALTERING_CAVE_WILD_SET, 0
L_AC_Pick:
#ifdef HOENN_TEST_CHPM_ALTERING
    WorkSetConst VAR_ALTERING_CAVE_WILD_SET, HOENN_TEST_CHPM_ALTERING - 1    // TEST ONLY
#endif
    ac_next_zone 0, 271                                  // gAlteringCave1 Zubat
    ac_next_zone 1, 272                                  // gAlteringCave2 Mareep
    ac_next_zone 2, 275                                  // gAlteringCave3 Pineco
    ac_next_zone 3, 276                                  // gAlteringCave4 Houndour
    ac_next_zone 4, 318                                  // gAlteringCave5 Teddiursa
    ac_next_zone 5, 320                                  // gAlteringCave6 Aipom
    ac_next_zone 6, 327                                  // gAlteringCave7 Shuckle
    ac_next_zone 7, 328                                  // gAlteringCave8 Stantler
    ac_next_zone 8, 330                                  // gAlteringCave9 Smeargle
    FieldSetNextZone 271, 1, AC_X, AC_Y, AC_Z            // (out of range: Emerald's own table)
L_AC_Ret:
    VMReturn
#endif
