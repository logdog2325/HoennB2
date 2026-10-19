# Pokémon Emerald NDS: rematches (emerald_rematch, 2026-10-18)

Emerald only. Sapphire and Ruby builds are unchanged: every change is in an Emerald-only file or patch, or behind
`#ifdef HOENN_EMERALD` (checked: the eight Gym scripts assemble to the same bytes for Sapphire and Ruby before and
after; `gen_trainers.py` for Sapphire writes the same files, `HOENN_VERSION=ruby gen_trainers.py --check` passes).

## What the player gets
- **Route trainers** (64 of Emerald's rematch table, `gRematchTable` in pokeemerald `src/battle_setup.c`): once the
  player has **5 badges** (Emerald's rule for any rematch), talking to a beaten trainer of the table gives Emerald's
  rematch line, then YES / NO. YES: a battle with Emerald's rematch team. Afterwards, and for the rest of the day, the
  trainer says Emerald's after-rematch line. **Once a day** per trainer (Black 2's midnight reset).
- **Tier**: Emerald's rematch teams 2-5 follow the badges: 5 badges tier 2, 6 tier 3, 7 tier 4, 8 tier 5.
- **Gym Leaders** (8): after the **Hall of Fame**, in their Gyms, once a day: Emerald's rematch line, YES / NO, a
  **double battle** with Emerald's rematch team (Tate and Liza: both, as their first battle). Tiers 2, 3, 4, 5 in turn
  (one more each rematch won; the fifth again after it). Before Wattson's New Mauville job is done (his Thunderbolt TM)
  only the first rematch, and none with Wattson (Emerald's `FLAG_WATTSON_REMATCH_AVAILABLE` rule,
  `src/gym_leader_rematch.c`).
- **Wally** (added 2026-10-18, "add the wally battles too"): after the Hall of Fame he waits at Victory Road 1F's
  exit, where Emerald places him (pokeemerald object 7 at (31,9) = zone 170 tile (39,17); Sapphire's post-game Wally
  object, shown by the Hall of Fame: `FLAG_HIDE_WALLY_DEFEATED_VICTORY_ROAD` = Emerald's `FLAG_HIDE_VICTORY_ROAD_EXIT_WALLY`,
  set at new game, cleared in the Hall of Fame). First talk: his post-game battle (TRAINER_WALLY_VR_2, id 742). Then once
  a day: YES / NO, Emerald's tiers VR_3, VR_4, VR_5 in turn (the fifth again after it), Emerald's lines
  (`REMATCH_WALLY_VR`, a post-game row: gym 9, its progress in `VAR_EM_REMATCH_POSTGAME`). Victory Road 1F's four Wally
  lines are Emerald's in an Emerald build (src/text/script/emerald/0228_room_VictoryRoad_1F.txt: "…" where Sapphire's
  say "...").
- Emerald's other Wally battles were already built and keep working: Mauville City (TRAINER_WALLY_MAUVILLE = id 741,
  Emerald's party = Sapphire's TRAINER_WALLY_2, Emerald's lines in src/text/scenes/emerald/MauvilleCity.txt, Scott
  after it) and Victory Road's entrance battle (TRAINER_WALLY_VR_1 = id 645, Emerald's party). Since 2026-10-18 the
  entrance battle is at Emerald's spot: step triggers (2,23) / (3,23) by the entrance (Sapphire / Ruby keep (34,3)-(34,5)
  by the exit), Wally walks in from (12,25) and then stands at (2,24) / (3,24) facing down until the Hall of Fame
  (notes/EMERALD_STORY.md "Fidelity fixes").
- Pairs (Anna & Meg, Lila & Roy, John & Jay, Amy & Liv, Kira & Dan): each NPC says its own rematch lines; a double
  battle; with one Pokémon able to battle, Emerald's "you need two Pokémon" rematch line.
- Levels: through `data/level_scaling.json`'s curve, like every trainer (`gen_trainers.py`). Default-move parties get
  Gen 3's level-up moves written out, items, AI and prize money as the first battles.

## Design (why)
Black 2's trainer table is full: 814 ids (a/0/9/1-2), of which Emerald's registry has 88 left (55 + 33); Emerald's 288
rematch tiers do not fit, and ids above 813 would have defeat flags (id + 1520) on Black 2's system flags and need a/0/9/1 and
a/0/9/0 to grow (no reserve: the ROM's file table would move). So the tiers are **not trainers** (option (a) of the
brief, with a code hook):
- **Rematch slots**: one per tier (Tate & Liza: two a tier, split as their first battle: the leads one each, Solrock
  Tate's, Lunatone Liza's, the others to whoever has fewer). Record (20 B) in **a/0/8/9 file 1** at slot × 20 (file 0
  is the trainer message table; Black 2 reads it by file number), party in **a/0/9/2 entry 814 + slot**. Both archives
  have a build_rom.py RESERVE: nothing moves in the ROM.
- **The battle keeps the first battle's trainer id** (name, picture, class, NPC, defeat flag all its own). While a
  rematch is armed (script command, right before `CallTrainerBattle`), `b2tools/patches/emerald_rematch.c` makes
  Black 2's two readers of trainer data, `TrainerData_ReadTrainerData` (arm9 0x020306e0) and `TrainerData_ReadParty`
  (0x02030724), load the slot for that id; every reader of trainer data goes through them (TrainerUtil_LoadTrainer /
  LoadParty, TrainerData_GetParam: battle style, class, prize money). The battle's defeat line (type 1) becomes the
  trainer's rematch defeat line (type 103) through the battle trainer-line call frontier_pike / frontier_pyramid
  already chain on. Disarmed right after the battle, and at every boot / soft reset (.bss in the Frontier code area).
- **Messages** are records of the first battle's trainer (a/0/8/9 file 0, text 381), Emerald's
  `trainerbattle_rematch[_double]` lines: 100 intro, 101 after, 102 "need two", 103 in battle; 104-106 the second NPC
  of a pair. They fit in Black 2's record count (247 new records; 362 filler records left).
- **Trigger** (Emerald's Match Call is not ported): talking to the trainer. Route trainers talk through Black 2's
  global trainer script 1239: Emerald's own copy `src/field_scripts/emerald/1239_global_trainers.s` adds one call in
  the "already beaten" path. Gym Leaders: `em_gym_rematch` (src/include/hoenn_rematch.inc) first in each Leader's
  "already beaten" branch (empty in Sapphire / Ruby). No eye-contact rematches.

### Differences from Emerald (for the user to decide)
- Emerald offers a route rematch when Match Call / a 31% roll after 255 steps says the trainer wants one, and the tier
  is the **next one after the last rematch won** (2, 3, 4, 5 in turn), whatever the badges. Here: every day, tier by
  badges. Emerald's order needs 2 bits a trainer (~8 more saved works: 64 × 2 bits); say if wanted.
- Emerald's Leaders become ready at random (31% every 20 trainer / 60 wild battles) and in step with each other; here
  each Leader is ready once a day.
- The first battle does not count as today's: a trainer beaten for the first time offers a rematch right away when
  the player talks to it again (5 badges or more).
- (Done 2026-10-18: Victory Road's entrance battle now stands at Emerald's spot by the entrance, see above.)
- The Elite Four and Wallace rematch as they already do (their rows have no tiers).

## Ids (fixed once given)
| What | Id |
|---|---|
| Script command | 299 (Black 2's BMAnmPlayInv, unused by every Black 2 and Hoenn script) = `EmRematch var, op, arg` |
| Saved works | `VAR_EM_REMATCH_DONE_0-4` 0x4154, 0x4155, 0x415F, 0x4160, 0x4161 (fought today: bit row % 16 of work row / 16); `VAR_EM_REMATCH_LEADERS` 0x4163 (2 bits a Gym: tiers beaten 0-3); `VAR_EM_REMATCH_POSTGAME` 0x4164 (2 bits a post-game row, gym 9 + n: Wally = bits 0-1) |
| Flag | `FLAG_DAILY_EM_REMATCHES` 2756 (midnight-reset block; clear = a new day: the code clears the DONE works, sets it) |
| Trainer ids | none new: rows use the first battles' ids (data/emerald/hoenn_trainers.json) |
| Rematch slots | 0-294 (data/emerald/hoenn_rematch.json "slots", src/trainers/emerald_rematch/NNN_*.s): 0-291 the first 72 rows, 292-294 Wally's VR_3-5; rows 0-71 in gRematchTable's order, row 72 Wally (REMATCH_LATE: rows and slots are only appended) |
| Message types | 100-106 of the first battle's trainer (above) |
| Archives | a/0/8/9 file 1 (records), a/0/9/2 entries 814-1108 (parties) |
| Code | Frontier code area (~2 KB), arm9 0x020306e0 / 0x02030724 entry jumps, ov167 battle-line call, EVCMD_TABLE[299] |

All works and the flag came from the Emerald reserve / the daily pool (`converter/gen_story_ids.py --claim Emerald`;
`claim()` now gives a FLAG_DAILY_ name a midnight-reset flag).

## Files
- `converter/gen_trainers.py`: `rematch_rows_emerald`, the rematch messages (REMATCH_MSG), the rematch slots;
  outputs `data/emerald/hoenn_rematch.json`, `src/trainers/emerald_rematch/` (+ the Emerald overlays' messages).
  Rerun: `cd converter && HOENN_VERSION=emerald python3 gen_trainers.py` (`--check` compares).
- `b2tools/patches/emerald_rematch.py` / `.c`: the patch (last in the lists of `story_build.sh` / `rebuild_slice.sh`).
- `src/field_scripts/emerald/1239_global_trainers.s`, `src/include/hoenn_rematch.inc`, the eight Gym scripts
  (1166 Rustboro, 0050 Dewford, 0478 Mauville, 0290 Lavaridge, scenes/PetalburgCity_Gym_ch6.inc + 0904, 0238 Fortree,
  0644 Mossdeep, 0046 Sootopolis), Victory Road 1F (0340: `#ifdef HOENN_EMERALD` around Wally's rematch),
  `src/text/script/emerald/0228_room_VictoryRoad_1F.txt` (Emerald's Wally lines).
- `data/story_ids.json` / `src/include/hoenn.h`: the ids above.

## Testing
- Checks (2026-10-18): `HOENN_VERSION=emerald gen_trainers.py --check` current; `HOENN_VERSION=ruby ... --check` current;
  Sapphire's run writes the same files as committed; the eight Gym scripts assemble to the same bytes for Sapphire and
  Ruby; `script_check.py` on the test ROM: the same counts as work/world_emerald.script_check.txt (no new finding; the
  Gym zones and Routes 102/116 clean).
- Sizes in the test build: a/0/8/9 15,212 of 26,112 B (10,900 left), a/0/9/2 45,228 of 59,904 B (14,676 left), Frontier
  code area +2,070 B; archive sizes unchanged (fixed), so the ROM layout does not move. pack 0: 22,784 B spare (as before).
- Where the trainers stand in the ROM (the patch's log line): 62 of the 64 route trainers are placed as eye-contact
  NPCs (all five pairs with both NPCs), the 8 Leaders call em_gym_rematch. Thalia (Abandoned Ship Rooms 1F) and
  Gabrielle (Mt. Pyre 3F), not placed before, are 3000 + id NPCs since 2026-10-18 (data/story/emerald/e_trainers.json,
  notes/EMERALD_STORY.md), so they rematch as the others.
- Test ROMs (sign kits, work/agents/emerald_rematch/): `build_test_rom.sh` (Groudon + Kyogre Lv 100, Hall of Fame, 8
  badges, Roxanne / Josh / Tommy / Marc and Route 116's Karen / Jerry beaten; warps in front of Roxanne; passed in
  melonDS 2026-10-18: Roxanne's rematch, once a day, Route 116 YES / NO) and `build_wally_test_rom.sh` (a boy: the
  Hall of Fame state, warps below Victory Road's post-game Wally; a girl: warps below Wally in Mauville City).
