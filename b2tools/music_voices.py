"""Compare GBA (Ruby/Sapphire) instrument samples with Black 2's instrument library, to propose the closest Black 2
instrument for each GBA voice (notes/MUSIC.md "Instrument mapping"). Read-only analysis.

    python3 music_voices.py [N]        Black 2's library (BANK_MUS_WB_SOUNDLIST) programs vs the GBA's named samples

Black 2's BANK_MUS_WB_SOUNDLIST (bank 1000, no sequence uses it) holds the whole instrument set with one program
number per instrument (80 = the drum kit, 100-107 = PSG square waves); each song's own bank copies the instruments
it uses, under the same program numbers, into the song's own wave archive. Features per instrument: the harmonic
spectrum of its middle-register sample (loop part, or the body of a one-shot sample) at the sample's own pitch, and
whether it sustains (looped wave and sustain level) or decays.
"""
import os, sys, struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sdat import SDAT, DEFAULT, parse_sbnk, parse_swar, decode_wave, wave_info  # noqa: E402
import m4a  # noqa: E402

NH = 16


def harmonics(x, sr, f0):
    """dB of the first NH harmonics (relative to the strongest), from a 8192-point FFT of a stretch of x."""
    n = 8192
    if len(x) < 64: return np.full(NH, -60.0)
    seg = np.resize(x, n) if len(x) < n else x[:n]
    spec = np.abs(np.fft.rfft(seg * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    out = []
    for k in range(1, NH + 1):
        f = k * f0
        if f > sr / 2 * 0.95: out.append(-60.0); continue
        band = (freqs > f * 0.97) & (freqs < f * 1.03)
        out.append(20 * np.log10(spec[band].max() + 1e-9) if band.any() else -60.0)
    out = np.array(out)
    return np.clip(out - out.max(), -60, 0)


def body(s, loop):
    """The steady part of a sample: its loop (repeated), else from 15% to 60% of a one-shot sample."""
    if loop is not None and len(s) - loop > 32:
        return np.tile(s[loop:], 1 + 8192 // max(1, len(s) - loop))
    a, b = int(len(s) * 0.15), int(len(s) * 0.6)
    return s[a:b] if b - a > 256 else s


def decay_time(s, sr):
    """Seconds until a one-shot sample's RMS falls 20 dB below its peak (loops: 9.9)."""
    win = max(1, int(sr * 0.01))
    rms = np.sqrt(np.convolve(s ** 2, np.ones(win) / win, mode='valid') + 1e-12)
    pk = rms.argmax()
    below = np.where(rms[pk:] < rms[pk] * 0.1)[0]
    return (below[0] / sr) if len(below) else len(s) / sr


def b2_library(s=None):
    """{program: dict(features...)} of BANK_MUS_WB_SOUNDLIST, using the region nearest key 66."""
    s = s or SDAT(open(DEFAULT, 'rb').read())
    bank = s.index('bank', 'BANK_MUS_WB_SOUNDLIST')
    prog = parse_sbnk(s.bank(bank))
    waves = parse_swar(s.wavearc(s.info['bank'][bank]['wavearcs'][0]))
    out = {}
    for p, (t, regs) in sorted(prog.items()):
        if t not in (1, 17): continue
        r = min(regs, key=lambda r: abs(r[5] - 66))
        x, sr, loop = decode_wave(waves[r[3]])
        f0 = 440 * 2 ** ((r[5] - 69) / 12)
        out[p] = dict(type=t, keys=(regs[0][0] if t == 17 else 0, regs[-1][1]), bases=[q[5] for q in regs],
                      adsr=r[6:10], loop=loop is not None, h=harmonics(body(x, loop), sr, f0),
                      decay=decay_time(x, sr) if loop is None else 9.9, waves=[q[3] for q in regs])
    return out


def gba_library(rom=None):
    """{sample name: features} for pokeruby's named instrument samples (sound/direct_sound_data.inc)."""
    rom = rom or m4a.GbaRom()
    rom.sample_name(0)
    out = {}
    for addr, name in rom.sample_names.items():
        if not (name.startswith('sc88pro') or name.startswith('unknown') or name.startswith('trinity')
                or name.startswith('unused')): continue
        w = rom.wave(addr)
        x = np.frombuffer(w['data'], dtype=np.int8).astype(np.float32) / 128
        sr = w['freq']
        loop = w['loop_start'] if w['loop'] else None
        out[name] = dict(loop=w['loop'], h=harmonics(body(x, loop), sr, 261.63),
                         decay=decay_time(x, sr) if loop is None else 9.9)
    return out


def distance(a, b):
    w = np.linspace(1.5, 0.5, NH)
    d = float(np.sqrt(np.mean(w * (a['h'] - b['h']) ** 2)))
    if a['loop'] != b['loop']: d += 4
    return d


def main(argv):
    k = int(argv[0]) if argv else 3
    b2, gba = b2_library(), gba_library()
    print('Black 2 program -> closest GBA samples (distance in dB)')
    for p, f in b2.items():
        best = sorted(gba, key=lambda n: distance(f, gba[n]))[:k]
        print(f'  {p:3d} keys {f["keys"]} bases {f["bases"]} adsr {f["adsr"]} {"loop" if f["loop"] else f"one-shot {f[chr(100)+chr(101)+chr(99)+chr(97)+chr(121)]:.2f}s"}: '
              + ', '.join(f'{n} {distance(f, gba[n]):.1f}' for n in best))
    print('GBA sample -> closest Black 2 programs')
    for n, f in gba.items():
        best = sorted(b2, key=lambda p: distance(b2[p], f))[:k]
        print(f'  {n}: ' + ', '.join(f'{p} {distance(b2[p], f):.1f}' for p in best))


if __name__ == '__main__':
    main(sys.argv[1:])
