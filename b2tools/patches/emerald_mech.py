"""Pokémon Emerald NDS mechanics (emerald_mech, 2026-10-12; notes/EMERALD.md "Phase 4"). HOENN_VERSION=emerald only:
Sapphire and Ruby builds return before touching anything.

apply_code(code):
  1. emerald_mech.c (two script commands, below) compiled with clang and placed in ITCM after the other ITCM patches
     (the same arena move as roamers.py / hoenn_world.py; so this patch runs after them: last in the patch lists).
  2. ov012 EVCMD_TABLE (0x0216B538): command 533 -> EM_CmdPartySwap, 281 -> EM_CmdTutorCheck, 686 -> EM_CmdPickParty
     (the tag battle's one party menu: Black 2's battle-entry screen, as the Battle Subway / Battle Institute open it,
     with Emerald's multi rule; emerald_mech.c). All three were unused by every Black 2 script and every Hoenn script
     (counted over external/pokebw2/data/field_scripts and src/field_scripts); their argument kinds stay the same as
     field_commands.json says (533: any, any; 281: var, any, any; 686: var), so the decomp's disassembler and
     b2tools/script_check.py still decode them. EVCMD_PERM_TABLE: 533 = 1, 281 = 7, 686 = 7 (allowed in normal and
     global scripts; unchanged).
  3. two calls redirected to emerald_mech.c (the tag battle's party, CALLS): ov036 0x021a1e2c (BtlSetup_SetTrainerLocal ->
     BtlSetup_SetTrainer2v2, the partner battle) -> EM_SetTrainer2v2 (the battle's copy of the player's party keeps its
     first n, n = bits 12-15 of the partner id, 1-3, 0 = Emerald's MULTI_PARTY_SIZE 3; global 2290 passes how many were
     picked); ov166 0x0219cf6e (after a local battle: PokeParty_Copy of the battle's party
     into the player's) -> EM_PartyCopyBack (a shorter battle party goes back into the first slots, the rest stays;
     every other battle: PokeParty_Copy as before). Tested: without them Black 2 let the player send out a 4th Pokémon (and with 2 picks, the 3rd slot).
     The other SetTrainer2v2 caller (ov012 0x021622b8, the Subway/Trial House) is left alone.
  4. arm9 TRAINER_CLASS_BACK_SPRITES (0x02092314, 32 x {u16 class, u16 back sprite}): the entry {37, 5} becomes
     {Steven's class, 5}: the Black 2 class of TRAINER_STEVEN_PARTNER in the Emerald trainer data (emerald_data,
     data/emerald/hoenn_trainer_data.json: 230, a spare class with Steven's front sprite 139; Black 2's own Steven
     class 177 if the data has no partner); back sprite 5 holds Steven's back from Emerald (emerald_art,
     src/sprites/trainer/back/emerald/005-steven). Class 37 (Black 2's Cheren-as-partner class) is HoennB2's Tuber M,
     never a partner. A multi-battle partner is drawn with its class's back sprite (GetTrSpriteBaseDatID, arm9
     0x02030740: Cheren 37 -> 5, Bianca 38 -> 6 in Black 2).

What Black 2 has (findings; decomp symbols + b2tools/armdis.py):
  - Tag battles: CallTrainerMultiBattle partner, foe1, foe2, flags (command 134, s0085_CallTrainerMultiBattle ov036
    0x021a685c) -> EventTrainerBattleCall_Create(.., multi=1, partner, foe1, foe2, flags) -> BtlSetup_SetTrainerLocal
    -> BtlSetup_SetTrainer2v2 (arm9 0x020183b0): the player's whole party (BtlSetup_LoadPlayerParty copies all six:
    in battle all six could be sent out, tested), the partner as client 2, the foes as clients 1 and 3; the battle
    music comes from the last trainer loaded (foe2's class). After a local battle ov166 (func_ov166_0219cef4) copies
    the battle's party back over the player's (PokeParty_Copy). Black 2's own uses (0014.s Striaton trio, 1104.s, 0812.s ...) pass flags 0 and, after a win, heal the
    party when none of the player's Pokémon can battle (PokePartyGetCount mode 2 == 0) before CallTrainerBattleEnd.
    No script command opens the battle-entry party screen outside the Subway/Battle Institute plugins, so EmPickParty
    (emerald_mech.c) runs the Battle Institute's own event for it (func_ov012_02161c88: field closed, ov165 party screen
    in mode 22 = the Subway's entry screen, numbered picks FIRST/SECOND/THIRD, NO ENTRY to take one out, CONFIRM /
    CANCEL, "No more than three Pokémon may enter.") with the regulation in that event's data changed to Emerald's
    multi rule; the choice is moved to party slots 0-2 with EmPartySwap, the battle takes only those three (item 3),
    then the order is put back.
  - Two trainers who see the player at once: Black 2 already fights them together. EventTrainerEye_CheckAll (ov036
    0x021a5d2c) finds the first trainer, and when the player has 2+ Pokémon able to battle it looks for a second one
    (EventTrainerEye_FindClashActor): battle type 2 -> global 1239 L_124E: both walk up, each says its intro line
    (type 0), CallTrainerBattle id1, id2 (BtlSetup_SetTrainer1v2), both flags set. With one able Pokémon only the
    first trainer battles (Emerald's rule too). So Emerald's pairs only need both trainers placed as ordinary
    eye-contact NPCs (script 3000 + id, evType 1, sight in param0) where Emerald puts them.
  - Move tutors: Black 2's tutor commands (MoveTutorCheckPkm, MoveTutorCallPokeSelect, MoveTutorGetMoveID) read
    Black 2's own tutor lists and its personal data's tutor bits (Unova's tutor moves); none of Emerald's 30 tutor
    moves but Sleep Talk is on them. So the compatibility comes from pokeemerald's sTutorLearnsets
    (src/data/pokemon/tutor_learnsets.h), read here at build time into kTutorCompat (one u16 per Black 2 species:
    the 10 Hoenn town tutors, TOWN_TUTORS). Species past Emerald's 386 take their family's Emerald entry (a Gen 4
    evolution its Gen 3 pre-evolution's, a Gen 4 baby the Gen 3 Pokémon it evolves into: Black 2's evolution data);
    the other Gen 4/5 species learn none (as in Emerald, where they do not exist). The learning itself (four moves:
    forget one) is Black 2's own sequence from global 1236 (its text file 615, lines 10-16).
Code space: ITCM (main RAM code: savestates made before this patch need a cold boot / new states, as roamers.py)."""
import os, re, sys, glob, struct, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import version  # noqa: E402

LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV012 = 0x021503C0
EVCMD_TABLE = 0x0216B538
OV036, OV166 = 0x0217F600, 0x0219CE80
# (call site, module base, file, old target, new symbol)
CALLS = [(0x021A1E2C, OV036, 'arm9_ov036.bin', 0x020183B0, 'EM_SetTrainer2v2'),
         (0x0219CF6E, OV166, 'arm9_ov166.bin', 0x020200AC, 'EM_PartyCopyBack')]
COMMANDS = {533: (0x021658C9, 'EM_CmdPartySwap'), 281: (0x02156EC1, 'EM_CmdTutorCheck'),
            686: (0x0216A82D, 'EM_CmdPickParty')}
BACK_SPRITES = 0x02092314                 # arm9 TRAINER_CLASS_BACK_SPRITES: 32 x {u16 class, u16 back sprite}
STEVEN_BACK, OLD_CLASS, B2_STEVEN_CLASS = 5, 37, 177
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
N_SPECIES = 650                           # Black 2 species 0-649 (national numbers)
# Emerald's ten one-time tutors in Hoenn towns (pokeemerald data/scripts/move_tutors.inc); the other 20 of its 30 tutor
# moves are the Battle Frontier's BP tutors (BattleFrontier_Lounge7; frontier_core, 2026-10-12, notes/FRONTIER.md 4).
# kTutorCompat has one bit per tutor (pokeemerald TUTOR_MOVE_* order), all 30.
TOWN_TUTORS = ['SWAGGER', 'ROLLOUT', 'FURY_CUTTER', 'MIMIC', 'METRONOME', 'SLEEP_TALK', 'SUBSTITUTE', 'DYNAMIC_PUNCH',
               'DOUBLE_EDGE', 'EXPLOSION']

def steven_class():
    """Black 2 class of TRAINER_STEVEN_PARTNER (the Emerald trainer data), else Black 2's Steven class."""
    t = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers'].get('TRAINER_STEVEN_PARTNER')
    return t['b2_class'] if t else B2_STEVEN_CLASS

def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_', os.path.join(HERE, 'roamers.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def tutor_data():
    """(tutor names in pokeemerald TUTOR_MOVE_* order, {name: move id}, {B2 species id: set of tutor names})."""
    src = open(os.path.join(EMERALD, 'src', 'data', 'pokemon', 'tutor_learnsets.h')).read()
    order = re.findall(r'#define TUTOR_MOVE_(\w+)\s+(\d+)', open(os.path.join(EMERALD, 'include', 'constants',
                                                                          'party_menu.h')).read())
    order = [n for n, i in sorted(order, key=lambda t: int(t[1])) if n != 'COUNT']
    assert len(order) == 30 and all(t in order for t in TOWN_TUTORS), order
    # move ids: pokeemerald's numbers (Gen 3 moves keep their numbers in Black 2; some names differ: SOFTBOILED)
    em_ids = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define MOVE_(\w+)\s+(\d+)',
                                                                open(os.path.join(EMERALD, 'include', 'constants', 'moves.h')).read())}
    em_moves = dict(re.findall(r'\[TUTOR_MOVE_(\w+)\]\s*=\s*MOVE_(\w+)', src))
    moves = {t: em_ids[em_moves[t]] for t in order}
    assert all(0 < m <= 354 for m in moves.values()), moves
    b2_species = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define SPECIES_(\w+) (\d+)',
                                                                    open(os.path.join(B2, 'include', 'constants', 'species.h')).read())}
    body = src.split('sTutorLearnsets[] =')[1]
    compat = {}
    for name, bits in re.findall(r'\[SPECIES_(\w+)\]\s*=\s*\(([^;]*?)\)\s*,', body, re.S):
        assert name in b2_species, f'pokeemerald species {name} has no Black 2 constant'
        compat[b2_species[name]] = set(re.findall(r'TUTOR\(MOVE_(\w+)\)', bits))
    assert len(compat) == 387, len(compat)
    # Gen 4/5 species: their Gen 3 family's entry (Black 2's evolution data, external/pokebw2/data/evolutions)
    pre, evo = {}, {}
    for f in sorted(glob.glob(os.path.join(B2, 'data', 'evolutions', '*.s'))):
        t = open(f).read()
        m = re.search(r'// SPECIES_(\w+)', t)
        if not m: continue
        for to in re.findall(r'Evolution \w+, [^,]+, SPECIES_(\w+)', t):
            pre.setdefault(b2_species[to], b2_species[m.group(1)])
            evo.setdefault(b2_species[m.group(1)], []).append(b2_species[to])
    inherited = {}
    for s in range(387, N_SPECIES):
        r, n = s, 0
        while r > 386 and r in pre and n < 4: r, n = pre[r], n + 1
        if r > 386:                                   # a baby: the first Gen 3 species it evolves into
            todo, r = [s], None
            while todo and r is None:
                for y in evo.get(todo.pop(), []):
                    if y <= 386: r = y; break
                    todo.append(y)
        if r: compat[s] = compat[r]; inherited[s] = r
    return order, moves, compat, inherited

def data_header():
    order, moves, compat, inherited = tutor_data()
    bit = {t: order.index(t) for t in order}                  # every tutor its own bit (30 of a u32)
    words = [sum(1 << bit[t] for t in compat.get(s, ()) if t in bit) for s in range(N_SPECIES)]
    lines = ['/* generated by b2tools/patches/emerald_mech.py from pokeemerald src/data/pokemon/tutor_learnsets.h */',
             f'#define N_SPECIES {N_SPECIES}', f'#define N_TUTOR {len(order)}',
             'static const u16 kTutorMove[N_TUTOR] = {' + ', '.join(str(moves[t]) for t in order) + '};',
             'static const u8 kTutorBit[N_TUTOR] = {' + ', '.join(str(bit[t]) for t in order) + '};',
             'static const u32 kTutorCompat[N_SPECIES] = {' + ', '.join(str(w) for w in words) + '};']
    learners = {t: sum(1 for w in words if w >> bit[t] & 1) for t in TOWN_TUTORS}
    lines += weather_lines()
    return '\n'.join(lines) + '\n', learners, len(inherited)

# ---- Emerald's crisis weather (emerald_ch10, 2026-10-12; emerald_mech.c EM_ZoneWeather / EM_WeatherTick) -------------
# pokeemerald's Common_EventScript_SetAbnormalWeather callers: kind 1 while FLAG_SYS_WEATHER_CTRL is set (the maps
# Sapphire's crisis has, patches/weather.py CRISIS_MAPS but Sootopolis), kind 2 only from VAR_SOOTOPOLIS_CITY_STATE 4
# (Route129/130/131 and SkyPillar_Outside OnTransition: call_if_ge ... 4), kind 3 Sootopolis (SootopolisCity_EventScript_
# SetWeather: the downpour at state 1 and while VAR_SKY_PILLAR_STATE is 1, else the abnormal weather).
WEATHER_HOOK = 0x02032FB8                 # GetEntralinkWeatherIfApplicable (patches/weather.py HOOK, filled before this)
TICK_CALL = (0x02180884, OV036, 'arm9_ov036.bin', 0x02199120, 'EM_WeatherTickShim')   # FieldG3D_Update -> FieldWeather_Update
LATE_CRISIS_MAPS = ('Route129', 'Route130', 'Route131', 'SkyPillar_Outside')
WEATHER_PERIOD = 300                      # field frames between swaps: Emerald's 600 frames at 60 fps = 10 s; Black 2's
                                          # field updates at 30 fps (notes/STORY_PORTING.md section 7)

def _weather_mod():
    spec = importlib.util.spec_from_file_location('weather_', os.path.join(HERE, 'weather.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def _hoenn_h(name):
    m = re.search(rf'^#define {name}\s+(\w+)', open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read(), re.M)
    return int(m.group(1), 0)

def crisis_table():
    """[(zone, kind)] of the Emerald crisis weather, from the world's zones (HOENN_WORLD_DIR)."""
    import json
    wd = os.environ.get('HOENN_WORLD_DIR') or version.world_dir()
    zones = json.load(open(os.path.join(wd, 'world.json')))['zones']
    def of(maps): return sorted({int(z) for z, v in zones.items() if any(m in maps for m in v.get('maps', []))})
    wm = _weather_mod()
    out = [(z, 1) for z in of([m for m in wm.CRISIS_MAPS if m != 'SootopolisCity'])]
    out += [(z, 2) for z in of(LATE_CRISIS_MAPS)] + [(z, 3) for z in of(['SootopolisCity'])]
    assert len({z for z, _ in out}) == len(out), out
    return out

def weather_lines():
    try:
        table, cycles = crisis_table(), _weather_mod().cycle_zones()
    except (OSError, KeyError):                          # (python3 emerald_mech.py without a world: sizes only)
        table, cycles = [], []
    period = int(os.environ.get('HOENN_TEST_EMW_PERIOD') or WEATHER_PERIOD)
    cyc = [b for z, ws in cycles for b in (z & 0xFF, z >> 8, *ws)] + [0, 0]
    return [f'#define EMW_FLAG {_hoenn_h("FLAG_SYS_WEATHER_CTRL")}', f'#define EMW_STATE {_hoenn_h("VAR_SOOTOPOLIS_STATE")}',
            f'#define EMW_SKY {_hoenn_h("VAR_SKY_PILLAR_STATE")}',
            f'#define EMW_RAIN_ID {version.table("weather", "sapphire")}      /* Sapphire NDS\'s Kyogre rainstorm */',
            f'#define EMW_DROUGHT_ID {version.table("weather", "ruby")}   /* Ruby NDS\'s Groudon drought */',
            f'#define EMW_PERIOD {period}',
            'static const u16 kEmCrisis[] = {' + ', '.join(f'{z}, {k}' for z, k in table) + (', ' if table else '') + '0, 0};',
            'static const u8 kEmCycles[] = {' + ', '.join(map(str, cyc)) + '};']

def build(base, workdir):
    header, learners, inherited = data_header()
    open(os.path.join(workdir, 'emerald_mech_data.h'), 'w').write(header)
    obj = os.path.join(workdir, 'emerald_mech.o')
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror',
                    '-I', workdir, '-c', os.path.join(HERE, 'emerald_mech.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'emerald_mech.c needs {und}: call Black 2 functions by address only'
    blob, sym = _roamers().link(obj, base)
    return blob, sym, learners, inherited

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
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'run emerald_mech after the other ITCM patches (the arena literal)'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym, learners, inherited = build(base, tmp)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    # Steven's class -> back sprite 5 (the tag battle partner)
    cls = steven_class()
    o = BACK_SPRITES - ARM9
    pairs = [struct.unpack_from('<HH', arm9, o + 4 * i) for i in range(32)]
    assert (OLD_CLASS, STEVEN_BACK) in pairs and not any(c == cls for c, _ in pairs), (cls, pairs)
    i = pairs.index((OLD_CLASS, STEVEN_BACK))
    struct.pack_into('<HH', arm9, o + 4 * i, cls, STEVEN_BACK)
    _save(path9, arm9)
    path, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(path, itcm + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    bl = _roamers()._bl
    # the crisis weather (emerald_ch10): GetEntralinkWeatherIfApplicable (weather.py's hook) -> EM_ZoneWeather (ldr r3, =sym;
    # bx r3: lr still returns to GetWeatherAll), FieldG3D_Update's FieldWeather_Update call -> EM_WeatherTickShim
    o = WEATHER_HOOK - ARM9
    assert arm9[o:o + 2] == bytes.fromhex('70b5'), f'GetEntralinkWeatherIfApplicable: not weather.py\'s hook ({arm9[o:o + 4].hex()})'
    arm9[o:o + 8] = bytes.fromhex('004b1847') + struct.pack('<I', sym['EM_ZoneWeather'] | 1)
    _save(path9, arm9)
    for at, mbase, name, old, new in CALLS + [TICK_CALL]:
        p, d = _load(code, name)
        assert bytes(d[at - mbase:at - mbase + 4]) == bl(at, old), f'{name} {at:#x}: not Black 2\'s call'
        d[at - mbase:at - mbase + 4] = bl(at, sym[new] & ~1)
        _save(p, d)
    p, d = _load(code, 'arm9_ov012.bin')
    for cmd, (old, new) in COMMANDS.items():
        e = EVCMD_TABLE - OV012 + 4 * cmd
        assert struct.unpack_from('<I', d, e)[0] == old, f'EVCMD_TABLE[{cmd}] is not Black 2\'s'
        struct.pack_into('<I', d, e, sym[new] | 1)
    _save(p, d)
    return (f'emerald_mech: {len(blob)} B of ITCM at {base:#x} (arena from {end:#x}); commands 533 EmPartySwap, '
            f'281 EmTutorCheck, 686 EmPickParty; partner battles: only the picked Pokémon (ov036, ov166 calls); class {cls} (Steven) -> back sprite {STEVEN_BACK} (was class {OLD_CLASS}); tutor learners '
            + ', '.join(f'{t.lower()} {n}' for t, n in learners.items()) + f' ({inherited} Gen 4/5 species by family)')

if __name__ == '__main__':          # python3 emerald_mech.py: the tutor table and the code size at a dummy base
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym, learners, inherited = build(0x01FFC000, tmp)
        print(len(blob), {k: hex(v) for k, v in sym.items() if k.startswith('EM_')}, learners, inherited)
