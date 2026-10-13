"""The Battle Palace's and the Battle Arena's room texts (frontier_palace_arena, 2026-10-12;
notes/FRONTIER_PALACE_ARENA.md): Emerald's own lines, word for word through frontier_core's b2tools/frontier_text.py
(gen3text), in the order the scripts name them. Writes the six rooms' text files and src/include/frontier_pa_lines.h
(PA_<ROOM>_<NAME> = line; PA_L_<NAME> = the battle lines' numbers, read by b2tools/patches/frontier_palace_arena.c).

    python3 b2tools/frontier_pa_text.py            (writes; --check compares)

Files: src/text/script/emerald/NNNN_room_<Room>.txt (NNNN = the zone's Black 2 text number; the text patch moves it to
the room's own number, data/emerald/hoenn_interiors.json own_text). Both battle rooms' files also hold the 300 Frontier
trainers' names (lines 100-399; 400 Spenser, 401 Greta) and their before-battle speeches (500-799), as the Factory's,
and the battle's own lines from 820 (the engine shows them as battle messages: ids 0x4000 | line from the Palace
battle room's file, 0x6000 | line from the Arena's). Lines marked NEW are not Emerald's."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import frontier_text as ft  # noqa: E402

PAL = 'BattleFrontier_BattlePalace'
ARE = 'BattleFrontier_BattleArena'
NAME_BASE, SPENSER, GRETA, SPEECH_BASE, BATTLE_BASE = 100, 400, 401, 500, 820

def S(name): return ft.conv(ft.strings_c(name))
def L(room, label): return ft.line(room, label)
def B(label): return ft.conv(ft.strings_c(label) if label.startswith('gText') else label)

def lobby(room, roles, prefix='LOBBY'):
    return [(f'{prefix}_{r}', s) for r, lab, s in ft.lobby_block(room, roles)]

def battle_message(label):
    """an Emerald battle string (src/battle_message.c sText_*) as plain text: {B_...} placeholders replaced below"""
    import re
    t = open(os.path.join(ft.EM, 'src', 'battle_message.c'), encoding='utf-8').read()
    m = re.search(r'static const u8 ' + re.escape(label) + r'\[\] = _\("((?:[^"\\]|\\.)*)"\);', t)
    assert m, label
    return m.group(1)

def bline(label, subs):
    """a battle line: Emerald's battle string with its placeholders replaced by Black 2's battle tags, then gen3text"""
    s = battle_message(label)
    for k, v in subs.items(): s = s.replace(k, v)
    s = s.replace('\\p', '')
    out = ft.conv(s)
    assert '{B_' not in out and 'B_' not in out.replace('{0', ''), (label, out)
    return out

def palace_battle_lines():
    """820-: the flavor texts and "incapable" (three wordings each: the player's, the wild (unused), the foe's
    Pokémon, as Black 2's own per-Pokémon battle lines) and the referee lines (Arena)"""
    out = []
    for key, label in (('GLINT', 'sText_GlintAppearsInEye'), ('POSITION', 'sText_PkmnGettingIntoPosition'),
                       ('GROWL', 'sText_PkmnBeganGrowlingDeeply'), ('EAGER', 'sText_PkmnEagerForMore'),
                       ('INCAPABLE', 'sText_PkmnIncapableOfPower')):
        tag = '{B_SCR_ACTIVE_NAME_WITH_PREFIX}' if key != 'INCAPABLE' else '{B_ATK_NAME_WITH_PREFIX}'
        s = battle_message(label).replace('\\p', '')
        lines = []
        for pre in ('', 'the wild ', 'the foe’s '):
            t = ft.conv(s.replace(tag, 'qqmonqq'))
            t = t.replace('qqmonqq', pre + '{0102:0}')
            if t.startswith('the '): t = 'T' + t[1:]
            lines.append(t)
        out += [(f'{key}', lines[0]), (f'{key}_WILD', lines[1]), (f'{key}_FOE', lines[2])]
    return out

def arena_battle_lines():
    pm, om = '{0102:0}', '{0102:1}'
    return [
        ('COMMENCE', bline('sText_RefCommenceBattle', {'{B_PLAYER_MON1_NAME}': pm, '{B_OPPONENT_MON1_NAME}': om}).replace(' Vs ', ' VS ')),
        ('THATS_IT', bline('sText_RefThatsIt', {})),
        ('MIND', bline('sText_RefJudgeMind', {})),
        ('SKILL', bline('sText_RefJudgeSkill', {})),
        ('BODY', bline('sText_RefJudgeBody', {})),
        # NEW (Emerald shows the three categories' marks in a window; here a line each): the first Pokémon named takes
        # the category (args: winner, loser), or a tie
        ('CAT_WIN', 'Referee: {0102:0} takes this one!'),
        ('CAT_TIE', 'Referee: It’s even!'),
        ('PLAYER_WON', bline('sText_RefPlayerWon', {'{B_BUFF1}': '{0202:0}', '{B_BUFF2}': '{0202:1}', '{B_PLAYER_NAME}': '{0100:2}',
                                                     '{B_PLAYER_MON1_NAME}': '{0102:3}'})),
        ('OPP_WON', bline('sText_RefOpponentWon', {'{B_BUFF1}': '{0202:0}', '{B_BUFF2}': '{0202:1}', '{B_TRAINER1_NAME}': '{0100:2}',
                                                    '{B_OPPONENT_MON1_NAME}': '{0102:3}'})),
        ('DRAW', bline('sText_RefDraw', {})),
        ('DEFEATED', bline('sText_DefeatedOpponentByReferee', {'{B_PLAYER_MON1_NAME}': pm, '{B_OPPONENT_MON1_NAME}': om})),
        ('LOST', bline('sText_LostToOpponentByReferee', {'{B_PLAYER_MON1_NAME}': pm, '{B_OPPONENT_MON1_NAME}': om})),
        ('TIED', bline('sText_TiedOpponentByReferee', {'{B_PLAYER_MON1_NAME}': pm, '{B_OPPONENT_MON1_NAME}': om})),
        ('CANT_SWITCH', ft.conv(ft.strings_c('gText_PkmnCantSwitchOut').replace('{STR_VAR_1}', 'qqmonqq').replace('{PAUSE_UNTIL_PRESS}', ''))
                         .replace('qqmonqq', '{0102:0}'))]

def rooms():
    out = {}
    m = PAL + 'Lobby'
    common = {'WHICH_LEVEL': 'WhichChallenge', 'NOT_ENOUGH_50': 'NotEnoughValidMonsLv50',
              'NOT_ENOUGH_OPEN': 'NotEnoughValidMonsLvOpen', 'CHOOSE': 'NowSelectThreeMons',
              'SAVE_BEFORE': 'MustSaveBeforeChallenge2', 'STEP': 'FollowMe', 'GOODBYE': 'ReturnWhenFortified',
              'DIDNT_SAVE': 'FailedToSaveBeforeEndingChallenge', 'WON': 'FirmTrueBondsFor7WinStreak',
              'WON_BRAIN': 'ToDefeatMavenAnd7Trainers', 'AWARD': 'PresentYouWithBattlePoints',
              'RECORD_WON': 'FeatWillBeRecorded', 'LOST': 'ResultsWillBeRecorded', 'RESUME': 'WeHaveBeenWaiting'}
    out[m] = lobby(m, dict(common, WELCOME='WelcomeForSingleBattle', TAKE='TakeSingleBattleChallenge',
                           EXPLAIN='ExplainSingleBattleChallenge')) + [
        ('BLACK_BELT', L(m, 'LadyCanTellWhatMonsThink')), ('MAN', L(m, 'NatureAndMovesKeyHere')),
        ('BEAUTY', L(m, 'MonDocileButTransforms')), ('MANIAC', L(m, 'WhatNatureFavorsChippingAway')),
        ('RULES', L(m, 'RulesAreListed')), ('RULES_WHICH', L(m, 'ReadWhichHeading')),
        ('RULES_BASICS', L(m, 'ExplainRulesBasics')), ('RULES_NATURE', L(m, 'ExplainRulesNature')),
        ('RULES_MOVES', L(m, 'ExplainRulesMoves')), ('RULES_UNDERPOWERED', L(m, 'ExplainRulesUnderpowered')),
        ('RULES_DANGER', L(m, 'ExplainRulesWhenInDanger')),
        ('MENU_BASICS', S('gText_BattleBasics')), ('MENU_NATURE', S('gText_PokemonNature')),
        ('MENU_MOVES', S('gText_PokemonMoves')), ('MENU_UNDERPOWERED', S('gText_Underpowered')),
        ('MENU_DANGER', S('gText_WhenInDanger')), ('MENU_EXIT', S('gText_Exit')),
        # NEW: Emerald's results windows (frontier_results) as one message each
        ('RESULTS', "{0100:0}’s Battle Palace Single Battle Hall results{be01}\\nLv. 50: current streak {0100:1}, "
                    "record {0100:2}\\nOpen Level: current streak {0100:3}, record {0100:4}"),
        ('RESULTS_D', "{0100:0}’s Battle Palace Double Battle Hall results{be01}\\nLv. 50: current streak {0100:1}, "
                      "record {0100:2}\\nOpen Level: current streak {0100:3}, record {0100:4}")] + \
        lobby(m, dict(common, WELCOME='WelcomeForDoubleBattle', TAKE='TakeDoubleBattleChallenge',
                      EXPLAIN='ExplainDoubleBattleChallenge'), 'LOBBYD')
    m = PAL + 'Corridor'
    out[m] = [('PEOPLE', L(m, 'PeopleAndMonAreSame')), ('LET_MON', L(m, 'LetMonDoWhatItLikes')),
              ('CORNERED', L(m, 'MonDifferentWhenCornered')), ('UNDERSTAND', L(m, 'BeginningToUnderstandNature')),
              ('HEARTFELT', L(m, 'HeartfeltBondBetweenYouAndMons'))]
    m = PAL + 'BattleRoom'
    out[m] = [('RESTORE', L(m, 'LetMeRestoreYourMons'))] + [
        (f'READY_{n}', L(m, f'PreparedFor{w}Opponent')) for n, w in zip(range(2, 8), ('2nd', '3rd', '4th', '5th', '6th', '7th'))] + [
        ('SAVE_QUIT', L(m, 'SaveAndQuitGame')), ('RETIRE', L(m, 'WishToQuitChallenge')), ('SAVING', L(m, 'SavingData')),
        ('MAVEN_NEXT', L(m, 'ChallengingPalaceMaven')), ('MAVEN_READY', L(m, 'ReadyForPalaceMaven')),
        ('MAVEN_ARRIVES', L(m, 'AnnounceArrivalOfSpenser')), ('SPENSER_INTRO', L(m, 'SpenserFirstIntro')),
        ('SPENSER_PROVE', L(m, 'ProveYourBondWithMons')), ('SPENSER_POST_SILVER', L(m, 'SpenserPostSilverBattle')),
        ('PASS', L(m, 'LetsSeeFrontierPass')), ('GOT_SILVER', L(m, 'ReceivedSpiritsSymbol')),
        ('SPENSER_NEXT', L(m, 'SpenserAwaitNextTime')), ('SPENSER_GOLD_INTRO', L(m, 'SpenserThisTimeWontHoldBack')),
        ('SPENSER_KAAAH', L(m, 'Kaaah')), ('SPENSER_POST_GOLD', L(m, 'SpenserYourTeamIsAdmirable')),
        ('PASS2', L(m, 'HurryWithFrontierPass')), ('GOT_GOLD', L(m, 'SpiritsSymbolTookGoldenShine')),
        ('SPENSER_LAST', L(m, 'SpenserComeSeeMeAgain')),
        ('MENU_GO_ON', S('gText_GoOn')), ('MENU_REST', S('gText_Rest')), ('MENU_RETIRE', S('gText_Retire'))]
    m = ARE + 'Lobby'
    out[m] = lobby(m, {'WELCOME': 'WelcomeToBattleArena', 'TAKE': 'WishToTakeChallenge', 'EXPLAIN': 'ExplainChallenge',
                       'WHICH_LEVEL': 'WhichLevelMode', 'NOT_ENOUGH_50': 'NotEnoughValidMonsLv50',
                       'NOT_ENOUGH_OPEN': 'NotEnoughValidMonsLvOpen', 'CHOOSE': 'SelectThreeMons', 'SAVE_BEFORE': 'OkayToSave',
                       'STEP': 'GuideYouToArena', 'GOODBYE': 'AwaitAnotherChallenge',
                       'DIDNT_SAVE': 'DidntSaveBeforeShuttingDown', 'WON': 'CongratsOnSevenWins',
                       'WON_BRAIN': 'CongratsOnDefeatingTycoon', 'AWARD': 'PleaseAcceptBattlePoints',
                       'RECORD_WON': 'RecordAchievement', 'LOST': 'ThankYouWaitWhileSave',
                       'RESUME': 'LookingForwardToArrivalSaveGame'}) + [
        ('YOUNGSTER', L(m, 'BadIdeaToNotAttack')), ('MAN', L(m, 'LandingHitsWorked')), ('CAMPER', L(m, 'MatchWasDeclaredDraw')),
        ('WOMAN', L(m, 'OrderOfMonsImportant')), ('RULES', L(m, 'RulesAreListed')), ('RULES_WHICH', L(m, 'ReadWhichHeading')),
        ('RULES_BATTLE', L(m, 'ExplainBattleRules')), ('RULES_MIND', L(m, 'ExplainMindRules')),
        ('RULES_SKILL', L(m, 'ExplainSkillRules')), ('RULES_BODY', L(m, 'ExplainBodyRules')),
        ('MENU_BATTLE', S('gText_BattleRules')), ('MENU_MIND', S('gText_JudgeMind')), ('MENU_SKILL', S('gText_JudgeSkill')),
        ('MENU_BODY', S('gText_JudgeBody')), ('MENU_EXIT', S('gText_Exit')),
        ('RESULTS', "{0100:0}’s Battle Arena results{be01}\\nLv. 50: current streak {0100:1}, record {0100:2}\\n"
                    "Open Level: current streak {0100:3}, record {0100:4}")]     # NEW (frontier_results as one message)
    m = ARE + 'Corridor'
    out[m] = [('STEP_IN', L(m, 'PleaseStepIn'))]
    m = ARE + 'BattleRoom'
    out[m] = [('PLAYER_STEP', L(m, 'PlayerStepForward')), ('OPPONENT_STEP', L(m, 'OpponentStepForward')),
              ('BEGIN', L(m, 'SetKOTourneyBegin')), ('WINNER_PLAYER', L(m, 'WinnerIsPlayer')),
              ('WINNER_OPPONENT', L(m, 'WinnerIsOpponent')), ('RESTORE', L(m, 'MonsWillBeRestored'))] + [
        (f'READY_{n}', L(m, f'ReadyFor{w}Opponent')) for n, w in zip(range(2, 8), ('2nd', '3rd', '4th', '5th', '6th', '7th'))] + [
        ('SAVE_QUIT', L(m, 'SaveAndShutDown')), ('RETIRE', L(m, 'RetireFromChallenge')), ('SAVING', L(m, 'SavingPleaseWait')),
        ('TYCOON_NEXT', L(m, 'NowFaceTycoon')), ('TYCOON_READY', L(m, 'PreparedForTycoon')),
        ('MAKE_WAY', L(m, 'MakeWayForGreta')), ('GRETA_INTRO', L(m, 'GretaYoureChallenger')), ('GRETA_RIGHT', L(m, 'IsThatRight')),
        ('GRETA_WEAK', L(m, 'YouLookWeakTakeThingsEasy')), ('GRETA_IGNITE', L(m, 'IgniteMyPassionForBattle')),
        ('GRETA_POST_SILVER', L(m, 'GretaYoureToughAfterAll')), ('GOT_SILVER', L(m, 'ReceivedGutsSymbol')),
        ('GRETA_NEXT', L(m, 'GoingToBeFunNextTime')), ('GRETA_GOLD_INTRO', L(m, 'GretaLookingForwardToSeeingAgain')),
        ('GRETA_READY', L(m, 'SoAreYouReady')), ('GRETA_HALFHEARTED', L(m, 'WontAllowHalfheartedEffort')),
        ('GRETA_START', L(m, 'LetsGetThisStarted')), ('GRETA_POST_GOLD', L(m, 'GretaBlownAway')),
        ('GOT_GOLD', L(m, 'GutsSymbolTookGoldenShine')), ('GRETA_LAST', L(m, 'IfWeBattleAgainWontLose')),
        ('MENU_GO_ON', S('gText_GoOn')), ('MENU_REST', S('gText_Rest')), ('MENU_RETIRE', S('gText_Retire'))]
    return out

def trainer_block():
    d = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'frontier.json'), encoding='utf-8'))
    names = {NAME_BASE + t['index']: t['name'] for t in d['trainers']}
    names[SPENSER], names[GRETA] = 'Spenser', 'Greta'
    speech = {SPEECH_BASE + t['index']: t['before'] for t in d['trainers']}
    return names, speech

def room_numbers():
    import version
    rooms_ = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    return {k: v['text'] for k, v in rooms_.items() if k.startswith((PAL, ARE))}

def main(check=False):
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    texts = rooms()
    nums = room_numbers()
    names, speech = trainer_block()
    defines = ['// GENERATED by b2tools/frontier_pa_text.py: the Battle Palace / Battle Arena rooms\' text lines',
               '#ifndef FRONTIER_PA_LINES_H', '#define FRONTIER_PA_LINES_H']
    changed = []
    for room, lines in texts.items():
        short = room[len('BattleFrontier_Battle'):].upper()
        body = [s for _, s in lines]
        for i, (n, _) in enumerate(lines):
            if n: defines.append(f'#define PA_{short}_{n} {i}')
        battle = {PAL + 'BattleRoom': palace_battle_lines(), ARE + 'BattleRoom': arena_battle_lines()}.get(room)
        if battle is not None:
            assert len(body) <= NAME_BASE, (room, len(body))
            body += ['…'] * (BATTLE_BASE + len(battle) - len(body))
            for k, v in names.items(): body[k] = v
            for k, v in speech.items(): body[k] = v
            for i, (n, s) in enumerate(battle):
                body[BATTLE_BASE + i] = s
                defines.append(f'#define PA_L_{n} {BATTLE_BASE + i}')
        p = os.path.join(ROOT, 'src', 'text', 'script', 'emerald', f'{nums[room]:04d}_room_{room}.txt')
        text = '\n'.join(body) + '\n'
        if not os.path.exists(p) or open(p, encoding='utf-8').read() != text:
            changed.append(os.path.basename(p))
            if not check: open(p, 'w', encoding='utf-8').write(text)
    defines += [f'#define PA_NAME_BASE {NAME_BASE}', f'#define PA_SPEECH_BASE {SPEECH_BASE}',
                f'#define PA_L_NAME_SPENSER {SPENSER}', f'#define PA_L_NAME_GRETA {GRETA}', '#endif']
    hp = os.path.join(ROOT, 'src', 'include', 'frontier_pa_lines.h')
    htext = '\n'.join(defines) + '\n'
    if not os.path.exists(hp) or open(hp).read() != htext:
        changed.append('frontier_pa_lines.h')
        if not check: open(hp, 'w').write(htext)
    print(('differs: ' if check else 'written: ') + (', '.join(changed) or 'nothing'))

if __name__ == '__main__':
    main('--check' in sys.argv)
