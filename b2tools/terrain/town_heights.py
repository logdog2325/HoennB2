"""Town terraces (town_look heights pass, phase H1 prototype, 2026-11-09): Black 2-style raised ground in some towns.

On in every build (user approved, phase H2 2026-11-09: Sapphire, Ruby and Emerald worlds alike); HOENN_TOWN_HEIGHTS=0
turns it off (the flat towns of v2.1, for comparisons). Checks and the impact tool: work/agents/town_look/h1.

Hooked in heights.height_field as step 10c (after the ground textures) and heights.draw (restyle, after its own rock
styles). F.town_tiles / F.town_style / F.town_stairs are this module's; heights' STYLES and F.style are left alone, so
no cell without a terrace changes (a 'town' entry in STYLES made _restyle cut every red-rock cell's faces).

Rule kept by every design: every walkable tile stays walkable (classes and flags are untouched; only heights move), and
every step between two walkable tiles stays under Black 2's 20 units (ov012 field_actor_tool.c:490-525) - the way up is
Black 2's stairs (45-degree planes, 16 a tile; Accumula chunk 5's 8-a-tile flights where two rows climb one level),
so the moves Black 2 allows are the same before and after. Solid tiles inside a design (buildings, fences, lamp bases,
bushes, the sign) stand on the level they belong to; Gen 3's harbour walls (class wall) stay where they are, their tops
(ground.py draw_walls, 16 units) level with a deck raised 16.

Designs, in each map's plan coordinates (the same tiles in Sapphire, Ruby and Emerald; Rustboro's lamp pairs in Devon's
forecourt stand one row further north in Sapphire/Ruby, which the stair rule below covers):
  RustboroCity  'devon'  Devon Corporation and its forecourt on a terrace 16 up: the building, rows 7-16 of x 7-16, and
                         the fences beside it (x 6 and x 17, rows 8-18, and the east corner x 16-17 row 19: railings on
                         the terrace's retaining walls); a
                         two-row flight (rows 17-18, 8 a row) down to the street, its lamp bases standing on pedestals at
                         the terrace's level between three flights.
  SlateportCity 'pier'   the Oceanic Museum's walled pier (x 25-35, rows 23-29) at the top of its quay walls (16 up);
                         the causeway from the town (x 23-24, rows 27-28) is a flight climbing east, 8 a tile, between
                         the walls (the Team Aqua/Magma queue and Emerald's Scott walk stand / walk on it).
"""
import os

ON = os.environ.get('HOENN_TOWN_HEIGHTS', '1') != '0'
STYLE = 'town'                    # F.town_style value: Black 2's stone walls instead of rock on these terraces' skirts
STYLE_TEX = {'gake01a': 't02_kabe01', 'yamagake01': 't02_kabe01', 'gake1_0': 't02_kiwa', 'gake1_1': 't02_kiwa',
             'gake_michi': 'gake_michi'}

DESIGNS = {
    'RustboroCity': [dict(name='devon', up=16, rects=[(7, 7, 16, 16), (6, 8, 6, 18), (17, 8, 17, 18), (16, 19, 17, 19)],
                          flight=dict(rect=(7, 17, 16, 18), rise='n', per=8, pedestal={'prop'}))],
    'SlateportCity': [dict(name='pier', up=16, rects=[(25, 23, 35, 29)], keep={'wall'},
                           flight=dict(rect=(23, 27, 24, 28), rise='e', per=8, pedestal=set()))],
}

def tiles(r):
    x0, z0, x1, z1 = r
    return [(x, z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)]

def apply(F, world, maps):
    """After height_field's step 9 (every tile has its height): lift the designs' tiles, lay their flights."""
    F.town_stairs, F.town_tiles, F.town_style = set(), {}, {}
    if not ON: return
    for name, designs in DESIGNS.items():
        if name not in maps: continue
        ox, oz = maps[name]['ox'], maps[name]['oz']
        W = lambda x, z: world.get((ox + x, oz + z))
        for d in designs:
            keep = d.get('keep', set())
            y0 = dict(F.h)           # (heights before this design: a flight starts from the street's own level)
            Y0 = lambda wx, wz: y0.get((wx, wz), 0)
            for r in d['rects']:
                for x, z in tiles(r):
                    e = W(x, z); k = (ox + x, oz + z)
                    if e is None or e[0] != name or e[1] in keep: continue
                    F.h[k] = F.y(*k) + d['up']; F.town_tiles[k] = d['name']
            fl = d['flight']; x0, z0, x1, z1 = fl['rect']; per = fl['per']
            for x, z in tiles(fl['rect']):
                e = W(x, z); k = (ox + x, oz + z)
                if e is None or e[0] != name: continue
                F.town_tiles[k] = d['name']
                if e[1] in fl['pedestal'] or not e[2]:          # solid (or a lamp's walkable top): a pedestal, level up
                    base = Y0(ox + x, oz + z1 + 1) if fl['rise'] == 'n' else Y0(ox + x0 - 1, oz + z)
                    F.h[k] = base + d['up']; continue
                if fl['rise'] == 'n':                         # rows climbing north from the tile south of the flight
                    i = z1 - z; base = Y0(ox + x, oz + z1 + 1)
                    F.slope[k] = ('n', base + per * i, per)
                else:                                         # columns climbing east from the tile west of it
                    i = x - x0; base = Y0(ox + x0 - 1, oz + z)
                    F.slope[k] = ('e', base + per * i, per)
                F.h[k] = round(base + per * (i + 0.5)); F.kind[k] = 'stairs'; F.town_stairs.add(k)
    # stone skirts and faces (restyle) on the designs' tiles; no cliff profile in a kept wall (draw_walls' block)
    F.town_style = {k: STYLE for k in F.town_tiles}
    for k in list(F.town_tiles):          # (and the solid tiles round them that hold the step: stone, not rock)
        for n in ((k[0] + dx, k[1] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
            if n in world and n not in F.town_tiles and not world[n][2] and n not in F.style and \
                    world[n][1] not in ('cliff', 'cliff_top', 'mountain', 'rock', 'cave_entrance'):
                F.town_style[n] = STYLE
                F.noface.add(n)           # (a fence, sign or lamp beside a terrace holds no 45-degree rock corner: a
                                          #  plain wall at the edge instead; glitch check 2026-11-10, Rustboro (64-65,199))
    for name, designs in DESIGNS.items():
        if name not in maps: continue
        ox, oz = maps[name]['ox'], maps[name]['oz']
        for d in designs:
            for r in d['rects']:
                for x, z in tiles((r[0] - 1, r[1] - 1, r[2] + 1, r[3] + 1)):     # (the pier: its walls and the sea
                    k = (ox + x, oz + z)                                            #  round it hold no rock corner)
                    if d.get('keep') and k in world and k not in F.town_tiles: F.noface.add(k)

def restyle(m, cell, F):
    """heights.draw's last step for a cell near a terrace: its rock skirts / faces on the terraces' tiles (F.town_style)
    become Black 2's stone wall and coping (cut at the style's edge as heights._restyle does), with their own UVs."""
    st = getattr(F, 'town_style', None)
    X, Z = cell.X, cell.Z
    if not st or not any((X + a, Z + b) in st for a in range(-1, 33) for b in range(-1, 33)): return
    from terrain import heights as H
    moved = {}
    for mat in [t for t in list(m.tris) if t in STYLE_TEX and STYLE_TEX[t] != t]:
        keep = []
        for t in m.tris[mat]:
            for s_, piece in H._style_pieces(t, st, X, Z):
                (moved.setdefault(STYLE_TEX[mat], []) if s_ else keep).append(piece)
        if keep: m.tris[mat] = keep
        else: del m.tris[mat]
    tmp = type(m)(m.name)
    for mat, tris in moved.items(): tmp.tris[mat] = tris
    fix_uv(tmp)
    for mat, tris in tmp.tris.items(): m.tris.setdefault(mat, []).extend(tris)

def fix_uv(m):
    """The restyled skirts keep gake01a's UVs (one image over 16 units): Black 2's wall (t02_kabe01, a texel a unit,
    its top row at the wall's top) and coping (t02_kiwa, 8 units an image) need their own."""
    for mat in ('t02_kabe01', 't02_kiwa'):
        for t in m.tris.get(mat, []):
            ys = [v[1] for v in t]; top = max(ys)
            (ax, ay, az), (bx, by, bz), (cx, cy, cz) = [v[:3] for v in t]
            n = ((by - ay) * (cz - az) - (bz - az) * (cy - ay), (bz - az) * (cx - ax) - (bx - ax) * (cz - az),
                 (bx - ax) * (cy - ay) - (by - ay) * (cx - ax))
            vertical = abs(n[1]) < 0.3 * (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
            for i, (x, y, z, u, v, c) in enumerate(t):
                if mat == 't02_kabe01':           # (a wall's face, upright or a lattice face's slant: along its run)
                    along = z if abs(n[0]) > abs(n[2]) else x
                    t[i] = (x, y, z, (along + 256) / 32, 1 - (top - y) / 64, c)
                else:
                    t[i] = (x, y, z, (x + 256) / 8, -(z + 256) / 8, c)
