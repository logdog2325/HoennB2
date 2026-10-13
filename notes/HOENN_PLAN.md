# Plan for the rest of Hoenn (2026-10-06, after the Littleroot–Route 101–Oldale milestone)

Numbers from `notes/HOENN_SURVEY.md` (`converter/survey.py`, all 394 pokeruby maps).

## Size
| Kind | Maps | Notes |
|---|---|---|
| Towns + cities | 16 | 3 done (Littleroot, Oldale; Route 101) |
| Land routes | 38 | 1 done; the long ones are 4–5 chunks (Routes 110/111/119/120) |
| Sea routes ("MAP_TYPE_6") | 11 | mostly water |
| Caves / dungeons | 61 | Granite Cave, Meteor Falls, Mt. Chimney/Pyre, Seafloor Cavern, Sky Pillar, … |
| Indoor | 234 | houses, Centers, Marts, gyms, labs, Contest Halls, ships… many repeat a few templates |
| Underwater (Dive) | 10 | Gen 5 has no Dive |
| Secret bases | 24 | optional |
| Scripts | ~35,000 lines | story, gyms, NPCs (indoor maps hold 20k of them) |
| Trainers | ~350 | Black 2 has trainer classes for most; Aqua/Magma need new sprites |

## Hard parts (flagged)
1. **World grid and zones.** Hoenn's outdoor world is far bigger than the Unova cells we reuse. Needs our own
   matrix (or several), new chunks appended to `a/0/0/8`, and a zone allocation table (394 maps vs Black 2's 615
   zones — enough if we repurpose Unova's). Limits on matrix size / chunk and zone counts: to research.
2. **Texture sets across seamless maps.** Black 2 reloads terrain textures and building packs only on warps, never
   when walking between zones; Unova uses gates between areas. Hoenn has no gates, so every connected outdoor area
   must share one texture set/pack within VRAM limits — or a code patch reloads the area on zone change.
   Research before building beyond area 2.
3. **Height levels.** Cliffs, stairs, bridges, Mt. Chimney: the terrain builder is flat-only today; needs cliff
   geometry (Black 2's `gake` textures), stairs, and heights from the global height table (or an overlay 36 patch).
4. **Water.** Surf tiles (class 0x3d/0x3f, flags 0x56/0x16), shores, animated water (`sea_mizu`, SRT animation),
   waterfalls; 27 routes and 8 cities have water.
5. **Caves.** Cave terrain style, darkness/Flash, Strength/Rock Smash, holes and ladders.
6. **Dive / underwater (10 maps).** No Gen 5 equivalent: needs a new mechanic (code) or a redesign.
7. **Story scripts.** ~35k lines of Gen 3 script to port to Gen 5's script language, with flags/vars mapping and
   cutscene movement. The biggest single job.
8. **Character sprites.** Brendan, May, Birch, Mom, Wally, Aqua/Magma: Gen 5-style edits of Black 2 sprites (decided).
   Overworld + battle (front/back) + trainer card variants.
9. **Interiors.** 234 maps, but a handful of templates (house, Center, Mart, gym shells) cover most.
10. **Starter sequence** (user request): new-game start in Littleroot, Birch on Route 101, choose from the bag, Lv 2
    Poochyena battle, lab; Black 2's starter-choice screen with Treecko/Torchic/Mudkip.
11. **Encounter rate** (user request: exact): decode how Black 2 turns its rate into a per-step chance.

## Order of work
**Phase A — infrastructure and research (next).** Batch converter for all maps; metatile labels for every
outdoor tileset; research for hard parts 1, 2, 10, 11 and the sprite format (8). Output: a map→zone/area/cell
allocation, a coverage report (which maps build cleanly), and answers with evidence.

**Phase B — the opening, to Rustboro (story order).** Route 102, Petalburg (+ gym shell), Route 104 (water!),
Petalburg Woods, Rustboro (+ gym), Routes 103/116, with the starter sequence, Mom/Birch/May scenes, the first
trainers, and Brendan/May/Birch sprites. ~15 outdoor maps, ~40 interiors.

**Phase C — features as they appear:** water (Route 104/105/106), caves (Granite Cave), heights (Route 111/112,
Mt. Chimney), then the rest of Hoenn in story order; Dive last.

## Workflow (multi-agent), proposed for Phase A
Run with the Workflow tool after the user approves; ~7 agents:
- 3 agents label metatiles for the outdoor tilesets (General + the town/route secondaries), rendering each metatile
  and writing `converter/metatiles.json` entries with the existing class names; uncertain ones listed, not guessed.
- 1 agent verifies labels by rendering each outdoor map with its labels overlaid (`render.py`) and reporting errors.
- 3 research agents, each answering with evidence (decomp code, bytes, emulator tests): (a) world grid / zone /
  chunk / area limits and the texture-reload problem; (b) encounter rate algorithm; (c) new-game start, starter
  selection screen, scripted wild battles, and the overworld/trainer sprite formats for the character edits.
Nothing is written to the ROM by agents; results land in notes/ and data/ for review.
