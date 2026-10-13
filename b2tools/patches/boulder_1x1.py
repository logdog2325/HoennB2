"""Hoenn's Strength boulder: one tile, like Sapphire's (caves_east, 2026-10-06; notes/CAVES.md "Strength boulders").

Black 2's boulders (object codes 0x2003 bigrock, 0x2005 bigrock2) cover 2x2 tiles: their a/0/4/7 records
(FieldActorConfig) say collWidth/collHeight 2, offX +8 / offZ -8 (the model sits on the corner of the 2x2 square).
The Strength push reads that size: StrengthRockSpaceCheck (ov036 0x021ba880) tests collWidth x collHeight tiles ahead
of the boulder (0x2167388 / 0x2167390 = the record's width / height), and every actor's collision
(CheckBlockedCollPathToPosition, src/ov012/field_actor_tool.c) does the same. Sapphire's boulder is one tile, so
Black 2's blocks a second row/column of a corridor and the puzzles don't work.

Object code 0x2004 is a Strength rock code in Black 2's code (IsNPCStrengthRock, ov012 0x02168284: 0x6d and
0x2003..0x2005; the only code that tests these numbers: a literal scan of every code binary finds no other use) whose
a/0/4/7 record (1001 = 0x2004 - 0x1C1B, GetIndexOfObjID) is empty: entityType 2, sceneNodeType 0, res 0, used by no
zone. This patch fills that record: a copy of 0x2005's (3D model, billboardSize 2) with collision 1x1, no offset,
and res = a new a/0/4/8 file: bigrock2 (a/0/4/8 file 1) with its MDL0 position scale halved (models_interior.py
scaled_bmd: Black 2's own model byte for byte, drawn at half size = one tile). 0x2003/0x2005 are unchanged.

Hoenn's boulders use code 0x2004 (8196): converter/gen_caves.py MODEL_BOULDER, data/sprite_map.json
OBJ_EVENT_GFX_PUSHABLE_BOULDER. List this patch after `sprites`.
"""
import os, sys, struct

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import narcio, sprites  # noqa: E402

CODE, BASE = 0x2004, 0x2005
SCALE = 0.5            # bigrock2 is 2 tiles wide; Sapphire's boulder is one

def scaled_bmd(bmd, s):
    """models_interior.scaled_bmd (kept here so the patch doesn't import the room builder)."""
    import nsbtx
    out = bytearray(bmd)
    nb = struct.unpack_from('<H', bmd, 0xE)[0]
    mdl = next(bo for bo in (struct.unpack_from('<I', bmd, 0x10 + 4 * k)[0] for k in range(nb)) if bmd[bo:bo + 4] == b'MDL0')
    for _, ent in nsbtx._dict(bmd, mdl + 8):
        info = mdl + struct.unpack_from('<I', ent, 0)[0] + 0x14
        for off, f in ((8, s), (12, 1 / s), (36, s), (40, 1 / s)):
            struct.pack_into('<i', out, info + off, round(struct.unpack_from('<i', bmd, info + off)[0] * f))
    return bytes(out)

def apply(files):
    table = narcio.load(files, sprites.ARC_OW_TABLE)
    t = bytearray(table[0])
    rec = lambda code: 4 + 28 * sprites.obj_record(code)
    keys = ('uid entityType sceneNodeType shadow footprint reflections billboardSize spriteAtlasSize '
            'spriteControllerType gender collWidth collHeight offX offY offZ res1 res2 anim0 anim1 anim2').split()
    fmt = '<HBBBBBBBBBBBbbbHHHHH'
    cur = dict(zip(keys, struct.unpack_from(fmt, t, rec(CODE))))
    base = dict(zip(keys, struct.unpack_from(fmt, t, rec(BASE))))
    sheets = narcio.load(files, sprites.ARC_OW_SHEETS)
    if cur['sceneNodeType'] == base['sceneNodeType'] and cur['collWidth'] == 1 and cur['res1'] >= len(sheets) - 1 \
            and sheets[cur['res1']][:4] == b'BMD0':
        return f'object {CODE:#x} is already the 1x1 boulder (a/0/4/8 file {cur["res1"]})'
    assert cur['sceneNodeType'] == 0 and cur['res1'] == 0 and cur['uid'] == CODE, f'record of {CODE:#x} is not empty: {cur}'
    bmd = sheets[base['res1']]
    assert bmd[:4] == b'BMD0', f'a/0/4/8 file {base["res1"]} is not a model'
    sheets.append(scaled_bmd(bmd, SCALE))
    new = dict(base, uid=CODE, collWidth=1, collHeight=1, offX=0, offY=0, offZ=0, res1=len(sheets) - 1)
    struct.pack_into(fmt, t, rec(CODE), *[new[k] for k in keys])
    table[0] = bytes(t)
    narcio.save(files, sprites.ARC_OW_SHEETS, sheets)
    narcio.save(files, sprites.ARC_OW_TABLE, table)
    return f'object {CODE:#x}: 1x1 Strength boulder (bigrock2 at {SCALE}, a/0/4/8 file {len(sheets) - 1})'
