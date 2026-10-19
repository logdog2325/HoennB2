# Upgrading external/pokebw2 to the latest decomp (RESUME item 17, 2026-10-18)

The newest fuddlesworth/pokebw2 (b1bcf254a, 87.18% decompiled) is at `external/pokebw2_new`; the old copy is still at
`external/pokebw2` and nothing has been switched over yet. The old copy was only read. Its `build/`, `extract/` and
`orig/` were not touched.

**Result.** The new copy can replace the old one. Every field script, encounter table and trainer still assembles to
the same bytes. The new decomp did more than add generated headers, though: it moved all its game data from
`data/*.s` and numbered text files to `res/**/*.json` and named text banks, and it reorganized `tools/scripts/` into
`tools/{data,text,script,build,decomp}/`. Many HoennB2 readers (both build-time and converter-time) still use the old
layout. The cheapest safe switch (option A below) carries the old data layer into the new tree as untracked files.
With that, the only code changes needed are the small ones already made (section 4).

## 1. Generated headers (done)

`configure.py` can't be used as is: even with `--no-download` it runs `tools/dsd json delinks` at configure time, and
the new copy has no `tools/dsd` (it would download dsd v0.12.1-dsi.4, wibo, sjiswrap, objdiff and mwccarm). Instead
I ran the decomp's own generator scripts directly. These are the exact commands its build.ninja rules
(`gen_constants`, `text_ids`, `pms_words`, `rom_blob`) would run. Nothing was downloaded. Run from
`external/pokebw2_new` (about 1 minute, 8.7 MB, into the git-ignored `build/include/generated/`):

```sh
G=build/include/generated
for s in generated/*.txt; do python3 tools/data/gen_constants.py "$s" "$G/constants/$(basename "$s" .txt).h"; done
for a in system script; do for s in res/text/$a/*.txt; do
  python3 tools/text/text_ids.py "$s" "$G/text/$a/$(basename "$s" .txt).h"; done; done
python3 tools/text/pms_words.py "$G/constants/pms_words.h"
python3 tools/build/rom_blob.py extract/b2_us/dsi/ltd_autoload_0.bin config/b2_us/arm9/ltd_autoload_0/symbols.txt DSP_G711Image "$G/rom/dsp/dsp_g711_image.inc"
python3 tools/build/rom_blob.py extract/b2_us/dsi/ltd_autoload_0.bin config/b2_us/arm9/ltd_autoload_0/symbols.txt DSP_GraphicsImage "$G/rom/dsp/dsp_graphics_image.inc"
```

Output: 37 constants headers (`abilities, areas, encounters, field_props_*, field_scripts, flags, item_icons, items,
map_*, moves, narc_intro, natures, obj_codes, places, pms_words, script_text_banks, sound*, species, text_banks,
tr_ai_scripts, trades, trainer_*, trainers, types, vars, zones`), 495 + 676 text-ID headers and 2 DSP blobs, for 1210
files in all. They live under `build/`, so if `build/` is ever moved (switch-over, or the 10-18 incident) they must be
moved with it or made again with the commands above.

## 2. Comparison results

### Assembled bytes (old vs new decomp, every version)

The test used a harness (scratchpad `compare.py`) that runs the same clang / llvm-nm / llvm-objcopy commands as
`patches/scripts.py`, `encounters.py` and `trainers.py`. It covered every `version.overlay` set: field scripts
Sapphire 521 / Ruby 524 / Emerald 607 with each version's `-D HOENN_<V> -D HOENN_VERSION_ID`, encounters 98/98/103,
and trainers 605/605/605. Trainers were compared on both `.trainer` and `.party`, and undefined names were checked as
`scripts.py` does.

| Sources | Unique assemblies | New copy as is | + generated `-I` | + old `asm/encounters.inc`, `asm/trainer.inc` |
|---|---|---|---|---|
| `src/field_scripts` | 1652 | 1652 errors (`constants/abilities.h` not found) | **1652 identical** | 1652 identical |
| `src/encounters` | 158 | 158 errors | 158 errors (`asm/encounters.inc` not found: gone, encounters are JSON now) | **158 identical** |
| `src/trainers` | 1108 | 1108 errors | 1108 errors (`asm/trainer.inc` gone, trainers are JSON now) | **1108 identical** |

Option A (the old 9 constants headers and 9 `asm/*.inc` files that the new tree lacks, placed in the new
`include/`, plus the generated `-I`) also gives 1652 + 158 + 1108 identical. After the edits in section 4, the real
`patches/scripts.assemble()` gives the same bytes with `DECOMP` = old and `DECOMP` = new for all 521 Sapphire
scripts.

Other assembler call sites that read the decomp's include/: `patches/hm_free.py` `_assemble`, `patches/exp_share.py`
`_test_party`, `script_check.py`, `scene_walks.py` and `rooms_check.py` (`-E` preprocessing). All of them include
`asm/field_script.inc`. The new copy's version of that file also includes `constants/trades.h` and
`constants/trainers.h`, which exist only as generated headers, so each call site now passes the generated `-I` too.

### Constant names our Python reads

The generated headers use `#define NAME value`, not enums. Values are decimal, except for lists that use hex values
(flags, vars). So regexes like `#define (ITEM_\w+)\s+(\d+)` still match. Every numeric `#define` of the old 17
`include/constants/*.h` is still defined in the new copy, with the same value; the old headers held 4,431 such
defines, none of them missing or changed. Within each file the order is the same.

The breakage is about **paths**, not regexes. These headers are no longer in `include/constants/`; they are now only
in `build/include/generated/constants/`: `abilities.h, flags.h, items.h, moves.h, sound.h, species.h,
trainer_classes.h, types.h, zones.h`. `arc, battle, field_script, hold_effects, move_effects, pokemon, tr_ai,
version.h` stay in `include/constants/`. Readers that open `{DECOMP}/include/constants/{species,moves,items,
trainer_classes}.h` would raise FileNotFoundError on the new copy without option A:

- b2tools: `gen_docs.py:39`, `patches/new_tms.py:105,166`, `patches/trade_evos.py:49-51`,
  `patches/hoenn_pokedex.py:401`, `patches/roamers.py:89`, `patches/frontier_factory_dome.py:124`,
  `patches/frontier_palace_arena.py:154-156`, `patches/emerald_mech.py:110`, `patches/frontier_core.py:72,158`
  (the save helper's file, not touched).
- converter: `gen_items.py:32,40,252`, `gen_key_items.py:90`, `gen_trainers.py:582-584,821`,
  `gen_frontier_emerald.py:220-222`, `gen_frontier_pike.py:87-88,219-221`, `gen_frontier_pyramid.py:100,119-120,153-155`,
  `gen_battle_tower.py:99-100,145-147`, `sprite_sheet.py:58`.

If these readers are ported to the generated path instead (option B), note what the new headers add: species.h gains
`SPECIES_EGG` (650), `SPECIES_BAD_EGG` and `SPECIES_POKESTAR_*` (651-684), and items.h gains `ITEM_UNUSED_<n>` for 21
unused numbers. A reader that inverts the dict, takes `max()`/`len()`, or maps Gen 3 names by name would see these
extra names. One example: Gen 3 `SPECIES_EGG` would now map to 650.

### Symbols (config/b2_us/**/symbols.txt, 350 files in both)

There are 55,438 old and 56,256 new entries. 23,923 old entries were renamed at the same address and kind, mostly
`func_`/`data_` names that got real names. Addresses can't move, because it is the same ROM.

- **By-name lookups in our code:** only `patches/fairy_ui.py` (`Module.funcs[...]`). 23 of its 31 names are gone in
  the new copy. Examples: `func_ov142_0219c444` is now `ItemMenuProc_Init`, `func_ov168_021ed81c` is now
  `BtlvInput_DrawMoveTiles`, and all `func_ov207_*`, `func_ov296_0219ec08..f6ac` and `func_ov300_021a3d04` were
  renamed. **Fixed** (section 4). All 31 now resolve to the same (address, size) with both copies.
- Address-to-name readers (`armdis.py`, `playtest/syms.py`) only print names, so they now show the new names. Nothing
  breaks.
- 115 old `func_`/`data_` names and a few real ones (`ITEM_CATEGORIES` is now `sItemPockets`, `g_SaveControlWork` is
  now `SaveControlWork`, `sys_reset` is now `OS_ResetSystem`, `cp15_flushDC` is now `DC_FlushRange`, ...) appear in
  our comments and in our own `#define`s in patch .c files. Those use fixed addresses, so they are only stale names in
  notes. The full list is in the scratchpad `symdiff.txt`.

### Text (a/0/0/2 system, a/0/0/3 script)

- **Same file numbers:** each archive still has 495 / 676 files. The old packer on the old `data/text/<kind>` and the
  new packer on `res/text/<kind>` give **byte-identical archives**, and both are equal to the build base's
  `a/0/0/2` and `a/0/0/3`.
- **Different names and format:** files are now named after `generated/text_banks.txt` / `script_text_banks.txt`.
  Examples: `0090_species_names.txt` is now `species_names.txt`, `0109_place_names.txt` is now `place_names.txt`,
  `0381_trainer_msg_load.txt` is now `trainer_messages.txt`, `0402_btl_main.txt` is now `btl_main_13.txt`,
  `0403_move_names.txt` is now `move_names.txt`, `script/0208_*` is now `script/global_10520.txt`. 81 system and 3
  script banks are still just numbers.
  - Every message line is now `Id = text`. The new `pack_file` refuses lines without an ID.
  - Name lists come from JSON through `\from{species.name}` lines, so line N of a file is no longer message N.
  - The packer moved: `tools/scripts/text_data.py` is now `tools/text/text_data.py`, and it imports `tools.text.*`
    and `tools.data.*` as a package.
  - So `patches/text.py` (copytree of `data/text/<kind>`, overrides keyed `system/0109_place_names.txt` by line), the
    `pack_file` call in `exp_share.py`, and the line readers in `gen_docs.py`, `new_tms.py:120`, `gen_dex_text.py`,
    `gen_trainers.py:646-869`, `gen_hidden_items.py:100`, `gen_frontier_pike.py:77-80` and
    `gen_battle_tower.py:97-104` all need the old layout.

### Other decomp paths HoennB2 uses

| Old path | New copy | Used by (build-time = run by build_rom patches) |
|---|---|---|
| `build/`, `extract/`, `orig/` | kept from the old copy (switch plan) | build_rom, every patch |
| `tools/dsd` (+ `dsd.rev`, v0.12.1-dsi.1) | **missing** (configure would download dsi.4) | `build_rom.py:136` (build), `patches/title.py:380`, `fairy_check.py:61` |
| `tools/scripts/narc.py` | `tools/data/narc.py` (same API) | `narcio.py` (every build), `frontier_core.py:145` |
| `tools/scripts/text_data.py`, `msgdata.py`, `field_script.py`, `field_commands.json` | `tools/text/*`, `tools/script/*` (package imports; new `pack_file` needs IDs) | `patches/text.py`, `exp_share.py:246`, `script_check.py:46` |
| `include/asm/trainer.inc`, `encounters.inc` (+ 7 more .inc) | **gone** | `patches/trainers.py`, `patches/encounters.py` (build) |
| `data/text/{system,script}` | `res/text/...` (renamed, ID format) | `patches/text.py` (build), converters above |
| `data/zones/0000_zone_headers.s` | `res/field/zones/*.json` | `zones.py` (`hm_free.py:1112` at build, `specials.py`, `script_check.py`) |
| `data/moves/*.s` | `res/moves/<name>/data.json` | `patches/frontier_palace_arena.py:98-128` (build) |
| `data/evolutions/*.s` | `res/pokemon/<name>/data.json` `evolutions` | `patches/emerald_mech.py:119` (build) |
| `data/personal/*.s`, `data/growth_rates/*.s` | `res/pokemon/.../data.json` | `converter/level_scaling.py:176,189` |
| `data/field_scripts/1240.s`, `1241.s` | `res/field/scripts/<name>.s` (`SCRIPTS_GLOBAL_7000` / `_8000`) | `converter/gen_items.py:94`, `gen_hidden_items.py:225` |
| `config/b2_us/**/symbols.txt` | present, renamed symbols | `fairy_ui.py` (fixed), `armdis.py`, `playtest/syms.py` |
| `include/`, `lib/nitro/include` | present | all assemblers |

## 3. Two ways to switch

**Option A (recommended now): new decomp plus the old data layer.** Move the old pieces the new tree lacks into it as
untracked files. None of these names exist in the new clone, so nothing tracked is overwritten. The pieces are
`tools/dsd` + `dsd.rev`, `tools/scripts/`, `data/` (32 MB), the 9 constants headers that are now generated
(`abilities flags items moves sound species trainer_classes types zones`) and the 9 `include/asm/*.inc` that are gone.
Every reader above then works unchanged, the ROM bytes are unchanged (tested above), and you get the new C sources,
symbols and config for research. With only the section 4 edits needed, the blockers are small.

Caveat: the old headers in `include/constants/` shadow the generated ones, and their include guards are the same.
Before running the decomp's own `configure.py`/`ninja`, move those 9 headers aside. The `git status` of the new clone
lists them as untracked.

**Option B (later, a real port): move HoennB2 to the new layout.** This is roughly:

- one `b2tools` helper that resolves a constants header (generated first, then `include/constants`) and the decomp's
  `-I` list;
- `narcio.py` imports `tools/data/narc.py`;
- `patches/text.py` and `exp_share.py` unpack the build base's `a/0/0/2`/`3` with `unpack_file`, apply our files and
  overrides by number, and pack. With the new `pack_file`, each line gets a dummy `M<n> = ` ID;
- `zones.py` reads `res/field/zones/*.json` (number order from `generated/zones.txt`);
- `frontier_palace_arena.py` and `emerald_mech.py` read `res/moves` and `res/pokemon` JSON;
- our own copy of the trainer/encounter macros, or switch those sources to the decomp's JSON packers. Copying the
  decomp's `.inc` files into HoennB2 brings GPL-3.0 files into the MIT public repo: ask first;
- every converter reader listed above;
- `frontier_core.py` (the save helper's file, after their work lands).

## 4. Changes made in the main tree (uncommitted; they work with both copies)

- `b2tools/patches/scripts.py`, `b2tools/script_check.py`, `b2tools/patches/hm_free.py`, `b2tools/patches/exp_share.py`,
  `b2tools/scene_walks.py`, `b2tools/rooms_check.py`: each now also passes `-I {DECOMP}/build/include/generated`
  after the nitro include. clang ignores a missing `-I` directory, so this does nothing with the old copy.
- `b2tools/patches/fairy_ui.py` `symbols()`: also indexes each function under its address name
  (`func_ovNNN_xxxxxxxx` / `func_xxxxxxxx`) with `setdefault`. With the old copy the result is unchanged; with the new
  copy, the 23 renamed functions resolve to the same address and size.

## 5. Switch-over (one command; NOT run)

This is option A. Every `mv` stays on one volume, so it is instant and there is no copy. The build base ends up at
`external/pokebw2/build` and `extract` again, at the same paths and with the same files. The new copy's own `extract/`
(a copy) and the rest of the old tree go to the Trash. Stop any running ROM build first.

```sh
cd ~/Documents/GitHub/HoennB2/external && T=~/.Trash/pokebw2_switch_$(date +%Y%m%d_%H%M%S) && mkdir "$T" && \
mv pokebw2_new/extract "$T/pokebw2_new_extract" && mv pokebw2/extract pokebw2_new/extract && \
mv pokebw2/build/b2_us pokebw2/build/pokeblack2_us.nds pokebw2_new/build/ && \
mv pokebw2/tools/dsd pokebw2/tools/dsd.rev pokebw2/tools/scripts pokebw2_new/tools/ && \
mv pokebw2/data pokebw2_new/data && \
for h in abilities flags items moves sound species trainer_classes types zones; do mv pokebw2/include/constants/$h.h pokebw2_new/include/constants/; done && \
for i in baby_species encounters evolution growth_rates levelup_moves move_data personal trainer zone_header; do mv pokebw2/include/asm/$i.inc pokebw2_new/include/asm/; done && \
mv pokebw2 "$T/pokebw2_old" && mv pokebw2_new pokebw2 && echo switched
```

After it: rerun the comparison, then one Sapphire build, to confirm the ROM SHA-1 matches the build from before the
switch (`b2tools/build_rom.py` with the usual patch list). To undo: `mv` the folders back from `$T`.

## 6. Needs the user

- Choose option A now (the command above) or a full port (option B, a few hours of tool work across about 25 files,
  including `frontier_core.py`).
- Option B question: may HoennB2 carry its own copy of the decomp's trainer/encounter macros (GPL-3.0) in the MIT
  repo, or should those sources move to the decomp's JSON format?
- Rebuilding the build base with the new decomp's own build (as on 10-18) needs `configure.py` to download its
  pinned dsd v0.12.1-dsi.4, wibo, sjiswrap, objdiff and mwccarm. The old copy's `tools/mwccarm`, `wibo` and
  `objdiff-cli` go to the Trash with the old tree in the plan above. Move them into the new `tools/` too if offline
  rebuilds matter. The new configure checks wibo's SHA-256 and may still replace it.
- The Trash keeps what the switch moves there until it is emptied: about 0.6 GB left of the old tree (mostly
  `orig/`, which the new copy already has) plus the new copy's duplicate `extract/` (278 MB). Emptying it is the
  user's call.
