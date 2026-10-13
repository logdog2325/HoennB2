"""Birch's 4th question picks the character sprite style (user decision 2026-10-11, notes/DECISIONS.md; notes/FAIRY.md "Birch's questions"):
CLASSIC = the Gen 3-based set of src/sprites, NEW = the community (Gen 5-style) set of src/sprites_gen5 over it. The
answer is bit 14 of the options u16 (save block 27; fairy.py's intro script sets it; 0 for a new game that answers
CLASSIC and for every older save). Both sets are in the ROM; only one is ever loaded.

apply (files): installs src/sprites twice on Black 2's own archives in two scratch trees (patches/sprites.py apply, the same
code as the real install: once as is, once with HOENN_SPRITES_GEN5=1, i.e. src/sprites_gen5's folders over src/sprites'),
compares them, and appends every entry that differs to this build's archive as an extra entry:
  a/0/4/8 overworld sheets: per sheet (the player's sheets, the rival NPC copies, the Ruby team swaps: whatever
          src/sprites_gen5 changes, read at build time)
  a/0/7/1, a/0/7/2 trainer front / back sprites: per sprite (8 files: pictures, cells, animations, MCSS data, palette)
  a/0/3/0 the player's icons (Continue panel, GTS, Spin Trade, Battle Video, Wi-Fi 2D room) and a/0/4/0 the trainer
          card pictures (sprites.py objframes / cardpic, made from the overworld and battle art): these two archives
          have no reserve, so their Gen 5 copies go into a/0/4/8 too (identical copies stored once)
Every remapped classic entry must equal this build's (no later patch changed it: checked). The archives keep their
fixed sizes (build_rom.py RESERVE 48 / 71 / 72), so the ROM layout does not change.

apply_code (code): sprite_switch.c in ITCM (after the code already there, the arena literal protocol of hoenn_music), with
the tables, and the hooks; each site is checked against Black 2's bytes:
  ov036 0x02193d6e  func_ov036_02193d54 (the field's sheet load)          bl GFL_G3DSysReadArcToolResource -> Sprite_OwRead
  ov036 0x02194084  FldBlAct_ExecAsyncRead (the field's async sheet load)  bl GFL_G3DSysReadArcToolResource -> Sprite_OwRead
  arm9  0x0201651c  func_02016510, the one-frame billboard helper (name entry icon, PWT bracket, Join Avenue: callers
                    ov280, ov320, ov060, ov085, via func_020164e8) `adds r4, r2, #0; adds r6, r3, #0` -> bl
                    Sprite_BillboardShim (the file number r2 remapped when the archive r0 is 48)
  arm9  0x02033cf2 ... 0x02033d46  the 8 GetTrSprite*DatID functions     bl GetTrSpriteBaseDatID -> Sprite_TrBase
  the player's icon, read from a handle on a/0/3/0 (func_0204b81c characters, func_0204bba0 / func_0204bbb8 palette;
  pokebw2 include/gfl/clact.h): with NEW and a Gen 5 copy, the load reads it from a handle on a/0/4/8 instead (opened
  and freed around the call, on the tail of the caller's heap):
    ov162 0x0219ef72/82, 0x0219ef98/a8  StartMenu_InitObj: the Continue panel (characters 5 / 7, palette 4 / 6)
    ov214 0x021d39b8/d4                 the GTS (worldtrade.c: 14 / 17, 4 / 6)
    ov216 0x021bc3a4/c4                 Spin Trade (guru2: 20 / 23, 4 / 6)
    ov271 0x021f4382/a0                 Battle Video profiles (br_util.c: 20 / 23, 4 / 6)
    ov203 0x021a7d8a/ae                 the Wi-Fi 2D room's own player (wifi_2dchar.c: 5 / 7, 4 / 6)
  the trainer card picture, by archive id (ov186 func_ov186_021a7ec0 / _021a7d40): GFL_G2DIOReadBGNCGR(40, 16 + v)
  at 0x021a7f32 and GFL_BGSysLoadNCLRDefault(40, v) at 0x021a7d58 -> the Gen 5 copy in a/0/4/8 with NEW
Sprite_OwRead remaps the sheet number (res1 of the object code's record; ARCID_MMODEL_GRA 48) before the read; with
CLASSIC it reads the same file as before. (The field's third reader of that handle, FldActSys_SetupG3DObj, loads 3D
models, never a sheet.) Sprite_TrBase remaps the sprite number GetTrSpriteBaseDatID gives (every
trainer picture file id goes through it: battle, Hall of Fame, trainer card, PWT; pokebw2 src/system/pokegra.c). The
sheets keep their size, so the field's material cache and its async reads take the same time and memory either way.
Test switch: HOENN_TEST_SPRITES=gen5|classic forces the style (the question then changes nothing).
"""
import os, re, sys, json, struct, shutil, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
B2T = os.path.dirname(HERE)
ROOT = os.path.dirname(B2T)
sys.path.insert(0, B2T)
import narcio  # noqa: E402

LLVM = '/opt/homebrew/opt/llvm/bin'
VANILLA_FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV036 = 0x0217F600
ARC_OW, ARC_FRONT, ARC_BACK = 48, 71, 72
ARC_ICONS, ARC_CARDS = 30, 40    # a/0/3/0 the player's icons, a/0/4/0 the trainer card pictures (no reserve: copies in 48)
CFG_BIT = 14                     # options u16 bit: 1 = NEW (Gen 5) sprites; fairy.py CFG_SPRITES_BIT
TABLES = 'sprite_switch.json'    # in the build dir (next to files/ and code/): the remap tables apply -> apply_code

_tables = None


def _sprites_patch():
    spec = importlib.util.spec_from_file_location('sprites_patch_for_switch', os.path.join(HERE, 'sprites.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _scratch_tree(path):
    """a files tree whose archives (a/X/Y/Z) are links to Black 2's own: narcio.save replaces a link, never writes
    through it"""
    src = os.path.join(VANILLA_FILES, 'a')
    for d, _, fs in os.walk(src, followlinks=True):
        rel = os.path.relpath(d, VANILLA_FILES)
        os.makedirs(os.path.join(path, rel), exist_ok=True)
        for f in fs:
            os.symlink(os.path.realpath(os.path.join(d, f)), os.path.join(path, rel, f))


def install_both(scratch):
    """{arc: (classic entries, gen5 entries)} for the overworld sheets and the trainer sprites, from Black 2's archives"""
    sp = _sprites_patch()
    keep = os.environ.pop('HOENN_SPRITES_GEN5', None)
    out = {}
    try:
        trees = {}
        for style in ('classic', 'gen5'):
            t = os.path.join(scratch, style)
            _scratch_tree(t)
            if style == 'gen5': os.environ['HOENN_SPRITES_GEN5'] = '1'
            else: os.environ.pop('HOENN_SPRITES_GEN5', None)
            sp.apply(t)
            trees[style] = t
        for arc in (ARC_OW, ARC_FRONT, ARC_BACK, ARC_ICONS, ARC_CARDS):
            out[arc] = (narcio.load(trees['classic'], arc), narcio.load(trees['gen5'], arc))
    finally:
        os.environ.pop('HOENN_SPRITES_GEN5', None)
        if keep is not None: os.environ['HOENN_SPRITES_GEN5'] = keep
    return out


def differing(classic, gen5, unit):
    """the numbers (sheet or sprite) whose entries differ; unit = files per number"""
    assert len(classic) == len(gen5) and len(classic) % unit == 0, (len(classic), len(gen5), unit)
    return [n for n in range(len(classic) // unit) if classic[unit * n:unit * n + unit] != gen5[unit * n:unit * n + unit]]


def apply(files):
    global _tables
    _tables = None
    if os.environ.get('HOENN_SPRITES_GEN5'):
        return 'HOENN_SPRITES_GEN5=1 installed the Gen 5 set as the only set: no switch'
    scratch = tempfile.mkdtemp(prefix='sprite_switch_', dir=os.path.dirname(os.path.abspath(files)))
    try:
        both = install_both(scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    tables, notes = {}, []
    for arc, unit, key in ((ARC_OW, 1, 'ow'), (ARC_FRONT, 8, 'front'), (ARC_BACK, 8, 'back')):
        classic, gen5 = both[arc]
        nums = differing(classic, gen5, unit)
        ents = narcio.load(files, arc)
        assert len(ents) % unit == 0, f'a/{arc:03d}: {len(ents)} files, not whole sprites of {unit}'
        pairs, extra = [], 0
        for n in nums:
            here = ents[unit * n:unit * n + unit]
            assert here == classic[unit * n:unit * n + unit], \
                f'a/{arc:03d} {key} {n}: this build\'s entry is not the classic install (a later patch changed it)'
            new = len(ents) // unit
            ents += gen5[unit * n:unit * n + unit]
            pairs.append([n, new])
            extra += sum(map(len, gen5[unit * n:unit * n + unit]))
        if key != 'ow':
            assert all(b < 256 for _, b in pairs), f'{key}: GetTrSpriteBaseDatID returns a u8 ({pairs})'
        if pairs:
            narcio.save(files, arc, ents)
        tables[key] = pairs
        notes.append(f'{key} {len(pairs)} (+{extra} B)')
    # the icons and card pictures: their Gen 5 copies appended to a/0/4/8 (each distinct copy once)
    ents = narcio.load(files, ARC_OW)
    first, icons, stored, extra = len(ents), [], {}, 0
    for arc in (ARC_ICONS, ARC_CARDS):
        classic, gen5 = both[arc]
        here = narcio.load(files, arc)
        for n in differing(classic, gen5, 1):
            assert here[n] == classic[n], f'a/{arc:03d} {n}: this build\'s entry is not the classic install (a later patch changed it)'
            if gen5[n] not in stored:
                stored[gen5[n]] = len(ents); ents.append(gen5[n]); extra += len(gen5[n])
            icons.append([arc, n, stored[gen5[n]]])
    if len(ents) > first:
        narcio.save(files, ARC_OW, ents)
    tables['icons'] = icons
    notes.append(f'icons/cards {len(icons)} as {len(ents) - first} entries of a/{ARC_OW:03d} (+{extra} B)')
    _tables = tables
    json.dump(tables, open(os.path.join(os.path.dirname(os.path.abspath(files)), TABLES), 'w'), indent=1)
    return 'Gen 5 entries appended: ' + ', '.join(notes) + ' ' + json.dumps(tables)


# ---- code -------------------------------------------------------------------------------------------------------------
G3D_READ, TR_BASE = 0x02049384, 0x02030740
OW_SITES = (0x02193d6e, 0x02194084)                                        # ov036, bl GFL_G3DSysReadArcToolResource
TR_SITES = (0x02033cf2, 0x02033cfe, 0x02033d0a, 0x02033d16, 0x02033d22, 0x02033d2e, 0x02033d3a, 0x02033d46)  # arm9
BILLBOARD = (0x0201651c, '141c1e1c')                                        # func_02016510: adds r4, r2; adds r6, r3
CHARS, PAL, PAL_EX = 0x0204b81c, 0x0204bba0, 0x0204bbb8                   # clact.h: handle-based characters / palettes
READ_BG_NCGR, LOAD_NCLR = 0x0204b264, 0x0204b0b8                          # arc_util.h: GFL_G2DIOReadBGNCGR, ..LoadNCLRDefault
OVERLAYS = {'ov162': 0x0219CE80, 'ov186': 0x021A75A0, 'ov203': 0x021A78C0, 'ov214': 0x021D3380, 'ov216': 0x021BB700,
            'ov271': 0x021EFE40}
ICON_SITES = [   # (overlay, call site, Black 2's callee, shim): every load of a/0/3/0 files 4-7, 14, 17, 20, 23 and the card
    ('ov162', 0x0219ef72, CHARS, 'Sprite_IconChars'), ('ov162', 0x0219ef82, PAL, 'Sprite_IconPal'),
    ('ov162', 0x0219ef98, CHARS, 'Sprite_IconChars'), ('ov162', 0x0219efa8, PAL, 'Sprite_IconPal'),
    ('ov214', 0x021d39b8, CHARS, 'Sprite_IconChars'), ('ov214', 0x021d39d4, PAL_EX, 'Sprite_IconPalEx'),
    ('ov216', 0x021bc3a4, CHARS, 'Sprite_IconChars'), ('ov216', 0x021bc3c4, PAL_EX, 'Sprite_IconPalEx'),
    ('ov271', 0x021f43a0, CHARS, 'Sprite_IconChars'), ('ov271', 0x021f4382, PAL_EX, 'Sprite_IconPalEx'),
    ('ov203', 0x021a7d8a, CHARS, 'Sprite_IconChars'), ('ov203', 0x021a7dae, PAL_EX, 'Sprite_IconPalEx'),
    ('ov186', 0x021a7f32, READ_BG_NCGR, 'Sprite_CardChars'), ('ov186', 0x021a7d58, LOAD_NCLR, 'Sprite_CardPal'),
]


def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_link', os.path.join(HERE, 'roamers.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _bl(src, dst):
    off = dst - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, hex(off)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)


def _put(d, base, addr, old, new, what):
    o = addr - base
    cur = bytes(d[o:o + len(old)])
    assert cur == old, f'{what} at {addr:#x}: {cur.hex()} (expected {old.hex()})'
    d[o:o + len(new)] = new


def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())


def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)


def header(t):
    def arr(name, pairs): return f'static const u16 {name}[] = {{{", ".join(str(x) for p in pairs for x in p) or "0"}}};\n'
    return (f'#define ARC_OW {ARC_OW}\n#define N_OW {len(t["ow"])}\n#define N_FRONT {len(t["front"])}\n'
            f'#define N_BACK {len(t["back"])}\n#define N_ICONS {len(t.get("icons", []))}\n#define ARC_ICONS {ARC_ICONS}\n'
            + arr('kOw', t['ow']) + arr('kFront', t['front']) + arr('kBack', t['back']) + arr('kIcons', t.get('icons', [])))


def build(base, workdir, t, force=None):
    with open(os.path.join(workdir, 'sprite_switch_data.h'), 'w') as f: f.write(header(t))
    obj = os.path.join(workdir, 'sprite_switch.o')
    defs = [f'-DSPRITE_FORCE={force}'] if force is not None else []
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror', *defs,
                    '-I', workdir, '-c', os.path.join(HERE, 'sprite_switch.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'sprite_switch.c needs {und}: call Black 2 functions by address only'
    return _roamers().link(obj, base)


def apply_code(code):
    if os.environ.get('HOENN_SPRITES_GEN5'): return 'off (HOENN_SPRITES_GEN5=1)'
    path = os.path.join(os.path.dirname(os.path.abspath(code)), TABLES)
    t = _tables if _tables is not None else json.load(open(path))
    if not any(t.values()): return 'no Gen 5 sprites in src/sprites_gen5: no switch'
    force = {'gen5': 1, 'classic': 0}.get(os.environ.get('HOENN_TEST_SPRITES', '').lower())
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    p9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not at the end of ITCM'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym = build(base, tmp, t, force)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    pi, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(pi, bytes(itcm) + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    for at in TR_SITES:
        _put(arm9, ARM9, at, _bl(at, TR_BASE), _bl(at, sym['Sprite_TrBase'] & ~1), 'bl GetTrSpriteBaseDatID')
    at, old = BILLBOARD
    _put(arm9, ARM9, at, bytes.fromhex(old), _bl(at, sym['Sprite_BillboardShim'] & ~1),
         'func_02016510 adds r4, r2, #0; adds r6, r3, #0')
    p036, ov036 = _load(code, 'arm9_ov036.bin')
    for at in OW_SITES:
        _put(ov036, OV036, at, _bl(at, G3D_READ), _bl(at, sym['Sprite_OwRead'] & ~1), 'bl GFL_G3DSysReadArcToolResource')
    _save(p9, arm9); _save(p036, ov036)
    if t.get('icons'):
        for name in sorted({ov for ov, *_ in ICON_SITES}):
            po, d = _load(code, f'arm9_{name}.bin')
            for ov, at, callee, shim in ICON_SITES:
                if ov == name:
                    _put(d, OVERLAYS[ov], at, _bl(at, callee), _bl(at, sym[shim] & ~1), f'{ov} bl {callee:#x}')
            _save(po, d)
    open(os.path.join(os.path.dirname(os.path.abspath(code)), 'sprite_switch_symbols.json'), 'w').write(json.dumps(  # kept after the build
        {k: sym[k] | 1 for k in ('Sprite_IsGen5', 'Sprite_OwFile', 'Sprite_TrBase')} | {'itcm_start': base, 'itcm_end': end},
        indent=1))
    return (f'sprite_switch: {len(blob)} B of ITCM at {base:#x} (ends {end:#x}); options bit {CFG_BIT}; '
            f'{len(t["ow"])} sheets, {len(t["front"])} fronts, {len(t["back"])} backs, {len(t.get("icons", []))} icon/card '
            f'files ({len(ICON_SITES)} load sites)'
            + (f'; HOENN_TEST_SPRITES forces {force}' if force is not None else ''))
