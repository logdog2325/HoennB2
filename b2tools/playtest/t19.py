import sys, time; sys.path.insert(0, sys.path[0])
from pt import *
g = G('t_party.dst')
t = time.time(); g.run(600); print('plain', 600 / (time.time() - t))
for l in range(4): g.e.d.gpu_set_layer_main_enable_state(l, False)
t = time.time(); g.run(600); print('main layers off', 600 / (time.time() - t))
for l in range(4): g.e.d.gpu_set_layer_sub_enable_state(l, False)
t = time.time(); g.run(600); print('all off', 600 / (time.time() - t))
t = time.time()
for i in range(600):
    g.e.d.skip_next_frame(); g.e.d.cycle(with_joystick=False)
print('skip', 600 / (time.time() - t))
