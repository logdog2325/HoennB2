# Battle Pike (Emerald only; frontier_pike, 2026-10-12)

Emerald's Battle Pike in the Emerald build (`HOENN_VERSION=emerald`). Sapphire and Ruby never see it: every file is in
an Emerald overlay folder or returns at once outside Emerald (`patches/frontier_pike.py`: "nothing (Emerald only)").
Built on frontier_core's shared parts (notes/FRONTIER.md: records, lobby macros, symbols, BP, the songs and Lucy's
pictures). Claims: notes/FRONTIER.md section 6.

## How it plays (as Emerald)
- **Lobby** (zone 399, the island's door 14 = warp 16 of zone 17): the attendant (`fr_lobby_attendant`): Challenge /
  Info / Exit, Lv. 50 or Open Level, three Pokémon picked on Black 2's pick screen, the save, the walk to the curtain.
  Back from a challenge (`fr_lobby_returned`): quit without saving, won (BP; +10 after Lucy), lost; the party's order
  and held items come back. The Hiker, the Twin and the Beauty; the results board and the rules board.
- **Corridor** (400): "Your Battle Choice challenge has now begun…", room number 1, healing on.
- **Three-path room** (401): three curtained doorways (step triggers). The hint giver says which doorway he has a
  feeling about and what kind of room it is (nostalgia / whispering / aroma of Pokémon / people), or, before Lucy,
  "a terrifying event…". The attendant: the room you are in (Emerald's own count: 1, 3, … 13), go on, save and quit
  (the game saves and resets; Continue brings you back to this room: "We've been awaiting your return…"), retire.
- **The rooms** (402 normal, 403 wild): Emerald's room choice (pokeemerald src/battle_pike.c: the hinted doorway holds
  the hinted room, the other two a random room of another hint group; status/double rooms only when the party can take
  them; healing rooms off once the party is healthy): single battle, hard battle (then a full heal), double battle
  (two trainers, one Pokémon each), full heal, part heal (one or two Pokémon), status (Kirlia or Dusclops: Toxic,
  Will-O-Wisp, Thunder Wave, Hypnosis or Ice Beam on Emerald's odds), an NPC with an easy-chat line (25 people, 42
  lines), the wild room (a maze; Emerald's per-step check, rate 10; Emerald's land slots: Seviper 26%, Milotic 26%,
  the third species 48% (Dusclops, then Electrode, Breloom, Wobbuffet by streak tier: rooms up to 280 / 560 / 840 /
  more), with their Pike moves and levels; a Static lead picks Electrode half the time, as Emerald). Each doorway and
  each room left adds 1 to the room number and the streak (Emerald counts both); after room 14 the final room (404)
  and the lobby.
- **Trainers**: Emerald's 300 Frontier trainers (name, class, greeting, defeat line, set list; trainers met once a
  challenge), Emerald's FillTrainerParty (sets of the trainer's list, no species/item twice, Lv. 50 sets at Lv. 50,
  fixed IVs by trainer, Emerald's bug: the double battle's second trainer draws from the first's list). No experience.
  Level: 50, or Open Level: the party's highest, at least 60.
- **Lucy** (Pike Queen) at Emerald's streaks (28th room: silver, 140th: gold, then every 56): the heal-before-queen
  odds, her speeches, her silver/gold parties, "Urk…" / "Darn!", the Luck Symbol (silver, gold) on the Frontier Pass.

## Files
| what | file |
|---|---|
| data generator (reads external/pokeemerald only) | converter/gen_frontier_pike.py -> data/emerald/frontier_pike.json, src/text/script/emerald/0628-0633_room_BattleFrontier_BattlePike*.txt, src/field_scripts/scenes/frontier_pike_lines.inc |
| patch (data file, battle slots 529-531, code in the Frontier code area + ITCM, command 290, call redirects) | b2tools/patches/frontier_pike.py, b2tools/patches/frontier_pike.c |
| scripts (named by the zones' Black 2 numbers, installed at the rooms' own numbers 1950-1961) | src/field_scripts/emerald/0798-0809_room_BattleFrontier_BattlePike*.s, src/field_scripts/scenes/frontier_pike_lib.inc |
| zone entities (Emerald tiles; the room origin is added) | data/interiors/emerald/399-404.json |
| rooms (pike_rooms helper: pokeemerald layouts, interior pipeline) | data/interior_layouts/BattleFrontier_BattlePike*.json, _styles_frontier_pike.json; proof screenshots/frontier_pike/rooms_*.png |
| claims | data/emerald/hoenn_interiors.json (six rooms, "claimed"), data/versions.json (rooms: "emerald"), data/emerald/hoenn_music.json zone_songs 399-404 mus_b_pike |

Shared builders touched (minimal, gated): b2tools/models_interior.py (recipe key "decomp": a room of pokeemerald's
map; recipes without it build as before), converter/allocate_interiors.py (Emerald mode: claimed rooms keep their
entries).

## Code (b2tools/patches/frontier_pike.c: 7.2 KB in the Frontier code area, 0.3 KB of ITCM)
- Since emerald_itcm (2026-10-12, Emerald v1.0.1) the code lives in the Frontier code area (main RAM 0x023D0000+,
  FRONTIER.md 7: loaded at boot, resident in battles too); only the battle's trainer-line hooks (PK_TrainerMsgExists /
  PK_TrainerMsgLoad, built with -DPK_PART_LINES) stay in ITCM. Before, all 7.6 KB were ITCM, and ITCM ran out when
  sprite_switch grew (Emerald's NEW Brendan, 40 sheets). frontier_pyramid chains onto these hooks wherever they are.
- `EmPike var, op, a, b` (command 290): ops PK_* in frontier_pike_lib.inc (room choice, hints, status, heals, wild
  Pokémon, Lucy, items, party order, BP, eligibility).
- Hooks (each call checked to be Black 2's first): party load (the battle keeps the challenge's three), trainer load
  (slots 529/530 = the room's Frontier trainers, 531 = Lucy, class 31 Pike Queen), wild setup (Pike moves), the field's
  per-step check (the wild room), the battle's trainer lines (Emerald's defeat lines).
- Records (frontier_core's u16[96]): keys 72-78, 91-94 (FRONTIER.md 6).
- Black 2's party status is one value (1 paralysis, 2 sleep, 3 freeze, 4 burn, 5 poison), not Gen 3's bit word.

## Tested in game (Emerald test builds, muted DeSmuME; work/agents/frontier_pike/out, screenshots/frontier_pike/)
Lobby, picks, corridor, hint giver, full heal, status room (freeze shown as FRZ), part heal (it cured it), NPC room,
wild room (encounters, a won battle with the Pike moves, fleeing, the maze to the exit), single, hard (heal after),
double (both defeat lines), the in-battle defeat lines (Emerald's), save and quit -> Continue -> resume, a loss (back to
the lobby, results recorded, party order and HP back), Lucy (Open Level: her warning, Lv. 60 party, "You are challenged
by Pike Queen Lucy!", "Urk…", the Luck Symbol, the final room, the lobby's Pike Queen line and BP).

## Differences from Emerald
- Black 2's battle UI: the Bag can be used and the "switch?" prompt shows (Emerald: Set style, no items); Frontier
  trainer battles cannot be forfeited (Emerald asks).
- The start menu keeps Bag and Save inside the Pike (Emerald hides them).
- Badly poisoned (Toxic from the status room) is kept as poison: Black 2 stores no bad poison outside battle.
- The curtain is a fade with Black 2's door sound (no curtain effect or sound in Black 2).
- The place name is the island's ("Battle Tower").

## Testing aids (removed)
The tests used switches in the scripts and code (a test party in the lobby, a doorway that picks the room kind and one
that set the three to 1 HP, an Open Level jump to Lucy's room); they are gone from the files. Lucy's win was tested with
her three set to 1 HP from outside the game (work/agents/frontier_pike/tools/poke_hp.py, a RAM poke on a savestate).
Test tools: work/agents/frontier_pike/tools/ (build.sh, boot.py, drive.py, to_three.sh, to_lucy.sh, wild_exit.py,
sr_check.py: the no-build Sapphire/Ruby check).

## Open points
- BP: frontier_core's award (`fr_lobby_returned`) reads sBattlePointAwards[streak / 14] without Emerald's
  "challengeNum - 1", so the Pike pays one row too high (Lucy's first win: 12 BP, Emerald 11). frontier_core's code.
- ITCM: done (emerald_itcm, 2026-10-12): the movable part went to the Frontier code area (see "Code"). The old note:
  the Pike's code was 7.7 KB; about 1.4 KB of ITCM was left after it (its data, 49 KB, is already a ROM file).
  **Can it move out of ITCM?** Mostly, yes. Everything but the battle-line hook (PK_TrainerMsgExists / PK_TrainerMsgLoad,
  about 0.2 KB, called from ov167 during battle) runs while the field is loaded: the script command, room choice,
  trainer and party setup (the BtlSetup calls come from the field before the battle starts), the wild hooks. That part
  is self-contained (9 redirected calls, command 290, a few call-backs into arm9) and could live outside ITCM, but
  HoennB2 has no other code area yet. Two ways, both untried: (1) main RAM below the heap, by moving the main arena's
  start as the ITCM patches move the ITCM arena literal (0x0207B400), after measuring how much heap slack Black 2
  leaves; (2) load the code from a ROM file into a heap block when a Pike zone loads (it would have to be built
  position-independent, and the hooks would stay as small ITCM thunks). Either way the battle-line hook and the thunks
  (well under 0.5 KB) stay in ITCM, freeing about 7 KB.
