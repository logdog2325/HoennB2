# In-game event tickets and islands (events agent, 2026-10-07)

User request: Sapphire's and Emerald's event tickets become in-game post-game events (no Mystery Gift). Proofs:
screenshots/events/ (01-21).

## What the player sees
| Ticket (Black 2 item) | Giver (after the Hall of Fame, first talk) | Island (zone) | Legendary (level) |
|---|---|---|---|
| Eon Ticket (Liberty Pass 574) | Mom, at home, after Dad's S.S. Ticket scene: a letter from the Lilycove ferry company | Southern Island (ch13's) | Latios 55 (ch13) |
| Old Sea Map (Journal 433) | Capt. Stern, Slateport Harbor: found in a wreck on the seafloor | Faraway Island (158 / forest 159) | Mew 32 (Emerald 30) |
| Aurora Ticket (Coupon 2 461) | Prof. Cozmo, Fallarbor: a colleague who studies meteorite sites | Birth Island (195) | Deoxys 32 (Emerald 30) |
| Mystic Ticket (Coupon 3 462) | Lanette, Route 114: from Bill, the Kanto PC maker | Navel Rock (232, caves, summit 233) | Lugia 78, Ho-Oh 78 (Emerald 70) |

- Givers' lines are new (Sapphire/Emerald have none): text lines 28-29 of both Littleroot houses' files (0619/0621),
  35-36 of 0352 (Slateport Harbor), 12-13 of 0108 (Cozmo's house), 8-9 of 0360 (Lanette's house). Every other line is
  Emerald's, word for word (work/agents/events/tools/etext.py converts Emerald text labels).
- Lilycove's harbor (Emerald's LilycoveCity_Harbor script, on top of ch13's attendant): the first time with a ticket, the
  ticket's scene (Old Sea Map: the sailor, "!", Mr. Briney apologises and sails you; Aurora / Mystic: "Is it you who
  brought that odd ticket?"; several: "Where shall we sail first?"); afterwards the regular menu lists Slateport,
  Battle Tower, then Navel Rock / Birth Island / Faraway Island for each ticket held. Sapphire's Eon Ticket scene stays
  first (ch13). Slateport's harbor does not offer the islands (Emerald: Lilycove only).
- Every crossing is `h_sail_ferry` (Black 2's ferry cutscene; boats agent). Each island's sailor sails you back to
  Lilycove ("Do you want to return to Lilycove?").
- Legendary battles: `ev_legend_battle` (scenes/events_lib.inc): caught -> caught + hide flags; defeated -> defeated +
  hide flags and Emerald's "The X flew away!"; ran -> the line only, it is there again next visit; lost -> whiteout.
  Every Hall of Fame clears the defeated flags (0114 HF_SetGameClearFlags, Emerald's ResetDefeatedEventLegendaries; all
  versions since postgame_fix 2026-10-19, user decision; Celebi too), so a knocked-out legendary is back after it.
  Levels follow data/level_scaling.json (30 -> 32, 70 -> 78), as ch13 did for Latios and Rayquaza.
- Emerald's Lilycove Harbor (postgame_fix 2026-10-19): the Eon Ticket is the fourth ticket (FLAG_SHOWN_EON_TICKET: its
  first-time scene sails straight to Southern Island, then "Southern Island" stays first in the destination menu while
  the ticket is held, and in the several-tickets menu), the menus say Emerald's words (Slateport City / Battle Frontier
  / ... / Exit; Slateport: Lilycove City / Battle Frontier / Exit). Southern Island's Lati: pokeemerald's rule
  (scenes/emerald/SouthernIsland_Interior.inc: FLAG_TEMP_2, FLAG_DEFEATED_/FLAG_CAUGHT_LATIAS_OR_LATIOS). Sapphire/Ruby
  keep their one-time Eon trip and one-chance Latios/Latias. Emerald's world had no slab sign (its content file names
  pokeemerald's script label): it is a story sign now (data/story/emerald/e_ch11.json), so Emerald v1.1's slab could not
  be read at all. Tested: screenshots/postgame_fix/ (01 island, 03 ferries, 04 Safari).

## Maps from other decomps
- data/hoenn_event_maps.json lists maps read from external/pokeemerald (and pokefirered, not used yet) as if they were
  pokeruby's: converter/gba.py `Repo.map_json` falls back to them, registers their layout, namespaces their tilesets
  `emerald:gTileset_X` (Emerald's General/Dewford/Rustboro/Fortree differ from Ruby's at some metatiles) and
  `map_folders()` knows their MAP_ ids (world.py, models_cave.py, allocate_*.py use it). Metatile behaviour numbers are
  the same in pokeruby and pokeemerald. FRLG's are not (its metatile attributes pack behaviour differently): a FRLG map
  needs its behaviour mapping in gba.py first.
- Labels: data/labels/emerald_islands.json (plan_map.py; a metatile that renders and behaves like Ruby's same id takes
  Ruby's label). work/agents/events/tools/labsheet.py draws the unclassified ids on the map.
- plan_map.py: for maps of another decomp, elevation-0 walkable tiles take the most common elevation of their walkable
  neighbours (Emerald's islands use elevation 0 freely; heights.py would cut them off).
- data/plans/<Map>.json and data/sapphire/<Map>.json: `python3 plan_map.py ../external/pokeemerald <Map>`,
  `python3 sapphire_data.py ../external/pokeemerald <Map>` (from converter/).

## Outdoor maps: warp-only groups
- data/hoenn_standalone.json groups: FarawayIsland_Entrance (bgm 385), FarawayIsland_Interior (385, forest),
  BirthIsland_Exterior (145, silent), NavelRock_Exterior (370; flat rocks retiled to mountain), NavelRock_Top (515, void
  border). Zones: `python3 converter/allocate_zones.py --events` (route pool, places 87-89 in data/hoenn_zones.json).
- "build" lists the 12 groups built before; the five island groups build with HOENN_STANDALONE=all. They fit now
  (a/0/0/8: 53,964 of 55,368 KB used with them, 1.40 MB free; islands ~0.53 MB, Navel Rock caves ~0.47 MB, every chunk
  under 57 KB): the lead sets "build" back to "all" when world.py is rerun. Raise RESERVE[8] before adding more islands.
- Ferry landings: matrix tile = Emerald tile + the group's origin (world.json "standalone"); events_lib.inc has the
  zones and origins (EV_*_ZONE, _OX, _OZ). Each island scene's script 1 is its landing (EV_ARRIVE_SCRIPT).

## Caves: Navel Rock
- `converter/allocate_interiors.py` third pass (event_rooms): zones 224-227, 229, 256-270 (data/hoenn_interiors.json).
- Recipes data/cave_layouts/NavelRock_*.json (work/agents/events/tools/navel_recipes.py): look d0, header_zone 515,
  'void' rects over Emerald's unreachable walkable filler, Bottom's waterfall column as a pool. Ladders:
  data/cave_tiles.json "emerald:gTileset_NavelRock". Build: `zsh b2tools/rebuild_interiors.sh NavelRock_...` then
  `python3 converter/gen_caves.py NavelRock_...`. Up4's ladder to the summit is a story trigger (Up4 (5,5), script 2 of
  0540: MapChangeCore to zone 233); the summit's ladder door goes back down to Up4.
- caves_check.py (sweep_caves): no chunk-size findings; north-wall holes are the builder's (reported to sweep_caves).

## Files
- Scenes: scenes/events_lib.inc (defines, `ev_legend_battle`, `ev_island_sailor`), LilycoveCity_Harbor_Events.inc
  (included by ch13's LilycoveCity_Harbor_Ch13.inc, guarded), FarawayIsland_Entrance/Interior(_init).inc,
  BirthIsland_Exterior(_init, _rock).inc, NavelRock_Exterior.inc, NavelRock_Top(_init).inc; story parts of
  0450/0451 (Bottom: Lugia), 0540 (Up4), 0406/0407 (Lilycove Harbor init: Briney's hide flag). Givers:
  players_house_1f_events.inc, SlateportCity_Harbor_Events.inc, FallarborTown_House1_Events.inc,
  Route114_LanettesHouse_Events.inc (each included, guarded, inside the giver's own script).
- Story objects: data/story/events.json (all "optional": skipped when the island or cave is not built).
- Ids: data/story_ids.json chapter "Events" (left for new ones: flags 2379-2394, works 0x411A, 0x4120-0x4122,
  0x4124-0x4125). Tickets: converter/gen_key_items.py EVENT (Black 2 items with field use 0 and a fitting icon).
- Test start: HOENN_TEST_CH13=1 + HOENN_TEST_CH13_EVENTS=1 (the three tickets, S.S. Ticket, Master Balls), 2 (Master
  Balls; Stern, Cozmo and Lanette shown: for the givers), 3 (as 1, Birth Island ignores the step limit). Talking to
  someone right after a sign's test warp into a room hangs (the warp script's context): walk out and back in first.

## Adding another legendary island (the user's later post-game legendaries)
1. Maps: list them in data/hoenn_event_maps.json (or use a pokeruby map). Label new metatiles (labels file + labsheet.py
   until plan_map reports nothing unclassified), run plan_map.py and sapphire_data.py.
2. Outdoor: a group in data/hoenn_standalone.json (bgm, border, ground, retile), `allocate_zones.py --events`, world.py
   (check the group's render: work/agents/events/tools/render_group.py). Caves: allocate_interiors.py, a recipe per cave
   (navel_recipes.py as a template), ladder ids in data/cave_tiles.json, rebuild_interiors.sh, gen_caves.py.
3. Ids in data/story_ids.json "Events" (hide/caught/defeated flags, the ship flag), `converter/gen_story_ids.py`.
4. Scene: scenes/<Map>.inc with `#ifdef SCENE_ENTRIES` (script 1 = landing), `ev_legend_battle`, `ev_island_sailor`;
   text in src/text/scenes/<Map>.txt; `converter/gen_map_content.py` makes the zone files. Story objects in
   data/story/events.json (legendary sprite: Black 2's own overworld model; sailor 359).
5. Ticket and ferry: a key item in gen_key_items.py EVENT, a giver (guarded include in the giver's script), the
   ticket's state in Sub_EV_LH_TicketStates and a menu entry in LilycoveCity_Harbor_Events.inc (h_sail_ferry to the
   landing). A legendary on an existing map (no island) needs only steps 3-4 and a story object.
6. Budget: work/agents/events/tools/budget.py <rom> (a/0/0/8 = map chunks); chunks < 110,600 B.

## Black 2 gaps
No harbour rooms (the ferry docks at the dock's end, as Southern Island; the harbour building itself is drawn since
2026-10-08: standalone res 481, buildings_audit, notes/WORLD.md "Invisible buildings"; Navel Rock's summit stands on its
rock over Black 2's clouds, res 487); Mew wanders visibly in the grass (no copy-
player-opposite move, no hiding in grass); the triangle is one white stone sphere that jumps (no 11 colours, no slide,
no shatter: the camera shakes); no camera pans at Ho-Oh/Lugia; no shade weather on the summit; the hidden Sacred Ash
is not placed; pedometer counts all steps (Emerald: island steps only; the ferry resets the puzzle anyway).

## Other event content (not built; proposals)
- Enigma Berry (R/S Mystery Event): Sapphire's own post-game script and text exist (Norman, Petalburg Gym,
  PetalburgCity_Gym_EventScript_ShouldGiveEnigmaBerry): give it after the Hall of Fame without the e-Reader check.
- National Pokédex (R/S Mystery Event `givenationaldex`): Emerald's own scene (Prof. Birch upgrades the Pokédex once the
  Hoenn Dex is complete) - needed anyway for many non-Hoenn legendaries.
- e-Reader Battle-e trainers (Mossdeep Game Corner, Sapphire's ValidateEReaderTrainer): the card trainers are not in
  the decomp; skip, or put fixed trainers there (needs the user's choice).
- Mystery Event ribbons (Country, National, Earth, World...): Black 2 has these ribbons; give them for milestones.
- Event Pokémon: Jirachi (Wishmaker, R/S bonus disc) as a Mossdeep Space Center post-game gift (the comet that wakes it);
  Celebi (Ageto) as a Petalburg Woods post-game encounter (the woods group exists).
- Altering Cave: built (postgame_maps, below).
- Pokémon Box Ruby & Sapphire bonus eggs (Swablu, Zigzagoon, Skitty, Pichu with special moves): from Lanette for
  Pokémon stored in the PC.
- Not events, still missing: Latias/Latios roaming after the TV news (ch13, no roamer command). Mirage Island: built (below).

## Post-game maps: Mirage Island, Altering Cave (postgame_maps, 2026-10-07)
Proofs: screenshots/postgame_maps/ (01-04 in DeSmuME, 05-07 renders).

**Mirage Island (Route 130).** Sapphire: Route 130's OnTransition swaps layout 46 (LAYOUT_UNREFERENCED_MAP, the island)
for 264 when IsMirageIslandPresent: the upper 16 bits of VAR_MIRAGE_RND (advanced once a day by the clock) equal the
lower 16 bits of a party Pokémon's personality (eggs count). Here:
- Layout: data/hoenn_world.json alt_layouts Route130 = map replace event 2 (work 0x4033 == 0x206: Black 2's own event-2
  entries patch matrix 175 only, no Hoenn zone uses it; no Black 2 script or code sets or reads uid 2), the island's two
  cells (19,10)/(20,10). Labels: data/labels/gTileset_Cave.json (the island's five Cave-tileset metatiles: stairs, cliff).
  `retile` (now also by "tiles"): Sapphire's flat top meets the sea along its north rim; those 16 rim tiles and the side
  columns are cliff faces, so heights.py raises the top by the stairs (64) and the stairs are the way up (outdoor_check
  accepts the lost Gen 3 surf landing on the rim).
- Rule (scenes/Route130.inc, zone init): a new 16-bit value each day (FLAG_DAILY_MIRAGE_RND, two Random 256 into
  VAR_MIRAGE_RND_H; Sapphire's LCG needs its RTC day counter, which scripts can't read), compared with every party
  Pokémon's PokePartyGetParam field 0. ODDS (user decision): only the low 7 bits are compared (MI_MASK 0x7F): 1 in 128
  per party Pokémon a day, about 1 in 22 days with six (Sapphire's 16 bits: 1 in 65,536; 0x3F would be 1 in 11). That field is not in Black 2's script whitelist: b2tools/patches/story.py
  GETPARAM_SWAP 0xa5 (Sp. Atk, read by no script) -> 0x00 (s0110 stores the u32 personality in a u16 work = & 0xFFFF).
- Showing it: a map replacement shows only when the field is built, and Route 130 is entered by surfing over a cell edge
  with the island's cells often already drawn. The zone init sets VAR_MIRAGE_REDRAW (1 show / 2 hide) when the island is
  in the wrong state; a map-script condition (scenes/Route130_init.inc) then fades out, sets the event, rebuilds the
  field in place with Black 2's FieldClose/FieldOpen (the player keeps surfing) and fades in. Nothing happens on days
  without a change. Tested: appears when crossing in, hides when no longer due, no redraw with a non-matching value.
- Liechi Berry: the daily berry spot tree_82 (52,9) (no change), placed at the island's height (story.py `alt_land`: an
  object on open sea in the main layout and land in an alt layout takes the alt cell's height), so it can't be read from
  the sea on other days. Wynaut: zone 240's land slots on the island's tall grass. Test switch HOENN_TEST_CHPM_MIRAGE=1
  (party[0]'s personality is the day's value), =2 (also shown at once on a warp in), =3 (party[0]'s + 1: no match).
**Altering Cave (Emerald, Route 103).**
- Map: data/hoenn_event_maps.json AlteringCave; allocate_interiors.py's event pass now follows warps that
  data/hoenn_map_additions.json adds to pokeruby maps (zone 271). Recipe data/cave_layouts/AlteringCave.json (d0, header
  zone 515 = Navel Rock's, levels 3:0 4:16, void); Emerald's rock piles 0x250/0x266 in data/cave_tiles.json
  "emerald:gTileset_Cave". Place name line 109 "Altering Cave" (Black 2's "Castelia Gate", same length: no text size change).
- Mouth: Emerald opens it after the game (Route103_OnLoad setmetatile 45,5/45,6 with FLAG_SYS_GAME_CLEAR) at the foot of a
  cliff its own Route 103 has a land strip under. data/hoenn_map_additions.json: LAYOUT_ROUTE103_ALTERING_CAVE = Sapphire's
  Route 103 + Emerald's two cave metatiles at (47,6) (the middle of Sapphire's cliff foot) + Emerald's land strip and shore
  metatiles (rows 7-8), and Route 103's warp 0 (47,6). alt_layouts Route103 = map replace event 7 (the game-clear event of
  Route 131's islet); `heights_box` keeps the rest of Route 103 at the main layout's heights. Black 2's cave mouth module
  draws the mouth (2 tiles, as the others).
- Tables: Emerald's nine (gAlteringCave1-9; Mystery Gift advances VAR_ALTERING_CAVE_WILD_SET). Black 2 has one wild file
  per zone header, so recipe "variants" = eight copies of zone 271 (272, 275, 276, 318, 320, 327, 328, 330: same room,
  entities, scripts; b2tools/patches/interiors.py copies the header with another encounter file; zone_effects counts them
  as ours: 318/320 had Black 2 gimmick 12), "encounter_files" 61-69 (Unova files no zone header of the build names).
  Route 103's door is Black 2's dynamic warp (dest id 0x100 -> GameData's next zone, saved with the game); Route 103's zone
  init (scenes/Route103_AlteringCave.inc, VMCall from Route103.inc) sets the next zone to the day's copy. Rotation BY DAY:
  Zubat (Emerald's own) until the first visit (FLAG_LANDMARK_ALTERING_CAVE, the cave's zone init), then the next table in
  Emerald's order each new day the player passes Route 103 (FLAG_DAILY_ALTERING_CAVE). Land rate 7 (3.9 %) -> rule 5 (5 %,
  no 4 % rule). Test switch HOENN_TEST_CHPM_ALTERING=n (game cleared, table n).
- Tested: post-game mouth, in (banner, Zubat on table 1), out, table 3 = zone 275 (Pineco).
**Glitch check (check_postgame, 2026-10-07; screenshots/check_postgame/).** Checkers on the own world/ROM vs the v14.1 world:
outdoor_check fast kinds 0 open (accepted walk 204 -> 220: the island's north rim, door 12 -> 13: Route 103's mouth before
the game, tex 51 -> 56: lip/foam slivers of the alt cells), layer/view on alt_Route130/alt_Route103 0 holes, 1-2 pixel back-
face specks only (north rim, stairs' sides; Route 103's cells as HEAD's), check_exits 0, npc_check 0 over. DeSmuME: surfing
into Route 130 shows the island; stairs, rim, tall grass (Wynaut, Shadow Tag: fought), the island still there after the
battle; Liechi Berry; with the island set but not due (work 0x4033 poked) entering Route 130 hides it, surfing over its old
beach works; the redraw run in view (VAR_MIRAGE_REDRAW poked) shows and hides it around a surfer. Continue never runs a
zone init (ov035 EventFieldContinue_Callback: LoadZone, no FieldMapControl_InitSpawn) [code], so a save on the island
keeps it, as Sapphire's saved map view. Route 103: the mouth from four sides and the water, the strip (surf off its west
end and land), in/out. Left by design: Sapphire's side cliff bands are low solid ground beside the 64-unit face (heights.py
cliff tiles take the low side, as Ever Grande's); the north rim lost its Gen 3 surf landing (outdoor_check ACCEPT).
In-game saving hangs on an empty message box in this harness on HEAD's v14.1 ROM too (not a post-game map issue).

