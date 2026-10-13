# Level scaling for the Gen 6 Exp. Share

`python3 converter/level_scaling.py` prints the report and writes `data/level_scaling.json` (the curve, a table for
every level, all 693 trainers and every Sapphire wild slot with new levels, key battles, sensitivity). Tags:
**[code]** = read in a decomp at file:line, **[computed]** = output of the script.

## Answer

**new = min(100, ⌊L + 0.3712 · max(0, L − 23)^0.80 + 0.5⌋)**, for every trainer Pokémon and every wild slot (min and
max separately) met after Mr. Stone's Exp. Share. Gym leaders, the Elite Four, the Champion, rivals, Wally and Team Aqua
all use the same curve. Content before the Exp. Share stays as it is. The curve doesn't change anything up to Lv24, so
nothing before the Exp. Share changes anyway: the highest level there is Brawly's Makuhita at Lv18 [computed].

| Sapphire | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 40 | 42 | 44 | 46 | 48 | 50 | 52 | 54 | 56 | 58 | 60 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **new** | 24 | 27 | 29 | 32 | 34 | 37 | 39 | 41 | 44 | 46 | 48 | 51 | 53 | 55 | 57 | 60 | 62 | 64 | 67 |

Odd levels: 25→26, 27→28, 29→31, 31→33, 33→35, 35→38, 37→40, 39→42, 41→45, 43→47, 45→49, 47→52, 49→54, 51→56,
53→59, 55→61, 57→63, 59→66. The full Lv1-100 list is in `curve.table`. Lv89 and above become 100.

**The increase is small** (+1 at Lv25, +2 at Lv30, +4 at Lv42, +6 at Lv58). The reason is that Black 2's own exp
formula already limits over-levelling [code/computed]:
- Each Pokémon's exp is multiplied by ((2L+10)/(L+Lp+10))^2.5, where L is the opponent's level and Lp its own.
  Out-levelling an opponent therefore costs a lot of exp. For example, a Lv10 beating a wild Lv3 Zigzagoon gets 12 exp instead
  of Gen 3's 25.
- Gen 5 base-exp yields are lower than Gen 3's for unevolved Pokémon (Zigzagoon 60→48, Geodude 86→60) and higher for
  final forms (Metagross 210→270).

With Sapphire's levels unchanged, Black 2's formula plus the Exp. Share leaves the two main battlers:
- 1.4 levels behind Sapphire's at Roxanne;
- level with Sapphire's at Wattson;
- only 4 levels ahead at the Champion.

What the Exp. Share really changes is the rest of the team. At the Champion, Sapphire's four non-main Pokémon are
Lv5-16. With the Exp. Share they are Lv54-57, a few levels below the main battlers (Lv63) [computed].

### Key battles

Starter Mudkip, so May uses the Treecko line. Her other two variants have the same levels in every battle. "main" is
the mean level of the two main battlers just before the battle, and "avg" is the whole party's mean. The last column is
the opponent's highest level minus "main".

| Battle | Sapphire | **New** | (a) Sapphire: main / avg | (b) Black 2 + Exp. Share, new levels: main / avg | ace − main (a) / (b) |
|---|---|---|---|---|---|
| Rival May 1 (Route 103) | 5 | **5** | 9.3 / 9.3 | 8.3 / 8.3 | −4.3 / −3.4 |
| Gym 1 Roxanne | 14, 15 | **14, 15** | 15.0 / 10.2 | 13.6 / 9.6 | +0.0 / +1.4 |
| Gym 2 Brawly | 17, 18 | **17, 18** | 18.6 / 12.0 | 16.9 / 11.2 | −0.6 / +1.1 |
| *Exp. Share received (Granite Cave → Mr. Stone)* | | | | | |
| Aqua grunts (Museum) | 14, 14 | **14, 14** | 20.9 / 13.2 | 19.7 / 17.1 | −6.9 / −5.7 |
| Rival May 2 (Route 110) | 18, 18, 20 | **18, 18, 20** | 23.4 / 14.2 | 22.8 / 20.1 | −3.4 / −2.8 |
| Wally 1 (Mauville) | 16 | **16** | 23.9 / 14.4 | 23.6 / 20.9 | −8.0 / −7.5 |
| Gym 3 Wattson | 22, 20, 23 | **22, 20, 23** | 25.4 / 15.0 | 25.1 / 22.6 | −2.4 / −2.1 |
| Aqua Admin Matt (Mt. Chimney) | 20, 20, 20 | **20, 20, 20** | 33.1 / 17.7 | 32.6 / 29.3 | −13.1 / −12.7 |
| Archie 1 (Mt. Chimney) | 24, 24, 25 | **24, 24, 26** | 33.2 / 17.7 | 32.8 / 29.5 | −8.2 / −6.8 |
| Gym 4 Flannery | 26, 26, 28 | **27, 27, 29** | 35.2 / 18.4 | 35.0 / 31.7 | −7.2 / −6.0 |
| Gym 5 Norman | 28, 30, 31 | **29, 32, 33** | 36.2 / 18.7 | 36.7 / 33.3 | −5.2 / −3.7 |
| Rival May 3 (Route 119) | 29, 29, 31 | **31, 31, 33** | 39.8 / 19.9 | 41.3 / 37.8 | −8.8 / −8.3 |
| Aqua Admin Shelly (Weather Institute) | 28, 28 | **29, 29** | 40.4 / 20.1 | 42.0 / 38.4 | −12.4 / −12.9 |
| Gym 6 Winona | 31, 30, 32, 33 | **33, 32, 34, 35** | 43.0 / 21.0 | 44.9 / 41.2 | −10.0 / −9.9 |
| Rival May 4 (Lilycove) | 31, 32, 32, 34 | **33, 34, 34, 37** | 44.3 / 21.4 | 46.6 / 42.9 | −10.3 / −9.6 |
| Aqua Admin Matt (Aqua Hideout) | 32, 32, 32 | **34, 34, 34** | 45.7 / 21.9 | 47.9 / 44.1 | −13.7 / −13.9 |
| Gym 7 Tate & Liza | 42, 42 | **46, 46** | 47.5 / 22.5 | 50.0 / 46.1 | −5.5 / −4.0 |
| Aqua Admin Shelly (Seafloor Cavern) | 38, 38 | **41, 41** | 50.1 / 23.4 | 53.0 / 48.9 | −12.1 / −12.1 |
| Archie 2 (Seafloor Cavern) | 41, 41, 43 | **45, 45, 47** | 50.3 / 23.4 | 53.4 / 49.3 | −7.3 / −6.4 |
| Kyogre (static, caught: no exp) | 45 | **49** | 51.2 / 23.8 | 54.6 / 50.4 | −6.2 / −5.6 |
| Gym 8 Wallace | 40, 42, 40, 42, 43 | **44, 46, 44, 46, 47** | 52.2 / 24.1 | 55.8 / 51.5 | −9.2 / −8.8 |
| Wally 2 (Victory Road) | 44, 43, 44, 41, 45 | **48, 47, 48, 45, 49** | 52.6 / 24.2 | 56.4 / 52.1 | −7.6 / −7.4 |
| Elite Four Sidney | 46, 48, 46, 48, 49 | **51, 53, 51, 53, 54** | 55.2 / 25.1 | 60.3 / 55.7 | −6.2 / −6.3 |
| Elite Four Phoebe | 48, 49, 50, 49, 51 | **53, 54, 55, 54, 56** | 55.7 / 25.2 | 61.0 / 56.4 | −4.7 / −5.0 |
| Elite Four Glacia | 50, 50, 52, 52, 53 | **55, 55, 57, 57, 59** | 56.1 / 25.4 | 61.7 / 57.0 | −3.1 / −2.7 |
| Elite Four Drake | 52, 54, 53, 53, 55 | **57, 60, 59, 59, 61** | 56.6 / 25.5 | 62.5 / 57.8 | −1.6 / −1.5 |
| Champion Steven | 57, 55, 56, 56, 56, 58 | **63, 61, 62, 62, 62, 64** | 57.1 / 25.7 | 63.6 / 58.8 | +0.9 / +0.4 |

Over all post-Exp. Share trainer battles, the gaps in (b) match those in (a) with an rms error of 0.40 levels
[computed]. Roxanne and Brawly are kept unchanged by decision, but under Black 2's formula the main battlers arrive
about 1.5 levels lower than in Sapphire, so these two fights are slightly harder.

### Wild levels (min–max of each table; Sapphire → new)

| Area | Land / cave | Area | Land / cave |
|---|---|---|---|
| Routes 101–104, Petalburg Woods, Route 116, Rusturf Tunnel, Granite Cave | unchanged (before Exp. Share) | Route 121 | 25–28 → 26–29 |
| Routes 110, 117, 112, 113, 114, Fiery Path, Meteor Falls 1F, Jagged Pass, Route 111 desert | unchanged (all ≤ 22) | Mt. Pyre exterior / summit | 25–29 → 26–31 / 24–30 → 24–32 |
| Route 115 | 23–26 → 23–27 | Mt. Pyre 1F–6F | 22–29 → 22–31 |
| New Mauville | 22–26 → 22–27 | Seafloor Cavern rooms | 28–36 → 29–39 |
| Route 118 | 24–27 → 24–28 | Cave of Origin | 28/30–36 → 29/32–39 |
| Route 119 | 24–27 → 24–28 | Victory Road 1F / B1F / B2F | 36–40 → 39–44 / 38–42 → 41–46 / 40–44 → 44–48 |
| Route 120 | 25–27 → 26–28 | Meteor Falls back rooms | 25/33–40 → 26/35–44 |
| Route 123 | 25–28 → 26–29 | Shoal Cave | 26–32 → 27–34 |
| Safari Zone | 25–31 → 26–33 | Sky Pillar 1F / 3F / 5F | 47–50 → 52–55 / 50–53 → 55–59 / 54–60 → 60–67 |
| Route 130 (Mirage Island) | 5–50 → 5–55 | | |

Other tables:
- **Surfing:** 5–35 → 5–38 everywhere. The exceptions are Route 104 (10–30 → 10–32), underwater (20–35 → 20–38), Victory
  Road B2F (25–40 → 26–44) and the Safari Zone (20–35 → 20–38 and 20–40 → 20–44).
- **Fishing:** 5–45 → 5–49. Old Rod slots (5–10) stay the same.
- **Rock Smash:** 5–20 stays the same; Victory Road B1F is 30–40 → 32–44.

Every slot, with species, is in `wild[].tables.*.slots`.

## What the answer depends on (sensitivity) [computed]

Each variant reruns the whole fit with one assumption changed:

| Variant | Norman 31 | Winona 33 | Tate&Liza 42 | Wallace 43 | Drake 55 | Steven 58 |
|---|---|---|---|---|---|---|
| **baseline** (2 main battlers, 10 wild/area, Exp. Share right after Granite Cave) | 33 | 35 | 46 | 47 | 61 | 64 |
| 5 wild battles per area | 34 | 36 | 47 | 48 | 62 | 66 |
| 20 wild battles per area | 31 | 33 | 44 | 45 | 59 | 62 |
| Exp. Share picked up after Wattson | 32 | 35 | 45 | 47 | 61 | 64 |
| Exp. Share picked up after Norman | 31 | 33 | 44 | 45 | 59 | 63 |
| **3** main battlers (in both) | 41 | 44 | 56 | 58 | 74 | 78 |
| **1** main battler (starter solo, in both) | 31 | 33 | 42 | 43 | 55 | 58 |
| (b) player battles with the whole party, compared on party average | 31 | 33 | 42 | 43 | 55 | 58 |
| baseline playstyle, but (b) compared on party average instead of main battlers | 31 | 33 | 42 | 43 | 55 | 58 |

**The biggest lever is how many Pokémon a Sapphire player levels by hand.**
- **One main battler:** a Sapphire player who solos the starter ends far above anything Black 2's formula allows (Lv71
  vs Lv65 at Steven). The Exp. Share adds nothing to a lone fighter, so no scaling is needed.
- **Three main battlers:** without the Exp. Share, each of the three gets a third of the exp. With it, each gets about
  two thirds, so the curve becomes steep. Raising opponents also raises the player's exp in Black 2, so the effect
  feeds on itself.

Your "typical 1–2 main battlers" therefore spans "no change" to the baseline. The baseline is the upper end of that
range and the safer choice for keeping fights hard.

The last two rows say that if success is measured on the whole team, Black 2 + Exp. Share puts the team about where
Sapphire's two main battlers were. No scaling would be needed then. The remaining difference in (b), that the player has
six usable Pokémon instead of two, is not a level difference. A level curve can't express it without over-levelling
fights for the main battlers.

## Method

1. **Story order** (`SEGMENTS` in the script): Sapphire's main path to the Champion. It has 36 segments, 221 trainer
   battles and 225 wild battles (10 per full area).
   - Trainers come from each map's `scripts.inc`, Sapphire branch, rematches left out. Team aliases come from
     `constants/version.inc`.
   - Routes split by a story gate use object positions from `map.json`: Route 104 south/north, Route 109 beach,
     Route 110 without the Cycling Road, Route 111 without the desert, Route 118 west/east.
   - The rival is picked from the `VAR_STARTER_MON` switches.
   - Optional areas are not in the battle list: Routes 105–108, 115, 123, 125, 129–134, the Trick House, the Abandoned
     Ship, the S.S. Tidal, the Mt. Pyre interior, the desert and Route 103 east. Their levels are still converted by
     the curve (`trainers[]`, `wild[]`).
2. **Party:**
   - Mudkip Lv5 (Route 101)
   - Lotad Lv4 (Route 102), 2 Pokémon by Route 102
   - Taillow Lv5 (Route 104) and Shroomish Lv6 (Petalburg Woods), 4 by Rustboro
   - Electrike Lv13 (Route 110)
   - Numel Lv16 (Route 112), 6 by mid-game

   Species only matter for growth rates.
3. **(a) Sapphire:** the Gen 3 formula. The two main battlers (Mudkip and Lotad) share the KOs: the lower-levelled one
   takes the next KO, alone. There is no Exp. Share. The bench never battles.
4. **(b) Black 2:** Black 2's formula, base yields and growth tables, with the same battles and the same two main
   battlers.
   - From the end of Granite Cave, the battler gets full exp.
   - Every other party member, including the other main battler, gets `base >> 1`, then Black 2's level scaling with
     its own level. This is the Gen 6 rule ("50% for those that didn't battle") put into Black 2's per-Pokémon
     scaling.
   - Opponents met after that point are at f(L).
5. **Wild battles:** each one gives the expected exp over the table's slot rates, with the level uniform in [min, max],
   as Gen 3 picks it.
   - The scaled table is [f(min), f(max)].
   - One participant per battle.
   - Doubles are treated as singles.
   - Kyogre is treated as caught, so it gives no exp (assumption).
6. **Fit:** the target for each post-Exp. Share trainer battle is that its gap stays as in (a): (opponent level −
   player's main-battler level). The target for each opponent Pokémon is L + (main_b − main_a).
   - Key battles (gym leaders, E4, Champion, rival, Wally, Aqua admins and Archie) have weight 3.
   - f(L) = L + a·max(0, L − L0)^p: a by least squares, L0 and p by grid search, a ≥ 0.
   - Raising opponents raises (b)'s exp, which moves the targets, so the fit is iterated to a fixed point. It took 8
     iterations, and the parameters changed by less than 10⁻⁶ at the end.

## Assumptions you may want to change

All are at the top of `converter/level_scaling.py`; rerun the script to refit.
- `MAIN_BATTLERS = 2`: the decisive one (see sensitivity).
- `N_WILD = 10` wild battles per route or cave, with half or a quarter for sub-areas (`SEGMENTS`).
- `EXP_SHARE_AFTER = 'granite'`: the player goes back to Rustboro right after the letter. Later pickups give almost
  the same curve.
- `PARTY_PLAN` and `STARTER`.
- **Exp. Share rule:** non-participants get half the base, scaled by their own level. The alternative is half of the
  participant's final exp, scaled by the participant's level. That alternative helps a bench that is behind less, but
  barely changes the main battlers.
- Trainer choice per segment: every trainer on the path, gym trainers included. The Winstrates (an optional house
  on Route 111) are left out.

## Evidence

**Gen 3 (pokeruby)**
- Exp formula [code] (`src/battle_script_commands.c`, `atk23_getexp`, line 3326):
  - `expYield * level / 7` (:3379);
  - divided by the number of participants, at least 1 (:3393-3395);
  - the held Exp. Share splits it in half (:3381-3391);
  - trainer battle ×150/100 (:3447-3448);
  - traded ×1.5 (:3450-3452).
- Yields and growth rates: `src/data/pokemon/base_stats.h`. Tables: `src/data/pokemon/experience_tables.h`, in the
  order of `include/pokemon.h:343-348` [code].
- The starter is given at Lv5 (`src/battle_setup.c:877`), from `sStarterMons = {TREECKO, TORCHIC, MUDKIP}`
  (`src/starter_choose.c:50`). Birch's rescue battle is Poochyena Lv2 (`src/battle_controllers.c:104`) [code].
- **Exp. Share in Sapphire:** Mr. Stone, Devon Corp 3F in **Rustboro** (`data/maps/RustboroCity_DevonCorp_3F/scripts.inc:146-163`)
  [code]. He gives it once `FLAG_DELIVERED_STEVEN_LETTER` is set (:150, `giveitem ITEM_EXP_SHARE` :160). The flag is set
  when the letter is handed to Steven in Granite Cave (`data/maps/GraniteCave_StevensRoom/scripts.inc:10`).
- Sapphire's Team Aqua trainer aliases: `constants/version.inc:33-61` [code]. Examples: Mt. Chimney's leader is Archie
  (`TRAINER_ARCHIE_3`), and Seafloor Cavern's is `TRAINER_ARCHIE_2`.

**Black 2 (pokebw2)**
- `CalcBaseExpGain` [code] (`src/ov167/btl_calc.c:481-495`):
  `baseExp = PML_PersonalGetParamSingle(species, form, 9); return baseExp * level / 5;` (:493-494).
  - Parameter 9 is `ldrh [r0, #0x22]` in `PML_PersonalGetParam` (main, 0x020202ac, jump-table entry 9).
  - Offset 0x22 is `BaseExp` (`include/asm/personal.inc:90-92`).
  - So the battle uses Black 2's own yields (`data/personal/*.s`), not Gen 3's.
- `AddExpAndEVs` [code] (ov167 0x021aee0c, `config/b2_us/arm9/overlays/ov167/symbols.txt:1369`; declared in
  `include/battle/btl_server_flow.h:165`, called from `src/ov167/btl_server_flow.c:5502`) is still assembly. It was
  read with `tools/dsd dis -c config/b2_us/arm9/config.yaml -a <scratch> --overlay 167`. In order, it:
  1. multiplies by 15/10 when `BtlSetup_GetBattleType() == 1` (just before `.L_021aee54`);
  2. counts live party members holding item 0xd8 = `ITEM_EXP_SHARE` (`include/constants/items.h:205`). If there are
     any, participants share `exp − (exp >> 1)` and each holder gets `(exp >> 1) / holders` (`.L_021aeea6`);
  3. divides the participants' pool by the number of non-fainted participants (`.L_021aef34`);
  4. per Pokémon, calls `ScaleExpGainedByLevel(mon, exp, own level, enemy level)` (`.L_021af010`);
  5. multiplies traded Pokémon by 1.5, or by 1.7 (0x1b33/4096) when the language differs, and the Lucky Egg (0xe7,
     `items.h:220`) by 1.5, then applies Pass Power and caps at 100000.
- Battle type 1 is a trainer battle [code, inferred]: `IsSwitchMode` (`src/ov167/btl_main.c:1521-1522`) offers Shift
  only for type 1 single battles.
- `ScaleExpGainedByLevel` [code] (ov167 0x021af0cc, `symbols.txt:1370`):
  `exp · ⌊(2L+10)^2.5⌋ / ⌊(L+Lp+10)^2.5⌋ + 1`, capped at the exp of Lv100. Each power is computed as
  `(FX_Sqrt(v) · v²) >> 12`, with `FX_Sqrt` at 0x02073e28 and `FX_GetSqrtResult` at 0x02073f20: a 64-bit hardware
  square root, rounded. The script repeats this integer for integer.
- Growth tables: `data/growth_rates/0000-0005`. They are identical to pokeruby's from Lv2 to Lv100 (Lv1 is 0 vs 1)
  [computed].

## For the ROM work

- The Exp. Share patch goes in `AddExpAndEVs` (above). When the key item is on, skip the held-item split. Give
  participants their normal amount and every other live party member `base >> 1` before `ScaleExpGainedByLevel`. This
  is the rule the curve was fitted for.
- The converter applies `curve.table` to:
  - every trainer Pokémon level;
  - every wild slot's min and max, except the land tables of the maps before the Exp. Share. These are unchanged by
    the curve anyway.

  `trainers[].new_levels` and `wild[].tables` are already converted.
