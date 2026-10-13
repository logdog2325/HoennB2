"""Underwater maps for the cave builder (dive agent, 2026-10-06; notes/DIVE.md). Called from b2tools/models_cave.py at
its hooks (end of Cave.classify, Cave.build_terrain, cave_collision), like models_cave_misc.py; switched on by the
recipe key "underwater", so recipes without it build exactly as before.

Sapphire's underwater maps (MAP_TYPE_UNDERWATER: Underwater1-4, Underwater_SootopolisCity, ...) are trenches in the
seabed: the walkable tiles are where the diving player swims, everything else is raised seabed. In Black 2 a diving
player (special state 3) moves on a grid map with the Surf logic (ov036 FieldPlayerGrid_DecideCommand and
FieldPlayerGrid_UpdateCore jump to the Surf handlers for states 2 and 3 [code]), so the swimmable floor needs water
cells. Black 2's own underwater grid map, the Abyssal Ruins (zone 245, chunks 560-610), uses class 0x9C flags 0x02 for
every swimmable cell and 0x01/0x81 for walls [bytes]; this module writes the same.

Recipe keys (data/cave_layouts/<Map>.json):
  underwater  true: every walkable Sapphire tile becomes swimmable floor (no drawn cave water; the look's floor),
              collision 0x9C/0x02, 0x9C/0x06 on Sapphire's seaweed (MB_SEAWEED 0x22, MB_SEAWEED_NO_SURFACING 0x2A:
              the Gen 3 encounter attribute; flag 0x04 is the encounter bit of Black 2's water cells 0x16 vs 0x12);
              seaweed tiles get the look's "seaweed" decal, tiles where Sapphire lets you surface (not
              MB_NO_SURFACING 0x19 / 0x2A) the look's "light" decal ("Light is filtering down from above");
              Sapphire's water doors (MB_WATER_DOOR 0x6C, a notch in a north trench wall you swim into) become the
              cave builder's doorway: Black 2's cave arch on the tile and a type-4 warp walked into northwards.
  currents    true: Sapphire's current tiles in a cave's surf water (MB_*_CURRENT 0x50-0x53) get Black 2's current
              cells (0x94 east, 0x95 west, 0x96 north, 0x97 south, flags 0x02, as terrain/water.py's overworld
              currents); drawn as plain cave water (Black 2's caves have no current art).
"""
import hashlib, math
from collections import defaultdict

SEAWEED = {0x22, 0x2A}
NO_SURFACE = {0x19, 0x2A}               # pokeruby MetatileBehavior_IsNotSurfacable
MB_WATER_DOOR = 0x6C
UW_CLASS, UW_FLAGS, UW_FLAGS_ENC = 0x9C, 0x02, 0x06

# Sapphire's currents (MB_EASTWARD/WESTWARD/NORTHWARD/SOUTHWARD_CURRENT 0x50-0x53) -> Black 2's current cells
# 0x94-0x97, flags 0x02 (Route 17/18; b2tools/terrain/water.py: 0x94 east, 0x95 west, 0x96 north, 0x97 south, tested
# there): a current tile whose next tile downstream is not water stays plain water (Black 2's carry does not stop at
# solid tiles)
CURRENT = {0x50: (0x94, (1, 0)), 0x51: (0x95, (-1, 0)), 0x52: (0x96, (0, -1)), 0x53: (0x97, (0, 1))}

def active(r):
    return bool(r.get('underwater') or r.get('currents'))

# ------------------------------------------------------------------------------------------------ classify hook
def classify(c):
    """Walkable tiles: floor (Sapphire's surfable underwater behaviours made them cave water); water doors: step
    warps on their own tile."""
    W, H, sm = c.W, c.H, c.sm
    c.uw_seaweed, c.uw_light, c.uw_current = set(), set(), {}
    if c.r.get('currents'):                  # (a cave's surf water: Seafloor Cavern rooms 6 and 7)
        for z in range(H):
            for x in range(W):
                b = sm['beh'][z][x]
                if c.kind[z][x] == 'water' and b in CURRENT:
                    cls, (dx, dz) = CURRENT[b]
                    if 0 <= x + dx < W and 0 <= z + dz < H and c.kind[z + dz][x + dx] == 'water':
                        c.uw_current[(x, z)] = cls
    if not c.r.get('underwater'): return
    for z in range(H):
        for x in range(W):
            if not sm['walk'][z][x]: continue
            if c.kind[z][x] == 'water': c.kind[z][x] = 'floor'
            b = sm['beh'][z][x]
            if b in SEAWEED: c.uw_seaweed.add((x, z))
            if b not in NO_SURFACE: c.uw_light.add((x, z))
            c.fy.setdefault((x, z), 0)
    c.wy.clear()
    # water doors: every one of Sapphire's is a notch in a north trench wall entered swimming north (Underwater2
    # (45,65), Underwater4 (38,26), Underwater_SealedChamber (7,1), AbandonedShip_Underwater2 (3,1)): built like the
    # cave builder's MB_DOOR doorways (Steven's room): Black 2's cave arch on the tile, a type-4 warp walked into
    # northwards (arriving through it puts you one tile south, as Black 2's cave exits)
    for s in c.spots:
        x, z = s['tiles'][0]
        if 0 <= x < W and 0 <= z < H and sm['beh'][z][x] == MB_WATER_DOOR and sm['walk'][z][x]:
            assert z > 0 and not sm['walk'][z - 1][x], f'{c.name}: water door ({x},{z}) is not in a north wall'
            s.update(kind='door', type=4, dir=2, x=c.ox + x, z=c.oz + z)
            c.kind[z][x] = 'arch'
            c.arches.append(dict(x=x, z=z, face='n', to_outside=False))
            c.fy.pop((x, z), None); c.uw_seaweed.discard((x, z)); c.uw_light.discard((x, z))

# ------------------------------------------------------------------------------------------------ geometry hook
def geometry(c):
    """Seaweed and light decals over the floor (2 and 3 units above it: Black 2's floor decal spacing, cave_builder)."""
    if not c.r.get('underwater'): return
    L = c.look
    C = lambda v: v - 256
    def put(tex, tiles, dy, size):
        for (x, z) in sorted(tiles):
            y = c.fy.get((x, z), 0) + dy
            X0, Z0 = c.lx(x), c.lz(z)
            X1, Z1 = X0 + 16, Z0 + 16
            c.m.quad(tex, [(C(X0), y, C(Z1), X0 / size, -Z1 / size), (C(X1), y, C(Z1), X1 / size, -Z1 / size),
                           (C(X1), y, C(Z0), X1 / size, -Z0 / size), (C(X0), y, C(Z0), X0 / size, -Z0 / size)])
    floor = {t for t in c.fy if c.kind[t[1]][t[0]] == 'floor'}
    # none on the tiles before an arch: its template's tunnel spill (h06kuro, 2 over the floor) lies there and they
    # z-fought with it in melonDS (sweep_caves)
    floor -= {(a['x'] + i, a['z'] + j) for a in c.arches for i in range(-2, 3) for j in range(-2, 3)}
    if L.get('no_void'):                     # the seabed also covers the matrix around the Sapphire map
        h, sz = 16 * c.tiers, L.get('top_size', 16)
        col = (L.get('top_color', 0.77),) * 3
        X0, Z0, X1, Z1 = c.lx(0), c.lz(0), c.lx(c.W), c.lz(c.H)
        for a0, b0, a1, b1 in ((0, 0, 512 * c.mw, Z0), (0, Z1, 512 * c.mw, 512 * c.mh), (0, Z0, X0, Z1), (X1, Z0, 512 * c.mw, Z1)):
            if a1 <= a0 or b1 <= b0: continue
            c.m.quad(L['top'], [(C(a0), h, C(b1), a0 / sz, -b1 / sz, col), (C(a1), h, C(b1), a1 / sz, -b1 / sz, col),
                                (C(a1), h, C(b0), a1 / sz, -b0 / sz, col), (C(a0), h, C(b0), a0 / sz, -b0 / sz, col)])
    # the sunlight net (opaque) 2 over the floor, the coral (alpha-tested) 2 over that: they lay 1 unit apart (light over
    # the coral) and z-fought in melonDS (sweep_caves)
    if L.get('depth') is not None:           # underwater_polish: depth shading, caustics, kelp, light rays
        Depth(c).run(floor)
        return
    if L.get('seaweed'):
        tex, size = L['seaweed']
        put(tex, c.uw_seaweed & floor, 4 if L.get('light') else 2, size)
    if L.get('light'):
        tex, size = L['light']
        put(tex, c.uw_light & floor, 2, size)

# ------------------------------------------------------------------------------------------------ depth (look "depth")
# underwater_polish (2026-10-08). Black 2 draws deep water with vertex colours, not with a darker texture: the Abyssal
# Ruins' seabed (zone 241, chunk 555) is in59_sand at colour (0, 0.77, 1.0) in the lit middle, (0, 0.45, 0.81) further
# out and (0, 0.13, 0.26) at the edge of the bowl [bytes]. The Marine Tube's light rays (pack 61 h06_light01/02) are
# slanted translucent quads from the seabed up to the surface, 56 units wide at the bottom, 32 at the top, leaning
# 52-84 units west, cyan-white (184, 255, 255), brightest at the top [bytes]. Sapphire's own underwater tileset says how
# bright each trench tile is: Underwater1/2's trenches mid purple with lit dive circles (metatile 0x16, with Sapphire's
# diagonal light streaks), Underwater3/4's and the Sealed Chamber's trenches deep navy (luminance 9-38 of 255).
# Look keys (all optional except depth):
#   depth     {"lum": [l0, v0, l1, v1, gamma]  Sapphire metatile luminance l0..l1 -> trench floor colour v0..v1,
#              "top_near"/"top_far": rgb of the raised seabed at its lip / "fade" units further out ("fade": [start, length]),
#              "wall_top": wall colour factor at its top (the foot takes the floor's), "grid": [floor/wall units, top units],
#              "tol": colour error a triangle may keep before it is split}
#   caustics  [tex, units per repeat, min luminance]: Black 2's underwater light-disc caustics (in59_light_a, translucent)
#             2 over the floor of Sapphire's lit tiles (instead of the opaque sunlight net)
#   kelp      [tex, size]: one plant per seaweed tile (h06sango2, the Marine Tube's coral), turned/mirrored per tile,
#             shaded with the floor
#   rays      {"tex", "min_lum", "spacing" (tiles), "height", "lean", "width": [bottom, top], "v": [floor, top],
#              "color", "strips"}: light rays over Sapphire's lit tiles (Black 2's Marine Tube rays, in14_light_a's
#              gradient)
class Depth:
    def __init__(self, c):
        import numpy as np
        self.c, self.L, self.np = c, c.look, np
        self.P = dict(lum=[9, 0.42, 100, 1.0, 1.4], top_near=[0.0, 0.42, 0.76], top_far=[0.0, 0.16, 0.32],
                      fade=[16, 96], wall_top=1.0, grid=[16, 32], tol=0.035)
        self.P.update(self.L['depth'])
        self.fields()

    # ---- fields over the zone tiles of the matrix --------------------------------------------------------------
    def lum_of(self, mt):
        if not hasattr(Depth, '_lum'): Depth._lum = {}
        key = (tuple(self.c.sm['tilesets']), mt)
        if key not in Depth._lum:
            import os, sys
            np = self.np
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'converter'))
            from gba import Repo, MetatileRenderer
            if not hasattr(Depth, '_mr') or Depth._mr[0] != key[0]:
                repo = Repo(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'external', 'pokeruby'))
                Depth._mr = (key[0], MetatileRenderer(repo, *key[0]))
            a = np.asarray(Depth._mr[1].render(mt))[..., :3].astype(float)
            Depth._lum[key] = float((a @ [0.299, 0.587, 0.114]).mean())
        return Depth._lum[key]

    def floor_value(self, lum):
        l0, v0, l1, v1, g = self.P['lum']
        t = min(1.0, max(0.0, (lum - l0) / (l1 - l0)))
        return v0 + (v1 - v0) * t ** g

    def fields(self):
        from collections import deque
        np, c = self.np, self.c
        NX, NZ = c.NXT, c.NZT
        self.floors = set(c.source_tiles())
        self.lum = {}
        F = np.full((NZ, NX), np.nan)
        # a seaweed tile's art is mostly its kelp (darker than the seabed under it): it takes the floor around it
        weed = c.uw_seaweed
        for (x, z) in self.floors:
            self.lum[(x, z)] = l = self.lum_of(c.sm['mt'][z][x])
            if (x, z) in weed and len(weed & self.floors) < len(self.floors): continue
            if 0 <= c.ox + x < NX and 0 <= c.oz + z < NZ: F[c.oz + z, c.ox + x] = self.floor_value(l)
        # every other tile takes its nearest floor tile's value (walls rise from it)
        q = deque((j, i) for j, i in zip(*np.nonzero(~np.isnan(F))))
        while q:
            j, i = q.popleft()
            for dj, di in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                a, b = j + dj, i + di
                if 0 <= a < NZ and 0 <= b < NX and np.isnan(F[a, b]): F[a, b] = F[j, i]; q.append((a, b))
        if np.isnan(F).any(): F[np.isnan(F)] = self.floor_value(255)
        # Sapphire shades its trenches tile by tile; a 3x3 average makes that a gradient (fewer, smoother changes)
        b = self.P.get('blur', 1)
        if b:
            Fp = np.pad(F, b, mode='edge')
            F = sum(Fp[b + dj:b + dj + NZ, b + di:b + di + NX] for dj in range(-b, b + 1) for di in range(-b, b + 1)) / (2 * b + 1) ** 2
        Fp = np.pad(F, 1, mode='edge')
        self.Fc = (Fp[:-1, :-1] + Fp[:-1, 1:] + Fp[1:, :-1] + Fp[1:, 1:]) / 4     # (NZ+1, NX+1) tile corners
        # distance (units) from each tile corner to the nearest floor tile
        tiles = np.array([(c.ox + x, c.oz + z) for (x, z) in self.floors], float)
        gx, gz = np.meshgrid(np.arange(NX + 1) * 16.0, np.arange(NZ + 1) * 16.0)
        D = np.full(gx.shape, 1e9)
        for k in range(0, len(tiles), 256):
            t = tiles[k:k + 256]
            dx = np.maximum(0, np.abs(gx[..., None] - (t[:, 0] * 16 + 8)) - 8)
            dz = np.maximum(0, np.abs(gz[..., None] - (t[:, 1] * 16 + 8)) - 8)
            D = np.minimum(D, np.sqrt(dx * dx + dz * dz).min(axis=-1))
        self.Dc, self.NX, self.NZ = D, NX, NZ

    def edge(self, x, z):
        """1 inside, 0 at the matrix's edge: past it the screen is black (nothing is drawn there), so the seabed fades
        into it over "edge" units, as Black 2's caves fade their rim to black (colour 0 past the last lip)."""
        e = self.P.get('edge', 0)
        if not e: return 1.0
        X, Z = x + 256, z + 256
        d = min(X, Z, 512 * self.c.mw - X, 512 * self.c.mh - Z)
        t = min(1.0, max(0.0, d / e))
        return t * t * (3 - 2 * t)

    def bil(self, G, X, Z):
        np = self.np
        gx = min(max(X / 16.0, 0.0), self.NX - 1e-6); gz = min(max(Z / 16.0, 0.0), self.NZ - 1e-6)
        i, j = int(gx), int(gz); fx, fz = gx - i, gz - j
        return (G[j, i] * (1 - fx) * (1 - fz) + G[j, i + 1] * fx * (1 - fz) + G[j + 1, i] * (1 - fx) * fz
                + G[j + 1, i + 1] * fx * fz)

    # ---- colour of a vertex (model coordinates: local units - 256) ----------------------------------------------
    def top_rgb(self, x, z):
        d0, ln = self.P['fade']
        t = min(1.0, max(0.0, (self.bil(self.Dc, x + 256, z + 256) - d0) / ln))
        t = t * t * (3 - 2 * t)
        a, b = self.P['top_near'], self.P['top_far']
        return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))

    def floor_f(self, x, z):
        return self.bil(self.Fc, x + 256, z + 256)

    def wall_f(self, x, y, z):
        t = min(1.0, max(0.0, y / (16.0 * self.c.tiers)))
        return self.floor_f(x, z) * (1 - t) + self.P['wall_top'] * t

    def wall_rgb(self, x, y, z, base):
        f = self.wall_f(x, y, z)
        return tuple(b * f * k for b, k in zip(base, self.P.get('wall_tint', [1.0, 1.0, 1.0])))

    # ---- triangles split on the tile grid where the colour is not linear over them --------------------------------
    @staticmethod
    def _clip(poly, axis, at):
        lo, hi = [], []
        n = len(poly)
        for k in range(n):
            p, q = poly[k], poly[(k + 1) % n]
            sp, sq = p[axis] - at, q[axis] - at
            if sp <= 0: lo.append(p)
            if sp >= 0: hi.append(p)
            if (sp < 0 < sq) or (sq < 0 < sp):
                t = sp / (sp - sq)
                r = [a + (b - a) * t for a, b in zip(p, q)]
                lo.append(r); hi.append(r)
        return lo, hi

    def split(self, tri, G):
        """tri: [(x, y, z, u, v, (r, g, b))] -> polygons of [x, y, z, u, v, r, g, b, b0, b1, b2] on a G-unit grid."""
        import math
        poly = [list(v[:5]) + list(v[5]) + [1.0 if k == i else 0.0 for k in range(3)] for i, v in enumerate(tri)]
        pieces = [poly]
        for axis in (0, 2):
            lo_, hi_ = min(v[axis] for v in poly), max(v[axis] for v in poly)
            k0, k1 = math.floor(lo_ / G) + 1, math.ceil(hi_ / G) - 1
            for k in range(k0, k1 + 1):
                out = []
                for p in pieces:
                    a, b = self._clip(p, axis, k * G)
                    out += [q for q in (a, b) if len(q) >= 3]
                pieces = out
        return pieces

    def recolour(self):
        """Floors, tops and walls get the depth colours. A triangle over which the colour is not linear enough is split
        on the grid; a split triangle inserts vertices on its edges, and where such an edge is not axis-aligned (a
        rectangle's diagonal, a sloped wall edge) the triangle on the other side is split too: a vertex of one lying
        on the other's edge only to 4 decimals (the DAE's precision) left a crack (caves_check h, Underwater4)."""
        c, L = self.c, self.L
        top_y = 16 * c.tiers
        walls = {L.get(k) for k in ('face_low', 'face_low_rock', 'face_mid', 'lip_floor', 'lip_rock', 'stairs', 'ledge')}
        gf, gt = self.P['grid']
        tol = self.P['tol']
        items = []                                         # [mat, tri, kind, colours, pieces, split]
        for mat in list(c.m.tris):
            if mat not in walls and mat not in (L['floor'], L['top']): continue
            for tri in c.m.tris[mat]:
                ys = [v[1] for v in tri]
                if mat in walls: kind = 'wall'
                elif mat == L['top'] and (mat != L['floor'] or min(ys) > top_y - 1): kind = 'top'
                else: kind = 'floor'
                cs = [self.col(kind, v, v[5]) for v in tri]
                pieces = self.split(tri, gt if kind == 'top' else gf)
                worst = 0.0
                for pc in pieces:
                    for v in pc:
                        lin = [sum(v[8 + i] * cs[i][k] for i in range(3)) for k in range(3)]
                        f = self.col(kind, v, v[5:8])
                        worst = max(worst, max(abs(f[k] - lin[k]) for k in range(3)))
                items.append([mat, tri, kind, cs, pieces, len(pieces) > 1 and worst >= tol])
        # edges that get vertices inserted and are not axis-aligned: both sides split
        key = lambda v: (round(v[0], 3), round(v[1], 3), round(v[2], 3))
        edges = defaultdict(list)
        for i, it in enumerate(items):
            if len(it[4]) == 1: continue                     # (no grid line crosses it: inserts nothing)
            t = it[1]
            for a_, b_ in ((0, 1), (1, 2), (2, 0)):
                p, q = t[a_], t[b_]
                if sum(abs(p[k] - q[k]) > 1e-6 for k in range(3)) < 2: continue        # axis-aligned: exact
                G = gt if it[2] == 'top' else gf
                if not any(math.floor(min(p[k], q[k]) / G) != math.floor(max(p[k], q[k]) / G - 1e-9) for k in (0, 2)): continue
                edges[tuple(sorted((key(p), key(q))))].append(i)
        todo = [i for i, it in enumerate(items) if it[5]]
        while todo:
            i = todo.pop()
            t = items[i][1]
            for a_, b_ in ((0, 1), (1, 2), (2, 0)):
                for j in edges.get(tuple(sorted((key(t[a_]), key(t[b_])))), ()):
                    if not items[j][5]: items[j][5] = True; todo.append(j)
        out = defaultdict(list)
        for mat, tri, kind, cs, pieces, split in items:
            if not split:
                out[mat].append([tuple(v[:5]) + (tuple(round(a, 4) for a in cs[i]),) for i, v in enumerate(tri)])
                continue
            for pc in pieces:
                vs = [tuple(v[:5]) + (tuple(round(a, 4) for a in self.col(kind, v, v[5:8])),) for v in pc]
                for k in range(1, len(vs) - 1):
                    t3 = [vs[0], vs[k], vs[k + 1]]
                    ax, ay, az = (t3[1][j] - t3[0][j] for j in range(3))
                    bx, by, bz = (t3[2][j] - t3[0][j] for j in range(3))
                    area = abs(ax * bz - az * bx) + abs(ax * by - ay * bx) + abs(ay * bz - az * by)
                    if area > 1e-3: out[mat].append(t3)
        for mat in out: c.m.tris[mat] = out[mat]

    def col(self, kind, v, base):
        x, y, z = v[0], v[1], v[2]
        e = self.edge(x, z)
        if kind == 'top': return tuple(k * e for k in self.top_rgb(x, z))
        if kind == 'floor': f = self.floor_f(x, z) * e; return (f, f, f)
        return tuple(k * e for k in self.wall_rgb(x, y, z, base))

    # ---- decals ---------------------------------------------------------------------------------------------------
    def lit_tiles(self, floor, min_lum):
        return {t for t in floor if self.lum.get(t, 0) >= min_lum}

    def caustics(self, floor):
        import sys
        c = self.c
        tex, size, min_lum = self.L['caustics'][:3]
        col = tuple(self.L['caustics'][3]) if len(self.L['caustics']) > 3 else (1.0, 1.0, 1.0)
        C = lambda v: v - 256
        rects = sys.modules[type(c).__module__].rects            # (models_cave's, also when it runs as __main__)
        for x0, z0, x1, z1 in rects(self.lit_tiles(floor, min_lum)):
            X0, X1, Z0, Z1 = c.lx(x0), c.lx(x1 + 1), c.lz(z0), c.lz(z1 + 1)
            y = c.fy.get((x0, z0), 0) + 2
            c.m.quad(tex, [(C(X0), y, C(Z1), X0 / size, -Z1 / size), (C(X1), y, C(Z1), X1 / size, -Z1 / size),
                           (C(X1), y, C(Z0), X1 / size, -Z0 / size), (C(X0), y, C(Z0), X0 / size, -Z0 / size)], color=col)

    def kelp(self, floor):
        """Plants on the seaweed tiles: a big one (size) on every other tile of the checkerboard, 4 over the floor (the
        caustics lie at 2), reaching a little into its four neighbours; a small one (small) on the others, 2 higher (no
        coplanar overlap); quarter turn, mirror, place and shade vary per tile.
        depth 'kelp_style': 'stand' (map_glitch_fix 2026-10-09): flat on the floor the coral read as bright green blobs on
        a grid (1.75x the floor's brightness; Sapphire's seaweed is darker than its floor). Black 2 stands its seabed
        props up as cards leaning back 30 degrees from vertical, facing the camera (the Marine Tube's h06rock01, chunks
        310-315): two per seaweed tile, 13-18 units, the base near the tile's north edge, place, size and mirror
        varying per tile, shaded darker than the floor (kelp_tint); they hide a diver's legs as tall grass does."""
        c = self.c
        tex, big, small = (list(self.L['kelp']) + [None])[:3]
        if self.P.get('kelp_style') == 'stand':
            C = lambda v: v - 256
            for (x, z) in sorted(c.uw_seaweed & floor):
                h = int(hashlib.md5(f'{c.name}{x},{z}'.encode()).hexdigest()[:8], 16)
                f = self.floor_f(c.lx(x) + 8 - 256, c.lz(z) + 8 - 256) * (0.85 + 0.15 * ((h >> 14) & 7) / 7)
                col = tuple(round(k * f, 4) for k in self.P.get('kelp_tint', [0.55, 0.75, 0.65]))
                for k in range(2):
                    hk = h >> (8 * k)
                    sz = 13 + 5 * ((hk >> 3) & 7) / 7
                    cx = c.lx(x) + 4 + 8 * k + 3 * (((hk >> 9) & 7) / 7 - 0.5)
                    zb = c.lz(z) + 2 + 6 * k + 3 * (x % 2)   # (parallel cards at least 3 apart in z: 2.6 between
                                                             # their planes; nearer they z-fought, caves_check f)
                    yb = c.fy.get((x, z), 0) + 0.5
                    ht, back = 0.87 * sz, 0.5 * sz
                    u0, u1 = (1, 0) if (hk >> 2) & 1 else (0, 1)
                    c.m.quad(tex, [(C(cx - sz / 2), yb, C(zb), u0, 0, col), (C(cx + sz / 2), yb, C(zb), u1, 0, col),
                                   (C(cx + sz / 2), yb + ht, C(zb - back), u1, 1, col),
                                   (C(cx - sz / 2), yb + ht, C(zb - back), u0, 1, col)])
            return
        small = small or big
        C = lambda v: v - 256
        for (x, z) in sorted(c.uw_seaweed & floor):
            h = int(hashlib.md5(f'{c.name}{x},{z}'.encode()).hexdigest()[:8], 16)
            # big ones only where all eight neighbours are floor: their spill would lie on a wall's foot (0.0 apart
            # from its flat crease faces at 4, caves_check f)
            even = (x + z) % 2 == 0 and all((x + a, z + b) in self.floors for a in (-1, 0, 1) for b in (-1, 0, 1))
            s = big if even else small
            jit = (1.5 if even else max(0.0, (16 - s) / 2)) * 2
            X0 = c.lx(x) + 8 - s / 2 + jit * (((h >> 6) & 15) / 15 - 0.5)
            Z0 = c.lz(z) + 8 - s / 2 + jit * (((h >> 10) & 15) / 15 - 0.5)
            X1, Z1 = X0 + s, Z0 + s
            y = c.fy.get((x, z), 0) + (4 if even else 6)
            uv = [(0, 0), (1, 0), (1, 1), (0, 1)]                  # SW SE NE NW corners of the texture
            r = h % 4; uv = uv[r:] + uv[:r]
            if (h >> 2) & 1: uv = [(1 - u, v) for u, v in uv]
            f = self.floor_f(c.lx(x) + 8 - 256, c.lz(z) + 8 - 256) * (0.88 + 0.12 * ((h >> 14) & 7) / 7)
            col = tuple(round(k * f, 4) for k in self.P.get('kelp_tint', [0.82, 0.95, 0.86]))
            c.m.quad(tex, [(C(X0), y, C(Z1)) + uv[0] + (col,), (C(X1), y, C(Z1)) + uv[1] + (col,),
                           (C(X1), y, C(Z0)) + uv[2] + (col,), (C(X0), y, C(Z0)) + uv[3] + (col,)])

    def rays(self, floor):
        """Light rays over Sapphire's lit tiles, one per "spacing" tiles: Black 2's Marine Tube rays (pack 61
        h06_light01: slanted translucent quads from the seabed up, narrowing upward, leaning west, cyan-white) drawn with
        in14_light_a's gradient (white, alpha 0..238 over its rows), clear at the floor and at the top and brightest
        half way up: seen from the field camera a ray's upper end is off the screen or close to the camera, so it fades
        out there instead of ending in an edge."""
        c, R = self.c, self.L['rays']
        # none in front of an arch's dark tunnel from the camera (a ray south of a door in a north wall rises over it;
        # caves_check h took the tunnel's black behind the ray for a hole), and none right at an arch
        def clear(t):
            for a in c.arches:
                dx, dz = t[0] - a['x'], t[1] - a['z']
                if max(abs(dx), abs(dz)) <= 2: return False
                if a['face'] == 'n' and 0 < dz <= 9 and abs(dx) <= 6: return False
            return True
        lit = sorted(t for t in self.lit_tiles(floor, R.get('min_lum', 90)) if clear(t))
        # (map_glitch_fix 2026-10-09: and only where the floor spans the ray's foot, x-2..x+1 on its row: a ray standing
        # at a trench's edge dipped into the rock beside it and lay over the wall and the sand top as a pale box)
        if R.get('foot_on_floor'): lit = [(x, z) for x, z in lit if all((x + i, z) in floor for i in range(-2, 2))]
        sp = R.get('spacing', 4)
        anchors = []
        for (x, z) in sorted(lit, key=lambda t: int(hashlib.md5(f'{c.name}{t}'.encode()).hexdigest()[:8], 16)):
            if all(max(abs(x - a), abs(z - b)) >= sp for a, b in anchors): anchors.append((x, z))
        tex = R.get('tex', 'in14_light_a')
        H, lean = R.get('height', 128), R.get('lean', 48)
        wb, wt = R.get('width', [32, 18])
        v_edge, v_peak = R.get('v', [0.844, 0.531])
        col = tuple(R.get('color', [0.72, 1.0, 1.0]))
        import sys
        L = c.look
        tw_, th = sys.modules[type(c).__module__].set_images(L.get('tex_sets', {}).get(tex, L['set']))[tex].size
        # the gradient runs along v only (every texel of a row alike): u gets v's texel density, so the face is not
        # stretched one way (caves_check t)
        du = abs(v_peak - v_edge) * th / (H / 2) / tw_
        for (x, z) in anchors:
            h = int(hashlib.md5(f'{c.name}ray{x},{z}'.encode()).hexdigest()[:8], 16)
            cx, cz = c.lx(x) + 8 - 256, c.lz(z) + 8 - 256
            y0 = c.fy.get((x, z), 0) + 2
            for k, s in enumerate(R.get('strips', [1.0, 0.5])):
                ln = lean * (0.8 + 0.4 * ((h >> (4 * k)) & 15) / 15)
                dz = -2 * k                                      # strips 2 units apart (no coplanar overlap)
                def at(t):                                        # centre x and width at height fraction t
                    return cx - ln * t, (wb + (wt - wb) * t) * s
                for t0, t1, va, vb in ((0.0, 0.5, v_edge, v_peak), (0.5, 1.0, v_peak, v_edge)):
                    (xa, wa), (xb, wbb) = at(t0), at(t1)
                    ya, yb = y0 + H * t0, y0 + H * t1
                    u1 = wb * s * du
                    c.m.quad(tex, [(xa - wa / 2, ya, cz + dz, 0, va, col), (xa + wa / 2, ya, cz + dz, u1, va, col),
                                   (xb + wbb / 2, yb, cz + dz, u1, vb, col), (xb - wbb / 2, yb, cz + dz, 0, vb, col)])

    def edge_walls(self):
        """Trenches that run into the Sapphire map's edge (Underwater3's south and east edges, Underwater4's north edge:
        Sapphire joins Underwater3 and 4 there, Black 2's zones are not joined) had nothing between their floor and the
        seabed plane past the edge: the screen's background showed through the side. A cliff of the look's middle face
        closes them, from the floor to the top over the trench's width and the rock slopes beside it."""
        c, L = self.c, self.L
        C = lambda v: v - 256
        tex, us = L['face_mid'], L.get('face_u', 32)
        top = 16 * c.tiers
        ext = 32 * c.tiers                                   # (the rock beside reaches the top within that)
        sides = {'n': lambda x, z: z == 0, 'w': lambda x, z: x == 0, 'e': lambda x, z: x == c.W - 1}
        for side, on in sides.items():
            tiles = sorted(t for t in self.floors if on(*t))
            runs = []
            for t in tiles:
                a = t[0] if side == 'n' else t[1]
                if runs and a == runs[-1][1] + 1: runs[-1][1] = a
                else: runs.append([a, a])
            for a0, a1 in runs:
                lo, hi = 16 * a0 - ext, 16 * (a1 + 1) + ext
                lo = max(lo, 0); hi = min(hi, 16 * (c.W if side == 'n' else c.H))
                pts = list(range(int(lo), int(hi) + 1, 16))
                if pts[-1] != hi: pts.append(hi)
                for p0, p1 in zip(pts, pts[1:]):
                    if side == 'n':
                        Z = c.lz(0); X0, X1 = c.lx(0) + p0, c.lx(0) + p1
                        q = [(X0, 0, Z), (X1, 0, Z), (X1, top, Z), (X0, top, Z)]
                    elif side == 'e':
                        X = c.lx(c.W); Z0, Z1 = c.lz(0) + p0, c.lz(0) + p1
                        q = [(X, 0, Z0), (X, 0, Z1), (X, top, Z1), (X, top, Z0)]
                    else:
                        X = c.lx(0); Z0, Z1 = c.lz(0) + p0, c.lz(0) + p1
                        q = [(X, 0, Z1), (X, 0, Z0), (X, top, Z0), (X, top, Z1)]
                    vs = []
                    for (X_, Y_, Z_) in q:
                        u = (X_ if side == 'n' else Z_) / us
                        col = self.col('wall', (C(X_), Y_, C(Z_)), (1.0, 1.0, 1.0))
                        vs.append((C(X_), Y_, C(Z_), u, Y_ / 16, col))
                    c.m.quad(tex, vs)

    def run(self, floor):
        self.recolour()
        self.edge_walls()
        if self.L.get('caustics'): self.caustics(floor)
        if self.L.get('kelp'): self.kelp(floor)
        if self.L.get('rays'): self.rays(floor)
        if self.P.get('backdrop'): self.backdrop()

    def backdrop(self):
        """depth 'backdrop' [r, g, b] (map_glitch_fix 2026-10-09): one sheet of the floor texture 2 under the trench floor
        over the whole matrix, deep blue. The DS snaps vertices to whole pixels, so where the cave builder's long wall
        strips meet shorter cells (T-junctions: 2,388 in Underwater1) one-pixel seams open; the background behind them
        was black (pure black pixels in the shot). Through a seam the deep blue shows now, as the wall's own foot."""
        c, L = self.c, self.L
        C = lambda v: v - 256
        y = min(c.fy.values(), default=0) - 2
        col = tuple(self.P['backdrop'])
        fs = L.get('floor_size', 64)
        X1, Z1 = 512 * c.mw, 512 * c.mh
        c.m.quad(L['floor'], [(C(0), y, C(Z1), 0, -Z1 / fs, col), (C(X1), y, C(Z1), X1 / fs, -Z1 / fs, col),
                              (C(X1), y, C(0), X1 / fs, 0, col), (C(0), y, C(0), 0, 0, col)])

# ------------------------------------------------------------------------------------------------ collision hook
def collision(c, cells, flat_record):
    """Floor cells -> the Abyssal Ruins' swimmable cells; current tiles -> Black 2's current cells."""
    for (x, z), cls in c.uw_current.items():
        a, idx, _, _ = cells[(c.ox + x, c.oz + z)]
        cells[(c.ox + x, c.oz + z)] = (a, idx, cls, 0x02)
    if not c.r.get('underwater'): return
    for z in range(c.H):
        for x in range(c.W):
            key = (c.ox + x, c.oz + z)
            if key not in cells or not c.sm['walk'][z][x]: continue
            a, idx, cls, fl = cells[key]
            if cls in (0x0A, 0x3F):
                cells[key] = (a, idx, UW_CLASS, UW_FLAGS_ENC if (x, z) in c.uw_seaweed else UW_FLAGS)
