"""Hoenn's map texture set: Black 2's area 2 summer set (a/0/1/4 entry 3, the one our terrain was built from; the
season is always summer, patches/hoenn_season.py) plus every texture the terrain modules (b2tools/terrain/*.py)
take from other Black 2 sets, merged byte for byte by b2tools/nsbtx.py (no re-encoding). Prints the size against
the ~200 KB budget for map + building textures (notes/RESEARCH_WORLD.md)."""
import os, sys
import narcio
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import nsbtx, terrain

HOENN_SET = 3

def apply(files):
    sets = narcio.load(files, 14)
    adds = []
    bsets = []
    for f in terrain.modules():
        for name, ts in getattr(f, 'TEXTURES', {}).items():
            if not isinstance(ts, int):          # 'ext<N>': exterior building texture set a/1/7/4 N (terrain/ship.py)
                bsets = bsets or narcio.load(files, 174)
            src = sets[ts] if isinstance(ts, int) else bsets[int(ts[3:])]
            pal = getattr(f, 'PALETTES', {}).get(name, name + '_pl')
            adds.append((src, name, pal if pal in {n for n, _ in nsbtx._parse(src)['pals']} else None))
    # Sapphire's ash drawn with Black 2's snowy winter art: renamed copies (data/hoenn_ash.json, world.py ash_tiles)
    ap = os.path.join(HERE, '..', '..', 'data', 'hoenn_ash.json')
    if os.path.exists(ap):
        import json
        for new, (ts, name) in json.load(open(ap)).get('textures', {}).items():
            src = sets[ts]
            pal = name + '_pl' if name + '_pl' in {n for n, _ in nsbtx._parse(src)['pals']} else None
            adds.append((src, name, pal, new, new + '_pl' if pal else None))
    if not adds: return 'no terrain module textures'
    before = len(sets[HOENN_SET])
    sets[HOENN_SET] = nsbtx.merge(sets[HOENN_SET], adds)
    narcio.save(files, 14, sets)
    pack = len(narcio.load(files, 174)[0])
    return (f'{len(adds)} textures added to set {HOENN_SET}: {before} -> {len(sets[HOENN_SET])} B; with building '
            f'textures {len(sets[HOENN_SET]) + pack} B of ~200 KB')
