# Hoenn's height levels in Gen 5 (heights agent, 2026-10-06)

Module: `b2tools/terrain/heights.py` (classes cliff, cliff_top, stairs, ledge_e, ledge_w, ledge_cap, mountain,
cave_entrance, cracked_floor, mud). Hooks: `b2tools/world.py` (lines marked `# heights:`), helpers
`ledge_run_ew` / `ground_heights` in `b2tools/build_chunk.py`, the `elevation` field in `converter/plan_map.py`.
Tags: **[code]** read in the decomp or disassembly (`b2tools/armdis.py`), **[bytes]** checked in the user's dump,
**[test]** checked in DeSmuME (`work/agents/heights/htest.py`) or offline over the built world.

## 1. How Black 2 stores and uses heights

**Every collision tile is a plane.** `FieldChunkAccessor_GetTerrainCore` (ov036 `0x021c7028`) **[code]**: from the
tile's record `u16 a, u16 b, u32 t` it takes, when `a & 3 == 0`, the normal `(n0, n1, -n2)` from
`MAP_HEIGHT_SLOPE_TABLE[3 * (a >> 2)]` (ov036 `0x021d2a04`, 317 fx16 triples) and `d = MAP_HEIGHT_OFFSET_TABLE[b]`
(`0x021d3174`, 1285 fx32), and returns `y = -(nx*x + nz*z + d) / ny` (FX_Div at `0x2073df0`) with x, z relative
to the chunk centre; class = `t & 0xFFFF`, flags = `t >> 16`. `a & 3 == 2` is the two-triangle kind (corner list,
notes/GEN5_MAPS.md); other kinds are flat y = 0. So:
- flat tile at height h = slope 0 (`(0, 4094, 0)`) + the offset index whose `-d/4094` is h. Flat heights that
  exist (within 0.75 units): every multiple of 16 from -192 to 336 **[bytes]** (`plane_record`/`flat_index` pick
  the index; the old `(0, 3)` records are y = 0).
- stairs = 45-degree planes: Accumula (chunk 5, x 22-23, rows 4-9: 72, 56, 48, 40, 24, 8) and Route 20 (chunk
  287) use slope 8 for steps rising north and 11 for steps rising east; Route 19 (chunk 282) uses 11 **[bytes]**.
  Slope 8 = `(0, 2895, -2895)` rises 16 units per tile to the north, 14 / 11 / 16 are south / east / west.

**An actor steps onto a tile only if its height differs by less than 20 units.** `ActorRouteCollCheckCore`
(`bw2/src/ov012/field_actor_tool.c:490-525`) **[code]**: `diff >= FX32_CONST(20)` sets the blocked bit; the height
comes from `GetHeightFromMap` (`:695`) = the terrain layer nearest the actor's y (`FieldG3DMapper_GetTerrain`,
`bw2/src/ov036/field_g3d_mapper.c:677`). `CheckRecalcActorY` (`field_actor_tool.c:771`) snaps an actor's y to the
map, so **NPCs and item balls (entity y = 0) stand on raised ground by themselves** [test: Route 104 / Route 116
shots, the NPC and item balls on the 16- and 32-unit plateaus]. Consequences: a level is 16 units (one Gen 3 cliff
row, one 45-degree stair tile), and two walkable tiles 16 apart can be walked between unless something blocks it.

**Events match on y too.** Warps, signs and step triggers fire only within 2 units of their y
(`CheckWarpPositionMatch`, `CheckBGPositionMatchGrid`, `CheckTriggerPositionMatchXYZ`,
`bw2/src/ov012/eventdata_system.c:691, 771, 849`) **[code]**, so world.py gives warps, signs, sign models, building
and prop placements and step triggers their tile's height (`hgt`); Route 101's rescue trigger fires at +16
**[test]** (`screenshots/heights/route101_trigger_at_16.png`). NPCs keep y = 0 and snap (above).

**Side walls on walkable tiles.** `CheckBlockedCollPathToPosition` (`field_actor_tool.c:630-673`) **[code]**
blocks a move when the current tile's class blocks leaving that way (`TILE_EXIT_BLOCK_CHECKS`, `:30-35`) or the
target's blocks entering from that side (`TILE_ENTER_BLOCK_CHECKS`, `:23-28`). The checks (ov036
`0x021a2d58..0x021a2db6`, disassembled) **[code]**: north wall 0x53/0x55/0x56, south 0x54/0x57/0x58, west
0x52/0x56/0x58, east 0x51/0x55/0x57. Black 2 uses 0x51-0x54 on walkable tiles with flags 0x80 (e.g. Accumula's
bottom stair tile (22, 9) is 0x52) **[bytes]**.

**Ledges**: classes 0x72/0x73/0x74/0x75 jump east/west/north/south (`MapTile_IsLedgeR/L/U/D`, ov036
`0x021a2a54..`), flags 0x0001, both sides the same height in Black 2's maps (Route 20 chunk 286, Route 19 chunk
282) **[bytes]**. A jump may also drop 32 units: Lilycove's ledges land 32 below the plateau and work **[test]**
(`screenshots/heights/lilycove_ledges_drop32.png`).

## 2. Black 2's own geometry, copied (all textures are in Hoenn's set 3: 0 bytes added **[test]**)

| Thing | Black 2 source | Recipe |
|---|---|---|
| Cliff, 16 high | Route 1 chunk 2 (row 21), Route 20 chunk 287 | Stands in the solid tile at the LOW height next to the high ground. Lip `gake1_1` (grass top) / `gake1_0` (rock top) rolls 4 units down over the first half tile; face `gake01a` (v 0..1 over the face, transparent foot row) drops over the second half. One strip per straight run (Route 1: one 14-tile quad). |
| Outer corner | Route 20 chunk 287 (19, 17) | In the diagonal tile: one lip triangle (corner, half-tile points 4 below) and a fan of face triangles to the foot. |
| Tall cliff | Route 19 chunk 282 row 3 (96 -> 16) | Lip, then `yamagake01` (16x32) stretched once over a 60-unit wall, `gake01a` foot. |
| Stairs | Accumula chunk 5, Route 20 chunk 287 | `kaidan01a` on the 45-degree collision plane, one tile per 16 units; red stringer (the left 3 texels of `kaidan01a`) on open sides. |
| Side ledge | Route 20 chunk 286 (x 24, rows 26-30) | The south ledge turned a quarter turn: lip x+0.38 -> x+0.88 (4 high) -> x+1.0, tapered caps (`build_chunk.ledge_run_ew`). |
| Cave mouth | Route 6 chunk 55 (warp (11,19)) and 12 other route chunks (section 7) | `doukutu01` in a 2-tier rock: dark back wall, side walls and shaded floor, rope jambs + lintel, pebbles; terrain/cave_mouth.py (section 7). |
| Rocky ground | Driftveil chunk 48 | `gake_michi` (64x64) on walkable rock. Rock ridges: `gake_futa` tops (Route 23 chunk 309). |

Cliffs and stairs in Black 2's collision: cliff tiles are solid at the low height (Route 20 chunk 287 rows 17-19,
Route 19 chunk 282 row 3) or solid 45-degree planes (Route 1 chunk 2 row 21) **[bytes]**.

**How heights.py draws it** (`draw`): every unwalkable tile lower than a (non-stair) 8-neighbour is a face tile
with a 3x3 lattice of heights (corners, edge middles, centre, 8 units apart): points touching higher tiles take
their height, points one step further in take it minus 4 (the lip), the rest the tile's own (low) height. Its 4
sub-quads give exactly the profile and corners above (lip triangle + face fan at outer corners). Neighbouring tiles
compute the same values for shared points; where two tiles still disagree on a shared edge (flat tiles of different
heights, stairs sides, faces of different heights), a vertical skirt closes the gap (`kaidan01a` stringer when the
upper side is a stair, else `gake01a` / `yamagake01`). So there are no holes, and planar sub-quads merge into one
strip per straight run. Ground is world.py's (`build_chunk.ground_heights`: every tile at its height, one texture
per level region, rectangles up to a whole chunk; none under stairs). Other modules draw at y 0 and are lifted
triangle by triangle (`Field.lift`).

## 3. Hoenn's heights from Sapphire's data

Sapphire stores an elevation per tile (pokeruby blockdata bits 12-15; `converter/plan_map.py` now writes it as the
plan's `elevation` grid; all 64 overworld plans regenerated - only that field was added). Movement rule
(`external/pokeruby/src/event_object_movement.c:7528-7598`) **[code]**: a move is blocked when the walker's
elevation is not 0, the target's is not 0/15 and they differ; elevation 0/15 tiles connect any level.

`height_field` (heights.py), in order:
1. **Regions**: walkable tiles of one elevation, 4-connected, are flat (3 = level 0, 4 = +16, 5 = +32 ...).
   Elevation-0/15 tiles join the region they touch; where they touch several levels they are a **junction** and
   those regions must stand level - Gen 3 often uses elevation only to order sprites (Route 120's path, Lilycove's
   lawn, Route 115: two elevations, no cliff, a row of elevation-0 grass between them).
2. **Constraints** (weighted union-find, strongest first, a contradicting one is dropped and listed in `F.notes`):
   stairs between two elevations keep their difference; junctions keep level; ledges keep level; stairs inside one
   elevation climb one level a row to the north (Gen 3 draws such stairs in a cliff band). Regions on the sea
   (water bodies of 400+ tiles; a waterfall splits a river) are anchored at their Sapphire level, any group left
   floating at its biggest region's. Result: the mainland (Littleroot, Routes 101-103, Petalburg) stands at +16
   above Route 104's beach and the sea, Route 112's plateau by the Fiery Path at +80, Fortree's tree-house platforms at +16
   and +32. 4 stairs end up flat (both ends pinned: Slateport 265,378 and 280,378, Route 119 346,113, Route 121
   478,153), one climbs south (Route 119 363,149) and Lilycove's ledge groups drop 32 (world.py's report lists
   every dropped constraint as `heights: ...`).
3. Stair tiles become 45-degree slopes from the low region to the high one (8 or 32 a row where the drop does not
   fit; 2 such, Route 110).
4. Ledges take the height of the side they are jumped from (else the landing side / walkable neighbours: Route
   112's ledge lines run between trees). Side ledges count as walkable here (Sapphire puts the collision bit on them).
5. Water takes its nearest shore's height (ties: lower); unwalkable cliff tops and mountains that a 2x2 block covers
   rise one level above the ground at their rim (mountains: one more level three tiles in, at most two); single
   rocks and one-tile spurs stay down (fewer faces, smaller chunks). Route 126's 41 passable crater tiles are solid
   rock (unreachable in Sapphire too).
6. Cliff tiles take the lowest height next to them (they hold the face); everything else the nearest height; trees
   stand at their lowest unwalkable tile, buildings at their door's front tile.
7. Walkable neighbours that Sapphire keeps apart (elevation mismatch) but that end up < 20 units apart get side
   walls (0x51-0x58) on plain-floor tiles: 260 tiles (Lilycove 62, Pacifidlog 61, Mossdeep 38, Routes 119/124/127
   16-18 each, Route 114's ridge path 14, Route 109's beach chairs 12, Fortree 12, ...).
8. Ground texture per level region: `gake_michi` where most of the region is brown rock in Sapphire, else grass.
9. (bridge_surf 2026-10-20) **Surf start**: walkable tiles beside surf water where Sapphire's player never stands at
   elevation 3 carry NOSURF (step 12b; hm_free refuses a surf from them, Gen 3's rule: notes/TERRAIN_WATER.md "Surf
   start and surf traps"). **Islands** in a warp-only group with no sea (no 400-tile water anchors its levels): a
   floating group with water beside it and no warp stands level with that water's biggest placed shore instead of its
   Sapphire level (Emerald's Safari Zone southeast; in the connected world the shore rule already does this).

**Offline check [test]** (`work/agents/heights/movecheck.py`, scratch, not in git): every move Sapphire allows on land (both sides walkable, not water,
from all reachable (tile, elevation) states) against Black 2's rule on the built collision (step < 20 units, side
walls, ledges only their way): **0 moves blocked that Sapphire allows and 0 allowed that Sapphire blocks**, except
door/sign/building/cave-entrance tiles (warps are solid tiles in Black 2 by design). Water and bridges are the water
and bridge modules' (water is solid without them).

## 4. In-game proof [test]

DeSmuME, `HOENN_TEST_NO_WILD=1`, from `work/emu/after_mom2.dst` through the test door (arrival moved with the
scratch patch `work/agents/heights/test_arrive.py` where Sapphire's story or water would block the way). y = the
player's position vector in RAM (the lowest-address copy reads ground + 4 right after a warp, the exact ground after
the first zone change).
- `screenshots/heights/route116_two_stairs.png`: Route 116 ground (y 4) -> stairs (12) -> plateau (20) -> stairs
  (28) -> plateau (36): two levels up, next to the Rusturf Tunnel mouth.
- `screenshots/heights/route102_104_ledge_e_stairs.png`: Route 102 east ledge jump (151,306 -> 153,306), then on foot
  through Petalburg to Route 104's beach (y 0), up the stairs (7.97) onto the cliff top (16) - reachable without water.
- `screenshots/heights/route104_ledge_w.png`: Route 104 west ledge jump (77,290 -> 75,290) below Petalburg Woods.
- `screenshots/heights/route112_tall_stairs.png`: Route 112, 3 stair rows up a 48-unit cliff (y 36 -> 84).
- `screenshots/heights/route112_cave_mouth.png`: Fiery Path entrance (no rock behind it on this map: a rock mound
  carries the mouth).
- `screenshots/heights/lilycove_ledges_drop32.png`: west and south ledge jumps down 32 units.
- `screenshots/heights/littleroot_at_16.png`: the slice at +16, house and player in place.
- `screenshots/heights/route101_trigger_at_16.png`: Route 101's step trigger (y = 16) starts the rescue.

## 5. Cost

All 9 textures are already in set 3 (`hoenn_textures`: 53184 -> 53184 B). World with heights only: 118,267
triangles (115,882 without: ground rectangles grew to whole-chunk merges), chunk files 7.02 MB in total, largest
66,472 B (cell 2,4, Route 114/115; limit 110,600). The slice-only world's models are 3.15 MB, the water agent's
5.46 MB, this one's 4.35 MB (+ 2.67 MB of collision in every case), so all modules together will pass
build_rom.py's 8 MB `RESERVE[8]` for a/0/0/8: raise it (about 12 MB) and rebuild the base savestates.

## 6. Open

- Bridges, puddles, water surfaces, waterfalls, rocks, fences and props are other modules'; they are lifted to
  their tile's height. Fortree's houses sit on +16/+32 platforms (Sapphire's tree-top elevations).
- `hoenn_world.py` writes fly points with y = 0 (zone header); flying into a raised town relies on the same snap as
  NPCs (not tested).
- Sapphire's mud slopes (Routes 111/115/119) are plain walkable 45-degree slopes (no sliding).
- Rivers whose banks Gen 3 drew at two levels get a rock step halfway (nearest-shore water).
- Cracked floors don't occur on the overworld maps (cave entrances: section 7).
- Back faces (north-facing walls) are drawn single-sided like everything from `dae.py`; not checked in melonDS.

## 7. Cave mouths (cave_mouths agent, 2026-10-07)

Module `b2tools/terrain/cave_mouth.py`, called by heights.py (`draw`: cliffs from `cave_mouth.drawn(FIELD, world)`,
section 1 skips the faces a mouth's opening replaces, section 5 calls `cave_mouth.draw`). Proof:
`screenshots/cave_mouths/mouths.png` (Sapphire | before | after | after: walked in, DeSmuME, every entrance).

**How Black 2 draws a route's cave entrance [bytes].** Every outdoor warp into a cave (zone entities of matrix 0, dest
zone named Cave/Passage/Mountain/Tunnel/Chasm...): Driftveil -> Clay Tunnel (chunk 48), Mistralton -> Chargestone (59),
Route 6 -> Chargestone (55), Route 7 -> Twist Mountain (63), Icirrus -> Twist Mountain (64), Giant Chasm (84), Undella
Bay -> Seaside Cave (263), Route 21 -> Seaside Cave (265), Route 3 -> Wellspring (14), Route 6 -> Mistralton Cave (53),
Undella -> Reversal Mountain (93), Route 20 -> Cave of Being (288), Reversal Mountain outside (298, `out57_doukutu`),
Routes 22/23 -> Giant Chasm (303/304). None places a building model near the warp (and no exterior pack has a
cave-mouth model): **the mouth is terrain in the chunk**, 16-22 triangles of `doukutu01` (32x32, repeat t only) set
into a cliff of two tiers (16 + 16 units, one tile row each), the faces of both tiers cut over 3 tiles:
- dark back wall from the floor (+2) at the warp tile's north edge up to +28 one tile further north (one dark texel),
  dark side walls, a floor shaded dark to light towards the front (u 0.38 -> 0.59) on the warp tile;
- rope frame (u 0.62-1.0): two jambs (lower half: the pebble column u 0-0.31) and a lintel under the upper tier's lip,
  which runs on over the opening; loose pebbles (u 0-0.31, v 0.53-0.97) on the tile in front;
- a 1-tile warp gets a 2-tile opening (u -16..16 around the warp tile's centre, jambs to +-32); south-facing warps are
  dir 2, type 4; Cave of Being (288) and Seaside Cave (263) stand in free-standing 2-tier mounds.
Chunk 55's triangles are the template (cave_mouth.TEMPLATE, vertex for vertex) at Black 2's own size: a 2-tile
opening, the faces cut over 3 tiles, round Sapphire's 1-tile door (`OPENING = 2`, user choice 2026-10-07; the door and
all collision stay Sapphire's: the tiles beside the door stay solid, nothing opens or closes a path). The frame stands
2.5 units further out than Black 2's so no surface is within 2 units of the face. `OPENING = 1` narrows it to
Sapphire's 1-tile opening (screenshots/cave_mouths/width_1_vs_2.png).

**The rock around a mouth (drawing only).** Most of Sapphire's cliff bands stay flat here (section 3: only 2x2 highland
rises), so a mouth had no 2-tier cliff to sit in. Within 3 tiles left/right and 4 rows behind the door, Sapphire's rock
tiles (cliff, cliff_top, mountain, cave_entrance, rock; unwalkable) rise one tier per tile from the rock's edge
(8-neighbour distance), at most two tiers, the tiles over the opening at least two (row y-2) and one (row y-1) tier up,
above the approach tile's height. heights.py draws the faces of that field with its own lattice (gake1_0 lips,
gake01a / yamagake01 faces, corners, skirts), cave_mouth.py the flat tops (`gake_futa`, Black 2's rock tops in chunks
55/288) and the mouth. **Collision, world.json, placements and door heights are unchanged** (checked: a world built
from HEAD and from HEAD + this module differ only in the terrain models of the 27 cells with a mouth's rock).
Where the rock beside the opening is not rock (Sootopolis's Cave of Origin, in the stone gate of models_standalone
`origin`), only the opening is drawn (its walls clamped to the opening's width, no frame).

| Entrance (Sapphire map, door) | Notes |
|---|---|
| Granite (Route 106), Rusturf (Route 116 x2, Verdanturf), Fiery Path (Route 112 x2), Meteor Falls (Routes 114, 115), Victory Road (Ever Grande x2), Desert Ruins (111), Island Cave (105), Ancient Tomb (120), New Mauville (110), Mt. Pyre (Route 122, Mt. Pyre exterior), Sky Pillar (Route 131 post-game layout, Sky Pillar Outside + its warp-less mouth at (15,20)), Shoal Cave (125) | mound + mouth; walked in on all of them [test] |
| Aqua Hideout (Lilycove cove), Scorched Slab (Route 120 pond) | water in front: the same mouth at the shore's height, no pebbles; the bank under the mouth's rock (cave_mouth.rock_shore) is Black 2's rocky waterline on the sea (sea_gake01, water.py ROCK_SEA_BANK, Route 1 chunk 3) and a rock-lipped pond bank (gake1_0 + shore01, ROCK_POND_BANK; Black 2's ponds are all grass-banked) instead of the grass bank; surfed in [test] |
| Cave of Origin (Sootopolis) | stone gate model around it, opening only; walked in [test] |

Tested on the v13 layout (HEAD cc338ed + this module, work/emu states of 09:09): Granite Cave (land), Aqua Hideout
(surf) and Route 131's post-game islet (now heights.py mountain, world_fixes) still enter their caves.

Rock style: the mouth uses the rock textures of the tiles it stands on, so the Fiery Path mouths are red (section 8);
a warp-only group's `retex` (data/hoenn_standalone.json) renames the mouth with its cliffs.

2026-10-07 (2-tile openings, red rock, rock banks): tested on the v13 layout (work/emu states of 09:09) - Fiery Path
south (red rock, walked in) and Aqua Hideout (surfed in); every mouth re-shot (screenshots/cave_mouths/mouths.png).

Cost: no texture added for the mouths (doukutu01, gake_futa, sea_gake01, gake1_0 already in set 3), no placement.
Checks (HEAD with the 1-tile mouths vs this, 2026-10-07): collision, placements and world.json identical; chunk files
+35,456 B over 32 cells, largest 103,068 B (cell (7,3), Route 112's red mountain; limit 110,600 for map type 0).
exterior_check.py layers/holes: no holes; no new layer pair except boulders (iwa01) touching the raised rock's faces
(Desert Ruins (279,145), Ancient Tomb (413,113), Route 106 (99,415)), the same kind as 13 existing spots; every mouth
and top triangle faces the camera; ledge_check.py unchanged. The raised rock hides no reachable walkable tile from the
camera (only Lilycove's walled-in 2x3 patch behind the hideout). Black 2 has no water cave mouth to copy: the approach
tiles of all its route cave warps are ground, path or beach sand (classes 0x00, 0x03, 0x1f, 0x19) [bytes].

## 8. Rock styles: Route 112's red mountain (2026-10-07, user choice)

heights.py `STYLES`: Sapphire's red volcanic rock - the own (secondary, id >= 512) rock metatiles of gTileset_Lavaridge
on Route 112 (Fiery Path's mountain, the cable car, Mt. Chimney's slopes) and round Lavaridge Town - is drawn in Black
2's red rock of Reversal Mountain's outside (zone 461, chunks 298/246, summer set 227) [bytes]: faces out57_gake01a,
rock lips out57_gake1_0, rock tops out57_futa, rock ground out57_yuka01, cave mouth out57_doukutu (Jagged Pass's and
Mt. Chimney's `retex` stand-ins; those two warp-only maps keep their own whole-group retex). Reversal Mountain's
cliffs are stacked 16-unit tiers (12-unit out57_gake01a face, v 0..1 with 2 transparent foot rows, + 4-unit lip); it
has no tall-wall texture, so a tall face (yamagake01 elsewhere) is out57_gake01a on its opaque rows (v 0.125..1 per
yamagake01 repeat; Reversal Mountain's own 16-unit tiers, cut out of every tall face, put cells (6,3)/(7,3) at 135 KB,
over the limit). Grass lips (gake1_1) and stairs (Sapphire's are grey stone there) stay. Route 112's brown cliffs of
the general tileset (its east side, the south-east corner) stay brown, as in Sapphire.
- Per tile (`F.style`, height_field step 10b): the rock tiles with the style's metatiles, then a majority filter over
  each rock tile's 8 rock neighbours (5+ and more than half decide), so Gen 3's mixed tiles leave no single odd tile.
  Styled rocky ground gets its texture through `F.mat` (world.py draws ground by tile: no cutting); the cliff
  geometry is renamed at the end of `draw` (`_restyle`), triangles cut at the style's edge (Field.pieces' clipping; a
  wall on a tile edge belongs to the tile behind it).
- Cost: 5 textures from set 227 merged into set 3, +5,300 B (set 3 + building textures 170,988 B of ~200 KB);
  chunk growth in the table above. Proof: screenshots/cave_mouths/mouths.png (Fiery Path rows).

