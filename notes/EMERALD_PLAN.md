# Pokémon Emerald NDS: the plan (emerald_plan, 2026-10-11)

Research only, done while v16.4 builds. Nothing in HoennB2 was changed except this file and `work/agents/emerald_plan/`.
No ROM was built, no emulator was run, nothing was downloaded. Every number below was measured from the two pret
decomps in `external/` (pokeruby 5784633c, pokeemerald 731ad5b) by the scripts in `work/agents/emerald_plan/tools/`
(re-run them to reproduce; outputs in `work/agents/emerald_plan/out/`). The chapter-by-chapter story comparison is
`work/agents/emerald_plan/story_beats.md`.

## In short

- **Emerald is mostly the same Hoenn.** Of the 387 Sapphire maps Emerald keeps, 253 have the same ground (112
  identical, 141 only with retouched tile art, which our 3D build mostly ignores). 46 more have small changes (30 tiles or
  less). The real map work is about 60 maps: the 8 Gyms (all redesigned), the 8 Trick House puzzles, ~15 towns and
  routes with bigger edits, and the new places: Magma Hideout (8 maps), Mirage Tower (4), Artisan Cave (2), Desert
  Underpass, Terra/Marine Cave (5), Steven's cave, the Safari Zone expansion (2) and 3 new underwater areas.
- **The Battle Frontier is the big extra** (58 maps, plus Trainer Hill 7 and the Battle Tents 9). As already agreed, it
  stays out at first: Black 2's PWT and our Battle Tower stand in for it.
- **The story changes the most.** Emerald has about 560 story scenes; about 320 are Sapphire's own scenes (HoennB2's port
  carries over), about 50 changed and 184 are new, but 87 of the new ones are the Battle Frontier and Trainer Hill. That
  leaves **about 150 new or changed scenes**, mostly in the second half: Team Magma as a second villain (Mt. Chimney,
  Meteor Falls, the Magma Hideout, the Mossdeep Space Center tag battle with Steven), the Groudon-vs-Kyogre crisis in
  Sootopolis, Sky Pillar and Rayquaza inside the main story, Juan as the 8th Gym Leader, Wallace as Champion, and
  Match Call (PokéNav) registrations everywhere.
- **Trainers, wild Pokémon, items, text** come out of HoennB2's generators once they can read pokeemerald. Emerald
  battles 834 trainers (Sapphire 632): 390 are the same or only re-levelled, the rest have other teams or are new.
  Black 2's trainer table has room for about 637, so **all of Emerald's rematches do not fit** (a decision, below).
- **Music:** 5 new story songs (18 with the Frontier). HoennB2's music converter reads the user's own Sapphire
  cartridge dump, so the new songs need **the user's own Emerald dump** (or a new reader for the decomp's MIDI files).
- **Sprites:** Pokémon stay Black 2's (Emerald's animated sprites are not needed). Black 2 already has Juan, Steven and
  Wallace. New art is only Brendan and May in their Emerald outfits (if wanted), Wallace as Champion, Steven's back
  sprite (for the tag battle) and the title.
- **Recommendation: option (a), a third version in HoennB2 (`HOENN_VERSION=emerald`)**, built like Ruby but with a
  pokeemerald reader. Everything that took the longest in HoennB2 (the world builder, buildings, rooms, caves, the
  engine patches, Fairy, music, Pokédex, checkers, release kit) is shared and keeps improving all three games.
- **Effort: about 3-4 agent-days without the Frontier**, roughly half of HoennB2's 7 (Ruby took about 1). That is
  more than the earlier "one third" guess: every Gym and the Trick House were redesigned, Chapter 10 is a rewrite,
  and the trainer table is full.
- **The user decides** (section 4): what the Frontier island shows at first, Trainer Hill / Battle Tents, Match Call
  and rematches,
  Brendan and May's outfits, the music source, the title and the release name.

---

## 1. What Emerald changes from Ruby/Sapphire (measured)

### 1.1 Maps
Map identity: matched by folder name, with Emerald's renames (`tools/diff_maps.py` ALIAS, each checked against
`map_groups.json` and the layouts: e.g. Underwater1-4 -> Underwater_Route124/126/127/128, EverGrandeCity_Corridor1-5 ->
Hall1-5, R/S's Cave of Origin B4F -> Emerald's CaveOfOrigin_B1F, R/S's SafariZone_Northeast/Southeast -> Emerald's
SafariZone_North/South (92-94% identical blocks; Emerald's NE/SE names hold the new areas)).

| | pokeruby | pokeemerald |
|---|---|---|
| maps (with map.json) | 394 | 518 |
| R/S maps Emerald keeps | 387 | |
| R/S maps Emerald drops | 7: the three Contest Lobbies + Halls of Fallarbor, Verdanturf and Slateport (Battle Tents take their place), LilycoveCity_EmptyMap. Kept but unused in Emerald: Cave of Origin B1F-B3F, the Lilycove Magma Hideout (Ruby's) | |
| Emerald-only maps | | 131 (list below) |

**Layouts of the 387 kept maps** (blocks: metatile id, collision, height, plus each metatile's look and behaviour):
| Result | Maps | What it means for us |
|---|---|---|
| identical | 112 | nothing to do |
| same ground, retouched art only (same metatile ids, collision, heights) | 141 | nothing beyond the label carry-over below: our terrain is built from labels and Black 2 textures |
| changed, walkability the same | 13 | almost nothing |
| changed, 30 tiles or less | 46 | a rebuild of the map |
| changed, more than 30 tiles | 29 | real work (list below) |
| resized | 23 | Route 103 (80x20 -> 80x22), Route 109 (40x60 -> 40x63), Lavaridge Gym 1F/B1F (11x24 -> 17x19), Mossdeep Gym (20x30 -> 26x36), Rustboro Gym (+1 row), Seafloor Cavern Room 2 (18x21 -> 18x12), Lilycove Contest Lobby (23 -> 31 wide), and every Pokémon Center 2F (15 maps, one layout, +1 row: the Union Room / wireless club floor) |
| retiled | 23 | 13 Abandoned Ship / S.S. Tidal rooms (same layout, tileset only renamed), Devon Corp 1F/3F, Mossdeep Game Corner, Lilycove elevator, and the 5 Battle Tower maps that became the Frontier's Battle Tower |

**Outdoor maps with the biggest changes** (collision/height tiles changed; `out/maps.json`):
| Map | Tiles | What (from the changed area and the new warps) |
|---|---|---|
| Battle Tower island -> Battle Frontier West | whole map | 29x30 -> 56x72, 1 -> 11 doors, + Battle Frontier East (new map) |
| Sky Pillar top | 296 | Emerald's layout; Sky Pillar 1F-5F + top also get "clean" layouts after Rayquaza |
| Route 109 | 226 | 3 more rows; beach redone |
| Mossdeep City | 178 | the east part (Space Center area) |
| Route 103 | 157 | 2 more rows; the east half redone |
| Route 125 | 132 | two areas east and south-west of Shoal Cave (likely the Marine Cave dive spots: unchecked) |
| Slateport City | 118 | the market (stalls) and the Battle Tent (was the Contest Hall) |
| Route 115 | 77 | north part; 2 Terra Cave doors |
| Route 127, 124 | 69, 64 | sea areas (Route 127 has Marine Cave spots; Route 124's change: unchecked) |
| Route 111 | 66 | the Trainer Hill building (south) and Mirage Tower (2 new doors; a "no Mirage Tower" layout) |
| Route 113 | 61 | 2 Terra Cave doors |
| Safari Zone (R/S east areas) | 57, 34 | joined to the new expansion areas |
| Route 116, Jagged Pass, Routes 114/118/119, Sootopolis, Route 117 | 25-33 each | Terra Cave doors (Routes 113-116 and 118, 2 each), the Magma Hideout door (Jagged Pass), the Mystery Events House (Sootopolis) |
| 14 more towns/routes | under 25 each | small edits |

**Rooms and caves with the biggest changes**: all 8 Gyms (Rustboro 76 tiles + resize, Dewford 145, Mauville 30 with
new switch barriers, Lavaridge 1F/B1F resized, Petalburg (heights, door scripts), Fortree 202, Mossdeep 345 + resize,
Sootopolis 1F 45 / B1F 15), all 8 Trick House puzzles (47-159 each), Cave of Origin (Emerald has Entrance, 1F and B1F
only; its B1F is R/S's B4F room with 94 tiles changed), Seafloor Cavern Room 2 (resized) and Room 3 (44),
Route 114 Fossil Maniac's tunnel (51: the way into the Desert Underpass), Mt. Pyre 2F/3F (11/8), Lilycove Contest
Lobby, Birch's lab (+ a "with table" layout), May's house.

**Emerald-only maps (131)**:
| Group | Maps | Notes |
|---|---|---|
| Battle Frontier | 58 | Outside West/East, 7 facilities' rooms, 16 Battle Pyramid squares, 9 lounges, Center, Mart, Ranking Hall, Exchange Corner, Scott's house |
| Event islands | 26 | Faraway, Birth, Navel Rock: **already in HoennB2** (data/hoenn_event_maps.json) |
| Battle Tents | 9 | Slateport, Verdanturf, Fallarbor (lobby, corridor, battle room) |
| Magma Hideout | 8 | 1F, 2F x3, 3F x3, 4F (Jagged Pass) |
| Trainer Hill | 7 | entrance, 4 floors, roof, elevator (Route 111) |
| Terra/Marine Cave | 5 | 2 + 2 + Underwater_MarineCave |
| Mirage Tower | 4 | Route 111 |
| Underwater | 3 | Routes 105, 125, 129 |
| Artisan Cave | 2 | on the Frontier island (doors in Outside East and West; Smeargle) |
| Safari Zone expansion | 2 | the new NE/SE areas |
| Sootopolis Mystery Events House | 2 | link/e-Reader battles |
| one each | 5 | Altering Cave (**already in HoennB2**), Desert Underpass, Meteor Falls Steven's Cave, Pokémon League 2F, Union Room |

**Tilesets** (`tools/diff_tilesets.py`, `out/tilesets.json`): all 50 pokeruby tilesets exist in Emerald (Ship ->
InsideShip, BattleTower -> BattleFrontier renamed). Behaviour bytes are almost unchanged (General: 0 of 512). The art
was retouched widely (General 228 of 512 metatiles look different, 66 of its 8x8 tiles redrawn; Cave 365 of 414;
Rustboro, Mauville, Slateport, Lilycove, Fallarbor ...), and the 8 Gym tilesets were rebuilt. 17 tilesets are new (10
Frontier ones, Mirage Tower, Navel Rock, Island Harbor, Trainer Hill, Mossdeep Game Corner, Mystery Events House, Union
Room). Example sheet (left R/S, right Emerald): `out/general_changed.png`: the same trees, cliffs and roofs, redrawn.

**Metatile labels** (what our 3D builder reads; `tools/label_need.py`, rule from data/hoenn_event_maps.json: a metatile
that renders and behaves exactly like pokeruby's keeps its label). Emerald's 66 outdoor maps use 3,259 distinct
metatiles: 1,294 identical (1,274 already labelled), 928 changed under 30% of their pixels (retouches: the label
carries over after a quick look), 828 changed more, 209 new ids, 6 with another behaviour. So **about 1,000 metatiles
need the labelling workflow** (HoennB2 labelled 3,107 in all), and a carry-over script does the rest.

**The world grid.** HoennB2 puts all outdoor maps on one grid from Sapphire's connections (49 maps, 0 conflicts).
Emerald's Route 103 grows by 2 rows at its south edge with the same connection offsets, so Emerald's own world is no
longer consistent: walking the connections from Littleroot gives 2-row conflicts at **Verdanturf-Route 116,
Fallarbor-Route 114 and Dewford-Route 107**, and 36 maps sit 2 rows off their Sapphire place. On the GBA nobody sees
this (connections are local); on our single matrix it must be resolved once (keep Sapphire's Route 103 height and put
Emerald's 2 rows into the forest/sea, or absorb 2 rows at one seam). Route 109's 3 new rows are at its open-sea south
edge (no conflict).

**Other layouts swapped by scripts** (setmaplayoutindex): Emerald: Route 111 (Mirage Tower gone), Sky Pillar 1F-5F and
top (clean after Rayquaza), Birch's lab (with table), Sootopolis (the legends' battle), Mystery Events House, Route 130,
Route 131, Shoal Cave; R/S: Route 130, 131, Shoal Cave, Seafloor Room 9, Cave of Origin B4F.

### 1.2 Story scripts
Full comparison: `work/agents/emerald_plan/story_beats.md` (one table per HoennB2 chapter, Emerald and pokeruby file:line
for every beat). A "scene" there is an event script that does more than talk (movement, warp, special, story flag,
non-plain battle, weather, wild battle); counts by text matching, corrected by hand (the agent's hand corrections applied per row).

| Ch | Emerald story | Same | Changed | New | Gone |
|---|---|---|---|---|---|
| Ch0 | truck, Littleroot, Route 101, starter (+ post-game National Dex / Johto starters) | 30 | 6 | 7 | 1 |
| Ch1 | Route 103 rival, Pokédex, Petalburg, Woods, Roxanne | 26 | 2 | 5 | 0 |
| Ch2 | Devon Goods, Match Call, Rustboro rival battle, Brawly, Steven | 37 | 2 | 1 | 0 |
| Ch3 | Slateport, Battle Tents, Route 110, Wattson, Trick House | 70 | 3 | 20 | 17 |
| Ch4 | Routes 111-115, Mirage Tower, Meteor Falls (Magma) | 15 | 2 | 9 | 2 |
| Ch5 | Mt. Chimney (Magma the villain), Jagged Pass, Flannery | 9 | 2 | 2 | 1 |
| Ch6 | Norman, Surf, Routes 105-108, Abandoned Ship, New Mauville | 11 | 0 | 0 | 0 |
| Ch7 | Routes 118-120, Weather Institute (Aqua), Winona | 13 | 3 | 0 | 0 |
| Ch8 | Lilycove, Mt. Pyre, **Magma Hideout**, Slateport sub, Aqua Hideout | 62 | 3 | 11 | 4 |
| Ch9 | Mossdeep, Tate & Liza, **Space Center tag battle**, Dive | 14 | 2 | 9 | 6 |
| Ch10 | Seafloor, Route 128, **Sootopolis crisis, Cave of Origin, Sky Pillar, Rayquaza**, Juan | 5 | 5 | 20 | 4 |
| Ch11 | Victory Road, Elite Four, **Champion Wallace**, Hall of Fame | 12 | 1 | 1 | 0 |
| Ch12 | Routes 129-134, Pacifidlog, Regis (new puzzles) | 6 | 1 | 1 | 0 |
| Ch13 | post-game (Frontier, Steven's Cave, Terra/Marine Cave, islands ...) | 11 | 20 | 98 | 5 |
| **Total** | | **321** | **52** | **184** | **40** |

The main differences, measured:
- **Both teams are villains.** Aqua's scenes are Sapphire's (same trainer slots; Seafloor Room 9 keeps 90% of
  Sapphire's text). Magma is the villain at Route 112 (cable car), Meteor Falls (takes the Meteorite, Archie chases),
  Mt. Chimney (Maxie + Tabitha; Archie asks you to stop them), Jagged Pass and the new **Magma Hideout** (Maxie wakes
  Groudon with the Blue Orb, it flees), and the **Mossdeep Space Center**. Emerald's Magma fights reuse **Ruby's**
  trainer slots and much of Ruby's text, so HoennB2's Ruby branches are a ready base for Mt. Chimney and Meteor Falls.
- **Mt. Pyre**: Archie takes the Red Orb; Magma already took the Blue Orb; the old lady gives the **Magma Emblem**,
  which opens the hideout at Jagged Pass. The Slateport submarine theft is triggered at the end of the Magma Hideout.
- **Space Center** (after Tate & Liza): the player picks 3 Pokémon for a tag battle beside Steven (his fixed team,
  pokeemerald src/battle_tower.c) against Maxie and Tabitha. Steven's Dive gift waits until it is won. Black 2 has
  `CallTrainerMultiBattle` for partner battles; the 3-of-6 choice needs a check.
- **Ch10 is the largest rewrite** (~6 scenes reusable, ~20 new): Kyogre escapes Seafloor Cavern; Groudon and Kyogre
  fight in Sootopolis (camera scene, downpour/drought swap, a "legends" layout); Wallace waits in the Cave of Origin
  (no legendary battle there; Emerald's cave is 3 maps, R/S's was 6); Sky Pillar joins the main story (Wallace opens it, Rayquaza wakes,
  stops the fight); Wallace gives Waterfall; **Juan** is the 8th leader (trainer slot 272, Sapphire's Wallace);
  Rayquaza is catchable right after, at Sky Pillar (no game-clear check in its scripts).
- **Champion Wallace** (slot 335, Sapphire's Steven); Steven's post-game battle is in Meteor Falls' Steven's Cave.
- **Match Call** is new: ~15 story registrations (Mom, Birch, the rival, Norman, Steven, Scott, Wally, every Gym
  Leader), 76 route-trainer registrations, 7 scripted PokéNav calls; Gym Leader rematches after the Hall of Fame.
- Smaller: an optional rival battle in Rustboro / on Route 104; Scott in ~10 places; Wally's dad walks you home for
  Surf; fossils from Mirage Tower (appears at random; the other fossil waits in the Desert Underpass after the Hall
  of Fame); new Regi puzzles (Rock Smash, Flash, a lap around the room instead of Strength, Fly, waiting); Battle
  Tents replace the contest halls; the Mossdeep Gym and Trick House 7 use rotating tiles.
- **Post-game**: National Dex + a Johto starter in Birch's lab; Latias or Latios by the colour you tell Mom; Kyogre /
  Groudon in Marine/Terra Cave at one of 16 spots the Weather Institute reports; Steven's Cave; Safari expansion;
  Trainer Hill; Gym rematches; Sudowoodo and Artisan Cave on the Frontier island; the event islands (HoennB2 has them).
- **New Black 2 work by need**: Match Call; the Sootopolis/Sky Pillar sequence (camera, weather swap, layout swaps);
  the tag battle; Mirage Tower's 6 specials; rotating tiles; the Regi puzzle hooks; the abnormal-weather caves.
- **Finding for HoennB2's notes** (not changed here): notes/STORY_CHAPTERS.md line 908 says Archie takes the Blue Orb
  and line 1106 that he wakes Kyogre with it; in Sapphire it is the **Red** Orb (pokeruby data/text/aqua_summit.inc
  "The RED ORB ... I, ARCHIE, claim it", "You take the remaining BLUE ORB"; aqua_awakening.inc; constants/version.inc
  ITEM_RED_OR_BLUE_ORB = Blue for Sapphire). The built scenes use the right orb; only the note is wrong.

Sizes (`tools/diff_text.py`, `out/text.json`): the kept maps' scripts grow from 24,715 to 29,941 command lines; the
new maps add 9,554 (mostly the Frontier). Dialogue on the kept maps: 2,883 Emerald lines, of which 1,458 are word for
word Sapphire's/Ruby's and 606 nearly (e.g. "X DEFEND" -> "X DEFENSE"), **819 are new** (72% same or nearly; "nearly"
is only searched in the same map's own text file, so lines pokeruby keeps in shared text files, such as Seafloor
Room 9's, can count as new: an upper bound). Maps whose text is mostly new: Sootopolis, Mt. Pyre summit, Mossdeep
Space Center 1F/2F, Cave of Origin, Birch's lab, the Sootopolis Gym, Sky Pillar outside, Route 104, May's house.
Flags and vars: outside the Frontier Emerald's scripts use 966 flags (pokeruby 770) and 143 vars (114). Black 2's free
pool (STORY_PORTING.md section 6: 874 free saved flags + the 400 item-ball flags, 277 free works) holds that.

Characters as map objects (Emerald `map.json` graphics ids; pokeruby draws the teams through version variables, so
its counts are in RUBY.md 1.1): Team Aqua in 23 maps, Team Magma in 14, Maxie 8, Archie 8, Steven 9 (new: Mossdeep
Space Center 1F/2F, Meteor Falls Steven's Cave; gone: Champion's room, Hall of Fame), Wallace 5 (Sootopolis, Sky
Pillar, Cave of Origin, Champion's room, Hall of Fame; no longer in the Gym), Juan 1 (Sootopolis Gym), Scott 13,
Rayquaza 3 objects in 2 maps (Sootopolis, Sky Pillar), Groudon 4 objects in Magma Hideout 4F, Sootopolis and Terra
Cave, Kyogre 4 in Seafloor Room 9, Sootopolis and Marine Cave.

### 1.3 Trainers and parties (`tools/diff_trainers.py`, `out/trainers.json`)
Trainer ids are the same numbers in both decomps (Emerald reuses slots: 272 Wallace -> Juan 1, 335 Steven -> Wallace).
| | pokeruby | pokeemerald |
|---|---|---|
| trainers in the table | 694 | 855 |
| battled (scripts, rematch tables) | 632 (incl. Ruby's 28) | 834 = 543 first-battle ids + 291 rematch-only ids (78 rematch rows of up to 5 tiers; the Elite Four and Wallace rematch under their own id) |
Of the 834: **242 identical** to R/S, **148 same Pokémon with other levels or moves** (mean -0.5 levels), **173 other
party**, **121 slots reused for another trainer** (R/S's unused grunts/"anonymous" slots: Emerald's Magma grunts,
Rustboro rival, Space Center, the double-battle pairs), **150 new ids** (16 Magma Hideout grunts, Tabitha and Maxie at
the hideout and Mossdeep, 22 new route trainers, the rival's Rustboro battles, the Gym leaders' rematch tiers 2-5,
Steven 804 (post-game), new rematch tiers). Black 2 side (STORY_PORTING.md section 5): HoennB2's registry has 604 ids
used + 33 left = **about 637 usable trainer ids**; trainer defeat flags are id + 1520, packed against Black 2's
system flags. Emerald's 543 first battles fit; with all 291 rematch-only ids they do not (the 8 Gym Leaders' rematches alone are 32 ids).

### 1.4 Wild encounters (`tools/diff_wild.py`, `out/wild.json`)
Emerald: 116 overworld tables (+ 7 Battle Pyramid, 4 Battle Pike). The 97 maps with a Sapphire table all have one in
Emerald: **71 are identical in every method**; 23 method tables have other species, 9 are Ruby's table (Meteor Falls
Solrock, Fiery Path), 3 other levels (Sky Pillar). Typical swaps: Poochyena/Mightyena for Zigzagoon/Linoone (Routes
104, 110, 116, 117, 120, 121, 123, Petalburg Woods), Goldeen for Surskit (Routes 102, 111, 114, 117, 120), Ruby's
Seedot/Nuzleaf, Marill on Routes 104/112, Abra on Route 116, Slugma on Route 113, Mawile in Victory Road. 19 new maps
have tables (Safari expansion 2, Magma Hideout 8, Mirage Tower 4, Desert Underpass, Artisan Cave 2, Altering Cave,
Steven's Cave). Species: 132 (Sapphire 112): +25 (16 Johto species in the Safari expansion, Ditto, Smeargle, Ruby's
Seedot/Nuzleaf/Mawile/Solrock, Mightyena ...), -5 (Lunatone, Meditite, Medicham, Roselia, Surskit). Static and gift
Pokémon: in the story comparison.

### 1.5 Items, tutors and other features (`tools/diff_items.py`, `out/items.json`)
- Item balls 135 -> 162 (98 same place and item, 13 another item, about 40 new on old maps and 11 on new maps, some
  moved a few tiles); hidden items 98 -> 112 (94 same, 17 new, 3 moved).
- Gifts: mostly the same (TM constants were only renamed). Real changes: the fossils come from Mirage Tower and the
  Desert Underpass (not Route 111), the Magma Emblem (Mt. Pyre summit, opens the Magma Hideout), Wallace gives HM07
  Waterfall in Sootopolis (R/S: an item ball in Cave of Origin B3F), Torment/Attract TMs at the Battle Tents (were the
  Contest Halls), the Powder Jar (Slateport), the Pokéblock Case in Lilycove.
- Marts: 17 -> 19 mart lists; new: Slateport market, Battle Frontier Mart, Trainer Hill; changed: Lilycove 4F.
- **Move tutors**: 10 one-time tutors in Hoenn towns (Swagger, Rollout, Fury Cutter, Mimic, Metronome, Sleep Talk,
  Substitute, Dynamic Punch, Double-Edge, Explosion; data/scripts/move_tutors.inc) + 20 at the Frontier for Battle
  Points (BattleFrontier_Lounge7). Black 2 has tutor script commands (STORY_SPECIALS.md 136/137).
- Other Emerald systems: Match Call on the PokéNav (trainers register after battles; Gym leader rematches after the
  Hall of Fame), Battle Frontier (7 facilities + Scott, Battle Points, symbols), Trainer Hill, 3 Battle Tents, all
  Contests in Lilycove, the abnormal-weather search for Groudon/Kyogre (Weather Institute), Mirage Tower collapse,
  tag battle with Steven, double battles started by two trainers spotting you, Lilycove ladies, Trainer Fan Club,
  Lotad/Seedot size houses, Walda's wallpaper phrase, Berry Powder / Berry Crush (link), Union Room (wireless).
- Specials: Emerald's scripts call 495 distinct `special` names (pokeruby 327), but the decomps name the same
  functions differently, so the real number of new mechanics is smaller; the story ones are listed in the story
  comparison. Black 2 has the building blocks for several: `CallTrainerMultiBattle` (tag battles, pokebw2
  include/asm/field_script.inc), its tutor and move-relearner commands, its Battle Subway and PWT engines.
- Items list: Emerald adds key items the story uses (Magma Emblem; Old Sea Map, Mystic and Aurora Tickets are already
  in HoennB2) and the Powder Jar.

### 1.6 Music (`sound/song_table.inc`)
Emerald's table has 210 `mus_*` songs (pokeruby 119): **18 new Hoenn songs**, of which 5 belong to the story
(mus_abnormal_weather, mus_rayquaza_appears, mus_vs_rayquaza, mus_vs_mew, mus_register_match_call) and 13 to the Battle
Frontier (b_frontier, b_tower, b_arena, b_dome, b_dome_lobby, b_factory, b_palace, b_pike, b_pyramid, b_pyramid_top,
vs_frontier_brain, obtain_symbol, obtain_b_points); R/S's Battle Tower song is kept as mus_b_tower_rs. Plus 76
FireRed/LeafGreen songs inside the ROM, 14 of them used (e.g. the event islands: VS Deoxys, VS Legend for Lugia/Ho-Oh,
Sevii cave). The other 107 Hoenn songs are the same songs (the decomps' MIDI files differ byte for byte, so whether a
sequence changed is unchecked). HoennB2's converter (b2tools/m4a.py) reads the songs from the user's own Sapphire dump
(roms/sapphire_rev1_original.gba); roms/ has no Emerald dump.

### 1.7 Sprites
- **Pokémon**: Emerald has 385 two-frame animated front sprites (graphics/pokemon/*/anim_front.png). Not needed:
  HoennB2 keeps Black 2's own animated Pokémon (decision 2026-10-06).
- **Trainer fronts** (graphics/trainers/front_pics, 93 vs 86): all R/S pictures are pixel-identical in Emerald except
  Brendan and May (new Emerald outfits; the R/S ones are kept as brendan_rs/may_rs) and Wallace (a new Champion
  picture). New: Juan, the 7 Frontier Brains, Red and Leaf (link only). Black 2 already has Juan (battle sprite 126,
  overworld 276), Steven (139/287) and Wallace (140/288) from the PWT (RESEARCH_STORY_SPRITES.md).
- **Trainer backs**: Brendan/May (Emerald outfits), Steven (the tag battle), Wally, Red, Leaf.
- **Overworld sheets** (graphics/object_events/pics, 253 vs 224): 150 identical, 28 identical under another name, 30
  changed (every Brendan/May pose: the Emerald outfits; Wallace; the nurse; a few NPCs; the legendaries' field
  sprites), 45 new (Frontier Brains, Juan, Brawly, Flannery, Scott, Deoxys, Lugia, Ho-Oh, Mew, Sudowoodo ...).

---

## 2. What HoennB2 reuses, area by area

"Share" = the part of HoennB2's own work in that area that Emerald must do again (rough, from the counts above).

| Area | Reused as is | Needs work | Share |
|---|---|---|---|
| Engine patches (49 Python modules in b2tools/patches (+ their C files): Exp. Share, HMs, Fairy + split, Hoenn music system, Hoenn Pokédex, town map, sprite switch, zone rectangles, weather, Dive, saves, trade evolutions, roamers, Battle Tower + PWT) | all | a third row in `version.py` (title: Rayquaza, logo; both teams' weather; roamer = the player's choice of Latias/Latios) | 5% |
| Pipeline and checkers (build_rom, rebuild_slice, story_build, outdoor/rooms/caves/npc checks, progression_check, script_check, emulator harness, make_states, release kit) | all | an Emerald build folder and its own savestates (more maps = another ROM layout) | 5% |
| Readers of the decomp | gba.py already reads pokeemerald maps and tilesets (the event islands) | gen_trainers, gen_encounters, gen_items, gen_hidden_items, gen_map_content, gen3text, sapphire_data, allocate_*, level_scaling, gen_dex_text read pokeruby's files (address labels, `.ifdef`, trainers_en.h): an Emerald input mode | new work, ~0.5 day |
| Metatile labels | 1,274 + the 928 lightly retouched ones | ~1,000 relabels (828 redrawn, 209 new, 6 behaviour) | 30% |
| Outdoor world (world.py, terrain modules, town building models) | 253 + 13 maps unchanged in ground | 75 maps with changes (29 big), the Route 103 seam, Frontier island (as decided), Trainer Hill and Mirage Tower on Route 111, Safari expansion, 10 Terra Cave doors, Slateport market + 3 Battle Tent buildings, Sootopolis legends layout | 20-25% |
| Rooms (interior builders, recipes) | every unchanged room recipe | 8 Gyms with their puzzles (Mauville switches, Lavaridge, Petalburg doors, Fortree turnstiles, Mossdeep spinners, Sootopolis ice), 8 Trick House puzzles, Center 2F (one layout), Lilycove Contest Lobby, Mossdeep Game Corner, Birch's lab, May's house | 30% |
| Caves and dungeons | every unchanged cave recipe; the Dive pipeline | Magma Hideout 8, Mirage Tower 4, Artisan Cave 2, Desert Underpass, Terra/Marine 5, Steven's Cave, Cave of Origin's new shape, Sky Pillar clean layouts, Seafloor Rooms 2/3, 3 underwater areas | 40% |
| Story | the porting library (hoenn_story.inc), the specials table (STORY_SPECIALS.md), the chapter method and test switches, scenes whose flow did not change | ~150 new or changed scenes outside the Frontier: Ch8 (Magma Hideout, Mt. Pyre), Ch9 (Space Center), Ch10 (~20 new), Match Call registrations, Scott, the post-game events | 35-40% |
| Trainers / wild / items / text | the generators and the level curve | regenerate from pokeemerald; trainer table limit (rematches); Emerald's own Pokédex text (src/data/pokemon/pokedex_text.h) | 15% |
| Sprites | every existing sprite set (CLASSIC and NEW), Juan/Steven/Wallace from Black 2 | Brendan/May Emerald outfits (if chosen: battle front/back, every overworld pose, the NEW-set equivalents if any exist), Steven's back, Wallace Champion picture (or Black 2's 140), the Emerald title logo | 20% |
| Music | the converter, the Hoenn/Unova option, all 107 shared songs | 5 story songs (+13 Frontier later), from an Emerald source | 10% |

---

## 3. How to build it: three options

### (a) A third version in HoennB2: `HOENN_VERSION=emerald`
How: as Ruby (notes/RUBY.md "WP0 layout"): `b2tools/version.py` gets an `emerald` row; Emerald-only files live in
`emerald/` overlay folders next to the shared ones; generators get a pokeemerald input mode; `data/versions.json` says
which rooms/maps each version installs. Emerald needs its own world build (`work/world_emerald`), because its maps
differ; Sapphire and Ruby keep sharing theirs.
- **For**: everything above that is "reused as is" stays one copy, so every later fix or feature (Fairy, music, Dex,
  post-game, sprite sets, saves, checkers) reaches all three games at once. The Ruby work already built and tested the
  overlay rule and the "Sapphire stays byte-identical" guard. One release kit, one set of notes.
- **Against**: Emerald differs far more than Ruby did (Ruby: 26 wild files, 21 trainer files, 3 rooms; Emerald:
  hundreds of files), so shared builders (world.py, town models, gym builders) get Emerald branches. Every shared edit
  must keep Sapphire and Ruby byte-identical (the WP0 test), which costs builds. Three games in one working tree means
  more care with parallel agents.

### (b) A fork: a new private repo cloned from HoennB2 at the v16.4 tag
- **For**: Emerald can change any builder freely; no risk at all to the released Sapphire/Ruby; simpler for agents. A
  `git clone` keeps the history, so fixes can still be cherry-picked between the two repos. The 17 GB of `work/` can be
  copied with APFS clones (`cp -c`, no extra disk) or rebuilt.
- **Against**: two copies of every engine patch and tool from day one; each later HoennB2 fix must be carried over by
  hand and the two drift apart. Sapphire/Ruby improvements (Fairy, post-game, sprites) stop reaching Emerald for free.

### (c) Build from the pokebw2 decomp's source
pokebw2 rebuilds Black 2 from C plus delinked code; `configure.py --shift 0x100` builds ROMs whose code moved, to test
that mods may change code sizes (docs/configs.md "Shifting"). Upstream matches 44% of the code (README, 2026-10-09);
HoennB2's own copy in external/ is older (11.85%).
- **For**: real C instead of ITCM hooks: no 32 KB ITCM ceiling (HoennB2 has used a good part of it: zone lookup,
  roamers, Fairy, music ...), big features become practical (Match Call, the Frontier facilities later), and the work
  doubles as pokebw2 contributions (the user's exception).
- **Against**: HoennB2's 49 patch modules are binary patches at fixed addresses; on a shifted build those addresses
  move, so either the build stays at Black 2's exact layout (then nothing gains room) or **every** patch is ported to C
  first: a large up-front cost before any Emerald content. Only files marked complete build from C; a modded build has
  no matching check ("tested by playing them"). It compiles with the Metrowerks compiler (a Nintendo SDK tool, run
  through wibo/Wine on this Mac), which the user allowed **only in the pokebw2 clone, never in HoennB2** (DECISIONS
  2026-10-09): using it for Emerald NDS needs the user's OK.

**The feasibility test for (c)** (after the v16.4 release; outline only, nothing done):
1. Bring `~/Documents/GitHub/pokebw2` (the local clone, checked out at 2cccec331, behind upstream) up to upstream main; build the
   matching Black 2 (`ninja`, SHA-1 check), then `configure.py --shift 0x100` and boot the shifted ROM (title, a new
   game, one battle).
2. List every code site the Fairy patches touch (b2tools/patches/fairy.py, fairy.c, fairy_ui.py; notes/FAIRY.md: ov167
   type chart and the 14 TYPE_NONE sentinels, item events, ov142 bag, ov255 PC, ov296/ov300 Pokédex, Hall of Fame,
   battle buttons, the intro command, the options bits) and mark each one's pokebw2 source file complete / not.
3. Port Fairy as C in the complete files (an 18x18 chart in btl_calc.c, the sentinels, the toggles), its data through
   the extracted file tree (type names, personal/move data from HoennB2's tables), build with `--shift`.
4. Re-run HoennB2's Fairy proofs (b2tools/fairy_check.py and the screenshots/fairy_core cases) on the result.
5. Report: what worked, which sites were not decompiled yet (blockers), lines of C vs bytes of patch, build time, and
   an estimate for porting all 49 patch modules (the real price of (c)).
Pass = Fairy behaves the same, the shifted ROM is stable, and the port estimate is affordable. Then (c) is worth it
for the Frontier update, not for Emerald's first release.

### Recommendation: (a)
The parts that cost HoennB2 the most (world, buildings, rooms, caves, sprites, engine features: about two thirds of its
commits) are 60-95% reusable for Emerald, and the Ruby work proved the version mechanism. Keep it simple with three
rules: (1) Emerald-only data goes in `emerald/` folders or Emerald rows, never edits of Sapphire data; (2) every merge is
checked with the Sapphire and Ruby SHA-1 test (cheap check: the generators' Sapphire/Ruby outputs byte-identical; full
ROM check before each release); (3) the Frontier waits (the user's decision). Decision point after phase 2: if more
than about a third of the shared builder files need Emerald branches, fork at that point (b) instead; nothing is lost.
Run the (c) feasibility test in parallel when there is time; adopt it later for the Frontier if it passes.

---

## 4. Decisions for the user (plain words)

1. **Battle Frontier** (agreed 2026-10-08: Black 2's PWT for now). What should the island look like at first?
   - A. Emerald's Battle Frontier island, with our Battle Tower (Black 2's Subway engine) and the PWT working, and the
     other six facility buildings standing but closed ("still under construction"). Sudowoodo and Scott's house can be
     there too. *(recommended: it looks like Emerald and the facilities can open one by one later)*
   - B. Keep Sapphire's small Battle Tower island from HoennB2 and no Frontier at all until a later update.
2. **Trainer Hill and the three Battle Tents**: closed buildings at first (recommended), left out, or built?
3. **Match Call and rematches.** Emerald's PokéNav registers about 15 story characters and 76 route trainers and
   makes 7 scripted calls; registered trainers and the Gym Leaders offer rematches. Those rematches are 291 extra
   trainers, and with them Emerald needs about 200 more trainers than Black 2's table holds (834 vs about 637).
   - A. No Match Call list and no rematches at first (as Sapphire/Ruby in HoennB2); the 7 story calls play as plain
     messages *(recommended for the first release)*
   - B. A, plus the 8 Gym Leaders' rematches after the Hall of Fame (32 battles: fits)
   - C. Everything, with a contact list on the Xtransceiver (HoennB2's PokéNav) and a code patch that enlarges the
     trainer table (much more work)
4. **Brendan and May**: their Emerald outfits (made from Emerald's own sprites, the same way as Sapphire's), or keep
   the Ruby/Sapphire outfits HoennB2 already has? And for the NEW (community) sprite set: are there Emerald-outfit
   sheets you want to use?
5. **Which Emerald-only extras at first** (recommended yes unless marked): the story places (Magma Hideout, Space
   Center tag battle, Sky Pillar and the Sootopolis Rayquaza scenes, Juan, Mirage Tower fossils, Desert Underpass,
   the new Regi puzzles), the post-game (Steven in Meteor Falls, Terra/Marine Cave with Groudon/Kyogre, Rayquaza, the
   Safari expansion, National Dex + Johto starters in Birch's lab, Latias/Latios by colour; Artisan Cave and
   Sudowoodo only with island choice 1A, since both are on the Frontier island), the 10 move tutors. Left out at
   first (recommended): Contests (as HoennB2: counters only), Union Room / Mystery Events House (link), Berry Crush,
   Walda's wallpaper, the Trainer Fan Club's TV shows.
6. **Music source**: do you own an Emerald cartridge you can dump yourself (the same rule as Sapphire)? Then the 5 new
   story songs (and later the 13 Frontier songs) convert like the others. If not: a new reader for the decomp's MIDI
   files (more work), or Black 2 stand-ins for those 5 songs.
7. **Title and name**: "Pokémon Emerald NDS" as the public name (agreed 2026-10-08); a new Gen 5-style "Pokémon
   Emerald" logo (new art, like the Sapphire/Ruby logos) with Rayquaza on the bottom screen and its cry (**replaced
   2026-10-12: Emerald's own title screen ported straight from Emerald, DECISIONS.md**); release files
   `Pokemon_Emerald_NDS_v1.{nds,bps}` (start at v1, or follow HoennB2's numbers?); its own post, as Sapphire and Ruby.
8. **Same house rules as HoennB2?** Birch's four questions (Fairy, move split, music, sprite style), the Gen 6 Exp.
   Share, HMs without the move, levels scaled for the Exp. Share, in-game event tickets, trade evolutions without
   trading, Emerald's own wild tables and teams exactly *(recommended: yes to all)*
9. **The structure**: option (a), a third version in HoennB2 (recommended), or (b) a fork.

---

## 5. Phased plan

Rough agent time at HoennB2's pace (several agents in parallel; HoennB2 itself took about 7 days, Ruby about 1).

| Phase | What | Effort |
|---|---|---|
| 0. Decisions and set-up | The user's answers (section 4). WP0 for Emerald: `version.py` row, `emerald/` overlays, pokeemerald readers in the generators, `data/versions.json` maps/rooms, Emerald world build folder; Sapphire/Ruby SHA-1 test | 0.5 day |
| 1. Data | Trainers (registry for Emerald, rematch choice; both teams at once: Ruby swapped Aqua's 5 class slots, Emerald needs Magma's beside them, so about 5 more spare trainer classes (how many are left: unchecked)), level curve refit, wild tables (116), items and hidden items, marts, tutors list, Emerald text layer, Emerald Pokédex text | 0.5 day (parallel with 2) |
| 2. World and maps | Label carry-over script + ~1,000 relabels; the Route 103 seam; the changed towns/routes; Frontier island (as decided), Route 111 (Mirage Tower, Trainer Hill building), Safari expansion, Terra Cave doors; rooms: 8 Gyms + puzzles, Trick House, Center 2F, the changed rooms; caves: Magma Hideout, Mirage Tower, Artisan Cave, Desert Underpass, Terra/Marine, Steven's Cave, Cave of Origin, Sky Pillar, Seafloor; then a separate glitch-check agent per new area (standing rule) | 1-1.5 days |
| 3. Story | Per chapter, as HoennB2: Ch0-7 and 11-12 mostly reuse the Sapphire port (+ Scott, Match Call registrations as chosen, the Rustboro rival battle, Wally's dad, Regi puzzles, Mirage Tower); Ch4/5 Magma scenes from the Ruby branches; Ch8 Magma Hideout + Mt. Pyre; Ch9 Space Center; Ch10 the big rewrite (Sootopolis crisis, Sky Pillar, Rayquaza, Juan); Ch11 Champion Wallace; Ch13 post-game without the Frontier (Steven's Cave, Terra/Marine Cave, Desert Underpass, Safari expansion, National Dex + Johto starters, Lati colour choice) | 1-1.5 days |
| 4. New mechanics | Space Center tag battle (CallTrainerMultiBattle + a 3-of-6 choice), the Sootopolis camera/weather/layout sequence and Rayquaza's scene, Mirage Tower (random visibility, collapse), rotating tiles (Mossdeep Gym, Trick House 7), the new Regi puzzle hooks, the abnormal-weather caves, double battles from two trainers, move tutors, Match Call / rematches as chosen; closed Frontier/Tent/Trainer Hill doors | 0.5-1 day (parallel with 3) |
| 5. Art and music | Emerald logo + Rayquaza title, Brendan/May outfits (if chosen), Steven's back, the 5 story songs (from the chosen source) | 0.5 day (parallel) |
| 6. Test and release | All checkers, progression solver, script/crash check, smoke tests of every option set incl. a forced loss, save tests, release kit `Pokemon_Emerald_NDS_v1`, showcase shots | 0.5 day |
| **Total** | | **about 3-4 days** (3 when phases overlap well) |
| Later: the Battle Frontier update | 58 maps, 7 facilities (only the Tower has a Black 2 engine: Subway), Frontier Brains, Battle Points, 20 tutors, 13 songs; Trainer Hill, Battle Tents | a project of its own (1.5-3 days); a candidate for the pokebw2 source build if test (c) passes |

Order inside the phases follows HoennB2's habits: a scope agent per chapter first, then builders, then separate check
agents; build only in each agent's own folder; one emulator at a time; never delete (Trash).

---

## Feasibility test results (emerald_srcbuild, 2026-10-11)

Option (c), tested for future reference (the user chose (a) for Emerald). Worktree `~/Documents/GitHub/pokebw2_srctest`,
local branch `srctest-fairy` from upstream main 2cbfdfddf (not committed, never pushed; left in place). Tools, logs,
screenshots: `work/agents/emerald_srcbuild/` (`proof/` = the battle shots, `srcdiff/fairy_full.diff` = every change).

**What was ported: the Fairy type core, in source form.**
- Data only (JSON, built by the decomp's packers): `TYPE_FAIRY = 17` and `TYPE_NULL = 18` in `data/constants/types.txt`,
  `data/types/fairy.json` (type name), the 22 species retypes (`data/pokemon/*/data.json`), Sweet Kiss/Charm/Moonlight
  to Fairy (`data/moves/*`).
- C, in files that are already complete (built from source): the Gen 6 18x18 chart and both chart readers in
  `btl_calc.c`, the "no type" sentinel as `TYPE_NULL` in `btl_pokeparam.c` (9 sites), `ability_handlers.c` (Color
  Change), `move_handlers.c` (Conversion 2). 40 lines of C changed in total, against HoennB2's fairy.py/fairy.c.
- Still asm: 3 of HoennB2's 14 sentinel sites are in `btl_server_flow.c`, whose C is a draft (480 of 997 functions
  matched, about half not written), so it is not linked. Solved with a small new build step: `mod/objpatches.txt` +
  `tools/build/objpatch.py` patch the *delinked object* by symbol + offset before linking (same-size edits only), so
  the edit moves with the code. The C draft says `TYPE_NULL` too, so the patch disappears once the file is complete.
- Test script: Mom's scene (`data/field_scripts/aspertia_city_2.s`) gives a Lv 15 Dratini and starts a wild Lv 5 Marill.

**What boots.**
- Matching build of the new worktree: SHA-1 identical, **91 s** from clean (extract, delink, 4,896 steps).
- Upstream `configure.py --shift 0x100` **does not boot**, even with no changes: (1) newer dsd refuses to pack it
  ("ARM9 secure area changed ... provide the ARM7 BIOS"); we have no BIOS and may not download one. HoennB2's own dsd
  (v0.12.1-dsi.1) packs it anyway, as it does HoennB2's ROMs (whose secure area also differs from the dump: 286 bytes,
  so their DSi-mode digests are already stale; emulators don't care). (2) The packed ROM then aborts at boot
  (white screen): `SaveControl_Create` calls into overlay 331 through a relocation dsd could not attribute
  (`module:overlays(36,331)`); the build links such relocations to the *first* candidate, which is only right while
  nothing moves. Black 2's configs still have **2,512 such ambiguous relocations**; a symbol check alone shows at least
  472 linked to the wrong overlay, 1,812 need knowledge of which overlays are loaded together.
- **Fairy build without the shift (`configure.py --mod`, a new non-matching option): boots and battles.** ov167 grows
  32 bytes (the chart), which moves 15 overlays (168, 171, 285-290, 297, 329, 339-343). That puts 188 ambiguous
  relocations at risk; without fixing them the battle aborted at start (`BtlvInput_Create` got a wrong heap ID).
  Resolving 100 of them by co-residency (`tools/resolve_ambig.py`, written into `config/b2_us/.../relocs.txt`) was
  enough: cold boot → title → new game → Mom → wild battle → **"Dratini used Twister! It doesn't affect the wild
  Marill..."** (`proof/02_*`; the control build without the chart change: Twister knocks Marill out, `proof/03_*`) →
  ran away → back in the house, walking (`proof/04_*`, `05_*`). Not tested: the other 85 at-risk relocations, other
  screens (summary/Pokédex would show type 17 with no icon: that is fairy_ui's part), saving.
- Build times: incremental C change + relink + ROM **20-45 s**; ROM pack ~10 s.
- Gotchas found: adding a type name also adds an easy-chat word and renumbers every later easy-chat word (the generated
  `pms_words.h` shows it); a changed constants list needs `ninja` twice (generated headers are tracked by absolute path).

**How much of what HoennB2 patches is C in pokebw2** (`tools/patch_sites.py`, a static scan of every address in the
patch modules and their C files, so it counts the functions HoennB2 calls as well as the bytes it changes; results in
`patch_sites.json`). Of 582 addresses that map to one source file: **236 (41%) in complete C files**, 118 (20%) in C
drafts that are not linked yet, **228 (39%) in code with no C at all** (mostly arm9 main: personal/move data, field
system, sound, ITCM); 196 more fall in overlays the scan could not tell apart. Upstream reports 56% of code matched,
29% in complete files (report.json).

**How hard each patch family would be to port:**

| Effort | Patch modules |
|---|---|
| None / data only (the decomp packs it from JSON or asm: trainers, encounters, field scripts, text, zones, events, map matrices, trades, species, moves, items) | encounters, encounter_rules, scripts, text, trades, shops (list files are not packed yet), starters, hoenn_dex |
| Data, but no source path yet (maps, models, textures, sprites, sound: needs a small "replace these files" step in configure.py) | interiors, hoenn_world (data part), hoenn_textures, standalone, objects3d, boat_demos, boulder_1x1, area2_buildings, sprites, centers |
| C edits in complete files, plus some object patches | fairy core (done), game_clear, pwt, capture_demo, story, title_scene, weather, fixed_weather, trainers |
| C on asm (new code that hooks code with no C yet: needs that code decompiled first, or object patches + new C files) | fairy (personal/move readers in arm9), fairy_ui, exp_share, hm_free, hoenn_music, hoenn_pokedex, roamers, sprite_switch, town_map, dive, battle_tower, zone_effects, hoenn_season, title, title_mcss, trade_evos |

**The real price of (c)** is not the patches themselves (they port at about the effort shown) but making code moves
safe: all 2,512 ambiguous relocations resolved (an upstream-worthy job, ~1-2 agent-days with a load-graph tool and
boot tests), the secure-area/BIOS question for any change to the ARM9 main module, and the ~6.6 KB between the last
overlay and the heap arena (fixed at 0x021fea60) for code that grows the overlay region.

**Recommendation (plain words):** keep Emerald on HoennB2's patch pipeline (option a), as decided. Source builds work
for small, contained changes today and are much nicer to edit, but every change that moves code needs the ambiguous
relocations fixed first. Revisit for Pearl or the Battle Frontier once upstream has resolved them (a good pokebw2
contribution if the user wants one); a hybrid (decomp data packers for trainers/encounters/scripts/text, patches for
code) is possible later without changing HoennB2's layout.
