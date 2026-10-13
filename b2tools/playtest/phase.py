"""phase.py STATE LABEL ZONE [ZONE ...]: for each outdoor zone in order, walk into it, tour it and every room behind
its doors (explore.py). Zones given as numbers or map names. Saves <LABEL>_after_<zone>.dst after each."""
import sys; sys.path.insert(0, sys.path[0])
from pt import *
import explore as EX, places as PL, flags as F
F.repel_all = True
state, label = sys.argv[1], sys.argv[2]
zones = [int(a) if a.isdigit() else PL.ZONE[a] for a in sys.argv[3:]]
g = G(state, name=label)
g.can_surf = os.environ.get('PT_SURF') == '1'
g.can_clear = os.environ.get('PT_CLEAR') == '1'
E = EX.Explorer(g, label)

def anchor(z):
    ws = [w for w in rom().entities(z)['warps'] if own_warp_z(z, w)]
    grid = rom().grid(z)
    cands = []
    for w in ws:
        cands.append((w['tile_x'], w['tile_z'] + 1))
    for n in rom().entities(z)['npcs']:
        cands += [(n['x'], n['z'] + 1), (n['x'] + 1, n['z'])]
    good = [c for c in cands if grid.zone_at(*c) in (z, None) and any(R.land(r) for r in grid.rec(*c))]
    try:
        import planner
        reg = planner.regions(rom().hdr[z]['matrix'], g.can_surf)
        here = reg.get(g.tile()) if rom().hdr[g.zone()]['matrix'] == rom().hdr[z]['matrix'] else None
        reach = [c for c in good if reg.get(c) is not None and (here is None or reg.get(c) == here)]
        if reach: return reach[0]
    except Exception as ex:
        print('anchor bfs failed', ex)
    return good[0] if good else (cands[0] if cands else None)

def own_warp_z(z, w):
    ws = rom().entities(z)['warps']
    return not [v for v in ws if (v['tile_x'], v['tile_z']) == (w['tile_x'], w['tile_z']) and v['dest_zone'] != w['dest_zone']]

for z in zones:
    if g.zone() != z:
        a = anchor(z)
        g.note(f'=== travel to zone {z} {PL.NAME.get(z, "")} via {a}')
        import planner
        r = planner.travel(g, z, a) if a else False
        if g.zone() != z:
            g.note(f'=== could not reach zone {z} (now {g.zone()} {g.tile()}): {r}')
            continue
    g.note(f'=== exploring zone {z} {PL.NAME.get(z, "")}')
    E.explore()
    g.save(f'{label}_after_{z}.dst')
