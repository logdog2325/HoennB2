"""Write every 'auto' Hoenn interior (data/hoenn_interiors.json, converter/allocate_interiors.py) for the interiors
patch, and re-point Black 2's own Pokémon Center rooms ('b2') at the Hoenn towns.

    python3 gen_interiors.py      (after allocate_interiors.py and b2tools/world.py: needs world.json's doors)

Per 'auto' room (zone Z, scripts S, text T):
  data/interiors/Z.json             room, one warp per Sapphire warp event in Sapphire's order on its own tile (a door
                                    names Sapphire's dest_warp_id), simple people and signs with their Sapphire lines,
                                    item balls (global scripts, converter/gen_items.py); "auto": true
  src/field_scripts/SSSS_room_<Map>.s, src/text/script/TTTT_room_<Map>.txt
  data/interior_layouts/<Map>.json  only if missing: a placeholder recipe (style by tileset, floor = the walkable
                                    area's box plus the furniture row along the back wall); furniture comes from the
                                    per-tileset work (notes/INTERIORS_PLAN.md) — a recipe without "_auto" is kept as is
A json without "auto" (made by hand) is never overwritten. Exits point at the outdoor zone's door warp: the zone's own
Black 2 warp slots come first (hoenn_world.py keeps them), then world.json's "doors" in order.
Skipped people: trainers, hide-flag (story) objects, scripts other than one message, sprites without a Black 2 match.
"""
import os, sys, json, glob, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'b2tools')); sys.path.insert(0, os.path.join(ROOT, 'b2tools', 'patches'))
import move_codes as MOVE_CODES                       # noqa: E402  (v165_fixes)
from gen3text import convert
from gen_map_content import ruby_scripts, simple_message
import narcio, zoneheaders
from zones import parse_entities

RUBY = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps')
FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
STYLE = {'gTileset_Lab': 'lab'}            # everything else starts as 'house' (data/interior_layouts/_styles.json)
AREA = {'house': 284, 'lab': 285}          # interior areas of Littleroot's rooms (packs 2 and 3); rooms share them

def placeholder_recipe(name, size):
    """Floor = box of the walkable tiles, one row higher (the furniture row along the back wall)."""
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    from models_interior import sapphire_map
    walk = sapphire_map(name)['walk']
    tiles = [(x, y) for y, row in enumerate(walk) for x, ok in enumerate(row) if ok]
    x0, x1 = min(t[0] for t in tiles), max(t[0] for t in tiles)
    y0, y1 = min(t[1] for t in tiles), max(t[1] for t in tiles)
    return [x0, max(0, y0 - 1), x1, y1]

def sign_block(i, msg):
    return f"""Script_{i}:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg {msg}, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def npc_block(i, msg):
    return f"""Script_{i}:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, {msg}, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def main():
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    world = json.load(open(os.path.join(os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'), 'world.json')))
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    headers, _ = zoneheaders.load(FILES)
    ents = narcio.load(FILES, 126)
    # outdoor door warps: (map, sapphire warp id) -> (zone, Black 2 warp index)
    door = {}
    for zid, z in world['zones'].items():
        base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
        for k, d in enumerate(z.get('doors', [])):          # a door in another zone's cell: its copy there wins
            if d.get('foreign') or (d['map'], d['id']) not in door: door[(d['map'], d['id'])] = (int(zid), base + k)
        for d in z.get('slot_doors', []):             # hand-made towns' own door slots (Oldale)
            door[(d['map'], d['id'])] = (int(zid), d['slot'])
    by_name = rooms
    text, scripts = ruby_scripts()
    sprites = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
    balls = json.load(open(os.path.join(ROOT, 'data', 'hoenn_items.json')))['balls']
    out_s, out_t = os.path.join(ROOT, 'src', 'field_scripts'), os.path.join(ROOT, 'src', 'text', 'script')
    def owned(r):                     # a room whose json lost "auto" belongs to whoever made it: never touched here
        p = os.path.join(ROOT, 'data', 'interiors', f'{r["zone"]}.json')
        return os.path.exists(p) and not json.load(open(p)).get('auto')
    for name, r in rooms.items():     # regenerated rooms' old files go (a renamed room leaves none behind)
        if r['status'] == 'auto' and not owned(r):
            for f in glob.glob(os.path.join(out_s, f'{r["scripts"]:04d}_room_*.s')) + glob.glob(os.path.join(out_t, f'{r["text"]:04d}_room_*.txt')):
                os.remove(f)
    report = collections.Counter(); unresolved = []
    parent = {}                       # room -> outdoor zone it belongs to (its door's zone, or that of a linked room)
    for _ in range(4):
        for name, r in rooms.items():
            for w in r['warps']:
                if w['dest'] in zones and (w['dest'], w['dest_warp']) in door: parent.setdefault(name, door[(w['dest'], w['dest_warp'])][0])
                elif w['dest'] in parent: parent.setdefault(name, parent[w['dest']])
    for name, r in sorted(rooms.items()):
        zone = r['zone']; jpath = os.path.join(ROOT, 'data', 'interiors', f'{zone}.json')
        if os.path.exists(jpath) and not json.load(open(jpath)).get('auto'): report['hand-made json kept'] += 1; continue
        if r['status'] == 'b2':             # Black 2's own Center: keep its room and people, re-point its exit mat
            e, _ = parse_entities(ents[headers[zone]['entities']])
            ext = next(((d['map'], d['id']) for d in [dict(map=w['dest'], id=w['dest_warp']) for w in r['warps']]
                        if (d['map'], d['id']) in door), None)
            warps = []
            for w in e['warps']:
                w = {k: v for k, v in w.items() if k not in ('tile_x', 'tile_z')}
                if w['type'] == 1 and ext:
                    w['dest_zone'], w['dest_warp'] = door[ext]
                warps.append(dict(x=w['x'] // 16, z=w['z'] // 16, w=w['w'], h=w['h'], type=w['type'], dir=w['dir'],
                                  to=[w['dest_zone'], w['dest_warp']]))
            json.dump(dict(zone=zone, auto=True, what=f'{name}: Black 2 Pokémon Center room, exit re-pointed',
                           warps=warps), open(jpath, 'w'), indent=1)
            report['b2 center re-pointed'] += 1; continue
        if r['status'] != 'auto': report[r['status']] += 1; continue
        j = json.load(open(os.path.join(RUBY, name, 'map.json')))
        # warps, in Sapphire's order
        warps = []
        for i, w in enumerate(r['warps']):
            dest = w['dest']; dw = w['dest_warp']
            if dest == 'MAP_DYNAMIC': to = (zone, 256)   # Black 2's dynamic warp: dest id 0x100 = GameData's next zone
            elif dest in zones: to = door.get((dest, dw))  # (ov035 EventMapChangeWarp_CreateFromEntity; b2tools/check_exits.py)
            elif dest in rooms and rooms[dest]['status'] in ('auto', 'center'): to = (rooms[dest]['zone'], dw)
            elif dest in rooms and rooms[dest]['status'] == 'b2': to = (rooms[dest]['zone'], 0)
            else: to = None
            if to is None: unresolved.append(f'{name} warp {i} -> {dest} {dw}'); to = (zone, 0)
            warps.append(dict(at=[w['x'], w['y']], tile_only=True, to=list(to), what=f'Sapphire warp {i} -> {dest} {dw}'))
        # people and signs with one message
        msgs, blocks, npcs, signs = [], [], [], []
        for lid, o in enumerate(j.get('object_events', []), 1):
            if o['graphics_id'] == 'OBJ_EVENT_GFX_ITEM_BALL':
                b = balls.get(o['script'])
                if b: npcs.append(dict(uid=lid, model=110, script=b['script'], flag=b['flag'], dir=1, at=[o['x'], o['y']]))
                else: report['item ball without a Black 2 item'] += 1
                continue
            if o.get('trainer_type', 'TRAINER_TYPE_NONE') not in ('TRAINER_TYPE_NONE', '0', 0): report['trainer'] += 1; continue
            if str(o.get('flag', '0')) not in ('0', ''): report['story person (hide flag)'] += 1; continue
            code = (sprites.get(o['graphics_id']) or {}).get('code')
            label = simple_message(o['script'], text, scripts) if code else None
            if not label or convert(text[label])[1]: report['person: story/complex script or no sprite'] += 1; continue
            msgs.append(convert(text[label])[0]); blocks.append(npc_block(len(blocks) + 1, len(msgs) - 1))
            face = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2,
                    'MOVEMENT_TYPE_FACE_RIGHT': 3}.get(o['movement_type'], 1)
            n = dict(uid=lid, model=code, script=len(blocks), dir=face, at=[o['x'], o['y']])
            n.update(MOVE_CODES.room_npc(o))     # Sapphire's movement type as Black 2's code (b2tools/move_codes.py)
            npcs.append(n); report['person'] += 1
        for b in j.get('bg_events', []):
            if b.get('type') != 'sign' or not b.get('script'): continue
            label = simple_message(b['script'], text, scripts)
            if not label or convert(text[label])[1]: report['sign: story/complex script'] += 1; continue
            msgs.append(convert(text[label])[0]); blocks.append(sign_block(len(blocks) + 1, len(msgs) - 1))
            facing = b.get('player_facing_dir', 'BG_EVENT_PLAYER_FACING_ANY')
            signs.append(dict(script=len(blocks), at=[b['x'], b['y']], dir=0 if facing.endswith('NORTH') else 4))
            report['sign'] += 1
        entries = '\n'.join(f'    ScriptEntry Script_{i}' for i in range(1, len(blocks) + 1))
        src = (f'// {name} (zone {zone}): generated by converter/gen_interiors.py from Sapphire\'s simple people and '
               f'signs.\n// Messages: src/text/script/{r["text"]:04d}_room_{name}.txt\n#include "asm/field_script.inc"\n\n'
               + (entries + '\n' if blocks else '    ScriptEntry Script_None\n') + '    ScriptEntriesEnd\n\n'
               + '\n'.join(blocks) + ('' if blocks else 'Script_None:\n    VMHalt\n') + '    .balign 4, 0\n')
        from story_merge import write_room_script, write_room_text  # a story agent's part (after "// ---- story") stays
        sp = os.path.join(out_s, f'{r["scripts"]:04d}_room_{name}.s')
        write_room_text(os.path.join(out_t, f'{r["text"]:04d}_room_{name}.txt'), msgs or ['…'], sp)
        write_room_script(sp, src)
        style = STYLE.get(r['tilesets'][1], 'house')
        files = {k: r[k] for k in ('scripts', 'init_scripts', 'text')} if r.get('own_files') else {}
        json.dump(dict(zone=zone, room=name, auto=True, area=AREA[style], parent=parent.get(name, 389), warps=warps,
                       npcs=npcs, signs=signs, **files),
                  open(jpath, 'w'), indent=1, ensure_ascii=False)
        lpath = os.path.join(ROOT, 'data', 'interior_layouts', f'{name}.json')
        if not os.path.exists(lpath) or json.load(open(lpath)).get('_auto'):
            json.dump(dict(_auto=True, _doc='Placeholder from converter/gen_interiors.py: floor only, no furniture yet.',
                           map=name, style=style, floor=[placeholder_recipe(name, r['size'])]),
                      open(lpath, 'w'), indent=1)
        report['auto room'] += 1
    print(dict(report))
    if unresolved: print(f'{len(unresolved)} warps to rooms not built yet (point at the room\'s own warp 0):', *unresolved[:12], sep='\n  ')

if __name__ == '__main__':
    main()
