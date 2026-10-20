# Interiors (Sapphire rooms as Black 2 interior chunks) — started 2026-10-06

## Coordinates (fixed): Sapphire tile (x, y) → zone tile (x, z) = (x + ox, y + oz)

Every room is one chunk in the zone's own 1x1 matrix, so zone tiles = chunk tiles (0..31). World units = tile * 16 + 8.

| Zone | Room (pokeruby map) | Offset (ox, oz) | Exit / door warp (zone tiles) | Stair warp (zone tile) |
|---|---|---|---|---|
| 394 | InsideOfTruck | (8, 8) | none (exit by trigger): exit tiles Sapphire (4,1..3) = (12, 9..11); triggers Sapphire (3,1..3) = (11, 9..11) | — |
| 390 | LittlerootTown_BrendansHouse_1F | (1, 0) | warp 0: (9, 8)-(10, 8), 2x1, type 1, = Sapphire's mat (8,8)-(9,8) | warp 1: (9, 2) = Sapphire (8,2), entered walking north |
| 391 | LittlerootTown_BrendansHouse_2F | (1, 1) | — | warp 0: (8, 2) = Sapphire (7,1), entered walking north |
| 392 | LittlerootTown_MaysHouse_1F | (1, 0) | warp 0: (2, 8)-(3, 8), = Sapphire's mat (1,8)-(2,8) | warp 1: (3, 2) = Sapphire (2,2) |
| 393 | LittlerootTown_MaysHouse_2F | (1, 1) | — | warp 0: (2, 2) = Sapphire (1,1) |
| 396 | LittlerootTown_ProfessorBirchsLab | (1, 1) | warp 0: (7, 13)-(8, 13), = Sapphire's mat (6,12)-(7,12) | — |

- Exit warps (type 1) are Sapphire's door mats themselves: you arrive on the mat facing north and leave by pressing
  down while standing on it — Black 2's mats work exactly like Sapphire's south-arrow warps (tested; stepping sideways
  along the mat does not warp). The stone "genkan" notch drawn below the mat is only Black 2's entrance look (solid).
- Stairs: type 2 warp on the stair tile (solid, as Black 2 does), direction 2 (entered from its south side, walking
  north); arriving you step south off it.
- Truck: models_truck.py's own origin (8, 8); the player start (Sapphire (2,2)) is (10, 10).

## NPC order (ObjInitNPCGPos etc. take the INDEX in the zone's NPC list, not the uid)

| Zone | index → uid (who) |
|---|---|
| 390 Brendan 1F | 0→1 Mom, 1→2 mover (box), 2→3 mover (TV), 3→4 rival's mom, 4→5 Norman |
| 391 Brendan 2F | 0→1 rival Brendan, 1→14 Mom |
| 392 May 1F | 0→1 Mom, 1→2 mover (TV), 2→3 mover (box), 3→4 rival's mom, 4→5 Norman |
| 393 May 2F | 0→1 rival May, 1→14 Mom (Sapphire's Pichu doll, id 15, has no Black 2 sprite) |
| 394 truck | none |
| 396 lab | 0→0 Birch, 1→1 Aide (the rival, Sapphire id 3, is not placed yet) |

The order is the order of "npcs" in data/interiors/<zone>.json.

## Pipeline

    data/interior_layouts/<Map>.json  --b2tools/models_interior.py-->  work/interiors/<Map>/ terrain.dae, collision.per,
    (+ _styles.json, Sapphire's map)                                     placements.bin, room.json, palettes.txt, *.png
    b2tools/models_truck.py (the truck, its own builder)  ------------>  work/interiors/truck/ (same files + door.dae)
    zsh b2tools/rebuild_interiors.sh [NAME ...]   runs both builders and ToNsbmd (--vcol for recipe rooms) -> *.nsbmd
    data/interiors/<zone>.json  + build patch `interiors` (b2tools/patches/interiors.py)  -> the ROM
    python3 b2tools/preview_interior.py NAME      renders a room + its furniture (apicula) without the emulator

`rebuild_slice.sh` calls `rebuild_interiors.sh` before the ROM build; `agent_build.sh` uses the rooms already in
work/interiors (run rebuild_interiors.sh first after changing a recipe). The patch must run after `hoenn_world`
(it appends chunks after the overworld's).

### What the patch does per zone with "room"
1. Appends the room's chunk (`WB`: terrain NSBMD, collision, placements) to a/0/0/8.
2. Points the zone's matrix at it: the zone's own 1x1 matrix is rewritten in place (all of 390-396 have their own:
   35-42); a matrix shared with a zone that is not being installed, or not 1x1, gets a new matrix (a/0/0/9 has a reserve).
3. Merges the room's map textures (`room.json` "map_textures": texture → source map texture set) into the zone area's
   texture set(s) with `nsbtx.merge` (lossless, existing bytes untouched; seasonal areas 2-281 get all four).
4. Adds furniture models the area's interior building pack lacks (copied with their info record from the Black 2
   pack that has them, or from a file for new models like the truck door) and merges their texture/palette pairs into
   the pack's texture set a/1/7/5. Added so far: pack 2 (area 284, zones 390-395) + shelf03 (13), art02 (78),
   monitor01 (144), truck door (200); pack 3 (area 285, the lab) + shelf03 (13).
5. Rewrites the zone's camera box (a/1/0/9 entry `cam_bound`, same 28 bytes; skipped and reported if another zone uses
   it) and its fly point (the exit mat, or the truck's start tile).
6. Entities: "npcs"/"signs"/"warps"/"triggers" from the json (Sapphire tiles + the room's offset). Map scripts: the
   zone's `src/field_scripts/<init number>_*.s` if it exists, otherwise an EMPTY table (Black 2's tables start Black 2
   scenes by script number: zone 390's "0x407d == 0 → script 4" ran every frame and froze the player).

### Zone json (data/interiors/<zone>.json)
- `npcs`: `uid, model, script, dir (0 up, 1 down, 2 left, 3 right), at [x, y] (Sapphire), flag (hide-if-set, the
  number from hoenn.h), move (3 = wander) + range [w, h]`.
- `signs`: `script, at, dir` — tested: dir 0 = read facing north only (Sapphire's PLAYER_FACING_NORTH and TV tiles),
  dir 4 = from any side. cond 0 (Black 2's interior objects).
- `warps`: `at` = any Sapphire tile of one of the room's warp spots (room.json "warp_spots"), `to` = [zone, warp].
  The list order is the warp index other zones point at.
- `triggers`: `script, var, value, at, w, h` (type 0, as most of Black 2's).
- Without "room", x/z are zone tiles (the old format).

### Test switch
`HOENN_TEST_INTERIOR_DOOR=<zone>`: Littleroot's warp 1 (May's door) leads to that zone, and a warp on the zone's fly
tile leads back (used to visit the truck, which no door reaches).

## How Black 2 builds a room (chunks 838, 842, 977, 1049; what models_interior.py copies)
- Floor y −2; collision cells `0000 0300 0000 8000` (walkable) / `0000 0300 0100 8100` (solid), as every interior.
- Walls 50 high (y −2..48) standing 12 units north of the first floor row and 3 units outside the side columns; one
  texture over the whole height (e.g. m_h05_kabe, 32x64, ~64 units per repeat).
- Shading is baked into vertex colours: back wall 1.0 at the bottom → 0.81 at the top, side walls 0.48, floor strips
  along the back wall 0.81 / side walls 0.84, the entrance fading to black. Our DAE → `ToNsbmd --vcol` keeps them
  (new switch: CTRMap's writer with preferVColOverNormal; checked with apicula and in the game).
- Black: 16-unit wall caps at y 48, the cut ends of the side walls and a floor lip down to y −18 along the open south
  side. The clear colour is black, so the room floats in black.
- Entrance: a one-tile notch below the door mat (stone texture); Black 2's mats are type-1 warps.
- Furniture = building placements (u16 angle; 0x4000 = 90°: a model's front faces south at 0, east at 90). Black 2
  puts chairs only on solid tiles and floor cushions (chushion01/02) on walkable ones; stairs: stair_u01 rises toward
  its −x (rot 270 = north), stair_d01 descends toward its +x (rot 90 = north) inside a hole cut in the floor.
- Camera box a/1/0/9: `u32 1; u32 1, u32 0; s32 xmin, xmax, zmin, zmax` (world units of the camera target). Black 2's
  rooms: x = walkable tile centres ± 45, z = first walkable row centre + 6 .. last row centre − 32 (tested: a smaller
  zmax pulls the view north).

## Recipe for a new room (the other ~230 Hoenn interiors)
1. Render the map: `cd converter && python3 render.py ../external/pokeruby <Map>`.
2. Pick a free interior zone with its own 1x1 matrix (or let the patch append one) and an interior area; note its
   script/text numbers (zone header) — `python3 b2tools/zones.py <zone>`.
3. Write data/interior_layouts/<Map>.json: style, floor rects (rows that have floor, incl. the furniture row along
   the back wall), furniture by Black 2 model name at Sapphire tiles (see the docstring of models_interior.py for the
   keys), rugs (`mats`), wall `decals`, `block` for tiles to make solid. Exits (south-arrow mats) and stairs/doors
   (MB_NON_ANIMATED_DOOR) are read from Sapphire's warp events. Mirror-image maps: `mirror_of`.
   Black 2 furniture: `python3 b2tools/preview_interior.py` caches every model it uses as DAE in
   work/interiors/_models; sizes come from each model's own bounding box (bmd_box), so `tile`/`tiles` centre them.
4. `zsh b2tools/rebuild_interiors.sh <Map>` and `python3 b2tools/preview_interior.py <Map>`; iterate.
5. Write data/interiors/<zone>.json (npcs/signs/warps/triggers) and the zone's script + text files
   (src/field_scripts/<scripts>_*.s, src/text/script/<text>_*.txt); objects use the SystemMsg pattern, people
   ParentActorMsg (see 0780_brendans_house_1f.s).
6. Point the outside door at the zone's exit warp (hoenn_world.json "warps": Sapphire map → warp index).
7. Build (`HOENN_AGENT=<you> zsh b2tools/agent_build.sh interiors ...`) and walk in.

## The rooms (2026-10-06)
| Room | Style / textures | Furniture (Black 2 models) | Deviations from Sapphire |
|---|---|---|---|
| Brendan/May 1F | house: m_h05_kabe wall, m_b08_yuka floor, m_b08_genkan entrance (set 349), rug m_b08_mat3, door mat in70_mat1 (351) | ref01 fridge, sink01, shelf02 glass cabinet, 2× win01, stair_u01, shelf03 counter, monitor01 TV (pack 24), table01 + 4 chushion02 | the right part's back wall is one row south (as Sapphire's art) except the stair recess; dining chairs are cushions (walkable, Black 2 convention); the octagonal table is ~2.8 tiles (overlaps the cushion tiles' inner edge) |
| Brendan/May 2F | house, red rug m_b08_mat | pcdesk01 (PC + notebook), art02 framed map (pack 3) as the Hoenn map, wii01 as the GameCube, monitor01 TV, stair_d01 in a floor hole, bed01, wall clock = picture in69_clock01 (set 350) | Black 2 has no wall-clock or wall-map model; the bed head (1,4) (Sapphire MB_IMPASSABLE_SOUTH_AND_NORTH) is solid; the desk chair is left out (walkable tile) |
| Birch's Lab | lab: m_lab01_01 floor, m_lab01_04 wall, m_lab01_08 entrance (set 285), door mat chip_mat | shelf01 bookshelves, box01/box02 for Sapphire's yellow boxes/cabinets, plant01, pcdesk02 PCs, shelf03 white counters (the desk with books), chair01, desk02, machine_l02 (Juniper's lab machine) as THE machine, machine02 white cabinet, chushion02 for the walkable green chairs | boxes stand in for Sapphire's yellow cabinets; the rival (story) is not placed |
| Truck | models_truck.py (Plasma Frigate metal, set 379) | box01/box02, rear door model res 200 | exit = the lead's trigger script 20 |

## Known gaps
- The bedroom PC runs Black 2's own Pokémon Center PC (global script 10090, room_pc 2026-10-08: `RTCallGlobal 10090` in
  Script_3 of 0782 / 0786; "<player> booted up the PC." is Black 2's own line 0 of text 479, word for word Sapphire's).
  Sapphire's Item Storage and Decoration do not exist in Black 2 (see notes/STORY_SPECIALS.md row 83); the region map is
  text only; the clock is Sapphire's "stopped" line (setting it is the lead's story).
- Movers are Black 2 workers (code 54): Black 2 has no walking Machoke.
- Sapphire's Pichu doll and the lab rival are not placed; the rival's-house variants of the moms follow Sapphire's
  flags (the truck script must set them as Sapphire's InsideOfTruck_EventScript_15FC45/68 does).

## Big rooms, camera boxes, gym features (gyms_league agent, 2026-10-06)

### Builder (b2tools/models_interior.py) — every key optional, older recipes build byte-identically (checked on all 175)
- **Big rooms** (bigger than one chunk incl. one tile of wall/lip): the room is spread over a w x h matrix of chunks
  the way Black 2's big interiors are (P2 Lab zone 239: matrix 191 = 1x2 chunks 935/970; interior map type 16 loads
  every chunk of the matrix). The model is built in chunk-0 units and cut at the chunk edges (Sutherland-Hodgman, a face
  lying on an edge goes to the chunk east/south of it); each chunk gets its own collision (32x32 of the room's zone tiles)
  and placements (each model in the chunk holding its centre, positions relative to that chunk). Outputs: terrain.dae /
  collision.per / placements.bin = chunk 0 as before, terrain_c<k>.dae (converted to .nsbmd by the builder itself with
  ToNsbmd --vcol, classes from HOENN_JAVA_DIR or work/java), collision_c<k>.per, placements_c<k>.bin, terrain_all.dae
  (previews), room.json "matrix": [w, h] and "chunks" (row-major; null = empty cell). Zone tiles run over the matrix.
  Recipe "matrix": [w, h] forces a size. Tested: Corridor 4 (1x2), Petalburg Gym (1x4) walked across chunk edges.
- `floor_tex`: floor texture regions (part of the floor, not layered): rect / units, tex, src, size, size_v, stretch, rot, uv.
- `blocks`: raised boxes (gym walls, rails, pillars, basins): rect / units / tiles, h, top, side, shades, "use" = a
  block style in a _styles*.json. Only top/south/west/east faces. Collision stays Sapphire's.
- `open`: tile rects (or true) outside the floor with no wall: the floor edge there gets only a black lip
  (Black 2's League walkways floating in the dark).
- `ledges: true`: Sapphire's jump tiles (MB_JUMP_* 0x38-0x3B) become Black 2 ledge cells (class 0x72-0x75, flags 1,
  as Route 2's). Opt-in so other rooms stay unchanged. Tested on Lavaridge B1F: down jumps over (2 tiles), up is blocked.

### Installer (b2tools/patches/interiors.py)
- Big rooms: one chunk appended per cell, a w x h format-0 matrix.
- **Matrices**: a matrix is rewritten in place only when exactly one zone names it; zones sharing one (also several of
  ours: Nacrene's 22/23/24 share matrix 31) each get a new matrix. Before, the last room installed overwrote the
  others (zone 23 showed zone 24's room; found in the emulator).
- **Camera boxes**: a zone that is the only user of its a/1/0/9 entry gets it rewritten in place; a zone whose box is
  shared, of another size or missing (0xFFFF) gets one of the 165 entries no zone header names (all 28 bytes).
  a/1/0/9 has no RESERVE in build_rom.py, so appending entries would move every later ROM file and break the
  savestates; same-size rewrites keep the layout. The only other reader of box ids is FieldCameraBoundary_ChangeZone
  (fieldmap.c, via the zone header). 44 zones were fixed in the first build (e.g. Slateport Fan Club, tested).
- Room json `bgm` (one SEQ for all seasons; Gyms 1062 = SEQ_BGM_GYM, League 1072) and `battle_bg` (header flags
  bits 5-9; Black 2's Elite Four rooms use 11-14, the Champion 16) override the parent town's.

### world.py
- A door to a 'big' room (data/hoenn_interiors.json) that has its data/interiors json gets its door warp too, appended
  after every other door of the zone (no existing door index moves). Needs a world rebuild (rebuild_slice.sh); tested
  with a copy (work/agents/gyms_league/world): Petalburg City door 5, Mossdeep City door 9.

### Warps that fire on stepping (tested)
- Black 2 type-1 warps do not fire when the player steps onto them (only when bumping out of them, as the exit mats);
  non-type-1 warps fire when walking into them in their direction (ov012 GetWarpIDByPlayerPos /
  CheckWarpDirectionMatch: dir 1 = down, 2 = up, 3 = right, 4 = left; 0 matches no direction = arrival spot only).
- Sapphire's step-on warps (Lavaridge holes 0x68 and vents 0x29, ladders 0x61) = a step trigger with workId 0 (always,
  FindTriggerAtPosGrid) running `MapChangeCore zone, x, 0, z, 1` to the destination tile, plus a dir-0 warp record on
  the tile as the arrival spot. Tested: Lavaridge 1F hole -> B1F, Sootopolis 1F ladder -> B1F.
- Zone 63 (Black 2's Nimbasa Gym) spawns Elesa's runway audience whatever room is installed: never use it
  (allocate_interiors.py NEVER; Phoebe's room moved to zone 123).

### The Gym and League rooms (b2tools/gyms_league_rooms.py writes recipes, styles, zone jsons, step scripts)
| Room (zone) | Area (pack) | Art | Story phase (not built) |
|---|---|---|---|
| Rustboro Gym (583) | 308 Driftveil Gym (26) | tan cobbles (258), rock blocks, sand dais | Roxanne, 2 trainers, guide, statue plaques |
| Dewford Gym (25) | 334 Marshal (52) | maze floating in the dark, low walls | Brawly, 3 trainers, guide; the darkness lifting |
| Mauville Gym (239) | 304 Nimbasa Gym (22) | white stage, poles, barriers = d6_yuka_biri02 | Wattson, 4 trainers; barrier switches |
| Lavaridge 1F/B1F (145/148) | 388 Reversal Mtn lava (80) | sand, lava-rock bands, holes, vents, ledges | Flannery, buried trainers; fall/jet animations |
| Petalburg Gym (452, 1x4) | 286 Aspertia Gym school (4) | 9 wood rooms, mats, door_pwood01 doors | Norman, Wally's tutorial, 7 trainers; doors open per trainer |
| Fortree Gym (119) | 309 Mistralton Gym (27) | turf, wooden posts, ledges | Winona, 4 trainers; rotating gates |
| Mossdeep Gym (322) | 335 Caitlin (53) | starry floor, white walls, arrow/stop tiles | Tate & Liza, 6 trainers; spin tiles + switches |
| Sootopolis 1F/B1F (23/24) | 292 Cold Storage (10) | ice rooms, fountains, ice ramps; snow cave | Wallace, 8 trainers; thin ice; exit (Sootopolis not built) |
| Corridors 1-5 (35/36/42/43/47) | 334 Marshal (52) | stairs between rails floating in the dark, door_h5_in | - |
| Sidney / Phoebe / Glacia / Drake (79/123/53/51) | 333 / 315 / 292 / 312 | Grimsley / Shauntal / Cold Storage / Drayden sets | the member; door opens and entrance closes after the battle |
| Champion (34) | 319 Iris (37) | octagon floating in the dark, stairs | Steven, rival, Birch; Hall of Fame (not built) |

gyms_league tools: `b2tools/gyms_league_rooms.py` (writes the 20 recipes, `_styles_gyms_league.json`, zone jsons and the
step-trigger scripts), `gyms_league_build.sh` (agent build; GL_WORLD=1 uses work/agents/gyms_league/world, a world.py
copy with the big rooms' doors), `gyms_league_test.sh ZONE,X,Z OUT.png MOVES` (one build + one silent walk),
`gyms_league_view.py` (renders Black 2 zones/texture sets/models, previews big rooms via terrain_all.dae),
`gyms_league_grid.py MAP beh` (Sapphire walk grid + behaviours), `gyms_league_proof.py` (proof sheets).
Proofs: screenshots/gyms_league/ (Sapphire render | town door | rooms, every Gym, the League chain).

## Room cleanup (rooms_cleanup agent, 2026-10-06): stairs, furniture footprints, flicker, scene paths
User (melonDS, v11): "walking through stairs instead of up them", "May's mom walks through the table", "the rug is
flashing in the lab". Checker: `python3 b2tools/rooms_check.py [--dir ROOMS] [--rom ROM] [--kinds abcdefg] [--summary]`
(reads only the built rooms: room.json, collision, terrain; `ROOMS_CHECK_MODELS=DIR` to check the lead's work/interiors
without writing there). Kinds: a stairs, b furniture over walkable tiles, c people on solid tiles / in furniture,
d scripted paths (the Littleroot scenes with their scripts' start tiles + every room script's ActorCmdExec) through
solid tiles or furniture, e warps/mats/arrivals, f layered surfaces < 1.95 units (melonDS z-fighting), g camera boxes.
Before (v11's rooms) -> after: a 120 -> 0, b 732 -> 2, c 43 -> 0, d 10 -> 0, e 22 -> 0, f 396 -> 2, g 0 -> 0.

How Black 2 does stairs (chunks 842/843/1049/828/829, all its houses): the warp tile is the first tile of the flight;
stair_u01's foot (model x +16) / stair_d01's top step (x -16) lies on the warp tile's approach edge, the model's axis
(z 0) through the tile centre; the stair tiles are solid with a **45-degree collision plane** (slope 8/14/11/16 = rising
N/S/E/W, 0 at the approach edge, 16 a tile: ov036's height tables, b2tools/terrain/heights.py). Black 2's houses run
their stairs sideways; Sapphire's are entered walking north, so ours rise north (the dungeon stairs d0stair do the same).
Found in the emulator: during a stair warp the player walks onto the warp tile, and a sprite leaning back with the
camera went behind the back wall a tile north of the first floor row (v11: the player was swallowed). Now
(models_interior.py STAIR_MODELS, recipe furniture `{"m": "stair_u01"|"stair_d01", "stair": [x, z], "dir": "N"}`):
the builder places the model from the warp tile, cuts the room's walls round it (a recess as big as the model, so no
wall cuts through the steps and the shaft of stair_d01 is all inside), makes stair_d01's floor opening, writes the
planes, and the warp's walk-in direction (warp_spots dir) follows "dir". Tested: Brendan's and May's houses, Rustboro
Flat 1, Cove Lily Motel: the player climbs the steps in view, goes down into the stairwell, and arrives the same way.
(Savestates taken inside a room keep that room's geometry in RAM: test from a state outside, e.g. base_littleroot.)

Furniture: Black 2 lets furniture reach at most ~2 units into a walkable tile (calibrated on its rooms). Too-big models
are resized copies (DERIVED_MODELS: Black 2's BMD with only its MDL0 posScale/box scale changed, res ids 300+, written
next to the room, installed by patches/interiors.py with the base model's info record and textures; preview_interior
draws them scaled): table01_2x2 (Sapphire's 2x2 tables: houses, Littleroot, Centers, League), box02_1, bed01_1w,
table02_2w, pcdesk02_2, d6_yuka_biri02_1 (Mauville barriers), shelf02_1, pc01_1 (slot machines), object02_1 (Gym
statues), pcshelf01_2 / shelf05_1 (house bookshelves). Walkable seats (Sapphire's stools, sofas, benches) are sunk to
cushion height (Black 2 puts only cushions on walkable tiles). May's 2F desk stood on her stairwell (mirror() did not
swap w_edge/e_edge: fixed).

Flicker (LAYER = 2, Black 2's own rug spacing): every rug >= 2 above the floor / the block or rug under it, every wall
decal >= 2 off the wall / the decal under it, a piece standing on a rug or piece lifted so its shadow is >= 2 above,
a floor cushion moved sideways off a neighbour's shadow; Littleroot's rugs and the lab's door mat lay 1 unit above the
floor (the lab's flashing rug). Overlapping counter pieces alternate 2 units lower/back (shops_recipes.py).
Gym exits and Mt. Pyre / the Dept. Store elevator got Sapphire's exit mat (in70_mat1).
Generators kept in step (re-running them reproduces the fixes): converter/gen_interior_recipes_houses.py +
data/interior_tiles_houses.json, b2tools/centers_rooms.py (masters OldaleTown_PokemonCenter_1F/2F), shops_recipes.py,
gyms_league_rooms.py, facilities_pyre.py. Left: the Day-Care back door and Devon 1F's doorway model reach ~1 unit into
their own door tiles; Sootopolis Gym's statues stand 1.75 units off the ice walls.
Proofs: screenshots/rooms_cleanup/.

## The Abandoned Ship and the hideouts (ship_hideouts agent, 2026-10-06)
Tags: **[code]** decomp/disassembly, **[bytes]** measured in the dump, **[test]** seen in DeSmuME.

| Rooms (zones) | Black 2 look (area / set / pack) | Generator |
|---|---|---|
| AbandonedShip_Deck (74), Corridors_1F/B1F (72/73), CaptainsOffice (71), Rooms_1F (91), Rooms2_1F (89), Rooms_B1F (92), Rooms2_B1F (90), Room_B1F (88) | Royal Unova cruise ship (zone 52): area 337, set 337, pack 55 (cabin_door, bed01, dust01, chair01 ...) | `b2tools/ship_hideouts_rooms.py` |
| AquaHideout_1F/B1F/B2F (2/5/10) | Plasma Frigate (zones 553-583): area 379, set 379, pack 76 (warp01-03 panels); its Team Plasma emblem textures are never used | same |
| MagmaHideout_1F/B1F/B2F (228/231/234): recipes built, **zone files only with `--magma`** | same, other floor/wall | same |

`python3 b2tools/ship_hideouts_rooms.py [Map ...] [--magma]` writes the recipes, `_styles_ship_hideouts.json`, the zone
jsons (warps in Sapphire's order, one per Sapphire warp on its own tile), the rooms' script/text files (simple people,
signs, Sapphire's furniture messages: trash cans "It's empty.", blueprints) and Rooms_B1F's encounter file (41, via
gen_caves.encounters). `HOENN_AGENT=ship_hideouts zsh b2tools/ship_hideouts_build.sh [ROOM ...]` = own world + zone
files + rooms + ROM (NOWORLD=1, SH_ARGS=--magma, SH_PATCHES=test_cave_kit for badges/HMs in tests).
Shapes: floor = Sapphire's walkable tiles + its furniture tiles (beds, tables, crates, machines, rails, pool banks) +
water; walls follow the outline; collision is Sapphire's. Furniture is found from Sapphire's metatile ids (tables in
the generator; labelled maps: work/agents/ship_hideouts/labels). Black 2 allows 32 models per chunk: crates are
stacked 2x2 (box02), a leftover crate row against a wall becomes wall, MagmaHideout_B1F's crates are wall.

New builder keys (models_interior.py, opt-in; the 196 other rooms and the 6 committed caves build byte-identically):
`raised` (walkable tiles at a collision height), `ramps` (45-degree slopes, 16 units a tile, slope planes as the
stair tiles), `water` (Wellspring's cave water cells 0x3f/0x16|0x12 at -8 + drawn water and banks; `solid` = drawn
only), decal `uv` (a quarter of an atlas texture: portholes maq_pt01, lifebuoys maq_pt11) and `face_z`.

Black 2 facts used:
- **Warp panels** = a type-5, dir-0 warp on the panel tile + building model warp01/02/03 (pack 76 res 106-108, type
  10) on it: the Plasma Frigate's zones 553/556/559/560/575-578 **[bytes]**; stepping on one warps, arriving on one does
  not re-fire; same-zone panels work (Aqua B1F/B2F) **[test]**. (Also `MapChangeWarpPad` = script command 191,
  `EventMapChangeWarpPad_Create`, transition 5 + spin-down, for scripted panels **[code]**.)
- **Surfing survives a warp**: surfing into a door lands you surfing in the next zone (Aqua 1F's water arrival works;
  on the ship's dock you dismount by moving onto land) **[test]**. FieldPlayerGrid_UpdateSurfBrake checks warps when
  you bump into a wall while surfing (ov036 0x0219c850 -> CheckWarpAtHitWall) **[code]**.
- A warp fires only within 2 units of its y (CheckWarpPositionMatch) **[code]**: a door entered by surfing needs the
  water's height (Hoenn sea: −8), see "World fixes" below **[test]**.
- **One walk-in warp per tile** (mtpyre, 2026-10-19): of several non-mat warps stacked on one solid tile (one per walking
  direction), only the first fires; walking into the tile in another warp's direction does nothing **[test]**. Mt. Pyre's
  holes were built that way and only their north side worked: 5F's two holes (east side only) trapped a player who fell
  from 6F (Discord). A tile entered from several sides wants a step trigger on a walkable tile instead
  (b2tools/facilities_pyre.py: the holes fall by trigger, as Gen 3 falls when you step on MB_MT_PYRE_HOLE).
  `interior_sweep_check.py zones ROM` (run by rooms_check --rom) reports stacked walk-in warps.
- Surf in a room: Wellspring's water cells work indoors (Rooms_B1F's flooded cabin: surf prompt, surfing, back on the
  carpet) **[test]**.
- Script warps (MapChangeCore) place the player in 16-unit levels, so the deck's levels are 16 / 48 / 80.

The deck: two levels and the dock (Sapphire draws the superstructure in its 3/4 view, elevation 3 everywhere): dock at
16, gangway ramp to the lower deck at 48, stairs ramp to the upper deck (the deckhouse roof) at 80, the bridge with the
captain's door; holes = black pits; sea = water floor around the hull **[test]** (walked dock -> gangway -> lower deck ->
stairs -> upper deck -> captain's office and back).

Tested (DeSmuME, proofs `screenshots/ship_hideouts/`): Route 108 -> deck (with the door-height fix); every door kind of
the ship (deck doors, cabin doors, exit mats, corridor arrow stairs 1F <-> B1F both ways, the storage room) and the
flooded cabin's surf; Lilycove -> Aqua 1F surfing in; 1F door -> B1F; panels (31,4)<->(27,12), (27,4)->(3,15),
(32,19)->(20,4); B1F door (18,1) -> B2F; B2F panel (31,8)->(5,8); B2F door (3,3) -> B1F.

### World fixes needed (world.py, not this agent's file) — done by world_fixes 2026-10-06 (notes/WORLD.md "World fixes")
1. Water doors: Route 108's ship stairs (Sapphire (29,6), MB_STAIRS_OUTSIDE_ABANDONED_SHIP 0x1B) and Lilycove's cove
   (70,5) (MB_WATER_DOOR 0x6C) are entered surfing; world.py gives every door y 0, the surfing player is at −8, so
   they never fire. Door y = the water's collision height (−8 here) makes both work **[test]**.
2. Route 108 return: leaving the ship you have dismounted on the deck, so you come out of the door walking onto the
   sea and stand on the water, stuck (`abandoned_ship_ingame.png`, last frame) **[test]**. Black 2's way: a walkable
   landing at Sapphire (29,6) (as Sapphire: the stairs tile is walkable) with the door on the hull tile north of it
   (y = landing height); then surf -> dismount on the landing -> walk into the door, and back. (Route 108's ship
   exterior is drawn as a grassy islet: the exterior agents' part.) The Aqua Hideout has no such problem: you never
   leave the water there.

### Story content left (listed by the generator's report)
Ship: Charlie (tuber trainer, Corridors_1F (5,10)), Duncan (sailor, Corridors_B1F (9,6)), Hal & Lois (double battle,
Rooms2_1F (6..7,13)), Capt. Stern's aide (CaptainsOffice (3,4): Scanner exchange), the storage room lock (Corridors_B1F
(11,4): Sapphire swaps the door metatile until FLAG_USED_STORAGE_KEY; in Black 2 move warp 5 away with ObjInitWarpGPos
in the zone init while locked; its sign script), FLAG_LANDMARK_ABANDONED_SHIP on the deck, the Storage Key item ball is
placed. The hidden floor (HiddenFloorCorridors/Rooms, keys, Scanner) is behind Dive: built by the dive agent with
this generator as a library (b2tools/dive_rooms.py, zones 173-176; notes/DIVE.md, which lists its story content).
Aqua Hideout: the grunts (VAR_1/VAR_2 sprites, FLAG_HIDE_GRUNT_1/2_BLOCKING_HIDEOUT, FLAG_HIDE_GRUNTS_HIDEOUTS), the
Electrode item balls (B1F (16,9)/(16,10)), the submarine shadow and Matt's scene (B2F coord events (28,16)/(28,17)),
the entrance's removal after Badge 7 (Lilycove's map script).

### Dive (research; built since: notes/DIVE.md)
Built by the dive agent (2026-10-06): a Hoenn dive table instead of the 4 Undella Bay entries, any number of
arrivals per underwater zone, the underwater maps and Seafloor Cavern with the cave builder; notes/DIVE.md. The
research as it was:
Black 2 has a Dive: global script 1243 asks "Would you like to Dive?" and runs `CallDiving 0` (script command 200 ->
EventDiveIn: player special state 3, `EventMapChangeDiveIn` to the dive zone's spawn, the surface spot remembered as
the next zone); surfacing is a script: `FieldSetNextZone zone, x, y, z` + `CallDiving 1` (Abyssal Ruins 0482.s
Script_3) **[code]**. Where you may dive is hard-coded: `GetAbyssalRuinsDiveZoneID` (ov036 0x021C3D50) ->
`DecideAbyssalRuinsDiveZoneByUndellaBayPos` (0x021C3D10): 4 entries of (zone, x, z, dest zone) at ov036 0x021D2540,
each a 3x3-tile square of Undella Bay (240) -> Abyssal Ruins 241-244 **[code][bytes]**. The underwater look is
`AbyssalRuinsCmd_StartUnderwaterEffect`, a script-plugin command only zones 241-245 have (script_plugin.c
sAbyssalRuinsZones) **[code]**. Proposal: point the dive table at a Hoenn table (pointer at 0x021C3D48 + the count
`cmp r3, #4`), one entry per 3x3 block of Sapphire's dive tiles, each to an underwater zone; add those zones to the
plugin's zone list (relocate it) for the underwater effect; build the underwater maps as normal rooms/caves with the
diving player; surface by scripts (FieldSetNextZone + CallDiving 1) on the tiles where Sapphire lets you surface.
Open points: one arrival per underwater zone (the zone's spawn), so big underwater maps need a zone per dive area or
a reposition script; Sapphire surfaces anywhere above surface water (Black 2 only through scripts). Seafloor Cavern
(10 maps, no zones allocated) is only reachable through Underwater4 -> Underwater_SeafloorCavern -> surfacing, so it
waits for that.

## Story fix-ups (story_fixups agent, 2026-10-07)
- **Room exits after a world change.** A room's exit says `"to": [zone, warp index]`; an outdoor zone keeps Black 2's
  warps and then gets world.json's doors, so an exit made before world.py changed a zone's door list points at the
  wrong door (the zone_rects change removed the "foreign" door copies: the Cycling Road gates, Trick House, Route 111/114/116
  houses, Verdanturf's houses, Fiery Path, Granite Cave were one door off). `python3 b2tools/check_exits.py [WORLD_DIR]
  [--fix]` checks every room exit against its Sapphire warp (outdoor doors, MAP_DYNAMIC = 256, room-to-room reported
  only); rebuild_slice.sh runs it as a report after the room generators. Rerunning the generators against a fresh world
  fixes their rooms (gen_interiors, gen_interior_recipes_houses, shops/centers/gyms_league/ship_hideouts/dive rooms,
  gen_caves); rooms no generator rewrites (Mt. Chimney's cable car station, Slateport Harbor, Battle Tower lobby,
  Lanette's house, Mt. Pyre 1F) were fixed with `--fix`. gyms_league_rooms.py now reads HOENN_WORLD_DIR and prefers a
  door's copy in its cell's zone, like the others.
- **Dynamic warps** (Sapphire MAP_DYNAMIC: the Dept. Store elevator): `"to": [zone, 256]`. Black 2's warp with dest id
  0x100 goes to GameData's next zone (ov035 EventMapChangeWarp_CreateFromEntity), which arriving on such a warp sets to
  where you came from (ov012 SetupZoneWarpArrival) and scripts set with FieldSetNextZone. gen_interiors.py writes it.
- **story_merge.py** also keeps a story agent's lines in the file's leading comment block, and a room text whose
  generator has no line of its own ('…') keeps the story's lines (a rerun of the houses generator had dropped both;
  checked over all 67 rooms with story parts: story parts, entries, includes, comments and story text lines unchanged).
- **Mauville Gym's barriers** (b2tools/gyms_league_rooms.py): Sapphire's three layouts (the map, MauvilleGymSpecial2
  "alt", MauvilleGymSpecial3 "off", simulated tile by tile in Sapphire's order) are three rooms: MauvilleCity_Gym,
  MauvilleCity_Gym_Alt, MauvilleCity_Gym_Off (recipes with `alt_of`, `block`/`unblock` and the beams on that layout's
  solid barrier tiles). data/interiors/239.json `alt_rooms` installs the other two (patches/interiors.py: their own
  matrices + a/0/1/0 kind-1 entries) on map replace events 3 and 4 (works 0x4034/0x4035, data/story_ids.json
  WORK_MAP_REPLACE_3/4: Black 2's own entries of those events patch matrices 9 and 0, which no Hoenn zone uses). New
  builder key `unblock` (models_interior.py): tiles walkable although Sapphire's collision blocks them. The interiors
  patch leaves out alternate rooms not built in its interiors folder. Black 2 draws a swapped matrix only on a map
  change (its scripts follow MapReplaceSetEvent with MapChangeCore; MapChangeCore takes constants only), so the switch
  and Wattson scripts end with a fade and a map change to the player's own tile (0478 Sub_MG_Redraw).
- **White dividers** (Dewford Hall, Rustboro Flat 2 1F-3F, Wanda's house: Sapphire tiles 2d7 2df 2e7 2f8 300 308 310):
  they were non-floor tiles inside the room, so the builder put walls round them with Black 2's black wall cap, a black
  slab from the camera. converter/gen_interior_recipes_houses.py now makes them floor + a wall-high block (sides in the
  room's wall texture, top b03_wall_a: the facilities partition top; data/interior_tiles_houses.json "divider").
  Fortree's tree trunks keep the wall treatment.
- **Scripted map changes from step triggers** (ladders, holes, vents, cracked floors; ch5's finding, story_fixups fix):
  `MapChangeCore` straight from a step trigger leaves every NPC and trainer of the arrival zone dead (no talk, no trainer
  sight; the same symptom as the test warp). Black 2's own scripts do ActorsPauseAll, FadeOutBlack, RTReserveScript <n>,
  FadeWait, MapChangeCore, FinishAllEvents, ActorsUnpauseAll, VMHalt and the reserved script n in the arrival zone fades
  back in (FadeInBlack, FadeWait). RTReserveScript takes any script id, so hm_free.py has one global arrival script,
  10017 (file 1243, Script_18), that every generator reserves: b2tools/gyms_league_rooms.py write_scripts (Lavaridge
  holes and vents, Sootopolis ladders) and converter/gen_caves.py (cave ladders, cracked-floor and hole falls: Granite
  Cave, Victory Road, Meteor Falls, Shoal Cave, Cave of Origin, Sky Pillar). No per-room arrival script, no change in
  the story parts. Tested: Lavaridge B1F vent -> 1F, the fade in, then Flannery talks (screenshots/story_fixups/07_*).
  Not run: ladders and cracked floors in the caves (same generated pattern, assembled). gen_caves.py with no names does
  not regenerate the Sky Pillar floors (name them: `gen_caves.py SkyPillar_1F ... SkyPillar_5F`). gen_caves.py also no
  longer overwrites a story agent's init file when its marker is "---- story" inside a comment line (it had dropped
  ch9's Shoal Cave zone init and ch10's Seafloor Cavern one on a rerun; restored).

## Room sweep 2 (sweep_rooms agent, 2026-10-07): black slabs, gravestones, more checks
Every room recipe (225 + the Hall of Fame's) rebuilt with the current builder and checked; proofs screenshots/sweep_rooms/.
- **Checks**: `b2tools/rooms_check.py` now runs kinds a-l by default (`--world WORLD` for j); the new ones live in
  `b2tools/rooms_check_more.py` (also runnable alone): **h** a thin wall (<= 2 tiles) or island between two floors that
  Sapphire draws as a wall (its metatile brighter than 100) but the room leaves black, culled (upside-down) faces;
  **i** images/chunk size (110,600 B buffer), with `--rom` every room texture in the zone area's map texture set with its
  source bytes (nsbtx.merge keeps a same-named texture), every furniture model in the area's pack under its res id and
  its textures/palettes in the pack's set ("probably not installed" when the room isn't in that ROM); **j** check_exits.py;
  **k** data/story NPCs on solid tiles / in furniture / two unflagged people on one tile, triggers nobody can step on;
  **l** reachable walkable tiles with nothing drawn at their height. (b) leaves out Black 2's warp pads warp01-03; (e)
  accepts a warp a generator moved onto the stairs next to Sapphire's arrow ("what": "Sapphire warp n (x,y)") and the
  mat-less exits of Sky Pillar 1F (Dragonspiral's lit doorway) and the ship's deck. rebuild_slice.sh runs it as a report
  after the ROM (`<world>.rooms_check.txt`, counts on screen). interior_sweep_check.check_zones skips rooms not built.
- **inner_walls** (models_interior.py, opt-in recipe key; every other room builds byte-identically, checked on all):
  `inner_wall_tiles()` finds Sapphire's thin walls between two floors and light islands (Sapphire's metatile brightness,
  `metatile_lum`); they become floor + blocks with a light top standing where Black 2 stands a wall (12 units off the
  floor south, 3 beside: doors/furniture keep their places; furniture/decals stop at them). Black 2's camera looks down
  ~45 degrees, so a 50-unit block hides a player right behind it (seen in the hidden floor's corridor): tiles with a
  walkable tile < 3 tiles north of them are 16 high (`h_low`), the rest 50 (dividers off the back wall, the front of the
  ship's cabin blocks with their doors). Used by: Weather Institute 1F/2F (top in04_wlab01, set 285), Lilycove Museum
  1F, Oceanic Museum 2F, Bike Shop (b03_wall_a, 330) — hand recipes; Aqua/Magma Hideout (in77room_01, 379) and the
  ship's corridors incl. the hidden floor's (fs_room8, 337) — ship_hideouts_rooms.py / dive_rooms.py. Black void that
  Sapphire draws black (the gaps between the ship's cabins, New Mauville) stays black. Fortree's tree trunks (a jog of
  the back wall) are left as story_fixups decided.
- **Mt. Pyre**: grey upright gravestones (user choice): block styles `fac_grave` (smooth grey in82_ishi, set 389, 10 x 5
  units, 18 high) on `fac_grave_base` (d17_wall_a, 14 x 8 x 3) in _styles_facilities.json; facilities_pyre.py. (20,8)
  on 1F walks fine (tested).
- Hideouts: the 2x1 computer desks turned (pcdesk02 runs along its z: it lay across three rows; an Aqua grunt stood in
  one), the 2-tile TV = DERIVED_MODELS `tv01_2w` (res 311). Ship's hidden floor: the 2x2 writing desk (0x299/0x29a/0x2a0/
  0x2a2) was left out of the floor (a black hole): floor + table02_2w. Sootopolis Gym 1F: no ice block under the
  statues (their sides flickered on it, 1.75 units).
- Generators got a recipes-only mode (zone files, scripts and texts untouched): `ship_hideouts_rooms.py --recipes`,
  `facilities_pyre.py --recipes`, `gyms_league_rooms.py --recipes` (each checked in step with the committed recipes first).
- Emulator looks with one build: `b2tools/room_look.py ROM STATE OUT.png ZONE,X,Z [moves]` (notes/TESTING.md).
- Left (reported): Steven's house balls (ch9 objects) stand inside the green table (Sapphire puts them on it);
  ship corridor B1F's stair_u01 reaches 7 units into the walkable tile beside it; the Day-Care back door and Devon 1F's
  elevator doorway 1 unit into a tile (known); the Hall of Fame room (halloffame agent) has four one-tile black notches
  in its side walls (Sapphire (1,6), (1,11), (13,6), (13,11)).

## Indoor check (indoor_check agent, 2026-10-08): people drawn into furniture
**Cause of the heads in the Center counters [code][test]:** Black 2 draws a person as a camera-facing quad (billboard.c
BLACT_TYPE_FACE_CAMERA, 28x28 units per 32-px frame, anchored at the feet), so the sprite leans back from the feet by
the camera's pitch and anything nearer the camera than that plane is drawn over it, even geometry behind the person.
The Pokémon Center 1F zones use field camera 3 (zone header weather_word >> 9: 31.75 degrees down, measured in RAM at
NNS_G3dGlb 0x02143a0c) and give people no depth margin (camera 0 rooms: ~4.3% of the view distance, ~10 units, measured):
the counters' cream top (y 18, reaching the row's south edge 8 units from the feet) crossed the head of everyone at the
counter. Fix: counter top 4 lower (y 14) and 1.5 units back, in Black 2's own Center counter colour (in02_pc's orange-red
column, set 283, as chunk 827 draws its counter; mats "uv" = one quad of part of a texture; the cream vanished into the floor) (rug rects may now end inside a tile), shelf03 sunk 4, the
balls/terminal on it (Center masters, centers_rooms.write_recipes copies). Same rule in camera 0 rooms for blocks over
18 units reaching the tile edge north of a walkable tile.
**Checker:** b2tools/rooms_view.py = rooms_check kinds m-q (default): m people (NPCs, and the player on every tile) with
geometry behind them drawn over the sprite / standing inside furniture / cut off by a side wall / head hidden by a wall in
front; n feet off the drawn floor; o doors off their warp tiles; p holes (void enclosed by the room); q floor open to the
void. Its renderer matches DeSmuME (screenshots/indoor_check/00_*); `--render OUT ROOM X,Z` draws a room with its people
from the game camera; `--b2 [ZONE]` runs it on Black 2's own rooms (the baseline: its terrain cuts 0.3% of tiles).
**Builder rules (models_interior.py):** FRONT_H 18 (taller blocks stand back 12 units from a walkable tile south of them,
as Black 2's walls), CORNER_H 16 (a side wall's first tile when a walkable tile is diagonally north of it), inner walls low
also for diagonal neighbours, pits (h < 0) get their north inner wall. Generators: gym wall styles 18-20 high
(gyms_league_rooms.py), New Mauville walls 18 (caves_misc_newmauville.py), registers on the counter-end tiles
(shops_recipes.py). Results 544 -> 50 findings (all rooms, both versions); left: the Abandoned Ship's void gaps between
cabins (36 player tiles), the shipyard's thin girders, Steven's balls inside the table (Sapphire puts them on it), the
museum grunt under the whirlpool machine, 3 slivers of 6-8 px. Tools: work/agents/indoor_check/tools.
**Follow-up (map_gfx 2026-10-11): heads cut by blocks behind, seen with the player north of the person.** Rustboro Gym's
Josh (7,12) and Tommy (3,7) stand south of 18-high rock blocks (gl_rock = FRONT_H, so at the tile edge). With the camera
centred on them the hat clears the block; with the player 3-5 rows north of them (the camera follows the player, so they
sit low on the screen) the block's top edge crossed the hat in DeSmuME (screenshots/map_gfx/03_*). rooms_view kind m
looked at NPCs only from the camera centred on them and the box's x ends, and its camera-0 depth factor 0.957 drew the
hat there; now NPCs are also seen with the player on the reachable tiles 6 rows north .. 3 south of them, and DEPTH_K[0]
is 0.959 (this case needs >= 0.958; the Oldale 2F rows bound it at <= 0.9592). Gyms: gl_rock, gl_fortree_post,
gl_ice_cliff, gl_ice_wall 18 -> 16 (Rustboro, Fortree, Sootopolis 1F/B1F: Josh, Tommy, Kylee, Terrell's head, Andrea,
Connie, player tiles). Left: Dewford's Laura (14 px) and Fortree's Terrell (9 px) body-side slivers from a camera 4
tiles to the side. FRONT_H 18 is at the limit for camera 0 rooms: over all rooms the extended check gives 88 m lines
(v16.3: 50), the new ones in non-Gym rooms mostly 6-9 px player slivers from the 0.959 factor (New Mauville GreenDown 10,
Fossil Maniac's tunnel +3, Space Center 2F +3, Abandoned Ship deck +3, ...; work/agents/map_gfx/all_rooms_m_after.txt):
not fixed (Gyms only).

## Walkability indoors (walkability agent, 2026-10-11): strips of floor in front of the walls, one-way walls
Checker: b2tools/walk_diff.py (notes/WORLD.md "Walkability"); rooms_check and rooms_view as above. Proofs:
screenshots/walkability/.
- **The back wall [code][test]**: Sapphire draws its walls two tiles high (row 0 and the solid lower row 1) and the
  recipes give row 1 floor (furniture against the wall stands on it, its front 12 units from the walkable row: the head
  rule FRONT_H). Where nothing stood on row 1 it was bare floor you could not step on, the wall 28 units in front of
  the player (Black 2: 12): 993 such tiles. models_interior.bare_wall_tiles: such a tile (solid in Sapphire, at the
  floor's back edge, walkable floor south of it, nothing standing anywhere in its column in front of the wall, no
  person, warp, water or block) is no floor now, so the wall stands 12 units north of the walkable row as Black 2's.
  Only whole back rows, runs from a room corner and runs of 3+ tiles are trimmed (a shorter bare stretch brought
  forward between two pieces stood out of the wall as a box; the side columns are left alone: trimmed, they notched
  the corners). A wall picture or window goes with the wall (MOUNTED pieces with "wall": "N"); a piece placed at a
  fixed spot keeps its column. Recipe "wall_rows": "keep" turns this off (the Battle Tower rooms: pwt_tower's).
- **Pieces against the back wall** (wall_row_front): brought forward to the head-rule line (12 units north of the first
  walkable row in front of them) when no person stands in front of or beside them and no other piece is in the way;
  pieces against the wall move together (a TV on its cabinet).
- **One-way walls and elevations [code]** (side_wall_classes): Sapphire's MB_IMPASSABLE_* walls (the Contest Halls'
  seat rows), its elevation rule between walkable tiles (Mossdeep Gym's and the hideouts' raised floors) and its surf
  rule (on/off the water only at elevation 3: the Aqua Hideout's raised banks) are Black 2's side walls (0x51-0x58) on
  one of the two tiles: walk_diff THROUGH 93 -> 0, no new INVISIBLE.
- Indoor check leftovers: the Abandoned Ship's broken-wall blobs (0x2AA-0x2AD) are light-topped inner-wall blocks
  (ship_hideouts_rooms.py; they were black notches with a full wall that hid the player's head: 23 rooms_view m lines
  gone); the shipyard's girders end 12 units north of the tile in front of them, the two free-standing ones 18 high;
  Steven's two Poke Balls stand on his table (recipe "solid_y": the table tiles' collision at the table top, 11, as
  Black 2's own starter balls stand on a table, zone 391: solid tiles at 8; rooms_view and rooms_check_more now see a
  person standing on a solid tile's height); the museum's experiment machines are Black 2's machine01 at FRONT_H
  (DERIVED machine01_s, res 318: the grunt's head 189 px -> 10 px). rooms_check (all rooms, no ROM) m 88 -> 57,
  k 9 -> 7, b 4 -> 4, h 13 -> 14 (Fortree's partitions smaller; one 2-tile line at the ship corridor's stairs).
- Left: back-row tiles in front of pieces that cannot come forward or keep their column (a person in front, a piece
  placed at a fixed spot) and bare stretches of 1-2 tiles between pieces (walk_diff OPEN, interiors 656, most of them
  back-row); the small slivers (6-16 px) rooms_view m lists, as Black 2's own rooms have them.

## Final interior sweep for v16.4 (sweep_rooms, 2026-10-11)
Every room (both versions) rebuilt from 9b691e0, rendered from the game camera (529 views; a renderer note: rooms_view's
`draw` drops a triangle with a vertex behind the near plane, so big floor quads of large rooms vanished in its renders,
not in the game: work/agents/sweep_rooms/v164/tools/subdiv.py splits them for looking) and spot-checked in DeSmuME
(houses, Centers, Mart, Gyms, labs, Museums, Devon, Aqua and Ruby's Magma Hideout, Abandoned Ship, Battle Tower, PWT
lobby, Elite Four). Proofs: screenshots/sweep_rooms_v164/.
- **Fossil Maniac's tunnel [code][test]**: Sapphire's one-tile rock ridges between two floors ((7,21), (7,11)-(7,12))
  were 48-unit cave walls; (7,21) hid the player at (7,20) entirely. Recipe "inner_walls" (tiles listed): low rock
  blocks with the dirt top.
- **Raised levels [code][test]** (Room.raster): a raised level's edge tile nobody stands on (Sapphire solid, or a door's
  warp tile in it) more than FRONT_H above the level in front stands back BACK units too, the strip in front given to
  the lower level's block; a whole edge run moves when someone walks below any of it (the ship's hull over the sea
  keeps its edge). Only the Abandoned Ship's deck uses "raised": the deckhouse front and the bridge cut the player's body
  and head along the decks (m up to 177 px); ship_hideouts_rooms.deck() puts its doors, portholes and lamps on the new
  face (dz / face_z - 12 units). Every other room builds byte-identically (checked).
- **Battle Tower lobby**: the terminal on the counter (Sapphire's sign (3,5)) 14 back along the counter's arm (its top cut
  the head of the player reading it). **Trick House puzzle 1**: the short fence posts and the back-wall shelf row were
  planks lying flat on solid tiles (walk_diff OPEN 26): low plank boxes (8 high, in01_kibako01).
- rooms_check_more (h): a stairs tile is drawn by its stair model, not black (the ship corridor 1F's (6,2) read as a
  partition once the blob (8,2) beyond Sapphire's black column became a light block).
- Counts (no ROM, all kinds, Sapphire = Ruby): b 4 -> 4, h 14 -> 12, k 7 -> 7, m 57 -> 41; walk_diff interiors OPEN
  656 -> 630, INVISIBLE 0, THROUGH 0 (both versions).
- **Left for the user**: the back-wall "bays" (49 rooms, mostly houses: where a 3+ tile bare stretch between two pieces
  was trimmed the wall juts out a tile at the window, the pieces stand in recesses): screenshots/sweep_rooms_v164/06_bay_A
  (as built) / B (flat wall, blocked strip in front of the window, as v16.3) / C (flat wall, the strip walkable: one row
  more than Sapphire). Left as known: h = Fortree's trunks (6), the Hall of Fame's notches (4), the ship corridor B1F's
  one-tile notches beside its cabins (2); m = people under tall furniture behind them seen from a camera far north
  (Space Center 2F, shipyard 2F, Dept. Store 5F: Black 2's own billboard look) and 6-30 px slivers; OPEN = mostly the
  head-rule strip in front of tall pieces against the back wall (Black 2's 12 units), 1-2 tile bare stretches and wall
  pictures between pieces, Sapphire's own blocked corners (the Centers' front corners), hideout pool banks; the Aqua /
  Magma Hideout 1F pool entrance walls are black where Sapphire draws brown rock.

## Back-wall bays: option C (v165_fixes, 2026-10-11; user decision 2026-10-11)
- **[code][test]** models_interior.bare_wall_tiles: a bare stretch of the back wall's lower row trimmed BETWEEN two
  parts of the row that keep their wall line (the "bays": the wall stepped forward a tile at the window, the pieces in
  recesses) is no longer trimmed: the floor stays, the wall stays flat, and those tiles (room.json "walk_up") are
  walkable in Room.collision: the player walks right up to the window, one row more than Sapphire (the user's choice).
  Whole back rows and runs from a room corner stay trimmed. 47 rooms, 212 tiles (every other room builds
  byte-identically); a Sapphire sign on such a tile is also readable from the strip (Dewford Hall's painting: a second
  sign entry on the wall row, data/story/ch2.json).
- walk_diff: the strip is THROUGH "back-wall strip" (intended, WALK list), interiors OPEN 630 -> 680: the +50 are the
  pieces beside the strip seen from the side (a shelf whose front stands 12 north of the row in front of it fills only
  the back 4 units of its tile: Black 2's own spacing; in the game the player stops beside it, shots below); rooms_check
  on the 47 rooms 9 -> 9 lines (2 slivers moved 3-7 px with the camera box). Behind counters (contest lobbies, the
  department store, the Safari entrance) the strip exists but cannot be reached. A Route 119 house Wingull can now fly
  into its strip (loop_check).
- Proofs: screenshots/v165_fixes/01-06 (Petalburg House 1, Steven's house: before top, after bottom).

## Copied models' animation textures (museum_freeze, 2026-10-12) [code][bytes][test]
- **Bug (v16.6/v16.7, public):** entering the Slateport Museum froze on melonDS / Delta (iPhone) / hardware, never in
  DeSmuME. A building model copied from another Black 2 pack (patches/interiors.py) brought its info record, which embeds
  a BTP0 texture-pattern animation, but only the textures its materials name (frame 0): machine02 swaps machin0.1 ->
  machin0.2 / machin0.3 by name. The missing name makes NNS_G3dGetResDataByIdx (arm9 0x02068458) return NULL and
  func_02069dc0 reads through it (`ldr r2, [r0]` at 0x02069dd6): a data abort under the DS memory protection (melonDS
  savestate: ABT mode, PC in the BIOS abort loop, SPSR thumb SYS); DeSmuME has no protection and reads ITCM's mirror at 0.
- **Fix:** interiors.py `anim_pairs(info)` adds every frame's texture/palette of the copied model's BTP0 animations
  from the source pack. 14 animations in 8 interior packs were incomplete (machine01/02, the Center ball machine mball01,
  pcmachine01, the electric floor d6_yuka_biri02); a/1/7/5 members 5, 22, 23, 24, 31, 53, 63, 76 grow 312-2,112 B; file
  layout unchanged. Check any ROM: `python3 b2tools/anim_tex_check.py ROM` (Black 2 itself: complete).
