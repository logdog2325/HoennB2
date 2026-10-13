# Sapphire's opening in Black 2, and replacing character sprites (researched 2026-10-06)

What it takes to rebuild Sapphire's opening (truck → Littleroot → Route 101 → lab) inside Black 2, and how Black 2
stores the character sprites we will edit. Everything was checked against the decomp (`external/pokebw2`, written
`bw2/` below), its built binaries (`bw2/build/b2_us/build/*.bin`, `bw2/build/b2_us/files`) and pokeruby
(`external/pokeruby`, `ruby/`). Disassembly came from `tools/dsd dis` into a scratch folder. Tags: **[code]** read from
code, **[bytes]** checked in the game files, **[test]** checked offline with a script, **[inferred]** fits the
evidence but not traced. Nothing here has been tried in the emulator yet.

Two corrections to what we assumed before:
- **People sprites in `a/0/4/8` are not BMD0 models.** 968 of its 975 files are `BTX0` texture sheets (one 32×32 or
  64×64 texture per frame); only 7 are `BMD0` (3D objects such as a boulder). The billboard itself is made by the
  engine. **[bytes]**
- **`VMJumpIf CMP_STACK, L` jumps when the condition is FALSE**, not TRUE as `bw2/docs/scripts.md` and the comment in
  `bw2/include/constants/field_script.h:14` say. The handler jumps when the popped value `!= 1`
  (`bw2/src/ov012/scrcmd_vm.c:291-303`), and the game's own scripts only make sense that way (see the starter code
  below). Our scripts have no conditionals yet, so nothing is broken, but every port must follow the handler.

## 1. Short answers

| Question | Answer |
|---|---|
| Where does a new game start? | Code: the new-game event loads **zone 427 (Aspertia City)** at that zone's header fly position (`LoadAspertiaCitySpawnInfo`, one literal `0x1ab` in arm9), runs global script 9600, then **scripts 29 and 30 of whatever zone it loaded**. Aspertia's script 30 plays Mom's phone scene and warps to the house (zone 428). |
| How do we start in Littleroot / the truck? | Best: change that one 4-byte literal (arm9.bin offset `0x15130`, 427 → our first zone) and give that zone's script file scripts 29 and 30. No-code fallback: rewrite Aspertia's scripts 29/30 to warp straight away (Aspertia flashes on screen). |
| Starter screen | Script command `callPoke3Select var` opens overlay 316 (`psel`). It returns 0/1/2; **the script picks the species**, and the screen shows the three species from a 6-byte table in overlay 316 (`ef01 f201 f501` = 495/498/501). Change both → Treecko/Torchic/Mudkip at Lv 5 with `PokePartyAdd var, species, 0, 5`. |
| Lv 2 Poochyena battle | `CallWildBattle SPECIES_POOCHYENA, 2, flags` then `WildBattleIsVictory`, `CallWildBattleEnd` / `CallWildLose`. |
| Player sprites | Nate: object codes **231** walk+run, **232** bike, **233** surf, **234-239** special actions (239 = fishing, 64×64). Rosa: **240-248**. Hilbert/Hilda (BW1 heroes) have a full set too: 1-6, 136-141, 156-161. |
| Hoenn characters already in B2 | Trainer (battle) sprites: Roxanne 118, Brawly 119, Wattson 120, Flannery 121, Norman 122, Winona 123, Tate 124, Liza 125, Juan 126, Steven 139, Wallace 140. Overworld: Roxanne..Juan **268-276**, Steven **287**, Wallace **288** — but these PWT sprites have **no back view and no front walking frames** (drawn as an X). No Brendan, May, Birch, Wally, Hoenn Mom, Aqua/Magma, Hoenn Elite Four. |
| Writing edited sprites back | No Nintendo tools needed. Overworld sheets: rewrite the 4bpp pixels and 16-colour palette **in place** (same size) — tested offline on all 348 people sheets. Battle sprites: rewrite a 256×128 4bpp bitmap + palette and LZ11-compress again — tested offline. |

## 2. New game: where the first map is decided

The chain, with every step from code **[code]**:

1. Start menu → `GameStart_NewGame` (`bw2/src/ov162/game_start.c:166`). `NewGame_Main` runs the intro (overlay 294),
   name entry, the intro again, then **rival name entry** (Hugh, `game_start.c:278`), and the intro's end.
2. `NewGame_Exit` creates the game system with `GAME_ENTRYPOINT_OPENING` and zone 0 (`game_start.c:336`).
3. `CreateGameEntryPointEvent` → `EventGameOpening` (`bw2/src/ov035/event_mapchange.c:148`, `:159`): season banner
   (`:173`), **3D demo 5** (`:177`), then `EventFieldFirst` (`:181`).
4. `EventFieldFirst_Create` (`event_mapchange.c:249-270`):
   - `LoadAspertiaCitySpawnInfo(&spawn)` (`:255`). This is `LoadZoneSpawnInfoCheckRail(spawn, 0x1ab)` — **zone 427** —
     at arm9 `0x02019128`; the zone number is the literal word at **`0x02019130`**, which is **offset `0x15130` in
     `bw2/build/b2_us/build/arm9.bin`** (value `ab 01 00 00`, checked) **[bytes]**. The position is the zone header's
     fly landing x/y/z (`LoadZoneFlyPosToVecFx32`; Aspertia: fly_x 47, fly_z 762). The only caller found is this one
     (searched main, ov012, ov035, ov036).
   - Overlay 279 (`bw2/src/ov279/new_game.c`): `InitItemBag` gives the Xtransceiver (by gender) and the Pal Pad;
     `InitDreamRadarFlagSave` sets Dream Radar values.
5. `EventFieldFirst_Callback` (`event_mapchange.c:205-247`):
   - `FieldScript_CallPlayerInitSetup` (`:213`) runs **global script 9600** (`bw2/src/ov012/script_sys.c:202`).
   - Loads the zone and places the player (`:214-215`).
   - `SetActorFlag(player, 4)` (`:231`), then runs **script 0x1d = 29** of the loaded zone (`:232`), fades the map in
     (`:236`), runs **script 0x1e = 30** (`:240`). Script ids below the global ranges index the zone's own script file
     (`FieldScript_ResolveSCRID`, `script_sys.c:398-427`).

What the intro sets (so a Hoenn start can copy or replace it):

| Where | What |
|---|---|
| Global script 9600 = `bw2/data/field_scripts/1242.s` Script_1 (`:8-13`) | `L_0024` (`:15-207`): **190 `FlagSet`s** (mostly flags that hide NPCs until the story shows them) and `WorkSetConst 0x4165, 1`; `L_0324`: `Cmd_0209` calls by version and gender; **`FieldSetTeleportZone 18`** (blackout/respawn = Aspertia Pokémon Center); **`MoneyAdd 3000`** (same as Sapphire's 3000). |
| Aspertia `0854.s` Script_29 (`:1813`) | `ActorNew 45, 763, 3, 251, 357, 0` — creates Mom (object code 357, the version with phone frames) as actor 251. |
| Aspertia `0854.s` Script_30 (`:1820-1859`) | Mom's phone call with Juniper, Mom walks to the door (`ActorWalkRoute`), door animation (`BMCreateHandleByGPos` + `BMHndAudioVisualAnmPlay`), then `RTReserveScript 17` and **`MapChangeCore 428, 14, 0, 3, 0`** (zone, x, y, z, dir). |
| Player's house `0856.s` Script_17 | Runs on arrival because it was reserved: `FlagReset 740` (Mom's NPC in zone 428 has spawn flag 740, which script 9600 set), Mom walks in (stairs sound), "I'm home!". |
| Aspertia map scripts `0855.s` | Scene conditions on var **0x40a1** (Aspertia's story state: 3, 4, 6 …), 0x40a8, 0x4115. |
| ov279 code | Xtransceiver + Pal Pad in the bag. |

The B2 starter scene (Bianca, Aspertia lookout) also sets: var **0x4030** = starter index 0/1/2 (`0854.s:378/390/398`),
`Cmd_0209 8, 3/1/2` (grass/fire/water), flag **2401** right after the Pokémon is added (`:413`; read by
`func_ov036_021a01c4`, meaning not traced) and flag **2402 = Pokédex** (`:438`; the start menu shows the Pokédex when
flag `0x962` is set, `bw2/src/ov162/startmenu.c:1139`).

### How to start in Littleroot, in the truck or in the house

**Option A (recommended): one 4-byte code patch.** Change arm9 offset `0x15130` from 427 to the first zone. The game
then loads that zone at its header fly position and runs **its** scripts 29 and 30. Because the player actor gets flag
4 before script 29 and B2's own opening never shows the player before warping (Script_30 ends in `MapChangeCore`),
script 30 should end with `RTReserveScript N` + `MapChangeCore` to the real start tile; the reserved script N then
plays the scene. That keeps B2's own pattern. For the truck:
- Make an "inside of truck" interior in a zone Littleroot does not need. Nuvema has three houses with two floors
  (390/391, 392/393, 394/395) and the lab (396); Littleroot uses 390-393 and 396, so **394 or 395** is free (their
  matrices 35/36, interior area 284).
- Point the patch at that zone; script 29 can be empty; script 30 = `MapChangeCore <truck zone>, x, 0, z, dir` with a
  reserved script that does Sapphire's `Task_HandleTruckSequence` (`ruby/src/field_special_scene.c:182-265`): dark
  screen, truck noise, `EvCameraShake` (command 328, 8 arguments, see section 4), stop, door opens (fade in).
- The truck's exit is Sapphire's trigger `InsideOfTruck_EventScript_15FC29` (`ruby/data/maps/InsideOfTruck/scripts.inc`):
  set respawn, intro state, hide flags, then warp to Littleroot **(3,10) boy / (12,10) girl = global tiles (777,746) /
  (786,746)** (Littleroot sits at matrix cell (24,23), chunk tiles 6..25 × 0..19, notes/LITTLEROOT.md).
- Scripts 1-28 of that file must exist (padding stubs) so ids 29/30 resolve.
- Sapphire's `setrespawn` → **`FieldSetTeleportZone 1`**: teleport values are 1-based indexes into
  `RESPAWN_ZONE_INFO` (`bw2/src/ov012/respawn_zone.c:139-144`, `:109-119`); entry 0 is zone **390 at (6,8), town
  389** = Nuvema's hero house = our Littleroot player's house. It is not set automatically on entering (only entries
  with the first bit set, the Pokémon Centers, are; `event_mapchange.c:1403-1406`).

**Option B (no code): data only.** Keep the spawn in Aspertia and replace Aspertia's Script_29 (empty) and Script_30
(`FadeOutBlack`, `RTReserveScript N`, `MapChangeCore <first zone>…`). Costs: Aspertia's map loads and fades in for a
moment, and Aspertia's script file (854) is no longer Unova's. Our test harness starts from Aspertia
(`test_door_to_nuvema`, notes/TESTING.md), so this also changes the test routes.

**Either way:** the season banner and 3D demo 5 still play first (skipping them is another ov035 code change), the
intro still shows Juniper/Cinccino/Nate/Rosa and asks for a rival name (overlay 294 and `game_start.c:278`; not
researched), and the bag still gets the Xtransceiver/Pal Pad (`ItemSub` in our first script can remove them).
Savestates cannot test this: a new game needs a fresh boot through the intro (~70 s, `make_states.py`).

## 3. Starter choice

**B2's flow** (`bw2/data/field_scripts/0854.s:359-460`, Bianca at the Aspertia lookout):

```
    WorkSetConst 0x8024, 0
    FadeOutBlackQ / FadeWait / FieldClose
    callPoke3Select 0x8024          // 0, 1 or 2
    FieldOpen / FadeInWhiteQ / FadeWait
    (0 → WorkSetConst 0x4030, 0; Cmd_0209 8, 3; species 495)   // Snivy
    (1 → 0x4030 = 1; Cmd_0209 8, 1; species 498)               // Tepig
    (2 → 0x4030 = 2; Cmd_0209 8, 2; species 501)               // Oshawott
    SystemMsg 43, 1                 // "{player} chose {species}!"
    PokePartyAdd 0x8010, 0x8025, 0, 5    // result, species, form, level
    FlagSet 2401
    … nickname offer (YesNoWin), nickname loop L_06C6 (:465-520), Pokédex (FlagSet 2402)
```

`callPoke3Select` = command 339, handler `s0153_callPoke3Select` (`bw2/src/ov012/scrcmd_proc.c:321-330`): it only
passes a result pointer to overlay 316 (`OVERLAY_PSEL`, `bw2/include/app/psel.h`). **The screen's three species are a
table inside overlay 316**: `data_ov316_0219fa94` = `ef 01 f2 01 f5 01` (495, 498, 501), offset **`0x2C14`** in
`bw2/build/b2_us/build/arm9_ov316.bin` (base `0x0219CE80`) **[bytes]**. The overlay uses it for the battle sprites
(`func_ov316_0219d534` → `MakePokeGraArcHandle`), the name (`func_ov316_0219e824` → `WordSet_LoadSpeciesName`) and the
cry (`func_ov316_0219f100` → `PokeVoice_Play`) **[code]**. The captions come from script text file 169 (Aspertia's)
lines 35-37 "The Water/Fire/Grass-type Pokémon\n{species}" via a per-ball table (37, 36, 35) — **Grass/Fire/Water
order already fits Treecko/Torchic/Mudkip**. The touch circles (`data_ov316_0219fae0`) put ball 0 at x 60 (left),
1 at 128, 2 at 200 — the same left/middle/right order as Sapphire's bag (`ruby/src/starter_choose.c:50`, Treecko,
Torchic, Mudkip).

**To make it Treecko/Torchic/Mudkip at Lv 5:**
1. Overlay patch: `arm9_ov316.bin` offset `0x2C14` → `fc 00 ff 00 02 01` (252, 255, 258).
2. Our script: same flow with `SPECIES_TREECKO/TORCHIC/MUDKIP` (`bw2/include/constants/species.h:258-264`), keep
   `0x4030` = 0/1/2 (Sapphire's `VAR_STARTER_MON` uses the same order) and `Cmd_0209 8, 3/1/2` by type, then
   `PokePartyAdd var, species, 0, 5`. `PokePartyAdd` makes a Poké Ball, random gender/ability, no item
   (`bw2/src/ov012/scrcmd_pokemon.c:421-447`), like Sapphire's `ScriptGiveMon(starter, 5, ITEM_NONE…)`.

Sapphire gives the Pokémon inside the C code right after the choice and starts the Poochyena battle at once
(`ScrSpecial_ChooseStarter` → `CB2_GiveStarter` → `CB2_StartFirstBattle`, `ruby/src/battle_setup.c:865-898`); in B2
the same order is just consecutive script commands. The psel screen (three balls on a 3D stand, picture and cry of
the chosen one, "Is this the Pokémon you want?") is the closest B2 thing to Birch's bag; I recommend it.

**The screen's own graphics (a/2/0/2, traced in ov316; `b2tools/psel_art.py`, patch `starters`, 2026-10-06):** the
coloured picture shown when a ball is picked is NOT the species' sprite: it is stored per ball (NCGR 12/13/14 = 2x
redraws of Snivy/Tepig/Oshawott, cells 21-23, anims 25-27, palettes 0/2/4 colour + 1/3/5 dark, faded into OBJ
palette slot i, which the small silhouettes (species stills from the 0x2C14 table) share). Now Treecko/Torchic/
Mudkip's Black 2 front stills at 2x (Scale2x, no new colours) with their own palettes. The bottom screen is a 3D scene
(files 34-41): model 34 `psel_s02` = Bianca (14 shapes, materials `bell_*`) holding the case; her shapes' SBC draw
commands are NOPed (the case, the room and the balls stay). No Birch: she is a skinned 3D model, no 2D picture fits.
Other files (backgrounds 15-20, ball ring 17/24/28, curves) and texts (file 169, lines 35-44) have no Unova content.

**No-code fallback:** a `ListMenu` with the three names plus a yes/no, then `PokePartyAdd` — works without patching
overlay 316, but shows no picture. No script command that shows a Pokémon picture was found by name.

## 4. Script commands we need

Macros are in `bw2/include/asm/field_script.inc`; argument kinds from `bw2/tools/scripts/field_commands.json`;
argument names from CTRMapV 1.4.1's script library (`SDK5-B2W2-Generated.lib` → `yml/Base.yml` inside
`tools/ctrmap-plugins/CTRMapV-1.4.1.jar`), which agree with the game's own uses below.

| Need | Command (id) | Arguments | Evidence |
|---|---|---|---|
| Scripted wild battle | `CallWildBattle` (372) | species, level, flags | `s0174` (ov036 `0x021ae394`) → `EventWildBattleCall_CreateStatic(enc, species, level, 0, flags)`; legendaries use flags 1 (`0032.s:252`). **Poochyena: `CallWildBattle SPECIES_POOCHYENA, 2, 0`** (261). |
| …with form | `CallWildBattleEx` (663) | species, level, form, flags | `1168.s:31` |
| …result | `WildBattleIsVictory var` (375), then `CallWildBattleEnd` (373) on a win or `CallWildLose` (374) on a loss | | pattern `0032.s:252-266`; `scrcmd_game_state.c:597-622` |
| Give a Pokémon | `PokePartyAdd var, species, form, level` (268); `PokePartyAddEx` (270) adds ability, gender, shiny, item, ball | | `scrcmd_pokemon.c:421-497` |
| Nickname | `CallPokeNameInput var, partySlot, transition` (261) | | loop in `0854.s:465-520` (checks `PokePartyGetParam var, 0, 117` = 1 when a nickname was given) |
| Flags | `FlagSet` (35) / `FlagReset` (36) / `FlagGet flag, var` (37) / `VMStackPushFlag` (16) | | |
| Vars | `WorkSetConst var, value` (40), `WorkSet`, `WorkAdd`, `WorkCmpConst` + `VMJumpIf CMP_EQ…` | `0x4000+` saved, `0x8000+` script-local | `bw2/docs/scripts.md` |
| Player gender | `TrainerCardGetSex var` (225): **0 = boy, 1 = girl** | | `scrcmd_game_state.c:150-159`; `bw2/include/save/player_info.h:9-10` |
| Gendered line | `ActorMsgGendered MSGFILE_SCRIPT, msgBoy, msgGirl, actor, pos, type` (72) | | `0854.s:317` |
| Yes/No | `YesNoWin var` (71): **0 = Yes, 1 = No** | | `0854.s:418-424` (0 → nickname) |
| Multiple choice | `ListMenu_AnchorTopRight x, y, default, cancellable, var` (or `…TopLeft`, `ListMenuInitCommon` = text from common file 410), `ListMenuAdd optionMsg, hintMsg (65535 none), value`, `ListMenuShow`, then read `var` | | `0086.s:144-150` |
| Message | `ActorMsg MSGFILE_SCRIPT, msg, actor, pos, type` (60) | | Littleroot already uses signs |
| Move an NPC | `ActorCmdExec actor, Movement_X` (100) + `ActorCmdWait` (101); `ActorWalkRoute actor, x, z, flags, acmd, pathfinding` (591; flags 1 = ignore NPCs, 2 = ignore collision) | | `0854.s:1823-1849` |
| Place/create/remove NPC | `ActorSetGPos actor, x, y, z, dir` (109), `ActorNew x, z, dir, actor, objCode, moveCode` (105), `ActorAdd`/`ActorDelete` (107/108) | | `0854.s:1814`, `0856.s` Script_17 |
| Warp from a script | `MapChangeCore zone, x, y, z, dir` (196); `RTReserveScript id` (33) before it runs that script after arrival | | `0854.s:1853-1855` |
| Respawn point | `FieldSetTeleportZone n` (217), n = 1-based `RESPAWN_ZONE_INFO` index | | section 2 |
| Heal party | `PokePartyRecoverAll` | | `1242.s` Script_2 |
| Camera shake | `EvCameraShake` (328, 8 values: intensity H/W, loop length, count, decay X/Y, decay start, step) | | CTRMapV `Base.yml` 0x148 |
| Door animation | `BMCreateHandleByGPos var, …, x, z` + `BMHndAudioVisualAnmPlay var, 0` + `BMHndAnmWait var` | | `0854.s:1841-1843` |
| Running Shoes | `GiveRunningShoes` | | `1242.s:253-255` |

Rules that matter when porting Gen 3 scripts:
- **Directions:** 0 up, 1 down, 2 left, 3 right (`bw2/include/field/field_actor.h:12-16`).
- **Map-local flags/vars are wiped on every zone init:** flags 0-0x63 and work `0x4000-0x401f`
  (`FieldScript_ResetMapLocalEvents`, `script_sys.c:197-200`). Story state must live elsewhere.
- **Map script table types** (`script_sys.c:232-281`, callers `bw2/src/ov036/fieldmap.c:403-412`, `:1087`,
  `event_mapchange.c:1411`): `MapScript 2` runs on zone init (every map change, also walking across a zone edge) ≈
  Gen 3 `ON_TRANSITION`; `MapScript 3` on a new field load; `MapScript 4` on reload (return from battle/menu)
  **[inferred from the flag name]**; `MapScriptConditions` (var, value, script) start a scene when you enter ≈ Gen 3
  `ON_FRAME_TABLE`.
- **Coord triggers** (`ruby` `coord_events` with var/value) map to zone triggers (`scriptId, workValue, workId`,
  notes/GEN5_MAPS.md section 5).
- **Dynamic sprites:** NPC object codes **162-177** read their real code from vars **`0x4020-0x402F`**
  (`GetWKOBJCODENPCOBJCODE`, ov012 `0x02167fc8`: code + `0x3F7E`); B2 sets them in map scripts (`WorkSetConst 0x4020,
  …`, 68 uses). This is the way to show May to a boy and Brendan to a girl from one NPC entry (Sapphire's
  `Common_EventScript_SetupRivalGfxId`).

**Movement data:** `Move action, count` … `MoveEnd` (u16 action, u16 count; `ACMD(code, count)` in
`bw2/include/field/field_acmd.h:9`). Confirmed: **0x0C-0x0F = walk one tile up/down/left/right at normal speed**
(`ACMD_QUEUE_WALK_N/S/W/E_8F` in ov012 = `0x1000c..0x1000f`) **[bytes]**. The table `ACMD_DIR_LUT` (ov036
`0x021cc8f8`) lists 37 groups of four direction-variants (0-3, 0x0C, 0x58, 0x14, 0x10, 0xA7, 0xA3, 0x04, 0x08, 0x18,
0x1C … 0x9B) **[bytes]**; its layout matches Gen 4's numbering (0x00 face, 0x04/0x08 slow walks, 0x0C normal,
0x10 fast, 0x14 faster, 0x20 walk in place, 0x4B "!" bubble) **[inferred]** — Sapphire's `walk_fast_*` would be
0x10-0x13. Safer: copy the code from a B2 script that visibly does the same thing, then check in the emulator.

## 5. Sprites

### 5.1 Overworld (field) sprites: `a/0/4/7` table + `a/0/4/8` sheets

- **`a/0/4/7`** (`ARCID_MMODEL_TBL`) = one file: `u32 count` (1008) then 1008 records of **0x1C bytes**
  (`FieldActorConfig`, `bw2/include/field/field_actor.h:33-55`): uid, entityType, sceneNodeType, shadow, footprint,
  reflections, billboardSize, spriteAtlasSize, spriteControllerType, gender, collision w/h, position offsets, then
  `res1` (file in `a/0/4/8`), `res2`, three animation ids, padding. Size 4 + 28×1008 = 28228 checked **[bytes]**.
- **Object code → record** (`GetIndexOfObjID`, arm9 `0x0200fe34`) **[code]**: codes 0-376 → record = code; codes
  `0x1000-0x126B` (Pokémon) → code − `0xE87`; `0x2000-0x200A` → code − `0x1C1B`; anything else → record 10.
- **`a/0/4/8`** (`ARCID_MMODEL_GRA`): 968 `BTX0` sheets (entityType 1, billboards) + 7 `BMD0` (entityType 0/2, 3D
  objects). A sheet holds one texture per frame named `t4x4xN.k` (32×32, 4×4 tiles, N frames) or `t8x8xN.k` (64×64),
  **4bpp 16-colour, colour 0 transparent, one palette `t4x4xN`** **[bytes]**.
- **Frame layout = `spriteControllerType`** **[bytes, by looking at the sheets]**: type 3 = 12 frames (up, down,
  left, right × stand + 2 steps; 161 people); type 2 = 7 frames (up, up-step, down, down-step, left + 2 steps, right
  mirrored; 99 people); type 1 = the player's 24 frames (walk + run); types 5/6 surf/bike; 13/14 = Pokémon (6/8
  frames); the rest are one-off sheets (e.g. 32 = Mom 357 with phone frames). `spriteAtlasSize` grows with frame
  count (21/22/23 for 32 px, 30/31 for 64 px) **[inferred]**.

**Player codes** (`PLAYER_SPRITE_MAP`, ov036 `0x021cfc10`, read by `FieldPlayer_GetObjCodeByForme(sex, forme)`)
**[bytes]**:

| Form | Nate | Rosa | Sheet |
|---|---|---|---|
| 0 walk + run | 231 | 240 | 24 frames (12 walk, 12 run) |
| 1 bike | 232 | 241 | 16 |
| 2, 3 surf | 233 | 242 | 4 (sitting) |
| 4-9 special | 234, 235, 236, 238, 239, 237 | 243, 244, 245, 247, 248, 246 | 234 raise arm/item (2), 235 (2), 236 (5), 237 throw Poké Ball (4), 238 arms out, probably catwalk balance (16), 239 fishing (12, 64×64). Which action uses which is not traced. |

Hilbert and Hilda (BW1 heroes) have the same set as NPC codes: **1/2/3 and 4/5/6** (walk/bike/surf, controller types
1/6/5), **136-141** and **156-161** (special actions). No zone NPC and no `ActorNew` in the scripts uses 1 or 4
(checked); code references were not checked.

**NPC codes we will use** (identity from the zones and dialogue that use them) **[bytes]**:

| Code | Who | Evidence |
|---|---|---|
| 251 | Mom (Nate/Rosa's), type 2 | zone 428 NPC script 4 "out looking for Bianca?" |
| 357 | Mom with phone frames | `0854.s:1814` |
| 104 | Cedric Juniper (male professor), type 3 → **donor for Birch** | Nuvema lab NPC script 7 "Cedric: Hey" |
| 105 | Aurea Juniper | Nuvema lab NPC script 6 "Professor Juniper: Why, hello!" |
| 249 | Bianca | Aspertia NPC 2 |
| 223-230 | Unova Gym Leaders (Cheren, Roxie, Burgh, Elesa, Clay, Skyla, Drayden, Marlon) | PWT table `a/2/4/7` records 0-7 |
| 8, 25, 12, 10 | twin, fat man, boy, youngster (already in Littleroot/Route 101) | notes/LITTLEROOT.md, ROUTE101.md |
| **4390** | **Poochyena** (6 frames) | Pokémon table `a/2/0/8` (LZ11; records `species, sex(2 = any), form, objCode`, read by `LoadTPokeData`/`GetFieldPokemonMMdlLUTIndex_`, arm9 `0x020303d8`/`0x0203047c`). Treecko 4381, Torchic 4384, Mudkip 4387, Zigzagoon 4392 |
| 110 / 216 | Poké Ball on the ground | sheet |

**Hoenn overworld sprites that exist** (PWT table `a/2/4/7`: 128 × 16-byte records, `u16 ?, objCode, trainer
class/id, ?`; checked visually) **[bytes]**: Roxanne 268, Brawly 269, Wattson 270, Flannery 271, Norman 272,
Winona 273, Tate 274, Liza 275, Juan 276, Steven 287 (class 177), Wallace 288 (class 178). (252-267 Kanto/Johto,
277-284 Sinnoh, 285 Blue, 286 Lance, 215 Cynthia, 97 Alder.) **All PWT sprites have placeholder X frames**: frames
0, 1, 3 of 7-frame sheets and 0-2, 4, 5 of 12-frame sheets — no back view, no walking toward the camera. Used as
Hoenn NPCs (Norman in Petalburg, Steven in Dewford/Granite Cave, Wallace) they needed those frames drawn: done for
the ten Hoenn uses (268-275, 287, 288; Juan 276 is unused) by `b2tools/sprite_pwt.py` (2026-10-07): the back view
from the sheet's own front frame (face turned into the back of the head, front of the clothes into their back, a few
hand-placed pixels: Wattson's white back hair, Winona's cap and locks, Wallace's hat and hair), the steps as Black 2's
own NPC sheets pose them (Cedric 104, Mom 251: body one pixel higher, the leading leg two pixels longer, the other
raised; type 2 sheets have one step, which the game mirrors). Review `screenshots/sprites/pwt_frames_review.png`.
**[test: Steven (287) walks down, right, up and left from Littleroot's test sign, screenshots/tests/pwt_steven_walk.png]**

### 5.2 Battle (trainer) sprites: `a/0/7/1` front, `a/0/7/2` back

- Trainer class → sprite: `TRAINER_CLASS_RESOURCES` (arm9 `0x02092394`, 4 bytes per class, byte 0 = front sprite)
  and `TRAINER_CLASS_BACK_SPRITES` (arm9 `0x02092314`, 32 × `{class, back sprite}`), read by `GetTrSpriteBaseDatID`
  (arm9 `0x02030740`) **[code + bytes]**. 188 front sprites, 31 back. Nate/Rosa: front 0/1, back 0/1.
- **Files per sprite `s` = `8s … 8s+7`** (`GetTrSprite*DatID`, arm9 `0x02033cf0-0x02033d50`) **[code]**: +0 NCGR
  "character 1" (LZ11, 10×10 tiles, 4bpp, parts), **+1 NCGR "character 2" (LZ11, 256×128 4bpp linear bitmap: the
  cut-up parts and one complete figure)**, +2 NCER cells, +3 NANR cell animation (LZ11), +4 NMCR multi-cell, +5 NMAR
  multi-cell animation, +6 extra data (role unknown), **+7 NCLR, 16 colours**. This is the same multi-cell (MCSS)
  animation system as the Pokémon battle sprites.
- Hoenn trainer sprites: listed in section 1 (Roxanne class 136 → sprite 118 … Juan 144 → 126, Steven 177 → 139,
  Wallace 178 → 140). Brendan/May: edit Nate/Rosa's front (rival battles can then use classes 0/1) and back sprites.

### 5.3 Writing an edited image back (no Nintendo SDK)

- **Overworld sheet, same frame count and size (recommended):** decode each frame to PNG (4bpp texel offsets from the
  TEX0 texture dictionary, palette BGR555), edit, map each pixel back to the 16 palette colours, write the bytes in
  place, and write the new palette over the old one. File size does not change, so the ROM layout and our savestates
  stay valid. **Round trip tested on all 348 people sheets: 335 byte-identical, 13 pixel-identical (palettes with a
  duplicated colour)** **[test]**. Pick a donor with the same controller type, so the frame layout matches.
- **Overworld sheet with a different frame count:** the BTX0 dictionary changes. CTRMapV's `NSBTXWriter` (as in
  `b2tools/java/MergeNsbtx.java`) writes BTX0, but it re-encodes textures, so the 16-colour palette and texture names
  would need checking; `spriteAtlasSize`/controller type in `a/0/4/7` would change too. Avoid unless needed.
- **Battle sprite:** keep the part rectangles of the donor (the cells/animations stay valid), redraw inside them in
  file +1, put the new 16 colours in +7, LZ11-compress +1 again. A small Python LZ11 compressor round-tripped
  sprites 0, 1, 118, 122, 139, 140 (decompresses to identical data, same compressed size, not byte-identical)
  **[test]**. Compressed sizes change, so `a/0/7/1`/`a/0/7/2` need `RESERVE` entries in `build_rom.py` like our other
  archives.
- New object codes are not needed for the opening: we can repaint existing codes (Nate/Rosa → Brendan/May; Hilbert/
  Hilda → rival Brendan/May NPCs; Mom → Hoenn Mom; Cedric → Birch).

### 5.4 Battle sprite animations, and Sapphire's characters redrawn (2026-10-06)

- **Intro gesture vs still** **[code: b2tools/mcss.py, checked on all 188 front sprites]**: NMAR sequence 0 = the
  intro gesture (played once, multi-cell 0 = the parts, cells rotated/moved about the cell's own (0, 0)); sequence 1
  loops multi-cell 1 = one node showing the whole-figure cell. +6 is a quad table (per cell: x, y, w, h, u, v = the
  NCER cell's bounding box on screen and in the texture). `mcss.static_intro` points the gesture's frames at the still
  figure (same length; tested in battle) for pictures no Black 2 gesture fits. **[test]**
- **Redrawn characters** (`b2tools/sprite_upgrade.py`, review `screenshots/sprites/upgrade_review.png`): Sapphire's
  own trainer pics (x1.25 to 80x80, one-pixel lines kept, Gen 5 outlines) cut onto a Black 2 trainer's parts of
  similar pose (`mcss.distribute`), and Sapphire's overworld frames at Black 2 proportions in the 12-frame layout.
  Then touched up to Black 2's conventions (user request): Gen 5 proportions (head x1.15, body x1.35), Black 2's
  skin ramps (the same 4 tones on every Black 2 person: battle 255,214,189 / 222,173,132 / 189,115,90 / 123,74,90;
  overworld 255,214,189 / 214,156,115 / 123,74,49), outlines black on clothes but the material's dark tone around
  skin and hair (measured: 50-70% of Black 2's edge pixels are black), two-pixel overworld eyes.
  Slots: `data/sprite_map.json` (`_trainer_front` for battle, `_overworld_extra` for Matt 88 / Shelly 92). Overworld
  codes **87 (Wally)**, **88 (Matt)**, **89 (Drake)** and **92 (Shelly)** are unused Black 2 sheets; **85 (Cilan)** and **229 (Drayden)**, the old stand-ins, are shown by the PWT (`a/2/4/7`)
  and must not be repainted. **[test: Archie walks (code 353) and battles (front 151, gesture), Drake walks (89);
  Drake's set (still intro) battles in slot 151]**
- **Brendan, May, Prof. Birch** (`b2tools/sprite_upgrade_players.py`, review
  `screenshots/sprites/upgrade_review_players.png`): Sapphire's own sets resized and animated the same way, every
  player sheet 231-248 from Sapphire's walk/run, Mach Bike, surf, field move and fishing frames (Black 2 sets
  Sapphire has no pictures for take its nearest frames: PLAYER_SETS), battle fronts 0/1 on front 108's parts, Birch
  overworld 104. Intro professor (a/1/6/8, Juniper's MCSS set, `mcss.distribute_pose`): Sapphire's
  `birch_speech/birch.png` cut onto her parts as she stands in animation 1; the idle ball toss and the throw work
  (Poke Ball cells kept, open-mouth head 27 drawn). Blink and talking mouth: the multi-cells' nodes that play them
  (NANR 1: eye strip, cells 2 open / 3 closed, 16x8; NANR 15: the mouth, cell 4 = MCSS quad table entry whose second
  quad, 32x8 at texture (96, 56), reads rows 56 while the MCSS flag 0x100 is clear and rows 64 while it is set:
  ov294's talk command toggles it every 6 frames while text prints and sets it at rest) are moved from Juniper's face
  (0, -46) / (0, -38) to Birch's eyes (7, -37) and mouth (7, -30) (sprite.json "node_moves" -> `mcss.move_nodes`,
  NMCR file 30, same size); the strips hold only the pixels they change (closed eyes: a one-pixel lid line; open
  mouth: lips around the red), clear elsewhere, so his face underneath shows through (v12 had them at Juniper's
  places, over his eyes, with an empty rows-64 strip: glitching eyes and a hole while talking). **[test: cold boot
  as boy and girl through the intro into the truck, walking and running; rival NPC codes 1/4 walk; battles vs
  classes 0/1 show the fronts; whole intro speech frame by frame: every frame with Birch on screen is the rest,
  blink, talk or blink+talk picture]**
- **Wally's back sprite** (`b2tools/sprite_upgrade_backs.py`, review `screenshots/sprites/wally_back_review.png`,
  2026-10-07): Wally's catch (Black 2's capture demo, `patches/capture_demo.py`) throws with back sprite 6 (Bianca's,
  class 38 in TRAINER_CLASS_BACK_SPRITES arm9 0x02092314; no other Hoenn use). Sapphire's `wally_back.png` frames 0-2
  (standing, wind-up, throw) scaled like the fronts (head x1.15, body x1.35, x1.2), his body continued below the
  picture as his front picture draws it (long white shirt, green trousers; behind the message box), each pose a whole
  figure in one or two of Bianca's cells: standing = cell 0, wind-up = cell 5, throw = cell 7 over cell 6 (her arm
  cells 1-4 clear). Data only, same sizes: sprite.json `node_edits` re-point / move multi-cell nodes
  (`mcss.set_nodes`), `still_multicells` [2, 3, 4] stops animation 1's slides (`mcss.still_translations`): Sapphire's
  own frame placement is the motion. Sapphire's frame 3 (follow-through) has no cell left. **[test: HOENN_TEST_CH1=3
  catch from Littleroot's sign: Wally slides in, winds up, throws; "Wally used Poké Ball!", the catch,
  screenshots/tests/wally_back_catch.png]**
- **Black 2 class side effects** **[test]**: class TEAM_PLASMA_GHETSIS (189) plays a "VS" cut-in with Ghetsis's
  portrait and the Plasma logo before the battle; an Elite Four class (Marshal 79, trainer 39) started from Littleroot
  hangs on a white screen even with Black 2's own sprite (the Elite Four battle needs something the League sets up).
  Both matter for the classes the trainers converter picks, not for the sprites.

### 5.5 Every picture of the player, and Brendan / May / Birch redrawn (2026-10-06, sprites_players)

Where Black 2 shows Nate/Rosa (decomp search; file indices male / female) and what Hoenn shows now
(`b2tools/sprite_players.py`, review `screenshots/sprites/players_upgrade_review.png`):

| Where | Files | Format | Now |
|---|---|---|---|
| Overworld (walk/run, bike, surf, item, actions, throw, balance, fishing) | object codes 231-239 / 240-248 (a/0/4/8) | BTX0 sheets | Brendan / May (Sapphire outfits). Rival NPC codes 1-6, 136-161 = copies **[test]** |
| Name entry icon | a/0/4/8 sheets 209 / 218 (= codes 231 / 240) | same sheet | follows the overworld art **[test]** |
| Start menu Continue panel, GTS, Spin Trade / Battle Video | a/0/3/0 NCGR 5, 14, 20 / 7, 17, 23, NCLR 4 / 6 | uncompressed 4 bpp 32x32 OBJ frames; **every frame is a frame of sheet 231 / 240** (checked) | copied from the overworld art (`src/sprites/objframes/`) **[test: Continue]** |
| Battle back (with the throw) | a/0/7/2 sprites 0 / 1 | MCSS | Brendan / May **[test]** |
| Battle front: trainer classes 0 / 1 (rival battles), Hall of Fame | a/0/7/1 sprites 0 / 1 | MCSS | Brendan / May **[test: trainers 360 / 363]** |
| New-game intro, boy/girl choice | a/1/6/8 file 22 (BMD0, ov294 IntroG3d): textures int_swan_m.2 / f.2 (128x256, 8 bpp, own 256-colour palette, colour 0 clear) and .1 (the same picture darkened, the side not chosen) | in-place texture edit (`src/sprites/texture/`) | user: the official **Omega Ruby / Alpha Sapphire art itself** (`src/reference/`), resampled (Lanczos, premultiplied alpha, edge colours taken from the solid pixels so no light fringe) to Nate's / Rosa's height and feet line, centred, quantized to 255 colours without dithering **[test]** |
| Intro professor | a/1/6/8 files 24-30 (MCSS) | MCSS | Prof. Birch **[test]** |
| End credits | a/2/1/5 (ov266 `func_ov266_0219e350`): per picture p, NCLR/NCGR/NSCR 21+12p / 22+12p / 23+12p for a boy and 24+12p / 25+12p / 26+12p for a girl (files 10/11/12 when work[16] == 1, not gendered); 165 files | 256x192 8 bpp BG screens | **not done** (user: Hoenn scenes later): six greyscale Unova scenes (Pokémon League hall, Opelucid gym, Join Avenue?, a lab, Skyarrow/airport, a town square) with the player's and Unova characters' overworld sprites drawn in |
| Trainer card | ov186 `func_ov186_021a7ec0`: the player's own card shows a built-in picture, a/0/3/9 NCGR 36 (110 8 bpp tiles shared by both) with NSCR 50 (Nate) / 51 (Rosa) and NCLR 14; another player's card (card data +4 bit 7) shows the Union Room avatar, a/0/4/0 NCGR 16+v / NCLR v (80x80 8 bpp tiled, table `data_ov186_021acf70`; v = random 0-7 + 8 x gender at the new game, `game_start.c:401`) | code edit + in place (`src/sprites/cardpic/`) | user: show Brendan / May. The picture test's `bne` at 0x021a7ee0 -> `b` (every card shows the avatar picture; the bit's other uses, no editing of another player's card, stay), and every boy avatar (NCGR 16-23, NCLR 0-7) = Brendan's battle front still, every girl avatar (24-31, 8-15) = May's, copied at build time (so Union Room cards show them too) **[test]** |
| Nimbasa Gym screen, Xtransceiver portraits (a/1/3/2, which pair is Nate/Rosa unverified), 3D cutscene models (a/1/5/8 hero/heroine BMD0s) | | | not done (Unova-only scenes or 3D models) |

- a/0/6/3 is a byte-identical copy of the battle backs a/0/7/2 (31 sets); battles read a/0/7/2 (tested). What reads
  a/0/6/3 was not traced; it still holds Nate's and Rosa's backs.
- The darkened gender-choice picture is Black 2's own darkening (fitted on Nate's and Rosa's pairs): about
  0.29 x colour - 2 per channel. The intro's model swaps .1/.2 with its BTP0; only the textures change.
- Testing tricks: the boy/girl choice takes input only after its message is dismissed (title + 42 A presses, one more
  A, then LEFT/RIGHT, then A); a battle as May from the boy savestates: set PlayerInfo.gender (+0x1D after the name
  "AAAAAAA" + 0xFFFF, two copies in RAM) to 1 before the battle. Savestates keep the player's overworld texture in
  VRAM (the old art shows until a cold boot).

## 6. Sapphire's opening, step by step, in Black 2 terms

| Sapphire (`ruby/data/maps/…`) | Black 2 implementation |
|---|---|
| New game warps into `InsideOfTruck` and runs `ExecuteTruckSequence` (`ruby/src/new_game.c:137-141`, `ruby/src/overworld.c:1282`, `field_special_scene.c:182-265`) | arm9 patch → truck zone (394/395); its script 30 `MapChangeCore`s into itself with a reserved truck script (black, sound, `EvCameraShake`, stop, door light = fade). Boxes: interior building models `box01`/`box02` (all interior packs 0-7). |
| Truck trigger: respawn, `VAR_LITTLEROOT_INTRO_STATE` 1/2, hide flags, warp to (3,10)/(12,10) (`InsideOfTruck/scripts.inc`) | Zone trigger → `TrainerCardGetSex`, `FieldSetTeleportZone 1`, our own saved vars/flags, `RTReserveScript`, `MapChangeCore 389, 777/786, 0, 746, 1`. |
| Littleroot `OnFrame` StepOffTruck: Mom comes out of the door, "our new home", both go in (`LittlerootTown/scripts.inc:77-131`) | Reserved script in 389: player hop (movement), door animation, Mom NPC (251 repainted) walks, `ActorMsg`, both walk in, `MapChangeCore 390 …`. Needs a **moving-truck building model** (B2 has none) and door animations on our custom houses. |
| House 1F/2F: movers, set the clock, Dad on TV, "go meet Prof. Birch's family" (`LittlerootTown_BrendansHouse_1F/2F`, `scripts/players_house.inc`) | Scripts in 390/391 (and 392/393 for a girl: the houses swap by gender, see Unknown 9). The DS has a real clock: the clock-setting screen has no B2 equivalent. |
| Rival's house, rival's mom (`…_MaysHouse_1F/2F`) | Scripts in 392/393; rival NPC via WKOBJCODE 162 + var 0x4020 by gender. |
| North exit: twin stops you; after the visit, "Prof. Birch… go see what's happening" (`LittlerootTown/scripts.inc:217-321`) | Zone triggers with saved vars. |
| Route 101: triggers at (10,19)/(11,19) with `VAR_ROUTE101_STATE` 1 → Birch chased (`Route101/scripts.inc:19-46`); Birch (9,13), Poochyena (10,13), bag (7,14) | Global tiles: x = 774 + sx, z = 716 + sy (Route 101 is built with `--offset 6,12` in cell (24,22), `b2tools/patches/route101.py:3`): triggers (784,735)/(785,735), Birch (783,729), Poochyena (784,729), bag (781,730). Birch = repainted 104, Poochyena = 4390, bag = a repainted one-frame object (none in B2). |
| Bag script: flags, fade, remove Poochyena, player to (6,13) facing left, choose starter → give Lv 5 → Poochyena Lv 2 battle → Birch thanks, heal, warp to lab (`Route101/scripts.inc:217-242`, `battle_setup.c:865-898`) | `FadeOutBlack`, `ActorDelete`, `ActorSetGPos`, `FieldClose`, `callPoke3Select`, `FieldOpen`, species by index, `PokePartyAdd var, species, 0, 5`, `FlagSet 2401`, `CallWildBattle SPECIES_POOCHYENA, 2, …`, `CallWildBattleEnd`, `ActorMsg`, `PokePartyRecoverAll`, `RTReserveScript`, `MapChangeCore 396 …`. Sapphire's first battle cannot be fled and has no critical hits (`battle_main.c:4174`, `battle_script_commands.c:1401`); B2 equivalent unknown (Unknown 4). |
| Lab: "I'd like you to have it", nickname yes/no, "go see your rival" (`…_ProfessorBirchsLab/scripts.inc:25-66`) | `MapScriptConditions` on our lab-state var (≈ `VAR_BIRCH_LAB_STATE` 2), `YesNoWin`, nickname loop as `0854.s:465-520`. |

## 7. Implementation plan for the opening

1. **Build support** (no game change): let `build_rom.py` apply code patches — copy `arm9.bin` /
   `arm9_ov316.bin` into the build folder, patch bytes, point `rom_config.yaml` at the copies. Add `RESERVE` entries
   for `a/0/4/8` (48), `a/0/7/1` (71), `a/0/7/2` (72), then rebuild the base savestates once.
2. **Sprite tool** `b2tools/sprites.py`: export/import overworld sheets (in place) and battle sprites (NCGR/NCLR +
   LZ11), with a round-trip self-check like the one above.
3. **Smoke tests of the two code patches** (cheap, decisive): (a) starter table → Treecko/Torchic/Mudkip, walk to
   B2's lookout scene on the existing Aspertia start; (b) spawn literal → zone 389, check the player appears and
   scripts 29/30 of `0778` run. Boot in melonDS (DS and DSi mode). If either fails, use the data-only fallbacks.
4. **Art (user decision on style, DECISIONS 2026-10-06):** Brendan/May player sets (repaint 231-248: 9 sheets each),
   rival NPC sets (repaint Hilbert/Hilda 1-6, 136-141, 156-161), battle front/back (Nate/Rosa 0/1), Hoenn Mom
   (251, 357), Birch (104), Birch's bag (one frame), moving truck model, truck interior.
5. **Truck zone** (394 or 395) with a small interior chunk, boxes and an exit trigger.
6. **Scripts**, in story order: truck → Littleroot arrival → house 1F/2F → rival's house → twin/exit triggers →
   Route 101 chase → bag/starter/battle → lab. Allocate saved vars/flags only after a usage dump (Unknown 12). Put
   Sapphire's text in `src/text/script/` as we do now.
7. **Gender:** player's house left for a boy, right for a girl (Sapphire). Either move the door warps at zone init
   (`ObjInitWarpGPos`, command 472) or give each house both interiors; signs already noted in LITTLEROOT.md.
8. **Tests:** a new-game route from boot (`make_states.py` path changes), then savestates after the truck, after
   the starter, after the lab.

## 8. Unknown (and what would settle it)

1. **Whether a patched arm9 / ov316 builds and boots.** Overlays are marked `signed: true` and the build has
   `arm9_hmac_sha1_key`; dsd reproduces the original signatures, so it probably re-signs changed overlays. A changed
   arm9 probably no longer matches the DSi header's arm9 HMAC, which would matter only in DSi mode (not checked).
   Settle: step 3 of the plan in melonDS (DS and DSi mode), later the flashcart. Also check the compressed ov316
   still fits its 512-byte slot (else the file layout moves).
2. **Actor flag 4** set on the player before script 29 (`event_mapchange.c:231`): probably "hidden"; no script command
   to clear it was found. Settle: test, or trace `SetActorFlag`/`CheckActorFlag` users of bit 4.
3. **3D demo 5** and the season banner before the first map: what demo 5 shows and whether to skip it (ov035 change).
4. **`CallWildBattle` flags:** bit 0 → `BtlSetup_SetFlag(4)` (legendaries), bits 1-11 set other fields
   (`EventWildBattleCall_CreateStatic`, ov036 `0x021a18d4`); none decoded. Which bit (if any) forbids running, and
   whether `CallWildBattleEnd` after a **loss** returns to the script (Sapphire continues regardless). Settle: test
   each bit in the emulator.
5. **Movement codes** other than 0x0C-0x0F (names inferred from Gen 4). Settle: copy from matching B2 scenes and test.
6. **psel overlay:** other species-dependent data (`data_ov316_0219fa9a/9b`, `0219fb78`) and how the 3D stand looks
   with Hoenn starters. Settle: smoke test 3a.
7. **Intro (overlay 294):** Juniper/Cinccino/Nate/Rosa graphics, and skipping rival naming (Sapphire names no rival).
   Not researched.
8. **Door animations** for our custom Littleroot buildings (`BMCreateHandleByGPos` needs a door model with animation
   in the building pack; our models were written without one?). Settle: check the pack info `doorResId` of our models.
9. **Swapping the houses by gender:** whether moving warps in the zone-init script happens before the arrival
   position is chosen. Settle: test.
10. **Spawn height** when spawning by header fly position (fly_y defaults to 0, `bw2/include/asm/zone_header.inc:19`, and neither header sets it; Aspertia's ground is
    y = 16 and the game copes, so probably the terrain decides). Settle: smoke test 3b.
11. **Battle sprite files +0 and +6**: what +0 (10×10 tile parts) and +6 are used for; whether files the game reads
    LZ11-compressed may also be stored plain. Not needed if we keep each file's format.
12. **Free flags/vars** for Hoenn's story (B2 uses many; map-local ones reset). Settle: dump every flag/var used by
    scripts and code (CTRMapV has `VWorkUsageDumper`), mark the ones only used by replaced Unova zones.
13. **Whether codes 1-6/136-141/156-161 (Hilbert/Hilda) are used by code** (Memory Link, PWT, Entralink). Scripts and
    zone NPCs were checked; code was not. Settle: grep the disassembly for those immediates near actor creation.
14. **Flag 2401** meaning (set when the first Pokémon is received; read by `func_ov036_021a01c4`). Settle: trace it.
15. **Music and sounds:** no Hoenn tracks (Birch's "help" theme, truck sounds); B2 equivalents to choose.
16. Trainer card, bag, intro and other menus that show the player (not part of this research).

## Sources

- Decomp: `bw2/src/ov162/game_start.c`, `bw2/src/ov035/event_mapchange.c`, `bw2/src/ov279/new_game.c`,
  `bw2/src/ov012/{script_sys.c, scrcmd_vm.c, scrcmd_proc.c, scrcmd_pokemon.c, scrcmd_game_state.c, respawn_zone.c}`,
  `bw2/src/ov036/fieldmap.c`, `bw2/src/ov060/scrcmd_resort_shop.c:1895-1902`, `bw2/src/ov055/{wbt_setup.c, wbt_tool.c}`,
  `bw2/include/field/{field_actor.h, field_acmd.h, zone.h}`, `bw2/include/app/psel.h`, `bw2/include/constants/*`,
  scripts `bw2/data/field_scripts/{0854, 0855, 0856, 0792, 1242, 0032, 0086}.s`, symbols in
  `bw2/config/b2_us/arm9/**/symbols.txt`; disassembly of main, ov012, ov035, ov036, ov316 with `tools/dsd dis`.
- Bytes: `bw2/build/b2_us/build/{arm9.bin, arm9_ov012.bin, arm9_ov036.bin, arm9_ov316.bin}`,
  `bw2/build/b2_us/files/a/0/4/{7,8}`, `a/0/7/{1,2}`, `a/2/0/8`, `a/2/4/7`.
- CTRMapV 1.4.1 script library (argument names), `tools/ctrmap-plugins/CTRMapV-1.4.1.jar`.
- pokeruby: `src/{new_game.c, overworld.c, field_special_scene.c, battle_setup.c, battle_controllers.c,
  starter_choose.c}`, `data/maps/{InsideOfTruck, LittlerootTown*, Route101, LittlerootTown_ProfessorBirchsLab}`.
- Earlier work: `work/sprites/table.json` and `people_1_200.png` (a previous session's dump of the same table).

## Trainer card badge page: Hoenn (v165_fixes, 2026-10-11; b2tools/patches/trainer_card.py)
The badge page (ov186 func_ov186_021ab178 / 021ab220 / 021ab25c) reads a/0/3/9 **[code][test]**: NCGR 28 + NSCR 38
(rows 1-10 the eight leader pennants, BG palettes 0-7 from NCLR 0 colour / NCLR 1 grey, colour copied over grey per
badge obtained; rows 11-20 the badge case, palette 8), NCGR 31 / NCER 52 / NCLR 4 (the 2D badges, 32x64 cells, palettes
1, 6, 2, 3, 4, 5, 7, 0), BMD0 56-63 (the badge on the top screen when touched), ov186 0x021ad19c u16[8] (the trainer
class whose battle sprite stands beside it) and system text 379 lines 65-112 (name, title, quote; badge name + date,
obedience). Now: pennants = 2x head-and-shoulders crops of Black 2's PWT fronts (a/0/7/1 118-125, 140; Tate above
Liza), each in <= 15 colours with the pennant's own dark; grey palettes by Black 2's own rule (luminance x 0.31);
the case's silhouettes, the 2D badges and the 3D badges are Sapphire's trainer-card badges (graphics/trainer_card/
badges.png, 16x16, silver) at 2x (3D: src/trainer_card/badge3d_N.nsbmd from b2tools/trainer_card_models.py, a
two-sided plate; ToNsbmd --tex); the classes 112, 113, 115, 114, 117, 116, 118, 119 (Roxanne ... Wallace,
data/hoenn_trainer_classes.json); text src/text/overrides_trainer_card.json (titles from Sapphire's Gym signs, one line
each leader says in Sapphire; Black 2's obedience lines kept, they describe the rule the game uses). Tiles must stay
at or below the last slot Black 2 uses (520): slots past it are not loaded (garbage stripes, tested); the patch reuses
the slots the replaced cells used. a/0/3/9 keeps its size (zero padding: no RESERVE). Tested in DeSmuME with 0, 4 and 8
badges (RAM: save block 0x34 + 4, one bit per badge), CLASSIC and NEW sprites (the front picture switches as before),
Sapphire and Ruby: screenshots/v165_fixes/07-14.
