"""Check a decomp update before switching to it (notes/POKEBW2_UPGRADE.md section 7): every field script, encounter
table and trainer of every version must assemble to the same bytes with both trees, and every function name
patches/fairy_ui.py looks up must resolve to the same (address, size).

    python3 b2tools/decomp_check.py [OLD [NEW]]     default: external/pokebw2 (the build base's copy) and b2decomp.SRC

Uses the real assemblers (patches/scripts.py assemble, patches/trainers.py assemble_trainer, patches/encounters.py's
command). Prints one line per version and kind, then OK or the differences; exit 1 on any difference."""
import concurrent.futures as cf
import importlib.util, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(HERE, 'patches')]
import b2decomp  # noqa: E402
LLVM = '/opt/homebrew/opt/llvm/bin'


def load(name):
    spec = importlib.util.spec_from_file_location(f'{name}_check', os.path.join(HERE, 'patches', f'{name}.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def encounter(dec, src):
    with tempfile.TemporaryDirectory() as t:
        o, b = os.path.join(t, 'x.o'), os.path.join(t, 'x.bin')
        subprocess.run([f'{LLVM}/clang', '--target=armv5te-none-eabi', '-x', 'assembler-with-cpp', '-c',
                        '-I', f'{dec}/include', '-D', 'BLACK2', '-o', o, os.path.abspath(src)], check=True, cwd=dec)
        subprocess.run([f'{LLVM}/llvm-objcopy', '-O', 'binary', o, b], check=True)
        return open(b, 'rb').read()


def one_version(old, new):
    """This process's version (HOENN_VERSION): assemble everything with both trees."""
    import version
    trees = {}
    for tag, dec in (('old', old), ('new', new)):
        s, t = load('scripts'), load('trainers')
        s.DECOMP = t.DECOMP = dec                  # their assemblers read the module's DECOMP
        trees[tag] = (s, t, dec)

    def run(job):
        kind, src = job
        out = {}
        for tag, (s, t, dec) in trees.items():
            try:
                out[tag] = (s.assemble(src) if kind == 'script' else t.assemble_trainer(src) if kind == 'trainer'
                            else encounter(dec, src))
            except (subprocess.CalledProcessError, SystemExit) as e:
                out[tag] = f'error: {e}'
        return kind, src, out
    jobs = [('script', p) for p in version.overlay(os.path.join(ROOT, 'src', 'field_scripts'), '*.s')]
    jobs += [('encounter', p) for p in version.overlay(os.path.join(ROOT, 'src', 'encounters'), '*.s')]
    jobs += [('trainer', p) for p in version.overlay(os.path.join(ROOT, 'src', 'trainers'), '*.s')]
    counts, bad = {}, []
    with cf.ThreadPoolExecutor(6) as ex:
        for kind, src, out in ex.map(run, jobs):
            c = counts.setdefault(kind, [0, 0]); c[0] += 1
            if out['old'] == out['new'] and not isinstance(out['old'], str): c[1] += 1
            else: bad.append(f'{kind} {os.path.relpath(src, ROOT)}: old {str(out["old"])[:80]} / new {str(out["new"])[:80]}')
    print(version.VERSION + ': ' + ', '.join(f'{k} {v[1]}/{v[0]} identical' for k, v in counts.items()))
    for b in bad: print('  DIFF', b)
    return not bad


def fairy_ui_names(old, new):
    fui = load('fairy_ui')
    names = sorted(set(re.findall(r"'(func_(?:ov\d{3}_)?[0-9a-f]{8})'", open(fui.__file__).read())))
    res = {}
    for dec in (old, new):
        fui.DECOMP, cache = dec, {}
        for n in names:
            m = re.match(r'func_(ov\d{3})_', n); mod = m.group(1) if m else 'arm9'
            cache.setdefault(mod, fui.symbols(mod))
            res.setdefault(n, []).append(cache[mod].get(n))
    bad = [n for n, (a, b) in res.items() if a is None or a != b]
    print(f'fairy_ui: {len(names) - len(bad)}/{len(names)} function names resolve the same' +
          (f'; DIFF {bad}' if bad else ''))
    return not bad


if __name__ == '__main__':
    args = [os.path.normpath(os.path.join(ROOT, a)) for a in sys.argv[1:] if not a.startswith('--')]
    old = args[0] if args else b2decomp.BASE
    new = args[1] if len(args) > 1 else b2decomp.SRC
    if '--one' in sys.argv:
        sys.exit(0 if one_version(old, new) else 1)
    print(f'old {old}\nnew {new}')
    ok = fairy_ui_names(old, new)
    for v in ('sapphire', 'ruby', 'emerald'):
        r = subprocess.run([sys.executable, __file__, old, new, '--one'], env=dict(os.environ, HOENN_VERSION=v),
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        print(r.stdout, end='')
        ok = ok and r.returncode == 0
    print('OK' if ok else 'DIFFERENCES')
    sys.exit(0 if ok else 1)
