# Building and testing (2026-10-05)

## Build a ROM
    cd b2tools && python3 build_rom.py --clean <patch> <patch> ...      → work/rom/hoenn.nds
- Starts from an APFS clone of the decomp's matching file tree (links followed), applies `b2tools/patches/<name>.py`
  (each has `apply(files_dir)`), writes `work/rom/rom_config.yaml` with absolute paths, runs `dsd rom build`.
- With no patches it reproduces the dump exactly (SHA1 `e51e6dfb…0abb`, checked). ~6 s.
- NARC edits go through `b2tools/narcio.py` (the decomp's own `narc.py` reader/writer).

## Emulator harness (DeSmuME via py-desmume 0.0.9, in `.venv`)
    ../.venv/bin/python walk.py ROM STATE OUT.png  D3 L2 A W60 S SAVE:path ...   (one sheet image per run)
- `emu.py`: headless DeSmuME; ~130 fps. `EMU_HOUR` (default 12) pins the game clock by giving the process a fixed
  UTC offset (DeSmuME's RTC follows local time). Season still follows the real month.
- **Savestates only work on ROMs with the same file layout** (the game keeps the ROM's file table in RAM; when a file
  grows, every later file moves and the game reads garbage after the next map load). So `build_rom.py` pads every
  archive we edit to a fixed size (`RESERVE`), and every test ROM shares one layout. Raise a reserve → rerun
  `make_states.py`. `--no-pad` builds the unpadded ROM (matches the dump when unpatched).
- Battery saves can't be exported from this py-desmume build (`backup.export_file` returns False), but the game's own
  saves work: DeSmuME autodetects 4 Mbit flash and writes `~/.config/desmume/<rom name>.dsv` (524,410 B = 512 KB +
  footer). Its log lines "BackupDevice: DeSmuME .dsv save file not found", "Autodetecting with autodetect_size=4" and
  "MC9: Unverified Backup Memory command: 08" appear for unmodified Black 2 too, which saves fine (save_check,
  2026-10-08). A save that hangs is a game problem: see "Saving and the field heap" below.
- Base savestates in `work/emu/` (not in git), made by `make_states.py ROM` (replays the intro, ~70 s; the ROM must
  have `test_door_to_nuvema`):
  - `base_bedroom.dst` — new game (boy, name AAAAAAA), player in their room in Aspertia.
  - `after_mom2.dst` — Mom's talk done. **Use this for slice tests**: route `D1 L3 D1 D1 L1 D1 L1 D1 W400` walks onto
    the exit mat and loads Nuvema fresh from the ROM under test.
  - `base_nuvema.dst` — standing in Nuvema (old Unova layout; obsolete since the Hoenn matrix).
- Since the Hoenn matrix (notes/WORLD.md) the test door lands in Littleroot at world tile (173,361):
  `D1 L3 D1 D1 L1 D1 L1 D1 W400 C173,361` then `T<x>,<z>` routes through work/world/cells collision.
- Clean up test images after looking at them; keep only proofs worth keeping in `screenshots/tests/`.

## Walking by position
`emu.player_tile()` reads the player's global tile from RAM (fx32 position at 0x02143c64/0x02143c6c, found by RAM
search in Littleroot). `walk.py` commands: `P` prints it, `G784,735` walks there tile by tile (x first, then z; stops
and reports if blocked). Counting held frames is unreliable: turning to face a new direction eats part of a press.

## Routing (navgrid.py)
`T784,690` walks the shortest route through our chunks' collision grids (ledges only downhill), re-planning from the
real position. The position address moves between builds and zones: `C779,745` (standing on a known tile) finds it,
and `step()` re-finds it after a zone change. Wild battles zero the position: route tests use
`HOENN_TEST_NO_WILD=1` builds.

## Test-only switches
- `HOENN_TEST_NO_WILD=1 python3 build_rom.py ...` sets every grass rate to 0 (no wild battles while walking routes).
- `HOENN_TEST_STILL_NPCS=1 python3 build_rom.py ...` makes Littleroot's NPCs stand still, so scripted inputs can talk
  to them (Sapphire's NPCs wander).
- The location banner only appears when walking into a place from another one (not when coming out of a door).

## Test-only patches
- `test_door_to_nuvema`: the player's house exit mat (zone 428 warp 0) leads to Nuvema (zone 389, warp 0).
  Route from `base_aspertia_outside.dst`: `U1 W200 D1 W400`.

## melonDS (user checks)
Open `work/rom/hoenn.nds` in `~/Applications/melonDS.app`. Real-hardware testing later via flashcart.

## Test switches for battles (2026-10-06)
- `HOENN_TEST_PARTY=1` (scripts patch): entering Littleroot with an empty party gives a Lv 50 Mudkip
  (`src/field_scripts/0778_littleroot_town.s` Script_9). The base savestates have no Pokémon, and a wild battle with
  an empty party hangs on the Poké Ball screen.
- `HOENN_TEST_NO_WILD_FILES=99,101`: only those encounter files lose their grass encounters (e.g. cross Route 101
  to test Route 102). `HOENN_TEST_NO_WILD=1` turns off all of them.
- **Keep a/1/2/7 file sizes unchanged**: the game keeps the encounter archive open with its file table in RAM, so
  savestates made before a size change read garbage (no battles, then the error screen). `gen_encounters.py` pads
  every table to its file's original size. The same may hold for other archives the game keeps open: if a test
  from a savestate behaves oddly after an archive changed size, rebuild the base states (`make_states.py`).
- `emu.travel(x, z, avoid='g')` routes around tall grass.

## Test warp (2026-10-06)
`HOENN_TEST_WARP=zone,x,z` (build env, b2tools/patches/scripts.py): reading Littleroot's town sign (stand at
(183,366) facing north; from work/emu/base_littleroot.dst: `C173,361 G184,361 G184,366 G183,366 U1 A W300`) warps
there. Since story_finish (2026-10-07) it fades out and in like a real warp (`h_warp_arrive`: FadeOutBlack, RTReserveScript
10017, FadeWait, MapChangeCore) and people, balloons and trainers work right after it (tested). The old artifact (talking
dead, NPC balloons hanging or crashing until a door warp) was the missing FadeInBlack after a scripted MapChangeCore: Black
2's field after a script's map change waits for the caller's fade-in (a door warp has its own, EventWarpSequence_CreateIn).
Either the reserved arrival script 10017 or a FadeInBlack + FadeWait in the same script after MapChangeCore fixes it
(both tested on Littleroot's twin scene: MapChangeCore alone left her balloon hanging). Not the arrival height: the player
lands on the ground below the given y (Fortree at 96 with y 0). emu.calibrate's lowest match 0x02143c64 reads the
ground + 4 (not the player's own vector, which reads the ground): use calib2 (work/agents/ch7/tests/lib.py). DeSmuME's battery saves live in ~/.config/desmume/<rom name>.dsv (all hoenn.nds
share one); cold-boot tests use b2tools/emu.py fresh_battery() on a uniquely named ROM copy. Savestates keep tables
the game reads once at boot (e.g. a/1/4/9 darkness): re-run make_states.py after changing such data.

- `HOENN_TEST_GAME_CLEAR=1` (scripts patch): Route 131's zone init sets FLAG_SYS_GAME_CLEAR first, so arriving there by a
  warp shows the post-game layout (Sky Pillar islet, map replace event 7; src/field_scripts/scenes/Route131.inc).

- The zone-lookup code patch (patches/hoenn_world.py apply_code, notes/WORLD.md "Sub-cell zones") lives in ITCM,
  copied at boot: states from a ROM without it crash when ov012 reloads. Make states on a ROM with it (test_cave_kit
  replaces Littleroot's scripts, so make them on a build without the kit: same file layout); world_fixes' tools:
  work/agents/world_fixes/tools/mkstate.py (make_states.py up to base_littleroot, into a folder of your own), zt.py
  (cave_test-style moves; INJECT=1 pokes the code into an older state instead), sandbox_build.sh.

## Continue tests (opening_polish, 2026-10-06)
Save from a state: X, touch SAVE at (60, 93), A ×4, wait ~900 frames (the .dsv is written). py-desmume cannot open a
second emulator in the same process, so boot in a new process: run 1200, A ×8 (title → CONTINUE), wait.
`work/agents/opening_polish/save_continue.py ROM STATE OUT.png save|boot` does both.

## Caves (cave_builder, 2026-10-06)
`b2tools/cave_test.py ROM OUT.png SIGN ...` walks caves (Q routes inside a built cave, Y waits for a warp's arrival
tile, F films a transition; `COLD=1` cold-boots through the intro for tables read at boot, e.g. darkness), and
`b2tools/agent_build_caves.sh` builds caves for a cave agent: notes/CAVES.md "How to test".
- **test_cave_kit + a state from a ROM without the kit: no trainer battles** (wild_tables, 2026-10-08). The kit makes
  script file 778 2,656 B shorter, so every later file inside a/0/5/6 moves (1,085 offsets change; the ROM's FAT stays the
  same). With a state from a ROM without the kit, the kit's sign and warp still work and so do wild battles. But a
  trainer who spots you walks up and then hangs, and DeSmuME logs `ARM9: Undefined instruction ... PC=0x3C` (Ruby,
  Mt. Pyre 3F's Psychic). On a scripts-patch HOENN_TEST_WARP build, with states made on that same ROM, the same trainer
  battle starts normally. The likely cause is that the state holds the old offsets of a/0/5/6's files, but this is
  not proven. For trainer tests, make states on the test ROM itself, or use the scripts-patch warp instead of the
  kit.
  Fix (check_ruby, 2026-10-08, its own kit copy in work/agents/check_ruby/tree): pad the kit's file 778 with zeros to the plain
  file's size and leave HOENN_TEST_WARP unset (the kit reads its target from another variable, so the scripts patch builds the
  plain 778): the kit ROM then differs from the plain ROM by 2,604 bytes, and states made on the plain ROM battle trainers
  normally (tested: Magma Hideout grunts, Tabitha).

## Story test switches (story_infra, 2026-10-06; notes/STORY_PORTING.md section 8)
- `HOENN_AGENT=<you> zsh b2tools/story_build.sh`: the full patch list + `trainers story`, into work/agents/<you>/rom.
- `HOENN_TRAINERS_FIT=1` (+ `HOENN_TRAINERS_FIT_KEEP=TRAINER_A,B`): keeps a/0/9/2 at Black 2's size until
  build_rom.py has RESERVE[92] (default-move parties fall back to Black 2's level-up moves; the kept ones stay exact).
- `HOENN_TEST_TRAINER=TRAINER_A[,x,z][+TRAINER_B…]`: eye-contact trainer NPCs in Littleroot from (176,358).
- `HOENN_TEST_MOVES=1`: the player's house sign (175,360) plays every movement group on the player (0778 Script_2);
  `work/agents/story_infra/tests/moves_probe.py` times them.
- The trainers patch changes overlay 36's compressed size: savestates from a ROM without it read a stale file table.
  Make states on a ROM with it (copy of make_states.py with OUT = your folder).
- `HOENN_TEST_TWO=1` (2026-10-07): Littleroot's town sign (stand at (183,366) facing north) starts the Tate & Liza
  battle (`h_trainerbattle_two`, lends Lv 100 Tyranitars until two can battle; pick their 2nd move, Earthquake does
  nothing to Levitate); Birch's house sign (180,360; stand below, face north) battles May (TRAINER_MAY_4) for her
  defeat line with the player's name. `work/agents/story_infra/tests/battle_test.py`, `opening_verify.py`.
- Story builds while other agents add rooms: `HOENN_SKIP_UNBUILT_ROOMS=1` leaves out rooms not built in your
  interiors folder (else the interiors patch stops at the first missing room.json).

## Story common pieces (story_infra, 2026-10-07; notes/STORY_COMMON.md)
- `HOENN_TEST_COMMON=1`: Littleroot's Lab sign (stand at (174,370), face north) runs every common macro once
  (`src/field_scripts/common/test_common.inc`); the town-sign line at the end = all checks passed.
- `HOENN_EXTRA_STORY=a.json[:b.json]` (story patch) adds test-only story-object files; `HOENN_EXTRA_TEXT=a.json`
  (text patch) adds a test-only text-override file (same format as src/text/overrides.json).
- `HOENN_TEST_CH<n>=v`: chapter test switches, passed to every script as `-D HOENN_TEST_CH<n>=v`
  (notes/STORY_PORTING.md §8).
- **Any system-text change** (a/0/0/2: item names/descriptions such as the key-item renames, place names, class
  names ...) moves the later files inside a/0/0/2, whose table the game reads at boot: savestates made before it hang
  as soon as something reads a later system text, e.g. a script that writes a species name into a message, or the
  nickname screen (black). Remake the states (copy of b2tools/make_states.py) or cold-boot after such a change.
- **Overlay code changes** (patches that edit arm9_ovNNN.bin and so change its compressed size: ov012 by the story
  patch with HOENN_STORY_CODE=1, ov036 by the trainers patch) break savestates made before them as soon as the game
  reloads that overlay (a door warp goes black: tested 2026-10-07). Same cure: new states.
- `HOENN_STORY_CODE=1` (story patch, 2026-10-07): the overlay edits of S_common (ribbons, hidden-item table, no
  Xtransceiver in the new-game Bag) are off by default until the lead's next savestate remake; build with it (and your
  own states) to test ribbons.
- Room generators keep a story agent's part (b2tools/story_merge.py): rerunning gen_interior_recipes_houses.py
  SlateportCity_House2, shops_rooms.py OldaleTown_Mart and gen_caves.py GraniteCave_1F on 2026-10-07 left their
  story sections, entries, includes and notes as they were.

## Stale savestates and Pokémon names (story_fixups, 2026-10-07)
"????" for every Pokémon's name in battle (trainers', gifts, even a fresh PokePartyAdd) = a savestate made before a
system-text size change: the game opens the species names (system file 90) once at boot and keeps reading through that
handle at the old offset. Tested: Youngster Calvin "sent out ????????!" from the v13 base state on a build with ch1's
0023/0037 overrides, "Zigzagoon" on a cold boot of the same ROM (screenshots/story_fixups/01_*). Since c38016b the text
patch puts every system file in a fixed slot (HOENN_TEXT_SLOTS, default on), so text edits no longer move files.
Cold-boot state for your own ROM: `cd b2tools && ../.venv/bin/python ../work/agents/world_fixes/tools/mkstate.py ROM OUTDIR/`.
Room exits: `python3 b2tools/check_exits.py [WORLD_DIR]` (notes/INTERIORS.md "Story fix-ups").

## Overlays and old savestates (dewford_dark, 2026-10-07) [code][test]
- An overlay's table entry (compressed size) is read from the ROM at each load (arm9 sys_read_overlay_header: the RAM
  copy at 0x0214bf68 is empty), its file position/length from the FAT the state holds in RAM, and the digest check is
  skipped on a cartridge boot (sys_get_boot_indicator == 1). So an overlay edit is safe for old states as long as its
  dsd-compressed size does not grow (same 512-byte slot, nothing moves): measure with
  work/agents/dewford_dark/tools/ovsize.py (rebuilds a vanilla rig with the candidate overlay; compressed size of the
  real build, which a plain BLZ encoder does not reproduce).
- But **ov012 stays resident**: in states made from v13.1's base_littleroot it was still the state's copy after the
  sign warp, door warps and Mr. Briney's boat (checked in RAM). New ov012 code (script commands) is never seen by an old
  state: a script using it runs the old command (0x1c9 in a map script: access error, the game hangs at Dewford Gym's
  door). Test such code on a cold-boot state of your own ROM (mkstate.py above).

## Looking at any room with one build (sweep_rooms, 2026-10-07)
`../.venv/bin/python b2tools/room_look.py ROM STATE OUT.png ZONE,X,Z [moves]`: on a HOENN_TEST_WARP=563,6,7 build (other
value: TEST_WARP env), it patches the town sign's MapChangeCore constants in an APFS clone of the ROM (room_look.nds next
to OUT) and warps there, so one build visits every room (moves: U3 D1 L2 R1 A B W60 S P Cx,z). STATE: a Littleroot state
of the ROM's layout (cold-boot one: work/agents/world_fixes/tools/mkstate.py). Pick a walkable arrival tile (a tile in
a wall puts the player inside it).

## Saving and the field heap (save_check, 2026-10-08) [code][test]
- **Symptom (v14 and v14.1):** menu → SAVE in any outdoor zone of the Hoenn matrix: the bottom screen goes black, the
  top keeps the menu's empty white strip, the game is frozen. A ROM bug, not the harness: unmodified Black 2 saves in
  the same harness ("AAAAAAA saved the game."), and a cold boot of v14.1 (no savestate) hangs the same way
  (screenshots/save_check/01-03). The text is fine (system 44 "Would you like to save the game?" etc. is Black 2's,
  byte for byte apart from HOENN_TEXT_SLOTS' zero padding).
- **Cause:** `GFL_HeapAllocate(HEAPID_FIELDMAP 0x15, 18,820 B)` in GFL_FontLoad (the save window's font) fails →
  `sys_exit` (ARM9 PC loops at 0x0207c7f8). The save needs **83,004 B** of the field heap (measured at every
  allocation: font, windows, and a 32 KB tail buffer from GFL_BGSysClearCharCore while it writes; same in Black 2).
  Pack 0 (371,448 B since towns5 joined it in v14; 382,856 B since buildings_audit 2026-10-08: 100,320 B free after a map load, the save 17,316 B to spare) is read whole into that
  heap, which then kept 31,3xx B free after a map load in every pack-0 zone (before the fix below). v11-v13.1 (pack 0 319,428 B) had an estimated 83,4xx B: it worked by ~0.4 KB.
  Black 2's biggest exterior pack is 223,356 B. The Slateport Energy Guru's Buy screen (outdoor, 33.5 KB) hung too.
- **Fix:** `patches/area2_buildings.py` apply_code: ov036 `MAP_CONFIGS[0].heapSize` 0x136800 → 0x14A800 (map type 0 =
  every Hoenn outdoor zone and the standalone ones; FIELDMAP = heapSize − 0xf000, fieldmap.c:131): field heap
  1,210,312 → 1,292,232 B, 113,2xx B free after a map load, 30,260 B spare during a save. It comes from HEAPID_USER's
  free space while the field runs (110,696 → 28,776 B). Nothing allocated from USER while the field existed in any
  test (opening, menus, Bag, shop, wild and trainer battles, walking, saving); battles and the Bag close the field
  before making their heaps. Black 2 keeps that space for C-Gear communication, which Hoenn never turns on (no script
  uses CGearPowerOn / FieldSubscreenChange): recheck USER if a type-0 zone ever gets the C-Gear, Union Room or PWT
  comm. `apply()` stops the build when pack 0 would leave the save < 8 KB (`save_headroom()`): grow pack 0 by more
  than ~22 KB → raise FIELD_HEAP_EXTRA (watch USER) or shrink the pack.
- **Tested** (screenshots/save_check/05-10): release-list build, cold boot → Littleroot → save → new process → title
  → CONTINUE ("Littleroot Town, Time 0:02") → standing at (173,361) → save again over it; 54 zones warped into
  (36 pack-0 zones all 96,880 B free with +0x10000, 18 standalone 415,832 B); Route 104 wild battle → run → Bag →
  save; Route 117 trainer battle won → back in the field; Pacifidlog surfing, 8 badges (check_postgame's state + a RAM
  poke of the same value) saves, hangs without it.
- Tools (work/agents/save_check/tools): `heapdump.py` (a GFL heap: size, free, largest, blocks by file:line),
  `savepeak2.py` (a save's exact need), `fieldsweep.py` (warp to every outdoor zone on a HOENN_TEST_WARP=563,6,7 build
  and read the heap), `warpdo.py` (warp + moves, watching USER/field heaps and sys_exit; POKE_HEAP=0x... tries
  another type-0 heap size in RAM at each field open), `statesave.py` (Bag reopen + save from any state, optional
  poke), `cycle.py ROM PREFIX play|continue [resave]` (save → reset → Continue with no savestate).
- Savestates: ov036 grows 4 B inside its 512-byte slot; ov036 is reloaded at each field open, so an older state gets
  the new heap size after its next field reload (Bag, battle).

- **Re-measured 2026-10-11 (pwt_tower, notes/BATTLE_TOWER.md §4.1):** the save keeps 18,632 B beside Mr. Briney's
  boat (Route 104, Dewford, Route 109: boat included), 195,976 B in the Oceanic Museum 1F, 265,032 B in Victory Road
  B1F and 296,376 B in the PWT lobby. Save -> Continue worked in each. In the PWT stadium (map type 0) nothing
  allocates from HEAPID_USER (28,776 B free) while the field runs. Driver: work/agents/pwt_tower/tools/savecycle.sh TAG
  ROM ZONE,X,Z STAGE, which runs a CHMO+TEST_WARP build from a cold-boot Littleroot state.
  Pitfalls found: a 4-frame X press after loading a state may not open the menu (hold 10 frames, then wait 150 for
  the bottom screen); freeze_fix's pt driver skips drawing in run(), so draw a few frames (cycle) before a screenshot.
- **door_fix (2026-10-11), same three boat spots, same driver** (work/agents/door_fix/tools/savecycle.sh, states made
  on its own CHMO build): v16.3's models 18,632 B; the door fix alone (commit 1810498, pack 0 383,724 B) **8,712 B**;
  with `buildings.cull_unseen` in every pack-0 model writer (triangles no view of the field camera can face: north
  walls, undersides; pack 0 372,812 B) **19,624 B**, Continue fine in all three. Free after a map load moves 1:1 with
  pack 0's size (101,636 / 91,716 / 102,628 B).

## Script checks (script_check, 2026-10-08) [code][test]
- `python3 b2tools/script_check.py ROM.nds [--world W] [--dir INTERIORS] [--labels]` (a report step of rebuild_slice.sh, after
  the ROM: `<world>.script_check.txt`; `HOENN_VERSION=ruby` for the Ruby ROM). It reads what the ROM has after every patch
  (zone headers, entities, field scripts decoded with the decomp's own `tools/scripts/field_script.py`, script texts) and
  checks it on the built tiles: people / signs / hidden items / step triggers where they can be used (BG events: y-2 <= the
  reader's y < y+2, CheckBGPositionMatchGrid; triggers: CheckTriggerPositionMatchXYZ, the same window), scripted map
  changes landing on walkable tiles of their zone, scripted movement paths (ActorCmdExec from the actors' tiles, the player
  from each tile of the trigger that starts the scene or from the arrival tile of a reserved-script warp; works followed,
  flag tests both ways), the player walking onto another zone's tile without h_zone_hold, a balloon waited on (LastKeyWait)
  still open at an info window or a window-opening global script (h_giveitem), message ids past the text file's end,
  script ids that resolve to nothing, movement lists not 4-byte aligned, Black 2's own triggers / signs left in a room.
  By-design findings: ACCEPT in the file (each with its reason). `--vanilla roms/black2_original.nds` prints which
  (open window, command) pairs Black 2's own scripts use (the evidence for the msg rule).
- Test kit `HOENN_TEST_CHSC=1` (src/field_scripts/scenes/script_check_test.inc, hooked in Littleroot's town sign like
  HOENN_TEST_CHMO; stage sentinel 0x5C01, rewritten in an APFS clone by work/agents/script_check/tools/mo.py): parties
  made by a normal script (Tyranitar/Swampert/Manectric), Ch5's or Ch13's start (with HOENN_TEST_CH5 / _CH13 built in),
  a Lv 2 Wurmple to lose battles (house or Oldale Center respawn). mo.py commands beyond the missing objects' version:
  F (battle by touch, cycling the four moves), E (run from a wild battle), K (calib2), TF x,z (travel, battling trainers on
  the way), TX x,y (touch), X, SS (both screens), SC_TRAP=1 / SC_HOOKS=name=addr,... (sys_exit / abort traps, call logs),
  SC_RESERVE=n (the warp reserves the target zone's script n, its arrival scene), SC_GIRL=1 (PlayerInfo gender +0x1D = 1).
  play.py = the same from any state without the warp.
- **A blackout at the player's house left the screen black for good** (fixed 2026-10-08, screenshots/script_check/15-17):
  EventBattleLose (ov012 event_battle_lose.c) runs local script 2 of the respawn zone, not the Centers' global 2001, when
  IsReturnLocationNonLeaguePokeCen is FALSE, and it is FALSE for RESPAWN_ZONE_INFO 0 (the new game's respawn: zone 390,
  Brendan's house 1F (6,8)); 0780 Script_2 was a VMHalt, so the field never faded in (MASTER_BRIGHT 0x8010, game running).
  Script_2 now heals and fades in (Sapphire's DoWhiteOut shows the player at home, healed, no line). Before the fix every
  battle lost before the first Pokémon Center, or after the Hall of Fame before one (h_setrespawn 1), soft-locked the game.
  A Center respawn always worked (nurse heal, tested from Oldale's). Record 0 is Brendan's house for a girl too, so
  Script_2 sends a girl on to May's house 1F (6,8) with its Script_2 (0784) reserved: the same heal and fade-in.
- **Field heap in rooms, caves and underwater maps** (2026-10-08, work/agents/script_check/heapsweep/): 31 of the heaviest
  (big rooms, harbors with the S.S. Tidal / submarine, hideouts, Seafloor rooms, Victory Road, Underwater1-4 and the
  submarine nook, Gyms) keep 278,980 B (Oceanic Museum 1F) to 386,632 B of the 1,210,312 B field heap free after the
  map loads; the save needs 83,004 B. A real save in the tightest one (Oceanic Museum 1F) worked (18_*). Only map type 0
  (outdoor, pack 0) was ever short.

## Bedroom PC test (room_pc, 2026-10-08)
- `HOENN_TEST_CHRP=1` (any HOENN_TEST_CH* env is passed to the assembler): in the player's room 2F (0782 / 0786 Script_3) an
  EMPTY party gets a Lv 5 Mudkip + Treecko before Black 2's PC runs, so Deposit works from work/emu/base_house.dst (the
  states have no Pokémon; Black 2 keeps the last one in the party). Route: `U8 W200 L7 U1 A` from base_house.dst = the PC.
  Harness: work/agents/room_pc/t/final_test.py ROM save | continue (save: PC menu, deposit, withdraw, deposit, Switch off, Save;
  continue: cold boot, CONTINUE, Withdraw list shows Treecko in Box 1, Deposit list shows Mudkip only). Proofs: screenshots/room_pc/.
- `HOENN_TEST_CHRP=2` (room_pc follow-up): on top of =1, the bedroom PC gives six caught Pokémon (the party), registers 12 Hoenn species
  as seen and sets the Pokédex flag (2402: the PC offers Prof. Birch's PC), and the notebook (Script_4) switches the National Dex on.
  Harness: work/agents/room_pc/t/dex_test.py ROM [1|2]; proofs screenshots/room_pc/06_*, 07_*.

## Pokédex: the regional dex is Hoenn's (dex_fix, 2026-10-08; v15.3 hotfix)
- **v15.2 bug:** opening the Pokédex from the menu showed "An error has occurred" (both versions, every save). Cause: the regional
  list was still Black 2's Unova dex (personal a/0/1/6 file 709 = regional number per species, 999 = none; a/0/9/7 file 4 = the
  regional order). A Hoenn player has only seen Hoenn Pokémon, so ov302 func_ov302_021ad624 counted 0 entries. Then
  func_ov302_021ad0e8 (Victini 0x1ee unseen, so entry #000 is skipped, func_ov302_021ad72c) passed 0 - 1 = 0xffff to ov299.
  func_ov299_021a0324 allocated 65535 strbufs from heap 0x6b, the allocation failed and sys_exit ran. Black 2 gives the dex the
  same way we do (FlagSet 2402 only, 0854.s); it never hits this because its starter is in the Unova dex.
- **Fix:** patch `hoenn_dex` (b2tools/patches/hoenn_dex.py; in rebuild_slice.sh and story_build.sh, **add it to any copied
  patch list**). Data only: Hoenn #1-#202 in Sapphire's order (pokeruby species.h), Victini kept as the hidden #000; both files
  keep their size. ROM layout, savestates and saves are unchanged.
  - No save repair is needed: the save holds seen and caught flags by national number. A v15.2 battery save opens the dex on
    the fixed ROM; tested on both versions.
  - The start menu's seen count, the save card's "Pokédex: N", the search results and the summary screen now count Hoenn.
- **Tests** (work/agents/dex_fix/tests/pt: a copy of the playthrough driver; `dt.py` = drive.py commands + traps at the
  list count 0x021ad14a, GFL_HeapAllocate failure and sys_exit; `newgame.py` = a new game from mkstate.py's
  base_littleroot to Birch's Pokédex; `STARTER=2` picks Mudkip, who beats May's Treecko more often than Torchic beats her
  Mudkip). Menu: POKÉDEX at touch (192,46), SAVE at (64,141). Dex list: touch a row twice, then A:INFO at (45,92).
  Proofs: screenshots/dex_fix/.
- Not changed (cosmetic, v16):
  - the header still reads UNOVA POKÉDEX (graphic), and "Unova Pokédex: Search Mode" is in system text 0479;
  - the AREA tab shows Black 2's Unova map (town_map's phase 2);
  - the Habitat list (after the National Dex) is Black 2's.
