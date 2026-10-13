"""recheck.py LABEL [result=silent]: for every target of that run with the given result, load the zone's entry state,
stand on each side of the target (people: wait for them to stand still first), face it, press A; log what happens and
save a picture (screenshots/playthrough/recheck/)."""
import sys, os, json, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt import *
import tour as TO
label = sys.argv[1]; want = sys.argv[2] if len(sys.argv) > 2 else 'silent'
OUT = os.path.join(SHOTS, 'recheck'); os.makedirs(OUT, exist_ok=True)
rows = [json.loads(l) for l in open(os.path.join(LOG, 'tour.jsonl'))]
todo = {}
for r in rows:
    if r.get('label') == label and r.get('result') == want and r.get('kind') not in ('warp', 'moved'):
        todo[(r['zone'], r['kind'], r.get('uid'), r.get('idx'))] = r
g = None
res = []
for (z, kind, uid, idx), r in sorted(todo.items()):
    st = os.path.join(TO.TSTATES, f'{label}_z{z}.dst')
    if not os.path.exists(st): continue
    if g is None:
        g = G(st, name=f'recheck_{label}'); g.can_surf = True; g.can_clear = True
    else:
        g.e.load_state(st); g.run(2); g.seen_text = set(g._strbufs_now())
    tx, tz = r['x'], r['z_']
    if uid is not None:
        a = next((a for a in g.actors() if a['uid'] == uid), None)
        if not a: res.append((z, kind, uid, idx, 'not present')); continue
    out = 'nothing'
    for dx, dz in ((0, 1), (0, -1), (-1, 0), (1, 0)):
        if uid is not None:
            a = next((a for a in g.actors() if a['uid'] == uid), None)
            if a: tx, tz = a['x'], a['z']
        c = (tx + dx, tz + dz)
        if not any(R.land(x) for x in g.nav_grid().rec(*c)): continue
        back = (c[0] + dx, c[1] + dz)
        if any(R.land(x) for x in g.nav_grid().rec(*back)) and g.go(*back, tries=4) is True:
            g.walk_dir((-dx, -dz), 1)
        elif g.go(*c, tries=4) is not True: continue
        if g.tile() != c: continue
        g.face((-dx, -dz)); g.press('A', 4, 30)
        started = False
        for _ in range(10):
            if g.event() or g.field() == 0: started = True; break
            g.run(4)
        if started:
            g.run(30); p = os.path.join(OUT, f'{label}_z{z}_{kind}_{uid if uid is not None else idx}.png'); g.screen().save(p)
            texts = g.texts(); g.adv()
            out = f'event from {c}: {[t[:60] for t in texts][:3]}'
            break
    if out == 'nothing':
        p = os.path.join(OUT, f'{label}_z{z}_{kind}_{uid if uid is not None else idx}_nothing.png'); g.screen().save(p)
    res.append((z, kind, uid, idx, out)); print(z, kind, uid, idx, out, flush=True)
json.dump(res, open(os.path.join(LOG, f'recheck_{label}_{want}.json'), 'w'), indent=0)
