# Town buildings, group towns3: Fallarbor, Lavaridge, Fortree (2026-10-06)

Decision 2026-10-05/06: Gen 3 shapes, Gen 5 art. Built like Littleroot/Oldale (notes/LITTLEROOT.md, notes/OLDALE.md):
Python-generated boxes/roofs (`b2tools/buildings.py`) tiled with regions of Black 2 building textures, sized to
Sapphire's footprints (`data/plans/<Map>.json`, converter/plan_map.py), Sapphire's colours.

Files: `b2tools/models_fallarbor.py`, `models_lavaridge.py`, `models_fortree.py` -> `work/buildings/<town>/*.dae`
(+ texture PNGs, palettes.txt, textures.txt) -> ToNsbmd -> `*.nsbmd`; registry `data/buildings/towns3.json`; placement
`data/towns/{FallarborTown,LavaridgeTown,FortreeCity}.json` (group `towns3`). Proofs: `screenshots/towns3/`.

Rebuild the models:

    cd b2tools && for T in fallarbor lavaridge fortree; do python3 models_$T.py ../work/buildings/$T; done
    for d in work/buildings/{fallarbor,lavaridge,fortree}/*.dae; do
      java -Djava.awt.headless=true -cp "work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar" \
        ToNsbmd $d ${d%.dae}.nsbmd $(dirname $d)/palettes.txt; done

## Placement rules used (world.py)
- Buildings found by plan_map.py: `buildings: {dest map: {res, front}}`; world.py puts the origin at the footprint's
  centre (x) and `door row + (4 - front)/16` (z), so the front wall stands 4 units into the door tile
  [code] `b2tools/world.py:226-231`.
- Buildings plan_map.py merges or misses (Lavaridge's Herb Shop + house = one 8x4 footprint; Fortree's tree houses
  have walkable doorways, and House 1 is merged into the Pokémon Center's footprint): `props` in map tile coords
  [code] `world.py:232-234`; a prop is lifted to the height of the tile under its origin (`hgt(wx, wz)`).
- Door models: the record's door res is drawn at origin + (dx, dz). Pack 0's door models span x -17..1 (164, 260),
  -18..2 (236), -20..0 (101), -13..13 (93) [test: apicula conversion of pack 0's door records]. Black 2 centres
  the door on the warp tile: Nuvema chunk 0 places res 5 (door 164, dx 0, dz 20) at tile x 777/783/788 (chunk-local
  x -112/-16/64) and zone 389's warps are at x 776.5/782.5/787.5 [bytes]. So dx = door tile centre - footprint
  centre + 8 (+10 for door 101, +0 for door 93).
- Collision is the plan's (Sapphire's walkable grid; building and door tiles solid, the door as Black 2's warp-on-solid
  tile) [code] `world.py:175`. Nothing changed there.
- Decals (windows, bands, posts) stand 1-2 units off their wall: nearer layers flicker on hardware/melonDS
  (notes in models_littleroot.py).

## Fallarbor Town (world origin 128,60; zone 6)
| Building (Sapphire dest) | Sapphire footprint (x, rows), door | Model | Res, door res/dx/dz |
|---|---|---|---|
| House 2 (`HOUSE2`) | x 0-3, rows 3-6, door (1,6) | `house`: olive siding, orange tiled gable roof, framed window with an orange awning right of the door; walls 34 high (door 236 is 4..33) | **360**, 236 / 0 / 20 |
| Prof. Cozmo's house (`HOUSE1`) | x 5-8, rows 15-17 (+ walk-behind roof row 14, pipes on row 13), door (6,17) | `house_pipes`: same house + two grey-capped pipes behind the ridge | **361**, 236 / 0 / 20 |
| Contest Hall (`CONTEST_LOBBY`) | x 6-10, rows 3-7, door (8,7) | `contest`: coral-red walls, blue/white base stripe, white bunting, light pillars by the door, grey fascia, chamfered pale-blue panel roof, Poké Ball plate over the door | **362**, 101 / 10 / 20 |
| Pokémon Center | x 13-16, rows 4-7, door (14,7) | shared | 0 |
| Poké Mart | x 14-17, rows 13-15 (+ roof row 12), door (15,15) | shared | 3 |

The Contest Hall is also placed by towns2 in Slateport (x 8-12, rows 8-12, door 10,12) and Verdanturf (x 2-6,
rows 3-7, door 4,7): all three Sapphire halls are 5x5 with the door in the middle of the front row.
Not buildings: the boulders by the Contest Hall (`rock`, ground module), the bonsai tree (plan tree), the crater
south-west (plan class `path`).

## Lavaridge Town (world origin 188,120; zone 62)
| Building | Sapphire footprint, door | Model | Res |
|---|---|---|---|
| Herb Shop (`HERB_SHOP`) | x 11-14, rows 13-15 (+ roof row 12), door (12,15); plan_map.py joins it with the house into one 8x4 footprint | `house`: tan board walls in a dark timber frame, red corrugated gable roof, light fascia, framed window right | **363** as prop at (13.0, 14.0), door 260 / 0 / 20 |
| House (`HOUSE`) | x 15-18, rows 13-15, door (16,15) | same | **363** as prop at (17.0, 14.0) |
| Gym (`GYM_1F`) | x 2-7, rows 12-15 (+ roof row 11), door (5,15) | shared Gen 3 Gym (towns1); Sapphire's Lavaridge Gym uses the same gym metatiles (1b2-1cd) as Petalburg's | 320, front 24 |
| Pokémon Center | x 8-11, rows 3-6, door (9,6) | shared | 0 |
| Poké Mart | x 14-17, rows 2-5, door (15,5) | shared | 3 |

Not buildings: the hot spring (puddle, rock border: water/ground modules), the walkway north of it (bridge), stairs.

## Fortree City (world origin 368,60; zone 16)
| Building | Sapphire footprint, door | Model | Res |
|---|---|---|---|
| House 1, 2, 3 | doors (10,3), (17,3), (25,3) | `treehouse` | **364** props at (door x + 0.5, 4.0) (data/towns had 2.0 until 2026-10-09: two rows north; walkways and houses on stilts since, notes/WORLD.md "Showcase glitches") |
| House 4 | door (32,2), deck rows 3-4 | `treehouse_tall` | **365** prop at (32.5, 3.0) |
| House 5, Decoration Shop | doors (12,13), (37,13) | `treehouse` | **364** props at (12.5 / 37.5, 14.0) |
| Pokémon Center | x 4-7, rows 2-6, door (5,6) (plan footprint x 4-12 includes House 1) | shared | 0 as prop at (6.0, 5.0) |
| Poké Mart | x 3-6, rows 12-14 (+ roof row 11), door (4,14) | shared | 3 |
| Gym | x 19-24, rows 7-11, door (22,11) | shared Gen 3 Gym (same gym metatiles 1b2-1cd as Petalburg/Lavaridge) | 320, front 24 |

Sapphire's tree house (gTileset_Fortree metatiles 224-237): crown row (3 wide), cabin rows door-1..door (a small brown
cabin with a dark open doorway and shutters, set into a yellow log platform ~4 tiles wide), then the walkway row
(plan class `bridge`, Sapphire elevation 4) with the rope bridges, and the ladder (`stairs`) below.
The model: cabin 2.5 tiles wide (orange boards, dark corner posts, open doorway, louvred shutters), plank platform
x ±31 from behind the cabin to the door row's south edge, stacked-plank wings either side, round leafy crown. The
walkway row itself is the ground module's (its `bridge` decks), so the model stops at the door row.
**Origin = door column centre at the south edge of the door row**, so the prop's height is the walkway tile's
height: with `HOENN_TERRAIN=heights` the houses stand on their raised walkways (+16) [test:
`screenshots/towns3/fortree.png`, last panel]. The doorway is modelled (Sapphire's are open doorways, behaviour 0x60),
so records 364/365 have no door model (0xFFFF), like Black 2's door-less records.

## Textures (all from Black 2 building texture sets a/1/7/4, `work/tex/extNN.nsbtx`)
| Texture | Set | Used for |
|---|---|---|
| `rr_misel1_02` | 59 (Join Avenue) | Fallarbor olive siding, tan trim |
| `yane_001`, `h_mado`, `pc_win1`, `gate_1`, `h_kage`, `plant_tex4`, `t2_buil1` | 0 (already in pack 0's set) | roof tiles, glass, crest, grey metal, shadow, crown leaves, shutters |
| `c14_h1_body`, `c14_h2_kabe` | 57 (Humilau) | framed windows, dark posts/doorway; cabin boards |
| `trailer_01a` | 4 (Virbank) | Contest Hall red walls, pillars |
| `c4_bp01` | 6 (Nimbasa) | Contest Hall roof panels (also used by towns2) |
| `r4_b03_yane01` | 5 (Route 4) | blue/white stripes (also slice) |
| `d22_farm01_1` | 53 (Floccesy Ranch) | Lavaridge red roof, tan walls, timber; Fortree planks |

All palettes are `<texture>_pl` in their sets [bytes: nsbtx._parse].

## Budget
- Models: 6 new (res 360-365 of 360-379). nsbmd sizes: house 4,496 B (72 triangles), house_pipes 7,664 (148),
  contest 11,792 (296), Lavaridge house 3,824 (64), treehouse 10,128 (242), treehouse_tall 12,208 (310).
- Textures: +8,100 B over the slice's set (73,952 -> 82,052 B); +7,504 B when towns1 and towns2 are merged first
  (c4_bp01 shared). Per texture: rr_misel1_02 2,132, d22_farm01_1 2,132, c14_h2_kabe 2,132, trailer_01a 1,108,
  c4_bp01 596 [test: nsbtx.merge on work/tex sets].
- Test build with slice + towns3 + towns1: 65 models in pack 0, building texture set 88,156 B (patch output).

## Testing
`HOENN_AGENT=towns3 HOENN_TOWN_GROUPS=towns3,towns1 HOENN_TEST_NO_WILD=1 HOENN_ARRIVE=X,Z zsh b2tools/agent_build.sh
../../work/agents/towns3/test_arrive` (scratch patch in `work/agents/towns3/`, moves the test door's arrival; same as
towns2's), then `walk.py ROM work/emu/after_mom2.dst OUT.png D1 L3 D1 D1 L1 D1 L1 D1 W400 C<X>,<Z> T... S`.
Arrivals used: Fallarbor (138,70), Lavaridge (198,130), Fortree (376,69). Proofs (Sapphire render left):
- `screenshots/towns3/fallarbor.png`: House 2, Contest Hall, Center; House 1 with pipes, Mart.
- `screenshots/towns3/lavaridge.png`: Center, Mart; Herb Shop + house with their doors; Gym.
- `screenshots/towns3/fortree.png`: tree houses 1-3 from the walkway; House 5, Mart, Center; House 2 on its +16
  walkway with the heights module.

## Open
- Warps, interiors, NPCs and signs: later work (not set here).
- Fortree looks bare today: its `tree_bot` tiles outside complete 2x2 trees are drawn as plain ground (plan/terrain,
  not buildings), and the rope bridges/ladders need the ground and heights modules.
- Sapphire's Lavaridge doors have red frames; Black 2's door_normal02 (260) is brown.
- The Contest Hall door is Black 2's door01 (101, blue); Sapphire's is glass with an emblem.
