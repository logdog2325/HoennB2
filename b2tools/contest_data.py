"""Gen 3 Pokémon Contests: the data the decomp's C reads (notes/CONTESTS.md), one pack per version.

Everything comes from the decomps: Sapphire/Ruby from external/pokeruby, Emerald from external/pokeemerald (moves,
opponents, AI scripts), the art and the contest screen's lines from pokeemerald's graphics and strings for all three
(same pictures and wording as pokeruby's: contest_check.py compares them and lists what differs).

    members(version) -> the list of archive 271's members, in include/hoennb2/contest.h's order
    python3 b2tools/contest_data.py [sapphire|ruby|emerald]   prints the pack's sizes and the Black 2 move table

The moves after Gen 3's 354: NEW_MOVES below (closest existing move); categories of 355-467 from Pearl's own data
(PearlB2 external/pokeplatinum res/moves/*/data.json "contest"."type", read when present, else the table's clone).
"""
import json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

EXTERNAL = os.path.join(ROOT, 'external')
RUBY = os.path.join(EXTERNAL, 'pokeruby')
EMERALD = os.path.join(EXTERNAL, 'pokeemerald')
PLATINUM_MOVES = os.path.expanduser('~/Documents/GitHub/PearlB2/external/pokeplatinum/res/moves')

N_MOVES = 566          # Black 2's 559 + b2tools/patches/fairy.py's 560-565
OBJ_TILES_PER_ROW = 32

# include/hoennb2/contest.h ContestArcMember (contest_check.py compares)
MEMBERS = ['BG_CHARS', 'BG_PAL', 'MAP_INTERFACE', 'MAP_AUDIENCE', 'MAP_CURTAIN',
           'OBJ_CHARS', 'OBJ_PLTT', 'OBJ_CELLS', 'OBJ_ANIMS',
           'RES_CHARS', 'RES_PAL', 'RES_MAP_BG', 'RES_MAP_UI', 'RES_MAP_BANNER', 'RES_TITLES',
           'MOVES', 'EFFECTS', 'OPPONENTS', 'AI', 'TEXT',
           'BLEND_CHARS', 'BLEND_PAL', 'BLEND_MAP', 'BLEND_OBJ_CHARS', 'BLEND_OBJ_PLTT', 'BLEND_OBJ_CELLS',
           'BLEND_OBJ_ANIMS', 'BLOCK_CHARS', 'BLOCK_PAL', 'BLOCK_MAP', 'BLOCK_OBJ_CHARS', 'BLOCK_OBJ_PLTT',
           'BLOCK_OBJ_CELLS', 'BLOCK_OBJ_ANIMS', 'BERRY_TABLE']

# ---- the closest existing move for Black 2's later moves (the lead reads this table) ------------------------------
# id: Gen 3 move whose contest effect (and category, when Pearl's data has none) it takes
NEW_MOVES = {
    355: 'MOVE_RECOVER', 356: 'MOVE_RAIN_DANCE', 357: 'MOVE_FORESIGHT', 358: 'MOVE_SMELLING_SALT',
    359: 'MOVE_CRABHAMMER', 360: 'MOVE_RAPID_SPIN', 361: 'MOVE_MEMENTO', 362: 'MOVE_SURF', 363: 'MOVE_SECRET_POWER',
    364: 'MOVE_FAKE_OUT', 365: 'MOVE_THIEF', 366: 'MOVE_AGILITY', 367: 'MOVE_DEFENSE_CURL', 368: 'MOVE_METAL_CLAW',
    369: 'MOVE_BATON_PASS', 370: 'MOVE_CROSS_CHOP', 371: 'MOVE_REVENGE', 372: 'MOVE_PURSUIT', 373: 'MOVE_TORMENT',
    374: 'MOVE_THIEF', 375: 'MOVE_HEAL_BELL', 376: 'MOVE_SWIFT', 377: 'MOVE_IMPRISON', 378: 'MOVE_CRUSH_CLAW',
    379: 'MOVE_BULK_UP', 380: 'MOVE_ACID_ARMOR', 381: 'MOVE_SAFEGUARD', 382: 'MOVE_MIMIC', 383: 'MOVE_MIMIC',
    384: 'MOVE_SKILL_SWAP', 385: 'MOVE_SKILL_SWAP', 386: 'MOVE_REVERSAL', 387: 'MOVE_DOUBLE_EDGE', 388: 'MOVE_SPORE',
    389: 'MOVE_QUICK_ATTACK', 390: 'MOVE_SPIKES', 391: 'MOVE_SKILL_SWAP', 392: 'MOVE_INGRAIN', 393: 'MOVE_BOUNCE',
    394: 'MOVE_BLAST_BURN', 395: 'MOVE_ARM_THRUST', 396: 'MOVE_AEROBLAST', 397: 'MOVE_AGILITY', 398: 'MOVE_POISON_TAIL',
    399: 'MOVE_CRUNCH', 400: 'MOVE_SLASH', 401: 'MOVE_IRON_TAIL', 402: 'MOVE_SLUDGE_BOMB', 403: 'MOVE_AIR_CUTTER',
    404: 'MOVE_SLASH', 405: 'MOVE_SIGNAL_BEAM', 406: 'MOVE_DRAGON_BREATH', 407: 'MOVE_DRAGON_CLAW', 408: 'MOVE_ANCIENT_POWER',
    409: 'MOVE_GIGA_DRAIN', 410: 'MOVE_MACH_PUNCH', 411: 'MOVE_FOCUS_PUNCH', 412: 'MOVE_SOLAR_BEAM', 413: 'MOVE_SKY_ATTACK',
    414: 'MOVE_EARTHQUAKE', 415: 'MOVE_TRICK', 416: 'MOVE_HYPER_BEAM', 417: 'MOVE_AMNESIA', 418: 'MOVE_MACH_PUNCH',
    419: 'MOVE_REVENGE', 420: 'MOVE_QUICK_ATTACK', 421: 'MOVE_SLASH', 422: 'MOVE_THUNDER_PUNCH', 423: 'MOVE_ICE_PUNCH',
    424: 'MOVE_FIRE_PUNCH', 425: 'MOVE_QUICK_ATTACK', 426: 'MOVE_MUD_SHOT', 427: 'MOVE_SLASH', 428: 'MOVE_HEADBUTT',
    429: 'MOVE_MIST_BALL', 430: 'MOVE_STEEL_WING', 431: 'MOVE_ROCK_SLIDE', 432: 'MOVE_HAZE', 433: 'MOVE_SKILL_SWAP',
    434: 'MOVE_OVERHEAT', 435: 'MOVE_THUNDERBOLT', 436: 'MOVE_ERUPTION', 437: 'MOVE_OVERHEAT', 438: 'MOVE_VINE_WHIP',
    439: 'MOVE_ROCK_THROW', 440: 'MOVE_SLASH', 441: 'MOVE_SLUDGE_BOMB', 442: 'MOVE_HEADBUTT', 443: 'MOVE_SWIFT',
    444: 'MOVE_ROCK_SLIDE', 445: 'MOVE_ATTRACT', 446: 'MOVE_SPIKES', 447: 'MOVE_LOW_KICK', 448: 'MOVE_SING',
    449: 'MOVE_EXTREME_SPEED', 450: 'MOVE_THIEF', 451: 'MOVE_CHARGE', 452: 'MOVE_DOUBLE_EDGE', 453: 'MOVE_QUICK_ATTACK',
    454: 'MOVE_FURY_CUTTER', 455: 'MOVE_IRON_DEFENSE', 456: 'MOVE_RECOVER', 457: 'MOVE_DOUBLE_EDGE', 458: 'MOVE_DOUBLE_KICK',
    459: 'MOVE_HYPER_BEAM', 460: 'MOVE_AEROBLAST', 461: 'MOVE_MEMENTO', 462: 'MOVE_CRUSH_CLAW', 463: 'MOVE_FIRE_SPIN',
    464: 'MOVE_GRASS_WHISTLE', 465: 'MOVE_SOLAR_BEAM', 466: 'MOVE_ANCIENT_POWER', 467: 'MOVE_DIG',
    468: 'MOVE_SHARPEN', 469: 'MOVE_PROTECT', 470: 'MOVE_PAIN_SPLIT', 471: 'MOVE_PAIN_SPLIT', 472: 'MOVE_IMPRISON',
    473: 'MOVE_PSYCHIC', 474: 'MOVE_SLUDGE_BOMB', 475: 'MOVE_AGILITY', 476: 'MOVE_FOLLOW_ME', 477: 'MOVE_CONFUSION',
    478: 'MOVE_IMPRISON', 479: 'MOVE_ROCK_THROW', 480: 'MOVE_SEISMIC_TOSS', 481: 'MOVE_EMBER', 482: 'MOVE_SLUDGE',
    483: 'MOVE_DRAGON_DANCE', 484: 'MOVE_BODY_SLAM', 485: 'MOVE_PSYWAVE', 486: 'MOVE_SHOCK_WAVE', 487: 'MOVE_WATER_SPORT',
    488: 'MOVE_FLAME_WHEEL', 489: 'MOVE_BULK_UP', 490: 'MOVE_ROCK_SMASH', 491: 'MOVE_ACID', 492: 'MOVE_FAINT_ATTACK',
    493: 'MOVE_CONVERSION', 494: 'MOVE_ROLE_PLAY', 495: 'MOVE_FOLLOW_ME', 496: 'MOVE_SING', 497: 'MOVE_UPROAR',
    498: 'MOVE_FALSE_SWIPE', 499: 'MOVE_HAZE', 500: 'MOVE_PSYCH_UP', 501: 'MOVE_DETECT', 502: 'MOVE_BATON_PASS',
    503: 'MOVE_SURF', 504: 'MOVE_BELLY_DRUM', 505: 'MOVE_HEAL_BELL', 506: 'MOVE_SHADOW_PUNCH', 507: 'MOVE_FLY',
    508: 'MOVE_DRAGON_DANCE', 509: 'MOVE_SEISMIC_TOSS', 510: 'MOVE_FLAMETHROWER', 511: 'MOVE_TAUNT', 512: 'MOVE_AERIAL_ACE',
    513: 'MOVE_CONVERSION_2', 514: 'MOVE_REVENGE', 515: 'MOVE_MEMENTO', 516: 'MOVE_TRICK', 517: 'MOVE_FLAMETHROWER',
    518: 'MOVE_WATER_PULSE', 519: 'MOVE_FLAMETHROWER', 520: 'MOVE_PETAL_DANCE', 521: 'MOVE_THUNDERBOLT', 522: 'MOVE_SIGNAL_BEAM',
    523: 'MOVE_MAGNITUDE', 524: 'MOVE_ICY_WIND', 525: 'MOVE_ROAR', 526: 'MOVE_GROWTH', 527: 'MOVE_THUNDER_WAVE',
    528: 'MOVE_VOLT_TACKLE', 529: 'MOVE_HORN_DRILL', 530: 'MOVE_DOUBLE_KICK', 531: 'MOVE_STOMP', 532: 'MOVE_MEGA_DRAIN',
    533: 'MOVE_SLASH', 534: 'MOVE_CRABHAMMER', 535: 'MOVE_BODY_SLAM', 536: 'MOVE_RAZOR_LEAF', 537: 'MOVE_STOMP',
    538: 'MOVE_COTTON_SPORE', 539: 'MOVE_CRUNCH', 540: 'MOVE_PSYCHIC', 541: 'MOVE_TAIL_WHIP', 542: 'MOVE_THUNDER',
    543: 'MOVE_TAKE_DOWN', 544: 'MOVE_DOUBLE_KICK', 545: 'MOVE_FLAMETHROWER', 546: 'MOVE_TRI_ATTACK', 547: 'MOVE_PERISH_SONG',
    548: 'MOVE_SLASH', 549: 'MOVE_ICY_WIND', 550: 'MOVE_THUNDER', 551: 'MOVE_SACRED_FIRE', 552: 'MOVE_TEETER_DANCE',
    553: 'MOVE_THUNDERBOLT', 554: 'MOVE_ICE_BEAM', 555: 'MOVE_SCREECH', 556: 'MOVE_ICICLE_SPEAR', 557: 'MOVE_OVERHEAT',
    558: 'MOVE_FLAMETHROWER', 559: 'MOVE_THUNDERBOLT',
    # Fairy (b2tools/patches/fairy.py)
    560: 'MOVE_GUST', 561: 'MOVE_SWIFT', 562: 'MOVE_SWEET_KISS', 563: 'MOVE_FLASH', 564: 'MOVE_FLAIL', 565: 'MOVE_MOONLIGHT',
}
# pokeruby/pokeemerald spell some moves differently from each other (checked when the table is read)
ALIASES = {'MOVE_FAINT_ATTACK': ('MOVE_FEINT_ATTACK',), 'MOVE_DRAGON_BREATH': ('MOVE_DRAGONBREATH',),
           'MOVE_SMELLING_SALT': ('MOVE_SMELLING_SALTS', 'MOVE_SMELLINGSALT'), 'MOVE_THUNDER_PUNCH': ('MOVE_THUNDERPUNCH',),
           'MOVE_SELF_DESTRUCT': ('MOVE_SELFDESTRUCT',), 'MOVE_VICE_GRIP': ('MOVE_VICEGRIP',),
           'MOVE_POISON_POWDER': ('MOVE_POISONPOWDER',), 'MOVE_ANCIENT_POWER': ('MOVE_ANCIENTPOWER',),
           'MOVE_SOLAR_BEAM': ('MOVE_SOLARBEAM',), 'MOVE_DYNAMIC_PUNCH': ('MOVE_DYNAMICPUNCH',),
           'MOVE_DOUBLE_SLAP': ('MOVE_DOUBLESLAP',), 'MOVE_FEATHER_DANCE': ('MOVE_FEATHERDANCE',),
           'MOVE_GRASS_WHISTLE': ('MOVE_GRASSWHISTLE',), 'MOVE_SMOKESCREEN': ('MOVE_SMOKE_SCREEN',)}


# ---- reading C constants ------------------------------------------------------------------------------------------
def _defines(path, out=None):
    out = {} if out is None else out
    src = re.sub(r'/\*.*?\*/', '', open(path, errors='replace').read(), flags=re.S)
    src = re.sub(r'//.*', '', src).replace('\\\n', ' ')
    for m in re.finditer(r'^[ \t]*#define[ \t]+(\w+)[ \t]+([^\n]+?)[ \t]*$', src, re.M):
        out.setdefault(m.group(1), m.group(2))
    for m in re.finditer(r'enum\s*\w*\s*\{(.*?)\}', src, re.S):
        v = 0
        for item in m.group(1).split(','):
            item = item.strip()
            if not item:
                continue
            name, _, val = item.partition('=')
            name = name.strip()
            if val.strip():
                try:
                    v = int(val.strip(), 0)
                except ValueError:
                    continue
            out.setdefault(name, str(v))
            v += 1
    return out


def _eval(expr, syms):
    expr = expr.strip()
    def sub(m):
        w = m.group(0)
        if w in syms:
            return f'({_eval(str(syms[w]), syms)})'
        raise KeyError(w)
    py = re.sub(r'\b[A-Za-z_]\w*\b', sub, expr)
    return int(eval(py, {'__builtins__': {}}))     # (our own decomps' constants)


def constants(decomp):
    syms = {}
    inc = os.path.join(decomp, 'include')
    syms.update(TRUE='1', FALSE='0')
    for f in ('constants/contest.h', 'contest.h', 'contest_effect.h', 'constants/moves.h', 'constants/species.h',
              'constants/pokemon.h', 'constants/global.h'):
        p = os.path.join(inc, f)
        if os.path.exists(p):
            _defines(p, syms)
    for f in ('constants/contest_constants.inc', 'constants/contest_move_effects.inc', 'constants/species_constants.inc',
              'constants/move_constants.inc'):
        p = os.path.join(decomp, f)
        if os.path.exists(p):
            for m in re.finditer(r'\.set\s+(\w+),\s*([^\s@]+)', open(p).read()):
                syms.setdefault(m.group(1), m.group(2))
    return syms


def _b2_constants():
    import b2decomp
    syms = {}
    g = os.path.join(b2decomp.SRC, 'build', 'include', 'generated', 'constants')
    for f in ('species.h', 'moves.h'):
        _defines(os.path.join(g, f), syms)
    return syms


def _strip_c(src):
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
    return re.sub(r'//[^\n]*', '', src)


# ---- moves ---------------------------------------------------------------------------------------------------------
def gen3_moves(decomp):
    """[(effect, category, comboStarterId, [4 combo moves])] of ids 0-354, by its own constants."""
    syms = constants(decomp)
    src = _strip_c(open(os.path.join(decomp, 'src/data/contest_moves.h')).read())
    moves = [None] * 355
    if '.effect' in src.split('gContestEffects')[0]:
        for m in re.finditer(r'\[(MOVE_\w+)\]\s*=\s*\{', src):
            j, depth = m.end(), 1
            while depth:
                depth += {'{': 1, '}': -1}.get(src[j], 0)
                j += 1
            body = src[m.end():j - 1]
            if '.effect' not in body:
                continue
            i = _eval(m.group(1), syms)
            eff = re.search(r'\.effect\s*=\s*(\w+)', body).group(1)
            cat = re.search(r'\.contestCategory\s*=\s*(\w+)', body).group(1)
            st = re.search(r'\.comboStarterId\s*=\s*(\w+)', body).group(1)
            combo = re.search(r'\{(.*?)\}', body).group(1)    # (`.comboMoves = {...}`, or `{0, X}` after comboStarterId)
            cm = [_eval(c, syms) for c in combo.split(',') if c.strip()]
            moves[i] = (_eval(eff, syms), _eval(cat, syms), _eval(st, syms), (cm + [0, 0, 0, 0])[:4])
        moves[0] = (0, 0, 0, [0, 0, 0, 0])
    else:
        table = src.split('gContestMoves[]')[1].split('};')[0]
        rows = re.findall(r'\{\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*\{([^}]*)\}\s*\}', table)
        assert len(rows) == 355, f'{decomp}: {len(rows)} contest moves'
        for i, (eff, cat, st, combo) in enumerate(rows):
            cm = [_eval(c, syms) for c in combo.split(',') if c.strip()]
            moves[i] = (_eval(eff, syms), _eval(cat, syms), _eval(st, syms), (cm + [0, 0, 0, 0])[:4])
    assert all(moves), f'{decomp}: move {moves.index(None)} missing'
    return moves


def effects(decomp):
    syms = constants(decomp)
    src = _strip_c(open(os.path.join(decomp, 'src/data/contest_moves.h')).read())
    table = src.split('gContestEffects[]')[1].split('};')[0]
    out = {}
    named = list(re.finditer(r'\[(CONTEST_EFFECT_\w+)\]\s*=\s*\{\s*\.effectType\s*=\s*(\w+)\s*,\s*\.appeal\s*=\s*(\w+)\s*,'
                             r'\s*\.jam\s*=\s*(\w+)', table))
    for m in named:
        out[_eval(m.group(1), syms)] = tuple(_eval(x, syms) for x in m.groups()[1:])
    if not out:
        for i, m in enumerate(re.finditer(r'\{\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\}', table)):
            out[i] = tuple(_eval(x, syms) for x in m.groups())
    assert sorted(out) == list(range(len(out))), f'{decomp}: effects {sorted(out)}'
    return [out[i] for i in range(len(out))]


def combo_lookup(decomp):
    src = _strip_c(open(os.path.join(decomp, 'src/data/contest_moves.h')).read())
    t = src.split('gComboStarterLookupTable[]')[1].split('};')[0].split('{', 1)[1]
    return [1 if w.strip() == 'TRUE' else 0 for w in t.split(',') if w.strip()]


def platinum_type(move_name):
    """Pearl's category of a Black 2 move constant (Platinum's data: Pearl's own has the same values), None if absent."""
    p = os.path.join(PLATINUM_MOVES, move_name[5:].lower(), 'data.json')
    if not os.path.exists(p):
        return None
    t = (json.load(open(p)).get('contest') or {}).get('type')
    return {'CONTEST_TYPE_COOL': 0, 'CONTEST_TYPE_BEAUTY': 1, 'CONTEST_TYPE_CUTE': 2, 'CONTEST_TYPE_SMART': 3,
            'CONTEST_TYPE_TOUGH': 4}.get(t)


def _gen3_id(name, syms):
    for n in (name,) + ALIASES.get(name, ()):
        if n in syms:
            return _eval(n, syms)
    raise KeyError(f'{name}: no such move in the decomp')


def move_table(decomp):
    """[(effect, category, starter, combos, clone name or None, category source)], ids 0..N_MOVES-1."""
    gen3 = gen3_moves(decomp)
    syms = constants(decomp)
    b2 = _b2_constants()
    by_id = {}
    for k, v in b2.items():
        if k.startswith('MOVE_') and re.fullmatch(r'\d+', v):
            by_id.setdefault(int(v), k)
    table = [(a, b, c, d, None, 'gen3') for a, b, c, d in gen3]
    for i in range(355, N_MOVES):
        clone = NEW_MOVES[i]
        e, cat, _, _ = gen3[_gen3_id(clone, syms)]
        name = by_id.get(i)
        src = 'clone'
        if name is not None:
            p = platinum_type(name)
            if p is not None:
                cat, src = p, 'pearl'
        table.append((e, cat, 0, [0, 0, 0, 0], clone, src))
    return table


def pack_moves(decomp):
    out = b''
    for e, c, s, combo, _, _ in move_table(decomp):
        out += bytes([e, c, s]) + bytes(combo) + b'\0'
    assert len(out) == N_MOVES * 8
    return out + bytes(combo_lookup(decomp)).ljust(64, b'\0')


def pack_effects(decomp):
    return b''.join(bytes([t, a, j, 0]) for t, a, j in effects(decomp))


# ---- opponents -------------------------------------------------------------------------------------------------------
GEN3_RENAMES = {'SPECIES_NIDORAN_F': 'SPECIES_NIDORAN_F', 'SPECIES_NIDORAN_M': 'SPECIES_NIDORAN_M'}


def opponents(decomp):
    """[dict] gContestOpponents in order, with names (mixed case as Sapphire's text) and the post-game filter."""
    syms = constants(decomp)
    src = _strip_c(open(os.path.join(decomp, 'src/data/contest_opponents.h')).read())
    names = {}
    for m in re.finditer(r'#define\s+(CONTEST_OPPONENT_(?:NICKNAME|OTNAME)_\w+)\s+"([^"]*)"', src):
        names.setdefault(m.group(1), m.group(2))      # pokeruby's first block is the English one
    head, table = src.split('gContestOpponents[]', 1)
    filt = {}
    if 'gPostgameContestOpponentFilter' in table:
        table, f = table.split('gPostgameContestOpponentFilter', 1)
        for m in re.finditer(r'\[(CONTEST_OPPONENT_\w+)\]\s*=\s*(CONTEST_FILTER_\w+)', f):
            filt[m.group(1)] = {'CONTEST_FILTER_NONE': 0, 'CONTEST_FILTER_NO_POSTGAME': 1, 'CONTEST_FILTER_ONLY_POSTGAME': 2}[m.group(2)]
    out = []
    for m in re.finditer(r'\[(CONTEST_OPPONENT_\w+)\]\s*=\s*\{', table):
        i, depth = m.end(), 1
        while depth:
            depth += {'{': 1, '}': -1}.get(table[i], 0)
            i += 1
        b = table[m.end():i - 1]
        def g(k):
            return re.search(r'\.' + k + r'\s*=\s*([^,\n]+)', b).group(1).strip()
        def name(k):
            v = g(k)
            q = re.match(r'_\(\s*"([^"]*)"\s*\)', v)
            if q:
                return q.group(1)
            q = re.match(r'_\(\s*(\w+)\s*\)', v)
            return names[q.group(1)]
        moves = re.search(r'\.moves\s*=\s*\{(.*?)\}', b, re.S).group(1)
        ai = g('aiFlags') if '.aiFlags' in b else g('flags')
        out.append(dict(id=m.group(1), species=g('species'), nick=name('nickname'), trainer=name('trainerName'),
                        rank=g('whichRank'), pools=[g('aiPool_' + c) == 'TRUE' for c in ('Cool', 'Beauty', 'Cute', 'Smart', 'Tough')],
                        moves=[w.strip() for w in moves.split(',') if w.strip()],
                        stats=[int(g(k), 0) for k in ('cool', 'beauty', 'cute', 'smart', 'tough', 'sheen')],
                        ai=ai, personality=int(g('personality'), 0), filter=filt.get(m.group(1), 0)))
    for o in out:
        o['rank'] = _eval(o['rank'], syms)
    return out


def _ai_flags(expr, syms):
    return _eval(expr, syms) & 0xffffffff


def mixed(name):
    """A Gen 3 all-caps name as Black 2's and HoennB2's text shows it."""
    return ' '.join(w[:1] + w[1:].lower() if w.isupper() or w.upper() == w else w for w in name.split(' '))


def pack_opponents(decomp):
    syms = constants(decomp)
    # (pokeruby's AI sets are defined in src/data/contest_opponents.h or contest.h)
    src = _strip_c(open(os.path.join(decomp, 'src/data/contest_opponents.h')).read())
    for m in re.finditer(r'^[ \t]*#define[ \t]+(CONTEST_AI\w*)[ \t]+(.+?)[ \t]*$', src, re.M):
        syms.setdefault(m.group(1), m.group(2))
    b2 = _b2_constants()
    out = b''
    for o in opponents(decomp):
        sp = int(b2[o['species']])
        pools = sum(1 << i for i, p in enumerate(o['pools']) if p)
        rec = struct.pack('<HBBB', sp, o['rank'], pools, o['filter']) + b'\0'
        rec += struct.pack('<4H', *[_gen3_id(m, syms) for m in o['moves']])
        rec += bytes(o['stats'])
        rec += struct.pack('<II', _ai_flags(o['ai'], syms), o['personality'])
        assert len(rec) == 28, len(rec)
        out += rec
    return out


# ---- the AI scripts: a small assembler for the two decomps' macros ---------------------------------------------------
def _ai_macros(path):
    macros = {}
    for m in re.finditer(r'\.macro[ \t]+(\w+)[ \t]*([^\n]*)\n(.*?)\.endm', open(path).read(), re.S):
        args = [a.split(':')[0].strip() for a in re.split(r'[, ]+', m.group(2).strip()) if a.strip()]
        body = []
        for line in m.group(3).split('\n'):
            line = line.split('@')[0].strip()
            q = re.match(r'\.(byte|2byte|4byte)\s+(.+)', line)
            if q:
                body.append((q.group(1), q.group(2).strip()))
            elif line:
                word, _, rest = line.partition(' ')
                body.append(('call', word, [a.strip() for a in rest.split(',')] if rest.strip() else []))
        macros[m.group(1)] = (args, body)
    return macros


def assemble_ai(decomp):
    """(table of 32 script offsets + bytes): pointers are offsets from the start of the member."""
    macro_path = os.path.join(decomp, 'include/macros/contest_ai_script.inc')
    if not os.path.exists(macro_path):
        macro_path = os.path.join(decomp, 'asm/macros/contest_ai_script.inc')
    macros = _ai_macros(macro_path)
    syms = constants(decomp)
    src = open(os.path.join(decomp, 'data/contest_ai_scripts.s')).read()
    table = []
    labels = {}
    code = bytearray()
    fixups = []
    enum = 0

    def emit(word, args):
        names, body = macros[word]
        assert len(args) == len(names), f'{word} {args}: {names}'
        local = sorted(zip(names, args), key=lambda kv: -len(kv[0]))
        def fill(expr):
            for n, v in local:
                expr = expr.replace('\\' + n, v)
            return expr
        for item in body:
            if item[0] == 'call':
                emit(item[1], [fill(a) for a in item[2]])
                continue
            kind, expr = item[0], fill(item[1])
            size = {'byte': 1, '2byte': 2, '4byte': 4}[kind]
            if kind == '4byte' and re.fullmatch(r'\w+', expr) and not re.fullmatch(r'\d+|0x[0-9a-fA-F]+', expr):
                fixups.append((len(code), expr))
                code.extend(bytes(4))
            else:
                v = _eval(expr, syms) & ((1 << (8 * size)) - 1)
                code.extend(v.to_bytes(size, 'little'))

    for raw in src.split('\n'):
        line = raw.split('@')[0].strip()
        if not line or line.startswith('.include') or line.startswith('.section') or line.startswith('#') or line.startswith('.align'):
            continue
        if line == 'enum_start':
            enum = 0
            continue
        m = re.match(r'enum\s+(\w+)', line)
        if m:
            syms[m.group(1)] = str(enum)
            enum += 1
            continue
        m = re.match(r'(\w+)::?$', line)
        if m:
            labels[m.group(1)] = len(code)
            continue
        m = re.match(r'\.4byte\s+(\w+)', line)
        if m:
            table.append(m.group(1))
            continue
        word, _, rest = line.partition(' ')
        if word not in macros:
            raise ValueError(f'{decomp}: AI line {line!r}')
        emit(word, [a.strip() for a in rest.split(',')] if rest.strip() else [])
    base = 4 * 32
    for off, name in fixups:
        struct.pack_into('<I', code, off, labels[name] + base)
    assert len(table) >= 32 - 1 or len(table) >= 7, len(table)
    head = b''.join(struct.pack('<I', labels[n] + base) for n in (table + [table[-1]] * 32)[:32])
    return head + bytes(code)


# ---- text ------------------------------------------------------------------------------------------------------------
_CAPS = [('POKéMON', 'Pokémon'), ('POKéBLOCK', 'Pokéblock'), ('JUDGE', 'Judge'), ('CONTEST', 'Contest'), ('COOL', 'Cool'),
         ('BEAUTY', 'Beauty'), ('CUTE', 'Cute'), ('SMART', 'Smart'), ('TOUGH', 'Tough'), ('RANK', 'Rank'),
         ('NORMAL', 'Normal'), ('SUPER', 'Super'), ('HYPER', 'Hyper'), ('MASTER', 'Master'), ('…', '...')]


def _clean(s):
    s = re.sub(r'\{PAUSE \d+\}|\{PAUSE_UNTIL_PRESS\}', '', s).replace('$', '')
    for a, b in _CAPS:
        s = s.replace(a, b)
    for n in (1, 2, 3):
        s = s.replace('{STR_VAR_%d}' % n, '{0100:%d}' % (n - 1))
    s = s.replace('The Judge \'s', 'The Judge’s').replace("'", '’')
    return s.strip()


def emerald_strings():
    src = open(os.path.join(EMERALD, 'data/text/contest_strings.inc')).read()
    out = {}
    for m in re.finditer(r'^(\w+)::\s*\n((?:\s*\.string "[^\n]*"\s*\n)+)', src, re.M):
        out[m.group(1)] = _clean(''.join(re.findall(r'\.string "(.*)"', m.group(2))))
    return out


def _table(name):
    src = _strip_c(open(os.path.join(EMERALD, 'src/data/contest_text_tables.h')).read())
    m = re.search(name + r'\[\]\s*=\s*\{(.*?)\};', src, re.S)
    return [re.sub(r'\[.*?\]\s*=\s*', '', w).strip() for w in m.group(1).split(',') if w.strip()]


# Lines of our own, in plain language matching the originals: the stage's introductions (Gen 3's Hall scene,
# pokeemerald contest_strings/contest_hall.inc), the results, YES/NO, the Blender and the Case.
OUR_LINES = [
    ('INTRO_HELLO', 'Hello! We’re just getting\nstarted with a {0100:1} Rank{be01}\nPokémon {0100:0} Contest!'),
    ('INTRO_ENTRY', 'Entry number {0100:0}!\n{0100:1} and {0100:2}!'),
    ('INTRO_ROUND1', 'Our judges looked over each\nPokémon’s condition!'),
    ('INTRO_GO', 'Now for the main event!\nLet’s see the appeal time!'),
    ('RES_PRELIM', 'Results of the condition check!'),
    ('RES_ROUND2', 'Results of the appeals!'),
    ('RES_ANNOUNCE', 'All the judging is done.\nThe results are in!'),
    ('RES_WINNER', 'The winner is {0100:1}\nand {0100:0}!'),
    ('NAME_SLASH', '/{0100:0}'),
    ('WORD', '{0100:0}'),
    ('YES', 'YES'),
    ('NO', 'NO'),
    ('CAT_COOL', 'Cool'), ('CAT_BEAUTY', 'Beauty'), ('CAT_CUTE', 'Cute'), ('CAT_SMART', 'Smart'), ('CAT_TOUGH', 'Tough'),
    ('RANK_NORMAL', 'Normal'), ('RANK_SUPER', 'Super'), ('RANK_HYPER', 'Hyper'), ('RANK_MASTER', 'Master'),
    # the Berry Blender (pokeemerald data/text/berry_blender.inc wording)
    ('BLEND_START', 'Start!'),
    ('BLEND_PRESS', 'Press A when the arrow reaches\nyour spot!'),
    ('BLEND_RESULTS', 'Results of the blending!'),
    ('BLEND_SPEED', 'Maximum speed: {0100:0}.{0100:1} RPM'),
    ('BLEND_GOT', 'You got a {0100:0}\nPokéblock!'),
    ('BLEND_FULL', 'The Pokéblock Case is full.\nThe new Pokéblock was left behind.'),
    ('BLEND_AGAIN', 'Blend another Berry?'),
    ('BLEND_NONE', 'You don’t have any Berries\nto put in the Blender.'),
    ('BLEND_PICK', 'Which Berry will you put in?'),
    ('BLEND_FAIL', 'The Berries turned into a\nBlack Pokéblock...'),
    ('BLEND_NAME_MISTER', 'Mister'), ('BLEND_NAME_LADDIE', 'Laddie'), ('BLEND_NAME_LASSIE', 'Lassie'),
    ('BLEND_NAME_DUDE', 'Dude'), ('BLEND_NAME_MISS', 'Miss'),
    # the Pokéblock Case (pokeemerald src/strings.c gText_*: pokeblock.c)
    ('CASE_EMPTY', 'The Case is empty.'),
    ('CASE_TITLE', 'Pokéblocks'),
    ('FLAVOR_SPICY', 'Spicy'), ('FLAVOR_DRY', 'Dry'), ('FLAVOR_SWEET', 'Sweet'), ('FLAVOR_BITTER', 'Bitter'), ('FLAVOR_SOUR', 'Sour'),
    ('CASE_ACTIONS_USE', 'USE'), ('CASE_ACTIONS_TOSS', 'TOSS'), ('CASE_ACTIONS_CANCEL', 'CANCEL'),
    ('CASE_LEVEL', 'Lv. {0100:0}'), ('CASE_FEEL', 'Feel {0100:0}'),
    ('CASE_TOSS', 'Throw away this Pokéblock?'),
    ('CASE_FED', '{0100:0} ate the\n{0100:1} Pokéblock!'),
    ('CASE_FULL_FEEL', '{0100:0} can’t eat any more...'),
    ('CASE_ROSE', '{0100:0}’s {0100:1} rose!'),
    ('CASE_ROSE_NONE', 'Nothing changed!'),
    ('CASE_EGG', 'An Egg can’t eat Pokéblocks.'),
    ('CASE_CHOOSE', 'Which Pokémon will eat it?'),
    ('COND_COOL', 'coolness'), ('COND_BEAUTY', 'beauty'), ('COND_CUTE', 'cuteness'), ('COND_SMART', 'smartness'), ('COND_TOUGH', 'toughness'),
    ('COLOR_0', 'Empty'), ('COLOR_1', 'Red'), ('COLOR_2', 'Blue'), ('COLOR_3', 'Pink'), ('COLOR_4', 'Green'),
    ('COLOR_5', 'Yellow'), ('COLOR_6', 'Purple'), ('COLOR_7', 'Indigo'), ('COLOR_8', 'Brown'), ('COLOR_9', 'LiteBlue'),
    ('COLOR_10', 'Olive'), ('COLOR_11', 'Gray'), ('COLOR_12', 'Black'), ('COLOR_13', 'White'), ('COLOR_14', 'Gold'),
    ('FLAVOR_0', 'Spicy'), ('FLAVOR_1', 'Dry'), ('FLAVOR_2', 'Sweet'), ('FLAVOR_3', 'Bitter'), ('FLAVOR_4', 'Sour'),
]
TEXT_WIDTH = 136        # the message window's 17 tiles
NAME_WIDTH = 46         # a ten-character name in font 2 (the screen's: narrow as Gen 3's)
MAX_LINES = 2


def _measure(font, line):
    return font.width(re.sub(r'\{0100:\d\}', '', line)) + NAME_WIDTH * len(re.findall(r'\{0100:\d\}', line))


def rewrap(s, font, width=TEXT_WIDTH):
    """Our font is wider than Gen 3's: the line break moves when a line doesn't fit the window (never more than two lines)."""
    lines = s.split('\\n')
    if all(_measure(font, l) <= width for l in lines):
        return s
    words = ' '.join(lines).split(' ')
    out = ['']
    for w in words:
        t = (out[-1] + ' ' + w).strip()
        if _measure(font, t) <= width or not out[-1]:
            out[-1] = t
        else:
            out.append(w)
    return '\\n'.join(out)


def header_text():
    """include/hoennb2/contest_text.h, written once into the decomp (contest_check.py compares it): the bank's order."""
    rows = ['// Generated by HoennB2 b2tools/contest_data.py: the lines of archive 271\'s text member. The opponents\' names are last.',
            '#ifndef POKEBW2_HOENNB2_CONTEST_TEXT_H', '#define POKEBW2_HOENNB2_CONTEST_TEXT_H', '']
    for i, (n, _) in enumerate(text_lines()):
        if n.startswith('OPP_') and not n.endswith('NICK_0'):
            break
        rows.append(f'#define CONTEST_TEXT_{n} {i}')
    return '\n'.join(rows + ['', '#endif', ''])


def text_lines(font=None):
    """[(name, line)] in the bank's order, the same as include/hoennb2/contest_text.h."""
    st = emerald_strings()
    rows = []
    desc = _table('gContestEffectDescriptionPointers')
    for i, n in enumerate(desc):
        rows.append((f'DESC_{i}', st[n]))
    for i, n in enumerate(_table('sAppealResultTexts')):
        rows.append((f'APPEAL_{i}', st[n]))
    for i, n in enumerate(_table('sRoundResultTexts')[:6]):
        rows.append((f'ROUND_{i}', st[n]))
    for i, n in enumerate(_table('sContestConditions')):
        rows.append((f'CONDITION_{i}', st[n]))
    for n, nm in (('gText_Contest_Shyness', 'NERVE_0'), ('gText_Contest_Anxiety', 'NERVE_1'), ('gText_Contest_Laziness', 'NERVE_2'),
                  ('gText_Contest_Hesitancy', 'NERVE_3'), ('gText_Contest_Fear', 'NERVE_4'),
                  ('gText_AppealNumWhichMoveWillBePlayed', 'APPEAL_NUM'), ('gText_AppealNumButItCantParticipate', 'APPEAL_NUM_CANT'),
                  ('gText_MonAppealedWithMove', 'APPEALED_WITH'), ('gText_MonWasWatchingOthers', 'WATCHING'),
                  ('gText_AllOutOfAppealTime', 'OUT_OF_TIME'), ('gText_MonCantAppealNextTurn', 'CANT_NEXT'),
                  ('gText_AppealComboWentOverWell', 'COMBO_WELL'), ('gText_JudgeLookedAtMonExpectantly', 'COMBO_START'),
                  ('gText_RepeatedAppeal', 'REPEATED'), ('gText_MonsXDidntGoOverWell', 'CROWD_BAD'), ('gText_MonsXWentOverGreat', 'CROWD_GOOD'),
                  ('gText_MonsXGotTheCrowdGoing', 'CROWD_MAX'), ('gText_CrowdContinuesToWatchMon', 'CROWD_WATCH'),
                  ('gText_MonsMoveIsIgnored', 'MOVE_IGNORED'), ('gText_MonWasTooNervousToMove', 'NERVOUS')):
        rows.append((nm, st[n]))
    rows += [(n, l.replace('\n', '\\n')) for n, l in OUR_LINES]
    for i, o in enumerate(version_opponents_for_text()):
        rows.append((f'OPP_NICK_{i}', mixed(o['nick'])))
        rows.append((f'OPP_NAME_{i}', mixed(o['trainer'])))
    if font is not None:
        # (the Blender's and the Case's windows are 28 tiles wide)
        rows = [(n, l if n.split('_')[0] in ('DESC', 'OPP') else rewrap(l, font, 220 if n.startswith(('BLEND_', 'CASE_')) else TEXT_WIDTH))
                for n, l in rows]
    return rows


_TEXT_DECOMP = EMERALD


def version_opponents_for_text():
    return opponents(_TEXT_DECOMP)


# ---- art --------------------------------------------------------------------------------------------------------------
def _png(path):
    from PIL import Image
    im = Image.open(path)
    assert im.mode == 'P', f'{path}: {im.mode}'
    return im


def _pal555(im, count=None):
    pal = im.getpalette() or []
    n = len(pal) // 3 if count is None else count
    out = []
    for i in range(n):
        r, g, b = pal[3 * i:3 * i + 3] if 3 * i + 3 <= len(pal) else (0, 0, 0)
        out.append((r >> 3) | (g >> 3) << 5 | (b >> 3) << 10)
    return out


def _jasc(path):
    rows = open(path).read().split('\n')
    n = int(rows[2])
    out = []
    for r in rows[3:3 + n]:
        a, b, c = (int(x) for x in r.split())
        out.append((a >> 3) | (b >> 3) << 5 | (c >> 3) << 10)
    return out


def _tiles4(im):
    w, h = im.size
    px = im.tobytes()
    out = bytearray()
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for y in range(8):
                row = px[(ty + y) * w + tx:(ty + y) * w + tx + 8]
                for x in range(0, 8, 2):
                    out.append((row[x] & 15) | (row[x + 1] & 15) << 4)
    return bytes(out)


def ncgr(raw, tiles_wide=OBJ_TILES_PER_ROW):
    """An uncompressed 4bpp NCGR (the character block + SOPC, as title_art.ncgr_build writes)."""
    n = len(raw) // 32
    while n % tiles_wide:
        raw += bytes(32)
        n += 1
    th = n // tiles_wide
    rahc = b'RAHC' + struct.pack('<IHHIIIII', 0x20 + len(raw), th, tiles_wide, 3, 0, 0, len(raw), 0x18) + raw
    sopc = b'SOPC' + struct.pack('<IIHH', 0x10, 0, tiles_wide, th)
    body = rahc + sopc
    return b'RGCN' + struct.pack('<HHIHH', 0xFEFF, 0x0101, 0x10 + len(body), 0x10, 2) + body


def nclr(colours):
    raw = struct.pack(f'<{len(colours)}H', *colours)
    ttlp = b'TTLP' + struct.pack('<IHHIII', 0x18 + len(raw), 3, 0, 0, len(raw), 0x10) + raw
    return b'RLCN' + struct.pack('<HHIHH', 0xFEFF, 0x0100, 0x10 + len(ttlp), 0x10, 1) + ttlp


_OBJ_SHAPE = {(8, 8): (0, 0), (16, 16): (0, 1), (32, 32): (0, 2), (64, 64): (0, 3), (16, 8): (1, 0), (32, 8): (1, 1),
              (32, 16): (1, 2), (64, 32): (1, 3), (8, 16): (2, 0), (8, 32): (2, 1), (16, 32): (2, 2), (32, 64): (2, 3)}


def ncer(cells):
    """cells: [[(x, y, w, h, tile, palette)]] centred on the actor's position; mapping 0 = 1D 32K, tile = 32-byte unit."""
    oams = bytearray()
    heads = b''
    for objs in cells:
        radius = 0
        for x, y, w, h, tile, pal in objs:
            shape, size = _OBJ_SHAPE[(w, h)]
            # (palette 0 in the cell: the actors say theirs, ClActor_SetPalette)
            oams += struct.pack('<HHH', (y & 0xff) | shape << 14, (x & 0x1ff) | size << 14, tile)
            radius = max(radius, max(abs(x), abs(x + w)), max(abs(y), abs(y + h)))
        heads += struct.pack('<HHI', len(objs), (radius + 3) // 4 & 0x3f, (len(oams) - 6 * len(objs)))
    kbec = struct.pack('<HHIIIII', len(cells), 0, 0x18, 0, 0, 0, 0) + heads + bytes(oams)
    while len(kbec) % 4:
        kbec += b'\0'
    # cellOffset 0x18 = from the block's data start (the header's 8 bytes after the signature and size)
    block = b'KBEC' + struct.pack('<I', 8 + len(kbec)) + kbec
    return b'RECN' + struct.pack('<HHIHH', 0xFEFF, 0x0100, 0x10 + len(block), 0x10, 1) + block


def nanr(count):
    """One sequence per cell: one frame, playing forward."""
    seq = b''.join(struct.pack('<HHIII', 1, 0, 0x00010000, 1, i * 8) for i in range(count))
    frames = b''.join(struct.pack('<IHH', i * 4, 4, 0xBEEF) for i in range(count))
    results = b''.join(struct.pack('<HH', i, 0xCCCC) for i in range(count))
    seq_off = 0x18
    frame_off = seq_off + len(seq)
    res_off = frame_off + len(frames)
    head = struct.pack('<HHIIIII', count, count, seq_off, frame_off, res_off, 0, 0)
    body = head + seq + frames + results
    block = b'KNBA' + struct.pack('<I', 8 + len(body)) + body
    return b'RNAN' + struct.pack('<HHIHH', 0xFEFF, 0x0100, 0x10 + len(block), 0x10, 1) + block


def contest_bg():
    """The stage: interface + audience characters, palette (Gen 3's LoadContestPalettes), three tilemaps."""
    g = os.path.join(EMERALD, 'graphics/contest')
    iface = _png(os.path.join(g, 'interface.png'))
    aud = _png(os.path.join(g, 'audience.png'))
    chars = _tiles4(iface) + _tiles4(aud)
    assert len(chars) == 0x4000, hex(len(chars))
    pal = (_pal555(iface) + [0] * 256)[:256]
    text = _jasc(os.path.join(g, 'text.pal'))
    pal[15 * 16:15 * 16 + 16] = (text + [0] * 16)[:16]
    pal[0] = 0                                               # SetBackdropFromColor(RGB_BLACK)
    for i in range(10, 14):
        pal[15 * 16 + i] = pal[15 * 16 + 1]
    pal[15 * 16 + 3] = 31 | 17 << 5 | 31 << 10
    return dict(BG_CHARS=chars, BG_PAL=struct.pack('<256H', *pal),
                MAP_INTERFACE=open(os.path.join(g, 'interface.bin'), 'rb').read(),
                MAP_AUDIENCE=open(os.path.join(g, 'audience.bin'), 'rb').read(),
                MAP_CURTAIN=open(os.path.join(g, 'curtain.bin'), 'rb').read())


# include/hoennb2/contest.h ContestSeq
def contest_obj():
    g = os.path.join(EMERALD, 'graphics/contest')
    judge = _png(os.path.join(g, 'judge.png'))
    sym = _png(os.path.join(g, 'judge_symbols.png'))
    heart = _png(os.path.join(g, 'slider_heart.png'))
    nt = _png(os.path.join(g, 'nextturn.png'))
    nums = _png(os.path.join(g, 'nextturn_numbers.png'))
    rnd = _png(os.path.join(g, 'nextturn_random.png'))
    app = _png(os.path.join(g, 'applause.png'))
    meter = _png(os.path.join(g, 'applause_meter.png'))
    raw = bytearray()
    cells = []
    def add(data):
        t = len(raw) // 32
        raw.extend(data)
        return t
    t = add(_tiles4(judge))                                  # SEQ_JUDGE
    cells.append([(-32, -32, 64, 64, t, 0)])
    symb = _tiles4(sym)                                      # SEQ_SYMBOL_0..6 (7 x 16x16: 4 tiles each)
    t = add(symb)
    for i in range(7):
        cells.append([(-8, -8, 16, 16, t + 4 * i, 1)])
    t = add(_tiles4(heart))                                  # SEQ_HEART
    cells.append([(-4, -4, 8, 8, t, 1)])
    nt_t = _tiles4(nt)
    numbers = _tiles4(nums)
    for i in range(5):                                       # SEQ_NEXT_0..4: "next turn" + 1-4 or ?
        b = bytearray(nt_t)
        b[6 * 32:7 * 32] = numbers[i * 32:(i + 1) * 32] if i < 4 else _tiles4(rnd)[:32]
        t = add(bytes(b))
        cells.append([(-28, -4, 32, 8, t, 2), (4, -4, 32, 8, t + 4, 2)])
    a = bytearray(_tiles4(app))
    m = _tiles4(meter)
    for level in range(6):                                   # SEQ_METER_0..5: the applause meter's lit columns
        b = bytearray(a)
        for i in range(5):
            src = m[64:128] if i < level else m[:64]
            b[(17 + i) * 32:(18 + i) * 32] = src[:32]
            b[(25 + i) * 32:(26 + i) * 32] = src[32:64]
        t = add(bytes(b))
        cells.append([(-32, -16, 64, 32, t, 2)])
    pal = (_pal555(judge, 16) + _pal555(sym, 16) + _pal555(nt, 16))
    return dict(OBJ_CHARS=ncgr(bytes(raw)), OBJ_PLTT=nclr(pal), OBJ_CELLS=ncer(cells), OBJ_ANIMS=nanr(len(cells)))


def results_art():
    g = os.path.join(EMERALD, 'graphics/contest/results_screen')
    im = _png(os.path.join(g, 'tiles.png'))
    titles = b''
    for n in ('title', 'title_cool', 'title_beauty', 'title_cute', 'title_smart', 'title_tough',
              'title_normal', 'title_super', 'title_hyper', 'title_master'):
        t = open(os.path.join(g, n + '.bin'), 'rb').read()
        titles += struct.pack('<H', len(t) // 2) + t + bytes(40 - len(t))        # 42 B each (contest_results.c BlitTitle)
    pal = (_pal555(im) + [0] * 256)[:256]
    pal[15 * 16:16 * 16] = (_jasc(os.path.join(g, 'text_window.pal')) + [0] * 16)[:16]
    return dict(RES_CHARS=_tiles4(im), RES_PAL=struct.pack('<256H', *pal),
                RES_MAP_BG=open(os.path.join(g, 'bg.bin'), 'rb').read(),
                RES_MAP_UI=open(os.path.join(g, 'interface.bin'), 'rb').read(),
                RES_MAP_BANNER=open(os.path.join(g, 'winner_banner.bin'), 'rb').read(),
                RES_TITLES=titles)


def pack_text(font=None):
    import b2decomp
    sys.path.insert(0, b2decomp.SRC)
    from tools.text import text_data
    # the stage's window takes Gen 3's colors for a message (letter 1, shadow 8, transparent background)
    def line(n, l):
        if n.startswith(('OPP_', 'CAT_', 'RANK_', 'CONDITION_', 'NERVE_', 'COLOR_', 'COND_', 'FLAVOR_', 'NAME_', 'WORD', 'DESC_',
                         'CASE_ACTIONS', 'CASE_LEVEL', 'CASE_FEEL', 'CASE_EMPTY', 'BLEND_SPEED')) or n in ('YES', 'NO'):
            return l
        return ('{bd00:1,2,0}' if n.startswith(('BLEND_', 'CASE_')) else '{bd00:1,8,0}') + l
    lines = ''.join(f'Contest_{n} = {line(n, l)}\n' for n, l in text_lines(font))
    return text_data.pack_file(lines)


def members(emerald=False):
    import contest_blend_data
    import b2font
    global _TEXT_DECOMP
    decomp = EMERALD if emerald else RUBY
    _TEXT_DECOMP = decomp
    data = {}
    data.update(contest_bg())
    data.update(contest_obj())
    data.update(results_art())
    data['MOVES'] = pack_moves(decomp)
    data['EFFECTS'] = pack_effects(decomp)
    data['OPPONENTS'] = pack_opponents(decomp)
    data['AI'] = assemble_ai(decomp)
    data['TEXT'] = pack_text(b2font.load(2))
    data.update(contest_blend_data.members())
    missing = [m for m in MEMBERS if m not in data]
    assert not missing, missing
    return [data[m] for m in MEMBERS]


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'sapphire'
    dec = EMERALD if which == 'emerald' else RUBY
    t = move_table(dec)
    for i in range(355, N_MOVES):
        e, c, _, _, clone, src = t[i]
        print(i, clone, 'cat', ['Cool', 'Beauty', 'Cute', 'Smart', 'Tough'][c], f'({src})')
    print('opponents', len(opponents(dec)), 'AI bytes', len(assemble_ai(dec)))
