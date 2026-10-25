"""The 141 community NPC overworld sheets (a Discord member, 2026-10-23: src/sprites/community/incoming/hoenn_npcs_141/,
overview screenshots/reports_2026-10-20/community_npcs_141_sheet.png; artists in
src/sprites/community/incoming/CREDITS.md) in the NEW (Gen 5) sprite set only. CLASSIC keeps every picture it has.

    python3 sprite_community_npcs.py plan      the mapping: sheet -> object code -> who uses it; skipped sheets and why
    python3 sprite_community_npcs.py build     src/sprites_gen5/overworld/[<version>/]<code>-<name>/ (NEW), the CLASSIC
                                               copies of the trainer-class codes (src/sprites/overworld/<code>-<name>/)
                                               and data/npc_class_sprites.json
    python3 sprite_community_npcs.py review    screenshots/npc_sprites/review.png (per code: CLASSIC / NEW frames)

The sheets are already Black 2-sized: 32x384, twelve 32x32 frames, the top-left pixel's colour = clear. Their frame
order (checked on all 141: frames 5, 4, 6 are 1, 2, 3 mirrored in 95 of them) is not Black 2's:
    0 up, 1 left step, 2 left, 3 left step, 4 right, 5 right step, 6 right step, 7 up step, 8 up step, 9 down,
    10 down step, 11 down step
Black 2 (notes/RESEARCH_STORY_SPRITES.md 5.1, by spriteControllerType):
    type 3 (12 frames): up, down, left, right x (stand, step, step)    -> community 0 7 8, 9 10 11, 2 1 3, 4 5 6
    type 2 (7 frames): up, up step, down, down step, left + 2 steps     -> community 0 7, 9 10, 2 1 3 (the game mirrors
                       the step for the other foot and left for right, so the artist's right frames are not shown)
    type 15 (9 frames, the Pokémon Center nurse 78): type 2's seven, then two bows -> the bow of the pack's second nurse
                       sheet (NPC08_2: one frame, the 11th) for both
Frames are placed whole, never redrawn, resized or recoloured: one vertical shift per sheet puts the down standing
frame's feet on the row where the code's CLASSIC picture has them (Black 2's row 30; the pack draws them on 29). Colours:
the sheet's own (at most 15 + clear; none merged: a sheet over the limit is skipped and listed).

Two kinds of target:
- SAME_CODE: a character or class with an object code of its own (Elite Four, admins, Maxie, Mom, the nurse, the Frontier
  Brains, and classes whose code only their own look uses: Youngster, Lass, Hiker, Swimmers ...): the code's NEW sheet is
  the community sheet; every NPC with the code gets it in NEW.
- CLASS: a trainer class that shares a townsperson's code (Aroma Lady on Black 2's Woman 27 with 31 townswomen, Ace
  Trainers on 19/43, Bird Keepers on 358 ...) gets a code of its own, a Black 2 code no reachable zone of any built
  version uses (FREE3 / FREE2: no NPC in a zone reachable by warps from Hoenn's, the PWT or the Union Room in v18.2 /
  Emerald v1.3, no HoennB2 data, script or art folder, no PWT record or class table entry, a normal people record:
  entityType 1, sceneNodeType 2). Its CLASSIC sheet is the old code's Black 2 picture (a type-2 picture laid out as type
  3 the way the game shows it: steps and right side mirrored), so CLASSIC looks as before; its NEW sheet is the class's
  community sheet. b2tools/patches/sprite_switch.py moves the trainers (zone NPCs with script 3000 + trainer id, of
  that class, on the old code) to the class's code in every build (data/npc_class_sprites.json). Townspeople keep the
  old code. People-sprite budget (b2tools/npc_check.py on the built ROMs): at most 3 more codes in a zone.
PWT sprites stay (user 2026-10-25: Gym Leaders, Juan, Steven, Wallace keep Black 2's PWT sheets).
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import sprites  # noqa: E402
import sprite_community as SC  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

PACK = os.path.join(SC.INCOMING, 'hoenn_npcs_141')
CLASS_JSON = os.path.join(ROOT, 'data', 'npc_class_sprites.json')
SHOTS = os.path.join(ROOT, 'screenshots', 'npc_sprites')
ORDER = {3: [0, 7, 8, 9, 10, 11, 2, 1, 3, 4, 5, 6], 2: [0, 7, 9, 10, 2, 1, 3], 15: [0, 7, 9, 10, 2, 1, 3, 'bow', 'bow']}
DOWN = {3: 3, 2: 2, 15: 2}            # Black 2's down standing frame per controller type
NURSE_BOW = ('NPC08_2_Nurse_Joy_by_diegowt_ddsjrhr.png', 10)

# (sheet, code, folder name, version overlay or None, who)
SAME_CODE = [
    ('NPC_061_Twin_PurpleZaffre.png', 9, 'twin', None, 'Twins trainers; little-girl townspeople (Black 2 Twins code)'),
    ('NPC_024_Youngster_PurpleZaffre.png', 11, 'youngster', None, 'Youngster trainers and townspeople'),
    ('NPC_057_School_Kid_M_PurpleZaffre.png', 12, 'school-kid-m', None, 'School Kid (M)'),
    ('NPC_026__Lass.png', 15, 'lass', None, 'Lass; also Sr. and Jr. and the Lass-look townsgirls (Gen 3 Lass sprite)'),
    ('NPC_016_Picnicker_PurpleZaffre.png', 35, 'picnicker', None, 'Picnicker; Pokémon Ranger (F) as in Gen 3 (Picnicker sprite)'),
    ('trCyclist_M_by_diegowt_ddsjrhr.png', 38, 'cyclist-m', None, 'Triathlete on a bike (M)'),
    ('trCyclist_F_by_diegowt_ddsjrhr.png', 39, 'cyclist-f', None, 'Triathlete on a bike (F)'),
    ('NPC_027_Swimmer_M_PurpleZaffre.png', 40, 'swimmer-m', None, 'Swimmer (M), Swimming Triathlete (M), Tuber in water'),
    ('NPC_030_Swimmer_F_PurpleZaffre.png', 41, 'swimmer-f', None, 'Swimmer (F), Swimming Triathlete (F), Sis and Bro'),
    ('NPC_037_Gentleman_PurpleZaffre.png', 44, 'gentleman', None, 'Gentleman trainers and townspeople (Mr. Stone too, as in Gen 3)'),
    ('NPC_007_Black_Belt_PurpleZaffre.png', 46, 'black-belt', None, 'Black Belt'),
    ('trClerk_M0_by_diegowt_ddsjrhr.png', 52, 'clerk-m', None, 'Devon Corp. staff (Gen 3 MAN_7)'),
    ('NPC_205_athlete_M_PurpleZaffre_Recolour.png', 58, 'athlete-m', None, 'Running Triathlete (M)'),
    ('NPC_208__athlete_F_PurpleZaffre_Recolour.png', 60, 'athlete-f', None, 'Running Triathlete (F)'),
    ('NPC_068_Fisherman_PurpleZaffre.png', 63, 'fisherman', None, 'Fisherman'),
    ('NPC_046_Hiker_PurpleZaffre.png', 64, 'hiker', None, 'Hiker; Ruin Maniac as in Gen 3 (Hiker sprite)'),
    ('trBaker_by_diegowt_ddsjrhr.png', 66, 'baker', None, 'Cook / baker (Gen 3 COOK)'),
    ('NPC_054_Scientist_M_PurpleZaffre.png', 73, 'scientist-m', None, 'Scientists (Devon, Space Center, ...)'),
    ('NPC_113_Mart_M_PurpleZaffre.png', 77, 'mart-clerk', None, 'Poké Mart clerk'),
    ('NPC08_Nurse_Joy_by_diegowt_ddsjrhr.png', 78, 'nurse', None, 'Pokémon Center nurse (+ the bow of NPC08_2)'),
    ('NPC_082_Psychic_M_PurpleZaffre.png', 183, 'psychic-m', None, 'Psychic (M)'),
    ('hex_maniac_ow_sprite_by_pokelustcompany_ddiwugd.png', 184, 'hex-maniac', None, 'Hex Maniac'),
    ('NPC_033_Sailor_PurpleZaffre.png', 359, 'sailor', None, 'Sailor trainers and townspeople'),
    ('NPC_127_Mom_PurpleZaffre.png', 251, 'mom', None, 'Mom (both houses: Gen 3 draws both mothers with one sprite)'),
    ('NPC_022_Reporter_PurpleZaffre_Recolour.png', 331, 'gabby', None, 'Gabby (TV reporter)'),
    ('NPC_021_Cameraman_PurpleZaffre.png', 340, 'ty', None, 'Ty (cameraman)'),
    ('Leader_Drake_by_izzyvicious.png', 89, 'drake', None, 'Drake (Elite Four)'),
    ('Leader_Phoebe_by_izzyvicious.png', 93, 'phoebe', None, 'Phoebe (Elite Four)'),
    ('Leader_Sydney_by_izzyvicious.png', 94, 'sidney', None, 'Sidney (Elite Four)'),
    ('Shelly_by_DiegoWT.png', 92, 'shelly', None, 'Shelly (Team Aqua admin; Sapphire, Emerald)'),
    ('NPC_Z39_Team_Magma_Boss_Maxie_PurpleZaffre_.png', 303, 'maxie', None, 'Maxie (Ruby: code 353 via ruby/353 copy_of 303)'),
    ('Leader_Courtney_by_izzyvicious_Recolour.png', 92, 'courtney', 'ruby', 'Courtney (Team Magma admin, Ruby)'),
    ('Leader_Anabel_by_izzyvicious.png', 56, 'anabel', 'emerald', 'Anabel (Salon Maiden, Emerald)'),
    ('Leader_Tucker_by_izzyvicious.png', 99, 'tucker', 'emerald', 'Tucker (Dome Ace, Emerald)'),
    ('Leader_Spenser_by_izzyvicious.png', 107, 'spenser', 'emerald', 'Spenser (Palace Maven, Emerald)'),
    ('Leader_Greta_by_izzyvicious.png', 207, 'greta', 'emerald', 'Greta (Arena Tycoon, Emerald)'),
    ('Leader_Noland_by_izzyvicious.png', 298, 'noland', 'emerald', 'Noland (Factory Head, Emerald)'),
    ('Leader_Lucy_by_izzyvicious.png', 299, 'lucy', 'emerald', 'Lucy (Pike Queen, Emerald)'),
    ('Leader_Brandon_by_izzyvicious.png', 300, 'brandon', 'emerald', 'Brandon (Pyramid King, Emerald)'),
]

# Free Black 2 codes (see the docstring): type 3 (12 frames) and type 2 (7 frames). A class on a type-3 code needs a
# type-3 slot; a class on a type-2 code takes a type-3 slot (all its frames shown) or, for a symmetric sheet, a type-2 one.
FREE3 = [131, 195, 196, 218, 219, 220, 308, 313, 316, 319, 373, 376, 59, 304, 305, 309, 310, 314, 317, 344]
FREE2 = [101, 147, 188, 189, 191, 193, 370, 371]
# (trainer pic, sheet, new code, old code, folder name)
CLASS = [
    ('COOL_TRAINER_M', 'NPC_001_Ace_Trainer_M_PurpleZaffre.png', 131, 19, 'ace-trainer-m'),
    ('DRAGON_TAMER', 'rse_dragon_tamer_overworld_sprites_revamped_by_brawlzilla_d8ozn5c.png', 195, 19, 'dragon-tamer'),
    ('BEAUTY', 'NPC_044_Beauty_PurpleZaffre.png', 196, 17, 'beauty'),
    ('BIRD_KEEPER', 'Birdkeeper_PurpleZaffre_Recolour 2.png', 218, 358, 'bird-keeper'),
    ('KINDLER', 'rse_kindler_overworld_sprites_revamped_by_brawlzilla_d8qlki9.png', 219, 358, 'kindler'),
    ('POKEFAN_F', 'trPokeFan_F.png', 220, 53, 'poke-fan-f'),
    ('POKEFAN_M', 'trPokeFan_M_2.png', 308, 20, 'poke-fan-m'),
    ('RICH_BOY', 'trRichBoy_by_diegowt_ddsjrhr_Recolour.png', 313, 18, 'rich-boy'),
    ('COOL_TRAINER_F', 'NPC_002_Ace_Trainer_F_PurpleZaffre.png', 316, 43, 'ace-trainer-f'),
    ('BATTLE_GIRL', 'NPC_009_Battle_Girl_PurpleZaffre_Recolour.png', 319, 15, 'battle-girl'),
    ('PSYCHIC_F', 'NPC_Z06_Psychic_F_PurpleZaffre.png', 373, 15, 'psychic-f'),
    ('CAMPER', 'NPC_015_Camper_PurpleZaffre.png', 376, 21, 'camper'),
    ('NINJA_BOY', 'NPC_060_Ninja_Boy_PurpleZaffre_Recolour 2.png', 59, 8, 'ninja-boy'),
    ('BUG_CATCHER', 'NPC_013_Bug_Catcher_PurpleZaffre.png', 304, 153, 'bug-catcher'),
    ('BUG_MANIAC', 'NPC_053_Bug_Maniac_PurpleZaffre_Recolour.png', 305, 24, 'bug-maniac'),
    ('AROMA_LADY', 'Aromalady_by_diegowt_ddsjrhr_Recolour.png', 309, 27, 'aroma-lady'),
    ('POKEMON_RANGER_M', 'trRanger_M_by_diegowt_ddsjrhr.png', 310, 21, 'ranger-m'),
    ('PARASOL_LADY', 'NPC_083_Parasol_Lady_PurpleZaffre_Recolour.png', 314, 43, 'parasol-lady'),
    ('LADY', 'NPC_043_Lady_PurpleZaffre_Recolour.png', 317, 27, 'lady'),
    ('POKEMANIAC', 'NPC_084_Poke_Maniac_PurpleZaffre_Recolour.png', 344, 24, 'poke-maniac'),
    ('TUBER_F', 'NPC_032_Tuber_F_PurpleZaffre.png', 101, 154, 'tuber-f'),
    ('TUBER_M', 'NPC_031_Tuber_M_PurpleZaffre.png', 147, 153, 'tuber-m'),
    ('POKEMON_BREEDER_F', 'NPC_Z08_Breeder_F_PurpleZaffre.png', 188, 27, 'breeder-f'),
    ('POKEMON_BREEDER_M', 'NPC_Z07_Breeder_M_PurpleZaffre.png', 189, 42, 'breeder-m'),
    ('COLLECTOR', 'NPC_053_Collector_PurpleZaffre.png', 191, 24, 'collector'),
    ('EXPERT_F', 'female_expert_overworld_sprites_revamped_by_brawlzilla_d8ozpxb.png', 193, 29, 'expert-f'),
    ('EXPERT_M', 'male_expert_overworld_sprites_revamped_by_brawlzilla_d8ozv6f.png', 370, 28, 'expert-m'),
    ('SCHOOL_KID_F', 'NPC_058_School_Kid_F_PurpleZaffre.png', 371, 15, 'school-kid-f'),
]

# Sheets not installed, and why (plan prints them; the report lists them)
PWT = 'PWT sprite kept (user 2026-10-25: characters with a Black 2 PWT sheet keep it)'
SKIP = {
    **{f: PWT for f in ('NPC_Z16_Gym_Leader_Roxanne_PurpleZaffre.png', 'NPC_Z17_Gym_Leader_Brawly_PurpleZaffre.png',
                        'NPC_Z18_Gym_Leader__Watson_PurpleZaffre.png', 'NPC_Z19_Gym_Leader_Flannery_PurpleZaffre_.png',
                        'NPC_Z20_Gym_Leader_Norman_PurpleZaffre.png', 'NPC_Z21_Gym_Leader_Winona_PurpleZaffre.png',
                        'NPC_Z22_Gym_Leader_Tate_PurpleZaffre.png', 'NPC_Z23_Gym_Leader_Liza_PurpleZaffre.png',
                        'NPC_Z24_Gym_Leader_Juan_PurpleZaffre.png', 'NPC_Z37_Champion_Wallace_PurpleZaffre_.png',
                        'Wallace_by_DiegoWT.png', 'Leader_Steven_by_izzyvicious.png')},
    'Archie_by_DiegoWT.png': 'Archie: the NEW set has this same DiegoWT art since 2026-10-11 (353)',
    'Wally_By_Kleinstudio.png': 'Wally: the NEW set has Kymotonian/Klein Studio\'s Wally (87, user-approved 2026-10-17); '
                                'this sheet also draws a grey shadow under the side standing frames',
    'Leader_Wally.png': 'Wally (unnamed artist): same art as Wally_By_Kleinstudio (shadow under the side frames); NEW '
                        'already has Wally',
    'kymotonian_birch_complete_by_kleinstudio_d3gk2yc.png': 'Birch: NEW has Wolfang62\'s (user-approved 2026-10-13); '
                                                            'this sheet draws a grey shadow under the side frames',
    'Aqua_Male_by_DiegoWT.png': 'Aqua grunt M: NEW has the Kimmylube/AzureAquarian RSE-outfit grunt (user-approved); '
                                'this is the ORAS outfit',
    'Aqua_F_by_DiegoWT.png': 'Aqua grunt F: as Aqua_Male (ORAS outfit; NEW keeps the approved RSE grunt)',
    'Leader_Magma_Grunt_M_by_izzyvicious.png': 'Magma grunt M: NEW keeps the approved Kimmylube/AzureAquarian grunt',
    'Leader_Magma_Grunt_F_by_izzyvicious.png': 'Magma grunt F: NEW keeps the approved Kimmylube/AzureAquarian grunt',
    'Leader_Tabitha_by_izzyvicious_Recolour 2.png': 'Tabitha: 29 colours (Black 2 allows 15), no 15-colour original in '
                                                    'the set: ask the artist/recolourist for a 15-colour version',
    'trGuitarist_2_by_diegowt_ddsjrhr_Recolour 2.png': 'Guitarist: 24 colours (16 even with near-identical ones '
                                                       'counted once): ask for a 15-colour version',
    'trRanger_F_by_diegowt_ddsjrhr.png': 'Pokémon Ranger (F): no free sprite code left; she keeps the Picnicker look '
                                         '(her Gen 3 sprite), which is the new Picnicker sheet in NEW',
    'NPC_081_Ruin_Maniac_PurpleZaffre.png': 'Ruin Maniac: no free sprite code left; keeps the Hiker look (his Gen 3 '
                                            'sprite), the new Hiker sheet in NEW',
    'Leader_Zinnia_by_izzyvicious.png': 'Zinnia: not in Sapphire/Ruby/Emerald',
    'Leader_Gracia_by_izzyvicious.png': 'not a Sapphire/Ruby/Emerald character',
    'Lisia_by_DiegoWT.png': 'Lisia: ORAS-only; no Contest NPC of hers in Gen 3 (no contest idol)',
    'hoenn_delinquent_overworld_sprite_gen_iv_style__by_lime029_dex0x51.png': 'Delinquent: not a Gen 3 trainer class',
    'Backpacker_by_DiegoWT.png': 'Backpacker: not a Gen 3 trainer class',
    'trBackpacker_F_by_diegowt_ddsjrhr.png': 'Backpacker: not a Gen 3 trainer class',
    'trBackpacker_M_by_diegowt_ddsjrhr.png': 'Backpacker: not a Gen 3 trainer class',
    'Street_thug_by_diegowt_ddsjrhr.png': 'Street Thug: not a Gen 3 trainer class',
    'NPC_Z09_Poke_Kid_PurpleZaffre.png': 'Poké Kid: not a Gen 3 trainer class',
    'NPC_062_Teammate_1_PurpleZaffre.png': 'Teammate: not a Gen 3 role',
    'tr_Teammate_2_by_diegowt_ddsjrhr.png': 'Teammate: not a Gen 3 role',
    'NPC_120_Director_PurpleZaffre.png': 'Director: not a Gen 3 role',
    'NPC_052_Young_Couple_Girl_PurpleZaffre.png': 'Young Couple: both partners share one trainer and Black 2 code; '
                                                  'no girl-only sheet target',
    'NPC_096_Young_Couple_Girl_PurpleZaffre.png': 'Young Couple: as NPC_052',
    'NPC_115_Nurse_1_PurpleZaffre.png': 'nurse: DiegoWT\'s nurse is used (it has the bow frame Black 2\'s nurse needs)',
    'NPC_115_Nurse_2_PurpleZaffre.png': 'nurse: as NPC_115_Nurse_1',
    'NPC08_2_Nurse_Joy_by_diegowt_ddsjrhr.png': None,      # used: the nurse's bow
    'trScientist__by_diegowt_ddsjrhr.png': 'Scientist (M): PurpleZaffre\'s NPC_054 is used (one look per code)',
    'NPC_055_Scientist_F_PurpleZaffre.png': 'Scientist (F): Sapphire/Ruby have none; Emerald\'s SCIENTIST_2 has no code '
                                            'of its own yet (data/emerald/sprite_map.json)',
    'trScientist_F_by_diegowt_ddsjrhr.png': 'Scientist (F): as NPC_055',
    'NPC_114_Mart_F_PurpleZaffre.png': 'Mart clerk (F): Hoenn\'s marts have the male clerk',
    'Mom_By_Kleinstudio.png': 'Mom: PurpleZaffre\'s NPC_127 is used (this one draws a grey shadow under the side frames)',
    'Rival_Mom_By_Kleinstudio.png': 'rival\'s Mom: Gen 3 draws both mothers with the one Mom sprite (OBJ_EVENT_GFX_MOM)',
    'NPC_Z14_Mr_Briney_PurpleZaffre.png': 'Mr. Briney: uses the generic Old Man code (28) with 37 townspeople; his own '
                                          'code needs per-scene work (not done)',
    'NPC_Z15_Mr_Stone_PurpleZaffre.png': 'Mr. Stone: uses the Gentleman code (44, Gen 3 GENTLEMAN); as Briney',
    **{f: 'generic townsperson (no class or named character): Black 2\'s own Gen 5 townspeople stay'
       for f in ('NPC02._by_diegowt_ddsjrhr.png', 'NPC05_by_diegowt_ddsjrhr.png', 'NPC07_by_diegowt_ddsjrhr.png',
                 'NPC10_by_diegowt_ddsjrhr.png', 'NPC11_by_diegowt_ddsjrhr.png', 'NPC13_by_diegowt_ddsjrhr.png',
                 'NPC14_by_diegowt_ddsjrhr.png', 'NPC19_by_diegowt_ddsjrhr.png', 'NPC21_by_diegowt_ddsjrhr.png',
                 'NPC24_by_diegowt_ddsjrhr.png', 'NPC29_by_diegowt_ddsjrhr.png', 'NPC45_by_diegowt_ddsjrhr.png',
                 'by_diegowt_ddsjrhr 1.png', 'by_diegowt_ddsjrhr.png', 'NPC_050_PurpleZaffre.png',
                 'NPC_051__PurpleZaffre_.png', 'NPC_060_PurpleZaffre.png', 'NPC_075_PurpleZaffre.png',
                 'NPC_077_PurpleZaffre.png', 'NPC_094_PurpleZaffre.png', 'NPC_098_PurpleZaffre.png',
                 'NPC_102_PurpleZaffre.png', 'NPC_108_PurpleZaffre.png', 'NPC_118_PurpleZaffre.png',
                 'NPC_119_PurpleZaffre.png')},
}


# ---------------------------------------------------------------------------------------------------- sheets

def pack_frames(name):
    """The 12 RGBA frames of a pack sheet, the top-left colour made clear."""
    from PIL import Image
    a = np.array(Image.open(os.path.join(PACK, name)).convert('RGBA'))
    assert a.shape[:2] == (384, 32), (name, a.shape)
    bg = a[0, 0, :3].copy()
    a[np.all(a[..., :3] == bg, -1)] = 0
    return [a[32 * i:32 * i + 32].copy() for i in range(12)]


def _bottom(a):
    ys = np.nonzero(a[..., 3] if a.ndim == 3 else a)[0]
    return int(ys.max())


def _b2_sheet(code, files=sprites.SRC_FILES):
    t = sprites.ow_table(files)
    rec = t[code]
    frames, pname, pal = sprites.btx_decode(narc_entries(arc_path(files, sprites.ARC_OW_SHEETS))[rec['res1']])
    return rec, frames, pal


def classic_folder(code, version=None):
    """The CLASSIC art folder of a code (the version's overlay first), or None (Black 2's own sheet)."""
    base = os.path.join(SC.SRC, 'overworld')
    for d in ([os.path.join(base, version)] if version else []) + [base]:
        if os.path.isdir(d):
            for n in os.listdir(d):
                if n.split('-')[0].isdigit() and int(n.split('-')[0]) == code:
                    f = os.path.join(d, n)
                    if 'copy_of' in sprites.read_json(os.path.join(f, 'sprite.json')):
                        return classic_folder(int(sprites.read_json(os.path.join(f, 'sprite.json'))['copy_of']))
                    return f
    return None


def classic_feet(code, version=None):
    """Row of the down standing frame's feet in the code's CLASSIC picture."""
    rec, frames, _ = _b2_sheet(code)
    k = DOWN[rec['spriteControllerType']]
    f = classic_folder(code, version)
    if f:
        return _bottom(SC._folder_frames(f)[k])
    return _bottom(np.frombuffer(bytes(frames[k][3]), np.uint8).reshape(frames[k][2], frames[k][1]))


def new_frames(sheet, code, version=None, feet=None):
    """(RGBA frames in the code's Black 2 layout, vertical shift) for a pack sheet on object code `code`."""
    rec, b2, _ = _b2_sheet(code)
    ctype = rec['spriteControllerType']
    src = pack_frames(sheet)
    used = [pack_frames(NURSE_BOW[0])[NURSE_BOW[1]] if k == 'bow' else src[k] for k in ORDER[ctype]]
    dy = (classic_feet(code, version) if feet is None else feet) - _bottom(src[9])
    dy = min(dy, 31 - max(_bottom(f) for f in used))      # moved up when a step's foot would leave the frame
    out = []
    for f in used:
        cv = np.zeros((32, 32, 4), np.uint8)
        lost = SC.paste(cv, f, dy, 0)
        assert lost == 0, f'{sheet}: {lost} pixels leave the frame with shift {dy}'
        out.append(cv)
    assert len(out) == len(b2), (sheet, code, len(out), len(b2))
    return out, dy


def _folder_name(code, name):
    return f'{code:03d}-{name}'


def write_new(code, name, version, frames, note, source):
    """The NEW (src/sprites_gen5) folder of a code: indexed frames + palette + sprite.json."""
    don, meta = SC._donor_frames(code)
    assert len(frames) == len(don) and frames[0].shape[:2] == don[0].shape[:2], (code, len(frames), len(don))
    idx, pal, merges, n = SC.index_frames(frames, near=0)
    assert not merges
    kind_dir = os.path.join(SC.GEN5, 'overworld', *( [version] if version else []))
    folder = os.path.join(kind_dir, _folder_name(code, name))
    SC._replace_folder(kind_dir, code, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    w, h = meta['size']
    for i, a in enumerate(idx):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), a.tobytes(), w, h, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='overworld', code=code, sheet=meta['sheet'], frames=len(idx), size=meta['size'],
        controller=meta['controller'], textures=meta['textures'], palette=meta['palette'], name=name, note=note,
        source=source, colours=n, made_by='b2tools/sprite_community_npcs.py'))
    return folder, n


def classic_class_frames(old, new):
    """(index frames, 16 BGR555) of the CLASSIC sheet of class code `new`: old code's Black 2 picture, laid out for new's
    controller type (type 2 -> 3 as the game shows type 2: up/down step 2 = step 1 mirrored, right = left mirrored)."""
    ro, fo, pal = _b2_sheet(old)
    rn, fn, _ = _b2_sheet(new)
    to, tn = ro['spriteControllerType'], rn['spriteControllerType']
    px = [np.frombuffer(bytes(p), np.uint8).reshape(h, w) for _, w, h, p in fo]
    m = lambda a: a[:, ::-1]
    if to == tn:
        out = px
    elif (to, tn) == (2, 3):
        out = [px[0], px[1], m(px[1]), px[2], px[3], m(px[3]), px[4], px[5], px[6], m(px[4]), m(px[5]), m(px[6])]
    else:
        raise ValueError(f'class code {new} (type {tn}) cannot show code {old} (type {to})')
    assert len(out) == len(fn) and all(a.shape == (fn[0][2], fn[0][1]) for a in out)
    return out, pal


def write_classic_class(new, old, name, who):
    don, meta = SC._donor_frames(new)
    assert classic_folder(old) is None, f'code {old} has a CLASSIC art folder: copy that instead'
    frames, pal = classic_class_frames(old, new)
    rgbs = [sprites.bgr555_to_rgb(c) for c in pal]
    kind_dir = os.path.join(SC.SRC, 'overworld')
    folder = os.path.join(kind_dir, _folder_name(new, name))
    SC._replace_folder(kind_dir, new, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), rgbs)
    w, h = meta['size']
    for i, a in enumerate(frames):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), a.tobytes(), w, h, rgbs)
    t = sprites.ow_table(sprites.SRC_FILES)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='overworld', code=new, sheet=meta['sheet'], frames=len(frames), size=meta['size'],
        controller=meta['controller'], textures=meta['textures'], palette=meta['palette'], name=name,
        note=f'{who} trainers (CLASSIC): Black 2\'s code {old} picture unchanged'
             + (' (its type-2 frames laid out as type 3: steps and right side mirrored, as the game shows them)'
                if t[old]['spriteControllerType'] != t[new]['spriteControllerType'] else '')
             + f'; NEW: src/sprites_gen5/overworld/{_folder_name(new, name)}',
        source=f'Black 2 a/0/4/8 sheet {t[old]["res1"]} (code {old})', made_by='b2tools/sprite_community_npcs.py'))
    return folder


# ---------------------------------------------------------------------------------------------------- checks / plan

def check_slots():
    t = sprites.ow_table(sprites.SRC_FILES)
    codes = [c for _, _, c, _, _ in CLASS]
    assert len(set(codes)) == len(codes)
    for pic, sheet, new, old, name in CLASS:
        r = t[new]
        assert r['entityType'] == 1 and r['sceneNodeType'] == 2 and r['spriteControllerType'] in (2, 3), (new, r)
        assert new in FREE3 + FREE2, new
        if t[old]['spriteControllerType'] == 3:
            assert r['spriteControllerType'] == 3, f'{pic}: type-3 code {old} needs a type-3 slot'
        for base in (SC.SRC, SC.GEN5):
            for d, _, _ in os.walk(os.path.join(base, 'overworld')):
                for n in os.listdir(d):
                    if n.split('-')[0].isdigit() and int(n.split('-')[0]) == new and n != _folder_name(new, name):
                        raise AssertionError(f'code {new} already has {os.path.join(d, n)}')
    used = [s for s, *_ in SAME_CODE] + [s for _, s, *_ in CLASS]
    allf = sorted(os.listdir(PACK))
    missing = [f for f in used if f not in allf]
    assert not missing, missing
    rest = [f for f in allf if f not in used and f not in SKIP]
    assert not rest, f'sheets with no decision: {rest}'


def plan():
    check_slots()
    lines = ['sheet | code | who (NEW only)']
    for s, code, name, ver, who in SAME_CODE:
        lines.append(f'{s} | {code}' + (f' ({ver})' if ver else '') + f' | {who}')
    for pic, s, new, old, name in CLASS:
        lines.append(f'{s} | {new} (was {old}) | {pic} trainers (new code; CLASSIC = code {old}\'s picture)')
    lines.append('\nnot used:')
    for f, why in sorted(SKIP.items()):
        if why: lines.append(f'  {f}: {why}')
    return '\n'.join(lines)


def build():
    check_slots()
    done, cls = [], {}
    for sheet, code, name, ver, who in SAME_CODE:
        fr, dy = new_frames(sheet, code, ver)
        folder, n = write_new(code, name, ver, fr, who, f'community: hoenn_npcs_141/{sheet} (shift {dy:+d})')
        done.append(f'{os.path.relpath(folder, ROOT)} ({n} colours, shift {dy:+d})')
    for pic, sheet, new, old, name in CLASS:
        write_classic_class(new, old, name, pic)
        fr, dy = new_frames(sheet, new, feet=classic_feet(old))
        folder, n = write_new(new, name, None, fr, f'{pic} trainers (moved from code {old} by sprite_switch)',
                              f'community: hoenn_npcs_141/{sheet} (shift {dy:+d})')
        done.append(f'{os.path.relpath(folder, ROOT)} ({n} colours, shift {dy:+d}; CLASSIC = code {old})')
        cls[pic] = dict(code=new, old=old, sheet=sheet)
    sprites.write_json(CLASS_JSON, {
        '_doc': 'Trainer classes with a sprite code of their own (b2tools/sprite_community_npcs.py, which writes this '
                'file): b2tools/patches/sprite_switch.py moves every zone NPC whose script is 3000 + a trainer id of '
                'that class (data/hoenn_trainer_data.json "pic") from code "old" to "code". The CLASSIC sheet of "code" '
                'is old\'s picture, the NEW one the class\'s community sheet ("sheet", src/sprites/community/incoming/'
                'hoenn_npcs_141/).',
        'classes': cls})
    return done


# ---------------------------------------------------------------------------------------------------- review

def review(path=None):
    """Per installed code: CLASSIC frames (art folder or Black 2) and NEW frames."""
    os.makedirs(SHOTS, exist_ok=True)
    path = path or os.path.join(SHOTS, 'review.png')
    rows = []
    def b2rgba(code):
        _, frames, pal = _b2_sheet(code)
        rgb = [sprites.bgr555_to_rgb(c) for c in pal]
        out = []
        for _, w, h, p in frames:
            a = np.frombuffer(bytes(p), np.uint8).reshape(h, w); im = np.zeros((h, w, 4), np.uint8)
            for i in range(1, 16): im[a == i] = (*rgb[i], 255)
            out.append(im)
        return out
    for sheet, code, name, ver, who in SAME_CODE:
        cf = classic_folder(code, ver)
        rows.append((f'{code} CLASSIC' + (f' ({ver})' if ver else ''), SC._folder_frames(cf) if cf else b2rgba(code)))
        rows.append((f'{code} NEW: {who[:60]}', SC._folder_frames(os.path.join(SC.GEN5, 'overworld', *([ver] if ver else []),
                                                                              _folder_name(code, name)))))
    for pic, sheet, new, old, name in CLASS:
        rows.append((f'{new} CLASSIC (= code {old})', SC._folder_frames(os.path.join(SC.SRC, 'overworld', _folder_name(new, name)))))
        rows.append((f'{new} NEW: {pic}', SC._folder_frames(os.path.join(SC.GEN5, 'overworld', _folder_name(new, name)))))
    return SC.review_rows(rows, path, scale=2)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    if cmd == 'plan':
        print(plan())
    elif cmd == 'build':
        print('\n'.join(build()))
    elif cmd == 'review':
        print(review())
    else:
        sys.exit(__doc__)
