# Ground terrain module (b2tools/terrain/ground.py), 2026-10-06

Stage O2 (3): sand, ash grass, long grass, Cycling Road, bridges, fences, walls, bushes, rocks, props and the
`other:*` props. Every recipe copies the closest thing Black 2 builds itself. Tags: **[bytes]** = read from the
user's dump (`external/pokebw2/build/b2_us/files`; chunks converted with apicula, collision read from the `.per`
section), **[code]** = decomp / disassembly, **[test]** = DeSmuME on an agent build. Chunk → place names come from
matrix 0's zone ids + `data/zones` headers [bytes].

## Recipes

| Class | Black 2 source | Geometry | Collision |
|---|---|---|---|
| `sand` (beach, sandy paths) | `sea_jimen` beach ground: Nuvema chunk 0, Route 13 chunk 87, Undella chunks 93/94 | flat plane at y 0.5, one repeat per tile | Sapphire `MB_SAND` (0x21) → beach 0x19/0x88 (Undella 93: 69 tiles, 94: 124, Route 13 87: 259, Route 22 302: 99) — makes footprints [test]; beh 0x00 → route sand path 0x03/0x80 (Route 1) or town floor 0x00/0x80 |
| `sand` on Route 111 (desert) | `sabaku01`, Route 4 (chunks 29-37, set 22) | as above | Sapphire `MB_UNUSED_DEEP_SAND` (0x06, wild encounters: pokeruby `src/metatile_behavior.c:15`) → deep sand 0x0C/0x0C (Route 4 chunk 32: 199 tiles); other Route 111 sand → 0x0B/0x88 (chunk 32: 188). Wild Cacnea on deep sand, sand battle background [test] |
| `ash_grass` | none in Black 2: frozen Opelucid's grey-green grass `c8k_grass01ax` (chunks 352-359 = a/0/1/0 swaps 50-57 of Opelucid chunks 74-77, condition 3) + Route 1's tall grass on top | ground every 4 tiles like `grass01ax`, `tall_grass_run` | tall grass 0x04/0x24 (`MB_ASHGRASS` has encounters, `metatile_behavior.c:45`) |
| `long_grass` | Black 2's own very tall grass `nagakusa01a/b`, Route 7 chunk 60 (set 39) — the same name and job (hides the player's legs) | raised mat: top y 16, inset 4 (W/E) and 7.5 (N); slopes from y 2 at the tile edge (v 0..0.5), fringe of blades to y 24 (v 0.5..1), leaning out N / in S / upright W-E; chunk 60 polygons dumped and matched | tall grass 0x04/0x24 (task: normal encounters; Route 7 itself uses 0x08/0x24, 204 tiles); `MB_LONG_GRASS_SOUTH_EDGE` (0x09, no encounters) → route floor. Wild Zigzagoon in long grass [test] |
| `long_grass` alt. (`HOENN_LONG_GRASS=dark`) | dark (double-battle) grass, Route 22 chunk 302 (0x06/0x24 ×62) | Route 1's three layers with `kusa_ec3` y2, `kusa_ec2s` y6, `kusa_ec1s` y9 (no extra texture bytes) | same |
| `bridge` | wooden plank bridges over water: Route 3 chunks 15/16, Route 14 chunk 95 (`hashi01a`) | deck at the land height (drawn at y 1 so it never z-fights the grass sheet), planks across (u 0.34..0.97), v one repeat per tile along the run, side face to 8 below (u 0.34→0.22) on open edges | Route 3's deck tiles: 24 × 0x03/0x80; Route 14 / Route 8: 0x00/0x80 → route 0x03, town 0x00. **No exit-block classes** (0x51-0x58 occur only on the Humilau/Route 22 piers, chunks 300/302) |
| `bike_path` + road railings | Route 8's concrete bridge `hashi02a` (chunk 69, deck tiles 0x00/0x80) | plain deck from the image's deck column, same side face; railings = `t2_saku01` fences | 0x00/0x80; Route 110 railings solid |
| `other:bridge_support` | (Sapphire's strip of bridge side/pillars under the road edge) | no deck: in 3D it is the road's side face; the tile below is water (`water_under`) or ground | solid |
| `fence` | `saku01a` (Route 1 chunk 3, Route 3 chunk 13), metal `t2_saku01` (Accumula chunk 5) in cities and along the Cycling Road | one upright plane y 2..20 (u 0..0.5), strips 10 units wide at y 3 (u 0.5..0.75) and 14.5 (u 0.75..1), v two repeats per tile — matches chunk 3's polygons | Sapphire's bit (walkable railing tiles: floor; Route 110: solid) |
| `wall` | Accumula's stone wall `t02_kabe01` + paving `t02michi_b` (chunk 5) | 16-unit block, faces S/E/W where the next tile is not wall | solid |
| `bush` | Striaton/Route 3 hedge `plant01` (chunks 11, 13) | leafy box with a gable (eaves +12, ridge +16, ridge inset 2) as chunk 13 | Sapphire's bit |
| `rock` (land and sea) | Black 2's terrain boulder `iwa01` (Route 4 35, Driftveil 48, Route 14 95, Humilau 300, Route 22 302) | sized to the 1×1/2×2 footprint; north-facing faces and faces hidden by a neighbouring rock dropped; in water the slopes reach y -8 | Sapphire's bit |
| `prop` | no single equivalent | low stone plinth (`t02michi_b` top, `t02_kabe01` sides) | Sapphire's bit |
| `other:berry_soil` | Accumula's tree pit `t02_ki_sita` (chunk 5): soil in a stone frame | flat decal | Sapphire's bit (not interactive) |
| `other:beach_umbrella` | pack 0 `o_parasol_01` (res 26), placed by Black 2 in chunks 18/835 | building placement at the 2×3 group centre (`placements()`) on beach sand | beach sand |
| `other:beach_chair`, `beach_mat` | bench slats `nagaisu` (Accumula chunk 5) | lounger with a raised back / flat mat on sand | beach sand |
| `other:big_tree` | Route 6 round tree (ki03, `bc.tree_row` recipe) | one tree as wide as the group, heights ×1.5 | Sapphire's bit |
| `other:tree_top_1wide` | same | Black 2's round tree scaled evenly to one tile (`build_chunk.NARROW_SCALE`), on the tile below (b2_trees 2026-10-11; was 1.25 then 1 tile wide at 0.8 height) | Sapphire's bit |
| `other:archway` | bridge planks `hashi01a` | open pergola: posts on the solid ends, front/back beams y 32..40, one 5-unit slat per column (a full roof hid the player [test]) | Sapphire's bit |
| `other:market_awning` | bridge planks | sloped plank canopy y 26..32 | Sapphire's bit |
| `other:acro_bike_rail(_support)`, `stepping_stone` | Route 8's concrete bridge `hashi02a` (rails), iwa01 (stones) | rails: concrete decks + thin posts in the water; bumpy slopes: low stepping stones, or stairs where a column joins two levels (`retile`) | walkable (one bike, no Acro Bike: user decision 2026-10-07; notes/WORLD.md "Acro Bike spots"); supports solid |
| `other:forest_entrance` | — | ground | Sapphire's bit |

## Budgets (measured)
- **Textures:** 3 textures from other sets: `nagakusa01a/b` (set 39), `c8k_grass01ax` (267), `sabaku01` (22). Set 3
  53,184 → 55,904 B (+2,720 B; with water's: 56,232 B); map + building textures 129,856 B of ~200 KB
  (`hoenn_textures` output) [test].
- **Chunks:** ground-only world: largest chunk 61,208 B (cell 02_06), water+ground 76,056 B (cell 18_04); limit
  110,600. Ground adds ~1.54 MB to a/0/0/8 over the bare world (5.83 → 7.37 MB); rocks are 26,474 of its 36,164
  triangles. **The archive's reserve (build_rom.py `RESERVE[8]` = 8 MB) is too small for all modules**: water+ground
  = 9.43 MB → "a/008 is 40965208 bytes, over its fixed size 39919616" [test]; water + heights alone are ~9.0 MB.
- **Placements:** at most **32 building placements per chunk** — `chunkConfig.propCapacity1 = 0x20`
  (`external/pokebw2/src/ov036/field_g3d_mapper.c:234`) and `FieldPropSystem_InstantiateProp` writes
  `propInstances[propIndex]` with no bound check (`src/ov012/field_g3d_map.c:137-140`); a building with a door uses 2
  slots (`field_buildmodel.c:161-173`); 0x120 prop holders in all (`include/field/field_prop.h:121`) [code]. Black 2's
  fullest chunk has exactly 32 (chunk 845) [bytes]. So Hoenn's rocks (2,813 groups, up to 72 per cell) cannot be pack-0
  `rock_01/02`/`searock_01/02` sprites; they stay terrain boulders. Parasols: 13 in cell (8,12) + 2 existing.

## Integration (for the lead)
1. Enable: add `"ground"` to `data/terrain_modules.json`.
2. world.py: call the placements hook, e.g. in `main()` after the per-map loop:
   `for c in order: for f in FEATURES: for res, wx, wz, rot, y in getattr(f, 'placements', lambda cell: [])(Cell(*c, world)): put(c, res, wx, wz, rot, y + hgt(wx, wz))`
   and fail the build when a cell gets more than 32 placements (doors count 2).
3. water.py: draw water under decks — in `look()`, before `if cls not in CLASSES: return None`:
   `if cls not in CLASSES and ground is enabled: p = ground.water_under(world, wx, wz); if p: return look(world, *p)`.
   Collision stays ground's (deck floor). Tried without editing water.py through a scratch import hook
   (scratchpad `site/sitecustomize.py`): Route 119 river, Route 110 sea, Pacifidlog walkways all correct [test].
4. Raise `RESERVE[8]` (e.g. 16 MB) and rebuild the base savestates (`make_states.py`).

## How it was tested
Scratch files in `work/agents/ground/`: `test_arrive.py` (moves zone 389's warp 0 to `HOENN_ARRIVE`, passed to
agent_build.sh as `../../work/agents/ground/test_arrive`) and `test_props.py` (writes `placements()` into the chunks,
standing in for step 2). Bridges over water were built with a reduced map set (Littleroot, Route 101, Oldale, 104,
Petalburg, 110, 119, Fortree, 120, Pacifidlog) so the chunk archive fits the reserve. Proofs: `screenshots/ground/`.

## Not done / open
- Surfing under bridges: our world is one layer, so a surfer meets the deck as land (lands on it, can surf off the
  other side). Black 2's two-layer `GC` chunks could do real under-passes (not studied).
- The Cycling Road and Fortree's walkways are flat (heights module could raise them); Fortree's walkways run between
  tree tiles that hide the player from the south camera (town layout).
- Ash grass blades are Black 2's green tall grass (its snowy winter grass has the same texture names as summer's, so
  `nsbtx.merge` cannot add it next to them).
- Models not in pack 0 that would fit better (pack budget, lead decides): Driftveil market `c5_market_01` (pack 8,
  res 52, 5,888 B model, ~1.9 KB textures) for Slateport's market; beach parasol `s_parasol_01` (pack 17, res 458) or
  `o_parasol_02` (packs 15-17, res 291).
- ~~Route 119's Acro Bike rails make that corner unreachable~~: walked since 2026-10-07 (notes/WORLD.md "Acro Bike spots").
