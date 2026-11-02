"""Route 119's Feebas (user 2026-11-01; gen_docs' wild pages say it): the fishing spots were never built, so Feebas and
Milotic could not be obtained. The code is the decomp's
src/hoennb2/resident/feebas.c, as Gen 3's src/wild_encounter.c: on Route 119, a bite while facing one of 6 spots is a Feebas
half the time (levels 20-25 on our level curve), else the route's table. build_rom.py adds this patch itself when our C is on.

This patch fills gHoennB2Feebas in the resident pool: the zone, the levels, and every fishing spot of Gen 3's Route 119 as
{world x, world z, Gen 3's spot number}: the surfable, non-waterfall tiles (MetatileBehavior_IsFeebasEncounterable), numbered as
GetFeebasFishingSpotId does, row by row in three sections (y 0-45 from 0, 46-91 from 131, 92-139 from 298: 447 in all; pokeruby's
gRoute119WaterTileData = pokeemerald's sRoute119WaterTileData), each version from its own map (pokeruby / pokeemerald). Gen 3's
tile (x, y) is world tile (ox + x, oz + y): the map's origin as world.py compose() computes it. The seed is the save's trainer ID
(Gen 3's, Dewford's trendy phrase, isn't in this game): the spots are fixed for a save.

    python3 feebas.py [TRAINER_ID]      the table's size, its section counts; with an ID, that save's 6 spots in world tiles
"""
import json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import b2decomp, resident, version  # noqa: E402

MAP = 'Route119'
SECTIONS = [(0, 45, 0), (46, 91, 131), (92, 139, 298)]      # {yMin, yMax, first spot - 1}: Gen 3's table
NUM_FISHING_SPOTS = 447
LEVELS = (20, 25)                                           # gWildFeebasRoute119Data / sWildFeebas


def surfable_behaviours():
    """The metatile behaviours that are fishable for Feebas (Gen 3's table in metatile_behavior.c: surfable, not MB_WATERFALL)."""
    src = open(os.path.join(ROOT, 'external', 'pokeruby', 'src', 'metatile_behavior.c')).read()
    table = re.search(r'sTileBitAttributes\[\]\s*=\s*\{(.*?)\};', src, re.S).group(1)
    rows = re.findall(r'TILE_ATTRIBUTES\((\w+), (\w+), (\w+)\),\s*// (\w+)', table)
    assert len(rows) >= 200, len(rows)
    return {i for i, (_, surf, _, name) in enumerate(rows) if surf == 'TRUE' and name != 'MB_WATERFALL'}


def origin():
    """World tile of the map's (0, 0): world.py compose(), without composing the whole world."""
    cfg = version.load_json(os.path.join(ROOT, 'data', 'hoenn_world.json'))
    lay = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps'][MAP]
    M = cfg['margin_cells'] * 32
    pad = cfg.get('pad_north', {}).get(MAP, 0)
    sx, sz = cfg.get('shift', {}).get(MAP, [0, 0])
    return lay['tile_x'] + M + sx, lay['tile_z'] + M + sz + pad


def spots():
    """[(world x, world z, Gen 3's spot number)] of this version's Route 119."""
    import models_interior as mi
    m = mi.sapphire_map(('pokeemerald/' if version.EMERALD else '') + MAP)
    water = surfable_behaviours()
    ox, oz = origin()
    out = []
    for y0, y1, first in SECTIONS:
        n = first
        for y in range(y0, y1 + 1):
            for x in range(m['w']):
                if m['beh'][y][x] in water:
                    n += 1
                    out.append((ox + x, oz + y, n))
        next_first = next((s[2] for s in SECTIONS if s[2] > first), NUM_FISHING_SPOTS)
        assert n == next_first, f'{MAP} y {y0}-{y1}: spots up to {n}, Gen 3 says {next_first}'
    return out


def levels():
    scale = json.load(open(os.path.join(ROOT, 'data', 'level_scaling.json')))['curve']['table']
    return scale[str(LEVELS[0])], scale[str(LEVELS[1])]


def zone():
    return version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps'][MAP]['zone']


def save_spots(trainer_id):
    """The 6 spot numbers of a save, as the C: for the tests."""
    rng, out = (trainer_id ^ (trainer_id >> 16)) & 0xffff, []
    while len(out) < 6:
        rng = (12345 + 0x41C64E6D * rng) & 0xFFFFFFFF
        pick = (rng >> 16) % NUM_FISHING_SPOTS or NUM_FISHING_SPOTS
        if pick >= 4:
            out.append(pick)
    return out


def apply_code(code):
    if not b2decomp.c_on():
        return 'feebas: our C is off (no Feebas spots)'
    import decomp_build
    slot = decomp_build.symbol('gHoennB2Feebas', code)
    if slot is None:
        raise SystemExit('feebas: the decomp has no gHoennB2Feebas (src/hoennb2/resident/feebas.c)')
    table = spots()
    lo, hi = levels()

    def build(base):
        return struct.pack('<4H', zone(), lo, hi, len(table)) + b''.join(struct.pack('<3H', *t) for t in table), {}

    base, end, _ = resident.install(code, build)
    assert resident.read(code, slot, 4) == bytes(4), f'gHoennB2Feebas at {slot:#x}: not NULL'
    resident.write(code, slot, struct.pack('<I', base))
    return f'feebas: {len(table)} spots, {end - base} B at {base:#x}, zone {zone()}, levels {lo}-{hi}'


if __name__ == '__main__':
    t = spots()
    print(version.NAME, len(t), 'spots; origin', origin(), 'levels', levels(), 'zone', zone())
    if len(sys.argv) > 1:
        ids = save_spots(int(sys.argv[1], 0))
        print('spots', ids, [next(x for x in t if x[2] == i)[:2] for i in ids])
