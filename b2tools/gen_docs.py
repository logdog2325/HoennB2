"""Player documentation for the public download repo (notes/RESUME.md item 14, user 2026-10-17): Markdown pages made
from the project's own data, so a new release regenerates them instead of anyone editing them by hand.

    python3 b2tools/gen_docs.py [OUT_DIR]      (default ~/Documents/GitHub/pokemon-ruby-sapphire-nds/docs)

Pages (a page per version where the versions differ):
  wild-pokemon-<version>.md  every built map's wild tables as the game has them (src/encounters, the version's overlay;
                             levels already scaled), Gen 3 slot odds (converter/gen_encounters.py keeps them), the Old /
                             Good / Super Rod split (patches/rods.py) and the Rock Smash tables (patches/hm_free.py);
                             the post-game twins' tables "after the Champion" (data/hoenn_postgame_encounters.json);
                             the Safari Zone's rules (the gate's scripts, the decomp's include/hoennb2/safari.h and
                             resident/safari.c; left out, like dexnav.md, without our C)
  items-<version>.md         item balls, hidden items and the berry trees per area (data/hoenn_items.json ...)
  trainers-<version>.md      Gym Leaders, Elite Four, Champion, rivals, Wally and the team bosses (data/*/hoenn_trainer_data.json)
  tms-and-hms.md             Gen 3's TMs and HMs and the TM each one is here (converter/gen_items.py, patches/new_tms.py),
                             the HM-free field moves (patches/hm_free.py)
  fairy-type.md              the Fairy option's retyped species, moves and new moves (patches/fairy.py)
  evolutions.md              the trade evolutions made in-game (data/trade_evos.json)
  options.md                 Birch's start-of-game questions
  dexnav.md                  the DexNav (notes/DEXNAV.md): getting it, Route 101's tutorial, the screens, searching,
                             sneaking, search levels, bonuses, chains and shiny odds, read from its C in the decomp
                             (src/hoennb2/resident/dexnav.c, src/hoennb2/dexnav/dexnav_screen.c), its scripts and text
                             (b2tools/dexnav_art.py TEXT, patches/dexnav.py); dexnav_page stops when one no longer has
                             what the page states. Skipped (one line printed, no links to it) when the decomp tree has no
                             HoennB2 C (include/hoennb2.h): the public source snapshot with upstream pokebw2
  postgame-<version>.md      after the Hall of Fame and outside the story: the event tickets and islands, the roamers,
                             the gifts, the new places, the other legendaries, the battles (Battle Tower / PWT or the
                             Frontier, Wally, Emerald's rematches). Read from the scripts themselves (src/field_scripts,
                             the version's overlay: levels, step limits, prizes, conditions; postgame_page stops when a
                             script no longer has what the page states), patches/roamers.py, the encounter files (Altering
                             Cave, Mirage Island) and data/emerald/hoenn_rematch.json (notes/POSTGAME.md, EVENTS.md,
                             EMERALD_REMATCH.md, BATTLE_TOWER.md); completing the Pokédex (the post-game tables, Birch's
                             two starters, Sapphire / Ruby's other weather legend and fossil, the legendaries back after
                             a Hall of Fame: notes/POSTGAME.md "Post-game dex completion"; Huntail and Gorebyss from the
                             build base's personal data, the wild Pokémon holding a Deep Sea item in the 5% slot)
  battle-frontier.md         Emerald's Frontier rules (patches/frontier_core.py, notes/FRONTIER.md)
  levels.md                  the Exp. Share level curve (data/level_scaling.json, converter/level_scaling.py,
                             notes/LEVEL_SCALING.md): the rule, the table, what follows it (the one-off battles read from
                             each version's scripts against its decomp's setwildbattle levels), what doesn't (gifts,
                             trades), the Gym Leaders', Elite Four's and Champion's aces per version (levels_data, run per
                             version with --levels-data)
Each version's data is read in its own process (HOENN_VERSION is read once, by b2tools/version.py)."""
import collections, glob, json, os, re, struct, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import b2decomp  # noqa: E402  (the Black 2 decomp's source tree and build base: notes/POKEBW2_UPGRADE.md section 7)
B2 = b2decomp.SRC
sys.path.insert(0, os.path.join(HERE, 'patches'))
import version  # noqa: E402

VNAME = {'sapphire': 'Sapphire', 'ruby': 'Ruby', 'emerald': 'Emerald'}
GRASS = (20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1)
SURF = (60, 30, 5, 4, 1)
SUPER_ROD = (40, 40, 15, 4, 1)
OLD_ROD, GOOD_ROD = (70, 30), (60, 20, 20)
ROCK_SMASH = (60, 30, 5, 4, 1)
HEADER = ('<!-- Generated by b2tools/gen_docs.py from the game\'s data: edit the generator, not this page. -->\n\n')


# ---- names ------------------------------------------------------------------------------------------------------------
def _constants(header, prefix):
    return {k: int(v) for k, v in re.findall(rf'#define ({prefix}\w+)\s+(\d+)', open(os.path.join(B2, 'include', 'constants', header)).read())}

def _text(num):
    """A system text file's lines as this version's game has them: the decomp's (or our replacement src/text/system/
    NNNN_*.txt, version overlay) with the overrides*.json lines (patches/text.py's order)."""
    ours = [p for p in version.overlay(os.path.join(ROOT, 'src', 'text', 'system'), '*.txt') if os.path.basename(p)[:4] == f'{num:04d}']
    src = ours[0] if ours else glob.glob(os.path.join(B2, 'data', 'text', 'system', f'{num:04d}_*.txt'))[0]
    lines = open(src, encoding='utf-8').read().split('\n')
    over = [os.path.join(ROOT, 'src', 'text', 'overrides.json')] + sorted(glob.glob(os.path.join(ROOT, 'src', 'text', 'overrides_*.json')))
    if version.OVERLAY: over += sorted(glob.glob(os.path.join(ROOT, 'src', 'text', version.OVERLAY, 'overrides*.json')))
    key = 'system/' + os.path.basename(glob.glob(os.path.join(B2, 'data', 'text', 'system', f'{num:04d}_*.txt'))[0])
    for p in over:
        for i, s in json.load(open(p, encoding='utf-8')).get(key, {}).items():
            i = int(i)
            lines += [''] * (i + 1 - len(lines))
            lines[i] = s
    return [s.replace('\\n', ' ') for s in lines]

class Names:
    def __init__(self):
        import new_tms
        self.species_id = _constants('species.h', 'SPECIES_')
        self.items_id = _constants('items.h', 'ITEM_'); self.items_id.update(new_tms.item_constants())
        self.moves_id = _constants('moves.h', 'MOVE_')
        self.species_t, self.items_t, self.moves_t = _text(90), _text(64), _text(403)

    def species(self, c):
        i = self.species_id.get(c if c.startswith('SPECIES_') else 'SPECIES_' + c)
        return self.species_t[i] if i is not None and i < len(self.species_t) else _title(c, 'SPECIES_')

    def item(self, c):
        i = self.items_id.get(c)
        name = self.items_t[i] if i is not None and i < len(self.items_t) else _title(c, 'ITEM_')
        m = re.match(r'ITEM_(TM|HM)(\d+)$', c)
        if m and self.tm_moves.get(c): name = f'{m.group(1)}{int(m.group(2)):02d} {self.move(self.tm_moves[c])}'
        return name

    def move(self, c):
        i = self.moves_id.get(c)
        return self.moves_t[i] if i is not None and i < len(self.moves_t) else _title(c, 'MOVE_')

    @property
    def tm_moves(self):
        """ITEM_TMnn / ITEM_HMnn -> MOVE_X (Black 2's TM table + the new TMs)."""
        if not hasattr(self, '_tm'):
            import new_tms
            sys.path.insert(0, os.path.join(ROOT, 'converter'))
            import gen_items
            self._tm = {it: mv for mv, it in gen_items.tm_items().items()}
            self._tm.update({it: mv for mv, it in new_tms.move_to_item().items()})
        return self._tm

def _title(c, prefix):
    return ' '.join(w.capitalize() for w in c[len(prefix):].split('_')) if c.startswith(prefix) else c

def place(name):
    """A decomp map name for players: Route101 -> Route 101, GraniteCave_B2F -> Granite Cave B2F. Emerald: where Emerald
    gave a Sapphire map's name to one of its own maps (data/versions.json "name_clash": the Safari Zone's new areas), both
    take Emerald's own names (SafariZone_Northeast = Emerald's Safari Zone North, SafariZone_Northeast_Emerald = its
    Safari Zone Northeast)."""
    if version.is_emerald():
        clash = version.versions_json().get('maps', {}).get('emerald', {}).get('name_clash', [])
        if name.endswith('_Emerald') and name[:-len('_Emerald')] in clash: name = name[:-len('_Emerald')]
        elif name in clash: name = version.decomp_map(name) or name
    out = []
    for tok in name.split('_'):
        if re.fullmatch(r'B?\d+F|\d+R', tok): out.append(tok); continue
        tok = re.sub(r'(?<=[a-z])(?=[A-Z0-9])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', tok)
        out.append(tok)
    s = ' '.join(out)
    s = re.sub(r'\b(Mt|Mr)\b', r'\1.', s)
    s = re.sub(r'(?<=\w) (Of|The|And)\b', lambda m: ' ' + m.group(1).lower(), s)
    s = re.sub(r'\b(' + '|'.join(POSSESSIVE) + r')s\b', r"\1's", s)
    return s.replace('Pokemon', 'Pokémon').replace('Poke ', 'Poké ')

POSSESSIVE = ('Steven', 'Sidney', 'Phoebe', 'Glacia', 'Drake', 'Wally', 'Briney', 'Cutter', 'Maniac', 'Wallace', 'Champion',
              'Rydel', 'Lanette', 'Brendan', 'May', 'Fan Club', 'Breeder', 'Collector', 'Sailor', 'Explorer', 'Professor')

def place_key(name):
    """Routes in number order first, then everything else alphabetically."""
    m = re.match(r'Route(\d+)', name)
    return (0, int(m.group(1)), name) if m else (1, 0, place(name))


# ---- wild Pokémon ---------------------------------------------------------------------------------------------------
def parse_encounters(path):
    """The first table of an encounter source (a four-season file repeats it): {section: [(species, lo, hi)]}."""
    out, cur = collections.OrderedDict(), None
    for line in open(path):
        s = line.split('//')[0].strip()
        if s == 'EncountersEnd': break
        m = re.match(r'Encounter (SPECIES_\w+), (\d+), (\d+)', s)
        if m and cur: out[cur].append((m.group(1), int(m.group(2)), int(m.group(3))))
        elif re.fullmatch(r'\w+Encounters', s): cur = s; out[cur] = []
    return out

def combine(mons, odds, names):
    """Rows species, levels, percent (same species summed, as a player sees the odds)."""
    acc = collections.OrderedDict()
    for (sp, lo, hi), p in zip(mons, odds):
        a = acc.setdefault(sp, [lo, hi, 0])
        a[0], a[1], a[2] = min(a[0], lo), max(a[1], hi), a[2] + p
    rows = sorted(acc.items(), key=lambda kv: -kv[1][2])
    return [(names.species(sp), f'{lo}' if lo == hi else f'{lo}-{hi}', f'{p}%') for sp, (lo, hi, p) in rows]

def rock_smash_tables():
    """map name -> [(species, lo, hi)] (scaled levels): the version's decomp rock_smash_mons of every built map, as
    patches/hm_free.py rock_smash_wild_asm reads them."""
    dec = 'pokeemerald' if version.is_emerald() else 'pokeruby'
    folder = {}
    for mj in glob.glob(os.path.join(ROOT, 'external', dec, 'data', 'maps', '*', 'map.json')):
        folder[json.load(open(mj))['id']] = os.path.basename(os.path.dirname(mj))
    groups = json.load(open(os.path.join(ROOT, 'external', dec, 'src', 'data', 'wild_encounters.json')))
    suffix = None if version.is_emerald() else ('_Ruby' if version.is_ruby() else '_Sapphire')
    D = os.path.join(ROOT, 'data')
    zones = version.load_json(os.path.join(D, 'hoenn_zones.json'))['maps']
    rooms = version.load_json(os.path.join(D, 'hoenn_interiors.json')); rooms = rooms.get('rooms', rooms)
    curve = json.load(open(os.path.join(D, 'level_scaling.json')))['curve']['table']
    out = {}
    for e in groups['wild_encounter_groups'][0]['encounters']:
        if 'rock_smash_mons' not in e or (suffix and not e.get('base_label', '').endswith(suffix)): continue
        name = folder.get(e['map'])
        name = name and version.hoenn_map(name)          # (Emerald's renames and name clashes, as hm_free.py)
        z = (zones.get(name) or {}).get('zone') or ((rooms.get(name) or {}).get('zone') if isinstance(rooms.get(name), dict) else None)
        if z is None: continue
        out[name] = [(m['species'], int(curve[str(m['min_level'])]), int(curve[str(m['max_level'])]))
                     for m in e['rock_smash_mons']['mons']]
    return out

def _sections(t, names):
    """[(title, rows)] of a parsed encounter table: grass / cave floor, surfing and the three rods."""
    sec = []
    if t.get('GrassEncounters'): sec.append(('Grass and cave floor', combine(t['GrassEncounters'], GRASS, names)))
    if t.get('SurfEncounters'): sec.append(('Surfing', combine(t['SurfEncounters'], SURF, names)))
    rip = t.get('RipplingFishingEncounters') or []
    if rip[:2]: sec.append(('Old Rod', combine(rip[:2], OLD_ROD, names)))
    if rip[2:5]: sec.append(('Good Rod', combine(rip[2:5], GOOD_ROD, names)))
    if t.get('FishingEncounters'): sec.append(('Super Rod', combine(t['FishingEncounters'], SUPER_ROD, names)))
    return sec

AFTER_CHAMPION = 'after the Champion'

def wild_areas(names):
    """[(maps, sections, after)] of every area with wild Pokémon, in the page's order: maps sharing an encounter file,
    sections [(title, rows)], and after {title: rows}: the sections the area's post-game twin changes. After the Champion
    (FLAG_SYS_GAME_CLEAR) a zone whose file is one of a version's maps in data/hoenn_postgame_encounters.json (data/ruby/,
    data/emerald/ replace its "maps") reads the twin instead (converter/gen_postgame_encounters.py writes the twins,
    b2tools/patches/postgame_encounters.py pairs them, keyed by the file; notes/POSTGAME.md "Post-game dex completion")."""
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    import gen_postgame_encounters
    pg_files, pg_maps = gen_postgame_encounters.load()
    enc = version.load_json(os.path.join(ROOT, 'data', 'hoenn_encounters.json'))
    by_file = collections.defaultdict(list)
    for m, f in enc.items():
        if m.startswith('_') or not isinstance(f, int): continue
        if re.search(r'_\d+$', m) and m.rsplit('_', 1)[0] in enc: continue     # Altering Cave's Mystery Event tables
        by_file[f].append(m)
    files = {int(os.path.basename(p)[:4]): p for p in version.overlay(os.path.join(ROOT, 'src', 'encounters'), '*.s')}
    smash = rock_smash_tables()
    areas, shown = [], set()
    for f, maps in by_file.items():
        if f not in files: continue
        sec = _sections(parse_encounters(files[f]), names)
        after = {}
        twins = {pg_files[m] for m in maps if m in pg_maps}
        if len(twins) > 1: raise SystemExit(f'gen_docs: file {f} has two post-game twins {twins}: update wild_areas')
        if twins:
            twin = twins.pop()
            if '_pg_' not in os.path.basename(files.get(twin, '')):
                raise SystemExit(f'gen_docs: post-game twin {twin} of {maps} is not a _pg_ table: update wild_areas')
            before = dict(sec)
            for title, rows in _sections(parse_encounters(files[twin]), names):
                if before.get(title) != rows: after[title] = rows
            if not after or set(after) - set(before):
                raise SystemExit(f'gen_docs: the post-game twin of {maps} changes nothing or adds a section: update wild_areas')
            shown.update(m for m in maps if m in pg_maps)
        for m in maps:
            if m in smash: sec.append(('Rock Smash', combine(smash.pop(m), ROCK_SMASH, names)))
        if sec: areas.append((sorted(maps, key=place_key), sec, after))
    for m, mons in smash.items():                            # a rock-smash map without other wild Pokémon
        areas.append(([m], [('Rock Smash', combine(mons, ROCK_SMASH, names))], {}))
    if set(pg_maps) - shown:
        raise SystemExit(f'gen_docs: post-game tables of {sorted(set(pg_maps) - shown)} are not on the page: update wild_areas')
    areas.sort(key=lambda a: place_key(a[0][0]))
    return areas

def area_name(maps):
    return ' / '.join(place(m) for m in maps)

def postgame_new(areas):
    """{species name: [(area name, how)]} of the Pokémon an area has only after the Champion (how: the section titles)."""
    out = collections.OrderedDict()
    for maps, sec, after in areas:
        before = dict(sec)
        hows = collections.defaultdict(list)
        for title, rows in after.items():
            old = {r[0] for r in before.get(title, [])}
            for r in rows:
                if r[0] not in old: hows[r[0]].append(title)
        for mon, ts in hows.items():
            out.setdefault(mon, []).append((area_name(maps), ts))
    return out

def safari_rules(names):
    """The Safari Zone's game (user decision 2026-11-10, notes/DECISIONS.md; notes/STORY_HANDOFFS.md "Safari Zone"), as
    the gate's scripts (1138, scenes/SafariZone_Southeast.inc), the announcements (1260, src/text/overrides_safari.json)
    and our C (decomp include/hoennb2/safari.h, src/hoennb2/resident/safari.c) have it: the wild page's section's lines,
    or None without our C (the public snapshot)."""
    if not has_our_c():
        print(f'{version.NAME}: the Safari Zone rules left out of wild-pokemon-{version.VERSION}.md (the decomp tree has no HoennB2 C)')
        return None
    rel_h, rel_c = 'include/hoennb2/safari.h', 'src/hoennb2/resident/safari.c'
    h, c = _decomp_c(rel_h), _decomp_c(rel_c)
    steps, flee = _c_define(h, 'HOENNB2_SAFARI_STEPS', rel_h), _c_define(h, 'HOENNB2_SAFARI_FLEE_PERCENT', rel_h)
    for t in ('script = HOENNB2_SCRID_SAFARI_OUT_OF_BALLS;', 'PlayerSave_GetStepCounter(playerSave) >= HOENNB2_SAFARI_STEPS',
              'if (!sInSafari && zone != HOENNB2_SAFARI_GATE_ZONE) {', 'TakeSafariBalls(gameData);',
              'GFL_RandomMTRange(100) < HOENNB2_SAFARI_FLEE_PERCENT', '(param->item == ITEM_SAFARI_BALL) != (sInSafari != FALSE)',
              'return zone == HOENNB2_SAFARI_REST_HOUSE_ZONE || GetZoneMatrixId(zone) == GetZoneMatrixId(HOENNB2_SAFARI_MATRIX_ZONE);',
              'return HOENNB2_TRAP_NONE;', 'BOOL HoennB2_Safari_CheckSureEscape('):
        if t not in c: raise SystemExit(f'gen_docs: {rel_c} no longer has {t!r}: update safari_rules')
    if "Emerald's two expansion parts share it" not in h:
        raise SystemExit(f"gen_docs: {rel_h}: Emerald's Safari expansion is no longer in the game: update safari_rules")
    gate = '1138_room_Route121_SafariZoneEntrance.s'
    fee, balls = _define(gate, 'SZE_FEE'), _define(gate, 'SZE_BALLS')
    _need(gate, 'h_checkitem ITEM_POKEBLOCK_CASE, 1, C8B_SEL', 'PokePartyGetCount C8B_A, 0', 'BoxGetCount C8B_A, 5',
          'c8b_take_safari_balls               // (discord_fixes', 'ItemAdd ITEM_SAFARI_BALL, SZE_BALLS, C8B_B',
          'PedometerEnd', 'PedometerStart', 'h_setvar VAR_SAFARI_ZONE_STATE, 2')
    _need('scenes/SafariZone_Southeast.inc', 'h_setvar VAR_SAFARI_ZONE_STATE, 3', 'SZSE_Camper:', 'h_yesno T_CamperAsk, C8B_SEL')
    _need('1260_global_pokedex_rating.s', 'SystemMsg T_SafariTimesUp, 2', 'SystemMsg T_SafariOutOfBalls, 2')
    over = json.load(open(os.path.join(ROOT, 'src', 'text', 'overrides_safari.json'), encoding='utf-8'))
    def line(f, n):
        return '"' + over[f][str(n)].replace('\\n', ' ').replace('’', "'") + '"'
    times_up = line('script/0434.txt', _define('1260_global_pokedex_rating.s', 'T_SafariTimesUp'))
    no_balls = line('script/0434.txt', _define('1260_global_pokedex_rating.s', 'T_SafariOutOfBalls'))
    only = line('system/0001.txt', _c_define(h, 'HOENNB2_MSG_SAFARI_BALLS_ONLY', rel_h))
    outside = line('system/0001.txt', _c_define(h, 'HOENNB2_MSG_SAFARI_BALLS_OUTSIDE', rel_h))
    case = names.item(_key_item('ITEM_POKEBLOCK_CASE'))
    ball = names.item('ITEM_SAFARI_BALL')
    return ['## Safari Zone rules\n',
            'The Safari Zone, north of Route 121, is a game as in Gen 3:\n',
            f'- **Entering:** the gate on Route 121 charges ${fee:,} and gives you {balls} {ball}s. You need the {case}, and '
            "with a full party a free place in your PC's Boxes (a Pokémon you catch goes there).",
            f'- **The game** lasts {steps} steps. It is over when you have walked them ({times_up}) or when your {ball}s '
            f'run out, after the battle in which you threw the last one ({no_balls}). Then you are back at the gate. The '
            'attendant by the door inside lets you leave sooner.',
            f'- **Leftover {ball}s** are taken back when the game ends. Flying away, Teleport or blacking out ends the game '
            'too, and takes the balls.',
            f'- **Battles** are normal battles: your Pokémon fight as anywhere else (there is no bait or rock). Only {ball}s '
            f"can be thrown ({only}), and they can't be used anywhere else ({outside}). Each turn, the wild Pokémon runs "
            f'away {flee}% of the time. You can always run, as in Gen 3: no ability such as Shadow Tag stops you.',
            '- The DexNav works here too: a search costs only the steps you walk, and its Pokémon follow the same rules.'
            + (" Emerald's two new areas (after the Hall of Fame) are part of the game." if version.is_emerald() else '')]

def wild_page(names):
    areas = wild_areas(names)
    safari = safari_rules(names)
    v = version.NAME
    L = [HEADER, f'# Wild Pokémon: {version.PUBLIC_NAME}\n',
         f'Every area with wild Pokémon, as the game has them. The tables are {v}\'s own (from the '
         f'{"pokeemerald" if version.is_emerald() else "pokeruby"} decompilation), with the same odds per slot.',
         'Levels above 24 are raised to go with the Exp. Share (levels up to 24 are unchanged), so the '
         'levels here are the ones you meet.\n',
         '- Each rod fishes its own table, as in Gen 3: the Old Rod, the Good Rod and the Super Rod.',
         '- Rock Smash: breaking a rock sometimes starts a battle, as in Gen 3.',
         '- Percentages add up the slots of the same Pokémon.',
         '- **After the Champion** (from your first Hall of Fame on), some areas use a second '
         f'table, marked "{AFTER_CHAMPION}": the other versions\' Pokémon take some of their slots, so you can catch '
         f'them without trading ([completing the Pokédex](postgame-{version.VERSION}.md#completing-the-pokédex)).'
         + ('' if safari else '\n'),
         *(['- **Safari Zone:** its areas are a game with its own rules ([Safari Zone rules](#safari-zone-rules)).\n']
           if safari else []),
         '## Areas\n']
    L += [f'- [{area_name(maps)}](#{_anchor(area_name(maps))})' + (f' (changes {AFTER_CHAMPION})' if after else '')
          for maps, _, after in areas]
    for maps, sec, after in areas:
        L += ['', f'## {area_name(maps)}']
        for title, rows in sec:
            L += ['', f'**{title}**', '', '| Pokémon | Level | Chance |', '|---|---|---|']
            L += [f'| {a} | {b} | {c} |' for a, b, c in rows]
            if title in after:
                L += ['', f'**{title}, {AFTER_CHAMPION}**', '', '| Pokémon | Level | Chance |', '|---|---|---|']
                L += [f'| {a} | {b} | {c} |' for a, b, c in after[title]]
                new = [r[0] for r in after[title] if r[0] not in {x[0] for x in rows}]
                if new: L += ['', f'New {AFTER_CHAMPION}: {_join(new)}.']
        if 'Route119' in maps:                               # patches/feebas.py: Gen 3's hidden spots, no table of their own
            scale = json.load(open(os.path.join(ROOT, 'data', 'level_scaling.json')))['curve']['table']
            L += ['', f'**Feebas: fish on Route 119, 6 spots.** Six water tiles of the route, different in every save and fixed '
                      f'for that save, as in Gen 3: fishing there with any rod, half the bites are a Feebas (Lv {scale["20"]}-{scale["25"]}), '
                      'the others come from the tables above.']
    if safari: L += [''] + safari
    return '\n'.join(L) + '\n'

def _anchor(s):
    s = s.lower().replace(' / ', '--')
    return re.sub(r'[^a-z0-9 _-]', '', s).replace(' ', '-')

def _slug(s):
    """GitHub's anchor of a heading (letters with accents kept, as 'completing-the-pokédex')."""
    return re.sub(r'[^\w\- ]', '', s.lower()).replace(' ', '-')


# ---- items ------------------------------------------------------------------------------------------------------------
def items_page(names):
    D = os.path.join(ROOT, 'data')
    balls = version.load_json(os.path.join(D, 'hoenn_items.json'))['balls']
    hidden = version.load_json(os.path.join(D, 'hoenn_hidden_items.json'))['items']
    trees = version.load_json(os.path.join(D, 'hoenn_berry_trees.json'))['trees']    # berry planting's Gen 3 trees
    sapphire_only = set(version.load_json(os.path.join(D, 'hoenn_items.json')).get('sapphire_only') or [])
    area = collections.defaultdict(lambda: {'ball': [], 'hidden': [], 'berry': []})
    for k, b in balls.items():
        if k in sapphire_only or b.get('built') is False: continue
        m = b.get('map') or k.split('_EventScript')[0]
        n = names.item(b['item']) + (f' x{b["count"]}' if b.get('count', 1) > 1 else '')
        area[m]['ball'].append(n)
    for k, h in hidden.items():
        if h.get('built') is False or k in (version.load_json(os.path.join(D, 'hoenn_hidden_items.json')).get('sapphire_only') or []): continue
        area[h['map']]['hidden'].append(names.item(h['item']))
    for k, t in trees.items():
        if k.startswith('_'): continue
        area[t['map']]['berry'].append(names.item(t['berry']) if t.get('berry') else 'soft soil')
    L = [HEADER, f'# Item locations: {version.PUBLIC_NAME}\n',
         'Items on the ground (item balls), hidden items (use the Itemfinder, or press A on the spot) and the daily '
         'berry spots, by area. Gifts from people and shops are not listed here; the TMs people give are on the '
         '[TM page](tms-and-hms.md).\n',
         'Berry trees work as in Gen 3: pick a ripe tree, then plant any berry in the soft soil (talk to it) and water '
         'it with the Wailmer Pail (from the flower shop on Route 104). Trees grow by the DS clock. The list shows '
         'what each spot holds at the start of a new game.\n']
    for m in sorted(area, key=place_key):
        a = area[m]
        L += [f'## {place(m)}', '']
        if a['ball']: L.append('- Items: ' + ', '.join(a['ball']))
        if a['hidden']: L.append('- Hidden: ' + ', '.join(a['hidden']))
        if a['berry']: L.append('- Berry trees: ' + ', '.join(sorted(a['berry'])))
        L.append('')
    return '\n'.join(L)


# ---- trainers ---------------------------------------------------------------------------------------------------------
BOSS_CLASSES = ('LEADER', 'ELITE_FOUR', 'CHAMPION', 'AQUA_LEADER', 'MAGMA_LEADER', 'AQUA_ADMIN', 'MAGMA_ADMIN')
RIVALS = ('Brendan', 'May', 'Wally', 'Steven')
GROUPS = [('Gym Leaders', ('LEADER',)), ('Elite Four', ('ELITE_FOUR',)), ('Champion', ('CHAMPION',)),
          ('Rivals and friends', ('RIVAL',)), ('Team Aqua and Team Magma', ('AQUA_LEADER', 'MAGMA_LEADER', 'AQUA_ADMIN', 'MAGMA_ADMIN'))]

def trainers_page(names):
    """One entry per Black 2 trainer id (an Emerald record is there under its Emerald name and its Sapphire twin's;
    Emerald's merged data still holds Sapphire's records of ids Emerald reuses: only records with "emerald_trainer")."""
    data = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers']
    by_id = {}
    for k, t in data.items():
        if version.is_emerald() and 'emerald_trainer' not in t: continue
        by_id.setdefault(t['b2_id'], t)
    seen, groups = set(), collections.defaultdict(lambda: collections.defaultdict(list))
    for t in by_id.values():
        cls = t['sapphire_class']
        if cls not in BOSS_CLASSES and not (cls == 'POKEMON_TRAINER_3' and t['name'] in RIVALS): continue
        if t.get('rematch_of'): continue           # (rematches: not built yet)
        party = tuple((p['species'], p['level'], p.get('item', 'ITEM_NONE'), tuple(p.get('moves') or ())) for p in t['party'])
        if (t['name'], party) in seen: continue
        seen.add((t['name'], party))
        groups['RIVAL' if cls == 'POKEMON_TRAINER_3' else cls][t['name']].append((t, party))
    L = [HEADER, f'# Important trainers: {version.PUBLIC_NAME}\n',
         'The teams of the Gym Leaders, the Elite Four, the Champion, your rival, Wally, and the team bosses. '
         'Levels above 24 are raised to go with the Exp. Share. Your rival\'s team depends on the starter you chose, '
         'so each rival battle is listed once per starter (you meet only one of each).\n']
    for title, classes in GROUPS:
        people = {}
        for c in classes:
            for n, battles in groups.get(c, {}).items(): people.setdefault(n, []).extend(battles)
        if not people: continue
        L += [f'## {title}', '']
        order = sorted(people, key=lambda n: min(max(p[1] for p in party) for _, party in people[n]))
        for n in order:
            battles = sorted(people[n], key=lambda b: (max(p[1] for p in b[1]), len(b[1])))
            L += [f'### {n}', '']
            for i, (t, party) in enumerate(battles):
                maps = t.get('maps') or [o['map'] for o in t.get('objects') or []]
                where = ', '.join(sorted({place(m) for m in maps}))
                head = f'Battle {i + 1}' + (f' ({where})' if where else '') + (' (double battle)' if t.get('double') else '')
                L += [f'**{head}**', '', '| Pokémon | Level | Held item | Moves |', '|---|---|---|---|']
                for sp, lv, item, moves in party:
                    it = '' if item in ('ITEM_NONE', None) else names.item(item)
                    mv = ', '.join(names.move(m) for m in moves if m != 'MOVE_NONE')
                    L.append(f'| {names.species(sp)} | {lv} | {it} | {mv or "(its level-up moves)"} |')
                L.append('')
    return '\n'.join(L)


# ---- shared pages ----------------------------------------------------------------------------------------------------
def tms_page(names):
    import new_tms
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    import gen_items
    b2 = gen_items.tm_items()
    new = new_tms.move_to_item()
    gen3 = re.findall(r'#define ITEM_(TM|HM)(\d+)_(\w+)\s', open(os.path.join(ROOT, 'external', 'pokeruby', 'include', 'constants', 'items.h')).read())
    L = [HEADER, '# TMs and HMs\n',
         'Hoenn\'s TMs and HMs are Black 2\'s items. Black 2 numbers its TMs differently, so a Gen 3 TM is the Black 2 '
         'TM that teaches the same move. The nine Gen 3 TM moves Black 2 has no TM for have their own new TMs, '
         'TM96 to TM104. Every Pokémon that could learn the Gen 3 TM can learn the new one.\n',
         '## Gen 3 TMs\n', '| Gen 3 | Move | In this game |', '|---|---|---|']
    for kind, num, mv in gen3:
        move = 'MOVE_' + mv.replace('SOLARBEAM', 'SOLAR_BEAM')
        item = b2.get(move) or new.get(move)
        here = names.item(item) if item else 'not given in this game'
        L.append(f'| {kind}{num} | {names.move(move)} | {here} |')
    L += ['', '## The new TMs\n', '| TM | Move | Was (Gen 3) |', '|---|---|---|']
    for n, _, mv, g3 in new_tms.NEW_TMS:
        L.append(f'| TM{n} | {names.move(mv)} | {g3} |')
    L += ['', '## Field moves without HMs\n',
          'Obstacles are still there, but you don\'t have to teach an HM. As in Ruby and Sapphire, a field move needs '
          'its Hoenn badge; then either a Pokémon that knows the move or the move\'s TM/HM in your Bag is enough.\n',
          '| Move | Item in the Bag | Badge |', '|---|---|---|']
    for mv, item, badge in (('Cut', 'ITEM_HM01', 'Stone'), ('Flash', 'ITEM_TM70', 'Knuckle'), ('Rock Smash', 'ITEM_TM94', 'Dynamo'),
                            ('Strength', 'ITEM_HM04', 'Heat'), ('Surf', 'ITEM_HM03', 'Balance'), ('Fly', 'ITEM_HM02', 'Feather'),
                            ('Dive', 'ITEM_HM06', 'Mind'), ('Waterfall', 'ITEM_HM05', 'Rain')):
        L.append(f'| {mv} | {names.item(item)} | {badge} Badge |')
    return '\n'.join(L) + '\n'

def fairy_page(names):
    import fairy
    sp = {v: k for k, v in names.species_id.items()}
    L = [HEADER, '# The Fairy type (optional)\n',
         'Birch\'s first question at the start of the game turns the Fairy type on or off. With it on, the game uses '
         'Gen 6\'s type chart and these changes. With it off, everything is as in Black 2.\n',
         '## Pokémon that gain the Fairy type\n', '| Pokémon | Type |', '|---|---|']
    for s, (a, b) in sorted(fairy.RETYPES.items()):
        t = a.capitalize() if a == b else f'{a.capitalize()} / {b.capitalize()}'
        L.append(f'| {names.species_t[s]} | {t} |')
    L += ['', '## Moves that become Fairy-type\n'] + [f'- {n}' for n in fairy.RETYPED_MOVES.values()]
    L += ['', '## New Fairy moves\n', '| Move | Power | Accuracy | PP |', '|---|---|---|---|']
    for mid, name, _, ch, _, _ in fairy.NEW_MOVES:
        acc = '-' if ch['acc'] > 100 else ch['acc']
        L.append(f'| {name} | {ch["power"]} | {acc} | {ch["pp"]} |')
    new = {mid: name for mid, name, *_ in fairy.NEW_MOVES}
    L += ['', '## Who learns them\n', '| Pokémon | Learns |', '|---|---|']
    for s, ms in sorted(fairy.LEVEL_UP.items()):
        L.append(f'| {names.species_t[s]} | ' + ', '.join(f'{new[m]} ({"Lv. " + str(lv) if lv > 1 else "start"})' for lv, m in ms) + ' |')
    for s, ms in sorted(fairy.EGG_MOVES.items()):
        L.append(f'| {names.species_t[s]} | ' + ', '.join(f'{new[m]} (Egg move)' for m in ms) + ' |')
    L += ['', 'New items: the Pixie Plate and the Fairy Gem.', '']
    return '\n'.join(L)

KEPT_EVOS = {('SPECIES_POLIWHIRL', 'EVO_METHOD_ITEM', 'ITEM_WATER_STONE'), ('SPECIES_SLOWPOKE', 'EVO_METHOD_LEVEL', 37),
             ('SPECIES_FEEBAS', 'EVO_METHOD_BEAUTY', 170)}     # Black 2's own, kept beside the new ones (trade_evos.json _doc)

def evolutions_page(names):
    d = json.load(open(os.path.join(ROOT, 'data', 'trade_evos.json')))
    def use(c):
        n = names.item(c) if isinstance(c, str) else str(c)
        return f'use {"an" if n[:1] in "AEIOU" else "a"} {n}'
    how = {'EVO_METHOD_LEVEL': lambda p: f'reach level {p}', 'EVO_METHOD_ITEM': use,
           'EVO_METHOD_SPECIES_IN_PARTY': lambda p: f'level up with {names.species(p) if isinstance(p, str) else p} in the party'}
    L = [HEADER, '# Trade evolutions\n',
         'Every Pokémon that evolves by trading can also evolve without a trade here (trading them with a friend still works):\n',
         '- a plain trade evolution happens at a level instead;',
         '- a trade holding an item becomes using that item from the Bag, like an evolution stone (the item can still be held);',
         '- Karrablast and Shelmet evolve when they level up with the other one (or its evolution) in the party.\n',
         '| Pokémon | Evolves into | How |', '|---|---|---|']
    for s, evos in d['evolutions'].items():
        for meth, param, into in evos:
            if (s, meth, param) in KEPT_EVOS: continue
            f = how.get(meth)
            L.append(f'| {names.species(s)} | {names.species(into)} | {f(param) if f else meth} |')
    shop = d.get('shop') or {}
    if shop.get('add'):
        L += ['', 'Items with no other source in Hoenn (and the Metal Coat and Dragon Scale) are sold at the Lilycove '
              'Department Store, 3F (the right clerk): ' + ', '.join(names.item(i) for i in shop['add']) + '.']
    L += ['', '## Evolution stones\n',
          'The Fire, Water, Thunder, Leaf, Moon and Sun Stones are found in Hoenn. The Shiny, Dusk and Dawn Stones and the '
          'Oval Stone are not, so the Lilycove Department Store sells them for 2,100 each. Use a stone from the Bag; a '
          'Happiny evolves when it levels up during the day holding an Oval Stone. The Razor Claw and Razor Fang (held at '
          'night, Weavile and Gliscor) are sold for 8 BP in the Pokémon World Tournament lobby.']
    return '\n'.join(L) + '\n'

def options_page():
    L = [HEADER, '# Start-of-game options\n',
         'Before your adventure starts, Professor Birch asks seven questions. Your answers set these options, and '
         'they can\'t be changed later, except Following Pokémon.\n',
         '| Question | Answers | What it changes |', '|---|---|---|',
         '| The Fairy type | Yes / No | Yes: the Fairy type, Gen 6\'s type chart, new Fairy moves ([details](fairy-type.md)). No: Black 2\'s types. |',
         '| Physical / special | Each move\'s own / By type | Modern split (each move is physical or special), or the classic Gen 3 rule (the move\'s type decides). |',
         '| Music | Hoenn / Unova | Hoenn\'s original soundtrack played on Black 2\'s instruments, or Black 2\'s music. |',
         '| Character sprites | Classic / New | The Gen 3 style sprites, or new Gen 5 style ones made by community artists: '
         'overworld sprites, and battle sprites for many trainers. |',
         '| Seasons | Yes / No | Yes: Black 2\'s seasons follow the month on your DS clock (spring: Jan/May/Sep, summer: '
         'Feb/Jun/Oct, autumn: Mar/Jul/Nov, winter: Apr/Aug/Dec). No: summer all year, as in Ruby and Sapphire. |',
         '| The Exp. Share | Yes / No | Yes: you start with the Exp. Share in your Key Items, switched on: Pokémon that '
         'don\'t battle still gain Exp. Points. Use it in the Bag to switch it off or on. No: Mr. Stone gives it to you in '
         'Rustboro after you deliver his Letter, as in the original games. |',
         '| Following Pokémon | Yes / No | Yes: your first Pokémon walks behind you. No: it stays in its Poké Ball. The aide '
         'in Birch\'s lab in Littleroot switches this on or off at any time, on saves from older versions too. |']
    return '\n'.join(L) + '\n'

def frontier_page(names):
    import frontier_core
    ban = frontier_core.banned_names_order(frontier_core.banned())
    L = [HEADER, '# Battle Frontier, Battle Tents and Trainer Hill (Emerald only)\n',
         'Pokémon Emerald NDS has the whole Battle Frontier: the Battle Tower, Dome, Palace, Arena, Factory, Pike and '
         'Pyramid, with Emerald\'s rules, Battle Points and prizes.\n',
         '## Rules for every facility\n',
         '- **Level 50**: Pokémon of level 50 or lower. **Open Level**: any level.',
         '- **Three Pokémon**, no Eggs.',
         '- **No duplicates**: no species twice, and no held item twice (Pokémon without items are fine).',
         '- **Banned Pokémon**: ' + ', '.join(names.species_t[s] for s in ban) + '.', '',
         '## Battle Points\n',
         'The Frontier\'s Battle Points are Black 2\'s own BP: one purse, up to 9,999. The Battle Tower and the '
         'Pokémon World Tournament pay into it too. Spend them at the Exchange Service Corner and with the move tutors.\n',
         '## Symbols\n',
         'Each facility has a Silver and a Gold Symbol, won from its Frontier Brain.\n',
         '## Battle Tents\n',
         'Three smaller challenges on the mainland, three battles each, with a prize for every challenge won:\n',
         '- **Verdanturf Battle Tent:** Battle Palace rules (your Pokémon choose their own moves). Prize: Nest Ball.',
         '- **Fallarbor Battle Tent:** Battle Arena rules (one Pokémon at a time, judged after 3 turns). Prize: Hyper Potion.',
         '- **Slateport Battle Tent:** Battle Factory rules (rent three of six Pokémon at Lv. 30, swap after a win). Prize: Full Heal.\n',
         '## Trainer Hill\n',
         'North of Mauville on Route 111, open after the Hall of Fame. Four modes (Normal, Variety, Unique, Expert Tag '
         'Match), four floors each, against the clock. The owner on the roof gives a prize by your time.\n']
    return '\n'.join(L)


# ---- the DexNav -------------------------------------------------------------------------------------------------------
def has_our_c():
    """True when the decomp tree (b2decomp.SRC) has HoennB2's own C (include/hoennb2.h): the private repo's, where the
    DexNav page and the Safari Zone's rules read its code and every check applies (a missing file stops the run). The
    public source snapshot is used with upstream pokebw2, which has none of it: there dexnav.md and the Safari rules are
    skipped with a one-line note, and nothing links them."""
    return os.path.exists(os.path.join(B2, 'include', 'hoennb2.h'))

def _decomp_c(rel):
    """A file of the decomp tree the build uses (b2decomp.SRC): the DexNav's and the Safari Zone's C is ours, in
    include/hoennb2 and src/hoennb2 (decomp_changes/hoennb2_decomp.patch)."""
    p = os.path.join(B2, rel)
    if not os.path.exists(p): raise SystemExit(f'gen_docs: no {rel} in {B2} (it has HoennB2\'s C otherwise): the guide reads it')
    return open(p, encoding='utf-8').read()

def _c_define(src, name, rel):
    m = re.search(rf'#define\s+{name}\s+(\d+)\b', src)
    if not m: raise SystemExit(f'gen_docs: {rel} has no {name} any more: update dexnav_page')
    return int(m.group(1))

def _c_body(src, name, rel):
    m = re.search(rf'\nstatic u32 {name}\(u32 level(?:, u32 chain)?\) \{{\n(.*?)\n\}}\n', src, re.S)
    if not m: raise SystemExit(f'gen_docs: {rel} has no {name} as the page reads it: update dexnav_page')
    return m.group(1)

def _c_ladder(body, name, rel):
    """`return level >= 100 ? 25 : level >= 50 ? 20 : ... : 0;` -> [(100, 25), (50, 20), ..., (0, 0)]."""
    m = re.fullmatch(r'\s*return ((?:level >= \d+ \? \d+ : )+)(\d+);\s*', body)
    if not m: raise SystemExit(f'gen_docs: {rel} {name} is no longer a simple ladder: update dexnav_page')
    return [(int(a), int(b)) for a, b in re.findall(r'level >= (\d+) \? (\d+)', m.group(1))] + [(0, int(m.group(2)))]

def dexnav_page(names):
    """dexnav.md (notes/DEXNAV.md): the DexNav in every version, read from its code (the decomp's
    src/hoennb2/resident/dexnav.c and src/hoennb2/dexnav/dexnav_screen.c), its scripts (the Lab's gift, Route 101's
    tutorial), its text (b2tools/dexnav_art.py TEXT) and b2tools/patches/dexnav.py (the tutorial's species and moves)."""
    if not has_our_c():
        return None
    import dexnav_art, dexnav as dexnav_patch
    rel_c, rel_s, rel_h = 'src/hoennb2/resident/dexnav.c', 'src/hoennb2/dexnav/dexnav_screen.c', 'include/hoennb2/dexnav.h'
    c, scr, h = _decomp_c(rel_c), _decomp_c(rel_s), _decomp_c(rel_h)
    # the screen's lines, by dexnav_screen.c's TXT_ names
    enum = re.search(r'// The text file\'s lines \(b2tools/dexnav_art.py TEXT\)\nenum \{\n(.*?)\n\};', scr, re.S)
    if not enum: raise SystemExit(f'gen_docs: {rel_s} has no TXT_ list any more: update dexnav_page')
    txt, i = {}, 0
    for name, num in re.findall(r'(TXT_\w+)(?: = (\d+))?,', enum.group(1)):
        i = int(num) if num else i
        txt[name] = dexnav_art.TEXT[i].replace('\\n', ' ').replace('’', "'")
        i += 1
    say = lambda k: f'"{txt[k]}"'
    # the numbers
    spot_min, spot_near, spot_max = (_c_define(c, n, rel_c) for n in ('SPOT_MIN', 'SPOT_NEAR', 'SPOT_MAX'))
    flee = _c_define(c, 'FLEE_DISTANCE', rel_c)
    odds = _c_define(c, 'SHINY_ODDS', rel_c)
    lv_max, chain_max = _c_define(h, 'DEXNAV_LEVEL_MAX', rel_h), _c_define(h, 'DEXNAV_CHAIN_MAX', rel_h)
    reveal = {k: _c_define(scr, f'REVEAL_{k}', rel_s) for k in ('POTENTIAL', 'ABILITY', 'MOVE')}
    ivs_body = _c_body(c, 'PerfectIVs', rel_c)
    ivs = [(int(a), int(b), int(x or 0)) for a, b, x in
           re.findall(r'if \(level >= (\d+)\) \{\s*return (\d+)(?: \+ Chance\((\d+)\))?;\s*\}', ivs_body)]
    last = re.search(r'\}\s*return Chance\((\d+)\);\s*$', ivs_body)
    if not ivs or not last: raise SystemExit(f'gen_docs: {rel_c} PerfectIVs changed shape: update dexnav_page')
    ivs.append((0, 0, int(last.group(1))))
    ladders = {k: _c_ladder(_c_body(c, f, rel_c), f, rel_c) for k, f in
               (('ability', 'HiddenAbilityChance'), ('egg', 'EggMoveChance'), ('item', 'RareItemChance'))}
    sh = re.search(r'rolls = \(chain >= (\d+) \? (\d+) : chain / (\d+)\) \+ level / (\d+);\s*'
                   r'if \(chain == (\d+) \|\| chain == (\d+)\) \{\s*rolls \+= (\d+);', _c_body(c, 'ShinyRolls', rel_c))
    if not sh: raise SystemExit(f'gen_docs: {rel_c} ShinyRolls changed shape: update dexnav_page')
    cap_at, cap, per_chain, per_level, bonus_a, bonus_b, bonus = (int(x) for x in sh.groups())
    def rolls(level, chain):
        return (cap if chain >= cap_at else chain // per_chain) + level // per_level + (bonus if chain in (bonus_a, bonus_b) else 0)
    def one_in(n):            # the game's own try, then n more, each 1 in `odds`
        return f'1 in {round(1 / (1 - (1 - 1 / odds) ** (1 + n))):,}'
    # what the page states, as the code has it
    for t in ('AddSlots(list, dex, gameData, enc->grass, 12, DEXNAV_GROUP_LAND', 'AddSlots(list, dex, gameData, enc->surf, 5, DEXNAV_GROUP_WATER',
              'if (FieldPlayer_GetExState(player) == FLD_PLAYER_EXSTATE_CYCLING) {', 'acmd >= ACMD_DASH',
              'if (result == BTL_RESULT_VICTORY || result == BTL_RESULT_CAPTURE) {\n            AddSearchLevel(gameData, work->species);',
              'chainSpecies == work->species && chain < DEXNAV_CHAIN_MAX ? chain + 1 : 1', '} else if (!work->tutorial) {\n            SetChain(gameData, work->species, 0);',
              'chain = 0;                          // another species: the chain starts again',
              'HoennB2_DexNav_RandomEncounter(EncountSystem *system, u32 mode) {\n    if (CFG != NULL && system != NULL && system->field != NULL && SpotIsOurs(system)) {\n        return NULL;',
              'sSearch.item = (u16)PML_PersonalGetParamSingle(sSearch.species, sSearch.form, PERSONAL_ITEM_2);',
              'return hidden != 0 && hidden != PML_PersonalGetParamSingle(species, form, PERSONAL_ABILITY_1)',
              'slot = i;       // the first empty slot, else the first move\'s', 'PokeParty_SetParam(pkm, PKM_PARAM_IV_HP + k, 31);',
              'if (mon->group == DEXNAV_GROUP_WATER && ExState(field) != FLD_PLAYER_EXSTATE_SURF) {',
              '} else if (!sSearch.tutorial && PlayerRunsOrRides(system->field)) {', 'EventWildBattleCall_CreateCore(system->gsys, system->field, setup, 0, 0, 0xff)',
              'sSearch.eggMove = CFG->tutorialMoves[GFL_RandomLC(3)];', 'kind = 4;'):
        if t not in c: raise SystemExit(f'gen_docs: {rel_c} no longer has {t!r}: update dexnav_page')
    for t in ('Dn_BlitHome(work, PIECE_CROWN);', 'Dn_Message(work, TXT_UNSEEN);', 'search->hiddenAbility', 'search->eggMove != 0'):
        if t not in scr: raise SystemExit(f'gen_docs: {rel_s} no longer has {t!r}: update dexnav_page')
    if 'TXT_CHAIN' in scr.split('// The files (b2tools/dexnav_art.py', 1)[1]:
        raise SystemExit(f'gen_docs: {rel_s} shows the chain now: update dexnav_page')
    _need('0792_birch_lab.s', 'VMCall DN_LabGive                             // the DexNav, after the Poké Balls', 'VMCall DN_LabOwed')
    lab = _src('0792_birch_lab.s').split('\nScript_7:', 1)[1]
    if lab.find('VMCall DN_LabOwed') > lab.find('VMCall PG_LabStartersDue'):      # (an old save: the DexNav before anything else)
        raise SystemExit('gen_docs: Birch no longer gives an old save the DexNav first: update dexnav_page')
    _need('scenes/BirchLab_DexNav.inc', 'MEPlay SEQ_ME_KEYITEM', 'h_setvar VAR_DEXNAV_STATE, DN_STATE_TUTORIAL', 'DN_LabOwed:',
          'h_goto_if_ne VAR_BIRCH_LAB_STATE, 5, L_DN_OwedDone', 'h_goto_if_ne VAR_DEXNAV_STATE, DN_STATE_NONE, L_DN_OwedDone')
    _need('0634_route_101.s', '#include "scenes/Route101_DexNav.inc"')
    _need('scenes/Route101_DexNav.inc', 'h_goto_if_ne DN_W_A, 0, DN_TutHasBalls', 'h_msgbox_gendered DN_T_INTRO_MAY, DN_T_INTRO_BRENDAN')
    balls = _num('scenes/Route101_DexNav.inc', r'h_giveitem ITEM_POKE_BALL, (\d+)')
    if "'-D', 'HOENN_DEXNAV'" not in open(os.path.join(HERE, 'patches', 'scripts.py'), encoding='utf-8').read():
        raise SystemExit('gen_docs: the scripts no longer build the DexNav: update dexnav_page')
    if '[_dexnav_button()]' not in open(os.path.join(HERE, 'pokenav_art.py'), encoding='utf-8').read() \
            or "'DEXNAV')" not in open(os.path.join(HERE, 'dexnav_art.py'), encoding='utf-8').read():
        raise SystemExit('gen_docs: the PokéNav menu has no DEXNAV button any more: update dexnav_page')
    tut = names.species(dexnav_patch.TUTORIAL_SPECIES)
    tut_moves = _or(names.move(m) for m in dexnav_patch.TUTORIAL_MOVES)
    if dexnav_patch.TUTORIAL_MAP != 'Route101': raise SystemExit('gen_docs: the DexNav tutorial moved: update dexnav_page')

    # the bonus table: a row per search-level band
    lows = sorted({lo for lo, _, _ in ivs} | {lo for lad in ladders.values() for lo, _ in lad})
    def at(lad, level): return next(v for lo, v in lad if level >= lo)
    def ivs_at(level):
        base, x = next((b, x) for lo, b, x in ivs if level >= lo)
        return f'{x}% chance of 1' if not base else f'{base}, {x}% chance of {base + 1}' if x else f'{base}'
    rows = []
    for k, lo in enumerate(lows):
        hi = lows[k + 1] - 1 if k + 1 < len(lows) else lv_max
        rows.append(f'| {lo}-{hi} | {ivs_at(lo)} | {at(ladders["ability"], lo)}% | {at(ladders["egg"], lo)}% | {at(ladders["item"], lo)}% |')
    chains = sorted({0, per_chain, 5 * per_chain, cap_at - 1, cap_at, cap_at + 1, bonus_a, bonus_b})
    levels = (0, per_level, 2 * per_level, lv_max)

    L = [HEADER, '# The DexNav\n',
         'The DexNav of Omega Ruby and Alpha Sapphire, in all three versions. It sits on the touch screen while you '
         'explore (the screen that used to stay empty) and has a page in the PokéNav. It shows the wild Pokémon of the '
         'place you are in, and it finds hidden Pokémon for you: they can come with perfect IVs, an egg move, their '
         'hidden ability or a rare held item, and now and then a shiny one.\n',
         '## Getting it\n',
         'Prof. Birch gives you the DexNav in his Lab, together with the Pokédex, right after your rival gives you Poké '
         'Balls. The touch screen turns into the DexNav at once.\n',
         'Already playing? If your save has its Pokédex from an older version, talk to Prof. Birch in his Lab and he gives '
         'you the DexNav, before anything else he has for you.\n',
         '## The tutorial on Route 101\n',
         'The first time you step into the tall grass of Route 101 after getting it, your rival (May, or Brendan if you '
         'play as May) runs up and shows you how it works:\n',
         f'- If you have no Poké Balls left, your rival gives you {balls}.',
         f'- The DexNav finds a {tut} hiding in shaking grass a few steps away. It knows {tut_moves}, one of its egg '
         'moves.',
         '- Walk onto the shaking grass to battle it. It is a normal wild battle: catch it or knock it out. This one '
         'doesn\'t run off if you hurry.',
         '- Afterwards your rival says goodbye and leaves. If you leave Route 101 before the battle, the shaking grass is '
         'back the next time you walk there.\n',
         '## The screen\n',
         '**The area map.** A map of the place you are in, drawn with its Gen 3 tiles. Each of its wild Pokémon stands on '
         'a tile of the kind it lives on: the ones of the tall grass, cave floor or sand on the ground, the ones you meet '
         'while surfing on the water. A Pokémon you have caught is in colour, one you have only seen is a dark shape, and '
         'one you haven\'t seen is a "?". A crown appears when you have caught every Pokémon of the place, and tapping '
         'the map tells you how far you are (' + ', '.join(say(k) for k in ('TXT_PROGRESS_SOME', 'TXT_PROGRESS_ALMOST', 'TXT_PROGRESS_DONE'))
         + f'). A place without wild Pokémon shows {say("TXT_NONE")} The POKéNAV button opens the PokéNav, once you have it.\n',
         'The DexNav lists the Pokémon of the tall grass, cave floors, sand and water. Pokémon you fish, find with Rock '
         'Smash or meet roaming, and Feebas, aren\'t on it. After the Champion it shows the area\'s new Pokémon too '
         '(completing the Pokédex: ' + ', '.join(f'[{VNAME[v]}](postgame-{v}.md#completing-the-pokédex)' for v in version.VERSIONS)
         + ').\n',
         f'**Found Pokémon.** Tap a Pokémon you have seen: its picture, name, type and search level, and SEARCH. (One '
         f'you haven\'t seen: {say("TXT_UNSEEN")})\n',
         '**Hidden Pokémon.** While a Pokémon hides, this shows what the DexNav knows about it. Its level always; the '
         'rest only from a high enough search level for that species (before that it shows "???"):\n',
         '| Shown | From search level |', '|---|---|',
         '| Level | always |',
         f'| Potential: a gold star for each perfect IV (up to three) | {reveal["POTENTIAL"]} |',
         f'| Ability ("!" for its hidden ability) | {reveal["ABILITY"]} |',
         f'| First Move ("!" for an egg move) | {reveal["MOVE"]} |', '',
         'The bonuses are decided when the search starts, so the battle\'s Pokémon is the one the screen shows.\n',
         '## Searching\n',
         '1. Tap a Pokémon on the area map, then SEARCH. Pokémon of the ground need you on foot; for one of the water you '
         f'must be surfing ({say("TXT_NEED_SURF")}).',
         f'2. The DexNav hides it {spot_near} to {spot_max} steps away ({spot_min} when there is no room further out), in '
         'a spot you can walk (or surf) to: shaking tall grass, a dust cloud on a cave floor or in the desert sand, or '
         f'rippling water. {say("TXT_ACTIVE")} When there is nowhere to put it: {say("TXT_NOT_FOUND")}',
         '3. Walk onto the spot: a wild battle with that Pokémon starts, with the normal wild battle music. Catch it or '
         'knock it out.\n',
         '- While it hides, no other wild Pokémon jump out at you.',
         f'- If you leave the area, or someone walks onto the spot, it is gone ({say("TXT_LOST")}).',
         '- The DexNav also works as a page of the PokéNav: its DEXNAV button. There the D-pad moves a cursor over the '
         'Pokémon and A picks one; starting a search closes the PokéNav.\n',
         '## Sneaking\n',
         f'Walk to it. If you run (holding B) or ride your Bicycle within {flee} steps of the spot, the Pokémon runs off '
         f'({say("TXT_FLED")}) and your chain ends.\n',
         '## Search levels\n',
         f'Every species has its own search level. It goes up by 1 each time you catch or knock out a Pokémon of that '
         f'species found with the DexNav (the tutorial\'s counts too), up to {lv_max}. The Found and Hidden screens show '
         'it. A higher search level shows more on the Hidden screen ([above](#the-screen)) and gives better bonuses. '
         'Saves from older versions start every species at 0.\n',
         '## Bonuses\n',
         'Each Pokémon the DexNav finds can get these, by the search level of its species:\n',
         '| Search level | Perfect IVs | Hidden ability | Egg move | Rare held item |', '|---|---|---|---|---|'] + rows + [
         '',
         '- **Perfect IVs:** that many of its six stats get the highest IV, 31 (different stats, at random).',
         '- **Hidden ability:** its hidden ability (from Black 2\'s data), only for a Pokémon whose hidden ability '
         'differs from its usual ones. Otherwise it has one of its usual abilities.',
         '- **Egg move:** one of its egg moves (for an evolved Pokémon, its first stage\'s), in its first empty move '
         'slot, or in place of its first move.',
         '- **Rare held item:** it holds its rarer wild item, the one wild Pokémon of its kind hold 5% of the time (only '
         'Pokémon that have one).\n',
         '## Chains and shiny Pokémon\n',
         f'Your chain goes up by 1 each time you catch or knock out a DexNav Pokémon of the same species as the last one '
         f'(up to {chain_max}). It goes back to 0 when you search for another species, when the Pokémon runs off or its '
         'spot is lost, and when you run from the battle or lose it. The DexNav doesn\'t show the chain: count it '
         'yourself.\n',
         f'Every wild Pokémon has a 1 in {odds:,} chance to be shiny. A DexNav Pokémon gets extra tries at that chance: '
         f'one for every {per_chain} in your chain ({cap} from a chain of {cap_at} on), one for every {per_level} search '
         f'levels of its species, and {bonus} more when your chain is exactly {bonus_a} or {bonus_b}. Some examples:\n',
         '| Chain | ' + ' | '.join(f'Search level {lv}' for lv in levels) + ' |', '|---|' + '---|' * len(levels)]
    L += [f'| {ch} | ' + ' | '.join(one_in(rolls(lv, ch)) for lv in levels) + ' |' for ch in chains]
    L += ['', '## Good to know\n',
          '- It works with saves from older versions: talk to Prof. Birch to get it ([above](#getting-it)).',
          '- In the Safari Zone a search costs only the steps you walk, and the Pokémon it finds follow the Safari Zone\'s '
          'rules (' + ', '.join(f'[{VNAME[v]}](wild-pokemon-{v}.md#safari-zone-rules)' for v in version.VERSIONS) + ').',
          '- Searching never changes the normal wild Pokémon: walking in the grass without a search is as before, and '
          'the [wild Pokémon pages](README.md) show the same tables.', '']
    return '\n'.join(L)


# ---- post-game --------------------------------------------------------------------------------------------------------
FS = os.path.join(ROOT, 'src', 'field_scripts')

def _src(rel):
    """A field script source as this version builds it: a numbered script file's version overlay
    (src/field_scripts/<version>/NNNN_*.s) replaces the shared one; scene files are read by the path given (a version's
    scene file under scenes/<version>/ is included by the shared one, it does not replace it)."""
    p = os.path.join(FS, rel)
    if not rel.startswith('scenes/'): p = version.overlay_file(p)
    return open(p, encoding='utf-8').read()

def _num(rel, pattern):
    """The first group of `pattern` in a script source as a number. The guide states it, so a script that no longer
    has it stops the generator instead of leaving the page wrong."""
    m = re.search(pattern, _src(rel))
    if not m: raise SystemExit(f'gen_docs: {rel} has no {pattern!r} any more: update postgame_page')
    return int(m.group(1), 0)

def _define(rel, name):
    return _num(rel, rf'#define\s+{name}\s+(0x[0-9A-Fa-f]+|\d+)\b')

def _need(rel, *texts):
    """The conditions the guide states, as the script has them (stops when one is gone)."""
    s = _src(rel)
    for t in texts:
        if t not in s: raise SystemExit(f'gen_docs: {rel} no longer has {t!r}: update postgame_page')

def _script_text(name):
    """A script message file's lines (src/text/script, the version's overlay) as one line of plain text each. Braille is
    shown as the text it spells (Black 2 has no braille font), so the guide can quote it."""
    p = version.overlay_file(os.path.join(ROOT, 'src', 'text', 'script', name))
    return [re.sub(r' +', ' ', re.sub(r'\{be0[01]\}', ' ', s).replace('\\n', ' ')).strip()
            for s in open(p, encoding='utf-8').read().split('\n')]

BADGES = ('Stone', 'Knuckle', 'Dynamo', 'Heat', 'Balance', 'Feather', 'Mind', 'Rain')   # TrainerCardHasBadge's numbers

def _key_item(c):
    """A Hoenn key item constant -> the Black 2 item it is (src/include/hoenn_key_items.h)."""
    m = re.search(rf'#define\s+{c}\s+(ITEM_\w+)', open(os.path.join(ROOT, 'src', 'include', 'hoenn_key_items.h')).read())
    return m.group(1) if m else c

def _version_define(name):
    """A species #define of src/include/hoenn_version.inc as this version's scripts assemble it (its #ifdef HOENN_EMERALD
    / #elif defined(HOENN_RUBY) / #else blocks), e.g. SPECIES_KYOGRE_OR_GROUDON -> 'GROUDON' in Sapphire."""
    src = open(os.path.join(ROOT, 'src', 'include', 'hoenn_version.inc'), encoding='utf-8').read()
    m = re.search(r'\n#ifdef HOENN_EMERALD\n(.*?)\n#elif defined\(HOENN_RUBY\)\n(.*?)\n#else\n(.*?)\n#endif', src, re.S)
    if not m: raise SystemExit('gen_docs: hoenn_version.inc has other version blocks now: update _version_define')
    d = re.search(rf'#define\s+{name}\s+SPECIES_(\w+)', m.group(1 if version.is_emerald() else 2 if version.is_ruby() else 3))
    if not d: raise SystemExit(f'gen_docs: hoenn_version.inc has no {name} for {version.NAME}: update postgame_page')
    return d.group(1)

def _join(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]

def _or(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' or ' + xs[-1]

def _routes(maps):
    """['Route110', 'Route111', 'Route117', ...] -> 'Routes 110-111 and 117-134'."""
    runs = []
    for n in sorted(int(re.fullmatch(r'Route(\d+)', m).group(1)) for m in maps):
        if runs and n == runs[-1][1] + 1: runs[-1][1] = n
        else: runs.append([n, n])
    parts = [f'{a}' if a == b else f'{a}-{b}' for a, b in runs]
    return ('Route ' if len(parts) == 1 and '-' not in parts[0] else 'Routes ') + _join(parts)

def _outside(room):
    """The outdoor map whose door leads into `room` (the version's decomp map.json warps), e.g. DesertRuins -> Route111."""
    maps = glob.glob(os.path.join(version.DECOMP, 'data', 'maps', '*', 'map.json'))
    ids = {json.load(open(p))['id']: os.path.basename(os.path.dirname(p)) for p in maps}
    target = next(i for i, n in ids.items() if n == room)
    for p in maps:
        d = json.load(open(p))
        if any(w.get('dest_map') == target for w in d.get('warp_events') or []) and d.get('map_type') != 'MAP_TYPE_INDOOR':
            name = os.path.basename(os.path.dirname(p))
            if name.startswith('Route'): return name
    raise SystemExit(f'gen_docs: no route door into {room}')

def _party(t, names):
    return ', '.join(f'{names.species(p["species"])} {p["level"]}' for p in t['party'])

def _levels(t):
    lv = sorted(p['level'] for p in t['party'])
    return f'{lv[0]}' if lv[0] == lv[-1] else f'{lv[0]}-{lv[-1]}'

def _class_names():
    """pokeemerald's trainer class names ("{PKMN} BREEDER" -> "Pokémon Breeder")."""
    src = open(os.path.join(ROOT, 'external', 'pokeemerald', 'src', 'data', 'text', 'trainer_class_names.h')).read()
    def nice(s):
        words = []
        for w in s.split():
            w = {'{PKMN}': 'Pokémon', 'AND': 'and'}.get(w, w.capitalize())
            words.append(w)
        return ' '.join(words)
    return {k: nice(v) for k, v in re.findall(r'\[TRAINER_CLASS_(\w+)\]\s*=\s*_\("([^"]*)"\)', src)}

def _rematch_pages(names):
    """Emerald's rematch tables (data/emerald/hoenn_rematch.json, the parties as built: levels on the curve)."""
    d = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_rematch.json')))
    data = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers']
    by_id = {}
    for t in data.values():
        if 'emerald_trainer' in t: by_id.setdefault(t['b2_id'], t)
    slots = {s['slot']: s for s in d['slots']}
    def team(slot):
        out = []
        for s in [slots[slot]] + ([slots[slot + 1]] if slots[slot].get('half') else []):
            mons = ', '.join(f'{names.species(m.split(" Lv")[0])} {m.split(" Lv")[1]}' for m in s['party'])
            out.append(f'{s["half"]}: {mons}' if s.get('half') else mons)
        return '; '.join(out)
    def top(slot):
        return max(int(m.split(' Lv')[1]) for m in slots[slot]['party'] + (slots[slot + 1]['party'] if slots[slot].get('half') else []))
    leaders, wally, route = [], [], []
    cls = _class_names()
    m = re.search(r'if \(b < (\d+)\) return -1;', open(os.path.join(HERE, 'patches', 'emerald_rematch.c')).read())
    if not m: raise SystemExit('gen_docs: emerald_rematch.c has no badge rule any more: update postgame_page')
    if 'case RM_BEATEN:' not in open(os.path.join(HERE, 'patches', 'emerald_rematch.c')).read():
        raise SystemExit('gen_docs: emerald_rematch.c no longer counts a first battle as that day\'s: update postgame_page')
    badges = int(m.group(1))
    for r in d['rows']:
        t = by_id[r['b2_id']]
        if 1 <= r['gym'] <= 8:
            where = ', '.join(sorted({place(m) for m in t.get('maps') or []}))
            name = t['name'] + (' and ' + by_id[r['partner']]['name'] if r['partner'] else '')
            leaders.append((r['gym'], name, where, [team(x['slot']) for x in r['tiers']]))
        elif r['gym'] == 9:
            wally = [team(x['slot']) for x in r['tiers']]
        else:
            tiers = {x['tier']: x['slot'] for x in r['tiers']}
            lv, last = [], '-'
            for k in range(2, 6):                # the tier fought at 5-8 badges (a missing tier: the one before it)
                if k in tiers: last = f'{top(tiers[k])}'
                lv.append(last)
            dbl = any(x['double'] for x in r['tiers'])
            who = f'{cls.get(t["emerald_class"], _title(t["emerald_class"], ""))} {t["name"]}' + (' (double)' if dbl else '')
            route.append((place_key(t['maps'][0]), who, place(t['maps'][0]), lv))
    leaders.sort()
    route.sort()
    return badges, leaders, wally, [r[1:] for r in route]

def deep_sea_line(names, areas):
    """Huntail and Gorebyss: Clamperl with a Deep Sea item from the Bag (data/trade_evos.json), Capt. Stern's Scanner trade
    for one of the two, wild Pokémon holding the other in their 5% item slot (Black 2's personal data a/0/1/6 +0xE of the
    build base, evo_items_check.py wild_held's rule) as this version's wild tables have them. The DexNav's part only
    where the decomp has its C (has_our_c)."""
    evos = json.load(open(os.path.join(ROOT, 'data', 'trade_evos.json')))['evolutions'].get('SPECIES_CLAMPERL') or []
    if {tuple(e) for e in evos} != {('EVO_METHOD_ITEM', 'ITEM_DEEP_SEA_TOOTH', 'SPECIES_HUNTAIL'),
                                     ('EVO_METHOD_ITEM', 'ITEM_DEEP_SEA_SCALE', 'SPECIES_GOREBYSS')}:
        raise SystemExit('gen_docs: Clamperl evolves another way now: update deep_sea_line')
    _need('scenes/SlateportCity_Harbor_Ch6.inc', 'h_checkitem ITEM_SCANNER, 1, HLIB_TMP', 'h_giveitem ITEM_DEEP_SEA_TOOTH',
          'h_giveitem ITEM_DEEP_SEA_SCALE', 'h_removeitem ITEM_SCANNER, 1, HLIB_TMP')
    _need('1192_room_SlateportCity_Harbor.s', 'h_goto_if_badge 7, Ch6_HB_SternScanner')
    import narcio
    recs = narcio.load(os.path.join(b2decomp.BASE, 'build', 'b2_us', 'files'), 16)   # (the build base, as the TM pages' arm9)
    targets = {names.species('HUNTAIL'), names.species('GOREBYSS')}
    wild = collections.defaultdict(set)              # species name -> how it is met (the wild page's sections)
    for maps, sec, after in areas:
        for title, rows in list(sec) + list(after.items()):
            how = ('fishing' if title.endswith(' Rod') else 'Rock Smash' if title == 'Rock Smash' else 'on foot'
                   if title == 'Grass and cave floor' else 'underwater' if maps[0].startswith('Underwater') else 'surfing')
            for r in rows: wild[r[0]].add(how)
    parts, findable = [], []
    for item in ('ITEM_DEEP_SEA_TOOTH', 'ITEM_DEEP_SEA_SCALE'):
        iid = names.items_id[item]
        mons = [names.species_t[i] for i, rec in enumerate(recs[:len(names.species_t)])
                if len(rec) >= 0x10 and struct.unpack_from('<H', rec, 0xE)[0] == iid]
        mons = [m for m in mons if m in wild and m not in targets]
        if not mons: raise SystemExit(f'gen_docs: no wild Pokémon holds the {item} in {version.NAME}: update deep_sea_line')
        hows = sorted({h for m in mons for h in wild[m]})
        parts.append(f'the {names.item(item)} {_join(mons)} ({_join(hows)})')
        findable += [m for m in mons if wild[m] & {'on foot', 'surfing'}]
    line = (f'{names.species("CLAMPERL")} evolves into {names.species("HUNTAIL")} when you use a '
            f'{names.item("ITEM_DEEP_SEA_TOOTH")} from the Bag, and into {names.species("GOREBYSS")} with a '
            f'{names.item("ITEM_DEEP_SEA_SCALE")} ([trade evolutions](evolutions.md)). Capt. Stern at Slateport City\'s '
            'harbor gives you one of the two for the Scanner. Wild Pokémon hold the other one 5% of the time: '
            f'{_join(parts)}. Catch one that holds it.')
    if findable:
        line += f' The [DexNav](dexnav.md)\'s rare-held-item bonus raises that chance for {_join(findable)}.'
    elif has_our_c():
        c, rel = _decomp_c('src/hoennb2/resident/dexnav.c'), 'src/hoennb2/resident/dexnav.c'
        for t in ('enc->grass, 12, DEXNAV_GROUP_LAND', 'enc->surf, 5, DEXNAV_GROUP_WATER',
                  'if (mon->group == DEXNAV_GROUP_WATER && ExState(field) != FLD_PLAYER_EXSTATE_SURF) {'):
            if t not in c: raise SystemExit(f'gen_docs: {rel} no longer has {t!r}: update deep_sea_line')
        if 'FLD_PLAYER_EXSTATE_DIVE = ' not in _decomp_c('include/field/player_state.h'):
            raise SystemExit('gen_docs: diving is no longer its own player state: update deep_sea_line')
        if len(re.findall(r'\bAddSlots\(list, ', c)) != 2 or 'ENCTYPE_FISHING' in c:
            raise SystemExit(f'gen_docs: {rel} lists fished Pokémon now: update deep_sea_line')
        line += (' The DexNav can\'t help with these: it doesn\'t list fished Pokémon, and it searches the water only '
                 'while you surf, not while you dive.')
    return line

def postgame_page(names):
    E = version.is_emerald()
    import roamers
    sp = names.species
    item = lambda c: names.item(_key_item(c))
    EON, MAP, AURORA, MYSTIC = item('ITEM_EON_TICKET'), item('ITEM_OLD_SEA_MAP'), item('ITEM_AURORA_TICKET'), item('ITEM_MYSTIC_TICKET')
    SS = names.item('ITEM_SS_TICKET')
    lati_roam, lati_island = sp(version.TABLE['roamer']), sp(version.TABLE['island'])
    colour = {'LATIAS': 'red', 'LATIOS': 'blue'}[version.TABLE['roamer']]
    if E: lati_island_txt = f'{sp("LATIOS")} or {sp("LATIAS")} (the one that is not roaming)'
    else: lati_island_txt = lati_island

    # the scripts' own conditions and levels
    _need('scenes/players_house_1f_events.inc', 'FLAG_SYS_GAME_CLEAR', 'FLAG_RECEIVED_SS_TICKET', 'ITEM_EON_TICKET')
    _need('scenes/SlateportCity_Harbor_Events.inc', 'FLAG_SYS_GAME_CLEAR', 'ITEM_OLD_SEA_MAP')
    _need('scenes/FallarborTown_House1_Events.inc', 'FLAG_SYS_GAME_CLEAR', 'ITEM_AURORA_TICKET')
    _need('scenes/Route114_LanettesHouse_Events.inc', 'FLAG_SYS_GAME_CLEAR', 'ITEM_MYSTIC_TICKET')
    _need('scenes/LilycoveCity_Harbor_Ch13.inc', 'FLAG_ENCOUNTERED_LATIAS_OR_LATIOS', 'L_EV_LH_EventTickets')
    _need('scenes/SouthernIsland_Interior.inc', 'h_setflag FLAG_ENCOUNTERED_LATIAS_OR_LATIOS')
    if E:                   # Emerald's Eon Ticket (one of the harbor's event tickets) and its Lati rule (postgame_fix)
        _need('scenes/LilycoveCity_Harbor_Events.inc', 'h_goto_if_set FLAG_SHOWN_EON_TICKET', 'L_EV_LH_EonFirstTime',
              'L_EV_LH_GoToSouthernIsland', 'ListMenuAdd EV_LH_T + 10, 65535, 2')
        _need('scenes/LilycoveCity_Harbor_Ch13.inc', 'ListMenuAdd EV_LH_T + 10, 65535, 7')
        _need('scenes/emerald/SouthernIsland_Interior.inc', 'h_goto_if_set SII_TEMP_2', 'h_goto_if_set FLAG_DEFEATED_LATIAS_OR_LATIOS',
              'h_goto_if_set FLAG_CAUGHT_LATIAS_OR_LATIOS', 'FLAG_CAUGHT_LATIAS_OR_LATIOS, FLAG_DEFEATED_LATIAS_OR_LATIOS')
        _need('0114_room_EverGrandeCity_HallOfFame.s', 'h_clearflag FLAG_DEFEATED_LATIAS_OR_LATIOS')
    _need('scenes/BirchLab_Postgame.inc', 'PokeDexGiveNational', 'Sub_PG_StartBeastsAndBirds')
    _need('scenes/PetalburgWoods_Postgame.inc', 'PokeDexHaveNational', 'FLAG_DEFEATED_CELEBI')
    _need('scenes/MossdeepCity_SpaceCenter_1F_Postgame.inc', 'FLAG_SYS_GAME_CLEAR', 'h_getpartysize')
    _need('scenes/PetalburgCity_Gym_Postgame.inc', 'FLAG_SYS_GAME_CLEAR', 'FLAG_RECEIVED_ENIGMA_BERRY', 'h_checkitem ITEM_ENIGMA_BERRY')
    _need('scenes/Route103_AlteringCave.inc', 'FLAG_SYS_GAME_CLEAR', 'FLAG_DAILY_ALTERING_CAVE', 'FLAG_LANDMARK_ALTERING_CAVE')
    _need('0114_room_EverGrandeCity_HallOfFame.s', 'HF_ResetEliteFour', 'FLAG_HIDE_WALLY_DEFEATED_VICTORY_ROAD', 'FLAG_HIDE_LILYCOVE_MOTEL_PEOPLE')
    _need('0114_room_EverGrandeCity_HallOfFame.s', 'h_clearflag FLAG_DEFEATED_MEW', 'h_clearflag FLAG_DEFEATED_DEOXYS',
          'h_clearflag FLAG_DEFEATED_LUGIA', 'h_clearflag FLAG_DEFEATED_HO_OH', 'h_clearflag FLAG_DEFEATED_CELEBI')
    hof_shared = _src('0114_room_EverGrandeCity_HallOfFame.s').split('HF_SetGameClearFlags:', 1)[1].split('#ifdef HOENN_EMERALD', 1)[0]
    if 'h_clearflag FLAG_DEFEATED_MEW' not in hof_shared:   # (every version since postgame_fix, not Emerald's block only)
        raise SystemExit('gen_docs: 0114 no longer resets the event legendaries in every version: update postgame_page')
    lv_lati_island = _define('scenes/SouthernIsland_Interior.inc', 'SII_LATIOS_LEVEL')
    lv = {k: _define('scenes/events_lib.inc', f'EV_{k}_LEVEL') for k in ('MEW', 'DEOXYS', 'LUGIA', 'HO_OH')}
    lv_jirachi = _define('scenes/postgame_lib.inc', 'PG_JIRACHI_LEVEL')
    lv_celebi = _define('scenes/postgame_lib.inc', 'PG_CELEBI_LEVEL')
    lv_beldum = _num('scenes/MossdeepCity_StevensHouse_Ch13.inc', r'PokePartyAdd \w+, SPECIES_BELDUM, 0, (\d+)')
    lv_regi = _level_in('scenes/ch12_lib.inc', re.search(r'CallWildBattle \\species, (\w+), 1', _src('scenes/ch12_lib.inc')).group(1))
    mirage = _define('scenes/Route130.inc', 'MI_MASK') + 1
    steps = [int(x) for x in re.findall(r'L_BE_Max\d+:\s*\n\s*h_goto_if_gt BE_STEPS, (\d+)', _src('scenes/BirthIsland_Exterior_rock.inc'))]
    # Birth Island's walkthrough (played in the emulator 2026-11-05 on the step-count fix 93bee0e): the side to talk from
    # after each jump. Checked here against the triangle's places and step limits: each walk is exactly the limit.
    rock = [(int(x), int(z)) for x, z in re.findall(r'ActorSetGPos BE_ROCK, (\d+) \+ EV_BIRTH_OX, BE_GY, (\d+) \+ EV_BIRTH_OZ',
                                                    _src('scenes/BirthIsland_Exterior_rock.inc'))]
    be_sides = ('above', 'below', 'above', 'right', 'left', 'above', 'right', 'left', 'above', 'below')
    _need('scenes/BirthIsland_Exterior.inc', 'PedometerEnd', 'PedometerStart', 'h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 10, L_BE_Solved',
          'h_setvar VAR_DEOXYS_ROCK_LEVEL, 0')
    _need('scenes/BirthIsland_Exterior_rock.inc', 'VMJump L_BE_Progress                // (level 0: no limit)')
    if len(rock) != len(steps) + 1 or len(be_sides) != len(steps):
        raise SystemExit('gen_docs: Birth Island has other places or step limits now: update postgame_page')
    off = {'above': (0, -1), 'below': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
    at = (rock[0][0], rock[0][1] + 1)                  # the first talk: from below, the side you come up from the dock
    for i, side in enumerate(be_sides):
        nxt = (rock[i + 1][0] + off[side][0], rock[i + 1][1] + off[side][1])
        if abs(nxt[0] - at[0]) + abs(nxt[1] - at[1]) != steps[i]:
            raise SystemExit(f'gen_docs: Birth Island jump {i + 1}: the walkthrough no longer fits its step limit: update postgame_page')
        at = nxt
    ev_objs = json.load(open(os.path.join(ROOT, 'data', 'story', 'events.json'), encoding='utf-8'))['objects']
    tri = next(o for o in ev_objs if o.get('map') == 'BirthIsland_Exterior' and o.get('uid') == 101)
    mew = next(o for o in ev_objs if o.get('map') == 'FarawayIsland_Interior' and o.get('flag') == 'FLAG_HIDE_MEW')
    if tri.get('model') != 144 or mew.get('move') != 3:   # the white stone sphere for the triangle; Mew wanders (Black 2 move 3)
        raise SystemExit('gen_docs: Birth Island\'s triangle or Faraway Island\'s Mew changed: update postgame_page')
    _need('scenes/FarawayIsland_Interior.inc', 'FI_FindMew', 'Mv_FI_MewMoveAndHide')
    # Navel Rock: the fork's two ladders, the rooms each way, Ho-Oh's trigger on the summit path, Lugia talked to
    fork = _src('0532_room_NavelRock_Fork.s')
    nr_up_x = int(re.search(r'ladder up \((\d+),\d+\) -> NavelRock_Up1 ', fork).group(1))
    nr_down_x = int(re.search(r'ladder down \((\d+),\d+\) -> NavelRock_Down01 ', fork).group(1))
    nr_up = len([p for p in glob.glob(os.path.join(FS, '*_room_NavelRock_Up*.s')) if '_init' not in p])
    nr_down = len([p for p in glob.glob(os.path.join(FS, '*_room_NavelRock_Down*.s')) if '_init' not in p])
    _need('scenes/NavelRock_Top.inc', 'step trigger (12,10)')
    _need('0450_room_NavelRock_Bottom.s', 'object 1 (NavelRock_Bottom_EventScript_Lugia)')
    # Sky Pillar: the cracks drop a walker (not a rider) to the floor below; the Bike is allowed on every floor; on 4F the
    # two middle cracks of the top passage drop into 3F's closed-off part, whose stairs lead to 4F's corner with 5F's stairs
    for f in ('0330_room_SkyPillar_2F.s', '0334_room_SkyPillar_4F.s'):
        _need(f, 'cracked floor (', 'PlayerGetExState 0x8010')
    _need('0334_room_SkyPillar_4F.s', 'cracked floor (6,4) -> fall to SkyPillar_3F (6,4)', 'cracked floor (7,4) -> fall to SkyPillar_3F (7,4)')
    sp_rooms = {z: version.load_json(os.path.join(ROOT, 'data', 'interiors', f'{z}.json')) for z in range(164, 169)}
    if not all(r.get('cycling') for r in sp_rooms.values()) \
            or not any(w['at'] == [7, 1] and w['to'] == [167, 1] for w in sp_rooms[166]['warps']) \
            or not any(w['at'] == [3, 1] and w['to'] == [168, 0] for w in sp_rooms[167]['warps']):
        raise SystemExit('gen_docs: Sky Pillar\'s Bike rule or its 3F/4F stairs changed: update postgame_page')
    # the Sealed Chamber and the three Regi chambers (the version's puzzles: Emerald = pokeemerald's)
    _need('0430_room_SealedChamber_OuterRoom.s', 'step trigger (9..11,3): Dig', 'h_dig_user CH12_DIG, L_SO_NoDig')
    _need('scenes/ch12_lib.inc', '.macro h_dig_user move, fail', 'Dig: no badge, no machine')
    m = re.search(r'#ifdef HOENN_EMERALD[^\n]*\n#define SI_FIRST_SPECIES SPECIES_(\w+)[^\n]*\n#define SI_LAST_SPECIES SPECIES_(\w+)'
                  r'[^\n]*\n#else[^\n]*\n#define SI_FIRST_SPECIES SPECIES_(\w+)[^\n]*\n#define SI_LAST_SPECIES SPECIES_(\w+)',
                  _src('0408_room_SealedChamber_InnerRoom.s'))
    if not m: raise SystemExit('gen_docs: 0408 has no Relicanth / Wailord order any more: update postgame_page')
    si_first, si_last = (m.group(1), m.group(2)) if E else (m.group(3), m.group(4))
    si_braille = _script_text('0263_room_SealedChamber_InnerRoom.txt')[0]
    if sp(si_first) not in si_braille.split('.')[0]:
        raise SystemExit('gen_docs: the Sealed Chamber\'s braille and its party check disagree: update postgame_page')
    sc_go_up = _script_text('0281_room_Underwater_SealedChamber.txt')[0]
    sc_dig = _script_text('0274_room_SealedChamber_OuterRoom.txt')[10]
    dive_src = open(os.path.join(HERE, 'patches', 'dive.py'), encoding='utf-8').read()
    if "('Underwater_SealedChamber', 'surface@12,44', 'SealedChamber_OuterRoom'" not in dive_src \
            or "('Underwater_SealedChamber', 'surface', 'Route134'" not in dive_src \
            or '10011/10012 surface when the player is diving' not in open(os.path.join(HERE, 'patches', 'hm_free.py'), encoding='utf-8').read():
        raise SystemExit('gen_docs: surfacing into the Sealed Chamber changed: update postgame_page')
    def braille_move(rel):
        """A chamber's field-move spot: (move, item, badge, spot tiles x0, x1, y, braille tile x, y)."""
        s = _src(rel)
        t = re.search(r'step trigger \((\d+)(?:\.\.(\d+))?,(\d+)\): ([A-Z][a-z]+(?: [A-Z][a-z]+)?)', s)
        u = re.search(r'h_field_move_user (ITEM_\w+), (\d+), \w+, L_', s)
        b = re.search(r'ScriptEntry Story_\w+_Braille +// \d+: braille \((\d+),(\d+)\)', s)
        if not (t and u and b): raise SystemExit(f'gen_docs: {rel}: its braille spot changed: update postgame_page')
        x0 = int(t.group(1))
        return (t.group(4), names.item(u.group(1)), BADGES[int(u.group(2))], x0, int(t.group(2) or x0), int(t.group(3)),
                int(b.group(1)), int(b.group(2)))
    regi_dr = braille_move('0232_room_DesertRuins.s')
    regi_at = braille_move('0188_room_AncientTomb.s')
    if E:
        ic = _src('0254_room_IslandCave.s')
        _need('0254_room_IslandCave.s', 'L_IC_CheckLap', 'IC_OffPath', 'L_IC_ClearIfFailed')
        ic_lap = len(re.findall(r'^IC_Path\d+:', ic, re.M))
    else:
        ic_wait = _num('0254_room_IslandCave.s', r'SystemMsg T_BRAILLE, 2[^\n]*\n\s*VMSleep (\d+)')
    br = {k: _script_text(f)[0] for k, f in (('dr', '0135_room_DesertRuins.txt'), ('ic', '0146_room_IslandCave.txt'),
                                              ('at', '0104_room_AncientTomb.txt'))}
    diploma = _src('0360_room_LilycoveCity_CoveLilyMotel_2F.s').split('Sub_MO2_CompletedHoennDex:', 1)[1]
    diploma = [int(x) for x in re.findall(r'PokeDexIsRegist 1, (\d+),', diploma)]
    roam = [(sp(s), roamers.scaled(l)) for s, l in roamers.ROAMERS]
    roam_routes = _routes(roamers.locations()[0])
    regis = []
    for f in ('0232_room_DesertRuins.s', '0254_room_IslandCave.s', '0188_room_AncientTomb.s'):
        s = re.search(r'h_regi_battle SPECIES_(\w+)', _src(f)).group(1)
        room = re.sub(r'^\d+_room_|\.s$', '', f)
        regis.append((sp(s), place(room), place(_outside(room))))
    if E:
        lv_ray = _define('scenes/emerald/em_ch10_lib.inc', 'EM_RAYQUAZA_LEVEL')
        lv_groudon = _define('0732_room_TerraCave_End.s', 'TCE_LEVEL')       # (Emerald-only script files: overlay_file)
        lv_kyogre = _define('0738_room_MarineCave_End.s', 'MCE_LEVEL')
        aw_steps = _define('scenes/emerald/abnormal_weather.inc', 'AW_STEPS')
        zones = version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps']
        aw = re.findall(r'\.set AW_ZONE_(\d+), (\d+)', _src('scenes/emerald/abnormal_weather.inc'))
        n_terra = _define('scenes/emerald/abnormal_weather.inc', 'AW_TERRA_SPOTS')
        def aw_routes(zs):
            return _routes(sorted({m for m, z in zones.items() if z.get('zone') in zs and re.fullmatch(r'Route\d+', m)}))
        terra_routes = aw_routes({int(z) for k, z in aw if int(k) <= n_terra})
        marine_routes = aw_routes({int(z) for k, z in aw if int(k) > n_terra})
        johto = re.findall(r'emj_ball SPECIES_(\w+)', _src('scenes/emerald/BirchLab_JohtoStarters.inc'))
        lv_johto = _num('scenes/emerald/BirchLab_JohtoStarters.inc', r'PokePartyAdd EMJ_SLOT, \\species, 0, (\d+)')
        johto_need = _num('scenes/emerald/BirchLab_JohtoStarters.inc', r'h_goto_if_lt C11_DEXCOUNT, (\d+), L_EMJ_NotReady')
        hoenn_dex = len(re.findall(r'PokeDexIsRegist C11_DEXKIND', _src('scenes/ch11_dexcount.inc')))
        _need('1086_room_TrainerHill_Entrance.s', 'L_TE_Closed')
        _need('0754_room_MeteorFalls_StevensCave.s', 'FLAG_DEFEATED_METEOR_FALLS_STEVEN')
        rm_badges, rm_leaders, rm_wally, rm_route = _rematch_pages(names)
        data = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers']
        steven = data['TRAINER_STEVEN_EMERALD']
        # the abnormal weather: Castform first, the report, two spots per route, the caves' way in and Kyogre/Groudon's step
        _need('1128_room_Route119_WeatherInstitute_2F.s', 'h_goto_if_set FLAG_RECEIVED_CASTFORM, L_WI2_AlreadyGave',
              'h_goto_if_set FLAG_SYS_GAME_CLEAR, L_WI2_TryStartAbnormalWeather', 'h_goto_if_set WI2_FLAG_TEMP_2, L_WI2_AwReport')
        per_route = collections.Counter(z for _, z in aw)
        aw_two = len(set(per_route.values())) == 1 and next(iter(per_route.values())) == 2
        _need('0732_room_TerraCave_End.s', 'trigger (17,26)'); _need('0738_room_MarineCave_End.s', 'trigger (9,26)')
        _need('scenes/emerald/abnormal_weather.inc', 'Over while in Terra / Marine Cave: the end is pending')
        if "('Underwater_MarineCave', 'surface', 'MarineCave_Entrance'" not in dive_src:
            raise SystemExit('gen_docs: the Marine Cave\'s surfacing changed: update postgame_page')
        # Steven's Cave: the first room's top-left corner, reached by the ladder up from B1F (the B1F rooms from the
        # waterfall room above the first room)
        mf = {z: version.load_json(os.path.join(ROOT, 'data', 'interiors', f'{z}.json'))['warps'] for z in (128, 129, 130)}
        if not (any(w['at'] == [10, 3] and w['to'][0] == 129 for w in mf[128]) and any(w['to'][0] == 130 for w in mf[129])
                and any(w['at'] == [3, 23] and w['to'] == [128, 3] for w in mf[130])):
            raise SystemExit('gen_docs: Meteor Falls\' way to Steven\'s Cave changed: update postgame_page')
        _need('0754_room_MeteorFalls_StevensCave.s', 'FLAG_DEFEATED_METEOR_FALLS_STEVEN')
        # the Desert Underpass (the tunnel opens after the game; the fossil only after the Mirage Tower's), the Safari
        # workers, Emerald's Sky Pillar after Sootopolis
        _need('1116_room_Route114_FossilManiacsTunnel.s', 'h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_FMT_InitDone')
        _need('0750_room_DesertUnderpass.s', 'FLAG_HIDE_DESERT_UNDERPASS_FOSSIL')
        _need('scenes/emerald/Route111_Mirage.inc', 'h_clearflag FLAG_HIDE_DESERT_UNDERPASS_FOSSIL')
        e13 = json.load(open(os.path.join(ROOT, 'data', 'story', 'emerald', 'e_ch13.json'), encoding='utf-8'))['objects']
        if sum(1 for o in e13 if o.get('map') == 'SafariZone_Southeast' and o.get('flag') == 'FLAG_HIDE_SAFARI_ZONE_SOUTH_CONSTRUCTION_WORKERS') != 2:
            raise SystemExit('gen_docs: the Safari Zone\'s two workers moved: update postgame_page')
        _need('0334_room_SkyPillar_4F.s', 'h_goto_if_ge VAR_SKY_PILLAR_STATE, 2, L_SPF_Cracked')
        _need('scenes/emerald/SootopolisCity.inc', 'h_setvar VAR_SKY_PILLAR_STATE, 3')
        _need('scenes/SkyPillar_Top.inc', 'L_SPT_Ran:')
    else:
        lv_ray = _define('scenes/SkyPillar_Top.inc', 'SP_RAYQUAZA_LEVEL')
        lv_legend = _define('0206_room_CaveOfOrigin_B4F.s', 'B4_KYOGRE_LEVEL')
        data = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers']
    wally = data['TRAINER_WALLY_3']
    enc = version.load_json(os.path.join(ROOT, 'data', 'hoenn_encounters.json'))
    files = {int(os.path.basename(p)[:4]): p for p in version.overlay(os.path.join(ROOT, 'src', 'encounters'), '*.s')}
    def grass(m):
        return combine(parse_encounters(files[enc[m]])['GrassEncounters'], GRASS, names)
    altering = [grass(m) for m in ['AlteringCave'] + [f'AlteringCave_{i}' for i in range(2, 10) if f'AlteringCave_{i}' in enc]]
    if E:   # the Safari Zone's new areas: their own tables, played by part zones (data/emerald/hoenn_weather.json "wild")
        wparts = version.load_json(os.path.join(ROOT, 'data', 'hoenn_weather.json'))['parts']
        smash = rock_smash_tables()
        safari_new = []                  # [(area, [(how, species ...)])]
        for m in ('SafariZone_Northeast_Emerald', 'SafariZone_Southeast_Emerald'):
            if not any(v.get('wild') == m for v in wparts.values()) or m not in enc:
                raise SystemExit(f'gen_docs: {m} has no wild table of its own any more: update postgame_page')
            t = parse_encounters(files[enc[m]])
            how = []
            for title, secs in (('grass', ('GrassEncounters',)), ('surfing', ('SurfEncounters',)),
                                ('fishing', ('RipplingFishingEncounters', 'FishingEncounters'))):
                mons = list(dict.fromkeys(names.species(s) for sec in secs for s, _, _ in t.get(sec) or []))
                if mons: how.append((title, mons))
            if smash.get(m): how.append(('Rock Smash', list(dict.fromkeys(names.species(s) for s, _, _ in smash[m]))))
            safari_new.append((m, how))
    wynaut = grass('Route130')
    tidal_to = 'the Battle Frontier' if E else 'the Battle Tower island'
    # completing the Pokédex (postgame_dex 2026-11-09; notes/POSTGAME.md "Post-game dex completion"): the other versions'
    # wild Pokémon (the wild pages' tables after the Champion), Birch's two starters, the legendaries back after a Hall of
    # Fame, Sapphire / Ruby's other weather legend in Seafloor Cavern Room 9 and the fossil not taken
    areas_all = wild_areas(names)
    pg_new = postgame_new(areas_all)
    deep_sea = deep_sea_line(names, areas_all)
    if not pg_new: raise SystemExit('gen_docs: no post-game wild Pokémon any more: update postgame_page')
    _need('0792_birch_lab.s', 'VMCall PG_LabStartersDue', 'h_goto_if_eq HLIB_TMP, 1, PG_LabStarters')
    _need('scenes/BirchLab_Postgame.inc', 'h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_PGS_DueDone', 'L_PGS_Full:',
          'h_goto_if_eq VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 1, L_PGS_DueDone', 'BoxAdd PGS_TMP, PGS_SPECIES, 0, 5',
          'h_goto_if_lt VAR_BIRCH_OTHER_STARTERS, 2, L_PGS_Give')
    lv_starters = _num('scenes/BirchLab_Postgame.inc', r'PokePartyAdd PGS_SLOT, PGS_SPECIES, 0, (\d+)')
    _need('0114_room_EverGrandeCity_HallOfFame.s', 'VMCall HF_ResetLostLegends', '#include "scenes/postgame_legends.inc"')
    _need('scenes/postgame_legends.inc', 'PokeDexIsRegist 1, \\species, HFL_TMP', 'hfl_reset SPECIES_REGIROCK, FLAG_HIDE_REGIROCK',
          'hfl_reset SPECIES_REGICE, FLAG_HIDE_REGICE', 'hfl_reset SPECIES_REGISTEEL, FLAG_HIDE_REGISTEEL')
    _need('scenes/ch12_lib.inc', 'FlagSet \\flag\n    CallWildBattle \\species, CH12_REGI_LEVEL, 1')   # (hidden before the battle)
    if E:
        _need('scenes/postgame_legends.inc', 'hfl_reset SPECIES_RAYQUAZA, FLAG_DEFEATED_RAYQUAZA',
              'hfl_reset SPECIES_KYOGRE, FLAG_DEFEATED_KYOGRE', 'hfl_reset SPECIES_GROUDON, FLAG_DEFEATED_GROUDON')
        _need('scenes/SkyPillar_Top.inc', 'h_setflag FLAG_DEFEATED_RAYQUAZA    // caught or knocked out')
        _need('scenes/emerald/abnormal_weather.inc', 'h_goto_if_set FLAG_DEFEATED_KYOGRE', 'h_goto_if_set FLAG_DEFEATED_GROUDON')
        _need('1128_room_Route119_WeatherInstitute_2F.s', 'h_goto_if_unset FLAG_DEFEATED_KYOGRE, L_WI2_AwStart',
              'h_goto_if_unset FLAG_DEFEATED_GROUDON, L_WI2_AwStart')
    else:
        _need('scenes/postgame_legends.inc', 'hfl_reset SPECIES_RAYQUAZA, FLAG_HIDE_RAYQUAZA',
              'hfl_reset SPECIES_LATIAS_OR_LATIOS, FLAG_ENCOUNTERED_LATIAS_OR_LATIOS',
              'h_clearflag FLAG_HIDE_LEGEND_MON_CAVE_OF_ORIGIN', 'h_clearflag FLAG_DEFEATED_OTHER_LEGEND')
        _need('0206_room_CaveOfOrigin_B4F.s', 'h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_B4_Again', 'L_B4_Again:')
        _need('scenes/LilycoveCity_Harbor_Ch13.inc', 'h_goto_if_set FLAG_ENCOUNTERED_LATIAS_OR_LATIOS, L_LH13_FerryUnavailable')
        r9 = 'scenes/SeafloorCavern_Room9_Postgame.inc'
        _need(r9, 'h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_PGR9_InitDone', 'h_goto_if_set FLAG_CAUGHT_OTHER_LEGEND, L_PGR9_InitDone',
              'h_goto_if_set FLAG_DEFEATED_OTHER_LEGEND, L_PGR9_InitDone', 'h_setflag FLAG_DEFEATED_OTHER_LEGEND',
              'CallWildBattle SPECIES_KYOGRE_OR_GROUDON, R9_OTHER_LEGEND_LEVEL, 1', 'h_setflag FLAG_CAUGHT_OTHER_LEGEND')
        _need('0380_room_SeafloorCavern_Room9.s', 'ScriptEntry PG_R9_OtherLegend')
        _need(r9, 'MapReplaceSetEvent R9_EVENT_OTHER_LOOK, 1, 1')          # (the room's look swaps after the Champion)
        lv_other = _define(r9, 'R9_OTHER_LEGEND_LEVEL')
        other = sp(_version_define('SPECIES_KYOGRE_OR_GROUDON'))
        if _version_define('SPECIES_KYOGRE_OR_GROUDON') == version.TABLE['legendary']:
            raise SystemExit('gen_docs: Room 9\'s post-game legend is the story\'s: update postgame_page')
        other_game = 'Ruby' if version.VERSION == 'sapphire' else 'Sapphire'
        _need('1128_room_Route119_WeatherInstitute_2F.s', 'h_goto_if_set FLAG_CAUGHT_OTHER_LEGEND, L_WI2_Rain',
              'h_goto_if_set FLAG_DEFEATED_OTHER_LEGEND, L_WI2_Rain', 'h_msgbox T_OtherLegendHint')
        hint = _script_text('0365_room_Route119_WeatherInstitute_2F.txt')[_define('1128_room_Route119_WeatherInstitute_2F.s', 'T_OtherLegendHint')]
        if 'Route 128...' not in hint: raise SystemExit('gen_docs: the Weather Institute\'s hint changed: update postgame_page')
        hint = hint.split('Route 128...', 1)[0] + 'Route 128...'
        if "('Underwater_SeafloorCavern', 'surface', 'SeafloorCavern_Entrance'" not in dive_src:
            raise SystemExit('gen_docs: surfacing into the Seafloor Cavern changed: update postgame_page')
        _need('scenes/Route111.inc', 'VMCall R111_PostgameFossil', 'h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_R111_PgfDone',
              'h_clearflag FLAG_HIDE_CLAW_FOSSIL       // the Root Fossil was taken', 'h_clearflag FLAG_HIDE_ROOT_FOSSIL',
              'L_R111_NoGoggles:')
        _need('scenes/RustboroCity_DevonCorp_2F_Fossil.inc', 'h_setvar VAR_FOSSIL_RESURRECTION_STATE, 0')

    # ---- at a glance
    glance = [(SS, 'Dad, at home in Littleroot', 'after the Hall of Fame', 'back-home-in-littleroot')]
    if E: glance.append((f'Roaming {sp("LATIAS")} or {sp("LATIOS")}', 'Mom\'s question at home', 'after the Hall of Fame', 'roaming-legendaries'))
    else: glance.append((f'Roaming {lati_roam}', 'the TV news at home', 'after the Hall of Fame', 'roaming-legendaries'))
    glance += [('National Pokédex', 'Prof. Birch\'s Lab, Littleroot', 'after the Hall of Fame', 'back-home-in-littleroot'),
               ('Roaming ' + _join(n for n, _ in roam[1:]), 'all over Hoenn', 'with the National Pokédex', 'roaming-legendaries'),
               (EON, 'Mom', f'after Dad gives you the {SS}', 'event-tickets-and-islands'),
               (MAP, 'Capt. Stern, Slateport City harbor', 'after the Hall of Fame', 'event-tickets-and-islands'),
               (AURORA, 'Prof. Cozmo, Fallarbor Town', 'after the Hall of Fame', 'event-tickets-and-islands'),
               (MYSTIC, 'Lanette, Route 114', 'after the Hall of Fame', 'event-tickets-and-islands'),
               (f'{sp("BELDUM")} (Lv {lv_beldum})', 'Steven\'s house, Mossdeep City', 'after the Hall of Fame', 'gifts'),
               (f'{sp("JIRACHI")} (Lv {lv_jirachi})', 'Mossdeep Space Center 1F', 'after the Hall of Fame', 'gifts'),
               (f'{sp("CELEBI")} (Lv {lv_celebi})', 'Petalburg Woods', 'with the National Pokédex', 'gifts'),
               (names.item('ITEM_ENIGMA_BERRY'), 'Dad, Petalburg City Gym', 'after the Hall of Fame', 'gifts'),
               (f'The two starters you didn\'t choose (Lv {lv_starters})', 'Prof. Birch\'s Lab, Littleroot',
                'after the Hall of Fame', _slug('The two starters you didn\'t choose')),
               ('The other versions\' wild Pokémon', 'routes and caves', 'after the Hall of Fame', 'completing-the-pokédex')]
    if not E:
        glance += [(f'{other} (Lv {lv_other})', 'Seafloor Cavern, Route 128', 'after the Hall of Fame',
                    _slug(f'{other} in the Seafloor Cavern')),
                   ('The fossil you didn\'t take', 'Route 111, the desert', 'after the Hall of Fame', _slug('The fossil you didn\'t take'))]
    if E: glance.append(('Johto starters', 'Prof. Birch\'s Lab', f'{johto_need} Hoenn Pokédex Pokémon caught', 'gifts'))
    glance += [('Diploma', 'Cove Lily Motel 2F, Lilycove City', 'all Hoenn Pokédex Pokémon caught', 'gifts'),
               ('Altering Cave', 'Route 103', 'after the Hall of Fame', 'altering-cave'),
               ('Mirage Island', 'Route 130', 'some days, any time in the game', 'mirage-island')]
    if E:
        glance += [('Steven\'s Cave', 'Meteor Falls', 'after the Hall of Fame', 'stevens-cave'),
                   (f'Terra Cave and Marine Cave ({sp("GROUDON")}, {sp("KYOGRE")})', 'Weather Institute, Route 119', 'after the Hall of Fame', 'terra-cave-and-marine-cave'),
                   ('Desert Underpass', 'Route 114', 'after the Hall of Fame', 'desert-underpass'),
                   ('Safari Zone, two new areas', 'Safari Zone', 'after the Hall of Fame', 'safari-zone')]
    else:
        glance.append((f'Sky Pillar ({sp("RAYQUAZA")})', 'Route 131', 'after the Hall of Fame', 'sky-pillar'))
    glance.append(('Wally', 'Victory Road 1F', 'after the Hall of Fame', 'battles-after-the-hall-of-fame'))
    if E:
        glance += [('Battle Frontier', 'the S.S. Tidal, from Slateport or Lilycove', 'after the Hall of Fame', 'battles-after-the-hall-of-fame'),
                   ('Trainer Hill', 'Route 111', 'after the Hall of Fame', 'battles-after-the-hall-of-fame'),
                   ('Gym Leader rematches', 'each Gym', 'after the Hall of Fame', 'rematches'),
                   ('Trainer rematches', 'the routes', f'with {rm_badges} badges', 'rematches')]
    else:
        glance.append(('Battle Tower and PWT', 'the S.S. Tidal, from Slateport or Lilycove', 'after the Hall of Fame', 'battles-after-the-hall-of-fame'))

    L = [HEADER, f'# After the Hall of Fame: {version.PUBLIC_NAME}\n',
         'What there is to do once you have entered the Hall of Fame: the event islands and their tickets, the roaming '
         'legendaries, gifts, new places and battles. Levels are the ones you meet in this game.\n',
         '## At a glance\n', '| What | Where | When |', '|---|---|---|']
    L += [f'| [{w}](#{a}) | {where} | {when} |' for w, where, when, a in glance]

    # ---- home
    beasts = _join(n for n, _ in roam[1:])
    L += ['', '## Back home in Littleroot\n', 'After the credits you wake up in your room.\n']
    if E:
        L += [f'1. Go downstairs. Dad is home and gives you the **{SS}**. Then Mom turns on the TV: a news flash about '
              'a Pokémon in flight. She asks you what colour the announcer said:',
              f'   - **Red**: {sp("LATIAS")} roams Hoenn, and {sp("LATIOS")} waits on Southern Island.',
              f'   - **Blue**: {sp("LATIOS")} roams Hoenn, and {sp("LATIAS")} waits on Southern Island.',
              f'2. Talk to Mom: a letter from the Lilycove ferry company, with the **{EON}**.',
              f'3. Go outside. Prof. Birch is waiting by your door and takes you to his Lab, where your Pokédex becomes '
              f'the **National Pokédex**. From then on {beasts} roam Hoenn.']
    else:
        L += [f'1. Go downstairs. Dad is home and gives you the **{SS}**.',
              f'2. Check the TV downstairs: a news bulletin about a {colour} Flying Pokémon. That is {lati_roam}, and it '
              'now roams Hoenn. (The news is only on the TV in your own house.)',
              f'3. Talk to Mom: a letter from the Lilycove ferry company, with the **{EON}**.',
              f'4. Go outside. Prof. Birch is waiting by your door and takes you to his Lab, where your Pokédex becomes '
              f'the **National Pokédex**. From then on {beasts} roam Hoenn too.']
    L += ['', f'The {SS} lets you board the S.S. Tidal at Slateport\'s and Lilycove\'s harbors, to {tidal_to} '
          '([battles](#battles-after-the-hall-of-fame)).\n']

    # ---- roamers
    L += ['## Roaming legendaries\n', '| Pokémon | Level | Starts roaming |', '|---|---|---|']
    if E: L.append(f'| {sp("LATIAS")} or {sp("LATIOS")} | {roam[0][1]} | after Mom\'s question (the colour you answer) |')
    else: L.append(f'| {lati_roam} | {roam[0][1]} | when you watch the news on the TV at home |')
    L += [f'| {n} | {l} | when you get the National Pokédex |' for n, l in roam[1:]]
    L += ['', f'- **Where:** {roam_routes}. Never in towns, caves or buildings.',
          '- **Meeting one:** on the route where a roamer is, 1 in 4 wild battles in tall grass or on the water is the '
          'roamer (never when fishing). With several on the same route, it is one of them at random. A Repel keeps a '
          'roamer away only when your first Pokémon\'s level is higher than the roamer\'s.',
          '- **They move:** each time you walk from one route or town into the next, every roamer moves to a route next '
          'to its own (now and then further away). When you fly, go through a door or load your game, they all jump to '
          'new routes at random.',
          '- **In battle:** a roamer runs away as soon as it can. A move or Ability that traps it (such as Mean Look or '
          'Shadow Tag) stops it. The damage and status problems you gave it stay after it gets away.',
          '- **Caught:** it stops roaming. **Knocked out:** it is gone until you next enter the Hall of Fame; then it '
          'roams again with full HP.',
          '- **Tracking:** a roamer\'s AREA page in the Pokédex shows the route it is on right now (no area while it is '
          'not roaming).', '']

    # ---- tickets and islands
    L += ['## Event tickets and islands\n',
          '| Ticket | Who gives it | Island | Pokémon |', '|---|---|---|---|',
          f'| {EON} | Mom, at home (after Dad gives you the {SS}) | Southern Island | {lati_island_txt}, Lv {lv_lati_island} |',
          f'| {MAP} | Capt. Stern, Slateport City harbor | Faraway Island | {sp("MEW")}, Lv {lv["MEW"]} |',
          f'| {AURORA} | Prof. Cozmo, in his house in Fallarbor Town | Birth Island | {sp("DEOXYS")}, Lv {lv["DEOXYS"]} |',
          f'| {MYSTIC} | Lanette, in her house on Route 114 | Navel Rock | {sp("LUGIA")} and {sp("HO_OH")}, Lv {lv["LUGIA"]} |'
          if lv['LUGIA'] == lv['HO_OH'] else
          f'| {MYSTIC} | Lanette, in her house on Route 114 | Navel Rock | {sp("LUGIA")} Lv {lv["LUGIA"]}, {sp("HO_OH")} Lv {lv["HO_OH"]} |',
          '',
          '- Each ticket is given the first time you talk to that person after the Hall of Fame.',
          '- Show the ticket at **Lilycove City\'s harbor** (the Slateport ferry doesn\'t sail to the islands). With '
          'several tickets you choose the island. Every island has a sailor who takes you back to Lilycove.',
          (f'- The first time you show the {EON}, the ferry sails you straight to Southern Island. After that Southern '
           'Island is on the ferry\'s list for as long as you hold the ticket.' if E else
           f'- While you hold the {EON} and haven\'t been to Southern Island yet, the Lilycove ferry takes you there first.'),
          f'- The first time you show the {MAP}, Mr. Briney sails you to Faraway Island himself.', '',
          '### Southern Island\n',
          'From the boat, walk into the middle of the island and on to the stone at its far end. Stand in front of it and '
          f'read it. {lati_island_txt[0].upper() + lati_island_txt[1:]} flies down and battles you. '
          + ('If you run away, it is there again on your next visit. If you knock it out, it flies away and comes back '
             'after your next Hall of Fame. Once caught, it is gone. You lose: you black out, and it waits for your next '
             'visit.\n' if E else
             f'Once caught, it is gone. If you run away, lose or knock it out, it is gone for now: after your next Hall of '
             f'Fame the ferry sails to the island again (while you hold the {EON}) and it waits at the stone '
             '([legendaries that come back](#legendaries-that-come-back)).\n'),
          '### Faraway Island\n',
          f'When you go into the grassy middle of the island, {sp("MEW")} sees you and runs a few steps into the tall grass. '
          'Unlike Gen 3, it doesn\'t hide in the grass or move away as you walk: it stays in sight and wanders about a '
          'small patch of the tall grass on its own. Walk up next to it and talk to it to battle it. If it moves off, wait '
          'for it to stop near you.\n',
          '### Birth Island\n',
          'The triangle stands in the middle of the island top (in this game it looks like a white stone ball). Walk up '
          'from the dock and talk to it from below: it jumps to another spot. Each time it jumps, walk the shortest way '
          'to the side of it given here and talk to it again. Every step counts; turning on the spot does not.\n',
          '| Jump | Talk to it from | Steps allowed |', '|---|---|---|']
    L += [f'| {i + 1} | {side} | {n} |' for i, (side, n) in enumerate(zip(be_sides, steps))]
    L += ['',
          f'The {len(steps)}th time you talk to it after a jump, it breaks and {sp("DEOXYS")} appears. One step too many '
          'and it goes back to the middle: talk to it there from below and start again from jump 1. Leaving the island '
          'resets the puzzle.\n',
          f'Up to {"v2.0" if E else "v19.0"} the triangle always went back to the middle after its first jump, however you '
          f'walked (a bug, fixed in {"v2.1" if E else "v19.1"}).\n',
          '### Navel Rock\n',
          'From the boat, go into the rock and on through the caves to the long tunnel, and walk to its far end. There '
          'the way forks:',
          f'- **Up:** the ladder on the {"left" if nr_up_x < nr_down_x else "right"} climbs through {nr_up} small rooms to '
          f'the summit. Walk up the narrow path: {sp("HO_OH")} flies down and battles you.',
          f'- **Down:** the ladder on the {"right" if nr_up_x < nr_down_x else "left"} goes down through {nr_down} small '
          f'rooms to the bottom, where {sp("LUGIA")} waits. Talk to it to battle it.\n',
          f'### If you run, lose or knock one out ({sp("MEW")}, {sp("DEOXYS")}, {sp("LUGIA")}, {sp("HO_OH")})\n',
          '- **Caught:** it is gone from the island.',
          f'- **Ran away:** it is there again on your next visit ({sp("DEOXYS")}: solve the triangle again).',
          '- **You lose:** you black out, and it waits for your next visit.',
          '- **Knocked out:** it flies away, and comes back after your next Hall of Fame.', '']

    # ---- gifts
    L += ['## Gifts\n',
          f'- **{sp("BELDUM")}** (Lv {lv_beldum}): the Poké Ball in Steven\'s house in Mossdeep City, after the Hall of Fame. '
          'You need room in your party.',
          f'- **{sp("JIRACHI")}** (Lv {lv_jirachi}): the scientist at the back of the Mossdeep Space Center (1F) gives it '
          'after the Hall of Fame. You need room in your party.',
          f'- **{sp("CELEBI")}** (Lv {lv_celebi}): once you have the National Pokédex, it stands in the clearing in the '
          'north-east of Petalburg Woods, behind the girl who gives the Miracle Seed. Talk to it to battle it. If you run, '
          'it is back next time; if you knock it out, it comes back after your next Hall of Fame.',
          f'- **{names.item("ITEM_ENIGMA_BERRY")}**: Dad gives you one in Petalburg City Gym after the Hall of Fame (once; not '
          'while you already carry one).',
          f'- **Diploma**: catch all {len(diploma)} Pokémon of the Hoenn Pokédex'
          + (f' ({sp("JIRACHI")} and {sp("DEOXYS")} aren\'t needed)' if 385 not in diploma and 386 not in diploma else '')
          + ' and talk to the game designer on the 2F of the Cove Lily Motel in Lilycove City. He and the rest of the '
          'game\'s staff are there after the Hall of Fame.']
    if E:
        L.append(f'- **{_join(sp(s) for s in johto)}** (Lv {lv_johto}): once you have caught {johto_need} of the '
                 f'{hoenn_dex} Pokémon of the Hoenn Pokédex (after the National Pokédex), go to Prof. Birch\'s Lab: '
                 'choose one of the three. You need room in your party.')
    L.append('')

    # ---- completing the Pokédex
    own = sp(version.TABLE['legendary'])
    FIELD = '[field moves](tms-and-hms.md#field-moves-without-hms)'
    DEXNAV = '[DexNav](dexnav.md)' if has_our_c() else 'DexNav'
    def where(areas):
        out = []
        for area, ts in areas:
            how = [{'Grass and cave floor': None, 'Surfing': 'surfing'}.get(t, t) for t in ts]
            q = ('' if how == [None] else f' ({_join(h for h in how if h)})' if None not in how
                 else f' (also {_join(h for h in how if h)})')
            out.append(f'[{area}](wild-pokemon-{version.VERSION}.md#{_anchor(area)}){q}')
        return ', '.join(out)
    L += ['## Completing the Pokédex\n',
          f'After the Hall of Fame the whole Hoenn Pokédex can be completed in {version.PUBLIC_NAME} on its own, without '
          'trading: the Pokémon only the other versions had, and the ones you could only have one of, are here too.\n',
          '### The other versions\' Pokémon\n',
          'Some routes and caves get new wild tables after the Hall of Fame: the other versions\' Pokémon take some of '
          f'their slots. The [wild Pokémon page](wild-pokemon-{version.VERSION}.md) shows both tables of these areas (the '
          f'second one is marked "{AFTER_CHAMPION}"). The Pokédex\'s AREA page and the {DEXNAV} show the new '
          'Pokémon there once you are the Champion.\n',
          '| Pokémon | Where |', '|---|---|']
    L += [f'| {mon} | {where(areas)} |' for mon, areas in sorted(pg_new.items(), key=lambda kv: names.species_t.index(kv[0]))]
    L += ['', '### The two starters you didn\'t choose\n',
          'Talk to Prof. Birch in his Lab after he has given you the National Pokédex. He gives you the two Pokémon from his '
          f'Bag that you didn\'t pick on Route 101, Lv {lv_starters}, one after the other. Each one joins your party, or '
          'goes to your PC when your party is full. If your Boxes are full too, he keeps it until you have made room.'
          + (' This comes before the Johto starters, which he still gives as before ([gifts](#gifts)).' if E else '') + '\n']
    L += [f'### {sp("HUNTAIL")} and {sp("GOREBYSS")}\n', deep_sea + '\n']
    if not E:
        L += [f'### {other} in the Seafloor Cavern\n',
              f'{other}, the legendary Pokémon of Pokémon {other_game}, sleeps in the last room of the Seafloor Cavern, '
              f'the room where the story\'s {own} slept. After the Hall of Fame that room looks as it does in Pokémon '
              f'{other_game}: ' + ('a basin of lava with Groudon on it' if other_game == 'Ruby' else 'a pool of water with '
              'Kyogre in it') + f'. Dive on Route 128 ({FIELD}), surface into the cavern as in the story and make your way '
              'through to that last room. Walk up toward it: it wakes up and '
              f'battles you (Lv {lv_other}). Once caught, it is gone. If you run away, lose or knock it out, it is back '
              'after your next Hall of Fame.\n',
              'While it sleeps there, the scientist on the 2F of the Weather Institute (Route 119), the one who gave you '
              f'Castform, has a hint: "{hint.replace(chr(8217), chr(39))}"\n',
              '### The fossil you didn\'t take\n',
              'After the Hall of Fame, the fossil you left in the Route 111 desert (the Root Fossil or the Claw Fossil) is '
              'back at its spot the next time you come to Route 111. You need the Go-Goggles to cross the sandstorm, as '
              'before. Take it to the Devon Corporation in Rustboro City to have it revived, as you did with the first '
              'one.\n']
    gone = 'it is back after your next Hall of Fame'
    L += ['### Legendaries that come back\n',
          'A legendary Pokémon that you ran from, lost to or knocked out comes back after your next Hall of Fame. Once '
          'caught, it is gone for good. That is how the event-island legendaries, Celebi and the roaming legendaries '
          'already worked, and now these do too:']
    if E:
        L += [f'- **{_join(n for n, _, _ in regis)}** in their chambers ([the Sealed Chamber](#the-sealed-chamber)).',
              f'- **{sp("RAYQUAZA")}** at the top of the Sky Pillar: if you run away or lose, it is there again on your next visit; '
              f'if you knock it out, {gone}.',
              f'- **{sp("GROUDON")}** and **{sp("KYOGRE")}**: if you knock one out, the Weather Institute reports its '
              'weather again after your next Hall of Fame, and its cave holds it again '
              '([Terra Cave and Marine Cave](#terra-cave-and-marine-cave)).']
    else:
        L += [f'- **{own}** in the Cave of Origin: it is back in the deepest room, where you met it in the story.',
              f'- **{_join(n for n, _, _ in regis)}** in their chambers ([the Sealed Chamber](#the-sealed-chamber)).',
              f'- **{sp("RAYQUAZA")}** at the top of the [Sky Pillar](#sky-pillar).',
              f'- **{lati_island}** on [Southern Island](#southern-island): the ferry sails there again while you hold '
              f'the {EON}.',
              f'- **{other}** in the [Seafloor Cavern]'
              f'(#{_slug(f"{other} in the Seafloor Cavern")}).']
    L += ['', '"Caught" means that your Pokédex shows it as caught (one you got in a trade counts too). This works on '
          'saves from older versions as well: a legendary you lost there comes back after your next Hall of Fame.\n']

    # ---- places
    L += ['## New places\n', '### Altering Cave\n',
          'After the Hall of Fame a cave opens in the cliff on the north side of the water on Route 103 (Surf to it). Its '
          f'wild Pokémon change by the day: {altering[0][0][0]} until your first visit, then the next one in this list '
          'each new day you pass through Route 103 (after the last, back to the first).\n',
          '| | Pokémon | Level |', '|---|---|---|']
    L += [f'| {i + 1} | {", ".join(r[0] for r in t)} | {", ".join(r[1] for r in t)} |' for i, t in enumerate(altering)]
    six = 1 - ((mirage - 1) / mirage) ** 6
    L += ['', '### Mirage Island\n',
          'Not tied to the Hall of Fame: the island shows on Route 130 (between Route 129 and Route 131) on days when the '
          f'day\'s number matches a Pokémon in your party (Eggs too). That is 1 in {mirage} for each Pokémon each day, '
          f'about 1 in {round(1 / six)} days with six. The number changes once a day. On the island: '
          f'{_join(f"{n} (Lv {l})" for n, l, _ in wynaut)} in the tall grass, and a {names.item("ITEM_LIECHI_BERRY")} tree.\n']
    sp_climb = [   # the Sky Pillar's floors once they are cracked (Sapphire / Ruby after the Hall of Fame, Emerald after Sootopolis)
        '- **Cracked floors (2F and 4F):** walking onto a crack drops you to the floor below. Ride your Bicycle over them. '
        'Here any riding crosses them, slow or fast (in Gen 3 it took the Mach Bike at full speed).',
        '- **4F:** the stairs up to 5F are in the top-left corner, and you can\'t ride there. Ride round to the narrow '
        'passage that runs just below that corner, get off the Bicycle, and walk onto one of the two cracks in the middle '
        'of the passage. You drop into a closed-off part of 3F; its stairs take you up into the corner, by the stairs to 5F.']
    if E:
        L += ['### Steven\'s Cave\n',
              'After the Hall of Fame the rock in the first room of Meteor Falls (the room you come into from Route 114) '
              'is gone, and behind it is Steven\'s cave. It is in the top-left corner of that room, which you can only reach '
              'by a ladder up from the floor below:',
              '1. In the first room, Surf to the waterfall and climb it (Waterfall) to the room above.',
              '2. In that room, take a ladder down to the floor below (Meteor Falls B1F).',
              '3. There, make your way to the ladder up in its west part (Surf where you need to). It comes up in the '
              'corner of the first room, next to the cave.\n',
              f'Steven battles you (Lv {_levels(steven)}; his team is on the [trainers page](trainers-emerald.md#steven)). '
              'Beat him once; after that he only talks. If you lose, he battles you again next time.\n',
              '### Terra Cave and Marine Cave\n',
              '1. After the Hall of Fame, talk to the scientist on the Weather Institute\'s 2F (Route 119). (If you never '
              'took his Castform, he gives you that first: talk to him again.) He reports a drought or heavy rain on one '
              'route, picked at random each time you come up to his floor. Asking him again on the same visit gives the '
              'same route.',
              f'2. Go to that route{" (each route has two places where it can happen: look along the whole route)" if aw_two else ""}:',
              f'   - **Drought** ({terra_routes}): the sun is harsh and a new cave mouth has opened in a rock wall. Walk in: '
              f'it is Terra Cave, with {sp("GROUDON")} (Lv {lv_groudon}) at its end.',
              f'   - **Heavy rain** ({marine_routes}): look for a patch of rough water. Dive there ({FIELD}), swim into '
              'the cave opening on the sea floor, and press A to surface inside. Surf across the pool to the shore and go '
              f'on: it is Marine Cave, with {sp("KYOGRE")} (Lv {lv_kyogre}) at its end.',
              '3. At the end of the cave, walk up toward it from below: it comes to you and battles you.\n',
              f'- The weather lasts {aw_steps:,} steps from the moment the scientist spoke: go straight there. If the steps '
              'run out while you are inside the cave, you can still finish it. After that, ask the scientist for a new place.',
              '- Caught: it is gone for good, and its weather ends. Knocked out: its weather ends, and after your next Hall '
              'of Fame the scientist reports it again. Ran away or lost: it is back on your next visit. Once neither is '
              'left (caught, or knocked out until your next Hall of Fame), the scientist has no more reports.\n',
              '### Desert Underpass\n',
              'Go into the Fossil Maniac\'s house on Route 114 and on into his tunnel. After the Hall of Fame he stands '
              'aside and the tunnel goes on into the Desert Underpass. At its far end lies the fossil you didn\'t take at '
              'the Mirage Tower (the Root Fossil or the Claw Fossil); it is only there once you have taken one of the two. '
              f'Wild Pokémon there: {_join(r[0] for r in grass("DesertUnderpass"))} '
              f'([wild Pokémon](wild-pokemon-emerald.md#{_anchor(place("DesertUnderpass"))})).\n',
              '### Safari Zone\n',
              'After the Hall of Fame the two workers at the east edge of the Safari Zone\'s first area (the one you come '
              'into) are gone. Walk east past where they stood into the new south-east area; north of it is the new '
              'north-east area.' + (' They are part of the Safari game ([Safari Zone rules](wild-pokemon-emerald.md#safari-zone-rules)).'
                                    if has_our_c() else '') + ' Each has its own wild Pokémon:']
        L += [f'- [{place(m)}](wild-pokemon-emerald.md#{_anchor(place(m))}): '
              + '; '.join(f'{how} {_join(mons)}' for how, mons in hows) + '.' for m, hows in safari_new]
        L += ['',
              '### Artisan Cave\n',
              'On the Battle Frontier island: a cave between its east and west halves, with wild '
              f'{_join(f"{r[0]} (Lv {r[1]})" for r in grass("ArtisanCave_1F"))} '
              f'([wild Pokémon](wild-pokemon-emerald.md#{_anchor(place("ArtisanCave_1F") + " / " + place("ArtisanCave_B1F"))})).\n']
    else:
        L += ['### Sky Pillar\n',
              'After the Hall of Fame a rocky islet appears on Route 131 (west of Pacifidlog Town). Surf to it and go into '
              'the cave; at its far end you come out by the tower\'s door. Inside, take the stairs up floor by floor:']
        L += sp_climb
        L += ['', f'At the top waits {sp("RAYQUAZA")} (Lv {lv_ray}): talk to it. Once caught, it is gone. If you run '
              'away, lose or knock it out, it is back at the top after your next Hall of Fame '
              '([legendaries that come back](#legendaries-that-come-back)).\n']

    # ---- other legendaries
    L += ['## Other legendaries\n', 'The legendaries you meet in the rest of the game:\n',
          '| Pokémon | Where | When | Level | Chances |', '|---|---|---|---|---|']
    back = 'not caught: back after your next Hall of Fame'
    ko = 'ran away: back next visit; knocked out: back after your next Hall of Fame'
    if not E:
        L.append(f'| {own} | Cave of Origin, Sootopolis City | during the story | {lv_legend} | {back} |')
    for n, room, route in regis:
        L.append(f'| {n} | {room} ({route}) | after the Sealed Chamber | {lv_regi} | {back} |')
    if E:
        L += [f'| {sp("RAYQUAZA")} | Sky Pillar, top (Route 131) | after the Sootopolis events | {lv_ray} | {ko} |',
              f'| {sp("GROUDON")} | Terra Cave | after the Hall of Fame | {lv_groudon} | {ko} |',
              f'| {sp("KYOGRE")} | Marine Cave | after the Hall of Fame | {lv_kyogre} | {ko} |']
    else:
        L += [f'| {sp("RAYQUAZA")} | Sky Pillar, top (Route 131) | after the Hall of Fame | {lv_ray} | {back} |',
              f'| {other} | [Seafloor Cavern, last room](#{_slug(f"{other} in the Seafloor Cavern")}) (Route 128) | '
              f'after the Hall of Fame | {lv_other} | {back} |']
    L += ['', '### The Sealed Chamber\n',
          'The three Regi chambers open together, from the Sealed Chamber under the sea of Route 134. Braille in this game '
          'is shown as the plain text it spells.\n',
          f'1. On Route 134, Surf to the patch of dark deep water (the current stops there) and Dive ({FIELD}).',
          '2. Underwater, swim south into the opening below you, then follow the trench down to its far end. Stand just '
          f'below the braille there ("{sc_go_up}") and press A to surface. (In Gen 3 it was B. Surfacing anywhere else '
          'brings you back up on Route 134.)',
          f'3. You come up in the Sealed Chamber. Walk to the braille in the middle of the top wall ("{sc_dig}") and step '
          'onto the floor right in front of it with a Pokémon in your party that knows Dig: it digs through the wall for '
          'you. It must be a Pokémon that knows Dig (the TM in your Bag is not enough; no badge is needed).',
          f'4. Go through. Put {sp(si_first)} first and {sp(si_last)} last in your party (the last Pokémon you carry, '
          f'however many you have), then read the braille on the far wall ("{si_braille}"). The room shakes: the three '
          'chambers are open.\n',
          '### The three Regi chambers\n',
          'Each is a small cave with braille on the back wall of its first room. Stand in front of the braille and read it, '
          'then do what it says: the wall behind it opens. Go through and talk to the Regi. When a field move is needed, '
          'you don\'t choose it from the menu: step onto the right spot and it is used for you, as long as you could use '
          f'it there ({FIELD}: the badge, then a Pokémon that knows the move or its TM or HM in your Bag).\n']
    regi_where = {r[1]: f'{r[1]} ({r[2]}), {r[0]}' for r in regis}
    def move_spot(spot):
        move, it, badge, x0, x1, y, bx, by = spot
        dx, dy = (x0 + x1) // 2 - bx, y - (by + 1)        # from the tile in front of the braille
        if dx and dy > 0:
            where = (f'{move} is used when you step onto the spot {abs(dx)} steps {"right" if dx > 0 else "left"} and {dy} '
                     'steps down from the one in front of the braille.')
        elif not dx and dy > 0:
            where = (f'{move} is used when you step onto the middle of the room, {dy} steps straight down from the spot in '
                     'front of the braille. You cross it when you walk straight up from the entrance.')
        else: raise SystemExit('gen_docs: a Regi chamber\'s spot is somewhere new: update postgame_page')
        return f'{where} ({badge} Badge; {it}.)'
    L.append(f'- **{regi_where[place("DesertRuins")]}.** The braille: "{br["dr"]}" {move_spot(regi_dr)}')
    if E:
        L.append(f'- **{regi_where[place("IslandCave")]}.** The braille: "{br["ic"]}" Read it from the spot right in front '
                 f'of it. Then walk once round the whole room on the tiles right next to the wall ({ic_lap} tiles: into every '
                 'corner and past the exit), either way round, and come back to the spot in front of the braille: the wall '
                 'opens. One step onto the open floor in the middle spoils it: read the braille again and start over.')
    else:
        L.append(f'- **{regi_where[place("IslandCave")]}.** The braille: "{br["ic"]}" Read it and then just wait: the '
                 f'message stays up for about {round(ic_wait / 30 / 60)} minutes, then the wall opens. Here pressing a '
                 'button doesn\'t spoil the wait (in Gen 3 it did).')
    L += [f'- **{regi_where[place("AncientTomb")]}.** The braille: "{br["at"]}" {move_spot(regi_at)}', '']
    if E:
        L += [f'### {sp("RAYQUAZA")} at the Sky Pillar\n',
              f'During the story the Sky Pillar\'s floors are whole. Once {sp("RAYQUAZA")} has stopped the fight in '
              f'Sootopolis, it goes back to the top of the Sky Pillar (Route 131), and the floors are cracked:']
        L += sp_climb
        L += ['', f'At the top, talk to {sp("RAYQUAZA")} (Lv {lv_ray}).\n']

    # ---- battles
    L += ['## Battles after the Hall of Fame\n',
          '- **The Pokémon League** can be challenged again. The Elite Four and the Champion keep their teams.',
          f'- **Wally** waits in Victory Road 1F for a battle (Lv {_levels(wally)}; his team is on the '
          f'[trainers page](trainers-{version.VERSION}.md#wally)).' + (' Afterwards he rematches you once a day '
                                                                         '([rematches](#rematches)).' if E else '')]
    if E:
        L += [f'- **The Battle Frontier**: take the S.S. Tidal from Slateport or Lilycove with the {SS}. Rules, Battle '
              'Points and prizes: [Battle Frontier page](battle-frontier.md). Black 2\'s Pokémon World Tournament (PWT) '
              'is in the Frontier\'s Ranking Hall.',
              '- **Trainer Hill** (Route 111) opens after the Hall of Fame; the **Battle Tents** in Verdanturf, Fallarbor '
              'and Slateport are open during the story too. Both are on the [Battle Frontier page](battle-frontier.md).',
              f'- **Steven** in [Steven\'s Cave](#stevens-cave).', '']
    else:
        bt = _src('0042_room_BattleTower_Lobby.s')
        short = re.findall(r'VAR_BT_PRIZE, (ITEM_\w+)', bt.split('Sub_BTL_DeterminePrize:', 1)[1].split('L_BTL_LongPrize:', 1)[0])
        long_ = re.findall(r'VAR_BT_PRIZE, (ITEM_\w+)', bt.split('L_BTL_LongPrize:', 1)[1].split('L_BTL_PrizeSet:', 1)[0])
        after = _num('0042_room_BattleTower_Lobby.s', r'h_goto_if_gt BT_T2, (\d+), L_BTL_LongPrize')
        ribbon = _num('0042_room_BattleTower_Lobby.s', r'WorkCmpConst BT_T2, (\d+)\s*\n\s*VMJumpIf CMP_LE, L_BTL_RibDone')
        banned = []
        for n in re.findall(r'WorkCmpConst 0x8050, (\d+)', _src('scenes/battle_tower_eligible.inc')):
            if int(n) not in banned: banned.append(int(n))
        L += [f'- **The Battle Tower island**: take the S.S. Tidal from Slateport or Lilycove with the {SS}.', '',
              '### Battle Tower\n',
              '- Two rooms: **Lv. 50** (your Pokémon must be level 50 or lower; the opponents are level 50) and '
              '**Lv. 100** (any level; the opponents are level 100). Your Pokémon keep their own levels.',
              '- Three Pokémon, no Eggs, no species twice and no held item twice. Not allowed: '
              + _join(names.species_t[s] for s in sorted(banned)) + '.',
              '- A challenge is seven battles in a row; your Pokémon are healed between battles. You can save and quit '
              'between battles and go on later.',
              f'- Prize for each challenge won: one of {_or(names.item(i) for i in short)} (at random) for your first '
              f'{after + 1} challenges in a row, then one of {_or(names.item(i) for i in long_)}.',
              f'- When a challenge ends with more than {ribbon} wins in a row, the three Pokémon get the Winning Ribbon '
              '(Lv. 50) or the Victory Ribbon (Lv. 100).',
              '- A man in the lobby awards the Silver Shield at a best streak of 50 and the Gold Shield at 100: decorations '
              'for your Secret Base.', '',
              '### Pokémon World Tournament (PWT)\n',
              'The second building on the island is Black 2\'s PWT. The left desk offers the Driftveil, Rental and Mix '
              'tournaments (Download needs Nintendo\'s closed online service). The right desk offers the Unova Leaders and '
              'Hoenn Leaders tournaments, and more as you win them, as in Black 2 (Kanto, Johto and Sinnoh Leaders after '
              'the Unova Leaders, then World Leaders and Champions). Battle Points won there are spent at the lobby\'s '
              'counters.', '',
              'Gym Leader and trainer rematches are in Pokémon Emerald NDS only.', '']
    if E:
        badges, leaders, wally_tiers, route = rm_badges, rm_leaders, rm_wally, rm_route
        L += ['## Rematches\n',
              f'- **Trainers on the routes:** once you have {badges} badges, talk to a trainer from the list below whom '
              'you have beaten. Answer YES for a rematch. Each trainer battles once a day, with a team that depends on '
              'your badges; the day you first beat a trainer counts as its battle that day, so its first rematch comes '
              'the next day. Pairs fight a double battle (you need two Pokémon that can battle).',
              '- **Gym Leaders:** after the Hall of Fame, talk to a Leader in their Gym, once a day. Each rematch is a '
              'double battle, with a stronger team each time you win (four teams; the last one repeats). Until you have '
              'done Wattson\'s job in New Mauville (he gives you TM24 Thunderbolt), each Leader offers only the first '
              'rematch, and Wattson none.',
              '- **Wally:** after the Hall of Fame he waits at the exit of Victory Road 1F. After your first battle there, '
              f'he rematches you once a day: {len(wally_tiers)} stronger teams in turn (the last one repeats).', '',
              '### Gym Leaders\n']
        for _, name, where, tiers in leaders:
            L += [f'**{name}** ({where})', '', '| Rematch | Team (double battle) |', '|---|---|']
            L += [f'| {i + 1} | {t} |' for i, t in enumerate(tiers)]
            L.append('')
        L += ['### Wally\n', '| Rematch | Team |', '|---|---|']
        L += [f'| {i + 1} | {t} |' for i, t in enumerate(wally_tiers)]
        L += ['', '### Trainers\n', 'The highest level in each team, by the badges you have.\n',
              f'| Trainer | Where | {badges} badges | {badges + 1} | {badges + 2} | {badges + 3} |', '|---|---|---|---|---|---|']
        L += [f'| {who} | {where} | ' + ' | '.join(lv) + ' |' for who, where, lv in route]
        L.append('')
    return '\n'.join(L)


# ---- levels -----------------------------------------------------------------------------------------------------------
def _level_in(rel, tok):
    """A level as a script writes it: a number, or a #define name (in the same file or any scene library)."""
    if tok.isdigit(): return int(tok)
    libs = sorted(os.path.relpath(p, FS) for p in glob.glob(os.path.join(FS, 'scenes', '**', '*.inc'), recursive=True))
    for p in [rel] + libs:
        m = re.search(rf'#define\s+{tok}\s+(\d+)\b', _src(p))
        if m: return int(m.group(1))
    raise SystemExit(f'gen_docs: no level for {tok} ({rel}): update levels_data')

def _gen3_statics(dec):
    """Species -> level of the decomp's one-off battles (setwildbattle / seteventmon in its maps' scripts)."""
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, 'external', dec, 'data', 'maps', '*', 'scripts.inc'))):
        for s, lv in re.findall(r'(?:setwildbattle|seteventmon) SPECIES_(\w+), (\d+)', open(p, encoding='utf-8').read()):
            out.setdefault(s, int(lv))
    return out

def levels_data(names):
    """This version's part of levels.md (gen_docs.py --levels-data prints it as JSON): the one-off battles (Gen 3 level,
    level here), the gifts and trades, and the Gym Leaders', Elite Four's and Champion's aces (data/hoenn_trainer_data.json:
    sapphire_level = the version's own Gen 3 level, level = this game's)."""
    import roamers, trades
    E = version.is_emerald()
    sp = names.species
    g3 = _gen3_statics('pokeemerald')                 # (the event islands are Emerald's maps in every version)
    if not E: g3.update(_gen3_statics('pokeruby'))
    one = []                                          # (key, Pokémon, where, Gen 3 level, level here)
    def add(key, mon, where, g3_species, here):
        one.append((key, mon, where, g3[g3_species], here))
    if not E:
        add('legend', sp(version.TABLE['legendary']), 'Cave of Origin', 'GROUDON_OR_KYOGRE',
            _define('0206_room_CaveOfOrigin_B4F.s', 'B4_KYOGRE_LEVEL'))
        # the other weather legend after the Champion (postgame_dex): Gen 3's level of that version's Cave of Origin B4F
        add('other_legend', sp(_version_define('SPECIES_KYOGRE_OR_GROUDON')), 'Seafloor Cavern (after the Hall of Fame)',
            'GROUDON_OR_KYOGRE', _define('scenes/SeafloorCavern_Room9_Postgame.inc', 'R9_OTHER_LEGEND_LEVEL'))
    regi = _level_in('scenes/ch12_lib.inc', re.search(r'CallWildBattle \\species, (\w+), 1', _src('scenes/ch12_lib.inc')).group(1))
    for f in ('0232_room_DesertRuins.s', '0254_room_IslandCave.s', '0188_room_AncientTomb.s'):
        s = re.search(r'h_regi_battle SPECIES_(\w+)', _src(f)).group(1)
        add(s, sp(s), place(re.sub(r'^\d+_room_|\.s$', '', f)), s, regi)
    lati = _define('scenes/SouthernIsland_Interior.inc', 'SII_LATIOS_LEVEL')
    if E: add('lati', f'{sp("LATIOS")} or {sp("LATIAS")}', 'Southern Island', 'LATIOS', lati)
    else: add('lati', sp(version.TABLE['island']), 'Southern Island', 'LATIAS_OR_LATIOS', lati)
    add('RAYQUAZA', sp('RAYQUAZA'), 'Sky Pillar', 'RAYQUAZA',
        _define('scenes/emerald/em_ch10_lib.inc', 'EM_RAYQUAZA_LEVEL') if E else _define('scenes/SkyPillar_Top.inc', 'SP_RAYQUAZA_LEVEL'))
    if E:
        add('GROUDON', sp('GROUDON'), 'Terra Cave', 'GROUDON', _define('0732_room_TerraCave_End.s', 'TCE_LEVEL'))
        add('KYOGRE', sp('KYOGRE'), 'Marine Cave', 'KYOGRE', _define('0738_room_MarineCave_End.s', 'MCE_LEVEL'))
    for s, where in (('MEW', 'Faraway Island'), ('DEOXYS', 'Birth Island'), ('LUGIA', 'Navel Rock'), ('HO_OH', 'Navel Rock')):
        add(s, sp(s), where, s, _define('scenes/events_lib.inc', f'EV_{s}_LEVEL'))
    disc = {n: int(a) for n, a, _ in re.findall(r'(\w+) (\d+) \([^)]*\) -> (\d+)', _src('scenes/postgame_lib.inc'))}
    one.append(('CELEBI', sp('CELEBI'), 'Petalburg Woods', disc['Celebi'], _define('scenes/postgame_lib.inc', 'PG_CELEBI_LEVEL')))
    for s, l in roamers.ROAMERS:
        one.append((s, sp(s), 'roaming', l, roamers.scaled(l)))
    def static_level(rel, species):      # a number or a #define name (postgame_fix: the statics follow the curve)
        return _level_in(rel, re.search(rf'h_static_battle SPECIES_{species}, (\w+)', _src(rel)).group(1))
    add('KECLEON', sp('KECLEON'), 'Routes 119 and 120 (Devon Scope)', 'KECLEON', static_level('scenes/ch7_lib.inc', 'KECLEON'))
    add('VOLTORB', sp('VOLTORB'), 'New Mauville', 'VOLTORB', static_level('0266_room_NewMauville_Inside.s', 'VOLTORB'))
    hideout = 'MagmaHideout_B1F' if version.is_ruby() else 'AquaHideout_B1F'
    hf = os.path.basename(next(p for p in version.overlay(FS, '*.s') if p.endswith(f'_room_{hideout}.s')))
    add('ELECTRODE', sp('ELECTRODE'), place(hideout), 'ELECTRODE', static_level(hf, 'ELECTRODE'))

    gifts = [('Your first Pokémon', 'Route 101', _num('0634_route_101.s', r'PokePartyAdd \w+, \w+, 0, (\d+)')),
             (sp('CASTFORM'), 'Weather Institute, Route 119',
              _num('1128_room_Route119_WeatherInstitute_2F.s', r'PokePartyAddEx \w+, SPECIES_CASTFORM, 0, (\d+)')),
             (f'{sp("LILEEP")} or {sp("ANORITH")}', 'Devon Corporation, Rustboro City (from the fossil)',
              _num('scenes/RustboroCity_DevonCorp_2F_Fossil.inc', r'PokePartyAdd \w+, DVF_SPECIES, 0, (\d+)')),
             (sp('BELDUM'), 'Steven\'s house, Mossdeep City',
              _num('scenes/MossdeepCity_StevensHouse_Ch13.inc', r'PokePartyAdd \w+, SPECIES_BELDUM, 0, (\d+)')),
             (sp('JIRACHI'), 'Mossdeep Space Center', _define('scenes/postgame_lib.inc', 'PG_JIRACHI_LEVEL')),
             ('The two starters you didn\'t choose', 'Prof. Birch\'s Lab (after the Hall of Fame)',
              _num('scenes/BirchLab_Postgame.inc', r'PokePartyAdd PGS_SLOT, PGS_SPECIES, 0, (\d+)'))]
    if E:
        johto = re.findall(r'emj_ball SPECIES_(\w+)', _src('scenes/emerald/BirchLab_JohtoStarters.inc'))
        gifts.append((_or(sp(s) for s in johto), 'Prof. Birch\'s Lab',
                      _num('scenes/emerald/BirchLab_JohtoStarters.inc', r'PokePartyAdd EMJ_SLOT, \\species, 0, (\d+)')))
    trade = [(names.species_t[t['species']], names.species_t[t['wanted']], t['level']) for _, t in sorted(trades.TRADES.items())]

    data = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers']
    by_id = {}
    for t in data.values():
        if E and 'emerald_trainer' not in t: continue
        if t.get('rematch_of'): continue
        by_id.setdefault(t['b2_id'], t)
    key = {}
    for i, t in sorted(by_id.items()):
        cls = t['sapphire_class']
        if cls not in ('LEADER', 'ELITE_FOUR', 'CHAMPION'): continue
        k = (('LEADER', 'ELITE_FOUR', 'CHAMPION').index(cls), 'Tate' if t['name'] == 'Liza' else t['name'])
        key.setdefault(k, []).extend(t['party'])
    aces = []
    for (c, name), party in sorted(key.items(), key=lambda kv: (kv[0][0], max(p['level'] for p in kv[1]))):
        ace = max(party, key=lambda p: (p['level'], p['sapphire_level']))
        who = {0: 'Gym Leader', 1: 'Elite Four', 2: 'Champion'}[c] + ' ' + ('Tate and Liza' if name == 'Tate' else name)
        aces.append((who, sp(ace['species']), ace['sapphire_level'], ace['level']))
    return dict(version=version.VERSION, one=one, gifts=gifts, trades=trade, aces=aces)

def levels_page(parts):
    """levels.md from data/level_scaling.json (converter/level_scaling.py, notes/LEVEL_SCALING.md) and each version's
    levels_data (parts: version -> its JSON)."""
    sc = json.load(open(os.path.join(ROOT, 'data', 'level_scaling.json')))
    t = {int(k): v for k, v in sc['curve']['table'].items()}
    same = max(l for l in t if all(t[k] == k for k in range(1, l + 1)))
    top = min(l for l in t if t[l] == 100 and l < 100)
    rise = ', '.join(f'+{t[l] - l} at Lv {l}' for l in (25, 30, 42, 58))
    a, l0, p = sc['curve']['a'], sc['curve']['L0'], sc['curve']['p']
    V = version.VERSIONS
    def vname(vs):
        return 'all versions' if len(vs) == len(V) else _join(VNAME[v] for v in vs)
    L = [HEADER, '# Levels and the Exp. Share\n',
         'This game has a Gen 6-style Exp. Share: a key item you switch on and off in the Bag. While it is on, the '
         'Pokémon that don\'t battle get Exp. Points too, so your whole team grows together. You get it from Prof. '
         'Birch\'s sixth question at the start ([options](options.md)) or from Mr. Stone in Rustboro, as in the '
         'original games.\n',
         '## Why the levels change\n',
         'With the whole team levelling, the original levels would make the second half of the game easier than it '
         'was. So opponents above Lv 24 (in the original story, everything after Mr. Stone\'s Exp. Share) get slightly '
         'higher levels. The rise is small, because '
         'Black 2\'s Exp. Points formula already gives less to a Pokémon that is stronger than its opponent. The new '
         'levels keep the gap between your main Pokémon and your opponents about where it was in the original games.\n',
         '## The rule\n',
         f'- Nothing at Lv {same} or below changes, so everything before the Exp. Share keeps its level.',
         f'- Above that the rise is small: {rise}.',
         f'- Lv {top} and above becomes Lv 100.',
         f'- The formula, for the curious: new level = L + {a:.2f} × (L − {l0:g})^{p:g}, rounded to the nearest level, '
         'at most 100.', '',
         '## The levels\n',
         f'Find the original level: the row is the tens, the column the ones. Levels 1-{same} don\'t change; '
         f'{top} and above become 100.\n',
         '| | ' + ' | '.join(f'+{i}' for i in range(10)) + ' |', '|---|' + '---|' * 10]
    for d in range(20, top + 1, 10):
        L.append(f'| **{d}** | ' + ' | '.join(str(t[d + i]) if d + i <= 100 else '' for i in range(10)) + ' |')
    L += ['', '## What follows the curve\n',
          '- **Every trainer**: route trainers, Gym Leaders, the Elite Four, the Champion, your rival, Wally and the '
          'team bosses (Pokémon Emerald NDS: the rematch teams too).',
          '- **Every wild Pokémon**: tall grass, caves, surfing, the three rods and Rock Smash. Each slot\'s lowest and '
          'highest level are both converted (the wild Pokémon pages already show the new levels).',
          '- **The legendaries and the other one-off battles**, as the table shows.', '',
          '| Pokémon | Where | Versions | Original | This game |', '|---|---|---|---|---|']
    rows, order = collections.OrderedDict(), []
    for v in V:                          # one order keeping every version's own (a version's new row after its neighbour)
        prev = None
        for k, mon, where, g, here in parts[v]['one']:
            rows.setdefault((k, mon, where, g, here), []).append(v)
            if k not in order: order.insert(order.index(prev) + 1 if prev else 0, k)
            prev = k
    off = []
    for (k, mon, where, g, here), vs in sorted(rows.items(), key=lambda kv: (order.index(kv[0][0]), V.index(kv[1][0]))):
        L.append(f'| {mon} | {where} | {vname(vs)} | {g} | {here} |')
        if t[g] != here and (mon, g, here) not in off: off.append((mon, g, here))
    if off:
        L += ['', 'Not on the curve: ' + _join(f'{m} (Lv {h}; the curve would give {t[g]})' for m, g, h in off)
              + '. These keep their original level.']
    L += ['', '## What doesn\'t\n',
          '- **Gifts** keep their original level:']
    grows = collections.OrderedDict()
    for v in V:
        for mon, where, lv in parts[v]['gifts']:
            grows.setdefault((mon, where, lv), []).append(v)
    L += [f'  - {mon} (Lv {lv}), {where}' + ('' if len(vs) == len(V) else f' ({vname(vs)})') for (mon, where, lv), vs in grows.items()]
    tgroups = collections.OrderedDict()               # (em_trades) each version's own trades (Emerald has its four)
    for v in V:
        tgroups.setdefault(json.dumps(parts[v]['trades']), []).append(v)
    def trade_list(trs):
        return _join(f'{a} for your {b} (Lv {lv})' for a, b, lv in trs)
    if len(tgroups) == 1 and parts[V[0]]['trades']:
        L.append('- **In-game trades** come at a fixed level: ' + trade_list(parts[V[0]]['trades']) + '.')
    elif len(tgroups) > 1:
        L.append('- **In-game trades** come at a fixed level:')
        L += [f'  - {vname(vs)}: ' + trade_list(json.loads(trs)) + '.' for trs, vs in tgroups.items() if json.loads(trs)]
    L += ['- **Battle facilities** have their own level rules: the Battle Tower, the Pokémon World Tournament, and in '
          'Pokémon Emerald NDS the Battle Frontier, Battle Tents and Trainer Hill '
          '([Battle Frontier page](battle-frontier.md)).', '',
          '## The switch doesn\'t matter\n',
          'The levels are part of the game itself. They are the same whether your Exp. Share is on or off, and whether '
          'you took it from Prof. Birch at the start or from Mr. Stone. Switching it off only means the Pokémon that '
          'don\'t battle stop getting Exp. Points; the opponents stay as they are.\n',
          '## Key battles\n',
          'The highest-level Pokémon of each Gym Leader, the Elite Four and the Champion: the original game\'s level and '
          'this game\'s. Full teams are on the trainers pages.\n']
    groups = collections.OrderedDict()
    for v in V:
        groups.setdefault(json.dumps(parts[v]['aces']), []).append(v)
    for aces, vs in groups.items():
        L += [f'### {_join(VNAME[v] for v in vs)}\n', '| Battle | Pokémon | Original | This game |', '|---|---|---|---|']
        L += [f'| {who} | {mon} | {g} | {here} |' for who, mon, g, here in json.loads(aces)]
        L += ['', 'Teams: ' + ', '.join(f'[{VNAME[v]}](trainers-{v}.md)' for v in vs) + '.', '']
    return '\n'.join(L)

def index_page(dexnav=True):
    L = [HEADER, '# Pokémon Ruby, Sapphire & Emerald NDS: player guide\n',
         'Made from the game\'s own data, so it matches the current release.\n',
         '| | Sapphire | Ruby | Emerald |', '|---|---|---|---|']
    for title, stem in (('Wild Pokémon', 'wild-pokemon'), ('Item locations', 'items'), ('Important trainers', 'trainers'),
                        ('After the Hall of Fame', 'postgame')):
        L.append(f'| {title} | ' + ' | '.join(f'[{VNAME[v]}]({stem}-{v}.md)' for v in version.VERSIONS) + ' |')
    L.append('| Levels and the Exp. Share | ' + ' | '.join(f'[{VNAME[v]}](levels.md)' for v in version.VERSIONS) + ' |')
    L += [''] + (['- [The DexNav](dexnav.md)'] if dexnav else []) + ['- [Start-of-game options](options.md)', '- [The Fairy type (optional)](fairy-type.md)',
          '- [TMs and HMs](tms-and-hms.md)', '- [Trade evolutions](evolutions.md)', '- [Battle Frontier, Battle Tents and Trainer Hill (Emerald)](battle-frontier.md)', '',
          'Learnsets are Black 2\'s, plus the Fairy moves when the Fairy type is on.', '']
    return '\n'.join(L)


def write(out, name, text):
    open(os.path.join(out, name), 'w', encoding='utf-8').write(text)
    print('wrote', name, len(text), 'B')

def main():
    if '--levels-data' in sys.argv:              # this version's part of levels.md, as JSON (HOENN_VERSION set by the caller)
        print(json.dumps(levels_data(Names()), ensure_ascii=False))
        return
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = os.path.abspath(args[0] if args else os.path.expanduser('~/Documents/GitHub/pokemon-ruby-sapphire-nds/docs'))
    os.makedirs(out, exist_ok=True)
    if '--part' in sys.argv:                     # one version's pages (HOENN_VERSION set by the caller)
        names = Names()
        write(out, f'wild-pokemon-{version.VERSION}.md', wild_page(names))
        write(out, f'items-{version.VERSION}.md', items_page(names))
        write(out, f'trainers-{version.VERSION}.md', trainers_page(names))
        write(out, f'postgame-{version.VERSION}.md', postgame_page(names))
        if version.is_emerald(): write(out, 'battle-frontier.md', frontier_page(names))
        return
    for v in version.VERSIONS:
        subprocess.run([sys.executable, os.path.abspath(__file__), out, '--part'], check=True,
                       env=dict(os.environ, HOENN_VERSION=v))
    names = Names()
    write(out, 'tms-and-hms.md', tms_page(names))
    write(out, 'fairy-type.md', fairy_page(names))
    write(out, 'evolutions.md', evolutions_page(names))
    write(out, 'options.md', options_page())
    dexnav = dexnav_page(names)
    if dexnav: write(out, 'dexnav.md', dexnav)
    else: print(f'skipped dexnav.md: the decomp tree ({os.path.relpath(B2, ROOT)}) has no HoennB2 C (include/hoennb2.h) to read the DexNav from')
    parts = {v: json.loads(subprocess.run([sys.executable, os.path.abspath(__file__), '--levels-data'], check=True,
                                          capture_output=True, text=True, env=dict(os.environ, HOENN_VERSION=v)).stdout)
             for v in version.VERSIONS}
    write(out, 'levels.md', levels_page(parts))
    write(out, 'README.md', index_page(dexnav is not None))

if __name__ == '__main__':
    main()
