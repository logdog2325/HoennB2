# The PWT as Hoenn's Battle Tower (research 2026-10-06)

User request: "see if you can move the PWT to the battle frontier". Sapphire has no Battle Frontier; its post-game
facility is the **Battle Tower** on its own island (pokeruby `BattleTower_Outside`), reached by ferry from Slateport
and Lilycove. This note covers what it takes to make Black 2's Pokémon World Tournament (PWT) that facility.

**Short answer: it works, with data and script edits only, and no code patch is needed for a first version.** The
engine ties the PWT to two zone ids, **192 (lobby)** and **193 (stadium)**, through the script-plugin table, the
gimmick table, the subscreen check and the respawn table. Both zones have their own matrices and interior areas, so
they survive Unova's overworld going away. Zone **191** (the outdoor PWT plaza south of Driftveil) is the only part
on matrix 0. Nothing in code sends the player back to Driftveil: all the Driftveil links are warp entities, one
town-map record and story scripts. Two script traps must be fixed even in the smallest version (§4.2, §4.3).
Recommendation: give `BattleTower_Outside` zone 191, point its tower door at the lobby, and keep 192/193 as they are.

Sources: `bw2/` = `external/pokebw2` (decomp); `ruby/` = `external/pokeruby`; asm = `b2tools/armdis.py` on the
decomp's built binaries (`bw2/build/b2_us/build/`), names and addresses from `bw2/config/b2_us/.../symbols.txt`;
"bytes" = read from `bw2/extract/b2_us/files`. Tags: **[code]** read from C or asm, **[bytes]** checked in the data,
**[script]** read from `bw2/data/field_scripts`, **[inferred]** consistent with the data but not traced. Nothing was
built or run. The only file changed is this note.

## 1. The PWT in Black 2

### 1.1 Zones (`bw2/data/zones/0000_zone_headers.s`)

| Zone | What | Header (line) | Matrix → chunks | Area → pack (tex set) | Scripts / text / entities |
|---|---|---|---|---|---|
| 106 | Driftveil–PWT gate | :216 map_type 16, parent 96, transition 2 | 373 (1×1) → 1029 | 352 → int 70 (352) | 212 (`0212.s`) / 125 / 119 |
| 191 | PWT plaza (outdoors) | :386 map_type 0, **matrix 0**, npc_cache 20, place 36, fly_from 1, cam_bound 0, fly (197, 469) | matrix-0 cells (5,14) (6,14) (5,15) (6,15) → chunks 51, 147, 337, 338 | 222 (seasonal 222-225) → ext 55 | 382 (`0382.s`) / 249 / 240 |
| 192 | PWT lobby (reception, shops) | :388 map_type 16, parent 191, place 36, bgm `SEQ_BGM_WBT_LOBBY`, escape_rope 0 | 265 (1×1) → 981 | 352 → int 70 | 384 (`0384.s`) / 250 / 241 |
| 193 | PWT stadium | :390 map_type 0, parent 191, place 36, camera 41, bgm `SEQ_BGM_WBT_GROUND` | 266 (2×1) → 982, 1005 | 381 → int 78 | 386 (empty) / 251 / 242 |

Matrices, cells, chunks and areas: [bytes] (`a/0/0/9` entries 0, 265, 266 and 373; area records in `a/0/1/3`).
Zone 96 (Driftveil City, matrix-0 cells (5..7, 12..13)) lies directly north of the plaza.

### 1.2 How the player gets there in Black 2

1. **Driftveil → gate.** Zone 96 warp 12 (tiles (176..178, 443), 3×1) → zone 106 warp 0 [bytes, `b2tools/zones.py 96 106`].
2. **Gate.** Zone 106 has a trigger at (3..11, 8) on var **0x40c5 == 0**, which runs `0212.s` Script_2 ("you don't
   have the Driftveil City Gym Badge yet", then walks you back). Warp 1 (3..7, 14) → zone 191 warp 2 [bytes, script].
3. **Plaza.** Zone 191 has a trigger at (191, 466..475) on var **0x40c6 == 0**, which runs `0382.s` Script_1: Clay's
   intro. It sets 0x40c6 = 1 and flags 711/713/1000, then `RTReserveScript 8` + `MapChangeWarp 192, 15, 26, 0`
   (`0382.s:144-149`). After that the door, warp 0 at (197, 465), type 62, leads to zone 192 warp 0.
4. **Lobby.** Zone 192 warp 0 (mat (14..16, 26), type 1) → zone 191 warp 0. Warp 1 (14..18, 1) → zone 193 warp 0.
   Tournaments do not use warp 1. The reception script moves you with `MapChangeCore 193, 31, 0, 15, 2` +
   `RTReserveScript 10665` (`1277.s:782-783`).
5. **Stadium.** After the last match, `1278.s` L_0139 (:78-95) reserves 10658 and sends you back with
   `MapChangeWarp 192, 14|16, 0, 1`, depending on which desk you used. This happens on a win and on a loss.
6. **Fly.** Town-map record 23 (`a/0/8/5` file 0, 54-byte records) = **zone 191, fly flag 2471 (0x9a7)**, screen
   (77, 103) [bytes]. Flying lands on zone 191's header fly point (197, 469) (`zone_header.inc:16`). Flag 2471 comes
   from `RESPAWN_ZONE_INFO[72]` = {flag 0x9a7, canReturnHere 0, discoverOnVisit 1, zone 192, main zone 192}
   (`bw2/src/ov012/respawn_zone.c:79`; ov012 0x0216c8dc [bytes]). `SetTeleportZoneDiscover` sets the flag whenever
   you arrive in zone **192** (`event_mapchange.c:1410`, `fieldmap.c:1086`).

### 1.3 Scripts

| File | Global ids | Plugin | What |
|---|---|---|---|
| `0382.s` / `0383.s` (map scripts) | zone 191 | none | Clay intro (1), Team Plasma scene (2, run on load while 0x40c6 == 2), post-Plasma scene (3), plaza NPCs, warp 3 moved for the Plasma Frigate (`ObjInitWarpGPos`) |
| `0384.s` / `0385.s` | zone 192 | 6 | lobby story: Script_8 (Clay registers you, sets flag **2441**), Script_9 (load, 0x4135 == 1), Script_12 (Roxie/Clay scene); spectators; BP guide; two BP shops (Scripts 16/17 → global 10110, shop ids 253/254) |
| `0386.s` / `0387.s` | zone 193 | 7 | empty: the stadium runs on global scripts |
| `1277.s` | 10655-10660 | 6 | 10655 left desk, 10656 records board, 10657 right desk, 10658 results, 10659 lobby load (desk position, "hall" NPCs 9-11), 10660 lobby init (flags 871-873) |
| `1278.s` | 10665-10667 | 7 | the matches, then back to 192 |
| `1279.s` | 10675-10678 | 6 | the three "hall" NPCs and NPC uid 12 (text 669: comments by leaders and champions) |

Global id ranges come from `bw2/tools/scripts/field_commands.json` (`global_scripts`). The lobby's map-script table
actually used is the tail of entity file 241, `04 00 a3290000 0400 09000000 0200 a4290000 0000` = MapScript 4 10659,
MapScript 4 9, MapScript 2 10660 [bytes]. That is byte-identical to `0385.s`; entity file 240's tail matches `0383.s`.
Note: `VMJumpIf CMP_STACK, L` jumps when the condition is **false** (`bw2/src/ov012/scrcmd_vm.c:291-298`), so
`push cond; VMJumpIf CMP_STACK, else; then-block`.

### 1.4 Entities (`a/1/2/6`, parsed with `b2tools/zones.py`) [bytes]

- 191 (file 240): 18 signs, 19 NPCs, 4 warps (0 → 192/0 door, 1 → 505 Relic Passage, 2 → 106/1 gate, 3 → 552 Plasma
  Frigate), 1 trigger (Clay). The story NPCs are Clay (uid 7, model 227, flag 713), Cheren (8/223/712), the rival
  (6/291/711) and Colress (9/250/710).
- 192 (file 241): 1 sign (10656), 21 NPCs, 2 warps. Receptionists uid 0 at (14, 6) → 10655 and uid 8 at (16, 6) →
  10657. "Hall" NPCs 9-11 (flags 871-873, scripts 10675-10677). Shops 18/19, BP guide 20, spectators 1/3/4/6/7/12/15,
  spectator 2 (flag 991). **Story NPCs**: rival 5 (model 291, flag 891), Clay 13 (227, 893), Cheren 14 (223, 892),
  Roxie 16 (224, 894), Colress 17 (250, 890). A hide flag that is clear means the NPC is shown, so at a new game all
  five stand in the lobby.
- 193 (file 242): warp 0 → 192/1 only.

## 2. What the engine hard-codes

| Where | What | Effect | Source |
|---|---|---|---|
| `SCRIPT_PLUGIN_TABLE` (ov012 0x0216c1ac) | zone **192** → plugin 6 (ov55 + ov56), zone **193** → plugin 7 (ov55 + ov57); zone arrays at ov012 0x0216c10c / 0x0216c108 | all `Wbt*` / `Plugin6_*` / `Plugin7_*` script commands exist only in these zones. Plugins are chosen when the field is created, from the player's zone (`fieldmap.c:351-352`), so any real warp into 192 works | `bw2/src/ov012/script_plugin.c:8,13,32-33,45` [code + bytes] |
| `GetZoneIsPWTBattleStage` (arm9 0x02018aac) | `cmp r0, #193` | stadium subscreen 11 | `event_mapchange.c:1532` [code] |
| Gimmick table `a/1/0/2` (u32 zone, u32 gimmick) | 192 → 51, 193 → 36 | `Field_InitGimmick` (ov036 0x021b7f7c) loads `GIMMICK_OVERLAY_INFO[g]` (ov036 0x021d1274, 16 B: overlay, init, end, update). 51 = overlay 135 with no hooks (WBT entrance library: BP award, party, `func_ov135_021ef904` bracket). 36 = overlay 134 + hooks 0x021eec81/0x021eecc9/0x021eece1 (stadium, "wbt_battle.c") | [bytes + asm] |
| `RESPAWN_ZONE_INFO[72]` | discovery of fly flag 2471 on entering 192 | Fly unlock (§1.2) | `respawn_zone.c:79` [code + bytes] |
| Town-map record 23 | zone 191, flag 2471 | Fly target | `a/0/8/5` [bytes] |
| `func_ov012_02160eb4` | for a zone whose parent is 552 (Plasma Frigate), var 0x4044 == 0 returns **191** (`movs r0, #191` at ov012 0x02160f02); 1 → 463, 2 → 230, 3 → 552 | where the Frigate is reported (callers: town map ov144, arm9 0x0202cb72/0x0202d434/0x0202d454, ov157, ov298, ov303). Only matters inside the Frigate | [asm] |

**Searched and not found:** a byte scan of arm9 and all overlays for Thumb `cmp rN, #191..193` (91 hits) and
`movs rN, #191|193` in the field overlays (arm9, ov005, ov011, ov012, ov022, ov035, ov036, ov055-057, ov134, ov135,
ov144). The hits in arm9 and the field overlays were mapped to their functions and the field ones disassembled. The
only zone compare is `GetZoneIsPWTBattleStage`. The rest are screen heights, `VCOUNT` (`func_020283f4`), UTF-8 masks,
struct offsets and the `movs r0,#191` above [asm]. Twelve overlays with hits (ov076, ov182, ov185, ov190, ov194,
ov197, ov199, ov208, ov214, ov257, ov286, ov310) were not disassembled. Eleven of them never call a zone getter
(arm9 0x020187d4-0x02018f48 or `PlayerState_GetZoneID`, per their `relocs.txt`). ov257 calls only Entralink checks,
at 0x021a19dc/0x021a19f0, in other functions than its compares [inferred: no zone compare there]. The decomp C has no other
literal ([code]: grep of `bw2/src`). The zone-keyed data tables were scanned for 191-193 [bytes]: fog (`a/0/8/0` file
29), lights (`a/0/8/1` file 1), Flash (`a/1/4/9`), calendar weather (`a/0/9/6` file 1), ISS zone sound (`a/1/3/6`)
and city units (`a/1/3/3`), `ZONE_CAMERA_ASSIGNMENTS` (arm9 0x020900ac, 9 u16 = zone:11 | camera:5) and
`VERSION_SPECIFIC_ZONES` (arm9 0x0209a348: 0↔424, 294↔295, 326↔551). None of them lists 191, 192 or 193. The
Wi-Fi tournament event (`bw2/src/ov005/event_wbt_wifi.c`) names no zone.

So the ids **192 and 193 must stay**. Their headers' matrix, area, place and so on can change, but the lobby and
stadium are best left as Black 2 built them. Zone **191** is free apart from record 23 and its own data.

## 3. Entering from Hoenn and getting back

- **In:** yes, with a plain warp. Zone 192 is an ordinary interior (map_type 16, own 1×1 matrix, interior area 352,
  pack 70), so a warp entity {dest_zone 192, dest_warp 0} or a scripted `MapChangeCore` works. The field is rebuilt
  on arrival, which loads plugin 6 and gimmick 51 by zone id (§2). For a script, use the project's tested pattern
  (`FadeOutBlack; RTReserveScript n; FadeWait; MapChangeCore …`, notes/OPENING.md:86):
  `MapChangeCore 192, 15, 0, 26, 0` is the tile and direction Black 2's own entry uses (`0382.s:149`, the middle of
  the mat, facing up). The arguments of `MapChangeWarp` (cmd 194, ov036 `s00C2_MapChangeWarp`) are not decompiled, so
  use `MapChangeCore` (zone, x, y, z, dir; dir 0 = up, 1 = down: `src/field_scripts/0778_littleroot_town.s:278,344`).
- **Out of the lobby:** only entity 241 warp 0 (→ 191/0). It is data: retarget it, or keep it if the island is 191.
- **Out of the stadium:** always back to 192 by script (`1278.s:87,95,114,144`). PWT battles return to the lobby
  after both a win and a loss (`1278.s` Script_1 → L_0139). No blackout in the stadium was seen [inferred from the
  script flow; the battle-end handling inside ov134 is not decompiled].
- **Fly:** record 23 → zone 191's header fly point. Zones 192/193 have fly_from 0 (no Fly from inside); 191 has
  fly_from 1.
- **Respawn / Teleport:** entry 72 has canReturnHere 0, so the PWT is never a respawn point. Blackout and Teleport
  use the last Pokémon Center (`GetRespawnLocationIndexForRespawnZone`, `respawn_zone.c`).
- **Escape Rope:** 192/193 have escape_rope 0. The exit memory is only written when you go from a matrix-0 zone into
  a non-matrix-0 zone (`event_mapchange.c:1232`).
- **"Return to Driftveil" logic: there is none in code.** The Driftveil links are data: warps 96/12 ↔ 106/0 and
  106/1 ↔ 191/2, record 23, and Driftveil's own Pokémon Center respawn entry (index 6, zone 99 → main 96).
- **State of the current build:** `b2tools/patches/hoenn_world.py` appends Hoenn as a new matrix (416) and leaves
  matrix 0 alone (:1-4). So zone 191 (the Unova plaza) still exists in the ROM, but the paths to it are gone:
  zone 96 is now **Lilycove** (`data/hoenn_zones.json`), whose B2 warp slot 12 (→ gate) is parked on a solid tile
  unless Lilycove's config maps it (`hoenn_world.py:63-64`), and zone 106 is now `FallarborTown_PokemonCenter_2F`
  (`data/hoenn_interiors.json`). Two consequences:
  1. **Entering the lobby sets flag 2471**, which unlocks a Fly to the Unova plaza (191 at (197, 469)). There, Clay's
     trigger fires because 0x40c6 == 0. Fix: give 191 the island (§5), or until then clear 2471 in the lobby's init
     map script. Map scripts of type 2 run after discovery (`event_mapchange.c:1410-1411`).
  2. **When the Hoenn overworld moves onto matrix 0** (notes/OVERWORLD_PLAN.md), 191's header (matrix 0) would load
     Hoenn cells at Unova coordinates. 191 must be re-pointed **before or together with** that switch.

## 4. What else the PWT depends on

### 4.1 Story variables and flags

| Var / flag | Meaning (from the scripts) | Used by | In Hoenn |
|---|---|---|---|
| var 0x40c5 | Driftveil Gym badge state; the gate blocks while 0 | gate 106 trigger | gone with the gate |
| var 0x40c6 | plaza story: 0 before Clay, 1 registered, 2 after the story tournament (Plasma scene on plaza load), 3/5 after the Plasma events | `0382.s`, `0383.s`, `0384.s:151` | unused if 191 gets our own scripts |
| var 0x4135 | lobby: 1 = story tournament won (Script_9 sets up actors), **2 = left desk closed** ("We're preparing a special tournament"), 3 = after the Plasma events | `1277.s:88-112,114-136`, `0384.s:157`, `0382.s` Script_3 | **must never become 2** (§4.2) |
| flag 2441 | story tournament active; passed to `WbtSystem_Create` as `unk4` | `scrcmd_wbt.c:67-74`, `1277.s:53-60,88-112`, set at `0384.s:98` | leave clear |
| flags 710-713 / 890-894 | hide flags of the story NPCs in 191 / 192 | entities 240 / 241 | set 890-894 (§6) |
| flags 871-873 | hall NPCs, set at init by 10660 and cleared by 10659 when the save has ranked trainers | `1277.s:47-86` | keep |
| flag 2400 | game clear: opens the **right desk** (`1277.s:138-160`) and the Unova Leaders tournament | §4.4 | keep, set by our Hall of Fame |
| var 0x4044, map-replace events 3/4 | Plasma Frigate dock; event 4 swaps matrix-0 chunk 338 (a plaza cell) for 406 (`a/0/1/0` entry 71, cond 7 = event uid 4, `map_replace.c:12-23`) | `0384.s:144-152` | unused |

### 4.2 Trap 1: the story tournament closes the left desk

The results script 10658 (`1277.s` Script_4, :1027) ends at L_1009 (:1101-1111) with
`if (0x8021 == 11) RTReserveScript 12`. Var 0x8021 is set by `WbtCmd_GetTournament` on the win path (L_0FE0, :1091).
So **winning the first Driftveil tournament (id 11) always runs lobby Script_12**, with or without the story flag.
That scene shows Roxie and Clay, plays Unova dialogue, sets **0x4135 = 2** (closing the left desk), 0x40c6 = 2 and
0x4044 = 0, and sets map-replace events (`0384.s:105-161`). In Black 2, only the plaza's post-Plasma script (`0382.s`
Script_3) reopens the desk with 0x4135 = 3, and it would never run in Hoenn. **Fix:** ship our own
`src/field_scripts/0384_*.s` in which Scripts 8, 9 and 12 are just `VMHalt`. Keep the `ScriptEntry` order so the
other script numbers do not move.

### 4.3 Trap 2: the story NPCs in the lobby

Their hide flags 890-894 are clear at a new game (§1.4), and in Black 2 only the story scripts set them. **Fix:** in
our lobby map-script table (the tail of entity file 241), add a MapScript 2 that sets flags 890, 891, 892, 893 and
894. That is Black 2's own pattern (10660 does the same for 871-873), and type 2 runs before NPCs spawn
(`event_mapchange.c:1411-1413`). Hide the NPCs rather than deleting them: index-based commands (`ObjInit*`,
notes/INTERIORS.md "NPC order") break when entries move.

### 4.4 Tournaments, unlocks and the Hall of Fame

The tournament table is `data_ov036_021d4920[15]` (`bw2/src/ov036/scrcmd_ochiba.c:30-46`, index = id − 1; names
come from system text **405**, `LoadPWTTournamentTypeText` :112). Unlocks are in `func_ov055_021e65e8`
(`bw2/src/ov055/wbt_tool.c:171-220`), based on the save's 29 win counters and flag 2400. The desk is the record's
`unk3`, checked by `func_ov056_021e7620` (`scrcmd_wbt_entrance.c`) [code].

| Id | Name (405) | Desk | Win record | Opens when |
|---|---|---|---|---|
| 11 | Driftveil (first time) | left | 18 | count 18 == 0 |
| 4 | Driftveil | left | 18 | count 18 ≠ 0 |
| 3 | Download | left | 29 | count 18 ≠ 0 |
| 12 / 14 | Rental / Mix | left | 25 / 27 | count 18 ≠ 0 |
| 5 | Unova Leaders | right | 19 | **flag 2400** |
| 6 / 7 / 8 / 9 | Kanto / Johto / **Hoenn** / Sinnoh Leaders | right | 20-23 | count 19 ≠ 0 (Unova Leaders won) |
| 10 | World Leaders | right | 24 | counts 19-23 all ≠ 0 |
| 2 | Type Expert | right | 0-16 (per type) | counts 19-23 all ≠ 0 |
| 13 / 15 | Rental Master / Mix Master | right | 26 / 28 | count 25 / 27 ≠ 0 and counts 19-23 all ≠ 0 |
| 1 | Champions | right | 17 | count 24 ≥ 10 |

(v16.4, pwt_tower: in this port Hoenn Leaders (8) opens with flag 2400, the first Driftveil (11) is never offered, and 4/3/12/14
are always offered: ov055 jump-table edits in b2tools/patches/pwt.py, notes/BATTLE_TOWER.md §2.4.)

The left desk (10655) is open unless 0x4135 == 2. The right desk (10657) needs flag 2400 (`1277.s:114-160`). Levels:
tournaments 4 and 11 force regulation `unk4` = 25 (`wbt_system.c` `func_ov055_021e5f78`); the lobby text says
"set to Level 25" (`data/text/script/0668.txt:11`) [inferred: `unk4` = level]. The others say Level 50. The project's
level curve does not matter in the PWT.

**Hall of Fame → flag 2400:** the Hall of Fame room (zone 145, `0290.s:105-120`) calls `CallGameClear 0` on the
first clear (2400 not set yet). `EventGameClear` state 10 then calls `FieldScript_CallPlayerPostHOFSetup`
(`event_game_clear.c:95-96`), which runs global **9601** (0x2581, `script_sys.c:206-208`). That is `1242.s` Script_2
(:260): if 2400 is clear it calls L_06DD (:478), which **sets 2400** and about 40 Unova post-game flags, then
`FieldSetNextZone 428` (Aspertia, :270). For Hoenn, the Ever Grande Hall of Fame must use `CallGameClear`, and 9601
must be rewritten for Hoenn (home = Brendan's or May's house, Hoenn post-game flags) **while keeping `FlagSet 2400`**.
Sapphire's own check for the ferry is `FLAG_SYS_GAME_CLEAR` (`ruby/data/maps/SlateportCity_Harbor/scripts.inc:161`),
the same moment.

### 4.5 Entrants

- **Who enters:** `func_ov055_021e5960` (cmd 1005, `scrcmd_wbt.c:107-113`) calls `func_ov135_021ef904`, which calls
  `func_ov135_021ef298` with the tournament id, the type, the arc-247 table and the seed. A 16-way jump table
  (ov135 0x021ef2b6) picks "N trainers of rank R" through `func_ov135_021eee08`. Leaders tournaments (5-9) and World
  Leaders: 7 of rank 3. Driftveil (4): 2 of rank 3, 1 of rank 2, 4 of rank 1. First Driftveil (11): ranks 5, 4, 3,
  plus 4 of rank 1. Champions (1): every member [asm].
- **Membership:** `func_ov135_021eef30` (jump table ov135 0x021eef38). Tournaments 1 and 5-9 compare record **byte 6**
  with the tournament id. Type Expert compares **byte 7** (the type; 17 = any). The others test bits of **byte 5**
  (bit 0 = 11, 1 = 4, 2 = 10, 3 = 12, 4 = 14, 5 = 13, 6 = 15). Download takes everyone [asm].
- **The table:** `a/2/4/7` file 0, 128 records × 16 B (`WbtTrainer`, `bw2/include/field/wbt.h`). Byte 4 = trainer
  class (system text 383, line = class + 1). Byte 8 bits 0-2 = rank. **System text 409 line i = record i's name** [bytes].
  The groups by byte 6: 5 Unova (13 records: Cheren … Lenora, Brycen), 6 Kanto (8), 7 Johto (8), **8 Hoenn (records
  36-44: Roxanne, Brawly, Wattson, Flannery, Norman, Winona, Tate, Liza, Juan)**, 9 Sinnoh (8), **1 Champions (14
  Blue, 15 Lance, 16 Steven, 17 Wallace, 18 Cynthia, 19 Alder, 53 Red)**. The first-Driftveil roster (byte 5 bit 0)
  holds Unova story characters at ranks 3-5 (54 Hilda, 55 the rival, 56 Cheren, 57 Colress).
- **Parties:** `WbtCmd_MakeOpponentParty` (`scrcmd_wbt_stadium.c`) calls `func_ov134_021f03cc`, which branches on the
  entrant's kind. Kind 0 with `unk6` == 145 (the rival) goes through `func_ov134_021f0220` and the regular trainer
  loader `TrainerUtil_LoadParty` (arm9 0x020308c0). Other kind 0 entrants use `func_ov134_021f0364`; kinds 1-2 use
  `func_ov134_021f012c` [asm]. **Not decoded:** where the leaders' and champions' parties are stored. Rental and Mix
  use the Battle Subway Pokémon archive 257 (`wbt_party.c`).
- Post-match lines: text 669 (global 10675-10678) and system texts 409/410.

So **Hoenn's leaders are already PWT entrants** (tournament 8, Emerald's roster, with Juan). Sapphire's eighth
leader, **Wallace**, and its champion, **Steven**, are both in the Champions tournament.

### 4.6 Text that names Unova

The rough count of lines mentioning Unova, Driftveil, Clay, the Subway, Nimbasa or Cheren: lobby text 250 (10 of
22), 667 (2), 668 (7, tournament descriptions), 669 (13, leader comments, e.g. Steven: "Emerald can be mined in
Driftveil City?!"), system 405 (2: "Driftveil Tournament", "Unova Leaders Tournament"), 409 (3), lobby Script_18 ("Nimbasa
City's Battle Subway"). The project's text patch can override them line by line (`src/text/overrides.json`,
`b2tools/patches/text.py:1-15`).

### 4.7 Keep or re-theme

| Thing | v1 | Later (flagged as later work) |
|---|---|---|
| Lobby, stadium, BGM, BP shops, Rental/Mix/Type Expert, Kanto/Johto/Sinnoh/World Leaders | keep | none |
| Hoenn Leaders (8) | keep (Emerald roster) | Sapphire flavour: Wallace instead of Juan, Sapphire-like teams; needs the party format (§4.5) |
| Unova Leaders (5), the gateway to 6-10 | keep (Unova's leaders as visitors) | re-theme it as Hoenn's own 8 (Sapphire roster) and rename tournament 8, or move the gate. Changing the gate means data edits in `func_ov055_021e65e8`, which is code |
| Driftveil tournaments 11/4 | keep, rename in text 405/668 (e.g. "Tower Tournament") | replace the story roster (records 54-57, byte 5 bit 0) with Hoenn characters (rival, Wally) |
| Champions (1) | keep (has Steven and Wallace) | none |
| Texts naming Unova/Driftveil/Clay | rewrite the lobby and reception lines (§4.6) | leader comments (669) |

## 5. Placing the entrance in Hoenn

**Sapphire** [`ruby/data/maps/BattleTower_Outside`, `…_Harbor/scripts.inc`]:
- The island is 29×30 tiles with no connections. The tower occupies x 7-21, y 0-8 and runs off the north edge; the
  door warp is at (14, 8) → BattleTower_Lobby (`data/plans/BattleTower_Outside.json`).
- The ferry attendant stands at (19, 24) and offers Slateport or Lilycove. Ferries arrive at (19, 23). On load the map
  sets `FLAG_LANDMARK_BATTLE_TOWER`, which is the Fly unlock; the heal (Fly) point is (14, 9)
  (`ruby/src/data/heal_locations.json:124-127`).
- Slateport and Lilycove harbor attendants offer "Battle Tower" only after `FLAG_SYS_GAME_CLEAR` and with the
  **S.S. Ticket**, which Sapphire gives after the Hall of Fame (`ruby/data/scripts/players_house.inc:379`,
  `hall_of_fame.inc:12`). They warp **straight to the island** (`warp MAP_BATTLE_TOWER_OUTSIDE, 255, 19, 23`). The
  S.S. Tidal's interior maps are only used for Slateport↔Lilycove, so "the S.S. Tidal route" here means the two
  harbor attendants' menus and no ship interior.
- Black 2 has item 456 "S.S. Ticket" (`bw2/include/constants/items.h:443`, item text) [whether its item data works
  as a key item is unverified].

**Zone for `BattleTower_Outside`:**
- **A (recommended): zone 191.** Record 23 (Fly), entry 72 (fly flag), lobby warp 0 (→ 191/0) and the 192/193
  `parent` = 191 all already point there, so only 191's own header, scripts and entities change. 191 has no gimmick,
  plugin, camera, ISS, calendar or version entry (§2). Cost: remove 191 from `DENY` in `converter/allocate_zones.py`
  (keep 192/193) and change `BattleTower_Outside` 17 → 191 in `data/hoenn_zones.json`. The allocator says ids never
  change once used; zone 17 has not been used by any build yet, because standalone maps are not built.
- **B: keep zone 17.** Then edit record 23's zone (`a/0/8/5` record 23, first u16) to 17, entity 241 warp 0 to 17, and
  the `parent` of 192/193 to 17. Leave 191 unreachable. It is the same amount of work, with three more edits.

**Island header (either zone):** a new 1×1 matrix (the island fits one chunk). Area = the Hoenn exterior area
(water, sand and the tower share its texture budget). map_type 0, place = **line 62 "Battle Tower"** (already
allocated). Fly point = Sapphire (14, 9) moved by the map's offset. `cam_bound`: 191 uses box 0, the overworld's, so
give it its own box like `b2tools/patches/interiors.py:119-124` does, or 0xFFFF. Zones 192/193 must also get
place 62 (§8).

**The tower model:**
- Per the project decision (Gen 3 shapes, Gen 5 art), build Sapphire's tower shape (15 tiles wide) in Python with the
  PWT's own textures `c5_wbt_*`: 12 materials, **7,744 B of texels + 352 B of palettes**, from exterior pack 55 [bytes,
  `nsbtx.material_pairs`].
- Black 2's dome `c5_wbt_01` (res 330, 14,548 B BMD) could be dropped in as a placeholder. But its collision is about
  13 tiles wide and at least 14 deep around a door on its south edge (chunk 147, door (197, 465)), against Sapphire's
  15 × 9 footprint, so the map would have to sit lower in its cell. `wbt_fountain` (res 404) costs another 2.7 KB.

## 6. Plan

### Step 0: first look, no edits (S)
Build a test ROM with `HOENN_TEST_WARP=192,15,24`. Littleroot's town sign then warps into the PWT lobby
(`src/field_scripts/0778_littleroot_town.s:42-47`). This checks that the lobby, the left desk and a tournament work
from the Hoenn build. Expect the story NPCs (§4.3). Do not leave through the door or win a first tournament, because
of §3 and §4.2.

### v1: minimal facility (no code patch)
1. **Lobby fixes** (a new patch, e.g. `b2tools/patches/pwt.py`, which runs after `hoenn_world`):
   - entity 241's map-script tail gets an extra MapScript 2 that sets flags 890-894 (§4.3), and also clears 2471
     until the island exists (§3);
   - `src/field_scripts/0384_pwt_lobby.s`: a copy of `0384.s` with Scripts 8/9/12 → `VMHalt` (§4.2);
   - headers 192/193: place 36 → 62.
2. **Text:** reception and lobby lines from §4.6, plus tournament names 4/11 in system 405 (overrides).
3. **Zone:** option A (§5).
4. **Island:** build `BattleTower_Outside` as a standalone map on zone 191. It needs the O1 "standalone maps" step and
   the O2 water/sand recipes. Tower model with door warp 0 → 192/0. Sapphire's sign and 3 NPCs (generated content).
   Our `0382`/`0383` (entity 240 tail): MapScript 3 `FlagSet 2471` (Sapphire's landmark flag) and the ferry
   attendant's script.
5. **Ferry:** the island attendant gets a menu (Slateport / Lilycove) → fade + `MapChangeCore` to the harbor (zones
   596 / 203 at Sapphire (8, 11) + the room's offset), or to the harbor doors outside until those rooms are built.
   The Slateport and Lilycove harbor attendants add "Battle Tower" → `MapChangeCore 191, <(19, 23) + offset>, dir 0`,
   only with flag 2400 (and S.S. Ticket 456 once the post-Hall of Fame ticket event exists).
6. **Hall of Fame (story work):** the Hoenn Hall of Fame calls `CallGameClear`, and our 9601 keeps `FlagSet 2400`
   (§4.4).
7. **Order:** 3-4 before the Hoenn overworld moves to matrix 0 (§3 point 2).

If the island must wait, there is a temporary v1: put the ferry attendant on Lilycove's dock (zone 96, already built)
and send it straight into the lobby with `MapChangeCore 192, 15, 0, 26, 0`. Point 241's warp 0 at Lilycove's harbor
door: its index is assigned at build time (B2 slots first, Hoenn doors appended, `hoenn_world.py:66-69`), so the
patch must look it up and not hard-code it.

### v2: fuller version (later work)
- Hoenn town map: move record 23 to Sapphire's Battle Tower cell (region map (22, 12),
  `ruby/src/data/region_map/region_map_entries_de.h:143`) as part of O4's town map.
- Re-theme rosters (§4.7). First decode the leaders' party source (`func_ov134_021f0364` / `021f012c`, ov134), then
  edit `a/2/4/7` records (byte 6 group, byte 4 class, rank), names (409), comments (669), and the regulation texts.
- Optionally patch `RESPAWN_ZONE_INFO[72]`'s main zone (ov012 0x0216c8dc + 8) to 191, so that arriving on the island
  unlocks Fly as in Sapphire. The step 4 script already does this without a code patch.
- Music for the island (Sapphire `MUS_B_TOWER` has no Black 2 counterpart; candidates `SEQ_BGM_WBT_LOBBY` or the plaza
  theme `SEQ_BGM_SW_C_5_NEW`).
- Optional: drop the Unova plaza assets (area 222, chunks 51/147/337/338). Nothing else reads them.

## 7. Effort and risks

| Piece | Effort | Risk |
|---|---|---|
| Step 0 test | S (one test build) | none; read-only check |
| v1 lobby fixes + text | S-M (½-1 day) | low: a script copy plus entity tail and header edits with existing tools (`zones.build_entities`, `scripts.assemble`, `zoneheaders`) |
| v1 island | M (1-2 days) **after** the standalone-map and water recipes exist | medium: camera box, chunk height values, the tower model |
| v1 ferry scripts | S (½ day); harbors depend on O4 | low |
| Hall of Fame / 9601 | part of the story work | must keep `FlagSet 2400`, or the right desk stays shut |
| v2 roster re-theme | L (several days) | **high**: the party source lives in undecompiled ov134; the rival path loads the constants 369/370 (`func_ov134_021f0220`, ov134 0x021f0244/0x021f0248) [asm], which are the rival's trainers (`bw2/data/trainers/0369_rival.s`, `0370_rival.s`) [inferred: 369/370 are trainer ids passed to `TrainerUtil_LoadParty`] |

Other risks:
1. Never reuse 192/193 for anything else (plugin, gimmick and subscreen are keyed on them). They are already in `DENY`.
2. Tournament 11 → Script_12 (§4.2) and the story NPCs (§4.3) must be fixed in the same change that makes the PWT
   reachable.
3. Flag 2471 + record 23 send Fly to zone 191: make 191 a valid island first, or clear 2471 (§3).
4. Matrix-0 switch ordering (§3).
5. The Download tournament needs Nintendo's discontinued Wi-Fi service. It stays listed but cannot be played
   [inferred].
6. Whether item 456 works as a key item is unverified. The ferry can check flag 2400 alone.

## 8. Side findings (outside the PWT, for the overworld work)

- **Place line 36 is now "Route 117"** (`data/hoenn_zones.json` → `b2tools/patches/text.py:12-15`), but zones 191-193
  still use place 36. So the lobby, rental Pokémon's met location (`WbtCmd_MakeRentalParty` uses
  `ZoneData_GetPlaceNameID`, `scrcmd_wbt_entrance.c:158`) and the town map would say Route 117.
- Zone-keyed engine tables that hit Hoenn zones [bytes/asm]:
  - script plugin 15 (overlay 67) loads for **465 Dewford, 463 Route 119, 474 Route 120** (`script_plugin.c:20`);
  - the gimmick table `a/1/0/2` gives gimmicks to 18 Jagged Pass (3), 7 Route 134 (4), 108 Sky Pillar Top (5),
    29 Mt Pyre Summit (6), 98 Sky Pillar Outside (8), 326/551/157 Routes 103/122/124 (25), 389/397/317 (32, the
    slice), 465/474/463 (54) and 120 Verdanturf (26);
  - `ZONE_CAMERA_ASSIGNMENTS` forces camera 4 on **326 Route 103** and 5 on **551 Route 122**;
  - `VERSION_SPECIFIC_ZONES` maps 326 → 551 when the version-area flag is set (`event_mapchange.c` `FieldMapControl_LoadZone`);
  - ISS city units (`a/1/3/3`) exist for 16 Fortree, 113 Rustboro, 120 Verdanturf and 418.
  None of these is handled in the project yet (grep of `b2tools`, `converter`).
- `RESPAWN_ZONE_INFO[6]` maps zone 99 (now Lavaridge's Pokémon Center 1F) to main zone 96 (now Lilycove), with
  Driftveil's numbers. It belongs to O4's respawn table.

## 9. Unknown (and what would settle it)

1. Where the leaders' and champions' parties are stored (`func_ov134_021f0364`, `func_ov134_021f012c`). Settle:
   disassemble both and trace the archive they read.
2. The meaning of `WbtSystem.unk4` (flag 2441) inside ov134/ov135. It is presumably the story bracket. Settle: find
   its readers in ov134/ov135.
3. The arguments of `MapChangeWarp` (cmd 194). Settle: disassemble ov036 `s00C2_MapChangeWarp`.
4. Whether item 456 (S.S. Ticket) has usable item data and pocket in Black 2. Settle: read its record in the item
   data archive.
5. Whether a stadium loss can ever white out. Settle: trace the battle setup flags in ov134 or `func_ov022_0216e854`.
6. Town-map record fields other than zone, screens and flag (54 bytes). Settle: ov144 readers (also needed for O4).
