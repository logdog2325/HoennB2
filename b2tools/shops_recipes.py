"""Shops agent: room recipes for the gTileset_Shop rooms (data/interior_layouts/<Map>.json), written from the layouts
below (Sapphire tiles) so the eleven Poké Marts that share LAYOUT_POKE_MART get one design.

    python3 shops_recipes.py [MAP ...]          (default: every room of the shops family)

Furniture is placed by the model's BODY, not its bounding box: Black 2's furniture models carry a floor shadow quad
(texture *kage*) that sticks out to one side (pcshelf01: body x -14..14, z -8..8, box x -22..14, z -8..16), and
models_interior.py centres the box. piece() turns a wanted body centre into the recipe's "at" + dx/dz.
Back wall: Black 2's rooms stand it 12 units north of the first floor row (models_interior BACK), i.e. at row - 0.75.
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import models_interior as mi                          # noqa: E402

LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
T = 16.0
_body = {}


def body(name):
    """(x0, x1, y0, y1, z0, z1) of a model's own geometry without its shadow quads (model units)."""
    if name not in _body:
        import shops_preview as sp
        by_name, _ = mi.interior_models()
        res, pack, bmd = by_name[name]
        parts = [p for p in sp.pi.furniture_parts(res, pack) if 'kage' not in os.path.basename(p[0] or '')]
        P = np.concatenate([p[1].reshape(-1, 3) for p in parts])
        _body[name] = tuple(float(v) for v in (P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max(),
                                                P[:, 2].min(), P[:, 2].max()))
    return _body[name]


def rot_xz(x, z, rot):
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    return x * c + z * s, -x * s + z * c            # as models_interior.rotate_box


def footprint(name, rot=0):
    """Body footprint (w along x, d along z) in tiles after rotation."""
    x0, x1, _, _, z0, z1 = body(name)
    w, d = (x1 - x0) / T, (z1 - z0) / T
    return (w, d) if rot % 180 == 0 else (d, w)


def piece(m, cx, cz, rot=0, what='', **kw):
    """Furniture entry with the model's body centred on Sapphire tile point (cx, cz) (tile units)."""
    by_name, _ = mi.interior_models()
    bx0, bx1, _, _, bz0, bz1 = mi.bmd_box(by_name[m][2])
    x0, x1, _, _, z0, z1 = body(m)
    ox, oz = rot_xz((x0 + x1) / 2 - (bx0 + bx1) / 2, (z0 + z1) / 2 - (bz0 + bz1) / 2, rot)
    f = {'m': m, 'at': [round(cx, 4), round(cz, 4)]}
    if rot: f['rot'] = rot
    if abs(ox) > 1e-3: f['dx'] = round(-ox + kw.pop('dx', 0), 3)
    if abs(oz) > 1e-3: f['dz'] = round(-oz + kw.pop('dz', 0), 3)
    f.update(kw)
    if what: f['_what'] = what
    return f


def on_wall_n(m, cx, row, rot=0, gap=0.0, what='', **kw):
    """Body against the back wall north of floor row `row` (the wall stands at row - 12/16)."""
    _, d = footprint(m, rot)
    return piece(m, cx, row - 0.75 + gap / T + d / 2, rot, what, **kw)


def on_wall_e(m, col, cz, rot=270, gap=0.0, what='', **kw):
    """Body against the east wall of column `col` (the wall stands 3 units east of the column)."""
    w, _ = footprint(m, rot)
    return piece(m, col + 1 + 3 / T - gap / T - w / 2, cz, rot, what, **kw)


def on_wall_w(m, col, cz, rot=90, gap=0.0, what='', **kw):
    w, _ = footprint(m, rot)
    return piece(m, col - 3 / T + gap / T + w / 2, cz, rot, what, **kw)


def top_of(m):
    """Height to stand a model on top of m: m's top + 2 units (Black 2 keeps layered surfaces >= 2 apart)."""
    return body(m)[3] + 2


# ------------------------------------------------------------------------------------------------ the rooms
def mart(name):
    """LAYOUT_POKE_MART (11x8): Sapphire's Poké Mart. Rows 0-1 back wall (clock at (1,0)); row 1 = shop shelves along
    the wall: glass-front coolers (3-5) and two goods shelves (6-7, 8-9); glass counter: (2,1)-(2,4) and (0,4)-(1,4)
    with the register at (2,2), the clerk at (1,3) behind it; goods shelf block (6-7, 4-6); goods shelf against the east
    wall (10, 4-6); plant (10,3); exit mat (3-4, 7)."""
    c = top_of('shelf03')
    fur = [
        piece('shelf03', 2.5, 2.5, 90, 'glass counter (2,1)-(2,3), display toward the customers (east)'),
        piece('shelf03', 2.5, 4.0, 90, 'glass counter (2,3)-(2,4)'),
        piece('shelf03', 2.5 - footprint('shelf03', 90)[0] / 2 - footprint('shelf03')[0] / 2, 4.5, 0,
              'glass counter (0,4)-(1,4), display toward the customers (south)'),
        piece('cashier01', 2.5, 2.5, 90, 'register on the counter (2,2), keys toward the clerk', y=c),
        on_wall_n('in_vender01', 3.5, 1, what='glass-front cooler (3,1)'),
        on_wall_n('in_vender01', 4.5, 1, what='glass-front cooler (4,1)'),
        on_wall_n('in_vender01', 5.5, 1, what='glass-front cooler (5,1)'),
        on_wall_n('pcshelf01', 7.0, 1, what='goods shelf (6,1)-(7,1)'),
        on_wall_n('pcshelf01', 9.0, 1, what='goods shelf (8,1)-(9,1)'),
        piece('pcshelf01', 7.0, 5.0, 180, 'goods shelf block (6-7, 4-6), north side'),
        piece('pcshelf01', 7.0, 6.0, 0, 'goods shelf block (6-7, 4-6), south side'),
        on_wall_e('pcshelf01', 10, 5.5, what='goods shelf against the east wall (10, 4-6)'),
        piece('plant01', 10.5, 3.5, 0, 'potted plant (10,3)'),
    ]
    return dict(
        _doc=mart.__doc__.split('\n')[0] + ' ' + ' '.join(l.strip() for l in mart.__doc__.split('\n')[1:]).strip()
        + ' Black 2 pieces: Shopping Mall Nine floor/wall (style "shop"), its red entrance mat in45_mat01; glass counter = '
          'shelf03 (the display counter of Black 2\'s Pokémon Center mart, chunk 827) with cashier01; goods shelves = '
          'pcshelf01 (the Center mart\'s goods shelf); coolers = in_vender01 (glass-front drinks machine, one tile); '
          'clock = the pendulum clock picture in69_clock01 (texture set 350) as in Brendan\'s room.',
        map=name, style='shop', area_note='zone json "area": 326 (Shopping Mall Nine, pack 44)',
        floor=[[0, 1, 10, 7]],
        mats=[{'tex': 'in45_mat01', 'src': 326, 'rect': [3, 7, 4, 7], 'border': 0.25, 'border_units': 4, 'y': 0,
               '_what': 'red entrance mat (Shopping Mall Nine)'}],
        decals=[{'tex': 'in69_clock01', 'src': 350, 'at': [1.5], 'y': 18, 'w': 11, 'h': 22, 'gap': 2, '_what': 'wall clock (1,0)'}],
        furniture=fur)


def doc(f, extra=''):
    return ' '.join(l.strip() for l in f.__doc__.split('\n')).strip() + (' ' + extra if extra else '')


def counter_run(x0, x1, cz, what):
    """Glass counter (shelf03, display facing south) pieces along row cz from tile line x0 to x1, evenly spread."""
    w, _ = footprint('shelf03')
    n = max(1, round((x1 - x0) / w))
    step = (x1 - x0) / n
    # overlapping pieces: every other one 2 units lower, so the overlapped tops are not one plane (melonDS flickers)
    sink = lambda k: {'y': -2, 'dz': -2} if step < w - 0.01 and k % 2 else {}       # (and 2 back: fronts not one plane)
    return [piece('shelf03', x0 + step * (k + 0.5), cz, 0, f'{what} {k + 1}/{n}', **sink(k)) for k in range(n)]


def herb_shop(name):
    """LAYOUT_LAVARIDGE_TOWN_HERB_SHOP (11x8): rows 0-1 back wall with a poster (3,0) and the clock (4,0); glass-front
    coolers (0-1, 1) and (7-9, 1); long glass counter (0-4, 3) and the register counter (5, 2-3); the clerk at (3,2)
    behind it; goods shelf against the east wall (10, 3-5); herb planters (0-1, 7) and (9-10, 7); exit mat (3-4, 7)."""
    c = top_of('shelf03')
    fur = [on_wall_n('in_vender01', x + 0.5, 1, what=f'glass-front cooler ({x},1)') for x in (0, 1, 7, 8, 9)]
    fur += counter_run(0.0, 5.5 - footprint('shelf03', 90)[0] / 2, 3.5, 'glass counter (0-4, 3)')
    fur += [piece('shelf03', 5.5, 2.75, 90, 'register counter (5, 2-3)'),
            piece('cashier01', 5.5, 2.4, 0, 'register (5,2), keys toward the clerk', y=c),
            on_wall_n('poster01', 3.4, 2, what='poster on the wall (3,0)'),
            on_wall_e('pcshelf01', 10, 4.5, what='goods shelf against the east wall (10, 3-5)')]
    fur += [piece('plant01', x + 0.5, 7.4, 0, f'herb planter ({x},7)') for x in (0, 1, 9, 10)]
    return dict(_doc=doc(herb_shop, 'Floor: Black 2 Pokémon Center orange tiles (in02_yuka6, set 283) for Sapphire\'s orange '
                         'herb-shop floor (style "shop_herb"); coolers in_vender01, counter shelf03 + cashier01, shelf '
                         'pcshelf01, planters plant01, poster poster01, clock in69_clock01 (set 350).'),
                map=name, style='shop_herb', floor=[[0, 1, 10, 7]],
                mats=[{'tex': 'in45_mat01', 'src': 326, 'rect': [3, 7, 4, 7], 'border': 0.25, 'border_units': 4, 'y': 0,
                       '_what': 'red entrance mat (Shopping Mall Nine)'}],
                decals=[{'tex': 'in69_clock01', 'src': 350, 'at': [4.6], 'y': 18, 'w': 11, 'h': 22, 'gap': 2, '_what': 'wall clock (4,0)'}],
                furniture=fur)


def at_origin(m, ox, oz, rot=0, what='', **kw):
    """Furniture entry with the model's own origin at tile point (ox, oz) (as Black 2 places e.g. elevator01)."""
    by_name, _ = mi.interior_models()
    bx0, bx1, bz0, bz1 = mi.rotate_box(mi.bmd_box(by_name[m][2]), rot)
    f = {'m': m, 'at': [round(ox + (bx0 + bx1) / 2 / T, 4), round(oz + (bz0 + bz1) / 2 / T, 4)]}
    if rot: f['rot'] = rot
    f.update(kw)
    if what: f['_what'] = what
    return f


def stairs(x, row, up, what):
    """Sapphire stairs tile (x, row) in the back-wall row: up = stair_u01 rising north in a recess of the back wall (as
    Brendan's 1F), down = stair_d01 descending north in a floor opening (as Brendan's 2F). -> (furniture, floor_extra,
    holes)."""
    # Black 2's stair placement (models_interior.py STAIR_MODELS: the flight starts on the warp tile, sloped collision,
    # stair_d01's floor opening made by the builder; rooms_cleanup agent)
    if up:
        f = {'m': 'stair_u01', 'stair': [x, row], 'dir': 'N', '_what': what}
        return [f], [[x - 0.5, row - 1.5, x + 1.5, row]], []
    f = {'m': 'stair_d01', 'stair': [x, row], 'dir': 'N', '_what': what}
    return [f], [], []


def gondola(x0, z0, x1, z1, what):
    """A Sapphire goods-shelf block (tiles x0..x1, z0..z1): pcshelf01 pairs back to back (fronts north and south), one
    pair per two tiles of width, centred on the block."""
    out = []
    cz = (z0 + z1 + 1) / 2
    for k in range((x1 - x0 + 2) // 2):
        cx = x0 + 1 + 2 * k if x1 > x0 else x0 + 0.5
        out += [piece('pcshelf01', cx, cz - 0.5, 180, f'{what}, north side'), piece('pcshelf01', cx, cz + 0.5, 0, f'{what}, south side')]
    return out


def counter_end(x, z0, z1, what):
    """A counter side running north-south over tile rows z0..z1 (tile lines), shelf03 turned 90 (display east)."""
    _, d = footprint('shelf03', 90)
    n = max(1, round((z1 - z0) / d))
    step = (z1 - z0) / n
    sink = lambda k: {'y': -2, 'dx': -2} if step < d - 0.01 and k % 2 else {}       # (as counter_run)
    return [piece('shelf03', x + 0.5, z0 + step * (k + 0.5), 90, f'{what} {k + 1}/{n}', **sink(k)) for k in range(n)]


def service_counter(a, b, registers=(True, True)):
    """Sapphire's service counter: ends at (a,2) and (b,2), a run along row 3 between them (clerks stand in row 2
    behind it, customers talk across row 3 from row 4); registers on the ends."""
    c = top_of('shelf03')
    _, d = footprint('shelf03', 90)
    w, _ = footprint('shelf03')
    n = round((b - a - 1 + 2 * (1 - d) / 2) / w) or 1
    inner = n * w                                    # run length; the ends sit right against it
    x_l, x_r = (a + b + 1) / 2 - inner / 2, (a + b + 1) / 2 + inner / 2
    zc = 3.5 - 5 / T - 1.5 / 2 + 0.01                 # ends touch the run's north face
    out = [piece('shelf03', x_l - d / 2, zc, 90, f'counter end ({a},2)'),
           piece('shelf03', x_r + d / 2, zc, 90, f'counter end ({b},2)')]
    # registers centred on the end tiles: at the ends' own x (pulled in to touch the run) they reached 2 units into the
    # clerks' tiles (a+1,2) / (b-1,2) at head height, across the clerk's face (indoor_check, rooms_view.py kind m)
    if registers[0]: out.append(piece('cashier01', a + 0.5, 2.35, 90, f'register ({a},2), keys toward the clerks', y=c))
    if registers[1]: out.append(piece('cashier01', b + 0.5, 2.35, 270, f'register ({b},2), keys toward the clerks', y=c))
    out += [piece('shelf03', x_l + w * (k + 0.5), 3.5, 0, f'counter run ({a + 1}-{b - 1}, 3) {k + 1}/{n}') for k in range(n)]
    return out


def dept_store(name):
    """Lilycove Department Store floors (18x8): back wall rows 0-1 with the elevator (2,1) and the stairs (13,1) /
    (16,1) as Sapphire's warps say (up = stair_u01 in a wall recess, down = stair_d01 in a floor opening); counters,
    goods shelf blocks, coolers, windows, planters and plants at Sapphire's tiles (per floor below)."""
    floor = name.rsplit('_', 1)[1]
    W = 18
    c = top_of('shelf03')
    fur, extra, holes, decals, mats = [], [], [], [], []
    fur.append(at_origin('elevator01', 2.5, 1.0, 0, 'elevator door (2,1) (Black 2 places its origin one tile north of '
                         'the first walkable row, as chunks 836/1011)'))
    ups = {'1F': {16: True}, '2F': {13: True, 16: False}, '3F': {13: False, 16: True}, '4F': {16: False, 13: True},
           '5F': {13: False, 16: True}}[floor]
    for x, up in ups.items():
        f, e, h = stairs(x, 1, up, f'stairs {"up" if up else "down"} ({x},1)')
        fur += f; extra += e; holes += h
    style = {'1F': 'shop_herb', '5F': 'shop_pink'}.get(floor, 'shop')
    if floor in ('1F', '3F', '5F'):
        # service counter: ends at (a,2) and (b,2), glass run along row 3 between them, registers on both ends
        fur += service_counter(*((5, 11) if floor == '5F' else (6, 11)))
    if floor in ('2F', '4F'):
        # counter open to the south: glass run along row 5, sides (a, 5-7) and (b, 5-7), register on the left side
        a, b = (6, 11) if floor == '2F' else (6, 10)
        fur += counter_end(a, 5.0, 8.0, f'counter side ({a}, 5-7)') + counter_end(b, 5.0, 8.0, f'counter side ({b}, 5-7)')   # on rows 5-7 only (rooms_cleanup)
        _, d = footprint('shelf03', 90)
        fur += counter_run(a + 0.5 + d / 2, b + 0.5 - d / 2, 5.5, f'glass counter run ({a + 1}-{b - 1}, 5)')
        fur.append(piece('cashier01', a + 0.5, 6.5, 90, f'register ({a},6), keys toward the clerks', y=c))
    if floor == '1F':
        fur += [piece('plant01', x + 0.5, z + 0.45, 0, f'planter ({x},{z})') for x in (0, 1) for z in (5, 7)]
        fur += [piece('plant01', x + 0.5, 7.45, 0, f'potted plant ({x},7)') for x in (14, 16, 17)]
        fur += [piece('chushion01', 16.5, z + 0.5, 0, f'red stool ({z} walkable: a Black 2 floor cushion)') for z in (3, 5)]
        mats.append({'tex': 'in45_mat01', 'src': 326, 'rect': [8, 7, 9, 7], 'border': 0.25, 'border_units': 4, 'y': 0,
                     '_what': 'red entrance mat (Shopping Mall Nine)'})
    if floor == '2F':
        fur += [on_wall_n('win03', x + 0.5, 1, y=6, what=f'window ({x},1)') for x in (7, 10)]
        fur += gondola(2, 4, 3, 6, 'goods shelf block (2-3, 4-6)') + gondola(14, 4, 15, 6, 'goods shelf block (14-15, 4-6)')
        fur += [piece('plant01', 17.5, z + 0.45, 0, f'potted plant (17,{z})') for z in (4, 7)]
    if floor == '3F':
        fur += [on_wall_n('in_vender01', x + 0.5, 1, what=f'glass-front cooler ({x},1)') for x in (8, 9, 10)]
        fur += gondola(2, 4, 3, 6, 'goods shelf block (2-3, 4-6)') + gondola(14, 4, 15, 6, 'goods shelf block (14-15, 4-6)')
        decals.append({'tex': 'in69_clock01', 'src': 350, 'at': [7.5], 'y': 18, 'w': 11, 'h': 22, 'gap': 2, '_what': 'wall clock (7,0)'})
    if floor == '4F':
        fur += [on_wall_n('win02', x, 1, y=4, what=f'double window ({int(x) - 1}-{int(x)},1)') for x in (6.0, 10.0)]
        fur += gondola(1, 5, 2, 6, 'goods shelf block (1-2, 5-6)') + gondola(13, 5, 16, 6, 'goods shelf block (13-16, 5-6)')
    if floor == '5F':
        fur.append(on_wall_n('win03', 6.5, 1, y=6, what='window (6,1)'))
        fur.append(on_wall_n('art02', 8.5, 1, gap=2, y=10, what='the heart sign on the wall (7-9, 0-1): a framed picture'))
        fur += gondola(2, 4, 3, 6, 'doll shelf block (2-3, 4-6)') + gondola(6, 5, 7, 6, 'doll shelf block (6-7, 5-6)') \
            + gondola(10, 5, 11, 6, 'doll shelf block (10-11, 5-6)')
        # second counter (14-17, 5) with its side (14, 5-7)
        _, d = footprint('shelf03', 90)
        fur += counter_end(14, 5.0, 8.0, 'counter side (14, 5-7)')
        fur += counter_run(14.5 + d / 2, 18.0, 5.5, 'glass counter run (15-17, 5)')
    r = dict(_doc=doc(dept_store, {
        '1F': 'Orange floor (Black 2 Center tiles, as the Herb Shop). Service counter (6,2), (7-10,3), (11,2) with two '
              'registers; planters (0-1, 5) and (0-1, 7); plants (14,7), (16,7), (17,7); red stools on walkable (16,3) '
              'and (16,5) = floor cushions (Black 2 convention); exit mat (8-9, 7). Sapphire\'s floor-guide sign is at '
              '(0,8), outside the map: kept there.',
        '2F': 'Trainer\'s Zone. Windows (7,1), (10,1); shelf blocks (2-3, 4-6), (14-15, 4-6); counter open to the south '
              '(6-11, 5-7) with the register (6,6), clerks inside at (7,6) and (10,6); plants (17,4), (17,7).',
        '3F': 'Battle Collection. Clock (7,0); coolers (8-10, 1); counter (6,2), (7-10,3), (11,2); shelf blocks (2-3, 4-6), '
              '(14-15, 4-6).',
        '4F': 'TM Corner. Double windows (5-6, 1), (9-10, 1); shelf blocks (1-2, 5-6), (13-16, 5-6); counter open to the '
              'south (6-10, 5-7) with the register (6,6).',
        '5F': 'Poké Doll Floor: pink floor (chip_yuka2, texture set 326); window (6,1), the heart sign = art02; counter '
              '(5,2), (6-10,3), (11,2); doll shelf blocks (2-3, 4-6), (6-7, 5-6), (10-11, 5-6); second counter (14-17, 5) '
              'with its side (14, 5-7).'}[floor]),
        map=name, style=style, floor=[[0, 1, W - 1, 7]])
    if extra: r['floor_extra'] = extra
    if holes: r['holes'] = holes
    if mats: r['mats'] = mats
    if decals: r['decals'] = decals
    r['furniture'] = fur
    return r


def rooftop(name):
    """LAYOUT_LILYCOVE_CITY_DEPARTMENT_STORE_ROOFTOP (18x12; rows 7-11 are the store's facade below the roof, not
    walkable): the roof floor (1-16, 1-6) with the stairwell house (12-14, 1-3) and its door (13,3) down to 5F, the raised
    roof (15-17, 1-2); two vending machines (9-10, 1); planters (1-2, 3) and (1-2, 5); benches (5-6, 5) and (9-10, 5);
    chairs (16, 4-5) facing west."""
    fur = [on_wall_n('in_vender01', x + 0.5, 1, what=f'vending machine ({x},1): Black 2 tile attribute 0xE2 = its own '
                     'vending machine (Fresh Water / Soda Pop / Lemonade, Sapphire\'s three drinks)') for x in (9, 10)]
    fur.append(on_wall_n('cabin_door', 13.5, 3, gap=2, what='stairwell door (13,3) down to 5F'))
    fur += [piece('plant01', x + 0.5, z + 0.45, 0, f'planter ({x},{z})') for x in (1, 2) for z in (3, 5)]
    fur += [piece('chair01', x + 0.5, 5.5, 0, f'bench seat ({x},5)') for x in (5, 6, 9, 10)]
    fur += [piece('chair01', 16.5, z + 0.5, 270, f'chair ({z}) facing west') for z in (4, 5)]
    return dict(_doc=doc(rooftop, 'Style "shop_roof": grey roof tiles chip_yuka (texture set 326) and the sky with clouds '
                         'in39_sora (texture set 320) as the walls around the roof (Sapphire shows railings and sky); '
                         'vending machines in_vender01, door cabin_door, planters plant01, benches and chairs chair01 '
                         '(Black 2 puts chairs on solid tiles, as these are).'),
                map=name, style='shop_roof', floor=[[1, 1, 11, 6], [12, 3, 16, 6]],
                attrs=[{'attr': '0xe2', 'tiles': [[9, 1], [10, 1]], '_what': 'vending machine'}],
                furniture=fur)


def cycling_gate(name):
    """LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRACE (15x6, both gates): back wall rows 0-1 with the clock (6,0) and a
    notice (8,0); counter (5,2), (6-9,3), (10,2) with the clerk at (7,2); planters (6-9, 5); potted plants (0,5) and
    (14,5); exit mats (1-2, 5) and (12-13, 5)."""
    fur = service_counter(5, 10, registers=(False, False))
    fur += [piece('plant01', x + 0.5, 5.45, 0, f'planter ({x},5)') for x in (6, 7, 8, 9)]
    fur += [piece('plant01', x + 0.5, 5.45, 0, f'potted plant ({x},5)') for x in (0, 14)]
    fur.append(on_wall_n('poster01', 8.5, 2, what='notice on the wall (8,0)'))
    return dict(_doc=doc(cycling_gate, 'Orange floor as the Herb Shop (style "shop_herb"); counter shelf03, plants plant01, '
                         'notice poster01, clock in69_clock01 (texture set 350).'),
                map=name, style='shop_herb', floor=[[0, 1, 14, 5]],
                mats=[{'tex': 'in45_mat01', 'src': 326, 'rect': r, 'border': 0.25, 'border_units': 4, 'y': 0, '_what': 'entrance mat'}
                      for r in ([1, 5, 2, 5], [12, 5, 13, 5])],
                decals=[{'tex': 'in69_clock01', 'src': 350, 'at': [6.5], 'y': 18, 'w': 11, 'h': 22, 'gap': 2, '_what': 'wall clock (6,0)'}],
                furniture=fur)


def safari_gate(name):
    """LAYOUT_ROUTE121_SAFARI_ZONE_ENTRANCE (18x14): the hall (0-17, 1-5) with the clock (9,0), the PC (12,1), a notice
    (15,1), the counter (6,2), (7-10,3), (11,2) with two clerks (8,2), (10,2), planters (7-10, 5), a potted plant (0,5),
    cushions for the walkable chairs (14,3), (17,3), (17,4), the exit mat (2-3, 5) to the Safari Zone; the corridor
    (12-17, 6-13) down to Route 121 with the booth counter (16, 7-10) (clerk inside at (17,9)), plants (12,8), (12,13),
    (17,13) and the exit mat (14-15, 13)."""
    fur = service_counter(6, 11)
    fur.append(on_wall_n('pcdesk02', 12.5, 1, rot=90, what='PC (12,1): Black 2 tile attribute 0xD6 = its own PC'))
    fur.append(on_wall_n('poster01', 15.5, 2, what='notice on the wall (15,1)'))
    fur += [piece('plant01', x + 0.5, 5.45, 0, f'planter ({x},5)') for x in (7, 8, 9, 10)]
    fur += [piece('plant01', x + 0.5, z + 0.45, 0, f'potted plant ({x},{z})') for x, z in ((0, 5), (12, 8), (12, 13), (17, 13))]
    fur += [piece('chushion02', x + 0.5, z + 0.5, 0, f'chair ({x},{z}), walkable: a Black 2 floor cushion')
            for x, z in ((14, 3), (17, 3), (17, 4))]
    fur += counter_end(16, 7.0, 11.0, 'booth counter (16, 7-10)')
    fur += [piece('shelf03', 17.5, z, 0, f'booth end (17,{int(z)})') for z in (7.4, 11.4)]
    return dict(_doc=doc(safari_gate, 'Orange floor as the Herb Shop (style "shop_herb"); counters shelf03 + cashier01, '
                         'PC = pcdesk02 (the lab\'s PC desk), plants plant01, notice poster01, clock in69_clock01.'),
                map=name, style='shop_herb', floor=[[0, 1, 17, 5], [12, 6, 17, 13]],
                mats=[{'tex': 'in45_mat01', 'src': 326, 'rect': r, 'border': 0.25, 'border_units': 4, 'y': 0, '_what': 'entrance mat'}
                      for r in ([2, 5, 3, 5], [14, 13, 15, 13])],
                decals=[{'tex': 'in69_clock01', 'src': 350, 'at': [9.5], 'y': 18, 'w': 11, 'h': 22, 'gap': 2, '_what': 'wall clock (9,0)'}],
                furniture=fur)


MARTS = ['FallarborTown_Mart', 'FortreeCity_Mart', 'LavaridgeTown_Mart', 'MauvilleCity_Mart', 'MossdeepCity_Mart',
         'OldaleTown_Mart', 'PetalburgCity_Mart', 'RustboroCity_Mart', 'SlateportCity_Mart', 'SootopolisCity_Mart',
         'VerdanturfTown_Mart']
ROOMS = {m: mart for m in MARTS}
ROOMS['LavaridgeTown_HerbShop'] = herb_shop
for _f in ('1F', '2F', '3F', '4F', '5F'): ROOMS[f'LilycoveCity_DepartmentStore_{_f}'] = dept_store
ROOMS['LilycoveCity_DepartmentStoreRooftop'] = rooftop
ROOMS['Route110_SeasideCyclingRoadNorthEntrance'] = ROOMS['Route110_SeasideCyclingRoadSouthEntrance'] = cycling_gate
ROOMS['Route121_SafariZoneEntrance'] = safari_gate


def write(name):
    r = ROOMS[name](name)
    r.pop('area_note', None)
    path = os.path.join(LAYOUTS, name + '.json')
    with open(path, 'w') as f:
        f.write('{\n')
        keys = list(r)
        for i, k in enumerate(keys):
            v = r[k]
            end = ',' if i < len(keys) - 1 else ''
            if isinstance(v, list) and v and isinstance(v[0], dict):
                f.write(f' "{k}": [\n' + ',\n'.join('  ' + json.dumps(e, ensure_ascii=False) for e in v) + f'\n ]{end}\n')
            else:
                f.write(f' "{k}": {json.dumps(v, ensure_ascii=False)}{end}\n')
        f.write('}\n')
    return path


if __name__ == '__main__':
    for n in sys.argv[1:] or sorted(ROOMS):
        print(write(n))
