"""World tour: depth-first through every room reachable by warps from where the player stands, touring each zone
(tour.Tour.zone), testing every warp (lands on a walkable tile, the player can move), then coming back by the room's own
exit (or the parent's saved state when the way back is one-way). Progress persists in log/explore_<label>.json."""
import os, json, time
from pt import *
import tour as TO
import places as PL

MAIN = 416


class Explorer:
    def __init__(self, g, label, skip=()):
        self.g = g; self.label = label
        self.T = TO.Tour(g, label=label)
        self.path = os.path.join(LOG, f'explore_{label}.json')
        self.st = json.load(open(self.path)) if os.path.exists(self.path) else {'toured': [], 'warps': {}}
        self.skip = set(skip)
        self.T.sigs = self.st.setdefault('sigs', {})
        self.gyms = False          # gyms: warps tested, people not (the story agents played them)

    def persist(self):
        json.dump(self.st, open(self.path, 'w'), indent=0)

    def matrix(self, z): return rom().hdr[z]['matrix']

    def warp_ok(self, z0, i, w):
        """After taking warp i of z0: did we land in its zone on a tile we can walk off?"""
        g = self.g
        z = g.zone(); t = g.tile()
        grid = g.nav_grid()
        moves = sum(1 for d in DIRK if step_options(grid, t, g.height(), d, 'land'))
        res = dict(zone=z0, warp=i, dest=w['dest_zone'], dest_warp=w['dest_warp'], landed=z, tile=t,
                   exits=moves, ok=(z == w['dest_zone'] and moves > 0))
        self.T.log(kind='warp', **res)
        if not res['ok']:
            res['shot'] = self.T.shot(f'warp_z{z0}_{i}_{int(time.time())}.png')
            g.note(f'!!! warp problem: {res}')
        return res

    def back_to(self, z):
        g = self.g
        ws = rom().entities(g.zone())['warps']
        for i, w in enumerate(ws):
            if w['dest_zone'] == z and own_warp(g, w):
                if g.warp(i) and g.zone() == z:
                    g.adv(); return True
        return False

    def explore(self, depth=0, came_from=None):
        g = self.g
        z = g.zone()
        if z < 0: return
        gym = 'Gym' in PL.NAME.get(z, '') and not self.gyms
        if z not in self.st['toured'] and z not in self.skip and not gym:
            summary = self.T.zone()
            self.st['sigs'] = self.T.sigs
            self.st['toured'].append(z)
            self.st.setdefault('unreach', {})[str(z)] = [k for k in self.T.last_unreached]
            self.persist()
        elif self.st.get('unreach', {}).get(str(z)):
            # back in a toured zone (maybe another part of it): retry what was out of reach
            keys = set(self.st['unreach'][str(z)])
            self.T.zone(only=keys)
            self.st['unreach'][str(z)] = [k for k in self.T.last_unreached]
            self.persist()
        here_state = os.path.join(TO.TSTATES, f'{self.label}_back_z{z}.dst')
        g.wait_idle(); g.e.save_state(here_state)
        ws = rom().entities(z)['warps']
        for i, w in enumerate(ws):
            dz = w['dest_zone']
            key = f'{z}:{i}'
            if key in self.st['warps']: continue
            if not own_warp(g, w): continue
            if dz in self.skip: continue
            if self.matrix(dz) == MAIN and self.matrix(z) == MAIN: continue      # outdoor walking, not a room
            if dz == came_from and dz in self.st['toured']:
                # the way back: test it once without going further
                pass
            if g.zone() != z:
                g.e.load_state(here_state); g.run(2)
            g.note(f'{"  " * depth}warp {i} of {z} {PL.NAME.get(z, "")} -> {dz} {PL.NAME.get(dz, "")}')
            ok = False
            try:
                ok = g.warp(i)
                if not ok and g.zone() == z:
                    # not reachable on foot from here: plan through other maps' warps, then try again
                    import planner
                    t = (w['tile_x'], w['tile_z'] + 1)
                    if planner.travel(g, z, t) or g.zone() == z:
                        ok = g.warp(i)
            except Exception as ex:
                g.note(f'warp exception {ex}')
            if not ok or g.zone() != dz:
                self.st['warps'][key] = 'not taken'
                self.T.log(kind='warp', zone=z, warp=i, dest=dz, ok=False, landed=g.zone(), tile=g.tile(), why='not taken')
                self.persist()
                g.e.load_state(here_state); g.run(2)
                continue
            g.adv()
            r = self.warp_ok(z, i, w)
            self.st['warps'][key] = 'ok' if r['ok'] else 'bad'
            self.persist()
            if r['ok'] and (dz not in self.st['toured'] or self.st.get('unreach', {}).get(str(dz)) or
                            any(f'{dz}:{k}' not in self.st['warps'] for k, _ in enumerate(rom().entities(dz)['warps']))):
                self.explore(depth + 1, came_from=z)
            # come back
            if g.zone() != z and not self.back_to(z):
                g.note(f'{"  " * depth}no way back to {z} from {g.zone()}: reload')
            g.e.load_state(here_state); g.run(2)
        return
