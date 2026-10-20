# Sapphire's opening in Black 2 (started 2026-10-06)

Parked at the user's request ("before you focus on the main story convert unova to hoenn using the maps you made"):
the overworld conversion comes first. Nothing here is in the default build (`rebuild_slice.sh` does not apply the
`opening` patch), so the playable slice is unchanged.

## Done and tested
- **New game starts in zone 394** (`b2tools/patches/opening.py`, `apply_code`): arm9.bin `0x15130` 427 → 394. Tested
  in DeSmuME on a fresh new game: after the intro, zone 394 loads at its header fly position and runs its scripts
  29 and 30 (a test message from `src/field_scripts/0788_truck.s` showed).
- **The player is invisible in that first map** (event_mapchange.c sets actor flag 4 before script 29), as the
  research expected. Black 2's own opening never shows the player there either: its script 30 warps away. Plan: zone
  394's fly position points at an empty (black) part of the truck chunk; script 30 plays the truck noise on the dark
  screen, then `RTReserveScript 31` + `MapChangeCore 394, 10, 0, 10, …` drops the visible player into the truck,
  where script 31 does the ride (shake, stop, door opens).
- `EvCameraShake 0, 1, 10, 30, 0, 0, 0, 0` blocked the script (no message after ~10 s): its arguments need testing
  against Black 2's own uses (`0246.s:54` = `0, 1, 3, 6, 0, 0, 0, 0`).
- Text: a page break is `{be01}\n` (Gen 3 `\p`), a scroll is `{be00}\n` (Gen 3 `\l`); a bare `{be01}` without the
  newline does not break the page.

## Built, not yet tried in the game
- `b2tools/models_truck.py` → `work/interiors/truck/`: the 5×5 truck as a Black 2 interior chunk (floor y −2, walls
  46 high with dark caps, open south side with a floor lip, as chunk 838), Plasma Frigate metal textures (map set 379:
  `in77room_01`, `in77g_kabe1`, `in77k_kabe1`, `in77i_yuka2`, `in77_wp01` as daylight), Black 2's cardboard boxes
  (interior pack 2 res 92 `box01`, 93 `box02`), collision = Sapphire's walkable tiles, exit tiles in column 4.
- Rear door = new building res 200 in interior pack 2 (`door.dae`), to hide with `BMSetVisible` when it opens.
  `BMSetVisible`'s first argument is the building's converted info type: 8 = raw info type 11 (`0274.s` hides
  `c09gate_main`, res 294, raw type 11), so the door's info record needs type 11 (notes/GEN5_MAPS.md, building packs;
  tested on the outdoor truck, 2026-10-06).
- `b2tools/rebuild_opening.sh` builds the models (ToNsbmd) and the texture sets with **`nsbtx.py merge`**.

## Still to do (in order)
1. `opening.py` `apply()`: append the truck chunk after the Hoenn chunks, matrix 35 → it, texture set 284 and
   interior building textures 2 = the merged files, interior pack 2 + res 200, zone 394 fly position (void) and
   music, entities 571 (box signs, exit triggers on `VAR_LITTLEROOT_INTRO_STATE` = 0, no NPCs/warps).
2. Scripts 30/31 (ride), exit trigger script (Sapphire `InsideOfTruck_EventScript_15FC29`: respawn
   `FieldSetTeleportZone 1`, intro state 1/2, hide flags, `MapChangeCore 389` to (171,362) boy / (180,362) girl).
3. Sounds: pick Black 2 sound effects for truck move/stop/unload/door (candidates by use: `SEQ_SE_FLD_126` with
   camera shakes, `SEQ_SE_FLD_118` after a gate animation) — the user should listen and choose.
4. ~~Moving-truck model outside the player's house~~ (done: pack 0 res 460, placed at both houses,
   `BMSetVisible 8, 170, 362, 0` / `8, 179, 362, 0`; `b2tools/models_truck_ext.py`), Mom's scenes, houses, Route 101 chase, starter
   (ov316 table `0x2C14` → Treecko/Torchic/Mudkip), Poochyena battle, lab. Intro text (Birch) later.

## Story state
`src/include/hoenn.h` (included by every field script) maps Sapphire's VAR_*/FLAG_* names to saved Black 2 ids that
no Black 2 script and no decompiled C source uses. Save layout read from arm9 (`EventWork_GetFlagBytePtr`,
`EventWork_GetWkPtr` at `0x0201924c`/`0x02019294`): works 0x4000–0x41AE (431, 2 bytes each, then the flags at
offset 0x35E), saved flags 0–3063 (383 bytes), flags ≥ 0x4000 are 64 unsaved temporary flags. Free runs: works
0x404E–0x406F, 0x4156–0x415F, 0x4197–0x41AE; flags 2049–2239, 2282–2348, 2350–2399, 2561–2611, 2816–2962,
3001–3063.

## Texture sets: lossless merge (`b2tools/nsbtx.py`)
CTRMap's NSBTX writer (used by `MergeNsbtx.java`) re-encodes every texture: A3I5 shadows (`h_kage`, `in40_kage`)
become A5I3 with small alpha changes, and `hh_ashiato` (footprints) lost pixels (alpha 255 → 0). `nsbtx.py merge`
keeps every byte of the base set and appends copied textures/palettes byte for byte; its dictionary trees are built
exactly like the game's (Patricia trie, head key all zeros, nodes in pre-order — byte-identical on 118 game
dictionaries; `merge(base, [])` reproduces 137 game texture sets exactly). The game's lookup rule (descend while the
node's bit index decreases, test bit `b` = byte `b>>3`, bit `b&7`) finds all 10,406 names in those dictionaries.
`nsbtx.py FILE OUT_DIR` decodes any set to PNGs (pixel-identical to apicula's export).

## Scenes (2026-10-06, evening): truck → Littleroot → houses → rival → north exit
User request: "add the truck ride and house scenes next". Sapphire's scripts are followed step by step; every
scene is a Black 2 script in the zone's own file. Rooms: the interiors agent (notes/INTERIORS.md, zone tile =
Sapphire tile + room offset); story ids: `src/include/hoenn.h`.

| Where | Script | Sapphire source |
|---|---|---|
| Truck 394 (`scenes/truck.inc` in 0788) | 30 new-game flags + warp in, 31 the ride (dark, bobbing `EvCameraShake`, stop jolt, door), 20 exit trigger (state 1/2, hide flags, `MapChangeCore 389` + reserve 31) | `InsideOfTruck`, `field_special_scene.c` |
| Littleroot 389 (0778) | 31 arrival: hop off, door opens (`BMCreateHandleByGPos 0x8020, 1, x, z` + `BMHndAudioVisualAnmPlay 0/1`), Mom out, speech, both in, warp + reserve 20 | `GoInsideWithMom` |
| Littleroot 389 | 20/21 twin stops you at the north exit (state 0), 22 "somebody has to go help" (state 1), 5 twin talk, 9 twin position (`ObjInitNPCGPos`) | `NeedPokemonTrigger*`, `GoSaveBirchTrigger`, `Twin` |
| House 1F 390/392 (`scenes/players_house_1f.inc`) | 20 moving in, 21 go set the clock, 22 TV report, 23 rival's mom, 24 init (Mom's spot), 25 mat trigger, 26 Mom, 27/28 movers, 29 rival's mom | `players_house.inc`, `*_1F/scripts.inc` |
| House 2F 391/393 (`scenes/players_house_2f.inc`) | 20 wall clock (sets it, Mom comes up), 21 the rival, 22 fade in after the push upstairs, 24 init | `*_2F/scripts.inc` |
| Map scripts | `0781/0785` (zone init 24 + conditions: intro state 5 → 21, 6 → 22, houses var 1 → 23), `0783/0787` (init 24), `0789` (none) | OnTransition / OnFrame |

Black 2 facts used (all from Black 2's own scripts or code, tested where marked):
- Movement lists must be **word-aligned** (`.balign 4` before them): an unaligned list crashed the game (tested).
- Movement codes (Gen 4 numbering, from Black 2 scenes): 0-3 face, 12-15 walk, 16-19 walk fast, 32-35 walk in place,
  51 jump in place right, **55 jump one tile right (tested)**, 63 delay 8, 69 invisible, 71/72 lock/unlock facing,
  75 "!" balloon.
- `EvCameraShake x_amp, y_amp, period, cycles, x_decay, y_decay, decay_after, decay_every` (ov036
  `s0148_EvCameraShake` → `FieldCameraShakeTask`): blocks until done; the field runs at 30 fps, so period 10 ×
  30 cycles = 10 s (why the first test seemed to hang).
- `ObjInitNPCGPos index, dir, x, y, z` = Gen 3 `setobjectxyperm` (zone init). **index = the NPC's position in the zone's
  NPC list, not its uid** (`SetZoneNPCLocation`, eventdata_system.c:255; tested: index 1 moved the fat man). `FlagReset f` + `ActorAdd uid` =
  `addobject`; `ActorDelete` + `FlagSet` = `removeobject`.
- Every scripted warp is `FadeOutBlack; RTReserveScript n; FadeWait; MapChangeCore …` and script n of the new zone
  fades in (Black 2's own pattern); `MapScriptConditions` scenes start after a normal warp's fade-in.
- Wall clock: Black 2 has no clock screen (it keeps the DS time): "The clock is stopped…", a short fade, then Mom.
- Sounds are stand-ins (truck `SEQ_SE_FLD_126`/`155`, door `SEQ_SE_KAIDAN`): the user should pick.

Tested 2026-10-06 (DeSmuME, fresh boot, boy): truck ride → step out → arrival (only your truck shows) → moving in →
clock + Mom → TV report → May's mom → May upstairs (walks around you to the stairs) → twin's request at the north
exit; the trucks are hidden after you go in. Build v9.
Girl's path tested 2026-10-19 (littleroot_may, DeSmuME, new games as May on v18.0, Emerald v1.1 and the fix build;
b2tools/release_kit/mk_boot.py's 9th argument `girl`): truck at May's house (east), Mom, clock, TV report, house signs
(fixed then), Brendan's mom ("Our son is upstairs"), Brendan at his notebook / Emerald's Poke Ball meeting, his PC's
e-mail, Mom's Running Shoes outside May's door and the manual on May's table: all as Sapphire / Emerald.
Bedroom PC (user, 2026-10-19): before the first Pokémon (flag 2401) the player's own PC is Gen 3's Player's PC with its one
Potion only (scenes/players_house_2f.inc L_PC_NoPokemon: Withdraw Item gives it once, FLAG_RECEIVED_PC_POTION, then
"There are no items."; Turn Off / B), never Black 2's boxes; with a Pokémon, Black 2's PC (global 10090) as before.
Fly to Littleroot lands in front of your own house since littleroot2 (2026-10-19; notes/TOWN_MAP.md "Fly to Littleroot by sex").
A blackout or Teleport with the home return point (before the first Center, after the Hall of Fame) wakes you in your own
bedroom at Gen 3's heal spot (5,3), facing down (littleroot2; notes/TOWN_MAP.md "Teleport home"); until then the 1F (6,8)
and, for Teleport, Littleroot between the houses. Emerald: the Hall of Fame now hides the Lilycove rival (flag 675, the
object's; it set the unused 445 before) and Lilycove's zone init hides it for saves already cleared.
The rival in their room (littleroot2): Sapphire/Ruby at the notebook only until the Route 103 battle
(FLAG_DEFEATED_RIVAL_ROUTE103), afterwards at the data's tile = the PC (home again after Lilycove, and after the Hall of Fame);
hidden from the first meeting until Lilycove. Emerald: no notebook rival; at the PC after the meeting, out from the Route 101
rescue, home again after the Lilycove battle (the zone init clears FLAG_HIDE_*_RIVAL_BEDROOM when FLAG_MET_RIVAL_LILYCOVE is
set and the game is not cleared: the shared Lilycove scene clears only Sapphire's flag), hidden after the Hall of Fame.
Open: stand-in sounds; Black 2 fast-walk codes (the twin walks at normal
speed); a hidden truck can reappear if its chunk reloads without a field load (walking far away and back); the
twin should wander again after Birch's rescue; Littleroot's Mom, Norman and the S.S. Ticket scenes come later.

## Truck: the back door opens (opening_polish, 2026-10-06)
User (v11): "when the moving truck finishes moving there's no door opening or indicator of where to go". Sapphire's
`Task_HandleTruckSequence` swaps the exit column (4, 1..3) to the bright `ExitLight_*` metatiles with `SE_TRUCK_DOOR`.
- `b2tools/models_truck.py`: the closed door is now part of the room's terrain (two metal leaves + a rib in the doorway);
  building res 200 (interior pack 2, **info type 11**) is the OPEN door: Black 2's cave-exit light `in14_exit_a` (map
  set 295, its white middle) filling the doorway, and the same set's `in14_light_a` (A5I3 white gradient, 93% → clear)
  on the floor of the exit column. Converted unlit (`ToNsbmd --vcol`, white vertex colours; lit by normals it came out
  grey-beige). `rebuild_interiors.sh` converts it that way. `patches/interiors.py`: extra models take a `type`.
- `scenes/truck.inc` Script_31: `BMSetVisible 8, 13, 10, 0` on the black screen at the start of the ride, `… 1` with
  the door sound. Open is the default (like Sapphire's map), so Continue / any field reload in the truck shows it open.
  One hide + one show only (`FieldChunkPropHolder_SetVisible` keeps a single saved index).
- Tested (DeSmuME): cold boot through the ride (door shut while riding, opens at the end, walk out → Littleroot);
  `base_truck.dst` + Bag (field reload) → open; save in the truck, reboot, Continue → open.
- Found while testing: **Continue hung on a blank top screen** in every build since a1dc520 (also in the truck and in
  Littleroot on v11): `patches/hoenn_intro.py` made the Continue entrance transition type 0 but left its 5th argument
  0; every type-0 caller passes 1, and with 0 `func_ov036_021b8d24` skips `FieldG3D_SetLCDConfigKeepBGs` (the
  season card did that itself). Fixed there (ov035 `0x0217cd4a` `movs r0,#0` → `#1`); tested in the truck and in
  Littleroot. Same ROM file layout.
