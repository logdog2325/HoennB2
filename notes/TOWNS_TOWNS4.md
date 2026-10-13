# Town buildings, group towns4: Lilycove, Mossdeep, Pacifidlog (2026-10-06)

Decision 2026-10-05/06: Gen 3 shapes, Gen 5 art. Built like Littleroot/Oldale and the other town groups: Python
boxes/roofs (`b2tools/buildings.py`) tiled with regions of Black 2 building textures, sized to Sapphire's footprints
(`data/plans/<Map>.json`), Sapphire's colours.

Files: `b2tools/models_lilycove.py` (also holds the helpers the other two import: rotated regions, wrapped faces,
prisms, rings), `models_mossdeep.py`, `models_pacifidlog.py` -> `work/buildings/<town>/*.dae` (+ texture PNGs,
palettes.txt, textures.txt) -> ToNsbmd -> `*.nsbmd`; registry `data/buildings/towns4.json` (res 380-390); placement
`data/towns/{LilycoveCity,MossdeepCity,PacifidlogTown}.json` (group `towns4`). Proofs: `screenshots/towns4/`.

Rebuild the models:

    cd b2tools && for T in lilycove mossdeep pacifidlog; do python3 models_$T.py ../work/buildings/$T; done
    cd .. && for d in work/buildings/{lilycove,mossdeep,pacifidlog}/*.dae; do
      java -Djava.awt.headless=true -cp "work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar" \
        ToNsbmd $d ${d%.dae}.nsbmd $(dirname $d)/palettes.txt; done

## Rules used
- Placement as the other groups: `buildings` {Sapphire door dest: {res, front}} -> world.py puts the origin at the
  footprint centre (x) and `door row + (4 - front)/16` (z), the front wall 4 units into the door tile [code]
  `b2tools/world.py` (plan buildings loop); `props` in map tile coords for structures plan_map.py has no footprint for.
- Door records: the game draws the door res at origin + (dx, dz). Doors 259/260/261 span x -17..1, y 6..32, z -2..2;
  door_pc (93) x -13.2..13.2, y 2.9..29.8 [test: apicula `convert -f dae` of pack 0's door records, vertex bounds].
  So dx = door tile centre - footprint centre + 8 (+0 for 93), and **walls under a 259-261 door must be >= 34 high**
  (my first 24-unit walls let the door poke through the roof in the preview).
- Collision is the plan's (Sapphire's walkable grid), unchanged.
- Decals stand 1-2 units off their wall (nearer layers flicker on hardware/melonDS: notes in models_littleroot.py).

## Lilycove City (world origin 528,130; zone 96)
| Building (Sapphire dest) | Sapphire footprint (x, rows), door | Model | Res, door res/dx/dz |
|---|---|---|---|
| Move Deleter's house, House 1 | x 35-38 / 41-44, rows 4-6 (+ roof row 3), doors (36,6) / (42,6) | `house`: lavender-white walls on a blue base, blue pillars by the door, blue-framed window right, tall gable roof of periwinkle ribs running down the slope (d5whouse1a turned 90 degrees), light ridge cap | **380**, 259 / 0 / 20 |
| House 4, House 2, House 3 | x 11-14 / 54-57 / 10-13, rows 11-14 / 12-15 / 19-22, doors (12,14) / (55,15) / (11,22) | same | **380** |
| Pokémon Trainer Fan Club | x 37-41, rows 11-14, door (39,14) | `fanclub`: the same house 5 wide, door in the middle, windows both sides | **381**, 259 / 8 / 20 |
| Department Store | x 23-31, rows 0-6 (Sapphire draws it past the map's north edge), door (27,6) | `dept`: 104-unit block of pale blue panels, 3x3 window grid with the Poké Ball emblem over the entrance, grey canopy, shop windows under orange awnings, grey parapet | **382**, 93 / 0 / 20 |
| Pokémon Center | x 23-26, rows 11-14, door (24,14) | shared | 0 |
| Contest Hall (`CONTEST_LOBBY`) | x 20-26, rows 19-24 (+ roof row 18), door (23,24) | `contest`: coral-red walls with darker pillars and white bunting, blue/white base stripe, grey fascia, big pale blue roof with chamfered corners and a wide flat top, emblem over the door. Not towns3's 5x5 hall (res 362): Lilycove's is 7x7 and drawn differently | **383**, 93 / 0 / 20 |
| Cove Lily Motel | x 36-41, rows 21-24, door (37,24) | `motel`: Littleroot-style two-tier tan shingle roof, timber posts and beam, framed windows, dark window band upstairs | **385**, 260 / -16 / 20 |
| Lilycove Museum | x 7-16, rows 2-6 (upper block x 9-14 over rows 0-3), entrance x 11-12, door row 5 (walkable doorway: no plan footprint) | `museum`: white neoclassical wings with square columns and windows on a blue base, flat studded roofs, taller central block with its own colonnade, recessed dark doorway; the stairs below are terrain | **384** prop at (12.0, 6.98), no door model |
| Harbor | x 9-15, rows 27-32, door (12,32) (walkable door: no plan footprint) | towns2's Slateport Harbor: Sapphire draws both harbors identically (side-by-side render of the two maps) | 345 prop at (12.5, 31.0) |
| Harbour light | Sapphire `prop` tiles (61,33) walkable top, (61,34) solid base | `beacon`: white waisted post with a yellow lamp | **390** prop at (61.5, 34.5), no door model |

Not buildings: the Aqua/Magma Hideout entrance (70-71,5) is a cave mouth in the rock island (terrain), fences, the
cliff ledges and the beach.

## Mossdeep City (world origin 688,160; zone 107)
| Building | Sapphire footprint, door | Model | Res |
|---|---|---|---|
| House 1, Steven's house, House 4 | x 27-30 / 18-21 / 17-20, rows 7-9 / 8-10 / 14-16 (+ roof row), doors (28,9) / (19,10) / (18,16) | `house`: beige stone walls (c7h2_1), dark window with a white sill, two-tier roof of brown kawara tiles with their round eave caps (en_sekia1): a skirt roof all round, then an upper gable with a white ridge band over a pale band | **386**, 260 / 0 / 20 |
| House 3, House 2 | x 48-51 / 66-69, rows 3-6 / 21-24, doors (49,6) / (67,24) | same | **386** |
| `GAME_CORNER_1F` building | x 35-39, rows 20-24 (+ roof row), door (36,24) | `gamecorner`: the same house 5 wide and a row deeper, two windows | **387**, 260 / -8 / 20 |
| Space Center | x 60-68, rows 6-13, door (64,13) | `space`: 92-unit block of green glass in dark green frames (c5_rb_03_w1), glass stair tower over the entrance, roof of framed green panes with two white satellite dishes | **388**, 93 / 0 / 20 |
| Gym | x 35-40, rows 6-9 (+ roof row 5), door (38,9) | shared Gen 3 Gym: Sapphire's Mossdeep Gym uses exactly Petalburg's gym metatiles (1aa-1cd) [bytes: data/plans] | 320 (towns1), front 24 |
| Pokémon Center / Poké Mart | x 27-30 rows 14-16 door (28,16) / x 36-39 rows 16-18 door (37,18) | shared | 0 / 3 |

Not buildings: the big 3x3 trees (plan class `other:big_tree`, terrain), cliffs, stairs, sand.

## Pacifidlog Town (world origin 528,320; zone 458)
| Building | Sapphire footprint, door | Model | Res |
|---|---|---|---|
| Houses 1-5 | 3 wide, 2 rows + a walk-behind roof row: x 15-17 rows 12-13 door (16,13); x 2-4 rows 21-22 door (3,22); x 11-13 rows 23-24 door (12,24); x 1-3 rows 11-12 door (2,12); x 16-18 rows 20-21 door (17,21) | `hut`: octagonal hut of dark vertical planks with wooden corner posts and a beam, roof of three scalloped green layers (pack 0's plant_tex4: Sapphire's olive thatch is layered the same way) and a cream knob | **389**, 260 / 8 / 20 |
| Pokémon Center | x 7-10, rows 13-15 (+ roof row), door (8,15) | shared | 0 |

Not buildings: the log rafts (plan class `cliff_top`) and bridges (`bridge`) are terrain; without the water/ground
modules they draw as grass today.

## Textures (Black 2 building texture sets a/1/7/4, `work/tex/extNN.nsbtx`; palettes `<texture>_pl` [bytes: palNN.txt])
| Texture | Set | Size | Used for |
|---|---|---|---|
| `d5whouse1a` | 8 (Driftveil warehouse) | 32x16, 16 colours, 256 + 32 B | Lilycove house roofs (turned 90 degrees) and ridge caps |
| `c4_bp01` | 6 (Nimbasa) | 512 + 32 B | Contest Hall roof, Department Store walls/roof (also towns2, towns3) |
| `trailer_01a` | 4 | 1,024 + 32 B | Contest Hall walls and pillars (also towns3) |
| `en_sekia1` | 48 (Abundant Shrine) | 64x64, 2,048 + 32 B | Mossdeep kawara roofs, slate windows, white ridge band; motel window band |
| `c7h2_1` | 10 (Icirrus) | 1,024 + 32 B | Mossdeep stone walls |
| `c5_rb_03_w1` | 8 (Driftveil) | 1,024 + 32 B | Space Center walls/roof, harbour light lamp |
| already in pack 0 / the slice | 0, 5, 57 | 0 B | `r4_b03_yane01` (white, blue, windows, studs, black), `pc_win1` (glass, emblem), `h_mado`, `h_kage`, `gate_1` (grey), `yane_001` (awnings), `plant_tex4` (hut roofs), `c14_h1_body` (posts, beams, planks, windows), `c14_h2_yane` (shingles) |

Sets exported for browsing/merging (only where missing): `work/tex/ext{10,13,15,16,46,48,56,58}.nsbtx` + PNG folders,
and palette pairs from each pack's own models (`nsbtx.material_pairs`, as rebuild_opening.sh does) in
`work/tex/pal{10,13,15,16,17,46,48,56,58,59,60}.txt`. Checked: the new pal59.txt keeps towns3/towns5's `rr_misel1_02`
on `rr_misel1_02_pl`, so no other group's palette changes.

## Budget
- Models: 11 new (res 380-390 of 380-399). nsbmd sizes (triangles): house 4,464 (88), fanclub 4,816 (98), dept 5,264
  (88), contest 6,928 (137), museum 9,008 (234), motel 6,832 (126), beacon 4,240 (80), Mossdeep house 4,528 (86),
  gamecorner 5,648 (118), space 9,328 (216), hut 7,376 (142): **68,432 B** in all. (Retail Black 2 houses in pack 0
  are 4.5-7.2 KB.)
- Textures: +6,392 B over the slice's set (78,948 -> 85,340 B); +4,688 B when towns1-3 are merged first (c4_bp01 and
  trailer_01a shared) [test: nsbtx.merge on work/tex sets; the patch printed 85,340 B for slice + towns4].

## Field heap limit for pack 0 (important for integration)
Arriving in Lilycove from the test door with different group mixes (HOENN_TEST_NO_WILD, same savestate) [test]:

| Groups in pack 0 | Models | Pack 0 bytes | Building texture set | Result |
|---|---|---|---|---|
| slice + towns1 + towns2 | 75 | 267,404 | 90,388 | OK |
| slice + towns4 + towns2 | 71 | 279,388 | 90,080 | OK |
| slice + towns4 + towns2 + towns3 | 77 | 329,764 | 96,476 | OK |
| slice + towns4 + towns1 + towns2 | 85 | 339,204 (and 356,596 with my first, bigger models) | 96,184 | **black screen after the warp** (player position updates in RAM, nothing is drawn) |
| same, but towns4's 10 models replaced by a 752-byte one-quad model | 85 | ~275,000 | 96,184 | OK |

So the limit is the bytes, not the model count: the field loads the whole pack file into its heap and sets every
model up there (`FieldPropSystem_LoadResBundle` / `InitResources` / `InstantiateResources`,
`external/pokebw2/src/ov036/field_buildmodel.c` [code]); somewhere between ~330 and ~339 KB of pack (with a ~96 KB
texture set, in Lilycove's cells) it no longer fits. **All four town groups together are ~387 KB today**, about 55-60
KB over. Options for the lead: drop retail pack-0 models Hoenn never places (the eight seasonal `r01_*` trees are
40.5 KB, `outwarp01/02` 7.9 KB, the replaced `t1_*` houses/lab), make all groups' models lighter, or split the pack
(needs areas/gates). The margin depends on what else the heap holds where the player is, so leave headroom.

## Testing
`HOENN_AGENT=towns4 HOENN_TOWN_GROUPS=towns4[,towns1|towns2] HOENN_TEST_NO_WILD=1 HOENN_ARRIVE=X,Z zsh
b2tools/agent_build.sh ../../work/agents/towns4/test_arrive` (scratch patch in `work/agents/towns4/`, moves the test
door's arrival; same as towns2/towns3's), then `walk.py ROM work/emu/after_mom2.dst OUT.png D1 L3 D1 D1 L1 D1 L1 D1
W400 D1 W30 P T... S`. Calibrating on the arrival tile itself picked a stale copy of the position (the walk then
failed); taking one step first and using the default address worked. Arrivals: Lilycove (558,146) with towns2 (Harbor),
Mossdeep (721,172) with towns1 (Gym), Pacifidlog (536,337). Proofs (Sapphire render left):
- `screenshots/towns4/lilycove.png`: Contest Hall, Motel, Department Store + Center, Museum, Move Deleter / House 1,
  Fan Club, Houses 4/3, Harbor, harbour light.
- `screenshots/towns4/mossdeep.png`: Center/Mart/Gym, House 1, Steven's house + House 4, Gym, Game Corner building,
  House 2, Space Center.
- `screenshots/towns4/pacifidlog.png`: Center and the five huts.

## Open
- Warps, interiors, NPCs and sign scripts: later work (not set here).
- Pack 0 heap limit above: the groups cannot all be enabled together yet.
- Door colours: Lilycove houses use the blue door_normal01 (259, Sapphire's are blue), Mossdeep/Pacifidlog/motel the
  brown 260; Sapphire's Mossdeep doors are orange-red with a round window.
- Pacifidlog's rafts/bridges and the sea, Mossdeep's big trees and Lilycove's beach/cliffs need the terrain modules;
  the museum stands on Sapphire's raised platform only once the heights module is on (its origin is on row 6, so it
  takes that row's height).
