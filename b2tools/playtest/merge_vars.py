"""merge_vars.py FROM_STATE TO_STATE OUT: copy the works that are 0 in TO but set in FROM (early-story progress a
chapter test kit does not set), and the flags set in FROM that TO lacks, if listed with --flags. Crash tour only."""
import sys, struct; sys.path.insert(0, sys.path[0])
import subprocess, json, os
from pt import *
import flags as F
if sys.argv[1] == 'dump':
    g = G(sys.argv[2])
    ew = F.ew(g)
    works = struct.unpack('<431H', g.rd(ew, 862))
    flg = g.rd(ew + 0x35e, 383)
    json.dump({'works': works, 'flags': list(flg)}, open(sys.argv[3], 'w'))
else:
    src = json.load(open(sys.argv[2]))
    g = G(sys.argv[3])
    ew = F.ew(g)
    n = 0
    for i, v in enumerate(src['works']):
        cur = g.u16(ew + 2 * i)
        if cur == 0 and v != 0 and i >= 0x20:
            g.e.d.memory.write_short(ew + 2 * i, v); n += 1
            print(f'work {0x4000 + i:#x}: 0 -> {v}')
    print('works merged', n)
    g.save(sys.argv[4])
