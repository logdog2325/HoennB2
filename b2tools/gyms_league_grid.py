"""gyms_league agent helper: print a Sapphire map's walkable grid ('.' walk, '#' solid), warp tiles (W), sign (S),
objects (N) and metatile behaviours (hex, non-zero) to plan a recipe.   python3 gyms_league_grid.py MAP [beh]"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models_interior import sapphire_map, ROOT
name = sys.argv[1]
sm = sapphire_map(name)
j = json.load(open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', name, 'map.json')))
mark = {}
for w in sm['warps']: mark[(w['x'], w['y'])] = 'W'
for b in j.get('bg_events', []): mark[(b['x'], b['y'])] = 'S'
for o in j.get('object_events', []): mark[(o['x'], o['y'])] = 'N'
print('    ' + ''.join(f'{x % 10}' for x in range(sm['w'])))
for z in range(sm['h']):
    row = ''.join(mark.get((x, z), '.' if sm['walk'][z][x] else '#') for x in range(sm['w']))
    beh = ' '.join(f'{x}:{sm["beh"][z][x]:x}' for x in range(sm['w']) if sm['beh'][z][x]) if 'beh' in sys.argv[2:] else ''
    print(f'{z:3d} {row}  {beh}')
for o in j.get('object_events', []):
    print('obj', o['x'], o['y'], o['graphics_id'], o['movement_type'], o.get('trainer_type'), o['script'], o.get('flag'))
for b in j.get('bg_events', []):
    print('bg', b['x'], b['y'], b.get('type'), b.get('script'), b.get('player_facing_dir'))
