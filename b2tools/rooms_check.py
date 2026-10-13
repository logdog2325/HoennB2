"""Static checker for the built interior rooms (rooms_cleanup agent, 2026-10-06; notes/INTERIORS.md "Room checks").

    python3 rooms_check.py [--dir ROOMS] [--rom ROM] [--world WORLD] [--kinds abcdefghijklmnopq] [--summary] [ROOM ...]

(ROOMS_CHECK_MODELS=DIR: take the furniture model cache from DIR/_models instead, e.g. to check the lead's
work/interiors without writing there.) Reads only what the builder made (ROOMS/<Map>/room.json, collision*.per, terrain(_all).dae; default HOENN_INTERIORS_DIR
or work/interiors), Sapphire's map, data/interiors/<zone>.json and the field scripts, so it checks any build (the
lead's work/interiors = what a ROM got, an agent's copy = after its fixes). Furniture geometry: Black 2's models via
preview_interior.py's apicula cache. One line per finding: "ROOM: (kind) detail"; --summary counts them by kind.

Kinds (what the player sees in the game):
  a  stairs: a stair model (stair_u01/stair_d01) not on a stairs warp tile, its foot (stair_u01) / the top of its steps
     (stair_d01) not on the warp tile's approach edge, its axis off the tile centre, the warp entered from another side
     than the model climbs, the approach tile blocked, the warp tile walkable, or a flat warp tile (no 45-degree
     collision plane: the player walks INTO the steps instead of up/down them, as Black 2's own stair tiles have);
     stair_d01 with floor over its steps or none on the approach tile
  b  furniture over walkable tiles: a model's drawn footprint (parts below 20 units, not flat on the floor) reaching
     within 5 units of a walkable tile's centre or covering > 30% of it (you appear to walk through it)
  c  people standing on solid tiles or inside furniture (their tile's centre under a model)
  d  scripted movement (ActorCmdExec + walk moves) crossing solid tiles or furniture: the Littleroot scenes
     (scenes/players_house_1f.inc, _2f.inc) with the start positions their scripts give, and every room script's
     movements from the mover's own tile; the final step into a stairs warp tile is allowed (leaving)
  e  warps: a zone warp not on one of Sapphire's warp tiles or the builder's warp spots, a stairs warp whose direction
     does not match its stair model, an exit mat drawn off its warp tiles, an arrival tile you cannot walk off,
     MapChangeCore into a room onto a tile that is neither walkable nor a warp; with --rom also the warps both ways
     (room -> door -> back, interior_sweep_check.check_zones)
  f  layered surfaces < 2 units apart (flicker in melonDS): same-facing overlapping faces of the room (floor, rugs,
     decals, blocks) or of two different pieces; not Black 2's own model-internal layers (a piece's shadow over the
     floor it was made for, shadows over shadows, a model's own faces)
  g  camera: a reachable tile that the camera box (room.json "camera", Black 2's rule: walkable centres +-45 in x,
     first row +6 .. last row -32 in z) leaves off screen, an inverted box; with --rom the zone's box differs
  h-l  b2tools/rooms_check_more.py (sweep_rooms 2026-10-07): h black slabs/gaps between floors and culled faces,
     i textures (missing / another same-named one in the area's set, with --rom), j room exits (check_exits.py),
     k story people (data/story) on solid tiles / in furniture, l walkable tiles with nothing drawn under them
  m-q  b2tools/rooms_view.py (indoor_check 2026-10-08): the people as the game's camera draws them (Black 2's
     camera-facing sprite quads and the zone's field camera, checked against DeSmuME): m a person (zone json and
     story NPCs, and the player on every reachable tile) with geometry behind them drawn across the sprite (heads in
     counters), standing inside furniture, cut off by a side wall, or their head hidden by a wall in front; n people
     whose feet are off the drawn floor (floating / sunk); o door / elevator models off their warp tiles; p holes:
     nothing drawn (the black void) inside the room from the camera; q walkable tiles open to the void with no wall
     (--rom: the people's sprites from the ROM, else Black 2's)
(b) leaves out Black 2's warp panels warp01-03 (pads stepped onto).
"""
import os, sys, re, json, glob, math, struct, subprocess, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import version  # noqa: E402  (HOENN_VERSION=ruby: the ruby/ overlays of data/interiors, data/story; notes/RUBY.md)

T, Y0, GAP = 16, -2, 1.95                  # GAP: Black 2's own rugs lie 1.96-1.99 above its floors
PADS = {'warp01', 'warp02', 'warp03'}      # Black 2's warp panels (pad + rising rings, 2 tiles): stepped onto (sweep_rooms)
WALK_MOVES = {12: (0, -1), 13: (0, 1), 14: (-1, 0), 15: (1, 0), 16: (0, -1), 17: (0, 1), 18: (-1, 0), 19: (1, 0)}
DIR_VEC = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}       # Black 2 warp dir -> the way the player walks in
INTERIORS = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
NO_MAT = {'Route114_FossilManiacsTunnel',                                  # exits Sapphire draws without a mat;
          'SkyPillar_1F',                    # Dragonspiral's lit doorway as the exit notch (caves_misc_skypillar.py)
          'AbandonedShip_Deck'}              # the gangway down to the dock and the sea (ship_hideouts_rooms.py)
TARGETS = {tuple(w['to']) for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json')
           for w in json.load(open(f)).get('warps', []) if 'to' in w}            # (zone, warp) some room warp leads to


def zone_cfgs():
    out = {}
    for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json'):
        c = json.load(open(f))
        if c.get('room'): out[c['room']] = c
    if version.is_emerald():            # (emerald_rooms) an Emerald room variant is checked with its room's zone json
        for room, v in version.variants().items():
            if room in out: out[v] = out[room]
    return out


# ------------------------------------------------------------------------------------------------ one built room
class Built:
    def __init__(self, rooms_dir, name, cfg):
        import models_interior as mi
        import preview_interior as pv
        self.mi, self.pv = mi, pv
        pv.OUT = os.environ.get('ROOMS_CHECK_MODELS') or rooms_dir           # where the apicula model cache (_models) is
        self.name, self.d, self.cfg = name, os.path.join(rooms_dir, name), cfg
        self.meta = json.load(open(os.path.join(self.d, 'room.json')))
        self.ox, self.oz = self.meta['origin']
        self.sm = mi.sapphire_map(self.meta['map'])
        self.out = []
        # collision over zone tiles: {(x, z): (a, b, cls, flags)}
        self.cells = {}
        mw, mh = self.meta.get('matrix', [1, 1])
        chunks = self.meta.get('chunks') or [dict(collision=self.meta['collision'])]
        for k, c in enumerate(chunks):
            if c is None: continue
            per = open(os.path.join(self.d, c['collision']), 'rb').read()
            ci, cj = k % mw, k // mw
            for i in range(1024):
                self.cells[(ci * 32 + i % 32, cj * 32 + i // 32)] = struct.unpack_from('<HHHH', per, 4 + 8 * i)
        self.walk = {t for t, c in self.cells.items() if not c[3] & 1}
        # terrain triangles (model units: x, y, z with the chunk-0 centre at 0)
        tf = os.path.join(self.d, 'terrain_all.dae') if os.path.exists(os.path.join(self.d, 'terrain_all.dae')) else os.path.join(self.d, 'terrain.dae')
        self.terrain = [(os.path.basename(tp or 'none')[:-4], P) for tp, P, UV, C in pv.parse(tf)]
        # furniture: {k, name, rot, pos, tris}
        names = {m['res']: m['name'] for m in self.meta['models']}
        packs = {m['res']: m['pack'] for m in self.meta['models']}
        by_name = {v: k for k, v in names.items()}
        self.furn = []
        for k, f in enumerate(self.meta['furniture']):
            res = f['m'] if isinstance(f['m'], int) else by_name[f['m']]
            parts = pv.placed(pv.furniture_parts(res, packs[res]), f['pos'], f['rot'])
            tris = [(os.path.basename(tp or '-')[:-4], P) for tp, P, UV, C in parts]
            allp = np.concatenate([P.reshape(-1, 3) for _, P in tris]) if tris else np.zeros((0, 3))
            self.furn.append(dict(k=k, name=names[res], rot=f['rot'] % 360, pos=f['pos'], tris=tris, pts=allp))
        self.whats = {}
        try:
            rec = mi.load_recipe(name)
            if len(rec.get('furniture', [])) == len(self.furn):
                self.whats = {k: f.get('_what', '') for k, f in enumerate(rec['furniture'])}
        except Exception:
            pass

    def say(self, kind, msg): self.out.append((kind, f'{self.name}: ({kind}) {msg}'))
    def label(self, f): return f"{f['name']}#{f['k']}" + (f" ({self.whats[f['k']][:40]})" if self.whats.get(f['k']) else '')
    def sap(self, t): return (t[0] - self.ox, t[1] - self.oz)                # zone tile -> Sapphire tile
    def zt(self, s): return (s[0] + self.ox, s[1] + self.oz)
    def local(self, x, z): return x + 256, z + 256                             # model units -> zone units

    # footprint of a piece: unit cells (zone units) under its triangles below 20 units that are not flat on the floor
    def footprint(self, f):
        if 'fp' in f: return f['fp']
        cells = set()
        for tex, P in f['tris']:
            for t in P:
                ys = t[:, 1]
                if ys.min() > 20 or ys.max() < Y0 + 5.5: continue           # overhead, or on the floor (rugs, cushions,
                                                                             # shadows, sunk stools: Black 2's cushions are 3 high)
                xs, zs = t[:, 0] + 256, t[:, 2] + 256
                x0, x1, z0, z1 = int(math.floor(xs.min())), int(math.ceil(xs.max())), int(math.floor(zs.min())), int(math.ceil(zs.max()))
                (ax, bx, cx), (az, bz, cz) = xs, zs
                den = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
                if abs(den) < 1e-9:                                         # a vertical face: its segment on the floor
                    n = max(2, int(max(x1 - x0, z1 - z0)) * 2)
                    for i in range(n + 1):
                        for a, b in ((0, 1), (1, 2), (0, 2)):
                            u = i / n
                            cells.add((int(math.floor(xs[a] + (xs[b] - xs[a]) * u)), int(math.floor(zs[a] + (zs[b] - zs[a]) * u))))
                    continue
                for X in range(x0, x1):
                    for Z in range(z0, z1):
                        px, pz = X + 0.5, Z + 0.5
                        w0 = ((bz - cz) * (px - cx) + (cx - bx) * (pz - cz)) / den
                        w1 = ((cz - az) * (px - cx) + (ax - cx) * (pz - cz)) / den
                        if w0 >= -1e-6 and w1 >= -1e-6 and w0 + w1 <= 1 + 1e-6: cells.add((X, Z))
        f['fp'] = cells
        return cells

    def covers(self, f, tile):
        """(fraction of the zone tile covered, whether the footprint reaches within 5 units of its centre)."""
        fp = self.footprint(f)
        X0, Z0 = tile[0] * T, tile[1] * T
        n = sum((X, Z) in fp for X in range(X0, X0 + T) for Z in range(Z0, Z0 + T))
        centre = any((X, Z) in fp for X in range(X0 + 3, X0 + 13) for Z in range(Z0 + 3, Z0 + 13))
        return n / (T * T), centre

    def stair_tiles(self):
        """Zone tiles of the stairs/door warp spots."""
        return {(s['x'], s['z']) for s in self.meta['warp_spots'] if s['kind'] == 'stairs'}

    # ---------------------------------------------------------------------------------------------- (a) stairs
    def check_stairs(self):
        import models_interior as mi
        spots = {(s['x'], s['z']): s for s in self.meta['warp_spots'] if s['kind'] == 'stairs'}
        zone_dir = {}
        for w in self.cfg.get('warps', []) if self.cfg else []:
            if 'at' in w: zone_dir[self.zt(w['at'])] = w.get('dir')
        for f in self.furn:
            if f['name'] not in mi.STAIR_MODELS: continue
            kind, ax = mi.STAIR_MODELS[f['name']]
            v = mi.rot_pt(-1 if kind == 'up' else 1, 0, f['rot'])               # the way you walk into it
            v = (int(round(v[0])), int(round(v[1])))
            a = mi.rot_pt(ax, 0, f['rot'])
            px, pz = self.local(f['pos'][0], f['pos'][2])
            Ax, Az = px + a[0], pz + a[1]                                        # anchor (foot / top of the steps)
            tile = (int(math.floor((Ax + v[0] * 8) / T)), int(math.floor((Az + v[1] * 8) / T)))
            s = spots.get(tile)
            if s is None:
                near = [t for t in spots if abs(t[0] - tile[0]) + abs(t[1] - tile[1]) <= 2]
                self.say('a', f'{self.label(f)}: its {"foot" if kind == "up" else "top step"} is at zone tile {tile} '
                         f'(Sapphire {self.sap(tile)}), not on a stairs warp tile' + (f' (warp at Sapphire {self.sap(near[0])})' if near else ''))
                continue
            sx, sz = self.sap(tile)
            self.stairs_with_model = getattr(self, 'stairs_with_model', set()) | {tile}
            edge = (tile[0] * T + 8 - v[0] * 8, tile[1] * T + 8 - v[1] * 8)    # approach edge midpoint
            along = (Ax - edge[0]) * v[0] + (Az - edge[1]) * v[1]
            side = (Ax - edge[0]) * v[1] - (Az - edge[1]) * v[0]
            if abs(along) > 2:
                self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): its {"foot" if kind == "up" else "top step"} is '
                         f'{along:+.0f} units from the warp tile\'s approach edge (Black 2: on it)')
            if abs(side) > 2:
                self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): its axis is {side:+.0f} units off the warp tile\'s centre')
            wd = s.get('dir'); wd = zone_dir.get(tile) or wd
            if DIR_VEC.get(wd) != v:
                self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): the warp is entered walking {DIR_VEC.get(wd)}, '
                         f'the model {"climbs" if kind == "up" else "descends"} toward {v}')
            app = (tile[0] - v[0], tile[1] - v[1])
            if app not in self.walk:
                self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): the tile you approach it from, Sapphire {self.sap(app)}, is not walkable')
            c = self.cells.get(tile)
            if tile in self.walk:
                self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): the warp tile is walkable (Black 2: solid, the warp fires walking into it)')
            if c and c[0] >> 2 == 0:
                self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): the warp tile is flat, so the player walks into the '
                         f'steps instead of {"up" if kind == "up" else "down"} them (Black 2: a 45-degree plane, 0 at the approach edge)')
            elif c:
                y = self.plane_y(c, tile[0] * T + 8, tile[1] * T + 8)
                if abs(y - (8 if kind == 'up' else -8)) > 2:
                    self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): the warp tile\'s plane is at y {y:.0f} at its centre '
                             f'(Black 2: {8 if kind == "up" else -8})')
            if kind == 'down':
                if not self.floor_at(app[0] * T + 8, app[1] * T + 8):
                    self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): no floor on the approach tile Sapphire {self.sap(app)}')
                if self.floor_at(tile[0] * T + 8 + v[0] * 4, tile[1] * T + 8 + v[1] * 4):
                    self.say('a', f'{self.label(f)} at Sapphire ({sx},{sz}): floor drawn over its steps (no opening)')
        covered = {t for f in self.furn for t in self.stair_tiles() for u in (t, (t[0], t[1] - 1))     # (doors stand on the
                   if self.covers(f, u)[1] or self.covers(f, u)[0] > 0.3 or (u != t and self.covers(f, u)[0] > 0.05)}  # wall north)
        covered |= getattr(self, 'stairs_with_model', set())
        for t in sorted(self.stair_tiles()):
            if t not in covered and any(f['name'] in mi.STAIR_MODELS for f in self.furn):
                b = self.sm['beh'][t[1] - self.oz][t[0] - self.ox] if 0 <= t[1] - self.oz < self.sm['h'] and 0 <= t[0] - self.ox < self.sm['w'] else None
                self.say('a', f'stairs/door warp at Sapphire {self.sap(t)} (behaviour {b:#x}) has no model on it')

    def plane_y(self, c, x, z):
        import models_interior as mi
        h = mi.heights()
        nx, ny, nz = h.NORMALS[c[0] >> 2]; d = h.OFFS[c[1]]
        cx, cz = (x % 512) - 256, (z % 512) - 256
        return -(nx * cx - nz * cz + d) / ny

    def floor_at(self, x, z, y=Y0):
        """Whether a terrain face at height y covers zone point (x, z) (units)."""
        mx, mz = x - 256, z - 256
        for tex, P in self.terrain:
            for t in P:
                if abs(t[:, 1] - y).max() > 0.01: continue
                if not (t[:, 0].min() <= mx <= t[:, 0].max() and t[:, 2].min() <= mz <= t[:, 2].max()): continue
                (ax, bx, cx), (az, bz, cz) = t[:, 0], t[:, 2]
                den = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
                if abs(den) < 1e-9: continue
                w0 = ((bz - cz) * (mx - cx) + (cx - bx) * (mz - cz)) / den
                w1 = ((cz - az) * (mx - cx) + (ax - cx) * (mz - cz)) / den
                if w0 >= -1e-6 and w1 >= -1e-6 and w0 + w1 <= 1 + 1e-6: return True
        return False

    # ---------------------------------------------------------------------------------------------- (b) furniture
    def check_furniture(self):
        import models_interior as mi
        stairs = self.stair_tiles()
        for f in self.furn:
            if f['name'] in mi.STAIR_MODELS: zone = None
            if f['name'] in PADS: continue                                 # warp panels: pads you step onto
            fp = self.footprint(f)
            if not fp: continue
            tiles = {(X // T, Z // T) for X, Z in fp}
            for t in sorted(tiles & self.walk):
                frac, centre = self.covers(f, t)
                if centre or frac > 0.3:
                    self.say('b', f'{self.label(f)} covers {frac:.0%} of walkable Sapphire tile {self.sap(t)}'
                             + (' up to its centre' if centre else ''))

    # ---------------------------------------------------------------------------------------------- (c) people
    def check_people(self):
        if not self.cfg: return
        stairs = self.stair_tiles()
        for i, n in enumerate(self.cfg.get('npcs', [])):
            if 'at' not in n: continue
            t = self.zt(n['at']); who = n.get('what') or n.get('_what') or f"uid {n.get('uid')} model {n.get('model')}"
            who = f'NPC {i} ({who[:50]})'
            if t in stairs: continue                                         # on the stairs: arriving / leaving
            if t not in self.walk:
                c = self.cells.get(t)
                self.say('c', f'{who} at Sapphire {tuple(n["at"])} stands on a solid tile (class {c[2]:#x})' if c else
                         f'{who} at Sapphire {tuple(n["at"])} stands outside the room')
            for f in self.furn:
                frac, centre = self.covers(f, t)
                if centre:
                    self.say('c', f'{who} at Sapphire {tuple(n["at"])} stands inside {self.label(f)} ({frac:.0%} of the tile)')

    # ---------------------------------------------------------------------------------------------- (d) paths
    def check_path(self, who, start, steps, script):
        """steps: [(dx, dz)] from zone tile start; the last step may enter a stairs warp tile (leaving)."""
        stairs = self.stair_tiles()
        exits = {(s['x'] + k, s['z']) for s in self.meta['warp_spots'] if s['kind'] == 'exit' for k in range(s['w'])}
        p = start
        for i, (dx, dz) in enumerate(steps):
            if p in exits and dz > 0: break                                  # out of the door: gone
            p = (p[0] + dx, p[1] + dz)
            last = i == len(steps) - 1
            if p not in self.walk and not (p in stairs and last):
                self.say('d', f'{script}: {who} steps onto Sapphire {self.sap(p)}, which is not walkable')
                break
            hits = [self.label(f) for f in self.furn if f['name'] not in self.mi.STAIR_MODELS and self.covers(f, p)[1]]
            if hits:
                self.say('d', f'{script}: {who} walks through {", ".join(hits)} at Sapphire {self.sap(p)}')
        return p

    # ---------------------------------------------------------------------------------------------- (e) warps
    def check_warps(self):
        if not self.cfg: return
        sap_warps = {(w['x'], w['y']) for w in self.sm['warps']}
        spot_tiles = {tuple(t): s for s in self.meta['warp_spots'] for t in s['tiles']}
        exits = {tuple(t) for sp in self.meta['warp_spots'] if sp['kind'] == 'exit' for t in sp['tiles']}
        for i, w in enumerate(self.cfg.get('warps', [])):
            arrival = (self.cfg['zone'], i) in TARGETS or i == 0 or tuple(w.get('at', ())) in exits
            if 'at' in w: s = tuple(w['at'])
            else: s = (w['x'] - self.ox, w['z'] - self.oz)
            t = self.zt(s)
            moved = re.search(r'Sapphire warp \d+ \((\d+),(\d+)\)', w.get('what', ''))     # a generator moved it onto
            moved = moved and (int(moved[1]), int(moved[2])) in sap_warps and abs(int(moved[1]) - s[0]) + abs(int(moved[2]) - s[1]) <= 1
            if s not in sap_warps and not moved:                   # the stairs next to Sapphire's arrow (ship corridors)
                self.say('e', f'warp {i} at Sapphire {s} is not on one of Sapphire\'s warp tiles {sorted(sap_warps)}')
            spot = spot_tiles.get(s)
            if 'at' in w and spot is None and not w.get('tile_only'):
                self.say('e', f'warp {i} at Sapphire {s}: no warp spot of the room there')
            if not (0 <= s[0] < self.sm['w'] and 0 <= s[1] < self.sm['h']): continue   # Sapphire's off-map warps (ferry)
            dflt = (2, 2) if w.get('tile_only') else (1, 1)                  # as patches/interiors.py
            typ = w.get('type', spot['type'] if spot else dflt[0]); d = w.get('dir', spot['dir'] if spot else dflt[1])
            # arrival: type 1 (mats) you arrive on the tile and walk off it north (or any side); others step out
            # opposite to the walk-in direction
            if not arrival: continue                                      # nothing leads here (Cable Club doors,
                                                                             # a hole's extra walk-in sides)
            if typ == 1:
                nb = [(t[0] + a, t[1] + b) for a, b in ((0, -1), (1, 0), (-1, 0))]
                if t not in self.walk and not any(q in self.walk for q in nb):
                    self.say('e', f'warp {i} (exit mat) at Sapphire {s}: you arrive on it and cannot walk off it')
            elif d in DIR_VEC and t not in self.walk:                       # (on a walkable warp tile you just stand)
                v = DIR_VEC[d]; out = (t[0] - v[0], t[1] - v[1])
                if out not in self.walk:
                    self.say('e', f'warp {i} at Sapphire {s} (entered walking {v}): the tile you step out onto, Sapphire {self.sap(out)}, is not walkable')
        # exit mats drawn on their warp tiles: a rug/mat face covers every exit tile (Sapphire draws a mat on every exit
        # but the Fossil Maniac's tunnel mouth)
        for sp in self.meta['warp_spots'] if self.name not in NO_MAT and self.name[:-8] not in NO_MAT else []:   # (+ its _Emerald variant)
            if sp['kind'] != 'exit': continue
            for st in sp['tiles']:
                t = self.zt(st)
                cx, cz = t[0] * T + 8, t[1] * T + 8
                mats = [tex for tex, P in self.terrain if self.face_over(P, cx, cz, Y0 + 0.5)]
                if not mats:
                    self.say('e', f'exit tile Sapphire {tuple(st)} has no mat drawn on it')

    def face_over(self, P, x, z, ymin):
        mx, mz = x - 256, z - 256
        for t in P:
            if t[:, 1].min() < ymin or abs(t[:, 1].max() - t[:, 1].min()) > 0.01 or t[:, 1].max() > Y0 + 8: continue
            if t[:, 0].min() <= mx <= t[:, 0].max() and t[:, 2].min() <= mz <= t[:, 2].max(): return True
        return False

    # ---------------------------------------------------------------------------------------------- (f) layers
    def check_layers(self):
        F = []
        for tex, P in self.terrain:
            for t in P: F.append(('T', tex, t))
        for f in self.furn:
            for tex, P in f['tris']:
                for t in P: F.append((f['k'], tex, t))
        buckets = defaultdict(list)
        for owner, tex, t in F:
            n = np.cross(t[1] - t[0], t[2] - t[0]); l = np.linalg.norm(n)
            if l < 0.1: continue
            n = n / l
            if not (n[1] > 0.3 or n[2] > 0.3 or abs(n[0]) > 0.7): continue      # faces the camera can see
            key = tuple(np.round(n, 2)); nk = np.array(key) / np.linalg.norm(key)     # one normal per bucket: a
            buckets[key].append((float(nk @ t.mean(0)), owner, tex, t, nk))          # tilted face's own n skews d
        hits = {}
        shadow = lambda tex: 'kage' in tex
        for key, items in buckets.items():
            items.sort(key=lambda it: it[0])
            n = items[0][4]
            u = np.cross(n, [0, 1, 0] if abs(n[1]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u); v = np.cross(n, u)
            P2 = [[(float(p @ u), float(p @ v)) for p in it[3]] for it in items]
            box = [(min(p[0] for p in q), max(p[0] for p in q), min(p[1] for p in q), max(p[1] for p in q)) for q in P2]
            for i in range(len(items)):
                di, oi, ti = items[i][0], items[i][1], items[i][2]
                for j in range(i + 1, len(items)):
                    dj, oj, tj = items[j][0], items[j][1], items[j][2]
                    if dj - di >= GAP - 1e-3: break
                    if oi == oj and oi != 'T': continue                       # a model's own faces
                    if oi == 'T' and oj == 'T' and abs(dj - di) < 1e-3: continue  # one surface split in triangles
                    if shadow(ti) and shadow(tj): continue                    # Black 2 overlaps shadows itself
                    if 'T' in (oi, oj) and (shadow(ti) or shadow(tj)):         # a piece's shadow over the floor it
                        other = items[i] if oi == 'T' else items[j]             # stands on (Black 2's own spacing)
                        if abs(other[3][:, 1] - Y0).max() < 0.01: continue
                    bi, bj = box[i], box[j]
                    if bi[1] <= bj[0] or bj[1] <= bi[0] or bi[3] <= bj[2] or bj[3] <= bi[2]: continue
                    # a sliver under 0.75 units wide (a shadow's edge over a rug's) is below a pixel: not a flicker
                    if min(min(bi[1], bj[1]) - max(bi[0], bj[0]), min(bi[3], bj[3]) - max(bi[2], bj[2])) < 0.75: continue
                    a = _overlap(P2[i], P2[j])
                    if a < 0.5: continue
                    k = (oi, ti, oj, tj, round(dj - di, 2), key)
                    hits[k] = hits.get(k, 0) + a
        for (oi, ti, oj, tj, dd, key), a in sorted(hits.items(), key=lambda kv: -kv[1]):
            if a < 2.0: continue
            nm = lambda o, t: f'room {t}' if o == 'T' else f'{self.label(self.furn[o])}/{t}'
            facing = 'up' if key[1] > 0.9 else ('south' if key[2] > 0.9 else 'side')
            self.say('f', f'{nm(oi, ti)} and {nm(oj, tj)} are {dd} units apart (facing {facing}), {a:.0f} sq units overlap')

    # ---------------------------------------------------------------------------------------------- (g) camera
    def check_camera(self):
        x0, x1, z0, z1 = self.meta['camera']
        if x1 < x0 or z1 < z0: self.say('g', f'camera box {self.meta["camera"]} is inverted'); return
        seen = set(); todo = [self.zt(t) for s in self.meta['warp_spots'] for t in s['tiles']]
        todo = [p for q in todo for p in [q] + [(q[0] + a, q[1] + b) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))] if p in self.walk]
        while todo:
            p = todo.pop()
            if p in seen: continue
            seen.add(p); todo += [q for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)) if q in self.walk and q not in seen]
        bad = []
        for p in sorted(seen):
            px, pz = p[0] * T + 8, p[1] * T + 8
            cx, cz = min(max(px, x0), x1), min(max(pz, z0), z1)
            if abs(px - cx) > 96 or pz - cz > 48 or cz - pz > 72: bad.append(p)
        if bad:
            self.say('g', f'camera box {self.meta["camera"]} leaves {len(bad)} reachable tiles off screen, e.g. Sapphire {self.sap(bad[0])}')


def _overlap(p, q):
    def area(poly): return abs(sum(poly[i - 1][0] * a[1] - a[0] * poly[i - 1][1] for i, a in enumerate(poly))) / 2
    if area(p) < 1e-9 or area(q) < 1e-9: return 0.0
    s = lambda t: (t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) - (t[1][1] - t[0][1]) * (t[2][0] - t[0][0])
    if s(q) < 0: q = [q[0], q[2], q[1]]
    poly = list(p)
    for i in range(3):
        a, b = q[i], q[(i + 1) % 3]; out = []
        side = lambda r: (b[0] - a[0]) * (r[1] - a[1]) - (b[1] - a[1]) * (r[0] - a[0])
        for k, cur in enumerate(poly):
            prv = poly[k - 1]; sc, sp = side(cur), side(prv)
            if (sc >= 0) != (sp >= 0):
                tt = sp / (sp - sc); out.append((prv[0] + (cur[0] - prv[0]) * tt, prv[1] + (cur[1] - prv[1]) * tt))
            if sc >= 0: out.append(cur)
        poly = out
        if len(poly) < 3: return 0.0
    return area(poly)


# ------------------------------------------------------------------------------------------------ (d) scripts
def preprocess(src):
    """A field script as the assembler sees it (the C preprocessor with the build's include paths and defines)."""
    dec = os.path.join(ROOT, 'external', 'pokebw2')
    r = subprocess.run(['/opt/homebrew/opt/llvm/bin/clang', '-E', '-P', '-x', 'assembler-with-cpp', '-I', f'{dec}/include',
                        '-I', f'{dec}/lib/nitro/include', '-I', os.path.join(ROOT, 'src', 'include'), '-D', 'BLACK2', src],
                       capture_output=True, text=True, cwd=os.path.dirname(src))
    return r.stdout if r.returncode == 0 else ''

def movements(text):
    """{label: [(dx, dz)...]} of the movement lists in a preprocessed script (walk moves only)."""
    out, cur = {}, None
    for ln in text.split('\n'):
        m = re.match(r'^\s*(\w+):', ln)
        if m: cur = m.group(1); out.setdefault(cur, []); continue
        m = re.match(r'^\s*Move\s+(\d+)\s*,\s*(\d+)', ln)
        if m and cur is not None and int(m.group(1)) in WALK_MOVES:
            out[cur] += [WALK_MOVES[int(m.group(1))]] * int(m.group(2))
    return out

def script_blocks(text):
    """{Script_n: [(actor, movement label)...]} in order."""
    out, cur = {}, None
    for ln in text.split('\n'):
        m = re.match(r'^\s*(Script_\w+|L_\w+):', ln)
        if m and m.group(1).startswith('Script_'): cur = m.group(1); out[cur] = []; continue
        m = re.match(r'^\s*ActorCmdExec\s+(\w+)\s*,\s*(\w+)', ln)
        if m and cur: out[cur].append((m.group(1), m.group(2)))
    return out

# The Littleroot scenes: where each actor stands when the script starts (zone tiles; scenes/*.inc and the zone init
# scripts 24 put Mom there; the player arrives on the mat from outside or one tile south of the stairs from upstairs)
def littleroot_scenarios(rooms_dir, cfgs):
    out = []
    for zone, name, src, brendan in ((390, 'LittlerootTown_BrendansHouse_1F', '0780_brendans_house_1f.s', True),
                                     (392, 'LittlerootTown_MaysHouse_1F', '0784_mays_house_1f.s', False),
                                     (391, 'LittlerootTown_BrendansHouse_2F', '0782_brendans_house_2f.s', True),
                                     (393, 'LittlerootTown_MaysHouse_2F', '0786_mays_house_2f.s', False)):
        text = preprocess(os.path.join(ROOT, 'src', 'field_scripts', src))
        inc = open(os.path.join(ROOT, 'src', 'field_scripts', 'scenes',
                                'players_house_1f.inc' if name.endswith('1F') else 'players_house_2f.inc')).read()
        inc = inc.split('#if HOUSE_BRENDAN', 1)[-1]    # (the house's own #if block: emerald_ch0_3 put an #ifdef HOENN_EMERALD
        defs = {k: int(v) for k, v in re.findall(r'#define\s+(\w+_X)\s+(\d+)', inc.split('#else')[0 if brendan else 1])}   # before it)
        cfg = cfgs.get(name, {}); npc = {n['uid']: tuple(n['at']) for n in cfg.get('npcs', [])}
        meta = json.load(open(os.path.join(rooms_dir, name, 'room.json'))); ox, oz = meta['origin']
        zt = lambda s: (s[0] + ox, s[1] + oz)
        stair = next(tuple(s['tiles'][0]) for s in meta['warp_spots'] if s['kind'] == 'stairs')
        below_stairs = (stair[0] + ox, stair[1] + oz + 1)
        mat = next(zt(w['at']) if 'at' in w else (w['x'], w['z']) for w in cfg.get('warps', []))
        if name.endswith('1F'):
            arrive = (defs['MOM_DOOR_X'] - 1, 8) if brendan else (defs['MOM_DOOR_X'] + 1, 8)
            out.append((name, text, 'Script_20', {'255': arrive, '1': (defs['MOM_DOOR_X'], 8)}))
            out.append((name, text, 'Script_21', {'255': below_stairs, '1': (defs['MOM_STAIRS_X'], 4)}))
            out.append((name, text, 'Script_22', {'255': below_stairs, '1': (defs['MOM_TV_X'], 5)}))
            out.append((name, text, 'Script_23', {'255': arrive, '4': zt(npc[4])}))
        else:
            out.append((name, text, 'Script_20', {'255': (stair[0] + ox - 1, stair[1] + oz + 1) if brendan else (stair[0] + ox + 1, stair[1] + oz + 1),
                                                  '14': zt(npc[14])}))
            out.append((name, text, 'Script_21', {'255': None, '1': (defs['RIVAL_X'], 3)}))
    return out


def check_scripts(rooms_dir, cfgs, built):
    """(d): returns [(room, kind, line)]."""
    done = set()
    for name, text, script, starts in littleroot_scenarios(rooms_dir, cfgs):
        b = built(name)
        if b is None: continue
        mv = movements(text); blocks = script_blocks(text)
        pos = dict(starts)
        seq = blocks.get(script, [])
        # Script_21 (2F) picks one of two routes by the player's facing: check both
        alts = [seq]
        if any(l == 'Mv_RivalAroundToStairs' for _, l in seq):
            alts = [[s for s in seq if s[1] != 'Mv_RivalAroundToStairs'], [s for s in seq if s[1] != 'Mv_RivalToStairs']]
        for alt in alts:
            pos = dict(starts)
            for actor, label in alt:
                steps = mv.get(label, [])
                if not steps or pos.get(actor) is None: continue
                who = 'the player' if actor == '255' else f'actor {actor}'
                pos[actor] = b.check_path(who, pos[actor], steps, f'{script} {label}')
        done.add(name)
    # every room script: each ActorCmdExec of a room NPC from its own tile
    for f in sorted(glob.glob(os.path.join(ROOT, 'src', 'field_scripts', '*_room_*.s'))):
        name = re.sub(r'^\d+_room_|\.s$', '', os.path.basename(f))
        if name.endswith('_init'): continue
        if name not in cfgs: continue
        raw = open(f).read()
        if 'ActorCmdExec' not in raw: continue
        text = preprocess(f); mv = movements(text)
        b = None
        npc = {str(n['uid']): tuple(n['at']) for n in cfgs[name].get('npcs', []) if 'at' in n}
        for script, seq in script_blocks(text).items():
            pos = {}
            for actor, label in seq:
                steps = mv.get(label, [])
                if not steps or actor not in npc: continue
                b = b or built(name)
                if b is None: break
                start = pos.get(actor) or b.zt(npc[actor])
                pos[actor] = b.check_path(f'NPC uid {actor}', start, steps, f'{os.path.basename(f)} {script} {label}')


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--rom'); ap.add_argument('--kinds', default='abcdefghijklmnopq'); ap.add_argument('--summary', action='store_true')
    ap.add_argument('--world')                                       # (j) exits: the world dir (default work/world)
    ap.add_argument('rooms', nargs='*')
    a = ap.parse_args()
    os.environ['HOENN_INTERIORS_DIR'] = os.path.abspath(a.dir)        # preview_interior's model cache lives there
    cfgs = zone_cfgs()
    names = a.rooms or sorted(d for d in os.listdir(a.dir) if os.path.exists(os.path.join(a.dir, d, 'room.json'))
                              and os.path.exists(os.path.join(ROOT, 'data', 'interior_layouts', d + '.json')))
    cache, lines = {}, []
    def built(n):
        if n not in cache:
            try: cache[n] = Built(a.dir, n, cfgs.get(n))
            except Exception as ex:
                lines.append(('!', f'{n}: (!) cannot read the built room: {type(ex).__name__}: {ex}')); cache[n] = None
        return cache[n]
    for n in names:
        b = built(n)
        if b is None: continue
        for k, fn in (('a', b.check_stairs), ('b', b.check_furniture), ('c', b.check_people), ('e', b.check_warps),
                      ('f', b.check_layers), ('g', b.check_camera)):
            if k in a.kinds:
                try: fn()
                except Exception as ex: b.say('!', f'check {k} failed: {type(ex).__name__}: {ex}')
    if 'd' in a.kinds: check_scripts(a.dir, cfgs, lambda n: built(n) if (not a.rooms or n in a.rooms) else None)
    out = list(lines)
    for n in names + sorted(set(cache) - set(names)):
        if cache.get(n): out += cache[n].out
    if set(a.kinds) & set('hijkl'):                                  # rooms_check_more.py (sweep_rooms 2026-10-07)
        import rooms_check_more
        out += [(k, ln) for k, ln in rooms_check_more.run(a.dir, names, cfgs, a.kinds, a.rom, built, a.world) if k != 'j-info']
    if set(a.kinds) & set('mnopq'):                                  # rooms_view.py (indoor_check 2026-10-08)
        import rooms_view
        out += rooms_view.run(a.dir, names, cfgs, a.kinds, a.rom, built)
    if a.rom:
        import interior_sweep_check as isc
        for ln in isc.check_zones(a.rom):
            k = 'g' if ': camera:' in ln else 'e'
            if k in a.kinds and (': warp:' in ln or ': camera:' in ln): out.append((k, ln.replace(': warp:', ': (e) warp:').replace(': camera:', ': (g) camera:')))
    # (emerald_integrate 2026-10-12) rooms this version leaves out (data/versions.json "rooms", patches/interiors.py: Emerald's
    # contest lobbies and halls) are not in its ROM: their findings are not this version's
    out = [(k, ln) for k, ln in out if version.room_in_version(ln.split(':')[0].strip())]
    if version.is_emerald():            # (emerald_rooms) rooms Emerald replaces by a variant are not in its ROM either
        rep = set(version.variants())
        out = [(k, ln) for k, ln in out if ln.split(':')[0].strip() not in rep]
    if a.summary:
        c = Counter(k for k, _ in out)
        rooms = defaultdict(set)
        for k, ln in out: rooms[k].add(ln.split(':')[0])
        for k in sorted(c): print(f'{k}: {c[k]} findings in {len(rooms[k])} rooms')
    else:
        for _, ln in out: print(ln)

if __name__ == '__main__':
    main()
