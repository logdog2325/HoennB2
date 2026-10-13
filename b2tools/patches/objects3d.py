"""Sapphire's large objects as Black 2 3D field objects (missing_objects, 2026-10-08; b2tools/models_objects.py).

src/objects3d/<code>-<name>/ holds a model (model.nsbmd: a BMD0 with MDL0 + TEX0, as Black 2's own 3D actors) and
object.json: the object code, the Black 2 record its a/0/4/7 entry copies ("record_from") and the fields it changes.
For each folder this patch appends the model to a/0/4/8 and fills the code's a/0/4/7 record (FieldActorConfig,
GetIndexOfObjID: codes 0x2000-0x200A -> record code - 0x1C1B) with the copy, pointing res1 at the new file. Only
records that are empty in Black 2 are filled (entityType 2, sceneNodeType 0, res1 0: 0x2000-0x2002; 0x2004 is the
Hoenn boulder of patches/boulder_1x1.py; and the empty people records of FREE_PEOPLE_RECORDS, codes < 377 = record
code: entityType 0, res1 0, used by no Black 2 zone NPC, ActorNew or WKOBJCODE work), so no Black 2 object changes. Zone NPCs and ActorNew use the code like any
object code; the spawn flag hides it and movement lists move it in whole tiles (as Strength boulders move).
List it after `sprites` (and `boulder_1x1`).
"""
import glob, json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import narcio, sprites  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src', 'objects3d')
FREE_PEOPLE_RECORDS = {112, 118, 194}    # empty people records (entityType 0, res 0) no Black 2 zone, ActorNew or WKOBJCODE work uses
KEYS = ('uid entityType sceneNodeType shadow footprint reflections billboardSize spriteAtlasSize '
        'spriteControllerType gender collWidth collHeight offX offY offZ res1 res2 anim0 anim1 anim2').split()
FMT = '<HBBBBBBBBBBBbbbHHHHH'

def folders():
    return sorted(d for d in glob.glob(os.path.join(SRC, '*')) if os.path.exists(os.path.join(d, 'object.json')))

def apply(files):
    found = folders()
    if not found:
        return 'no 3D objects (src/objects3d)'
    table = narcio.load(files, sprites.ARC_OW_TABLE)
    t = bytearray(table[0])
    sheets = narcio.load(files, sprites.ARC_OW_SHEETS)
    rec = lambda code: 4 + 28 * sprites.obj_record(code)
    done = []
    for d in found:
        meta = json.load(open(os.path.join(d, 'object.json')))
        code = meta['code']
        bmd = open(os.path.join(d, 'model.nsbmd'), 'rb').read()
        assert bmd[:4] == b'BMD0', f'{d}: model.nsbmd is not a BMD0'
        cur = dict(zip(KEYS, struct.unpack_from(FMT, t, rec(code))))
        if cur['entityType'] == 2 and cur['res1'] >= 975 and sheets[cur['res1']] == bmd:
            done.append(f'{code:#x} {meta["name"]} (already)'); continue
        empty3d = cur['entityType'] == 2 and cur['sceneNodeType'] == 0 and cur['res1'] == 0
        empty_person = code in FREE_PEOPLE_RECORDS and cur['entityType'] == 0 and cur['res1'] == 0
        assert (empty3d or empty_person) and cur['uid'] == code, f'{d}: record of {code:#x} is not an empty record: {cur}'
        base = dict(zip(KEYS, struct.unpack_from(FMT, t, rec(meta['record_from']))))
        assert base['entityType'] == 2, f'{d}: record_from {meta["record_from"]:#x} is not a 3D object'
        sheets.append(bmd)
        new = dict(base, **meta.get('record', {}), uid=code, res1=len(sheets) - 1)
        struct.pack_into(FMT, t, rec(code), *[new[k] for k in KEYS])
        done.append(f'{code:#x} {meta["name"]} (a/0/4/8 file {len(sheets) - 1}, {len(bmd)} B)')
    table[0] = bytes(t)
    narcio.save(files, sprites.ARC_OW_SHEETS, sheets)
    narcio.save(files, sprites.ARC_OW_TABLE, table)
    return '3D objects: ' + ', '.join(done)
