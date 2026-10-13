# How Black 2 builds terrain, and how we copy it (2026-10-06)

Learned by dumping Black 2's own chunks (`b2tools/blender/tilemap.py`, `dump_region.py`, `viewer/chunk.html`).
Units: 16 per tile; chunk = 32×32 tiles centred on the origin; y up; +z = south (towards the camera).

## Layers (area 2 / Nuvema, Route 6)
| Thing | Texture | Geometry |
|---|---|---|
| Ground | `grass01ax` 64×64 | flat at y = 0, texture repeats every 4 tiles (u = x/4, v = -z/4 in tiles) |
| Path middle | `michi01b` 16×16 | flat y 0, 1 tile per repeat |
| Path edge (grass fringe) | `michi01a` 32×16 | 1-tile strip inside the path border, fringe (v = 1) on the outer edge, corners mitred diagonally |
| Sand patch | `michi_hage` 32×32 | 2×2-tile decal at y = 3 |
| Flowers | `hana01.1` 16×16 | 1-tile decal at y = 2 (white/yellow); `kisetu_hana` = seasonal pink/white |
| Grass tufts | `ue_grass00/01` | small decals at y = 3 |
| Pine tree (Nuvema) | `ki02ax/bx/c/dx` | shadow ki02c y3 (2×2), one south-facing side image ki02ax y3–72, canopy ki02bx y26, top ki02dx y60 |
| Round tree (Route 6) | `ki03ax/bx/dx` + `ki02c` | shadow y3, side image ki03ax y3–56 facing south plus **one north-south ki03ax card through every tree's centre**, canopy ki03bx y23, top ki03dx y46.3; every tree polygon has normal (0, 1, 0), the cards are drawn from both sides (see "Trees" below) |
| Tall grass | `kusa_ec3` y2, `kusa_ec2` y6, `kusa_ec1` y8 | three stacked flat leaf layers, nudged 2 units south, one repeat per tile; one quad per layer per run of tiles (Route 1) |
| Ledge (jump south) | `dansa01a` 16×16 | earth lip in the south part of the ledge tile: rises from z+0.38 to 4 units at z+0.88, drops to the ground at z+1; tapered caps over the end tiles (Route 2). Collision: class 0x75, flags 0x0001, same height |

- Draw trees as **rows** (one strip per row of side-by-side trees, texture repeating per tree), as Black 2 draws its
  forests: Littleroot went from 63 KB to 18.5 KB.
- Paths: border tiles are 2×2 quads of `michi01a` with v = 1 − (distance to the nearest grass tile, capped at one
  tile); deeper tiles plain `michi01b`. Gives straight fringed edges and rounded corners like Black 2's.
- Trees are 2×2 tiles, like Hoenn's. **Hoenn trees use the round tree** (closer to Sapphire's leafy trees, and
  shorter, so they hide less).
- Gen 5's camera looks from the south (~40° elevation, measured from occlusion in-game): a tree hides the tiles up to
  ~3 rows north of it. Black 2's own maps accept this (Route 6). For trees that are *outside* a Sapphire map (the
  forest border), we leave one blocked grass row (`--south-gap 1`) so the player stays visible on the last row.

## Seasonal chunk swaps
`a/0/1/0` swaps chunks by season (e.g. Route 1's chunk 3 → 273/275/277 in summer/autumn/winter). Any chunk we
rebuild must have its swap entries pointed back at itself (`patches/no_season_swaps.py`), or the game shows the old
map in other seasons.

## Collision (`.per`), values copied from Nuvema / Route 1 / Route 2
- Route floor: class 0x1f flags 0x80; route sand path: class 0x03 flags 0x80; tall grass: class 0x04 flags 0x24.
- Walkable: inclination 0, height index 3 (= y 0), class 0x00, flags 0x0080.
- Solid (trees, buildings incl. the door tile, outside the map): same height, class 0x01, flags 0x0081.
- Doors are warps on the (solid) door tile; walking into it from the south enters.

## Model rules (for `ToNsbmd`)
- The DAE must have **normals** (without them the game lights it wrongly; our writer computes face normals).
- Each texture's image must be next to the DAE (CTRMap reads its size to scale UVs); image id = game texture name.
- Palettes: `<texture>_pl` except a few (`b2tools`/`work/tex/palNN.txt` from the game's own models).
- Size: our Littleroot terrain is 63 KB; Black 2's largest chunk model is 92 KB (median 18 KB).
- **Back faces are culled** (Black 2's terrain materials and ours: apicula `info` "Cull: Backfacing"): wind every
  polygon counter-clockwise seen from the side the camera looks at (ground and ledge lips: from above). The ledge
  middles were wound the other way and were invisible in the game until 2026-10-06 (only the end caps showed);
  `b2tools/ledge_check.py [WORLD]` checks every ledge tile, corner and seam of a built world.
- **Ledge corners**: Sapphire turns its ledges round corner tiles (class `ledge_cap`, solid). Black 2 has no corner
  piece (its one overworld corner, Route 23 chunk 309 tile (12,20), is two tapered ends with a tree on the corner
  tile), so `build_chunk.ledge_corners` turns Black 2's own lip round the tile with a mitre (the profile is the same
  on both sides of the diagonal), and runs that end at a corner, or go on into the next chunk, end at full height
  instead of tapering (`ledge_joins`, `_open_end`). Side ledges use the south ledge's v (1 back, 0.5 crest, 0 foot),
  as Black 2's do (apicula DAE of chunks 286 / 282).

## Buildings
- Footprint in collision = solid; the **front wall sits 4 units into the door tile** (Black 2's own placement);
  model origin = footprint centre on the ground; door model comes from the building
  pack record (`door res`, offset dx/dy/dz) and is drawn by the game.
- Pack record (36 bytes, no animation): `res, type 0, door res, dx, dy, dz, 0xFFFF, 0, 4×0, 4×0xFFFFFFFF`.
- Building textures live in the area's building texture set (`a/1/7/4` entry = pack id). Adding textures:
  `MergeNsbtx` (CTRMapV writer). It re-encodes translucent A5I3 textures as A3I5 (`t01_kira`, Nuvema's sea sparkle,
  changes); every other texture is checked pixel-identical after merging.

## Trees (b2_trees, 2026-10-11): Black 2's round tree exactly
Read from all 96 Black 2 chunks that use the round tree (apicula DAE + `apicula info`; Route 6 chunks 53-55):
- **Every tree polygon has normal (0, 1, 0)**, the vertical cards too, so the area light (a/0/6/0; light 0 points
  down-left, about (-0.47, -0.87, -0.07)) lights the cards like the canopy. Our writer used face normals: the cards got
  almost no diffuse light (south) or were lit on one side only (the crossed ones), under brighter tops: the "scuffed"
  look (dark bodies, a light or dark stripe through trees at the screen's sides). `dae.Model.normals` (material ->
  normal) gives the tree materials (0, 1, 0) (world.py write_cell, `nsbmd_fix.TREE_MATS`).
- **Materials:** diffuse 25/31 with "diffuse = vertex colour" and ambient 31 (NNSG3dResMatData diffAmb `0x7fffe739`),
  ki03ax drawn from both sides (polyAttr `0x1f80c1`; the others `0x1f8081`). CTRMap's writer gives every material
  `0x7fff7fff` and back-face culling; `nsbmd_fix.tree_materials` writes Black 2's values when patches/hoenn_world.py
  packs the chunks.
- **A north-south card through every tree** (we crossed only a row's two ends, one-sided), except a tree with a
  height change within a tile (its card met the cliff's face: outdoor_check layer). Heights: card 3-56, canopy 23,
  top 46 (Black 2 46.3; 46 stays 2 under ground 48 up).
- Black 2 has no one-tile tree: 32 wide (2x2) almost everywhere, 48 wide with heights x1.5 in a Gym (chunk 1001;
  our `other:big_tree` recipe). Its forests overlap and offset trees (Route 6 chunk 55). So a dense-forest tile that
  no 2x2 tree fits now gets a whole tree over a 2x2 window of forest tiles of one height (`world.overlap_fill`, after
  the heights): no shadow, cards moved 2 units per level (never in an overlapped tree's card plane), canopy and top
  lifted (`build_chunk.overlap_lift`, 4+) to stay 2 clear of every tree layer under it, the 16-unit levels and a
  cliff's faces/lips beside it. Only trees no window fits (lone trees between walkable tiles) and Sapphire's
  `tree_top_1wide` stay one tile wide: Black 2's tree scaled evenly to one tile (`build_chunk.NARROW_SCALE` 0.5,
  canopy 1.5 lower to clear tall grass at 8 and lips at 12), never squeezed (were 16 wide x 0.8 high: the art at
  40% width).
- Winter (ash) trees: the same geometry with Icirrus's winter textures (`*_y`, data/hoenn_ash.json).
- Collision and placements untouched (all 422 cells byte-identical to v16.3). Main world after the 2026-10-11 second
  pass: 1,272 forest-fill trees, 927 overlapping, 1,216 one-tile (v16.3: 2,634 squeezed ones). a/0/0/8 +1.06 MB over
  v16.3; largest chunk 90,012 B (v16.3 95,340; limit 110,600); terrain triangles 291,889 -> 334,141, the most in any
  20x15-tile view unchanged (1,633; +560 at most in one view, to 1,409). outdoor_check vs v16.3: default kinds
  identical, layer 36 -> 34 open (+1 accepted: the palm's own crown fans), cull 292 -> 289, hole 59 -> 58.
- **Lighting: DeSmuME vs melonDS (settled 2026-10-11):** in our DeSmuME harness (py-desmume 0.9.12) Black 2's own
  chunks render about 1.3x darker than ours (a Black 2 chunk put into one of our cells, tools/b2ref.py: about 0.75 of
  the texture's colours by day; ours at full colour). In melonDS 1.1 (the user's emulator; muted, run in the background
  with a battery save and a test-only auto-A patch: work/agents/b2_trees/tools/melonshot.sh, test_autopilot.py) Black
  2's chunk and ours render alike: a Black 2 tree (63, 173, 132) mean colour, ours (65, 177, 132); our cells look the
  same in both emulators. So the gap is DeSmuME's handling of Black 2's own models, nothing to fix in ours
  (screenshots/b2_trees/melonds_vs_desmume_lighting.png).
- **Every blocked tree tile shows a tree (user, 2026-10-11):** forest_fill also gives blocked tree tips (Sapphire's
  tip tiles are usually walk-behind; 99 are blocked) and blocked tree tiles by a sign, prop, bridge, stairs or building
  a tree (overlapping or one-tile; not by a big tree or a Fortree tree house, whose models have their own trees and
  crowns), and Sapphire's one-tile-wide trees (`tree_top_1wide`) get a one-tile tree on their blocked crown tile too
  (ground.py's stands on the trunk tile). No tree stands on a walkable tile except the walk-behind top rows of
  Sapphire's own 2x2 trees (as Sapphire); a one-tile tree beside a sign has its south card 3 units south (the sign's
  board reaches 5 units into the tile). Left: 151 blocked tiles by Fortree's tree houses and big trees (the models
  cover them). Collision unchanged. Top-down check: work/agents/b2_trees/tools/footprints.py.
- **Mossdeep's trees are Black 2's Humilau palm** (user, 2026-10-11; terrain/palms.py): its 16 triangles copied from
  Humilau chunk 300 (texture set 230: ki04ax trunk cards, ki04bx/ki04dx crown fans, ki04c shadow; normals up, Black
  2's material values), one per 2x2 tree, scaled evenly to one tile or to Sapphire's 3x3 trees (1.5x), palms
  never overlapping (a tile no whole palm fits gets a one-tile palm). +2,896 B in Hoenn's texture set 3 (72,856 B;
  with the building textures 175,436 B of ~200 KB).
- Black 2's other trees, not used: Castelia's park tree (`c3_tree3`), the dark pines `ki00*` and `ki02*`.
- Proof and tools: work/agents/b2_trees (shots/, tools/ab.sh = world + chunkpatch onto the release ROM + warps,
  tools/b2ref.py = Black 2's own chunk model in one of our cells, the in-engine reference).
