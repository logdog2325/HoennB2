"""Story ids: Sapphire's FLAG_*/VAR_* names -> Black 2 saved flags/works (notes/STORY_PORTING.md "Ids").

    python3 gen_story_ids.py                  data/story_ids.json -> new ids allocated, src/include/hoenn.h rewritten
    python3 gen_story_ids.py --init CHAPTER_IDS.json FREE_RUNS.json     (once: copies the two surveys into the json)

data/story_ids.json holds
  "free":      the saved flags/works Black 2 itself never touches once Unova is replaced (survey 2026-10-06 of the code
               of main + every overlay, all 1289 script files and the zone entities; conservative mode). Taken out:
               flags 0-0x63 / works 0x4000-0x402F (wiped on map change / dynamic sprites), 1100-1499 (the item balls,
               converter/gen_items.py), the trainer defeat flags 1520-2333 (trainer id + 1520, data/hoenn_trainers.json),
               2720-2819 (reset every midnight), 2820-3032 (Black 2's hidden-item flags).
  "daily":     flags of the midnight-reset block 2720-2819 that only replaced Unova zones used: Sapphire's FLAG_DAILY_*
               live here, so Black 2 resets them every day as Sapphire does.
  "chapters":  per story chapter (notes/STORY_PORTING.md), the Sapphire vars/flags it is the first to write ("home").
  "ids":       name -> {"id", "kind" (flag/var), "chapter"}: FIXED once given (saves and scripts depend on them).
  "reserved":  per chapter, spare flags/works its agent may name for ids Sapphire does not have (claim one by adding
               it to "ids" with that chapter and rerunning this script; never take another chapter's).
  "engine":    Sapphire names that are not story flags here (badges, hidden items, Black 2 system flags).
hoenn.h keeps every id it had (same names, same values) and gains the rest, grouped by chapter.

    python3 gen_story_ids.py --claim GROUP NAME ...   give each new FLAG_*/VAR_* NAME the next unused id of GROUP's
                                                      reserve (a chapter, or Emerald), then regenerate as above

Emerald (emerald_s0 2026-10-12, notes/EMERALD_STORY.md S0-4): Pokémon Emerald NDS's own ids (Emerald-only story state and
hide flags: Scott, the Magma Hideout, the Space Center, Sootopolis' legends ...) come from ONE reserve, group "Emerald",
carved once (carve_emerald) out of reserves nobody had used: most of the unused reserve of S_common, Events, Postgame,
Postgame_maps, Berry_trees and Battle_tower (each keeps EMERALD_KEEP), the 6 flags / 15 works no group held, and the
highest EMERALD_FROM_CHAPTER unused flags of Ch0-Ch12 (each chapter keeps the rest of its 16). No id that "ids" names moves;
only the reserve comments in hoenn.h change. An Emerald id is an ordinary define in hoenn.h (unused by Sapphire and Ruby
builds); its name is pokeemerald's (include/constants/flags.h, vars.h) where Emerald has one.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REG = os.path.join(ROOT, 'data', 'story_ids.json')
HDR = os.path.join(ROOT, 'src', 'include', 'hoenn.h')

ITEM_BALLS = range(1100, 1500)
TRAINER_FLAGS = range(1520, 2334)
DAILY_FREE = [f for f in range(2744, 2794) if f not in (2773, 2778)]   # 'code' (the midnight reset) + Unova zones only
SPARE_FLAGS, SPARE_WORKS = 16, 6                                     # per chapter
ORDER = ['Ch0', 'Ch1', 'Ch2', 'Ch3', 'Ch4', 'Ch5', 'Ch6', 'Ch7', 'Ch8', 'Ch9', 'Ch10', 'Ch11', 'Ch12', 'Ch13',
         'S_common', 'Events',      # Events: the in-game event islands (Emerald's flag names; events agent, 2026-10-07)
         'Postgame',                # Postgame: National Dex, Enigma Berry, Jirachi, Celebi, roamers (postgame_scripts, 2026-10-07)
         'Postgame_maps',           # Postgame_maps: Mirage Island, Altering Cave (postgame_maps, 2026-10-07)
         'Berry_trees',             # Berry_trees: daily berry spot k's tree picked today (missing_objects, 2026-10-08)
         'Battle_tower',            # Battle_tower: Sapphire's Battle Tower status/records + the shields (battle_tower, 2026-10-08)
         'Dex_habitat',             # Dex_habitat: the Pokédex Habitat list's visited places, 57 bits (dex_area, 2026-10-11)
         'Emerald']                 # Emerald: Pokémon Emerald NDS's own ids (emerald_s0, 2026-10-12; carve_emerald)
# The Emerald reserve (carve_emerald, once): what each donor group keeps of its unused reserve (flags, works), how many
# of each chapter's unused reserved flags go to Emerald, and how many of the unreserved free ids
EMERALD = 'Emerald'
EMERALD_KEEP = {'S_common': (2, 0), 'Events': (2, 1), 'Postgame': (2, 1), 'Postgame_maps': (2, 1), 'Berry_trees': (2, 1),
                'Battle_tower': (2, 1)}
EMERALD_FROM_CHAPTER = 5                                              # Ch0-Ch12 (Ch13 keeps all 16)
EMERALD_CHAPTERS = [f'Ch{i}' for i in range(13)]
EMERALD_UNRESERVED = (6, 15)                                          # flags, works no group held
# reserved flags the test kits use by number as their "start state written" mark: never carved (scenes/ch5_test.inc
# CH5_TEST_DONE, ch8b_test.inc CH8B_TEST_DONE, ch13_test.inc, postgame_test.inc, battle_tower_test.inc)
TEST_MARKS = {539, 750, 1513, 2432, 2433, 3042}
ENGINE = {   # not allocated as story flags: what a port uses instead
    'FLAG_SYS_POKEMON_GET': ('alias', 2401, "Black 2's own 'has a Pokemon' flag (set after the starter)"),
    'FLAG_SYS_B_DASH': ('alias', 2403, "Black 2's Running Shoes flag (GiveRunningShoes)"),
    'FLAG_SYS_GAME_CLEAR': ('alias', 2400, "Black 2's game-clear flag (set by the Hall of Fame)"),
}
ENGINE_PATTERNS = [
    (r'FLAG_BADGE0(\d)_GET', 'Black 2 badges: TrainerCardAddBadge n / TrainerCardHasBadge var, n with n = gym number - 1 '
                             '(b2tools/patches/hm_free.py checks them for field moves)'),
    (r'FLAG_HIDDEN_ITEM_\w+', "Black 2's hidden items (entries of global script 8000+i, flag 2820+i): a hidden-item "
                              'converter like gen_items.py, not story flags'),
]

def runs(ids):
    ids = sorted(ids); out = []
    for i in ids:
        if out and i == out[-1][1] + 1: out[-1][1] = i
        else: out.append([i, i])
    return out

def fmt_runs(r, hexa=False):
    f = (lambda v: f'0x{v:04X}') if hexa else str
    return ', '.join(f(a) if a == b else f'{f(a)}-{f(b)}' for a, b in r)

def parse_hoenn_h():
    """Existing defines in file order: (name, value, comment)."""
    out = []
    for line in open(HDR):
        m = re.match(r'#define\s+((?:FLAG|VAR)_\w+)\s+(0x[0-9a-fA-F]+|\d+)\s*(?://\s*(.*))?$', line.rstrip())
        if m: out.append((m.group(1), int(m.group(2), 0), (m.group(3) or '').strip()))
    return out

def init(chapter_ids, free_runs):
    ch = json.load(open(chapter_ids)); fr = json.load(open(free_runs))['free']['conservative']
    flags = {i for a, b in fr['flags'] for i in range(a, b + 1)} - set(ITEM_BALLS) - set(TRAINER_FLAGS)
    flags = {f for f in flags if f >= 0x64 and not 2720 <= f <= 3032}
    works = {i for a, b in fr['works'] for i in range(a, b + 1) if i >= 0x4030}
    reg = {'_doc': 'Sapphire FLAG_*/VAR_* -> Black 2 saved flag/work ids. Generated and kept by converter/gen_story_ids.py '
                   '(see its docstring); "ids" are FIXED once given.',
           'free': {'flags': runs(flags), 'works': runs(works), 'source': 'flag/work survey 2026-10-06 (conservative)'},
           'daily': runs(DAILY_FREE),
           'chapters': {k: {'vars': v.get('home_vars', []), 'flags': v.get('home_flags', [])}
                        for k, v in ch.items() if k in ORDER},
           'ids': {}, 'reserved': {}}
    for name, value, comment in parse_hoenn_h():
        reg['ids'][name] = {'id': value, 'kind': 'flag' if name.startswith('FLAG_') else 'var', 'chapter': 'Ch0',
                            **({'note': comment} if comment else {})}
    json.dump(reg, open(REG, 'w'), indent=1)

def carve_emerald(reg):
    """Once: reserved["Emerald"] from the unused reserves (EMERALD_KEEP, EMERALD_FROM_CHAPTER, EMERALD_UNRESERVED). An id is
    unused when no "ids" entry has it (of that kind). Donors keep their lowest unused ids; the carved ids leave their
    reserve lists. Returns (flags, works) carved."""
    ids, reserved = reg['ids'], reg['reserved']
    used = {(v['kind'], v['id']) for v in ids.values()}
    flags, works = [], []
    def carve(group, n_flags_keep=None, n_works_keep=None, n_flags_take=None):
        r = reserved[group]
        fu = [f for f in r['flags'] if ('flag', f) not in used and f not in TEST_MARKS]
        wu = [w for w in r['works'] if ('var', w) not in used]
        tf = fu[n_flags_keep:] if n_flags_take is None else fu[len(fu) - n_flags_take:]
        tw = wu[n_works_keep:] if n_works_keep is not None else []
        r['flags'] = [f for f in r['flags'] if f not in tf]          # (a kept test mark stays in its group)
        r['works'] = [w for w in r['works'] if w not in tw]
        flags.extend(tf); works.extend(tw)
    for g, (kf, kw) in EMERALD_KEEP.items():
        carve(g, kf, kw)
    for ch in EMERALD_CHAPTERS:
        carve(ch, n_flags_take=EMERALD_FROM_CHAPTER)
    taken = {(v['kind'], v['id']) for v in ids.values()} | {('flag', f) for c in reserved.values() for f in c['flags']} \
            | {('var', w) for c in reserved.values() for w in c['works']} | {('flag', f) for f in flags} | {('var', w) for w in works}
    free_f = [i for a, b in reg['free']['flags'] for i in range(a, b + 1) if ('flag', i) not in taken and i not in TEST_MARKS]
    free_w = [i for a, b in reg['free']['works'] for i in range(a, b + 1) if ('var', i) not in taken]
    flags += free_f[:EMERALD_UNRESERVED[0]]; works += free_w[:EMERALD_UNRESERVED[1]]
    reserved[EMERALD] = {'flags': sorted(flags), 'works': sorted(works),
                         'note': 'carved by gen_story_ids.carve_emerald (emerald_s0 2026-10-12, notes/EMERALD_STORY.md S0-4)'}
    return len(flags), len(works)

def claim(reg, group, names):
    """Give each new NAME (FLAG_* -> flag, VAR_* -> work) the next unused id of `group`'s reserve, in "ids"."""
    ids, r = reg['ids'], reg['reserved'][group]
    used = {(v['kind'], v['id']) for v in ids.values()}
    out = []
    for name in names:
        assert re.fullmatch(r'(FLAG|VAR)_\w+', name), f'{name}: not a FLAG_/VAR_ name'
        if name in ids:
            out.append(f'{name} already {ids[name]["id"]} ({ids[name]["chapter"]})'); continue
        kind = 'var' if name.startswith('VAR_') else 'flag'
        pool = r['works' if kind == 'var' else 'flags']
        if name.startswith('FLAG_DAILY_'):     # a midnight-reset flag: the daily pool (as main() gives chapters' FLAG_DAILY_*)
            pool = [i for a, b in reg['daily'] for i in range(a, b + 1)]                      # (emerald_rematch 2026-10-18)
        free = [i for i in pool if (kind, i) not in used]
        if not free: raise SystemExit(f'{group}: no unused reserved {kind} left for {name}')
        ids[name] = {'id': free[0], 'kind': kind, 'chapter': group}
        used.add((kind, free[0]))
        out.append(f'{name} = {free[0]:#06x}' if kind == 'var' else f'{name} = {free[0]}')
    return out

def main(claims=None):
    reg = json.load(open(REG))
    ids, reserved = reg['ids'], reg.setdefault('reserved', {})
    if EMERALD not in reserved:
        nf, nw = carve_emerald(reg)
        print(f'Emerald reserve carved: {nf} flags, {nw} works')
    if claims:
        for line in claim(reg, claims[0], claims[1:]): print('claimed', line)
    taken = {(v['kind'], v['id']) for v in ids.values()} | {('flag', f) for c in reserved.values() for f in c['flags']} \
            | {('var', w) for c in reserved.values() for w in c['works']}
    pool = {'flag': [i for a, b in reg['free']['flags'] for i in range(a, b + 1)],
            'var': [i for a, b in reg['free']['works'] for i in range(a, b + 1)],
            'daily': [i for a, b in reg['daily'] for i in range(a, b + 1)]}
    def take(kind):
        for i in pool[kind]:
            k = 'flag' if kind == 'daily' else kind
            if (k, i) not in taken: taken.add((k, i)); return i
        raise SystemExit(f'no free {kind} id left')
    engine = {}
    for ch in ORDER:
        c = reg['chapters'].get(ch, {'vars': [], 'flags': []})
        for name in c['vars'] + c['flags']:
            if name in ids: continue
            if name in ENGINE: engine[name] = ENGINE[name]; continue
            pat = next((why for p, why in ENGINE_PATTERNS if re.fullmatch(p, name)), None)
            if pat: engine[name] = ('engine', None, pat); continue
            kind = 'var' if name.startswith('VAR_') else 'flag'
            ids[name] = {'id': take('daily' if name.startswith('FLAG_DAILY_') else kind), 'kind': kind, 'chapter': ch}
        if ch not in reserved:
            reserved[ch] = {'flags': [take('flag') for _ in range(SPARE_FLAGS)],
                            'works': [take('var') for _ in range(SPARE_WORKS)]}
    # engine entries an agent claimed by hand (an id the code uses, e.g. caves_misc's map-replacement works 0x4039/
    # 0x403A) are kept: before (dive agent, 2026-10-06) a rerun dropped them
    claimed = {k: v for k, v in reg.get('engine', {}).items() if k not in engine and v.get('what') == 'engine' and v.get('id') is not None}
    reg['engine'] = dict(sorted({**{k: {'what': v[0], 'id': v[1], 'note': v[2]} for k, v in engine.items()}, **claimed}.items()))
    json.dump(reg, open(REG, 'w'), indent=1)

    # hoenn.h: Ch0 (the opening's ids, in their original order and wording) first, then each chapter
    old = {n: c for n, _, c in parse_hoenn_h()}
    lines = ['// Hoenn story variables and flags (Sapphire\'s VAR_*/FLAG_* names) as saved Black 2 works/flags.',
             '// GENERATED by converter/gen_story_ids.py from data/story_ids.json: add ids there (or run the script after',
             '// claiming a reserved id), never by hand. Ids are fixed once given (saves and scripts use them).',
             '// Free ids (survey 2026-10-06: Black 2 code, its 1289 script files and zone data, once Unova is replaced):',
             f'//   flags {fmt_runs(reg["free"]["flags"])}',
             f'//   works {fmt_runs(reg["free"]["works"], True)}',
             '// Not free: flags 0-0x63 and works 0x4000-0x401F (wiped on every map change), works 0x4020-0x402F (dynamic',
             '// NPC sprites), flags 1100-1499 (item balls), 1520-2333 (trainer defeat flags = trainer id + 1520; 2049-2076',
             '// below predate this and their trainer ids 529-556 are never used), 2720-2819 (reset every midnight: only',
             '// FLAG_DAILY_* live there), 2820-3032 (Black 2 hidden items), 2400-2719 except the runs above (Black 2 system).',
             '#pragma once', '']
    def define(name, v):
        val = f'0x{v["id"]:04X}' if v['kind'] == 'var' else str(v['id'])
        note = v.get('note') or old.get(name) or ''
        return f'#define {name:<44} {val:<6}' + (f'  // {note}' if note else '')
    for ch in ORDER:
        mine = [(n, v) for n, v in ids.items() if v['chapter'] == ch]
        if not mine and ch not in reserved: continue
        lines.append(f'// ---- {ch} ' + '-' * 100)
        for kind in ('var', 'flag'):
            for n, v in mine:
                if v['kind'] == kind: lines.append(define(n, v))
        r = reserved.get(ch)
        if r:
            lines.append(f'// {ch} reserved for its own new ids: flags {fmt_runs(runs(r["flags"]))}; works '
                         f'{fmt_runs(runs(r["works"]), True)}')
        lines.append('')
    lines.append('// ---- Black 2 system flags with the same meaning as Sapphire\'s -------------------------------------')
    for n, e in reg['engine'].items():
        if e['what'] == 'alias': lines.append(f'#define {n:<44} {e["id"]:<6}  // {e["note"]}')
    lines.append('// Not flags in this port (use what the note says): ' + '; '.join(
        sorted({e['note'] for e in reg['engine'].values() if e['what'] == 'engine'})))
    open(HDR, 'w').write('\n'.join(lines) + '\n')
    # Sapphire's new-game flags (data/scripts/new_game.inc EventScript_ResetAllMapFlags) as one subroutine for the
    # new-game script (scenes/truck.inc Script_30: VMCall Sub_NewGameFlags)
    src = open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'scripts', 'new_game.inc')).read()
    body = src.split('EventScript_ResetAllMapFlags::', 1)[1].split('return', 1)[0]
    names = re.findall(r'setflag\s+(FLAG_\w+)', body)
    have = [n for n in names if n in ids or reg['engine'].get(n, {}).get('what') == 'alias']
    out = ['// Sapphire\'s new-game flags (pokeruby data/scripts/new_game.inc EventScript_ResetAllMapFlags): every one this',
           '// port has an id for. GENERATED by converter/gen_story_ids.py. Called by the new-game script (scenes/truck.inc).',
           f'// Left out (no id here): {", ".join(n for n in names if n not in have) or "none"}', 'Sub_NewGameFlags:']
    out += [f'    FlagSet {n}' for n in have]
    # Emerald (S0-4): pokeemerald's new-game flags that are Emerald's own ids (group Emerald, e.g. the Scott hide flags),
    # set after Sapphire's, which an Emerald build keeps while it plays Sapphire's scenes (pokeemerald's renamed copies of
    # Sapphire's flags are those). Regenerated with every claim: a claimed name in Emerald's list joins by itself.
    esrc = open(os.path.join(ROOT, 'external', 'pokeemerald', 'data', 'scripts', 'new_game.inc')).read()
    enames = re.findall(r'setflag\s+(FLAG_\w+)', esrc.split('EventScript_ResetAllMapFlags::', 1)[1].split('return', 1)[0])
    emine = [n for n in enames if ids.get(n, {}).get('chapter') == EMERALD and n not in names]
    out += ['#ifdef HOENN_EMERALD',
            '// Emerald\'s own (pokeemerald data/scripts/new_game.inc EventScript_ResetAllMapFlags, ids of group Emerald):',
            f'// {len(emine)} of its {len(enames)}; the rest are Sapphire\'s above under other names, or have no id yet']
    out += [f'    FlagSet {n}' for n in emine] + ['#endif', '    VMReturn']
    open(os.path.join(ROOT, 'src', 'field_scripts', 'scenes', 'new_game_flags.inc'), 'w').write('\n'.join(out) + '\n')
    nf = sum(1 for v in ids.values() if v['kind'] == 'flag'); nv = len(ids) - nf
    print(f'{nv} vars, {nf} flags; reserved per chapter: {SPARE_FLAGS} flags, {SPARE_WORKS} works; engine: {len(reg["engine"])}')

if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--init':
        init(sys.argv[2], sys.argv[3])
    if len(sys.argv) >= 4 and sys.argv[1] == '--claim':
        main(sys.argv[2:])
    else:
        main()
