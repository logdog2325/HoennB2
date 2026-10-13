"""Ported movement lists against Sapphire's (wally_walk, 2026-10-12). Read-only.

    python3 move_compare.py [--all]

Every movement label in src/field_scripts (*.s, scenes/*.inc) whose comment names a Sapphire movement label
(`Mv_X:   // Map_Movement_Y`) is expanded to its tile steps (walks and jumps; turns, delays and balloons ignored) and
compared with pokeruby's list of that name (data/maps/*/scripts.inc, data/scripts/*.inc). A different net
displacement or a different path is listed: such a port puts the walker on other tiles than Sapphire (what made
Wally's tutorial and Rustboro's thief run through buildings). --all also lists lists whose path differs only in order.
(walk_sweep, 2026-10-12) Also matched: the short comment forms "// _StevenLeadPlayerToWallace" and "// _1608D5" / hex
labels, looked up among the Sapphire labels of the file's own map (NNNN_kind_Map.s, scenes/Map[_suffix].inc); Sapphire
lists that fall through into the next label (BattleTower_Corridor_Movement_1608D1 = walk_right + _1608D2) are read to
their step_end; walk_<dir>_start_affine / walk_<dir>_affine count as steps (Kyogre's approach). 206 lists compared.
Known and kept: Dewford's Mv_DT_ExitBoatFromRoute109 (one step shorter on purpose, script_check 2026-10-08).
"""
import os, re, sys, glob, argparse
ROOT = os.path.expanduser('~/Documents/GitHub/HoennB2')
FS = os.environ.get('SCENE_WALKS_FS') or os.path.join(ROOT, 'src', 'field_scripts')
DIRV = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
ORDER = ['up', 'down', 'left', 'right']

def steps_of(lines):
    out = []
    for ln in lines:
        ln = ln.split('//')[0].split('@')[0].strip()
        if not ln: continue
        parts = ln.split(None, 1); op = parts[0]; args = [a.strip() for a in parts[1].split(',')] if len(parts) > 1 else []
        n = int(args[-1], 0) if args and re.fullmatch(r'\d+|0x[0-9a-fA-F]+', args[-1]) else 1
        m = re.match(r'^(walk|walk_slow|walk_fast|walk_faster|walk_fastest|player_run|slide|jump|jump_2|ride_water_current|walk_slow_diag)_(up|down|left|right)$', op)
        a = re.match(r'^walk_(up|down|left|right)_(start_affine|affine)$', op)   # (Kyogre's growing walk, Cave of Origin)
        if m:
            d = DIRV[m.group(2)]; k = 2 if m.group(1) == 'jump_2' else 1
            out += [(d[0] * k, d[1] * k)] * n
        elif a: out += [DIRV[a.group(1)]] * n
        elif op in ('Move', 'hmv') and args:
            c = int(args[0], 0); n = int(args[1], 0) if len(args) > 1 else 1
            if 4 <= c <= 27: out += [DIRV[ORDER[(c - 4) % 4]]] * n
            elif 52 <= c <= 59: d = DIRV[ORDER[c % 4]]; k = 1 if c < 56 else 2; out += [(d[0] * k, d[1] * k)] * n
            elif 92 <= c <= 95: d = DIRV[ORDER[c % 4]]; out += [(d[0] * 3, d[1] * 3)] * n
    return out

def lists(text, sapphire=False):
    """{label: (steps, comment)}. A label inside a list falls through (Sapphire's BattleTower_Corridor_Movement_1608D1
    is one walk_right + all of _1608D2): every open label runs to the next step_end."""
    out = {}
    open_ = []                                     # [(label, comment, body)] still running
    for raw in text.split('\n'):
        m = re.match(r'^([A-Za-z_]\w*)::?\s*(?://\s*(.*)|@.*)?$', raw.strip()) if not raw.startswith((' ', '\t')) else None
        if m:
            # a label with no movement yet before it ends nothing; a label after code that is not a movement starts over
            if open_ and not any(b for _, _, b in open_) or not open_ or all(is_move(b[-1]) for _, _, b in open_ if b):
                open_.append((m.group(1), (m.group(2) or '').strip(), []))
            else:
                open_ = [(m.group(1), (m.group(2) or '').strip(), [])]
            continue
        if not open_: continue
        s = raw.split('//')[0].split('@')[0].strip()
        if s in ('step_end', 'MoveEnd'):
            for lab, com, body in open_: out[lab] = (steps_of(body), com)
            open_ = []; continue
        if not s: continue
        if not is_move(raw): open_ = []; continue
        for _, _, body in open_: body.append(raw)
    return out

def is_move(raw):
    s = raw.split('//')[0].split('@')[0].strip()
    if not s: return True
    op = s.split()[0]
    return bool(re.match(r'^(walk|jump|face|delay|emote|set_|lock|unlock|Move|hmv|slide|ride|player|disable|enable|'
                         r'init|nurse|levitate|fly|restore|clear|\.balign|step)', op))

def sapphire_map_of(path):
    """the Sapphire map a field script file ports: NNNN_kind_Map.s -> Map; scenes/Map[_suffix].inc -> the longest
    Map prefix that is a pokeruby map folder"""
    b = os.path.basename(path)
    m = re.match(r'^\d+_(?:auto|room|cave)_(\w+)\.s$', b)
    if m: return m.group(1)
    stem = b.rsplit('.', 1)[0]
    parts = stem.split('_')
    for k in range(len(parts), 0, -1):
        cand = '_'.join(parts[:k])
        if os.path.isdir(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', cand)): return cand
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--all', action='store_true'); a = ap.parse_args()
    sap, by_map = {}, {}
    for f in glob.glob(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', '*', 'scripts.inc')) + \
             glob.glob(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'scripts', '*.inc')):
        mp = os.path.basename(os.path.dirname(f))
        for k, v in lists(open(f).read(), True).items(): sap[k] = v[0]; by_map.setdefault(mp, {})[k] = v[0]
    ours = []
    for f in sorted(glob.glob(os.path.join(FS, '*.s')) + glob.glob(os.path.join(FS, 'scenes', '*.inc')) +
                    glob.glob(os.path.join(FS, 'ruby', '*.s'))):
        mp = sapphire_map_of(f)
        for lab, (st, com) in lists(open(f).read()).items():
            names = re.findall(r'\b(\w+_Movement_\w+)\b', com)
            if not names and mp in by_map:             # (walk_sweep) the short forms: "_StevenLeadPlayerToWallace",
                tok = re.match(r'^(?:\w+_(?:Movement|EventScript))?(_[0-9A-Za-z_]+?)\b', com)   # "_1608D5", "// 1B6CCC"
                hx = re.search(r'\b_?([0-9A-F]{6})\b', com)
                for t in ([tok.group(1)] if tok else []) + (['_' + hx.group(1)] if hx else []):
                    hit = [k for k in by_map[mp] if k.endswith(t)]
                    if len(hit) == 1: names = hit; break
            if names: ours.append((os.path.relpath(f, FS), lab, st, names[0]))
    n = 0
    for f, lab, st, name in ours:
        if name not in sap: continue
        sp = sap[name]
        if st == sp: continue
        net = lambda s: (sum(d[0] for d in s), sum(d[1] for d in s))
        same_net = net(st) == net(sp)
        if same_net and not a.all: continue
        n += 1
        def short(s):
            out = []; prev = None; c = 0
            for d in s + [None]:
                if d == prev: c += 1; continue
                if prev is not None: out.append(f"{ {(0,-1):'U',(0,1):'D',(-1,0):'L',(1,0):'R'}.get(prev, str(prev)) }{c}")
                prev, c = d, 1
            return ' '.join(out)
        print(f'{f} {lab} ({name}): ours {short(st)} (net {net(st)}) | Sapphire {short(sp)} (net {net(sp)})')
    print('lists compared', len(ours), 'different', n)

if __name__ == '__main__':
    main()
