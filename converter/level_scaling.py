#!/usr/bin/env python3
"""How much higher Sapphire's trainer and wild levels should be once the player has a Gen 6-style Exp. Share.

    python3 converter/level_scaling.py            # prints the report, writes data/level_scaling.json

Everything is read from the local decomps, nothing is downloaded:
  external/pokeruby  trainers, parties, map scripts (story order, Sapphire branch), wild tables, Gen 3 exp yields,
                     growth tables, the Gen 3 exp formula (src/battle_script_commands.c atk23_getexp)
  external/pokebw2   Black 2's exp yields and growth tables (data/personal, data/growth_rates) and its exp formula
                     (src/ov167/btl_calc.c CalcBaseExpGain + AddExpAndEVs / ScaleExpGainedByLevel in overlay 167,
                     which are still assembly: `tools/dsd dis -c config/b2_us/arm9/config.yaml -a <dir> --overlay 167`)

Two playthroughs of the same story-ordered battle list are simulated:
  (a) Sapphire as designed: Gen 3 formula, the two main battlers share the KOs, no Exp. Share.
  (b) Black 2's formula, same battles and same main battlers, plus the Exp. Share (key item) from the point where
      Mr. Stone gives it: every party Pokemon that did not battle gets 50% of the base exp, scaled by its own level.
Opponents in (b) are scaled by new = f(L) = L + a * max(0, L - L0)^p (rounded, capped at 100) for everything met after
the Exp. Share; f is fitted (fixed point, since higher opponents also give more exp in (b)) so that every trainer
battle has the same opponent-minus-main-battler level gap in (b) as in (a). See notes/LEVEL_SCALING.md.
"""
import json, math, os, re, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import version  # noqa: E402  (HOENN_VERSION: which pokeruby branch the readers see)
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
BW2 = os.path.join(ROOT, 'external', 'pokebw2')
OUT_JSON = os.path.join(ROOT, 'data', 'level_scaling.json')

# ------------------------------------------------------------------------------------------------------------------
# Assumptions (change here; every one is printed in the report and written to the JSON)
# ------------------------------------------------------------------------------------------------------------------
STARTER = 'MUDKIP'          # player's starter; the rival (May) gets the one strong against it
N_WILD = 10                 # wild battles per "full" wild area (a route or a cave); areas below use 0.25-1.0 of it
MAIN_BATTLERS = 2           # (a) and (b): the first N party members fight; the lower-levelled one takes the next KO
EXP_SHARE_AFTER = 'granite' # segment after which the Exp. Share is on (Steven's letter delivered, Mr. Stone visited)
KEY_WEIGHT = 3.0            # weight of gym leaders / E4 / champion / rival / Wally / Aqua bosses in the fit
# party: (segment it joins in, species, level when caught). The starter is given at Lv5 (src/battle_setup.c:877).
PARTY_PLAN = [
    ('r101', 'MUDKIP', 5),
    ('r102', 'LOTAD', 4),
    ('r104s', 'TAILLOW', 5),
    ('woods', 'SHROOMISH', 6),
    ('r110', 'ELECTRIKE', 13),
    ('r112', 'NUMEL', 16),
]

# ------------------------------------------------------------------------------------------------------------------
# pokeruby: Sapphire branch of the scripts, trainers, wild tables, Gen 3 species data
# ------------------------------------------------------------------------------------------------------------------
def sapphire_lines(path):
    """Lines of an .inc with `.ifdef SAPPHIRE / .else / .endif` resolved for the build's version (Sapphire unless
    HOENN_VERSION=ruby; b2tools/version.py resolve_ifdef, the same result as this function's old Sapphire-only copy on
    every file read here: checked on all 406 pokeruby scripts by ruby_infra 2026-10-08)."""
    return version.resolve_ifdef(path)


def load_aliases(version_=None):  # constants/version.inc: TRAINER_MT_CHIMNEY_GRUNT_3 -> TRAINER_ARCHIE_3 etc. for Sapphire
    """The 28 version aliases of the build's version, or of version_ ('sapphire'/'ruby': gen_trainers.py pairs the twins)."""
    alias = {}
    for line in version.resolve_ifdef(f'{RUBY}/constants/version.inc', version_):
        m = re.match(r'\s*\.set\s+(TRAINER_\w+),\s*(TRAINER_\w+)', line)
        if m:
            alias[m.group(1)] = m.group(2)
    return alias


def load_trainers():
    parties, cur, lvl = {}, None, None
    for line in open(f'{RUBY}/src/data/trainer_parties.h', encoding='latin-1'):
        m = re.match(r'const struct \w+ (gTrainerParty_\w+)\[\]', line)
        if m:
            cur = m.group(1); parties[cur] = []; continue
        m = re.search(r'\.level = (\d+)', line)
        if m:
            lvl = int(m.group(1))
        m = re.search(r'\.species = SPECIES_(\w+)', line)
        if m:
            parties[cur].append((lvl, m.group(1)))
    trainers, cur = OrderedDict(), None
    for line in open(f'{RUBY}/src/data/trainers_en.h', encoding='latin-1'):
        m = re.match(r'\s*\[(TRAINER_\w+)\] =', line)
        if m:
            cur = m.group(1); trainers[cur] = {'id': cur}; continue
        if cur is None:
            continue
        for key, pat in (('class', r'\.trainerClass = TRAINER_CLASS_(\w+)'), ('name', r'\.trainerName = _\("(.*)"\)'),
                         ('double', r'\.doubleBattle = (\w+)'), ('party', r'\.party = \{\.\w+ = (\w+) \}')):
            m = re.search(pat, line)
            if m:
                v = m.group(1)
                trainers[cur][key] = v == 'TRUE' if key == 'double' else parties.get(v, []) if key == 'party' else v
    return trainers


def load_map_trainers(alias):
    """map -> [(trainer, x, y)] in script order, Sapphire branch, rematches left out. Positions from map.json."""
    import glob
    result = {}
    for path in sorted(glob.glob(f'{RUBY}/data/maps/*/scripts.inc')):
        mp = path.split('/')[-2]
        label, lab2t, order = None, {}, []
        for line in sapphire_lines(path):
            m = re.match(r'^(\w+)::', line)
            if m:
                label = m.group(1); continue
            m = re.match(r'\s*(trainerbattle\w*)\s+(.*)', line)
            if not m or 'rematch' in m.group(1):
                continue
            ids = [a for a in re.split(r'[,\s]+', m.group(2)) if a.startswith('TRAINER_') and not a.startswith('TRAINER_BATTLE_')]
            t = alias.get(ids[0], ids[0])
            lab2t.setdefault(label, t)
            if t not in order:
                order.append(t)
        if not order:
            continue
        pos = {}
        mj = json.load(open(f'{RUBY}/data/maps/{mp}/map.json'))
        for o in mj.get('object_events', []) or []:
            t = lab2t.get(o.get('script'))
            if t and t not in pos:
                pos[t] = (o['x'], o['y'])
        result[mp] = [(t, *pos.get(t, (None, None))) for t in order]
    return result


def load_wild():
    """MAP_X -> {'land'|'water'|'rock'|'fish': [(min, max, species, rate)]}, Sapphire tables only."""
    d = json.load(open(f'{RUBY}/src/data/wild_encounters.json'))['wild_encounter_groups'][0]
    rates = {f['type']: f['encounter_rates'] for f in d['fields']}
    out = {}
    for e in d['encounters']:
        if 'Ruby' in e['base_label']:
            continue
        t = {}
        for k, short in (('land_mons', 'land'), ('water_mons', 'water'), ('rock_smash_mons', 'rock'), ('fishing_mons', 'fish')):
            if k in e:
                t[short] = [(m['min_level'], m['max_level'], m['species'][8:], r) for m, r in zip(e[k]['mons'], rates[k])]
        out[e['map']] = t
    return out


GROWTH_NAMES = ['MEDIUM_FAST', 'ERRATIC', 'FLUCTUATING', 'MEDIUM_SLOW', 'FAST', 'SLOW']  # include/pokemon.h:343


def load_gen3_species():
    text = open(f'{RUBY}/src/data/pokemon/base_stats.h', encoding='latin-1').read()
    out = {}
    for m in re.finditer(r'\[SPECIES_(\w+)\] =\s*\{(.*?)\n    \}', text, re.S):
        y = re.search(r'\.expYield = (\d+)', m.group(2))
        g = re.search(r'\.growthRate = GROWTH_(\w+)', m.group(2))
        if y and g:
            out[m.group(1)] = (int(y.group(1)), g.group(1))
    return out


def load_gen3_tables():
    tables, cur = [], None
    for line in open(f'{RUBY}/src/data/pokemon/experience_tables.h', encoding='latin-1'):
        if '{ //' in line:
            cur = []; tables.append(cur); continue
        m = re.match(r'\s*(\d+),?\s*// (\d+)', line)
        if m and cur is not None:
            cur.append(int(m.group(1)))
    return {GROWTH_NAMES[i]: tables[i] for i in range(6)}


# ------------------------------------------------------------------------------------------------------------------
# pokebw2: Black 2's species data and growth tables
# ------------------------------------------------------------------------------------------------------------------
def load_bw2_species():
    import glob
    out = {}
    for path in sorted(glob.glob(f'{BW2}/data/personal/*.s')):
        text = open(path, encoding='utf-8').read()
        n = re.search(r'// SPECIES_(\w+)', text)
        b = re.search(r'BaseExp (\d+)', text)
        g = re.search(r'GrowthRate GROWTH_(\w+)', text)
        if n and b and g and n.group(1) not in out:
            out[n.group(1)] = (int(b.group(1)), g.group(1))
    return out


def load_bw2_tables():
    import glob
    out = {}
    for path in sorted(glob.glob(f'{BW2}/data/growth_rates/000[0-5]_*.s')):
        text = open(path, encoding='utf-8').read()
        name = re.search(r'// GROWTH_(\w+)', text).group(1)
        out[name] = [int(e) for _, e in re.findall(r'Level (\d+), (\d+)', text)]
    return out


# ------------------------------------------------------------------------------------------------------------------
# The two exp formulas
# ------------------------------------------------------------------------------------------------------------------
def gen3_exp(yield3, level, trainer):
    """pokeruby src/battle_script_commands.c atk23_getexp: 3379 (yield*L/7), 3393 (/ participants, at least 1),
    3447-3448 (trainer battle *150/100). One participant, no held Exp. Share, not traded."""
    e = max(1, yield3 * level // 7)
    if trainer:
        e = e * 150 // 100
    return e


def gen5_base(base5, level, trainer):
    """Black 2 CalcBaseExpGain (src/ov167/btl_calc.c:481-494): base_exp * L / 5 (base_exp = personal field 9 =
    offset 0x22, PML_PersonalGetParam 0x020202ac); AddExpAndEVs 0x021aee3c-0x021aee52: battle type 1 (trainer)
    -> *15/10."""
    e = base5 * level // 5
    if trainer:
        e = e * 15 // 10
    return e


def _fx_sqrt_int(v):
    # FX_Sqrt(v << 12) (main 0x02073e28 + FX_GetSqrtResult 0x02073f20): 64-bit hardware sqrt of (x << 32),
    # then (r + 0x200) >> 10 -> sqrt(v) in 20.12 fixed point, rounded
    return (math.isqrt((v << 12) << 32) + 0x200) >> 10


_POW25 = {}
def _pow25(v):  # ScaleExpGainedByLevel: (FX_Sqrt(v) * v * v) >> 12, 32-bit multiply
    if v not in _POW25:
        _POW25[v] = ((_fx_sqrt_int(v) * v * v) & 0xFFFFFFFF) >> 12
    return _POW25[v]


def gen5_scale(exp, player_level, enemy_level):
    """ScaleExpGainedByLevel (ov167 0x021af0cc): exp * (2L+10)^2.5 / (L+Lp+10)^2.5 + 1, 64-bit divide."""
    return exp * _pow25(2 * enemy_level + 10) // _pow25(enemy_level + player_level + 10) + 1


# ------------------------------------------------------------------------------------------------------------------
# Story order (Sapphire, main path, player Brendan + STARTER, rival May)
# ------------------------------------------------------------------------------------------------------------------
# rival battle per starter (VAR_STARTER_MON 0/1/2 = Treecko/Torchic/Mudkip, src/starter_choose.c:50), from the
# `switch VAR_STARTER_MON` in data/maps/Route103/scripts.inc:30-32 (battles 52-62), Route110/scripts.inc:364-367
# (371-381), Route119/scripts.inc:91-94 (98-108), LilycoveCity/scripts.inc:254-257 (306-316)
RIVAL = {
    'TREECKO': ['TRAINER_MAY_4', 'TRAINER_MAY_5', 'TRAINER_MAY_6', 'TRAINER_MAY_LILYCOVE_TREECKO'],
    'TORCHIC': ['TRAINER_MAY_7', 'TRAINER_MAY_8', 'TRAINER_MAY_9', 'TRAINER_MAY_LILYCOVE_TORCHIC'],
    'MUDKIP': ['TRAINER_MAY_1', 'TRAINER_MAY_2', 'TRAINER_MAY_3', 'TRAINER_MAY_LILYCOVE_MUDKIP'],
}
# never taken from a map automatically: rival variants (chosen above), post-game Wally (VictoryRoad_1F:94)
AUTO_EXCLUDE = {t for v in RIVAL.values() for t in v} | {t.replace('MAY', 'BRENDAN') for v in RIVAL.values() for t in v} \
    | {'TRAINER_WALLY_3'}

# event kinds: ('catch', species, level) ('wild', MAP, kind, weight) ('map', Map, include|None, exclude|None)
#              ('trainer', TRAINER_X, key label|None) ('first', species, level)  ('static', species, level, label)
# the leader of a gym map is moved to the end of that map's battles and labelled automatically.
R = RIVAL[STARTER]
SEGMENTS = [
    ('r101', 'Route 101 (starter, Birch rescue)', [('first', 'POOCHYENA', 2), ('wild', 'MAP_ROUTE101', 'land', 1.0)]),
    ('r103', 'Route 103 (rival 1)', [('wild', 'MAP_ROUTE103', 'land', 0.5), ('trainer', R[0], 'Rival May 1 (Route 103)')]),
    ('r102', 'Route 102', [('wild', 'MAP_ROUTE102', 'land', 1.0), ('map', 'Route102', None, None)]),
    ('r104s', 'Route 104 south', [('wild', 'MAP_ROUTE104', 'land', 0.5),
                                  ('map', 'Route104', ['TRAINER_WINSTON_1', 'TRAINER_BILLY'], None)]),
    ('woods', 'Petalburg Woods', [('wild', 'MAP_PETALBURG_WOODS', 'land', 1.0), ('map', 'PetalburgWoods', None, None)]),
    ('r104n', 'Route 104 north', [('wild', 'MAP_ROUTE104', 'land', 0.5),
                                  ('map', 'Route104', ['TRAINER_HALEY_1', 'TRAINER_CINDY_1', 'TRAINER_GINA_AND_MIA_1', 'TRAINER_IVAN'], None)]),
    ('gym1', 'Rustboro Gym', [('map', 'RustboroCity_Gym', None, None)]),
    ('r116', 'Route 116 + Rusturf Tunnel', [('wild', 'MAP_ROUTE116', 'land', 1.0), ('map', 'Route116', None, None),
                                            ('wild', 'MAP_RUSTURF_TUNNEL', 'land', 0.5),
                                            ('map', 'RusturfTunnel', ['TRAINER_GRUNT_15'], None)]),
    ('gym2', 'Dewford Gym', [('map', 'DewfordTown_Gym', None, None)]),
    ('granite', 'Granite Cave (letter to Steven)', [('wild', 'MAP_GRANITE_CAVE_1F', 'land', 0.5),
                                                    ('wild', 'MAP_GRANITE_CAVE_B1F', 'land', 0.25),
                                                    ('wild', 'MAP_GRANITE_CAVE_B2F', 'land', 0.25)]),
    ('r109', 'Route 109 beach + Seashore House', [('map', 'Route109', ['TRAINER_HUEY', 'TRAINER_EDMOND', 'TRAINER_RICKY_1', 'TRAINER_LOLA_1'], None),
                                                  ('map', 'Route109_SeashoreHouse', None, None)]),
    ('museum', 'Slateport Oceanic Museum', [('trainer', 'TRAINER_GRUNT_19', None), ('trainer', 'TRAINER_GRUNT_20', 'Aqua grunts (Museum)')]),
    ('r110', 'Route 110 (rival 2)', [('wild', 'MAP_ROUTE110', 'land', 1.0),
                                     ('map', 'Route110', ['TRAINER_EDWARD', 'TRAINER_JACLYN', 'TRAINER_EDWIN_1', 'TRAINER_DALE', 'TRAINER_TIMMY', 'TRAINER_ISABEL_1'], None),
                                     ('trainer', R[1], 'Rival May 2 (Route 110)')]),
    ('gym3', 'Mauville (Wally 1, Route 118 west, gym)', [('trainer', 'TRAINER_WALLY_2', 'Wally 1 (Mauville)'),
                                                          ('map', 'Route118', ['TRAINER_ROSE_1', 'TRAINER_WADE', 'TRAINER_DALTON_1'], None),
                                                          ('map', 'MauvilleCity_Gym', None, None)]),
    ('r117', 'Route 117', [('wild', 'MAP_ROUTE117', 'land', 1.0), ('map', 'Route117', None, None)]),
    ('r112', 'Route 111 south + Route 112 + Fiery Path', [('map', 'Route111', ['TRAINER_TRAVIS', 'TRAINER_IRENE'], None),
                                                          ('wild', 'MAP_ROUTE112', 'land', 0.5), ('map', 'Route112', None, None),
                                                          ('wild', 'MAP_FIERY_PATH', 'land', 0.5)]),
    ('r113', 'Route 111 north + Route 113', [('map', 'Route111', ['TRAINER_WILTON_1', 'TRAINER_BROOKE_1', 'TRAINER_DAISUKE'], None),
                                             ('wild', 'MAP_ROUTE113', 'land', 1.0), ('map', 'Route113', None, None)]),
    ('r114', 'Route 114 + Meteor Falls', [('wild', 'MAP_ROUTE114', 'land', 1.0), ('map', 'Route114', None, None),
                                          ('wild', 'MAP_METEOR_FALLS_1F_1R', 'land', 0.5)]),
    ('chimney', 'Mt. Chimney', [('trainer', 'TRAINER_GRUNT_13', None), ('trainer', 'TRAINER_MATT_2', 'Aqua Admin Matt (Mt. Chimney)'),
                                ('trainer', 'TRAINER_ARCHIE_3', 'Archie 1 (Mt. Chimney)'),
                                ('map', 'MtChimney', None, ['TRAINER_GRUNT_13', 'TRAINER_MATT_2'])]),
    ('jagged', 'Jagged Pass', [('wild', 'MAP_JAGGED_PASS', 'land', 1.0), ('map', 'JaggedPass', None, None)]),
    ('gym4', 'Lavaridge Gym', [('map', 'LavaridgeTown_Gym_1F', None, None)]),
    ('gym5', 'Petalburg Gym', [('map', 'PetalburgCity_Gym', None, None)]),
    ('r118', 'Route 118 east (Surf)', [('wild', 'MAP_ROUTE118', 'land', 1.0),
                                       ('map', 'Route118', ['TRAINER_BARNY', 'TRAINER_CHESTER', 'TRAINER_PERRY'], None)]),
    ('r119', 'Route 119 (rival 3)', [('wild', 'MAP_ROUTE119', 'land', 1.0), ('map', 'Route119', None, None),
                                     ('trainer', R[2], 'Rival May 3 (Route 119)')]),
    ('weather', 'Weather Institute', [('map', 'Route119_WeatherInstitute_1F', None, None),
                                      ('map', 'Route119_WeatherInstitute_2F', None, ['TRAINER_SHELLY_1']),
                                      ('trainer', 'TRAINER_SHELLY_1', 'Aqua Admin Shelly (Weather Institute)')]),
    ('gym6', 'Route 120 + Fortree Gym', [('wild', 'MAP_ROUTE120', 'land', 1.0), ('map', 'Route120', None, None),
                                         ('map', 'FortreeCity_Gym', None, None)]),
    ('r121', 'Route 121 + Lilycove (rival 4)', [('wild', 'MAP_ROUTE121', 'land', 1.0), ('map', 'Route121', None, None),
                                                ('trainer', R[3], 'Rival May 4 (Lilycove)')]),
    ('pyre', 'Mt. Pyre exterior + summit', [('wild', 'MAP_MT_PYRE_EXTERIOR', 'land', 0.5), ('wild', 'MAP_MT_PYRE_SUMMIT', 'land', 0.5),
                                            ('trainer', 'TRAINER_GRUNT_22', None), ('trainer', 'TRAINER_GRUNT_23', None),
                                            ('trainer', 'TRAINER_GRUNT_24', None)]),
    ('hideout', 'Aqua Hideout', [('map', 'AquaHideout_1F', None, None), ('map', 'AquaHideout_B1F', None, None),
                                 ('map', 'AquaHideout_B2F', None, ['TRAINER_MATT_1']),
                                 ('trainer', 'TRAINER_MATT_1', 'Aqua Admin Matt (Aqua Hideout)')]),
    ('gym7', 'Route 124 + Mossdeep Gym', [('wild', 'MAP_ROUTE124', 'water', 0.5), ('map', 'Route124', None, None),
                                          ('map', 'MossdeepCity_Gym', None, None)]),
    ('r127', 'Routes 127-128', [('wild', 'MAP_ROUTE127', 'water', 0.5), ('map', 'Route127', None, None),
                                ('map', 'Route128', None, None)]),
    ('seafloor', 'Seafloor Cavern', [('wild', 'MAP_SEAFLOOR_CAVERN_ROOM1', 'land', 1.0),
                                     ('map', 'SeafloorCavern_Room1', None, None),
                                     ('trainer', 'TRAINER_SHELLY_2', 'Aqua Admin Shelly (Seafloor Cavern)'),
                                     ('map', 'SeafloorCavern_Room4', None, None),
                                     ('trainer', 'TRAINER_ARCHIE_2', 'Archie 2 (Seafloor Cavern)')]),
    ('origin', 'Route 126 + Sootopolis + Cave of Origin', [('map', 'Route126', None, None),
                                                           ('wild', 'MAP_CAVE_OF_ORIGIN_1F', 'land', 1.0),
                                                           ('static', 'KYOGRE', 45, 'Kyogre (Cave of Origin, caught: no exp)')]),
    ('gym8', 'Sootopolis Gym', [('map', 'SootopolisCity_Gym_B1F', None, None), ('map', 'SootopolisCity_Gym_1F', None, None)]),
    ('vroad', 'Victory Road', [('trainer', 'TRAINER_WALLY_1', 'Wally 2 (Victory Road)'),
                               ('wild', 'MAP_VICTORY_ROAD_1F', 'land', 0.5), ('map', 'VictoryRoad_1F', None, ['TRAINER_WALLY_1']),
                               ('wild', 'MAP_VICTORY_ROAD_B1F', 'land', 0.25), ('map', 'VictoryRoad_B1F', None, None),
                               ('wild', 'MAP_VICTORY_ROAD_B2F', 'land', 0.25), ('map', 'VictoryRoad_B2F', None, None)]),
    ('league', 'Elite Four + Champion', [('trainer', 'TRAINER_SIDNEY', 'Elite Four Sidney'), ('trainer', 'TRAINER_PHOEBE', 'Elite Four Phoebe'),
                                         ('trainer', 'TRAINER_GLACIA', 'Elite Four Glacia'), ('trainer', 'TRAINER_DRAKE', 'Elite Four Drake'),
                                         ('trainer', 'TRAINER_STEVEN', 'Champion Steven')]),
]
GYM_LEADERS = {'TRAINER_ROXANNE': 'Gym 1 Roxanne', 'TRAINER_BRAWLY': 'Gym 2 Brawly', 'TRAINER_WATTSON': 'Gym 3 Wattson',
               'TRAINER_FLANNERY': 'Gym 4 Flannery', 'TRAINER_NORMAN': 'Gym 5 Norman', 'TRAINER_WINONA': 'Gym 6 Winona',
               'TRAINER_TATE_AND_LIZA': 'Gym 7 Tate & Liza', 'TRAINER_WALLACE': 'Gym 8 Wallace'}


def build_story(trainers, map_trainers, wild):
    """Flatten SEGMENTS into an event list; each event carries its segment and whether it is before the Exp. Share."""
    events, seen = [], set()
    catches = {}
    for seg, sp, lv in PARTY_PLAN:
        catches.setdefault(seg, []).append((sp, lv))
    share_on = False
    for seg, label, spec in SEGMENTS:
        for sp, lv in catches.get(seg, []):
            events.append({'kind': 'catch', 'species': sp, 'level': lv, 'seg': seg, 'pre_share': not share_on})
        for item in spec:
            if item[0] == 'first':
                events.append({'kind': 'wild_fixed', 'species': item[1], 'level': item[2], 'seg': seg, 'pre_share': not share_on,
                               'label': 'Birch rescue (src/battle_controllers.c:104)'})
            elif item[0] == 'static':
                events.append({'kind': 'static', 'species': item[1], 'level': item[2], 'seg': seg, 'pre_share': not share_on,
                               'label': item[3]})
            elif item[0] == 'wild':
                _, mp, kind, w = item
                assert mp in wild and kind in wild[mp], (mp, kind)
                events.append({'kind': 'wild', 'map': mp, 'table': kind, 'count': w * N_WILD, 'seg': seg, 'pre_share': not share_on})
            else:
                if item[0] == 'trainer':
                    ids = [(item[1], item[2])]
                else:
                    _, mp, inc, exc = item
                    have = [t for t, x, y in map_trainers[mp] if t not in AUTO_EXCLUDE]
                    if inc is not None:
                        assert all(t in have for t in inc), (mp, inc, have)
                        have = [t for t in have if t in inc]
                    if exc:
                        have = [t for t in have if t not in exc]
                    leaders = [t for t in have if t in GYM_LEADERS]
                    ids = [(t, None) for t in have if t not in GYM_LEADERS] + [(t, GYM_LEADERS[t]) for t in leaders]
                for t, key in ids:
                    assert t not in seen, t
                    seen.add(t)
                    tr = trainers[t]
                    events.append({'kind': 'trainer', 'id': t, 'name': tr['name'], 'class': tr['class'], 'key': key,
                                   'party': tr['party'], 'seg': seg, 'pre_share': not share_on})
        if seg == EXP_SHARE_AFTER:
            share_on = True
            events.append({'kind': 'exp_share', 'seg': seg, 'pre_share': False})
        events.append({'kind': 'seg_end', 'seg': seg, 'label': label, 'pre_share': not share_on})
    return events


# ------------------------------------------------------------------------------------------------------------------
# Simulation
# ------------------------------------------------------------------------------------------------------------------
class Mon:
    def __init__(self, species, level, table):
        self.species, self.table = species, table
        self.exp = float(table[level])
        self.level = level

    def add(self, e):
        if self.level >= 100:
            return
        self.exp = min(self.exp + e, self.table[100])
        while self.level < 100 and self.exp >= self.table[self.level + 1]:
            self.level += 1

    def flevel(self):  # level with the fraction towards the next one, for smooth comparisons
        if self.level >= 100:
            return 100.0
        lo, hi = self.table[self.level], self.table[self.level + 1]
        return self.level + (self.exp - lo) / (hi - lo)


def wild_distribution(slots, levelmap):
    """[(species, level, probability)] for a wild table; Gen 3 picks a level uniformly in [min, max]."""
    total = sum(r for *_, r in slots)
    out = []
    for lo, hi, sp, r in slots:
        lo2, hi2 = levelmap(lo), levelmap(hi)
        n = hi2 - lo2 + 1
        for lv in range(lo2, hi2 + 1):
            out.append((sp, lv, r / total / n))
    return out


class Sim:
    """mode 'a': Gen 3 formula, no Exp. Share.  mode 'b': Black 2 formula + Gen 6 Exp. Share once received."""

    def __init__(self, mode, data, scale=None, playstyle='mains'):
        self.mode, self.d, self.scale = mode, data, scale or (lambda L: L)
        self.playstyle = playstyle
        self.party, self.share = [], False
        self.log, self.snap = [], {}

    def lv(self, L, pre_share):
        return L if (self.mode == 'a' or pre_share) else self.scale(L)

    def fighters(self):
        if self.playstyle == 'solo':
            return self.party[:1]
        if self.playstyle == 'rotate':
            return self.party
        return self.party[:MAIN_BATTLERS]

    def participant(self):
        return min(self.fighters(), key=lambda m: m.flevel())

    def gain(self, species, level, trainer, weight=1.0):
        p = self.participant()
        if self.mode == 'a':
            p.add(weight * gen3_exp(self.d['y3'][species][0], level, trainer))
            return
        base = gen5_base(self.d['y5'][species][0], level, trainer)
        p.add(weight * gen5_scale(base, p.level, level))
        if self.share:
            half = base >> 1  # the existing held-item code also halves with `exp >> 1` (AddExpAndEVs .L_021aeea6)
            for m in self.party:
                if m is not p:
                    m.add(weight * (gen5_scale(half, m.level, level) if half else 0))

    def state(self):
        mains = self.fighters()  # the Pokemon that do the battling: the main battlers (or the whole party)
        return {'main': sum(m.flevel() for m in mains) / len(mains),
                'top': max(m.flevel() for m in self.party),
                'avg': sum(m.flevel() for m in self.party) / len(self.party),
                'levels': [m.level for m in self.party]}

    def run(self, events):
        for ev in events:
            k = ev['kind']
            if k == 'catch':
                tab = self.d['t3' if self.mode == 'a' else 't5'][self.d['y3' if self.mode == 'a' else 'y5'][ev['species']][1]]
                self.party.append(Mon(ev['species'], ev['level'], tab))
            elif k == 'exp_share':
                self.share = self.mode == 'b'
            elif k == 'seg_end':
                self.snap[ev['seg']] = self.state()
            elif k == 'wild_fixed':
                self.gain(ev['species'], ev['level'], False)
            elif k == 'static':
                self.log.append((ev, self.state(), [self.lv(ev['level'], ev['pre_share'])]))
            elif k == 'wild':
                slots = self.d['wild'][ev['map']][ev['table']]
                dist = wild_distribution(slots, lambda L: self.lv(L, ev['pre_share']))
                n = ev['count']
                whole = int(n)
                for i in range(whole + (1 if n > whole else 0)):
                    w = 1.0 if i < whole else n - whole
                    p = self.participant()
                    # expected exp of one battle with the participant fixed for that battle
                    if self.mode == 'a':
                        p.add(w * sum(pr * gen3_exp(self.d['y3'][sp][0], lv, False) for sp, lv, pr in dist))
                    else:
                        others = [m for m in self.party if m is not p] if self.share else []
                        gp, go = 0.0, [0.0] * len(others)
                        for sp, lv, pr in dist:
                            base = gen5_base(self.d['y5'][sp][0], lv, False)
                            gp += pr * gen5_scale(base, p.level, lv)
                            for j, m in enumerate(others):
                                go[j] += pr * (gen5_scale(base >> 1, m.level, lv) if base >> 1 else 0)
                        p.add(w * gp)
                        for j, m in enumerate(others):
                            m.add(w * go[j])
            elif k == 'trainer':
                before = self.state()
                opp = [self.lv(L, ev['pre_share']) for L, sp in ev['party']]
                self.log.append((ev, before, opp))
                for (L, sp), L2 in zip(ev['party'], opp):
                    self.gain(sp, L2, True)
        return self


# ------------------------------------------------------------------------------------------------------------------
# The curve and its fit
# ------------------------------------------------------------------------------------------------------------------
def curve(a, L0, p):
    def f(L):
        return L + a * max(0.0, L - L0) ** p
    return f


def apply_curve(params):
    f = curve(*params)
    return lambda L: min(100, int(math.floor(f(L) + 0.5)))


def fit(points):
    """points: [(L, target, weight)]. f(L) - L = a * g(L), g = max(0, L - L0)^p: a is linear least squares,
    L0 and p by grid search."""
    agg = {}
    for L, T, w in points:
        s = agg.setdefault(L, [0.0, 0.0])
        s[0] += w; s[1] += w * (T - L)
    pts = [(L, w, sw / w) for L, (w, sw) in agg.items()]
    best = None
    for i in range(0, 61):
        L0 = 0.5 * i
        for j in range(0, 41):
            p = 0.5 + 0.05 * j
            g = [(w, max(0.0, L - L0) ** p, d) for L, w, d in pts]
            sgg = sum(w * x * x for w, x, d in g)
            if sgg == 0:
                continue
            a = max(0.0, sum(w * x * d for w, x, d in g) / sgg)
            err = sum(w * (a * x - d) ** 2 for w, x, d in g)
            if best is None or err < best[0]:
                best = (err, a, L0, p)
    err, a, L0, p = best
    rms = math.sqrt(err / sum(w for _, w, _ in pts))
    return (a, L0, p), rms


def fit_points(sa, sb, metric_b='main'):
    """Per trainer battle after the Exp. Share: keep (opponent L) - (player's battling level) as in (a).
    (a) is always measured on its main battlers; (b) on its main battlers ('main') or its whole party ('avg')."""
    pts = []
    for (ev, st_a, opp_a), (_, st_b, _) in zip(sa.log, sb.log):
        if ev['kind'] != 'trainer' or ev['pre_share']:
            continue
        w = (KEY_WEIGHT if ev['key'] else 1.0) / len(ev['party'])
        for L, sp in ev['party']:
            pts.append((L, L + st_b[metric_b] - st_a['main'], w))
    return pts


def solve(data, events, style_a='mains', style_b='mains', metric_b='main', iters=40):
    """Fixed point: simulate (b) with the current curve, refit the curve to the gaps of (a), repeat."""
    sa = Sim('a', data, playstyle=style_a).run(events)
    params, n = (0.0, 0.0, 1.0), 0
    for n in range(1, iters + 1):
        sb = Sim('b', data, scale=apply_curve(params), playstyle=style_b).run(events)
        new, rms = fit(fit_points(sa, sb, metric_b))
        if all(abs(x - y) < 1e-6 for x, y in zip(new, params)):
            break
        if n > 25:  # rounding to whole levels can make two neighbouring grid points alternate: settle between them
            new = tuple((x + y) / 2 for x, y in zip(new, params))
        params = new
    sb = Sim('b', data, scale=apply_curve(params), playstyle=style_b).run(events)
    s0 = Sim('b', data, playstyle=style_b).run(events)  # (b) with Sapphire's levels unchanged
    return params, sa, sb, s0, n, rms


# ------------------------------------------------------------------------------------------------------------------
# Emerald (HOENN_VERSION=emerald; emerald_data 2026-10-12, notes/EMERALD.md EMERALD-1)
# ------------------------------------------------------------------------------------------------------------------
# The curve maps a level to a level (it makes up for Black 2's exp formula and the Exp. Share), so Emerald can use
# Sapphire's as it is (converter/gen_trainers.py applies data/level_scaling.json "curve.table" to Emerald's parties, as
# gen_encounters.py does to its wild tables) if fitting it on Emerald's own levels gives the same curve. This check refits
# it with the same story order and assumptions, but every Sapphire trainer replaced by Emerald's trainer of the same slot
# (both decomps number the slots alike; the same person, or the one playing the role: ROLE_EMERALD) and Emerald's wild
# tables, and compares the two curves. Emerald's new battles (the Rustboro rival, Magma Hideout, Space Center) are not
# in Sapphire's story order; they add a little exp, which the comparison of the key battles below shows is not needed.
ROLE_EMERALD = {'TRAINER_MATT_2': 'TRAINER_TABITHA_MT_CHIMNEY', 'TRAINER_ARCHIE_3': 'TRAINER_MAXIE_MT_CHIMNEY',
                'TRAINER_WALLACE': 'TRAINER_JUAN_1', 'TRAINER_STEVEN': 'TRAINER_WALLACE'}


def emerald_check():
    import gen_trainers as G
    import gen_encounters as GE
    alias = load_aliases('sapphire')
    trainers = load_trainers()
    em = G.load_trainers_emerald(G.load_parties_emerald())
    rn, en = G.trainer_numbers(RUBY), G.trainer_numbers(G.EMERALD)
    e_by_num = {v: k for k, v in en.items()}
    swapped = kept = 0
    for t, tr in trainers.items():
        e = em.get(ROLE_EMERALD.get(t) or e_by_num.get(rn.get(t)))
        if not e or not e.get('party') or (t not in ROLE_EMERALD and (e.get('name'), e.get('class')) != (tr.get('name'), tr.get('class'))):
            kept += 1; continue
        tr['party'] = [(m['level'], m['species'][len('SPECIES_'):]) for m in e['party']]; swapped += 1
    map_trainers = load_map_trainers(alias)
    wild = load_wild()
    ew = json.load(open(os.path.join(G.EMERALD, 'src', 'data', 'wild_encounters.json')))
    rates = {f['type']: f['encounter_rates'] for f in next(g for g in ew['wild_encounter_groups'] if g.get('label') == 'gWildMonHeaders')['fields']}
    for mp, e in GE.wild_tables('emerald').items():
        t = {}
        for k, short in (('land_mons', 'land'), ('water_mons', 'water'), ('rock_smash_mons', 'rock'), ('fishing_mons', 'fish')):
            if k in e:
                t[short] = [(m['min_level'], m['max_level'], m['species'][8:], r) for m, r in zip(e[k]['mons'], rates[k])]
        if mp in wild: wild[mp] = t
    y3, t3 = load_gen3_species(), load_gen3_tables()
    y5, t5 = load_bw2_species(), load_bw2_tables()
    data = {'y3': y3, 't3': t3, 'y5': y5, 't5': t5, 'wild': wild}
    events = build_story(trainers, map_trainers, wild)
    params, sa, sb, s0, iters, rms = solve(data, events)
    old = json.load(open(OUT_JSON))['curve']
    f_e, f_s = apply_curve(params), apply_curve((old['a'], old['L0'], old['p']))
    diff = [(L, f_s(L), f_e(L)) for L in range(1, 101) if f_s(L) != f_e(L)]
    a, L0, p = params
    print('# Emerald: Sapphire\'s Exp. Share curve or a refit? (converter/level_scaling.py, HOENN_VERSION=emerald)\n')
    print(f'Sapphire story order, {swapped} trainers with Emerald\'s party of the same slot ({kept} kept Sapphire\'s: no '
          f'Emerald twin), Emerald\'s wild tables; same assumptions ({iters} fixed-point iterations, fit rms {rms:.2f} levels)')
    print(f'  Sapphire: f(L) = L + {old["a"]:.4f} * max(0, L - {old["L0"]:.1f})^{old["p"]:.2f}')
    print(f'  Emerald:  f(L) = L + {a:.4f} * max(0, L - {L0:.1f})^{p:.2f}')
    print(f'  levels 1-100 where the two curves differ: {len(diff)}' + (f' (largest {max(abs(x - y) for _, x, y in diff)} '
          f'level): ' + ', '.join(f'{L}: {x} vs {y}' for L, x, y in diff[:20]) if diff else ''))
    sb_s = Sim('b', data, scale=f_s).run(events)
    def gap_rms(sim, prm):     # fit()'s error measure for given parameters on Emerald's battles (levels)
        agg = {}
        for L, T, w in fit_points(sa, sim):
            x = agg.setdefault(L, [0.0, 0.0]); x[0] += w; x[1] += w * (T - L)
        num = sum(w * (prm[0] * max(0.0, L - prm[1]) ** prm[2] - sw / w) ** 2 for L, (w, sw) in agg.items())
        return math.sqrt(num / sum(w for w, _ in agg.values()))
    rms_s = gap_rms(sb_s, (old['a'], old['L0'], old['p']))
    print(f'  how well each curve keeps Emerald\'s level gaps after the Exp. Share (rms, levels): Sapphire\'s {rms_s:.2f}, '
          f'refit {rms:.2f}')
    print('\n## Key battles in Emerald (its own levels): opponent ace, player main battlers (a) Gen 3, (b) Black 2 + Exp. Share '
          'with Sapphire\'s curve / with the refit')
    for (ev, st_a, _), (_, st_b, opp_b), (_, st_s, opp_s) in zip(sa.log, sb.log, sb_s.log):
        if ev.get('key') and ev['kind'] == 'trainer':
            ace = max(L for L, _ in ev['party'])
            print(f"  {ev['key'][:34]:34s} ace {ace:3d} -> {max(opp_s):3d} / {max(opp_b):3d}   main (a) {st_a['main']:5.1f}  "
                  f"(b) {st_s['main']:5.1f} / {st_b['main']:5.1f}   gap (a) {ace - st_a['main']:+5.1f}  (b) {max(opp_s) - st_s['main']:+5.1f}")
    # The decision (emerald_data 2026-10-12): reuse Sapphire's curve when the refit keeps Emerald's gaps better by less
    # than a quarter of a level (rms). Measured: Sapphire's 0.50, refit 0.40; the refit is 1 level higher at most levels
    # (2 at a few, e.g. the Champion's ace 64 vs 66). That is less than the model's own uncertainty (Sapphire's
    # sensitivity table, data/level_scaling.json: 5 or 20 instead of 10 wild battles per route move the curve by 1-2
    # levels), and this check leaves out Emerald's extra battles (Rustboro rival, new route trainers, Magma Hideout,
    # Space Center), whose exp would pull a refit back towards Sapphire's curve.
    reuse = rms_s - rms < 0.25
    verdict = (f'reuse Sapphire\'s curve (the refit keeps Emerald\'s gaps only {rms_s - rms:.2f} level better)' if reuse else
               f'refit (it keeps Emerald\'s gaps {rms_s - rms:.2f} level better)')
    print(f'\nVerdict: {verdict}. Nothing written (data/level_scaling.json stays Sapphire\'s; gen_trainers.py applies its '
          f'curve.table to Emerald\'s parties, gen_encounters.py to Emerald\'s wild tables).')
    return params, diff


# ------------------------------------------------------------------------------------------------------------------
def main():
    global N_WILD, EXP_SHARE_AFTER, MAIN_BATTLERS
    if version.is_ruby():   # the curve is fitted once on Sapphire and serves both versions (notes/RUBY.md 3.2 "Wild")
        raise SystemExit('level_scaling.py: data/level_scaling.json already holds every Ruby trainer and the curve is '
                         'species-independent: run it without HOENN_VERSION=ruby')
    if version.is_emerald():   # EMERALD-1: the check that Sapphire's curve serves Emerald too (writes nothing)
        return emerald_check()
    alias = load_aliases()
    trainers = load_trainers()
    map_trainers = load_map_trainers(alias)
    wild = load_wild()
    y3, t3 = load_gen3_species(), load_gen3_tables()
    y5, t5 = load_bw2_species(), load_bw2_tables()
    data = {'y3': y3, 't3': t3, 'y5': y5, 't5': t5, 'wild': wild}
    tables_equal = all(t3[g][2:101] == t5[g][2:101] for g in GROWTH_NAMES)  # Lv1 is 1 in pokeruby, 0 in Black 2

    events = build_story(trainers, map_trainers, wild)
    species_used = {sp for ev in events if ev['kind'] == 'trainer' for _, sp in ev['party']}
    species_used |= {s for ev in events if ev['kind'] == 'wild' for *_, s, _ in wild[ev['map']][ev['table']]}
    missing = sorted(s for s in species_used | {s for _, s, _ in PARTY_PLAN} if s not in y5 or s not in y3)
    assert not missing, missing

    params, sa, sb, s0, iters, rms = solve(data, events)
    f = apply_curve(params)
    a, L0, p = params

    # ---------------- report ----------------
    P = print
    P('# Level scaling for the Gen 6 Exp. Share (computed by converter/level_scaling.py)\n')
    P(f'f(L) = L + {a:.4f} * max(0, L - {L0:.1f})^{p:.2f}   rounded, capped at 100; applied to everything met after '
      f'the Exp. Share (segment "{EXP_SHARE_AFTER}" and earlier stay as in Sapphire)  [computed, {iters} fixed-point iterations]\n')
    P('Sapphire level -> new level:')
    row = [f'{L}->{f(L)}' for L in range(10, 71, 2)]
    for i in range(0, len(row), 10):
        P('  ' + '  '.join(row[i:i + 10]))
    P(f'\nAssumptions: starter {STARTER}, party {[(s, l, seg) for seg, s, l in PARTY_PLAN]}, {MAIN_BATTLERS} main battlers '
      f'(lower-levelled one takes each KO), {N_WILD} wild battles per full area, Exp. Share after "{EXP_SHARE_AFTER}", '
      f'key-battle weight {KEY_WEIGHT}.')
    P(f'Growth tables pokeruby == Black 2 (Lv2-100): {tables_equal};  fit rms {rms:.2f} levels\n')

    P('## Key battles: player main-battler level (a) Sapphire, (b0) Black 2 + Exp. Share with Sapphire levels, (b) with f')
    P(f"{'battle':34s} {'Sapphire lv':>16s} {'new lv':>16s} {'(a) main':>8s} {'(b0) main':>9s} {'(b) main':>8s} "
      f"{'(b) avg':>7s} {'gap a':>6s} {'gap b':>6s}")
    keyrows = []
    for (ev, st_a, opp_a), (_, st_b, opp_b), (_, st_0, _) in zip(sa.log, sb.log, s0.log):
        if not ev.get('key') and ev['kind'] != 'static':
            continue
        if ev['kind'] == 'static':
            Ls, news = [ev['level']], opp_b
            label = ev['label']
        else:
            Ls, news = [L for L, _ in ev['party']], opp_b
            label = ev['key']
        ace, ace2 = max(Ls), max(news)
        gap_a, gap_b = ace - st_a['main'], ace2 - st_b['main']
        keyrows.append({'battle': label, 'trainer': ev.get('id'), 'segment': ev['seg'], 'sapphire_levels': Ls,
                        'new_levels': news, 'player_a_main': round(st_a['main'], 2), 'player_a_top': round(st_a['top'], 2),
                        'player_a_avg': round(st_a['avg'], 2), 'player_b0_main': round(st_0['main'], 2),
                        'player_b0_avg': round(st_0['avg'], 2), 'player_b_main': round(st_b['main'], 2),
                        'player_b_top': round(st_b['top'], 2), 'player_b_avg': round(st_b['avg'], 2),
                        'party_a': st_a['levels'], 'party_b': st_b['levels'],
                        'ace_gap_a': round(gap_a, 2), 'ace_gap_b': round(gap_b, 2)})
        P(f"{label[:34]:34s} {','.join(map(str, Ls))[:16]:>16s} {','.join(map(str, news))[:16]:>16s} "
          f"{st_a['main']:8.1f} {st_0['main']:9.1f} {st_b['main']:8.1f} {st_b['avg']:7.1f} {gap_a:+6.1f} {gap_b:+6.1f}")

    P('\n## Party levels at each gym leader (integer levels, party order as caught)')
    for r in keyrows:
        if r['battle'].startswith('Gym') or r['battle'].startswith('Champion'):
            P(f"  {r['battle']:22s} (a) {r['party_a']}   (b) {r['party_b']}")

    P('\n## Story segments: trainers / wild battles simulated, main-battler level at the end ((a), (b0), (b)) and (b) party avg')
    segrows = []
    for seg, label, _ in SEGMENTS:
        evs = [e for e in events if e['seg'] == seg]
        nt = sum(1 for e in evs if e['kind'] == 'trainer')
        nw = sum(e['count'] for e in evs if e['kind'] == 'wild')
        ra, r0, rb = sa.snap[seg], s0.snap[seg], sb.snap[seg]
        segrows.append({'segment': seg, 'label': label, 'trainers': [e['id'] for e in evs if e['kind'] == 'trainer'],
                        'wild_battles': nw, 'pre_exp_share': evs[0]['pre_share'],
                        'a_main': round(ra['main'], 2), 'b0_main': round(r0['main'], 2), 'b_main': round(rb['main'], 2),
                        'b_avg': round(rb['avg'], 2), 'party_a': ra['levels'], 'party_b': rb['levels']})
        P(f"  {label[:44]:44s} {nt:3d} tr {nw:5.1f} wild   {ra['main']:5.1f} {r0['main']:5.1f} {rb['main']:5.1f}  avg {rb['avg']:5.1f}")

    # sensitivity
    P('\n## Sensitivity (same method, one assumption changed)')
    sens = []
    base_wild, base_share, base_mains = N_WILD, EXP_SHARE_AFTER, MAIN_BATTLERS
    # (name, overrides, style a, style b, metric b)
    variants = [('baseline', {}, 'mains', 'mains', 'main'),
                ('N_WILD=5', {'N_WILD': 5}, 'mains', 'mains', 'main'),
                ('N_WILD=20', {'N_WILD': 20}, 'mains', 'mains', 'main'),
                ('Exp. Share after Wattson', {'EXP_SHARE_AFTER': 'gym3'}, 'mains', 'mains', 'main'),
                ('Exp. Share after Norman', {'EXP_SHARE_AFTER': 'gym5'}, 'mains', 'mains', 'main'),
                ('3 main battlers', {'MAIN_BATTLERS': 3}, 'mains', 'mains', 'main'),
                ('starter solo in (a) and (b)', {}, 'solo', 'solo', 'main'),
                ('(b) whole party battles, avg', {}, 'mains', 'rotate', 'main'),
                ('(b) matched on party average', {}, 'mains', 'mains', 'avg')]
    anchors = [('Wattson ace', 23), ('Norman ace', 31), ('Winona ace', 33), ('Tate&Liza', 42), ('Wallace ace', 43),
               ('Drake ace', 55), ('Steven ace', 58)]
    for name, over, st_a, st_b, met in variants:
        N_WILD = over.get('N_WILD', base_wild); EXP_SHARE_AFTER = over.get('EXP_SHARE_AFTER', base_share)
        MAIN_BATTLERS = over.get('MAIN_BATTLERS', base_mains)
        ev2 = build_story(trainers, map_trainers, wild)
        prm, a2, b2 = (params, sa, sb) if name == 'baseline' else solve(data, ev2, st_a, st_b, met)[:3]
        f2 = apply_curve(prm)
        champ = [(x, y) for x, y in zip(a2.log, b2.log) if x[0].get('key') == 'Champion Steven'][0]
        sens.append({'variant': name, 'style_a': st_a, 'style_b': st_b, 'metric_b': met,
                     'params': {'a': prm[0], 'L0': prm[1], 'p': prm[2]},
                     'anchors': {n: f2(L) for n, L in anchors},
                     'champion_main_a': round(champ[0][1]['main'], 1), 'champion_main_b': round(champ[1][1]['main'], 1),
                     'champion_avg_b': round(champ[1][1]['avg'], 1)})
        P(f"  {name:30s} a={prm[0]:.4f} L0={prm[1]:4.1f} p={prm[2]:.2f}  " +
          ' '.join(f'{n.split()[0]} {L}->{f2(L)}' for n, L in anchors) +
          f"   at Steven: (a) main {champ[0][1]['main']:.1f}, (b) main {champ[1][1]['main']:.1f} avg {champ[1][1]['avg']:.1f}")
    N_WILD, EXP_SHARE_AFTER, MAIN_BATTLERS = base_wild, base_share, base_mains

    # ---------------- per-trainer and per-route results ----------------
    story_ids = {ev['id']: ev for ev in events if ev['kind'] == 'trainer'}
    in_sapphire = {t for lst in map_trainers.values() for t, _, _ in lst}
    for inc in ('magma_chimney.inc', 'magma_summit.inc', 'gabby_and_ty.inc'):
        for line in sapphire_lines(f'{RUBY}/data/scripts/{inc}'):
            for tok in re.findall(r'TRAINER_\w+', line):
                in_sapphire.add(alias.get(tok, tok))
    pre_share_trainers = {ev['id'] for ev in events if ev['kind'] == 'trainer' and ev['pre_share']}
    all_trainers = []
    for t, tr in trainers.items():
        if not tr.get('party'):
            continue
        exempt = t in pre_share_trainers
        all_trainers.append({'id': t, 'name': tr.get('name'), 'class': tr.get('class'),
                             'story_segment': story_ids[t]['seg'] if t in story_ids else None,
                             'key': story_ids[t]['key'] if t in story_ids else None,
                             'in_sapphire_scripts': t in in_sapphire,
                             'unchanged_pre_exp_share': exempt,
                             'sapphire_levels': [L for L, _ in tr['party']],
                             'new_levels': [L if exempt else f(L) for L, _ in tr['party']],
                             'species': [sp for _, sp in tr['party']]})
    pre_share_maps = {ev['map'] for ev in events if ev['kind'] == 'wild' and ev['pre_share']} | {'MAP_ROUTE103'}
    story_maps = OrderedDict()
    for ev in events:
        if ev['kind'] == 'wild':
            story_maps.setdefault(ev['map'], ev['seg'])
    routes = []
    for mp, tabs in wild.items():
        entry = {'map': mp, 'story_segment': story_maps.get(mp), 'tables': {}}
        for kind, slots in tabs.items():
            exempt = kind == 'land' and mp in pre_share_maps
            lo, hi = min(s[0] for s in slots), max(s[1] for s in slots)
            entry['tables'][kind] = {'unchanged_pre_exp_share': exempt, 'sapphire': [lo, hi],
                                     'new': [lo, hi] if exempt else [f(lo), f(hi)],
                                     'slots': [{'species': sp, 'sapphire': [a_, b_], 'new': [a_, b_] if exempt else [f(a_), f(b_)]}
                                               for a_, b_, sp, r in slots]}
        routes.append(entry)
    order = {m: i for i, m in enumerate(story_maps)}
    routes.sort(key=lambda e: (order.get(e['map'], 999), e['map']))

    P('\n## Wild level ranges on the story path (land/cave unless noted), Sapphire -> new')
    for e in routes:
        if e['story_segment'] is None:
            continue
        parts = []
        for kind, t in e['tables'].items():
            if kind in ('land', 'water') and (kind == 'land' or 'land' not in e['tables']):
                parts.append(f"{kind} {t['sapphire'][0]}-{t['sapphire'][1]} -> {t['new'][0]}-{t['new'][1]}" +
                             (' (unchanged, before Exp. Share)' if t['unchanged_pre_exp_share'] else ''))
        P(f"  {e['map'][4:]:28s} " + '; '.join(parts))

    out = OrderedDict()
    out['curve'] = {'formula': 'new = min(100, floor(L + a * max(0, L - L0) ** p + 0.5)), for content met after the Exp. Share',
                    'a': a, 'L0': L0, 'p': p,
                    'table': {L: f(L) for L in range(1, 101)}}
    out['assumptions'] = {'starter': STARTER, 'party_plan': PARTY_PLAN, 'main_battlers': MAIN_BATTLERS,
                          'wild_battles_per_full_area': N_WILD, 'exp_share_after_segment': EXP_SHARE_AFTER,
                          'key_weight': KEY_WEIGHT,
                          'exp_share_rule': 'participant: full Black 2 exp; every other party member: (base >> 1) '
                                            'then Black 2 level scaling with its own level',
                          'doubles': 'treated as singles (one participant per opponent Pokemon)',
                          'wild': 'expected exp over the slot rates, level uniform in [min, max]'}
    out['story'] = segrows
    out['key_battles'] = keyrows
    out['sensitivity'] = sens
    out['trainers'] = all_trainers
    out['wild'] = routes
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w') as fh:  # one list entry per line: diffable without being huge
        parts = []
        for k, v in out.items():
            if isinstance(v, list):
                body = '[\n  ' + ',\n  '.join(json.dumps(x) for x in v) + '\n ]'
            else:
                body = json.dumps(v)
            parts.append(f' {json.dumps(k)}: {body}')
        fh.write('{\n' + ',\n'.join(parts) + '\n}\n')
    P(f'\nwrote {os.path.relpath(OUT_JSON, ROOT)}')


if __name__ == '__main__':
    main()
