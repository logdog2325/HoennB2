"""Shops agent: zone json, script and text files of the gTileset_Shop rooms (notes/INTERIORS_PLAN.md), with working
shop clerks.

    python3 shops_rooms.py [MAP ...]          (default: every room of the family)

Writes (owned by the shops agent from now on; converter/gen_interiors.py leaves a json without "auto" alone):
  data/interiors/<zone>.json                       room, area, warps (Sapphire order, one per warp tile), people, signs
  src/field_scripts/<scripts>_room_<Map>.s         people: ParentActorMsg; signs: SystemMsg; clerks: Black 2's shop
  src/text/script/<text>_room_<Map>.txt            Sapphire's lines (converter/gen3text.py)

Clerks: Black 2's Pokémon Center clerk pattern (its scripts 0796.s etc.): 0x8000 = shop id, 0x8001 = greeting
(1 "Welcome! May I help you?", 2 the TM department), RTCallGlobal 10110 (Buy / Sell / Quit). Shop ids and lists:
b2tools/shops_data.py -> data/hoenn_shops.json, installed by the build patch `shops`. Sapphire marts that switch to a
bigger list after a story flag do so here behind #ifdef: the flag's name is Sapphire's, and the branch assembles in as
soon as src/include/hoenn.h defines it (until then the clerk sells the starting list, as Sapphire does before the
flag).
People: Sapphire's people whose script is one message (as gen_interiors), plus the clerks; story people (flags,
gifts, Pokémon cries, lottery, decorations) are left for the story phase and listed by `python3 shops_rooms.py --todo`.
"""
import os, sys, json, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches')); sys.path.insert(0, os.path.join(ROOT, 'converter'))
import move_codes as MOVE_CODES                       # noqa: E402  (v165_fixes)
from gen3text import convert                                   # noqa: E402
from gen_map_content import ruby_scripts, simple_message       # noqa: E402
from shops_data import ID_FOR                                   # noqa: E402

RUBY = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps')
FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
AREA = 326          # Shopping Mall Nine's interior area (pack 44, texture set 326): the shop rooms' own area

ROOMS = ['FallarborTown_Mart', 'FortreeCity_Mart', 'LavaridgeTown_HerbShop', 'LavaridgeTown_Mart',
         'LilycoveCity_DepartmentStoreRooftop', 'LilycoveCity_DepartmentStore_1F', 'LilycoveCity_DepartmentStore_2F',
         'LilycoveCity_DepartmentStore_3F', 'LilycoveCity_DepartmentStore_4F', 'LilycoveCity_DepartmentStore_5F',
         'MauvilleCity_Mart', 'MossdeepCity_Mart', 'OldaleTown_Mart', 'PetalburgCity_Mart',
         'Route110_SeasideCyclingRoadNorthEntrance', 'Route110_SeasideCyclingRoadSouthEntrance',
         'Route121_SafariZoneEntrance', 'RustboroCity_Mart', 'SlateportCity_Mart', 'SootopolisCity_Mart',
         'VerdanturfTown_Mart']

# Sapphire marts whose clerk switches lists on a story flag: label of the list sold once the flag is set
EXPANDED = {'OldaleTown_Mart_Pokemart_Expanded': 'FLAG_ADVENTURE_STARTED',
            'PetalburgCity_Mart_Pokemart_Expanded': 'FLAG_PETALBURG_MART_EXPANDED_ITEMS',
            'RustboroCity_Mart_Pokemart_Expanded': 'FLAG_MET_DEVON_EMPLOYEE'}
TM_SHOPS = {'LilycoveCity_DepartmentStore_4F_Pokemart_AttackTMs', 'LilycoveCity_DepartmentStore_4F_Pokemart_DefenseTMs'}
# hand-made outdoor zones: (Sapphire map, Sapphire warp id) -> (zone, Black 2 warp slot) (b2tools/patches/hoenn_world.py
# keeps their Black 2 warp slots: Oldale = Accumula's slots, slot 1 = Accumula's Mart-side house, moved to Oldale's
# Mart door at Sapphire (14,6))
HAND_DOORS = {('OldaleTown', 3): (397, 1)}
PARENT = {'OldaleTown_Mart': 397}


def door_map():
    """(outdoor map, Sapphire warp id) -> (zone, warp index), as converter/gen_interiors.py builds it."""
    import narcio, zoneheaders
    from zones import parse_entities
    world = json.load(open(os.path.join(ROOT, 'work', 'world', 'world.json')))
    headers, _ = zoneheaders.load(FILES)
    ents = narcio.load(FILES, 126)
    door = dict(HAND_DOORS)
    for zid, z in world['zones'].items():
        base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
        for k, d in enumerate(z.get('doors', [])):
            door[(d['map'], d['id'])] = (int(zid), base + k)
    return door


def sign_block(i, msg, what):
    return f"""Script_{i}:                                      // {what}
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


def npc_block(i, msg, what):
    return f"""Script_{i}:                                      // {what}
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


def clerk_block(i, labels, what, greet_msg=None):
    """Shop clerk: Black 2's Center clerk pattern with Sapphire's list(s)."""
    base = [l for l in labels if l not in EXPANDED]
    exp = [l for l in labels if l in EXPANDED]
    sid = ID_FOR[(base or exp)[0]]
    greet = 2 if set(labels) & TM_SHOPS else 1
    s = [f'Script_{i}:                                      // {what}',
         '    ActorsPauseAll', '    SEPlay SEQ_SE_MESSAGE', '    ActorSetEyeToEye']
    if greet_msg is not None:            # the shop's own Sapphire greeting first (Herb Shop)
        s += [f'    ParentActorMsg MSGFILE_SCRIPT, {greet_msg}, 0, 0', '    LastKeyWait', '    ActorMsgClose']
    s += ['    VMStackPush 0x8000', '    VMStackPush 0x8001', f'    WorkSet 0x8000, {sid}' + ' ' * 18 + f'// {(base or exp)[0]}']
    if base and exp:
        flag = EXPANDED[exp[0]]
        s += [f'#ifdef {flag}                   // Sapphire: the bigger list once {flag} is set',
              f'    VMStackPushFlag {flag}', '    VMStackPushConst 1',
              '    VMStackCmp CMP_NE                   // (Ch1: CMP_STACK jumps when the compare is false: NE = flag set)',
              f'    VMJumpIf CMP_STACK, L_Shop{i}_Expanded', f'    VMJump L_Shop{i}_Open',
              f'L_Shop{i}_Expanded:', f'    WorkSet 0x8000, {ID_FOR[exp[0]]}' + ' ' * 17 + f'// {exp[0]}',
              f'L_Shop{i}_Open:', '#endif']
    s += [f'    WorkSet 0x8001, {greet}', '    RTCallGlobal 10110', '    VMStackPop 0x8001', '    VMStackPop 0x8000',
          '    FinishAllEvents', '    ActorsUnpauseAll', '    VMHalt', '']
    return '\n'.join(s)


def pokemart_labels(script, scripts):
    """Every pokemart list a Sapphire script (and the labels it jumps to) opens."""
    out, seen, todo = [], set(), [script]
    while todo:
        lab = todo.pop(0)
        if lab in seen: continue
        seen.add(lab)
        for line in scripts.get(lab, []):
            w = line.replace(',', ' ').split()
            if not w: continue
            if w[0] == 'pokemart' and w[1] not in out: out.append(w[1])
            if w[0] in ('goto', 'goto_if_set', 'goto_if_unset', 'call', 'call_if_set', 'call_if_unset', 'goto_if_eq'):
                todo.append(w[-1])
    return out


def conv(t):
    """converter/gen3text.convert, plus Sapphire's {POKEBLOCK} code spelled out (Pokéblocks are a Safari Zone item
    in Sapphire; the sign's words stay Sapphire's)."""
    return convert(t.replace('{POKEBLOCK}S', 'Pokéblocks').replace('{POKEBLOCK}', 'Pokéblock'))


def build(name, rooms, door, text, scripts, sprites, todo):
    r = rooms[name]; zone = r['zone']
    j = json.load(open(os.path.join(RUBY, name, 'map.json')))
    warps = []
    for i, w in enumerate(r['warps']):
        dest, dw = w['dest'], w['dest_warp']
        if (dest, dw) in door: to = door[(dest, dw)]
        elif dest in rooms and rooms[dest]['status'] in ('auto', 'hand'): to = (rooms[dest]['zone'], dw)
        else:
            to = (zone, 0); todo.append(f'{name}: warp {i} -> {dest} {dw} has no Black 2 destination yet (points at the room\'s own warp 0)')
        warps.append(dict(at=[w['x'], w['y']], tile_only=True, to=list(to), what=f'Sapphire warp {i} -> {dest} {dw}'))
    msgs, blocks, npcs, signs = [], [], [], []
    def msg(s):
        msgs.append(s); return len(msgs) - 1
    for lid, o in enumerate(j.get('object_events', []), 1):
        code = (sprites.get(o['graphics_id']) or {}).get('code')
        face = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2,
                'MOVEMENT_TYPE_FACE_RIGHT': 3}.get(o['movement_type'], 1)
        who = f"{o['graphics_id'][14:].lower()} ({o['x']},{o['y']}), Sapphire {o['script']}"
        marts = pokemart_labels(o['script'], scripts)
        if marts and all(m in ID_FOR for m in marts) and code is not None:
            greet = None
            first = [l for l in scripts.get(o['script'], []) if l.startswith('message ')]
            if first and 'Text_HowMayIServeYou' not in first[0]:
                lab = first[0].split()[1]
                line, unk = conv(text[lab])
                if not unk: greet = msg(line)
            blocks.append(clerk_block(len(blocks) + 1, marts, 'clerk ' + who, greet))
            npcs.append(dict(uid=lid, model=code, script=len(blocks), dir=face, at=[o['x'], o['y']], _what='clerk ' + who))
            continue
        if str(o.get('flag', '0')) not in ('0', ''):
            todo.append(f'{name}: {who}: story person (hide flag {o["flag"]})'); continue
        if o.get('trainer_type', 'TRAINER_TYPE_NONE') not in ('TRAINER_TYPE_NONE', '0', 0):
            todo.append(f'{name}: {who}: trainer'); continue
        label = simple_message(o['script'], text, scripts) if code is not None else None
        if not label or conv(text[label])[1]:
            why = 'decoration shop (Black 2 has no Secret Base decorations)' if any(
                l.startswith('pokemartdecoration') for l in scripts.get(o['script'], [])) else \
                'no Black 2 sprite' if code is None else 'story / multi-step script'
            todo.append(f'{name}: {who}: {why}'); continue
        blocks.append(npc_block(len(blocks) + 1, msg(conv(text[label])[0]), who))
        n = dict(uid=lid, model=code, script=len(blocks), dir=face, at=[o['x'], o['y']], _what=who)
        n.update(MOVE_CODES.room_npc(o))     # Sapphire's movement type as Black 2's code (b2tools/move_codes.py)
        npcs.append(n)
    for b in j.get('bg_events', []):
        if b.get('type') != 'sign' or not b.get('script'): continue
        who = f"sign ({b['x']},{b['y']}), Sapphire {b['script']}"
        label = simple_message(b['script'], text, scripts)
        if not label or conv(text[label])[1]:
            todo.append(f'{name}: {who}: not a one-message sign'); continue
        blocks.append(sign_block(len(blocks) + 1, msg(conv(text[label])[0]), who))
        facing = b.get('player_facing_dir', 'BG_EVENT_PLAYER_FACING_ANY')
        at, d = [b['x'], b['y']], 0 if facing.endswith('NORTH') else 4
        lay = next(l for l in json.load(open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'layouts', 'layouts.json')))['layouts']
                   if l['id'] == j['layout'])
        if b['y'] >= lay['height']:     # (script_check 2026-10-08) a sign below Sapphire's map (Lilycove Dept Store 1F's floor
            at, d = [b['x'], lay['height'] - 1], 4   # names at (0,8) of an 8-row map: never readable): on the last row,
        signs.append(dict(script=len(blocks), at=at, dir=d, _what=who))   # read from any side (the tile above it)
    for c in j.get('coord_events', []):
        todo.append(f"{name}: trigger ({c['x']},{c['y']}) {c.get('script')}: story")
    s_path = os.path.join(ROOT, 'src', 'field_scripts', f'{r["scripts"]:04d}_room_{name}.s')
    t_path = os.path.join(ROOT, 'src', 'text', 'script', f'{r["text"]:04d}_room_{name}.txt')
    entries = '\n'.join(f'    ScriptEntry Script_{i}' for i in range(1, len(blocks) + 1)) or '    ScriptEntry Script_None'
    src = (f'// {name} (zone {zone}): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,\n'
           f'// shop clerks with Sapphire\'s lists: data/hoenn_shops.json). Messages: src/text/script/{os.path.basename(t_path)}\n'
           '#include "asm/field_script.inc"\n#include "hoenn.h"\n\n' + entries + '\n    ScriptEntriesEnd\n\n'
           + '\n'.join(blocks) + ('' if blocks else 'Script_None:\n    VMHalt\n') + '    .balign 4, 0\n')
    from story_merge import write_room_script, write_room_text      # a story agent's part (after "// ---- story") stays
    write_room_text(t_path, msgs or ['…'], s_path)
    write_room_script(s_path, src)
    # parent (place name and music): the outdoor zone the room's door is in; a town not built yet (Sootopolis) -> its
    # zone in data/hoenn_zones.json, so the room is named after it once it exists
    hz = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    out_door = [(w['dest'], w['dest_warp']) for w in r['warps'] if (w['dest'], w['dest_warp']) in door]
    out_map = next((w['dest'] for w in r['warps'] if w['dest'] in hz), None)
    parent = PARENT.get(name) or (door[out_door[0]][0] if out_door else hz[out_map]['zone'] if out_map else
                                  json.load(open(os.path.join(ROOT, 'data', 'interiors', f'{zone}.json'))).get('parent', 389))
    cfg = dict(zone=zone, room=name, area=AREA, parent=parent,
        _doc=f'{name}: shops agent (b2tools/shops_rooms.py); recipe data/interior_layouts/{name}.json (b2tools/shops_recipes.py)',
        warps=warps, npcs=npcs, signs=signs)
    if name.startswith('Route110_SeasideCyclingRoad'):   # (frontier_sp 2026-10-20) Gen 3 lets you ride in the Cycling Road
        cfg = dict(list(cfg.items())[:2] + [('cycling', True)] + list(cfg.items())[2:])   # gates (pokeruby
        # Overworld_IsBikingAllowed): the gatesman sends a walker back, so the gate must let you get on the Bike there
    json.dump(cfg, open(os.path.join(ROOT, 'data', 'interiors', f'{zone}.json'), 'w'), indent=1, ensure_ascii=False)
    return s_path, len(npcs), len(signs)


def main(names, show_todo=False):
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    text, scripts = ruby_scripts()
    sprites = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
    door = door_map()
    todo = []
    for n in names or ROOMS:
        p, nn, ns = build(n, rooms, door, text, scripts, sprites, todo)
        print(f'{n}: {nn} people, {ns} signs -> {os.path.basename(p)}')
    if show_todo or True:
        print('\nLeft for the story phase / not convertible:'); print('\n'.join('  ' + t for t in todo))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    main(args, '--todo' in sys.argv)
