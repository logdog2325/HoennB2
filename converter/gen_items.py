"""Sapphire's item balls as Black 2 item balls.

    python3 gen_items.py        -> data/hoenn_items.json, src/field_scripts/1240_items.s

Black 2's item balls (checked in its zone entity files and script file 1240): an NPC with object code 110, script id
6999 + n for the file's Script_n (global ids count from 0: 7000 = Script_1; tested) and a saved flag (Black 2 uses
script - 5900, i.e. 1099 + n). Global scripts 7000-7799 are file 1240 (GLOBAL_SCRIPT_TABLE, ov012
0x0216af98, read with b2tools/armdis.py); its Script_n sets 0x800c = item, 0x800d = count and calls Script_401, which
gives the item and sets the calling NPC's own flag (ActorGetSpawnFlag) so the ball stays gone. No new-game script sets
flags 1100-1500 (1242.s). So each Sapphire item ball (pokeruby data/item_ball_scripts.inc, `finditem ITEM, count`)
gets a slot n (1-400, fixed once given) and Black 2's item:
- by name (Black 2 spellings: Parlyz Heal, Thunderstone);
- TMs/HMs by their move, through Black 2's TM/HM move table (arm9 0x02090c84: TM01-92, HM01-06, TM93-95); a Gen 3 TM
  whose move is no Gen 5 TM keeps its number (stand-in, listed in 'notes');
- Gen 3 mail -> a Gen 5 mail (stand-in); key items Black 2 lacks (Scanner) are left for the story work.
"""
import os, re, json, struct, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import version  # noqa: E402  (HOENN_VERSION=emerald: main_emerald)
ALIAS = {'ITEM_PARALYZE_HEAL': 'ITEM_PARLYZ_HEAL', 'ITEM_THUNDER_STONE': 'ITEM_THUNDERSTONE'}
MAIL = ['ITEM_GREET_MAIL', 'ITEM_FAVORED_MAIL', 'ITEM_RSVP_MAIL', 'ITEM_THANKS_MAIL', 'ITEM_INQUIRY_MAIL',
        'ITEM_LIKE_MAIL', 'ITEM_REPLY_MAIL', 'ITEM_BRIDGE_MAIL_S', 'ITEM_BRIDGE_MAIL_D']
TM_TABLE = 0x02090c84

def b2_items():
    return {k: int(v) for k, v in re.findall(r'#define (ITEM_\w+)\s+(\d+)', open(f'{B2}/include/constants/items.h').read())}

def tm_items():
    """MOVE_X -> Black 2 TM/HM item constant."""
    arm9 = open(f'{B2}/build/b2_us/build/arm9.bin', 'rb').read()
    moves = struct.unpack_from('<101H', arm9, TM_TABLE - 0x02004000)
    names = {int(v): k for k, v in re.findall(r'#define (MOVE_\w+)\s+(\d+)', open(f'{B2}/include/constants/moves.h').read())}
    out = {}
    for i, m in enumerate(moves):
        item = f'ITEM_TM{i + 1:02d}' if i < 92 else f'ITEM_HM{i - 91:02d}' if i < 98 else f'ITEM_TM{i - 5:02d}'
        out[names[m]] = item
    return out

def map_item(name, items, tms, notes, mail_i):
    if name in items: return name
    if name in ALIAS: return ALIAS[name]
    m = re.match(r'ITEM_(TM|HM)(\d\d)_(\w+)', name)
    if m:
        move = 'MOVE_' + m.group(3).replace('SOLARBEAM', 'SOLAR_BEAM')
        if move in tms: return tms[move]
        stand = f'ITEM_{m.group(1)}{m.group(2)}'
        notes.append(f'{name}: {move} is no Gen 5 TM/HM; stand-in {stand}')
        return stand
    if name.endswith('_MAIL'):                      # one Gen 5 mail per Gen 3 mail type, in order of first use
        if name not in mail_i[1]:
            mail_i[1][name] = MAIL[len(mail_i[1]) % len(MAIL)]
            notes.append(f'{name}: Gen 3 mail; stand-in {mail_i[1][name]}')
        return mail_i[1][name]
    notes.append(f'{name}: not in Black 2 (key item?) - skipped')
    return None

def main():
    items, tms = b2_items(), tm_items()
    src = open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'item_ball_scripts.inc')).read()
    balls = re.findall(r'^(\w+)::.*\n\s*finditem (ITEM_\w+)(?:,\s*(\d+))?', src, re.M)
    reg_path = os.path.join(ROOT, 'data', 'hoenn_items.json')
    old = json.load(open(reg_path))['balls'] if os.path.exists(reg_path) else {}
    used = {v['n'] for v in old.values()}
    notes, mail_i, balls_out = [], [0, {}], {}
    nxt = 1
    for label, item, qty in balls:
        b2 = map_item(item, items, tms, notes, mail_i)
        if not b2: continue
        if label in old: n = old[label]['n']
        else:
            while nxt in used: nxt += 1
            n = nxt; used.add(n)
        balls_out[label] = dict(n=n, sapphire=item, item=b2, count=int(qty or 1), script=6999 + n, flag=1099 + n)
    assert max(v['n'] for v in balls_out.values()) <= 400
    json.dump({'_doc': __doc__.strip().split('\n\n')[0], 'balls': balls_out, 'notes': notes},
              open(reg_path, 'w'), indent=1)
    # script file 1240 = Black 2's own, with our slots' item and count
    s = open(f'{B2}/data/field_scripts/1240.s').read()
    by_n = {v['n']: v for v in balls_out.values()}
    def fix(m):
        n = int(m.group(1)); body = m.group(2)
        if n not in by_n: return m.group(0)
        v = by_n[n]
        body = re.sub(r'WorkSetConst 0x800c, \w+', f'WorkSetConst 0x800c, {items[v["item"]]}', body, count=1)
        body = re.sub(r'WorkSetConst 0x800d, \w+', f'WorkSetConst 0x800d, {v["count"]}', body, count=1)
        return f'Script_{n}:{body}'
    s = re.sub(r'^Script_(\d+):((?:\n(?!Script_|L_).*)*)', fix, s, flags=re.M)
    head = ('// Black 2\'s item ball scripts (file 1240) with Hoenn items in the slots of data/hoenn_items.json.\n'
            '// Generated by converter/gen_items.py from external/pokebw2/data/field_scripts/1240.s.\n')
    open(os.path.join(ROOT, 'src', 'field_scripts', '1240_items.s'), 'w').write(head + s)
    print(f'{len(balls_out)} item balls, {len(notes)} notes:', *notes, sep='\n  ')

# ---- Emerald (HOENN_VERSION=emerald python3 gen_items.py [--check]; emerald_data 2026-10-12, notes/EMERALD.md EMERALD-1) ----
# pokeemerald's item balls (data/scripts/item_ball_scripts.inc, the objects of data/maps/*/map.json that run them):
# - a ball at the same place as a Sapphire ball (the HoennB2 map Emerald's map plays, same tile) takes that ball's slot n,
#   so the ball Sapphire's world places there (script 6999 + n, flag 1099 + n) gives Emerald's item;
# - the others get free slots (1-400, none Sapphire's), placed once the Emerald world places Emerald's objects
#   (EMERALD-2/3: gen_map_content.py reads this registry by pokeemerald's script label);
# - Sapphire's balls Emerald does not have keep their slot and item (they stand in the Sapphire world an Emerald build
#   still shows until phase 2).
# Writes data/emerald/hoenn_items.json (registry: pokeemerald label -> slot; deep-merged over Sapphire's) and
# src/field_scripts/emerald/1240_items.s (file 1240 with every slot's Emerald item).
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')

def emerald_tm_names():
    """pokeemerald ITEM_TM_<MOVE> / ITEM_HM_<MOVE> -> pokeruby's ITEM_TMnn_<MOVE> / ITEM_HMnn_<MOVE> (map_item's form),
    numbered by include/constants/tms_hms.h FOREACH_TM / FOREACH_HM."""
    src = open(os.path.join(EMERALD, 'include', 'constants', 'tms_hms.h')).read()
    out = {}
    for kind in ('TM', 'HM'):
        blk = src[src.index(f'#define FOREACH_{kind}(F)'):]
        blk = blk[:blk.index('\n\n')] if '\n\n' in blk else blk
        for n, mv in enumerate(re.findall(r'F\((\w+)\)', blk), 1):
            out[f'ITEM_{kind}_{mv}'] = f'ITEM_{kind}{n:02d}_{mv}'
    return out

def emerald_place(root, script):
    """{script label: (map folder, x, y, flag)} of the object events of root's maps."""
    out = {}
    base = os.path.join(root, 'data', 'maps')
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d, 'map.json')
        if not os.path.exists(p): continue
        for o in json.load(open(p)).get('object_events') or []:
            if o.get('script') in script: out.setdefault(o['script'], (d, o['x'], o['y'], o.get('flag')))
    return out

def emerald_maps():
    """(hoenn(map) -> the HoennB2 map an Emerald map plays or None, built: the maps this build has) as gen_trainers."""
    m = version.versions_json().get('maps', {}).get('emerald', {})
    back = {e: s for s, e in m.get('alias', {}).items()}
    clash = set(m.get('name_clash', ()))
    def hoenn(e): return e + '_Emerald' if e in clash else back.get(e, e)      # (name_clash: EMERALD.md's naming)
    built = set(json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'])
    built |= {r for r, v in json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms'].items()
              if v.get('status') != 'link'}
    only = {x for g in m.get('new', {}).values() for x in g}
    return hoenn, built, only

def _write_or_check(want, check):
    changed = [p for p, t in want.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if check:
        if changed: raise SystemExit(f'NOT CURRENT: {[os.path.relpath(p, ROOT) for p in changed]}')
        print(f'current: {len(want)} files'); return
    for p in changed:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(want[p])
    print(f'{len(changed)} files written: {[os.path.relpath(p, ROOT) for p in changed]}')

def main_emerald():
    check = '--check' in sys.argv[1:]
    items, tms = b2_items(), tm_items()
    sap = json.load(open(os.path.join(ROOT, 'data', 'hoenn_items.json')))
    mail = dict(re.match(r'(ITEM_\w+_MAIL): Gen 3 mail; stand-in (ITEM_\w+)', n).groups() for n in sap['notes'] if 'Gen 3 mail' in n)
    tmn = emerald_tm_names()
    hoenn, built, only = emerald_maps()
    src = open(os.path.join(EMERALD, 'data', 'scripts', 'item_ball_scripts.inc')).read()
    balls = re.findall(r'^(\w+)::.*\n\s*finditem (ITEM_\w+)(?:,\s*(\d+))?', src, re.M)
    e_at = emerald_place(EMERALD, {b[0] for b in balls})
    r_src = open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'item_ball_scripts.inc')).read()
    r_at = emerald_place(os.path.join(ROOT, 'external', 'pokeruby'), {l for l, _, _ in re.findall(
        r'^(\w+)::.*\n\s*finditem (ITEM_\w+)(?:,\s*(\d+))?', r_src, re.M)})
    sap_slot = {(m, x, y): (lab, sap['balls'][lab]) for lab, (m, x, y, _) in r_at.items() if lab in sap['balls']}
    reg_path = os.path.join(ROOT, 'data', 'emerald', 'hoenn_items.json')
    old = json.load(open(reg_path))['balls'] if os.path.exists(reg_path) else {}
    used = {v['n'] for v in sap['balls'].values()} | {v['n'] for v in old.values()}
    notes, out, nxt, paired = [], {}, 1, set()
    unused = sorted(l for l, _, _ in balls if l not in e_at)       # finditem scripts no object runs (pokeemerald: Unused)
    for label, item, qty in balls:
        if label in unused: continue
        name = tmn.get(item, item)
        b2 = mail.get(name) or map_item(name, items, tms, notes, [0, dict(mail)])
        if not b2: continue
        em, x, y, flag = e_at.get(label, (None, None, None, None))
        hm = hoenn(em) if em else None
        twin = sap_slot.get((hm, x, y))
        if twin: n = twin[1]['n']; paired.add(twin[0])
        elif label in old: n = old[label]['n']
        else:
            while nxt in used: nxt += 1
            n = nxt; used.add(n)
        out[label] = dict(n=n, emerald=item, item=b2, count=int(qty or 1), script=6999 + n, flag=1099 + n,
                          map=hm, emerald_map=em, at=[x, y], emerald_flag=flag, sapphire_twin=twin[0] if twin else None,
                          built=bool(hm and hm in built), emerald_only_map=em in only)
    assert max(v['n'] for v in out.values()) <= 400
    gone = sorted(l for l in sap['balls'] if l not in paired)
    same = sum(1 for v in out.values() if v['sapphire_twin'] and sap['balls'][v['sapphire_twin']]['item'] == v['item'])
    want = {reg_path: json.dumps({
        '_doc': 'Emerald overlay of data/hoenn_items.json (version.load_json deep merge), written by converter/gen_items.py '
                'with HOENN_VERSION=emerald: pokeemerald\'s item balls by script label. A ball on the tile of a Sapphire ball '
                '(sapphire_twin) takes its slot n (so the Sapphire world\'s ball there gives Emerald\'s item); the others '
                'have free slots and are placed with the Emerald world (map = the HoennB2 map, built = this build has it). '
                'sapphire_only: Sapphire balls Emerald does not have (their slots keep Sapphire\'s item).',
        'balls': dict(sorted(out.items(), key=lambda kv: kv[1]['n'])), 'sapphire_only': gone, 'unused_scripts': unused,
        'notes': sorted(set(notes))}, indent=1) + '\n'}
    # file 1240: Sapphire's slots, with Emerald's items in the slots Emerald's balls take
    s = open(os.path.join(ROOT, 'src', 'field_scripts', '1240_items.s')).read()
    by_n = {v['n']: v for v in out.values()}
    def fix(m):
        n = int(m.group(1)); body = m.group(2)
        if n not in by_n: return m.group(0)
        v = by_n[n]
        body = re.sub(r'WorkSetConst 0x800c, \w+', f'WorkSetConst 0x800c, {items[v["item"]]}', body, count=1)
        body = re.sub(r'WorkSetConst 0x800d, \w+', f'WorkSetConst 0x800d, {v["count"]}', body, count=1)
        return f'Script_{n}:{body}'
    s = re.sub(r'^Script_(\d+):((?:\n(?!Script_|L_).*)*)', fix, s, flags=re.M)
    s = s.replace('// Generated by converter/gen_items.py from external/pokebw2/data/field_scripts/1240.s.\n',
                  '// Generated by converter/gen_items.py from external/pokebw2/data/field_scripts/1240.s.\n'
                  '// Emerald (HOENN_VERSION=emerald): the slots of data/emerald/hoenn_items.json hold Emerald\'s items.\n', 1)
    want[os.path.join(ROOT, 'src', 'field_scripts', 'emerald', '1240_items.s')] = s
    unbuilt = sorted(f'{v["emerald_map"]} ({v["at"][0]},{v["at"][1]}) {v["emerald"]}' for v in out.values() if not v['built'])
    print(f'Emerald item balls: {len(out)} ({len(out) - sum(1 for v in out.values() if v["sapphire_twin"])} new places; '
          f'{sum(1 for v in out.values() if v["sapphire_twin"])} on a Sapphire ball\'s tile, {same} with the same item); '
          f'Sapphire balls Emerald does not have: {len(gone)}; slots used up to {max(used)} of 400; '
          f'scripts no object runs: {len(unused)}')
    print(f'  on maps this build does not have ({len(unbuilt)}): ' + '; '.join(unbuilt))
    print('  notes: ' + '; '.join(sorted(set(notes))))
    want.update(tutors_emerald(hoenn, built))
    _write_or_check(want, check)

def tutors_emerald(hoenn, built):
    """Emerald's 10 one-time move tutors in Hoenn towns (pokeemerald data/scripts/move_tutors.inc; the 20 Battle Frontier
    tutors, BattleFrontier_Lounge7, are not listed: Frontier closed at first) -> data/emerald/move_tutors.json for the
    tutor mechanism (emerald_mech, EMERALD-4): where each stands (the object that runs the script: HoennB2 map, tile,
    pokeemerald local id and graphics), the move (Black 2's constant), the once-only flag, the lines (gen3text, Sapphire's
    conventions) and the species that can learn it (pokeemerald src/data/pokemon/tutor_learnsets.h)."""
    from gen3text import convert
    src = open(os.path.join(EMERALD, 'data', 'scripts', 'move_tutors.inc')).read()
    texts = {}
    for lab, body in re.findall(r'^(\w+):+\n((?:\t\.string .*\n)+)', open(os.path.join(EMERALD, 'data', 'text', 'move_tutors.inc')).read(), re.M):
        texts[lab] = ''.join(re.findall(r'\.string "(.*)"', body))
    learn = collections.defaultdict(list)
    tl = open(os.path.join(EMERALD, 'src', 'data', 'pokemon', 'tutor_learnsets.h')).read()
    for sp, body in re.findall(r'\[(SPECIES_\w+)\]\s*=\s*\((.*?)\)\s*,', tl, re.S):
        for mv in re.findall(r'TUTOR\((MOVE_\w+)\)', body): learn[mv].append(sp)
    b2_moves = {k for k in re.findall(r'#define (MOVE_\w+)\s+\d+', open(f'{B2}/include/constants/moves.h').read())}
    labels = re.findall(r'^(\w+_EventScript_(\w+)Tutor)::', src, re.M)
    at = emerald_place(EMERALD, {l for l, _ in labels})
    out = []
    for lab, _ in labels:
        body = src.split(lab + '::', 1)[1].split('\n\n', 1)[0]
        mv = re.search(r'setvar VAR_0x8005, TUTOR_(MOVE_\w+)', body).group(1)
        flag = re.search(r'setflag (FLAG_\w+)', body).group(1)
        em, x, y, _ = at.get(lab, (None, None, None, None))
        mj = json.load(open(os.path.join(EMERALD, 'data', 'maps', em, 'map.json'))) if em else {}
        objs = mj.get('object_events') or []
        k = next((i for i, o in enumerate(objs) if o.get('script') == lab), None)
        name = mv[len('MOVE_'):].title().replace('_', '')
        msg = re.findall(r'msgbox (\w+)', body)                       # Teach, WhichMon; then the Declined / Taught scripts'
        for kind in ('Declined', 'Taught'):
            sub = re.search(rf'goto\w* (?:VAR_RESULT, \w+, )?(MoveTutor_EventScript_\w+{kind})', body)
            if sub: msg += re.findall(r'msgbox (\w+)', src.split(sub.group(1) + '::', 1)[1].split('\n\n', 1)[0])[:1]
        lines = {kind: convert(texts[l], expand=True)[0] for kind, l in zip(('Teach', 'WhichMon', 'Declined', 'Taught'), msg)}
        hm = hoenn(em) if em else None
        out.append(dict(move=mv, b2_move=mv if mv in b2_moves else None, script=lab, map=hm, emerald_map=em, at=[x, y],
                        local_id=k + 1 if k is not None else None, gfx=objs[k]['graphics_id'] if k is not None else None,
                        flag=flag, built=hm in built, lines=lines, learners=len(learn[mv]), species=learn[mv]))
    doc = ('Emerald\'s 10 one-time move tutors (written by converter/gen_items.py with HOENN_VERSION=emerald from pokeemerald '
           'data/scripts/move_tutors.inc, text/move_tutors.inc, src/data/pokemon/tutor_learnsets.h). map = the HoennB2 map '
           'the tutor\'s Emerald map plays, at = its tile there, built = this build has the map; lines = Teach / WhichMon / '
           'Declined / Taught in Black 2 text form; species = who can learn the move (Emerald). The tutor mechanism is '
           'EMERALD-4 (emerald_mech); the 20 Battle Frontier tutors (BattleFrontier_Lounge7) wait for the Frontier.')
    print(f'Emerald move tutors: {len(out)}: ' + '; '.join(f'{t["move"][5:]} {t["emerald_map"]} ({t["at"][0]},{t["at"][1]})'
                                                          f'{"" if t["built"] else " NOT BUILT"}' for t in out))
    return {os.path.join(ROOT, 'data', 'emerald', 'move_tutors.json'):
            json.dumps({'_doc': doc, 'tutors': out}, indent=1, ensure_ascii=False) + '\n'}

if __name__ == '__main__':
    main_emerald() if version.is_emerald() else main()
