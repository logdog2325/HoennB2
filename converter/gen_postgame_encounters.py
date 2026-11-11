"""Post-game wild tables (postgame_dex, 2026-11-09; notes/POSTGAME.md "Post-game dex completion"): after the Champion each
version's exclusives can be caught in the other versions' routes and slots. For every map of the version's post-game
slot edits (data/hoenn_postgame_encounters.json; data/ruby/ and data/emerald/ twins REPLACE its "maps") this writes the
map's post-game twin: the installed table of the map (src/encounters[/<version>]/NNNN_*.s, as the encounters patch
installs it) with the edited slots, into the twin's a/1/2/7 id ("files", fixed once given).

    python3 gen_postgame_encounters.py [--report]      (HOENN_VERSION=ruby|emerald for the other versions; after
                                                        gen_encounters.py / gen_caves.py of that version)

- Output: src/encounters/NNNN_pg_<Map>.s (Sapphire), src/encounters/ruby|emerald/NNNN_pg_<Map>.s (only the files that
  differ from Sapphire's). Stale _pg_ files of the version's folder go to ~/.Trash.
- An edit keeps the slot's levels, which must be the levels the "from" version has for that species in that slot (the
  slots of the three Gen 3 tables line up; the check reads that version's installed table). An edit
  [species, Gen 3 min, Gen 3 max] gives levels of its own on data/level_scaling.json's curve.
- A twin keeps its id's original a/1/2/7 size (232 B: one season; 928 B: the table four times), as gen_encounters.py
  does, so the archive's layout and old savestates' file table stay. Maps that share an id must come out the same.
- The ids must be ones no Hoenn zone of any version uses (checked here against every version's encounter files and
  registries; b2tools/patches/postgame_encounters.py checks the built zone headers too).
- Slot odds are fixed per slot (grass 20/20/10/10/10/10/5/5/4/4/1/1, surf 60/30/5/4/1, Super Rod 40/40/15/4/1): an edit
  never changes a table's total.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import version  # noqa: E402

DATA = os.path.join(ROOT, 'data', 'hoenn_postgame_encounters.json')
ENC = os.path.join(ROOT, 'src', 'encounters')
SECTIONS = {'grass': 'GrassEncounters', 'dark_grass': 'DarkGrassEncounters', 'shaking_grass': 'ShakingGrassEncounters',
            'surf': 'SurfEncounters', 'rippling_surf': 'RipplingSurfEncounters', 'fishing': 'FishingEncounters',
            'rippling_fishing': 'RipplingFishingEncounters'}
RATE_KEY = {'grass': 'grass', 'dark_grass': 'dark_grass', 'shaking_grass': 'shaking_grass', 'surf': 'surf',
            'rippling_surf': 'rippling_surf', 'fishing': 'fishing', 'rippling_fishing': None}   # (the rods: rate 0 by design)
ODDS = {'grass': [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1], 'surf': [60, 30, 5, 4, 1], 'fishing': [40, 40, 15, 4, 1],
        'rippling_fishing': [70, 30, 60, 20, 20]}
TABLE = 232


def load(version_=None):
    """(files {map: twin id}, maps {map: edits}) of a version: the base file's "files", the version's "maps"."""
    v = version_ or version.VERSION
    base = json.load(open(DATA, encoding='utf-8'))
    maps = base['maps']
    if version.OVERLAYS[v]:
        alt = os.path.join(os.path.dirname(DATA), version.OVERLAYS[v], os.path.basename(DATA))
        if os.path.exists(alt):
            maps = json.load(open(alt, encoding='utf-8'))['maps']
    return base['files'], maps


def registry():
    """{map: installed a/1/2/7 id} of every version (data/hoenn_encounters.json + Emerald's own maps)."""
    reg = dict(json.load(open(os.path.join(ROOT, 'data', 'hoenn_encounters.json'))))
    em = os.path.join(ROOT, 'data', 'emerald', 'hoenn_encounters.json')
    if os.path.exists(em):
        reg.update({k: v for k, v in json.load(open(em)).items() if not k.startswith('_')})
    return reg


def installed(fid, version_):
    """The source of a/1/2/7 file fid as version_'s build installs it (its overlay folder first), not a twin."""
    over = version.OVERLAYS[version_]
    for d in ([os.path.join(ENC, over)] if over else []) + [ENC]:
        hits = [p for p in glob.glob(os.path.join(d, f'{fid:04d}_*.s')) if '_pg_' not in os.path.basename(p)]
        if hits:
            assert len(hits) == 1, hits
            return hits[0]
    raise SystemExit(f'gen_postgame_encounters: {version_} installs no table as file {fid}')


def parse(path):
    """One season of a table source: its lines (EncounterRates .. EncountersEnd), the rates, and
    {section: [(line index, species, min, max)]}."""
    lines, out, rates, sec = [], {}, None, None
    for raw in open(path):
        l = raw.rstrip('\n')
        if l.strip().startswith('EncounterRates'):
            if lines: break                      # (a 4-season file repeats the table: the first one)
            rates = dict((k, int(v)) for k, v in re.findall(r'(\w+)=(\d+)', l))
        if rates is None: continue
        lines.append(l)
        m = re.match(r'\s*(\w+Encounters)$', l)
        if m:
            sec = next(k for k, v in SECTIONS.items() if v == m.group(1)); out[sec] = []
        m = re.match(r'\s*Encounter (\w+), (\d+), (\d+)$', l)
        if m: out[sec].append((len(lines) - 1, m.group(1), int(m.group(2)), int(m.group(3))))
        if l.strip() == 'EncountersEnd': break
    assert rates is not None and lines[-1].strip() == 'EncountersEnd', path
    return lines, rates, out


def species_names():
    import b2decomp
    names = set()
    for p in (os.path.join(b2decomp.SRC, 'build', 'include', 'generated', 'constants', 'species.h'),
              os.path.join(b2decomp.SRC, 'include', 'constants', 'species.h')):
        if os.path.exists(p):
            names |= set(re.findall(r'#define (SPECIES_\w+)\s', open(p).read()))
    return names


def scale():
    return {int(k): v for k, v in json.load(open(os.path.join(ROOT, 'data', 'level_scaling.json')))['curve']['table'].items()}


def twin(map_, edits, version_, sizes, species, curve):
    """(season lines of the twin, [(section, slot, odds, old, new)]) of one map in version_."""
    reg = registry()
    lines, rates, secs = parse(installed(reg[map_], version_))
    ref = None
    if edits.get('from'):
        ref = parse(installed(reg[map_], edits['from']))[2]
    changes = []
    lines = list(lines)
    for sec, slots in edits.items():
        if sec in ('from', 'note'): continue
        assert sec in SECTIONS, f'{map_}: unknown section {sec}'
        if RATE_KEY[sec]:
            assert rates.get(RATE_KEY[sec]), f'{map_} {sec}: the table has no {sec} encounters (rate 0)'
        for k, spec in slots.items():
            k = int(k)
            at, old, lo, hi = secs[sec][k]
            if isinstance(spec, list):
                new, lo, hi = spec[0], curve[spec[1]], curve[spec[2]]
            else:
                new = spec
                if ref is not None:
                    _, rs, rlo, rhi = ref[sec][k]
                    assert (rs, rlo, rhi) == (new, lo, hi), \
                        f'{map_} {sec} slot {k}: {edits["from"]} has {rs} {rlo}-{rhi} there, not {new} {lo}-{hi}'
            assert new in species, f'{map_}: unknown species {new}'
            assert new != old, f'{map_} {sec} slot {k}: already {old}'
            lines[at] = f'    Encounter {new}, {lo}, {hi}'
            changes.append((sec, k, ODDS.get(sec, [0] * 12)[k], (old, secs[sec][k][2], secs[sec][k][3]), (new, lo, hi)))
    return lines, changes


def group_name(maps):
    if len(maps) == 1: return maps[0]
    head = os.path.commonprefix(maps).rstrip('_')
    return head + '_' + '_'.join(m[len(head):].strip('_') for m in maps)


def main(argv):
    import narcio
    files, maps = load()
    reg = registry()
    sizes = [len(x) for x in narcio.load(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'), 127)]
    used = set(reg.values())
    for d in (ENC, *[os.path.join(ENC, o) for o in version.OVERLAYS.values() if o]):
        used |= {int(os.path.basename(p)[:4]) for p in glob.glob(os.path.join(d, '*.s')) if '_pg_' not in p}
    bad = sorted({f for f in files.values()} & used)
    assert not bad, f'post-game ids {bad} are tables some version installs'
    species, curve = species_names(), scale()
    out_dir = version.overlay_dir(ENC)
    by_id = {}
    report = []
    for m, edits in maps.items():
        assert m in files, f'{m}: no twin id in {DATA} "files"'
        fid = files[m]
        lines, changes = twin(m, edits, version.VERSION, sizes, species, curve)
        assert sizes[fid] % TABLE == 0 and sizes[fid] // TABLE in (1, 4), (fid, sizes[fid])
        if fid in by_id:
            assert by_id[fid][1] == lines, f'{m} and {by_id[fid][0][0]} share twin {fid} but differ'
            by_id[fid][0].append(m)
        else:
            by_id[fid] = ([m], lines)
        report.append((m, reg[m], fid, edits.get('note', ''), changes))
    written, kept = [], []
    wanted = set()
    for fid, (ms, lines) in sorted(by_id.items()):
        name = group_name(ms)
        text = (f'#include "asm/encounters.inc"\n\n// {name}: the post-game twin (encounter file {fid}) of '
                + ', '.join(f'{m} (file {reg[m]})' for m in ms) + f' in {version.NAME} NDS, read after the Champion\n'
                f'// (src/hoennb2/resident/postgame_enc.c). Generated by converter/gen_postgame_encounters.py from '
                f'data/hoenn_postgame_encounters.json: {maps[ms[0]].get("note", "")}.\n\n'
                + '\n'.join(lines * (sizes[fid] // TABLE)) + '\n')
        path = os.path.join(out_dir, f'{fid:04d}_pg_{name}.s')
        if version.has_overlay():
            shared = glob.glob(os.path.join(ENC, f'{fid:04d}_pg_*.s'))
            if shared and open(shared[0]).read().split('\n\n', 2)[-1] == text.split('\n\n', 2)[-1]:
                kept.append(fid); continue          # the same table as Sapphire's twin: shared
        wanted.add(os.path.basename(path))
        if not os.path.exists(path) or open(path).read() != text:
            open(path, 'w').write(text)
        written.append(f'{name}:{fid}')
    for p in glob.glob(os.path.join(out_dir, '*_pg_*.s')):
        if os.path.basename(p) not in wanted:          # a stale twin: to the Trash, never deleted
            os.rename(p, os.path.join(os.path.expanduser('~/.Trash'), f'{os.path.basename(p)}.{os.getpid()}'))
    print(f'{version.NAME}: {len(written)} post-game tables:', ' '.join(written), f'(shared with Sapphire: {kept})' if kept else '')
    if '--report' in argv:
        for m, base, fid, note, changes in report:
            print(f'| {m} | {base} -> {fid} | ' + '; '.join(
                f'{sec} {k} ({odds} %) {old[0][8:].title()} {old[1]}-{old[2]} -> {new[0][8:].title()}'
                + (f' {new[1]}-{new[2]}' if new[1:] != old[1:] else '') for sec, k, odds, old, new in changes) + ' |')
    return by_id


if __name__ == '__main__':
    main(sys.argv[1:])
