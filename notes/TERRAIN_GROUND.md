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
- Surfing under bridges (surf_under 2026-10-17, surf_under2 2026-10-18): Route 110's Seaside Cycling Road (both parts
  over the sea) is Black 2 `GC` chunks with two collision layers (world.py bridge_layers, the caves' rule: notes/CAVES.md
  "Walk-under bridges"): layer 0 = surf water under the road, layer 1 = the road; its fenced railings = water in layer
  0, solid in layer 1; the land at the road's ends = solid in layer 0. Surfers pass under (New Mauville's entrance is
  reached under the road, as in Sapphire), walkers and cyclists stay on the road. The road's support tiles (open
  water in the model) stay solid, as before.
  **Two lookup heights [code][test].** The first try (8502244; user's melonDS test: no surfing under, then stuck on the
  road) had water at -8 under the road at 0. Black 2 checks a step at the actor's own height (ActorRouteCollCheck),
  but the surf landing test (ov036 CheckSurfExitEvent), surfing off land (CheckSurfHeightAllow) and the bike's tile
  tests read the tile in front via FieldPlayer_GetWPosInDir (0x0219a9ce), whose y is the player's GRID height << 16 =
  HEIGHT_TO_GRID(y) * 16, truncated toward 0 (ov012 field_actor_tool.c:14). A surfer at -8 looks ahead at 0, where the
  road (0) beats the water (-8): the landing test fired, the surfer jumped onto the road and stood on its water layer
  (the step's own height) on foot. Fix (world.py _bridge_ok, _b2_front_y): water under the railings at -27.8 (the
  deepest flat record whose step in from the -8 water stays under 20: offset index 371; 81,054 of 81,920 fx), under the
  road at -31.4 (index 145: a surfer at -27.8 or -31.4 looks ahead at -16, where -31.4 water is still nearer than the
  road at 0), railings solid at 16, ends solid at -31.4. Black 2 draws the part of the sprite above the deck through it:
  16 under the road showed head and body, 24 the tip of the hat (user's melonDS test of db93950), 31.4 nothing (one
  pixel of hat on the east railing, 27.8 under it, while passing; DeSmuME, surf_under_hat 2026-10-18).
  outdoor_check.py models both heights; on 8502244's world it reports 98 "stuck" landings, on this one none. DeSmuME:
  work/agents/surf_under2/tests/surf.py, bike.py.
  Routes 119/120's plank bridges (bridges 2026-10-18): their decks stood 8 over the water with open water beside
  them; a deeper water under them loses the step in from the open water (20 units), so no two-layer setting both
  passed a surfer and hid it. **Raised** (terrain/heights.py raise_bridges, step 11b, after every other height): the
  span (Sapphire's walkable elevation-15 tiles over surf water) stands at least RAISE_CLEAR = 32 over its water's
  surf height - the higher bank's height when that is enough and reachable, else the lowest multiple of 16 that
  works - and the dry end tiles step 16 at a time from each bank, then run flat to it (Black 2's limit is 20). A walker
  on the end tile next to the span must read the deck in front at its grid height (_b2_front_y), not the water layer.
  bridge_layers then gives the span two layers with the water at the open water's own height (no dip going under,
  first choice when the deck stands RAISE_CLEAR over it) and its end tiles a solid layer under them (the end check
  also has the walkers stepping on from the bank). Results (all three versions, the same tiles):
  | bridge | span | water (surf y) | end tiles (west .. east) | cells |
  |---|---|---|---|---|
  | Route 119 by the Weather Institute (344-348, 93-94) | 48 | 8 | 32 48 / 48 48 | (10, 2) |
  | Route 120 by Fortree (418-433, 75-76) | 80 | 40 | 48 64 / 80 80 | (13, 2) |
  | Route 120 south (432-439, 127-128) | 32 | -8 | 32 / 32 | (13, 3), (13, 4) |
  Route 120's south bridge is not raised: its river was split at the bridge into two water bodies, the north one (and
  the strip of land north of it, Sapphire elevation 3, two secret-base caves) at the bridge's level 32 over the south
  bank, where Sapphire has one body of elevation 1 reached from the south bank. heights.py now treats the water on both
  sides of a surf-under span as one body when floating regions take a shore's level (step 2), and the span counts as a
  surf shore only within one level of the water's other shores (4b): the river and the strip are at the south bank's
  level 0, 40 under the deck. Drawing (terrain/ground.py): runs split at the deck's steps, wooden risers at every step
  (deck_risers; heights.py draws no rock skirt there, _riser), posts every 4 tiles from the span's middle (bridge_posts;
  a pier's post per tile read as a fence and stood in a surfer's way), south/east side faces a hair inside the deck so
  world.py lifts them by the deck (they fell to the water's level; jetty 2026-10-18: so do every plank deck's faces
  over a tile of another height - Mr. Briney's jetty, Lavaridge's bridge, Route 119's south bridge). Rock round the dry end tiles rises to them as
  faces; water.py draws the water under the span at its own level. People on the decks (Route 120's Steven and
  Kecleon) stand at the deck's height (story.py deck_y). Cost: a second collision layer is 8,200 B per cell, and
  Black 2 loads a chunk into a fixed 110,600-byte buffer with no length check: world.py write_cell's chunk_fit measures
  every two-layer cell (its model through ToNsbmd) and, when it is over, gives back the cracks fix in that cell only -
  first the T-junction splits, then also the ground's under-floor. Sapphire: (10, 2) (Route 119's bridge) 123,444 B
  with both, 105,652 B without either; (13, 4) (Route 120's south bridge, its south row) 101,156 B without the splits.
- The Cycling Road and Fortree's walkways are flat (heights module could raise them); Fortree's walkways run between
  tree tiles that hide the player from the south camera (town layout).
- Ash grass blades are Black 2's green tall grass (its snowy winter grass has the same texture names as summer's, so
  `nsbtx.merge` cannot add it next to them).
- Models not in pack 0 that would fit better (pack budget, lead decides): Driftveil market `c5_market_01` (pack 8,
  res 52, 5,888 B model, ~1.9 KB textures) for Slateport's market; beach parasol `s_parasol_01` (pack 17, res 458) or
  `o_parasol_02` (packs 15-17, res 291).
- ~~Route 119's Acro Bike rails make that corner unreachable~~: walked since 2026-10-07 (notes/WORLD.md "Acro Bike spots").
