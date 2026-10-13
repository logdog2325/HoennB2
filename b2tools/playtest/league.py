"""league.py STATE: from Ever Grande City (Ch11 stage-3 save on the release clone), walk into the Pokemon League and
on to the Champion's room (E4 marked beaten by the kit), battle Steven, play the Hall of Fame scene. Logs Birch's
Pokedex rating line. Screenshots: screenshots/playthrough/league_*.png."""
import sys, os, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt import *
import planner, tour as TO
g = G(sys.argv[1], name='league')
TO.install_watch(g)
g.can_surf = True
shots = 0
def shot(tag):
    global shots
    shots += 1
    g.proof(f'league_{shots:02d}_{tag}.png')
route = ['EverGrandeCity_PokemonLeague', 'EverGrandeCity_Corridor1', 'EverGrandeCity_SidneysRoom', 'EverGrandeCity_Corridor2',
         'EverGrandeCity_PhoebesRoom', 'EverGrandeCity_Corridor3', 'EverGrandeCity_GlaciasRoom', 'EverGrandeCity_Corridor4',
         'EverGrandeCity_DrakesRoom', 'EverGrandeCity_Corridor5', 'EverGrandeCity_ChampionsRoom']
import places as PL
for name in route:
    z = PL.ZONE[name]
    if g.zone() == z: continue
    g.note(f'-> {name} ({z}) from {g.zone()} {g.tile()}')
    ok = g.enter(z) if any(w['dest_zone'] == z for w in rom().entities(g.zone())['warps']) else False
    if not ok:
        # people in the way / scenes: talk through, then try the warp again
        g.adv(); ok = g.enter(z)
    g.adv()
    g.note(f'   now {g.zone()} {g.tile()} ok={ok}')
    if g.zone() != z:
        shot(f'stuck_{z}')
        break
shot('champion_room')
# Steven: talk to him (or his scene starts on entry)
st = [a for a in g.actors() if a['uid'] != 255]
g.note(f'actors in the Champion room: {[(a["uid"], a["x"], a["z"], a["scr"]) for a in st]}')
for a in st:
    g.talk(a['x'], a['z'])
    break
for _ in range(3): g.adv(maxn=2000)
shot('after')
for line in open(os.path.join(LOG, 'transcript_league.txt')):
    if 'seen' in line and 'caught' in line: g.note('RATING LINE: ' + line.strip())
g.save('league_end.dst')
