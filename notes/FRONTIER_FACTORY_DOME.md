# Battle Factory and Battle Dome (Emerald only; frontier_factory_dome, 2026-10-12)

Pokémon Emerald NDS's Battle Factory (rent three of six, swap one after each win, seven battles a round, Factory Head
Noland) and Battle Dome (16-trainer single-elimination tournament, pick two of three for each match, Dome Ace Tucker),
built on Black 2's Battle Subway battle, its battle-entry party screen and the PWT's bracket screen, with Emerald's
rules, data and text. Shared Frontier pieces (lobby flow, record keys, BP, Brains' art, songs) are frontier_core's:
notes/FRONTIER.md. Sapphire and Ruby get nothing from any of this (the patch returns "nothing (Emerald only)").

## In game (tested 2026-10-12, Emerald test builds in work/agents/frontier_factory_dome, muted DeSmuME)
Proof: screenshots/frontier_factory_dome/ (factory_*.png, dome_*.png, 256x192 or 256x384).

Factory (factory_00-24): the receptionist (Lv. 50 / Open Level, save), the walk into the rental room, the opponent
investigation lines (type, style), Black 2's battle-entry screen with six Lv. 50 rentals (exactly three must be
entered), the battle room (opponent walks in, Emerald greeting), the battle with the three rentals, the win ("restore
your Pokémon", "the 2nd match is next" GO ON / REST / RETIRE), the swap (your three -> give one; the beaten opponent's
three -> take one; the next battle's party shows the swap), REST = save and quit -> reset -> Continue -> "We've been
waiting for you" -> back in the rental room at "the 3rd match is next" with the same rentals, a loss (by fainting and by
forfeit) -> lobby ("Thank you for participating", rentals returned, results saved), free to walk, the results terminal
(Lv. 50: current streak 0, record 2).

Dome (dome_01-19): the receptionist, pick three, save (the tournament is drawn just before: dome_init), the corridor
walk, the waiting room menu (OPPONENT / TOURNEY TREE / READY TO START / REST / RETIRE), the opponent line (name and
Pokémon), the bracket (Black 2's PWT screen: your block, then the other block, with Emerald's 16 trainers), pick two of
three, the battle room (announcer lines by round and history, VERSUS, the opponent's greeting), a 2-vs-2 battle, the
win ("is the winner! Congratulations!"), back in the waiting room ("All 1st-round matches have been completed", the
bracket animating the round's results with winners and losers), round 2, a loss by forfeit ("Kathy is the winner!"),
the lobby ("Thank you for playing", saved), free to walk, the lobby's "last tournament" terminal (the bracket).

Second round of tests (2026-10-12, factory_d*/n*, dome_t*/d* screenshots):
- Double Battle mode, as Emerald: a second receptionist in each lobby (Battle Swap Double, Double Battle Tournament;
  Emerald's object 6) with Emerald's doubles lines and rules, her own door, the same rooms. Factory: three rentals in
  3-vs-3 Double Battles (target choice, the third Pokémon coming in). Dome: two of the three registered Pokémon in a
  2-vs-2 Double Battle ("one of the three must be held in reserve"). Separate doubles streaks, rental counts and
  results terminals; the challenge's mode decides where the player is put back in the lobby and who speaks.
- Retire: Factory (doubles, after a win: back to the lobby as a loss, record 1 on the doubles terminal) and Dome
  (doubles, after round 1). The lobby's "last tournament" terminal names a Double Battle tournament as such.
- Noland (Silver): "can't tell you anything about the Factory Head", his walk-in and Emerald lines, "Factory Head
  Noland" with his Emerald battle picture and his rental party, the Knowledge Symbol, then the round's end in the
  lobby ("defeating the Factory Head and winning seven matches in a row", 14 BP).
- Tucker (Silver): in the other block of the bracket, "For the final match, you will challenge the Dome Ace Tucker",
  his entrance and lines, "Dome Ace Tucker" with his Emerald battle picture and party (Salamence...), the Tactics
  Symbol, Level 50 champion, the lobby ("You defeated the Dome Ace", 13 BP).
  These used a test switch that set the streak just before each Brain (removed afterwards) and Lv. 5 opponents
  (HOENN_TEST_FD_WEAK). The Brain class names are frontier_core's (Factory Head, Dome Ace).
Fixed after these runs (compiled, not replayed): the bracket's "Your block" / "The other block" label was by left /
right half, so with the player in the right half it was swapped (dome_t01 shows the old label).
Not seen in game: Gold Symbol fights, Open Level, a 7-win round without the switch, the Factory "Head is coming"
call between battles.

## What differs from Emerald (and why)
- Screens are Black 2's: the rental, swap and pick-two screens are the Battle Institute's battle-entry party screen
  (no Emerald rental summary window); the Dome bracket is the PWT's 8-trainer screen, so Emerald's 16-trainer tree is
  shown as two halves ("Your block", "The other block") and Black 2's bracket comments ("That was a lopsided battle!")
  play over the results. The opponent's info card is two lines in the waiting room (name, then the three Pokémon).
  After the semifinal the half-bracket shows round 2's results again (the PWT screen has no slot for a third round).
- The Brains only take singles challenges (as Emerald: GetFrontierBrainStatus).
- Battles are Black 2's Battle Subway battles: no draws (the Dome's referee decision never happens), forfeit = loss
  (Emerald's frontier battles also offer it).
- New lines (not Emerald's): the bracket's block names, the Dome opponent's Pokémon line, the results terminal as one
  message.
- Rooms: Emerald's layouts (interior pipeline), Black 2 building art; the Dome crowd stands still (no cheering,
  confetti).
- Trainer battle pictures and names: each Emerald Frontier trainer gets the Black 2 class of its Emerald picture
  (data/hoenn_trainer_classes.json review); walking sprites are Emerald's own choice per facility class (battle_tower.c
  gTowerMale/FemaleTrainerGfxIds) through data/sprite_map.json.
- Noland and Tucker: frontier_core's Brain classes 33 / 7 (their Emerald battle pictures) and walking sprites 298 / 99;
  the class names, sex and battle music are still Black 2's (notes/FRONTIER.md 5: data/emerald/hoenn_trainer_classes.json).
- Emerald quirks kept on purpose: Dome opponents' IVs (CreateDomeOpponentMon's bug), CalcDomeMonStats (no EVs, u8
  truncation), DecideRoundWinners' points, the tournament's seeded draw, GetFactoryMonFixedIV, rental ranks.
- Music: the rooms play Emerald's Frontier songs automatically (hoenn_music.py zone songs from the pokeemerald map:
  mus_b_factory, mus_b_dome_lobby, mus_b_dome); the symbol fanfare is FR_ME_OBTAIN_SYMBOL. Not listened to (muted tests).

## How it works
- Data: converter/gen_frontier_emerald.py -> data/emerald/frontier.json (882 sets, 300 trainers, ranges, Factory
  tables, Tucker's sets, the Gen 3 type chart). b2tools/patches/frontier_factory_dome.py appends them to the Battle
  Subway set archive (arc 211 files 1000-1889) and stores the engine there too (file 1890).
- Engine: b2tools/patches/frontier_factory_dome.c, built position-independent (clang -fropi; the patch's own linker,
  PC-relative relocations only) and loaded into the game-event heap (heap 4) by a 345-byte loader in ITCM
  (frontier_fd_stub.c) on each script command. ITCM has no room for the whole engine (12 KB).
- Script command 505 `FrontierCmd sub, a, b, var` (src/field_scripts/scenes/frontier_fd_lib.inc): 0 random, 1 heap
  free; Factory 10 GEN_RENTALS, 11 RENT (screen), 12 GEN_OPPONENT, 13 OPP_TYPE, 14 OPP_STYLE, 15 SWAP (screens),
  16 KEEP_OPPONENT, 17 BRAIN_STATUS, 18 WON, 19 SET_SWAPPED, 20 INIT; Dome 30 INIT, 31 OPPONENT, 32 PICK2 (screen),
  33 TREE (bracket), 34 RESULT, 35 SET_PICKS, 36 WINNER, 37 OPP_NAME, 38 OPP_SPECIES, 39 HISTORY, 41 PREV_KIND;
  40 WORD_LINE;
  battle 50 PREP, 51 BATTLE, 52 RESULT, 53 END, 54 SPEECH, 55 NAME, 56 BRAIN_GOLD.
- Battle: Black 2's Battle Subway battle (BSubwayScrWork); the hook at ov012 0x02166082 builds the setup with the
  rentals / the two picks against the opponent's sets (Black 2's PWT rental engine: func_ov012_02162490 / 021621d4),
  as a Single or Double Battle by FR_BATTLE_MODE (SetupTrialHouseBattle mode 0 / 1: BtlSetup_SetTrainerTrialHouse).
- Bracket: ov320's PWT proc through EventFieldSubprocessTransition_Create (fade out, screen, field back), a WbtSetup
  filled from Emerald's tree (names, walking sprites, round results).
- State: frontier_core's record keys (FR_*; streaks per mode and level) plus keys 79-90 (notes/FRONTIER.md 6); the
  Dome tree is rebuilt from its seed (keys 88/89) and the facts stored at the draw (key 90: trainer range, mode,
  level, Tucker and his party), so the lobby's "last tournament" stays the same after the record changes.
- Text: b2tools/frontier_fd_text.py writes the seven rooms' texts (src/text/script/emerald/0637-0646_*) and
  src/include/frontier_fd_lines.h; the names (lines 100-399) and greetings (500-799) live in the Factory battle room's
  text (998).
- Rooms: work/agents/frontier_factory_dome/tools/rooms.py -> data/interior_layouts/BattleFrontier_Battle{Factory,Dome}*.json,
  data/interiors/emerald/408-411, 415-417.json; doors from the island (zone 17).

## Test switches (test builds only)
`HOENN_TEST_CHFD=1`: three Lv. 50 Pokémon in the Dome lobby when the party has fewer; the Factory lobby's fat man warps
to the Dome lobby. `HOENN_TEST_FD_WEAK=1`: Factory and Dome opponents at Lv. 5 (quick wins). (The Brain-test switch
used on 2026-10-12, "the streak just before each Brain", is removed.) Build:
work/agents/frontier_factory_dome/tools/build.sh with `HOENN_TEST_WARP=408,10,8` (Littleroot's sign -> Factory lobby).

## Claims
| What | Taken |
|---|---|
| Zones (data/emerald/hoenn_interiors.json, "claimed") | 408 Factory lobby, 409 Factory pre-battle (rental) room, 410 Factory battle room, 411 Dome lobby, 415 Dome corridor, 416 Dome pre-battle room, 417 Dome battle room |
| Room script / init / text file numbers | own_scripts 1962-1975 (two per room), own_text 996-1002 |
| Script command | 505 (Black 2's `Cmd_01F9`, unused by every script; args any, any, any, var) = `FrontierCmd sub, a, b, var` |
| Archives | arc 211 (Battle Subway sets) files 1000-1890 (sets, Tucker, facts, trainers, engine; Emerald builds only) |
| Code | ITCM loader after frontier_core's (345 B); ov012 0x02166082 hooked |
| Record keys | 79-90 (notes/FRONTIER.md 6) |

## Left to do
- The Dome crowd's animation, confetti, Emerald's rental summary window, Noland/Tucker in-battle lines.
- Not yet played: Gold Symbol fights, Open Level, the Factory Head's call between battles.
