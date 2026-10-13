"""Mist caves for the cave builder (underwater_polish, 2026-10-08). Called from b2tools/models_cave.py at its hooks (end of
Cave.build_terrain, after the chunk split in build()), like models_cave_uw.py; active only for a cave whose room has a
mist weather in data/hoenn_weather.json "rooms" (Cave of Origin B2F-B4F, Seafloor Cavern Room 9 and their Ruby layouts
through "alt_of", Rusturf Tunnel), or with the recipe key "mist": true/false. Every other cave builds as before.

What the mist does there [code][bytes]: Black 2's weathers change the field light (ov036 0x02199734/0x02199740 ->
FieldLight_ChangeData(light, arc 61, file = arm9 table 0x02090124[weather], 60 or 1 frames)); mist 9 loads a/0/6/1
file 1, whose 14 time-of-day records give the fog colour 0x6318 (grey) and the clear colour of the sky: 0x7b10 light
blue by day, 0x4868 / 0x4d28 / 0x3f1f at night, dawn, dusk. FieldLight_FlushCore (ov036 0x02197abc) sets both,
FieldFog_SetColor(record fog) and gfxClearColor(record clear, alpha 31, depth 0x7fff, polygon id 0, fog FALSE): the
rear plane is never fogged, its colour is the sky's. A cave's own light (area 332: a/0/6/0 file 32) has clear 0 and
fog 0. So in a mist cave everything the terrain does not cover is light blue (past the map's edge, past the matrix,
one-pixel T-junction cracks), and the builder's black (the rim's colour-0 part past the last lip, the arches' tunnels)
takes the fog's grey with distance (patches/fixed_weather.py sets the fog flag on every Hoenn material).

Here: (1) the black: the rim's all-black triangles use the material VOID ("d29_gake2d"), the arch tunnels keep
"d0ana_002"; patches/fixed_weather.py leaves both without the fog flag, so they stay black; (2) a black VOID floor under the whole
matrix and an apron of it past the matrix's edges (edge chunks draw past their cell, as Black 2's own chunks do: the
Marine Tube's seabed spans -3088..3600), so no light blue shows anywhere; (3) under every flat rock top a copy of the
top 4 units lower: a crack between merged top strips shows rock instead of the background.
"""
import os, json

VOID = 'd29_gake2d'         # set 332's opaque near-black 16x16 (Relic Passage's), no Hoenn chunk uses it; drawn at
                            # colour 0. (d0ana_002, the inside arch's tunnel, has 37% transparent texels: as the void
                            # it let the light blue through in dots [test]; it stays unfogged for the tunnels)
MIST_WEATHERS = {9, 10, 11, 13, 14}
APRON = 256                 # units past the matrix's south edge (and the walls' reach past its corners)
UNDER = 4                   # the rock-top copy lies this far under the top (caves_check f: >= 1.95)

_rooms = None
def _weather_rooms():
    global _rooms
    if _rooms is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'hoenn_weather.json')
        _rooms = json.load(open(p)).get('rooms', {}) if os.path.exists(p) else {}
    return _rooms

def active(c):
    if 'mist' in c.r: return bool(c.r['mist'])
    v = _weather_rooms().get(c.r.get('alt_of') or c.name)
    return bool(v) and v.get('weather') in MIST_WEATHERS and c.look.get('set') == 332

# ------------------------------------------------------------------------------------------------ rooms
def room_active(room):
    """A room of the room builder (models_interior.Room) with a mist weather in data/hoenn_weather.json "rooms"
    (Lavaridge Gym 1F/B1F, Sapphire's WEATHER_FOG_1 steam), or recipe "mist": true/false (final_check 2026-10-08).
    Mist 9 swaps the room's light for the sky's too: past the room's walls the clear colour showed light blue [test]."""
    if 'mist' in room.r: return bool(room.r['mist'])
    v = _weather_rooms().get(room.r.get('map') or room.name)
    return bool(v) and v.get('weather') in MIST_WEATHERS

def room_geometry(room, m):
    """models_interior.build, after build_terrain: the void floor under the whole matrix (the walls and the apron past
    its edges follow after the chunk split: apron(room, parts)). The room's texture list takes VOID from set 332."""
    room.mist_y = min(v[1] for ts in m.tris.values() for t in ts for v in t) - 24
    _void_quad(m, -256, -256, 512 * room.mw - 256, 512 * room.mh - 256, room.mist_y)

# ------------------------------------------------------------------------------------------------ geometry hook
def geometry(c):
    """End of Cave.build_terrain: the black parts on VOID, the rock tops doubled underneath, the void floor."""
    m, L = c.m, c.look
    # (1) the rim's black (all three vertices colour 0) and the arch tunnels
    rim = m.tris.get(L['rim'], [])
    black = [t for t in rim if all(max(v[5]) == 0 for v in t)]
    if black:
        m.tris[L['rim']] = [t for t in rim if not all(max(v[5]) == 0 for v in t)]
        if not m.tris[L['rim']]: del m.tris[L['rim']]
        m.tris.setdefault(VOID, []).extend(black)
    # (3) the rock tops: every flat lattice cell of one height, merged per height, a copy UNDER units lower
    import numpy as np
    H = c.Hh; nz, nx = H.shape
    floors = c.source_tiles()
    by_h = {}
    tmax = 32 * c.tiers + 16
    for j in range(nz - 1):
        for i in range(nx - 1):
            if (i // 3, j // 3) in floors or (i // 3, j // 3) in c.cut: continue
            hs = (H[j, i], H[j, i + 1], H[j + 1, i], H[j + 1, i + 1])
            if max(hs) > 1e8 or max(hs) - min(hs) > 1e-6: continue
            ds = (c.D[j, i], c.D[j, i + 1], c.D[j + 1, i], c.D[j + 1, i + 1])
            if min(ds) < 16 - 1e-6 or min(ds) >= tmax - 1e-6: continue   # (floor cells, the first face band; the rim)
            by_h.setdefault(round(hs[0], 3), set()).add((i, j))
    C = lambda v: v - 256
    s, col = L.get('top_size', 16), (L.get('top_color', 0.77),) * 3
    for h, cells in by_h.items():
        for i0, j0, i1, j1 in _rects(cells):
            X0, X1, Z0, Z1 = c.LX[i0], c.LX[i1 + 1], c.LZ[j0], c.LZ[j1 + 1]
            y = h - UNDER
            m.quad(L['top'], [(C(X0), y, C(Z1), X0 / s, -Z1 / s, col), (C(X1), y, C(Z1), X1 / s, -Z1 / s, col),
                              (C(X1), y, C(Z0), X1 / s, -Z0 / s, col), (C(X0), y, C(Z0), X0 / s, -Z0 / s, col)])
    # (2) the void floor under the whole matrix
    c.mist_y = min(v[1] for ts in m.tris.values() for t in ts for v in t) - 24
    _void_quad(m, -256, -256, 512 * c.mw - 256, 512 * c.mh - 256, c.mist_y)

TILE = 128                  # the void is drawn in TILE-unit squares: the DS hides a whole polygon that crosses the
                            # far plane (POLYGON_ATTR bit 12 clear, as in Black 2's materials 0x001f8081: GBATEK),
                            # and one big quad vanished whole wherever its far end lay past it [test]

def _void_quad(m, x0, z0, x1, z1, y):
    k = (0.0, 0.0, 0.0)
    xs = list(range(int(x0), int(x1), TILE)) + [x1]
    zs = list(range(int(z0), int(z1), TILE)) + [z1]
    for a0, a1 in zip(xs, xs[1:]):
        for b0, b1 in zip(zs, zs[1:]):
            if a1 <= a0 or b1 <= b0: continue
            m.quad(VOID, [(a0, y, b1, a0 / 16, -b1 / 16, k), (a1, y, b1, a1 / 16, -b1 / 16, k),
                          (a1, y, b0, a1 / 16, -b0 / 16, k), (a0, y, b0, a0 / 16, -b0 / 16, k)])

def _rects(cells):
    """Greedy rectangles (i0, j0, i1, j1) covering a set of lattice cells."""
    left, out = set(cells), []
    for (i, j) in sorted(cells, key=lambda t: (t[1], t[0])):
        if (i, j) not in left: continue
        i1 = i
        while (i1 + 1, j) in left: i1 += 1
        j1 = j
        while all((a, j1 + 1) in left for a in range(i, i1 + 1)): j1 += 1
        for a in range(i, i1 + 1):
            for b in range(j, j1 + 1): left.discard((a, b))
        out.append((i, j, i1, j1))
    return out

# ------------------------------------------------------------------------------------------------ after the split
CURTAIN = 160               # height of the black walls standing on the matrix's north, west and east edges: below
                            # the camera's eye (~230 over the floor)

def _void_wall(m, side, at, a0, a1, y0, y1):
    """A vertical black wall on the chunk-local line x = at (side 'w'/'e') or z = at ('n'), facing into the matrix,
    in TILE squares."""
    k = (0.0, 0.0, 0.0)
    cs = list(range(int(a0), int(a1), TILE)) + [a1]
    ys = list(range(int(y0), int(y1), TILE)) + [y1]
    for c0, c1 in zip(cs, cs[1:]):
        for b0, b1 in zip(ys, ys[1:]):
            if c1 <= c0 or b1 <= b0: continue
            if side == 'n': q = [(c0, b0, at), (c1, b0, at), (c1, b1, at), (c0, b1, at)]           # faces south
            elif side == 'w': q = [(at, b0, c1), (at, b0, c0), (at, b1, c0), (at, b1, c1)]         # faces east
            else: q = [(at, b0, c0), (at, b0, c1), (at, b1, c1), (at, b1, c0)]                    # faces west
            m.quad(VOID, [v + ((v[0] if side == 'n' else v[2]) / 16, v[1] / 16, k) for v in q])

def apron(c, parts):
    """After models_interior.split_chunks (which clips every face to its chunk): the edge chunks draw black past the
    matrix (chunk-centred units). Black 2's field camera looks north and down: past the north, west and east edges a
    ray meets a wall standing on the edge (CURTAIN high) close by, before the far plane; past the south edge (under the
    camera) a floor APRON wide. All from the void floor's height up."""
    y = getattr(c, 'mist_y', -48)
    for cj in range(c.mh):
        for ci in range(c.mw):
            k = cj * c.mw + ci
            if parts[k] is None: continue
            m = parts[k]
            x0 = -256 - APRON if ci == 0 else -256
            x1 = 256 + APRON if ci == c.mw - 1 else 256
            if cj == 0: _void_wall(m, 'n', -256, x0, x1, y, y + CURTAIN)
            if ci == 0: _void_wall(m, 'w', -256, -256, 256 + (APRON if cj == c.mh - 1 else 0), y, y + CURTAIN)
            if ci == c.mw - 1: _void_wall(m, 'e', 256, -256, 256 + (APRON if cj == c.mh - 1 else 0), y, y + CURTAIN)
            if cj == c.mh - 1: _void_quad(m, x0, 256, x1, 256 + APRON, y)
    return parts
