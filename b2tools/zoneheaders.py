"""Read/write Black 2 zone headers (a/0/1/2: one file, 615 x 0x30 bytes). Field layout from the decomp's
include/asm/zone_header.inc (ZoneHeader macro)."""
import struct
import narcio

FMT = struct.Struct('<BBHHHHH4HHHHHHHHH3I')   # 0x30 bytes
FIELDS = ['map_type', 'npc_cache', 'area', 'matrix', 'scripts', 'init_scripts', 'text', 'bgm0', 'bgm1', 'bgm2', 'bgm3',
          'enc', 'entities', 'parent', 'place_word', 'weather_word', 'flags', 'cam_bound', 'icon_word', 'fly_x', 'fly_y', 'fly_z']
assert FMT.size == 0x30

def parse(data):
    out = []
    for i in range(len(data) // 0x30):
        h = dict(zip(FIELDS, FMT.unpack_from(data, 0x30 * i)))
        h['encounters'], h['enc_slot'] = h['enc'] & 0x1FFF, h['enc'] >> 13
        h['place'], h['place_display'] = h['place_word'] & 0x3FF, h['place_word'] >> 10
        out.append(h)
    return out

def build(headers):
    out = b''
    for h in headers:
        h = dict(h)
        h['enc'] = (h['encounters'] & 0x1FFF) | (h['enc_slot'] << 13)
        h['place_word'] = (h['place'] & 0x3FF) | (h['place_display'] << 10)
        out += FMT.pack(*[h[f] for f in FIELDS])
    return out

def load(files):
    entries = narcio.load(files, 12)
    return parse(entries[0]), entries

def save(files, headers, entries):
    entries[0] = build(headers) + entries[0][len(headers) * 0x30:]
    narcio.save(files, 12, entries)
