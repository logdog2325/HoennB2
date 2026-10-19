"""Pokémon Emerald NDS: Emerald's rematches (emerald_rematch, 2026-10-18; notes/EMERALD_REMATCH.md). HOENN_VERSION=emerald
only: Sapphire and Ruby builds return before touching anything. Last in the patch lists (after frontier_pyramid: it
chains onto the battle trainer-line hook frontier_pike / frontier_pyramid put there; nothing after it hooks the same).

Black 2's trainer table is full, so Emerald's 288 rematch tiers (converter/gen_trainers.py rematch_rows_emerald) are
"rematch slots", not trainers: a rematch battles the first battle's own trainer id, with the slot's record and party.

apply(files):
  1. the rematch slots (src/trainers/emerald_rematch/NNN_*.s, slot NNN; data/emerald/hoenn_rematch.json "slots"),
     assembled like every trainer (patches/trainers.py assemble_trainer): records -> a/0/8/9 file 1 (slot * 20 bytes;
     file 0 is the trainer message table, which Black 2 reads by file number), parties -> a/0/9/2 entries 814 + slot
     (after Black 2's 814 trainers). Both archives are in build_rom.py RESERVE: the ROM's file table does not move.
  2. emerald_rematch.c compiled into the Frontier code area (frontier_area.add) with the table of the 72 rows
     ("rows": the first battle's id, Gym number (9 + n: a post-game row, 9 = Wally at Victory Road), Liza's id for Tate,
     the tiers' slots, which tiers are doubles) and the ids of src/include/hoenn.h (VAR_EM_REMATCH_DONE_0-4,
     VAR_EM_REMATCH_LEADERS, VAR_EM_REMATCH_POSTGAME, FLAG_DAILY_EM_REMATCHES,
     FLAG_SYS_GAME_CLEAR, FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON).
  3. a report of where each row's trainer stands in this ROM: route trainers as eye-contact NPCs (script 3000 + id /
     5000 + id: their talk script is global 1239, src/field_scripts/emerald/1239_global_trainers.s), Gym Leaders in the
     Gym scripts that use em_gym_rematch (src/include/hoenn_rematch.inc).
apply_code(code):
  4. frontier_area.install (the area's loader: the first user installs it);
  5. arm9 TrainerData_ReadTrainerData (0x020306e0) and TrainerData_ReadParty (0x02030724): the first 8 bytes become
     `ldr r3, [pc]; bx r3; .word EM_RmRead*` (both checked to be Black 2's bytes first): every reader of trainer data
     goes through these two;
  6. the battle's trainer-line call (trainers.py's rewrite of ov167 0x021d0288: the one bl that is not one of the
     rewrite's three other calls; frontier_pike / frontier_pyramid point it at their hooks) -> EM_RmMsgLoad, which
     calls on to what the call pointed at (NEXT_MSGLD, read in apply and checked again here);
  7. ov012 EVCMD_TABLE[299] (BMAnmPlayInv, unused by every Black 2 and Hoenn script) -> EM_RmCmd (EmRematch var, op,
     arg; EVCMD_PERM_TABLE 3 kept: global and zone scripts).
Code: the Frontier code area (main RAM; savestates made on other ROMs lack it: test from cold-boot states)."""
import os, re, sys, glob, json, struct, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import version, narcio  # noqa: E402

ARM9, OV012, OV167 = 0x02004000, 0x021503C0, 0x021998C0
EVCMD_TABLE, COMMAND, CMD_OLD = 0x0216B538, 299, 0x021AB895          # BMAnmPlayInv (ov036 s012B_BMAnmPlayInv)
READ_TRDATA, READ_PARTY = 0x020306E0, 0x02030724                      # TrainerData_ReadTrainerData / _ReadParty
BTL_TRAINER_MSG, BTL_TRAINER_MSG_END = 0x021D0288, 0x021D0288 + 68
REWRITE_OTHER_CALLS = {0x021D4E4C, 0x02024920, 0x021D01D8}           # trainers.py battle_trainer_msg: BtlStr_SetTrainerName,
                                                                     # GFL_WordSetFormatStrbuf, Btlv_PrintStrbuf
B2_TRAINERS = 814                                                    # Black 2's a/0/9/1-2 entries (ids 0-813)
TRDATA_FILE = 1                                                      # a/0/8/9 file 1: the slots' records
SRC = os.path.join(ROOT, 'src', 'trainers', 'emerald_rematch')
DATA = os.path.join(ROOT, 'data', 'emerald', 'hoenn_rematch.json')
MSG = dict(intro=100, intro2=104, defeat=103)                        # converter/gen_trainers.py REMATCH_MSG
GYM_WATTSON = 3
STATE = {}

def _mod(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def _hoenn_h(name):
    m = re.search(rf'^#define {name}\s+(\w+)', open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read(), re.M)
    assert m, f'{name} is not in src/include/hoenn.h (converter/gen_story_ids.py)'
    return int(m.group(1), 0)

def _target(d, base, at):
    h1, h2 = struct.unpack_from('<HH', d, at - base)
    if h1 & 0xF800 != 0xF000 or h2 & 0xF800 != 0xF800: return None
    off = (h1 & 0x7FF) << 12 | (h2 & 0x7FF) << 1
    if off & (1 << 22): off -= 1 << 23
    return at + 4 + off

def msg_call(ov167):
    """(site, target) of the battle trainer-line call in trainers.py's rewrite of ov167 0x021d0288."""
    sites = [(a, _target(ov167, OV167, a)) for a in range(BTL_TRAINER_MSG, BTL_TRAINER_MSG_END - 3, 2)]
    sites = [(a, t) for a, t in sites if t is not None and t not in REWRITE_OTHER_CALLS]
    assert len(sites) == 1, f'ov167 {BTL_TRAINER_MSG:#x}: {[(hex(a), hex(t)) for a, t in sites]} (trainers patch first)'
    return sites[0]

def data_header(rows, next_msgld):
    done = [_hoenn_h(f'VAR_EM_REMATCH_DONE_{i}') for i in range(5)]
    assert len(rows) <= 16 * len(done), len(rows)
    assert all(r['gym'] <= 8 + 8 for r in rows), 'W_POSTGAME holds 8 post-game rows (gym 9-16)'
    def row(r):
        slots = [t['slot'] for t in r['tiers']] + [0xFFFF] * (4 - len(r['tiers']))
        dbl = sum(1 << k for k, t in enumerate(r['tiers']) if t['double'])
        return '{%d, %d, %d, %d, {%s}}' % (r['b2_id'], r['partner'], r['gym'], dbl, ', '.join(map(str, slots)))
    return '\n'.join([
        '/* generated by b2tools/patches/emerald_rematch.py from data/emerald/hoenn_rematch.json and src/include/hoenn.h */',
        f'#define N_ROWS {len(rows)}', f'#define RM_PARTY_BASE {B2_TRAINERS}', f'#define RM_TRDATA_FILE {TRDATA_FILE}',
        f'#define F_DAILY {_hoenn_h("FLAG_DAILY_EM_REMATCHES")}', f'#define F_GAME_CLEAR {_hoenn_h("FLAG_SYS_GAME_CLEAR")}',
        f'#define F_WATTSON {_hoenn_h("FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON")}', f'#define GYM_WATTSON {GYM_WATTSON}',
        f'#define W_LEADERS {_hoenn_h("VAR_EM_REMATCH_LEADERS"):#x}', f'#define W_POSTGAME {_hoenn_h("VAR_EM_REMATCH_POSTGAME"):#x}',
        f'#define MSG_DEFEAT {MSG["defeat"]}',
        f'#define MSG_INTRO {MSG["intro"]}', f'#define MSG_INTRO2 {MSG["intro2"]}', f'#define NEXT_MSGLD {next_msgld:#x}',
        'static const u16 kDoneWork[] = {' + ', '.join(f'{w:#x}' for w in done) + '};',
        'static const RmRow kRows[N_ROWS] = {\n    ' + ',\n    '.join(row(r) for r in rows) + '};']) + '\n'

def build(base, workdir):
    import frontier_area
    open(os.path.join(workdir, 'emerald_rematch_data.h'), 'w').write(data_header(STATE['rows'], STATE['next_msgld']))
    obj = frontier_area.compile(os.path.join(HERE, 'emerald_rematch.c'), workdir)
    return frontier_area.link(obj, base)

def _fixed_size(arc):
    """build_rom.py's fixed size of a RESERVE archive (pad_archives)."""
    from b2files import arc_path
    reserve = _mod('trainers_rm', 'trainers.py').reserved()
    assert arc in reserve, f'a/{arc:03d} has no RESERVE in build_rom.py'
    orig = os.path.getsize(arc_path(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'), arc))
    return (orig + reserve[arc] + 0x1FF) & ~0x1FF

def placed(files, rows):
    """Where each row's trainer stands in this ROM: {'npc': route rows with an eye-contact NPC (script 3000 + id),
    'gym': Leader rows whose Gym script calls em_gym_rematch with that trainer, 'missing': the others}."""
    from zones import parse_entities
    scripts = set()
    for e in narcio.load(files, 126):
        try: scripts |= {n['script'] for n in parse_entities(e)[0]['npcs']}
        except Exception: pass                              # (entries that are not zone entities)
    ids = {}
    for h in ('hoenn_trainers.h', 'hoenn_trainers_emerald.h'):
        ids.update(re.findall(r'#define (TRAINER_\w+)\s+(\w+)', open(os.path.join(ROOT, 'src', 'include', h)).read()))
    for k in list(ids):                                     # (TRAINER_TATE = TRAINER_TATE_AND_LIZA: SPLIT's alias)
        v = ids[k]
        while v in ids and v != ids[v]: v = ids[v]
        ids[k] = int(v) if str(v).isdigit() else None
    called = set()
    for p in glob.glob(os.path.join(ROOT, 'src', 'field_scripts', '**', '*.*'), recursive=True):
        if p.endswith(('.s', '.inc')):
            called |= {ids.get(t) for t in re.findall(r'^\s*em_gym_rematch\s+(\w+)', open(p, encoding='utf-8').read(), re.M)}
    out = {'npc': [], 'gym': [], 'missing': []}
    for r in rows:
        if r['gym']: out['gym' if r['b2_id'] in called else 'missing'].append(r['row'])
        else: out['npc' if 3000 + r['b2_id'] in scripts else 'missing'].append(r['row'])
    return out

def apply(files):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    import frontier_area
    data = json.load(open(DATA))
    rows, slots = data['rows'], data['slots']
    srcs = sorted(glob.glob(os.path.join(SRC, '*.s')))
    assert [int(os.path.basename(p)[:3]) for p in srcs] == list(range(len(slots))), \
        'src/trainers/emerald_rematch: one source per rematch slot, 000 on (HOENN_VERSION=emerald converter/gen_trainers.py)'
    asm = _mod('trainers_rm2', 'trainers.py').assemble_trainer
    recs, parties = [], []
    for p in srcs:
        tr, party = asm(p)
        assert len(tr) == 20 and len(party) <= 108, (p, len(tr), len(party))   # (TrainerUtil_LoadParty's buffer: 108 B)
        recs.append(tr); parties.append(party)
    m89, m92 = narcio.load(files, 89), narcio.load(files, 92)
    assert len(m89) == 1 and len(m92) == B2_TRAINERS, (len(m89), len(m92))
    m89.append(b''.join(recs)); m92 += parties
    narcio.save(files, 89, m89); narcio.save(files, 92, m92)
    sizes = {a: (os.path.getsize(os.path.join(files, 'a', '0', str(a // 10 % 10), str(a % 10))), _fixed_size(a)) for a in (89, 92)}
    for a, (n, cap) in sizes.items():
        assert n <= cap, f'a/0/{a // 10 % 10}/{a % 10}: {n} B > its fixed size {cap} (build_rom.py RESERVE[{a}])'
    # the battle trainer-line call's present target (frontier_pyramid's hook in the full list), for EM_RmMsgLoad to chain to
    ov167 = open(os.path.join(os.path.dirname(files), 'code', 'arm9_ov167.bin'), 'rb').read()
    site, nxt = msg_call(ov167)
    STATE.update(rows=rows, next_msgld=nxt, msg_site=site)
    syms, base, size = frontier_area.add(files, 'emerald_rematch', build)
    STATE.update(syms=syms, base=base, size=size)
    where = placed(files, rows)
    return (f'emerald_rematch: {len(rows)} trainers ({sum(1 for r in rows if 1 <= r["gym"] <= 8)} Gym Leaders, '
            f'{sum(1 for r in rows if r["gym"] > 8)} post-game), {len(slots)} rematch slots: '
            f'records a/0/8/9 file {TRDATA_FILE} ({len(recs) * 20} B), parties a/0/9/2 {B2_TRAINERS}-{B2_TRAINERS + len(parties) - 1} '
            f'({sum(map(len, parties))} B); sizes ' + ', '.join(f'a/0/{a // 10 % 10}/{a % 10} {n}/{cap} ({cap - n} B left)'
                                                             for a, (n, cap) in sizes.items()) +
            f'; {size} B in the Frontier code area at {base:#x}; battle line chains to {nxt:#x}; route trainers placed as NPCs '
            f'{len(where["npc"])}, em_gym_rematch callers {len(where["gym"])}, not found {where["missing"]}')

def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())

def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)

def apply_code(code):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    assert 'syms' in STATE, 'emerald_rematch: apply() must run first (same patch)'
    import frontier_area
    sym = STATE['syms']
    loader = frontier_area.install(code)
    vanilla = open(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build', 'arm9.bin'), 'rb').read()
    p9, arm9 = _load(code, 'arm9.bin')
    for at, name in ((READ_TRDATA, 'EM_RmReadTrainerData'), (READ_PARTY, 'EM_RmReadParty')):
        o = at - ARM9
        assert not at & 3 and bytes(arm9[o:o + 8]) == vanilla[o:o + 8], f'arm9 {at:#x}: not Black 2\'s code (another patch?)'
        arm9[o:o + 8] = bytes.fromhex('004b1847') + struct.pack('<I', sym[name] | 1)     # ldr r3, [pc, #0]; bx r3; .word
    _save(p9, arm9)
    p167, ov167 = _load(code, 'arm9_ov167.bin')
    site, nxt = msg_call(ov167)
    assert (site, nxt) == (STATE['msg_site'], STATE['next_msgld']), 'ov167: the battle line call changed since apply()'
    ov167[site - OV167:site - OV167 + 4] = _mod('roamers_rm', 'roamers.py')._bl(site, sym['EM_RmMsgLoad'] & ~1)
    _save(p167, ov167)
    p12, ov12 = _load(code, 'arm9_ov012.bin')
    e = EVCMD_TABLE - OV012 + 4 * COMMAND
    assert struct.unpack_from('<I', ov12, e)[0] == CMD_OLD, f'EVCMD_TABLE[{COMMAND}] is not Black 2\'s (another patch took it?)'
    struct.pack_into('<I', ov12, e, sym['EM_RmCmd'] | 1)
    _save(p12, ov12)
    return (f'emerald_rematch: TrainerData_ReadTrainerData/_ReadParty -> {sym["EM_RmReadTrainerData"]:#x}/'
            f'{sym["EM_RmReadParty"]:#x}; battle line call {site:#x} -> {sym["EM_RmMsgLoad"]:#x} (then {nxt:#x}); '
            f'command {COMMAND} EmRematch -> {sym["EM_RmCmd"]:#x}; {loader}')

if __name__ == '__main__':          # python3 emerald_rematch.py: the code's size at the area's base (no ROM needed)
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    import tempfile, frontier_area
    STATE.update(rows=json.load(open(DATA))['rows'], next_msgld=0x02164839)
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym = build(frontier_area.FRAM_BASE, tmp)
    print(len(blob), {k: hex(v) for k, v in sym.items() if k.startswith('EM_')})
