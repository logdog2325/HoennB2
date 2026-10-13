"""Pokémon Sapphire's title screen (notes/RESEARCH_TITLE.md, option A; formats in b2tools/title_art.py).

Top screen: the new "Pokémon Sapphire" logo over Black 2's crystal strip and "PRESS START".
Bottom screen (since 2026-10-11, SCENE_DOC below): Sapphire's own title scene (Ruby: Ruby's), the dark Kyogre (Groudon)
with its glowing markings under the rippling sea (lava) with rising bubbles, from pokeruby's own tiles, maps and
colours, moved frame for frame as pokeruby's src/title_screen.c moves them; Black 2's "Developed by GAME FREAK inc."
line in front. A or Start plays Kyogre's cry. No 3D Kyurem, no 29 s swap, no motion blur. Booting goes from the legal
screens and the Game Freak logo straight to this title: Black 2's opening movie is skipped (user choice 2026-10-06).
Earlier titles, kept as switches: HOENN_TITLE_MCSS=1 (2026-10-08, ANIMATED_DOC: Kyogre's Black 2 battle sprite and
idle animation through MCSS on a pale backdrop), HOENN_TITLE_STILL=1 (2026-10-06: Kyogre's Black 2 front still,
a/0/0/4 7640, palette 7658, drawn into BG3).

Data, a/0/2/6 (ARCID_TITLE), rebuilt from Black 2's own files (read from the decomp's extract, so the patch can run
on any tree) and data/title/:
- files 0/1/2/3 (logo tiles, logo map, the 256 colours, strip map) <- data/title/logo.png + strip.png (indexed PNGs
  sharing one palette; `python3 title_art.py drafts` / `use N` make them)
- files 8/9/10 (bottom palettes, tiles, BG3 map) <- Sapphire's scene tiles + palettes 14/15 and Black 2's credit line
  (title_art.pack_scene), files 15/16 (new) = BG1's and BG2's maps. MCSS/still titles: the backdrop + the credit line
  (+ Kyogre's tiles in the still title), every pixel opaque (title_art.py "packing")
- files 4-7 (PRESS START) and 11-14 (boot screens) unchanged
The archive is padded inside the NARC to Black 2's own size (24436 bytes), so the ROM's file layout does not
change and savestates keep working (a bigger archive is refused: then it needs a RESERVE entry in build_rom.py).
Checked 2026-10-06: with this patch the ROM's file table differs only in ov162's compressed size (4 bytes smaller,
same start, the next file does not move).

Code, arm9_ov162.bin (src/ov162/title.c, base 0x0219ce80; bytes checked against the decomp's build):
- scene title: TitleG3D_Init/Draw/Free replaced by patches/title_scene.c (SCENE_DOC), MCSS title by
  patches/title_mcss.c (ANIMATED_DOC); StepCurve/SetFrame become `bx lr`; the Kyurem scene is never loaded
- still title only: 0x8D0 `bl GFL_G3DSysDrawObj` in TitleG3D_Draw -> 2x nop: no 3D actor is drawn (the scene still
  loads and runs, hidden under the opaque BG3)
- 0xB4 HIDE_LAYERS_FRAMES literal 1740 -> 0xFFFFFFFF: the 29 s swap (3D to the top screen, BG3 hidden) never fires
- 0x1B0 cry species literal 646 (Kyurem) -> 382 (Kyogre); 0x12C `movs r1, #2` (cry form) -> `movs r1, #0`
- the display capture's blend (TitleSys_VBlank: shown = (new * EVA + last * EVB) / 16): EVA/EVB 12/4 at start
  (0x476 `movs r0, #12`, 0x458 `movs r5, #4`) and 8/8 after Start (0x172/0x174 `movs r1, #8; movs r2, #8`) ->
  16/0. With a still picture the blur only showed as rounding: flat colours settled one step dark in some rows and
  exact in others (visible bands on the bottom backdrop in DeSmuME)

Code, arm9.bin (base 0x02004000): the boot sequence is StartMenuEventTick (0x020362ec, not decompiled; read with
armdis.py), a 4-state machine that queues one process per call:
  state 0: ov162 BOOT_SCREENS_PROC_FUNCTIONS (The Pokémon Company/Nintendo logos + copyright, src/ov162/boot_screens.c)
  state 1: ov264 (the cutscene player, cdemo_main.c) with its parameter data_02141808 = {mode 0, 1, 0, 1}: the Game
           Freak logo. The u32 at +4 also lands on the boot screens' parameter (data_0214180c, skipLogos = TRUE)
  state 2: ov264 again with mode 2: Black 2's opening movie
  state 3: ov162 TITLE_PROC_FUNCTIONS, then back to state 0
- 0x02036332 `movs r0, #2` (state 1's next state) -> `movs r0, #3`: the movie is never queued (seen on a cold boot:
  the title at frame ~1250 instead of ~3900)
When the title times out (6780 frames, 113 s, NEXT_NONE) the machine starts over at state 0: the copyright notice only
(skipLogos), the Game Freak logo, the title again, about 1050 frames later; the movie still never plays.
"""
import os, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import narcio, title_art  # noqa: E402
from b2files import arc_path  # noqa: E402

# The bottom screen: 'scene' = Sapphire's own title scene (title_anim, 2026-10-11, SCENE_DOC below); 'mcss' = Kyogre's
# Black 2 battle animation (2026-10-08, ANIMATED_DOC, HOENN_TITLE_MCSS=1); 'still' = the still (HOENN_TITLE_STILL=1).
STYLE = 'still' if os.environ.get('HOENN_TITLE_STILL') else 'mcss' if os.environ.get('HOENN_TITLE_MCSS') else 'scene'
ANIMATED = STYLE != 'still'           # TitleG3D_* replaced by new code

CODE = {
    'arm9_ov162.bin': [(0x8D0, 'acf604fa', 'c046c046'),     # TitleG3D_Draw: bl GFL_G3DSysDrawObj -> nop nop
                       (0xB4, 'cc060000', 'ffffffff'),      # Title_UpdateTimer: HIDE_LAYERS_FRAMES 1740 -> never
                       (0x1B0, '86020000', struct.pack('<I', title_art.TITLE['species']).hex()),   # Title_HandleInput:
                                                            # PokeVoice_Play species 646 -> 382 (Ruby 383; version.py)
                       (0x12C, '0221', '0021'),             # ... form 2 (Black Kyurem) -> 0
                       (0x476, '0c20', '1020'),             # TitleSys_Init: captureEva 12 -> 16
                       (0x458, '0425', '0025'),             # ... captureEvb 4 -> 0 (r5 only feeds that store)
                       (0x172, '0821', '1021'),             # Title_HandleInput: SetCaptureBlend(8, 8) -> (16,
                       (0x174, '0822', '0022')],            # ... 0)
    'arm9.bin': [(0x02036332 - 0x02004000, '0220', '0320')],   # StartMenuEventTick: Game Freak logo -> title
}

def pad_narc(data, size):
    """Grow a NARC's GMIF section (the last one) with zeros to `size` bytes, as build_rom.py's padding does."""
    data = bytearray(data)
    off = struct.unpack_from('<H', data, 0xC)[0]
    for _ in range(2):  # BTAF, BTNF
        off += struct.unpack_from('<I', data, off + 4)[0]
    assert data[off:off + 4] == b'GMIF'
    extra = size - len(data)
    struct.pack_into('<I', data, off + 4, struct.unpack_from('<I', data, off + 4)[0] + extra)
    struct.pack_into('<I', data, 8, size)
    return bytes(data + bytes(extra))

def apply(files):
    art = title_art.DATA                           # data/title, or data/title/ruby (version.py); a version without its
    if not os.path.exists(os.path.join(art, 'logo.png')):          # own logo yet shows Sapphire's
        print(f'title: no {art}/logo.png: Sapphire\'s logo')
        art = os.path.join(title_art.ROOT, 'data', 'title')
    logo, pal, size = title_art.load_indexed(os.path.join(art, 'logo.png'))
    strip, pal2, size2 = title_art.load_indexed(os.path.join(art, 'strip.png'))
    assert size == size2 == (256, 192), (size, size2)
    assert pal == pal2, 'logo.png and strip.png must share one palette'
    top, top_tiles = title_art.pack_top(logo, strip, pal)
    if STYLE == 'scene':
        bottom, bottom_tiles = title_art.pack_scene()
    else:
        bottom, bottom_tiles = title_art.pack_bottom(still=STYLE == 'still')
    entries = list(title_art.title_entries())          # Black 2's own a/0/2/6 (15 files), + 15/16 for the scene
    for k, v in {**top, **bottom}.items():
        entries += [b''] * (k + 1 - len(entries))
        entries[k] = v
    narcio.save(files, title_art.ARC_TITLE, entries)
    path = arc_path(files, title_art.ARC_TITLE)
    orig = os.path.getsize(arc_path(title_art.SRC_FILES, title_art.ARC_TITLE))
    data = open(path, 'rb').read()
    if len(data) > orig:
        raise SystemExit(f'a/0/2/6 is {len(data)} bytes, over Black 2\'s {orig}: give it a RESERVE entry in '
                         f'build_rom.py (and rebuild the base savestates) or simplify the logo')
    open(path, 'wb').write(pad_narc(data, orig))
    return (f'a/0/2/6 ({STYLE} title): logo + strip {top_tiles}/512 tiles, bottom {bottom_tiles}/512 tiles, '
            f'{len(data)} bytes padded to {orig}')

def apply_code(code):
    done = []
    for name, edits in CODE.items():
        path = os.path.join(code, name)
        data = bytearray(open(path, 'rb').read())
        if name == 'arm9_ov162.bin' and ANIMATED:
            edits = [e for e in edits if e[0] != 0x8D0]          # inside TitleG3D_Draw, which the new code replaces
            what = new_code(data)
        for at, old, new in edits:
            o, n = bytes.fromhex(old), bytes.fromhex(new)
            assert data[at:at + len(o)] in (o, n), f'{name} {at:#x}: unexpected {data[at:at + len(o)].hex()}'
            data[at:at + len(o)] = n
        if os.path.islink(path): os.unlink(path)
        open(path, 'wb').write(data)
        done.append(f'{name}: {len(edits)} edits')
    if ANIMATED:
        done.append(what)
    cry = {382: 'Kyogre', 383: 'Groudon', 384: 'Rayquaza'}.get(title_art.TITLE['species'], title_art.TITLE['species'])
    return '; '.join(done) + (' (no 3D Kyurem, no 29 s swap, no motion blur, %s\'s cry, no opening movie)' % cry)

# ---------------------------------------------------------------------------------------------------- animated figure
ANIMATED_DOC = """
Animated figure (title_anim, 2026-10-08; user: "have kyogre and groudon do their idle animation like in battle on the
title screen"). Evidence: decomp symbols and C (external/pokebw2), disassembly of the decomp's build (capstone).

What Black 2 offers. Every animated Pokemon outside battle is drawn by MCSS, the multi-cell sprite system in the main
module (always resident), so any overlay can call it:
  MCSSSys_Create 0x020199e8 (capacity, heap), MCSSSys_Update 0x02019ae8 (steps each sprite's NNS multi-cell animation
  once), MCSSSys_Draw 0x02019c0c (3D quads through the geometry engine), MCSSSys_Add 0x0201a8a8 (x, y, z, load info:
  reads the NCER/NANR/NMCR/NMAR/bin and the NCGR/NCLR of a/0/0/4, LoadMCSSGraphicsData 0x0201b2a0), MCSSSys_Free
  0x02019a88 (removes every sprite), MCSS_SetScale 0x0201ab88, SetupPokemonLoaderFSTool 0x0201c044 (species, form,
  sex, shiny, egg, info, direction -> the a/0/0/4 file numbers).
Users: the summary screen ov207 (p_status; MCSSSys_Create at 0x021b35be, sprites added through func_0201c14c at
0x021b66e8/0x021b6726, update+draw at 0x021b3344/0x021b3352), the Pokedex ov298 (zukan_detail; func_ov298_021a8df8
create, func_ov298_021a8e80 add via SetupPokemonLoaderFSTool), ov265 (func_ov265_0219a06c create + an orthographic
camera, func_ov265_0219a0f0 add, func_ov265_02199ea8 update+draw), the intro ov294 (src/ov294/intro_mcss.c, in C),
evolution ov284, egg hatching ov307, trades ov194, battle ov168.
What MCSS needs, and what the title has (src/ov162/title.c):
- heap: one sprite is a 0x188-byte MCSS plus its files (the 256x128 4bpp texture is 16 KB); the title's own heap is
  1,152 KB (HEAPID_TITLE 0x120000) and the Kyurem scene (models, animations, a 186 KB camera curve) is no longer loaded.
- VRAM: MCSS writes the texture to texture VRAM at char offset + 0x4000 * slot and the palette to texture-palette VRAM
  at 0x1000 + 0x20 * slot (VBlank task func_0201b75c: NNS_G2dLoadImage2DMapping / NNS_G2dLoadPalette with VRAM type
  0 = 3D), plus a fade palette at 0x1100 (MCSSSys_Create). The title maps texture VRAM A+B (256 KB) and texture
  palettes E (sVRAMConfig); with the Kyurem models gone nothing else uses them, so the char offset is 0 (as ov207, ov265
  and ov298 use).
- 3D: the title already runs the 3D engine on main BG0 (GFL_G3DSysCreate in TitleSys_Init, sLCDConfig GX_BG0_AS_3D)
  and swaps its buffers in TitleG3D_Draw. MCSS uses no OAM (the title has no main OBJ VRAM, and does not need any).
- display: the main screen shows VRAM D, captured from 2D+3D every VBlank (TitleSys_VBlank); the 3D layer is in the
  capture. The 3D clear colour has alpha 0 (GFL_G3DSysCreate's default), so BG3 (the backdrop + credit line, opaque)
  shows wherever the sprite is not; the 3D layer goes in front (GFL_BGSysSet3DBGPriority(0), BG3 has priority 0 too).
- placement: with func_0201aacc (the "2D" flag, sys+0x2c bit 0) MCSSSys_Draw projects the sprite's position through
  the current camera to a screen point (x_ndc * 128, y_ndc * 96) and draws the cells there at one texel per pixel times
  scale / 16. The camera here is orthographic, 256 x 192 units, so the position is in pixels from the screen centre.
  The projected depth (clip z, not divided) becomes the sprite's depth in MCSS's own view, so the eye sits beyond the
  far plane (EYE_Z below), as ov265's camera does.
- speed: MCSSSys_Update steps the animation one tick per call; the title calls it once per frame. Battle does the same
  (DeSmuME, check_ruby's battle state: Zubat's 3-tick frames change every 3 frames, Swampert's 7-tick ones every 7);
  Kyogre's 7-tick frames change every 7 frames on the title.
Code: b2tools/patches/title_mcss.c (compiled with clang like patches/roamers.c, every call by address) replaces
TitleG3D_Init/Draw/Free in place; TitleG3D_StepCurve and TitleG3D_SetFrame become `bx lr` (A/Start no longer jumps a
camera curve: the figure keeps moving while its cry plays and the screen fades). Bottom BG3 loses the still
(title_art.bottom_screen(still=False)); the sprite's first frame is the still's pose, placed over it
(title_art.mcss_origin()).
"""

# ---------------------------------------------------------------------------------------------------- Sapphire's scene
SCENE_DOC = """
Sapphire's own title scene (title_anim, 2026-10-11; user: "Kyogre's animation on the title screen looks off", lead:
compare it frame by frame with Sapphire's own title and fix what differs, Sapphire's/Ruby's own art only). Evidence:
pokeruby src/title_screen.c, src/scanline_effect.c, src/trig.c, graphics/title_screen/ [C]; Black 2's title
src/ov162/title.c and arm9 disassembly [asm]; DeSmuME runs of both ROMs [test].

What Sapphire does (phase 3 of its title, Task_TitleScreenPhase3, after the logo shine and the version banner):
- BG0 (priority 3): the dark legendary over a dark gradient, kyogre.png tiles + kyogre_map.bin (32x20), palettes 14/15
  = kyogre_dark/kyogre_glow (Ruby: groudon.png, groudon_map.bin, groudon_dark/glow). Static.
- BG1 (priority 2): the sea with bubbles, water_map.bin 32x32 on the same tiles, palette 15 (Ruby: lava_map.bin).
  x offset per line = ScanlineEffect_InitWave(0, 160, 4, 4, 0, BG1HOFS): gSineTable[4 j] * 4 / 256, a 4-pixel sine,
  64 lines long, one line further each frame (HBlank DMA); y offset gBattle_BG1_Y = +1 every second frame (the
  bubbles rise half a pixel per frame).
- blend BLDCNT 0x2142, BLDALPHA 0x1F0F: BG1 is target 1, BG0 + backdrop target 2, EVA 15, EVB 31 (= 16): the sea is
  added over the dark Kyogre (min(31, sea * 15/16 + kyogre)).
- the markings (palette 14 colour 15) every 4th frame: red 0..31 over 128 frames, back to 0 over the next 128
  (UpdateLegendaryMarkingColor; Ruby: blue).
- BG2 (priority 1): the GBA logo; OBJs: the version banner, PRESS START (16 frames on, 16 off), the copyright line.
What Black 2's own title does (src/ov162/title.c): a 3D Black Kyurem moved by a 7781-frame camera curve, drawn
through a display capture with motion blur on the bottom screen; the top screen's crystal strip scrolls one pixel
every 2 frames and PRESS START blinks (32 frames off, 64 on). Since 2026-10-06 we keep Black 2's top screen (our logo,
the strip, PRESS START) and the cry/flash/fade on Start; the bottom screen was a still (10-06) and Black 2's MCSS
battle sprite of Kyogre idling on a pale backdrop (10-08), neither of which is what Sapphire shows: no dark
silhouette, no sea, no bubbles, no ripple, no glowing markings, a different background, a small sprite in the middle.

What is built (title_scene.c, title_art.pack_scene): the bottom screen shows Sapphire's scene 1x, Sapphire's 240x160
screen at (8, 16) of the DS's 256x192 (title_art.SCENE_AT; the extra rim repeats Sapphire's own edge tiles), on main
BG1 (the legendary, priority 2) and BG2 (the sea, priority 1), both on BG3's characters (char base 0x4000; 137 tiles
Sapphire, 192 Ruby, with Black 2's credit line), screens at 0x1000 and 0x1800 (BG3's is at 0x0800); the same blend
registers; Black 2's credit line on BG3 in front in Black 2's own colours. The motion runs in an HBlank task
(GFL_HBlankTCBAdd 0x02005680, the mechanism Black 2's Pokedex ov299 uses for its per-line blend), so it is tied to the
display like Sapphire's: frame n of its counter shows what Sapphire shows after its phase-3 frame n
(SCENE_WAVE0: Sapphire's wave starts with the logo, 402 frames before phase 3). The 3D layer stays on (empty, behind).
TitleG3D_Init/Draw/Free are replaced (Init 176 B + the HBlank function 144 B in Init's room, Draw 12 B, Free 40 B: it
removes the task with interrupts off and clears BLDCNT and BG2's offsets for the next screen).
Tested [test] (2026-10-11, full story_build ROMs, cold boot): 600 consecutive frames per version, every frame's bottom
screen is the reference for consecutive n (work/agents/title_anim/tools/scene_check.py), and over Sapphire's 240x160
area it equals Sapphire's own scene rendered straight from pokeruby's files and title_screen.c's rules
(scene_lib.GBA), except one to five lines in about 40 % of the frames where DeSmuME ran the HBlank interrupt late and
that line kept the previous line's x offset (1 pixel; Sapphire's HBlank DMA cannot be late; an interrupt handler can).
The frame counter changes on the first VBlank line it sees, so a late interrupt never skips or repeats a frame.
Start (cry, flash, fade), the start menu, New Game into Birch's intro, and the 113 s timeout (the title starts over and
its task is added again) work in both versions. ov162 stays 15204 compressed bytes (FILL['scene']) and a/0/2/6 24436.
Not reproduced: Sapphire's logo shine and version-banner slide (our logo is new art on the top screen); Sapphire's
16/16 PRESS START blink (Black 2's 32/64 kept on the top screen); the scene only appearing after the logo (400 frames
in Sapphire: here it is there from the fade-in).
"""

LLVM = '/opt/homebrew/opt/llvm/bin'
OV162 = 0x0219ce80
# TitleG3D_* in ov162 (config/b2_us/arm9/overlays/ov162/symbols.txt): entry address, room up to the next function
SLOTS = {'mcss': {'TitleMcss_Init': (0x0219d554, 0x1a8),      # TitleG3D_Init
                  'TitleMcss_Draw': (0x0219d70c, 0xa4),       # TitleG3D_Draw
                  'TitleMcss_Free': (0x0219d7b0, 0x28)},      # TitleG3D_Free (+2 bytes of alignment)
         'scene': {'TitleScene_Init': (0x0219d554, 0xc0),     # TitleG3D_Init's first 0xc0 bytes
                   'TitleScene_HBlank': (0x0219d614, 0xe8),   # ... the rest of it (address known before compiling)
                   'TitleScene_Draw': (0x0219d70c, 0xa4),
                   'TitleScene_Free': (0x0219d7b0, 0x28)}}
SOURCE = {'mcss': 'title_mcss.c', 'scene': 'title_scene.c'}
STUBS = {0x0219d6fc: 0x10,                           # TitleG3D_StepCurve -> bx lr
         0x0219d7d8: 0x6c}                           # TitleG3D_SetFrame -> bx lr
REGION = (0x0219d554, 0x0219d844)                    # TitleG3D_Init .. TitleObj_Init
# Emerald (title_scene.c TITLE_EMERALD): the Sapphire/Ruby top screen and Emerald's own scene on the bottom, whose
# markings need TitleScene_Marks, 128 bytes of data (64 colours), placed in TitleG3D_Draw's room after TitleScene_Draw
# (12 B): Draw keeps 0x10 of it, the table the rest.
EMERALD_MARKS = 0x0219d71c

def _emerald(style=None):
    return (style or STYLE) == 'scene' and title_art.EMERALD_SCENE

def slots(style=None):
    """SLOTS of a style, with Emerald's TitleScene_Marks when the scene is Emerald's."""
    out = dict(SLOTS[style or STYLE])
    if _emerald(style):
        at, room = out['TitleScene_Draw']
        out['TitleScene_Draw'] = (at, EMERALD_MARKS - at)
        out['TitleScene_Marks'] = (EMERALD_MARKS, at + room - EMERALD_MARKS)
    return out

def _elf_sections(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF' and d[4] == 1 and d[5] == 1
    shoff, = struct.unpack_from('<I', d, 0x20)
    shentsize, shnum, shstrndx = struct.unpack_from('<HHH', d, 0x2E)
    secs = [struct.unpack_from('<10I', d, shoff + i * shentsize) for i in range(shnum)]
    stro = secs[shstrndx][4]
    name = lambda s: d[stro + s[0]:d.index(b'\0', stro + s[0])].decode()
    out = {name(s): d[s[4]:s[4] + s[5]] for s in secs if s[1] == 1}          # PROGBITS
    rels = [name(secs[s[7]]) for s in secs if s[1] == 9]                      # SHT_REL: for which section
    return out, rels

# The camera's eye sits beyond its far plane (3000 vs 1024), as ov265 sets its own MCSS camera: in "2D" mode
# MCSSSys_Draw uses the projected depth (clip z, without the divide) as the sprite's depth in its own identity view, so
# the sprite must project to clip z > 1 to land in front of the near plane (z = 1). Tested 2026-10-08: with the eye at
# 512 (inside near..far, clip z about 0) parts of the figure were cut away (Kyogre's right fin), at 3000 it is whole.
EYE_Z = 3000 * 4096

def compile_c(style, defines):
    """title_<style>.c -> {function: code bytes}; every call goes by address, so the code has no relocations."""
    with tempfile.TemporaryDirectory() as tmp:
        obj = os.path.join(tmp, 'title.o')
        subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os',
                        '-ffreestanding', '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables',
                        '-fno-asynchronous-unwind-tables', '-fno-exceptions', '-fno-common', '-mno-unaligned-access',
                        '-ffunction-sections', '-Wall', '-Werror', *(f'-D{k}={v}' for k, v in defines.items()),
                        '-c', os.path.join(HERE, SOURCE[style]), '-o', obj], check=True)
        secs, rels = _elf_sections(obj)
    assert not [r for r in rels if r.startswith('.text')], f'title_mcss.c: relocations in {rels}'
    assert not secs.get('.text') and not any(k.startswith(('.data', '.rodata', '.bss')) for k in secs), sorted(secs)
    return {k[len('.text.'):]: v for k, v in secs.items() if k.startswith('.text.')}

def compile_mcss(species, x, y):
    return compile_c('mcss', dict(TITLE_EYE_Z=EYE_Z, TITLE_SPECIES=species, TITLE_X=x, TITLE_Y=y,
                                  **({'TITLE_TEST_PAUSE': 1} if os.environ.get('HOENN_TITLE_TEST_PAUSE') else {})))

SETUP_MAIN3 = 0x021a1510        # ov162 sBGSetupMain3 (BG3's BGSetup: text, 16 colours, screen 0x0800, chars 0x4000)

def compile_scene():
    """title_scene.c with this version's values (SCENE_DOC; Emerald: title_scene.c TITLE_EMERALD)."""
    defines = dict(TITLE_HBLANK=slots('scene')['TitleScene_HBlank'][0], TITLE_SETUP=SETUP_MAIN3,
                   TITLE_FILE_MON=title_art.SCENE_FILES[0],
                   TITLE_MARK_SHIFT=10 if title_art.version.is_ruby() else 0,
                   TITLE_WAVE0=(title_art.SCENE_WAVE0 - title_art.SCENE_AT[1]) % 64)
    if _emerald('scene'):
        marks = title_art.emerald_mark_colours()
        defines.update(TITLE_EMERALD=1, TITLE_MARKS=EMERALD_MARKS, TITLE_MARK_DATA=','.join(f'{c:#06x}' for c in marks))
    funcs = compile_c('scene', defines)
    if _emerald('scene'):
        assert funcs['TitleScene_Marks'] == struct.pack('<64H', *marks), 'TitleScene_Marks: not the 64 colours'
    return funcs

def compile_style(style):
    if style == 'scene':
        return compile_scene()
    ox, oy = title_art.mcss_origin()                      # screen pixel of the sprite's origin
    return compile_mcss(title_art.TITLE['species'], (ox - 128) * 4096, (96 - oy) * 4096)

# ov162's compressed size must not change: Sapphire's and Ruby's must be equal (one FAT for both, notes/RUBY.md "WP0
# results"), and equal to v15.1's 15204 bytes (FAT 0x178400..0x17bf64), so the ROM's file table stays the one the
# base savestates were made with. dsd compresses the overlay (BLZ) when it builds the ROM; the new code compresses a
# little worse than Black 2's (Sapphire 15228, Ruby 15232 with the dead bytes kept). So the dead bytes after the new
# functions are zeroed except the first FILL[version] of them, which keep Black 2's old code: tuned with dsd itself by
# `python3 patches/title.py tune` (rebuilds a rig ROM with `hoenn_intro title`, the two patches that edit ov162, and
# searches FILL). Rerun it after changing title_mcss.c or any ov162 edit, then check with rom_layout_diff.py.
OV162_TARGET = 15204
FILL = {'mcss': {'sapphire': 347, 'ruby': 339,       # tuned 2026-10-08 (title_anim) for hoenn_intro + title
                 'emerald': 332},                     # tuned 2026-10-12 (emerald_wp0: Rayquaza's cry, Sapphire's scene)
        'scene': {'sapphire': 262, 'ruby': 258,       # tuned 2026-10-11 (title_anim)
                  'emerald': 146}}                    # tuned 2026-10-12 (emerald_art: Sapphire/Ruby top, Emerald's scene)

def dead_ranges(funcs, style=None):
    """The bytes of REGION no new code uses, in the order FILL keeps them: the stubs' rooms, then each function's."""
    out = [(at + 2, at + room) for at, room in STUBS.items()]
    out += [(at + len(funcs[fn]), at + room) for fn, (at, room) in slots(style).items()]
    return [(x - OV162, y - OV162) for x, y in out]

def new_code(data, fill=None, style=None):
    """Writes the compiled title_<style>.c over TitleG3D_* in the decompressed ov162 `data` (bytearray)."""
    style = style or STYLE
    src = open(os.path.join(title_art.ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build', 'arm9_ov162.bin'), 'rb').read()
    a, b = REGION[0] - OV162, REGION[1] - OV162
    funcs = compile_style(style)
    places = slots(style)
    new = bytearray(src)
    for fn, (at, room) in places.items():
        code = funcs[fn]
        assert len(code) <= room, f'{fn}: {len(code)} bytes, room for {room}'
        new[at - OV162:at - OV162 + len(code)] = code
    for at in STUBS:
        new[at - OV162:at - OV162 + 2] = bytes.fromhex('7047')       # bx lr
    if fill is None:
        fill = FILL[style][title_art.version.VERSION]
    keep = fill if fill is not None else 1 << 30
    for x, y in dead_ranges(funcs, style):                 # dead bytes: Black 2's old code for the first `fill`, then 0
        n = max(0, min(keep, y - x)); keep -= n
        new[x + n:y] = bytes(y - x - n)
    assert data[a:b] == src[a:b] or data[a:b] == new[a:b], 'ov162 TitleG3D_*: unexpected bytes'
    data[a:b] = new[a:b]
    legendary = title_art.version.TABLE['legendary'].capitalize()
    what = (f'{title_art.version.NAME}\'s title scene ({title_art.SCENE_MON}, {title_art.SCENE_SEA})' if style == 'scene' else
            f'animated {legendary} (MCSS, species {title_art.TITLE["species"]}, origin at {title_art.mcss_origin()})')
    return (f'{what}; ' + ', '.join(f'{fn} {len(funcs[fn])}/{room} B' for fn, (_, room) in places.items())
            + f'; {fill} dead bytes kept: ov162 tuned to {OV162_TARGET} compressed bytes with hoenn_intro)')

mcss_code = new_code      # the 2026-10-08 name

def tune(rig):
    """FILL for this HOENN_VERSION: the smallest number of kept dead bytes with which dsd compresses ov162 to
    OV162_TARGET bytes. `rig`: a scratch folder (an APFS-cloned file tree and one 512 MB ROM)."""
    import importlib.util, shutil
    env = dict(os.environ, HOENN_BUILD_DIR=rig)
    b2 = os.path.dirname(HERE)
    subprocess.run([sys.executable, 'build_rom.py', '--clean', '--no-pad', 'hoenn_intro'], cwd=b2, env=env, check=True,
                   capture_output=True)
    base = bytearray(open(os.path.join(rig, 'code', 'arm9_ov162.bin'), 'rb').read())
    for at, old, new in CODE['arm9_ov162.bin']:
        if at != 0x8D0:
            base[at:at + len(old) // 2] = bytes.fromhex(new)
    dsd = os.path.join(title_art.ROOT, 'external', 'pokebw2', 'tools', 'dsd')
    sizes = {}
    def size(fill):
        if fill not in sizes:
            d = bytearray(base); new_code(d, fill)
            path = os.path.join(rig, 'code', 'arm9_ov162.bin')
            if os.path.islink(path): os.unlink(path)
            open(path, 'wb').write(d)
            rom = os.path.join(rig, 'tune.nds')
            subprocess.run([dsd, 'rom', 'build', '--config', os.path.join(rig, 'rom_config.yaml'), '--rom', rom],
                           check=True, capture_output=True)
            h = open(rom, 'rb').read(0x60)
            oo, on = struct.unpack_from('<II', h, 0x50)
            with open(rom, 'rb') as f:
                f.seek(oo); ovt = f.read(on)
            sizes[fill] = next(e[7] & 0xFFFFFF for e in (struct.unpack_from('<8I', ovt, 32 * k) for k in range(on // 32))
                               if e[0] == 162)
            print(f'  fill {fill}: ov162 {sizes[fill]} B', flush=True)
        return sizes[fill]
    funcs = compile_style(STYLE)
    top = sum(y - x for x, y in dead_ranges(funcs))
    lo, hi = 0, top
    if not size(lo) <= OV162_TARGET <= size(hi):
        raise SystemExit(f'ov162 is {size(lo)}..{size(hi)} B with 0..{top} dead bytes kept: {OV162_TARGET} out of reach')
    while hi - lo > 1:                                     # the size grows with the bytes kept (checked below)
        mid = (lo + hi) // 2
        if size(mid) < OV162_TARGET: lo = mid
        else: hi = mid
    for f in range(max(0, hi - 8), hi + 9):                # the smallest exact hit near the boundary
        if size(f) == OV162_TARGET:
            return f
    raise SystemExit(f'no fill gives exactly {OV162_TARGET} B near {hi}: {sorted(sizes.items())}')

if __name__ == '__main__':          # HOENN_VERSION=sapphire|ruby [HOENN_TITLE_MCSS=1] python3 patches/title.py tune RIG_DIR
    if sys.argv[1:2] == ['tune']:
        print(f'{title_art.version.VERSION} ({STYLE}): FILL = {tune(os.path.abspath(sys.argv[2]))}')
