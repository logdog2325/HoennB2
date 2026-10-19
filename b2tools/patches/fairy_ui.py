"""Fairy type (v16): the screens and icons (fairy_ui, 2026-10-08; notes/FAIRY_SCOPE.md section 2, notes/FAIRY.md).

Type 17 = Fairy, 18 = "no type" (agreed with fairy_core; its patch fairy.py does the engine, data, the 17 -> 18 sites
outside the screens below, Birch's toggle and the data hooks). When the toggle is off, fairy.py's hooks map Fairy back
in the species and move data, so no screen ever gets a 17 and every screen looks as in v15.2; only the Pokédex type
search reads the toggle itself (its list is a fixed table).

Black 2 keeps type graphics in fixed per-type arrays inside each screen's work struct, sized 17, with other fields
right behind them. Each screen below gets an 18th entry WITHOUT overrunning anything: the work struct is allocated
bigger and the array moves to the new space at its end (every access was found by reading the code: the offsets are
in the comments; proof in notes/FAIRY.md "Screens (fairy_ui)"). Loops over the types go
to 18. Where an access can't be re-encoded in place, a few bytes of Thumb in ITCM (after fairy.py's code) do it.

Art (the user's rule: made from Black 2's own icons, nothing drawn or downloaded): b2tools/fairy_art.py builds the
FAIRY icon (a/0/8/2 entry 51 = icon of type 17, an unused contest icon before) from FIRE's frame and the
letters of FIRE, DARK and FLYING, in Gen 6 Fairy pink (palette entry 33 row 2, colours 8/9, unused before).

Test switch (test builds only): HOENN_TEST_FAIRY_UI=1 makes type 1 of Groudon, Mudkip, Poochyena, Zigzagoon and Wurmple
Fairy and Earth Power + Surf Fairy-type in the data (the ch11 test party of six Groudon with HM03, the ch1 test's
Mudkip, Route 101), so every screen can be checked without fairy.py; it also makes the Pokédex search's Fairy_IsOn
stub return 1 when fairy.py is not in the build.
"""
import os, re, struct, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
LLVM = '/opt/homebrew/opt/llvm/bin'
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
TYPE_FAIRY, TYPE_NONE = 17, 18
ARM9 = 0x02004000
ITCM_BASE, ARENA_ITCM_LIT = 0x01FF8000, 0x0207B400
TYPE_PAL_ROWS = 0x0209208C              # arm9 data_0209208c: palette row of each type icon (func_0202d7e8)

# ------------------------------------------------------------------------------------------------ small tools

def asm(text):
    """Thumb machine code of `text` (no pc-relative forms) through llvm-mc."""
    assert '=' not in text and not re.search(r'\[pc|\badr\b|\bb[a-z]*\s+#', text), f'pc-relative form in {text!r}'
    src = '.syntax unified\n.thumb\n' + '\n'.join(l.strip() for l in text.strip().splitlines()) + '\n'
    r = subprocess.run([f'{LLVM}/llvm-mc', '-triple=thumbv5te-none-eabi', '-show-encoding'], input=src,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = bytearray()
    for m in re.finditer(r'encoding: \[([^\]]*)\]', r.stdout):
        out += bytes(int(b, 16) for b in m.group(1).split(','))
    return bytes(out)

def bl(src, dst):
    off = (dst & ~1) - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, (hex(src), hex(dst))
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)

def symbols(module):
    p = os.path.join(DECOMP, 'config', 'b2_us', 'arm9', 'symbols.txt' if module == 'arm9' else
                     f'overlays/{module}/symbols.txt')
    out = {}
    for line in open(p):
        m = re.match(r'(\S+) kind:function\(\w+,size=(0x[0-9a-f]+)\) addr:(0x[0-9a-f]+)', line)
        if m:
            addr, size = int(m.group(3), 16), int(m.group(2), 16)
            out[m.group(1)] = (addr, size)
            # also by the decomp's address name (func_ov142_0219c444 / func_0201f14c), which a newer decomp may have
            # replaced with a real one (ItemMenuProc_Init): our lookups keep working (notes/POKEBW2_UPGRADE.md)
            out.setdefault(f'func_{module}_{addr:08x}' if module != 'arm9' else f'func_{addr:08x}', (addr, size))
    return out

def ov_base(n):
    cur = None
    for line in open(os.path.join(DECOMP, 'extract', 'b2_us', 'arm9_overlays', 'overlays.yaml')):
        m = re.match(r'\s*-\s*id:\s*(\d+)', line)
        if m: cur = int(m.group(1)); continue
        m = re.match(r'\s*base_address:\s*(\d+)', line)
        if m and cur == n: return int(m.group(1))

class Module:
    """A decompressed code binary of the build's code/ dir, edited by matched byte sequences."""
    def __init__(self, code, n):
        self.name = f'ov{n:03d}'
        self.path = os.path.join(code, f'arm9_ov{n:03d}.bin')
        self.d = bytearray(open(self.path, 'rb').read())
        self.base = ov_base(n)
        self.funcs = symbols(self.name)
        self.log = []
    def _matcher(self, old):
        """[(bytes, None) | (None, (rd, literal address))] per instruction of `old`; 'ldr rN, =0xADDR' = a pc-relative
        load of the literal word AT that address."""
        out = []
        for line in old.strip().splitlines():
            mm = re.match(r'\s*ldr r(\d), =(0x[0-9a-fA-F]+)\s*$', line)
            mb = re.match(r'\s*bl =(0x[0-9a-fA-F]+)\s*$', line)
            out.append((None, (int(mm.group(1)), int(mm.group(2), 16))) if mm else
                       (None, ('bl', int(mb.group(1), 16))) if mb else (asm(line), None))
        return out
    def find_all(self, func, old, extra=0):
        start, size = self.funcs[func]
        pat = self._matcher(old) if isinstance(old, str) else [(old, None)]
        n = sum(len(b) if b else (4 if lit[0] == 'bl' else 2) for b, lit in pat)
        hits = []
        for a in range(start, start + size + extra - n + 1, 2):
            o, ok = a - self.base, True
            for b, lit in pat:
                if b is not None:
                    if bytes(self.d[o:o + len(b)]) != b: ok = False; break
                    o += len(b)
                elif lit[0] == 'bl':
                    if bytes(self.d[o:o + 4]) != bl(self.base + o, lit[1]): ok = False; break
                    o += 4
                else:
                    h = struct.unpack_from('<H', self.d, o)[0]
                    pc = self.base + o
                    if h >> 11 != 9 or (h >> 8 & 7) != lit[0] or ((pc + 4) & ~3) + 4 * (h & 0xFF) != lit[1]: ok = False; break
                    o += 2
            if ok: hits.append(a)
        return hits, n
    def find(self, func, old):
        """Address of the one occurrence of `old` (asm text, see _matcher, or bytes) inside function `func`."""
        hits, _ = self.find_all(func, old)
        assert len(hits) == 1, f'{self.name} {func}: {len(hits)} matches of {old!r}'
        return hits[0]
    def patch(self, func, old, new):
        """Replace the instructions `old` (found once in `func`) by `new` (asm text, bytes or f(addr)), same size."""
        at = self.find(func, old)
        code = new(at) if callable(new) else (asm(new) if isinstance(new, str) else new)
        n = self.find_all(func, old)[1]
        assert len(code) == n, (func, len(code), n)
        self.d[at - self.base:at - self.base + n] = code
        self.log.append(at)
        return at
    def word(self, addr, old, new):
        o = addr - self.base
        assert struct.unpack_from('<I', self.d, o)[0] == old, f'{self.name} {addr:#x}: {struct.unpack_from("<I", self.d, o)[0]:#x} != {old:#x}'
        struct.pack_into('<I', self.d, o, new); self.log.append(addr)
    def save(self):
        if os.path.islink(self.path): os.unlink(self.path)
        open(self.path + '.tmp', 'wb').write(self.d); os.replace(self.path + '.tmp', self.path)

# ------------------------------------------------------------------------------------------------ data (NitroFS)

def apply(files):
    import narcio, fairy_art
    out = []
    e = narcio.load(files, 82)
    assert len(e[51]) == 304 and e[51][:4] == b'RGCN'
    e[51], e[33], _ = fairy_art.build(e)
    narcio.save(files, 82, e)
    out.append('a/0/8/2 entry 51 = FAIRY icon, palette 33 row 2 colours 8/9 = Fairy pinks')
    out.append(button_palette(files))
    out.append(dex_sheets(files, e[51]))
    out.append(hof_data(files))
    if os.environ.get('HOENN_TEST_FAIRY_UI'):
        out.append(test_data(files))
    return '; '.join(out)

def gradient(src, top):
    """A colour ramp shaped like `src` (BGR555 list, brightest first), recoloured to start at `top` (r, g, b 5-bit):
    each step keeps src's brightness ratio to its first colour (Black 2's own ramp, only the hue changes)."""
    def ch(v): return v & 31, v >> 5 & 31, v >> 10 & 31
    r0, g0, b0 = ch(src[0]); base = max(r0, g0, b0)
    out = []
    for v in src:
        k = max(ch(v)) / base
        r, g, b = (min(31, round(c * k)) for c in top)
        out.append(r | g << 5 | b << 10)
    return out

FAIRY_RGB = (29, 19, 21)                      # Gen 6 Fairy pink #EE99AC in 5-bit (fairy_art.FILL)
BUTTON_PAL_TABLE, BUTTON_PAL_PSYCHIC = 0x021F3864, 469

def button_palette(files):
    """a/0/1/1: battle move-button palettes, one NCLR per type (ov168 data_ov168_021f3864, 17 file ids 464-480).
    Colours 8-13 are the type's ramp, the rest is shared. Fairy = Psychic's (469) with a Fairy-pink ramp, appended as
    entry FAIRY_BUTTON_PAL (the archive had 572 entries, 0-571)."""
    import narcio, fairy_art as icons
    e = narcio.load(files, 11)
    assert len(e) == FAIRY_BUTTON_PAL, len(e)
    pal = icons.palette(e[BUTTON_PAL_PSYCHIC])
    pal[8:14] = gradient(pal[8:14], FAIRY_RGB)
    e.append(icons.set_palette(e[BUTTON_PAL_PSYCHIC], pal))
    narcio.save(files, 11, e)
    return f'a/0/1/1 entry {FAIRY_BUTTON_PAL} = Fairy move-button palette ({" ".join(f"{c:04x}" for c in pal[8:14])})'

FAIRY_BUTTON_PAL = 572

HOF_PARTICLE_TABLE, HOF_PALETTE_TABLE = 0x0219B8CC, 0x0219BA98     # ov265: a/2/1/3 file of each type (17 u32 each)
HOF_NORMAL_SPA, HOF_PSYCHIC_PAL = 45, 17
HOF_FAIRY_SPA, HOF_FAIRY_PAL = 52, 53                               # appended (a/2/1/3 had 52 entries, 0-51)

def tint(c, top=FAIRY_RGB):
    """A grey/any BGR555 colour -> the same brightness (max channel) in the Fairy pink's hue."""
    lum = max(c & 31, c >> 5 & 31, c >> 10 & 31)
    m = max(top)
    r, g, b = (min(31, round(ch * lum / m)) for ch in top)
    return r | g << 5 | b << 10

def hof_data(files):
    """a/2/1/3 (Hall of Fame). Per type: a particle file (SPA, entries 34-50: one 256x256 A5I3 texture of type motifs,
    texture block ' TPS' at +0xf0, its palette at +0xf0 + [+0xc], [+0x10] bytes) and a background palette (entries 3-20,
    colours 1-9 a ramp). Fairy: Normal's star field (45) with its texture palette tinted Fairy pink (the stars become
    pink sparkles; texture untouched) -> entry 52; Psychic's palette (17) with a Fairy-pink ramp -> entry 53."""
    import narcio, fairy_art as icons
    e = narcio.load(files, 213)
    assert len(e) == HOF_FAIRY_SPA, len(e)
    spa = bytearray(e[HOF_NORMAL_SPA])
    o = 0xF0
    assert spa[:4] == b' APS' and spa[o:o + 4] == b' TPS' and spa[o + 5] == 6     # A5I3
    poff, psize = struct.unpack_from('<II', spa, o + 0xC)
    n = psize // 2
    pal = list(struct.unpack_from(f'<{n}H', spa, o + poff))
    struct.pack_into(f'<{n}H', spa, o + poff, *[tint(c) if c else 0 for c in pal])
    e.append(bytes(spa))
    bg = icons.palette(e[HOF_PSYCHIC_PAL])
    bg[1:10] = gradient(bg[1:10], FAIRY_RGB)
    e.append(icons.set_palette(e[HOF_PSYCHIC_PAL], bg))
    narcio.save(files, 213, e)
    return f'a/2/1/3 entries {HOF_FAIRY_SPA} (Fairy particles = Normal\'s stars tinted pink) and {HOF_FAIRY_PAL} (Fairy ramp)'

def dex_sheets(files, fairy_ncgr):
    """a/1/5/7 entries 19-24: the Pokédex's type sheets for French, German, Italian, Japanese, Korean and Spanish entries
    (256x256 4bpp, 2D tiles, same palette indices as a/0/8/2's icons; a type's icon = the 32x16 cell at (row, col)
    from data_ov296_0219fac8). Fairy's icon (the same pixels as a/0/8/2 entry 51) goes into the free cell (5, 3)."""
    import narcio, fairy_art as icons
    pix = icons.icon_decode(fairy_ncgr)
    e = narcio.load(files, 157)
    r0, c0 = DEX_FAIRY_CELL
    for f in DEX_SHEETS:
        d = bytearray(e[f])
        th, tw = struct.unpack_from('<HH', d, 0x18)
        assert (tw, th) == (32, 32) and struct.unpack_from('<I', d, 0x24)[0] == 0, f
        off = 0x18 + struct.unpack_from('<I', d, 0x2C)[0]
        for y in range(16):
            for x in range(32):
                X, Y = c0 * 32 + x, r0 * 16 + y
                t = (Y // 8) * 32 + X // 8; j = (Y % 8) * 8 + X % 8
                i = off + t * 32 + j // 2
                assert (d[i] >> (4 * (j & 1))) & 15 == 0, f'a/1/5/7 {f}: cell {DEX_FAIRY_CELL} not empty'
                d[i] |= pix[y][x] << (4 * (j & 1))
        e[f] = bytes(d)
    narcio.save(files, 157, e)
    return f'a/1/5/7 entries {DEX_SHEETS[0]}-{DEX_SHEETS[-1]}: FAIRY icon in cell {DEX_FAIRY_CELL}'

def test_data(files):
    """Test builds only: Groudon (383) Fairy/Ground, Mudkip (258) Fairy/Water, Earth Power (414) and Surf (57) Fairy."""
    import narcio
    p = narcio.load(files, 16)
    for sp, t in ((383, 4), (258, 10), (261, 16), (263, 0), (265, 6)):   # + Route 101's Poochyena, Zigzagoon, Wurmple
        rec = bytearray(p[sp]); assert rec[6] == rec[7] == t, (sp, rec[6], rec[7])
        rec[6] = TYPE_FAIRY; p[sp] = bytes(rec)
    narcio.save(files, 16, p)
    m = narcio.load(files, 21)
    for mv, t in ((414, 4), (57, 10)):
        rec = bytearray(m[mv]); assert rec[0] == t, (mv, rec[0]); rec[0] = TYPE_FAIRY; m[mv] = bytes(rec)
    narcio.save(files, 21, m)
    return 'TEST: Groudon, Mudkip, Poochyena, Zigzagoon, Wurmple type 1 Fairy; Earth Power and Surf Fairy'

# ------------------------------------------------------------------------------------------------ code

def summary(code):
    """ov207 (Pokémon summary). Work struct 0x264 B (GFL_ProcInitSubsystem in func_ov207_021b50b0); the 17 type-icon
    char resources sit at +0x130..+0x173 and +0x174 is another field used everywhere. New: struct 0x2ac B, the array
    at +0x264 with 18 entries. Every access of +0x130 (constscan.py over the whole overlay; 9 sites) is re-based."""
    m = Module(code, 207)
    NEW = 0x264
    # struct size: GFL_ProcInitSubsystem(proc, 0x99 << 2, heap) and the memset after it
    m.patch('func_ov207_021b50b0', 'movs r1, #0x99\nadds r0, r4, #0x0\nlsls r1, r1, #0x2',
            'movs r1, #0xab\nadds r0, r4, #0x0\nlsls r1, r1, #0x2')
    m.patch('func_ov207_021b50b0', 'movs r2, #0x99\nstr r0, [sp, #0x8]\nmovs r1, #0x0\nlsls r2, r2, #0x2',
            'movs r2, #0xab\nstr r0, [sp, #0x8]\nmovs r1, #0x0\nlsls r2, r2, #0x2')
    # load loop (func_ov207_021b36a4): [sp+0xc] = 0x1a0 - 0x70 = 0x130 -> 0x1a0 + 0xc4 = 0x264; 17 -> 18 icons
    m.patch('func_ov207_021b36a4', 'str r1, [sp, #0x1c]\nsubs r0, #0x70\nstr r0, [sp, #0xc]',
            'str r1, [sp, #0x1c]\nadds r0, #0xc4\nstr r0, [sp, #0xc]')
    m.patch('func_ov207_021b36a4', 'str r0, [r2, r1]\nadds r0, r4, #0x1\nlsls r0, r0, #0x18\nlsrs r4, r0, #0x18\ncmp r4, #0x11',
            'str r0, [r2, r1]\nadds r0, r4, #0x1\nlsls r0, r0, #0x18\nlsrs r4, r0, #0x18\ncmp r4, #0x12')
    # free loop (func_ov207_021b3c5c): r6 = 0x13 << 4 -> 0x99 << 2; 17 -> 18
    m.patch('func_ov207_021b3c5c', 'movs r6, #0x13\nmovs r4, #0x0\nlsls r6, r6, #0x4',
            'movs r6, #0x99\nmovs r4, #0x0\nlsls r6, r6, #0x2')
    m.patch('func_ov207_021b3c5c', 'lsrs r4, r0, #0x18\ncmp r4, #0x11', 'lsrs r4, r0, #0x18\ncmp r4, #0x12')
    # func_ov207_021b3cf4 (two cell actors made with type 0's icon): r1 = 0x174 - 0x44 -> 0x174 + 0xf0
    start, size = m.funcs['func_ov207_021b3cf4']
    old, new = asm('subs r1, #0x44\nadds r2, #0xa4\nsubs r3, #0x68'), asm('adds r1, #0xf0\nadds r2, #0xa4\nsubs r3, #0x68')
    body = bytes(m.d[start - m.base:start - m.base + size])
    hits = [i for i in range(0, size, 2) if body[i:i + len(old)] == old]
    assert len(hits) == 2, hits
    for i in hits: m.d[start - m.base + i:start - m.base + i + len(old)] = new; m.log.append(start + i)
    # info page types (func_ov207_021b6ad4): 0xaf + 0x81 -> 0x99 << 2; [sp+0x1c] = 0x60 + 0xd0 -> 0x99 << 2
    m.patch('func_ov207_021b6ad4', 'movs r0, #0xaf\nadds r0, #0x81\nldr r0, [r1, r0]',
            'movs r0, #0x99\nlsls r0, r0, #0x2\nldr r0, [r1, r0]')
    m.patch('func_ov207_021b6ad4', 'ldr r0, [sp, #0x1c]\nadd r5, sp, #0x24\nadds r0, #0xd0',
            'movs r0, #0x99\nadd r5, sp, #0x24\nlsls r0, r0, #0x2')
    # another page's types (func_ov207_021b8d50): 0xaf + 0x81, 0x78 + 0xb8 -> 0x99 << 2
    m.patch('func_ov207_021b8d50', 'movs r0, #0xaf\nadds r0, #0x81\nldr r0, [r1, r0]',
            'movs r0, #0x99\nlsls r0, r0, #0x2\nldr r0, [r1, r0]')
    m.patch('func_ov207_021b8d50', 'movs r0, #0x78\nadds r0, #0xb8\nldr r0, [r1, r0]',
            'movs r0, #0x99\nlsls r0, r0, #0x2\nldr r0, [r1, r0]')
    # move-list cell actor made with type 0's icon (func_ov207_021ba56c): r1 = r7 (0x174) - 0x44 -> + 0xf0
    m.patch('func_ov207_021ba56c', 'adds r1, r7, #0x0\nsubs r1, #0x44', 'adds r1, r7, #0x0\nadds r1, #0xf0')
    # move types (func_ov207_021ba7d4): 0x13 << 4 -> 0x99 << 2
    m.patch('func_ov207_021ba7d4', 'movs r0, #0x13\nlsls r0, r0, #0x4\nldr r0, [r1, r0]',
            'movs r0, #0x99\nlsls r0, r0, #0x2\nldr r0, [r1, r0]')
    m.save()
    return f'ov207 summary: struct 0x264 -> 0x2ac, type icons at +{NEW:#x} x18 ({len(m.log)} sites)'

# ------------------------------------------------------------------------------------------------ ITCM blob

_spec = __import__('importlib.util').util.spec_from_file_location('exp_share_fui', os.path.join(HERE, 'exp_share.py'))
_es = __import__('importlib.util').util.module_from_spec(_spec); _spec.loader.exec_module(_es)

class Blob(_es.Thumb):
    """exp_share's Thumb encoder (labels, bl to addresses, literal words) + any non-pc-relative instruction via llvm-mc."""
    def a(self, text): self.out += asm(text)
    def align4(self):
        while self.pc & 3: self.nop()
    def table(self, name, words):
        self.align4(); self.label(name); self.out += struct.pack(f'<{len(words)}I', *words)

BAG_SIZE_OLD, BAG_SIZE = 0x1F54, 0x2008
BAG_CHARS, BAG_ACTORS = 0x1F60, 0x1FC0       # 0xfb << 5, 0xfe << 5

def itcm_blob(base, vanilla_buttons, vanilla_hof, fairy_on):
    t = Blob(base)
    # ov142 Bag: the struct size for GFL_ProcInitSubsystem (r0 = r4 as before) and for the memset after it
    t.label('BagInitArgs'); t.a('adds r0, r4, #0x0'); t.ldr_lit(1, 'bag_size'); t.a('bx lr')
    t.label('BagMemsetArgs'); t.ldr_lit(2, 'bag_size'); t.a('movs r1, #0x0\nbx lr')
    # ov142 Bag func_ov142_0219dda0: r0 = work + type * 4 -> the type's actor (r4 is dead after it)
    t.label('BagTypeActor'); t.a(f'movs r4, #{BAG_ACTORS >> 5:#x}\nlsls r4, r4, #0x5\nldr r0, [r0, r4]\nbx lr')
    t.word('bag_size', BAG_SIZE)
    pc_thunks(t)
    # ov300 Pokédex search, end of the type list's build loop (func_ov300_021a3d04), in place of
    # `str r0, [r1, r7]; cmp r4, #0x10`: the store, then the loop's compare against 16 + Fairy_IsOn() (17 or 18 entries)
    t.label('DexTypeListCmp')
    t.a('str r0, [r1, r7]\npush {r0, r1, r2, r3, lr}')
    if fairy_on is None:
        t.bl_label('FairyIsOnStub')
    else:
        t.bl(fairy_on)
    t.a('adds r0, #0x10\ncmp r4, r0\npop {r0, r1, r2, r3, pc}')
    if fairy_on is None:                                   # solo test builds without fairy.py
        t.label('FairyIsOnStub'); t.a(f'movs r0, #{1 if os.environ.get("HOENN_TEST_FAIRY_UI") else 0}\nbx lr')
    # ov168 battle move buttons: palette file (a/0/1/1) of each type, 18 entries
    t.table('ButtonPalettes', list(vanilla_buttons) + [FAIRY_BUTTON_PAL])
    # ov265 Hall of Fame: particle file and palette file (a/2/1/3) of each type, 18 entries
    t.table('HofParticles', list(vanilla_hof[0]) + [HOF_FAIRY_SPA])
    t.table('HofPalettes', list(vanilla_hof[1]) + [HOF_FAIRY_PAL])
    return t.assemble(), dict(t.labels)

def install_itcm(code, build):
    """Append the blob to ITCM after everything before us (hoenn_world, roamers, fairy.py), as roamers.py does:
    itcm.bin grows, itcm.yaml's code_size and the arm9 literal of the ITCM arena start move past it."""
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    base = ITCM_BASE + size
    p9 = os.path.join(code, 'arm9.bin'); arm9 = bytearray(open(p9, 'rb').read())
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not the end of ITCM'
    blob, sym = build(base)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000
    struct.pack_into('<I', arm9, lit, end)
    for path, d in ((p9, arm9),):
        if os.path.islink(path): os.unlink(path)
        open(path + '.tmp', 'wb').write(d); os.replace(path + '.tmp', path)
    pi = os.path.join(code, 'itcm.bin'); itcm = open(pi, 'rb').read()
    assert len(itcm) == size
    if os.path.islink(pi): os.unlink(pi)
    open(pi + '.tmp', 'wb').write(itcm + blob + bytes(end - base - len(blob))); os.replace(pi + '.tmp', pi)
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    return base, len(blob), sym

# ------------------------------------------------------------------------------------------------ ov255 PC

PC_SIZE_OLD, PC_SIZE = 0xA5BC, 0xA5C8
PC_FCHAR, PC_FACT, PC_FLAG = 0xA5BC, 0xA5C0, 0xA5C4       # Fairy's char resource, cell actor, "char loaded" flag
PC_CHARS, PC_ACTORS = 0xA0DC, 0x9E98                      # the PC's char table (0x81) and actor slots (0x91)
PC_FCHAR_IDX = (PC_FCHAR - PC_CHARS) // 4                 # 0x138: a char index that lands on PC_FCHAR
PC_VSLOT = (PC_FACT - PC_ACTORS) // 4                     # 0x1ca: an actor slot that lands on PC_FACT
F = dict(load_char=0x0204B81C, free_char=0x0204B98C, pal_row=0x0202D7E8, cell_59=0x0202D7F8, set_pal=0x0204C378,
         pc_make_actor=0x021CF51C, pc_set_vis=0x021CF63C, pc_del_slot=0x021CF570)

def pc_thunks(t):
    """ov255 helpers (Thumb, called with bl from the patched sites; each keeps the registers its site needs)."""
    # func_ov255_021d07d0, after the 17 type-icon loads (r5 = work, r6 = a/0/8/2 handle, r7 = heap 0x4c), in place of
    # `bl func_0202d7f8` (r0 = 2): load icon 51 (Fairy) like the loop does, then that call.
    t.label('PcLoadFairyChar')
    t.a('push {r3, lr}\nsub sp, #0x8\nstr r7, [sp, #0x0]\nadds r0, r6, #0x0\nmovs r1, #0x33\nmovs r2, #0x0\nmovs r3, #0x1')
    t.bl(F['load_char'])
    t.ldr_lit(1, 'pc_fchar'); t.a('str r0, [r5, r1]\nmovs r0, #0x1'); t.ldr_lit(1, 'pc_flag'); t.a('str r0, [r5, r1]')
    t.a('add sp, #0x8\nmovs r0, #0x2'); t.bl(F['cell_59']); t.a('pop {r3, pc}')
    # func_ov255_021d0978's epilogue (r5 = work, r7 = sp = its 24-byte actor params, [+8] = char index): one more
    # iteration of its loop for Fairy (char index PC_FCHAR_IDX, actor at PC_FACT = slot PC_VSLOT), then the epilogue.
    t.label('PcMakeFairyActor')
    t.ldr_lit(0, 'pc_fchar_idx'); t.a('str r0, [r7, #0x8]\nadds r0, r5, #0x0\nadds r1, r7, #0x0'); t.bl(F['pc_make_actor'])
    t.ldr_lit(1, 'pc_fact'); t.a('str r0, [r5, r1]\nmovs r0, #0x11'); t.bl(F['pal_row'])
    t.a('adds r1, r0, #0x0'); t.ldr_lit(0, 'pc_fact'); t.a('ldr r0, [r5, r0]\nmovs r2, #0x1'); t.bl(F['set_pal'])
    t.a('adds r0, r5, #0x0'); t.ldr_lit(1, 'pc_vslot'); t.a('movs r2, #0x0'); t.bl(F['pc_set_vis'])
    t.a('add sp, #0x18\npop {r3, r4, r5, r6, r7, pc}')
    # func_ov255_021d09dc (show type1 r6 / type2 r4): slot = type + 0x20, Fairy's = PC_VSLOT (r0-r2 kept)
    t.label('PcTypeSlotR7'); t.a('adds r7, r6, #0x0\ncmp r7, #0x11'); t.beq('pc_r7f'); t.a('adds r7, #0x20\nbx lr')
    t.label('pc_r7f'); t.ldr_lit(7, 'pc_vslot'); t.a('bx lr')
    t.label('PcTypeSlotR4'); t.a('adds r0, r5, #0x0\ncmp r4, #0x11'); t.beq('pc_r4f'); t.a('adds r4, #0x20\nbx lr')
    t.label('pc_r4f'); t.ldr_lit(4, 'pc_vslot'); t.a('bx lr')
    # the two loops that hide slots 0x20..0x30: func_ov255_021cf63c(work, slot, vis), and Fairy's after slot 0x30
    t.label('PcSetTypeVis')
    t.a('push {r4, r5, r6, lr}\nadds r4, r0, #0x0\nadds r5, r1, #0x0\nadds r6, r2, #0x0'); t.bl(F['pc_set_vis'])
    t.a('cmp r5, #0x30'); t.bne('pc_vis_done')
    t.a('adds r0, r4, #0x0'); t.ldr_lit(1, 'pc_vslot'); t.a('adds r2, r6, #0x0'); t.bl(F['pc_set_vis'])
    t.label('pc_vis_done'); t.a('pop {r4, r5, r6, pc}')
    # func_ov255_021cf488 after its char-table free loop (r5 = work), in place of `movs r4, #0; ldr r7, =0xa4e4`
    t.label('PcFreeFairyChar')
    t.a('push {r3, lr}'); t.ldr_lit(1, 'pc_flag'); t.a('ldr r0, [r5, r1]\ncmp r0, #0x0'); t.beq('pc_free_done')
    t.a('movs r0, #0x0\nstr r0, [r5, r1]'); t.ldr_lit(1, 'pc_fchar'); t.a('ldr r0, [r5, r1]'); t.bl(F['free_char'])
    t.label('pc_free_done'); t.a('movs r4, #0x0'); t.ldr_lit(7, 'pc_a4e4'); t.a('pop {r3, pc}')
    # func_ov255_021cf58c after deleting slots 0..0x90 (r4 = work), in place of `ldr r0, =0x9e94; ldr r0, [r4, r0]`
    t.label('PcDeleteFairyActor')
    t.a('push {r3, lr}\nadds r0, r4, #0x0'); t.ldr_lit(1, 'pc_vslot'); t.bl(F['pc_del_slot'])
    t.ldr_lit(0, 'pc_9e94'); t.a('ldr r0, [r4, r0]\npop {r3, pc}')
    for name, v in (('pc_fchar', PC_FCHAR), ('pc_fact', PC_FACT), ('pc_flag', PC_FLAG), ('pc_fchar_idx', PC_FCHAR_IDX),
                    ('pc_vslot', PC_VSLOT), ('pc_a4e4', 0xA4E4), ('pc_9e94', 0x9E94)):
        t.word(name, v)

def pc(code, sym):
    """ov255 (PC boxes, the type icons of the Pokémon under the cursor). Work struct 0xa5bc B (GFL_HeapAllocate(0x4c,
    0xa5bc, clear) in the PC's init, literal .L_021c2a10). Char resources: a table of 0x81 at +0xa0dc (type icons =
    indices 0x63-0x73 at +0xa268, index 0x74 is a box icon). Cell actors: 0x91 slots at +0x9e98 (types = slots
    0x20-0x30, slot 0x31 is the first box icon; func_ov255_021cf58c deletes all 0x91, the char table follows at
    +0xa0dc). Both tables are full, so Fairy gets its own fields after the struct: +0xa5bc char (= char index 0x138),
    +0xa5c0 actor (= slot 0x1ca: every slot helper of the PC takes it as is), +0xa5c4 flag; struct 0xa5c8 B."""
    m = Module(code, 255)
    m.word(0x021C2A10, PC_SIZE_OLD, PC_SIZE)                                     # the work struct's size (one use)
    # one more cell actor in the PC's unit (func_ov255_021cf4e8: func_0204bf1c(0xe9, 0, 0x4c))
    m.patch('func_ov255_021cf4e8', 'movs r0, #0xe9\nmovs r1, #0x0\nmovs r2, #0x4c', 'movs r0, #0xea\nmovs r1, #0x0\nmovs r2, #0x4c')
    # icon load (func_ov255_021d07d0): after the loop of 17, Fairy's icon
    m.patch('func_ov255_021d07d0', f'movs r0, #0x2\nbl ={F["cell_59"]:#x}\nadds r4, r0, #0x0',
            lambda a: asm('movs r0, #0x2') + bl(a + 2, sym['PcLoadFairyChar']) + asm('adds r4, r0, #0x0'))
    # actor creation (func_ov255_021d0978): its epilogue makes Fairy's actor too
    m.patch('func_ov255_021d0978', 'add sp, #0x18\npop {r3, r4, r5, r6, r7, pc}', lambda a: bl(a, sym['PcMakeFairyActor']))
    # show (func_ov255_021d09dc): the two slot computations
    m.patch('func_ov255_021d09dc', 'adds r7, r6, #0x0\nadds r7, #0x20', lambda a: bl(a, sym['PcTypeSlotR7']))
    m.patch('func_ov255_021d09dc', 'adds r4, #0x20\nadds r0, r5, #0x0', lambda a: bl(a, sym['PcTypeSlotR4']))
    # the hide loops over slots 0x20-0x30
    for f in ('func_ov255_021d0a28', 'func_ov255_021bf288'):
        m.patch(f, f'adds r2, r6, #0x0\nbl ={F["pc_set_vis"]:#x}\nadds r4, r4, #0x1\ncmp r4, #0x31',
                lambda a: asm('adds r2, r6, #0x0') + bl(a + 2, sym['PcSetTypeVis']) + asm('adds r4, r4, #0x1\ncmp r4, #0x31'))
    # frees: Fairy's char after the char table's loop, Fairy's actor after the slots' loop
    m.patch('func_ov255_021cf488', 'movs r4, #0x0\nldr r7, =0x021cf4e0', lambda a: bl(a, sym['PcFreeFairyChar']))
    m.patch('func_ov255_021cf58c', 'ldr r0, =0x021cf5ac\nldr r0, [r4, r0]', lambda a: bl(a, sym['PcDeleteFairyActor']))
    m.save()
    return f'ov255 PC: struct {PC_SIZE_OLD:#x} -> {PC_SIZE:#x}, Fairy char +{PC_FCHAR:#x} (index {PC_FCHAR_IDX:#x}), actor +{PC_FACT:#x} (slot {PC_VSLOT:#x}) ({len(m.log)} sites)'

# ------------------------------------------------------------------------------------------------ ov296 Pokédex entry

DEX_SIZE_OLD, DEX_SIZE = 0x2B4, 0x328
DEX_ACTORS = 0x2E0                     # 0xb8 << 2 = 0x170 << 1: reachable in one instruction from the old constants
DEX_SHEET_TABLE = 0x0219FAC8           # data_ov296_0219fac8: (row, col) of each type in the foreign-language sheets
DEX_SHEETS = (19, 20, 21, 22, 23, 24)  # a/1/5/7: FR, DE, IT, JA, KO, ES type sheets (256x256, cells 32x16)
DEX_FAIRY_CELL = (5, 3)                # the one free cell of every sheet (row 5 has the three contest cells 0-2)

def dex(code):
    """ov296 (Pokédex entry). Work struct 0x2b4 B (GFL_HeapAllocate + memset in func_ov296_0219d768, size in r5).
    English mode (preloaded, flag +0xe4): 17 char resources at +0xe8, 17 cell actors at +0x12c, then the two shown
    types as bytes at +0x170/+0x171 (17 = none). Actor index 17 would be those bytes. New: actors at +0x2e0 (x18,
    struct 0x328 B); the chars grow in place to 18 (+0x12c, the old actor 0, is now free); 'none' = 18.
    Other languages (modes 0-5): the icon is cut from a sheet by data_ov296_0219fac8[type] = (row, col); [17] is the
    table's 2 bytes of alignment padding: Fairy's cell (5, 3)."""
    m = Module(code, 296)
    A = DEX_ACTORS >> 2                                                         # 0xb8
    # struct size (alloc + memset): 0xad << 2 -> 0xca << 2
    m.patch('func_ov296_0219d768', 'movs r5, #0xad\nstr r3, [sp, #0x14]', 'movs r5, #0xca\nstr r3, [sp, #0x14]')
    f = 'func_ov296_0219ec08'                                                   # create
    m.patch(f, 'movs r1, #0x11\nstr r0, [sp, #0x14]\nstrb r1, [r5, r0]', 'movs r1, #0x12\nstr r0, [sp, #0x14]\nstrb r1, [r5, r0]')
    for slot in (0x24, 0x20, 0x1c, 0x18):                                       # actor base 0x170 - 0x44 -> 0x170 << 1
        m.patch(f, f'str r0, [sp, #{slot:#x}]\nsubs r0, #0x44\nstr r0, [sp, #{slot:#x}]',
                f'str r0, [sp, #{slot:#x}]\nlsls r0, r0, #0x1\nstr r0, [sp, #{slot:#x}]')
    m.patch(f, 'ldr r0, [sp, #0x14]\nsubs r0, #0x44\nstr r0, [sp, #0x14]', 'ldr r0, [sp, #0x14]\nlsls r0, r0, #0x1\nstr r0, [sp, #0x14]')
    m.patch(f, 'lsrs r6, r0, #0x18\ncmp r6, #0x11', 'lsrs r6, r0, #0x18\ncmp r6, #0x12')
    f = 'func_ov296_0219ed84'                                                   # free
    m.patch(f, 'movs r7, #0x4b\nmovs r4, #0x0\nlsls r7, r7, #0x2', f'movs r7, #{A:#x}\nmovs r4, #0x0\nlsls r7, r7, #0x2')
    m.patch(f, 'lsrs r4, r0, #0x18\ncmp r4, #0x11', 'lsrs r4, r0, #0x18\ncmp r4, #0x12')
    at = m.find('func_ov296_0219ede4', 'movs r2, #0x11\ncmp r6, #0x6')      # type2 = none when type1 == type2
    m.d[at - m.base:at + 2 - m.base] = asm('movs r2, #0x12'); m.log.append(at)
    f = 'func_ov296_0219ee38'                                                   # show (English mode + other path)
    m.patch(f, 'str r1, [sp, #0x18]\ncmp r0, #0x11', 'str r1, [sp, #0x18]\ncmp r0, #0x12')
    m.patch(f, 'ldr r0, [sp, #0x18]\nadds r0, #0x5c\nldr r0, [r1, r0]', f'movs r0, #{A:#x}\nlsls r0, r0, #0x2\nldr r0, [r1, r0]')
    m.patch(f, 'ldr r0, [sp, #0x18]\nmovs r1, #0x11\nadds r0, #0xa0', 'ldr r0, [sp, #0x18]\nmovs r1, #0x12\nadds r0, #0xa0')
    hits, _ = m.find_all(f, 'movs r0, #0x4b\nlsls r0, r0, #0x2\nldr r0, [r1, r0]')
    assert len(hits) == 2, hits
    for a in hits: m.d[a - m.base:a + 2 - m.base] = asm(f'movs r0, #{A:#x}'); m.log.append(a)
    m.patch(f, 'ldrb r1, [r5, r0]\nsubs r0, #0x44\nlsls r1, r1, #0x2', 'ldrb r1, [r5, r0]\nlsls r0, r0, #0x1\nlsls r1, r1, #0x2')
    lit = 0x0219F09C                                                            # .L_0219f09c: .word 0x171
    m.patch(f, f'ldr r0, ={lit:#x}\nldrb r0, [r5, r0]\ncmp r0, #0x11',
            lambda a: m.d[a - m.base:a + 2 - m.base] + asm('ldrb r0, [r5, r0]\ncmp r0, #0x12'))
    m.patch(f, f'ldr r0, ={lit:#x}\nsubs r0, #0x45\nldr r0, [r1, r0]', lambda a: asm(f'movs r0, #{A:#x}\nlsls r0, r0, #0x2\nldr r0, [r1, r0]'))
    m.patch(f, f'ldr r0, ={lit:#x}\nmovs r1, #0x11\nstrb r1, [r5, r0]', lambda a: m.d[a - m.base:a + 2 - m.base] + asm('movs r1, #0x12\nstrb r1, [r5, r0]'))
    m.patch(f, f'ldr r0, ={lit:#x}\nldrb r1, [r5, r0]\nsubs r0, #0x45\nlsls r1, r1, #0x2\nadds r1, r5, r1\nldr r0, [r1, r0]',
            lambda a: m.d[a - m.base:a + 2 - m.base] + asm(f'ldrb r1, [r5, r0]\nadds r1, #{A:#x}\nlsls r1, r1, #0x2\nadds r1, r5, r1\nldr r0, [r1, #0x0]'))
    at = m.find(f, 'movs r0, #0x17\nlsls r0, r0, #0x4\nstr r0, [sp, #0x20]') - 4   # cmp r4, #0x11 ; beq
    assert bytes(m.d[at - m.base:at + 2 - m.base]) == asm('cmp r4, #0x11'); m.d[at - m.base:at + 2 - m.base] = asm('cmp r4, #0x12'); m.log.append(at)
    hits, _ = m.find_all(f, 'ldr r0, [sp, #0x20]\nsubs r0, #0x44')
    assert len(hits) == 2, hits
    for a in hits: m.d[a + 2 - m.base:a + 4 - m.base] = asm('lsls r0, r0, #0x1'); m.log.append(a + 2)
    at = m.find(f, f'ldr r4, ={lit:#x}\nstrb r6, [r5, r4]') - 4                  # cmp r6, #0x11 ; bne ; b
    assert bytes(m.d[at - 2 - m.base:at - m.base]) == asm('cmp r6, #0x11'); m.d[at - 2 - m.base:at - m.base] = asm('cmp r6, #0x12'); m.log.append(at - 2)
    m.patch(f, 'adds r0, r4, #0x0\nsubs r0, #0x45\nldr r0, [r1, r0]', f'movs r0, #{A:#x}\nlsls r0, r0, #0x2\nldr r0, [r1, r0]')
    m.patch(f, 'lsls r0, r0, #0x2\nadds r0, r5, r0\nsubs r4, #0x45\nldr r0, [r0, r4]',
            f'adds r0, #{A:#x}\nlsls r0, r0, #0x2\nadds r0, r5, r0\nldr r0, [r0, #0x0]')
    m.patch(f, 'ldrb r0, [r0, r6]\ncmp r0, #0x11', 'ldrb r0, [r0, r6]\ncmp r0, #0x12')        # the other path (2 icons)
    f = 'func_ov296_0219f0a0'                                                   # other languages
    m.patch(f, 'str r0, [sp, #0x14]\ncmp r0, #0x11', 'str r0, [sp, #0x14]\ncmp r0, #0x12')
    f = 'func_ov296_0219f6ac'                                                   # visibility
    m.patch(f, 'ldrb r0, [r5, r0]\ncmp r0, #0x11', 'ldrb r0, [r5, r0]\ncmp r0, #0x12')
    m.patch(f, 'lsls r0, r0, #0x2\nadds r0, r5, r0\nsubs r4, #0x64\nldr r0, [r0, r4]',
            f'adds r0, #{A:#x}\nlsls r0, r0, #0x2\nadds r0, r5, r0\nldr r0, [r0, #0x0]')
    m.patch(f, 'ldrb r1, [r5, r0]\ncmp r1, #0x11', 'ldrb r1, [r5, r0]\ncmp r1, #0x12')
    m.patch(f, 'lsls r1, r1, #0x2\nadds r1, r5, r1\nsubs r0, #0x45\nldr r0, [r1, r0]',
            f'adds r1, #{A:#x}\nlsls r1, r1, #0x2\nadds r1, r5, r1\nldr r0, [r1, #0x0]')
    # foreign-language sheets: Fairy's cell in the table's padding
    o = DEX_SHEET_TABLE + 2 * TYPE_FAIRY - m.base
    assert bytes(m.d[o:o + 2]) == b'\0\0' and DEX_SHEET_TABLE + 36 == 0x0219FAEC
    m.d[o:o + 2] = bytes(DEX_FAIRY_CELL); m.log.append(o + m.base)
    m.save()
    return f'ov296 Pokédex entry: struct {DEX_SIZE_OLD:#x} -> {DEX_SIZE:#x}, actors +{DEX_ACTORS:#x} x18, chars +0xe8 x18, none = 18 ({len(m.log)} sites)'

# ------------------------------------------------------------------------------------------------ ov300 Pokédex search

DEX_SEARCH_LABELS = 0x021A40AE           # data_ov300_021a40ae: message (text 0479) of each type in the type list
FAIRY_LABEL_MSG = 77                     # text 0479 line 77 "Fairy" (src/text/overrides_fairy_ui.json; blank in Black 2)

def fairy_symbol(code, name):
    """An ITCM function of fairy.py (it writes <code>/fairy_symbols.json, Thumb addresses |1); None when fairy.py is not
    in this build."""
    import json
    p = os.path.join(code, 'fairy_symbols.json')
    if not os.path.exists(p): return None
    v = json.load(open(p))[name]
    return (int(v, 0) if isinstance(v, str) else v) & ~1

def dex_search(code, sym):
    """ov300 (Pokédex search). The type list (func_ov300_021a3d04) adds entries 0..16 (`cmp r4, #0x10; bls`), each
    labelled by data_ov300_021a40ae[i]; the chosen entry's index is the type stored in the search conditions
    (func_ov300_021a1b10 through func_ov300_021a086c = identity; 0xff = none) and ov302's search compares it with the
    species' types, so entry 17 = Fairy works as it is. The label table holds 18 u16 ([17] = message 48 '-', read by
    nothing) + 2 bytes of padding. The item texts go to +0x1e4 + 4*i, an array of 50 (func_ov300_021a3ed0 frees 0x32),
    so an 18th fits. The list has 18 entries only while the Fairy toggle is on (Fairy_IsOn)."""
    m = Module(code, 300)
    o = DEX_SEARCH_LABELS + 2 * TYPE_FAIRY - m.base
    assert struct.unpack_from('<H', m.d, o)[0] == 0x30
    struct.pack_into('<H', m.d, o, FAIRY_LABEL_MSG); m.log.append(o + m.base)
    m.patch('func_ov300_021a3d04', 'str r0, [r1, r7]\ncmp r4, #0x10', lambda a: bl(a, sym['DexTypeListCmp']))
    m.save()
    return f'ov300 Pokédex search: type list 17 + Fairy_IsOn(), label [17] = text 0479 line {FAIRY_LABEL_MSG}'

# ------------------------------------------------------------------------------------------------ ov142 Bag

def bag(code, sym):
    """ov142 (Bag, the TM/HM move type icon). Work struct 0x1f54 B (GFL_ProcInitSubsystem in func_ov142_0219c444; its
    literal 0x1f54 also addresses the last field +0x1f50, so it stays and two thunks pass the new size). 17 type char
    resources at +0x5ac (0x54c + 0x60) and 17 cell actors at +0x6e0 (0x6ac + 0x34), followed by +0x5f0.. (palette,
    cell, category chars) and +0x724.. (used everywhere). New: struct 0x2008 B, chars at +0x1f60, actors at +0x1fc0,
    18 each. Accesses (constscan.py, literals included): load loop, actor creation, two show sites, two hide loops.
    The Bag frees them with the whole cell system (func_0204bf98 / func_0204b758), no per-type free loop."""
    m = Module(code, 142)
    f = 'func_ov142_0219c444'
    lit = 0x0219C690                                               # .L_0219c690: .word 0x1f54
    assert struct.unpack_from('<I', m.d, lit - m.base)[0] == BAG_SIZE_OLD
    m.patch(f, f'ldr r1, ={lit:#x}\nadds r0, r4, #0x0\nmovs r2, #0xe', lambda at: bl(at, sym['BagInitArgs']) + asm('movs r2, #0xe'))
    m.patch(f, f'ldr r2, ={lit:#x}\nmovs r1, #0x0\nadds r4, r0, #0x0', lambda at: bl(at, sym['BagMemsetArgs']) + asm('adds r4, r0, #0x0'))
    f = 'func_ov142_0219d7a8'
    # the cell-actor unit holds exactly the Bag's actors (func_0204bf1c(0x36, ...)): one more for Fairy's
    # (else switching pockets asserts in func_0204cf00: no free actor; tested)
    m.patch(f, 'movs r0, #0x36\nldrh r2, [r4, r2]\nmovs r1, #0x0', 'movs r0, #0x37\nldrh r2, [r4, r2]\nmovs r1, #0x0')
    # load loop: r6 = 0x54c (.L_0219db34) + 0x60 -> 0xfb << 5; 17 -> 18 icons
    m.patch(f, 'ldr r6, =0x0219db34\nmovs r7, #0x0\nadds r6, #0x60',
            f'movs r6, #{BAG_CHARS >> 5:#x}\nmovs r7, #0x0\nlsls r6, r6, #0x5')
    m.patch(f, 'str r0, [r1, r6]\ncmp r5, #0x11', 'str r0, [r1, r6]\ncmp r5, #0x12')
    # actor creation: [sp+0x44] = 0x54c + 0x60 = chars; r7 = 0x6ac + 0x34 and [sp+0x38], [sp+0x34], [sp+0x30] = actors
    m.patch(f, 'ldr r0, =0x0219dd0c\nldr r7, =0x0219dd10\nstr r0, [sp, #0x44]\nadds r0, #0x60\nstr r0, [sp, #0x44]',
            f'movs r0, #{BAG_CHARS >> 5:#x}\nmovs r7, #{BAG_ACTORS >> 5:#x}\nlsls r0, r0, #0x5\nlsls r7, r7, #0x5\nstr r0, [sp, #0x44]')
    m.patch(f, 'adds r7, #0x34\nstr r0, [sp, #0x3c]', 'adds r7, #0x0\nstr r0, [sp, #0x3c]')
    for slot in (0x38, 0x34, 0x30):
        m.patch(f, f'ldr r0, =0x0219dd10\nstr r0, [sp, #{slot:#x}]\nadds r0, #0x34\nstr r0, [sp, #{slot:#x}]',
                f'movs r0, #{BAG_ACTORS >> 5:#x}\nstr r0, [sp, #{slot:#x}]\nlsls r0, r0, #0x5\nstr r0, [sp, #{slot:#x}]')
    m.patch(f, 'adds r6, r6, #0x1\ncmp r6, #0x11', 'adds r6, r6, #0x1\ncmp r6, #0x12')
    # show the TM's type (func_ov142_0219dda0): adds r4, #0xc ; ldr r0, [r0, r4] -> bl BagTypeActor
    m.patch('func_ov142_0219dda0', 'adds r4, #0xc\nldr r0, [r0, r4]', lambda at: bl(at, sym['BagTypeActor']))
    # show (func_ov142_0219f4b0): r0 = r7 (0x74c) - 0x6c -> 0xfe << 5
    m.patch('func_ov142_0219f4b0', 'adds r0, r7, #0x0\nsubs r0, #0x6c', f'movs r0, #{BAG_ACTORS >> 5:#x}\nlsls r0, r0, #0x5')
    # hide loops: 0x6e << 4 -> 0xfe << 5; 17 -> 18
    m.patch('func_ov142_0219de0c', 'movs r6, #0x6e\nlsls r6, r6, #0x4', f'movs r6, #{BAG_ACTORS >> 5:#x}\nlsls r6, r6, #0x5')
    m.patch('func_ov142_0219de0c', 'adds r4, r4, #0x1\ncmp r4, #0x11', 'adds r4, r4, #0x1\ncmp r4, #0x12')
    m.patch('func_ov142_0219e120', 'movs r4, #0x6e\nmovs r7, #0x0\nlsls r4, r4, #0x4',
            f'movs r4, #{BAG_ACTORS >> 5:#x}\nmovs r7, #0x0\nlsls r4, r4, #0x5')
    m.patch('func_ov142_0219e120', 'adds r5, r5, #0x1\ncmp r5, #0x11', 'adds r5, r5, #0x1\ncmp r5, #0x12')
    m.save()
    return f'ov142 Bag: struct {BAG_SIZE_OLD:#x} -> {BAG_SIZE:#x}, type chars +{BAG_CHARS:#x}, actors +{BAG_ACTORS:#x} x18 ({len(m.log)} sites)'

# ------------------------------------------------------------------------------------------------ ov168 battle

def battle(code, sym):
    """ov168 func_ov168_021ed81c (touch-screen move buttons): palette file = data_ov168_021f3864[type] (17 u32; index
    17 would read the next table, data_ov168_021f38a8[0] = 0). Its one literal now points at an 18-entry copy in
    ITCM; the button's type icon is read by type (func_0202d7f4) and needs nothing."""
    m = Module(code, 168)
    start, size = m.funcs['func_ov168_021ed81c']
    hits = [a for a in range(start, start + size + 0x100, 4)
            if struct.unpack_from('<I', m.d, a - m.base)[0] == BUTTON_PAL_TABLE]
    assert len(hits) == 1, hits
    m.word(hits[0], BUTTON_PAL_TABLE, sym['ButtonPalettes'])
    m.save()
    return f'ov168 buttons: palette table -> {sym["ButtonPalettes"]:#x} (18)'

def hof(code, sym):
    """ov265 (Hall of Fame). The Pokémon's type 1 (work +0x915a, PokeParty_GetParam 0xae) picks a particle file
    (func_ov265_02199f3c, literal .L_02199f74 -> data_ov265_0219b8cc) and a palette file (func_ov265_0219af14,
    literal .L_0219af58 -> data_ov265_0219ba98, the last data of the overlay) from 17-entry tables: index 17 read the
    next table's function pointer / past the overlay (tested: 'An error has occurred' on a Fairy Pokémon). Both
    literals now point at 18-entry copies in ITCM."""
    m = Module(code, 265)
    m.word(0x02199F74, HOF_PARTICLE_TABLE, sym['HofParticles'])
    m.word(0x0219AF58, HOF_PALETTE_TABLE, sym['HofPalettes'])
    m.save()
    return f'ov265 Hall of Fame: particle/palette tables -> {sym["HofParticles"]:#x}/{sym["HofPalettes"]:#x} (18)'

def apply_code(code):
    out = []
    p = os.path.join(code, 'arm9.bin')
    d = bytearray(open(p, 'rb').read())
    o = TYPE_PAL_ROWS - ARM9 + TYPE_FAIRY
    assert d[o] == 0, f'arm9 {TYPE_PAL_ROWS + TYPE_FAIRY:#x} = {d[o]}'
    d[o] = 2                                     # Fairy's icon uses palette row 2 (colours 8/9 are its pinks)
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)
    out.append('arm9 type palette row[17] = 2')
    out.append(summary(code))
    vanilla = struct.unpack('<17I', open(os.path.join(code, 'arm9_ov168.bin'), 'rb').read()[
        BUTTON_PAL_TABLE - ov_base(168):BUTTON_PAL_TABLE - ov_base(168) + 68])
    fairy_on = fairy_symbol(code, 'Fairy_IsOn')
    d265 = open(os.path.join(code, 'arm9_ov265.bin'), 'rb').read()
    hof_tables = [struct.unpack_from('<17I', d265, a - ov_base(265)) for a in (HOF_PARTICLE_TABLE, HOF_PALETTE_TABLE)]
    base, n, sym = install_itcm(code, lambda b: itcm_blob(b, vanilla, hof_tables, fairy_on))
    out.append(f'ITCM {n} B at {base:#x}')
    out.append(bag(code, sym))
    out.append(pc(code, sym))
    out.append(dex(code))
    out.append(dex_search(code, sym))
    if fairy_on is None: out.append('(no fairy.py: Fairy_IsOn stub)')
    out.append(battle(code, sym))
    out.append(hof(code, sym))
    return '; '.join(out)
