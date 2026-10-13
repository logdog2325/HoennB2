"""Roaming legendaries (postgame_scripts, 2026-10-07; user request: roaming beasts and birds, and Sapphire's Latias after
the TV news). Code: b2tools/patches/roamers.c (compiled here with clang, linked into ITCM after hoenn_world's ZoneLookup).
Scripts: src/field_scripts/scenes/postgame_lib.inc (pg_roamer_start k, loc / pg_roamer_get var, k).

What Black 2 keeps of Black/White 1's roamers (Tornadus/Thundurus) [code: decomp symbols + disassembly, b2tools/armdis.py]:
  - Save: the encounter block (SaveControl block 55, 52 bytes; arm9 EncountSave_* 0x0200dcec-0x0200ddf8) still has BW1's two
    20-byte roamer records (+0, +20), two "zone clock" bytes (+40/+41, EncountSave_GetRoamingPkmZoneClock) and two state
    bytes (+42/+43, func_0200dd38), then the swarm (+44), Repel (+45..+47) and N's Pokemon bits (+48). Record fields
    (EncountSave_GetRoamingPkmParam 0x0200dd5c): +0 u16 zone, +2 u8 nature, +4 IVs, +8 PID, +12 species, +14 HP, +16 level,
    +17 status, +18 active.
  - Encounter: EventWildBattleCall_CreateRandom (ov036 0x021a1750) asks FieldEncount_RndCheckRoaming (0x021a0c68) on every
    random wild encounter (not fishing): of the TWO slots, those active, in the player's zone and not kept away by a Repel;
    then a coin flip (GFL_RandomLCAlt(1000) < 500: no roamer). FieldEncount_SetupRoaming (0x021a1cac) makes the Pokemon
    from the record (FieldEncount_GenRoamingPkm 0x021a0ecc) and sets battle flag 8, which gives the wild side AI flag 11
    (ov167 func_ov167_0219d8d4 -> 0x800; data/tr_ai/11_roaming_pokemon.s: it flees unless trapped, Sapphire's AI_Roaming).
  - Gone in Black 2: everything that writes a record. No code calls the getters except the encounter check, the Route
    gate's news board (ov104 func_ov104_021efb30, gated off: func_ov012_02159218 returns 0) and two script commands no
    Black 2 script uses (434 = func_ov036_021ae4f4, which calls the emptied start hook func_ov012_0215921c; 435 =
    func_ov012_02165950, reads +42/+43). The move hook on zone changes (func_ov012_021591f4, called by Field_SwapZoneByMatrix
    through func_ov012_0215ee10) and the game-clear hook (func_ov012_02159220) are empty functions; ROAMING_POKEMON_ZONES
    (ov012 0x0216ca52, 17 Unova zones) is read only through the gated gate code; the wild-battle callback
    (ov012 EventWildBattleCall_Callback 0x021684bc) records only N's Pokemon, nothing of a roamer's HP or capture.
  - Pokedex: no code reads the roamer data (all modules searched for calls of the getters), so the Pokedex area page shows
    only its own habitat data, never a roamer's current route.
So Black 2 holds two roamers and cannot start, move or update one. This patch keeps Black 2's encounter and battle path
(record -> GenRoamingPkm -> flag 8, roaming AI) and adds what is missing, for seven roamers (roamers.c has the layout):
  1. ov036 0x021a180a: bl FieldEncount_RndCheckRoaming -> bl PG_RndCheck (seven roamers, Sapphire's 1 in 4)
  2. ov036 0x021a1830: bl FieldEncount_SetupRoaming -> bl PG_SetupRoaming (builds the record, then the original)
  3. ov012 0x02168cee: bl EventBattleCall_SyncGameDataOnReturn -> bl PG_BattleReturn (after a roaming battle, marked by
     PG_SetupRoaming in the block's +42: HP/status kept, the roamer moved, caught: gone, knocked out: gone until the next
     Hall of Fame; then the original call), in EventBattleCall_Callback while the BtlSetup still exists
     (EventBattleCall_ReleaseBtlSetup frees it before EventWildBattleCall_Callback's after-battle step, which therefore
     cannot read it: tested, the battle flag read 0 there)
  4. ov036 0x02180c76 in Field_SwapZoneByMatrix (walking into another zone): bl func_ov012_0215ee10 -> bl PG_OnZoneSwapShim
     (passes the new zone, the caller's r4 = ZoneLookup's answer; that call, then Sapphire RoamerMove on a map connection;
     a step into another zone of the same place does nothing). Tested: Route 110 -> Mauville -> Route 110 moved every
     roamer to a neighbour each time, never back to where the player was two maps ago.
  5. ov035 0x0217e574 in FieldMapControl_InitSpawn (every map load: EventMapChangeCore's warps of all kinds, fly, blackout,
     Continue, the first field): bl func_ov012_0215ee40 -> bl PG_OnSpawn (that call, then Sapphire
     RoamerMoveToOtherLocationSet). (func_ov012_021591b4, which EventMapChangeCore calls, runs only for map-change types
     1-3, not for doors: tested, the roamers did not move through doors.)
  6. ov012 0x0215a4c4 in EventGameClear_Create (the Hall of Fame's CallGameClear, before the save): bl func_ov012_02159220
     (BW1's game-clear roamer hook, empty) -> bl PG_OnGameClear: every roamer knocked out (not caught) roams again (the
     Gen 4+ rule; user decision 2026-10-07: Sapphire's knocked-out roamer stays gone)
  7. ov012 EVCMD_TABLE (0x0216b538) entries 434 / 435 -> PG_CmdStartRoamer / PG_CmdGetRoamer (both allowed in normal
     scripts: EVCMD_PERM_TABLE 1 / 7)
Roamers (index, species, level = Sapphire's / FRLG's on data/level_scaling.json's curve, as every static legendary here):
see ROAMERS. Locations: Sapphire's sRoamerLocations (pokeruby src/roamer.c, read at build time), the map numbers turned into
place-name ids through data/hoenn_zones.json.
Code space: ITCM after hoenn_world's ZoneLookup (the same arena move; hoenn_world.py has the findings), so this patch runs
after hoenn_world. Main-RAM code: savestates made before need a cold boot (make_states.py on the new ROM).
Emerald (emerald_ch11_gameclear 2026-10-12): roamer 0 is Latias or Latios by the answer to Mom after the Hall of Fame; `pg_roamer_start 0x100` makes
it Latios (bit 8 of the number, kept in bit 0 of the seed; roamers.c PG_LATI_BY_SEED, compiled in an Emerald build only).
Test: HOENN_TEST_ROAMER_ALWAYS=1 drops the 1-in-4 (every encounter on a roamer's route is the roamer);
HOENN_TEST_ROAMER_DEBUG=1 writes markers into the block's +42/+43 (the battle result, the place a zone swap saw);
HOENN_TEST_ROAMER_NOFLEE=1 clears battle flag 8 after the setup (no roaming AI: a roamer can be knocked out);
HOENN_TEST_ROAMER_PLACE0=<place id> makes location 0 (Route 110) that place (e.g. 14 = Route 101, next to Littleroot)."""
import os, re, sys, json, struct, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import version  # noqa: E402  (Sapphire's roamer is Latias, Ruby's Latios: pokeruby ROAMER_SPECIES)
LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV012, OV035, OV036 = 0x021503C0, 0x0217C940, 0x0217F600
EVCMD_TABLE = 0x0216B538

ROAMERS = [(version.TABLE['roamer'], 40), ('RAIKOU', 50), ('ENTEI', 50), ('SUICUNE', 50), ('ARTICUNO', 50), ('ZAPDOS', 50), ('MOLTRES', 50)]
# Sapphire: Latias Lv 40, Ruby: Latios Lv 40 (pokeruby roamer.c CreateInitialRoamerMon, ROAMER_SPECIES); FRLG: the beasts Lv 50 (pokefirered roamer.c), the
# birds Lv 50 (their static encounters: pokefirered data/maps/*/scripts.inc setwildbattle)

# (call site, module base, file, old target, new symbol)
CALLS = [(0x021A180A, OV036, 'arm9_ov036.bin', 0x021A0C68, 'PG_RndCheck'),
         (0x021A1830, OV036, 'arm9_ov036.bin', 0x021A1CAC, 'PG_SetupRoaming'),
         (0x02168CEE, OV012, 'arm9_ov012.bin', 0x021690E8, 'PG_BattleReturn'),
         (0x02180C76, OV036, 'arm9_ov036.bin', 0x0215EE10, 'PG_OnZoneSwapShim'),
         (0x0217E574, OV035, 'arm9_ov035.bin', 0x0215EE40, 'PG_OnSpawn'),
         (0x0215A4C4, OV012, 'arm9_ov012.bin', 0x02159220, 'PG_OnGameClear')]
COMMANDS = {434: (0x021AE4F5, 'PG_CmdStartRoamer'), 435: (0x02165951, 'PG_CmdGetRoamer')}

def _bl(src, dst):
    off = dst - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, hex(off)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)

def _species():
    out = {}
    for line in open(os.path.join(ROOT, 'external', 'pokebw2', 'include', 'constants', 'species.h')):
        m = re.match(r'#define SPECIES_(\w+)\s+(\d+)\s*$', line)
        if m: out[m.group(1)] = int(m.group(2))
    return out

def scaled(level):
    return json.load(open(os.path.join(ROOT, 'data', 'level_scaling.json')))['curve']['table'][str(level)]

def locations():
    """Sapphire's sRoamerLocations as (place ids, neighbour rows of location indexes)."""
    src = open(os.path.join(ROOT, 'external', 'pokeruby', 'src', 'roamer.c')).read()
    body = src.split('sRoamerLocations[][6] =', 1)[1].split('};', 1)[0]
    rows = [[int(v, 16) for v in r.split(',')] for r in re.findall(r'\{\s*([0-9A-Fa-fx,\s]+?)\s*\}', body)]
    rows = [r for r in rows if r[0] != 0xFF]
    groups = json.load(open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', 'map_groups.json')))
    names = groups[groups['group_order'][0]]           # map group 0: towns and routes (Sapphire's roamer maps)
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    index = {r[0]: i for i, r in enumerate(rows)}
    places = [zones[names[r[0]]]['place'] for r in rows]
    adj = [[index[v] if v != 0xFF else 0xFF for v in r[1:]] for r in rows]
    assert len(rows) == 20 and all(p < 0x70 for p in places), places
    return [names[r[0]] for r in rows], places, adj

def data_header():
    sp = _species()
    _, places, adj = locations()
    if os.environ.get('HOENN_TEST_ROAMER_PLACE0'): places = [int(os.environ['HOENN_TEST_ROAMER_PLACE0'])] + places[1:]
    lines = ['/* generated by b2tools/patches/roamers.py */',
             'static const u16 kSpecies[N_ROAMERS] = {' + ', '.join(str(sp[s]) for s, _ in ROAMERS) + '};',
             'static const u8 kLevel[N_ROAMERS] = {' + ', '.join(str(scaled(l)) for _, l in ROAMERS) + '};',
             'static const u8 kPlace[N_LOCS] = {' + ', '.join(map(str, places)) + '};',
             'static const u8 kAdj[N_LOCS][5] = {' + ', '.join('{' + ', '.join(map(str, r)) + '}' for r in adj) + '};']
    if version.is_emerald():     # roamer 0 is Latias, or Latios when the script asked for it (roamers.c PG_LATI_BY_SEED)
        lines.append(f'static const u16 kLatiAlt = {sp["LATIOS"]};')
    return '\n'.join(lines) + '\n'

def history_work():
    src = open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()
    return int(re.search(r'#define\s+VAR_ROAMER_PLACE_HISTORY\s+(0x[0-9A-Fa-f]+)', src).group(1), 16)

# ---- a minimal ELF32 (ARM, REL) linker: .text/.rodata at `base`, ABS32 / THM_CALL / THM_JUMP11 relocations --------------
def _elf(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF' and d[4] == 1 and d[5] == 1
    shoff, = struct.unpack_from('<I', d, 0x20)
    shentsize, shnum, shstrndx = struct.unpack_from('<HHH', d, 0x2E)
    secs = []
    for i in range(shnum):
        name, typ, flags, addr, off, size, link, info, align, entsize = struct.unpack_from('<10I', d, shoff + i * shentsize)
        secs.append(dict(name=name, type=typ, flags=flags, off=off, size=size, link=link, info=info, align=align, entsize=entsize))
    strtab = secs[shstrndx]
    for s in secs:
        e = d.index(b'\0', strtab['off'] + s['name']); s['name'] = d[strtab['off'] + s['name']:e].decode()
    return d, secs

def link(obj, base):
    d, secs = _elf(obj)
    place, blob = {}, bytearray()
    for i, s in enumerate(secs):
        if s['flags'] & 2 and s['size'] and not s['name'].startswith('.ARM.'):   # SHF_ALLOC (not the unwind index)
            assert s['type'] == 1, f"section {s['name']}: only PROGBITS (no .bss/.data)"
            assert not s['flags'] & 1, f"section {s['name']} is writable: the code keeps no RAM of its own"
            while len(blob) % max(s['align'], 1): blob += b'\0'
            place[i] = base + len(blob)
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
        if s['type'] != 9 or s['info'] not in place: continue     # SHT_REL for an allocated section
        tbase = place[s['info']]
        for i in range(s['size'] // 8):
            off, info = struct.unpack_from('<II', d, s['off'] + 8 * i)
            sym, typ = info >> 8, info & 0xFF
            name, val, shndx = syms[sym]
            assert shndx in place, f'undefined symbol {name!r}: everything outside the blob is called by address'
            S = place[shndx] + val
            at = tbase - base + off
            P = tbase + off
            if typ == 2:                                          # R_ARM_ABS32
                A, = struct.unpack_from('<I', blob, at)
                struct.pack_into('<I', blob, at, (S + A) & 0xFFFFFFFF)
            elif typ == 10:                                       # R_ARM_THM_CALL (bl): X = S + A - P, A in place (-4)
                h1, h2 = struct.unpack_from('<HH', blob, at)
                assert h2 & 0xF800 == 0xF800, 'blx to a Thumb symbol'
                A = (h1 & 0x7FF) << 12 | (h2 & 0x7FF) << 1
                if A & (1 << 22): A -= 1 << 23
                X = (S & ~1) + A - P
                assert -(1 << 22) <= X < (1 << 22)
                struct.pack_into('<HH', blob, at, 0xF000 | (X >> 12) & 0x7FF, 0xF800 | (X >> 1) & 0x7FF)
            elif typ == 102:                                      # R_ARM_THM_JUMP11 (b)
                h, = struct.unpack_from('<H', blob, at)
                A = (h & 0x7FF) << 1
                if A & 0x800: A -= 0x1000
                o = (S & ~1) + A - P
                assert -2048 <= o < 2048 and not o & 1
                struct.pack_into('<H', blob, at, 0xE000 | (o >> 1) & 0x7FF)
            else:
                raise SystemExit(f'roamers: relocation type {typ} not handled')
    return bytes(blob), names

def build(base, workdir):
    with open(os.path.join(workdir, 'roamers_data.h'), 'w') as f: f.write(data_header())
    obj = os.path.join(workdir, 'roamers.o')
    defs = [f'-DPG_VAR_HISTORY={history_work()}']
    if os.environ.get('HOENN_TEST_ROAMER_ALWAYS'): defs.append('-DPG_TEST_ALWAYS')
    if os.environ.get('HOENN_TEST_ROAMER_DEBUG'): defs.append('-DPG_DEBUG')
    if os.environ.get('HOENN_TEST_ROAMER_NOFLEE'): defs.append('-DPG_TEST_NO_FLEE')
    if version.is_emerald(): defs.append('-DPG_LATI_BY_SEED')       # Emerald: the Lati that roams follows the colour told to Mom
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror', *defs,
                    '-I', workdir, '-c', os.path.join(HERE, 'roamers.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'roamers.c needs {und}: call Black 2 functions by address only'
    return link(obj, base)

def apply_code(code):
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    def load(name):
        p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())
    def save(p, d):
        if os.path.islink(p): os.unlink(p)
        open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)
    path9, arm9 = load('arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'run roamers after hoenn_world (the ITCM arena literal)'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym = build(base, tmp)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000
    struct.pack_into('<I', arm9, lit, end); save(path9, arm9)
    path, itcm = load('itcm.bin')
    assert len(itcm) == size
    save(path, itcm + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    mods = {}
    for at, mbase, name, old, new in CALLS:
        p, d = mods.get(name) or load(name)
        cur = bytes(d[at - mbase:at - mbase + 4])
        assert cur == _bl(at, old), f'{name} {at:#x}: unexpected bytes {cur.hex()}'
        d[at - mbase:at - mbase + 4] = _bl(at, sym[new] & ~1)
        mods[name] = (p, d)
    p, d = mods['arm9_ov012.bin']
    for cmd, (old, new) in COMMANDS.items():
        e = EVCMD_TABLE - OV012 + 4 * cmd
        assert struct.unpack_from('<I', d, e)[0] == old, f'EVCMD_TABLE[{cmd}]'
        struct.pack_into('<I', d, e, sym[new] | 1)
    for p, d in mods.values(): save(p, d)
    names, places, _ = locations()
    return (f'roamers: {len(blob)} B at {base:#x} (ITCM arena from {end:#x}); '
            + ', '.join(f'{s.title()} Lv {scaled(l)}' for s, l in ROAMERS) + f'; routes {names[0]}..{names[-1]} = places {places}')

if __name__ == '__main__':                       # python3 roamers.py: compile and link at a dummy base, show the code
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym = build(0x01FF9400, tmp)
        print(len(blob), {k: hex(v) for k, v in sym.items() if k.startswith('PG_')})
        out = sys.argv[1] if len(sys.argv) > 1 else None
        if out: open(out, 'wb').write(blob)
