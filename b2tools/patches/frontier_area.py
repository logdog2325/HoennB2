"""The Frontier code area (frontier_palace_arena, 2026-10-12; notes/FRONTIER.md "Code space"): a shared helper for the
Emerald Frontier patches, not a patch itself (it is in no patch list). Pokémon Emerald NDS only.

ITCM is full (about 256 bytes were left after rods in the Emerald list). Black 2's heaps leave main RAM above
0x023A9000 unused in DS mode (measured: the main arena's start after GFL_HeapMgrInit is 0x023A8AC4, its end 0x023E0000,
and nothing writes 0x023B0000-0x023E0000 from boot through the intro; every mem_alloc_direct call runs at boot: notes/
WORLD.md "Code space"). The area takes the top 64 KB of it:

  FRAM_BASE 0x023D0000 - 0x023E0000   the main arena's end (arm9 literal 0x0207B358, read by GetUserMemRegionDefaultEnd
                                       in DS mode) moves from 0x023E0000 down to FRAM_BASE, so no allocator can reach it
  arc 211, a file after 1890           the area's image: 16-byte header ('FRAM', size, FRAM_BASE, 0), then each user's
                                       code and data, one after another (32-byte aligned), linked at their RAM addresses
  ITCM FRAM_Boot (frontier_area_boot.c, ~70 B)  main's call of GameInit (arm9 0x0200515c) -> FRAM_Boot: reads the image
                                       to FRAM_BASE (after the arc system is up; again after a soft reset), then GameInit

A user patch, in its apply(files): `syms = frontier_area.add(files, 'name', build)` where build(base, workdir) compiles
and links its code at `base` (frontier_area.compile + frontier_area.link: ordinary non-PIC Thumb code; writable data
and .bss are allowed, the area is RAM); in its apply_code(code): `frontier_area.install(code)` (once per build, the first
user installs the loader) and then point Black 2's calls at its symbols (bl / literal / table words). Code in the area
can call Black 2's functions by address only. DSi mode is not measured (the area lies below the DSi arena, 0x0276DDE0).
Savestates made before the area exists hold none of it: remake them (as for every ITCM patch)."""
import os, re, struct, subprocess, sys, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
LLVM = '/opt/homebrew/opt/llvm/bin'
ARC, FIRST_FILE = 211, 1891                                      # (the area's file: the first 'FRAM' file from 1891)
FRAM_BASE, FRAM_SIZE = 0x023D0000, 0x10000
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
MAIN_ARENA_END_LIT, MAIN_ARENA_END = 0x0207B358, 0x023E0000     # GetUserMemRegionDefaultEnd(OS_ARENA_MAIN), DS mode
GAMEINIT_CALL, GAMEINIT = 0x0200515C, 0x02005264                 # main: bl GameInit
MAGIC = 0x4D415246                                               # 'FRAM'
CFLAGS = ['--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding', '-fno-builtin',
          '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables', '-fno-exceptions',
          '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror']

def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_fa', os.path.join(HERE, 'roamers.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def bl(src, dst):
    return _roamers()._bl(src, dst)

def blx(src, dst):
    """Thumb BLX (immediate) at src to ARM code at dst (4-aligned)."""
    assert not dst & 3, hex(dst)
    off = dst - ((src + 4) & ~3)
    assert -(1 << 22) <= off < (1 << 22), hex(off)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xE800 | (off >> 1) & 0x7FE)

def compile(src, workdir, extra=()):
    obj = os.path.join(workdir, os.path.basename(src)[:-2] + '.o')
    subprocess.run([f'{LLVM}/clang', *CFLAGS, *extra, '-I', workdir, '-c', src, '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    und = [u for u in und if u not in ('U',)]
    assert not und, f'{src} needs {und}: call Black 2 functions by address only'
    return obj

def link(obj, base):
    """Link an object at `base` (roamers.link's relocations: ABS32, THM_CALL, THM_JUMP11), writable .data and .bss
    allowed (the area is RAM; .bss is written out as zeros). -> (bytes, {symbol: address})"""
    d, secs = _roamers()._elf(obj)
    place, blob = {}, bytearray()
    for i, s in enumerate(secs):
        if s['flags'] & 2 and s['size'] and not s['name'].startswith('.ARM.'):
            while len(blob) % max(s['align'], 1): blob += b'\0'
            place[i] = base + len(blob)
            blob += bytes(s['size']) if s['type'] == 8 else d[s['off']:s['off'] + s['size']]   # SHT_NOBITS: zeros
    symtab = next(s for s in secs if s['type'] == 2)
    strs = secs[symtab['link']]
    syms, names = [], {}
    for i in range(symtab['size'] // 16):
        nm, val, size, info, other, shndx = struct.unpack_from('<IIIBBH', d, symtab['off'] + 16 * i)
        name = d[strs['off'] + nm:d.index(b'\0', strs['off'] + nm)].decode()
        syms.append((name, val, shndx))
        if name and shndx in place: names[name] = place[shndx] + val
    for s in secs:
        if s['type'] != 9 or s['info'] not in place: continue
        tbase = place[s['info']]
        for i in range(s['size'] // 8):
            off, info = struct.unpack_from('<II', d, s['off'] + 8 * i)
            sym, typ = info >> 8, info & 0xFF
            name, val, shndx = syms[sym]
            assert shndx in place, f'undefined symbol {name!r}'
            S, at, P = place[shndx] + val, tbase - base + off, tbase + off
            if typ == 2:                                          # R_ARM_ABS32
                A, = struct.unpack_from('<I', blob, at)
                struct.pack_into('<I', blob, at, (S + A) & 0xFFFFFFFF)
            elif typ == 10:                                       # R_ARM_THM_CALL
                h1, h2 = struct.unpack_from('<HH', blob, at)
                A = (h1 & 0x7FF) << 12 | (h2 & 0x7FF) << 1
                if A & (1 << 22): A -= 1 << 23
                if h2 & 0xF800 == 0xE800:                         # blx to ARM code
                    X = (S & ~3) + A - (P & ~3)
                    struct.pack_into('<HH', blob, at, 0xF000 | (X >> 12) & 0x7FF, 0xE800 | (X >> 1) & 0x7FE)
                else:
                    X = (S & ~1) + A - P
                    assert -(1 << 22) <= X < (1 << 22)
                    struct.pack_into('<HH', blob, at, 0xF000 | (X >> 12) & 0x7FF, 0xF800 | (X >> 1) & 0x7FF)
            elif typ == 102:                                      # R_ARM_THM_JUMP11
                h, = struct.unpack_from('<H', blob, at)
                A = (h & 0x7FF) << 1
                if A & 0x800: A -= 0x1000
                o = (S & ~1) + A - P
                assert -2048 <= o < 2048 and not o & 1
                struct.pack_into('<H', blob, at, 0xE000 | (o >> 1) & 0x7FF)
            elif typ == 103:                                      # R_ARM_THM_JUMP8
                h, = struct.unpack_from('<H', blob, at)
                A = (h & 0xFF) << 1
                if A & 0x100: A -= 0x200
                o = (S & ~1) + A - P
                assert -256 <= o < 256 and not o & 1
                struct.pack_into('<H', blob, at, (h & 0xFF00) | (o >> 1) & 0xFF)
            else:
                raise SystemExit(f'frontier_area: relocation type {typ} ({name}) not handled')
    return bytes(blob), names

STATE = {}                                                       # the area's file in arc 211 (this build)

def _find(entries):
    for i in range(FIRST_FILE, len(entries)):
        if len(entries[i]) >= 16 and struct.unpack_from('<I', entries[i], 0)[0] == MAGIC: return i
    return None

def image(files):
    """The area's image (header + body) from arc 211 (found by its 'FRAM' header after file FIRST_FILE - 1), or a new
    empty one (appended at the archive's end by add())."""
    import narcio
    entries = narcio.load(files, ARC)
    assert len(entries) >= FIRST_FILE, f'arc {ARC} has {len(entries)} files: frontier_factory_dome first (1000-1890)'
    i = _find(entries)
    if i is not None:
        img = entries[i]
        magic, size, base, _ = struct.unpack_from('<4I', img, 0)
        assert base == FRAM_BASE and size == len(img) - 16, f'arc {ARC} file {i}: a bad Frontier code area image'
        STATE['file'] = i
        return img
    return struct.pack('<4I', MAGIC, 0, FRAM_BASE, 0)

def add(files, name, build):
    """Append a user's code to the area: build(base, workdir) -> (bytes, syms). Returns (syms, base, size)."""
    import narcio
    img = bytearray(image(files))
    body = len(img) - 16
    body = (body + 31) & ~31
    img += bytes(16 + body - len(img))
    base = FRAM_BASE + body
    with tempfile.TemporaryDirectory() as tmp:
        blob, syms = build(base, tmp)
    img += blob
    size = len(img) - 16
    assert size <= FRAM_SIZE, f'Frontier code area full: {size} > {FRAM_SIZE} ({name})'
    struct.pack_into('<I', img, 4, size)
    entries = narcio.load(files, ARC)
    i = _find(entries)
    if i is None: i = len(entries); entries.append(bytes(img))
    else: entries[i] = bytes(img)
    narcio.save(files, ARC, entries)
    STATE['file'] = i
    return syms, base, len(blob)

def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())

def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)

def install(code):
    """The boot loader in ITCM, main's GameInit call, the main arena's end. Idempotent (the second user finds it)."""
    assert 'file' in STATE, 'frontier_area.install: no add() in this build'
    path9, arm9 = _load(code, 'arm9.bin')
    o = GAMEINIT_CALL - ARM9
    if bytes(arm9[o:o + 4]) != bl(GAMEINIT_CALL, GAMEINIT):
        return 'Frontier code area: loader already installed'
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    base = ITCM_BASE + size
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not at the end of ITCM'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        obj = compile(os.path.join(HERE, 'frontier_area_boot.c'), tmp,
                      [f'-DFRAM_FILE={STATE["file"]}', f'-DFRAM_BASE={FRAM_BASE:#x}', f'-DFRAM_SIZE={FRAM_SIZE:#x}'])
        blob, sym = _roamers().link(obj, base)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    assert struct.unpack_from('<I', arm9, MAIN_ARENA_END_LIT - ARM9)[0] == MAIN_ARENA_END, 'main arena end literal moved?'
    struct.pack_into('<I', arm9, MAIN_ARENA_END_LIT - ARM9, FRAM_BASE)
    arm9[o:o + 4] = bl(GAMEINIT_CALL, sym['FRAM_Boot'] & ~1)
    _save(path9, arm9)
    path, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(path, itcm + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    return (f'Frontier code area: loader {len(blob)} B of ITCM at {base:#x} (arena from {end:#x}); main RAM '
            f'{FRAM_BASE:#x}-{FRAM_BASE + FRAM_SIZE:#x} (main arena end {MAIN_ARENA_END:#x} -> {FRAM_BASE:#x}), image arc {ARC} file {STATE["file"]}')
