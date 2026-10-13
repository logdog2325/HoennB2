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
Our water is 8 below the land, like all of Black 2's (below).

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
