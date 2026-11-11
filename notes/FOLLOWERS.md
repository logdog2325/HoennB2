# The following Pokémon (Birch's seventh question)

User (2026-11-01): port PearlB2's following Pokémon to the Hoenn games. The module is PearlB2's, copied unchanged
(PearlB2 notes/FOLLOWERS.md has its design and "Alpha 0.1 fixes"); this file is HoennB2's side.

## What it does
- Birch asks it as the seventh question, after the Exp. Share (now "Sixth..."): "And last... your partner! Will your
  first Pokémon walk with you wherever you go?" YES/NO, the cursor on YES like the others, B = NO. "seven quick
  questions" in his intro. It sets the event flag FLAG_POKE_FOLLOWER (a new saved flag, 2563); clear (NO, and every save
  from before the question) = no follower. Not fixed for the game, unlike the other answers: see the next point.
- A lab aide in Prof. Birch's Lab in Littleroot, at Gen 3 tile (3,10) (all versions; the Aide's sprite, `data/story/followers/`,
  0792 Script_9, text 0625 lines 38-43: placeholder rows in every version's 0625, filled with our C on; Emerald's Johto lines
  are 44-54 since postgame_dex 2026-11-09, before that they were overwritten), offers it: flag clear, "would you like your first Pokémon to walk with you?" YES/NO
  (cursor on YES, B = NO), YES sets the flag; flag set, "should it go back in its Poké Ball?", YES clears it. So saves from before
  the question can turn it on and every save can change its mind. Only the flag changes; follower.c needs no call: at the
  next step it makes the follower or deletes it (no ball shows when it is deleted), and if the player saves first, it goes
  when the field opens (Follower_FieldOpen).
- Who follows: party slot 1; an Egg or a fainted slot 1 = nobody. When slot 1's species has no walking sprite (103 Gen 5
  species), the next party Pokémon that has one and isn't an Egg or fainted.
- Sprites: Black 2's official walking Pokémon only (ARCID_TPOKE), never made-up pixels. Shiny Pokémon show their normal
  colours. 64 x 64 sheets (31: the big legendaries, Steelix, Wailord) only on the overworld. A code this build painted
  over is never shown (followers.py compares a/0/4/7 and a/0/4/8 with Black 2's).
- It hides on the bike and on the water and comes back behind the player on the first step on foot; after a map change it
  appears on the first step; left behind (ledges, slides, forced moves), it is put back behind the player at the next step.
  A Poké Ball shows for 14 frames when it is put away or sent out (Black 2's item ball, code 110, and its ball sound).
- Talking to it: its cry and one of 9 lines (Pokémon Pearl's Amity Square lines, as PearlB2's).

## Off zones (`OFF` in b2tools/patches/followers.py)
By Pearl's rules (Battle Tower and Hall of Fame; Black 2's IsZoneNormal already covers its Union Room, colosseums, Battle
Subway and Entralink zones), extended to our rooms: BattleTower_Lobby/Corridor/Elevator/BattleRoom, the PWT (192, 193),
EverGrandeCity_HallOfFame, SingleBattleColosseum, DoubleBattleColosseum, TradeCenter, RecordCorner, UnionRoom, every
BattleFrontier_Battle* room, every *_BattleTent* room, TrainerHill except the Entrance, the *_ContestHall stages, every
Underwater* map (Dive). Scripted scenes elsewhere use the module's hooks: a list that walks or jumps someone puts the
follower away until the player's next step.

## Files
| File | What |
|---|---|
| decomp `include/follower.h`, `src/hoennb2/resident/follower.c` | the module, PearlB2's, unchanged (private: decomp_changes/) |
| decomp `include/follower_port.h` | our switch: `#include "hoennb2.h"`, `FOLLOWER_MODULE HOENNB2` |
| decomp ov036 `fieldmap.c`, `fieldmap_event.c`, `fldmmdl_movecode_pair.c`, `scrcmd_fldmmdl.c`, `entrance_camera.c`, `event_trainer_eye.c`; ov012 `event_action_call.c`, `pair_sys.c` | the hooks, `#if HOENNB2`, each only changes the function a call goes to (PearlB2's table) |
| `b2tools/patches/followers.py` | the config into the resident pool, its address into `gFollowerConfig`; build_rom.py adds this patch itself, last, when our C is on |
| `b2tools/patches/fairy.py` `intro_script(ov294, follower)`, `src/text/overrides_followers.json` | the question, text 54 line 36, "seven", "Sixth" |
| `src/field_scripts/1260_global_pokedex_rating.s` Script_1 (global 10380, `#ifdef HOENN_FOLLOWERS`), text 0434 lines 23-31 | talking to it |
| `src/include/hoenn.h` | FLAG_POKE_FOLLOWER 2563, VAR_FOLLOWER_SLOT 0x4170 (converter/gen_story_ids.py --claim Emerald) |

With our C off (`HOENN_DECOMP_C=0`) or `HOENN_CODE=base`: no question, no lab aide, no text, no script, no follower: `b2decomp.c_on()`.
Test builds (any `HOENN_TEST_*`) leave the config out unless `HOENN_TEST_FOLLOW=1`, since the drivers answer YES to every
question by mashing A.

## Birch's question in the intro script
Script 9 + the dead FAREWELL (21 entries) and script 10 RIVAL_NAMED (14) were full with six questions. The seventh takes
script 11, the dead RENAME_RIVAL (4 entries): script 9 now also shows the fifth question's text before its jump (the
interpreter jumps at once, and YES_NO only reads the entries after it in its own script), script 10 has the fifth's menu,
the sixth, the seventh and "you're ready" text, and script 11 ends it. Without the followers (`follower=None`) the old
layout stays byte for byte. `make_states.py` presses 118 times now; `mk_boot.py` has a tenth argument, follower yes|no.

## Budgets
Code in the resident section: the module about 1.9 KB, its config 132 B in Sapphire/Ruby (more in Emerald's longer off list: 66
zones). Sprite slots: one for the follower, one for the ball; the fullest zones are Route 123 at 28/32 (S/R) and 33/40
(Emerald), so 30 and 35. One or two more actors of 64. Nothing new is saved but the flag and the slot work.

## Test
Not run yet (the user's process: everything together on one combined ROM): `work/agents/decomp_src/pt/ft.py` has the cases,
the list is in the lead's report. Static proofs done: the module compiles and links unchanged, `HOENNB2 0` gives the dump's
code, and every hook is the same-size call change PearlB2's are.
