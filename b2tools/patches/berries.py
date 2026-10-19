"""Berry planting (user goal 2026-10-18; notes/BERRY_PLANTING.md): Gen 3's berry trees (pokeemerald / pokeruby
src/berry.c, data/scripts/berry_tree.inc) in all three versions. Behind the switch HOENN_BERRY_PLANTING=1 (build_rom.py
appends this patch; scripts.py, text.py and story.py switch their parts): without it every build is byte-identical to
before (the daily berry spots of notes/DECISIONS.md 2026-10-06 / 10-08).

apply (files):
  1. a/0/4/7 (object records, read per record from the file: GetNPCMdlInfoForOBJCODE, no whole-table load): one record
     per tree picture (src/sprites/berry_planting/pictures.json, b2tools/berry_planting_art.py) appended after Black 2's
     1008, a copy of Black 2's one-frame billboard record 208 (controller 4, 32x32) with uid = its code, res1 = its sheet,
     shadow on for the tree stages (as the daily trees' people records), off for the blank, the dirt pile and the sprout.
     The count at +0 grows with them. Codes PIC_CODE_BASE + i (0x0E00..; Black 2 maps 377..0x0FFF to record 10).
  2. a/0/4/8: one sheet per picture appended (Black 2's sheet of record 208 as the template: one 32x32 4bpp texture
     t4x4x1.0 + its palette, 708 bytes; build_rom.py keeps a/0/4/8 in its 2 MB reserve). In a field each picture is one
     material (544 B of texture VRAM) while an actor shows it.
apply_code (code): berries.c (+ berries_data.h written here) in ITCM after the code already there (the arena literal
protocol of roamers.py / rods.py), and the hooks, each checked against Black 2's bytes:
  - ov012 EVCMD_TABLE[612] (HollowRivalCmd_0264 func_ov012_0216a748: no Black 2 or Hoenn script uses it; permission byte
    7 as the roamers' 435) -> Berry_Cmd (`BerryCmd op, arg`, src/field_scripts/common/berry_planting_defs.inc).
  - ov012 GetWKOBJCODENPCOBJCODE 0x02167fc8 (LoadActorParamsByZoneNPC's and ActorNew's code resolution; codes 162-177
    read works 0x4020-0x402F) -> `ldr r2, =Berry_ResolveCode; bx r2`: the same for 162-177, and VCODE_BASE + tree id
    (the tree actors of data/story/berries/berry_trees.json) -> the tree's picture code now.
  - arm9 GetIndexOfObjID 0x0200fe34 (code -> a/0/4/7 record) -> `ldr r1, =Berry_ObjIndex; bx r1`: Black 2's ranges
    unchanged, PIC_CODE_BASE + i -> REC_BASE + i.
berries_data.h: per version, from its own decomp (Sapphire/Ruby pokeruby, Emerald pokeemerald): kBerry[43] =
{stageDuration, maxYield, minYield} (gBerries), kPic[43][5] (the picture of each stage), kInit[128] (the berry Gen 3's
new game plants in each tree: data/hoenn_berry_trees.json, Emerald data/emerald/), kTreeX/kTreeZ[128] (each tree's world
tile: the script finds the tree by the talked-to actor's tile), the bases.
"""
import os, re, sys, json, struct, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import narcio, sprites, version  # noqa: E402

LLVM = '/opt/homebrew/opt/llvm/bin'
VANILLA = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
ART = os.path.join(ROOT, 'src', 'sprites', 'berry_planting')
ITCM_BASE, ARENA_ITCM_LIT, ARM9, OV012 = 0x01FF8000, 0x0207B400, 0x02004000, 0x021503C0
EVCMD_TABLE, EVCMD_PERM_TABLE, COMMAND, CMD_OLD = 0x0216B538, 0x0216B1F0, 612, 0x0216A749   # HollowRivalCmd_0264 (Thumb)
GET_INDEX = 0x0200FE34                     # arm9 GetIndexOfObjID
GET_INDEX_OLD = bytes.fromhex('0e498842')  # ldr r1, =377; cmp r0, r1
RESOLVE = 0x02167FC8                       # ov012 GetWKOBJCODENPCOBJCODE
RESOLVE_OLD = bytes.fromhex('08b5a229')    # push {r3, lr}; cmp r1, #162
VCODE_BASE = 0x0F00                        # a tree actor's code: 0x0F00 + tree id (converter/gen_hidden_items.py PLANT_VCODE)
PIC_CODE_BASE = 0x0E00                     # the pictures' codes
TEMPLATE_CODE = 208                        # Black 2's gift box: one-frame 32x32 billboard (controller 4, no shadow)
N_TREES = 128
STATE = {}                                 # apply -> apply_code: rec_base, n_pics


def enabled():
    return os.environ.get('HOENN_BERRY_PLANTING', '1') != '0'


def pictures():
    return json.load(open(os.path.join(ART, 'pictures.json')))


def apply(files):
    pj = pictures()
    pics = pj['pictures']
    table_v = narcio.load(VANILLA, sprites.ARC_OW_TABLE)[0]
    rec = bytearray(table_v[4 + 28 * TEMPLATE_CODE:4 + 28 * TEMPLATE_CODE + 28])
    assert struct.unpack_from('<HBBBBBBBBBBB', rec, 0)[1] == 1 and rec[9] == 4, 'record 208 is not a one-frame billboard'
    tsheet = narcio.load(VANILLA, sprites.ARC_OW_SHEETS)[struct.unpack_from('<H', rec, 0x10)[0]]
    assert [f[0] for f in sprites.btx_layout(tsheet)[0]] == ['t4x4x1.0'], 'template sheet is not one 32x32 frame'
    tables = narcio.load(files, sprites.ARC_OW_TABLE)
    t = bytearray(tables[0])
    n = struct.unpack_from('<I', t, 0)[0]
    assert len(t) == 4 + 28 * n, f'a/0/4/7: {len(t)} bytes for {n} records'
    sheets = narcio.load(files, sprites.ARC_OW_SHEETS)
    sheet0 = len(sheets)
    for i, p in enumerate(pics):
        meta, frames, pal = sprites.ow_load_folder(os.path.join(ART, p['folder']))
        assert meta['frames'] == 1 and meta['size'] == [32, 32], p['folder']
        sheets.append(sprites.btx_encode(tsheet, frames, pal))
        r = bytearray(rec)
        struct.pack_into('<H', r, 0, PIC_CODE_BASE + i)          # uid = the code (as Black 2's people records)
        r[4] = p['shadow']                                       # shadow: the trees yes, blank / dirt / sprout no
        struct.pack_into('<H', r, 0x10, sheet0 + i)              # res1 = its sheet
        t += r
    struct.pack_into('<I', t, 0, n + len(pics))
    tables[0] = bytes(t)
    narcio.save(files, sprites.ARC_OW_TABLE, tables)
    narcio.save(files, sprites.ARC_OW_SHEETS, sheets)
    STATE.update(rec_base=n, n_pics=len(pics))
    return (f'{len(pics)} berry tree pictures: codes {PIC_CODE_BASE:#x}-{PIC_CODE_BASE + len(pics) - 1:#x} = records '
            f'{n}-{n + len(pics) - 1} (a/0/4/7 count {n + len(pics)}), sheets {sheet0}-{sheet0 + len(pics) - 1} of a/0/4/8')


def berry_stats(decomp):
    """[(stageDuration, maxYield, minYield)] of Gen 3 berries 1-43 (the decomp's gBerries)."""
    s = open(os.path.join(ROOT, 'external', decomp, 'src', 'berry.c')).read()
    body = s[s.index('gBerries[]'):]
    body = body[:body.index('};\n')]
    out = []
    for e in re.split(r'\n    (?:\[[^\]]*\] = )?\{', body)[1:]:
        f = {k: int(re.search(r'\.' + k + r' = (\d+)', e).group(1)) for k in ('stageDuration', 'maxYield', 'minYield')}
        out.append((f['stageDuration'], f['maxYield'], f['minYield']))
    assert len(out) == 43 and all(0 < a <= 24 and c <= b <= 15 for a, b, c in out), out
    return out


def trees():
    """{tree id: Gen 3 berry number (0 = soft soil)} of this version (converter/gen_hidden_items.py planting_trees)."""
    path = version.overlay_file(os.path.join(ROOT, 'data', 'hoenn_berry_trees.json'))   # (whole file, not merged)
    return {int(k): v['number'] for k, v in json.load(open(path))['trees'].items()}


def tree_tiles():
    """{tree id: (x, z)}: each tree's world tile on the main matrix (the map's offset + its Gen 3 tile, as story.py places
    the tree's actor), which the code matches against the talked-to actor's tile."""
    import world as W
    cfg, lay = W.load()
    _, _, main = W.compose(cfg, lay)
    path = version.overlay_file(os.path.join(ROOT, 'data', 'hoenn_berry_trees.json'))
    out = {}
    for k, v in json.load(open(path))['trees'].items():
        m = main[v['map']]
        out[int(k)] = (m['ox'] + v['at'][0], m['oz'] + v['at'][1])
    assert len(set(out.values())) == len(out), 'two trees on one tile'
    return out


def data_header(rec_base, n_pics):
    decomp = 'pokeemerald' if version.is_emerald() else 'pokeruby'
    stats = berry_stats(decomp)
    pj = pictures()
    pic = [pj['berries'][nm] for nm in sorted(pj['berries'], key=lambda k: list(pj['berries']).index(k))]
    assert len(pic) == 43 and all(len(r) == 5 and max(r) < n_pics for r in pic)
    init = trees()
    assert max(init) < N_TREES and all(0 <= b <= 43 for b in init.values())
    kinit = [init.get(i, 0) for i in range(N_TREES)]
    tiles = tree_tiles()
    kx = [tiles[i][0] if i in tiles else 0xffff for i in range(N_TREES)]
    kz = [tiles[i][1] if i in tiles else 0xffff for i in range(N_TREES)]
    return '\n'.join([
        f'/* generated by b2tools/patches/berries.py ({version.VERSION}: {decomp}) */',
        f'#define VCODE_BASE {VCODE_BASE:#x}', f'#define PIC_CODE_BASE {PIC_CODE_BASE:#x}', f'#define N_PICS {n_pics}',
        f'#define REC_BASE {rec_base}', f'#define HOENN_VERSION_ID {version.GAME_VERSION}',
        'static const u8 kBerry[43][3] = {' + ', '.join('{%d, %d, %d}' % s for s in stats) + '};',
        'static const u8 kPic[43][5] = {' + ', '.join('{' + ', '.join(map(str, r)) + '}' for r in pic) + '};',
        'static const u8 kInit[128] = {' + ', '.join(map(str, kinit)) + '};',
        'static const u16 kTreeX[128] = {' + ', '.join(map(str, kx)) + '};',
        'static const u16 kTreeZ[128] = {' + ', '.join(map(str, kz)) + '};']) + '\n'


def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_link', os.path.join(HERE, 'roamers.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def build(base, workdir, rec_base=1008, n_pics=None):
    n_pics = n_pics or len(pictures()['pictures'])
    open(os.path.join(workdir, 'berries_data.h'), 'w').write(data_header(rec_base, n_pics))
    obj = os.path.join(workdir, 'berries.o')
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror',
                    '-I', workdir, '-c', os.path.join(HERE, 'berries.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'berries.c needs {und}: call Black 2 functions by address only'
    return _roamers().link(obj, base)


def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())


def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)


def _stub(reg, target):
    """ldr r<reg>, [pc, #0]; bx r<reg>; .word target | 1 (at a word-aligned address: the literal follows)."""
    return struct.pack('<HHI', 0x4800 | reg << 8, 0x4700 | reg << 3, target | 1)


def apply_code(code):
    assert STATE, 'berries: apply (the pictures) must run first'
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    p9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not at the end of ITCM (run berries last)'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym = build(base, tmp, STATE['rec_base'], STATE['n_pics'])
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    o = GET_INDEX - ARM9                                         # GetIndexOfObjID -> Berry_ObjIndex
    assert bytes(arm9[o:o + 4]) == GET_INDEX_OLD, f'arm9 {GET_INDEX:#x}: {arm9[o:o + 4].hex()}'
    arm9[o:o + 8] = _stub(1, sym['Berry_ObjIndex'] & ~1)
    _save(p9, arm9)
    pi, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(pi, bytes(itcm) + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    p12, ov12 = _load(code, 'arm9_ov012.bin')
    o = RESOLVE - OV012                                          # GetWKOBJCODENPCOBJCODE -> Berry_ResolveCode
    assert bytes(ov12[o:o + 4]) == RESOLVE_OLD, f'ov012 {RESOLVE:#x}: {ov12[o:o + 4].hex()}'
    ov12[o:o + 8] = _stub(2, sym['Berry_ResolveCode'] & ~1)
    e = EVCMD_TABLE - OV012 + 4 * COMMAND                        # script command 612 -> Berry_Cmd
    assert struct.unpack_from('<I', ov12, e)[0] == CMD_OLD, f'EVCMD_TABLE[{COMMAND}] is not Black 2\'s (another patch took it?)'
    struct.pack_into('<I', ov12, e, sym['Berry_Cmd'] | 1)
    perm = ov12[EVCMD_PERM_TABLE - OV012 + COMMAND]
    assert perm == 7, f'EVCMD_PERM_TABLE[{COMMAND}] = {perm}'
    _save(p12, ov12)
    return (f'berries: {len(blob)} B of ITCM at {base:#x} (arena from {end:#x}, {0x02000000 - end} B left); command '
            f'{COMMAND} BerryCmd, GetWKOBJCODENPCOBJCODE -> tree pictures (codes {VCODE_BASE:#x}+tree), GetIndexOfObjID '
            f'-> records {STATE["rec_base"]}+; save block 0x47; {sum(1 for b in trees().values() if b)} new-game trees '
            f'of {len(trees())} ({version.VERSION})')


if __name__ == '__main__':      # python3 berries.py: compile and link at a dummy base, show the size and the symbols
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym = build(0x01FFC400, tmp)
        print(len(blob), {k: hex(v) for k, v in sym.items() if k.startswith('Berry_')})
        print(open(os.path.join(tmp, 'berries_data.h')).read()[:600])
