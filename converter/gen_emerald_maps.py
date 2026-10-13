"""Emerald's maps against Sapphire's: the "maps" -> "emerald" section of data/versions.json (emerald_wp0 2026-10-12,
notes/EMERALD.md; the measurements behind it: notes/EMERALD_PLAN.md 1.1).

    python3 gen_emerald_maps.py            writes data/versions.json "maps" -> "emerald" (every other key is kept)
    python3 gen_emerald_maps.py --check    exit 1 when the section is not current (nothing written)

Read from the two decomps (external/pokeruby, external/pokeemerald: data/maps/*/map.json, data/layouts/layouts.json and
each layout's map.bin); nothing is guessed. A map is the same map when its folder name is the same, or by Emerald's
renames (ALIAS, from the emerald_plan agent's diff_maps.py, each checked there against map_groups.json and the layouts).

  alias       Sapphire folder -> Emerald folder, where Emerald renamed it (version.decomp_map reads it)
  gone        Sapphire maps Emerald dropped (its Battle Tents took the contest halls' places, ...)
  new         Emerald-only maps by group (Battle Frontier, Magma Hideout, Trainer Hill, ...); "event_islands" are already
              in HoennB2 (data/hoenn_event_maps.json)
  name_clash  Emerald-only maps whose folder name is also a Sapphire/Ruby folder of another map (Emerald's
              MagmaHideout_1F is not Ruby's; Emerald's SafariZone_Northeast is a new area, R/S's is Emerald's
              SafariZone_North): their HoennB2 rooms need another name (TODO EMERALD-2: e.g. <Map>_Emerald, as
              the _Ruby room variants)
  ground      Sapphire maps whose Emerald blocks differ (metatile, collision or elevation of any block, or the size):
              {map: "N blocks, M of them collision/elevation (WxH)" or "resized WxH -> WxH"}. Maps
              not listed have the same blocks (their tileset art may still be retouched: EMERALD_PLAN.md 1.1)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R = os.path.join(ROOT, 'external', 'pokeruby')
E = os.path.join(ROOT, 'external', 'pokeemerald')
VERSIONS = os.path.join(ROOT, 'data', 'versions.json')

ALIAS = {
    'Underwater1': 'Underwater_Route124', 'Underwater2': 'Underwater_Route126',
    'Underwater3': 'Underwater_Route127', 'Underwater4': 'Underwater_Route128',
    'FallarborTown_House1': 'FallarborTown_CozmosHouse', 'FallarborTown_House2': 'FallarborTown_MoveRelearnersHouse',
    'SlateportCity_House1': 'SlateportCity_NameRatersHouse', 'SlateportCity_House2': 'SlateportCity_House',
    'SootopolisCity_House8': 'SootopolisCity_LotadAndSeedotHouse',
    'EverGrandeCity_Corridor1': 'EverGrandeCity_Hall1', 'EverGrandeCity_Corridor2': 'EverGrandeCity_Hall2',
    'EverGrandeCity_Corridor3': 'EverGrandeCity_Hall3', 'EverGrandeCity_Corridor4': 'EverGrandeCity_Hall4',
    'EverGrandeCity_Corridor5': 'EverGrandeCity_Hall5', 'EverGrandeCity_PokemonLeague': 'EverGrandeCity_PokemonLeague_1F',
    'CaveOfOrigin_B1F': 'CaveOfOrigin_UnusedRubySapphireMap1', 'CaveOfOrigin_B2F': 'CaveOfOrigin_UnusedRubySapphireMap2',
    'CaveOfOrigin_B3F': 'CaveOfOrigin_UnusedRubySapphireMap3', 'CaveOfOrigin_B4F': 'CaveOfOrigin_B1F',
    'MagmaHideout_1F': 'AquaHideout_UnusedRubyMap1', 'MagmaHideout_B1F': 'AquaHideout_UnusedRubyMap2',
    'MagmaHideout_B2F': 'AquaHideout_UnusedRubyMap3',
    'SingleBattleColosseum': 'BattleColosseum_2P', 'DoubleBattleColosseum': 'BattleColosseum_4P',
    'LinkContestRoom1': 'ContestHall', 'LinkContestRoom2': 'ContestHallBeauty', 'LinkContestRoom3': 'ContestHallTough',
    'LinkContestRoom4': 'ContestHallCool', 'LinkContestRoom5': 'ContestHallSmart', 'LinkContestRoom6': 'ContestHallCute',
    'UnknownMap_25_29': 'UnusedContestHall1', 'UnknownMap_25_30': 'UnusedContestHall2', 'UnknownMap_25_31': 'UnusedContestHall3',
    'UnknownMap_25_32': 'UnusedContestHall4', 'UnknownMap_25_33': 'UnusedContestHall5', 'UnknownMap_25_34': 'UnusedContestHall6',
    'BattleTower_Outside': 'BattleFrontier_OutsideWest', 'BattleTower_Lobby': 'BattleFrontier_BattleTowerLobby',
    'BattleTower_Elevator': 'BattleFrontier_BattleTowerElevator', 'BattleTower_Corridor': 'BattleFrontier_BattleTowerCorridor',
    'BattleTower_BattleRoom': 'BattleFrontier_BattleTowerBattleRoom',
    # R/S's two east Safari areas are Emerald's North/South (92-94% identical blocks); Emerald's NE/SE are the new areas
    'SafariZone_Northeast': 'SafariZone_North', 'SafariZone_Southeast': 'SafariZone_South',
}
GONE = ['FallarborTown_ContestLobby', 'FallarborTown_ContestHall', 'VerdanturfTown_ContestLobby', 'VerdanturfTown_ContestHall',
        'SlateportCity_ContestLobby', 'SlateportCity_ContestHall', 'LilycoveCity_EmptyMap']
# Emerald-only maps by group (first matching rule)
GROUPS = [
    ('event_islands', lambda n: n.startswith(('FarawayIsland', 'BirthIsland', 'NavelRock')) or n == 'AlteringCave'),
    ('battle_tents', lambda n: 'BattleTent' in n),
    ('artisan_cave', lambda n: n.startswith('ArtisanCave')),
    ('battle_frontier', lambda n: n.startswith(('BattleFrontier', 'BattlePyramidSquare'))),
    ('trainer_hill', lambda n: n.startswith('TrainerHill')),
    ('magma_hideout', lambda n: n.startswith('MagmaHideout')),
    ('terra_marine_cave', lambda n: n.startswith(('TerraCave', 'MarineCave')) or n == 'Underwater_MarineCave'),
    ('mirage_tower', lambda n: n.startswith('MirageTower')),
    ('underwater', lambda n: n.startswith('Underwater_Route')),
    ('safari_expansion', lambda n: n.startswith('SafariZone')),
    ('mystery_events_house', lambda n: n.startswith('SootopolisCity_MysteryEventsHouse')),
    ('other', lambda n: True),
]


def maps(root):
    out = {}
    base = os.path.join(root, 'data', 'maps')
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d, 'map.json')
        if os.path.exists(p): out[d] = json.load(open(p))
    return out


def blocks(root, layout_id):
    lays = {l['id']: l for l in json.load(open(os.path.join(root, 'data', 'layouts', 'layouts.json')))['layouts'] if 'id' in l}
    l = lays[layout_id]
    d = open(os.path.join(root, l['blockdata_filepath']), 'rb').read()
    w, h = l['width'], l['height']
    return w, h, [int.from_bytes(d[2 * i:2 * i + 2], 'little') for i in range(w * h)]


def section():
    mr, me = maps(R), maps(E)
    for a, b in ALIAS.items():
        assert a in mr and b in me, (a, b)
    assert all(g in mr for g in GONE)
    kept = {n: ALIAS.get(n, n) for n in mr if n not in GONE}
    missing = sorted(n for n, e in kept.items() if e not in me)
    assert not missing, f'Sapphire maps with no Emerald map and not in GONE: {missing}'
    played = set(kept.values())
    new = {}
    for n in me:
        if n in played: continue
        g = next(k for k, rule in GROUPS if rule(n))
        new.setdefault(g, []).append(n)
    clash = sorted(n for ns in new.values() for n in ns if n in mr)
    ground = {}
    for n, en in sorted(kept.items()):
        wa, ha, a = blocks(R, mr[n]['layout'])
        wb, hb, b = blocks(E, me[en]['layout'])
        if (wa, ha) != (wb, hb):
            ground[n] = f'resized {wa}x{ha} -> {wb}x{hb}'; continue
        diff = sum(x != y for x, y in zip(a, b))
        walk = sum((x >> 10) != (y >> 10) for x, y in zip(a, b))       # collision (bits 10-11) and elevation (12-15)
        if diff: ground[n] = f'{diff} blocks, {walk} of them collision/elevation ({wa}x{ha})'
    doc = ('converter/gen_emerald_maps.py (emerald_wp0): Emerald\'s maps against Sapphire\'s, read from pokeruby and '
           'pokeemerald. alias: Sapphire folder -> Emerald folder (version.decomp_map); gone: Sapphire maps Emerald '
           'dropped; new: Emerald-only maps by group (event_islands are already in HoennB2); name_clash: Emerald-only maps '
           'whose folder name is a different Sapphire/Ruby map (their HoennB2 rooms need another name, TODO EMERALD-2); '
           'ground: Sapphire maps whose Emerald blocks differ (blocks that differ, of them collision/elevation; or the new '
           'size). Phase 0 builds none of this: the Emerald ROM has Sapphire\'s maps '
           '(notes/EMERALD.md).')
    return {'_doc': doc, 'alias': {k: ALIAS[k] for k in sorted(ALIAS)}, 'gone': sorted(GONE),
            'new': {g: new[g] for g, _ in GROUPS if g in new}, 'name_clash': clash, 'ground': ground}


def main():
    cur = json.load(open(VERSIONS, encoding='utf-8'))
    sec = section()
    want = dict(cur)
    want.setdefault('maps', {})
    want['maps'] = dict(want['maps'], emerald=sec)
    text = json.dumps(want, indent=1, ensure_ascii=False) + '\n'
    n_new = sum(len(v) for v in sec['new'].values())
    print(f'Emerald: {len(sec["alias"])} renamed, {len(sec["gone"])} gone, {n_new} new '
          f'({", ".join(f"{g} {len(v)}" for g, v in sec["new"].items())}), {len(sec["name_clash"])} name clashes '
          f'{sec["name_clash"]}, {len(sec["ground"])} kept maps with other blocks '
          f'({sum(1 for v in sec["ground"].values() if v.startswith("resized"))} resized)')
    if '--check' in sys.argv:
        same = open(VERSIONS, encoding='utf-8').read() == text
        print('data/versions.json maps.emerald is', 'current' if same else 'NOT current')
        sys.exit(0 if same else 1)
    open(VERSIONS, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    main()
