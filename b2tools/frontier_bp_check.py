"""frontier_core: the BP award (frontier_core.c award(), compiled for this Mac from the real source) against pokeemerald's
GiveBattlePoints re-done in Python from pokeemerald's own table, for every facility, battle mode, streak 0-300, Brain or not."""
import os, re, sys, subprocess, tempfile, importlib.util
ROOT = os.path.expanduser('~/Documents/GitHub/HoennB2')
P = os.path.join(ROOT, 'b2tools', 'patches')
spec = importlib.util.spec_from_file_location('fc', os.path.join(P, 'frontier_core.py')); fc = importlib.util.module_from_spec(spec); spec.loader.exec_module(fc)
src = open(os.path.join(P, 'frontier_core.c')).read()
body = 'static u32 udiv' + src.split('static u32 udiv', 1)[1].split('static u16 *records', 1)[0]
body += 'static u32 award' + src.split('static u32 award', 1)[1].split('\nu32 FR_CmdGet', 1)[0]
if '--old' in sys.argv: body = body.replace('if (row) row--;', '')     # the code before the fix: must differ
body = re.sub(r'/\* pokeemerald CheckPartyIneligibility.*', '', body, flags=re.S)   # (stop before banned_names)
with tempfile.TemporaryDirectory() as t:
    hdr, info = fc.data_header()
    open(os.path.join(t, 'frontier_core_data.h'), 'w').write(hdr)
    c = ('#include <stdio.h>\ntypedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;\n'
         '#define K_FACILITY 1\n#define K_BATTLE_MODE 2\n#include "frontier_core_data.h"\n' + body +
         '\nint main(void){u16 rec[96]={0};for(u32 f=0;f<7;f++)for(u32 m=0;m<4;m++)for(u32 s=0;s<=300;s++)for(u32 b=0;b<2;b++)'
         '{rec[1]=f;rec[2]=m;printf("%u %u %u %u %u\\n",f,m,s,b,award(rec,s,b));}return 0;}\n')
    open(os.path.join(t, 'h.c'), 'w').write(c)
    subprocess.run(['clang', '-w', '-I', t, '-o', os.path.join(t, 'h'), os.path.join(t, 'h.c')], check=True)
    out = subprocess.run([os.path.join(t, 'h')], capture_output=True, text=True, check=True).stdout.split('\n')
# pokeemerald, from its own source text
em = open(os.path.join(ROOT, 'external', 'pokeemerald', 'src', 'frontier_util.c')).read()
rows, div = fc.awards()
def emerald(f, m, streak, brain):
    n = streak // div[f]
    if n != 0: n -= 1
    n = min(n, len(rows) - 1)
    return rows[n][f][m] + (10 if brain else 0)
bad = 0
for line in out:
    if not line: continue
    f, m, s, b, v = map(int, line.split())
    if m >= [4, 2, 2, 1, 2, 1, 1][f]: continue        # FRONTIER_MODE_COUNT per facility in the table (missing = no mode)
    if v != emerald(f, m, s, b): bad += 1; print('DIFF', f, m, s, b, v, emerald(f, m, s, b))
names = ['Tower', 'Dome', 'Palace', 'Arena', 'Factory', 'Pike', 'Pyramid']
print(f'{len(out) - 1} cases, {bad} differ from pokeemerald; examples:')
for f, s in [(0, 7), (0, 14), (1, 1), (1, 2), (5, 14), (5, 28), (6, 7)]:
    print(f'  {names[f]} streak {s}: {emerald(f, 0, s, 0)} BP (+10 with the Brain: {emerald(f, 0, s, 1)})')
