"""Emerald's Trainer Hill (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md). HOENN_VERSION=emerald only: Sapphire and
Ruby builds return before touching anything. Last in the patch lists (after frontier_pyramid and emerald_rematch: it
chains onto the hooks they and frontier_pike put on the same call sites; it reads each site's present target).

apply(files):
  1. trainer ids TH_TR_A / TH_TR_B (534 / 535: Black 2 ids no Hoenn trainer takes, after the Pike's 529-531 and the
     Pyramid's 532/533; converter/gen_trainers.py POOL leaves 529-556 out): a/0/9/1 records (single, Emerald's Trainer
     Hill AI) and a one-Pokemon a/0/9/2 party (the engine fills class, name and party at battle time);
  2. trainer_hill.c compiled into the Frontier code area (frontier_area.add) with trainer_hill_data.h (from
     data/emerald/trainer_hill.json, converter/gen_trainer_hill.py: the four modes' floors' trainers and Pokémon, the
     prize lists; the floors' own text numbers; the call sites' present targets NEXT_*, read from the code binaries);
  0. (first) the Entrance clerk's Mart lists as shop ids 23 / 25 (marts()).
apply_code(code):
  3. frontier_area.install (the area's loader: the first user installs it);
  4. calls redirected to the area (each calls on to the site's previous target): arm9 0x020182b8 / 0x02018388 /
     0x020183a0 (BtlSetup_LoadTrainer's: frontier_pyramid's PY_I_LoadTrainer) -> TH_LoadTrainer; ov167 0x021b3b28
     (TrainerMsg_CheckExists: PY_I_MsgExists) -> TH_MsgExists; the battle's trainer-line call (trainers.py's rewrite of
     ov167 0x021d0288: the one bl that is not one of its three other calls) -> TH_MsgLoad; ov036 0x021815e6 /
     0x02181afe (the field's per-step checks: PY_O_Step) -> TH_Step;
  5. ov012 EVCMD_TABLE[562] (Black 2's Cmd_0232, func_ov036_021af9dc: unused by every Black 2 and Hoenn script; args
     any, var as field_commands.json says) -> TH_Cmd (`ThHill op, var`), EVCMD_PERM_TABLE[562] -> 7 (the floors' zone
     inits run it).
Code: the Frontier code area (main RAM; savestates made on other ROMs lack it: test from cold-boot states)."""
import os, re, sys, json, struct, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import version, narcio  # noqa: E402

ARM9, OV012, OV036, OV167 = 0x02004000, 0x021503C0, 0x0217F600, 0x021998C0
EVCMD_TABLE, EVCMD_PERM_TABLE, COMMAND, CMD_OLD = 0x0216B538, 0x0216B1F0, 562, 0x021AF9DD   # Cmd_0232 (Thumb)
TRAINER_CALLS = (0x020182B8, 0x02018388, 0x020183A0)
MSGEX_CALL = 0x021B3B28
STEP_CALLS = (0x021815E6, 0x02181AFE)
BTL_TRAINER_MSG, BTL_TRAINER_MSG_END = 0x021D0288, 0x021D0288 + 68
REWRITE_OTHER_CALLS = {0x021D4E4C, 0x02024920, 0x021D01D8}     # (trainers.py battle_trainer_msg's other calls)
TR_A, TR_B = 534, 535
AI = 0x1 | 0x2 | 0x4 | 0x80          # Emerald's Trainer Hill AI (CHECK_BAD_MOVE, TRY_TO_FAINT, CHECK_VIABILITY), as the
                                     # Frontier trainers' (frontier_pyramid.py AI)
HIDE_FLAG = 0x20                     # map-local flags 0x21-0x28 hide the floors' trainer NPCs (uid 1-8)
LINE_BASE = 100                      # the floors' texts: line 100 + 5 * (uid - 1) + (0 name, 1 before, 2 win, 3 lose, 4 after)
W = dict(TH_W_A=0x4002, TH_W_SA=0x4003, TH_W_DA=0x4004, TH_W_B=0x4005, TH_W_SB=0x4006, TH_W_DB=0x4007)   # map-local works
SCR_SPOTTED = 11                     # the floors' script "a trainer saw the player"
FLOORS = ['TrainerHill_1F', 'TrainerHill_2F', 'TrainerHill_3F', 'TrainerHill_4F']
DATA = os.path.join(ROOT, 'data', 'emerald', 'trainer_hill.json')
STATE = {}


def _mod(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def _target(d, base, at):
    h1, h2 = struct.unpack_from('<HH', d, at - base)
    assert h1 & 0xF800 == 0xF000 and h2 & 0xF800 == 0xF800, f'{at:#x}: not a bl'
    off = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
    if off & (1 << 22): off -= 1 << 23
    return at + 4 + off


def msg_call(ov167):
    """(site, target) of the battle trainer-line call: the bl in trainers.py's rewrite that is none of its other calls"""
    sites = [a for a in range(BTL_TRAINER_MSG, BTL_TRAINER_MSG_END - 3, 2)
             if ov167[a - OV167 + 1] & 0xF8 == 0xF0 and ov167[a - OV167 + 3] & 0xF8 == 0xF8
             and _target(ov167, OV167, a) not in REWRITE_OTHER_CALLS]
    assert len(sites) == 1, f'ov167 {BTL_TRAINER_MSG:#x}: {len(sites)} candidate calls'
    return sites[0], _target(ov167, OV167, sites[0])


def next_targets(code):
    """the present targets of every call site this patch chains onto (each site's own previous hook)"""
    arm9 = open(os.path.join(code, 'arm9.bin'), 'rb').read()
    ov36 = open(os.path.join(code, 'arm9_ov036.bin'), 'rb').read()
    ov167 = open(os.path.join(code, 'arm9_ov167.bin'), 'rb').read()
    def one(d, base, sites):
        t = {_target(d, base, s) for s in sites}
        assert len(t) == 1, f'{[hex(s) for s in sites]}: different targets {[hex(x) for x in t]}'
        return t.pop()
    site, msgld = msg_call(ov167)
    return dict(NEXT_TRAINER=one(arm9, ARM9, TRAINER_CALLS), NEXT_MSGEX=one(ov167, OV167, [MSGEX_CALL]),
                NEXT_STEP=one(ov36, OV036, STEP_CALLS), NEXT_MSGLD=msgld), site


HILL_ROOMS = ['TrainerHill_Entrance'] + FLOORS + ['TrainerHill_Roof', 'TrainerHill_Elevator']


def floor_texts():
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    zones = [rooms[r]['zone'] for r in HILL_ROOMS]
    assert zones == list(range(zones[0], zones[0] + len(zones))), f'the Hill zones are not in a row: {zones}'
    return [rooms[f]['own_text'] for f in FLOORS], rooms['TrainerHill_1F']['zone'], zones


def data_header(nxt):
    d = json.load(open(DATA, encoding='utf-8'))
    texts, zone1, zones = floor_texts()
    out = ['/* generated by b2tools/patches/trainer_hill.py from data/emerald/trainer_hill.json */',
           'typedef struct { u16 species, item, moves[4]; u8 evs[6], ivs[6]; u16 ability; u8 nature, friendship; u32 personality; } HillMon;',
           'typedef struct { u16 cls, pad; HillMon mons[3]; } HillTr;',
           f'#define TH_TR_A {TR_A}', f'#define TH_TR_B {TR_B}', f'#define TH_HIDE_FLAG {HIDE_FLAG}',
           f'#define TH_LINE_BASE {LINE_BASE}', f'#define TH_ZONE_1F {zone1}', f'#define TH_SCR_SPOTTED {SCR_SPOTTED}',
           f'#define TH_ZONE_FIRST {zones[0]}', f'#define TH_ZONE_LAST {zones[-1]}']
    out += [f'#define {k} {v:#x}' for k, v in W.items()]
    out += [f'#define {k} {v:#x}' for k, v in nxt.items()]
    out.append(f'static const u16 kFloorText[4] = {{{", ".join(map(str, texts))}}};')
    rows = []
    for m in d['modes']:
        fl = []
        for f in m['floors']:
            trs = []
            for t in f['trainers']:
                mons = []
                for p in t['mons']:
                    mv = (p['move_ids'] + [0, 0, 0, 0])[:4]
                    mons.append('{' + f"{p['species_id']}, {p['item_id']}, {{{', '.join(map(str, mv))}}}, "
                                f"{{{', '.join(map(str, p['evs']))}}}, {{{', '.join(map(str, p['ivs']))}}}, "
                                f"{p['ability_id']}, {p['nature_id']}, {p['friendship']}, {p['personality']:#x}u" + '}')
                trs.append('{' + f"{t['b2_class']}, 0, {{{', '.join(mons)}}}" + '}')
            fl.append('{' + ', '.join(trs) + '}')
        rows.append('{' + ', '.join(fl) + '}')
    out.append(f'static const HillTr kHill[4][4][2] = {{{", ".join(rows)}}};')
    out.append('static const u16 kPrize[4][6] = {' + ', '.join('{' + ', '.join(map(str, m['prize_ids'])) + '}' for m in d['modes']) + '};')
    return '\n'.join(out) + '\n'


def build(base, workdir, nxt):
    fa = _mod('frontier_area_th', 'frontier_area.py')
    open(os.path.join(workdir, 'trainer_hill_data.h'), 'w').write(data_header(nxt))
    sc = _mod('save_compat_th', 'save_compat.py')       # HOENN_SAVE_COMPAT=1: the records' offset (notes/SAVE_PKHEX.md)
    obj = fa.compile(os.path.join(HERE, 'trainer_hill.c'), workdir, sc.cflags())
    return fa.link(obj, base)


MART_IDS = (23, 25)                  # the clerk's shop ids (Basic, Expanded): data/hoenn_shops.json's two fillers (no Sapphire
                                     # list, no Hoenn Center uses them; Emerald's shop overlay lists the Hill's marts as later)


def marts(files):
    """the Entrance clerk's two Mart lists (TrainerHill_Entrance_Pokemart_Basic / _Expanded, Emerald's order) as shop ids
    23 / 25 (list files 29 / 31, their counts in a/2/8/3 file 0). a/2/8/2 grows by their bytes (it is no longer kept at
    Black 2's 1300: fairy.py's list file 79 already grows it; savestates made before this ROM read a short file table)."""
    from b2files import arc_path
    d = json.load(open(DATA, encoding='utf-8'))['marts']
    lists, counts = narcio.load(files, 282), narcio.load(files, 283)
    size0 = os.path.getsize(arc_path(files, 282))
    cnt = bytearray(counts[0])
    for sid, key in zip(MART_IDS, ('basic', 'expanded')):
        f, ids = sid + 6, d[key]['ids']
        assert cnt[f] <= 1 and len(lists[f]) <= 2, f'shop {sid}: not the one-item filler (another patch took it?)'
        lists[f] = struct.pack(f'<{len(ids)}H', *ids)
        cnt[f] = len(ids)
    counts[0] = bytes(cnt)
    narcio.save(files, 282, lists); narcio.save(files, 283, counts)
    size = os.path.getsize(arc_path(files, 282))
    return (f'marts: shop {MART_IDS[0]} {len(d["basic"]["ids"])} items, {MART_IDS[1]} {len(d["expanded"]["ids"])} items '
            f'(a/2/8/2 {size0} -> {size} B)')


def apply(files):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    import frontier_area
    mart = marts(files)
    tr, party = narcio.load(files, 91), narcio.load(files, 92)
    for tid in (TR_A, TR_B):
        tr[tid] = struct.pack('<4B4HIBBH', 0, 2, 0, 1, 0, 0, 0, 0, AI, 0, 0, 0)
        party[tid] = struct.pack('<4BHH', 0, 0, 50, 0, 25, 0)
    narcio.save(files, 91, tr); narcio.save(files, 92, party)
    nxt, site = next_targets(os.path.join(os.path.dirname(files), 'code'))
    STATE.update(next=nxt, msg_site=site)
    syms, base, size = frontier_area.add(files, 'trainer_hill', lambda b, w: build(b, w, nxt))
    STATE.update(syms=syms, base=base, size=size)
    return (f'trainer_hill: {size} B in the Frontier code area at {base:#x}; trainer slots {TR_A}/{TR_B}; {mart}; chains to '
            + ', '.join(f'{k} {v:#x}' for k, v in nxt.items()))


def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())


def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)


def apply_code(code):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    assert 'syms' in STATE, 'trainer_hill: apply() must run first (same patch)'
    import frontier_area
    sym = STATE['syms']
    done = [frontier_area.install(code)]
    nxt, site = next_targets(code)
    assert nxt == STATE['next'] and site == STATE['msg_site'], 'trainer_hill: the call sites changed between apply and apply_code'
    bl = frontier_area.bl
    p9, arm9 = _load(code, 'arm9.bin'); p36, ov36 = _load(code, 'arm9_ov036.bin')
    p12, ov12 = _load(code, 'arm9_ov012.bin'); p167, ov167 = _load(code, 'arm9_ov167.bin')
    def redirect(d, base, at, new):
        d[at - base:at - base + 4] = bl(at, new & ~1)
    for s in TRAINER_CALLS: redirect(arm9, ARM9, s, sym['TH_LoadTrainer'])
    redirect(ov167, OV167, MSGEX_CALL, sym['TH_MsgExists'])
    redirect(ov167, OV167, site, sym['TH_MsgLoad'])
    for s in STEP_CALLS: redirect(ov36, OV036, s, sym['TH_Step'])
    e = EVCMD_TABLE - OV012 + 4 * COMMAND
    assert struct.unpack_from('<I', ov12, e)[0] == CMD_OLD, f'EVCMD_TABLE[{COMMAND}] is not Black 2\'s (another patch took it?)'
    struct.pack_into('<I', ov12, e, sym['TH_Cmd'] | 1)
    pe = EVCMD_PERM_TABLE - OV012 + COMMAND
    ov12[pe] = 7                                       # (zone inits, field loads and normal scripts run ThHill)
    for p, dd in ((p9, arm9), (p36, ov36), (p12, ov12), (p167, ov167)): _save(p, dd)
    done.append(f'command {COMMAND} ThHill; {len(TRAINER_CALLS) + len(STEP_CALLS) + 2} calls redirected (from '
                + ', '.join(f'{k} {v:#x}' for k, v in nxt.items()) + ')')
    return '; '.join(done)


if __name__ == '__main__':          # python3 trainer_hill.py: the generated header and the code's size (dummy targets)
    import tempfile
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    fa = _mod('frontier_area_th2', 'frontier_area.py')
    nxt = dict(NEXT_TRAINER=0x02164839, NEXT_MSGEX=0x02164901, NEXT_STEP=0x021C8A01, NEXT_MSGLD=0x02164951)
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym = build(fa.FRAM_BASE, tmp, nxt)
        print(open(os.path.join(tmp, 'trainer_hill_data.h')).read()[:1500])
        print('code', len(blob), 'B;', {k: hex(v) for k, v in sym.items() if k.startswith('TH_')})
