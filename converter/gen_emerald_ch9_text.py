"""Emerald text overlays of chapter 9 and the Mirage Tower (emerald_ch9_mirage 2026-10-12; notes/EMERALD_STORY.md B5 / B6): writes
src/text/scenes/emerald/MossdeepCity.txt and Route111.txt and src/text/script/emerald/0547 / 0550 / 0551 / 0575 (Mossdeep's Space
Center 1F / 2F, Steven's house, the Mirage Tower's 4F) from pokeemerald's own strings (external/pokeemerald, gen_trainers.load_texts +
gen3text.convert with Emerald's placeholders), as converter/gen_emerald_magma_text.py does for the Magma chapters.
Each spec: output file -> (base file, {line index: pokeemerald label | '=' + literal text}); lines not named keep the base file's
line (Sapphire's, same index), indices past the end are appended in order.
    HOENN_VERSION=emerald python3 converter/gen_emerald_ch9_text.py [--check]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
os.environ.setdefault('HOENN_VERSION', 'emerald')
import gen_trainers as g
from gen3text import convert
_T = None
def line(label):
    global _T
    if _T is None: _T = g.load_texts(os.path.join(ROOT, 'external', 'pokeemerald'))
    s, unk = convert(_T[label], expand=True)
    assert not unk, (label, unk)
    return s
T = os.path.join(ROOT, 'src', 'text')

M = 'MossdeepCity_'
SC1 = 'MossdeepCity_SpaceCenter_1F_Text_'
SC2 = 'MossdeepCity_SpaceCenter_2F_Text_'
SH = 'MossdeepCity_StevensHouse_Text_'
SPECS = {
 # ---- Mossdeep City (scenes/emerald/MossdeepCity_Magma.inc and scenes/MossdeepCity.inc MD_T_*): lines 0-4 are Sapphire's people
 # (the King's Rock boy's after-line is Emerald's), 5 the bag-full line, 6-10 Emerald's Space Center people and Scott
 'scenes/emerald/MossdeepCity.txt': ('scenes/MossdeepCity.txt', {
     0: M + 'Text_SurfExhilarating', 1: M + 'Text_WantKingsRockStevenGaveMe', 2: M + 'Text_YouCanKeepIt',
     3: M + 'Text_StevensHouseOverThere', 4: M + 'Text_WhatToDoWithWeirdRock',
     6: M + 'Text_SpaceCenterReceivedLetter', 7: M + 'Text_SpaceCenterLaunchingRockets',
     8: M + 'Text_MossdeepTargetedByMagma', 9: M + 'Text_FeelReliefOnLand', 10: M + 'Text_ScottSomethingWrongWithTown'}),
 # ---- Space Center 1F (src/field_scripts/emerald/0670_room_MossdeepCity_SpaceCenter_1F.s): lines 0-7 as Sapphire's (same indices),
 # 8-11 the post-game Jirachi gift (Sapphire's own lines, kept), 12-24 Emerald's Magma lines
 'script/emerald/0547_room_MossdeepCity_SpaceCenter_1F.txt': ('script/0547_room_MossdeepCity_SpaceCenter_1F.txt', {
     0: SC1 + 'RocketLaunchDemandsPerfection', 1: SC1 + 'DidPokemonComeFromSpace', 2: SC1 + 'RocketsBoggleMyMind',
     3: SC1 + 'RocketLaunchImminent', 4: SC1 + 'SuccessfulLaunchNumber', 5: SC1 + 'FoundThisYouCanHaveIt',
     6: SC1 + 'HoennFamousForMeteorShowers',
     12: SC1 + 'HaywireButRocketLaunchImminent', 13: SC1 + 'HaywireButSuccessfulLaunchNumber',
     14: SC1 + 'MagmaHaveSightsOnSpaceCenter', 15: SC1 + 'MagmaCantStealFuelTakeThis', 16: SC1 + 'CantStrollOnBeachWithMagma',
     17: SC1 + 'AquaShouldBeatMagma', 18: SC1 + 'MagmaWantsToSpoilMyDream', 19: SC1 + 'StevenMagmaCantBeAllowedToTakeFuel',
     20: SC1 + 'MagmaIntentToStealNotice', 21: SC1 + 'Grunt2Intro', 22: SC1 + 'Grunt2PostBattle'}),
 # ---- Space Center 2F (0676_room_MossdeepCity_SpaceCenter_2F.s): lines 0-2 the three people (Sapphire's indices), 3-5 their
 # Magma lines, 6-22 the scene
 'script/emerald/0550_room_MossdeepCity_SpaceCenter_2F.txt': ('script/0550_room_MossdeepCity_SpaceCenter_2F.txt', {
     0: SC2 + 'WishOrdinaryPeopleCouldGoIntoSpace', 1: SC2 + 'WouldveLikedToBeAstronaut', 2: SC2 + 'MossdeepIdealForRockets',
     3: SC2 + 'WhyWouldMagmaStealRocketFuel', 4: SC2 + 'MagmaCantGetAwayWithThis', 5: SC2 + 'DoesMagmaWantToGoToSpace',
     6: SC2 + 'YoureOutnumberedTakeUsOn', 7: SC2 + 'GoodAnswer', 8: SC2 + 'Grunt5Intro', 9: SC2 + 'Grunt6Intro',
     10: SC2 + 'Grunt7Intro', 11: SC2 + 'Grunt6PostBattle', 12: SC2 + 'Grunt7PostBattle', 13: SC2 + 'Grunt5PostBattle',
     14: SC2 + 'WellTakeCareOfYou', 15: SC2 + 'MaxieDontInterfere', 16: SC2 + 'StevenWhyStealRocketFuel',
     17: SC2 + 'MaxieUseFuelToEruptVolcano', 18: SC2 + 'StevenAreYouReadyToBattle', 19: SC2 + 'StevenHurryGetReadyQuickly',
     20: SC2 + 'MaxieWeFailedIsAquaAlsoMisguided', 21: SC2 + 'MaxieWeWillGiveUp', 22: SC2 + 'StevenThankYouComeSeeMeAtHome'}),
 # ---- Steven's house (0678_room_MossdeepCity_StevensHouse.s, same line numbers as Sapphire's): Emerald's Dive scene, one letter
 'script/emerald/0551_room_MossdeepCity_StevensHouse.txt': ('script/0551_room_MossdeepCity_StevensHouse.txt', {
     0: SH + 'CollectionOfRareRocks', 1: SH + 'CollectionOfRareRocks', 2: SH + 'CollectionOfRareRocks', 3: SH + 'CollectionOfRareRocks',
     5: SH + 'UnderwateCavernBetweenMossdeepSootopolis', 6: SH + 'YouveEarnedHMDive', 7: SH + 'ExplainDive',
     8: SH + 'TakeBallContainingBeldum', 9: SH + 'ObtainedBeldum', 10: SH + 'NoSpaceForAnotherMon',
     11: SH + 'LeftPokeBallWhereItWas', 12: SH + 'LetterFromSteven', 13: SH + 'LetterFromSteven',
     14: '@nick'}),     # (Emerald's gText_NicknameThisPokemon with the species in word 2, where Ch13's Beldum scene buffers it)
 # ---- Route 111 (scenes/emerald/Route111_Mirage.inc): the two lines of the fossil that sinks (lines 37-38 follow Sapphire's 0-36)
 'scenes/emerald/Route111.txt': ('scenes/Route111.txt', {
     37: 'Route111_Text_ClawFossilDisappeared', 38: 'Route111_Text_RootFossilDisappeared'}),
 # ---- Mirage Tower 4F (src/field_scripts/emerald/0726_room_MirageTower_4F.s, zone 363, text 575): Emerald only
 'script/emerald/0575_room_MirageTower_4F.txt': (None, {
     0: 'MirageTower_4F_Text_TakeRootFossil', 1: '=%PLAYER_LEFT_ROOT%', 2: 'MirageTower_4F_Text_TakeClawFossil', 3: '=%PLAYER_LEFT_CLAW%',
     4: '=Too bad!\\nThe Bag is full...'}),     # (the bag-full line of every room of this port; pokeemerald does not check)
 # ---- Desert Underpass (src/field_scripts/emerald/0750_room_DesertUnderpass.s, zone 375, text 587): Emerald only; only the bag-full line
 'script/emerald/0587_room_DesertUnderpass.txt': (None, {0: '=Too bad!\\nThe Bag is full...'}),
}

def main(check=False):
    bad = 0
    for out, (base, over) in SPECS.items():
        bp = os.path.join(T, base) if base else None
        lines = open(bp, encoding='utf-8').read().rstrip('\n').split('\n') if bp and os.path.exists(bp) else []
        for i in sorted(over):
            v = over[i]
            if v == '@nick': s = line('gText_NicknameThisPokemon').replace('{0100:1}', '{0100:2}')
            elif v == '=%PLAYER_LEFT_ROOT%': s = line('MirageTower_4F_Text_LeftRootFossilAlone')
            elif v == '=%PLAYER_LEFT_CLAW%': s = line('MirageTower_4F_Text_LeaveClawFossilAlone')
            else: s = v[1:] if v.startswith('=') else line(v)
            if i < len(lines): lines[i] = s
            else:
                assert i == len(lines), (out, i, len(lines))
                lines.append(s)
        data = '\n'.join(lines) + '\n'
        path = os.path.join(T, out)
        if check:
            same = os.path.exists(path) and open(path, encoding='utf-8').read() == data
            print(('ok   ' if same else 'DIFF ') + out); bad += not same
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'w', encoding='utf-8').write(data); print('wrote', out, len(lines), 'lines')
    return bad

if __name__ == '__main__':
    sys.exit(1 if main('--check' in sys.argv) else 0)
