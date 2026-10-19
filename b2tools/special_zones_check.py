"""Black 2's zone-keyed code tables against Hoenn's zones (special_zones, 2026-10-18; notes/SPECIAL_ZONES.md).

    python3 special_zones_check.py <build dir>     a HOENN_BUILD_DIR's code/ and files/ (before they are moved away):
                                                   no camera, rail, version-swap, gimmick, a/0/8/0#29 or calendar entry
                                                   may name a zone Hoenn uses; the location-evolution lists must be
                                                   special_zones.py's places. Exit 1 on a finding.
    python3 special_zones_check.py --list [zone ...]
                                                   the Hoenn zones on ids Black 2's decompiled C names (PearlB2's
                                                   data/b2_special_zones.json "avoid", read-only), or who uses each zone
Version: HOENN_VERSION (as the build)."""
import os, re, sys, json, struct, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import narcio  # noqa: E402


def _patch(name):
    spec = importlib.util.spec_from_file_location(name + '_', os.path.join(HERE, 'patches', name + '.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def check_build(build):
    ze, sz = _patch('zone_effects'), _patch('special_zones')
    ours, _ = ze.our_zones()
    a = open(os.path.join(build, 'code', 'arm9.bin'), 'rb').read()
    files = os.path.join(build, 'files')
    bad = []
    def u16s(addr, n): return struct.unpack_from(f'<{n}H', a, addr - sz.ARM9)
    evo, want = u16s(sz.EVO_LISTS, 8), tuple(sz.zone_of(n) for _, n in sz.EVO_PLACES)
    print('evolution lists (ice, moss, elec x3, elec2 x3):', evo)
    if evo != want: bad.append(f'evolution lists {evo}, special_zones wants {want}')
    for name, addr, n, mask in (('camera', 0x020900ac, 9, 0x7FF), ('rail spawn', sz.ZONES_WITH_RAILS, sz.RAILS_N, 0xFFFF),
                                ('rail', sz.ZONE_RAIL_ASSIGNMENTS, sz.ASSIGN_N, 0x7FF), ('version swap', 0x0209a348, 6, 0xFFFF)):
        zs = [v & mask for v in u16s(addr, n)]
        print(f'{name}: {zs}')
        if set(zs) & ours: bad.append(f'{name} table names Hoenn zones {sorted(set(zs) & ours)}')
    g = narcio.load(files, 102)[0]
    hit = [struct.unpack_from('<I', g, o)[0] for o in range(0, len(g) - 7, 8)]
    if set(hit) & ours: bad.append(f'gimmick table (a/1/0/2) names {sorted(set(hit) & ours)}')
    f = narcio.load(files, 80)[29]
    hit = [struct.unpack_from('<H', f, o)[0] for o in range(0, len(f) - 3, 4)]
    if set(hit) & ours: bad.append(f'a/0/8/0#29 names {sorted(set(hit) & ours)}')
    c = narcio.load(files, sz.ARC_CALENDAR)[1]
    cal = [struct.unpack_from('<H', c, 2 + 4 * i)[0] for i in range(struct.unpack_from('<H', c, 0)[0])]
    print('calendar zones:', [z for z in cal if z != 0xFFFF])
    if set(cal) & ours: bad.append(f'calendar (a/0/9/6) names {sorted(set(cal) & ours)}')
    print('FINDINGS: ' + '; '.join(bad) if bad else
          'OK: no Black 2 zone table names a Hoenn zone; the evolution lists are special_zones\' places')
    return not bad


def listing(zones):
    P = os.path.expanduser('~/Documents/GitHub/PearlB2')
    sz = json.load(open(P + '/data/b2_special_zones.json'))
    avoid, why = set(sz['avoid']), sz['why']
    names = {}
    for line in open(P + '/external/pokebw2/build/include/generated/constants/zones.h'):
        m = re.match(r'#define (ZONE_\w+) (\d+)', line)
        if m: names[int(m.group(2))] = m.group(1)
    use = {}
    def add(z, who): use.setdefault(int(z), set()).add(who)
    for f, tag in (('hoenn_zones.json', 'S'), ('emerald/hoenn_zones.json', 'E')):
        for k, v in json.load(open(os.path.join(ROOT, 'data', f)))['maps'].items(): add(v['zone'], f'{tag}:{k}')
    for f, tag in (('hoenn_interiors.json', 'S'), ('emerald/hoenn_interiors.json', 'E')):
        for k, v in json.load(open(os.path.join(ROOT, 'data', f)))['rooms'].items():
            if 'zone' in v: add(v['zone'], f'{tag}:{k}')
    for f, tag in ((os.path.expanduser('~/HoennB2_lead/work/world_rel/world.json'), 'Wrel'),
                   (os.path.join(ROOT, 'work', 'agents', 'rustboro_em', 'world', 'world.json'), 'Wem')):
        if os.path.exists(f):
            for k, v in json.load(open(f))['zones'].items(): add(k, f"{tag}:{','.join(v.get('maps', []))}")
    if zones:
        for z in zones: print(z, names.get(z), sorted(use.get(z, [])), why.get(str(z), ''))
        return
    hits = sorted(z for z in use if z in avoid)
    print(len(hits), 'Hoenn zones on ids that Black 2\'s code names')
    for z in hits:
        print(z, names.get(z), '|', ', '.join(sorted({x.split(':', 1)[1] for x in use[z]}))[:90], '|', ' '.join(why[str(z)]))
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from allocate_interiors import deny_avoid, NEVER
    rest = sorted(z for z in avoid if z not in use and z not in deny_avoid() | NEVER)
    print('named in code, no Hoenn zone, not in allocate_zones DENY/AVOID:', rest or 'none')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        listing([int(z) for z in sys.argv[2:]])
    elif len(sys.argv) == 2:
        sys.exit(0 if check_build(sys.argv[1]) else 1)
    else:
        sys.exit(__doc__)
