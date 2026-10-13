# NPC movement: Gen 3 movement types -> Black 2 move codes (v165_fixes, 2026-10-11)

One table for every writer: `b2tools/move_codes.py` (`TABLE`, `walk()`, `npc(movement, range, graphics)`,
`room_npc(object)`). Used by `converter/gen_trainer_npcs.py` (trainers), `b2tools/world.py` (town/route people),
the room generators (`converter/gen_interiors.py`, `gen_interior_recipes_houses.py`, `gen_caves.py`,
`b2tools/shops_rooms.py`, `centers_rooms.py`, `ship_hideouts_rooms.py`, `specials.py`); the hand-placed story people
(`data/story/*.json`, `data/interiors/*.json`) were brought in line once (work/agents/v165_fixes/tools/move_fix.py).
Checkers: `b2tools/move_audit.py ROM` (every Sapphire object's code in a ROM, per type), `b2tools/loop_check.py ROM`
(walkers and wanderers walked step by step in Gen 3 on Sapphire's map and in Black 2 on the ROM: paths, areas, warps,
traps).

## Black 2's move codes [code]
ov036 `ACTOR_MOVE_CODE_FUNCTION_TABLES` (pokebw2_field `build/asm/_dsd_gap@ov036_4.s`:36982; entries {code, init,
update, delete}; direction lists `data_ov036_021cbc70`; actor collision `src/ov012/field_actor_tool.c`
ActorRouteCollCheckCore: walk area = spawn +- areaW/areaH (0xFFFF no limit), MapTile_BlocksCollision (flags bit 0),
side walls 0x51-0x58, height step >= 20, other actors). Uses in Black 2's own zones (a/1/2/6) in brackets.

| Code | Behaviour |
|---|---|
| 0 | stand, facing the dir field [1716] |
| 2 | look around, 4 ways, a turn every 16-64 frames [69] |
| 3 / 4 / 5 | wander inside the area: all ways / up-down / left-right [336/11/11] |
| 6-13 | look in 2-3 ways: UL, UR, DL, DR, UDL, UDR, ULR, DLR |
| 14-17 | face up / down / left / right (same as 0 + that dir) [627] |
| 18 / 19 | spin counter-clockwise / clockwise, a turn per 24 frames |
| 20 | walk back and forth: start -> area edge (dir field's way) -> start ... [72] |
| 21-44 | walk a route of 4 legs (the 24 orders of U/D/L/R, Gen 3's WALK_SEQUENCE order: code = Gen 3 value - 8) [~10] |
| 45 / 46 | look up/down, left/right |
| 47 | NULL table entry (DP's berry tree): crashes |
| 48 / 50 | follower (story partner) / trainer pair partner (set by scripts / Black 2's double trainers) |
| 49 | spin that reverses at its dir field |
| 51-54, 85 | hidden trainers under grass (51, 54), soil (52, 53), a leaf pile (85): 32 units below ground with the effect on top, jump out when they spot the player (`EventTrainerEyeSub_DecideJumpOut`) [8] |
| 55-62 | turn as the player faces (facing only, never walk; 59-62 "in grass", flag unread) |
| 63-66 | follow walls (left / right hand) |
| 67 | wander left/right through walls |
| 68 | network player |
| 69-84 | rail versions (rail maps only) |

No walk-in-place, invisible or mirrored-copy codes exist (Black 2 does walk-in-place with script movements 28-43 and
hides people with spawn flags or the sprite).

Trainer sight (`event_trainer_eye.c` EventTrainerEye_CheckActorClash): evType 1 looks along its current facing (the
walk codes turn it the way it walks, as Gen 3), evType 2 looks all 4 ways (Black 2's hidden trainers; Gen 3's
TRAINER_TYPE_BURIED). A trainer that spots the player gets code 0 (Gen 3: a facing type).

## The table (Sapphire objects (trainers) / Emerald objects -> code)
Gen 3's range 0 means "no limit" on that axis; Black 2's 0 means "no movement": a wanderer with 0 on the axis it walks
gets 0xFFFF (Emerald only: Battle Frontier lounge / corridor). Things that are not people (Gen 3 anim tables
Inanimate, BerryTree, CuttableTree, BreakableRock: rocks, Cut trees, boulders, item balls, fossils, dolls, cushions,
the truck: `move_codes.static_graphics()`) keep what their writer gave them: a look-around code would turn a sheet with
one usable frame.

| Gen 3 type | Sapphire (trainers) | Emerald | Black 2 | Note |
|---|---|---|---|---|
| FACE_UP/DOWN/LEFT/RIGHT | 135/761/151/199 (19/88/40/41) | 227/914/220/269 | 14/15/16/17 | exact (0 + dir is the same) |
| LOOK_AROUND | 386 (11) | 526 | 2 | exact |
| WANDER_AROUND | 122 | 159 | 3 + range | exact |
| WANDER_UP_AND_DOWN / DOWN_AND_UP | 28 | 30 | 4 + range | exact |
| WANDER_LEFT_AND_RIGHT / RIGHT_AND_LEFT | 40 | 42 | 5 + range | exact |
| FACE_UP_AND_LEFT, UP_AND_RIGHT, DOWN_AND_LEFT, DOWN_AND_RIGHT | 10/6/15/9 | 25/20/32/27 | 6/7/8/9 | exact |
| FACE_DOWN_UP_AND_LEFT, DOWN_UP_AND_RIGHT, UP_LEFT_AND_RIGHT, DOWN_LEFT_AND_RIGHT | 0/3/5/2 | 0/4/4/3 | 10/11/12/13 | exact |
| FACE_DOWN_AND_UP / FACE_LEFT_AND_RIGHT | 9/12 | 7/16 | 45/46 | exact |
| ROTATE_COUNTERCLOCKWISE / CLOCKWISE | 15/15 (all trainers) | 10/12 | 18/19 | exact |
| WALK_UP_AND_DOWN, DOWN_AND_UP, LEFT_AND_RIGHT, RIGHT_AND_LEFT | 1/2/6/7 | 9/14/7/12 | 20 + range, dir = first way | exact (Gen 3 MovementType_WalkBackAndForth) |
| WALK_SEQUENCE_* (16 used) | 32 (28 trainers) | 30 | 21-44 + range | exact, except UP_LEFT_RIGHT_DOWN: Black 2's 25 holds 26's directions, so 21 (its mirror: up, right, left back, down; Route 117's little boy) |
| BERRY_TREE_GROWTH | 88 | 88 | 0 | (47 crashes) |
| TREE_DISGUISE | 3 (3) | 5 | 54, evType 1 | hidden in grass, jumps out; sees down only, as Gen 3 |
| MOUNTAIN_DISGUISE | 2 (2) | 2 | 53, evType 1 | hidden under soil, jumps out; sees down |
| HIDDEN (Emerald: BURIED) | 2 (2) | 2 | 53, evType 2 | buried in Route 113's ash; sees all 4 ways as Gen 3's TRAINER_TYPE_BURIED |
| COPY_PLAYER_IN_GRASS (COPY_PLAYER) | 1 (1) | 1 | 59 (55) | turns as the player faces (Gen 3 also walks) |
| COPY_PLAYER_OPPOSITE / COUNTERCLOCKWISE / CLOCKWISE (_IN_GRASS) | 2/2/1 | 3/2/1 | 2 | approximated: no mirrored copy in Black 2 |
| WALK_IN_PLACE_*, JOG_IN_PLACE_*, RUN_IN_PLACE_*, WALK_SLOWLY_IN_PLACE_* | 9/3/1/0 | 26/3/1/6 | 14-17 (facing that way) | approximated: no in-place code |
| INVISIBLE | 15 | 16 | (kept) | the writers give these an invisible sprite / flag (Kecleon: model 4481) |

## What changed in v16.5 (Sapphire; Ruby the same except Aqua -> Magma hideout grunts)
146 people behave differently (46 trainers), b2tools/move_audit.py / work/agents/v165_fixes/tools/move_compare.py
against v16.4: 42 walkers (34 route trainers, Charlie on the Abandoned Ship, 3 Aqua Hideout grunts, the 2 Machoke movers
in the Littleroot houses, Route 112's hiker, Route 117's little boy: before they looked around / faced / wandered);
wander left/right 36 and up/down 26 (Black 2's own 5 / 4 instead of 3 with one axis fixed, and story people who had no
area and only turned now walk Sapphire's range); look around 18 (stood still); wander around 10 (story people with no
area); look in 2-3 ways 6; the 7 disguised / buried trainers hide and jump out; 1 copy-the-player trainer. 34 more
only changed 0 -> 14-17 (same look). Kept on purpose: Mr. Briney (his loop starts by script after the rescue: 0474eda),
the rival's bike scene on Route 110, Archie on the Slateport harbour (scene facing), the moving-in Brendan room object.
Two Sapphire wanderers never step in Sapphire (object elevation unlike the floor: Pretty Petal's little girl, Route
115's woman): they only turn here too (area 0).

## Checks (v165_fixes)
- loop_check: all 42 placed walkers walk exactly Sapphire's path (UP_LEFT_RIGHT_DOWN mirrored), none stuck, no trap;
  Charlie passes over a cabin door tile on the ship, as in Sapphire. Wanderers: Black 2's reach = Sapphire's, except
  a Route 119 house Wingull that can now fly into the back-wall strip (option C) and the two elevation cases above.
- npc_check 0 over a limit; script_check 0 open.
- Emulator (test ROM with the sign warp; work/agents/v165_fixes/shots/): Route 110 Benjamin's loop = the simulated
  one, spots the player at 3 tiles from the side and from above -> battle; Route 117 Dylan (back and forth) spots at 4;
  Route 104 Billy and Route 117's boy loop as simulated; Charlie on the ship; the Machoke mover; Route 113 buried
  trainers jump out at 1 tile from the front and the side; Route 119/120 disguised trainers jump out from below
  (2-3 tiles) and not from the side; Route 119 Greg turns as the player faces; Lavaridge/Rustboro wanderers and lookers.
