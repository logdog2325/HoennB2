# How Black 2 stores its overworld maps (researched 2026-10-05)

Everything here was checked against the decomp (`external/pokebw2`, abbreviated `bw2/`) and the actual bytes
of `bw2/extract/b2_us/files/` (B2 USA, DSi-enhanced). Citations are `file:line`, a symbol name (with its
address from `bw2/config/b2_us/...symbols.txt`), or a byte check. Disassembly came from
`tools/dsd dis` run into a scratch folder (the repo has no `build/asm`). Tags:
**[bytes]** = checked against every relevant file; **[code]** = read from code; **[inferred]** = consistent with the
data but not traced in code. CTRMapV 1.4.1 (`tools/ctrmap-plugins/`) was used as a cross-check where it agrees.
`tools/CTRMap.jar` (the core) has no Gen V map readers, only `GFContainer` (the 2-letter container header below).

## Units

- 1 tile = 16 world units = fx32 `0x10000`. 1 chunk = 32 x 32 tiles = 512 x 512 units.
  `GetChunkCoordOfWorld` divides by 0x1000, then 16, then 32 (`bw2/src/ov012/map_matrix.c:127`); `MAP_CONFIGS`
  (ov036 `0x021ca01c`) gives chunk span 512.0 for 28 of 29 map types; every terrain grid is 32x32 **[bytes]**.
- A chunk's world position is its **centre**: `halfSpan + x*span` (`bw2/src/ov036/field_g3d_mapper.c:375`).
- +x is east and +z is south: terrain row = (z + 256) / 16 inside a chunk.

## 1. Which archive holds what

ARC ID N is the file `a/(N/100)/(N/10%10)/(N%10)`. Checked: `NARC_PATH_LIST` (arm9 `0x02099a20`) is a table of
308 path strings and entry i is exactly that path for every i **[bytes]**. IDs are from `bw2/include/constants/arc.h`.
None of these archives has file names (each NARC name table is the 8-byte root only) **[bytes]**.

| What | File | Entries | How confirmed |
|---|---|---|---|
| Map chunks (terrain model + collision + building placements) | `a/0/0/8` | 1065 | `ARCID_MAP_TERRAIN 8` (arc.h:11); `MAP_CONFIGS` chunkArcId = 8 for all 29 map types; magics: 961 `WB`, 60 `GC`, 36 `NG`, 8 `RD` |
| Map matrices | `a/0/0/9` | 416 | `MapMatrix_Load` reads arc 9 (`map_matrix.c:18`); all 416 sizes match the header **[bytes]** |
| Map replacements (season/version/event chunk swaps) | `a/0/1/0` | 1 file, 74 x 16 B | `MapReplaceEntry` (`bw2/include/field/field_map.h:46`); 1184 = 74*16 |
| Zone headers | `a/0/1/2` | 1 file, 615 x 0x30 | `bw2/docs/data.md:228`; 29520 = 615*48 **[bytes]** |
| Area table (texture set + building pack per area) | `a/0/1/3` | raw file (not a NARC), 409 x 10 B | `AreaData_Create` (arm9 `0x02018ee4`) reads 10 bytes at `id*10` from arc 0xd, id clamped < 0x199; 4090 = 409*10 |
| Map (terrain) textures | `a/0/1/4` | 409 `BTX0` | `SetupLoadZoneMapTypeData` sets textures arc 14, file = area's texset (`bw2/src/ov036/fieldmap.c:1507`) |
| Edge-colour tables | `a/0/1/5` | 8 | arc.h:16 |
| Script message text | `a/0/0/3` | 676 | arc.h:9, `bw2/docs/data.md:33` |
| Place names | `a/0/0/2` entry 109 | 155 lines | zone_header.inc:11 ("system message file 109"); `data/text/system/0109_place_names.txt` |
| Field scripts (+ map script tables) | `a/0/5/6` | 1289 | arc.h:32, `bw2/docs/scripts.md:62` |
| Field lights | `a/0/6/0` | 200 | arc.h:34 (area lights ids go up to 196) |
| Terrain texture SRT / pattern animations | `a/0/6/8` / `a/0/6/9` | 58 `BTA0` / 8 | arc.h:36-37; area srt ids ≤ 57, pat ids ≤ 7 |
| Camera boundaries | `a/1/0/9` | 444 | arc.h:45 (name only; reader not traced) |
| Zone entities (signs, NPCs, warps, triggers) | `a/1/2/6` | 616 (615 + 4-byte stub) | `EventData_Create` opens arc 0x7e (`bw2/src/ov012/eventdata_system.c:16`); all 615 parse exactly **[bytes]** |
| Wild encounters | `a/1/2/7` | 135 (122 x 232 B, 13 x 928 B) | arc 0x7f (eventdata_system.c:17); `EncData_Load` (`bw2/src/ov012/field_encount_st.c:19`) |
| Building textures, exterior / interior | `a/1/7/4` / `a/1/7/5` | 70 / 93 `BTX0` | `FieldPropSystem_LoadArea` (`bw2/src/ov036/field_buildmodel.c:101`) |
| Building packs ("bundles"), exterior / interior | `a/2/2/5` / `a/2/2/6` | 70 / 93 `AB` | same function; `ARCID_AREA_BMDATA_EXT/INT` (arc.h:68-69) |

All chunk models and building models are `BMD0` with **only an MDL0 block** (no textures inside); all texture
files have one TEX0 block **[bytes]**. Textures are bound by name at load time.

## 2. Map matrix (`a/0/0/9`)

Header (`MapMatrixFileHeader`, field_map.h:37; `ProcessMapMatrix`, map_matrix.c:97):

| Offset | Type | Meaning |
|---|---|---|
| 0x0 | u16 | format: 0 = chunk ids only, 1 = chunk ids + a zone id per cell |
| 0x2 | u16 | always 0 **[bytes]** |
| 0x4 / 0x6 | u16 / u16 | width / height in chunks |
| 0x8 | u32[w*h] | chunk id per cell (index into `a/0/0/8`), `0xFFFFFFFF` = empty; row-major, index = z*width + x |
| then | u32[w*h] | format 1 only: zone id per cell (game keeps it as u16, after `GetVersionedMapChangeZoneNum2`) |

- The game holds at most 900 cells (`struct MapMatrix`, field_map.h:9).
- 414 matrices are format 0, two are format 1: **matrix 0** (the Unova overworld, 29 x 27, 277 cells with a
  chunk, 187 distinct chunks, 53 zones) and matrix 175 (same chunks, different zone ids: 289-316) **[bytes]**.
- In matrix 0, 135 cells have a chunk but zone 0xFFFFFFFF (scenery); stepping onto them keeps the current zone
  (`fieldmap.c:1048` ignores 0xffff).
- Format 0 matrices give every cell the zone that loaded it. Interiors are almost all 1x1.
- Walking into a cell with a different zone id runs `Field_SwapZoneByMatrix` (`fieldmap.c:1055`): it reloads
  entities, BGM, fog, weather, camera boundary and place name, but **not** the area (textures/buildings).
- `a/0/1/0` replacements: `{u16 matrixId, u8 kind, u8 condition, u16 values[6]}`; kind 0 = swap chunk id
  values[0] for values[index], kind 1 = load another matrix; condition 0 = season, 1 = version, 2 = both,
  else a story event (`MapReplace_ResolvePatch`, `bw2/src/ov012/map_replace.c:49`). Example: Route 20's chunks
  286-289 become 290-293 in autumn (entries `(0,0,0, 286,286,290,286,...)` etc.) **[bytes]**.

## Map chunk containers (`a/0/0/8`)

Every entry is a Game Freak container: 2-char magic, u16 section count N, u32 offsets[N+1] (the last one is
the file size), sections follow. All 1065 match this, with offsets[0] = 4+4(N+1) and offsets[N] = file size
**[bytes]**; same as CTRMap's `GFContainer$GFContainerHeader`. Section use is from the accessors
(ov036 `FieldChunkAccessor_*`, `0x0218a7f8`..`0x0218ac90`) **[code]**:

| Magic | Count | Sections | Used for |
|---|---|---|---|
| `WB` | 3 | model (BMD0), terrain, buildings | normal chunks (961) |
| `GC` | 4 | model, terrain layer 0, terrain layer 1, buildings | two walkable layers (60; e.g. Lacunosa chunk 83, Humilau chunk 301) |
| `NG` | 2 | model, buildings | no collision at all; `NG_GetTerrain` returns 0 layers (36; Marine Tube, Castelia, Gear Station) |
| `RD` | 3 | model, extra data for Join Avenue's builder, buildings | Join Avenue (zone 490, matrix 376) (8) |

### 3. Terrain / collision section

`u16 width, u16 height` (always 32, 32), then `width*height` cells of 8 bytes, row-major (z*32 + x), then an
optional list of 8-byte "corner" entries. Size = 4 + 8192 + 8k for every terrain section **[bytes]**.
Decoder: `FieldChunkAccessor_GetTerrainCore` (ov036 `0x021c7028`) **[code]**; CTRMapV's `VMapTerrain$Tile`
reads the same fields.

| Cell bytes | Meaning |
|---|---|
| u16 @0, bits 0-1 | height kind: 0 = one plane (1,099,063 cells), 2 = two triangles (10,953); 1/3 never used (code treats them as flat y=0) |
| u16 @0, bits 2-15 | kind 0: slope index into `MAP_HEIGHT_SLOPE_TABLE` (ov036 `0x021d2a04`, 317 fx16 normals) |
| u16 @2 | kind 0: index into `MAP_HEIGHT_OFFSET_TABLE` (ov036 `0x021d3174`, 1285 fx32 plane offsets d). Kind 2: index of a corner entry |
| u32 @4, bits 0-15 | tile class (behaviour) - `GetTileClass` |
| u32 @4, bits 16-30 | flags - `GetTileFlags`; bit 16 = blocks movement (`MapTile_BlocksCollision`) |
| u32 @4, bit 31 | kind 2 only: which diagonal splits the tile |

- Corner entry: `u16 normalA (index<<2, low bits always 1), u16 normalB (index<<2), u16 offsetA, u16 offsetB`.
  Bit 31 = 0: triangle A where fx+fz < 1 tile; bit 31 = 1: A where fx > fz.
- Height: `y = -(nx*x + nz*z + d) / ny` with n raw fx16, d raw fx32, x/z in units **relative to the chunk
  centre**. Checked: with centre-relative x/z, 94% of walkable slope edges meet their neighbour within 1 unit
  (corner-relative: 66%) **[bytes]**. Flat ground uses normal 0 = (0, 4094, 0), so y ≈ -d/4094.
- **The slope and height tables are global and live in overlay 36**; chunks only store indices (max used:
  slope 315, offset 1283) **[bytes]**. A new map can only use heights that already exist in the table (flat
  heights -64..256 exist in steps of 8 except 168; many above 256 are missing) or must patch overlay 36.
- Town ground level is y = 16 in Aspertia (969 of 1024 tiles of chunk 279), matching its warp and NPC y values.

Tile classes found in code (ov036 `0x021a29ec`..`0x021a2ec0`, swan names) **[code]**; counts are over all chunks:

| Class | Meaning |
|---|---|
| 0x00 | plain floor (142,978 cells) |
| 0x01 | always paired with the collision flag: wall/out of bounds (818,660) |
| 0x04, 0x05, 0x21 / 0x06, 0x07, 0x22 | tall grass, single / double battles |
| 0x08 / 0x09 | very tall (dark) grass, single / double |
| 0x24 | Hidden Grotto entrance grass |
| 0x3d, 0x3e, 0x3f, 0x42, 0x43 | surfable water (`IsTileSurfWater`); 0x40 waterfall; 0x41, 0x44 shore/surf edge |
| 0x72 / 0x73 / 0x74 / 0x75 | ledge jumping right / left / up / down (`MapTile_IsLedgeR/L/U/D`) |
| 0x51-0x58 | block leaving in one direction (`TileExitBlockCheck_*`) |
| 0x0b, 0x0c, 0x23 sand (0x0c deep sand); 0x7c quicksand; 0x0e snow; 0x0f snow, no cycling; 0x10, 0x18 sliding ice; 0x1c swamp; 0x1d Strength hole; 0x30 electric floor; 0x32 electric rock; 0xbe/0xbf catwalk | terrain effects |
| 0xd4 counter, 0xd6 PC, 0xd8 TV, 0xd9-0xdc bookcases, 0xdd-0xde bins, 0xdf-0xe1 shelves, 0xe2 vending machine | interior "read" tiles |
| 0xff | invalid |

- Flags: bit 16 (flags & 1) = solid **[code]**; bit 17 (flags & 2) = can surf onto it (`CheckSurfBeginTiles`,
  `0x021a2ec0`) **[code]**. Water 0x3d carries flags 0x56 **[bytes]**.
- `GetTileEncountType` (`0x021a2e94`) maps 40 classes to another number (table `data_ov036_021d0324`, e.g. 0→4,
  4..9→5, 0x3d→6); its meaning (probably battle terrain) is not verified.
- **Doors and warps are not tile classes.** A warp is an entity at the door tile (section 5); the door's
  opening animation comes from the building pack.
- Example: Aspertia chunk 279 = 349 plain floor, 578 wall, 20 water (0x3d), 22 shore (0x41) cells **[bytes]**.

### 4. Building placements (last section of every chunk)

`u32 count`, then `count` entries of 16 bytes. Every chunk's section is exactly 4 + 16*count **[bytes]**.
`FieldPropSourceInfo` (`field_buildmodel.c:25`), used by `FieldPropSystem_InstantiateFromInfo` (:182):

| Offset | Type | Meaning |
|---|---|---|
| 0x0 / 0x4 / 0x8 | fx32 x3 | x, y, z relative to the chunk centre; **z is stored negated** (`z = -info->z`, :191) |
| 0xC | u16 | Y rotation, 0x10000 = 360° (0, 0x4000, 0x8000, 0xC000 make up 4396 of 4404 placements) |
| 0xE-0xF | u16 **big-endian** | building model id (resId = byte[0xE]<<8 | byte[0xF]), 0..511 |

- So world x = chunkX*512 + 256 + x, world z = chunkZ*512 + 256 - z. Checked: Aspertia's Pokémon Center (`pc_01`,
  chunk 279 at x=8, z=232, matrix cell (1,23)) lands at world (776, 11800); its door warp is at (776, 11832) **[bytes]**.
- CTRMapV's `ChunkBuilding` reads the same: VecFX32, unsigned 16-bit angle, byte-swapped u16 model UID.
- Coordinates may leave ±256 (big buildings over a chunk edge): observed x -296..384, z -479..304.
- 4404 placements in all chunks.

### Building packs (`a/2/2/5` exterior, `a/2/2/6` interior)

Also a GF container, magic `AB`, section count 2n: sections 0..n-1 are model info records, n..2n-1 are the BMD0
models (`FieldPropResBundle_GetResInfo` / `_GetModelData`, `field_buildmodel.c:309-318`) **[bytes + code]**.
Info record (`FieldPropResInfo`, `bw2/include/field/field_prop.h:42`): `u16 resId, u16 type, u16 doorResId
(0xFFFF = none), s16 doorX, doorY, doorZ, u16, u16`, then an animation header `{u8 controllerType, u8, u8
ambientCount, u8, u32 animOffsets[4]}` (0x24 bytes), followed by any embedded animation files.
**Doors** (door_fix 2026-10-11) **[code + bytes]**: each placed building with a door res gets a second instance, the
door model, at the building's position + (doorX, doorY, doorZ), *not* turned with the building, the door model
itself turned by the building's rotation (`FieldPropSystem_CheckCreateDoorReq` / `_InstantiateProps`,
`field_buildmodel.c:132-170`). Black 2 uses doorY -3..+11 on a few buildings. Door models: door_n_01-03 (259-261)
and door_t1_01 (164) a plate x -17..1, y 6..32, face at z +2; door_t1_02 (165, 236) x -18..2, y 4..33; door_pc (93)
a curved sliding door x -13.2..13.2, y 2.9..29.8, its arc from z 4.2 (ends) to 13.8 (middle). Black 2's houses keep
2-6 units of wall (or a canopy) over these doors and their eaves above them; `b2tools/door_check.py b2` measures all
70 exterior packs, `models` / `world` ours (buildings.DOOR_WALL, buildings.pc_door_hood).
The game maps resId → slot with a 512-entry lookup; a resId missing from the loaded pack falls back to the
default (0x15 exterior, 0x14 interior) (`FieldPropSystem_BuildResIDLUT`, :277). The pack and its textures use the
**same index** (pack i ↔ `a/1/7/4` or `a/1/7/5` entry i).

**Info `type` and hiding a building by script** (2026-10-06, Littleroot's moving truck) **[code + tested]**:
- Code uses the converted type `FieldPropResInfo_GetTypeConv` (`field_buildmodel.c:359`): lut `{0,1,1,1,2,0,3,4,5,6,7,8,9,1,1,1}`.
  Raw types seen: 0 buildings/props (most), 1/2/13/14 doors, 3 badge gates, 4 quicksand, 6 `pcmachine01`, 7 `pc01`,
  8/9 `pcev01/02`, 10 warp pads, 11 event props (`c09gate_main`, `c03_ship_02/03`, `tt_train01-10`, `c09_03_cart`),
  12 `pal01`. Only the PC/HOF/quicksand events and handle sounds read the type (callers of `FindPropsInArea`).
- `BMSetVisible type, x, z, visible` (cmd 301, ov036 `s012D_BMSetVisible`) → `FieldPropSystem_FindPropAtGPos`: position
  (x·16, 0, z·16) units (x, z in tiles, the tile's corner), search box x ± 2 tiles, z ± 3 tiles (inclusive,
  `FieldPropSearchArea_Set`), first prop whose **converted** type equals `type` (0 = any type); then
  `FieldChunkPropHolder_SetVisible` (saves/clears the instance's res index). So Black 2's `BMSetVisible 8, …` targets
  raw type **11** (`0274.s` → `c09gate_main` at tile (31.5, 50.5); `0836.s` → `tt_train01`), not `pcev01`.
- Black 2 calls it from `MapScript 3` / `MapScript 4` (field (re)load, field exists) and from events; `MapScript 2` runs
  at zone init, on a warp before the field is created: **a direct `BMSetVisible` there hangs the game after a warp**
  (black screen, tested); `RTReserveScript` from it to a script that hides works. Visibility lives in the chunk's prop holder: a reloaded chunk
  shows the model again, so a hidden model must be hidden again on every field load.
- Tested: Littleroot's truck (pack 0 res 460, raw type 11) at tile (169.56, 362.5) hides with `BMSetVisible 8, 170, 362, 0`,
  the one at (178.56, 362.5) with `BMSetVisible 8, 179, 362, 0` (from a reserved script, `RTReserveScript`).

## Area table (`a/0/1/3`, 409 x 10 bytes)

`u16 buildingPack, u16 texSet, u8 srtAnim (0xFF none), u8 patAnim (0xFF none), u8 isExterior, u8 lightsId,
u8 edgeColorTable, u8 actorMatColor` (getters at arm9 `0x02018f18`..`0x02018f44`) **[code + bytes]**.

- `isExterior` picks `a/2/2/5`+`a/1/7/4` (1) or `a/2/2/6`+`a/1/7/5` (0). 288 exterior, 121 interior areas.
- texSet == area id for all 409 **[bytes]**.
- Areas 2..281 are seasonal (`AreaData_HasSeasons`, `0x02018f48`): the game loads record `area + season`
  (`fieldmap.c:196-212`), so they come in fours (spring..winter) with the same pack and lights 140..143.
- **One area per field.** `AreaData_Create` runs only in `Field_Create` (`fieldmap.c:212`); walking into
  another zone does not change it. A warp/fly reloads it.

## 5. Zone entities (`a/1/2/6`)

`LoadZoneEntities` (`eventdata_system.c:62`): `u32 initOffset` (from byte 4), `u8 counts[4]` = signs/BG,
NPCs, warps, triggers, then the four arrays, then the zone's init-script table (CTRMapV calls it
`VZoneInitScriptDispatcher`). For all 615 files, initOffset + 4 = end of the arrays **[bytes]**.

**Warp, 0x14 bytes** (`ZoneWarp`, `bw2/include/field/zone.h:114`; CTRMapV `VWarp` agrees):
`u16 destZone, u16 destWarpIndex, u8 direction (0 any, 1 N, 2 S, 3 W, 4 E), u8 transitionType, u16 isRail`, then
grid `u16 x, y, z` (**world units**, x = tile*16 + 8), `u16 width, height` (tiles), `u16 unk`.
- The destination is "warp number k of zone Z": you arrive on that warp's position (`SetupWarpParamByWarp` :198,
  `GetGridWarpOutPos` :677). Warps come in pairs, e.g. Aspertia 427 warp 5 → zone 435 warp 0, and 435 warp 0 →
  427 warp 5 **[bytes]**.
- Type 1 fires on stepping onto it (interior exit mats); other types fire when walking into it in the matching
  direction (`GetWarpIDByPlayerPos` :124). Seen (meanings inferred from where they are): 3 = building door,
  4 = gate or cave entrance on a route (often 2-3 tiles wide), 2 = stairs, 57 = Aspertia Gym door.
- Hit test: x..x+16(w-1), z..z+16(h-1), y ± 2 (`CheckWarpPositionMatch` :691).

**NPC, 0x24 bytes** (`ZoneNPC`, `bw2/include/field/field_actor.h:78`): `u16 uid, modelId, moveCode, evType,
spawnFlag, scriptId, direction, param0-2, areaW, areaH; u32 isRail`; grid `u16 x, u16 z` (tiles), `fx32 y`.

**Sign / BG event, 0x14 bytes** (`ZoneBGEntity`, zone.h:69): `u16 scriptId, condition, direction, isRail`, then
`s32 x, s32 z (tiles), s32 y (units)`. **The header names them x, y, z, but the order is x, z, y**: the converter
`func_ov012_0215d88c` (:756) uses coords[1] as z and coords[2] as y, Aspertia data reads (56, 739, 16), and
CTRMapV's `VFurniture` reads gridX, gridZ, y.

**Trigger, 0x16 bytes** (zone.h:89): `u16 scriptId, workValue, workId, type, isRail`, then `u16 x, z, width,
height` (tiles), `s16 y`, `u16 unk`. CTRMapV names the types STANDARD, DIR_UP/DOWN/LEFT/RIGHT, DISABLED, COLLIDING, 7.

Script ids below about 2000 index the zone's own script file. Higher ids are global scripts (ranges in
`bw2/tools/scripts/field_commands.json`, `global_scripts`).

## 6. Zone header (`a/0/1/2`, 0x30 bytes; `bw2/include/asm/zone_header.inc:7-43`)

My byte parser matches `data/zones/0000_zone_headers.s` for all zones checked.

| Off | Field | Notes |
|---|---|---|
| 0x00 | u8 map_type | index into `MAP_CONFIGS` (29 kinds): 0 = overworld (2x2 chunks loaded around the player), 16 = interior (all chunks of the matrix loaded). 417 zones use 16, 143 use 0 |
| 0x01 | u8 npc_cache | |
| 0x02 | u16 area | `a/0/1/3` record (+ season for areas 2..281) |
| 0x04 | u16 matrix | `a/0/0/9` entry |
| 0x06 / 0x08 | u16 scripts / init_scripts | `a/0/5/6` entries; init = scripts + 1 (map script table) |
| 0x0A | u16 text | `a/0/0/3` entry |
| 0x0C-0x13 | u16 x4 | BGM per season (SEQ_*) |
| 0x14 | u16 | encounters (bits 0-12, `a/1/2/7` entry, 0x1FFF = none) + enc_slot (bits 13-15) |
| 0x16 | u16 entities | `a/1/2/6` entry |
| 0x18 | u16 parent | the main zone of a place (interiors point at their town) |
| 0x1A | u16 | place-name id (bits 0-9, line of system text 109) + display style (bits 10-15) |
| 0x1C | u16 | weather (0-5), projection (6-8), camera (9-15) |
| 0x1E | u16 | transition (0-4), battle bg (5-9), cycling, flag11, escape rope, fly-from, cycle/surf BGM, Entralink warp |
| 0x20 | u16 cam_bound | 0xFFFF = none; for interiors it usually equals the matrix id |
| 0x22 | u16 | name icon (0-12), Easy Mode level adjust (13-15) |
| 0x24-0x2F | s32 x3 | fly landing x, y, z (tiles, or rail coords) |

Encounter file (`bw2/include/asm/encounters.inc`): 8 rate bytes, then 56 slots of `u16 species|form<<11, u8 min,
u8 max` (12 grass, 12 dark grass, 12 shaking grass, 5 surf, 5 rippling surf, 5 fishing, 5 rippling fishing) =
232 bytes; 928 = four seasons.

## 7. Example places

All outdoor zones below use **matrix 0**; "cells" are matrix-0 cells (x, z) whose zone id is that zone.
Building counts are placements in those chunks **[bytes]**.

| Place | Outdoor zone | Area → pack | Cells → chunks | Buildings | Entities (sign/NPC/warp/trigger) | Other zones |
|---|---|---|---|---|---|---|
| Aspertia City | 427 | 210 → ext 52 | (1,22)→280, (1,23)→279 | 17 | 21/14/7/9 | interiors 428-436 (435 = Poké Center; 436 = Gym, matrix 51, entered by warp 4 in front of `c12_gym_01`), 489 (Gym battle area, matrix 275, `SEQ_BGM_GYM`), gate 438 |
| Route 19 | 437 | 214 → ext 53 | (1,21)→281, (2,21)→282 | 10 | 19/8/1/3 | enc 128 |
| Floccesy Town | 439 | 214 → ext 53 | (3,20)→284, (3,21)→283 | 14 | 19/9/5/6 | 440-443 (443 = PC), 600; Ranch 444 (cell (4,19)→285) |
| Route 20 | 446 | 214 → ext 53 | (4,20)→286, (5,20)→287, (4,21)→288, (5,21)→289 | 9 | 19/25/2/9 | autumn chunks 290-293; enc 129 |
| Nuvema Town | 389 | 2 → ext 0 | (24,23)→0 | 10 | 20/3/4/0 | 390-396 |
| Accumula Town | 397 | 2 → ext 0 | (24,20)→5 | 7 | 15/11/6/0 | 398 (PC), 399-405 |
| Lacunosa Town | 406 | 66 → ext 16 | (20,5)→83 (`GC`) | 12 | 15/15/5/5 | 407 (PC), 408-411; zone 315 is a copy on matrix 175 |
| Humilau City | 465 | 230 → ext 57 | (24,4)→301 (`GC`), (24,5)→300 | 26 | 22/16/8/4 | 466-470, 472 (PC), 473 (matrix 336, 1x3) |

Interiors (all map_type 16, 1x1 matrix, one `WB` chunk):

| Example | Zone | Matrix → chunk | Area → pack | Buildings (furniture) | Notes |
|---|---|---|---|---|---|
| Pokémon Center (Aspertia) | 435 | 13 → 827 | 283 → int 1 | 15 | 18 of the 21 zones with `SEQ_BGM_POKECEN` use matrix 13 + area 283 (the others: matrices 88, 89, 102) |
| Poké Mart | 435 (same room) | - | - | - | **No separate Mart building**: in the PC, NPCs uid 4 and 5 run zone scripts 1/2 (`data/field_scripts/0870.s:151`), which call global script 10110 = shop (`0870.s:159`, file 1247, text "Welcome! May I help you?") |
| Small one-room house (Floccesy) | 441 (442 shares it) | 261 → 977 | 349 → int 67 | 13 | room fills only the top-left ~12x10 tiles of the 32x32 grid; one warp back to 439 |
| Two-floor house (Aspertia) | 429 + 430 | 406 → 1049, 258 → 974 | 349 / 348 | 19 / 9 | 431 and 433 reuse matrix 406 |

## 8. Building models

- Exterior: **446 distinct models** (resIds 0..459 with gaps) across the 70 packs (28-72 per pack). Interior:
  **222** (0..223) across 93 packs. A given resId has byte-identical model data in every pack that holds it
  **[bytes]**, so resId is a global model id per side (exterior/interior). Textures still come per pack.
- Names come from inside each BMD0 (MDL0 model name). 28 models are in every exterior pack: `pc_01`, `gate_01`,
  `door_pc`, `door_normal01-03`, `sign01-04`, `rock_01/02`, `searock_01/02`, `plant_01`, `out_dust01`,
  `out_vender01`, `outwarp01-03`, `fountain_01`, `cart_01`, `thouse_01`, picnic set, ...
- Town sets (verified by what the town's chunks place): `c12_*` Aspertia (pack 52), `t06_*` Floccesy (pack 53,
  shared with Routes 19/20 and Floccesy Ranch), `t1_*` Nuvema and `t2_*` Accumula (pack 0, with Route 1's seasonal
  `r01_*`), `tg_*` Lacunosa (pack 16), `c14_*` Humilau (pack 57). Larger families: `rr_*` 44, `bc_*` 28 (Black
  City?), `wf_*` 26 (White Forest?), `c8_*` 24, `door_*` 23, `ptree_*` 20, `badgegate_*` 11.
- Interior names are generic furniture (`pc01`, `table01`, `chair01`, `shelf01`, `bed01`, `tv01`, `stair_u01`,
  `cashier01`, ...) plus place sets such as `ja_*` (34) and `c09gate_*` (17).

## Unknown / unverified (and what would settle it)

1. **Chunk 281 (Route 19, zone 437) uses 11 `C12_*` textures that are only in Aspertia's texture sets 210-213**,
   not in Route 19's own set 214. How the game draws a material whose texture isn't loaded is unverified. Settle:
   screenshot the south end of Route 19 in melonDS. Either way: **every chunk visible from a zone must have its
   textures in that zone's area texture set.**
2. Flag bits other than bit 16 (solid) and 17 (surfable). 0x80 (bit 23) is on most outdoor tiles (flag values 0x81,
   0x80, 0x84, 0x88, 0x24, 0x56...). Settle: find every `GetTileFlags` caller in ov036/ov012.
3. Tile classes with no named reader: 0x02, 0x03, 0x0a (24,925 cells), 0x16 (10,419), 0x1f (17,114), 0x9c
   (6,844), 0xfe (3,029; fills unused cells of GC layer 1). Settle: grep the disassembly for compares with these.
4. Meaning of `GetTileEncountType` values, the corner entry's low bits, building info `type` (settled for
   scripts: see "Info `type` and hiding a building" above) and the two u16 after the door offset. Settle: trace the callers.
5. Whether overlay 36's height/slope tables can be extended (needs a code patch; size and relocation limits unknown).
6. The camera-boundary format (`a/1/0/9`) and the `camera` / `projection` header values (`GetCameraIDForZone`
   uses `ZONE_CAMERA_ASSIGNMENTS` first). Settle: decode `FieldCameraBoundary_ChangeID`.
7. What matrix 175 (overworld copy naming zones 289-316) is for, and when B2 uses those zones.
8. Exterior areas name packs up to 76 and interior up to 93, past the archive ends (70 / 93 entries); the code
   then silently uses pack 0 (`FieldPropSystem_LoadResBundle`, :260). Which zones hit this is unchecked.
9. The coordinate frame of the chunk BMD0 vertices (assumed chunk-centred like buildings and terrain). Settle:
   export one chunk with `tools/apicula` and check the bounds are ±256.
10. Whether B2 accepts more zones/matrices/chunks than retail (615 / 416 / 1065) without code changes.
11. NPC `param0-2`, `evType`, sign `condition`, warp's last u16, and the init-script table layout (CTRMapV has a
    reader: `VZoneInitScriptDispatcher`).
