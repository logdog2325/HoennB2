"""Emerald's Battle Frontier texts as Black 2 text lines (frontier_core, 2026-10-12; notes/FRONTIER.md), word for word
through converter/gen3text.py (Emerald's placeholders, {PLAYER} = word 0, {STR_VAR_n} = word n).

    python3 b2tools/frontier_text.py lobby <Map> [role=Label ...]   the lobby text block (hoenn_frontier.inc FRT_*:
                                                    23 lines in that order) of pokeemerald map <Map>; a role's label
                                                    is guessed from the usual names, `role=Label` names it
    python3 b2tools/frontier_text.py tutor 0|1      the BP tutor block (fr_bp_tutor: 19 lines) of Lounge7's left/right
    python3 b2tools/frontier_text.py line <Map> <Label>              one text
    python3 b2tools/frontier_text.py tower_room                      Anabel's Battle Tower battle room lines (Emerald)

Used by the build-free generators of frontier_core (the Exchange Service Corner's text, the Battle Tower's Emerald
lines) and by the facility agents for their lobbies."""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'converter'))
sys.path.insert(0, HERE)
import gen3text  # noqa: E402

EM = os.path.join(ROOT, 'external', 'pokeemerald')
MAPS = os.path.join(EM, 'data', 'maps')

def raw(path, label):
    """the .string text after `label:` (or `label::`) in a pokeemerald .inc/.s file"""
    t = open(path, encoding='utf-8').read()
    m = re.search(r'^' + re.escape(label) + r'::?\s*\n((?:\s*\.string\s+"(?:[^"\\]|\\.)*"\s*\n)+)', t, re.M)
    assert m, f'{label}: not in {path}'
    return ''.join(re.findall(r'\.string\s+"((?:[^"\\]|\\.)*)"', m.group(1)))

def strings_c(name):
    t = open(os.path.join(EM, 'src', 'strings.c'), encoding='utf-8').read()
    m = re.search(r'const u8 ' + re.escape(name) + r'\[\] = _\("((?:[^"\\]|\\.)*)"\);', t)
    assert m, name
    return m.group(1)

def conv(s):
    out, unknown = gen3text.convert(s, expand=True, version_='emerald')
    assert not unknown, f'{s!r}: codes gen3text drops: {unknown}'
    while out.endswith('{be01}\\n') or out.endswith('{be01}'):   # a text that ends on a page break (Emerald goes on
        out = out[:-len('{be01}\\n')] if out.endswith('\\n') else out[:-len('{be01}')]   # with the next message)
    return out

def line(mapname, label):
    path = os.path.join(MAPS, mapname, 'scripts.inc')
    full = label if label.startswith(mapname) or label.startswith('BattleFrontier_Text') else f'{mapname}_Text_{label}'
    try:
        return conv(raw(path, full))
    except AssertionError:
        for p in [os.path.join(MAPS, m, 'scripts.inc') for m in os.listdir(MAPS)]:
            if os.path.exists(p) and (full + ':') in open(p, encoding='utf-8').read():
                return conv(raw(p, full))
        raise

# the usual label endings of each role in Emerald's lobby scripts (first that exists wins)
ROLES = [
    ('WELCOME', ['WelcomeToBattle\\w*', 'Welcome\\w*']),
    ('TAKE', ['TakeChallenge', 'Take\\w*Challenge\\w*', 'WantToChallenge\\w*']),
    ('EXPLAIN', ['Explain\\w*Challenge\\w*', 'Explain\\w*']),
    ('WHICH_LEVEL', ['WhichLevelMode', 'WhichChallengeMode', 'Which\\w*Mode\\w*']),
    ('NOT_ENOUGH_50', ['NotEnoughValidMonsLv50\\w*']),
    ('NOT_ENOUGH_OPEN', ['NotEnoughValidMonsLvOpen\\w*']),
    ('CHOOSE', ['PleaseChooseThreeMons', 'SelectThreeMons', 'Select\\w*Mons', 'Choose\\w*Mons']),
    ('SAVE_BEFORE', ['SaveBeforeChallenge', 'OkayToSaveBefore\\w*', '\\w*SaveBefore\\w*']),
    ('STEP', ['StepThisWay', 'ShowYouToBattleRoom', '\\w*ThisWay\\w*']),
    ('GOODBYE', ['LookForwardToSeeingYou', 'LookForwardTo\\w*', '\\w*NextVisit']),
    ('DIDNT_SAVE', ['DidntSaveBeforeQuitting', 'FailedToSaveBeforeQuitting', '\\w*SaveBeforeQuitting']),
    ('WON', ['Congrats\\w*', 'PossessLuckInAbundance', '\\w*Won\\w*']),
    ('WON_BRAIN', ['\\w*Defeated\\w*', 'SnatchedVictory\\w*']),
    ('AWARD', ['AwardYouTheseBattlePoints', 'Award\\w*BattlePoints', '\\w*BattlePoints']),
    ('RECORD_WON', ['ShallRecordResults', 'RecordWillBeSaved', '\\w*Record\\w*', '\\w*Save\\w*']),
    ('LOST', ['ChallengeEndedRecordResults', 'ReturnMonsSaveResults', 'ThankYouForPlaying', '\\w*Ended\\w*']),
    ('RESUME', ['WaitingForYouToResume', 'WeveBeenWaitingForYou', '\\w*Waiting\\w*']),
]
MENU = [('MENU_CHALLENGE', 'gText_Challenge'), ('MENU_INFO', 'gText_Info3'), ('MENU_EXIT', 'gText_Exit'),
        ('MENU_LV50', 'gText_Lv50'), ('MENU_OPEN', 'gText_OpenLevel')]

def lobby_block(mapname, overrides=None):
    """[(role, label, line)] x 23 in hoenn_frontier.inc's FRT_* order (label None: no such line in this lobby)"""
    overrides = overrides or {}
    t = open(os.path.join(MAPS, mapname, 'scripts.inc'), encoding='utf-8').read()
    labels = re.findall(r'^' + re.escape(mapname) + r'_Text_(\w+)::?', t, re.M)
    out = []
    for role, pats in ROLES:
        lab = overrides.get(role)
        if not lab:
            lab = next((l for p in pats for l in labels if re.fullmatch(p, l)), None)
        if not lab:                              # a role this facility's Emerald lobby has no line for (the Pike
            out.append((role, None, '…'))        # never pauses): a placeholder the facility's flow never shows
            continue
        out.append((role, lab, line(mapname, lab)))
    for role, name in MENU:
        out.append((role, name, conv(strings_c(name))))
    out.append(('OBTAINED_BP', 'BattleFrontier_Text_ObtainedXBattlePoints',
                conv(raw(os.path.join(MAPS, 'BattleFrontier_BattleTowerLobby', 'scripts.inc'),
                         'BattleFrontier_Text_ObtainedXBattlePoints'))))
    assert len(out) == 23
    return out

def tutor_block(side):
    """fr_bp_tutor's 19 lines for Lounge7's left (0) or right (1) tutor"""
    m = 'BattleFrontier_Lounge7'
    who = ['Left', 'Right'][side]
    sm = open(os.path.join(EM, 'src', 'field_specials.c'), encoding='utf-8').read()
    key = f'SCROLL_MULTI_BF_MOVE_TUTOR_{side + 1}'
    body = sm.split('[' + key + '] =', 1)[1].split('}', 1)[0]
    items = re.findall(r'(gText_\w+)', body)
    assert len(items) == 11 and items[-1] == 'gText_Exit', items
    def item(name):
        s = strings_c(name)                      # "SOFTBOILED{CLEAR_TO 78}16BP"
        mv, bp = re.split(r'\{CLEAR_TO \w+\}', s)
        return conv(mv) + '  ' + bp.replace('BP', ' BP')
    lines = [line(m, f'{who}TutorIntro'), line(m, f'{who}TutorWelcomeBack'), line(m, 'TeachWhichMove')]
    lines += [item(n) for n in items[:10]] + [conv(strings_c('gText_Exit'))]
    lines += [line(m, 'MoveWillBeXBattlePoints'), line(m, 'HaventGotEnoughPoints'), line(m, 'TeachMoveToWhichMon'),
              line(m, 'IllTakeBattlePoints'), line(m, 'YouDontWantTo')]
    assert len(lines) == 19
    return lines

# ---- what frontier_core installs (python3 b2tools/frontier_text.py install) -------------------------------------------
OVERRIDES = os.path.join(ROOT, 'src', 'text', 'emerald', 'overrides_frontier_core.json')
TOWER_FIRST = 68                         # the Battle Tower lobby (zone 21): Sapphire's 68 lines + these

def room_text_name(room):
    """the text file of a room as the text patch names it: the room's own text number (data/hoenn_interiors.json
    own_text; src/text/script/NNNN_ is its Black 2 number, the patch moves it)"""
    import version
    r = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms'][room]
    return f'script/{r["own_text"]:04d}_room_{room}.txt'

TOWER_TEXT = room_text_name('BattleTower_Lobby')

def tower_lines():
    """the Battle Tower lobby's Emerald lines (0042_room_BattleTower_Lobby.s BTL_FR_TB = 68, BTL_FR_STREAK_49 = 91):
    Emerald's single-battle receptionist (BattleFrontier_BattleTowerLobby)"""
    m = 'BattleFrontier_BattleTowerLobby'
    block = lobby_block(m, {'WELCOME': 'WelcomSingleBattle', 'NOT_ENOUGH_50': 'NotEnoughValidMonsLv50Singles',
                            'NOT_ENOUGH_OPEN': 'NotEnoughValidMonsLvOpenSingles'})
    out = []
    for role, lab, s in block:
        if role == 'STEP': s = s.replace('{0100:1}', 'Single')                # Emerald buffers the room's kind
        out.append(s)
    out.append(line(m, 'AboutToFace50thTrainer'))
    return out

ESC = 'BattleFrontier_ExchangeServiceCorner'
ESC_TEXT = os.path.join(ROOT, 'src', 'text', 'script', 'emerald', '0648_room_' + ESC + '.txt')   # header text 648 (own 1003)
ESC_TUTOR_LEFT, ESC_TUTOR_RIGHT = 7, 26          # the tutor blocks (19 lines each) in that file

def esc_lines():
    """the Exchange Service Corner's text (src/field_scripts/emerald/0838_room_BattleFrontier_ExchangeServiceCorner.s):
    0 the clerks' welcome, 1 their goodbye, 2-6 the people, 7-25 / 26-44 the left / right BP tutor (fr_bp_tutor)"""
    out = [line(ESC, l) for l in ('WelcomePleaseChoosePrize', 'ThankYouVisitWithPoints', 'WishIHadAllDolls',
                                  'GetYouAnythingYouWant', 'ItemsWillGetMonTougher', 'GoGetYourOwnDoll',
                                  'MoreBattlePointsForRecord')]
    assert len(out) == ESC_TUTOR_LEFT
    out += tutor_block(0)
    assert len(out) == ESC_TUTOR_RIGHT
    out += tutor_block(1)
    return out

def install():
    import json
    esc = esc_lines()
    open(ESC_TEXT, 'w', encoding='utf-8').write('\n'.join(esc) + '\n')
    print(f'{ESC_TEXT}: {len(esc)} lines')
    tower = tower_lines()            # the "not enough" lines keep Emerald's {STR_VAR_1} = word 1 (fr_lobby_attendant fills it)
    data = {'_doc': 'Emerald builds (frontier_core, 2026-10-12; notes/FRONTIER.md): written by b2tools/frontier_text.py '
                    'install from pokeemerald. ' + TOWER_TEXT + ' (src/text/script/0027_room_BattleTower_Lobby.txt) lines 68-90: the Battle Frontier lobby text block of the '
                    'Battle Tower (hoenn_frontier.inc FRT_*), 91: the 50th Trainer line '
                    '(src/field_scripts/0042_room_BattleTower_Lobby.s, #ifdef HOENN_EMERALD).',
            TOWER_TEXT: {str(TOWER_FIRST + i): s for i, s in enumerate(tower)}}
    json.dump(data, open(OVERRIDES, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(OVERRIDES, 'a').write('\n')
    print(f'{OVERRIDES}: {TOWER_TEXT} {len(tower)} lines')

# ---- the Battle Tower's Salon Maiden Anabel (Emerald v1.1, 2026-10-18; python3 b2tools/frontier_text.py tower_room) ----
# Emerald's Battle Room lines for Anabel, appended in Emerald builds to the Tower battle room's text (Sapphire's 6 lines,
# src/text/script/0021_room_BattleTower_BattleRoom.txt) by src/text/emerald/overrides_frontier_tower.json; their numbers
# in src/include/frontier_tower_lines.h (src/field_scripts/0030_room_BattleTower_BattleRoom.s #ifdef HOENN_EMERALD and
# frontier_palace_arena.c's Tower battle, which reads her name line)
TOWER_ROOM = 'BattleFrontier_BattleTowerBattleRoom'
TOWER_ROOM_FIRST = 6
TOWER_ROOM_OVERRIDES = os.path.join(ROOT, 'src', 'text', 'emerald', 'overrides_frontier_tower.json')
TOWER_ROOM_LINES_H = os.path.join(ROOT, 'src', 'include', 'frontier_tower_lines.h')

def tower_room_lines():
    """[(define, line)]: pokeemerald BattleFrontier_BattleTowerBattleRoom's Salon Maiden texts in the order its script
    uses them, then Anabel's name (src/data/trainers.h gTrainers[TRAINER_ANABEL].trainerName, Black 2's spelling)"""
    labels = [('BTB_L_MAIDEN_ON_HER_WAY', 'SalonMaidenOnHerWay'), ('BTB_L_MAIDEN_READY', 'ReadyForSalonMaiden'),
              ('BTB_L_ANABEL_GREETINGS', 'GreetingsImAnabel'), ('BTB_L_ANABEL_LET_ME_SEE', 'LetMeSeeYourTalent'),
              ('BTB_L_ANABEL_POST_SILVER', 'AnabelTalentShallBeRecognized'), ('BTB_L_GOT_SILVER', 'ReceivedAbilitySymbol'),
              ('BTB_L_ANABEL_UNTIL_NEXT', 'UntilNextTime'), ('BTB_L_ANABEL_CAME_BACK', 'AnabelYouCameBack'),
              ('BTB_L_ANABEL_LETS_BEGIN', 'LetsBeginShallWe'), ('BTB_L_ANABEL_POST_GOLD', 'AnabelCongratsYourPassPlease'),
              ('BTB_L_GOT_GOLD', 'AbilitySymbolTookGoldenShine'), ('BTB_L_ANABEL_LAST', 'WishICouldBattleYouAgain')]
    out = [(d, line(TOWER_ROOM, l)) for d, l in labels]
    tr = open(os.path.join(EM, 'src', 'data', 'trainers.h'), encoding='utf-8').read()
    name = re.search(r'\[TRAINER_ANABEL\] =\s*\{[^}]*?\.trainerName = _\("([^"]*)"\)', tr, re.S).group(1)
    out.append(('BTB_L_ANABEL_NAME', conv(name).capitalize()))
    return out

def tower_room_install():
    import json
    import version
    r = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']['BattleTower_BattleRoom']
    src = os.path.join(ROOT, 'src', 'text', 'script', f'{r["text"]:04d}_room_BattleTower_BattleRoom.txt')
    have = len(open(src, encoding='utf-8').read().rstrip('\n').split('\n'))
    assert have == TOWER_ROOM_FIRST, f'{src}: {have} lines, the Emerald lines start at {TOWER_ROOM_FIRST}'
    rows = tower_room_lines()
    name = room_text_name('BattleTower_BattleRoom')
    data = {'_doc': 'Emerald builds (Anabel, 2026-10-18): written by b2tools/frontier_text.py tower_room from pokeemerald. '
                    + name + ' (src/text/script/0021_room_BattleTower_BattleRoom.txt) lines '
                    f'{TOWER_ROOM_FIRST}-{TOWER_ROOM_FIRST + len(rows) - 1}: the Salon Maiden Anabel\'s Battle Room lines and her '
                    'name (src/include/frontier_tower_lines.h).',
            name: {str(TOWER_ROOM_FIRST + i): s for i, (d, s) in enumerate(rows)}}
    json.dump(data, open(TOWER_ROOM_OVERRIDES, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(TOWER_ROOM_OVERRIDES, 'a').write('\n')
    h = ['// GENERATED by b2tools/frontier_text.py tower_room: the Battle Tower battle room\'s Emerald lines (Anabel)',
         '#ifndef FRONTIER_TOWER_LINES_H', '#define FRONTIER_TOWER_LINES_H']
    h += [f'#define {d} {TOWER_ROOM_FIRST + i}' for i, (d, s) in enumerate(rows)]
    h += ['#endif', '']
    open(TOWER_ROOM_LINES_H, 'w').write('\n'.join(h))
    print(f'{TOWER_ROOM_OVERRIDES}: {name} {len(rows)} lines; {TOWER_ROOM_LINES_H}')

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'lobby':
        ov = dict(x.split('=', 1) for x in a[2:])
        for i, (role, lab, s) in enumerate(lobby_block(a[1], ov)):
            print(f'{i:2d} {role:15s} {lab or "(none)":40s} {s}')
    elif a and a[0] == 'tutor':
        for i, s in enumerate(tutor_block(int(a[1]))): print(f'{i:2d} {s}')
    elif a and a[0] == 'install':
        install()
    elif a and a[0] == 'tower_room':
        tower_room_install()
    elif a and a[0] == 'line':
        print(line(a[1], a[2]))
    else:
        print(__doc__)
