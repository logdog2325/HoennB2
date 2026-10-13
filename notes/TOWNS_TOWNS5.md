# Town buildings, group towns5: Ever Grande City and the buildings on routes (2026-10-06)

Decision 2026-10-05/06: Gen 3 shapes in Gen 5 art. Built like Littleroot/Oldale and groups towns1-3: Python boxes and
roofs (`b2tools/buildings.py`, helpers from `models_slateport.py`) tiled with regions of Black 2 building textures,
Sapphire footprints and colours. Res range 400-419; used **400-413 (14 models)**. Tags: [code] = file:line,
[bytes] = read from the dump / our files, [test] = DeSmuME on `work/agents/towns5/rom/hoenn.nds`.

## Files
| File | What |
|---|---|
| `b2tools/models_routes.py` | route buildings, res 400-408, 410-413 -> `work/buildings/routes/*.dae` |
| `b2tools/models_evergrande.py` | Pokemon League, res 409 -> `work/buildings/evergrande/league.dae` |
| `data/buildings/towns5.json` | pack-0 records (res, model, door res/dx/dz) + 10 textures |
| `data/towns/EverGrandeCity.json`, `Route104/109/110/111/112/113/114/116/117/118/119/121/123/124.json` | placement (group `towns5`) |
| `screenshots/towns5/*.png` | proofs: Sapphire (left) next to the test ROM (right), one pair per building |

Rebuild the models (DAE, then NSBMD with the palettes file written next to them):

    cd b2tools && python3 models_routes.py ../work/buildings/routes && python3 models_evergrande.py ../work/buildings/evergrande
    for B in work/buildings/routes work/buildings/evergrande; do for d in $B/*.dae; do
      java -Djava.awt.headless=true -cp "work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar" \
        ToNsbmd $d ${d%.dae}.nsbmd $B/palettes.txt; done; done          # (from the repo root)
    HOENN_AGENT=towns5 HOENN_TOWN_GROUPS=towns5,towns1,towns3 zsh b2tools/agent_build.sh

**towns5 needs towns1 and towns3 enabled too**: 7 route houses are towns1's res 321/322 and one is towns3's res 360
(below); without those groups the game draws its default model 0x15 there (notes/RESEARCH_WORLD.md).

## Which buildings (every door warp on the route maps and Ever Grande, `external/pokeruby/data/maps/*/map.json`)
Not buildings (left to terrain/caves): Petalburg Woods' forest gaps (Route 104), New Mauville's rock entrance
(Route 110), Desert Ruins, Fiery Path, Jagged Pass, Meteor Falls, Rusturf Tunnel, Island Cave, Granite Cave,
Abandoned Ship, Shoal Cave, Mt. Pyre, Sky Pillar, Ancient Tomb, Scorched Slab, Victory Road (cave mouths, checked on
Sapphire renders). Sootopolis is skipped (standalone map, not built yet).

### Reused models (same Sapphire metatiles as the town that made them) [bytes: plan `metatiles`]
| Building | Sapphire footprint, door | Metatiles | Res |
|---|---|---|---|
| Route 111 old lady's rest stop | x 25-28, rows 15-18, door (26,18) | 008-00a / 010-012 / 018 019 00b 01a / 020 021 013 022 = Petalburg House 1/2 | 322 (towns1) |
| Route 117 Pokemon Day Care | x 50-53, rows 3-5 + roof row, door (51,5) | same | 322 |
| Route 119 house | x 32-35, rows 106-109, door (33,109) | same | 322 |
| Route 123 Berry Master's house | x 21-24, rows 4-6 + roof row, door (22,6) | same | 322 |
| Route 124 Diving Treasure Hunter's house | x 69-72, rows 46-48 + roof row, door (70,48) | same, Mossdeep corner posts (2e0/2e1/2e8/2e9) | 322 |
| Route 114 Lanette's house | x 25-29, rows 34-36 + roof row, door (27,36) | 008-00a.. / 018 00b 019 00b 01a = Wally's house (5 wide) | 321 (towns1) |
| Route 116 Tunneler's rest house | x 36-40, rows 5-8, door (38,8) | same | 321 |
| Route 114 Fossil Maniac's house | x 28-31, rows 2-5, door (29,5) | 285-287 / 28d 29d 29e 28f / 295 2a5 2a6 297 = Fallarbor House 1/2 (only the top roof row differs: 344-346) | 360 (towns3) |
| Ever Grande Pokemon Center | x 26-29, rows 46-48 + roof row, door (27,48) | 048-063 | 0 (slice) |

### New models
| Res | Building (map) | Sapphire footprint, door | Placed as | Model and textures | Door res / dx |
|---|---|---|---|---|---|
| 400 | Mr. Briney's cottage (Route 104) | x 15-19, rows 48-50 + roof row 47, door (17,50) | prop (17.5, 49.0) | brown thatched gable roof `c14_h1_body` planks, cream ridge `c14_h2_yane`, blue band with a white edge hanging from the eave `r4_b03_yane01`, straw-screen walls (`wbase_a` stripes turned upright), dark posts | 260 / 8 |
| 401 | Pretty Petal flower shop (Route 104) | x 3-8, rows 15-18, door (5,18) | prop (6.0, 17.0) | green siding `rr_misel1_02`, salmon tiled roof `yane_001` with a red eave band `t06_h_03_a`, pink-and-white striped awning (`h2` / `r4_b03_yane01` stripes) over the door and window, windows with flower boxes `plant_tex4` | 260 / 0 |
| 402 | Seashore House (Route 109) | x 10-14, rows 3-5 + roof row 2, door (12,5) | prop (12.5, 4.0) | purple roof `c13_ho01b` with a light ridge band, orange plank walls `c14_h2_kabe`, posts, a window either side | 260 / 8 |
| 403 | Seaside Cycling Road north + south entrance (Route 110) | north x 14-19 rows 12-16, doors (15,16) (18,16); south x 15-20 rows 84/85-88, doors (16,88) (19,88) | plan (both) | yellow brick `wbase_a` on a red base, flat grey roof rim `gate_1` round a grid of pale panels `c4_bp01` (towns2 made Mauville's annex, the same Sapphire metatiles 27e-2b7, this way), two windows | 261 / -16 (west door); east door = res 261 prop at (19.0, 16.25) / (20.0, 88.25) |
| 404 | Trick House (Route 110) | x 9-13, rows 61-66, door (11,66) | plan | grey walls `gate_1` with gold ornament panels (`wbase_a` upright), windows, wide pink skirt roof `h2`, narrower grey upper floor with a pink gable roof | 261 / 8 |
| 405 | Winstrate family's house (Route 111) | x 11-15, rows 110-113 + roof row, door (13,113) | plan | as 403, 5 wide, one door | 261 / 8 |
| 406 | Cable car station (Route 112) | x 27-30 + east wing x 31-32, rows 23-27, doors (28,27) (29,27); pylon on prop tiles x 24, rows 24-26 | prop (29.0, 26.0) | white walls `r4_b03_yane01`, beige lintel, orange ribbed gable roof `t06_h_03_a`, lower east wing with a roof sloping down to the east, blue pylon 4.5 tiles west with its cables | 261 / 0; second door = res 261 prop at (30.0, 27.25) |
| 407 | Weather Institute (Route 119) | x 1-11, rows 26-32, door (6,32) | prop (6.5, 31.0) | two-storey glass body with rounded ends `c4_bp01`, white band, beige fascia and ribbed roof `t06_h_03_a`, two round turrets with dark tops, entrance porch: grey frame `gate_1` with glass `pc_win1` under a beige canopy on four grey columns | 261 / 8 |
| 408 | Safari Zone entrance (Route 121) | x 35-39, rows 0-5, door (37,5) | plan | grey walls `gate_1`, two windows, flat beige roof in a grey rim, canopy over the door, planting `plant_tex4` either side | 93 / 0 |
| 409 | Pokemon League (Ever Grande) | x 13-23, rows 0-5, door (18,5) | plan | 72-unit block `t2_buil1` (window rows over orange brick, glass `h_mado` 1 unit behind the window holes), cream end towers standing forward `t06_h_03_a`, porch: four grey columns, curved cream canopy with the Poke Ball emblem `pc_win1` | 93 / 0 |
| 410 | Glass workshop (Route 113) | x 32-35, rows 2-5, door (33,5) | plan | towns3's Fallarbor house (olive siding, window with an orange awning; `models_fallarbor` regions and window) under Sapphire's ash-covered roof: grey-tan shingles `c14_h2_yane`. Same metatile family as Fallarbor (2de-30f, Fallarbor tileset) but an ash-grey roof, hence its own model | 236 / 0 |
| 411 | Route 118 door-less house (buildings_audit, 2026-10-08) | x 0-3, rows 15-17 + roof row 14, no door (Mauville tileset 0x283-0x29d) | prop (2.0, 16.0), data/towns/Route118.json | Mauville house 2's build (towns2 res 351): pink gable roof `h2`, gold siding `wbase_a`, a window in column 2, posts at columns 0 and 3; it stood invisible (solid tiles, grass drawn) | none |
| 412 | Route 112 cable car pylon (buildings_audit, 2026-10-08) | prop tiles x 12, rows 19-21 | prop (12.5, 21.375), covers | tapered blue mast 140 high, beam, cable east to the station's pylon (res 406's mast now reaches its ground, 80 under the station) | none |
| 413 | Route 112 cable car pylon | prop tiles x 4, rows 15-17 | prop (4.5, 17.375), covers | mast 102 high on the 48-high ground, cable east to 412's and west off the map | none |

Props are the buildings plan_map.py finds no footprint for: their door tiles are walkable in Sapphire (Briney, flower
shop, Seashore House, cable car, Weather Institute; plan rows show the door as walkable `door`), so the warp is not
inside the solid component `converter/plan_map.py:47,60-61` [code]. Prop origin = footprint centre x, door row +
(4 - 20)/16 (the same spot world.py computes for plan buildings, `b2tools/world.py:230-235` [code]).

## Placement and collision
- Front wall 4 units into the door tile (front 20) as Black 2 places buildings (notes/OLDALE.md); walls >= 34 high
  so door models (259-261 span y 6..32, notes/TOWNS_TOWNS2.md) stand under them.
- Door dx: door tile centre − footprint centre + 8 for 236/259-261, + 0 for 93 (notes/TOWNS_TOWNS3.md).
- **Second doors** (Cycling Road gates, cable car): the record draws one door, the other door tile gets the door
  model itself as a prop (origin = door tile centre + 8 units, z = door row + 0.25). Black 2 does this too: retail
  chunks 856 (res 164, 165), 860, 1025, 1048, 1054 (res 93) place door models directly [bytes: chunk placements vs
  door-type records of all exterior packs]. Both doors show in the test [test: routes_104_109_110.png, 111_to_117].
- Collision is Sapphire's, from the plans (world.py: building/door/sign tiles solid, walk-behind roof rows walkable)
  [code] `b2tools/world.py:175`; nothing is added. Checked in the built grids: Briney rows 288-290 x 63-67 solid, roof
  row 287 walkable, door (65,290) solid; cable car front row x 235-240 solid incl. both doors [bytes: chunk.json].

## Budget
- Models: 11 new (400-410), 51,536 B of NSBMD: league 5,616 (95 triangles), briney 4,080 (62), cablecar 4,464 (68),
  flowershop 5,744 (72), gate 3,952 (40), glassworks 3,856 (44), safari 4,112 (64), seashore 4,016 (50), trickhouse
  4,240 (54), weather 7,504 (140), winstrate 3,952 (40). Measured cost per model: ~700 B + ~300 B per texture
  (material) + ~30 B per triangle [test: ToNsbmd on scratch models], so faces use whole repeating textures or
  stretched regions instead of cutting atlases per repeat, and no north-facing walls (models_slateport helpers).
- Textures: **+0 B** over towns1-3 (every texture is pack 0's own, the slice's, or one towns1-3 already merge);
  +8,168 B if towns5 is enabled with the slice only (78,948 -> 87,116 B) [test: nsbtx.merge as area2_buildings].
  Texture set with slice + towns1 + towns3 + towns5: 96,460 B (patch output).
- Pack 0 grows by 52,020 B with towns5 (slice 174,304 -> 226,324 B) [bytes: area2_buildings' container build].

## Pack 0 and the field heap (for the lead)
The whole pack is read into the field heap (towns2 found the limit, notes/TOWNS_TOWNS2.md). Tests here, from
after_mom2 through the test door to Route 104:

| Groups in pack 0 | Models | Pack 0 bytes | Result [test] |
|---|---|---|---|
| slice + towns5 + towns1 + towns3 | 78 | 336,516 | loads (all proofs) |
| slice + towns5 + towns1 + towns2 + towns3 | 92 | 396,076 | **black screen** (still black 900 frames later) |
| slice + towns1-5 | 103 | 464,992 | black screen |

With towns2's results (344,056 loads, 375,648 black) the limit is between those two, so **all groups together do not
fit**: towns1-5 need ~465 KB before towns6+ and the standalone maps. Something has to give at the lead's level:
drop the retail pack-0 models no registry uses (~72 KB, listed in notes/TOWNS_TOWNS2.md), split the overworld into
more than one area/pack (warp-joined, like Unova's gates), and/or trim models further (the per-texture cost above
suggests merging small textures into fewer materials).

## Testing
Scratch test patch `work/agents/towns5/test_arrive.py` (copy of towns3's: moves the test door's arrival to
`HOENN_ARRIVE`), then `walk.py ROM work/emu/after_mom2.dst OUT.png D1 L3 D1 D1 L1 D1 L1 D1 W400 C<X>,<Z> W30 S`,
standing one tile south of each door (world tile = map tile + layout position + 32). Arrivals used: Briney (65,291),
flower shop (53,259), Seashore (260,386), gates (264,237) / (266,309), Trick House (259,287), rest stop (274,79),
Winstrate (261,174), cable car (237,108), glass workshop (181,66), Fossil Maniac (117,66), Lanette (115,97),
Tunneler (126,189), Day Care (239,206), Weather Institute (334,93), Route 119 house (361,170), Safari (485,146),
Berry Master (390,207), Route 124 (678,169), League (826,246), Ever Grande Center (835,289). Every building was
reachable this way with water/cliffs as placeholders. Proof sheets (Sapphire's map, same 16x12-tile framing, next to
the emulator's top screen): `screenshots/towns5/routes_104_109_110.png`, `routes_111_to_117.png`,
`routes_119_to_124_evergrande.png`. Gen 5's camera cuts the tops of tall buildings (Trick House upper roof,
League, Weather Institute turrets) from one tile away; the models were also checked from further back with
`b2tools/preview_interior.py`'s rasteriser (scratch).

## Open
- Warps, interiors, NPCs, sign scripts: later work (doors are solid tiles without warps).
- Colours that differ from Sapphire: League walls are brick-brown (`t2_buil1`) where Sapphire is orange; gate and
  Winstrate walls read gold-brown in game (Sapphire: lemon yellow); door models are Black 2's (no pink doors);
  Safari/League doors are Black 2's Pokemon Center sliding door (93) with its crest.
- Not modelled: Route 109's beach umbrellas and deck chairs, the Cycling Road itself (`bike_path`), fences, Ever
  Grande's stone walls and round bushes: terrain classes for the ground module. The ground module draws a plinth on
  every `prop` tile (notes/TOWNS_TOWNS2.md); the cable car pylon stands on Route 112's prop tiles x 24, rows 24-26,
  so with ground enabled a plinth would appear under it.
- Placement height: props and buildings are lifted by world.py's height field when the heights module is on
  (Route 112's station stands on a cliff top in Sapphire); only tested flat (no terrain modules).
