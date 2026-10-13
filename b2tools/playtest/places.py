"""Names -> zones (outdoor maps and rooms), from the repo's data (read only)."""
import json, os
ROOT = os.path.expanduser('~/Documents/GitHub/HoennB2')
ZONE = {}
for k, v in json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'].items(): ZONE[k] = v['zone']
for k, v in json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms'].items(): ZONE[k] = v['zone']
NAME = {}
for k, v in ZONE.items(): NAME.setdefault(v, k)
def pc_of(town):
    return ZONE.get(f'{town}_PokemonCenter_1F')
