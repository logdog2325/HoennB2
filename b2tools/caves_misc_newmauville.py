"""The caves_misc agent's New Mauville generator: writes the recipe of New Mauville's inside (data/interior_layouts/
NewMauville_Inside.json, built by b2tools/models_interior.py as a big room, 2x2 chunks) from Sapphire's metatiles, and
the agent's room styles (data/interior_layouts/_styles_caves_misc.json "cm_newmauville", "cm_nm_wall").

    python3 caves_misc_newmauville.py    (then HOENN_AGENT=caves_misc zsh b2tools/agent_build_caves.sh NewMauville_Inside:
                                          converter/gen_caves.py writes the zone files)

Sapphire's New Mauville (41x41, gTileset_BikeShop; metatile ids read off the map, b2tools/../work/agents/caves_misc
mtcrop renders): rooms and corridors in the black (0x208), separated by two-tile walls (a dark top row, a beige riveted
face row: 0x21f/0x227 and their ends and corners, white pillars 0x270/0x272 at the rooms' sides), machines standing in
the walls' face row or on the floor. Black 2 (P2 Laboratory, area 345: its beige panel wall in64_lab03_04 is
Sapphire's riveted wall, its pale tile floor in64_lab03_01):
  floor     every tile that is not the black outside; no room walls of the builder ("open": the rooms float in the
            black, as Sapphire's and Black 2's League walkways)
  walls     every other blocked tile: a raised block (cm_nm_wall: 24 units of the panel wall, a black top as Black 2's
            wall caps; 40 hid the player standing north of a wall)
  machines  0x2d7 orange cabinet -> machine01, 0x2d6 white terminal -> machine02, 0x2a1/0x2a2 tool shelf -> shelf01,
            the green tank units (0x2d4-0x2e5, 2x3) -> machine_l02, the generator (0x2d0-0x2eb, 4x4) -> pcmachine01
            (Black 2's orange hexagonal core), crates 0x2c0/0x2c2 -> box01, 0x2c1/0x2c3/0x2b3 -> box02_1 (2x2 squares of crates -> box02), desks 0x2b0/
            0x2b1 -> table02_2w, 0x2b4 -> desk02, the bench 0x2ab/0x2ac -> table02_2w, debris 0x258 -> dust01
  barriers  the blue (0x2b7/0x2bf/0x2c7/0x2cf) and green (0x2b6/0x2be/0x2c6/0x2ce) barriers: Black 2's electric floor
            (d6_yuka_biri02_1, as the Mauville Gym's) on their two passage tiles, blocked as in Sapphire's map (both
            colours up). Sapphire's switches lower one colour and raise the other (setmetatile: the passage tiles of
            the lowered colour become plain floor, passable): two more layouts of the room, NewMauville_Inside_BlueDown
            (blue lowered, green up) and NewMauville_Inside_GreenDown, loaded instead of the room's by map replace
            events 5 and 6 (works 0x4036 / 0x4037; the zone's "alt_rooms": b2tools/patches/interiors.py; story_fixups
            2026-10-07; the story: src/field_scripts/0266_room_NewMauville_Inside.s)
Wild encounters (behaviour 0x0B on the floor): recipe "encounters". The exit (32,33) is the builder's stair spot (a
warp walked into northwards in a notch of the wall).
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'converter'))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
NAME = 'NewMauville_Inside'
ORIGIN = [12, 12]        # Sapphire (20, 20) on the corner of the 2x2 chunks: the machines spread over all four (Black 2
                         # allows 32 building placements per chunk)
SET = 345
VOID = 0x208
PER_TILE = {0x2d7: 'machine01', 0x2d6: 'machine02', 0x2c0: 'box01', 0x2c2: 'box01', 0x2c1: 'box02_1', 0x2c3: 'box02_1',
            0x2b3: 'box02_1', 0x2b4: 'desk02', 0x258: 'dust01'}
GROUPS = {'shelf01': {0x2a1, 0x2a2}, 'machine_l02': {0x2d4, 0x2d5, 0x2dc, 0x2dd, 0x2e4, 0x2e5},
          'pcmachine01': set(range(0x2d0, 0x2d4)) | set(range(0x2d8, 0x2dc)) | set(range(0x2e0, 0x2e4)) | set(range(0x2e8, 0x2ec)),
          'table02_2w': {0x2b0, 0x2b1, 0x2ab, 0x2ac}}
CRATES = {0x2c0, 0x2c1, 0x2c2, 0x2c3}
BARRIER_PASS = {0x2c7, 0x2cf, 0x2c6, 0x2ce}          # the two lower tiles of each barrier (walkable when lowered)
BLUE_PASS, GREEN_PASS = {0x2c7, 0x2cf}, {0x2c6, 0x2ce}
EVENT_BLUE_DOWN, EVENT_GREEN_DOWN = 5, 6              # map replace events (works 0x4036 / 0x4037, data/story_ids.json)
ALTS = {'blue': (NAME + '_BlueDown', EVENT_BLUE_DOWN), 'green': (NAME + '_GreenDown', EVENT_GREEN_DOWN)}

STYLES = {
    "cm_newmauville": {
        "_doc": "caves_misc: New Mauville = Black 2's P2 Laboratory (texture set 345, area 345): pale tile floor in64_lab03_01, beige panel wall in64_lab03_04 (Sapphire's riveted wall).",
        "floor": {"tex": "in64_lab03_01", "src": SET, "size": 16},
        "wall": {"tex": "in64_lab03_04", "src": SET, "u_size": 32},
        "genkan": {"tex": "in64_lab03_01", "src": SET, "size": 16},
        "black": {"tex": "black", "src": 285}},
    "cm_nm_wall": {
        "_doc": "caves_misc: block style: New Mauville's two-tile walls: P2 Lab's beige panel wall over 18 units (a 40-unit wall hid the player standing north of it from Black 2's camera; at 24 its black top was drawn across the head of a person standing south of it: indoor_check, rooms_view.py kind m), a black top (Black 2's wall caps).",
        "h": 18, "top": {"tex": "black", "src": 285, "size": 16},
        "side": {"tex": "in64_lab03_04", "src": SET, "u_size": 32}}}

def recipe(state='base'):
    """state: 'base' (Sapphire's map: every barrier up), 'blue' (the blue barriers lowered: Sapphire's EventScript_15E5DA,
    green up) or 'green' (EventScript_15E728)."""
    from gba import Repo
    repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    mj = repo.map_json(NAME)
    g, l = repo.layout_grid(mj['layout'])
    H, W = g.shape
    mt = lambda x, z: int(g[z, x]) & 0x3FF
    walk = lambda x, z: (int(g[z, x]) >> 10) & 3 == 0
    tiles = [(x, z) for z in range(H) for x in range(W) if mt(x, z) != VOID]
    furniture, walls, used, lowered = [], [], set(), []
    # 2x2 squares of crates: one stack (box02, 1.6x1.9 tiles), so the crates of a room fit Black 2's 32 placements
    crates = {t for t in tiles if mt(*t) in CRATES}
    for (x, z) in sorted(crates, key=lambda t: (t[1], t[0])):
        sq = [(x, z), (x + 1, z), (x, z + 1), (x + 1, z + 1)]
        if all(t in crates and t not in used for t in sq):
            furniture.append(dict(m='box02', at=[x + 1, z + 1], _what=f'crates {x},{z}..{x + 1},{z + 1}')); used |= set(sq)
    for (x, z) in tiles:
        m = mt(x, z)
        if (x, z) in used: continue
        if m in PER_TILE:
            furniture.append(dict(m=PER_TILE[m], tile=[x, z], _what=f'Sapphire 0x{m:x} ({x},{z})')); used.add((x, z))
        elif m in BARRIER_PASS:
            used.add((x, z))
            if state == ('blue' if m in BLUE_PASS else 'green' if m in GREEN_PASS else None):
                lowered.append([x, z])               # lowered: plain floor, passable (no electric floor)
            else:
                furniture.append(dict(m='d6_yuka_biri02_1', tile=[x, z], _what=f'barrier ({x},{z}) 0x{m:x}'))
    for model, ids in GROUPS.items():
        todo = {t for t in tiles if mt(*t) in ids}
        while todo:
            t0 = min(todo, key=lambda t: (t[1], t[0])); comp = {t0}; st = [t0]
            while st:
                c = st.pop()
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (c[0] + dx, c[1] + dz)
                    if n in todo and n not in comp: comp.add(n); st.append(n)
            todo -= comp; used |= comp
            xs = [t[0] for t in comp]; zs = [t[1] for t in comp]
            furniture.append(dict(m=model, at=[(min(xs) + max(xs) + 1) / 2, (min(zs) + max(zs) + 1) / 2],
                                  _what=f'Sapphire {model} group {min(xs)},{min(zs)}..{max(xs)},{max(zs)}'))
    for (x, z) in tiles:
        if not walk(x, z) and (x, z) not in used: walls.append([x, z])
    rows = {}
    for x, z in tiles: rows.setdefault(z, []).append(x)
    floor = []
    for z, xs in sorted(rows.items()):
        xs.sort(); s = p = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == p + 1: p = x; continue
            floor.append([s, z, p, z])
            if x is not None: s = p = x
    r = dict(map=NAME, style='cm_newmauville', origin=ORIGIN, encounters=True, open=True, floor=floor,
             blocks=[dict(use='cm_nm_wall', tiles=walls)], furniture=furniture,
             cave_zone=dict(area=SET, header_zone=239))    # converter/gen_caves.py: P2 Laboratory's header
    if state == 'base':
        r['alt_rooms'] = [dict(room=n, event=e) for n, e in ALTS.values()]     # gen_caves -> the zone json -> interiors patch
    else:
        del r['cave_zone']                                 # another layout of the zone: no zone files of its own
        r['alt_of'] = NAME
        r['unblock'] = lowered                             # Sapphire's collision blocks them; this layout lowers them
        r['_doc'] = (f'New Mauville inside with the {state} barriers lowered (story_fixups): Sapphire\'s '
                     f'{"EventScript_15E5DA (blue switch)" if state == "blue" else "EventScript_15E728 (green switch)"}, '
                     f'loaded instead of the room by map replace event {ALTS[state][1]}.')
    return r, dict(tiles=len(tiles), walls=len(walls), furniture=len(furniture), lowered=len(lowered))

def main():
    sp = os.path.join(LAYOUTS, '_styles_caves_misc.json')
    styles = json.load(open(sp)) if os.path.exists(sp) else {}
    styles.update(STYLES)
    json.dump(styles, open(sp, 'w'), indent=1, ensure_ascii=False)
    for state, name in (('base', NAME), ('blue', ALTS['blue'][0]), ('green', ALTS['green'][0])):
        r, info = recipe(state)
        doc = dict(_doc='New Mauville inside (Sapphire NewMauville_Inside): Black 2\'s P2 Laboratory look. Generated by '
                        'b2tools/caves_misc_newmauville.py from Sapphire\'s metatiles (see its docstring); edit that script.')
        out = dict(doc, **r)
        json.dump(out, open(os.path.join(LAYOUTS, name + '.json'), 'w'), indent=1, ensure_ascii=False)
        print(name, info)

if __name__ == '__main__':
    main()
