#!/usr/bin/env python3
"""The Contest counters' and Blender people's lines (src/field_scripts/common/contests.inc CL_*): each lobby's text file gets them
from its line t on, replacing the Musical's lines. Sapphire's and Ruby's lobbies from pokeruby's data/text/contest_hall.inc,
Emerald's from pokeemerald's data/scripts/contest_hall.inc and berry_blender.inc.

    python3 b2tools/gen_contest_text.py       rewrites the lobbies' text files
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')

# (lobby's text file, line t): contests.inc's `contest_reception t` in the .s file (Musical's T_Musical)
LOBBIES = {'src/text/script/0070_room_VerdanturfTown_ContestLobby.txt': (7, 'ruby'),
           'src/text/script/0103_room_FallarborTown_ContestLobby.txt': (6, 'ruby'),
           'src/text/script/0351_room_SlateportCity_ContestLobby.txt': (8, 'ruby'),
           'src/text/script/0219_room_LilycoveCity_ContestLobby.txt': (12, 'ruby'),
           'src/text/script/emerald/0219_room_LilycoveCity_ContestLobby.txt': (14, 'emerald')}


def _labels(*paths):
    out = {}
    for p in paths:
        src = open(p, errors='replace').read()
        for m in re.finditer(r'((?:^\w+::?(?:[ \t]*@[^\n]*)?\s*\n)+)((?:\s*\.string "[^\n]*"\s*\n)+)', src, re.M):
            text = ''.join(re.findall(r'\.string "(.*)"', m.group(2)))
            for label in re.findall(r'^(\w+)::?', m.group(1), re.M):
                out[label] = text
    return out


def clean(s):
    s = s.replace('$', '').replace('\\p', '{be01}\\n').replace('\\l', '\\n').replace('{PLAYER}', '{0100:0}')
    for n, r in ((1, 0), (2, 1), (3, 2)):
        s = s.replace('{STR_VAR_%d}' % n, '{0100:%d}' % r)
    for a, b in (('POKéMON', 'Pokémon'), ('{POKEBLOCK}', 'Pokéblock'), ('POKéBLOCK', 'Pokéblock'), ('JUDGE', 'Judge'),
                 ('CONTESTS', 'Contests'), ('CONTEST', 'Contest'), ('TRAINERS', 'Trainers'), ('TRAINER', 'Trainer'), ('RIBBON', 'Ribbon'),
                 ('COOLNESS', 'Coolness'), ('BEAUTY', 'Beauty'), ('CUTENESS', 'Cuteness'), ('SMARTNESS', 'Smartness'),
                 ('TOUGHNESS', 'Toughness'), ('COOL', 'Cool'), ('CUTE', 'Cute'), ('SMART', 'Smart'), ('TOUGH', 'Tough'),
                 ('NORMAL', 'Normal'), ('SUPER', 'Super'), ('HYPER', 'Hyper'), ('MASTER', 'Master'), ('RANK', 'Rank'),
                 ('BERRIES', 'Berries'), ('BERRY', 'Berry'), ('BLENDER', 'Blender'), ('BAG', 'Bag'), ('PASS', 'Pass'),
                 ('LUXURY BALL', 'Luxury Ball'), ('…', '...'), ("'", '’')):
        s = s.replace(a, b)
    return s


RUBY_KEYS = ['FallarborTown_ContestLobby_Text_1A5E46', 'FallarborTown_ContestLobby_Text_1A5E7C', 'LilycoveCity_ContestLobby_Text_ExplainContests',
             'LilycoveCity_ContestLobby_Text_ExplainContestTypes', 'LilycoveCity_ContestLobby_Text_ExplainContestRanks',
             'LilycoveCity_ContestLobby_Text_ParticipateAnotherTime', 'FallarborTown_ContestLobby_Text_EnterWhichPokemon1',
             'FallarborTown_ContestLobby_Text_1A6340', 'FallarborTown_ContestLobby_Text_1A64F4', 'FallarborTown_ContestLobby_Text_1A6583',
             'FallarborTown_ContestLobby_Text_1A6590', 'FallarborTown_ContestLobby_Text_1A65EA', 'FallarborTown_ContestLobby_Text_1A6623',
             'LilycoveCity_ContestLobby_Text_MonNotQualifiedForRank', 'LilycoveCity_ContestLobby_Text_ConfirmContestMon',
             'FallarborTown_ContestLobby_Text_1A6724', 'LilycoveCity_ContestLobby_Text_EggCannotTakePart',
             'LilycoveCity_ContestLobby_Text_MonInNoConditionForContest', 'FallarborTown_ContestLobby_Text_1A67C1',
             'FallarborTown_ContestLobby_Text_1A685A', 'FallarborTown_ContestLobby_Text_1A68C6', 'LinkContestRoom1_Text_1A6D6A',
             'LinkContestRoom1_Text_1A6D96', 'LinkContestRoom1_Text_1A6DAC', 'LinkContestRoom1_Text_1A6DF1', 'LinkContestRoom1_Text_1A6E1F']
EMERALD_KEYS = {'LilycoveCity_ContestLobby_Text_EnterContest1': 0, 'LilycoveCity_ContestLobby_Text_WhichTopic1': 1,
                'LilycoveCity_ContestLobby_Text_ExplainContests': 2, 'LilycoveCity_ContestLobby_Text_ExplainContestTypes': 3,
                'LilycoveCity_ContestLobby_Text_ExplainContestRanks': 4, 'LilycoveCity_ContestLobby_Text_ParticipateAnotherTime': 5,
                'LilycoveCity_ContestLobby_Text_EnterWhichPokemon1': 6, 'LilycoveCity_ContestLobby_Text_EnterWhichRank': 43}
MENUS = {26: 'Enter', 27: 'Info', 28: 'Exit', 29: 'What’s a Contest?', 30: 'Types of Contests', 31: 'Ranks', 32: 'Cancel',
         33: 'Cool', 34: 'Beauty', 35: 'Cute', 36: 'Smart', 37: 'Tough', 38: 'Exit',
         39: 'Normal Rank', 40: 'Super Rank', 41: 'Hyper Rank', 42: 'Master Rank',
         43: 'Which Rank would you like to enter?',
         44: 'Did you want to make some Pokéblocks\\nwith the Blender?',
         45: 'But you don’t have a Pokéblock Case.{be01}\\nYou should get a Pokéblock Case and\\nthen come see me.',
         46: 'Oh?\\nYou don’t have any Berries?{be01}\\nIf you don’t have any Berries,\\nyou can’t make any Pokéblocks.',
         47: 'But your Pokéblock Case is full.{be01}\\nYou should use some Pokéblocks before\\nyou come see me again.',
         48: 'Let’s get started, then!{be01}\\nWhich Berry will you put in?',
         49: 'That won’t blend, I’m afraid.\\nIt isn’t that kind of Berry.',
         50: 'Oh...\\nYou’ve made this old-timer sad...'}


# The Musical's person in Lilycove's lobby (contests.inc's lines, then these: common/musical.inc MUSL_*), its original lines
MUSICAL_LINES = ['Hello, there!{be01}\\nOur Musical stage is open!',
                 'In a Musical, Pokémon dress up\\nin Props and dance on stage!{be01}\\nHere’s a Prop Case. It holds a set\\nof Props to get you started!',
                 'Oh! Fans from your last show left\\nyou some presents!', 'Would you like to perform?',
                 'I’m sorry, but none of your Pokémon\\ncan perform.', 'Please choose the Pokémon that\\nwill perform.',
                 'Which show would you like\\nto perform in?', 'Stardom', 'Forest Stroll', 'A Sweet Soirée', 'Exciting Nimbasa', 'Cancel',
                 'Great! Please walk this way!', 'We hope to see you on stage\\nanother time.']


def lines_for(which):
    ruby = _labels(os.path.join(RUBY, 'data/maps/LilycoveCity_ContestLobby/text.inc'), os.path.join(RUBY, 'data/text/contest_hall.inc'))
    rows = [clean(ruby[k]) for k in RUBY_KEYS]
    assert len(rows) == 26
    full = rows + [MENUS[i] for i in sorted(MENUS)]
    if which == 'emerald':
        src = _labels(os.path.join(EMERALD, 'data/scripts/contest_hall.inc'), os.path.join(EMERALD, 'data/text/contest_strings.inc'))
        for key, i in EMERALD_KEYS.items():
            if key in src:
                full[i] = clean(src[key])
    # (the script's word 0 = the player, word 1 = the Pokémon; Gen 3's line names the Pokémon with STR_VAR_1)
    head, sep, tail = full[23].rpartition('{0100:0}')
    assert sep
    full[23] = head + '{0100:1}' + tail
    return full


def main():
    done = []
    for rel, (t, which) in LOBBIES.items():
        path = os.path.join(ROOT, rel)
        old = open(path, encoding='utf-8').read().split('\n')
        if old and old[-1] == '':
            old.pop()
        new = old[:t] + lines_for(which) + (MUSICAL_LINES if '0219_' in rel else [])
        open(path, 'w', encoding='utf-8').write('\n'.join(new) + '\n')
        done.append(f'{rel}: {len(old)} -> {len(new)} lines')
    print('\n'.join(done))


if __name__ == '__main__':
    main()
