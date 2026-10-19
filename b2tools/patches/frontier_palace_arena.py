"""The Battle Palace and the Battle Arena (frontier_palace_arena, 2026-10-12; notes/FRONTIER_PALACE_ARENA.md).
HOENN_VERSION=emerald only: Sapphire and Ruby builds return before touching anything ("nothing (Emerald only)").
In the patch lists after rods (it uses the Frontier code area, which needs frontier_factory_dome's arc 211 files first).

apply(files): frontier_palace_arena.c compiled and linked into the Frontier code area (main RAM 0x023D0000+,
  b2tools/patches/frontier_area.py: its image is a file of arc 211 after frontier_factory_dome's), with
  frontier_pa_data.h generated here from pokeemerald and HoennB2's data (nothing typed in by hand):
    Emerald's Palace tables (battle_script_commands.c gBattlePalaceNatureToMoveGroupLikelihood, sBattlePalaceNatureTo-
    FlavorTextId; battle_anim_smokescreen.c gBattlePalaceNatureToMoveTarget), the move groups of GetBattlePalaceMoveGroup
    and the Arena's sMindRatings per move (Gen 3 moves from pokeemerald's gBattleMoves / battle_arena.c; Black 2's later
    moves and HoennB2's Fairy moves by their Black 2 target and power, mapped as Emerald maps the same targets),
    the Brains' parties (frontier_util.c sFrontierBrainsMons[PALACE / ARENA], species / items / moves by name to Black
    2's ids as converter/gen_frontier_emerald.py), their streaks (sFrontierBrainStreakAppearances), the same for the
    Battle Tower's Salon Maiden Anabel (sFrontierBrainsMons[TOWER]: FrontierPA PA_TOWER_*, 2026-10-18), the trainer id
    ranges (data/emerald/frontier.json), the text lines (src/include/frontier_pa_lines.h, b2tools/frontier_pa_text.py)
    and the rooms' text numbers (data/hoenn_interiors.json).
apply_code(code): frontier_area.install (the area's boot loader, once per build), then
  ov012 EVCMD_TABLE[291] (Black 2's BoxAddEx, unused by every script; args var + 8 any) -> PA_Cmd;
  ov167 (the battle): the calls, words and two detours in HOOKS below (each checked to be Black 2's first)."""
import os, re, sys, json, struct, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import version  # noqa: E402
import frontier_area  # noqa: E402

EM = os.path.join(ROOT, 'external', 'pokeemerald')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
OV012, OV167 = 0x021503C0, 0x021998C0
EVCMD_TABLE, PA_COMMAND, BOXADDEX = 0x0216B538, 291, 0x021570A5
# (site, old target, new symbol): `bl` calls in ov167
CALLS = [(0x021B5B1A, 0x021B4A24, 'PA_AIStoreFlags'),        # AISelectAction: StoreSelectableMoveFlag (Palace: by Nature)
         (0x021B5AF4, 0x021BDAF8, 'PA_AISetFight'),          # AISelectAction: BattleAction_SetFightParam (Palace target)
         (0x021B5A6C, 0x021B4DF8, 'PA_AISwitchChecks'),      # AISelectAction: AISwitchChecks (Arena: never)
         (0x021B5FFC, 0x021B5C4C, 'PA_AIPickBest'),          # the AI's replacement: PickBestMonToSwitchInto (Arena: order)
         (0x021B375A, 0x021BBAC4, 'PA_RootCheckCondition'),  # ActionSelectRoot, POKéMON: CheckCondition 33 (Arena)
         (0x021B38C4, 0x021D0AEC, 'PA_RootStringSetup'),     # ActionSelectRoot's message: Btlv_StringParam_Setup (Arena)
         (0x0219F6B0, 0x0219F6FC, 'PA_TurnStart'),           # ServerFlow turn start (flavor text, the Arena's matchup)
         (0x021A087E, 0x021A0A44, 'PA_Obedience'),           # the action's obedience check (Palace: incapable)
         (0x021A3F22, 0x021A3FC4, 'PA_FailMessage'),         # the move-fail message (Palace: "incapable")
         (0x021A0892, 0x021A1940, 'PA_Fight'),               # the fight action (Arena: Mind, Skill)
         (0x021A1A0A, 0x021A3AC0, 'PA_MovePrecheck'),        # the move's precheck (Arena: no Skill when it can't act)
         (0x0219FAAC, 0x021A7F1C, 'PA_TurnEnd'),             # the turn's end (Arena: the judgment)
         (0x021D4F56, 0x021D4F64, 'PA_StdString')]           # the battle's std strings (ours: ids 0x4000 / 0x6000)
# (word address, old value, new symbol): procs the client calls through a pointer (blx: Thumb, bit 0 set)
WORDS = [(0x021B3918, 0x021B3C01, 'PA_SelectFight'),         # ActionSelectRoot's literal: BattleClient_ActionSelectFight
         (0x021D70B4, 0x021B5FA5, 'PA_ChangeProc5'),         # the client command table: command 5's UI proc
         (0x021D70C4, 0x021B5FB1, 'PA_ChangeProc6'),         # ... command 6's UI proc
         (0x021D70A4, 0x021B5F31, 'PA_ShiftProc')]           # ... command 7's (the Shift-style "switch?" prompt)
# (site = function + 4, the two instructions moved into the detour, new symbol)
DETOURS = [(0x021B15D4, '07aa0321', 'PA_MsgSpy'),             # func_ov167_021b15d0 (messages): add r2,sp,#28; movs r1,#3
           (0x021B1438, '071c0799', 'PA_CmdSpy')]             # func_ov167_021b1434 (commands): adds r7,r0,#0; ldr r1,[sp,#28]
NATURES = ['HARDY', 'LONELY', 'BRAVE', 'ADAMANT', 'NAUGHTY', 'BOLD', 'DOCILE', 'RELAXED', 'IMPISH', 'LAX', 'TIMID', 'HASTY',
           'SERIOUS', 'JOLLY', 'NAIVE', 'MODEST', 'MILD', 'QUIET', 'BASHFUL', 'RASH', 'CALM', 'GENTLE', 'SASSY', 'CAREFUL',
           'QUIRKY']
# the Brains (notes/FRONTIER.md 5: frontier_core's classes = their pictures, walking sprites)
SPENSER_CLASS, SPENSER_SPRITE, GRETA_CLASS, GRETA_SPRITE = 8, 107, 34, 207
ANABEL_CLASS = 9                    # the Battle Tower's Salon Maiden (her walking sprite 56: the tower's script sets it)
STATE = {}

def em(path): return open(os.path.join(EM, path), encoding='utf-8').read()

def _gfe():
    spec = importlib.util.spec_from_file_location('gfe_pa', os.path.join(ROOT, 'converter', 'gen_frontier_emerald.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def palace_tables():
    t = em('src/battle_script_commands.c')
    lik = {n: [int(x) for x in m] for n, *m in re.findall(
        r'\[NATURE_(\w+)\]\s*=\s*PALACE_STYLE\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', t)}
    styles = [[a, a + d, al, al + dl] for a, d, al, dl in (lik[n] for n in NATURES)]
    flv_ids = {'GLINT_IN_EYE': 0, 'GETTING_IN_POS': 1, 'GROWL_DEEPLY': 2, 'EAGER_FOR_MORE': 3}
    body = re.search(r'sBattlePalaceNatureToFlavorTextId\[NUM_NATURES\] =\s*\{(.*?)\};', t, re.S).group(1)
    flv = dict(re.findall(r'\[NATURE_(\w+)\]\s*=\s*B_MSG_(\w+)', body))
    hdr = em('include/constants/battle_string_ids.h')
    for k in flv_ids: assert re.search(rf'#define B_MSG_{k}\s+{flv_ids[k]}\b', hdr), k
    s = em('src/battle_anim_smokescreen.c')
    body = re.search(r'gBattlePalaceNatureToMoveTarget\[NUM_NATURES\] =\s*\{(.*?)\};', s, re.S).group(1)
    tgt = dict(re.findall(r'\[NATURE_(\w+)\]\s*=\s*PALACE_TARGET_(\w+)', body))
    tv = {'STRONGER': 0, 'WEAKER': 1, 'RANDOM': 2}
    return styles, [flv_ids[flv[n]] for n in NATURES], [tv[tgt[n]] for n in NATURES]

# ---- moves: Emerald's Palace group (GetBattlePalaceMoveGroup) and Arena Mind rating per move id ------------------
MI_ATTACK, MI_DEFENSE, MI_SUPPORT = 0, 1, 2
MI_MIND1, MI_MINDN, MI_SELECT, MI_USER = 4, 8, 16, 32
EM_TGT = {'SELECTED': 0, 'DEPENDS': 1, 'USER_OR_SELECTED': 2, 'RANDOM': 4, 'BOTH': 8, 'USER': 16, 'FOES_AND_ALLY': 32,
          'OPPONENTS_FIELD': 64}

def em_group(target, power):
    if target in ('SELECTED', 'USER_OR_SELECTED', 'RANDOM', 'BOTH', 'FOES_AND_ALLY'):
        return MI_SUPPORT if power == 0 else MI_ATTACK
    if target in ('DEPENDS', 'OPPONENTS_FIELD'): return MI_SUPPORT
    if target == 'USER': return MI_DEFENSE
    return MI_ATTACK

def b2_move(i):
    files = [f for f in os.listdir(os.path.join(B2, 'data', 'moves')) if f.startswith(f'{i:04d}_')]
    t = open(os.path.join(B2, 'data', 'moves', files[0])).read()
    return re.search(r'Target MOVE_TARGET_(\w+)', t).group(1), int(re.search(r'Power (\d+)', t).group(1))

def move_table():
    """{move id: info byte}; the Black 2 targets of Gen 4/5 moves map to Emerald's targets as the Gen 3 moves show"""
    t = em('src/data/battle_moves.h')
    ids = {m: int(v) for m, v in re.findall(r'#define (MOVE_\w+) (\d+)', em('include/constants/moves.h'))}
    gen3 = {}
    for name, body in re.findall(r'\[(MOVE_\w+)\]\s*=\s*\{(.*?)\n    \}', t, re.S):
        if name == 'MOVE_NONE': continue
        gen3[ids[name]] = (re.search(r'\.target = MOVE_TARGET_(\w+)', body).group(1),
                           int(re.search(r'\.power = (\d+)', body).group(1)))
    mind = {ids[m]: int(v) for m, v in re.findall(r'\[(MOVE_\w+)\]\s*=\s*(-?\d+)', re.search(
        r'sMindRatings\[MOVES_COUNT\] =\s*\{(.*?)\};', em('src/battle_arena.c'), re.S).group(1))}
    n_gen3 = max(gen3) + 1
    # Black 2 target -> Emerald target, from the Gen 3 moves (the majority; every disagreement reported)
    votes = {}
    for i, (tg, pw) in gen3.items():
        b2t, _ = b2_move(i)
        votes.setdefault(b2t, {}).setdefault(tg, 0)
        votes[b2t][tg] += 1
    b2map = {'SELECTED': 'SELECTED', 'USER_OR_ALLY': 'USER', 'ALLY': 'USER', 'FOE': 'SELECTED',
             'ALL_ADJACENT': 'FOES_AND_ALLY', 'ADJACENT_FOES': 'BOTH', 'USER_PARTY': 'USER', 'USER': 'USER', 'ALL': 'USER',
             'RANDOM_FOE': 'RANDOM', 'FIELD': 'USER', 'FOE_SIDE': 'OPPONENTS_FIELD', 'USER_SIDE': 'USER', 'DEPENDS': 'DEPENDS'}
    b2map.update({b: max(v, key=v.get) for b, v in votes.items()})     # (what Emerald's own moves say wins)
    STATE['b2map'] = b2map
    sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location('fairy_pa', os.path.join(HERE, 'fairy.py'))
    fairy = importlib.util.module_from_spec(spec); spec.loader.exec_module(fairy)
    n_b2 = len([f for f in os.listdir(os.path.join(B2, 'data', 'moves')) if f.endswith('.s')])
    out = [0] * (fairy.FIRST_NEW_MOVE + fairy.N_NEW_MOVES)
    for i in range(1, len(out)):
        if i in gen3:
            tg, pw = gen3[i]
            m = mind.get(i, 0)
        elif i < n_b2:
            b2t, pw = b2_move(i)
            tg = b2map[b2t]
            m = 1 if pw and tg != 'DEPENDS' else 0       # (as sMindRatings: every damaging move 1, the counters 0)
        else:
            mid, name, tmpl, ch, _, _ = fairy.NEW_MOVES[i - fairy.FIRST_NEW_MOVE]
            b2t, _ = b2_move(tmpl)
            tg, pw = b2map[b2t], ch['power']
            m = 1 if pw else 0
        info = em_group(tg, pw) | (MI_MIND1 if m == 1 else MI_MINDN if m == -1 else 0)
        if tg == 'SELECTED': info |= MI_SELECT
        if tg == 'USER': info |= MI_USER
        out[i] = info
    assert n_gen3 == 355, n_gen3
    return out, {b: v for b, v in votes.items() if len(v) > 1}

def brains(pairs=(('PALACE', 'ARENA'), ('ARENA', 'FACTORY'))):
    """sFrontierBrainsMons[PALACE], [ARENA] (or the facilities of `pairs`: (facility, the next one in the table)):
    [silver x3, gold x3] each, Black 2 ids"""
    gfe = _gfe()
    gbt = gfe.gbt
    sp = gbt.defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    mv = gbt.defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    it = gbt.defines(f'{B2}/include/constants/items.h', 'ITEM_')
    fu = em('src/frontier_util.c')
    out = []
    for fac, nxt in pairs:
        body = re.search(rf'\[FRONTIER_FACILITY_{fac}\] =\s*\{{(.*?)\n    \}},\n    \[FRONTIER_FACILITY_{nxt}\]', fu, re.S).group(1)
        mons = []
        for b in re.findall(r'\{\s*\.species = (.*?)\n            \}', body, re.S):
            s = re.match(r'(SPECIES_\w+)', b).group(1)
            item = re.search(r'\.heldItem = (ITEM_\w+)', b).group(1)
            iv = re.search(r'\.fixedIV = (\w+)', b).group(1)
            moves = [gfe.MOVE_ALIAS.get(x, x) for x in re.findall(r'MOVE_\w+', re.search(r'\.moves = \{(.*?)\}', b).group(1))]
            mons.append(dict(species=sp[gfe.SPECIES_ALIAS.get(s, s)], item=it[item] if item != 'ITEM_NONE' else 0,
                             iv=31 if iv == 'MAX_PER_STAT_IVS' else int(iv),
                             nature=NATURES.index(re.search(r'\.nature = NATURE_(\w+)', b).group(1)),
                             evs=[int(x) for x in re.search(r'\.evs = \{(.*?)\}', b).group(1).split(',')],
                             moves=[mv[m] for m in moves], names=(s, item, moves)))
        assert len(mons) == 6, (fac, len(mons))
        out.append(mons)
    return out

def brain_streaks(facs=('PALACE', 'ARENA')):
    fu = em('src/frontier_util.c')
    return [[int(x) for x in re.search(rf'\[FRONTIER_FACILITY_{f}\]\s*=\s*\{{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\}}', fu).groups()]
            for f in facs]

def brain_rows(mons):
    """BrainMon initializers: {silver x3}, {gold x3}"""
    return ', '.join('{' + ', '.join('{' + f"{m['species']}, {m['item']}, {m['iv']}, {m['nature']}, "
                     f"{{{', '.join(map(str, m['evs']))}}}, {{{', '.join(map(str, (m['moves'] + [0] * 4)[:4]))}}}" + '}'
                     for m in grp) + '}' for grp in (mons[:3], mons[3:]))

def c_table(name, ctype, rows):
    if rows and isinstance(rows[0], (list, tuple)):
        body = ', '.join('{' + ', '.join(str(x) for x in r) + '}' for r in rows)
        return f'static const {ctype} {name}[{len(rows)}][{len(rows[0])}] = {{{body}}};'
    return f'static const {ctype} {name}[{len(rows)}] = {{{", ".join(str(x) for x in rows)}}};'

def data_header():
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    d = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'frontier.json'), encoding='utf-8'))
    spec = importlib.util.spec_from_file_location('ffd_pa', os.path.join(HERE, 'frontier_factory_dome.py'))
    ffd = importlib.util.module_from_spec(spec); spec.loader.exec_module(ffd)
    styles, flavor, target = palace_tables()
    moves, conflicts = move_table()
    STATE['conflicts'] = conflicts
    b = brains()
    lines = open(os.path.join(ROOT, 'src', 'include', 'frontier_pa_lines.h')).read()
    L = dict(re.findall(r'#define (PA_L_\w+) (\d+)', lines))
    rows = ['{' + brain_rows(f) + '}' for f in b]
    tower = brains((('TOWER', 'DOME'),))[0]
    out = ['/* generated by b2tools/patches/frontier_palace_arena.py */',
           '#include "frontier_pa_lines.h"',
           f'#define PA_SET_BASE {ffd.SET_BASE}', f'#define PA_TRAINERS_FILE {ffd.TRAINERS_FILE}',
           # the Battle Tents (battle_tents 2026-10-18): Verdanturf (Palace rules, tent 0) and Fallarbor (Arena, tent 1)
           f'#define TENT_FILE {ffd.TENT_FILE}', f'#define TENT_LEVEL {ffd.tent_data()["min_level"]}',
           f'#define TENT_TEXT_VERDANTURF {ffd.tent_text_files()["verdanturf"]}',
           f'#define TENT_TEXT_FALLARBOR {ffd.tent_text_files()["fallarbor"]}',
           f'#define TENT_NAME_BASE {ffd.TENT_NAME_BASE}', f'#define TENT_SPEECH_BASE {ffd.TENT_SPEECH_BASE}',
           f'#define PA_HIGH_TIER {d["high_tier"]}',
           f'#define PA_TEXT_PALACE {rooms["BattleFrontier_BattlePalaceBattleRoom"]["own_text"]}',
           f'#define PA_TEXT_ARENA {rooms["BattleFrontier_BattleArenaBattleRoom"]["own_text"]}',
           '#define PA_FD_TEXT PA_TEXT_PALACE      /* (the trainers\' names and greetings: both battle rooms have them) */',
           '#define PA_MSG_PALACE 0x4000', '#define PA_MSG_ARENA 0x6000',
           f'#define PA_SPENSER_CLASS {SPENSER_CLASS}', f'#define PA_SPENSER_SPRITE {SPENSER_SPRITE}',
           f'#define PA_GRETA_CLASS {GRETA_CLASS}', f'#define PA_GRETA_SPRITE {GRETA_SPRITE}',
           f'#define MI_GROUP 3', f'#define MI_ATTACK {MI_ATTACK}', f'#define MI_MIND1 {MI_MIND1}', f'#define MI_MINDN {MI_MINDN}',
           f'#define MI_SELECT {MI_SELECT}', f'#define MI_USER {MI_USER}', f'#define PA_N_MOVES {len(moves)}',
           c_table('kMoveInfo', 'u8', moves),
           c_table('kTrainerRanges', 'u16', d['trainer_ranges']), c_table('kTrainerRangesHard', 'u16', d['trainer_ranges_hard']),
           c_table('kPalaceLikelihood', 'u8', styles), c_table('kPalaceFlavor', 'u8', flavor), c_table('kPalaceTarget', 'u8', target),
           f'static const u16 kFlavorLine[4] = {{{L["PA_L_GLINT"]}, {L["PA_L_POSITION"]}, {L["PA_L_GROWL"]}, {L["PA_L_EAGER"]}}};',
           c_table('kBrainStreak', 'u8', brain_streaks()),
           'typedef struct { u16 species, item; u8 iv, nature, evs[6]; u16 moves[4]; } BrainMon;',
           f'static const BrainMon kBrainMons[2][2][3] = {{{", ".join(rows)}}};',
           # the Battle Tower's Salon Maiden Anabel (2026-10-18): her parties and streaks, her class, her name's line in
           # the tower battle room's text (b2tools/frontier_text.py tower_room: src/include/frontier_tower_lines.h)
           '#include "frontier_tower_lines.h"',
           f'#define PA_ANABEL_CLASS {ANABEL_CLASS}',
           f'#define PA_TOWER_TEXT {rooms["BattleTower_BattleRoom"]["own_text"]}',
           c_table('kTowerStreak', 'u8', brain_streaks(('TOWER',))[0]),
           f'static const BrainMon kTowerBrainMons[2][3] = {{{brain_rows(tower)}}};']
    return '\n'.join(out) + '\n'

def build(base, workdir):
    open(os.path.join(workdir, 'frontier_pa_data.h'), 'w').write(data_header())
    import save_compat                                   # HOENN_SAVE_COMPAT=1: the records' offset (notes/SAVE_PKHEX.md)
    extra = ['-I', os.path.join(ROOT, 'src', 'include')] + save_compat.cflags()
    obj = frontier_area.compile(os.path.join(HERE, 'frontier_palace_arena.c'), workdir, extra)
    return frontier_area.link(obj, base)

def apply(files):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    syms, base, size = frontier_area.add(files, 'frontier_palace_arena', build)
    STATE.update(syms=syms, base=base, size=size)
    c = STATE.get('conflicts')
    return (f'frontier_palace_arena: {size} B in the Frontier code area at {base:#x} (arc 211 file {frontier_area.STATE["file"]})'
            + (f'; Black 2 move targets with mixed Emerald targets (majority used): {c}' if c else ''))

def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())

def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)

def apply_code(code):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    assert 'syms' in STATE, 'frontier_palace_arena: apply() must run first (same patch)'
    sym = STATE['syms']
    done = [frontier_area.install(code)]
    p, d = _load(code, 'arm9_ov167.bin')
    bl = frontier_area.bl
    for at, old, new in CALLS:
        o = at - OV167
        assert bytes(d[o:o + 4]) == bl(at, old), f'ov167 {at:#x}: not Black 2\'s call of {old:#x} (another patch?)'
        d[o:o + 4] = bl(at, sym[new] & ~1)
    for at, old, new in WORDS:
        o = at - OV167
        assert struct.unpack_from('<I', d, o)[0] == old, f'ov167 {at:#x}: not Black 2\'s {old:#x}'
        struct.pack_into('<I', d, o, sym[new] | 1)
    for at, orig, new in DETOURS:
        o = at - OV167
        assert bytes(d[o:o + 4]) == bytes.fromhex(orig), f'ov167 {at:#x}: not Black 2\'s instructions'
        d[o:o + 4] = bl(at, sym[new] & ~1)
    _save(p, d)
    p, d = _load(code, 'arm9_ov012.bin')
    e = EVCMD_TABLE - OV012 + 4 * PA_COMMAND
    assert struct.unpack_from('<I', d, e)[0] == BOXADDEX, f'EVCMD_TABLE[{PA_COMMAND}] is not Black 2\'s (another patch took it?)'
    struct.pack_into('<I', d, e, sym['PA_Cmd'] | 1)
    _save(p, d)
    done.append(f'command {PA_COMMAND} FrontierPA; ov167: {len(CALLS)} calls, {len(WORDS)} words, {len(DETOURS)} detours')
    return '; '.join(done)

if __name__ == '__main__':          # python3 frontier_palace_arena.py: the generated header and the code's size
    import tempfile
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym = build(frontier_area.FRAM_BASE, tmp)
        print(open(os.path.join(tmp, 'frontier_pa_data.h')).read()[:3000])
        print('code', len(blob), 'B;', {k: hex(v) for k, v in sym.items() if k.startswith('PA_')})
        print('conflicts', STATE.get('conflicts'))
