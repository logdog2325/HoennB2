"""Emerald's eight Gyms (emerald_rooms, 2026-10-12): the rooms, their people and their puzzles on pokeemerald's maps.
Called by b2tools/emerald_rooms.py (build(ER) with that module's registries); never run alone.

Rooms: the gyms_league agent's recipe rules (b2tools/gyms_league_rooms.py: the same styles, blocks and statues) applied to
pokeemerald's map of each Gym, as <Gym>_Emerald variants (data/versions.json room_variants.emerald).

People: the Gym's story objects (data/story/ch*.json, Sapphire's) get "<key>_emerald" values where Emerald puts the same
person elsewhere: a trainer by its Black 2 trainer id (data/emerald/hoenn_trainers.json: Emerald's trainer of that slot,
e.g. Dewford's Hideki slot is Emerald's Takao), the leader and the guide by their script's name; a Sapphire trainer whose
slot Emerald does not use in this Gym is left out ("skip_emerald"). Emerald's trainers that no Sapphire object plays are
new Emerald-only objects (data/story/emerald/e_rooms.json): eye-contact trainers (script 3000 + id, sight, facing as
pokeemerald's object), the way the chapter agents place Sapphire's.

Puzzles: see each Gym below. Scripts that need Emerald's tiles are #ifdef HOENN_EMERALD blocks in the Gym's own script
file (written between "emerald_rooms" marker lines, rewritten by every run; Sapphire's build never assembles them).
"""
import os, sys, json, copy, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import gyms_league_rooms as GL                 # noqa: E402  (its recipe helpers and styles; importing writes nothing)
import models_interior as mi                    # noqa: E402
import move_codes as MOVE_CODES                 # noqa: E402

EM = 'pokeemerald/'
PE = os.path.join(ROOT, 'external', 'pokeemerald', 'data', 'maps')
PR = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps')

_bg_sapphire = GL.bg
def _bg(name, kind='sign', script=''):           # GL.bg for "pokeemerald/<Folder>" maps too
    if not name.startswith(EM): return _bg_sapphire(name, kind, script)
    j = json.load(open(os.path.join(PE, name[len(EM):], 'map.json')))
    return [[b['x'], b['y']] for b in j.get('bg_events') or [] if b.get('type') == kind and script in str(b.get('script'))]
GL.bg = _bg

def mapjson(decomp, folder):
    return json.load(open(os.path.join(PE if decomp == 'e' else PR, folder, 'map.json')))

_labels = {}
def trainer_of(folder, label):
    """The TRAINER_* a pokeemerald object script battles (its trainerbattle line), or None."""
    if folder not in _labels:
        src = open(os.path.join(PE, folder, 'scripts.inc')).read()
        out = {}
        for m in re.finditer(r'^(\w+)::[^\n]*\n((?:(?!^\w+::).*\n)*)', src, re.M):
            t = re.search(r'trainerbattle\w*\s+([^\n]*)', m.group(2))
            names = [x for x in re.findall(r'TRAINER_\w+', t.group(1)) if not x.startswith('TRAINER_BATTLE_')] if t else []
            if names: out[m.group(1)] = names[0]
        _labels[folder] = out
    if label not in _labels[folder] and folder != '*':          # (a label of another map's scripts.inc: Lavaridge B1F's
        if '*' not in _labels:                                  #  trainers are in the 1F's file)
            import glob
            allm = {}
            for p in glob.glob(os.path.join(PE, '*', 'scripts.inc')):
                for k, v in trainer_index(open(p).read()).items(): allm.setdefault(k, v)
            _labels['*'] = allm
        return _labels['*'].get(label)
    return _labels[folder].get(label)

def trainer_index(src):
    out = {}
    for m in re.finditer(r'^(\w+)::[^\n]*\n((?:(?!^\w+::).*\n)*)', src, re.M):
        t = re.search(r'trainerbattle\w*\s+([^\n]*)', m.group(2))
        names = [x for x in re.findall(r'TRAINER_\w+', t.group(1)) if not x.startswith('TRAINER_BATTLE_')] if t else []
        if names: out[m.group(1)] = names[0]
    return out

REG = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_trainers.json')))['trainers']
SREG = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainers.json')))['trainers']

_slabels = {}
def sapphire_trainer_of(folder, label):
    """The TRAINER_* a pokeruby object script battles, or None."""
    if folder not in _slabels:
        src = open(os.path.join(PR, folder, 'scripts.inc')).read()
        out = {}
        for m in re.finditer(r'^(\w+)::[^\n]*\n((?:(?!^\w+::).*\n)*)', src, re.M):
            t = re.search(r'trainerbattle\w*\s+(?:\d+,\s*)?(TRAINER_\w+)', m.group(2))
            if t: out[m.group(1)] = t.group(1)
        _slabels[folder] = out
    return _slabels[folder].get(label)

_sprites = None
def model_of(gfx):
    global _sprites
    if _sprites is None:
        os.environ['HOENN_VERSION'] = 'emerald'
        import version
        _sprites = version.load_json(os.path.join(ROOT, 'data', 'sprite_map.json'))
    alias = _sprites.get('_gfx_alias') or {}
    row = _sprites.get(gfx) or _sprites.get(alias.get(gfx, ''))
    return row['code'] if row else None

def facing(o):
    m = MOVE_CODES.npc(o['movement_type'], (int(o.get('movement_range_x', 0)), int(o.get('movement_range_y', 0))))
    return m['move'], m.get('dir', 1)

def suffix(label):
    return label.split('_EventScript_')[-1] if label else ''

def story_objects(gym):
    """[(file, object)] of the shared data/story files (Sapphire's) for map gym."""
    out = []
    d = os.path.join(ROOT, 'data', 'story')
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json'): continue
        for o in json.load(open(os.path.join(d, f))).get('objects', []):
            if o.get('map') == gym: out.append((f, o))
    return out

def place_people(ER, gym, floors=None, signs=True):
    """Moves the Gym's story people (and statue signs) to Emerald's places, leaves out Sapphire's trainers Emerald has
    not here, adds Emerald's new trainers. floors: {Sapphire map: Emerald folder} of the Gym's maps (Lavaridge's two
    floors trade trainers). Returns a report (list of lines)."""
    floors = floors or {gym: ER.emerald_folder(gym)}
    rep = []
    em = {m: mapjson('e', f) for m, f in floors.items()}
    sap = {m: mapjson('s', m) for m in floors}
    # Emerald's trainers of these maps: Black 2 id -> (map, local id, object)
    etr = {}
    for m, j in em.items():
        for i, o in enumerate(j['object_events'], 1):
            t = trainer_of(floors[m], o['script'])
            if t and o['trainer_type'] != 'TRAINER_TYPE_NONE': etr[REG[t]] = (m, i, o, t)
    used = set()
    objs = story_objects(gym) + [x for m in floors if m != gym for x in story_objects(m)]
    taken_uid = {m: {o['uid'] for _, o in objs if o.get('map') == m and o.get('kind', 'npc') == 'npc'} for m in floors}
    for f, o in objs:
        m = o['map']
        if o.get('kind', 'npc') == 'npc':
            sid = o['script'] - 3000 if 3000 <= o.get('script', 0) < 5000 else None
            hit = None
            so = sap[m]['object_events'][o['uid'] - 1] if o['uid'] - 1 < len(sap[m]['object_events']) else None
            if sid is None and so is not None:          # a trainer the room's own script battles (Petalburg's): its id
                st = sapphire_trainer_of(m, so['script'])
                if st in SREG: sid = SREG[st]; local = True
                else: local = False
            else: local = False
            if sid is not None and sid in etr:
                hit = etr[sid]; used.add(sid)
                if local: sid = None                    # (no eye-contact fields for it)
            elif so is not None:
                cands = [(i, eo) for i, eo in enumerate(em[m]['object_events'], 1)
                         if suffix(eo['script']) and suffix(eo['script']) == suffix(so['script'])]
                same = [c for c in cands if c[1]['graphics_id'] == so['graphics_id']]   # (Tate and Liza share a script)
                if same or cands: i, eo = (same or cands)[0]; hit = (m, i, eo, None)
                if local: sid = None
            if hit is None:
                if sid is not None:
                    ER.STORY_SKIP.add((f, m, o['uid']))
                    rep.append(f'{m} uid {o["uid"]} (script {o["script"]}): no Emerald trainer of that slot here: left out')
                else:
                    rep.append(f'{m} uid {o["uid"]} ({(o.get("what") or "")[:40]}): no Emerald counterpart, stays at {o["at"]}')
                continue
            em_map, lid, eo, t = hit
            want = dict(at=[eo['x'], eo['y']])
            mv, dr = facing(eo)
            if o.get('move') is not None or 'dir' in o:
                want['dir'] = dr
                if 'move' in o: want['move'] = mv
            if sid is not None: want['p0'] = int(eo['trainer_sight_or_berry_tree_id'])
            if em_map != m: want['map'] = em_map
            ER.STORY_SET[(f, m, o['uid'])] = want
            if t: rep.append(f'{m} uid {o["uid"]}: Emerald {t} at {want["at"]}' + (f' in {em_map}' if em_map != m else ''))
        elif o.get('kind') == 'sign' and signs:
            pass                                            # (statues below)
    if signs:                       # statue plaques: Sapphire's signs on Emerald's of the same name (one per Emerald sign)
        for m in floors:
            sb = [b for b in sap[m].get('bg_events') or [] if b.get('type') == 'sign']
            ew = mi.sapphire_map(EM + floors[m])['walk']          # (a sign on a walkable tile is a statue's head: Dewford)
            eb = [b for b in em[m].get('bg_events') or [] if b.get('type') == 'sign' and not ew[b['y']][b['x']]]
            mine = [(f, o) for f, o in objs if o.get('map') == m and o.get('kind') == 'sign']
            left = list(eb); todo = []
            for f, o in mine:                                   # a sign Emerald has on the same tile stays
                e = next((b for b in left if [b['x'], b['y']] == o['at']), None)
                if e is not None: left.remove(e); ER.STORY_SET[(f, m, tuple(o['at']))] = dict(at=list(o['at']))
                else: todo.append((f, o))
            for f, o in todo:
                sname = next((suffix(b['script']) for b in sb if [b['x'], b['y']] == o['at']), None)
                e = next((b for b in left if sname and suffix(b['script']) == sname), None)
                if e is not None: left.remove(e); ER.STORY_SET[(f, m, tuple(o['at']))] = dict(at=[e['x'], e['y']])
                else:
                    ER.STORY_SKIP.add((f, m, tuple(o['at']))); rep.append(f'{m} sign {o["at"]}: no Emerald sign: left out')
    # Emerald's trainers no Sapphire object plays: new Emerald-only objects
    for sid, (m, lid, eo, t) in sorted(etr.items(), key=lambda kv: (kv[1][0], kv[1][1])):
        if sid in used: continue
        uid = lid if lid not in taken_uid[m] else 100 + lid
        if model_of(eo['graphics_id']) is None:          # (never write an object the build cannot place)
            rep.append(f'{m}: Emerald trainer {t} {sid}: no Black 2 sprite for {eo["graphics_id"]}: NOT placed'); continue
        taken_uid[m].add(uid)
        mv, dr = facing(eo)
        NEW_TRAINERS.setdefault(GYM_NUM.get(gym), []).append((sid, t))
        ER.STORY_NEW.append(dict(kind='npc', map=m, at=[eo['x'], eo['y']], uid=uid, model=model_of(eo['graphics_id']),
                                 script=3000 + sid, evtype=1, p0=int(eo['trainer_sight_or_berry_tree_id']), move=mv, dir=dr,
                                 what=f"{t} {sid}: eye-contact trainer, Emerald only (pokeemerald {floors[m]} object {lid}, "
                                      f"{eo['graphics_id'][14:]}, {eo['movement_type'][14:]}, sight {eo['trainer_sight_or_berry_tree_id']})"))
        rep.append(f'{m}: new Emerald trainer {t} {sid} at ({eo["x"]},{eo["y"]}) uid {uid}')
    return rep

def statues(n, model='object02_1'):
    """GL.statues on Emerald's maps: only the solid GymStatue tiles (Emerald also puts the sign on a statue's walkable head
    tile: Dewford's (4,23) (7,23))."""
    w = GL.walk(n)
    out = []
    for x, z in GL.bg(n, script='GymStatue'):
        if w[z][x]: continue
        out.append(dict(m=model, tile=[x, z]) if z == 0 or w[z - 1][x] else dict(m=model, at=[x + 0.5, z]))
    return out

def solid_tiles(n, rect, skip=()):
    return GL.solid_in(n, rect, skip)

def gym_variant(ER, base, doc, rec):
    n = base + '_Emerald'
    rec = dict(rec)
    rec['_doc'] = ER.DOC + doc
    rec.pop('mats', None)
    rec = GL.exit_mats(rec['map'], rec)
    ER.OUT[n] = rec
    ER.VARIANTS[base] = n
    return n

# ------------------------------------------------------------------------------------------------ the Gyms
REPORT = []
GYM_NUM = {'RustboroCity_Gym': 1, 'DewfordTown_Gym': 2, 'MauvilleCity_Gym': 3, 'LavaridgeTown_Gym_1F': 4,
           'PetalburgCity_Gym': 5, 'FortreeCity_Gym': 6, 'MossdeepCity_Gym': 7, 'SootopolisCity_Gym_1F': 8}
NEW_TRAINERS = {}   # gym number -> [(Black 2 id, TRAINER_*)] of Emerald's new Gym trainers (h_set_gym_trainers)
SCRIPTS = os.path.join(ROOT, 'src', 'field_scripts')
def script_file(n):
    import glob
    return glob.glob(os.path.join(SCRIPTS, f'*_room_{n}.s'))[0]

def gym_trainers_block(ER):
    """Emerald's new Gym trainers count as beaten with their leader too (Common_EventScript_SetGymTrainers: pokeemerald
    data/scripts/set_gym_trainers.inc): an Emerald branch at the start of hoenn_story.inc's h_set_gym_trainers."""
    body = ['#ifdef HOENN_EMERALD', '    .if 0']
    for g in sorted(k for k in NEW_TRAINERS if k):
        body.append(f'    .elseif \\gym == {g}')
        body += [f'    TrainerFlagSet {sid}                     // {t} (Emerald only)' for sid, t in sorted(NEW_TRAINERS[g])]
    body += ['    .endif', '#endif']
    ER.SCRIPT_BLOCKS.append((os.path.join(ROOT, 'src', 'include', 'hoenn_story.inc'), 'gym_trainers', ('after', r'^\s*\.macro h_set_gym_trainers gym'),
                             '\n'.join(body)))

def dewford_dark(ER):
    """Emerald's darkness: SetFlashLevel 7 (24 pixels) with no trainer beaten, each of its six trainers 8 pixels more
    (pokeemerald field_screen_effect.c sFlashLevelToRadius 24 ... 72), lights on once Brawly is beaten. Sapphire's
    Sub_DG_FlashTarget jumps to the Emerald one in an Emerald build."""
    f = script_file('DewfordTown_Gym')
    names = ['TRAINER_TAKAO', 'TRAINER_JOCELYN', 'TRAINER_LAURA', 'TRAINER_BRENDEN', 'TRAINER_CRISTIAN', 'TRAINER_LILITH']
    ER.SCRIPT_BLOCKS.append((f, 'dewford_flash_jump', ('after', r'^Sub_DG_FlashTarget:'),
                             '#ifdef HOENN_EMERALD\n    VMJump Sub_DG_FlashTargetEm         // Emerald: six trainers, 8 pixels each\n#endif'))
    body = ['#ifdef HOENN_EMERALD', '#include "hoenn_trainers_emerald.h"',
            'Sub_DG_FlashTargetEm:                   // pokeemerald DewfordTown_Gym_EventScript_SetFlashLevel + CountTrainersDefeated',
            '    WorkSetConst DG_TARGET, 0',
            '    h_goto_if_set FLAG_DEFEATED_DEWFORD_GYM, L_DG_EmTargetEnd',
            '    WorkSetConst DG_TARGET, FLASH_PX(24)']
    for k, t in enumerate(names):
        body += [f'    h_goto_if_not_defeated {t}, L_DG_EmTarget{k}', '    WorkAdd DG_TARGET, FLASH_PX(8)', f'L_DG_EmTarget{k}:']
    body += ['L_DG_EmTargetEnd:', '    VMReturn', '    .balign 4, 0', '#endif']
    ER.SCRIPT_BLOCKS.append((f, 'dewford_flash', 'end', '\n'.join(body)))

def rustboro(ER):
    g = 'RustboroCity_Gym'; n = EM + g
    st = GL.bg(n, script='GymStatue')
    base = ER.recipe(g)
    r = copy.deepcopy(base)
    r.update(map=n, floor=[[0, 2, 10, 19]], blocks=[dict(use='gl_rock', tiles=solid_tiles(n, [0, 2, 10, 18], skip=st))],
             furniture=statues(n))
    gym_variant(ER, g, "Emerald's Rustboro Gym (11x20, Emerald's maze): the rock walls of pokeemerald's map as raised rock "
                "blocks, Roxanne's sand dais (rows 2-3), the two statues by the entrance (18).", r)
    ER.overlay(583, g, "the exits (5,19) (6,19) (Emerald's room is a row longer).", warps={0: (5, 19), 1: (6, 19)})
    REPORT.extend(place_people(ER, g))

def dewford(ER):
    g = 'DewfordTown_Gym'; n = EM + g
    sm = mi.sapphire_map(n); w = sm['walk']
    st = GL.bg(n, script='GymStatue') + GL.statue_heads(n)
    walls = [[x, z] for z in range(sm['h']) for x in range(sm['w']) if not w[z][x] and [x, z] not in st and
             any(0 <= x + dx < sm['w'] and 0 <= z + dz < sm['h'] and w[z + dz][x + dx] for dx in (-1, 0, 1) for dz in (-1, 0, 1))]
    floor = [[x, z, x, z] for z in range(sm['h']) for x in range(sm['w']) if w[z][x] or [x, z] in walls or [x, z] in st]
    r = copy.deepcopy(ER.recipe(g))
    r.update(map=n, floor=floor, open=True, blocks=[dict(use='gl_dewford_wall', tiles=walls)], furniture=statues(n))
    gym_variant(ER, g, "Emerald's Dewford Gym (Emerald's dark maze, same size): corridors floating in the dark, every wall "
                "tile next to a corridor a low wall block, the four statues by the entrance.", r)
    REPORT.extend(place_people(ER, g))
    # the darkness: Emerald counts its six trainers (Sapphire three): scenes in 0050 (EMERALD_DEWFORD block)
    dewford_dark(ER)

def fortree(ER):
    g = 'FortreeCity_Gym'; n = EM + g
    st = GL.bg(n, script='GymStatue')
    ledges = GL.beh_tiles(n, (0x3B,))
    posts = [t for t in solid_tiles(n, [0, 1, 19, 23], skip=st) if t not in ledges]
    r = copy.deepcopy(ER.recipe(g))
    r.update(map=n, floor=[[0, 1, 19, 24]], ledges=True,
             blocks=[dict(use='gl_fortree_post', tiles=posts), dict(use='gl_fortree_ledge', tiles=ledges)],
             furniture=statues(n))
    gym_variant(ER, g, "Emerald's Fortree Gym (Emerald's layout, same size): the grass paths between wooden posts, the "
                "ledges of the right lane (rows 6/12/17, jumped down), Winona's nook top right, the statues by the exit "
                "(15-16, 24). The rotating gates are not built (as in Sapphire's room).", r)
    ER.overlay(119, g, "the exits (15,24) (16,24).", warps={0: (15, 24), 1: (16, 24)})
    REPORT.extend(place_people(ER, g))

def petalburg(ER):
    g = 'PetalburgCity_Gym'; n = EM + g
    r = copy.deepcopy(ER.recipe(g))
    r['map'] = n
    # Norman's raised dais (2-6, 2-3) with a post at each end ((2,2)-(2,3), (6,2)-(6,3) solid in Emerald): the mat in front
    # of him moves onto it
    for ft in r.get('floor_tex', []):
        if ft.get('tex') == 'in05_mat1': ft['rect'] = [3, 2, 5, 3]
    r.setdefault('blocks', []).append(dict(h=10, tiles=[[2, 2], [2, 3], [6, 2], [6, 3]], top=GL.T(286, 'in05_yuka2', size=16),
                                          side=GL.T(286, 'in05_sch_ka3', u_size=16, v=[0, 0.25]), _what="the dais' posts"))
    gym_variant(ER, g, "Emerald's Petalburg Gym (same rooms and doors): Norman's room has a raised dais (2-6, 2-3) with posts "
                "at its ends and Norman at (4,2) on it.", r)
    REPORT.extend(place_people(ER, g))


def build(ER):
    for f in (rustboro, dewford, fortree, petalburg, mauville, lavaridge, sootopolis, mossdeep):
        f(ER)
    gym_trainers_block(ER)
    open(os.path.join(ROOT, 'work', 'agents', 'emerald_rooms', 'gyms_people.txt'), 'w').write('\n'.join(REPORT) + '\n')

# ---- Mauville Gym: Emerald's beams and four switches -------------------------------------------------------------------
# pokeemerald field_specials.c MauvilleGymSetDefaultBarriers / MauvilleGymDeactivatePuzzle are Sapphire's
# MauvilleGymSpecial2 / 3 (the same metatiles, the same loops over x 0-8, y 5-16), so the room's three layouts (the map,
# "alt" = every switch's toggle, "off" = Wattson beaten) come from Emerald's map the way gyms_league_rooms.py makes
# Sapphire's (MauvilleCity_Gym_Alt_Emerald / _Off_Emerald, the zone's alt rooms with map replace events 3 / 4 as
# Sapphire's). Emerald has four switches (Sapphire three): (0,15) (4,12) (3,9) (8,9) = scripts 5, 6, 7 and the Emerald-only
# MG_Switch4Em; Sub_MG_Redraw's tiles (the switches, the tiles beside Wattson at (5,2)) are Emerald's in an Emerald build.
MG_POLES = {0x218, 0x240, 0x241, 0x242, 0x243, 0x24E}     # pole bases / pole bottoms (solid in every state)
def mauville_em_states():
    from gba import Repo
    M = GL.MG_SAPPHIRE
    repo = Repo(os.path.join(ROOT, 'external', 'pokeemerald'))
    g, _ = repo.layout_grid(repo.map_json('MauvilleCity_Gym')['layout'])
    t0 = {(x, z): (int(g[z, x]) & 0x3FF, (int(g[z, x]) >> 10) & 3 != 0) for z in range(g.shape[0]) for x in range(g.shape[1])}
    def run(t, table, floor_rule):
        t = dict(t)
        for z in range(5, 17):
            for x in range(0, 9):
                m = t[(x, z)][0]
                if floor_rule and m == M['floor']:
                    t[(x, z)] = (M['gv2_on'], True) if t[(x, z - 1)][0] == M['gv1_on'] else (M['rv2_on'], True)
                elif m in table: t[(x, z)] = table[m]
        return t
    off = lambda k: (M[k], False)
    on = lambda k: (M[k], True)
    special3 = {M[c + 'h%d_on' % i]: off(c + 'h%d_off' % i) for c in 'gr' for i in (1, 2, 3, 4)}
    special3.update({M['gv1_on']: on('pb_on'), M['rv1_on']: on('pb_off'), M['gv2_on']: off('floor'),
                     M['rv2_on']: off('floor'), M['pt_on']: off('pt_off')})
    special2 = dict(special3)
    special2.update({M[c + 'h%d_off' % i]: (on if i > 2 else off)(c + 'h%d_on' % i) for c in 'gr' for i in (1, 2, 3, 4)})
    special2.update({M['pb_on']: on('gv1_on'), M['pb_off']: on('rv1_on'), M['pt_off']: on('pt_on')})
    states = dict(normal=t0, alt=run(t0, special2, True), off=run(t0, special3, False))
    return states

def mauville(ER):
    g = 'MauvilleCity_Gym'; n = EM + g
    st = mauville_em_states()
    coll = {k: {xz: v[1] for xz, v in s.items()} for k, s in st.items()}
    toggles = sorted((xz for xz in coll['normal'] if len({coll[k][xz] for k in coll}) > 1), key=lambda t: (t[1], t[0]))
    poles = sorted([list(xz) for xz in coll['normal'] if all(coll[k][xz] for k in coll) and 5 <= xz[1] <= 16 and
                    any(st[k][xz][0] in MG_POLES for k in st)], key=lambda t: (t[1], t[0]))
    base = ER.recipe(g)
    def rec(state):
        beams = [[x, z] for x, z in toggles if coll[state][(x, z)]]
        walls = [t for t in solid_tiles(n, [0, 2, 9, 17]) if t not in poles and tuple(t) not in toggles and
                 (t[1] >= 8 or 3 <= t[0] <= 6)]          # (Emerald's dais posts (3/6, 2-3) and (3/6, 6-7) too)
        r = copy.deepcopy(base)
        r.update(map=n, blocks=[dict(use='gl_mauville_pole', units=[x + 0.25, z + 0.3, x + 0.75, z + 0.8]) for x, z in poles] +
                 [dict(use='gl_mauville_wall', tiles=walls)],
                 furniture=[dict(m='d6_yuka_biri02_1', tile=t) for t in beams] + statues(n))
        for k in ('alt_of', 'block', 'unblock'): r.pop(k, None)
        if state != 'normal':
            r['alt_of'] = g
            blk = [[x, z] for x, z in toggles if coll[state][(x, z)] and not coll['normal'][(x, z)]]
            unb = [[x, z] for x, z in toggles if not coll[state][(x, z)] and coll['normal'][(x, z)]]
            if blk: r['block'] = blk
            if unb: r['unblock'] = unb
        return r
    doc = ("Emerald's Mauville Gym (Emerald's beams, same room): the poles and walls of pokeemerald's map, the beam tiles as "
           "Black 2 electric floor, the statues.")
    gym_variant(ER, g, doc, rec('normal'))
    for state, name, ev in (('alt', 'MauvilleCity_Gym_Alt_Emerald', GL.MG_EVENT_ALT), ('off', 'MauvilleCity_Gym_Off_Emerald', GL.MG_EVENT_OFF)):
        r = rec(state); r['_doc'] = ER.DOC + doc + (f" Layout \"{state}\": every switch's toggle (MauvilleGymSetDefaultBarriers)"
                                                    if state == 'alt' else ' Layout "off": every beam off (MauvilleGymDeactivatePuzzle)') + \
                                    f', loaded instead of the room by map replace event {ev}.'
        r.pop('mats', None); r = GL.exit_mats(n, r)
        ER.OUT[name] = r
    z = ER.overlay(239, g, "the alt rooms are Emerald's (MauvilleCity_Gym_Alt_Emerald / _Off_Emerald, events 3 / 4 as "
                   "Sapphire's).")
    z['alt_rooms'] = [dict(room='MauvilleCity_Gym_Alt_Emerald', event=GL.MG_EVENT_ALT), dict(room='MauvilleCity_Gym_Off_Emerald', event=GL.MG_EVENT_OFF)]
    REPORT.extend(place_people(ER, g))
    REPORT.append(f'MauvilleCity_Gym: toggles {toggles}; poles {poles}')
    # the switches: Sapphire's three triggers on Emerald's switches 1-3, a fourth (Emerald only) on switch 4
    f = 'ch3b.json'
    for sap_at, em_at in (((0, 9), (0, 15)), ((8, 11), (4, 12)), ((4, 15), (3, 9))):
        ER.STORY_SET[(f, g, sap_at)] = dict(at=list(em_at))
    sf = script_file(g)
    sw4 = next_entries(sf, 1)[0]
    ER.STORY_NEW.append(dict(kind='trigger', map=g, at=[8, 9], script=sw4, var=0, value=0,
                             what="floor switch 4 (always; Emerald only: MauvilleCity_Gym_EventScript_Switch4, MG_Switch4Em)"))
    ER.SCRIPT_BLOCKS.append((sf, 'mauville_entries', 'table',
                             f'#ifdef HOENN_EMERALD\n    ScriptEntry MG_Switch4Em        // {sw4}: MauvilleCity_Gym_EventScript_Switch4, (8,9) (Emerald only)\n#endif'))
    ER.SCRIPT_BLOCKS.append((sf, 'mauville_redraw_jump', ('after', r'^Sub_MG_Redraw:'),
                             '#ifdef HOENN_EMERALD\n    VMJump Sub_MG_RedrawEm          // Emerald: its switches and Wattson\'s tiles\n#endif'))
    oz = 0                                        # zone tiles = Emerald tiles + origin (the variant's room.json)
    ER.SCRIPT_BLOCKS.append((sf, 'mauville_em', 'end', f'''#ifdef HOENN_EMERALD
MG_Switch4Em:                           // MauvilleCity_Gym_EventScript_Switch4 (Emerald's fourth switch, VAR_MAUVILLE_GYM_STATE 4)
    h_lock
    h_goto_if_set FLAG_DEFEATED_MAUVILLE_GYM, L_MG_SwitchDoNothing
    h_goto_if_eq VAR_MAUVILLE_GYM_STATE, 4, L_MG_SwitchDoNothing
    h_setvar VAR_MAUVILLE_GYM_STATE, 4
    VMJump L_MG_PressFloorSwitch
Sub_MG_RedrawEm:                        // Sub_MG_Redraw on Emerald's tiles (zone tiles = Emerald tiles + (1,0))
    PlayerGetGPos MG_X, MG_Z
    PlayerGetDir MG_DIR
    FadeOutBlack
    FadeWait
    MG_IF_AT 1, 15, L_MG_EmAt1          // the switches (0,15) (4,12) (3,9) (8,9)
    MG_IF_AT 5, 12, L_MG_EmAt2
    MG_IF_AT 4, 9, L_MG_EmAt3
    MG_IF_AT 9, 9, L_MG_EmAt4
    MG_IF_AT 5, 2, L_MG_EmAtWattsonW    // beside Wattson (5,2): west (4,2), south (5,3)
    MG_IF_AT 6, 3, L_MG_EmAtWattsonS
    FadeInBlack
    FadeWait
    VMReturn
L_MG_EmAt1:
    MG_WARP_HERE 1, 15
L_MG_EmAt2:
    MG_WARP_HERE 5, 12
L_MG_EmAt3:
    MG_WARP_HERE 4, 9
L_MG_EmAt4:
    MG_WARP_HERE 9, 9
L_MG_EmAtWattsonW:
    MG_WARP_HERE 5, 2
L_MG_EmAtWattsonS:
    MG_WARP_HERE 6, 3
    .balign 4, 0
#endif'''))

def next_entries(sf, k):
    """The script numbers the next k ScriptEntry lines of an Emerald build get in room script sf: after every entry an
    Emerald build assembles (other agents' #ifdef HOENN_EMERALD entries count, Ruby's and test builds' do not), this
    script's own blocks left out (they are rewritten)."""
    src = open(sf, encoding='utf-8').read()
    src = re.sub(r'(?m)^[ \t]*// >>> emerald_rooms .*\n(?:.*\n)*?[ \t]*// <<< emerald_rooms .*\n', '', src)
    stack, n = [], 0
    for ln in src.split('\n'):
        t = ln.strip()
        m = re.match(r'#(ifdef|ifndef)\s+(\w+)', t)
        if m:
            on = m.group(2) == 'HOENN_EMERALD'
            stack.append(on if m.group(1) == 'ifdef' else not on); continue
        if t.startswith('#if '): stack.append(True); continue
        if t.startswith('#else') and stack: stack[-1] = not stack[-1]; continue
        if t.startswith('#endif') and stack: stack.pop(); continue
        if t.startswith('ScriptEntry ') and all(stack): n += 1
    return [n + 1 + i for i in range(k)]

# ---- Lavaridge Gym 1F / B1F: Emerald's 17x19 floors -------------------------------------------------------------------
# 1F: three bands of sand between rock walls, ledges (rows 13 and 15, jumped down), 24 holes (MB_LAVARIDGE_GYM_1F_WARP)
# you drop through onto the B1F tile below; B1F: the vents (MB_LAVARIDGE_GYM_B1F_WARP) that blow you back up. As
# Sapphire's rooms (gyms_league_rooms.py step_triggers): each hole / vent a step trigger whose script fades and changes the
# map to the destination warp's tile (MapChangeCore); every warp tile an arrival spot (dir 0). The Emerald scripts are
# entries after the rooms' own (#ifdef HOENN_EMERALD), the zone jsons Emerald overlays with pokeemerald's warps in its order.
LAVA_ORIGIN = [1, 0]
def lavaridge(ER):
    f1, fb = 'LavaridgeTown_Gym_1F', 'LavaridgeTown_Gym_B1F'
    n1, nb = EM + f1, EM + fb
    for g, n, style in ((f1, n1, 'gl_lavaridge'), (fb, nb, 'gl_lavaridge')):
        st = GL.bg(n, script='GymStatue')
        ledges = GL.beh_tiles(n, (0x3B,))
        r = copy.deepcopy(ER.recipe(g))
        r.update(map=n, style=style, origin=LAVA_ORIGIN, floor=[[0, 2, 16, 18]], ledges=True,
                 blocks=[dict(use='gl_lava_band', h=14, tiles=[t for t in solid_tiles(n, [0, 2, 16, 18], skip=st) if t not in ledges]),
                         dict(use='gl_lava_ledge', tiles=ledges)],      # (14 high: Emerald's walls stand in the middle of
                 furniture=[dict(m=f['m'], tile=[round(f.get('tile', f.get('at'))[0]), f.get('tile', f.get('at'))[1]], dz=3)
                            for f in statues(n)])          #  the floor, people behind them; statues on their tile, 3 off the wall)
        if g == f1:
            r['floor_tex'] = [dict(GL.HOLE, rect=[x, z, x, z]) for x, z in GL.beh_tiles(n, (0x68,))]
            doc = ("Emerald's Lavaridge Gym 1F (17x19): sand bands between rock walls, ledges on rows 13 and 15, the 24 sand "
                   "holes you drop through (MB_LAVARIDGE_GYM_1F_WARP) as dark holes, the statues by the exit.")
        else:
            r['floor_tex'] = [GL.T(388, 'in81_magu06', rect=[x, z, x, z], stretch=True) for x, z in GL.beh_tiles(n, (0x29,))]
            doc = ("Emerald's Lavaridge Gym B1F (17x19): the sand cave under 1F with its rock walls and ledges, the steam "
                   "vents (MB_LAVARIDGE_GYM_B1F_WARP) that blow you back up.")
        gym_variant(ER, g, doc, r)
    j1, jb = mapjson('e', f1), mapjson('e', fb)
    sm1, smb = mi.sapphire_map(n1), mi.sapphire_map(nb)
    zone = {f1: 145, fb: 148}
    ox, oz = LAVA_ORIGIN
    for g, j, sm, other, oj in ((f1, j1, sm1, fb, jb), (fb, jb, smb, f1, j1)):
        sf = script_file(g)
        z = ER.zone_json(zone[g])
        sap_exits = [w for w in z['warps'] if w['to'][0] != zone[other]]
        warps, trig, entries, bodies = [], [], [], []
        steps = [(i, w) for i, w in enumerate(j['warp_events']) if w['dest_map'].endswith('GYM_B1F' if g == f1 else 'GYM_1F')
                 and sm['beh'][w['y']][w['x']] in GL.STEP_ON]
        nums = next_entries(sf, len(steps))
        for i, w in enumerate(j['warp_events']):
            to_other = w['dest_map'].endswith('GYM_B1F' if g == f1 else 'GYM_1F')
            if not to_other:                          # the exits (1F): Sapphire's destination
                e = dict(sap_exits[len([x for x in warps if x.get('_exit')])]); e['at'] = [w['x'], w['y']]; e['_exit'] = True
                warps.append(e); continue
            dw = int(w['dest_warp_id'])
            warps.append(dict(at=[w['x'], w['y']], tile_only=True, to=[zone[other], dw], type=2, dir=0,
                              what=f"Emerald warp {i} -> {other} {dw}"))
        for (i, w), num in zip(steps, nums):
            dw = int(w['dest_warp_id']); d = oj['warp_events'][dw]
            lab = f"EL_{'Hole' if g == f1 else 'Vent'}{i}"
            entries.append(f'    ScriptEntry {lab:<20s}// {num}: Emerald warp {i} ({w["x"]},{w["y"]}) -> {other} warp {dw} ({d["x"]},{d["y"]})')
            bodies.append(f'''{lab}:                                  // Emerald warp {i} ({w["x"]},{w["y"]}) -> {other} warp {dw} ({d["x"]},{d["y"]})
    ActorsPauseAll
    FadeOutBlack
    RTReserveScript {GL.ARRIVAL_SCRIPT}                            // hm_free Script_18: fades in on arrival
    FadeWait
    MapChangeCore {zone[other]}, {d["x"] + ox}, 0, {d["y"] + oz}, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt''')
            trig.append(dict(script=num, var=0, value=0, at=[w['x'], w['y']]))
        for w in warps: w.pop('_exit', None)
        ER.OVERLAYS[zone[g]] = dict(z, _doc=ER.DOC + f"Emerald's overlay of {zone[g]}.json: pokeemerald's warps in its order "
                                    f"(tiles of {g}_Emerald), the {'holes' if g == f1 else 'vents'} as step triggers running the "
                                    "Emerald scripts (#ifdef HOENN_EMERALD entries of the room's script file). " + z.get('_doc', z.get('what', '')),
                                    warps=warps, triggers=trig)
        ER.SCRIPT_BLOCKS.append((sf, 'lavaridge_entries', 'table', '#ifdef HOENN_EMERALD\n' + '\n'.join(entries) + '\n#endif'))
        ER.SCRIPT_BLOCKS.append((sf, 'lavaridge_warps', 'end', '#ifdef HOENN_EMERALD\n' + '\n\n'.join(bodies) + '\n    .balign 4, 0\n#endif'))
    REPORT.extend(place_people(ER, f1, floors={f1: f1, fb: fb}))

# ---- Sootopolis Gym 1F / B1F: Emerald's ice ---------------------------------------------------------------------------
# The same three ice rooms; Emerald moved some thin-ice tiles (64 tiles: 7 / 19 / 38 per room, Sapphire 7 / 19 / 40), so
# its third ramp opens at 67 steps (pokeemerald OnFrame thresholds 8 / 28 / 67; Sapphire 69). Sapphire's thin-ice triggers
# on tiles Emerald has no thin ice on are left out, Emerald's new thin-ice tiles get triggers (e_rooms.json) running
# Emerald-only entries of the same macro (gy_ice: the row's work bit, the B1F tile below = tile + (1,-4)). The B1F's rooms
# are wider in Emerald (2-14 / 4-12). Floor tiles no exit or ramp reaches (Emerald's side pockets beside the middle
# room) are made solid.
SOOTO_ROWS = [6, 7, 8, 9, 12, 13, 14, 17, 18, 19]          # their works 0x4001-0x400A (0046 GY_Init), bit x - 3
def reachable(sm, starts):
    seen, st = set(starts), list(starts)
    while st:
        x, z = st.pop()
        for q in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            if q not in seen and 0 <= q[0] < sm['w'] and 0 <= q[1] < sm['h'] and sm['walk'][q[1]][q[0]]:
                seen.add(q); st.append(q)
    return seen

def sootopolis(ER):
    f1, fb = 'SootopolisCity_Gym_1F', 'SootopolisCity_Gym_B1F'
    n1, nb = EM + f1, EM + fb
    # 1F
    ice = GL.beh_tiles(n1, (0x26, 0x27))
    rocks = [t for r in GL.SOOTO_ROOMS for t in solid_tiles(n1, r)]
    stat = [list(t) for t in GL.bg(n1, script='GymStatue')]
    sm1 = mi.sapphire_map(n1)
    reach = reachable(sm1, [(8, 25), (9, 25), (11, 22)])
    pockets = sorted([[x, z] for z in range(sm1['h']) for x in range(sm1['w']) if sm1['walk'][z][x] and (x, z) not in reach],
                     key=lambda t: (t[1], t[0]))
    walls = [t for t in solid_tiles(n1, [3, 2, 13, 25]) if t not in rocks and t[1] > 2 and t not in stat]
    r = copy.deepcopy(ER.recipe(f1))
    r.update(map=n1, origin=[1, 0], floor=[[3, 2, 13, 25]],
             floor_tex=[GL.T(292, 'd5ice_yuka', rect=[x, z, x, z], size=32) for x, z in ice] +
                       [GL.T(292, 'd5ice_yuka2', rect=rr, size=32) for rr in GL.SOOTO_LINKS[:3]] +
                       [GL.T(292, 'd5kaidan1', rect=GL.SOOTO_LINKS[3], size=16), GL.T(315, 'gos_hasigo01', rect=[11, 22, 11, 22], stretch=True)],
             blocks=[dict(use='gl_fountain', rect=[4, 2, 5, 2]), dict(use='gl_fountain', rect=[11, 2, 12, 2]),
                     dict(use='gl_ice_wall', tiles=walls)],               # (Emerald's fountains: one tile narrower)
             furniture=[dict(m='d6stone02', tile=t) for t in rocks] + statues(n1))
    if pockets: r['block'] = pockets
    gym_variant(ER, f1, "Emerald's Sootopolis Gym 1F (same rooms, Emerald's thin ice): the entrance hall with the statues and "
                "the ladder down, the three ice rooms with Emerald's thin-ice tiles, the ice ramps, the leader's dais "
                f"between the fountains. Tiles no exit reaches (Emerald's side pockets) are solid: {pockets}.", r)
    # B1F
    smb = mi.sapphire_map(nb)
    r = copy.deepcopy(ER.recipe(fb))
    r.update(map=nb, origin=[1, -4], floor=[[2, 6, 14, 25]],
             blocks=[dict(use='gl_ice_cliff', tiles=solid_tiles(nb, [2, 6, 14, 25]))])
    reachb = reachable(smb, [(11, 22)])
    pb = [[x, z] for z in range(smb['h']) for x in range(smb['w']) if smb['walk'][z][x] and (x, z) not in reachb]
    if pb: r['block'] = pb
    gym_variant(ER, fb, "Emerald's Sootopolis Gym B1F: the snowy ice cave under the ice rooms (Emerald's rooms are wider: "
                "2-14 and 4-12), the ladder up at (11,22).", r)
    # the thin ice
    S = mi.sapphire_map(f1)
    si = {(x, z) for z in range(S['h']) for x in range(S['w']) if S['beh'][z][x] == 0x26}
    ei = {(x, z) for z in range(sm1['h']) for x in range(sm1['w']) if sm1['beh'][z][x] == 0x26}
    sf = script_file(f1)
    for x, z in sorted(si - ei, key=lambda t: (t[1], t[0])):
        ER.STORY_SKIP.add(('ch10.json', f1, (x, z)))
    new = sorted(ei - si, key=lambda t: (t[1], t[0]))
    nums = next_entries(sf, len(new))
    entries, bodies = [], []
    for (x, z), num in zip(new, nums):
        lab = f'GY_EIce_{x}_{z}'
        entries.append(f'    ScriptEntry {lab:<16s}// {num}: thin ice ({x},{z}) (Emerald only)')
        bodies.append(f'{lab}:\n    gy_ice 0x{0x4001 + SOOTO_ROWS.index(z):04X}, 0x{1 << (x - 3):04X}, {x + 1}, {z - 4}')
        ER.STORY_NEW.append(dict(kind='trigger', map=f1, at=[x, z], script=num, var=0, value=0,
                                 what=f'thin ice ({x},{z}) (Emerald only: {lab})'))
    ER.SCRIPT_BLOCKS.append((sf, 'sootopolis_entries', 'table', '#ifdef HOENN_EMERALD\n' + '\n'.join(entries) + '\n#endif'))
    ER.SCRIPT_BLOCKS.append((sf, 'sootopolis_cracked_jump', ('after', r'^GY_IceCracked:'),
                             '#ifdef HOENN_EMERALD\n    VMJump GY_IceCrackedEm              // Emerald: 8 / 28 / 67\n#endif'))
    ER.SCRIPT_BLOCKS.append((sf, 'sootopolis_link3', ('after', r'^GY_Link3:'),
                             '#ifdef HOENN_EMERALD\n    gy_link 68, GY_Ice_8_6              // Emerald: the third ramp opens at 67 (+1)\n#endif'))
    ER.SCRIPT_BLOCKS.append((sf, 'sootopolis_ice', 'end', '#ifdef HOENN_EMERALD\n' + '\n'.join(bodies) + '''
GY_IceCrackedEm:                        // GY_IceCracked with Emerald's thresholds (OnFrame: 8 / 28 / 67)
    WorkAdd VAR_ICE_STEP_COUNT, 1
    SEPlay C10_SE_ICE_CRACK
    WorkCmpConst VAR_ICE_STEP_COUNT, 8
    VMJumpIf CMP_EQ, GY_IceUnlock
    WorkCmpConst VAR_ICE_STEP_COUNT, 28
    VMJumpIf CMP_EQ, GY_IceUnlock
    WorkCmpConst VAR_ICE_STEP_COUNT, 67
    VMJumpIf CMP_EQ, GY_IceUnlock
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
#endif'''))
    REPORT.append(f'SootopolisCity_Gym_1F thin ice: Sapphire-only {sorted(si - ei)} left out, Emerald-only {new} added; pockets {pockets}')
    REPORT.extend(place_people(ER, f1, floors={f1: f1, fb: fb}))

# ---- Mossdeep Gym: Emerald's rooms, warp pads and rotating tiles ------------------------------------------------------
# pokeemerald's Mossdeep Gym (26x36) is a set of small rooms floating in space, joined by warp pads (MB_MOSSDEEP_GYM_WARP:
# stepping onto one sets you down on its partner, keeping every object where it is: DoMossdeepGymWarp saves the objects).
# Its puzzle (rotating_tile_puzzle.c): colored 2x2 squares of arrow tiles carry trainers and statues; a floor switch of a
# color moves every object standing on that color's arrows one tile along its arrow (around the square, counter-
# clockwise) and turns it a quarter counter-clockwise, which opens paths and turns the trainers' gaze. Here:
# - the room: Black 2 floor on the walkable tiles and a low white wall on the solid tiles beside them, floating in the
#   dark (open), the arrows / switches / pads drawn on the floor (Sapphire's arrow texture: the colors are not drawn);
# - the pads: step triggers that set the player down on the partner pad (ActorSetGPos 255: a map change to the same zone
#   hangs in Black 2, 0644's own MG_WarpToEntrance does the same), so the objects stay where they are, as Emerald;
# - the switches: step triggers running EMG_Switch<Color>: every object of that color's squares walks one tile (facing
#   locked) and turns, by the color's press count (map-local works 0x4011-0x4015, 0 on entering, as Emerald's object
#   positions reset when you enter the Gym): the positions and facings follow from the starting ones (the squares are
#   closed loops), so no position is read at run time;
# - the statues: rocks (Black 2 has no statue person; code 206, Clay Tunnel's rock) as Emerald-only objects.
MG_COLORS = ['Yellow', 'Blue', 'Green', 'Purple', 'Red']
LEADER_TILES = {(23, 7), (24, 7)}                               # Tate and Liza's solid dais (talked to from row 8)
MG_WORK0 = 0x4011
MG_ORIGIN = [1, 2]
DIRN = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}            # arrow kind -> walk
DIRV = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}
FACE_OF = {'FACE_UP': 0, 'FACE_DOWN': 1, 'FACE_LEFT': 2, 'FACE_RIGHT': 3}
CCW = {3: 0, 1: 3, 2: 1, 0: 2}                                  # Black 2 dir (0 up 1 down 2 left 3 right) turned a quarter CCW
B2NAME = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}
STATUE_MODEL = 206

def mossdeep(ER):
    g = 'MossdeepCity_Gym'; n = EM + g
    from gba import Repo
    repo = Repo(os.path.join(ROOT, 'external', 'pokeemerald'))
    j = repo.map_json(g); grid, _ = repo.layout_grid(j['layout'])
    H, W = grid.shape
    sm = mi.sapphire_map(n)
    arrows = {}
    for z in range(H):
        for x in range(W):
            mt = int(grid[z, x]) & 0x3FF
            if 0x250 <= mt < 0x250 + 5 * 8: arrows[(x, z)] = ((mt - 0x250) // 8, (mt - 0x250) % 8)
    pads = {(w['x'], w['y']): i for i, w in enumerate(j['warp_events']) if w['dest_map'] == 'MAP_MOSSDEEP_CITY_GYM'}
    pad_tiles = set(pads) | {(c['x'], c['y']) for c in j['coord_events'] if c['script'].endswith('WarpToEntrance')}
    # reachable: from the exits, through the pads (the objects block nothing for this)
    seen = reachable(sm, [(6, 35), (7, 35)])
    while True:
        more = [(j['warp_events'][int(j['warp_events'][pads[t]]['dest_warp_id'])]['x'], j['warp_events'][int(j['warp_events'][pads[t]]['dest_warp_id'])]['y'])
                for t in list(seen) if t in pads]
        more += [(7, 30)] if any(t in seen for t in pad_tiles - set(pads)) else []
        new = [t for t in more if t not in seen]
        if not new: break
        seen |= reachable(sm, new)
    walk = {(x, z) for z in range(H) for x in range(W) if sm['walk'][z][x]}
    unreach = sorted(walk - seen, key=lambda t: (t[1], t[0]))
    live = walk & seen
    walls = sorted({(x + dx, z + dz) for x, z in live for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                    if 0 <= x + dx < W and 0 <= z + dz < H and (x + dx, z + dz) not in walk}, key=lambda t: (t[1], t[0]))
    st = GL.bg(n, script='GymStatue')
    ft = []
    for (x, z), (c, k) in sorted(arrows.items()):
        if k < 4: ft.append(GL.T(258, 'out_65_dai2', rect=[x, z, x, z], stretch=True, rot={0: 0, 1: 90, 2: 180, 3: 270}[k]))
        else: ft.append(GL.T(304, 'c4g_mat', rect=[x, z, x, z], stretch=True))
    ft += [GL.T(334, 'gra_light02', rect=[x, z, x, z], stretch=True) for x, z in sorted(pad_tiles)]
    r = copy.deepcopy(ER.recipe(g))
    for k in ('matrix',): r.pop(k, None)
    r.update(map=n, origin=MG_ORIGIN, open=True,
             floor=[[x, z, x, z] for x, z in sorted(live | set(walls), key=lambda t: (t[1], t[0]))],
             floor_tex=ft, blocks=[dict(use='gl_mossdeep_wall', tiles=[list(t) for t in walls if list(t) not in st and
                                                                        t not in LEADER_TILES])],
             furniture=statues(n))
    if unreach: r['block'] = [list(t) for t in unreach]
    gym_variant(ER, g, "Emerald's Mossdeep Gym (26x36): small rooms floating in the dark, joined by warp pads (the light "
                "panels), the colored squares of arrow tiles and their floor switches (Black 2's switch mat), low white "
                "walls beside the rooms, the statues by the entrance. Tiles no pad or exit reaches are solid.", r)
    ox, oz = MG_ORIGIN
    ER.overlay(322, g, "the exits (6,35) (7,35) (the warp pads are step triggers, not warps).", warps={0: (6, 35), 1: (7, 35)})
    # people (Tate, Liza, the guide, the trainers) and the statues' plaques; Sapphire's switch signs and pad trigger go
    REPORT.extend(place_people(ER, g))
    ER.STORY_SET[('ch9.json', g, (12, 3))] = dict(at=[21, 6])            # MG_WarpToEntrance: Emerald's (21,6) -> (7,30)
    # the statues: Emerald-only rock objects
    objs = j['object_events']
    taken = {o['uid'] for _, o in story_objects(g) if o.get('kind', 'npc') == 'npc'} | \
            {o['uid'] for o in ER.STORY_NEW if o.get('map') == g and o.get('kind') == 'npc'}
    for i, o in enumerate(objs, 1):
        if o['graphics_id'] != 'OBJ_EVENT_GFX_TRICK_HOUSE_STATUE': continue
        uid = i if i not in taken else 100 + i
        ER.STORY_NEW.append(dict(kind='npc', map=g, at=[o['x'], o['y']], uid=uid, model=STATUE_MODEL, script=0, move=0, dir=1,
                                 what=f"statue (pokeemerald object {i}, TRICK_HOUSE_STATUE: Black 2's rock 206 stands in), "
                                      "carried by the rotating tiles (Emerald only)"))
    # who rides which color: uid (as placed) -> start tile, start facing
    uid_of = {}
    for f, o in story_objects(g):
        if o.get('kind', 'npc') != 'npc': continue
        at = tuple(ER.STORY_SET.get((f, g, o['uid']), {}).get('at', o['at']))
        uid_of[at] = (o['uid'], ER.STORY_SET.get((f, g, o['uid']), {}).get('dir', o.get('dir', 1)), (f, o['uid']))
    for o in ER.STORY_NEW:
        if o.get('map') == g and o.get('kind') == 'npc': uid_of[tuple(o['at'])] = (o['uid'], o.get('dir', 1), None)
    riders = {c: [] for c in range(5)}
    for t, (uid, d, ref) in uid_of.items():
        if t in arrows and arrows[t][1] < 4:
            riders[arrows[t][0]].append((uid, t, d))
            if ref is not None: ER.STORY_SET[(ref[0], g, ref[1])].update(move=0)     # (stands: its facing is the script's)
            else:
                for o in ER.STORY_NEW:
                    if o.get('map') == g and o.get('uid') == uid: o['move'] = 0
    sf = script_file(g)
    sw_tiles = {}
    for c in j['coord_events']:
        name = c['script'].split('_EventScript_')[-1]
        for k, col in enumerate(MG_COLORS):
            if name == col + 'FloorSwitch': sw_tiles.setdefault(k, []).append((c['x'], c['y']))
    pad_list = sorted(pads, key=lambda t: pads[t])
    labels = [f'EMG_Switch{MG_COLORS[k]}' for k in range(5)] + [f'EMG_Pad{pads[t]}' for t in pad_list]
    nums = dict(zip(labels, next_entries(sf, len(labels))))
    entries = [f'    ScriptEntry {lab:<20s}// {nums[lab]}: ' + (f'{lab[10:]} floor switch(es) {sw_tiles.get(MG_COLORS.index(lab[10:]), [])}'
               if lab.startswith('EMG_Switch') else 'warp pad') + ' (Emerald only)' for lab in labels]
    bodies, lists = [], set()
    for k, col in enumerate(MG_COLORS):
        work = MG_WORK0 + k
        body = [f'EMG_Switch{col}:                     // MossdeepCity_Gym_EventScript_{col}FloorSwitch (rotating tiles, color {k})',
                '    ActorsPauseAll', '    SEPlay SEQ_SE_FLD_127', '    VMSleep 8']
        for step in range(4):
            body.append(f'    WorkCmpConst 0x{work:04X}, {step}')
            body.append(f'    VMJumpIf CMP_EQ, L_EMG_{col}{step}')
        body.append(f'    VMJump L_EMG_{col}End')
        for step in range(4):
            body.append(f'L_EMG_{col}{step}:')
            for uid, t, d in sorted(riders[k]):
                x, z = t; face = d
                for _ in range(step):                       # where it is after `step` presses
                    dx, dz = DIRV[arrows[(x, z)][1]]; x, z = x + dx, z + dz; face = CCW[face]
                a = arrows[(x, z)][1]
                lst = f'Mv_EMG_{DIRN[a]}_{B2NAME[CCW[face]]}'; lists.add((DIRN[a], B2NAME[CCW[face]]))
                body.append(f'    ActorCmdExec {uid}, {lst}            // ({x},{z}) -> {DIRN[a]}, then faces {B2NAME[CCW[face]]}')
            body += ['    ActorCmdWait', f'    WorkSetConst 0x{work:04X}, {(step + 1) % 4}', f'    VMJump L_EMG_{col}End']
        body += [f'L_EMG_{col}End:', '    FinishAllEvents', '    ActorsUnpauseAll', '    VMHalt']
        bodies.append('\n'.join(body))
        for t in sw_tiles.get(k, []):
            ER.STORY_NEW.append(dict(kind='trigger', map=g, at=list(t), script=nums[f'EMG_Switch{col}'], var=0, value=0,
                                     what=f'{col.lower()} floor switch (Emerald only: EMG_Switch{col})'))
    for t in pad_list:
        i = pads[t]; d = j['warp_events'][int(j['warp_events'][i]['dest_warp_id'])]
        bodies.append(f'''EMG_Pad{i}:                          // warp pad ({t[0]},{t[1]}) -> ({d["x"]},{d["y"]}) (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, {d["x"] + ox}, 0, {d["y"] + oz}, 1
    h_fadescreen_from_black
    h_release''')
        ER.STORY_NEW.append(dict(kind='trigger', map=g, at=list(t), script=nums[f'EMG_Pad{i}'], var=0, value=0,
                                 what=f'warp pad -> ({d["x"]},{d["y"]}) (Emerald only: EMG_Pad{i})'))
    mv = [f'''Mv_EMG_{w}_{f}:
    lock_facing_direction
    walk_{w}
    unlock_facing_direction
    face_{f}
    step_end''' for w, f in sorted(lists)]
    ER.SCRIPT_BLOCKS.append((sf, 'mossdeep_entries', 'table', '#ifdef HOENN_EMERALD\n' + '\n'.join(entries) + '\n#endif'))
    ER.SCRIPT_BLOCKS.append((sf, 'mossdeep_entrance', ('after', r'^#define MG_ENTRANCE_Z'),
                             f'#ifdef HOENN_EMERALD\n#undef MG_ENTRANCE_X\n#undef MG_ENTRANCE_Z\n#define MG_ENTRANCE_X {7 + ox}                // Emerald (7,30) + the room origin\n#define MG_ENTRANCE_Z {30 + oz}\n#endif'))
    ER.SCRIPT_BLOCKS.append((sf, 'mossdeep_puzzle', 'end', '#ifdef HOENN_EMERALD\n' + '\n\n'.join(bodies) +
                             '\n    .balign 4, 0\n' + '\n    .balign 4, 0\n'.join(mv) + '\n    .balign 4, 0\n#endif'))
    REPORT.append(f'MossdeepCity_Gym: riders ' + '; '.join(f'{MG_COLORS[k]}: {sorted(v)}' for k, v in riders.items()) +
                  f'; unreachable walkable tiles made solid {unreach}')
