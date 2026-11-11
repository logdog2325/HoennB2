# The DexNav (dexnav, 2026-11-09; ORAS look (variant A, picked by the user), tested on the combined Emerald ROM 45c397bf)

Omega Ruby / Alpha Sapphire's DexNav in all three versions, made of Black 2's own pieces: the field's touch screen (in
place of the NoGear screen Hoenn always showed), a page of the PokéNav, Black 2's phenomena (shaking grass, a dust cloud,
rippling water) as the hidden Pokémon, and Route 101's tutorial with the rival. Research: work/agents/dexnav/
(bottom_screen.md, wild_battle.md, dex_audit.md, REPORT.md).

## What the player sees
- **The Lab** (Pokédex scene, 0792 Script_12): right after the rival's five Poké Balls, Birch gives the DexNav (key-item
  jingle, "<player> received the DexNav!"), the touch screen wipes from NoGear to the DexNav, Birch explains (the rival
  will show you). A save that got its Pokédex before this existed gets the same lines from Birch when talked to (Script_7,
  lab state 5).
- **Route 101's tutorial**: the first step into Route 101's tall grass afterwards: "!" over the player, the rival (May for a
  boy, Brendan for a girl, Emerald too) runs up from behind, explains the screen, gives two Poké Balls if the Bag has none,
  and the DexNav puts a Poochyena (Route 101's level, knowing Thunder Fang, Ice Fang or Fire Fang at random: its egg moves
  in a/1/2/4) in shaking grass 3-5 steps away. Walking onto it starts a normal wild battle (catch it or knock it out).
  After it the rival comments (caught / fainted / ran) and walks back the way it came. A blackout ends the tutorial with
  no lines. Leaving Route 101 before the battle: the spot comes back at the next step in Route 101 (rival gone).
- **The touch screen** (once VAR_DEXNAV_STATE != 0), Omega Ruby / Alpha Sapphire's look (the user picked variant A of
  screenshots/dexnav/mockups 2026-11-09; our own art, b2tools/dexnav_art.py), three views:
  - **Area**: a snapshot of the place's Gen 3 map (its own tiles, b2tools/dexnav_snapshots.py) in an orange PokéNav
    Plus-like frame, the "DexNav" tab, each species' icon standing on a tile of its kind (land: grass, cave floor, sand;
    water: surfable water): caught = colour, seen = dark silhouette, not seen = "?" (tapping it: "You haven't seen this
    Pokémon yet."). The place's name on a dark strip (window 0, brightness down), a crown once every species is caught,
    a pulsing red ring over the species being searched for. Tapping the map: a progress line ("There are Pokémon here you
    haven't caught yet!" / "Almost done! ..." / "Well done! ..."). A place without wild Pokémon: a red panel with a Poké
    Ball and "No wild Pokémon live here." The bar: POKéNAV (once the player has it, FLAG_SYS_POKENAV_GET), or the back
    button on the PokéNav's page.
  - **Found Pokémon** (an icon tapped): the species at double size (its icon, an affine sprite) in a teal ring, Name,
    Type (Black 2's type icons), Search Level, SEARCH and back; the stripes go from grey to orange with the search level.
    A failed search returns to the area with its line (go surfing, not on the water, nothing found).
  - **Hidden Pokémon** (while it hides, also during the tutorial): its silhouette on a radar, Search Level, Level always,
    Potential (gold stars = perfect IVs) from search level 5, Ability from 10 ("!" = hidden ability), First Move from 25
    ("!" = egg move); "???" before that. Back returns to the area (the search stays; tapping its icon shows it again).
    After the battle, a flee or a lost spot: the area with its line.
  The bonuses, the ability and the first move are rolled when the search starts (dexnav.c RollBonuses), so the Hidden
  view shows what the battle gets. No touch while a script runs.
- **The PokéNav**: a DEXNAV button (sixth, before Switch Off) opens the same screen as a page (D-pad: a teal cursor over
  the icons, A = Found / SEARCH, B = back; a started search closes the PokéNav).
- **A search**: land species need the player on land, water species need surfing ("Go surfing to look for this one").
  The spot is a tile of the group's kind (grass/sand/cave floor, or sea/pond) 3-5 tiles away (2 if nothing else), in the
  player's zone, at the player's height, with nobody on it, and reachable on foot (or by surf) within 7 tiles (a BFS in
  dexnav.c, so never behind a wall or a ledge); else "Nothing could be found here." No random battles while a
  spot is out. Running (B) or the Bike within 3 tiles: it flees ("It ran off!"), chain 0. A zone change, a script or an
  NPC stepping on it takes it away (chain 0).

## Bonuses (our numbers, roughly ORAS's; dexnav.c)
| Search level | Perfect IVs | Hidden ability | Egg move | Item 2 (5% wild) |
|---|---|---|---|---|
| 0-4 | 10% one | 0% | 20% | 5% |
| 5-9 | 1 | 5% | 30% | 10% |
| 10-24 | 1 (20%: 2) | 10% | 40% | 15% |
| 25-49 | 2 | 15% | 50% | 20% |
| 50-99 | 2 (30%: 3) | 20% | 60% | 25% |
| 100+ | 3 | 25% | 60% | 25% |
- Search level: +1 per DexNav battle won or caught (max 255). Hidden ability only for species with a distinct one; the egg
  move goes in the first empty move slot, else replaces the first move.
- Shiny: extra tries (1/8192 each) past the game's own (1, +2 Shiny Charm): chain/5 (10 from chain 50) + level/50, +20 at
  chain 50 and 100. Chain: +1 per DexNav battle of the same species won or caught; running, fleeing, losing, a lost spot or
  searching another species resets it.
- Battle: a normal wild battle (normal wild music; catchable; Synchronize/Cute Charm as usual), the species' level range
  in this zone's table.

## Data and save
- Search levels: the Dream Radar block's unused bytes (`DreamRadarSave.padding09`, inside its CRC; only a new game writes
  them): [0] = 1 once written, then a byte per species in the order of b2tools/patches/dexnav.py (Hoenn dex #1-#202, then
  EXTRAS, APPEND ONLY; 220 of 230). Old saves read 0 everywhere.
- Works (Ch1's reserve): VAR_DEXNAV_STATE 0x405F (0 none, 1 given, 2 tutorial search out, 3 done, 4-6 the tutorial
  battle's result for its last script), VAR_DEXNAV_CHAIN 0x4060, VAR_DEXNAV_CHAIN_SPECIES 0x4061.
- The spot is Black 2's own EncountState.rareSpot (not saved); the search's state is in the resident section's .bss.

## Code and files
| Where | What |
|---|---|
| decomp `include/hoennb2/dexnav.h`, `src/hoennb2/resident/dexnav.c` (resident, ~5.8 KB) | list, search, bonuses (+ ability, first move), battle event, step hooks, row 5's functions, script ops 0x60-0x7F |
| decomp `src/hoennb2/dexnav/dexnav_screen.c` (overlay 349, 7.5 KB, in the C-Gear's slot 0x021EA860-0x021EEC80) | the three views |
| decomp `src/ov036/field_subscreen.c` | row 5 (BLANK_STANDBY_2) -> HoennB2_DexNavScreen_* under #if HOENNB2 |
| decomp `src/ov036/fieldmap_event.c` | CheckPhenomenonEvent's two calls, CheckCallRandomEncounter's call |
| decomp `src/ov036/effect_encount.c` | HOENNB2_STATIC: IsPositionOccupiedByActorAny, EffectEncount_CreateSpotEffect |
| decomp `src/hoennb2/resident/ext_cmd.c`, `include/hoennb2/ext_cmd.h` | row 3 (0x60-0x7F) of the extension command |
| decomp `src/hoennb2/pokenav/pokenav.c`, `pokenav_local.h`, `resident/pokenav_event.c` | the PokéNav page; its memory check counts the DexNav's share |
| decomp `tools/hoennb2/link_overlays.py` | SUBSCREEN_SLOT_OVERLAYS: overlay 349 at AFTER(OV074..OV078) |
| `b2tools/dexnav_art.py` | the views (ORAS look, Black 2's font for labels), pieces, sprites, the text; the PokéNav menu's DEXNAV button (Gen 3's) |
| `b2tools/dexnav_snapshots.py`, `data/dexnav_snapshots.json` | each wild table's Gen 3 map snapshot and icon places; crops (Route 111's two views with a frame bar between them: the desert's rocks and the pond by Mauville; Route 115's window) and stand-ins (Route 130's Mirage Island land, Shoal Cave's low-tide rooms' water) |
| `b2tools/dexnav_check.py` | the hardware budgets, run by the patch in every build (standalone: `python3 b2tools/dexnav_check.py`) |
| `b2tools/patches/dexnav.py` | text to a/0/0/2; views + snapshots to the end of a/0/0/8 (uncompressed, no RESERVE change); gHoennB2DexNav; overlay 349 in the table |
| `b2tools/pokenav_art.py`, `b2tools/pokenav_check.py` | the PokéNav menu's sixth button |
| `b2tools/patches/scripts.py`, `text.py`, `build_rom.py` | -D HOENN_DEXNAV, overrides_dexnav.json, the patch, all only with our C |
| `src/field_scripts/common/dexnav_defs.inc`, `scenes/Route101_DexNav.inc`, `scenes/BirchLab_DexNav.inc`, 0634, 0792 | scripts |
| `src/text/overrides_dexnav.json` | every DexNav script line (approved by the user 2026-11-09), in Route 101's text file 516 |

Text rule: a line break inside a line is the two characters `\n` in the JSON (a real one splits the file's lines and
shifts every later line; patches/text.py now refuses it). The screen's own lines are dexnav_art.py TEXT (0-34, all
approved 2026-11-09).

## Budgets (b2tools/dexnav_check.py, 2026-11-09, all three versions)
- Characters (bank H: 768 for the three BGs): area 346 (82 art + 131 the largest snapshot + 132 windows), Found 247,
  Hidden 471. Palette lines (0-14 art): area 9-10, Found 2, Hidden 5.
- Snapshots: Sapphire / Ruby 95, Emerald 102 (the no-wild panel included); at most 131 characters and 8 lines each;
  286 KB / 308 KB uncompressed in a/0/0/8 (10.4 MB free in its fixed size). Every one is read in 2 KB parts.
- Sprites: at most 11 icons a zone (Emerald's Safari Zone, its post-game twin counted): 14.8 of 16 KB sub OBJ VRAM with the
  ring, the cursor, the big icon and two type icons; 8 of 16 OBJ palettes.
- HEAPID_FIELD_MENU, measured (45c397bf, Route 101 / Granite Cave): area view 39.1 KB held (22,268 B free of 61,384),
  Found 35.3 KB, Hidden 37.0 KB; the X menu frees it first. NEED_MENU_HEAP (40 KB) unchanged; dexnav_check.py's
  estimate is calibrated on these.
- A zone change (DeSmuME's emulated time, timer 0): on b8add5e3 (one table lookup a file, icons two a frame) into
  Oldale 27.9 ms in one frame (the snapshot 5.3 ms, the rest printing "No wild Pokémon live here.": the field's font
  reads each letter from the card), back into Route 101 19.4 ms (snapshot 4.5 + two icons 4.5 + the name) then 2.4 ms;
  a cave's ladder is a map change (the screen made again behind the fade: snapshot 4.7 + icons 6.7 ms). Since then
  (offline): the no-wild line is drawn into its panel's art and the place's name prints through a print queue, 2 ms a
  frame (the screen made, or back from Found / Hidden: at once), so a frame's share is the snapshot's or two icons'.

## Memory (measured 2026-11-09 on the v19.1 / v2.1 release ROMs, NoGear; work/agents/dexnav/tools/meas.py)
- HEAPID_FIELD_MENU 61,368 B free of 61,384 (house, Slateport with 29-32 actors and the follower, talking, a Mart's Buy
  list); the X menu takes 9.6 KB of it. The DexNav keeps ~38 KB (estimate: font, windows, cell actors), ~46 KB at Init.
- Field heap: nothing new (3 BG screens, as NoGear's 3). Arena: the resident section + overlay 345 grow ~6 KB.
- Cell actors (field): 10/72 char, 4/64 palette, 4/64 cell resources with NoGear; sub OAM unused; the X menu uses 8 chars,
  12 KB of sub OBJ VRAM. The DexNav: up to 18 actors, 12+1 char resources (~14 KB sub OBJ VRAM at most).
- Tiles (ROM terrain): tall grass 0x04/0x24 -> shaking grass; cave floor 0x0a/0x84 -> dust; sea 0x3f/0x16 and pond
  0x3d/0x56 -> ripples; Route 111's deep sand 0x0c/0x0c -> dust (our own mapping).

## Tests (2026-11-09, combined Emerald test ROM 169adf74, girl and boy; work/agents/dexnav/tools/dn.py, ff.py)
Lab gift, old save at lab state 5, Route 101 screen + silhouettes, tutorial (no Poké Balls -> two; Poochyena with a Fang;
caught / knocked out / ran lines), a search with chain 2 and a flee, cave dust (Granite Cave), sea ripples (Route 104),
land-while-surfing message, PokéNav page, save + continue, normal random battles elsewhere: pass after the fixes below.
Fixed offline (the combined ROM still has them): real line breaks in 516's lines, an empty player name in the rival's
lines (h_buffer_player), a black selection frame (palette offset 0), a stale Search Lv. after a battle, the level range
and detail lines' layout, spots behind walls. Not tested: the Bike flee, shiny/chain/bonus odds (code read only), fishing
and Feebas with the DexNav on, Ruby and Sapphire ROMs. Screenshots: screenshots/dexnav/ (dexnav_contact_sheet.png).

## Tests, variant A (2026-11-09, combined Emerald ROM 45c397bf; work/agents/dexnav/tools/va.py, va_chain.sh)
Lab (red no-wild panel inside), Route 101 map (snapshot, caught / seen / "?"), progress line, Found (type icons, the
search level's colour), SEARCH -> Hidden (Search Level 29 and 30: level, egg move "!", ability, stars) -> battle: the
battle's level, ability, first / egg move and perfect IVs matched the Hidden view; the red ring; the tutorial's Hidden
view; Granite Cave's crown; Route 104 land + Surf ("Go surfing..."); Route 111's two strips; Oldale (no wild); a door's
map change; the menu heap per view; save and CONTINUE; the PokéNav page (cursor, Found, SEARCH closes it). Found and
fixed offline: the place's name window lay under the message window (only its last letters showed); the page's first
D-pad press skipped the first icon; a zone change's reads (above). Not testable on Emerald: Sapphire / Ruby's snapshots
(pokeruby's tiles and encounter-tile flags, Route 111 / 115 crops on their maps). Shots: screenshots/dexnav/variant_a/
(dexnav_variant_a_sheet.png).
Final recheck (b8add5e3, 2026-11-09): the name strip whole on Route 101, 104, 111 and in Granite Cave; the PokéNav
page's first press picks the first icon; Route 111's two views in game; Lab, tutorial (this run lost the tutorial
battle: it ended as a loss should, the PC, state 3), Search -> Hidden -> battle (level, ability, first move matched),
save and CONTINUE. Shots: screenshots/dexnav/variant_a/final/ (dexnav_final_sheet.png).
Timing check (270a38f5, 2026-11-09): into Oldale 7.8 ms in one frame (was 27.9), back into Route 101 10.9 ms then
the icons 4.5 and 2.4 ms on the next frames, the name whole by the third frame and never garbled while it prints; the
screen made again (a cave's ladder, closing the X menu) ~104 ms behind the field's fade (font 18 ms, name banks 14,
file reads 22, the name 9.5, icons 7); menu heap 39,848 B held at the area view's peak (Found 36.0 KB). Found then: one
frame at a zone change or a view switch showed the new characters through the old maps (or the old ones through
new palette lines). Since then (offline): the maps are emptied in VRAM before new characters load and written at once
after; the screen's creation opens fewer files (the species, move and ability names when first needed, the type
icons' palette and cells at the first Found, the open icon archive reused) and queues the name. Shots:
screenshots/dexnav/variant_a/timing/ (dexnav_timing_sheet.png).
Check (06bc12c5, 2026-11-09): no mixed frame at a zone change or a view switch (the BGs), the X menu's close clean;
one sprite (Found's type icon) stays a frame into Hidden (sprites change at the next VBlank). The screen made again:
78-80 ms (was 102-104; the field's own font would save its 18 ms more). Zone changes 8.6 / 11.8 ms, then 4.5 and
2.4 ms. Menu heap: 38,784 B held in the area view (22,600 B free). Tutorial start, a search battle (its level, ability
and first move as the Hidden view had them), save and CONTINUE: fine. Shots: screenshots/dexnav/variant_a/check6/.
