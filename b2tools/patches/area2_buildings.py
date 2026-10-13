"""Exterior building pack 0 (the Hoenn overworld's one pack, area 2) and its texture set (a/1/7/4 entry 0).

Built from registries data/buildings/<group>.json (format in data/buildings/slice.json), for the groups listed in
data/buildings/enabled.json, or in HOENN_TOWN_GROUPS (comma list) for an agent's test build:
- models: an existing pack-0 res id is replaced, a new one is appended (36-byte record, no animation; the door is
  drawn by the game from the door res at the model origin + (dx, dz)). Pack limit: 128 models
  (notes/RESEARCH_WORLD.md). Optional "type": the record's info type (default 0, a plain building); type 11 = event
  prop that scripts can hide with BMSetVisible 8, x, z, 0 (the command filters on the converted type, lut[11] = 8;
  see Littleroot's moving truck, b2tools/models_truck_ext.py).
- drop: res ids of Black 2 models to remove from the pack (unused by Hoenn): the whole pack is loaded into the
  field heap, and above roughly 330-344 KB the field goes black (measured by the town agents, notes/TOWNS_TOWNS2.md).
  A missing res falls back to res 21 (rock_01), which is kept.
- textures: [set, texture] pairs from work/tex/<set>.nsbtx (Black 2's building texture sets), merged byte for byte
  into pack 0's set by b2tools/nsbtx.py (palette: work/tex/pal<NN>.txt pair if listed, else <texture>_pl).

apply_code: a bigger field heap for map type 0 (save_check, 2026-10-08; notes/TESTING.md "Saving and the field heap").
The menu's SAVE runs on the field heap (HEAPID_FIELDMAP 0x15) and needs about 83 KB of it free (82,984-83,004 B
measured in DeSmuME: the save window's font, windows, and a 32 KB tail buffer from GFL_BGSysClearCharCore while it
writes). With pack 0 at 370 KB the field heap keeps only 31-41 KB after a map load in Hoenn's outdoor zones, so
GFL_HeapAllocate fails and the game halts in sys_exit with the bottom screen black (v14.1, every outdoor zone).
Black 2 sizes the field heap per map type: ov036 MAP_CONFIGS[type].heapSize - 0xf000 (src/ov036/fieldmap.c:131-132,
1517; read only there). Map type 0 (every Hoenn outdoor zone) gets FIELD_HEAP_EXTRA more, taken from HEAPID_USER's
free space while the field runs (110,696 B in Black 2 and here; Black 2 keeps it for C-Gear communication, which
Hoenn never turns on: no script uses CGearPowerOn / FieldSubscreenChange)."""
import os, sys, json, struct
import narcio
from b2files import gf_container, gf_container_build

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import nsbtx

OV036 = 0x0217F600                   # arm9_ov036.bin load address (extract/b2_us/arm9_overlays/overlays.yaml)
MAP_CONFIGS = 0x021CA01C             # 29 x 0x48 B FieldMapConfig, heapSize at +0x44 (decomp symbols.txt, fieldmap.c:84)
FIELD_HEAP_VANILLA = 0x136800
FIELD_HEAP_EXTRA = 0x14000           # map type 0: 1,210,312 -> 1,292,232 B of field heap; HEAPID_USER keeps 28,776 B free
# Measured in DeSmuME (save_check): with pack 0 at 371,448 B (file) and FIELD_HEAP_EXTRA 0x10000, every pack-0 zone had
# 96,880 B of field heap free (one block) after a map load (36 zones, warped in), and the save took 83,004 B of it.
# Free space moves 1:1 with the pack (it is read whole into one block) and with FIELD_HEAP_EXTRA.
SAVE_NEED, FREE_MEASURED = 83004, (371448, 0x10000, 96880)
SAVE_HEADROOM_MIN = 8 << 10

def save_headroom(pack_bytes):
    """Field heap left over during a save in a pack-0 zone (estimate from the measurement above)."""
    p, x, free = FREE_MEASURED
    return free + (p - pack_bytes) + (FIELD_HEAP_EXTRA - x) - SAVE_NEED

def info_record(res, door, dx, dz, typ=0):
    return struct.pack('<HHHhhhHH', res, typ, door, dx, 0, dz, 0xFFFF, 0) + bytes(4) + struct.pack('<4I', *[0xFFFFFFFF] * 4)

def groups():
    env = os.environ.get('HOENN_TOWN_GROUPS')
    if env: return ['slice'] + [g for g in env.split(',') if g and g != 'slice']
    return json.load(open(os.path.join(ROOT, 'data', 'buildings', 'enabled.json')))['groups']

def pairs_for(setname):
    p = os.path.join(ROOT, 'work', 'tex', 'pal' + setname[3:] + '.txt')
    out = {}
    if os.path.exists(p):
        for line in open(p):
            a = line.replace('"', '').split()
            if len(a) == 2: out[a[0]] = a[1]
    return out

def apply(files):
    regs = [json.load(open(os.path.join(ROOT, 'data', 'buildings', f'{g}.json'))) for g in groups()]
    packs = narcio.load(files, 225)
    magic, secs = gf_container(packs[0]); n = len(secs) // 2
    infos, bmds = secs[:n], secs[n:]
    index = {struct.unpack_from('<H', s, 0)[0]: i for i, s in enumerate(infos)}
    for r in regs:
        for m in r['models']:
            rec = info_record(m['res'], m['door'], m['dx'], m['dz'], m.get('type', 0))
            path = os.path.join(ROOT, m['model'])
            alt = os.environ.get('HOENN_BUILDINGS_DIR')     # an agent's own model builds (as exterior_check.py), where
            if alt and m['model'].startswith('work/buildings/'):   # it built that town; the lead's otherwise
                p2 = os.path.join(alt, m['model'][len('work/buildings/'):])
                if os.path.exists(p2): path = p2
            bmd = open(path, 'rb').read()
            if m['res'] in index: infos[index[m['res']]], bmds[index[m['res']]] = rec, bmd
            else: index[m['res']] = len(infos); infos.append(rec); bmds.append(bmd)
    drop = {res for r in regs for res in r.get('drop', [])}       # Black 2 models Hoenn never places (heap budget)
    keep = [i for i, s in enumerate(infos) if struct.unpack_from('<H', s, 0)[0] not in drop]
    infos, bmds = [infos[i] for i in keep], [bmds[i] for i in keep]
    assert len(infos) <= 128, f'pack 0 has {len(infos)} models, over the limit of 128'
    size = sum(map(len, infos + bmds))
    packs[0] = gf_container_build(magic, infos + bmds)
    room = save_headroom(len(packs[0]))
    print(f'pack 0: {len(infos)} models, {len(packs[0])} B (all of it loads into the field heap); the menu save keeps about '
          f'{room} B of it spare')
    if room < SAVE_HEADROOM_MIN:      # the save would hang in every outdoor zone (notes/TESTING.md "Saving and the field heap")
        raise SystemExit(f'pack 0 is {len(packs[0])} B: the save would keep only {room} B of field heap (min {SAVE_HEADROOM_MIN}); '
                         f'shrink pack 0 or raise FIELD_HEAP_EXTRA (and check HEAPID_USER still has room)')
    narcio.save(files, 225, packs)
    tex = narcio.load(files, 174)
    adds, srcs = [], {}
    for r in regs:
        for setname, name, *pal in r['textures']:
            src = srcs.setdefault(setname, open(os.path.join(ROOT, 'work', 'tex', setname + '.nsbtx'), 'rb').read())
            have = {p for p, _ in nsbtx._parse(src)['pals']}
            pn = pal[0] if pal else pairs_for(setname).get(name, name + '_pl')
            adds.append((src, name, pn if pn in have else None))
    tex[0] = nsbtx.merge(tex[0], adds)
    narcio.save(files, 174, tex)
    return f'groups {groups()}: {len(infos)} models in pack 0, texture set {len(tex[0])} B'

def apply_code(code):
    path = os.path.join(code, 'arm9_ov036.bin')
    data = bytearray(open(path, 'rb').read())
    at = MAP_CONFIGS + 0x44 - OV036                                  # MAP_CONFIGS[0].heapSize
    new = FIELD_HEAP_VANILLA + FIELD_HEAP_EXTRA
    old = struct.unpack_from('<I', data, at)[0]
    assert old in (FIELD_HEAP_VANILLA, new), f'MAP_CONFIGS[0].heapSize: unexpected {old:#x}'
    struct.pack_into('<I', data, at, new)
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(data); os.replace(path + '.tmp', path)
    return f'field heap for map type 0: {FIELD_HEAP_VANILLA:#x} -> {new:#x} (MAP_CONFIGS[0].heapSize; the save needs ~83 KB free)'
