# People sprites per zone: the limit, its cause and the fix (npc_limit, 2026-10-07)

Tags: **[code]** decomp / `tools/dsd dis` of ov012, ov035, ov036, main; **[bytes]** game files; **[test]** DeSmuME
(proofs `screenshots/npc_limit/`, scripts `work/agents/npc_limit/tests/`).

## The limit
**32 billboard materials per field** (Emerald: 40 since 2026-10-19, section "Emerald Route 123" below): one per distinct
people-sprite code (a/0/4/7 object code) in use at once. Not a VRAM or heap shortage. **[code + test]**
- `Field_InitActorSystem` (ov036 0x02180a50) calls `FldActSys_InitBlAct(actorSystem, actorBlAct, 0x20)` (the
  immediate is `mov r2, #0x20` at 0x02180a86, the `bl` at 0x02180a88) -> `FldBlAct_InitMatCache` allocates 32 entries of
  `{u16 objCode, u16 texMat, u16 flags, u16}` (`FldBlAct_CreateMatCache` 0x02193bf0). The billboard system itself has
  64 materials and 128 actors (`BlActSys_Create(0x40, 0x80, …)`, fieldmap.c:869), the actor system 64 actors
  (`FldActSys_Create(heap, 0x40, …)`).
- Who takes entries: the zone's **preload list** (zone header byte 1 `npc_cache` < 24 = a/0/5/7 file, read on every
  map change by ov035 event_mapchange.c `LoadMModelSystemInfoCache`, uploaded at field creation by
  `FldActSys_LoadCachedBlact`, flags 0 = kept for the whole field), the player's walking sheet
  (`FldActSys_LoadStaticBlact`, flags 0), and every other code when its first actor appears (`FldAct_InitBlActNewMat`
  -> async read -> `FieldBlAct_FinishAsyncMatLoad` -> `func_ov036_02193d14`, flags 1 = freed when its last actor goes,
  `FieldBlAct_UnbindActorObjCode`). The player's bike/surf/fishing forms are such dynamic codes too.
- Each entry's sheet goes whole into texture VRAM (`BlActSys_LoadSingleUseTexMaterial` -> `GFL_G3DResUploadTexData`;
  32x32 people: 3,616 B for 7 frames, 6,176 B for 12, the player 12,320 B).
- **When the cache is full, `FldBlAct_RegistCachedMat` silently stores nothing**: the sheet was uploaded (VRAM
  leaked), the actor's set-up never finds its material (`FldBlAct_UpdateAsyncActorSetup` waits for
  `FieldBlAct_FindCachedObjMat`), so the person is never drawn but exists: solid, talkable, its shadow drawn.
  Codes are claimed in spawn order (`SpawnAllZoneNPCs`, the zone's NPC list order), so the last new codes lose.

## Why Hoenn hit it at ~12 new codes
`b2tools/patches/hoenn_world.py` copied every Hoenn outdoor zone's header fields from Nuvema/Route 1, including
`npc_cache` 0: a/0/5/7 file 0 = **19 Unova codes** `[49 48 37 36 30 31 110 18 63 14 22 9 20 11 21 28 312 29 15]`
(73,312 B of VRAM) preloaded on every warp into the overworld. 19 + the player = 20 entries gone, **12 left** for
a zone's own people (plus any of theirs in that list: Slateport's 18, 20, 22). **[test]** Slateport, Ch3a state
before the Dock (18 codes present): cache 32/32 = the 19 + 231 + 12; codes 61 (Man1), 24 (Maniac), 12 (School Kid)
missing and invisible, only shadows (`screenshots/npc_limit/01_*`); free texture VRAM 57,840 B.
All 203 Hoenn rooms/caves already had 24 (their Black 2 templates).

## Black 2's own crowded zones **[bytes]** (`work/agents/npc_limit/tools/b2union.py`, `b2zones.py`)
Black 2 never needs more than 27 entries. A zone with a preload list has **all** its own people's codes in it
(Game Freak lists the region's people: Route 3 / Striaton / Driftveil / Humilau: 26 listed codes, 0 others), so
walking between those zones shows people at once; zones without a list load everything dynamically: Pokéstar
Studios 566 (23 codes, the most), Musical Theater 77 (22), Royal Unova 52 (21), PWT lobby 192 (19). Castelia 28
has 4 codes (map type 2, its crowds are not zone NPCs), Join Avenue 490 4 (visitors are added by its own code).
Nimbasa 62: 18 codes, all in its list #6. Area textures of those zones: 115-187 KB (map + building sets).

## The fix (data, no code) **[test]**
`hoenn_world.py` now sets **`npc_cache` = 24 (no list)** for every Hoenn outdoor zone (hand-made Littleroot/Route
101/Oldale and the warp-only groups included), as 562 of Black 2's 615 zones. A zone can then use **30 sprite codes
at once** (31 while the player walks). Proofs:
- Slateport after: cache 19 entries (player + all 18 codes), every person drawn, VRAM free 114,672 B (01_*).
- Stress (`work/agents/npc_limit/stress.json`, HOENN_EXTRA_STORY): Slateport + 14 test people = 32 NPC codes ->
  cache 32/32 with exactly one person invisible, the last one in list order; free VRAM 36,336 B with 31 sheets
  loaded (most 12-frame); no flicker over 4 shots 30 frames apart; walking still 16 emulator frames a tile in a zone
  of 45 NPCs (no slowdown) (04_*).
- Zone swaps on foot Slateport <-> Route 110: each zone's codes are released and loaded (cache 19 -> 16 -> 19, VRAM
  back to 114,672 B: no leak) (05_*). Rustboro (16 codes) after: 150,000 B free (06_*).
- Warps (doors, fly) wait for every sheet before the field shows (`FieldRoutine_MapSpawnFinish` loops on
  `FldActSys_IsAsyncLoadPending`); walking across a zone line loads them one per frame or two, as before for all but
  the few codes Nuvema's list happened to share.
- Raising the 32 itself (the `mov r2, #0x20` above; the texMat pool is 64) is **not needed** for Sapphire/Ruby: with
  every Sapphire object ported the busiest zone needs 22 entries (projection below), 28 with berry planting's trees.
  Emerald needed it for Route 123 in 2026-10 (below).
- The header byte is read from the ROM on each map change: no savestate remake needed for this change (tested with
  states made before it).

## Checker: `b2tools/npc_check.py`
    python3 b2tools/npc_check.py ROM.nds|FILES_DIR [--zone N ...] [--all-zones] [--set FLAG_A,FLAG_B|new-game]
                                                  [--sapphire] [--verbose] [--strict]
Reads a built ROM (or a build's files/ folder): every Hoenn zone's NPC entities (so everything the build put there:
generated people of data/hoenn_content.json, room files, trainer NPCs, data/story/*.json objects), the preload list,
each sheet's VRAM size, the area's map + building texture bytes, ActorNew codes in the zone's script source; codes
162-177 count as the rival (12,320 B), berry planting's tree codes 0x0F00-0x0F7F one picture each. Limits checked:
materials (preload + codes + 2 for the player <= the cache size, read from the ROM's ov036: 32, Emerald 40), texture
VRAM (area + sheets + player 12,320 + fishing form 24,608 + 32 KB for effects/shadows (24.4 KB measured in Slateport)
<= 393,216), actors (<= 64). Story states: the table is the worst case (every spawn flag clear, so every state is at
most that); a zone over a limit is re-checked for every combination of its spawn flags and the people that would be
invisible are listed in load order; `--set` checks one state, `new-game` = the flags scenes/new_game_flags.inc sets;
`--sapphire` = projection with every Sapphire object of each outdoor map present (data/sprite_map.json codes).
`b2tools/patches/npc_check.py` runs it as the last build step (reports, changes nothing).
`--sapphire` and the table print the cache size the ROM was built with (`Material cache: 40 (ov036)`).
Results (HEAD ab94d76 with the banner rectangles, `work/agents/npc_limit/npc_check_*.txt`): **340 zones, 0 over**.
Fullest: Slateport 23/32 materials (21 codes, 31 NPCs, VRAM 327,504/393,216), Lilycove Contest Hall 23/32 (21 codes,
30 NPCs), Route 110 17, Rustboro 17, Route 117 16, Route 109 15; with the new-game flags set Slateport is 20/32. Projection (every Sapphire object): Slateport 22/32, Route 111 20, Route 117
18, Route 104 17, Routes 110/120 16, Lilycove 13, Sootopolis 11; with the old preload Routes 111/117/120 and
Slateport would have been over (33-38).

## Emerald Route 123 (route123, 2026-10-19) **[code + test]**
npc_check had Emerald's Route 123 (zone 154, and its sunny-end parts 586/550, which share its entity file) at 33/32
since Emerald v1.1: 13 people codes (the Emerald-only trainers Alberto/Fernando 358, Ed 24, Frederick 28, Davis 11,
Jonas 8 next to Sapphire's 8 codes; every one a different pokeemerald graphic, Giga Drain girl and Jacki share 15) + 18
berry trees (each can show another picture: berry planting) + the player's 2. Sapphire/Ruby: 8 + 18 + 2 = 28.
- In game (Emerald v1.1 clone + the signwarp kit, DeSmuME, `work/agents/route123/pt/r123.py`, shots
  `screenshots/route123/`): with the new-game trees (8 different pictures) the cache holds 22. With 18 different
  berries fully grown (a player who fills the route with different berries) and at least one item ball left: 32/32
  while walking (the player's sheet + 13 + 18), everything drawn. The 33rd is the player's own **Surf** sprite (also the
  bike and fishing forms, same mechanism): surfing the route's pond (402-409, 204-208), the player's sprite stayed
  standing on the shore while the empty Surf mount moved on (its code 233 found no entry); after the Bag (the field is
  made again: the people claim their entries first) the player was gone altogether, only the mount drawn. Not tested:
  riding the bike across the zone line from Route 118 (the bike's entry is taken before the zone's people spawn) should
  leave the last new code in list order without one instead: the tree at (111,13) (uid 233).
- Data fixes don't fit: all 13 people codes are different pokeemerald graphics (merging two would change a trainer's
  look); the parts copy zone 154's entity file (fixed_weather.py asserts it), so a split along them means new entity
  files and duplicated warps for one zone; the 18 trees can
  legitimately show 18 pictures. Nothing in Black 2 caps the cache at 32 but this immediate: every user is sized by it
  (`FldBlAct_CreateMatCache`, `FldBlAct_InitLoader`'s request array, the loops of ov036 0x02193728-0x02194620), and
  the billboard system under it has 64 materials.
- Fix: `patches/area2_buildings.py` apply_code sets 40 in Emerald (Sapphire/Ruby keep 32, byte-identical). Cost 160 B of
  field heap (8 x 8 B cache + 8 x 12 B request entries). A zone with <= 32 entries behaves exactly as before; only a
  zone that would have overflowed uses the new entries. Texture VRAM is still checked by npc_check (Route 123 worst
  case 294,128 of 393,216 B). ov036 stays in its ROM slot (same file positions as v1.1: no layout move).
- Tests: the v1.1 clone with an exec hook giving FldActSys_InitBlAct 40 (`cache=40`): 33/40 while surfing, the player
  riding. The real build (`tests/build_test_rom.sh`: a clean worktree of main 52d37e5 + this fix, HOENN_TEST_WARP=154,478,215,
  states from `tests/mkstates.sh`): npc_check 367 zones, 0 over (Route 123 and its parts 33/40; Sapphire/Ruby v18.0
  read 32, 0 over); with 18 different trees the pond Surf drew the player (33/40); a walk from the east end to the
  west grove (`walk=1`, ten stops; `stops=` for the east trio and Wendy) battled Kayley, Jonas, Cameron, Ed, Kindra,
  Alberto, Fernando, Frederick, Jacki, Jazmyn and Davis, had Wendy, Braxton, Miu & Yuki, Violet, the Giga Drain girl
  and the trees on screen, and found no actor without a material at any stop. Shots: `screenshots/route123/` (01-07
  v1.1, 08-10 + sheet the fixed build).

## Slateport market stalls and signs (same day)
- **Stalls** (res 347, `b2tools/models_slateport.py stall`): people are camera-facing quads at the depth of their feet
  (`FldActSys_AddBlAct` type 0 = `BLACT_TYPE_FACE_CAMERA`, billboard.c Draw) and the field camera looks down at
  **52.6 degrees** (eye 185.7 above and 142.0 south of its target, RAM, Slateport) **[test]**. So a roof point (y, z)
  hides a seller at z_s unless z < z_s - 1.307 y, and covers someone standing north of it unless z > z_a + 0.764 y
  (screen height). Seller row and the aisle row above are 48 units apart: only roofs lower than ~23 fit. The stall is
  now a low roof (eaves 13, ridge 20) over Sapphire's two awning rows; on screen it fills those rows with the seller
  in front, as in Sapphire. Before/after: `screenshots/npc_limit/02_*` (Cook, Energy Guru, Effort Ribbon woman, Doll
  clerk visible; test people in the aisles fully drawn, 04_*). Same size (2,192 B), same props.
- **Signs**: `converter/gen_map_content.py` now gives a story-scripted Sapphire sign its event and signboard model
  (152/154) when the map's scene file names it in a `ScriptEntry` comment (the Sapphire label, or `sign (x,y)`):
  Slateport's harbor (24,12) -> script 12 and shipyard (23,38) -> script 11, Rustboro's Gym sign (23,19) -> 22.
  The story json sign entries for those three (ch3a.json harbor/shipyard, ch2.json Rustboro Gym sign) are now
  duplicates (harmless: same script) and can be dropped. Read in game: 03_*.

## Testing notes
- The camera target at 0x02143c64 (emu.py's default player position) is rewritten during the frame and reads 0 at
  times; a heap copy (lowest address >= 0x02200000 holding the tile on two frames running, `tests/lib.py
  find_player`) is stable.
- Reading a sign right after `HOENN_TEST_WARP` aborted DeSmuME ("YOUR GAME IS BOGARTED", same on a ROM without these
  changes); after passing a real door it works (the Mart, `tests/t10_signs.py VIA_MART=1`).
- v13 layout (story overlay edits on): `work/emu` states (v12) don't run; mine: `work/agents/npc_limit/states/v13_*`.
