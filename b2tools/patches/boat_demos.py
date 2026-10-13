"""Black 2's boat cutscenes without Unova (boats agent, 2026-10-07; src/field_scripts/common/boat.inc).

The story's trips play Black 2's 3D demos (Call3DDemo, overlay 293, models in a/1/5/8 = ARCID_DEMO3D_RESOURCE 158):
Mr. Briney's boat = demo 4 (Castelia -> Unity Tower motorboat), the ferries = demo 26 (Virbank ferry, open sea only).
Demo 4 starts at a Castelia pier (the user: no Unova landmark may show in any trip), so this patch hides the pier and
its people; the white motorboat then pulls away and speeds off on the open sea, with its wake and the cloud shadows.

What is hidden (models read with work/agents/boats/tools/sbc.py; which demo uses them: the boat textures, c3ship4
blue = demo 4, c3ship5 yellow = demo 10, and the frames):
- a/1/5/8 member 256 `g_ship_port01` (demo 4's scene: Castelia's pier and the sea): every mesh drawn with a pier
  material (c3_* pier floor, roads, railings, quay blocks, lines, h_kage shadows, lambert2 = the bench texture,
  lambert17, sea_gake02 = the quay wall); kept: sea_mizu1_lm1/_lm2 (the water) and cloudtex02 (cloud shadows)
- member 261 `g_ship_port03` (the two people on the pier: girl4, info): both meshes
- member 265 `g_ship_ramp` (Castelia's street lamps c__c3_gaito, flags c3_hata, the gangway, their shadows): all 5
How: in the model's render command list (SBC) each hidden mesh's draw command `05 mesh` becomes two NOPs `00 00`.
Every member keeps its size, so a/1/5/8 and the ROM's file layout do not change (savestates unaffected). The bytes
are checked against Black 2's before they are changed (a different file stops the build).
"""
import os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from b2files import arc_path  # noqa: E402

ARC_DEMO3D = 158
KEEP_256 = {'sea_mizu1_lm1', 'sea_mizu1_lm2', 'cloudtex02'}     # demo 4's water and cloud shadows
HIDE = {256: lambda mat: mat not in KEEP_256,                    # Castelia's pier
        261: lambda mat: True,                                   # the people on it
        265: lambda mat: True}                                   # its street lamps, flags and gangway
EXPECT = {256: ('g_ship_port01', 15), 261: ('g_ship_port03', 2), 265: ('g_ship_ramp', 5)}   # (model, meshes hidden)

def _dict(d, off):
    """Nitro dictionary at off: (names, data entries). u8 0, u8 count, u16 size; the unknown block's size (u16 at
    +6) is counted from the dictionary's start; then u16 entry size, u16 block size, entries; then 16-byte names."""
    cnt = d[off + 1]
    doff = off + struct.unpack_from('<H', d, off + 6)[0]
    esz, dsz = struct.unpack_from('<HH', d, doff)
    data = [d[doff + 4 + i * esz: doff + 4 + (i + 1) * esz] for i in range(cnt)]
    names = [d[doff + dsz + 16 * i: doff + dsz + 16 * i + 16].rstrip(b'\0').decode('latin1') for i in range(cnt)]
    return names, data

_LEN = {0x00: 1, 0x01: 1, 0x02: 3, 0x03: 2, 0x04: 2, 0x24: 2, 0x44: 2, 0x05: 2, 0x06: 4, 0x26: 5, 0x46: 5,
        0x66: 6, 0x07: 2, 0x47: 2, 0x08: 2, 0x48: 2, 0x0b: 1, 0x2b: 1, 0x0c: 3, 0x0d: 3}

def hide_meshes(bmd, hide):
    """NOP the draw commands of the meshes whose bound material hide(name) selects; returns (data, model name, n)."""
    d = bytearray(bmd)
    assert d[:4] == b'BMD0'
    mdl = struct.unpack_from('<I', d, 0x10)[0]
    assert d[mdl:mdl + 4] == b'MDL0'
    mnames, mdata = _dict(d, mdl + 8)
    m = mdl + struct.unpack_from('<I', mdata[0], 0)[0]
    _size, sbc, mat, _mesh, _inv = struct.unpack_from('<IIIII', d, m)
    mats = _dict(d, m + mat + 4)[0]                   # material block: u16 tex dict, u16 pal dict offsets, then dict
    p, end, cur, n = m + sbc, m + mat, None, 0
    while p < end:
        op = d[p]
        ln = 3 + 3 * d[p + 2] if op == 0x09 else _LEN[op]
        if op in (0x04, 0x24, 0x44): cur = mats[d[p + 1]]
        elif op == 0x05 and hide(cur):
            d[p] = d[p + 1] = 0; n += 1
        if op == 0x01: break
        p += ln
    return bytes(d), mnames[0], n

def apply(files_dir):
    path = arc_path(files_dir, ARC_DEMO3D)
    a = bytearray(open(path, 'rb').read())
    assert a[:4] == b'NARC'
    off = struct.unpack_from('<H', a, 0xC)[0]
    assert a[off:off + 4] == b'BTAF'
    fat = off + 12
    gmif = off + struct.unpack_from('<I', a, off + 4)[0]
    gmif += struct.unpack_from('<I', a, gmif + 4)[0]          # skip BTNF
    assert a[gmif:gmif + 4] == b'GMIF'
    out = []
    for member, hide in HIDE.items():
        s, e = struct.unpack_from('<II', a, fat + 8 * member)
        new, name, n = hide_meshes(a[gmif + 8 + s: gmif + 8 + e], hide)
        if (name, n) != EXPECT[member]:
            raise SystemExit(f'boat_demos: a/1/5/8 member {member} is {name} with {n} meshes to hide, expected '
                             f'{EXPECT[member]}: not Black 2\'s file')
        a[gmif + 8 + s: gmif + 8 + e] = new
        out.append(f'{member} {name}: {n} meshes hidden')
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(a); os.replace(path + '.tmp', path)
    return 'demo 4 without Castelia\'s pier: ' + ', '.join(out)
