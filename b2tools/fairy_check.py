"""Proof of the Fairy type's "no type" sweep and its tables (fairy_core, 2026-10-08; notes/FAIRY.md "Proofs").

    python3 b2tools/fairy_check.py [--rom-code DIR]        static: every #17 in ov167, the patched bytes, the chart
    ../.venv/bin/python b2tools/fairy_check.py --emu ROM STATE OUT.json   (HOENN_TEST_FAIRY_SELFTEST + HOENN_TEST_CHFA ROM)

1. The sweep (static). Black 2 uses type 17 for "no type"; Fairy takes 17 and "no type" moves to 18. Every Thumb
   instruction of ov167 (the battle engine, where types are compared) whose immediate is 17 is listed from the decomp's
   disassembly (`dsd dis`, addresses from the function headers and labels). Each one is either a sentinel fairy.py moves
   to 18, inside a function fairy.py replaces (GetTypeEffectiveness, GetTypeWeaknesses), or shown not to be a type: a
   rule recognises the call it feeds (GetBattleMonStat(mon, 17) = the ability, CheckCondition, event ids, ...), and the
   rest carry a reason read in the code. An unexplained 17 fails the check. The battle's other overlays (ov168 UI is
   fairy_ui's, ov169, ov170 AI) are listed the same way.
2. The patched code (--rom-code: a build's code dir, or its keep/ copy): the 14 sentinel bytes are 18, the replaced
   functions jump to fairy.py's ITCM symbols.
3. The chart: fairy.py builds Gen 6 as Black 2's table + the Fairy row/column + the Steel change; this file types the
   whole published Gen 6 chart out independently (GEN6 below) and compares all 324 entries.
4. --emu: the ROM's self-test (fairy.c FAIRY_SELFTEST, run in a battle) calls the real entry points (GetTypeEffectiveness
   and GetTypeWeaknesses in ov167, PML_MoveGetParam, PML_PersonalGetParamSingle) for every type pair 0-18, every move
   and every species in the four toggle states; every value is compared with what the data and the rules say.
"""
import os, re, sys, json, struct, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
spec = importlib.util.spec_from_file_location('fairy', os.path.join(HERE, 'patches', 'fairy.py'))
fairy = importlib.util.module_from_spec(spec); spec.loader.exec_module(fairy)

# ---- the published Gen 6 chart (attacker rows, defender columns; 0 = no effect, h = 1/2, 1 = x1, 2 = x2), typed out
#      independently of fairy.py's construction
ORDER = 'NOR FIG FLY POI GRO ROC BUG GHO STE FIR WAT GRA ELE PSY ICE DRA DAR FAI'.split()
GEN6 = '''
NOR 1 1 1 1 1 h 1 0 h 1 1 1 1 1 1 1 1 1
FIG 2 1 h h 1 2 h 0 2 1 1 1 1 h 2 1 2 h
FLY 1 2 1 1 1 h 2 1 h 1 1 2 h 1 1 1 1 1
POI 1 1 1 h h h 1 h 0 1 1 2 1 1 1 1 1 2
GRO 1 1 0 2 1 2 h 1 2 2 1 h 2 1 1 1 1 1
ROC 1 h 2 1 h 1 2 1 h 2 1 1 1 1 2 1 1 1
BUG 1 h h h 1 1 1 h h h 1 2 1 2 1 1 2 h
GHO 0 1 1 1 1 1 1 2 1 1 1 1 1 2 1 1 h 1
STE 1 1 1 1 1 2 1 1 h h h 1 h 1 2 1 1 2
FIR 1 1 1 1 1 h 2 1 2 h h 2 1 1 2 h 1 1
WAT 1 1 1 1 2 2 1 1 1 2 h h 1 1 1 h 1 1
GRA 1 1 h h 2 2 h 1 h h 2 h 1 1 1 h 1 1
ELE 1 1 2 1 0 1 1 1 1 1 2 h h 1 1 h 1 1
PSY 1 2 1 2 1 1 1 1 h 1 1 1 1 h 1 1 0 1
ICE 1 1 2 1 2 1 1 1 h h h 2 1 1 h 2 1 1
DRA 1 1 1 1 1 1 1 1 h 1 1 1 1 1 1 2 1 0
DAR 1 h 1 1 1 1 1 2 1 1 1 1 1 2 1 1 h h
FAI 1 2 1 h 1 1 1 1 h h 1 1 1 1 1 2 2 1
'''
SYM = {'0': 0, 'h': 2, '1': 3, '2': 4}

def gen6_published():
    rows = [l.split() for l in GEN6.strip().splitlines()]
    assert [r[0] for r in rows] == ORDER and all(len(r) == 19 for r in rows)
    return [[SYM[v] for v in r[1:]] for r in rows]

# ---- 1. the sweep ---------------------------------------------------------------------------------------------------
def disassemble(outdir):
    subprocess.run([os.path.join(DECOMP, 'tools', 'dsd'), 'dis', '-c', 'config/b2_us/arm9/config.yaml', '-a', outdir],
                   cwd=DECOMP, check=True, capture_output=True)

def scan(asmdir):
    """(module, function, address, instruction) of every instruction in dsd's output, in address order per module"""
    import glob
    out = []
    for path in sorted(glob.glob(os.path.join(asmdir, '*.s')) + glob.glob(os.path.join(asmdir, 'src', '*', '*.s'))):
        b = os.path.basename(path)
        m = re.match(r'_dsd_gap@(\w+?)_\d+\.s$', b)
        mod = m.group(1) if m else os.path.basename(os.path.dirname(path))
        fn = addr = None; mode = 'thumb'
        for line in open(path):
            s = line.strip()
            if not s or s.startswith(('.include', '.global', '.text', '.data', '.bss', '.rodata', '.section', ';', '.balign', '.align')):
                continue
            if s.startswith('thumb_func_start'): mode = 'thumb'; continue
            if s.startswith('arm_func_start'): mode = 'arm'; continue
            if s.startswith(('thumb_func_end', 'arm_func_end')): fn = None; continue
            m = re.match(r'^([A-Za-z_][\w@$.]*): ; (0x[0-9a-f]+)$', s)
            if m: fn, addr = m.group(1), int(m.group(2), 16); continue
            m = re.match(r'^\.L_([0-9a-f]{8}):\s*(.*)$', s)
            if m:
                addr = int(m.group(1), 16); s = m.group(2).split(';')[0].strip()
                if not s: continue
            if fn is None or addr is None: continue
            if s.startswith('.word'): addr += 4; continue
            if s.startswith(('.short', '.hword')): addr += 2; continue
            if s.startswith('.byte'): addr += len(s[5:].split(',')); continue
            if s.startswith('.'): continue
            out.append((mod, fn, addr, s))
            addr += 4 if mode == 'arm' or (re.match(r'^blx?\s+[A-Za-z_.]', s) and not re.match(r'^blx\s+r\d', s)) else 2
    out.sort(key=lambda x: (x[0], x[2]))
    return out

# What a register loaded with 17 feeds (the call within the next instructions that takes it as that argument)
CALL_RULES = {
    ('r1', 'GetBattleMonStat'): 'BattleMon parameter 17 = the ability (BPP_TOKUSEI)',
    ('r1', 'CheckCondition'): 'condition id 17',
    ('r1', 'BattleEvent_CallHandlers'): 'battle event id 17',
    ('r0', 'BattleEventVar_SetRewriteOnceValue'): 'event variable id 17',
    ('r0', 'BattleEventVar_GetValue'): 'event variable id 17',
    ('r0', 'BattleEventVar_RewriteValue'): 'event variable id 17',
    ('r1', 'BattleHandler_PushWork'): 'handler work kind 17',
    ('r2', 'Btlv_StringParam_Setup'): 'string parameter 17',
    ('r1', 'GFL_MsgDataLoadStrbuf'): 'message id 17',
    ('r2', 'GFL_MsgSysLoadData'): 'message file id 17',
    ('r1', 'func_ov167_021b1434'): 'a message parameter of the cure-condition message (func_ov167_021b1434 arg 1)',
    ('r1', 'func_ov167_021abc60'): 'ignored argument: func_ov167_021abc60 returns flow + 0x1ff0 (Conversion 2\'s buffer)',
}
# Read in the code (ov167), each with what the 17 is
MANUAL = {
    0x0219df08: 'struct offset 17 << 6 = 0x440 (ldrh r0, [r0, r1])',
    0x0219df1c: 'struct offset 17 << 6 = 0x440',
    0x021a3bf4: 'func_ov167_021a3ac0: a fail reason code returned in r6 (the next checks return 0x19 ...), not a type',
    0x021a7da6: 'func_ov167_021a7d18: r6 = an event-var stack id + 17 for BattleEventVar_Pop',
    0x021b26d2: 'struct offset 17 << 4 = 0x110 (strb r4, [r1, r0])',
    0x021b2b58: 'func_ov167_021b2864: a state/return code (b .L_021b296e), not a type',
    0x021b2d60: 'func_ov167_021b2d1c: a switch on a sound/scene id (cases 0 1 2 16 17 18 32 33 34) of a 7 x 24 B table',
    0x021b3b32: 'func_ov167_021b3a5c: trainer message id - 17 into a 4-case jump table',
    0x021bae22: 'struct offset 17 << 4 = 0x110',
    0x021bae46: 'struct offset 17 << 4 = 0x110',
    0x021d0ca8: 'func_ov167_021d0c24: struct offset arithmetic (sub r0, #0x11; strb r7, [r4, r0])',
    0x021d0d54: 'GFL_BGSysFillScrArea height argument on the stack (UI)',
    0x021d2aa6: 'func_ov167_021d29bc: a message id (0xe or 0x11 by a flag), lsl #16',
    0x021d2dae: 'func_ov167_021d2d64: a return code (0xe-0x13 by position), not a type',
    0x021d3cf6: 'func_ov167_021d3c34: a text width/character count before GFL_BitmapGetPixelData (UI)',
    0x021d4cc2: 'GFL_MsgSysLoadData file id (17 or another by a flag)',
    0x021c9e36: 'Conversion 2: func_ov167_021abc60(flow, 17) ignores its 2nd argument (returns flow + 0x1ff0)',
    0x021a919e: 'ServerControl_CureCondition: func_ov167_021b1434(.., 17, ..) message parameter',
    0x021c67c8: 'HandlerWorrySeedCheckFail: r4 = 17 is the ability parameter id passed on (GetBattleMonStat right after)',
    0x021b5026: 'ShouldSwitchIfWonderGuard: r4 = 17 kept for the next GetBattleMonStat(mon, 17) (ability)',
    0x0217f9fa: 'ov170 TrAI_ChooseMoveAndTarget: r1 = 0x10 - 0x11 = -1, stored as a byte ("no choice"), not a type',
}

def classify(ins, i):
    mod, fn, addr, s = ins[i]
    if addr in fairy.SENTINELS: return 'SENTINEL', fairy.SENTINELS[addr]
    for at, (name, _, size) in fairy.REPLACED.items():
        if at <= addr < at + size: return 'REPLACED', f'{name} (now in ITCM: 18 types when Fairy is on, Black 2\'s 17 when off)'
    if re.match(r'^(lsl|lsr|asr)\b', s): return 'SHIFT', 'a shift amount'
    if addr in MANUAL: return 'NOT A TYPE', MANUAL[addr]
    m = re.match(r'^mov (r\d), #0x11$', s)
    if m:
        reg = m.group(1)
        for j in range(i + 1, min(i + 6, len(ins))):
            n = ins[j][3]
            c = re.match(r'^bl (\w+)$', n)
            if c:
                why = CALL_RULES.get((reg, c.group(1)))
                if why: return 'NOT A TYPE', f'{why} ({c.group(1)})'
                break
            if re.match(rf'^(mov|add|sub|ldr|ldrb|ldrh) {reg},', n): break     # the register is overwritten
    return 'UNEXPLAINED', ''

def sweep(asmdir, modules=('ov167', 'ov169', 'ov170')):
    ins = [x for x in scan(asmdir) if x[0] in modules]
    rows, bad = [], 0
    for i, (mod, fn, addr, s) in enumerate(ins):
        if not re.search(r'#0x11$', s): continue
        kind, why = classify(ins, i)
        bad += kind == 'UNEXPLAINED'
        rows.append((mod, addr, fn, s, kind, why))
    return rows, bad

# ---- 2. patched bytes -----------------------------------------------------------------------------------------------
def check_code(codedir):
    sym = json.load(open(os.path.join(codedir, 'fairy_symbols.json')))
    ov167 = open(os.path.join(codedir, 'arm9_ov167.bin'), 'rb').read()
    arm9 = open(os.path.join(codedir, 'arm9.bin'), 'rb').read()
    errs = []
    for at in fairy.SENTINELS:
        b = ov167[at - fairy.OV167:at - fairy.OV167 + 2]
        if b[0] != 0x12: errs.append(f'sentinel {at:#x}: {b.hex()}')
    lo, hi = sym['itcm_start'], sym['itcm_end']
    for at, (name, _, _) in list(fairy.REPLACED.items()) + list(fairy.REPLACED_ARM9.items()):
        d, base = (arm9, fairy.ARM9) if at < 0x02100000 else (ov167, fairy.OV167)
        h1, h2, lit = struct.unpack_from('<HHI', d, at - base)
        if (h1, h2) != (0x4B00, 0x4718) or not lo <= (lit & ~1) < hi: errs.append(f'{name} {at:#x} does not jump into ITCM')
    return errs

# ---- 4. the emulator self-test --------------------------------------------------------------------------------------
def expected_selftest():
    """what the self-test must read, from the data (vanilla + fairy.py's edits) and the rules, per state (fairy, classic)"""
    import narcio
    van = fairy.vanilla_chart()
    g6 = gen6_published()
    moves = narcio.load(fairy.VANILLA_FILES, 21)
    pers = narcio.load(fairy.VANILLA_FILES, 16)
    move_type, move_cat = [], []
    tmpl = {m[0]: m for m in fairy.NEW_MOVES}
    for i in range(fairy.FIRST_NEW_MOVE + fairy.N_NEW_MOVES):
        if i < fairy.FIRST_NEW_MOVE:
            t, c = moves[i][0], moves[i][2]
            if i in fairy.RETYPED_MOVES: t = 17
        else:
            r = fairy.move_record(moves[tmpl[i][2]], tmpl[i][3]); t, c = r[0], r[2]
        move_type.append(t); move_cat.append(c)
    classic = [1] * 19
    for k in ('FIRE', 'WATER', 'GRASS', 'ELECTRIC', 'ICE', 'PSYCHIC', 'DRAGON', 'DARK', 'FAIRY'): classic[ORDER.index(k[:3])] = 2
    out = {}
    for s in range(4):
        on, cl = bool(s & 1), bool(s & 2)
        n = 18 if on else 17
        chart = [[(g6[a][d] if on else van[a][d]) if a < n and d < n else 3 for d in range(19)] for a in range(19)]
        weak = [[d for d in range(n) if chart[a][d] in (0, 2)] if a < n else [] for a in range(19)]
        mv = []
        for i, (t, c) in enumerate(zip(move_type, move_cat)):
            if t == 17 and not on: t = 0 if i < fairy.FIRST_NEW_MOVE else fairy.T[tmpl[i][4]]
            if c and cl: c = classic[t]
            mv.append((t, c))
        sp = []
        for i in range(650):
            t1, t2 = pers[i][6], pers[i][7]
            if on and i in fairy.RETYPES: t1, t2 = (fairy.T[x] for x in fairy.RETYPES[i])
            sp.append((t1, t2))
        out[s] = dict(chart=chart, weak=weak, moves=mv, species=sp)
    return out

def run_emu(rom, state, outpath):
    sys.path.insert(0, os.path.join(ROOT, 'work', 'agents', 'fairy_core', 'tools'))
    sys.path.insert(0, HERE)
    from emu import Emu
    sym = json.load(open(os.path.join(os.path.dirname(os.path.abspath(rom)), 'keep', 'fairy_symbols.json'))) \
        if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(rom)), 'keep', 'fairy_symbols.json')) else None
    st = int(os.environ.get('FAIRY_ST_ADDR', '0'), 16) or sym['selftest']
    e = Emu(rom); e.load_state(state); e.run(2)
    e.d.memory.write_long(st, 0x52494146)                      # 'FAIR': the next type lookup runs the self-test
    e.touch(128, 90, 6, 40); e.touch(64, 50, 6, 10)            # FIGHT, the first move: the turn looks types up
    for _ in range(200):
        e.run(10)
        if struct.unpack('<I', bytes(e.d.memory.unsigned[st:st + 4]))[0] == 0x454e4f44: break
    else:
        raise SystemExit('self-test did not run (no DONE)')
    n = struct.unpack('<I', bytes(e.d.memory.unsigned[st + 4:st + 8]))[0]
    buf = bytes(e.d.memory.unsigned[st + 16:st + 16 + n])
    exp = expected_selftest()
    o, errs, counts = 0, [], {}
    for s in range(4):
        cnt = 0
        for a in range(19):
            for d in range(19):
                if buf[o] != exp[s]['chart'][a][d]: errs.append(f'state {s} chart {a} vs {d}: {buf[o]} != {exp[s]["chart"][a][d]}')
                o += 1; cnt += 1
        for a in range(19):
            k = buf[o]; got = list(buf[o + 1:o + 1 + k]); o += 19
            if got != exp[s]['weak'][a]: errs.append(f'state {s} weaknesses of {a}: {got} != {exp[s]["weak"][a]}')
            cnt += 1
        for i, want in enumerate(exp[s]['moves']):
            got = (buf[o], buf[o + 1]); o += 2; cnt += 1
            if got != want: errs.append(f'state {s} move {i}: type/category {got} != {want}')
        for i, want in enumerate(exp[s]['species']):
            got = (buf[o], buf[o + 1]); o += 2; cnt += 1
            if i and got != want: errs.append(f'state {s} species {i}: types {got} != {want}')
        counts[s] = cnt
    res = dict(bytes=n, values_per_state=counts, errors=errs[:50], n_errors=len(errs))
    json.dump(res, open(outpath, 'w'), indent=1)
    return res

def main(argv):
    if '--emu' in argv:
        i = argv.index('--emu'); rom, state, out = argv[i + 1:i + 4]
        res = run_emu(rom, state, out)
        print(f'self-test: {res["bytes"]} B read, values per toggle state {res["values_per_state"]}, errors {res["n_errors"]}')
        for x in res['errors'][:20]: print('  ', x)
        return 1 if res['n_errors'] else 0
    fail = 0
    with tempfile.TemporaryDirectory() as t:
        disassemble(t)
        rows, bad = sweep(t)
    kinds = {}
    for mod, addr, fn, s, kind, why in rows:
        kinds[kind] = kinds.get(kind, 0) + 1
        if '-v' in argv or kind in ('SENTINEL', 'REPLACED', 'UNEXPLAINED'):
            print(f'{mod} {addr:08x} {fn:40s} {s:22s} {kind:11s} {why}')
    print(f'sweep: {len(rows)} instructions with #17 in ov167/ov169/ov170: {kinds}')
    if bad: print(f'FAIL: {bad} unexplained'); fail = 1
    missing = [hex(a) for a in fairy.SENTINELS if a not in {r[1] for r in rows}]
    if missing: print('FAIL: sentinels not found in the disassembly:', missing); fail = 1
    pub, built = gen6_published(), fairy.gen6_chart()
    diff = [(ORDER[a], ORDER[d], built[a][d], pub[a][d]) for a in range(18) for d in range(18) if built[a][d] != pub[a][d]]
    print(f'chart: fairy.py\'s 18x18 == the published Gen 6 chart typed here: {not diff} ({324 - len(diff)}/324)')
    if diff: print('FAIL:', diff); fail = 1
    van = fairy.vanilla_chart()
    gen5 = [[pub[a][d] for d in range(17)] for a in range(17)]
    gen5[ORDER.index('GHO')][ORDER.index('STE')] = gen5[ORDER.index('DAR')][ORDER.index('STE')] = 2
    print(f'chart: Black 2\'s 17x17 == Gen 6 without Fairy and with Gen 5 Steel: {van == gen5}')
    if van != gen5: fail = 1
    if '--rom-code' in argv:
        errs = check_code(argv[argv.index('--rom-code') + 1])
        print(f'code: {len(fairy.SENTINELS)} sentinel bytes = 18, {len(fairy.REPLACED) + len(fairy.REPLACED_ARM9)} functions jump into ITCM: {not errs}')
        for x in errs: print('FAIL:', x); fail = 1
    print('OK' if not fail else 'FAILED')
    return fail

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
