"""Real TMs for the Gen 3 TM moves Black 2 has no TM for (new_tms, 2026-10-18; notes/RESUME.md item 16). Before this,
those gifts gave the closest Black 2 TM (item 15b). Now TM96-TM104 teach Focus Punch, Water Pulse, Bullet Seed, Giga
Drain, Iron Tail, Shock Wave, Secret Power, Steel Wing and Skill Swap (Gen 3 order: TM01, 03, 09, 19, 23, 34, 43, 47,
48). Snatch (Gen 3 TM49) is given nowhere we build (SS Tidal), so it has no TM yet (one more free id, 129, would do).

What Black 2 has [decomp: external/pokebw2_new src/system/pml_item.c, myitem_savedata.c, poke_tool.c, ov142 itemmenu*.c;
caller list: config/b2_us/**/relocs.txt]:
  - Items: ids 0-638 (ITEM_LAST); every table is sized by it. Ids above 638 are cut to 0 in about 30 places (FAIRY_SCOPE
    3.3), so the new TMs take unused ids: 113-115, 120-133 and 426-427 are "???" (zero data, "?" icon); Fairy has 113/114.
    TM96-TM104 = ids 120-128.
  - TM01-TM92 = items 328-419, HM01-06 = 420-425, TM93-95 = 618-620. Four arm9 functions know these ranges:
    PML_ItemIsTMHM 0x02026a94, PML_ItemIsTM 0x02026abc, PML_ItemGetTMWazaID 0x02026ae4 (TM_MOVE_LIST 0x02090c84: 101
    moves + 0) and PML_ItemGetTMBitMask 0x02026b40 (the personal-data bit: TM01-92 = 0-91, TM93-95 = 92-94, HM01-06 =
    95-100). Every TM user calls them: the Bag (ov142), the Pokemon list's TM teaching (ov165 plist_sys.c: the move and
    the "ABLE" check canPkmLearnTM_Wrapper 0x0201d8dc), the field scripts (ov036: item-get message move name, shops,
    random owned TM), the day care (ov036 inheritTmMoves 0x021be4b4) and the bag save (PML_ItemGetMaxStorageCount: 1).
  - Compatibility: personal data a/0/1/6, 4 words at +0x28 (machines[4] = 128 bits, 101 used). canPkmLearnTM tests
    word bit/32, bit bit%32: no limit, so bits 101-127 work as they are.
  - Pocket: ITEM_CATEGORIES 0x0208f4d0 (u8 per item; 2 = TMs & HMs). The Bag sends any item of the TM pocket to its TM
    flow ("Booted up a TM ... teach?", then the party list). The pocket holds 109 (BAG_TMS_HMS_MAX): Black 2's 101 + 9
    = 110 > 109, but Hoenn gives far fewer than 101 of Black 2's TMs (about 60), so it never fills.
  - The Bag shows a TM row as its move name with the TM mark (any TMBitMask != 0xff) and, below, message 69 "No. N
    <move>" with N = TMBitMask + 1 in 2 zero-padded digits (100 would print "?0"); its sort by number sorts by TMBitMask
    (HMs 95-100 would come before TM96).
  - Item data a/0/2/4 (36 B): TMs = price 1000 (x10 = 10000), +8 0x013f (no Give/Toss, field pocket 2), +0xA field use 6,
    +0xF sort index = TMBitMask. Icons ITEM_GRAPHICS_CHARS_AND_PALETTES 0x02090d50 {char, palette}: the TM disc 397 with
    one palette per move type. Dummy/unholdable bit tables 0x02090a48 / 0x02090a98 (20 words each).
  - Text: item names 0064, names with article 0481, plurals 0482, descriptions 0063 (a TM's = its move's, 0402).
What this patch does:
  apply (data):   a/0/2/4 items 120-128 = TM01's data, sort index 101-109; a/0/1/6 bits 101-109 for every species:
                  Gen 1-3 species from the Gen 3 learnsets (pokeruby, Emerald: pokeemerald; the same for these moves),
                  Gen 4-5 species (no Gen 3 learnset) from Black 2's closest data (PROXY below: Black 2's own tutors
                  for Iron Tail / Giga Drain / Skill Swap, a close TM or tutor otherwise); forms as their own record
                  (Deoxys's and Castform's forms: the Gen 3 species).
  apply_code:     ITCM: new_tms.c (the four functions, the Bag's number and sort key, a 3-digit WordSetNumber);
                  arm9: long jumps at the four functions; ITEM_CATEGORIES 120-128 -> 2; their dummy bits cleared and
                  unholdable bits set; icons (397, the move type's TM palette);
                  ov142: 0x0219dfa4 bl GetTMBitMask -> NewTm_BagNumber, 0x0219dfe0 bl WordSetNumber ->
                  NewTm_WordSetNumber (the "No. N" line), 0x0219ba36 bl GetTMBitMask -> NewTm_SortKey (sort by number);
                  ov036: the day care's TM-move loop starts at item 120 instead of 328 (0x021be4e2: movs r4, #82 ->
                  #120; 0x021be4e6: lsls r4, r4, #2 -> #0), so a father's TM96+ move passes to the egg as Black 2's do.
  Text: src/text/overrides_new_tms.json (`python3 new_tms.py --text` writes it; apply checks it is current).
  Scripts: src/include/hoenn_tms.h (ITEM_TM96 ...; apply checks it), the six gifts and converter/gen_items.py.
Not changed: shops (none sells these; their "TM N" line would show item - 327), Black 2's script command 0x2D4 (counts
TM01-TM95 only; no Hoenn script uses it). Savestates made before need a cold boot (ITCM code)."""
import os, re, sys, json, struct, subprocess, tempfile, importlib.util, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
VANILLA_FILES = os.path.join(DECOMP, 'build', 'b2_us', 'files')
VANILLA_CODE = os.path.join(DECOMP, 'build', 'b2_us', 'build')
sys.path.insert(0, os.path.dirname(HERE))
import narcio  # noqa: E402
import version  # noqa: E402

LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9, ITCM_END = 0x01FF8000, 0x0207B400, 0x02004000, 0x02000000
OV036, OV142 = 0x0217F600, 0x021998C0

# (TM number, item id, move, Gen 3 TM); the item ids are Black 2's unused 120-128
NEW_TMS = [(96, 120, 'MOVE_FOCUS_PUNCH', 'TM01'), (97, 121, 'MOVE_WATER_PULSE', 'TM03'),
           (98, 122, 'MOVE_BULLET_SEED', 'TM09'), (99, 123, 'MOVE_GIGA_DRAIN', 'TM19'),
           (100, 124, 'MOVE_IRON_TAIL', 'TM23'), (101, 125, 'MOVE_SHOCK_WAVE', 'TM34'),
           (102, 126, 'MOVE_SECRET_POWER', 'TM43'), (103, 127, 'MOVE_STEEL_WING', 'TM47'),
           (104, 128, 'MOVE_SKILL_SWAP', 'TM48')]
FIRST_ITEM, FIRST_BIT = NEW_TMS[0][1], 101            # personal-data bits 101-109 (Black 2 uses 0-100)
assert [it for _, it, _, _ in NEW_TMS] == list(range(FIRST_ITEM, FIRST_ITEM + len(NEW_TMS)))
ITEM_TM01, TEMPLATE = 328, 328                         # the new items copy TM01's data (price, pocket, field use)
POCKET_TMS = 2
TM_CHAR, DUMMY_ICON = 397, (1021, 1022)

# Gen 4-5 species have no Gen 3 learnset: they follow Black 2's closest data. ('tm', n) = Black 2 TMn, ('hm', n),
# ('tutor', t, bit) = Black 2's paid tutor t (0 Driftveil, 1 Lentimas, 2 Humilau, 3 Nacrene: pokebw2_new scrcmd_shop.c
# MOVE_TUTOR_ITEMS_*): personal word +0x3c + 4t, bit = the move's place in that array (checked: Pikachu has Covet,
# Signal Beam, ThunderPunch, Magnet Rise, Iron Tail, Helping Hand, Sleep Talk; Alakazam Trick ... Skill Swap)
PROXY = {'MOVE_FOCUS_PUNCH': ('tm', 52),               # Focus Blast
         'MOVE_WATER_PULSE': ('tm', 55),               # Scald
         'MOVE_BULLET_SEED': ('tutor', 0, 6),          # Seed Bomb
         'MOVE_GIGA_DRAIN': ('tutor', 2, 10),           # Giga Drain (Black 2 tutor)
         'MOVE_IRON_TAIL': ('tutor', 1, 16),           # Iron Tail (Black 2 tutor)
         'MOVE_SHOCK_WAVE': ('tm', 57),                # Charge Beam
         'MOVE_SECRET_POWER': ('tm', 27),              # Return
         'MOVE_STEEL_WING': ('hm', 2),                 # Fly
         'MOVE_SKILL_SWAP': ('tutor', 3, 14)}          # Skill Swap (Black 2 tutor)

# code sites (every one checked against Black 2's bytes before writing)
REPLACED = {0x02026a94: ('PML_ItemIsTMHM', 'NewTm_IsTMHM', 0x28), 0x02026abc: ('PML_ItemIsTM', 'NewTm_IsTM', 0x28),
            0x02026ae4: ('PML_ItemGetTMWazaID', 'NewTm_GetMove', 0x34),
            0x02026b40: ('PML_ItemGetTMBitMask', 'NewTm_GetBit', 0x44)}
GET_BIT, WORD_SET_NUMBER = 0x02026b40, 0x0202451c
OV142_CALLS = [(0x0219dfa4, GET_BIT, 'NewTm_BagNumber', 'ItemMenuDisp_DrawItemInfo: the "No. N" line'),
               (0x0219dfe0, WORD_SET_NUMBER, 'NewTm_WordSetNumber', 'ItemMenuDisp_DrawItemInfo: N in 3 digits from 100'),
               (0x0219ba36, GET_BIT, 'NewTm_SortKey', 'ItemMenu_SortByNumber: the key')]
DAYCARE = [(0x021be4e2, 0x2452, 0x2400 | FIRST_ITEM, 'inheritTmMoves: movs r4, #82 -> #120'),
           (0x021be4e6, 0x00a4, 0x0024, 'inheritTmMoves: lsls r4, r4, #2 -> #0')]
ITEM_CATEGORIES, DUMMY_ITEMS, UNHOLDABLE_ITEMS, ITEM_ICONS = 0x0208f4d0, 0x02090a48, 0x02090a98, 0x02090d50
TM_MOVE_LIST = 0x02090c84

TEXT_JSON = os.path.join(ROOT, 'src', 'text', 'overrides_new_tms.json')
HEADER = os.path.join(ROOT, 'src', 'include', 'hoenn_tms.h')


def move_ids():
    return {k: int(v) for k, v in re.findall(r'#define (MOVE_\w+)\s+(\d+)', open(f'{DECOMP}/include/constants/moves.h').read())}


def item_constants():
    """ITEM_TM96 ... -> item id (converter/gen_items.py adds these to Black 2's constants)."""
    return {f'ITEM_TM{n}': it for n, it, _, _ in NEW_TMS}


def move_to_item():
    """MOVE_X -> ITEM_TMnn for the new TMs (converter/gen_items.py)."""
    return {mv: f'ITEM_TM{n}' for n, _, mv, _ in NEW_TMS}


# ---- text and the scripts' header ------------------------------------------------------------------------------------
def text_lines():
    desc = open(os.path.join(DECOMP, 'data', 'text', 'system', '0402_btl_main.txt'), encoding='utf-8').read().split('\n')
    mid = move_ids()
    out = {'_doc': 'TM96-TM104 at items 120-128 (b2tools/patches/new_tms.py writes this file: python3 new_tms.py --text). '
                   'Descriptions = the move\'s own (0402), as Black 2\'s TMs.',
           'system/0064_item_names.txt': {}, 'system/0481_item_names_with_article.txt': {},
           'system/0482_item_names_plural.txt': {}, 'system/0063_scrcmd_resort_shop_scrcmd_bsubway.txt': {}}
    for n, it, mv, _ in NEW_TMS:
        out['system/0064_item_names.txt'][str(it)] = f'TM{n}'
        out['system/0481_item_names_with_article.txt'][str(it)] = f'{{bd01}}a {{ff00:255}}TM{n}'
        out['system/0482_item_names_plural.txt'][str(it)] = f'TM{n}s'
        out['system/0063_scrcmd_resort_shop_scrcmd_bsubway.txt'][str(it)] = desc[mid[mv]]
    return out


def header_text():
    rows = '\n'.join(f'#define ITEM_TM{n:<3d} {it:3d}   // {mv[5:].replace("_", " ").title()} (Gen 3 {g3})' for n, it, mv, g3 in NEW_TMS)
    return ('// The new TMs (b2tools/patches/new_tms.py NEW_TMS; it checks this file): Black 2\'s unused item ids 120-128.\n'
            '#pragma once\n' + rows + '\n')


def check_sources():
    want = json.dumps(text_lines(), ensure_ascii=False, indent=1) + '\n'
    assert os.path.exists(TEXT_JSON) and open(TEXT_JSON, encoding='utf-8').read() == want, \
        'src/text/overrides_new_tms.json is not current: python3 b2tools/patches/new_tms.py --text'
    assert os.path.exists(HEADER) and open(HEADER).read() == header_text(), \
        'src/include/hoenn_tms.h is not current: python3 b2tools/patches/new_tms.py --text'


# ---- species compatibility ------------------------------------------------------------------------------------------
def gen3_learnsets():
    """Species name (SPECIES_X without the prefix) -> the set of MOVE_X it learns by TM/HM in Gen 3."""
    path = os.path.join(ROOT, 'external', version.DECOMP, 'src', 'data', 'pokemon', 'tmhm_learnsets.h')
    s = open(path).read()
    out = {}
    if 'TMHM_LEARNSET(' in s:                                   # pokeruby: TMHM(TMnn_MOVE)
        for name, body in re.findall(r'\[SPECIES_(\w+)\]\s*=\s*TMHM_LEARNSET\((.*?)\),\s*\n', s, re.S):
            out[name] = {'MOVE_' + m.replace('SOLARBEAM', 'SOLAR_BEAM') for m in re.findall(r'TMHM\((?:TM|HM)\d\d_(\w+)\)', body)}
    else:                                                       # pokeemerald: .MOVE = TRUE
        for name, body in re.findall(r'\[SPECIES_(\w+)\]\s*=\s*\{\s*\.learnset\s*=\s*\{(.*?)\}\s*\}', s, re.S):
            out[name] = {'MOVE_' + m for m in re.findall(r'\.(\w+)\s*=\s*TRUE', body)}
    assert len(out) > 400, f'{path}: {len(out)} species parsed'
    return out


def compat_bits(pers):
    """[(record, {bit: bool})] for every personal record: what bits 101-109 should be."""
    b2 = {k: int(v) for k, v in re.findall(r'#define SPECIES_(\w+)\s+(\d+)', open(f'{DECOMP}/include/constants/species.h').read())}
    g3 = gen3_learnsets()
    by_nat = {}
    for name, moves in g3.items():
        if name == 'NONE' or name.startswith('OLD_UNOWN'): continue
        assert name in b2 and 1 <= b2[name] <= 386, f'Gen 3 species {name} not in Black 2 1-386'
        by_nat[b2[name]] = moves
    assert sorted(by_nat) == list(range(1, 387)), 'Gen 3 learnsets do not cover 1-386'
    base_of = {s: s for s in range(len(pers))}
    for s in range(1, 650):                                     # forms: files formFile .. formFile + formCount - 2
        r = pers[s]
        first, count = struct.unpack_from('<H', r, 0x1C)[0], r[0x20]
        if first:
            for f in range(first, first + count - 1): base_of[f] = s
    def word(r, off, i): return struct.unpack_from('<I', r, off + 4 * i)[0]
    def proxy(r, how):
        if how[0] == 'tm': b = how[1] - 1
        elif how[0] == 'hm': b = 95 + how[1] - 1
        else: return bool(word(r, 0x3C, how[1]) >> how[2] & 1)
        return bool(word(r, 0x28, b // 32) >> (b % 32) & 1)
    out = []
    for rec in range(1, len(pers)):
        r = pers[rec]
        if len(r) != 0x4C: continue                         # (the last file, 709, is the regional dex table)
        base = base_of.get(rec, rec)
        bits = {}
        for k, (_, _, mv, _) in enumerate(NEW_TMS):
            bits[FIRST_BIT + k] = mv in by_nat[base] if base in by_nat else proxy(r, PROXY[mv])
        out.append((rec, bits))
    return out


def _vanilla(arc):
    return narcio.load(VANILLA_FILES, arc)


def apply(files):
    check_sources()
    out = []
    # items 120-128: TM01's data with their own sort index
    items, van = narcio.load(files, 24), _vanilla(24)
    tmpl = van[TEMPLATE]
    for k, (n, it, mv, _) in enumerate(NEW_TMS):
        d = bytearray(tmpl); d[0xF] = FIRST_BIT + k
        assert items[it] == van[it] or items[it] == bytes(d), f'item {it}: changed by another patch ({items[it].hex()})'
        assert not any(van[it][:0xC]), f'item {it} is not one of Black 2\'s unused ids'
        items[it] = bytes(d)
    narcio.save(files, 24, items)
    out.append(f'items {FIRST_ITEM}-{FIRST_ITEM + len(NEW_TMS) - 1} = TM{NEW_TMS[0][0]}-TM{NEW_TMS[-1][0]}')
    # personal data bits 101-109
    pers = narcio.load(files, 16)
    vpers = _vanilla(16)
    count = collections.Counter()
    for rec, bits in compat_bits(pers):
        r = bytearray(pers[rec])
        w3 = struct.unpack_from('<I', r, 0x28 + 12)[0]
        assert struct.unpack_from('<I', vpers[rec], 0x28 + 12)[0] >> 5 == 0, f'record {rec}: Black 2 uses TM bits past 100'
        for b, on in bits.items():
            m = 1 << (b - 96)
            w3 = (w3 | m) if on else (w3 & ~m)
            count[b] += on
        struct.pack_into('<I', r, 0x28 + 12, w3)
        pers[rec] = bytes(r)
    narcio.save(files, 16, pers)
    out.append('learners ' + ', '.join(f'TM{n} {count[FIRST_BIT + k]}' for k, (n, _, _, _) in enumerate(NEW_TMS)))
    return 'new_tms: ' + '; '.join(out)


# ---- code -----------------------------------------------------------------------------------------------------------
def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_link', os.path.join(HERE, 'roamers.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def build(base, workdir):
    mid = move_ids()
    defs = [f'-DNEW_TM_FIRST={FIRST_ITEM}', f'-DNEW_TM_COUNT={len(NEW_TMS)}', f'-DNEW_TM_BIT={FIRST_BIT}',
            '-DNEW_TM_MOVES=' + ','.join(str(mid[mv]) for _, _, mv, _ in NEW_TMS)]
    obj = os.path.join(workdir, 'new_tms.o')
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror', *defs,
                    '-c', os.path.join(HERE, 'new_tms.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'new_tms.c needs {und}: call Black 2 functions by address only'
    return _roamers().link(obj, base)


def _bl(src, dst):
    off = dst - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, hex(off)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)


def _long_jump(addr, target):
    """ldr r3, [pc, #0]; bx r3; .word target|1 at a 4-aligned function start (r3 is free: one-argument functions)"""
    assert addr % 4 == 0
    return struct.pack('<HHI', 0x4B00, 0x4718, target | 1)


def _put(d, base, addr, old, new, what):
    """Write new at addr (old = Black 2's bytes; already new is fine: a rerun)."""
    o = addr - base
    cur = bytes(d[o:o + len(new)])
    assert cur in (old, new), f'{what} at {addr:#x}: {cur.hex()} (expected {old.hex()})'
    d[o:o + len(new)] = new


def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())


def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)


def type_palettes(arm9):
    """Move type -> the palette most of Black 2's TMs of that type use (char 397, the TM disc)."""
    moves = struct.unpack_from('<101H', arm9, TM_MOVE_LIST - ARM9)
    mv = _vanilla(21)
    items = list(range(328, 420)) + list(range(618, 621))          # the TMs (HMs use another disc)
    idx = list(range(92)) + [98, 99, 100]
    c = collections.defaultdict(collections.Counter)
    for it, i in zip(items, idx):
        ch, pal = struct.unpack_from('<HH', arm9, ITEM_ICONS - ARM9 + 4 * it)
        assert ch == TM_CHAR
        c[mv[moves[i]][0]][pal] += 1
    return {t: cnt.most_common(1)[0][0] for t, cnt in c.items()}


def apply_code(code):
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    p9, arm9 = _load(code, 'arm9.bin')
    vanilla9 = open(os.path.join(VANILLA_CODE, 'arm9.bin'), 'rb').read()
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not the end of ITCM'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym = build(base, tmp)
    end = (base + len(blob) + 31) & ~31
    assert end <= ITCM_END, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    pi, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(pi, bytes(itcm) + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    # arm9: the four functions -> ITCM
    for at, (name, new, fsize) in REPLACED.items():
        o = at - ARM9
        assert arm9[o:o + fsize] == vanilla9[o:o + fsize], f'{name} was changed by another patch'
        arm9[o:o + 8] = _long_jump(at, sym[new] & ~1)
    # arm9 data: pocket, dummy / unholdable bits, icons
    pal = type_palettes(vanilla9)
    mv = _vanilla(21)
    mid = move_ids()
    for n, it, m, _ in NEW_TMS:
        _put(arm9, ARM9, ITEM_CATEGORIES + it, bytes([0]), bytes([POCKET_TMS]), f'pocket of item {it}')
        _put(arm9, ARM9, ITEM_ICONS + 4 * it, struct.pack('<HH', *DUMMY_ICON), struct.pack('<HH', TM_CHAR, pal[mv[mid[m]][0]]),
             f'icon of item {it}')
        w = it // 32 * 4
        d, u = struct.unpack_from('<I', vanilla9, DUMMY_ITEMS - ARM9 + w)[0], struct.unpack_from('<I', vanilla9, UNHOLDABLE_ITEMS - ARM9 + w)[0]
        bit = 1 << (it % 32)
        assert d & bit, f'item {it} is not a dummy in Black 2'
        cur_d = struct.unpack_from('<I', arm9, DUMMY_ITEMS - ARM9 + w)[0]
        cur_u = struct.unpack_from('<I', arm9, UNHOLDABLE_ITEMS - ARM9 + w)[0]
        struct.pack_into('<I', arm9, DUMMY_ITEMS - ARM9 + w, cur_d & ~bit)
        struct.pack_into('<I', arm9, UNHOLDABLE_ITEMS - ARM9 + w, cur_u | bit)
    _save(p9, arm9)
    # ov142: the Bag's number line and sort
    p142, ov142 = _load(code, 'arm9_ov142.bin')
    for at, old, new, what in OV142_CALLS:
        _put(ov142, OV142, at, _bl(at, old), _bl(at, sym[new] & ~1), what)
    _save(p142, ov142)
    # ov036: the day care's TM-move loop
    p036, ov036 = _load(code, 'arm9_ov036.bin')
    for at, old, new, what in DAYCARE:
        _put(ov036, OV036, at, struct.pack('<H', old), struct.pack('<H', new), what)
    _save(p036, ov036)
    return (f'new_tms: {len(blob)} B of ITCM at {base:#x} (arena from {end:#x}, {ITCM_END - end} B left); 4 TM functions, '
            f'Bag number/sort, day care; icons ' + ', '.join(f'TM{n} pal {pal[mv[mid[m]][0]]}' for n, _, m, _ in NEW_TMS))


if __name__ == '__main__':
    if '--text' in sys.argv:              # write the text overrides and the scripts' header
        open(TEXT_JSON, 'w', encoding='utf-8').write(json.dumps(text_lines(), ensure_ascii=False, indent=1) + '\n')
        open(HEADER, 'w').write(header_text())
        print('wrote', os.path.relpath(TEXT_JSON, ROOT), os.path.relpath(HEADER, ROOT))
    else:                                 # compile and link at a dummy base, show the symbols
        with tempfile.TemporaryDirectory() as tmp:
            blob, sym = build(0x01FFE000, tmp)
            print(len(blob), {k: hex(v) for k, v in sym.items() if k.startswith('NewTm_')})
