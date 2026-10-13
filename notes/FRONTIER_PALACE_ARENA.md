# Battle Palace and Battle Arena (Emerald only; frontier_palace_arena, 2026-10-12)

Pokémon Emerald NDS's Battle Palace (your Pokémon choose their own moves by Nature; Single and Double Battle Halls,
Lv. 50 and Open Level; Palace Maven Spenser) and Battle Arena (1-vs-1, three turns, then the referee's judgment of
Mind, Skill and Body; no switching; Arena Tycoon Greta), built on Black 2's Battle Subway battle with Emerald's rules
added inside Black 2's battle engine. Shared Frontier pieces (lobby flow, record keys, BP, Brains' art, songs) are
frontier_core's (notes/FRONTIER.md); the Frontier trainers' sets and set lists are frontier_factory_dome's (arc 211
1000-1889). Sapphire and Ruby get nothing (the patch returns "nothing (Emerald only)"; every file is Emerald-only).

## How it plays (as Emerald)
- **Palace lobby** (zone 466, the island's door = zone 17 warp 4): two attendants (Single Battle Halls, Double Battle
  Halls; frontier_core's `fr_lobby_attendant`), three Pokémon on Black 2's pick screen, the save, the walk through the
  door. Back from a challenge (`fr_lobby_returned`): quit without saving, won (BP; +10 after Spenser), lost, resumed.
  The black belt, man, beauty and maniac; the two results boards and the rules board (five headings).
- **Palace corridor** (467): the garden walk; the attendant's comment (Emerald's palace_getcomment: one of three at
  random below a 50-win streak, then the streak lines), the Lv. 50 or Open Level hall's door.
- **Palace battle room** (468): the opponent walks in and greets (Emerald's easy-chat speech), the battle, "Let me
  restore your Pokémon", "prepared for the Nth opponent?" GO ON / REST / RETIRE. Spenser at Emerald's streaks
  (21st battle: silver; 42nd: gold; then every 21st) walks in with his Dusclops and Azurill; his speeches, the Spirits
  Symbol.
- **The Palace battle** (frontier_palace_arena.c): on FIGHT, the Pokémon picks its move itself (Emerald's
  ChooseMoveAndTargetInBattlePalace): a group by its Nature's weights (Attack / Defense / Support; the second set once
  it is at half HP or less and not asleep, kept until it switches out), then Black 2's trainer AI picks among that
  group's moves (Emerald's AI picks among selectedMoves); with no move of the group, a random usable move and half the
  time "X appears incapable of using its power!"; in Double Battles the target by Nature (the foe with more / less HP,
  or random). The opponents choose the same way. At the turn's start, a Pokémon at half HP or less shows its Nature's
  line once ("A glint appears in X's eyes!", "X is getting into position!", "X began growling deeply!", "X is eager
  for more!"). The player can still switch and forfeit (as Emerald's menu).
- **Arena lobby** (429, island door = zone 17 warp 3): the attendant, Lv. 50 (the left door) / Open Level (the right
  door); the woman, man, camper and youngster; results and rules boards (four headings).
- **Arena corridor** (431): the walk round the hall, "Please step in!".
- **Arena battle room** (433): the announcer calls both Trainers forward ("Set KO Tourney! Begin!"), the battle, "The
  winner is ...!" with the black belts jumping, "Your Pokémon will be restored to full health", GO ON / REST / RETIRE.
  Greta at Emerald's streaks (28th battle: silver; 56th: gold; then every 28th), her speeches, the Guts Symbol.
- **The Arena battle**: one Pokémon each at a time, in party order; "Referee: X VS Y! Commence battling!" when a
  matchup starts; the POKéMON command says "X can't be switched out!", the opponents never switch, a fainted Pokémon's
  replacement is the next in order (U-turn / Baton Pass too). After the third full turn of a matchup with both still
  standing: "That's it! We will now go to judging...", Mind (Emerald's sMindRatings per move used: attacks +1, Counter /
  Mirror Coat / Bide 0, Fake Out / Protect / Detect / Endure -1), Skill (each move's result: super effective +2, not
  very effective -1, no effect / missed / already statused -2, blocked by the target's Ability -3, else +1; no points
  when it could not act), Body (HP left in percent of the HP at the matchup's start); each category 2 points to the
  better, 1 each when even; the higher total wins, the loser faints (both on a draw).

## What differs from Emerald
- Black 2's Battle Subway battle and screens (as the Factory/Dome): the trainer intro, music, battle backgrounds.
- The Palace's message about Nature appears when the turn's actions start (Emerald: before the menu). Emerald's
  move choice among the group uses Emerald's AI; here Black 2's own trainer AI (a VM for the player's side is made the
  first time the Palace chooses for it).
- The Arena's judgment is told in battle messages, one line per category ("Referee: X takes this one!" / "It's even!",
  NEW lines) instead of Emerald's window with circle / triangle / cross marks; the loser shows the referee's line and
  faints (no "fainted!" line). The Skill score reads Black 2's battle messages for each move's result; Emerald's
  ability-blocked list is approximated by "another Pokémon's Ability window and no damage" (-3).
- Black 2's Bag can be opened in battle (as every Frontier facility here); Emerald's "record the battle" option is not
  offered (Black 2 has no Frontier battle videos).
- The rooms are built from Emerald's layouts with Black 2 textures; the player walks in where Emerald uses a stand-in
  object (the camera follows); the announcer's drum and the crowd's sounds are left out.

## How it works
- Engine: b2tools/patches/frontier_palace_arena.c, linked into the **Frontier code area** (main RAM 0x023D0000,
  b2tools/patches/frontier_area.py; notes/FRONTIER.md 7). Field: script command 291 `FrontierPA var, sub, a, b`
  (src/field_scripts/scenes/frontier_pa_lib.inc). Battle: 13 `bl` calls, 3 words and 2 detours in ov167
  (frontier_palace_arena.py HOOKS): the player's FIGHT proc, the AI's move flags / target / switch checks / replacement
  order, the turn's start and end, the obedience check, the move-fail message, the fight action, the move precheck,
  the root menu's POKéMON command and its message, the replacement procs, the battle's std strings, and two detours
  in the server's message and command put functions (the Arena's Skill spy). Each does Black 2's own thing outside a
  Palace/Arena battle (the rule is set only while our battle event runs).
- Battle setup: SetupTrialHouseBattle (Black 2's Subway setup) with our trainer record, then the player's three as
  they are (no Lv. 50 scaling) and the opponent's party: Emerald's FillTrainerParty (three sets of the trainer's list,
  no species / held item twice, high-tier sets only at Open Level, fixed IVs by trainer, EVs 510 / n, the set's
  Nature) at Lv. 50 or the three's highest (at least 60); the Brains' fixed parties (frontier_util.c
  sFrontierBrainsMons). Opponents: GetRandomScaledFrontierTrainerId, never twice in a challenge (record keys 11-14).
- Texts: b2tools/frontier_pa_text.py -> src/text/script/emerald/0192-0194, 0174, 0176, 0178 (+ the names 100-399,
  greetings 500-799 and the battle lines 820+ in both battle rooms' files), src/include/frontier_pa_lines.h. Battle
  lines are std messages with ids 0x4000 | line (the Palace battle room's file) or 0x6000 | line (the Arena's).
- Rooms: work/agents/frontier_palace_arena/tools/rooms.py -> data/interior_layouts/BattleFrontier_Battle{Palace,Arena}*.json,
  _styles_frontier_pa.json, data/interiors/emerald/{466,467,468,429,431,433}.json.

## Tested (2026-10-12, Emerald test build in work/agents/frontier_palace_arena, muted; screenshots/frontier_palace_arena/)
- Rooms: both lobbies, corridors and battle rooms (rooms_*.png, palace_corridor, *_room_greeting); attendant flow, pick
  screen, save, door, corridor, the opponent's greeting.
- Palace (one Lv. 50 singles battle, the opponents' HP set to 1 in RAM to keep it short): no move list; the engine's
  choice log (a test-only RAM log, since removed) showed each pick inside its Nature's group: Shuckle (Naive) attack
  group -> Bug Bite, support group -> Power Split (palace_support_by_nature); Poliwag (Relaxed, low HP) attack group ->
  Water Gun; Cubone (Hardy, low HP) support group with no support move -> "appears incapable of using its power!"
  (palace_incapable), the next time a random move (Aerial Ace). Won -> "Let me restore your Pokémon" (palace_win_restore).
- Arena (one challenge): "X VS Y! Commence battling!" per matchup; the POKéMON command says "can't be switched out!";
  a 3-turn judgment lost 0 to 6 (Blissey vs Poliwhirl; the loser faints, the next comes in by party order); a
  confused turn scores no Skill; a KO in turn 2 (no judgment, new matchup); the player's last Pokémon fainting ->
  "The winner is <opponent>!" -> the lobby ("Thank you so much for participating!", the save). A judged WIN (4 to 2) was
  seen on the build before the side fix below (arena_judged_win_prefix*.png); after the fix only the loss was replayed.
- Fixed during the test: the side of a Pokémon is Black 2's (monId >= 12 is the foe's; the first draft used monId / 6,
  which scored both sides as the player's).
- Not tested (time): Brains (Spenser, Greta), Double Battle Halls, Open Level, the Palace's low-HP Nature lines,
  resume after a soft reset mid-challenge, a Palace loss (the Arena's loss path is the same lobby flow).

## Test switches
Removed after the test (HOENN_TEST_CHPA party givers / warps / Brain streak, HOENN_TEST_PA log and streak command,
HOENN_TEST_PA_LEVEL). Nothing test-only is left in the scripts, the engine or the patch.

## Claims
notes/FRONTIER.md section 6 (zones, own script/text numbers, record keys 9 and 11-14, command 291, the code area).
