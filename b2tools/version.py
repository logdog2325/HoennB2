"""The game version of a build: Sapphire (default), Ruby or Emerald (notes/RUBY.md 3.1 and "WP0 layout", ruby_infra
2026-10-08; notes/EMERALD.md, emerald_wp0 2026-10-12).

    HOENN_VERSION=sapphire|ruby|emerald       (unset or empty = sapphire; anything else stops the build)

Every tool that differs per version asks this module; nothing else reads HOENN_VERSION. A Sapphire build reads no
`ruby/` or `emerald/` folder and none of the Ruby/Emerald rows below, so its ROM is byte-identical to a build without
this module.

Overlay rule: a `<version>/` folder (`ruby/`, `emerald/`) next to shared files. In a Ruby or Emerald build a file in
the version's folder with the same number (NNNN_ prefix of script/text/encounter/trainer sources, <number>- prefix of
sprite folders, <zone>.json of interiors) replaces the shared one, a new number is added, everything else is shared
(Sapphire's). The loaders' globs are not recursive, so Sapphire never sees these folders, and Ruby and Emerald never
see each other's. Sapphire has no overlay folder (OVERLAY is None): its files are the shared ones.

pokeruby's switch (Makefile `--defsym SAPPHIRE=1` / `RUBY=1`, constants/version.inc) maps to:
  POKERUBY              'SAPPHIRE' / 'RUBY': the symbol pokeruby's `.ifdef` tests (resolve_ifdef). Emerald reads
                        pokeruby's Sapphire branch wherever it still uses Sapphire's world (phase 0, notes/EMERALD.md)
  SUFFIX                wild-table label suffix in pokeruby src/data/wild_encounters.json (`*_Sapphire` / `*_Ruby`);
                        pokeemerald's labels have none ('' for Emerald: wild_label_ok)
  EXPAND                the version placeholders of pokeruby src/string_util.c (VERSION_DEPENDENT_PLACEHOLDER_LIST),
                        plus pokeemerald's own ({AQUA} {MAGMA} {ARCHIE} {MAXIE} {KYOGRE} {GROUDON}, charmap FD 08-0D)
  ASM_DEFINES           clang -D flags for field scripts: HOENN_SAPPHIRE, HOENN_RUBY or HOENN_EMERALD (+ HOENN_VERSION_ID
                        1 / 2 / 3, the decomps' GAME_VERSION / VERSION_EMERALD); src/include/hoenn_version.inc has the aliases
  DECOMP                the decomp the version's own data comes from: external/pokeruby (Sapphire, Ruby) or
                        external/pokeemerald (Emerald); decomp_map() names a Sapphire map in it (Emerald's renames)
"""
import glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))

VERSIONS = ('sapphire', 'ruby', 'emerald')
VERSION = (os.environ.get('HOENN_VERSION') or 'sapphire').strip().lower()
if VERSION not in VERSIONS:
    raise SystemExit(f'HOENN_VERSION={os.environ.get("HOENN_VERSION")!r}: must be one of {", ".join(VERSIONS)}')

def is_ruby():
    return VERSION == 'ruby'

def is_emerald():
    return VERSION == 'emerald'

RUBY = is_ruby()
EMERALD = is_emerald()
# the overlay folder of each version: Sapphire's files are the shared ones (no folder)
OVERLAYS = {'sapphire': None, 'ruby': 'ruby', 'emerald': 'emerald'}
OVERLAY = OVERLAYS[VERSION]

def has_overlay(version_=None):
    """True in a version with its own overlay folders (Ruby, Emerald): such a build reads `<version>/` over the
    shared files and its generators write only what differs from Sapphire's, never Sapphire's own files."""
    return OVERLAYS[version_ or VERSION] is not None

POKERUBY = 'RUBY' if RUBY else 'SAPPHIRE'
SUFFIX = {'sapphire': 'Sapphire', 'ruby': 'Ruby', 'emerald': ''}[VERSION]
NAME = {'sapphire': 'Sapphire', 'ruby': 'Ruby', 'emerald': 'Emerald'}[VERSION]
GAME_VERSION = {'sapphire': 1, 'ruby': 2, 'emerald': 3}[VERSION]   # pokeruby constants/version.inc GAME_VERSION;
                                                                     # pokeemerald include/constants/global.h VERSION_EMERALD
ASM_DEFINES = ['-D', 'HOENN_' + VERSION.upper(), '-D', f'HOENN_VERSION_ID={GAME_VERSION}']

# Game codes and names (metadata: nothing in the build reads them yet). GBA codes of the original games (the user's
# dumps: roms/sapphire_rev1_original.gba, roms/emerald_original.gba; notes/SETUP.md, DECISIONS 2026-10-11), the public
# names and release file stems (DECISIONS 2026-10-08, 2026-10-11: "Pokémon Emerald NDS", Pokemon_Emerald_NDS_v1).
GAME_CODE = {'sapphire': 'AXPE', 'ruby': 'AXVE', 'emerald': 'BPEE'}[VERSION]
PUBLIC_NAME = f'Pokémon {NAME} NDS'
RELEASE_STEM = f'Pokemon_{NAME}_NDS'

# The decomp each version's own data comes from (pokeruby builds Ruby and Sapphire; pokeemerald Emerald), and the
# user's own cartridge dump of that game (the music converter reads songs from it: b2tools/m4a.py reads Sapphire's,
# which also serves Ruby, whose songs are the same; Emerald's new songs are emerald_art's: TODO phase 5 in
# notes/EMERALD.md).
DECOMPS = {'sapphire': 'pokeruby', 'ruby': 'pokeruby', 'emerald': 'pokeemerald'}
GBA_DUMPS = {'sapphire': 'roms/sapphire_rev1_original.gba', 'ruby': 'roms/sapphire_rev1_original.gba',
             'emerald': 'roms/emerald_original.gba'}

def decomp(version_=None):
    """Absolute path of the version's decomp (external/pokeruby or external/pokeemerald)."""
    return os.path.join(ROOT, 'external', DECOMPS[version_ or VERSION])

DECOMP = decomp()

def gba_dump(version_=None):
    return os.path.join(ROOT, *GBA_DUMPS[version_ or VERSION].split('/'))

# pokeruby src/string_util.c VERSION_DEPENDENT_PLACEHOLDER_LIST (X(ph, ruby, sapphire)), in Sapphire's capitals as
# gen3text.convert(expand=True) uses them. Emerald: pokeruby's placeholders as Sapphire's (an Emerald build reads
# pokeruby only where it still plays Sapphire's world and story: phase 0) with VERSION EMERALD, and pokeemerald's own
# fixed placeholders (charmap.txt FD 07-0D, string_util.c ExpandPlaceholder_*: always these words in English).
_TEAMS = {'sapphire': {'VERSION': 'SAPPHIRE', 'EVIL_TEAM': 'AQUA', 'GOOD_TEAM': 'MAGMA', 'EVIL_LEADER': 'ARCHIE',
                       'GOOD_LEADER': 'MAXIE', 'EVIL_LEGENDARY': 'KYOGRE', 'GOOD_LEGENDARY': 'GROUDON'},
          'ruby':     {'VERSION': 'RUBY', 'EVIL_TEAM': 'MAGMA', 'GOOD_TEAM': 'AQUA', 'EVIL_LEADER': 'MAXIE',
                       'GOOD_LEADER': 'ARCHIE', 'EVIL_LEGENDARY': 'GROUDON', 'GOOD_LEGENDARY': 'KYOGRE'},
          'emerald':  {'VERSION': 'EMERALD', 'EVIL_TEAM': 'AQUA', 'GOOD_TEAM': 'MAGMA', 'EVIL_LEADER': 'ARCHIE',
                       'GOOD_LEADER': 'MAXIE', 'EVIL_LEGENDARY': 'KYOGRE', 'GOOD_LEGENDARY': 'GROUDON',
                       'AQUA': 'AQUA', 'MAGMA': 'MAGMA', 'ARCHIE': 'ARCHIE', 'MAXIE': 'MAXIE', 'KYOGRE': 'KYOGRE',
                       'GROUDON': 'GROUDON'}}
EXPAND_VERSION = _TEAMS[VERSION]

def expand_for(version):
    """The version placeholders of `version` (for tools that write both, e.g. a Ruby text layer made from Sapphire's)."""
    return dict(_TEAMS[version])

# ---------------------------------------------------------------------------------------------------- per-version tables
# One row per version; a tool reads TABLE[key] (the current version) or table(key, version).
_TABLE = {
    'sapphire': dict(
        # legendary of the story (pokeruby SPECIES_GROUDON_OR_KYOGRE) and the Southern Island one (SPECIES_LATIAS_OR_LATIOS)
        legendary='KYOGRE', legendary_species=382, legendary_model=4511,       # field model: a/2/0/8 record (RUBY.md 2)
        island='LATIOS', island_species=381, island_model=4510,
        roamer='LATIAS',                                                       # pokeruby ROAMER_SPECIES (the other one)
        orb='ITEM_BLUE_ORB',                                                   # ITEM_RED_OR_BLUE_ORB
        # title (patches/title.py, title_art.py): cry species, front still + normal palette in a/0/0/4 (species * 20,
        # + 18), the figure's top-left on the bottom screen, the bottom backdrop, the folder of logo.png + strip.png
        title=dict(species=382, still=7640, pal=7658, at=(80, 40), backdrop=(206, 234, 247), data='data/title'),
        # the crisis weather (patches/weather.py): Black 2 weather id while FLAG_SYS_WEATHER_CTRL is set
        weather=6,                                                             # thunderstorm (Kyogre's heavy rain)
    ),
    'ruby': dict(
        legendary='GROUDON', legendary_species=383, legendary_model=4512,
        island='LATIAS', island_species=380, island_model=4509,
        roamer='LATIOS',
        orb='ITEM_RED_ORB',
        # still/pal by the a/0/0/4 formula (383 * 20, + 18); `at` and `backdrop` are WP4's to tune (placeholders)
        title=dict(species=383, still=7660, pal=7678, at=(80, 40), backdrop=(247, 222, 206), data='data/title/ruby'),
        # Groudon's drought: Black 2 has no harsh-sun weather; the user chose id 3, the warm orange haze
        # (screenshots/ruby_infra/weather_all_ids.png, 2026-10-08). HOENN_LEGEND_WEATHER=<id> overrides for tests.
        weather=3,
    ),
    # Emerald (notes/EMERALD.md). Phase 0 plays Sapphire's world and story, so the story rows are Sapphire's until
    # phase 3/4 changes them (TODO EMERALD-3: Emerald wakes both legendaries, Kyogre at Seafloor Cavern and Groudon in
    # the Magma Hideout, and Sootopolis' crisis swaps rain and drought until Rayquaza (pokeemerald
    # data/maps/SootopolisCity/scripts.inc); Latias or Latios by the colour you tell Mom after the Hall of Fame, the other
    # one roams (pokeemerald data/maps/LittlerootTown_BrendansHouse_1F, src/roamer.c); Archie takes the Red Orb at
    # Mt. Pyre). Title: Rayquaza's cry and Black 2 still (384 * 20, + 18); logo.png + strip.png in data/title/emerald/
    # (emerald_art; until they exist patches/title.py shows Sapphire's logo); `at` and `backdrop` are emerald_art's.
    'emerald': dict(
        legendary='KYOGRE', legendary_species=382, legendary_model=4511,
        island='LATIOS', island_species=381, island_model=4510,
        roamer='LATIAS',
        orb='ITEM_BLUE_ORB',
        title=dict(species=384, still=7680, pal=7698, at=(80, 40), backdrop=(206, 234, 247), data='data/title/emerald'),
        weather=6,
    ),
}
TABLE = _TABLE[VERSION]

def table(key, version=None):
    return _TABLE[version or VERSION][key]

# ---------------------------------------------------------------------------------------------------- pokeruby sources
def resolve_ifdef(path, version=None):
    """Lines of a pokeruby .inc/.s with `.ifdef/.ifndef SAPPHIRE|RUBY ... .else ... .endif|.endc` resolved for the
    version (the symbol pokeruby defines: SAPPHIRE or RUBY; any other symbol counts as undefined; Emerald reads
    pokeruby's Sapphire branch). Other `.if` blocks are kept as written (their lines and their .else/.endif), as
    converter/gen_trainers.py's sapphire_lines did."""
    sym = 'RUBY' if (version or VERSION) == 'ruby' else 'SAPPHIRE'
    out, stack = [], []
    for line in open(path, encoding='utf-8', errors='replace'):
        s = line.strip()
        m = re.match(r'\.(ifdef|ifndef)\s+(\w+)', s)
        if m:
            cond = m.group(2) == sym
            stack.append(cond if m.group(1) == 'ifdef' else not cond); continue
        if re.match(r'\.if\w*\s', s): stack.append(None); continue
        if s == '.else':
            if stack and stack[-1] is not None: stack[-1] = not stack[-1]
            continue
        if s in ('.endif', '.endc'):
            if stack: stack.pop()
            continue
        if all(c is not False for c in stack): out.append(line)
    return out

def wild_label_ok(label, version=None):
    """True for a src/data/wild_encounters.json base_label of the version: pokeruby's `gRoute101_Sapphire` /
    `gRoute101_Ruby`; Emerald: every label (pokeemerald has one table per map, no suffix; its caller reads
    pokeemerald's file, version.decomp())."""
    v = version or VERSION
    if v == 'emerald': return True
    return label.endswith('Ruby' if v == 'ruby' else 'Sapphire')

# ---------------------------------------------------------------------------------------------------- overlay folders
def overlay_dir(d):
    """Where a generator writes a version's own files: d itself for Sapphire, d/ruby or d/emerald for the others."""
    return os.path.join(d, OVERLAY) if OVERLAY else d

def _key(path, key):
    return key(os.path.basename(path)) if key else os.path.basename(path)

def number_key(name):
    """'0381_trainer_msg_load.txt' -> 381, '152-tabitha' -> 152, '228.json' -> 228 (the overlay key of a name)."""
    m = re.match(r'(\d+)', name)
    return int(m.group(1)) if m else name

def overlay(d, pattern, key=number_key):
    """Sorted paths of glob(d/pattern), where (Ruby, Emerald) d/<version>/pattern replaces a shared file of the same key
    and adds the others. Sapphire: exactly sorted(glob(d/pattern)). Sorted by file name as the shared list is."""
    shared = sorted(glob.glob(os.path.join(d, pattern)))
    if not OVERLAY:
        return shared
    over = sorted(glob.glob(os.path.join(d, OVERLAY, pattern)))
    if not over:
        return shared
    keys = {}
    for p in over:
        k = _key(p, key)
        assert k not in keys, f'two {OVERLAY}/ files for {k}: {keys[k]} and {p}'
        keys[k] = p
    out = [p for p in shared if _key(p, key) not in keys] + over
    return sorted(out, key=lambda p: (os.path.basename(p), p))

def overlay_file(path):
    """d/<version>/name instead of d/name when it exists in a Ruby or Emerald build (data files replaced whole)."""
    if OVERLAY:
        alt = os.path.join(os.path.dirname(path), OVERLAY, os.path.basename(path))
        if os.path.exists(alt): return alt
    return path

def merge(base, over):
    """Deep merge of JSON values: dicts merge key by key (over wins), anything else is replaced by over."""
    if isinstance(base, dict) and isinstance(over, dict):
        out = dict(base)
        for k, v in over.items(): out[k] = merge(base[k], v) if k in base else v
        return out
    return over

def load_json(path):
    """json.load(path), deep-merged (Ruby, Emerald) with path's <version>/ twin when there is one: data/ruby/x.json
    holds only the keys that differ (e.g. a few trainer classes of data/hoenn_trainer_classes.json)."""
    data = json.load(open(path, encoding='utf-8'))
    if OVERLAY:
        alt = os.path.join(os.path.dirname(path), OVERLAY, os.path.basename(path))
        if os.path.exists(alt): data = merge(data, json.load(open(alt, encoding='utf-8')))
    return data

# ---------------------------------------------------------------------------------------------------- rooms per version
def versions_json():
    p = os.path.join(ROOT, 'data', 'versions.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}

def room_in_version(name, version=None):
    """False for a room that only other versions have (data/versions.json "rooms": {name: version or [versions]})."""
    only = versions_json().get('rooms', {}).get(name)
    if only is None: return True
    return (version or VERSION) in ([only] if isinstance(only, str) else only)

def door_alias(map_, warp, version_=None):
    """(map, Sapphire warp id) of the world.json door that plays outdoor warp (map_, warp) in the version: Ruby's
    Lilycove warp 14 (to Magma Hideout) is door 6's (data/versions.json doors "as_warp"). Else (map_, warp)."""
    for r in versions_json().get('doors', {}).get(version_ or VERSION, []):
        if (r['map'], r.get('as_warp')) == (map_, warp): return r['map'], r['id']
    # (Emerald, data/versions.json "door_plays": a door of another map plays the Sapphire warp: Emerald's Battle Tower door
    # is BattleFrontier_OutsideEast's warp 0, where Sapphire's is BattleTower_Outside's warp 0; same zone, same index)
    for r in versions_json().get('door_plays', {}).get(version_ or VERSION, []):
        if (r['map'], r['warp']) == (map_, warp): return tuple(r['door'])
    return map_, warp

def room_variant(room, version_=None):
    """The built room that plays `room` in the version (data/versions.json "room_variants": a cave built from Ruby's
    other layout, e.g. SeafloorCavern_Room9 -> SeafloorCavern_Room9_Ruby), else room."""
    return versions_json().get('room_variants', {}).get(version_ or VERSION, {}).get(room, room)

def variants(version_=None):
    """{room: the room variant that plays it} of the version (data/versions.json "room_variants"; Emerald's rooms built
    from pokeemerald's maps: b2tools/emerald_rooms.py)."""
    return dict(versions_json().get('room_variants', {}).get(version_ or VERSION, {}))

def version_object(o, version_=None):
    """A story object (data/story/*.json) as the version's build places it: its "<key>_<version>" keys replace "<key>"
    (patches/story.py version_keys: "at_emerald", "script_emerald" ...); None when "skip_<version>" leaves it out.
    For the checkers (emerald_rooms 2026-10-12)."""
    sfx = '_' + (version_ or VERSION)
    over = {k[:-len(sfx)]: v for k, v in o.items() if k.endswith(sfx) and len(k) > len(sfx)}
    o = dict(o, **over) if over else o
    return None if o.get('skip') else o

def decomp_map(name, version_=None):
    """The map folder in the version's decomp (decomp()) that plays Sapphire's map `name` (a pokeruby folder name):
    Emerald's renames (data/versions.json "maps" -> "emerald" -> "alias": Underwater1 -> Underwater_Route124,
    CaveOfOrigin_B4F -> CaveOfOrigin_B1F, ...), else `name`. None for a Sapphire map Emerald does not have ("gone")."""
    m = versions_json().get('maps', {}).get(version_ or VERSION, {})
    if name in m.get('gone', ()): return None
    return m.get('alias', {}).get(name, name)

# ---------------------------------------------------------------------------------------------------- outputs
def build_dir(default):
    """The ROM folder: HOENN_BUILD_DIR, else `default` (work/rom) for Sapphire and default + '_ruby' / '_emerald' for
    the others, so a Ruby or Emerald build never writes the Sapphire ROM."""
    d = os.environ.get('HOENN_BUILD_DIR')
    if d: return d
    return default + '_' + OVERLAY if OVERLAY else default

def plan_path(name):
    """A map's build plan (converter/plan_map.py): data/plans/<name>.json, or data/plans/emerald/<name>.json in Emerald's
    world (every Emerald plan is made from pokeemerald's map: converter/gba.py world_repo)."""
    d = os.path.join(ROOT, 'data', 'plans')
    return os.path.join(d, 'emerald' if EMERALD else '', f'{name}.json')

def world_dir():
    """The built world (b2tools/world.py's output): HOENN_WORLD_DIR, else work/world (Sapphire and Ruby share it) or
    work/world_emerald (Emerald's own world: Sapphire's maps in phase 0, Emerald's from phase 2, notes/EMERALD.md)."""
    return os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world_emerald' if EMERALD else 'world')

if __name__ == '__main__':
    print(VERSION, POKERUBY, SUFFIX, ASM_DEFINES)
