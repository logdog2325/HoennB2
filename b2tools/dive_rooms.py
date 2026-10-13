"""dive agent: the Abandoned Ship's hidden floor and its two flooded rooms (Sapphire's AbandonedShip_HiddenFloorCorridors,
_HiddenFloorRooms, _Underwater1, _Underwater2: only Dive reaches them), built with the ship_hideouts agent's generator
(b2tools/ship_hideouts_rooms.py, used as a library: the same Royal Unova look, styles and zone-file writer). Writes
their recipes (data/interior_layouts), zone jsons, scripts and texts as that generator does, plus:
  - the flooded rooms: every walkable tile is the Abyssal Ruins' swimmable cell (models_interior "water": "cell"
    [0x9C, 2], "y" 0, "draw" false: models_cave_uw.py's underwater cells), the floor Black 2's Marine Tube sunlight
    net (h06nami01, texture set 246) as in the underwater maps, Black 2's diving music (SEQ_BGM_DIVING, the Abyssal
    Ruins');
  - warps Sapphire's way: the corridor's lower doors (3,8)/(6,8) like its (9,8) (solid door tiles walked into
    northwards, Royal Unova's cabin door), its upper doors (3,3)/(6,3)/(9,3) Sapphire's south arrows (type 1: press
    down on them, as exit mats; a door mat drawn), Underwater1's south arrows (3,7)/(4,7) type 1, Underwater2's
    water door (3,1) a notch in the north wall swum into: a solid door tile with a type-2 warp walked into northwards
    (a surfing/diving player's warps fire when bumping into a wall).

    python3 dive_rooms.py [Map ...]          (default: all four)

Story content (listed, not built: the story agents'): the four room keys (Sapphire's hidden items in the hidden rooms,
FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_1/2/4/6_KEY), the locked doors of rooms 1, 2, 4 and 6 (Sapphire swaps their
metatiles until FLAG_USED_ROOM_n_KEY: in Black 2 move those warps away with ObjInitWarpGPos at zone init while locked,
as the ship_hideouts notes suggest for the storage room) and their door signs (insert the key), the key sparkles
(OnFrame field effects); the Scanner (room 2) is an item ball here, Capt. Stern's exchange is the ship's story.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ship_hideouts_rooms as SH

ROOT = SH.ROOT
BGM_DIVING = 1014                    # SEQ_BGM_DIVING: Abyssal Ruins zones 241-245 (Sapphire: MUS_UNDERWATER)
UNDERWATER = ('AbandonedShip_Underwater1', 'AbandonedShip_Underwater2')
MINE = ('AbandonedShip_HiddenFloorCorridors', 'AbandonedShip_HiddenFloorRooms') + UNDERWATER

def corridor():
    name = 'AbandonedShip_HiddenFloorCorridors'
    SH.ship_room(name, 'sh_corridor', stair_tiles=[(3, 8), (6, 8)], inner_walls=SH.SHIP_INNER,   # (sweep_rooms: the cabin block)
                 furniture=[dict(m='cabin_door', tile=[x, 9], wall='N', gap=0.5, y=0, lift=False,
                                 _what=f'door ({x},8): Royal Unova\'s cabin door') for x in (3, 6)],
                 mats=[dict(tex='in70_mat1', src=351, border=0.25, border_units=3, y=0, rect=[x, 3, x, 3],
                            _what=f'door ({x},3): Sapphire\'s south arrow (a door indent)') for x in (3, 9)],
                 water=dict(tex=SH.T(337, 'd0_miz', size=32), bank=SH.T(337, 'd0_mizgiwa', u_size=16)))
    SH.ROOMS[name]['warp_kind'] = {3: dict(type=1, dir=1), 5: dict(type=1, dir=1)}

def rooms():
    SH.ship_room('AbandonedShip_HiddenFloorRooms', 'sh_cabin')

def flooded(name, warp_kind, doors=()):
    """A flooded room; `doors`: Sapphire's water doors (notches swum into) as solid door tiles with a warp walked into
    (a surfing or diving player's warp fires when bumping into a wall: ov036 FieldPlayerGrid_UpdateSurfBrake ->
    CheckWarpAtHitWall; stepping onto a walkable warp tile does not fire it [test])."""
    sm = SH.smap(name)
    swim = sorted(t for t in SH.walkable(name) if t not in doors)
    SH.ship_room(name, 'sh_cabin', stair_tiles=list(doors),
                 water=dict(tiles=[list(t) for t in swim], cell=[0x9C, 2], y=0, draw=False),
                 floor_tex=[dict(rect=[0, 0, sm['w'] - 1, sm['h'] - 1], tex='h06nami01', src=246, size=32,
                                 _what='underwater: the Marine Tube\'s sunlight net (as the underwater maps\' trenches)')])
    SH.ROOMS[name]['warp_kind'] = warp_kind

corridor()
rooms()
flooded('AbandonedShip_Underwater1', {0: dict(type=1, dir=1), 1: dict(type=1, dir=1)})
flooded('AbandonedShip_Underwater2', {0: dict(type=2, dir=2)}, doors=[(3, 1)])
for n in MINE: SH.ROOMS[n]['parent'] = 74            # the ship family's first zone (the deck), as ship_hideouts does

def finish_underwater(name, report):
    """Diving music. (No underwater effect: the Abyssal Ruins' effect models are a fixed bowl of light and haze around
    world (256, 0, 256), made for its one-chunk descent; around a ship room they show in the black outside its walls.)"""
    reg = SH.rooms_registry()[name]; zone = reg['zone']
    zp = os.path.join(SH.ZONES, f'{zone}.json')
    zj = json.load(open(zp))
    for k in ('bgm0', 'bgm1', 'bgm2', 'bgm3'): zj['header'][k] = BGM_DIVING
    json.dump(zj, open(zp, 'w'), indent=1, ensure_ascii=False)
    ip = os.path.join(ROOT, 'src', 'field_scripts', f'{reg["init_scripts"]:04d}_room_{name}_init.s')
    if os.path.exists(ip) and 'b2tools/dive_rooms.py' in open(ip).read():     # an earlier run's effect: to the Trash
        os.rename(ip, os.path.join(os.path.expanduser('~/.Trash'), os.path.basename(ip) + f'.{os.getpid()}'))
    report.append(f'{name}: diving music')

def main(args):
    names = [a for a in args if a in MINE] or list(MINE)
    family = set(SH.ROOMS)
    report = []
    for n in names:
        SH.write_room(n, family, report)
        if n in UNDERWATER: finish_underwater(n, report)
    print('\n'.join(report))

if __name__ == '__main__':
    main(sys.argv[1:])
