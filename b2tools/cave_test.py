"""Emulator walks through caves (notes/CAVES.md, cave_builder 2026-10-06). One silent DeSmuME run, one sheet image.

    ../.venv/bin/python cave_test.py ROM OUT.png MOVES...              (run from b2tools/, ROM = a uniquely named copy)
    STATE=path.dst ...      start state (default ../work/emu/base_after_rival.dst)
    COLD=1 ...              cold boot instead: fresh battery, the new-game intro as make_states.py plays it, then the
                            moves from Littleroot (173,361): for tables read at boot (the darkness table a/1/4/9)
    HOENN_INTERIORS_DIR     where the built caves are (for Q routing; default work/agents/$HOENN_AGENT/interiors)

Moves (walk.py's plus cave ones):
  U3 D1 L2 R1   hold a direction n tiles       A B   press           W60  wait frames      S  shot     N<text> label next shot
  P  print the tile        C<x>,<z>  find the player's position in RAM while standing on that tile (walk.py)
  G<x>,<z> walk x then z    K<x>,<z> the same with retries    T<x>,<z> route over the overworld (navgrid.py)
  SIGN          from base_after_rival.dst: walk to Littleroot's sign and read it (a HOENN_TEST_WARP build warps)
  Z<Room>       the cave/room the player is in (for Q)     Mwater / Mland  Q routes over water (surfing) / land     Q<x>,<z> route inside it (its collision.per; the zone's
                objects block), the goal may be a warp tile (an arch is walked into)
  Y<x>,<z>      after a warp: wait until the player stands on that tile (tile coordinates repeat between maps, so
                a stale copy can match: look at the shot)
  F<every>,<n>  n shots every <every> frames (transitions)     X<path>  save a state
"""
import sys, os, json, struct, glob
from collections import deque
sys.path.insert(0, os.path.abspath('.'))
from emu import Emu, fresh_battery
from PIL import Image, ImageDraw

rom, out, moves = sys.argv[1], sys.argv[2], sys.argv[3:]
ROOMS = os.environ.get('HOENN_INTERIORS_DIR') or f'../work/agents/{os.environ.get("HOENN_AGENT", "cave_builder")}/interiors'
DIR = {'U': 'UP', 'D': 'DOWN', 'L': 'LEFT', 'R': 'RIGHT'}
SIGN_FROM_RIVAL = 'C179,353 K179,356 K186,356 K186,364 K184,364 K184,366 K183,366 U1 A W300'
SIGN_FROM_LITTLEROOT = 'C173,361 G169,361 G169,356 G186,356 G186,364 G184,364 G184,366 G183,366 U1 A W300'

if os.environ.get('COLD'):
    fresh_battery(rom)
    e = Emu(rom)
    def times(n, ms): return ' '.join([ms] * n)
    e.run(1200)
    for _ in range(40): e.press('A', 6, 50)          # title, Birch's intro (b2tools/make_states.py's moves)
    for _ in range(58): e.press('A', 6, 40)          # boy, name, into the truck: the ride plays
    intro = ('W900 C10,10 R1 W300 ' + times(26, 'A W50') + ' W100 C9,7 U4 U1 W120 L2 U1 A W40 A W40 W200 '
             + times(10, 'A W40') + ' W150 C6,3 A W40 A W40 A W40 W200 G8,3 U1 W150 ' + times(16, 'A W45')
             + ' W100 R4 D3 D1 W200')
    moves = intro.split() + [m for m in (SIGN_FROM_LITTLEROOT.split() if moves[:1] == ['SIGN'] else moves[:1]) ] + moves[1:]
else:
    e = Emu(rom); e.load_state(os.environ.get('STATE', '../work/emu/base_after_rival.dst')); e.run(2)
    if moves[:1] == ['SIGN']: moves = SIGN_FROM_RIVAL.split() + moves[1:]

shots, label, cave = [], '', [None]

WATER_CLASSES = {0x3d, 0x3e, 0x3f, 0x40, 0x42, 0x43}      # surfable tiles (ov036 IsTileSurfWater, waterfall 0x40)
mode = ['land']                                         # 'M' command: land (default) or water routing (caves_east)

def cave_grid(name):
    """Walkable zone tiles of a built cave/room (its collision.per files, and collision1 where a cave has a second
    layer: a tile walkable in either) minus the tiles of its zone's objects; land tiles only, or water tiles only
    after 'Mwater' (caves_east)."""
    d = os.path.join(ROOMS, name)
    meta = json.load(open(os.path.join(d, 'room.json')))
    mw, mh = meta.get('matrix', [1, 1])
    walk = set()
    chunks = meta.get('chunks') or [dict(collision='collision.per', **({'collision1': meta['collision1']} if meta.get('collision1') else {}))]
    for k, c in enumerate(chunks):
        if not c: continue
        for key in ('collision', 'collision1'):
            if not c.get(key): continue
            per = open(os.path.join(d, c[key]), 'rb').read()
            for i in range(1024):
                a, b, cls, fl = struct.unpack_from('<HHHH', per, 4 + 8 * i)
                if fl & 1 or ((cls in WATER_CLASSES) != (mode[0] == 'water')): continue
                walk.add(((k % mw) * 32 + i % 32, (k // mw) * 32 + i // 32))
    ox, oz = meta.get('origin', [0, 0])
    for f in glob.glob('../data/interiors/*.json'):
        j = json.load(open(f))
        if j.get('room') == name:
            for n in j.get('npcs', []): walk.discard((n['at'][0] + ox, n['at'][1] + oz))
    return walk

def route(start, goal, walk):
    prev = {start: None}; q = deque([start])
    mv = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}
    while q:
        p = q.popleft()
        if p == goal: break
        for k, (dx, dz) in mv.items():
            n = (p[0] + dx, p[1] + dz)
            if n in prev or (n not in walk and n != goal): continue
            prev[n] = (p, k); q.append(n)
    if goal not in prev: return None
    path, p = [], goal
    while prev[p]: p, k = prev[p]; path.append(k)
    return path[::-1]

def travel_cave(tx, tz):
    walk = cave_grid(cave[0])
    for _ in range(4):
        if e.player_tile() == (tx, tz): return True
        path = route(e.player_tile(), (tx, tz), walk)
        if path is None: return False
        for mv in path:
            if not e.step(mv): e.run(30); break
    return e.player_tile() == (tx, tz)

def goto_retry(tx, tz, tries=12):
    for _ in range(tries):
        if e.goto(tx, tz): return True
        e.run(40)
    return e.player_tile() == (tx, tz)

def snap():
    global label
    im = e.d.screenshot().crop((0, 0, 256, 192)); d = ImageDraw.Draw(im)
    if label: d.text((3, 3), label, fill=(255, 255, 0)); label = ''
    shots.append(im)

for m in moves:
    xz = lambda: tuple(map(int, m[1:].split(',')))
    if m[0] in DIR and m[1:].isdigit(): e.hold(DIR[m[0]], 16 * int(m[1:])); e.run(4)
    elif m == 'A': e.press('A', 6, 30)
    elif m == 'B': e.press('B', 6, 30)
    elif m[0] == 'W': e.run(int(m[1:]))
    elif m[0] == 'N': label = m[1:]
    elif m == 'S': snap()
    elif m == 'P': print('pos', e.player_tile())
    elif m[0] == 'C': print('calibrated' if e.calibrate(*xz()) else 'calibration failed', xz())
    elif m[0] == 'G': print('goto', xz(), 'ok' if e.goto(*xz()) else f'blocked at {e.player_tile()}')
    elif m[0] == 'K': print('goto*', xz(), 'ok' if goto_retry(*xz()) else f'blocked at {e.player_tile()}')
    elif m[0] == 'T': print('travel', xz(), 'ok' if e.travel(*xz()) else f'stopped at {e.player_tile()}')
    elif m[0] == 'Z': cave[0] = m[1:]
    elif m[0] == 'M': mode[0] = m[1:]          # Mwater / Mland: what Q routes over (surfing or walking)
    elif m[0] == 'Q': print('cave travel', xz(), 'ok' if travel_cave(*xz()) else f'stopped at {e.player_tile()}')
    elif m[0] == 'X': e.save_state(m[1:]); print('saved', m[1:])
    elif m[0] == 'Y':
        ok = False
        for _ in range(40):
            e.run(15)
            if e.calibrate(*xz()): ok = True; break
        print('arrived' if ok else 'NOT arrived', xz())
    elif m[0] == 'F':
        ev, cnt = map(int, m[1:].split(','))
        for i in range(cnt): e.run(ev); label = label or f'+{ev * (i + 1)}'; snap()
    else: print('unknown move', m)
if shots:
    cols = min(4, len(shots)); rows = (len(shots) + cols - 1) // cols
    sheet = Image.new('RGB', (256 * cols, 192 * rows))
    for i, im in enumerate(shots): sheet.paste(im, (256 * (i % cols), 192 * (i // cols)))
    sheet.save(out)
print('shots', len(shots), '->', out)
e.close()
