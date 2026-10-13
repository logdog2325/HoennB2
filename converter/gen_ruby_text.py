"""Ruby's text layer: the lines of our Sapphire text that Ruby words differently, at the same line indices (WP1, notes/RUBY.md
3.2 "Text" and "WP0 layout").

    python3 gen_ruby_text.py            writes src/text/script/ruby/NNNN_*.txt and src/text/ruby/overrides.json
    python3 gen_ruby_text.py --check    compares them with the committed files, writes nothing (exit 1 when not current)
    python3 gen_ruby_text.py --dry      shows every replaced line (S = Sapphire, R = Ruby) and writes nothing
    python3 gen_ruby_text.py --list     like a normal run, and shows every replaced line
    python3 gen_ruby_text.py --report   also lists every Ruby/Sapphire pair of pokeruby that no line of ours matches, and
                                        our lines that name a team, a legendary or an orb and got no twin

Run it after converter/gen_map_content.py (which merges src/text/scenes/*.txt into src/text/script/*.txt) and after
converter/gen_trainers.py (the trainer messages and class names, src/text/system/0381-0383 and 0485, are that tool's: its
Ruby run writes src/text/system/ruby/). Needs no ROM and does not depend on HOENN_VERSION; Sapphire's files are only read.

How a Ruby line is found (every string is pokeruby's own, word for word):
- pokeruby builds both games from one source. A text label is either shared (it holds {EVIL_TEAM}, {GOOD_TEAM},
  {EVIL_LEADER}, {GOOD_LEADER}, {EVIL_LEGENDARY}, {GOOD_LEGENDARY}, {VERSION}, which string_util.c fills per version), or a
  script picks another label with `.ifdef SAPPHIRE ... .else ... .endif` (76 label pairs: Mt. Chimney, Mt. Pyre summit,
  Seafloor Cavern Room 9, Sootopolis, ...). The twin of a Sapphire label is the label at the same position of the .else branch.
- Sapphire line = gen3text.convert(raw string of the Sapphire label, expand=True) for Sapphire = what the converters
  wrote into src/text; Ruby line = the same call on the Ruby twin with Ruby's placeholders (gen3text.convert(version_='ruby')).
- Every line of src/text/script/NNNN_*.txt (all our rooms, scenes and zone files) that equals a Sapphire line is replaced by
  its Ruby line, in a copy src/text/script/ruby/NNNN_<same name>.txt (the whole file, as patches/text.py's overlay replaces by
  file number).
- Every team/legend/orb line of ours matched (--report lists the ones that would not, and the hand-written lines near a
  pokeruby string): there is no hand-made Ruby text in this tool. The 13 trainer messages that differ are in 0381 (gen_trainers).
- The Aqua Hideout rooms (data/versions.json "rooms": Sapphire only) get their Ruby text too: the Ruby ROM carries their
  text files but never shows them, and this keeps the census clean (no "Team Aqua" evil-team line anywhere in the Ruby ROM).
  ruby_maps writes the Magma Hideout rooms' own text files (script/ruby/0287, 0290, 0293); those have no Sapphire file, so
  this tool never writes them.
- src/text/ruby/overrides.json: the place-name line of the hideout ("Magma Hideout").
"""
import os, re, sys, glob, json, collections, difflib, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import version                                                         # noqa: E402
from gen3text import convert                                          # noqa: E402

SCRIPT = os.path.join(ROOT, 'src', 'text', 'script')
SYSTEM = os.path.join(ROOT, 'src', 'text', 'system')
OVERLAY = 'ruby'                          # (this tool writes Ruby's layer; it runs without HOENN_VERSION)
# system files that gen_trainers.py writes (its Ruby run makes src/text/system/ruby/)
TRAINER_FILES = {'0381', '0382', '0383', '0485'}
# words that mark a line as team/legend/orb text (the --report list of unmatched lines)
TEAM_WORDS = re.compile(r"Aqua|Magma|Archie|Maxie|Kyogre|Groudon|Latias|Latios|Blue Orb|Red Orb|Matt\b|Shelly|Tabitha|Courtney|Team ")

# ---- pokeruby: texts and the Sapphire/Ruby label pairs -------------------------------------------------------------------
def pokeruby_files():
    return sorted(glob.glob(f'{RUBY}/data/**/*.inc', recursive=True) + glob.glob(f'{RUBY}/data/**/*.s', recursive=True))

def load_texts():
    """label -> raw .string text. data/text/aqua_misc.s is an unused older copy of aqua_settled.inc: identical labels
    and strings are the same label."""
    text, clash = {}, set()
    for path in pokeruby_files():
        label, cur = None, None
        for line in open(path, encoding='utf-8', errors='replace'):
            m = re.match(r'^(\w+):{1,2}', line)
            if m: label, cur = m.group(1), None; continue
            m = re.match(r'\s*\.string\s+"(.*)"', line)
            if m and label:
                if cur is None: cur = ''
                cur += m.group(1)
                if m.group(1).endswith('$'):
                    if label in text and text[label] != cur: clash.add(label)    # (a data table that reuses a name)
                    text[label] = cur; label = None
    for label in clash: del text[label]
    return text

def ifdef_pairs(texts):
    """[(sapphire label, ruby label, file)] from the `.ifdef SAPPHIRE/RUBY ... .else ... .endif|.endc` blocks of pokeruby's
    scripts: the text labels each branch uses (msgbox, trainerbattle, message, ...), paired by position."""
    pairs = []
    for path in pokeruby_files():
        stack = []
        for line in open(path, encoding='utf-8', errors='replace'):
            s = line.split('@')[0].strip()
            m = re.match(r'\.(ifdef|ifndef)\s+(\w+)', s)
            if m:
                if m.group(2) in ('SAPPHIRE', 'RUBY'):
                    stack.append(dict(ver=True, first_sap=(m.group(2) == 'SAPPHIRE') == (m.group(1) == 'ifdef'),
                                      br=0, lists=[[], []]))
                else:
                    stack.append(dict(ver=False))
                continue
            if re.match(r'\.if\w*\s', s): stack.append(dict(ver=False)); continue
            if s == '.else':
                if stack and stack[-1]['ver']: stack[-1]['br'] = 1
                continue
            if s in ('.endif', '.endc'):
                if not stack: continue
                f = stack.pop()
                if f['ver']:
                    a, b = f['lists']
                    sap, rub = (a, b) if f['first_sap'] else (b, a)
                    if len(sap) != len(rub):
                        raise SystemExit(f'{path}: the SAPPHIRE and RUBY branches use {len(sap)} and {len(rub)} text labels')
                    pairs += [(x, y, path) for x, y in zip(sap, rub)]
                continue
            for fr in reversed(stack):                      # text labels used (or defined) in the innermost version block
                if fr['ver']:
                    for tok in re.findall(r'[A-Za-z_]\w*', s):
                        if tok in texts: fr['lists'][fr['br']].append(tok)
                    break
    return pairs

def twins(texts):
    """Sapphire line -> {Ruby line: [labels]} for every label whose Ruby wording differs."""
    pairs = ifdef_pairs(texts)
    twin = {}
    for s, r, path in pairs:
        if twin.setdefault(s, r) != r: raise SystemExit(f'{s}: two Ruby twins ({twin[s]}, {r})')
    ruby_side = set(twin.values())
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    unknown = collections.Counter()
    for label, raw in texts.items():
        if label in ruby_side and label not in twin: continue        # a Ruby-only label: no Sapphire line of ours
        s_line, u1 = convert(raw, True, 'sapphire')
        r_line, u2 = convert(texts[twin[label]] if label in twin else raw, True, 'ruby')
        for c in u1 + u2: unknown[c] += 1
        if s_line != r_line: out[s_line][r_line].append(label)
    return out, pairs

# ---- our text ------------------------------------------------------------------------------------------------------------
def our_files(kind):
    d = os.path.join(ROOT, 'src', 'text', kind)
    return sorted(glob.glob(os.path.join(d, '*.txt')))

def read_lines(path):
    return open(path, encoding='utf-8').read().split('\n')

def hideout_place_name():
    """(place-name line, name) for MAPSEC_EVIL_TEAM_HIDEOUT with Ruby's team: pokeruby's region map section is
    "{EVIL_TEAM} HIDEOUT"; converter/allocate_zones.py wrote Sapphire's "Aqua Hideout" on this line of text 109."""
    secs = json.load(open(os.path.join(RUBY, 'src', 'data', 'region_map', 'region_map_sections.json')))['map_sections']
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['places']
    out = {}
    for s in secs:
        if '{EVIL_TEAM}' in s['name'] and s['id'] in zones:
            name = s['name'].replace('{EVIL_TEAM}', version.expand_for('ruby')['EVIL_TEAM'])
            out[zones[s['id']]['line']] = ' '.join(w[0] + w[1:].lower() for w in name.split())
    return out

def main():
    check, report, dry = '--check' in sys.argv[1:], '--report' in sys.argv[1:], '--dry' in sys.argv[1:]
    texts = load_texts()
    tw, pairs = twins(texts)
    print(f'{len(texts)} pokeruby labels, {len(pairs)} Sapphire/Ruby label pairs, {len(tw)} Sapphire lines worded differently in Ruby')

    ambiguous = {s: r for s, r in tw.items() if len(r) > 1}
    want, hits = {}, []
    used = set()
    for path in our_files('script'):
        name = os.path.basename(path)
        lines = read_lines(path)
        new = list(lines)
        for i, l in enumerate(lines):
            if l in tw:
                if l in ambiguous:
                    raise SystemExit(f'{name} line {i}: {len(ambiguous[l])} different Ruby wordings: ' +
                                     '; '.join(f'{r!r} <- {labels}' for r, labels in ambiguous[l].items()))
                (r, labels), = tw[l].items()
                used.add(l)
                new[i] = r; hits.append((name, i, l, r, labels[0]))
        if new != lines: want[os.path.join(SCRIPT, OVERLAY, name)] = '\n'.join(new)
    scene_lines = sum(1 for p in our_files('scenes') for l in read_lines(p) if l in tw)
    # system text other than gen_trainers.py's
    sys_hits = []
    for path in our_files('system'):
        name = os.path.basename(path)
        if name[:4] in TRAINER_FILES: continue
        for i, l in enumerate(read_lines(path)):
            if l in tw: sys_hits.append((name, i, l))
    if sys_hits: raise SystemExit(f'system text lines with a Ruby twin: {sys_hits[:5]}: add the file to this tool')
    # the place name (and any other line override) of the Ruby overlay
    ov = {f'system/0109_place_names.txt': {str(k): v for k, v in sorted(hideout_place_name().items())}}
    want[os.path.join(ROOT, 'src', 'text', OVERLAY, 'overrides.json')] = json.dumps(
        {'_doc': 'Ruby text line overrides (patches/text.py applies them after the shared ones). Generated by '
                 'converter/gen_ruby_text.py: the hideout\'s place name with Ruby\'s team.', **ov}, indent=1) + '\n'

    files = sorted({h[0] for h in hits})
    print(f'{len(hits)} lines replaced in {len(files)} script files')
    seg = lambda t: max(len(re.sub(r'\{[0-9a-f:]+\}', 'XXXXXXX' if '{0100' in t else '', x)) for x in re.split(r'\\n|\{be0[01]\}', t))
    print(f'widest line (characters between breaks): Ruby {max(seg(h[3]) for h in hits)}, Sapphire {max(seg(h[2]) for h in hits)}; '
          f'{sum(len(h[3]) - len(h[2]) for h in hits):+d} characters in all')
    print(f'(the same lines are in {scene_lines} lines of src/text/scenes/*.txt, which gen_map_content.py merges into these files)')
    for name, i, s_line, r_line, label in (hits if '--list' in sys.argv[1:] or report or dry else []):
        print(f'  {name} [{i}] {label}\n      S {s_line[:110]!r}\n      R {r_line[:110]!r}')

    if report:
        missing = [s for s in tw if s not in used]
        print(f'\n{len(missing)} Sapphire lines of {len(tw)} not found in any of our script files (not ported, or hand-edited):')
        corpus = [l for p in our_files('script') for l in read_lines(p) if len(l) > 20]
        for s in missing:
            (r, labels), = list(tw[s].items())[:1]
            near = difflib.get_close_matches(s, corpus, n=1, cutoff=0.75)
            print(f'  {labels[0]}: {s[:90]!r}' + (f'\n      NEAR {near[0][:90]!r}' if near else ''))
        print('\nour lines that name a team, legend or orb and have no twin (hand-written or neutral):')
        for path in our_files('script'):
            for i, l in enumerate(read_lines(path)):
                if TEAM_WORDS.search(l) and l not in tw and (os.path.basename(path), i) not in {(h[0], h[1]) for h in hits}:
                    print(f'  {os.path.basename(path)} [{i}] {l[:120]!r}')

    # write / compare; stale generated files go to the Trash
    mine = glob.glob(os.path.join(SCRIPT, OVERLAY, '*.txt'))
    stale = [p for p in mine if p not in want and os.path.basename(p) in {os.path.basename(q) for q in our_files('script')}]
    changed = [p for p, txt in want.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != txt]
    if check:
        if changed or stale:
            print('NOT CURRENT:', [os.path.relpath(p, ROOT) for p in changed + stale]); raise SystemExit(1)
        print(f'Ruby text current: {len(want)} files'); return
    if dry:
        print(f'dry run: {len(changed)} of {len(want)} files would be written'); return
    for p in changed:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(want[p])
    for p in stale:
        shutil.move(p, os.path.join(os.path.expanduser('~/.Trash'), f'{int(time.time())}_{os.path.basename(p)}'))
    print(f'wrote {len(changed)} of {len(want)} files (src/text/script/{OVERLAY}/, src/text/{OVERLAY}/overrides.json); '
          f'{len(stale)} stale moved to the Trash')

if __name__ == '__main__':
    main()
