"""The Battle Frontier's shared systems (frontier_core, 2026-10-12; notes/FRONTIER.md). HOENN_VERSION=emerald only:
Sapphire and Ruby builds return before touching anything. Run after emerald_mech (both put code in ITCM).

apply_code(code):
  1. frontier_core.c compiled with clang and placed in ITCM after the other ITCM patches (the arena move of
     hoenn_world.py / roamers.py / emerald_mech.py).
  2. ov012 EVCMD_TABLE (0x0216B538): command 230 -> FR_CmdGet (`FrGet key, var`), 232 -> FR_CmdOp (`FrOp op, var`).
     Both were Black 2's trainer-card item checks (TrainerCardCmd_00E6 / _00E8, func_ov012_02155d80 / _02155dd4) that
     no Black 2 or Hoenn script uses (counted over external/pokebw2/data/field_scripts and src/field_scripts); their
     argument kinds stay (any, var) as field_commands.json says, so script_check still decodes them; EVCMD_PERM_TABLE
     gives both 7 (normal, init and global scripts), unchanged.
  3. The Frontier's records: save block 0x38 (Black 2's Battle Subway play block; arm9 func_0200e0f0 = its size, 60)
     becomes 252 bytes. SaveData_BuildTable (arm9 0x0203c2e8) gives each block size + 4 (footer) rounded up to 0x100,
     so this block keeps its 256-byte slot and no other block moves. Black 2's own code reads and clears only its 60
     bytes (func_0200e0f4, also called by ov033/ov050 when a Subway challenge ends: the Battle Tower never touches the
     records); the block's new-game initializer (save table SAVEDATA_INIT entry 0x38, arm9 0x0208f408) becomes
     FR_PlayInit (all 252). Saves of an Emerald ROM made before this patch have the old block size: their CRC no longer
     matches (start a new game). Sapphire and Ruby keep 60.
  4. The BP shop lists: ov036 ShopUI_Init's call of ShopUI_LoadMsgData (0x021abf68) -> FR_ShopMsgData: the Exchange
     Service Corner's shop ids (SHOPS below) load Emerald's list into Black 2's BP list 0 and go on as shop 254 (the
     BP shop screen: BP shown, BP paid); every shop first gets Black 2's own list 0 back (the PWT's BP clerks).
  5. The Battle Tower's Open Level (Black 2 play mode 5, the Lv. 100 room): ov012 0x02161fac (BtlSetup_SetTrialHouseParty's
     `bl` to battle_tower.py's level helper: r0 = heap 4, r2 = 50 + 10 x mode) -> FR_TowerLevelShim: mode 5 = pokeemerald
     GetFrontierEnemyMonLevel's Open Level (the highest level of the player's battle party, the three entered, at least
     60); other modes unchanged. Run after battle_tower (asserted).
Data from pokeemerald (frontier_core_data.h): sBattlePointAwards (frontier_util.c), the Exchange Service Corner's
vitamin and hold-item clerks (prices, items, order), the two BP tutors (BattleFrontier_Lounge7 prices,
sBattleFrontier_TutorMoves1/2), the banned list (Black 2's arc 106 file 20 = the Battle Subway's: Emerald's
gFrontierBannedSpecies and the Gen 4/5 legends)."""
import os, re, sys, struct, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import version  # noqa: E402

LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV012, OV036 = 0x021503C0, 0x0217F600
EVCMD_TABLE = 0x0216B538
COMMANDS = {230: (0x02155D81, 'FR_CmdGet'), 232: (0x02155DD5, 'FR_CmdOp')}
SHOP_CALL = (0x021ABF68, 0x021ACA14, 'FR_ShopMsgData')            # ShopUI_Init -> ShopUI_LoadMsgData
TOWER_LEVEL_CALL = 0x02161FAC        # BtlSetup_SetTrialHouseParty: battle_tower.py's `bl level_helper` (the opponents' level)
PLAY_SIZE_FN, PLAY_INIT_LIT = 0x0200E0F0, 0x0208F408             # block 0x38: size function, its table initializer
PLAY_B2_SIZE, PLAY_SIZE = 60, 252
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
ESC = os.path.join(EMERALD, 'data', 'maps', 'BattleFrontier_ExchangeServiceCorner', 'scripts.inc')
LOUNGE7 = os.path.join(EMERALD, 'data', 'maps', 'BattleFrontier_Lounge7', 'scripts.inc')
# Exchange Service Corner shops: (shop id for CallFriendlyShopBuy, Emerald's menu label). Black 2's ids 240/241 are
# special Poké Mart lists no Hoenn script opens; FR_ShopMsgData turns them into BP shops with Emerald's lists.
SHOPS = [(240, 'ChooseVitamin'), (241, 'ChooseHoldItem')]
FR_BPWIN = (613, 26)                     # script text 613 (the shop screen's): line 26 "{0205:0} BP"

def _emerald_mech():
    spec = importlib.util.spec_from_file_location('emerald_mech_', os.path.join(HERE, 'emerald_mech.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def _battle_tower():
    spec = importlib.util.spec_from_file_location('battle_tower_', os.path.join(HERE, 'battle_tower.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def _save_compat():
    spec = importlib.util.spec_from_file_location('save_compat_', os.path.join(HERE, 'save_compat.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_', os.path.join(HERE, 'roamers.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def b2_items():
    return {m.group(1): int(m.group(2)) for m in re.finditer(r'#define ITEM_(\w+)\s+(\d+)',
                                                              open(os.path.join(B2, 'include', 'constants', 'items.h')).read())}

def em_moves():
    return {m.group(1): int(m.group(2)) for m in re.finditer(r'#define MOVE_(\w+)\s+(\d+)',
                                                              open(os.path.join(EMERALD, 'include', 'constants', 'moves.h')).read())}

def _switch(text, label):
    """the case labels of `label`'s switch, in case order (0, 1, ...)"""
    body = text.split(label + '::', 1)[1].split('\n\n')[0]
    return [l for _, l in sorted((int(n), l) for n, l in re.findall(r'case (\d+), \w+_EventScript_(\w+)', body))]

def _setvars(text, label):
    body = text.split('_EventScript_' + label + '::', 1)[1].split('\n\n')[0]
    return dict(re.findall(r'setvar (VAR_0x800[89]), (\w+)', body))

def shop_lists():
    """[(shop id, [(B2 item id, price, Emerald item name)])] in Emerald's menu order"""
    t, items = open(ESC).read(), b2_items()
    out = []
    for sid, menu in SHOPS:
        rows = []
        for lab in _switch(t, 'BattleFrontier_ExchangeServiceCorner_EventScript_' + menu):
            if lab == 'ClerkGoodbye': continue
            v = _setvars(t, lab)
            name = v['VAR_0x8009'][len('ITEM_'):]
            assert name in items, f'{name}: no Black 2 item'
            rows.append((items[name], int(v['VAR_0x8008']), name))
        out.append((sid, rows))
    return out

def tutor_lists():
    """[(side, [(tutor index, move id, price, name)] x 10)]: Lounge7's left (TutorMoves1) and right (TutorMoves2)"""
    t, mv = open(LOUNGE7).read(), em_moves()
    order, moves, _, _ = _emerald_mech().tutor_data()               # TUTOR_MOVE_* order, {tutor: move id}
    by_move = {m: order.index(tn) for tn, m in moves.items()}
    fs = open(os.path.join(EMERALD, 'src', 'field_specials.c')).read()
    out = []
    for side, (menu, arr) in enumerate([('ChooseLeftTutorMove', 'sBattleFrontier_TutorMoves1'),
                                         ('ChooseRightTutorMove', 'sBattleFrontier_TutorMoves2')]):
        names = re.findall(r'MOVE_(\w+)', fs.split(arr + '[] =', 1)[1].split('};', 1)[0])
        labs = _switch(t, 'BattleFrontier_Lounge7_EventScript_' + menu)
        labs = [l for l in labs if l != 'ExitTutorMoveSelect']
        assert len(names) == len(labs) == 10, (names, labs)
        rows = []
        for n, lab in zip(names, labs):
            assert lab.upper().replace('_', '') == n.replace('_', ''), (lab, n)    # case k is move k of the list
            m = mv[n]
            rows.append((by_move[m], m, int(_setvars(t, lab)['VAR_0x8008']), n))
        out.append((side, rows))
    return out

def awards():
    """sBattlePointAwards[row][facility][mode] (missing modes 0), and each facility's streak divisor"""
    src = open(os.path.join(EMERALD, 'src', 'frontier_util.c')).read()
    body = src.split('sBattlePointAwards[][NUM_FRONTIER_FACILITIES][FRONTIER_MODE_COUNT] =', 1)[1].split('};', 1)[0]
    rows = []
    for r in re.findall(r'\{\s*(\{[^{}]*\}(?:\s*,\s*\{[^{}]*\})*)\s*\}', body):
        fac = [[int(x) for x in re.findall(r'\d+', g)] for g in re.findall(r'\{([^{}]*)\}', r)]
        assert len(fac) == 7, fac
        rows.append([(f + [0, 0, 0, 0])[:4] for f in fac])
    gb = src.split('static void GiveBattlePoints(void)', 1)[1].split('points = sBattlePointAwards', 1)[0]
    # the row is challengeNum - 1 (0 stays 0), clamped: frontier_core.c award() does the same
    assert re.search(r'if \(challengeNum != 0\)\s*challengeNum--;\s*if \(challengeNum >= ARRAY_COUNT\(sBattlePointAwards\)\)', gb), \
        'pokeemerald GiveBattlePoints changed: check frontier_core.c award()'
    div = {}
    for fac, expr in re.findall(r'case FRONTIER_FACILITY_(\w+):\s*challengeNum = ([^;]*);', gb):
        m = re.search(r'/ (\w+)', expr)
        div[fac] = {'FRONTIER_STAGES_PER_CHALLENGE': 7, 'NUM_PIKE_ROOMS': 14}[m.group(1)] if m else 1
    order = ['TOWER', 'DOME', 'PALACE', 'ARENA', 'FACTORY', 'PIKE', 'PYRAMID']
    return rows, [div[f] for f in order]

def banned():
    """national numbers banned by Black 2's Battle Subway regulation (arc 106 file 20; byte 0xA.. a species bitfield)"""
    sys.path.insert(0, os.path.join(B2, 'tools', 'scripts'))
    from narc import read_narc
    from b2files import arc_path
    d = read_narc(open(arc_path(os.path.join(B2, 'extract', 'b2_us', 'files'), 106), 'rb').read())[20]
    bits = d[0xA:0xA + 0x52]
    return [s for s in range(1, 656) if bits[s >> 3] >> (s & 7) & 1]

def banned_names_order(ban):
    """the banned species in the order Emerald names them: gFrontierBannedSpecies (frontier_util.c), then the rest of
    Black 2's list (the Gen 4/5 species Emerald never had) by number"""
    src = open(os.path.join(EMERALD, 'src', 'frontier_util.c')).read()
    em = re.findall(r'SPECIES_(\w+)', src.split('gFrontierBannedSpecies[] =', 1)[1].split('};', 1)[0])
    b2 = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define SPECIES_(\w+) (\d+)',
                                                            open(os.path.join(B2, 'include', 'constants', 'species.h')).read())}
    first = [b2[n] for n in em]
    assert sorted(first) == sorted(s for s in ban if s <= 386), (first, ban)
    return first + [s for s in ban if s not in first]

def data_header():
    rows, div = awards()
    shops, tutors, ban = shop_lists(), tutor_lists(), banned()
    mx = max(len(r) for _, r in shops)
    L = ['/* generated by b2tools/patches/frontier_core.py from pokeemerald and Black 2\'s arc 106 */',
         f'#define N_AWARD_ROWS {len(rows)}',
         'static const u8 kAwards[N_AWARD_ROWS][7][4] = {' + ', '.join(
             '{' + ', '.join('{' + ', '.join(map(str, f)) + '}' for f in r) + '}' for r in rows) + '};',
         'static const u8 kStreakDiv[7] = {' + ', '.join(map(str, div)) + '};',
         'static const u16 kBanned[] = {' + ', '.join(map(str, ban)) + ', 0};',
         'static const u16 kBannedNames[] = {' + ', '.join(map(str, banned_names_order(ban))) + ', 0};',
         f'#define N_SHOPS {len(shops)}',
         'static const u16 kShopIds[N_SHOPS] = {' + ', '.join(str(s) for s, _ in shops) + '};',
         'static const u8 kShopCount[N_SHOPS] = {' + ', '.join(str(len(r)) for _, r in shops) + '};',
         f'static const u32 kShopItems[N_SHOPS][{2 * mx}] = {{' + ', '.join(
             '{' + ', '.join(f'{i}, {p}' for i, p, _ in r) + '}' for _, r in shops) + '};',
         'static const u8 kTutorCost[2][10] = {' + ', '.join('{' + ', '.join(str(c) for _, _, c, _ in r) + '}' for _, r in tutors) + '};',
         'static const u8 kTutorId[2][10] = {' + ', '.join('{' + ', '.join(str(t) for t, _, _, _ in r) + '}' for _, r in tutors) + '};',
         'static const u16 kTutorMove[2][10] = {' + ', '.join('{' + ', '.join(str(m) for _, m, _, _ in r) + '}' for _, r in tutors) + '};',
         f'#define FR_BPWIN_FILE {FR_BPWIN[0]}', f'#define FR_BPWIN_LINE {FR_BPWIN[1]}']
    return '\n'.join(L) + '\n', dict(rows=len(rows), div=div, shops=shops, tutors=tutors, banned=ban)

def build(base, workdir):
    header, info = data_header()
    open(os.path.join(workdir, 'frontier_core_data.h'), 'w').write(header)
    obj = os.path.join(workdir, 'frontier_core.o')
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror', *_save_compat().cflags(),
                    '-I', workdir, '-c', os.path.join(HERE, 'frontier_core.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'frontier_core.c needs {und}: call Black 2 functions by address only'
    blob, sym = _roamers().link(obj, base)
    return blob, sym, info

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
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    path9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'run frontier_core after the other ITCM patches (the arena literal)'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym, info = build(base, tmp)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    # block 0x38: 252 bytes (movs r0, #60 -> #252), its new-game initializer FR_PlayInit. HOENN_SAVE_COMPAT=1
    # (save_compat.py, notes/SAVE_PKHEX.md): it keeps Black 2's 60 (the records after its footer, save_compat's hooks)
    compat = _save_compat().enabled()
    o = PLAY_SIZE_FN - ARM9
    assert struct.unpack_from('<HH', arm9, o) == (0x2000 | PLAY_B2_SIZE, 0x4770), 'block 0x38 size function is not Black 2\'s'
    if not compat:
        struct.pack_into('<H', arm9, o, 0x2000 | PLAY_SIZE)
    o = PLAY_INIT_LIT - ARM9
    assert struct.unpack_from('<I', arm9, o)[0] == 0x0200E0F5 and struct.unpack_from('<I', arm9, o - 4)[0] == PLAY_SIZE_FN | 1
    struct.pack_into('<I', arm9, o, sym['FR_PlayInit'] | 1)
    _save(path9, arm9)
    path, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(path, itcm + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    bl = _roamers()._bl
    at, old, new = SHOP_CALL
    p, d = _load(code, 'arm9_ov036.bin')
    assert bytes(d[at - OV036:at - OV036 + 4]) == bl(at, old), 'ov036 ShopUI_Init: not Black 2\'s call'
    d[at - OV036:at - OV036 + 4] = bl(at, sym[new] & ~1)
    _save(p, d)
    p, d = _load(code, 'arm9_ov012.bin')
    level_helper = _battle_tower().ov033_code()[2]
    at = TOWER_LEVEL_CALL
    assert bytes(d[at - OV012:at - OV012 + 4]) == bl(at, level_helper), 'run frontier_core after battle_tower (its level call)'
    d[at - OV012:at - OV012 + 4] = bl(at, sym['FR_TowerLevelShim'] & ~1)
    for cmd, (old, new) in COMMANDS.items():
        e = EVCMD_TABLE - OV012 + 4 * cmd
        assert struct.unpack_from('<I', d, e)[0] == old, f'EVCMD_TABLE[{cmd}] is not Black 2\'s'
        struct.pack_into('<I', d, e, sym[new] | 1)
    _save(p, d)
    shops = '; '.join(f'shop {s}: ' + ', '.join(f'{n.lower()} {c}' for _, c, n in r) for s, r in info['shops'])
    tut = '; '.join(f'tutor {s}: ' + ', '.join(f'{n.lower()} {c}' for _, _, c, n in r) for s, r in info['tutors'])
    return (f'frontier_core: {len(blob)} B of ITCM at {base:#x} (arena from {end:#x}); commands 230 FrGet, 232 FrOp; '
            f'Battle Tower Open Level (mode 5): opponents at the highest level of the three entered, at least 60; '
            + (f'save block 0x38 {PLAY_B2_SIZE} B, records after its footer (HOENN_SAVE_COMPAT=1); ' if compat else
               f'save block 0x38 {PLAY_B2_SIZE} -> {PLAY_SIZE} B (records {(PLAY_SIZE - PLAY_B2_SIZE) // 2} keys); ') +
            f'BP awards {info["rows"]} rows, divisors {info["div"]}; banned {len(info["banned"])}; {shops}; {tut}')

if __name__ == '__main__':          # python3 frontier_core.py: the data and the code size at a dummy base
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym, info = build(0x01FFD000, tmp)
        print(open(os.path.join(tmp, 'frontier_core_data.h')).read())
        print(len(blob), {k: hex(v) for k, v in sym.items() if k.startswith('FR_')})
