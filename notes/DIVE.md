# Dive and the maps behind it (dive agent, 2026-10-06/07)

Sapphire's Dive rebuilt on Black 2's own Dive (Undella Bay -> Abyssal Ruins), plus every map only Dive reaches:
the underwater maps, Seafloor Cavern, the Sealed Chamber, the Abandoned Ship's hidden floor.
Tags: **[code]** decomp/disassembly, **[bytes]** measured in the dump, **[test]** seen in DeSmuME.

## How it works
| Piece | Black 2 | Hoenn (b2tools/patches/dive.py) |
|---|---|---|
| Where you may dive | GetAbyssalRuinsDiveZoneID (ov036 0x021C3D50) -> 4 entries (zone, x, z, dest), each a 3x3 square of Undella Bay (0x021D2540) **[code][bytes]** | the two functions replaced by one with the same interface (zone in; BOOL + zone out); its 3 callers re-pointed (A button: FieldEventProvider_Grid_CheckForEvent 0x021816D2; party menu: CalcPlayerActionPossibilities ov012 0x02159344; EventDiveIn_Callback ov033 0x02179F94) |
| The table | in ov036 | a file of a/1/2/6 (zone 241's entity file, 297: replacing a file keeps the archive's section offsets, which the field's open handle caches; an appended file failed its fileCount assert after a state load **[test]**), read on demand through EventData->entityArc + GFL_ArcToolReadRange: u16 per zone (record offset/16 << 4 | count), 16-byte records (x0, z0, w, h, dest zone, ax, az, tile-map offset, flags), a byte per tile. 1 read in a zone without dives, 3-4 with |
| Where you arrive | the dest zone's spawn (LoadZoneSpawnInfoCheckRail) **[code]**, then EventDiveIn walks you 1 tile up (actor command 8) **[code][test]** | the tile under you (Sapphire's "dive" connection: same coordinates) or Sapphire's fixed setdivewarp spot: the lookup writes VAR_HOENN_DIVE_X/_Z/_ZONE (works 0x411D-0x411F, data/story_ids.json), a hook in EventMapChangeDiveIn_Create (ov035 0x0217DE10 -> ov033 0x02179E98) puts the spawn there, and the walk-up is command 0 (face up) (ov033 0x02179FB6) **[test: arrival tiles exact]** |
| Surfacing | a script: FieldSetNextZone + CallDiving 1 (Abyssal Ruins 0482.s Script_3) **[code]** | the same lookup over the underwater zones' surfacing tiles (Sapphire: not MB_NO_SURFACING 0x19 / MB_SEAWEED_NO_SURFACING 0x2A); global scripts 10011 (A) / 10012 (party menu) see PlayerGetExState 3 and surface with FieldSetNextZone from the works + CallDiving 1 (b2tools/patches/hm_free.py) **[test]** |
| Messages | Black 2's | Sapphire's five lines (src/text/script/0433.txt 37-41): "The sea is deep here...", "Light is filtering down from above..." |
| Underwater movement | the diving player (special state 3) uses the Surf handlers on grid maps (FieldPlayerGrid_DecideCommand / _UpdateCore jump tables, states 2 and 3) **[code]**; Abyssal Ruins' swimmable cells are class 0x9C flags 0x02 (zone 245, chunks 560-610) **[bytes]** | every walkable underwater tile 0x9C/0x02, seaweed 0x9C/0x06 (encounter bit: FieldEncount_DecideTypeByTerrain gives surf encounters, a wild Clamperl in Underwater1 **[test]**) |
| Doors underwater | a surfing/diving player's warps fire when bumping into a wall (FieldPlayerGrid_UpdateSurfBrake -> CheckWarpAtHitWall) **[code]**; stepping onto a walkable warp tile does not **[test]** | Sapphire's water doors (MB_WATER_DOOR, notches in a north wall) = solid tiles with a warp walked into northwards (caves: Black 2's cave arch; ship: a door tile); water arrows (MB_WATER_SOUTH_ARROW_WARP) = the cave builder's arches / exit-mat warps **[test]** |
| Underwater look | AbyssalRuinsCmd_StartUnderwaterEffect (script plugin 5, zones 241-245) draws ov126's three models (bubbles, a light disc, haze walls) **at world (256, 0, 256)**: the Abyssal descent's bowl **[code][bytes]** | plugin 5's zone list moved onto the Black Tower's 12 slots (DENY zones; the Black Tower entry gets count 0) with the 10 underwater zones; only the one-chunk maps (Underwater_SootopolisCity, _SeafloorCavern, _Route134, _SealedChamber) run it (centred on (16,16)); the big maps and the ship rooms don't (the bowl would stand in one place) |
| HM rules | | hm_free's: Dive needs the Mind Badge (7) and a Pokémon with Dive or HM06 |
Code space: the two old functions (140 B), UpdateAbyssalRuinsSteps (68 B, its call now returns 0: it counted steps in
zones 245-248 only), the old table (32 B), CheckAbyssalRuinsStepEvent (ov033, 108 B). Sizes: lookup 138/140, hit tail
48/68, read helper 28/32, spawn hook 52/108.
**Savestates**: the patch changes ov012/ov033/ov036's compressed sizes (FAT ends of overlays 12, 33, 36): work/emu
states made without `dive` read stale overlays after a map change; remake them with `dive` in the list. My tests used
my own states (work/agents/dive/tools/make_states.py -> work/agents/dive/states, a ROM without test patches).

## Sapphire's dive spots -> underwater areas
| Sapphire map (dive tiles 0x11/0x12/0x14) | Underwater map | How |
|---|---|---|
| Route 124: 188 tiles in 16 patches | Underwater1 (80x80: 902 swimmable tiles in 10 trench regions, 188 surfacing tiles under the 16 patches) | same tile both ways |
| Route 126: 1,349 tiles in 6 patches (the ring around Sootopolis is 1,213) | Underwater2 (1,468 swimmable, 4 regions; water door (45,65) -> Underwater_SootopolisCity) | same tile |
| Route 127: 1,036 tiles in 6 patches | Underwater3 (1,101 swimmable, 7 regions) | same tile |
| Route 128: 491 tiles in 3 patches | Underwater4 (492 swimmable; water door (38,26) -> Underwater_SeafloorCavern) | same tile |
| Sootopolis City: 19 tiles (24-32,53-55) | Underwater_SootopolisCity (9,6); surfacing -> Sootopolis (29,53) | fixed (setdivewarp) |
| Route 134: 12 tiles (59-62,30-33) | Underwater_Route134 (8,6); its arrow (8,8) -> Underwater_SealedChamber; surfacing -> Route 134 (60,31) | fixed |
| Sealed Chamber outer room: 6 tiles (9-11,18-19) | Underwater_SealedChamber (12,44); surfacing at (12,44) -> the outer room (10,19), anywhere else -> Route 134 (60,31) | fixed |
| Seafloor Cavern entrance: 16 tiles (7-12,16-18) | Underwater_SeafloorCavern (6,5); surfacing -> the entrance (10,17) | fixed |
| Abandoned Ship Rooms_B1F: 4 tiles (12-14,6-7) | AbandonedShip_Underwater2 (17,4); surfacing -> Rooms_B1F (13,7) | fixed |
| Abandoned Ship hidden corridor: 3 tiles (0-1,9-10) | AbandonedShip_Underwater1 (5,4); surfacing -> the corridor (0,10) | fixed |
Routes 131/132/133, the Aqua/Magma hideouts and Cave of Origin B4F have dive tiles but no dive warp in Sapphire: no Dive
there (as Sapphire). The overworld already draws every one of them as deep water (terrain/water.py deep_water); no
world change was needed (Route 134's westward currents stop on its dive spot, as Sapphire's).

## What differs from Sapphire
- Sapphire surfaces with **B**; Black 2's field only looks for events on A (FieldEventProvider): surfacing is **A** on a
  surfacing tile (or Dive from the party menu), with Sapphire's prompt.
- Without the badge Sapphire says nothing on a dive spot; hm_free's scripts give the "may be able to go underwater"
  line (the same as without a Pokémon).
- Seafloor Cavern rooms 6/7: Sapphire's currents work (Black 2's current cells 0x94-0x97, as the overworld's) but are drawn
  as plain cave water (Black 2's caves have no current art).
- The underwater maps are built from Sapphire's walkable tiles; the raised seabed is one 16-unit tier (two in the small
  nooks), seaweed = the Marine Tube's coral, Sapphire's sunlit dive circles = its sunlight net.

## The maps (zones from converter/allocate_interiors.py, which now follows Dive links; status cave)
| Map | Zone | Built with | Notes |
|---|---|---|---|
| Underwater1-4 | 216-219 | cave builder, look `uw`, recipe `underwater`, 3x3 / 4x2 chunks | encounters: Underwater1/2 Sapphire's (files 91/92) |
| Underwater_SootopolisCity / _SeafloorCavern / _Route134 / _SealedChamber | 223 / 221 / 220 / 222 | same, two tiers, origins centring the nook on (16,16), underwater effect | |
| SeafloorCavern_Entrance, Room1-9 | 177, 179, 183-190 | cave builder, look d0 (Room6/7 `currents`, Entrance `shoals`) | boulders = caves_east's 1x1 boulder (patch boulder_1x1); rocks = hm_free 10016; encounter files shared with identical Sapphire tables (Rooms 1-5/8 = 51, 6/7 = 94, Entrance 93) |
| SealedChamber_OuterRoom / InnerRoom | 215 / 204 | cave builder, d0 | braille = story |
| AbandonedShip_HiddenFloorCorridors / _HiddenFloorRooms | 173 / 174 | room builder via b2tools/dive_rooms.py (ship_hideouts' generator as a library, Royal Unova look) | corridor water pool (dive spot); 3 item balls |
| AbandonedShip_Underwater1 / _Underwater2 | 175 / 176 | the same; recipe `water`: `cell` [0x9C, 2], `y` 0, `draw` false; floor = the sunlight net | diving music |
Look `uw` (data/cave_layouts/_looks.json): area 340 (Abyssal Ruins: lights, diving player, header of zone 241: SEQ_BGM_DIVING,
battle background 8), Marine Tube textures merged in (`tex_sets`: h06soko01 seabed, h06suna01 sand, h06gake01 rock,
h06sango2 coral, h06nami01 sunlight, h06kuro). Every chunk is under 110,600 bytes (largest 51,704, Underwater1 chunk 4).

## Builder keys added (all opt-in; the 217 rooms and 32 other caves build byte-identically, checked)
- models_cave.py: hooks to b2tools/models_cave_uw.py (`underwater`, `currents`), look keys `no_void` (rock tops over the
  whole map and matrix instead of rim + black) and `tex_sets` (textures from other Black 2 sets).
- models_interior.py: `water` `cell` / `draw`.
- converter/gen_caves.py: underwater maps get field-load/return map scripts with the underwater effect (`uw_effect`
  false: none); identical Sapphire wild tables share one encounter file (a/1/2/7 has no free files left); the wild
  table is looked up by the map's own id (upper_map turned Underwater1 into MAP_UNDERWATER_1).
- converter/allocate_interiors.py: a second pass follows Sapphire's dive/emerge connections and setdivewarp targets
  (existing entries unchanged).
- converter/gen_story_ids.py: keeps engine ids claimed by hand (a rerun dropped caves_misc's 0x4039/0x403A).

## Build and test
    HOENN_AGENT=dive zsh b2tools/dive_build.sh [MAP ...]     (zone files, maps, ROM: the full patch list + dive)
    DV_PATCHES="boulder_1x1 test_cave_kit" HOENN_TEST_WARP=zone,x,z HOENN_TEST_NO_WILD=1 HOENN_TEST_NO_WILD_SURF=1 ...
    cd b2tools && STATE=../work/agents/dive/states/base_littleroot.dst ../.venv/bin/python ../work/agents/dive/tools/dtest.py ROM OUT.png MOVES
dtest.py = cave_test.py + `V<x>,<z>,<D>` (calibration by a probe step: after a dive the lowest RAM copy of the arrival
tile is a stale spawn record) + `H` (count copies of tile positions). After HOENN_TEST_WARP the A button does nothing
until a real warp: start next to a door (Route 124's Treasure Hunter's house 571,4,8; Corridors_B1F 73,9,6; Seafloor
entrance 177,10,3; Sealed Chamber 215,10,4). Tested end to end: Route 124 dive / trench swim / surface at the other
spot; Route 126 -> Underwater2 water door -> Underwater_SootopolisCity -> surface in Sootopolis; Seafloor entrance ->
Room1 and back, dive -> Underwater_SeafloorCavern -> arch -> Underwater4 -> surface on Route 128; Sealed Chamber outer ->
inner -> dive -> surface back at (10,19); ship cabin dive -> Underwater2 -> door -> Underwater1 -> surface on the hidden
floor; a wild Clamperl in Underwater1's seaweed. Proofs: screenshots/dive/.

## Story content left (listed by gen_caves / dive_rooms; the story agents')
Kyogre's awakening (Room9: Kyogre, Archie, grunts, FLAG_HIDE_*_SEAFLOOR_CAVERN), the Seafloor grunts (Room1/3/4, VAR_1/VAR_2
sprites), the submarine (Underwater_SeafloorCavern: Sapphire's map tiles + FLAG_HIDE_UNDERWATER_SUBMARINE_INTERACTION,
its walls after FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN), FLAG_LANDMARK_SEAFLOOR_CAVERN / _SEALED_CHAMBER; the Sealed Chamber
braille (6 + 6 signs), the entrance cover until FLAG_SYS_BRAILLE_DIG (the door to the inner room is open now), the
Relicanth/Wailord check (FLAG_REGI_DOORS_OPENED) and its escape warp; the ship's room keys (hidden items), locked doors
of rooms 1/2/4/6 and their key signs, the key sparkles, the Scanner (key item, not an item ball here); hidden items on
the underwater maps (7 + 8 + 4 + 2, Black 2 hidden items not placed).

## Deep-water look (underwater_polish, 2026-10-08) [bytes][test]
The uw look's `depth` keys (b2tools/models_cave_uw.py `Depth`; only the 8 underwater maps use look `uw`). What Black 2
does for deep water: vertex colours, not a darker texture - the Abyssal Ruins' seabed (zone 241, chunk 555) is in59_sand
at (0, 0.77, 1.0) in the lit middle, (0, 0.45, 0.81) further out, (0, 0.13, 0.26) at the bowl's edge; the Marine Tube's
light rays are pack 61's h06_light01/02 (slanted translucent quads seabed -> surface, 56 wide at the bottom, 32 at the
top, leaning 52-84 units west, cyan-white, brightest at the top). Now:
- raised seabed = in59_sand (set 340, the area's own) shaded (0, 0.46, 0.82) at the trench lip fading to (0, 0.24, 0.46)
  96 units out (Euclidean distance to the nearest trench tile, smoothstep), and to black over the last 64 units before
  the matrix's edge (past it the screen is black, as Black 2's cave rims fade to black); was the pale h06suna01.
- trench floors and walls take their brightness from Sapphire's own art: each walkable tile's metatile luminance
  (pokeruby tileset, 9..100 -> 0.5..1.0, gamma 1.4; seaweed tiles take the floor around them; 3x3 average) - Underwater3/4
  and the Sealed Chamber come out deep navy as in Sapphire, Underwater1/2 mid blue with lit dive circles; walls run from
  the floor's value at their foot to 0.8 x (0.7, 0.9, 1.0) at the lip. Triangles are split on a 32-unit grid only where
  the colour is not linear over them (both sides of a split diagonal/sloped edge: no T-junction cracks off the grid).
- Sapphire's lit tiles (luminance >= 90, its 0x16/0x28 light-streak metatiles): Black 2's underwater caustics
  in59_light_a (translucent) 2 over the floor, (0.6, 0.9, 1.0), 48 units a repeat (was the opaque h06nami01 net); one light
  ray per 5 tiles of them: the Marine Tube's shape (two strips 32 -> 18 wide, 128 high, leaning ~48 west) with
  in14_light_a's gradient, clear at the floor and at the top, brightest half way (the field camera has the top off screen),
  colour (0.72, 1, 1); none at an arch or south of a north-wall door within 9 tiles (in front of its tunnel).
- seaweed: h06sango2 plants, 22 units on every other tile of the checkerboard where all 8 neighbours are floor (4 over
  the floor), 14 on the others (6 over), turned/mirrored/placed/shaded per tile, tinted (0.82, 0.95, 0.86) x the floor.
- trenches that run into the Sapphire map's edge (Underwater3 south/east, Underwater4 north) get a cliff there (the
  background showed through). Sapphire joins Underwater3's south edge (29-36,79) to Underwater4's north edge (29-36,0)
  (map connection "down"/"up"): joined since final_check (below).
Chunks: largest 78,968 B (Underwater2 chunk 3; was 63,288). caves_check abcefhistwx on the 8 maps: 0 before, 0 after.
Proofs: screenshots/underwater_polish/ (01-03 dives at the Seafloor Cavern entrance, the Sealed Chamber, Route 124;
04 warp views; 05 save + Continue in Underwater1; 08 renders of every map, HEAD look | new).

## Underwater3 <-> Underwater4 (final_check, 2026-10-08) [code][test]
Sapphire's "down"/"up" connection between the two trenches (x 29-36) was a dead end. Now a recipe key `links`
(data/cave_layouts/Underwater3.json / Underwater4.json; b2tools/models_cave.py spots, converter/gen_caves.py warps after
Sapphire's): one type-4 warp 8 tiles wide on the row past each map's edge, walked into. A diver's warps fire on bumping a
wall (FieldPlayerGrid_UpdateSurfBrake -> CheckWarpAtHitWall -> GetWarpIDByPlayerPos: the tile in front), the arrival walks
one step in, and a wide warp keeps the column (ZoneWarp_CalcPosWeightBitsGrid / GetGridWarpOutPos / CalcWarpTransferAddend,
ov012 eventdata_system.c: same width, opposite directions = same index). The warp row must be inside the matrix (warp x/z
are u16), so the origins moved: Underwater3 [0, 15] (its south edge 16 units from the matrix's, the trench fades into
the dark there as Underwater4's north end always did), Underwater4 [0, 1]. Dives, surfacing and the hidden items follow
room.json's origin (patches/dive.py frames(), story.py). Tested (screenshots/final_check/01_underwater3_4_link.png): dive
on Route 128 (31,8), swim north from Underwater4 (32,0) -> Underwater3 (32,79), back south -> (32,0); columns 29 and 36
both ways; surface at Underwater3 (32,79) -> Route 127 (32,79) and dive back. caves_check abcefhistwx on the 8 underwater
maps: 0; rooms_check counts unchanged. Largest chunk Underwater4 68,112 B.

## Trench outline, seaweed (map_glitch_fix, 2026-10-09)
Look 'uw' keys (models_cave.py lattice_diag / cell_quad / flat_rect / face_uv; models_cave_uw.py): 'outline': 'diag' -
L1 distance (45-degree contours) and wedges cut into rock tiles at floor corners (legs 16, or 10 when a tile has several),
floor drawn there (the walls stepped along the tile grid: 88% of Underwater1's wall edge on the axes, 127 right-angle
corners); face cells split along the true crease (588 flat corner ledges in Underwater1 gone); 'face_uv' [96, 48] one wall
texel density up the slope (the top band was squeezed into a streaky rim); depth 'kelp_style' 'stand' - two cards a seaweed
tile leaning back 30 degrees as the Marine Tube's props, tinted darker than the floor, 3+ units apart (the flat bright
coral cards read as floating squares); rays 'foot_on_floor'; depth 'backdrop' - a deep blue sheet 2 under the floor
(pixel seams at T-junctions showed black); depth grid [32, 64]. All 8 underwater maps; largest chunk 95,920 B (nsbmd,
Underwater2). caves_check abcefhistwx on them: 0. Collision unchanged.
