"""Emerald's Battle Pike (frontier_pike, 2026-10-12; notes/FRONTIER_PIKE.md). HOENN_VERSION=emerald only: Sapphire and
Ruby builds return before touching anything. In the patch lists after emerald_mech, frontier_core and
frontier_factory_dome (its battle-line hooks go into ITCM after theirs; its other code into the Frontier code area, which
needs frontier_factory_dome's arc 211 files first).

apply(files):
  1. the Pike's data (data/emerald/frontier_pike.json, converter/gen_frontier_pike.py) as one file appended to a/0/0/8
     (the map chunks archive: 32 MB reserve; no map matrix names it, so the field never loads it as a chunk); the code
     reads its parts with GFL_ArcSysReadRange. Sections: 300 Frontier trainers (24 bytes: Black 2 class, overworld
     sprite, set list offset and count, name), their set lists (u16), 882 sets (16 bytes), Lucy's two parties (24 bytes a
     Pokémon), the wild room's tables (12 bytes), the 25 people of the empty room (6 bytes).
  2. the Pike's three battle slots, trainer ids 529-531 (Black 2 ids no Hoenn trainer may take: their defeat flags are
     the opening's story flags, data/hoenn_trainers.json "_doc"; the Pike never sets them): a/0/9/1 records (single
     style, Emerald's Frontier AI: check bad moves + try to faint + check viability = Black 2 BASIC | EVAL_ATTACK |
     EXPERT, + TAG_STRATEGY, no money, no items) and a one-Pokémon a/0/9/2 party; frontier_pike.c fills class, name and
     party at battle time (529/530: the Frontier trainers the room chose; 531: Lucy, class LUCY_CLASS, her name).
  3. frontier_pike.c (all but the battle's trainer-line hooks) compiled with clang and linked into the Frontier code area
     (b2tools/patches/frontier_area.py: main RAM 0x023D0000+, loaded at boot, resident in battles too; emerald_itcm
     2026-10-12: it was 7.6 KB of ITCM, and ITCM ran out when sprite_switch grew).
apply_code(code):
  3. frontier_pike.c -DPK_PART_LINES (PK_TrainerMsgExists / PK_TrainerMsgLoad: they run inside the battle) linked into
     ITCM after the other ITCM patches (the arena literal moves on); frontier_area.install (the area's boot loader, once
     per build: the first user installs it).
  4. ov012 EVCMD_TABLE[290] (BoxAdd, unused by every Black 2 and Hoenn script; args var, any, any, any; permission 7)
     -> PK_Cmd.
  5. call sites redirected (each checked to be Black 2's call first):
     arm9 0x02018082 (BtlSetup_SetWildNormal) and 0x02018190 (BtlSetup_LoadTrainerBase): BtlSetup_LoadPlayerParty ->
       PK_LoadPlayerParty (the battle takes the challenge's three);
     arm9 0x020182b8 (BtlSetup_SetTrainer1v1Single), 0x02018388 / 0x020183a0 (BtlSetup_SetTrainer1v2): BtlSetup_LoadTrainer
       -> PK_LoadTrainer (the Pike's slots: Frontier trainer / Lucy, their parties, no experience);
     ov036 0x021a196e (EventWildBattleCall_CreateStatic): FieldEncount_SetupNormal -> PK_EncSetupNormal (the wild room's
       Pokémon get their Pike moves);
     ov036 0x021815e6 and 0x02181afe (the field's per-step checks): CheckCallRandomEncounter -> PK_CheckEncounter (Emerald's
       step check in the wild room starts its battle script);
     ov167 0x021b3b28 (the battle's mid-battle trainer lines, types 13-20): TrainerMsg_CheckExists -> PK_TrainerMsgExists
       and the TrainerMsg_Load call inside trainers.py's rewrite of ov167 0x021d0288 -> PK_TrainerMsgLoad: a beaten Pike
       trainer says Emerald's speechLose line (the RoomNormal text file, PKL_ROOM_LOSE + its Frontier index, record keys
       93/94), Lucy "Urk…" / "Darn!"; the slots' Black 2 lines are never shown.
Code space: the Frontier code area and ITCM (savestates made on other ROMs lack them: test from cold-boot states of
this ROM)."""
import os, re, sys, json, struct, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import version, narcio  # noqa: E402
import frontier_area  # noqa: E402

ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV012, OV036, OV167 = 0x021503C0, 0x0217F600, 0x021998C0
EVCMD_TABLE, PK_COMMAND, BOXADD = 0x0216B538, 290, 0x02157025
# (call site, module base, file, old target, new symbol)
CALLS = [(0x02018082, ARM9, 'arm9.bin', 0x02017F14, 'PK_LoadPlayerParty'),
         (0x02018190, ARM9, 'arm9.bin', 0x02017F14, 'PK_LoadPlayerParty'),
         (0x020182B8, ARM9, 'arm9.bin', 0x02017E54, 'PK_LoadTrainer'),
         (0x02018388, ARM9, 'arm9.bin', 0x02017E54, 'PK_LoadTrainer'),
         (0x020183A0, ARM9, 'arm9.bin', 0x02017E54, 'PK_LoadTrainer'),
         (0x021A196E, OV036, 'arm9_ov036.bin', 0x021A1BCC, 'PK_EncSetupNormal'),
         (0x021815E6, OV036, 'arm9_ov036.bin', 0x02182AF8, 'PK_CheckEncounter'),
         (0x02181AFE, OV036, 'arm9_ov036.bin', 0x02182AF8, 'PK_CheckEncounter'),
         (0x021B3B28, OV167, 'arm9_ov167.bin', 0x02030548, 'PK_TrainerMsgExists')]
# the battle's trainer-line print (ov167 0x021d0288, rewritten by the trainers patch: battle_trainer_msg): its call of
# TrainerMsg_Load is found in those 68 bytes and redirected to PK_TrainerMsgLoad
BTL_TRAINER_MSG, BTL_TRAINER_MSG_END, TRAINERMSG_LOAD = 0x021D0288, 0x021D0288 + 68, 0x020305D8
DATA = os.path.join(ROOT, 'data', 'emerald', 'frontier_pike.json')
TR_A, TR_B, TR_LUCY = 529, 530, 531
ZONE_WILD, WILD_SCRIPT = 403, 3        # the wild room's zone and its battle script (0806_room_..._RoomWildMons.s)
# Black 2 object codes of the Pike's people: the Frontier attendant (pokeemerald LINK_RECEPTIONIST = pokeruby WOMAN_6,
# data/sprite_map.json: 65), the gentleman (44), Black 2's field Pokémon Kirlia 4410 / Dusclops 4485 (a/2/0/8) and Lucy
# (frontier_core's Frontier Brain sheet 299, Emerald's own picture)
OBJ = dict(ATTENDANT=65, GENTLEMAN=44, KIRLIA=4410, DUSCLOPS=4485, LUCY=299)   # Lucy: frontier_core's sheet (FRONTIER.md 5)
LUCY_CLASS = 31          # Lucy's battle class: frontier_core's Brain slot (FRONTIER.md 5: picture, "Pike Queen")
AI = 0x1 | 0x2 | 0x4 | 0x80                 # AI_FLAG_BASIC | EVAL_ATTACK | EXPERT | TAG_STRATEGY (constants/tr_ai.h)
STATE = {}

def blob():
    """(bytes, {section: offset}) of the Pike's data file."""
    d = json.load(open(DATA, encoding='utf-8'))
    tr, lists = bytearray(), bytearray()
    for t in d['trainers']:
        name = [ord(c) for c in t['name']][:7] + [0xFFFF]
        name += [0xFFFF] * (8 - len(name))
        tr += struct.pack('<4H8H', t['b2_class'], t['sprite'], len(lists) // 2, len(t['sets']), *name)
        lists += struct.pack(f'<{len(t["sets"])}H', *t['sets'])
    sets = b''.join(struct.pack('<6HBBH', s['species_id'], *(s['move_ids'] + [0] * 4)[:4], s['item_id'], s['nature'], s['ev'], 0)
                    for s in d['sets'])
    lucy = b''.join(struct.pack('<HHBB6B4H2H', m['species_id'], m['item_id'], m['iv'], m['nature'], *m['evs'], *m['move_ids'], 0, 0)
                    for party in d['lucy'] for m in party)
    wild = b''.join(struct.pack('<HBB4H', m['species_id'], m['delta'], 0, *m['move_ids'])
                    for mode in ('50', 'open') for tab in d['wild'][mode] for m in tab)
    npcs = b''.join(struct.pack('<H3BB', n['sprite'], *n['speech'], 0) for n in d['npcs'])
    out, offs = bytearray(32), {}
    for name, part in (('TRAINERS', tr), ('LISTS', lists), ('SETS', sets), ('LUCY', lucy), ('WILD', wild), ('NPCS', npcs)):
        while len(out) % 4: out += b'\0'
        offs[name] = len(out); out += part
    struct.pack_into('<4sHH', out, 0, b'PIKE', len(d['trainers']), len(d['sets']))
    assert len(d['trainers']) == 300 and len(d['sets']) == 882 and len(d['npcs']) == 25 and len(lucy) == 6 * 24
    return bytes(out), offs, d

def apply(files):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    data, offs, d = blob()
    chunks = narcio.load(files, 8)
    STATE['dat'] = len(chunks); STATE['offs'] = offs; STATE['high_tier'] = d['high_tier']
    chunks.append(data)
    narcio.save(files, 8, chunks)
    tr, party = narcio.load(files, 91), narcio.load(files, 92)
    for tid, cls in ((TR_A, 2), (TR_B, 2), (TR_LUCY, LUCY_CLASS)):
        tr[tid] = struct.pack('<4B4HIBBH', 0, cls, 0, 1, 0, 0, 0, 0, AI, 0, 0, 0)
        party[tid] = struct.pack('<4BHH', 0, 0, 50, 0, 25, 0)        # (Pikachu Lv. 50: replaced at battle time)
    narcio.save(files, 91, tr); narcio.save(files, 92, party)
    syms, abase, asize = frontier_area.add(files, 'frontier_pike', build)
    STATE.update(syms=syms, abase=abase, asize=asize)
    return (f'frontier_pike: data a/0/0/8 member {STATE["dat"]} ({len(data)} B: {", ".join(f"{k} @{v}" for k, v in offs.items())}); '
            f'battle slots {TR_A}/{TR_B}/{TR_LUCY}; code {asize} B in the Frontier code area at {abase:#x} '
            f'(arc 211 file {frontier_area.STATE["file"]})')

def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_', os.path.join(HERE, 'roamers.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def data_header():
    o = STATE['offs']
    lines = ['/* generated by b2tools/patches/frontier_pike.py */', '#define PK_ARC 8', f'#define PK_DAT {STATE["dat"]}']
    lines += [f'#define PK_OFF_{k} {v}' for k, v in o.items()]
    lines += [f'#define PK_HIGH_TIER {STATE["high_tier"]}', '#define PK_N_NPCS 25', f'#define PK_ZONE_WILD {ZONE_WILD}',
              f'#define PK_WILD_SCRIPT {WILD_SCRIPT}']
    lines += [f'#define PK_OBJ_{k} {v}' for k, v in OBJ.items()]
    inc = open(os.path.join(ROOT, 'src', 'field_scripts', 'scenes', 'frontier_pike_lines.inc')).read()
    for name, key in (('LOSE', 'PKL_ROOM_LOSE'), ('LUCY_LOSE', 'PKL_ROOM_LUCY_LOSE')):
        lines.append(f'#define PK_LINE_{name} ' + re.search(rf'#define {key} (\d+)', inc).group(1))
    room = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']['BattleFrontier_BattlePikeRoomNormal']
    lines.append(f'#define PK_TEXT_ROOM {room["own_text"]}     /* the room\'s text file (script texts, a/0/0/3) */')
    return '\n'.join(lines) + '\n'

def build(base, workdir, lines=False):
    """frontier_pike.c linked at base: the Frontier code area's part (lines=False, frontier_area.link) or the battle's
    trainer-line hooks for ITCM (lines=True: -DPK_PART_LINES, roamers.link: code only, no RAM of its own)."""
    open(os.path.join(workdir, 'frontier_pike_data.h'), 'w').write(data_header())
    import save_compat                                   # HOENN_SAVE_COMPAT=1: the records' offset (notes/SAVE_PKHEX.md)
    obj = frontier_area.compile(os.path.join(HERE, 'frontier_pike.c'), workdir,
                                (['-DPK_PART_LINES'] if lines else []) + save_compat.cflags())
    return _roamers().link(obj, base) if lines else frontier_area.link(obj, base)

ITCM_SYMS = ('PK_TrainerMsgExists', 'PK_TrainerMsgLoad')     # (the rest are the Frontier code area's)

def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())

def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)

def apply_code(code):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    assert 'syms' in STATE, 'frontier_pike: apply() must run first (same patch)'
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    base = ITCM_BASE + size
    path9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'run frontier_pike after the other ITCM patches (the arena literal)'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob_, isym = build(base, tmp, lines=True)
    assert sorted(k for k in isym if k.startswith('PK_')) == sorted(ITCM_SYMS), sorted(isym)
    sym = {k: v for k, v in STATE['syms'].items() if k.startswith('PK_')}
    assert not set(sym) & set(ITCM_SYMS), 'the trainer-line hooks belong to the ITCM part'
    sym.update(isym)
    end = (base + len(blob_) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    _save(path9, arm9)
    path, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(path, itcm + blob_ + bytes(end - base - len(blob_)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    loader = frontier_area.install(code)
    bl = _roamers()._bl
    for at, mbase, name, old, new in CALLS:
        p, d = _load(code, name)
        assert bytes(d[at - mbase:at - mbase + 4]) == bl(at, old), f'{name} {at:#x}: not Black 2\'s call (another patch?)'
        d[at - mbase:at - mbase + 4] = bl(at, sym[new] & ~1)
        _save(p, d)
    p, d = _load(code, 'arm9_ov167.bin')
    sites = [a for a in range(BTL_TRAINER_MSG, BTL_TRAINER_MSG_END - 3, 2)
             if bytes(d[a - OV167:a - OV167 + 4]) == bl(a, TRAINERMSG_LOAD)]
    assert len(sites) == 1, f'ov167 {BTL_TRAINER_MSG:#x}: {len(sites)} calls of TrainerMsg_Load (trainers patch first)'
    d[sites[0] - OV167:sites[0] - OV167 + 4] = bl(sites[0], sym['PK_TrainerMsgLoad'] & ~1)
    _save(p, d)
    p, d = _load(code, 'arm9_ov012.bin')
    e = EVCMD_TABLE - OV012 + 4 * PK_COMMAND
    assert struct.unpack_from('<I', d, e)[0] == BOXADD, f'EVCMD_TABLE[{PK_COMMAND}] is not Black 2\'s'
    struct.pack_into('<I', d, e, sym['PK_Cmd'] | 1)
    _save(p, d)
    return (f'frontier_pike: {STATE["asize"]} B in the Frontier code area at {STATE["abase"]:#x}, battle lines {len(blob_)} B '
            f'of ITCM at {base:#x} (arena from {end:#x}); command {PK_COMMAND} EmPike; {len(CALLS)} calls redirected; '
            f'data member {STATE["dat"]}; {loader}')

if __name__ == '__main__':          # python3 frontier_pike.py: the data and the two parts' sizes at dummy bases
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    data, offs, _ = blob()
    STATE.update(dat=9999, offs=offs, high_tier=849)
    with tempfile.TemporaryDirectory() as tmp:
        b, sym = build(frontier_area.FRAM_BASE, tmp)
        print(len(data), offs, 'area part', len(b), {k: hex(v) for k, v in sym.items() if k.startswith('PK_')})
    with tempfile.TemporaryDirectory() as tmp:
        b, sym = build(0x01FFD000, tmp, lines=True)
        print('ITCM part', len(b), {k: hex(v) for k, v in sym.items() if k.startswith('PK_')})
