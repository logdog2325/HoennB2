"""kitsave.py TESTROM NAME [sign x z]: make a battery save on a test build with a chapter test kit, then load it in a clone
of the release ROM (the save is ROM-layout independent).
  1. new game on TESTROM up to Littleroot (newgame.py's steps), read the town sign (183,365) = the kit's start state + warp
  2. in-game SAVE; copy ~/.config/desmume/<testrom>.dsv to pt_<NAME>.dsv next to a cp -c clone pt_<NAME>.nds of the release
  3. (second process) boot the clone, CONTINUE, save states/<NAME>.dst
Usage: kitsave.py make TESTROM NAME [x z]   then   kitsave.py load NAME"""
import sys, os, shutil, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt import *

def ingame_save(g):
    """Menu -> SAVE -> YES. The SAVE button moves once the Pokedex is in the menu: find it by the prompt."""
    for xy in ((64, 140), (192, 94)):
        g.press('X', 4, 40); g.wait_stable()
        g.touch(*xy, 4, 60)
        ok = False
        for _ in range(12):
            for t in g.texts(): print('  >', t[:80])
            if 'save' in (g.last_msg or '').lower(): ok = True; break
            g.run(20)
        if ok: break
        for _ in range(6): g.press('B', 4, 30)
        g.wait_idle()
    print('save prompt:', g.last_msg)
    done = False
    for attempt in range(4):
        g.run(60); g.wait_stable(); g.touch(222, 60, 4, 40)          # YES (bottom screen)
        for _ in range(20):
            for t in g.texts(): print('  >', t[:80])
            if 'saved the game' in (g.last_msg or '').lower(): done = True; break
            g.run(30)
        if done: break
    print('save result:', g.last_msg)
    g.run(300)
    for _ in range(6): g.press('B', 4, 30)
    g.wait_idle()

if sys.argv[1] == 'make':
    testrom, name = os.path.abspath(sys.argv[2]), sys.argv[3]
    sx, sz = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (183, 366)
    st = f'ng_{name}.dst'
    if not os.path.exists(os.path.join(STATES, st)):
        subprocess.run([sys.executable, '-u', os.path.join(HERE, 'newgame.py'), testrom, st], check=True)
    if os.path.exists(os.path.join(STATES, f'kit_{name}.dst')):
        g = G(f'kit_{name}.dst', rom_path=testrom, name=f'kit_{name}')
    else:
        g = G(st, rom_path=testrom, name=f'kit_{name}')
        print('at', g.zone(), g.tile())
        g.go(sx, sz); g.face((0, -1)); g.press('A', 4, 30)
        g.adv(); g.run(120); g.adv()
        print('after kit', g.zone(), g.tile())
        g.save(f'kit_{name}.dst')
    ingame_save(g)
    g.S(True); g.sheet(os.path.join(PT, f'scratch_kit_{name}.png'))
    g.close()
    src = os.path.expanduser(f'~/.config/desmume/{os.path.splitext(os.path.basename(testrom))[0]}.dsv')
    dst = os.path.expanduser(f'~/.config/desmume/pt_{name}.dsv')
    if os.path.exists(dst): shutil.move(dst, os.path.expanduser(f'~/.Trash/pt_{name}_{int(time.time())}.dsv'))
    shutil.copy(src, dst)
    clone = os.path.join(PT, f'pt_{name}.nds')
    if not os.path.exists(clone): subprocess.run(['cp', '-c', ROM, clone], check=True)
    print('battery save copied to', dst)
else:
    name = sys.argv[2]
    clone = os.path.join(PT, f'pt_{name}.nds')
    g = G(None, rom_path=clone, name=f'kitload_{name}')
    g.run(1300)
    for _ in range(3): g.press('A', 4, 120)       # title -> menu (CONTINUE first) -> load
    for _ in range(40):
        g.run(30)
        if g.field() and g.zone() >= 0: break
        g.press('A', 4, 10)
    g.adv()
    print('continued at', g.zone(), g.tile())
    g.S(True); g.sheet(os.path.join(PT, f'scratch_kitload_{name}.png'))
    g.save(f'{name}.dst')
