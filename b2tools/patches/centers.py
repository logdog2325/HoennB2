"""Pokémon Center respawn records (centers agent): Black 2's ov012 RESPAWN_ZONE_INFO for Hoenn's Centers.

Black 2 (external/pokebw2/src/ov012/respawn_zone.c, ov035 event_mapchange.c):
  - entering a zone whose record has canReturnHere sets the return location (FieldMapControl_InitSpawn);
  - a blackout returns you to the record's zone at its tile (x, z), facing up (CreateRespawnZoneChangeData), and the
    global script 2001 (data/field_scripts/1230.s Script_2) has the actor 2 tiles north of you (the nurse) heal you;
  - Teleport and the Escape Rope after a blackout go to the record's main zone (GetRespawnZoneMainZone);
  - entering a record's main zone sets its discovery flag when discoverOnVisit (the Fly destinations).
The 15 Hoenn 1F rooms are Black 2's own Center zones (converter/allocate_interiors.py), every one with a record at
tile (7, 12); the rooms put the tile in front of the nurse there (recipe origin (0, 8)), so the blackout itself needs no
change. This patch points each of those records' main zone at its Hoenn town (Black 2's were the Unova towns:
Lavaridge's Center returned Teleport to Lilycove, ...), turns discoverOnVisit on, and sets the two unused (zone, x, z)
copies (unk0A..unk12, read by no decompiled code) to the town and the tile in front of the Center's door.
Table: ov012 0x0216c33c (symbols.txt) = arm9_ov012.bin offset 0x1BF7C, 82 records of 20 bytes:
  u16 flag, u16 canReturnHere:1 discoverOnVisit:1, u16 zone, u8 x, u8 z, u16 mainZone, u16 x2, z2, zone3, x3, z3."""
import os, sys, json, struct

TABLE, COUNT, SIZE = 0x1BF7C, 82, 20
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

def records(data):
    return [list(struct.unpack_from('<HHHBBHHHHHH', data, TABLE + SIZE * i)) for i in range(COUNT)]

def center_towns():
    """{1F zone: (town map, town zone)} for every Hoenn Pokémon Center 1F."""
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    out = {}
    for name, r in rooms.items():
        if r['status'] == 'center' and name.endswith('_PokemonCenter_1F'):
            town = name.split('_PokemonCenter')[0]
            out[r['zone']] = (town, zones[town]['zone'])
    return out

def door_tile(town, town_zone, center_zone):
    """World tile just south of the town's door into the Center (work/world/world.json), or None."""
    p = os.path.join(os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'), 'world.json')
    if not os.path.exists(p): return None
    z = json.load(open(p))['zones'].get(str(town_zone), {})
    for d in z.get('doors', []):
        if d['dest_zone'] == center_zone: return (d['x'] - 8) // 16, (d['z'] - 8) // 16 + 1
    cfg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world.json')))['maps'].get(town, {})
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    for dest, slot in cfg.get('warps', {}).items():     # a door that keeps one of Black 2's own warp slots
        if rooms.get(town + '_PokemonCenter_1F', {}).get('map_id') == dest and str(slot) in z.get('warps', {}):
            x, _, zz = z['warps'][str(slot)]
            return (x - 8) // 16, (zz - 8) // 16 + 1
    return None

# Black 2's GetReturnLocationIdx (arm9 0x02017310, used by the blackout, Teleport and the Escape Rope) treats return
# locations 15 and 16 as one place and picks between them by a game check (0x0201732A: bhi past it when the location
# is neither). Here 15 is Dewford's Center and 16 Rustboro's, so losing after healing in Rustboro could wake you up in
# Dewford (stuck there before Mr. Briney sails: v16-v16.2). The branch now always skips the swap.
RETURN_PAIR_BRANCH, ARM9_BASE = 0x0201732A, 0x02004000

def apply_arm9(code):
    path = os.path.join(code, 'arm9.bin')
    data = bytearray(open(path, 'rb').read())
    off = RETURN_PAIR_BRANCH - ARM9_BASE
    assert data[off:off + 2] in (b'\x0b\xd8', b'\x0b\xe0'), data[off:off + 2].hex()   # bhi / b to 0x02017344
    data[off:off + 2] = b'\x0b\xe0'
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)

def apply_code(code):
    apply_arm9(code)
    path = os.path.join(code, 'arm9_ov012.bin')
    data = bytearray(open(path, 'rb').read())
    towns = center_towns()
    done, recs = [], records(data)
    for i, r in enumerate(recs):
        flag, bits, zone, x, z, main, x2, z2, zone3, x3, z3 = r
        if zone not in towns: continue
        assert bits & 1 and (x, z) == (7, 12), f'record {i}: zone {zone} {r}'
        town, tz = towns[zone]
        t = door_tile(town, tz, zone) or (x2, z2)
        new = [flag, bits | 2, zone, x, z, tz, t[0], t[1], tz, t[0], t[1]]
        struct.pack_into('<HHHBBHHHHHH', data, TABLE + SIZE * i, *new)
        done.append(f'{zone}->{town}')
    # Black 2's other Center records (Unova Centers) now name Hoenn maps that are not Centers (zone 20 Mt. Pyre's
    # exterior, 146 Shoal Cave's low-tide inner room) or no map: entering one made it the return point, and a blackout
    # then put you at its tile (7, 12) with no nurse. Only Hoenn's 15 Centers can be returned to now.
    for i, r in enumerate(records(data)):
        if r[1] & 1 and r[2] not in towns and i != 0:
            struct.pack_into('<H', data, TABLE + SIZE * i + 2, r[1] & ~1)
            done.append(f'record {i + 1} zone {r[2]}: no return')
    missing = sorted(set(towns) - {r[2] for r in recs})
    assert not missing, f'no respawn record for Center zones {missing}'
    # a town that is also the main zone of an earlier record would give its discovery flag to that one
    recs = records(data)
    clash = [(i, r[2], r[5]) for i, r in enumerate(recs) if r[5] in {tz for _, tz in towns.values()} and r[2] not in towns]
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)
    return f'respawn records -> Hoenn towns: {", ".join(done)}' + (f'; other records with a Hoenn town as main zone: {clash}' if clash else '')

if __name__ == '__main__':          # print the table as it is in the decomp's build (and what the patch would write)
    d = open(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build', 'arm9_ov012.bin'), 'rb').read()
    towns = center_towns()
    for i, r in enumerate(records(d)):
        if r[2] in towns: print(i, r, '->', towns[r[2]])
