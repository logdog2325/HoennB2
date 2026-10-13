"""Playthrough driver (player inputs only; RAM is only read). Run with ~/Documents/GitHub/HoennB2/.venv/bin/python.

    from pt import *
    g = G('state.dst')        # or G() for a cold boot
    g.adv()                   # A through an event (answers choice menus, fights battles)
    g.go(x, z)                # walk to a tile of the current zone's matrix (routes on the ROM's collision)
"""
import sys, os, struct, time, ctypes, json
from collections import deque
ROOT = os.path.expanduser('~/Documents/GitHub/HoennB2')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PT = os.path.dirname(HERE)
ROM = os.environ.get('PT_ROM') or os.path.join(PT, 'pt_sapphire.nds')
STATES = os.path.join(PT, 'states')
SHOTS = os.path.join(ROOT, 'screenshots', 'playthrough')
LOG = os.path.join(PT, 'log')
os.makedirs(LOG, exist_ok=True)
from emu import Emu, KEYS
from desmume.controls import keymask
from PIL import Image, ImageStat, ImageChops
import numpy as np
import romdata as R

G_GAMESYS = 0x021410f4
STRBUF_MAGIC = 0xb6f8d2ec
DIRK = {(0, -1): 'UP', (0, 1): 'DOWN', (-1, 0): 'LEFT', (1, 0): 'RIGHT'}
DVEC = {v: k for k, v in DIRK.items()}
FACE = {0: 'UP', 1: 'DOWN', 2: 'LEFT', 3: 'RIGHT'}
_ROM = None
def rom():
    global _ROM
    if _ROM is None: _ROM = R.Rom(ROM)
    return _ROM


def decode_chars(ws):
    out = []; i = 0
    while i < len(ws):
        c = ws[i]
        if c == 0xffff: break
        if c == 0xfffe: out.append('\n')
        elif c == 0xf000:
            if i + 2 < len(ws):
                argc = ws[i + 2]; out.append('{%x}' % ws[i + 1]); i += 3 + argc; continue
        elif c < 0xd800 or c >= 0xe000: out.append(chr(c))
        else: out.append('?')
        i += 1
    return ''.join(out)


class Stop(Exception):
    pass

def _fast_run(self, frames=1):
    """Emu.run that skips drawing every frame but the last one (the screen is fresh after each call)."""
    d = self.d
    for i in range(frames):
        d.skip_next_frame()
        d.cycle(with_joystick=False)
    self.frames += frames
Emu.run = _fast_run

_orig_save = Emu.save_state
def _safe_save(self, path):
    """DeSmuME quirk (2026-10-09): a state saved right after a drawn frame that follows skipped ones segfaults when a
    new process loads it; one more skipped frame first avoids it."""
    for _ in range(3):                      # (tested 2026-10-09: 3 drawn frames make every save load again)
        self.d.cycle(with_joystick=False)
    self.frames += 3
    _orig_save(self, path)
Emu.save_state = _safe_save

import signal
def _alarm(signum, frame): raise Stop('wall-clock limit (PT_TIMEOUT)')
signal.signal(signal.SIGALRM, _alarm)
signal.alarm(int(os.environ.get('PT_TIMEOUT', '1800')))


class G:
    def __init__(self, state=None, rom_path=ROM, name='run'):
        self.e = Emu(rom_path)
        self.lib = self.e.d.lib
        self.MAIN = ctypes.addressof(ctypes.c_ubyte.in_dll(self.lib, 'MMU')) + 0xC000
        if state:
            self.e.load_state(state if os.path.isabs(state) else os.path.join(STATES, state))
            self.e.run(2)
        self.shots = []
        self.name = name
        self.tlog = open(os.path.join(LOG, f'transcript_{name}.txt' if name not in ('run',) else 'transcript.txt'), 'a')
        self.tlog.write(f'\n===== {time.strftime("%H:%M:%S")} {name} from {state}\n')
        self.seen_text = set(self._strbufs_now())
        self.last_msg = ''
        self.blocked = {}            # (zone, x, z) -> frames when found blocked
        self.held = set()
        self.battle_hook = None       # set by battle module: callable(g) -> runs a battle to its end
        self.other_screen_hook = None
        self.prefer_no_grass = True
        self.run_shoes = True
        self.can_surf = False
        self.can_clear = False
        try:
            import battle as _bt
            _bt.install(self, run_wild=True)
        except Exception as ex:
            print('battle bot not installed', ex)
        self.events = []

    # ------------------------------------------------------------------ memory
    def rd(self, a, n): return ctypes.string_at(self.MAIN + (a - 0x02000000), n)
    def u8(self, a): return ctypes.c_uint8.from_address(self.MAIN + a - 0x02000000).value
    def u16(self, a): return ctypes.c_uint16.from_address(self.MAIN + a - 0x02000000).value
    def u32(self, a): return ctypes.c_uint32.from_address(self.MAIN + a - 0x02000000).value
    def s16(self, a): return ctypes.c_int16.from_address(self.MAIN + a - 0x02000000).value
    def s32(self, a): return ctypes.c_int32.from_address(self.MAIN + a - 0x02000000).value
    def ram(self): return self.rd(0x02000000, 0x400000)
    @staticmethod
    def ok(p): return 0x02000000 <= p < 0x02400000

    def gsys(self): return self.u32(G_GAMESYS)
    def gdata(self):
        g = self.gsys(); return self.u32(g + 0x1c) if self.ok(g) else 0
    def zone(self):
        d = self.gdata(); return self.u16(d + 0x114) if self.ok(d) else -1
    def field(self):
        g = self.gsys(); return self.u32(g + 0x20) if self.ok(g) else 0
    def event(self):
        g = self.gsys(); return self.u32(g + 0x18) if self.ok(g) else 0
    def idle(self): return self.field() != 0 and self.event() == 0

    def actors(self):
        d = self.gdata()
        if not self.ok(d): return []
        mm = self.u32(d + 0x1a8)
        if not self.ok(mm): return []
        heap = self.u32(mm + 0x1c); cap = self.u16(mm + 4)
        if not self.ok(heap) or cap > 128: return []
        out = []
        for k in range(cap):
            a = heap + k * 0x100
            fl = self.u32(a)
            if not fl & 1: continue
            gx, gy, gz = struct.unpack('<3h', self.rd(a + 0x3c, 6))
            wx, wy, wz = struct.unpack('<3i', self.rd(a + 0x44, 12))
            out.append(dict(addr=a, flags=fl, uid=self.u16(a + 8), zone=self.u16(a + 0xa), model=self.u16(a + 0xc),
                            move=self.u16(a + 0xe), scr=self.u16(a + 0x14), face=self.u16(a + 0x18), x=gx, y=gy, z=gz,
                            wx=wx / 4096, wy=wy / 4096, wz=wz / 4096))
        return out

    def me(self):
        for a in self.actors():
            if a['uid'] == 255: return a
        return None

    def tile(self):
        p = self.me()
        if p: return (p['x'], p['z'])
        d = self.gdata()
        x, y, z = struct.unpack('<3i', self.rd(d + 0x118, 12))
        return (x >> 16, z >> 16)

    def height(self):
        p = self.me(); return p['wy'] if p else 0

    # ------------------------------------------------------------------ text
    def _strbufs_now(self):
        ram = np.frombuffer(self.ram(), dtype='<u4')
        out = []
        for h in np.where(ram == STRBUF_MAGIC)[0]:
            a = 0x02000000 + 4 * int(h) - 4
            size, length = struct.unpack('<HH', self.rd(a, 4))
            if not (0 < length <= size <= 2048): continue
            ws = struct.unpack('<%dH' % length, self.rd(a + 8, 2 * length))
            out.append(decode_chars(ws))
        return out

    def texts(self):
        """New (expanded) messages since the last call; logged to the transcript."""
        now = self._strbufs_now()
        new = [s for s in dict.fromkeys(now) if s not in self.seen_text]
        self.seen_text = set(now)
        out = []
        for s in new:
            if len(s) < 2: continue
            if '{1' in s and any(('{1' not in t and len(t) > 0) for t in new if t is not s and len(t) >= len(s) - 40): continue
            out.append(s)
            if len(s) >= 12 and ' ' in s: self.last_msg = s
            self.tlog.write(f'[{self.e.frames} z{self.zone()}] {s!r}\n')
        if out: self.tlog.flush()
        return out

    def note(self, s):
        self.tlog.write(f'## {s}\n'); self.tlog.flush(); print(s, flush=True)

    # ------------------------------------------------------------------ inputs
    def run(self, n=1): self.e.run(n)
    def press(self, k, frames=4, after=12): self.e.press(k, frames, after)
    def hold(self, k, frames): self.e.hold(k, frames)
    def touch(self, x, y, frames=6, after=20): self.e.touch(x, y, frames, after)
    def key_down(self, k):
        if k not in self.held: self.e.d.input.keypad_add_key(keymask(KEYS[k])); self.held.add(k)
    def key_up(self, k):
        if k in self.held: self.e.d.input.keypad_rm_key(keymask(KEYS[k])); self.held.discard(k)
    def release_all(self):
        for k in list(self.held): self.key_up(k)

    # ------------------------------------------------------------------ screens
    def screen(self):
        self.e.d.cycle(with_joystick=False); self.e.frames += 1      # one drawn frame (Emu.run skips drawing)
        return self.e.d.screenshot()
    def top(self): return self.screen().crop((0, 0, 256, 192))
    def bot(self): return self.screen().crop((0, 192, 256, 384))
    def S(self, both=False, label=None):
        im = self.screen()
        self.shots.append(im if both else im.crop((0, 0, 256, 192))); return im
    def sheet(self, path, cols=4):
        if not self.shots: return
        w = max(i.size[0] for i in self.shots); h = max(i.size[1] for i in self.shots)
        rows = (len(self.shots) + cols - 1) // cols
        sh = Image.new('RGB', (w * min(cols, len(self.shots)), h * rows))
        for i, im in enumerate(self.shots): sh.paste(im, (w * (i % cols), h * (i // cols)))
        sh.save(path); self.shots = []
    def proof(self, name, both=True):
        os.makedirs(SHOTS, exist_ok=True)
        im = self.screen() if both else self.top()
        im.save(os.path.join(SHOTS, name)); return os.path.join(SHOTS, name)
    def save(self, name):
        self.e.save_state(os.path.join(STATES, name)); self.note(f'saved state {name} zone {self.zone()} tile {self.tile()}')
    def close(self):
        self.tlog.close(); self.e.close()

    def wait_stable(self, maxf=120, step=6, screen='bot'):
        """Wait until the (bottom) screen stops changing (UI transitions), up to maxf frames."""
        last = None; same = 0
        for _ in range(maxf // step):
            im = self.bot() if screen == 'bot' else self.top()
            a = np.asarray(im.convert('L').resize((64, 48))).astype(int)
            if last is not None and np.abs(a - last).mean() < 0.5 and a.mean() > 12:
                same += 1
                if same >= 2: return True
            else: same = 0
            last = a; self.run(step)
        return False

    def tap(self, x, y):
        """Touch, then wait for the UI to settle."""
        self.touch(x, y, 4, 8); self.wait_stable()

    def choice_menu(self, im=None):
        """A field choice window (YES/NO or a list) on the top screen's right: white box with a dark cursor."""
        im = im or self.top()
        px = np.asarray(im.convert('RGB')).astype(int)
        # white box right side, above the message box
        reg = px[60:146, 168:254]
        white = (reg.min(axis=2) > 225).mean()
        dark = (reg.max(axis=2) < 90).mean()
        return white > 0.55 and dark > 0.01

    # ------------------------------------------------------------------ battles
    def event_chain(self):
        ev = self.event(); out = []
        while self.ok(ev) and len(out) < 8:
            out.append(self.u32(ev + 4) & ~1); ev = self.u32(ev)
        return out

    def in_battle(self):
        return self.field() == 0 and 0x02168bac in self.event_chain()

    def naming_screen(self):
        return 0x02019560 in self.event_chain() and self.field() == 0 and is_naming(self.screen())

    def battle_module(self):
        if self.field() != 0: return None
        ram = np.frombuffer(self.ram(), dtype='<u4')
        idx = np.arange(len(ram), dtype=np.int64) * 4 + 0x02000000
        hits = np.where((ram.astype(np.int64) == idx - 0xc8) & (ram > 0x02000000))[0]
        for h in hits:
            m = int(ram[h])
            j = (m + 0x1b0 - 0x02000000) // 4
            if j < len(ram) and ram[j] == m: return m
        return None

    # ------------------------------------------------------------------ advancing events
    def adv(self, answers=None, maxn=600, quiet=30, rule=None, verbose=True):
        """Advance whatever is running (scripts, messages, battles) until the field is idle for `quiet` frames.
        answers: list of 'yes'/'no'/int consumed at choice menus (then `rule(msg)` or yes)."""
        answers = list(answers or [])
        still = 0; n = 0
        while n < maxn:
            n += 1
            for t in self.texts():
                if verbose: print('  >', t.replace('\n', ' ')[:150], flush=True)
            if self.field() == 0:
                still = 0
                if self.in_battle():
                    if self.battle_hook: self.battle_hook(self)
                    else: self.run(20)
                    continue
                if self.naming_screen():
                    self.note('naming screen: keep the default name'); self.press('START', 4, 20); self.press('A', 4, 60); continue
                if self.other_screen_hook and self.other_screen_hook(self): continue
                self.run(30); self.press('A', 4, 10)       # other screens (fades, evolution): A advances, never cancels
                continue
            if self.event() == 0:
                still += 10; self.run(10)
                if still >= quiet: return True
                continue
            still = 0
            if self.choice_menu():
                ans = answers.pop(0) if answers else (rule(self.last_msg) if rule else None)
                if ans is None: ans = default_answer(self.last_msg)
                if verbose: print('  choice ->', ans, '| after:', self.last_msg.replace('\n', ' ')[-80:], flush=True)
                self.tlog.write(f'   (choice -> {ans})\n')
                if ans == 'yes' or ans == 0: self.press('A', 4, 30)
                elif ans == 'no': self.press('B', 4, 30)
                else:
                    for _ in range(int(ans)): self.press('DOWN', 4, 8)
                    self.press('A', 4, 30)
                continue
            self.press('A', 4, 16)
        return False

    # ------------------------------------------------------------------ walking
    def nav_grid(self):
        return rom().grid(self.zone())

    CLEARABLE = (10004, 10016)      # hm_free: Cut tree, Rock Smash rock (talk: A + yes clears them)

    def obstacles(self, clearable=False):
        out = set()
        for a in self.actors():
            if a['uid'] == 255 or a['flags'] & 0x200: continue
            if clearable and a['scr'] in self.CLEARABLE: continue
            out.add((a['x'], a['z']))
        return out

    def clear_ahead(self, d):
        """Cut the tree / smash the rock in direction d."""
        p = self.tile(); t = (p[0] + d[0], p[1] + d[1])
        for a in self.actors():
            if (a['x'], a['z']) == t and a['scr'] in self.CLEARABLE:
                self.face(d); self.press('A', 4, 20); self.adv(answers=['yes']); self.run(30)
                return True
        return False

    def exstate(self):
        d = self.gdata(); return self.u32(d + 0x154) if self.ok(d) else 0

    def route(self, goal, surfing=None, avoid_grass=False, extra_block=(), goal_adjacent=False):
        """BFS on the ROM collision from the player's tile. Returns list of (dir, kind) moves or None.
        kinds: walk, jump (ledge), surf (start surfing onto the water ahead: needs A + yes), climb (waterfall).
        Surfing is planned only when self.can_surf."""
        grid = self.nav_grid()
        start = self.tile(); y0 = self.height()
        z = self.zone()
        mode0 = 'surf' if self.exstate() == 2 else 'land'
        block = self.obstacles(clearable=self.can_clear) | set(extra_block) | {(x, zz) for (zn, x, zz), f in self.blocked.items() if zn == z}
        goals = {goal} if not goal_adjacent else {(goal[0] + dx, goal[1] + dz) for dx, dz in DIRK}
        startk = (start, round(y0), mode0)
        prev = {startk: None}; q = deque([(start, y0, mode0)])
        found = None
        while q:
            p, y, mode = q.popleft()
            if p in goals:
                found = (p, round(y), mode); break
            for d in DIRK:
                opts = step_options(grid, p, y, d, mode)
                if self.can_surf and mode == 'land':
                    b = (p[0] + d[0], p[1] + d[1])
                    for rb in grid.rec(*b):
                        if R.surf(rb) and rb[2] != 0x40:
                            yb = R.Grid.y(rb, *b)
                            yb = y if yb is None else yb
                            if 0 <= y - yb < 20: opts.append((b, yb, 'surf', 'surf'))
                for nxt, ny, nmode, kind in opts:
                    if nxt in block and nxt not in goals: continue
                    if avoid_grass and nxt not in goals and any(r[2] in R.GRASS for r in grid.rec(*nxt)): continue
                    if mode == 'surf' and kind == 'walk' and any(r[2] == 0x40 for r in grid.rec(*nxt)) and d == (0, -1):
                        if not self.can_surf: continue
                        kind = 'climb'
                    k = (nxt, round(ny), nmode)
                    if k in prev: continue
                    prev[k] = ((p, round(y), mode), d, kind)
                    q.append((nxt, ny, nmode))
        if not found: return None
        out = []; k = found
        while prev[k]:
            pk, d, kind = prev[k]; out.append((d, kind)); k = pk
        return out[::-1]

    def start_surf(self, d):
        """Face the water ahead and use Surf (the badge + HM03 in the Bag or a Pokemon that knows it).
        (A map-replace chunk can make 'water' land: if the turn walks us onto it, that is fine too.)"""
        p0 = self.tile()
        self.face(d)
        if self.tile() != p0: return True
        self.press('A', 4, 20)
        self.adv(answers=['yes'])
        for _ in range(60):
            if self.exstate() == 2: return True
            self.run(5)
        return self.exstate() == 2

    def climb(self, d):
        self.face(d); self.press('A', 4, 20); self.adv(answers=['yes']); self.run(30)
        return True

    def walk_dir(self, d, tiles=1, timeout=60):
        """Hold a direction until the player has moved `tiles` tiles that way (or stops). Returns tiles moved."""
        k = DIRK[d]
        start = self.tile(); z0 = self.zone()
        if self.run_shoes: self.key_down('B')
        target = (start[0] + d[0] * tiles, start[1] + d[1] * tiles)
        self.key_down(k)
        moved_frames = 0; last = start; stuck = 0
        try:
            for f in range(timeout * tiles + 30):
                self.run(1)
                if self.zone() != z0 or self.field() == 0 or self.event() != 0: break
                t = self.tile()
                if t == target: break
                if t == last:
                    stuck += 1
                    if stuck > 30: break
                else: stuck = 0; last = t
        finally:
            self.key_up(k); self.key_up('B')
        # let the step finish
        for _ in range(24):
            p = self.me()
            if not p: break
            if abs(p['wx'] - (p['x'] * 16 + 8)) < 0.5 and abs(p['wz'] - (p['z'] * 16 + 8)) < 0.5: break
            self.run(1)
        t = self.tile()
        return abs(t[0] - start[0]) + abs(t[1] - start[1])

    def face(self, d):
        """Turn to face direction d (tap)."""
        want = {(0, -1): 0, (0, 1): 1, (-1, 0): 2, (1, 0): 3}[d]
        for _ in range(3):
            p = self.me()
            if p and p['face'] == want: return True
            self.hold(DIRK[d], 3); self.run(10)
        p = self.me(); return bool(p and p['face'] == want)

    def go(self, x, z, tries=12, avoid_grass=False, adjacent=False, on_event='adv', surfing=False):
        """Walk to (x, z) in the current matrix. Re-plans around blocks; on an event (trainer, trigger) runs adv()
        and goes on (on_event='stop' returns 'event'). Returns True when there (or next to it with adjacent)."""
        goal = (x, z)
        for attempt in range(tries):
            here = self.tile()
            if (not adjacent and here == goal) or (adjacent and abs(here[0] - x) + abs(here[1] - z) == 1): return True
            path = self.route(goal, avoid_grass=True, goal_adjacent=adjacent) if self.prefer_no_grass else None
            if path is None:
                path = self.route(goal, avoid_grass=avoid_grass, goal_adjacent=adjacent)
            if path is None:
                self.note(f'no route {here} -> {goal} zone {self.zone()}'); self.run(30)
                if attempt > 2: self.blocked = {}
                continue
            # run straight segments
            i = 0; z0 = self.zone()
            while i < len(path):
                d, kind = path[i]; n = 1
                while i + n < len(path) and path[i + n] == (d, 'walk') and kind == 'walk': n += 1
                before = self.tile()
                exp = (before[0] + d[0] * (n if kind == 'walk' else 2), before[1] + d[1] * (n if kind == 'walk' else 2))
                if kind == 'jump':
                    self.walk_dir(d, 1); self.run(24)
                elif kind == 'surf':
                    if not self.start_surf(d): self.note(f'surf failed at {before}'); break
                    i += n; continue
                elif kind == 'climb':
                    self.climb(d); i += n; continue
                else:
                    self.walk_dir(d, n)
                if self.zone() != z0:
                    zn = self.zone()
                    if zn < 0 or rom().hdr[zn]['matrix'] != rom().hdr[z0]['matrix']:
                        self.note(f'zone changed to {zn} while walking (warp)'); self.wait_zone(z0); return 'zone'
                    z0 = zn
                if self.event() != 0 or self.field() == 0:
                    if on_event == 'stop': return 'event'
                    self.adv(); break
                now = self.tile()
                if now != exp and self.can_clear and self.clear_ahead(d):
                    break                                   # cleared: re-plan from here
                if now != exp:
                    # blocked: mark the next tile (temporarily) and re-plan
                    nxt = (now[0] + d[0], now[1] + d[1])
                    self.blocked[(self.zone(), nxt[0], nxt[1])] = self.e.frames
                    self.run(10); break
                i += n
            else:
                continue
        here = self.tile()
        return (here == goal) if not adjacent else (abs(here[0] - x) + abs(here[1] - z) == 1)

    def find_grass(self, radius=12):
        """Nearest pair of adjacent tall-grass tiles (a, b) reachable from here."""
        grid = self.nav_grid(); x0, z0 = self.tile()
        cands = []
        for x in range(x0 - radius, x0 + radius + 1):
            for z in range(z0 - radius, z0 + radius + 1):
                r = grid.rec(x, z)
                if r and r[0][2] in R.GRASS and not r[0][3] & 1:
                    for d in ((1, 0), (0, 1)):
                        r2 = grid.rec(x + d[0], z + d[1])
                        if r2 and r2[0][2] in R.GRASS and not r2[0][3] & 1:
                            cands.append((abs(x - x0) + abs(z - z0), (x, z), (x + d[0], z + d[1])))
        cands.sort()
        return [(a, b) for _, a, b in cands]

    def pace_grass(self, steps=200, pair=None):
        """Walk back and forth in tall grass until a wild battle starts (returns True) or steps run out."""
        for a, b in ([pair] if pair else self.find_grass())[:5]:
            if self.go(*a) is not True: continue
            for i in range(steps):
                t = b if i % 2 == 0 else a
                here = self.tile()
                d = (t[0] - here[0], t[1] - here[1])
                if abs(d[0]) + abs(d[1]) != 1: break
                self.walk_dir(d, 1)
                if self.field() == 0 or self.event() != 0: return True
            return False
        return False

    def wait_idle(self, quiet=20, maxf=1200):
        still = 0
        for _ in range(maxf // 5):
            if self.idle(): still += 5
            else: still = 0
            if still >= quiet: return True
            self.run(5)
        return False

    def wait_zone(self, z0, maxf=240):
        """After stepping into a warp: wait for the zone to change, then for the field to settle."""
        for _ in range(maxf // 5):
            if self.zone() != z0:
                for _ in range(80):
                    if self.field() != 0: break
                    self.run(5)
                self.run(30); return True
            self.run(5)
        return False

    def talk(self, x, z, answers=None, rule=None):
        """Walk next to the person / thing at (x, z), face it, press A and advance the event."""
        if not self.go(x, z, adjacent=True): self.note(f'talk: could not reach {x},{z}'); return False
        here = self.tile()
        self.face((x - here[0], z - here[1]))
        self.press('A', 4, 20)
        return self.adv(answers=answers, rule=rule)

    def talk_uid(self, uid, answers=None, rule=None):
        for a in self.actors():
            if a['uid'] == uid: return self.talk(a['x'], a['z'], answers, rule)
        self.note(f'no actor uid {uid}'); return False

    def warp(self, idx=None, to_zone=None, tries=3):
        """Use warp `idx` (or the first one to `to_zone`) of the current zone: walk to it / into it."""
        z0 = self.zone()
        ws = rom().entities(z0)['warps']
        if idx is None: idx = next(i for i, w in enumerate(ws) if w['dest_zone'] == to_zone)
        w = ws[idx]
        tiles = [(w['tile_x'] + i, w['tile_z'] + j) for i in range(w['w']) for j in range(w['h'])]
        grid = self.nav_grid()
        for t in tiles:
            recs = grid.rec(*t)
            if recs and any(R.land(r) for r in recs):
                # mat / walkable warp: walk onto it, then push the way out (dir 1 = down ...)
                r = self.go(*t)
                if self.zone() != z0: return self.wait_idle()
                if r is True:
                    for d in ([{0: (0, -1), 1: (0, 1), 2: (-1, 0), 3: (1, 0)}.get(w['dir'], (0, 1))] + list(DIRK)):
                        self.walk_dir(d, 1)
                        if self.wait_zone(z0): return True
            else:
                # solid warp (door, stairs): stand next to it and walk into it (doors: from the tile below)
                below = (t[0], t[1] + 1)
                br = grid.rec(*below)
                if w['type'] == 3 and br and any(R.land(x) for x in br):
                    r = self.go(*below)
                else:
                    r = self.go(*t, adjacent=True)
                if self.zone() != z0: return self.wait_idle()
                if r is True:
                    here = self.tile()
                    self.walk_dir((t[0] - here[0], t[1] - here[1]), 1)
                    if self.wait_zone(z0): return True
        self.note(f'warp {idx} of zone {z0} not taken'); return False


import places as PL

def _enter(self, zone_target, tries=2):
    """Take the warp of the current zone that leads to zone_target."""
    ws = rom().entities(self.zone())['warps']
    idx = [i for i, w in enumerate(ws) if w['dest_zone'] == zone_target and own_warp(self, w)]
    if not idx: self.note(f'no warp from {self.zone()} to {zone_target}'); return False
    for i in idx:
        if self.warp(i) and self.zone() == zone_target: return True
    return self.zone() == zone_target
G.enter = _enter

def own_warp(self, w):
    """False for a 'parked' warp: Hoenn zones keep warps of rooms entered from elsewhere stacked on one far tile."""
    if w['tile_x'] <= 0 and w['tile_z'] <= 0 or w['tile_x'] >= 4000 or w['tile_z'] >= 4000: return False   # leftovers off-map
    ws = rom().entities(self.zone())['warps']
    same = [v for v in ws if (v['tile_x'], v['tile_z']) == (w['tile_x'], w['tile_z']) and v['dest_zone'] != w['dest_zone']]
    return not same


def _exit_room(self):
    """Leave a room by the warp to its parent zone (or any warp to an outdoor zone)."""
    z = self.zone(); par = rom().hdr[z]['parent']
    ws = rom().entities(z)['warps']
    outdoor = [i for i, w in enumerate(ws) if rom().hdr[w['dest_zone']]['map_type'] == 0 or w['dest_zone'] == par]
    for i in outdoor:
        if self.warp(i) and self.zone() != z: self.adv(); return True
    return False
G.exit_room = _exit_room

def _heal(self):
    """In a town: walk into its Pokemon Center, heal at the nurse, walk out."""
    z = self.zone()
    ws = rom().entities(z)['warps']
    pcz = [w['dest_zone'] for w in ws if 'PokemonCenter_1F' in PL.NAME.get(w['dest_zone'], '') and own_warp(self, w)]
    if not pcz: self.note(f'no Pokemon Center from zone {z}'); return False
    if not self.enter(pcz[0]): return False
    self.adv()
    nurse = [n for n in rom().entities(self.zone())['npcs'] if n['script'] == 1] or rom().entities(self.zone())['npcs'][:1]
    n = nurse[0]
    # the nurse stands behind the counter: talk from the tile two below her (across the counter)
    self.go(n['x'], n['z'] + 2)
    self.face((0, -1)); self.press('A', 4, 20)
    self.adv(answers=['yes'])
    self.note('healed at ' + PL.NAME.get(self.zone(), str(self.zone())))
    self.exit_room()
    return True
G.heal = _heal

def _hunt(self, species, max_battles=15, pair=None):
    """Pace tall grass until one of `species` joins the party (the battle hook must catch wanted species)."""
    import party as P
    want = set(species)
    def have(): return want & {m['species'] for m in P.party(self) if m}
    n = 0
    while n < max_battles and not have():
        if not self.pace_grass(pair=pair): self.note('hunt: no grass'); return False
        self.adv(); n += 1
    got = have()
    self.note(f'hunt {species}: {"caught " + str(got) if got else "none"} after {n} battles')
    return bool(got)
G.hunt = _hunt

def is_naming(im):
    """The naming keyboard: teal grid background and the OK key at the bottom right of the bottom screen."""
    b = im.crop((0, 192, 256, 384)).convert('RGB')
    p = b.getpixel((200, 172)); q = b.getpixel((20, 40))
    return p[1] > 60 and p[2] > 60 and abs(p[1] - p[2]) < 60 and q[0] < 60 and q[2] > q[0]


def default_answer(msg):
    m = msg.lower()
    if 'nickname' in m: return 'no'
    return 'yes'


def step_options(grid, p, y, d, mode):
    """Moves from tile p (height y) in direction d: list of (tile, height, mode, kind)."""
    out = []
    b = (p[0] + d[0], p[1] + d[1])
    ra_list = grid.rec(*p)
    ra = pick(grid, p, y, ra_list)
    side = R.DIRS[d]
    for rb in grid.rec(*b):
        yb = R.Grid.y(rb, *b)
        if yb is None: yb = y
        if mode == 'land':
            if rb[2] in R.LEDGE and R.LEDGE[rb[2]] == d:
                c = (b[0] + d[0], b[1] + d[1])
                for rc in grid.rec(*c):
                    yc = R.Grid.y(rc, *c)
                    if R.land(rc) and (yc is None or abs(yc - y) < 24):
                        out.append((c, yc if yc is not None else y, 'land', 'jump'))
                continue
            if not R.land(rb): continue
            if abs(yb - y) >= 20: continue
            if ra is not None and side in R.WALL_SIDES.get(ra[2], ''): continue
            if R.OPP[side] in R.WALL_SIDES.get(rb[2], ''): continue
            out.append((b, yb, 'land', 'walk'))
        else:
            if R.surf(rb) and (abs(yb - y) < 20 or rb[2] == 0x40):
                out.append((b, yb, 'surf', 'walk'))
            elif not (rb[3] & (3 | R.NOLAND)) and rb[2] not in R.SURF:
                out.append((b, yb, 'land', 'walk'))
    return out


def pick(grid, p, y, recs):
    best = None; bd = 1e9
    for r in recs:
        yy = R.Grid.y(r, *p)
        dd = abs((yy if yy is not None else y) - y)
        if dd < bd: bd = dd; best = r
    return best
