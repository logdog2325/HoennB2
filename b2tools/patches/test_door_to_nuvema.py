"""TEST ONLY: the player's front-door mat in Aspertia (zone 428, warp 0) leads to Nuvema Town (zone 389) instead,
arriving at Nuvema's warp 0. Lets the emulator harness reach the slice from the opening savestate."""
import struct
import narcio
from zones import parse_entities, WARP

def apply(files):
    ents = narcio.load(files, 126)
    data = bytearray(ents[167])          # zone 428's entities (header field entities=167)
    _, warps_at = parse_entities(bytes(data))
    old = struct.unpack_from('<HH', data, warps_at)
    struct.pack_into('<HH', data, warps_at, 389, 0)
    ents[167] = bytes(data)
    narcio.save(files, 126, ents)
    return f'zone 428 warp 0: {old} -> (389, 0)'
