"""The following Pokémon (user 2026-11-01; ported from PearlB2's notes/FOLLOWERS.md "Porting to another B2 hack"; ours:
notes/FOLLOWERS.md). With YES to Birch's seventh question (flag FLAG_POKE_FOLLOWER), the first Pokémon of the party walks
behind the player, as in HeartGold/SoulSilver. build_rom.py adds this patch itself, last, when our C is on.

The code is the decomp's src/hoennb2/resident/follower.c (the module copied unchanged from PearlB2) with its hooks at
Black 2's own functions (`#if HOENNB2`: decomp_changes/). This patch puts its config in the resident section's pool and
the config's address in gFollowerConfig (without it: NULL, the game's behaviour, no follower):
- the flag, the talk script (global 10380, Script_1 of 1260_global_pokedex_rating.s, with #ifdef HOENN_FOLLOWERS; Black 2's
  Juniper script, unused in Hoenn), rooms and caves on, the work that gets the following Pokémon's party slot
  (VAR_FOLLOWER_SLOT, which the talk script reads), the Poké Ball shown when it is put away or sent out (Black 2's
  item-ball actor, code 110; no new pixels);
- no hack sheets: every species uses Black 2's walking Pokémon (ARCID_TPOKE), read by the C;
- the zones with no follower: OFF below;
- the 64 x 64 walking sheets (billboard size 2 in a/0/4/7), shown outdoors only;
- walking-Pokémon codes this build painted over (a record or sheet that differs from Black 2's), never shown.
Test builds (any HOENN_TEST_*) leave the config out unless HOENN_TEST_FOLLOW=1: the test drivers answer YES to every
question by mashing A, and no other test should get a follower.
"""
import os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import b2decomp, resident, sprites, version  # noqa: E402
from b2files import narc_entries, arc_path  # noqa: E402

ROOMS = 1                                   # every zone but the off list
SCRIPT = 10380                              # global: a/0/5/6 file 1260's Script_1 (see the docstring)
BALL_CODE = 110                             # Black 2's item ball (converter/gen_items.py)
TPOKE = range(0x1000, 0x126C)               # Black 2's walking Pokémon codes (sprites.obj_record)
PWT = [192, 193]                            # S/R's Battle Tower leads to Black 2's PWT (notes/BATTLE_TOWER.md)
# Rooms by name (data/hoenn_interiors.json and the version's own). Battle rooms and the like, by Pearl's rules: its Battle
# Tower block and Hall of Fame; here also every Battle Frontier facility and Battle Tent room, Trainer Hill above its
# entrance, the link rooms that are Hoenn's rooms, the contest stages and the underwater maps (Dive). Black 2's own Union
# Room, colosseums, Battle Subway and Entralink zones are its IsZoneNormal already. Scenes elsewhere use the hooks.
OFF = re.compile(r'^(BattleTower_(Lobby|Corridor|Elevator|BattleRoom)|EverGrandeCity_HallOfFame|'
                 r'SingleBattleColosseum|DoubleBattleColosseum|TradeCenter|RecordCorner|UnionRoom|'
                 r'BattleFrontier_Battle\w+|\w+_BattleTent\w+|TrainerHill_(?!Entrance)\w+|\w+_ContestHall|'
                 r'(\w+_)?Underwater\w*)$')
UIDS = (0xfb, 0xfc)                         # the module's actors (follower.h); saves keep a uid in 8 bits
_made = {}


def on():
    """The follower's config goes in this build: our C is on and it isn't another test's build."""
    if not b2decomp.c_on():
        return False
    test = [k for k in os.environ if k.startswith('HOENN_TEST_') and k != 'HOENN_TEST_FOLLOW' and os.environ[k]]
    return not test or os.environ.get('HOENN_TEST_FOLLOW') == '1'


def hoenn_id(name):
    m = re.search(rf'^#define\s+{name}\s+(0x[0-9A-Fa-f]+|\d+)', open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read(), re.M)
    assert m, f'{name} missing from src/include/hoenn.h (converter/gen_story_ids.py)'
    return int(m.group(1), 0)


def off_zones():
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    named = sorted((v['zone'], n) for n, v in rooms.items() if OFF.match(n) and v.get('zone') is not None)
    assert any(n == 'EverGrandeCity_HallOfFame' for _, n in named), 'no Hall of Fame among the rooms'
    return sorted({z for z, _ in named} | set(PWT)), [n for _, n in named]


def _check_uids(files):
    """No zone's person may share the module's uids (follower.h), also after a save's 8 bits."""
    import zones
    bad = []
    for i, e in enumerate(narc_entries(arc_path(files, 126))):
        if len(e) < 8:
            continue
        try:
            ents = zones.parse_entities(e)[0]
        except Exception:
            continue
        bad += [(i, n['uid']) for n in ents.get('npcs', []) if isinstance(n, dict) and n.get('uid', 0) & 0xff in UIDS]
    assert not bad, f'followers: people with the follower\'s uids (entity file, uid): {bad[:10]}'


def apply(files):
    if not on():
        return 'followers: off in this build (our C off, or a test build without HOENN_TEST_FOLLOW=1)'
    _check_uids(files)
    vanilla = sprites.ow_table(os.path.join(b2decomp.BASE, 'build', 'b2_us', 'files'))
    table = sprites.ow_table(files)
    sheets0 = narc_entries(arc_path(os.path.join(b2decomp.BASE, 'build', 'b2_us', 'files'), sprites.ARC_OW_SHEETS))
    sheets = narc_entries(arc_path(files, sprites.ARC_OW_SHEETS))
    never = [c for c in TPOKE if table[sprites.obj_record(c)] != vanilla[sprites.obj_record(c)]
             or sheets[table[sprites.obj_record(c)]['res1']] != sheets0[vanilla[sprites.obj_record(c)]['res1']]]
    huge = [c for c in TPOKE if c not in never and table[sprites.obj_record(c)]['billboardSize'] == 2]
    _made.update(huge=huge, never=never)
    return f'followers: {len(huge)} 64x64 codes outdoors only, never {never}'


def apply_code(code):
    if not on():
        return 'followers: no config (gFollowerConfig stays NULL)'
    import decomp_build
    slot = decomp_build.symbol('gFollowerConfig', code)
    if slot is None:
        raise SystemExit('followers: the decomp has no gFollowerConfig (src/hoennb2/resident/follower.c)')
    flag, work = hoenn_id('FLAG_POKE_FOLLOWER'), hoenn_id('VAR_FOLLOWER_SLOT')
    off, names = off_zones()
    huge, never = _made['huge'], _made['never']

    def build(base):
        head = struct.pack('<10H', flag, SCRIPT, ROOMS, 0, len(off), len(huge), len(never), work, BALL_CODE, 0)
        return head + struct.pack(f'<{len(off) + len(huge) + len(never)}H', *off, *huge, *never), {}

    base, end, _ = resident.install(code, build)
    assert resident.read(code, slot, 4) == bytes(4), f'gFollowerConfig at {slot:#x}: not NULL'
    resident.write(code, slot, struct.pack('<I', base))
    return (f'followers: config {end - base} B at {base:#x} (gFollowerConfig {slot:#x}): flag {flag}, slot work {work:#x}, '
            f'no follower in {len(off)} zones ({", ".join(names)}; PWT {PWT}), {len(huge)} 64x64 codes, never {never}, rooms on')
