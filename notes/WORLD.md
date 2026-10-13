# The Hoenn world build (from 2026-10-06)

All of Hoenn's connected overworld goes on **one matrix (416, appended to a/0/0/9)** with **one exterior area (2)**
(decision 2026-10-06; why: notes/RESEARCH_WORLD.md). Unova's matrix 0 and chunks stay untouched.

## Pipeline
    b2tools/rebuild_slice.sh      (plans -> world.py -> ToNsbmd per cell -> buildings -> textures -> ROM)

- `data/hoenn_world.json`: which maps are built, their B2 zone, floor type (town/route), and how their Sapphire
  events map onto B2: door warp slots (Sapphire dest map -> warp index in the zone's entity file), building models
  (res id in pack 0 + front offset), sign scripts/models, NPC scripts/sprites. `pad_north` / `shift` hold Route
  101's 12 extra rows and Littleroot's matching shift (safe: they are a dead-end branch below Oldale).
- `data/hoenn_world_layout.json`: every outdoor map's position on one global grid, from Sapphire's own connections
  (research agent; 49 maps form one consistent 800×380-tile world, 16 more are reached by warps).
- `b2tools/world.py`: composes the built maps on the grid (+1 cell margin), builds every cell with map tiles plus a
  ring of forest cells (`work/world/cells/<cx>_<cz>/`), assigns each cell the zone with most tiles in it, and writes
  `work/world/world.json` (cells, chunk ids from 1065, per-zone signs/NPCs/warps/fly point/park spot).
- `b2tools/patches/hoenn_world.py`: appends the chunks and the matrix, points the zones' headers at matrix 416 /
  area 2 / the fly point, rewrites the zones' entities.

## Coordinates
World tile = layout tile + 32 × margin. Today: Oldale cell (5,9), Route 101 (5,10), Littleroot (5,11); the player
arrives from the test door at (173,361). Tests: `walk.py ... C173,361 T<x>,<z>`.

## Mixed cells and events
A cell holding several maps gets the zone of the one with most tiles (a town wins any cell it is in), but since
2026-10-08 every map has its own zone on all of its tiles (zone rectangles, "Sub-cell zones" below): banner, music,
wild table and people change at Sapphire's map edges, and every event of a map (doors, signs, people, trainers, item
balls, hidden items, berry spots, triggers) sits in the map's own zone, so its script belongs in the map's own script
file. Only tiles of no map (the forest ring, open sea between maps) keep their cell's zone. world.py warns when a
map's sign lands in another zone (none now).

## Limits to check as Hoenn grows (RESEARCH_WORLD.md)
Matrix ≤ 900 cells; each chunk ≤ 110,600 B; zones < 615; ≤ 128 models in the building pack; map + building
textures of the area ≤ ~200 KB (measure VRAM at 0x02141a54).

## World fixes (world_fixes agent, 2026-10-06)
Tags: **[code]** decomp, **[bytes]** dump/built files, **[test]** DeSmuME (proofs: screenshots/world_fixes/).

**Door heights.** Black 2 fires a warp only when the player's y is within 2 units of the warp's (ov012
eventdata_system.c CheckWarpPositionMatch; GetWarpIDByPlayerPos tests the tile in front at the player's own y) and
puts an arriving player at the warp's y (GetGridWarpOutPos) **[code]**. world.py `door_heights` (after the cells are
written) gives every door and door slot the collision height of the tile it is walked into from (DOOR_STEP by the
warp's dir), read back from the written collision.per. Changed (all others keep theirs, checked against HEAD's
world.py on the same data): Lilycove -> Aqua Hideout 0 -> -8, Route 120 -> Scorched Slab 32 -> 24 (pond),
Route 125 -> Shoal Cave 0 -> -8 (shoal), Route 115 -> Meteor Falls 0 -> 32 (plateau), Route 108 -> Abandoned Ship
0 -> -8, Route 131 -> Sky Pillar keeps 0 (the post-game sand). A door whose Sapphire tile lies outside its map
keeps its y (Slateport's harbour warp at x 40 of a 40-wide map, unreachable in Sapphire). All tested **[test]**.

**Route 108's Abandoned Ship** (b2tools/terrain/ship.py, module "ship" in data/terrain_modules.json): drawn into
the Route 108 cell's terrain in Sapphire's shape with Black 2's ferry texture c13ship_01 + glass h_mado (exterior
building texture set 46; a module TEXTURES value 'ext<N>' = a/1/7/4 entry N, merged into set 3 by hoenn_textures,
+2,264 B). A module `retile(world, maps)` hook (world.py main, after compose) makes the hull tiles unsurfable sea
and Sapphire's stairs tile (29,6) a shoal landing (water.py: MB_STAIRS_OUTSIDE_ABANDONED_SHIP 0x1B is shallow
flowing water in Sapphire too); world.py puts the door on the hull tile north of it. Surf -> landing -> deck ->
landing -> surf off **[test]**. Not a pack-0 building: pack 0 is at the field-heap limit (TOWNS_TOWNS5.md).

**Other layouts of a map** (data/hoenn_world.json "alt_layouts"; Sapphire's setmaplayoutindex). Route 131 swaps in
layout 320 (the Sky Pillar islet, its door (36,6)) once FLAG_SYS_GAME_CLEAR is set. world.py `build_alts` builds the
world again with that layout (converter/plan_map.py LAYOUT OUT.json; `sapphire_layout` makes heights/water/ground/
behaviours read it; the sea outside the maps stays the main world's) and keeps the cells that differ
(cells/alt_<map>_<cx>_<cz>: (17,9), (18,9), (17,10), (18,10), 160,576 B of chunks; world.json "alt_cells").
patches/hoenn_world.py appends them after every other chunk and adds a/0/1/0 entries (matrix 416, kind 0 = swap one
chunk id, condition 10 = event uid 7 = work 0x4038 == 0x408: no Black 2 script or entry uses it; data/story_ids.json
WORK_MAP_REPLACE_7_SKY_PILLAR). Black 2 applies them when a matrix loads (ov035 FieldMapControl_LoadZone ->
MapMatrix_Patch) **[code]**, so **the game-clear scene must run `MapReplaceSetEvent 7, 1, 0`** where it sets
FLAG_SYS_GAME_CLEAR; Route 131's zone init (scenes/Route131.inc, Sapphire's OnTransition) also sets it and reloads
(as Shoal Cave's tide) when you warp/fly into Route 131. Tested: not cleared = open sea; cleared = islet, door ->
Sky Pillar entrance -> back **[test]**. The door's y comes from the alt cells; in the normal layout a surfer (-8)
can't trigger it (y 0). b2tools/navgrid.py ignores alt_* cells.

**More other layouts (postgame_maps, 2026-10-07; notes/EVENTS.md "Post-game maps").** Route 130 (Mirage Island, event 2) and
Route 103 (Altering Cave mouth, event 7) after Route 131 (their chunks follow its, no chunk id moves). An alt layout may be
a pokeruby layout plus edits (data/hoenn_map_additions.json "layouts", converter/gba.py; sapphire_layout reads it through
gba.Repo), and data/hoenn_map_additions.json "events" adds events to a pokeruby map (Route 103's warp to Altering Cave).
alt_layouts keys: `retile` by "tiles" as well as "box"; `heights_box` (map tiles): only there may heights differ from
the main layout. Checked: the main cells are byte-identical to HEAD's; the alt cells differ from the main ones only
inside the island box / the mouth box.

**Banners / zones inside a cell.** Black 2 has one zone per matrix cell (format-1 matrix, ov012 map_matrix.c
GetZoneIDAtMatrixXZWorld) and swaps zone on the first move into a cell with another zone id (ov036 fieldmap.c
Field_ShouldSwapZone / Field_SwapZoneByMatrix: entities, BGM, weather, camera box, place-name banner; 0xFFFF cells
keep the current zone) **[code]**. No sub-cell override exists in its data or code; Unova's own towns and routes
meet at cell edges (gates, 0xFFFF scenery cells). Spots where a warp lands in another zone's cell (world.json
"foreign" doors): Granite Cave's mouth (Dewford), Fiery Path south and Jagged Pass (Lavaridge), Fiery Path north
(Route 113), Route 117's Day Care (Mauville), Route 124's house (Mossdeep), Mr. Briney's cottage (Petalburg), and
Slateport's unreachable harbour warp (Route 134, outside its map: left as it is). User decision: the code patch.

**Sub-cell zones (the banner code patch, 2026-10-07; every map since 2026-10-08).** world.py `zone_rects`: every map
gets its own zone on all of its tiles in other zones' cells (with its pad rows), one rectangle (map rectangle x cell)
per such cell, `[x0, z0, x1, z1, zone]` in world tiles (world.json "zone_rects": 73 on the Hoenn matrix; until
2026-10-08 only the 14 of the maps with a door in another zone's cell: Route 104, 106, 112, 117, 124).
world.py `zone_at` and the converters' zone lookups (gen_map_content, gen_encounters, gen_trainer_npcs: `W.zone_of`)
use them, so those maps' doors, signs, people, trainers and wild tables sit in their own zone and the "foreign" door
copies are gone. patches/hoenn_world.py `apply_code` puts the table and a Thumb `ZoneLookup` into ITCM and makes
GetZoneIDAtMatrixXZWorld (ov012 0x02154af0, the only reader of the matrix's zone ids: callers ov036 Field_ShouldSwapZone,
Field_SwapZoneByMatrix, UpdatePhenomenon, ov086 0x021eab88 [code]) call it: a tile in a rectangle on the Hoenn matrix
gets the rectangle's zone, every other position the cell's as before (it calls the original GetChunkCoordOfWorld and
GetZoneIDAtMatrixXZ). The swap (banner, BGM, people, encounters, weather, camera box) then happens at the map's own
edge, and a warp into a rectangle arrives in the right zone with no swap on the first step.
- Code space [code][bytes][test]: the ITCM autoload (itcm.yaml: 0x01FF8000, 5024 bytes, no bss) leaves 27 KB of the
  32 KB ITCM to the SDK's ITCM arena (arena 3; default start = literal 0x01FF93A0 at arm9 0x0207B400, read by
  GetUserMemRegionDefaultStart). Black 2 never allocates from it: every mem_init_alloc_area / mem_alloc_direct /
  malloc_device call passes arena 0 or 4; no relocation in any module points past 0x01FF939C and no code binary holds
  another word in 0x01FF93A0-0x01FFFFFF (ov012/ov180/ov182's 0x01FFFFxx words are masks). The autoload grows by
  242 B (code 100 + table), the arena literal moves past it (0x01FF94A0). Checked on a cold boot: the code is in ITCM
  at the title, through the opening and in Littleroot (dsd writes the autoload table from itcm.yaml).
- The hook keeps the old body after it, so ov012 compresses to its old 512-byte slot (+8 B); arm9 grows inside its
  padding: no ROM file moves. **But savestates made before it hold an ITCM without the code**: remake the base states;
  a state from an unpatched ROM crashes when something reloads ov012 (a battle, a warp into another overlay set).
- Tested on a cold-booted state of the patched ROM and with the code poked into older states (screenshots/world_fixes/
  banner_zones.png): Granite Cave -> "Route 106" (Dewford's banner only on entering Dewford, "Route 106" walking back),
  Fiery Path south and north exits, Jagged Pass -> "Route 112" (Lavaridge's banner at x 207/208 both ways), Day Care ->
  "Route 117" (Mauville's at x 248), Route 124's house -> "Route 124", Mr. Briney's cottage -> "Route 104".

**Route 131's post-game islet in brown rock** (user decision): data/hoenn_world.json alt_layouts Route131 "retile"
turns the islet's cliff/cliff-top/summit tiles (box (26,0)-(46,6)) into heights.py mountain: Black 2's brown rock
(gake_michi tops, gake1_0 lips, yamagake01 faces, terraces), the cave door at its foot, the beach in front. The alt
world keeps the main world's heights outside the maps (its raised edge had lifted the open sea north of it).
Tested in game: screenshots/world_fixes/route131_islet_brown.png.

**Acro Bike spots (one bike: user decision 2026-10-07).** Sapphire closes its Acro Bike tiles to a player on foot
(pokeruby field_player_avatar.c check_acro_bike_metatile: MB_BUMPY_SLOPE 0xD1, MB_ISOLATED_VERTICAL/HORIZONTAL_RAIL
0xD3/0xD4, MB_VERTICAL/HORIZONTAL_RAIL 0xD5/0xD6). All of them in Sapphire's maps (scan of every map's metatiles):
Jagged Pass 14 bumpy slopes (5 columns through its ledge bands), Route 119 51 rail tiles (34 horizontal, 14 vertical,
7 isolated: the river crossings north of the Weather Institute and at rows 91-94), Safari Zone northeast 3 bumpy slopes
(a 32-unit climb), Safari Zone southeast 13 rails. terrain/ground.py now walks them: rails are concrete decks (hashi02a,
the white of Sapphire's rails, Route 8's bridge recipe) with thin posts in the water under them (Sapphire's support
tiles; water drawn under, ground.water_under); bumpy slopes are low iwa01 stepping stones on walkable floor (Jagged
Pass: its ledge bands keep level, so a column is a gap in the ledge line, as Black 2 leaves a gap where a path goes on);
a column that joins two levels (Safari northeast) becomes stairs (ground.retile -> heights.py's 45-degree kaidan01a
steps). Tested in game (screenshots/world_fixes/acro_bike_spots.png): up Jagged Pass from Route 112 to Mt. Chimney,
across both Route 119 crossings to the item at their south end, the Safari Zone's southeast rails and northeast stairs.

## Fixed weather (weather agent, 2026-10-07; data/hoenn_weather.json, b2tools/patches/fixed_weather.py)
Tags as above; proofs: screenshots/weather/.
- **How Black 2 sets weather [code]**: one weather per zone, header 0x1C bits 0-5 (GetZoneEnvFlagsWeather), asked by
  GetWeatherAll (arm9 0x02032e94: stub, Entralink hook = ch10's Kyogre patch, Route 7, birthday, the calendar a/0/9/6
  only while the save's season is the real one and only for its zones, else the header). Every zone change re-reads it
  (ov036 Field_SwapZoneByMatrix -> Field_SwapWeather -> ResetWeather) and the music (Field_SwapZoneBGM); the banner
  does not show again when the place name is the same (IsLocNameIdxChanged) **[test]**.
- **Ids** (ov036 WEATHER_OVERLAYS, names from system text 43 lines 181-191, battle weather from ConvFieldWeatherToBtl):
  0 sunny, 1 snow (no battle weather), 2 rain, 3 sandstorm, 4 blizzard (hail), 5 hail (hail), 6 thunderstorm, 7 heavy
  rain, 8 diamond dust (gives a medal), 9/10/11/13/14 mist, 12 Desert Resort's sandstorm (battle sandstorm).
- **Parts of a map** get a zone of their own (610 Route 111 desert, 611 Route 113 ash, 612 Jagged Pass ash, 613 Mt. Pyre
  outside fog; Black 2's unused Regi-chamber zones, no zone table names them): a copy of the map zone's header (same
  scripts, text, entities, encounters, camera, place) with its weather (+ music: the desert plays the Route 4 / Desert
  Resort entrance theme, zone 157's SEQ_BGM_R_C_*: user choice). Their tiles (Sapphire's weather trigger lines: the zone starts where Sapphire's weather starts) go
  into the ITCM zone lookup, which now takes rectangles per matrix: table = groups (u16 matrix, u16 count, then
  x0 z0 x1 z1 zone), count 0 ends it (hoenn_world.py lookup_tables / zone_lookup_code; the parts first, then
  world.json's zone_rects on matrix 416); 444 B. The parts share the map's entity file, so its people, triggers (ch4's
  Go-Goggles check, tested without goggles in the desert zone) and doors work in both; crossing respawns the map's
  people (DeleteAllActors + spawn) and runs its zone init again. Rooms' exits that arrive inside a part point at the
  part's zone (fixed_weather.apply: Desert Ruins, Glass Workshop, Mt. Chimney -> Jagged Pass, Mt. Pyre summit).
  **The part zones 610-613 must stay out of allocate_zones/allocate_interiors' pools** (fixed_weather asserts it).
- **Day-by-day weather (v166_fixes 2026-10-12) [code][test]**: Route 119 and Route 123 cycle like Sapphire's
  WEATHER_ROUTE119/123_CYCLE (data/hoenn_weather.json 'cycles'; patches/weather.py's GetWeatherAll hook: sunny / rain 2 /
  thunderstorm 6 / rain 2 and sunny / sunny / rain 2 / sunny by the DS clock's day mod 4, rain in battle as in Sapphire).
  Their ends beyond Sapphire's cycle triggers stay sunny: parts 609/608 (Route 119 north/south) and 586/550 (Route 123
  west/east), also kept out of the zone pools (allocate_zones AVOID). Continue keeps the saved weather until the next zone
  change (Black 2's continue path). Proofs: screenshots/v166/03_*, 04_*.
- Whole zones: Mt. Pyre summit (29) mist 9, Mt. Chimney (19) snow 1; rooms (fixed_weather.apply, after `interiors`):
  Rusturf Tunnel, Lavaridge Gym 1F/B1F, Cave of Origin B2F-B4F, Seafloor Cavern room 9: mist 9.
- **Fog flag [bytes][test]**: every Black 2 weather draws its haze with the 3D fog (overlays 75-78 call ov036
  0x0219990c = FieldFog depth shift/offset/enable). The DS fogs only polygons whose material polygon attribute has bit
  15; Black 2's chunks and building models have it (0x001f8081; not its effect materials such as the warp pads),
  CTRMap's NSBMD writer leaves it off (0x001f0081), so our weathers showed only their particles. User decision: the
  flag on everything Hoenn draws: fixed_weather.apply (fog_everything, after every patch that writes chunks or packs)
  sets it in every a/0/0/8 chunk from the first Hoenn chunk on (world cells, warp-only maps, other layouts, rooms,
  caves) and in every model of the building packs our zones' areas use that is not byte-identical to a Black 2 model.
  The fog is off in zones without a fog weather (zone fog table: our zones removed), so a clear zone looks the same
  (tested pixel for pixel).

## Outdoor checks and fixes (sweep_outdoor, 2026-10-07)
Tags as above; proofs: screenshots/sweep_outdoor/.

**b2tools/outdoor_check.py** (report step of rebuild_slice.sh; `--kinds`, `--frames`, `--all`, `--summary`) checks every
frame of a built world: the connected world, each warp-only group (incl. the event islands when HOENN_STANDALONE builds
them) and the other layouts. Kinds: `place` (> 32 placement slots a chunk, a door counts 2), `size` (chunk > 110,600 B),
`walk` (collision vs Sapphire: tiles walkable/surfable in one game only, moves Sapphire's elevation rule allows and Black
2's 20-unit step / side walls block or the reverse - Sapphire modelled from pokeruby ObjectEventUpdateZCoord /
IsZCoordMismatchAt from every warp, Black 2 from every door's approach tile with ledges, surfing (step rule too) and
waterfalls - and regions Sapphire reaches that Black 2 never does), `door` (warp y vs its approach tile, approach
walkable, warp tile solid, a door for every Sapphire warp), `bld` (every Sapphire house door MB_ANIMATED_DOOR needs a
placed model whose door model stands on it; non-animated doors a cave mouth or a model front), `zone` (walkable tiles of
a map in another map's zone), `tex` (terrain/building materials not in the area's texture sets; smeared/stretched UVs),
`layer` (same-facing surfaces < 2 units apart; a model's own pieces and its door < 1, as Black 2's models), `view`
(camera-angle rasters at yaw -20/0/+20: `cull` = back faces the camera sees, `hole` = nothing drawn). Findings kept on
purpose are in its ACCEPT list with the reason (one-layer Cycling Road, Black 2's own single-sided trees/fences/long
grass/models, open forest entrances, Sky Pillar's/Navel Rock's void, the event islands' ferry landings...) and only
counted. Retail pack-0 DAEs cache in work/check_models. The field heap: work/agents/sweep_outdoor/tools/heap.py.

Fixes (builders, not hand edits):
- **Route buildings (towns5)** were never in pack 0 (field-heap fear): 36 Sapphire house doors had no building (Mr.
  Briney's cottage, Winstrate house, Old Lady's Rest Stop, the League and Ever Grande's Center, Weather Institute,
  Safari entrance, Cycling Road gates, Trick House, glass workshop, flower shop, Seashore House, cable car, the route
  houses). data/buildings/enabled.json now has towns5: pack 0 370,824 B; HEAPID_FIELDMAP (0x15, 1,210,312 B) keeps
  40,788 B free after a map load in Lilycove, Slateport, Mauville, Mossdeep, Rustboro, Ever Grande, 31,3xx B in Littleroot
  and on Route 104 [test]. towns5.json: the gate (403) and glass workshop (410) doors 1 unit in front of their walls;
  Route 112's / Mt. Chimney's second door props 1 unit forward (they overlapped the record's door).
- **Waterfalls** (water.py, heights.py): Black 2's Waterfall carries the surfer 2 tiles over ONE 0x40 row; Sapphire's
  columns (Ever Grande 12x8, Route 119 4 rows, Route 114 3) left the surfer on a 0x40 tile, stuck (A does nothing there)
  [test]: the way to the League. Only a column's bottom row is 0x40 now, the rows above are the water above the falls;
  down and up at Ever Grande [test].
- **Water levels** (heights.py 4b): a body whose surf shores (Sapphire elevation 3, PlayerGetZCoord() == 3, and bridge
  decks) stand at one height lies at that height (nearest-shore split Route 120's lake / the Scorched Slab pond, etc.
  into 32-unit steps that stopped surfers); shoreless strips behind sea rocks take the level of the water past the rocks
  (Route 115's west sea stood at 0, 16 over the rest); a floating group across a pond from a bridge stands at the
  bridge's height (Route 120's Scorched Slab strip: the cave was unreachable).
- **Bridges** (heights.py 3b): a bridge whose banks the solver left > 16 apart keeps its water part level and steps 16
  at a time over its dry ends (Route 120 east of Fortree: a 64-unit wall in the deck; Route 119 by the Weather
  Institute: 32). **Slopes** (step 3): one too steep to walk (centre-to-centre >= 20) takes in rows beyond its ends
  (the Safari Zone's mud slope into the northwest, 64 over 2 rows: the northwest was unreachable) [test].
- **Doors** (world.py): a room door on an arrow-warp tile gets the arrow's walk-in warp (Lavaridge's Center back door
  was entered from inside the building) [test]; 'building' tiles Sapphire walks on outside every placed footprint stay
  walkable (the Weather Institute's front step: its door could not be reached) [test].
- **Roofs over water** (world.py open_buildings): Pacifidlog's / Sootopolis's / Route 110's roof rows and the Safari
  feeder's pond tile were land in the sea; now water.
- **Zones** (user decision 2026-10-07; done by zone_edges 2026-10-08, below): 10,000 walkable tiles of 29 routes lay in
  another map's zone (37 map/zone pairs: outdoor_check 'zone', accepted as PENDING then); every map has its zone
  rectangles now (outdoor_check 'zone' 0, the PENDING entry is gone).
- **Trainer NPCs**: data/hoenn_trainer_npcs.json predated the zone rectangles: Route 104's Billy and Ivan, Route 117's
  Anna & Meg and Route 126's Chad sat in the zone of their cell, where the game never spawns them (outdoor_check --rom
  'ent'). rebuild_slice.sh now reruns converter/gen_trainer_npcs.py after gen_map_content.
- **Walls and plinths on cliff faces** (ground.py face_tile): Sootopolis's rims, Ever Grande, Sky Pillar's top drew a
  wall block in the plane of the cliff face the tile holds (depth fight); the face is the wall there now.
- Left open (report): boulders touching cliff faces (iwa01 vs gake: the rock tile holds the face), trees against cliff
  faces (0.4-0.55), ledge seams (0.09), a few town models' single-sided sides seen from the screen edge (Fortree tree
  houses, Mauville Game Corner, Pacifidlog roofs' ridge seams, Lilycove houses, Mt. Chimney's cable), 1-60-pixel cracks.

## Zone rectangles for every map (zone_edges, 2026-10-08)
Tags as above; proofs: screenshots/zone_edges/.
- **world.py zone_rects**: every map (not only those with a door in another zone's cell) gets its own zone on its tiles
  in other zones' cells: 73 rectangles on the Hoenn matrix (+ the 14 fixed-weather part rectangles first: ZoneLookup
  1,066 B in ITCM, roamers' code after it). Geometry unchanged: every cell's terrain.dae / collision.per / chunk.json
  byte-identical to work/world's; one placements.bin differs (cell (5,9)): Route 103's "ROUTE 103 / OLDALE TOWN" sign
  (11,9) gets its signboard - its tile was in Oldale's hand-made zone 397, where gen_map_content places nothing.
- **What moved** (outdoor_check 'zone' 37 -> 0; work/agents/zone_edges/analyze1.txt lists every event): the generated
  signs/people/item balls of 11 maps, in the auto files of 14 zones (gen_map_content, data/hoenn_content.json; the 3
  Route 113/119 signs world.py warned about), 14 trainer NPCs (gen_trainer_npcs; the committed
  data/hoenn_trainer_npcs.json also still had 5 in their cell's zone), 10 berry spots and 2 hidden items (global scripts:
  story.py places them in the tile's zone, the hidden-item table follows), and the story scripts: ch7's Route 119 rival
  scene (triggers, the five rival entities incl. uid 125, which had to be held by zone 16), Kecleon 1, Yasu and Hideo
  (scenes/FortreeCity.inc -> scenes/Route119.inc, scripts 7-9; the rival sprites' setup moved into Route 119's init,
  Sapphire's Route119_MapScript1_15119B), ch2's lost-glasses man (VerdanturfTown.inc -> Route116.inc, script 6), ch3b's
  first Route 110 grunt (Route103.inc -> Route110.inc, script 11); their jsons through their generators
  (work/agents/ch7/gen_objects.py, ch2/tools/mkjson.py, ch3b/tools/gen_objects.py). Checked: no scripted warp, test
  warp or data table (respawn, fly, dive, boats) points at a tile whose zone changed; roamers match place names, which
  the rectangles only make right; no outdoor ObjInitNPCGPos index moved (Petalburg's, Slateport's, Lavaridge's,
  Littleroot's, Oldale's NPC lists are unchanged). Every NPC/sign/trigger/warp of every zone stands on its own zone's
  tiles in the ROM (work/agents/zone_edges/tools/entcheck.py: 1 of 1066, Slateport's unreachable harbour warp).
- **Wild tables** (gen_encounters): the towns that borrowed a route's grass in their cells (Oldale, Rustboro, Mauville,
  Fortree; Lilycove and Petalburg their grass part) have none now; a map that once had an encounter file keeps it,
  written empty, so no zone header points at a file with Unova's table.
- **Fixed-weather parts** (patches/fixed_weather.py parts): a part also covers its map's tiles in the map's own
  rectangles (none of the four parts reaches another zone's cell today: their rectangles are unchanged).
- **Zone hold** [code][test]: Black 2 swaps zone as soon as the player's position is in another zone, also while a
  script walks the player (ov036 FieldRoutine_Run calls Field_CheckDoRealTimeLoad every frame; the banner alone waits
  for the event), and the swap deletes every actor (ov012 DeleteAllActors keeps only the player and flag-0x20 actors).
  Wally's catching tutorial walks 6 tiles into Route 102 (Sapphire keeps Petalburg's objects across its map change):
  with the rectangles Wally vanished mid-walk and a Route 102 man said his lines [test]. ZoneLookup now returns the
  cell's zone while map-local flag 0x60 is set (`h_zone_hold`, src/include/hoenn_story.inc; it reads the flag through
  g_GameSystem 0x021410f4 -> GSYS_GetGameData -> GameData_GetEventWork -> EventWork_FlagGet); every zone change clears
  flags 0-0x63 (FieldScript_CallOnZoneInit), so the scene's warp ends it. scenes/PetalburgCity.inc sets it before the
  walk [test: Wally walks and talks to the end, Petalburg's zone throughout]. The scripted player walks of every outdoor
  scene were listed (work/agents/zone_edges/tools/warps.py and the movement scan): no other crosses a map edge.
- **Tested** (T builds with HOENN_TEST_CHZE_W1-4 = Littleroot's four signs warp to "zone,x,z,dir", 0778): the game's
  zone id, the music (RAM copies of the zone's BGM) and the wild table in RAM change on the step over Sapphire's edge,
  not at the old cell edge: Rustboro/Route 115 at z 179/180 (old 159/160), Rustboro/Route 104 at 239/240, Route
  119/Fortree at x 367/368 (old 351/352: nothing there now), Mauville/Route 111 at z 199/200 (old 191/192), Route
  111/the desert part at 122/123 (sandstorm, desert music), Mossdeep/Route 127 surfing at z 199/200 (old 223/224);
  banners "Route 115"/"Rustboro City", "Route 127"/"Mossdeep City", "Route 111" [test]. Route 119/Fortree shows no banner
  either way: their invisible-Kecleon scene condition (ch7_lib c7_hide_kecleon) runs on every zone entry and closes it
  (as at the old cell edge). Ch7's Route 119 rival scene in zone 463 (bike ride-in, balloons, battle, HM02, ride-away),
  ch3b's first grunt in zone 368, Wally's tutorial with the hold [test].
- The ROM's arm9 grew 520 B (the rectangles + the hold code in the ITCM autoload): every ROM file moved 512 B, and the
  ITCM code changed: savestates made before need remaking (make_states.py).


## Invisible buildings (buildings_audit, 2026-10-08)
Tags as above; proofs: screenshots/buildings_audit/ (Sapphire left, DeSmuME right). Tools: work/agents/buildings_audit/tools
(`audit.py` warps/uncovered tiles/ROM packs and textures, `sweep.py` every outdoor map top-down next to Sapphire, `look.py`
one spot at the camera angle, `tour.py` warp + screenshot + field heap [+ save] on a HOENN_TEST_WARP=563,6,7 build).
- **Audit, every frame** (main, the 17 warp-only groups incl. the event islands, alt_Route103/130/131; Ruby shares the world
  and the packs: no version branch in world.py / area2_buildings / standalone, its only outdoor change is Lilycove's
  repainted hideout entrance, notes/RUBY.md): every outdoor warp (209 over the frames) by Sapphire behaviour; every plan building / roof /
  door / prop tile no model covers; all 72 maps side by side with Sapphire [renders]; every placed res is in its area's
  pack (a/0/1/3 area -> pack; a missing one would draw rock 0x15) and every material's texture and palette is in the
  pack's texture set (a/1/7/4 entry = pack) [bytes]; one tile south of every zone's first door, 54 zones, every model
  drawn [test: screenshots/buildings_audit/door_tour_*.png].
- **Built** (Sapphire's footprints and look, Black 2 textures, the town builders' way):
  - Route 118's door-less house (x 0-3, rows 15-17 + roof row 14, Mauville tileset 0x283-0x29d): solid, grass drawn.
    towns5 res 411 (models_routes.house118: Mauville house 2's build without a door, window and posts at Sapphire's
    columns), data/towns/Route118.json prop (2.0, 16.0); 3,248 B.
  - Slateport's white stone monument (prop tiles x 32-33, rows 52-54; the ground module drew a 12-unit plinth): towns2 res
    354 (models_slateport.statue, six-sided tiers, faces the camera never sees left out), prop (33.0, 54.0) + covers; 4,368 B.
  - Emerald's harbour at the end of Birth Island's (x 12-18, rows 24-28) and Navel Rock's (x 7-13, rows 18-22) docks
    (gTileset_Dewford 0x352-0x377, labelled solid water: open sea was drawn): standalone res 481 (models_standalone.harbour),
    one model, data/towns/BirthIsland_Exterior.json / NavelRock_Exterior.json. Low (eaves 16 over the dock) because it
    stands between the camera and the player / ferry sailor at the dock's end. Its warp stays parked (no harbour room).
  - Sky Pillar top's doorway (16,14), one of the 11 accepted 'bld' doors ("the hole down into Sky Pillar"): Sapphire draws
    a dark arched door in the wall band (0x2a2). standalone res 482 (spdoor): dark arch and stone jambs leaning with the
    heights module's cliff face there (yamagake01 rises from the north edge of row 15 to 8 units further north at y 28),
    3 units in front of it; data/towns/SkyPillar_Top.json prop (16.5, 15.0).
- **The other 10 accepted 'bld' doors** are open entrances in Sapphire too (Route 104 ×4 into Petalburg Woods, Route 112 ×2
  into Jagged Pass, Southern Island ×2, Faraway Island ×2: forest/path gaps) [renders]. Cave and water doors have mouths.
- **outdoor_check 'bld'** now also lists solid Sapphire building/roof/door tiles that no model covers as the camera sees it
  (a point h up hides the ground h·cot 40° further north: dome knobs, tall roofs). Accepted: Fortree's tree-house door rows
  (the deck in front of houses that stand a row north) [test], the Abandoned Ship (terrain/ship.py), Sky Pillar top's
  outer wall (void). On the world before this audit it also finds Route 118's house and Sky Pillar's doorway; the
  harbours (labelled water) and the monument (a prop) were found by the map-by-map comparison.
- **Route 112's cable car line** (follow-up): the pylons on the prop tiles x 12 rows 19-21 and x 4 rows 15-17 (the ground
  module drew plinths) are towns5 res 412/413 (models_routes.pylon_mid/pylon_top, Route112.json props + covers): tapered
  blue masts and the cable in one straight line from the station's pylon (beam 126: the station stands on the heights
  module's 80-unit block) rising to 150 at x 4 and on off the map's west edge, so the x 12 mast is 140 high and the x 4
  one 102 (on 48-high ground). The station's own pylon (res 406) hung 80 units over its ground: its mast now reaches down
  (cablecar(); it assumes the station's 80) and its stub cable west is gone (res 412 carries it). The masts lean outward
  near the screen's edges (the camera's perspective), as tall things do in Black 2.
- **The DS took some polygons' first vertex from the polygon drawn before** [code][bytes][test]: CTRMap's NSBMD writer
  writes a vertex near its polygon's node centre as VTX_DIFF counted from (0, 0, 0) when it is the first of the polygon;
  the DS geometry engine keeps the last vertex across polygons, so that triangle came out sheared and its neighbour
  missing (Sky Pillar top's stairs: a sky-coloured triangle and a slanted face reaching the lower floor). apicula and a
  decode with the writer's assumption draw it right; the same cell written without that command draws right in DeSmuME.
  7 of the 4,708 polygons of the 422 world cells began so (cells 05_03, 05_13, 15_11, 22_03, Faraway Island 01_00, Sky
  Pillar Outside 00_00, Sky Pillar Top 00_01); none of Black 2's own models. b2tools/nsbmd_fix.py rewrites such a first
  vertex command as VTX_10 (absolute, same size, at most 32/4096 of a model unit off); patches/fixed_weather.py's pass over
  every Hoenn chunk and pack model applies it: 0 left in the ROM. work/agents/buildings_audit/tools/dlist.py decodes
  display lists.
- **Nothing is drawn over void tiles** (world.py build_cell): heights.py's faces between void tiles of different heights
  went on there (Sky Pillar top: 32-unit faces from the sunken band (x 7-18, rows 15-18) down the screen to the matrix
  edge, one triangle pair from row 17 to row 41); triangles over void are cut on the tile grid and the pieces over void
  dropped. Collision unchanged (every collision.per byte-identical).
- **Sky Pillar's and Navel Rock's summits** (user: "polish sky pillar it looks unfinished"): they floated in the clear
  colour. Black 2's own high places stand over a sea of clouds: chunk 521 (a round stone tower top, map set 90, clouds of
  o23_cloud_a 340 under its floor at one repeat per 256 units; probably Dragonspiral Tower's top) and chunk 542 (a
  rooftop of columns over the same clouds); sky textures exist too (c3_sky2, un_sky backdrops, pk_l_sky, c12_cloud01) but
  a cloud floor is what Black 2 puts under a summit. Standalone res 483-486 (models_standalone.sky_pillar_top: one model
  per cell, since Black 2 draws only the buildings of the chunks loaded round the player; cloud sheets 4 units apart,
  texture coordinates from the map position so they line up): Black 2's clouds 200 under the floor, the tower's face
  under the south parapet in the tower foot's dark brick (res 477) with stone bands and dark windows, a low curb of the
  parapet's stone along the other floor edges. Res 487 (navel_top): the rock down from the summit's own outline, clouds.
  Sky Pillar Outside's border is sea: nothing bare there. Texture VRAM free in those zones 164,176 B (Sootopolis 146,256).
- **Mt. Chimney's lava** (user: "the lava on the mountain looks a little glitchy"): one flat tile-sized quad of
  in81_magu00 level with the ground, stepped hard edges, a green grass lip (heights.py's gake1_1) along some edges, static.
  world.py lava_tile lays it as Reversal Mountain does (chunks 723/726, map set 388): the lava 10 under the ground, the
  dark crust with holes (in81_magu01) 2 over it, banks (in81_mizuga1) sloping 4 down over 6 and a glowing shore
  (in81_mizugiwa) at their foot on every side meeting ground, mitred at corners; data/hoenn_standalone.json MtChimney
  'lava_top'/'lava_bank'/'lava_shore', retex gake1_1 -> out57_gake1_0. **It moves**: Black 2 animates terrain per area
  (AreaData_GetSRTAnmID, a/0/6/8: entry 0 = area 3's water, 29 = Reversal Mountain's, which scrolls in81_magu00/01 and
  in81_mizugiwa by material name); the group gets its own area record (407: a Black 2 area no zone uses and whose texture
  set nothing else reads; 'area' + 'srt_anim' in the group, world.py -> world.json, patches/standalone.py writes the
  SRT id), the other warp-only groups keep 408 with area 3's water animation. Measured: ~900 of 11,000 lava pixels change
  in 45 frames. Jagged Pass and the Fiery Path have no lava. Mt. Chimney's meteorite machine (prop tiles (14, 5-6)) is
  still a plinth.
- **Memory** [bytes][test]: Black 2 loads one area per field and the connected world is one area (2) -> pack 0 only (a
  second area means a warp-joined split, as the standalone groups' pack 70). Pack 0 371,448 -> 382,856 B (81 models: res
  411, 354, 412, 413); the build prints "the menu save keeps about 18,852 B"; measured in DeSmuME: 100,320 B of field heap
  free after a map load in pack-0 zones (Route 112, Littleroot) = 17,316 B over the save's 83,004 (the estimate is ~1.5 KB
  optimistic); saves in Slateport, on Route 118 and a cold-boot save -> reset -> Continue -> save again in Littleroot
  work. Pack 70 74,880 -> 98,476 B (412,488 B free in its zones); standalone texture set 109,340 -> 119,132 B, map sets
  407/408 76,412 B. Room left in pack 0: ~10 KB above area2_buildings' 8 KB floor.
- **Left as plinths (props, not buildings)**: Mauville's bike racks, Slateport's shipyard boats and crates, the Safari
  Zone feeders, Mt. Chimney's meteorite machine.

## Overworld polish (overworld_polish, 2026-10-08)
Tags as above; proofs: screenshots/overworld_polish/ (before = HEAD's world, after = this pass, same ROM patches, stage-2
objects shown). User asks: Dewford and Mr. Briney's cottage first ("the rocks look very glitchy, missing pixels"; "the
bottom of the docks is rock"), then anything unpolished. Terrain and textures only: pack 0 unchanged (382,856 B).
- **Sea and route rocks** (ground.py draw_rocks / rock_card): Black 2 does not build its rocks into terrain; it places the
  tiny models rock_01/02 (res 21/258) and searock_01/02 (res 54/55): one card each, leaning back 45 degrees, 32x24 or
  16x8, images rock01 / searock1.1 (grey rock in a foam ring) from every exterior building texture set [bytes: apicula
  DAEs of retail pack 0; placements in chunks 2, 23, 247, 300: on land at the ground's height, in the sea at the water's
  collision height]. Hoenn's ~8,000 rock tiles exceed the 32 placements a chunk, so the cards are drawn into the terrain
  with the same geometry and images ('ext46', +1,192 B of map texture set). The iwa01 cones they replace had their north
  faces and neighbour-hidden faces left out and were torn by the per-tile lift where a 2x2 boulder spanned two heights
  (the user's missing pixels). 2x2 cards only over tiles drawn at one height. HOENN_ROCKS=iwa restores the cones.
- **Rock masses in the sea** (heights.py sea_rock_masses / raise_sea_rock): cliff / cliff-top masses that touch water and
  no land (Sapphire's pink rock piles and reefs, Routes 104-109, 124-134, Pacifidlog, Mossdeep, Lilycove) were grass
  plateaus when their metatiles came out greenish. Now Black 2's brown rock (rock top gake_michi, lip gake1_0, face
  yamagake01, rock-lipped banks), the inside raised a level and a second one 4+ tiles in (square terraces); masses between
  seas more than a level apart (Route 125's east wall, 0/96) and masses with a top a surfer can land on are not raised.
  Small masses (<= 12 tiles, <= 4x4: Sapphire's big pointed rocks) are one searock card scaled to the mass, in the water.
  Every rock-coloured cliff by the sea gets the rock-lipped bank (it had a grass lip).
- **Water steps along rock lines** (heights.py lower_rocks): a line of sea rocks between two water levels a level apart
  (Route 104's rocks between the open sea at 8 and the channel at -8) stood at the upper level, the step's face cut the
  cards in the lower tiles. Rocks standing only in water are drawn at the lower water's level and hold no face
  (F.noface); no skirt between them and the higher water (_Lattice.water_step). Rocks touching land or a cliff keep their
  height (Route 125's arc).
- **Mr. Briney's jetty and cove** (heights.py 4b, _Lattice.open_under, ground.py pier_posts, water.py `under`): a pier (a
  deck reached from land at one end) at Sapphire elevation 4+ is no surf shore (PlayerGetZCoord() == 3 is needed to
  surf, pokeruby IsPlayerFacingSurfableFishableWater): his jetty had split the cove from the channel south of it at a
  16-unit rock step under the boat. **Collision change**: the cove's 15 surf tiles (Route 104 x 7-13, rows 52-54,
  world (55-61, 292-294)) 8 -> -8, level with the channel; plus 5 solid rocks there 16 -> 0. No other record changes
  (checked against HEAD's collision.per, every cell). The jetty (16) now stands on posts 24 over open water: no face or
  skirt under a deck over water, posts from the deck's side face into the water, the water under the deck at the level
  of the lowest water beside it, the jetty's unwalkable west end drawn as deck. outdoor_check walk unchanged (Sapphire
  does not surf from the jetty either). missing_objects' boat follows the tile height (told, checked).
- **Ground under buildings, trees and rocks** (ground.py ground_under): world.py drew grass under every building tile:
  squares of grass under Dewford's houses, Gym and trees, Rustboro's, Slateport's, Mauville's... buildings. A building
  takes the most common ground of its 5x5 (sand -> sea_jimen, a town's path -> world.py's path tiles, decks out on the
  water -> deck planks with water under: Pacifidlog's houses, as Black 2's Humilau on its walkways); trees and rocks take
  sand when their Sapphire metatile shows sand (Dewford's trees).
- **Dewford's corner across the channel** (heights.py RAISED): trees behind a brown cliff on a sand top in Sapphire, a
  grove at the town's height with a grass rim before: raised a level (drawn only), rock lips, rocky banks, sand under the
  trees. **Pacifidlog's walkways and Dewford's dock** stand on posts (POSTED_DECKS).
- **Ferry piers** (ground.py pier_tiles, water.py PIER_BANK): the Battle Tower's and Southern Island's S.S. Tidal piers
  stood on grass banks with a 16-unit stone block across their front; now paved (t02michi_b) with straight stone sides
  (t02_kabe01) into the water.
- **Drawing vs collision**: every height drawn differently from the collision (F.coll_h: raised masses and corners,
  lowered rocks, card masses, jetty end) keeps the collision's height in Field.record, water.collision, the tiles
  outside the maps (step 11) and the alt layouts (world.py keep_main). work/agents/overworld_polish/tools/drawn_reach.py:
  none of those tiles is reachable in either game.
- **Checked**: outdoor_check fast kinds 0 open (accepted counts as HEAD); view/layer: layer 43 -> 38, cull 311 -> 299, hole
  63 -> 67 cells (1-2 px cracks at terrace corners of the raised masses, Route 124/125/Mossdeep); npc_check 0 over
  a limit; field heap unchanged (100,216 B free; 92,512 beside Mr. Briney's boat, save margin +9,508, saves there);
  save -> Continue cycle.
- **Leftovers, second pass** (user, same day; proofs paved_towns_before_after.png, sand_rings_before_after.png):
  Rustboro, Slateport and Mauville paved where Sapphire paves (ground.py paved_tiles / draw_paving: Accumula's slabs
  t02michi_b, its plain stone t02michi_c for the pale roads and white stone, by Sapphire's metatile colour; buildings,
  lamps, signs and stall props in the paving stand on it; world.py leaves those path tiles alone); Dewford's forest ring
  outside the map stands on sand within 4 tiles of its sand-ground trees (ring_sand); sea rock masses may touch a beach
  (Route 127's island: brown rock instead of a grass field) and the shallows Sapphire draws as sand round the rock
  islands are sand (water.py, sandy_tile); the sea rocks' masses rise one level only (HOENN_SEA_ROCK_TERRACES, default 1:
  the second terrace's diagonal corners left 1-25 px cracks; main-frame view holes 43 cells / 409 px vs HEAD's 43 / 382,
  the rest at Route 125's 0/96 sea wall). Collision unchanged against the first pass (a599496); 0 texture bytes.
- **Left**: Mt. Chimney's meteorite machine is still a plinth; Route 125's east sea wall (0/96) shows a few px of cracks.

## Final glitch check before v15.2 (final_check, 2026-10-08)
Both versions built from HEAD c13dcb8 in work/agents/final_check (own tree, world, interiors; rebuild_slice.sh's patch
list; test ROMs with HOENN_TEST_CHMO + the test warp, states made on each). Proofs: screenshots/final_check/.
- **Checkers** (HEAD -> after): outdoor_check fast 0 open both (accepted walk 220, door 13, bld 17, tex 55 unchanged);
  layer/view 40 / 300 / 64 both (HEAD a599496's 38 / 299 / 67 -> c13dcb8's polish 2: +2 layer, one Route 125 searock card
  whose leaning foot meets the island's foam band (min gap 0.07, an intersection line, no flicker in DeSmuME)); caves_check
  t 42 both (the rim-fade class; abcefhistwx on the 8 underwater maps and the mist caves: nothing else); rooms_check
  Sapphire b4 e118 g1 h13 k9, Ruby b4 e115 g4 h13 i3 k9 both unchanged by the fixes (k +5 since v15.1: the S.S. Tidal / sub
  shadow on harbour water and the cable cars on their rail, solid tiles as in Sapphire, seen in game); npc_check 0 over;
  check_exits 0 outdoor; the menu save keeps 18,852 B (unchanged); beside Mr. Briney's boat 92,512 B free (+9,508),
  save -> Continue -> save again [test].
- **Fixed**: berry soil heights (heights.py 9c: Route 119 (8-9,23), Route 120 (9-10,92) trees stood 16 / 32 under the
  ground, two invisible [test], screenshots/final_check/03); Mr. Briney's boat collision 1 x 2 (04; notes/STORY_HANDOFFS.md);
  Underwater3 <-> Underwater4 joined (notes/DIVE.md); Lavaridge Gym's void black (notes/CAVES.md "Mist rooms").
- **Seen in game, as designed**: every 3D object (boats at their docks/beach, S.S. Tidal at both harbours, the Battle Tower
  and Southern Island (no surf shore there: nobody reaches its hull), submarine shadows, Seafloor submarine), cable cars,
  fossils, Birch's bag, Pichu Doll, all 80 berry trees, the new buildings, summits, Mt. Chimney's lava (moves), the
  underwater and mist maps, the polish places; Ruby's Magma B2F sub, Groudon's B4F / Room 9 layouts.
- **Surf landing** (follow-up, same day) [code][bytes][test]: Black 2 lands a surfer on any tile in front that is neither
  solid (flag bit 0) nor surfable (bit 1) with no actor on it - no height or elevation test (ov036 CheckSurfExitEvent
  0x02182cd4; surfing off land needs 0 <= land - water < 20, CheckSurfHeightAllow 0x0219ab30; walking 20,
  ActorRouteCollCheckCore). No collision attribute forbids landing on a walkable tile (bit 1 would let the player surf onto
  it). Black 2's own maps never need one: all 1,121 landable cells beside surf water in a/0/0/8 are 0, 4 or 8 units above
  it, higher edges are solid. Sapphire lands only onto elevation 3 (pokeruby field_player_avatar.c sub_8058EF0), so here a
  surfer climbed onto Mr. Briney's jetty and Mossdeep's north bank (24 up), Lilycove's and Route 119/120's raised banks,
  bike rails and bridge decks. Now heights.py step 12 sets collision flag NOLAND (0x4000; flag bits 9-14 are read by no
  ov036 code) on the 163 walkable tiles beside surf water whose Sapphire elevation is not 0, 1 or 3, and hm_free.py's
  SurfLandingTileType (44 B in ITCM, both `bl GetTileTypeAtPos` of CheckSurfExitEvent) adds the solid flag there for the
  landing check only. Collision otherwise byte-identical. Tested (screenshots/final_check/11): no landing on the jetty (with
  and without the boat) or Mossdeep's bank or Route 120's bridge deck; landing on Route 104's beach and on Route 120's
  elevation-3 bank 24 units up; walking the jetty. Dewford's dock, Route 109's beach and Pacifidlog's walkways are
  elevation 3 (landable, as Sapphire); the Tidal piers have no surf shore. outdoor_check models it (b2_landing; Sapphire:
  elevation 0/1/3) and compares every landing both games reach ("surf landing" findings): 0, walk accepted 220 as HEAD;
  with Black 2's own rule it reports 93 (that is how the jetty is caught).
- **Southern Island's Lati@s** [test]: test stages 4/5 in scenes/missing_objects_test.inc. Its object waits at Sapphire's
  (13,2), inside the forest band as in Sapphire (where the camera pans up to it); it exists only for the slab scene, which
  adds it off screen: it flies in over the tree tops at the top of the screen and down the clearing to the slab
  (screenshots/final_check/12). No change.
- **Left**: Route 119 (30,90)'s tree base hidden by the elevation-4 plateau right south of it (Sapphire's layout).

## Showcase glitches (map_glitch_fix, 2026-10-09)
A Reddit moderator called out clipping in the public shots (release/showcase/*/03, 04, 05, 05b). Proofs:
screenshots/map_glitch_fix/ (DeSmuME before/after, Sapphire and Ruby; offline renders of the pattern elsewhere); retaken
shots release/showcase/{sapphire,ruby}/<name>_v2.png.
- **Pits under walled-in patches** (heights.py step 2, the last anchor): a group of walkable tiles tied to nothing
  (no stairs, ledge, junction, water or warp: walk-behind tiles among trees, Fortree's big-tree trunk tiles (13,8)/(29,8)
  and the grass behind its Gym (18,10)) was anchored at its absolute Sapphire level (0) though the land round it stands
  32-96 higher; step 7 then gave the trees and rock round it that height too: Fortree's 96-deep pit under its houses,
  Route 113's under the ash grass (trees' crowns cut by the pit's faces), Route 112's round the cable car, Ever Grande's
  rock. Such a group now keeps Sapphire's level difference to the nearest placed region (an "any level" patch takes
  its level) when its absolute level is 2+ levels off. Drawn heights change in 12 maps (Route 111-115, 119-121, Fortree,
  Fallarbor, Lavaridge, Ever Grande; 2,116 tiles incl. the Fortree stilts), no walkable tile's collision height, walkability 0 changes.
- **Step 8** keeps walkable non-building tiles inside a plan footprint's box at their region's height (Fortree's
  Center + House 1 merged footprint pulled the walkway's west end down 16).
- **Fortree's tree houses** (heights.STILTS = {'FortreeCity'}; ground.py pier_posts / stilt_floor; models_fortree.py;
  data/towns/FortreeCity.json): the walkways (bridge) and ladders keep their collision but no longer lend their height
  to the solid tiles round them: forest floor at 96, plank walkways at 112 (128 east) on posts with their 8-unit fascia
  and the floor drawn under them; the houses stand at their door row's south edge (z = door + 1: the props used the
  Center's front 20 and stood two rows north, behind a grass strip, House 5 and the Decoration Shop over a cliff) on
  stilts with a plank rim and side braces (pack 0 +3,264 B: the menu save keeps ~27,904 B).
- **Ash** (data/hoenn_ash.json 'ground', 'lips', 'ash_grass'; world.py ash_tiles/ash_ground): the snowy art covered only
  the ash grass and trees on Black 2's green summer lawn (snow-capped boxes, white rims). Every ash-coloured tile drawn
  as grass in the ash maps gets the winter ground (Route 113 1,829 tiles incl. 287 ash grass; Jagged Pass; Mt. Chimney),
  the outside forest where its nearest map tile is ash, all tall-grass layers winter (olive kusa_ec2_y), snowy lips
  (gake1_1_y) within a tile of ash ground; +2 textures in set 3.
- Caves (Meteor Falls slab) and the underwater outline: notes/CAVES.md and notes/DIVE.md, same date.
- Checks: outdoor_check fast kinds open 0 -> 0 (accepted bld 17 -> 12, the Fortree door rows now covered; gake1_1_y
  added to the smeared-lip accept); caves_check abceistwx t 42 -> 42, f/h on the 18 rebuilt caves h 8 -> 8, f 0 -> 0;
  rooms_check Sapphire b4 e118 g1 h13 k9 m50 unchanged.
- Left: Meteor Falls' waterfalls show thin grey-tan vertical lines: the look's 'waterfall_streaks' d0sizuku (16x128)
  has one full-height 75%-opaque column (9c9484) at u 11, repeated once per tile (u x4); not changed here.
  Fixed (map_gfx 2026-10-11): d0sizuku is an atlas (Black 2's chunk 788 maps only texels 13-16, the falling drop, onto
  2-unit strips, 64 texels per 78 units, and texels 0-10, the splash, onto the floor; column 11 is never shown). The
  falls now get three such strips per tile, each at its own phase (models_cave_levels.py); Meteor Falls 1F_1R and
  Victory Road B2F rebuilt (+44 triangles, +1.5 KB / +0.5 KB chunk).

## Walkability: invisible walls (walkability, 2026-10-11)
Tags as above; proofs: screenshots/walkability/ (before = the public v16.3 ROM, after = this build, both with the
Littleroot test-warp sign).

**b2tools/walk_diff.py** (report step of rebuild_slice.sh, `<world>.walk_diff.txt`): every built map against Sapphire
(pokeruby's own map.bin collision/elevation bits and metatile behaviours, placed with the builders' offsets), per
family (town, route, other outdoor maps, interior, cave, dive). Kinds: INVISIBLE (walkable and reached in Sapphire,
blocked here: tile or step), THROUGH (the reverse), WATER/LEDGE/LANDING, and OPEN: a blocked tile next to a tile you
walk on with nothing drawn on it (inside the tile every surface is floor within -6..+3.5 of the walker's floor, no
upright piece, lip, model, water or void; no person on it in the ROM). Movement comes from outdoor_check.check_walk
and caves_check.check_walk (rooms too), so the rules stay in one place. Intended differences are listed apart
(`--all`): outdoor_check's ACCEPT list, room recipes' block/unblock, Sapphire's own invisible walls (its metatile has
only its walkable neighbours' colours) and elevation walls, Black 2's room conventions (the floor strip at a room's
front edge: 1,467 such tiles in Black 2's own 373 one-chunk rooms; the genkan notch), the forest's south gap row
(DECISIONS 2026-10-06). Measured on Black 2's own rooms first (work/agents/walkability/tools/b2_baseline.py).

What the user saw (counts: walk_diff before -> after, open findings):
| family | before | after |
|---|---|---|
| towns | OPEN 443 | OPEN 17 |
| routes | OPEN 953 | OPEN 9 |
| other outdoor | OPEN 677 | OPEN 9 |
| interiors | OPEN 1,224, THROUGH 93 | OPEN 656 |
| caves | OPEN 84 | OPEN 84 |
| Dive | 0 | 0 |

Causes and fixes (builders):
- **Flat rock beside paths [code]** (heights.py): Sapphire's cliff tiles that touch no ground (the inner rows of a cliff
  band two or more rows deep, Ever Grande's and Route 111's mountain masses) took the lowest height next to them (step
  6) and lay flat, level with the path, as rocky ground or grass: 1,700+ blocked tiles that looked walkable. Step 5 now
  counts such tiles as highland (they rise a level above the ground at their rim); step 9d raises every flat rock tile
  (cliff, cliff top, mountain) still level with a walkable neighbour, with the flat rock behind it, one level (drawing
  only, F.coll_h keeps the collision). clamp_south (Mt. Chimney) lowers rock to one level above the walkway, not to it.
  world.py lift_field now lifts F.coll_h too (a standalone group's drawn-otherwise heights kept the unlifted height).
- **Triangles** (heights.py draw): skirts along a straight line are one wall per run, and faces turned away from every
  field camera (north faces; tested against a camera 65 degrees down) are left out: they were culled in the game. The
  world has 355,048 triangles (324,401 at the start, other agents' palms and trees included); largest chunk
  104,956 B. outdoor_check before -> after: walk/door/bld/tex/size 0 open both; hole 59 -> 24 cells, cull 288 -> 247,
  layer 34 -> 41 (the new ones: raised-rock skirts back to back with Mt. Pyre's grave plinths and Sootopolis's
  carved buildings - on Mt. Pyre checked: opposite facings, one of the two culled - a ledge lip by a skirt, Slateport's stall plinth by
  a sign, and door_fix's door_pc against its own roof at (555, 136)).
- **Building and sign tiles you walk on in Sapphire [code]** (world.py open_uncovered): a placed building's whole
  Sapphire footprint was solid, but Black 2's models stand back from the door row beside their entrance (every Gym's
  door-row corners, the Battle Tower's front) and a sign model stands on its own tile (the tops of the Gym signs): 36
  tiles of flat ground. They are walkable where no placed model rises over them (read from the models' geometry, the
  outdoor_check registry); the Route 110/111 gates and the glass workshop keep theirs (bigger models).
- **Slateport's stalls**: the stall model covers its two awning rows only (data/towns/SlateportCity.json "covers"); the
  row in front (Sapphire's posts and wares, the seller between them) gets the ground module's counters.
- **Ferry piers** (Battle Tower island, Southern Island): Sapphire's railing along the pier front is Black 2's metal
  railing (ground.py draw_pier); **Cycling Road**: its support tiles over land beside the road deck, or beside walkable
  ground level with them, get the railing too (they are always solid: ground.py collision).
- **The foot of rock faces [code]** (heights.py GAKE_FOOT): gake01a's two bottom texel rows are transparent at the tile
  ends, so the clear colour showed as a thin blue line at the foot of every 1-level face (the raised rock made many
  more: outdoor_check hole 59 -> 126 cells). Its v now starts 1/7 up (skirts and lattice faces): no geometry change.
- **Route 110's south Cycling Road gate [code]** (door_fix's finding; heights.py after the region solve): two doors in
  one wall into one room get their front tiles at one height (the building stands level). The east door's ground,
  cut off by the fence and tied only by the 3-row stairs up to the Cycling Road (whose deck a junction keeps level
  with the west door's ground), stood 16 lower: the door half under the gate's base. That region (60 tiles) now
  stands at the west door's level; the stairs there are flat (as four others the constraints flatten). It is the
  only building where the rule changes anything; walkability is unchanged.
- Left (walk_diff after): Fortree's forest tiles next to the tree houses (15; forest_fill leaves tiles next to
  buildings to the town models, b2_trees' rule), Lilycove's and Sky Pillar's building corners Sapphire blocks that the
  models do not cover (4), six ledge-corner tiles (Jagged Pass, Route 114), eight single cliff tiles with a lip only,
  two Cycling Road supports by water, one Route 119 rail end, two Safari tiles outside the maps.

## Final outdoor sweep for v16.4 (sweep_outdoor, 2026-10-11)
Proofs: screenshots/sweep_outdoor/ (DeSmuME, test-warp sign; before = HEAD 9b691e0, after = this build). Every outdoor
map rendered from the game camera (work/agents/sweep_outdoor/tools/render_maps.py: outdoor_check frames, textured,
culled; magenta = nothing drawn) and a 4-view emulator tour of every map (269 views, tools/tour_list.txt).
- **Graves, carved houses, boulders and trees by the raised rock [code]** (heights.py 9d): walkability's raise of the
  flat rock beside paths turned the solid non-rock tiles round it (Mt. Pyre's grave plinths, Sootopolis's carved houses,
  fences, signs) into face tiles: their surface rose to the rock's top and buried what stands on them (graves 12 deep;
  outdoor_check layer gake01a/gate_1, c8_gake01w2/sth03_1, /vtou_kabe01 - same-facing, both drawn, not back to back).
  They now stay flat (F.noface; ground.face_tile honours it, so prop plinths and wall blocks stand there) with the skirt
  at their edge; trees and ledge caps keep their faces. Trees, boulders and bushes embedded in a raised mass (rock on
  two sides, no path beside them) rise with it: they stood in one-level pits (Mt. Chimney, Jagged Pass, Mt. Pyre).
- **Route 103's east sea [code]** (heights.py 4b): one body of water whose surf shores stand at two heights one level
  apart (Oldale's side 16, the east beach 0) took the nearest shore's height: a sandy wall across open water down its
  middle. Open water (100+ tiles) with shores one level apart now lies at one level (surface flush with the lower
  shore, 16 under the higher: both under the 20-unit surf start); Field.record keeps water records off the y-0 ground
  rewrite, step 11 gives the sea outside the map the water's own level. Ponds keep their old rule (Route 120's pond:
  its banks need it).
- **Mt. Chimney's crater [code]** (heights.py 9e): the lava pool lies at one height (its tiles took 72/81/88/92 from
  the rock round them: a rock ridge ran diagonally across the lava). **Tall faces in Mt. Chimney / Jagged Pass**
  (world.py retex): yamagake01 renamed to out57_gake01a showed its clear foot rows where two tiers meet (holes 87+42 px);
  now banded like Route 112's red rock (heights._banded).
- **Big sea rocks [code]** (ground.py draw_rocks, heights.raise_sea_rock): the one-card masses are lifted as one piece
  (_as_one): the card leans north over the shoal behind the rock, and the per-tile lift floated its peak away from its
  base (Route 125 by Shoal Cave, Route 128); rock-class corner tiles inside a mass's box join its card.
- **Fortree [code]** (world.py forest_fill): blocked tree tiles round the tree houses get one-tile trees (the houses
  are on stilts since map_glitch_fix and hold no trees), except beside a house's side wall (the model is wider than
  Sapphire's footprint: a tree card there lay 1 unit from the wall) and by the big trees.
- Checks (HEAD 9b691e0 -> after, Sapphire; Ruby the same): walk_diff OPEN town 19 -> 15, route 9 -> 9, other outdoor
  9 -> 9, cave 84 -> 0 (notes/CAVES.md), dive 0; outdoor_check layer 39 -> 36 (the 5 grave/carved-house pairs gone; new:
  a sea rock card 0.66 from a skirt on Route 103), hole 24 -> 21 (Mt. Chimney 4 cells / 170 px -> 2 / 19 px, Jagged
  Pass 2 -> 0; new: 1 px on Route 103), cull 235 -> 232; walk/door/bld/zone/tex/place/size 0 -> 0; caves_check h 13 -> 14
  (a 6 px hole at Victory Road B2F (41, 24), one view), t 42 -> 42; npc_check 0 over; check_exits unchanged.
- Build order (report): rebuild_slice.sh runs world.py (whose open_uncovered reads the building models' geometry)
  before it rebuilds the models, so a world is made from the previous models (in a fresh folder: none, two Rustboro Gym
  front tiles stayed solid). Running world.py after the models, or twice, avoids it.

## Emerald's world (emerald_world, 2026-10-12)
HOENN_VERSION=emerald builds the same world machinery on pokeemerald's maps (notes/EMERALD.md "Phase 2: Emerald's outdoor
world"): `converter/gba.py world_repo()` (Repo(pokeruby) for Sapphire/Ruby, the Emerald view for Emerald) is what
plan_map.py, world.py, the terrain modules, outdoor_check.py and walk_diff.py read; plans go to data/plans/emerald/
(`version.plan_path`), the world to work/world_emerald. New world.py hooks, inert without settings (no Sapphire/Ruby map
has one): a map's `retile` rules (`retile_map`, its tiles drawn as another class: Emerald's structures without a model
yet), a town file's `prop_moves`, a standalone group's `order` (the order its maps' doors go into the zone), and in
Emerald only a signboard on sign tiles no Sapphire sign stands on and a closed placeholder door for a room not built yet
(status `todo`), so the shared rooms' exits keep their door numbers. Sapphire/Ruby outputs are byte-identical
(work/agents/emerald_world/proof/).

## Dewford bug report: forest gap hedge, cave mouths, beach rocks (dewford_fix, 2026-10-12)
User (Ruby v16.5): "an invisible wall at the bottom of Dewford", "the entrance to Granite Cave looks glitched", "the
Stardust you pick up next to the fisherman looks glitched". Built on v16.6 (work/agents/dewford_fix/v167.patch; v16.7
is built from the tag, notes/RESUME.md); proofs screenshots/dewford_fix/ (Ruby and Sapphire, before = the v16.6 release
ROMs with the Littleroot test-warp kit, after = the v16.6 + patch builds), renders work/agents/dewford_fix/render/ba/.
- **The forest's gap row [code]** (world.py build_cell): the forest outside a map leaves the row south of the map's
  walkable tiles open (DECISIONS 2026-10-06, so Gen 5's camera doesn't hide the player on the map's last row). That row
  is solid ground outside the map, drawn as the ground beside it: Dewford's beach went on a row further than you could
  walk (walk_diff listed it as intended, OPEN 'outside every map'). It now gets Black 2's hedge (ground.py hedge,
  Striaton's plant01, 16 units at the ridge: the player in front of it stays in view), one run per row and height,
  carried on across chunk edges (hedge ends=). Same rows elsewhere, all hedged (128 tiles): Dewford, Littleroot,
  Petalburg, Verdanturf, Fallarbor, Fortree, Routes 102, 106 (by Granite Cave), 116, 117, 123, Safari Zone SW/SE.
- **Cave mouths [code]** (heights.py 9d): the walkability pass (v16.4) raised a cliff tile level with the path beside
  it one level; at a cave mouth that hit the rock beside the door on the door row, where terrain/cave_mouth.py stands
  the frame on the ground: a flat-topped block a level high stuck out beside the opening (Granite Cave: on its right).
  9d now leaves the door row within the frame's span alone. Changed: 15 mouths (Route 105 Island Cave, 106 Granite
  Cave, 110, 111, 112 x2, 114 Meteor Falls, 120, 122 Mt. Pyre, 125 Shoal Cave, Verdanturf Rusturf Tunnel, Lilycove,
  Ever Grande Victory Road, Sky Pillar, Sootopolis Cave of Origin). With the door row down, a boulder beside the raised
  rock became the low tile that holds the rock face (buried: Route 106's by the fisherman): cave_mouth.Drawn keeps
  boulders/signs beside its raised rock flat, the skirt at their edge (4 tiles: Route 106 x2, Route 125, Sky Pillar).
  The rock at a mouth's foot on a sand approach takes the sand (ground.py ground_under; grass showed as green strips:
  Route 105, 106, 111).
- **Beach rocks [code]** (ground.py rock_wet): a rock with any water tile in the ring round it (diagonals too) was
  drawn as Black 2's sea rock at the water's level, 8 units down: on a beach or a lawn next to water only a grey
  sliver of it showed (Route 106's (53,12), where Sapphire hides the Stardust). A rock with walkable land beside it and
  no water drawn under it (water.py look) is now a land rock on the ground (94 rocks: Route 126 31, Mossdeep 9,
  Lavaridge 8, Rustboro 6, Routes 118/124 6 each, Route 132 4, Lilycove/Routes 120/127/134/Faraway Island 3 each,
  Routes 129 2, 103/106/114/115/125/128 and Safari Zone NW 1).
- Checks (v16.6 -> after, Sapphire and Ruby): walk_diff outdoor intended 131 -> 3 (the gap rows), every open count
  unchanged (town 15, route 9, outdoor 9, interior 680, cave 0); outdoor_check place/size/walk/door/bld/zone/tex 0;
  rooms_check 0; caves_check t 42 (unchanged); script_check 0 open; ROMs: layout identical to v16.6, only a/0/0/8 (78
  map chunks) differs; menu save margin 28,896 B (unchanged).
- Left: in the mouths whose rock beside the door's upper row was already at tier 1 (Route 111, Route 120, Lilycove's
  cove), world.py's ground still covers that tile's cut half: a small light square in the opening's top corners
  (previously hidden behind the 9d blocks; world.py's ground is not cut for cave_mouth's opening).
