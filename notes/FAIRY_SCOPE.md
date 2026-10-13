# Fairy type (Gen 6 rules) in HoennB2: scope (fairy_scope, 2026-10-08)

Read-only research. Sources: the decomp (external/pokebw2: C in src/, `tools/dsd dis` of every module, symbols in
config/b2_us/arm9), the vanilla NARCs (build/b2_us/files), and our src/ and data/. Addresses are RAM addresses. Ratings:
**trivial** (data byte), **easy** (small patch in place), **medium** (relocation, several sites, or new code),
**hard** (many sites or new code paths). Nothing in external/ has Gen 6 data (grep for TYPE_FAIRY/MOONBLAST: none), so
Gen 6 move stats and learnsets would be typed in by hand.

**Short version:** Fairy = type id **17**. In Black 2, 17 also means "no type", so every such check moves to 18 (about
30 one-byte sites). The type chart has to be moved (no slack after it). Most UI is data-only, because type 17 lands on
an unused contest icon. Five screens preload 17 icons and need code. New moves past 559 need an animation-remap hook.
Items fit in free ids 113-133, but each held-item effect needs new battle code. **Recommended design:** one ROM per
version, with Birch asking "Fairy type on/off?" in the intro (section 7). This replaces a separate-builds switch.

## 1. Where Black 2 assumes 17 types (code)

### 1.1 Type chart and the "17 = no type" value
| What | Where | How it works / change for Fairy | Rating |
|---|---|---|---|
| Type chart | `data_ov167_021d7500` (btl_calc.c:56), file offset 0x3DC40 in arm9_ov167.bin | `u8[17][17]`, attacker x defender, values 0/2/4/8. 289 B + 3 pad, then Stall's handler table `data_ov167_021d7624`. 18x18 = 324 B, so it **must move** (ITCM, see 5.1) or be packed into the same slot as 4-bit values (162 B) | medium |
| Chart reader 1 | GetTypeEffectiveness 0x021bd160 (pool 0x021bd1ac; x17 stride `lsls #4; adds` at 0x021bd16c) | New pointer, stride 18. Its 0/2/4/8 switch can go if the table stores the result directly, which frees room in place | medium |
| Chart reader 2 | GetTypeWeaknesses 0x021bd2b0 (pool 0x021bd2e4, stride 0x021bd2b2-b6, loop `cmp #0x11` 0x021bd2d8) | Same; used by Conversion 2 | medium |
| Other readers | none in any module (asm + literal pools searched) | - | - |
| PWT copy of the chart | ov055 0x021e73d4 (wbt_system.c:468), its own 17x17 | Separate edit (only matters for simulated PWT matches; our PWT is planned) | medium |
| 17 = no type, ov167 (16 instructions) | GetTypeEffectiveness 0x021bd160/164; Roost splitTypeCore 0x021bafc4/afd6/afe2/afe6/aff4; DoesMonHaveType 0x021bb01a; last-move-type default 0x021ba6a8/0x021bab8e/0x021bc522; Color Change 0x021bf822; Conversion 2 0x021c9e30; no-STAB 0x021a5a52; neutral skip 0x021aa966; Struggle 0x021aa066 | Each is a 1-byte immediate: 17 -> 18 | trivial (x16) |
| 17 = no/any type, elsewhere | Pokédex entry ov296 (0x0219ecc0, ee10 set; ee7a, ee98, eed4, eef2, ef24, ef5e, effc, f12e, f6d6, f6ec compare); arm9 func_0201f14c 0x0201f1b2 (party check, 17 = any); PWT wbt_system.c:315 default, scrcmd_wbt.c:46-48 | 17 -> 18 | easy |
| Data | no move (data/moves) and no species (data/personal) has type 17; no 0x1111 type-pair constant | none | - |
| Gen 6 Steel change | chart [Ghost][Steel] and [Dark][Steel] 2 -> 4 | data in the new chart | trivial |

### 1.2 Loops and fixed-size per-type arrays
| What | Where | Change | Rating |
|---|---|---|---|
| GetTypeWeaknesses loop | 0x021bd2d8 `cmp #0x11` | -> 18 | trivial |
| PWT type counts | ov055 wbt_tool.c:118-150 `counts[17]`, `types[17]` (skips 17, so Fairy is ignored safely) | resize if PWT should know Fairy | medium |
| Medal Rally | ov065 `TYPE_COUNT 17`; types read from a/2/3/9 entry 0 (301 records) | leave that archive at Gen 5 types, or `typesCaught[17]` overflows | trivial (don't touch) |
| Monotype champion medals | ov012 0x0215a684 (event_game_clear.c:287) `typeCounts[17]` on the stack; index 17 hits padding | harmless; no Fairy medal | - |
| Trainer AI (ov170, C) | no type loops or tables | none | - |
| Hidden Power | HandlerHiddenPowerType 0x021c8b04 -> getHiddenPowerType 0x0201d7c0: idx = IV bits x15/63 (0-15), `hpTypes` 0x02090358 = 1..16 | none: never Fairy, as in Gen 6 | - |

### 1.3 Arceus, type-changing effects, items
| What | Where | Change | Rating |
|---|---|---|---|
| Plate -> type | arm9 PML_ItemGetArceusPlateType 0x0201ee48: `item-298`, 16-case switch (items 298-313; 314 is Odd Incense). Used for battle type (PML_PkmGetParamCore 0x0201e366) and Arceus's form (form = type id) | Pixie Plate at another id needs a compare + redirect | medium |
| Judgment | ov167 HandlerJudgement 0x021c89c8, its own copy of the switch | Replace with `bl PML_ItemGetArceusPlateType` (same results, frees ~100 B) | easy |
| Plate can't be knocked off | ov167 0x021cde78 -> ov169 list 0x0689e514 (16 u16, count `movs r2,#0x10` 0x0689cb0c, packed) | Relocate list or add a check | medium |
| Arceus form on give / PC | ov165 func_ov165_021a02c8, ov255 func_ov255_021bcabc (form = plate type) | none | - |
| Conversion 0x021c5c90, Color Change 0x021bf7ec, Reflect Type 0x021cd05c, Soak 0x021ccb6c, Normalize 0x021bf948, Weather Ball 0x021c8780, Camouflage 0x021c5d40 (terrain switch), Pledges, Techno Blast 0x021c8a84 | - | none beyond the 17->18 sites. No Protean-like ability in Gen 5 (last ability 164) | - |
| Natural Gift | 0x021c8bc4: type = item param 0xc (5 bits in item data) | data | trivial |
| Held-item dispatch | ItemEvent_AddItemCore 0x021c26ec: linear search of 172 `{item, EventAdd}` at `data_ov167_021d8f28`, count `cmp #0xac` 0x021c273a. **One free slot** (index 171 = {0, NULL}) | 2+ new items: relocate the table | medium |
| Gems | items 548-564; per-gem thunk `mov #type` -> CommonGemDecide 0x021c59fc / CommonGemPower 0x021c5aac | Fairy Gem: new thunk + 3-entry table + EventAdd (~64 B) + slot | medium |
| Resist berries | items 184-200; thunk (type, isChilan) -> CommonResistBerry 0x021c3500 | Roseli: same, **plus** BERRY_ITEM_IDS 0x02090b4c (64 u16, PML_ItemIsBerry loops 0x40) and the 64-slot berry pocket are full | hard (or skip / overwrite a berry) |
| Type boosters, plates | thunk `mov r3,#type` -> CommonTypeBoostingItem 0x021c5164; plates reuse booster tables | Pixie Plate: new thunk + table + slot | medium |

### 1.4 AI and messages
| What | Where | Change |
|---|---|---|
| Trainer AI | ov170 AIIfTypeEffectiveness 0x02180658, AIIfHasSuperEffectiveMove 0x02181278, AIDoesMonHaveType 0x02180d94; switch AI ov167 0x021b509c-0x021b5cd2: all go through the engine's chart | none (optional Fairy-aware AI scripts in data/tr_ai) |
| "It's super effective!" etc. | func_ov167_021a504c (std 0x4e/0x4f -> text 0017/0019 lines 79-80), func_ov167_021a9358 (0018 lines 7-24), "doesn't affect" 0018 lines 211-213 | none: picked by effectiveness value |

### 1.5 Text
| File | Use | Change | Rating |
|---|---|---|---|
| 0398_type_names (17 lines) | loadTypeTextToStrbuf 0x02024598 (battle, script WordSetPokeTypeName ov036 0x021a78bc, PC box): no bound | + line "Fairy". HOENN_TEXT_SLOTS spare 88 B | trivial |
| 0479 Pokédex search labels | blank messages 77-94 free | + "Fairy" | trivial |
| 0397 Xtransceiver matchup comments (153 = 17x18/2) | ov259 0x0219fa92 `mov r2,#0x11` | -> 0x12, rewrite as 171 entries | easy |
| 0489 (upper-case names, no code ref found), 0000 questionnaire, 0080/81/83 medals, 0411 PWT | - | leave | - |

## 2. Type UI
| Asset / screen | Where | 18th entry | Rating |
|---|---|---|---|
| Type icons | a/0/8/2: entries 34-50 = 17 types (32x16 NCGR), **51-55 = unused contest icons**, 56-58 categories, palette entry 33 (3 rows used). Icon = `type+0x22` (arm9 0x0202d7f4), palette row = `data_0209208c[type]` (0x0202d7e8, 24 B) | Type 17 -> entry 51: replace its graphic, set byte 0x0209209d to 1 or 2, put the pinks in free colours (row 2 colours 8-13, row 1 colour 13) | trivial |
| On-demand screens: battle party/move info ov287, ov288, Move Reminder ov258, trade ov194, Pokéstar ov322 | load the icon by type when drawn | ready with the icon edit | trivial |
| Battle move buttons | ov168 func_ov168_021ed81c; colour = a/0/1/1 entry from `data_ov168_021f3864` (17 u32 -> entries 464-480; 463 empty; next table follows directly) | Append a pink NCLR (a/0/1/1 entry 572) + move or hook the table | medium |
| Summary | ov207 func_ov207_021b36a4 preloads 17 icons at work+0x130 (loops 0x021b3a1a, 0x021b3cec); +0x174 is another field | 2 bounds + move the array | medium |
| Bag (TM move type) | ov142 func_ov142_0219d7a8: 17 graphics work+0x5ac, 17 sprites +0x6e0 (loops 0x0219dadc, 0x0219dc4a; frees 0x0219de3c, 0x0219e15e) | move arrays | medium |
| Bag TM disc icon | arm9 0x02090d50 per item {char, palette} into a/0/2/5 (TM char 397, type palettes 398-413 + 610) | append an NCLR (a/0/2/5 entry 1025), point the Fairy TM at it | trivial |
| PC box | ov255: 17 graphics work+0xa268 (loop 0x021d0806), 17 sprites in slots 0x20+i (0x021d09ca), hide loop to 0x31 (0x021bf2c0) | move arrays, check slot 0x31 | medium-hard |
| PC search | no search by type (name filter only, text 0013 lines 150-155) | none | - |
| Pokédex entry | ov296: preloads 17 (0x0219ed70/0x0219edc4); icon array work+0x12c runs into the type bytes +0x170/171; 17 = "no 2nd type" (1.1) | ~12 one-byte sites + move the array; unpatched, a Fairy is never shown | medium-hard |
| Pokédex search by type | ov300 func_ov300_021a3d04: list of 17 (`cmp r4,#0x10` 0x021a3da2), labels `data_ov300_021a40ae` ([17] at 0x021a40d0 is "-", unused); search ov302 0x021adf0c is generic | 1 byte + 1 u16 + text 0479 | easy |
| Hall of Fame | ov265: particles `data_ov265_0219b8cc` (a/2/1/3 entries 34-50), palettes `data_ov265_0219ba98` (last data in the overlay: type 17 reads past its end) | new particle a/2/1/3 entry 52, a palette, relocate/guard | medium |
| Arceus Fairy form | personal 0493 `Forms 0, 0, 17` -> 18; battle palette `0x3ab9 + shiny + 2*(form-1)` in a/0/0/4 (15065 entries, none spare): append 15065/15066; box icon shared (icon 994) | data | trivial |

## 3. Data changes
### 3.1 Species (a/0/1/6, 0x4c-byte records; same size, no patch of ours edits it)
22 species, **trivial**. Gen 5 types read from data/personal; none of the alternate-form records (685-708) changes.

| Species (dex no.) | Now | Gen 6 | Hoenn dex |
|---|---|---|---|
| Clefairy 35, Clefable 36, Cleffa 173 | Normal | Fairy | (233, National) |
| Jigglypuff 39, Wigglytuff 40, Igglybuff 174 | Normal | Normal/Fairy | 138, 139, 137 |
| Mr. Mime 122, Mime Jr. 439 | Psychic | Psychic/Fairy | - |
| Togepi 175 | Normal | Fairy | (325) |
| Togetic 176, Togekiss 468 | Normal/Flying | Fairy/Flying | - |
| Marill 183, Azumarill 184 | Water | Water/Fairy | 55, 56 |
| Azurill 298 | Normal | Normal/Fairy | 54 |
| Snubbull 209, Granbull 210 | Normal | Fairy | (352) |
| Ralts 280, Kirlia 281, Gardevoir 282 | Psychic | Psychic/Fairy | 29-31 |
| Mawile 303 | Steel | Steel/Fairy | 69 |
| Cottonee 546, Whimsicott 547 | Grass | Grass/Fairy | - |

### 3.2 Moves (a/0/2/1, 0x24-byte records)
Sweet Kiss 186, Charm 204, Moonlight 236: Normal -> Fairy, **trivial**. All three are status moves, so after the retypes
Black 2 has **no damaging Fairy move**. Without section 4, Fairy is a defensive type only.

### 3.3 Items
- **Ids:** ITEM_LAST = 638 (a/0/2/4, 639 x 36 B).
  - Free ids: 113-115, 120-133 and 426-427 ("???", zero data, "?" icon). Ids 505-531 are probably free too.
  - None of these is taken by us. Ours: 99, 100, 216, 428-481 (various), 534-536, 574, 621, 626.
  - Ids above 638 are **hard**: about 30 clamps, e.g. PML_PkmGetParamCore treats a held item above 638 as 0.
- **Per new item, at a free id (easy):**
  - item data;
  - 4 text lines: 0064 / 0481 / 0482 names, 0063 description (slots have 1.2-7 KB spare);
  - icon pointer (arm9 0x02090d50: plate char 619, gem char 934, plus a new palette);
  - pocket byte (ITEM_CATEGORIES 0x0208f4d0).
- **Battle effects:** see 1.3. Pixie Plate and Fairy Gem are medium; Roseli Berry is hard as a 65th berry.

### 3.4 Gen 6 chart
| Side | Effect |
|---|---|
| Fairy attacking | x2 vs Fighting, Dragon, Dark; x0.5 vs Fire, Poison, Steel |
| Fairy defending | x0.5 from Fighting, Bug, Dark; x0 from Dragon; x2 from Poison, Steel |
| Steel defending (Gen 6 change) | Ghost and Dark now x1 |

## 4. New Fairy moves
- **No unused move ids:** all 559 are distinct, real moves.
- **Move-count assumptions:** Metronome (btl_calc.c:69 allocates 0x230, :461 loops to 0x22f: 2 constants, easy) and
  the animation split below. Pokémon/trainer/learnset move fields are u16 with no clamp. Fest Mission and gift checks
  can be ignored.

| Piece per new id 560+ | Where | Rating |
|---|---|---|
| Move record | append to a/0/2/1. Effects are all data: Moonblast like Mist Ball (SpA -1, 30%); Play Rough like Aurora Beam (Atk -1, 10%) + contact; Dazzling Gleam adjacent foes; Disarming Voice accuracy 101 + sound + spread; Draining Kiss DrainHeal 75 (read from data, btl_server_flow.c:3557-3560); Fairy Wind plain. No handler needed | easy |
| Text | 0403 + 0488 names (1,060 B spare each, ~29 names), 0402 descriptions (6,892 B), 0016 "used" lines (3 per move, 6,680 B). text.py only replaces lines (`text[int(i)] = v`): needs an append mode | easy |
| Animation | ov168 func_ov168_021e0ee8: id < 0x231 -> a/0/6/5[id], else a/0/6/6[id-0x231] (status effects). a/0/6/5 has 41 filler slots (560-600 = copies of Pound), but only 560 is reachable. **561+ need a remap hook** in func_ov167_021cfc60 (btlv_core.c:1111) to a donor move's animation | 560 easy, 561+ medium |
| Learnsets | a/0/1/8 (`.2byte move, level`, no 9-bit limit), egg moves a/1/2/4, TM list arm9 0x02090c84 (101 u16: overwrite one), tutors ov036 0x021d0b38.. (60 entries, 12 B each) | easy (data typed by hand) |
| Our converters | gen_trainers.py:350/466-481 needs MOVE_ constants for new names; gen_items.py:25-36 maps Gen 3 TMs through the TM list | easy |

- **Cheapest honest path:** append 6 moves at 560-565 (Fairy Wind, Disarming Voice, Draining Kiss, Dazzling Gleam,
  Play Rough, Moonblast), add one animation-remap hook, and put a/0/2/1 / a/0/1/8 / a/1/2/4 in RESERVE.
- **The trivial alternative:** overwrite 6 existing moves. That is pure data, but loses real moves.

## 5. Fit in our build
### 5.1 Our patches and code space
| Patch | Overlap | Note |
|---|---|---|
| exp_share.py | ov167 0x021aee70-0x021aeef8, 0x021aef8a, 0x021a8e68/8dec; arm9 0x02005050-7f; item 216 | Same binaries, different bytes. It already used the only dead ov167 block. Its ov167 code reads an event flag in battle (template for the Fairy flag hook) |
| trainers.py | ov167 0x021d0288 (trainer lines), arm9 class table | no overlap |
| hm_free.py | arm9 0x02005080-0x02005123 (last free arm9 bytes) | arm9 has no free bytes left |
| hoenn_world.py, roamers.py | ITCM: ZoneLookup 1,066 B + roamers 1,414 B; arena now starts 0x01FF9D80 | **~25 KB of ITCM free** (to 0x02000000). Use it for the chart (324 B), item thunks/tables, the hooks. Run after roamers |
| text.py | fixed slots | fits (1.5, 4) |
| hoenn_intro.py | ov162 0x021a022a, ov294 intro table 0x277c-0x27ac (RIVAL_PICTURE) | the toggle edits the same table (section 7) |
| trade_evos, shops, gen_key_items | a/0/2/4 in place, item lines | free ids avoid ours |
| (none) | a/0/1/6, a/0/2/1, a/0/1/8, a/0/8/2, a/0/1/1 | free to edit |

- **ov167 can't grow:** it ends at 0x021dda60, which is where ov168 and ov171 start, and ov168 is loaded with it in
  battle. Its ROM slot has 272 B slack.

### 5.2 Savestates and layout
- **Code:** the ITCM additions grow arm9 and change ov167/ov168/ov296/... sizes. That is one layout change: remake
  the base states.
- **Data:** appending moves, items, palettes and icons grows archives that are not in RESERVE: 21, 18, 124, 11, 25, 4
  and 213 (65 if animations are added). Add them to RESERVE once, in every build, so all ROMs keep one FAT.
- **With separate builds (5.3):** 4 ROMs, each with its own state set. Savestates carry arm9, as with Ruby (RUBY.md
  WP1/WP2 results).
- **With the in-game toggle (7):** still 2 ROMs and 2 state sets.

### 5.3 A HOENN_FAIRY build switch (the alternative to section 7)
- `version.py`: `FAIRY` from HOENN_FAIRY=0|1, `-D HOENN_FAIRY`, and `build_dir()` suffix `_fairy`.
- `patches/fairy.py` comes last in rebuild_slice.sh / story_build.sh and is a no-op when off, so off-builds stay
  byte-identical.
- Release files `Pokemon_{Sapphire,Ruby}_NDS_Fairy_vNN`.
- Cost: easy infrastructure, but 4 ROMs, 4 state sets, 4 .bps files and doubled battle tests.

## 6. Game impact in Hoenn
Read from src/trainers (+ ruby/) and src/encounters. Level scaling (converter/level_scaling.py) is exp-only: **no level changes**.

### 6.1 Pokémon that change
| Group | Pokémon |
|---|---|
| Wild, both versions | Ralts (Route 102, 4% slot, Lv 4); Marill (Route 117 grass; surf in Petalburg and Routes 102/111/114/117/120); Jigglypuff (Route 115) |
| Wild, Ruby only | Mawile: Granite Cave, Cave of Origin, Sky Pillar, Victory Road |
| Other | Azurill by egg |
| Not affected | No post-game legendary, roamer or gift |

### 6.2 Trainer fights
**Totals, both versions:**
- Retyped species: 65 party slots in 54 trainers (Marill 28, Azumarill 9, Ralts 8, Kirlia 8, Gardevoir 5, Azurill 4, Mawile 3).
- Dragons: 28 slots in 17 trainers.
- Dark: 111 slots in 82 trainers (Sapphire) / 87 in 75 (Ruby).
- Charm/Sweet Kiss/Moonlight: 42 slots in 33 trainers (cosmetic).

| Fight | Change |
|---|---|
| Drake (0388): Shelgon, Altaria, Flygon x2, Salamence | All Dragon, so Fairy is x2 on them and immune to his 8 Dragon moves. Biggest swing |
| Wally (0645, 0742-0745) | Gardevoir 49-63 becomes Psychic/Fairy, but has no Fairy attack unless given one. His Altaria becomes Fairy-weak; Delcatty's Charm becomes Fairy |
| Winona (0394) | Altaria stays Dragon/Flying: Fairy-weak, and its Dragon Breath misses Fairies. Skarmory resists Fairy |
| Steven (0457) | Skarmory, Aggron and Metagross resist Fairy and hit Fairies x2 (Meteor Mash, Steel Wing); Cradily's Sludge Bomb is x2 too. Gen 6 Steel change: Ghost/Dark moves neutral on his Steels. **Harder for Fairy teams** |
| Aqua (Sapphire) / Magma (Ruby) | Mightyena, Sharpedo and Carvanha are Fairy-weak. Golbat/Crobat (Poison) resist Fairy and hit it x2. Maxie's Camerupt (Fire) resists |
| Sidney (0380) | All Dark, so Fairy is x2 and resists Crunch/Faint Attack |
| Phoebe (0386) | Neutral (Steel change only) |
| Brawly (0390) | Ralts and Marill resist Fighting: easier |
| Wattson (0391) | Magnemite line resists Fairy |
| Wallace (0396) | Luvdisc's Sweet Kiss becomes Fairy (cosmetic) |

- **Balance:** a Fairy is available in the first hour (Ralts, Marill). With section 4's moves, Drake and Sidney get
  much easier and Steven harder. Boss AIs adapt automatically through the chart.

## 7. Recommended design: Birch asks once, in the intro (one ROM per version)
- **Flow:** Birch asks "Fairy type on/off" right after the player's name ("Ah, okay! You're X…", text 0054 line 22).
- **Storage:** the answer goes into the save once and is fixed for the playthrough, so there's no mid-game switching.
- **When off:** the ROM behaves as Gen 5. The Fairy work below is still all built; the switch only adds steps 3-4.

| Step | Where | What | Rating |
|---|---|---|---|
| 1. Question | ov294 intro_script.c `sScriptAskRivalName` (file 0x277c-0x27ac; hoenn_intro.py RIVAL_PICTURE already rewrote it, and 0x2794/0x27ac are spare cmd-0x33 entries). The rival-named scripts after it are dead, because hoenn_intro sends NewGame_Main to END | Insert `TALK 27` (question), `YES_NO {20, 21, 1}` (yes = next entry, no = skip one, as in sScriptGender), then `SET_RESULT 3` (new value) on yes and keep `SET_RESULT 2` on no. Uses the dead entries; no new space | easy-medium |
| 2. Save flag, set once | ov162 NewGame_Main `case NEW_GAME_AFTER_PLAYER_NAMED` (game_start.c:271; 0x021a022a already patched to END) | `if result == 3: wk->newConfig bit 11 = 1; state = END`. NewGame_Exit's `initConfig(wk->newConfig, getTrainerDataBlkAddress(save))` (game_start.c:330) writes it into the save. **Config u16 bits 11-15 are free**: the accessors 0x0200898c-0x02008b0c use bits 0-10, and the init 0x020089c0 zeroes all 4 bytes. The setters mask their own bits, so Options keeps bit 11 (no reader of the raw u16 elsewhere checked). Code room: ov162's dead rival-naming states 7-11 | easy-medium |
| 3. Text | src/text/system/0054_game_start.txt (we already replace it): lines 27-29 are blank; YES/NO = lines 20/21 | One question of at most ~110 characters (slot 5,040 B, about 250 B left) | trivial |
| 4. Hooks reading the flag (ITCM, ~150 B) | Flag read = SaveControl_GetInstance -> getTrainerDataBlkAddress -> `ldrh`, bit 11 | When **off**, map Fairy back at the data chokepoints (rows below) | easy-medium |
| 4a. Species | arm9 PML_PersonalFetchBW2 0x02020234: the only reader of a/0/1/6 records (2 callers) | After ReadRaw: if off and the species is in a 22-entry table, write the old types | |
| 4b. Moves | PML_MoveGetParam 0x02021280: the single GFL_ArcSysRead of a/0/2/1 (has a cache) | If off and type == 17: old type (Charm/Sweet Kiss/Moonlight -> Normal; new moves -> Normal, or a type the user picks) | |
| 4c. Chart | GetTypeEffectiveness / GetTypeWeaknesses | Off: the untouched vanilla table at 0x021d7500 (Gen 5 Steel). On: the new 18x18 | |
| 4d. Arceus | PML_ItemGetArceusPlateType | Pixie Plate -> 0 when off, or don't hand it out | |
| 4e. Not needed | UI, AI, the 17 -> 18 sites | With no type-17 data nothing shows Fairy | |
| Fallback (no intro code) | truck new-game script 30 (src/field_scripts/scenes/truck.inc, already sets new-game flags) | `YesNo` + `FlagSet FLAG_FAIRY_ON` (src/include/hoenn.h); hooks read the EventWork flag the way exp_share does. Pure script, but Birch is not on screen | trivial |

**When it's off:**
- Fairy Gem and Roseli Berry never trigger.
- Traded Pokémon follow the receiving game's setting (types come from ROM data, not the Pokémon).
- Untested risk: link battles or battle videos between an "on" and an "off" save may disagree.

| Option | Extra cost on top of the Fairy work | ROMs / state sets |
|---|---|---|
| Separate builds (5.3) | easy (infrastructure) | 4 / 4 |
| **Intro question (7)** | **easy-medium** (2 intro edits + ~150 B of hooks) | **2 / 2** |
| Options menu entry | medium-hard: ov140 loads exactly 5 values (func_ov140_0219e860: 0x02008a14, a4c, a68, getSoundFlags, ac8); a 6th row means new UI code. JP's CHARACTERS row (text 0032 line 5) isn't loaded in the US build | 2 / 2 |

## 8. Verdict
**Feasible but costly.**
- The type itself is cheap: chart, sentinels, data, icon, names.
- The cost is spread across about 8 overlays of mostly undecompiled code: the ov296 Pokédex, ov255 PC, ov207/ov142
  preloads, Hall of Fame, battle buttons, item handlers, and the new-move animation hook.
- Without new moves the type is cosmetic and defensive, so a worthwhile version needs section 4 too.

| Work package | Content | Size |
|---|---|---|
| F0 Infrastructure | fairy.py skeleton, ITCM allocator after roamers, RESERVE additions, state remake; intro question + hooks (7) | S-M (~1 day) |
| F1 Battle engine | 18x18 chart + 2 readers, 16 + PWT sentinel bytes, Judgment/plate paths, item table relocation + Fairy Gem/Pixie Plate thunks | M-L (asm in ov167/ov169/arm9) |
| F2 Data | 22 species, 3 moves, type name, chart values, Arceus form + palette | S |
| F3 UI | icon/palette (trivial), Dex search (easy), Xtransceiver, then summary, Bag, PC, Pokédex entry, battle buttons, Hall of Fame | L (5 screens with code) |
| F4 New moves | 6 records, text append mode in text.py, animation remap hook, learnsets/TM/tutor typed by hand, Metronome bound | M |
| F5 Items | Pixie Plate + Fairy Gem at free ids; Roseli Berry skipped or replacing a berry | S-M |
| F6 Test + balance | battle matrix (each matchup, Roost, Conversion 2, Struggle, Arceus), every screen with a Fairy, both versions x on/off, optional trainer move tweaks (Wally's Gardevoir) | M |

**Riskiest piece:** the screens that preload 17 icons into fixed work-struct arrays that run straight into other
fields: the ov296 Pokédex entry (icons into its type bytes, plus 12 "17 = none" checks), the ov255 PC box, the ov207
summary and the ov142 Bag. All are undecompiled, so moving those arrays without corrupting a neighbour needs careful
asm work and a full screen-by-screen test.

A close second is the 17 -> 18 sentinel sweep. One missed site gives wrong damage silently, not a crash.
