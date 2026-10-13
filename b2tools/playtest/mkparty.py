"""Crash-tour only: write a strong party into the save data in RAM (allowed for the tour: it tests scripts and battles,
not progression). Builds each PartyPkm from the player's first Pokemon (keeps OT, TID, met data), with a new species,
level 100, neutral nature, max IVs, moves with full PP, stats from the ROM's personal data, re-encrypted."""
import struct
import party as P
from pt import rom

EXP100 = {0: 1000000, 1: 600000, 2: 1640000, 3: 1059860, 4: 800000, 5: 1250000}


def _xor(words, seed):
    out = []; x = seed
    for w in words:
        x = (x * 0x41C64E6D + 0x6073) & 0xffffffff
        out.append(w ^ (x >> 16))
    return out


def build(template, species, moves, level=100, nick=None, item=0):
    """template: a valid 220-byte PartyPkm (encrypted). Returns a new encrypted PartyPkm."""
    pid0, flags0, chk0 = struct.unpack('<IHH', template[:8])
    raw = list(struct.unpack('<64H', template[8:136]))
    dec = _xor(raw, chk0) if not flags0 & 1 else raw
    order = P.ORDERS[((pid0 >> 13) & 31) % 24]
    B = {order[i]: dec[16 * i:16 * i + 16] for i in range(4)}
    # new PID: neutral nature (Hardy, pid % 25 == 0), ability slot 1, keep the low bits' gender-ish value
    pid = (pid0 & 0xFFFE0000) | 0x0000
    while pid % 25: pid += 1
    per = rom().personal[species]
    base = per[0:6]; growth = per[0x15]; ab1 = per[0x18]
    A, Bb, C, D = list(B['A']), list(B['B']), list(B['C']), list(B['D'])
    exp = EXP100.get(growth, 1000000) if level == 100 else A[4] | (A[5] << 16)
    A[0] = species; A[1] = item; A[4] = exp & 0xffff; A[5] = exp >> 16
    A[6] = 255 | (ab1 << 8)                      # friendship 255, ability
    for i in range(4):
        Bb[i] = moves[i] if i < len(moves) else 0
    pps = []
    for i in range(4):
        m = Bb[i]
        pps.append(rom().move(m)['pp'] if m else 0)
    Bb[4] = pps[0] | (pps[1] << 8); Bb[5] = pps[2] | (pps[3] << 8)
    Bb[6] = 0; Bb[7] = 0
    iv = 31 | (31 << 5) | (31 << 10) | (31 << 15) | (31 << 20) | (31 << 25)
    iv |= (1 << 31) if nick else 0
    Bb[8] = iv & 0xffff; Bb[9] = iv >> 16
    if nick:
        name = [ord(c) for c in nick[:10]] + [0xffff]
        name += [0xffff] * (11 - len(name))
        C[0:11] = name[:11]
    # re-shuffle
    order_new = P.ORDERS[((pid >> 13) & 31) % 24]
    blocks = {'A': A, 'B': Bb, 'C': C, 'D': D}
    dec_new = []
    for ch in order_new: dec_new += blocks[ch]
    chk = sum(dec_new) & 0xffff
    enc = _xor(dec_new, chk)
    # battle stats
    hp = (2 * base[0] + 31) * level // 100 + level + 10
    st = [(2 * base[k] + 31) * level // 100 + 5 for k in (1, 2, 3, 4, 5)]
    pw0 = list(struct.unpack('<42H', template[136:220]))
    pw = _xor(pw0, pid0) if not flags0 & 1 else pw0
    pw[0] = 0; pw[1] = 0
    pw[2] = level | (pw[2] & 0xff00)
    pw[3] = hp; pw[4] = hp
    pw[5], pw[6], pw[7], pw[8], pw[9] = st[0], st[1], st[2], st[3], st[4]
    penc = _xor(pw, pid)
    return struct.pack('<IHH', pid, 0, chk) + struct.pack('<64H', *enc) + struct.pack('<42H', *penc)


TEAM = [
    (260, [89, 57, 58, 280], 'SWAMPERT'),       # Earthquake, Surf, Ice Beam, Brick Break
    (376, [309, 428, 89, 9], 'METAGROSS'),       # Meteor Mash, Zen Headbutt, Earthquake, Thunder Punch
    (373, [337, 53, 89, 19], 'SALAMENCE'),       # Dragon Claw, Flamethrower, Earthquake, Fly
    (282, [94, 85, 247, 411], 'GARDEVOIR'),      # Psychic, Thunderbolt, Shadow Ball, Focus Blast
]


def install(g, team=TEAM):
    """The strong team first, then the player's own Pokemon (up to six in all)."""
    d = g.gdata(); p = g.u32(d + 0x194)
    cap, cnt = struct.unpack('<II', g.rd(p, 8))
    own = [g.rd(p + 8 + 220 * i, 220) for i in range(cnt)]
    tmpl = own[0]
    mons = [build(tmpl, sp, mv, nick=nk) for sp, mv, nk in team] + own
    mons = mons[:6]
    for slot, m in enumerate(mons):
        for k in range(0, 220, 4):
            g.e.d.memory.write_long(p + 8 + 220 * slot + k, struct.unpack_from('<I', m, k)[0])
    g.e.d.memory.write_long(p + 4, len(mons))
    return P.party(g)
