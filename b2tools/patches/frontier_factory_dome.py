"""Pokémon Emerald NDS: the Battle Factory and the Battle Dome (frontier_factory_dome, 2026-10-12;
notes/FRONTIER_FACTORY_DOME.md). HOENN_VERSION=emerald only: Sapphire and Ruby builds return before touching anything.

apply(files): Black 2's Battle Subway set archive (arc 211, 1000 files: HoennB2's Battle Tower uses 0-599) gets
  files 1000-1881  Emerald's 882 Battle Frontier sets (data/emerald/frontier.json, converter/gen_frontier_emerald.py) in
                   Black 2's 16-byte set format (u16 species, 4 x u16 moves, u8 EV flags, u8 nature, u16 item, u16 form),
                   the format func_ov012_02162490 reads (the PWT's rental engine reads the same format from arc 257)
  files 1882-1887  Tucker's two parties (pokeemerald sFrontierBrainsMons[DOME]: silver, gold)
  file 1888        16 bytes of facts per set (0-887): u16 species, u16 item, Gen 3 types, Levitate / Wonder Guard flags,
                   base stat total / 10, the four moves' Gen 3 types (255 = no power), their Factory battle styles (4 bits
                   each), nature, EV flags: what Emerald's Factory and Dome rules read (most common type, battle style,
                   the Dome's NPC-vs-NPC points and its opponents' choice of two, the seeding)
  file 1889        the 300 Frontier trainers: {u16 Black 2 class, u16 overworld sprite, u16 set-list offset, u16 count}
                   then the set lists (u16 set ids)
  file 1890        the engine: frontier_factory_dome.c built position-independent (clang -fropi, linked here at 0) after
                   a 16-byte header ('FRFD', size, FR_Cmd offset, FR_BuildSetup offset). It does not fit the ITCM the
                   other patches leave (~11 KB; ~2 KB were free after frontier_core), so frontier_fd_stub.c loads it into the
                   game-event heap per call (notes/FRONTIER_FACTORY_DOME.md "Code")
  The archive grows (Emerald builds have their own savestates; Sapphire and Ruby never run this).
apply_code(code): frontier_fd_stub.c (the loader, a few hundred bytes) in ITCM after the other ITCM patches (as
  emerald_mech), script command 505 (Black 2's Cmd_01F9, func_ov036_021c730c: unused by every Black 2 and Hoenn script;
  args any, any, any, var as field_commands.json says, so script_check still decodes it) -> FRS_Cmd, and ov012
  0x02166082 (func_ov012_02166070's call of func_ov033_0217c094, the Subway battle's setup) -> FRS_BuildSetup (Factory and
  Dome battles get their parties from the engine there; every other Subway battle is Black 2's call)."""
import os, re, sys, json, struct, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import version  # noqa: E402

LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV012 = 0x021503C0
EVCMD_TABLE = 0x0216B538
CMD, CMD_OLD = 505, 0x021C730D                  # Cmd_01F9 (ov036 func_ov036_021c730c, Thumb)
HOOK_AT, HOOK_OLD = 0x02166082, 0x0217C094      # ov012: bl func_ov033_0217c094
SET_BASE, ARC_SETS = 1000, 211
N_SETS, TUCKER = 882, 882
FACTS_FILE, TRAINERS_FILE, BLOB_FILE = 1888, 1889, 1890
NAME_BASE, SPEECH_BASE = 100, 500               # lines of the Factory battle room's text (FR_TEXT_FILE)
NAME_NOLAND, NAME_TUCKER = 400, 401
LINE_TOURNAMENT, LINE_YOUR_BLOCK, LINE_OTHER_BLOCK = 90, 91, 92
# the Frontier Brains: frontier_core's Brain classes (= their front pictures) and walking sprites (notes/FRONTIER.md 5;
# `python3 b2tools/sprite_emerald_frontier.py check`). The class names, sex and music are still Black 2's there.
NOLAND_CLASS, NOLAND_SPRITE = 33, 298
TUCKER_CLASS, TUCKER_SPRITE = 7, 99
PLAYER_SPRITE = (1, 4)                          # the player's overworld code, male / female (the PWT bracket's icon)
PICK_MODE, PICK_REGULATION, REG_OFFSET = 22, 22, 216   # emerald_mech.c: the Battle Institute's team selection
DOME_OPPONENT_IV = 3                            # pokeemerald CreateDomeOpponentMon (no BUGFIX): every Dome trainer's IVs are 3
EV_ORDER = ['HP', 'ATTACK', 'DEFENSE', 'SPEED', 'SP_ATTACK', 'SP_DEFENSE']
NATURES = ['NATURE_HARDY', 'NATURE_LONELY', 'NATURE_BRAVE', 'NATURE_ADAMANT', 'NATURE_NAUGHTY', 'NATURE_BOLD',
           'NATURE_DOCILE', 'NATURE_RELAXED', 'NATURE_IMPISH', 'NATURE_LAX', 'NATURE_TIMID', 'NATURE_HASTY',
           'NATURE_SERIOUS', 'NATURE_JOLLY', 'NATURE_NAIVE', 'NATURE_MODEST', 'NATURE_MILD', 'NATURE_QUIET',
           'NATURE_BASHFUL', 'NATURE_RASH', 'NATURE_CALM', 'NATURE_GENTLE', 'NATURE_SASSY', 'NATURE_CAREFUL',
           'NATURE_QUIRKY']

def data():
    return json.load(open(os.path.join(ROOT, 'data', 'emerald', 'frontier.json'), encoding='utf-8'))

def text_file():
    """The script text number that holds the trainers' names (the Factory battle room's own text)."""
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    return rooms['BattleFrontier_BattleFactoryBattleRoom']['own_text']

def ev_flags(names):
    return sum(1 << EV_ORDER.index(e) for e in names)

def set_record(m):
    moves = (m['move_ids'] + [0, 0, 0, 0])[:4]
    return struct.pack('<H4HBBHH', m['species_id'] & 0x7ff, *moves, ev_flags(m['ev']), m['nature_id'], m['item_id'], 0)

def tucker_record(m):
    flags = sum(1 << i for i, v in enumerate(m['evs']) if v)        # (the real EVs are set by the C code: kTuckerEvs)
    return struct.pack('<H4HBBHH', m['species_id'] & 0x7ff, *(m['move_ids'] + [0] * 4)[:4], flags, m['nature_id'], m['item_id'], 0)

def fact(m, evs):
    styles = sum((v & 15) << (4 * i) for i, v in enumerate((m['styles'] + [0] * 4)[:4]))
    mt = (m['move_types'] + [255] * 4)[:4]
    return struct.pack('<HHBBBB4BHBB', m['species_id'], m['item_id'], m['types'][0], m['types'][1],
                       (1 if m['levitate'] else 0) | (2 if m['wonder_guard'] else 0), m['stat_sum10'], *mt, styles,
                       m['nature_id'], evs)

def files_blob():
    d = data()
    sets = [set_record(m) for m in d['sets']]
    tk = d['tucker']['silver'] + d['tucker']['gold']
    sets += [tucker_record(m) for m in tk]
    facts = b''.join(fact(m, ev_flags(m['ev'])) for m in d['sets'])
    facts += b''.join(fact(m, sum(1 << i for i, v in enumerate(m['evs']) if v)) for m in tk)
    head, lists = b'', []
    off = 4 * len(d['trainers'])                         # u16 units: the 8-byte headers come first
    for t in d['trainers']:
        head += struct.pack('<HHHH', t['b2_class'], t['sprite'], off, len(t['mon_set']))
        lists += t['mon_set']; off += len(t['mon_set'])
    trainers = head + struct.pack(f'<{len(lists)}H', *lists)
    return sets, facts, trainers

def apply(files):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    import narcio
    entries = narcio.load(files, ARC_SETS)
    assert len(entries) == SET_BASE, f'arc {ARC_SETS} has {len(entries)} files: expected Black 2\'s {SET_BASE} (another patch appended?)'
    sets, facts, trainers = files_blob()
    with tempfile.TemporaryDirectory() as tmp:
        engine = build_engine(tmp)
    entries += sets + [facts, trainers, engine]
    assert len(entries) == BLOB_FILE + 1, len(entries)
    narcio.save(files, ARC_SETS, entries)
    return (f'arc {ARC_SETS}: {len(sets)} Emerald Frontier sets at {SET_BASE}-{SET_BASE + len(sets) - 1}, facts {FACTS_FILE} '
            f'({len(facts)} B), trainers {TRAINERS_FILE} ({len(trainers)} B), engine {BLOB_FILE} ({len(engine)} B)')

def c_table(name, ctype, rows):
    if rows and isinstance(rows[0], (list, tuple)):
        body = ', '.join('{' + ', '.join(str(x) for x in r) + '}' for r in rows)
        return f'static const {ctype} {name}[{len(rows)}][{len(rows[0])}] = {{{body}}};'
    return f'static const {ctype} {name}[{len(rows)}] = {{{", ".join(str(x) for x in rows)}}};'

def data_header():
    d = data()
    tk = d['tucker']['silver'] + d['tucker']['gold']
    b2_species = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define SPECIES_(\w+) (\d+)', open(
        os.path.join(ROOT, 'external', 'pokebw2', 'include', 'constants', 'species.h')).read())}
    chart = [r for r in d['type_chart'] if r[2] != 10]
    lines = ['/* generated by b2tools/patches/frontier_factory_dome.py from data/emerald/frontier.json */',
             f'#define FR_SET_BASE {SET_BASE}', f'#define FR_FACTS_FILE {FACTS_FILE}', f'#define FR_TRAINERS_FILE {TRAINERS_FILE}',
             f'#define FR_TEXT_FILE {text_file()}', f'#define FR_NAME_BASE {NAME_BASE}', f'#define FR_SPEECH_BASE {SPEECH_BASE}',
             f'#define kNameNoland {NAME_NOLAND}', f'#define kNameTucker {NAME_TUCKER}', f'#define kNameBrain {NAME_NOLAND}',
             f'#define kLineTournamentName {LINE_TOURNAMENT}', f'#define kLineYourBlock {LINE_YOUR_BLOCK}',
             f'#define kLineOtherBlock {LINE_OTHER_BLOCK}',
             f'#define kSpeciesUnown {b2_species["UNOWN"]}', f'#define kHighTier {d["high_tier"]}',
             f'#define kTuckerSet {TUCKER}', f'#define kNolandClass {NOLAND_CLASS}', f'#define kNolandSprite {NOLAND_SPRITE}',
             f'#define kTuckerClass {TUCKER_CLASS}', f'#define kTuckerSprite {TUCKER_SPRITE}',
             f'#define kPlayerSpriteM {PLAYER_SPRITE[0]}', f'#define kPlayerSpriteF {PLAYER_SPRITE[1]}',
             f'#define kDomeOpponentIv {DOME_OPPONENT_IV}',
             f'#define PICK_MODE {PICK_MODE}', f'#define PICK_REGULATION {PICK_REGULATION}', f'#define REG_OFFSET {REG_OFFSET}',
             c_table('kFactoryRanges', 'u16', d['factory_ranges']), c_table('kFactoryIV', 'u8', d['factory_fixed_iv']),
             c_table('kTrainerRanges', 'u16', d['trainer_ranges']), c_table('kTrainerRangesHard', 'u16', d['trainer_ranges_hard']),
             c_table('kStyleRequired', 'u8', d['factory_style_required']),
             c_table('kBrainFactory', 'u8', [21, 42, 21, 1]), c_table('kBrainDome', 'u8', [4, 9, 5, 0]),
             c_table('kDomeIvLimit', 'u16', d['dome_iv_limits']),
             c_table('kTypeChart', 'u8', chart),
             c_table('kTuckerIv', 'u8', [m['iv'] for m in tk]), c_table('kTuckerEvs', 'u8', [m['evs'] for m in tk])]
    # pokeemerald's numbers the C code has as literals (brain streaks: frontier_util.c sFrontierBrainStreakAppearances)
    fu = open(os.path.join(ROOT, 'external', 'pokeemerald', 'src', 'frontier_util.c')).read()
    assert re.search(r'\[FRONTIER_FACILITY_DOME\]\s*=\s*\{\s*4,\s*9,\s*5,\s*0\}', fu)
    assert re.search(r'\[FRONTIER_FACILITY_FACTORY\]\s*=\s*\{21,\s*42,\s*21,\s*1\}', fu)
    bd = open(os.path.join(ROOT, 'external', 'pokeemerald', 'src', 'battle_dome.c')).read()
    assert '{0, 8, 12, 4, 7, 15, 11, 3, 2, 10, 14, 6, 5, 13, 9, 1}' in bd and '{ 0, 8, 4, 12, 7, 15, 3, 11, 2, 10, 6, 14, 5, 13, 1, 9 }' in bd
    return '\n'.join(lines) + '\n'

def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_fd', os.path.join(HERE, 'roamers.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

CFLAGS = ['--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding', '-fno-builtin',
          '-fno-jump-tables', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables', '-fno-exceptions', '-fno-common',
          '-mno-unaligned-access', '-Wall', '-Werror']

def _compile(src, workdir, extra):
    obj = os.path.join(workdir, os.path.basename(src)[:-2] + '.o')
    subprocess.run([f'{LLVM}/clang', *CFLAGS, *extra, '-I', workdir, '-c', src, '-o', obj], check=True)
    return obj

def link_pic(obj):
    """Link a -fropi object at address 0: its read-only sections in order, PC-relative relocations only (R_ARM_REL32,
    R_ARM_THM_CALL, R_ARM_THM_JUMP11/8 inside the blob); any absolute address of the blob would break when it is loaded
    elsewhere, so R_ARM_ABS32 to a blob symbol is refused. -> (bytes, {symbol: offset})"""
    roam = _roamers()
    d, secs = roam._elf(obj)
    place, blob = {}, bytearray()
    for i, s in enumerate(secs):
        if s['flags'] & 2 and s['size'] and not s['name'].startswith('.ARM.'):
            assert s['type'] == 1 and not s['flags'] & 1, f"section {s['name']}: the engine keeps no RAM of its own"
            while len(blob) % max(s['align'], 4): blob += b'\0'
            place[i] = len(blob)
            blob += d[s['off']:s['off'] + s['size']]
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
            assert shndx in place, f'undefined symbol {name!r}: Black 2 functions are called by address only'
            S, P = place[shndx] + val, tbase + off
            if typ == 3:                                          # R_ARM_REL32: S + A - P
                A, = struct.unpack_from('<i', blob, P)
                struct.pack_into('<I', blob, P, (S + A - P) & 0xFFFFFFFF)
            elif typ == 10:                                       # R_ARM_THM_CALL
                h1, h2 = struct.unpack_from('<HH', blob, P)
                assert h2 & 0xF800 == 0xF800, 'blx to a Thumb symbol'
                A = (h1 & 0x7FF) << 12 | (h2 & 0x7FF) << 1
                if A & (1 << 22): A -= 1 << 23
                X = (S & ~1) + A - P
                assert -(1 << 22) <= X < (1 << 22)
                struct.pack_into('<HH', blob, P, 0xF000 | (X >> 12) & 0x7FF, 0xF800 | (X >> 1) & 0x7FF)
            elif typ == 102:                                      # R_ARM_THM_JUMP11
                h, = struct.unpack_from('<H', blob, P)
                A = (h & 0x7FF) << 1
                if A & 0x800: A -= 0x1000
                o = (S & ~1) + A - P
                assert -2048 <= o < 2048
                struct.pack_into('<H', blob, P, (h & 0xF800) | (o >> 1) & 0x7FF)
            else:
                raise SystemExit(f'frontier engine: relocation type {typ} ({name}) is not position-independent')
    return bytes(blob), names

def build_engine(workdir):
    """The engine (frontier_factory_dome.c, -fropi) with its 16-byte header: 'FRFD', size, FR_Cmd, FR_BuildSetup."""
    open(os.path.join(workdir, 'frontier_fd_data.h'), 'w').write(data_header())
    test = ['-DHOENN_TEST_FD_WEAK'] if os.environ.get('HOENN_TEST_FD_WEAK') else []   # test builds only: Lv. 5 opponents
    obj = _compile(os.path.join(HERE, 'frontier_factory_dome.c'), workdir, ['-fropi'] + test)
    blob, sym = link_pic(obj)
    head = 16
    out = struct.pack('<4sIII', b'FRFD', head + len(blob), head + (sym['FR_Cmd'] & ~1), head + (sym['FR_BuildSetup'] & ~1))
    return out + blob

def build_stub(base, workdir):
    obj = _compile(os.path.join(HERE, 'frontier_fd_stub.c'), workdir, ['-fno-pic', f'-DFR_BLOB_FILE={BLOB_FILE}'])
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'frontier_fd_stub.c needs {und}'
    return _roamers().link(obj, base)

def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())

def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)

def apply_code(code):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    base = ITCM_BASE + size
    path9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'run frontier_factory_dome after the other ITCM patches (the arena literal)'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym = build_stub(base, tmp)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    _save(path9, arm9)
    path, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(path, itcm + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    bl = _roamers()._bl
    p, d = _load(code, 'arm9_ov012.bin')
    o = HOOK_AT - OV012
    assert bytes(d[o:o + 4]) == bl(HOOK_AT, HOOK_OLD), 'ov012 0x02166082 is not Black 2\'s call of func_ov033_0217c094'
    d[o:o + 4] = bl(HOOK_AT, sym['FRS_BuildSetup'] & ~1)
    e = EVCMD_TABLE - OV012 + 4 * CMD
    assert struct.unpack_from('<I', d, e)[0] == CMD_OLD, f'EVCMD_TABLE[{CMD}] is not Black 2\'s (another patch took it?)'
    struct.pack_into('<I', d, e, sym['FRS_Cmd'] | 1)
    _save(p, d)
    return (f'frontier_factory_dome: loader {len(blob)} B of ITCM at {base:#x} (arena from {end:#x}); command {CMD} FrontierCmd; '
            f'Subway battle setup hook at {HOOK_AT:#x}; engine in arc {ARC_SETS} file {BLOB_FILE}; names in script text {text_file()}')

if __name__ == '__main__':          # python3 frontier_factory_dome.py: the loader's and the engine's sizes, the files'
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym = build_stub(0x01FFD000, tmp)
        print('loader', len(blob), {k: hex(v) for k, v in sym.items() if k.startswith('FRS_')})
        print('engine', len(build_engine(tmp)))
    s, f, t = files_blob()
    print(len(s), 'sets', len(f), 'B facts', len(t), 'B trainers')
