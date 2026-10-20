"""Release kit (from freeze_fix's tests/mk_boot.py): cold boot -> Birch's six questions (answers given) -> truck -> base_house.
    python mk_boot.py ROM OUTDIR yes|no yes|no hoenn|unova [classic|new] [seasons yes|no] [expshare yes|no] [boy|girl]
    (Fairy, modern split = yes, music, sprite style: notes/FAIRY.md "Birch's questions"; the 4th defaults to classic;
    the 5th, seasons (2026-10-18, notes/SEASONS.md), defaults to no; the 6th, the Exp. Share from the start
    (2026-10-19, notes/RESEARCH_EXPSHARE_HM.md), defaults to no = today's game. A ROM from before the 6th question
    has no 6th menu: the 20 presses that look for it are then part of the mashing into the truck.)
    The 9th, the player (2026-10-19, littleroot_may), defaults to boy; girl picks May on Birch's two pictures (RIGHT once
    "Are you a boy? Or are you a girl?" is dismissed), so the truck stops at May's house (the east one).
The options u16 printed at the end: bit 11 Fairy, 12 classic split, 13 Hoenn music, 14 NEW (Gen 5) sprites, 15 seasons;
then FLAG_EXP_SHARE_ON (2058) and whether the Bag has the Exp. Share (item 216)."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Documents/GitHub/HoennB2/work/agents/fairy_core/tools'))
import fairyemu as F
from emu import Emu, fresh_battery
rom, OUT, fairy, split, music = sys.argv[1:6]
sprites = sys.argv[6] if len(sys.argv) > 6 else 'classic'
assert sprites in ('classic', 'new'), sprites
seasons = sys.argv[7] if len(sys.argv) > 7 else 'no'
assert seasons in ('yes', 'no'), seasons
expshare = sys.argv[8] if len(sys.argv) > 8 else 'no'
assert expshare in ('yes', 'no'), expshare
gender = sys.argv[9] if len(sys.argv) > 9 else 'boy'
assert gender in ('boy', 'girl'), gender
GIRL_Q = 'Or are you a girl?'.encode('utf-16-le')     # Birch's question (system text 0054), decoded in a string buffer

def asked_gender(e):
    return GIRL_Q in bytes(e.d.memory.unsigned[0x02000000:0x02400000])

def intro_to_questions(e, girl, max_presses=140):
    """F.intro_to_questions (cold boot -> Birch's first two-line YES/NO, the Fairy question; returns the A presses),
    picking the girl on the gender pictures when asked (the boy is the default: A alone picks him)."""
    e.run(1200)
    pending = girl
    for i in range(max_presses):
        e.press('A', 6, 50 if i < 40 else 40)
        if pending and asked_gender(e):
            pending = False
            e.run(90)                             # let the question finish printing, then dismiss it: the choice is live
            e.press('A', 6, 60)
            for _ in range(3): e.press('RIGHT', 10, 40)
            e.shot(OUT + '/gender.png'); e.press('A', 6, 90)
            continue
        if F.menu_open(e):
            if F.two_lines(e):
                assert not pending, 'the gender question never showed'
                return i + 1
            e.press('A', 6, 40)                   # YES to the gender / name confirmations
            F.wait_closed(e)
    raise SystemExit('no Fairy question in the intro')

fresh_battery(rom)
e = Emu(rom)
n = intro_to_questions(e, gender == 'girl')
shots = [F.answer(e, fairy == 'yes')]
n += F.to_next_menu(e); shots.append(F.answer(e, split == 'yes'))
n += F.to_next_menu(e); shots.append(F.answer(e, music == 'hoenn'))
n += F.to_next_menu(e); shots.append(F.answer(e, sprites == 'classic'))
n += F.to_next_menu(e); shots.append(F.answer(e, seasons == 'yes'))     # (the 5th question: seasons)
try:                                                                    # (the 6th: the Exp. Share from the start)
    n += F.to_next_menu(e, 20); shots.append(F.answer(e, expshare == 'yes'))
except SystemExit:
    n += 20; print('no 6th question (a ROM from before 2026-10-19)', flush=True); assert expshare == 'no', 'no Exp. Share question'
cfg = F.config(e); print('presses', n, 'config', hex(cfg) if cfg is not None else None, flush=True)
F.sheet(shots, OUT + '/questions.png', 2)
for i, im in enumerate(shots): im.save(f'{OUT}/question_{i + 1}.png')     # 256x384 each
for _ in range(max(10, 140 - n - 5)): e.press('A', 6, 40)
e.run(900); e.shot(OUT + '/truck.png', 'top'); e.save_state(OUT + '/base_truck.dst')
assert e.calibrate(10, 10), 'truck calibration'
e.hold('RIGHT', 16); e.run(4); e.run(300)
for _ in range(26): e.press('A', 6, 30); e.run(50)
e.run(100); e.shot(OUT + '/house.png', 'top'); e.save_state(OUT + '/base_house.dst')
gd = F.r32(e, F.r32(e, 0x021410f4) + 0x1c)                 # GameSystem -> GameData: the zone at +0x114 (pt.py zone())
print('player', gender, 'in zone', F.r16(e, gd + 0x114), '(390 Brendan\'s house 1F, 392 May\'s)', flush=True)
cfg = F.config(e); print('config', hex(cfg) if cfg is not None else None, 'fairy', bool(cfg & 0x800), 'classic', bool(cfg & 0x1000),
                          'hoenn music', bool(cfg & 0x2000), 'new sprites', bool(cfg & 0x4000), 'seasons', bool(cfg & 0x8000))
ew = F.block_addr(e, 0x2d)                                 # EventWork: flags at +0x35E (notes/OPENING.md "Story state")
bag = F.block_addr(e, 0x19) + 0x4d8                         # BagSave's Key Items: 83 {u16 item, u16 count} (freeze_fix pt/party.py)
keys = [F.r16(e, bag + 4 * i) for i in range(83) if F.r16(e, bag + 4 * i + 2)]
print('FLAG_EXP_SHARE_ON', bool(e.d.memory.unsigned[ew + 0x35E + 2058 // 8] >> (2058 % 8) & 1), 'key items', keys,
      'Exp. Share in Key Items', 216 in keys)
