"""houses agent helper: size of the interior building pack (a/2/2/6) + its texture set (a/1/7/5) and of the map
texture set (a/0/1/4) of every interior area that data/interiors/*.json rooms use, after the interiors patch adds the
rooms' furniture models and textures (same steps as b2tools/patches/interiors.py, nothing written).

    python3 houses_packsize.py [AREA ...]        (default: every area a room json names)
"""
import os, sys, json, glob, struct
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import b2files, nsbtx
from b2files import gf_container_build
from interiors import _pack_sections

FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
ROOMS = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'agents', 'houses', 'interiors')

def main(areas):
    packs = b2files.narc_entries(b2files.arc_path(FILES, 226))
    btex = b2files.narc_entries(b2files.arc_path(FILES, 175))
    sets = b2files.narc_entries(b2files.arc_path(FILES, 14))
    by_area = {}
    for f in glob.glob(os.path.join(ROOT, 'data', 'interiors', '*.json')):
        c = json.load(open(f))
        if c.get('room') and 'area' in c: by_area.setdefault(c['area'], []).append(c['room'])
    for area in sorted(areas or by_area):
        ar = b2files.area(FILES, area); p = ar['pack']
        infos, bmds = _pack_sections(packs[p])
        have = {struct.unpack_from('<H', i, 0)[0] for i in infos}
        bt = btex[p]; ts = sets[ar['texset']]
        added, map_adds = {}, []
        src_maps, src_btex = {}, {}
        for room in by_area.get(area, []):
            meta_p = os.path.join(ROOMS, room, 'room.json')
            if not os.path.exists(meta_p): continue
            meta = json.load(open(meta_p))
            for tex, s in meta['map_textures'].items():
                if s not in src_maps: src_maps[s] = b2files.map_textures(FILES, s)
                map_adds.append((src_maps[s], tex, tex + '_pl'))
            for m in meta.get('models', []):
                if m['res'] in have or m['res'] in added or 'file' in m: continue
                pi, pb = _pack_sections(packs[m['pack']])
                k = [struct.unpack_from('<H', i, 0)[0] for i in pi].index(m['res'])
                added[m['res']] = (m['name'], pi[k], pb[k], m['pack'])
        for res, (name, info, bmd, sp) in added.items():
            infos.append(info); bmds.append(bmd)
            if sp not in src_btex: src_btex[sp] = b2files.building_textures(FILES, sp, exterior=False)
            bt = nsbtx.merge(bt, [(src_btex[sp], t, pl) for t, pl in sorted(nsbtx.material_pairs(bmd), key=str) if t])
        new_pack = gf_container_build('AB', infos + bmds)
        new_ts = nsbtx.merge(ts, map_adds) if map_adds else ts
        print(f'area {area} ({len(by_area.get(area, []))} rooms): pack {p} {len(packs[p])} -> {len(new_pack)} B '
              f'(+{sorted(n for n, *_ in added.values())}), pack textures {len(btex[p])} -> {len(bt)} B, '
              f'map texture set {ar["texset"]} {len(sets[ar["texset"]])} -> {len(new_ts)} B')

if __name__ == '__main__':
    main([int(a) for a in sys.argv[1:]])
