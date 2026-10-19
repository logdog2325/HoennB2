# Real seasons in Hoenn (seasons_study, 2026-10-18)

The user asked (2026-10-18) whether Black 2's real seasons can work in Hoenn. Short answer: **yes, and it is cheap**.
Black 2 already does almost everything by itself once the summer lock (patches/hoenn_season.py) is lifted. The main
job is giving Hoenn's textures to the three other seasons' texture sets. That is done and checked offline, behind a test
switch. The test ROM is **not built yet**: the disk had 3.4 GB free and the rule is no builds under 5 GB.

## Birch's seasons option (seasons agent, 2026-10-18; the user-tested prototype made a player choice)
- **Birch's fifth question** (after the sprite style; fairy.py intro_script, text 0054 line 34): "And last... the
  seasons! Here in Hoenn, it's summer all year round. Would you like the seasons to change with the months instead?"
  YES / NO. Same text in Sapphire, Ruby and Emerald (0054 has no version overrides). Line 26 now says "five quick
  questions", line 31 starts "Fourth...". 0054 is at 5000 of its 5040-byte fixed slot (Black 2's unused placeholder
  lines 3, 4, 35, 37-39 shortened like 0/34/36 before).
- **Options u16 bit 15** (save block 27; bits 11-14 are Fairy, split, music, sprites; 0-10 Black 2's): YES = 1.
  Every save made before the question has 0 there, so it stays summer; a NO is the same.
- **Code**: hoenn_season still writes the summer lock; fairy.py (which asks the question) then points both lock sites
  at two ITCM readers in fairy.c: Season_GetRealTime's "(month - 1) & 3" -> `bl Season_FromMonth` (bit 15 ? (month -
  1) & 3 : 1), GameData_GetSeason -> long jump to `Season_Kept` (bit 15 ? GameData +0x1c8 : 1). No save loaded yet ->
  summer. +96 B of ITCM. The HOENN_SEASONS=1 build switch is gone: the seasonal texture sets are always built.
- **Music**: Music_ZoneBGM's Unova option always plays the summer field (bgm1), so Unova music is the same in every
  season (the prototype's fix, now unconditional; with the lock the season was 1 anyway).
- **Warp-only maps** (standalone.py seasonal_areas): their zones move from the fixed areas 407 (Mt. Chimney) / 408
  (the rest: Petalburg Woods, Jagged Pass, Mt. Pyre, Safari Zone, Sky Pillar, Southern Island, Sootopolis, Battle
  Tower outside, Faraway/Birth Island, Navel Rock) to the first two seasonal Black 2 area groups no zone uses (6-9 and
  10-13 in all three versions; asserted free at build time), records = the old record with the season's lights
  (140-143) and texture set. The four sets (Hoenn's set for the season + the stand-in textures, each from its Black 2
  area's set for that season when it has the same texture) are shared by both groups (entries of the first group);
  summer = the old set byte for byte (asserted). Ash stays ash grey in every season (the ash copies are the same in
  all four of area 2's sets). The season card on warps and the banner without the season part are unchanged.
- Release branch: b2tools/release_kit/next/seasons.patch (sapphire-ruby). Test ROM: Sapphire_SEASONS_OPTION_TEST.nds.

## How Black 2 picks the season [code]
- `Season_GetRealTime` (arm9 0x02034f6c) returns `(month - 1) & 3` from the DS clock (read with armdis: `ldr r0,
  [sp,#4]` = month 1-12, `subs r1, r0, #1`, `ands` with 3). So **Jan/May/Sep = spring, Feb/Jun/Oct = summer,
  Mar/Jul/Nov = autumn, Apr/Aug/Dec = winter** (0-3).
- The season the game uses (`GameData_GetSeason`, GameData +0x1c8) is **set from the clock every time the game
  starts**: `GameData_Create` (arm9 0x02016f04) stores `Season_GetRealTime()` there. Nothing else writes it except
  `Season_Set`, called only by the new-game opening (ov035 0x217c9b8) and by warps (0x217d122). No save-file field
  was found, so the season is not in the save.
- If the month changes while you play, the next warp into an outdoor area plays the season card ("Autumn") and
  switches (`EventMapChange_LoadSeasons`, ov035 event_mapchange.c:386, then :493-503).
- On Continue, Black 2 shows the season card once. **Already removed** for Hoenn by patches/hoenn_intro.py (transition
  3 -> 0), so loading a save is silent (user decision 2026-10-06). The new-game season card is removed there too.
- `GameSystem_GetSeason` (arm9 0x02034f20) goes through the comm system to `GameData_GetSeason` (ov012
  getSeasonFromPlayerData 0x02153640), so every reader (textures, lights, weather, encounters, music, buildings' night
  windows, map swaps) sees the same season.

## 1. Texture sets
Area 2 (Hoenn's overworld, world.json "area") has four records in a/0/1/3; the game loads record `2 + season`
(`AreaData_Create`, seasonal for 2 <= id < 0x11a; Black 2's zone headers all name the spring record, id = 2 mod 4):

| Season | Record | Map texture set | Lights | Building pack |
|---|---|---|---|---|
| spring | 2 | 2 | 140 | 0 |
| summer | 3 | 3 (Hoenn's, merged) | 141 | 0 |
| autumn | 4 | 4 | 142 | 0 |
| winter | 5 | 5 | 143 | 0 |

- Black 2's four sets hold the same 112 names. Hoenn adds 26 to set 3 (19 from terrain modules' other Black 2 sets,
  7 ash copies). Buildings use pack 0 in all four seasons, so they need nothing.
- **Yes, the same merge works** (`seasonal_sets` in patches/hoenn_textures.py, switch `HOENN_SEASONS=1`): each season's
  set keeps Black 2's own art for its 112 names, gets the terrain modules' textures from the same Black 2 area's set for
  that season when it has one with the same size (in practice only Route 7's very tall grass `nagakusa01a/b` differs:
  Humilau's palms, Route 4's sand, Route 13/Undella's sea and the out57 cliffs are identical in all four), and gets
  the ash copies unchanged (ash all year). `c8k_grass01ax` (ash grass) is kept the same on purpose (`SEASON_KEEP`).
  The function asserts every summer name is in each set (a missing one would draw flat white).
- **Sizes (offline run on Black 2's files + the release's pack 0)**, budget ~200 KB for map + building textures
  (notes/RESEARCH_WORLD.md, VRAM measured):

| Set | Black 2 | With Hoenn's | + buildings (pack 0, 102,580 B) |
|---|---|---|---|
| spring 2 | 53,424 | 73,096 | 175,676 |
| summer 3 | 53,184 | 72,856 | 175,436 (today's release, same bytes) |
| autumn 4 | 53,072 | 72,744 | 175,324 |
| winter 5 | 53,152 | 72,824 | 175,404 |

  All fit, with the same ~24 KB to spare as summer today. a/0/1/4 grows by ~59 KB inside its 4 MB reserve (about
  4.0 MB free), so the ROM layout and savestates stay the same.
- With the switch off, the patch writes byte-identical a/0/1/4 to the lead's tree (sha1 6dd9a107... both).
- What changes on Hoenn's maps (textures Hoenn's chunks really use): grass `grass01ax`, cliff-top grass `gake1_1`,
  trees `ki03ax/bx/dx`, `ki02c`, tall grass `kusa_ec1/2`, very tall grass `nagakusa01a/b`, paths `michi01a/b`,
  `michi_hage`, flowers `hana01.1`, `plant01`, the bridge `hashi01a`, ponds `ike01` (autumn) and `mizutama01`.
  Sea, shore, sand, cliffs, rock, palms and the ash stay the same. Proof sheet:
  work/agents/seasons_study/season_textures.png (16 textures x 4 seasons).
- **Black 2's own winter on these textures has no snow**: Black 2's snow comes from the `kisetu_yuki` patches (a decal
  only its own chunks use) and from swapped winter chunks (a/0/1/0, e.g. Route 1's chunk 3 -> 277). So Hoenn's winter is pale, dull green with dark blue-green
  trees, not white. Spring is bright green, autumn orange-brown trees and yellow grass.

## 2. Everything else that follows the season
| Thing | What Black 2 does | Hoenn |
|---|---|---|
| Lights | the area record's lights (140-143) and the hour table `day_part` (arm9 0x0208ff98): spring morning 5, day 10, evening 17, night 20; summer 4/9/19/21; autumn 6/10/17/20; winter 7/11/17/19 | automatic; nights start at 19:00 in winter instead of 21:00 |
| Wild Pokémon | `EncData_Load` reads table `season` of a 4-table file, table 0 of a 1-table file | our files hold 1 table or 4 identical copies (converter/gen_encounters.py): same Pokémon all year, no work. The Pokédex area pages say "same in every season" |
| Music | zone header bgm0-3 = spring-winter; only `GetRegularZoneBGMID` reads them (scan: the only caller of `DecideZoneHeaderBGMID`) | hoenn_music keeps the Hoenn song in bgm2 (autumn); **with the Unova option autumn would play the Hoenn song and spring/winter the reused zone's own**. Fixed behind the switch: `Music_ZoneBGM` asks field 1 (summer) for the Unova option, exactly today's music. Hoenn option unaffected. Same code size (2,928 B) |
| Place-name banner | name + season part | the season part is hidden (hoenn_season.py `banner_without_season`, kept in the prototype). User choice whether to show "WINTER" etc. again |
| Season card | on warps into outdoor areas when the month changed mid-session; on Continue | Continue: already removed. Warps: kept in the prototype (it is when the world changes) |
| Deerling / Sawsbuck forms | follow the season (`TransformVsPokePartyBySeason`) | not in Hoenn's data; a traded-in one changes form, as in Black 2 |
| Winter-only map swaps (a/0/1/0) | condition 0 = season, keyed by matrix id | Hoenn's matrices (416+) have no season entries (hoenn_world asserts none before adding Route 131's event swap): nothing changes |
| Snow footprints, winter grass rustle | ov012 field_actor_tool.c by tile class in winter | Black 2's rule on Black 2's tile classes; harmless |
| Calendar weather (24 zones, a/0/9/6) | used while the kept season equals the clock's | date-based, same as now (with the lock both were always summer, so it was always used; it still is) |
| Lens flare, weather system, building night windows | take the season / day period | automatic |

## 3. Special cases
- **Ash** (Route 113, Jagged Pass, Mt. Chimney): renamed copies of Icirrus's winter art, copied unchanged into all
  four sets: ash all year. Their green neighbours change with the season.
- **Beaches and the sea**: the sea, shore and sand textures are the same in all four Black 2 sets, and palms are
  Humilau's (same all year). In winter the beaches stay sandy, the sea blue, the grass dull green: no snow anywhere.
  Real snow would need snowy winter art (for example Icirrus's set 45) for the winter set, which would also put snow
  next to the beaches (one texture set per area for the whole overworld). Recommend Black 2's mild version.
- **Caves and rooms**: every Hoenn room and cave uses a fixed area (282-388, release ROM), unaffected, except two link
  rooms: DoubleBattleColosseum (zone 33, area 186) and RecordCorner (501, area 274) keep Black 2's seasonal areas; patches/interiors.py already merges into all
  four of their sets.
- **Warp-only outdoor maps** (Petalburg Woods, Jagged Pass, Mt. Chimney, Mt. Pyre outside and summit, Safari Zone, Sky
  Pillar, Southern Island, Sootopolis, Battle Tower outside, Faraway/Birth Island, Navel Rock): areas 407/408, fixed
  (not seasonal) copies of summer. They stay summer in the prototype. Making them seasonal: move them to two free
  seasonal area groups (4 records + 4 sets each, built the same way); hoenn_world.py and standalone.py assert
  area >= 282 today.
- **Emerald**: same layout (area 2 + 407/408, work/world_emerald), the same terrain-module texture lists; the patch
  applies to the main tree cleanly (`git apply --check`). Needs its own build and look.

## 4. Risks
- **Saves**: no change to the save. Old saves load in the current month's season; no card on Continue.
- **Existing players**: nothing changes in October (summer). From November they see autumn, then winter in December,
  spring in January. Players on real DS hardware get the DS clock's season.
- **Menu-save margin**: no save data or field-heap change except the texture file size (spring set +240 B over
  summer's, the others smaller). The build prints the margin; expect it unchanged.
- **ITCM**: nothing added (the summer lock's two 8-byte arm9 patches are simply not applied; music code same size).
- **Changing the DS date** trips Black 2's clock-change check (some daily things wait a day): fine on a test copy.
- **Savestates** keep the season they were made in; the next outdoor warp then shows the card and switches.

## 5. Effort and recommendation
- Prototype (done, behind `HOENN_SEASONS=1`): lift the lock, three seasonal texture sets, music fix. About an hour of
  build and a short melonDS look per season once disk allows.
- Full version: the warp-only maps on seasonal areas, the user's choices (banner season, warp card, snow or not),
  Ruby and Emerald builds, then one look per season at a handful of places (Littleroot, a tall-grass route, a pond,
  Route 113's ash, Fortree, a beach, Petalburg Woods, Mt. Pyre). Roughly one or two agent sessions plus one round of
  user testing per version. No risky code: Black 2 does the work.
- **Recommendation: do it** as a Sapphire/Ruby (and Emerald) update, with Black 2's mild winter (no snow), the banner
  without the season part, the warp card kept, and the warp-only maps made seasonal too.

## Files of the prototype (behind HOENN_SEASONS=1; superseded by the option above)
In the worktree work/agents/seasons_study/wt (sapphire-ruby fb0dc0a); also as work/agents/seasons_study/seasons.patch
(applies to main cleanly):
- b2tools/patches/hoenn_season.py: `seasons_on()`; with it, the two arm9 summer patches are skipped.
- b2tools/patches/hoenn_textures.py: `seasonal_sets()`; switch off = byte-identical output.
- b2tools/patches/hoenn_music.c / hoenn_music.py: `-DHOENN_SEASONS=1`, Unova option keeps the summer field.
Build: `zsh work/agents/seasons_study/build_test_rom.sh` (refuses under 5 GB free) -> ~/Desktop/Sapphire_SEASONS_TEST.nds.

## Testing the ROM in melonDS
melonDS 1.1: Config -> Date and time..., set a date (June = summer, November = autumn, December = winter, May =
spring), OK, then System -> Reset (the season is read when the game starts). Continue a copy of a save (rename it
Sapphire_SEASONS_TEST.sav), fly to Littleroot / Oldale and walk Route 101. Look for: grass and tree colours per season,
tall grass and paths, Route 113's ash still grey, beaches and sea unchanged, no flat-white patches, no season card on
Continue, the same wild Pokémon and music. Finally "Reset to system date and time".
