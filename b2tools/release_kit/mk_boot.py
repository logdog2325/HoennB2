"""Release kit (from freeze_fix's tests/mk_boot.py): cold boot -> Birch's four questions (answers given) -> truck -> base_house.
    python mk_boot.py ROM OUTDIR yes|no yes|no hoenn|unova [classic|new]
    (Fairy, modern split = yes, music, sprite style: notes/FAIRY.md "Birch's questions"; the 4th defaults to classic)
The options u16 printed at the end: bit 11 Fairy, 12 classic split, 13 Hoenn music, 14 NEW (Gen 5) sprites."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Documents/GitHub/HoennB2/work/agents/fairy_core/tools'))
import fairyemu as F
from emu import Emu, fresh_battery
rom, OUT, fairy, split, music = sys.argv[1:6]
sprites = sys.argv[6] if len(sys.argv) > 6 else 'classic'
assert sprites in ('classic', 'new'), sprites
fresh_battery(rom)
e = Emu(rom)
n = F.intro_to_questions(e)
shots = [F.answer(e, fairy == 'yes')]
n += F.to_next_menu(e); shots.append(F.answer(e, split == 'yes'))
n += F.to_next_menu(e); shots.append(F.answer(e, music == 'hoenn'))
n += F.to_next_menu(e); shots.append(F.answer(e, sprites == 'classic'))
cfg = F.config(e); print('presses', n, 'config', hex(cfg) if cfg is not None else None, flush=True)
F.sheet(shots, OUT + '/questions.png', 2)
for i, im in enumerate(shots): im.save(f'{OUT}/question_{i + 1}.png')     # 256x384 each
for _ in range(max(10, 130 - n - 4)): e.press('A', 6, 40)
e.run(900); e.shot(OUT + '/truck.png', 'top'); e.save_state(OUT + '/base_truck.dst')
assert e.calibrate(10, 10), 'truck calibration'
e.hold('RIGHT', 16); e.run(4); e.run(300)
for _ in range(26): e.press('A', 6, 30); e.run(50)
e.run(100); e.shot(OUT + '/house.png', 'top'); e.save_state(OUT + '/base_house.dst')
cfg = F.config(e); print('config', hex(cfg) if cfg is not None else None, 'fairy', bool(cfg & 0x800), 'classic', bool(cfg & 0x1000),
                          'hoenn music', bool(cfg & 0x2000), 'new sprites', bool(cfg & 0x4000))
