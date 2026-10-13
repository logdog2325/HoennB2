"""Sapphire's Abandoned Ship (the S.S. Cactus) on Route 108, drawn into the Route 108 cell's terrain model (world_fixes,
2026-10-06). Our Route 108 showed a grassy islet there: plan_map.py classes Sapphire's ship metatiles as building and
building roof, and nothing modelled them.

Sapphire (pokeruby data/maps/Route108, rendered by converter/render.py): the wreck lies in the shallows (MB_SHALLOW_WATER)
north of the sea lane, hull x 27.05..32.4, deck rows 3.67..5.0 in its 3/4 view, cream hull with a green waterline, khaki
deck planks, a deckhouse with a row of windows (x 28.5..31.6); its boarding stairs are the tile (29, 6)
(MB_STAIRS_OUTSIDE_ABANDONED_SHIP 0x1B: a north arrow warp, MetatileBehavior_IsNorthArrowWarp, and shallow flowing
water, MetatileBehavior_IsShallowFlowingWater: walkable, src/metatile_behavior.c).

Black 2's art: the ferry model c13_ship_01 (exterior packs 46/54/55, res 318; white hull, green waterline band, tan
deck, green window band) is the Black 2 passenger ship whose colours are closest to Sapphire's; its one texture
c13ship_01 (32x128, 16 colours, exterior building texture set a/1/7/4 46) has the hull side (rows 104-127: white,
grey, green), the deck (rows 96-103: tan planks) and the window band (rows 0-15, windows as colour-0 holes with
Black 2's glass h_mado behind them, as its own ships). New geometry in Sapphire's shape at Black 2's texel density
(1 texel a unit, the building rule, b2tools/buildings.py), not the model itself (its 240-unit hull scaled to 96 would
pack 2.5 texels into a screen pixel).

How it fits Black 2's door rules (world.py): Sapphire's stairs tile (29, 6) stays a walkable landing (a shoal tile at
the sea's height, water.py) and Black 2's door goes on the hull tile north of it, (29, 5), at the landing's height
(world.door_heights): surf onto the landing (you dismount), walk north into the ship; coming out you arrive on the
door tile on foot and step down onto the landing, then surf away. The hull and deckhouse tiles become unsurfable
water (water.py draws the sea under the hull, collision WATER_SOLID).
"""
import os
import buildings as B

CLASSES = set()                                   # (no tile classes of its own: retile() hands the tiles to water.py)
TEXTURES = {'c13ship_01': 'ext46', 'h_mado': 'ext46'}   # 'ext<N>': exterior building texture set a/1/7/4 entry N
WRAP = {'c13ship_01': ('WRAP', 'WRAP'), 'h_mado': ('WRAP', 'WRAP')}

# Sapphire map tiles: hull/deckhouse tiles (building, building roof) become unsurfable water; the stairs tile a shoal
SHIPS = {'Route108': dict(box=(27, 3, 32, 5), landing=(29, 6))}
_ORIGIN = {}                                      # map -> world tile of its Sapphire (0, 0) (set by retile)

def retile(world, maps):
    """world.py hook, after compose (main matrix): the ship's tiles as water.py's classes (see the docstring)."""
    for name, s in SHIPS.items():
        mp = maps.get(name)
        if mp is None: continue
        ox, oz = mp['ox'], mp['oz']; _ORIGIN[name] = (ox, oz)
        x0, z0, x1, z1 = s['box']
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                e = world.get((ox + x, oz + z))
                if e and e[1] in ('building', 'building_roof'): world[(ox + x, oz + z)] = (e[0], 'water', False)
        lx, lz = s['landing']
        world[(ox + lx, oz + lz)] = (name, 'puddle', True)

T = (32, 128)
HULL = B.Region('c13ship_01', T, 0, 104, 32, 128)      # white / grey / green waterline, top to bottom
DECK = B.Region('c13ship_01', T, 0, 96, 32, 104)       # tan planks (stripes along u)
BAND = B.Region('c13ship_01', T, 0, 0, 32, 16)         # deckhouse: white, grey, green band with two windows
GREY = B.Region('c13ship_01', T, 0, 109, 32, 116)      # light grey / grey (stairs, landing)
GLASS = B.Region('h_mado', (16, 16), 0, 0, 16, 16)

DECK_Y, BOTTOM_Y, HOUSE_Y = 8, -12, 24                # deck, hull bottom (the green band rises 3 over the sea, -11), roof
WATER_Y = -8                                          # the landing's collision height (shoal, water.py)

def draw(m, cell):
    for name, s in SHIPS.items():
        if name not in _ORIGIN: continue
        ox, oz = _ORIGIN[name]
        X, Z = cell.X, cell.Z
        x0, z0, x1, z1 = s['box']
        if not (X <= ox + x0 and ox + x1 < X + 32 and Z <= oz + z0 and oz + z1 < Z + 32): continue
        ux = lambda x: (ox + x - X) * 16 - 256      # Sapphire map tile coordinate -> chunk units
        uz = lambda z: (oz + z - Z) * 16 - 256
        ship(m, ux, uz, s['landing'])

def ship(m, ux, uz, landing):
    up = (0, 1, 0)
    # hull: bow tip at x 27.05 (mid-deck), sides x 27.9..32.45, deck z 3.67..5.0 (Sapphire's deck rows)
    bx, sx, ex, zn, zs = ux(27.05), ux(27.9), ux(32.45), uz(3.67), uz(5.0)
    zm = (zn + zs) / 2
    rep = (32, DECK_Y - BOTTOM_Y)                     # the 24 hull rows over 20 units: the green shows at the waterline
    B.rect(m, HULL, (sx, BOTTOM_Y, zs), (1, 0, 0), up, ex - sx, DECK_Y - BOTTOM_Y, rep)        # side, faces south
    B.rect(m, HULL, (ex, BOTTOM_Y, zs), (0, 0, -1), up, zs - zn, DECK_Y - BOTTOM_Y, rep)       # stern, faces east
    L = ((sx - bx) ** 2 + (zs - zm) ** 2) ** 0.5                                               # bow, faces south-west
    B.rect(m, HULL, (bx, BOTTOM_Y, zm), ((sx - bx) / L, 0, (zs - zm) / L), up, L, DECK_Y - BOTTOM_Y, rep)
    # (north-facing faces are never seen: Gen 5's camera looks north)
    B.face(m, DECK, (0, DECK_Y, 0), (1, 0, 0), (0, 0, -1),                                    # deck, faces up
           [(bx, -zm), (sx, -zs), (ex, -zs), (ex, -zn), (sx, -zn)], (32, 8))
    # deckhouse x 28.5..31.55, z 3.8..4.85, 16 high, the window band on its walls and Black 2's glass behind them
    hx0, hx1, hz0, hz1 = ux(28.5), ux(31.55), uz(3.8), uz(4.85)
    B.box_walls(m, hx0, hx1, hz0, hz1, DECK_Y, HOUSE_Y, BAND, (32, 16), sides='sew')
    B.face(m, DECK, (0, HOUSE_Y, 0), (1, 0, 0), (0, 0, -1),
           [(hx0, -hz1), (hx1, -hz1), (hx1, -hz0), (hx0, -hz0)], (32, 8))
    g0, g1 = DECK_Y + 2, HOUSE_Y - 2                  # glass 2 units inside the walls (Black 2's layer spacing)
    B.rect(m, GLASS, (hx0 + 2, g0, hz1 - 2), (1, 0, 0), up, hx1 - hx0 - 4, g1 - g0, (16, 16))
    B.rect(m, GLASS, (hx1 - 2, g0, hz1 - 2), (0, 0, -1), up, hz1 - hz0 - 4, g1 - g0, (16, 16))
    B.rect(m, GLASS, (hx0 + 2, g0, hz0 + 2), (0, 0, 1), up, hz1 - hz0 - 4, g1 - g0, (16, 16))
    # boarding stairs on the door tile (landing x, row 5): steps from the water up the hull side to the deck in the
    # tile's north part (z 5.0..5.3), so a player arriving through the door (on the tile's centre, z 5.5, at the
    # landing's height) stands in front of them, in the shallows, as on Sapphire's stairs tile
    lx = landing[0]
    a, b = ux(lx + 0.2), ux(lx + 0.8)
    zf = uz(5.3)
    z0 = zs + 2                                       # (no riser closer than 2 units to the hull side: melonDS flicker)
    foot = WATER_Y - 4                                # (the lowest riser starts under the sea's surface, -11)
    steps = 4
    for k in range(steps):                            # step k: tread at WATER_Y + (k+1)*4, z from z0 + .. back to z0
        y = WATER_Y + (DECK_Y - WATER_Y) * (k + 1) / steps
        zb, zfr = z0 + (zf - z0) * (steps - 1 - k) / steps, z0 + (zf - z0) * (steps - k) / steps
        if k == steps - 1: zb = zs                    # (the top tread reaches the deck's edge)
        yl = WATER_Y + (DECK_Y - WATER_Y) * k / steps if k else foot
        B.rect(m, GREY, (a, yl, zfr), (1, 0, 0), up, b - a, y - yl, (32, 7))                    # riser, faces south
        B.face(m, GREY, (0, y, 0), (1, 0, 0), (0, 0, -1), [(a, -zfr), (b, -zfr), (b, -zb), (a, -zb)], (32, 7))
    for x, sgn in ((a, -1), (b, 1)):                  # stringers (side faces)
        pts = [(zs, foot), (zf, foot), (zf, WATER_Y), (zs, DECK_Y)]
        u = (0, 0, -1) if sgn > 0 else (0, 0, 1)
        outline = [(-z if sgn > 0 else z, y) for z, y in pts]
        if sgn > 0: outline = outline[::-1]
        B.face(m, GREY, (x, 0, 0), u, up, outline, (32, 7))
