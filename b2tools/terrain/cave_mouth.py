"""Black 2's cave mouths for Hoenn's outdoor cave entrances (cave_mouths agent, 2026-10-07; notes/TERRAIN_HEIGHTS.md
"Cave mouths"). Not a terrain module of its own: terrain/heights.py draws its cliffs through drawn() and calls draw().

How Black 2 draws a cave entrance on a route (its own chunks, apicula DAEs; [bytes]): always **terrain geometry in the
chunk**, never a building model (no exterior pack has a cave-mouth model; the chunks of Driftveil -> Clay Tunnel 48,
Mistralton -> Chargestone 59, Route 6 -> Chargestone 55, Route 7 -> Twist Mountain 63, Icirrus -> Twist Mountain 64,
Giant Chasm 84, Undella Bay -> Seaside Cave 263, Route 21 -> Seaside Cave 265, Route 3 -> Wellspring 14, Route 6 ->
Mistralton Cave 53, Undella -> Reversal Mountain 93, Route 20 -> Cave of Being 288, Route 22/23 -> Giant Chasm 303/304
place no model near the warp). The mouth is 16-22 triangles of one texture, `doukutu01` (Reversal Mountain's red
version `out57_doukutu`, chunk 298), set into a 2-tier cliff (16 + 16 units, one tile row per tier):
- a dark back wall sloping from the floor at the warp tile's north edge up 26 units to the next tile's north edge,
  dark side walls, and a floor shaded dark->light towards the front (u 0.38->0.59 of the texture) on the warp tile;
- a frame of the texture's rock rope (u 0.62-1.0) standing ~2 units in front of the face: two jambs (lower half from
  the pebble column, upper half rope) and a lintel under the upper tier's lip, which runs on over the opening;
- loose pebbles (u 0-0.31) on the tile in front;
- the cliff faces of both tiers are cut away over the opening (3 tiles for a 1-tile warp; the jambs hide the cut).
Chunk 55 (Route 6, 1-tile warp at (11, 19), ground 16) is the template copied here vertex for vertex (TEMPLATE), at
Black 2's own size: a 2-tile opening around Sapphire's 1-tile door (user choice 2026-10-07; the door and collision stay
Sapphire's: the tiles beside the door stay solid). OPENING = 1 narrows it to Sapphire's 1-tile opening.

Hoenn's mouths need that 2-tier rock: the heights module leaves most of Sapphire's cliff bands flat (only 2x2 blocks
of highland rise), so the rock around each mouth is raised **for drawing only** (collision is untouched): within 3
tiles left/right and 4 rows behind the door, rock tiles rise one tier per tile from the edge of the rock (Black 2's
2-tier profile; Cave of Being's free-standing mound, chunk 288), with the tiles over the opening at least 2 tiers up.
heights.py draws its faces from drawn(F) (the same lattice, lips and faces as every other Hoenn cliff); this module
adds the flat tops of the raised rock (gake_futa, Black 2's rock tops in chunks 55/288) and the mouth itself.

Sapphire's mouths are the bottom tile of a column of class cave_entrance (warp on the bottom tile, entered walking
north); all face south. Water entrances (Lilycove's cove, Route 120's Scorched Slab pond) get the same mouth at the
rock's height, no pebbles; the water module gives the water's edge under their rock (rock_shore) a rock bank. Textures: doukutu01, gake_futa (Hoenn's set
3 has both: 0 bytes); a standalone group's 'retex' renames them like its cliffs (data/hoenn_standalone.json).
"""
import sys

ROCK = {'cliff', 'cliff_top', 'mountain', 'cave_entrance', 'rock'}     # what the mouth's rock may stand on
WIDE, DEEP = 3, 4                    # the raised rock: x - WIDE .. x + WIDE, rows y - DEEP .. y (the door's row)
TIER = 16                            # Black 2's tier (one Gen 3 cliff row)
# the opening: 2 = Black 2's own size for a 1-tile warp (its chunks 48, 55, 63, 84: a 2-tile opening with the cliff cut
# over 3 tiles; user choice 2026-10-07), 1 = Sapphire's 1-tile mouth; screenshots/cave_mouths/width_1_vs_2.png
OPENING = 2
SPAN = 1 if OPENING == 1 else 2      # tiles on each side of the door that the mouth's frame and forced rock reach

def narrow(u, opening=None):
    """Black 2's mouth across (u from the warp tile's centre) -> Hoenn's: Black 2 opens 2 tiles for a 1-tile warp
    (|u| < 16), Sapphire's opening is 1 tile; the opening halves, the rope frame keeps Black 2's width (16) and stands
    in front of the neighbouring tiles' faces (|u| 8..24); the back and side walls (|u| 28) stay behind the frame."""
    if (opening or OPENING) == 2: return u
    a = abs(u)
    w = a / 2 if a <= 16 else (14 if a == 28 else a - 8)
    return w if u >= 0 else -w
TOP = 'gake_futa'
TEX = 'doukutu01'
PEBBLE_ON = {'grass', 'sand', 'path', 'cliff_top', 'ash_grass', 'mud', 'cracked_floor', None}

# Black 2 chunk 55 (Route 6 -> Chargestone Cave), the warp tile's mouth: (u, y', d) = (x - warp tile centre,
# y - ground, warp tile's south edge - z), DAE uv; and which way each piece faces (for the winding)
DARK, SIDE = (0.44, 0.09), (0.53, 0.03)
TEMPLATE = [
    # back wall, side walls (one dark texel each), floor (dark -> light towards the front)
    ('back', [(-28, 2, 16, DARK), (28, 2, 16, DARK), (28, 28, 32, DARK), (-28, 28, 32, DARK)], (0, 1, 1)),
    ('side', [(28, 28, 32, SIDE), (28, 2, 16, SIDE), (28, 2, 0, SIDE)], (-1, 0, 0)),
    ('side', [(-28, 2, 0, SIDE), (-28, 2, 16, SIDE), (-28, 28, 32, SIDE)], (1, 0, 0)),
    ('floor', [(28, 2, 0, (0.59, 1.0)), (28, 2, 16, (0.38, 1.0)), (-28, 2, 16, (0.38, 0.0)), (-28, 2, 0, (0.59, 0.0))], (0, 1, 0)),
    # jambs: lower part from the pebble column, upper part rope; left then right
    ('jamb', [(-16, 2, -2, (0.31, 0.03)), (-16, 12, 6, (0.31, 0.34)), (-32, 12, 8, (0.0, 0.34)), (-32, 2, 0, (0.0, 0.03))], (0, 0.5, 1)),
    ('jamb', [(-16, 24, 18, (0.62, -2.0)), (-32, 24, 20, (1.0, -2.0)), (-32, 12, 8, (1.0, -2.53)), (-16, 12, 6, (0.62, -2.53))], (0, 0.5, 1)),
    ('jamb', [(32, 12, 8, (0.0, 0.34)), (16, 12, 6, (0.31, 0.34)), (16, 2, -2, (0.31, 0.03)), (32, 2, 0, (0.0, 0.03))], (0, 0.5, 1)),
    ('jamb', [(32, 12, 8, (1.0, -2.53)), (32, 24, 20, (1.0, -2.0)), (16, 24, 18, (0.62, -2.0)), (16, 12, 6, (0.62, -2.53))], (0, 0.5, 1)),
    # lintel under the upper tier's lip (rope along it, 2.5 repeats over 48 units) and its corners
    ('lintel', [(-24, 28, 24, (0.91, -2.5)), (-16, 24, 18, (0.62, -2.12)), (16, 24, 18, (0.62, -0.38)), (24, 28, 24, (0.91, 0.0))], (0, 1, 1)),
    ('lintel', [(24, 28, 24, (0.91, -3.53)), (16, 24, 18, (0.62, -3.53)), (32, 24, 20, (1.0, -3.78))], (0, 1, 1)),
    ('lintel', [(-24, 28, 24, (0.91, -3.53)), (-32, 24, 20, (1.0, -3.41)), (-16, 24, 18, (0.62, -3.53))], (0, 1, 1)),
]
# loose pebbles on the tile in front (Black 2: two 16x16 patches at y' 2; here the first one, centred, at y' 3 so it
# stays 2+ units over Hoenn's sand plane at 0.5)
PEBBLES = PEBBLES_1 = [[(-8, -16, (0.31, 0.97)), (8, -16, (0.0, 0.97)), (8, 0, (0.0, 0.56)), (-8, 0, (0.31, 0.56))]]
if OPENING == 2:                     # (Black 2's two patches)
    PEBBLES = [[(-16, -16, (0.31, 0.97)), (0, -16, (0.0, 0.97)), (0, 0, (0.0, 0.56)), (-16, 0, (0.31, 0.56))],
               [(0, -16, (0.31, 0.53)), (16, -16, (0.31, 0.84)), (16, 0, (0.0, 0.84)), (0, 0, (0.0, 0.53))]]
PEBBLE_Y = 3
FRONT = 2.5    # the frame stands this much further out than Black 2's (whose outer jamb edges touch the face: Hoenn
               # keeps layered surfaces 2+ units apart, exterior_check.py layers)
FLAT_BESIDE = {'rock', 'sign', 'prop'}       # (Drawn.noface)
SHADOWED = {'sign', 'building', 'door', 'tree_bot', 'tree_top_l', 'tree_top_r', 'tree_tip', 'prop', 'rock'}

def _heights():
    return sys.modules.get('terrain.heights') or sys.modules.get('heights')

def _water_look(world, wx, wz):
    w = sys.modules.get('terrain.water')
    return w.look(world, wx, wz) if w is not None else None

def find(world):
    """Door tiles of Sapphire's cave mouths: the bottom tile of each column of class cave_entrance."""
    return sorted(k for k, e in world.items() if e[1] == 'cave_entrance'
                  and (world.get((k[0], k[1] + 1)) or (0, 0))[1] != 'cave_entrance')

def _emerald():
    v = sys.modules.get('version')
    return bool(v is not None and getattr(v, 'EMERALD', False))

def span(world, k):
    """Tiles on each side of door k that its frame reaches: SPAN, or (Emerald only, emerald_polish_outdoor 2026-10-12)
    1 = Sapphire's 1-tile opening (OPENING 1's geometry, narrow()) where the rock beside the door is less than two
    tiles wide on the door row or the row behind it. Black 2's 2-tile opening is 4 tiles of frame: on Emerald's
    Magma Hideout mouth in Jagged Pass (a 3-wide outcrop, stairs on its left, ash grass on its right) the jambs stood
    half over the stairs and in the open beside the outcrop. Every mouth of Sapphire's and Ruby's world, and every other
    mouth of Emerald's, has the rock (checked: emerald_polish_outdoor's tools/fieldprobe.py MOUTHS=1)."""
    if OPENING == 1 or not _emerald(): return SPAN
    x, y = k
    rock = lambda p: (world.get(p) or (0, None, True))[1] in ROCK and not world[p][2]
    return SPAN if all(rock(p) for p in ((x - 2, y), (x + 2, y), (x - 2, y - 1), (x + 2, y - 1))) else 1

class Drawn:
    """The height field heights.py draws cliffs from: its Field with the rock around each mouth raised (drawing only;
    collision, lifts and ground keep the Field's own heights)."""
    def __init__(self, F, over, mouths, world=None):
        self._F, self.over, self.mouths = F, over, mouths
        self.walk, self.slope, self.kind, self.rocktop = F.walk, F.slope, F.kind, F.rocktop
        self.rock = F.rock | set(over)               # raised rock gets rock lips (gake1_0), as Black 2's mouths
        # (dewford_fix 2026-10-12) a boulder or sign beside the raised rock, with nothing higher round it before, stays
        # flat at its height and the rock's skirt stands at its edge (heights.py 9d's rule for its own raised rock):
        # as the low tile it held the mound's face, the boulder buried in it (Route 106's by the Granite Cave fisherman)
        self.noface = set(F.noface)
        for k in over:
            for n in ((k[0] + a, k[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                e = (world or {}).get(n)
                if (e is None or e[1] not in FLAT_BESIDE or e[2] or n in over or n in F.walk or n in F.slope or
                        any(F.y(n[0] + a, n[1] + b) > F.y(*n) for a in (-1, 0, 1) for b in (-1, 0, 1))): continue
                self.noface.add(n)
        self.cut = {}                                # tile -> 'all' (door tile) or 'south' (the face over the opening)
        for m in mouths:
            if m.get('pillar'):                          # (a block's doorway: the door tile flat on the ground, its
                self.noface.add((m['x'], m['y'])); continue   #  sides and back the block's own skirts; see mouth())
            op = m.get('open', OPENING)
            for dx in range(1 - op, op):                 # (Black 2 cuts 3 tiles for its 2-tile opening)
                self.cut[(m['x'] + dx, m['y'])] = 'all'; self.cut[(m['x'] + dx, m['y'] - 1)] = 'south'

    def y(self, wx, wz):
        return self.over.get((wx, wz), self._F.y(wx, wz))

    def skip(self, k, j):
        """True when sub-quad row j (0 = north half) of face tile k lies in a mouth's opening."""
        c = self.cut.get(k)
        return c == 'all' or (c == 'south' and j == 1)

    def __getattr__(self, n):
        return getattr(self._F, n)

_DRAWN = {}
def drawn(F, world):
    """The Field heights.py draws with: F itself when the world has no cave mouth, else a Drawn (cached per Field)."""
    if id(F) in _DRAWN and _DRAWN[id(F)][0] is F: return _DRAWN[id(F)][1]
    ms = [mouth(F, world, k) for k in find(world)]
    over = {}
    for m in ms:
        for k, v in m['raise'].items(): over[k] = max(v, over.get(k, v))
    D = Drawn(F, over, ms, world) if ms else F
    _DRAWN.clear(); _DRAWN[id(F)] = (F, D)
    return D

def rock_shore(world):
    """Land tiles of the rock round a mouth entered from water (water.py gives their banks Black 2's rock shore)."""
    H = _heights()
    F = getattr(H, 'FIELD', None) if H else None
    if F is None: return set()
    D = drawn(F, world)
    return {k for mo in getattr(D, 'mouths', ()) if mo['wet'] for k in mo['rock']}

def mouth(F, world, k):
    """One mouth: base height, approach, and the rock raised around it (tile -> height)."""
    x, y = k
    cls = lambda p: (world.get(p) or (None, None))[1]
    ap = (x, y + 1)
    h = F.y(*ap)               # the ground (or the water's shore level) in front: the door tile itself is a face tile
                               # holding the lowest height around it (Route 115's door 0, its plateau 32)
    wet = _water_look(world, *ap) in ('pond', 'sea', 'deep', 'current', 'fall', 'shoal')
    win = {(x + dx, y + dz) for dx in range(-WIDE, WIDE + 1) for dz in range(-DEEP, 1)}
    A = {p for p in win if cls(p) in ROCK and p not in F.walk and p not in F.slope} | {k, (x, y - 1)}
    # the opening needs rock over it and beside it (a cliff); Sootopolis's Cave of Origin stands in a stone portal
    need = [(x - 1, y), (x + 1, y), (x - 1, y - 1), (x + 1, y - 1), (x, y - 2)]
    mound = all(p in A for p in need)
    sp = span(world, k)
    op = OPENING if sp == SPAN else 1
    # (emerald_polish_outdoor 2026-10-12, Emerald only) a door in a free-standing block of rock two rows deep with open
    # ground behind it (Emerald's Mirage Tower stand-in on Route 111: data/towns/emerald/Route111.json retiles its 3x2
    # base): no 2-tier mound fits (the frame's lintel and back wall need the second tier behind), and the portal
    # template left the cut faces open beside its 2-tile opening (holes, outdoor_check hole/cull) with its back wall
    # standing 12 units out of the block's top. The block rises 2 tiers (TIER * 2) and the door is a doorway into it:
    # the door tile stays on the ground (Drawn.noface), the block's skirts are the doorway's sides and back, draw()
    # adds a dark back, the floor, a lid and the lintel over a 26-unit opening, and the pebbles
    pillar = (not mound and _emerald() and (x, y - 2) not in A and
              all(p in A for p in ((x - 1, y), (x + 1, y), (x - 1, y - 1), (x + 1, y - 1), (x, y - 1))))
    raise_ = {}
    if pillar:
        sp, op = 1, 1
        for p in ((x - 1, y), (x + 1, y), (x - 1, y - 1), (x, y - 1), (x + 1, y - 1)):
            if h + 2 * TIER > F.y(*p): raise_[p] = h + 2 * TIER
    elif mound:
        # rock rises one tier per tile from its edge (8-neighbour distance to anything that is not rock, or outside
        # the window), at most two tiers: Black 2's 2-tier cliff / mound
        from collections import deque
        dist, q = {}, deque()
        for p in A:
            if any((p[0] + a, p[1] + b) not in A for a in (-1, 0, 1) for b in (-1, 0, 1)):
                dist[p] = 1; q.append(p)
        while q:
            p = q.popleft()
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    n = (p[0] + a, p[1] + b)
                    if n in A and n not in dist: dist[n] = dist[p] + 1; q.append(n)
        level = {p: min(2, dist.get(p, 1) - 1) for p in A}
        for dx in range(-sp, sp + 1):                # over the opening and its frame: tier 2 behind tier 1
            for dz, lv in ((-2, 2), (-1, 1), (0, 0)):
                if (x + dx, y + dz) in A: level[(x + dx, y + dz)] = lv
        for p, lv in level.items():
            frame = abs(p[0] - x) <= sp and p[1] >= y - 2
            if lv == 0 and not frame: continue
            v = h + TIER * lv
            if v > F.y(*p): raise_[p] = v
    look = cls(ap)
    rock = set(raise_) | ({(x + dx, y) for dx in range(-sp, sp + 1)} & A if mound else set())
    return {'x': x, 'y': y, 'h': h, 'wet': wet, 'mound': mound, 'raise': raise_, 'rock': rock,
            'span': sp, 'open': op, 'pillar': pillar,
            # (no pebbles where a sign's, building's or tree's shadow may reach the tile: both lie 2-3 units up)
            'pebbles': not wet and look in PEBBLE_ON and ap in F.walk and
                       not any(cls((ap[0] + a, ap[1] + b)) in SHADOWED for a in (-1, 0, 1) for b in (-1, 0, 1))}

def _oriented(pts, out):
    """pts (x, y, z, u, v) in order around the polygon; reversed when its normal points away from `out`."""
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = [p[:3] for p in pts[:3]]
    n = ((by - ay) * (cz - az) - (bz - az) * (cy - ay), (bz - az) * (cx - ax) - (bx - ax) * (cz - az),
         (bx - ax) * (cy - ay) - (by - ay) * (cx - ax))
    return pts if n[0] * out[0] + n[1] * out[1] + n[2] * out[2] >= 0 else pts[::-1]

def _poly(m, tex, pts, out):
    pts = _oriented(pts, out)
    if len(pts) == 3: m.tri(tex, pts)
    else: m.quad(tex, pts)

DOOR_H = 26                          # a block doorway's opening (pillar mouths), as high as the template's lintel's foot

def _doorway(m, xc, zs, h, H):
    """A pillar mouth's doorway (see mouth()): the door tile is a 1-tile notch into the 2-tier block, walled by the
    block's own skirts (heights.py: the door tile is flat on the ground, Drawn.noface). Here: the dark back 3 units in
    front of the notch's back skirt (outdoor_check layer keeps same-facing surfaces 2+ apart), the template's floor
    shading 3 units over the ground, a lid level with the block's top (gake_futa, as the raised rock's tops) and the
    rock over the opening from DOOR_H to the top in the skirts' own texture and mapping (heights._skirt: a wall over
    TALL units is yamagake01, v by TALL_REPEAT, u by x)."""
    top, back = h + 2 * TIER, zs - 13
    x0, x1 = xc - 8, xc + 8
    _poly(m, TEX, [(x0, h + 3, back, *DARK), (x1, h + 3, back, *DARK), (x1, h + DOOR_H, back, *DARK),
                   (x0, h + DOOR_H, back, *DARK)], (0, 0, 1))
    _poly(m, TEX, [(x1, h + 3, zs, 0.59, 1.0), (x1, h + 3, back, 0.38, 1.0), (x0, h + 3, back, 0.38, 0.0),
                   (x0, h + 3, zs, 0.59, 0.0)], (0, 1, 0))
    _poly(m, TOP, [(px, top, pz, px / 16, -pz / 16) for px, pz in ((x0, zs), (x1, zs), (x1, zs - 16), (x0, zs - 16))],
          (0, 1, 0))
    tall = 2 * TIER > H.TALL
    tex = 'yamagake01' if tall else 'gake01a'
    vv = lambda y: (y - h) / (H.TALL_REPEAT(2 * TIER) if tall else 2 * TIER)
    _poly(m, tex, [(x0, h + DOOR_H, zs, x0 / 16, vv(h + DOOR_H)), (x1, h + DOOR_H, zs, x1 / 16, vv(h + DOOR_H)),
                   (x1, top, zs, x1 / 16, vv(top)), (x0, top, zs, x0 / 16, vv(top))], (0, 0, 1))

def draw(m, cell, D):
    """This cell's mouths and the flat tops of the rock raised around them (heights.py's draw, after the cliffs)."""
    H = _heights()
    if not isinstance(D, Drawn): return
    bc = cell.bc
    X, Z = cell.X, cell.Z
    inside = lambda p: X <= p[0] < X + 32 and Z <= p[1] < Z + 32
    lat = H._lat(D)
    # flat tops of the raised rock: the lattice's flat parts at the tile's own (raised) height, which heights.py
    # leaves to world.py's ground (drawn at the Field's height, under the rock): same sub-quads and diagonals
    for k, L in D.over.items():
        if not inside(k): continue
        x0, z0 = bc.ux(k[0] - X), bc.uz(k[1] - Z)
        v = lat.lattice(k) if lat.face(k) else [[L] * 3 for _ in range(3)]
        for j in range(2):
            for i in range(2):
                if D.skip(k, j): continue
                hNW, hNE, hSE, hSW = v[j][i], v[j][i + 1], v[j + 1][i + 1], v[j + 1][i]
                a, b = x0 + 8 * i, z0 + 8 * j
                NW, NE, SE, SW = (a, hNW, b), (a + 8, hNE, b), (a + 8, hSE, b + 8), (a, hSW, b + 8)
                flat = lambda t: all(abs(p[1] - L) < 0.01 for p in t)
                if all(abs(q - L) < 0.01 for q in (hNW, hNE, hSE, hSW)): tris = [(SW, SE, NE), (SW, NE, NW)]
                elif abs(hNW - hNE) < 0.01 and abs(hSW - hSE) < 0.01 or abs(hNW - hSW) < 0.01 and abs(hNE - hSE) < 0.01:
                    continue                                    # (a sloped run quad: heights.py draws all of it)
                elif abs(hNW - hSE) <= abs(hNE - hSW): tris = [(SW, SE, NW), (SE, NE, NW)]
                else: tris = [(SW, SE, NE), (SW, NE, NW)]
                for t in tris:
                    if flat(t): _poly(m, TOP, [(px, py, pz, px / 16, -pz / 16) for px, py, pz in t], (0, 1, 0))
    for mo in D.mouths:
        if not inside((mo['x'], mo['y'])): continue
        xc, zs = bc.ux(mo['x'] - X) + 8, bc.uz(mo['y'] - Z) + 16
        h = mo['h']
        op = mo.get('open', OPENING)
        if mo.get('pillar'):
            _doorway(m, xc, zs, h, H)
        for kind, pts, out in (() if mo.get('pillar') else TEMPLATE):
            if not mo['mound'] and kind in ('jamb', 'lintel'): continue      # (in a stone portal: the opening only)
            q = []
            for u, yy, d, uv in pts:
                tu, tv = uv
                if kind == 'lintel' and len(pts) == 4: tv = (narrow(u, op) - narrow(24, op)) / 19.2   # (rope as dense as Black 2's)
                if kind == 'jamb' or kind == 'lintel' and yy < 28: d -= FRONT   # (the lintel's top meets the lip)
                x_ = narrow(u, op)
                if not mo['mound']: x_ = max(-8 * op, min(8 * op, x_))   # (a portal: walls of the opening)
                q.append((xc + x_, h + yy, zs - d, tu, tv))
            _poly(m, TEX, q, out)
        if (mo['mound'] or mo.get('pillar')) and mo['pebbles']:
            for patch in (PEBBLES if op == 2 else PEBBLES_1):
                _poly(m, TEX, [(xc + u, h + PEBBLE_Y, zs - d, tu, tv) for u, d, (tu, tv) in patch], (0, 1, 0))
