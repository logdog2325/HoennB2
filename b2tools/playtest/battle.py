"""Battle bot: reads the battle module (BtlMainModule, found by its pokeCons' back-pointers) and plays by touch.
Policy (Battle.policy): 'run' wild battles unless the species is wanted (catch) or exp is wanted."""
import os, struct, time
from pt import *
import romdata as R
import party as P

BATTLE_CB = 0x02168bac
WILD_CB = 0x021684bc
MOVE_XY = [(64, 57), (192, 57), (64, 104), (192, 104)]
PARTY_XY = [(64, 22), (192, 30), (64, 70), (192, 78), (64, 118), (192, 126)]
UNK = os.path.join(LOG, 'unknown')
os.makedirs(UNK, exist_ok=True)


def px(im, p): return im.getpixel(p)

def classify(g):
    im = g.bot().convert('RGB')
    bag, poke, fight = px(im, (40, 168)), px(im, (215, 168)), px(im, (128, 95))
    if bag[0] > 180 and bag[1] > 150 and bag[2] < 100 and poke[1] > 150 and poke[0] < 160:
        return 'cmd', im
    if bag[0] > 180 and bag[1] > 150 and bag[2] < 100 and fight[0] > 150 and fight[1] < 80:
        return 'cmd_norun', im          # trainer battle variant? (keep same handling)
    arr = np.asarray(im).astype(int)
    if arr.std() < 8:
        return 'flat', im
    t = px(im, (100, 175)); c = px(im, (234, 172))
    if t[0] > 220 and t[1] > 220 and t[2] > 220 and c[2] > 150:
        return 'party', im
    a, b2 = px(im, (64, 57)), px(im, (128, 20))
    if b2[0] < 40 and b2[1] < 40 and px(im, (214, 168))[2] > 150 and 40 < a[0] < 120:
        return 'moves', im
    # the waiting emblem: dark screen, dark-red upper half of a ball in the middle
    if arr.mean() < 45:
        return 'wait', im
    return 'other', im


class Battle:
    def __init__(self, g, wanted=(), run_wild=True, catch=False, learn=None):
        self.g = g; self.wanted = set(wanted); self.run_wild = run_wild
        self.catch = catch
        self.log = []
        self.unknown_n = 0

    # ------------------------------------------------------------------ reading the battle
    def module(self):
        g = self.g
        ram = np.frombuffer(g.ram(), dtype='<u4')
        idx = np.arange(len(ram), dtype=np.int64) * 4 + 0x02000000
        hits = np.where((ram.astype(np.int64) == idx - 0xc8) & (ram > 0x02000000))[0]
        mine = {m['species'] for m in P.party(g) if m}
        best = None
        for h in hits:
            m = int(ram[h])
            j = (m + 0x1b0 - 0x02000000) // 4
            if not (j < len(ram) and ram[j] == m): continue
            pc = g.u8(m + 0x46c)
            if pc > 3: continue
            mons = self.party_of(m, pc)
            if mons and all(x['species'] in mine for x in mons): best = m
        return best

    def mon(self, a):
        g = self.g
        sp, mhp, hp = struct.unpack('<HHH', g.rd(a + 0x0c, 6))
        moves = []
        for i in range(4):
            mid, pp, mpp = struct.unpack('<HBB', g.rd(a + 0x104 + 14 * i, 4))
            moves.append((mid, pp, mpp))
        st = struct.unpack('<5H', g.rd(a + 0xee, 10))
        return dict(addr=a, species=sp, maxhp=mhp, hp=hp, level=g.u8(a + 0x18), monId=g.u8(a + 0x19),
                    types=(g.u8(a + 0xf8), g.u8(a + 0xf9)), moves=moves, atk=st[0], df=st[1], spa=st[2], spd=st[3], spe=st[4],
                    ability=g.u16(a + 0x13c))

    def party_of(self, m, client):
        g = self.g
        base = m + 0xc8 + 4 + 0x1c * client
        cnt = g.u8(base + 24)
        if cnt > 6: return []
        out = []
        for p in struct.unpack('<6I', g.rd(base, 24))[:cnt]:
            if not g.ok(p): return []
            out.append(self.mon(p))
        return out

    def sides(self):
        """(my client's party, list of foe parties), front members first."""
        m = self.mod
        pc = self.g.u8(m + 0x46c)
        mine = self.party_of(m, pc)
        foes = [self.party_of(m, c) for c in range(4) if c != pc and (c - pc) % 2 == 1]
        ally = [self.party_of(m, c) for c in range(4) if c != pc and (c - pc) % 2 == 0]
        return mine, [f for f in foes if f], [a for a in ally if a]

    # ------------------------------------------------------------------ deciding
    def move_score(self, me, foe, slot):
        mid, pp, mpp = me['moves'][slot]
        if mid == 0 or pp == 0: return -1
        mv = R_rom().move(mid)
        if mv['cat'] == 0 or mv['power'] == 0:
            return 0.5                       # status / fixed damage: last resort
        if mid in (120, 153):                # Selfdestruct, Explosion
            return 0.1
        eff = R.effectiveness(mv['type'], *foe['types'])
        if eff == 0: return 0
        if mv['type'] == 4 and foe['ability'] == 26: return 0     # Ground vs Levitate
        stab = 1.5 if mv['type'] in me['types'] else 1.0
        acc = min(mv['acc'], 100) / 100 if mv['acc'] <= 100 else 1.0
        stat = me['atk'] / max(1, foe['df']) if mv['cat'] == 1 else me['spa'] / max(1, foe['spd'])
        hits = 1
        if mv['hits'][1] > 1: hits = (mv['hits'][0] + mv['hits'][1]) / 2
        power = mv['power'] * hits
        if mid in (63, 307, 308, 416, 338): power *= 0.6      # recharge moves
        return power * eff * stab * acc * stat

    def best_move(self, me, foe):
        scores = [self.move_score(me, foe, i) for i in range(4)]
        best = max(range(4), key=lambda i: scores[i])
        return best, scores

    def front_foe(self, foes):
        live = [p[0] for p in foes if p and p[0]['hp'] > 0]
        live += [p[1] for p in foes if len(p) > 1 and p[1]['hp'] > 0 and self.doubles]
        return live

    # ------------------------------------------------------------------ playing
    def run(self):
        g = self.g
        self.mod = None
        for _ in range(60):
            self.mod = self.module()
            if self.mod: break
            g.run(10)
        self.wild = WILD_CB in g.event_chain()
        self.doubles = False
        self.turns = 0
        stuck = 0
        g.note(f'battle start ({"wild" if self.wild else "trainer"}) module {hex(self.mod) if self.mod else None}')
        if self.mod:
            mine, foes, ally = self.sides()
            self.doubles = self.style() >= 1
            g.note('  foes: ' + ', '.join(f"{m['species']} L{m['level']}" for f in foes for m in f))
        cmd_seen = 0; loops = 0
        if not self.mod:
            g.note('  no battle module of my party: watching (demo battle)')
            n = 0
            while g.in_battle() and n < 400:
                for t in g.texts(): pass
                g.run(30); n += 1
                if n % 2 == 0: g.press('A', 4, 6)
            g.note('  demo battle over'); return True
        while g.in_battle():
            loops += 1
            if loops > 4000 or self.turns > 150:
                g.note('  battle loop guard hit: giving up control'); g.S(True); raise Stop('battle loop guard')
            for t in g.texts(): self.log.append(t)
            kind, im = classify(g)
            if kind in ('cmd', 'cmd_norun'):
                cmd_seen += 1; stuck = 0
                if cmd_seen < 2: g.run(6); continue      # let it settle
                cmd_seen = 0
                self.command()
            elif kind == 'moves':
                g.touch(214, 168, 4, 20)                   # back to the command menu
            elif kind == 'party':
                self.choose_party()
            elif kind == 'flat':
                g.run(10)
            elif kind == 'wait':
                stuck = 0
                g.run(20); g.press('B', 4, 6)
            else:
                stuck += 1
                if not self.other(im, stuck):
                    g.run(20)
        g.note(f'battle over after {self.turns} turns')
        return True

    def style(self):
        """Battle style from the BtlSetup (the main module's first field): 0 single, 1 double, 2 triple, 3 rotation."""
        try:
            setup = self.g.u32(self.mod)
            return self.g.u32(setup + 4) if self.g.ok(setup) else 0
        except Exception:
            return 0

    def asking(self, mine):
        """My front Pokemon the command menu asks about ("What will X do?"), by nickname -> species."""
        import re
        m = re.search(r'What will (.+?) do\?', self.g.last_msg or '')
        if not m or len(mine) < 2: return mine[0] if mine else None
        name = m.group(1)
        sp = {p['nick']: p['species'] for p in P.party(self.g) if p}
        want = sp.get(name)
        for x in mine[:2]:
            if x['species'] == want: return x
        return mine[0]

    SPREAD = {89, 57, 284, 153, 120, 436, 330, 222, 523}     # Earthquake, Surf, Eruption, Explosion... hit the ally too

    def command(self):
        g = self.g
        if not self.mod: self.mod = self.module()
        mine, foes, ally = self.sides()
        me = self.asking(mine)
        targets = self.front_foe(foes)
        if not me or not targets:
            g.tap(128, 95); g.touch(*MOVE_XY[0], 4, 30); self.after_move(); return
        foe = min(targets, key=lambda f: f['hp'] / max(1, f['maxhp']))
        if self.wild and foe['species'] in self.wanted and self.catch and foe['species'] not in {m['species'] for m in P.party(g) if m}:
            if self.try_catch(foe): return
        if self.wild and (foe['species'] not in self.wanted or not self.catch):
            low = me['hp'] * 2 < me['maxhp'] or foe['level'] > me['level'] + 3
            if self.run_wild or low or self.best_move(me, foe)[1][self.best_move(me, foe)[0]] <= 0.5:
                g.touch(128, 178, 4, 40); self.turns += 1; return
        best, scores = self.best_move(me, foe)
        if self.doubles:
            for i in range(4):
                if me['moves'][i][0] in self.SPREAD and scores[i] > 0: scores[i] *= 0.4
            best = max(range(4), key=lambda i: scores[i])
        if not self.doubles and me['hp'] * 4 < me['maxhp'] and len(mine) > 1:
            sw = self.better_member(mine, foe, me)
            if sw is not None:
                g.note(f'  switch to party slot {sw}')
                if self.switch_to(sw): self.turns += 1; return
        g.tap(128, 95)
        g.touch(*MOVE_XY[best], 4, 30)
        self.turns += 1
        self.after_move()

    def after_move(self):
        """Doubles: the target screen follows every move: a foe box (left, then right), then the partner's box."""
        if not self.doubles: return
        g = self.g
        for xy in ((64, 50), (192, 50), (192, 98), (64, 98)):
            g.wait_stable(maxf=60)
            k, im = classify(g)
            if k in ('cmd', 'cmd_norun', 'wait', 'flat', 'party'): return
            g.touch(*xy, 4, 20)

    def better_member(self, mine, foe, me):
        best = None; bs = self.best_move(me, foe)[1][self.best_move(me, foe)[0]] * (me['hp'] / max(1, me['maxhp']))
        for i, m in enumerate(mine[1:], 1):
            if m['hp'] * 2 < m['maxhp']: continue
            s = self.best_move(m, foe)
            sc = s[1][s[0]] * (m['hp'] / max(1, m['maxhp']))
            if sc > bs * 1.5: best, bs = i, sc
        return best

    def switch_to(self, slot):
        g = self.g
        g.tap(215, 168)
        k, _ = classify(g)
        if k != 'party': return False
        return self.pick_slot_shift(slot)

    def pick_slot_shift(self, slot):
        g = self.g
        g.tap(*PARTY_XY[slot])
        g.touch(128, 100, 4, 40)          # SHIFT
        return True

    def choose_party(self):
        """Forced pick after a faint (or a switch prompt): the healthiest member that can fight."""
        g = self.g
        g.screen().save(os.path.join(UNK, f'party_{time.strftime("%H%M%S")}.png'))
        mine, foes, ally = self.sides()
        foe = (self.front_foe(foes) or [None])[0]
        order = []
        for i, m in enumerate(mine):
            if i == 0 or m['hp'] == 0: continue
            sc = self.best_move(m, foe)[1] if foe else [1]
            order.append((max(sc) * m['hp'] / max(1, m['maxhp']), i))
        order.sort(reverse=True)
        if not order:
            g.press('B', 4, 30); return
        slot = order[0][1]
        g.note(f'  send out party slot {slot}')
        self.pick_slot_shift(slot)

    BALLS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 492, 493, 494, 495, 496, 497, 498, 499, 500, 576]
    PREF = [2, 3, 4]          # Ultra, Great, Poké

    def try_catch(self, foe):
        g = self.g
        items = P.bag_list(g, 'items')
        balls = [it for it, c in items if it in self.BALLS]
        if not balls: return False
        mine, foes, ally = self.sides()
        me = mine[0]
        if foe['hp'] * 2 > foe['maxhp'] and foe['level'] >= 3:
            # weaken with the weakest damaging move that still hurts
            sc = [self.move_score(me, foe, i) for i in range(4)]
            ok = [i for i in range(4) if sc[i] > 1]
            if ok:
                i = min(ok, key=lambda k: sc[k])
                g.tap(128, 95); g.touch(*MOVE_XY[i], 4, 30); self.turns += 1
                return True
        pick = next((b for b in self.PREF if b in balls), balls[0])
        slot = balls.index(pick)
        g.note(f'  throw ball {pick} (slot {slot}) at {foe["species"]} hp {foe["hp"]}/{foe["maxhp"]}')
        g.tap(40, 168); g.tap(192, 48)
        g.tap(*[(64, 30), (192, 30), (64, 78), (192, 78), (64, 126), (192, 126)][slot % 6])
        g.touch(128, 175, 4, 40)
        self.turns += 1
        return True


    def other(self, im, stuck):
        """Screens we have not classified: save once, then try B / A carefully."""
        g = self.g
        if stuck in (8, 40):
            self.unknown_n += 1
            p = os.path.join(UNK, f'{time.strftime("%H%M%S")}_{self.unknown_n}.png')
            g.screen().save(p); g.note(f'  unknown battle screen saved {p}')
        if stuck % 6 == 5: g.press('B', 4, 20); return True
        return False


_ROMC = None
def R_rom():
    global _ROMC
    if _ROMC is None:
        import pt
        _ROMC = pt.rom()
    return _ROMC


def install(g, **kw):
    def hook(gg):
        Battle(gg, **kw).run()
    g.battle_hook = hook
