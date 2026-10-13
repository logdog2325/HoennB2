"""Gen 3 movement types (Sapphire, Ruby, Emerald) as Black 2 move codes (v165_fixes 2026-10-11; notes/NPC_MOVEMENT.md).

    npc(movement, rng, graphics) -> dict(move, [dir], areaw, areah, [evtype], note) for any MOVEMENT_TYPE_*, None to
                                    keep the writer's own (INVISIBLE, things that are not people)
    room_npc(object)             -> the keys a room generator writes (data/interiors/<zone>.json)
    walk(movement, rng)          -> dict(move, dir, areaw, areah) for a walker (WALK_SEQUENCE_*, WALK_*_AND_*), else None

Black 2's own code [code] (ov036 ACTOR_MOVE_CODE_FUNCTION_TABLES 0x021cc990, route lists at 0x021cbc70; pokebw2
field_actor_tool.c for the collision and walk-area checks; briney_peeko found 42/43, commit 0474eda):
- 21-44 walk a route of four legs, the same 24 routes in the same order as Gen 3's MOVEMENT_TYPE_WALK_SEQUENCE_*
  (0x1D-0x34): Black 2 code = Gen 3 value - 8. Each leg walks one tile at a time and turns to the next leg when the next
  tile is outside the walk area (spawn x +- areaW, spawn z +- areaH); the third leg also ends level with the start
  (x or z, the same axis as Gen 3's MovementType_WalkSequence*_Step1); back at the start the route begins again. A tile
  blocked otherwise (wall, height step >= 20, another actor) makes it walk in place and try again, as in Gen 3
  (MoveNextDirectionInSequence). Sapphire's movement_range_x/y are the same radius (pokeruby
  IsCoordOutsideObjectEventMovementRange), so they copy over as areaW/areaH.
- 20 walks back and forth along its direction field between the start and the walk area's edge, as Gen 3's
  MOVEMENT_TYPE_WALK_UP_AND_DOWN / DOWN_AND_UP / LEFT_AND_RIGHT / RIGHT_AND_LEFT (MovementType_WalkBackAndForth: start ->
  edge -> start -> edge ...); the direction field is the first way it walks.
- Differences: Black 2's route list for 25 (Gen 3 UP_LEFT_RIGHT_DOWN) holds code 26's directions (L, R, D, U), so it
  is not used: UP_LEFT_RIGHT_DOWN walks code 21's mirror image (up, RIGHT, left back, down; Route 117's little boy, the
  only Sapphire object of that type; tested walkable). Gen 3 ends the routes of 22, 23, 26, 27, 30, 31, 34, 35 on their
  second leg, Black 2 on the third: no Sapphire object uses them.
- A Gen 3 range of 0 means "no limit" on that axis, a Black 2 area of 0 "no movement" (0xFFFF = no limit); every
  Sapphire walker has a range >= 1 on the axes it walks along, so the values copy as they are.
Trainers (evType 1) look along the way they face, which these codes turn to the way they walk (as Gen 3); once one
spots the player Black 2 sets its code to 0 (event_trainer_eye.c), as Gen 3 sets a facing type.
"""
DIR = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3}

# Gen 3 MOVEMENT_TYPE_WALK_SEQUENCE_* in value order 0x1D..0x34 (pokeruby include/constants/event_object_movement.h)
SEQUENCES = ['UP_RIGHT_LEFT_DOWN', 'RIGHT_LEFT_DOWN_UP', 'DOWN_UP_RIGHT_LEFT', 'LEFT_DOWN_UP_RIGHT', 'UP_LEFT_RIGHT_DOWN',
             'LEFT_RIGHT_DOWN_UP', 'DOWN_UP_LEFT_RIGHT', 'RIGHT_DOWN_UP_LEFT', 'LEFT_UP_DOWN_RIGHT', 'UP_DOWN_RIGHT_LEFT',
             'RIGHT_LEFT_UP_DOWN', 'DOWN_RIGHT_LEFT_UP', 'RIGHT_UP_DOWN_LEFT', 'UP_DOWN_LEFT_RIGHT', 'LEFT_RIGHT_UP_DOWN',
             'DOWN_LEFT_RIGHT_UP', 'UP_LEFT_DOWN_RIGHT', 'DOWN_RIGHT_UP_LEFT', 'LEFT_DOWN_RIGHT_UP', 'RIGHT_UP_LEFT_DOWN',
             'UP_RIGHT_DOWN_LEFT', 'DOWN_LEFT_UP_RIGHT', 'LEFT_UP_RIGHT_DOWN', 'RIGHT_DOWN_LEFT_UP']
LOOP = {name: 0x1D + i - 8 for i, name in enumerate(SEQUENCES)}            # name -> Black 2 code 21..44
LOOP['UP_LEFT_RIGHT_DOWN'] = LOOP['UP_RIGHT_LEFT_DOWN']                    # (Black 2's 25 walks 26's route: see above)
BACK_AND_FORTH = {'UP_AND_DOWN': 'UP', 'DOWN_AND_UP': 'DOWN', 'LEFT_AND_RIGHT': 'LEFT', 'RIGHT_AND_LEFT': 'RIGHT'}
WALK_CODES = set(range(20, 45))                                             # (codes that walk a fixed path)


# Every Gen 3 movement type (pokeruby / pokeemerald include/constants/event_object_movement.h) -> (Black 2 code, first
# direction or None = keep the object's own, area: 'range' = Sapphire's movement range, evType for trainers or None,
# source / note). Black 2's codes [code]: ov036 ACTOR_MOVE_CODE_FUNCTION_TABLES (pokebw2_field asm _dsd_gap@ov036_4.s
# 36982, entries {code, init, update, delete}; direction lists data_ov036_021cbc70), its own NPCs in a/1/2/6 counted.
FACE = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3}
NO_LIMIT = 0xFFFF
TABLE = {
    'NONE': (0, None, None, None, 'stand (code 0: empty init/update)'),
    'LOOK_AROUND': (2, None, None, None, 'look around, 4 directions (list 0; random 16-64 frame timer) [exact]'),
    'WANDER_AROUND': (3, None, 'range', None, 'wander inside the area (list 0xb) [exact]'),
    'WANDER_UP_AND_DOWN': (4, None, 'range', None, 'wander up/down inside the area (list 0xc) [exact]'),
    'WANDER_DOWN_AND_UP': (4, None, 'range', None, 'wander up/down inside the area (list 0xc) [exact]'),
    'WANDER_LEFT_AND_RIGHT': (5, None, 'range', None, 'wander left/right inside the area (list 0xd) [exact]'),
    'WANDER_RIGHT_AND_LEFT': (5, None, 'range', None, 'wander left/right inside the area (list 0xd) [exact]'),
    'FACE_UP': (14, 0, None, None, 'face up (code 0 + dir 0 is the same: both only set the facing)'),
    'FACE_DOWN': (15, 1, None, None, 'face down (= code 0 + dir 1)'),
    'FACE_LEFT': (16, 2, None, None, 'face left (= code 0 + dir 2)'),
    'FACE_RIGHT': (17, 3, None, None, 'face right (= code 0 + dir 3)'),
    'PLAYER': (1, None, None, None, 'the player'),
    'BERRY_TREE_GROWTH': (0, None, None, None, "a berry tree stands (Black 2's berry code 47 is a NULL table entry: crashes)"),
    'FACE_DOWN_AND_UP': (45, None, None, None, 'look up/down (list 9) [exact]'),
    'FACE_LEFT_AND_RIGHT': (46, None, None, None, 'look left/right (list 10) [exact]'),
    'FACE_UP_AND_LEFT': (6, None, None, None, 'look up/left (list 1) [exact]'),
    'FACE_UP_AND_RIGHT': (7, None, None, None, 'look up/right (list 2) [exact]'),
    'FACE_DOWN_AND_LEFT': (8, None, None, None, 'look down/left (list 3) [exact]'),
    'FACE_DOWN_AND_RIGHT': (9, None, None, None, 'look down/right (list 4) [exact]'),
    'FACE_DOWN_UP_AND_LEFT': (10, None, None, None, 'look up/down/left (list 5) [exact]'),
    'FACE_DOWN_UP_AND_RIGHT': (11, None, None, None, 'look up/down/right (list 6) [exact]'),
    'FACE_UP_LEFT_AND_RIGHT': (12, None, None, None, 'look up/left/right (list 7) [exact]'),
    'FACE_DOWN_LEFT_AND_RIGHT': (13, None, None, None, 'look down/left/right (list 8) [exact]'),
    'ROTATE_COUNTERCLOCKWISE': (18, None, None, None, 'spin counter-clockwise, a turn per 24 frames [exact]'),
    'ROTATE_CLOCKWISE': (19, None, None, None, 'spin clockwise [exact]'),
    # 0x19-0x34: walk() below (20 back and forth, 21-44 routes)
    'COPY_PLAYER': (55, 0, None, None, "turn as the player faces (55-58; Black 2 copies the facing only, Gen 3 also walks)"),
    'COPY_PLAYER_IN_GRASS': (59, 0, None, None, "turn as the player faces (59-62: the grass flag is never read)"),
    'COPY_PLAYER_OPPOSITE': (2, None, None, None, 'Black 2 has no mirrored copy: looks around (approximated)'),
    'COPY_PLAYER_COUNTERCLOCKWISE': (2, None, None, None, 'Black 2 has no rotated copy: looks around (approximated)'),
    'COPY_PLAYER_CLOCKWISE': (2, None, None, None, 'Black 2 has no rotated copy: looks around (approximated)'),
    'COPY_PLAYER_OPPOSITE_IN_GRASS': (2, None, None, None, 'Black 2 has no mirrored copy: looks around (approximated)'),
    'COPY_PLAYER_COUNTERCLOCKWISE_IN_GRASS': (2, None, None, None, 'Black 2 has no rotated copy: looks around (approximated)'),
    'COPY_PLAYER_CLOCKWISE_IN_GRASS': (2, None, None, None, 'Black 2 has no rotated copy: looks around (approximated)'),
    'TREE_DISGUISE': (54, 1, None, 1, "hidden trainer in grass, jumps out (54: Black 2's own, Pinwheel Forest; "
                      "EventTrainerEyeSub_DecideJumpOut 0x33-0x36/0x55); sees down as Gen 3's disguise (evType 1)"),
    'MOUNTAIN_DISGUISE': (53, 1, None, 1, 'hidden trainer under soil, jumps out (53, mv_hide_tsuchi); sees down (evType 1)'),
    'HIDDEN': (53, 1, None, 2, 'buried trainer under soil, jumps out (53); sees all 4 ways as Gen 3 TRAINER_TYPE_BURIED (evType 2)'),
    'BURIED': (53, 1, None, 2, '(Emerald name of HIDDEN) as HIDDEN'),
    'INVISIBLE': (None, None, None, None, 'no Black 2 code: invisibility is the sprite (model) or a hide flag; the code is kept'),
    'WALK_IN_PLACE_UP': (14, 0, None, None, 'faces up: Black 2 has no walk-in-place move code (script movements 28-43 only) (approximated)'),
    'WALK_IN_PLACE_DOWN': (15, 1, None, None, 'faces down (no walk-in-place code; approximated)'),
    'WALK_IN_PLACE_LEFT': (16, 2, None, None, 'faces left (no walk-in-place code; approximated)'),
    'WALK_IN_PLACE_RIGHT': (17, 3, None, None, 'faces right (no walk-in-place code; approximated)'),
}
for _k in ('JOG', 'RUN', 'WALK_SLOWLY', 'WALK_FAST'):
    for _d in FACE:
        TABLE[f'{_k}_IN_PLACE_{_d}'] = (14 + FACE[_d], FACE[_d], None, None, f'faces {_d.lower()} (no in-place code; approximated)')


_STATIC = {}
def static_graphics(decomp='pokeruby'):
    """OBJ_EVENT_GFX_* of things that are not people or Pokemon (Gen 3's anim tables Inanimate, BerryTree, CuttableTree,
    BreakableRock: rocks, Cut trees, boulders, item balls, fossils, dolls ...): their movement type turns nothing, so npc() leaves them to the
    writer (a look-around code would turn a Black 2 sheet that has only one usable frame)."""
    if decomp not in _STATIC:
        import os, re
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'external', decomp)
        info = open(os.path.join(root, 'src', 'data', 'object_events', 'object_event_graphics_info.h')).read()
        still = set(re.findall(r'gObjectEventGraphicsInfo_(\w+) = \{[^}]*?\.anims = gObjectEventImageAnimTable_'
                               r'(?:Inanimate|BerryTree|CuttableTree|BreakableRock)\b', info, re.S))
        ptrs = open(os.path.join(root, 'src', 'data', 'object_events', 'object_event_graphics_info_pointers.h')).read()
        table = re.search(r'gObjectEventGraphicsInfoPointers\[[^\]]*\] = \{(.*?)\};', ptrs, re.S).group(1)
        order = re.findall(r'&gObjectEventGraphicsInfo_(\w+)', table)
        consts = {int(v, 0): k for k, v in re.findall(r'#define (OBJ_EVENT_GFX_\w+)\s+(\d+|0x[0-9A-Fa-f]+)\b',
                  open(os.path.join(root, 'include', 'constants', 'event_objects.h')).read())}
        _STATIC[decomp] = {consts[i] for i, name in enumerate(order) if name in still and i in consts}
    return _STATIC[decomp]


def npc(movement, rng=(0, 0), gfx=None):
    """dict(move, dir?, areaw, areah, evtype?, note) of any Gen 3 movement type; None when Black 2 has no code for it
    (INVISIBLE: keep what the writer chose) or the type is unknown."""
    if gfx is not None and gfx in static_graphics(): return None
    w = walk(movement, rng)
    m = str(movement).replace('MOVEMENT_TYPE_', '')
    if w: return dict(w, note='walk route / back and forth (move_codes.walk)')
    if m not in TABLE or TABLE[m][0] is None: return None
    code, d, area, ev, note = TABLE[m]
    rx, ry = (int(v) for v in rng)
    if area and code in (3, 4, 5):           # Gen 3: a range of 0 is no limit on that axis (Emerald's Battle Frontier
        if code in (3, 5) and rx == 0: rx = NO_LIMIT     # lounge / corridor people); Black 2: 0xFFFF (-1) is no limit
        if code in (3, 4) and ry == 0: ry = NO_LIMIT
    out = dict(move=code, areaw=rx if area else 0, areah=ry if area else 0, note=note)
    if d is not None: out['dir'] = d
    if ev is not None: out['evtype'] = ev
    return out


def room_npc(o):
    """The keys a room generator writes for a Sapphire object (data/interiors/<zone>.json, b2tools/patches/interiors.py):
    'move' (+ 'range' [areaW, areaH], 'dir') when it does more than stand facing one way (that stays code 0 + dir)."""
    m = npc(o['movement_type'], (o.get('movement_range_x', 0), o.get('movement_range_y', 0)), o.get('graphics_id'))
    if m is None or m['move'] == 0 or 14 <= m['move'] <= 17: return {}
    out = {'move': m['move']}
    if m['areaw'] or m['areah']: out['range'] = [m['areaw'], m['areah']]
    if 'dir' in m: out['dir'] = m['dir']
    if 'evtype' in m: out['evtype'] = m['evtype']
    return out


def expected(movement):
    """Short text of the mapping (move_audit.py)."""
    r = npc(movement, (1, 1))
    return '-' if r is None else str(r['move']) + (' +area' if r['areaw'] or r['areah'] else '') + (f" ev{r['evtype']}" if 'evtype' in r else '')


def walk(movement, rng):
    """Black 2 move code, first direction and walk area of a Sapphire walker (MOVEMENT_TYPE_WALK_SEQUENCE_* or
    MOVEMENT_TYPE_WALK_*_AND_*) with Sapphire's movement range (x, y); None for any other movement type."""
    m = str(movement).replace('MOVEMENT_TYPE_', '')
    rx, ry = (int(v) for v in rng)
    if m.startswith('WALK_SEQUENCE_') and m[14:] in LOOP:
        code = LOOP[m[14:]]
        first = 'UP' if code == LOOP['UP_RIGHT_LEFT_DOWN'] else m[14:].split('_')[0]
        return dict(move=code, dir=DIR[first], areaw=rx, areah=ry)
    if m.startswith('WALK_') and m[5:] in BACK_AND_FORTH:
        return dict(move=20, dir=DIR[BACK_AND_FORTH[m[5:]]], areaw=rx, areah=ry)
    return None
