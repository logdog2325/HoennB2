"""Walkable grid of the chunks we built (work/chunks/*/chunk.json 'collision'), for routing test walks
(HOENN_NAV_GROUP=<group>: a warp-only map's own matrix instead of the main one).
Characters: '#' solid, 'v' ledge (can only be crossed going south), anything else walkable."""
import glob, json, os
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__))

def load():
    grid = {}
    world_dir = os.environ.get('HOENN_WORLD_DIR') or os.path.join(HERE, '..', 'work', 'world')   # agents: own dir
    group = os.environ.get('HOENN_NAV_GROUP')      # a warp-only map's own matrix (world.json 'standalone' group)
    if group:
        g = next(g for g in json.load(open(os.path.join(world_dir, 'world.json')))['standalone'] if g['group'] == group)
        cells = [((c['cx'], c['cz']), os.path.join(world_dir, 'cells', c['dir'], 'chunk.json')) for c in g['cells']]
    else:                                          # the main matrix (its cells, not the warp-only maps' s_* nor the
        cells = [(None, f) for f in glob.glob(os.path.join(world_dir, 'cells', '*', 'chunk.json'))   # alt layouts' alt_*)
                 if not os.path.basename(os.path.dirname(f)).startswith(('s_', 'alt_'))]
    for at, f in cells:
        c = json.load(open(f)); cx, cz = at or c['cell']
        for z, row in enumerate(c['collision']):
            for x, ch in enumerate(row):
                grid[(cx * 32 + x, cz * 32 + z)] = ch
    return grid

def route(start, goal, grid=None, avoid=''):
    """Shortest list of moves ('UP'/'DOWN'/'LEFT'/'RIGHT') from start to goal tile; a ledge is jumped going down.
    Tiles in `avoid` are not used (e.g. 'g' to keep out of tall grass). Test builds made with HOENN_TEST_NO_WILD=1
    have no wild battles, so routes may cross tall grass."""
    grid = grid or load()
    moves = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}
    prev = {start: None}; q = deque([start])
    while q:
        p = q.popleft()
        if p == goal: break
        for name, (dx, dz) in moves.items():
            n = (p[0] + dx, p[1] + dz); ch = grid.get(n, '#')
            if ch == 'v':
                if name != 'DOWN': continue
                n = (n[0], n[1] + 1)                 # jumping a ledge lands one tile past it
                if grid.get(n, '#') in '#v': continue
            elif ch == '#' or (ch in avoid and n != goal):
                continue
            if n not in prev:
                prev[n] = (p, name); q.append(n)
    if goal not in prev: return None
    out = []; p = goal
    while prev[p]:
        p, name = prev[p]; out.append(name)
    return out[::-1]
