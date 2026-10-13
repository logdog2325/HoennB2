# Wild encounter rate: Sapphire vs Black 2 (research, 2026-10-06)

Goal: make Route 101's (and later every route's) wild encounter **rate** match Sapphire. Slots/species/levels are
already Sapphire's (`src/encounters/0099_route_101.s`); this note is only about how often a battle starts.

## Short answer

- **Sapphire**: each step on grass has chance `p = 23·rate/4096` (Route 101, rate 20: **11.23 %**). The first step
  onto grass from another tile type is ×0.6 (6.74 %), and the first 4 steps after any battle or map load can't
  start a battle.
- **Black 2**: the EncData "grass" byte is **not a chance**. It is an index (1–12) into a fixed table of 12 rules in
  overlay 36 (`ENCOUNT_RATE_CONFIGS`). Each rule makes the chance ramp up from 0 after you enter grass or finish a
  battle. The chance per step is `(R+1)/100`, where `R` is a whole number. So B2 can only give 2 %, 3 %, …, 100 %.
- **An exact match is impossible.** 11.23 % is not a whole percent, and no vanilla rule stays at 11 %. B2 also has
  one counter that resets both on entering grass and after a battle. Sapphire handles those two cases differently.
- **Closest with data only (no engine change): keep `grass=1`.** By grass step after entering or after a battle,
  the chance is 0, 0, 5, 8, 11 %, then 14 % from the 6th step on. Compared with Sapphire: about 32 % fewer
  encounters on a 6-step crossing, about the same at 15–20 steps, and about 21 % more over long grinding.
- **Closest overall (needs a 4-byte edit of overlay 36's table, which is a user decision):** give a spare table
  entry (8 or 11, which no vanilla table uses) the values `{9, 1, 10, 2}` and set `grass=8` (or 11). That gives a
  flat **11 %** from the 3rd grass step. Tested in DeSmuME: the patched overlay loads and battles follow the new
  entry (see Verification).

## 1. Sapphire (pokeruby)

Sources: `external/pokeruby/src/wild_encounter.c` (`StandardWildEncounter`, `DoWildEncounterTest`,
`DoWildEncounterRateDiceRoll`, `DoGlobalWildEncounterDiceRoll`, `ChooseWildMonIndex_Land`),
`src/field_control_avatar.c` (`GetPlayerFieldInput`, `CheckStandardWildEncounter`), `src/random.c`,
`src/data/wild_encounters.json` (+ `.json.txt` template), `src/overworld.c`, `src/battle_setup.c`.

**When it runs:** every frame the player is centred on a tile (`T_TILE_CENTER`) and not on a forced-movement tile,
i.e. once per completed step. A trainer's sight, a frame script or a step script that fires first takes precedence
(`ProcessPlayerFieldInput`).

**Immunity:** `CheckStandardWildEncounter` skips the first 4 checks after `RestartWildEncounterImmunitySteps()`.
That is called at every battle start (`Task_BattleStart`, both wild and trainer battles), on a warp map load
(`sub_8053994`) and when crossing a map connection (`LoadMapFromCameraTransition`). These 4 checks count **any**
tile, not only grass.

**Per check on a land-encounter tile** (`MetatileBehavior_IsLandWildEncounter`, map has `land_mons`):
1. If the previous tile's behavior differs from this one (e.g. path → grass): continue only if
   `Random() % 100 < 60` (39336/65536 = 60.02 %).
2. `r = rate × 16`; Mach/Acro Bike: `r = r·80/100`; White Flute flag: `r += r/2`, Black Flute flag: `r /= 2`;
   lead holds Cleanse Tag (item 0xBE): `r = r·2/3`; lead's ability (if it isn't an egg): Stench `r /= 2`,
   Illuminate `r *= 2`; cap 2880.
3. Battle if `Random() % 2880 < r`. `Random()` returns a u16 (LCG `x = x·1103515245 + 24691`, top 16 bits), so for
   `r ≤ 2176` the chance is exactly `23·r/65536`. **No modifiers: `p = 23·rate/4096`** (≈ rate/178).
4. Then roamer (1/4 if it's on this map), mass outbreak, then the slot. Repel: if the slot's level is below the first
   healthy non-egg party member's level, no battle. The counter is not reset in that case.

Route 101 (rate 20): `p = 460/4096 = 0.11230` (1/9 would be 0.11111). The first step from path into grass is
0.6002 × 0.1123 = **0.0674**. In unbroken grass, a battle comes every **4 + 1/p = 12.90 steps** on average,
counting from the previous battle. On a bike: 0.0898.

**Grass slots:** `Random() % 100` against cumulative `[20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]`.

**Turning in place (code reading only, not tested in a GBA emulator):** when a tap-turn's animation ends, the player
is still in `TURN_DIRECTION`, so `sub_8059204` sets `T_TILE_CENTER` for one frame and the check runs. This looks the
same as Black 2 (below).

## 2. Black 2 (pokebw2 decomp, overlay 36, not yet decompiled)

How the asm was read: `tools/dsd dis -c config/b2_us/arm9/config.yaml -a <scratch>/asm --overlay 36`, then
`python3 tools/scripts/show_func.py --asm-dir <scratch>/asm NAME`. Function names come from the decomp's symbols
(swan's names). The decomp checkout was not modified (`git status` clean). Addresses are B2 US.

### The EncData rate bytes are rule IDs

`EncData_Load` (`src/ov012/field_encount_st.c`) loads the zone's 0xE8-byte table; `EncSys` keeps a pointer to it
(`sys+0xC`). Bytes 0–6 are the "rates" for grass, dark grass, shaking grass, surf, rippling surf, fishing and rippling
fishing (types 0–6 from `FieldEncount_DecideTypeByTerrain` 0x021a1b14).

- `EventWildBattleCall_CreateRandom` (0x021a1750): no encounter if `rate[type] == 0`.
- `EncSys_GetEncountRateConfig` (0x021a1b6c): for types 0–4, `idx = rate[type] − 1`; if `idx ≥ 12`, use idx 0.
  It returns `&ENCOUNT_RATE_CONFIGS[idx]`. Types 5/6 (fishing) get NULL, so fishing doesn't use this path.
- `ENCOUNT_RATE_CONFIGS` (0x021d0294, ov036 .rodata, offset **0x50C94** in the decompressed `arm9_ov036.bin`)
  holds 12 entries of 4 bytes `{inc, period, max, min}`, dumped from the binary:

| ID | inc, period, max, min | chance per grass step after a reset (steps 1–10) | steady state | mean steps/battle* | vanilla use |
|---|---|---|---|---|---|
| 1 | 3, 1, 13, 2 | 0 0 5 8 11 14 14 14 14 14 | 14 % from step 6 | 10.4 | grass on routes (Rt 1–3, 5–7, 9, 11–16, 18–20, 22, 23, forests) |
| 2 | 3, 1, 19, 2 | 0 0 5 8 11 14 17 20 20 20 | 20 % from step 8 | 9.0 | Floccesy Ranch, Route 20 (a season) |
| 3, 9, 12 | 2, 3, 13, 3 | 0 0 0 2 2 4 4 4 6 6 | 14 % from step 21 | 16.6 | 3: dark grass; 9: Desert Resort/Route 4; 12: Route 8, Moor of Icirrus, Icirrus City |
| 4 | 2, 2, 19, 2 | 0 0 2 4 4 6 6 8 8 10 | 20 % from step 20 | 13.0 | dark grass (1 table) |
| 5, 6 | 5, 1, 31, 2 | 0 0 7 12 17 22 27 32 32 32 | 32 % from step 8 | 7.2 | 5: Route 7 (a season); 6: dark grass (1 table) |
| 7 | 2, 18, 7, 8 | 0 ×8, then 2 % | 8 % from step 62 | 37.0 | caves, buildings (Relic Castle, Chargestone, …) |
| 8 | 2, 9, 7, 4 | 0 0 0 0 2 2 2 2 2 2 | 8 % from step 31 | 26.4 | **unused** |
| 10 | 1, 12, 7, 3 | 0 0 0 2 2 2 2 2 2 2 | 8 % from step 75 | 32.4 | surfing (all) |
| 11 | 1, 9, 7, 3 | 0 0 0 2 2 2 2 2 2 2 | 8 % from step 57 | 29.7 | **unused** |

\* Mean number of steps to the next battle in unbroken grass, counting from the previous battle, no modifiers.
Vanilla use comes from tallying `EncounterRates` in `external/pokebw2/data/encounters/*.s`. Grass uses only
1, 2, 5, 7, 9 and 12; dark grass 3, 4 and 6; surf 10. **8 and 11 appear in no table.**

### The per-step state machine

`EncountState` (`include/field/encounter.h`; found at 0x022427d0 in our test build): +6 tick (u8), +7 started
(u8), +8 step counter (u32), +0xC terrain, +0x10 `R` (u16).

1. `FieldEventProvider_InitCheckData` (0x02181cd4) sets bit 4 of the check flags when the player's move observer
   reports "move finished" (`FieldPlayerCore_UpdateActionStatusObserver` 0x0219ae80, status 3). It sets bit 2 when that
   move was a step (`FieldPlayerGrid_UpdateNormalMove`/`Jump` move status 1). A turn in place is move status 2
   (`FieldPlayerGrid_UpdateNormalTurn` 0x0219c4a0), so it sets bit 4 only.
2. `FieldEventProvider_Grid_CheckForEvent` (0x021814dc), on bit 4: `EncSys_Update(sys, stepped=bit2, bit10)`
   (0x021a16e8). Later, if no trainer sight, script, warp or per-step event fires first: `CheckCallRandomEncounter`
   (0x02182af8) → `EventWildBattleCall_CreateRandom(sys, 0)`.
3. `EncSys_Update`:
   - On a step, `EncountState_UpdateTerrain` (0x021a1f18) **resets** the state (`EncountState_SetTerrain`: counter 0,
     `R` 1, tick 0, started 0) when the new tile's "encounter tile" flag (`GetTileFlags & 4`) differs from the stored
     tile's. It also resets when both are encounter tiles of a different `GetTileEncountType`.
   - If started: `EncSys_UpdateEncountRate`. Otherwise, on a step: `EncSys_UpdateEncountRate`, then started = 1.
4. `EncSys_UpdateEncountRate` (0x021a1f7c) runs only on an encounter tile (grass, dark grass or water) and only while
   counter < 0xA000. It does `counter++`, and if `counter > min`, `tick += started`. When `tick ≥ period`: `tick = 0`
   and `R = min(R + inc, max)`.
5. `EventWildBattleCall_CreateRandom`: `R' = FieldEncount_CalcEncountRate(R)` (modifiers below), then
   `EncSys_CheckRNGEncounter` (0x021a1b90): no battle while `counter ≤ min`. Otherwise **battle if
   `GFL_RandomLC(100) ≤ min(R', 100)`**. `GFL_RandomLC` (0x02005748) is a 64-bit LCG returning
   `(high32 · 100) >> 32`, i.e. 0–99, so the chance is **(R'+1)/100** (100 % from R' = 99).
6. A battle calls `EncountState_SyncToPlayer` (0x021a1ed8), which resets the state.

Closed form, with no modifiers. On the n-th grass step after a reset, for n > min:
`R(n) = min(1 + inc·⌊(n − max(min,1)) / period⌋, max)` and the chance is `(R(n)+1)/100`. For n ≤ min the chance is 0.

**Other resets:** walking into another zone (`Field_SwapZoneByMatrix` → `func_ov012_0215ee10` →
`func_ov012_0215917c` → `EncountState_SetTerrain`), any map change (`EventMapChangeCore` →
`GameData_InitEncountTerrain`), and entering or leaving grass (above). I found no reset after trainer battles (see
Unknown). Walking on non-encounter tiles doesn't advance anything.

**Turning in place counts like a step** once started (verified, below). It advances the counter and `R` and rolls.

**Modifiers** (`CreateEncountManager` 0x021a0a1c, `SetupEncountFlagsByPartyPokeAbil` 0x021a1008,
`FieldEncount_CalcEncountRate` 0x021a0b9c, `PassPower_ApplyEncounter` 0x02013650). The lead is party slot 0 and is
skipped if it's an egg. Ability Illuminate/Arena Trap/No Guard: `R×2`. Stench/White Smoke/Quick Feet: `R/2`.
Sand Veil (weather 3/12) and Snow Cloak (weather 1/4/5): `R/2`. Lead holds Cleanse Tag (224) or Pure Incense (320):
`R' = 2R/3`, computed from the unmodified `R`, so it overrides the ability. Cap 100, then the Encounter Pass Power
scales `R'` by a percentage. There is **no bike or flute term** (unlike Sapphire). Repel (`FieldEncount_CheckLevelRepelled`):
no battle if the slot's level is below the first battle-ready party member's level. The state is not reset then.

**Grass slots:** `FieldEncount_PrepareActiveSlots` → `EncountMakeRnd12` (0x021a15d8) → `GetEncountSlotByProbability`
(0x021a15ac): `GFL_RandomLCAlt(100)` against cumulative `ENCOUNTRATE_RND12` row 0 = **[20, 20, 10, 10, 10, 10, 5, 5,
4, 4, 1, 1]**, the same as Sapphire. Rows 1–3 (`[10×8, 5×4]`, `[5×4, 10×8]`, reversed row 0) are used only when
`PassPower_ApplyLuckyEncProb` returns 1–3 (a Pass Power state). Slot order in our tables is therefore kept 1:1.

## 3. Verification in the emulator (DeSmuME, `b2tools/emu.py`)

Build: `HOENN_BUILD_DIR=<scratch> build_rom.py --clean test_door_to_nuvema littleroot route101 oldale
area2_buildings no_season_swaps text scripts encounters` (Route 101 `grass=1`). State: `after_mom2.dst` → exit to
Littleroot (loaded fresh from the ROM) → walk (avoiding grass) to (784,727) on Route 101, facing east into the big
patch (785–790, 727). In each trial we load that state, write a random 64-bit seed into the `GFL_RandomLC`
context (pointer at 0x0209da6c), walk 6 tiles east through grass, and read `EncountState` after each step. A step
that leaves counter 0 and started 0 is the step that started a battle.

**Vanilla rule 1 (`grass=1`), 2000 trials.** In every trial the counter and `R` after each step matched the model
(counter 1…6, `R` = 1, 1, 4, 7, 10, 13).

| grass step | 1 | 2 | 3 | 4 | 5 | 6 | no battle in 6 |
|---|---|---|---|---|---|---|---|
| trials still walking | 2000 | 2000 | 2000 | 1899 | 1749 | 1551 | |
| battles | 0 | 0 | 101 | 150 | 198 | 217 | 1334 |
| measured chance | 0 | 0 | 5.05 % | 7.90 % | 11.32 % | 13.99 % | 66.70 % |
| model `(R+1)/100` | 0 | 0 | 5 % | 8 % | 11 % | 14 % | 66.90 % |

χ² = 0.22 (4 df) for the asm model. The alternative "chance = R/100" gives χ² = 12.7 and is 6 log-likelihood units
worse (≈400:1), so the `≤` in `EncSys_CheckRNGEncounter` is confirmed.

**Turning:** after 2 grass steps, 3-frame taps of Up/Down (position unchanged) advanced counter and `R` exactly like
steps (`R` 1→4→7→10→13→13…). Battles started on a turn in 3 of 3 runs (21 taps).

**Patched table (test of the engine-edit option):** I copied `external/pokebw2/build/b2_us/build` to scratch, set
entry 1 to `{9, 1, 10, 2}` at offset 0x50C94 of `arm9_ov036.bin`, and ran `dsd rom build` with the same files. dsd
recompressed the overlay, and the ROM's FAT came out identical. On that ROM, loading the Route 101 state, then
opening and closing the Bag, reloads overlay 36 from the ROM: the table in RAM changed from `3,1,13,2` to
`9,1,10,2` and the game kept running. **1200 trials:** `R` = 1, 1, 10, 10, 10, 10 in every trial. Battles on steps
3–6: 134/1200, 122/1066, 95/944, 96/849, which pools to **11.0 %** (447/4059, 95 % CI 10.0–12.0 %). Model: 11 %;
χ² = 1.17 (4 df); "R/100" χ² = 5.8. No battles on steps 1–2, as predicted.

## 4. Conversion

**Why an exact match is impossible**
1. The rate byte only picks one of 12 hard-coded rules. None of them has a flat 11 %.
2. Even with an edited table, B2's chance is `(R+1)/100` with a whole-number `R`. Sapphire's 11.23 % lies between
   11 % and 12 %.
3. The structure differs:
   - Sapphire gives 4 safe checks (on any tile) after a battle or map load, and 60 % of the chance on the first
     step into grass.
   - B2 has one counter, reset both by a battle and by entering grass. The first eligible step after a reset is
     always `R = 1` (2 %) when min = 0. B2 can't give 6.7 % on the entry step, and it can't keep post-battle
     safety separate from entry behaviour.
4. Modifiers differ (no bike/flute in B2; extra abilities, Pure Incense and Pass Power in B2).

**Data only (no engine change).** Steady per-step chances available: 8 %, 14 %, 20 % or 32 %. For rate 20 the
closest is 14 %, and rule 1 reaches it fastest (6th step), so **keep `grass=1`**.

Expected battles on a walk of k grass steps, starting by entering from a path tile, counting battles along the way:

| k | 3 | 6 | 10 | 15 | 20 | 50 | 100 |
|---|---|---|---|---|---|---|---|
| Sapphire (rate 20) | 0.265 | 0.494 | 0.804 | 1.191 | 1.579 | 3.904 | 7.778 |
| B2 `grass=1` | 0.050 | 0.334 | 0.721 | 1.203 | 1.684 | 4.575 | 9.391 |
| B2 custom `{9,1,10,2}` | 0.110 | 0.385 | 0.746 | 1.197 | 1.647 | 4.352 | 8.860 |
| B2 custom `{9,1,10,1}` | 0.208 | 0.505 | 0.902 | 1.397 | 1.893 | 4.866 | 9.821 |
| B2 custom `{9,1,10,4}` | 0 | 0.208 | 0.515 | 0.899 | 1.281 | 3.572 | 7.392 |

**With an edited table entry `{R−1, 1, R, m}`:**
- `R = round(100·23·rate/4096) − 1` (at least 1).
- `inc = R−1` makes the chance jump from 2 % straight to `(R+1)` % on the first eligible step.
- `m` sets how many grass steps after a reset are safe. A small `m` matches short crossings; `m = 4` matches
  grinding (Sapphire's 4 safe steps) but makes short crossings too quiet.

The `m` below minimises the worst relative error in expected battles over walks of 6–100 grass steps. Sapphire
rates come from `wild_encounters.json`. The "best vanilla ID" uses the same criterion.

| Sapphire rate (where) | Sapphire p | custom R → chance | best m (worst error) | m = 2 worst error | best vanilla ID (worst error) |
|---|---|---|---|---|---|
| 1 (water: Petalburg, Sootopolis) | 0.56 % | 1 → 2 % (B2 minimum) | — (can't go below 2 %) | — | none fits |
| 4 (Seafloor Cavern, Cave of Origin; most water) | 2.25 % | 1 → 2 % | 0 (3 %) | 35 % | 10 (51 %) |
| 9 (Safari water) | 5.05 % | 4 → 5 % | 1 (12 %) | 26 % | 3 (69 %) |
| 10 (caves: Granite, Meteor Falls, Mt Pyre, Victory Road, …) | 5.62 % | 5 → 6 % | 2 (20 %) | 20 % | 4 (60 %) |
| 15 (Route 119) | 8.42 % | 7 → 8 % | 1 (16 %) | 26 % | 1 (49 %) |
| **20 (Route 101 and most routes)** | **11.23 %** | **10 → 11 %** | **2 (22 %)** | 22 % | **1 (32 %)** |
| 25 (Safari Zone) | 14.04 % | 13 → 14 % | 2 (19 %) | 19 % | 1 (43 %) |

Limits of the edit option:
- Only 12 entries exist, and an ID above 12 silently falls back to entry 1.
- 8 and 11 are free in vanilla. 6 duplicates 5, and 9/12 duplicate 3, but those are used by a few vanilla tables
  (dark grass 6; Desert Resort 9; Icirrus/Route 8 12).
- Once all B2 maps are replaced, all 12 entries are free.
- Surfing (type 3) uses the same table. Fishing does not.

## 5. Recommended values

- **Route 101 now (no engine change): `grass=1`**, as in `src/encounters/0099_route_101.s`. It is the closest data-only
  value. Its comment ("rate code is not decompiled") can now point here.
- **If the user approves an overlay-36 data edit** (contradicts "no engine changes" in DECISIONS.md, so it's their
  call):
  - Set entry 8 (bytes at `arm9_ov036.bin` + 0x50C94 + 4·7) to `09 01 0A 02` and use `grass=8` for every
    Sapphire rate-20 route.
  - Add more entries from the table above for other rates (e.g. entry 11 = `04 01 05 02` for rate-10 caves).
  - `build_rom.py` would need a step that copies and patches the overlay and points `rom_config.yaml` at the copy.
    It patches only NitroFS files today.

## Unknown

- **Sapphire turning in place:** whether a tap-turn rolls an encounter is from code reading only. Settle it with
  pokeruby in a GBA emulator: tap-turn in grass and watch `sWildEncounterImmunitySteps` / battles.
- **B2 trainer battles:** I found no `EncountState` reset after trainer battles. Only map changes, zone swaps,
  terrain changes and wild-battle starts reset it. Not tested; settle by reading `EncountState` before and after a
  trainer battle.
- **Patched overlay on other targets:** loading works in DeSmuME (NDS mode) only. melonDS, DSi mode (the overlay
  is marked `signed`; DSi-mode digest checks) and real hardware are untested. Settle by booting the patched ROM there.
- **Pass Power scaling values** and which power `PassPower_ApplyLuckyEncProb` belongs to: not read (data at
  0x021410c0).
- **Weather IDs** for Sand Veil/Snow Cloak (3/12, 1/4/5) are raw values; their names weren't looked up.
- **Hidden effects outside this path** (e.g. Gen 5's flute items, if they change rates elsewhere) weren't searched.
  `FieldEncount_CalcEncountRate` itself has no flute term.
- **Water and fishing:** surf conversion uses the same table (above). Fishing's rate byte goes through
  `BtlSetup_CreateFishing`, which I haven't read.
