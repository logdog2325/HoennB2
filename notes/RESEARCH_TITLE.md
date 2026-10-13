# Title screen research: "Pokémon Sapphire" logo + Kyogre (2026-10-06)

Research only: nothing was built, patched or run in an emulator. Evidence tags: **[C]** decomp C source (file:line),
**[asm]** `b2tools/armdis.py` disassembly of the decomp's build (address), **[bytes]** bytes of the built/extracted
files, **[decoded]** decoded and rendered in this session, **[inferred]** not proven, a reading of the evidence.
Paths: `bw2/` = `external/pokebw2/`; overlay offsets are into `bw2/build/b2_us/build/arm9_ov162.bin`
(base `0x0219CE80`).

## Summary

- The title is **overlay 162**, fully decompiled and matching in C: `bw2/src/ov162/title.c` (all six ov162 files are
  marked `complete` in `bw2/config/b2_us/arm9/overlays/ov162/delinks.txt`).
- **Top screen** (sub engine): the logo is a **256-colour (8bpp) text BG**, not OBJ or 3D (sub BG3, `a/0/2/6` files
  0/1/2). Behind it, sub BG2 scrolls a strip of blue ice crystals (file 3, same tiles). "PRESS START" is a blinking
  **OBJ** (files 4–7).
- **Bottom screen** (main engine): **3D Black Kyurem** (`a/1/5/8` files 446–453: three models, their animations and
  a camera-path file), drawn through a display-capture motion blur, with "Developed by GAME FREAK inc." on main BG3
  (files 8/9/10) in front.
- The version name ("BLACK VERSION 2") and its colours are **baked into the logo bitmap and its palette**. There is
  no version text. Version differences live in ov162's code (#ifdef: 3D files, Kyurem's cry form) and in each ROM's
  own `a/0/2/6`.
- **Kyurem can be removed with a 4-byte patch**, and every 2D layer can be replaced by data alone. Kyogre's Black 2
  battle sprite (`a/0/0/4` files 7640–7659) can be shown as a static picture on a BG with data only. Showing it
  **animated** needs new code (MCSS, as the intro and the evolution screen do).
- **The logo needs your decision** (section 4): Black 2's own logo has none of the letters P and H, so a "SAPPHIRE"
  wordmark means either editing Black 2's letters (cut and paste) or drawing a new one.
- **Recommendation: option A** (2D, mostly data, four tiny ov162 patches) first. Option C (animated Kyogre through
  MCSS) is a later upgrade that reuses all of A's work.

## 1. How Black 2's title works

### Boot chain and process
- arm9 `StartMenuEventTick` (`0x020362ec`) queues, in order: ov162 `BOOT_SCREENS_PROC_FUNCTIONS` (`0x021a19e4`),
  overlay 264 twice (its only string is `cdemo_main.c`, so it is the cutscene/movie player; which movies those are is
  **[inferred]**), then ov162 `TITLE_PROC_FUNCTIONS` (`0x021a1614`) **[asm]** (literal `0x0203637c`, relocation in
  `bw2/config/b2_us/arm9/relocs.txt:8555`).
- `Title_Init` creates a 0x120000-byte heap and the sound stream (`title.c:265-274`). The music is
  `GFL_SndStreamPlay(0)` (`title.c:347`), Black 2's title theme, untouched here.
- On exit, A or Start goes to the start menu, Up+Select+B to deleting the save, and Down+X+Y to the mic test
  (`title.c:392-407`).

### State machine (`Title_Main`, `title.c:329-390`)
| State | What happens |
|---|---|
| INIT_DISPLAY | master brightness −16, all BGs off; VRAM banks + LCD config (`sVRAMConfig`, `sLCDConfig`) |
| INIT | `TitleSys_Init`, `TitleBG_Init`, `TitleG3D_Init`, `TitleObj_Init`; fade in from black; music on |
| WAIT_FADE_IN → RUN | each frame: `Title_Update` (BG scroll, camera curve stepped once per VBlank, 3D draw, OBJ) + input + timer |
| WAIT_CRY | after A/Start: Kyurem's cry, camera jumps to frame 7001, white flash, stronger blur (8/8), music fades |
| FADE_OUT → FREE → END | fade to black, free everything |

Timer (`Title_UpdateTimer`, `title.c:276-292`):
- At **frame 1740 (29 s)** the "attract" swap runs: a white flash, then the **3D moves to the top screen**
  (`GFL_BGSysSetDisplayLayout(1)`), and main BG3, sub BG2 and sub OBJ are hidden, so the bottom screen shows only the
  logo. A, B or Start brings the layers back, and the camera then loops over frames 7300–7780.
- At **frame 6780 (113 s)** the title ends with nothing chosen.

### Screens and layers
`GFL_BGSysSetDisplayLayout(0)` = `GX_DISP_SELECT_SUB_MAIN`, so the **sub engine is on top**
(`bw2/lib/nitro/include/nitro/gx.h:460-462`, `bw2/src/gfl/gx_layers.c:118`). GFL BGs 0–3 are main and 4–7 are sub
(`bw2/include/gfl/bg_sys.h:11,67-69`).

| Screen | Layer (GFL id) | Content | Files `a/0/2/6` (ARCID_TITLE 26) | Format | Prio | Source |
|---|---|---|---|---|---|---|
| top | sub BG3 (7) | **logo** "Pokémon BLACK VERSION 2" | 0 NCGR, 1 NSCR, 2 NCLR | 8bpp text BG, 256×256 map; tiles at char base 0x4000, loaded with size 0x8000 | 2 | `title.c:202-205,493-497` |
| top | sub BG2 (6) | ice-crystal strip, scrolls x by `scroll/2` each frame | 3 NSCR (tiles and palette shared with the logo) | 8bpp, 256×192 map | 3 (behind the logo) | `title.c:207-210,498-499,520-528` |
| top | sub BG1 (5) | one text line from system text 373 line 1, **blank**, and hidden every frame | font a/0/2/3, text a/0/0/2 #373 | 4bpp BmpWin | 0 | `title.c:481-528`; `bw2/data/text/system/0373_title.txt` |
| top | sub OBJ | **"PRESS START"**, one actor at (128,96) | 5 NCGR, 6 NCER, 7 NANR, 4 NCLR | 4bpp, 1D 32K mapping | OBJ prio 0 | `title.c:640-659` |
| bottom | main BG0 (3D) | **Black Kyurem scene** | `a/1/5/8` 446–453 | NSBMD/NSBCA/NSBTA + curve | 1 | `title.c:542-580` |
| bottom | main BG3 (3) | "Developed by GAME FREAK inc." | 9 NCGR, 10 NSCR, 8 NCLR | 4bpp text BG, 256×192 | 0 (over the 3D) | `title.c:212-215,484-492` |

- Files 11–14 belong to the boot screens (`bw2/src/ov162/boot_screens.c:101-106`).
- Archive ids → paths come from the arm9 table at `0x02099a20`: id 26 = `a/0/2/6`, 158 = `a/1/5/8`, 2 = `a/0/0/2`,
  23 = `a/0/2/3` **[bytes]**.

**Motion blur:** the main LCD shows **VRAM D** (`GX_DISPMODE_VRAM_D`, `title.c:240`). Each VBlank captures the main
engine's 2D+3D output blended with the previous frame (EVA 12 / EVB 4) back into VRAM D (`title.c:440-459`). Static
2D images are unaffected.

**VRAM** (`title.c:248-261`): main BG 32 KB (F+G), sub BG 128 KB (C), sub OBJ 16 KB (I), **no main OBJ**, textures
256 KB (A+B), texture palettes 64 KB (E), VRAM D for the capture.

### The 2D files (all decoded and rendered this session) [decoded]
| File | Bytes | Decoded | Notes |
|---|---|---|---|
| 0 NCGR (LZ10) | 16321 | 32832 | 8bpp, 32×16 tiles = **512 tiles, the full 0x8000 the loader takes**; logo uses 327, strip 52 (1 shared), 378 distinct |
| 1 NSCR (LZ10) | 939 | 2084 | 256×256 logo map; logo bbox x 27–244, y 32–152 |
| 2 NCLR | 552 | — | one 256-colour palette; colour 0 = black (top screen backdrop); logo uses 126 colours, strip 79 |
| 3 NSCR (LZ10) | 330 | 1572 | 256×192 strip map (ice crystals along the top edge) |
| 4 NCLR | 552 | — | 16×16 OBJ palettes; text is white/greys in palette 0 |
| 5 NCGR (LZ10) | 281 | 688 | 20 4bpp tiles: "PRESS START" in two 8-px rows |
| 6 NCER | 140 | — | 2 cells: **cell 0 empty**, cell 1 = 8 OBJs of text at y +68/+75 (screen y ≈ 164–179) |
| 7 NANR | 112 | — | 1 sequence, forward loop: cell 0 for 32 frames, cell 1 for 64 → the blink |
| 8 NCLR | 552 | — | 16 palettes, only 4 colours used; **colour 0 = white = main backdrop** |
| 9 NCGR (LZ10) | 626 | 1600 | 4bpp, 48 tiles (credit line) |
| 10 NSCR (LZ10) | 295 | 1572 | 256×192, 39 tiles used, palette 0 only |

The code loads files 0, 1, 3, 5, 9 and 10 with `compressed = TRUE`. The loader decompresses through
`sys_uncomp_lz1x` (`bw2/lib/nitro/include/nitro/mi.h:24-25`). Replacements should be written as **LZ10** like the
originals: b2tools has an LZ11 compressor (`sprites.py`) but **no LZ10 compressor** (GBATEK format, small to add).
Whether LZ11 would also load there is **[inferred]** possible but untested.

**Limits for new art** (from the setups, `title.c:202-220,484-499`):
- **Top logo + strip:** at most **512 8bpp tiles together** (sub BG1's characters start at 0xC000 =
  0x4000 + 0x8000) and **one shared 256-colour palette**.
- **Bottom BG3:** at most **512 4bpp tiles** (char base 0x4000, size 0x4000, inside main BG's 32 KB) and 16 palettes
  of 16 colours.
- **Sub OBJ:** 16 KB of VRAM = 512 4bpp tiles.

### The 3D scene (`a/1/5/8`, ARCID_DEMO3D_RESOURCE 158)
`sResources` / `sActors` / `CURVE_FILE` (`title.c:169-200`), with names from apicula `info` **[decoded]**:

| Actor | Model | Animations | What it is |
|---|---|---|---|
| 0 | 447 BMD `title_b_01` (159 KB, 25 bones: pelvis…tail, 9 textures `bq_*` incl. 256×256 4bpp body) | 446 BCA (7781 frames, 25 nodes) | **Black Kyurem** |
| 1 | 449 BMD `title_b_02` (nodes `bk_02`,`a`,`a1`,`a2`; textures `bq_body`,`bq_body2`,`bq_clear`,`bq_rock`) | 448 BCA (4 nodes) | Kyurem's ice/rock pieces |
| 2 | 451 BMD `title_b_03` (spheres/surfaces; `isi3b`,`moya` A5I3 translucent, `w_isi_03`) | 452 BTA (SRT on `moya_1`,`isi3b_1`), 450 BCA (scale) | mist ("moya") and ice-stone effects |
| camera | 453 curve (186752 B) | — | camera path |

- Every model's textures are **embedded** in it: `texResource` = the model's own resource (`title.c:181-185`).
- The scene uses a 60° frustum camera with near 0.1 and far 2048 (`title.c:563-572`), four white directional lights
  (`title.c:228-235`), antialiasing and alpha blending on (`title.c:577-579`).
- The 3D clear colour is black with **alpha 0** (`GFL_G3DSysCreate` with no callback, `bw2/src/gfl/g3d_system.c:178-188`,
  called at `title.c:451`). So where nothing 3D is drawn, main BG3 and the main backdrop (file 8 colour 0) show
  through **[inferred from the code; not seen on screen]**.

**Camera-curve format** (file 453; `GFL_G3DCurveLoadHeader` arm9 `0x02015df8`, `…PreloadFrames` `0x02015f58`,
`…ApplyCamera` `0x020162a4`) **[asm]+[bytes]**:
- **Header, 8 bytes:** `u32 frameCount` (0x1E65 = **7781**), then `u8 hasScale, u8 hasRotation, u8 hasTranslation,
  u8 pad` (`00 01 01 00`).
- **Frames:** for each frame, the present tracks as 3 × **f32**, interleaved; the loader converts them to fx32
  (×4096, rounded). Size check: 8 + 7781 × 24 = 186752.
- **Track order [inferred, but consistent]:** the code checks scale, then rotation, then translation, and the data
  reads that way: frame 0 = (24.98, −40.0, 0.0) then (−15.84, 24.48, 18.87).
- **How it moves the camera:** the rotation is **Euler degrees** (wrapped to 0–360, then `MAT3_RotationEulerZYX`)
  applied to two constant vectors (`data_0208fff8`, `data_02090004`). The translation is the camera position.
- **Frame numbers the code relies on:** 7001, 7300 and 7780 (`title.c:59-61`). A new curve must keep at least 7781
  frames, or those constants must be patched.
- White 2's set is 454–461 (`title_w_01..03`, `wq_*` textures). **Both versions' 3D sets ship in the Black 2 ROM**;
  Black 2's code only loads 446–453 **[C]+[decoded]**.

### Kyurem's cry
`PokeVoice_Play(SPECIES_KYUREM, KYUREM_FORM, 64, …)` (`title.c:308`), with form 2 = Black Kyurem in Black 2
(`title.c:41-46`). In the build: species literal `0x286` at **ov162 offset 0x1B0** (`0x0219d030`), form
`movs r1,#2` (`02 21`) at **offset 0x12C** (`0x0219cfac`) **[asm]+[bytes]**.

## 2. Black 2 vs White 2

| What | Black 2 | White 2 | Where |
|---|---|---|---|
| Logo bitmap and its colours | "BLACK VERSION 2", grey chrome + blue "2" | its own | **each ROM's own `a/0/2/6`** (`TitleBG_Init`/`TitleObj_Init` have no #ifdef, so the difference must be data) **[inferred; no White 2 dump on disk]** |
| 3D models, animations, camera | 446–452, curve 453 | 454–460, curve 461 | `#ifdef BLACK2` in `sResources`/`CURVE_FILE` (`title.c:169-198`). In the build the curve id is computed as `410 + 43` (`adds r4,#43` at offset 0x804) |
| Cry form | 2 (Black Kyurem) | 1 (White Kyurem) | `title.c:41-46` |
| Strip scroll direction | +1 per frame | −1 per frame | at run time: `getGameVersion()` (`title.c:523`), which in Black 2 is `movs r0,#23; bx lr` (arm9 `0x02015878`) **[asm]** |

HoennB2 is built from Black 2 only (`build_rom.py` `ORIGINAL_SHA1`), so only the Black 2 column matters. White 2's
3D files are unused data inside the Black 2 ROM **[inferred: no other reference found]**.

## 3. Kyogre's Black 2 sprite (`a/0/0/4`, ARCID_POKEGRA 4)

Species 382 → files **7640–7659** (20 per species). Checked by rendering file 7640 with palette 7658 **[decoded]**,
which matches `GetPokemonPaletteDataNo` adding 18 (arm9 `0x020337dc`) **[asm]**.

| +k | File | Content |
|---|---|---|
| 0 | 7640 | front still, NCGR LZ11, 96×96 4bpp, **OBJ-ordered** 64×64, 32×64, 64×32, 32×32 [decoded]; figure bbox x 1–95, y 19–76 |
| 2 | 7642 | front MCSS parts texture, NCGR LZ11, 256×128 4bpp bitmap |
| 4–8 | 7644–7648 | NCER, NANR, NMCR, NMAR, MCSS data (the animation) |
| 9–17 | 7649–7657 | the same for the back sprite |
| 18 / 19 | 7658 / 7659 | normal / shiny NCLR (16 colours) |

As a BG picture (unique 8×8 tiles, flips folded) **[decoded]**:
- at 1× it takes **74 tiles** (2.3 KB 4bpp);
- at 2× (pixel-doubled, about 188×114 px) **220 tiles** (7 KB), which still fits main BG3's 512-tile area next to the
  credit line.

Animated display is **MCSS** (arm9 `mcss.c`: `MCSSSys_Create` `0x020199e8` … `bw2/include/system/mcss.h`):
- MCSS draws through the 3D engine and sets its own look-at (`gfxLookAt` in `MCSSSys_Draw`) **[asm]**. It uses
  whatever projection is current **[inferred]**.
- Decompiled users to copy from: the intro adds a Pokémon by species (`IntroMcss_AddPokemon`,
  `bw2/src/ov294/intro_mcss.c:74-87`: `PokeParty_NewTempPkm` → `func_0201bfdc` → `MCSSSys_Add` → `MCSS_SetScale`).
  The evolution and egg screens do the same (`bw2/src/ov284/shinka_demo_view.c:534-596`, `bw2/src/ov307/egg_demo_view.c`).

## 4. The logo: a decision for you

Black 2's logo has a big chrome **B L A C K** and a small chrome **V E R S I O N**, plus the "2" with an ice burst
**[decoded]**. "SAPPHIRE" needs S A P P H I R E:
- In the big style only **A** exists.
- In the small style **S, I, R, E** exist.
- **P and H exist in neither.**

There is no Sapphire logo anywhere in Black 2 that I know of (not searched exhaustively). Using the GBA logo would
break the "no GBA graphics" rule. Choices:

1. **Cut-and-paste from Black 2's letters** (closest to the rules, but it is an *edit*, like the character sprites
   in DECISIONS 2026-10-06):
   - Keep the yellow "Pokémon" wordmark exactly; Sapphire uses the same mark.
   - Build big-style **SAPPHIRE**:
     - A as is;
     - P = B's stem and upper bowl;
     - R = P + K's lower leg;
     - E = L + bars;
     - I = L's stem;
     - H = two stems + a bar;
     - S = C's upper half + a mirrored C's lower half.
   - Keep small "VERSION" as is.
   - Recolour the chrome to sapphire blues through palette file 2.
   - Drop the "2", or keep its burst recoloured as a water splash.
2. **Draw a new Gen 5-style "SAPPHIRE VERSION"** wordmark (allowed only if you agree).
3. **Text only:** "SAPPHIRE VERSION" in Black 2's own font (`a/0/2/3`) under the "Pokémon" wordmark. Fully Black 2
   pieces, but plain.

The art for any of these must fit the budget above: tiles + strip ≤ 512, ≤ 256 colours with the strip.

## 5. Options

### Option A: 2D title, Kyogre still, 3D off (recommended first)
**What you'd see:**
- **Top:** the Sapphire logo on black or deep blue, the crystal strip recoloured to sea blue (or a new strip), and
  "PRESS START" blinking as today.
- **Bottom:** Kyogre's Black 2 front sprite, still, at 1× or pixel-doubled 2×, on a deep-sea backdrop, with
  "Developed by GAME FREAK inc." below.
- A or Start plays **Kyogre's cry** with the white flash.
- No 3D and no 29-second screen swap.

**Data (`a/0/2/6`):**
- files 0/1/2: new logo, with the strip in file 3;
- file 2: palette;
- files 8/9/10: Kyogre's tiles + the credit line, Kyogre in palette slot 1, **file 8 colour 0 = the bottom
  background colour**;
- files 4/5/6/7 unchanged, or recoloured through 4.

**ov162 patches** (bytes checked against the build) **[asm]+[bytes]**:

| Offset | Address | Old → new | Effect |
|---|---|---|---|
| 0x8D0 | `0x0219d750` | `ac f6 04 fa` (`bl GFL_G3DSysDrawObj`) → `c0 46 c0 46` (2× nop) | no 3D actor is drawn; the scene still loads and runs, harmless |
| 0xB4 | `0x0219cf34` | `cc 06 00 00` (1740) → `ff ff ff ff` | the 29 s swap never fires. It would otherwise hide BG3, which now holds Kyogre, and put an empty 3D screen on top |
| 0x1B0 | `0x0219d030` | `86 02 00 00` (646) → `7e 01 00 00` (382) | cry species = Kyogre |
| 0x12C | `0x0219cfac` | `02 21` → `00 21` | cry form 0 |
| optional 0x6A2 | `0x0219d522` | `40 1c` (`adds r0,r0,#1`) → `00 1c` (`adds r0,r0,#0`) | stop the strip scrolling |

**Effort:** small once the logo art exists: an LZ10 writer + an NCGR/NSCR/NCLR packer (sprites.py already parses
these) + a `patches/title.py` in the style of `patches/starters.py`.

**Risk:** low. All formats were decoded here and the patches are NOPs or literals. Unverified: the alpha-0 clear
colour letting the backdrop show **[inferred]**.

**Variant A2, closer to Sapphire's GBA title** (data only):
- Put Kyogre on the **top** screen behind the logo, darkened to a silhouette through its palette, on sub BG2
  instead of the crystal strip (+74 tiles at 1×).
- Or as sub OBJs added to **both** cells 0 and 1 of file 6, so it stays visible while "PRESS START" blinks.
- The bottom screen then needs something else, for example a sea colour or Black 2 water art.

### Option B: Kyogre on a card inside the 3D scene
**What you'd see:** Black 2's cinematic bottom screen kept (camera moves, motion blur, mist), with Kyogre's still
sprite standing on a flat card in place of Kyurem, larger than 2D allows. The 29 s swap still shows it on the top
screen.

**Files (`a/1/5/8`):**
- **447** → one-quad BMD with Kyogre's sprite as an embedded 128×64 4bpp texture. Build it with CTRMapV's
  `NSBMDWriter`: its settings take `includeTextures` (`b2tools/java/ToNsbmd.java:68`), but **embedding has not been
  tried here**.
- **446** → a 1-node BCA (CTRMapV 1.4.1 has `nitrowriter/nsbca/NSBCAWriter`, no driver in b2tools yet).
  Alternatively keep 446 and let node 0 take the pelvis motion: NNS binds joints by index **[inferred]**.
- **449/448** → an empty model or a Black 2 sea plane, because actor 1 wears Kyurem's own body textures.
- **451/452/450** → keep as sea mist, or recolour.
- **453** → a new camera path in the format above: mostly frontal, so the flat card never turns edge-on, and
  ≥ 7781 frames.

**Code:** the same cry patch as A.

**Effort:** medium to high (three new 3D files + a curve writer).

**Risk:** medium. Unverified: textures embedded by the writer, how animations bind to a model with a different
node count, and how the camera looks until tested.

### Option C: animated Kyogre (MCSS), the full version
**What you'd see:** Kyogre moving exactly as in Black 2 battles (its own NANR/NMCR), on the bottom screen with a
backdrop. The top screen is the same as A.

**Code:** `TitleG3D_*` (`0x0219d554`–`0x0219d844`, 752 bytes) is replaced by the intro's pattern:
- create: `MCSSSys_Create(1)`, then the texture/palette offsets (`func_0201aefc`/`func_0201af00`) and
  `func_0201aacc`;
- add Kyogre: `PokeParty_NewTempPkm(382)` → `func_0201bfdc` → `MCSSSys_Add`, then `MCSS_SetScale`;
- each frame: `MCSSSys_Update`/`Draw` before the buffer swap;
- exit: `Remove`/`Free`.

Optionally keep the mist actor.

Two ways to build it:
1. **(a)** Edit `title.c` and build a **non-matching** ov162 with the decomp's own compiler. ov162 is all C, the
   decomp supports size-changing builds (`bw2/docs/configs.md` "Shifting"), and the linker script places ov163/ov294
   `AFTER(... OV162 ...)` (`bw2/build/b2_us/arm9.lcf:134,136`), so ov162 may grow. Needs a modded-build flow
   outside the matching checkout.
2. **(b)** Hand-write Thumb code into the 752 bytes.

**Open questions:**
- the projection MCSS needs (the intro uses an ortho camera, `bw2/src/ov294/intro_g3d.c:65`);
- which texture-VRAM offset is safe next to the G3D texture manager (A+B, 256 KB, `title.c:451`).

**Effort:** high. **Risk:** medium to high.

### Comparison
| | A (2D) | B (3D card) | C (MCSS) |
|---|---|---|---|
| Kyogre | still, 1×/2× | still, any size, moved by the camera | **animated, Black 2's battle animation** |
| Black 2 cinematic camera/blur | no | yes | blur yes, camera optional |
| New code | 4–5 bytes/words | cry only | new functions |
| New tools | LZ10 + BG packer | + textured BMD, BCA, curve writer | + decomp modded build or asm |
| Risk | low | medium | medium–high |

## 6. Build and test consequences
- **Archive sizes:** `a/0/2/6` (26) and, for B, `a/1/5/8` (158) are not in `build_rom.py` `RESERVE`. New file sizes
  change the ROM's file table, so add RESERVE entries and **rebuild the base savestates once** (comment above
  `RESERVE`).
- **Signed overlay:** ov162 is `compressed: true, signed: true`
  (`bw2/extract/b2_us/arm9_overlays/overlays.yaml:1623-1632`), like ov036, which is already patched. The same
  untested DSi-mode caveat applies as in `notes/RESEARCH_ENCOUNTERS.md`.
- **Testing:** the title is only reached from a cold boot (boot screens → cutscene player ×2 → title), not from the
  savestates. A test needs a boot-and-wait (or Start) script in `emu.py`, plus a check after 30 s (A) or of the swap
  (B).
- **Not covered here:** the title music, the boot screens/movies before the title, and the start menu after it
  (`a/0/3/4`).

## 7. Open points
1. Your logo choice (section 4), and whether 2× pixel-doubled Kyogre is acceptable or 1× only.
2. Whether Kyogre goes on the bottom screen (A) or behind the logo on the top screen (A2), or both.
3. Option B/C unknowns (listed in their sections) are only settled by building and booting a test ROM.

## 8. Option C built: the animated figure (title_anim, 2026-10-08)
User: "is it possible to have kyogre and groudon do their idle animation like in battle on the title screen". Built
and tested: the bottom screen plays Kyogre's (Ruby: Groudon's) own Black 2 battle animation, through MCSS, where the
still used to be. Code: `b2tools/patches/title_mcss.c` (C, compiled by `patches/title.py` with clang, every Black 2
function called by address like `patches/roamers.c`); the findings are in `title.py` `ANIMATED_DOC`. Evidence tags as
above: [C] decomp source, [asm] disassembly of the decomp's build (capstone), [test] DeSmuME.

**What Black 2 offers [C]+[asm].** MCSS lives in the main module (`mcss.c`, `include/system/mcss.h`), so any overlay
can call it: `MCSSSys_Create` 0x020199e8, `MCSSSys_Update` 0x02019ae8, `MCSSSys_Draw` 0x02019c0c, `MCSSSys_Add`
0x0201a8a8 (→ `LoadMCSSGraphicsData` 0x0201b2a0), `MCSSSys_Free` 0x02019a88, `MCSS_SetScale` 0x0201ab88,
`SetupPokemonLoaderFSTool` 0x0201c044 (species, form, sex, shiny, egg, info, direction). Callers (relocs.txt): the
summary screen ov207 `p_status` (create 0x021b35be, add 0x021b66e8/0x021b6726 through `func_0201c14c`, update/draw
0x021b3344/0x021b3352), the Pokédex ov298 `zukan_detail` (`func_ov298_021a8df8` create, `func_ov298_021a8e80` add),
ov265 (`func_ov265_0219a06c` create + its own orthographic camera, `func_ov265_02199ea8` update/draw), the intro ov294
(C), evolution ov284, eggs ov307, trades ov194, battle ov168.
- **Heap:** a sprite is a 0x188-byte MCSS plus its files (the 256×128 texture is 16 KB); the title heap is 1,152 KB and
  no longer loads the Kyurem scene.
- **VRAM:** the VBlank task `func_0201b75c` loads the texture with `NNS_G2dLoadImage2DMapping` and the palette with
  `NNS_G2dLoadPalette`, VRAM type 0 = 3D: texture VRAM at char offset + 0x4000 × slot, texture palettes at 0x1000 +
  0x20 × slot (`MCSSSys_Create` sets 0x24000 / 0x1000; `func_0201aefc` / `func_0201af00` change them) and a fade palette
  at 0x1100. The title maps texture A+B and texture palettes E (`sVRAMConfig`); nothing else uses them once the
  models are gone, so the char offset is 0 (as ov207, ov265 and ov298). No OAM: the title has no main OBJ VRAM and MCSS
  does not need any.
- **3D:** the title already runs the 3D engine on main BG0 and swaps its buffers; MCSS draws quads through it. The main
  screen shows VRAM D captured from 2D+3D, so the sprite is in the capture. The 3D clear colour has alpha 0
  (`GFL_G3DSysCreate` default), so the opaque BG3 (backdrop + credit line) shows around the sprite once the 3D layer is
  in front (`GFL_BGSysSet3DBGPriority(0)`; BG3 has priority 0 too and BG0 wins a tie).
- **Placement [asm]+[test]:** with `func_0201aacc` (sys+0x2c bit 0, set by ov265/ov298/the intro) `MCSSSys_Draw`
  projects the sprite's position through the current camera (`func_0201bea4`, view × projection at 0x2143a58 /
  0x2143a14), divides x and y by w and scales them to pixels (× 128, × 96), and keeps the clip z (no divide) as the
  depth in its own identity view, where the cells are drawn at one texel per pixel (scale 16 = 1:1). So the camera is
  orthographic 256 × 192 units (one unit per pixel), and its eye is put beyond the far plane (z 3000, far 1024, as
  ov265 does) so that clip z > 1 lands in front of the near plane: with the eye at 512 (clip z ≈ 0) Kyogre's right fin
  was cut away [test].

**What was built.** `TitleG3D_Init/Draw/Free` (0x0219d554 / 0x0219d70c / 0x0219d7b0) are replaced in place by
`TitleMcss_Init/Draw/Free` (216/56/28 B for Kyogre, 220 B Init for Groudon); `TitleG3D_StepCurve` and
`TitleG3D_SetFrame` are `bx lr` (Start no longer jumps a camera curve: the figure keeps moving through its cry and the
fade). The Kyurem scene, curve and light are never loaded. Bottom BG3 = backdrop + credit line only
(`title_art.bottom_screen(still=False)`). The sprite's origin goes to `title_art.mcss_origin()` = the still's place
minus the still's offset from the MCSS origin, found by matching the still against the MCSS pose at tick 0 (mcss.py):
Kyogre (-56, -95) → origin (136, 135), Groudon (-48, -85) → (128, 125); 99.9% / 100% of the still's pixels match.
Its animation is multi-cell animation 0 (play mode loop: Kyogre 875 ticks, Groudon 371), stepped once per frame by
`MCSSSys_Update`, as in battle. Switches: `HOENN_TITLE_STILL=1` (the old still title), `HOENN_TITLE_TEST_PAUSE=1`
(test: the sprite paused on its first frame).

**ROM layout.** dsd recompresses ov162; the new code compresses a little worse (15228 Sapphire / 15232 Ruby with the
dead bytes kept). `title.py` keeps `FILL` = 347 (Sapphire) / 339 (Ruby) bytes of Black 2's dead code and zeroes the
rest, so ov162 is exactly 15204 B in both versions, v15.1's size (with `hoenn_intro`, the other ov162 patch). Retune
after any ov162 edit: `HOENN_VERSION=… python3 patches/title.py tune RIG_DIR`.

**Tests [test] (DeSmuME, 2026-10-08).** Full story_build.sh ROMs of both versions (work/agents/title_anim/rom*/):
- `HOENN_TITLE_TEST_PAUSE=1` (the sprite held on its first frame) against a `HOENN_TITLE_STILL=1` build: the same
  outline at the same place, 262 (Kyogre) / 212 (Groudon) pixels of inner detail differ (MCSS's first pose vs the
  still: highlight, eye, a claw).
- Cold boot, no save: the title at frame ~1250 with the figure animating (`screenshots/title_anim/<version>_strip.png`,
  `_anim.gif`, `_frames/` = 36 frames 7 apart); Start: white flash, cry, the figure keeps moving through the fade, then
  the start menu (`_start.png`). New Game from that title through the opening to Littleroot and an in-game save, then a
  second cold boot: title → CONTINUE → Littleroot (173,361) (`_newgame_save.png`, `_continue.png`; save_check's
  cycle.py).
- rom_layout_diff.py: Sapphire = Ruby = release v15.1 (FAT, OVT, FNT identical; ov162 15204 B in all three);
  work/emu/base_littleroot.dst (v15.1) loads on both ROMs and warps into the player's house and out.
- Tools: work/agents/title_anim/tools (boot.py, title_proof.py, battle_rate.py, ovsize.py, state_check.py).

## 9. Sapphire's own title scene (title_anim, 2026-10-11)
User: "Kyogre's animation on the title screen looks off" (and Ruby's Groudon). Compared frame by frame with Sapphire's
own title (pokeruby `src/title_screen.c`, `src/scanline_effect.c`, `src/trig.c`, `graphics/title_screen/`) and with
Black 2's (`src/ov162/title.c`). Full findings: `patches/title.py` `SCENE_DOC`.

**What differed.** Sapphire's title shows a large dark Kyogre (Groudon) silhouette over a dark gradient, the sea (lava)
with rising bubbles blended over it (EVA 15, EVB 16), the sea rippling sideways (a 4-pixel sine, 64 lines long,
moving one line per frame) and rising half a pixel per frame, and Kyogre's markings glowing red (Groudon's blue),
0 to 31 and back over 256 frames. Ours (2026-10-08) showed Black 2's small battle sprite idling (MCSS) on a flat pale
backdrop: different art, size, place, background, timing, and no glow, sea, bubbles or ripple.

**Fixed.** The bottom screen is now Sapphire's scene, from Sapphire's/Ruby's own tiles, maps and palettes, 1x, its
240x160 screen at (8, 16) of the bottom screen (the rim the GBA never shows repeats Sapphire's edge tiles), with
Sapphire's blend and its exact motion (`patches/title_scene.c`: main BG1 + BG2 on BG3's characters, an HBlank task as
Black 2's Pokédex uses, `title_art.pack_scene`, new a/0/2/6 files 15/16). Black 2's credit line stays in front in its
own colours. The Kyogre tiles, map, water map and both palettes are byte-identical to the user's Sapphire dump (rev1,
at 0x3931b8). `HOENN_TITLE_MCSS=1` builds the 2026-10-08 title, `HOENN_TITLE_STILL=1` the 2026-10-06 one.

**Tested [test].** DeSmuME, full story builds, cold boot, 600 consecutive frames per version
(`work/agents/title_anim/tools/scene_check.py`, results `work/agents/title_anim/shots/{s3,r3}/check.txt`): every frame
advances the scene by exactly one frame, and over Sapphire's 240x160 area the picture equals Sapphire's own title
rendered straight from pokeruby's files and rules, except 1-5 lines in about 40 % of the frames where DeSmuME ran the
HBlank interrupt late (that line keeps the previous line's offset: 1 pixel). Start (cry, flash, fade), the start menu,
New Game into the intro and the 113 s timeout (the title starts again) work in both versions. ov162 stays 15204
compressed bytes, a/0/2/6 24436. Proof: `screenshots/title_anim/{sapphire,ruby}_scene_sheet.png` (before / after /
Sapphire's own at the same frames), `release/showcase/{sapphire,ruby}/01_title_*_v2.gif` (one whole 512-frame loop).

**Not reproduced (top screen, Black 2's design kept):** Sapphire's logo shine and version-banner slide, its 16/16
PRESS START blink (Black 2's 32 off / 64 on kept), and the scene appearing only after the logo (400 frames in
Sapphire; here it is there from the fade-in). The sea could also continue behind the logo on the top screen: not done
(the top screen's 256 colours are all used by the logo and the strip).

## 10. Emerald's title (emerald_art, 2026-10-12)
First built as a straight port of Emerald's whole title (its logo, shines, banner, PRESS START and copyright on the top
screen; commit 58773f1, b2tools/title_emerald.py), then (user, same day) the top screen was put back to the
Sapphire/Ruby style: Black 2's strip and PRESS START with a Gen 5-style "EMERALD VERSION" logo made as Ruby's was
(`title_art.py` EMERALD_DRAFTS: draft 1 = Sapphire's draft 1 construction in emerald green, 2 = pokeemerald's own
banner doubled, 3 = draft 1 deeper green; new letters M, L, D; EMERALD_STRIP_TINT turns the crystals green;
`HOENN_VERSION=emerald python3 title_art.py drafts | use N`). The bottom screen is Emerald's own scene (title_art.py
"Emerald": Rayquaza + clouds from pokeemerald's files, verified in the user's dump by emerald_src.py; clouds a pixel
every 4 frames, BLDALPHA 6/15, cosine markings), through the Sapphire scene code with three TITLE_EMERALD branches in
patches/title_scene.c (the markings' 64 colours as TitleScene_Marks in TitleG3D_Draw's room). Emerald's title files are
LZ11 (title_art.lz_title; the loader sys_uncomp_lz1x takes both) so a/0/2/6 stays within Black 2's size. Rayquaza's
cry (384). Sapphire/Ruby: title data and code byte-identical to before Emerald (8cb43d4).
