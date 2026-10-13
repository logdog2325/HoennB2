#!/usr/bin/env python3
"""BPS patches for releases (the BPS format of byuu's beat/Floating IPS: "BPS1", then source size, target size and
metadata size as BPS numbers, the metadata, the actions, and three little-endian CRC32s: source, target, and the patch
bytes before that last one).
Actions: (length - 1) << 2 | command, as a BPS number; 0 SourceRead (source bytes at the output offset), 1 TargetRead
(the bytes follow), 2 SourceCopy and 3 TargetCopy (a signed BPS number, (|d| << 1) | negative, moves the source/target
read offset, then length bytes are copied from there).

  ../.venv/bin/python bps.py make  <original.nds> <hoenn.nds> <out.bps>    (checks itself by applying the patch)
  ../.venv/bin/python bps.py apply <original.nds> <patch.bps> <out.nds>

The encoder: same-offset runs become SourceRead; 512-byte blocks found elsewhere in the source (moved files) become
SourceCopy, extended byte by byte both ways; runs of one byte become TargetCopy of the byte before; then, inside what is
left, source data at any 4-aligned offset (files moved inside rebuilt archives) becomes SourceCopy; the rest TargetRead."""
import sys, zlib
import numpy as np

B = 512

def put_num(n, out):
    while True:
        x = n & 0x7f
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return
        out.append(x)
        n -= 1

def get_num(buf, pos):
    data, shift = 0, 1
    while True:
        x = buf[pos]
        pos += 1
        data += (x & 0x7f) * shift
        if x & 0x80:
            return data, pos
        shift <<= 7
        data += shift

MULT = np.random.default_rng(0x5a17).integers(1, 2**63, 64, dtype=np.uint64) | np.uint64(1)

def block_hashes(a):
    """One 64-bit hash per aligned 512-byte block (blocks compared byte for byte before use)."""
    n = len(a) // B
    h = np.empty(n, np.uint64)
    step = 1 << 16                       # blocks per slice (32 MB)
    with np.errstate(over='ignore'):
        for i in range(0, n, step):
            j = min(n, i + step)
            h[i:j] = (a[i * B:j * B].view('<u8').reshape(j - i, 64) * MULT).sum(axis=1)
    return h

def run_len(x, xo, y, yo, limit):
    """How many bytes x[xo:] and y[yo:] agree, at most limit (numpy windows)."""
    n, w = 0, 256
    while n < limit:
        k = min(w, limit - n)
        ne = np.flatnonzero(x[xo + n:xo + n + k] != y[yo + n:yo + n + k])
        if len(ne):
            return n + int(ne[0])
        n += k
        w = min(w * 4, 1 << 24)
    return limit

W = B // 4                               # words in a window of the second pass
K = np.uint64(0x9E3779B97F4A7C15)

def block_keys(a):
    """The second pass's hash (sum of words, sum of word * its index) of every aligned 512-byte block."""
    n = len(a) // B
    keys = np.empty(n, np.uint64)
    j = np.arange(W, dtype=np.uint64)
    with np.errstate(over='ignore'):
        for i in range(0, n, 1 << 16):
            k = min(n, i + (1 << 16))
            w = a[i * B:k * B].view('<u4').reshape(k - i, W).astype(np.uint64)
            keys[i:k] = w.sum(axis=1) * K + (w * j).sum(axis=1)
    return keys

def region_keys(T, a0, n):
    """word_keys at every 4-aligned offset a0, a0 + 4, ... of n windows, from running sums."""
    w = T[a0:a0 + 4 * (n + W - 1)].view('<u4').astype(np.uint64)
    with np.errstate(over='ignore'):
        c1 = np.concatenate(([np.uint64(0)], np.cumsum(w, dtype=np.uint64)))
        c2 = np.concatenate(([np.uint64(0)], np.cumsum(w * np.arange(len(w), dtype=np.uint64), dtype=np.uint64)))
        i = np.arange(n, dtype=np.uint64)
        s1 = c1[W:W + n] - c1[:n]
        return s1 * K + (c2[W:W + n] - c2[:n]) - i * s1

def make(src, tgt, meta=b''):
    S = np.frombuffer(src, np.uint8)
    T = np.frombuffer(tgt, np.uint8)
    # pass 1, on 512-byte blocks: same offset (SourceRead), a block found elsewhere in the source (SourceCopy), runs of
    # one byte (TargetCopy of the byte before), else literal
    hS, hT = block_hashes(S), block_hashes(T)
    first = {}
    for off, h in enumerate(hS.tolist()):
        first.setdefault(h, off * B)
    hT = hT.tolist()
    ops = []                                 # ('R', len) | ('L', start, end) | ('C', source, len) | ('U', len)
    t = lit = 0
    def flush(upto):
        nonlocal lit
        if upto > lit:
            ops.append(('L', lit, upto))
        lit = upto
    while t < len(tgt):
        if t < len(src):
            r = run_len(S, t, T, t, min(len(src), len(tgt)) - t)
            if r >= 32:
                flush(t); ops.append(('R', r))
                t = lit = t + r
                continue
        b = t // B
        if t % B == 0 and b < len(hT):
            s = first.get(hT[b])
            if s is not None and src[s:s + B] == tgt[t:t + B]:
                r = B + run_len(S, s + B, T, t + B, min(len(src) - s, len(tgt) - t) - B)
                back = 0
                while t - back > lit and s - back > 0 and src[s - back - 1] == tgt[t - back - 1]:
                    back += 1
                t, s, r = t - back, s - back, r + back
                flush(t); ops.append(('C', s, r))
                t = lit = t + r
                continue
        if t % B == 0 and t + B <= len(tgt) and not (T[t:t + B] != T[t]).any():
            r = B + run_len(T, t + B, T, t + B - 1, len(tgt) - t - B)    # each byte equals the one before it
            if t == 0 or tgt[t - 1] != tgt[t]:
                t += 1; r -= 1                         # its first byte stays literal
            flush(t); ops.append(('U', r))
            t = lit = t + r
            continue
        t = min(len(tgt), (b + 1) * B)
    flush(len(tgt))
    # pass 2, inside the literals: source data at any 4-aligned offset (files moved inside rebuilt archives) found by
    # the hash of a 512-byte window against every 512-aligned source window
    nb = len(src) // B
    skeys = block_keys(S)
    order = np.argsort(skeys, kind='stable')
    sk = skeys[order]
    refined = []
    for op in ops:
        if op[0] != 'L' or op[2] - op[1] < 2 * B:
            refined.append(op); continue
        lo, hi = op[1], op[2]
        a0 = (lo + 3) & ~3
        n = (hi - a0) // 4 - W + 1
        if n <= 0:
            refined.append(op); continue
        keys = region_keys(T, a0, n)
        at = np.searchsorted(sk, keys)
        hit = np.flatnonzero((at < len(sk)) & (sk[np.minimum(at, len(sk) - 1)] == keys))
        pos, k = lo, 0
        while k < len(hit):
            p = a0 + 4 * int(hit[k])
            if p < pos:
                k = int(np.searchsorted(hit, (pos - a0 + 3) // 4)); continue
            s = int(order[at[hit[k]]]) * B
            if src[s:s + B] != tgt[p:p + B]:
                k += 1; continue
            r = B + run_len(S, s + B, T, p + B, min(len(src) - s, hi - p) - B)
            back = 0
            while p - back > pos and s - back > 0 and src[s - back - 1] == tgt[p - back - 1]:
                back += 1
            if p - back > pos:
                refined.append(('L', pos, p - back))
            refined.append(('C', s - back, r + back))
            pos = p + r
            k += 1
        if pos < hi:
            refined.append(('L', pos, hi))
    # write the actions
    out = bytearray(b'BPS1')
    put_num(len(src), out); put_num(len(tgt), out); put_num(len(meta), out); out += meta
    o = srel = trel = 0
    stats = [0, 0, 0, 0]                       # source read, literal, source copy, byte runs
    for op in refined:
        if op[0] == 'R':
            put_num((op[1] - 1) << 2 | 0, out); n = op[1]; stats[0] += n
        elif op[0] == 'L':
            n = op[2] - op[1]
            put_num((n - 1) << 2 | 1, out); out += tgt[op[1]:op[2]]; stats[1] += n
        elif op[0] == 'C':
            n = op[2]
            put_num((n - 1) << 2 | 2, out); d = op[1] - srel; put_num(abs(d) << 1 | (d < 0), out)
            srel = op[1] + n; stats[2] += n
        else:
            n = op[1]
            put_num((n - 1) << 2 | 3, out); d = (o - 1) - trel; put_num(abs(d) << 1 | (d < 0), out)
            trel = o - 1 + n; stats[3] += n
        o += n
    assert o == len(tgt)
    out += zlib.crc32(src).to_bytes(4, 'little')
    out += zlib.crc32(tgt).to_bytes(4, 'little')
    out += zlib.crc32(out).to_bytes(4, 'little')
    return bytes(out), stats

def apply(src, patch):
    assert patch[:4] == b'BPS1', 'not a BPS patch'
    assert zlib.crc32(patch[:-4]) == int.from_bytes(patch[-4:], 'little'), 'patch checksum'
    assert zlib.crc32(src) == int.from_bytes(patch[-12:-8], 'little'), 'source checksum: not the right original ROM'
    p = 4
    ss, p = get_num(patch, p); ts, p = get_num(patch, p); ms, p = get_num(patch, p)
    assert ss == len(src)
    p += ms
    out = bytearray(ts)
    o = srel = trel = 0
    end = len(patch) - 12
    while p < end:
        d, p = get_num(patch, p)
        cmd, ln = d & 3, (d >> 2) + 1
        if cmd == 0:
            out[o:o + ln] = src[o:o + ln]
        elif cmd == 1:
            out[o:o + ln] = patch[p:p + ln]
            p += ln
        elif cmd == 2:
            d, p = get_num(patch, p)
            srel += -(d >> 1) if d & 1 else d >> 1
            out[o:o + ln] = src[srel:srel + ln]
            srel += ln
        else:
            d, p = get_num(patch, p)
            trel += -(d >> 1) if d & 1 else d >> 1
            period = o - trel                              # may overlap its own output: a repeating pattern
            if period >= ln:
                out[o:o + ln] = out[trel:trel + ln]
            else:
                out[o:o + ln] = (bytes(out[trel:o]) * (ln // period + 1))[:ln]
            trel += ln
        o += ln
    assert o == ts, 'output size'
    assert zlib.crc32(out) == int.from_bytes(patch[-8:-4], 'little'), 'target checksum'
    return bytes(out)

if __name__ == '__main__':
    cmd, a, b, c = sys.argv[1:5]
    if cmd == 'make':
        src, tgt = open(a, 'rb').read(), open(b, 'rb').read()
        patch, (sr, tr, sc, rn) = make(src, tgt)
        assert apply(src, patch) == tgt, 'round trip failed'
        open(c, 'wb').write(patch)
        print(f'{c}: {len(patch):,} B (source read {sr:,}, source copy {sc:,}, byte runs {rn:,}, literal {tr:,}); verified by applying it')
    elif cmd == 'apply':
        open(c, 'wb').write(apply(open(a, 'rb').read(), open(b, 'rb').read()))
        print(f'{c} written')
