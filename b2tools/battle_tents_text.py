"""The three Battle Tents' room texts (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md): Emerald's own lines, word for
word through frontier_core's b2tools/frontier_text.py (converter/gen3text.py), in the order the scripts name them.
Writes the nine rooms' text files and src/include/battle_tents_lines.h (BT_<ROOM>_<NAME> = line).

    python3 b2tools/battle_tents_text.py            (writes; --check compares)

Files: src/text/script/emerald/NNNN_room_<Room>.txt (NNNN = the zone's Black 2 text number; the text patch moves it to
the room's own number, data/emerald/hoenn_interiors.json own_text). Each lobby's first 20 lines are the tent lobby block
(battle_tents_lib.inc TT_*: the same order in every tent; '…' where a tent has no such line). Each battle room's file
also holds its tent's 30 trainers' names (lines 100-129) and before-battle speeches (200-229): the engines read them
there (frontier_factory_dome.py TENT_NAME_BASE / TENT_SPEECH_BASE). Sources: pokeemerald data/text/battle_tent.inc, the
tents' and the Battle Frontier's map scripts, src/strings.c. Lines marked NEW are not Emerald's."""
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import frontier_text as ft  # noqa: E402

V, F, SL = 'VerdanturfTown_BattleTent', 'FallarborTown_BattleTent', 'SlateportCity_BattleTent'
NAME_BASE, SPEECH_BASE = 100, 200
TENT_INC = os.path.join(ft.EM, 'data', 'text', 'battle_tent.inc')
TENT_OF = {V: 'verdanturf', F: 'fallarbor', SL: 'slateport'}


def T(label):
    """an Emerald text by label: data/text/battle_tent.inc, else the maps' scripts (frontier_text.line)"""
    if (label + ':') in open(TENT_INC, encoding='utf-8').read():
        return ft.conv(ft.raw(TENT_INC, label))
    m = re.match(r'(\w+?)_Text_', label)
    return ft.line(m.group(1), label)


def S(name): return ft.conv(ft.strings_c(name))


BAG_FULL = None                         # gText_TooBadBagIsFull (data/text/obtain_item.inc), set in rooms()


NONE = '…'
# the tent lobby block (battle_tents_lib.inc TT_*), in this order
LOBBY_ROLES = ['WELCOME', 'TAKE', 'EXPLAIN', 'NOT_ENOUGH', 'CHOOSE', 'SAVE_BEFORE', 'STEP', 'GOODBYE', 'DIDNT_SAVE', 'WON',
               'WON_SAVE', 'PRIZE', 'RECEIVED', 'NO_ROOM', 'LOST', 'RESUME', 'RESUME_SAVE', 'GOODBYE2',
               'MENU_CHALLENGE', 'MENU_INFO', 'MENU_EXIT']


def lobby_block(prefix, labels):
    out = []
    for role in LOBBY_ROLES:
        lab = labels.get(role)
        if role == 'MENU_CHALLENGE': out.append((f'LOBBY_{role}', S('gText_Challenge'))); continue
        if role == 'MENU_INFO': out.append((f'LOBBY_{role}', S('gText_Info3'))); continue
        if role == 'MENU_EXIT': out.append((f'LOBBY_{role}', S('gText_Exit'))); continue
        out.append((f'LOBBY_{role}', T(lab if '_Text_' in lab else f'{prefix}_Text_{lab}') if lab else NONE))
    return out


def rooms():
    global BAG_FULL
    BAG_FULL = ft.conv(ft.raw(os.path.join(ft.EM, 'data', 'text', 'obtain_item.inc'), 'gText_TooBadBagIsFull'))
    out = {}
    m = V + 'Lobby'
    out[m] = lobby_block(m, dict(
        WELCOME='WelcomeToBattleTent', TAKE='TakeChallenge', EXPLAIN='ExplainVerdanturfTent',
        NOT_ENOUGH='NotEnoughValidMonsLvOpen', CHOOSE='SelectThreeMons', SAVE_BEFORE='SaveBeforeChallenge', STEP='NowFollowMe',
        GOODBYE='ReturnFortified', DIDNT_SAVE='BattleFrontier_BattlePalaceLobby_Text_FailedToSaveBeforeEndingChallenge',
        WON='AchievedThreeWinStreak', WON_SAVE='FeatWillBeRecorded', PRIZE='PresentYouWithPrize',
        RECEIVED='BattleFrontier_BattleDomeLobby_Text_ReceivedPrize',
        NO_ROOM='BattleFrontier_BattlePalaceLobby_Text_NoSpaceForPrize', LOST='ResultsWillBeRecorded',
        RESUME='BattleFrontier_BattlePalaceLobby_Text_WeHaveBeenWaiting',
        RESUME_SAVE='BattleFrontier_BattlePalaceLobby_Text_MustSaveBeforeChallenge', GOODBYE2='ReturnFortified')) + [
        ('ATTRACT', ft.line(m, f'{m}_Text_AttractionRunsDeep')), ('ATTRACT_AFTER', ft.line(m, f'{m}_Text_AttractionMutual')),
        ('BOY1', ft.line(m, f'{m}_Text_TaughtWhatKindsOfMoves')), ('BOY2', ft.line(m, f'{m}_Text_MonsReluctantToUseDislikedMoves')),
        ('LITTLE_BOY', ft.line(m, f'{m}_Text_GentleMonsScaryIfAngry')),
        ('SCOTT', ft.line(m, f'{m}_Text_ScottCanMeetToughTrainers')), ('SCOTT_AFTER', ft.line(m, f'{m}_Text_ScottVisitRegularly')),
        ('BAG_FULL', BAG_FULL),
        ('RULES', T(f'{m}_Text_RulesAreListed')), ('RULES_WHICH', T('BattleFrontier_BattlePalaceLobby_Text_ReadWhichHeading')),
        ('RULES_LEVEL', T('BattleTentLobby_Text_ExplainLevelRules')),
        ('RULES_BASICS', T('BattleFrontier_BattlePalaceLobby_Text_ExplainRulesBasics')),
        ('RULES_NATURE', T('BattleFrontier_BattlePalaceLobby_Text_ExplainRulesNature')),
        ('RULES_MOVES', T('BattleFrontier_BattlePalaceLobby_Text_ExplainRulesMoves')),
        ('RULES_UNDERPOWERED', T('BattleFrontier_BattlePalaceLobby_Text_ExplainRulesUnderpowered')),
        ('RULES_DANGER', T('BattleFrontier_BattlePalaceLobby_Text_ExplainRulesWhenInDanger')),
        ('MENU_TRAINERS', S('gText_BattleTrainers')), ('MENU_BASICS', S('gText_BattleBasics')),
        ('MENU_NATURE', S('gText_PokemonNature')), ('MENU_MOVES', S('gText_PokemonMoves')),
        ('MENU_UNDERPOWERED', S('gText_Underpowered')), ('MENU_DANGER', S('gText_WhenInDanger')), ('MENU_EXIT', S('gText_Exit'))]
    m = F + 'Lobby'
    out[m] = lobby_block(m, dict(
        WELCOME='WelcomeToBattleTent', TAKE='TakeChallenge', EXPLAIN='ExplainFallarborTent',
        NOT_ENOUGH='NotEnoughValidMonsLvOpen', CHOOSE='SelectThreeMons', SAVE_BEFORE='SaveBeforeChallenge',
        STEP='GuideYouToBattleTent', GOODBYE='AwaitAnotherChallenge', DIDNT_SAVE='DidntSaveBeforeQuitting',
        WON='BeatThreeTrainers', WON_SAVE='WaitWhileSaveGame', PRIZE='PresentYouWithPrize', RECEIVED='ReceivedPrize',
        NO_ROOM='BagFullReturnForPrize', LOST='ThankYouWaitWhileSaving', RESUME='LookingForwardToArrival',
        GOODBYE2='AwaitAnotherChallenge2')) + [
        ('HIKER', ft.line(m, f'{m}_Text_CameToCampOut')), ('LITTLE_BOY', ft.line(m, f'{m}_Text_MakeThinkImJustKid')),
        ('LASS', ft.line(m, f'{m}_Text_FallarborTentMyFavorite')),
        ('SCOTT', ft.line(m, f'{m}_Text_ScottLookingForSomeone')), ('SCOTT_AFTER', ft.line(m, f'{m}_Text_ScottMakeChallenge')),
        ('RULES', T('BattleFrontier_BattleArenaLobby_Text_RulesAreListed')),
        ('RULES_WHICH', T('BattleFrontier_BattleArenaLobby_Text_ReadWhichHeading')),
        ('RULES_LEVEL', T('BattleTentLobby_Text_ExplainLevelRules')),
        ('RULES_BATTLE', T('BattleFrontier_BattleArenaLobby_Text_ExplainBattleRules')),
        ('RULES_MIND', T('BattleFrontier_BattleArenaLobby_Text_ExplainMindRules')),
        ('RULES_SKILL', T('BattleFrontier_BattleArenaLobby_Text_ExplainSkillRules')),
        ('RULES_BODY', T('BattleFrontier_BattleArenaLobby_Text_ExplainBodyRules')),
        ('MENU_TRAINERS', S('gText_BattleTrainers')), ('MENU_BATTLE', S('gText_BattleRules')),
        ('MENU_MIND', S('gText_JudgeMind')), ('MENU_SKILL', S('gText_JudgeSkill')), ('MENU_BODY', S('gText_JudgeBody')),
        ('MENU_EXIT', S('gText_Exit'))]
    m = SL + 'Lobby'
    out[m] = lobby_block(m, dict(
        WELCOME='WelcomeToBattleTent', TAKE='TakeChallenge', EXPLAIN='ExplainSlateportTent', SAVE_BEFORE='SaveBeforeChallenge',
        STEP='StepThisWay', GOODBYE='LookForwardToNextVisit', DIDNT_SAVE='DidntSaveBeforeQuitting',
        WON='WonThreeMatchesReturnMons', PRIZE='AwardYouThisPrize', RECEIVED='BattleFrontier_BattleTowerLobby_Text_ReceivedPrize',
        NO_ROOM='NoRoomInBagMakeRoom', LOST='ReturnRentalMonsSaveResults', RESUME='BeenWaitingForYou',
        GOODBYE2='LookForwardToNextVisit')) + [
        ('TORMENT', ft.line(m, f'{m}_Text_CouldntFindMonForMe')), ('TORMENT_AFTER', ft.line(m, f'{m}_Text_ExplainTorment')),
        ('MAN', ft.line(m, f'{m}_Text_IllTryUsingBugMons')), ('GIRL', ft.line(m, f'{m}_Text_BattleEvenWithoutToughMons')),
        ('WOMAN', ft.line(m, f'{m}_Text_NiceIfMoreSelection')),
        ('BAG_FULL', BAG_FULL),
        ('RULES', T('BattleFrontier_BattleFactoryLobby_Text_RulesAreListed')),
        ('RULES_WHICH', T('BattleFrontier_BattleFactoryLobby_Text_ReadWhichHeading')),
        ('RULES_BASICS', T(f'{m}_Text_ExplainBasicRules')), ('RULES_SWAP_PARTNER', T(f'{m}_Text_ExplainSwapPartnerRules')),
        ('RULES_SWAP_NUMBER', T(f'{m}_Text_ExplainSwapNumberRules')), ('RULES_SWAP_NOTES', T(f'{m}_Text_ExplainSwapNotes')),
        ('RULES_MONS', T(f'{m}_Text_ExplainMonRules')),
        ('MENU_BASICS', S('gText_BasicRules')), ('MENU_SWAP_PARTNER', S('gText_SwapPartners')),
        ('MENU_SWAP_NUMBER', S('gText_SwapNumber')), ('MENU_SWAP_NOTES', S('gText_SwapNotes')),
        ('MENU_MONS', S('gText_BattlePokemon')), ('MENU_EXIT', S('gText_Exit'))]
    for c in (V, F):
        out[c + 'Corridor'] = [('NONE', NONE)]
    m = SL + 'Corridor'
    P = 'BattleFrontier_BattleFactoryPreBattleRoom_Text_'
    out[m] = [('HOLD_CHOOSE', T(P + 'HoldMonsChooseFromSelection')), ('THIS_WAY', T(P + 'RightThisWay')),
              ('RESTORE', T(P + 'LetUsRestoreMons')), ('READY_2', T(P + 'ReadyFor2ndOpponent')),
              ('READY_3', T(P + 'ReadyFor3rdOpponent')), ('SAVE_QUIT', T(P + 'SaveAndQuitGame')),
              ('RETIRE', T(P + 'RetireFromChallenge')), ('LIKE_SWAP', T(P + 'LikeToSwapMon')),
              ('SWAP_DONE', T(P + 'YourSwapIsComplete')), ('SAVING', T(P + 'SavingDataPleaseWait')),
              ('MENU_GO_ON', S('gText_GoOn')), ('MENU_REST', S('gText_Rest')), ('MENU_RETIRE', S('gText_Retire'))]
    P = 'BattleFrontier_BattlePalaceBattleRoom_Text_'
    out[V + 'BattleRoom'] = [('RESTORE', T(P + 'LetMeRestoreYourMons')), ('READY_2', T(P + 'PreparedFor2ndOpponent')),
                             ('READY_3', T(P + 'PreparedFor3rdOpponent')), ('SAVE_QUIT', T(P + 'SaveAndQuitGame')),
                             ('RETIRE', T(P + 'WishToQuitChallenge')), ('SAVING', T(P + 'SavingData')),
                             ('MENU_GO_ON', S('gText_GoOn')), ('MENU_REST', S('gText_Rest')), ('MENU_RETIRE', S('gText_Retire'))]
    P = 'BattleFrontier_BattleArenaBattleRoom_Text_'
    out[F + 'BattleRoom'] = [('BEGIN', T(P + 'SetKOTourneyBegin')), ('WINNER_OPPONENT', T(P + 'WinnerIsOpponent')),
                             ('WINNER_PLAYER', T(P + 'WinnerIsPlayer')), ('RESTORE', T(P + 'MonsWillBeRestored')),
                             ('READY_2', T(P + 'ReadyFor2ndOpponent')), ('READY_3', T(P + 'ReadyFor3rdOpponent')),
                             ('SAVE_QUIT', T(P + 'SaveAndShutDown')), ('RETIRE', T(P + 'RetireFromChallenge')),
                             ('SAVING', T(P + 'SavingPleaseWait')),
                             ('MENU_GO_ON', S('gText_GoOn')), ('MENU_REST', S('gText_Rest')), ('MENU_RETIRE', S('gText_Retire'))]
    out[SL + 'BattleRoom'] = [('NONE', NONE)]
    return out


def room_numbers():
    import version
    rooms_ = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    return {k: v['text'] for k, v in rooms_.items() if 'BattleTent' in k}


def short(room):
    a, b = room.split('_BattleTent')
    return {'VerdanturfTown': 'V', 'FallarborTown': 'F', 'SlateportCity': 'S'}[a] + '_' + b.upper()


def main(check=False):
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    texts = rooms()
    nums = room_numbers()
    tents = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'battle_tents.json'), encoding='utf-8'))
    defines = ['// GENERATED by b2tools/battle_tents_text.py: the Battle Tents\' rooms\' text lines (battle_tents)',
               '#ifndef BATTLE_TENTS_LINES_H', '#define BATTLE_TENTS_LINES_H']
    changed = []
    for room, lines in texts.items():
        body = [s for _, s in lines]
        for i, (n, _) in enumerate(lines):
            if n != 'NONE': defines.append(f'#define BT_{short(room)}_{n} {i}')
        if room.endswith('BattleRoom'):
            tent = tents['tents'][TENT_OF[room[:-len('BattleRoom')]]]
            assert len(body) <= NAME_BASE, (room, len(body))
            body += [NONE] * (SPEECH_BASE + len(tent['trainers']) - len(body))
            for t in tent['trainers']:
                body[NAME_BASE + t['index']] = t['name']
                body[SPEECH_BASE + t['index']] = t['before']
        p = os.path.join(ROOT, 'src', 'text', 'script', 'emerald', f'{nums[room]:04d}_room_{room}.txt')
        text = '\n'.join(body) + '\n'
        if not os.path.exists(p) or open(p, encoding='utf-8').read() != text:
            changed.append(os.path.basename(p))
            if not check: open(p, 'w', encoding='utf-8').write(text)
    for t, d in tents['tents'].items():
        defines.append(f'#define BT_PRIZE_{t.upper()} {d["prize_ids"][0]}     // {d["prizes"][0]}')
    defines += [f'#define BT_NAME_BASE {NAME_BASE}', f'#define BT_SPEECH_BASE {SPEECH_BASE}', '#endif']
    hp = os.path.join(ROOT, 'src', 'include', 'battle_tents_lines.h')
    htext = '\n'.join(defines) + '\n'
    if not os.path.exists(hp) or open(hp).read() != htext:
        changed.append('battle_tents_lines.h')
        if not check: open(hp, 'w').write(htext)
    print(('differs: ' if check else 'written: ') + (', '.join(changed) or 'nothing'))


if __name__ == '__main__':
    main('--check' in sys.argv)
