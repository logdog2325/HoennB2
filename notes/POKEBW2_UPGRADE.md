# Upgrading external/pokebw2 to the latest decomp (RESUME item 17, 2026-10-18)

**Status 2026-10-25: switched (section 7).** HoennB2's readers now use `external/pokebw2_new` at 0f2e215061 (the same
commit as PearlB2's `external/pokebw2_latest`) for the decomp's source, through `b2tools/b2decomp.py`. The ROM
builder's base (`external/pokebw2/build`, `extract`, `orig`, its `tools/dsd` and `config/`) is unchanged and was not
moved. Sections 1-6 are the 2026-10-18 study (at b1bcf254a); section 5's plan was replaced by section 7.
**Step 2 (2026-10-25): building from source works (section 8).** The decomp builds the dump byte for byte offline,
`HOENN_CODE=source` builds our ROMs from it (Sapphire v18.3 byte-identical), and the Gen 6 Exp. Share runs as C.

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

(These are the b1bcf254a commands. From 0f2e215061 on, `rom_blob.py` takes a subcommand and there is one more
generated file; section 7 has the current commands.)

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

## 5. Switch-over (one command; NOT run, replaced by section 7)

Not used: it moves `external/pokebw2/build` and `extract`, which must stay where they are (the ROM builder's base).

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

## 7. The switch (done 2026-10-25)

**Commit.** `external/pokebw2_new` (a shallow clone of fuddlesworth/pokebw2) is at **0f2e215061** (2026-10-25, "GFL:
bring ArchiveMoveImageTop to 9 lines of the original"). That is the same commit as PearlB2's
`external/pokebw2_latest`; origin/main had already moved on to be2c125a7 by then. The repo states no percentage: its
README only shows CI badges (bytematch.dev). In its `docs/source-files.md`, 1151 overlay files are "complete" and 43
are "partial". PearlB2's notes say about 99% C. Only the source was fetched (`git fetch --depth=1`, 12 MB). No
toolchain was downloaded, and `configure.py` was not run.

**Layout.** One module, `b2tools/b2decomp.py`, says where everything is:

| Name | Path | What our readers take from it |
|---|---|---|
| `b2decomp.SRC` | `external/pokebw2_new` (`HOENN_DECOMP=<dir>` overrides, relative to the repo) | `include/`, `lib/nitro/include`, `build/include/generated/`, `config/**/symbols.txt`, and option A's old data layer |
| `b2decomp.BASE` | `external/pokebw2` (never moved or modified) | `build/b2_us` (the matching build), `extract/`, `orig/`, `tools/dsd` and the `config/` it reads |
| `b2decomp.dsd()` | `BASE/tools/dsd` | `dsd rom build` / `dsd dis`; checks its SHA-1 (v0.12.1-dsi.1) first |

- **Option A data layer:** untracked APFS clones (`cp -c`, no extra disk) of the old copy's `data/`, `tools/scripts/`,
  the 9 constants headers that are now generated (`abilities flags items moves sound species trainer_classes types
  zones`) and the 9 `include/asm/*.inc` that are gone (`baby_species encounters evolution growth_rates levelup_moves
  move_data personal trainer zone_header`). Each is byte-identical to the old copy's file. `git status` in the clone
  lists them as untracked.
- **dsd stays with the base,** not in SRC. The old dsd cannot read the new config (`delinks.txt:1914: section .ltdmain
  does not exist`), and the decomp's `configure.py` replaces `tools/dsd` with its own pinned version (now
  v0.12.1-dsi.9). `fairy_check.py`'s `dsd dis` therefore runs in BASE with BASE's config.
- **39 readers changed** (b2tools: `build_rom narcio npc_check script_check zones scene_walks rooms_check armdis
  playtest/syms gen_docs fairy_check special_zones_check`; patches: `fairy_ui hm_free text frontier_palace_arena trainers
  frontier_core trade_evos scripts emerald_mech exp_share new_tms encounters roamers hoenn_pokedex frontier_factory_dome
  title`; converter: `gen_trainers gen_key_items gen_frontier_pike gen_items gen_hidden_items gen_frontier_pyramid
  gen_frontier_emerald gen_battle_tower level_scaling sprite_sheet gen_dex_text`). Decomp source paths now go
  through `SRC`, and build/extract paths go through `BASE`. Readers that only read `external/pokebw2/build|extract`
  (about 50 files) keep their paths, which are still right.
  `armdis.symbols` reads BASE's symbols, then SRC's. The new names win, and the ~1,050 addresses (mostly inner data
  labels) that the new config no longer labels keep their old names. `special_zones_check` now reads our own generated
  `zones.h` instead of PearlB2's.

**Proof (2026-10-25).** All builds below used main 8e6fc0f (the same code as aa8e3a3 plus RESUME only) and
`HOENN_BUILD_DIR=work/agents/decomp_switch/rom`. The Sapphire world and rooms were clones of `~/HoennB2_lead/work/
world_rel` + `interiors`, and the Emerald ones were clones of `~/HoennB2_em/work/world_emerald` + `interiors`.
Each build used story_build.sh's patch list.

| Build | Old tree (code before the switch) | New tree (after) |
|---|---|---|
| no patches (`HOENN_BERRY_PLANTING=0 build_rom.py --clean --no-pad`) | (dump) | `e51e6dfb…0abb`, "matches original" |
| Sapphire story_build | `107b5495…` (= the v18.3 release) | `107b5495…` |
| Emerald story_build | `4290ed00…` (= the Emerald v1.4 release) | `4290ed00…` |

- `python3 b2tools/decomp_check.py`: every field script, encounter table and trainer assembles to the same bytes with
  both trees (Sapphire 541/98/605, Ruby 544/98/605, Emerald 674/105/605). All 31 `fairy_ui` function names resolve
  to the same (address, size).
- Converters: 19 runs, in clones of the repo, of the code before the switch with the old tree and the code after it
  with the new tree. The runs were gen_items/key_items/hidden_items/trainers (S, R, E), battle_tower, level_scaling,
  dex_text, the Emerald frontier/tents/hill generators, sprite_sheet and gen_docs. Their data/, src/, docs and sprite
  sheet came out identical.
- Every numeric `#define` of the old 17 constants headers is still defined in the new copy, with the same value
  (4,431 of them).

**What our readers see differently** (none of it changes a ROM byte):
- New symbol names: 23k+ `func_`/`data_` names became real names. `fairy_ui`'s by-address fallback (section 4) covers
  the renames.
- The new `asm/field_script.inc` also includes the generated `constants/trainers.h`. That header now defines Black 2's
  `TRAINER_NATE` (360) and `TRAINER_BIANCA` (4). Our `src/include/hoenn_trainers_emerald.h` defines them again
  (347 / 428) later in the same file, so ours win and the bytes are identical. clang prints "macro redefined" warnings
  for the ~16 scripts that include it (Emerald builds). A later cleanup could `#undef` them in that generated header.
- `Cmd_0221`/`Cmd_0222` were renamed `AnvilleTrainGetModelID`/`AnvilleTrainGetDailyIndex` (we use neither). The new
  `pokemon.h` no longer defines `SPECIES_EGG` itself (the generated `species.h` does; ours only names it in a comment).

**Update again later** (from the repo root; nothing here touches BASE):
```sh
cd external/pokebw2_new
git fetch --depth=1 origin <commit, or main> && git checkout -B main FETCH_HEAD   # stops if upstream adds a file at an option A path
mv build/include/generated ~/.Trash/pokebw2_generated_$(date +%Y%m%d_%H%M%S)     # stale headers out, then regenerate:
G=build/include/generated; mkdir -p $G/constants $G/text/system $G/text/script $G/rom/dsp $G/rom/syscall
for s in generated/*.txt; do python3 tools/data/gen_constants.py "$s" "$G/constants/$(basename "$s" .txt).h"; done
for a in system script; do for s in res/text/$a/*.txt; do python3 tools/text/text_ids.py "$s" "$G/text/$a/$(basename "$s" .txt).h"; done; done
python3 tools/text/pms_words.py "$G/constants/pms_words.h"
python3 tools/build/rom_blob.py array extract/b2_us/dsi/ltd_autoload_0.bin config/b2_us/arm9/ltd_autoload_0/symbols.txt DSP_G711Image "$G/rom/dsp/dsp_g711_image.inc"
python3 tools/build/rom_blob.py array extract/b2_us/dsi/ltd_autoload_0.bin config/b2_us/arm9/ltd_autoload_0/symbols.txt DSP_GraphicsImage "$G/rom/dsp/dsp_graphics_image.inc"
python3 tools/build/rom_blob.py range extract/b2_us/arm9/arm9.bin 0x02004000 0x02004800 FILLER "$G/rom/syscall/secure_area_b2_us.inc"
cd ../.. && python3 b2tools/decomp_check.py          # must print OK (old = external/pokebw2, new = b2decomp.SRC)
```
These commands mirror configure.py's `gen_constants`, `text_ids`, `pms_words`, `rom_blob` and `rom_range` rules; check
them there if a rule changes. They produce 1211 files (8.9 MB). Then build once with
`HOENN_DECOMP=external/pokebw2` and once without, using the same world, rooms and patch list. The two ROMs must have
the same SHA-1. Also grep the new tree for anything our readers still need from the old layout (`data/`,
`tools/scripts/`, the 18 option A files): upstream may change what the generated headers define.

**Step 2 (building the decomp from source) needs to know:**
- `configure.py` downloads dsd v0.12.1-dsi.9, wibo, sjiswrap, objdiff and mwccarm (ask the user first). Its
  `tools/dsd` goes into SRC. That cannot change our ROMs, because `b2decomp.dsd()` uses BASE's dsd, pinned by SHA-1.
- Before the decomp's own build, move option A's 9 `include/constants/*.h` aside: they shadow the generated headers.
  The 9 extra `include/asm/*.inc`, `data/` and `tools/scripts/` are not read by its build. Put everything back
  afterwards, or port those readers (option B, section 3). (Step 2 did neither: its `configure.py` puts the generated
  headers first, section 8.)
- SRC has its own `orig/baserom_b2_us.nds` (identical to BASE's) and its own `extract/` copy, so the decomp's build
  writes only inside `external/pokebw2_new`.

## 8. Building from source (step 2 feasibility, 2026-10-25)

Goal (user-approved): build Black 2's code from the decomp's C, so features are written as changes to the game's
code instead of patches on the finished binaries. This section is the feasibility study, not the migration.

### 8.1 Results

| Check | Result |
|---|---|
| Toolchain, offline | Copied (APFS clones) from PearlB2's `external/pokebw2_pearlb2/tools`, nothing downloaded. SHA-256 = `configure.py`'s pins: wibo `d11a80c3…` (pokebw2-sjis-1, macOS), sjiswrap `4e9c917b…` (v1.2.2-pokebw2.1); dsd `1357b8d2…` with `dsd.rev` v0.12.1-dsi.9 (configure pins the version only); mwccarm dsi/1.1p1 `bcc7d057…` (= our old copy's), dsi/1.1 mwldarm, 1.2/base, 2.0/sp1p2, 2.0/sp2, dsi/1.2. objdiff-cli v3.8.1 is not there and not needed (only the decomp's progress report). |
| The decomp, as is | `configure.py --no-download b2_us` + `ninja -j5 b2_us`: 5 min 27 s, all 344 overlays and modules "OK", ROM SHA-1 **`e51e6dfb…0abb` = the dump**. Its code binaries equal BASE's except the dsd windows (below); its 318 NitroFS files equal BASE's. |
| With our hooks, switched off (`HOENNB2 0`) | Again `e51e6dfb…0abb`; `decomp_build.py changed` lists nothing; layout check: 48,572 symbols in place. |
| Our pipeline on it, no patches | `HOENN_CODE=source build_rom.py --clean --no-pad` (berries off): "matches original". The copied code dir is byte-identical to BASE's `build/b2_us/build` after `dsd_compat`. |
| Our pipeline on it, Sapphire story_build list, `HOENNB2 0` | **`107b5495…` = the v18.3 release**, byte for byte (release world clones). |
| Exp. Share in C (`HOENNB2 1`), Sapphire | Every patch of the list applies; nothing breaks. `exp_share` sees the C and patches nothing. In DeSmuME (8.5) the battle and the bag switch work exactly as the binary version. |
| Exp. Share in C, Emerald | Every patch applies (ROM `f2017ff1…`), but ITCM is now nearly full: **160 B left** (8.6 Risks). |

`decomp_build.py changed` with the Exp. Share in C, exactly the expected functions: arm9 `sItemPockets` (1 B: item 216 =
key items), `OS_GetInitArenaLo` (2 B: the ITCM arena literal) and `BuildInfo` (4 B), ov142 `sItemMenuFieldUses`
entries 8-9 (7 B), ov167 `ServerControl_CheckExpGain` (4 B: the call), and 1,088 B of new ITCM code. Making three
static functions global (`HOENNB2_STATIC`) changed no byte.

### 8.2 How it is set up

- **Decomp tree:** `external/pokebw2_new` (SRC), uncommitted local changes on top of 0f2e215061 (saved as
  `work/agents/decomp_src/hoennb2_decomp.patch`; nothing committed, no branch pushed):
  - `include/hoennb2.h`: `#define HOENNB2 1`, the rules, our prototypes and constants, `HOENNB2_STATIC`;
  - `src/hoennb2/exp_share_itcm.c`: the new code (all inside `#if HOENNB2`);
  - `tools/hoennb2/link_itcm.py` + three small `configure.py` blocks: `src/hoennb2/*_itcm.c` linked after Black 2's
    ITCM code; the `b2_us_hoennb2` target (code binaries + files, no ROM); `src/hoennb2` as a configure input. The same
    design as PearlB2's `pearlb2` branch (PearlB2 `notes/DECOMP_WORKFLOW.md`, read only);
  - `configure.py` also puts `build/include/generated` FIRST in the include path, so option A's 9 old constants
    headers (section 7) no longer shadow the generated ones. Nothing has to be moved aside, and our readers keep
    working while the decomp builds (no other header name is in both places; the ROM is still the dump's);
  - the game files with a hook, each `#if HOENNB2 … #else <original> #endif`: `src/ov167/btl_server_flow.c`,
    `btl_server_flow_sub.c`, `src/ov142/itemmenu.c`, `src/system/myitem_savedata.c`.
- **Configure once** (in SRC): `PATH=/opt/homebrew/opt/llvm/bin:$PATH python3 configure.py --no-download b2_us`.
  ninja reruns it by itself after that.
- **`b2tools/decomp_build.py`** (HoennB2's copy of PearlB2's `decomp.py` idea): `build` (ninja `b2_us_hoennb2` under a
  lock + layout check), `check`, `changed`, `vanilla [--rom]` (HOENNB2 0 must give the dump), `symbol NAME`,
  `dsd_compat()`, `copy_map()`.
- **`b2decomp.CODE`** / `HOENN_CODE=base|source`, `b2decomp.code_dir()`.
- Cost: no-op ninja + check 1-3 s; a C change about 100 s (compile + the whole-game link); a full decomp build from
  nothing 5.5 min. Disk: SRC's `build/` 0.9 GB. `ninja b2_us` (the ROM check) also writes a 512 MB ROM, identical
  to `orig/`; replace it by an APFS clone of `orig/baserom_b2_us.nds` afterwards (the two from this study are in the
  Trash).

### 8.3 How build_rom.py takes decomp-built code (done for the prototype)

With `HOENN_CODE=source`, `build_rom.py --clean`:
1. `decomp_build.build()`: ninja `b2_us_hoennb2` (incremental) and the **layout check** (every module its dump size,
   ITCM may only grow; every symbol of the decomp's `symbols.txt` at its address in the link map). It stops the build
   if a C change moved anything;
2. copies SRC's `build/b2_us/build` into `<build>/code` under the same lock (instead of BASE's);
3. `dsd_compat()` on the copy: the decomp (dsd dsi.5+) links the overlay digests (`OverlayTableDigests` ..
   `SDK_OVERLAY_DIGEST_END`) and one word of `LtdModuleParams` as zeros for its own dsd to fill; our ROM writer is
   still BASE's dsd dsi.1 (pinned by SHA-1), so the dump's bytes go back there, `overlay_signatures: 0`,
   `table_signed: false`, and the 2 DS Protect `bss_variable` lines the new yaml lacks come back from BASE's yaml;
4. copies the link map (`arm9.o.xMAP`) next to the code, so a patch can ask `decomp_build.symbol(name, code)` where our
   C put something (exp_share does, to see whether the C version is there);
5. then everything as before: NitroFS files from BASE (identical to SRC's), every patch, padding, BASE's dsd writes the
   ROM.
Without `HOENN_CODE` nothing changes (`code_dir()` = BASE's build).

### 8.4 The rules while binary patches remain

Our 50 code patches hard-code about 900 addresses (in the .py files and the clang .c files). Black 2's overlays are
chained in memory, so a C change that makes a function a byte longer moves everything after it and those patches
stop applying (they assert the bytes they replace, so the build stops; it never silently breaks). So, for now:
1. a change in a game file keeps its function's size (a call target, a constant, a table value), original in `#else`;
2. new code goes to the resident section, `src/hoennb2/resident/*.c` (section 9; ITCM, `src/hoennb2/*_itcm.c`, only for code
   that runs before it is read, or in an interrupt);
3. per-version data (Sapphire/Ruby/Emerald) is not compiled into the decomp: either the same for all three (the
   Exp. Share's flag and message ids; exp_share.py checks they equal ours) or a table in the resident pool with a pointer
   the patch fills in (`resident.install`, `resident.write`; followers.py, feebas.py), so one decomp build serves all three;
4. only files marked `complete` in `config/b2_us/**/delinks.txt` are linked from C (1151 complete, 43 partial);
5. `decomp_build.py vanilla` must give the dump with `HOENNB2 0`.

### 8.5 The prototype: Gen 6 Exp. Share

Before: `patches/exp_share.py`, about 50 lines of hand-assembled Thumb in 7 places (the dead held-item block of ov167
`AddExpAndEVs`, a rewritten `ServerControl_GiveExp` body, a call site, the arm9 SDK version strings for the bag
handler, `ITEM_CATEGORIES`, the ov142 Use table), each checked against the dump's bytes.
After (`src/hoennb2/exp_share_itcm.c`, 195 lines of readable C with the decomp's names):
- `HoennB2_GainExpFromFainted` (replaces the call in `ServerControl_CheckExpGain`): Black 2's own
  `ServerControl_GainExpFromFainted` while `FLAG_EXP_SHARE_ON` is off; on: `HoennB2_AddExpAndEVs` (Black 2's function
  with the Gen 6 share in place of the held item's: every mon that can battle gets base/2, the ones that faced the
  foe their usual share, marked in the unused `unk0B`), then the participants' messages, one team line, the benched
  mons' exp without a line (`HoennB2_GiveExp`);
- `HoennB2_ExpShareToggle` (the freed Xtransceiver entry of `sItemMenuFieldUses`): flips the flag and shows the bag
  message;
- `sItemPockets[ITEM_EXP_SHARE] = BAG_POCKET_KEY_ITEMS`.
The data and text parts (item 216's record, bag/battle lines) stay in `exp_share.py`; its `apply_code` now only checks
the C's constants and tables when the code has `HoennB2_GainExpFromFainted`, else does the old binary patch.
Behaviour: the same rules and messages as the binary version (participant `=` share, flag read from the save,
Lv 100 skipped, team line only when a benched mon got exp). Not identical bytes: the old version also freed 136 B of
ov167 and 48 B of arm9 strings; the new one leaves them as Black 2 had them and uses 1,088 B of ITCM instead.

**Test (DeSmuME, 2026-10-25, `work/agents/decomp_src/pt/exp_test2.py` and `exp_bag.py`, a copy of the playthrough
driver).** Sapphire story_build list, `HOENN_CODE=source`, `HOENN_TEST_EXPSHARE=2` (new, test only: as `=1`, and
Littleroot's town sign starts a wild battle against a Lv 2 Wurmple); cold boot through the intro, Littleroot gives
Treecko 5, Torchic 5, Mudkip 1 and the Exp. Share (on).
- Battle: "Treecko gained 10 Exp. Points!", then "The rest of your team gained Exp. Points thanks to the Exp. Share!",
  then "Mudkip grew to Lv. 2!" and its stat windows; no line for Torchic or Mudkip. Party exp: Treecko 135 -> 145
  (+10), Torchic 135 -> 140 (+5), Mudkip 0 -> 9 (Lv 1 -> 2). The same numbers and lines as the binary version's test
  (notes/RESEARCH_EXPSHARE_HM.md, "Tests" 3). `screenshots/decomp_src/exp_share_in_c_battle.png`.
- Bag: Key Items -> Exp. Share -> USE: "The Exp. Share was turned off." (flag 2058: 1 -> 0), again: "... turned on."
  (0 -> 1). `screenshots/decomp_src/exp_share_in_c_bag_toggle.png`.
- Note for this kind of test: `HOENN_TEST_EXPSHARE` replaces all of Littleroot's scripts, so after the truck the
  screen stays black (no moving-in scene, no fade-in) and the north exit runs into a broken scene; go in and out of
  the house first (the door has its own fade-in) and battle at the sign.

### 8.6 Migration plan

**Phase 1: from-source builds as the default (about half a day).** Commit the decomp changes on a local branch
`hoennb2` in `external/pokebw2_new` (never pushed without the user's OK; the remote is fuddlesworth's); commit
`decomp_build.py` and the `build_rom`/`b2decomp`/`exp_share` changes; make `HOENN_CODE=source` the default in
`story_build.sh`, `rebuild_slice.sh` and the release scripts. Proof before switching: S/R/E release builds with
`HOENNB2 0` must give the last release SHA-1s (done for Sapphire today), then `HOENNB2 1` with the Exp. Share in C and
one Exp. Share test per version. Each helper that changes C gets its own decomp worktree (PearlB2's `agent_tree.py
decomp NAME` pattern), so half-made C never reaches another build.

**Phase 2: patches look addresses up by name (2-4 days of helper time).** This is what frees the layout. Of the
~908 addresses in `patches/*.py` and `*.c`, 607 are a decomp symbol's start and 285 are inside one (function +
offset); 16 are neither (checked against `symbols.txt`). A converter rewrites each into `sym('Name')` /
`sym('Name') + 0x1e` (resolved from the link map, `decomp_build.symbol`; the dump's `symbols.txt` for
`HOENN_CODE=base`), and the "old bytes" asserts read the decomp's own unpatched build instead of BASE. Done module by
module, each step proven by byte-identical S/R/E ROMs. After it, a C change may change sizes: the linker moves the
game and the patches follow.

**Phase 3: move patches into C (8-15 days of helper time, one patch at a time, any order).** Order, by value:
1. *Hand-assembled Thumb* (hardest to read and change, most like the Exp. Share): `hm_free` (48 addresses),
   `hoenn_pokedex` (73), `town_map`, `zone_effects`, `battle_tower`, `dive`, `fairy_ui`, `weather`, `trainers`,
   `story`, `hoenn_world` (the ITCM zone lookup). 1-3 h each plus its test.
2. *The ov167 battle group*, together, since they edit one overlay: `fairy` (61 addresses, 16 sentinels: a type
   constant change in C), `frontier_palace_arena`, `frontier_pike`, `frontier_pyramid`, `roamers`, `trainer_hill`,
   `emerald_rematch`, `capture_demo`. Their logic is already C (clang); it moves into the functions it hooks.
3. *The other clang C patches* (`berries`, `rods`, `rotating_gates`, `new_tms`, `sprite_switch`, `hoenn_music`,
   `save_compat`, `emerald_mech`, `emerald_postgame`, `frontier_core`, `frontier_factory_dome`): mostly replacing
   `FN(type, 0x…)` macros by the decomp's prototypes and the `bl` hooks by C calls; 1-2 h each. mwcc is not clang (no
   `__attribute__`, its own pragmas and warnings, `-requireprotos`); budget for that.
4. *Byte and table edits* (`met_names`, `escape_rope`, `encounter_rules`, `special_zones`, `centers`, `musical`,
   `pwt`, `starters`, `game_clear`, `link`, `sprites`, `trainer_card`, `antipiracy`, `hoenn_intro`, `hoenn_season`,
   `area2_buildings`, `opening`, `title`): a table value or constant under `#if HOENNB2`; 15-30 min each, but low value,
   so last (or never).
Per-version differences stay data (rule 3), not three decomp builds.

**Phase 4: free layout (1-2 days, once).** Drop rules 1-2, put new code in the overlay it belongs to, give ITCM back,
write the ROM with the decomp's own dsd (then `dsd_compat` goes); remake every savestate once.

**Keeping S/R/E byte-identical (or proving them equivalent) during the move.**
- Plumbing changes (Phases 1-2, and `HOENNB2 0` at any time) must give identical SHA-1s for all three versions, against
  the last release: the check that proved the switch today. `decomp_build.py vanilla --rom` proves the C side alone.
- A patch moved into C cannot be byte-identical (other bytes, ITCM shifts). Its proof is: (a) `decomp_build.py
  changed` lists only the functions it should; (b) the ROM's other bytes are unchanged apart from addresses into the
  shifted ITCM (a `cmp` script that relocates them); (c) the patch's own test from its notes, run on both ROMs; (d)
  `script_check`, `rooms_check`, `fairy_check --emu` and the other checkers as for any release.
- One moved patch per commit, so a regression points at one change.

**Savestates and layout.**
- `HOENNB2 0` or no C change: same ROM, every state works.
- C code in ITCM moves every later ITCM patch (hoenn_world, roamers, fairy, ...) by its size, and arm9 changes: old
  savestates crash (ITCM and arm9 are loaded at boot). Cold-boot or remake states after any C change (as for ITCM
  patches today); `make_states.py` and the cold-boot drivers work unchanged.
- Battery saves (.sav) are unaffected unless a C change moves save data (the Exp. Share uses the same flag 2058).
- Overlay files keep their slots: dsd still writes the same file table; an overlay whose compressed size grows past
  its 512-byte slot moves later files (the existing rule in TESTING.md).
- Phase 4 changes RAM addresses: every state once, and any tool that pins a RAM address (playthrough drivers, `emu.py`
  position addresses) must look it up from the link map too.

**Risks.**
- **ITCM space.** Fixed layout puts all new C into ITCM. With the release patch lists, Sapphire has 9,984 B left and
  Emerald 1,248 B; the Exp. Share in C takes 1,088 B (Sapphire 8,896 B left, Emerald **160 B**). The next C feature
  will not fit in Emerald until Phase 2, so Phase 2 is the real gate, not a nice-to-have.
- **Upstream changes.** Renamed functions and headers break our C (the compiler says where); rebase conflicts only in
  our `#if HOENNB2` blocks and the three `configure.py` blocks. Pin a decomp commit; update deliberately (section 7).
- **Two dsd versions.** The decomp needs dsi.9, our ROM writer is dsi.1; `dsd_compat` bridges them and asserts if
  upstream changes what dsd fills.
- **Toolchain.** wibo is an x86-64 macOS binary under Rosetta 2 (if a future macOS drops Rosetta, a native wibo build is
  needed); mwccarm is Metrowerks' proprietary compiler (allowed for pokebw2; never published).
- **Licences.** pokebw2 is GPL-3.0; HoennB2's public repo is MIT. Our C inside the decomp tree is a change to GPL code:
  keep it out of the MIT export (publish it, if ever, as a GPL patch or a fork branch). Needs the user's call before
  any publication.
- **Concurrency.** The decomp tree is shared by every helper's build: the lock, plus one decomp worktree per helper
  that changes C.
- **Partial files.** 43 decomp files are still `partial`; a change there does nothing (the ROM takes the dump's
  bytes). Check `delinks.txt` first.
- **Option A data layer.** Still in SRC for our readers; the include-order line keeps it out of the decomp's build.
  Porting the readers (option B, section 3) removes it.

**Effort.** Phase 1 half a day; Phase 2 2-4 days; Phase 3 8-15 days (about 50 patches, any order, each shippable on
its own); Phase 4 1-2 days. In all about 3-4 weeks of helper time, which can be spread over releases: after Phase 1
every new code feature can be written in C right away (in ITCM while it lasts), and old patches move when they are
next touched.

### 8.7 Files (step 2)

- New: `b2tools/decomp_build.py`; in SRC (untracked or uncommitted there): `include/hoennb2.h`,
  `src/hoennb2/exp_share_itcm.c`, `tools/hoennb2/link_itcm.py`, edits to `configure.py`, `compile_flags.txt`
  (generated), `src/ov167/btl_server_flow.c`, `src/ov167/btl_server_flow_sub.c`, `src/ov142/itemmenu.c`,
  `src/system/myitem_savedata.c`; tools copied into `SRC/tools` (git-ignored).
- Changed: `b2tools/b2decomp.py` (`CODE`, `code_dir()`), `b2tools/build_rom.py` (`HOENN_CODE=source`),
  `b2tools/patches/exp_share.py` (`_c_version`; the test switch `HOENN_TEST_EXPSHARE=2`). With `HOENN_CODE` unset
  all three behave as before.
- Proof pictures: `screenshots/decomp_src/` (battle, bag switch).
- Work files: `work/agents/decomp_src/` (build logs, `build.sh` = story_build's list on the release-world clones without
  its `rm`, the decomp patch, the test drivers in `pt/`, the one test ROM `sapphire_src_on_test2/expc_test2.nds` and its
  state `states/lr_door_c.dst`, the code dirs of the builds for comparison).

### 8.8 Phase 1: Black 2's code is built from source by default (2026-11-01)

`build_rom.py` now takes the decomp's build (`HOENN_CODE=source`) unless told otherwise. No patch list changes: the decomp
step is inside `build_rom.py`, so `story_build.sh`, `rebuild_slice.sh` and the release scripts need nothing new to use it.

**The one switch back:** `HOENN_CODE=base` = the dump's binaries from `external/pokebw2/build`, as every build before
Phase 1. The Exp. Share then falls back to its binary patch, and the C-only features stay out. `HOENN_DECOMP_C=0` is the
middle step, used for the proofs: the decomp's code with every HoennB2 C change off (the dump's bytes, checked by
`decomp_build.changed()`). Neither needs any other change: `b2decomp.c_on()` keeps text, scripts and the question consistent.

**Proofs (2026-11-01; code = main 0486a15 + Phase 1, decomp with our C off, release-world clones):**

| Version | Release | From source, C off |
|---|---|---|
| Sapphire v18.3 | `107b5495…` | **`107b5495…`**: identical (a full build, with `HOENN_DECOMP_C=0`) |
| Ruby v18.3 | `8fb0df2e…` | not built (test list: the user's "one build" process) |
| Emerald v1.4 | `4290ed00…` | not built (same) |

What covers Ruby and Emerald offline: with `HOENNB2 0` every code module equals the dump's (`decomp_build.py vanilla`, also
with the resident section and every hook in), and after `dsd_compat` the code dir equals BASE's byte for byte; the
patches then get the same input as a `HOENN_CODE=base` build. The two ROM proofs stay on the test list.

**How a release builds.**
1. `release_sr.sh` / `release_emerald.sh` first run `release_tree.sh <path> <commit>`: it creates the worktree if it is
   missing (`git worktree prune`, `worktree add --detach`), links `.venv external roms tools backups` to main's and
   makes `work/`. `rebuild_slice.sh` makes everything in `work/` (buildings, world, rooms, ROMs), so a fresh tree only
   takes as long as a full rebuild. Nothing has to be copied by hand.
2. They then run `decomp_build.py verify`: the decomp tree must be `decomp_changes/UPSTREAM` plus exactly the commit's
   `decomp_changes/hoennb2_decomp.patch`, with `HOENNB2 1`. It stops the release otherwise. It sees the decomp through the
   tree's `external` link, so main's `external/pokebw2_new` (with its git-ignored toolchain and build) serves all trees.
3. `build_rom.py` runs the decomp's ninja (a no-op when nothing changed), the layout check, copies the code, `dsd_compat`,
   adds the resident section (section 9), then the patches as always. The log's `decomp ...` line says what was built.

**A release whose patch differs from the shared tree's** (an older commit, or main's C has moved on):
`python3 b2tools/decomp_build.py setup DIR` makes a decomp tree of its own (git worktree at UPSTREAM + that commit's
patch + the toolchain, `orig/`, `extract/` and section 7's data layer as APFS clones, configured; first ninja 6-8 min,
about 1 GB), then `HOENN_DECOMP=DIR zsh release_sr.sh ...`. A helper changing C works the same way, so half-made C never
reaches another build.

**Keeping the patch current:** `python3 b2tools/decomp_build.py patch` saves the tree's changes as
`decomp_changes/hoennb2_decomp.patch` (private, GPL-3.0: `public/export.sh` never exports `decomp_changes/`). Every build's
`decomp ...` line warns if the tree differs from it; `decomp_build.py diff` shows how.

## 9. The resident section (2026-11-01): where new C goes

Instead of Phase 2 for now (PearlB2's shortcut; its notes/DECOMP_WORKFLOW.md rules 2-3). Emerald had 160 B of ITCM left with the
Exp. Share in it; now it has 1,216 B (the Exp. Share moved out; 32 B of boot code stay).

- **What:** overlay 344 (`src/hoennb2/resident/*.c`), linked after overlay 290, the last overlay of main memory, at
  0x021FD080 (`tools/hoennb2/link_overlays.py`). Code 3,744 B today (Exp. Share, followers, Feebas) + a 16 KB pool for the
  build's tables (`HOENNB2_RESIDENT_POOL`, `b2tools/resident.py`), 20,128 B in all. Nothing of Black 2 moves: the layout
  check still passes (48,572 symbols), and `bl` reaches it from everywhere (2 MB from arm9, nearer from overlays).
- **Loaded:** once at boot, right after GFL's overlay manager is set up (`GFLAppInit`'s call -> `HoennB2_OvlManagerInit`, 36 B
  of ITCM: `src/hoennb2/resident_itcm.c`), with NitroSDK's `FS_LoadOverlay`: it takes no GFL slot, nothing else loads there,
  it is never unloaded, and a soft reset reads it again. `FS_LoadOverlayInfo`'s DS-mode id check counts it
  (`HOENNB2_OVERLAY_COUNT` 345; a DSi checks no count).
- **In the ROM:** `decomp_build.install_overlays` adds its entry to `code/arm9_overlays.yaml` (unsigned, uncompressed) right
  after `dsd_compat`, before any patch. With our C off, no entry: the ROM's layout is the release's. With it on, the first
  NitroFS file id is one higher (dsd assigns them; the game opens archives by path).
- **Memory, checked against our uses (notes/TESTING.md "DSi", notes/FRONTIER.md section 7):** DS mode: the main arena now
  starts at `HOENNB2_REGION_END` 0x02201F20 instead of 0x021FD080 (`os_arena.c`), so GFL's fixed root heaps end 20 KB higher:
  about 0x023AD964 instead of 0x023A8AC4 (measured then, by the arena's table). Above it, 0x023B0000-0x023E0000 stays unused in
  Sapphire/Ruby, and Emerald's Frontier code area (0x023D0000-0x023E0000, loaded by FRAM_Boot before GameInit) is
  untouched, with about 136 KB free below it. DSi mode: 0x021FD080-0x02700000 is outside every arena (the DSi arena starts at
  0x0276DDE0), and arm9i's staging at 0x02400000 is far above the section. No patch uses 0x021FD080-0x02201F20; nothing
  of ours pins a heap address (tools scan for them).
- **Use it:** a C file in `src/hoennb2/resident/` (whole file in `#if HOENNB2`), called from a same-size call change in a
  game file; data through `#pragma explicit_zero_data on`, `Type *gName = NULL;` (it must be in .data, in the file) and
  `resident.install` + `resident.write`. `decomp_build.py changed` lists what each change touches.
- **`decomp_build.py changed` today, 19 lines:** the arena literal (`OS_GetInitArenaLo`), `FS_LoadOverlayInfo`'s count,
  `GFLAppInit`'s call, `BuildInfo`, `sItemPockets`; ITCM's 36 B; `sItemMenuFieldUses`; the Exp. Share's, Feebas's and the 8
  follower hook functions' calls. No patch address is within 4 bytes of any of them, except the ITCM arena literal, which
  the ITCM patches read and move as always.
