"""Movement-type audit (v165_fixes 2026-10-11, notes/NPC_MOVEMENT.md): every object of every Sapphire (or Ruby) map,
found in a built ROM at its tile, and the Black 2 move code it got, counted per Sapphire MOVEMENT_TYPE_*. Read-only.

    python3 b2tools/move_audit.py ROM [--rooms ROOMS] [--world WORLD] [--list TYPE]    (HOENN_VERSION=ruby: Ruby)

An object is found when a zone NPC stands on its tile (Sapphire tile + the map's offset: main matrix, warp-only groups,
rooms and caves); scripted people a scene moves elsewhere, item balls, berry trees and objects of maps not built show as
'not found' (or under the code of whatever stands there). Compare with b2tools/move_codes.py's table (expected column).
"""
import os, sys, json, argparse, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import loop_check as LC
import move_codes as MC
import version


def locator(rom, rooms_dir, world_dir):
    L = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps']
    I = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    Z = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    W = json.load(open(os.path.join(world_dir, 'world.json')))
    main = rom.hdr[Z['LittlerootTown']['zone']]['matrix']
    stand = {}
    for s in W['standalone']:
        zone = s['cells'][0]['zone']
        for mp, (ox, oz) in s['origins'].items(): stand[mp] = (rom.hdr[zone]['matrix'], ox, oz)
    def where(mp):
        if mp in L: return main, L[mp]['tile_x'] + 32, L[mp]['tile_z'] + 32
        if mp in stand: return stand[mp]
        if mp in I and version.room_in_version(mp) and os.path.exists(os.path.join(rooms_dir, mp, 'room.json')):
            ox, oz = json.load(open(os.path.join(rooms_dir, mp, 'room.json')))['origin']
            return rom.hdr[I[mp]['zone']]['matrix'], ox, oz
        return None
    return where


def objects():
    for d in sorted(os.listdir(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps'))):
        f = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', d, 'map.json')
        if not os.path.exists(f): continue
        j = json.load(open(f))
        for i, o in enumerate(j.get('object_events') or [], 1):
            yield j['name'], i, o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--rooms', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--world', default=os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'))
    ap.add_argument('--list', default='')
    a = ap.parse_args()
    rom = LC.Rom(a.rom)
    where = locator(rom, a.rooms, a.world)
    by_tile = {}
    for zone, h in enumerate(rom.hdr):
        try: e = rom.entities(zone)
        except Exception: continue
        for i, n in enumerate(e['npcs']): by_tile.setdefault((h['matrix'], n['x'], n['z']), []).append((zone, n))
    got = collections.defaultdict(collections.Counter)
    total = collections.Counter(); found = collections.Counter(); trainers = collections.Counter()
    listing = []
    for mp, lid, o in objects():
        mt = o.get('movement_type', '').replace('MOVEMENT_TYPE_', '')
        total[mt] += 1
        if o.get('trainer_type', 'TRAINER_TYPE_NONE') not in ('TRAINER_TYPE_NONE', '0', 0): trainers[mt] += 1
        w = where(mp)
        here = by_tile.get((w[0], w[1] + o['x'], w[2] + o['y'])) if w else None
        if not here:
            got[mt]['not found'] += 1; continue
        found[mt] += 1
        zone, n = here[0]
        key = f"{n['move']}" + (f" ({n['areaw']}x{n['areah']})" if n['areaw'] or n['areah'] else '') + (' ev%d' % n['evtype'] if n['evtype'] not in (0, 1) else '')
        got[mt][key] += 1
        if a.list and a.list in mt: listing.append(f'  {mp} #{lid} {o["graphics_id"][14:]} range {o.get("movement_range_x")}x{o.get("movement_range_y")}: zone {zone} {n}')
    print(f'{version.NAME + " type":40s} {"objects":>7s} {"trainers":>8s} {"found":>5s}  expected (move_codes)  ROM move codes (area) [count]')
    for mt, c in sorted(total.items(), key=lambda kv: -kv[1]):
        exp = MC.expected(mt) if hasattr(MC, 'expected') else ''
        print(f'{mt:40s} {c:7d} {trainers[mt]:8d} {found[mt]:5d}  {str(exp):21s}  ' +
              ', '.join(f'{k} [{v}]' for k, v in got[mt].most_common()))
    for l in listing: print(l)


if __name__ == '__main__':
    main()
