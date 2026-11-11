// The other weather legend in Sapphire / Ruby NDS (postgame_dex, 2026-11-09; user decision 2026-11-09, notes/POSTGAME.md
// "Post-game dex completion"): after the Champion, the legend this version never had (Sapphire: Groudon, Ruby: Kyogre:
// SPECIES_KYOGRE_OR_GROUDON, src/include/hoenn_version.inc) sleeps in Seafloor Cavern Room 9 at (17,38), the very spot
// where the other version's legend slept (pokeruby SeafloorCavern_Room9: one map, one sleeping legend, Kyogre in
// Sapphire and Groudon in Ruby). Room 9's own legend is gone for good after the story, so nothing else uses the room.
// THE ROOM'S LOOK (user 2026-11-10): after the Champion Room 9 is the other version's room, so the legend sleeps on its own
// element as in its own game: Sapphire shows Ruby's lava basin with Groudon on it, Ruby Sapphire's water pool with Kyogre
// in it. The zone's other layout (data/cave_layouts/SeafloorCavern_Room9.json "alt_rooms": SeafloorCavern_Room9_Ruby in
// Sapphire, SeafloorCavern_Room9 in Ruby; b2tools/patches/interiors.py) is loaded while map replace event 0 is set (work
// 0x4031, Emerald's Route 111: Sapphire and Ruby never use it). The zone init sets it on entry only, never while the player
// is inside: on every entry (warp, Continue) it compares the event with the game-clear flag and only when they differ
// sets it and reloads the zone's matrix (Sky Pillar's floors' way). A save inside the room keeps the event with it, so it
// loads the same layout. Before the Champion and in a new game the event stays clear: the room as it always was. Both
// layouts are the same map (pokeruby's one Room 9, two block sets) outside the basin (x 12-23, y 31-42), so every person,
// item and trigger fits both; the legend's tile (17,38) is in the basin in both (water / lava, as each game had it).
// Stepping on (17,42), the tile of the story's scene, wakes it: its cry twice (it stays on its tile: the basin is solid
// lava in one layout and water in the other, no walking), the legendary battle at Lv 49 (Gen 3's 45 on
// data/level_scaling.json's curve, as B4F's). Caught: gone. Knocked
// out, ran or lost: gone until the next Hall of Fame (0114 clears FLAG_DEFEATED_OTHER_LEGEND; the zone init shows it again),
// with Gen 3's own line of that version's Cave of Origin B4F ("Groudon appears to have settled into sleep again...").
// No orb glow: this version's orb is not the one this legend answers to.
// Objects (data/story/postgame.json): the legend uid 8 (Black 2's Groudon / Kyogre model: MODEL_KYOGRE_OR_GROUDON), hidden
// by map-local flag 0x58, and the trigger at (17,42) on VAR_TEMP_1 (0x4001) = 1. Both are set by this zone init only
// (flags 0-0x63 and works 0x4000-0x401F are cleared on every map change: Route116.inc's tunneler uses a local hide flag
// the same way). Both skip_emerald: Emerald NDS has both legends already (Marine / Terra Cave), so in an Emerald build
// the two entries below do nothing.
// Included by 0380_room_SeafloorCavern_Room9.s (entry 4, R9_Init's call). Text: line 14 of src/text/script/0248_* (ruby/).
#define R9_OTHER_LEGEND 8
#define R9_OTHER_LEGEND_LEVEL 49        // Gen 3 45 (pokeruby CaveOfOrigin_B4F, the legend's level) on the curve
#define R9_TEMP_TRIGGER 0x4001          // VAR_TEMP_1 (data/story/postgame.json's trigger)
#define T_OtherLegendSettled 14         // Gen 3's CaveOfOrigin_B4F line of the other version
#define R9_FLAG_HIDE_OTHER_LEGEND 0x58  // map-local: set by the zone init unless the legend is shown
#define R9_EVENT_OTHER_LOOK 0           // map replace event of the other version's layout (data/interiors/190.json alt_rooms)
#define R9_TMP 0x8000

#ifdef HOENN_EMERALD
PG_R9_Init:
    VMReturn
PG_R9_OtherLegend:
    VMHalt
#else
PG_R9_Init:                             // (zone init) the room's look, then the legend
    MapReplaceIsEventSet R9_EVENT_OTHER_LOOK, R9_TMP          // after the Champion: the other version's layout (above)
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_PGR9_OtherLook
    h_goto_if_eq R9_TMP, 0, L_PGR9_Legend
    MapReplaceSetEvent R9_EVENT_OTHER_LOOK, 0, 1              // (the zone's matrix is loaded already: reload it)
    VMJump L_PGR9_Legend
L_PGR9_OtherLook:
    h_goto_if_eq R9_TMP, 1, L_PGR9_Legend
    MapReplaceSetEvent R9_EVENT_OTHER_LOOK, 1, 1
L_PGR9_Legend:                          // shown after the Champion while neither caught nor met since the last Hall of Fame
    FlagSet R9_FLAG_HIDE_OTHER_LEGEND
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_PGR9_InitDone
    h_goto_if_set FLAG_CAUGHT_OTHER_LEGEND, L_PGR9_InitDone
    h_goto_if_set FLAG_DEFEATED_OTHER_LEGEND, L_PGR9_InitDone
    FlagReset R9_FLAG_HIDE_OTHER_LEGEND
    h_setvar R9_TEMP_TRIGGER, 1
L_PGR9_InitDone:
    VMReturn

PG_R9_OtherLegend:                      // trigger (17,42) while R9_TEMP_TRIGGER is 1 (CaveOfOrigin_B4F_EventScript_15DDD7's shape)
    c10_lock
    h_setvar R9_TEMP_TRIGGER, 0
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_waitse
    h_playmoncry SPECIES_KYOGRE_OR_GROUDON
    h_delay 40
    h_waitmoncry
    h_delay 60
    h_waitse
    h_playmoncry SPECIES_KYOGRE_OR_GROUDON
    h_delay 40
    h_waitmoncry
    FlagSet R9_FLAG_HIDE_OTHER_LEGEND      // (the object is gone after the battle whatever happens)
    h_setflag FLAG_DEFEATED_OTHER_LEGEND                // (lost, ran or knocked out: back after the next Hall of Fame)
    CallWildBattle SPECIES_KYOGRE_OR_GROUDON, R9_OTHER_LEGEND_LEVEL, 1
    WildBattleIsVictory C10_A
    WorkCmpConst C10_A, 1
    VMJumpIf CMP_EQ, L_PGR9_Continue
    CallWildLose
    VMHalt
L_PGR9_Continue:
    ActorDelete R9_OTHER_LEGEND
    CallWildBattleEnd
    WildBattleGetResult C10_A           // 0 caught, else knocked out or ran
    WorkCmpConst C10_A, 0
    VMJumpIf CMP_NE, L_PGR9_NotCaught
    h_setflag FLAG_CAUGHT_OTHER_LEGEND
    h_release
L_PGR9_NotCaught:
    h_msgbox_info T_OtherLegendSettled  // Groudon (Ruby's line) / Kyogre (Sapphire's) appears to have settled into sleep again...
    h_closemessage
    h_release
    .balign 4, 0
#endif
