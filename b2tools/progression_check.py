"""Progression check (progression_check agent, 2026-10-08; notes/TESTING.md "Progression check"): a static story-logic
solver over the built ROM and its world, like a randomizer's logic, run on our real data. It plays the whole game from a
new game to the Hall of Fame and through the post-game without an emulator, and lists what can never be reached.

    python3 b2tools/progression_check.py ROM.nds [--world WORLD] [--dir INTERIORS] [--json OUT.json] [--flags OUT.json]
                                         [--girl] [--trace EVENT] [--all]

What it reads (the same sources as script_check.py, which it reuses): the ROM's zone headers, zone entities (people,
signs, hidden items, triggers, warps), map-script tables and field scripts (a/0/5/6, decoded with the decomp's own
tools/scripts/field_script.py), the dive table (dive.py's file in a/1/2/6), the world (WORLD/world.json, cells/*/collision.per,
alt_cells) and the built rooms and caves (INTERIORS/<Map>/room.json + collision*.per, alt_rooms).

The model:
- State: saved flags, saved works (vars), badges, the Bag's items (have / not), trainer flags, map-replacement events,
  the party's size, the Hall of Fame and National Dex marks. Flags 0-0x63 and works 0x4000-0x401F (cleared on every
  map change) and the script works 0x8000+ live only while a script runs.
- Movement (Black 2's rules as caves_check.py has them): land steps (height step < 20 units, side walls 0x51-0x58,
  ledges 0x72-0x75 one way, ice slides), Surf (badge 5 + HM03 in the Bag: hm_free.py), surf landings (hm_free's rule:
  flags without solid/surfable/NOLAND, over a shore tile 0x41/0x44), waterfalls (up: badge 8 + HM05; down: free),
  Dive and surfacing (badge 7 + HM06, dive.py's table), warps (entered walking in their direction, or standing on them;
  arrival on the destination warp or the tile you step out onto), scripted map changes (boats, ferries, cable car,
  falls, h_warp_*: the scripts' MapChangeCore / MapChangeWarp / FieldSetNextZone + CallDiving), map replacements (world
  alt_cells and room alt_rooms while their event is set: Mauville Gym, New Mauville, Shoal tides, Sky Pillar islet,
  Mirage Island, Altering Cave), people as obstacles (a person whose hide flag can be set is passable once it can),
  Strength boulders (badge 4 + HM04), Rock Smash rocks (badge 3 + TM94), Cut trees (badge 1 + HM01). One bike, no
  Acro spots (DECISIONS.md): nothing needs a bike.
- Events: talking to a person (from a tile next to it, or across a counter tile), a trainer's eye contact (its sight line),
  reading a sign / hidden item (script_check's height rule), stepping on a trigger while its work has its value, the
  zone's map scripts on every entry (init, load, conditions), item balls, reserved arrival scripts. Each script is run
  symbolically (every branch its conditions allow: flags, works, items, badges, trainer flags; unknowns such as Yes/No,
  Random, the party, the clock and the player's position take both ways) and its effects are applied.
- Two passes:
  1. may-pass ("abstract"): the set of values each flag / work / item can have grows until nothing changes; an event,
     area or item it never reaches can never be reached in the game (up to the limits below). The story blocks.
  2. play-pass ("concrete"): one realistic playthrough of an eager player from the new game (every event as soon as it
     can be done, the player's real position, Fly after badge 6, whiting out to the last Center): order problems, and
     the flags / vars / badges / items at the start of each chapter (--flags: chapter_flags.json for save making).

Limits (printed with the report): scripts read the party, the clock, Random or the player's facing (both ways taken);
movements of the player inside talk scenes are not followed (only map changes and trigger scenes); people moved by a
scene for the rest of a visit (ActorSetGPos, ActorCmdExec) count only by their flags; Strength puzzles are treated as
solvable (a boulder's tile is free with Strength) unless the separate boulder check (--boulders) says otherwise; the
may-pass treats flags and works as independent (a combination that can never happen together counts as possible).
"""
import os, sys, re, json, struct, argparse, time, itertools
from collections import defaultdict, Counter, deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import script_check as SC                     # noqa: E402  (Rom, World, the decomp's field_script)
FS = SC.FS
import version                                # noqa: E402

# ------------------------------------------------------------------------------------------------------ constants
SOLID, SURFABLE, NOLAND = 1, 2, 0x4000
WATERFALL, UNDERWATER = 0x40, 0x9C
LEDGE = {0x72: (1, 0), 0x73: (-1, 0), 0x74: (0, -1), 0x75: (0, 1)}
WALLS = {0x51: 'e', 0x52: 'w', 0x53: 'n', 0x54: 's', 0x55: 'ne', 0x56: 'nw', 0x57: 'se', 0x58: 'sw'}
ICE = {0x10, 0x18}
SHORE = {0x41, 0x44}
COUNTER = set(range(0xd0, 0xe8))              # Black 2's counter tiles (0xd4 in front of the nurse): talked across
DIRS = ((0, -1, 'n'), (0, 1, 's'), (-1, 0, 'w'), (1, 0, 'e'))
DNAME = {(0, -1): 'n', (0, 1): 's', (-1, 0): 'w', (1, 0): 'e'}
OPP = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
LAND, SURF, DIVE = 0, 1, 2
MODE = {0: 'land', 1: 'surf', 2: 'dive'}
WARP_VEC = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}    # warp dir -> the way the player walks in (CheckWarpDirectionMatch)
# field moves (b2tools/patches/hm_free.py FIELD_MOVES): machine item, badge index (gym - 1)
FIELD_MOVES = {'CUT': (420, 0), 'FLASH': (397, 1), 'ROCK_SMASH': (619, 2), 'STRENGTH': (423, 3), 'SURF': (422, 4),
               'FLY': (421, 5), 'DIVE': (425, 6), 'WATERFALL': (424, 7)}
SCRIPT_BOULDER, SCRIPT_CUT, SCRIPT_ROCK = 10000, 10004, 10016
TRAINER_FLAG0 = 1520                          # trainer id -> flag (notes/STORY_PORTING.md section 6)
TEMP_FLAGS = 0x64                              # flags 0-0x63: cleared on every map change
TEMP_WORKS = (0x4000, 0x4020)                  # works cleared on every map change
SPRITE_WORKS = (0x4020, 0x4030)                # dynamic sprite works (zone inits set them on every entry)
LOCAL_WORKS = 0x8000                           # script works
VAR0, VAREND = 0x4000, 0xC000
TOP = None                                     # any value
MAXVALS = 24                                   # a value set bigger than this becomes TOP
FLAG_GAME_CLEAR = 2400
GAME_CLEAR_GLOBAL = 9601                       # src/field_scripts/1242_global_9600.s Script_2 (game_clear.py)
DIVE_TABLE_ZONE = 241                          # dive.py: the table is the entity file of zone 241
ROAMER_START = 434                             # pg_roamer_start (roamers.py, postgame_lib.inc)
HOENN_COMMANDS = {0x1c9: 'h_flash_scale', 434: 'pg_roamer_start'}

def isvar(v): return isinstance(v, int) and VAR0 <= v < VAREND
def s16(v): return v - 0x10000 if v >= 0x8000 else v


def y_of(c, lx, lz):
    return SC.y_of(c, lx, lz)


# ------------------------------------------------------------------------------------------------------ spaces
class Space:
    """One coordinate frame the player walks in: the connected outdoor world ('main'), a warp-only outdoor group, a
    room / cave / underwater map, or one of their other layouts (map replacements). recs: {tile: (layer records)}."""
    def __init__(self, key, recs, zone_of, base=None, event=None, underwater=False, name=''):
        self.key, self.recs, self.zone_of, self.base, self.event = key, recs, zone_of, base or key, event
        self.underwater, self.name = underwater, name or str(key)
        self._y = {}

    def layers(self, t):
        return self.recs.get(t, ())

    def y(self, t, li):
        k = (t, li)
        if k not in self._y:
            r = self.recs.get(t)
            self._y[k] = y_of(r[li], t[0] % 32, t[1] % 32) if r and li < len(r) else None
        return self._y[k]

    def cell(self, t, y):
        """(layer index, record, height) at tile t for an actor at height y: the nearest layer (FieldG3DMapper_GetTerrain)."""
        r = self.recs.get(t)
        if not r: return None
        if len(r) == 1 or y is None: return 0, r[0], self.y(t, 0)
        best = None
        for li, c in enumerate(r):
            yy = self.y(t, li)
            d = abs(yy - y) if yy is not None else 1e9
            if best is None or d < best[0]: best = (d, li, c, yy)
        return best[1], best[2], best[3]


def _per(path):
    b = open(path, 'rb').read()
    return [struct.unpack_from('<HHHH', b, 4 + 8 * i) for i in range(1024)]


class Data:
    """The ROM (script_check.Rom), the world (script_check.World) and everything derived from them."""
    def __init__(self, rom, world_dir, rooms_dir):
        self.R = SC.Rom(rom)
        self.W = SC.World(world_dir, rooms_dir)
        self.wd, self.rooms_dir = world_dir, rooms_dir
        self.zones = [z for z in self.W.hoenn_zones() if z < len(self.R.hdr)]
        self.zset = set(self.zones)
        # zones that share a Hoenn zone's entities (the weather patch's ash / sandstorm / fog copies, Altering Cave's
        # daily copies): the same map under another header
        byent = {}
        for z in self.zones: byent.setdefault(self.R.hdr[z]['entities'], z)
        self.alias = {z: byent[self.R.hdr[z]['entities']] for z in range(len(self.R.hdr))
                      if z not in self.zset and self.R.hdr[z]['entities'] in byent}
        self.spaces = {}                       # key -> Space
        self.zone_spaces = defaultdict(list)   # zone -> [space keys] (base first)
        self._build_spaces()
        self.dive = self._dive_table()

    def name(self, z): return self.W.name(self.alias.get(z, z))

    def zone(self, z):
        """The Hoenn zone a zone id stands for (a weather / daily copy -> its map)."""
        return self.alias.get(z, z)

    # ---- spaces -----------------------------------------------------------------------------------------------
    def _build_spaces(self):
        W, wd = self.W.W, self.wd
        rects = W.get('zone_rects', [])
        owner = {(c['cx'], c['cz']): c['zone'] for c in W['cells']}
        def zone_main(t, rects=rects, owner=owner):
            for x0, z0, x1, z1, zz in rects:
                if x0 <= t[0] <= x1 and z0 <= t[1] <= z1: return zz
            return owner.get((t[0] // 32, t[1] // 32))
        recs = {}
        for c in W['cells']:
            for i, r in enumerate(_per(os.path.join(wd, 'cells', f"{c['cx']:02d}_{c['cz']:02d}", 'collision.per'))):
                recs[(c['cx'] * 32 + i % 32, c['cz'] * 32 + i // 32)] = (r,)
        main = Space(('main',), recs, zone_main, name='main')
        self.spaces[main.key] = main
        alts = defaultdict(dict)
        for a in W.get('alt_cells', []):
            for i, r in enumerate(_per(os.path.join(wd, 'cells', a['dir'], 'collision.per'))):
                alts[a['event']][(a['cx'] * 32 + i % 32, a['cz'] * 32 + i // 32)] = (r,)
        self.main_alts = {}
        for ev, rr in alts.items():
            sp = Space(('main', ev), rr, zone_main, base=('main',), event=ev, name=f'main (map replace {ev})')
            self.spaces[sp.key] = sp; self.main_alts[ev] = sp
        for zs, zz in W['zones'].items():
            z = int(zs)
            if z not in self.zset: continue
            g = zz.get('group')
            if not g: self.zone_spaces[z] = [('main',)] + [('main', ev) for ev in alts]
        for G in W['standalone']:
            grecs, gown = {}, {}
            for c in G['cells']:
                p = os.path.join(wd, 'cells', c['dir'], 'collision.per')
                if not os.path.exists(p): continue
                for i, r in enumerate(_per(p)):
                    t = (c['cx'] * 32 + i % 32, c['cz'] * 32 + i // 32)
                    grecs[t] = (r,); gown[t] = c['zone']
            sp = Space(('grp', G['group']), grecs, gown.get, name=G['group'])
            self.spaces[sp.key] = sp
            for z in {c['zone'] for c in G['cells']}:
                if z in self.zset: self.zone_spaces[z] = [sp.key]
        self.room_alts = {}
        uw = set()
        try:
            rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
            uw = {r['zone'] for r in rooms.values() if r.get('map_type') == 'MAP_TYPE_UNDERWATER'}
        except Exception: pass
        self.underwater = uw
        for z, (room, built, cfg) in self.W.zone_room.items():
            if z not in self.zset: continue
            sp = self._room_space(('room', z), built, z, uw)
            if sp is None: continue
            self.zone_spaces[z] = [sp.key]
            self.room_alts[z] = [a['event'] for a in cfg.get('alt_rooms', [])]
            for alt in cfg.get('alt_rooms', []):
                a = self._room_space(('room', z, alt['event']), alt['room'], z, uw, base=('room', z), event=alt['event'])
                if a is not None: self.zone_spaces[z].append(a.key)

    def _room_space(self, key, built, z, uw, base=None, event=None):
        p = os.path.join(self.rooms_dir, built, 'room.json')
        if not os.path.exists(p): return None
        meta = json.load(open(p))
        mw = meta.get('matrix', [1, 1])[0]
        chunks = meta.get('chunks') or [dict(collision=meta['collision'], collision1=meta.get('collision1'))]
        recs = {}
        for k, c in enumerate(chunks):
            if c is None: continue
            ci, cj = k % mw, k // mw
            l0 = _per(os.path.join(self.rooms_dir, built, c['collision']))
            l1 = _per(os.path.join(self.rooms_dir, built, c['collision1'])) if c.get('collision1') else None
            for i in range(1024):
                t = (ci * 32 + i % 32, cj * 32 + i // 32)
                recs[t] = (l0[i],) if l1 is None or l1[i] == l0[i] else (l0[i], l1[i])
        sp = Space(key, recs, lambda t, z=z: z, base=base, event=event, underwater=z in uw,
                   name=built + (f' (map replace {event})' if event is not None else ''))
        self.spaces[key] = sp
        return sp

    def space_of(self, z):
        """The base space key of zone z (None when it is not built)."""
        ks = self.zone_spaces.get(z)
        return ks[0] if ks else None

    # ---- the dive table (b2tools/patches/dive.py table()) -----------------------------------------------------
    def _dive_table(self):
        out = defaultdict(list)
        if DIVE_TABLE_ZONE >= len(self.R.hdr): return out
        data = self.R.ents[self.R.hdr[DIVE_TABLE_ZONE]['entities']]
        if len(data) < 2 * 616: return out
        for z in range(616):
            e = struct.unpack_from('<H', data, 2 * z)[0]
            if not e: continue
            off, n = e & ~0xF, e & 0xF
            for k in range(n):
                x0, z0, w, h, dest, ax, az, mo, fl = struct.unpack_from('<HHBBHhhHH', data, off + 16 * k)
                tiles = [(x0 + i, z0 + j) for j in range(h) for i in range(w) if data[mo + j * w + i]]
                out[z].append(dict(tiles=tiles, dest=dest, ax=ax, az=az, fixed=bool(fl & 1)))
        return out

    # ---- map scripts --------------------------------------------------------------------------------------------
    def map_table(self, z):
        """[(kind, script id)] and [('cond', work, value, script id)] of the zone's map-script table (header init file)."""
        data = self.R.scr[self.R.hdr[z]['init_scripts']] if self.R.hdr[z]['init_scripts'] < len(self.R.scr) else b''
        out, pos = [], 0
        while pos + 6 <= len(data) and (kind := FS.u16(data, pos)) != 0:
            if kind == 1:
                t = pos + 6 + FS.s32(data, pos + 2)
                while 0 <= t and t + 6 <= len(data) and FS.u16(data, t) != 0:
                    out.append(('cond', FS.u16(data, t), FS.u16(data, t + 2), FS.u16(data, t + 4))); t += 6
            else:
                out.append((kind, struct.unpack_from('<I', data, pos + 2)[0]))
            pos += 6
        return out


# ------------------------------------------------------------------------------------------------------ the tile graph
class Graph:
    """Every place the player can be: states (space, tile, layer, mode) and the moves between them, each move with the
    conditions it needs (an ability, a map replacement, a tile whose people / trigger decide). Static moves are condensed
    into strongly connected components, so one reachability pass is a walk over a few thousand nodes."""
    def __init__(self, D, dyn_tiles):
        self.D = D
        self.dyn = dyn_tiles                   # {(base space key, tile)} tiles whose passability depends on the state
        self.keys = list(D.spaces)
        self.si = {k: i for i, k in enumerate(self.keys)}
        self.sp = [D.spaces[k] for k in self.keys]
        self.states, self.sid, self.ys = [], {}, []
        for i, sp in enumerate(self.sp):
            for t, recs in sp.recs.items():
                for li, c in enumerate(recs):
                    m = self.mode_of(sp, c)
                    if m is None: continue
                    self.sid[(i, t, li)] = len(self.states)
                    self.states.append((i, t, li, m)); self.ys.append(sp.y(t, li))
        self.out = [[] for _ in self.states]   # [(dst, conds tuple)]
        for s in range(len(self.states)):
            self.out[s] = self.moves(s)
        self._condense()

    @staticmethod
    def mode_of(sp, c):
        cls, fl = c[2], c[3]
        if fl & SOLID: return None
        if cls == UNDERWATER: return DIVE if sp.underwater else None
        if cls == WATERFALL: return None
        if fl & SURFABLE: return SURF
        return LAND

    def state_at(self, si, t, y=None, mode=None):
        """The state of space si at tile t nearest to height y (None if nobody can stand there)."""
        sp = self.sp[si]
        r = sp.recs.get(t)
        if not r: return None
        cands = [self.sid[(si, t, li)] for li in range(len(r)) if (si, t, li) in self.sid]
        if mode is not None: cands = [s for s in cands if self.states[s][3] == mode] or cands
        if not cands: return None
        if y is None or len(cands) == 1: return cands[0]
        return min(cands, key=lambda s: abs((self.ys[s] if self.ys[s] is not None else 0) - y))

    def targets(self, si, t):
        """Spaces a step onto tile t of space si can land in, with the map-replacement condition: the main world's
        alternative cells while their event is (not) set; leaving an alternative layout's cells = the main world."""
        sp = self.sp[si]
        if sp.key == ('main',):
            out = []
            for ev, a in self.D.main_alts.items():
                if t in a.recs:
                    out.append((self.si[a.key], (('mr', ev, 1),)))
                    out.append((si, (('mr', ev, 0),)))
            return out or [(si, ())]
        if sp.key[0] == 'main' and len(sp.key) == 2 and t not in sp.recs:
            return [(self.si[('main',)], ())]
        return [(si, ())]

    def dyn_cond(self, si, t):
        k = (self.sp[si].base, t)
        return (('dyn',) + k,) if k in self.dyn else ()

    def moves(self, s):
        si, t, li, mode = self.states[s]
        sp = self.sp[si]
        y = self.ys[s]
        cur = sp.recs[t][li]
        out = []
        for dx, dz, d in DIRS:
            n = (t[0] + dx, t[1] + dz)
            if d in WALLS.get(cur[2], ''): continue
            for si2, mc in self.targets(si, n):
                sp2 = self.sp[si2]
                cl = sp2.cell(n, y)
                if cl is None: continue
                li2, c, cy = cl
                if OPP[d] in WALLS.get(c[2], ''): continue
                cls, fl = c[2], c[3]
                if mode == LAND:
                    if LEDGE.get(cls) == (dx, dz):
                        n2 = (n[0] + dx, n[1] + dz)
                        for si3, mc2 in self.targets(si2, n2):
                            c2 = self.sp[si3].cell(n2, y)
                            if c2 is None: continue
                            s2 = self.sid.get((si3, n2, c2[0]))
                            if s2 is not None and self.states[s2][3] == LAND:
                                out.append((s2, mc + mc2 + self.dyn_cond(si3, n2)))
                        continue
                    if fl & SOLID or cls == WATERFALL: continue
                    if cls == UNDERWATER: continue
                    s2 = self.sid.get((si2, n, li2))
                    if s2 is None: continue
                    if fl & SURFABLE:
                        out.append((s2, mc + (('cap', 'SURF'),) + self.dyn_cond(si2, n))); continue
                    if y is not None and cy is not None and abs(cy - y) >= 20: continue
                    if cls in ICE:
                        s2 = self.slide(s2, dx, dz)
                    out.append((s2, mc + self.dyn_cond(si2, n)))
                elif mode == SURF:
                    if cls == WATERFALL:
                        if (dx, dz) not in ((0, -1), (0, 1)): continue
                        q = n
                        for _ in range(16):
                            q = (q[0] + dx, q[1] + dz)
                            cq = sp2.cell(q, None)
                            if cq is None or cq[1][2] != WATERFALL: break
                        cq = sp2.cell(q, y)
                        if cq is None: continue
                        s2 = self.sid.get((si2, q, cq[0]))
                        if s2 is None or self.states[s2][3] != SURF: continue
                        out.append((s2, mc + ((('cap', 'WATERFALL'),) if dz < 0 else ()) + self.dyn_cond(si2, q)))
                        continue
                    if fl & SURFABLE and not fl & SOLID:
                        s2 = self.sid.get((si2, n, li2))
                        if s2 is not None and self.states[s2][3] == SURF:
                            if y is not None and cy is not None and abs(cy - y) >= 20: continue
                            out.append((s2, mc + self.dyn_cond(si2, n)))
                        continue
                    # landing (hm_free: CheckSurfExitEvent + SurfLandingTileType)
                    q, cq = n, (li2, c, cy)
                    if cls in SHORE:
                        q = (n[0] + dx, n[1] + dz)
                        cq = sp2.cell(q, y)
                        if cq is None: continue
                    if cq[1][3] & (SOLID | SURFABLE | NOLAND): continue
                    s2 = self.sid.get((si2, q, cq[0]))
                    if s2 is not None and self.states[s2][3] == LAND:
                        out.append((s2, mc + self.dyn_cond(si2, q)))
                elif mode == DIVE:
                    if cls != UNDERWATER or fl & SOLID: continue
                    s2 = self.sid.get((si2, n, li2))
                    if s2 is not None: out.append((s2, mc + self.dyn_cond(si2, n)))
        return out

    def slide(self, s, dx, dz):
        """Ice: the player slides on until the next tile stops them."""
        for _ in range(64):
            si, t, li, mode = self.states[s]
            c = self.sp[si].recs[t][li]
            if c[2] not in ICE: return s
            n = (t[0] + dx, t[1] + dz)
            cl = self.sp[si].cell(n, self.ys[s])
            if cl is None: return s
            li2, c2, cy = cl
            if c2[3] & (SOLID | SURFABLE) or (self.ys[s] is not None and cy is not None and abs(cy - self.ys[s]) >= 20): return s
            if (self.sp[si].base, n) in self.dyn: return s
            s2 = self.sid.get((si, n, li2))
            if s2 is None: return s
            s = s2
        return s

    # ---- condensation -------------------------------------------------------------------------------------------
    def _condense(self):
        N = len(self.states)
        index = [-1] * N; low = [0] * N; onst = [False] * N; comp = [-1] * N
        st, ncomp, counter = [], 0, 0
        static = [[d for d, c in self.out[v] if not c] for v in range(N)]
        for root in range(N):
            if index[root] != -1: continue
            work = [(root, 0)]
            while work:
                v, i = work.pop()
                if i == 0:
                    index[v] = low[v] = counter; counter += 1
                    st.append(v); onst[v] = True
                recurse = False
                ws = static[v]
                while i < len(ws):
                    w = ws[i]; i += 1
                    if index[w] == -1:
                        work.append((v, i)); work.append((w, 0)); recurse = True; break
                    elif onst[w]:
                        low[v] = min(low[v], index[w])
                if recurse: continue
                if low[v] == index[v]:
                    while True:
                        w = st.pop(); onst[w] = False; comp[w] = ncomp
                        if w == v: break
                    ncomp += 1
                if work:
                    u = work[-1][0]
                    low[u] = min(low[u], low[v])
        self.comp = comp
        self.ncomp = ncomp
        cout = [set() for _ in range(ncomp)]
        for v in range(N):
            cv = comp[v]
            for d, c in self.out[v]:
                cd = comp[d]
                if cd != cv or c: cout[cv].add((cd, c))
        self.cout = [list(x) for x in cout]
        self.members = [[] for _ in range(ncomp)]
        for v in range(N): self.members[comp[v]].append(v)

    def describe(self, s):
        si, t, li, mode = self.states[s]
        sp = self.sp[si]
        z = sp.zone_of(t)
        return f'{self.D.name(z) if z is not None else sp.name} {t}{" layer " + str(li) if li else ""}{" " + MODE[mode] if mode else ""}'


# ------------------------------------------------------------------------------------------------------ values
def V(*xs): return frozenset(xs)
ZERO, ONE, BOOL = V(0), V(1), V(0, 1)

def vs_union(a, b):
    if a is TOP or b is TOP: return TOP
    u = a | b
    return TOP if len(u) > MAXVALS else u

def vs_map(a, f):
    if a is TOP: return TOP
    out = set()
    for x in a:
        try: out.add(f(x) & 0xFFFF)
        except ZeroDivisionError: return TOP
    return TOP if len(out) > MAXVALS else frozenset(out)

def vs_has(a, v): return a is TOP or v in a

def cmp3(a, b): return 0 if a < b else 1 if a == b else 2
LUT = {0: (1, 0, 0), 1: (0, 1, 0), 2: (0, 0, 1), 3: (1, 1, 0), 4: (0, 1, 1), 5: (1, 0, 1)}   # VM_CMP_LUT[cond][cmp]
REL = {0: lambda l, r: l < r, 1: lambda l, r: l == r, 2: lambda l, r: l > r, 3: lambda l, r: l <= r,
       4: lambda l, r: l >= r, 5: lambda l, r: l != r}


def is_temp(key):
    """Keys that live only while the player stays in one map (or one script)."""
    k = key[0]
    if k == 'f': return key[1] < TEMP_FLAGS
    if k == 'w': return key[1] >= LOCAL_WORKS or TEMP_WORKS[0] <= key[1] < TEMP_WORKS[1] or SPRITE_WORKS[0] <= key[1] < SPRITE_WORKS[1]
    return False


# ------------------------------------------------------------------------------------------------------ the interpreter
class Outcome:
    __slots__ = ('writes', 'mapchange', 'reserved', 'disp', 'npcpos', 'warppos', 'end', 'battles', 'nextzone',
                 'notes', 'choices', 'moved', 'local')
    def __init__(self):
        self.writes, self.mapchange, self.reserved, self.disp, self.local = {}, None, None, (0, 0), {}
        self.npcpos, self.warppos, self.end, self.battles, self.nextzone = {}, {}, None, (), None
        self.notes, self.choices, self.moved = (), (), False


class Path:
    __slots__ = ('file', 'pc', 'frames', 'stack', 'cmp', 'over', 'origin', 'o', 'steps')
    def copy(self):
        p = Path.__new__(Path)
        p.file, p.pc, p.frames, p.stack, p.cmp = self.file, self.pc, self.frames, self.stack, self.cmp
        p.over, p.origin, p.steps = dict(self.over), dict(self.origin), self.steps
        o = Outcome.__new__(Outcome)
        for k in Outcome.__slots__: setattr(o, k, getattr(self.o, k))
        o.writes, o.npcpos, o.warppos = dict(self.o.writes), dict(self.o.npcpos), dict(self.o.warppos)
        p.o = o
        return p


class Interp:
    """Runs one script entry symbolically over a state (get(key) -> value set): every path the conditions allow.
    Returns ([Outcome], keys read)."""
    MAX_STEPS, MAX_PATHS = 60000, 400
    JOIN_AFTER = 6

    def __init__(self, D, concrete=False, gender=0):
        self.D, self.R = D, D.R
        self.concrete, self.gender = concrete, gender
        self.limits = Counter()             # things the model could not follow (reported)
        self.coverage = defaultdict(set)    # file -> pcs executed
        self._merges = {}

    def run(self, zone, sid, get, ctx=None):
        ctx = ctx or {}
        reads = set()
        def rd(key):
            if not is_temp(key): reads.add(key)
            return get(key)
        r = self.R.resolve(zone, sid)
        if r is None or r[1] is None:
            self.limits[f'script {sid} of zone {zone} resolves to nothing'] += 1
            return [], reads
        f, k, _ = r
        sf = self.R.script_file(f, zone)
        if sf is None or not 0 <= k < len(sf.entries):
            self.limits[f'script {sid} of zone {zone}: no such entry'] += 1
            return [], reads
        p = Path(); p.file, p.pc, p.frames, p.stack, p.cmp = f, sf.entries[k], (), (), None
        p.over, p.origin, p.steps = {}, {}, 0
        p.o = Outcome()
        for w, v in ctx.get('works', {}).items(): p.over[('w', w)] = V(v)
        todo, outs, seen, steps = [p], [], set(), 0
        at = Counter()                          # distinct states seen at one point of the script
        joined = {}                             # point -> the joined state explored from there (dataflow join)
        while todo:
            p = todo.pop()
            while True:
                steps += 1
                if steps > self.MAX_STEPS or len(outs) > self.MAX_PATHS:
                    self.limits[f'script {sid} of zone {zone} ({self.D.name(zone)}): too many paths (cut)'] += 1
                    p.o.end = 'cut'; outs.append(p.o); todo = []; break
                if p.pc not in self.merges(p.file, zone):
                    res = self.step(p, zone, rd, ctx)
                    if res is None: continue
                    if res == 'end':
                        p.o.local = {k[1]: v for k, v in p.over.items() if k[0] == 'f' and k[1] < TEMP_FLAGS}
                        outs.append(p.o); break
                    if res == 'dead': break
                    todo.extend(res); break
                key = (p.file, p.pc, p.frames, p.stack, p.cmp, frozenset(p.over.items()), frozenset(p.origin.items()),
                       p.o.mapchange, p.o.disp, p.o.reserved)
                if key in seen: break
                seen.add(key)
                point = (p.file, p.pc, p.frames, p.stack, p.cmp, p.o.mapchange, p.o.disp, p.o.reserved, p.o.end,
                         frozenset(p.o.npcpos.items()), frozenset(p.o.warppos.items()), p.o.nextzone)
                at[point] += 1
                if at[point] > self.JOIN_AFTER and not self.concrete:
                    j = joined.get(point)
                    if j is None: joined[point] = p.copy()
                    else:
                        q = self.join(j, p, rd)
                        if q is None: break                      # nothing new
                        joined[point] = q; p = q.copy()
                res = self.step(p, zone, rd, ctx)
                if res is None: continue            # p advanced
                if res == 'end':
                    p.o.local = {k[1]: v for k, v in p.over.items() if k[0] == 'f' and k[1] < TEMP_FLAGS}
                    outs.append(p.o); break
                if res == 'dead': break
                todo.extend(res); break             # forks
        return outs, reads

    def merges(self, f, zone):
        """Points of script file f where paths can meet (jump / call targets, return points, entries)."""
        m = self._merges.get(f)
        if m is None:
            sf = self.R.script_file(f, zone)
            m = set(sf.entries) if sf else set()
            if sf:
                for pc, (cmd, args, end) in sf.instructions.items():
                    if cmd.name in ('VMJump', 'VMCall'): m.add(args[0])
                    if cmd.name in ('VMJumpIf', 'VMCallIf'): m.add(args[1]); m.add(end)
                    if cmd.name in ('VMCall', 'VMCallIf', 'RTCallGlobal', 'RTCallGlobalAsync', 'CallGameClear'): m.add(end)
            self._merges[f] = m
        return m

    def join(self, a, b, rd):
        """The union of two paths at one point (every key's values from either), or None when b adds nothing to a."""
        q = a.copy()
        grew = False
        for key in set(a.over) | set(b.over):
            va = a.over[key] if key in a.over else self.get(a, rd, key)
            vb = b.over[key] if key in b.over else self.get(b, rd, key)
            u = vs_union(va, vb)
            if u != va: grew = True
            q.over[key] = u
            if key in a.o.writes or key in b.o.writes:
                q.o.writes[key] = u
        for v in set(a.origin) | set(b.origin):
            if a.origin.get(v) != b.origin.get(v): q.origin.pop(v, None); grew = grew or v in a.origin
        q.o.battles = tuple(sorted(set(a.o.battles) | set(b.o.battles), key=repr))
        q.o.notes = tuple(sorted(set(a.o.notes) | set(b.o.notes), key=repr))
        return q if grew else None

    # ---- helpers ----
    def get(self, p, rd, key):
        if key in p.over: return p.over[key]
        if is_temp(key):
            if key[0] == 'w' and key[1] >= LOCAL_WORKS: return ZERO
            return ZERO if self.concrete else TOP
        return rd(key)

    def put(self, p, key, vs):
        p.over[key] = vs
        if not is_temp(key): p.o.writes[key] = vs
        if key[0] == 'w': p.origin.pop(key[1], None)

    def val(self, p, rd, v):
        """Value set of an 'any' argument."""
        if isvar(v): return self.get(p, rd, ('w', v))
        return V(v)

    def one(self, vs):
        """The single value of a value set, else None."""
        if vs is TOP or len(vs) != 1: return None
        return next(iter(vs))

    def fork_on(self, p, key, true_vals, false_vals, take_true, take_false, origin_key=None):
        """Forks p into the paths a condition allows: [(path, taken)] with key refined (origin key too)."""
        out = []
        for want, vals in ((True, true_vals), (False, false_vals)):
            if vals is not TOP and not vals: continue
            q = p.copy()
            if key is not None and vals is not TOP: q.over[key] = vals
            if origin_key is not None and vals is not TOP:
                base = self.get(q, lambda k: TOP, origin_key)
                q.over[origin_key] = vals if base is TOP else (base & vals if base & vals else vals)
            out.append((q, want))
        return out

    def split(self, vs, pred):
        """(values for which pred holds, values for which it does not); TOP -> (TOP, TOP)."""
        if vs is TOP: return TOP, TOP
        t = frozenset(x for x in vs if pred(x)); f = frozenset(x for x in vs if not pred(x))
        return t, f

    # ---- one instruction ----
    def step(self, p, zone, rd, ctx):
        sf = self.R.script_file(p.file, zone)
        ins = sf.instructions.get(p.pc) if sf else None
        if ins is None:
            self.limits[f'file {p.file}: no instruction at {p.pc:#x}'] += 1
            return 'end'
        cmd, args, end = ins
        self.coverage[p.file].add(p.pc)
        nm = cmd.name
        num = cmd.id
        p.pc = end
        o = p.o
        g = lambda key: self.get(p, rd, key)
        # ---- flow
        if nm in ('VMHalt', 'RTEndGlobal'):
            return self.vm_end(p, zone)
        if nm == 'VMReturn':
            if p.frames and p.frames[-1][0] == 'call':
                fr = p.frames[-1]; p.frames = p.frames[:-1]; p.file, p.pc = fr[1], fr[2]; return None
            return self.vm_end(p, zone)
        if nm == 'VMJump': p.pc = args[0]; return None
        if nm == 'VMCall': p.frames = p.frames + (('call', p.file, end),); p.pc = args[0]; return None
        if nm in ('VMJumpIf', 'VMCallIf'):
            c, tgt = args
            if c == 0xff and nm == 'VMJumpIf':
                if not p.stack: return None
                (vs, src), p.stack = p.stack[-1], p.stack[:-1]
                # jumps when the popped value != 1
                jt, jf = self.split(vs, lambda x: x != 1)
                return self.branch_stack(p, src, jt, jf, tgt, end)
            if p.cmp is None:
                return self.take_both(p, nm, tgt, end)
            cvs, src = p.cmp
            lut = LUT.get(c)
            if lut is None: return self.take_both(p, nm, tgt, end)
            if src is not None and src[0] == 'kc':          # key vs const
                key, const, okey = src[1], src[2], src[3]
                kv = g(key)
                yes, no = self.split(kv, lambda x: lut[cmp3(x, const)] == 1)
                if kv is TOP:
                    yes = V(const) if c == 1 else TOP
                    no = V(const) if c == 5 else TOP
                outs = []
                for q, want in self.fork_on(p, key, yes, no, True, True, okey):
                    if want: self.goto(q, nm, tgt, end)
                    outs.append(q)
                return self.after_fork(p, outs)
            can_t = any(lut[x] for x in cvs) if cvs is not TOP else True
            can_f = any(not lut[x] for x in cvs) if cvs is not TOP else True
            if can_t and not can_f: self.goto(p, nm, tgt, end); return None
            if can_f and not can_t: return None
            return self.take_both(p, nm, tgt, end)
        # ---- stack
        if nm == 'VMStackPushConst': p.stack = p.stack + ((V(args[0]), ('const', args[0])),); return None
        if nm == 'VMStackPush':
            v = args[0]
            src = ('key', ('w', v), p.origin.get(v)) if isvar(v) else ('const', v)
            p.stack = p.stack + ((self.val(p, rd, v), src),); return None
        if nm == 'VMStackPushFlag':
            fl = self.flag_ids(p, rd, args[0])
            if fl is None or len(fl) != 1: p.stack = p.stack + ((BOOL, None),); return None
            key = ('f', next(iter(fl)))
            p.stack = p.stack + ((self.flagvals(g(key)), ('key', key, None)),); return None
        if nm == 'VMStackPop':
            if not p.stack: return None
            (vs, src), p.stack = p.stack[-1], p.stack[:-1]
            self.put(p, ('w', args[0]), vs); return None
        if nm == 'VMStackDiscard':
            p.stack = p.stack[:-1]; return None
        if nm == 'VMStackCmp':
            if len(p.stack) < 2: p.stack = (); p.stack = ((BOOL, None),); return None
            (rv, rs), (lv, ls) = p.stack[-1], p.stack[-2]
            p.stack = p.stack[:-2]
            op = args[0]
            if op in REL:
                f = REL[op]
                if lv is TOP or rv is TOP: res = BOOL
                else: res = frozenset(int(f(a, b)) for a in lv for b in rv)
                src = ('rel', op, ls, rs, lv, rv)
            elif op == 6:
                res = BOOL if lv is TOP or rv is TOP else frozenset(int(a == 1 or b == 1) for a in lv for b in rv); src = None
            elif op == 7:
                res = BOOL if lv is TOP or rv is TOP else frozenset(int(a == 1 and b == 1) for a in lv for b in rv); src = None
            else: res, src = ZERO, None
            p.stack = p.stack + ((res, src),); return None
        if nm == 'WorkCmpConst':
            v, c = args
            kv = g(('w', v))
            p.cmp = (TOP if kv is TOP else frozenset(cmp3(x, c) for x in kv), ('kc', ('w', v), c, p.origin.get(v)))
            return None
        if nm == 'WorkCmpWork':
            a, b = g(('w', args[0])), g(('w', args[1]))
            if a is TOP or b is TOP: p.cmp = (TOP, None)
            elif len(b) == 1:
                p.cmp = (frozenset(cmp3(x, y) for x in a for y in b), ('kc', ('w', args[0]), next(iter(b)), p.origin.get(args[0])))
            else: p.cmp = (frozenset(cmp3(x, y) for x in a for y in b), None)
            return None
        # ---- flags and works
        if nm in ('FlagSet', 'FlagReset'):
            fl = self.flag_ids(p, rd, args[0])
            if fl is None: self.limits[f'{nm} of an unknown flag (zone {zone})'] += 1; return None
            for f in fl: self.put(p, ('f', f), ONE if nm == 'FlagSet' else ZERO)
            return None
        if nm == 'FlagGet':
            fl = self.flag_ids(p, rd, args[0])
            if fl is None or len(fl) != 1: self.put(p, ('w', args[1]), BOOL); return None
            key = ('f', next(iter(fl)))
            self.put(p, ('w', args[1]), self.flagvals(g(key))); p.origin[args[1]] = key; return None
        if nm == 'WorkSetConst': self.put(p, ('w', args[0]), V(args[1])); return None
        if nm in ('WorkSet', 'WorkGet'):
            src = args[1]
            self.put(p, ('w', args[0]), self.val(p, rd, src))
            if isvar(src) and src in p.origin: p.origin[args[0]] = p.origin[src]
            elif isvar(src) and not is_temp(('w', src)): p.origin[args[0]] = ('w', src)
            return None
        if nm in ('WorkAdd', 'WorkSub', 'WorkMul', 'WorkDiv', 'WorkMod', 'WorkAnd', 'WorkOr'):
            a, b = g(('w', args[0])), self.val(p, rd, args[1])
            if a is TOP or b is TOP or len(b) != 1: self.put(p, ('w', args[0]), TOP); return None
            k = next(iter(b))
            f = {'WorkAdd': lambda x: x + k, 'WorkSub': lambda x: x - k, 'WorkMul': lambda x: x * k,
                 'WorkDiv': lambda x: x // k, 'WorkMod': lambda x: x % k, 'WorkAnd': lambda x: x & k,
                 'WorkOr': lambda x: x | k}[nm]
            self.put(p, ('w', args[0]), vs_map(a, f)); return None
        # ---- items, badges, trainers, map replacement
        if nm in ('ItemAdd', 'ItemSub', 'ItemCheckSpace', 'ItemCheckAmount', 'ItemGetCount', 'ItemIsTMHM'):
            items = self.val(p, rd, args[0])
            outv = args[-1]
            if items is TOP:
                self.limits[f'{nm} of an unknown item (zone {zone})'] += 1
                self.put(p, ('w', outv), BOOL if nm != 'ItemGetCount' else TOP); return None
            if nm == 'ItemAdd':
                for it in items: self.put(p, ('i', it), ONE)
                self.put(p, ('w', outv), ONE); return None
            if nm == 'ItemSub':
                for it in items: self.put(p, ('i', it), ZERO)
                self.put(p, ('w', outv), ONE); return None
            if nm == 'ItemCheckSpace': self.put(p, ('w', outv), ONE); return None
            if nm == 'ItemIsTMHM':
                self.put(p, ('w', outv), frozenset(int(328 <= it <= 427 or 618 <= it <= 620) for it in items)); return None
            if len(items) != 1:
                self.put(p, ('w', outv), BOOL); return None
            key = ('i', next(iter(items)))
            self.put(p, ('w', outv), self.flagvals(g(key))); p.origin[outv] = key; return None
        if nm == 'TrainerFlagSet' or nm == 'TrainerFlagReset':
            for t in self.ids(p, rd, args[0], nm, zone): self.put(p, ('f', TRAINER_FLAG0 + t), ONE if nm == 'TrainerFlagSet' else ZERO)
            return None
        if nm == 'TrainerFlagGet':
            ts = self.ids(p, rd, args[0], nm, zone)
            if len(ts) != 1: self.put(p, ('w', args[1]), BOOL); return None
            key = ('f', TRAINER_FLAG0 + ts[0])
            self.put(p, ('w', args[1]), self.flagvals(g(key))); p.origin[args[1]] = key; return None
        if nm == 'TrainerCardAddBadge':
            for b in self.ids(p, rd, args[0], nm, zone): self.put(p, ('b', b), ONE)
            return None
        if nm == 'TrainerCardHasBadge':
            bs = self.ids(p, rd, args[1], nm, zone)
            if len(bs) != 1: self.put(p, ('w', args[0]), BOOL); return None
            key = ('b', bs[0])
            self.put(p, ('w', args[0]), self.flagvals(g(key))); p.origin[args[0]] = key; return None
        if nm == 'MapReplaceSetEvent':
            for u in self.ids(p, rd, args[0], nm, zone):
                sv = self.val(p, rd, args[1])
                self.put(p, ('mr', u), BOOL if sv is TOP else frozenset(int(x != 0) for x in sv))
            return None
        if nm == 'MapReplaceIsEventSet':
            us = self.ids(p, rd, args[0], nm, zone)
            if len(us) != 1: self.put(p, ('w', args[1]), BOOL); return None
            key = ('mr', us[0])
            self.put(p, ('w', args[1]), self.flagvals(g(key))); p.origin[args[1]] = key; return None
        if nm == 'TrainerCardGetSex':
            self.put(p, ('w', args[0]), V(self.gender) if self.concrete else BOOL); return None
        # ---- battles
        if nm == 'CallTrainerBattle':
            o.battles = o.battles + (tuple(self.one(self.val(p, rd, a)) for a in args[:2]),); return None
        if nm in ('TrainerBattleIsVictory', 'WildBattleIsVictory'):
            self.put(p, ('w', args[0]), ONE if self.concrete else BOOL); return None
        if nm == 'WildBattleGetResult': self.put(p, ('w', args[0]), V(0, 1, 2)); return None
        if nm in ('CallTrainerLose', 'CallWildLose'):
            o.end = 'lose'; return 'end'
        # ---- party, Pokédex, game clear
        if nm in ('PokePartyAdd', 'PokePartyAddEx', 'PokePartyAddEgg'):
            pc = g(('party',))
            self.put(p, ('party',), vs_map(pc, lambda x: min(6, x + 1)))
            self.put(p, ('w', args[0]), BOOL if not self.concrete else ONE); return None
        if nm == 'PokePartyGetCount':
            pc = g(('party',))
            self.put(p, ('w', args[0]), pc); p.origin[args[0]] = ('party',); return None
        if nm == 'PokeDexGiveNational': self.put(p, ('natdex',), ONE); return None
        if nm == 'PokeDexHaveNational':
            self.put(p, ('w', args[0]), self.flagvals(g(('natdex',)))); p.origin[args[0]] = ('natdex',); return None
        if nm == 'CallGameClear':
            self.put(p, ('hof',), ONE); self.put(p, ('f', 0x9f8), ONE)
            o.notes = o.notes + ('game clear',)
            # global 9601 (game_clear.py): FLAG_SYS_GAME_CLEAR, respawn, the place Continue loads
            p.frames = p.frames + (('global', p.file, end, 'halt'),)
            return self.call_global(p, zone, GAME_CLEAR_GLOBAL, end)
        if nm == 'YesNoWin': self.put(p, ('w', args[0]), BOOL); return None
        if nm == 'Random':
            n = self.one(self.val(p, rd, args[1]))
            self.put(p, ('w', args[0]), frozenset(range(n)) if n and n <= MAXVALS else TOP); return None
        if nm == 'PlayerGetDir': self.put(p, ('w', args[0]), V(0, 1, 2, 3)); return None
        if nm == 'PlayerGetGPos':
            pt = ctx.get('player')
            if pt is not None and o.disp == (0, 0) and not o.moved:
                self.put(p, ('w', args[0]), V(pt[0])); self.put(p, ('w', args[1]), V(pt[1]))
            elif pt is not None and not o.moved:
                self.put(p, ('w', args[0]), V(pt[0] + o.disp[0])); self.put(p, ('w', args[1]), V(pt[1] + o.disp[1]))
            else:
                self.put(p, ('w', args[0]), TOP); self.put(p, ('w', args[1]), TOP)
            return None
        # ---- warps and map changes
        if nm == 'MapChangeCore':
            vs = [self.one(self.val(p, rd, a)) for a in args]
            o.mapchange = ('xy', vs[0], vs[1], vs[3], vs[2]); return None
        if nm == 'MapChangeWarp':
            vs = [self.one(self.val(p, rd, a)) for a in args]
            o.mapchange = ('xy', vs[0], vs[1], vs[2], None); return None
        if nm == 'FieldSetNextZone':
            vs = [self.one(self.val(p, rd, a)) for a in args]
            o.nextzone = ('xy', vs[0], vs[2], vs[4], vs[3]); return None
        if nm == 'CallDiving':
            if o.nextzone: o.mapchange = o.nextzone
            return None
        if nm == 'RTReserveScript': o.reserved = self.one(self.val(p, rd, args[0])); return None
        if nm in ('RTCallGlobal', 'RTCallGlobalAsync'):
            sid = self.one(self.val(p, rd, args[0]))
            if sid is None: self.limits['RTCallGlobal of an unknown script'] += 1; return None
            return self.call_global(p, zone, sid, end)
        if nm == 'ObjInitNPCGPos':
            idx, x, zz = (self.one(self.val(p, rd, args[i])) for i in (0, 2, 4))
            if None in (idx, x, zz): self.limits[f'ObjInitNPCGPos with works (zone {zone})'] += 1
            else: o.npcpos[idx] = (x, zz)
            return None
        if nm == 'ObjInitWarpGPos':
            idx, x, zz = (self.one(self.val(p, rd, args[i])) for i in (0, 1, 3))
            if None in (idx, x, zz): self.limits[f'ObjInitWarpGPos with works (zone {zone})'] += 1
            else: o.warppos[idx] = (x, zz)
            return None
        if nm == 'ActorCmdExec':
            a = self.one(self.val(p, rd, args[0]))
            if a == 255:
                dx, dz = self.movement(sf, args[1])
                o.disp = (o.disp[0] + dx, o.disp[1] + dz)
            return None
        if nm == 'ActorSetGPos':
            a = self.one(self.val(p, rd, args[0]))
            if a == 255: o.moved = True
            return None
        if nm == 'ActorGetSpawnFlag':
            a = self.one(self.val(p, rd, args[0]))
            npc = None
            ents = self.R.entities(zone)['npcs']
            if a is not None and a != 0: npc = next((n for n in ents if n['uid'] == a), None)
            if npc is None: npc = ctx.get('npc')
            self.put(p, ('w', args[1]), V(npc['flag']) if npc else TOP); return None
        if nm == 'FieldSetTeleportZone':
            o.notes = o.notes + (('respawn', self.one(self.val(p, rd, args[0]))),); return None
        if num == ROAMER_START:
            k = self.one(self.val(p, rd, args[0]))
            if k is not None: self.put(p, ('roam', k), ONE)
            return None
        # ---- anything else: works it writes become unknown (script works only)
        # (a menu, a party / Pokédex / clock query ...: any script work it names may come back with any value)
        if nm in ('ListMenuInitCommon', 'ListMenu_AnchorTopLeft', 'ListMenu_AnchorTopRight'):   # (the choice's work)
            if isvar(args[4]): p.over[('w', args[4])] = TOP; p.origin.pop(args[4], None)
            return None
        for kind, a in zip(cmd.kinds, args):
            if isvar(a) and kind == 'var':
                if a >= LOCAL_WORKS or TEMP_WORKS[0] <= a < TEMP_WORKS[1]: p.over[('w', a)] = TOP; p.origin.pop(a, None)
                else: self.limits[f'{nm} with saved work {a:#x} (not followed)'] += 1
        return None

    def flagvals(self, vs):
        if vs is TOP: return BOOL
        return frozenset(1 if x else 0 for x in vs)

    def flag_ids(self, p, rd, a):
        if isvar(a):
            vs = self.get(p, rd, ('w', a))
            return None if vs is TOP else vs
        return V(a)

    def ids(self, p, rd, a, nm, zone):
        vs = self.val(p, rd, a)
        if vs is TOP: self.limits[f'{nm} with an unknown argument (zone {zone})'] += 1; return []
        return sorted(vs)

    def goto(self, p, nm, tgt, end):
        if nm == 'VMCallIf': p.frames = p.frames + (('call', p.file, end),)
        p.pc = tgt

    def take_both(self, p, nm, tgt, end):
        q = p.copy(); self.goto(q, nm, tgt, end)
        p.o.choices = p.o.choices + ((p.file, end, 0),); q.o.choices = q.o.choices + ((p.file, end, 1),)
        return [p, q]

    def after_fork(self, p, outs):
        if len(outs) == 1:
            q = outs[0]
            p.pc, p.frames, p.over, p.origin = q.pc, q.frames, q.over, q.origin
            return None
        return outs

    def branch_stack(self, p, src, jt, jf, tgt, end):
        """VMJumpIf CMP_STACK: jt = values that jump. Refines the flag / work behind a simple comparison."""
        can_j = jt is TOP or bool(jt); can_n = jf is TOP or bool(jf)
        if can_j and not can_n: p.pc = tgt; return None
        if can_n and not can_j: return None
        outs = []
        for jump in (False, True):
            q = p.copy()
            if jump: q.pc = tgt
            self.refine_rel(q, src, want=not jump)
            outs.append(q)
        return outs

    def refine_rel(self, q, src, want):
        """The comparison src (VMStackCmp of a key and a constant) is `want` on this path: narrow the key (and the
        saved key a script work was read from)."""
        if not src or src[0] != 'rel': return
        op, ls, rs, lv, rv = src[1:]
        f = REL[op]
        for side, other, cur, flip in ((ls, rs, lv, False), (rs, ls, rv, True)):
            if not side or side[0] != 'key' or not other or other[0] != 'const': continue
            key, okey = side[1], side[2]
            c = other[1]
            test = (lambda x: f(c, x)) if flip else (lambda x: f(x, c))
            if cur is TOP:
                if op == 1 and want or op == 5 and not want: sub = V(c)
                else: continue
            else:
                sub = frozenset(x for x in cur if bool(test(x)) == want)
            if not sub: continue
            q.over[key] = sub
            if okey is not None: q.over[okey] = sub

    def call_global(self, p, zone, sid, ret):
        if 3000 <= sid < 7000:                        # a trainer's eye-contact script: the battle and its flag
            t = sid - 3000 if sid < 5000 else sid - 5000
            self.put(p, ('f', TRAINER_FLAG0 + t), ONE); return None
        r = self.R.resolve(zone, sid)
        if r is None or r[1] is None:
            self.limits[f'call of script {sid}: resolves to nothing'] += 1; return None
        sf = self.R.script_file(r[0], zone)
        if sf is None or not 0 <= r[1] < len(sf.entries):
            self.limits[f'call of script {sid}: no entry'] += 1; return None
        if not p.frames or p.frames[-1][:3] != ('global', p.file, ret):
            p.frames = p.frames + (('global', p.file, ret),)
        p.file, p.pc = r[0], sf.entries[r[1]]
        return None

    def vm_end(self, p, zone):
        """VMHalt / RTEndGlobal / VMReturn at the top: back to the caller of a global script, else the end."""
        fr = p.frames
        while fr and fr[-1][0] != 'global': fr = fr[:-1]
        if not fr: return 'end'
        top = fr[-1]
        p.frames = fr[:-1]
        if len(top) > 3 and top[3] == 'halt': return 'end'     # CallGameClear: the script ends after it
        p.file, p.pc = top[1], top[2]
        return None

    def movement(self, sf, start):
        """(dx, dz) a movement list moves its actor."""
        data = sf.data
        pos, dx, dz = start, 0, 0
        while pos + 4 <= len(data):
            code, count = struct.unpack_from('<HH', data, pos); pos += 4
            if code == FS.MOVEMENT_END: break
            if code in SC.MOVES:
                mx, mz, tiles, kind = SC.MOVES[code]
                dx += mx * tiles * count; dz += mz * tiles * count
        return dx, dz


# ------------------------------------------------------------------------------------------------------ events
class Event:
    __slots__ = ('key', 'kind', 'zone', 'idx', 'sid', 'ctx', 'inter', 'what', 'flag', 'work', 'value', 'tiles', 'label')
    def __init__(self, key, kind, zone, idx, sid, what, ctx=None):
        self.key, self.kind, self.zone, self.idx, self.sid, self.what = key, kind, zone, idx, sid, what
        self.ctx, self.inter, self.flag, self.work, self.value, self.tiles, self.label = ctx or {}, {}, 0, 0, 0, (), ''


class World:
    """Events, warps, dives and the tiles whose passability depends on the state, over the tile graph."""
    def __init__(self, D):
        self.D, self.R = D, D.R
        self.events = {}
        self.npc_pos = {}                      # (zone, idx) -> [tiles it can stand on] (home first)
        self.warp_pos = {}                     # (zone, idx) -> [tiles]
        self.dyn = defaultdict(list)           # (base space, tile) -> [('npc', z, i) | ('trig', z, i)]
        self._scan_positions()
        self.local_flags = defaultdict(set)    # zone -> map-local flags its people hide by
        for z in D.zones:
            for n in self.R.entities(z)['npcs']:
                if 0 < n['flag'] < TEMP_FLAGS: self.local_flags[z].add(n['flag'])
        self._dyn_tiles()
        self.G = Graph(D, set(self.dyn))
        self.comp_zones = [set() for _ in range(self.G.ncomp)]
        for s, (si, t, li, m) in enumerate(self.G.states):
            z = self.G.sp[si].zone_of(t)
            if z is not None: self.comp_zones[self.G.comp[s]].add(z)
        self._events()
        self.inits = defaultdict(list)          # zone -> its zone-init map scripts (kind 2)
        for k, ev in self.events.items():
            if k[0] == 'map' and k[2] == 2: self.inits[k[1]].append(ev)
        self._portals()

    # ---- where people and warps can be ---------------------------------------------------------------------------
    def _scan_positions(self):
        R = self.R
        moved_npc, moved_warp = defaultdict(set), defaultdict(set)
        for z in self.D.zones:
            for fno in {R.hdr[z]['scripts'], R.hdr[z]['init_scripts']}:
                sf = R.script_file(fno, z)
                if sf is None: continue
                for pc, (cmd, args, end) in sf.instructions.items():
                    if cmd.name == 'ObjInitNPCGPos' and not any(isvar(a) for a in (args[0], args[2], args[4])):
                        moved_npc[(z, args[0])].add((args[2], args[4]))
                    if cmd.name == 'ObjInitWarpGPos' and not any(isvar(a) for a in (args[0], args[1], args[3])):
                        moved_warp[(z, args[0])].add((args[1], args[3]))
        self.moved_npc, self.moved_warp = moved_npc, moved_warp
        for z in self.D.zones:
            e = R.entities(z)
            for i, n in enumerate(e['npcs']):
                self.npc_pos[(z, i)] = [(n['x'], n['z'])] + sorted(moved_npc.get((z, i), set()) - {(n['x'], n['z'])})
            for i, w in enumerate(e['warps']):
                self.warp_pos[(z, i)] = [(w['tile_x'], w['tile_z'])] + sorted(moved_warp.get((z, i), set()) - {(w['tile_x'], w['tile_z'])})

    def npc_kind(self, n):
        """'trainer', 'boulder', 'cut', 'rock', 'wander' (never in the way), 'person'."""
        if n['evtype'] == 1: return 'trainer'
        s = n['script']
        if s == SCRIPT_BOULDER: return 'boulder'
        if s == SCRIPT_CUT: return 'cut'
        if s == SCRIPT_ROCK: return 'rock'
        if n['move'] in (3, 4, 5) and (n['areaw'] or n['areah']): return 'wander'
        if 20 <= n['move'] <= 44 and (n['areaw'] or n['areah']): return 'wander'   # walks a fixed path (move_codes.py)
        return 'person'

    def _dyn_tiles(self):
        for z in self.D.zones:
            base = self.D.space_of(z)
            if base is None: continue
            e = self.R.entities(z)
            for i, n in enumerate(e['npcs']):
                if self.npc_kind(n) == 'wander': continue
                for t in self.npc_pos[(z, i)]: self.dyn[(base, t)].append(('npc', z, i))
            for i, tr in enumerate(e['triggers']):
                if tr['w'] >= 0x100: continue
                for a in range(max(1, tr['w'])):
                    for b in range(max(1, tr['h'])):
                        self.dyn[(base, (tr['x'] + a, tr['z'] + b))].append(('trig', z, i))

    # ---- states around things -------------------------------------------------------------------------------------
    def states_on(self, z, t, mode=None):
        G = self.G
        out = []
        for key in self.D.zone_spaces.get(z, []):
            si = G.si[key]
            sp = G.sp[si]
            if t not in sp.recs: continue
            if sp.key[0] == 'main' and sp.zone_of(t) != z: continue
            for li in range(len(sp.recs[t])):
                s = G.sid.get((si, t, li))
                if s is not None and (mode is None or G.states[s][3] == mode): out.append(s)
        return out

    def _events(self):
        D, R, G = self.D, self.R, self.G
        for z in D.zones:
            base = D.space_of(z)
            if base is None: continue
            e = R.entities(z)
            nm = D.name(z)
            for i, n in enumerate(e['npcs']):
                k = self.npc_kind(n)
                if k in ('boulder', 'cut', 'rock') or not n['script']: continue
                kind = 'trainer' if k == 'trainer' else 'npc'
                ev = Event((kind, z, i), kind, z, i, n['script'], f"{nm}: {'trainer' if kind == 'trainer' else 'person'} {i} uid {n['uid']} (script {n['script']}, sprite {n['model']}) at {(n['x'], n['z'])}",
                           ctx=dict(npc=n))
                ev.flag = n['flag']
                for t in self.npc_pos[(z, i)]:
                    st = set()
                    for dx, dz, d in DIRS:
                        q = (t[0] + dx, t[1] + dz)
                        st.update(self.states_on(z, q))
                        if kind == 'npc' and not self.states_on(z, q):     # across a counter
                            if any(c[2] in COUNTER for key in D.zone_spaces.get(z, []) for c in D.spaces[key].layers(q)):
                                st.update(self.states_on(z, (q[0] + dx, q[1] + dz)))
                        if kind == 'trainer':
                            for k2 in range(2, max(1, n['p0']) + 1):
                                q2 = (t[0] + dx * k2, t[1] + dz * k2)
                                s2 = self.states_on(z, q2)
                                if not s2: break
                                st.update(s2)
                    ev.inter[t] = st
                self.events[ev.key] = ev
            for i, sg in enumerate(e['signs']):
                if not sg['script']: continue
                t = (sg['x'], sg['z'])
                ev = Event(('sign', z, i), 'sign', z, i, sg['script'],
                           f"{nm}: {'hidden item' if sg['cond'] == 2 else 'sign'} {i} (script {sg['script']}) at {t}")
                sides = [(0, 1)] if sg['dir'] == 0 else [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
                st = set()
                for dx, dz in sides:
                    for s in self.states_on(z, (t[0] + dx, t[1] + dz)):
                        h = G.ys[s]
                        if h is None or -2 <= s16(sg['y']) - h < 2 or (dx, dz) == (0, 0) and G.states[s][3] != LAND:
                            st.add(s)
                ev.inter[t] = st
                self.events[ev.key] = ev
            for i, tr in enumerate(e['triggers']):
                if tr['w'] >= 0x100 or not tr['script']: continue
                y = tr['y'] - 0x10000 if tr['y'] >= 0x8000 else tr['y']
                tiles = [(tr['x'] + a, tr['z'] + b) for a in range(max(1, tr['w'])) for b in range(max(1, tr['h']))]
                ev = Event(('trig', z, i), 'trig', z, i, tr['script'],
                           f"{nm}: trigger {i} (script {tr['script']}, work {tr['work']:#x}=={tr['value']}) at {tiles[0]}{' ' + str(tr['w']) + 'x' + str(tr['h']) if len(tiles) > 1 else ''}")
                ev.work, ev.value, ev.tiles = tr['work'], tr['value'], tiles
                for t in tiles:
                    ev.inter[t] = {s for s in self.states_on(z, t) if G.ys[s] is None or -2 <= G.ys[s] - y < 2}
                self.events[ev.key] = ev
            for ms in D.map_table(z):
                if ms[0] == 'cond':
                    _, w, v, sid = ms
                    ev = Event(('cond', z, w, v, sid), 'cond', z, None, sid, f'{nm}: map script condition {w:#x}=={v} (script {sid})')
                    ev.work, ev.value = w, v
                else:
                    kind, sid = ms
                    ev = Event(('map', z, kind, sid), 'map', z, None, sid, f'{nm}: map script {kind} (script {sid})')
                self.events[ev.key] = ev

    # ---- warps and dives -------------------------------------------------------------------------------------------
    def arrival_states(self, z, t, y=None, dirv=None, warp_type=None):
        """States the player can be in right after landing on tile t of zone z (y: the arrival height, units)."""
        on = self.states_on(z, t)
        if on:
            if y is None or len(on) == 1: return on
            return [min(on, key=lambda s: abs((self.G.ys[s] or 0) - y))]
        outs = []
        if dirv:
            q = (t[0] - dirv[0], t[1] - dirv[1])
            outs = self.states_on(z, q)
        if not outs:
            for dx, dz, d in DIRS:
                outs += self.states_on(z, (t[0] + dx, t[1] + dz))
        if y is not None and outs:
            best = min(abs((self.G.ys[s] or 0) - y) for s in outs)
            outs = [s for s in outs if abs((self.G.ys[s] or 0) - y) <= best + 4]
        return outs

    def warp_arrival(self, dz, dw, from_zone=None):
        R = self.R
        dz = self.D.zone(dz)
        if dz >= len(R.hdr) or dz not in self.D.zset: return []
        ws = R.entities(dz)['warps']
        if dw == 0x100:          # (Black 2: back where you came from) any warp of dz back to the zone we came from
            out = []
            for i, w in enumerate(ws):
                if self.D.zone(w['dest_zone']) == from_zone: out += self.warp_arrival(dz, i)
            return out
        if dw >= len(ws): return []
        w = ws[dw]
        out = []
        tiles = [(w['tile_x'] + a, w['tile_z'] + b) for a in range(max(1, w['w'])) for b in range(max(1, w['h']))]
        for t in tiles:
            out += self.arrival_states(dz, t, s16(w['y']), WARP_VEC.get(w['dir']), w['type'])
        return sorted(set(out))

    def variant_atom(self, s):
        """(('var', state),) when state s is in another layout (map replacement) or under one: it exists only while its
        map-replacement events say so."""
        si, t, li, m = self.G.states[s]
        key = self.G.keys[si]
        if len(key) > 1 and key[0] == 'room' and (len(key) == 3 or self.D.room_alts.get(key[1])): return (('var', s),)
        if key[0] == 'main' and (len(key) == 2 or any(t in a.recs for a in self.D.main_alts.values())): return (('var', s),)
        return ()

    def _portals(self):
        """Warps (conditional on their position), dives and surfacings: extra edges of the component graph."""
        G, R = self.G, self.R
        self.portal_edges = defaultdict(set)    # comp -> {(comp, conds)}
        self.warp_info = {}                      # (z, i, k) -> (entry states, arrival states)
        for z in self.D.zones:
            if self.D.space_of(z) is None: continue
            for i, w in enumerate(R.entities(z)['warps']):
                arr = self.warp_arrival(w['dest_zone'], w['dest_warp'], z)
                v = WARP_VEC.get(w['dir'])
                for k, p in enumerate(self.warp_pos[(z, i)]):
                    tiles = [(p[0] + a, p[1] + b) for a in range(max(1, w['w'])) for b in range(max(1, w['h']))]
                    ent = set()
                    for t in tiles:
                        cands = self.states_on(z, t)
                        if v: cands += self.states_on(z, (t[0] - v[0], t[1] - v[1]))
                        else:
                            for dx, dz, d in DIRS: cands += self.states_on(z, (t[0] + dx, t[1] + dz))
                        ent.update(s for s in cands if G.ys[s] is None or abs(G.ys[s] - s16(w['y'])) <= 4)
                    self.warp_info[(z, i, k)] = (ent, arr)
                    for s in ent:
                        for a in arr:
                            self.portal_edges[G.comp[s]].add((G.comp[a], (('warp', z, i, k),) + self.variant_atom(a)))
        self.dive_info = []
        for z, recs in self.D.dive.items():
            if z not in self.D.zset: continue
            under = z in self.D.underwater
            for r in recs:
                for t in r['tiles']:
                    src = self.states_on(z, t, DIVE if under else SURF)
                    if not src: continue
                    dt = (r['ax'], r['az']) if r['fixed'] else (t[0] + r['ax'], t[1] + r['az'])
                    dst = self.arrival_states(self.D.zone(r['dest']), dt)
                    self.dive_info.append((z, t, r['dest'], dt, src, dst))
                    for s in src:
                        for a in dst:
                            self.portal_edges[G.comp[s]].add((G.comp[a], (('cap', 'DIVE'),) + self.variant_atom(a)))


# ------------------------------------------------------------------------------------------------------ the state
class State:
    """Flags, works, items ... -> value sets. may=True: every value each key can have so far (the may-pass); else one
    value per key (the play-pass)."""
    def __init__(self):
        self.vals = {}
        self.npc_pos = {}                     # (zone, idx) -> frozenset of tiles (only zones whose init moved them)
        self.warp_pos = {}
        self.version = 0

    def get(self, key):
        return self.vals.get(key, ZERO)


class View:
    """What the state allows on the map: abilities, people, triggers, warps, map replacements ('may' semantics on a
    may-state: something passes when it CAN pass)."""
    def __init__(self, Wd, st, trig_pass=None, zinit=None):
        self.Wd, self.st = Wd, st
        self.trig_pass = trig_pass               # (trigger event, tile) -> the player stays on the tile after its script
        self.zinit = zinit                       # zone -> its init's Outcome on this state (play-pass), else st's unions
        g = st.get
        self.cap = {}
        for m, (item, badge) in FIELD_MOVES.items():
            self.cap[m] = vs_has(g(('b', badge)), 1) and vs_has(g(('i', item)), 1)
        self._dyn = {}

    def npc_tiles(self, z, i):
        if self.zinit is not None:
            if (z, i) not in self.Wd.moved_npc: return frozenset(self.Wd.npc_pos[(z, i)][:1])
            o = self.zinit(z)
            return frozenset([o.npcpos.get(i, self.Wd.npc_pos[(z, i)][0]) if o else self.Wd.npc_pos[(z, i)][0]])
        p = self.st.npc_pos.get((z, i))
        return p if p is not None else frozenset(self.Wd.npc_pos[(z, i)][:1])

    def flagvals(self, z, f):
        if f < TEMP_FLAGS:                                               # a map-local flag: what the zone's map scripts set
            if self.zinit is not None:
                o = self.zinit(z)
                v = o.local.get(f, ZERO) if o else ZERO
                return ZERO if v is TOP else v
            return self.st.vals.get(('lf', z, f), ZERO)
        return self.st.get(('f', f))

    def npc_may_absent(self, z, i):
        n = self.Wd.R.entities(z)['npcs'][i]
        k = self.Wd.npc_kind(n)
        if k == 'boulder' and self.cap['STRENGTH']: return True
        if k == 'cut' and self.cap['CUT']: return True
        if k == 'rock' and self.cap['ROCK_SMASH']: return True
        return bool(n['flag']) and vs_has(self.flagvals(z, n['flag']), 1)

    def npc_may_present(self, z, i):
        n = self.Wd.R.entities(z)['npcs'][i]
        return not n['flag'] or vs_has(self.flagvals(z, n['flag']), 0)

    def trig_active(self, ev):
        """(may be active, may be inactive)"""
        if ev.work == 0: return True, False
        if is_temp(('w', ev.work)): return True, True          # a map-local work: what the visit's scripts set
        vs = self.st.get(('w', ev.work))
        return vs_has(vs, ev.value), vs is TOP or bool(vs - {ev.value})

    def dyn(self, base, t):
        """(can enter, triggers that may fire on entering) of a tile whose passability depends on the state."""
        k = (base, t)
        if k in self._dyn: return self._dyn[k]
        enter, trigs, stop = True, [], False
        for kind, z, i in self.Wd.dyn[k]:
            if kind == 'npc':
                tiles = self.npc_tiles(z, i)
                if t not in tiles: continue
                if len(tiles) > 1: continue                 # it may stand elsewhere
                if not self.npc_may_absent(z, i): enter = False
            else:
                ev = self.Wd.events.get(('trig', z, i))
                if ev is None: continue
                act, inact = self.trig_active(ev)
                if act: trigs.append(ev)
                if act and not inact and not (self.trig_pass and self.trig_pass(ev, t)): stop = True
        r = (enter and not stop, trigs if enter else [])
        self._dyn[k] = r
        return r

    def mr(self, ev, v):
        return vs_has(self.st.get(('mr', ev)), v)

    def warp_at(self, z, i, k):
        if self.zinit is not None and (z, i) in self.Wd.moved_warp:
            o = self.zinit(z)
            t = o.warppos.get(i, self.Wd.warp_pos[(z, i)][0]) if o else self.Wd.warp_pos[(z, i)][0]
            return self.Wd.warp_pos[(z, i)][k] == t
        p = self.st.warp_pos.get((z, i))
        if p is None: return k == 0
        return self.Wd.warp_pos[(z, i)][k] in p

    def state_ok(self, s):
        """Can the player be in state s (its layout loaded)?"""
        G, D = self.Wd.G, self.Wd.D
        si, t, li, m = G.states[s]
        key = G.keys[si]
        if key[0] == 'room':
            if len(key) == 3: return self.mr(key[2], 1)
            return all(self.mr(ev, 0) for ev in D.room_alts.get(key[1], ()))
        if key[0] == 'main':
            if len(key) == 2: return self.mr(key[1], 1)
            return all(self.mr(ev, 0) for ev, a in D.main_alts.items() if t in a.recs)
        return True

    def ok(self, atom):
        a = atom[0]
        if a == 'var': return self.state_ok(atom[1])
        if a == 'cap': return self.cap[atom[1]]
        if a == 'mr': return self.mr(atom[1], atom[2])
        if a == 'warp': return self.warp_at(atom[1], atom[2], atom[3])
        if a == 'dyn': return self.dyn(atom[1], atom[2])[0]
        return True


def reach(Wd, view, starts):
    """Components reached from the start states; the triggers touched ({event key: set of states stepped onto})."""
    G = Wd.G
    seen = set(); q = deque()
    for s in starts:
        if not view.state_ok(s): continue
        c = G.comp[s]
        if c not in seen: seen.add(c); q.append(c)
    touched = defaultdict(set)
    while q:
        c = q.popleft()
        for lst in (G.cout[c], Wd.portal_edges.get(c, ())):
            for d, conds in lst:
                if d in seen and not any(a[0] == 'dyn' for a in conds): continue
                go = True
                for a in conds:
                    if a[0] == 'dyn':
                        enter, trigs = view.dyn(a[1], a[2])
                        if trigs:
                            for ev in trigs:
                                for s in G.members[d]:
                                    if s in ev.inter.get(G.states[s][1], ()): touched[ev.key].add(s)
                        if not enter: go = False
                    elif not view.ok(a): go = False
                if go and d not in seen: seen.add(d); q.append(d)
    return seen, touched


# ------------------------------------------------------------------------------------------------------ the may-pass
NEW_GAME_ZONE = 394                            # opening.py: the truck; scripts 29 and 30 run at the start


def trainer_of(sid):
    if 3000 <= sid < 5000: return sid - 3000
    if 5000 <= sid < 7000: return sid - 5000
    return None


class MaySolver:
    """Grows the set of values every key can have, the places the player can be and the events that can fire, until
    nothing changes."""
    def __init__(self, Wd, interp, log=None):
        self.Wd, self.I, self.G = Wd, interp, Wd.G
        self.st = State()
        self.starts = set()
        self.arrivals = {}                      # ('arrive', zone, sid, tile) -> Event
        self.last = {}                          # event key -> snapshot of the values it read
        self.fired = {}                         # event key -> pass number it first ran
        self.outcomes = defaultdict(int)        # event key -> paths that ran
        self.first_set = {}                     # key -> (pass, event key) the first write of each value
        self.passno = 0
        self.log = log
        self.mapchange_bad = []
        self._tp = {}

    def add_arrival(self, zone, sid, tile, src):
        k = ('arrive', zone, sid, tile)
        if k not in self.arrivals:
            ev = Event(k, 'arrive', zone, None, sid, f'{self.Wd.D.name(zone)}: arrival script {sid} at {tile} (from {src})',
                       ctx=dict(player=tile))
            self.arrivals[k] = ev
            return True
        return False

    def landing(self, mc, src):
        """Start states of a scripted map change ('xy', zone, x, z, y)."""
        _, z, x, zz, y = mc
        z = self.Wd.D.zone(z) if z is not None else None
        if None in (z, x, zz):
            self.I.limits[f'map change with works ({src})'] += 1; return []
        if z not in self.Wd.D.zset or self.Wd.D.space_of(z) is None:
            self.mapchange_bad.append((src, mc)); return []
        warps = self.Wd.R.entities(z)['warps']
        dirv = None
        for w in warps:
            if w['tile_x'] <= x < w['tile_x'] + max(1, w['w']) and w['tile_z'] <= zz < w['tile_z'] + max(1, w['h']):
                dirv = WARP_VEC.get(w['dir'])
        out = self.Wd.arrival_states(z, (x, zz), None, dirv)
        if not out: self.mapchange_bad.append((src, mc))
        return out

    def apply(self, ev, outs):
        st, changed = self.st, False
        for o in outs:
            for k, v in o.writes.items():
                if is_temp(k): continue
                cur = st.vals.get(k, ZERO)
                new = vs_union(cur, v)
                if new != cur:
                    st.vals[k] = new; changed = True
                    for x in (v if v is not TOP else ['TOP']):
                        self.first_set.setdefault((k, x), (self.passno, ev.key))
            z = ev.zone
            if ev.kind in ('map', 'cond'):
                for f in self.Wd.local_flags.get(z, ()):
                    k = ('lf', z, f)
                    cur = st.vals.get(k, frozenset())
                    new = vs_union(cur, o.local.get(f, ZERO))
                    if new != cur: st.vals[k] = new; changed = True
            if ev.kind == 'map' and ev.key[2] == 2:
                for i in range(len(self.Wd.R.entities(z)['npcs'])):
                    if (z, i) not in self.Wd.moved_npc: continue
                    t = o.npcpos.get(i, self.Wd.npc_pos[(z, i)][0])
                    cur = st.npc_pos.get((z, i), frozenset())
                    if t not in cur: st.npc_pos[(z, i)] = cur | {t}; changed = True
            wp = dict(o.warppos)
            if ev.kind == 'map' and ev.key[2] == 2:
                for (zz, i) in self.Wd.moved_warp:
                    if zz == z: wp.setdefault(i, self.Wd.warp_pos[(z, i)][0])
            for i, t in wp.items():
                key = (z, i)
                cur = st.warp_pos.get(key)
                if cur is None: cur = frozenset(self.Wd.warp_pos[key][:1]) if key in self.Wd.warp_pos else frozenset()
                if t not in cur: st.warp_pos[key] = cur | {t}; changed = True
            if ev.kind == 'map' and ev.key[2] == 2 and o.warppos == {}:
                pass
            new_starts = []
            if o.mapchange:
                new_starts = self.landing(o.mapchange, ev.what)
                if o.reserved is not None and o.mapchange[1] is not None and new_starts:
                    if self.add_arrival(self.Wd.D.zone(o.mapchange[1]), o.reserved, (o.mapchange[2], o.mapchange[3]), ev.what): changed = True
            elif ev.kind in ('trig', 'arrive') and o.end != 'lose':
                base_tiles = [ev.ctx['player']] if ev.kind == 'arrive' else [self.G.states[s][1] for s in ev.ctx.get('touched', ())]
                for t in base_tiles:
                    q = (t[0] + o.disp[0], t[1] + o.disp[1])
                    new_starts += self.Wd.states_on(ev.zone, q)
            for s in new_starts:
                if s not in self.starts: self.starts.add(s); changed = True
        if changed: st.version += 1
        return changed

    def run_event(self, ev, ctx_extra=None):
        st = self.st
        if ev.kind == 'trainer':
            t = trainer_of(ev.sid)
            o = Outcome(); o.writes = {('f', TRAINER_FLAG0 + t): ONE} if t is not None else {}
            return [o], set()
        ctx = dict(ev.ctx)
        if ctx_extra: ctx.update(ctx_extra)
        return self.I.run(ev.zone, ev.sid, st.get, ctx)

    def trig_pass(self, ev, t):
        """May the player stay on trigger tile t after the trigger's script (no map change, not moved)?"""
        k = (ev.key, t, self.st.version)
        if k not in self._tp:
            outs, reads = self.I.run(ev.zone, ev.sid, self.st.get, dict(ev.ctx, player=t))
            self._tp[k] = any(o.mapchange is None and o.disp == (0, 0) and o.end != 'lose' for o in outs)
        return self._tp[k]

    def available(self, comps, touched):
        Wd, G, st = self.Wd, self.G, self.st
        view = self.view
        zones = set()
        for c in comps: zones |= Wd.comp_zones[c]
        self.zones = zones
        out = []
        for k, ev in Wd.events.items():
            if ev.kind == 'trig':
                if k in touched: ev.ctx['touched'] = touched[k]; out.append(ev)
                continue
            if ev.zone not in zones: continue
            if ev.kind == 'map': out.append(ev); continue
            if ev.kind == 'cond':
                if is_temp(('w', ev.work)) or vs_has(st.get(('w', ev.work)), ev.value): out.append(ev)
                continue
            if ev.kind == 'trig':
                if k in touched: ev.ctx['touched'] = touched[k]; out.append(ev)
                continue
            if ev.kind in ('npc', 'trainer') and not view.npc_may_present(ev.zone, ev.idx): continue
            tiles = view.npc_tiles(ev.zone, ev.idx) if ev.kind in ('npc', 'trainer') else ev.inter.keys()
            if any(G.comp[s] in comps for t in tiles for s in ev.inter.get(t, ())): out.append(ev)
        for k, ev in self.arrivals.items():
            out.append(ev)
        return out

    def solve(self, max_passes=400):
        Wd = self.Wd
        h = Wd.R.hdr[NEW_GAME_ZONE]
        self.add_arrival(NEW_GAME_ZONE, 29, (h['fly_x'], h['fly_z']), 'new game')
        self.add_arrival(NEW_GAME_ZONE, 30, (h['fly_x'], h['fly_z']), 'new game')
        self.starts.update(Wd.arrival_states(NEW_GAME_ZONE, (h['fly_x'], h['fly_z'])))
        t0 = time.time()
        while self.passno < max_passes:
            self.passno += 1
            self.view = self.View()
            comps, touched = reach(Wd, self.view, self.starts)
            self.comps, self.touched = comps, touched
            changed = False
            for ev in self.available(comps, touched):
                snap_keys = self.last.get(ev.key)
                if snap_keys is not None:
                    keys, vals = snap_keys
                    if tuple(self.st.get(k) for k in keys) == vals and ev.kind != 'trig' and ev.kind != 'arrive': continue
                    if ev.kind in ('trig', 'arrive') and tuple(self.st.get(k) for k in keys) == vals and \
                            self.fired.get(ev.key, (0, 0))[1] == len(ev.ctx.get('touched', ())): continue
                outs, reads = self.run_event(ev)
                keys = tuple(sorted(reads, key=repr))
                self.last[ev.key] = (keys, tuple(self.st.get(k) for k in keys))
                if ev.key not in self.fired: self.fired[ev.key] = (self.passno, len(ev.ctx.get('touched', ())))
                else: self.fired[ev.key] = (self.fired[ev.key][0], len(ev.ctx.get('touched', ())))
                self.outcomes[ev.key] += len(outs)
                if self.apply(ev, outs): changed = True
            if self.log: self.log(f'pass {self.passno}: {len(comps)} components, {len(self.zones)} zones, '
                                  f'{len(self.fired)} events fired, {len(self.st.vals)} keys, {time.time() - t0:.1f}s')
            if not changed: break
        return self


# ------------------------------------------------------------------------------------------------------ the play-pass
CHAPTERS = [   # (chapter, what starts it: a predicate on the state) -- notes/STORY_CHAPTERS.md section 1
    ('Ch0', 'new game', lambda g: True),
    ('Ch1', 'the starter received (Birch rescued)', lambda g: 1 in g(('party',)) or 2 in g(('party',))),
    ('Ch2', 'Stone Badge (Roxanne)', lambda g: 1 in g(('b', 0))),
    ('Ch3', 'Knuckle Badge (Brawly)', lambda g: 1 in g(('b', 1))),
    ('Ch4', 'Dynamo Badge (Wattson)', lambda g: 1 in g(('b', 2))),
    ('Ch5', 'the grunts leave the cable car (Meteor Falls done)', lambda g: 1 in g(('f', 461))),
    ('Ch6', 'Heat Badge (Flannery)', lambda g: 1 in g(('b', 3))),
    ('Ch7', 'Balance Badge (Norman)', lambda g: 1 in g(('b', 4))),
    ('Ch8', 'Feather Badge (Winona)', lambda g: 1 in g(('b', 5))),
    ('Ch9', 'Team escaped in the submarine (Aqua Hideout done)', lambda g: 1 in g(('f', 646))),
    ('Ch10', 'Mind Badge (Tate & Liza)', lambda g: 1 in g(('b', 6))),
    ('Ch11', 'Rain Badge (Wallace)', lambda g: 1 in g(('b', 7))),
    ('Ch13', 'Hall of Fame (post-game)', lambda g: 1 in g(('hof',))),
]
RESPAWN_HOUSE = (390, 389)                      # the player's house 1F / Littleroot (RESPAWN_ZONE_INFO 1)


def map_chapters():
    """{Sapphire map: chapter number} from notes/STORY_CHAPTERS.md (each chapter's 'owned' maps)."""
    out, cur = {}, None
    p = os.path.join(ROOT, 'notes', 'STORY_CHAPTERS.md')
    if not os.path.exists(p): return out
    for ln in open(p):
        h = re.match(r'### Ch(\d+)', ln)
        if h: cur = int(h.group(1)); continue
        if ln.startswith('### ') or ln.startswith('## '): cur = None if not ln.startswith('### Ch') else cur
        r = re.match(r'\| ([A-Za-z0-9_]+) \| owned', ln)
        if r and cur is not None: out.setdefault(r.group(1), cur)
    return out


class PlaySolver:
    """One realistic playthrough: an eager player (does every event it can reach, the best way each time) from the new
    game, with a real position. Fly after badge 6 (to a town visited before), whiting out to the last Center when stuck."""
    def __init__(self, Wd, interp, log=None, max_steps=20000):
        self.Wd, self.I, self.G = Wd, interp, Wd.G
        self.st = State()
        self.log = log
        self.max_steps = max_steps
        self.steps = []                         # (n, event what, changes)
        self.chapters = {}                      # chapter -> snapshot
        self.visited = set()
        self.fired = Counter()
        self.cache = {}
        self.seen_states = set()
        self.respawn = None
        self.anchor = None
        self.whiteouts = 0
        self.mapchange_bad = []
        self.fly_spots = {}
        for zs, zz in Wd.D.W.W['zones'].items():
            if zz.get('kind') == 'town' and zz.get('fly') and int(zs) in Wd.D.zset:
                st = Wd.arrival_states(int(zs), tuple(zz['fly']))
                if st: self.fly_spots[int(zs)] = st[0]
        self.centers = {z for z in Wd.D.zones if Wd.D.name(z).endswith('PokemonCenter_1F')}
        self.history = {}                       # key -> values it has had
        mc = map_chapters()
        self.zone_ch = {}
        for z in Wd.D.zones:
            zz = Wd.D.W.W['zones'].get(str(z))
            names = zz.get('maps', []) if zz else [Wd.D.name(z)]
            chs = [mc[n] for n in names if n in mc]
            self.zone_ch[z] = min(chs) if chs else 13            # (maps added after the chapter split: the post-game)
        self.cur_ch = 0
        # keys whose change can change where the player can go (people's hide flags, trigger works, abilities, layouts)
        rel = set()
        for z in Wd.D.zones:
            for n in Wd.R.entities(z)['npcs']:
                if n['flag']: rel.add(('f', n['flag']) if n['flag'] >= TEMP_FLAGS else ('lf', z, n['flag']))
        for ev in Wd.events.values():
            if ev.kind in ('trig', 'cond') and ev.work: rel.add(('w', ev.work))
        for m, (item, badge) in FIELD_MOVES.items(): rel.add(('i', item)); rel.add(('b', badge))
        self.relevant = rel

    def g(self, key):
        return self.st.get(key)

    def hash(self):
        return hash((frozenset(self.st.vals.items()), frozenset(self.st.npc_pos.items()), frozenset(self.st.warp_pos.items()),
                     self.G.comp[self.anchor] if self.anchor is not None else None))

    def zinit(self, z):
        """The zone init's outcome on the current state (where its people and warps are, its map-local flags)."""
        evs = self.Wd.inits.get(z)
        if not evs: return None
        o = None
        for ev in evs:
            outs = self.run(ev)
            b = self.choose(ev, outs) if outs else None
            if b:
                if o is None: o = b[1]
                else:
                    o2 = Outcome(); o2.npcpos = dict(o.npcpos, **b[1].npcpos); o2.warppos = dict(o.warppos, **b[1].warppos)
                    o2.local = dict(o.local, **b[1].local); o = o2
        return o

    def View(self):
        return View(self.Wd, self.st, self.trig_pass, self.zinit)

    def solve_puzzles(self):
        """Thin-ice rooms: solved by check_ice (a search on the real tiles and scripts); the play-pass then walks them
        as solved (every tile cracked once: the ramps open) instead of following the visit's step counts."""
        self.ice = {}
        self.puzzles = []
        for z in self.Wd.D.zones:
            name = self.Wd.D.name(z)
            if name in ICE_ROOMS:
                ok, how, count = check_ice(self.Wd, z, ICE_ROOMS[name], Interp(self.Wd.D, concrete=True))
                tiles = getattr(check_ice, 'tiles', dict(ice=set(), ramps={}))
                self.puzzles.append((name, ok, how, count))
                if ok: self.ice[z] = (ICE_ROOMS[name], count, tiles['ice'])

    def run(self, ev, ctx_extra=None):
        if ev.kind == 'trig' and ev.zone in self.ice:            # a solved thin-ice room: the ramps see the full count
            w, count, tiles = self.ice[ev.zone]
            ctx_extra = dict(ctx_extra or {}, works={w: count})
        if ev.kind == 'trainer':
            t = trainer_of(ev.sid)
            o = Outcome(); o.writes = {('f', TRAINER_FLAG0 + t): ONE} if t is not None else {}
            return [o]
        ctx = dict(ev.ctx)
        if ctx_extra: ctx.update(ctx_extra)
        keyc = (ev.key, ctx.get('player') if ev.kind in ('arrive', 'trig') else None,
                tuple(sorted(ctx.get('works', {}).items())))
        c = self.cache.get(keyc)
        if c is not None:
            keys, vals, outs = c
            if tuple(self.st.get(k) for k in keys) == vals: return outs
        outs, reads = self.I.run(ev.zone, ev.sid, self.st.get, ctx)
        keys = tuple(sorted(reads, key=repr))
        self.cache[keyc] = (keys, tuple(self.st.get(k) for k in keys), outs)
        if ev.kind in ('map', 'cond'): self.relevant.update(keys)    # (what a zone's people and warps depend on)
        return outs

    def changes(self, ev, o):
        """{key: new value} of an outcome against the state (and the zone's people / warps / local flags)."""
        ch = {}
        for k, v in o.writes.items():
            if is_temp(k) or v is TOP: continue
            if self.st.get(k) != v: ch[k] = v
        return ch                    # (people, warps and map-local flags of a zone come from its init: zinit())

    def choose(self, ev, outs):
        """The outcome an eager player picks: no lost battle; a new place first; then the most changes."""
        best = None
        for o in outs:
            if o.end == 'cut': continue
            ch = self.changes(ev, o)
            new = 0
            if o.mapchange and o.mapchange[1] is not None and self.Wd.D.zone(o.mapchange[1]) not in self.visited: new = 1
            score = (o.end != 'lose', new, len(ch), -len(o.battles))
            if best is None or score > best[0]: best = (score, o, ch)
        return best

    def apply(self, ev, o, ch, where):
        for k, v in ch.items():
            if k[0] == 'npcpos': self.st.npc_pos[(k[1], k[2])] = v
            elif k[0] == 'warppos': self.st.warp_pos[(k[1], k[2])] = v
            else: self.st.vals[k] = v
        moved = None
        if o.mapchange:
            _, z, x, zz, y = o.mapchange
            z = self.Wd.D.zone(z) if z is not None else None
            arr = MaySolver.landing(self, o.mapchange, ev.what) if z is not None else []
            view = View(self.Wd, self.st)
            arr = [a for a in arr if view.state_ok(a)] or arr
            if arr:
                moved = arr[0]
                if o.reserved is not None:
                    ak = ('arrive', z, o.reserved, (x, zz))
                    self.pending.append(Event(ak, 'arrive', z, None, o.reserved, f'{self.Wd.D.name(z)}: arrival script {o.reserved} at {(x, zz)}',
                                              ctx=dict(player=(x, zz))))
        elif ev.kind in ('trig', 'arrive') and o.end != 'lose':
            t = ev.ctx['player'] if ev.kind == 'arrive' else self.G.states[where][1] if where is not None else None
            if t is not None:
                q = (t[0] + o.disp[0], t[1] + o.disp[1])
                view = View(self.Wd, self.st)
                s = [x for x in self.Wd.states_on(ev.zone, q) if view.state_ok(x)]
                if s: moved = s[0]
        elif where is not None:
            moved = where
        if moved is not None: self.anchor = moved
        if ev.kind != 'map' or ch:
            self.steps.append((len(self.steps), ev.what, {repr(k): sorted(v) for k, v in ch.items()}
                               | ({'map change': list(o.mapchange[1:4])} if o.mapchange else {})))
        self.fired[ev.key] += 1
        if any(c[0] == 'b' for c in ch) and self.log: self.log(f'  step {len(self.steps)}: {ev.what}: badge {[c[1] + 1 for c in ch if c[0] == "b"]}')
        self.snapshot(ev)

    def snapshot(self, ev):
        for name, why, pred in CHAPTERS:
            if pred(self.g): self.cur_ch = max(self.cur_ch, int(name[2:]))
            if name not in self.chapters and pred(self.g):
                self.chapters[name] = dict(step=len(self.steps), event=ev.what if ev else 'new game', why=why,
                                           vals=dict(self.st.vals), anchor=self.anchor,
                                           npc_pos=dict(self.st.npc_pos))
                if self.log: self.log(f'  {name} starts at step {len(self.steps)} ({why}) at {self.G.describe(self.anchor) if self.anchor is not None else "?"}')

    def interact_state(self, ev, comps, touched):
        """A reached state the event can be done from (None: not reachable now)."""
        G = self.G
        if ev.kind == 'trig':
            ss = touched.get(ev.key)
            return next(iter(sorted(ss))) if ss else None
        if ev.kind in ('map', 'cond'): return self.anchor
        tiles = self.view.npc_tiles(ev.zone, ev.idx) if ev.kind in ('npc', 'trainer') else ev.inter.keys()
        best = None
        for t in tiles:
            for s in ev.inter.get(t, ()):
                if G.comp[s] in comps:
                    if G.comp[s] == G.comp[self.anchor]: return s
                    if best is None: best = s
        return best

    def candidates(self, comps, touched):
        Wd, st = self.Wd, self.st
        view = self.view
        zones = set()
        for c in comps: zones |= Wd.comp_zones[c]
        self.visited |= zones
        az = self.G.sp[self.G.states[self.anchor][0]].zone_of(self.G.states[self.anchor][1])
        out = []
        for k, ev in Wd.events.items():
            if ev.kind == 'trig':
                if ev.zone in self.ice and ev.tiles[0] in self.ice[ev.zone][2]: continue   # (thin ice: solved)
                if k in touched:
                    act, inact = view.trig_active(ev)
                    if act: ev.ctx['touched'] = touched[k]; out.append(ev)
                continue
            if ev.zone not in zones: continue
            if ev.kind == 'map':
                out.append(ev); continue
            if ev.kind == 'cond':
                if is_temp(('w', ev.work)) or vs_has(st.get(('w', ev.work)), ev.value): out.append(ev)
                continue
            if ev.kind in ('npc', 'trainer') and not view.npc_may_present(ev.zone, ev.idx): continue
            out.append(ev)
        # the anchor's zone first (its map scripts run on entry), then by zone, kind
        order = {'map': 0, 'cond': 1, 'trig': 2, 'trainer': 3, 'npc': 4, 'sign': 5}
        cur = self.cur_ch
        out.sort(key=lambda e: (max(0, self.zone_ch.get(e.zone, 13) - cur), e.zone != az, order.get(e.kind, 9), e.zone, repr(e.key)))
        return out

    def starts(self):
        out = {self.anchor}
        if self.view.cap['FLY']:
            for z, s in self.fly_spots.items():
                if z in self.visited: out.add(s)
        return out

    def solve(self):
        Wd = self.Wd
        self.solve_puzzles()
        h = Wd.R.hdr[NEW_GAME_ZONE]
        t0 = (h['fly_x'], h['fly_z'])
        self.anchor = Wd.arrival_states(NEW_GAME_ZONE, t0)[0]
        self.pending = deque(Event(('arrive', NEW_GAME_ZONE, sid, t0), 'arrive', NEW_GAME_ZONE, None, sid,
                                   f'truck: new-game script {sid}', ctx=dict(player=t0)) for sid in (29, 30))
        self.snapshot(None)
        n = 0
        stuck_tries = set()
        while n < self.max_steps:
            n += 1
            self.view = self.View()
            if self.pending:
                ev = self.pending.popleft()
                outs = self.run(ev)
                b = self.choose(ev, outs)
                if b: self.apply(ev, b[1], b[2], None)
                continue
            comps, touched = reach(Wd, self.view, self.starts())
            fired = False
            travel = []
            for ev in self.candidates(comps, touched):
                where = self.interact_state(ev, comps, touched)
                if where is None: continue
                ctx = None
                if ev.kind == 'trig': ctx = dict(player=self.G.states[where][1])
                outs = self.run(ev, ctx)
                b = self.choose(ev, outs)
                if b is None: continue
                score, o, ch = b
                mc = o.mapchange is not None and o.mapchange[1] is not None
                if mc and self.Wd.D.zone(o.mapchange[1]) in self.visited:
                    travel.append((ev, o, ch, where)); continue          # (a trip back: only when nothing else is left)
                if ch and not self.progress(ch):
                    travel.append((ev, o, ch, where)); continue          # (only values seen before: a toggle)
                if not ch and not mc and not (ev.kind == 'trig' and o.disp != (0, 0) and self.leaves(ev, o, where, comps)):
                    continue
                quiet = not mc and o.disp == (0, 0) and not any(k in self.relevant or k[0] in ('npcpos', 'warppos', 'mr', 'lf')
                                                                for k in ch) and ev.kind not in ('map', 'cond')
                ch0 = self.cur_ch
                if self.fire(ev, o, ch, where):
                    fired = True
                    if quiet and self.cur_ch == ch0 and not self.pending:
                        self.view = self.View()
                        continue                             # nothing that moves the player or the map: go on scanning
                    break
            if fired: continue
            # nothing new here: a trip somewhere visited (boat, ferry, warp scene), Fly is in starts(); else white out
            for ev, o, ch, where in travel:
                if self.fire(ev, o, ch, where, need_new=comps): fired = True; break
            if fired: continue
            if self.whiteout(comps): continue
            break
        self.final_comps, self.final_touched = reach(Wd, self.View(), self.starts())
        return self

    def progress(self, ch):
        """Does a change give some key a value it never had (so not a toggle back and forth)?"""
        for k, v in ch.items():
            if v not in self.history.get(k, ()): return True
        return False

    def fire(self, ev, o, ch, where, need_new=None):
        """Applies an event's outcome unless it brings back a state seen before (a cycle); need_new: only when the
        player ends where something not in those components can be reached."""
        before = (dict(self.st.vals), dict(self.st.npc_pos), dict(self.st.warp_pos), self.anchor, len(self.steps), len(self.pending))
        self.apply(ev, o, ch, where if ev.kind not in ('map', 'cond') else None)
        hsh = self.hash()
        bad = hsh in self.seen_states
        if not bad and need_new is not None:
            c2, _ = reach(self.Wd, self.View(), self.starts())
            bad = c2 <= need_new and not self.pending
        if bad:
            self.st.vals, self.st.npc_pos, self.st.warp_pos, self.anchor = before[0], before[1], before[2], before[3]
            del self.steps[before[4]:]
            while len(self.pending) > before[5]: self.pending.pop()
            self.fired[ev.key] -= 1
            return False
        self.seen_states.add(hsh)
        for k, v in ch.items(): self.history.setdefault(k, set()).add(v)
        return True

    def trig_pass(self, ev, t):
        if ev.zone in self.ice and t in self.ice[ev.zone][2]: return True
        outs = self.run(ev, dict(player=t))
        b = self.choose(ev, outs)
        return b is not None and b[1].mapchange is None and b[1].disp == (0, 0) and b[1].end != 'lose'

    def leaves(self, ev, o, where, comps):
        t = self.G.states[where][1]
        q = (t[0] + o.disp[0], t[1] + o.disp[1])
        return any(self.G.comp[s] not in comps for s in self.Wd.states_on(ev.zone, q))

    def whiteout(self, comps):
        Wd = self.Wd
        tgt = None
        cs = [z for z in self.visited if z in self.centers]
        cands = []
        for z in sorted(cs) + [RESPAWN_HOUSE[0]]:
            for i, w in enumerate(Wd.R.entities(z)['warps']):
                cands += Wd.warp_arrival(z, i)
        for s in cands:
            if self.G.comp[s] not in comps:
                key = (self.hash(), s)
                if key in self.seen_states: continue
                self.seen_states.add(key)
                tgt = s; break
        if tgt is None: return False
        self.whiteouts += 1
        self.steps.append((len(self.steps), f'(stuck at {self.G.describe(self.anchor)}: white out / escape to {self.G.describe(tgt)})', {}))
        self.anchor = tgt
        return True


# ------------------------------------------------------------------------------------------------------ puzzles
ICE_ROOMS = {'SootopolisCity_Gym_1F': 0x40E0}   # thin-ice rooms: map -> the step-count work (VAR_ICE_STEP_COUNT)


def check_ice(Wd, zone, count_work, interp, log=None):
    """Sootopolis Gym's thin ice (scripts of 0046_room_SootopolisCity_Gym_1F.s, Sapphire's PerStepCallback): a first step on
    a thin-ice trigger cracks it and counts up, a second one drops the player to B1F; the ramp triggers slide the player back
    onto the tile below until the count reaches their need. Read from the ROM's own scripts: each trigger is run with
    counts 1..100. Then a search (tile, cracked tiles, count) from the room's entrance to the leader, never stepping on a
    cracked tile. Returns (solvable, path length or reason, the count at the leader)."""
    G, D = Wd.G, Wd.D
    key = ('w', count_work)
    ice, ramps = {}, {}
    for (k, z, i), ev in [(k, ev) for k, ev in Wd.events.items() if k[0] == 'trig' and k[1] == zone]:
        t = ev.tiles[0]
        res = {}
        for c in (1, 2, 5, 8, 9, 20, 28, 29, 50, 69, 70, 99):
            outs, _ = interp.run(zone, ev.sid, lambda kk: V(c) if kk == key else ZERO, dict(player=t, works={}))
            res[c] = outs
        o1 = res[1]
        if any(key in o.writes and o.mapchange is None and o.disp == (0, 0) for o in o1):
            ice[t] = ev
        elif any(o.disp != (0, 0) for o in o1):
            need = next((c for c in sorted(res) if all(o.disp == (0, 0) for o in res[c])), None)
            ramps[t] = (need, ev)
    if not ice: return None, 'no thin-ice triggers found', None
    needs = sorted(n for n, ev in ramps.values() if n)
    unlock = {n - 1 for n in needs}                         # the count at which the next ramp opens (+1 more)
    si = G.si[D.space_of(zone)]
    sp = G.sp[si]
    walk = {}
    for (s_i, t, li), s in G.sid.items():
        if s_i != si or G.states[s][3] != LAND: continue
        walk[t] = s
    def nbrs(t):
        s = walk[t]
        out = []
        for d, conds in G.out[s]:
            if G.states[d][0] != si: continue
            out.append(G.states[d][1])
        return out
    # the entrance: arrival tiles of warps into this zone; the goal: the tiles next to the leader (the zone's first person)
    starts = set()
    for z2 in D.zones:
        for i2, w in enumerate(D.R.entities(z2)['warps']):
            if D.zone(w['dest_zone']) == zone:
                starts |= {G.states[s][1] for s in Wd.warp_arrival(zone, w['dest_warp'], z2)}
    leader = next((ev for k, ev in Wd.events.items() if k[0] == 'npc' and k[1] == zone and ev.ctx['npc']['uid'] == 1), None)
    goal = {t for t in walk if leader and any(abs(t[0] - x) + abs(t[1] - y) == 1 for x, y in Wd.npc_pos[(zone, leader.idx)])}
    blocked = {(n['x'], n['z']) for n in D.R.entities(zone)['npcs'] if n['flag'] == 0}
    import sys as _s
    _s.setrecursionlimit(10000)
    seen = set()
    best = [None]
    def step_on(t, cracked, count):
        """Count after a first step on t (or None: a cracked tile = a fall)."""
        if t in cracked: return None
        count += 1
        if count in unlock: count += 1
        return count
    def dfs(t, cracked, count, depth):
        if t in goal: best[0] = (depth, count); return True
        k = (t, cracked, count)
        if k in seen: return False
        seen.add(k)
        if len(seen) > 2_000_000: return False
        for n in nbrs(t):
            if n in blocked: continue
            if n in ramps:
                need = ramps[n][0]
                if need is None or count < need: continue       # slid back (onto the tile below: never better)
                if dfs(n, cracked, count, depth + 1): return True
                continue
            if n in ice:
                c2 = step_on(n, cracked, count)
                if c2 is None: continue
                if dfs(n, cracked | {n}, c2, depth + 1): return True
                continue
            if dfs(n, cracked, count, depth + 1): return True
        return False
    check_ice.tiles = dict(ice=set(ice), ramps={t: n for t, (n, ev) in ramps.items()})
    for t in sorted(starts):
        if t in walk and dfs(t, frozenset(), 1, 0):
            return True, best[0][0], best[0][1]
    return False, f'no way from {sorted(starts)} to the leader at {leader and Wd.npc_pos[(zone, leader.idx)]} ({len(ice)} thin-ice tiles, ramps need {needs}, {len(seen)} states searched)', None
