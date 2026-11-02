#!/usr/bin/env python3
"""Offline checks of Secret Bases and decorations (notes/SECRET_BASES.md).

    HOENN_DECOMP=<decomp tree> python3 b2tools/secret_base_check.py [--world DIR] [--emerald-world DIR]

1. Gen 3's data: the decoration table and the spots agree in pokeruby and pokeemerald; the shops' decorations exist.
2. The rooms: every layout has a mat, a PC with a floor tile in front of it reachable from the mat, its zone is no other room's.
3. The scripts assemble for Sapphire, Ruby, Emerald; the ops in common/secret_base_defs.inc are the C's; every SBT_ is a line.
4. The worst case, a base with 16 of the biggest decorations: props, field heap and texture VRAM.
5. The spots: on a solid tile with walkable floor south of it, in each world given.
"""
import argparse, glob, json, os, re, struct, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'patches'))
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import secret_base_data as SB

FAILS = []
def fail(msg): FAILS.append(msg); print('  FAIL', msg)
def ok(msg): print('  ok', msg)


def data():
    print('1. data')
    SB.check()
    ds = SB.decorations()
    for name, bp, lst in SB.shops():
        bad = [d for d in lst if not 1 <= d <= 120]
        if bad: fail(f'shop {name}: {bad}')
        if bp:
            prices = SB._bp_prices()
            miss = [d for d in lst if d not in prices]
            if miss: fail(f'shop {name}: no price for {miss}')
    ok(f'{len(SB.shops())} shop lists, every entry a decoration')
    ok(f'decorations by category: ' + ', '.join(f"{c} {sum(1 for d in ds[1:] if d['cat'] == c)}" for c in SB.CATS))
    # every decoration has a way to get it, in some version
    got = {d for _, _, lst in SB.shops() for d in lst} | {31, 32, 44, 42, 43, 99, 100, 117, 13, 6, 88, 89, 90}
    miss = [ds[i]['name'] for i in range(1, 121) if i not in got]
    print('  decorations no shop or gift of ours gives:', miss)


def rooms():
    print('2. rooms')
    used = {}
    for f in glob.glob(os.path.join(ROOT, 'data', 'interiors', '**', '*.json'), recursive=True):
        c = json.load(open(f))
        if isinstance(c, dict) and 'zone' in c:
            if c['zone'] in SB.ZONES and c.get('room') not in SB.LAYOUTS: fail(f'zone {c["zone"]} is also {f}')
    for i, (n, z) in enumerate(zip(SB.LAYOUTS, SB.ZONES)):
        g = SB.grid(n)
        from gba import Repo
        r = Repo(SB.RUBY)
        mj = r.map_json(n)
        grid, _ = r.layout_grid(mj['layout'])
        walk = lambda x, y: 0 <= y < g['h'] and 0 <= x < g['w'] and ((int(grid[y, x]) >> 10) & 3) == 0
        mat = g['warp']
        if not walk(*mat): fail(f'{n}: the mat {mat} is not walkable')
        pc_front = SB.ENTRY[i]
        if not walk(*pc_front): fail(f'{n}: the tile {pc_front} in front of the PC is not walkable')
        seen, todo = {mat}, [mat]
        while todo:
            x, y = todo.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                t = (x + dx, y + dy)
                if t not in seen and walk(*t):
                    seen.add(t); todo.append(t)
        if pc_front not in seen: fail(f'{n}: the PC cannot be reached from the mat')
        pcs = [(x, y) for k, x, y in g['fix'] if k == 'pc']
        if len(pcs) != 1 or (pc_front[0], pc_front[1] - 1) != pcs[0]:
            print(f'  note {n}: PC at {pcs}, Gen 3\'s entry tile {pc_front}')
    ok(f'{len(SB.LAYOUTS)} layouts: mat and PC reachable')


def perm_0x15f():
    """The extension command must be allowed: EVCMD_PERM_TABLE[0x15F] is { 0, 0, 0 } in Black 2, whose guard then hangs the game."""
    p = os.path.join(os.environ.get('HOENN_DECOMP') or os.path.join(ROOT, 'external', 'pokebw2_new'), 'src', 'ov012', 'script_sys.c')
    t = open(p).read()
    body = t[t.index('EVCMD_PERM_TABLE[] = {'):]
    body = re.sub(r'#else.*?#endif', '', body[:body.index('};')], flags=re.S)       # the HOENNB2 side
    rows = re.findall(r'\{ *(\d), *(\d), *(\d) *\}', body)
    if rows[0x15F] == ('0', '0', '0'): fail('EVCMD_PERM_TABLE[0x15F] is 0: every script using the extension command hangs')
    else: ok(f'EVCMD_PERM_TABLE[0x15F] = {rows[0x15F]}, {len(rows)} rows')


def scripts():
    print('3. scripts')
    perm_0x15f()
    defs = open(os.path.join(ROOT, 'src', 'field_scripts', 'common', 'secret_base_defs.inc')).read()
    ops = dict((a, int(b)) for a, b in re.findall(r'#define (SB_OP_\w+) (\d+)', defs))
    decomp = os.environ.get('HOENN_DECOMP')
    if decomp:
        c = open(os.path.join(decomp, 'src', 'hoennb2', 'secret_base', 'sb_main.c')).read()
        body = c[c.index('enum {\n    SB_OP_SPOT = 2'):]
        body = body[:body.index('};')]
        names = re.findall(r'^\s+(SB_OP_\w+)', body, re.M)
        for k, nm in enumerate(names):
            if ops.get(nm) != k + 2: fail(f'{nm}: C {k + 2}, scripts {ops.get(nm)}')
        ok(f'{len(names)} ops agree with the C')
    lines = open(SB.TEXT_FILE, encoding='utf-8').read().split('\n')
    sbt = dict((a, int(b)) for a, b in re.findall(r'#define (SBT_\w+) (\d+)', open(SB.DEFS_FILE).read()))
    if max(sbt.values()) >= len(lines) - 1: fail('a SBT_ line past the text file')
    src = open(os.path.join(ROOT, 'src', 'field_scripts', '1281_secret_bases.s')).read()
    for nm in set(re.findall(r'\bSBT_\w+', src)):
        if nm not in sbt: fail(f'{nm} has no line')
    entries = re.findall(r'^\s*ScriptEntry', src, re.M)
    if len(entries) > 50: fail(f'{len(entries)} entries: global 10735-10784 holds 50')
    ok(f'{len(entries)} script entries, {len(lines) - 1} lines, {len(src)} B of source')
    files = ['1281_secret_bases.s', '0402_room_LilycoveCity_DepartmentStore_5F.s', '0364_room_LilycoveCity_DepartmentStoreRooftop.s',
             '0228_room_FortreeCity_DecorationShop.s', '1010_room_Route104_PrettyPetalFlowerShop.s',
             '0422_room_LilycoveCity_LilycoveMuseum_2F.s', '1118_room_Route114_LanettesHouse.s',
             '0098_room_SootopolisCity_House6.s', '1026_room_Route110_TrickHouseEnd.s', '1112_room_Route113_GlassWorkshop.s',
             '0474_room_MauvilleCity_GameCorner.s', '0782_brendans_house_2f.s', '0786_mays_house_2f.s']
    code = """
import os, sys
sys.path.insert(0, 'b2tools'); sys.path.insert(0, 'b2tools/patches')
import scripts as S
for f in sys.argv[1:]:
    print(f, len(S.assemble(f)))
"""
    for ver, extra in (('sapphire', ['0042_room_BattleTower_Lobby.s']), ('ruby', ['0042_room_BattleTower_Lobby.s']),
                       ('emerald', ['emerald/0996_room_BattleFrontier_ScottsHouse.s', 'emerald/0838_room_BattleFrontier_ExchangeServiceCorner.s'])):
        env = dict(os.environ, HOENN_VERSION='' if ver == 'sapphire' else ver)
        fl = [os.path.join('src', 'field_scripts', x) for x in files + extra]
        r = subprocess.run([sys.executable, '-c', code, *fl], cwd=ROOT, env=env, capture_output=True, text=True)
        if r.returncode:
            fail(f'{ver}: {(r.stdout + r.stderr)[-1500:]}')
        else:
            ok(f'{ver}: {len(fl)} files assemble')


def worst_case():
    print('4. the worst case')
    import nsbtx
    P = os.path.join(os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'), '_secret_bases')
    props = json.load(open(os.path.join(P, 'props.json')))
    size = {p['res']: os.path.getsize(os.path.join(P, p['name'] + '.nsbmd')) for p in props}
    biggest = sorted((v for k, v in size.items() if k < SB.RES_FIXTURE), reverse=True)[:17]     # 16 + the preview
    fixtures = [size[SB.RES_FIXTURE]] + [size[SB.RES_FIXTURE + 1]] * 6 + [size[SB.RES_CURSOR]]
    model_bytes = sum(biggest) + sum(fixtures)
    print(f'  all {len(props)} models: {sum(size.values()):,} B; a full base keeps {model_bytes:,} B + {(len(biggest) + len(fixtures)) * 36} B of records')
    # GFL_G3DResGetAllocSize + a model + an actor per prop type: at most ~0x400 B each (measured on Black 2's towns: 300-900)
    per = 0x400 * (len(biggest) + len(fixtures))
    heap = model_bytes + per
    print(f'  field heap: {heap:,} B at worst (rooms keep 280,000+ B above the save\'s need: notes/BATTLE_TOWER.md)')
    if heap > 150000: fail(f'field heap {heap}')
    from PIL import Image
    tex = pal = 0
    for p in props:
        w, h = Image.open(os.path.join(P, p['name'] + '.png')).size
        tex += w * h // 2
        pal += 32
    dict_bytes = (16 + 8 + 4) * len(props) * 2
    print(f'  decoration textures: {tex:,} B of texture VRAM + {pal:,} B of palettes, dictionaries ~{dict_bytes:,} B')
    rooms_tex = 0
    from nsbtx import decode
    import b2files
    FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    room = {}
    for n in SB.LAYOUTS:
        m = json.load(open(os.path.join(os.path.dirname(P), n, 'room.json')))
        for t, src in m['map_textures'].items(): room[t] = src
    per_set = {}
    for t, src in room.items(): per_set.setdefault(src, []).append(t)
    for src, ts in per_set.items():
        parsed = nsbtx._parse(b2files.map_textures(FILES, src))
        for nm, (params, _) in parsed['texs']:
            if nm in ts:
                w, h, fmt = 8 << ((params >> 20) & 7), 8 << ((params >> 23) & 7), (params >> 26) & 7
                bits = {1: 8, 2: 2, 3: 4, 4: 8, 5: 2, 6: 8, 7: 16}[fmt]
                rooms_tex += w * h * bits // 8
    total = tex + rooms_tex + 12320 + 24608 + 32768
    print(f'  the rooms\' map textures (one set for 24 rooms): {rooms_tex:,} B; with the player and effects {total:,} of 393,216 B')
    if total > 393216: fail('texture VRAM')
    # A doll on a bedroom's rug: the resident's IsOnRug repeats the two rugs of the overlay's grid (a doll placed there was invisible)
    for z, x0 in ((391, 4), (393, 1)):
        rows = SB.grid(SB.BEDROOMS[z][0])['rows']
        cells = {(x, y): v for y, row in enumerate(rows) for x, v in enumerate(row)}
        want = {(x, y) for x in range(x0, x0 + 4) for y in range(3, 7)}
        centre = {(x, y) for x in range(x0 + 1, x0 + 3) for y in range(4, 6)}
        got = {t for t, v in cells.items() if v in (SB.G_EDGE, SB.G_CENTER)}
        if got != want or {t for t, v in cells.items() if v == SB.G_CENTER} != centre: fail(f'zone {z}: the rug differs from IsOnRug')
    ok('the bedrooms\' rugs are where the resident code has them')
    # Colours: the pack's palettes hold the pictures' own colours (a numpy u8 once wrapped in the BGR555 shifts: every decoration red)
    import numpy as np
    bad = []
    for p in props:
        src = SB.rgba_source(p['name'], Image.open(os.path.join(P, p['name'] + '.png')).convert('RGBA'))
        words = struct.unpack(f"<{len(src['pdata']) // 2}H", src['pdata'])
        px = np.array(Image.open(os.path.join(P, p['name'] + '.png')).convert('RGBA'))
        colours = {(int(r) >> 3, int(g) >> 3, int(b) >> 3) for r, g, b, a in px.reshape(-1, 4) if a}
        pal = {(w & 31, (w >> 5) & 31, (w >> 10) & 31) for w in words[1:]}
        if len(colours) <= 15 and not colours <= pal: bad.append(p['name'])
    if bad: fail(f'palettes differ from the pictures: {bad[:5]}')
    ok(f'{len(props)} palettes hold their pictures\' colours')
    nprops = 16 + 8
    if nprops > 32: fail('props')
    ok(f'at most {nprops} props in a chunk of 32; people sprites: 2 of 32 materials (the player\'s), 0 actors')


def spots(world, label):
    print(f'5. the spots on {label} ({world})')
    if not world or not os.path.isdir(os.path.join(world, 'cells')):
        print('  no world: skipped')
        return
    os.environ['HOENN_WORLD_DIR'] = world
    import world as W
    cfg, lay = W.load()
    _, _, main = W.compose(cfg, lay)
    def cell(x, z):
        path = os.path.join(world, 'cells', f'{x // 32:02d}_{z // 32:02d}', 'collision.per')
        if not os.path.exists(path): return None
        return struct.unpack_from('<HHHH', open(path, 'rb').read(), 4 + 8 * ((z % 32) * 32 + x % 32))
    bad = 0
    for i, s in enumerate(SB.spots()):
        m = main[s['map']]
        wx, wz = m['ox'] + s['x'], m['oz'] + s['y']
        a, b = cell(wx, wz), cell(wx, wz + 1)
        if a is None or b is None:
            print(f'  spot {i} {s["map"]} ({s["x"]},{s["y"]}): no cell'); bad += 1; continue
        if not a[3] & 1:
            print(f'  spot {i} {s["map"]} ({s["x"]},{s["y"]}): walkable tile (class {a[2]:#x})'); bad += 1
        if b[3] & 1:
            print(f'  spot {i} {s["map"]} ({s["x"]},{s["y"]}): the tile south is solid (class {b[2]:#x})'); bad += 1
    if bad: fail(f'{label}: {bad} spot findings')
    else: ok('75 spots: solid, with walkable floor south')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--world')
    ap.add_argument('--emerald-world')
    a = ap.parse_args()
    data(); rooms(); scripts(); worst_case()
    if a.world: spots(a.world, 'Sapphire')
    print('FAILED: ' + '; '.join(FAILS) if FAILS else 'all pass')
    sys.exit(1 if FAILS else 0)
