# Hoenn town map (town_map agent, 2026-10-08)

User request: "the town map in Pokémon Centers and code the town map to be Hoenn and not Unova". Black 2's town map app
now shows Sapphire's region map everywhere it opens: the Town Map key item, Fly (party menu and the Town Map), the
Pokémon Centers' wall maps and the player's bedroom map. Patch: `b2tools/patches/town_map.py` (last in the patch list);
wall maps: `b2tools/centers_rooms.py` `region_map()` + the 15 `*_PokemonCenter_1F.s` and 0782/0786 (Script_7); test kit
`src/field_scripts/scenes/town_map_test.inc` (HOENN_TEST_CHTM). Proofs: `screenshots/town_map/`.
Tags: **[code]** read in the dsd disassembly of ov144/ov012/ov036/ov298/ov303 (decomp symbols and relocs), **[bytes]**
read in the decomp's extracted files, **[test]** seen in DeSmuME.

## 1. Black 2's town map [code][bytes]

**The app.** FIELD_APP 8 = overlay 144 (`townmap.c`, `townmap_grh.c`), 0x0219CE80-0x0219F960 (10,976 B, compressed
8,688 B), proc table `data_ov144_0219f774` (init 0x0219CE80, main 0x0219D1E4, end 0x0219D140). It loads ov139 (0x8B,
a UI library) itself. While it runs the field (ov036) is unloaded (ov036 covers the same RAM).
- Param (`TownMapParam`, `event_field_proclink.c`): +0 mode, +4 result, +8 zoneId, +0xA escape-rope zone, +0xC/+0x10
  extra fly words, +0x14 gsys. **Mode 0** = "Fly to where?" (A on a flyable place: result 2, zone at +8), **1** = view
  only, **2** = fly anywhere (every place flyable, Join Avenue's service). Init 0x0219CEFE reads it; `mode != 1` makes the
  "Fly to where?" window (0x0219CF6x); the main loop 0x0219D2D4 flies in modes 0/2.
- Entry points: `func_ov012_0215bf8c` (FIELD_APP 8 create; mode 0 only from the party menu, appId 0, or the Bag's Town
  Map via hm_free's `HoennTownMapMode` at ov012 0x0215BFDC: HM02 + Feather Badge + a zone with Fly); result 2 -> event 4
  (Fly) with the zone (`func_ov012_0215bff8`). Script command **CallPlaceSelect var, var** (644, ov036
  `s0284_CallPlaceSelect` 0x021AE244) runs the same app as a subprocess with mode 0 and copies result/zone into the vars
  (Black 2 uses it only for Join Avenue's taxi, 1280.s). The Y-registered Town Map opens view-only.
- Art: **a/0/8/4** (ARC 84), loaded by `func_ov144_0219f414`: NCLR 0 = 16 x 256-colour extended palettes (both slots of
  BG2/BG3 get it), BG3 (prio 3, 8bpp extended affine, screen 0x2000, chars 0x18000) = NCGR 7 + NSCR 16 = the painted map,
  BG2 (prio 2, same kind, screen 0x1000, chars 0xC000) = NCGR 5 + NSCR 17 = routes, town circles and landmark squares;
  bottom-screen BG0/BG1 = text and the bar; top screen BG5 = NCGR 6 + NSCR 15 (the round frame). The map is drawn 1:1 at
  screen (0,0) (256x168 visible above the bar) and "+" zooms it 2x by scaling BG2/BG3 around (128,96)
  (`func_ov144_0219e8e0`; scroll bounds x -128..128, y -72..96 at 2x). Cursor (`func_ov144_0219d9cc`): x 0..0xF8,
  y 8..0xA8, D-pad 3 px/frame, touch.
- Sprites: NCGR 8 (4bpp, 1D 128K: a cell's tile number counts 128-byte units), NCER 12 (25 cells), NANR 19 (19 anims),
  NCLR 2 (OBJ palettes 0-4). Anims: 1/2 town dot (cells 4/5), 3 selected landmark (6), 5 the selection ring, 6 the player,
  13 small dot, 14/15 green/red square (20/21), 16-18 rings (22-24). **32 affine matrices**: more than ~25 icons on screen
  at once draw as solid boxes (tested with 41).
- Locations: **a/0/8/5** file 0 = 85 records x 54 B (27 u16) [bytes, decoded with the code]:

  | u16 | meaning | used by |
  |---|---|---|
  | 0 | zone (name = its header's place, system text 109; Fly target) | ov144, ov298, ov303 |
  | 1 | snap radius (the cursor drifts to fields 4,5 when it rests inside) | 0x0219E5DC |
  | 2,3 | icon point (also the player marker) | 0x0219E6BC, 0x0219E7D4 |
  | 4,5 | snap point (also the cursor's start and the selection ring) | 0x0219DCDC |
  | 6,7 / 8,9 / 10 | hit capsule: segment end points and radius (`CalcCapsule_HitSphere`) | 0x0219E3BC |
  | 11 | type: 0 town (dot when visited), 1 route (no icon), 2 landmark (red square when selected), 3/4/5 other icons (4/5 shown unless the show flag hides them; 5 by the visited flag) | 0x0219E18C |
  | 12 | can fly (with the fly flag set) | |
  | 13,14 | words copied to the Fly event (0 in Black 2) | 0x0219D46x |
  | 15 | fly / visited flag (0xFFFF none) | `func_ov012_02160f74` (0xF000-0xF002 special) |
  | 16 | show flag (0xFFFF always; unset = hidden, no hit) | |
  | 17-23 | system text 377 lines: description, facilities (0xFFFF none; facilities only when visited) | 0x0219EB6C |
  | 24-26 | Pokédex area page: highlight anim, x, y (ov303 0x021A2D3C adds 24 to y) | ov298, ov303 |

  The location module (`func_ov144_0219dd78`) makes 0x54 = 84 entries of 0x44 B from records 0..84, skipping zone 424
  and swapping zone 0 for the next record on White 2; zone 490 (Join Avenue) has special code. The player's location:
  `func_ov144_0219e118` = the record whose zone is `func_ov012_02160eb4(zone)` (the zone header's parent, with Unova
  special cases). `func_ov144_0219f718` loads the records (`GFL_ArcSysReadHeapNewLZ(0x55, 0)`), `f730` reads a field,
  `f73c` finds a record by zone (85-record loop).
- **The Pokédex's area page shares all of it**: ov298 (`zukan_detail`) and ov303 load a/0/8/4's BG files 0/5/7/16/17
  and OBJ files 2/8/12/19, call ov144's `f718`/`f730`/`f73c` (so ov144 is resident with them) and read the habitat
  archive **a/1/7/6** (176): one file per species (684 x 345 B) = 1 byte + 4 seasons x (1 byte + 85 bytes, one per
  town-map record).

## 2. What the patch does

**Art (Sapphire's own pixels, 1:1).** Sapphire's region map (pokeruby `graphics/pokenav/region_map.png` 8bpp tiles +
`region_map_map.bin`) is a 32x20-tile picture: exactly the DS screen's width, so it needs no rescale; it sits 2 tiles
down (Y0) so the 168-px map area holds it (Sapphire's cursor area at y 32..152), Sapphire's sea tile around it, its own
palette (indices 113-140 of extended palette 0; 233 tiles instead of Black 2's 704). BG2 is empty except Black 2's own
landmark square (its pixels, read from its BG2) at each landmark. The town icons are **Sapphire's fly-target icons**
(`fly_target_icons.png`: pink = visited, grey = not yet, dot / 2x1 / 1x2 capsule as the town) as 6 new cells/anims
(NCER 12 cells 25-30, NANR 19 anims 19-24, NCGR 8 units 56-61, colours in OBJ palette 4 slots 2-5/9-12, unused by Black
2's cells); Black 2's own cells are unchanged (the Pokédex draws with them). The NARC keeps its size (padded).

**Locations: 85 records** (84 + one harmless filler: Black 2's loops and the habitat format are made for 85) in a/0/8/4
file 21, after the art, Sapphire's region map sections (`region_map_sections.json`,
cursor grid `region_map_layout.h`), in hit order: 25 landmarks, 16 towns, 34 routes in 43 runs.
- Towns (type 5, anims from field 26 by the patched case 5): capsule over their grid cells, Fly with Sapphire's own
  `FLAG_VISITED_<TOWN>` (set by the ported OnTransition scripts), "Pokémon Center" (system 377 line 5) for the 15 with
  one; no description (Sapphire has none).
- Routes (type 1): one record per straight run of their grid cells (Route 124's 4x3 = 3 runs, Route 126 around
  Sootopolis = 4), radius 5; the main record holds the marker.
- Landmarks (type 2, Black 2's square on BG2): Granite Cave, Mt. Chimney (its 2x2 grid block hovers), Safari Zone,
  Petalburg Woods, Rusturf Tunnel, Abandoned Ship, New Mauville, Meteor Falls, Mt. Pyre, Aqua/Magma Hideout (line 69 per
  version), Shoal Cave, Seafloor Cavern, Victory Road, Cave of Origin, Fiery Path, Jagged Pass, Sealed Chamber, Scorched
  Slab, Island Cave, Desert Ruins, Ancient Tomb. Type 4 (sprite, hidden by a flag): **Battle Tower** (Sapphire:
  shown and flyable with FLAG_LANDMARK_BATTLE_TOWER), **Southern Island** (FLAG_LANDMARK_SOUTHERN_ISLAND), **Sky Pillar**
  and **Altering Cave** (FLAG_SYS_GAME_CLEAR: their islet / mouth appear after the game in this build). Not on the map,
  as Emerald (`sMapSecIdsOffMap`): Faraway Island, Birth Island, Navel Rock (no marker there). Mirage Island is Route 130.
- Ever Grande's second Fly point (Pokémon League with FLAG_SYS_POKEMON_LEAGUE_FLY) is not made: one zone, one fly point.

**File 21 layout** (hoenn_pokedex reads it; `town_map.read_file21(files)`): records at 0 (85 x 54 B) | zone table at ZT
| refine table at REF (u16 count, u16 0, 20-B entries: zone, ox, oz, flags, section x, x thresholds[4], y thresholds[5],
section y) | icon anims at ANIM (u16 per record) | 16-B trailer 'TMAP', N, ZT, zone count, REF, ANIM, 0. Fields 24-26
hold Black 2-compatible Pokédex values (anim 0 towns / 1 others, icon point - 8) for phase 2.

**Zone table** (615 bytes): every zone header -> record. A zone's location is the region map
section of its pokeruby/pokeemerald map (`map.json`), rooms included (fixes headers whose place is wrong, e.g.
OldaleTown_House1/2 and Lilycove's elevator say "Littleroot Town"); underwater -> the route above (region_map.c
`sUnderwaterMaps`); PWT zones 191-193 -> Battle Tower; zones of no Hoenn map: by their place name; link rooms and the
event islands: none.

**Refine table** (33 routes): Sapphire's `RegionMap_InitializeStateBasedOnPlayerLocation` (x / (map width / section
width), clamped; Route 114's x = 0 below row 0; Routes 121/126's own thresholds) as thresholds in map tiles, from the
player's position (PlayerState +4/+0xC, tile = fx32 >> 16) and the map's world origin (world.py `compose`: layout tile +
margin + shift + pad_north). Rooms and caves: the town's / cave's point.

**Code (ov144, inside its own size; compressed to exactly 8,688 B like Black 2 with a tuned filler, so the ROM file
table is unchanged):**

| Where | Black 2 | Now |
|---|---|---|
| 0x0219CF18 init `bl func_ov144_0219f718` | B2 records | `HoennLoad` (0x0219ECFC): mode 0 in a zone without Fly -> mode 1 (view: the wall maps' CallPlaceSelect; party Fly and the Bag's Fly only happen where Fly is on), records from a/0/8/4 #21, refine |
| 0x0219DDA4 `movs r0, #0x54` / 0x0219DE3C `cmp r4, #0x55` | 84 entries of 85 records | 85 / 85 (none skipped) |
| 0x0219F71C in `func_ov144_0219f718` | a/0/8/5 #0 | unchanged (POKEDEX_RECORDS = False; True = a/0/8/4 #21 for the Pokédex too, phase 2) |
| 0x0219E118 `func_ov144_0219e118` | record by parent zone | record from the zone table |
| 0x0219E2B8 case 5 of the type switch | anims 0x10/0x11/0x12 | `Type5Anims`: field 26 (visited \| not visited << 5) when set |
| 0x0219ECF8, 0x0219EBD4, 0x0219F13E | Join Avenue (zone 490) paths | jumped over, code zeroed (the free space above) |

**Fly landing.** Black 2 lands on the zone header's fly point (ov033 EventFly, `LoadZoneSpawnInfoCheckRail`), which
world.py put near each map's middle (4-35 tiles from Sapphire's spot). The patch sets the 15 towns' and the Battle Tower's
header fly point to **Sapphire's heal location** (`heal_locations.json`, the tile in front of the Center; checked
walkable and in the town's zone in work/world), as Sapphire's Fly (`sub_8053538(heal location)`). Teleport and the Escape
Rope's fallback use the same point (ov035), as Sapphire's Teleport. Littleroot keeps world.py's point between the houses.
`HEAL_LANDING = False` turns this off.

**Wall maps.** Sapphire's `EventScript_RegionMap` (msgbox Common_Text_LookCloserAtMap, fade, `special
FieldShowRegionMap`): the Centers' map (centers_rooms.py `region_map()`) and the bedroom map now show the line, then
`FadeOutBlackQ / FadeWait / CallPlaceSelect 0x8000, 0x8001 / FadeInBlackQ / FadeWait`. Every Center 1F and the
bedrooms have Fly off, so the map opens in view mode.

## 3. Limits
- Records: up to 255 with this code (immediates); 85 for the Pokédex's habitat format (85 bytes per season).
- Icons: <= ~25 affine sprites on screen (32 matrices, also cursor/marker/ring): landmarks therefore on BG2.
- BG3: 0x8000 B of chars reserved (512 8bpp tiles); Sapphire's picture uses 233.
- a/0/8/4 must stay 207,232 B (no RESERVE): NCGR 7 shrank by ~30 KB, file 21 is 5.8 KB.

## 4. Testing
- Done (2026-10-08, screenshots/town_map/01-11, review sheet 00): Town Map item (fly mode with HM02 + badge, view mode
  without), markers in Littleroot, Route 111 north/south cells, Granite Cave, Oldale's Center; Center wall map (view);
  Fly from the Town Map to Slateport and from the party (Swellow) to Fortree, both landing on Sapphire's heal tile
  (267,340) / (373,67); zoom; post-game Battle Tower icon + Fly; save -> Continue (save_check's cycle.py). Layout:
  Sapphire = Ruby = the v15.2 releases (rom_layout_diff: LAYOUT IDENTICAL; ov144 tuned to 8,688 B, a/0/8/4 padded).
  Not tested: the Pokédex area page with the new art (phase 2), underwater markers, the bedroom map.
- Build: `OUT=rom_test HOENN_TEST_CHTM=1 HOENN_TEST_WARP=563,6,7 zsh work/agents/town_map/build.sh`; state:
  `work/agents/world_fixes/tools/mkstate.py`; runs: `work/agents/town_map/tests/tm.py ROM STATE OUT ZONE,X,Z[,STAGE] MOVES`
  (room_look's sentinel method; MAP = Bag -> Key Items -> Town Map -> Use; stages in town_map_test.inc).
- Quick art iteration: `tools/inject.py ROM` rewrites a/0/8/4 in a built ROM (same size). `tools/ovsize.py` measures
  dsd's compressed ov144 (recheck SIZE_FILLER after any code change). `tools/preview.py` renders the map offline.

## 5. Phase 2: the Pokédex area page (dex_area, 2026-10-11: built and tested; the plan below it is history)
Code and data: `b2tools/patches/hoenn_pokedex.py` (its docstring has the findings), shapes in `town_map.dex_highlights`.
- **Records.** ov298 (area page), ov303 (Habitat list map) and ov308 (C-Gear beacon detail) call `func_ov144_0219f718`
  and `f73c`: their calls now go to ITCM `DexLoadRecords` (a/0/8/4 #21) and `DexFindRecord` (the zone table, without
  Black 2's parent-zone mapping, so rooms and caves find their town or cave); ov144 is untouched (its tuned size), so
  `POKEDEX_RECORDS` stays False. ov298's 85 habitat zones (`data_ov298_021ac544`) = the records' zones: a route's runs
  share one habitat byte.
- **Habitat a/1/7/6** (file = species - 1; byte 0: 1 = one table for all seasons; per season 1 byte (1 = "Area Unknown")
  + 85 bytes): bits are Black 2's encounter groups (0x01 grass/cave, 0x08 surf, 0x20 fishing, ...), made from the
  built game's own Hoenn tables (a/1/2/7 of the version being built), so Sapphire's and Ruby's tables each give their
  own page. The bottom screen's three icons (walking, surfing, fishing) light for the place picked on the map. Rock
  Smash and Old/Good Rod tables are not in this game, so they are not shown: the only species this hides compared with
  Sapphire's own area screen are **Nosepass and Graveler (Rock Smash only: no wild place in this game)**. Wynaut is
  hidden as in Sapphire. 117 of species 1-386 have a place (both versions).
- **Highlights**: a/1/5/7 NCGR 15 / NCER 29 / NANR 46 / NCLR 5 rebuilt from Sapphire's `area_glow.png` (tile 0x10, the
  glow, on a town's cells or a route run) and `area_marker.png` (dungeons); 10 cells; semi-transparent so Black 2's
  pulse is Sapphire's glow; the archive keeps its size. Show-flag places (Sky Pillar, Altering Cave, Battle Tower,
  Southern Island) only highlight when their flag is set (Black 2's rule = Sapphire's sLandmarkData).
- **Roamers**: the habitat read (ov298 0x021a5c26) goes through `HabitatRead`: for the seven roamers the page shows
  where the roamer is now (Sapphire's area screen), "Area Unknown" when it is not roaming.
- Tested (screenshots/dex_area/, both versions, new games + test kit `HOENN_TEST_CHTM=1` stage 0x7A05 in
  scenes/town_map_test.inc; harness work/agents/dex_area/tests/dex.py): list, INFO with the A page flip, AREA for a
  route, water, cave and roaming Pokémon, "Area Unknown", the place details, National list, search, Habitat list
  map (no crash), save -> Continue -> the same pages, a catch's registration screen (Ruby); Habitat list (stage
  0x7A06: every place visited, HM03 + Super Rod): only Route 101 after walking there from a fresh kit, all 57 places
  with the kit, Slateport, Route 103/104, Granite Cave, Altering Cave, Jagged Pass pages, save -> Continue (both versions).
- **Habitat list** (the Pokédex's HABITAT button after the National Dex; ported 2026-10-11, the user's choice): Black
  2's 57-place table (four copies: ov302, ov303, ov298, ov036) and its pages a/2/9/6 are Hoenn's: the map sections
  with wild Pokémon in Sapphire's region-map order (Dewford, Pacifidlog, Petalburg, Slateport, Lilycove, Mossdeep,
  Sootopolis, Routes 101-134, then the dungeons to Sky Pillar and Altering Cave); 58 sections for 57 places, so Ever
  Grande City's water is left out (all its Pokémon and kinds are on Route 128). Pages come from the AREA page's data
  (per version). A place is listed once visited, as in Black 2: 57 bits in works VAR_HABITAT_VISITED_0-3 (no free flag
  was left in data/story_ids.json), set on every zone entry by `HabitatDiscover` (rooms and caves count for their town
  or cave); Black 2's surfing / fishing kinds unlock with HM03 / a rod in the Bag (flags 0x987 / 0x985, Black 2's
  meaning). Seen/caught per place and kind and the stamps ("!") are Black 2's own code on these pages (checked: the
  "!" places match the kinds whose Pokémon are all seen). Old saves list a place after their next visit to it.
- **Not done**: the catch screen's A page flip
  (`CaptureKeys`, ov297 0x021f4420) is never reached in a battle catch: there the battle UI (ov168
  func_ov168_021eecbc) reads the keys and A closes the entry as in Black 2.

### Phase 2 plan (2026-10-08, kept for reference)
It is the same art and records: since this patch the area page draws Sapphire's map, but `f718` still gives it Black
2's 85 Unova records and a/1/7/6 Black 2's Unova habitats, so its markers sit at Unova places (it never had Hoenn data:
before, it showed Unova). To finish:
1. Done in the data: 85 records, private data out of fields 24-26 (Black 2-compatible defaults there). To switch:
   `POKEDEX_RECORDS = True` (f718 loads a/0/8/4 #21 for ov298/ov303 too), retune SIZE_FILLER (tools/tune.py), test the
   area page. hoenn_pokedex (a98ffe8acecbdea4f) is writing a/1/7/6 from Hoenn encounters keyed by these records.
2. Highlights: ov298/ov303 draw each place with an anim of field 24 (Black 2: 0 towns, 1 landmarks, 2-21 route-shaped
   highlights) from the Pokédex's own sprite archive (a/1/6/5, still to be decoded). Hoenn needs one highlight per
   Sapphire section: from Sapphire's area screen (pokedex_area_screen.c fills the section rectangles), as new cells.
3. a/1/7/6: per species, the record bytes for every place it lives (data/hoenn_encounters.json -> zone -> zone table
   -> record; the same for the 4 seasons; the bit meanings (1, 3 seen) to be read in ov298), file sizes unchanged.
4. Roamers (user, notes/RESUME.md): b2tools/patches/roamers.py keeps each roamer's current zone; the area page's
   "roaming" display (Black 2's Thundurus/Tornadus) needs reading in ov298 and a hook giving it the Hoenn roamer's zone
   -> record.
Estimate: a separate job (2-3 working sessions: the highlight art and the ov298/ov303 reading are most of it).

## 6. Not done / for the lead
- **No one gives the Town Map** in this port (Sapphire's map is in the PokéNav; our PokéNav is the Xtransceiver).
  Proposal: Mr. Stone's `h_give_pokenav` also adds ITEM_TOWN_MAP (silently, as part of the PokéNav), or the Bag's
  PokéNav "Use" opens the town map.
- Black 2's descriptions (system 377) stay unused; Sapphire has none.
