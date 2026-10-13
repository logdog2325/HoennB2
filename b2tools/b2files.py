"""Read Black 2's map-related files (formats from notes/GEN5_MAPS.md). Read-only.

Archive id N lives at files/a/<N/100>/<N/10%10>/<N%10>.
"""
import os, struct

def arc_path(files_dir, arc):
    return os.path.join(files_dir, 'a', str(arc // 100), str(arc // 10 % 10), str(arc % 10))

def narc_entries(path):
    """Return the list of entries (bytes) in a NARC file."""
    d = open(path, 'rb').read()
    assert d[:4] == b'NARC', path
    hdr_size = struct.unpack_from('<H', d, 0xC)[0]
    off = hdr_size
    assert d[off:off+4] == b'BTAF'
    btaf_size, count = struct.unpack_from('<IH', d, off + 4)
    spans = [struct.unpack_from('<II', d, off + 12 + 8*i) for i in range(count)]
    off += btaf_size
    assert d[off:off+4] == b'BTNF'
    off += struct.unpack_from('<I', d, off + 4)[0]
    assert d[off:off+4] == b'GMIF'
    base = off + 8
    return [d[base+s:base+e] for s, e in spans]

def gf_container(data):
    """GF container: 2-char magic, u16 section count, u32 offsets (last one = file size). Returns (magic, sections)."""
    magic = data[:2].decode('ascii', 'replace')
    n = struct.unpack_from('<H', data, 2)[0]
    offs = list(struct.unpack_from(f'<{n+1}I', data, 4))
    return magic, [data[offs[i]:offs[i+1]] for i in range(n)]

def area(files_dir, area_id):
    raw = open(os.path.join(files_dir, 'a', '0', '1', '3'), 'rb').read()
    pack, texset, srt, pat, ext, lights, edge, matcol = struct.unpack_from('<HHBBBBBB', raw, area_id * 10)
    return dict(pack=pack, texset=texset, srt=srt, pat=pat, exterior=ext, lights=lights, edge=edge, matcol=matcol)

def nitro_names(bmd):
    """Model names from a BMD0's MDL0 dictionary."""
    if bmd[:4] != b'BMD0':
        return []
    nblocks = struct.unpack_from('<H', bmd, 0xE)[0]
    for i in range(nblocks):
        bo = struct.unpack_from('<I', bmd, 0x10 + 4*i)[0]
        if bmd[bo:bo+4] == b'MDL0':
            d = bo + 8
            count = bmd[d + 1]
            size = struct.unpack_from('<H', bmd, d + 2)[0]
            names_at = d + size - 16 * count
            return [bmd[names_at+16*k:names_at+16*k+16].rstrip(b'\0').decode('ascii', 'replace') for k in range(count)]
    return []

def building_pack(files_dir, pack_id, exterior=True):
    """Returns [(resId, name, info_bytes, bmd_bytes)] for a building pack."""
    packs = narc_entries(arc_path(files_dir, 225 if exterior else 226))
    magic, secs = gf_container(packs[pack_id])
    assert magic == 'AB', magic
    n = len(secs) // 2
    out = []
    for i in range(n):
        res_id, typ, door = struct.unpack_from('<HHH', secs[i], 0)
        names = nitro_names(secs[n + i])
        out.append(dict(res_id=res_id, type=typ, door=None if door == 0xFFFF else door,
                        name=names[0] if names else f'res{res_id}', bmd=secs[n + i]))
    return out

def building_textures(files_dir, pack_id, exterior=True):
    return narc_entries(arc_path(files_dir, 174 if exterior else 175))[pack_id]

def map_textures(files_dir, texset):
    return narc_entries(arc_path(files_dir, 14))[texset]

def chunk(files_dir, chunk_id):
    magic, secs = gf_container(narc_entries(arc_path(files_dir, 8))[chunk_id])
    return magic, secs

def chunk_buildings(files_dir, chunk_id):
    magic, secs = chunk(files_dir, chunk_id)
    b = secs[-1]
    count = struct.unpack_from('<I', b, 0)[0]
    out = []
    for i in range(count):
        x, y, z, rot = struct.unpack_from('<iiiH', b, 4 + 16*i)
        res = (b[4 + 16*i + 14] << 8) | b[4 + 16*i + 15]
        out.append(dict(x=x / 4096, y=y / 4096, z=-z / 4096, rot=rot * 360 / 0x10000, res_id=res))
    return out

def gf_container_build(magic, sections):
    """Inverse of gf_container: 2-char magic, u16 count, u32 offsets (count+1, the last = file size), then data."""
    head = 4 + 4 * (len(sections) + 1)
    offs, pos = [], head
    for s in sections:
        offs.append(pos); pos += len(s)
    offs.append(pos)
    return magic.encode('ascii') + struct.pack(f'<H{len(offs)}I', len(sections), *offs) + b''.join(sections)
