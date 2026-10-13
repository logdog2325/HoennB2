"""The caves_misc agent's Sky Pillar generator: writes the five Sky Pillar floor recipes (data/interior_layouts/
SkyPillar_<n>F.json, built by b2tools/models_interior.py) from Sapphire's metatiles, and the agent's room style
(data/interior_layouts/_styles_caves_misc.json "cm_skypillar").

    python3 caves_misc_skypillar.py      (then HOENN_AGENT=caves_misc zsh b2tools/agent_build_caves.sh SkyPillar_1F ...:
                                          converter/gen_caves.py writes the zone files, cracked-floor falls included)

Sapphire's Sky Pillar floors (14x14, gTileset_Pacifidlog; metatile ids checked on all five maps):
  back wall    rows 0-1: 0x227/0x22f wall, 0x23b-0x23d / 0x243 / 0x245 doorway frames, 0x244 / 0x24c doorways (warps,
               behaviour 0x60: stairs up drawn in them = 0x244 when the warp leads up). Black 2: the room builder's back
               wall (Dragonspiral Tower's set 295: in14_yuka_a tan stone, the closest to Sapphire's brown wall), the
               doorways painted on it: a dark opening (in14_kage_a), grey jambs (in14_colum_a) and a lintel (in14_wall_c),
               steps (in14_slope_a) in the openings that lead up; the warp is the builder's stair spot (solid, walked into
               northwards).
  floor        everything else; walkable to the map's edges (Sapphire draws no side walls): no side walls ("open").
               Black 2: Dragonspiral's grey stone slab in14_yuka_c.
  the shaft    the dark rectangle in the middle (blocked metatiles 0x238-0x24d that are not the wall): a hole in the
               floor (black below, as Sapphire's dark blue).
  rubble       0x20f / 0x207 (one crystal; 0x207 on the floor row along the wall) and 0x21f / 0x217 (a cluster): Black
               2's blue stones d6stone04 / d6stone02 (Chargestone Cave's,
               interior pack 11; copied into Dragonspiral's pack 13 by the interiors patch).
  cracked      MB_CRACKED_FLOOR (0xD2, 2F and 4F): Dragonspiral's broken-floor patch in14_yuka_g laid on the tile; the
               fall (Sapphire's CaveHole scripts: to the floor below, same x,y) is a step trigger from gen_caves.py.
  exit         1F's south-arrow warps (6,13)/(7,13): the builder's exit mat (type 1) with Dragonspiral's lit doorway
               in14_exit_a as the notch below it.
Wild encounters on the floors Sapphire has them (behaviour 0x08: 1F, 3F, 5F): recipe "encounters".
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'converter'))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
FLOORS = ['SkyPillar_1F', 'SkyPillar_2F', 'SkyPillar_3F', 'SkyPillar_4F', 'SkyPillar_5F']
ORIGIN = [1, 0]          # zone tile of Sapphire (0, 0) (models_interior's default for a first floor row 2; written out
                         # so converter/gen_caves.py's falls land on the right tile)
SET = 295                # Dragonspiral Tower's texture set (area 295, interior pack 13)
ROCKS = {0x20f: 'd6stone04', 0x207: 'd6stone04', 0x21f: 'd6stone02', 0x217: 'd6stone02'}
DOOR_BEH, CRACKED_BEH, EXIT_BEH = 0x60, 0xD2, 0x65

STYLE = {"cm_skypillar": {
    "_doc": "caves_misc: Sky Pillar inside = Black 2's Dragonspiral Tower (texture set 295, area 295): grey stone slab floor in14_yuka_c, tan stone wall in14_yuka_a (Sapphire's wall is brown; Dragonspiral's own walls are teal brick), Dragonspiral's lit doorway in14_exit_a as the exit notch.",
    "floor": {"tex": "in14_yuka_c", "src": SET, "size": 32},
    "wall": {"tex": "in14_yuka_a", "src": SET, "u_size": 32},
    "genkan": {"tex": "in14_exit_a", "src": SET, "size": 16},
    "black": {"tex": "black", "src": 285}}}

def floor_no(name):
    return 6 if name.endswith('Top') else int(name.split('_')[1][0])

def recipe(name):
    from gba import Repo, MetatileRenderer
    repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    mj = repo.map_json(name)
    g, l = repo.layout_grid(mj['layout'])
    mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
    H, W = g.shape
    mt = lambda x, z: int(g[z, x]) & 0x3FF
    walk = lambda x, z: (int(g[z, x]) >> 10) & 3 == 0
    beh = lambda x, z: mr.behavior(mt(x, z))
    shaft, rocks, cracked = [], [], []
    for z in range(2, H):
        for x in range(W):
            m = mt(x, z)
            if m in ROCKS: rocks.append(dict(m=ROCKS[m], tile=[x, z], _what=f'Sapphire rubble 0x{m:x} ({x},{z})'))
            elif not walk(x, z): shaft.append((x, z))
            if beh(x, z) == CRACKED_BEH: cracked.append([x, z])
    xs = [t[0] for t in shaft]; zs = [t[1] for t in shaft]
    sx0, sz0, sx1, sz1 = min(xs), min(zs), max(xs), max(zs)
    assert len(shaft) == (sx1 - sx0 + 1) * (sz1 - sz0 + 1), f'{name}: the shaft is not a rectangle'
    r = dict(map=name, style='cm_skypillar', origin=ORIGIN, encounters=True,
             floor=[[0, 2, W - 1, H - 1]],
             holes=[[sx0, sz0, sx1 + 1, sz1 + 1]],
             open=[[-1, 0, -1, H], [W, 0, W, H]])
    r['furniture'] = rocks
    decals = []
    me = floor_no(name)
    for w in mj['warp_events']:
        x, z = w['x'], w['y']
        if beh(x, z) != DOOR_BEH: continue
        dest = w['dest_map'][4:].title().replace('_', '')     # MAP_SKY_PILLAR_2F -> SkyPillar2F
        up = floor_no('SkyPillar_' + dest[len('SkyPillar'):]) > me if dest != 'SkyPillarTop' else True
        a = [x + 0.5]
        decals += [dict(tex='in14_kage_a', src=SET, at=a, z=z + 1, y=-2, w=14, h=28, gap=2, _what=f'doorway ({x},{z}) to {w["dest_map"]}'),
                   dict(tex='in14_colum_a', src=SET, at=[x + 0.5 - 0.5625], z=z + 1, y=-2, w=4, h=32, gap=4, _what='jamb'),
                   dict(tex='in14_colum_a', src=SET, at=[x + 0.5 + 0.5625], z=z + 1, y=-2, w=4, h=32, gap=4, _what='jamb'),
                   dict(tex='in14_wall_c', src=SET, at=a, z=z + 1, y=26, w=20, h=6, gap=6, _what='lintel')]
        if up: decals.append(dict(tex='in14_slope_a', src=SET, at=a, z=z + 1, y=-2, w=14, h=10, gap=4, _what='steps up'))
    r['decals'] = decals
    if cracked:
        r['mats'] = [dict(tex='in14_yuka_g', src=SET, rect=[x, z, x, z], border=0, border_units=0, y=0, _what='cracked floor') for x, z in cracked]
    exits = [(w['x'], w['y']) for w in mj['warp_events'] if beh(w['x'], w['y']) == EXIT_BEH]
    # Sapphire's 1F exit is the doorway out of the tower: no rug, the notch below shows Dragonspiral's lit doorway
    r['cave_zone'] = dict(area=SET, header_zone=208)     # converter/gen_caves.py: Dragonspiral Tower 2F's header
    return r, dict(shaft=(sx0, sz0, sx1, sz1), rocks=len(rocks), cracked=len(cracked), doors=len(decals), exits=exits)

def main():
    sp = os.path.join(LAYOUTS, '_styles_caves_misc.json')
    styles = json.load(open(sp)) if os.path.exists(sp) else {}
    styles.update(STYLE)
    json.dump(styles, open(sp, 'w'), indent=1, ensure_ascii=False)
    for name in FLOORS:
        r, info = recipe(name)
        out = dict(_doc=f'Sky Pillar {name[-2:]} (Sapphire {name}): Black 2\'s Dragonspiral Tower look. Generated by '
                        'b2tools/caves_misc_skypillar.py from Sapphire\'s metatiles (see its docstring); edit that script.', **r)
        json.dump(out, open(os.path.join(LAYOUTS, name + '.json'), 'w'), indent=1, ensure_ascii=False)
        print(name, info)

if __name__ == '__main__':
    main()
