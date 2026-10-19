"""Sapphire's trainers as Black 2 trainers (story groundwork, notes/STORY_PORTING.md "Trainers").

    python3 gen_trainers.py            (reads pokeruby + the Black 2 decomp; no ROM needed)

Black 2's trainer format, read from the decomp (external/pokebw2):
- a/0/9/1 (ARCID_TRDATA 91) entry N = trainer N's 20-byte record, a/0/9/2 (ARCID_TRPOKE 92) entry N = its party:
  include/asm/trainer.inc (Trainer / PartyMon / PartyEnd macros), docs/data.md "Trainers", data/trainers/*.s.
- Names: system text 382 (line N = trainer N, "\\c" = stored compressed); class names: 383 and 485 ("a ...").
- Messages: system text 381; a/0/8/9 file 0 = (u16 trainer, u16 type) records, record i = line i of text 381;
  a/0/9/0 file 0 = u16 per trainer: byte offset of its first record (TrainerMsg_Load, arm9 0x020305d8).
  Types (ov036 s0088_TrainerGetMessageTypes 0x021a68d0 + global script 1239): single trainer 0 intro / 2 after;
  double trainer, NPC script 3000+N: 3 intro / 5 after / 6 "you need two Pokémon"; second NPC of a pair (5000+N):
  7 / 9 / 10; 1 = the defeat line shown in battle (one per trainer).
- A trainer NPC = zone entity NPC with evType 1, param0 = sight range, script 3000+N (5000+N: second of a pair),
  run by global script file 1239 (talk) and its eye-contact script; defeat flag = N + 0x5f0
  (src/ov012/trainer_script.c), set by that global script.
- Prize money = trdata money * 4 * level of the last Pokémon (ov167 btl_calc.c:565) = Sapphire's base money
  (x2 for a double battle, as Sapphire doubles it: battle_script_commands.c:5505).
- Class -> battle sprite / sex / encounter BGM: arm9 TRAINER_CLASS_RESOURCES (0x02092394, 4 bytes per class);
  battle BGM group + pedestal: SPECIAL_TRAINER_CLASSES (0x020922bc, 29 x 3 bytes). b2tools/patches/trainers.py
  edits both (data/hoenn_trainer_classes.json).

Tate & Liza (SPLIT): Sapphire's one double-battle trainer becomes two Black 2 trainers fought together, each with
their own picture, the way Black 2 battles two trainers at once (global script 1239 L_124E: `CallTrainerBattle a, b`
with both trainers single-style -> BtlSetup_SetTrainer1v2, ov036 BtlSetup_SetTrainerLocal 0x021a1db4); scripts use
h_trainerbattle_two (src/include/hoenn_story.inc). The battle music and encounter effect come from the first trainer's
class (ov036 EventBattleCall_DecideEnvTrainer reads client 1 only).
Class names: Sapphire's, except where the user chose Black 2's (B2_CLASS_NAME: Cooltrainer -> "Ace Trainer").

Which Sapphire trainers: every trainer a Sapphire map script battles (Sapphire branch of the .ifdef SAPPHIRE
blocks and constants/version.inc aliases), plus the rematch tiers of gTrainerEyeTrainers (battle_setup.c).
Levels: data/level_scaling.json (converter/level_scaling.py). Parties with default moves get Sapphire's own
level-up moves (Gen 3 learnsets, GiveBoxMonInitialMoveset), so every battle has Sapphire's movesets.

Writes:
  data/hoenn_trainers.json          registry: Sapphire TRAINER_* -> Black 2 trainer id (FIXED once given; append-only)
  data/hoenn_trainer_data.json      generated: every converted trainer (class, name, party, texts, NPC objects)
  data/hoenn_trainer_classes.json   generated: class edits for the patch + the class/sprite review table
  data/hoenn_trainer_msgs.json      generated: (trainer, type) of each line of text 381, in order
  src/trainers/NNNN_<name>.s        generated: one per converted trainer, the decomp's trainer.inc macros
  src/text/system/0381_trainer_msg_load.txt, 0382_trainer_names.txt, 0383_trainer_class_names.txt,
  0485_trainer_class_names_with_article.txt   generated: Black 2's files with the Hoenn lines in place

Ruby (HOENN_VERSION=ruby python3 gen_trainers.py [--check]; notes/RUBY.md "WP0 layout", WP1): the same run on pokeruby's
Ruby branch (.ifdef RUBY, constants/version.inc), then ONLY what differs from the Sapphire files above is written, into the
ruby/ overlays, and nothing Sapphire's is touched (the registry is read only):
- each of the 28 version aliases (TRAINER_MT_CHIMNEY_GRUNT_1 = Matt 2 / Tabitha 2, TRAINER_HIDEOUT_1F_GRUNT = Grunt 1 /
  Grunt 28, ...) takes the Black 2 trainer id of its Sapphire twin: the scenes, zone scripts and defeat flags keep
  naming the Sapphire constant, and that id now holds the Ruby trainer (party, name, class, messages);
- src/trainers/ruby/NNNN_*.s            trainers whose record or party differs (Carvanha -> Numel, Sharpedo -> Camerupt,
                                        Zangoose -> Seviper, the admins' AI flags); the 7 identical grunts need none
- src/text/system/ruby/0381-0383, 0485  whole files (names Tabitha/Courtney/Maxie, "Team Magma"/"Magma Admin"/"Magma
                                        Leader", every grunt/admin/leader message with Ruby's words)
- data/ruby/hoenn_trainer_data.json     the 28 entries (under the Sapphire constant and under the Ruby one)
- data/ruby/hoenn_trainer_classes.json  class edits: Magma fronts 154/156/148 (admins keep 152/153: Tabitha/Courtney's
                                        art is in src/sprites/trainer/front/ruby/), names
a/0/8/9 and a/0/9/0 keep their records (same trainers, same message types: asserted), so hoenn_trainer_msgs.json is shared.
--check compares the generated files with the committed overlays and writes nothing. HOENN_GEN_OUT=<dir> writes the
overlay files there instead (dry run).

Emerald (HOENN_VERSION=emerald python3 gen_trainers.py [--check]; notes/EMERALD.md EMERALD-1, emerald_data 2026-10-12):
the same run on pokeemerald (load_trainers_emerald, its scripts, texts, maps, money table and class names; levels: Sapphire's
Exp. Share curve, data/level_scaling.json curve.table, see level_scaling.py's Emerald check), then only what differs from
the Sapphire files is written (install_emerald), into the emerald/ overlays:
- the 543 trainers Emerald's scripts battle first (no rematch tiers: decision 3A) + Steven as the Space Center partner
  (STEVEN_PARTNER) + Liza (SPLIT_EMERALD). Black 2 ids (emerald_ids, data/emerald/hoenn_trainers.json, FIXED once given):
  a trainer in a slot Emerald shares with Sapphire takes that Sapphire trainer's id (377: Sapphire's scenes, NPCs and
  defeat flags reach Emerald's trainer of that place); the 168 new ones take Sapphire's rematch-tier ids (no rematches in
  HoennB2), then never-given ids; 88 ids are left (55 + 33);
- pictures: PIC_EMERALD (pokeemerald names), EMERALD_SPRITE / EMERALD_CLASS: Juan, Champion Wallace, Steven, Team Magma
  on Black 2's other Plasma/Colress/N special classes beside Team Aqua's; every picture both games have keeps Sapphire's
  class;
- src/trainers/emerald/NNNN_*.s (records/parties that differ), src/text/system/emerald/0381-0383, 0485 (whole files),
  data/emerald/hoenn_trainer_data.json (by Emerald name and by the Sapphire name of the id), hoenn_trainer_classes.json,
  hoenn_trainer_msgs.json (Emerald's message records), src/include/hoenn_trainers_emerald.h (Emerald names for scripts).
"""
import os, re, sys, json, glob, collections, tempfile, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
B2 = os.path.join(ROOT, 'external', 'pokebw2')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import version                                                           # noqa: E402  (HOENN_VERSION)
from gen3text import convert                                            # noqa: E402
from level_scaling import load_aliases                                   # noqa: E402

def sapphire_lines(path):
    """Lines of an .inc with .ifdef/.ifndef SAPPHIRE resolved for the build's version (Sapphire unless
    HOENN_VERSION=ruby; other .if blocks: kept as written): b2tools/version.py resolve_ifdef, this function's old body."""
    return version.resolve_ifdef(path)

OUT = os.environ.get('HOENN_GEN_OUT') or ROOT      # dry runs: HOENN_GEN_OUT=<scratch dir> writes everything there
# Sapphire: GEN is OUT. Ruby: the whole set is generated into a scratch folder GEN and only the differences with the
# committed Sapphire files are installed into the ruby/ overlays under OUT (install_ruby); the registry is read only.
# Emerald: the same as Ruby (install_emerald), with its own registry data/emerald/hoenn_trainers.json (written) next to
# Sapphire's (read only).
GEN = (tempfile.mkdtemp(prefix=f'gen_trainers_{version.VERSION}_') if version.has_overlay() and __name__ == '__main__'
       else OUT)      # (imported, e.g. by level_scaling.py's Emerald check: no scratch folder)
REGISTRY = os.path.join(ROOT if version.is_ruby() else OUT, 'data', 'hoenn_trainers.json')
if version.is_emerald(): REGISTRY = os.path.join(ROOT, 'data', 'hoenn_trainers.json')
REGISTRY_EMERALD = os.path.join(OUT, 'data', 'emerald', 'hoenn_trainers.json')
OUT_DATA = os.path.join(GEN, 'data', 'hoenn_trainer_data.json')
OUT_CLASSES = os.path.join(GEN, 'data', 'hoenn_trainer_classes.json')
OUT_MSGS = os.path.join(GEN, 'data', 'hoenn_trainer_msgs.json')
OUT_SRC = os.path.join(GEN, 'src', 'trainers')
OUT_TEXT = os.path.join(GEN, 'src', 'text', 'system')

# ---- Black 2 trainer ids Hoenn may take ------------------------------------------------------------------------
# Defeat flag = id + 1520 (src/ov012/trainer_script.c). Survey of every flag Black 2 still touches once Unova is
# replaced (code of main + all overlays, all 1289 script files, zone entities; notes/STORY_PORTING.md "Ids"):
# - ids 529-556 have flags 2049-2076 = story flags of src/include/hoenn.h since the opening: never trainers. Story
#   flags are allocated outside 1520-2333 from now on (converter/gen_story_ids.py), so every other id is a slot;
# - resetRebattleTrainers clears the flags of 12 trainers every day (REBATTLE);
# - field gimmick 10 (overlay 99) reads the flags of ids 381-385 in zone 121, now FortreeCity_House1 (GIMMICK);
# - StadiumResetTrainerFlags (command 485, table a/2/0/6) clears 132 trainers' flags; only Unova stadium scripts run
#   it, but these ids are left out too (STADIUM), so nothing in Black 2 can ever clear a Hoenn defeat flag.
POOL = list(range(1, 529)) + list(range(557, 814))
REBATTLE = {0x5f, 0x60, 0xb7, 0xb8, 0xb9, 0xba, 0x128, 0x12b, 0x12e, 0x12f, 0x14d, 0x2f0}
GIMMICK = set(range(381, 386))
STADIUM = {i for a, b in ((1, 3), (7, 9), (13, 15), (17, 18), (20, 30), (48, 132), (227, 251)) for i in range(a, b + 1)}
NEVER = REBATTLE | GIMMICK | STADIUM

# ---- classes ----------------------------------------------------------------------------------------------------
# Sapphire trainer pic -> Black 2 battle sprite (stand-in art: Black 2's own; Hoenn art drawn so far: Brendan 0,
# May 1, Aqua grunts 149/150, Archie 151, Matt 152, Shelly 153). Review: data/hoenn_trainer_classes.json "review".
PIC_SPRITE = {
    'BRENDAN': 0, 'MAY': 1, 'LASS': 3, 'YOUNGSTER': 2, 'HIKER': 73, 'BEAUTY': 141, 'FISHERMAN': 29, 'LADY': 42,
    'RICH_BOY': 41, 'BLACK_BELT': 50, 'BATTLE_GIRL': 63, 'GENTLEMAN': 75, 'PARASOL_LADY': 64, 'PSYCHIC_M': 35,
    'PSYCHIC_F': 36, 'SCHOOL_KID_M': 4, 'SCHOOL_KID_F': 5, 'POKEFAN_M': 58, 'POKEFAN_F': 59, 'POKEMON_BREEDER_M': 17,
    'POKEMON_BREEDER_F': 18, 'POKEMON_RANGER_M': 24, 'POKEMON_RANGER_F': 25, 'COOL_TRAINER_M': 49,
    'COOL_TRAINER_F': 48, 'SWIMMER_M': 83, 'SWIMMER_F': 84, 'TWINS': 16, 'GUITARIST': 128,
    'AQUA_GRUNT_M': 149, 'AQUA_GRUNT_F': 150, 'ARCHIE': 151, 'AQUA_ADMIN_M': 152, 'AQUA_ADMIN_F': 153,
    # Ruby's Team Magma (WP1): the grunts/leader use the existing fronts 154/156/148; the admins use the slots Matt and
    # Shelly have in Sapphire, whose art is Tabitha's and Courtney's in the Ruby overlay (src/sprites/trainer/front/ruby)
    'MAGMA_GRUNT_M': 154, 'MAGMA_GRUNT_F': 156, 'MAXIE': 148, 'MAGMA_ADMIN_M': 152, 'MAGMA_ADMIN_F': 153,
    'ROXANNE': 118, 'BRAWLY': 119, 'WATTSON': 120, 'FLANNERY': 121, 'NORMAN': 122, 'WINONA': 123,
    'TATE_AND_LIZA': 124, 'LIZA': 125, 'WALLACE': 140, 'STEVEN': 139,     # LIZA: SPLIT's second picture
    'SIDNEY': 79, 'PHOEBE': 77, 'GLACIA': 80, 'DRAKE': 78,          # src/sprites/trainer/front/077-080 (over B2's E4)
    'WALLY': 127,                                                      # src/sprites/trainer/front/127-wally (over Hugh's)
    # Hoenn-only classes: the closest Black 2 picture (stand-ins, see the review table)
    'AROMA_LADY': 13, 'RUIN_MANIAC': 27, 'INTERVIEWER': 22, 'TUBER_F': 14, 'TUBER_M': 15, 'HEX_MANIAC': 179,
    'POKEMANIAC': 32, 'KINDLER': 56, 'CAMPER': 72, 'PICNICKER': 28, 'BUG_MANIAC': 51, 'BUG_CATCHER': 110,
    'EXPERT_M': 69, 'EXPERT_F': 70, 'CYCLING_TRIATHLETE_M': 89, 'CYCLING_TRIATHLETE_F': 90,
    'RUNNING_TRIATHLETE_M': 52, 'RUNNING_TRIATHLETE_F': 6, 'SWIMMING_TRIATHLETE_M': 83,
    'SWIMMING_TRIATHLETE_F': 84, 'DRAGON_TAMER': 100, 'BIRD_KEEPER': 109, 'NINJA_BOY': 15, 'SAILOR': 82,
    'COLLECTOR': 58, 'SR_AND_JR': 62, 'YOUNG_COUPLE': 68, 'OLD_COUPLE': 74, 'SIS_AND_BRO': 16,
}
# Black 2 classes to use as they are (same role, sprite and battle music), by Sapphire pic
KEEP_CLASS = {
    'BRENDAN': 0, 'MAY': 1, 'YOUNGSTER': 2, 'LASS': 3, 'SCHOOL_KID_M': 4, 'SCHOOL_KID_F': 5, 'TWINS': 16,
    'POKEMON_BREEDER_M': 17, 'POKEMON_BREEDER_F': 18, 'POKEMON_RANGER_M': 24, 'POKEMON_RANGER_F': 25,
    'FISHERMAN': 29, 'PSYCHIC_M': 35, 'PSYCHIC_F': 36, 'RICH_BOY': 41, 'LADY': 42, 'COOL_TRAINER_F': 49,
    'COOL_TRAINER_M': 50, 'BLACK_BELT': 51, 'POKEFAN_M': 59, 'POKEFAN_F': 60, 'BATTLE_GIRL': 64,
    'PARASOL_LADY': 65, 'HIKER': 74, 'GENTLEMAN': 76, 'SWIMMER_M': 84, 'SWIMMER_F': 85, 'GUITARIST': 146,
    'BEAUTY': 179, 'WALLY': 145,          # Hugh's class (the PWT shows Cilan's class 11); battle music: SPECIAL_GROUP
    # repurposed with their battle music kept (SPECIAL_TRAINER_CLASSES): the patch only changes sprite/sex
    'AQUA_GRUNT_M': 187, 'AQUA_GRUNT_F': 188, 'ARCHIE': 189, 'AQUA_ADMIN_F': 191, 'AQUA_ADMIN_M': 192,
    'MAGMA_GRUNT_M': 187, 'MAGMA_GRUNT_F': 188, 'MAXIE': 189, 'MAGMA_ADMIN_F': 191, 'MAGMA_ADMIN_M': 192,   # Ruby: same classes
    'ROXANNE': 112, 'BRAWLY': 113, 'FLANNERY': 114, 'WATTSON': 115, 'WINONA': 116, 'NORMAN': 117,
    'TATE_AND_LIZA': 118, 'WALLACE': 119, 'PHOEBE': 78, 'DRAKE': 79, 'SIDNEY': 80, 'GLACIA': 81, 'STEVEN': 193,
}
# The special classes' battle music and encounter effect (EventBattleCall_DecideEnvTrainer, ov036 0x021c618c): arm9
# SPECIAL_TRAINER_CLASSES (0x020922bc, 29 x {u8 class, u8 BGM group, u8 pedestal}), ov036 SPECIAL_TRAINER_BGM
# (0x021d28e4, u16 SEQ per group) and SPECIAL_TRAINER_ENCEFF (0x021d2900, u8 effect per entry). Black 2's effects of
# these entries are character cut-ins (Unova leaders 11-18, Elite Four 19-22, Hugh 10, Iris 23, Plasma 26, Ghetsis 27:
# portraits/logos of Black 2's people; the Elite Four ones hang outside the League): every Hoenn trainer of a special
# class gets effect 5 instead, the effect Black 2 gives Cynthia, Bianca and Cheren and every normal trainer outdoors.
SPECIAL_ENCEFF = 5
SPECIAL_BGM = {0: 0x4e1, 8: 0x4e2}   # leaders: SEQ_BGM_VS_RS_LEADER, champion: SEQ_BGM_VS_RS_CHAMP (Black 2's PWT Hoenn themes)
SPECIAL_GROUP = {145: 4,             # Wally: SEQ_BGM_VS_TRAINER (Sapphire plays the normal trainer theme)
                 191: 7}             # Shelly: the grunts' theme (Sapphire's admins and grunts share one)
# classes no Hoenn trainer keeps and no remaining Black 2 system needs: free to become Hoenn-only classes
SPARE_CLASSES = [20, 21, 22, 23, 37, 39, 47, 55, 56, 77, 82, 93, 94, 95, 96, 98, 99, 103, 104, 105, 106, 107, 108,
                 109, 110, 111, 156, 166, 228, 229, 230, 6, 7, 8, 9, 13, 14, 15, 26, 27, 28, 30, 31, 32, 33, 34]
# Emerald's seven Frontier Brains (frontier_core 2026-10-12, notes/FRONTIER.md 5): each sits on a spare class whose own
# picture holds the Brain's front (b2tools/sprite_emerald_frontier.py: class c shows picture c), named as Emerald names
# the class (pokeemerald src/data/text/trainer_class_names.h) with its sex; never given to another Emerald trainer. Their
# battle music (mus_vs_frontier_brain) is data/emerald/hoenn_music.json "classes".
FRONTIER_BRAINS = {9: ('Salon Maiden', 1), 7: ('Dome Ace', 0), 8: ('Palace Maven', 0), 34: ('Arena Tycoon', 1),
                   33: ('Factory Head', 0), 31: ('Pike Queen', 1), 30: ('Pyramid King', 0)}
SEX = {0: 'M', 1: 'F'}
# Sapphire classes that keep the Black 2 class's own name (user choice, notes/DECISIONS.md 2026-10-06)
B2_CLASS_NAME = {'COOL_TRAINER'}
# Sapphire trainers fought as two Black 2 trainers (see the docstring). Part 0 keeps the Sapphire registry name; the
# others get their own registry entry ("id"). party: the Sapphire Pokémon each one sends out (Tate: Solrock, Liza:
# Lunatone, as their Gen 6 remake splits them); the bag items and the prize are shared out evenly (the summed prize =
# Sapphire's); defeat_pages: the pages of Sapphire's defeat text each one says in battle (Black 2 shows the first
# trainer's defeat line, then the second's: ov167 0x021b6840/0x021b68ce), so the dialogue keeps Sapphire's order;
# the field lines (intro 0, after 2, "need two Pokémon" 6) stay with part 0. objects: the Sapphire object gfx of each.
SPLIT = {
    'TRAINER_TATE_AND_LIZA': [
        dict(alias='TRAINER_TATE', name='Tate', pic='TATE_AND_LIZA', party=['SPECIES_SOLROCK'], defeat_pages=(0, 1),
             gfx='OBJ_EVENT_GFX_TATE'),
        dict(id='TRAINER_LIZA', name='Liza', pic='LIZA', female=True, party=['SPECIES_LUNATONE'], defeat_pages=(1, None),
             gfx='OBJ_EVENT_GFX_LIZA'),
    ],
}
# Sapphire encounter music -> Black 2 eye-contact BGM (SEQ_BGM_EYE_01.. = 1114..; picked by the Black 2 classes
# that use each one: 01 youngster, 02 lass, 03 preschoolers/twins, 04 ace trainers, 05 roughneck/guitarist,
# 06 breeder F/swimmer F, 07 swimmer M/cyclists, 08 psychic/black belt, 09 scientists, 10 pokefans/backers,
# 11 hiker/fisherman/backpacker, 12 workers, 13 gentleman/socialite, NEO_PLASMA 1127)
EYE_BGM = {'MALE': 1114, 'FEMALE': 1115, 'GIRL': 1116, 'SUSPICIOUS': 1118, 'INTENSE': 1121, 'COOL': 1117,
           'AQUA': 1127, 'MAGMA': 1127, 'SWIMMER': 1120, 'TWINS': 1116, 'ELITE_FOUR': 1117, 'HIKER': 1124,
           'INTERVIEWER': 1123, 'RICH': 1126}
FEMALE_MUSIC = {'FEMALE', 'GIRL', 'TWINS'}

# Gen 3 AI script bits (pokeruby data/battle_ai_scripts.s BattleAIs) -> Black 2 AI_FLAG_* (include/constants/tr_ai.h)
AI_BITS = {0: 'AI_FLAG_BASIC', 1: 'AI_FLAG_EXPERT', 2: 'AI_FLAG_EVAL_ATTACK', 3: 'AI_FLAG_SETUP_FIRST_TURN',
           4: 'AI_FLAG_TARGET_HP', 5: 'AI_FLAG_FUSION_MOVES', 6: 'AI_FLAG_BATON_PASS', 8: 'AI_FLAG_CHECK_HP'}
ITEM_ALIAS = {'ITEM_PARALYZE_HEAL': 'ITEM_PARLYZ_HEAL', 'ITEM_THUNDER_STONE': 'ITEM_THUNDERSTONE'}
MOVE_ALIAS = {'MOVE_SELF_DESTRUCT': 'MOVE_SELFDESTRUCT', 'MOVE_SMOKESCREEN': 'MOVE_SMOKE_SCREEN'}

def defines(path, prefix):
    return {k: int(v, 0) for k, v in re.findall(rf'#define ({prefix}\w+)\s+(0x[0-9a-fA-F]+|\d+)\b', open(path).read())}

def text_lines(path):
    return open(path, encoding='utf-8').read().split('\n')

# ---- Sapphire data ----------------------------------------------------------------------------------------------
def load_parties():
    parties, cur, mon = {}, None, None
    for line in open(f'{RUBY}/src/data/trainer_parties.h', encoding='utf-8'):
        m = re.match(r'const struct (\w+) (gTrainerParty_\w+)\[\]', line)
        if m:
            cur = m.group(2); parties[cur] = []; continue
        if re.match(r'\s*\{\s*$', line) and cur:
            mon = {'iv': 0, 'level': 1, 'species': None, 'item': 'ITEM_NONE', 'moves': None}; parties[cur].append(mon)
        for key, pat in (('iv', r'\.iv = (\d+)'), ('level', r'\.level = (\d+)'), ('species', r'\.species = (\w+)'),
                         ('item', r'\.heldItem = (\w+)')):
            m = re.search(pat, line)
            if m: mon[key] = int(m.group(1)) if key in ('iv', 'level') else m.group(1)
        m = re.search(r'\.moves = (.*?)\s*$', line)
        if m: mon['moves'] = [x.strip() for x in m.group(1).rstrip(',').split(',')]
    return parties

def load_trainers(parties):
    out, cur = collections.OrderedDict(), None
    for line in open(f'{RUBY}/src/data/trainers_en.h', encoding='utf-8'):
        m = re.match(r'\s*\[(TRAINER_\w+)\] =', line)
        if m:
            cur = {'id': m.group(1)}; out[cur['id']] = cur; continue
        if cur is None: continue
        for key, pat in (('class', r'\.trainerClass = TRAINER_CLASS_(\w+)'), ('pic', r'\.trainerPic = TRAINER_PIC_(\w+)'),
                         ('music', r'\.encounterMusic_gender = (.*),'), ('name', r'\.trainerName = _\("(.*)"\)'),
                         ('items', r'\.items = \{(.*)\}'), ('double', r'\.doubleBattle = (\w+)'),
                         ('ai', r'\.aiFlags = (\w+)'), ('party', r'\.party = \{\.(\w+) = (\w+) \}')):
            m = re.search(pat, line)
            if not m: continue
            if key == 'items': cur[key] = [x.strip() for x in m.group(1).split(',')]
            elif key == 'double': cur[key] = m.group(1) == 'TRUE'
            elif key == 'ai': cur[key] = int(m.group(1), 0)
            elif key == 'party': cur['party_kind'] = m.group(1); cur['party'] = parties.get(m.group(2), [])
            elif key == 'music':
                mm = re.search(r'TRAINER_ENCOUNTER_MUSIC_(\w+)', m.group(1))
                cur['music'] = mm.group(1) if mm else 'MALE'
                cur['female'] = 'F_TRAINER_FEMALE' in m.group(1)
            else: cur[key] = m.group(1)
    return out

def load_class_names():
    src = open(f'{RUBY}/src/data/text/trainer_class_names_en.h', encoding='utf-8').read()
    names = re.findall(r'_\("(.*?)"\)', src)
    consts = re.findall(r'^\s*TRAINER_CLASS_(\w+),?\s*$', open(f'{RUBY}/include/constants/trainers.h').read(), re.M)
    return dict(zip(consts, names))

def load_texts(root=RUBY):
    """label -> raw Sapphire string, from every .inc/.s under data/ (as gen_map_content.ruby_scripts); root: the decomp
    (pokeemerald for Emerald)."""
    text = {}
    for path in sorted(glob.glob(f'{root}/data/**/*.inc', recursive=True) + glob.glob(f'{root}/data/**/*.s', recursive=True)):
        label = None
        for line in open(path, encoding='utf-8', errors='replace'):
            m = re.match(r'^(\w+):{1,2}', line)
            if m: label = m.group(1); continue
            m = re.match(r'\s*\.string\s+"(.*)"', line)
            if m and label:
                text[label] = text.get(label, '') + m.group(1)
                if m.group(1).endswith('$'): label = None
    return text

def load_scripts(alias, root=RUBY):
    """label -> (map or None, [command lines]) for every Sapphire script, Sapphire branch (root: the decomp; pokeemerald
    has no version branches)."""
    scripts = {}
    paths = sorted(glob.glob(f'{root}/data/maps/*/scripts.inc')) + sorted(p for p in glob.glob(f'{root}/data/scripts/*.inc') if not p.endswith('debug.inc'))
    for path in paths:
        mp = path.split('/')[-2] if '/maps/' in path else None
        cur = None
        for line in sapphire_lines(path):
            m = re.match(r'^(\w+):{1,2}', line)
            if m:
                cur = m.group(1); scripts[cur] = (mp, []); continue
            s = line.split('@')[0].strip()
            if cur and s: scripts[cur][1].append(s)
    return scripts

def battles_in(scripts, alias):
    """Every trainerbattle command: dict(label, map, kind, trainer, intro, defeat, cannot, after, cont)."""
    out = []
    for label, (mp, body) in scripts.items():
        for i, cmd in enumerate(body):
            m = re.match(r'(trainerbattle\w*)\s+(.*)', cmd)
            if not m or m.group(1) == 'trainerbattlebegin': continue
            kind, args = m.group(1), [a.strip() for a in m.group(2).split(',')]
            if kind == 'trainerbattle':        # raw form: TYPE, trainer, local id, pointers...
                typ = args[0]; args = args[1:2] + args[3:]
                kind = {'TRAINER_BATTLE_CONTINUE_SCRIPT': 'trainerbattle_single',
                        'TRAINER_BATTLE_CONTINUE_SCRIPT_NO_MUSIC': 'trainerbattle_single'}.get(typ, typ)
                if typ == 'TRAINER_BATTLE_PYRAMID': continue           # (pokeemerald: the Battle Pyramid's own trainers)
            t = alias.get(args[0], args[0])
            b = dict(label=label, map=mp, kind=kind, trainer=t, intro=None, defeat=None, cannot=None, after=None, cont=None)
            if kind == 'trainerbattle_no_intro': b['defeat'] = args[1]
            elif kind.startswith('TRAINER_BATTLE_SET_TRAINER'):        # pokeemerald's Space Center multi battle: the two
                b['kind'] = 'trainerbattle_multi'; b['defeat'] = args[2]   # opponents' (intro, defeat) for DoSpecialTrainerBattle
            elif kind in ('trainerbattle_single', 'trainerbattle_rematch'):
                b['intro'], b['defeat'] = args[1], args[2]
                if len(args) > 3: b['cont'] = args[3]
            elif kind in ('trainerbattle_double', 'trainerbattle_rematch_double'):
                b['intro'], b['defeat'], b['cannot'] = args[1], args[2], args[3]
                if len(args) > 4: b['cont'] = args[4]
            for later in body[i + 1:]:          # the text shown when you talk to it again after the battle
                mm = re.match(r'msgbox\s+(\w+)', later)
                if mm: b['after'] = mm.group(1); break
                if later.split()[0] in ('end', 'goto', 'trainerbattle_rematch', 'trainerbattle_rematch_double', 'release'): break
            if version.is_emerald():           # no Match Call (decision 3A): a continue script that only registers the
                if b['cont'] and 'Register' in b['cont']: b['cont'] = None     # trainer, and the rematch/register checks
                b['simple'] = b['cont'] is None and simple_trainer_body([c for c in body if not MATCH_CALL.match(c)])
            else:
                b['simple'] = b['cont'] is None and simple_trainer_body(body)
            out.append(b)
    return out

# pokeemerald's Match Call lines in a trainer's script (registration and rematch checks), left out with decision 3A
MATCH_CALL = re.compile(r'(setvar VAR_0x8004, TRAINER_\w+|specialvar VAR_RESULT, (IsTrainerRegistered|ShouldTryRematchBattle)'
                        r'|goto_if_eq VAR_RESULT, (TRUE|FALSE), \w*(Rematch|Register)\w*)$')

SIMPLE = {'trainerbattle_single', 'trainerbattle_double', 'msgbox', 'end', 'specialvar', 'compare', 'goto_if_eq',
          'goto_if', 'release', 'lock', 'faceplayer'}

def simple_trainer_body(body):
    """A script that only battles and then shows one line (rematch checks allowed): Black 2's global trainer
    script does all of it, so the NPC needs no zone script."""
    cmds = [c.split()[0] for c in body]
    if not set(cmds) <= SIMPLE: return False
    for c in body:
        if c.startswith('specialvar') and 'ShouldTryRematchBattle' not in c: return False
    return cmds.count('msgbox') <= 1

def learnsets(gen3_species):
    """Gen 3 species constant -> [(level, MOVE_X)]"""
    order = re.findall(r'^\s*(g\w+LevelUpLearnset),?\s*$', open(f'{RUBY}/src/data/pokemon/level_up_learnset_pointers.h').read(), re.M)
    # (the last entry, Chimecho's, has no comma: before 2026-10-12 it was missed; no Sapphire or Ruby trainer has one)
    sets, cur = {}, None
    for line in open(f'{RUBY}/src/data/pokemon/level_up_learnsets.h'):
        m = re.match(r'const u16 (g\w+LevelUpLearnset)\[\]', line)
        if m: cur = m.group(1); sets[cur] = []; continue
        m = re.search(r'LEVEL_UP_MOVE\(\s*(\d+),\s*(MOVE_\w+)\)', line)
        if m and cur: sets[cur].append((int(m.group(1)), m.group(2)))
    by_id = {v: k for k, v in gen3_species.items()}
    return {by_id[i]: sets[name] for i, name in enumerate(order) if i in by_id}

def default_moves(learnset, level):
    """pokeruby GiveBoxMonInitialMoveset: every move up to the level, the oldest dropped when four are known."""
    moves = []
    for lvl, mv in learnset:
        if lvl > level: break
        if mv in moves: continue
        if len(moves) == 4: moves.pop(0)
        moves.append(mv)
    return moves

# ---- Emerald data (pokeemerald, HOENN_VERSION=emerald; notes/EMERALD.md) ------------------------------------------
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')
# pokeemerald's renamed trainer classes -> pokeruby's names (the classes of PIC/KEEP tables above; the same people:
# checked on every trainer whose slot and name both decomps share)
CLASS_EMERALD = {'COOLTRAINER': 'COOL_TRAINER', 'RIVAL': 'POKEMON_TRAINER_3', 'PKMN_RANGER': 'POKEMON_RANGER',
                 'PKMN_BREEDER': 'POKEMON_BREEDER', 'PKMN_TRAINER_1': 'POKEMON_TRAINER_1'}
# pokeemerald include/data.h party macros -> pokeruby's union member names (load_trainers' party_kind)
PARTY_KIND = {'NO_ITEM_DEFAULT_MOVES': 'NoItemDefaultMoves', 'NO_ITEM_CUSTOM_MOVES': 'NoItemCustomMoves',
              'ITEM_DEFAULT_MOVES': 'ItemDefaultMoves', 'ITEM_CUSTOM_MOVES': 'ItemCustomMoves'}

def trainer_numbers(root):
    """{TRAINER_X: number} of a decomp's include/constants/opponents.h (both decomps number the same slots alike:
    Emerald reuses R/S's numbers, e.g. 265 = TRAINER_ROXANNE / TRAINER_ROXANNE_1)."""
    return {k: int(v) for k, v in re.findall(r'#define (TRAINER_\w+)\s+(\d+)\b', open(f'{root}/include/constants/opponents.h').read())}

def load_parties_emerald():
    """pokeemerald src/data/trainer_parties.h in load_parties' form (`.lvl` is pokeruby's `.level`, moves in braces)."""
    parties, cur, mon = {}, None, None
    for line in open(f'{EMERALD}/src/data/trainer_parties.h', encoding='utf-8'):
        m = re.match(r'static const struct (\w+) (sParty_\w+)\[\]', line)
        if m:
            cur = m.group(2); parties[cur] = []; continue
        if re.match(r'\s*\{\s*$', line) and cur:
            mon = {'iv': 0, 'level': 1, 'species': None, 'item': 'ITEM_NONE', 'moves': None}; parties[cur].append(mon)
        for key, pat in (('iv', r'\.iv = (\d+)'), ('level', r'\.lvl = (\d+)'), ('species', r'\.species = (\w+)'),
                         ('item', r'\.heldItem = (\w+)')):
            m = re.search(pat, line)
            if m: mon[key] = int(m.group(1)) if key in ('iv', 'level') else m.group(1)
        m = re.search(r'\.moves = \{(.*?)\}', line)
        if m: mon['moves'] = [x.strip() for x in m.group(1).split(',')]
    return parties

def load_trainers_emerald(parties):
    """pokeemerald src/data/trainers.h in load_trainers' form, keyed by Emerald's constant. aiFlags are pokeemerald's
    AI_SCRIPT_* names (include/constants/battle_ai.h; the same bits as pokeruby's numbers); trainerPic names are
    Emerald's (TRAINER_PIC_LEADER_ROXANNE where pokeruby says TRAINER_PIC_ROXANNE): 'pic' is the PIC_SPRITE name
    (PIC_EMERALD), 'pic_emerald' pokeemerald's."""
    bits = {k: 1 << int(v) for k, v in re.findall(r'#define (AI_SCRIPT_\w+)\s+\(1 << (\d+)\)',
                                                  open(f'{EMERALD}/include/constants/battle_ai.h').read())}
    out, cur = collections.OrderedDict(), None
    for line in open(f'{EMERALD}/src/data/trainers.h', encoding='utf-8'):
        m = re.match(r'\s*\[(TRAINER_\w+)\] =', line)
        if m:
            cur = {'id': m.group(1)}; out[cur['id']] = cur; continue
        if cur is None: continue
        for key, pat in (('class', r'\.trainerClass = TRAINER_CLASS_(\w+)'), ('pic', r'\.trainerPic = TRAINER_PIC_(\w+)'),
                         ('music', r'\.encounterMusic_gender = (.*),'), ('name', r'\.trainerName = _\("(.*)"\)'),
                         ('items', r'\.items = \{(.*)\}'), ('double', r'\.doubleBattle = (\w+)'),
                         ('ai', r'\.aiFlags = (.*),'), ('party', r'\.party = (\w+)\((\w+)\)')):
            m = re.search(pat, line)
            if not m: continue
            if key == 'items': cur[key] = [x.strip() for x in m.group(1).split(',') if x.strip()]
            elif key == 'double': cur[key] = m.group(1) == 'TRUE'
            elif key == 'ai': cur[key] = sum(bits[w.strip()] if w.strip() in bits else int(w.strip(), 0)
                                             for w in m.group(1).split('|'))
            elif key == 'party': cur['party_kind'] = PARTY_KIND[m.group(1)]; cur['party'] = parties.get(m.group(2), [])
            elif key == 'music':
                mm = re.search(r'TRAINER_ENCOUNTER_MUSIC_(\w+)', m.group(1))
                cur['music'] = mm.group(1) if mm else 'MALE'
                cur['female'] = 'F_TRAINER_FEMALE' in m.group(1)
            elif key == 'class': cur['class'] = CLASS_EMERALD.get(m.group(1), m.group(1)); cur['class_emerald'] = m.group(1)
            elif key == 'pic': cur['pic'] = PIC_EMERALD.get(m.group(1), m.group(1)); cur['pic_emerald'] = m.group(1)
            else: cur[key] = m.group(1)
    return out

# pokeemerald's trainer pictures -> the picture names of PIC_SPRITE / KEEP_CLASS (pokeruby's: the same art, plan 1.7: every
# R/S picture is pixel-identical in Emerald except Brendan/May, whose Emerald outfits are src/sprites/trainer/front/emerald/,
# and Wallace, a new Champion picture). The other names are the same in both decomps.
PIC_EMERALD = {'COOLTRAINER_M': 'COOL_TRAINER_M', 'COOLTRAINER_F': 'COOL_TRAINER_F', 'AQUA_LEADER_ARCHIE': 'ARCHIE',
               'MAGMA_LEADER_MAXIE': 'MAXIE', 'MAGMA_ADMIN': 'MAGMA_ADMIN_M', 'LEADER_ROXANNE': 'ROXANNE',
               'LEADER_BRAWLY': 'BRAWLY', 'LEADER_WATTSON': 'WATTSON', 'LEADER_FLANNERY': 'FLANNERY', 'LEADER_NORMAN': 'NORMAN',
               'LEADER_WINONA': 'WINONA', 'LEADER_TATE_AND_LIZA': 'TATE_AND_LIZA', 'LEADER_JUAN': 'JUAN',
               'ELITE_FOUR_SIDNEY': 'SIDNEY', 'ELITE_FOUR_PHOEBE': 'PHOEBE', 'ELITE_FOUR_GLACIA': 'GLACIA',
               'ELITE_FOUR_DRAKE': 'DRAKE', 'CHAMPION_WALLACE': 'CHAMPION_WALLACE'}
# Emerald's own pictures and classes (both teams are villains, Juan leads the 8th Gym, Wallace is the Champion, Steven
# battles as a "PKMN Trainer" in Meteor Falls and as your partner at the Space Center):
# - Juan: Sapphire's 8th-leader class 119 with Black 2's own Juan (battle sprite 126, RESEARCH_STORY_SPRITES.md);
#   Champion Wallace: the Champion class 193 with Black 2's Wallace (140, a stand-in for Emerald's new Champion art);
# - Team Magma beside Team Aqua (Aqua: Plasma's classes 187/188/189/191/192): Black 2's other Team Plasma / Colress / N
#   classes, all in arm9 SPECIAL_TRAINER_CLASSES (so they can get the Plasma battle music group, as Aqua's have): Maxie
#   186 (Colress, Team Plasma: group 9 = Archie's), Tabitha 195 (PKMN Trainer Colress), grunts 235 (PKMN Trainer Colress)
#   and 40 (PKMN Trainer N; group 7 = the grunts'). Colress and N battle only in Unova's story, which HoennB2 replaced.
#   They are edited like spare classes (sprite, sex, eye-contact music, name); Magma's fronts are the shared 154/156/148
#   (Ruby's art) and Tabitha's own slot 169 (Black 2's Brycen Jet of Pokéstar Studios, gone with Unova):
#   src/sprites/trainer/front/emerald/169-tabitha = Ruby's Tabitha drawn on 152's parts ("mcss_from": 152);
# - Steven: a spare class, battle sprite 139 (Black 2's Steven), Gen 3's "PKMN Trainer" name.
EMERALD_CLASS = {'JUAN': 119, 'CHAMPION_WALLACE': 193, 'MAXIE': 186, 'MAGMA_ADMIN_M': 195, 'MAGMA_GRUNT_M': 235,
                 'MAGMA_GRUNT_F': 40}
EMERALD_REPURPOSED = {'MAXIE', 'MAGMA_ADMIN_M', 'MAGMA_GRUNT_M', 'MAGMA_GRUNT_F'}
EMERALD_SPRITE = {'JUAN': 126, 'CHAMPION_WALLACE': 140, 'STEVEN': 139, 'MAGMA_ADMIN_M': 169}
EMERALD_GROUP = {186: 9, 195: 7, 235: 7, 40: 7}      # SPECIAL_TRAINER_BGM groups: 9 Archie's (Ghetsis), 7 the grunts'
# b2tools/patches/hoenn_music.py class_songs takes each class's Hoenn songs from pokeruby's trainers of a picture: Emerald's
# new pictures take those of the picture with the same songs (Emerald's rules, pokeemerald pokemon.c GetBattleBGM: the
# same as R/S): Juan a Gym Leader's (Wallace's), Champion Wallace the Champion's (Steven's), Steven (class RIVAL, not
# Wally) the rival's with male encounter music (Brendan's)
MUSIC_PIC_EMERALD = {'JUAN': 'WALLACE', 'CHAMPION_WALLACE': 'STEVEN', 'STEVEN': 'BRENDAN'}
# Tate & Liza (SPLIT): Emerald's pair has four Pokémon (Claydol, Xatu, Lunatone, Solrock); each twin takes one lead and
# their own Pokémon of Sapphire's split (Tate: Claydol + Solrock, Liza: Xatu + Lunatone), so the battle opens with
# Emerald's two leads (Claydol and Xatu) and the defeat pages are shared out as in Sapphire.
SPLIT_EMERALD = {
    'TRAINER_TATE_AND_LIZA_1': [
        dict(SPLIT['TRAINER_TATE_AND_LIZA'][0], party=['SPECIES_CLAYDOL', 'SPECIES_SOLROCK']),
        dict(SPLIT['TRAINER_TATE_AND_LIZA'][1], party=['SPECIES_XATU', 'SPECIES_LUNATONE']),
    ],
}
# Steven at the Space Center (pokeemerald battle_tower.c sStevenMons, FillPartnerParty: not in gTrainers): a trainer of
# its own for Black 2's multi battle (CallTrainerMultiBattle takes a partner trainer id: emerald_mech, EMERALD-4).
# Max IVs (fixedIV 31) -> difficulty 255; natures and EVs have no place in Black 2's party format.
STEVEN_PARTNER = 'TRAINER_STEVEN_PARTNER'

def steven_partner():
    src = open(f'{EMERALD}/src/battle_tower.c', encoding='utf-8').read()
    blk = src[src.index('sStevenMons[MULTI_PARTY_SIZE] ='):]
    blk = blk[:blk.index('};')]
    party = [dict(iv=255, level=int(l), species=sp, item='ITEM_NONE', moves=[x.strip() for x in mv.split(',')])
             for sp, l, mv in re.findall(r'\.species = (\w+),.*?\.level = (\d+),.*?\.moves = \{(.*?)\}', blk, re.S)]
    assert len(party) == 3, party
    return {'id': STEVEN_PARTNER, 'class': 'POKEMON_TRAINER_3', 'class_emerald': 'RIVAL', 'pic': 'STEVEN',
            'pic_emerald': 'STEVEN', 'music': 'MALE', 'female': False, 'name': 'STEVEN', 'items': [], 'double': False,
            'ai': 0b111, 'party_kind': 'NoItemCustomMoves', 'party': party}

# Emerald's rematches (emerald_rematch 2026-10-18, notes/EMERALD_REMATCH.md): pokeemerald src/battle_setup.c gRematchTable,
# one row per trainer who rematches: the first battle's trainer, then up to four rematch tiers ("tier 2-5": the row's
# entries 1-4, repeats dropped). The tiers are not Black 2 trainers (no ids: Black 2's table is full); each tier's record
# and party are "rematch slots" (data/emerald/hoenn_rematch.json, src/trainers/emerald_rematch/) that
# b2tools/patches/emerald_rematch.py installs and loads in place of the first battle's record while the rematch is
# fought (the first battle's id, name, picture and NPC stay). Messages of the first battle's trainer: REMATCH_MSG.
# Rows and slots are only ever appended (saves keep a bit per row): gRematchTable's order, then REMATCH_LATE in the
# order they were added. Left out: the Elite Four and Wallace (their rows have no tiers).
REMATCH_LATE = ['REMATCH_WALLY_VR']        # added later (emerald_rematch 2026-10-18, "add the wally battles too")
# gym: 1-8 the Gym Leaders (after the Hall of Fame, tiers in turn); 9 + n post-game trainers with their own progress
# (Wally at Victory Road's exit: after the Hall of Fame, tiers in turn); 0 route trainers (tier by badges)
REMATCH_GYM = {'REMATCH_ROXANNE': 1, 'REMATCH_BRAWLY': 2, 'REMATCH_WATTSON': 3, 'REMATCH_FLANNERY': 4,
               'REMATCH_NORMAN': 5, 'REMATCH_WINONA': 6, 'REMATCH_TATE_AND_LIZA': 7, 'REMATCH_JUAN': 8,
               'REMATCH_WALLY_VR': 9}
# message types of a rematch trainer (a/0/8/9 records of the first battle's id; Black 2's own types stop at 24):
# 100 intro (shown before YES/NO), 101 after the rematch, 102 "you need two Pokémon"; 104-106 the same for the second
# NPC of a pair (Black 2's 5000 + id NPC); 103 the in-battle defeat line (both NPCs' lines joined, as type 1)
REMATCH_MSG = dict(intro=100, post=101, cannot=102, defeat=103, intro2=104, post2=105, cannot2=106)

def rematch_rows_emerald():
    """[{row, first, tiers [TRAINER_*], gym (REMATCH_GYM, 0 = a route trainer), map}]: gRematchTable's order, then
    REMATCH_LATE."""
    src = open(f'{EMERALD}/src/battle_setup.c', encoding='utf-8').read()
    out = []
    for name, args in re.findall(r'\[(REMATCH_\w+)\] = REMATCH\(([^)]*)\)', src):
        a = [x.strip() for x in args.split(',')]
        first, tiers = a[0], []
        for t in a[1:5]:
            if t != first and t not in tiers: tiers.append(t)
        if tiers:
            out.append(dict(row=name, first=first, tiers=tiers, gym=REMATCH_GYM.get(name, 0), map=a[5]))
    out = [r for r in out if r['row'] not in REMATCH_LATE] + [r for n in REMATCH_LATE for r in out if r['row'] == n]
    assert len(out) == 73 and sum(1 for r in out if 1 <= r['gym'] <= 8) == 8 and out[-1]['row'] == 'REMATCH_WALLY_VR', len(out)
    return out

def load_class_names_emerald():
    """pokeemerald src/data/text/trainer_class_names.h, by the pokeruby class names (CLASS_EMERALD)."""
    src = open(f'{EMERALD}/src/data/text/trainer_class_names.h', encoding='utf-8').read()
    return {CLASS_EMERALD.get(c, c): n for c, n in re.findall(r'\[TRAINER_CLASS_(\w+)\] = _\("(.*?)"\)', src)}

def load_money_emerald():
    """pokeemerald src/battle_main.c gTrainerMoneyTable (pokeruby's data/trainer_money.inc), by pokeruby class names."""
    src = open(f'{EMERALD}/src/battle_main.c', encoding='utf-8').read()
    return {CLASS_EMERALD.get(c, c): int(v) for c, v in re.findall(r'\{TRAINER_CLASS_(\w+), (\d+)\}', src)}

def emerald_maps():
    """(Emerald map folder -> the HoennB2 (Sapphire) map it plays, the maps this build has: outdoor zones and rooms):
    data/versions.json "maps" -> "emerald" "alias" reversed; Emerald-only maps play themselves (none is built yet), the 3
    whose folder name is another Sapphire map ("name_clash": MagmaHideout_1F, SafariZone_Northeast/Southeast) are called
    <name>_Emerald (notes/EMERALD.md EMERALD-2)."""
    m = version.versions_json().get('maps', {}).get('emerald', {})
    back = {e: s for s, e in m.get('alias', {}).items()}
    clash = set(m.get('name_clash', ()))
    def hoenn(e): return e + '_Emerald' if e in clash else back.get(e, e)      # (name_clash: EMERALD.md's naming)
    built = set(json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'])
    built |= {r for r, v in json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms'].items()
              if v.get('status') not in ('link',)}
    return hoenn, built

def emerald_ids(wanted, em, sap_reg, sap_data):
    """Emerald's registry (data/emerald/hoenn_trainers.json): Emerald TRAINER_* -> Black 2 trainer id.
    1. a trainer in a slot Emerald shares with Sapphire (both decomps number the slots alike) takes the Black 2 id of the
       Sapphire trainer of that number, so Sapphire's scenes, NPCs and defeat flags reach Emerald's trainer there;
    2. an id given before stays (FIXED once given, as Sapphire's registry);
    3. the others (Emerald's new trainers) take ids no Emerald trainer uses, first the 223 ids of Sapphire's rematch
       tiers (data/hoenn_trainer_data.json rematch_of: no rematches in HoennB2, none is placed or battled; decision 3A),
       then the never-given pool ids (gen_trainers POOL minus NEVER), lowest first.
    Returns (ids, report dict)."""
    rn, en = trainer_numbers(RUBY), trainer_numbers(EMERALD)
    r_by_num = {v: k for k, v in rn.items()}
    old = json.load(open(REGISTRY_EMERALD)).get('trainers', {}) if os.path.exists(REGISTRY_EMERALD) else {}
    ids, how = {}, {}
    for t in wanted:
        s = r_by_num.get(en.get(t))
        if t == 'TRAINER_LIZA': s = t                                                    # (SPLIT's second twin)
        if s in sap_reg:
            ids[t] = sap_reg[s]; how[t] = 'slot'
            if t in old and old[t] != ids[t]: raise SystemExit(f'Emerald registry: {t} had id {old[t]}, its slot now gives {ids[t]}')
        elif t in old: ids[t] = old[t]; how[t] = 'new'
    used = set(ids.values())
    rematch = sorted(sap_reg[t] for t, d in sap_data.items() if d.get('rematch_of') and t in sap_reg)
    never = [i for i in POOL if i not in set(sap_reg.values()) and i not in NEVER]
    free = [i for i in rematch + never if i not in used]
    for t in wanted:
        if t in ids: continue
        if not free: raise SystemExit(f'Emerald: no free Black 2 trainer id left for {t}')
        ids[t] = free.pop(0); how[t] = 'new'
    dup = [i for i, n in collections.Counter(ids.values()).items() if n > 1]
    assert not dup, f'Emerald registry: ids given twice {dup}'
    return ids, dict(how=how, left=len(free), left_rematch=sum(1 for i in free if i in set(rematch)),
                     left_never=sum(1 for i in free if i in set(never)))

# ---- main ---------------------------------------------------------------------------------------------------------
def main():
    ruby, emerald = version.is_ruby(), version.is_emerald()
    split = SPLIT_EMERALD if emerald else SPLIT
    twin = {}          # Ruby: the Ruby trainer of each alias -> the Sapphire trainer whose Black 2 id it takes
    if emerald:        # pokeemerald (no version aliases); levels: Sapphire's Exp. Share curve (level_scaling.py Emerald)
        alias = {}
        trainers = load_trainers_emerald(load_parties_emerald())
        trainers[STEVEN_PARTNER] = steven_partner()
        class_names3 = load_class_names_emerald()
        texts = load_texts(EMERALD)
        scripts = load_scripts(alias, EMERALD)
        battles = battles_in(scripts, alias)
        curve = {int(k): v for k, v in json.load(open(os.path.join(ROOT, 'data', 'level_scaling.json')))['curve']['table'].items()}
        scaling = {t: dict(sapphire_levels=[m['level'] for m in d.get('party', [])],
                           new_levels=[curve[m['level']] for m in d.get('party', [])]) for t, d in trainers.items()}
    else:
        alias = load_aliases()
        if ruby:
            sap_alias = load_aliases('sapphire')
            assert set(sap_alias) == set(alias), sorted(set(sap_alias) ^ set(alias))
            twin = {alias[k]: sap_alias[k] for k in alias}
            assert len(twin) == len(alias) == 28, len(twin)
        trainers = load_trainers(load_parties())
        class_names3 = load_class_names()
        texts = load_texts()
        scripts = load_scripts(alias)
        battles = battles_in(scripts, alias)
        scaling = {t['id']: t for t in json.load(open(os.path.join(ROOT, 'data', 'level_scaling.json')))['trainers']}

    b2_species = defines(f'{B2}/include/constants/species.h', 'SPECIES_')
    b2_moves = defines(f'{B2}/include/constants/moves.h', 'MOVE_')
    b2_items = defines(f'{B2}/include/constants/items.h', 'ITEM_')
    g3_species = defines(f'{RUBY}/include/constants/species.h', 'SPECIES_')
    sets = learnsets(g3_species)

    # which trainers: battled by a Sapphire script, then the rematch tiers of those
    first = []
    for b in battles:
        if b['trainer'] not in first and 'rematch' not in b['kind']: first.append(b['trainer'])
    eye = re.findall(r'\{\s*\{(TRAINER_\w+(?:,\s*TRAINER_\w+)*)\}', open(f'{RUBY}/src/battle_setup.c').read())
    if emerald: eye = []          # no rematches (decision 3A)
    rematch = []
    for row in eye:
        tiers = [t.strip() for t in row.split(',')]
        if tiers[0] in first:
            rematch += [t for t in tiers[1:] if t != 'TRAINER_NONE' and t not in first and t not in rematch]
    wanted = [t for t in trainers if t in first or t in rematch]        # Sapphire's own order
    if emerald: wanted.append(STEVEN_PARTNER)
    if ruby:      # the Ruby twins take their Sapphire twin's place in the order (spare classes are handed out in this order)
        pos = {t: i for i, t in enumerate(trainers)}
        wanted.sort(key=lambda t: pos[twin.get(t, t)])

    # registry (fixed once given)
    reg = json.load(open(REGISTRY)) if os.path.exists(REGISTRY) else {}
    ids = reg.get('trainers', {})
    if emerald:   # Emerald's own registry (emerald_ids); Sapphire's is read only
        sap_data = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json')))['trainers']
        ids, id_report = emerald_ids(wanted + [p['id'] for t0, parts in split.items() if t0 in wanted for p in parts[1:]],
                                     trainers, dict(ids), sap_data)
    if ruby:      # read only: each Ruby alias plays the Black 2 trainer of its Sapphire twin (RUBY.md 3.2 "Trainers")
        for t, s0 in twin.items():
            if s0 not in ids: raise SystemExit(f'Ruby trainer {t}: its Sapphire twin {s0} has no id in data/hoenn_trainers.json')
            ids[t] = ids[s0]
    used = set(ids.values())
    free = [i for i in POOL if i not in used and i not in NEVER]
    for t in wanted + [p['id'] for t0, parts in split.items() if t0 in wanted for p in parts[1:]]:
        if t not in ids:
            if ruby: raise SystemExit(f'Ruby build: {t} has no Black 2 trainer id (data/hoenn_trainers.json is Sapphire\'s; '
                                      f'run the Sapphire generator first)')
            if not free: raise SystemExit(f'no free Black 2 trainer id left for {t}')
            ids[t] = free.pop(0)
    if ruby:      # the Ruby set is the Sapphire set with the 28 twins swapped (same ids, same message record list)
        expect = (set(ids) - set(twin) - set(twin.values())) | set(twin)
        got = {t for t in wanted} | {p['id'] for t0, parts in SPLIT.items() if t0 in wanted for p in parts[1:]}
        assert got == expect, ('Ruby trainer set differs from Sapphire\'s', sorted(got ^ expect)[:10])
    reg_doc = {'_doc': 'Sapphire TRAINER_* -> Black 2 trainer id (a/0/9/1-2 entry, script 3000+id, defeat flag id+1520). '
                   'FIXED once given, append-only: savestates, scripts and flags depend on these numbers. Written by '
                   'converter/gen_trainers.py; ids come from its POOL (1-528, 557-813 minus the ids Black 2 code or scripts '
                   'reset or read: daily rebattle, gimmick 381-385, stadium resets), so no defeat flag lands on a story '
                   'flag (2049-2076) or on a flag Black 2 touches.',
           'trainers': dict(sorted(ids.items(), key=lambda kv: kv[1]))}
    reg = reg_doc
    hdr = os.path.join(GEN, 'src', 'include', 'hoenn_trainers.h')     # Sapphire names for scripts (h_trainerbattle)
    os.makedirs(os.path.join(GEN, 'data'), exist_ok=True)
    os.makedirs(os.path.dirname(hdr), exist_ok=True)
    if not version.has_overlay(): json.dump(reg, open(REGISTRY, 'w'), indent=1)   # (Ruby, Emerald: Sapphire's stays)
    open(hdr, 'w').write('// Sapphire trainer names -> Black 2 trainer ids (data/hoenn_trainers.json). GENERATED by '
                         'converter/gen_trainers.py.\n// Defeat flag = id + 1520; eye-contact NPC script = 3000 + id.\n'
                         '#pragma once\n' + ''.join(f'#define {t:<36} {i}\n' for t, i in reg['trainers'].items()) +
                         ''.join(f'#define {p["alias"]:<36} {t0}   // SPLIT: first of two trainers\n'
                                 for t0, parts in split.items() for p in parts if 'alias' in p))

    # ---- classes: Sapphire pic -> Black 2 class (kept, or a spare one repurposed by the patch)
    b2_class_names = text_lines(f'{B2}/data/text/system/0383_trainer_class_names.txt')
    b2_class_art = text_lines(f'{B2}/data/text/system/0485_trainer_class_names_with_article.txt')
    arm9 = open(f'{B2}/build/b2_us/build/arm9.bin', 'rb').read()
    def resources(c):
        o = 0x02092394 - 0x02004000 + 4 * c
        return arm9[o], arm9[o + 1], int.from_bytes(arm9[o + 2:o + 4], 'little')
    spare = list(SPARE_CLASSES)
    keep_class, sprite_of, groups = KEEP_CLASS, PIC_SPRITE, SPECIAL_GROUP
    if emerald:   # Sapphire's class for every picture both games have (its edits stay as they are); Emerald's own
        sap_review = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json')))['review']
        prefer = {r['sapphire_pic']: r['b2_class'] for r in sap_review if r['sapphire_pic'] != 'STEVEN'}
        spare = [c for c in SPARE_CLASSES if c not in {r['b2_class'] for r in sap_review} and c not in FRONTIER_BRAINS]
        keep_class = {k: v for k, v in KEEP_CLASS.items() if k != 'STEVEN' and k not in EMERALD_REPURPOSED}
        keep_class.update({k: v for k, v in EMERALD_CLASS.items() if k not in EMERALD_REPURPOSED})
        sprite_of = {**PIC_SPRITE, **EMERALD_SPRITE}
        groups = {**SPECIAL_GROUP, **EMERALD_GROUP}
    pic_class, class_edit, review = {}, {}, []
    pics = collections.OrderedDict()
    for t in wanted:
        tr = trainers[t]; pics.setdefault(tr['pic'], []).append(tr)
    for t, parts in split.items():        # (after every Sapphire picture: the spare classes already given stay put)
        for p in parts:
            if t in wanted and p['pic'] not in pics:
                pics[p['pic']] = [dict(trainers[t], id=p.get('id', t), pic=p['pic'], female=p.get('female', False))]
    for pic, trs in pics.items():
        cls3 = collections.Counter(tr['class'] for tr in trs).most_common(1)[0][0]
        music = collections.Counter(tr['music'] for tr in trs).most_common(1)[0][0]
        sex = 1 if sum(1 for tr in trs if tr.get('female')) * 2 > len(trs) else 0   # F_TRAINER_FEMALE (Gen 3's gender bit)
        name3, _ = convert(class_names3[cls3].replace('{PKMN}', '\x01'))
        name3 = name3.replace('\x01', '⒆⒇').replace('♂', ' ⑭').replace('♀', ' ⑮').replace('  ', ' ')
        name3 = re.sub(r'\bAnd\b', 'and', name3)                       # "Sr. and Jr.", "Sis and Bro"
        sprite = sprite_of.get(pic)
        if sprite is None: raise SystemExit(f'no Black 2 sprite chosen for Sapphire pic {pic} ({[tr["id"] for tr in trs][:3]})')
        if emerald and pic in EMERALD_CLASS:
            c = EMERALD_CLASS[pic]
        elif emerald and pic in prefer:
            c = prefer[pic]
        elif pic in keep_class:
            c = keep_class[pic]
        else:
            c = spare.pop(0)
        old_sprite, old_sex, old_eye = resources(c)
        edit = {}
        if old_sprite != sprite: edit['sprite'] = sprite
        keep_sex = pic in keep_class and c not in (112, 113, 114, 115, 116, 117, 118, 119, 78, 79, 80, 81, 189, 191, 192, 193, 145)
        if not keep_sex and old_sex != sex: edit['sex'] = sex
        if pic not in keep_class: edit['eye_bgm'] = EYE_BGM.get(music, 1114)
        b2_name = b2_class_names[c]
        same = re.sub(r'[\s⑭⑮]', '', b2_name).lower() == re.sub(r'[\s⑭⑮]', '', name3).lower() or cls3 in B2_CLASS_NAME
        if not same:
            edit['name'] = name3
            art = 'an' if name3[:1].upper() in 'AEIOU' else 'a'
            edit['name_with_article'] = f'{art} {name3}'
        pic_class[pic] = c
        if edit: class_edit[c] = edit
        review.append(dict(sapphire_pic=pic, sapphire_class=cls3, name=edit.get('name', b2_name), b2_class=c,
                           b2_class_was=b2_name, sprite=sprite, sprite_was=old_sprite, sex=SEX[edit.get('sex', old_sex)],
                           eye_bgm=edit.get('eye_bgm', old_eye), trainers=len(trs),
                           how='kept' if not edit else ('repurposed spare class' if pic not in keep_class else 'kept class, edited'),
                           **({'emerald_pics': sorted({tr.get('pic_emerald', pic) for tr in trs})} if emerald else {}),
                           **({'music_pic': MUSIC_PIC_EMERALD[pic]} if emerald and pic in MUSIC_PIC_EMERALD else {})))
    # special classes (battle music group + encounter effect): every one a Hoenn trainer uses
    spec_off = 0x020922bc - 0x02004000
    special_classes = {arm9[spec_off + 3 * i]: i for i in range(29)}
    special = {}
    for c in sorted(set(pic_class.values())):
        if c in special_classes:
            e = {'entry': special_classes[c], 'enceff': SPECIAL_ENCEFF}
            if c in groups: e['bgm_group'] = groups[c]
            special[str(c)] = e

    # ---- trainer records, parties, names, messages
    species_alias = {}
    out_trainers, report = {}, collections.Counter()
    unknown = collections.Counter()
    def b2c(table, name, kind):
        n = {'item': ITEM_ALIAS, 'move': MOVE_ALIAS}.get(kind, {}).get(name, name)
        if n not in table: unknown[f'{kind} {name}'] += 1; return None
        return n
    by_trainer = collections.defaultdict(list)
    for b in battles: by_trainer[b['trainer']].append(b)
    root = EMERALD if emerald else RUBY
    if emerald:
        money = load_money_emerald()
        hoenn_map, built = emerald_maps()
    else:
        money = {cls: int(v) for cls, v in re.findall(r'TRAINER_CLASS_(\w+),\s*(\d+)', open(f'{RUBY}/data/trainer_money.inc').read())}
    em_rows = rematch_rows_emerald() if emerald else []           # Emerald's rematches (REMATCH_MSG)
    em_first = {r['first']: r for r in em_rows}
    for t in wanted:
        tr = trainers[t]; bid = ids[t]; sc = scaling.get(t)
        levels = sc['new_levels'] if sc else [m['level'] for m in tr['party']]
        mons = []
        has_items = any(m['item'] != 'ITEM_NONE' for m in tr['party'])
        for k, m in enumerate(tr['party']):
            lv = levels[k] if k < len(levels) else m['level']
            sp = b2c(b2_species, m['species'], 'species')
            mv = m['moves'] if m['moves'] else default_moves(sets.get(m['species'], []), lv)
            mv = [b2c(b2_moves, x, 'move') or 'MOVE_NONE' for x in mv if x != 'MOVE_NONE'] + ['MOVE_NONE'] * 4
            mons.append(dict(level=lv, sapphire_level=m['level'], species=sp, difficulty=m['iv'],
                             item=b2c(b2_items, m['item'], 'item') or 'ITEM_NONE', moves=mv[:4]))
        items = [b2c(b2_items, i, 'item') or 'ITEM_NONE' for i in tr.get('items', [])] + ['ITEM_NONE'] * 4
        ai = [AI_BITS[b] for b in range(16) if tr.get('ai', 0) >> b & 1 and b in AI_BITS]
        if tr.get('double'): ai.append('AI_FLAG_TAG_STRATEGY')        # Black 2's double-battle trainers all have it
        # texts: the first battle command (not a rematch) gives intro/defeat/after; a rematch tier its own
        bs = [b for b in by_trainer.get(t, []) if 'rematch' not in b['kind']] or by_trainer.get(t, [])
        if not bs:     # a rematch tier: the rematch command of its first tier
            base = next((row.split(',')[0].strip() for row in eye if t in [x.strip() for x in row.split(',')]), None)
            bs = [b for b in by_trainer.get(base, []) if 'rematch' in b['kind']]
        objects = []
        for b in bs:
            mj = json.load(open(f'{root}/data/maps/{b["map"]}/map.json')) if b['map'] else {}
            for lid, o in enumerate(mj.get('object_events') or [], 1):
                if o.get('script') == b['label']:
                    objects.append(dict(map=b['map'], local_id=lid, x=o['x'], y=o['y'], gfx=o['graphics_id'],
                                        movement=o['movement_type'], trainer_type=o['trainer_type'],
                                        sight=int(o['trainer_sight_or_berry_tree_id'], 0), flag=o['flag'],
                                        script=b['label'], simple=b['simple'] and o['flag'] in ('0', 0),
                                        intro=b['intro'], defeat=b['defeat'], cannot=b['cannot'], after=b['after']))
                    if emerald:       # map: the HoennB2 (Sapphire) map Emerald's map plays; built: this build has it
                        hm = hoenn_map(b['map'])
                        objects[-1].update(map=hm, emerald_map=b['map'], built=hm in built)
        double = bool(tr.get('double'))
        pair = double and len(objects) >= 2 and len({(o['map']) for o in objects}) == 1
        for k, o in enumerate(objects):
            o['npc_script'] = (5000 if pair and k == 1 else 3000) + bid
        msgs = []
        def say(typ, label, page_end):
            if not label or label not in texts: return
            line, unk = convert(texts[label], expand=True)
            if unk: report[f'text codes dropped: {",".join(unk)}'] += 1
            if page_end and not line.endswith('{be01}'): line += '{be01}'     # Black 2's intro lines end like this
            msgs.append((typ, line))
        o0 = objects[0] if objects else (dict(intro=bs[0]['intro'], defeat=bs[0]['defeat'], cannot=bs[0]['cannot'],
                                              after=bs[0]['after']) if bs else {})
        if not double:
            say(0, o0.get('intro'), True); say(1, o0.get('defeat'), False); say(2, o0.get('after'), False)
        else:
            say(3, o0.get('intro'), True)
            defeats = [o0.get('defeat')] + ([objects[1]['defeat']] if pair and objects[1]['defeat'] != o0.get('defeat') else [])
            if defeats[0] in texts:
                msgs.append((1, '{be01}\\n'.join(convert(texts[d], expand=True)[0] for d in defeats if d in texts)))
            say(5, o0.get('after'), False); say(6, o0.get('cannot'), False)
            if pair:
                o1 = objects[1]
                say(7, o1['intro'], True); say(9, o1['after'], False); say(10, o1['cannot'], False)
        if t in em_first:     # Emerald's rematch lines (REMATCH_MSG): the trainerbattle_rematch[_double] each NPC's script
            rbs = [b for b in by_trainer.get(t, []) if 'rematch' in b['kind']]          # jumps to, and its msgbox after
            def rematch_of(label, k):
                for c in scripts.get(label, (None, []))[1]:
                    mm = re.match(r'goto_if_eq VAR_RESULT, TRUE, (\w+)$', c)
                    hit = [b for b in rbs if mm and b['label'] == mm.group(1)]
                    if hit: return hit[0]
                return rbs[k] if k < len(rbs) else None
            npcs = [rematch_of(o['script'], k) for k, o in enumerate(objects[:2 if pair else 1])] or rbs[:1]
            assert npcs and all(npcs), f'{t}: no trainerbattle_rematch for its NPCs'
            for k, rb in enumerate(npcs):
                base = REMATCH_MSG['intro2'] if k else REMATCH_MSG['intro']   # (the YES / NO follows the intro: no {be01})
                say(base, rb['intro'], False); say(base + 1, rb['after'], False); say(base + 2, rb['cannot'], False)
            defeats = [rb['defeat'] for rb in npcs]
            defeats = [d for k, d in enumerate(defeats) if d in texts and d not in defeats[:k]]
            if defeats:
                msgs.append((REMATCH_MSG['defeat'], '{be01}\\n'.join(convert(texts[d], expand=True)[0] for d in defeats)))
        name, _ = convert(tr.get('name', ''), expand=True)
        out_trainers[t] = dict(b2_id=bid, sapphire_class=tr['class'], pic=tr['pic'], b2_class=pic_class[tr['pic']],
                               name=name, double=double, pair=pair, items=items[:4], ai=ai,
                               money=money.get(tr['class'], 5) * (2 if double else 1), party_items=has_items,
                               sapphire_default_moves='DefaultMoves' in tr.get('party_kind', ''),
                               party=mons, messages=msgs, objects=objects,
                               rematch_of=None if t in first else next((row.split(',')[0].strip() for row in eye if t in [x.strip() for x in row.split(',')]), None),
                               level_scaled=bool(sc and sc['new_levels'] != sc['sapphire_levels']))
        if emerald:
            out_trainers[t].update(emerald_class=tr.get('class_emerald'), emerald_pic=tr.get('pic_emerald'),
                                   maps=sorted({b['map'] for b in bs if b['map']}))
        report['trainers'] += 1
    for t, parts in split.items():
        if t not in out_trainers: continue
        d = out_trainers.pop(t); msgs = dict(d['messages'])
        pages = msgs.get(1, '').split('{be01}\\n')
        field = {0: msgs.get(3, msgs.get(0)), 2: msgs.get(5, msgs.get(2)), 6: msgs.get(6)}
        n = len(parts)
        for k, p in enumerate(parts):
            a, b = p['defeat_pages']
            m = [(1, '{be01}\\n'.join(pages[a:b]))]
            if k == 0: m = [(0, field[0])] + m + [(ty, field[ty]) for ty in (2, 6) if field[ty]]
            if REMATCH_MSG['defeat'] in msgs:     # Emerald's rematch lines: the field lines are the first twin's, the
                rp = '{be01}\\n'.join(msgs[REMATCH_MSG['defeat']].split('{be01}\\n')[a:b])   # in-battle line by page as type 1
                if k == 0: m += [(ty, msgs[ty]) for ty in (100, 101, 102) if ty in msgs]
                if rp: m.append((REMATCH_MSG['defeat'], rp))
            items = [i for i in d['items'] if i != 'ITEM_NONE']; per = len(items) // n
            objs = [dict(o, npc_script=3000 + ids[p.get('id', t)]) for o in d['objects'] if o['gfx'] == p['gfx']]
            out_trainers[p.get('id', t)] = dict(
                d, b2_id=ids[p.get('id', t)], pic=p['pic'], b2_class=pic_class[p['pic']], name=p['name'], double=False,
                pair=False, split_of=t, items=(items[k * per:(k + 1) * per] + ['ITEM_NONE'] * 4)[:4],
                money=d['money'] // n, party=[mon for mon in d['party'] if mon['species'] in p['party']], messages=m,
                objects=objs)
    # ---- write sources: one trainer.inc file per Hoenn trainer
    os.makedirs(OUT_SRC, exist_ok=True)
    class_consts = {v: k for k, v in defines(f'{B2}/include/constants/trainer_classes.h', 'TRAINER_CLASS_').items()}
    names_dir = {os.path.basename(f)[:4]: f for f in glob.glob(os.path.join(OUT_SRC, '*.s'))}
    def source_lines(t, d, what='generated by converter/gen_trainers.py, do not edit'):
        cls_const = class_consts.get(d['b2_class'], str(d['b2_class']))
        kind = ['PARTY_MOVES'] + (['PARTY_ITEMS'] if d['party_items'] else [])
        args = [f'class={cls_const}', f'party={" | ".join(kind)}']
        if d['double']: args.append('style=BTL_STYLE_DOUBLE')
        args += [f'item{i + 1}={it}' for i, it in enumerate(d['items']) if it != 'ITEM_NONE']
        if d['ai']: args.append('ai=' + ' | '.join(d['ai']))
        args.append(f'money={d["money"]}')
        lines = ['#include "asm/trainer.inc"', '',
                 f'// {t} ({d["sapphire_class"]} {d["name"]}): {what}',
                 f'    Trainer {", ".join(args)}']
        for m in d['party']:
            a = [f'level={m["level"]}', f'species={m["species"] or "SPECIES_NONE"}', f'difficulty={m["difficulty"]}']
            if d['party_items'] and m['item'] != 'ITEM_NONE': a.append(f'item={m["item"]}')
            a += [f'move{i + 1}={mv}' for i, mv in enumerate(m['moves']) if mv != 'MOVE_NONE']
            lines.append(f'    PartyMon {", ".join(a)}')
        lines.append('    PartyEnd')
        return lines
    for t, d in out_trainers.items():
        lines = source_lines(t, d)
        safe = re.sub(r'\W', '', t[len('TRAINER_'):].lower())
        path = os.path.join(OUT_SRC, f'{d["b2_id"]:04d}_{safe}.s')
        old = names_dir.get(f'{d["b2_id"]:04d}')
        if old and old != path: os.replace(old, path)       # (renamed: same file, never deleted)
        open(path, 'w').write('\n'.join(lines) + '\n')

    # ---- Emerald's rematch tiers (rematch_rows_emerald): one rematch slot per tier, numbered in gRematchTable's order
    #      (Tate & Liza: two, split as their first battle, SPLIT_EMERALD); record and party as a first battle's (levels
    #      through data/level_scaling.json, default moves written out), class and name the first battle's
    em_rematch = None
    if emerald:
        def tier_record(t, d0, r_first):
            tr, sc = trainers[t], scaling.get(t)
            levels = sc['new_levels'] if sc else [m['level'] for m in tr['party']]
            mons = []
            for k, m in enumerate(tr['party']):             # (as the first-battle loop above)
                lv = levels[k] if k < len(levels) else m['level']
                mv = m['moves'] if m['moves'] else default_moves(sets.get(m['species'], []), lv)
                mv = [b2c(b2_moves, x, 'move') or 'MOVE_NONE' for x in mv if x != 'MOVE_NONE'] + ['MOVE_NONE'] * 4
                mons.append(dict(level=lv, sapphire_level=m['level'], species=b2c(b2_species, m['species'], 'species'),
                                 difficulty=m['iv'], item=b2c(b2_items, m['item'], 'item') or 'ITEM_NONE', moves=mv[:4]))
            items = [b2c(b2_items, i, 'item') or 'ITEM_NONE' for i in tr.get('items', [])] + ['ITEM_NONE'] * 4
            ai = [AI_BITS[b] for b in range(16) if tr.get('ai', 0) >> b & 1 and b in AI_BITS]
            if tr.get('double'): ai.append('AI_FLAG_TAG_STRATEGY')
            if tr['pic'] != trainers[r_first]['pic']: report[f'rematch tier with another picture: {t}'] += 1
            return dict(sapphire_class=tr['class'], name=d0['name'], b2_class=d0['b2_class'], double=bool(tr.get('double')),
                        items=items[:4], ai=ai, money=money.get(tr['class'], 5) * (2 if tr.get('double') else 1),
                        party_items=any(m['item'] != 'ITEM_NONE' for m in tr['party']), party=mons,
                        level_scaled=bool(sc and sc['new_levels'] != sc['sapphire_levels']))
        def split_party(mons):         # Tate & Liza: the leads one each (Emerald's double sends party[0] and [1]), Solrock
            fixed = {}                 # Tate's and Lunatone Liza's (their first battle's split), the others to whoever has
            for i, m in enumerate(mons):                     # fewer (Liza on a tie); each keeps Emerald's order
                if i == 0 or m['species'] == 'SPECIES_SOLROCK': fixed[i] = 0
                elif i == 1 or m['species'] == 'SPECIES_LUNATONE': fixed[i] = 1
            for i in range(len(mons)):
                if i not in fixed:
                    n = [sum(1 for v in fixed.values() if v == s) for s in (0, 1)]
                    fixed[i] = 0 if n[0] < n[1] else 1
            return [[m for i, m in enumerate(mons) if fixed[i] == s] for s in (0, 1)]
        rdir = os.path.join(GEN, 'src', 'trainers_rematch')
        os.makedirs(rdir, exist_ok=True)
        rows, slots = [], []
        for r in em_rows:
            f = r['first']
            if f not in out_trainers: raise SystemExit(f'Emerald rematch {r["row"]}: {f} is not a converted trainer')
            parts = split.get(f)
            d0 = out_trainers[f]
            row = dict(row=r['row'], first=f, b2_id=ids[f], gym=r['gym'], map=r['map'],
                       partner=ids[parts[1]['id']] if parts else 0, tiers=[])
            for k, t in enumerate(r['tiers']):
                rec = tier_record(t, d0, f)
                recs = [(t, rec)]
                if parts:              # two single-style trainers fought together (h_trainerbattle_two), as the first battle
                    halves = split_party(rec['party'])
                    items = [i for i in rec['items'] if i != 'ITEM_NONE']; per = len(items) // 2
                    recs = []
                    for h, p in enumerate(parts):
                        dp = out_trainers[p.get('id', f)]
                        recs.append((t, dict(rec, name=dp['name'], b2_class=dp['b2_class'], double=False,
                                             items=(items[h * per:(h + 1) * per] + ['ITEM_NONE'] * 4)[:4],
                                             money=rec['money'] // 2, party=halves[h],
                                             party_items=any(m['item'] != 'ITEM_NONE' for m in halves[h]), part=p['name'])))
                row['tiers'].append(dict(tier=2 + k, trainer=t, slot=len(slots), double=rec['double'] or bool(parts)))
                for t2, rd in recs:
                    s = len(slots)
                    half = f', {rd["part"]}\'s half' if 'part' in rd else ''
                    slots.append(dict(slot=s, trainer=t2, row=r['row'], first=f, half=rd.get('part'), b2_class=rd['b2_class'],
                                      double=rd['double'], party=[f'{m["species"]} Lv{m["level"]}' for m in rd['party']]))
                    safe = re.sub(r'\W', '', t2[len('TRAINER_'):].lower()) + (f'_{rd["part"].lower()}' if 'part' in rd else '')
                    what = f'rematch slot {s} (tier {2 + k} of {f}{half}): generated by converter/gen_trainers.py, do not edit'
                    open(os.path.join(rdir, f'{s:03d}_{safe}.s'), 'w').write('\n'.join(source_lines(t2, rd, what)) + '\n')
            rows.append(row)
        em_rematch = dict(rows=rows, slots=slots)
        json.dump(em_rematch, open(os.path.join(GEN, 'data', 'hoenn_rematch.json'), 'w'), indent=1, ensure_ascii=False)

    # ---- text: names, class names, messages (Black 2's files with our lines in place)
    os.makedirs(OUT_TEXT, exist_ok=True)
    names = text_lines(f'{B2}/data/text/system/0382_trainer_names.txt')
    if emerald:   # Sapphire's files under Emerald's lines: the ids Emerald leaves to Sapphire's trainers keep their names
        names = text_lines(os.path.join(ROOT, 'src', 'text', 'system', '0382_trainer_names.txt'))
    for t, d in out_trainers.items(): names[d['b2_id']] = '\\c' + d['name']
    cls = list(b2_class_names); art = list(b2_class_art)
    if emerald:   # (and the classes Emerald does not use keep Sapphire's names; the ones it uses: Black 2's or the edit)
        cls = text_lines(os.path.join(ROOT, 'src', 'text', 'system', '0383_trainer_class_names.txt'))
        art = text_lines(os.path.join(ROOT, 'src', 'text', 'system', '0485_trainer_class_names_with_article.txt'))
        for c in set(pic_class.values()): cls[c], art[c] = b2_class_names[c], b2_class_art[c]
    for c, e in class_edit.items():
        if 'name' in e: cls[c] = e['name']; art[c] = e['name_with_article']
    if emerald:   # the Frontier Brains' classes (FRONTIER_BRAINS; their json edits: install_emerald)
        for c, (n, _) in FRONTIER_BRAINS.items(): cls[c], art[c] = n, ('an ' if n[0] in 'AEIOU' else 'a ') + n
    # messages: Black 2's records with every Hoenn trainer's records replaced; records of Black 2 trainers no system
    # uses any more are dropped to make room; the file keeps Black 2's record count (filler records at the end)
    import struct
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import narcio
    F = f'{B2}/build/b2_us/files'
    a89, a90 = narcio.load(F, 89)[0], narcio.load(F, 90)[0]
    recs = [struct.unpack_from('<HH', a89, i) for i in range(0, len(a89), 4)]
    old_lines = text_lines(f'{B2}/data/text/system/0381_trainer_msg_load.txt')
    hoenn_ids = {d['b2_id'] for d in out_trainers.values()}
    keep = [(tid, ty, old_lines[i]) for i, (tid, ty) in enumerate(recs) if tid not in hoenn_ids and tid not in POOL_DROP(ids)]
    new = [(d['b2_id'], ty, line) for d in out_trainers.values() for ty, line in d['messages']]
    sapphire_left = {}
    if emerald:   # Sapphire's first battles whose id no Emerald trainer takes keep their lines (Sapphire's world and
        taken = set(ids.values())     # scenes still stand in an Emerald build until phases 2-3)
        sapphire_left = {d['b2_id']: t for t, d in sap_data.items() if not d.get('rematch_of') and d['b2_id'] not in taken}
        new += [(d['b2_id'], ty, line) for t, d in sap_data.items() if d['b2_id'] in sapphire_left for ty, line in d['messages']]
    allm = sorted(keep + new, key=lambda r: r[0])                  # grouped by trainer (the lookup scans one group)
    if len(allm) > len(recs):
        raise SystemExit(f'{len(allm)} trainer messages > Black 2\'s {len(recs)}: a/0/8/9 would grow')
    filler = len(recs) - len(allm)
    allm += [(0xFFFF, 0xFFFF, '…')] * filler
    json.dump({'_doc': 'Generated by converter/gen_trainers.py: [trainer, type] of each line of '
                       'src/text/system/0381_trainer_msg_load.txt, in order (b2tools/patches/trainers.py builds a/0/8/9 '
                       'and a/0/9/0 from it).', 'records': [[a, b] for a, b, _ in allm]},
              open(OUT_MSGS, 'w'))
    for fname, lines in (('0381_trainer_msg_load.txt', [l for _, _, l in allm]), ('0382_trainer_names.txt', names),
                         ('0383_trainer_class_names.txt', cls), ('0485_trainer_class_names_with_article.txt', art)):
        body = '\n'.join(lines)
        open(os.path.join(OUT_TEXT, fname), 'w', encoding='utf-8').write(body if body.endswith('\n') else body + '\n')
    json.dump({'_doc': 'Generated by converter/gen_trainers.py. "edits": Black 2 class -> changes the trainers patch '
                       'makes (sprite/sex/eye_bgm in arm9 TRAINER_CLASS_RESOURCES; names in text 383/485). "review": '
                       'the class and battle sprite each Sapphire trainer picture got (stand-ins: Black 2 art).',
               'edits': {str(k): v for k, v in sorted(class_edit.items())},
               'special': special, 'special_bgm': {str(k): v for k, v in SPECIAL_BGM.items()}, 'review': review},
              open(OUT_CLASSES, 'w'), indent=1, ensure_ascii=False)
    json.dump({'_doc': 'Generated by converter/gen_trainers.py from pokeruby; per Sapphire trainer: Black 2 id, class, '
                       'party (levels after data/level_scaling.json), messages [type, line] and the Sapphire objects '
                       'that battle it (npc_script = the Black 2 NPC script id; simple = no zone script needed).',
               'trainers': out_trainers}, open(OUT_DATA, 'w'), indent=1, ensure_ascii=False)
    if emerald: free = [None] * id_report['left']
    print(f'{len(out_trainers)} trainers ({len(first)} battled by scripts, {len(rematch)} rematch tiers), '
          f'ids {min(ids.values())}-{max(ids.values())}, {len(free)} pool ids left; classes: {len(review)} '
          f'({len(class_edit)} edited); messages {len(allm) - filler}/{len(recs)} records; unknown: {dict(unknown)}; {dict(report)}')
    if ruby: install_ruby(twin, scaling, trainers)
    if emerald: install_emerald(ids, id_report, out_trainers, sapphire_left, b2_class_names, b2_class_art, resources, em_rematch)

# ---- Ruby: install what differs from Sapphire's files into the ruby/ overlays -------------------------------------------
def _read(path):
    return open(path, encoding='utf-8').read()

def _trash(path):
    """Never delete: a stale generated overlay file goes to ~/.Trash."""
    dest = os.path.join(os.path.expanduser('~/.Trash'), f'{int(time.time())}_{os.path.basename(path)}')
    shutil.move(path, dest)
    return dest

def _dump(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False) + '\n'

def install_ruby(twin, scaling, trainers):
    """Compare the Ruby set generated in GEN with the committed Sapphire files and write the differences into the ruby/
    overlays (OUT/src/trainers/ruby, OUT/src/text/system/ruby, OUT/data/ruby). --check writes nothing and fails when
    the committed overlays are not what this run produces."""
    check = '--check' in sys.argv[1:]
    want = {}       # path -> text of every overlay file this run produces
    # the same trainers and levels as the Sapphire twins (the records of a/0/8/9 and a/0/9/0 then stay as they are)
    for t, s0 in twin.items():
        a, b = scaling.get(t), scaling.get(s0)
        if not (a and b) or a['new_levels'] != b['new_levels']:
            raise SystemExit(f'{t} / {s0}: data/level_scaling.json has different levels for the twins ({a and a["new_levels"]} / {b and b["new_levels"]})')
    shared_msgs = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_msgs.json')))['records']
    ruby_msgs = json.load(open(OUT_MSGS))['records']
    if shared_msgs != ruby_msgs:
        bad = [i for i, (x, y) in enumerate(zip(shared_msgs, ruby_msgs)) if x != y][:5]
        raise SystemExit(f'Ruby trainer messages: the record list differs from Sapphire\'s at {bad} (types or count): '
                         f'a/0/8/9 would change size; each Ruby twin must have the same message types')
    # 1. trainer sources: the record and party, not the comment line
    shared_src = {os.path.basename(f)[:4]: f for f in glob.glob(os.path.join(ROOT, 'src', 'trainers', '*.s'))}
    body = lambda txt: [l for l in txt.split('\n') if not l.startswith('//')]
    for f in sorted(glob.glob(os.path.join(OUT_SRC, '*.s'))):
        num, new = os.path.basename(f)[:4], _read(f)
        if num in shared_src and body(_read(shared_src[num])) == body(new): continue
        want[os.path.join(OUT, 'src', 'trainers', version.OVERLAY, os.path.basename(f))] = new
    # 2. system text: whole files (names, class names, messages)
    for fname in ('0381_trainer_msg_load.txt', '0382_trainer_names.txt', '0383_trainer_class_names.txt',
                  '0485_trainer_class_names_with_article.txt'):
        new = _read(os.path.join(OUT_TEXT, fname))
        if new != _read(os.path.join(ROOT, 'src', 'text', 'system', fname)):
            want[os.path.join(OUT, 'src', 'text', 'system', version.OVERLAY, fname)] = new
    # 3. data: only the entries/classes that differ (version.load_json deep-merges them over the shared files)
    sap = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json')))['trainers']
    rub = json.load(open(OUT_DATA))['trainers']
    entries = {}
    for t, d in rub.items():
        s0 = twin.get(t)
        if s0 is None: continue
        d = dict(d, ruby_trainer=t, sapphire_twin=s0)
        entries[s0] = d                  # under the Sapphire constant the scenes and registry use (replaces its entry)
        entries[t] = d                   # and under Ruby's own name (HOENN_TEST_TRAINER=TRAINER_GRUNT_28)
    for t, d in rub.items():             # (a Ruby entry that equals Sapphire's would not be listed; none is expected)
        if t not in twin and d != sap.get(t): raise SystemExit(f'{t}: Ruby trainer data differs from Sapphire\'s without being an alias')
    want[os.path.join(OUT, 'data', version.OVERLAY, 'hoenn_trainer_data.json')] = _dump({
        '_doc': 'Ruby overlay of data/hoenn_trainer_data.json (version.load_json deep merge). Generated by converter/gen_trainers.py '
                'with HOENN_VERSION=ruby: the 28 trainers that differ, under the Sapphire constant (same Black 2 id) and under '
                'Ruby\'s own; "ruby_trainer" / "sapphire_twin" name the pair.',
        'trainers': dict(sorted(entries.items()))})
    sc = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json')))
    rc = json.load(open(OUT_CLASSES))
    edits = {}
    for c, e in rc['edits'].items():
        if e != sc['edits'].get(c):
            lost = set(sc['edits'].get(c, {})) - set(e)
            if lost: raise SystemExit(f'class {c}: Sapphire\'s edit keys {sorted(lost)} would survive the deep merge')
            edits[c] = e
    gone = set(sc['edits']) - set(rc['edits'])
    if gone: raise SystemExit(f'Ruby drops the class edits {sorted(gone)}: the overlay cannot remove them')
    special = {c: e for c, e in rc['special'].items() if e != sc['special'].get(c)}
    if set(sc['special']) - set(rc['special']): raise SystemExit('Ruby drops special classes')
    if rc['special_bgm'] != sc['special_bgm']: raise SystemExit('special_bgm differs')
    cls = {'_doc': 'Ruby overlay of data/hoenn_trainer_classes.json (version.load_json deep merge). Generated by '
                   'converter/gen_trainers.py with HOENN_VERSION=ruby: Team Magma classes 187/188/189/191/192 (same Black 2 '
                   'classes as Sapphire\'s Team Aqua ones) with the Magma fronts 154/156/148 (admins: slots 152/153, Tabitha '
                   'and Courtney in src/sprites/trainer/front/ruby) and their names (text 383/485).',
           'edits': dict(sorted(edits.items(), key=lambda kv: int(kv[0])))}
    if special: cls['special'] = special
    want[os.path.join(OUT, 'data', version.OVERLAY, 'hoenn_trainer_classes.json')] = _dump(cls)
    # compare with / write the committed overlays; stale generated ones go to the Trash
    mine = [(os.path.join(OUT, 'src', 'trainers', version.OVERLAY), '*.s'),
            (os.path.join(OUT, 'src', 'text', 'system', version.OVERLAY), '0381_*.txt'),
            (os.path.join(OUT, 'src', 'text', 'system', version.OVERLAY), '0382_*.txt'),
            (os.path.join(OUT, 'src', 'text', 'system', version.OVERLAY), '0383_*.txt'),
            (os.path.join(OUT, 'src', 'text', 'system', version.OVERLAY), '0485_*.txt')]
    stale = [p for d, pat in mine for p in glob.glob(os.path.join(d, pat)) if p not in want]
    changed = [p for p, txt in want.items() if not os.path.exists(p) or _read(p) != txt]
    if check:
        if changed or stale:
            print('NOT CURRENT:', [os.path.relpath(p, OUT) for p in changed + stale])
            raise SystemExit(1)
        print(f'Ruby trainer overlays current: {len(want)} files')
        return
    for p, txt in want.items():
        if p in changed:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(txt)
    for p in stale: _trash(p)
    n_src = sum(1 for p in want if p.endswith('.s'))
    print(f'Ruby overlays: {n_src} trainer sources, {len([p for p in want if p.endswith(".txt")])} system text files, '
          f'{len(entries)} data entries ({len(twin)} trainers), {len(edits)} class edits; {len(changed)} files written, '
          f'{len(stale)} stale moved to the Trash')
    print('  ' + ', '.join(sorted(os.path.relpath(p, OUT) for p in want)))

# ---- Emerald: install what differs from Sapphire's files into the emerald/ overlays ---------------------------------------
def install_emerald(ids, id_report, out_trainers, sapphire_left, b2_class_names, b2_class_art, resources, em_rematch=None):
    """Compare the Emerald set generated in GEN with the committed Sapphire files and write Emerald's overlays (as
    install_ruby): OUT/src/trainers/emerald, OUT/src/text/system/emerald (0381-0383, 0485), OUT/data/emerald
    (hoenn_trainers.json = Emerald's registry, hoenn_trainer_data.json, hoenn_trainer_classes.json, hoenn_trainer_msgs.json)
    and OUT/src/include/hoenn_trainers_emerald.h. --check writes nothing and fails when they are not current."""
    check = '--check' in sys.argv[1:]
    E = version.OVERLAY
    want = {}
    sap_reg = json.load(open(REGISTRY))['trainers']
    sap_by_id = {v: k for k, v in sap_reg.items()}
    # Emerald names that are Sapphire names of another id (pokeemerald's TRAINER_WALLACE is the Champion, pokeruby's the
    # 8th leader; TRAINER_STEVEN the Meteor Falls battle, pokeruby's the Champion): "_EMERALD" in the data file and header
    clash = {t for t, i in ids.items() if t in sap_reg and sap_reg[t] != i}
    def key(t): return t + '_EMERALD' if t in clash else t
    # 1. registry + header
    how = id_report['how']
    reg = {'_doc': 'Emerald TRAINER_* (pokeemerald names) -> Black 2 trainer id (a/0/9/1-2 entry, script 3000+id, defeat flag '
                   'id+1520). FIXED once given. Written by converter/gen_trainers.py (HOENN_VERSION=emerald, emerald_ids): a '
                   'trainer in a slot Emerald shares with Sapphire takes the Black 2 id of Sapphire\'s trainer of that slot '
                   '(data/hoenn_trainers.json); Emerald\'s new trainers take ids no Emerald trainer uses: Sapphire\'s rematch '
                   'tiers (no rematches, decision 3A), then never-given pool ids. Rematch tiers are not converted. '
                   '"sapphire": the Sapphire trainer whose id it is (slot twin, or the rematch tier it replaces).',
           'trainers': dict(sorted(ids.items(), key=lambda kv: kv[1])),
           'sapphire': {t: sap_by_id[i] for t, i in sorted(ids.items(), key=lambda kv: kv[1]) if i in sap_by_id},
           'new': sorted((t for t in ids if how.get(t) == 'new'), key=ids.get),
           'ids_left': {'total': id_report['left'], 'sapphire_rematch_tiers': id_report['left_rematch'],
                        'never_given': id_report['left_never']}}
    want[os.path.join(OUT, 'data', E, 'hoenn_trainers.json')] = _dump(reg)
    want[os.path.join(OUT, 'src', 'include', 'hoenn_trainers_emerald.h')] = (
        '// Emerald trainer names (pokeemerald) -> Black 2 trainer ids (data/emerald/hoenn_trainers.json). GENERATED by\n'
        '// converter/gen_trainers.py (HOENN_VERSION=emerald). Can be included next to hoenn_trainers.h: a name both decomps\n'
        '// share with the same id is repeated identically; ' + ', '.join(sorted(clash)) + ' (another trainer in Sapphire)\n'
        '// are named <name>_EMERALD here. Defeat flag = id + 1520; eye-contact NPC script = 3000 + id.\n#pragma once\n'
        + ''.join(f'#define {key(t):<36} {i}\n' for t, i in sorted(ids.items(), key=lambda kv: kv[1])))
    # 2. trainer sources whose record or party differs from the shared file of that number
    shared_src = {os.path.basename(f)[:4]: f for f in glob.glob(os.path.join(ROOT, 'src', 'trainers', '*.s'))}
    body = lambda txt: [l for l in txt.split('\n') if not l.startswith('//')]
    for f in sorted(glob.glob(os.path.join(OUT_SRC, '*.s'))):
        num, new = os.path.basename(f)[:4], _read(f)
        if int(num) in sapphire_left: continue          # (Sapphire's own trainer, generated here only for completeness)
        if num in shared_src and body(_read(shared_src[num])) == body(new): continue
        want[os.path.join(OUT, 'src', 'trainers', E, os.path.basename(f))] = new
    # 3. system text: whole files
    for fname in ('0381_trainer_msg_load.txt', '0382_trainer_names.txt', '0383_trainer_class_names.txt',
                  '0485_trainer_class_names_with_article.txt'):
        new = _read(os.path.join(OUT_TEXT, fname))
        if new != _read(os.path.join(ROOT, 'src', 'text', 'system', fname)):
            want[os.path.join(OUT, 'src', 'text', 'system', E, fname)] = new
    # 4. message records (a/0/8/9, a/0/9/0): Emerald's own list when it differs (a list: replaced whole by load_json)
    shared_msgs = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_msgs.json')))
    em_msgs = json.load(open(OUT_MSGS))
    if em_msgs['records'] != shared_msgs['records']:
        want[os.path.join(OUT, 'data', E, 'hoenn_trainer_msgs.json')] = json.dumps(
            dict(em_msgs, _doc='Emerald overlay of data/hoenn_trainer_msgs.json (replaces "records"): ' + em_msgs['_doc'])) + '\n'
    # 5. trainer data: every Emerald trainer under its Emerald name (key()), and under the Sapphire name of its Black 2 id
    #    (the slot twin or the replaced rematch tier), so the merged file says what each Sapphire key's id holds
    entries = {}
    for t, d in out_trainers.items():
        e = dict(d, emerald_trainer=t)
        s0 = sap_by_id.get(d['b2_id'])
        if s0: e['sapphire_twin'] = s0; entries[s0] = e
        entries[key(t)] = e
    unbuilt = {'emerald_only': collections.defaultdict(list), 'not_built': collections.defaultdict(list)}
    only = {m for g in version.versions_json().get('maps', {}).get('emerald', {}).get('new', {}).values() for m in g}
    for t, d in out_trainers.items():
        for o in d['objects']:
            if not o.get('built'): unbuilt['emerald_only' if o['emerald_map'] in only else 'not_built'][o['emerald_map']].append(t)
    want[os.path.join(OUT, 'data', E, 'hoenn_trainer_data.json')] = _dump({
        '_doc': 'Emerald overlay of data/hoenn_trainer_data.json (version.load_json deep merge). Generated by '
                'converter/gen_trainers.py with HOENN_VERSION=emerald from pokeemerald: every Emerald trainer under its '
                'Emerald name ("emerald_trainer"; TRAINER_WALLACE_EMERALD / TRAINER_STEVEN_EMERALD where pokeruby uses the '
                'name for another trainer) and under the Sapphire name of its Black 2 id ("sapphire_twin"). objects: '
                '"map" = the HoennB2 (Sapphire) map Emerald\'s map "emerald_map" plays, "built" = this build has that map '
                '(no: Emerald-only maps, placed with the Emerald world, phase 2). "unbuilt": the trainers of maps this build '
                'does not have, by map: "emerald_only" (data/versions.json maps.emerald.new) and "not_built" (Sapphire maps '
                'HoennB2 has not built either: Trick House puzzles 2-8, S.S. Tidal).',
        'unbuilt': {k: {m: sorted(set(v)) for m, v in sorted(u.items())} for k, u in unbuilt.items()},
        'trainers': dict(sorted(entries.items()))})
    # 6. classes: the edits that differ from Sapphire's (with Black 2's own value for any key Sapphire edits and Emerald
    #    does not, which the deep merge would otherwise keep), the special classes that differ, Emerald's whole review
    sc = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json')))
    rc = json.load(open(OUT_CLASSES))
    used = {r['b2_class'] for r in rc['review']}
    edits = {}
    for c in sorted(set(rc['edits']) | {c for c in sc['edits'] if int(c) in used}, key=int):
        e = dict(rc['edits'].get(c, {}))
        sprite, sex, eye = resources(int(c))
        orig = dict(sprite=sprite, sex=sex, eye_bgm=eye, name=b2_class_names[int(c)],
                    name_with_article=b2_class_art[int(c)])
        for k in set(sc['edits'].get(c, {})) - set(e): e[k] = orig[k]
        if e != sc['edits'].get(c): edits[c] = e
    for c, (name, sex) in FRONTIER_BRAINS.items():          # the Frontier Brains' classes (name, sex)
        art = 'an' if name[0] in 'AEIOU' else 'a'
        edits[str(c)] = dict(edits.get(str(c), {}), name=name, name_with_article=f'{art} {name}', sex=sex)
    edits = dict(sorted(edits.items(), key=lambda kv: int(kv[0])))
    special = {c: e for c, e in rc['special'].items() if e != sc['special'].get(c)}
    cls = {'_doc': 'Emerald overlay of data/hoenn_trainer_classes.json (version.load_json deep merge; "review" replaced '
                   'whole). Generated by converter/gen_trainers.py with HOENN_VERSION=emerald: Sapphire\'s class for every '
                   'picture both games have; Juan on the 8th leader class 119 (Black 2\'s Juan, sprite 126), Champion '
                   'Wallace on 193 (Black 2\'s Wallace 140), Team Magma beside Team Aqua on Black 2\'s other Plasma/Colress/N '
                   'special classes (Maxie 186, Tabitha 195, grunts 235/40: the Plasma battle music groups 9/7), Steven on a '
                   'spare class (sprite 139); the seven Frontier Brains on spare classes 7, 8, 9, 30, 31, 33, 34 (Emerald\'s class '
                   'names; their pictures: b2tools/sprite_emerald_frontier.py). review "emerald_pics": pokeemerald\'s '
                   'pictures; "music_pic": the pokeruby picture whose songs b2tools/patches/hoenn_music.py gives the class.',
           'edits': edits}
    if special: cls['special'] = special
    if rc['special_bgm'] != sc['special_bgm']: cls['special_bgm'] = rc['special_bgm']
    cls['review'] = rc['review']
    want[os.path.join(OUT, 'data', E, 'hoenn_trainer_classes.json')] = _dump(cls)
    # 7. Emerald's rematches (rematch_rows_emerald): the rematch slots' sources and the table emerald_rematch.py reads
    rdir = os.path.join(OUT, 'src', 'trainers', 'emerald_rematch')
    if em_rematch:
        for f in sorted(glob.glob(os.path.join(GEN, 'src', 'trainers_rematch', '*.s'))):
            want[os.path.join(rdir, os.path.basename(f))] = _read(f)
        want[os.path.join(OUT, 'data', E, 'hoenn_rematch.json')] = _dump(dict(
            _doc='Emerald\'s rematches (emerald_rematch 2026-10-18, notes/EMERALD_REMATCH.md). Generated by converter/gen_trainers.py '
                 '(HOENN_VERSION=emerald) from pokeemerald src/battle_setup.c gRematchTable: "rows" = the 73 trainers who '
                 'rematch (64 route trainers, the 8 Gym Leaders = gym 1-8, Wally at Victory Road = gym 9, a post-game '
                 'row; gym 0 = a route trainer; rows and slots are only appended), each with its first battle\'s '
                 'Black 2 id (b2_id; partner: Liza\'s for Tate & Liza) and its tiers 2-5 (slot = the rematch slot of the tier, '
                 'Tate & Liza: slot = Tate\'s half, slot + 1 = Liza\'s); "slots" = what each rematch slot holds '
                 '(src/trainers/emerald_rematch/NNN_*.s, installed by b2tools/patches/emerald_rematch.py). Rematch slots are '
                 'not Black 2 trainer ids: the battle keeps the first battle\'s id, name, picture, NPC and flag. Message '
                 'types of the first battle\'s trainer: ' + ', '.join(f'{v} {k}' for k, v in REMATCH_MSG.items()) + '.',
            **em_rematch))
    # compare with / write the committed overlays; stale generated ones go to the Trash
    mine = [(os.path.join(OUT, 'src', 'trainers', E), '*.s'), (rdir, '*.s')] + [
        (os.path.join(OUT, 'src', 'text', 'system', E), f'{n}_*.txt') for n in ('0381', '0382', '0383', '0485')]
    stale = [p for d, pat in mine for p in glob.glob(os.path.join(d, pat)) if p not in want]
    changed = [p for p, txt in want.items() if not os.path.exists(p) or _read(p) != txt]
    spare_left = [c for c in SPARE_CLASSES if c not in used and c not in {r['b2_class'] for r in sc['review']}
                  and c not in FRONTIER_BRAINS]
    print(f'Emerald registry: {len(ids)} trainers ({sum(1 for v in how.values() if v == "slot")} in Sapphire\'s slots, '
          f'{sum(1 for v in how.values() if v == "new")} new ids); '
          f'Black 2 ids left: {id_report["left"]} ({id_report["left_rematch"]} Sapphire rematch tiers + '
          f'{id_report["left_never"]} never given); Sapphire-only trainers left in their ids: {len(sapphire_left)}')
    print(f'  classes: {len(used)} used, {len(edits)} overlay edits; spare classes left: {len(spare_left)} {spare_left}')
    for k, u in unbuilt.items():
        print(f'  trainers on maps not built ({k}): {sum(len(set(v)) for v in u.values())} on {len(u)} maps: {sorted(u)}')
    if em_rematch:
        print(f'  rematches: {len(em_rematch["rows"])} trainers ({sum(1 for r in em_rematch["rows"] if 1 <= r["gym"] <= 8)} Gym Leaders, '
              f'{sum(1 for r in em_rematch["rows"] if r["gym"] > 8)} post-game), '
              f'{sum(len(r["tiers"]) for r in em_rematch["rows"])} tiers in {len(em_rematch["slots"])} rematch slots')
    if check:
        if changed or stale:
            print('NOT CURRENT:', [os.path.relpath(p, OUT) for p in changed + stale])
            raise SystemExit(1)
        print(f'Emerald trainer overlays current: {len(want)} files')
        return
    for p, txt in want.items():
        if p in changed:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(txt)
    for p in stale: _trash(p)
    print(f'  Emerald overlays: {sum(1 for p in want if p.endswith(".s"))} trainer sources, '
          f'{len([p for p in want if p.endswith(".txt")])} system text files, {len(entries)} data entries; '
          f'{len(changed)} files written, {len(stale)} stale moved to the Trash')

def POOL_DROP(ids):
    """Black 2 trainers whose messages can go: the pool ids (Unova trainers of replaced maps) not given to Hoenn."""
    used = set(ids.values())
    return {i for i in POOL if i not in used}

if __name__ == '__main__':
    try:
        main()
    finally:
        if GEN != OUT: shutil.rmtree(GEN, ignore_errors=True)       # Ruby's scratch folder
