#!/usr/bin/env python3
"""Offline checks of the Contests (notes/CONTESTS.md), no ROM and no emulator:
 1. the C's numbers against the data: archive members, OBJ cells, text bank, songs, the game-clear flag;
 2. the data's bounds, per version: moves, effects, opponents, AI script offsets;
 3. the rules, run on the host (contest_logic.c, contest_effect.c, contest_ai.c): many AI-only contests, each decomp's data;
 4. the blending and feeding rules on the host (pokeblock_logic.c) against Python's own copy of two worked examples;
 5. the save: berries.c's bound, a growth update on a block as old saves have it leaves +552 on alone;
 6. the Musical's person in Lilycove's lobby: its lines, its tile;
 7. the lobby scripts assemble for each version with no undefined name.
    python3 b2tools/contest_check.py [DECOMP_DIR]
"""
import json, os, re, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import contest_data as cd, contest_blend_data, gen_contest_text as gen  # noqa: E402

DECOMP = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('HOENN_DECOMP', os.path.join(ROOT, 'external', 'pokebw2_new'))
LLVM = '/opt/homebrew/opt/llvm/bin'
errors = []


def fail(msg):
    errors.append(msg)
    print('FAIL', msg)


def check_constants():
    h = open(os.path.join(DECOMP, 'include/hoennb2/contest.h')).read()
    enum = re.search(r'enum \{\s*CA_BG_CHARS.*?CA_COUNT', h, re.S).group(0)
    names = re.findall(r'CA_(\w+)', enum)
    if names[:-1] != cd.MEMBERS:
        fail(f'archive members differ: {set(names) ^ set(cd.MEMBERS)}')
    text = open(os.path.join(DECOMP, 'include/hoennb2/contest_text.h')).read()
    if text != cd.header_text():
        fail('include/hoennb2/contest_text.h is not what contest_data.py makes')
    ui = open(os.path.join(DECOMP, 'src/hoennb2/contest/contest_ui.h')).read()
    music = json.load(open(os.path.join(ROOT, 'data/hoenn_music.json')))
    for name, key in (('CONTEST_BGM_STAGE', 'mus_contest'), ('CONTEST_BGM_RESULTS', 'mus_contest_results'), ('CONTEST_BGM_WINNER', 'mus_contest_winner')):
        got = re.search(r'#define %s (\w+)' % name, ui).group(1)
        want = _find(music, key)
        if got != want:
            fail(f'{name} = {got}, hoenn_music.json {key} = {want}')
    hoenn = open(os.path.join(ROOT, 'src/include/hoenn.h')).read()
    if not re.search(r'#define FLAG_SYS_GAME_CLEAR\s+2400\b', hoenn):
        fail('FLAG_SYS_GAME_CLEAR is not 2400')
    obj = cd.contest_obj()
    cells = struct.unpack_from('<H', obj['OBJ_CELLS'], 0x18)[0]
    if cells != 1 + 7 + 1 + 5 + 6:
        fail(f'OBJ cells {cells}')
    print('constants: members, text bank, songs, flag, OBJ cells agree')


def _find(d, key):
    if isinstance(d, dict):
        if key in d:
            return d[key]
        for v in d.values():
            r = _find(v, key)
            if r:
                return r
    return None


def check_data(decomp, label):
    moves = cd.pack_moves(decomp)
    effs = cd.effects(decomp)
    for i in range(cd.N_MOVES):
        e, c, st = moves[i * 8:i * 8 + 3]
        if e >= len(effs) or c > 4:
            fail(f'{label}: move {i}: effect {e} category {c}')
    lookup = cd.combo_lookup(decomp)
    for i in range(cd.N_MOVES):
        if moves[i * 8 + 2] >= len(lookup):
            fail(f'{label}: move {i}: combo starter')
    opp = cd.pack_opponents(decomp)
    n = len(opp) // 28
    pools = {}
    for i in range(n):
        sp, rank, pool, filt, _ = struct.unpack_from('<HBBBB', opp, i * 28)
        ms = struct.unpack_from('<4H', opp, i * 28 + 6)
        if not 1 <= sp <= 649 or rank > 3 or any(m >= cd.N_MOVES for m in ms) or not any(ms):
            fail(f'{label}: opponent {i}: species {sp} rank {rank} moves {ms}')
        for c in range(5):
            if pool >> c & 1:
                if filt != 2:
                    pools.setdefault((rank, c), 0)
                    pools[(rank, c)] += 1
    for rank in range(4):
        for c in range(5):
            if pools.get((rank, c), 0) < 3:
                fail(f'{label}: rank {rank} category {c}: only {pools.get((rank, c), 0)} opponents before the Hall of Fame')
    ai = cd.assemble_ai(decomp)
    for i in range(32):
        off, = struct.unpack_from('<I', ai, 4 * i)
        if not 128 <= off < len(ai):
            fail(f'{label}: AI script {i} offset {off}')
    print(f'data {label}: {cd.N_MOVES} moves, {len(effs)} effects, {n} opponents, AI {len(ai)} B in bounds')


def host_build(work, sources, out, includes=()):
    flags = ['-O1', '-std=gnu99', '-w', '-I', os.path.join(HERE, 'contest_host'), '-I', os.path.join(DECOMP, 'src/hoennb2/contest')]
    for i in includes:
        flags += ['-I', i]
    subprocess.run(['clang', *flags, '-o', out, *sources], check=True)


def check_rules(work):
    c = os.path.join(DECOMP, 'src/hoennb2/contest')
    exe = os.path.join(work, 'contest_sim')
    host_build(work, [os.path.join(HERE, 'contest_host/sim.c'), os.path.join(c, 'contest_logic.c'), os.path.join(c, 'contest_effect.c'),
                      os.path.join(c, 'contest_ai.c')], exe)
    for decomp, label in ((cd.RUBY, 'Sapphire/Ruby'), (cd.EMERALD, 'Emerald')):
        paths = []
        for name, data in (('moves', cd.pack_moves(decomp)), ('effects', cd.pack_effects(decomp)), ('opp', cd.pack_opponents(decomp)),
                           ('ai', cd.assemble_ai(decomp))):
            p = os.path.join(work, f'{label[:3]}_{name}.bin')
            open(p, 'wb').write(data)
            paths.append(p)
        r = subprocess.run([exe, *paths, '3000'], capture_output=True, text=True, timeout=120)
        print(f'rules {label}:', r.stdout.strip(), r.stderr.strip()[:200])
        if r.returncode != 0 or not r.stdout.startswith('OK'):
            fail(f'rules {label}: {r.stdout} {r.returncode}')


def check_blend(work):
    p = os.path.join(DECOMP, 'src/hoennb2/pokeblock/pokeblock_logic.c')
    main = os.path.join(work, 'blend_main.c')
    open(main, 'w').write(r'''
#include <stdio.h>
#include "types.h"
#include "pokeblock_app.h"
u32 GFL_RandomLC(u32 m) { return 0; }
int main(void) {
    BlenderBerry b[4] = {{149,{10,0,0,0,0,25}},{150,{0,10,0,0,0,25}},{151,{0,0,10,0,0,25}},{152,{0,0,0,10,0,25}}};
    Pokeblock r; u8 fl[6];
    CalculatePokeblock(b, &r, 2, fl, 10000);
    printf("%d %d %d %d %d %d %d\n", r.color, r.spicy, r.dry, r.sweet, r.bitter, r.sour, r.feel);
    b[1] = b[0];
    CalculatePokeblock(b, &r, 2, fl, 10000);
    printf("%d\n", r.color);
    return 0;
}
''')
    stub = os.path.join(work, 'blend_inc')
    os.makedirs(os.path.join(stub, 'constants'), exist_ok=True)
    os.makedirs(os.path.join(stub, 'pml'), exist_ok=True)
    open(os.path.join(stub, 'constants/pokemon.h'), 'w').write('#define PKM_PARAM_NATURE 0x70\n#define PKM_PARAM_CONTEST_COOL 0x13\n#define PKM_PARAM_CONTEST_BEAUTY 0x14\n#define PKM_PARAM_CONTEST_CUTE 0x15\n#define PKM_PARAM_CONTEST_SMART 0x16\n#define PKM_PARAM_CONTEST_TOUGH 0x17\n#define PKM_PARAM_CONTEST_SHEEN 0x18\n')
    open(os.path.join(stub, 'pml/poke_party.h'), 'w').write('typedef struct PartyPkm PartyPkm;\nu32 PokeParty_GetParam(const PartyPkm *p, int f, void *b);\nvoid PokeParty_SetParam(PartyPkm *p, int f, u32 v);\n')
    open(os.path.join(stub, 'pokeblock_app.h'), 'w').write(r'''
#pragma once
#include "types.h"
#include "pml/poke_party.h"
typedef struct { u8 color, spicy, dry, sweet, bitter, sour, feel; } Pokeblock;
enum { PBLOCK_CLR_NONE, PBLOCK_CLR_RED, PBLOCK_CLR_BLUE, PBLOCK_CLR_PINK, PBLOCK_CLR_GREEN, PBLOCK_CLR_YELLOW, PBLOCK_CLR_PURPLE, PBLOCK_CLR_INDIGO, PBLOCK_CLR_BROWN, PBLOCK_CLR_LITEBLUE, PBLOCK_CLR_OLIVE, PBLOCK_CLR_GRAY, PBLOCK_CLR_BLACK, PBLOCK_CLR_WHITE, PBLOCK_CLR_GOLD };
typedef struct { u16 itemId; u8 flavors[6]; } BlenderBerry;
void CalculatePokeblock(BlenderBerry *berries, Pokeblock *pokeblock, u8 numPlayers, u8 *flavors, u16 maxRPM);
s16 PokeblockGetGain(u32 nature, const Pokeblock *block);
s32 GetFlavorRelationByNature(u32 nature, u32 flavor);
BOOL Pokeblock_Feed(PartyPkm *pkm, const Pokeblock *block, u16 *gains);
''')
    stubc = os.path.join(work, 'blend_stub.c')
    open(stubc, 'w').write('#include "types.h"\n#include "pml/poke_party.h"\nu32 PokeParty_GetParam(const PartyPkm *p, int f, void *b){return 0;}\nvoid PokeParty_SetParam(PartyPkm *p, int f, u32 v){}\n')
    exe = os.path.join(work, 'blend')
    # (a copy beside the stub header: the source's own folder would win over it)
    copy = os.path.join(stub, 'pokeblock_logic.c')
    open(copy, 'w').write(open(p).read())
    host_build(work, [main, copy, stubc], exe, includes=[stub])
    r = subprocess.run([exe], capture_output=True, text=True, timeout=20)
    out = r.stdout.split('\n')
    # Worked by hand: Cheri + Chesto: spicy 10-10=0 -> sour... spicy-dry 0, dry-sweet 10, sweet-bitter 0, bitter-sour 0, sour-spicy -10
    # (one negative): dry 10 - 1 = 9; RPM factor 10000/333+100 = 130: 9*130/10 = 117 -> 11, remainder 7 -> 12. One flavor, dry: Blue
    # (feel: (25+25)/2 - 2 = 23). The same Berry twice: Black.
    if out[0] != '2 0 12 0 0 0 23' or out[1] != '12':
        fail(f'blending: {out[:2]}')
    print('blending: two worked examples agree:', out[0])


def check_save(work):
    src = open(os.path.join(HERE, 'patches/berries.c')).read()
    if not re.search(r'#define N_TREES 90\b', src):
        fail('berries.c: N_TREES is not 90')
    for pat in (r'trees\[N_TREES\]', r'i < N_TREES', r'VCODE_BASE \+ N_TREES'):
        if not re.search(pat, src):
            fail(f'berries.c: {pat} not found')
    if re.search(r'\b128\b', re.sub(r'/\*.*?\*/', '', src, flags=re.S)):
        fail('berries.c still names 128')
    py = open(os.path.join(HERE, 'patches/berries.py')).read()
    if not re.search(r'^N_TREES = 90\b', py, re.M):
        fail('berries.py: N_TREES is not 90')
    def part(start, end):
        i = src.index(start)
        j = src.index(end, i)
        return src[i:j]
    body = ('#include "types.h"\ntypedef struct { u8 pad; } unused_t;\nu32 GFL_RandomLC(u32 m);\n'
            '#define GFL_RandomLCAlt(m) ((m) ? 0 : 0)\n#define BERRY_MAGIC 0x33595242u\n#ifndef N_TREES\n#define N_TREES 90\n#endif\n'
            'enum { STAGE_NO_BERRY, STAGE_PLANTED, STAGE_SPROUTED, STAGE_TALLER, STAGE_FLOWERING, STAGE_BERRIES };\n'
            'static const u8 kBerry[43][3] = {' + ','.join('{3,5,2}' for _ in range(43)) + '};\n' +
            part('typedef struct {\n    u8 berry;', '/* ---- Gen 3 rules') + part('static u32 stage_minutes', 'static void time_update_trees') +
            part('static void time_update_trees', '\n}\n') + '\n}\n')
    body = re.sub(r'^typedef char BerrySaveEndsAt552[^\n]*$', '', body, flags=re.M)   # (true of the game's; the old bound's check runs too)
    open(os.path.join(work, 'berries_extract.h'), 'w').write(body)
    if not re.search(r'typedef char BerrySaveEndsAt552\[sizeof\(BerrySave\) == 552', src):
        fail('berries.c: the size check is gone')
    exe = os.path.join(work, 'save_sim')
    host_build(work, [os.path.join(HERE, 'contest_host/save_sim.c')], exe, includes=[work])
    r = subprocess.run([exe], capture_output=True, text=True, timeout=30)
    print('save:', r.stdout.strip())
    if r.returncode != 0 or not r.stdout.startswith('OK'):
        fail(f'save: {r.stdout}')
    # an existing save's trees: the old 128-tree bound gives the same first 552 bytes from the same block
    old = os.path.join(work, 'save_sim_old')
    subprocess.run(['clang', '-O1', '-std=gnu99', '-w', '-DOLD_BOUND', '-DN_TREES=128', '-I', os.path.join(HERE, 'contest_host'), '-I', work, '-o', old,
                    os.path.join(HERE, 'contest_host/save_sim.c')], check=True)
    o = subprocess.run([old], capture_output=True, text=True, timeout=30).stdout.strip()
    if o != r.stdout.split()[1]:
        fail(f'save: trees differ with the old bound: {o} / {r.stdout.split()[1]}')
    else:
        print(f"save: an existing save's trees come out the same as with the old bound ({o})")
    # the magic and fit, on the C's source
    h = open(os.path.join(DECOMP, 'include/hoennb2/contest.h')).read()
    if 'POKEBLOCK_SAVE_OFFSET 552' not in h:
        fail('contest.h: POKEBLOCK_SAVE_OFFSET')
    size = 4 + 6 + 2 + 7 * 40
    if size > 996 - 552:
        fail(f'PokeblockSave {size} B past the block')
    print(f'save: PokeblockSave {size} B, +552 to +{552 + size} of 996 (a compile-time check in contest_cmd.c too)')


def check_musical():
    # the Musical's person: the macro's start is where its lines are, per version; the people's tile is free floor in Gen 3
    import gen_contest_text as g
    src = open(os.path.join(ROOT, 'src/field_scripts/0322_room_LilycoveCity_ContestLobby.s')).read()
    want = {'src/text/script/0219_room_LilycoveCity_ContestLobby.txt': 63, 'src/text/script/emerald/0219_room_LilycoveCity_ContestLobby.txt': 65}
    for rel, t in want.items():
        rows = open(os.path.join(ROOT, rel), encoding='utf-8').read().split('\n')
        if f'#define T_Musical {t}' not in src or rows[t:t + 14] != g.MUSICAL_LINES:
            fail(f'{rel}: the Musical\'s lines are not at {t}')
    host = [o for o in json.load(open(os.path.join(ROOT, 'data/story/ch8a.json')))['objects'] if o['map'] == 'LilycoveCity_ContestLobby' and o['uid'] == 30]
    if len(host) != 1:
        fail('the Musical\'s person is not in ch8a.json')
    for decomp, at in ((cd.RUBY, host[0]['at']), (cd.EMERALD, host[0]['at_emerald'])):
        j = json.load(open(os.path.join(decomp, 'data/layouts/layouts.json')))
        l = next(x for x in j['layouts'] if x['id'] == 'LAYOUT_LILYCOVE_CITY_CONTEST_LOBBY')
        raw = open(os.path.join(decomp, l['blockdata_filepath']), 'rb').read()
        block, = struct.unpack_from('<H', raw, 2 * (at[1] * l['width'] + at[0]))
        m = json.load(open(os.path.join(decomp, 'data/maps/LilycoveCity_ContestLobby/map.json')))
        if block >> 10 & 3 or (at[0], at[1]) in [(o['x'], o['y']) for o in m['object_events']]:
            fail(f'{decomp}: the Musical\'s person at {at}: not free floor')
    print('musical: its lines and its person\'s tile are right for each version')


def check_emulator_fixes(decomp):
    """What the first emulator run found: each came back wrong once."""
    for rel in gen.LOBBIES:
        lines = open(os.path.join(ROOT, rel), encoding='utf-8').read().split('\n')
        t = gen.LOBBIES[rel][0]
        if not lines[t + 23].endswith('{0100:1}.'):
            fail(f'{rel}: the Ribbon line has to name the Pokémon with word 1: {lines[t + 23]}')
    inc = open(os.path.join(ROOT, 'src/field_scripts/common/contests.inc'), encoding='utf-8').read()
    if not re.search(r'BGMPush \d+\n\s*con_run [^\n]*\n\s*BGMPop ', inc):
        fail('contests.inc: con_run has to sit between BGMPush and BGMPop, or the winner\'s music stays on the field')
    # GFL_BGSysLoadChar's offset is in tiles
    results = open(os.path.join(decomp, 'src/hoennb2/contest/contest_results.c')).read()
    app = open(os.path.join(decomp, 'src/hoennb2/contest/contest_app.c')).read()
    if '* 0x20);' in ''.join(l for l in results.split('\n') if 'GFL_BGSysLoadChar' in l) or '0x1000, 0x2000)' in app:
        fail('GFL_BGSysLoadChar takes its offset in tiles')
    # BmpWin_CreateStatic returns NULL when characters overlap: the stage's windows end at 0x336
    if not re.search(r'BmpWin_CreateStatic\(RES_BG_ROWS, [^;]*0x340 \+ i \* 24\)', results):
        fail('contest_results.c: the rows\' windows must stay clear of the stage\'s characters')
    for rel in ('src/field_scripts/common/contests.inc', 'src/field_scripts/common/musical.inc'):
        if 'ListMenu_AnchorTopRight 31, 1,' in open(os.path.join(ROOT, rel), encoding='utf-8').read():
            fail(f'{rel}: a list menu over the speech bubble')
    print('emulator fixes: Ribbon line, the field\'s music around a Contest, BG char offsets')


def check_scripts(work):
    files = ['0120_room_VerdanturfTown_ContestLobby', '0186_room_FallarborTown_ContestLobby', '1190_room_SlateportCity_ContestLobby',
             '0322_room_LilycoveCity_ContestLobby']
    for version, vid in (('HOENN_SAPPHIRE', 1), ('HOENN_RUBY', 2), ('HOENN_EMERALD', 3)):
        for f in (files if version != 'HOENN_EMERALD' else files[-1:]):
            o = os.path.join(work, f'{f}_{version}.o')
            r = subprocess.run([f'{LLVM}/clang', '--target=armv5te-none-eabi', '-x', 'assembler-with-cpp', '-c', '-D', version, '-D', f'HOENN_VERSION_ID={vid}',
                                '-D', 'HOENN_BERRY_PLANTING', '-D', 'HOENN_FOLLOWERS', '-I', 'include', '-I', 'lib/nitro/include', '-I', 'build/include/generated',
                                '-I', os.path.join(ROOT, 'src/include'), '-I', os.path.join(ROOT, 'src/field_scripts'), '-D', 'BLACK2', '-o', o,
                                os.path.join(ROOT, 'src/field_scripts', f + '.s')], cwd=DECOMP, capture_output=True, text=True)
            if r.returncode != 0:
                errs = [l for l in r.stderr.split('\n') if 'error' in l][:6]
                fail(f'{f} {version}: {errs}')
                continue
            undef = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', o], capture_output=True, text=True).stdout.split()
            undef = [w for w in undef if w != 'U']
            if undef:
                fail(f'{f} {version}: undefined {undef}')
            size = os.path.getsize(o)
            print(f'script {f} {version}: assembled ({size} B object)')


def main():
    work = tempfile.mkdtemp(prefix='contest_check_')
    check_constants()
    check_data(cd.RUBY, 'Sapphire/Ruby')
    check_data(cd.EMERALD, 'Emerald')
    check_rules(work)
    check_blend(work)
    check_save(work)
    check_musical()
    check_emulator_fixes(DECOMP)
    check_scripts(work)
    print('contest_check:', 'FAILED ' + str(len(errors)) if errors else 'all checks pass')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
