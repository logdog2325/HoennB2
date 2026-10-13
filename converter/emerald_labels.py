"""Emerald's metatile labels carried over from Sapphire's (emerald_world 2026-10-12; notes/EMERALD.md "Emerald's world").

    python3 emerald_labels.py [--todo OUT.json]   -> data/labels/emerald/carry_<tileset>.json (+ the metatiles that still
                                                     need a label by eye, with where they are used, in OUT.json)
    python3 emerald_labels.py --check             exit 1 when a carry file is not current (nothing written)

Emerald's world reads pokeemerald's tilesets (converter/gba.py world_repo), whose metatiles keep Ruby/Sapphire's ids but
whose art was retouched widely (notes/EMERALD_PLAN.md 1.1). converter/plan_map.py gives an Emerald metatile only an
Emerald label (data/labels/emerald/): this script's carry files, under the hand-made <tileset>.json files (which win).
A metatile of a tileset that one of Emerald's outdoor maps uses (data/hoenn_zones.json's maps by version.decomp_map, the
Emerald-only outdoor maps of data/emerald/hoenn_standalone.json) takes Sapphire's label (converter/metatiles.json, then
data/labels/gTileset_*.json, as plan_map.py reads them; tileset renames InsideShip/BattleFrontier as Ship/BattleTower)
when it behaves as Sapphire's same id (metatile_attributes.bin behaviour byte) and either
  same    renders exactly as Sapphire's (the 16x16 pixels), or
  placed  stands where Sapphire has the same id in the same map (any built map, same tile): the same thing, retouched.
Every other metatile those maps use (redrawn and moved, other behaviour, ids Sapphire's tileset does not have, tilesets
Sapphire lacks) needs a label by eye (data/labels/emerald/<tileset>.json; sheets: work/agents/emerald_world/tools/
label_sheets.py): the run counts the ones still without one.
"""
import glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
from gba import Repo, MetatileRenderer, event_maps  # noqa: E402
import version  # noqa: E402

OUT = os.path.join(ROOT, 'data', 'labels', 'emerald')
RENAME_TS = {'gTileset_InsideShip': 'gTileset_Ship', 'gTileset_BattleFrontier': 'gTileset_BattleTower'}
PRIMARY_FALLBACK = 'gTileset_Petalburg'      # (a primary id renders with any secondary: its palettes are the primary's)


def sapphire_table():
    """plan_map.py's table: metatiles.json first, then data/labels/gTileset_*.json (setdefault)."""
    table = json.load(open(os.path.join(HERE, 'metatiles.json')))
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'labels', 'gTileset_*.json'))):
        for ts, ids in json.load(open(f)).items():
            if ts.startswith('_'): continue
            for k, v in ids.items(): table.setdefault(ts, {}).setdefault(k, v)
    return table


def outdoor_maps():
    """HoennB2 names of Emerald's outdoor maps (event maps excluded: they keep data/labels/emerald_islands.json)."""
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    names = [n for n in zones if n not in event_maps() and version.decomp_map(n, 'emerald')]
    p = os.path.join(ROOT, 'data', 'emerald', 'hoenn_standalone.json')
    if os.path.exists(p):
        for g in json.load(open(p)).get('groups', {}).values():
            names += [n for n in g.get('maps', {}) if n not in names]
    return names


def main(check=False, todo_out=None):
    R = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    E = Repo(os.path.join(ROOT, 'external', 'pokeruby'), emerald=True)
    table = sapphire_table()
    rend = {}

    def mr(repo, a, b):
        k = (repo.root, a, b)
        if k not in rend:
            try: rend[k] = MetatileRenderer(repo, a, b)
            except FileNotFoundError: rend[k] = None
        return rend[k]

    used = {}                     # (tileset, id) -> [(map, x, y)] (first few)
    pairs = {}                    # tileset -> a (prim, sec) pair it is used in (for rendering)
    placed = {}                   # (tileset, id) -> (map, x, y) where Sapphire has the same id
    for name in outdoor_maps():
        ej = E.map_json(name)
        ge, le = E.layout_grid(ej['layout'])
        prim, sec = le['primary_tileset'], le['secondary_tileset']
        pairs.setdefault(prim, (prim, sec)); pairs.setdefault(sec, (prim, sec))
        gs = None
        if os.path.exists(os.path.join(R.root, 'data', 'maps', name, 'map.json')):
            sj = R.map_json(name); gs, ls = R.layout_grid(sj['layout'])
            if (RENAME_TS.get(prim, prim), RENAME_TS.get(sec, sec)) != (ls['primary_tileset'], ls['secondary_tileset']): gs = None
        for y in range(ge.shape[0]):
            for x in range(ge.shape[1]):
                m = int(ge[y, x]) & 0x3FF
                key = (prim if m < 512 else sec, m)
                u = used.setdefault(key, [])
                if len(u) < 3: u.append((name, x, y))
                if gs is not None and y < gs.shape[0] and x < gs.shape[1] and int(gs[y, x]) & 0x3FF == m:
                    placed.setdefault(key, (name, x, y))
    carry, how, todo = {}, {}, {}
    for ts, (prim, sec) in sorted(pairs.items()):
        rts = RENAME_TS.get(ts, ts)
        is_prim = ts == prim
        b = mr(E, prim, sec)
        rp, rs = RENAME_TS.get(prim, prim), RENAME_TS.get(sec, sec)
        a = mr(R, rp, rs) or (mr(R, rp, PRIMARY_FALLBACK) if is_prim else None)
        n_e = len(b.p['mt'] if is_prim else b.s['mt'])
        n_r = (len(a.p['mt'] if is_prim else a.s['mt'])) if a else 0
        for i in range(n_e):
            m = i if is_prim else i + 512
            key = (ts, m); hx = f'{m:03x}'
            lab = table.get(rts, {}).get(hx)
            kind = None
            if a is not None and i < n_r and lab is not None and a.behavior(m) == b.behavior(m):
                if np.array_equal(a.render(m)[..., :3], b.render(m)[..., :3]): kind = 'same'
                elif key in placed: kind = 'placed ' + '{} ({},{})'.format(*placed[key])
            if kind:
                carry.setdefault(ts, {})[hx] = lab; how.setdefault(ts, {})[hx] = kind
            elif key in used:
                why = ('new id' if a is None or i >= n_r else 'other behaviour' if a.behavior(m) != b.behavior(m) else
                       'no Sapphire label' if lab is None else 'redrawn, not where Sapphire has it')
                todo[f'{ts}:{hx}'] = dict(why=why, sapphire_label=lab, at=used[key], pair=[prim, sec],
                                          beh=b.behavior(m), sapphire_beh=a.behavior(m) if a is not None and i < n_r else None)
    stale = []
    os.makedirs(OUT, exist_ok=True)
    for ts in sorted(carry):
        doc = (f"Sapphire's labels carried over to Emerald's {ts} (converter/emerald_labels.py, generated: do not edit; "
               f"labels by eye go in {ts}.json, which wins). _how: 'same' = drawn and behaving as Sapphire's same id, "
               f"'placed <map> (x,y)' = behaving the same and standing where Sapphire has that id in that map.")
        out = {'_doc': doc, ts: dict(sorted(carry[ts].items())), '_how': dict(sorted(how[ts].items()))}
        p = os.path.join(OUT, f'carry_{ts}.json')
        text = json.dumps(out, indent=1, ensure_ascii=False) + '\n'
        if check:
            if not os.path.exists(p) or open(p).read() != text: stale.append(p)
        else:
            open(p, 'w').write(text)
    if check:
        print('stale:' if stale else 'carry files current', *stale)
        return 1 if stale else 0
    if todo_out:
        os.makedirs(os.path.dirname(os.path.abspath(todo_out)), exist_ok=True)
        json.dump(todo, open(todo_out, 'w'), indent=1)
    hand = {}                         # labels by eye (data/labels/emerald/<tileset>.json)
    for f in glob.glob(os.path.join(OUT, 'gTileset_*.json')):
        for ts, ids in json.load(open(f)).items():
            if not ts.startswith('_'): hand.setdefault(ts, set()).update(ids)
    left = [k for k in todo if k.split(':')[1] not in hand.get(k.split(':')[0], ())]
    from collections import Counter
    print(f"carried: {sum(len(v) for v in carry.values())} labels in {len(carry)} tilesets "
          f"({sum(1 for t in how.values() for k in t.values() if k == 'same')} same, "
          f"{sum(1 for t in how.values() for k in t.values() if k != 'same')} placed)")
    print(f'need a label by eye: {len(todo)} ({dict(Counter(v["why"] for v in todo.values()))}); still without one: '
          f'{len(left)} {dict(Counter(k.split(":")[0] for k in left).most_common())}')
    return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    sys.exit(main('--check' in a, a[a.index('--todo') + 1] if '--todo' in a else None))
