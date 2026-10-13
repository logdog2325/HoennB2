"""Emerald's Rayquaza cutscene (emerald_art, 2026-10-12; notes/EMERALD_STORY.md section 8). HOENN_VERSION=emerald
only: Sapphire and Ruby builds return before touching anything ("nothing (Emerald only)"). In the patch lists after the
Frontier patches (it uses frontier_factory_dome's arc 211 and the Frontier code area).

pokeemerald's src/rayquaza_scene.c (the five scenes Script_DoRayquazaScene plays: the two legends' fight, the shorter
fight of the first arrival, Rayquaza taking flight, coming down through the clouds, charging, chasing them away) runs
as written, with pokeemerald's own engine files (sprite.c, task.c, bg.c, palette.c, dma3_manager.c, trig.c), compiled
for the DS by arm-none-eabi-gcc (pokeemerald's own "modern" compiler) and linked into one file, with
b2tools/patches/emerald_rayquaza_scene.c as the GBA's side on the DS (how: that file's comment). Its graphics are
Emerald's, from the user's dump: every one of the 51 files of pokeemerald's src/data/graphics/rayquaza_scene.h is made
as pokeemerald's build makes it (emerald_src's PNG -> 4bpp/8bpp, palettes, -num_tiles; the 12 extra bytes of the tail
file), found in the dump as an LZ77 stream that decompresses to exactly those bytes, and the dump's own compressed bytes
go into the file (nothing redrawn, nothing recompressed).

apply(files):  the scene's file appended to arc 211 (found again by its 'EMRQ' header), and emerald_rayquaza_stub.c
               (~150 B) linked into the Frontier code area (frontier_area.add) with the file's number.
apply_code:    frontier_area.install; ov012 EVCMD_TABLE[494] (Black 2's TrainerCardCmd_01EE, func_ov012_0216465c,
               unused by every Black 2 and Hoenn script; args: one `any`, as field_commands.json says) -> RQ_Cmd.
The script side: src/include/em_rayquaza_scene.inc (`em_rayquaza_scene anim`: FieldClose, the command, FieldOpen).

Sounds (Black 2's own, the closest found; [guess] = picked by name/situation, to audition):
  SE_DOWNPOUR       SEQ_SE_FLD_84   Black 2's rain sound (its rain weathers, ov075/ov077, start it as their loop)
  SE_DOWNPOUR_STOP  stops it        (Emerald's SE_DOWNPOUR_STOP ends the downpour loop)
  SE_THUNDER        SEQ_SE_FLD_32   Black 2's thunderstorm (ov076) plays it after its lightning flash
  SE_M_WHIRLPOOL    SEQ_SE_W250_UZUSHIO  Whirlpool's own sound in Black 2
  SE_INTRO_BLAST    SEQ_SE_W307_EXP [guess] Blast Burn's blast
  SE_MUGSHOT        SEQ_SE_TOUJOU_LARGE [guess] (Rayquaza stopping in the air)
  SE_SLIDING_DOOR   SEQ_SE_W556_KAZE [guess] (the rings pushing the two away)
  cry               Rayquaza's Black 2 cry (PokeVoice_Play 384)
  MUS_RAYQUAZA_APPEARS  data/emerald/hoenn_music.json's slot (mus_rayquaza_appears), only with the Hoenn music answer
                    (as h_playbgm_hoenn; with the Unova answer the scene leaves the music alone)."""
import os, re, sys, struct, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import version  # noqa: E402

PEM = os.path.join(ROOT, 'external', 'pokeemerald')
ARC, MAGIC = 211, 0x51524D45                       # 'EMRQ'
OV012, EVCMD_TABLE, COMMAND, CMD_OLD = 0x021503C0, 0x0216B538, 494, 0x0216465D
GCC = '/opt/homebrew/bin/arm-none-eabi-gcc'
OBJCOPY = '/opt/homebrew/bin/arm-none-eabi-objcopy'
NM = '/opt/homebrew/bin/arm-none-eabi-nm'
CFLAGS = ['-mthumb', '-march=armv5te', '-mtune=arm946e-s', '-O2', '-std=gnu17', '-DMODERN=1', '-fno-toplevel-reorder',
          '-fno-common', '-fno-builtin', '-ffreestanding', '-fno-pic', '-fno-asynchronous-unwind-tables',
          '-Wno-pointer-to-int-cast', '-Wno-attributes', '-Wno-builtin-declaration-mismatch']
ENGINE = ['src/rayquaza_scene.c', 'src/sprite.c', 'src/task.c', 'src/bg.c', 'src/palette.c', 'src/dma3_manager.c',
          'src/trig.c']
SOUNDS = {'RAY_SE_DOWNPOUR': 'SEQ_SE_FLD_84', 'RAY_SE_THUNDER': 'SEQ_SE_FLD_32', 'RAY_SE_M_WHIRLPOOL': 'SEQ_SE_W250_UZUSHIO',
          'RAY_SE_INTRO_BLAST': 'SEQ_SE_W307_EXP', 'RAY_SE_MUGSHOT': 'SEQ_SE_TOUJOU_LARGE',
          'RAY_SE_SLIDING_DOOR': 'SEQ_SE_W556_KAZE'}
STATE = {}

# ---------------------------------------------------------------------------------------------------- the graphics

def _plte(path):
    d = open(path, 'rb').read(); i = d.index(b'PLTE'); n = struct.unpack('>I', d[i - 4:i])[0]
    p = d[i + 4:i + 4 + n]
    return b''.join(struct.pack('<H', (p[k] // 8) | (p[k + 1] // 8) << 5 | (p[k + 2] // 8) << 10) for k in range(0, n, 3))

def _lz_end(d, pos):
    size = d[pos + 1] | d[pos + 2] << 8 | d[pos + 3] << 16
    p, n = pos + 4, 0
    while n < size:
        f = d[p]; p += 1
        for b in range(8):
            if n >= size: break
            if f & (0x80 >> b): x = d[p] << 8 | d[p + 1]; p += 2; n += (x >> 12) + 3
            else: p += 1; n += 1
    return p

def graphics():
    """[(symbol, the dump's compressed bytes, dump address)] for pokeemerald's rayquaza_scene.h, each checked."""
    import emerald_src as E
    src = open(os.path.join(PEM, 'src', 'data', 'graphics', 'rayquaza_scene.h')).read()
    items = re.findall(r'const u32 (\w+)\[\]\s*=\s*INCGFX_U32\("([^"]+)",\s*"([^"]+)"(?:,\s*"([^"]+)")?\)', src)
    assert len(items) == 51, len(items)
    d, out, after = E.rom(), [], 0
    for sym, path, ext, opt in items:
        if ext in ('.4bpp.lz', '.8bpp.lz'):
            bpp = 4 if ext.startswith('.4') else 8
            raw = E.png_4bpp(path, bpp=bpp)
            m = re.search(r'-num_tiles (\d+)', opt or '')
            if m: raw = raw[:int(m.group(1)) * 8 * bpp]
        elif ext == '.gbapal.lz':
            raw = E.gbapal(path) if path.endswith('.pal') else _plte(os.path.join(PEM, path))
        elif ext == '.lz' and path.endswith('_fix.4bpp'):          # pokeemerald's make rule: the .4bpp + 12 bytes
            raw = E.png_4bpp(path.replace('_fix.4bpp', '.png')) + bytes(12)
        elif ext == '.lz':
            raw = open(os.path.join(PEM, path), 'rb').read()
        else:
            raise SystemExit(f'{sym}: {ext}?')
        hits = [h - 0x08000000 for h in E.find_lz(raw)]
        assert hits, f'{sym}: {path} not found in the dump'
        a = min((h for h in hits if h >= after), default=hits[0])   # the copy in rayquaza_scene.h's order
        e = _lz_end(d, a)
        after = e
        out.append((sym, d[a:e], 0x08000000 + a))
    return out

def _gfx_c(path):
    import math
    lines = ['/* generated by b2tools/patches/emerald_rayquaza_scene.py: Emerald\'s own compressed graphics from the',
             ' * user\'s dump (roms/emerald_original.gba), each checked against pokeemerald\'s source files */',
             'typedef unsigned int u32; typedef short s16;']
    for sym, data, addr in graphics():
        data += bytes(-len(data) % 4)
        words = struct.unpack(f'<{len(data) // 4}I', data)
        lines.append(f'const u32 {sym}[] = {{ /* dump {addr:#x}, {len(data)} B */')
        lines += ['    ' + ', '.join(f'0x{w:08x}' for w in words[i:i + 8]) + ',' for i in range(0, len(words), 8)]
        lines.append('};')
    # the GBA BIOS's sine table for BgAffineSet / ObjAffineSet (theta >> 8, 1.14 fixed point); the scene's angles are 0
    sine = [round(math.sin(2 * math.pi * i / 256) * 0x4000) for i in range(256)]
    lines.append('const s16 gRayBiosSine[256] = {' + ', '.join(map(str, sine)) + '};')
    open(path, 'w').write('\n'.join(lines) + '\n')

# ---------------------------------------------------------------------------------------------------- the build

def _shadow(inc):
    """gba/macro.h and gba/defines.h as pokeemerald's, with the DMA macros done by the CPU (GbaDmaSet / GbaDmaStop) and
    the OBJ VRAM / OAM where the DS has them (OAM: the RAM copy emerald_rayquaza_scene.c moves into the real OAM)."""
    os.makedirs(os.path.join(inc, 'gba'), exist_ok=True)
    m = open(os.path.join(PEM, 'include', 'gba', 'macro.h')).read()
    m, n1 = re.subn(r'#define DmaSetUnchecked\(dmaNum, src, dest, control\) \\\n(?:.*\\\n)*?\}\n',
                    '#define DmaSetUnchecked(dmaNum, src, dest, control) '
                    'GbaDmaSet(dmaNum, (const void *)(src), (void *)(dest), (u32)(control))\n', m)
    m, n2 = re.subn(r'#define DmaStop\(dmaNum\) +\\\n(?:.*\\\n)*?\}\n', '#define DmaStop(dmaNum) GbaDmaStop(dmaNum)\n', m)
    assert n1 == 1 and n2 == 1, (n1, n2)
    m = m.replace('#define GUARD_GBA_MACRO_H\n', '#define GUARD_GBA_MACRO_H\nvoid GbaDmaSet(u32, const void *, void *, u32);'
                  '\nvoid GbaDmaStop(u32);\n', 1)
    open(os.path.join(inc, 'gba', 'macro.h'), 'w').write(m)
    dfn = open(os.path.join(PEM, 'include', 'gba', 'defines.h')).read()
    for old, new in [('#define OBJ_VRAM0      (VRAM + 0x10000)', '#define OBJ_VRAM0      0x6400000'),
                     ('#define OBJ_VRAM1      (VRAM + 0x14000)', '#define OBJ_VRAM1      0x6404000'),
                     ('#define OAM      0x7000000', 'extern unsigned char gRayOam[];\n#define OAM      ((unsigned int)gRayOam)')]:
        assert old in dfn, old
        dfn = dfn.replace(old, new)
    open(os.path.join(inc, 'gba', 'defines.h'), 'w').write(dfn)
    # generated by pokeemerald's build from its map data (not built here); no file of the scene uses a map
    open(os.path.join(inc, 'map_groups.h'), 'w').write('/* (the scene uses no maps) */\n')

def _sounds():
    from sdat import SDAT, DEFAULT
    S = SDAT(open(DEFAULT, 'rb').read())
    import importlib.util
    spec = importlib.util.spec_from_file_location('hm_rq', os.path.join(HERE, 'hoenn_music.py'))
    hm = importlib.util.module_from_spec(spec); spec.loader.exec_module(hm)
    ids = {k: S.index('seq', v) for k, v in SOUNDS.items()}
    ids['RAY_MUS_RAYQUAZA_APPEARS'] = S.index('seq', hm._mapping()['slots']['mus_rayquaza_appears'])
    return ids

def build_blob(work):
    """-> (file bytes, {symbol: offset in the image}, sizes)"""
    inc = os.path.join(work, 'inc'); _shadow(inc)
    _gfx_c(os.path.join(work, 'ray_gfx.c'))
    defs = [f'-D{k}={v}' for k, v in _sounds().items()]
    objs = []
    for src in [os.path.join(PEM, s) for s in ENGINE] + [os.path.join(HERE, 'emerald_rayquaza_scene.c'),
                                                           os.path.join(work, 'ray_gfx.c')]:
        obj = os.path.join(work, os.path.basename(src)[:-2] + '.o')
        subprocess.run([GCC, *CFLAGS, *defs, '-iquote', inc, '-iquote', os.path.join(PEM, 'include'), '-c', src, '-o', obj],
                       check=True)
        objs.append(obj)
    images = []
    for base in (0x02000000, 0x02800000):
        ld = os.path.join(work, f'link_{base:x}.ld')
        open(ld, 'w').write(
            'ENTRY(Ray_Cmd)\nSECTIONS {\n  . = %#x;\n  .text : { *(.text*) *(.rodata*) *(.data*) . = ALIGN(4); }\n'
            '  .bss (NOLOAD) : { __bss_start = .; *(.bss*) *(COMMON) *(ewram_data) *(iwram_data) *(common_data) '
            '*(.sbss*) . = ALIGN(4); __bss_end = .; }\n  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) }\n}\n'
            % base)
        elf = os.path.join(work, f'ray_{base:x}.elf')
        subprocess.run([GCC, *CFLAGS, '-nostdlib', '-T', ld, '-o', elf, *objs, '-lgcc'], check=True)
        binf = elf[:-4] + '.bin'
        subprocess.run([OBJCOPY, '-O', 'binary', '-j', '.text', elf, binf], check=True)
        syms = {}
        for line in subprocess.run([NM, elf], capture_output=True, text=True, check=True).stdout.split('\n'):
            p = line.split()
            if len(p) == 3: syms[p[2]] = int(p[0], 16) - base
        images.append((open(binf, 'rb').read(), syms))
    (a, sa), (b, _) = images
    assert len(a) == len(b) and len(a) % 4 == 0
    delta = 0x00800000
    relocs = []
    for o in range(0, len(a), 4):
        x, y = struct.unpack_from('<I', a, o)[0], struct.unpack_from('<I', b, o)[0]
        if x != y:
            assert (y - x) & 0xFFFFFFFF == delta, f'word {o:#x} differs by {y - x:#x}: not an address'
            relocs.append(o)
    image = bytearray(a)
    for o in relocs:
        struct.pack_into('<I', image, o, (struct.unpack_from('<I', image, o)[0] - 0x02000000) & 0xFFFFFFFF)
    assert sa['__bss_start'] == len(image), (sa['__bss_start'], len(image))
    bss = sa['__bss_end'] - sa['__bss_start']
    head_size = 32
    reloc_off = head_size + len(image)
    file_size = reloc_off + 4 * len(relocs)
    mem_size = head_size + len(image) + bss
    head = struct.pack('<8I', MAGIC, file_size, mem_size, sa['Ray_Cmd'] | 1, reloc_off, len(relocs), len(image), bss)  # Thumb
    blob = head + bytes(image) + struct.pack(f'<{len(relocs)}I', *relocs)
    return blob, sa, {'image': len(image), 'bss': bss, 'relocs': len(relocs), 'file': len(blob), 'memory': mem_size}

def apply(files):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    import narcio, frontier_area
    with tempfile.TemporaryDirectory() as work:
        blob, sym, sizes = build_blob(work)
    entries = narcio.load(files, ARC)
    assert len(entries) >= frontier_area.FIRST_FILE, f'arc {ARC}: frontier_factory_dome first'
    idx = next((i for i in range(frontier_area.FIRST_FILE, len(entries))
                if len(entries[i]) >= 4 and struct.unpack_from('<I', entries[i])[0] == MAGIC), None)
    if idx is None: idx = len(entries); entries.append(blob)
    else: entries[idx] = blob
    narcio.save(files, ARC, entries)

    def build(base, tmp):
        obj = frontier_area.compile(os.path.join(HERE, 'emerald_rayquaza_stub.c'), tmp, [f'-DRQ_FILE={idx}'])
        return frontier_area.link(obj, base)
    syms, base, size = frontier_area.add(files, 'emerald_rayquaza_scene', build)
    STATE['syms'] = syms
    return (f'Rayquaza scene: arc {ARC} file {idx}, {sizes["file"]} B (code + graphics {sizes["image"]} B, '
            f'{sizes["relocs"]} relocations), {sizes["memory"]} B in memory while it plays; stub {size} B at {base:#x}')

def apply_code(code):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    import frontier_area
    assert 'syms' in STATE, 'emerald_rayquaza_scene: apply() must run first'
    done = [frontier_area.install(code)]
    p = os.path.join(code, 'arm9_ov012.bin')
    d = bytearray(open(p, 'rb').read())
    e = EVCMD_TABLE - OV012 + 4 * COMMAND
    assert struct.unpack_from('<I', d, e)[0] == CMD_OLD, f'EVCMD_TABLE[{COMMAND}] is not Black 2\'s (another patch took it?)'
    struct.pack_into('<I', d, e, STATE['syms']['RQ_Cmd'] | 1)
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)
    done.append(f'command {COMMAND} EmRayquazaScene -> {STATE["syms"]["RQ_Cmd"]:#x}')
    return '; '.join(done)

if __name__ == '__main__':          # python3 emerald_rayquaza_scene.py [verify]: the graphics check / the file's sizes
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    if sys.argv[1:] == ['verify']:
        for s, data, a in graphics(): print(f'{s:42s} {a:#x} {len(data)} B')
    else:
        with tempfile.TemporaryDirectory() as work:
            blob, sym, sizes = build_blob(work)
        print(sizes, hex(sym['Ray_Cmd']))
