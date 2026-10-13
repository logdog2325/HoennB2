"""Inside of the moving truck (Sapphire's InsideOfTruck, 5x5 tiles) as a Black 2 interior chunk for zone 394.

    python3 models_truck.py ../work/interiors/truck

Writes terrain.dae (+ texture PNGs beside it), palettes.txt, collision.per, placements.bin, door.dae, truck.json,
room.json (the manifest b2tools/patches/interiors.py installs into zone 394, data/interiors/394.json).
Built like Black 2's own house rooms (chunk 838, notes/OPENING.md): floor at y -2, walls ~48 high with dark caps,
no south wall (the camera looks from the south) but a floor lip, room in an otherwise empty chunk (black around it).
Textures: Plasma Frigate metal from map texture set 379 (in77room_01 floor, in77g_kabe1 panels, in77k_kabe1 ribs,
in77i_yuka2 trim); they are merged into texture set 284 (zone 394's area). Furniture: Black 2's
cardboard moving boxes box01 (res 92) / box02 (res 93) from interior building pack 2.

The rear door (Sapphire's Task_HandleTruckSequence: the exit tiles turn to bright ExitLight metatiles when the door
opens). The closed door is part of the terrain; the OPEN door is building res DOOR_RES (door.dae, added to interior
pack 2 with info type 11, so BMSetVisible 8, 13, 10, 0/1 finds it): Black 2's dungeon-exit light (in14_exit_a, map
texture set 295: its white middle) filling the doorway in front of the closed door, and the light falling in on the
exit column (in14_light_a, the same set's A5I3 light gradient, white at 93% to clear, laid on the floor).
Like Sapphire's map, the open state is the default (a Continue or field reload shows the door open); the new-game
ride (src/field_scripts/scenes/truck.inc Script_31) hides it on the black screen and shows it when the door opens.

Truck tile (tx, tz) = Sapphire's map tile = chunk tile (OX + tx, OZ + tz). Walkable tiles are Sapphire's (collision 0):
(1-4, 1), (1-4, 2), (3-4, 3); the player starts on (2, 2); column 4 is the open back of the truck (exit trigger).
"""
import os, sys, json, struct, shutil
from dae import Model

HERE = os.path.dirname(os.path.abspath(__file__))
OX, OZ = 8, 8
DOOR_RES = 200
WALK = {(x, 1) for x in range(1, 5)} | {(x, 2) for x in range(1, 5)} | {(3, 3), (4, 3)}
BOXES = [(93, 0, 1, 0), (92, 0, 2, 0), (93, 0, 3, 0), (92, 1, 3, 0), (93, 2, 3, 90), (92, 1, 0.8, 0), (92, 3, 0.8, 0)]
SIGNS = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (1, 0), (3, 0)]     # box tiles that show the box text
TEXSRC = {'in77room_01': 379, 'in77g_kabe1': 379, 'in77k_kabe1': 379, 'in77i_yuka2': 379}
LIGHTSRC = {'in14_exit_a': 295, 'in14_light_a': 295}   # the open door's light (map texture set 295, a cave exit)
DOOR_TYPE = 11                        # info type 11 -> converted type 8 = BMSetVisible's first argument
T = lambda t: t * 16 - 256           # chunk tile -> model units
Y0, YW = -2, 46                       # floor and wall-top heights (Black 2 house: -2 and 47)

def tile_x(tx): return T(OX + tx)
def tile_z(tz): return T(OZ + tz)

def wall_x(m, x, z0, z1, y0, y1, mat, facing_east, u_per=16.0, v=(0, 1)):
    """Vertical wall in the plane x, from z0 to z1 (z0 < z1); v spans the texture over y0..y1."""
    a, b = (z1, z0) if facing_east else (z0, z1)
    ua, ub = 0, abs(z1 - z0) / u_per
    m.quad(mat, [(x, y0, a, ua, v[0]), (x, y0, b, ub, v[0]), (x, y1, b, ub, v[1]), (x, y1, a, ua, v[1])])

def wall_z(m, z, x0, x1, y0, y1, mat, facing_south, u_per=16.0, v=(0, 1)):
    a, b = (x0, x1) if facing_south else (x1, x0)
    ua, ub = 0, abs(x1 - x0) / u_per
    m.quad(mat, [(a, y0, z, ua, v[0]), (b, y0, z, ub, v[0]), (b, y1, z, ub, v[1]), (a, y1, z, ua, v[1])])

def flat(m, x0, x1, z0, z1, y, mat, per=16.0):
    m.quad(mat, [(x0, y, z1, x0 / per, -z1 / per), (x1, y, z1, x1 / per, -z1 / per),
                 (x1, y, z0, x1 / per, -z0 / per), (x0, y, z0, x0 / per, -z0 / per)])

def build_terrain():
    m = Model('truck')
    xl, xr = tile_x(0) - 3, tile_x(5) + 3          # inner faces of the side walls
    zb, zf = tile_z(0) + 4, tile_z(4)               # back wall face, front lip
    zo0, zo1 = tile_z(1), tile_z(4)                 # door opening (rows 1-3)
    zmid = (zo0 + zo1) / 2
    th = 8                                          # wall thickness
    flat(m, xl, xr, zb, zf, Y0, 'in77room_01')
    # back wall: panels with ribs at both ends and in the middle, dark cap on top
    wall_z(m, zb, xl, xr, Y0, YW, 'in77g_kabe1', True)
    for rx in (xl, (xl + xr) / 2 - 8, xr - 16):
        wall_z(m, zb + 0.5, rx, rx + 16, Y0, YW, 'in77k_kabe1', True)
    flat(m, xl - th, xr + th, zb - th, zb, YW, 'in77i_yuka2', per=8)
    # left wall (the cab side)
    wall_x(m, xl, zb, zf, Y0, YW, 'in77g_kabe1', True)
    flat(m, xl - th, xl, zb, zf, YW, 'in77i_yuka2', per=8)
    # right side: short wall pieces around the rear door opening, header beam above it, daylight behind it
    wall_x(m, xr, zb, zo0, Y0, YW, 'in77g_kabe1', False)
    wall_x(m, xr, zo1, zf, Y0, YW, 'in77g_kabe1', False) if zf > zo1 else None
    wall_x(m, xr, zo0, zo1, 40, YW, 'in77i_yuka2', False, u_per=8, v=(0, 0.75))
    flat(m, xr, xr + th, zb, zf, YW, 'in77i_yuka2', per=8)
    # the closed rear door in the opening (the open door is building res DOOR_RES, drawn in front of it)
    for z0, z1, mat in ((-24, -2, 'in77g_kabe1'), (2, 24, 'in77g_kabe1'), (-2, 2, 'in77k_kabe1')):
        wall_x(m, xr - 0.5, zmid + z0, zmid + z1, Y0, 40, mat, False, u_per=16 if mat != 'in77k_kabe1' else 4)
    # front: floor lip and the cut ends of the side walls, like Black 2's rooms
    wall_z(m, zf, xl - th, xr + th, Y0 - 15, Y0, 'in77i_yuka2', True, u_per=8, v=(0, 1))
    wall_z(m, zf, xl - th, xl, Y0, YW, 'in77i_yuka2', True, u_per=8, v=(0, 1))
    wall_z(m, zf, xr, xr + th, Y0, YW, 'in77i_yuka2', True, u_per=8, v=(0, 1))
    return m

LIGHT_IN = 32                         # how far the light reaches into the truck (units from the doorway)
LAYER = 2                             # gap between stacked faces (as models_interior.py's decals and rugs)

def build_door():
    """The OPEN rear door (building res DOOR_RES), origin at the doorway's centre on the floor (the inner face of the
    right wall, xr): bright exit light filling the doorway just in front of the closed door (terrain, at x -0.5) and
    the light falling in on the floor of the exit column, fading away from the door. Converted unlit (ToNsbmd --vcol,
    white vertex colours: b2tools/rebuild_interiors.sh), so the light is not shaded like the walls."""
    m = Model('truck_door')
    h, w = 40, 24                         # doorway: 40 high, rows 1-3 = 48 wide (z -24..24)
    a, b = 11 / 32, 21 / 32               # in14_exit_a's pure white middle (pixels 11-20 both ways, so v's direction
    x = -0.5 - LAYER                      # LAYER in front of the closed door (models_interior's decal gap)
    m.quad('in14_exit_a', [(x, Y0, -w, a, a), (x, Y0, w, b, a), (x, h, w, b, b), (x, h, -w, a, b)])  # does not matter)
    # in14_light_a: white, alpha 0 (top row) .. 93% (bottom row); v = 1 is the top row (tested), so v 0 at the door
    y = Y0 + LAYER
    m.quad('in14_light_a', [(x, y, -w, 0, 0), (x - LIGHT_IN, y, -w, 0, 1), (x - LIGHT_IN, y, w, 1, 1), (x, y, w, 1, 0)])
    return m

def collision():
    per = bytearray(struct.pack('<HH', 32, 32))
    for z in range(32):
        for x in range(32):
            walk = (x - OX, z - OZ) in WALK
            per += struct.pack('<HHHH', 0, 3, 0, 0x80) if walk else struct.pack('<HHHH', 0, 3, 1, 0x81)
    return bytes(per)

def placements():
    recs = []
    def put(res, lx, lz, rot=0):
        recs.append(struct.pack('<iiiH', round(lx * 4096), 0, round(-lz * 4096), rot * 0x10000 // 360)
                    + bytes([res >> 8, res & 0xFF]))
    for res, tx, tz, rot in BOXES:
        put(res, tile_x(tx) + 8, tile_z(0) + tz * 16 + 8, rot)
    put(DOOR_RES, tile_x(5) + 3, tile_z(2) + 8)
    return struct.pack('<I', len(recs)) + b''.join(recs)

def main(out):
    sys.path.insert(0, HERE)
    import b2files, nsbtx
    files = os.path.join(HERE, '..', 'external', 'pokebw2', 'build', 'b2_us', 'files')
    os.makedirs(out, exist_ok=True)
    texs = {}
    for ts in set(TEXSRC.values()) | set(LIGHTSRC.values()):
        texs.update({n: img for n, img, _ in nsbtx.decode(b2files.map_textures(files, ts))})
    terrain, door = build_terrain(), build_door()
    clamp = {'in14_light_a': ('CLAMP', 'CLAMP')}
    for m, name in ((terrain, 'terrain'), (door, 'door')):
        for mat in m.tris:
            texs[mat].save(os.path.join(out, mat + '.png'))
        m.write(os.path.join(out, name + '.dae'), wrap=clamp)
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in {**TEXSRC, **LIGHTSRC}))
    open(os.path.join(out, 'collision.per'), 'wb').write(collision())
    open(os.path.join(out, 'placements.bin'), 'wb').write(placements())
    json.dump(dict(origin=[OX, OZ], start=[OX + 2, OZ + 2], door_res=DOOR_RES, door_tile=[OX + 5, OZ + 2],
                   exit_tiles=[[OX + 4, OZ + z] for z in (1, 2, 3)], signs=[[OX + x, OZ + z] for x, z in SIGNS],
                   textures={t: s for t, s in TEXSRC.items()}, door_textures=sorted(door.tris), door_type=DOOR_TYPE),
              open(os.path.join(out, 'truck.json'), 'w'), indent=1)
    # manifest for b2tools/patches/interiors.py (same format as models_interior.py's room.json; data/interiors/394.json)
    walk = [(OX + x, OZ + z) for x, z in WALK]
    xs, zs = [x for x, _ in walk], [z for _, z in walk]
    cam = [min(xs) * 16 + 8 + 45, max(xs) * 16 + 8 - 45, min(zs) * 16 + 8 + 6, max(zs) * 16 + 8 - 32]
    if cam[0] > cam[1]: cam[0] = cam[1] = (cam[0] + cam[1]) // 2
    if cam[2] > cam[3]: cam[2] = cam[3] = (cam[2] + cam[3]) // 2
    json.dump(dict(name='truck', map='InsideOfTruck', origin=[OX, OZ], size=[5, 5], terrain='terrain.nsbmd',
                   collision='collision.per', placements='placements.bin', map_textures=TEXSRC,
                   models=[dict(res=r, pack=2) for r in sorted({b[0] for b in BOXES})],
                   extra_models=[dict(res=DOOR_RES, file='door.nsbmd', type=DOOR_TYPE,
                                      textures={t: LIGHTSRC[t] for t in sorted(door.tris)})],
                   camera=cam, fly=[OX + 2, OZ + 2], warp_spots=[]),
              open(os.path.join(out, 'room.json'), 'w'), indent=1)
    print('truck ->', out, sum(len(t) for t in terrain.tris.values()), 'terrain triangles')

if __name__ == '__main__':
    main(sys.argv[1])
