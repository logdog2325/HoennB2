"""Party (encrypted PartyPkm, 220 bytes) and bag readers. Read only."""
import struct
ORDERS = ['ABCD', 'ABDC', 'ACBD', 'ACDB', 'ADBC', 'ADCB', 'BACD', 'BADC', 'BCAD', 'BCDA', 'BDAC', 'BDCA',
          'CABD', 'CADB', 'CBAD', 'CBDA', 'CDAB', 'CDBA', 'DABC', 'DACB', 'DBAC', 'DBCA', 'DCAB', 'DCBA']

def _xor(words, seed):
    out = []; x = seed
    for w in words:
        x = (x * 0x41C64E6D + 0x6073) & 0xffffffff
        out.append(w ^ (x >> 16))
    return out

def decode(pkm):
    pid, flags, chk = struct.unpack('<IHH', pkm[:8])
    raw = list(struct.unpack('<64H', pkm[8:136]))
    if sum(raw) & 0xffff == chk and flags & 1: dec = raw          # decrypted in place
    else:
        dec = _xor(raw, chk)
        if sum(dec) & 0xffff != chk: return None
    order = ORDERS[((pid >> 13) & 31) % 24]
    B = {order[i]: dec[16 * i:16 * i + 16] for i in range(4)}
    A, Bb, C, D = B['A'], B['B'], B['C'], B['D']
    if A[0] == 0: return None
    pw = _xor(list(struct.unpack('<42H', pkm[136:220])), pid) if not flags & 1 else list(struct.unpack('<42H', pkm[136:220]))
    iv = Bb[8] | (Bb[9] << 16)
    nick = []
    for w in C[:11]:
        if w == 0xffff: break
        nick.append(chr(w) if w < 0xd800 else '?')
    return dict(pid=pid, species=A[0], item=A[1], exp=A[4] | (A[5] << 16), friendship=A[6] & 0xff, ability=A[6] >> 8,
                moves=Bb[0:4], pp=[Bb[4] & 0xff, Bb[4] >> 8, Bb[5] & 0xff, Bb[5] >> 8], egg=bool(iv >> 30 & 1),
                nick=''.join(nick), status=pw[0] | (pw[1] << 16), level=pw[2] & 0xff, hp=pw[3], maxhp=pw[4],
                atk=pw[5], df=pw[6], spe=pw[7], spa=pw[8], spd=pw[9])

def party(g):
    d = g.gdata(); p = g.u32(d + 0x194)
    if not g.ok(p): return []
    cap, cnt = struct.unpack('<II', g.rd(p, 8))
    out = []
    for i in range(min(cnt, 6)):
        m = decode(g.rd(p + 8 + 220 * i, 220))
        out.append(m)
    return out

POCKETS = {'items': (0, 310), 'key': (0x4d8, 83), 'tms': (0x624, 109), 'medicine': (0x7d8, 48), 'berries': (0x898, 64)}
def bag(g, pocket=None):
    d = g.gdata(); b = g.u32(d + 0x190)
    out = {}
    if not g.ok(b): return out
    for name, (off, n) in POCKETS.items():
        if pocket and name != pocket: continue
        raw = g.rd(b + off, 4 * n)
        for i in range(n):
            it, cnt = struct.unpack_from('<HH', raw, 4 * i)
            if it: out[it] = out.get(it, 0) + cnt
    return out
def bag_list(g, pocket):
    """Items of one pocket in bag order [(item, count)]."""
    d = g.gdata(); b = g.u32(d + 0x190)
    off, n = POCKETS[pocket]
    raw = g.rd(b + off, 4 * n)
    return [struct.unpack_from('<HH', raw, 4 * i) for i in range(n) if struct.unpack_from('<H', raw, 4 * i)[0]]

def bag_add(g, pocket, item, count=1):
    """Crash tour only: put an item in a pocket's first free slot (or raise its count)."""
    d = g.gdata(); b = g.u32(d + 0x190)
    off, n = POCKETS[pocket]
    for i in range(n):
        it, cnt = struct.unpack('<HH', g.rd(b + off + 4 * i, 4))
        if it == item or it == 0:
            g.e.d.memory.write_short(b + off + 4 * i, item)
            g.e.d.memory.write_short(b + off + 4 * i + 2, (cnt if it == item else 0) + count)
            return True
    return False
