"""Scripted walks against the built collision (wally_walk, 2026-10-12; start guesses and Sapphire comparison: walk_sweep,
2026-10-12). Read-only.

    python3 scene_walks.py [--world WORLD] [--rooms ROOMS] [--files 0878,0904,...] [--maps A,B] [-v]
    SCENE_WALKS_TRACE=1 ...   also prints every walk followed (start and end tile)
    SCENE_WALKS_FS=DIR ...    reads the field scripts from DIR (e.g. an older copy, to check the checker)

For every field script file (src/field_scripts/*.s, preprocessed as the build does, HOENN_VERSION picks the version),
each ScriptEntry is followed through its branches (every conditional goto/call both ways, except the player-facing
variable set by h_getplayerfacing, which is known per start). Each h_applymovement / ActorCmdExec walks its actor from
where it stands and every tile it steps on is looked up in the built collision of the script's zone (outdoor maps:
the world's collision.per cells, outdoor_check.frames; rooms and caves: ROOMS/<map>/collision*.per, a tile counting as
walkable when either layer is: collision1 holds the bridge decks).

What is reported (counted in the total):
  solid        a step onto a tile the built world blocks and Sapphire does not;
  solid (Sapphire blocks it too, mid-walk)
               a blocked stretch in the middle of a walk that goes on afterwards: what a walk started on the wrong tile
               looks like (Wally's tutorial ran through the Pokémon Center's front wall that way);
  lands on a Sapphire door tile
               a scripted warp that starts a scene lands on a tile whose Sapphire metatile is a door: Sapphire's warp
               exit walks the player one tile south first, Black 2's scripted map change does not (fix: land on the
               tile below, as 3cb602e did in Petalburg);
  outside the built zone.
Listed with -v only: 'solid (Sapphire too)' (someone starting on a tile Sapphire blocks: Latios in the wall, Kyogre in
its pool, the submarine; or a walk ending in tiles Sapphire blocks: the Kecleon fleeing into a tree), 'solid (start
guessed ...)' (a person the zone init moves, followed from a start that is not known to apply), and ACCEPT entries.
Never reported: the last step of a walk into a door/warp tile, or of a list that ends with set_invisible (someone
walking into a door, an elevator, onto the submarine).

Where people start:
  the player   trigger scripts: the trigger tile (data/story/*.json, data/interiors/<zone>.json and world.json triggers,
               with the trigger's var value known to the zone init);
               talk scripts: the four tiles next to the person whose script it is (facing them), not where someone else
               stands, and in a room only tiles you can walk to from its exit mats without passing anyone; not for a
               script that is a scripted warp's arrival scene;
               h_warp_scene / RTReserveScript + MapChangeCore arrivals: that warp's tile; OnFrame scripts
               (MapScriptCondition): every plain scripted warp into the zone whose script sets the condition's var to
               its value (MapChangeCore, MapChangeWarp, h_warpsilent, h_warp_arrive of any script file);
               otherwise unknown (the player's walks are skipped).
  people       data/story objects (uid, Sapphire tile 'at' + the map's offset, or zone/x/z), the generated people
               (world.json zone npcs: uid = index unless they carry one; data/interiors/<zone>.json npcs), and every
               ObjInitNPCGPos / h_setobjectxyperm of the zone init as the build sees it (preprocessed: another
               version's lines do not count; #defines and one-parameter macros evaluated), its index turned into a uid
               by a NAME_INDEX define or else by the zone's NPC list order (built people, then story objects in file
               order, as patches/story.py appends them). A move under a guard on a var the start knows applies or not;
               one in a block reached by `h_goto_if_<op> VAR, n, LABEL` applies when that jump is taken; one under an
               unknown guard is an extra candidate. Each candidate start is tried.
Coordinates in the report: zone tile, then the Sapphire map tile in brackets.
"""
import os, sys, re, json, struct, glob, subprocess, argparse
from collections import defaultdict

ROOT = os.path.expanduser('~/Documents/GitHub/HoennB2')
sys.path[:0] = [os.path.join(ROOT, 'b2tools'), os.path.join(ROOT, 'b2tools', 'patches'), os.path.join(ROOT, 'converter')]
import version
import outdoor_check as oc

FS = os.environ.get('SCENE_WALKS_FS') or os.path.join(ROOT, 'src', 'field_scripts')
DIRV = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
ORDER = ['up', 'down', 'left', 'right']
GENDER = ['boy']
SPECIAL = {'0634': 'Route101', '0778': 'LittlerootTown', '0788': 'InsideOfTruck', '0792': 'LittlerootTown_ProfessorBirchsLab',
           '0794': 'OldaleTown', '0780': 'LittlerootTown_BrendansHouse_1F', '0782': 'LittlerootTown_BrendansHouse_2F',
           '0784': 'LittlerootTown_MaysHouse_1F', '0786': 'LittlerootTown_MaysHouse_2F'}
FACE_TO = {(0, -1): 1, (0, 1): 0, (-1, 0): 3, (1, 0): 2}   # player's offset from the person -> Black 2 facing (0 up 1 down 2 left 3 right)
# Findings checked and kept on purpose: (file, words of the finding) -> why. Listed with -v only.
ACCEPT = {
    ('0672_room_BattleTower_Corridor.s', 'lands on a Sapphire door tile'):
        "the room draws a one-tile wall with the doors north of row 1, so Sapphire's door tile (8,1) is the floor in "
        "front of the elevator, where Sapphire's step leaves the player (data/interior_layouts/BattleTower_Corridor.json; "
        "the attendant stands beside it at (9,1): walk_sweep 2026-10-12)",
}


# ------------------------------------------------------------------------------------------------- preprocessing
def preprocess(path):
    dec = os.path.join(ROOT, 'external', 'pokebw2')
    r = subprocess.run(['/opt/homebrew/opt/llvm/bin/clang', '-E', '-P', '-x', 'assembler-with-cpp', '-I', f'{dec}/include',
                        '-I', f'{dec}/lib/nitro/include', '-I', os.path.join(ROOT, 'src', 'include'), '-I', FS,
                        '-D', 'BLACK2', *version.ASM_DEFINES, path], capture_output=True, text=True, cwd=os.path.dirname(path))
    if r.returncode: raise RuntimeError(r.stderr[:400])
    return r.stdout

_PP = {}
def preprocess_cached(path):
    if path not in _PP:
        try: _PP[path] = preprocess(path)
        except Exception: _PP[path] = open(path).read()
    return _PP[path]

def num(s):
    s = s.strip()
    try: return int(s, 0)
    except ValueError: pass
    if re.fullmatch(r'[0-9xa-fA-F+\-*() ]+', s) and re.search(r'\d', s):
        try: return int(eval(s, {'__builtins__': {}}))
        except Exception: return None
    return None

class Steps(list):
    vanish = False

def parse(text):
    """(code [(op, args, line)], labels {name: index}, movements {label: [(dx, dz, last_ok)]}, entries [label])"""
    code, labels, entries = [], {}, []
    for raw in text.split('\n'):
        ln = raw.split('//')[0].strip()
        if not ln: continue
        m = re.match(r'^([A-Za-z_.][\w.]*):\s*(.*)$', ln)
        if m:
            labels[m.group(1)] = len(code); ln = m.group(2).strip()
            if not ln: continue
        parts = ln.split(None, 1)
        op = parts[0]; args = [a.strip() for a in parts[1].split(',')] if len(parts) > 1 else []
        if op == 'ScriptEntry': entries.append(args[0]); continue
        code.append((op, args, ln))
    moves = {}
    for lab, i in labels.items():
        steps, j = Steps(), i
        while j < len(code):
            op, args, _ = code[j]
            if op in ('step_end', 'MoveEnd'): break
            n = num(args[-1]) if args else 1
            m = re.match(r'^(walk|walk_slow|walk_fast|walk_fastest|jump|jump_2)_(up|down|left|right)$', op)
            if m:
                d = DIRV[m.group(2)]; k = 2 if m.group(1) == 'jump_2' else 1
                steps += [(d[0] * k, d[1] * k)] * (n or 1)
            elif op in ('Move', 'hmv') and args:
                c = num(args[0]); n = num(args[1]) if len(args) > 1 else 1
                if c is not None and 4 <= c <= 27: d = DIRV[ORDER[(c - 4) % 4]]; steps += [d] * n
                elif c is not None and 52 <= c <= 59:
                    d = DIRV[ORDER[c % 4]]; k = 1 if c < 56 else 2; steps += [(d[0] * k, d[1] * k)] * n
                elif c is not None and 92 <= c <= 95: d = DIRV[ORDER[c % 4]]; steps += [(d[0] * 3, d[1] * 3)] * n
            elif not (op.startswith(('walk_in_place', 'face_', 'delay', 'jump_in_place', 'emote', 'set_', 'lock_', 'unlock_'))
                      or op in ('Move', 'hmv', '.balign')):
                break                                     # not a movement list (a script label)
            if op == 'set_invisible' and steps: steps.vanish = True   # walks into something and disappears (a door,
            j += 1                                                    # an elevator, a submarine): its last step may be solid
        if j < len(code) and code[j][0] in ('step_end', 'MoveEnd'): moves[lab] = steps
    return code, labels, moves, entries


# ------------------------------------------------------------------------------------------------- the world
class Coll:
    """solid(x, z) -> True / False / None (outside) of one zone; off(x, z) -> Sapphire tile; doors: warp tiles.
    sap_solid(x, z): Sapphire's own collision bits at that zone tile (None outside the map), so a step onto a tile that
    Sapphire blocks too (a Kecleon fleeing into a tree, Latios flying out of the wall) is told apart from one that only
    the built world blocks (walk_sweep, 2026-10-12)."""
    def __init__(self, solid, ox, oz, doors, mp=None):
        self.solid, self.ox, self.oz, self.doors = solid, ox, oz, doors
        self._sap = sapphire_grid(mp) if mp else None
        self._mp = mp
        self._reach = None
    def sap(self, p): return (p[0] - self.ox, p[1] - self.oz)
    def sap_door(self, x, z):
        """True on a tile whose Sapphire metatile is a door (MB_ANIMATED_DOOR 0x69 / MB_NON_ANIMATED_DOOR 0x60):
        Sapphire's warp exit (field_fadetransition.c sub_8080AE4) walks the player one tile south off it before any
        OnFrame scene runs; Black 2's scripted map change does not (wally_walk, Petalburg 2026-10-12)."""
        if self._sap is None or self._mp is None: return False
        sx, sz = x - self.ox, z - self.oz
        if not (0 <= sz < self._sap.shape[0] and 0 <= sx < self._sap.shape[1]): return False
        return sapphire_behavior(self._mp, int(self._sap[sz, sx]) & 0x3FF) in (0x60, 0x69)
    def sap_solid(self, x, z):
        if self._sap is None: return None
        sx, sz = x - self.ox, z - self.oz
        g = self._sap
        if not (0 <= sz < g.shape[0] and 0 <= sx < g.shape[1]): return None
        return bool((int(g[sz, sx]) >> 10) & 3)
    def reachable(self, t, room, blocked=frozenset()):
        """False when t cannot be walked to from the zone's doors without stepping on a blocked tile (people) (rooms
        with doors only; else True)."""
        seeds = getattr(self, 'entries', None) or set()
        if not room or not seeds: return True
        key = frozenset(blocked)
        if self._reach is None: self._reach = {}
        if key not in self._reach:
            seen, todo = set(), []
            for d in seeds:
                for dx, dz in ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)):
                    q = (d[0] + dx, d[1] + dz)
                    if self.solid(*q) is False and q not in seen and q not in key: seen.add(q); todo.append(q)
            while todo:
                x, z = todo.pop()
                for dx, dz in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    q = (x + dx, z + dz)
                    if q not in seen and q not in key and self.solid(*q) is False: seen.add(q); todo.append(q)
            self._reach[key] = seen
        return t in self._reach[key]

_SB = {}
def sapphire_behavior(mp, metatile):
    """Sapphire's metatile behaviour of a metatile id of map mp"""
    if mp not in _SB:
        try:
            from gba import MetatileRenderer
            R = _SG.get('repo')
            l = R.layouts[R.map_json(mp)['layout']] if R else None
            _SB[mp] = MetatileRenderer(R, l['primary_tileset'], l['secondary_tileset']) if l else None
        except Exception:
            _SB[mp] = None
    return _SB[mp].behavior(metatile) if _SB[mp] else None

_SG = {}
def sapphire_grid(mp):
    """Sapphire's (the version's decomp) block grid of map mp (collision = bits 10-11), or None."""
    if mp not in _SG:
        try:
            from gba import world_repo
            if 'repo' not in _SG: _SG['repo'] = world_repo()
            R = _SG['repo']
            _SG[mp] = R.layout_grid(R.map_json(mp)['layout'])[0]
        except Exception:
            _SG[mp] = None
    return _SG[mp]

_FR = {}
def frames(wd):
    if wd not in _FR: _FR[wd] = oc.frames(wd)
    return _FR[wd]

def sapphire_warps(mp):
    f = os.path.join(version.decomp(), 'data', 'maps', mp, 'map.json')
    if not os.path.exists(f): f = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', mp, 'map.json')
    if not os.path.exists(f): return []
    return [(w['x'], w['y']) for w in json.load(open(f)).get('warp_events') or []]

def coll_for(mp, wd, rd):
    for fr in frames(wd):
        if fr.group is not None and mp in fr.maps or fr.group is None and fr.name == 'main' and mp in fr.maps:
            m = fr.maps[mp]
            def solid(x, z, fr=fr):
                r = fr.rec(x, z)
                return None if r is None else bool(r[3] & 1)
            doors = {(m['ox'] + x, m['oz'] + y) for x, y in sapphire_warps(mp)}
            for z in fr.world['zones'].values():
                if mp in z.get('maps', []):
                    for d in z.get('doors', []): doors.add((int(d['x'] // 16), int(d['z'] // 16)))
            c = Coll(solid, m['ox'], m['oz'], doors, mp); c.room = False
            return c
    d = os.path.join(rd, mp)
    if version.is_emerald() and os.path.exists(os.path.join(rd, version.room_variant(mp), 'room.json')):
        d = os.path.join(rd, version.room_variant(mp))    # (emerald_rooms) the Emerald build's variant of the room
    if os.path.exists(os.path.join(d, 'room.json')):
        meta = json.load(open(os.path.join(d, 'room.json')))
        ox, oz = meta['origin']; mw = meta.get('matrix', [1, 1])[0]
        cells = {}
        top = {k: meta[k] for k in ('collision', 'collision1') if k in meta}
        for k, c in enumerate(meta.get('chunks') or [top]):
            if c is None: continue
            ci, cj = k % mw, k // mw
            for layer in ('collision', 'collision1'):     # collision1: the bridge decks (notes/CAVES.md "Walk-under
                if layer not in c: continue                # bridges"): a tile is walkable when either layer is
                per = open(os.path.join(d, c[layer]), 'rb').read()
                for i in range(1024):
                    r = struct.unpack_from('<HHHH', per, 4 + 8 * i); t = (ci * 32 + i % 32, cj * 32 + i // 32)
                    if layer == 'collision' or not (r[3] & 1): cells[t] = r
        def solid(x, z, cells=cells):
            r = cells.get((x, z))
            return None if r is None else bool(r[3] & 1)
        doors = {(ox + x, oz + y) for x, y in sapphire_warps(mp)}
        entries = set()
        exits = [s for s in meta.get('warp_spots', []) if s.get('kind') == 'exit']
        for s in meta.get('warp_spots', []):            # (x, z, w, h: zone tiles; "tiles" are Sapphire's, before the origin)
            for t in [(s['x'] + i, s['z'] + j) for i in range(s.get('w', 1)) for j in range(s.get('h', 1))]:
                doors.add(t)
                if s in exits or not exits: entries.add(t)   # (where you come in: the exit mats when the room has
                                                             #  them; the Battle Tower lobby's elevator is script-only)
        c = Coll(solid, ox, oz, doors, mp); c.room = True; c.entries = entries
        return c
    return None


# ------------------------------------------------------------------------------------------------- people
def zone_of(mp):
    Z = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    I = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    if mp in Z: return Z[mp]['zone']
    if mp in I: return I[mp]['zone']
    return None

def story_objects():
    out = []
    for f in sorted(version.overlay(os.path.join(ROOT, 'data', 'story'), '*.json')):
        for o in json.load(open(f))['objects']:
            if version.is_emerald():        # (emerald_rooms) as Emerald's build places it (at_emerald, skip_emerald ...)
                o = version.version_object(o)
                if o is None: continue
            out.append(dict(o, _file=os.path.basename(f)))
    return out

def people(mp, zone, coll, wd, objs):
    """uid -> [zone tile], uid -> script index, triggers [(script, tile)], order: the zone's NPC list as uids (the
    index ObjInitNPCGPos / h_setobjectxyperm take: the built zone's people (world.json, uid = index) or the room's
    data/interiors npcs, then the story objects in data/story file order, as patches/story.py appends them)"""
    pos, scr, trig, order = defaultdict(list), {}, [], []
    W = json.load(open(os.path.join(wd, 'world.json')))
    z = W['zones'].get(str(zone))
    if z:
        for i, n in enumerate(z.get('npcs', [])):          # (uid = index unless the world config fixes one: Littleroot)
            u = str(n.get('uid', i))
            pos[u].append((n['x'], n['z'])); order.append(u)
            if n.get('script'): scr.setdefault(n['script'], []).append(u)
        for t in z.get('triggers', []):                    # the world's step triggers (Littleroot's north exit)
            trig.append((t['script'], (t['x'], t['z']), {t['work']: t['value']} if t.get('work') else {}))
    for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), f'{zone}.json'):
        c = json.load(open(f))
        for n in c.get('npcs', []):
            if 'uid' in n and 'at' in n:
                pos[str(n['uid'])].append((n['at'][0] + coll.ox, n['at'][1] + coll.oz)); order.append(str(n['uid']))
                if n.get('script'): scr.setdefault(n['script'], []).append(str(n['uid']))
        for t in c.get('triggers', []):
            if 'at' in t: trig.append((t['script'], (t['at'][0] + coll.ox, t['at'][1] + coll.oz), {}))
    for o in objs:
        if o.get('map') != mp and not (o.get('zone') == zone and 'x' in o): continue
        if 'zone' in o and 'x' in o: t = (o['x'], o['z'])
        elif 'at' in o: t = (o['at'][0] + coll.ox, o['at'][1] + coll.oz)
        else: continue
        if o['kind'] == 'npc' and 'uid' in o:
            pos[str(o['uid'])].append(t); order.append(str(o['uid']))
            if o.get('script'): scr.setdefault(o['script'], []).append(str(o['uid']))
        elif o['kind'] == 'trigger': trig.append((o['script'], t, {o['var']: o['value']} if o.get('var') and 'value' in o else {}))
    return pos, scr, trig, order

GUARD = {'ne': lambda v, x: v == x, 'eq': lambda v, x: v != x, 'ge': lambda v, x: v < x, 'gt': lambda v, x: v <= x,
         'lt': lambda v, x: v >= x, 'le': lambda v, x: v > x}

def cdefs(txt):
    """#define NAME value / NAME(p) body of a raw script text: ({name: text}, {name: (param, body)})"""
    obj, fn = {}, {}
    for ln in txt.split('\n'):
        m = re.match(r'^\s*#define\s+(\w+)\(\s*(\w+)\s*\)\s+(.*?)\s*(?://.*|/\*.*)?$', ln)
        if m: fn[m.group(1)] = (m.group(2), m.group(3)); continue
        m = re.match(r'^\s*#define\s+(\w+)\s+([^/]+?)\s*(?://.*|/\*.*)?$', ln)
        if m: obj[m.group(1)] = m.group(2)
    return obj, fn

def ev(s, obj, fn, depth=0):
    """an argument's value: object-like and one-parameter function-like #defines expanded, then arithmetic (or None)"""
    if s is None or depth > 6: return None
    v = num(s)
    if v is not None: return v
    def call(m):
        p, body = fn[m.group(1)]
        return '(' + re.sub(r'\b' + re.escape(p) + r'\b', '(' + m.group(2) + ')', body) + ')'
    t = s
    for _ in range(4):
        t2 = re.sub(r'\b(' + '|'.join(map(re.escape, fn)) + r')\(([^()]*)\)', call, t) if fn else t
        t2 = re.sub(r'\b([A-Za-z_]\w*)\b', lambda m: '(' + obj[m.group(1)] + ')' if m.group(1) in obj else m.group(1), t2)
        if t2 == t: break
        t = t2
    return num(t)

def split_args(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == ',' and depth == 0: out.append(cur.strip()); cur = ''; continue
        cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

def init_moves(raw_files, order=(), code_text=None):
    """uid -> [(zone tile, (var, op, value) or None)] from the zone init's ObjInitNPCGPos / h_setobjectxyperm; the index
    is turned into a uid by a NAME_INDEX ('#define NAME uid' + '#define NAME_INDEX n'), else by the zone's NPC list
    order (people()); arguments may use #defines and one-parameter macros (SC_X(29), 1 + 1). The condition is the
    nearest guard before it that jumps past it (h_goto_if_<op> VAR, VALUE, LABEL with LABEL after the line): the move
    happens when GUARD[op](VAR, VALUE)."""
    defs, out = {}, defaultdict(list)
    txt = '\n'.join(open(f).read() for f in raw_files if os.path.exists(f))
    for k, v in re.findall(r'#define\s+(\w+)\s+(\d+)', txt): defs[k] = int(v)
    obj, fn = cdefs(txt)
    if code_text is not None: txt = code_text     # the preprocessed code (#if resolved: another version's lines are out)
    lines = [l.split('//')[0] for l in txt.split('\n')]
    for i, ln in enumerate(lines):
        m = re.match(r'^\s*(ObjInitNPCGPos|h_setobjectxyperm)\s+(.*)$', ln)
        if not m: continue
        a = split_args(m.group(2))
        if m.group(1) == 'ObjInitNPCGPos':
            if len(a) < 5: continue
            idx, x, z = a[0], ev(a[2], obj, fn), ev(a[4], obj, fn)
        else:
            if len(a) < 3: continue
            idx, x, z = a[0], ev(a[1], obj, fn), ev(a[2], obj, fn)
        if x is None or z is None: continue
        if idx.endswith('_INDEX') and idx[:-6] in defs: uid = str(defs[idx[:-6]])
        elif ev(idx, obj, fn) is not None:
            k = ev(idx, obj, fn)
            uid = order[k] if 0 <= k < len(order) else str(k)   # (outdoor generated people: uid = index)
        else: continue
        cond = None
        for j in range(i - 1, max(-1, i - 6), -1):
            gb = re.match(r'^\s*h_goto_if_(boy|girl)\s+(\w+)', lines[j])
            if gb:
                if any(re.match(r'^\s*' + re.escape(gb.group(2)) + r':', l) for l in lines[i + 1:i + 8]): cond = ('GENDER', 'not', gb.group(1))
                break
            g = re.match(r'^\s*h_goto_if_(ne|eq|ge|gt|lt|le)\s+(\w+)\s*,\s*(\w+)\s*,\s*(\w+)', lines[j])
            if g:
                after = any(re.match(r'^\s*' + re.escape(g.group(4)) + r':', l) for l in lines[i + 1:i + 8])
                if after: cond = (g.group(2), g.group(1), num(g.group(3)) if num(g.group(3)) is not None else defs.get(g.group(3)))
                break
            g = re.match(r'^\s*(h_goto_if_\w+|VMJumpIf)\s+.*?(\w+)\s*$', lines[j])
            if g:
                if any(re.match(r'^\s*' + re.escape(g.group(2)) + r':', l) for l in lines[i + 1:i + 8]): cond = ('?', 'unknown', None)
                break
            lab = re.match(r'^\s*(\w+):', lines[j])
            if lab:                                        # the move starts a block other code jumps to: it happens only
                jumps = re.findall(r'^\s*(h_goto\w*|h_call\w*|VMJump\w*|VMCall\w*)\s+(.*?)\b' + re.escape(lab.group(1)) +
                                   r'\s*$', txt, re.M)    # on that path (Sootopolis: Steven by the Gym after the legend)
                if len(jumps) == 1 and re.match(r'h_goto_if_(eq|ne|ge|gt|lt|le)$', jumps[0][0]):
                    v = [t.strip() for t in jumps[0][1].split(',') if t.strip()]
                    happens = {'eq': 'ne', 'ne': 'eq', 'ge': 'lt', 'lt': 'ge', 'gt': 'le', 'le': 'gt'}[jumps[0][0][10:]]
                    if len(v) == 2:                        # h_goto_if_eq VAR, n, LABEL: the move happens when VAR == n
                        cond = (v[0], happens, num(v[1]) if num(v[1]) is not None else defs.get(v[1]))
                    else: cond = ('?', 'unknown', None)
                elif jumps: cond = ('?', 'unknown', None)
                break
        out[uid].append(((x, z), cond))
    return out

def start_cands(pos, inits, known):
    """uid -> [(tile, how)] for a script start with the known var values"""
    out = {u: [(t, 'default') for t in ts] for u, ts in pos.items()}
    for u, lst in inits.items():
        for t, cond in lst:
            if cond is None: out[u] = [(t, 'init')]; continue
            var, op, val = cond
            if var == 'GENDER':
                if known.get('GENDER') != val: out[u] = [(t, f'init ({known.get("GENDER")})')]
                continue
            kn = {var_number(k): v for k, v in known.items() if k != 'GENDER'}
            if var_number(var) in kn and val is not None:
                kv = kn[var_number(var)]
                if GUARD[op](kv, val): out[u] = [(t, f'init {var}={kv}')]
            elif not any(h == 'init' or h.startswith('init ') and not h.startswith('init if') for _, h in out.get(u, [])):
                out[u] = out.get(u, []) + [(t, f'init if {var} {op}-guard {val}')]   # (a move known to happen wins)
    return out


# ------------------------------------------------------------------------------------------------- scripted warps
def all_warps(texts):
    """zone -> [(x, z, scene script or None, source)]; a MapChangeCore right after RTReserveScript n (n < 10000: the
    zone's own script; 10017 is the global arrival) runs script n on arrival, as h_warp_scene does"""
    out = defaultdict(list)
    for name, text in texts.items():
        reserved = None
        for ln in text.split('\n'):
            ln = ln.split('//')[0].strip()
            r = re.match(r'^RTReserveScript\s+(\w+)', ln)
            if r: reserved = num(r.group(1)); continue
            if re.match(r'^[A-Za-z_.][\w.]*:', ln) or ln.startswith(('VMHalt', 'VMEnd', 'h_release')): reserved = None
            m = re.match(r'^(h_warpsilent|h_warp_scene|h_warp_arrive|MapChangeCore|MapChangeWarp)\s+(.*)$', ln)
            if not m: continue
            a = [num(x) for x in m.group(2).split(',')]
            if None in a[:3]: continue
            if m.group(1) == 'MapChangeWarp':          # Black 2's own warp: zone, x, z, dir (it fades in by itself)
                zone, x, z, scene = a[0], a[1], a[2], None
            elif m.group(1) == 'MapChangeCore':
                zone, x, z = a[0], a[1], a[3]; scene = reserved if reserved is not None and reserved < 10000 else None
            else: zone, x, z = a[0], a[1], a[2]; scene = a[4] if m.group(1) == 'h_warp_scene' and len(a) > 4 else None
            reserved = None
            out[zone].append((x, z, scene, name))
    return out

_HV = {}
def var_number(name):
    """a VAR_/FLAG_ name's number from src/include/hoenn.h (or the number itself)"""
    if num(str(name)) is not None: return num(str(name))
    if not _HV:
        for f in glob.glob(os.path.join(ROOT, 'src', 'include', '*.h')):
            for k, v in re.findall(r'#define\s+(\w+)\s+(0x[0-9a-fA-F]+|\d+)', open(f).read()): _HV.setdefault(k, int(v, 0))
    return _HV.get(name)

def sets_var(text, var, value):
    """True when a (preprocessed) script text sets var to value (h_setvar / WorkSetConst)"""
    n = var_number(var)
    if n is None or value is None: return True                    # (unknown: keep the start)
    for v, x in re.findall(r'(?:h_setvar|WorkSetConst)\s+(\w+)\s*,\s*(\w+)', text):
        if var_number(v) == n and num(x) == value: return True
    return False


# ------------------------------------------------------------------------------------------------- tracing
COND = re.compile(r'^(h_goto_if_\w+|h_call_if_\w+|VMJumpIf|VMCallIf)$')
END = {'VMHalt', 'VMEnd', 'h_release', 'h_end', 'h_releaseall'}

def _ending_macros():
    """Macros of src/include whose last command ends the script (h_msgbox_npc: a whole MSGBOX_NPC script ending in
    VMHalt): the code after one is another script's, not this one's (emerald_integrate 2026-10-12: Petalburg's
    Story_WallysMom 'fell through' into the Emerald Scott scene that the build places after the Sapphire bodies)."""
    out = set()
    for f in glob.glob(os.path.join(ROOT, 'src', 'include', '*.inc')):
        name, last = None, None
        for ln in open(f, encoding='utf-8', errors='replace'):
            s = ln.split('//')[0].strip()
            m = re.match(r'\.macro\s+(\w+)', s)
            if m: name, last = m.group(1), None; continue
            if s.startswith('.endm'):
                if name and last in END: out.add(name)
                name = None; continue
            if name and re.match(r'^[\w.\\@]+:$', s): last = None          # (a label before .endm: falls through)
            elif name and s and not s.startswith('.'): last = s.split()[0].rstrip(',')
    return out
END |= _ending_macros()
WARP = {'h_warpsilent', 'h_warp_scene', 'h_warp_arrive', 'MapChangeCore', 'MapChangeWarp', 'h_warp'}

def trace(code, labels, moves, entry, starts, cands, coll, report, tag, limit=4000):
    """starts: {actor: tile} known at the start (255 = the player), vars: {name: value}; cands: uid -> [tiles]."""
    seen = set(); stack = [(labels[entry], (), tuple(sorted(starts['pos'].items())), tuple(sorted(starts['vars'].items())))]
    n = 0
    while stack and n < limit:
        pc, ret, pos, var = stack.pop(); n += 1
        key = (pc, ret, pos, var)
        if key in seen: continue
        seen.add(key)
        pos_d, var_d = dict(pos), dict(var)
        local = set(); steps_run = 0
        while pc < len(code):
            if (pc, ret) in local or steps_run > 20000: break       # a loop inside one path
            local.add((pc, ret)); steps_run += 1
            op, args, ln = code[pc]
            if op in END: break
            if op in WARP: break
            if op == 'VMReturn' or op == 'h_return':
                if not ret: break
                pc = ret[-1]; ret = ret[:-1]; continue
            if op == 'VMJump' or op == 'h_goto':
                if args[0] not in labels: break
                pc = labels[args[0]]; continue
            if op == 'VMCall' or op == 'h_call':
                if args[0] not in labels: pc += 1; continue
                ret = ret + (pc + 1,); pc = labels[args[0]]; continue
            if op in ('h_getplayerfacing', 'PlayerGetDir'):
                if 'facing' in starts: var_d[args[0]] = starts['facing']
                else: var_d.pop(args[0], None)
                pc += 1; continue
            if COND.match(op):
                tgt = args[-1]; call = 'call' in op.lower()
                take = untake = True
                if op in ('h_goto_if_boy', 'h_goto_if_girl'):
                    take = op.endswith(GENDER[0]); untake = not take
                if op in ('h_goto_if_eq', 'h_goto_if_ne', 'h_call_if_eq', 'h_call_if_ne') and args[0] in var_d and num(args[1]) is not None:
                    eq = var_d[args[0]] == num(args[1])
                    take = eq if op.endswith('eq') else not eq; untake = not take
                if tgt in labels:
                    if take:
                        if call: stack.append((labels[tgt], ret + (pc + 1,), tuple(sorted(pos_d.items())), tuple(sorted(var_d.items()))))
                        else: stack.append((labels[tgt], ret, tuple(sorted(pos_d.items())), tuple(sorted(var_d.items()))))
                    if not untake: break
                pc += 1; continue
            if op in ('h_setvar', 'WorkSetConst') and len(args) >= 2 and num(args[1]) is not None and re.match(r'^0x80[0-9a-fA-F]{2}$', args[0]):
                var_d[args[0]] = num(args[1]); pc += 1; continue
            if op == 'ActorGetGPos' and len(args) >= 3:          # ActorGetGPos uid, VX, VZ (work variables)
                a0 = str(num(args[0]) if num(args[0]) is not None else args[0])
                if pos_d.get(a0) is not None: var_d['_w_%s' % num(args[1])] = pos_d[a0][0]; var_d['_w_%s' % num(args[2])] = pos_d[a0][1]
                pc += 1; continue
            if op == 'ActorSetGPos' and len(args) >= 4 and num(args[1]) is not None:
                def val(v):                                  # a work variable (0x4000-0x40ff, 0x8000-0x80ff): its value
                    v = num(v)
                    if v is not None and (0x4000 <= v <= 0x40ff or 0x8000 <= v <= 0x80ff): return var_d.get('_w_%s' % v)
                    return v
                xx, zz = val(args[1]), val(args[3])
                a0 = str(num(args[0]) if num(args[0]) is not None else args[0])
                if xx is None or zz is None: pos_d.pop(a0, None)
                else: pos_d[a0] = (xx, zz)
                pc += 1; continue
            if op in ('h_applymovement', 'ActorCmdExec') and len(args) >= 2:
                actor = str(num(args[0]) if num(args[0]) is not None else args[0]); lab = args[1]
                steps = moves.get(lab)
                if steps:
                    if actor not in pos_d:
                        cs = cands.get(actor, [])
                        if actor != '255' and cs:
                            for c, how in cs[1:]:
                                p2 = dict(pos_d); p2[actor] = c; v2 = dict(var_d); v2['_how_' + actor] = how
                                stack.append((pc, ret, tuple(sorted(p2.items())), tuple(sorted(v2.items()))))
                            pos_d[actor] = cs[0][0]; var_d['_how_' + actor] = cs[0][1]
                    if actor in pos_d and pos_d[actor] is not None:
                        how = var_d.get('_how_' + actor, '')
                        guess = (how == 'default' and any(h != 'default' for _, h in cands.get(actor, []))
                                 or how.startswith('init if') or actor == '255' and var_d.get('_guess'))
                        pos_d[actor] = walk(actor, pos_d[actor], steps, coll, report, f'{tag} {lab}' + (f' ({how} start)' if how else ''),
                                            guess)
                pc += 1; continue
            pc += 1
    return n

def reaches_move(code, labels, entry):
    todo, seen = [labels[entry]], set()
    while todo:
        pc = todo.pop()
        while pc < len(code) and pc not in seen:
            seen.add(pc); op, args, _ = code[pc]
            if op in ('h_applymovement', 'ActorCmdExec'): return True
            if op in END or op in WARP or op in ('VMReturn', 'h_return'): break
            if args and args[-1] in labels and (op in ('VMJump', 'h_goto', 'VMCall', 'h_call') or COND.match(op)):
                todo.append(labels[args[-1]])
                if op in ('VMJump', 'h_goto'): break
            pc += 1
    return False

TRACED = set()
def walk(actor, start, steps, coll, report, where, guess=False):
    """'solid': the built world blocks a tile Sapphire lets you walk on; 'solid (Sapphire too)': Sapphire's own
    collision blocks it as well (Sapphire's scene does the same). The last step may enter a door/warp tile, or any
    tile when the list ends with set_invisible (someone walking into a door, an elevator, a submarine)."""
    p = start
    who = 'player' if actor == '255' else f'uid {actor}'
    if os.environ.get('SCENE_WALKS_TRACE'):                # every walk followed: where it starts and ends
        e = (start[0] + sum(d[0] for d in steps), start[1] + sum(d[1] for d in steps))
        TRACED.add(f'  . {where}: {who} {start}[{coll.sap(start)[0]},{coll.sap(start)[1]}] -> {e}[{coll.sap(e)[0]},{coll.sap(e)[1]}]')
    path = []
    for i, (dx, dz) in enumerate(steps):
        p = (p[0] + dx, p[1] + dz)
        s = coll.solid(*p)
        if s is None: report.add((where, who, start, p, 'outside the built zone')); return p
        path.append((p, s, coll.sap_solid(*p)))
    # Sapphire's own: someone starting on a tile Sapphire blocks (Latios in the wall, Kyogre in its pool, the submarine)
    # or a walk that ends in tiles Sapphire blocks (a Kecleon fleeing into a tree, Briney walking off into the rock).
    # A blocked stretch in the middle of a walk is reported even when Sapphire blocks it too: that is what a walk
    # started on the wrong tile looks like (Wally's tutorial through the Pokémon Center's front wall).
    flying = coll.sap_solid(*start) is True and coll.solid(*start) is True and start not in coll.doors
    for i, (q, s, ss) in enumerate(path):
        last = i == len(path) - 1
        if not s or last and (q in coll.doors or getattr(steps, 'vanish', False)): continue
        tail = all(t[2] for t in path[i:])
        own = ss and (flying or tail)
        report.add((where, who, start, q, 'solid (Sapphire too)' if own else
                    'solid (start guessed: the zone init moves this person)' if guess else
                    'solid (Sapphire blocks it too, mid-walk)' if ss else 'solid'))
    return p


# ------------------------------------------------------------------------------------------------- main
def file_map(path):
    b = os.path.basename(path)[:-2]
    m = re.match(r'^(\d+)_(auto|room|cave)_(\w+)$', b)
    if m: return m.group(3)
    return SPECIAL.get(b[:4])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default=os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'))
    ap.add_argument('--rooms', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--files', default='')
    ap.add_argument('--maps', default='')
    ap.add_argument('-v', action='store_true')
    ap.add_argument('--warps-all', action='store_true', help='preprocess every file for the scripted warps (slower)')
    ap.add_argument('--gender', default='boy', choices=['boy', 'girl'])
    a = ap.parse_args()
    GENDER[0] = a.gender
    files = sorted(f for f in glob.glob(os.path.join(FS, '*.s')) if not f.endswith('_init.s'))
    want_m = set(a.maps.split(',')) if a.maps else None
    want_f = set(a.files.split(',')) if a.files else None
    if want_m: want_f = (want_f or set()) | {os.path.basename(f)[:4] for f in files if file_map(f) in want_m}
    texts = {}
    for f in files:
        if want_f and os.path.basename(f)[:4] not in want_f and not a.warps_all: texts[f] = open(f).read(); continue
        try: texts[f] = preprocess(f)
        except Exception as e: print('preprocess failed', os.path.basename(f), str(e)[:200]); texts[f] = ''
    warps = all_warps(texts)
    objs = story_objects()
    total = same = 0
    for f in files:
        b = os.path.basename(f)
        if want_f and b[:4] not in want_f: continue
        mp = file_map(f)
        if not mp or (want_m and mp not in want_m): continue
        text = texts[f]
        if 'h_applymovement' not in text and 'ActorCmdExec' not in text: continue
        zone = zone_of(mp)
        coll = coll_for(mp, a.world, a.rooms)
        if coll is None or zone is None:
            print(f'{b}: {mp}: no built collision / zone (skipped)'); continue
        code, labels, moves, entries = parse(text)
        pos, scr, trig, order = people(mp, zone, coll, a.world, objs)
        nxt = '%04d' % (int(b[:4]) + 1)
        initf = [f] + [g for g in glob.glob(os.path.join(FS, nxt + '_*_init.s'))] + glob.glob(os.path.join(FS, 'scenes', mp + '*.inc'))
        # (the code as the build sees it: the file and its init file preprocessed, so a scene file's other-version
        # lines (#ifdef HOENN_EMERALD) do not count; the raw files only give the NAME / NAME_INDEX defines)
        init_code = [text] + [preprocess_cached(g) for g in initf[1:] if g.endswith('.s')]
        inits = init_moves(initf, order, '\n'.join(init_code))
        # OnFrame entries (MapScriptCondition in the init file / scene init): script -> (var, value)
        onframe = {}
        for g in init_code:
            for v, val, sc in re.findall(r'MapScriptCondition\s+(\w+)\s*,\s*(\w+)\s*,\s*(\w+)', g):
                if num(sc) is not None: onframe[num(sc)] = (v, num(val))
        report = set(); runs = 0
        for k, lab in enumerate(entries, 1):
            if lab not in labels or not reaches_move(code, labels, lab): continue
            starts = []
            for s, t, known in trig:
                if s == k: starts.append(dict(pos={'255': t}, vars={}, known=known, why=f'trigger {t}'))
            others = {ts[0][0] for u, ts in start_cands(pos, inits, {}).items() if ts and u not in scr.get(k, [])}
            arrival = any(sc == k for _, _, sc, _ in warps.get(zone, []))    # a scripted warp's arrival scene: nobody
            for uid in ([] if arrival else scr.get(k, [])):                   # talks to start it
                cs = start_cands(pos, inits, {}).get(uid, [])
                for npc, how in cs:
                    for (dx, dz), fdir in FACE_TO.items():
                        t = (npc[0] + dx, npc[1] + dz)
                        # (not where someone else stands, and in a room only where you can walk to from its doors
                        # without passing through anyone)
                        if coll.solid(*t) is False and t not in others and coll.reachable(t, coll.room, others | {npc}):
                            g = len(cs) > 1 and (how == 'default' or how.startswith('init if'))
                            starts.append(dict(pos={'255': t, uid: npc}, vars=dict({'_how_' + uid: how} if len(cs) > 1 else {},
                                               **({'_guess': 1} if g else {})),
                                               known={}, facing=fdir, why=f'talk to uid {uid} from {t}'))
            if k in onframe or any(sc == k for _, _, sc, _ in warps.get(zone, [])):
                known = dict([onframe[k]]) if k in onframe else {}
                for x, z, sc, src in warps.get(zone, []):
                    # a plain warp starts an OnFrame scene only when its script sets the scene's condition (the truck's
                    # warp into the house is the moving-in scene, not the TV report)
                    if sc == k or sc is None and k in onframe and sets_var(texts.get(src, ''), *onframe[k]):
                        starts.append(dict(pos={'255': (x, z)}, vars={}, known=known, why=f'warp ({x},{z}) from {os.path.basename(src)}'))
                        if coll.sap_door(x, z):           # the general cause of wally_walk's Petalburg walk
                            report.add((f'{b} #{k} {lab} [warp ({x},{z}) from {os.path.basename(src)}]', 'player', (x, z), (x, z),
                                        'lands on a Sapphire door tile: Sapphire steps the player one tile south first'))
            if not starts: starts = [dict(pos={}, vars={}, known={}, why='player unknown')]
            for st in starts:
                cands = start_cands(pos, inits, dict(st['known'], GENDER=a.gender))
                runs += trace(code, labels, moves, lab, st, cands, coll, report, f'{b} #{k} {lab} [{st["why"]}]')
        for t in sorted(TRACED): print(t)
        TRACED.clear()
        def accepted(r): return next((why for (fn, words), why in ACCEPT.items() if fn == b and words in r[4]), None)
        real = {r for r in report if (r[4] in ('solid', 'solid (Sapphire blocks it too, mid-walk)') or
                                      r[4].startswith(('outside', 'lands on'))) and not accepted(r)}
        total += len(real); same += len(report) - len(real)
        if real or a.v and report:
            print(f'== {b} ({mp}, zone {zone}): {len(real)} finding(s)'
                  f'{f" + {len(report) - len(real)} also solid in Sapphire or from a guessed start" if len(report) > len(real) else ""}, {runs} paths', flush=True)
            groups = defaultdict(list)
            for where, who, start, p, kind in sorted(report if a.v else real): groups[(where, who, start, kind)].append(p)
            for (where, who, start, kind), ps in groups.items():
                why = accepted((where, who, start, None, kind))
                print(f'  {where}: {who} from {start} [Sapphire {coll.sap(start)}] {kind}: ' +
                      ' '.join(f'{p}[{coll.sap(p)[0]},{coll.sap(p)[1]}]' for p in ps) + (f'  (accepted: {why})' if why else ''))
    print('total findings', total, f'(+ {same} steps onto tiles Sapphire blocks too or from a guessed start: -v lists them)')

if __name__ == '__main__':
    main()
