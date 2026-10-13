"""report.py [label ...]: summary of log/tour.jsonl: hangs, bad warps, unreachable/silent targets, per-zone counts."""
import sys, json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(os.path.dirname(HERE), 'log')
labels = set(sys.argv[1:])
rows = [json.loads(l) for l in open(os.path.join(LOG, 'tour.jsonl'))]
if labels: rows = [r for r in rows if r.get('label') in labels]
inter = [r for r in rows if r.get('kind') not in ('warp', 'moved')]
warps = [r for r in rows if r.get('kind') == 'warp']
res = collections.Counter(r['result'].split(':')[0] for r in inter)
zones = sorted({r['zone'] for r in inter})
print(f'{len(inter)} interactions in {len(zones)} zones: {dict(res)}; {len(warps)} warps tested, '
      f'{sum(1 for w in warps if not w.get("ok"))} not ok')
print('\n== HANG / STOP')
for r in inter:
    if r['result'].startswith(('HANG', 'STOP')):
        print(f"  zone {r['zone']} {r['name']} {r['kind']} uid {r.get('uid')} idx {r.get('idx')} ({r.get('x')},{r.get('z_')}) "
              f"script {r.get('script')}: {r['result']} shot {r.get('shot')}")
print('\n== warps not ok')
for w in warps:
    if not w.get('ok'):
        print(f"  zone {w['zone']} warp {w.get('warp')} -> {w.get('dest')}: landed {w.get('landed')} {w.get('tile')} exits {w.get('exits')} {w.get('why', '')}")
print('\n== moved by a script')
for r in rows:
    if r.get('kind') == 'moved': print(f"  zone {r['zone']} -> {r.get('to')} after {r.get('after', {}).get('kind')} {r.get('after', {}).get('script')}")
for kind in ('unreachable', 'silent'):
    print(f'\n== {kind}')
    for r in inter:
        if r['result'] == kind:
            print(f"  zone {r['zone']} {r['name']} {r['kind']} uid {r.get('uid')} idx {r.get('idx')} ({r.get('x')},{r.get('z_')}) script {r.get('script')}")
