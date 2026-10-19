# The Battle Frontier's shared systems (frontier_core, 2026-10-12)

Pokémon Emerald NDS only (`HOENN_VERSION=emerald`). Sapphire and Ruby never build any of this.
Status markers: **[built]** = in the tree and tested in game, **[built, untested]**, **[planned]** = the interface is
fixed (names, numbers, meaning) but the code is still being written. Facility agents can write scripts against
[planned] interfaces now; this note is updated as each part lands.

Facility agents: frontier_factory_dome (Factory, Dome; Black 2's PWT engine), frontier_pike (Pike). Later: Palace, Arena,
Pyramid. The Battle Tower is HoennB2's Sapphire tower on Black 2's Subway engine (notes/BATTLE_TOWER.md); in Emerald it
also uses this library (example facility).

## 1. Battle Points (decision)

**Emerald's BP are Black 2's own BP.** Black 2 keeps one BP purse: a u16 at the start of its Battle Subway score save
block (save block 0x39 +0; arm9 func_0200e318 adds and caps at 9,999, func_0200e330 subtracts, func_0200e354 reads;
the decomp names the block in include/save/bsubway_save.h). Why it fits:
- the same cap as Emerald (MAX_BATTLE_FRONTIER_POINTS 9,999) and one purse for every facility, as Emerald;
- Black 2's shop screen already sells for BP (ShopUI_LoadBPShopItems, ov036; shop ids 253/254, the BP shown in the
  corner, the BP taken on purchase), and its trainer card counts BP earned (record 0x21);
- the PWT (open behind the Ranking Hall in the Emerald build) and the Battle Tower pay into the same purse, so every
  battle facility on the island counts toward the Exchange Service Corner.
Nothing is converted: a Black 2 BP is an Emerald BP.

## 2. Script interface: `src/include/hoenn_frontier.inc` [built; tested in game 2026-10-12]

**Build**: add `frontier_core` right after `emerald_mech` in your build's patch list (the lead adds it to
story_build.sh / rebuild_slice.sh; frontier_core's own test build: work/agents/frontier_core/tools/build.sh). Tested
(screenshots/frontier_core/): BP added, the BP shop (one Protein bought: 100 -> 99 BP), a BP tutor (Body Slam taught
to Mudkip: 99 -> 51 BP; "welcome back" the second time), the BP window, the record area and the BP kept through a menu
save + cold boot + Continue (the 252-byte block loads), the Battle Tower lobby flow up to the first battle's start.
Not yet seen in game: `fr_give_points` (the BP award by Emerald's table: needs a won challenge), `fr_pick_party`
(the Tower uses its own Subway pick), `fr_lobby_returned` (the Tower keeps its own state), `fr_rest_and_quit`.

Include after `hoenn_story.inc` and `hoenn_emerald.inc`. The commands exist only in Emerald builds
(`b2tools/patches/frontier_core.py` + `.c`, in the patch lists after `emerald_mech`). Scratch works: the macros use
`FR_T0`-`FR_T3` (0x8048-0x804B) and `FR_PICK` (0x804C-0x804F); HLIB_TMP is left alone.

### 2.1 Two script commands
Both replace Black 2 trainer-card item checks no Black 2 or Hoenn script uses (TrainerCardCmd_00E6 / _00E8); their
argument kinds stay (any, var), so script_check decodes them; allowed in normal, zone-init and global scripts.
- **230 `FrGet key, var`**: var = the value of `key` (a record key, or a computed key below; key may be a work).
- **232 `FrOp op, var`**: does `op` with var as its input, and writes its answer back into var.

### 2.2 The record area (keys 0-95)
The Frontier's save data lives in the unused tail of Black 2's Battle Subway play block (save block 0x38): Black 2
uses 60 bytes of its 256-byte slot; the Emerald build declares the block 252 bytes long (SaveData_BuildTable rounds
size + 4 up to 256, so no other block moves). Black 2's code never reads past byte 60 (its clear of the block, run when
a Battle Tower challenge ends, clears only 60); a new game clears all of it. An Emerald save made with a ROM before
frontier_core has the old block size, so its check value no longer matches (expected: start a new game; not tested).
96 u16 keys:

| key | name (hoenn_frontier.inc) | meaning |
|---|---|---|
| 0 | `FR_STATUS` | the challenge status (Emerald's CHALLENGE_STATUS_*): `FR_ST_NONE` 0, `FR_ST_SAVING` 1 (entered and saved in the lobby; seen on Continue = quit without saving), `FR_ST_PAUSED` 2 (saved and quit mid-challenge), `FR_ST_WON` 3, `FR_ST_LOST` 4 |
| 1 | `FR_FACILITY` | `FRONTIER_FACILITY_*`: 0 Tower, 1 Dome, 2 Palace, 3 Arena, 4 Factory, 5 Pike, 6 Pyramid |
| 2 | `FR_BATTLE_MODE` | `FRONTIER_MODE_*`: 0 singles, 1 doubles, 2 multis, 3 link multis |
| 3 | `FR_LVL_MODE` | `FR_LVL_50` 0, `FR_LVL_OPEN` 1 |
| 4 | `FR_PARTY` | the picks: (slot1+1) \| (slot2+1) << 4 \| (slot3+1) << 8 (0 = none); `fr_get FR_GET_PICK \| i` reads pick i |
| 5 | `FR_BATTLE_NUM` | the round / room inside the current challenge (the facility's own use) |
| 6 | `FR_SYMBOLS` | bit 2f = facility f's Silver Symbol, bit 2f+1 its Gold Symbol |
| 7 | `FR_LAST_BP` | the BP the last award paid |
| 8 | `FR_BRAIN_BEATEN` | set it to 1 when the challenge just won ended with the Brain: the lobby says the Brain line and pays +10 BP |
| 9 | spare | (frontier_core's test switch used it; free) |
| 10 | `FR_TUTOR_MET` | bit 0 / 1: the left / right BP tutor has been met |
| 11-15 | spare | |
| 16 + 8f + 4m + 2l | `fr_streak(f, m, l)` | facility f's **current** streak in battle mode m (0 singles, 1 doubles), level mode l |
| 17 + 8f + 4m + 2l | `fr_best(f, m, l)` | its **best** streak |
| 72-95 | extras | claimed in section 6 |

Streak units are Emerald's per facility: battles won for the Tower, Palace, Arena, Factory and Pyramid; tournaments won
for the Dome; rooms cleared for the Pike (pokeemerald GiveBattlePoints divides by 7, 1, 14). The macros below take the
level mode from `FR_LVL_MODE`.

### 2.3 Macros
| macro | does |
|---|---|
| `fr_get KEY, var` / `fr_set KEY, value` | read / write a key (value: a number or a work) |
| `fr_bp var` | var = the player's BP |
| `fr_add_bp value` | BP += value (cap 9,999; the trainer card's BP record too) |
| `fr_take_bp cost, result` | result = 1 and the BP taken when the player has `cost`, else 0 and nothing taken |
| `fr_streak_win FAC, MODE` | the current streak + 1, the best follows; FR_T0 = the streak |
| `fr_streak_reset FAC, MODE` | the current streak = 0 |
| `fr_streak FAC, MODE, var` / `fr_best FAC, MODE, var` | read them |
| `fr_give_points brain=0` | Emerald's GiveBattlePoints: BP from pokeemerald's sBattlePointAwards (30 rows) for `FR_FACILITY` / `FR_BATTLE_MODE` / `FR_LVL_MODE` and the current streak (row = streak / 7, 1 or 14, minus one unless 0, as Emerald; fixed 2026-10-12, checked against pokeemerald for every facility, mode and streak 0-300: work/agents/frontier_core/tools/bp_check.py), +10 when brain = 1; FR_T0 = the BP, also word 1 (for "obtained {N} Battle Point(s)") |
| `fr_give_points_for streak, brain=0` | the same with the facility's own streak count (the Battle Tower: Black 2's Subway streak) |
| `fr_check_party lvl, result` | result = Pokémon eligible under Emerald's rules (CheckPartyIneligibility: not an Egg, not banned, level <= 50 in Lv. 50, no species or held item twice) |
| `fr_pick_party need, cancel` | Black 2's battle-entry screen (emerald_mech's EmPickParty, numbered picks, CONFIRM/CANCEL) with the Frontier's rule: exactly `need`, Lv. 50 = level 50 or less, no species or held item twice, the banned list; the picks go to `FR_PARTY`; CANCEL/B -> `cancel` |
| `fr_symbol_get FAC, var` (0 none, 1 silver, 2 gold) / `fr_symbol_give FAC, gold` | the symbols |
| `fr_save_game result` | Black 2's save dialog (global 2003); result 0 = saved |
| `fr_save_quiet` | a save without the dialog (the caller says "SAVING...") |
| `fr_bp_window` | Black 2's money window (top right) showing the BP ("N BP", the shop's own line); close with `MoneyWinClose` |
| `fr_soft_reset` | Black 2's soft reset (as the Subway's) |
| `fr_rest_and_quit zone, x, z, dir, saving, who` | Emerald's pause: FR_STATUS = PAUSED, Continue in the lobby at (x, z) (Black 2's next zone + flag 2405, as the Battle Tower's rest), the save, the soft reset |
| `fr_lobby_attendant ...`, `fr_lobby_returned ...` | the lobby: section 3 |
| `fr_bp_shop SHOP, welcome, bye`, `fr_bp_tutor SIDE, tt` | section 4 |
Raw ops for C-free special cases: `FrOp FR_OP_*` / `FrGet FR_GET_*` (listed in hoenn_frontier.inc).

### 2.4 Rules shared by all facilities
- **Level 50**: only Pokémon of level 50 or lower (pokeemerald AppendIfValid: `monLevel > FRONTIER_MAX_LEVEL_50` is
  ineligible; Black 2's regulation level mode 2, "50 or less"). **Open Level**: any level.
- **Banned**: Black 2's own Battle Subway list (arc 106 file 20, read at build time): Mewtwo, Mew, Lugia, Ho-Oh, Celebi,
  Kyogre, Groudon, Rayquaza, Jirachi, Deoxys (= Emerald's gFrontierBannedSpecies, exactly) and the Gen 4/5 species Emerald
  never had: Dialga, Palkia, Giratina, Phione, Manaphy, Darkrai, Shaymin, Arceus, Victini, Reshiram, Zekrom, Kyurem,
  Keldeo, Meloetta, Genesect.
- **No duplicates**: no species twice, no held item twice (no item is fine), as Emerald's AppendIfValid; the pick screen
  enforces the same (regulation bytes 8/9 = 0, as every Subway rule). No banned items (Black 2's Subway rule bans the
  Soul Dew; Emerald bans none).
- **Three Pokémon** (FRONTIER_PARTY_SIZE); Eggs never. Emerald's "not enough eligible" line names the banned species
  the player has caught: "Eggs{STR_VAR_1} ineligible." keeps word 1, which `fr_lobby_attendant` fills
  (`FrGet FR_GET_BANNED_NAMES | 1`: the caught banned species in Emerald's order, joined as Emerald's
  AppendCaughtBannedMonSpeciesName does, then "are"). Tested: "Eggs and Mewtwo / are ineligible."
- **The Steven tag battle is not a Frontier battle**: emerald_mech's pick menu (EmPickParty without PICK_FRONTIER) lets
  any Pokémon but an Egg or a fainted one join, legends and the same species twice included (tested), as Emerald's
  ChooseHalfPartyForBattle.

## 3. The lobby [built; the receptionist flow tested on the Battle Tower]
A facility's lobby uses two macros expanded in its own zone script, with its own text lines in a fixed order: the
**lobby text block**, 23 lines (`FRT_*` in hoenn_frontier.inc): welcome, take the challenge?, info, which level?, not
enough (Lv. 50), not enough (Open), choose the Pokémon, save before?, step this way, goodbye, didn't save, won, won
against the Brain, award BP, record (after a win), lost, resume, the menu words CHALLENGE / INFO / EXIT / LV. 50 / OPEN
LEVEL, "{player} obtained {N} Battle Point(s)". `python3 b2tools/frontier_text.py lobby <pokeemerald lobby map>
[ROLE=Label ...]` prints them converted (guesses each role's label; name it when the guess is wrong; a role the lobby
has no line for prints "…").
- **`fr_lobby_attendant fac, mode, tb, enter, pick=3, onpick, onunpick, onsave, track=1`**: the receptionist, Emerald's
  flow: welcome, CHALLENGE / INFO / EXIT, LV. 50 / OPEN LEVEL / EXIT, the eligibility check, the pick (`pick` Pokémon;
  0 = none, e.g. the Factory's rentals; or the facility's own via `onpick`), "the game must be saved" YES/NO, Black 2's
  save dialog, "step this way", then `VMJump enter` (the facility walks the player in and warps). Sets FR_FACILITY,
  FR_BATTLE_MODE, FR_LVL_MODE, FR_PARTY, and FR_STATUS = SAVING before the save (track=1). Hooks are labels the macro
  VMCalls: `onpick` (FR_T0 = the level mode; set FR_T1 = 1 picked / 0 cancelled), `onunpick` (NO to the save or the save
  refused), `onsave` (just before the save).
- **`fr_lobby_returned fac, mode, tb, who, resume, onquit, onwon, onlost, me=MUS_OBTAIN_ITEM`**: the lobby's map-script
  condition script (run once per visit, as Emerald's OnFrame table): FR_STATUS of this facility -> quit without saving
  (the line, the current streak ends), won (congratulations or the Brain line, "we award you these Battle Points",
  Emerald's BP, the record saved), lost (the line, the streak ends, saved), paused ("waiting for you", FR_STATUS back to
  SAVING, saved, `VMJump resume`). `who` = the receptionist's uid. Hooks: `onquit`, `onwon`, `onlost`.
- The facility's battle rooms: `fr_streak_win` after each win (in Emerald's units), FR_STATUS = FR_ST_WON / FR_ST_LOST
  (and FR_BRAIN_BEATEN) before warping back to the lobby, `fr_rest_and_quit` for "save and quit".
- **Example: the Battle Tower** (src/field_scripts/0042_room_BattleTower_Lobby.s, `#ifdef HOENN_EMERALD`): the
  receptionist is `fr_lobby_attendant` with the tower's Black 2 Subway steps as hooks (its own pick screen and status);
  its seven-win return pays Emerald's BP (`fr_give_points_for` with the Subway's streak) instead of Sapphire's prize.
  Its 24 Emerald lines are appended to the lobby's text by `b2tools/frontier_text.py install`
  (src/text/emerald/overrides_frontier_core.json). Lv. 50 = the Lv. 50 room; Open Level = the Lv. 100 room (Black 2
  play mode 5) with Emerald's level rule (pokeemerald GetFrontierEnemyMonLevel): the opponents are at the highest level
  of the three Pokémon entered, at least 60 (frontier_core.c FR_TowerLevel, in place of battle_tower.py's 50 + 10 x mode
  at ov012 0x02161fac; Sapphire and Ruby keep their Lv. 100 room). Tested: Metagross Lv. 72 entered, Golduck Lv. 72.

## 4. Exchange Service Corner, BP tutors [built; tested in game]
The room: zone 419 (frontier_core_room: data/interior_layouts/BattleFrontier_ExchangeServiceCorner.json,
data/interiors/emerald/419.json, door = BattleFrontier_OutsideEast warp 6), zone script
src/field_scripts/emerald/0838_room_BattleFrontier_ExchangeServiceCorner.s, text
src/text/script/emerald/0648_room_BattleFrontier_ExchangeServiceCorner.txt (b2tools/frontier_text.py install). The two
BP tutors sit on Emerald's empty west bench (zone tiles (1,7), (1,8)), talked to from the east.
- **BP shops**: `fr_bp_shop SHOP, welcome, bye`: Emerald's welcome line, Black 2's BP shop screen (BP shown in the corner,
  BP paid, Black 2's quantity and "not enough BP" / bag checks), Emerald's goodbye. `FR_SHOP_VITAMINS` 240 (Protein, Calcium, Iron,
  Zinc, Carbos, HP Up: 1 BP each), `FR_SHOP_HOLD_ITEMS` 241 (Leftovers, White Herb, Quick Claw, Mental Herb 48 BP; Bright
  Powder, Choice Band, King's Rock, Focus Band, Scope Lens 64 BP), in Emerald's order, read from pokeemerald at build time.
  How: ShopUI_Init's call of ShopUI_LoadMsgData (ov036 0x021abf68) -> FR_ShopMsgData: these ids load Emerald's list into
  Black 2's BP list 0 and continue as shop 254; every shop first gets Black 2's list back, so the PWT's BP clerks keep
  Black 2's prizes.
- **The two decoration clerks are not placed** (the user, 2026-10-12: Black 2 has no decorations); their script numbers
  1 and 6 stay unused.
- **BP tutors**: `fr_bp_tutor SIDE, tt` (the first talk is kept in record key 10, `FR_TUTOR_MET`): Emerald's flow (intro once / welcome back, "which move?" with the BP
  window and a list of the ten moves with prices, "That will be N Battle Points, okay?", not enough BP, "pick the
  Pokémon", then emerald_mech's tutor global 2289 (pokeemerald's sTutorLearnsets for all 30 tutor moves now, "not
  compatible" / "already knows" / forget a move), the BP taken only when taught. Side 0 (left): Softboiled 16, Seismic
  Toss 24, Dream Eater 24, Mega Punch 24, Mega Kick, Body Slam, Rock Slide, Counter, Thunder Wave, Swords Dance 48; side 1
  (right): Defense Curl 16, Snore, Mud-Slap, Swift, Icy Wind 24, Endure, Psych Up, Ice Punch, Thunder Punch, Fire Punch
  48. Text block (19 lines): `python3 b2tools/frontier_text.py tutor 0|1`.

## 5. Music, Frontier Brains
- **Music [installed 2026-10-12, frontier_core_music; tested in game: see the end of this bullet]**: all 13 Frontier
  songs, converted from the user's Emerald dump (data/emerald/hoenn_music.json: songs, slots, gains). Emerald's sound
  archive grows by 4 MiB (data `archive_reserve`, patches/hoenn_music.archive_reserve, Emerald only): 89,373,024 ->
  93,567,328 B; 2,302,884 B of new files sit there, 1,889,884 B stay spare for later Emerald songs. This moved the
  Emerald ROM's file layout once: Emerald savestates made before it need remaking. The 10 voices Black 2 has no
  instrument for (choir, female voice, gamelan, electric piano, distortion / overdrive guitars, shakuhachi, koto) play
  Emerald's own samples with their own envelopes (b2tools/m4a_emerald.py EmeraldSong). Sound memory: one song gets about
  282 KB; the largest is the Pyramid's at 250,848 B (its 6 tom notes on two toms, its 6 Chinese-cymbal notes on the crash).
  Zones (data `zone_songs`, Hoenn answer): the island (17, both halves) mus_b_frontier; the Battle Tower lobby 21,
  elevator 343, corridor 336, battle room 15 Emerald's tower song; the Exchange Service Corner 419 Ruby/Sapphire's tower
  song (Emerald's mus_b_tower_rs, also its lounges, Reception Gate and Scott's house: add their zones to `zone_songs`
  with "mus_b_tower" when they get zones). A facility room gets its song by a `zone_songs` line in
  data/emerald/hoenn_music.json ("<zone>": "<song key>"); scripts play the sequence id (playbgm / MEPlay + MEWait for the
  two fanfares, which end; with the Unova answer they become Black 2's SEQ_ME_BADGE / SEQ_ME_BPGET through `reverse`).

| song (data key) | where Emerald plays it | Black 2 sequence id (slot) | bytes | ends? |
|---|---|---|---|---|
| mus_b_frontier | island outside | 2398 (SEQ_SE_SW_KYUREON_03_02) | 228,980 | loops |
| mus_b_tower_frontier (Emerald's mus_b_tower, 465) | Tower lobby, elevator, corridor, battle rooms | 2405 (SEQ_SE_SW_KYUREON_03_07w) | 240,752 | loops |
| mus_b_dome | Dome battle room, pre-battle room | 2324 (SEQ_SE_SW_FRIGATE_02) | 235,936 | loops |
| mus_b_dome_lobby | Dome lobby, corridor | 2328 (SEQ_SE_SW_FRIGATE_06) | 113,676 | loops |
| mus_b_factory | Factory lobby, pre-battle, battle room | 2326 (SEQ_SE_SW_FRIGATE_04) | 234,260 | loops |
| mus_b_pike | every Pike room | 2325 (SEQ_SE_SW_FRIGATE_03) | 173,472 | loops |
| mus_b_palace | Palace lobby, corridor, battle room | 2404 (SEQ_SE_SW_KYUREON_03_07b) | 166,384 | loops |
| mus_b_arena | Arena lobby, corridor, battle room | 2400 (SEQ_SE_SW_KYUREON_03_04) | 175,868 | loops |
| mus_b_pyramid | Pyramid lobby; floors by script (playbgm) | 2402 (SEQ_SE_SW_KYUREON_03_06b) | 250,848 | loops |
| mus_b_pyramid_top | Pyramid top, by script (playbgm) | 2403 (SEQ_SE_SW_KYUREON_03_06w) | 102,516 | loops |
| mus_vs_frontier_brain | Frontier Brain battles (pokemon.c GetBattleBGM) | 2327 (SEQ_SE_SW_FRIGATE_05) | 243,436 | loops |
| mus_obtain_symbol | symbol given (playfanfare) | 2323 (SEQ_SE_SW_FRIGATE_01) | 186,480 | ends |
| mus_obtain_b_points | BP given (playfanfare) | 2401 (SEQ_SE_SW_KYUREON_03_05) | 167,736 | ends |

`hoenn_frontier.inc` names them: `FR_ME_OBTAIN_BP` 2401 (now the default fanfare of `fr_lobby_returned` and the
Battle Tower's Emerald BP award), `FR_ME_OBTAIN_SYMBOL` 2323, `FR_BGM_*` for the songs.
In game (2026-10-12, one Emerald test build with the music test kit, muted DeSmuME, Hoenn music answer;
work/agents/frontier_core/music/ingame/, comparison out/ingame_compare.json): the grown archive loads; the island
(zone 17) plays mus_b_frontier and the Tower lobby (zone 21) Emerald's tower song (each recording matches its own song's
GBA render 0.83, other Frontier songs at most 0.42); mus_obtain_symbol and mus_obtain_b_points play as fanfares and end
(the script's MEWait returns, Littleroot's song comes back); mus_b_arena (koto, shakuhachi: Emerald's own samples) plays
(0.81). Sound memory: room for one song 281.7-281.8 KB (zone songs); a fanfare pushed over a song gets the song's room
(the song's data is freed while the fanfare plays).

- **Frontier Brains [installed, not yet seen in game]** (frontier_core_sprites, b2tools/sprite_emerald_frontier.py;
  Emerald's own pictures from the user's dump, resized as sprite_emerald.py, nothing redrawn; review sheet
  screenshots/frontier_core/brains_review.png). Each front picture sits on the own picture of a spare Black 2 class
  (class c shows picture c), so a Brain battle needs that class (name, sex, music: data/emerald/hoenn_trainer_classes.json):

| Brain | facility | trainer class = front picture | walking sprite code (data/emerald/sprite_map.json `OBJ_EVENT_GFX_*`) |
|---|---|---|---|
| Anabel (Salon Maiden) | Tower | 9 | 56 |
| Tucker (Dome Ace) | Dome | 7 | 99 |
| Spenser (Palace Maven) | Palace | 8 | 107 |
| Greta (Arena Tycoon) | Arena | 34 | 207 |
| Noland (Factory Head) | Factory | 33 | 298 |
| Lucy (Pike Queen) | Pike | 31 | 299 |
| Brandon (Pyramid King) | Pyramid | 30 | 300 |
  Check the slots are still free before using them: `python3 b2tools/sprite_emerald_frontier.py check`. In use: the
  Pike's Lucy (class 31, sprite 299), the Factory's Noland (class 33, sprite 298) and the Dome's Tucker (class 7, sprite
  99; patches/frontier_factory_dome.py since 2026-10-12); the Tower's Anabel (class 9, sprite 56; 2026-10-18, below).
- **The Battle Tower's Salon Maiden Anabel [built 2026-10-18, compiled, not played]**: src/field_scripts/0030_room_
  BattleTower_BattleRoom.s (`#ifdef HOENN_EMERALD`) as pokeemerald's BattleFrontier_BattleTowerBattleRoom: her status
  by GetFrontierBrainStatus with sFrontierBrainStreakAppearances[TOWER] {35, 70, 35, 1} on Black 2's Subway streak
  (command 358: battle 35 = the 7th battle of the 5th set for the Silver Symbol, battle 70 for the Gold; with both, 35,
  70 and every 35th after), the attendant's "Salon Maiden is on her way" / "prepared?" (YES/NO, the tower's questions),
  her slow walk-in (sprite 56), her first / Gold intros once (record key 9 bits 12/13), the battle (frontier_palace_
  arena.c `FrontierPA PA_TOWER_BATTLE`: sFrontierBrainsMons[TOWER] with their IVs, EVs, natures, items, at Lv. 50 or
  the Open Level rule; class 9 "Salon Maiden", name "Anabel"), the Ability Symbol (FR_SYMBOLS bits 0/1, fanfare), her
  closing line, FR_BRAIN_BEATEN; the lobby (0042) says Emerald's "defeated the Salon Maiden" line and pays +10 BP. Lines:
  `python3 b2tools/frontier_text.py tower_room` (src/text/emerald/overrides_frontier_tower.json, the battle room's
  text lines 6-18; src/include/frontier_tower_lines.h). Not done: Emerald's second attendant running in (the room has
  one attendant), her in-battle lines (as Spenser/Greta: none).
  **Classes done** (converter/gen_trainers.py FRONTIER_BRAINS, Emerald only; data/emerald/hoenn_trainer_classes.json,
  src/text/system/emerald/0383/0485): Emerald's names Salon Maiden 9, Dome Ace 7, Palace Maven 8, Arena Tycoon 34,
  Factory Head 33, Pike Queen 31, Pyramid King 30 with their sex; never handed to another Emerald trainer; battle music
  mus_vs_frontier_brain (2327) by data/emerald/hoenn_music.json "classes" (Hoenn music answer). Tested: a class-9 battle
  says "You are challenged by Salon Maiden Bonita!" with Anabel's picture, the song stack plays 2327. A Brain battle
  needs a trainer of that class (the facility's own trainer slot). Tucker and
  Spenser stand still in the battle intro (no Black 2 animation fits their poses).

## 7. Code space: the Frontier code area [built, frontier_palace_arena 2026-10-12]
ITCM is full: an Emerald build of today's lists leaves 256 bytes after rods (arena from 0x1ffff00; emerald_mech grew to
4 KB). Frontier code goes to **main RAM 0x023D0000-0x023E0000 (64 KB)** instead:
- Why it is free: Black 2's heap system takes its root heaps from the bottom of the main arena at boot
  (GFL_HeapMgrInit, fixed sizes); in DS mode the arena is 0x021FD080-0x023E0000 and its start after the heaps is
  0x023A8AC4 (read from the SDK's arena table at 0x023FFDA0 in a running Emerald build). Nothing writes above
  0x023A8F82 from boot through the opening (a RAM scan), and every mem_alloc_direct call runs at boot
  (notes/WORLD.md "Code space"). The area takes the top 64 KB of that slack; about 92 KB stay unused below it.
- Reserved for real: the main arena's end (the literal 0x023E0000 at arm9 0x0207B358, which
  GetUserMemRegionDefaultEnd returns in DS mode) becomes 0x023D0000, so no allocator can reach the area.
- Loaded at boot: main's call of GameInit (arm9 0x0200515C) goes to FRAM_Boot (b2tools/patches/frontier_area_boot.c,
  ~70 bytes of ITCM), which reads the area's image (an arc 211 file after frontier_factory_dome's 1000-1890: a 16-byte
  'FRAM' header, then every user's code and data) to 0x023D0000, flushes the caches and calls GameInit. A soft reset
  restarts main, so the area is reloaded.
- Using it (b2tools/patches/frontier_area.py): in a patch's apply(files), `syms, base, size = frontier_area.add(files,
  name, build)` with build(base, workdir) = frontier_area.compile + frontier_area.link (ordinary non-PIC Thumb code
  linked at its RAM address; writable data and .bss allowed, the area is RAM; Black 2 called by address only); in its
  apply_code(code), `frontier_area.install(code)` (once per build: the first user installs the loader, the others find
  it) and then point Black 2's calls / words at `syms`. Users so far: frontier_pike (7.2 KB, first: its apply runs earlier; only its two battle-line hooks, 0.3 KB, stay in
  ITCM; emerald_itcm 2026-10-12, when sprite_switch's growth overflowed ITCM by 32 B), frontier_palace_arena (8.0 KB),
  emerald_rayquaza_scene; about 48 KB free. frontier_pike installs the loader now (the first user).
- ITCM left (Emerald v1.0.1, emerald_itcm): 7296 B (arena from 0x1ffe380 after rods and frontier_pyramid's 4 B; v1.0
  had 32 B). A patch that wants ITCM for battle-time hooks should still prefer the area: it is resident from boot to
  power-off, in battle too.
- Limits: DS mode measured (the DSi mode's arena starts at 0x0276DDE0, above the area, not measured); savestates made
  before a ROM with the area hold none of it (remake them, as for every ITCM patch).

## 6. Claims (facility agents: add a line)
| what | by | |
|---|---|---|
| Core: zone 419 Exchange Service Corner (header scripts/init/text 838/839/648, own 1976/1977/1003; data/emerald/hoenn_interiors.json "claimed"); record keys 0-15; script commands 230 FrGet, 232 FrOp; ov036 0x021abf68 (ShopUI_Init's ShopUI_LoadMsgData call) hooked; save block 0x38 size 60 -> 252; shop ids 240/241; Brain classes/pictures 7, 8, 9, 30, 31, 33, 34 and walking sprites 56, 99, 107, 207, 298, 299, 300 | frontier_core | this note |
| Pike: zones 399-404 (lobby, corridor, three-path room, room, wild room, final room; data/emerald/hoenn_interiors.json "claimed"), room script/init/text files: sources named by the Black 2 numbers 798-809 / texts 628-633 (src/field_scripts/emerald/, src/text/script/emerald/), installed as the own numbers 1950-1961 / 990-995 | frontier_pike | notes/FRONTIER_PIKE.md |
| Pike: record keys 72-78 and 91-92 (72 hint/door/room state, 73 status room, 74-76 held items kept at entry, 77/78 completed challenges Lv. 50 / Open, 91/92 the trainers met in this challenge, 93/94 the room's two Frontier trainers (their in-battle defeat lines)); uses FR_STATUS, FR_FACILITY 5, FR_LVL_MODE, FR_PARTY, FR_BATTLE_NUM (room number), FR_SYMBOLS bits 10/11, fr_streak/fr_best(5, 0, l) | frontier_pike | |
| Pike: script command 290 (Black 2's BoxAdd, unused; args var, any, any, any) = `EmPike var, op, a, b`; trainer ids 529-531 (Black 2 ids no Hoenn trainer may take: their defeat flags are the opening's) as the Pike's battle slots (party, class and name filled at battle time; Lucy = Brain class 31, walking sprite 299); calls redirected: arm9 0x02018082/0x02018190 (party load), 0x020182B8/0x02018388/0x020183A0 (trainer load), ov036 0x021A196E (wild setup), 0x021815E6/0x02181AFE (per-step encounter check), ov167 0x021B3B28 (TrainerMsg_CheckExists) and the TrainerMsg_Load call inside trainers.py's rewrite at 0x021D0288 | frontier_pike | |
| Factory / Dome: zones 408-411, 415-417 (Factory lobby, rental room, battle room; Dome lobby, corridor, pre-battle room, battle room; data/emerald/hoenn_interiors.json "claimed"), room script/init files 1962-1975, room texts 996-1002 | frontier_factory_dome | notes/FRONTIER_FACTORY_DOME.md |
| Factory / Dome: record keys 79-90 (79-84 Factory rental mon ids: the player's three, then the last opponent's three; 85/86 Factory swaps count singles / doubles, low byte Lv. 50, high byte Open (Emerald's factoryRentsCount, read as a u8: the rental rank); 87 Factory challenge seed; 88/89 Dome tournament seed (low/high); 90 Dome: the player's seed slot (bits 0-3), Tucker in this tournament (bit 4), the round lost (5-7), Tucker's Gold party (8), tried before (9, 10), the draw's trainer range min(tournaments won, 7) (11-13), doubles (14), Open Level (15)); uses FR_STATUS, FR_FACILITY 1 / 4, FR_LVL_MODE, FR_PARTY (Dome), FR_BATTLE_NUM (Factory battle 0-6 / Dome round 0-3), FR_SYMBOLS bits 2/3 (Dome) and 8/9 (Factory), fr_streak/fr_best(1 or 4, 0, l) | frontier_factory_dome | |
| Factory / Dome: script command 505 (Black 2's Cmd_01F9, unused; args any, any, any, var) = `FrontierCmd sub, a, b, var`; Battle Subway set archive arc 211 files 1000-1889 (Emerald's 882 Battle Frontier sets 1000-1881, Tucker's six 1882-1887, per-set facts 1888, the 300 Frontier trainers' classes, walking sprites and set lists 1889, the engine 1890; converter/gen_frontier_emerald.py -> data/emerald/frontier.json, usable by any facility); ITCM: a 345-byte loader (frontier_fd_stub.c) placed after frontier_core's (0x1ffd9e0 in today's build; the engine itself runs from heap 4); ov012 0x02166082 (the Subway battle's setup call) hooked | frontier_factory_dome | notes/FRONTIER_FACTORY_DOME.md |
| Pyramid (core tested 2026-10-12; status and what is left: notes/FRONTIER_PYRAMID.md): zones 347 lobby, 388 floor, 420 top (data/emerald/hoenn_interiors.json "claimed"), own script/init/text files 2040-2045 / 1035-1037 (sources named by the Black 2 numbers 694/695, 776/777, 840/841, texts 559/600/649) | frontier_pyramid | notes/FRONTIER_PYRAMID.md |
| Pyramid: script command 530 (Black 2's Cmd_0212, unused; args any, any, any; read as var, any, any) = `EmPyr var, op, a`, its EVCMD_PERM_TABLE byte 1 -> 7 (zone inits and field loads run it); trainer ids 532 (the floor's Frontier trainers) and 533 (Brandon) (Black 2 ids no Hoenn trainer takes, as the Pike's 529-531; CallTrainerBattle never sets their flags); save block 0x3e (Black 2's Unity Tower block, 16 B used, nothing of it in Hoenn) grows 16 -> 16 + the Pyramid's state (its 256-byte slot keeps every other block in place); uses FR_STATUS, FR_FACILITY 6, FR_LVL_MODE, FR_PARTY, FR_BATTLE_NUM (floor 0-7), FR_SYMBOLS bits 12/13, fr_streak/fr_best(6, 0, l) | frontier_pyramid | |
| **Code space (frontier_pyramid, 2026-10-12): ITCM is full** (an Emerald build of today's lists leaves 256 B: arena from 0x1ffff00 after rods). The Pyramid keeps only 4 B there (the engine's address, placed after the other ITCM patches: 0x1ffff40 after rods in its own build, 160 B left; with frontier_area's loader it takes 32 of the 64 B left, alignment included; not yet built together); its battle-time hooks live in ov012's dead handlers of script commands 530/531 (0x02164838-0x021649ec: 268 of 436 B used; ov012 is resident in battles); its field-time hooks live in ov036's dead Join Avenue code (func_ov036_021c898c..0x021c8c34, 680 B: Hoenn has no Join Avenue, the RD-chunk call is the floor's own hook) and its engine is a position-independent file loaded into heap 4 (as frontier_factory_dome's). Other facilities: ov036 has more dead Unova-only code; ask before taking 0x021c898c-0x021c8c34 | frontier_pyramid | |
| Palace / Arena (built, tested 2026-10-12): zones 466 Palace lobby, 467 corridor, 468 battle room, 429 Arena lobby, 431 corridor, 433 battle room (data/emerald/hoenn_interiors.json "claimed"), own script/init/text files 2028-2039 / 1029-1034 (sources named by the Black 2 numbers 932-937, 858/859, 862/863, 866/867; texts 192-194, 174, 176, 178); the island doors: zone 17 warp 4 (Palace), 3 (Arena) | frontier_palace_arena | notes/FRONTIER_PALACE_ARENA.md |
| Palace / Arena (built, tested 2026-10-12): record keys 9 (the current opponent: bits 0-9 trainer 0-299 or 1023 the Brain; bit 14 Spenser's first speech heard, bit 15 Greta's) and 11-14 (the trainers met in this challenge, 6 x 9 bits); script command 291 (Black 2's BoxAddEx, unused; args var + 8 any) = `FrontierPA var, sub, a, b`; ov167 hooks (the battle): see notes/FRONTIER_PALACE_ARENA.md; uses FR_STATUS, FR_FACILITY 2 / 3, FR_BATTLE_MODE, FR_LVL_MODE, FR_PARTY, FR_BATTLE_NUM, FR_SYMBOLS bits 4/5 and 6/7, fr_streak/fr_best(2, m, l) and (3, 0, l); reads frontier_factory_dome's arc 211 sets 1000-1881 / trainers 1889 and the Factory battle room's text 998 (names, greetings) | frontier_palace_arena | |
| **Frontier code area (frontier_palace_arena, 2026-10-12): main RAM 0x023D0000-0x023E0000 (64 KB), for any Frontier patch.** Black 2's heaps leave 0x023A9000-0x023E0000 unused in DS mode (measured: the main arena's start after the heaps is 0x023A8AC4, nothing writes above 0x023A8F82 from boot through the intro); the main arena's end (arm9 literal 0x0207B358) moves down to 0x023D0000; a ~70-byte ITCM loader on main's GameInit call (arm9 0x0200515C) reads the area's image (an arc 211 file after frontier_factory_dome's: 'FRAM' header + code) at boot and after every soft reset. Users link ordinary Thumb code there (data and .bss allowed) with b2tools/patches/frontier_area.py (`add` in apply, `install` in apply_code; its docstring). The Palace/Arena code lives there | frontier_palace_arena | notes/FRONTIER.md 7 |
| Battle Tents + Trainer Hill (battle_tents, 2026-10-18; built, test ROM pending the user's melonDS test): zones 519-527 (the three tents' lobby, corridor, battle room: Verdanturf 519/522/525, Fallarbor 520/523/526, Slateport 521/524/527) and 543-549 (Trainer Hill entrance, 1F-4F, roof, elevator; the four modes' floors are each floor's alt rooms on map replace events 3/4/5, shared with the rooms that set them on every load), own script/init/text files 2046-2077 / 1038-1053 (sources named by the Black 2 numbers 1038-1055, 1086-1099; texts 527, 529-536, 112-121); record keys **15** (tents: bits 0-2 a prize waiting per tent, 8/9 Scott met in Verdanturf / Fallarbor), **44** (the tent's opponent and the trainers met), **45-47** (Slateport's rentals), **60-63, 68-69** (Trainer Hill: 60 flags and the beaten trainers, 61-62 the timer, 63/68/69 the four modes' best times; 70-71 stay free) - Arena / Pike / Pyramid doubles streak keys that no facility uses; FR_FACILITY 8/9/10 for the tents (no BP, no streaks); script command **562** (Black 2's Cmd_0232, unused; args any, var) = `ThHill op, var` and its EVCMD_PERM_TABLE byte -> 7; trainer ids **534/535** (the Hill's two battle slots); arc 211 file **1891** (the tents' trainers and sets, after frontier_factory_dome's engine 1890; the FRAM image moved one file on); FrontierPA tent mode (fac | 0x10) and FrontierCmd 60-65 (Slateport); calls chained after frontier_pyramid / emerald_rematch: arm9 0x020182b8 / 0x02018388 / 0x020183a0, ov167 0x021b3b28 and the trainer-line call, ov036 0x021815e6 / 0x02181afe; ~6.5 KB of the Frontier code area; shop ids 23 / 25 (the Hill's Mart lists, the two fillers; a/2/8/2 +40 B) | battle_tents | notes/BATTLE_TENTS.md |
| Battle Tower Anabel (2026-10-18): FrontierPA (command 291) sub-commands 20-22 PA_TOWER_STATUS / BATTLE / HEARD; record key 9 bits 12/13 (her speeches heard); FR_SYMBOLS bits 0/1, FR_BRAIN_BEATEN (the Tower lobby clears it); the Tower battle room's text lines 6-18 (Emerald) | Anabel | section 5 |
- Script command 494 is claimed by emerald_rayquaza_scene (Emerald's Rayquaza cutscene); the scene loads from arc 211 and uses 287 B of the Frontier code area (2026-10-12).
- save_compat (2026-10-18; ON by default in Emerald builds since 2026-10-18, HOENN_SAVE_COMPAT=0 = the old layout; notes/SAVE_PKHEX.md): blocks 0x38 / 0x3e keep Black 2's 60 / 16 bytes (PKHeX), the records move to block 0x38 + 64 (after its footer) and the PySave to 0x3e + 20; record key 95 holds the record area's CRC (keys 0-94 for scripts); ~860 B of the Frontier code area; arm9 hooks 0x0203b854, 0x0203b95e, 0x0200713a, 0x0200732c.
