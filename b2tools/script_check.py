"""Script regression check (script_check agent, 2026-10-08; notes/TESTING.md "Script checks"): what the built ROM's
field scripts and zone entities do on the built world's tiles. A report step of rebuild_slice.sh, after the ROM.

    python3 b2tools/script_check.py ROM.nds [--world WORLD] [--dir INTERIORS] [--kinds k1,k2] [--zone N ...] [--all]
                                    [--vanilla]

Reads what the game has after every patch: the ROM's zone headers (a/0/1/2), zone entities (a/1/2/6: world.json's,
the generated people/signs, trainers, story objects, berry trees, hidden items), field scripts (a/0/5/6, decoded with the
decomp's own disassembler tools/scripts/field_script.py and its command table) and script texts (a/0/0/3); the world
(WORLD/world.json, cells/*/collision.per, default $HOENN_WORLD_DIR or work/world) and the built rooms and caves
(INTERIORS/<Map>/room.json + collision*.per, default $HOENN_INTERIORS_DIR or work/interiors; Ruby: data/versions.json's
rooms and room variants). Only Hoenn zones (world.json zones, the version's rooms). One line per finding,
"zone Z Name: (kind) detail"; by-design findings are in ACCEPT (counted apart, --all prints them).

Kinds:
  ent    a person on a tile nobody can stand on (solid, outside the zone's tiles, another zone's tiles: the game spawns a
         zone's people only while you are in it), two people that are always there on one tile; a sign / hidden item
         nobody can read (no walkable tile in front at its height: CheckBGPositionMatchGrid -2..+2, caves_check's rule); a
         step trigger on a tile nobody can step on or not within 2 units of its y (it never fires); ObjInitNPCGPos /
         ActorSetGPos onto such a tile
  mapc   a scripted map change (MapChangeCore / MapChangeWarp / h_warp_*) landing outside the target zone's built tiles,
         on a tile you cannot stand on, or (outdoors) on another zone's tile
  path   scripted movement: every ActorCmdExec walk / jump of a person (from its zone tile), and of the player from each
         tile of the step trigger that starts the scene (or the arrival tile of a scripted warp whose reserved script it
         is), followed through the script with the works it sets (PlayerGetGPos, WorkCmpConst ...; flag tests take both
         ways): a step onto a solid tile, water (people) or land (boats), a height jump of 20+ units (a cliff), or into a
         person who is always there (flag 0), a berry tree or a 3D object
  zone   a scripted walk of the player onto another zone's tile without the zone hold (map-local flag 0x60, h_zone_hold):
         Black 2 swaps zone at once and deletes every actor of the scene (notes/STORY_PORTING.md "Zone hold")
  msg    a balloon (ActorMsg / ParentActorMsg / ActorMsgGendered) waited on with LastKeyWait and still open at an info /
         system window (SystemMsg, InfoMsg, MsgPlaceSign) or a global script that opens its own window (RTCallGlobal 2805
         = h_giveitem's obtain-item script): ARM9 undefined instruction (notes/STORY_HANDOFFS.md, found by ch4)
  text   a message id past the end of the zone's (or global script's) text file
  id     a script id (people, signs, triggers, map-script tables, RTCallGlobal, RTReserveScript, MapScriptCondition)
         that resolves to no script; a script file that does not decode
  align  a movement list (ActorCmdExec target) not 4-byte aligned (missing `.balign 4` before it)
--vanilla runs the msg analysis over Black 2's own scripts too and prints which (open window, command) pairs Game Freak's
scripts use (the evidence for the msg rule).
"""
import os, sys, re, json, struct, argparse, subprocess, tempfile, collections
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
sys.path.insert(0, os.path.join(ROOT, 'external', 'pokebw2', 'tools', 'scripts'))
import field_script as FS                     # noqa: E402  (the decomp's disassembler: command table, tracing)
from msgdata import read_msgdata              # noqa: E402
import version                                # noqa: E402
import zoneheaders                            # noqa: E402
from zones import parse_entities              # noqa: E402

PLAYER = 255
VANILLA = os.path.join(ROOT, 'roms', 'black2_original.nds')   # Black 2's own entities (leftover triggers in rooms)
ZONE_HOLD_FLAG = 0x60                         # h_zone_hold (src/include/hoenn_story.inc)
SURF = {0x3d, 0x3e, 0x3f, 0x42, 0x43, 0x40, 0x94, 0x95, 0x96, 0x97}   # outdoor_check SURF_CLASSES + caves_check WATER
VAR0 = 0x4000
# movement actions that move (hoenn_story.inc, notes/STORY_PORTING.md section 7): code -> (dx, dz, tiles, kind)
DIRV = [(0, -1), (0, 1), (-1, 0), (1, 0)]
MOVES = {}
for base, n, kind in ((8, 1, 'walk'), (12, 1, 'walk'), (16, 1, 'walk'), (20, 1, 'walk'), (52, 1, 'jump'), (56, 2, 'jump'),
                      (92, 3, 'jump')):
    for d in range(4): MOVES[base + d] = (DIRV[d][0], DIRV[d][1], n, kind)
WATER_OBJECTS = {0x2000, 0x2001, 0x2002, 112, 194}    # 3D objects (missing_objects): sub shadow, Briney's boat, S.S. Tidal
BERRY_UIDS = range(400, 480)                            # berry trees (data/story/berry_spots.json: uid 400 + k)
# windows
OPEN = {'ActorMsg': 'B', 'ParentActorMsg': 'B', 'ActorMsgGendered': 'B', 'ActorMsgVersioned': 'B',
        'SystemMsg': 'S', 'SystemMsgAsync': 'S', 'InfoMsg': 'I', 'MsgPlaceSign': 'P', 'CheckerMsg': 'C'}
CLOSE = {'MsgWinCloseAll': 'BSIPC', 'ActorMsgClose': 'B', 'InfoMsgClose': 'SI', 'MsgPlaceSignClose': 'P',
         'CheckerMsgClose': 'C'}
# Black 2 commands that Hoenn's patches rewrote (other arguments than the decomp's table): 0x1c9 h_flash_scale (zone_effects.py,
# hoenn_story.inc: scale, frames), 434 pg_roamer_start (roamers.py, postgame_lib.inc: k, loc)
HOENN_COMMANDS = {0x1c9: ('u16', 'u16'), 434: ('u16', 'u16')}
MAPCHANGE = {'MapChangeCore': (0, 1, 3, 2), 'MapChangeWarp': (0, 1, 2, None)}   # name -> (zone, x, z, y) argument index


# ------------------------------------------------------------------------------------------------------ ROM
class Rom:
    def __init__(self, path, vanilla=False):
        import importlib.util
        spec = importlib.util.spec_from_file_location('npc_check_tool', os.path.join(HERE, 'npc_check.py'))
        NC = importlib.util.module_from_spec(spec); spec.loader.exec_module(NC)      # (not patches/npc_check.py)
        f = NC.Files(path)
        self.hdr = zoneheaders.parse(f.narc(12)[0])
        self.ents = f.narc(126); self.scr = f.narc(56); self.txt = f.narc(3)
        self.base, self.plugins, self.pzones, self.globals = FS.load_commands()
        for cmd, kinds in HOENN_COMMANDS.items():     # commands our patches gave new arguments
            self.base[cmd].kinds = list(kinds); self.base[cmd].meanings = [None] * len(kinds)
        self.plugin_of_zone = {z: n for n, zs in self.pzones.items() for z in zs}
        self._sf, self._tx, self._ent = {}, {}, {}

    def texts(self, n):
        if n not in self._tx:
            try: self._tx[n] = read_msgdata(self.txt[n]) if n < len(self.txt) else None
            except Exception: self._tx[n] = None
        return self._tx[n]

    def entities(self, zone):
        e = self.hdr[zone]['entities']
        if e not in self._ent:
            data = self.ents[e]
            ent, _ = parse_entities(data)
            init_off = struct.unpack_from('<I', data, 0)[0]
            ent['map_scripts'] = FS.map_script_ids(data[init_off + 4:])
            self._ent[e] = ent
        return self._ent[e]

    def script_file(self, n, zone=None):
        """Decoded script file n (FS.ScriptFile, traced from its entries), None if it is not one."""
        key = (n, self.plugin_of_zone.get(zone))
        if key not in self._sf:
            data = self.scr[n] if n < len(self.scr) else b''
            h = FS.script_header(data)
            if h is None: self._sf[key] = None
            else:
                sf = FS.ScriptFile(data, self.base, self.plugins.get(key[1]))
                sf.entries = h[0]
                sf.trace(h[0])
                if sf.errors:          # a zone our patches gave a script plugin (dive.py: the Abyssal Ruins underwater
                    for pn, cmds in self.plugins.items():                          # effect): the plugin it decodes with
                        alt = FS.ScriptFile(data, self.base, cmds)
                        alt.entries = h[0]; alt.trace(h[0])
                        if not alt.errors: sf = alt; break
                self._sf[key] = sf
        return self._sf[key]

    def resolve(self, zone, sid):
        """(file, entry index, text file) a script id runs in a zone, or None. Trainer ids (3000-6999) -> (1239, None)."""
        if sid == 0: return None
        if sid < 2000:
            h = self.hdr[zone]
            return h['scripts'], sid - 1, h['text']
        for g in self.globals:
            if g['first'] <= sid <= g['last']:
                if 3000 <= sid <= 6999: return g['file'], None, g['text_file']
                return g['file'], sid - g['first'], g['text_file']
        return None

    def map_scripts(self, zone):
        """Script ids of a zone's map-script tables (the header's init file and the entities' own table), with kind."""
        out = []
        n = self.hdr[zone]['init_scripts']
        data = self.scr[n] if n < len(self.scr) else b''
        pos = 0
        while pos + 6 <= len(data) and (kind := FS.u16(data, pos)) != 0:
            if kind == 1:
                t = pos + 6 + FS.s32(data, pos + 2)
                while 0 <= t and t + 6 <= len(data) and FS.u16(data, t) != 0:
                    out.append(('condition', FS.u16(data, t + 4))); t += 6
            else:
                out.append((f'map script {kind}', struct.unpack_from('<I', data, pos + 2)[0]))
            pos += 6
        out += [('entity map script', s) for s in self.entities(zone)['map_scripts']]
        return out


def labels_for(file_no):
    """{offset: label} of our source of script file file_no (assembled again; empty when there is no source)."""
    import scripts as SP
    back = {v: k for k, v in SP.room_numbers().items()}
    src = SP.source_for(back.get(file_no, file_no))
    if not src: return {}, None
    LLVM = SP.LLVM
    with tempfile.TemporaryDirectory() as t:
        o = os.path.join(t, 'x.o')
        r = subprocess.run([f'{LLVM}/clang', '--target=armv5te-none-eabi', '-x', 'assembler-with-cpp', '-c', *version.ASM_DEFINES,
                            '-I', f'{SP.DECOMP}/include', '-I', f'{SP.DECOMP}/lib/nitro/include', '-I', os.path.join(ROOT, 'src', 'include'),
                            '-I', os.path.join(ROOT, 'src', 'field_scripts'), '-D', 'BLACK2', '-o', o, os.path.abspath(src)],
                           capture_output=True, cwd=SP.DECOMP)
        if r.returncode: return {}, src
        nm = subprocess.run([f'{LLVM}/llvm-nm', '-n', '--defined-only', o], capture_output=True, text=True).stdout
    out = {}
    for ln in nm.split('\n'):
        p = ln.split()
        if len(p) == 3 and p[1] in 'tTdD' and not p[2].startswith('$'): out[int(p[0], 16)] = p[2]
    return out, src


# ------------------------------------------------------------------------------------------------------ geometry
def y_of(c, lx, lz):
    """Height of a collision record at the centre of chunk tile (lx, lz) (terrain/heights.py planes)."""
    from terrain import heights as H
    if c[0] & 3: return None
    nx, ny, nz = H.NORMALS[c[0] >> 2]
    return -(nx * (lx * 16 - 248) - nz * (lz * 16 - 248) + H.OFFS[c[1]]) / ny


class Geo:
    """A zone's tiles: layers {tile: record} (outdoor: per-cell collision.per; rooms: collision + collision1) and the
    zone each tile belongs to (outdoor: cells + zone_rects; rooms: the room's zone)."""
    def __init__(self, name, layers, zone_at, alts=()):
        self.name, self.layers, self.zone_at, self.alts = name, layers, zone_at, alts

    def recs(self, t):
        return [L(t) for L in self.layers if L(t) is not None]

    def inside(self, t): return bool(self.recs(t))

    def kind(self, t):
        """'land', 'surf' or None (blocked / outside) of the best layer."""
        best = None
        for c in self.recs(t):
            if c[3] & 1 and c[2] != 0x40: continue
            k = 'surf' if c[2] in SURF else 'land'
            if k == 'land': return 'land'
            best = k
        return best

    def reach(self, starts):
        """Tiles reachable on foot from starts (4-neighbours, walkable land, height steps < 20 units: outdoor_check's rule)."""
        seen, todo = set(), [t for t in starts if self.kind(t) == 'land']
        seen.update(todo)
        while todo:
            p = todo.pop(); hp = self.heights(p)
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (p[0] + dx, p[1] + dz)
                if q in seen or self.kind(q) != 'land': continue
                hq = self.heights(q)
                if hp and hq and min(abs(a - b) for a in hp for b in hq) >= 20: continue
                seen.add(q); todo.append(q)
        return seen

    def heights(self, t, walk_only=True):
        out = []
        for c in self.recs(t):
            if walk_only and c[3] & 1: continue
            y = y_of(c, t[0] % 32, t[1] % 32)
            if y is not None: out.append(y)
        return out


def _per_reader(path):
    b = open(path, 'rb').read()
    return lambda lx, lz: struct.unpack_from('<HHHH', b, 4 + 8 * (lz * 32 + lx))


class World:
    def __init__(self, wd, rooms_dir):
        self.wd, self.rooms_dir = wd, rooms_dir
        self.W = json.load(open(os.path.join(wd, 'world.json')))
        self._geo = {}
        self.zone_room = {}
        for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json'):
            c = json.load(open(f))
            if c.get('room') and version.room_in_version(c['room']):
                self.zone_room[int(c['zone'])] = (c['room'], version.room_variant(c['room']), c)

    def hoenn_zones(self):
        return sorted(set(int(z) for z in self.W['zones']) | set(self.zone_room))

    def name(self, z):
        if str(z) in self.W['zones']:
            zz = self.W['zones'][str(z)]
            return '/'.join(zz.get('maps', [])[:2]) or zz.get('group') or f'zone {z}'
        if z in self.zone_room: return self.zone_room[z][0]
        return f'zone {z}'

    def outdoor(self, z): return str(z) in self.W['zones']

    def geo(self, z):
        if z in self._geo: return self._geo[z]
        g = None
        if str(z) in self.W['zones']:
            grp = self.W['zones'][str(z)].get('group')
            if grp:
                G = next(x for x in self.W['standalone'] if x['group'] == grp)
                cells = {(c['cx'], c['cz']): os.path.join(self.wd, 'cells', c['dir']) for c in G['cells']}
                owner = {(c['cx'], c['cz']): c['zone'] for c in G['cells']}
                rects = []
            else:
                cells = {(c['cx'], c['cz']): os.path.join(self.wd, 'cells', f"{c['cx']:02d}_{c['cz']:02d}") for c in self.W['cells']}
                owner = {(c['cx'], c['cz']): c['zone'] for c in self.W['cells']}
                rects = self.W.get('zone_rects', [])
            key = grp or 'main'
            if key not in self._geo:
                cache = {}
                def layer(t, cells=cells, cache=cache):
                    c = (t[0] // 32, t[1] // 32)
                    if c not in cache:
                        p = os.path.join(cells[c], 'collision.per') if c in cells else None
                        cache[c] = _per_reader(p) if p and os.path.exists(p) else None
                    r = cache[c]
                    return r(t[0] % 32, t[1] % 32) if r and t[0] >= 0 and t[1] >= 0 else None
                zone_at = lambda t, owner=owner, rects=rects: next((zz for x0, z0, x1, z1, zz in rects if x0 <= t[0] <= x1 and z0 <= t[1] <= z1), owner.get((t[0] // 32, t[1] // 32)))
                alts = []
                if not grp:
                    by_map = defaultdict(dict)
                    for a in self.W.get('alt_cells', []): by_map[a['map']][(a['cx'], a['cz'])] = os.path.join(self.wd, 'cells', a['dir'])
                    for m, cs in by_map.items():
                        acache = {}
                        def alayer(t, cs=cs, acache=acache):
                            c = (t[0] // 32, t[1] // 32)
                            if c not in cs: return None
                            if c not in acache: acache[c] = _per_reader(os.path.join(cs[c], 'collision.per'))
                            return acache[c](t[0] % 32, t[1] % 32)
                        alts.append((m, Geo(f'alt_{m}', [alayer], zone_at)))
                self._geo[key] = Geo(key, [layer], zone_at, alts)
            g = self._geo[key]
        elif z in self.zone_room:
            room, built, cfg = self.zone_room[z]
            p = os.path.join(self.rooms_dir, built, 'room.json')
            if os.path.exists(p):
                meta = json.load(open(p))
                mw = meta.get('matrix', [1, 1])[0]
                chunks = meta.get('chunks') or [dict(collision=meta['collision'], collision1=meta.get('collision1'))]
                L0, L1 = {}, {}
                for k, c in enumerate(chunks):
                    if c is None: continue
                    ci, cj = k % mw, k // mw
                    for key, dst in (('collision', L0), ('collision1', L1)):
                        if not c.get(key): continue
                        b = open(os.path.join(self.rooms_dir, built, c[key]), 'rb').read()
                        for i in range(1024):
                            dst[(ci * 32 + i % 32, cj * 32 + i // 32)] = struct.unpack_from('<HHHH', b, 4 + 8 * i)
                g = Geo(built, [L0.get] + ([L1.get] if L1 else []), lambda t, z=z, L0=L0: z if t in L0 else None)
                g.origin = meta.get('origin', [0, 0])
        self._geo[z] = g
        return g


# ------------------------------------------------------------------------------------------------------ the checker
class Checker:
    def __init__(self, rom, world, kinds, only=None, vanilla=None):
        self.rom, self.world, self.kinds, self.only, self.vanilla = rom, world, kinds, only, vanilla
        self.out = []                      # (zone, kind, msg, (file, pc) or None)
        self._seen = set()
        self.arrivals = []                 # (target zone, x, z, reserved script, from)
        self.global_opens = {}
        self.unreached = Counter()         # Black 2 leftovers nobody can reach (not findings)

    def say(self, zone, kind, msg, where=None):
        k = (zone, kind, msg)
        if k in self._seen or kind not in self.kinds: return
        self._seen.add(k); self.out.append((zone, kind, msg, where))

    # ---------------------------------------------------------------------------------------------- entities
    def static_npcs(self, zone):
        """{tile: [npc]} of the people that are always there (flag 0), berry trees and 3D objects."""
        out = defaultdict(list)
        for n in self.rom.entities(zone)['npcs']:
            if n['flag'] == 0 or n['uid'] in BERRY_UIDS or n['model'] in WATER_OBJECTS:
                out[(n['x'], n['z'])].append(n)
        return out

    def check_entities(self, z):
        W, R = self.world, self.rom
        g = W.geo(z)
        if g is None: return
        e = R.entities(z)
        outdoor = W.outdoor(z)
        def where_ok(t, want='stand'):
            """(ok, why) for a tile of zone z: built, of zone z, walkable (stand) ."""
            if not g.inside(t): return False, 'outside the built tiles'
            k = g.kind(t)
            alt_ok = [m for m, ag in g.alts if ag.inside(t) and ag.kind(t)]
            if k is None and not alt_ok:
                c = g.recs(t)[0]
                return False, f'on a solid tile (class {c[2]:#x} flags {c[3]:#x})'
            zz = g.zone_at(t)
            if outdoor and zz is not None and zz != z:
                return False, f"on zone {zz}'s tiles ({W.name(zz)})"
            return True, k or f'walkable in alt layout {alt_ok[0]}'
        # people
        seen = defaultdict(list)
        for i, n in enumerate(e['npcs']):
            t = (n['x'], n['z'])
            what = f"person {i} uid {n['uid']} (sprite {n['model']}, script {n['script']}, flag {n['flag']}) at {t}"
            ok, why = where_ok(t)
            if n['model'] in WATER_OBJECTS:
                if not ok and 'solid' not in why: self.say(z, 'ent', f'{what}: {why}')
            elif not ok: self.say(z, 'ent', f'{what}: {why}')
            seen[t].append(n)
        for t, ns in seen.items():
            if len(ns) < 2: continue
            always = [n for n in ns if n['flag'] == 0 or n['uid'] in BERRY_UIDS or n['model'] in WATER_OBJECTS]
            same = Counter(n['flag'] for n in ns if n['flag'])
            if len(always) >= 2 or (always and len(ns) > len(always) and any(n['uid'] in BERRY_UIDS or n['model'] in WATER_OBJECTS for n in always)):
                self.say(z, 'ent', f'people on one tile {t}: ' + ', '.join(f"uid {n['uid']} (sprite {n['model']}, flag {n['flag']})" for n in ns))
        # signs / hidden items (BG events): read from a tile next to them (dir 0: from the south) at -2..+2 of its y
        for i, s in enumerate(e['signs']):
            t = (s['x'], s['z']); y = s['y']
            what = f"sign {i} (script {s['script']}, dir {s['dir']}) at {t} y {y}"
            sides = [(0, 1)] if s['dir'] == 0 else [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
            hs, other = [], []
            for dx, dz in sides:
                q = (t[0] + dx, t[1] + dz)
                if outdoor and g.zone_at(q) not in (None, z): other.append(q); continue
                hs += [h for h in g.heights(q) if g.kind(q) == 'land' or (dx, dz) == (0, 0)]
                for m, ag in g.alts: hs += ag.heights(q)
            if not g.inside(t): self.say(z, 'ent', f'{what}: outside the built tiles')
            elif not hs: self.say(z, 'ent', f'{what}: no walkable tile of this zone to read it from' + (f' (zone tiles of another zone at {other})' if other else ''))
            elif not any(-2 <= y - h < 2 for h in hs):
                self.say(z, 'ent', f'{what}: read from heights {sorted({round(h, 1) for h in hs})}: never readable')
        # step triggers: on a walkable tile within 2 units of their y (CheckTriggerPositionMatchXYZ: y-2 <= player y < y+2)
        vt = set()
        if self.vanilla is not None and not outdoor and z < len(self.vanilla.hdr):
            vt = {(t['script'], t['x'], t['z'], t['work'], t['value']) for t in self.vanilla.entities(z)['triggers']}
        for i, tr in enumerate(e['triggers']):
            y = tr['y'] - 0x10000 if tr['y'] >= 0x8000 else tr['y']
            if (tr['script'], tr['x'], tr['z'], tr['work'], tr['value']) in vt or tr['w'] >= 0x100: continue   # (below)
            bad = []
            for a in range(max(1, tr['w'])):
                for b in range(max(1, tr['h'])):
                    t = (tr['x'] + a, tr['z'] + b)
                    hs = g.heights(t) + [h for m, ag in g.alts for h in ag.heights(t)]
                    if outdoor and g.zone_at(t) not in (None, z): bad.append(f'{t} zone {g.zone_at(t)}')
                    elif not hs: bad.append(f'{t} not walkable')
                    elif not any(-2 <= h - y < 2 for h in hs): bad.append(f'{t} at {sorted({round(h, 1) for h in hs})}')
            if bad and len(bad) == max(1, tr['w']) * max(1, tr['h']):
                self.say(z, 'ent', f"trigger {i} (script {tr['script']}, work {tr['work']:#x}={tr['value']}) at ({tr['x']},{tr['z']}) {tr['w']}x{tr['h']} y {y}: never fires: {', '.join(bad[:4])}")
            elif bad:
                self.say(z, 'ent', f"trigger {i} (script {tr['script']}) at ({tr['x']},{tr['z']}) {tr['w']}x{tr['h']} y {y}: {len(bad)} of its tiles never fire: {', '.join(bad[:4])}")
        # Black 2's own triggers and signs left in a room zone (the interiors patch keeps the zone's lists when the room's
        # json gives none): one on a tile the player reaches runs whatever this room's script of that number is (or none)
        if self.vanilla is not None and not outdoor and z < len(self.vanilla.hdr):
            starts = [(w['tile_x'] + a + dx, w['tile_z'] + b + dz) for w in e['warps'] for a in range(max(1, w['w'])) for b in range(max(1, w['h']))
                      for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))]
            reach_set = g.reach(starts)
            ve = self.vanilla.entities(z)
            vt = {(t['script'], t['x'], t['z'], t['work'], t['value']) for t in ve['triggers']}
            vs = {(s['script'], s['x'], s['z']) for s in ve['signs']}
            for i, tr in enumerate(e['triggers']):
                if (tr['script'], tr['x'], tr['z'], tr['work'], tr['value']) not in vt or tr['w'] >= 0x100: continue
                reach = [(tr['x'] + a, tr['z'] + b) for a in range(max(1, tr['w'])) for b in range(max(1, tr['h']))
                         if (tr['x'] + a, tr['z'] + b) in reach_set and any(abs(h - tr['y']) <= 2 for h in g.heights((tr['x'] + a, tr['z'] + b)))]
                if reach:
                    self.say(z, 'ent', f"Black 2's own trigger {i} (script {tr['script']}, work {tr['work']:#x}=={tr['value']}) is still "
                             f"in the room at {reach[:3]}: stepping there runs this room's script {tr['script']}"
                             + ('' if self.script_exists(z, tr['script']) else ', which does not exist (crash)'))
                else: self.unreached["Black 2 trigger"] += 1
            for i, sg in enumerate(e['signs']):
                if (sg['script'], sg['x'], sg['z']) not in vs: continue
                t = (sg['x'], sg['z'])
                near = [q for q in [(t[0], t[1] + 1), (t[0], t[1] - 1), (t[0] + 1, t[1]), (t[0] - 1, t[1])] if q in reach_set]
                if near and any(-2 <= sg['y'] - h < 2 for q in near for h in g.heights(q)):
                    self.say(z, 'ent', f"Black 2's own sign {i} (script {sg['script']}) is still in the room at {t}: reading it runs "
                             f"this room's script {sg['script']}" + ('' if self.script_exists(z, sg['script']) else ', which does not exist (crash)'))
                else: self.unreached["Black 2 sign"] += 1
        # script ids of the zone's events and map scripts
        def tiles(kind, o):
            if kind == 'trigger': return [(o['x'] + a, o['z'] + b) for a in range(max(1, o['w'])) for b in range(max(1, o['h'])) if o['w'] < 0x100]
            if kind == 'sign': return [(o['x'] + a, o['z'] + b) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))]
            return [(o['x'] + a, o['z'] + b) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))]
        for kind, lst in (('person', e['npcs']), ('sign', e['signs']), ('trigger', e['triggers'])):
            for i, o in enumerate(lst):
                if o['script'] and not self.script_exists(z, o['script']):
                    # (rooms keep Black 2's own triggers when their json gives none: off the room's tiles they never fire)
                    reach = [t for t in tiles(kind, o) if g.kind(t) and (outdoor or t in g.reach(
                        [(w['tile_x'] + dx, w['tile_z'] + dz) for w in e['warps'] for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))]))]
                    if reach:
                        self.say(z, 'id', f"{kind} {i} at ({o['x']},{o['z']}) runs script {o['script']}, which does not exist "
                                 f"(the game crashes when it starts): reachable from {reach[:3]}")
                    else: self.unreached['no-script ' + kind] += 1
        for kind, sid in R.map_scripts(z):
            if sid and not self.script_exists(z, sid): self.say(z, 'id', f'{kind} script {sid} resolves to no script')

    def script_exists(self, z, sid):
        r = self.rom.resolve(z, sid)
        if r is None: return False
        f, k, _ = r
        if k is None: return True
        sf = self.rom.script_file(f, z)
        return sf is not None and 0 <= k < len(sf.entries)

    # ---------------------------------------------------------------------------------------------- scripts
    def check_scripts(self, z):
        """Instruction-level checks of the zone's script file: texts, ids, map changes, positions, alignment."""
        R, W = self.rom, self.world
        n = R.hdr[z]['scripts']
        sf = R.script_file(n, z)
        if sf is None:
            if R.hdr[z]['scripts'] < len(R.scr) and len(R.scr[n]) > 4: self.say(z, 'id', f'script file {n} does not decode')
            return
        texts = R.texts(R.hdr[z]['text'])
        if sf.errors: self.say(z, 'id', f'script file {n}: {dict(sf.errors)}', (n, None))
        for pc, (cmd, args, end) in sorted(sf.instructions.items()):
            self.check_instr(z, n, sf, pc, cmd, args, texts)
        for start in sf.movements:
            if start % 4: self.say(z, 'align', f'script file {n}: movement list at {start:#x} is not 4-byte aligned', (n, start))

    def check_instr(self, z, n, sf, pc, cmd, args, texts):
        R, W = self.rom, self.world
        name = cmd.name
        # texts
        files = [v for m, v in zip(cmd.meanings, args) if m == 'message_file']
        if texts is not None and (not files or files[0] == FS.MSGFILE_SCRIPT):
            for m, v in zip(cmd.meanings, args):
                if m == 'message' and not VAR0 <= v < 0xC000 and v >= len(texts):
                    self.say(z, 'text', f'script file {n}: {name} message {v} but the text file {R.hdr[z]["text"]} has {len(texts)} lines', (n, pc))
        # script ids
        if name in ('RTCallGlobal', 'RTCallGlobalAsync', 'RTReserveScript') and not VAR0 <= args[0] < 0xC000:
            if (name != 'RTReserveScript' or args[0] >= 2000) and not self.script_exists(z, args[0]):   # (a reserved local
                # script runs in the zone of the next map change: check_arrivals)
                self.say(z, 'id', f'script file {n}: {name} {args[0]} resolves to no script', (n, pc))
        # map changes
        if name in MAPCHANGE:
            iz, ix, iz2, iy = MAPCHANGE[name]
            self.check_arrival(z, n, pc, name, args[iz], args[ix], args[iz2], args[iy] if iy is not None else None)
        # positions set by scripts
        if name == 'ObjInitNPCGPos':
            idx, d, x, y, zz = args
            npcs = R.entities(z)['npcs']
            if not any(VAR0 <= v < 0xC000 for v in (idx, x, zz)) and idx < len(npcs):
                self.check_tile(z, (x, zz), f"script file {n}: ObjInitNPCGPos moves person {idx} (uid {npcs[idx]['uid']}) to {(x, zz)}", (n, pc))
            elif idx >= len(npcs) and not VAR0 <= idx < 0xC000:
                self.say(z, 'id', f'script file {n}: ObjInitNPCGPos person {idx} but the zone has {len(npcs)}', (n, pc))
        if name == 'ActorSetGPos':
            a, x, y, zz, d = args
            if not any(VAR0 <= v < 0xC000 for v in (x, zz)):
                self.check_tile(z, (x, zz), f'script file {n}: ActorSetGPos {a} to {(x, zz)}', (n, pc))

    def check_tile(self, z, t, what, where):
        g = self.world.geo(z)
        if g is None: return
        if not g.inside(t): self.say(z, 'ent', f'{what}: outside the built tiles', where); return
        if g.kind(t) is None and not any(ag.kind(t) for m, ag in g.alts):
            c = g.recs(t)[0]; self.say(z, 'ent', f'{what}: a solid tile (class {c[2]:#x} flags {c[3]:#x})', where)

    def check_arrival(self, z, n, pc, name, tz, x, zt, y):
        W = self.world
        if any(VAR0 <= v < 0xC000 for v in (tz, x, zt)): return
        what = f'script file {n}: {name} {tz} ({W.name(tz)}) ({x},{zt})'
        if tz >= len(self.rom.hdr):
            self.say(z, 'mapc', f'{what}: no such zone', (n, pc)); return
        g = W.geo(tz)
        if g is None:
            if tz in W.hoenn_zones(): self.say(z, 'mapc', f'{what}: target zone not built in this world/interiors', (n, pc))
            return
        t = (x, zt)
        if not g.inside(t): self.say(z, 'mapc', f'{what}: outside the target zone\'s built tiles', (n, pc)); return
        k = g.kind(t)
        if k is None and not any(ag.kind(t) for m, ag in g.alts):
            c = g.recs(t)[0]
            # a door / warp tile is solid on purpose (the player arrives on it and steps out)
            if not self.is_warp_tile(tz, t):
                self.say(z, 'mapc', f'{what}: lands on a solid tile (class {c[2]:#x} flags {c[3]:#x})', (n, pc))
        if W.outdoor(tz):
            zz = g.zone_at(t)
            if zz is not None and zz != tz:
                self.say(z, 'mapc', f'{what}: lands on zone {zz}\'s tiles ({W.name(zz)}): the game swaps zone at once', (n, pc))

    def is_warp_tile(self, z, t):
        for w in self.rom.entities(z)['warps']:
            if w['tile_x'] <= t[0] < w['tile_x'] + max(1, w['w']) and w['tile_z'] <= t[1] < w['tile_z'] + max(1, w['h']):
                return True
        return False

    # ---------------------------------------------------------------------------------------------- windows (msg)
    def window_analysis(self, sf, entry_pcs, on_event, global_opens):
        """Follows each entry with the open windows ('' closed; letters of OPEN; 'k' = the balloon was waited on with
        LastKeyWait, 'y' = with YesNoWin, since its last line); calls on_event(pc, cmd, args, state) at every command.
        Calls (VMCall/VMCallIf) are followed with the caller's state (memoised per (target, state)); RTCallGlobal leaves
        the state as it is."""
        memo = {}
        def step(st, nm):
            if nm in OPEN: return ''.join(sorted((set(st) - {'k', 'y'}) | {OPEN[nm]}))
            if nm in CLOSE:
                left = ''.join(c for c in st if c not in CLOSE[nm])
                return left if 'B' in left else left.replace('k', '').replace('y', '')
            if nm == 'LastKeyWait' and 'B' in st: return ''.join(sorted(set(st) | {'k'}))
            if nm == 'YesNoWin' and 'B' in st: return ''.join(sorted(set(st) | {'y'}))
            return st
        def run(start, state, depth=0):
            key = (start, state)
            if key in memo: return memo[key]
            memo[key] = set()                       # (recursion guard)
            exits = set()
            todo, seen = [(start, state)], set()
            while todo:
                pc, st = todo.pop()
                while True:
                    if (pc, st) in seen: break
                    seen.add((pc, st))
                    ins = sf.instructions.get(pc)
                    if ins is None: break
                    cmd, args, end = ins
                    nm = cmd.name
                    on_event(pc, cmd, args, st)
                    st = step(st, nm)
                    if nm == 'VMReturn': exits.add(st); break
                    if nm in ('VMHalt', 'RTEndGlobal', 'CallTrainerLose'): break
                    if nm == 'VMJump': pc = args[0]; continue
                    if nm == 'VMJumpIf': todo.append((args[1], st)); pc = end; continue
                    if nm in ('VMCall', 'VMCallIf'):
                        tgt = args[0] if nm == 'VMCall' else args[1]
                        if depth < 12:
                            outs = run(tgt, st, depth + 1)
                            if nm == 'VMCallIf': todo.append((end, st))
                            for o in outs: todo.append((end, o))
                            break
                    pc = end
            memo[key] = exits
            return exits
        for pc in entry_pcs: run(pc, '')

    def global_opens_window(self, sid):
        """Does global script sid open a message window (from a closed state)?"""
        if sid in self.global_opens: return self.global_opens[sid]
        self.global_opens[sid] = False
        r = self.rom.resolve(0, sid) if sid >= 2000 else None
        if r and r[1] is not None:
            sf = self.rom.script_file(r[0])
            if sf and 0 <= r[1] < len(sf.entries):
                found = []
                def ev(pc, cmd, args, st):
                    if cmd.name in OPEN: found.append(1)
                self.window_analysis(sf, [sf.entries[r[1]]], ev, self.global_opens)
                self.global_opens[sid] = bool(found)
        return self.global_opens[sid]

    def check_windows(self, z, file_no, sf, stats=None):
        """A balloon a script waited on (h_msgbox / h_msgbox_actor: ParentActorMsg/ActorMsg + LastKeyWait) and did not
        close before an info/system window or a global script that opens its own window (h_giveitem's 2805): ch4's crash
        (ARM9 undefined instruction), a pattern Black 2's own 1,289 script files never use after LastKeyWait (--vanilla).
        A movement after such a balloon is not reported: Black 2 never does it either and ch8b's Slateport interview
        crashed on one, but the Rustboro boy's turn after his line (RB_LittleBoy, the talked-to speaker) plays fine
        (script_check 2026-10-08, screenshots/script_check/), as do the tested scenes with the same order (Wally's
        tutorial, Room 9, Route 128). A balloon still printing (Black 2's nurse) or answered with YesNoWin is how Black 2's
        own scripts do it."""
        def ev(pc, cmd, args, st):
            nm = cmd.name
            if stats is not None and 'B' in st:
                key = nm if nm != 'RTCallGlobal' else f'RTCallGlobal {args[0]}{" (opens a window)" if self.global_opens_window(args[0]) else ""}'
                stats[(st, key)] += 1
            if 'B' not in st or 'k' not in st: return
            bad = None
            if nm in ('SystemMsg', 'SystemMsgAsync', 'InfoMsg', 'MsgPlaceSign'): bad = f'an info/system window ({nm})'
            elif nm == 'RTCallGlobal' and not VAR0 <= args[0] < 0xC000 and self.global_opens_window(args[0]):
                bad = f'global script {args[0]} that opens its own window' + (' (h_giveitem)' if args[0] == 2805 else '')
            if bad and stats is None:
                self.say(z, 'msg', f'script file {file_no}: a balloon waited on (LastKeyWait) is still open at {bad}', (file_no, pc))
        self.window_analysis(sf, sf.entries, ev, self.global_opens)

    # ---------------------------------------------------------------------------------------------- paths
    def run_paths(self, z, file_no, sf, entry, starts, why):
        """Follows script entry `entry` of sf with actor positions `starts` ({actor: tile}); checks every step."""
        W, R = self.world, self.rom
        g = W.geo(z)
        if g is None: return
        npcs = R.entities(z)['npcs']
        static = self.static_npcs(z)
        model = {n['uid']: n['model'] for n in npcs}
        home = {n['uid']: (n['x'], n['z']) for n in npcs}
        budget = [6000]
        seen = set()
        stack = [(sf.entries[entry], dict(starts), {}, (), None, False, None)]
        while stack and budget[0] > 0:
            pc, pos, works, calls, cmp, hold, reserved = stack.pop()
            while budget[0] > 0:
                budget[0] -= 1
                key = (pc, tuple(sorted(pos.items())), tuple(sorted(works.items())), calls, cmp, hold)
                if key in seen: break
                seen.add(key)
                ins = sf.instructions.get(pc)
                if ins is None: break
                cmd, args, end = ins
                nm = cmd.name
                isvar = lambda v: VAR0 <= v < 0xC000
                val = lambda v: works.get(v) if isvar(v) else v
                nxt = end
                if nm in ('VMHalt', 'RTEndGlobal', 'CallTrainerLose'): break
                if nm == 'VMReturn':
                    if not calls: break
                    nxt, calls = calls[-1], calls[:-1]
                elif nm == 'VMJump': nxt = args[0]
                elif nm in ('VMJumpIf', 'VMCallIf'):
                    c, tgt = args
                    take = None
                    if cmp is not None and c in (0, 1, 2, 3, 4, 5):
                        take = {0: cmp == 0, 1: cmp == 1, 2: cmp == 2, 3: cmp in (0, 1), 4: cmp in (1, 2), 5: cmp != 1}[c]
                    if nm == 'VMJumpIf':
                        if take is None: stack.append((tgt, dict(pos), dict(works), calls, cmp, hold, reserved))
                        elif take: nxt = tgt
                    else:
                        if take is None:
                            stack.append((tgt, dict(pos), dict(works), calls + (end,), cmp, hold, reserved))
                        elif take: nxt, calls = tgt, calls + (end,)
                elif nm == 'VMCall': nxt, calls = args[0], calls + (end,)
                elif nm == 'WorkCmpConst':
                    a = works.get(args[0]); cmp = None if a is None else (0 if a < args[1] else 1 if a == args[1] else 2)
                elif nm == 'WorkCmpWork':
                    a, b = works.get(args[0]), works.get(args[1]); cmp = None if a is None or b is None else (0 if a < b else 1 if a == b else 2)
                elif nm in ('VMStackCmp',): cmp = None
                elif nm == 'WorkSetConst': works[args[0]] = args[1]
                elif nm == 'WorkSet':
                    v = val(args[1])
                    if v is None: works.pop(args[0], None)
                    else: works[args[0]] = v
                elif nm in ('WorkAdd', 'WorkSub'):
                    v = val(args[1])
                    if args[0] in works and v is not None: works[args[0]] = (works[args[0]] + (v if nm == 'WorkAdd' else -v)) & 0xFFFF
                    else: works.pop(args[0], None)
                elif nm == 'PlayerGetGPos':
                    p = pos.get(PLAYER)
                    for v, k in zip(args, (0, 1)):
                        if p is None: works.pop(v, None)
                        else: works[v] = p[k]
                elif nm == 'ActorGetGPos':
                    a = val(args[0]); p = pos.get(a) if a is not None else None
                    for v, k in zip(args[1:], (0, 1)):
                        if p is None: works.pop(v, None)
                        else: works[v] = p[k]
                elif nm in ('FlagSet', 'FlagReset') and args[0] == ZONE_HOLD_FLAG: hold = nm == 'FlagSet'
                elif nm == 'RTReserveScript': reserved = args[0]
                elif nm == 'ActorAdd':
                    a = val(args[0])
                    if a in home: pos[a] = home[a]
                elif nm == 'ActorDelete':
                    a = val(args[0]); pos.pop(a, None)
                elif nm == 'ActorSetGPos':
                    a, x, y, zz = val(args[0]), val(args[1]), val(args[2]), val(args[3])
                    if a is not None and x is not None and zz is not None: pos[a] = (x, zz)
                    elif a is not None: pos.pop(a, None)
                elif nm in MAPCHANGE:
                    iz, ix, iz2, iy = MAPCHANGE[nm]
                    tz, x, zt = val(args[iz]), val(args[ix]), val(args[iz2])
                    if None not in (tz, x, zt) and reserved is not None:
                        self.arrivals.append((tz, x, zt, reserved, f'{W.name(z)} file {file_no}'))
                    break
                elif nm == 'ActorCmdExec':
                    a = val(args[0])
                    if a is not None and a in pos:
                        pos[a] = self.walk(z, g, file_no, sf, pc, a, pos[a], args[1], model.get(a), static, hold, why)
                pc = nxt

    def walk(self, z, g, file_no, sf, pc, actor, p, mv, model, static, hold, why):
        """Applies one movement list to an actor at tile p; reports the first bad step; returns the end tile."""
        data = sf.data
        pos = mv
        who = 'the player' if actor == PLAYER else f'actor {actor}'
        water_obj = model in WATER_OBJECTS
        while pos + 4 <= len(data):
            code, count = struct.unpack_from('<HH', data, pos); pos += 4
            if code == FS.MOVEMENT_END: break
            if code not in MOVES: continue
            dx, dz, tiles, kind = MOVES[code]
            for _ in range(count):
                q = (p[0] + dx * tiles, p[1] + dz * tiles)
                bad = None
                k = g.kind(q)
                if not g.inside(q): bad = 'outside the built tiles'
                elif k is None and not water_obj and not any(ag.kind(q) for m, ag in g.alts) and not self.is_warp_tile(z, q):
                    c = g.recs(q)[0]; bad = f'a solid tile (class {c[2]:#x} flags {c[3]:#x})'
                elif k == 'surf' and not water_obj and kind == 'walk' and actor != PLAYER: bad = 'water'
                elif k == 'land' and water_obj: bad = 'land (a boat)'
                elif kind == 'walk' and g.kind(p) and k:
                    h0, h1 = g.heights(p), g.heights(q)
                    if h0 and h1 and min(abs(a - b) for a in h0 for b in h1) >= 20:
                        bad = f'a height step {h0[0]:.0f} -> {h1[0]:.0f} (a cliff)'
                if bad is None and q in static:
                    others = [n for n in static[q] if n['uid'] != actor]
                    if others:
                        o = others[0]
                        bad = f"uid {o['uid']} (sprite {o['model']}{', berry tree' if o['uid'] in BERRY_UIDS else ''}{', 3D object' if o['model'] in WATER_OBJECTS else ''})"
                if bad is None and actor == PLAYER and self.world.outdoor(z) and not hold:
                    zz = g.zone_at(q)
                    if zz is not None and zz != z:
                        self.say(z, 'zone', f'script file {file_no}: the player walks from {p} onto zone {zz}\'s tile {q} ({self.world.name(zz)}) without h_zone_hold ({why})', (file_no, mv))
                if bad:
                    self.say(z, 'path', f'script file {file_no}: {who} steps from {p} onto {q}: {bad} ({why})', (file_no, mv))
                    return q
                p = q
        return p

    def check_paths(self, z):
        R = self.rom
        n = R.hdr[z]['scripts']
        sf = R.script_file(n, z)
        if sf is None: return
        e = R.entities(z)
        npc_pos = {o['uid']: (o['x'], o['z']) for o in e['npcs']}
        done = set()
        for i, tr in enumerate(e['triggers']):
            r = R.resolve(z, tr['script'])
            if not r or r[0] != n or r[1] is None or not 0 <= r[1] < len(sf.entries): continue
            for a in range(max(1, tr['w'])):
                for b in range(max(1, tr['h'])):
                    st = dict(npc_pos); st[PLAYER] = (tr['x'] + a, tr['z'] + b)
                    self.run_paths(z, n, sf, r[1], st, f'trigger {i} script {tr["script"]} from {st[PLAYER]}')
            done.add(r[1])
        for k in range(len(sf.entries)):
            if k in done: continue
            self.run_paths(z, n, sf, k, dict(npc_pos), f'script {k + 1}')

    def check_arrivals(self):
        """Arrival scripts reserved before a scripted map change (boats, ferries, cable car, h_warp_scene): their
        movements from the arrival tile."""
        R = self.rom
        done = set()
        for tz, x, zt, sid, src in list(self.arrivals):
            if (tz, x, zt, sid) in done or sid >= 2000 or tz >= len(R.hdr): continue
            done.add((tz, x, zt, sid))
            r = R.resolve(tz, sid)
            sf = R.script_file(r[0], tz) if r else None
            if not sf or not 0 <= r[1] < len(sf.entries): continue
            st = {o['uid']: (o['x'], o['z']) for o in R.entities(tz)['npcs']}; st[PLAYER] = (x, zt)
            self.run_paths(tz, r[0], sf, r[1], st, f'arrival script {sid} after a map change from {src}, player at {(x, zt)}')

    def run(self):
        zones = [z for z in self.world.hoenn_zones() if not self.only or z in self.only]
        files_done = set()
        for z in zones:
            if z >= len(self.rom.hdr): continue
            self.check_entities(z)
            n = self.rom.hdr[z]['scripts']
            if n in files_done: continue
            files_done.add(n)
            self.check_scripts(z)
            sf = self.rom.script_file(n, z)
            if sf is not None and 'msg' in self.kinds: self.check_windows(z, n, sf)
            if {'path', 'zone'} & set(self.kinds): self.check_paths(z)
        if {'path', 'zone'} & set(self.kinds): self.check_arrivals()


# ------------------------------------------------------------------------------------------------------ by design
V151_SCENES = ("a scene of v15.1 played through by its chapter (people leave through a door, a gap or past a counter, or "
               "start where a zone init moved them): the same finding on release/HoennB2_v15.1.nds")
ACCEPT = [   # (zone name regex, kind regex, message regex, why); checked on the v15.2 build (script_check 2026-10-08)
    ('Route1(0[2-4]|1[0-9]|2[0-3])', 'ent', r'uid 4\d\d \(sprite (90|102|106|111|113|114|180), script 82\d\d, .*on a solid tile',
     'berry trees (data/story/berry_spots.json) stand on their soft-soil tile, which the world makes solid'),
    ('.*', 'ent', r'\(sprite (4509|4510|4511|4512|4379|356|206|251), script \d+, ',
     'legendaries in their pools / on their perch (Kyogre, Lati@s, Ho-Oh), the cable car at its station, the Regi '
     'caves\' sealing rocks on the cave mouths, the bedroom clock: talked to or watched, never walked to'),
    ('Route111|LavaridgeTown|Route105|Route120', 'ent', r'(uid 10[234] \(sprite (53|15|29)|uid 108 \(sprite 162|uid 1[46]0 \(sprite 206).*solid',
     "people who step out of a door in a scene (the Winstrates, the rival at Lavaridge's Gym) and the Regi rocks (outdoor_check)"),
    ('Route101', 'ent', r'uid 1[01] \(', "Route 101's rescue-scene actors on the ledge row (outdoor_check)"),
    ('SlateportCity_OceanicMuseum_2F', 'ent', r'uid [234] .* at \(7, 2\)', 'Archie and the grunts come up the stairs in the scene'),
    ('MossdeepCity_StevensHouse', 'ent', r'uid [23] \(sprite 110', "Beldum's and the Dive ball on Steven's table (talked to across it)"),
    ('Route113', 'ent', r'trigger \d+ \(script 1\) at \(\d+,62\) 1x13', "the Soot Sack's ash columns run over the route's rocks too (ch4)"),
    ('MeteorFalls_1F_[12]R', 'ent', r'sign 0 .*outside the built tiles', "Sapphire's own off-map signs (caves_check)"),
    ('ShoalCave_LowTideInnerRoom', 'ent', r'ObjInitNPCGPos .* to \(0, 0\)', 'the tide items are moved off the map while taken'),
    ('CableCarStation', 'ent|path', r'ObjInitNPCGPos moves person 0 \(uid 1\)|actor 1 steps|uid 1 \(sprite 17\)',
     "the attendant behind the counter: the zone init moves him (VAR_CABLE_CAR_STATION_STATE), which this check does not follow (ch5, tested)"),
    ('.*', 'path', r'(actor|the player) .*onto .*: water .*(Board|script [124]\b|trigger)|Mv_R128_ArchieLeaves|actor 102 steps from \(269',
     "people step onto Mr. Briney's boat, the submarine or a legendary's pool (the scene then hides them)"),
    ('SeafloorCavern_Room9|CaveOfOrigin_B4F|SouthernIsland_Interior|NavelRock_Top|MagmaHideout_4F', 'path', r'actor 10?[123]? steps',
     'Kyogre / Groudon rise out of their pool (Groudon in the Magma Hideout 4F: its lava pool, 0718_room_MagmaHideout_4F.s), Lati@s and Ho-Oh fly down to the player (103: the Emerald Latias, scenes/emerald/SouthernIsland_Interior.inc)'),
    ('SlateportCity_Harbor', 'path', r'actor [67] steps .* onto \([89], 7\)', 'the grunts board the submarine (then removed)'),
    ('EverGrandeCity_ChampionsRoom$', 'path', r'actor\ 2\ steps\ from\ \(7,\ 5\)\ onto\ \(7,\ 4\)',
     V151_SCENES),
    ('FortreeCity$', 'path', r'actor\ 107\ steps\ from\ \(393,\ 68\)\ onto\ \(394,\ 68\)',
     V151_SCENES),
    ('LavaridgeTown$', 'path', r'actor\ 107\ steps\ from\ \(201,\ 136\)\ onto\ \(202,\ 136\)',
     V151_SCENES),
    ('LittlerootTown$', 'path', r'actor\ 1\ steps\ from\ \(187,\ 360\)\ onto\ \(188,\ 360\)|actor\ 1\ steps\ from\ \(187,\ 362\)\ onto\ \(188,\ 362\)|actor\ 1\ steps\ from\ \(188,\ 360\)\ onto\ \(188,\ 361\)|actor\ 1\ steps\ from\ \(188,\ 362\)\ onto\ \(188,\ 363\)|actor\ 1\ steps\ from\ \(188,\ 363\)\ onto\ \(189,\ 363\)|actor\ 104\ steps\ from\ \(167,\ 361\)\ onto\ \(167,\ 360\)|actor\ 104\ steps\ from\ \(168,\ 361\)\ onto\ \(167,\ 361\)|actor\ 104\ steps\ from\ \(180,\ 361\)\ onto\ \(180,\ 360\)',
     V151_SCENES),
    ('LittlerootTown_BrendansHouse_2F$', 'path', r'actor\ 1\ steps\ from\ \(7,\ 3\)\ onto\ \(7,\ 2\)',
     V151_SCENES),
    ('LittlerootTown_MaysHouse_2F$', 'path', r'actor\ 1\ steps\ from\ \(3,\ 3\)\ onto\ \(3,\ 2\)',
     V151_SCENES),
    ('LittlerootTown_ProfessorBirchsLab$', 'path', r'actor\ 0\ steps\ from\ \(9,\ 9\)\ onto\ \(10,\ 9\)',
     V151_SCENES),
    ('MtChimney$', 'path', r'actor\ 101\ steps\ from\ \(17,\ 24\)\ onto\ \(17,\ 25\)|actor\ 101\ steps\ from\ \(18,\ 20\)\ onto\ \(18,\ 21\)|actor\ 101\ steps\ from\ \(18,\ 23\)\ onto\ \(17,\ 23\)|actor\ 101\ steps\ from\ \(19,\ 16\)\ onto\ \(18,\ 16\)|actor\ 101\ steps\ from\ \(19,\ 17\)\ onto\ \(18,\ 17\)|actor\ 101\ steps\ from\ \(19,\ 23\)\ onto\ \(18,\ 23\)|actor\ 101\ steps\ from\ \(20,\ 16\)\ onto\ \(19,\ 16\)|actor\ 101\ steps\ from\ \(20,\ 17\)\ onto\ \(20,\ 16\)|actor\ 101\ steps\ from\ \(20,\ 18\)\ onto\ \(20,\ 19\)',
     V151_SCENES),
    ('OldaleTown$', 'path', r'actor\ 1\ steps\ from\ \(180,\ 305\)\ onto\ \(181,\ 305\)|actor\ 1\ steps\ from\ \(181,\ 307\)\ onto\ \(181,\ 306\)',
     V151_SCENES),
    ('PetalburgCity$', 'path', r'actor\ 3\ steps\ from\ \(101,\ 307\)\ onto\ \(100,\ 307\)|actor\ 3\ steps\ from\ \(104,\ 306\)\ onto\ \(105,\ 306\)|actor\ 3\ steps\ from\ \(106,\ 305\)\ onto\ \(107,\ 305\)|actor\ 3\ steps\ from\ \(107,\ 305\)\ onto\ \(107,\ 306\)',
     V151_SCENES),
    ('PetalburgCity_Gym$', 'path', r'actor\ 10\ steps\ from\ \(5,\ 111\)\ onto\ \(5,\ 112\)',
     V151_SCENES),
    ('Route111$', 'path', r'actor\ 133\ steps\ from\ \(257,\ 86\)\ onto\ \(257,\ 87\)',
     V151_SCENES),
    ('Route119_WeatherInstitute_2F$', 'path', r'actor\ 5\ steps\ from\ \(20,\ 7\)\ onto\ \(21,\ 7\)',
     V151_SCENES),
    ('RustboroCity$', 'path', r'actor\ 160\ steps\ from\ \(70,\ 197\)\ onto\ \(70,\ 196\)',
     V151_SCENES),
    ('RusturfTunnel$', 'path', r'actor\ 5\ steps\ from\ \(4,\ 4\)\ onto\ \(3,\ 4\)',
     V151_SCENES),
    ('SootopolisCity$', 'path', r'actor\ 105\ steps\ from\ \(50,\ 43\)\ onto\ \(50,\ 44\)|actor\ 105\ steps\ from\ \(50,\ 44\)\ onto\ \(49,\ 44\)|actor\ 110\ steps\ from\ \(48,\ 42\)\ onto\ \(48,\ 41\)|actor\ 110\ steps\ from\ \(49,\ 43\)\ onto\ \(49,\ 44\)|actor\ 110\ steps\ from\ \(49,\ 44\)\ onto\ \(48,\ 44\)',
     V151_SCENES),
    ('Route101', 'path|ent', r'onto \(175, 350\)|actor 10 steps|trigger 7 \(script 12',
     "the opening's rescue on Route 101 (hand-made, v15.1 the same; the opening is played every release)"),
    ('Route1(19|20)$', 'ent', r'sign \d \(script 82\d\d', 'a berry spot read before the trees: its tree (an NPC on the spot) is talked to now'),
    ('Route104$', 'path', r'player steps from \(60, 292\) onto \(60, 293\): a height step 16 -> -8',
     "boarding Mr. Briney's boat from the jetty on posts (overworld_polish, v15.2): one step down onto the boat, then the "
     "player is hidden and the boat sails (played in the emulator: screenshots/script_check/06_*)"),
    ('Route119_WeatherInstitute_1F$', 'ent', r'sign 0 \(script 5, dir 4\) at \(1, 3\)',
     "the bed's top-left tile (Sapphire (0,2)): Sapphire lists all four bed tiles, this one touches no floor there either; "
     "the bed is read from its other three tiles"),
    ('BattleTower_Elevator$', 'path', r'script file 1865: the player steps from \(2, 7\) onto \(2, 6\): uid 1 |'
                                      r'script file 1865: the player steps from \(3, 7\) onto \(3, 8\): a solid tile',
     "Sapphire's elevator ride (battle_tower, v16): the attendant steps up out of the player's way as the player starts "
     "(both movements run together); the checker keeps her on (2,6), so it also sees the player's way out start from "
     "(2,7). Played in the emulator: the player rides at (2,5) and leaves by (3,7) (notes/BATTLE_TOWER.md)"),
    ('BattleTower_Corridor$', 'path', r'script file 1863: (the player|actor 1) steps from \((13|16), 2\) onto \(\2, 1\): a solid tile',
     "Sapphire's walk into the Lv. 50 / Lv. 100 Battle Room door (battle_tower, v16): the script opens the door prop, "
     "the attendant and then the player walk into it, are hidden and the map changes (played in the emulator, "
     "notes/BATTLE_TOWER.md; the attendant stands beside the player on row 1 since walk_sweep, screenshots/walk_sweep/corridor_*)"),
    ('BattleTower_Corridor$', 'path', r'script file 1863: the player steps from \(9, 2\) onto \(10, 2\): uid 1',
     "the attendant walks ahead of the player (walk_sweep 2026-10-12: she stands beside the arrival tile, as Sapphire's "
     "does after its door step); both movements run together, the checker keeps her on (10,2) (played in the emulator: "
     "she leads, the player follows one tile behind, screenshots/walk_sweep/corridor_*)"),
    ('SafariZone_Southeast$', 'path', r'script file 80: actor 101 steps from \(96, 98\) onto \(97, 98\): a solid tile',
     "the camper's walk back in front of the door (Sapphire's walk_right, walk_sweep 2026-10-12): the zone init puts him "
     "on (95,98) beside it whenever the arrival scene runs (VAR_SAFARI_ZONE_STATE 2); the checker starts him on his "
     "template tile (96,98) (played in the emulator: (95,98) -> (96,98), screenshots/walk_sweep/safari_*)"),
]

def accepted(zone_name, kind, msg):
    return next((why for zn, k, rx, why in ACCEPT if re.match(f'({k})$', kind) and re.search(zn, zone_name) and re.search(rx, msg)), None)


def vanilla_stats(rom_path):
    """(open window, command) pairs in Black 2's own scripts (every file of the unmodified dump)."""
    R = Rom(rom_path)
    C = Checker(R, None, {'msg'})
    stats = Counter()
    for n in range(len(R.scr)):
        sf = R.script_file(n)
        if sf is None: continue
        C.check_windows(None, n, sf, stats)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--world', default=os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'))
    ap.add_argument('--dir', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--kinds', default='ent,mapc,path,zone,msg,text,id,align')
    ap.add_argument('--zone', type=int, nargs='*')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--vanilla', metavar='VANILLA_NDS')
    ap.add_argument('--labels', action='store_true', help='name the source label of each finding (assembles the sources again)')
    a = ap.parse_args()
    if a.vanilla:
        st = vanilla_stats(a.vanilla)
        for (s, c), k in sorted(st.items(), key=lambda kv: (kv[0][0], -kv[1])):
            if re.match(r'ActorCmdExec|SystemMsg|InfoMsg|MsgPlaceSign|RTCallGlobal', c): print(f'vanilla: open {s:4s} at {c}: {k}')
        return
    R = Rom(a.rom); W = World(a.world, a.dir)
    V = Rom(VANILLA) if os.path.exists(VANILLA) else None
    C = Checker(R, W, set(a.kinds.split(',')), set(a.zone or []), V)
    C.run()
    labels = {}
    def where(w):
        if not w or not a.labels or w[1] is None: return ''
        f, pc = w
        if f not in labels: labels[f] = labels_for(f)
        lab, src = labels[f]
        best = max((o for o in lab if o <= pc), default=None)
        return f'  [{os.path.basename(src) if src else f"file {f}"}: {lab[best]}+{pc - best:#x}]' if best is not None else ''
    tot, acc = Counter(), Counter()
    for z, kind, msg, w in C.out:
        zn = f'zone {z} {W.name(z)}'
        why = accepted(zn, kind, msg)
        if why: acc[kind] += 1
        else: tot[kind] += 1
        if not why or a.all: print(f'{zn}: ({kind}) {msg}{where(w)}' + (f'  [accepted: {why}]' if why else ''))
    ks = a.kinds.split(',')
    if C.unreached: print('not findings (nobody reaches them):', dict(C.unreached))
    print('script_check (open):', ', '.join(f'{k} {tot[k]}' for k in ks), '| accepted:', ', '.join(f'{k} {acc[k]}' for k in ks if acc[k]) or 'none')


if __name__ == '__main__':
    main()
