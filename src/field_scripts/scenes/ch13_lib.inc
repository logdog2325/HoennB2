// Chapter Ch13's shared pieces (ch13 agent, 2026-10-07): the ferry. Macros only (no code, no labels). Needs
// hoenn_story.inc (included by the harbor rooms and the island zones) and, for the item names, hoenn_key_items.h.
//
// Black 2 has no ship to ride on a map (no ship object code, data/sprite_map.json OBJ_EVENT_GFX_SS_TIDAL; its ships move
// in its 3D demos: common/boat.inc), and the S.S. Tidal's own rooms (SSTidalCorridor, SSTidalRooms, SSTidalLowerDeck:
// no zone, no map) do not exist. So a crossing is: the attendant steps aside, the player boards and vanishes (Sapphire's
// hideobjectat), the screen fades out and Black 2's ferry cutscene plays with its ship music (h_sail_ferry, boats agent
// 2026-10-07), and the destination's arrival script (RTReserveScript) fades in at Sapphire's landing tile.
// Slateport <-> Lilycove also plays the S.S. Tidal's two public-address announcements of Sapphire's trip (the
// ding-dong, then the line): the departure one before the cutscene, the "We have made land in X" one on arrival.
// What is lost with the unbuilt ship: the cabins (the 8 trainers, the TM49 Snatch man, the bed that heals, Capt. Briney
// and Peeko), the porthole texts and the sailor's "We've arrived!".
#ifndef CH13_LIB_INC
#define CH13_LIB_INC
#include "hoenn_key_items.h"
#include "scenes/ch2_boat.inc"              // ch2_land, ch2_hide_player (the ferry trips: h_sail_ferry, hoenn_story.inc)

// The ferry's landing at the island (zone 17, standalone group BattleTower_Outside): Sapphire's MAP_BATTLE_TOWER_OUTSIDE
// (19,23), group origin (17,18). Emerald's island is the Battle Frontier: pokeemerald's harbors warp MAP_BATTLE_FRONTIER_
// OUTSIDE_WEST, 19, 67 (its dock, the attendant below at (19,68)); Outside West's origin in Emerald's world is (16,13).
// (Until 2026-10-19 Emerald used Sapphire's numbers: (36,41) is a wall tile in the middle of the Frontier.)
#ifdef HOENN_EMERALD
#define CH13_BT_DOCK_X (19 + 16)
#define CH13_BT_DOCK_Z (67 + 13)
#else
#define CH13_BT_DOCK_X (19 + 17)
#define CH13_BT_DOCK_Z (23 + 18)
#endif

#define CH13_SE_DING_DONG SEQ_SE_DECIDE1    /* [guess] Sapphire SE_DING_DONG, the ship's chime (notes/STORY_SPECIALS.md: no match known) */
#define CH13_RESPAWN_LILYCOVE 8             /* FieldSetTeleportZone n = 1 + the record of Lilycove's Pokémon Center (RESPAWN_ZONE_INFO 7) */
#define CH13_RESPAWN_SLATEPORT 18           /* ... of Slateport's (record 17): notes in b2tools/patches/centers.py */

// a line of the public-address system: the chime, then the line in an info window nobody says
    .macro ch13_announce n
    SEPlay CH13_SE_DING_DONG
    SystemMsg \n, 2
    LastKeyWait
    MsgWinCloseAll
    .endm

// the crossing of the S.S. Tidal between the two harbors: the ship's departure announcement n (Sapphire plays it on the
// ship's arrival, SSTidalCorridor_EventScript_15FCBC / ..._15FCD2) while the harbor is still on the screen (a message
// window does not show over Black 2's fade to black: tested), then Black 2's ferry cutscene, then the destination's
// arrival script
    .macro ch13_sail_announce zone, x, z, dir, script, n
    VMSleep 20
    ch13_announce \n
    h_sail_ferry \zone, \x, \z, \dir, \script
    .endm

// BoardFerry of the harbors: the attendant (uid) turns to the sea and is gone (hideobjectat: the object is back when the
// zone loads again), the player walks onto the attendant's tile (Black 2 directions: 0 = facing north, 3 = facing east)
    .macro ch13_board_dock uid
    h_closemessage
    h_move \uid, 40                         // walk_in_place_fastest_up
    VMSleep 15                              // delay 30
    ActorDelete \uid
    h_getplayerfacing HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, .Lbd_up\@
    h_goto_if_eq HLIB_TMP, 3, .Lbd_right\@
    VMJump .Lbd_done\@
.Lbd_up\@:
    h_move 255, 12                          // walk_up
    VMJump .Lbd_done\@
.Lbd_right\@:
    h_move 255, 15                          // walk_right
    h_move 255, 40                          // walk_in_place_fastest_up
.Lbd_done\@:
    VMSleep 15
    ch2_hide_player
    .endm

// FerryDepartIsland of the two islands: the person on the dock (uid) turns to the ferry and is gone; the player steps
// onto its tile (facing south: walk down; facing west: walk left, then turn south)
    .macro ch13_board_island uid
    h_closemessage
    h_move \uid, 41                         // walk_in_place_fastest_down
    VMSleep 15
    ActorDelete \uid
    h_getplayerfacing HLIB_TMP
    h_goto_if_eq HLIB_TMP, 1, .Lbi_down\@
    h_goto_if_eq HLIB_TMP, 2, .Lbi_left\@
    VMJump .Lbi_done\@
.Lbi_down\@:
    h_move 255, 13                          // walk_down
    VMJump .Lbi_done\@
.Lbi_left\@:
    h_move 255, 14                          // walk_left
    h_move 255, 41                          // walk_in_place_fastest_down
.Lbi_done\@:
    VMSleep 15
    ch2_hide_player
    .endm

// a legendary battle after its scene (Sapphire: setwildbattle + ScrSpecial_StartRayquazaBattle / StartSouthernIslandBattle,
// BATTLE_TYPE_LEGENDARY): Black 2's legendary encounter, as its own Latios/Latias and Volcarona scripts (0304.s, 0364.s).
// Won or caught: the actor is gone; lost: Black 2's whiteout (CallWildLose). The hide flag is set by the caller before
// the battle, as Sapphire does, so the Pokémon never comes back whatever happened. Levels are the scaled ones
// (data/level_scaling.json curve: Sapphire 70 -> 78, 50 -> 55), like Kyogre's 45 -> 49.
    .macro ch13_legend_battle species, level, uid
    CallWildBattle \species, \level, 1
    WildBattleIsVictory HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, .Lclb\@
    CallWildLose
    VMHalt
.Lclb\@:
    ActorDelete \uid
    CallWildBattleEnd
    .endm
#endif
