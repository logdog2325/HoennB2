# Porting Sapphire's story (guide for the chapter agents) — 2026-10-06

How to turn pokeruby's story scripts (`external/pokeruby/data/maps/*/scripts.inc`, `data/scripts/*.inc`) into Black 2
field scripts with the groundwork below. Worked example: chapter Ch1's start (Route 103 rival battle → Oldale →
Pokédex in the Lab), ported and tested end to end (section 9). Companion notes: `notes/STORY_SPECIALS.md` (every
Sapphire special / command / sound → Black 2), `notes/STORY_CHAPTERS.md` (the chapter split in detail),
`notes/OPENING.md` (the opening's facts), `notes/RESEARCH_STORY_SPRITES.md`.

## 1. Rules (the user's, all mandatory)
- Follow Sapphire: its scenes, its text **word for word** (`converter/gen3text.py`, `convert(s, expand=True)`), its
  flags and its order. Black 2's own art, sound and engine. Never download anything; never invent a format: read the
  decomp / Black 2's own scripts or test, and say what you found.
- Never delete files (move them to `~/.Trash`). Don't commit (the lead reviews).
- Every script file must assemble (`b2tools/patches/scripts.py` refuses undefined names). Movement lists need
  `.balign 4, 0` before them.
- One emulator at a time, close it after each run, builds and tests under `nice`, tests silent (`b2tools/emu.py`).
- Build only into your own folder (`work/agents/<you>/`); never write `work/rom`, `work/world`, `work/interiors`,
  `work/emu`. Re-read a shared file right before you edit it (other agents edit rooms, scenes, world.py).

## 2. What exists
| Piece | Where |
|---|---|
| Porting library (macros named after Sapphire's commands) | `src/include/hoenn_story.inc` |
| Story ids (FLAG_*/VAR_* → saved Black 2 flags/works) | `data/story_ids.json` → `src/include/hoenn.h` (`converter/gen_story_ids.py`) |
| Sapphire's new-game flags | `src/field_scripts/scenes/new_game_flags.inc` (generated), called by `scenes/truck.inc` Script_30 |
| Trainers (604: every scripted battle + rematch tiers) | `converter/gen_trainers.py` → `data/hoenn_trainers.json` (registry), `src/trainers/*.s`, `src/include/hoenn_trainers.h`, `src/text/system/0381-0383, 0485`, `data/hoenn_trainer_{data,classes,msgs}.json`; patch `b2tools/patches/trainers.py` |
| Trainer NPCs (eye contact, no zone script) | `converter/gen_trainer_npcs.py` → `data/hoenn_trainer_npcs.json`; placed by the `trainers` patch |
| Story objects (NPCs, triggers, signs of scenes) | `data/story/<chapter>.json`; patch `b2tools/patches/story.py` |
| Scenes of generated ("auto") outdoor maps | `src/field_scripts/scenes/<Map>.inc`, `<Map>_init.inc`, `src/text/scenes/<Map>.txt`, merged by `converter/gen_map_content.py` |
| Test build | `HOENN_AGENT=<you> zsh b2tools/story_build.sh` → `work/agents/<you>/rom/hoenn.nds` |

## 3. How a chapter agent works
1. **Read the Sapphire scripts** of your maps (`notes/STORY_CHAPTERS.md` lists them per chapter, with the flags/vars
   you own). Text: `python3 -c "import sys; sys.path.insert(0,'converter'); import gen_trainers as g; from gen3text import convert; t=g.load_texts(); print(convert(t['LABEL'], expand=True)[0])"`.
2. **Where the script goes**
   - Hand-made zone files (Littleroot 0778, Route 101 0634, Oldale 0794, the houses, the Lab 0792 …): add scripts to
     the file (next free `ScriptEntry`), text lines at the end of its text file, map scripts in its init file
     (`NNNN_*_init.s`: `MapScript 2, n` = zone init ≈ Sapphire ON_TRANSITION; `MapScriptConditions` ≈ ON_FRAME_TABLE;
     `MapScript 3/4` = field load / return).
   - Generated outdoor maps (`*_auto_<Map>.s`): never edit the generated file. Write `src/field_scripts/scenes/<Map>.inc`
     (entries between `#ifdef SCENE_ENTRIES` and `#else`, bodies after `#else`), optional `scenes/<Map>_init.inc`
     (the zone's map-script table) and `src/text/scenes/<Map>.txt` (its lines), then run
     `python3 converter/gen_map_content.py`: your scripts become 1..n and your lines 0..t-1; the generated
     signs/people follow. Example: `scenes/Route103.inc`. The world must then be rebuilt (world.py) so the generated
     NPCs' new script numbers reach world.json (the lead's rebuild_slice does both).
   - Rooms: once the lead has moved the room files off Black 2's numbers, story code goes in the room's own file;
     until then put it in `src/field_scripts/scenes/<name>.inc` for the room to include, and give the room's owner
     the `#include` line.
3. **Story objects** (an NPC that appears/disappears with a flag, a step trigger): `data/story/<chapter>.json`
   (format in `b2tools/patches/story.py`): Sapphire map + Sapphire tile, uid (outdoors 100 + Sapphire local id; rooms
   the local id), model (`data/sprite_map.json`; the rival = `RIVAL_GFX` 162 with `h_setup_rival_gfx` in the zone
   init), script, flag/var by hoenn.h name. They are appended after every other NPC of the zone, so no existing
   `ObjInitNPCGPos` index moves; never edit world/room jsons other agents own.
   **Signs of an outdoor map with a story script** don't go in the json (it can't place a signboard model): name the
   sign in its `ScriptEntry` comment, the Sapphire label or `sign (x,y)` (`ScriptEntry Story_HarborSign // 12: sign
   (24,12)`), and `converter/gen_map_content.py` (scene_sign) gives it its event and Black 2 signboard. **People
   sprites**: a zone can show 30 different sprite codes at once (32 billboard materials minus the player's two);
   `python3 b2tools/npc_check.py ROM` checks every zone (notes/NPC_LIMIT.md).
4. **Ids**: use Sapphire's names; every FLAG_/VAR_ a chapter writes already has an id in `hoenn.h`. For a new id
   Sapphire doesn't have, claim one of your chapter's reserved ids (section 6) in `data/story_ids.json` "ids" and
   rerun `python3 converter/gen_story_ids.py`.
5. **Trainers**: plain route trainers are already placed (section 5). Story battles: `h_trainerbattle TRAINER_X`
   (Sapphire names from `hoenn_trainers.h`); the trainer's intro/defeat/after lines and party are already converted.
6. **Build and test** (section 8). Write proofs to `screenshots/<you>/`, notes to `notes/`.

## 4. The library (`src/include/hoenn_story.inc`)
Include `"asm/field_script.inc"`, `"hoenn.h"`, `"hoenn_trainers.h"` (for trainer names), `"hoenn_story.inc"`.
| Sapphire | Macro | Black 2 underneath |
|---|---|---|
| lock / lockall, release + end | `h_lock`, `h_release` | `ActorsPauseAll`; `FinishAllEvents ActorsUnpauseAll VMHalt` |
| faceplayer | `h_faceplayer` | `ActorSetEyeToEye` |
| msgbox X, MSGBOX_NPC / _SIGN (whole script) | `h_msgbox_npc n`, `h_msgbox_sign n` | Black 2's NPC / signpost pattern |
| msgbox X (DEFAULT) | `h_msgbox n` (talked-to NPC), `h_msgbox_actor n, uid`, `h_msgbox_info n` (nobody) | `ParentActorMsg` / `ActorMsg` / `SystemMsg` + `LastKeyWait` |
| a line with {RIVAL} | `h_msgbox_gendered nBoy, nGirl, uid` | `ActorMsgGendered`: write the line twice (May / Brendan) |
| msgbox X, MSGBOX_AUTOCLOSE, closemessage | `h_msgbox_autoclose n`, `h_closemessage` | + `MsgWinCloseAll` |
| MSGBOX_YESNO + compare VAR_RESULT, YES | `h_yesno n, var` + `h_goto_if_yes var, L` / `h_goto_if_no` | `YesNoWin`: **0 = YES** |
| setflag/clearflag/setvar/addvar/copyvar | `h_setflag` … `h_copyvar` | `FlagSet`, `WorkSetConst`, `WorkAdd`, `WorkSet` |
| goto_if_set/unset, call_if_set/unset | `h_goto_if_set f, L` … | `VMStackPushFlag` + `CMP_STACK` (jumps when FALSE: the macro tests the opposite) |
| compare + goto_if_eq/ne/lt/le/gt/ge, call_if_eq/ne | `h_goto_if_eq var, n, L` … `h_call_if_eq` | `WorkCmpConst` + `VMJumpIf CMP_xx` (jumps when TRUE) |
| checkplayergender + goto | `h_goto_if_girl L`, `h_goto_if_boy L`, `h_checkplayergender var` | `TrainerCardGetSex` (0 boy) |
| VAR_FACING | `h_getplayerfacing var` | `PlayerGetDir`: 0 up, 1 down, 2 left, 3 right |
| applymovement / waitmovement / turnobject | `h_applymovement uid, list`, `h_waitmovement`, `h_turnobject uid, dir`, `h_move uid, code, n` | `ActorCmdExec` (player 255), `ActorCmdWait` |
| addobject / removeobject | `h_addobject uid, flag`, `h_removeobject uid, flag` | `FlagReset`+`ActorAdd`; `ActorDelete`+`FlagSet` (ActorDelete alone does NOT set the flag) |
| setobjectxyperm (zone init) | `h_setobjectxyperm index, x, z, dir` | `ObjInitNPCGPos`: **index in the zone's NPC list**, not uid |
| giveitem X, n (+ compare VAR_RESULT, 0) | `h_giveitem ITEM, n` + test `HLIB_RESULT` (1 given, 0 bag full) | global 2805 (room check, pocket jingle, "obtained"/"put in the X pocket") |
| the Pokédex | `h_obtain_pokedex n` + `FlagSet 2402` | Black 2's Pokédex sequence (jingle, Pokédex shown over the player) |
| givemon / getpartysize / checkitem / removeitem / HealPlayerParty | `h_givemon sp, lv, var`, `h_getpartysize`, `h_checkitem`, `h_removeitem`, `h_heal` | `PokePartyAdd`, `PokePartyGetCount`, `ItemCheckAmount`, `ItemSub`, `PokePartyRecoverAll` |
| trainerbattle_no_intro / scripted battle | `h_trainerbattle TRAINER_X` | `CallTrainerBattle id,0,0`; lost → `CallTrainerLose` (whiteout); won → `TrainerFlagSet` |
| battle that continues after a loss | `h_trainerbattle_continue TRAINER_X, var` | `CallTrainerBattle id,0,1` (Black 2's first rival battle) |
| trainerbattle_double against two people (Tate & Liza) | `h_trainerbattle_two TRAINER_TATE, TRAINER_LIZA` | `CallTrainerBattle a,b,0` (two single-style trainers → 1v2); both flags set |
| "need two Pokémon" check of trainerbattle_double | `h_goto_if_cannot_double label` | `PokePartyGetCount var, 2` (able to battle) < 2 |
| trainer intro said by the trainer table | `h_trainer_intro id, uid` | `TrainerBGMPlayPush` + `TrainerSayMessage id, 0` |
| goto_if_defeated / not_defeated, settrainerflag | `h_goto_if_defeated id, L`, `h_goto_if_not_defeated`, `h_settrainerflag` | `TrainerFlagGet/Set` (flag = id + 1520) |
| playse / waitse / playfanfare / waitfanfare / playbgm / fadedefaultbgm / playmoncry | `h_playse` … `h_playmoncry` | `SEPlay`, `MEPlay`, `BGMPlay`, `BGMChangeMap`, `PVPlay` |
| Sapphire sound names | `SE_EXIT`, `SE_LEDGE`, `MUS_OBTAIN_ITEM`, `MUS_ENCOUNTER_MAY`, `MUS_EVIL_TEAM`, `MUS_FOLLOW_ME` … `#define`d to Black 2 ids | guesses marked in the file; the user picks by ear |
| warpsilent / warp with a scene on arrival / setrespawn | `h_warpsilent zone,x,z,dir`, `h_warp_scene zone,x,z,dir,script`, `h_setrespawn n` | `FadeOutBlack` + `RTReserveScript` + `MapChangeCore` (the reserved script starts on black) |
| (a scene that walks the player over a map edge: Sapphire keeps the old map's objects) | `h_zone_hold` (before the walk), `h_zone_release` | map-local flag 0x60: the zone lookup gives each tile its cell's zone until the next map change (b2tools/patches/hoenn_world.py ZONE_HOLD_FLAG; Wally's tutorial) |
| delay N | `h_delay N` | `VMSleep N/2` (the field runs at 30 fps, measured) |
| SetupRivalGfxId | `h_setup_rival_gfx` (zone init) | work 0x4020 = 4 (rival May) / 1 (rival Brendan); NPC model 162 |
Scratch works: `HLIB_TMP` (0x8030), `HLIB_RESULT` (0x8031). Specials and everything else: `notes/STORY_SPECIALS.md`.

Facts behind the macros (all from Black 2's code/scripts; the starred ones measured in the emulator):
- `ActorMsg`/`ParentActorMsg` return when the text is printed; Black 2 closes with `MsgWinCloseAll` alone only when the
  line ends with a page break `{be01}`. Sapphire lines don't, so the macros wait for a key (`LastKeyWait`).
  The opening's scripts had 16 such messages (0778 twin push-back, Script_22, Script_31, `scenes/players_house_1f/2f.inc`):
  fixed 2026-10-07 (`work/agents/story_infra/tests/scan_msgwait.py` lists any left in `src/field_scripts`; the nurse's
  "Okay, I'll take your Pokémon" stays open during the heal and closes by itself, as Black 2's own nurse).
- In-battle trainer lines (type 1, and the mid-battle lines) get the player's name in word 0 like the field ones:
  the trainers patch rewrites ov167 `func_ov167_021d0288` (`b2tools/patches/trainers.py` `battle_trainer_msg`; Black 2
  printed them without the word set, so Sapphire's `{PLAYER}` showed nothing). Only word 0 is set there: use
  `{0100:0}` for the player and no other word in battle lines. Tested: May's "Wow! That's great!\n<player>, you're
  pretty good!" (`screenshots/story_infra/17_*`).

## 5. Trainers
**Format** (decomp `include/asm/trainer.inc`, `docs/data.md`): a/0/9/1 entry N = 20-byte record (party kind, class,
style, count, 4 items, AI flags, money multiplier, reward), a/0/9/2 entry N = party (difficulty = Sapphire's IV
byte, level, species, item, 4 moves). Names: system text 382; class names 383/485; messages: text 381 + a/0/8/9
(trainer, type) records + a/0/9/0 offsets (TrainerMsg_Load, arm9 0x020305d8). Message types (ov036
`s0088_TrainerGetMessageTypes`): single 0 intro / 2 after; double, NPC 3000+N: 3/5/6 (6 = "you need two Pokémon");
second NPC of a pair 5000+N: 7/9/10; 1 = the defeat line in battle. Prize = money × 4 × last level (ov167
btl_calc.c:565) = Sapphire's class base money (×2 for doubles, as Sapphire).
**What the converter does**: every trainer a Sapphire script battles (Sapphire branch, `constants/version.inc`
aliases) + the rematch tiers of `gTrainerEyeTrainers` = 604 trainers; levels from `data/level_scaling.json`;
default-move parties get Sapphire's own level-up moves (Gen 3 learnsets, GiveBoxMonInitialMoveset); moves/items/
species by name (aliases: Self-Destruct, Smokescreen, Parlyz Heal, Thunderstone); Gen 3 AI bits → Black 2 AI flags
(+ TAG_STRATEGY for doubles, as Black 2's doubles); the twins' two defeat lines are joined (Black 2 has one).
**Tate & Liza** (`SPLIT` in the converter; user choice) are two trainers fought together, each with their picture:
`TRAINER_TATE` (= `TRAINER_TATE_AND_LIZA`, id 395, class 118, sprite 124, Solrock) and `TRAINER_LIZA` (780, a spare
class named "Leader", sprite 125, Lunatone), 2 Hyper Potions and half the prize each (the sum = Sapphire's ₽). Black 2's
way to battle two trainers: `CallTrainerBattle a, b, 0` with both single-style trainers (global script 1239 `L_124E`
when two trainers spot you; ov036 `BtlSetup_SetTrainerLocal` → `BtlSetup_SetTrainer1v2`): the porting macro
`h_trainerbattle_two TRAINER_TATE, TRAINER_LIZA` (+ `h_goto_if_cannot_double label` for Sapphire's "need two Pokémon"
check). Music and encounter effect come from the first trainer's class (leader). In battle Black 2 shows each
trainer's defeat line in turn, so Sapphire's two-page defeat text is split by page (Tate: page 1, Liza: page 2:
the dialogue keeps its order). Field lines are Tate's: 0 intro, 2 after, 6 "need two Pokémon" (`TrainerSayMessage
TRAINER_TATE, 6, actor`). Tested: `screenshots/story_infra/18_*` (both pictures, both lines, ₽9200).
**Registry** `data/hoenn_trainers.json` (fixed once given): Black 2 ids 1-528 and 557-813 minus the ids whose flags
Black 2 still touches (daily rebattle 12, gimmick 10 in zone 121: 381-385, stadium resets 132). Ids 529-556 are
never used: their defeat flags (2049-2076) are the opening's story flags. 33 ids are left (Liza took 780).
**Classes and sprites** (`data/hoenn_trainer_classes.json` "review"; arm9 `TRAINER_CLASS_RESOURCES` sprite/sex/
eye-contact music, `SPECIAL_TRAINER_CLASSES` music group, ov036 `SPECIAL_TRAINER_ENCEFF`/`_BGM`):
- Kept Black 2 classes for the same roles (Youngster, Lass, Hiker, Fisherman, Swimmers, Psychics, Black Belt, Battle
  Girl, Lady, Rich Boy, Gentleman, Beauty, Pokéfans, Breeders, Rangers, School Kids, Twins, Guitarist); Sapphire's
  Cooltrainers are Black 2's Ace Trainers, named "Ace Trainer" (user choice; the converter's `B2_CLASS_NAME`).
- Hoenn art: Brendan/May (classes 0/1, the player's), Wally (145, Hugh's class, sprite 127), Aqua grunts (187/188),
  Archie (189), Shelly (191), Matt (192, sprite 152), Hoenn leaders on Unova's leader classes 112-119 (PWT sprites
  118-123, Tate 124, Wallace 140; Liza 125 on spare class 229), Elite Four on 78-81 (sprites 77-80 redrawn), Steven = Champion 193
  (sprite 139).
- Special classes: Black 2's character cut-ins (Unova leaders, Elite Four, Iris, Hugh, Plasma, Ghetsis) are replaced
  by encounter effect 5 (Black 2's plain outdoor trainer effect) for every Hoenn trainer of those classes. This also
  fixes the white-screen hang of Elite Four battles outside the League (tested: Sidney in Littleroot). Music: gym
  leaders `SEQ_BGM_VS_RS_LEADER`, Champion `SEQ_BGM_VS_RS_CHAMP` (Black 2's own PWT Hoenn themes), Wally the normal
  trainer theme, Shelly the grunts' theme (Sapphire's admins share it).
- Hoenn-only classes on spare classes with stand-in Black 2 pictures: Aroma Lady (13), Ruin Maniac (27), Interviewer
  (22, Gabby & Ty), Tuber F/M (14/15), Hex Maniac (179), Pokémaniac (32), Kindler (56), Camper (72), Picnicker (28),
  Bug Maniac (51), Bug Catcher (110), Expert M/F (69/70), Triathletes (cycling 89/90, running 52/6, swimming 83/84),
  Dragon Tamer (100), Bird Keeper (109), Ninja Boy (15), Sailor (82), Collector (58), Sr. and Jr. (62), Young Couple
  (68), Old Couple (74), Sis and Bro (16). **For review** (the user): every stand-in picture.
**Trainer NPCs** (`converter/gen_trainer_npcs.py`): evType 1, param0 = Sapphire's sight, script 3000 + id (5000 + id
for the second twin), move code from Sapphire's movement type (decoded from ov036's movement tables: 2 look around,
6-13 and 45/46 look in 2-3 directions, 14-17 face, 18/19 spin, 3-5 wander). 197 placed outdoors (warp-only maps such as Petalburg Woods included); Black 2's global
trainer script does sight, "!", walk-up, intro, battle, flag and the after line. Not placed (`data/hoenn_trainer_npcs.json`
"not_placed"): **story** 64 (more than battle + one line, or a hide flag: rival, Wally, Aqua, gym gimmicks …),
**owned** 35 (rooms owned by agents: gyms, Mt. Pyre, …: their owners add them), **unbuilt** 53 (caves, Trick House, S.S. Tidal, Victory Road).
38 movement types are approximated (walk sequences → look around).
Not done: rematches (Sapphire's Trainer's Eyes; ids allocated), music choices (stand-ins).

## 6. Ids (`data/story_ids.json`, `converter/gen_story_ids.py`)
Survey (2026-10-06: Black 2 code of main + every overlay with a register-tracking scanner, all 1289 script files,
zone entities; conservative): free saved flags 874 outside the item balls (1100-1499) and trainer flags (1520-2333);
free saved works 277. Not free: flags 0-0x63 / works 0x4000-0x401F (wiped on map change), works 0x4020-0x402F
(dynamic sprites), 2400-2719 (Black 2 system, fly flags, medals; hoenn.h's old claim of 2816-2962 was wrong),
2720-2819 (reset every midnight), 2820-3032 (Black 2 hidden items). Field gimmicks still run in zones 121, 137, 97,
98, 108, 29, 561, 564 unless a/1/0/2 is edited (side finding).
Allocation: every var/flag a chapter is the first to write ("home", from the chapter survey) has an id now — 81 vars,
474 flags, grouped by chapter in hoenn.h; `FLAG_DAILY_*` sit in 2744-2792 (Black 2 resets them at midnight like
Sapphire); `FLAG_SYS_POKEMON_GET`/`B_DASH`/`GAME_CLEAR` = Black 2's 2401/2403/2400; badges are Black 2 badges
(`TrainerCardAddBadge n`, `TrainerCardHasBadge var, n`, n = gym − 1); `FLAG_HIDDEN_ITEM_*` are left for a
hidden-item converter (Black 2's own hidden-item entries). Reserved per chapter for new ids:
| Chapter | Ids given | Reserved flags | Reserved works |
|---|---|---|---|
| Ch0 | 49 | 114-122, 125-130, 133 | 0x403D-0x4040, 0x4042, 0x4056 |
| Ch1 | 43 | 231-232, 235-245, 248, 250, 254 | 0x405F-0x4064 |
| Ch2 | 55 | 314-324, 329, 331, 333-335 | 0x406C-0x4071 |
| Ch3 | 88 | 430-443, 445-446 | 0x408E-0x4093 |
| Ch4 | 46 | 490, 492-506 | 0x409F, 0x40A1-0x40A4, 0x40A6 |
| Ch5 | 18 | 524-539 | 0x40A9-0x40AA, 0x40AC-0x40AF |
| Ch6 | 25 | 563-578 | 0x40B2-0x40B6, 0x40B8 |
| Ch7 | 37 | 618-620, 622-626, 632-639 | 0x40BC-0x40C1 |
| Ch8 | 71 | 714-715, 719-720, 725-726, 728-729, 732, 738, 742, 744-745, 747-748, 750 | 0x40CE, 0x40D2-0x40D6 |
| Ch9 | 31 | 813, 815-820, 827, 829-831, 835-838, 840 | 0x40D9-0x40DE |
| Ch10 | 32 | 906-911, 943, 947-949, 952, 954, 956, 958-959, 961 | 0x40EE-0x40F3 |
| Ch11 | 18 | 1024-1027, 1036, 1038-1040, 1051-1058 | 0x40F6-0x40FB |
| Ch12 | 16 | 1075-1090 | 0x40FC-0x4101 |
| Ch13 | 24 | 1513-1519, 2334-2342 | 0x4104-0x4109 |
| S_common | 2 | 2345-2360 | 0x410D-0x410F, 0x4112-0x4114 |
About 270 flags and 190 works stay unallocated for later.

## 7. Movement actions (in lists: Sapphire's names are macros of hoenn_story.inc)
Codes = ov036's action table (0x021cca50 + 38) and the movement probe (`HOENN_TEST_MOVES=1`: the player's house
sign plays every group; `work/agents/story_infra/tests/moves_probe.py` logs the tile each frame). Up/down/left/right:
| Sapphire | Codes | Measured |
|---|---|---|
| face_* | 0-3 | |
| walk_slow_* / walk_* / walk_fast_* / walk_fastest_* | 8-11 / 12-15 / 16-19 / 20-23 | 16 / 8 / 4 / 2 field frames a tile* |
| walk_in_place_slow_* / walk_in_place_* / _fast_* / _fastest_* | 28-31 / 32-35 / 36-39 / 40-43 | 8* and 2* frames for 32-35 and 40-43 |
| jump_in_place_* | 48-51 (44-47 = slower) | |
| jump_* (one tile) / jump_2_* / (three tiles) | 52-55 / 56-59* / 92-95* | 2* and 3* tiles |
| delay_1/2/4/8/16 | 60, 60, 61, 62, 63 (60-66 = 1, 2, 4, 8, 15, 16, 32 field frames) | code 63 = 8 frames* |
| set_invisible / set_visible, lock/unlock_facing_direction | 69 / 70, 71 / 72 | |
| emote_exclamation_mark / emote_question_mark / (heart: none) | 75* / 159* / 160 music note*, 161 "…"* | `screenshots/story_infra/07_*` |
NPC move codes for entities: section 5. The opening's delays were twice Sapphire's (delay_48 as `Move 63, 6`,
delay_8 as `Move 63, 1`, delay 15/10 as `VMSleep 15/10`): fixed 2026-10-07 to this table (delay_48 = `Move 63, 3`,
delay_16 + delay_8 = `Move 63, 1` + `Move 62, 1`, delay N = `VMSleep N/2`).

## 8. Building and testing
- `HOENN_AGENT=<you> zsh b2tools/story_build.sh` (`GEN=1` reruns gen_map_content first). It uses `work/world` and
  `work/interiors` read-only; when they lag behind the shared data, clone them into your folder and point
  `HOENN_WORLD_DIR` / `HOENN_INTERIORS_DIR` there (APFS `cp -c -R` is free). If you changed a scene of an auto map,
  your world copy needs world.py's renumbered NPC scripts (or the lead's next rebuild).
- Since v12 build_rom.py has RESERVE[92]/[89] and story_build.sh uses the v12 patch list: `work/emu/base_*.dst` (the
  lead's) match your build's layout (tested 2026-10-07). While agents add rooms, build with
  `HOENN_SKIP_UNBUILT_ROOMS=1`. Your own states (if a change moves the layout): copy `b2tools/make_states.py` with
  `OUT` = your folder (the opening replays in ~90 s). `base_after_rival.dst` = Littleroot north exit before Route 101.
- Room files you share with a generator: put your scripts after `// ---- story` (notes/STORY_COMMON.md "Room scripts
  shared with a generator": reruns keep them).
- **Test switches per chapter** (`HOENN_TEST_CH<n>`, 2026-10-07): every environment variable `HOENN_TEST_CH<n>=v` is
  passed to the script assembler as `-D HOENN_TEST_CH<n>=v` (b2tools/patches/scripts.py; nothing to register). In
  your own scene file (an outdoor map's init `scenes/<Map>_init.inc`, or the first map of your chapter), put the
  start-of-chapter state under `#ifdef HOENN_TEST_CH<n>`: the earlier chapters' flags and vars (data/story_ids.json),
  badges (`h_givebadge N`), party (`PokePartyAdd`), key items (`h_giveitem`, src/include/hoenn_key_items.h), and the
  warp to where your chapter starts; guard it with a flag of yours so it runs once. Build with
  `HOENN_TEST_CH3A=1 HOENN_AGENT=ch3a zsh b2tools/story_build.sh` and test from `work/emu/base_*.dst`. Never put
  test code outside `#ifdef`: normal builds must not change.
- Walking: `emu.travel(x, z)` routes through the world's collision (`HOENN_WORLD_DIR` for your copy); after a scripted
  movement or a warp, calibrate on the tile you know (`e.calibrate(x, z)`; several actors can match). The starter
  screen takes the d-pad (RIGHT RIGHT A A for Mudkip). `HOENN_TEST_NO_WILD=1` for walks; `HOENN_TEST_PARTY=1` gives a
  Lv 50 Mudkip when the party is empty; `HOENN_TEST_TRAINER=TRAINER_A+TRAINER_B` puts eye-contact trainers in
  Littleroot (176,358)+; `HOENN_TEST_WARP=zone,x,z` warps from Littleroot's sign (talking is dead until a real warp).
- Cold boot for boot-time data: `fresh_battery()` on a uniquely named ROM copy (notes/TESTING.md).

## 9. Worked example: Route 103 → Oldale → the Pokédex (chapter Ch1, tested 2026-10-06)
Files: `scenes/Route103.inc` + `Route103_init.inc` + `src/text/scenes/Route103.txt` (rival talk, battle by starter,
exit around the player and over the ledge, flags), `0794_oldale_town.s` scripts 7-11 + `0795_oldale_town_init.s` +
two lines of `0626` (the rival's three triggers, "Let's hurry home!"), `0778` Script_9 (Sapphire's
MoveRivalFromOldale), `0792_birch_lab.s` scripts 10/12/13 + `0793_birch_lab_init.s` + 14 lines of `0625` (the
Pokédex: walk up 7, Birch, the Pokédex sequence, the rival's Poké Balls, state 5; the rival's talk; Birch's state-5
line), `data/story/ch1.json` (rival NPCs on Route 103, in Oldale and in the Lab; Oldale's triggers),
`scenes/new_game_flags.inc` (FLAG_HIDE_RIVAL_* start set). Tested from a new game on the story_infra ROM (states
remade with this ROM): Route 101 rescue → Mudkip → Lab → Route 103 → May's battle (Treecko Lv 5, ₽300) → May leaves
around the player and jumps the ledge → Oldale trigger → Lab: Pokédex, 5 Poké Balls, May and Birch's next lines.
Proofs: `screenshots/story_infra/10_*`-`16_*`. Not ported yet: Oldale's Mart employee (Potion) and footprints man,
Littleroot's rival/Mom changes after the Pokédex, Petalburg (Norman, Wally's catch).

## 10. Chapters (details: `notes/STORY_CHAPTERS.md`; ids per chapter: `data/story_chapter_ids.json`)
Every Sapphire map file has one owning chapter; a beat of another chapter in that file goes in as a scene include.
"In progress" = built in another agent's test ROM (standalone maps, Aqua Hideout), not yet in the main build.
| Ch | Story (badge) | State | Blocking maps / in progress |
|---|---|---|---|
| Ch0 | Opening | done | |
| Ch1 | Route 103 rival, Pokédex (done), Petalburg (Norman, Wally), Petalburg Woods, Rustboro: Roxanne (1) | unblocked | in progress: PetalburgWoods |
| Ch2 | Devon Goods, Rusturf Tunnel, Mr. Stone, Mr. Briney, Dewford: Brawly (2), Granite Cave: Steven | unblocked | |
| Ch3 | Slateport, Route 110 rival, Mauville: Wattson (3), Verdanturf (largest: split 3a/3b) | unblocked | Trick House 2-8 optional, not built |
| Ch4 | Routes 111-115, Fiery Path, Fallarbor, Meteor Falls | **blocked** | MeteorFalls_1F_1R |
| Ch5 | Mt. Chimney, Jagged Pass, Lavaridge: Flannery (4) | unblocked | in progress: MtChimney, JaggedPass |
| Ch6 | Norman (5), Surf, Routes 105-108 (+ Ch12: small) | unblocked | Abandoned Ship, New Mauville optional |
| Ch7 | Routes 118-120, Weather Institute, Fortree: Winona (6) | unblocked | |
| Ch8 | Lilycove rival, Mt. Pyre, Slateport sub, Aqua Hideout | unblocked | in progress: MtPyre_Exterior/Summit, AquaHideout_1F/B1F/B2F |
| Ch9 | Routes 124-127, Mossdeep: Tate & Liza (7), Dive | unblocked | Black 2 has no Dive: needs a decision |
| Ch10 | Seafloor Cavern, Sootopolis, Cave of Origin, Wallace (8) | **blocked** | underwater maps, SeafloorCavern_*, CaveOfOrigin_* (in progress: SootopolisCity) |
| Ch11 | Victory Road (Wally), Elite Four, Steven, Hall of Fame | **blocked** | VictoryRoad_1F/B1F/B2F, EverGrandeCity_HallOfFame (left out as a link room) |
| Ch12 | Routes 129-134, Pacifidlog, Regi puzzle (optional) | unblocked | Regi caves optional |
| Ch13 | Post-game (optional): S.S. Tidal, Battle Tower, Southern Island, Sky Pillar | **blocked** | BattleTower corridor/elevator, SSTidal*, SkyPillar_* |
| S_common | common scripts every chapter calls (Pokémon Center, Mart, PC, …) | lead first | |
