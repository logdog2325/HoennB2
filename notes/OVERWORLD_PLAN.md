# Converting Unova's overworld into Hoenn (plan, 2026-10-06)

User request: "before you focus on the main story convert unova to hoenn using the maps you made". So: every
Sapphire outdoor map rebuilt with the Littleroot/Route 101/Oldale pipeline (converter → plan → world.py → chunks),
replacing Unova's overworld; story scripts come after.

## Where we start (converter/plan_map.py over all 65 outdoor maps)
All tiles of all 65 maps are classified (0 unknown metatiles). The builder supports grass, path, tall grass, south
ledges, flowers, trees and town buildings (per-town models); **only Littleroot and Oldale are fully buildable**.
Missing, by tile count: water 41k, cliffs 18k + cliff tops 11k, rocks 8k, sand 4.9k, currents 4.2k, deep water 3.4k,
puddles 3k, fences 1.5k, long grass 1.5k, mountains 1.1k, bike path, walls, bridges, stairs, ash grass, props,
shores, bushes, east/west ledges, waterfalls, cave entrances, and ~20 special props (berry soil, market awnings,
beach umbrellas, Acro Bike rails, archways, big tree…). Buildings: ~2,900 building tiles in 14 more towns.

## Stages
**O1 — foundations (me):**
- Matrix 0 becomes the Hoenn overworld (Escape Rope and Dowsing only work on matrix 0, RESEARCH_WORLD.md §1);
  Unova's overworld is dropped. Test harness: Aspertia's house + test door still work (they are interiors).
- Zone allocation for all 65 outdoor maps (`data/hoenn_zones.json`): Unova's own outdoor zones first (towns→towns,
  routes→routes), never the engine's special zones (Union Room 422, Entralink 279-288, PWT 191-193, Royal Unova 52,
  Join Avenue 490-491, Abyssal Ruins, Nimbasa stadium, 150/151, the matrix-175 zones 289-316, Victory Road…),
  and not 427/428 while the test harness starts there. Place names for all of them.
- world.py: all 49 connected maps on matrix 0; the 16 warp-only maps (Petalburg Woods, Jagged Pass, Mt Chimney,
  Safari Zone…) on their own matrices; features in separate modules (`b2tools/terrain/*.py`) behind one registry;
  a feature without a recipe yet is drawn as plain ground with Sapphire's collision, so the whole world is
  walkable end to end from the start.
- Simple map content generated from pokeruby for every map: signs and NPCs whose script is a single message (their
  scripts/text files written automatically, dialogue word for word), NPC sprites via a Sapphire→Black 2 sprite
  table, wild encounter tables (Sapphire's species/slots; levels scaled later), place-name banners.
**O2 — terrain recipes (multi-agent, ask first):** each recipe copied from how Black 2's own chunks build the same
thing, like notes/GEN5_TERRAIN.md: (1) water, shores, deep water, currents, waterfalls, puddles (Surf collision);
(2) heights: cliffs, cliff tops, stairs, E/W ledges, mountains, rocks (needs Black 2's height values);
(3) sand, ash, long grass, bike path, bridges, fences, walls, bushes, props. Each lands as a module + proof
screenshots; I integrate.
**O3 — town buildings (multi-agent, ask first):** Gen 3 shapes in Gen 5 art for the other 14 towns, inside the
shared budget (≤ 128 models in the one building pack, map + building textures ≤ ~200 KB; Centers/Marts shared).
**O4 —** interiors per building (Black 2 interiors reused by type), warps, fly points, town map, respawn table.
**O5 —** caves and dungeons (61 maps, own matrices/areas), Dive last.

## Other requests queued (decisions 2026-10-06)
Gen 6 Exp. Share (key item, Mr. Stone), HMs usable with HM item + badge (moves forgettable), trainer and wild levels
scaled for the Exp. Share. These are code/data patches independent of the map pipeline.

## Progress (2026-10-06, evening)
O1 done:
- All 49 connected outdoor maps on the Hoenn matrix (416 for now: Black 2's new-game intro still plays in Aspertia on
  matrix 0; switch to matrix 0 when the opening replaces it), 326 cells; 64 maps have zones and place names
  (`data/hoenn_zones.json`), town/route header templates, Unova calendar weather removed, always summer
  (`hoenn_season`).
- Sapphire wild tables for 45 zones (sizes kept: savestates cache a/1/2/7), flat rules per Sapphire rate, levels
  through the Exp. Share curve (`data/level_scaling.json`).
- 204 simple signs/townspeople + 61 item balls generated with Sapphire's text (`gen_map_content.py`, `gen_items.py`,
  `gen3text.py`); zone map scripts now come from our sources into the entity files (Unova's ran our scripts and froze
  the game on entering Petalburg's cell).
- Character sprites (Brendan, May, Birch, Mom, rivals; May and the intro Birch need another pass), Gen 6 Exp. Share,
  HM-free field moves.
- Infrastructure for parallel work: terrain modules (`b2tools/terrain/`), building registries (`data/buildings/`),
  town settings (`data/towns/`), `agent_build.sh`; O2/O3 workflow (8 agents) running.
Still open in O1: standalone maps (Petalburg Woods, Jagged Pass, Mt Chimney, Mt Pyre, Safari Zone, Sky Pillar,
Southern Island, Sootopolis, Battle Tower) on their own matrices; trainers (221 outdoor); hidden items; weather per map;
story NPCs (hide flags) and interiors (O4).
