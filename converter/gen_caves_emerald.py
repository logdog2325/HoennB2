"""Emerald's caves (emerald_caves 2026-10-12; notes/EMERALD.md "Caves and dungeons"): converter/gen_caves.py's zone files
for the cave recipes whose map is Emerald's ("map": "emerald/<Map>": b2tools/models_cave.py reads it as Emerald's world
does, converter/gba.py Repo(..., emerald=True): HoennB2 names and MAP_ ids, pokeemerald's layouts and events).

    HOENN_VERSION=emerald python3 gen_caves.py [ROOM ...]      (gen_caves.main calls emerald_main; no names = every
                                                                 "emerald/" recipe, after gen_caves.ruby_encounters)

Two kinds of recipe (data/cave_layouts/<Room>.json):
  - an Emerald-only cave (data/emerald/hoenn_interiors.json, zone claimed with allocate_interiors.py --claim): its own
    zone json data/interiors/emerald/<zone>.json, script/init files src/field_scripts/emerald/<n>_room_<Map>.s (named by the
    zone's Black 2 numbers, installed at its own numbers as Sapphire's rooms), text src/text/script/emerald/, its wild
    table (pokeemerald gWildMonHeaders) src/encounters/emerald/<fid>_cave_<Map>.s with a free Unova encounter file kept in
    data/emerald/hoenn_encounters.json (identical tables share one file);
  - an Emerald variant of a Sapphire cave ("alt_of": <Sapphire room>, installed for it through data/versions.json
    room_variants.emerald): no zone of its own; with "emerald_zone": true its warps/triggers/objects differ from
    Sapphire's, so the zone json is replaced in Emerald (data/interiors/emerald/<the Sapphire zone>.json, "room" = the
    Sapphire name: patches/interiors.py swaps in the variant) and the zone's script file too (src/field_scripts/emerald/,
    the same file number: the shared file's story part is copied after the Emerald head, so every story entry keeps its
    number: notes/EMERALD_STORY.md 2.3). The wild table stays the shared zone's file (gen_caves.ruby_encounters writes
    Emerald's lines for it).
Sapphire's and Ruby's files are never written. Story objects (trainers, scenes) are listed, not placed, as gen_caves does.
"""
import os, sys, json, re, shutil, collections

import gen_caves as GC
from gen_caves import (ROOT, FILES, step_script, cave_lines, cave_text, level_y, story_flag, dest_origin, ARRIVAL_SCRIPT,
                       STORY_MARK, MODEL_BOULDER, SCRIPT_STRENGTH, SCRIPT_ROCK, HEADER_KEYS, TEMPLATE, TEMPLATE_DARK)
MC, version = GC.MC, GC.version
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')
# Place-name lines of Emerald's new places (system text 0109): lines no zone of the Emerald build shows (Black 2's
# "Village Bridge" 91 and "Accumula Gate" 106 name no zone; not "White Gate" 113: ZoneData_GetPlaceNameID (arm9
# 0x02018c80) returns 112 for 113, so a zone with 113 showed "Terra Cave" (emerald_release 2026-10-12); "Undella Gate" 107, "Nimbasa Gate" 110, "Opelucid Gate" 111,
# "Black Gate" 112 only Unova zones the Emerald build has made Hoenn rooms); the names: src/text/emerald/
# overrides_emerald_caves.json. Underwater maps: Sapphire's "Underwater" line.
PLACES = {'MAPSEC_MAGMA_HIDEOUT': 91, 'MAPSEC_MIRAGE_TOWER': 107, 'MAPSEC_ARTISAN_CAVE': 110, 'MAPSEC_DESERT_UNDERPASS': 111,
          'MAPSEC_TERRA_CAVE': 112, 'MAPSEC_MARINE_CAVE': 106, 'MAPSEC_UNDERWATER_105': 55, 'MAPSEC_UNDERWATER_129': 55,
          'MAPSEC_UNDERWATER_MARINE_CAVE': 55}
PLACE_NAMES = {91: 'Magma Hideout', 107: 'Mirage Tower', 110: 'Artisan Cave', 111: 'Desert Underpass', 112: 'Terra Cave',
               106: 'Marine Cave'}
OVERLAY_TEXT = os.path.join(ROOT, 'src', 'text', 'emerald', 'overrides_emerald_caves.json')

_R = {}
def repo():
    if 'r' not in _R:
        from gba import Repo
        _R['r'] = Repo(os.path.join(ROOT, 'external', 'pokeruby'), emerald=True)
    return _R['r']

def emerald_recipes():
    """Recipe name -> recipe of every data/cave_layouts/<Room>.json whose map is Emerald's."""
    out = {}
    for f in sorted(os.listdir(MC.LAYOUTS)):
        if not f.endswith('.json') or f.startswith('_'): continue
        r = MC.load_json(os.path.join(MC.LAYOUTS, f), {}) or {}
        if isinstance(r, dict) and str(r.get('map', '')).startswith('emerald/'): out[f[:-5]] = r
    return out

def scripts_inc(mapname):
    """pokeemerald's scripts.inc of HoennB2 map `mapname` ('' without one)."""
    folder = repo().emerald_folder(mapname) or mapname
    p = os.path.join(EMERALD, 'data', 'maps', folder, 'scripts.inc')
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''

def hole_warp(mapname):
    """Emerald's fall destination (setholewarp MAP_X in the map's scripts) as a HoennB2 map name, or None."""
    m = re.search(r'setholewarp\s+(MAP_\w+)', scripts_inc(mapname))
    return MC.emerald_dest_name(repo().hoenn_id(m.group(1))) if m else None

def map_scripts(mapname):
    src = scripts_inc(mapname)
    folder = repo().emerald_folder(mapname) or mapname
    m = re.search(rf'{folder}_MapScripts::.*?\n((?:\s*map_script .*\n)*)', src)
    return re.findall(r'map_script (MAP_SCRIPT_\w+), (\w+)', m.group(1)) if m else []

def wild_table(mapname):
    """pokeemerald's gWildMonHeaders entry of the map (by its Emerald MAP_ id), or None."""
    if 'wild' not in _R:
        wild = json.load(open(os.path.join(EMERALD, 'src', 'data', 'wild_encounters.json')))
        g = next(g for g in wild['wild_encounter_groups'] if g.get('label') == 'gWildMonHeaders')
        _R['wild'] = {}
        for e in g['encounters']: _R['wild'].setdefault(e['map'], e)
    folder = repo().emerald_folder(mapname) or mapname
    p = os.path.join(EMERALD, 'data', 'maps', folder, 'map.json')
    return _R['wild'].get(json.load(open(p))['id']) if os.path.exists(p) else None

def recipe_for(mapname, recipes):
    """The recipe that builds HoennB2 map `mapname` in Emerald: its Emerald variant (room_variants.emerald) or its own."""
    v = version.room_variant(mapname, 'emerald')
    return v if v in recipes or os.path.exists(os.path.join(MC.LAYOUTS, v + '.json')) else mapname

# ---------------------------------------------------------------------------------------------------- encounters
REG_DOC = ('Emerald-only maps\' wild-table files (a/1/2/7 ids; caves: converter/gen_caves_emerald.py, outdoor maps: '
           'converter/gen_encounters.py emerald_new_maps; allocate: free Unova files that no Sapphire or Emerald zone and no '
           'data/hoenn_encounters.json entry uses, else new files after Black 2\'s)')

def allocate(name, table, reg, shared_reg, tables):
    """A free Unova a/1/2/7 file for an Emerald-only cave (gen_caves.allocate's rules over Sapphire's and Emerald's zones and
    both registries); an Emerald-only cave whose table equals another's shares its file."""
    import narcio, zoneheaders
    if name in reg: return reg[name]
    key = GC._table_key(table)
    for other, fid in sorted(reg.items()):
        if other in tables and tables[other] is not None and GC._table_key(tables[other]) == key:
            reg[name] = fid; return fid
    sizes = [len(x) for x in narcio.load(FILES, 127)]
    headers, _ = zoneheaders.load(FILES)
    zones = version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps']
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    hoenn = {m['zone'] for m in zones.values()} | {r['zone'] for r in rooms.values() if 'zone' in r}
    keep = {headers[z]['encounters'] for z in (427, 428)}
    free = sorted({h['encounters'] for i, h in enumerate(headers) if i not in hoenn and h['encounters'] < len(sizes)}
                  - keep - {headers[z]['encounters'] for z in hoenn} - set(shared_reg.values()) - set(reg.values()))
    if free:
        reg[name] = free[-1]      # (from the end: Sapphire's allocate takes them from the start)
    else:                         # none left (Sapphire's caves took them): a new file after Black 2's 135, Emerald only
        reg[name] = max([len(sizes) - 1] + [v for v in reg.values() if v >= len(sizes)]) + 1   # (patches/encounters.py
    return reg[name]                                                                         # appends it)

def write_encounters(name, zone, table, fid):
    import narcio
    sizes = [len(x) for x in narcio.load(FILES, 127)]
    out = os.path.join(ROOT, 'src', 'encounters', 'emerald'); os.makedirs(out, exist_ok=True)
    shared = [f for f in os.listdir(out) if f.startswith(f'{fid:04d}_') and not f.endswith(f'_cave_{name}.s')]
    for f in os.listdir(out):                     # this cave's file under another id, or a second cave of a shared file
        if f.endswith(f'_cave_{name}.s') and (shared or not f.startswith(f'{fid:04d}_')):
            os.rename(os.path.join(out, f), os.path.join(os.path.expanduser('~/.Trash'), f'{f}.{os.getpid()}'))
    if shared: return f'{name}: Emerald\'s wild table = {shared[0]}\'s (encounter file {fid} shared)'
    sec, lines = cave_lines(table, sizes[fid] if fid < len(sizes) else 232)   # (a new file: one table, as caves')
    open(os.path.join(out, f'{fid:04d}_cave_{name}.s'), 'w').write(cave_text(name, zone, fid, table, sec, lines))
    return None

# ---------------------------------------------------------------------------------------------------- main
def emerald_main(names):
    from gen_map_content import ruby_scripts, simple_message
    from gen3text import convert
    from gen_interiors import npc_block, sign_block
    from story_merge import write_room_script, write_room_text, _split
    import zoneheaders
    recipes = emerald_recipes()
    names = names or sorted(recipes)
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    zones = version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))
    world = json.load(open(os.path.join(version.world_dir(), 'world.json')))
    door = GC.door_index(world)
    headers, _ = zoneheaders.load(FILES)
    balls = version.load_json(os.path.join(ROOT, 'data', 'hoenn_items.json'))['balls']
    sprites = version.load_json(os.path.join(ROOT, 'data', 'sprite_map.json'))
    shared_reg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_encounters.json')))
    reg_path = os.path.join(ROOT, 'data', 'emerald', 'hoenn_encounters.json')
    reg = json.load(open(reg_path)) if os.path.exists(reg_path) else {}
    reg = {k: v for k, v in reg.items() if not k.startswith('_')}
    reg_before = dict(reg)
    text, scripts = ruby_scripts(EMERALD)
    report, story = [], collections.defaultdict(list)
    caves = {}
    def cave(n):
        if n not in caves: caves[n] = MC.Cave(n)
        return caves[n]
    def to_of(dest, dw, zone):
        """(zone, warp) a warp to HoennB2 map dest, warp dw leads to (a door of Emerald's world, a room, a dynamic warp)."""
        if dest == 'MAP_DYNAMIC': return (zone, 256)    # Black 2's dynamic warp: dest id 0x100 = GameData's next zone
        to = door.get(version.door_alias(dest, dw, 'emerald')) or door.get((dest, dw))
        if to is None and dest in rooms and 'zone' in rooms[dest]:
            st = rooms[dest]['status']
            to = (rooms[dest]['zone'], 0 if st == 'b2' else dw) if st in ('auto', 'big', 'b2', 'hand', 'cave', 'center') else None
        return to
    tables = {n: wild_table(n) for n in rooms if rooms[n].get('claimed_by') == 'emerald_caves'}
    for name in names:
        r_ = recipes[name]
        base = r_.get('alt_of')
        mapname = r_['map'][len('emerald/'):]
        if base and not r_.get('emerald_zone'):
            report.append(f'{name}: Emerald layout of {base} (data/versions.json room_variants.emerald), Sapphire\'s zone json'); continue
        room_name = base or name
        r = rooms[room_name]; zone = r['zone']
        c = cave(name); sm = c.sm
        dark = bool(sm['json'].get('requires_flash'))
        # ---- warps, in Emerald's order (a door names Emerald's dest_warp_id)
        warps, unresolved = [], []
        for spot, w in zip(c.spots, sm['warps']):
            dest, dw = MC.emerald_dest_name(w['dest_map']), w['dest_warp_id']
            dw = int(dw) if str(dw).isdigit() else 0
            to = to_of(dest, dw, zone)
            what = f'Emerald warp {spot["index"]} ({w["x"]},{w["y"]}) -> {dest} {dw}'
            if to is None: unresolved.append(what); to = (zone, 0); what += ' (not built: points at this cave\'s warp 0)'
            warps.append(dict(at=[w['x'], w['y']], to=list(to), what=what))
        # ---- links (recipe "links": Sapphire's map connections between two underwater maps, gen_caves.main's): one wide
        # warp each way; FIRST here, so a variant keeps the index the other map's shared zone json names (Underwater4 ->
        # Underwater3 warp 0: Sapphire's Underwater3 has no warps of its own, Emerald's has two to the Marine Cave)
        opp = {'n': 's', 's': 'n'}
        links = []
        for spot in (s_ for s_ in c.spots if s_['kind'] == 'link'):
            ln = c.r['links'][spot['link']]
            dc = cave(recipe_for(ln['to'], recipes))
            nth = next(k_ for k_, l2 in enumerate(dc.r.get('links', [])) if l2['to'] == room_name and l2['side'] == opp[ln['side']])
            dw_ = len(rooms[ln['to']]['warps']) + nth
            links.append(dict(x=spot['x'], z=spot['z'], w=spot['w'], h=1, type=4, dir=spot['dir'],
                              to=[rooms[ln['to']]['zone'], dw_], **MC.spot_y(c, spot),
                              what=f'Sapphire connection {ln["side"]} (x {ln["x"][0]}-{ln["x"][1]}) -> {ln["to"]} warp {dw_}'))
        warps = links + warps
        # ---- step triggers: ladders and cracked floors (gen_caves.main's patterns)
        blocks, trig, k = [], [], 0
        for spot, w in zip(c.spots, sm['warps']):
            if not spot.get('step'): continue
            dest = MC.emerald_dest_name(w['dest_map'])
            if dest not in rooms or rooms[dest].get('status') != 'cave':
                report.append(f'{name}: ladder {w["x"]},{w["y"]} -> {dest}: not a cave, no trigger'); continue
            dc = cave(recipe_for(dest, recipes))
            dwp = dc.sm['warps'][int(w['dest_warp_id'])]
            dox, doz = dest_origin(dc.name, dc)
            tx, tz = dox + dwp['x'], doz + dwp['y']
            ty = round(dc.fy.get((dwp['x'], dwp['y']), 0) / 16)
            k += 1
            blocks.append(step_script(k, f'ladder {spot["kind"][7:]} ({w["x"]},{w["y"]}) -> {dest} warp {w["dest_warp_id"]} ({dwp["x"]},{dwp["y"]})',
                                      ['ActorsPauseAll', 'SEPlay SEQ_SE_KAIDAN', 'FadeOutBlack', f'RTReserveScript {ARRIVAL_SCRIPT}',
                                       'FadeWait', f'MapChangeCore {rooms[dest]["zone"]}, {tx}, {ty}, {tz}, 1',
                                       'FinishAllEvents', 'ActorsUnpauseAll', 'VMHalt']))
            trig.append(dict(script=k, var=0, value=0, at=[w['x'], w['y']], **level_y(c, w['x'], w['y'])))
        falls = [(x, z) for (x, z), s in c.special.items() if s in ('cracked', 'hole')]
        if falls:
            dest = hole_warp(mapname)
            if not dest or dest not in rooms:
                report.append(f'{name}: {len(falls)} cracked floor tiles, hole warp {dest} not a Hoenn cave: no triggers')
            else:
                dc = cave(recipe_for(dest, recipes)); dz = rooms[dest]['zone']
                for (x, z) in sorted(falls, key=lambda t: (t[1], t[0])):
                    k += 1
                    dox, doz = dest_origin(dc.name, dc)
                    lx, lz = x, z
                    if not dc.sm['walk'][z][x]:
                        near = [(x + a, z + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))
                                if 0 <= z + b < len(dc.sm['walk']) and 0 <= x + a < len(dc.sm['walk'][0]) and dc.sm['walk'][z + b][x + a]]
                        if near: lx, lz = near[0]
                        report.append(f'{name}: fall from {x},{z} lands on a blocked tile of {dest}' + (f': moved to {lx},{lz}' if near else ''))
                    tx, tz = dox + lx, doz + lz
                    lab = f'L_Fall_{k}'
                    blocks.append(step_script(k, f'cracked floor ({x},{z}) -> fall to {dest} ({lx},{lz})',
                        ['PlayerGetExState 0x8010', 'VMStackPush 0x8010', 'VMStackPushConst 1', 'VMStackCmp CMP_EQ',
                         f'VMJumpIf CMP_STACK, {lab}', 'VMHalt', '']).rstrip() + f'\n{lab}:\n' + ''.join(f'    {l}\n' for l in
                        ['ActorsPauseAll', 'SEPlay SEQ_SE_DANSA', 'FadeOutBlack', f'RTReserveScript {ARRIVAL_SCRIPT}', 'FadeWait',
                         f'MapChangeCore {dz}, {tx}, {round(dc.fy.get((lx, lz), 0) / 16)}, {tz}, 1',
                         'FinishAllEvents', 'ActorsUnpauseAll', 'VMHalt']))
                    trig.append(dict(script=k, var=0, value=0, at=[x, z], **level_y(c, x, z)))
        # ---- objects (Emerald's: item balls of data/emerald/hoenn_items.json, boulders, rocks, simple people/signs)
        npcs, signs, msgs = [], [], []
        for lid, o in enumerate(sm['objects'], 1):
            g = o['graphics_id']; at = [o['x'], o['y']]
            if g == 'OBJ_EVENT_GFX_ITEM_BALL':
                b = balls.get(o['script'])
                if b: npcs.append(dict(uid=lid, model=110, script=b['script'], flag=b['flag'], dir=1, at=at, what=f'item ball {b["item"]}'))
                else: story[name].append(f'item ball {o["script"]} without a Black 2 item')
                continue
            if g == 'OBJ_EVENT_GFX_PUSHABLE_BOULDER':
                npcs.append(dict(uid=lid, model=MODEL_BOULDER, script=SCRIPT_STRENGTH, flag=0, dir=1, at=at, what='Strength boulder')); continue
            if g == 'OBJ_EVENT_GFX_BREAKABLE_ROCK':
                code = sprites.get(g, {}).get('code') or 206
                fl = str(o.get('flag', '0'))
                hide = story_flag(fl) if not fl.startswith('FLAG_TEMP') and fl != '0' else 0
                if fl not in ('0', '') and not fl.startswith('FLAG_TEMP'):
                    story[name].append(f'breakable rock {lid} ({o["x"]},{o["y"]}) has {fl}' + (f' ({hide})' if hide else ' (no id: placed without it)'))
                npcs.append(dict(uid=lid, model=code, script=SCRIPT_ROCK, flag=hide, dir=1, at=at, what='breakable rock'
                                 + (f' ({fl})' if hide else ''))); continue
            if o.get('trainer_type', 'TRAINER_TYPE_NONE') not in ('TRAINER_TYPE_NONE', '0', 0):
                story[name].append(f'trainer {g} ({o["x"]},{o["y"]}) {o["script"]}'); continue
            if str(o.get('flag', '0')) not in ('0', ''):
                story[name].append(f'story object {g} ({o["x"]},{o["y"]}) {o["script"]} hide flag {o["flag"]}'); continue
            code = (sprites.get(g) or {}).get('code')
            label = simple_message(o['script'], text, scripts) if code else None
            if not label or convert(text[label])[1]:
                story[name].append(f'person {g} ({o["x"]},{o["y"]}) {o["script"]}: not one message / no sprite'); continue
            msgs.append(convert(text[label])[0]); k += 1
            blocks.append(npc_block(k, len(msgs) - 1))
            face = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2,
                    'MOVEMENT_TYPE_FACE_RIGHT': 3}.get(o['movement_type'], 1)
            n = dict(uid=lid, model=code, script=k, dir=face, at=at)
            n.update(GC.MOVE_CODES.room_npc(o))
            npcs.append(n)
        for i, x in enumerate(c.r.get('extra_npcs', [])):   # recipe "extra_npcs": objects Emerald draws as map tiles
            fl = x.get('flag', 0)                          # (a cave mouth closed until the game is clear: Black 2's
            npcs.append(dict(uid=x.get('uid', 100 + i), model=x['model'], script=x.get('script', 0), dir=x.get('dir', 1),
                             at=x['at'], flag=story_flag(fl) if isinstance(fl, str) else fl, what=x.get('what', '')))   # rock 206)
        for b in sm['bgs']:
            if b.get('type') == 'hidden_item':
                story[name].append(f'hidden item {b["item"]} at ({b["x"]},{b["y"]}) {b["flag"]} (Black 2 hidden items: not placed)'); continue
            if b.get('type') != 'sign' or not b.get('script'): continue
            label = simple_message(b['script'], text, scripts)
            if not label or convert(text[label])[1]: story[name].append(f'sign ({b["x"]},{b["y"]}) {b["script"]}'); continue
            msgs.append(convert(text[label])[0]); k += 1
            blocks.append(sign_block(k, len(msgs) - 1))
            signs.append(dict(script=k, at=[b['x'], b['y']], dir=0 if b.get('player_facing_dir', '').endswith('NORTH') else 4,
                              **level_y(c, b['x'], b['y'])))
        for e in sm['coords']:
            story[name].append(f'coord event ({e["x"]},{e["y"]}) {e.get("script")} var {e.get("var")}={e.get("var_value")}')
        for kind_, label in map_scripts(mapname):
            if label.startswith('CaveHole_') or (falls and kind_ == 'MAP_SCRIPT_ON_RESUME'): continue
            story[name].append(f'map script {kind_} {label}')
        # ---- header: the look's Black 2 cave header, Emerald's place name, the wild table's file
        t = headers[c.r.get('header_zone') or (c.look.get('header_zone_dark', TEMPLATE_DARK) if dark else c.look.get('header_zone', TEMPLATE))]
        hd = {k_: t[k_] for k_ in HEADER_KEYS}
        hd['map_type'] = 16
        sec = sm['json'].get('region_map_section')
        if sec in zones['places']: hd['place'] = zones['places'][sec]['line']
        elif sec in PLACES: hd['place'] = PLACES[sec]
        else: report.append(f'{name}: no place name for {sec}')
        if base and shared_reg.get(base) is not None:   # a variant: the shared zone's file (Emerald's lines: ruby_encounters)
            fid = shared_reg.get(base)
        elif base:                                      # a variant whose Sapphire room has no wild table but Emerald's
            tab = wild_table(mapname)                   # has (Emerald's Cave of Origin B1F): a file of Emerald's own
            fid = allocate(room_name, tab, reg, shared_reg, dict(tables, **{room_name: tab})) if tab else None
            if tab:
                w_ = write_encounters(room_name, zone, tab, fid)
                if w_: report.append(w_)
        else:
            tab = tables.get(room_name)
            fid = allocate(room_name, tab, reg, shared_reg, tables) if tab else None
            if tab:
                w_ = write_encounters(room_name, zone, tab, fid)
                if w_: report.append(w_)
        hd.update(encounters=fid if fid is not None else 0x1FFF, enc_slot=2 if fid is not None else 6)
        # ---- write: zone json, script (+ init), text
        jdir = os.path.join(ROOT, 'data', 'interiors', 'emerald'); os.makedirs(jdir, exist_ok=True)
        jpath = os.path.join(jdir, f'{zone}.json')
        cfg = dict(zone=zone, room=room_name, cave=True, cave_auto=True, area=c.look['area'], dark=dark, header=hd,
                   warps=warps, triggers=trig, npcs=npcs, signs=signs,
                   what=f'{room_name}: Emerald\'s cave (converter/gen_caves_emerald.py from {r_["map"]}, b2tools/models_cave.py'
                        + (f', room {name}' if base else '') + '); story objects: see notes/EMERALD.md')
        old = json.load(open(jpath)) if os.path.exists(jpath) else None
        if old and not old.get('cave_auto'):
            for k_ in ('npcs', 'signs'): cfg[k_] = old.get(k_, cfg[k_])
            cfg['cave_auto'] = False
            report.append(f'{name}: zone {zone} Emerald json edited by hand: kept its npcs/signs')
        if c.r.get('alt_rooms'): cfg['alt_rooms'] = c.r['alt_rooms']
        if base and os.path.exists(os.path.join(ROOT, 'data', 'interiors', f'{zone}.json')):   # (a variant keeps the
            sh = json.load(open(os.path.join(ROOT, 'data', 'interiors', f'{zone}.json')))     # shared zone's own keys)
            for k_ in ('scripts', 'init_scripts', 'text', 'alt_rooms', 'variants'):
                if k_ in sh and k_ not in cfg: cfg[k_] = sh[k_]
        json.dump(cfg, open(jpath, 'w'), indent=1, ensure_ascii=False)
        sdir = os.path.join(ROOT, 'src', 'field_scripts', 'emerald'); os.makedirs(sdir, exist_ok=True)
        tdir = os.path.join(ROOT, 'src', 'text', 'script', 'emerald'); os.makedirs(tdir, exist_ok=True)
        fname = f'{r["scripts"]:04d}_room_{room_name}.s'
        sp = os.path.join(sdir, fname)
        shared_sp = os.path.join(ROOT, 'src', 'field_scripts', fname)
        if base and os.path.exists(shared_sp) and not msgs and all(b_ in open(shared_sp).read() for b_ in blocks) \
                and not (c.r.get('underwater') and c.r.get('uw_effect', True)):
            # (a variant whose Emerald scripts are Sapphire's, the same numbers: the shared file serves Emerald too, and
            # story agents keep one file; an older Emerald copy goes to the Trash)
            if os.path.exists(sp): os.rename(sp, os.path.join(os.path.expanduser('~/.Trash'), f'{fname}.{os.getpid()}'))
            report.append(f'{name}: zone {zone} (Emerald zone json), scripts: the shared {fname}, {len(warps)} warps, {len(trig)} '
                          f'triggers, {len(npcs)} objects, encounters {fid}, dark {dark}')
            continue
        if base and not os.path.exists(sp) and os.path.exists(shared_sp) and _split(open(shared_sp).read())[1]:
            shutil.copy(shared_sp, sp)              # (a variant: the shared story part follows the Emerald head)
            report.append(f'{name}: {fname}: the shared story part copied after the Emerald head (story entries keep their numbers)')
        if c.r.get('underwater') and c.r.get('uw_effect', True):   # Black 2's underwater look (gen_caves.main's)
            k += 1
            blocks.append(step_script(k, 'field load / return: the underwater effect (Abyssal Ruins script plugin, '
                                         'b2tools/patches/dive.py lists this zone)', ['AbyssalRuinsCmd_StartUnderwaterEffect', 'VMHalt']))
            ip = os.path.join(sdir, f'{r["init_scripts"]:04d}_room_{room_name}_init.s')
            if not os.path.exists(ip) or not GC._has_story_mark(ip):
                open(ip, 'w').write(f'// Map scripts of {room_name} (zone {zone}, Emerald): converter/gen_caves_emerald.py. Field load (MapScript 3)\n'
                                    f'// and return (MapScript 4) = script {k}: the underwater effect, as Black 2\'s Abyssal Ruins\n'
                                    f'// (0483.s). Story map scripts: add a line "{STORY_MARK}" (then this file is left alone).\n'
                                    '#include "asm/field_script.inc"\n#include "hoenn.h"\n\n'
                                    f'    MapScript 3, {k}\n    MapScript 4, {k}\n    MapScriptsEnd\n    .balign 4, 0\n')
        if base and os.path.exists(sp) and _split(open(sp).read())[1]:   # (a variant with the shared story part: the story
            nums = [int(m_) for m_ in re.findall(r'^\s*ScriptEntry Script_(\d+)\s*$', open(shared_sp).read(), re.M)]   # entries
            k_shared = max(nums, default=0)                  # follow Sapphire's generated count: pad to it, so each keeps its number)
            assert k <= k_shared, f'{name}: {k} generated scripts, Sapphire has {k_shared}: the story entries would move'
            for i in range(k + 1, k_shared + 1):
                blocks.append(step_script(i, f'(Sapphire\'s script {i}: nothing in Emerald; keeps the story entries\' numbers)', ['VMHalt']))
            k = k_shared
        entries = ''.join(f'    ScriptEntry Script_{i}\n' for i in range(1, k + 1)) or '    ScriptEntry Script_None\n'
        src = (f'// {room_name} (zone {zone}, Emerald): converter/gen_caves_emerald.py from {r_["map"]} (emerald_caves): ladders and\n'
               f'// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "{STORY_MARK}" (this\n'
               f'// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them\n'
               f'// after these entries.\n'
               + (f'// Messages: src/text/script/emerald/{r["text"]:04d}_room_{room_name}.txt\n' if msgs else '')
               + '#include "asm/field_script.inc"\n#include "hoenn.h"\n\n' + entries + '    ScriptEntriesEnd\n\n'
               + ('\n'.join(blocks) if blocks else 'Script_None:\n    VMHalt\n') + '    .balign 4, 0\n')
        if msgs:
            tp = os.path.join(tdir, f'{r["text"]:04d}_room_{room_name}.txt')
            shared_tp = os.path.join(ROOT, 'src', 'text', 'script', os.path.basename(tp))
            if base and not os.path.exists(tp) and os.path.exists(shared_tp): shutil.copy(shared_tp, tp)
            w = write_room_text(tp, msgs, sp)
            if w: report.append(w)
        if write_room_script(sp, src) != 'written': report.append(f'{name}: {sp} has story scripts (after "{STORY_MARK}"): merged')
        report.append(f'{name}: zone {zone}, {len(warps)} warps ({len(unresolved)} unresolved), {len(trig)} triggers, '
                      f'{len(npcs)} objects, encounters {fid}, dark {dark}')
        for u in unresolved: report.append(f'  unresolved: {u}')
    if reg != reg_before:
        json.dump(dict(_doc=REG_DOC, **dict(sorted(reg.items()))), open(reg_path, 'w'), indent=1)
    # the new places' names on their lines (patches/text.py reads src/text/emerald/overrides*.json in an Emerald build)
    json.dump({'_doc': 'Emerald\'s new cave places (converter/gen_caves_emerald.py PLACES: lines no zone of the Emerald build shows)',
               'system/0109_place_names.txt': {str(k): v for k, v in sorted(PLACE_NAMES.items())}},
              open(OVERLAY_TEXT, 'w'), indent=1, ensure_ascii=False)
    print('\n'.join(report))
    for n, items in story.items():
        print(f'{n}: left for the story agents:'); print('\n'.join('  ' + s for s in items))
