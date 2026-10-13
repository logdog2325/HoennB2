# Littleroot Town (milestone map 1) — status 2026-10-06

Replaces Nuvema Town: zone 389, matrix 0 cell (24,23), chunk 0, area 2 (building pack 0, texture set 2).
Sapphire's 20×20 map sits at chunk tiles (6..25, 0..19); everything else in the chunk is forest.

## Rebuild
    b2tools/rebuild_slice.sh        → work/rom/hoenn.nds   (copy for testing: builds/hoenn_littleroot_vN.nds)

Steps it runs:
1. `converter/plan_map.py` → `data/plans/LittlerootTown.json` (tile classes from `converter/metatiles.json`,
   trees, building footprints, doors, signs). Matches Sapphire exactly; no unclassified tiles.
2. `b2tools/build_chunk.py` → terrain DAE (grass, flowers, sand patches, round trees, forest border), collision,
   placements → `ToNsbmd` → NSBMD.
3. `b2tools/models_littleroot.py` → house_l/house_r/lab DAEs (Gen 3 shapes, Black 2 textures) → `ToNsbmd`.
4. `MergeNsbtx` → building texture set for pack 0 (+ `c14_h2_yane`, `c14_h1_body` from Humilau, `c4m_yane_001`).
5. `build_rom.py --clean test_door_to_nuvema littleroot text scripts`.

## What's in the game
| Feature | Status |
|---|---|
| Layout tile-for-tile (trees, flowers, sand patches, signs, building footprints, north exit) | done, verified against Sapphire (`screenshots/littleroot/`) |
| Collision = Sapphire's walkable area | done |
| Brendan's house, Prof. Birch's house, lab: Gen 3 shapes, Gen 5 textures | done (v1 art) |
| Doors → interiors | done: Brendan → zone 390 (Nuvema hero's house), Birch → 392, lab → 396 (Juniper's lab) |
| Signs with Sapphire text | done: town sign, "{player}'s House", "Prof. Birch's House", "Prof. Birch's Pokémon Lab" |
| NPCs at Sapphire positions with Sapphire dialogue | done: twin (sprite 8), fat man (25), boy (12), wandering like Sapphire |
| Location name "Littleroot Town" | text done (place name 4); banner shows when walking in from Route 101 (not built yet) |

## Known gaps / next polish
- House signs assume a boy player (Sapphire swaps them for May). Gender check comes with the story work.
- Twin uses only her pre-story line; Mom (story) is not placed.
- Moving trucks (opening) stand at both houses (pack 0 res 460, `b2tools/models_truck_ext.py`, LittlerootTown "props" in
  data/hoenn_world.json); scripts hide them with `BMSetVisible 8, 170, 362, 0` (Brendan's) / `8, 179, 362, 0` (May's),
  on every field load (MapScript 3 and 4). Their row-10 tiles are solid also when hidden (static collision).
- Flowers are Black 2's white/yellow `hana01.1`, Sapphire's are red: look for a red flower texture in other sets.
- Roof shingles (`c14_h2_yane` block) look blotchy; consider a smaller/seamless region or another roof texture.
- Interiors are Nuvema's (allowed for the milestone); Littleroot interiors come later.
- `test_door_to_nuvema` is how tests reach Littleroot (player's front door in Aspertia). A real new-game start in
  Littleroot needs a script/code change later.

## Text conventions
Sapphire wording kept; capitalisation in Gen 5 style (POKéMON → Pokémon, PROF. BIRCH → Prof. Birch, LAB → Lab).
`\p`/`\l` → `{be01}` (wait for a button, scroll). `{0100:0}` = player name, needs `WordSetPlayerName 0` first.
