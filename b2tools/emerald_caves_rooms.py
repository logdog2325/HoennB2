"""Emerald's changed dungeon rooms built by the room builder (emerald_caves, 2026-10-12; notes/EMERALD.md "Caves and
dungeons"): Mt. Pyre 2F/3F/6F, the Aqua Hideout B1F and the Fossil Maniac's tunnel on Route 114.

    python3 b2tools/emerald_caves_rooms.py            write the variants below (rerun after editing this file)
    python3 b2tools/emerald_caves_rooms.py --check    only say what would change

Each is a room variant in emerald_rooms' convention (b2tools/emerald_rooms.py): a recipe data/interior_layouts/<Room>_Emerald.json
whose "map" is "pokeemerald/<Emerald folder>" (models_interior.map_source), installed for the Sapphire room in an Emerald
build only (data/versions.json room_variants.emerald; the variant is listed in "rooms" as Emerald's).
  - Mt. Pyre 2F/3F/6F: Emerald moved gravestones (2F 11 tiles, 3F 8, 6F 2: 0x2e6 floor <-> 0x2ee gravestone): the recipe
    from b2tools/facilities_pyre.py's generator run on Emerald's map (its holes, doorways and warps are Sapphire's: the
    zone jsons stay the shared ones).
  - Aqua Hideout B1F: Emerald changes the elevation of 7 tiles at (20-22, 8-10) (the side walls between levels follow
    it): Sapphire's recipe on Emerald's map.
  - Route 114's Fossil Maniac's tunnel: Emerald opens its north end to the Desert Underpass (warp 2 at (6,2), a cave door
    in the back wall) after the game (Route114_FossilManiacsTunnel_OnLoad covers it with rock wall until
    FLAG_SYS_GAME_CLEAR): Sapphire's recipe on Emerald's map (the door drawn open) and the Emerald overlay of its zone
    json (data/interiors/emerald/558.json): warp 2 to the Desert Underpass (zone 375 warp 0) and a boulder (code 0x2004,
    no script: it cannot be pushed) on the tile in front of the door until the game is clear.
  - Sky Pillar 1F-5F: Emerald's clean floors before Rayquaza (see sky_clean below).
"""
import os, sys, json, copy, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'converter'))
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
ZONES = os.path.join(ROOT, 'data', 'interiors')
EM = 'pokeemerald/'
DOC = 'emerald_caves (b2tools/emerald_caves_rooms.py writes this file: edit the script and rerun). '
FLAG_SYS_GAME_CLEAR = 2400        # src/include/hoenn.h (Black 2's game-clear flag)
MODEL_CLAY_ROCK = 206             # data/sprite_map.json OBJ_EVENT_GFX_BREAKABLE_ROCK: Clay Tunnel's rock (drawn in caves; in this
                                  # room zone it blocked but was not drawn [test]: the boulder below instead)
MODEL_BOULDER = 8196              # 0x2004, Hoenn's one-tile boulder (patches/boulder_1x1.py); script 0: it cannot be pushed

OUT, VARIANTS, OVERLAYS = {}, {}, {}

def recipe(name):
    return json.load(open(os.path.join(LAYOUTS, name + '.json')))

def pyre(name):
    """facilities_pyre.recipe() on Emerald's map (its pokeruby Repo read as pokeemerald's)."""
    import gba, facilities_pyre as FP
    orig = gba.Repo
    gba.Repo = lambda root, emerald=False: orig(os.path.join(ROOT, 'external', 'pokeemerald'))
    try: r, _ = FP.recipe(name)
    finally: gba.Repo = orig
    r['map'] = EM + name
    r['_doc'] = (DOC + f"Emerald's {name} (pokeemerald: gravestones moved), b2tools/facilities_pyre.py's recipe on Emerald's "
                 f"map; installed for {name} in an Emerald build. Zone json, holes, warps: Sapphire's.")
    return dict(_doc=r.pop('_doc'), **r)

for n in ('MtPyre_2F', 'MtPyre_3F', 'MtPyre_6F'):
    OUT[n + '_Emerald'] = pyre(n); VARIANTS[n] = n + '_Emerald'

r = copy.deepcopy(recipe('AquaHideout_B1F'))
r['_doc'] = (DOC + "Emerald's AquaHideout_B1F (7 tiles at (20-22,8-10) on another level): Sapphire's recipe on Emerald's "
             "map, installed for AquaHideout_B1F in an Emerald build. " + r.get('_doc', ''))
r['map'] = EM + 'AquaHideout_B1F'
OUT['AquaHideout_B1F_Emerald'] = r; VARIANTS['AquaHideout_B1F'] = 'AquaHideout_B1F_Emerald'

TUNNEL, TUNNEL_ZONE = 'Route114_FossilManiacsTunnel', 558
r = copy.deepcopy(recipe(TUNNEL))
r['_doc'] = (DOC + "Emerald's Route114_FossilManiacsTunnel with its north door to the Desert Underpass (warp 2, (6,2)) drawn "
             "open; closed by a rock object until the game is clear (data/interiors/emerald/558.json). " + r.get('_doc', ''))
r['map'] = EM + TUNNEL
r['block'] = r.get('block', []) + [[6, 1]]      # (Emerald's walkable tile behind the door: unreachable, as Black 2's doors are solid)
OUT[TUNNEL + '_Emerald'] = r; VARIANTS[TUNNEL] = TUNNEL + '_Emerald'
z = json.load(open(os.path.join(ZONES, f'{TUNNEL_ZONE}.json')))
z['_doc'] = (DOC + "Emerald's tunnel: Sapphire's zone json (" + z.get('_doc', '') + ") + warp 2 (Emerald's (6,2) -> "
             "DesertUnderpass warp 0, zone 375) + a boulder (0x2004, no script) on (6,3), hidden by the game-clear flag (pokeemerald "
             "Route114_FossilManiacsTunnel_OnLoad: rock wall over (6,1)-(6,2) until FLAG_SYS_GAME_CLEAR).")
z['warps'] = z['warps'] + [dict(at=[6, 2], to=[375, 0], what='Emerald warp 2 -> DesertUnderpass 0')]
z['npcs'] = z.get('npcs', []) + [dict(uid=100, model=MODEL_BOULDER, script=0, dir=1, at=[6, 3], flag=FLAG_SYS_GAME_CLEAR,
                                      what='the Desert Underpass closed until the game is clear')]
OVERLAYS[TUNNEL_ZONE] = z

# ---- Sky Pillar 1F-5F before Rayquaza: Emerald's clean floors (LAYOUT_SKY_PILLAR_<n>F_CLEAN: no rubble, no cracked floor;
# pokeemerald SkyPillar_<n>F_OnTransition sets them while VAR_SKY_PILLAR_STATE < 2). Emerald's cracked layouts are
# Sapphire's own floors. The clean floor = Sapphire's recipe (b2tools/caves_misc_skypillar.py) without the rubble rocks
# and the cracked-floor mats, its rubble tiles walkable ("unblock": the clean layout's collision); 2F/4F's Emerald zone
# jsons have no fall triggers. Installed in an Emerald build for the whole game until the story switches to the cracked
# floors after Rayquaza (notes/EMERALD.md "Caves and dungeons": alt_rooms + the floors' zone init, the falls).
SKY_ZONES = {1: 164, 2: 165, 3: 166, 4: 167, 5: 168}
def clean_cracks(n):
    """Tiles of LAYOUT_SKY_PILLAR_<n>F_CLEAN whose metatile is a cracked floor (MB_CRACKED_FLOOR / _HOLE): Emerald's clean
    4F keeps five, (0,3) (1,3) (6,4) (7,4) (9,4), the only way down to 3F's middle (its ladder leads to 4F's west half and
    5F); before Rayquaza that is the climb (emerald_ch10, 2026-10-12). pokeemerald's blockdata + metatile behaviours."""
    import struct
    em = os.path.join(ROOT, 'external', 'pokeemerald', 'data')
    lay = next(l for l in json.load(open(os.path.join(em, 'layouts', 'layouts.json')))['layouts']
               if l.get('id') == f'LAYOUT_SKY_PILLAR_{n}F_CLEAN')
    blocks = open(os.path.join(ROOT, 'external', 'pokeemerald', lay['blockdata_filepath']), 'rb').read()
    def attrs(ts):
        d = 'primary' if ts == 'gTileset_General' else 'secondary'
        name = {'gTileset_General': 'general', 'gTileset_Pacifidlog': 'pacifidlog'}[ts]
        return open(os.path.join(em, 'tilesets', d, name, 'metatile_attributes.bin'), 'rb').read()
    pri, sec = attrs(lay['primary_tileset']), attrs(lay['secondary_tileset'])
    out = set()
    for i in range(len(blocks) // 2):
        m = struct.unpack_from('<H', blocks, 2 * i)[0] & 0x3ff
        a = pri if m < 0x200 else sec
        if struct.unpack_from('<H', a, 2 * (m % 0x200))[0] & 0xff in (0xd2, 0xd3):   # MB_CRACKED_FLOOR(_HOLE)
            out.add((i % lay['width'], i // lay['width']))
    return out
def sky_clean(n):
    import models_cave as MC
    base = f'SkyPillar_{n}F'
    sap = MC.sapphire(base)
    cln = MC.sapphire('emerald/' + base, f'LAYOUT_SKY_PILLAR_{n}F_CLEAN')
    unblock = [[x, z] for z in range(sap['h']) for x in range(sap['w']) if cln['walk'][z][x] and not sap['walk'][z][x]]
    gone = [[x, z] for z in range(sap['h']) for x in range(sap['w']) if not cln['walk'][z][x] and sap['walk'][z][x]]
    assert not gone, (base, gone)
    r = copy.deepcopy(recipe(base))
    r['_doc'] = (DOC + f"Emerald's clean Sky Pillar {n}F (LAYOUT_SKY_PILLAR_{n}F_CLEAN, before Rayquaza): Sapphire's recipe without "
                 f"its rubble and cracked-floor mats, the {len(unblock)} rubble tiles walkable. " + r.get('_doc', ''))
    ub = {tuple(t) for t in unblock}
    r['furniture'] = [f for f in r.get('furniture', []) if tuple(f.get('tile', (-1, -1))) not in ub]
    keep = clean_cracks(n)                     # (emerald_ch10) the clean floor's own cracked tiles keep their mat
    mats = [m for m in r.get('mats', []) if (m['rect'][0], m['rect'][1]) in keep and m['rect'][:2] == m['rect'][2:]]
    if mats: r['mats'] = mats
    else: r.pop('mats', None)
    if unblock: r['unblock'] = sorted(set(map(tuple, r.get('unblock', []))) | ub)
    r['unblock'] = [list(t) for t in r.get('unblock', [])]
    if not r['unblock']: r.pop('unblock')
    return r

# After Rayquaza (emerald_ch10, 2026-10-12: VAR_SKY_PILLAR_STATE >= 2) the cracked floors come back: Sapphire's own room is
# the floor's other layout ("alt_rooms", patches/interiors.py: its matrix is loaded instead while map replace event
# SKY_EVENT is set). Black 2 has no free event left, so SKY_EVENT is Mauville Gym's event 3 (work 0x4034): each user's zone
# init sets it to its own state on every entry (Mauville Gym: MG_SHOW_LAYOUT; each floor: SPF_Init in
# src/field_scripts/03NN_room_SkyPillar_<n>F.s, its map script src/field_scripts/emerald/03NN_room_SkyPillar_<n>F_init.s),
# and each zone's a/0/1/0 entries name only its own matrix. 2F/4F keep Sapphire's falls with a condition: temporary work
# SKY_FALL_WORK = 1, which the floor's zone init sets only for the cracked floor.
SKY_EVENT, SKY_FALL_WORK = 3, 0x4001
for n in range(1, 6):
    OUT[f'SkyPillar_{n}F_Emerald'] = sky_clean(n); VARIANTS[f'SkyPillar_{n}F'] = f'SkyPillar_{n}F_Emerald'
    z = json.load(open(os.path.join(ZONES, f'{SKY_ZONES[n]}.json')))
    z['_doc'] = (DOC + f"Emerald's Sky Pillar {n}F: the clean floor (the room variant) until Rayquaza, then Sapphire's cracked "
                 f"room as its other layout (alt_rooms, map replace event {SKY_EVENT} set by the floor's zone init, emerald_ch10)"
                 + (f"; Sapphire's {len(z['triggers'])} falls of the cracked floor fire only while work {SKY_FALL_WORK:#x} is 1 "
                    "(the zone init: the cracked floor)" if z.get('triggers') else '') + '.')
    clean = clean_cracks(n)                    # (the clean floor's own cracks: their falls work in both layouts)
    z['triggers'] = [t if tuple(t['at']) in clean else dict(t, var=SKY_FALL_WORK, value=1) for t in z.get('triggers', [])]
    if clean: z['_doc'] += f" Its clean layout keeps {len(clean)} cracked tiles ({sorted(clean)}), whose falls always work (Emerald's way to 3F's middle and 5F)."
    z['alt_rooms'] = [dict(room=f'SkyPillar_{n}F', event=SKY_EVENT)]
    OVERLAYS[SKY_ZONES[n]] = z

def write_json(p, d, check):
    s = json.dumps(d, indent=1, ensure_ascii=False) + '\n'
    old = open(p, encoding='utf-8').read() if os.path.exists(p) else None
    if old == s: return False
    print(('would write ' if check else 'wrote ') + os.path.relpath(p, ROOT))
    if not check:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(s)
    return True

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); a = ap.parse_args()
    for n, r in OUT.items(): write_json(os.path.join(LAYOUTS, n + '.json'), r, a.check)
    for zone, z in OVERLAYS.items(): write_json(os.path.join(ZONES, 'emerald', f'{zone}.json'), z, a.check)
    p = os.path.join(ROOT, 'data', 'versions.json')
    v = json.load(open(p, encoding='utf-8'))          # (read just before writing: other agents edit this file too)
    v.setdefault('room_variants', {}).setdefault('emerald', {}).update(VARIANTS)
    for n in OUT: v['rooms'][n] = 'emerald'
    s = json.dumps(v, indent=1) + '\n'
    if s != open(p, encoding='utf-8').read():
        print(('would update ' if a.check else 'updated ') + 'data/versions.json (room_variants.emerald, rooms)')
        if not a.check: open(p, 'w', encoding='utf-8').write(s)

if __name__ == '__main__':
    main()
