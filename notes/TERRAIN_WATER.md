# How Black 2 builds water, and how Hoenn copies it (2026-10-06)

Module: `b2tools/terrain/water.py` (classes `water`, `deep_water`, `current_n/s/e/w`, `waterfall`, `puddle`,
`water_edge`; 41k+ tiles). Same units as notes/GEN5_TERRAIN.md: 16 per tile, chunk centred on the origin, y up.
Tags: **[code]** read in the decomp / disassembly (`b2tools/armdis.py`), **[bytes]** read from the user's dump
(`external/pokebw2/extract/b2_us/files`; chunks converted with `tools/apicula` to glTF and their `.per` collision
parsed), **[test]** seen in DeSmuME on our ROM. UV note: apicula's glTF has `v_gltf = 1 - v_dae`; the recipes
below are in our DAE convention (as GEN5_TERRAIN.md).

## Reference chunks

| Place (zone) | Chunk | Area (summer) | What it shows |
|---|---|---|---|
| Route 1 (317) | 2, 3 | 2 (**3** = Hoenn's own texture set) | sea, beach, sea cliffs |
| Route 3 (321) | 15, 16 | 6 (7) | pond with grass banks |
| Striaton (6) | 11 | 6 (7) | pond |
| Route 11 (365) | 72, 73 | 54 (55) | river, waterfall |
| Route 13 (370), Undella Town (412), Undella Bay (240) | 85-92, 93-94, 247/260/263/264 | 66, 70 (67, 71) | beach, shallows, dive spots |
| Route 14 (374) | 95-98 | 70 (71) | waterfalls |
| Route 17/18 (423/387) | 22-28 | 122 (123) | sea currents |
| Route 6 (331), Pinwheel Forest (154) | 53/54, 19-21 | 34 (35), 10 (11) | puddles |
| Humilau (465) | 300, 301 | 230 (231) | shallows |

Chunks were found by matrix 0's zone ids (format 1, `a/0/0/9` entry 0) and the zone names in
`data/zones/0000_zone_headers.s`; texture users by searching `a/0/0/8` for the material name bytes
(`mizutama01`: chunks 19-21, 53/54, 58-60, 63; `sea_asase*`: 23-25, 90, 247, 265, 299; `sea_diving`: 247, 260, 264;
`sea_nagare*`: 22-25) **[bytes]**.

## Collision

Tile classes **[code]** (overlay 36): `IsTileSurfWater` 0x021a2cb0 = classes 0x3d, 0x3e, 0x3f, 0x42, 0x43;
`IsTileWaterfall` 0x021a2c10 = 0x40; `MapTile_IsSurfEdge` 0x021a2be4 = 0x41, 0x44; 0x021a2c04 = 0x17;
0x021a2bf4 = 0x14 or 0x15; `IsTileSand` 0x021a2c7c = 0x0b, 0x0c, 0x23; 0x021a2c70 = 0x19.

Starting to surf **[code]**: `CheckFieldEnvInteraction` (ov036 0x02182e54) → `CheckSurfHeightAllow` (0x0219ab30):
not already surfing; `CheckSurfBeginTiles(tile under, tile in front)` (0x021a2ec0): the tile under must not block,
the tile in front needs flag 0x02 and must not block (or be a surf edge 0x41/0x44, which you jump over:
`CreateSurfPos`, `src/ov033/event_fishing.c:27-66`); and `0 <= y_player - y_water < 20` units.
Our water is 8 below the land, like all of Black 2's (below). Since bridge_surf (2026-10-20) a tile with NOSURF (Gen 3's
elevation rule) refuses it too: "Surf start and surf traps" below.

| Hoenn | Record (incl., height idx, class, flags) | Black 2 source **[bytes]** |
|---|---|---|
| sea, deep water, currents off | (0, 61, 0x3f, 0x16) | Route 1 chunk 2 (68 tiles), Route 13, Route 17, Undella Bay (461 in chunk 247) |
| pond (Sapphire MB_POND_WATER) | (0, 61, 0x3d, 0x56) | Route 3 chunks 15/16 (141/146), Striaton chunk 11 |
| waterfall | (0, 61, 0x40, 0x13) | Route 11 chunk 72, Route 14 chunks 95/97/98 |
| shoal (Sapphire MB_SHALLOW_WATER) | (0, 61, 0x17, 0x10) — at the sea's height | Undella Bay 247 (87), Route 13 86/87/90, Humilau 301 (157) |
| puddle (MB_PUDDLE, Lavaridge hot springs) | (0, 3, 0x14, 0x40) — at ground height | Route 6 53/54, Pinwheel Forest 19-21, Mistralton 59, Route 7 60 |
| beach sand with water drawn (water_edge on MB_SAND) | (0, 3, 0x19, 0x88) | Undella Town 94, Route 17/18 26-28 |
| west/north/south/east current | (0, 61, 0x95/0x96/0x97/0x94, 0x02) | Route 17 chunks 24/25 (lanes of 0x94-0x97 next to `sea_nagare01`) |
| unsurfable water (Sapphire blocks it) | (0, 61, 0x01, 0x81) | Black 2's wall record at the water's height |

- Height index 3 = y 0, 61 = y −8.0 (MAP_HEIGHT_OFFSET_TABLE, ov036 0x021d3174) **[bytes]**. Water is always 8
  below the land beside it **[bytes]**: Route 3 land 0 / pond −8; Route 1 beach −16 / sea −24; Route 17 sand −16 /
  sea −24; Undella sand −80 / sea and shallows −88. With heights.py enabled the water module puts its records at
  that module's water level − 8 (`heights.flat_index`), because heights.py only re-heights ground-level records.
- Black 2 lines most ponds/rivers with a row of solid surf-edge tiles (0x41/0x44) that the surf start jumps over.
  Hoenn doesn't: Sapphire lets you surf onto the first water tile, and Black 2's Undella beach does the same (sea
  0x3f straight next to shallows 0x17 / sand 0x19) **[bytes]**.
- Shoals sit at the water level, 8 below the sand, as in Undella; puddles stay at ground level, as in Route 6.

## Geometry

| Thing | Black 2 **[bytes]** | Hoenn recipe |
|---|---|---|
| Sea | `sea_mizu1` twice: material `sea_mizu1_1` (same texture, **alpha 16/31**, blend) 3 below the water's collision height, opaque `sea_mizu1` 16 below it; one quad over the whole chunk, 1 repeat per 4 tiles (Route 1 chunk 2: −27/−40 for water at −24; Undella: −91/−104 for −88) | translucent at −11, opaque at −24 (land 0, water −8); one quad per rectangle of water tiles; the opaque layer reaches 2 tiles under the banks |
| Pond | `ike01` (**alpha 12/31**) at the collision height, 1 repeat per 2 tiles; opaque `mizu_sita2` 24 below, 1 repeat per 8 tiles, reaching under the banks (Route 3 chunk 15) | same: −8 / −32 |
| Grass bank | `gake1_1` from the land edge (y 0) down to −8 in half a tile, then `shore01` to −12 at 3/4 tile, both inside the water tile; 1 repeat per tile along the edge; corners mitred / chamfered diagonally (Route 3 chunk 15) | same; collinear edges merged into strips; a 1-tile channel squeezes the profile to 2/3 |
| Beach | dry `sea_jimen` at land height, wet `sea_simi.1` sloping 8 down over one tile then flat, foam `sea_zanami` (blend, v 1→0.66) from +1 to −7 over it, `sea_zanami2` band (1.25 tiles) on the water (Route 1 chunk 2; Undella Bay 247 where the sloped tile is a walkable sand tile with a slope record) | the same layers squeezed into the water tile (wet sand 0→−9 over 3/4 tile, foam, band) so Hoenn's sand tiles stay flat and walkable |
| Shallows | flat `sea_asase02` at the collision height (Undella −88); a 1-tile `sea_zanami2` band on the sea around them, level with them (Undella Bay 247) | `sea_asase02` at −8; band on the sea tiles beside a shoal; beach bank where land meets a shoal |
| Deep water | `sea_diving` (dive-spot ring) between the two sea layers at −94 (Undella Bay 247) | a flat dark-blue texel of `sea_diving` (08395a) at −14 under the translucent layer, over the deep tiles |
| Waterfall | one tile row of class 0x40 between river levels; `kawa01b` sheet (+ `kawa01b_1/_2` at the foot), `kawa01a` side streaks, `taki_sakai.1` lips, `taki_shibu.1` spray (Route 11 chunk 72) | flat for now (`kawa01b` sheet, `kawa01a` sides, `taki_shibu.1` where it meets water); see open items |
| Puddle | `mizutama01` (blend; opaque grass-coloured rim, interior alpha ≈ 0.48) at ground height; each tile in quarters: rounded corner from the image's top-left quarter (u,t 0-0.47), straight rim from its right half (u 0.53-1, t 0-0.5), centre texel inside (Route 6 chunk 53, Pinwheel Forest chunk 21: 130 triangles over rectangular puddles) | the same quarters chosen per tile from its neighbours (concave corners use the centre); 1 unit above the grass (we can't set Black 2's depth-equal polygon mode) |

Materials with alpha and the second sea layer go through a write hook in water.py (dae.py has no material alpha
and binds a material to the texture of the same name): `<transparent opaque="A_ONE">` + RGBA vertex colours, and
material `sea_mizu1_1` pointed at image `sea_mizu1`. Checked by converting our `.nsbmd` back with apicula:
`sea_mizu1_1` uses the same texture as `sea_mizu1` with alpha 16/31, `ike01` alpha 12/31, exactly as Route 1 and
Route 3 **[test]**. The ground under water tiles is cut out when the model is written, so it also works when
heights.py draws the ground (checked: Route 120's plateau ponds at 24 = level 32 − 8, collision 24, puddles 32).

## Animation (no area-table change needed)

Area records (`a/0/1/3`, 10 bytes) **[bytes]**: area 3 (= Hoenn's area 2 in summer) has srt 0, pat 0 (so do the
Route 3, 11, 13 and Undella areas); Route 17/18's areas 122/123 use srt 44, pat 4; Humilau's srt 50.
`fieldmap.c:1509-1510` passes them to `FieldG3DMapper_CreateTerrainAnimator` (`field_g3d_mapper.c:771-786`) **[code]**.
- SRT 0 (`a/0/6/8` entry 0, BTA0 "area_ita_00", 240 frames; read with `apicula info`) animates materials
  `ue_grass01, kawa01a, kawa01b, kawa01b_1, kawa01b_2, shore01, sea_zanami2, sea_zanami, sea_mizu1, sea_mizu1_1,
  sea_gake02, sea_asase02, mizu_sita2, ike01` **[bytes]**. SRT 44 adds `sea_nagare01` (currents) and `kawa01b_3`.
- Pattern 0 (`a/0/6/9` entry 0, Game Freak format with embedded BTX0 frames) swaps the images of `sea_simi.1-4`,
  `kawa_fuchi.1-4`, `taki_sakai.1-4`, `kawa_nose.1-2`, `hana01.1-4`, `taki_shibu.1-4` **[bytes]**.
- Hoenn's water uses exactly these names, so it animates as is: at the Route 104 shore, 9-10k of the ~12.6k water
  pixels change between frames 15-90 apart, the land region 0 **[test]**. No `hoenn_water.py` patch.

## Textures and budget

All but two textures are already in set 3: `ike01, mizu_sita2, shore01, gake1_1, sea_mizu1, sea_simi.1,
sea_zanami, sea_zanami2, sea_jimen, kawa01a, kawa01b, taki_shibu.1, mizutama01` **[bytes]**. Added:
`sea_asase02` (Route 13 summer set 67, 16×16 4-colour) and `sea_diving` (Undella Bay summer set 71, 16×16
16-colour): hoenn_textures reports set 3 53,184 → 53,512 B (+328 B), 127,464 B with the building set **[test]**.
Largest chunk with water: 57,932 B (Lilycove cell 18,4) of 110,600.

## Sea outside the maps (world.py filler hook)

`world.py` builds a 1-cell ring around the maps and filled every non-map tile with forest. The hook (two lines in
`build_cell`'s forest loop): `fillers = [f.filler for f in FEATURES if hasattr(f, 'filler')]`, and a 2×2 forest
square is skipped when any module's `filler(world, wx, wz)` returns a class for one of its tiles. water.py's filler:
a multi-source BFS from every map tile over the non-map tiles (radius 128, more than the ring); a tile is sea when
the nearest map tile is surface water. Those tiles are drawn as sea (with banks against forest) and stay solid
(Sapphire's map borders can't be crossed). Whole sea cells are 4 triangles.

## Emulator tests (`work/agents/water/rom`, DeSmuME)

- Route 104 shore, surf, open sea, landing **[test]** (`screenshots/water/route104_shore_surf.png`): with the
  Balance Badge (hm_free requires it even when a Pokémon knows Surf) facing the sea: "The water is a deep blue...
  Would you like to surf on it?" → Yes → surfing on our 0x3f tiles; a wild battle there uses the water background
  (water encounters work); stepping onto the sand dismounts.
- Petalburg's pond (`petalburg_pond.png`), Route 124 shoals with deep water around an island
  (`route124_shoals_deep_water.png`: walking on 0x17 shows Black 2's wading ripple), Route 120 puddles
  (`route120_puddles.png`: 0x14 shows the puddle ripple) **[test]** (shoal/puddle arrivals used a scratch patch
  that moves the test door's arrival; not in b2tools/patches).
- Currents **[test]** (scratch ROM: Route 104 sea at x 56-61, z 300-304 turned into one class, surfing onto it):
  0x95 carried the player west 6 tiles after one tile of input (`current_test_west.png`), 0x96 north
  (60,302)→(60,299), 0x97 south (60,302)→(60,305); the carry stops on the first non-current tile — **even a solid
  one** (the 0x95 run ended on the rock tile (55,302)). So Hoenn's current tiles whose next tile downstream isn't
  open surfable water stay plain sea: 3,554 of 3,777 west, all 236 north and 142 south currents keep their class.
  `HOENN_WATER_CURRENTS=0` turns all currents into plain sea.

## Rock banks under water-entrance cave mouths (cave_mouths agent, 2026-10-07)
The bank of a water tile whose land is the rock round a cave mouth entered from water (terrain/cave_mouth.py
`rock_shore`: Lilycove's Aqua Hideout, Route 120's Scorched Slab) is rock, not grass: on the sea `ROCK_SEA_BANK`,
Black 2's rocky waterline at a sea cliff's foot (Route 1 chunk 3: sea_gake01 from 1 over the land at its edge to 2 over
it 5 units out, down to the water's collision height 11 units out, v 1 -> 0.69 -> 0, repeat s only) [bytes]; on a pond
`ROCK_POND_BANK`, the pond bank with the rock lip gake1_0 instead of gake1_1 (Black 2's ponds are all grass-banked,
Route 3 chunks 15/16, Striaton 11: shore01 only ever meets gake1_1 [bytes]). Both textures are in set 3 (0 bytes).

## Open

- Waterfalls are flat sheets on the water; Black 2's are one tile row between two water levels 80 units apart
  (Route 11). Sapphire's are 3-6 tile columns. Needs heights.py's levels for the river above and below, then a
  vertical sheet; climbing/descending (Waterfall, `CheckAutoTileEvents`) untested (no reachable waterfall yet).
- Deep water has square edges (Sapphire's tile layout); Black 2's dive spots are round rings. Could use the ring
  quarters of `sea_diving` like the puddle corners.
- Beach slope is inside the water tile (Black 2 slopes the last sand tile, record class 0x19 with a slope).
- Unsurfable water (Sapphire's map-border water) is solid at the water's height; Dive spots (deep water) are plain
  surfable sea (no Dive in Gen 5).

## Water seams (water_seams, 2026-10-19) [code][test]
Discord (Emerald, "Oldale Town", evening): thin light lines across a rectangular pond by an orange-roofed house and
trees, Brendan on the grass bank to its right. melonDS on the v18.0/E v1.1 geometry shows exactly that at Petalburg
City's pond (tile (96, 312): two horizontal lines, the middle one going on over the left bank, and a thin vertical one
in the lower part, on the cell border x = 96); Route 102's east pond 5 tiles west of Oldale (x 158-163, z 302-306, in
Oldale's cell (5, 9)) had the same kinds of lines (screenshots/water_seams). Same geometry in Sapphire/Ruby. Causes,
all fixed in terrain/water.py:
- **Grass over the water** (the lines DeSmuME shows too: Petalburg's two, Route 102's bank line, wedges over Route
  114's ponds). tjunction.fix ran before the ground over water was cut (the cut ran when the model was written) and
  re-fanned the ground's rectangles; the cut reads triangles by rounding corners to the tile grid, wrong for fans, and
  kept slivers of ground over water: 182 triangles in Sapphire's world, 189 in Emerald's (~25 cells each).
  `water.cut_ground_now` cuts before tjunction.fix (world.py write_cell): 0 left in both.
- **Cracks in the water's layers.** The DS opens 1-pixel cracks along edges inside a surface (T-junctions, and shared
  edges too). Through the translucent sheet (ike01 12/31) the light pond floor shows; through an opaque floor
  (mizu_sita2, sea_mizu1) the sky. A cell border through a pond (x = 160 at Route 102, x = 96 at Petalburg) gives
  T-junctions tjunction.fix can't see (it works per cell). Fix (`_seam_layers`): under every sheet a second sheet of
  the same material in the same plane (one quad per water body, its bounding box reaching 2 tiles into the next built
  cell, water under a deck counted at its own level, diagonal the other way), under every floor a second floor 4
  lower. A same-ID translucent pixel is never blended twice on the DS, so the second sheet only shows through the
  first one's cracks; `nsbmd_fix.water_materials` (patches/hoenn_world.py) gives ike01 polygon ID 2 and sea_mizu1_1 ID 3
  in every chunk (CTRMap numbered them by material index, 2-8 and 1-22, so neighbouring cells also blended twice along
  their border; Black 2: ike01 0, sea_mizu1_1 3). The box is used only where its other tiles hide the layer; else
  (water of another level in it: Route 119's falls) the box's tiles that do, in column rectangles.
- **Cracks where a bank meets the ground** (or a cliff's foot): the ground and the cracks fix's under-floor both end
  on the bank's top line. `_bank_seams`: a strip of the land's ground 6 under the water's land level, 14 units into
  the land tile and 2 under the slope.
- Every seam quad is cut at half tiles into pieces at most 4 times as long as wide (`_square_pieces`): the diagonal of
  a long thin quad runs within a pixel of the edges beside it for a long way, where cracks of both layers can meet.
- Cost: Emerald a/0/0/8 +797 KB (it had 1.56 MB spare); largest chunk 110,364 B (22, 5) of 110,600. world.py
  chunk_fit drops the water seams first at each step, so no cell has less of the ground cracks fix than in v18.0/E
  v1.1: (13, 4) keeps its T-junction splits now (without water seams); (22, 6) keeps v18's state. outdoor_check size 0
  in both worlds; collision, placements and world.json byte-identical to v18.0's/E v1.1's (walk_diff can't change).
- Check: `python3 b2tools/water_seams_check.py WORLD [--before WORLD0] [cx_cz ...]` (inner edges of each water layer and
  whether a polygon of the layer or the one under it backs them, water bank tops, ground over water, area the new
  layers add where nothing hides them). `outdoor_check --kinds layer` accepts the coplanar seam sheets (ike01/ike01).
- Left: the mitred corners of the banks (short diagonal seams over the floor) have no layer under them; cells (13, 4)
  and (22, 6) have no water seams (chunk buffer).

## Surf start and surf traps (bridge_surf, 2026-10-20) [code][test]
Discord (Emerald v1.0.4, video): from Route 119's plank bridge by the Weather Institute the player surfed north into the
short river below the waterfall, could not get back onto the bridge and had no other way out (no Fly or Teleport).
- **Gen 3** [code] (pokeruby / pokeemerald `field_player_avatar.c`): `IsPlayerFacingSurfableFishableWater` starts a surf
  only when `PlayerGetElevation()` (the player's previousElevation) is 3 and the water's elevation mismatches the
  current one (a current elevation 0 never mismatches). A bridge tile (elevation 15) keeps the elevation the player
  carried onto it (`ObjectEventUpdateElevation`). Route 119's bridge (Route119 (16-20, 33-34)) has elevation-4 land at
  both ends (Route119 (14-15)/(21-22)), so Gen 3 never surfs off it - nor off the river's elevation-4 banks south of it
  (Route119 (16-18,44), (21-22,46), (24-26,47)). A surfer (elevation 1) passes under elevation-15 tiles, and lands only on
  elevation 3 (`CanStopSurfing`): the pocket below the waterfall is reached and left under the bridge, and has four
  elevation-3 tiles to land on (Route119 (16,29-30), (20,29-30)).
- **Black 2** [code]: `CheckSurfHeightAllow` (ov036 0x0219ab30) wants only `0 <= y(tile under) - y(water) < 20` and a
  non-solid tile under (`CheckSurfBeginTiles`). In v1.0.4 the deck stood 8 over the water in one layer: surf off it,
  no landing back on it (NOLAND, step 12) and no way under it: trapped. `b2tools/surf_trap_check.py` on that world
  (work/agents/bridges/world_base) finds exactly this pocket plus three more traps at Route 120's two bridges. v18.0 /
  Emerald v1.1 raised the decks 32+ over their water with two collision layers (notes/TERRAIN_GROUND.md): the height
  refuses the surf off, a surfer passes under. **v1.1/v1.2 have no trap at any bridge** (checked on the release ROMs'
  own collision: v18.1 Sapphire and Ruby and Emerald v1.2 are byte-identical to work/world and work/world_emerald).
- **Emerald v1.2 still had a trap elsewhere**: Mossdeep's north shore (MossdeepCity (54-55,4) elevation 7 at 64,
  (61-69,6) elevation 9 at 96) stands 8 over the water north of it, a 941-tile sea (Route 125's east end) no Gen 3
  player reaches and that has no landing: surf off = stuck. And the Safari Zone southeast (Emerald): the pond under the
  waterfall stood at two levels 32 apart (the grass east of it, an island, had taken the upper river's level), so a
  surfer who came down the waterfall reached no shore.
- **Fix**: heights.py step 12b sets the collision flag NOSURF (0x2000) on walkable tiles beside surf water where
  Sapphire's player never has elevation 3: elevation 0, 2, 4-14, and groups of elevation-15 tiles with no elevation-3
  land beside them (all four bridges over water carry elevation 4: Route 119 by the Weather Institute and south of it
  (Route119 (21-23, 84-85), no surfer under it in either game), Route 120 by Fortree and south). hm_free.py
  `SurfStartTileType` (ITCM, after the landing hook) wraps CheckSurfHeightAllow's tile-under lookup and adds the solid
  flag on NOSURF: no surf prompt there. 168 tiles in Sapphire/Ruby's world, 169 in Emerald's (+5 Battle Frontier, +11
  Birth Island); nothing else in the collision changes. Safari Zone: heights.py's island rule (TERRAIN_HEIGHTS.md
  step 9): the pond is one level (24) with its shores at 32, the waterfall drops 32 into it.
- **Check**: `HOENN_VERSION=... python3 b2tools/surf_trap_check.py [WORLD] [--sim]`: Gen 3's movement (elevation and
  previous elevation, surf start and landing, bridges, ledges, waterfalls only downhill) and Black 2's (outdoor_check's
  rules) from every warp / door; a TRAP is a reachable state that reaches no warp again (no Fly, Teleport, Dive,
  Waterfall). Also lists surf starts one game allows and the other refuses. outdoor_check's walk models NOSURF and the
  Sapphire side's surf start (state elevation 3).
  | world | traps | surf starts B2 allows, Gen 3 refuses |
  |---|---|---|
  | v1.0.4-era (bridges' world_base, Sapphire) | 4 (Route 119 pocket, Route 120 x3) | 68 (bridge decks, Route 119 banks) |
  | v18.1 / E v1.2 (work/world, work/world_emerald) | 0 / 2 (Mossdeep north sea, Safari SE pond) | 10 / 21 |
  | after (bridge_surf worlds) | 0 / 0 | 2 / 2 (Route 134's elevation-3 water tiles at (367,354): Gen 3 walks onto them) |
- **Tests** [test] (DeSmuME, muted; work/agents/bridge_surf/tests/surf_test.py on test ROMs from main HEAD + this fix,
  HOENN_TEST_WARP=463,340,93 with the sign kit Groudon/Swampert/Balance Badge/HM03; other spots by clones of the ROM
  with the sign's warp rewritten; screenshots/bridge_surf/): Emerald and Sapphire: on Route 119's deck facing north and
  south and on its elevation-4 south bank, A gives no prompt; from the elevation-3 east shore (353,102) "The water is a
  deep blue..." -> surf, north under the deck (8 under it at 48) into the pocket, land on (344,90), surf again, back
  under the deck, land at (353,102) ((352,102) is a trainer's tile). Emerald: Mossdeep's north bank (742,164) and
  (750,166): no prompt; the same ROM with NOSURF cleared on those tiles (v1.2's collision) surfs off (742,164) into a
  45-tile pocket with no landing (the v1.2 trap, `emerald_mossdeep_repro_*`); Safari Zone southeast: surf off the upper
  river's bank, down the waterfall (carried 2 tiles to (125,83), 56 -> 24), across the pond, land on (124,92), walk on.
  Sapphire: Route 120's Fortree deck facing north and south: no prompt; surf off the strip's west end (425,73), south
  under the deck (40) to (424,79) and back, land on the strip. All 29 checks passed.
- Left as they are: Route 120's strip north of the Fortree bridge (Route120 (17-22,13), elevation 3, 64) stands 24 over
  the pond south of it (40): Gen 3 surfs south from it, Black 2 refuses; its west end surfs off as in Gen 3 (pre-dates
  the bridges work; no trap). Caves (their own collision, notes/CAVES.md) have no NOSURF. The Safari waterfall now
  drops 32 like Route 119's below the Weather Institute: the same grass/waterfall-streak layer pairs at its foot as the
  other waterfalls (outdoor_check layer; waterfalls are still flat sheets, "Open" above).

## Going down a waterfall needs a lower foot (artisan_surf, 2026-10-20) [code][test]
Found by frontier_sp: in Emerald, Artisan Cave B1F (Frontier West (39,55), our (55,68)) is reached only by surfing down
the falls south of the Battle Palace (Frontier East (34-53,64-66), our (106-125,77-79)); here the surfer stopped at
(114,78) facing the 0x40 row.
- **Cause** [code]: ov036 CheckAutoTileEvents (0x02182890) runs the descent (script 10015) only when the surfer's y is
  HIGHER than the tile 2 ahead (`ble` at 0x02182946; y = the player's own, FieldInteractWk_CalcPlayerFrontPos copies
  it). The whole Frontier is one level (land 16, every water 8), so the water above the falls and the foot stood level
  (8.00 / 8.00): no descent, no message. Same on Route 119 north of the Weather Institute bridge (345-347,88), all
  versions.
- **Fix** (water.py `_fall_foot`): the surf water right below a 0x40 row, when level (within 1 unit) with the water above
  the row, gets the highest flat collision height under it: 7.85 for 8.00 (0.16 units; drawing unchanged).
  Collision diff against main's world: only those 23 tiles (Frontier East 20, Route 119 3), class and flags as before.
- **Check**: work/agents/artisan_surf/tools/fall_sweep.py WORLD lists every 0x40 tile with the heights above / at the foot.
  Emerald after: Frontier, Route 119, Safari SE (56 -> 24, bridge_surf) go down. Not going down (foot higher than the
  top; climbed with Waterfall, going down never needed): Ever Grande (823-834,307) -24 / -8, Route 114 by Meteor Falls
  (97-100,72) -8 / 24. surf_trap_check 0 traps; outdoor_check size 0.
- **Test** (DeSmuME, muted; post-game sign kit, screenshots/artisan_surf/): land east of the falls (127,75) -> surf off
  (126,75) -> (114,78) -> down the falls to (114,80) (y 8.00 -> 7.85) -> surf west to (55,72) -> land (55,71) -> walk
  into the mouth (55,68) -> Artisan Cave B1F (zone 373) at (8,48) -> walked to (10,46). All 8 checks passed.
