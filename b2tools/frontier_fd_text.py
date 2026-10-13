"""The Battle Factory's and the Battle Dome's room texts (frontier_factory_dome, 2026-10-12; notes/FRONTIER_FACTORY_DOME.md):
Emerald's own lines, word for word through frontier_core's b2tools/frontier_text.py (gen3text), in the order the
scripts name them. Writes the seven rooms' text files and src/include/frontier_fd_lines.h (FD_<ROOM>_<NAME> = line).

    python3 b2tools/frontier_fd_text.py            (writes; --check compares)

Files: src/text/script/emerald/NNNN_room_<Room>.txt (NNNN = the zone's Black 2 text number; the text patch moves it to
the room's own number, data/emerald/hoenn_interiors.json own_text). The Factory battle room's file (FR_TEXT_FILE of
b2tools/patches/frontier_factory_dome.py) also holds the 300 Frontier trainers' names (lines 100-399, Noland 400,
Tucker 401) and their before-battle speeches (500-799), which the engine reads; the Dome battle room's file has the
same block (its scripts show the speeches). Lines marked NEW are not Emerald's (Black 2's screens need them)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import frontier_text as ft  # noqa: E402

FAC = 'BattleFrontier_BattleFactory'
DOME = 'BattleFrontier_BattleDome'
NAME_BASE, NOLAND, TUCKER, SPEECH_BASE = 100, 400, 401, 500
TREE_NAME, YOUR_BLOCK, OTHER_BLOCK, ROUND_NAMES = 90, 91, 92, 93
GEN3_TYPES = ['Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug', 'Ghost', 'Steel', None, 'Fire',
              'Water', 'Grass', 'Electric', 'Psychic', 'Ice', 'Dragon', 'Dark']
STYLES = ['StyleUnrestrained', 'StyleTotalPreparation', 'StyleSlowAndSteady', 'StyleEndurance', 'StyleHighRisk',
          'StyleWeakenFoe', 'StyleImpossibleToPredict', 'StyleDependsOnFlow', 'StyleFlexible']   # FACTORY_STYLE_* 0-8

def S(name): return ft.conv(ft.strings_c(name))
def L(room, label): return ft.line(room, label)

def lobby(room, roles, prefix='LOBBY'):
    # (the "not enough eligible" lines keep Emerald's {STR_VAR_1}: fr_lobby_attendant fills word 1, frontier_core)
    return [(f'{prefix}_{r}', s) for r, lab, s in ft.lobby_block(room, roles)]

def rooms():
    """{room: [(NAME, line text) in line order; (None, ...) = a placeholder]}"""
    out = {}
    m = FAC + 'Lobby'
    out[m] = lobby(m, {'WON_BRAIN': 'CongratsForDefeatingHead', 'RECORD_WON': 'ExchangeMonsAndSave'}) + [
        ('MAN_KNOWLEDGE', L(m, 'NeedKnowledgeOfMonsMoves')), ('CAMPER', L(m, 'SwappedForWeakMon')),
        ('PICNICKER', L(m, 'NeedToCheckOpponentsMons')), ('FAT_MAN', L(m, 'CantFigureOutStaffHints')),
        ('RULES', L(m, 'RulesAreListed')), ('RULES_WHICH', L(m, 'ReadWhichHeading')),
        ('RULES_BASIC', L(m, 'ExplainBasicRules')), ('RULES_PARTNER', L(m, 'ExplainSwapPartnerRules')),
        ('RULES_NUMBER', L(m, 'ExplainSwapNumberRules')), ('RULES_NOTES', L(m, 'ExplainSwapNotesRules')),
        ('RULES_OPEN', L(m, 'ExplainOpenLvRules')),
        ('MENU_BASIC', S('gText_BasicRules')), ('MENU_PARTNER', S('gText_SwapPartners')),
        ('MENU_NUMBER', S('gText_SwapNumber')), ('MENU_NOTES', S('gText_SwapNotes')), ('MENU_OPEN', S('gText_OpenLevel')),
        ('MENU_EXIT', S('gText_Exit')),
        # NEW: Emerald's results window (frontier_results) as one message: Lv. 50 and Open Level, current and record
        ('RESULTS', "{0100:0}’s Battle Factory results{be01}\\nLv. 50: current streak {0100:1}, record {0100:2}\\n"
                    "Open Level: current streak {0100:3}, record {0100:4}"),
        # NEW (Emerald's doubles results window, as one message)
        ('RESULTS_D', "{0100:0}’s Battle Swap Double results{be01}\\nLv. 50: current streak {0100:1}, record {0100:2}\\n"
                      "Open Level: current streak {0100:3}, record {0100:4}")] + \
        lobby(m, {'WELCOME': 'WelcomeForDoubleBattle', 'TAKE': 'TakeDoublesChallenge', 'EXPLAIN': 'ExplainDoublesChallenge',
                  'WON_BRAIN': 'CongratsForDefeatingHead', 'RECORD_WON': 'ExchangeMonsAndSave'}, 'LOBBYD')   # the doubles attendant
    m = FAC + 'PreBattleRoom'
    out[m] = [('HOLD_CHOOSE', L(m, 'HoldMonsChooseFromSelection')), ('RESTORE', L(m, 'LetUsRestoreMons'))] + [
        (f'READY_{n}', L(m, f'ReadyFor{w}Opponent')) for n, w in zip(range(2, 8), ('2nd', '3rd', '4th', '5th', '6th', '7th'))] + [
        ('SAVE_QUIT', L(m, 'SaveAndQuitGame')), ('RETIRE', L(m, 'RetireFromChallenge')),
        ('INVESTIGATED', L(m, 'InvestigatedUpcomingOpponent'))] + [
        (f'TYPE_{i}', L(m, f'TrainerSkilledIn{t}Type') if t else '…') for i, t in enumerate(GEN3_TYPES)] + [
        ('TYPE_18', L(m, 'TrainerHasNoClearFavorite'))] + [(f'STYLE_{i}', L(m, s)) for i, s in enumerate(STYLES)] + [
        ('LIKE_SWAP', L(m, 'LikeToSwapMon')), ('SWAP_DONE', L(m, 'YourSwapIsComplete')), ('THIS_WAY', L(m, 'RightThisWay')),
        ('SAVING', L(m, 'SavingDataPleaseWait')), ('WAIT_MOMENTS', L(m, 'WaitFewMoments')),
        ('UNDERSTOOD', L(m, 'UnderstoodSirWillDo')), ('HEAD_COME', L(m, 'MessageFromHeadComeRightNow')),
        ('PREPARED_HEAD', L(m, 'PreparedToFaceHead')), ('CANT_TELL_HEAD', L(m, 'CantTellAnythingAboutHead')),
        ('MENU_GO_ON', S('gText_GoOn')), ('MENU_REST', S('gText_Rest')), ('MENU_RETIRE', S('gText_Retire'))]
    m = FAC + 'BattleRoom'
    out[m] = [('GET_MOVE_ON', L(m, 'GetAMoveOn')), ('NOLAND_HEAD', L(m, 'NolandImFactoryHead')),
              ('NOLAND_SILVER', L(m, 'ShakeOutKnowledgeBringItOn')), ('NOLAND_PASS', L(m, 'NolandLetsSeeFrontierPass')),
              ('GOT_SILVER', L(m, 'ReceivedKnowledgeSymbol')), ('NOLAND_NEXT', L(m, 'NextTimeNoHoldsBarred')),
              ('NOLAND_HARDER', L(m, 'HarderLookThanLastTime')), ('NOLAND_GOLD', L(m, 'AllRightBringItOn')),
              ('NOLAND_PASS2', L(m, 'OutOfMyLeagueLetsSeePass')), ('GOT_GOLD', L(m, 'KnowledgeSymbolTookGoldenShine')),
              ('NOLAND_LAST', L(m, 'LastTimeILoseToYou'))]
    m = DOME + 'Lobby'
    out[m] = lobby(m, {'WELCOME': 'WelcomeSingleBattle', 'STEP': 'ShowYouToBattleDome', 'GOODBYE': 'HopeToSeeYouAgain',
                       'WON': 'CongratsForWinningTourney', 'WON_BRAIN': 'CongratsDefeatedTucker',
                       'AWARD': 'AwardTheseBattlePoints', 'RECORD_WON': 'RecordWillBeSaved', 'LOST': 'ThankYouForPlaying',
                       'RESUME': 'WeveBeenWaitingForYou', 'SAVE_BEFORE': 'OkayToSaveBeforeChallenge'}) + [
        ('MAN', L(m, 'LastWinnerWasTough')), ('LASS', L(m, 'WinnersGainReputation')),
        ('FAT_MAN', L(m, 'TrashedInFirstRound')), ('MANIAC', L(m, 'NeedToCheckOpponentCarefully')),
        ('PREV_TREE', L(m, 'PrevTourneyResultsSinglesLv50')), ('PREV_TREE_OPEN', L(m, 'PrevTourneyResultsSinglesLvOpen')),
        ('RULES', L(m, 'RulesAreListed')), ('RULES_WHICH', L(m, 'ReadWhichHeading')),
        ('RULES_MATCHUP', L(m, 'ExplainMatchupRules')), ('RULES_TREE', L(m, 'ExplainTourneyTree')),
        ('RULES_DOUBLE_KO', L(m, 'ExplainDoubleKORules')),
        ('MENU_MATCHUP', S('gText_Matchup')), ('MENU_TREE', S('gText_TourneyTree')), ('MENU_DOUBLE_KO', S('gText_DoubleKO')),
        ('MENU_EXIT', S('gText_Exit')),
        ('RESULTS', "{0100:0}’s Battle Dome results{be01}\\nLv. 50: current streak {0100:1}, record {0100:2}\\n"
                    "Open Level: current streak {0100:3}, record {0100:4}"),   # NEW (Emerald's results window)
        ('RESULTS_D', "{0100:0}’s Double Battle Tournament results{be01}\\nLv. 50: current streak {0100:1}, record {0100:2}\\n"
                      "Open Level: current streak {0100:3}, record {0100:4}"),   # NEW (the doubles window)
        ('PREV_TREE_D', L(m, 'PrevTourneyResultsDoublesLv50')), ('PREV_TREE_D_OPEN', L(m, 'PrevTourneyResultsDoublesLvOpen'))] + \
        lobby(m, {'WELCOME': 'WelcomeDoubleBattle', 'TAKE': 'TakeDoublesChallenge', 'EXPLAIN': 'ExplainDoublesChallenge',
                  'STEP': 'ShowYouToBattleDome', 'GOODBYE': 'HopeToSeeYouAgain',
                  'WON': 'CongratsForWinningTourney', 'WON_BRAIN': 'CongratsDefeatedTucker',
                  'AWARD': 'AwardTheseBattlePoints', 'RECORD_WON': 'RecordWillBeSaved', 'LOST': 'ThankYouForPlaying',
                  'RESUME': 'WeveBeenWaitingForYou', 'SAVE_BEFORE': 'OkayToSaveBeforeChallenge'}, 'LOBBYD')
    out[DOME + 'Corridor'] = [('NONE', '…')]
    m = DOME + 'PreBattleRoom'
    out[m] = [(f'READY_{i}', L(m, f'ReadyFor{w}')) for i, w in enumerate(('Round1', 'Round2', 'Semifinals', 'Finals'))] + [
        ('CHOOSE_TWO', L(m, 'ChooseTwoMons')), ('THIS_WAY', L(m, 'RightThisWay')), ('RESTORE', L(m, 'RestoreMonsToFullHealth'))] + [
        (f'COMPLETE_{i}', L(m, f'{w}Complete')) for i, w in ((1, 'Round1'), (2, 'Round2'), (3, 'Semifinals'))] + [
        ('NEXT_OPPONENT', L(m, 'PlayersNextOpponentIsTrainer'))] + [
        (f'IN_ROUND_{i}', L(m, f'TourneyIn{w}')) for i, w in enumerate(('Round1', 'Round2', 'Semifinals', 'Finals'))] + [
        ('SAVE_QUIT', L(m, 'SaveAndQuitGame')), ('RETIRE', L(m, 'RetireYourChallenge')), ('SAVING', L(m, 'SavingDataPleaseWait')),
        ('TUCKER_SILVER', L(m, 'ReadyForTuckerSilver')), ('TUCKER_GOLD', L(m, 'ReadyForTuckerGold')),
        ('TUCKER_SILVER_SHORT', L(m, 'ReadyForTuckerSilverShort')), ('TUCKER_GOLD_SHORT', L(m, 'ReadyForTuckerGoldShort')),
        ('MENU_OPPONENT', S('gText_Opponent')), ('MENU_TREE', S('gText_TourneyTree')), ('MENU_READY', S('gText_ReadyToStart')),
        ('MENU_REST', S('gText_Rest')), ('MENU_RETIRE', S('gText_Retire')),
        # NEW: Emerald's opponent card (its three Pokémon) as one line: word 1 the trainer, words 2-4 the species
        ('OPP_MONS', '{0100:1}’s Pokémon:\\n{0100:2}, {0100:3} and {0100:4}.')]
    m = DOME + 'BattleRoom'
    ann = ['BrightNewHope', 'RisingStar', 'WillTheyRaceToChampionship', 'CanAchieveChampionFirstTry',        # first try
           'CanLossBeAvenged', 'OnFireForChampionship', 'WinHereAdvancesToFinal', 'WillLongHeldDreamComeTrue',  # never won
           'TheInvincibleChampion', 'CanAnyoneHopeToBeatTrainer', 'DoBattlesExistSolelyForTrainer', 'CurrentChampAimingToRetainTitle',
           'FormerChampHasReturned', 'FormerToughnessReturned', 'WillDoExpectedAdvanceToFinals', 'WillFormerChampRegainGlory']
    out[m] = [('ENTERED', L(m, 'PlayerHasEnteredDome')), ('VERSUS', L(m, 'PlayerVersusTrainer')),
              ('PLAYER_WINS', L(m, 'PlayerIsWinner')), ('TRAINER_WINS', L(m, 'TrainerIsWinner')),
              ('CHAMP_50', L(m, 'PlayerIsLv50Champ')), ('CHAMP_OPEN', L(m, 'PlayerIsLvOpenChamp'))] + [
        (f'ANNOUNCE_{i}', L(m, a)) for i, a in enumerate(ann)] + [
        ('TUCKER_GLOW', L(m, 'FeelGlowOfTrueMaster')), ('TUCKER_MAKE_WAY', L(m, 'MakeWayForDomeAceTucker')),
        ('TUCKER_CHANT', L(m, 'SpectatorTuckerChant')), ('TUCKER_SILVER_INTRO', L(m, 'TuckerSilverIntro')),
        ('TUCKER_STRATEGY', L(m, 'LetsSeeYourStrategy')), ('VICTOR_PLAYER', L(m, 'IncredibleVictorIsPlayer')),
        ('WINNER_TUCKER', L(m, 'WinnerIsTucker')), ('TUCKER_PASS', L(m, 'SeeYourFrontierPass')),
        ('GOT_SILVER', L(m, 'ReceivedTacticsSymbol')), ('TUCKER_NEXT', L(m, 'WontUnderestimateYouNextTime')),
        ('TUCKER_STRETCHED', L(m, 'CanWinStreakBeStretched')), ('TUCKER_LEGEND', L(m, 'LegendHasReturnedDomeAceTucker')),
        ('TUCKER_GOLD_INTRO', L(m, 'TuckerGoldIntro')), ('TUCKER_UNLEASH', L(m, 'UnleashAllPowerIPossess')),
        ('TUCKER_NEVER_LOST', L(m, 'NeverLostWhenPowerUnleashed')), ('GOT_GOLD', L(m, 'TacticsSymbolTookGoldenShine')),
        ('TUCKER_LOOK_FORWARD', L(m, 'LookForwardToNextEncounter')), ('VERSUS_TUCKER', L(m, 'PlayerVersusTucker'))]
    return out

def trainer_block():
    d = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'frontier.json'), encoding='utf-8'))
    names = {NAME_BASE + t['index']: t['name'] for t in d['trainers']}
    names[NOLAND], names[TUCKER] = 'Noland', 'Tucker'
    speech = {SPEECH_BASE + t['index']: t['before'] for t in d['trainers']}
    return names, speech

def room_numbers():
    sys.path.insert(0, HERE)
    import version
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    return {k: v['text'] for k, v in rooms.items() if k.startswith((FAC, DOME))}

def main(check=False):
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    texts = rooms()
    nums = room_numbers()
    names, speech = trainer_block()
    defines = ['// GENERATED by b2tools/frontier_fd_text.py: the Battle Factory / Battle Dome rooms\' text lines', '#ifndef FRONTIER_FD_LINES_H', '#define FRONTIER_FD_LINES_H']
    changed = []
    for room, lines in texts.items():
        short = room[len('BattleFrontier_Battle'):].upper()
        body = [s for _, s in lines]
        for i, (n, _) in enumerate(lines):
            if n: defines.append(f'#define FD_{short}_{n} {i}')
        if room in (FAC + 'BattleRoom', DOME + 'BattleRoom'):
            assert len(body) <= TREE_NAME, (room, len(body))
            body += ['…'] * (SPEECH_BASE + 300 - len(body))
            body[TREE_NAME], body[YOUR_BLOCK], body[OTHER_BLOCK] = 'Battle Dome', 'Your block', 'The other block'  # NEW (the bracket's two halves)
            for i, n in enumerate(('Round 1', 'Round 2', 'Semifinal', 'Final')): body[ROUND_NAMES + i] = n   # Emerald's gRoundsStringTable
            for k, v in names.items(): body[k] = v
            for k, v in speech.items(): body[k] = v
        p = os.path.join(ROOT, 'src', 'text', 'script', 'emerald', f'{nums[room]:04d}_room_{room}.txt')
        text = '\n'.join(body) + '\n'
        if not os.path.exists(p) or open(p, encoding='utf-8').read() != text:
            changed.append(os.path.basename(p))
            if not check: open(p, 'w', encoding='utf-8').write(text)
    defines += [f'#define FD_NAME_BASE {NAME_BASE}', f'#define FD_SPEECH_BASE {SPEECH_BASE}', f'#define FD_ROUND_NAMES {ROUND_NAMES}', '#endif']
    hp = os.path.join(ROOT, 'src', 'include', 'frontier_fd_lines.h')
    htext = '\n'.join(defines) + '\n'
    if not os.path.exists(hp) or open(hp).read() != htext:
        changed.append('frontier_fd_lines.h')
        if not check: open(hp, 'w').write(htext)
    print(('differs: ' if check else 'written: ') + (', '.join(changed) or 'nothing'))

if __name__ == '__main__':
    main('--check' in sys.argv)
