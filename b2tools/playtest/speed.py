import sys, time, os
sys.path.insert(0, os.path.expanduser('~/Documents/GitHub/HoennB2/b2tools'))
from emu import Emu
e = Emu(sys.argv[1])
t = time.time(); e.run(600); print('plain fps', 600 / (time.time() - t))
t = time.time()
for _ in range(600):
    e.d.skip_next_frame(); e.d.cycle(with_joystick=False)
print('skip fps', 600 / (time.time() - t))
e.shot(sys.argv[2])
