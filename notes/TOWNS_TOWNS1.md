# Town buildings, group towns1: Petalburg, Rustboro, Dewford (2026-10-06)

Gen 3 shapes, Gen 5 art (decision 2026-10-05/06): Python-generated boxes/roofs (`b2tools/buildings.py`) sized to
Sapphire's footprints (`data/plans/<Map>.json`), tiled with regions of Black 2 building textures. Res range 320-339;
res 320 is the **generic Gym** used by every Hoenn town.

## Files
| File | What |
|---|---|
| `b2tools/models_petalburg.py` | `gym` (res 320), `wally` (321), `house` (322); helpers `wface/wslope/wgable/whip` (whole wrapped texture, one polygon per face), `UW` (stretch a region along u) |
| `b2tools/models_rustboro.py` | `grey5` 323, `flat1` 324, `school` 325, `cutter` 326, `house3` 327, `flat2` 328, `devon` 329, `annex` 332, `lamp` 333 |
| `b2tools/models_dewford.py` | `hall` 330, `house` 331 |
| `work/buildings/{petalburg,rustboro,dewford}/` | DAEs, NSBMDs, texture PNGs, palettes.txt, textures.txt |
| `data/buildings/towns1.json` | pack-0 records (res, model, door res, dx, dz) + 6 textures |
| `data/towns/{PetalburgCity,RustboroCity,DewfordTown}.json` | `group: towns1`, buildings by Sapphire door dest, props (Rustboro only) |

Rebuild models: `cd b2tools && python3 models_<town>.py ../work/buildings/<town>`, then per DAE
`java -cp "work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar" ToNsbmd X.dae X.nsbmd work/buildings/<town>/palettes.txt`.
Test: `HOENN_AGENT=towns1 HOENN_TOWN_GROUPS=towns1 HOENN_TEST_NO_WILD=1 zsh b2tools/agent_build.sh`.
Enable for normal builds: add `"towns1"` to `data/buildings/enabled.json`.

## Buildings (Sapphire footprint in map tiles, inclusive; "+ roof row" = walk-behind row above it)
| Town / building | Footprint, door | Res | Door record | front |
|---|---|---|---|---|
| Petalburg Wally's house | 5x4 (5,2)-(9,5), door (7,5) | 321 | 260 dx 8 dz 20 | 20 |
| Petalburg Gym | 6x5 (12,4)-(17,8), door (15,8) | 320 | 93 dx 8 dz 24 | 24 |
| Petalburg Mart | 4x4 (24,9)-(27,12), door (25,12) | 3 (slice) | 93 dx -8 dz 20 | 20 |
| Petalburg Pokémon Center | 4x3 (19,14)-(22,16) + roof row, door (20,16) | 0 (slice) | 93 dx -8 dz 20 | 20 |
| Petalburg House 1 | 4x3 (9,17)-(12,19) + roof row, door (10,19) | 322 | 260 dx 0 dz 20 | 20 |
| Petalburg House 2 | 4x4 (19,21)-(22,24), door (20,24) | 322 | 260 dx 0 dz 20 | 20 |
| Rustboro Gym | 6x5 (24,15)-(29,19), door (27,19) | 320 | 93 dx 8 dz 24 | 24 |
| Rustboro House 1 / House 2 | 5x4 (31,16)-(35,19) / (28,25)-(32,28) + roof row, door col 2 | 323 | 261 dx 8 dz 20 | 20 |
| Rustboro Flat 1 | 9x5 (9,26)-(17,30) + roof row, door (13,30) | 324 | 261 dx 8 dz 20 | 20 |
| Rustboro Trainer's School | 7x5 (24,30)-(30,34), door (27,34) | 325 | 261 dx 8 dz 20 | 20 |
| Rustboro Cutter's house | 5x4 (7,35)-(11,38) + roof row, door (9,38) | 326 | 261 dx 8 dz 20 | 20 |
| Rustboro Pokémon Center / Mart | 4x3 (15,36)-(18,38) / (15,43)-(18,45) + roof row | 0 / 3 (slice) | 93 dx -8 dz 20 | 20 |
| Rustboro House 3 | 6x4 (24,43)-(29,46) + roof row, door (26,46) | 327 | 261 dx 0 dz 20 | 20 |
| Rustboro Flat 2 | 7x8 (3,44)-(9,51) + roof row, door (5,51) | 328 | 261 dx -8 dz 20 | 20 |
| Rustboro Devon Corp. (prop) | wings x 7-16 rows 7-14, tower x 10-13 to row 15; doors (11,15),(12,15) | 329 | 93 dx 0 dz 4 | prop x 12.0 z 15.0 |
| Rustboro grey block east of the fountain (prop, no door) | 4x7 (31,40)-(34,46) + roof row 39 | 332 | none | prop x 33.0 z 45.0 |
| Rustboro street lamps (18, props) | lower tile of each 2-tile Sapphire lamp | 333 | none | props |
| Rustboro fountain (prop) | 3x3 (27,38)-(29,40) | 24 (Black 2's pack-0 `fountain_01`) | none | prop x 28.5 z 39.5 |
| Dewford Hall | 5x4 (1,0)-(5,3), door (3,3) | 330 | 236 dx 8 dz 20 | 20 |
| Dewford House 2 / House 1 | 4x4 (7,5)-(10,8) / 4x3 (16,12)-(19,14) + roof row, door col 1 | 331 | 236 dx 0 dz 20 | 20 |
| Dewford Pokémon Center | 4x3 (1,8)-(4,10) + roof row, door (2,10) | 0 (slice) | 93 dx -8 dz 20 | 20 |
| Dewford Gym | 6x4 (5,14)-(10,17) + roof row, door (8,17) | 320 | 93 dx 8 dz 24 | 24 |

Devon has no plan footprint (`plan_map.py` finds none: its door tiles are walkable in Sapphire), so it and the
door-less grey block are props placed with their front wall 4 units into their bottom row, like every other building.
Collision is Sapphire's for everything (from the plan: building/door/prop tiles solid), not from the models.

**Generic Gym (res 320)**: every Sapphire Gym exterior is 6 tiles wide with the door in column 3 (all 8 plans checked
[code] `data/plans/*.json`), so one model fits all: place with `"front": 24` (porch front 4 units into the door row);
the record draws Black 2's sliding door (93) at dx 8. Depth covers 5 rows (also 4 rows + a walk-behind roof row).
Look: Sapphire's tan roof (low hip), white walls with blue bands and a window band, Poké Ball crest and sign board on
the left, glass-sided entrance porch.

## Textures
New in pack 0's building set (merged byte for byte by `patches/area2_buildings.py`), **+6,104 B** over the slice's set
[test: `nsbtx.merge` of slice vs slice+towns1, 78,948 → 85,052 B]:

| Texture | Set | Used for |
|---|---|---|
| `sand_tex001` 32×32 | ext01 (Striaton) | Gym roof, Rustboro flat roofs (whole texture, WRAP) |
| `c1sch001` 64×64 | ext01 | Rustboro tan stone walls, cornice, brick frieze (Flat 1, School, Cutter's, House 3, Devon) |
| `bill_kabe` 32×32 | ext09 (Mistralton) | grey walls (Rustboro grey houses, flats, vents, lamp base) |
| `c8w_001` 32×32 | ext12 (Opelucid) | dark windows with a light sill, black trim |
| `t06_h_01_a` 64×64 | ext53 (Floccesy) | Petalburg houses: red-orange roof tiles, cream ridge band, cream walls |
| `nsyane` 16×32 | ext54 (Virbank) | Dewford's blue roof tiles. **Name clash**: ext01/ext59 hold a red `nsyane` [bytes: mean colour (209,21,0) vs ext54 (79,87,183)]; the first group merged wins, so no other group may add the red one |

Reused from the slice/pack 0: `r4_b03_yane01` (white wall, blue bands, corrugated stripes, gym windows/sign board),
`pc_win1` (crest, glass), `c14_h1_body` (posts, beams, framed windows, Dewford plaster), `h_mado`, `h_kage`.

## Budget
14 models (res 320-333), 59,200 B of NSBMD in pack 0 (was 103 KB in the first pass: regions that are uniform along the
wall are now stretched instead of repeated, and whole textures are drawn as single WRAP polygons: 2,470 triangles for
the first 13 models → 1,044 for all 14 now). Pack 0: 61 models with slice + towns1 (agent build). Note: pack 0 grows with every group; the largest
retail exterior pack is 223,356 B and the field heap headroom is still unmeasured (RESEARCH_WORLD.md §1).

## Findings
- **Door model offsets** [bytes + test]: door models 164, 165, 236, 259, 260, 261 span x −18..2 around their origin
  (apicula export of pack 0), so the game draws their centre at the building origin + dx − 8; the Pokémon Center door
  93 spans −13.2..13.2 (centred). Black 2's own records agree (e.g. `sodateya_01` 259 dx 8, `t06_house_01` 259 dx 16).
  So **dx = door tile centre − footprint centre + 8** for those doors (+0 for 93). Verified in the emulator: towns1's
  doors sit centred over the player standing at door+1 (`screenshots/towns1/door_offsets.png`, bottom row).
  **The slice's records are half a tile off**: Littleroot `house_l`/`house_r`/`lab` (164/165, dx 16/−16/16) and Oldale's
  `house` (236, dx −8) draw the door ~8 units left of the door tile (same image, top row). Fix (slice.json, lead):
  house_l dx 24, house_r dx −8, lab dx 24, Oldale house dx 0.
- Sign models now come from `data/hoenn_content.json` (`model` 152/154 on generated signs), so the sign props of the
  first pass were dropped from data/towns (they doubled every sign).
- Decals stand ≥ 1 unit off their wall and overlapping layers ≥ 1 unit apart (nearer layers flicker on
  hardware/melonDS, as noted for Littleroot); window frames are kept clear of the wooden posts.
- Gen 5's camera hides ~2 tiles behind a 30-unit-high building (as with trees): e.g. the tile in front of Rustboro
  House 2's door is hidden by the School's roof when walking behind it. Same as Black 2's own towns.

## Proofs (screenshots/towns1/)
- `petalburg_ingame.png`, `rustboro_ingame.png`, `dewford_ingame.png`: emulator, standing in front of the buildings
  (Rustboro and Dewford reached with a scratch-only patch moving the test door's arrival; Petalburg too, because the
  walk from Littleroot triggers Birch's chase on Route 101).
- `petalburg_compare.png`, `rustboro_compare.png`, `dewford_compare.png`: Sapphire's map next to a 3/4 render of our
  world cells with the building models at their placements (doors, signs and the fountain are pack-0 models the game
  draws; terrain modules not enabled in this build, so water/sand/paving/fences show as grass).
- `door_offsets.png`: the door-offset finding above.

## Not done / next
- Terrain is other groups' work: Rustboro's paving, fences and the grass squares under lamp tiles (`prop` class),
  Dewford's sand and dock, Petalburg's ponds and hedges.
- Devon Corp.'s emblem on the tower crown (no Black 2 texture looks like Devon's logo; crown left plain stone).
- Petalburg's roofs are Floccesy's red-orange tiles; Sapphire's are redder with horizontal ribs.
- Warps/interiors, NPCs and sign scripts (O4 / generated content).
