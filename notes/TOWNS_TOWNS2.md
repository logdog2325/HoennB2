# Town buildings, group towns2: Slateport, Mauville, Verdanturf (2026-10-06)

Decision 2026-10-05/06: Gen 3 shapes in Gen 5 art. Built like Littleroot/Oldale (`b2tools/buildings.py` boxes and
roofs tiled with regions of Black 2 building textures, Sapphire footprints and colours). Res range 340-359; used
340-353 (14 models, the group's limit). Tags: [code] = decomp, [bytes] = read from the dump, [test] = DeSmuME on
`work/agents/towns2/rom/hoenn.nds`.

## Build and test
    cd b2tools
    for T in slateport mauville verdanturf; do python3 models_$T.py ../work/buildings/$T; done
    # every DAE -> NSBMD (as rebuild_slice.sh does for the slice), from the repo root:
    java -Djava.awt.headless=true -cp "work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar" \
         ToNsbmd work/buildings/$T/<model>.dae work/buildings/$T/<model>.nsbmd work/buildings/$T/palettes.txt
    HOENN_AGENT=towns2 HOENN_TOWN_GROUPS=towns2,towns1,towns3 zsh b2tools/agent_build.sh
(`work/agents/towns2/build_models.sh` runs the first two steps; scratch.) Geometry helpers shared by the three
scripts live in `models_slateport.py` (whole textures repeated by the GPU as one polygon per face, no north-facing
faces, to keep the pack small). Registry: `data/buildings/towns2.json`; placement: `data/towns/<Map>.json`.

Placement: `buildings` (Sapphire door destination -> res, front 20) where `converter/plan_map.py` found a footprint;
`props` (model origin in map tile coordinates) where it did not: the door tile is walkable in Sapphire (Fan Club,
Museum, Shipyard, Harbor, Game Corner) or two buildings share one plan footprint (Slateport house 2 = house + annex,
Mauville house 2 + Mart, Verdanturf Mart + Center). Every front wall sits 4 units into the door tile, as Black 2
places its buildings (notes/OLDALE.md). Collision is Sapphire's (world.py: building, door, sign tiles solid; roof
rows walkable = Sapphire's walk-behind rows). Door models: the record's door res at origin + (dx, dz); Black 2's
`door_normal01-03` (259-261) span x -17..1, y 6..32, `door_pc` (93) x -13.2..13.2 [bytes: apicula on pack 0], so
dx = door tile centre - footprint centre + 8 for 259-261 and + 0 for 93.

## Buildings (map tile coordinates; rows = Sapphire's solid rows, + roof = walk-behind row above)
### Slateport City (40x60, world origin (248, 320))
| Building | Sapphire footprint, door | Placed as | Res | Model and textures |
|---|---|---|---|---|
| Contest Hall | x 8-12, rows 8-12, door (10,12) | plan | 362 | group towns3's Gen 3 hall |
| Name Rater's house | x 4-7, rows 17-19 + roof, door (5,19) | plan | 340 | `house`: purple gable roof `c13_ho01b` (pack 54), yellow siding `wbase_a` (pack 6), posts/window `c14_h1_body` |
| Pokémon Center | x 18-21, rows 17-19 + roof, door (19,19) | plan | 0 | shared (slice) |
| Poké Mart | x 12-15, rows 24-26 + roof, door (13,26) | plan | 3 | shared (slice) |
| Pokémon Fan Club | x 2-6, rows 23-26 + roof, door (4,26) | prop (4.5, 25) | 342 | `fanclub`: chamfered box, gold striped roof ring and porch `wbase_a`, beige walls/top `t06_h_03_a`, posts `c14_h1_body`, base `gate_1` |
| Oceanic Museum | x 28-33, rows 23-26, doors (30,26) (31,26) | prop (31, 25) | 343 | `museum`: green ribbed walls `d5_conte01a`, mint flat roof `d5_conte01b` (pack 8), plinth `c4_bp01` (pack 6), skylights/crest `pc_win1`; door 93 |
| Stern's Shipyard | x 24-31, rows 33-38 + roof, door (26,38); dock frames x 32-33, legs on rows 35 and 38 | prop (28, 37) | 344 | `shipyard`: plank walls `c14_h1_body`, panel roof `c4_bp01`, vents `r4_b03_yane01`, frames |
| Harbor | x 25-31, rows 7-12, door (28,12) | prop (28.5, 11) | 345 | `harbor`: pale blue panels `c4_bp01`, orange ribbed roof `t06_h_03_a` |
| House 2 | x 20-29, rows 42-44 + roof, door (21,44) | props (22, 43) + (27, 43) | 340 + 341 | `house` + `annex` (6 wide, two windows, no door) |
| Market canopies (2) | canopy rows 7-8 / 30-31 (walkable), posts (16,9) (20,9) / (8,32) (12,32) | props (18.5, 9), (10.5, 32) | 346 | `awning`: orange tiles `yane_001` (pack 0) on two posts |
| Market stalls (6) | awning rows (walkable) over a post/wares row: posts x 2/6 and 10/13, rows 43, 47, 51 | props (4.5 / 12, 43 / 47 / 51) | 347 | `stall`: olive roof `c4m_yane_001` on two front posts; since 2026-10-07 a low roof (eaves 13, ridge 20) over the awning rows only, so the sellers in the post row and people in the aisle row above stay drawn (npc_limit: camera-facing people at 52.6 degrees, notes/NPC_LIMIT.md) |

### Mauville City (40x20, world origin (248, 200))
| Building | Sapphire footprint, door | Placed as | Res | Model and textures |
|---|---|---|---|---|
| Gym | x 5-10, rows 2-5 + roof, door (8,5) | plan, front 24 | 320 | group towns1's generic Gym (same metatiles as Petalburg's) |
| Pokémon Center | x 21-24, rows 2-5, door (22,5) | plan | 0 | shared |
| Rydel's Cycles | x 34-38, rows 2-5, door (35,5) | plan | 348 | `bikeshop`: pink roof `h2` (pack 9), yellow siding `wbase_a`, posts |
| Game Corner | x 5-11, rows 11-13 + roof, door (8,13) | prop (8.5, 12) | 349 | `gamecorner`: pink barrel roof `h2` with two rows of windows, glass front `pc_win1`, pink porch; door 93 |
| House 2 | x 18-21, rows 12-14 + roof, door (19,14) | prop (20, 13) | 351 | `house`: pink roof, yellow siding |
| Poké Mart | x 22-25, rows 12-14 + roof, door (23,14) | prop (24, 13) | 3 | shared |
| House 1 + annex | x 31-35 rows 12-14 / annex x 36-39 rows 12-15, + roof, door (32,14) | plan | 350 | `house1`: grey walls `gate_1`, pink roof; annex yellow siding, flat grey roof with vents `r4_b03_yane01` |

### Verdanturf Town (20x20, world origin (168, 200))
| Building | Sapphire footprint, door | Placed as | Res | Model and textures |
|---|---|---|---|---|
| Poké Mart | x 11-14, rows 0-3, door (12,3) | prop (13, 2) | 3 | shared |
| Pokémon Center | x 15-18, rows 0-3, door (16,3) | prop (17, 2) | 0 | shared |
| Contest Hall | x 2-6, rows 3-7, door (4,7) | plan | 362 | group towns3 |
| Friendship Rater's house | x 0-3, rows 12-14 + roof, door (1,14) | plan | 352 | `house`: flat mint roof slab `d5_conte01b`, yellow fascia `wbase_a`, beige walls `t06_h_03_a`, pillars |
| Wanda's house | x 8-12, rows 12-14 + roof, door (10,14) | plan | 353 | `wanda`: same build, 5 wide, door in the middle |
| House (east) | x 16-19, rows 13-15 + roof, door (17,15) | plan | 352 | as the Friendship Rater's |

## Budget (measured)
- Models: 14 (340-353), 58,944 B of NSBMD (2.2-6.4 KB each, 22-112 triangles).
- Textures new to pack 0's set (scratch merge with `nsbtx.merge`, same as `area2_buildings`): `c13_ho01b` +2,116 B,
  `d5_conte01a` +1,108, `h2` +596, `c4_bp01` +596 (0 when towns3 is in, it uses it too), `wbase_a` +596,
  `d5_conte01b` +324: **+5,336 B** (set 73,952 -> 79,288 B over the slice). Everything else comes from pack 0
  (`h_kage`, `h_mado`, `gate_1`, `pc_win1`, `yane_001`) or the slice (`t06_h_03_a`, `c14_h1_body`, `c4m_yane_001`,
  `r4_b03_yane01`). Palettes: `<texture>_pl`, as the game's own models pair them (`work/tex/palNN.txt`).
- Placements: at most 11 per cell in my towns' cells = 18 prop slots with their doors (limit 32,
  notes/TERRAIN_GROUND.md).

## Pack 0 size: the field heap is the real limit (for the lead)
The whole pack is read into the field heap (`FieldPropSystem_LoadResBundle` -> `GFL_ArcToolReadHeapNew(arc, fileId,
system->heapId)`, external/pokebw2/src/ov036/field_buildmodel.c:255-266) [code]. Tests from the after_mom2
savestate through the test door, same world:

| Groups in pack 0 | Models | Pack 0 bytes | Result [test] |
|---|---|---|---|
| slice + towns2 + towns3 (+ ground module) | 67 | 284,240 | loads |
| slice + towns2 + towns1 (towns1 at 102 KB then) | 73 | 325,080 | loads |
| all four groups (towns1 at 102 KB then) | 79 | 375,648 | **black screen** after the warp (1,000 frames) |
| all four groups (current registries) | 81 | 344,056 | loads |

So today's total fits with ~30 KB to spare at most, and Lilycove/Mossdeep/Sootopolis/Pacifidlog/Ever Grande still
need buildings. The limit is free field-heap space, so it also moves with everything else on that heap (not
measured). Room to gain: 71,668 B of the original pack-0 models are neither replaced nor referenced by any registry
(door, sign 151-154, parasol 26, default model 0x15 = `rock_01`, which must stay): Route 1's seasonal trees
`r01_*` (295-302, 40.5 KB), `outwarp01-03` (8.4 KB), `gate_01`, `fountain_01`, `thouse_01`, `cart_01`,
`out_vender01`, `out_dust01`, `o_table/chair_01`, `plant_01`, `t01_kira`, `door_t2_b`, `c0101`, `searock_01/02`,
`rock_02` [bytes]. Hoenn's chunks place only registry models and sign models (`world.py` `put()` calls), plus ground's
parasol 26 once its placements hook is in; dropping the rest from pack 0 would roughly triple the headroom.

## Conflict with the ground module (for the lead)
`other:market_awning` occurs only in Slateport (90 tiles) and ground draws plank canopies on them; ground also puts a
stone plinth on every `prop` tile, including the shipyard's dock frames. With both enabled, the plank canopies stand
round towns2's stalls and canopies and the plinths round the frames (`screenshots/towns2/conflict_ground.png`)
[test]. Suggested: ground skips `other:market_awning` and the prop tiles a town model covers (towns2's models carry
Sapphire's colours: green stall roofs, orange canopies), or towns2's res 346/347 are dropped.

## Proofs
`screenshots/towns2/slateport.png`, `mauville.png`, `verdanturf.png`: emulator views next to Sapphire's map render
(mauville with towns1 for the Gym, the others with towns3 for the Contest Halls; the whole pack is too big for one
build with everything plus more towns, see above). Reached through a scratch patch that moves the test door's
arrival (`work/agents/towns2/test_arrive.py`, `HOENN_ARRIVE`); from Verdanturf `emu.travel` walks on to Mauville and
Slateport (all reachable on foot with the current placeholders).

## Not done / open
- Warps and interiors (O4), signs/NPCs: not part of this task (doors are solid tiles without warps).
- Door-less details not modelled: the boats at the shipyard (in water); Mauville's bike racks in front of the Center
  (prop tiles x 26-28 / 30-32, rows 3-4). Ground draws its plinth there when enabled. Slateport's statue in the south
  plaza (prop tiles x 32-33, rows 52-54) is res 354 since 2026-10-08 (buildings_audit: `models_slateport.statue`, a
  white six-sided tiered lantern 43 high, 4,368 B; data/towns/SlateportCity.json prop (33.0, 54.0) with 'covers').
- Shipyard roof is pale blue panels (Sapphire: grey); door styles are Black 2's (`door_normal`, `door_pc`).
- The Gym (320) and Contest Hall (362) are the other groups' models; without towns1/towns3 those spots draw the
  default model 0x15 (`field_buildmodel.c:277-306`, RESEARCH_WORLD.md).
