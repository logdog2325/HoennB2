"""Zone headers (from the decomp's source) and zone entities (a/1/2/6). Formats: notes/GEN5_MAPS.md sections 5-6."""
import os, re, struct
from b2files import narc_entries, arc_path

HERE = os.path.dirname(os.path.abspath(__file__))
DECOMP = os.path.join(HERE, '..', 'external', 'pokebw2')
FILES = os.path.join(DECOMP, 'extract', 'b2_us', 'files')

def zone_headers():
    """{zone_id: {'name': ..., field: value}} parsed from data/zones/0000_zone_headers.s. Omitted fields take the
    defaults documented in include/asm/zone_header.inc (not filled in here)."""
    out, cur = {}, None
    for line in open(os.path.join(DECOMP, 'data/zones/0000_zone_headers.s')):
        m = re.match(r'\s*// Zone (\d+): (.*)', line)
        if m:
            cur = int(m.group(1)); out[cur] = {'name': m.group(2).strip()}; continue
        m = re.match(r'\s*ZoneHeader\s*(.*)', line)
        if m and cur is not None:
            for k, v in re.findall(r'(\w+)=([^,\s]+)', m.group(1)):
                out[cur][k] = int(v, 0) if re.match(r'^-?(0x[0-9a-fA-F]+|\d+)$', v) else v
    return out

WARP = struct.Struct('<HHBBHHHHHHH')     # 0x14
NPC = struct.Struct('<HHHHHHHHHHHHIHHi')  # 0x24
SIGN = struct.Struct('<HHHHiii')          # 0x14
TRIG = struct.Struct('<HHHHHHHHHhH')      # 0x16

def parse_entities(data):
    """Return (dict of lists, layout) for one a/1/2/6 entry."""
    init_off = struct.unpack_from('<I', data, 0)[0]
    n_sign, n_npc, n_warp, n_trig = data[4:8]
    off = 8
    out = {'signs': [], 'npcs': [], 'warps': [], 'triggers': []}
    for _ in range(n_sign):
        s, c, d, r, x, z, y = SIGN.unpack_from(data, off); off += SIGN.size
        out['signs'].append(dict(script=s, cond=c, dir=d, rail=r, x=x, z=z, y=y))
    for _ in range(n_npc):
        v = NPC.unpack_from(data, off); off += NPC.size
        out['npcs'].append(dict(zip(['uid', 'model', 'move', 'evtype', 'flag', 'script', 'dir', 'p0', 'p1', 'p2',
                                     'areaw', 'areah', 'rail', 'x', 'z', 'y'], v)))
    warps_at = off
    for _ in range(n_warp):
        dz, dw, d, t, r, x, y, z, w, h, u = WARP.unpack_from(data, off); off += WARP.size
        out['warps'].append(dict(dest_zone=dz, dest_warp=dw, dir=d, type=t, rail=r, x=x, y=y, z=z, w=w, h=h, unk=u,
                                 tile_x=(x - 8) // 16, tile_z=(z - 8) // 16))
    for _ in range(n_trig):
        v = TRIG.unpack_from(data, off); off += TRIG.size
        out['triggers'].append(dict(zip(['script', 'value', 'work', 'type', 'rail', 'x', 'z', 'w', 'h', 'y', 'unk'], v)))
    assert init_off + 4 == off, (init_off, off)
    return out, warps_at

def entities(entity_index, files=FILES):
    return parse_entities(narc_entries(arc_path(files, 126))[entity_index])[0]

if __name__ == '__main__':
    import sys
    zh = zone_headers()
    for z in map(int, sys.argv[1:]):
        h = zh[z]; e = entities(h['entities'])
        print(f"zone {z} {h['name']}: entities={h['entities']} matrix={h.get('matrix', 0)} area={h.get('area')}")
        for i, w in enumerate(e['warps']):
            print(f"  warp {i}: -> zone {w['dest_zone']} ({zh.get(w['dest_zone'], {}).get('name')}) warp {w['dest_warp']}"
                  f" type {w['type']} at tile ({w['tile_x']},{w['tile_z']}) {w['w']}x{w['h']}")

def build_entities(e, original, init=None):
    """Serialise entities dict (same shape as parse_entities' output) back to an a/1/2/6 entry. The zone's map-script
    table that follows the arrays (MapScript/MapScriptConditions, run on zone init/load) is `init` (assembled) if
    given, else copied from `original` unchanged."""
    init_off = struct.unpack_from('<I', original, 0)[0]
    tail = original[init_off + 4:] if init is None else init
    body = bytes([len(e['signs']), len(e['npcs']), len(e['warps']), len(e['triggers'])])
    for s in e['signs']:
        body += SIGN.pack(s['script'], s['cond'], s['dir'], s['rail'], s['x'], s['z'], s['y'])
    for n in e['npcs']:
        body += NPC.pack(*[n[k] for k in ['uid', 'model', 'move', 'evtype', 'flag', 'script', 'dir', 'p0', 'p1', 'p2',
                                          'areaw', 'areah', 'rail', 'x', 'z', 'y']])
    for w in e['warps']:
        body += WARP.pack(w['dest_zone'], w['dest_warp'], w['dir'], w['type'], w['rail'], w['x'], w['y'], w['z'],
                          w['w'], w['h'], w['unk'])
    for t in e['triggers']:
        body += TRIG.pack(*[t[k] for k in ['script', 'value', 'work', 'type', 'rail', 'x', 'z', 'w', 'h', 'y', 'unk']])
    return struct.pack('<I', len(body)) + body + tail
