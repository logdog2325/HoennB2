"""Gen 3's rotating gates (th_p6, 2026-10-19; notes/TRICK_HOUSE.md "P6"): Trick House Puzzle 6, faithful per version
(Sapphire/Ruby: pokeruby's 14 gates, Emerald: pokeemerald's 11). A port of src/rotating_gate.c in rotating_gates.c.

Black 2 has no rotating gates and runs no script when you walk into something, so this is field code:
  1. The player's move check. ov036 PlayerMoveCollCheck (0x0219c88c: the tile, actor and height checks of a step) is
     called by FieldPlayerGrid_DecideCommandNormalMoving (walking and running, `bl` at 0x0219bc30) and the bike's
     move decision (func_ov036_0219c000, 0x0219c034). Both calls go to Gate_MoveCollCheck: Black 2's check first, and
     when nothing is in the way (Gen 3: COLLISION_NONE) CheckForRotatingGatePuzzleCollision's: the destination tile in a
     gate's 4x4 square + the direction -> the arm walked into (sRotatingGate_RotationInfo*); with an arm there, the
     gate turns if no map collision is where its arms sweep (sRotatingGate_ArmPositions*, as Gen 3's check, which
     looks at the map only) and the step goes on, else the result is 4 (an actor's bit: the player bumps).
     Surfing, forced moves and catwalks keep Black 2's check (Gen 3 has no gate on water or ice).
  2. The arms' drawing: ov036's 3D draw processor table (0x021cf9a0, the only one: models_objects.py) entry 1
     (0x021cf9a4, func_ov036_021974b4, which only sets the model's position) -> Gate_Update3D: Black 2's, then for a
     gate arm (object codes GATE_CODE_SHORT / _LONG) the turn, the pivot offset and the quarter-turn animation, and the
     arm leaves Black 2's actor collision (flag 0x80). Every other 3D actor is unchanged.
State: map-local works 0x4000 + gate (quarter turns since the zone init; Gen 3's VAR_TEMP_*). Gates of a zone: PUZZLES
(Gen 3's GetCurrentMapRotatingGatePuzzleType: Trick House Puzzle 6 = zone 442, Fortree Gym = zone 119; fortree_gates
2026-10-20), one table per version (pokeruby / pokeemerald); a zone's gates are numbered from 0 (its works and arm uids).
Arm actors: Puzzle 6's in data/story/trick_house.json (b2tools/trick_house.py puzzle6_objects), Fortree's in
data/story/fortree_gates.json (pokeruby) / data/story/emerald/fortree_gates.json (pokeemerald), written by
`python3 rotating_gates.py story` (story_objects).

Code space: ITCM after the other patches' code (the arena literal arm9 0x0207B400, as rods.py); run it after them.
Main-RAM code: savestates made before need a cold boot or a state of this ROM.

    python3 rotating_gates.py          compile at a dummy base and print the gates of both versions
    python3 rotating_gates.py story    write Fortree Gym's arm actors (data/story/fortree_gates.json + emerald/)
    python3 rotating_gates.py check    the same, only checking the files are current (exit 1 if not)
"""
import os, re, json, struct, subprocess, sys, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV036 = 0x0217F600
PLAYER_MOVE_COLL_CHECK = 0x0219C88C
CALLS = [0x0219BC30, 0x0219C034]          # FieldPlayerGrid_DecideCommandNormalMoving, the bike's (func_ov036_0219c000)
DRAW_3D_SLOT, DRAW_3D = 0x021CF9A4, 0x021974B4
GATE_ZONE = 442                           # Route110_TrickHousePuzzle6 (data/hoenn_interiors.json)
# The zones with gates (rotating_gate.c GetCurrentMapRotatingGatePuzzleType): (sRotatingGate_<which>PuzzleConfig, zone,
# zone tile of Gen 3 tile (0, 0) (the built room's origin, room.json), the Gen 3 map (Sapphire's name)). Both Fortree
# rooms (Sapphire's and Emerald's variant) have origin (1, 1), as every Trick House room.
PUZZLES = [('TrickHouse', GATE_ZONE, (1, 1), 'Route110_TrickHousePuzzle6'),
           ('Fortree', 119, (1, 1), 'FortreeCity_Gym')]
GATE_UID0 = 100                           # arm actors: uid 100 + 4 * gate + shape arm (N, E, S, W)
GATE_CODE_SHORT, GATE_CODE_LONG = 119, 135   # empty people records (patches/objects3d.py FREE_PEOPLE_RECORDS)
GATE_SE = 0x674                           # SE_ROTATING_GATE -> SEQ_SE_FLD_03, Black 2's Strength boulder push sound
                                          # (EventStrengthRockPush_Callback; a one-shot field sound) [guess: listen]
ORIGIN = (1, 1)                           # zone tile = Gen 3 tile + (1, 1) (every Trick House room)
SHAPES = ['L1', 'L2', 'L3', 'L4', 'T1', 'T2', 'T3', 'T4']
DIRS = {'NORTH': 0, 'EAST': 1, 'SOUTH': 2, 'WEST': 3}


def _decomp(v):
    return os.path.join(ROOT, 'external', 'pokeruby' if v == 'rs' else 'pokeemerald', 'src', 'rotating_gate.c')


def gates(v, which='TrickHouse'):
    """[(x, y, shape 0-7, orientation 0-3)] in Gen 3 tiles: sRotatingGate_{which}PuzzleConfig (v 'rs' pokeruby, 'em'
    pokeemerald)."""
    src = open(_decomp(v)).read()
    body = re.search(rf'RotatingGate_{which}PuzzleConfig\[\]\s*=\s*\{{(.*?)\}};', src, re.S).group(1)
    out = []
    for x, y, sh, o in re.findall(r'\{\s*(\d+),\s*(\d+),\s*GATE_SHAPE_(\w+),\s*GATE_ORIENTATION_(\d+)\s*\}', body):
        out.append((int(x), int(y), SHAPES.index(sh), int(o) // 90))
    assert out, which
    return out


def tables(v):
    """The decomp's tables: rotation info (B2 direction order up, down, left, right = N, S, W, E), arm positions
    (ACW, CW), arm layout of the 8 shapes."""
    src = open(_decomp(v)).read()
    def body(name):
        return re.search(rf'{name}\[[^\]]*\](?:\[[^\]]*\])?\s*=\s*\{{(.*?)\}};', src, re.S).group(1)
    def rot(name):
        out = []
        for tok in re.findall(r'GATE_ROT_NONE|GATE_ROT_(?:A?CW)\(\s*GATE_ARM_\w+\s*,\s*\d\s*\)', body(name)):
            if tok == 'GATE_ROT_NONE': out.append(0xFF); continue
            m = re.match(r'GATE_ROT_(A?CW)\(\s*GATE_ARM_(\w+)\s*,\s*(\d)', tok)
            r = 1 if m[1] == 'ACW' else 2
            out.append((r & 15) << 4 | (DIRS[m[2]] & 7) << 1 | int(m[3]) & 1)
        assert len(out) == 16, name
        return out
    info = [rot(f'sRotatingGate_RotationInfo{d}') for d in ('North', 'South', 'West', 'East')]
    def pos(name):
        p = [tuple(map(int, t)) for t in re.findall(r'\{\s*(-?\d+),\s*(-?\d+)\s*\}', body(name))]
        assert len(p) == 8, name
        return p
    arm = [pos('sRotatingGate_ArmPositionsAntiClockwiseRotation'), pos('sRotatingGate_ArmPositionsClockwiseRotation')]
    lay = [list(map(int, re.findall(r'\d', b))) for b in re.findall(r'\{([\d,\s]*)\}', body('sRotatingGate_ArmLayout'))]
    assert len(lay) >= 8 and all(len(l) == 8 for l in lay), lay
    return info, arm, lay[:8]


def arms(v, which='TrickHouse'):
    """[(gate, shape arm 0-3 (N E S W), long?)] of every arm of the version's gates (the arm actors)."""
    _, _, lay = tables(v)
    return [(g, i, bool(lay[sh][2 * i + 1])) for g, (x, y, sh, o) in enumerate(gates(v, which))
            for i in range(4) if lay[sh][2 * i]]


def story_objects(v, which='Fortree'):
    """A puzzle's arm actors as story objects (patches/story.py; "at" = Gen 3 tile of the puzzle's map): one 3D actor per
    arm, uid GATE_UID0 + 4 * gate + shape arm (N E S W), code GATE_CODE_SHORT / _LONG, standing on the first walkable
    tile of the four around the pivot (the gate's tile, west, north, north-west), as trick_house.puzzle6_objects places
    Puzzle 6's; rotating_gates.c turns each one onto its tile edge and takes it out of the actor collision."""
    import models_interior as mi
    name = next(p[3] for p in PUZZLES if p[0] == which)
    sm = mi.sapphire_map(('pokeemerald/' if v == 'em' else '') + name)
    people = {(o['x'], o['y']) for o in sm['objects']}
    gs, out = gates(v, which), []
    for g, arm, long in arms(v, which):
        x, y, sh, o = gs[g]
        at = next(t for t in ((x, y), (x - 1, y), (x, y - 1), (x - 1, y - 1)) if sm['walk'][t[1]][t[0]])
        assert at not in people, f'{which} gate {g}: a person stands on {at}'
        out.append(dict(kind='npc', map=name, at=list(at), uid=GATE_UID0 + 4 * g + arm,
                        model=GATE_CODE_LONG if long else GATE_CODE_SHORT, script=0, dir=1, flag=0,
                        what=f"gate {g} ({SHAPES[sh]} at Gen 3 ({x},{y}), turned {90 * o}): its {'NESW'[arm]} arm "
                             f"({'long' if long else 'short'}), standing on {tuple(at)}"))
    return out


def write_story(check=False):
    """data/story/fortree_gates.json (Sapphire/Ruby: pokeruby) and data/story/emerald/fortree_gates.json (pokeemerald):
    Fortree Gym's arm actors. Returns the files that changed (check: that would change)."""
    changed = []
    for v, path in (('rs', os.path.join(ROOT, 'data', 'story', 'fortree_gates.json')),
                    ('em', os.path.join(ROOT, 'data', 'story', 'emerald', 'fortree_gates.json'))):
        objs = story_objects(v, 'Fortree')
        doc = (f"Fortree Gym's rotating gates (fortree_gates 2026-10-20; GENERATED by b2tools/patches/rotating_gates.py "
               f"story: edit the generator): the arm actors of {'pokeruby' if v == 'rs' else 'pokeemerald'}'s "
               f"sRotatingGate_FortreePuzzleConfig ({len(gates(v, 'Fortree'))} gates, {len(objs)} arms; "
               f"{'Sapphire/Ruby' if v == 'rs' else 'Emerald, replacing data/story/fortree_gates.json'}). Positions: "
               f"Gen 3 tiles of FortreeCity_Gym{'' if v == 'rs' else ' (Emerald map)'}; the turning and the gates' "
               "collision are b2tools/patches/rotating_gates.c (zone 119).")
        text = '{\n "_doc": ' + json.dumps(doc) + ',\n "objects": [\n' + \
            ',\n'.join('  ' + json.dumps(o) for o in objs) + '\n ]\n}\n'
        old = open(path).read() if os.path.exists(path) else None
        if old != text:
            changed.append(os.path.relpath(path, ROOT))
            if not check:
                open(path, 'w').write(text)
    return changed


def header(v):
    info, arm, lay = tables(v)
    assert (info, arm, lay) == tables('em' if v == 'rs' else 'rs'), 'pokeruby and pokeemerald tables differ'
    puz, rows = [], []
    for which, zone, (ox, oy), _m in PUZZLES:
        g = gates(v, which)
        puz.append(f'{{{zone}, {len(rows)}, {len(g)}}}')
        rows += [f'    {{{x + ox}, {y + oy}, {sh}, {o}}},  /* {which} {i}: Gen 3 ({x}, {y}) {SHAPES[sh]} {90 * o} */'
                 for i, (x, y, sh, o) in enumerate(g)]
    body = '\n'.join(rows)
    c = lambda l: '{' + ', '.join(str(n) for n in l) + '}'
    return (f'/* GENERATED by b2tools/patches/rotating_gates.py from {os.path.relpath(_decomp(v), ROOT)} */\n'
            f'#define GATE_PUZZLES {len(PUZZLES)}\n#define GATE_TOTAL {len(rows)}\n#define GATE_UID0 {GATE_UID0}\n'
            f'#define GATE_CODE_SHORT {GATE_CODE_SHORT}\n#define GATE_CODE_LONG {GATE_CODE_LONG}\n#define GATE_SE {GATE_SE:#x}\n'
            f'/* {{zone, first gate in sGates, gate count}}: {", ".join(p[0] for p in PUZZLES)} */\n'
            f'static const u16 sPuzzles[GATE_PUZZLES][3] = {{{", ".join(puz)}}};\n'
            f'/* {{x, y (zone tiles = Gen 3 + the room origin), shape (GATE_SHAPE_*), orientation (quarter turns)}} */\n'
            f'static const u8 sGates[GATE_TOTAL][4] = {{\n{body}\n}};\n'
            f'/* sRotatingGate_RotationInfo North, South, West, East (= Black 2 directions up, down, left, right) */\n'
            f'static const u8 sRotInfo[4][16] = {{{", ".join(c(r) for r in info)}}};\n'
            f'/* sRotatingGate_ArmPositions AntiClockwise, Clockwise */\n'
            f'static const s8 sArmPos[2][8][2] = {{{", ".join("{" + ", ".join(c(p) for p in a) + "}" for a in arm)}}};\n'
            f'static const u8 sArmLayout[8][8] = {{{", ".join(c(l) for l in lay)}}};\n')


ARM_COLOURS = [(57, 57, 24), (123, 115, 65), (16, 16, 8), (180, 164, 98)]   # pokeemerald graphics/rotating_gates/*.png:
                                    # the arm's body and its light stripe, the pivot ring and its centre (palette 13, 12, 15, 11)

def arm_model(long):
    """src/objects3d/<code>-gate-arm-short|long: one arm of a rotating gate as Black 2 draws a 3D actor: a low rail
    (4 units wide, 10 high) from the pivot north (-z) for 1 or 2 tiles (16 per tile), the pivot post (6 x 6, 12 high) at
    the model's origin; Gen 3's colours (one 8x8 texture, a band per colour). Gate_Update3D turns it and puts the origin
    on the pivot. Returns (BMD0 bytes, object.json dict)."""
    import numpy as np
    import models_objects as MO
    from dae import Model
    px = np.zeros((8, 8, 4), dtype=np.uint8)
    for k, c in enumerate(ARM_COLOURS):
        px[2 * k:2 * k + 2, :, :3] = c
    px[..., 3] = 255
    uv = lambda k: (0.5, 1 - (2 * k + 1) / 8)            # the middle of colour band k (v = 1 at the image's top row)
    m = Model('gatearm')
    def box(x0, x1, y0, y1, z0, z1, side, top, shade=0.8):
        su, sv = uv(side); tu, tv = uv(top)
        m.quad('gatearm', [(x0, y1, z0, tu, tv), (x0, y1, z1, tu, tv), (x1, y1, z1, tu, tv), (x1, y1, z0, tu, tv)])  # top (+y)
        f = lambda pts, s: m.quad('gatearm', [p + (su, sv) for p in pts], (s, s, s))
        f([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], 1.0)      # south (+z)
        f([(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)], shade)    # north (-z)
        f([(x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)], shade)    # east (+x)
        f([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], shade)    # west (-x)
    n = 2 if long else 1
    box(-2, 2, 0, 10, -16 * n + 1, -3, 0, 1)               # the rail (Gen 3's bar: body, light stripe on top); its
                                    # top and sides 2 units off a wall block it lies along (P6's plank boxes: 8 high;
                                    # 1-1.5 units flickered in melonDS: th_check67 2026-10-20)
    box(-3, 3, 0, 12, -3, 3, 2, 3)                          # the pivot post (the black ring, its light centre on top)
    mdl = MO.to_mdl0(m, {'gatearm': px})
    bmd = MO.bmd0(mdl, MO.tex0_block([('gatearm', px, 3)]))
    code = GATE_CODE_LONG if long else GATE_CODE_SHORT
    meta = dict(code=code, name=f'gate-arm-{"long" if long else "short"}',
                what=f"a rotating gate's {'long (2 tiles)' if long else 'short (1 tile)'} arm (Gen 3 rotating_gate.c: "
                     'Trick House Puzzle 6): a rail pointing north from the pivot post at the origin; '
                     'b2tools/patches/rotating_gates.c turns it and moves the origin onto the pivot (a tile corner)',
                record_from=0x2009, record={'collWidth': 1, 'collHeight': 1, 'offX': 0, 'offY': 0, 'offZ': 0},
                made_by='b2tools/patches/rotating_gates.py (arm_model; b2tools/trick_house.py writes it)')
    return bmd, meta


def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_link', os.path.join(HERE, 'roamers.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _bl(src, dst):
    off = dst - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, hex(off)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)


def _put(d, base, addr, old, new, what):
    o = addr - base
    cur = bytes(d[o:o + len(new)])
    assert cur in (old, new), f'{what} at {addr:#x}: {cur.hex()} (expected {old.hex()})'
    d[o:o + len(new)] = new


def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())


def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)


def _version():
    import version
    return 'em' if version.EMERALD else 'rs'


def build(base, workdir, v):
    open(os.path.join(workdir, 'rotating_gates_gen.h'), 'w').write(header(v))
    obj = os.path.join(workdir, 'rotating_gates.o')
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror', '-I', workdir,
                    '-c', os.path.join(HERE, 'rotating_gates.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'rotating_gates.c needs {und}: call Black 2 functions by address only'
    return _roamers().link(obj, base)


def apply_code(code):
    v = _version()
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    p9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not at the end of ITCM (run after hoenn_world)'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym = build(base, tmp, v)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    _save(p9, arm9)
    pi, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(pi, bytes(itcm) + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    p036, ov036 = _load(code, 'arm9_ov036.bin')
    for at in CALLS:
        _put(ov036, OV036, at, _bl(at, PLAYER_MOVE_COLL_CHECK), _bl(at, sym['Gate_MoveCollCheck'] & ~1),
             'bl PlayerMoveCollCheck')
    _put(ov036, OV036, DRAW_3D_SLOT, struct.pack('<I', DRAW_3D | 1), struct.pack('<I', sym['Gate_Update3D'] | 1),
         '3D draw processor entry 1')
    _save(p036, ov036)
    zones = ', '.join(f'zone {z}: {len(gates(v, w))} gates' for w, z, _o, _m in PUZZLES)
    return (f'rotating_gates: {len(blob)} B of ITCM at {base:#x} (arena from {end:#x}, {0x02000000 - end} B left); '
            f'{zones} ({"pokeemerald" if v == "em" else "pokeruby"}); move check '
            f'{", ".join(hex(c) for c in CALLS)}, 3D draw {DRAW_3D_SLOT:#x}')


if __name__ == '__main__':
    if sys.argv[1:2] in (['story'], ['check']):
        ch = write_story(check=sys.argv[1] == 'check')
        print(('stale: ' if sys.argv[1] == 'check' else 'written: ') + (', '.join(ch) or 'nothing'))
        sys.exit(1 if ch and sys.argv[1] == 'check' else 0)
    for v in ('rs', 'em'):
        with tempfile.TemporaryDirectory() as tmp:
            blob, sym = build(0x01FFE000, tmp, v)
            print(v, len(blob), 'B', {k: hex(x) for k, x in sym.items() if k.startswith('Gate_')},
                  '; '.join(f'{w} zone {z}: {len(gates(v, w))} gates, {len(arms(v, w))} arms' for w, z, _o, _m in PUZZLES))
