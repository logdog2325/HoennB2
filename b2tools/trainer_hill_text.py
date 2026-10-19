"""The Trainer Hill's room texts (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md): Emerald's own lines, word for
word through frontier_core's b2tools/frontier_text.py (converter/gen3text.py), in the order the scripts name them.
Writes the seven rooms' text files and src/include/trainer_hill_lines.h (TH_<ROOM>_<NAME> = line).

    python3 b2tools/trainer_hill_text.py            (writes; --check compares)

Files: src/text/script/emerald/NNNN_room_<Room>.txt (NNNN = the zone's Black 2 text number; the text patch moves it to
the room's own number). The Entrance's first five lines are the nurse's (src/field_scripts/centers/nurse.inc reads
lines 0-4: pokeemerald's Common_EventScript_PkmnCenterNurse words). Each floor's file holds, from line 100, its eight
trainers (the four modes' two: uid u = 1 + 2 * mode + i at 100 + 5 * (u - 1)): name, speechBefore, speechWin, speechLose,
speechAfter (b2tools/patches/trainer_hill.c reads the name and speechLose there). Sources: pokeemerald
data/maps/TrainerHill_*/scripts.inc, data/text/pkmn_center_nurse.inc, data/event_scripts.s, src/strings.c, the floors'
speeches from data/emerald/trainer_hill.json (converter/gen_trainer_hill.py). Lines marked NEW are not Emerald's."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import frontier_text as ft  # noqa: E402

E = 'TrainerHill_Entrance'
NONE = '…'
LINE_BASE = 100


def L(label):
    full = label if label.startswith('TrainerHill_') else f'{E}_Text_{label}'
    return ft.line(full.split('_Text_')[0], full)
def S(name): return ft.conv(ft.strings_c(name))
def R(path, label): return ft.conv(ft.raw(os.path.join(ft.EM, path), label))


def rooms():
    out = {}
    nurse = [('NURSE_WELCOME', R('data/text/pkmn_center_nurse.inc', 'gText_WouldYouLikeToRestYourPkmn')),
             ('NURSE_TAKE', R('data/text/pkmn_center_nurse.inc', 'gText_IllTakeYourPkmn')),
             ('NURSE_DONE', R('data/text/pkmn_center_nurse.inc', 'gText_RestoredPkmnToFullHealth')),
             ('NURSE_BYE', R('data/text/pkmn_center_nurse.inc', 'gText_WeHopeToSeeYouAgain')),
             ('NURSE_POKERUS', R('data/event_scripts.s', 'gText_PokerusExplanation'))]
    time = '{0100:1} min. {0100:2}.{0100:3} sec.'          # TrainerHill_Entrance_Text_ChallengeTime / gText_XMinYDotZSec
    assert ft.conv(ft.raw(os.path.join(ft.MAPS, E, 'scripts.inc'), f'{E}_Text_ChallengeTime')).replace(
        '{0100:1}', 'a').replace('{0100:2}', 'b').replace('{0100:3}', 'c') == 'a min. b.c sec.'
    board = S('gText_TimeBoard')
    modes = [S(f'gText_{m}TagMatch') for m in ('Normal', 'Variety', 'Unique', 'Expert')]
    cleared = S('gText_TimeCleared').strip()
    # NEW (Emerald shows the Time Board in a window): the board's four rows as one message
    rows = [f'{modes[m]}\\n{cleared} {{0100:{1 + 3 * m}}} min. {{0100:{2 + 3 * m}}}.{{0100:{3 + 3 * m}}} sec.' for m in range(4)]
    out[E] = nurse + [
        ('STILL_GETTING_READY', L('StillGettingReady')), ('WELCOME', L('WelcomeToTrainerHill')),
        ('SAVE_FIRST', L('SaveGameBeforeEnter')), ('EVERY_ROOM', L('TrainersInEveryRoom')),
        ('LIKE_TO_CHALLENGE', L('LikeToChallengeTrainers')), ('GET_SET_GO', L('TimeProgessGetSetGo')),
        ('VISIT_AGAIN', L('PleaseVisitUsAgain')), ('TOO_BAD', L('TooBadTremendousEffort')),
        ('GIVE_YOUR_BEST', L('HopeYouGiveItYourBest')), ('THANKS', L('ThankYouForPlaying')),
        ('EXPLAIN', L('ExplainTrainerHill')), ('MAN', L('WhatSortOfTrainersAreAhead')),
        ('MAN_CLOSED', L('CantWaitToTestTheWaters')), ('GIRL', L('FriendsTryingToReachTimeBoardTop')),
        ('GIRL_CLOSED', L('DoYouKnowWhenTheyOpen')),
        ('MENU_YES', S('gText_Yes')), ('MENU_NO', S('gText_No')), ('MENU_INFO', S('gText_Info')),
        ('MENU_NORMAL', modes[0]), ('MENU_VARIETY', modes[1]), ('MENU_UNIQUE', modes[2]), ('MENU_EXPERT', modes[3]),
        ('MENU_EXIT', S('gText_Exit')),
        ('BOARD', board + '{be01}\\n' + '{be01}\\n'.join(rows))]
    d = json.load(open(os.path.join(ROOT, 'data', 'emerald', 'trainer_hill.json'), encoding='utf-8'))
    for f in range(4):
        room = f'TrainerHill_{f + 1}F'
        lines = [('TIME', time)]
        tr = {}
        for m in d['modes']:
            for i, t in enumerate(m['floors'][f]['trainers']):
                u = 1 + 2 * m['mode'] + i
                for k, key in enumerate(('name', 'before', 'win', 'lose', 'after')):
                    tr[LINE_BASE + 5 * (u - 1) + k] = t[key]
        out[room] = (lines, tr)
    out['TrainerHill_Roof'] = [
        ('OWNER_CAME', L('TrainerHill_Roof_Text_YouFinallyCameBravo')), ('OWNER_GIFT', L('TrainerHill_Roof_Text_HaveTheMostMarvelousGift')),
        ('OWNER_FULL', L('TrainerHill_Roof_Text_FullUpBeBackLaterForThis')), ('OWNER_QUICK', L('TrainerHill_Roof_Text_GotHereMarvelouslyQuickly')),
        ('OWNER_SLOW', L('TrainerHill_Roof_Text_YouWerentVeryQuick')), ('OWNER_ZIPPIER', L('TrainerHill_Roof_Text_ArriveZippierNextTime')),
        ('OBTAINED', R('data/text/obtain_item.inc', 'gText_ObtainedTheItem')), ('BAG_FULL', R('data/text/obtain_item.inc', 'gText_TheBagIsFull'))]
    out['TrainerHill_Elevator'] = [('RETURN', L('TrainerHill_Elevator_Text_ReturnToReception'))]
    return out


def engine_defines():
    """the engine's numbers the scripts use (b2tools/patches/trainer_hill.py and .c are their source): ThHill's op codes
    (TH_<OP> << 8 | argument), the trainer slots, the spotted works, the hide flags, the zones"""
    import re, importlib.util
    spec = importlib.util.spec_from_file_location('trainer_hill_patch', os.path.join(HERE, 'patches', 'trainer_hill.py'))
    th = importlib.util.module_from_spec(spec); spec.loader.exec_module(th)
    c = open(os.path.join(HERE, 'patches', 'trainer_hill.c'), encoding='utf-8').read()
    names = re.findall(r'TH_\w+', re.search(r'enum \{ (TH_START = 1,.*?)\};', c, re.S).group(1))
    assert names[0] == 'TH_START' and len(names) > 10, names
    out = [f'#define TH_OP_{n[3:]} {(i + 1) << 8:#x}' for i, n in enumerate(names)]
    out += [f'#define TH_TR_A {th.TR_A}', f'#define TH_TR_B {th.TR_B}', f'#define TH_HIDE_FLAG {th.HIDE_FLAG:#x}',
            f'#define TH_SCR_SPOTTED {th.SCR_SPOTTED}']
    out += [f'#define {k} {v:#x}' for k, v in th.W.items()]
    rooms_ = __import__('version').load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    out += [f'#define TH_Z_{r[len("TrainerHill_"):].upper()} {rooms_[r]["zone"]}' for r in th.HILL_ROOMS]
    return out


def room_numbers():
    import version
    rooms_ = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    return {k: v['text'] for k, v in rooms_.items() if k.startswith('TrainerHill_')}


def main(check=False):
    os.environ.setdefault('HOENN_VERSION', 'emerald')
    texts = rooms()
    nums = room_numbers()
    defines = ['// GENERATED by b2tools/trainer_hill_text.py: the Trainer Hill rooms\' text lines (battle_tents)',
               '#ifndef TRAINER_HILL_LINES_H', '#define TRAINER_HILL_LINES_H']
    changed = []
    for room, v in texts.items():
        lines, extra = v if isinstance(v, tuple) else (v, {})
        short = room[len('TrainerHill_'):].upper()
        body = [s for _, s in lines]
        for i, (n, _) in enumerate(lines): defines.append(f'#define TH_{short}_{n} {i}')
        if extra:
            body += [NONE] * (max(extra) + 1 - len(body))
            for k, s in extra.items(): body[k] = s
        p = os.path.join(ROOT, 'src', 'text', 'script', 'emerald', f'{nums[room]:04d}_room_{room}.txt')
        text = '\n'.join(body) + '\n'
        if not os.path.exists(p) or open(p, encoding='utf-8').read() != text:
            changed.append(os.path.basename(p))
            if not check: open(p, 'w', encoding='utf-8').write(text)
    defines += [f'#define TH_LINE_BASE {LINE_BASE}'] + engine_defines() + ['#endif']
    hp = os.path.join(ROOT, 'src', 'include', 'trainer_hill_lines.h')
    htext = '\n'.join(defines) + '\n'
    if not os.path.exists(hp) or open(hp).read() != htext:
        changed.append('trainer_hill_lines.h')
        if not check: open(hp, 'w').write(htext)
    print(('differs: ' if check else 'written: ') + (', '.join(changed) or 'nothing'))


if __name__ == '__main__':
    main('--check' in sys.argv)
