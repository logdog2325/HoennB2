# Black 2 asset inventory for the first milestone (2026-10-05)

How to look: `b2tools/export_models.py <group> pack:<id> chunk:<chunk>:<area>` converts models with apicula into
`work/models/<group>/` (not in git, it's game data). View with the `hoenn-viewer` preview server:
`/viewer/index.html?manifest=/work/models/<group>/manifest.json`, or `/viewer/plan.html` for the comparison page.

## Key facts
- **Trees, tall grass, ledges, fences, paths and water are not separate models.** They are baked into each map
  chunk's terrain model and textured from the zone's area texture set (`a/0/1/4`). New maps need new terrain models.
- **Buildings and props** (houses, Pokémon Center, signs, rocks, doors) come from the area's building pack
  (`a/2/2/5`), placed per chunk. 446 distinct exterior models; 28 shared ones are in every pack (`pc_01`, `gate_01`,
  `sign01`–`04`, `door_*`, rocks, `thouse_01`, ...).
- **There is no standalone Poké Mart building** anywhere in Black 2. Marts are counters inside the Pokémon Center
  (script 10110).
- **Gen 5 buildings are bigger than Sapphire's**: Pokémon Center 7.3×5.3 tiles (Sapphire 4×4), Juniper's lab 8.6×5.8
  (Birch's 7×6), Nuvema house 5.0×4.4 (Littleroot house 5×5), Accumula house 5.3×3.6 (Oldale house 4×4).
  One tile = 16 units.
- Walking between zones in one matrix does **not** reload textures or building packs, so a seamlessly connected
  slice must use **one area** for all its maps.

## Closest Unova match: Black/White's own opening (all area 2 → texture set 2, building pack 0)
| Hoenn | Unova | Zone | Matrix 0 cell(s) | Chunk(s) |
|---|---|---|---|---|
| Oldale Town | Accumula Town | 397 | (24,20) | 5 |
| Route 101 | Route 1 | 317 | (24,21), (23,22), (24,22), (23,23) | 4, 2, 3, 1 |
| Littleroot Town | Nuvema Town | 389 | (24,23) | 0 |

Pack 0 holds: `t1_house_01`/`02` (Nuvema family houses, with mailboxes), `t1_labo_01` (Juniper's lab),
`t2_house01` (Accumula, blue roof), `t2_build01` (Accumula apartment), `pc_01`, the shared signs/doors, and seasonal
flower-bed overlays `r01_{a,b}_{season}` (Route 1).

Other candidates seen: Floccesy (pack 53: `t06_house_01`–`04`, `t06_ctower_01`, `d22_farm_01`; rural, red roofs),
Aspertia (pack 52: `c12_*`). Floccesy/Route 19/20 use area 214. Route 19's chunk 281 shows white faces when textured
with set 214: it uses 11 textures that only Aspertia's set has (matches the open question in GEN5_MAPS.md).

## Direction (user, 2026-10-05): Gen 3 shapes, Gen 5 art
Buildings are **new models in the shape of the Sapphire buildings** (same footprint, roof shape, door and window
layout), textured only with **Black 2's own textures** so they read as Gen 5 art. Unova buildings are reference for
style (proportions, roof overhang, shading), not drop-in replacements. This also removes the size mismatch above.

Texture kit seen so far (`screenshots/plan/b2_building_textures.png`): blue roof tiles `t1hy1` (Nuvema houses),
orange roof tiles `yane_001` (lab) / `t06_h_01_a` (Floccesy), Pokémon Center wall + logo `pc_kabe02`, `pc_win1`,
brick/wood walls `t1h03`, `t2_house01_01`, `t06_h_03_a/b`, windows `h_mado`, `t1h04`, `kabe_001/002`,
mailbox `t1_h_post01`, drop shadow `h_kage`.

| Sapphire building | Built as | Textures from |
|---|---|---|
| Player/rival houses | Littleroot house shape (two-tier roof) | Nuvema houses / lab |
| Birch's lab | Birch's lab shape (long roof, rooftop vent) | Juniper's lab |
| Pokémon Center | Gen 3 Center shape, red roof | `pc_01` textures |
| Poké Mart | Gen 3 Mart shape, blue roof | `pc_01` walls + blue roof tiles |
| Oldale houses | Oldale house shape, orange roof | Floccesy / lab roof tiles |
| Signs | shared Gen 5 `sign01`–`04` | — |
| Trees / grass / ledges / paths | new terrain from texture set 2 | — |
| Interiors | reuse Black 2 interiors for now | — |

Open: texture memory budget of a building pack (adding textures to pack 0 / `a/1/7/4` entry 0); CTRMap's "+"
import path (DAE/OBJ/SMD) for new building models.
