"""Headless DeSmuME harness (py-desmume) for automated test screenshots. Run with ../.venv/bin/python.

    from emu import Emu
    e = Emu('rom.nds'); e.run(600); e.press('A'); e.shot('out.png')

Battery saves live in ~/.config/desmume/<rom file name>.dsv (DeSmuME's folder, checked 2026-10-06: every hoenn.nds
shares hoenn.dsv); savestates via e.save_state()/load_state(). Cold-boot tests that need no save: fresh_battery(rom).
"""
import os, time, datetime

def _pin_local_hour(hour):
    """Make this process's local time read ~hour:00 by choosing a fixed UTC offset (DeSmuME's RTC uses local time)."""
    utc = datetime.datetime.now(datetime.timezone.utc)
    off = (hour - utc.hour + 12) % 24 - 12          # hours east of UTC, in -12..11
    os.environ['TZ'] = f'<EMU>{-off:+d}'             # POSIX TZ: sign is west-positive
    time.tzset()

_pin_local_hour(int(os.environ.get('EMU_HOUR', '12')))
from desmume.emulator import DeSmuME  # noqa: E402
from desmume.controls import Keys, keymask

KEYS = {k[4:]: getattr(Keys, k) for k in dir(Keys) if k.startswith('KEY_')}

class Emu:
    def __init__(self, rom):
        self.d = DeSmuME()
        self.d.volume_set(0)          # silent: the user hears every test run otherwise
        self.d.open(rom)
        self.d.volume_set(0)
        self.frames = 0

    def run(self, frames=1):
        for _ in range(frames):
            self.d.cycle(with_joystick=False)
        self.frames += frames

    def hold(self, keys, frames):
        """Hold one or more keys ('A', 'UP', 'A+B') for a number of frames, then release."""
        ks = [KEYS[k] for k in keys.upper().split('+')]
        for k in ks: self.d.input.keypad_add_key(keymask(k))
        self.run(frames)
        for k in ks: self.d.input.keypad_rm_key(keymask(k))

    def press(self, keys, frames=6, after=20):
        self.hold(keys, frames); self.run(after)

    def touch(self, x, y, frames=6, after=20):
        self.d.input.touch_set_pos(x, y); self.run(frames); self.d.input.touch_release(); self.run(after)

    def shot(self, path, screen='both'):
        img = self.d.screenshot()  # 256x384, top screen first
        if screen == 'top': img = img.crop((0, 0, 256, 192))
        elif screen == 'bottom': img = img.crop((0, 192, 256, 384))
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        img.save(path)
        return img

    pos_addr = 0x02143c64   # default; the address moves between builds, so call calibrate() at a known tile

    def calibrate(self, tx, tz):
        """Find the player's position vector (fx32 x, y, z; world units = tile*16+8) in main RAM while the player
        stands on the known global tile (tx, tz). Uses the lowest matching address (the player actor's own copy)."""
        import numpy as np
        ram = np.frombuffer(bytes(self.d.memory.unsigned[0x02000000:0x02400000]), dtype='<i4')
        want_x, want_z = (tx * 16 + 8) << 12, (tz * 16 + 8) << 12
        hits = np.where((ram[:-2] == want_x) & (ram[2:] == want_z))[0]
        if len(hits) == 0: return False
        self.pos_addr = 0x02000000 + 4 * int(hits[0])
        return True

    def player_tile(self):
        """Player's global tile (x, z), from the position vector at pos_addr (see calibrate)."""
        import struct
        x, y, z = struct.unpack('<3i', bytes(self.d.memory.unsigned[self.pos_addr:self.pos_addr + 12]))
        return ((x >> 12) - 8) // 16, ((z >> 12) - 8) // 16

    DELTA = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}

    def step(self, direction, timeout=48):
        """Walk one tile; returns True if the player's tile changed. A short tap starts exactly one step (the tile
        value only changes at the end of a step, so holding until it changes would start a second one); a tap
        while facing elsewhere only turns, so up to 3 taps. Crossing into another zone can move the position data
        in RAM; then the address is found again from the tile the player must have reached (or two on, a ledge)."""
        start = self.player_tile()
        dx, dz = self.DELTA[direction]
        moved = False
        for _ in range(3):
            self.d.input.keypad_add_key(keymask(KEYS[direction]))
            self.run(6)
            self.d.input.keypad_rm_key(keymask(KEYS[direction]))
            last, still = self.player_tile(), 0
            for _ in range(timeout):              # wait until the position stops changing
                self.run(1)
                now = self.player_tile()
                still = still + 1 if now == last else 0
                last = now
                if still >= 20: break             # (a ledge jump pauses mid-air)
            if last != start: moved = True; break
        now = self.player_tile()
        if moved and abs(now[0] - start[0]) + abs(now[1] - start[1]) > 2:   # garbage: position data moved
            self.run(30)
            for k in (1, 2):
                if self.calibrate(start[0] + k * dx, start[1] + k * dz): break
        return moved

    def goto(self, tx, tz, max_steps=200):
        """Walk to global tile (tx, tz), x first then z, going around nothing; stops when blocked."""
        for _ in range(max_steps):
            x, z = self.player_tile()
            if (x, z) == (tx, tz): return True
            moves = []
            if x != tx: moves.append('RIGHT' if tx > x else 'LEFT')
            if z != tz: moves.append('DOWN' if tz > z else 'UP')
            if not any(self.step(mv) for mv in moves):
                return False
        return False

    def travel(self, tx, tz, avoid=''):
        """Walk to global tile (tx, tz) along the shortest route through our chunks' collision (navgrid.py);
        avoid='g' keeps out of tall grass."""
        import navgrid
        for attempt in range(4):                  # re-plan from wherever the player really is
            if self.player_tile() == (tx, tz): return True
            path = navgrid.route(self.player_tile(), (tx, tz), avoid=avoid)
            if path is None: return False
            for mv in path:
                before = self.player_tile()
                if not self.step(mv): break
                if before[1] + 1 < self.player_tile()[1]:   # a ledge jump moves two tiles; let it land
                    self.run(20)
        return self.player_tile() == (tx, tz)

    def save_state(self, path): self.d.savestate.save_file(path)
    def load_state(self, path): self.d.savestate.load_file(path)
    def close(self): self.d.destroy()

def fresh_battery(rom):
    """Move DeSmuME's battery save for this ROM name to the Trash (never deleted), so a cold boot starts with no save."""
    import os, shutil, time
    p = os.path.expanduser(f'~/.config/desmume/{os.path.splitext(os.path.basename(rom))[0]}.dsv')
    if os.path.exists(p):
        shutil.move(p, os.path.expanduser(f'~/.Trash/{os.path.basename(p)}.{time.strftime("%H%M%S")}'))
