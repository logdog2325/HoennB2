"""Emerald text overlays of the Magma chapters (emerald_ch45_magma 2026-10-12; notes/EMERALD_STORY.md section 6): writes the
src/text/scenes/emerald/*.txt and src/text/script/emerald/*.txt files of Route 112, Meteor Falls, Mt. Chimney, Jagged Pass,
Mt. Pyre summit, the Cove Lily Motel, the Lilycove contest lobby and the Aqua Hideout 1F guards from pokeemerald's own strings
(external/pokeemerald, gen_trainers.load_texts + gen3text.convert with Emerald's placeholders).
Each spec: output file -> (base file, {line index: pokeemerald label | '=' + literal text}); lines not named keep the base file's
line (Sapphire's, same index), indices past the end are appended in order.
    HOENN_VERSION=emerald python3 converter/gen_emerald_magma_text.py [--check]"""
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

SPECS = {
 # ---- Route 112 (scenes/Route112.inc): the two Magma grunts' talk (E:Route112:10)
 'scenes/emerald/Route112.txt': ('scenes/Route112.txt', {
     0: 'Route112_Text_LeaderGoingToAwakenThing', 1: 'Route112_Text_YeahWeNeedMeteorite',
     2: 'Route112_Text_OhThatsWhyCrewWentToFallarbor', 3: 'Route112_Text_CantLetAnyonePassUntilTheyreBack'}),
 # ---- Meteor Falls 1F (0256_room_MeteorFalls_1F_1R.s; line 0 is the generated sign's)
 'script/emerald/0147_room_MeteorFalls_1F_1R.txt': ('script/0147_room_MeteorFalls_1F_1R.txt', {
     1: 'MeteorFalls_1F_1R_Text_WithThisMeteorite', 2: 'MeteorFalls_1F_1R_Text_DontExpectMercyFromMagma',
     3: 'MeteorFalls_1F_1R_Text_HoldItRightThereMagma', 4: 'MeteorFalls_1F_1R_Text_BeSeeingYouTeamAqua',
     5: 'MeteorFalls_1F_1R_Text_ArchieSeenYouBefore', 6: 'MeteorFalls_1F_1R_Text_BossWeShouldChaseMagma',
     7: 'MeteorFalls_1F_1R_Text_ArchieYesNoTellingWhatMagmaWillDo', 8: 'MeteorFalls_1F_1R_Text_ArchieFarewell',
     9: 'MeteorFalls_1F_1R_Text_MeetProfCozmo', 10: 'MeteorFalls_1F_1R_Text_WhatsTeamMagmaDoingAtMtChimney'}),
 # ---- Mt. Chimney (scenes/MtChimney.inc MC_T_*): Maxie is the villain, Archie asks you to stop him; the two teams' people swap
 'scenes/emerald/MtChimney.txt': ('scenes/MtChimney.txt', {
     0: 'MtChimney_Text_LavaCookiesJust200', 1: 'MtChimney_Text_ThankYouDear', 2: 'MtChimney_Text_OhFineThen',
     3: 'MtChimney_Text_YouveNotGotTheMoney',
     5: 'MtChimney_Text_MagmaOutnumbersUs', 6: 'MtChimney_Text_LessHabitatForWaterPokemon', 7: 'MtChimney_Text_MagmasNameSimilar',
     8: 'MtChimney_Text_MeteoritesPackAmazingPower', 9: 'MtChimney_Text_YouBetterNotMessWithUs',
     10: 'MtChimney_Text_AquasNameSimilar', 11: 'MtChimney_Text_DouseThemInFire',
     12: 'MtChimney_Text_Bufoh', 13: 'MtChimney_Text_Bushaa',
     14: 'MtChimney_Text_RemoveTheMeteorite', 15: 'MtChimney_Text_PlayerRemovedMeteorite', 16: 'MtChimney_Text_PlayerLeftMeteorite',
     17: 'MtChimney_Text_MachineMakesNoResponse', 18: 'MtChimney_Text_MeteoriteFittedOnMachine',
     19: 'MtChimney_Text_ArchieGoStopTeamMagma', 20: 'MtChimney_Text_ArchieIHaveMyHandsFull',
     21: 'MtChimney_Text_MeteoriteWillActivateVolcano', 22: 'MtChimney_Text_MaxieIntro',
     23: 'MtChimney_Text_MaxieYouHaventSeenLastOfMagma', 24: 'MtChimney_Text_ArchieThankYou',
     25: 'MtChimney_Text_TeamAquaAlwaysMessingWithPlans',      # (the generated sign's line follows at 26: the scene's lines come first)
     26: 'MtChimney_Text_KeepMakingMoreLand'}),
 # ---- Mt. Pyre summit (scenes/MtPyre_Summit_Em.inc; lines 9-11 are Sapphire's, unused in Emerald)
 'scenes/emerald/MtPyre_Summit.txt': ('scenes/MtPyre_Summit.txt', {
     0: 'MtPyre_Summit_Text_ArchieWeGotTheOrbLetsGo', 1: 'MtPyre_Summit_Text_BothOrbsTakenMagmaLeftThis',
     2: 'MtPyre_Summit_Text_OrbsHaveBeenTaken', 3: 'MtPyre_Summit_Text_GroudonKyogreAwakened',
     4: 'MtPyre_Summit_Text_SuperAncientPokemonTaughtUs', 5: 'MtPyre_Summit_Text_WillYouHearOutMyTale',
     6: 'MtPyre_Summit_Text_GroudonKyogreTale', 7: 'MtPyre_Summit_Text_WellThatTooIsFine',
     8: 'MtPyre_Summit_Text_ThoseTwoMenReturnedOrbs', 12: 'MtPyre_Summit_Text_MaxieSilence',
     13: 'MtPyre_Summit_Text_HearTheNewLegendOfHoenn', 14: 'MtPyre_Summit_Text_HoennTrioTale'}),
 # ---- Cove Lily Motel 2F (0360_room_LilycoveCity_CoveLilyMotel_2F.s; line 0 is the generated sign's): the staff's lines, Scott's two
 'script/emerald/0238_room_LilycoveCity_CoveLilyMotel_2F.txt': ('script/0238_room_LilycoveCity_CoveLilyMotel_2F.txt', {
     1: 'LilycoveCity_CoveLilyMotel_2F_Text_ShowMeCompletedDex', 2: 'LilycoveCity_CoveLilyMotel_2F_Text_FilledPokedexGiveYouThis',
     3: 'LilycoveCity_CoveLilyMotel_2F_Text_ImTheProgrammer', 4: 'LilycoveCity_CoveLilyMotel_2F_Text_ImTheGraphicArtist',
     5: 'LilycoveCity_CoveLilyMotel_2F_Text_GirlsAreCute', 6: 'LilycoveCity_CoveLilyMotel_2F_Text_SeaBreezeTicklesHeart',
     7: 'LilycoveCity_CoveLilyMotel_2F_Text_NeverLeaveWithoutGameBoy',
     8: 'LilycoveCity_CoveLilyMotel_2F_Text_SnoozingPreferBattles', 9: 'LilycoveCity_CoveLilyMotel_2F_Text_ContestsDoTakeStrategy'}),
 # ---- Lilycove contest lobby (0322_room_LilycoveCity_ContestLobby.s): the receptionist gives the Pokéblock Case (appended lines 12-13)
 'script/emerald/0219_room_LilycoveCity_ContestLobby.txt': ('script/0219_room_LilycoveCity_ContestLobby.txt', {
     5: 'LilycoveCity_ContestLobby_Text_ContestReception', 12: 'LilycoveCity_ContestLobby_Text_ReceptionDontHavePokeblockCase',
     13: 'LilycoveCity_ContestLobby_Text_NowThatWeveClearedThatUp'}),
 # ---- Aqua Hideout 1F (0004_room_AquaHideout_1F.s): the entrance guards' lines (1-4 as Sapphire's) and the two Magma hints (5-6)
 'script/emerald/0005_room_AquaHideout_1F.txt': ('script/0005_room_AquaHideout_1F.txt', {
     1: 'AquaHideout_1F_Text_OurBossIsSnatchingSomething', 2: 'AquaHideout_1F_Text_BossWentToJackASubmarine',
     3: 'AquaHideout_1F_Text_BossIsOnRoute122', 4: 'AquaHideout_1F_Text_BossIsInSlateportCity',
     5: 'AquaHideout_1F_Text_WhereMightMagmaHideoutBe', 6: 'AquaHideout_1F_Text_TeamMagmaAtMtChimney'}),
 # ---- Magma Hideout 4F (src/field_scripts/emerald/0718_room_MagmaHideout_4F.s MH4F_Maxie; emerald_ch8_hideout 2026-10-12): Emerald only, a new
 # room file (text number 571 = the zone's `text` in data/emerald/hoenn_interiors.json; the grunts' and Tabitha's lines are trainer messages)
 'script/emerald/0571_room_MagmaHideout_4F.txt': (None, {
     0: 'MagmaHideout_4F_Text_MaxieAwakenGroudon', 1: 'MagmaHideout_4F_Text_MaxieGroudonWhatsWrong',
     2: 'MagmaHideout_4F_Text_MaxieOhItWasYou', 3: 'MagmaHideout_4F_Text_MaxieImGoingAfterGroudon'}),
 # ---- Jagged Pass (scenes/JaggedPass.inc: Emerald only, no Sapphire text)
 'scenes/emerald/JaggedPass.txt': (None, {
     0: 'JaggedPass_Text_BoulderShakingInResponseToEmblem', 1: 'JaggedPass_Text_GruntIntro', 2: 'JaggedPass_Text_GoWhereverYouWant'}),
}

def main(check=False):
    bad = 0
    for out, (base, over) in SPECS.items():
        bp = os.path.join(T, base) if base else None
        lines = open(bp, encoding='utf-8').read().rstrip('\n').split('\n') if bp and os.path.exists(bp) else []
        for i in sorted(over):
            v = over[i]
            s = v[1:] if v.startswith('=') else line(v)
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
