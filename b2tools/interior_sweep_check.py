"""Interior glitch sweep (interior_sweep agent, notes/INTERIORS_PLAN.md): static checks over every built room and the
zones a built ROM gives them.

    python3 interior_sweep_check.py rooms [NAME ...]     geometry: layered surfaces < 2 units apart (terrain + furniture,
                                                         same-facing parallel faces that overlap), furniture through
                                                         walls, furniture overlapping furniture, furniture over walkable
                                                         tiles, walkable tiles with no floor (holes), people standing in
                                                         furniture/walls/void, arrival tiles that are boxed in
    python3 interior_sweep_check.py zones ROM            the ROM's zone data for every room zone (data/interiors):
                                                         warps both ways (room -> dest -> back), arrival tiles, script and
                                                         message numbers, place name and banner, music, camera box
Rooms are read from HOENN_INTERIORS_DIR (default work/agents/interior_sweep/interiors); furniture models via
preview_interior.py's apicula cache (<rooms>/_models). Output: one line per finding, "ROOM: kind: detail".
"""
import os, sys, json, glob, math, struct
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ.setdefault('HOENN_INTERIORS_DIR', os.path.join(ROOT, 'work', 'agents', 'interior_sweep', 'interiors'))
ROOMS_DIR = os.environ['HOENN_INTERIORS_DIR']
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import models_interior as mi                                           # noqa: E402
import preview_interior as pv                                          # noqa: E402

GAP = 2.0                     # Black 2 keeps layered surfaces >= 2 units apart (melonDS flickers closer)
INTERIORS = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']

# ------------------------------------------------------------------------------------------------ NitroFS reader
def nds_file(rom, path):
    """Bytes of one NitroFS file ('a/0/0/8') of an .nds (FNT at header 0x40, FAT at 0x48)."""
    with open(rom, 'rb') as f:
        hdr = f.read(0x50)
        fnt_off, fnt_size, fat_off, fat_size = struct.unpack_from('<IIII', hdr, 0x40)
        f.seek(fnt_off); fnt = f.read(fnt_size)
        def lookup(dir_id, parts):
            sub, first, _ = struct.unpack_from('<IHH', fnt, 8 * (dir_id & 0xFFF))
            fid, p = first, sub
            while True:
                t = fnt[p]; p += 1
                if t == 0: raise KeyError(path)
                name = fnt[p:p + (t & 0x7F)].decode(); p += t & 0x7F
                if t & 0x80:
                    did = struct.unpack_from('<H', fnt, p)[0]; p += 2
                    if name == parts[0]: return lookup(did, parts[1:])
                else:
                    if name == parts[0] and len(parts) == 1: return fid
                    fid += 1
        fid = lookup(0xF000, path.split('/'))
        f.seek(fat_off + 8 * fid); s, e = struct.unpack('<II', f.read(8))
        f.seek(s); return f.read(e - s)

def nds_narc(rom, arc):
    import narcio
    from narc import read_narc
    return read_narc(nds_file(rom, f'a/{arc // 100}/{arc // 10 % 10}/{arc % 10}'))

# ------------------------------------------------------------------------------------------------ geometry helpers
def tri_normal(t):
    n = np.cross(t[1] - t[0], t[2] - t[0]); l = np.linalg.norm(n)
    return (n / l, l / 2) if l > 1e-9 else (None, 0)

def clip(poly, a, b):
    """Sutherland-Hodgman: part of convex poly (2D points) left of edge a->b."""
    out = []
    side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    for i, cur in enumerate(poly):
        prv = poly[i - 1]; sc, sp = side(cur), side(prv)
        if (sc >= 0) != (sp >= 0):
            t = sp / (sp - sc); out.append((prv[0] + (cur[0] - prv[0]) * t, prv[1] + (cur[1] - prv[1]) * t))
        if sc >= 0: out.append(cur)
    return out

def area2d(poly):
    return abs(sum(poly[i - 1][0] * p[1] - p[0] * poly[i - 1][1] for i, p in enumerate(poly))) / 2

def overlap_area(p, q):
    """Overlap of two triangles (2D, any winding)."""
    if area2d(p) < 1e-9 or area2d(q) < 1e-9: return 0.0
    s = lambda t: (t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) - (t[1][1] - t[0][1]) * (t[2][0] - t[0][0])
    if s(q) < 0: q = [q[0], q[2], q[1]]
    poly = list(p)
    for i in range(3):
        poly = clip(poly, q[i], q[(i + 1) % 3])
        if len(poly) < 3: return 0.0
    return area2d(poly)

def visible(n):
    """Faces the camera can see (it looks north and down): up, south, east and west faces."""
    return n[1] > 0.3 or n[2] > 0.3 or abs(n[0]) > 0.7

# ------------------------------------------------------------------------------------------------ one room
class Checked:
    def __init__(self, name):
        self.name = name
        self.d = os.path.join(ROOMS_DIR, name)
        self.meta = json.load(open(os.path.join(self.d, 'room.json')))
        self.room = mi.Room(name)
        self.model = self.room.build_terrain()
        self.room.placements()
        self.room.collision()
        self.out = []

    def say(self, kind, msg): self.out.append(f'{self.name}: {kind}: {msg}')

    # faces: (owner, label, tri 3x3) -- owner 'T' = terrain, k = furniture index
    def faces(self):
        F = []
        for mat, tris in self.model.tris.items():
            for t in tris:
                F.append(('T', mat, np.array([v[:3] for v in t], float)))
        self.furn = []
        packs = {m['res']: m['pack'] for m in self.meta['models']}
        names = {m['res']: m['name'] for m in self.meta['models']}
        by_name = {v: k for k, v in names.items()}
        for k, f in enumerate(self.meta['furniture']):
            res = f['m'] if isinstance(f['m'], int) else by_name[f['m']]
            parts = pv.placed(pv.furniture_parts(res, packs[res]), f['pos'], f['rot'])
            pts = np.concatenate([P.reshape(-1, 3) for _, P, _, _ in parts]) if parts else np.zeros((0, 3))
            self.furn.append(dict(k=k, name=names[res], pos=f['pos'], rot=f['rot'], pts=pts,
                                  what=self.room.r['furniture'][k].get('_what', '')))
            for tp, P, UV, C in parts:
                lab = names[res] + '/' + os.path.basename(tp or '-')[:-4]
                for t in P: F.append((k, lab, np.array(t, float)))
        return F

    def layers(self):
        """Same-facing parallel faces of different owners (or terrain with itself) closer than GAP that overlap."""
        F = self.faces()
        buckets = defaultdict(list)
        for owner, lab, t in F:
            n, a = tri_normal(t)
            if n is None or a < 0.05 or not visible(n): continue
            key = tuple(np.round(n, 2))
            d = float(n @ t[0])
            buckets[key].append((d, owner, lab, t, n))
        hits = {}
        for key, items in buckets.items():
            items.sort(key=lambda it: it[0])
            n = items[0][4]
            # 2D basis in the plane
            u = np.cross(n, [0, 1, 0] if abs(n[1]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u); v = np.cross(n, u)
            P2 = [[(float(p @ u), float(p @ v)) for p in it[3]] for it in items]
            box = [(min(p[0] for p in q), max(p[0] for p in q), min(p[1] for p in q), max(p[1] for p in q)) for q in P2]
            j0 = 0
            for i in range(len(items)):
                di, oi, li = items[i][0], items[i][1], items[i][2]
                for j in range(i + 1, len(items)):
                    dj, oj, lj = items[j][0], items[j][1], items[j][2]
                    if dj - di >= GAP: break
                    if oi == oj and (oi != 'T' or abs(dj - di) < 1e-3): continue      # one model's own faces
                    if oi == 'T' and oj == 'T' and abs(dj - di) < 1e-3: continue
                    bi, bj = box[i], box[j]
                    if bi[1] <= bj[0] or bj[1] <= bi[0] or bi[3] <= bj[2] or bj[3] <= bi[2]: continue
                    a = overlap_area(P2[i], P2[j])
                    if a < 0.5: continue
                    k = (oi, li, oj, lj, round(dj - di, 2), key)
                    hits[k] = hits.get(k, 0) + a
        for (oi, li, oj, lj, dd, key), a in sorted(hits.items(), key=lambda kv: -kv[1]):
            if a < 1.0: continue
            name = lambda o, l: l if o == 'T' else f'{l}#{o}({self.furn[o]["what"][:40]})'
            self.say('layers', f'{name(oi, li)} and {name(oj, lj)} {dd} apart (normal {key}), {a:.0f} sq units')

    def local(self, p):            # model units -> local units of the chunk (0..512 per chunk)
        return p[..., 0] + 256, p[..., 2] + 256

    def furniture(self):
        """Furniture through walls, over walkable tiles, inside other furniture."""
        kind = self.room.kind
        NZ, NX = kind.shape
        walk = self.room.walk_chunk
        T = 16
        ox, oz = self.room.ox, self.room.oz
        boxes = []
        for f in self.furn:
            if not len(f['pts']): continue
            x, z = self.local(f['pts']); y = f['pts'][:, 1]
            x0, x1, z0, z1 = x.min(), x.max(), z.min(), z.max()
            boxes.append((f, x0, x1, float(y.min()), float(y.max()), z0, z1))
            f['mask'] = footprint(f, x0, z0, x1, z1)
            flat = y.max() - y.min() < 3 and y.max() < 6
            # through walls: footprint outside the room's floor/wall strip (kind 0), beyond 1.5 units
            X0, X1, Z0, Z1 = int(math.floor(x0 + 1.5)), int(math.ceil(x1 - 1.5)), int(math.floor(z0 + 1.5)), int(math.ceil(z1 - 1.5))
            if X1 > X0 and Z1 > Z0:
                sub = kind[max(Z0, 0):min(Z1, NZ), max(X0, 0):min(X1, NX)]
                outside = int((sub == 0).sum()) + (X1 - X0) * (Z1 - Z0) - sub.size
                if outside > 0 and y.max() > 0:
                    # how deep: units of the footprint beyond the room on each side
                    zs, xs = np.nonzero(sub == 0)
                    self.say('through wall', f'{f["name"]}#{f["k"]} ({f["what"][:50]}): {outside} sq units of its '
                             f'footprint outside the room (x {x0:.0f}..{x1:.0f}, z {z0:.0f}..{z1:.0f})')
            # over walkable tiles (the player walks through it)
            if not flat and y.min() < 20:
                for (tx, tz) in walk:
                    a = covered(f, tx, tz)
                    if a > 0.2 * T * T:
                        self.say('furniture on walkable tile', f'{f["name"]}#{f["k"]} ({f["what"][:50]}) covers '
                                 f'{a / T / T:.0%} of walkable Sapphire tile ({tx - ox},{tz - oz})')
        # furniture inside furniture (both solid models; stacked ones only touch)
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                fa, ax0, ax1, ay0, ay1, az0, az1 = boxes[i]; fb, bx0, bx1, by0, by1, bz0, bz1 = boxes[j]
                dx = min(ax1, bx1) - max(ax0, bx0); dy = min(ay1, by1) - max(ay0, by0); dz = min(az1, bz1) - max(az0, bz0)
                if min(dx, dy, dz) > 2:
                    self.say('furniture overlap', f'{fa["name"]}#{fa["k"]} ({fa["what"][:30]}) and {fb["name"]}#{fb["k"]} '
                             f'({fb["what"][:30]}) overlap {dx:.0f} x {dy:.0f} x {dz:.0f} units')
        self.boxes = boxes

    def tiles(self):
        """Walkable tiles with no floor under them; people in walls/furniture/void; boxed-in arrival tiles."""
        kind = self.room.kind
        T = 16
        ox, oz = self.room.ox, self.room.oz
        def has_floor(tx, tz):          # zone tile
            X0, Z0 = tx * T, tz * T
            if X0 < 0 or Z0 < 0 or Z0 + T > kind.shape[0] or X0 + T > kind.shape[1]: return False
            sub = kind[Z0:Z0 + T, X0:X0 + T]
            return bool(((sub == 1) | (sub == 2) | (sub == 4)).all())
        # tiles the player can reach: from every warp spot over walkable tiles
        walk = self.room.walk_chunk
        seen = set(); todo = []
        for sp in self.meta['warp_spots']:
            for t in sp['tiles']:
                p = (t[0] + ox, t[1] + oz)
                todo += [p] + [(p[0] + dx, p[1] + dz) for dx, dz in ((0, 1), (0, -1), (1, 0), (-1, 0))]
        todo = [p for p in todo if p in walk]
        while todo:
            p = todo.pop()
            if p in seen: continue
            seen.add(p)
            todo += [q for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)) if q in walk and q not in seen]
        self.reach = seen
        for (tx, tz) in sorted(walk):
            if not has_floor(tx, tz):
                self.say('hole', f'walkable Sapphire tile ({tx - ox},{tz - oz}) has no floor under it'
                         + ('' if (tx, tz) in seen else ' (not reachable from the warps)'))
        zone = INTERIORS.get(self.name, {}).get('zone')
        cfg = json.load(open(os.path.join(ROOT, 'data', 'interiors', f'{zone}.json'))) if zone is not None and \
            os.path.exists(os.path.join(ROOT, 'data', 'interiors', f'{zone}.json')) else {}
        if cfg.get('room') != self.name: return
        solid_furn = [b for b in getattr(self, 'boxes', []) if b[4] - b[3] >= 3 or b[4] >= 6]
        for n in cfg.get('npcs', []):
            if 'at' not in n: continue
            tx, tz = n['at'][0] + ox, n['at'][1] + oz
            who = n.get('_what', f'uid {n.get("uid")} model {n.get("model")}')
            if not has_floor(tx, tz):
                self.say('person', f'{who} at Sapphire {tuple(n["at"])} stands where there is no floor')
            for b in solid_furn:
                f, x0, x1, y0, y1, z0, z1 = b
                a = covered(f, tx, tz)
                if a > 0.25 * T * T and y0 < 20:
                    self.say('person', f'{who} at Sapphire {tuple(n["at"])} stands in {f["name"]}#{f["k"]} ({a / T / T:.0%} of the tile)')
        # arrival: every warp's tile must let the player walk off it (mats: north; stairs/doors: south; others: any)
        walk = self.room.walk_chunk
        for i, w in enumerate(cfg.get('warps', [])):
            if 'at' not in w: continue
            tx, tz = w['at'][0] + ox, w['at'][1] + oz
            spot = next((s for s in self.meta['warp_spots'] if list(w['at']) in s['tiles']), None)
            nb = [(tx + dx, tz + dz) for dx, dz in ((0, 1), (0, -1), (1, 0), (-1, 0))]
            if not any(p in walk for p in nb) and (tx, tz) not in walk:
                self.say('arrival', f'warp {i} at Sapphire {tuple(w["at"])}: no walkable tile around it')
            if spot and spot['kind'] == 'stairs' and (tx, tz + 1) not in walk and w.get('dir', 2) == 2:
                self.say('arrival', f'warp {i} (stairs) at Sapphire {tuple(w["at"])}: the tile south of it is not walkable')
            if not has_floor(tx, tz) and not (spot and spot['kind'] == 'stairs'):
                self.say('arrival', f'warp {i} at Sapphire {tuple(w["at"])}: no floor under the arrival tile')

    def camera(self):
        x0, x1, z0, z1 = self.meta['camera']
        if x1 - x0 < 0 or z1 - z0 < 0: self.say('camera', f'box {self.meta["camera"]} is inverted')

def footprint(f, x0, z0, x1, z1):
    """Unit-cell mask of a furniture model's footprint seen from above (its triangles rasterised; cell centres)."""
    X0, Z0 = int(math.floor(x0)), int(math.floor(z0))
    W, H = int(math.ceil(x1)) - X0 + 1, int(math.ceil(z1)) - Z0 + 1
    m = np.zeros((H, W), bool)
    xs, zs = np.meshgrid(np.arange(W) + X0 + 0.5, np.arange(H) + Z0 + 0.5)
    P = f['pts'].reshape(-1, 3, 3)
    for t in P:
        ax, az = t[0, 0] + 256, t[0, 2] + 256; bx, bz = t[1, 0] + 256, t[1, 2] + 256; cx, cz = t[2, 0] + 256, t[2, 2] + 256
        den = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
        if abs(den) < 1e-9: continue
        i0, i1 = int(max(0, min(ax, bx, cx) - X0)), int(min(W, max(ax, bx, cx) - X0 + 1))
        j0, j1 = int(max(0, min(az, bz, cz) - Z0)), int(min(H, max(az, bz, cz) - Z0 + 1))
        if i1 <= i0 or j1 <= j0: continue
        sx, sz = xs[j0:j1, i0:i1], zs[j0:j1, i0:i1]
        w0 = ((bz - cz) * (sx - cx) + (cx - bx) * (sz - cz)) / den
        w1 = ((cz - az) * (sx - cx) + (ax - cx) * (sz - cz)) / den
        m[j0:j1, i0:i1] |= (w0 >= 0) & (w1 >= 0) & (w0 + w1 <= 1)
    return (X0, Z0, m)

def covered(f, tx, tz, T=16):
    """Unit cells of zone tile (tx, tz) under the furniture's footprint."""
    X0, Z0, m = f['mask']
    a0, a1 = max(tx * T - X0, 0), min((tx + 1) * T - X0, m.shape[1])
    b0, b1 = max(tz * T - Z0, 0), min((tz + 1) * T - Z0, m.shape[0])
    return int(m[b0:b1, a0:a1].sum()) if a1 > a0 and b1 > b0 else 0

class B2Room(Checked):
    """A Black 2 room chunk (calibration: which layered surfaces Black 2 itself has)."""
    def __init__(self, zone, chunk_k=0):
        import subprocess, b2files, zoneheaders
        self.name = f'b2 zone {zone}'
        hd = zoneheaders.parse(b2files.narc_entries(b2files.arc_path(mi.FILES, 12))[0])[zone]
        mat = b2files.narc_entries(b2files.arc_path(mi.FILES, 9))[hd['matrix']]
        fmt, _, w, h = struct.unpack_from('<HHHH', mat, 0)
        cid = struct.unpack_from('<I', mat, 8 + 4 * chunk_k)[0]
        self.name += f' chunk {cid}'
        pack = b2files.area(mi.FILES, hd['area'])['pack']
        d = os.path.join(ROOMS_DIR, '_b2', str(cid)); os.makedirs(d, exist_ok=True)
        _, secs = b2files.chunk(mi.FILES, cid)
        if not os.path.isdir(os.path.join(d, 'dae')):
            open(os.path.join(d, 'm.nsbmd'), 'wb').write(secs[0])
            open(os.path.join(d, 't.nsbtx'), 'wb').write(b2files.map_textures(mi.FILES, b2files.area(mi.FILES, hd['area'])['texset']))
            subprocess.run([pv.APICULA, 'convert', os.path.join(d, 'm.nsbmd'), os.path.join(d, 't.nsbtx'), '-o',
                            os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True)
        dae = [os.path.join(d, 'dae', f) for f in os.listdir(os.path.join(d, 'dae')) if f.endswith('.dae')][0]
        self.terrain = pv.parse(dae)
        self.place = b2files.chunk_buildings(mi.FILES, cid)
        self.pack = pack
        self.out = []

    def faces(self):
        F = []
        for tp, P, UV, C in self.terrain:
            for t in P: F.append(('T', os.path.basename(tp or 'none'), np.array(t, float)))
        self.furn = []
        names = {r['res_id']: r['name'] for r in __import__('b2files').building_pack(mi.FILES, self.pack, exterior=False)}
        for k, b in enumerate(self.place):
            parts = pv.placed(pv.furniture_parts(b['res_id'], self.pack), [b['x'], b['y'], b['z']], b['rot'])
            self.furn.append(dict(k=k, name=names.get(b['res_id'], b['res_id']), what=f'at {b["x"]:.0f},{b["y"]:.0f},{b["z"]:.0f} rot {b["rot"]:.0f}',
                                  pts=np.concatenate([P.reshape(-1, 3) for _, P, _, _ in parts]) if parts else np.zeros((0, 3))))
            for tp, P, UV, C in parts:
                lab = f'{self.furn[-1]["name"]}/{os.path.basename(tp or "-")[:-4]}'
                for t in P: F.append((k, lab, np.array(t, float)))
        return F

def check_room(name):
    c = Checked(name)
    c.layers(); c.furniture(); c.tiles(); c.camera()
    return c.out

# ------------------------------------------------------------------------------------------------ zones of a ROM
def _check_cameras(hdrs, cams):
    """Camera boxes of the version's room zones (data/interiors with the version's overlay; the room variant a Ruby or
    Emerald build installs, e.g. CaveOfOrigin_1F_Emerald): the zone's a/1/0/9 entry must hold the box its room wants,
    and must not be shared with a zone that wants another box (Emerald v1.1: Emerald's interiors patch lets room zones
    that want the same box share one entry). A zone's header copies (data/interiors "variants": Altering Cave's wild
    tables) want their room's box; before, Altering Cave's own copies were listed as sharing its box."""
    import version
    box = lambda k: struct.unpack('<7i', cams[k])[3:] if k < len(cams) and len(cams[k]) == 28 else None
    want = {}                                            # zone -> (room, wanted box)
    for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json'):
        cfg = json.load(open(f))
        if not cfg.get('room') or not version.room_in_version(cfg['room']): continue
        room = version.room_variant(cfg['room'])
        if not os.path.exists(os.path.join(ROOMS_DIR, room, 'room.json')): room = cfg['room']
        if not os.path.exists(os.path.join(ROOMS_DIR, room, 'room.json')): continue   # not built in this folder
        want[cfg['zone']] = (room, tuple(json.load(open(os.path.join(ROOMS_DIR, room, 'room.json')))['camera']))
        for v in cfg.get('variants', []):               # the zone's header copies (Altering Cave's wild tables)
            want.setdefault(v['zone'], want[cfg['zone']])
    out = []
    copies = {v['zone'] for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json')
              for v in json.load(open(f)).get('variants', [])}
    for zone, (room, w) in sorted(want.items()):
        if zone in copies: continue                      # (checked as their room's zone)
        k = hdrs[zone]['cam_bound']; cam = box(k)
        if cam is None or tuple(cam) != w:
            out.append(f'{room}: camera: zone {zone} camera box {k} = {cam}, room wants {list(w)}')
        users = [z for z, hh in enumerate(hdrs) if hh['cam_bound'] == k]
        if len(users) > 1 and any(want.get(z, (None, None))[1] != w for z in users):
            out.append(f'{room}: camera: camera box {k} shared by zones {users}')
    return out

def check_zones(rom):
    import zoneheaders
    from zones import parse_entities
    out = []
    hdrs = zoneheaders.parse(nds_narc(rom, 12)[0])
    ents = nds_narc(rom, 126)
    cams = nds_narc(rom, 109)
    E = {}
    def ent(z):
        if z not in E: E[z] = parse_entities(ents[hdrs[z]['entities']])[0]
        return E[z]
    cfgs = {c['zone']: c for c in (json.load(open(f)) for f in glob.glob(os.path.join(ROOT, 'data', 'interiors', '*.json')))}
    names = {r['zone']: n for n, r in INTERIORS.items()}
    tmpl = hdrs[390]
    out += _check_cameras(hdrs, cams)
    for zone, cfg in sorted(cfgs.items()):
        name = cfg.get('room') or names.get(zone, f'zone {zone}')
        say = lambda kind, msg: out.append(f'{name}: {kind}: {msg}')
        h = hdrs[zone]; e = ent(zone)
        meta = None
        if cfg.get('room') and not os.path.exists(os.path.join(ROOMS_DIR, cfg['room'], 'room.json')):
            continue                      # (sweep_rooms) a room not built in this interiors folder (not in this ROM)
        if cfg.get('room'):
            meta = json.load(open(os.path.join(ROOMS_DIR, cfg['room'], 'room.json')))
            musers = [z for z, hh in enumerate(hdrs) if hh['matrix'] == h['matrix']]
            if len(musers) > 1: say('matrix', f'matrix {h["matrix"]} shared by zones {musers}')
        # walk-in warps (not mats) stacked on one tile: Black 2 fires only the first of them, the others never (Mt. Pyre's
        # holes had one per walking direction and only the one entered walking north worked: a softlock on 5F, mtpyre
        # 2026-10-19 [test]); a tile you can step onto from several sides wants a step trigger (facilities_pyre.py)
        stack = defaultdict(list)
        for i, w in enumerate(e['warps']):
            if w['type'] != 1:
                stack[(w['tile_x'], w['tile_z'], w['y'])].append(i)
        for (tx, tz, _), ids in sorted(stack.items()):
            if len(ids) > 1:
                say('warp', f'warps {ids} on one tile ({tx},{tz}), entered walking {[e["warps"][i]["dir"] for i in ids]} (dir '
                    f'1 S, 2 N, 3 E, 4 W): only the first, warp {ids[0]}, ever fires')
        # warps both ways
        for i, w in enumerate(e['warps']):
            dz, dw = w['dest_zone'], w['dest_warp']
            if dz == zone and dw == 0 and i != 0:
                say('warp', f'warp {i} at tile ({w["tile_x"]},{w["tile_z"]}) leads to its own warp 0 (destination not built)')
                continue
            if w['type'] == 1 and 0xFFFF in (dz, dw): continue   # a mat that never fires (GetWarpIDByPlayerPos skips it:
                                     # IsWarpZoneOrWarpID0xFFFF): a landing spot or a Mt. Pyre hole (its step trigger falls)
            if dz >= len(hdrs): say('warp', f'warp {i} -> zone {dz} (no such zone)'); continue
            de = ent(dz)
            if dw >= len(de['warps']):
                say('warp', f'warp {i} -> zone {dz} warp {dw}, which does not exist ({len(de["warps"])} warps)'); continue
            back = de['warps'][dw]
            if back['dest_zone'] != zone:
                bn = names.get(dz, f'zone {dz}')
                say('warp', f'warp {i} at ({w["tile_x"]},{w["tile_z"]}) -> {bn} (zone {dz}) warp {dw}, which leads to zone '
                    f'{back["dest_zone"]} warp {back["dest_warp"]}, not back here')
            elif back['dest_warp'] >= len(e['warps']):
                say('warp', f'warp {i} -> zone {dz} warp {dw} -> back to warp {back["dest_warp"]}, which does not exist')
            else:
                bw = e['warps'][back['dest_warp']]
                near = abs(bw['tile_x'] - w['tile_x']) <= max(w['w'], bw['w']) and abs(bw['tile_z'] - w['tile_z']) <= max(w['h'], bw['h'])
                if not near:
                    say('warp', f'warp {i} at ({w["tile_x"]},{w["tile_z"]}) -> zone {dz} warp {dw} -> back to warp '
                        f'{back["dest_warp"]} at ({bw["tile_x"]},{bw["tile_z"]}), another spot')
        # people and signs: script numbers exist; their messages exist
        src = glob.glob(os.path.join(ROOT, 'src', 'field_scripts', f'{h["scripts"]:04d}_*.s'))
        txt = glob.glob(os.path.join(ROOT, 'src', 'text', 'script', f'{h["text"]:04d}_*.txt'))
        if cfg.get('room') and not src: say('script', f'no src/field_scripts/{h["scripts"]:04d}_*.s for the zone header')
        if src:
            s = open(src[0]).read()
            import re
            entries = re.findall(r'^\s*ScriptEntry\s+(\w+)', s, re.M)
            n_entries = len(entries)
            used = [n['script'] for n in e['npcs'] if n['script'] < 3000] + [g['script'] for g in e['signs'] if g['script'] < 3000] + \
                   [t['script'] for t in e['triggers'] if t['script'] < 3000]
            for u in used:
                if u > n_entries or u < 1: say('script', f'script {u} used by a person/sign, {src[0][-60:]} has {n_entries} entries')
            if txt:
                lines = open(txt[0], encoding='utf-8').read().rstrip('\n').split('\n')
                for m in re.findall(r'(?:ParentActorMsg|ActorMsg\w*|SystemMsg\w*|EasyMsg\w*|TalkMsg\w*)\s+(?:MSGFILE_SCRIPT,\s*)?(\d+)', s):
                    if int(m) >= len(lines): say('message', f'message {m} used, {os.path.basename(txt[0])} has {len(lines)} lines')
                if any(l.strip() in ('', '…') for l in lines) and entries and entries != ['Script_None']:
                    say('message', f'{os.path.basename(txt[0])} has an empty line')
            elif n_entries and entries != ['Script_None']:
                say('message', f'no src/text/script/{h["text"]:04d}_*.txt for the zone header')
        # place name, banner, music: rooms take their town's (parent) name and music and Littleroot house's banner
        if cfg.get('room'):
            parent = cfg.get('header', {}).get('parent', cfg.get('parent'))
            if h['place_display'] != tmpl['place_display']:
                say('banner', f'place_display {h["place_display"]} (Littleroot house: {tmpl["place_display"]})')
            if parent is not None and parent < len(hdrs) and h['place'] != hdrs[parent]['place'] and 'place' not in cfg.get('header', {}):
                say('place', f'place {h["place"]} but parent zone {parent} has {hdrs[parent]["place"]}')
            if parent is not None:
                exits = [w['dest_zone'] for w in e['warps'] if w['dest_zone'] not in cfgs and w['dest_zone'] not in (zone, 0xFFFF)]
                if exits and parent not in exits:
                    say('parent', f'parent zone {parent} (place {hdrs[parent]["place"]}), but its exits lead to zones {sorted(set(exits))}')
    return out

if __name__ == '__main__':
    mode, args = sys.argv[1], sys.argv[2:]
    if mode == 'rooms':
        names = args or sorted(d for d in os.listdir(ROOMS_DIR) if os.path.exists(os.path.join(ROOMS_DIR, d, 'room.json'))
                               and os.path.exists(os.path.join(ROOT, 'data', 'interior_layouts', d + '.json')))
        for n in names:
            try:
                for line in check_room(n): print(line)
            except Exception as ex:
                print(f'{n}: ERROR: {type(ex).__name__}: {ex}')
            sys.stdout.flush()
    elif mode == 'b2':                    # Black 2's own rooms, for calibration: b2 ZONE [ZONE ...]
        for z in args:
            c = B2Room(int(z)); c.layers()
            for line in c.out: print(line)
    elif mode == 'zones':
        for line in check_zones(args[0]): print(line)
