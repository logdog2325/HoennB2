"""Sapphire's trainer objects as Black 2 eye-contact trainer NPCs (notes/STORY_PORTING.md "Trainers").

    python3 gen_trainer_npcs.py        (after gen_trainers.py; reads work/world/world.json or $HOENN_WORLD_DIR, read only)

A Black 2 trainer NPC is a zone NPC with evType 1, param0 = sight range and script 3000 + trainer id (the second NPC
of a double pair: 5000 + id); Black 2's global trainer scripts (file 1239) run the eye contact, the intro, the battle,
the defeat flag (id + 1520) and the line after the battle, so a plain Sapphire trainer needs no zone script at all
(checked: every trainer NPC of Black 2's zone entities looks like this, e.g. zone 29 uid 1 = script 3734, evType 1,
param0 5). Sapphire's movement types map to Black 2 move codes read from ov036's ACTOR_MOVE_CODE_FUNCTION_TABLES
(0x021cc990) and its look-around direction tables (0x021cbc70): 2 look in all directions, 6 up/left, 7 up/right,
8 down/left, 9 down/right, 10 up/down/left, 11 up/down/right, 12 up/left/right, 13 down/left/right, 45 up/down,
46 left/right, 14-17 face up/down/left/right (also global script 1239 L_0FFA), 3 wander, 18/19 spin, 20 walk back
and forth, 21-44 walk a route (b2tools/move_codes.py; with Sapphire's movement range as the walk area areaw/areah).

Writes data/hoenn_trainer_npcs.json: the NPCs b2tools/patches/trainers.py appends to each zone's NPC list (after the
zone's own NPCs, so no existing NPC index moves), and the lists of trainers it did NOT place, for the chapter agents:
  story     the object's script does more than battle + one line, or the object has a hide flag (story trainers:
            rival, Wally, Aqua, gym leaders, gym trainers with gimmicks...): the chapter agent writes the scene and
            places the NPC (data already converted: data/hoenn_trainer_data.json)
  owned     the room belongs to an agent (data/interiors/<zone>.json without "auto"): its owner adds the NPC
  unbuilt   the map is not built yet (caves, standalone maps)
  no_sprite the Sapphire graphics id has no Black 2 sprite (data/sprite_map.json)
Outdoor NPC uids: 100 + Sapphire local id (bumped past any clash); room NPC uids: the Sapphire local id (as
converter/gen_interiors.py numbers people).

Emerald (HOENN_VERSION=emerald; S0-3, emerald_s0 2026-10-12, notes/EMERALD_STORY.md 2.4): the same run with Emerald's
trainers (data/emerald/hoenn_trainer_data.json, the entries under their Emerald name: emerald_data's registry and
pokeemerald's objects), pokeemerald's movement ranges, Emerald's zones, rooms and world (version.load_json /
version.world_dir), data/emerald/sprite_map.json over Sapphire's rows (+ "_gfx_alias"); writes
data/emerald/hoenn_trainer_npcs.json, whose lists replace Sapphire's in patches/trainers.py (version.load_json: a list is
replaced, not merged). It stops while Emerald's world is not built.
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import move_codes as MOVE_CODES                               # noqa: E402
import version                                                # noqa: E402
EM = version.is_emerald()
OUT = os.path.join(os.environ.get('HOENN_GEN_OUT') or ROOT, 'data', *(['emerald'] if EM else []), 'hoenn_trainer_npcs.json')

MOVE = {   # Sapphire movement type -> (Black 2 move code, initial direction 0 up 1 down 2 left 3 right)
    'FACE_UP': (14, 0), 'FACE_DOWN': (15, 1), 'FACE_LEFT': (16, 2), 'FACE_RIGHT': (17, 3),
    'LOOK_AROUND': (2, 1), 'FACE_UP_AND_LEFT': (6, 0), 'FACE_UP_AND_RIGHT': (7, 0), 'FACE_DOWN_AND_LEFT': (8, 1),
    'FACE_DOWN_AND_RIGHT': (9, 1), 'FACE_DOWN_UP_AND_LEFT': (10, 1), 'FACE_DOWN_UP_AND_RIGHT': (11, 1),
    'FACE_UP_LEFT_AND_RIGHT': (12, 0), 'FACE_DOWN_LEFT_AND_RIGHT': (13, 1), 'FACE_DOWN_AND_UP': (45, 1),
    'FACE_LEFT_AND_RIGHT': (46, 2), 'ROTATE_COUNTERCLOCKWISE': (18, 1), 'ROTATE_CLOCKWISE': (19, 1),
    'WANDER_AROUND': (3, 1), 'WANDER_UP_AND_DOWN': (4, 1), 'WANDER_LEFT_AND_RIGHT': (5, 2),
}
# Sapphire's walkers (WALK_SEQUENCE_*, WALK_*_AND_*): Black 2's walk-route codes 21-44 and back-and-forth code 20 with
# Sapphire's movement range as the walk area (b2tools/move_codes.py; v165_fixes 2026-10-11, before: look around / face)

# trainers a chapter agent places (data/story): hidden ones (Black 2's jump-out codes 53/54 need a story entry with
# evType) and the copy-the-player ones (Route 119)
STORY_TYPES = ('TREE_DISGUISE', 'MOUNTAIN_DISGUISE', 'HIDDEN', 'BURIED')

def move_of(movement, rng=(0, 0)):
    """((Black 2 move code, direction), approximated?, (walk area w, h)) from b2tools/move_codes.py's table."""
    m = movement.replace('MOVEMENT_TYPE_', '')
    if m in STORY_TYPES or m.startswith('COPY_PLAYER'): return None, True, (0, 0)
    r = MOVE_CODES.npc(movement, rng)
    if r is None: return None, True, (0, 0)
    return (r['move'], r.get('dir', MOVE.get(m, (0, 1))[1])), 'approximated' in r['note'], (r['areaw'], r['areah'])

_ranges = {}
def sapphire_range(mapname, local_id):
    """(movement_range_x, movement_range_y) of a Sapphire object (pokeruby data/maps/<map>/map.json)."""
    if mapname not in _ranges:          # (Emerald: pokeemerald's map, mapname = the object's emerald_map)
        j = json.load(open(os.path.join(version.decomp() if EM else os.path.join(ROOT, 'external', 'pokeruby'), 'data', 'maps',
                                        mapname, 'map.json')))
        _ranges[mapname] = [(int(o.get('movement_range_x', 0)), int(o.get('movement_range_y', 0)))
                            for o in j.get('object_events') or []]
    return _ranges[mapname][local_id - 1]

def main():
    import world as W
    wdir = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    if EM:
        wdir = version.world_dir()
        if not os.path.exists(os.path.join(wdir, 'world.json')):
            raise SystemExit(f'Emerald mode reads Emerald\'s world ({wdir}/world.json): not built yet (emerald_world, EMERALD-2)')
        data = {k: v for k, v in json.load(open(os.path.join(os.environ.get('HOENN_GEN_OUT') or ROOT, 'data', 'emerald',
                'hoenn_trainer_data.json')))['trainers'].items() if v.get('emerald_trainer') == k}   # each trainer once
        sprites = version.load_json(os.path.join(ROOT, 'data', 'sprite_map.json'))
        zones = version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps']
        rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    else:
        data = json.load(open(os.path.join(os.environ.get('HOENN_GEN_OUT') or ROOT, 'data', 'hoenn_trainer_data.json')))['trainers']
        sprites = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
        zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
        rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    alias = sprites.get('_gfx_alias', {}) if EM else {}
    wj = json.load(open(os.path.join(wdir, 'world.json')))
    owner = {(c['cx'], c['cz']): c['zone'] for c in wj['cells']}
    cfg, lay = W.load()
    _, _, maps = W.compose(cfg, lay)
    frame = {n: (maps, owner) for n in maps}                     # main matrix; then each warp-only map's own
    for _, _, fm, fo in W.standalone_frames(cfg):                 # matrix (world.py standalone groups), as
        for n in fm: frame.setdefault(n, (fm, fo))                # gen_map_content does
    outdoor, inrooms = [], []
    lists = collections.defaultdict(list)
    approx = []
    used_uid = collections.defaultdict(set)
    if EM:    # (emerald_integrate 2026-10-12) the story objects' uids stay theirs: patches/story.py adds them after these NPCs
        # and stops on a uid already in the zone. In Sapphire both come from one object list; Emerald's objects are numbered
        # otherwise (data/story/ch4.json Route 111's Claw Fossil 135 = 100 + Sapphire's object 35 = Emerald's Tyron, 35)
        sfx = '_emerald'
        for p in version.overlay(os.path.join(ROOT, 'data', 'story'), '*.json'):
            for o in json.load(open(p)).get('objects', []):
                o = dict(o, **{k[:-len(sfx)]: v for k, v in o.items() if k.endswith(sfx) and len(k) > len(sfx)})
                if o.get('skip') or 'uid' not in o or o.get('kind', 'npc') != 'npc': continue
                if 'zone' in o: used_uid[o['zone']].add(o['uid']); continue
                if o.get('map') in frame and 'at' in o:
                    fmaps, fowner = frame[o['map']]; mp = fmaps[o['map']]
                    used_uid[W.zone_of(fowner, mp['ox'] + o['at'][0], mp['oz'] + o['at'][1],
                                       wj.get('zone_rects', []) if fowner is owner else ())].add(o['uid'])
    for t, d in sorted(data.items(), key=lambda kv: kv[1]['b2_id']):
        for o in d['objects']:
            what = f"{t} ({d['name']}) {o['map']} #{o['local_id']}"
            if not o['simple']:
                lists['story'].append(what + f" script {o['script']}" + (f" flag {o['flag']}" if str(o['flag']) not in ('0', '') else '')); continue
            code = (sprites.get(o['gfx']) or sprites.get(alias.get(o['gfx'], '')) or {}).get('code')
            if not code: lists['no_sprite'].append(what + f" {o['gfx']}"); continue
            mv, rough, area = move_of(o['movement'], sapphire_range(o.get('emerald_map', o['map']) if EM else o['map'], o['local_id']))
            if mv is None: lists['story'].append(what + f" movement {o['movement']}"); continue
            if rough: approx.append(f"{what}: {o['movement']} -> code {mv[0]}")
            npc = dict(trainer=t, model=code, move=mv[0], dir=mv[1], evtype=1, p0=o['sight'], p1=0, p2=0,
                       script=o['npc_script'], flag=0, sapphire=[o['map'], o['local_id'], o['x'], o['y']])
            if any(area): npc.update(areaw=area[0], areah=area[1])     # (a walker's walk area: trainers.py)
            if o['map'] in zones and o['map'] in frame:
                fmaps, fowner = frame[o['map']]
                mp = fmaps[o['map']]; wx, wz = mp['ox'] + o['x'], mp['oz'] + o['y']
                zone = W.zone_of(fowner, wx, wz, wj.get('zone_rects', []) if fowner is owner else ())   # (sub-cell zones)
                if zone is None: lists['unbuilt'].append(what + ' (no cell)'); continue
                uid = 100 + o['local_id']
                while uid in used_uid[zone]: uid += 1
                used_uid[zone].add(uid)
                outdoor.append(dict(npc, zone=zone, uid=uid, x=wx, z=wz))
            elif o['map'] in rooms:
                r = rooms[o['map']]
                jp = os.path.join(ROOT, 'data', 'interiors', f"{r['zone']}.json")
                if EM: jp = version.overlay_file(jp)                  # (Emerald's own room file, data/interiors/emerald/)
                if r['status'] in ('cave', 'link') or not os.path.exists(jp):
                    lists['unbuilt'].append(what + f" (room status {r['status']})"); continue
                if not json.load(open(jp)).get('auto'):
                    lists['owned'].append(what + f" (zone {r['zone']}, {r['status']}, data/interiors/{r['zone']}.json)"); continue
                inrooms.append(dict(npc, zone=r['zone'], room=o['map'], uid=o['local_id'], at=[o['x'], o['y']]))
            else:
                lists['unbuilt'].append(what)
    out = {'_doc': 'Generated by converter/gen_trainer_npcs.py: trainer NPCs b2tools/patches/trainers.py appends to '
                   'zones (outdoor: zone tiles; rooms: Sapphire tile "at" + the room origin), and the trainers left to '
                   'the chapter agents.',
           'outdoor': outdoor, 'rooms': inrooms, 'approximated_movement': approx,
           'not_placed': {k: v for k, v in sorted(lists.items())}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f"{len(outdoor)} outdoor + {len(inrooms)} room trainer NPCs in {len({n['zone'] for n in outdoor + inrooms})} zones; "
          f"not placed: { {k: len(v) for k, v in lists.items()} }; approximated movement: {len(approx)}")

if __name__ == '__main__':
    main()
