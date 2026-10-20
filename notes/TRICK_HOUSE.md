# The Trick House (trick_house helper, 2026-10-19)

User request: "build the Trick House for all three versions, faithful per version". Sapphire/Ruby follow pokeruby
(`external/pokeruby/data/maps/Route110_TrickHouse*`), Emerald follows pokeemerald (same map names). Ruby = Sapphire
(pokeruby has no Ruby branch here except the Puzzle 8 tent: Sapphire's Blue Tent, Ruby's Red Tent).

## 1. What the originals do
- **Entrance** (zone 514): the Trick Master (OBJ_EVENT_GFX_MAN_1, local id 1) hides, invisible, at a different spot
  for each puzzle level (VAR_TRICK_HOUSE_ROOMS_COMPLETED 0-7: under the desk (6,3), behind the tree (11,5), in the dresser
  (9,1), beyond the window (3,1), in the planter (0,5), in the cupboard (11,1), behind the window (8,1), under the cushion
  (4,4)). Stepping in (4,7)/(5,6)/(6,6)/(7,7) says "You're being watched..." (levels 0-2 also sparkle at his spot).
  Talking to his spot: "!" over the player, "Hah? Grrr... How did you know I concealed myself beneath this desk?",
  a warp to (6,2), and on arrival his intro (level 0: "Behold! ... The TRICK MASTER!"), "You've come to challenge my
  TRICK HOUSE ...", spin, explosion sound, he jumps away. The scroll (5,1): "There is a big hole behind the scroll!
  Want to go in?" -> the current puzzle room at (0,21).
- **Badge gates** (CheckReadyForNextPuzzle, both versions): puzzle 1 any time, 2 = Dynamo Badge (3), 3 = Heat (4),
  4 = Balance (5), 5 = Feather (6), 6 = Mind (7), 7 = Rain (8), 8 = game cleared. Not ready -> the Trick Master stands
  at the scroll ("For the next time, I'll use this trick..." / "I'm in the midst of devising new tricky challenges!").
- **Puzzle rooms** (15x22): a scroll with the secret code (fanfare "found a scroll", "memorized the code"), a locked
  door (13,1) ("write the secret code here" -> "the lock opened"), the exit mats back to the entrance's scroll.
- **End room** (zone 513): "Aak! You've made it to me?", the level's line, the prize, "I'll make new tricks to stump
  you", spin + jump away, VAR_TRICK_HOUSE_ROOMS_COMPLETED + 1. Leaving him without talking: "You're ignoring me now?".
  A full Bag keeps the prize with him (VAR_TRICK_HOUSE_PRIZE_PICKUP: given at the entrance next time).
  Prizes 1-7: Rare Candy, Timer Ball, Hard Stone, Smoke Ball, TM12 Taunt, Magnet, PP Max (same in Emerald).
  After puzzle 8: "My fountain of ideas for tricks has run dry", a tent (Sapphire Blue, Ruby Red; Emerald asks
  "Which do you prefer?" Red/Blue), "I am leaving on a journey", the hidden Nugget under him (4,5) becomes findable;
  the scroll then reads "I am leaving on a journey. Don't look for me. TRICK MASTER". If the PC was full, Mechadoll 5
  waits at the scroll with the tent.
- **The corridor** (512) sets VAR_TRICK_HOUSE_STATE 1: back in the entrance the Trick Master is gone until the next
  visit from Route 110.

| # | Sapphire/Ruby puzzle | Emerald puzzle (all 8 maps differ) | Trainers (S/R; Emerald) |
|---|---|---|---|
| 1 | Cut trees maze | Cut trees, other maze | Sally, Eddie, Robin |
| 2 | 4 floor buttons, each opens one door (VAR_TEMP) | same, other maze | Ted, Paul, Georgia |
| 3 | 7 buttons (4 under Rock Smash rocks) toggle all red/blue doors | 4 buttons, same doors, no rocks on buttons | Justin, Martha, Alan |
| 4 | Strength boulders | Strength boulders, other maze | Cora, Yuji, Jill; Emerald Paula (= Jill's id) |
| 5 | 5 Mechadolls' quiz (wrong answer: pushed back) | 5 Mechadolls, other questions/positions | none |
| 6 | 14 rotating gates | rotating gates, other layout | Sophia, Benny, Sebastian |
| 7 | arrow slide tiles, 5 levers, a warp pad | Mossdeep-style rotating tiles (colour buttons), statues | Joshua, Alexis, Patricia; Emerald + Alvaro, Mariela, Everett |
| 8 | slippery floor (ice) between rocks | slippery floor, other layout | Vincent, Elaine, Leroy; Emerald Keira (= Elaine's id) |

## 2. How each part is built in Black 2
- **Ids**: Sapphire's own vars/flags already have ids (src/include/hoenn.h Ch3 block: VAR_TRICK_HOUSE_* 0x407C-0x408C,
  FLAG_HIDE_TRICKMASTER_ENTRANCE 375, FLAG_HIDE_TRICK_HOUSE_END_MAN 376, FLAG_LANDMARK_TRICK_HOUSE 386,
  FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_1-5 421-425). Gen 3's VAR_TEMP_* = Black 2's map-local works 0x4000-0x401F and
  flags 0-0x5F (cleared at every zone init, kept through battles and menus: ov012 FieldScript_CallOnZoneInit).
  New saved ids come from **Ch3's reserve** (the Trick House is Ch3's optional block 3T): flags 433-440, works
  0x408E-0x4093 (`gen_story_ids.py --claim Ch3 ...`). No new id group.
- **Zones** (fixed now, all of them, so later rounds don't need the lead): P2 432, P3 434 (+ 451 = P3's other door
  state), P4 438, P5 441, P6 442, P7 447, P8 449 (free in both worlds; allocate_interiors.py pool order). P1 keeps 552.
  Emerald installs its own maze recipe in the same zone (data/versions.json room_variants, `*_Emerald` recipes).
- **Trick Master** (story objects, data/story/trick_house.json; Emerald data/story/emerald/trick_house.json):
  model 61 (MAN_1's Black 2 look), entrance uid 1 = NPC index 0 of zone 514, end room uid 1 = index 0 of 513.
  Hidden = present but invisible (movement 69 set_invisible from a scene condition, the invisible Kecleons' way,
  scenes/ch7_lib.inc), placed per level with ObjInitNPCGPos in the zone init (setobjectxyperm). "Found" warp = a
  scripted warp to the entrance itself (h_warp_arrive), the intro runs from a scene condition. Sparkle (no Black 2
  field effect): the "..." balloon over his spot + a sound.
- **Scroll entrance**: sign (5,1) read facing north; YES walks the player into the scroll, hides them and warps to the
  puzzle zone at (0,21). A puzzle that is not built yet counts as "not ready" (the Trick Master keeps devising), so
  every build is playable to its last built puzzle.
- **Puzzle door** (13,1): a sign read facing north; its warp (Sapphire warp 2) is moved off the map in the zone init
  until VAR_TRICK_HOUSE_PUZZLE_n_STATE is 2 (ObjInitWarpGPos), and moved back when the lock opens.
- **End room**: arrival door (10,1) is arrival-only (it "closes" in Gen 3). The hidden Nugget's flag (2858) is set
  on every entry while the Trick Master is there (SetTrickHouseEndRoomFlag) and cleared after puzzle 8.
- **Tents**: Black 2 has no decorations (DECISIONS 2026-10-06 / Sootopolis' Wailmer Doll): his lines play, no item.
- **Trainers**: eye-contact trainer NPCs (global script 3000 + id, evtype 1, Sapphire's sight), parties already in
  data/hoenn_trainer_data.json on the level curve.
- **Mechanics per puzzle**
  - P1: Cut trees = Black 2 cut-tree objects (code 108, script 10004).
  - P2: each hole = a flat object (src/objects3d/008e-trick-hole: Gen 3's hole metatile on a quad, code 142, solid)
    lying over the closed-lid floor art, spawn flag = a map-local flag (back on every entry, as Gen 3); each button =
    a step trigger (map-local work 0x4001-0x4004 = VAR_TEMP_1-4) that hides its hole.
  - P3: the room exists twice (blue open / red closed and the reverse) in zones 434 and 451; a button press fades and
    swaps zone at the player's tile (the Mauville Gym's barriers, without a map-replace event: all ten are taken).
    State that must survive the swap (which colour, rocks smashed) lives in Ch3-reserve saved works, reset when you
    come in from the entrance.
  - P4: Strength boulders = code 0x2004 (Hoenn's 1x1 boulder), script 10000.
  - P5: Mechadolls = people (model 61, as Gen 3 draws them like the Trick Master), triggers in front of each, Black 2
    multichoice lists; a wrong answer walks the player back.
  - P6: rotating gates (Fortree's were never built: notes/STORY_HANDOFFS.md Ch7). Plan: each gate arm = a 1x1 object;
    walking onto an arm's approach tile (step trigger) checks the sweep (Gen 3 rotating_gate.c tables) and turns the
    gate (arm objects moved with ActorSetGPos) or walks the player back.
  - P7 S/R: arrow slide tiles (Black 2 has no conveyor class): step triggers that move the player along the arrows;
    levers = signs that move the switched arrows' triggers (ObjInitTrigger is not a command: alternate zones as P3,
    5 levers = too many states) -> needs its own design (section 4).
  - P7 Emerald: the Mossdeep Gym's rotating-tile puzzle (b2tools/emerald_gyms.py mossdeep) on this map.
  - P8: Black 2's sliding ice (collision class 0x18, flags 0x80; Shoal Cave's ice room) on Gen 3's slippery tiles.

## 3. Test plan
One test ROM per version (`HOENN_AGENT=trick_house zsh b2tools/story_build.sh`, sign kit HOENN_TEST_CHTH: a stage
sentinel picks the level and badges, then the town sign warps to the entrance). Per built puzzle: find the Trick
Master, enter via the scroll, solve, fight its trainers, read the scroll, open the door, end room, prize, leave via the
corridor, check the entrance has moved on (Trick Master hidden at the next spot / "still devising" without the badge).
Checkers on each build: script_check, npc_check, rooms_check, caves_check. Proofs: screenshots/trick_house/.

## 4. Status (2026-10-19)
Generator: `python3 b2tools/trick_house.py [--check]` writes every Trick House script, text, recipe, zone json, story
object list and the test kit. `BUILT` in it says how many puzzles a build offers (the rest: "still devising").

| Part | S/R | Emerald | Tested |
|---|---|---|---|
| Entrance: hiding spots, watched trigger, found + intro, scroll hole, badge gates, prize pickup | built | built | S, E, R |
| End room: prizes 1-7, puzzle 8 farewell + tent lines (Emerald Red/Blue menu), Nugget, door shuts behind you | built | built | S, E (prizes 1-5, farewell) |
| Corridor (VAR_TRICK_HOUSE_STATE 1, the Trick Master gone until you come back from Route 110) | built | built | S, E, R |
| P1 Cut trees (zone 552) | built | built | S, E, R |
| P2 buttons + holes (zone 432) | built | built | S, E |
| P3 red/blue doors, rocks (zones 434 + 451) | built | built | S, E |
| P4 Strength boulders (zone 438) | built | built | S, E |
| P5 Mechadoll quiz (zone 441) | built | built | S, E, R |
| P6 rotating gates (zone 442): field code b2tools/patches/rotating_gates.c, arms = 3D actors (section 6) | built | built | S, E |
| P7 arrows + 5 levers + warp pad (zone 447; Emerald: Mossdeep Gym's rotating tiles, buttons, 10 pads), section 7 | built | built | S, E |
| P8 slippery floor (zone 449): Black 2 ice cells (recipe key "ice", class 0x18) | built | built | S, E |

Tests: work/agents/trick_house/tools/th_test.py (one run per puzzle and version: sign kit -> find him -> scroll ->
solve -> scroll -> door -> end room prize -> door stays shut -> corridor -> re-enter), proofs in
screenshots/trick_house/ (s* Sapphire, e* Emerald, r* Ruby). Every run passed.

`P8_READY` in the generator: puzzle 8 is built before 6 and 7, so normal play still stops after 5 ("still
devising"); the test kit's stage 0x7B79 (7 done, game cleared) reaches it.

Ids used (all from Ch3's reserve): VAR_TRICK_HOUSE_PUZZLE_3_DOORS 0x408E, VAR_TRICK_HOUSE_PUZZLE_3_BUTTON 0x408F,
FLAG_TRICK_HOUSE_PUZZLE_3_ROCK_1-4 433-436; 3D object record 142 (the hole). Left in the reserve: flags 437-440,
works 0x4090-0x4093.

Known gaps: the sparkle at his spot is a "..." balloon; SE_PIN/SE_SUCCESS/SE_FAILURE/explosion are guessed Black 2
sounds; P2/P3 pressed-button art is not drawn (the buttons keep their up picture); Rock Smash rocks in P3 come back
after a battle in the room (Black 2's global rock script 10016 has no flag; the saved rock flags only cover rocks on
buttons); rooms_check (e) on P2-P5 ("exit leads to the entrance, not back here") is Gen 3's design.

### Split plan for P6-P7 (each needs field code or a big new mechanic)
- **P6 rotating gates** (S/R 14 gates, Emerald its own layout; Fortree's gates need the same thing): a field-code hook
  "walking into an actor runs its script" (Black 2 only runs scripts on A), then each gate = 1-4 arm objects
  (ActorSetGPos to turn) with Gen 3's rotating_gate.c sweep tables decided in script. One code patch, then both
  Fortree and P6 are data. Trainers Sophia, Benny, Sebastian are ready in the trainer data. (A no-code fallback:
  arms as objects without collision, a step trigger on every tile an arm can take; stepping on an arm turns the gate
  or walks you back. It shows a step-and-back where Gen 3 just bumps.)
- **P7 S/R** arrow slides + 5 levers + warp pad: precomputed slide paths (one script per arrow trigger per lever
  state: the lever states live in FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_1-5, triggers check them), arrows drawn as floor
  objects that turn with the levers. **P7 Emerald**: reuse b2tools/emerald_gyms.py mossdeep (rotating tiles) on this
  map. Trainers ready.
  (pokeemerald's comment: "Puzzle Room 7 in RSE uses whatever puzzle Mossdeep Gym uses": warp pads MB 0x0E.)
Zones 442/447 and text/script numbers for P6-P7 are already registered (data/hoenn_interiors.json); once both are
built, set BUILT to 8 (P8_READY can go).

<!-- th_p6 coord -->
## 5. Coordination (th_p6 / th_p7, 2026-10-19 night)
- th_p6 (Puzzle 6) claims: object records **119, 135** (empty people records: no Black 2 zone NPC, ActorNew or
  WKOBJCODE work uses them) for the gate arm models; a new code patch `rotating_gates` (b2tools/patches/rotating_gates.py/.c: ITCM,
  hooks ov036 0x0219bc30/0x0219c034 `bl PlayerMoveCollCheck` and the 3D draw table entry 0x021cf9a4); P6's own
  map-local works 0x4000-0x400D (gate turns); story uids 100-155 in zone 442. Ch3 reserve: flags 437-438, works
  0x4090-0x4091 (only if needed). Generator edits: P6 sections only (puzzle6*, PUZZLE_SCRIPTS[6], main()'s P6 block,
  story_objects' P6 line), plus BUILT when done (now 6). Release patch: work/agents/th_p6/tools/mkpatch6.py rebuilds
  the generator's sections from HEAD + th_glitch's th_edits.py + th_p6's edits (p6_edits.py) and keeps every other
  section; th_glitch's mkpatch.py rewrites trick_house.py/notes/rooms_check.py from HEAD + its own edits only, so run
  th_p6's after it (or add th_p6's edits there). Final patch: th_p7's mkpatch7.py (it replays th_glitch's, th_p6's and
  th_p7's edits; run it LAST, not mkpatch6.py, which leaves P7 out of the shared sections).
<!-- /th_p6 coord -->
<!-- th_p7 coord -->
- th_p7 (Puzzle 7) claims: object records **145, 146, 202, 203** (empty people records, checked the same way:
  no Black 2 zone NPC, ActorNew or WKOBJCODE work; 185 is NOT free: zones 301-303/445 use it; 135 is th_p6's) for the
  turned red arrows (src/objects3d/0091, 0092, 00ca, 00cb); P7's map-local flags 0x20-0x24 and works 0x4011-0x4014 (Emerald's
  colour press counts); story uids in zone 447 as Sapphire's/Emerald's local ids + 21-25 (the switch objects). Ch3
  reserve flags 439-440 / works 0x4092-0x4093: not used. Generator edits: P7 sections only (puzzle7*,
  PUZZLE_SCRIPTS[7], main()'s P7 block, story_objects' P7 line, P7_READY + the entrance's puzzle-7 gate).
<!-- /th_p7 coord -->
<!-- th_check67 coord -->
- th_check67 (P6/P7 glitch check, 2026-10-20) -> **fortree_gates**: one edit in b2tools/patches/rotating_gates.py,
  `arm_model` only (the rail box and its docstring numbers): the rail 3 -> 4 units wide and 9 -> 10 high, so its faces
  stay 2 units off a wall block it lies along (P6's plank boxes are 8 high; 1-1.5 units flickers in melonDS,
  notes/INTERIORS.md "Flicker"). Nothing else in rotating_gates.py/.c is touched; please keep these two numbers
  when you rewrite the file. Regenerated arm models: src/objects3d/0077-gate-arm-short, 0087-gate-arm-long
  (`python3 b2tools/trick_house.py`).
<!-- /th_check67 coord -->
<!-- fortree_gates coord -->
- fortree_gates (2026-10-20) -> th_check67 / th_glitch2: rotating_gates.py/.c edited in place (th_check67's arm_model numbers
  kept): `PUZZLES` + `sPuzzles` (zone 442 first, then Fortree 119), ZoneGates() in both hooks, story_objects()/write_story()
  for data/story/fortree_gates.json (+ emerald/). P6 unchanged (works, uids, codes, hooks); P6 regression passed on the
  fortree_gates ROMs. fortree_gates.patch leaves th_check67's arm_model hunk out (that one is th_check67's to ship).
<!-- /fortree_gates coord -->
- th_glitch (new-area check of P1-P5, P8 and the shared rooms) edits: `puzzle_recipe` (Gen 3's ledges: MB_JUMP_* tiles
  get "ledges" + low ledge blocks with Gen 3's art; only P4 has them), `puzzle5_recipe` (floor_extra strip so the back
  wall is whole over the void; "open_no_strip"), plus b2tools/models_interior.py (new opt-in recipe key
  `open_no_strip`, no other room changes), caves_check.py (Gen 3's 0x48 slippery floor slides as MB_ICE),
  rooms_check.py ACCEPT (the puzzle rooms' Gen 3 warp graph, `Route110_TrickHousePuzzle[2-8]`: covers P6/P7 too).
  Running `python3 b2tools/trick_house.py` writes everyone's outputs from the current generator (it wrote P6's WIP
  files once at 23:15). Release patch: section 6 below.

<!-- th_p6 p6 -->
## 6. Puzzle 6: the rotating gates (th_p6, 2026-10-19)
Built for all three versions (S/R: pokeruby's 14 gates, Emerald: pokeemerald's 11). th_p6 set `BUILT` = 6 (puzzle 6
after the Mind Badge); th_p7 then set 8 once P7 was in.
- **How it works**: a port of rotating_gate.c in field code (option (a) of the split plan, but at the move check, not as
  "walking into an actor runs its script": Gen 3's arms lie on tile *edges*, which no Black 2 actor or collision tile
  can be). New patch `rotating_gates` (b2tools/patches/rotating_gates.py + .c, last in the patch lists of
  rebuild_slice.sh and story_build.sh; 1.2 KB of ITCM after new_tms, S/R 13.6 KB left, Emerald ~4.9 KB):
  - ov036 `bl PlayerMoveCollCheck` in FieldPlayerGrid_DecideCommandNormalMoving (0x0219bc30, walk/run) and the bike's
    (0x0219c034) -> Gate_MoveCollCheck: Black 2's check, then (nothing in the way) CheckForRotatingGatePuzzleCollision:
    the step's destination tile in a gate's 4x4 square + the direction -> the arm crossed (RotationInfo tables); the
    gate turns if no map collision is where its arms sweep (ArmPositions; Gen 3 checks the map only) and you walk
    through, else the result is 4 and you bump. Surf/forced moves/catwalks keep Black 2's check.
  - ov036's 3D draw processor table entry 1 (0x021cf9a4, func_ov036_021974b4) -> Gate_Update3D: Black 2's update,
    then for an arm actor its turn (MAT3_RotationEulerZYX on the G3D object's rotation), the model origin moved onto
    the pivot (the NW corner of the gate's tile), an 8-frame quarter-turn animation and actor flag 0x80 (no actor
    collision). Other 3D actors unchanged.
  - Tables (rotation info, arm sweep, arm layout, the gates) are read from the decomps at build time
    (rotating_gates.py header(); pokeruby's and pokeemerald's tables are asserted equal); zone 442 only.
  - State: map-local works 0x4000 + gate = quarter turns since the zone init (Black 2 clears them at every zone init =
    Gen 3's OnTransition RotatingGate_InitPuzzle; battles and menus keep them).
- **Arms**: one 3D actor per arm (story objects, uid 100 + 4 * gate + shape arm N/E/S/W, S/R 36, Emerald 26) standing on a
  walkable tile next to the pivot; object codes **119** (short arm, 1 tile) and **135** (long arm, 2 tiles), empty
  people records (FREE_PEOPLE_RECORDS; models from rotating_gates.arm_model: a low olive rail with Gen 3's colours and a
  black pivot post, src/objects3d/0077-gate-arm-short, 0087-gate-arm-long). npc_check: zone 442 40 actors, ok.
- **Room**: puzzle 1's rules (recipe Route110_TrickHousePuzzle6[_Emerald]), scroll/door/zone init as P4 (simple_puzzle),
  trainers Sophia, Benny, Sebastian (eye contact), the Glitter Mail ball (Black 2's Reply Mail, as data/hoenn_items).
- **Ids**: no saved ids (Ch3 reserve flags 437-440 / works 0x4090-0x4093 untouched by th_p6); map-local works
  0x4000-0x400D of zone 442; object records 119, 135.
- **Tested** (work/agents/th_p6/tools/th6_test.py: a Python twin of the C logic plans the route over (tile, gate
  turns) and every step is checked against the game's tile and works): Sapphire: sign kit -> find him -> scroll ->
  bump into a gate that cannot turn (stays, gate unchanged) -> 35 gate turns exactly as predicted -> all 3 trainers ->
  scroll -> door -> end room (Magnet, "It took me all night to install the doors") -> corridor -> "still devising".
  Emerald: see the results line below. Screenshots screenshots/trick_house/p6_s_* / p6_e_* (p6_*_orient0-3: one
  L gate turned through its 4 orientations: clockwise on screen).
- **Checkers**: script_check (ent "people on one tile": the arms; ACCEPT added), rooms_check (k: same; ACCEPT added),
  npc_check ok, caves_check unchanged.
- Gaps: SE_ROTATING_GATE is a guess (SEQ_SE_FLD_03 0x674, Black 2's Strength boulder push: user listening check); Gen 3
  plays a faster turn when you run (here always 8 frames).

### Fortree Gym with the same code (fortree_gates, 2026-10-20: done)
Fortree's gates are the same rotating_gate.c with sRotatingGate_FortreePuzzleConfig: S/R pokeruby's 7 (incl. a T4), Emerald
pokeemerald's 8.
- rotating_gates.py `PUZZLES` = Gen 3's GetCurrentMapRotatingGatePuzzleType: (TrickHouse, zone 442), (Fortree, zone 119),
  both rooms origin (1, 1). The header has `sPuzzles[] = {zone, first gate, count}` and one `sGates` table (P6's gates
  first, so P6 is unchanged); both hooks find the player's zone's gates (ZoneGates). A zone's gates are numbered from 0:
  works 0x4000 + gate and arm uids 100 + 4 * gate + arm, as before. 1320 B of ITCM (+96 B).
- Arm actors: data/story/fortree_gates.json (S/R: 18 arms) and data/story/emerald/fortree_gates.json (Emerald: 23),
  written by `python3 b2tools/patches/rotating_gates.py story` (`... check` = are they current); placed as
  trick_house.puzzle6_objects (first walkable tile of the four round the pivot). No arm is on a person's tile or in a
  trainer's sight line. npc_check zone 119: S/R 24 actors, 9/32 materials, ok.
- Room: nothing to change. The recipes already make every Gen 3 solid tile a post and leave the rest open; walk_diff
  INVISIBLE/THROUGH 0 for both rooms, and the test checks every gate's 4x4 square against Gen 3 tile by tile.
- Reset on entering: map-local works are cleared on every map change (= RotatingGate_InitPuzzle); battles keep them.
- Checkers: script_check `ent` "people on one tile" and rooms_check (k) for FortreeCity_Gym(_Emerald): ACCEPT entries as P6's.
- Tested (work/agents/fortree_gates/tools/fg_test.py: th6_test's Python twin of rotating_gate.c, CanRotate on Gen 3's
  own map collision; every step's tile and every gate's orientation checked against the game; sign kit HOENN_TEST_CHTH
  + test warp into the Gym): Sapphire 18/18 (168 steps, 18 turns, 1 bump, all 4 trainers, Winona: badge + TM40),
  Emerald 20/20 (132 steps, 19 turns, 1 bump, all 6 trainers, Winona); both: all arms present and out of the actor
  collision, every gate's 4x4 square = Gen 3, works 0 on arrival, left with a gate turned -> Fortree City -> back in:
  every gate back at its start. P6 regression on the same ROMs (test warp patched to zone 442): S bump + 10 turns,
  E bump + 6 turns, all as predicted. Ruby: data only (shared fortree_gates.json = pokeruby, same table as Sapphire).
  Screenshots: screenshots/fortree_gates/ (s_* / e_*: arrival, bump, a turn before/after, reset, Winona, badge).
<!-- /th_p6 p6 -->

<!-- th_p7 p7 -->
## 7. Puzzle 7: arrows, levers, the warp pad / Emerald's rotating tiles (th_p7, 2026-10-19)
Built for all three versions (Ruby = Sapphire: pokeruby has one puzzle 7). Generator: the "puzzle 7" section of
b2tools/trick_house.py (P7Map, puzzle7_rs/_em, puzzle7_objects, puzzle7_recipe, p7_switch_models).
- **Sapphire/Ruby** (pokeruby Route110_TrickHousePuzzle7): Gen 3 moves you on by itself on an arrow (field_player_avatar.c
  ForcedMovement_*): red arrows (MB_WALK_*) walk you on, blue ones (MB_SLIDE_*) slide you facing as you were, the two
  crossings (0x48) slip you on, until the next tile is blocked; a raised track (elevation 4, rows 6-7) crosses the room.
  Black 2 has no arrow cells, so: P7Map simulates Gen 3 (collision incl. elevation, people, forced movement, levers,
  pad) from pokeruby's map; every arrow you can walk onto (75) is a step trigger whose script moves you along Gen 3's
  slide (lock_facing + walk_fast for blue, walk for red), branching on FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_k only where the
  slide meets lever k's arrow (81 distinct slides). The raised track is solid (block): Gen 3 bumps you at its edge
  (elevation); the scripted slides cross it. 5 levers = signs (Switch1-5: delay, click, flag toggled); the turned red
  arrow is a flat 3D object shown while the lever is on (map-local flags 0x20-0x24 hide them; the zone init clears
  the 5 flags, as OnTransition): only 4 empty object records were left (145, 146, 202, 203), so the arrows you can
  walk onto (levers 1, 4, 5) are drawn by an object standing on its lever with the arrow off to the side, levers 2-3's
  (only crossed by slides) by one shared model on the arrow. The warp pad (9,2) -> (3,19): fade + ActorSetGPos (the
  zone stays, so the levers stay, as VAR_..._7_STATE_2). Checked: every reachable state can walk back to the exit;
  no slide ends in a trainer's sight; no reachable tile is on the raised track.
- **Emerald** (pokeemerald): Mossdeep Gym's rotating-tile puzzle (initrotatingtilepuzzle TRUE), as
  b2tools/emerald_gyms.py mossdeep: 4 colour buttons (step triggers; Red is unused, as pokeemerald) move every trainer
  (Joshua, Patricia: yellow; Alexis: purple) and statue (blue, green: Black 2's rock 206) on that colour's 2x2 arrow
  square one tile round it and turn it a quarter counter-clockwise; press counts in map-local works 0x4011-0x4014
  (0 on entering: Emerald resets the objects); 10 warp pads (MB_MOSSDEEP_GYM_WARP) = step triggers moving the player
  to the partner pad (the objects stay). Trainers Alvaro, Mariela, Everett stand.
- **Ids**: no saved ids (Ch3 reserve flags 439-440 / works 0x4092-0x4093 untouched); object records 145, 146, 202,
  203 (src/objects3d/0091-trick-arrow-262, 0092-trick-arrow-262-lever1, 00ca-trick-arrow-27c-lever4,
  00cb-trick-arrow-261-lever5); map-local flags 0x20-0x24, works 0x4011-0x4014 of zone 447.
- **Tested** (work/agents/th_p7/tools/p7_test.py: plans with the Gen 3 model and checks every step lands where Gen 3
  puts you): Sapphire 29/29: sign kit -> find him -> scroll -> every lever on (its arrow object shown) and a slide over
  each turned arrow -> the warp pad (5x) -> Joshua, Alexis, Patricia (battles) -> scroll -> door -> end room (PP Max,
  "It took me all night setting up arrows") -> corridor -> "still devising". Emerald 58/58: every colour button (40
  presses: after each one every trainer and statue stood where Emerald's rotating_tile_puzzle.c puts it), warp pads
  (18 uses), all six trainers (battles), scroll, door, PP Max, corridor. Screenshots screenshots/trick_house/p7_s_*
  (levers on, the turned arrows, the pad) / p7_e_* (buttons, pad, trainers).
- **BUILT = 8** (th_p7, once P6 and P7 were both tested): normal play runs puzzles 1-8 (P7 after the Rain Badge, P8
  after the game is cleared). P7_READY / P8_READY stay (harmless now).
- **Checkers**: script_check (ent: the switch objects on their levers, the scroll's sign on vanilla zone 447's sign
  tile; path: S/R slides across the raised track, Emerald's riders walked through all four press-count branches by
  the checker: ACCEPT added; P7 0 open in both versions), rooms_check / npc_check (S 10/32, E 8/40 materials) /
  caves_check: nothing for P7.
- Release patch: work/agents/th_p7/tools/mkpatch7.py (th_p6's mkpatch6.py + th_p7's p7_edits.py: a clean HEAD copy +
  th_glitch's, th_p6's and th_p7's edits, generator rerun; it checks the generator equals main's): run it LAST (it
  writes everyone's sections). p6_edits.py's build-list anchors are main's; on the lead mkpatch7 replays th_p6's
  shared hunks with the lead's anchors (" link met_names").
- Gaps: the levers' light (Lever_On's green lamp) is not drawn (no free object record); SE_CLICK and the pad's
  warpteleport sound are guesses (SEQ_SE_DECIDE1, SEQ_SE_KAIDAN); the pad fades instead of Gen 3's spin.
<!-- /th_p7 p7 -->

## 6. New-area glitch check (th_glitch, 2026-10-19 night)
Checked zones 432, 434 + 451, 438, 441, 449 and the changed 512-514, 552 in Sapphire and Emerald (Ruby: spot check):
rooms_check / walk_diff / interior_sweep_check / script_check / npc_check on test ROMs, plus per-state and per-slide
comparisons with the decomps and an emulator walk of every puzzle (work/agents/th_glitch/tools/gl_test.py: the builder's
th_test.py + probes; proofs screenshots/trick_house/glitch_*).
- **Fixed**
  - P4 (both versions): Gen 3's ledge row (Sapphire row 17, Emerald row 18, MB_JUMP_SOUTH) was a row of plank boxes:
    you could not hop down from the maze to the exit mats, only walk round by column 0 (a boulder there could shut you
    in). Now Black 2 ledge cells drawn as low steps with Gen 3's ledge art (`puzzle_recipe`, any puzzle with
    MB_JUMP_* tiles; tested: (3,17) -> (3,19), no way back up).
  - P5 (both): the back wall stood only behind row 2's walkways (black gaps in it: rooms_check (p) at Sapphire
    (10, 0)); now whole (floor_extra strip). The walkways also had the 12-unit back-wall floor strip drawn into the
    void north of them (looked most of a tile deeper: walk_diff OPEN 6 S / 1 E): new opt-in models_interior key
    `open_no_strip`.
  - P3 zone 451 played Route 110's song with the Hoenn soundtrack (hoenn_music gave the zone copy its parent's song):
    music changed at every button. patches/hoenn_music.py: a room's zone copy ("variants" with "room") plays the
    room's song (both zones' headers now differ only in the matrix).
  - Checkers: caves_check's Gen 3 model slides on MB_TRICK_HOUSE_PUZZLE_8_FLOOR 0x48 as on MB_ICE (pokeruby
    ForcedMovement_Slip for both): walk_diff's 126 P8 "INVISIBLE" were the checker's; every P8 slide (every stop tile
    x 4 directions, people and item balls blocking) ends where Gen 3's ends, S 89 / E 84 stop tiles
    (tools/p8_slides.py).
- **Accepted (by design, as the originals)**: rooms_check (e) on Puzzle2-8: the exit mats lead to the Entrance's
  warp 2 (the scroll's hole), whose own warp names Puzzle 1, and the door to the one end room, whose warp 0 names
  Puzzle 1's door: both decomps' warp tables (ACCEPT, `Route110_TrickHousePuzzle[2-8]`, covers P6/P7). walk_diff
  INVISIBLE on Puzzle3_Alt_Emerald: Gen 3's door state 1 shuts the same pocket (WALK list). The builder's P5 "(p) black
  void" was not by design (the back-wall gap above), fixed. Left as known (the interiors' documented OPEN class, room
  geometry unchanged since before the Trick House): floor in front of the back wall in the Entrance's scroll bay, the
  End room and the Corridor.
- **Checked, no problem**: P3's two rooms: walkability = Gen 3's SetDoorsState0/1 tile for tile, same cells and the
  same triangles outside the door tiles, same people/signs/warps/triggers/header; reach with buttons toggling = Gen 3's
  (tools/p3_states.py, p3_geom.py); in the emulator a button swaps zones with you on the button (facing: below).
  P2 holes block until their button. P5 wrong answer -> back to (0,21) as Gen 3's warp. Exit mats -> the Entrance
  (Sapphire (4,2), the lead's arrival; the scroll's warp tile does not fire), back in by the scroll. Doors open,
  end room, door shuts, corridor, Trick Master gone: every puzzle.
- **Still open (not small)**: P2/P3 pressed-button art (needs a walk-over object: Black 2 actors block their tile);
  P3 Rock Smash rocks come back after a battle or a button press (the two by the mats in both versions; Black 2's
  rock script sets no flag, and Ch3's reserve is spent on P6/P7). Neither can trap you (you have Rock Smash). After a
  P3 swap the first step is eaten by the fade-in (as any scripted warp). A turn made onto a button (e.g. walking
  down, then right onto it) leaves you facing the old way after the swap: Black 2 fires the step trigger before the
  turn is applied, so PlayerGetDir reads the old facing (also read after the fade; PlayerTurnByTrigger did not help;
  straight onto a button keeps the facing). Cosmetic (Mauville Gym's and New Mauville's switches use the same
  PlayerGetDir pattern).
- **Release patch**: th_p7's work/agents/th_p7/tools/mkpatch7.py replays the generator edits (tools/th_edits.py) and
  this section; then work/agents/th_glitch/tools/addtracked.py adds the hunks of models_interior.py, caves_check.py,
  walk_diff.py and patches/hoenn_music.py. The two rooms_check ACCEPT entries are in main only: the lead's
  rooms_check has no ACCEPT list until sr_rooms.patch / em_rooms.patch (add them there, as th_p6's).
- P6 (442) and P7 (447): static checks only (rooms_check 0, walk_diff 0 open, S and E); emulator walk: section 8.

<!-- th_check67 check -->
## 8. P6/P7 glitch check (th_check67, 2026-10-20)
Emulator walk of zones 442 and 447, one per room and version (test ROMs Sapphire 419d1ceb, Emerald ee63e3e2; tools in
work/agents/th_check67/tools: gl67.py = th_p7's p7_test.py + th_p6's P6 solver + th_glitch's probes + new ones, run.sh,
arms_static.py, specks.py; logs work/agents/th_check67/test_glitch2_*.log; proofs screenshots/trick_house/glitch2_*).
Results: Sapphire P6 17/17, P7 34/34; Emerald P6 17/17, P7 96/96.
- **Checked, fine**: scroll arrival (0,21) on floor; exit mats -> the Entrance (5,3) on floor, back in by the scroll; door
  -> end room; player height 0 on every tile visited (S 125 / 79, E 118 / 111 tiles); zone headers: no cycling, no
  Escape Rope (Gen 3: indoor, allow_cycling/allow_escaping false), so no bike in either room. P6: all arm actors there
  on every check, flag 0x80 (no collision), y 0; every gate drawn in each orientation it can reach (works poked, three
  camera spots); running through the gates (B held: S 20 turns, E 5) and walking, every step and turn as
  rotating_gate.c; a bump; the three trainers. P7 S/R: each lever's turned arrow drawn exactly on its arrow tile
  (object + model offset = tile centre, y 0); a slide over each; the warp pad -> (3,19). P7 Emerald: after each of ~40
  button presses every rider stands where rotating_tile_puzzle.c puts it, never in a wall or on the player (statically
  too: all 4 places of each rider are floor, off buttons and pads); 18 pad uses; all six trainers. Black areas near the
  room's corners: the same camera box as P1-P5.
- **Fixed** (layered surfaces < 2 units flicker in melonDS, notes/INTERIORS.md "Flicker"):
  - P6 arms (both versions): every gate rests an arm along a plank box (Gen 3 keeps one quadrant of each gate solid as
    its stop), and the rail sits on the tile edge: its top was 1 unit over the 8-high box top and its side 1.5 units in
    front of the box face. rotating_gates.arm_model: rail 3 -> 4 units wide, 9 -> 10 high (coordinated, section 5);
    seen in the Emerald build (glitch2_e6_p6_gates_*).
  - P7 S/R: the turned-arrow objects lay 1 unit over the floor's arrow art: now 2 (p7_switch_models). Geometry only
    (the Sapphire test ROM was built before; the arrows' positions were checked on it).
- **Also fixed** (lead's request): P2's hole object (008e) lay 1 unit over the floor art: now 2 (hole_object; static
  proof only: model height, generator current, rooms_check).
- **Left for the lead**: a few isolated 1-pixel dark specks on the floor in DeSmuME in every puzzle room P2-P8 (the shared room rules'
  floor, not P6/P7's). The black-backed arrows at S/R P7 (2,8) and (12,8) are Gen 3's own metatile 0x276. The Emerald
  test ROM had fortree_gates' unfinished rotating_gates.py/.c (two-puzzle tables): P6 behaved the same.
<!-- /th_check67 check -->
