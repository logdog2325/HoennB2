# Emerald's Battle Tents and Trainer Hill (battle_tents, 2026-10-18)

Pokémon Emerald NDS only: every file and patch below is gated on `version.is_emerald()`, the `emerald/` source folders or
`data/versions.json` ("emerald" rooms). Sapphire and Ruby stay byte-identical. Status: built and checked; the test ROM
`~/Desktop/Emerald_TENTS_TEST.nds` waits for the user's melonDS test. Nothing is committed.

The rules come from pokeemerald, not from memory: `src/battle_tent.c`, `src/data/battle_frontier/battle_tent.h`,
`include/constants/battle_tent.h`, `data/maps/*BattleTent*/scripts.inc`, `src/trainer_hill.c`,
`src/data/battle_frontier/trainer_hill.h`, `data/maps/TrainerHill_*/scripts.inc` and `data/scripts/trainer_hill.inc`.

## 1. The three Battle Tents

All three use the Frontier library. They are three battles in a row against the tent's own 30 trainers (no trainer twice in
a challenge). Each prize is paid once per challenge won. A tent challenge has no level limit, and its opponents' Pokémon
are at least level 30 (`TENT_MIN_LEVEL`, `TENT_STAGES_PER_CHALLENGE`). There is no BP and no streak.
The tent lobby flow is in `src/field_scripts/scenes/battle_tents_lib.inc`: the attendant, the eligibility check (the
Frontier's rules: three different species, different held items, no banned species), the save, and the walk through the door.
If the Bag is full, the prize waits in record key 15 until there is room.

| tent | rules | trainers / sets | prize | engine |
|---|---|---|---|---|
| Verdanturf (zones 519 lobby, 522 corridor, 525 battle room) | Battle Palace: the Pokémon choose their moves by Nature | 30 trainers, 45 sets (`gVerdanturfBattleTentMons`) | Nest Ball (`sVerdanturfTentRewards`) | frontier_palace_arena.c, tent mode (`FrontierPA ..., FRONTIER_FACILITY_PALACE \| 0x10`) |
| Fallarbor (520, 523, 526) | Battle Arena (Set KO Tourney): one Pokémon each at a time in party order, no switching, the referee's judgment after 3 turns | 30 trainers, 45 sets | Hyper Potion (`sFallarborTentRewards`) | frontier_palace_arena.c, tent mode (`ARENA \| 0x10`) |
| Slateport (521, 524, 527) | Battle Factory (Battle Swap): six rentals, keep three; after each win, swap one for one of the beaten trainer's | 30 trainers, 70 sets | Full Heal (`sSlateportTentRewards`) | frontier_factory_dome.c, Slateport tent mode (`FrontierCmd 60-65`) |

- **Opponent level:** the Palace and Arena tents use the highest level among the player's three, but at least 30
  (`SetTentPtrsGetLevel`: `GetHighestLevelInPlayerParty` while the party is the three, min `TENT_MIN_LEVEL`). Slateport
  uses level 30 for both sides (`FillFactoryTentTrainerParty`).
- **Opponent Pokémon:** IVs 0 (the tent sets' own spreads and Natures).
- **Slateport rentals** (`GenerateInitialRentalMons`): no set twice and a species at most twice.
- **Slateport opponent** (`GenerateOpponentMons`): three sets that share no species with the rentals and repeat no
  species or item. It has no AI scripts, as in Emerald's tents (`GetAiScriptsInBattleFactory`: `FRONTIER_LVL_TENT` -> 0).
- **Trainer data:** `converter/gen_battle_tents.py` reads pokeemerald and writes `data/emerald/battle_tents.json`.
  `b2tools/patches/frontier_factory_dome.py` then writes it into arc 211 file 1891 (`'TENT'`: per tent its trainers, set
  lists and 16-byte sets). It is a new data file of my own, so `gen_trainers.py` stays untouched. Trainer names and the
  three speeches are in the battle rooms' texts (lines 100+ / 200+), written by `b2tools/battle_tents_text.py`. That
  script also writes the lobby, corridor and room lines and `src/include/battle_tents_lines.h`.
- **Lobby people:**
  - Verdanturf: the TM45 Attract girl.
  - Slateport: the TM41 Torment giver.
  - Scott, in the Verdanturf and Fallarbor lobbies. No new flags are allocated, because `story_ids.json` belongs to
    another helper, so his visibility follows story-state proxies:
    - Verdanturf: badge 3 and Fiery Path not yet visited.
    - Fallarbor: Fiery Path visited and Meteor Falls state 0.
    - His "met" bits are in key 15.
- **Rooms:** `work/agents/battle_tents/tools/rooms_tents.py` builds them into `data/interior_layouts/*BattleTent*.json`,
  `data/interiors/emerald/519-527.json` and `work/interiors`.

## 2. The Trainer Hill (Route 111; zones 543 entrance, 544-547 floors 1-4, 548 roof, 549 elevator)

It opens after the Hall of Fame (`FLAG_SYS_GAME_CLEAR`). The challenge is the base game's four modes: Normal, Variety,
Unique and Expert Tag Match. Each mode has 4 floors with 2 trainers per floor (data from `sHillData` in
`trainer_hill.h`, via `converter/gen_trainer_hill.py` -> `data/emerald/trainer_hill.json`).

**Entrance (the counter trigger (9,6)):**
- The player must save once before the first challenge (`savedGame`).
- The player then picks Yes / No / Info, then the mode.
- The party is healed and the timer starts.

**Floors:**
- Each floor's layout is the mode's own: the mode rooms are the floor zone's alt rooms on map replace events 3/4/5. The
  zone init sets these events and reloads.
- Trainer sight is the trainer's facing and Emerald's range (`TrainerEye` on NPC p0). `trainer_hill.c`'s per-step check
  handles it.
- One trainer who sees the player battles a single battle. Two at once battle a double battle against both, if the
  player has two Pokémon able to fight (`CheckForTrainersWantingBattle`).
- Talking to a trainer starts a single battle. Talking to a beaten trainer shows speechAfter.
- Enemy Pokémon are at the level of the player's highest Pokémon (`SetTrainerHillMonLevel`), with the data's IVs, EVs,
  ability, Nature (personality % 25), friendship and held item. There is no experience.
- Losing ends the challenge with no whiteout. The player is sent to the counter, hears "That was too bad", is pushed
  back and healed.

**Roof:**
- The first talk with the owner stops the timer and marks every trainer as battled.
- The prize is the mode's list's item for the time: under 12, 13, 14, 16 or 18 minutes, else the last item
  (`GetPrizeItemId`, game-clear lists; Expert takes list + 1). It is given once per challenge; with a full Bag it is
  kept for later.
- A time faster than the mode's best becomes the new record on the time board (8,10).

**Elevator:** back to the entrance (17,11). Leaving the building ends the challenge (`Route111_OnTransition`), done by
the per-step check outside zones 543-549.

**Mart clerk:** Emerald's Basic list, or Expanded after the Hall of Fame, in Emerald's order. These are shop ids 23
and 25 (the two one-item fillers), and a/2/8/2 grows by 40 bytes (1336 -> 1376; fairy.py had already grown it past
Black 2's 1300).

**Engine:** `b2tools/patches/trainer_hill.c` / `.py`, in the Frontier code area (about 6.5 KB). It provides:
- script command 562, `ThHill op, var`;
- the per-step trainer eyes;
- `BtlSetup_LoadTrainer` for trainer slots 534/535;
- the battle's speechLose.

**Texts:** `b2tools/trainer_hill_text.py` writes the texts and `src/include/trainer_hill_lines.h` (line numbers and the
engine's numbers). **Scripts:** `src/field_scripts/emerald/1086-1099` and `scenes/trainer_hill_lib.inc` /
`trainer_hill_floor.inc`. **Rooms:** `work/agents/battle_tents/tools/rooms_hill.py`.

## 3. Record keys (Frontier record area, save block 0x38; notes/FRONTIER.md 6)

| key | use |
|---|---|
| 15 | tents: bits 0-2 a prize waiting (Verdanturf, Fallarbor, Slateport); bit 8 / 9 Scott met in Verdanturf / Fallarbor |
| 44 | tents: bits 0-4 the current opponent (0-29); 5-9 / 10-14 the opponents of battles 1 and 2 |
| 45-47 | Slateport: the six rentals (tent set indices, one per byte; 0xFF none) |
| 60 | Hill: bits 0-1 the mode, 2 active, 3 owner spoken to (timer stopped), 4 prize received, 5 final time checked, 6 lost, 7 saved before the first challenge, 8-15 the floors' trainers beaten (8 + 2 (floor - 1) + i) |
| 61-62 | Hill: the play time (seconds) at the start, or (owner spoken to) the final time |
| 63, 68, 69 | Hill: the four modes' best times, 12 bits each (seconds + 1; 0 none) |

Keys 44-47, 60-63 and 68-69 are the Arena, Pike and Pyramid doubles streak keys, which those facilities never use
(16 + 8f + 4m + 2l). Keys 70-71 are still free. All of these keys are within 0-94, as save_compat requires.

## 4. Left out, and why

- **e-Reader floors and the Japanese "Default" mode:** the e-Reader floor sets only exist on Japanese e-Cards. The
  English ROM has only the four base modes, and all four are built.
- **Hill timer resolution:** the timer is Black 2's play time, which counts whole seconds (also in battles and menus,
  and kept across a save). The hundredths always show 00; the 59:59 cap shows 59:59.99 as in Emerald.
- **Hill messages:**
  - The winner's speechWin after a loss shows in the field before the warp, not in the battle.
  - The time board is a message, not Emerald's records window.
  - The Hill trainers' eye-contact music by class is not played.
- **Hill map tiles** (Black 2 has no tile for these): the slide arrows and the jump, spin, glitter and sound mats are
  drawn only. Ledges and the slippery floor work. The list of drawn-only tiles is in
  `work/agents/battle_tents/hill/hill_special_tiles.json`.
- **Hill rooms:**
  - The floor board does not show the floor number.
  - The counter gate (17,10) never opens, so the elevator brings the player to (17,11).
  - The elevator is the Battle Tower's car.
- **Tents:**
  - Emerald keeps the camera still with a stand-in player; here the player walks in.
  - The Arena referee's drum, snore and bang sounds are left out (as in the Frontier Arena).
  - Scott edge case: if Fiery Path is visited before Wattson's badge, Verdanturf's Scott does not appear (no new flags
    could be allocated).
- **World doors:** the outdoor doors resolve at the next world build. The test world
  `work/agents/battle_tents/world` resolves them by hand.

## 5. Checks and tests

- Build-time asserts:
  - `frontier_factory_dome.py`: the tent file's index.
  - `trainer_hill.py`: the Hill zones in a row; the chained call sites unchanged between apply and apply_code;
    EVCMD_TABLE[562] still Black 2's; shops 23 / 25 still the one-item fillers.
- Checkers: `script_check.py`, the rooms checks (`work/agents/battle_tents/tools/rooms_check_tents.py`,
  `hill_check.py`), the camera check (`interior_sweep_check`), `outdoor_check.py`, `frontier_bp_check.py`.
- Test ROM: `work/agents/battle_tents/build_test_rom.sh`.

## 6. Self-test (2026-10-18, DeSmuME muted, the playtest harness)

Driver: `work/agents/battle_tents/tests/pt/tt.py` (a copy of freeze_fix's harness; `ice.py` routes over the Hill
floors' ice and ledges from data/emerald/trainer_hill.json). Cold boot -> Littleroot's sign (the test kit) -> each place
(the sign's warp rewritten per place in an APFS clone of the test ROM). Screenshots: `screenshots/battle_tents/`;
every message: `work/agents/battle_tents/log/transcript_<phase>.txt` (copied to `screenshots/battle_tents/messages/`).

- Verdanturf: the pick (Blaziken / Swampert / Sceptile), the save, three Palace battles won (opponents at Lv 50 =
  the three's highest), the Nest Ball.
- Fallarbor: three Arena battles won; the referee's judgment reached (Mind / Skill / Body, "4 to 2", "2 to 4"), the
  Hyper Potion.
- Slateport: six Lv 30 rentals, three rented, battle 1 won, REST (save and soft reset), Continue -> "we've been waiting
  for you" -> the corridor -> swap (Baltoy given, the beaten trainer's Kirlia taken: Kirlia led battle 2), battles 2-3
  won, the party returned, the Full Heal.
- Trainer Hill: Variety (bottom to roof without battles: the timer sign, the owner's Elixir and "marvelously quickly",
  his second talk, the elevator, the time board "Variety 1 min. 12.00 sec."); Normal (4F's double spot (7,12): both
  trainers' greetings, "challenged by Psychic Keenan and Aroma Lady Kristina", a double battle won with both defeat
  lines; the owner's TM11 (Sunny Day) at 8:35); a deliberate loss to Alaina (1F): no whiteout, her speechWin, the
  counter, "That was too bad", the push back, the healed party; the counter asks again; the Mart's Expanded list in
  Emerald's order; the nurse.
- Fixed by it: the Hill timer read the save block's play time (written only when saving: it stayed 0); it reads
  GameData's live play time now (GameData + 0x2f0, the copy GameData_SaveBackup saves).
