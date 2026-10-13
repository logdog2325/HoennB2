# Common story scripts (S_common): what chapters call

Owner: story_infra. Sapphire's shared scripts (`notes/STORY_CHAPTERS.md` §4 S_common: `data/event_scripts.s`,
`data/scripts/*.inc`) and the name each chapter calls instead. **DONE** = usable now (tested in game unless marked),
**TODO** = name reserved, not written yet (call sites can be written already; they will assemble once it lands),
**B2** = Black 2 already does it (nothing to port), **CH** = belongs to one chapter (do it there), **DECIDE** = needs
the user. Library: `src/include/hoenn_story.inc` (macros, `h_` + Sapphire's name; see `notes/STORY_PORTING.md` §4).
Shared code with labels: `src/field_scripts/common/*.inc` (include them in your zone script; each has an include
guard, so including one twice is fine).

Every chapter script starts with:
```
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"        // Sapphire key item names (ITEM_DEVON_GOODS ...)
#include "hoenn_story.inc"
    ScriptEntry ...                   // your scripts
...
// at the END of the file (shared code with labels must come after your scripts):
#include "common/movement.inc"        // only if you use Common_Movement_* lists
#include "common/briney.inc"          // only if you call Sub_*MrBriney*
```
`#include "common/x.inc"` works from any script file (the assembler searches `src/field_scripts`).
Text: messages always come from your zone's own text file (`MSGFILE_SCRIPT`), so a common macro that shows a line takes
the line's id: copy Sapphire's common text (`data/text/*.inc`, quoted below) into your zone's text file.

## Index

| Sapphire (event_scripts.s / scripts/*.inc) | Call this | Status |
|---|---|---|
| `msgbox X, MSGBOX_*` (std_msgbox.inc) | `h_msgbox_npc`, `h_msgbox_sign`, `h_msgbox`, `h_msgbox_actor`, `h_msgbox_info`, `h_msgbox_autoclose`, `h_yesno` | DONE |
| `Common_EventScript_SaveGame` (special SaveGame) | — (only Battle Tower, Contest lobby, Game Corner link rooms: S_optional; Black 2's scripted save is `SaveDataWrite`, 0150.s:938-955) | S_optional |
| `trainerbattle_single/_double/_no_intro` (trainer_battle.inc) for scripted battles | `h_trainerbattle`, `h_trainerbattle_continue`, `h_trainerbattle_two`, `h_goto_if_cannot_double`, `h_trainer_intro` | DONE |
| eye-contact route trainers (`EventScript_StartTrainerBattle`, `Movement_RevealTrainer`) | placed by the trainers patch (`data/hoenn_trainer_npcs.json`): Black 2's global trainer script | B2 |
| `trainerbattle_rematch*`, Trainer's Eyes | — | TODO (rematches come later, user) |
| `giveitem ITEM, n` / `giveitem_std` (obtain_item.inc) | `h_giveitem ITEM, n`: Black 2's jingle + "obtained" + pocket lines; `HLIB_RESULT` 1 given, 0 no room (then nothing is shown, as Sapphire) | DONE |
| `Common_EventScript_ShowBagIsFull` (giveitem + `compare VAR_RESULT, 0` + goto) | `h_giveitem ITEM, n` then `h_goto_if_eq HLIB_RESULT, 0, L_BagFull` … `L_BagFull: h_bag_is_full n` + `h_release` (n = Sapphire's "Too bad!\nThe Bag is full..." in your text) | DONE |
| `finditem` item balls (item_ball_scripts.inc) | placed by `converter/gen_items.py` (global scripts 7000+n, `data/hoenn_items.json`) | B2 |
| `EventScript_HiddenItem` (hidden items, `bg_events` type hidden_item) | `converter/gen_hidden_items.py`: Black 2 hidden-item signs (cond 2, script 7999+n = file 1241 Script_n, flag 2819+n), registry `data/hoenn_hidden_items.json` (98 items, slots 1-98 of 213), signs in `data/story/hidden_items.json` placed by the story patch (maps not built yet are skipped until they are) | DONE (tested: found once, gone after) |
| `giveitem` of a decoration / `givedecoration` | — | S_optional (no decorations) |
| `Common_EventScript_PkmnCenterNurse` (pkmn_center_nurse.inc) | `src/field_scripts/centers/nurse.inc` (centers agent) | DONE |
| `EventScript_PC` (pc.inc), `FLAG_SYS_PC_LANETTE` | Black 2's PC in the centers / player's room (already named "Lanette's PC": src/text/overrides.json) | B2 |
| `Common_Movement_*` (movement.inc) | `common/movement.inc`: same labels (`Common_Movement_ExclamationMark`, `_QuestionMark`, `_Delay48`, `_Delay32`, `_WalkInPlaceFastestLeft/Up/Right/Down`, `_WalkUp`, `_WalkUp2`, `_WalkUp4`, `_WalkUp6`) + the movement macros. `_FacePlayer`/`_FaceAwayPlayer`/`_FaceOriginalDirection`: Black 2 has no such move: `h_faceplayer` for the NPC talked to, else `face_<dir>` | DONE |
| `Common_EventScript_SetupRivalGfxId` (dynamic_npc_graphics.inc) | `h_setup_rival_gfx` (zone init; NPC model 162) | DONE |
| `Common_EventScript_SetupRivalOnBikeGfxId` (Route 110 / 119 rival on a bike) | `h_setup_rival_bike_gfx` | DONE as a stand-in: the walking rival (no Brendan/May bike sprites yet: sprites agents) |
| `Common_EventScript_SetupEvilTeamGfxIds` | none: Sapphire is Aqua only, place Aqua models directly | DONE (no-op) |
| `Common_EventScript_SetupLegendaryGfxIds` | Ch10: Kyogre is placed directly with the Pokémon sprite code 4511 as its NPC model (data/story/ch10.json, Seafloor Cavern Room 9 and Cave of Origin B4F); Ch13 still to do for Rayquaza / Latios | DONE (Kyogre) |
| `Common_EventScript_SetGymTrainers` + `VAR_0x8008 = gym` (set_gym_trainers.inc) | `h_set_gym_trainers N` (N = 1 Rustboro … 8 Sootopolis) | DONE |
| `setflag FLAG_BADGEnn_GET`, `goto_if_set/unset FLAG_BADGEnn_GET` | `h_givebadge N`, `h_goto_if_badge N, L`, `h_goto_if_no_badge N, L` (Black 2's trainer card badge N-1; hm_free reads it) | DONE |
| `Common_EventScript_PlayGymBadgeFanfare` | `h_badge_fanfare` | DONE |
| `Common_EventScript_OutOfCenterPartyHeal` (fade, heal, jingle) | `h_heal_party_fade` | DONE |
| `Common_EventScript_PlayerHandedOverTheItem` ("{PLAYER} handed over the {STR_VAR_2}.") | `h_handover_item ITEM, msg` | DONE |
| `Common_EventScript_NameReceivedPartyMon` (nickname a gift Pokémon) | `h_name_received_mon slot` (slot: number or work; Black 2's nickname screen) | DONE |
| `Common_EventScript_UpdateBrineyLocation`, `EventScript_SetBrineyLocation_*`, `EventScript_ResetMrBriney`, `EventScript_BackupMrBrineyLocation`, `EventScript_HideMrBriney` | `common/briney.inc`: `Sub_UpdateBrineyLocation`, `Sub_ResetMrBriney`, `Sub_BackupMrBrineyLocation`, `Sub_HideMrBriney` (VMCall) | DONE (Sapphire runs ResetMrBriney on whiteout: Black 2 has no whiteout hook, Ch2 decides) |
| `Common_EventScript_PlayBrineysBoatMusic` / `StopBrineysBoatMusic` | `h_play_briney_boat_music` / `h_stop_briney_boat_music` (`MUS_SAILING` = Black 2's surf theme, a stand-in) | DONE (assembles; music choice later) |
| a boat / ship crossing (Briney's boat, the S.S. Tidal and every ferry), the cable car | `h_sail_briney` / `h_sail_ferry` / `h_ride_cable_car zone, x, z, dir, script` (hoenn_story.inc; research and macros in `common/boat.inc`): Black 2's 3D boat cutscene (demo 4 without Castelia's pier: patch `boat_demos`; demo 26 the ferry at sea), then the map change and the destination's arrival script; the cable car stays a fade (Black 2 has no ride) | DONE (boats agent; Briney, S.S. Tidal and the cable car tested) |
| `Common_EventScript_FerryDepart`, `FerryDepartIsland` | — | CH (Ch13 S.S. Tidal) |
| `Common_EventScript_PokemartSign` / `PokemonCenterSign` | `h_msgbox_sign` with Sapphire's `Text_PokemartSign` / `Text_PokemonCenterSign` in your text file | DONE |
| `EventScript_RegionMap` (wall maps: "look closer at the map") | — Black 2 has no script command for the Town Map: show the line only (`h_msgbox_sign`) | DONE (text only) |
| `EventScript_WhiteOut`, `S_RepelWoreOff` | Black 2's engine (`h_setrespawn` sets where you wake up) | B2 |
| `Common_EventScript_SetLegendaryWeather` | `common/legendary_weather.inc` `Common_SetLegendaryWeather` (a no-op: the `weather` patch, b2tools/patches/weather.py, makes the crisis zones' weather the thunderstorm while FLAG_SYS_WEATHER_CTRL is set; findings in the file) | DONE (ch10) |
| `Common_EventScript_ReadyPetalburgGymForBattle` | — | CH (Ch6) |
| `Common_EventScript_ShowEasyChatScreen`, `BufferTrendyPhrase` | — | S_optional |
| field moves (field_move_scripts.inc, surf.inc): Cut, Rock Smash, Strength, Surf, Waterfall, Dive, Flash, Fly; `FLAG_SYS_USE_STRENGTH` | `b2tools/patches/hm_free.py` (global scripts 10000-10016; rock/boulder objects: notes/CAVES.md) | B2 + hm_free |
| Secret Power (field_move_scripts.inc) | — | S_optional |
| berry trees (berry_tree.inc) | **daily berry spots** (user decision): `converter/gen_hidden_items.py` puts one sign on each Sapphire tree that has a berry at new game (80 of 88; the 8 empty soils have nothing without planting), global 8212+k in file 1241; Sapphire's berry, its unwatered yield, Sapphire's lines; once a day (`VAR_BERRY_PICKED_0-5` bits + `FLAG_DAILY_BERRY_SPOTS`, Black 2's midnight reset). Placed by the story patch on built maps (`data/story/berry_spots.json`, registry `data/hoenn_berry_spots.json`). Each spot shows Sapphire's grown tree (NPC, hidden by FLAG_BERRY_TREE_PICKED_<k> while picked; the tree zones' inits reset them on a new day: notes/STORY_HANDOFFS.md "From missing_objects") | DONE (tested: pick, "soft, loamy soil" the same day, berries again after midnight; trees: gone when picked, back the next day) |
| cracked floors / holes (cave_hole.inc: Granite Cave, Sky Pillar) | — | TODO (with the cave owners) |
| static Pokémon (static_pokemon.inc: Kecleon, Electrode) | `h_static_battle SPECIES, level, hide_flag, uid` (sets the flag, battles, the object goes; lost = whiteout; `HLIB_RESULT` 0 caught, 1/2 fainted or fled) | DONE |
| `VAR_ICE_STEP_COUNT` (cracked ice: Sootopolis Gym, Sky Pillar) | — | TODO (with the ice-floor owner) |
| `FLAG_POKERUS_EXPLAINED` | nurse.inc | DONE |
| Lilycove Trainer Fan Club state (`UpdateTrainerFanClubGameClear`, `sub_810FF60`, `ShouldMoveLilycoveFanClubMember` ...: Hall of Fame, Drake's room, Battle Tower rooms) | `common/fan_club.inc` (ch8a): `Sub_FanClub_GameClear`, `Sub_FanClub_CountWin` (0x8004 = 0 Drake / 3 Battle Tower), `Sub_FanClub_NumMoved` ...; include at the END of the calling file | DONE (the scene and fan lines tested; the update subs assemble, untested) |
| Sapphire key items (`ITEM_DEVON_GOODS`, `ITEM_LETTER`, `ITEM_DEVON_SCOPE` …) | `src/include/hoenn_key_items.h` (table below) | DONE |

## Key items (`converter/gen_key_items.py` → `src/include/hoenn_key_items.h`, `data/hoenn_key_items.json`)
Every key item a Sapphire script uses. **same** = Black 2's own item with the same meaning (use Black 2's constant,
already the Sapphire name where it matches); **reuse** = a Gen 4 key item Black 2 carries but no Black 2 script gives,
renamed. Every item below gets Sapphire's name and description in the Bag (system texts 0063/0064/0481/0482; tested
2026-10-07: "obtained the Devon Goods!", Bag icons and Sapphire descriptions, `screenshots/story_infra/24_*`).
**The item text is not installed yet** (lead; same step as `HOENN_STORY_CODE=1`): `python3 converter/gen_key_items.py --install` writes
`src/text/overrides_key_items.json`; install it in the same build as new base savestates. The longer texts move the
system message files after 0063 inside a/0/0/2, whose table the game reads at boot: savestates made before then read
later system texts at stale offsets (tested: black screen at the nickname screen). Until then the item ids work and the
Bag shows Black 2's names (Parcel, Poké Radar ...). Test builds: `HOENN_EXTRA_TEXT=<file.json>` adds a text-override
file to one build (b2tools/patches/text.py), with your own savestates.

| Sapphire | Black 2 item (id) | how |
|---|---|---|
| ITEM_DEVON_GOODS | ITEM_PARCEL (459) | reuse (parcel icon) |
| ITEM_POKEBLOCK_CASE | ITEM_POFFIN_CASE (449) | reuse (case) |
| ITEM_LETTER | ITEM_OAKS_LETTER (452) | reuse (envelope) |
| ITEM_DEVON_SCOPE | ITEM_POKE_RADAR (431) | reuse (device) |
| ITEM_GO_GOGGLES | ITEM_EXPLORER_KIT (428) | reuse (explorer's helmet; Black 2 has no goggles icon) |
| ITEM_SOOT_SACK | ITEM_LOOT_SACK (429) | reuse (sack) |
| ITEM_WAILMER_PAIL | ITEM_SPRAYDUCK (448) | reuse (watering can) |
| ITEM_SCANNER | ITEM_MACHINE_PART (481) | reuse (device) |
| ITEM_METEORITE | ITEM_ENIGMA_STONE (536) | reuse (rock) |
| ITEM_EON_TICKET | ITEM_LIBERTY_PASS (574) | reuse (Black 2's island-event ticket) |
| ITEM_ROOM_1_KEY / _2 / _4 / _6 | ITEM_SUITE_KEY (451) / ITEM_WORKS_KEY (438) / ITEM_SECRET_KEY (467) / ITEM_CARD_KEY (475) | reuse (keys; no 4th key icon: card key) |
| ITEM_MACH_BIKE | ITEM_BICYCLE (450) | same (Black 2's bike: rides; tested), named "Mach Bike"; Rydel gives it (one bike: user decision) |
| ITEM_ACRO_BIKE | — | **not given** (one bike; the map agents make the Acro-only spots walkable): no define |
| ITEM_POKENAV / ITEM_POKENAV_FEMALE (not a Sapphire item) | ITEM_XTRANSCEIVER_MALE (621) / _FEMALE (626) | reuse (user decision): named "PokéNav", described with Mr. Stone's words; Mr. Stone gives it with `h_give_pokenav` (the player's gender's one) + `h_setflag FLAG_RECEIVED_POKENAV`. No longer in the new-game Bag (story patch: ov279 InitItemBag_, the Pal Pad stays). Tested: opens Black 2's call screen with no contacts ("Please choose who to call.") and closes cleanly; Black 2's own incoming calls come from Unova story scripts this port replaced |
| ITEM_ITEMFINDER | ITEM_DOWSING_MCHN (471) | same (Black 2's item finder), named "Itemfinder" |
| ITEM_OLD_ROD / ITEM_GOOD_ROD / ITEM_SUPER_ROD | same ids (445/446/447) | same; **Old/Good Rod have no field use in Black 2's item data** (only the Super Rod fishes): TODO item-data patch with the encounters owner |
| ITEM_SS_TICKET, ITEM_CONTEST_PASS, ITEM_COIN_CASE, ITEM_BASEMENT_KEY, ITEM_STORAGE_KEY, ITEM_RED_ORB, ITEM_BLUE_ORB, ITEM_ROOT_FOSSIL, ITEM_CLAW_FOSSIL | same names and ids | same |
Sapphire has no Magma/Aqua key items (the Magma Emblem is Emerald's).

## Notes
- Hidden-item table (2026-10-07): Black 2 keeps a table of its 213 hidden items (ov012 HIDDEN_ITEMS: zone and tile for
  the Itemfinder, and a "respawns" byte: every new day 20 % of those come back). The story patch now writes Sapphire's
  items' placed zone and tile there and turns respawning off for every slot (Sapphire's are found once); unused slots
  are moved off-map so the Itemfinder does not beep at Unova spots.
- Tested 2026-10-07 in game (`HOENN_TEST_COMMON=1`, Littleroot's Lab sign, `src/field_scripts/common/test_common.inc`,
  from work/emu/base_littleroot.dst on a story_build ROM): "!" over the player, obtained Potion, 999 Potions = no room
  (silent, `HLIB_RESULT` 0), hand-over line with the player's name + the Potion taken, fade heal, badge 1 + jingle +
  badge checks, gym 1 trainers marked beaten, all four Briney subs, nickname screen, a Kecleon static battle whose
  actor is gone afterwards: every check passed (the town sign line at the end).
- Hidden items (2026-10-07): Black 2's own find script (global 2811: "<player> found a Rare Candy!", pocket line,
  flag): its wording, not Sapphire's "found one RARE CANDY!". Tested with the Petalburg Rare Candy's sign moved to
  Littleroot in a test build (`HOENN_EXTRA_STORY=<json>` adds test-only story objects; `screenshots/story_infra/25_*`):
  found once, nothing on the second try. Signs on warp-only maps now get their ground height too.
- Badges: `h_givebadge N` = `TrainerCardSaveGymVictoryParty`, `TrainerCardAddBadge N-1` and Black 2's per-badge
  system flag 2413+N, as every Black 2 gym does. Black 2's badge picture over the player (field effects) is left out
  (Unova's badges). The "received the X Badge" line is Sapphire's text in your gym's file (`h_msgbox_info`).
- Map-script permissions (ch3b, 2026-10-07, [code + test]): a zone init (`MapScript 2`) runs at script feature level 2,
  field load/return (`MapScript 3/4`) at level 1, everything else at level 0 (ov012 script_sys.c
  `FieldScript_CallZoneInitCore`, `FieldScript_OpcodeGuard`). A command whose bit is clear in ov012 `EVCMD_PERM_TABLE`
  (0x0216b1f0, one byte per command: bit0 level 0, bit1 level 1, bit2 level 2) **hangs the game**
  (`FieldScript_ThrowOpcodeAccessError` loops forever). Level 0 only: `TrainerCardSaveGymVictoryParty` (so `h_givebadge`
  cannot go in a zone init: use `TrainerCardAddBadge N-1` + `FlagSet 2413+N` there), `DayCareCheckSpawnFlag`,
  `DayCareGetPkmCount`, `DayCareDeposit`. Levels 0-1: `ActorSetGPos`. Level 2 only: `ObjInitNPCGPos`. Every level:
  `FlagSet`, `WorkSetConst`, `TrainerCardAddBadge`, `ItemAdd`, `MoneyAdd`, `PokePartyAdd`, `PokePartyRecoverAll`,
  `TrainerFlagSet`, `MapReplaceSetEvent`. Checker: `python3 work/agents/ch3b/tools/check_perm.py SCRIPT.s INIT.s`.
- Story fix-ups (story_fixups, 2026-10-07): **map replacement events** taken: 3 and 4 (works 0x4034/0x4035, Mauville
  Gym's barrier layouts), 5 and 6 (works 0x4036/0x4037, New Mauville's barrier layouts: fixups2), 7 (Sky Pillar islet), 8/9 (Shoal Cave): data/story_ids.json engine WORK_MAP_REPLACE_*; Black 2
  has ten (0-9), the rest are Unova's. A layout swapped in the field shows only after a map change (MapChangeCore with
  constants: 0478_room_MauvilleCity_Gym.s Sub_MG_Redraw). **Wally's name**: class 145 (Hugh's) took its trainer name
  from the save's rival name ("PKMN Trainer ???????"); the trainers patch makes it read text 382 like every class
  (arm9 TrainerUtil_LoadTrainer, RIVAL_NAME_CLASS). **Wally's Ralts** in the catching demo is male, as Sapphire's
  (patches/capture_demo.py: PKM_PARAM_SEX). **Story objects and the dive table** use world.json zone_rects (story.py
  W_zone_of, dive.py frames: 32 of Route 124's dive tiles were in Mossdeep's/Route 126's zone).

## Ribbons (user decision 2026-10-07: really given)
`h_give_ribbon slot, RIBBON_x` sets one of the Hoenn ribbon fields of a party Pokémon (any of Black 2's fields
0x4d-0x6c: `RIBBON_CHAMPION`, `RIBBON_WINNING`, `RIBBON_VICTORY`, `RIBBON_ARTIST`, `RIBBON_EFFORT`,
`RIBBON_CONTEST(category, rank)`); `h_check_ribbon var, slot, RIBBON_x` reads one of the five Sapphire's scripts use
(Champion, Winning, Victory, Artist, Effort); `h_get_lead_mon var` = Sapphire's GetLeadMonIndex (first non-Egg slot).
Sapphire's specials also set `FLAG_SYS_RIBBON_GET`: do it after the give. They need a small ov012 change (Black 2's
PokePartySetIV / PokePartyGetParam whitelists, b2tools/patches/story.py `ribbon_commands`), which is in the gated
overlay edits: build with `HOENN_STORY_CODE=1` (own savestates) until the lead's savestate remake. Tested: a Mudkip
reads 0, gets the Effort Ribbon, reads 1. Used by the Slateport Effort Ribbon woman (scenes/SlateportCity.inc).

## Room scripts shared with a generator
Story scripts in a room file go after a line `// ---- story`; the generators (gen_interiors, gen_interior_recipes_houses,
specials, centers_rooms, shops_rooms, gyms_league_rooms, ship_hideouts_rooms, gen_caves) now rewrite such a file
through `b2tools/story_merge.py` and keep: everything from that line on, your `ScriptEntry` lines (in place of or
after theirs), your `#include` lines, comment lines between the `#include`s and the table, and the text lines you
appended to the room's text file. Anything else you change above the story line is theirs: fix the generator.

## Centers and Mr. Briney
The nine Centers whose Sapphire map script calls `Common_EventScript_UpdateBrineyLocation` (Oldale, Petalburg, Rustboro,
Dewford, Slateport, Mauville, Verdanturf, Fallarbor, Lavaridge) now run `Sub_UpdateBrineyLocation` in their zone init
(b2tools/centers_rooms.py; tested: Oldale's Center loads and works).
