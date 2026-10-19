# Emerald saves and PKHeX (RESUME #4; save_compat, 2026-10-18)

Status: **built behind a switch that is OFF by default** (`HOENN_SAVE_COMPAT=1`). Without the switch every build is
byte-identical to before. It changes how Emerald saves are stored, so it ships only after the user's OK and a save test.

## 1. Cause (confirmed on copies of real saves)

Black 2's main save (backup_system.c / savedata.c in external/pokebw2) is two copies, main at card 0x0 and backup at
0x26000, each 0x25FA4 bytes:

| part | where | what |
|---|---|---|
| block i (73 of them) | 0x100-aligned (SaveData_BuildTable) | `size` bytes, then BlockFooter {u16 count; u16 crc}, then padding up to the next 0x100 |
| CRC table | 0x25F00, 0x94 B | crc of every block (73 x u16 + 2 padding) |
| SaveFooter | 0x25F94, 0x10 B | u32 count, u32 size (0x25FA4), u32 magic (0x31053527), u16, u16 crc of the CRC table |

All CRCs are CRC-16/CCITT (poly 0x1021, init 0xFFFF): NitroSDK MATH_CalcCRC16CCITT, PKHeX's `Checksums.CRC16_CCITT`.
A block's crc covers exactly its `size` bytes.

PKHeX (SAV5B2W2): the file must be 0x80000 bytes and the CRC of 0x25F00..+0x94 must equal the u16 at 0x25FA2 (that is
how it recognises a B2W2 save); then each block of its fixed list is checked: CRC-16 of (Offset, Length) against the
u16 at Offset + Length + 2 and against the table entry 0x25F00 + 2i. Block 56 (0x38) is (0x21A00, 0x3C), block 62
(0x3e) is (0x23600, 0x10).

The Emerald builds enlarge two blocks: 0x38 (Black 2's Battle Subway play data) 60 -> 252 bytes for the Frontier's
records (frontier_core.py point 3), 0x3e (Unity Tower) 16 -> 112 for the Pyramid's PySave (frontier_pyramid.py
point 7). The slot is 256 bytes either way, so nothing moves, but the game's CRC now covers 252 / 112 bytes.

Measured (work/agents/save_compat/savemodel.py on copies of ~/Desktop/Emerald_JUAN_TEST.sav,
Emerald_v1.0.4_WATTSON_TEST.sav, Emerald_v1.0.4_WATTSON_TEST2.sav, with Sapphire_WALLY_TEST.sav and Ruby_TM_TEST.sav
as references):
- every save: 0x80000 bytes, PKHeX's B2W2 recognition check passes, footer/magic/size as Black 2's;
- Sapphire and Ruby: all 73 blocks pass PKHeX's checks;
- Emerald: exactly blocks 56 and 62 fail; scanning for the length whose CRC matches the stored one gives 252 and 112.
  Nothing else in an Emerald save differs in structure from a Sapphire/Ruby save. **The cause is confirmed.** (What
  PKHeX shows for two bad block checksums, a refusal or a warning, depends on its version; either way these two checks
  are the only difference.)

## 2. The bytes after a block's footer: what Black 2 and PKHeX do with them

- **Loaded**: a load reads each whole copy (0x25FA4 bytes) into RAM, padding included.
- **Not checked**: nothing covers them: a block's CRC covers `size` bytes, the table's CRC covers only the table, the
  footer has no whole-save CRC. PKHeX checks the same ranges, so it ignores them too.
- **Never written**: a save first compares each block with the card over `size` bytes (func_0203b81c) and writes a
  changed block as `size + 4` bytes (func_0203b92c). A change after the footer is neither noticed nor written: it is
  lost at the next boot. (The card keeps 0xFF there: the real saves show `ff` after the 0x3e footer.)
- **Recovery**: when one copy's block is bad, the loader copies `size + 4` bytes from the other copy; the padding stays.
- **New game**: runSaveBlkInitializers clears the whole save area in RAM, padding included.
- **PKHeX** writes the file back with the padding untouched (it recomputes only the main copy's CRCs).

So the padding can hold data only if the game is taught to write it, to notice changes in it and to check it.

## 3. Design

### Layout (each 256-byte slot; card offsets of the main copy, + 0x26000 for the backup)

| slot | today's Emerald builds | HOENN_SAVE_COMPAT=1 |
|---|---|---|
| 0x38 @ 0x21A00 | [Black 2's 60][records: keys 0-95, 192][footer 4] | [Black 2's 60][footer 4][records: keys 0-94, 190][ext CRC 2] |
| 0x3e @ 0x23600 | [Black 2's 16][PySave 96][footer 4][unused 140] | [Black 2's 16][footer 4][PySave 96][ext CRC 2][unused 138] |

The blocks keep Black 2's sizes (60, 16), so the game's own CRCs, the CRC table and PKHeX's checks cover exactly
Black 2's bytes. The extension ("ext") has its own CRC-16 (same algorithm) over the records / the PySave. Key 95 was
never claimed (notes/FRONTIER.md 6: claims stop at 94), so its place holds the CRC: under the switch `FrGet`/`FrOp`
take keys 0-94 (FR_N_KEYS).

### Code (all behind the switch)

- `b2tools/patches/save_compat.py` + `.c` (new): the code goes into the Frontier code area (frontier_area.py; main RAM,
  loaded by FRAM_Boot before GameInit, so before SaveControl_Create's load). Four `bl` sites in arm9:
  - 0x0203b95e in func_0203b92c (the block write, its `getSizeOfSaveBlockData` = write length - 4) -> **SC_WriteLen**:
    for the main save's blocks 0x38 / 0x3e, seal the ext (its CRC) and return the slot's used length - 4 (writes 256 /
    118 bytes: one card page from the slot start, never past the slot);
  - 0x0203b854 in func_0203b81c (the compare with the card before a save) -> **SC_CmpLen**: the same, used length
    (256 / 118) so a change in the ext alone makes the block dirty;
  - 0x0200713a (SaveControl_Create) and 0x0200732c (func_02007324), the main save's two calls of func_0203ae4c (load)
    -> **SC_Load** (section 4).
  "Main save" = the SaveDataTable of g_SaveControlWork's SaveData; other SaveData (extra saves) are untouched.
- `frontier_core.py` / `frontier_pyramid.py`: with the switch they leave the size functions at 60 / 16.
- `frontier_core.c`, `_pike.c`, `_factory_dome.c`, `_palace_arena.c`, `_pyramid.c`: the records' offset (`FR_REC_OFF`,
  60 -> 64), the key count (`FR_N_KEYS`, 96 -> 95), the PySave offset (`PY_SAVE_OFF`, 16 -> 20) are macros whose
  defaults are today's values; their .py files pass `save_compat.cflags()` (empty without the switch).
  FR_PlayInit (block 0x38's new-game initializer) clears the whole slot under the switch.
- `b2tools/build_rom.py`: `HOENN_SAVE_COMPAT=1` appends `save_compat` to the patch list (as HOENN_MUSIC does
  hoenn_music), so the switch alone gives a consistent ROM.

## 4. Load and the one-time migration (SC_Load)

1. Black 2's load with the sizes 60 / 16. A new-form save: OK.
2. If it says **broken**: Black 2's load again with the old sizes (0x38 252 and 0x3e 112; then 252/16 and 60/112 for
   saves of builds that had only one of the two), sizes restored right after. The first that loads OK is the save's
   form. Black 2's own two-copy logic decides everything (which copy, which block from where), so a save that only
   loaded with the old ROM because of its backup copy still loads.
3. Migration of each block found in the old form (RAM only): the ext moves 4 bytes up into its new place (records keys
   0-94; key 95 dropped: never used), the footer's place gets the old footer's count, the ext CRC is computed, the
   block is marked "write to both copies" (blockStatus = WRITE_MAIN). The card is not touched: the **first in-game save**
   writes both blocks (new form), the CRC table and the footer to both copies.
4. Then every load checks each ext CRC. A bad one (garbage padding of a save made before the Frontier existed, a torn
   card page, a block Black 2 restored from the backup) is read from the main and then the backup copy in the card
   (func_0203bf48 into SaveData's compareBuffer) and the first good one is taken; if neither is good the ext is cleared.
   Either way the block is marked to be written.

If the old sizes do not load either, the result is Black 2's broken result, as without the patch.
Until the player saves, the card keeps the old form: going back to the old ROM still works; a later boot of the new
ROM migrates again (idempotent). After the first save the save is new-form for good: **the old ROMs (Emerald up to
v1.0.4) cannot read it** (their load says broken). Keep a copy of the .sav before the first save on the new ROM.

## 5. Failure modes

| case | what happens |
|---|---|
| old-form save, normal boot + save | migrated; PKHeX-valid after the save; records and PySave kept (keys 0-94) |
| power loss during the migration's save (after any of its 10 card writes) | next boot: Black 2's loader picks the copy that is whole (new or old form), SC_Load migrates again if needed; data kept (tested: every cut point) |
| main copy's ext corrupt | taken from the backup copy (tested) |
| both exts corrupt | ext cleared (Frontier records / Pyramid state lost, everything else kept) (tested) |
| save from an Emerald build before frontier_core (Black 2 sizes, padding 0xFF) | loads as new form, ext CRC bad -> cleared: such saves load again (today they are "broken") |
| Sapphire/Ruby save in the Emerald ROM | as above (not a supported case) |
| a script writes key 95 | impossible: FrGet/FrOp take keys < 95 under the switch |
| PKHeX edits a migrated save | it rewrites Black 2's CRCs only; the ext and its CRC are untouched |
| the new save on an old ROM | broken (one-way migration) |
| false detection | an old-form block passing the new-size check needs two 16-bit CRCs to match by chance (~2^-32 per copy) |

Cost: an old-form save loads up to 4 times at its first boot (each load reads 2 x 0x25FA4 bytes); normal boots load once.

## 6. How it was checked (no ROM built: the disk is nearly full and ROM builds are on hold)

- `work/agents/save_compat/test_save_compat.py`: a Python model of Black 2's loader (func_0203b170) and saver
  (func_0203b9bc: compare, footer counts, blocks, CRC table, footer, both passes) with SC_CmpLen / SC_WriteLen /
  SC_Load as in save_compat.c, and PKHeX's checks. On copies of the three Emerald saves, as they are and refilled with
  random records + PySave by the old layout: Black 2 sizes alone -> broken; SC_Load -> migrated (both blocks); records
  0-94 and PySave kept; the first save completes; **PKHeX model: all 73 blocks valid**; every other block unchanged;
  unhooked Black 2 loads the result; both copies' ext CRCs good; a reload needs no migration; an unchanged ext is not
  rewritten; an ext-only change is written to both copies; power loss after each of the 9 intermediate writes of the
  migration save recovers; ext repair from the backup; ext cleared when both are bad; one-block-enlarged saves (mask 1
  / 2); Sapphire/Ruby saves load and stay PKHeX-valid. Result: ALL PASS.
- `save_compat.c` compiles with the Frontier code area's clang flags and links (frontier_area.link): 863 bytes.
- `work/agents/save_compat/identity_check.py`: each edited Frontier C file preprocesses (clang -E -P, the patches'
  flags) to the same token stream as git HEAD with the switch off -> the same object code; with the switch on only the
  offsets / key bound / FR_PlayInit differ. The .py edits only add `save_compat.cflags()` (empty) and skip the size
  writes under `enabled()`.
- All five Frontier modules compile with the switch on and off (their `__main__` builds).
- The whole Emerald patch chain (story_build.sh's 57 patches + save_compat) up to the code stage, with the switch on
  and no .nds (`work/agents/save_compat/patch_stage.py`, log `patch_stage.log`, 3.5 min, 316 MB moved to the Trash
  after): every patch's asserts pass; arm9 size functions at 60 / 16; the four hooks point at save_compat's code
  (Frontier code area 0x23d3d00, 863 B); ITCM 6656 B left (frontier_core +8 B and the Pike's ITCM part +4 B with the
  switch: the records' offset 64 no longer folds into `ldrh` immediates).

Not tested: the game itself (no ROM built), real hardware, DSi mode (the Frontier code area is DS-mode only, as for
every Frontier patch), PKHeX itself (its checks are modelled from its known B2W2 layout, matched against the game's
own table here).

## 7. User test (melonDS, with a COPY of a real Emerald save)

1. Build: `zsh work/agents/save_compat/build_test_rom.sh` (needs 1.5 GB free) -> ~/Desktop/Emerald_SAVE_COMPAT_TEST.nds.
2. Copy an Emerald save next to it under the ROM's name, e.g.
   `cp ~/Desktop/Emerald_JUAN_TEST.sav ~/Desktop/Emerald_SAVE_COMPAT_TEST.sav` (copy, never move: keep the original),
   ideally one with Frontier progress (BP, a streak, a symbol) and/or a Pyramid challenge in progress.
3. Optional: open the copy in PKHeX first: it should complain (blocks 56/62).
4. melonDS (sound muted), open the ROM, Continue: the save loads (no "corrupted" message), same place, party, BP.
5. Save in game (Start menu -> Save). Quit melonDS.
6. Open ~/Desktop/Emerald_SAVE_COMPAT_TEST.sav in PKHeX: it opens with no checksum complaint.
7. Back in melonDS: Continue again; check the Frontier: a facility lobby's streak/record talk, the symbols on the
   Frontier pass / trainer card, BP; in the Pyramid, a saved challenge resumes on its floor with its bag.
8. Save once more in the Frontier after a change (e.g. win a battle, buy with BP), reload: the change is there.
9. Optional: open the saved file in PKHeX, change something harmless (a box Pokémon's nickname), save it, load it in the
   game: it loads.

## 8. Turning it on (after the user's OK)

Make the switch the default (or drop it), build, test step 7 with a fresh copy, publish with a release note: "the first
save converts an Emerald save for PKHeX; older Emerald ROMs cannot read it afterwards".
