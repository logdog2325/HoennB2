"""Emerald's Battle Pyramid (frontier_pyramid, 2026-10-12; notes/FRONTIER_PYRAMID.md). HOENN_VERSION=emerald only:
Sapphire and Ruby builds return before touching anything. Last in the patch lists (after frontier_pike and rods: it
chains onto their hooks and puts its few ITCM bytes after theirs).

apply(files):
  1. the Pyramid's data (data/emerald/frontier_pyramid.json, converter/gen_frontier_pyramid.py) as one file appended to
     a/0/0/8 (the map chunks archive; no matrix names it): the pick-up items, the wild Pokemon, the trainers' hint text
     groups, Brandon's parties, the banned species (frontier_core's: Black 2's Battle Subway list); the 300 Frontier
     trainers and their sets are frontier_pike's file (found by its 'PIKE' magic);
  2. the engine (frontier_pyramid.c, clang -fropi, frontier_factory_dome's position-independent linker) as another
     file of a/0/0/8: a 64-byte header 'PYRM' (size, allocation size with the engine's RAM, entry offsets), then the code;
  3. the floor's chunk: an 'RD' container (Black 2's Join Avenue kind: its loader calls ov036 0x021c898c with the
     chunk's terrain and props, where the Pyramid's code builds the floor) of the floor model (b2tools/pyramid_models.py,
     built here when missing), a 32x32 terrain of 24-byte cells (ov036 FieldChunkAccessor_RD_GetTerrain) and no props;
     zone 388 (the floor) gets a new 1x1 matrix of it, area 291 (Relic Castle: its textures; interior pack 9, which no
     other area uses) and its own script / text numbers; pack 9 gets the 16 square models and the exit panel (res ids
     PY_RES_SQUARE..+15, PY_RES_STAIRS) with their textures (map set 291) in its texture set;
  4. trainer ids 532 (the floor's Frontier trainers) and 533 (Brandon, class 30 Pyramid King): a/0/9/1 records (single,
     Emerald's Frontier AI) and a one-Pokemon a/0/9/2 party (the engine fills class, name and party at battle time).
apply_code(code):
  5. 4 bytes of ITCM after the other ITCM patches (the engine's address); frontier_pyramid_stub.c -DPART_OV012 into
     ov012 0x02164838-0x021649ec (the handlers of script commands 530/531, unused, with their callbacks: the battle-time
     hooks), -DPART_OV036 into ov036 0x021c898c-0x021c8c34 (Join Avenue's map building: zone 490, which Hoenn never
     uses: the loader and the field's hooks);
  6. calls: ov036 0x0218ac40 (the RD loader's resort call) -> PY_O_RDHook; ov036 0x021815e6 / 0x02181afe (per-step
     checks, frontier_pike's PK_CheckEncounter) -> PY_O_Step; ov036 0x021a196e (wild setup, PK_EncSetupNormal) ->
     PY_O_EncSetup; ov012 0x0215c0fc (the Start menu's Save: EventSave_Create) -> PY_O_SaveMenu; arm9 0x02018082 /
     0x02018190 (PK_LoadPlayerParty) -> PY_I_LoadParty; arm9 0x020182b8 / 0x02018388 / 0x020183a0 (PK_LoadTrainer) ->
     PY_I_LoadTrainer; ov167 0x021b3b28 (PK_TrainerMsgExists) and the battle's trainer-line call (PK_TrainerMsgLoad) ->
     PY_I_MsgExists / PY_I_MsgLoad; script command 530 (Cmd_0212, unused) -> PY_O_Cmd, EVCMD_PERM_TABLE[530] 1 -> 7
     (allowed in zone inits and field loads too); ov012 0x0215bd8a / 0x0215bdc6 (the field Bag's launcher: its start
     data) -> PY_I_BagNew and 0x0215bd9c (its pocket after the party screen) -> PY_I_BagPocket: in the Pyramid the
     Battle Bag opens on its first pocket with items, never an empty one (2026-10-18; frontier_pyramid.c bag_pocket);
  7. save block 0x3e (Black 2's Unity Tower block: 16 bytes, unused in Hoenn): size 16 -> 16 + the Pyramid's state
     (frontier_pyramid.c PySave); its 256-byte slot keeps every other block where it was.
Savestates made on other ROMs lack all this (ITCM, ov036): test from cold-boot states of this ROM."""
import os, re, sys, json, struct, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import version, narcio  # noqa: E402

LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV012, OV036, OV167 = 0x021503C0, 0x0217F600, 0x021998C0
EVCMD_TABLE, PY_COMMAND, CMD_OLD = 0x0216B538, 530, 0x02164839       # Cmd_0212 (func_ov012_02164838)
EVCMD_PERM_TABLE = 0x0216B1F0                                        # a byte per command: bit n = allowed at feature level n
OV036_LO, OV036_HI = 0x021C898C, 0x021C8C34                          # func_ov036_021c898c, 021c89cc, 021c8b40
OV012_LO, OV012_HI = 0x02164838, 0x021649EC                          # Cmd_0212 / Cmd_0213 and their callbacks
CMD531_OLD = 0x0216491D
RD_CALL, RD_OLD = 0x0218AC40, 0x021C898C
SAVE_CALL, SAVE_OLD = 0x0215C0FC, 0x0215C4F8                         # bl EventSave_Create
BLOCK3E_SIZE_FN = 0x0200F128                                         # UnityTowerSave_GetBlockSize: movs r0, #16
STEP_CALLS, ENC_CALL = (0x021815E6, 0x02181AFE), 0x021A196E
PARTY_CALLS, TRAINER_CALLS = (0x02018082, 0x02018190), (0x020182B8, 0x02018388, 0x020183A0)
MSGEX_CALL = 0x021B3B28
BAG_NEW_CALLS, BAG_NEW = (0x0215BD8A, 0x0215BDC6), 0x02034AD0       # ov012 func_ov012_0215bd48 (the field Bag's launcher)
BAG_POCKET_CALL, BAG_SET_POCKET = 0x0215BD9C, 0x020088A4             #   -> func_02034ad0, func_020088a4 (2026-10-18)
BTL_TRAINER_MSG, BTL_TRAINER_MSG_END = 0x021D0288, 0x021D0288 + 68
ZONE_LOBBY, ZONE_FLOOR, ZONE_TOP = 347, 388, 420
TR, TR_BRAIN, BRAIN_CLASS = 532, 533, 30
AREA, PACK = 291, 9                                                  # Relic Castle's area and its interior pack
RES_SQUARE, RES_STAIRS = 480, 496
DATA = os.path.join(ROOT, 'data', 'emerald', 'frontier_pyramid.json')
LINES = os.path.join(ROOT, 'src', 'field_scripts', 'scenes', 'frontier_pyramid_lines.inc')
AI = 0x1 | 0x2 | 0x4 | 0x80
PY_MAGIC = 0x5950
SAVE_STATE = 96                                                      # sizeof(PySave) (frontier_pyramid.c)
STUB_SCRIPTS = dict(PY_SCR_SPOTTED=17, PY_SCR_EXIT=18, PY_SCR_WILD=19, PY_SCR_MENU=20, PY_SCR_MENU_TOP=5)
WORKS = dict(PY_W_SLOT=0x4010, PY_W_STEPS=0x4011, PY_W_DIR=0x4012, PY_W_WILD_LV=0x4013)
STATE = {}

def _mod(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def rooms():
    return version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']

def lines():
    return {m.group(1): int(m.group(2)) for m in re.finditer(r'#define (PYL_\w+) (\d+)', open(LINES).read())}

# --------------------------------------------------------------------------------------------- data file
def data_file(d):
    """(bytes, {section: offset}): PICKUP u16[2][20][10], WILD {u16 species, u8 lvl, u8 ability, u16 moves[4]}[2][20][8],
    GROUPS u8[300], BRANDON {u16 species, item; u8 iv, nature, evs[6]; u16 moves[4], pad[2]}[2][3], BANNED u16[]"""
    core = _mod('frontier_core_py', 'frontier_core.py')
    ban = core.banned()
    pick = b''.join(struct.pack('<10H', *row) for t in (d['pickup_50'], d['pickup_open']) for row in t)
    wild = b''.join(struct.pack('<HBB4H', m['species_id'], m['lvl'], m['ability'], *(m['move_ids'] + [0] * 4)[:4])
                    for k in ('50', 'open') for rnd in d['wild'][k] for m in rnd)
    groups = bytes(d['trainer_text_group'])
    brandon = b''.join(struct.pack('<HHBB6B4H2H', m['species_id'], m['item_id'], m['iv'], m['nature'], *m['evs'],
                                   *(m['move_ids'] + [0] * 4)[:4], 0, 0) for party in d['brandon'] for m in party)
    banned = struct.pack(f'<{len(ban)}H', *ban)
    out, offs = bytearray(16), {}
    for name, part in (('PICKUP', pick), ('WILD', wild), ('GROUPS', groups), ('BRANDON', brandon), ('BANNED', banned)):
        while len(out) % 4: out += b'\0'
        offs[name] = len(out); out += part
    struct.pack_into('<4sI', out, 0, b'PYRD', len(out))
    assert len(pick) == 800 and len(wild) == 2 * 20 * 8 * 12 and len(groups) == 300 and len(brandon) == 144
    return bytes(out), offs, len(ban)

def pike_data(chunks):
    """frontier_pike's data file in a/0/0/8: (member, {section: offset}, high tier), checked against its blob()"""
    pike = _mod('frontier_pike_py', 'frontier_pike.py')
    blob, offs, d = pike.blob()
    hits = [i for i, c in enumerate(chunks) if c[:4] == b'PIKE' and c == blob]
    assert len(hits) == 1, f'frontier_pike\'s data file: {len(hits)} members of a/0/0/8 match (run frontier_pike first)'
    return hits[0], offs, d['high_tier']

# --------------------------------------------------------------------------------------------- the engine
def c_table(name, ctype, rows):
    def f(r): return '{' + ', '.join(f(x) for x in r) + '}' if isinstance(r, (list, tuple)) else str(r)
    dims = ''
    x = rows
    while isinstance(x, (list, tuple)): dims += f'[{len(x)}]'; x = x[0]
    return f'static const {ctype} {name}{dims} = {f(rows)};'

def data_header(d):
    L = lines(); rm = rooms()
    sq = d['squares']
    walls = [[sum(1 << x for x in range(8) if row[x] == '#') for row in s['walls']] for s in sq]
    objs = [[[o['x'], o['y'], 1 if o['kind'] == 'item' else 0, o['move'], o['dir'], o['sight']] for o in s['objects']] for s in sq]
    assert all(len(o) <= 8 for o in objs)
    objs8 = [o + [[0] * 6] * (8 - len(o)) for o in objs]
    tpl = ',\n  '.join('{%d, %d, %d, %d, %d, {%s}}' % (t['num_items'], t['num_trainers'], t['item_positions'], t['trainer_positions'],
                                                    t['run_multiplier'], ', '.join(map(str, t['layout_offsets']))) for t in d['templates'])
    defs = {
        'BAG_SIZE': 0x9EC, 'PY_MAGIC': PY_MAGIC, 'PK_DAT': STATE['pk_dat'], 'PK_HIGH_TIER': STATE['high_tier'],
        'PY_DAT': STATE['dat'], 'PY_N_BANNED': STATE['n_banned'], 'PY_TR': TR, 'PY_TR_BRAIN': TR_BRAIN,
        'PY_ZONE_FLOOR': ZONE_FLOOR, 'PY_ZONE_TOP': ZONE_TOP, 'PY_HIDE_FLAG': 0x40, 'PY_ITEM_BALL': 110,
        'PY_TILE_FLOOR': 0x00800000, 'PY_TILE_WALL': 0x00810001, 'PY_RES_SQUARE': RES_SQUARE, 'PY_RES_STAIRS': RES_STAIRS,
        'PY_TEXT_FLOOR': rm['BattleFrontier_BattlePyramidFloor']['own_text'],
        'PY_START_ITEM0': d['start_items'][0], 'PY_START_ITEM1': d['start_items'][1],
        'PYL_FLOOR_INTRO': L['PYL_FLOOR_INTRO'], 'PYL_FLOOR_LOSE': L['PYL_FLOOR_LOSE'],
        'PYL_FLOOR_BRANDON_LOSE': L['PYL_FLOOR_BRANDON_LOSE'], 'PYL_FLOOR_HINTS': L['PYL_FLOOR_HINTS'],
    }
    defs.update({f'PK_OFF_{k}': v for k, v in STATE['pk_offs'].items()})
    defs.update({f'PY_OFF_{k}': v for k, v in STATE['offs'].items()})
    defs.update(STUB_SCRIPTS); defs.update(WORKS)
    out = ['/* generated by b2tools/patches/frontier_pyramid.py from data/emerald/frontier_pyramid.json */']
    out += [f'#define {k} {v}' for k, v in defs.items()]
    out += ['typedef struct { u8 numItems, numTrainers, itemPos, trainerPos, runMult, lo[8]; } Tpl;',
            'static const Tpl kTpl[16] = {\n  ' + tpl + '};',
            c_table('kTplOptions', 'u8', d['template_options']), c_table('kTplOffsets', 'u8', d['template_offsets']),
            c_table('kSqWalls', 'u8', walls), c_table('kSqExit', 'u8', [s['exit'][0] | s['exit'][1] << 4 for s in sq]),
            c_table('kSqObjN', 'u8', [len(o) for o in objs]), c_table('kSqObj', 'u8', objs8),
            c_table('kBordered', 'u8', d['bordered']), c_table('kPickupSlots', 'u8', d['pickup_slots']),
            c_table('kPickupOffsets', 'u8', d['pickup_offsets']), c_table('kHintTypes', 'u8', d['hint_types']),
            c_table('kTrRange', 'u16', d['trainer_ranges']), c_table('kTrRangeHard', 'u16', d['trainer_ranges_hard']),
            c_table('kWildRate', 'u8', [f['rate'] for f in d['wild_floors']]),
            c_table('kWildSlots', 'u8', [f['slots'] for f in d['wild_floors']]),
            c_table('kBrainStreak', 'u8', d['brain_streaks'])]
    return '\n'.join(out) + '\n'

CFLAGS = ['--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding', '-fno-builtin',
          '-fno-jump-tables', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables', '-fno-exceptions', '-fno-common',
          '-mno-unaligned-access', '-Wall', '-Werror', '-Wno-unused-function']
ENTRIES = ['PY_Cmd', 'PY_RDHook', 'PY_Step', 'PY_EncSetup', 'PY_SaveMenu', 'PY_LoadParty', 'PY_LoadTrainer',
           'PY_MsgExists', 'PY_MsgLoad', 'PY_BagOpen']
HDR = 64

def check_ops():
    """the scripts' op numbers (frontier_pyramid_lib.inc PY_*) = the engine's enum (frontier_pyramid.c)"""
    c = open(os.path.join(HERE, 'frontier_pyramid.c')).read()
    enum = re.findall(r'\b(PY_[A-Z_0-9]+)\b', re.search(r'enum \{ (PY_INIT,.*?)\};', c, re.S).group(1))
    lib = open(os.path.join(ROOT, 'src', 'field_scripts', 'scenes', 'frontier_pyramid_lib.inc')).read()
    for i, name in enumerate(enum):
        m = re.search(rf'#define {name} (\d+)', lib)
        assert m and int(m.group(1)) == i, f'frontier_pyramid_lib.inc {name}: not {i} (the engine\'s order)'

def build_engine(d, workdir):
    open(os.path.join(workdir, 'frontier_pyramid_data.h'), 'w').write(data_header(d))
    obj = os.path.join(workdir, 'frontier_pyramid.o')
    check_ops()
    compat = _mod('save_compat_py', 'save_compat.py').cflags()   # HOENN_SAVE_COMPAT=1: the save offsets (notes/SAVE_PKHEX.md)
    subprocess.run([f'{LLVM}/clang', *CFLAGS, '-fropi', *compat, '-I', workdir, '-c', os.path.join(HERE, 'frontier_pyramid.c'),
                    '-o', obj], check=True)
    fd = _mod('frontier_fd_py', 'frontier_factory_dome.py')
    blob, sym = fd.link_pic(obj)
    state = 0x9EC + 4 + 10 + 5 + 16 + 16 * 4 + 4 + 128 + 0x1A + 64     # sizeof(State) (frontier_pyramid.c), rounded up
    size = HDR + len(blob)
    ents = [HDR + (sym[e] & ~1) for e in ENTRIES]
    head = struct.pack('<4sIII', b'PYRM', size, ((size + 3) & ~3) + state, len(ents)) + struct.pack(f'<{len(ents)}I', *ents)
    head += bytes(HDR - len(head))
    return head + blob, size, state

# --------------------------------------------------------------------------------------------- the floor's chunk
def floor_models():
    rooms_dir = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
    out = os.path.join(rooms_dir, 'BattleFrontier_BattlePyramidFloor')
    meta = os.path.join(out, 'models.json')
    src = [os.path.join(os.path.dirname(HERE), 'pyramid_models.py'), DATA]
    if not os.path.exists(meta) or any(os.path.getmtime(s) > os.path.getmtime(meta) for s in src):
        sys.path.insert(0, os.path.dirname(HERE))
        pm = _mod('pyramid_models_py', os.path.join('..', 'pyramid_models.py'))
        pm.build(out)
    return out, json.load(open(meta))

def rd_container(base_bmd):
    """'RD': model, terrain (u16 32, u16 32, 1024 x 24-byte cells: two planes {normal (0, 4094, 0), d 0} and the tile:
    walkable 0x00800000, as Black 2's interiors), props (u32 count 0: the engine adds the squares)."""
    cell = struct.pack('<6hiiI', 0, 4094, 0, 0, 4094, 0, 0, 0, 0x00800000)
    terrain = struct.pack('<HH', 32, 32) + cell * 1024
    from b2files import gf_container_build
    return gf_container_build('RD', [base_bmd, terrain, struct.pack('<I', 0)])

STATIC_INFO = bytes.fromhex('0000 0000 ffff 0000 0000 0000 ffff 0000 0000 0000 ffff ffff ffff ffff ffff ffff ffff ffff')

def install_floor(files):
    import zoneheaders, nsbtx, b2files
    from b2files import gf_container, gf_container_build
    out, meta = floor_models()
    chunks, mats = narcio.load(files, 8), narcio.load(files, 9)
    base = open(os.path.join(out, meta['models']['base']['file']), 'rb').read()
    chunk = len(chunks); chunks.append(rd_container(base))
    m = len(mats); mats.append(struct.pack('<HHHHI', 0, 0, 1, 1, chunk))
    narcio.save(files, 8, chunks); narcio.save(files, 9, mats)
    headers, hentries = zoneheaders.load(files)
    users = sorted(z for z, h in enumerate(headers) if h['area'] == AREA and z != ZONE_FLOOR)
    lob, hd = headers[ZONE_LOBBY], headers[ZONE_FLOOR]
    for k in ('map_type', 'npc_cache', 'flags', 'weather_word', 'place_display', 'icon_word', 'parent', 'place',
              'bgm0', 'bgm1', 'bgm2', 'bgm3'):
        hd[k] = lob[k]
    r = rooms()['BattleFrontier_BattlePyramidFloor']
    hd.update(matrix=m, area=AREA, scripts=r['own_scripts'], init_scripts=r['own_init'], text=r['own_text'],
              encounters=0x1FFF, enc_slot=6, cam_bound=0xFFFF, fly_x=16, fly_y=0, fly_z=16)
    zoneheaders.save(files, headers, hentries)
    # the square models and the exit panel -> pack 9 (+ their textures, map set 291, into its texture set a/1/7/5)
    packs, btex = narcio.load(files, 226), narcio.load(files, 175)
    magic, secs = gf_container(packs[PACK]); n = len(secs) // 2
    infos, bmds = secs[:n], secs[n:]
    have = {struct.unpack_from('<H', i, 0)[0] for i in infos}
    src = b2files.map_textures(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'), meta['texset'])
    adds = {}
    for k in range(17):
        name = 'stairs' if k == 16 else f'sq{k:02d}'
        res = RES_STAIRS if k == 16 else RES_SQUARE + k
        assert res not in have, f'pack {PACK} already has res {res}'
        infos.append(struct.pack('<HH', res, 0) + STATIC_INFO[4:])
        bmds.append(open(os.path.join(out, meta['models'][name]['file']), 'rb').read())
        for t in meta['models'][name]['textures']: adds[t] = (src, t, t + '_pl')
    packs[PACK] = gf_container_build('AB', infos + bmds)
    btex[PACK] = nsbtx.merge(btex[PACK], list(adds.values()))
    narcio.save(files, 226, packs); narcio.save(files, 175, btex)
    return chunk, m, users

# --------------------------------------------------------------------------------------------- apply
def apply(files):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    d = json.load(open(DATA, encoding='utf-8'))
    chunks = narcio.load(files, 8)
    STATE['pk_dat'], STATE['pk_offs'], STATE['high_tier'] = pike_data(chunks)
    data, offs, nb = data_file(d)
    STATE['dat'] = len(chunks); STATE['offs'] = offs; STATE['n_banned'] = nb
    chunks.append(data)
    with tempfile.TemporaryDirectory() as tmp:
        engine, size, state = build_engine(d, tmp)
    STATE['engine'] = len(chunks); chunks.append(engine)
    narcio.save(files, 8, chunks)
    STATE['floor_chunk'], mat, users = install_floor(files)
    tr, party = narcio.load(files, 91), narcio.load(files, 92)
    for tid, cls in ((TR, 2), (TR_BRAIN, BRAIN_CLASS)):
        tr[tid] = struct.pack('<4B4HIBBH', 0, cls, 0, 1, 0, 0, 0, 0, AI, 0, 0, 0)
        party[tid] = struct.pack('<4BHH', 0, 0, 50, 0, 25, 0)
    narcio.save(files, 91, tr); narcio.save(files, 92, party)
    return (f'frontier_pyramid: data a/0/0/8 member {STATE["dat"]} ({len(data)} B), engine member {STATE["engine"]} '
            f'({size} B code + {state} B RAM), Pike data member {STATE["pk_dat"]}; floor chunk {STATE["floor_chunk"]} (RD, '
            f'matrix {mat}), area {AREA} (other zones on it: {users or "none"}), pack {PACK} + res {RES_SQUARE}-{RES_STAIRS}; '
            f'trainer slots {TR}/{TR_BRAIN}')

# --------------------------------------------------------------------------------------------- apply_code
def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())

def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)

def _target(d, base, at):
    h1, h2 = struct.unpack_from('<HH', d, at - base)
    assert h1 & 0xF800 == 0xF000 and h2 & 0xF800 == 0xF800, f'{at:#x}: not a bl'
    off = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
    if off & (1 << 22): off -= 1 << 23
    return at + 4 + off

def build_stub(part, base, workdir, defs):
    open(os.path.join(workdir, 'frontier_pyramid_stub.h'), 'w').write(
        '/* generated by b2tools/patches/frontier_pyramid.py */\n' + ''.join(f'#define {k} {v:#x}\n' for k, v in defs.items()))
    obj = os.path.join(workdir, f'stub_{part}.o')
    subprocess.run([f'{LLVM}/clang', *CFLAGS, '-fno-pic', f'-DPART_{part}', '-I', workdir, '-c',
                    os.path.join(HERE, 'frontier_pyramid_stub.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'frontier_pyramid_stub.c ({part}) needs {und}'
    return _mod('roamers_py', 'roamers.py').link(obj, base)

def apply_code(code):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    assert 'engine' in STATE, 'frontier_pyramid: apply() must run first (same patch)'
    roam = _mod('roamers_py2', 'roamers.py')
    p9, arm9 = _load(code, 'arm9.bin'); p36, ov36 = _load(code, 'arm9_ov036.bin')
    p12, ov12 = _load(code, 'arm9_ov012.bin'); p167, ov167 = _load(code, 'arm9_ov167.bin')
    # the previous targets of the call sites (frontier_pike's hooks), checked to be the same at every site
    def one(d, base, sites):
        t = {_target(d, base, s) for s in sites}
        assert len(t) == 1, [hex(x) for x in t]
        return t.pop()
    msg_sites = [a for a in range(BTL_TRAINER_MSG, BTL_TRAINER_MSG_END - 3, 2)
                 if ov167[a - OV167 + 1] & 0xF8 == 0xF0 and ov167[a - OV167 + 3] & 0xF8 == 0xF8
                 and _target(ov167, OV167, a) not in (MSGEX_CALL,)]
    nxt = dict(NEXT_PARTY=one(arm9, ARM9, PARTY_CALLS), NEXT_TRAINER=one(arm9, ARM9, TRAINER_CALLS),
               NEXT_MSGEX=one(ov167, OV167, [MSGEX_CALL]), NEXT_STEP=one(ov36, OV036, STEP_CALLS),
               NEXT_ENC=one(ov36, OV036, [ENC_CALL]))
    # the battle trainer-line call (trainers.py's rewrite of ov167 0x021d0288): the one bl into ITCM (frontier_pike's)
    ld = [a for a in msg_sites if 0x01FF8000 <= _target(ov167, OV167, a) < 0x02000000]
    assert len(ld) == 1, f'ov167 {BTL_TRAINER_MSG:#x}: {len(ld)} ITCM calls (frontier_pike first)'
    nxt['NEXT_MSGLD'] = _target(ov167, OV167, ld[0])
    for k in ('NEXT_PARTY', 'NEXT_TRAINER', 'NEXT_MSGEX', 'NEXT_STEP', 'NEXT_ENC', 'NEXT_MSGLD'):   # (frontier_pike's
        # field-time hooks live in the Frontier code area since emerald_itcm 2026-10-12, its battle-line hooks in ITCM)
        assert 0x01FF8000 <= nxt[k] < 0x02000000 or 0x023D0000 <= nxt[k] < 0x023E0000, \
            f'{k} {nxt[k]:#x}: expected frontier_pike\'s hook (ITCM or the Frontier code area)'
    assert _target(ov36, OV036, RD_CALL) == RD_OLD and _target(ov12, OV012, SAVE_CALL) == SAVE_OLD
    # 5a. ITCM: 4 bytes, the engine's address (0 at every reset: ITCM is loaded from the ROM)
    yml = os.path.join(code, 'itcm.yaml'); text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    base = ITCM_BASE + size
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'run frontier_pyramid after the other ITCM patches (the arena literal)'
    end = (base + 4 + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    pi, itcm = _load(code, 'itcm.bin'); assert len(itcm) == size
    _save(pi, itcm + bytes(end - base))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    assert all(_target(ov12, OV012, a) == BAG_NEW for a in BAG_NEW_CALLS) and _target(ov12, OV012, BAG_POCKET_CALL) == BAG_SET_POCKET
    defs = dict(PY_ENG_ADDR=base, PY_TR=TR, PY_TR_BRAIN=TR_BRAIN, BAG_NEW=BAG_NEW, BAG_SET_POCKET=BAG_SET_POCKET, **nxt)
    # 5b. ov012's dead command handlers (530, 531): the hooks that run in battles (ov036 is unloaded then)
    e530, e531 = EVCMD_TABLE - OV012 + 4 * PY_COMMAND, EVCMD_TABLE - OV012 + 4 * (PY_COMMAND + 1)
    assert struct.unpack_from('<II', ov12, e530) == (CMD_OLD, CMD531_OLD), 'EVCMD_TABLE[530/531] are not Black 2\'s'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        iblob, isym = build_stub('OV012', OV012_LO, tmp, defs)
    assert len(iblob) <= OV012_HI - OV012_LO, f'ov012 part {len(iblob)} B > {OV012_HI - OV012_LO}'
    ov12[OV012_LO - OV012:OV012_LO - OV012 + len(iblob)] = iblob
    # 5b. ov036's dead Join Avenue code
    defs.update(PY_ENGINE_FILE=STATE['engine'], PY_FLOOR_CHUNK=STATE['floor_chunk'], PY_ZONE_FLOOR=ZONE_FLOOR,
                PY_ZONE_TOP=ZONE_TOP)
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        oblob, osym = build_stub('OV036', OV036_LO, tmp, defs)
    assert len(oblob) <= OV036_HI - OV036_LO, f'ov036 part {len(oblob)} B > {OV036_HI - OV036_LO}'
    ov36[OV036_LO - OV036:OV036_LO - OV036 + len(oblob)] = oblob
    # 6. the call sites
    bl = roam._bl
    def redirect(d, base, at, new):
        d[at - base:at - base + 4] = bl(at, new & ~1)
    redirect(ov36, OV036, RD_CALL, osym['PY_O_RDHook'])
    for s in STEP_CALLS: redirect(ov36, OV036, s, osym['PY_O_Step'])
    redirect(ov36, OV036, ENC_CALL, osym['PY_O_EncSetup'])
    redirect(ov12, OV012, SAVE_CALL, osym['PY_O_SaveMenu'])
    for s in PARTY_CALLS: redirect(arm9, ARM9, s, isym['PY_I_LoadParty'])
    for s in TRAINER_CALLS: redirect(arm9, ARM9, s, isym['PY_I_LoadTrainer'])
    redirect(ov167, OV167, MSGEX_CALL, isym['PY_I_MsgExists'])
    redirect(ov167, OV167, ld[0], isym['PY_I_MsgLoad'])
    for s in BAG_NEW_CALLS: redirect(ov12, OV012, s, isym['PY_I_BagNew'])     # the Battle Bag's first pocket with items
    redirect(ov12, OV012, BAG_POCKET_CALL, isym['PY_I_BagPocket'])
    struct.pack_into('<II', ov12, e530, osym['PY_O_Cmd'] | 1, osym['PY_O_Cmd'] | 1)   # (531: no script uses it)
    # EVCMD_PERM_TABLE[530] 1 -> 7: the floor's and the top's zone init (MapScript 2) and field loads (3/4) run
    # EmPyr; with Black 2's 1 the guard (FieldScript_OpcodeGuard) stops the VM there (tested: black screen on the floor)
    assert ov12[EVCMD_PERM_TABLE - OV012 + PY_COMMAND] == 1
    ov12[EVCMD_PERM_TABLE - OV012 + PY_COMMAND] = 7
    # 7. save block 0x3e: 16 -> 16 + the Pyramid's state. HOENN_SAVE_COMPAT=1 (save_compat.py, notes/SAVE_PKHEX.md):
    # it keeps Black 2's 16, the state after its footer (save_compat's hooks)
    compat = _mod('save_compat_py2', 'save_compat.py').enabled()
    o = BLOCK3E_SIZE_FN - ARM9
    assert struct.unpack_from('<HH', arm9, o) == (0x2010, 0x4770), 'save block 0x3e\'s size function is not Black 2\'s'
    assert 16 + SAVE_STATE + 4 <= 256
    if not compat:
        struct.pack_into('<H', arm9, o, 0x2000 | (16 + SAVE_STATE))
    for p, dd in ((p9, arm9), (p36, ov36), (p12, ov12), (p167, ov167)): _save(p, dd)
    return (f'frontier_pyramid: ITCM 4 B at {base:#x} (arena from {end:#x}, {0x02000000 - end} B left); ov012 {len(iblob)} of '
            f'{OV012_HI - OV012_LO} B at {OV012_LO:#x}; ov036 {len(oblob)} of {OV036_HI - OV036_LO} B at {OV036_LO:#x}; '
            f'command {PY_COMMAND} EmPyr; '
            f'{2 + len(STEP_CALLS) + len(PARTY_CALLS) + len(TRAINER_CALLS) + 3 + len(BAG_NEW_CALLS) + 1} calls redirected; save block 0x3e ' + ('16 B, state after its footer (HOENN_SAVE_COMPAT=1)' if compat else f'16 -> {16 + SAVE_STATE} B'))

if __name__ == '__main__':          # python3 frontier_pyramid.py: the sizes (dummy data members)
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    d = json.load(open(DATA, encoding='utf-8'))
    data, offs, nb = data_file(d)
    pike = _mod('frontier_pike_py', 'frontier_pike.py')
    _, pk_offs, pd = pike.blob()
    STATE.update(dat=9999, offs=offs, n_banned=nb, pk_dat=9998, pk_offs=pk_offs, high_tier=pd['high_tier'])
    with tempfile.TemporaryDirectory() as tmp:
        engine, size, state = build_engine(d, tmp)
        nxt = dict(NEXT_PARTY=0x01FFF001, NEXT_TRAINER=0x01FFF101, NEXT_MSGEX=0x01FFF201, NEXT_STEP=0x01FFF301,
                   NEXT_ENC=0x01FFF401, NEXT_MSGLD=0x01FFF501)
        defs = dict(PY_ENG_ADDR=0x01FFFE00, PY_TR=TR, PY_TR_BRAIN=TR_BRAIN, BAG_NEW=BAG_NEW, BAG_SET_POCKET=BAG_SET_POCKET, **nxt)
        ib, _ = build_stub('OV012', OV012_LO, tmp, defs)
        defs.update(PY_ENGINE_FILE=9999, PY_FLOOR_CHUNK=9999, PY_ZONE_FLOOR=ZONE_FLOOR, PY_ZONE_TOP=ZONE_TOP)
        ob, _ = build_stub('OV036', OV036_LO, tmp, defs)
    print(f'data {len(data)} B {offs}; engine {size} B + {state} B RAM; ov012 stub {len(ib)} B (room {OV012_HI - OV012_LO}); ov036 stub {len(ob)} B '
          f'(room {OV036_HI - OV036_LO})')
