"""Crash tour: in each map, talk to every person, read every sign / hidden item, step on every trigger, with a
watchdog (sys_exit / abort hooks, frozen screens, black screens, endless events). Results: log/tour.jsonl,
pictures of anomalies: screenshots/playthrough/tour/."""
import os, json, time, struct
from pt import *
import battle as BT
import party as P
import places as PL

TOUR_SHOTS = os.path.join(SHOTS, 'tour')
os.makedirs(TOUR_SHOTS, exist_ok=True)
TSTATES = os.path.join(STATES, 'tour')
os.makedirs(TSTATES, exist_ok=True)
JLOG = os.path.join(LOG, 'tour.jsonl')
SYS_EXIT, ABORT = 0x0207c774, 0x0207c7dc


class Hang(Exception):
    pass


_TRC = {}
def trainer_class(script):
    """(class, style) of the trainer a trainer script (3000+id / 5000+id) battles."""
    tid = script - 5000 if script >= 5000 else script - 3000
    if tid not in _TRC:
        try:
            if not hasattr(trainer_class, 'tr'): trainer_class.tr = rom().f.narc(91)
            d = trainer_class.tr[tid]; _TRC[tid] = (d[1], d[2])
        except Exception:
            _TRC[tid] = (-1, -1)
    return _TRC[tid]


def install_watch(g):
    g.halted = None
    def hit(addr, n):
        if g.halted is None:
            r = g.e.d.memory.register_arm9
            g.halted = (g.e.frames, addr, r.lr)
    g.e.d.memory.register_exec(SYS_EXIT, hit)
    g.e.d.memory.register_exec(ABORT, hit)
    g.sig_last = None; g.sig_frame = g.e.frames; g.black_since = None


def screen_sig(g):
    im = g.screen().convert('L').resize((32, 48))
    a = np.asarray(im).astype(np.int16)
    return a


def check(g, budget_start, budget=7000):
    """Raise Hang on a halt, a screen frozen for 1500 frames, a black screen for 900 frames, or an event over budget."""
    if g.halted:
        raise Hang(f'sys_exit/abort hit at frame {g.halted[0]} addr {g.halted[1]:#x} lr {g.halted[2]:#x}')
    s = screen_sig(g)
    if g.sig_last is None or np.abs(s - g.sig_last).mean() > 0.3:
        g.sig_last = s; g.sig_frame = g.e.frames
    elif g.e.frames - g.sig_frame > 1500:
        raise Hang(f'screen frozen for {g.e.frames - g.sig_frame} frames')
    if s.max() < 8:
        if g.black_since is None: g.black_since = g.e.frames
        elif g.e.frames - g.black_since > 900: raise Hang('black screen for 900+ frames')
    else:
        g.black_since = None
    if g.e.frames - budget_start > budget:
        raise Hang(f'event still running after {budget} frames')


def box_height(im):
    """Height of the white choice box on the top screen's right (0 if none)."""
    px = np.asarray(im.convert('RGB')).astype(int)
    col = px[:150, 200:250].min(axis=2) > 225
    rows = np.where(col.mean(axis=1) > 0.8)[0]
    if len(rows) == 0: return 0
    return int(rows.max() - rows.min())


def run_event(g, budget=7000, answers=None):
    """Advance whatever runs until the field is idle; choice menus: yes/no -> yes (nickname: no), lists -> B.
    Battles -> the bot. App screens -> B. Watchdog raises Hang."""
    start = g.e.frames; still = 0; answers = list(answers or [])
    g.sig_last = None; g.sig_frame = g.e.frames; g.black_since = None
    n = 0
    while True:
        n += 1
        check(g, start, budget)
        for t in g.texts(): g.tour_texts.append(t)
        if g.field() == 0:
            still = 0
            if g.in_battle():
                if g.battle_hook: g.battle_hook(g)
                else: g.run(20)
                g.sig_last = None; g.sig_frame = g.e.frames
                continue
            if g.naming_screen():
                g.press('START', 4, 20); g.press('A', 4, 60); continue
            g.run(20); g.press('B', 4, 10)
            continue
        if g.event() == 0:
            still += 10; g.run(10)
            if still >= 30: return True
            continue
        still = 0
        if g.choice_menu():
            im = g.top(); h = box_height(im)
            msg = g.last_msg.lower()
            if answers: ans = answers.pop(0)
            elif h > 40: ans = 'B'
            elif 'nickname' in msg: ans = 'no'
            else: ans = 'yes'
            g.tlog.write(f'   (choice h{h} -> {ans})\n')
            if ans == 'yes': g.press('A', 4, 30)
            elif ans in ('no', 'B'): g.press('B', 4, 30)
            else:
                for _ in range(int(ans)): g.press('DOWN', 4, 8)
                g.press('A', 4, 30)
            continue
        # long events: menus the A button keeps cycling (shops, PCs): back out with B after a while
        if g.e.frames - start > budget * 0.45: g.press('B', 4, 16)
        else: g.press('A', 4, 16)


class Tour:
    def __init__(self, g, label='tour'):
        self.g = g; self.label = label
        g.tour_texts = []
        install_watch(g)
        self.results = []
        self.repel = True
        self.last_unreached = []

    def log(self, **kw):
        kw.update(t=time.strftime('%H:%M:%S'), label=self.label, frame=self.g.e.frames)
        with open(JLOG, 'a') as f: f.write(json.dumps(kw) + '\n')
        self.results.append(kw)

    def shot(self, name):
        p = os.path.join(TOUR_SHOTS, name)
        self.g.screen().save(p); return p

    def entry_state(self, z):
        return os.path.join(TSTATES, f'{self.label}_z{z}.dst')

    def reload(self, z):
        g = self.g
        g.e.load_state(self.entry_state(z)); g.run(2)
        g.halted = None; g.release_all()
        g.seen_text = set(g._strbufs_now())

    # ------------------------------------------------------------------ targets
    def targets(self, z):
        """Everything to interact with in zone z: live people, signs/hidden items, triggers."""
        g = self.g
        ent = rom().entities(z)
        out = []
        live = {a['uid']: a for a in g.actors() if a['uid'] != 255}
        for n in ent['npcs']:
            a = live.get(n['uid'])
            if not a: continue
            kind = 'trainer' if n['evtype'] == 1 else ('item' if 7000 <= n['script'] < 8000 else
                    ('berry' if 400 <= n['uid'] < 480 else 'npc'))
            out.append(dict(kind=kind, uid=n['uid'], x=a['x'], z=a['z'], script=n['script'], model=n['model']))
        for i, s in enumerate(ent['signs']):
            out.append(dict(kind='hidden' if s['script'] >= 8000 else 'sign', idx=i, x=s['x'], z=s['z'], script=s['script'], dir=s['dir']))
        for i, t in enumerate(ent['triggers']):
            out.append(dict(kind='trigger', idx=i, x=t['x'], z=t['z'], w=t['w'], h=t['h'], script=t['script'],
                            work=t['work'], value=t['value']))
        return out

    # ------------------------------------------------------------------ choosing what to test
    RISK = None
    def risk_rows(self, z):
        if Tour.RISK is None:
            Tour.RISK = json.load(open(os.path.join(LOG, 'risk.json')))
        return Tour.RISK.get(str(z), [])

    def select(self, z, ts):
        """Risky scripts first; templates (item balls, hidden items, HM obstacles, nurses, clerks...) a few times per run;
        message-only people: one per map; story triggers skipped (story agents tested them), warp triggers all."""
        rows = self.risk_rows(z)
        byuid = {r['uid']: r for r in rows if 'uid' in r}
        byidx = {(r['kind'], r['idx']): r for r in rows if 'idx' in r}
        if not hasattr(self, 'sigs'): self.sigs = {}
        out = []; low_done = False
        for t in ts:
            r = byuid.get(t.get('uid')) if t['kind'] in ('npc', 'trainer', 'item', 'berry') else \
                byidx.get(('sign' if t['kind'] in ('sign', 'hidden') else t['kind'], t.get('idx')))
            risk = r['risk'] if r else 3
            cmds = tuple(r.get('cmds', [])) if r else ()
            t['risk'] = risk; t['cmds'] = list(cmds)
            if t['kind'] == 'trigger':
                if set(cmds) <= {'MapChangeCore', 'RTReserveScript', 'FadeOutBlack', 'FadeInBlack', 'FadeWait', 'SEPlay'} and 'MapChangeCore' in cmds:
                    out.append(t)
                continue
            if t['kind'] == 'trainer':
                cls = trainer_class(t['script'])
                key = repr(('T',) + cls)
                if self.sigs.get(key, 0) >= 1: continue
                self.sigs[key] = 1; out.append(t); continue
            if risk <= 0:
                if not low_done: out.append(t); low_done = True
                continue
            key = repr(('G' if t['script'] >= 2000 else 'L',) + cmds)
            cap = 3 if t['script'] >= 2000 else (6 if risk >= 3 else 3)
            if self.sigs.get(key, 0) >= cap: continue
            self.sigs[key] = self.sigs.get(key, 0) + 1
            out.append(t)
        out.sort(key=lambda t: -t['risk'])
        return out

    # ------------------------------------------------------------------ one interaction
    def interact(self, z, t):
        g = self.g
        g.tour_texts = []
        g.blocked = {}
        if self.repel:
            import flags as F
            F.repel(g)
        f0 = g.e.frames
        res = 'ok'
        try:
            if t['kind'] == 'trigger':
                tiles = [(t['x'] + i, t['z'] + j) for i in range(max(1, t['w'])) for j in range(max(1, t['h']))]
                r = None
                for tile in tiles[:2]:
                    r = g.go(*tile, on_event='stop')
                    if r == 'event' or g.event(): break
                    if r is True: break
                if r not in (True, 'event') and not g.event(): res = 'unreachable'
                else:
                    g.run(30)
                    run_event(g)
            else:
                if t['kind'] in ('npc', 'trainer', 'item', 'berry'):
                    a = next((a for a in g.actors() if a['uid'] == t['uid']), None)
                    if not a: return self.done(z, t, 'gone', f0)
                    tx, tz = a['x'], a['z']
                else:
                    tx, tz = t['x'], t['z']
                self.started = False
                ok = self.approach(tx, tz, t)
                if not ok: res = 'unreachable'
                else:
                    run_event(g)
                    if not self.started and not g.tour_texts and t['kind'] in ('npc', 'sign', 'item', 'trainer', 'hidden', 'berry'):
                        res = 'silent'
        except Hang as h:
            res = 'HANG: ' + str(h)
        except Stop as s:
            res = 'STOP: ' + str(s)
        return self.done(z, t, res, f0)

    def approach(self, tx, tz, t):
        """Stand next to (tx, tz), face it and press A (across a counter when no neighbour is reachable).
        Wild battles and other events on the way are played out and the approach is retried.
        Returns True when A was pressed facing the target (or the target's own event started)."""
        g = self.g
        z0 = g.zone()
        for attempt in range(4):
            if g.zone() != z0: return True
            here = g.tile()
            if t['kind'] in ('npc', 'trainer', 'item', 'berry'):
                a = next((a for a in g.actors() if a['uid'] == t['uid']), None)
                if not a: return False
                tx, tz = a['x'], a['z']
            cands = [(tx + dx, tz + dz) for dx, dz in ((0, 1), (0, -1), (-1, 0), (1, 0))]
            cands += [(tx, tz + 2), (tx, tz - 2), (tx - 2, tz), (tx + 2, tz)]       # across a counter / table
            cands = [c for c in cands if self.walkable(c)]
            cands.sort(key=lambda c: (abs(c[0] - tx) + abs(c[1] - tz) > 1, abs(c[0] - here[0]) + abs(c[1] - here[1])))
            interrupted = False
            for c in cands[:4]:
                r = g.go(*c, on_event='stop', tries=4)
                if r == 'zone': return True
                if r == 'event' or g.event() or g.field() == 0:
                    run_event(g); interrupted = True; break
                if r is not True: continue
                here = g.tile()
                d = (int(np.sign(tx - here[0])), int(np.sign(tz - here[1])))
                if d[0] and d[1]: continue
                me = g.me()
                want = {(0, -1): 0, (0, 1): 1, (-1, 0): 2, (1, 0): 3}[d]
                if me and me['face'] != want:
                    if self.walkable((tx, tz)) and abs(tx - here[0]) + abs(tz - here[1]) == 1 and t['kind'] in ('sign', 'hidden'):
                        # a tap would walk onto the target: step back and come in facing it
                        back = (here[0] - d[0], here[1] - d[1])
                        if self.walkable(back) and g.go(*back, on_event='stop', tries=2) is True:
                            g.walk_dir(d, 1)
                    else:
                        g.face(d)
                if g.tile() != here and t['kind'] in ('sign', 'hidden'):
                    continue
                g.press('A', 4, 20)
                for _ in range(10):
                    if g.event() or g.field() == 0:
                        self.started = True; return True
                    g.run(4)
                if t['kind'] in ('npc', 'trainer', 'item', 'berry'): break   # pressed A at it: nothing happened
            if not interrupted: return bool(cands)
        return False

    def walkable(self, c):
        recs = self.g.nav_grid().rec(*c)
        return any(R.land(r) for r in recs)

    def done(self, z, t, res, f0):
        g = self.g
        info = dict(zone=z, name=PL.NAME.get(z, str(z)), kind=t['kind'], x=t.get('x'), z_=t.get('z'),
                    uid=t.get('uid'), idx=t.get('idx'), script=t.get('script'), result=res,
                    frames=g.e.frames - f0, texts=[s[:160] for s in g.tour_texts[:12]], now_zone=g.zone(), tile=g.tile())
        if res.startswith(('HANG', 'STOP')):
            info['shot'] = self.shot(f'hang_z{z}_{t["kind"]}_{t.get("uid", t.get("idx"))}_{int(time.time())}.png')
            g.note(f'!!! {res} in zone {z} {info["name"]} at {t}')
        self.log(**info)
        return info

    # ------------------------------------------------------------------ one zone
    @staticmethod
    def tkey(t):
        return f"{t['kind']}:{t.get('uid', t.get('idx'))}"

    def zone(self, skip_kinds=(), max_targets=80, only=None):
        """Interact with everything in the current zone. Reloads the zone's entry state after a hang or a warp."""
        g = self.g
        z = g.zone()
        g.wait_idle()
        g.e.save_state(self.entry_state(z))
        ts = [t for t in self.targets(z) if t['kind'] not in skip_kinds]
        if only is not None:
            ts = [t for t in ts if self.tkey(t) in only]
        else:
            ts = self.select(z, ts)[:max_targets]
        self.last_unreached = []
        g.note(f'zone {z} {PL.NAME.get(z, "")}: {len(ts)} targets')
        summary = {}
        for i, t in enumerate(ts):
            if g.zone() != z or not g.idle():
                self.reload(z)
            info = self.interact(z, t)
            summary[info['result'].split(':')[0]] = summary.get(info['result'].split(':')[0], 0) + 1
            if info['result'] == 'unreachable': self.last_unreached.append(self.tkey(t))
            if info['result'].startswith(('HANG', 'STOP')) or g.zone() != z or g.field() == 0:
                if g.zone() != z and not info['result'].startswith(('HANG', 'STOP')):
                    self.log(zone=z, kind='moved', to=g.zone(), after=t)
                self.reload(z)
        g.note(f'zone {z} done: {summary}')
        return summary
