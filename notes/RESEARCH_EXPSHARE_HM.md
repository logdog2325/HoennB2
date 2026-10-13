# Gen 6 Exp. Share and HM-free field moves (research + prototype, 2026-10-06)

Decisions of 2026-10-06 (DECISIONS.md). Patches: `b2tools/patches/exp_share.py`, `b2tools/patches/hm_free.py`; one id in
`src/include/hoenn.h` (`FLAG_EXP_SHARE_ON 2058`). Tags: **[code]** read in the decomp (source, `dsd dis` output,
symbols, relocs), **[bytes]** read from the user's dump / the decomp's matching build, **[test]** seen in DeSmuME.
Proof images: `screenshots/tests/2026-10-06_exp_share.png`, `screenshots/tests/2026-10-06_hm_free.png`,
`screenshots/tests/2026-10-06_hm_badge_rule.png`.

**Update (same day, after the user's answers):**
- HMs follow Sapphire: the badge is always required, also for a Pokémon that knows the move, including the party
  menu.
- The Exp. Share shows one Gen 6 line for the benched team instead of a line per Pokémon.
- The new text lines live in `src/text`, so the patch order no longer matters.
- TM70/TM94, Flash auto-light and Fly from the Town Map stay as built.

## Short answers

**Exp. Share: works, tested.**
- The Exp. Share (item 216) is now a key item. It sits in Key Items [test], and **Use** in the Bag switches it on and
  off with "The Exp. Share was turned on." / "...off." [test]. The state is `FLAG_EXP_SHARE_ON` (flag 2058) [test].
- In battle, while the flag is on, every live, non-egg party member that did not take part gets `base >> 1` before
  its own level scaling. Participants get exactly Black 2's normal share. This is the rule `notes/LEVEL_SCALING.md`
  fitted its curve to.
- **Messages as in Gen 6** [test]:
  - each participant keeps its own "X gained N Exp. Points!";
  - then one line, "The rest of your team gained Exp. Points thanks to the Exp. Share!";
  - then the benched Pokémon's level-ups ("Mudkip grew to Lv. 2!" with the stat window), with no line per Pokémon.
- Wild Wurmple Lv2, Treecko Lv5 fighting, Torchic Lv5 and Mudkip Lv1 benched:
  - flag on: "Treecko gained 10 Exp. Points!", the team line, "Mudkip grew to Lv. 2!";
  - flag off: only "Treecko gained 10 Exp. Points!".
  - The amounts match the formula: Treecko 10, Torchic 5, Mudkip 9 = exactly Lv2 [test + code].
- The first version (one line per Pokémon) showed the amounts directly: Wurmple Lv3 gave Treecko +18 and
  Torchic +9 [test].
- Mr. Stone's script only needs two lines:
  `ItemAdd ITEM_EXP_SHARE, 1, <var>` and `FlagSet FLAG_EXP_SHARE_ON` (Gen 6 hands it over switched on).

**HMs not required: obstacle scripts, the party menu, Flash, Fly and forgetting work, tested. Surf, Waterfall and Dive
are patched but untested on real water.**
- The rule, as in Sapphire: **the Hoenn badge for the move, always**, and then **a Pokémon that knows the move, or
  the machine in the Bag**.
- Black 2 itself has no badge checks for field moves [code]. The patch adds them:
  - in the talk scripts;
  - in the party menu, which answers with Black 2's own "This can't be used until a new Badge is obtained.".
- Tested for the badge rule:
  - Torchic knows Rock Smash, no badge: "It's a rugged rock, but a Pokémon may be able to smash it." [test];
  - party menu → Treecko → Surf, or Torchic → Flash, no badge: "This can't be used until a new Badge is obtained."
    [test];
  - with the badges: "Torchic used Flash!", the cut-in, and the cave lights up [test].
- Tested in a dark test Littleroot:
  - Cut: without the badge, "This tree looks like it can be cut down!"; with it, prompt, "AAAAAAA used Cut!", and the
    tree is gone [test].
  - Strength: "AAAAAAA used Strength!" and Strength flag 2404 is set [test].
  - Rock Smash (new script 10016, Pokémon path): Torchic's cut-in, and the rock is gone [test].
  - Flash: auto-light with TM70 + Knuckle Badge; it stays dark without the badge [test].
  - Fly: the Town Map key item opens in "Fly to where?" mode with HM02 + Feather Badge and flies [test]. Without the
    badge it is the normal view-only map [test].
  - HM moves can be forgotten: "Treecko forgot how to use Surf." With Black 2's check restored in RAM on the same
    savestate: "HM moves can't be forgotten now." [test].
- **Untested:** Surf, Waterfall (up and down) and Dive. No built map has water yet. Their scripts use the same tested
  helper.
- **Not possible without new map/engine work:**
  - Dive spots: Black 2's Dive exists only at Abyssal Ruins positions, hard-coded [code].
  - Rock Smash rock sprite and rock-smash wild battles.
  - A Hoenn Town Map.

## How to build and test

- **Text is in `src/text`.** These are full copies of the decomp's files with the new lines appended (`overrides.json`
  can only replace lines). The `text` patch installs them.
  - `system/0006_btl_main.txt`: bag lines 161/162.
  - `system/0017.txt`, `system/0019.txt`: the battle std message files. The team line is id 221 in both. 0019 also
    gets 0017's 20 extra lines, so the ids match.
  - `script/0433.txt`: Rock Smash lines 34-36.
  - exp_share/hm_free read the ids from these files. They also pack the same files into the archives themselves, as
    `text` does (byte-identical; checked that every decomp text file round-trips through `text_data.pack_file`
    [test]). So **the patch order no longer matters**.
  - `scripts` must still run before `HOENN_TEST_*` test builds (they replace entry 778).
- Test switches (test builds only):
  - `HOENN_TEST_EXPSHARE=1`: Littleroot's map-load script gives Treecko 5, Torchic 5, Mudkip 1 and the Exp. Share,
    switched on.
  - `HOENN_TEST_HM=1`:
    - Littleroot's NPCs become a boulder at (184,362), a cut tree at (180,365) and a rock
      (entity at (182,369); in the test it blocked (182,368), talked to from (182,367) facing down).
    - Littleroot is dark.
    - The party: Treecko with Pound/Leer/Surf/Absorb, and Torchic with Rock Smash and Flash.
    - Flag 2401 is set: Black 2's "has a Pokémon" flag, which shows POKéMON in the field menu (set after the starter
      in script 0854) [code].
    - Items: HM01, HM02, HM04, TM70 and the Town Map.
    - The town sign gives all 8 badges.
  - Both switches replace a/0/5/6 entry 778, so use one at a time.
- Builds for this work: `HOENN_BUILD_DIR=$PWD/work/rom_expshare`, with `files/` and `code/` deleted after each build.
  - The last one there is the `HOENN_TEST_HM=1 HOENN_TEST_NO_WILD=1` test build of `rebuild_slice.sh`'s patch list,
    SHA1 `ac2f254b…9f0`.
- **Savestates can't test the arm9 parts.** arm9 is loaded once at boot, so a savestate made on another ROM keeps the
  old arm9 in RAM. ov142/ov167 also changed size: FAT entries 142 and 167 differ from `work/rom/base_layout.nds`
  [bytes].
  - So every test here booted fresh through `make_states.py`'s intro inputs (~70 s), then took the test door to
    Littleroot.
  - The resulting savestates are kept in my scratch only; `work/emu` was not touched.

## 1. Exp. Share: evidence

### Where Black 2 computes exp

`AddExpAndEVs` (ov167 `0x021aee0c`, still assembly, read with `dsd dis --overlay 167`) [code]. It is called once per
fainted opponent from `func_ov167_021a8dec` (`src/ov167/btl_server_flow.c:5498-5510`), and
`func_ov167_021a8e68` then shows the messages and adds the exp [code]. In C:

```c
base = CalcBaseExpGain(defeated)          // personal BaseExp * level / 5   (btl_calc.c, 0x021bd6c8)
if (BtlSetup_GetBattleType() == 1) base = base * 15 / 10;           // trainer battle
memset(entries, 0, 6 * 12);                                          // {u32 exp; u8 boosted; u8 evs[6]; ...}
// held Exp. Share (0x021aee70-0x021aeef8): holders = live members holding item 0xd8 (216)
if (holders) { share = (base >> 1) / holders ?: 1; base -= base >> 1; entries[holder].exp = share; }
n = alive opponents-list members of `defeated` (func_ov167_021bc604/0c: list at +0xd0/+0xd1, unique ids)
per = base / n ?: 1;
for each live party member that is in the list: entries[i].exp += per;        // 0x021aef8a-0x021aef90
for each entry with exp: exp = ScaleExpGainedByLevel(...) (x1.5 / x1.7 traded, x1.5 Lucky Egg 0xe7, Pass Power,
                         cap 100000);   then AddEVs for every entry with exp
```

### How Black 2 shows the exp [code]

`func_ov167_021a8e68(flow, party, entries)` loops over the 6 entries (`0x021a8e78-0x021a8f22`). For each entry with
exp and level < 100 it:
1. queues command 0x5a with message 0x2a "{name} gained {n} Exp. Points!" (0x2b "a boosted" when traded or Lucky Egg)
   through `func_ov167_021b15d0(queue, 0x5a, msg, monId, exp, 0xffff0000)` (variadic, ended by 0xffff0000);
2. queues 0x3e (EVs);
3. runs the server-side level-up loop (`func_ov167_021bc1b8`);
4. queues 0x45 (exp gauge, "grew to Lv. N!", move learning);
5. adds a record.

Black 2's held Exp. Share already sent benched Pokémon through this path, so benched level-ups and moves work there.

- 0x5a's messages are the battle's "std" message file: system text **19**, or **17** in one mode (`ov167 0x021d4cb4`,
  table `0x021daa1c` = [19, 18, 16, 20, …]). Both hold "gained … Exp. Points" as line 42 [bytes].
- The entry struct is `{u32 exp; u8 unk4 (boosted); u8 unk5[6] (EVs); u8 unk0B}` (`include/battle/btl_handler.h:80-85`).
  - `unk0B` is never read or written: `AddEVs` writes +5..+10, `func_ov167_021a8e68` reads +0..+10, and
    `AddExpAndEVs` only memsets it.
  - So the patch uses it as the participant mark.

### The patch (ov167, decompressed `arm9_ov167.bin`, base `0x021998c0`)

1. **`0x021aee70-0x021aeef8`** (136 bytes, used exactly): the held-item block.
   - It is dead once the item is a key item: a key item can't be given (+8 bit 5) [code], so no Pokémon can hold one.
   - It now holds the share code and `ExpReport`. r4/r6/r7 are free here: the code at `0x021aeef8` sets them again
     [code].

   ```
   021aee70  bl SaveControl_GetInstance ; bl getConstDataBlock ; ldr r1,=2058 ; bl EventWork_FlagGet
             cmp r0,#0 ; beq done
             ldr r7,[sp,#40] ; lsrs r7,r7,#1                 ; share = base >> 1 (base >= 7: BaseExp >= 36, level >= 1)
             movs r4,#0
   loop:     ldr r0,[sp,#4] ; adds r1,r4,#0 ; bl GetBattleMonFromParty ; bl CanPokemonBattle     ; live, not an egg
             cmp r0,#0 ; beq next ; movs r0,#12 ; muls r0,r4 ; str r7,[r5,r0]                   ; entries[i].exp = share
   next:     adds r4,#1 ; ldr r0,[sp,#36] ; cmp r4,r0 ; blo loop
   done:     b 0x021aeef8
   021aeea8  ExpReport(flow, party, entries):           ; replaces func_ov167_021a8dec's call (0x021a8e58)
             push {r4-r7,lr} ; r4-r6 = args
             movs r3,#0 ; bl func_ov167_021a8e68 ; r7 = result     ; phase 0: participants, own messages
             any entry with unk0B == 0 and exp != 0? (6-entry loop) ; none: return r7
             ldr r0,[r4,#12] ; movs r1,#0x5a ; movs r2,#221 ; ldr r3,=0xffff0000 ; bl func_ov167_021b15d0  ; team line
             r0-r2 = args ; movs r3,#1 ; bl func_ov167_021a8e68 ; orrs r0,r7 ; pop     ; phase 1: benched, no own line
             .word 2058, 0xffff0000
   ```

   - The flag access is the game's own chain [code]:
     - `GameData_Create` stores `getConstDataBlock(save)` at `gameData+0x1ac`.
     - That `+0x1ac` is what `GameData_GetEventWork` returns.
     - `getConstDataBlock` is `SaveControl_GetBlockPtr(save, 0x2d)`.
   - All BL targets are within range; the arm9 ones are always loaded [code].
   - `CanPokemonBattle` = `!IS_EGG && hp != 0` (`btl_pokeparam.c:761-772`) [code].
   - The party count is ≥ 1 in any battle that gives exp.
2. **Participant loop `0x021aef8a-0x021aef91`:**
   - Before: `ldr r1,[r5,r6]; ldr r0,[sp,#32]; adds r0,r1,r0; str r0,[r5,r6]` (`a959 0898 0818 a851`).
   - After: `adds r1,r5,r6; ldr r0,[sp,#32]; strb r7,[r1,#11]; str r0,[r5,r6]` (`a919 0898 cf72 a851`).
   - It stores `per` instead of adding it, so participants get exactly their normal amount.
   - It marks the entry as a participant: `unk0B = r7`, the opponent-list length, ≥ 1.
   - With the flag off, all entries are 0 at that point, so store = add = vanilla [code + test].
3. **`func_ov167_021a8e68` prologue:**
   - `0x021a8e6e` `movs r0,#0` → `str r3,[sp,#28]` (`0020` → `0793`): the phase, in the old message-id slot.
   - `0x021a8e76` `str r0,[sp,#36]` → `str r7,[sp,#36]` (`0990` → `0997`): i = 0 (r7 = 0 there).
4. **`func_ov167_021a8e68` body `0x021a8e88-0x021a8ece`** (70 bytes, rewritten in place; before = the decomp's bytes,
   asserted):

   ```
   ldr r1,[sp,#36] ; ldr r0,[sp,#20] ; bl func_ov167_0219d4e4 ; adds r4,r0,#0   ; mon (2 redundant u8 casts dropped)
   movs r1,#15 ; bl GetBattleMonStat ; cmp r0,#100 ; bge next                  ; Lv100: nothing (as before)
   ldrb r2,[r6,#11] ; ldr r3,[sp,#28] ; cmp r2,#1 ; sbcs r2,r2 ; adds r2,r2,r3 ; bne next
                                       ; participant (mark != 0) only in phase 0, benched only in phase 1
   ldr r7,[r6] ; adds r0,r4,#0 ; bl GetMonID ; str r0,[sp,#32]
   ldr r3,[sp,#28] ; cmp r3,#0 ; bne 0x021a8ece                                  ; phase 1: no own message
   ldrb r2,[r6,#4] ; adds r2,#0x2a ; ldr r0,=0xffff0000 ; str r7,[sp] ; str r0,[sp,#4]
   ldr r0,[r5,#12] ; ldr r3,[sp,#32] ; movs r1,#0x5a ; bl func_ov167_021b15d0 ; nop
   ```

   - The 0x3e / level-up / 0x45 / record code after `0x021a8ece` is untouched, so benched Pokémon still level up and
     learn moves.
5. **`0x021a8e58`** (`func_ov167_021a8dec`): `bl func_ov167_021a8e68` → `bl ExpReport` (`0x021aeea8`). It is the only
   call [code: `relocs.txt`].

Result per KO, with the flag on:

| Party member | Exp before level scaling | Message |
|---|---|---|
| Participant | `base / n` | own "gained N" line, first |
| Live non-participant | `base >> 1` | the one team line, then its level-ups |
| Fainted or egg | nothing | none |

- Everything with exp also gets EVs. The "boosted" text for traded mons and the Lucky Egg still applies to
  participants.

### The key item, and Use from the Bag

- **Save pocket** = `ITEM_CATEGORIES[item]` (arm9 `0x0208f4d0`, one byte per item; `PML_ItemGetType`), not the item
  data [code].
  - Values [bytes]:

    | Value | Pocket | Examples |
    |---|---|---|
    | 0 | Items | Master Ball, Exp. Share, Lucky Egg |
    | 1 | Medicine | Potion |
    | 2 | TMs & HMs | TM01, HM01 |
    | 3 | Berries | Oran Berry |
    | 4 | Key Items | Bicycle, Dowsing MCHN |

  - Patch: `[216]` `00` → `04`.
- **Item data** (a/0/2/4, 639 × 36 bytes). Fields from `PML_ItemGetParam`'s jump table (arm9 `0x02026820`)
  [code + bytes]:
  - +0 price/10;
  - +8 u16 bits: 0-4 Natural Gift type, 5 = param 3, 6 = param 4 "registrable", 7-10 = param 5 field pocket,
    11-15 battle pocket;
  - +0xA = param 6, field use;
  - +0xD/+0xF = params 15/17, the bag's sort key (`ov142 0x0219b7f2`).
  - In the bag's item menu (`func_ov142_0219bf04` / `0219bf58`) [code]:
    - param 6 ≠ 0 adds **Use**;
    - param 3 = 0 adds Give / Toss;
    - param 4 adds Register.
  - Exp. Share `2c01 3300 0000 1e00 1f00 0000 0001 0027` → price 0, `+8 = 0x023f` (bit 5, pocket 4), `+0xA = 25`
    [bytes]. Bicycle has `+8 = 0x027f`, `+0xA = 4` [bytes].
  - Only that menu builder reads param 6 with a constant argument (searched every module's disassembly) [code].
- **Use dispatch** (`func_ov142_0219a4d0`) [code]:
  - Key items go through `data_ov142_021a0980`: 11 × `{u16 first item, u16 count, handler}`, searched by
    `func_ov142_0219a4a0` (first ≤ item < first + count).
  - Its entries [bytes]: Bicycle 450, Town Map 442, Pal Pad 437, Honey 94, Super Rod 447, Vs. Recorder 465,
    Dowsing 471, Escape Rope 78, Xtransceiver 621, Xtransceiver 626 (same handler `0x0219a481`), Medal Box 627.
  - Patch [bytes before/after]:
    - entry 8 `{621,1}` → `{621,6}` (622-625 are "???"/Grams with no Use);
    - entry 9 `{626,1,0x0219a481}` → `{216,1,0x02005051}`.
- **Handler `ExpShareToggle`** (arm9 `0x02005050-0x0200507f`, 48 bytes):
  - It gets `EventWork_GetFlagBytePtr(EventWork, 2058)` and XORs the flag's bit (`1 << (2058 & 7)`).
  - Then it calls `func_ov142_0219a2c4(work, on ? 161 : 162)`, the bag's own "message about the selected item" routine
    (word 0 = player name, word 1 = item name; used for "There's a time and place…"). It returns to the item list
    [code + test].
- **Free space** [code + bytes]:
  - `0x02005050-0x02005123` holds Nitro SDK middleware version strings (`[SDK+NINTENDO:DWC5.3…]`,
    `[SDK+NINTENDO:BACKUP]`, `[SDK+UBIQUITOUS:CPS]`, `[SDK+NINTENDO:WiFi…]`, `[SDK+UBIQUITOUS:SSL]`,
    `[SDK+Nintendo:libVCT 1.4.1]`). `0x02005030-0x0200503f` are 16 zero bytes before them.
  - No relocation in any module's `relocs.txt` points into `0x02005000-0x02005123`. The only nearby one is the
    reference to `main` at `0x02005125`.
  - Allocation:

    | Range | Used by |
    |---|---|
    | `0x02005050-0x0200507f` | exp_share |
    | `0x02005080-0x02005123` | hm_free, 164/164 bytes |
    | `0x02005030-0x0200503a` | hm_free's badge table |

  - This is inside the arm9 secure area. DeSmuME boots it [test]; melonDS, DSi mode and hardware are untested.
  - No other free code turned up:
    - unreferenced functions: none in arm9, ov012, ov142 or ov167;
    - ov165's are the anti-piracy blocks (`mov r10, pc` / `+0x2200` obfuscation), which must not be touched.
  - The battle part fits into the freed held-item block exactly (136 bytes).
- **Messages** [code]:
  - Bag message file = system text 6 (`GFL_MsgSysLoadData(0, 2, 6, …)` at `0x0219c55e`), lines 161/162.
  - Battle team line = id 221 in system texts 17 and 19.
  - All of them are in `src/text` (see "How to build").

### Tests [test]

1. Build: `HOENN_TEST_EXPSHARE=1 HOENN_BUILD_DIR=$PWD/work/rom_expshare build_rom.py --clean` with
   `rebuild_slice.sh`'s patch list (`… text scripts … sprites exp_share hm_free`). Then a fresh boot to Littleroot.
2. **Bag:** Key Items shows Xtransceiver, Pal Pad, Exp. Share. Item menu: USE / TO FREE SPACE / CANCEL, with no Give.
   - Three uses gave "turned off", "turned on", "turned off".
   - The flag was read through the game's pointer chain (`*0x02140f60` → `+0x10` → `+0x34` + block 0x2d offset =
     EventWork `0x022254e4`; flag byte `0x02225943`): it went 1→0→1→0. Tested with both handler versions.
3. **Battle (team message):** Treecko Lv5 leads; Torchic Lv5 and Mudkip Lv1 are benched; wild Wurmple Lv2. The same
   savestate was run with the flag left on and cleared in RAM. The clear changes no RNG, so the encounter and every
   roll were identical.
   - On: "Treecko gained 10 Exp. Points!" → "The rest of your team gained Exp. Points thanks to the Exp. Share!" →
     "Mudkip grew to Lv. 2!" plus the stat window. No line for Torchic or Mudkip.
   - Off: only "Treecko gained 10 Exp. Points!", then the battle ends.
   - The model [code]: Wurmple `BaseExp 39` (`data/personal/0265_wurmple.s:19`), so `base = 39·2/5 = 15`.
     - Scale = `14^2.5 / (17^2.5 | 13^2.5)` = `733 / (1191 | 609)`.
     - Treecko `15·733/1191 + 1 = 10`.
     - Torchic `(15>>1 = 7)·733/1191 + 1 = 5`.
     - Mudkip (Lv1) `7·733/609 + 1 = 9`, which is exactly Lv2 (Medium Slow) → the level-up.
4. **Earlier, per-line version:** Wurmple Lv3 gave "Treecko gained 18" and "Torchic gained 9". This matches the same
   model with base 23.

## 2. HMs not required: evidence

### How Black 2 gates field moves [code]

- **No badges anywhere.**
  - `CalcPlayerActionPossibilities` (`src/ov012/field_encount_st.c:112-194`) sets one bit per hidden-move kind from
    terrain only: cut tree in front = object 0x6c, water, waterfall, boulder (`IsNPCStrengthRock`: 0x6d,
    0x2003-0x2005), fly-zone flag, flash zone, Abyssal Ruins dive spot.
  - The scripts never call `TrainerCardHasBadge`.
- **Talk scripts** live in global script file **1243** = ids 10000-10089 (GLOBAL_SCRIPT_TABLE entry 45 at ov012
  `0x0216af98`: `{10000, 10089, file 1243, msg arc 3, file 433}`) [bytes]:

  | Id | Script | Kind | Party check | Notes |
  |---|---|---|---|---|
  | 10000 | Script_1 | boulder | `PokePartyHasMoveAny 70` | Strength flag 2404 |
  | 10002 | Script_3 | water | `PokePartyHasMoveAny 57` | |
  | 10004 | Script_5 | cut tree | `PokePartyHasMoveAny 15` | |
  | 10006 | Script_7 | waterfall | `PokePartyHasMoveAny 127` | |
  | 10011 | Script_12 | dive | `PokePartyHasMoveAny 291` | |
  | 10001/3/5/7/8/9/10/12 | | party-menu versions | | the Pokémon is in 0x8000 |
  | 10015 | Script_16 | going down a waterfall | | |

  - `PokePartyHasMoveAny` returns the first slot with the move, or 6 (`scrcmd_pokemon.c:403-419`).
  - `VMJumpIf CMP_STACK` jumps when the popped value ≠ 1 (`scrcmd_vm.c:284-297`).
  - In Black 2's own entities, every cut tree is object 0x6c with script 10004 (19), and every boulder is 0x2003/0x2005
    with script 10000 (65) [bytes, a/1/2/6].
  - Assembling the decomp's `1243.s` with the project's clang command gives entry 1243 byte for byte [test].
- **C-side checks:**
  - **Surf prompt** (ov036 `CheckFieldEnvInteraction` `0x02182e54`): returns script 0x2712 only if
    `GameData_FindPartyPkmByMove(Surf) != 6`.
  - **Surfing down a waterfall** (`CheckAutoTileEvents` `0x02182890`): runs 0x271f only if a Pokémon knows Waterfall.
  - **Waterfall up** (0x2716) has no C party check.
  - **Dive:** only where `DecideAbyssalRuinsDiveZoneByUndellaBayPos` (Undella Bay positions) says so.
- **Forgetting:** `PML_MoveIsHM` (arm9 `0x02026b18`) compares against `TM_MOVE_LIST[92..97]`, the HM01-06 moves
  (`0x02090c84` + 0xb8) [code + bytes]. Callers:
  - `isPkmMoveHmMove` (the move-forget screens: ov207 ×2, ov287 ×1);
  - `doesPkmHaveTmMove` (ov194 Pokémon trade).
- **Party menu field moves** (ov165): table `data_ov165_021a4a1a` [15, 57, 127, 70, 19, 148, 100, 91, 230, 448, 291,
  208, 135] and `func_ov165_0219d9b8` map a known move to a menu option (11 + hidden-move kind).
  - Choosing one calls `CheckAllowHidenEvent(kind, ctx)` at ov165 `0x0219d654`. This is the function's only caller
    (`relocs.txt`).
  - The result goes through a switch (`0x0219d668`):

    | Result | Party menu |
    |---|---|
    | 0 | use |
    | 1 | message 0x51 "You can't use that here." |
    | 2 | message 0x39 "This can't be used until a new Badge is obtained." |
    | 3 | message 0xab, the "someone with you" one |
    | 4 | message 0x50 "You're already surfing." |

  - The messages are system text 178 [code + bytes].
  - So Black 2 already has the badge answer; nothing in Black 2 returns 2.
- **Flash:** dark zones are `{u16 zone, u16 flags}` in a/1/4/9 entry 0. Black 2 has 10, flags 1 = dark [bytes].
  `GameData_UpdateFlashStatus` (ov035 `0x0217e754`, `event_mapchange.c:1504-1513`) lights a dark zone on map change
  when `FieldStatus_CheckFlashUsed` [code].
- **Fly:**
  - The Town Map app (FIELD_APP 8, ov144) opens in fly mode only when the flow started in the party menu
    (`appId == 0`).
  - Only then does result 2 become `eventId 4` (Fly) with the chosen zone (`event_field_proclink.c:758-818`).
  - `EventFly_Create` needs only the zone, not a Pokémon (`src/ov033/event_fly.c:29-46`).
- **Rock Smash:** Black 2 has no field Rock Smash: none of the 11 hidden-move kinds (`hiden_event.c:20-33`) and no
  rock object. Rock Smash is TM94 and Flash is TM70 in Black 2 [bytes, TM_MOVE_LIST]. Items 426/427 are unused "???"
  [bytes].
- **Sapphire** [code, pokeruby]:
  - Field move i (Cut, Flash, Rock Smash, Strength, Surf, Fly, Dive, Waterfall) needs `FLAG_BADGE01_GET + i`
    (`src/pokemon_menu.c:154-159, 728`).
  - The tree, rock and boulder scripts check the badge first (`data/field_move_scripts.inc`).
  - Surfing down a waterfall is a forced current, with no move or badge (`src/field_player_avatar.c:137-157`).

### The patches (`hm_free.py`)

**Machines and badges.** Badge index = Hoenn gym − 1, so gym scripts must use `TrainerCardAddBadge (gym-1)`. The
machines are Black 2's own items for each move:

| Move | Machine | Badge |
|---|---|---|
| Cut | HM01 420 | 0 Stone |
| Flash | TM70 397 | 1 Knuckle |
| Rock Smash | TM94 619 | 2 Dynamo |
| Strength | HM04 423 | 3 Heat |
| Surf | HM03 422 | 4 Balance |
| Fly | HM02 421 | 5 Feather |
| Dive | HM06 425 | 6 Mind |
| Waterfall | HM05 424 | 7 Rain |

**Data**
- **a/0/5/6 entry 1243** is rebuilt from the decomp's `1243.s` (1628 → 2024 bytes; the archive is padded).
  - New helper `L_HMAccess` checks `TrainerCardHasBadge` first. It returns 0x8010 = 7 without the badge. With the
    badge it returns the slot of a Pokémon that knows the move, else 6 if the machine is in the Bag, else 7.
  - Talk scripts 10000/10002/10004/10006/10011 use it.
  - On the item path, word 0 is the player's name ("AAAAAAA used Cut!") and there is no cut-in.
  - Water does nothing when you can't surf, as in Sapphire.
  - New **10016** = breakable rock, with Sapphire's three texts as lines 34-36 of `src/text/script/0433.txt`. It is
    the same flow, and the rock is deleted with a sound.
  - Temporaries 0x8030-0x8034. 0x8011 is the talked-to actor (`ScriptWork_SetParentActor`) and is not touched.
  - Party-menu scripts are unchanged: the party menu is gated in code (below).

**Code** [bytes before → after]

| Site | Before | After | Effect |
|---|---|---|---|
| ov165 `0x0219d654` (party menu) | `bl CheckAllowHidenEvent` | `bl 0x020050f0` HoennCheckHiden | without the badge: Cut, Surf, Waterfall, Strength, Fly, Flash, Dive return 2 (the badge message); the others and badge holders go to Black 2's check |
| arm9 `0x02026b18` `PML_MoveIsHM` | `08 4a 00 23` (`ldr r2,=TM_MOVE_LIST; movs r3,#0`) | `00 20 70 47` (`movs r0,#0; bx lr`) | HM moves forgettable everywhere |
| ov036 `0x02182ede` (after `FindPartyPkmByMove(57)`; `cmp r0,#6`) | `02 d0` beq | `c0 46` nop | facing surfable water always runs 10002 |
| ov036 `0x02182902` (after `FindPartyPkmByMove(127)`) | `29 d0` beq | `c0 46` nop | surfing down waterfalls needs no move |
| ov035 `0x0217e76e` | `bl FieldStatus_CheckFlashUsed` | `bl 0x020050b0` HoennFlashUsed | dark zone lit on entry if Flash used **or** TM70 + badge 1 |
| ov012 `0x0215bfdc` (town map createParam) | `00 69 00 28` (`ldr r0,[r0,#16]; cmp r0,#0`) | `bl 0x020050c4` HoennTownMapMode | fly mode for the party menu, or the Bag's Town Map + HM02 + badge 5 + fly-allowed zone |
| ov012 `0x0215c01e-29` (town map result, bag branch) | `ldr r1,[r1,#4]; cmp r1,#0; beq; cmp r1,#1; beq; b +10` | `ldr r2,[r1,#4]; cmp r2,#0; beq; cmp r2,#1; beq; b 0x0215c048` | result 2 goes to the party branch's Fly code (param kept in r1) |

**arm9 helpers** at `0x02005080-0x02005123` (164 bytes, listing in the patch's `helpers()`):
- `HoennHasItemAndBadge(item, badge)` = `isBadgeObtained(getTrainerGameInfoAddress(sc), badge)` && (`item == 0` ||
  `BagSave_CheckAmount(SaveControl_GetBlockPtr(sc, 0x19), item, 1)`).
  - These are the same blocks `getTrainerCardDataBlkAddress` and `GameData_GetBag` return (`GameData_Create`)
    [code].
  - The 4th argument of `BagSave_CheckAmount` is unused (`BagSave_GetItemHandleIfAmount`) [code].
- `HoennFlashUsed(status)`.
- `HoennTownMapMode(input)`: reads `param->zoneId` from the caller's r4 and returns with `cmp r0,#0` flags.
- `HoennCheckHiden(kind, ctx)`: the badge from the table at `0x02005030` (kind → badge: `00 04 07 03 05 01 ff ff ff ff
  06`, ff = none for Teleport, Dig, Sweet Scent, Chatter). Missing badge → 2; else `CheckAllowHidenEvent(kind, ctx)`.

### Tests [test]

Setup:
- Build: `HOENN_TEST_HM=1 HOENN_TEST_NO_WILD=1 … text scripts encounters encounter_rules exp_share hm_free`, then a
  fresh boot.
- Littleroot is dark on arrival.
- The player has HM01/HM02/HM04/TM70/Town Map and no badges.
- The badge-rule tests are from the updated patch; the rest were run on both versions.

| Test | Result |
|---|---|
| Cut tree, no badge | "This tree looks like it can be cut down!", tree stays (walking up is blocked) |
| Read sign (8 badges), cut tree | YES/NO → "AAAAAAA used Cut!" → walking up passes the tree's tile |
| Boulder | "…Would you like to use Strength?" → "AAAAAAA used Strength!" → "Strength made it possible…"; flag 2404 = 1 |
| Rock, Torchic knows Rock Smash, **no badge** | "It's a rugged rock, but a Pokémon may be able to smash it." (no prompt) |
| Rock, Torchic knows Rock Smash, badges | new prompt → "Torchic used Rock Smash!" with Torchic's cut-in → rock tile walkable |
| Party menu → Treecko → Surf, **no badge** | "This can't be used until a new Badge is obtained." |
| Party menu → Torchic → Flash, **no badge** | "This can't be used until a new Badge is obtained." |
| Party menu → Torchic → Flash, badges | "Torchic used Flash!", cut-in, Littleroot lit |
| Re-enter Littleroot through a door with badges | lit (large Flash radius); same route without badges: still dark |
| Bag → Key Items → Town Map → Use, badges | "Fly to where?" map; A on Littleroot → Fly animation → lands, banner shown |
| Same without badges | view-only map, A does nothing |
| HM01 on Treecko (Pound, Leer, Surf, Absorb), forget Surf | "Treecko forgot how to use Surf." / "Treecko learned Cut!" |
| Same savestate, `PML_MoveIsHM` bytes restored in RAM | "HM moves can't be forgotten now." |

- Strength: the boulder did not move when pushed on this test map.
  - Pushing is Black 2's own code (`FieldPlayerGrid_CheckStrengthRockPushEvent` → `StrengthRockSpaceCheck`,
    `ActorRouteCollCheckOneTileInDir`, ov036 `0x021ba954`), which only needs flag 2404 (set).
  - It depends on the destination's collision in our converted map: **untested on a real Strength map**.

## Untested / known gaps

- **Surf (10002 + the ov036 nop), Waterfall up (10006) and down (ov036 nop + 10015), Dive (10011): not run.** No built
  map has water.
- **Hoenn Dive spots** need new code or data. Black 2 only dives at Undella Bay positions (`GetAbyssalRuinsDiveZoneID`,
  ov036 `0x021c3d50`) [code].
- **Rock Smash:**
  - needs an overworld rock object (the test used boulder 0x2003);
  - has no break animation;
  - has no rock-smash wild battles (Sapphire `ScrSpecial_RockSmashWildEncounter`).
- **Fly via the Y button:** a Town Map registered to Y opens from another app id and stays view-only. Fly also shows
  Black 2's Unova map until a Hoenn town map exists.
- **Exp. Share, not tested:**
  - Order with a benched Pokémon *before* a participant in the party (the two passes put participants first [code]).
  - A benched Pokémon learning a move (same 0x45 path as level-ups and Black 2's held Exp. Share [code]).
  - The team line also shows when every benched Pokémon is Lv100 and only gets EVs.
- **Exp. Share UX:**
  - the Bag description is still "An item to be held by a Pokémon…";
  - there is no Y registration.
- **Party menu with Flash already active:** Black 2's own checks still answer after the badge check (e.g. "You can't
  use that here.").
- **Other targets:** melonDS, DSi mode and real hardware are untested. Both patches write into the arm9 secure area,
  and dsd recompresses/re-signs as before.
- **Edge cases, by reading only:** fainted/egg non-participants, two participants (switching), trainer battles ×1.5,
  Lv100 members.

## Open questions for the user

1. **Non-participant share** (not answered yet). Implemented: `base >> 1`, independent of how many fought (Gen 6's
   value, and the rule LEVEL_SCALING.md assumed). The alternative "half of what each participant got" (`(base/n) >> 1`)
   needs a different hook, after the participant count.
2. **Team line when all benched Pokémon are Lv100:** keep it, or check levels too? That needs about 12 more bytes, which
   the block doesn't have.
3. **Exp. Share Bag description:** replace Black 2's held-item text (system text 63, line 216) with a key-item one?

Answered 2026-10-06:
- the badge is always required;
- keep TM70/TM94;
- Flash auto-light and Fly from the Town Map are OK;
- text in src/text;
- one team line.
