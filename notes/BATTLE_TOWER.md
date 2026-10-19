# Sapphire's Battle Tower on Black 2's Battle Subway (v16, battle_tower agent, 2026-10-08)

The decision is in notes/DECISIONS.md (2026-10-08, v16). The Battle Tower island (BattleTower_Outside, zone 17) has Sapphire's
tower with its four rooms and Sapphire's flow, run on Black 2's Battle Subway engine. A second building on the island
leads to Black 2's PWT (zones 192/193).

Sources: `bw2/` = `external/pokebw2` (decomp; addresses and names from `config/b2_us/.../symbols.txt` and `relocs.txt`,
asm with `b2tools/armdis.py` on the built binaries); `ruby/` = `external/pokeruby`. Tags: **[code]** read in C/asm,
**[bytes]** read in the data, **[test]** seen in the emulator.

## 1. Black 2's Battle Subway engine (research)

### 1.1 Where it runs
- **Script plugin 1** = ov050 (`scrcmd_bsubway.c`: `BSubwayCmd_Tool` = command 1003, `Plugin1_Cmd1000/1001/1002`). The
  field loads it only in the zones of `sBSubwayZones` (ov012 0x0216c156, file offset 0x1bd96: 11 × u16 = zones 66-76,
  `script_plugin.c`) [code]. Our ROM's zone_effects patch already writes 0xFFFF into entries 0-8 (66-74). The
  battle_tower patch sets entries 9/10 (75/76, Black 2's subway platforms, which no Hoenn map uses) to **21** (lobby) and
  **15** (battle room), the only rooms whose scripts call plugin 1 [code, test].
- **ov033** (`bsubway_scr.c`) has the play state, `BSubwayScrWork` (heap 4 GAMEEVENT, magic 0x12345678; the battle
  setup is at +0x7D0). ov036 `FieldRoutine_Open` loads it whenever the field is open, so ov033 code can be called from
  ov012 at any time [code].
- PWT is separate: script plugin 6 for zones 192/193, gimmick 51/36, ov055/ov134/ov135 (notes/RESEARCH_PWT.md).

### 1.2 `BSubwayCmd_Tool` subcommands used (ov050 `scrcmd_bsubway.c`) [code, test]
| cmd | what |
|---|---|
| 1001 p / 1002 | create the work for play mode p (0 = new; 1 = resume from the play block) / free it |
| 300 | party list (pick 3); the regulation (arc 106) comes from `func_ov012_02165f70` by mode |
| 301 | copy the choice (returns 1 = OK) |
| 359 / 349 | start a streak if none / end the streak (counter 0, round 0) |
| 316 / 317 i | choose the 7 trainer ids (ov033 0x0217c11c) / party slot of member i |
| 306 | save the play block (mode, round, member slots, 14 trainer ids, resume bit) |
| 307 / 308 / 352 | build the round's trainer / its field sprite by class (ov033 0x0217bca0 → ov012 0x02162b38) / its intro balloon (system text 376 line 3·id, param1 = actor uid) |
| 309 / 332 / 347 | battle (ScriptWork_CallEvent `func_ov012_02166070`) / result (1 = won) / free the setup |
| 357 / 358 / 8 / 303 | round+1 and wins+1 (returns wins) / wins / next battle number / round ≥ 7 |
| 304 / 305 | lost (keeps the streak's length, updates the best, counter 0, round 0) / 7 won (set counter + 1) |
| 6 m / 30 m / 7 | stored streak of mode m / completed sets of mode m / end the streak of the play block's mode |
| 1 | `sys_reset` (soft reset) |

Save blocks: **0x39** score (u16[9] at +8 current streak per mode, +0x1A best, +0x2C set counter); **0x38** play block
[code].

### 1.3 Trainers and sets [code, bytes]
- Trainer id t → **arc 212** file t + 1 = `u16 class, u16 count, u16 set ids[count]`; **arc 211** = 16-byte sets:
  `u16 species (11 bits) | form`, 4 × u16 moves, `u8 EV flags` (HP, Atk, Def, Spe, SpA, SpD), `u8 nature`, `u16 item`,
  `u16 form`. Each flagged stat gets min(255, 510 / n) EVs.
- Names: system text **15** line t (7 characters at most). Lines: system text **376** line 3t (intro balloon), 3t + 1 /
  3t + 2 (Black 2's in-battle win / lose lines).
- The party draws 3 sets at random from the list: no repeated species, items deduplicated in up to 50 tries. A list
  with fewer than 3 species loops forever, so gen_battle_tower.py asserts against it.
- IVs: `func_ov012_02162828(id)`; level: `BtlSetup_SetTrialHouseParty` 0x02161fac (Black 2's constant 50 at 0x02161fba);
  the player's levels: `SetupTrialHouseBattle` 0x02162006 (`RestrictPlayerParty` to exactly 50); nature:
  `genSubwayBtlInstitutePoke` 0x0216274a (`PokeParty_SetNature`).
- Regulation **arc 106** (188 B): byte 4 level, byte 5 level mode (1 min, 2 "or less", 3/4 no check); file 20 serves
  modes 0/4/5 (`movs r0, #20; str r0, [sp, #4]` at 0x02165fd4).
- Field sprite by class: `func_ov012_02162b38`, table `data_ov012_0216d9b4` (53 × {u16 class, u16 object code}; missing
  class → 10). **The PWT reads it too** (ov135 0x021ef6fc).

### 1.4 Continue in the lobby [code, test]
`FieldSetNextZone zone, dir, x, y, z` + flag **2405** (EVENT_FLAG_CONTINUE_SCRIPT) make Continue load that zone with
its zone init (ov035 `EventFieldContinue_Callback`). Map-local works 0x4000-0x401F reset at zone init but are saved.

## 2. What is built

### 2.1 Mapping Sapphire → Black 2
| Sapphire | here |
|---|---|
| LV. 50 room / LV. 100 room (`battleTowerLevelType`) | play mode **0** (Single Train) / **5** (Super Single); VAR_BT_LEVEL_TYPE |
| Lv. 50: only Pokémon of level ≤ 50 (CheckPartyBattleTowerBanlist) | Sapphire's check unrolled in script (battle_tower_eligible.inc, banned 150/151/249-251/382-386 national), plus arc 106 **file 38** = file 20 with level mode 2 for mode 0 |
| Lv. 100: opponents level 100 (Sapphire's own rule, not scaled) | opponents level 50 + 10 × mode (ov033 helper called from 0x02161fac) |
| player keeps their levels | 0x02162006 `movs r3, #50` → 0 |
| trainers 0-99, Lv50/Lv100 mon pools, teamFlags | ids k (Lv. 50 sets, arc 211 files 0-299) and 100 + k (Lv. 100 sets, files 300-599); each trainer lists exactly the sets Sapphire's FillBattleTowerTrainerParty could draw |
| ChooseNextBattleTowerTrainer (tiers by challenge, battle 7 harder) | ov033 0x0217c11c rewritten (same rule; Black 2's caller keeps the seven distinct) |
| fixed IVs by trainer index (6/9/12/15/18/21/31) | `func_ov012_02162828` rewritten |
| random natures (.nature never read) | 0x0216274a `bl SetNature` → `bl RecalcStats` |
| opponent's sprite by facility class | command 308's literal (ov033 0x0217bcb0) → our lookup (42 classes) then Black 2's table |
| status var_4AE, records, prize, last streak | VAR_BT_STATUS_LV50/LV100, VAR_BT_RECORD_*, VAR_BT_PRIZE, VAR_BT_LAST_STREAK_* (0x4156-0x415D) |
| Silver/Gold Shield (decorations) | FLAG_RECEIVED_SILVER/GOLD_SHIELD only (Black 2 has no secret bases) |
| TEALA (receptionist, attendants) | code 79, the project's redrawn Teala (data/sprite_map.json), as in the Pokémon Centers |

### 2.2 Flow (Sapphire word for word; texts in src/text/script/0027 and 0021)
Lobby (0042/0043): receptionist (challenge / info / cancel; Lv. 50 / Lv. 100; party check with Sapphire's
"can't enter" lines; pick 3; "progress must be saved" + Black 2's save dialog; walk to the elevator door); interviewer
(Black 2 phrase picker); award man (records ≥ 50 / ≥ 100 → shields); records sign; zone-init states: disqualified
(entered, no save), won (ribbons when streak > 55: Winning Lv. 50 / Victory Lv. 100, record save, prize: vitamins, or
held items after 5 sets; bag full keeps it), lost, resumed ("We've been waiting for you!"). Elevator (0686: ride with
Black 2's rumble SE and shake), Corridor (0672: Lv. 50 or Lv. 100 door), Battle Room (0030: opponent walks in,
greeting, heal, battle, after a win heal + "opponent no. N" / save and quit / cancel; loss and 7 wins back to the lobby).
Rest = save the play block + FieldSetNextZone(lobby) + flag 2405 + save, then soft reset (Sapphire resets too).
Retire = soft reset without saving → "didn't save … disqualified" on Continue (as Sapphire).

Emerald builds (2026-10-18): the Battle Room brings out the Salon Maiden Anabel at Emerald's streaks (battle 35 / 70, then
every 35th with both symbols) and the lobby pays her +10 BP: notes/FRONTIER.md 5 ("The Battle Tower's Salon Maiden
Anabel"); Sapphire and Ruby assemble 0030/0042 byte for byte as before.

### 2.3 PWT building (zone 192)
Second building on the island (door 3 at tile (37,30): helper C's porch + standalone `pwt.nsbmd`, `B2_ZONE_192`). pwt.py:
zones 192/193 place 62 (Battle Tower), the lobby's exit → island warp 3, lobby map scripts from 0385. 0384.s: entries 8,
9, 12 (Clay's registration, story actors on reload, the post-Driftveil scene that closes the left desk) → halt; new
entry 19 (zone init): flags 890-894 set (Colress, rival, Cheren, Clay, Roxie hidden), fly flag 2471 cleared.

### 2.4 PWT tournaments (pwt_tower, 2026-10-11) [code, test]
Black 2 decides which tournaments the desks offer in ov055 `func_ov055_021e65e8` (`src/ov055/wbt_tool.c`). It is a
switch on the tournament id over the save's 29 win counters and flag 2400, compiled to a 16-entry Thumb jump table at
0x021e663e. `b2tools/patches/pwt.py` apply_code repoints only table entries, each to a return that already exists in
the function, so there is no new code and the overlay keeps its size:
| Id | Tournament | Black 2 | Here |
|---|---|---|---|
| 8 | Hoenn Leaders | counts[19] != 0 (Unova Leaders won), with Kanto/Johto/Sinnoh | flag 2400 (Hall of Fame), the case-5 code |
| 11 | Driftveil, first time | counts[18] == 0 | never (B2's story tournament) |
| 4 / 3 / 12 / 14 | Driftveil / Download / Rental / Mix | counts[18] != 0 | always |
- **Hoenn Leaders.** The island (the S.S. Tidal needs FLAG_SYS_GAME_CLEAR and the S.S. Ticket) and the right desk
  (global 10657 checks flag 2400) both open with the Hall of Fame. So "the eight Hoenn badges or the Hall of Fame" is
  always the Hall of Fame, and no badge check is needed.
- **No Elite Four tournament.** Black 2 has none (system text 405 lists 14 tournaments). Steven and Wallace are in
  Champions (1). That one opens after 10 World Leaders wins, and World Leaders needs all five Leaders tournaments,
  Unova's too. Both are kept as Black 2 has them.
- **Driftveil.** Black 2 offers tournament 11 only before its story win. Its roster is the story characters at ranks
  3-5 (arc 247 records 55-57: the player's Unova rival, who has no name here and shows as "???????", Cheren and
  Colress; byte 5 bit 0). Here it is never offered. The left desk offers what Black 2 offers after its story:
  Driftveil (4), Rental, Mix and Download (Download needs Nintendo's closed Wi-Fi).
- **Why tournament 4 keeps its roster.** It is Black 2's regular roster: 2 of the 5 Unova Gym Leaders (Cheren, Roxie,
  Burgh, Elesa, Clay; records 0-4) plus generic trainers (tested: Burgh and Roxie). Giving it Hoenn trainers does not
  fit Black 2's data. In the party archives this tournament family reads (arcs 248-250, chosen by
  `data_ov055_021e74f8[tournament.byte5]`), the Hoenn leaders' entries all point to the same 4-Pokémon filler list
  (Stoutland, Watchog, Klink, Golbat). The Unova leaders' entries point to 6-Pokémon lists of their own.
- Tested (screenshots/pwt_tower/02, 03, 07): left desk lists Driftveil, Rental, Mix, Download; right desk lists Unova
  Leaders, Hoenn Leaders. Driftveil bracket: Burgh, Masashi, Theodora, the player, Chloe, Roxie, Willa, Dorian. Hoenn
  Leaders bracket: Winona, Roxanne, Norman, the player, Tate, Flannery, Wattson, Brawly; the first match calls Norman.
  Both start their first battle.

### 2.5 Tower doors (pwt_tower, 2026-10-11) [code, test]
Black 2 stands door_h5_in in a dark recess of a taller wall (League chunk 899, zone 384). The wall face is 9 units in
front of the door, the black-textured recess goes back 11 units behind it, and the wall rises 32 units above the door.
The room builder now has a recipe flag for this: `"doorway": true` on a `"wall": "N"` furniture entry
(models_interior.py `doorway_spans` + build_terrain). It cuts the model's width out of the back wall and adds a black
recess behind the cut (2 × CAP deep, 8 units wider each side, roofed at the wall top) plus a black lintel over the void.
The Battle Tower Lobby and Corridor doors use it, standing 1 unit inside the cut and 1 lower (`gap` -1, `y` -1), so no
edge of a swung half shows over the wall top. Collision is unchanged. No other room uses the flag yet; the Elite Four
rooms' door_h5_in could opt in if their doors open. Tested: lobby elevator door and the Lv. 50 corridor door opening
in the challenge flow (screenshots/pwt_tower/01_doors_before_after.png).

## 3. Differences from Sapphire (Black 2 limits)
- **Shields**: flags only (no decorations in Black 2).
- **Reporter / Bravo Trainer TV**: the reporter stays hidden (no TV system); the interviewer uses Black 2's phrase picker.
- **Battles**: Black 2's subway battle (its music and transitions). Black 2 heals held berries each battle (Sapphire
  restores the party too). The in-battle win/lose lines are empty: Sapphire shows no trainer text in tower battles
  (`gUnknown_081D8E0D`), and Black 2 shows no empty box [test].
- **Messages**: Black 2's balloons wait for A where Sapphire's `message + waitmessage` did not (13, 14, 18).
- **Greetings**: Sapphire's easy-chat words in Black 2's spelling (gen_battle_tower.py; 2 words per row like Sapphire).
- **EVs**: Sapphire's `CreateMonWithEVSpread` gives 510 / n per flagged stat into a u8 (a single-stat set gets 510 & 0xFF
  = 254); Black 2 gives min(255, 510 / n), so single-stat sets get 255 (1 point more). Friendship (Sapphire: 0 with
  Frustration, else 255) is Black 2's set loader's own (not traced).
- **Doors** (fixed by pwt_tower, 2026-10-11, §2.5): the open door showed plain wall and a few pixels of the door over the
  wall top. Black 2's door_h5_in does not slide: its open animation (BCA0 `door_h5_in_op`, 16 frames, objects 1/2
  rotated about the vertical axis, up to 60°) swings both halves back into a dark recess.
- **PWT arrival**: the black below the lobby's entrance mat is Black 2's own look: the geometry ends about a row
  south of the mat, and camera box 265 follows the player onto it. Vanilla Black 2 looks the same
  (screenshots/pwt_tower/04_pwt_entrance_ours_vs_black2.png). The user chose to hide it (2026-10-11): pwt.py sets box
  265's z max from 440 to 365. At the screen's bottom edge, camera 0 shows the floor 82 units south of its target, and
  447 - 82 = 365. Tested walking in from the island door and around the lobby (mat, channel, both desks, both sides):
  no all-black row on any screen, and the player and the desks are framed as before
  (08_pwt_lobby_camera_before_after.png).

## 4. Tests (bt2.nds, HOENN_TEST_CH13 + W1 = Slateport harbour + HOENN_TEST_CHBT=2 + NO_WILD) [test]
Proofs in screenshots/battle_tower/:
arrive_ss_tidal.png (S.S. Tidal to the island), party_select_lv50.png, lobby_save.png (save in the lobby),
battle_won_questions.png (heal, "opponent no. 7", save and quit, cancel), battle_room_next_opponent.png,
rest_save_quit.png (mid-challenge save), continue_waiting_for_you.png (Continue → lobby → resumed), prize_seven_wins.png
(7th win: Zinc), retire_then_continue.png (retire → reset → disqualified), ribbons_streak56.png (Winning Ribbons: the
subway work's wins, `BSubwayScrWork` +14 = RAM 0x0224c69e in that state, poked to 55 before the 7th battle),
lv100_battle.png (Lv. 100 room: Swampert Lv. 100 entered, opponent Lanturn Lv. 100), teala_and_opponent_sprite.png (Teala
at the desk; Battle Girl Cassie shown with Sapphire's GIRL_3 → Black 2 Lass sprite by the new lookup), pwt_lobby_entry.png, pwt_desk.png,
pwt_right_desk.png (Unova Leaders offered: game cleared), pwt_tournament_start.png (Driftveil tournament started),
rooms_elevator.png, rooms_corridor.png, island_overview.png, island_pwt_door.png.
Field heap 0x15 free − 83,004 (save_check's need): island +301,784, lobby +287,668 (+280,812 after Continue),
elevator +291,620, corridor +286,908, battle room +283,488, PWT lobby +296,376 (work/agents/battle_tower/tools/heapm.py).

Checkers on the normal build (work/agents/battle_tower/rom, world and interiors of the same folder):
outdoor_check island frame 0 open, plus Black 2's 3 cull lines, as before (run it with HOENN_STANDALONE_BUILDINGS set to the
folder holding pwt.dae, or the PWT porch shows as an uncovered building); rooms_check for the 4 rooms: only the (m)
at the lobby's records sign (3,6), which was there before; npc_check 0 over a limit (367 zones; lobby 6 NPCs,
battle room 2, zone 192 21);
check_exits 0 outdoor/dynamic differ (same 4 room-to-room report-only lines as work/world); script_check 0 open (4 path lines
accepted in its ACCEPT: the elevator's parallel walk, the walk into the Battle Room doors). rom_layout_diff Sapphire vs
Ruby (both built from this tree): LAYOUT IDENTICAL.

### 4.1 Save margins and HEAPID_USER (pwt_tower, 2026-10-11) [test]
How it was measured (notes/TESTING.md "Saving and the field heap"): a menu SAVE with every GFL_HeapAllocate watched,
then a cold boot and CONTINUE in a new process. The save's lowest field-heap free (after its 32 KB request) is the
spare, and its need from idle is 83,004 B everywhere. The test build was HOENN_TEST_CHMO=1 stage 2 (game clear,
Mr. Briney's boat at all three docks) + HOENN_TEST_WARP, with work/agents/pwt_tower/tools/savecycle.sh, pt/t.py and
pt/bt.py. Before = this tree without pwt_tower's changes; after = with them. Other agents' changes in the shared tree
between the two builds account for the 208 B.
| Place | free after load | spare during the save | Continue |
|---|---|---|---|
| Route 104 beside the boat | 101,844 -> 101,636 | 18,840 -> 18,632 | back on Route 104 |
| Dewford (boat) | 101,844 -> 101,636 | 18,840 -> 18,632 | ok |
| Route 109 (boat) | 101,844 -> 101,636 | 18,840 -> 18,632 | ok |
| Oceanic Museum 1F (tightest room, script_check's sweep) | 278,980 | 195,976 (both) | ok |
| Victory Road B1F (tightest cave) | 348,036 | 265,032 (both) | ok |
| PWT lobby (192, type 16) | 379,380 | 296,376 (both) | ok |
Nothing is under 10 KB, so nothing was changed for the saves. The old 9.5 KB beside the boat (missing_objects, before
the save fix's heap was counted with the boat) no longer applies.

The PWT stadium (193) is map type 0, so it has the save fix's bigger field heap: 1,292,232 B, 309,584-313,696 B free.
HEAPID_USER keeps 28,776 B free there, as in every outdoor zone. In the Driftveil and Hoenn Leaders tournaments, no
allocation came from USER while the field existed: lobby, walk-in, bracket, stage, first battle start (screenshots
03/07). Battles and the bracket screen close the field first. No Hoenn script turns the C-Gear on: the only
FieldSubscreenChange is Black 2's save dialog in global 2000. The save keeps its own field-heap need everywhere
(05_save_continue_after.png).

## 5. Files
New: b2tools/patches/battle_tower.py, b2tools/patches/pwt.py, converter/gen_battle_tower.py, data/battle_tower.json,
src/text/overrides_battle_tower.json, src/field_scripts/0043_room_BattleTower_Lobby_init.s, 0672_room_BattleTower_Corridor.s,
0686_room_BattleTower_Elevator.s, 0384_pwt_lobby.s, 0385_pwt_lobby_init.s, scenes/battle_tower_lib.inc,
battle_tower_eligible.inc (work/agents/battle_tower/tools/gen_eligible.py), battle_tower_test.inc, data/interiors/336.json,
343.json, data/interior_layouts/BattleTower_Corridor.json, BattleTower_Elevator.json, _styles_battle_tower.json.
Changed: src/field_scripts/0042_room_BattleTower_Lobby.s, 0030_room_BattleTower_BattleRoom.s,
src/text/script/0027_room_BattleTower_Lobby.txt, 0021_room_BattleTower_BattleRoom.txt, data/interiors/21.json, 15.json,
converter/allocate_interiors.py (script-warp pass) + data/hoenn_interiors.json (Corridor 336, Elevator 343),
converter/gen_story_ids.py + data/story_ids.json + src/include/hoenn.h (Battle_tower block), island: data/hoenn_map_additions.json,
data/plans/BattleTower_Outside.json, data/towns/BattleTower_Outside.json, data/buildings/standalone.json,
b2tools/models_standalone.py (pwt), b2tools/world.py (standalone_door: `B2_ZONE_<n>` destination, 3 lines).
b2tools/script_check.py (two ACCEPT entries).

## 6. For the lead (merge)
1. Patch lists: add `pwt battle_tower` after `roamers` in story_build.sh / rebuild_slice.sh / the release build
   (work/agents/battle_tower/tools/build.sh has the list used here).
2. World: rerun world.py into work/world (island cell: the PWT porch and door 3 → zone 192) and build the standalone
   model `pwt` (b2tools/models_standalone.py → the standalone buildings folder, res 488). work/agents/battle_tower/world and
   island/buildings are this agent's builds of both.
3. Interiors: rebuild BattleTower_Elevator (343) and BattleTower_Corridor (336) into work/interiors (recipes in
   data/interior_layouts; work/agents/battle_tower/interiors has them). The Lobby and Battle Room rooms are unchanged.
4. Data already generated: data/battle_tower.json + src/text/overrides_battle_tower.json (converter/gen_battle_tower.py),
   data/story_ids.json + src/include/hoenn.h (gen_story_ids.py, chapter Battle_tower), data/hoenn_interiors.json.
5. Savestates: remake them (ov012/ov033 code, ov033 grew 160 B compressed, arc 106 +1 file).
6. Test switches: HOENN_TEST_CHBT=1 (three Lv. 50 Pokémon with IVs 31 in the lobby) / =2 (also: the first win of a challenge
   counts as six → the 7th battle, prize and record) on top of HOENN_TEST_CH13.
7. (pwt_tower, 2026-10-11) Rebuild BattleTower_Lobby and BattleTower_Corridor into work/interiors (their recipes now
   have `"doorway": true`, gap -1, y -1; the builder change is in models_interior.py: `doorway_spans` and the doorway
   block in build_terrain). pwt.py has apply_code (ov055 table, same compressed size: rom_layout_diff LAYOUT IDENTICAL,
   so the savestates still fit).
