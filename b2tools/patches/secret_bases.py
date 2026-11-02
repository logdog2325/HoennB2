"""Secret Bases and decorations (notes/SECRET_BASES.md): the prop pack and the area records, before `interiors`.

The decomp's code (src/hoennb2/resident/secret_base.c, overlay 348) loads from a/2/2/6 file 17 only the models a room shows.
- a/0/1/3: area 299 (the bases) and area 300 (the two bedrooms) load prop pack 17; neither has a zone in Hoenn otherwise.
- a/2/2/6 file 17: replaced by the 121 decorations' + the fixtures' + the cursor's models. a/1/7/5 file 17: their textures.
- a/0/1/4 files 299, 300: emptied (`interiors` then merges the rooms' textures, like any room).
The room furniture of the bedrooms joins pack 17 in `interiors`, by data/interiors/391.json's area.
The late part (secret_bases_late.py) gives the base zones gimmick 30, after zone_effects has cleaned the gimmick table.
"""
import json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import narcio, nsbtx, b2files                               # noqa: E402
from b2files import gf_container_build                      # noqa: E402
import secret_base_data as SB                               # noqa: E402

PROPS = os.path.join(os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'), '_secret_bases')
# What a static prop's record says (patches/interiors.py STATIC_INFO, the model's animations none)
STATIC_INFO = bytes.fromhex('0000 0000 ffff 0000 0000 0000 ffff 0000 0000 0000 ffff ffff ffff ffff ffff ffff ffff ffff')


def apply(files):
    from PIL import Image
    props = json.load(open(os.path.join(PROPS, 'props.json')))
    # area records (10 bytes each, a plain file)
    path = os.path.join(files, 'a', '0', '1', '3')
    raw = bytearray(open(path, 'rb').read())
    struct.pack_into('<H', raw, SB.AREA_BASE * 10, SB.PACK)
    struct.pack_into('<H', raw, SB.AREA_BEDROOM * 10, SB.PACK)
    open(path, 'wb').write(raw)
    # the pack
    infos, bmds, adds = [], [], []
    for p in props:
        infos.append(struct.pack('<HH', p['res'], 0) + STATIC_INFO[4:])
        bmds.append(open(os.path.join(PROPS, p['name'] + '.nsbmd'), 'rb').read())
        img = Image.open(os.path.join(PROPS, p['name'] + '.png')).convert('RGBA')
        adds.append((SB.rgba_source(p['name'], img), p['name'], p['name'] + '_pl'))
    packs, btex, sets = narcio.load(files, 226), narcio.load(files, 175), narcio.load(files, 14)
    assert len(packs) > SB.PACK
    packs[SB.PACK] = gf_container_build('AB', infos + bmds)
    old = nsbtx._parse(btex[SB.PACK])
    btex[SB.PACK] = nsbtx.merge(btex[SB.PACK], adds, drop={n for n, _ in old['texs']})
    # the rooms' own set(s): their textures come in with `interiors`
    for area in (SB.AREA_BASE, SB.AREA_BEDROOM):
        s = struct.unpack_from('<H', raw, area * 10 + 2)[0]
        parsed = nsbtx._parse(sets[s])
        sets[s] = nsbtx.merge(sets[s], [], drop={n for n, _ in parsed['texs']}, drop_pals={n for n, _ in parsed['pals']})
    narcio.save(files, 226, packs)
    narcio.save(files, 175, btex)
    narcio.save(files, 14, sets)
    size = len(packs[SB.PACK])
    return (f'Secret Bases: pack {SB.PACK} = {len(props)} props, {size:,} B; its textures {len(btex[SB.PACK]):,} B; '
            f'areas {SB.AREA_BASE}, {SB.AREA_BEDROOM} load it')
