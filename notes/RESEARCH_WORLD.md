# Can Black 2 hold Hoenn's outdoor world? (research 2026-10-06)

**Short answer: yes, without code changes, if the whole connected overworld is one matrix and one area (one
texture set + one building pack) that stays inside the VRAM budget below.** The hard limits are not the counts
(matrices, chunks, packs and texture sets are read from the archives) but: 900 cells per matrix, zones only per
32×32-tile cell, one area per loaded field, 384 KB of texture VRAM, ≤128 building models per pack.

Sources: `bw2/` = `external/pokebw2`; `asm` = `tools/dsd dis` output (function names/addresses from
`bw2/config/b2_us/.../symbols.txt`); "bytes" = checked against `bw2/extract/b2_us/files`; "emu" = DeSmuME test
on a scratch ROM (patches described where used; ROMs deleted). Scripts that produced the numbers were scratch
files; the layout result is kept in `data/hoenn_world_layout.json`.

## 1. Limits

| Thing | Limit | Evidence | What it means for Hoenn |
|---|---|---|---|
| Matrix size | **≤ 900 cells** (w × h); w, h are u16 | `struct MapMatrix` has `zoneIds[900]`, `chunkIds[900]` (`bw2/include/field/field_map.h:9-20`); `ProcessMapMatrix` copies w×h ids with **no size check** (`bw2/src/ov012/map_matrix.c:97-125`) | Hoenn's overworld needs 26×13 (28×15 with a filler margin) — fits. Over 900 overwrites the heap. |
| Matrix 0's 29×27 | **not fixed anywhere found** | All matrix readers take w/h from the loaded file: zone swap (`bw2/src/ov036/fieldmap.c:1039-1067`), chunk streaming (`field_g3d_mapper.c` `GenLocators1`, skips cells outside w/h), map change (`bw2/src/ov035/event_mapchange.c:1550`), script reload (`bw2/src/ov012/scrcmd_game_state.c:278-282`), Dowsing MCHN (asm ov086 `func_ov086_021eaaf0`, overlay string `dowsing.c`). No other caller of the matrix functions exists in the asm. | Free to give matrix 0 any size ≤ 900 cells. |
| "Matrix 0" itself | special | `GetIsZoneMatrix0` (arm9 `0x02018cfc`, header matrix == 0). Used by the Escape Rope exit memory (`event_mapchange.c:1232`) and the Dowsing MCHN (ov086 `0x021eaaf0`). | **Put the Hoenn overworld in matrix 0** (or patch that compare). |
| Zone granularity | **one zone per 32×32-tile cell** | `GetChunkCoordOfWorld` divides by 0x1000/16/32 (`map_matrix.c:127-129`); `GetZoneIDAtMatrixXZWorld` (`:32-34`); zone 0xFFFF = keep current zone (`fieldmap.c:1048`). The only caller of the swap is the field loop (`fieldmap.c:1010-1017`; asm: no other callers). | Sapphire map borders that are not on 32-tile lines can't change zone exactly there (see §3). |
| Matrices (a/0/0/9, 416) | archive size only | `MapMatrix_Load` reads arc 9 by id (`map_matrix.c:17-22`); archive counts come from each NARC's FAT (`bw2/src/gfl/arc_tool.c:99,195`); no 416 (0x1a0) constant in the asm | Add or replace freely. |
| Chunks (a/0/0/8, 1065) | archive size only; **file ≤ 110,600 bytes** | chunk ids are u32 per cell; no 1065 constant in the asm. Map type 0 gives each chunk slot a 0x1b008-byte buffer (`MAP_CONFIGS[0]`, ov036 `0x021ca01c`, bytes +0x34) allocated at `bw2/src/ov012/field_g3d_map.c:34` and filled with **no length check** (`:262-294`). Largest retail chunk: 99,884 B (chunk 1028). | Keep every chunk file (model + terrain + buildings) under 110,600 B. |
| Chunks loaded at once | 2×2 around the player (map type 0) | `MAP_CONFIGS[0]`: load diameter 2,2, locator type 1 (bytes) | Anything visible must be within those 4 cells. |
| Zones (a/0/1/2, 615) | header file has no bound, but **615 (0x267) is the "no zone" value** | Header read at `id*0x30` with no check (`ZoneData_GetHeaderCore`, arm9 `0x02018818`). 0x267 is a sentinel in `InitZoneDataSystem` (cache key, `0x02018774`), `PlayerSave_Init` (`0x02008eec`), ov036 `func_ov036_021b59d4`, ov036 `DecideAbyssalRuinsDiveZoneByUndellaBayPos` / `GetAbyssalRuinsDiveZoneID` (`0x021c3d10`/`0x021c3d50`), ov012 `func_ov012_0215f55c`. Range checks: ov308 `func_ov308_021a0a30` replaces zone ≥ 615 by 317 for a location name; arm9 `func_02013bd4` rejects ≥ 615. | **Stay inside 0..614 by reusing Unova zones.** Hoenn has 394 maps (`notes/HOENN_SURVEY.md`), 65 outdoor. Avoid zones with hard-coded behaviour (Union Room, Entralink, Join Avenue 490, Abyssal Ruins, PWT, Victory Road, 478/479 (ov036 `0x0218141c`), etc.: the `IsZone*`/`GetZoneIs*` functions at arm9 `0x02018a54`-`0x02018ee4`). |
| Zone-keyed tables | searched lists, not arrays sized 615 | Sound (ISS): linear search, `ISSZoneSys_FindZoneDesc` `0x020323a0`, `ISSCitySys_SetUnitByZone` `0x02031190`. Fog `GetZoneFogIndex` `0x02018d50` (table = a/0/8/0 file 29, length/4 entries), lights `0x02018d90` (a/0/8/1 file 1), Flash `0x02018dd0` (a/1/4/9), all loaded by `InitZoneDataSystem`. Camera `GetCameraIDForZone` `0x02018e0c`: 9 entries, 11-bit zone ids. Weather `GetWeatherAll` `0x02032e94` → zone header, or calendar: **24** zones (ov012 `Calendar_Preload` `0x0215f3c0` reads 0x60 bytes of a/0/9/6 file 1; `Calendar_GetOffsetForZone` loop 0x18). A size scan of every archive found no other 615-entry table (heuristic). | Data edits, no code. |
| Fly / respawn points | **82** entries | `RESPAWN_ZONE_INFO[82]`, loops to 0x52 (`bw2/src/ov012/respawn_zone.c:6,92,112,125`) | Hoenn needs ~16; reuse entries. |
| Town map | **85** records × 54 bytes, keyed by zone id | a/0/8/5 file 0 = 4590 bytes (bytes); ov144 (string `townmap.c`): read `func_ov144_0219f718`, stride 0x36 `0x0219f730`, search loop 0x55 `0x0219f73c`. Records hold zone, screen x/y, fly flag (e.g. 389 → 232,158, flag 0x9a8). No matrix use in ov144. | Town map = new image + 85 records; matrix size irrelevant. |
| Areas (a/0/1/3, 409) | **id + season ≥ 409 → area 0** | `AreaData_Create` arm9 `0x02018ee4`, literal `0x199` at `0x02018f0c`. Seasonal: 2 ≤ id < 0x11a (`AreaData_HasSeasons` `0x02018f48`), game adds the season (`fieldmap.c:195-212`). | Reuse area records (288 exterior). For no seasons use an id in 282..408, or make all 4 seasonal records identical — and then any added *map* texture must go into all 4 sets. |
| Building packs (a/2/2/5, 70 ext) | archive size only; **≤ 128 models per pack**; resId < 512 | `FieldPropSystem_LoadResBundle` uses pack 0 only if id ≥ archive count (`bw2/src/ov036/field_buildmodel.c:255-266`); id→slot table is u8 with 0x80 = empty, slots ≥ 0x80 rejected (`:277-306`) | One pack for the whole overworld must hold ≤ 128 distinct building models. A missing resId draws the default model 0x15 (`:283-292`). |
| Field heap (map type 0) | 0x136800 − 0xf000 bytes | `MAP_CONFIGS[0].heapSize` (bytes); `fieldmap.c:131-132`. The whole pack is loaded into it (`field_buildmodel.c:262`). Largest retail exterior pack 223,356 B (pack 33). | A big shared pack costs heap; headroom not measured (Unknown). |
| ROM space | ~230 MB free | extracted files total 276 MB in a 512 MB image | Not a constraint. (`b2tools/build_rom.py` reserves only 8 MB for a/0/0/8: raise it.) |

## 2. Textures and buildings when walking between zones

**Code: walking into another zone never reloads the area.**
- The area is read once, in `Field_Create` (`fieldmap.c:186-212`). Map textures: `SetupLoadZoneMapTypeData`
  (`fieldmap.c:1496-1512`: arc 14, file = area's texSet, `isSharedTexResource = TRUE`) → `FieldG3DMapper_CreateMap`
  → `FieldG3DMapper_LoadMapTextures` uploads the whole set (`field_g3d_mapper.c:194-300`); chunks get no texture
  VRAM of their own (`textureVRAMSize = 0`, `:230`) and bind the shared set by name (`field_g3d_map.c:424`).
  Buildings: `FieldPropSystem_LoadArea` (`field_buildmodel.c:101-121`). Both run in `FieldRoutine_MapLoad`
  (`fieldmap.c:281-294`), i.e. only when a field is built (warp, fly, continue).
- `Field_SwapZoneByMatrix` (`fieldmap.c:1055-1091`) swaps entities (NPCs are deleted and the new zone's spawned:
  neighbours' NPCs are not visible across a zone line, as in Gen 3), BGM, fog, weather, camera boundary, scene
  area, place name, fly-point discovery and zone-init scripts. It does not touch `areaData`, textures, the building
  pack, lights, edge colours or the map type.
- **A missing texture draws flat white** (emu, no crash): area 3's texture set pointed at set 214 (which lacks
  Nuvema's `t01wd*` boardwalk textures) → the boardwalk renders solid white, everything else normal.
  Proof: `screenshots/tests/missing_texture_white_dock.png`.

**How Unova does it (bytes, matrix 0):**
- 29 pairs of neighbouring cells have zones with different areas. 28 have no walkable shared edge: they are
  joined through gate buildings (separate interior zones), e.g. Aspertia (427, area 210) → Aspertia Gate (438,
  interior, matrix 12) → Route 19 (437, area 214); Driftveil (96) → gate 106 → PWT (191).
- One open seam: **Route 13 (area 66) ↔ Undella Bay (area 70)**, 17 walkable floor tiles on the cell edge
  (23,8)|(24,8). Game Freak made the two sets overlap: with Route 13 loaded, Undella Bay's chunks miss 1 of 20
  textures (`sea_diving`); with Undella loaded, Route 13's chunks miss 0 of 38 textures and 1 building model (113).
- 134 of the 142 zoned cells use only textures in their own zone's set (every season). Exceptions: 6 seasonal
  chunks that `a/0/1/0` swaps in other seasons (Route 8/Icirrus 64-69 → 194-199) and 2 real ones: Route 10 chunk
  104 (lacks `grass01ax`, `ki02*` in set 282) and Route 19 chunk 281 (lacks 11 `C12_*` textures in sets 214-217).
  Emu: Route 19 next to the gate looks correct, so those materials are out of view there (where they are: Unknown).
- So Unova's rule is: **a texture set must contain every texture of every chunk visible from the zones that use
  it**; areas change only through warps, or where the two sets were built to overlap.

**VRAM (code):** the field uses VRAM A+B+C for 3D textures and G for texture palettes (`FIELDMAP_VRAM_CONFIG`,
ov036 data: texture 0x07, palette 0x40), managed by linked-list managers of **3 × 128 KB = 393,216 B** and
**16,384 B** (`GFL_G3DSysCreate(0, 3, 0, 1, …)`, `fieldmap.c:237`; `bw2/src/gfl/g3d_system.c:115-155`).

**VRAM (bytes, TEX0 sizes):** no set uses 4×4-compressed textures.

| Set | Largest | Median |
|---|---|---|
| Map textures a/0/1/4 | 168,448 B (sets 18-21, Castelia) | 41,712 B |
| Building textures a/1/7/4 (ext) | 96,608 B (pack 31, Pokémon League) | 22,368 B |
| Building textures a/1/7/5 (int) | 122,272 B (pack 71, Join Avenue) | 11,520 B |
| Exterior area total (map + building) | **185,056 B (Castelia)** | ~75 KB |
| Palettes, exterior area total | 6,176 B | — |
| All distinct Unova exterior map textures | 1,786 textures, 1.31 MB | 512 B each |
| All distinct exterior building textures | 868 textures, 0.93 MB | — |
| Current slice (area 2 summer: set 3 + merged pack 0) | 44,688 + 70,720 = 115,408 B | — |

**VRAM (emu, measured):** free lists of the texture manager (head pointer at `0x02141a54`, blocks
`{addr, size, prev, next}`; size at `0x02141a60`) and palette manager (`0x02141a70`, size `0x02141a78`), found from
`NNS_GfdInitLnkTexVramManager` (arm9 `0x0205fcd8`) / `func_0205fd10` / `NNS_GfdInitLnkPlttVramManager`
(`0x0205fefc`). Reached by pointing Nuvema's door warp at each place on a scratch ROM; October = summer records.
"Other" = used − (map set + building set): player, NPC sprites, effects… (not broken down).

| Place | Map type | Map + building sets | Texture VRAM used | Other | Free |
|---|---|---|---|---|---|
| Aspertia house 428 (interior) | 16 | 33,744 | 79,952 | 46,208 | 313,264 |
| Aspertia Gate 438 (interior) | 16 | 136,320 | 284,032 | 147,712 | 109,184 |
| Aspertia 427 | 0 | 113,264 | 215,280 | 102,016 | 177,936 |
| Nuvema 389 | 0 | 103,600 | 229,296 | 125,696 | 163,920 |
| Route 19 437 | 0 | 88,864 | 226,720 | 137,856 | 166,496 |
| Humilau 465 | 0 | 95,584 | 260,640 | 165,056 | 132,576 |
| Castelia 28 | 2 (rails) | 185,056 | 238,960 | 53,904 | 154,256 |

Palette VRAM peaked at 7,584 of 16,384 B (Castelia). **Budget for one Hoenn area (map + building textures):
≤ ~185 KB is proven by Castelia; on map-type-0 towns "other" reached 165 KB, so ~228 KB (393,216 − 165,056) is
the ceiling seen so far — plan for ≤ ~200 KB and measure.**

## 3. Layout

**Geometry (from pokeruby `data/maps/*/map.json` connections; result in `data/hoenn_world_layout.json`):**
- 49 of the 65 outdoor maps form one walk/surf-connected world: 56 connections, 8 independent loops, **0
  conflicts and 0 overlaps**, so Sapphire's world is one consistent grid of **800 × 380 tiles**.
- Best global offset (+16, +28) puts it in **26 × 13 cells** (338 ≤ 900; 28 × 15 = 420 with a 1-cell filler margin,
  needed because cells outside the matrix are not drawn). **190 cells hold map tiles**; 127 hold one map, **63 hold
  2-4 maps** (24 route|town, 10 sea|town, 17 route|route, 12 sea|sea). Worst offsets give 224 cells / 92 mixed.
- 16 maps are reached only by warps (Petalburg Woods, Jagged Pass, Mt Chimney, Mt Pyre ×2, Sky Pillar ×2,
  Southern Island ×2, Battle Tower outside, Sootopolis, Safari Zone ×4 (one consistent 4×4 block), plus the 1×1
  test map `Route104_Prototype`): **44 chunks** rounded per map.
- **Chunk estimate: ~190 + ~44 ≈ 234 unique chunks, plus a few reusable filler chunks** (a chunk id may repeat:
  Unova's chunk 104 fills 3 cells). Rounding every map up separately would be 220 + 44 = 264, but then the
  geometry no longer closes around the loops.
- Snapping every map edge to chunk lines by inserting whole rows/columns makes the world 38 × 22 cells (+52 %
  width, +85 % height); snapping only town edges is impossible (9 gaps where no insertion line misses a town, e.g.
  Littleroot/Slateport/Pacifidlog z 280-300).

**Options**

| Option | How | Pro | Con |
|---|---|---|---|
| **A. One matrix, one area (recommended)** | Matrix 0 = Hoenn overworld (format 1), exact geometry, 1-cell filler margin. One exterior area: one curated texture set + one pack. | No code. Truly seamless. Matches Unova's rule. Escape Rope/Dowsing work. | All overworld textures within ~185-200 KB and ≤ 128 building models; one lighting/edge-colour set. Mixed cells (below). |
| B. Several areas + gates | Split at chokepoints with Gen 5 gate buildings or warps (Gen 3 has a few natural ones: Cycling Road entrances, Petalburg Woods, tunnels). | No code; each region gets its own budget. | Adds fades/buildings Sapphire doesn't have; most of Hoenn (incl. the sea) has no natural break. |
| C. Code patch: reload area on zone change | Hook `Field_SwapZoneByMatrix` (`fieldmap.c:1055`) to reload map textures and the pack when the area differs. | Unlimited regional sets. | New code (no free-space study done); upload stall; the 2×2 window shows the other region before and after the switch, so the boundary band must still use shared textures (place it in open sea). Pack reload must re-link props in loaded chunks. |
| D. Zone-lookup patch | Replace the 32-tile cell lookup (`GetZoneIDAtMatrixXZWorld`, ov012 `0x02154af0`) with per-map rectangles. | Exact Sapphire zone borders. | New code; Dowsing uses the same lookup. |

**Mixed cells under option A:** give each mixed cell the zone of the map with most tiles there, or 0xFFFF (zone
stays what it was until a single-map cell). BGM, banner, wild table and entities then change up to 31 tiles from
Sapphire's border. Entities (NPCs, signs, warps, triggers) use global coordinates, so an object of map B inside a
cell owned by zone A goes into A's entity file (into both files with 0xFFFF). Local padding (like Route 101's 12
extra rows) is safe only on dead-end branches: Littleroot–Route 101 is one (only Oldale connects onward), so the
current slice fits this plan; padding inside any of the 8 loops breaks the loop.

**Recommendation:** A, with build-time checks (map set + building set TEX0 ≤ ~200 KB; ≤ 128 models in the pack;
every chunk ≤ 110,600 B; zones < 615; matrix ≤ 900 cells), and a VRAM measurement of the heaviest town once it
exists (read `0x02141a54` as above). Share terrain textures across all towns; give towns their look through
building textures. Fall back to B (a few gates) or C only if the budget is exceeded. Moving the slice from Unova
cells (24,21..23) into the Hoenn matrix needs the entity/warp coordinates re-based (chunks themselves are
position-independent).

## Unknown (and what would settle it)

1. **What the 46-165 KB of "other" texture VRAM is** (NPC sprites — a/0/4/8 holds 968 BTX0, median 3.5 KB, max
   30 KB — effects, water?) and its worst case in a busy Hoenn town. Settle: log every `NNS_GfdAllocTexVram`
   (callers of `g_TexVRAMAllocFunc`) with sizes in the emulator, or measure the finished towns.
2. Free field-heap headroom for one large shared building pack. Settle: read the GFL heap free size in-game after
   loading a big pack.
3. Option C/D feasibility: free code space for hooks, upload time of ~200 KB mid-walk. Not studied.
4. Whether zone ids ≥ 615 are safe elsewhere (save data, records/Xtransceiver). Only the spots in §1 were found;
   avoided by staying < 615.
5. How the town map (ov144) places the player marker on routes; only the 85-record table was decoded.
6. Where the `C12_*` materials of Route 19 chunk 281 and the trees of Route 10 chunk 104 are, and whether they show
   in any view. Settle: render the chunk models with `tools/apicula` and locate those materials.
7. Camera boundaries (a/1/0/9, zone header `cam_bound`): whether a new overworld needs entries. Settle: decode
   `FieldCameraBoundary_ChangeID`.
8. pokeruby connection offset semantics were assumed (up: x + offset, above; left: y + offset, to the left); the
   0 conflicts across 8 loops strongly supports them but no map was checked against Sapphire's in-game world map.
