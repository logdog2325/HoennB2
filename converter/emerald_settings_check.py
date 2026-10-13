"""Do HoennB2's per-map settings still fit Emerald's maps? (emerald_world 2026-10-12; notes/EMERALD.md "Emerald's world")

    python3 emerald_settings_check.py          report (exit 1 when a setting's tiles changed)

HoennB2 keeps Sapphire's map names, so every per-map setting (data/towns/<Map>.json, data/hoenn_world.json,
data/hoenn_standalone.json, the terrain modules' map tables) applies to Emerald's map of that name (version.decomp_map:
Emerald's renames, e.g. BattleTower_Outside -> BattleFrontier_OutsideWest, SafariZone_Northeast -> SafariZone_North):
nothing is copied. A setting that names map tiles holds only where Emerald's map has the same thing there. For every
outdoor map Emerald changed (data/versions.json maps.emerald.ground, plus the renamed ones), each such setting's tiles
are compared, plan class against plan class (data/plans/<Map>.json vs data/plans/emerald/<Map>.json):
  props        data/towns/<Map>.json props: the model origin's tile, its 'on' tile, 'solid' tiles, 'covers' rectangles
  buildings    a building setting (by door destination) whose door Emerald no longer has, or moved
  alt_layouts  data/hoenn_world.json: 'retile' boxes/tiles and 'heights_box' of Route 103/130/131
  modules      terrain/ship.py SHIPS boxes, heights.py RAISED boxes, STILTS / PALM / DESERT / PIER map lists
A changed tile is reported with both classes; a setting whose tiles are all the same class is 'ok'. Fix a reported one
in Emerald's overlay (data/towns/emerald/<Map>.json, data/emerald/hoenn_world.json), never in Sapphire's file.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.append(os.path.join(ROOT, 'b2tools'))
import version  # noqa: E402

def plan(name, emerald):
    p = os.path.join(ROOT, 'data', 'plans', 'emerald' if emerald else '', f'{name}.json')
    return json.load(open(p)) if os.path.exists(p) else None

def cls(p, x, y):
    if p is None or not (0 <= y < len(p['tiles']) and 0 <= x < len(p['tiles'][0])): return None
    return p['tiles'][y][x], p['walkable'][y][x]

def main():
    vj = version.versions_json()['maps']['emerald']
    changed = set(vj['ground']) | set(vj['alias'])
    rows, bad = [], 0
    def check(name, what, tiles, by=(0, 0)):
        nonlocal bad
        a, b = plan(name, False), plan(name, True)
        if a is None or b is None: return
        dx, dz = by          # (a prop an overlay moved: Sapphire's tile against Emerald's tile it moved to)
        d = [(x + dx, y + dz, cls(a, x, y), cls(b, x + dx, y + dz)) for x, y in tiles if cls(a, x, y) != cls(b, x + dx, y + dz)]
        if d:
            bad += 1
            rows.append(f'CHANGED {name}: {what}: ' + ', '.join(f'({x},{y}) {s} -> {e}' for x, y, s, e in d[:8])
                        + (f' (+{len(d) - 8})' if len(d) > 8 else ''))
        else:
            rows.append(f'ok      {name}: {what}')
    import glob
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    from world import moved_props
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'towns', '*.json'))):
        name = os.path.basename(f)[:-5]
        if name not in changed: continue
        t = json.load(open(f))
        base_props = {(p_['res'], p_['x'], p_['z']) for p_ in t.get('props', [])}
        ov = os.path.join(ROOT, 'data', 'towns', 'emerald', os.path.basename(f))      # (Emerald's overlay, as world.py)
        if os.path.exists(ov): t = version.merge(t, json.load(open(ov)))
        moves = {(m['res'], m['at'][0] + m['by'][0], m['at'][1] + m['by'][1]): tuple(m['by']) for m in t.get('prop_moves', [])}
        if t.get('prop_moves'): t = dict(t, props=moved_props(t.get('props', []), t['prop_moves']))
        for pr in t.get('props', []):
            dx, dz = moves.get((pr['res'], pr['x'], pr['z']), (0, 0))
            if (pr['res'], pr['x'] - dx, pr['z'] - dz) not in base_props:      # (a prop only Emerald's overlay places)
                rows.append(f"new     {name}: prop res {pr['res']} at ({pr['x']}, {pr['z']}) {pr.get('what', '')}"); continue
            ts = [(int(pr['x']) - dx, int(pr['z']) - dz)]
            if 'on' in pr: ts.append((pr['on'][0] - dx, pr['on'][1] - dz))
            ts += [(x - dx, z - dz) for x, z in pr.get('solid', [])]
            for x0, z0, x1, z1 in pr.get('covers', []):
                ts += [(x - dx, z - dz) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)]
            check(name, f"prop res {pr['res']} at ({pr['x']}, {pr['z']}) {pr.get('what', '')}"
                  + (f' (moved by {dx, dz} in Emerald)' if (dx, dz) != (0, 0) else ''), ts, (dx, dz))
        a, b = plan(name, False), plan(name, True)
        for dest, bcfg in t.get('buildings', {}).items():
            sa = [x for x in (a or {}).get('buildings', []) if x['dest'] == dest]
            se = [x for x in (b or {}).get('buildings', []) if x['dest'] == dest]
            if [(x['footprint'], x['door']) for x in sa] == [(x['footprint'], x['door']) for x in se]:
                rows.append(f'ok      {name}: building {dest} (res {bcfg["res"]})')
            elif se:
                rows.append(f'moved   {name}: building {dest} (res {bcfg["res"]}) stands on Emerald\'s footprint '
                            f'{[(x["footprint"], x["door"]) for x in se]} (Sapphire {[(x["footprint"], x["door"]) for x in sa]})')
            elif sa:
                rows.append(f'gone    {name}: building {dest} (res {bcfg["res"]}): Emerald has no such door (unused setting)')
        covered = set()                  # (tiles a prop's origin or 'covers' holds: a building drawn by a prop, as Sapphire's)
        for pr in t.get('props', []):
            covered.add((int(pr['x']), int(pr['z'])))
            for x0, z0, x1, z1 in pr.get('covers', []): covered |= {(x, z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)}
        for x in (b or {}).get('buildings', []):
            fx0, fy0, fx1, fy1 = x['footprint']
            if x['dest'] not in t.get('buildings', {}) and any((xx, yy) in covered for yy in range(fy0, fy1 + 1) for xx in range(fx0, fx1 + 1)):
                rows.append(f'prop    {name}: Emerald building {x["dest"]} {x["footprint"]}: drawn by a prop (no door model)')
            elif x['dest'] not in t.get('buildings', {}):
                bad += 1
                rows.append(f'MISSING {name}: Emerald building {x["dest"]} {x["footprint"]} door {x["door"]}: no model setting')
    cfg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world.json')))
    for name, al in cfg.get('alt_layouts', {}).items():
        if name.startswith('_') or name not in changed: continue
        for r in al.get('retile', []):
            if 'tiles' in r: ts = [tuple(t) for t in r['tiles']]
            else:
                x0, z0, x1, z1 = r['box']; ts = [(x, z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)]
            check(name, f"alt layout retile {r.get('box') or 'tiles'} (main layouts compared)", ts)
        if 'heights_box' in al:
            x0, z0, x1, z1 = al['heights_box']
            check(name, f"alt layout heights_box {al['heights_box']} (main layouts compared)",
                  [(x, z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)])
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    from terrain import ship, heights, ground, palms
    for name, s in ship.SHIPS.items():
        if name in changed:
            x0, z0, x1, z1 = s['box']
            check(name, f"terrain/ship.py SHIPS box {s['box']} + landing {s['landing']}",
                  [(x, z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)] + [tuple(s['landing'])])
    for name, boxes in heights.RAISED.items():
        if name in changed:
            for x0, z0, x1, z1 in boxes:
                check(name, f'terrain/heights.py RAISED box {(x0, z0, x1, z1)}', [(x, z) for z in range(z0, z1 + 1) for x in range(x0, x1 + 1)])
    for what, names in (('heights.STILTS', heights.STILTS), ('palms.PALM_MAPS', palms.PALM_MAPS),
                        ('ground.DESERT_MAPS', ground.DESERT_MAPS), ('ground.PIER_MAPS', ground.PIER_MAPS),
                        ('ground.PAVED_MAPS', ground.PAVED_MAPS), ('ground.POSTED_DECKS', ground.POSTED_DECKS)):
        for name in sorted(set(names) & changed):
            rows.append(f'map     {name}: in {what} (a whole-map rule: look at it in the built world)')
    print('\n'.join(rows))
    print(f'{bad} settings whose tiles changed in Emerald')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
