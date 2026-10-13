#!/bin/zsh
# v16.3 new-game smoke test with freeze_fix's driver (inputs only): run A (Fairy on, modern split, Hoenn music, NEW
# sprites), run B (Fairy off, classic split, Unova music, CLASSIC sprites), Ruby R (run A's answers, to the lab starter).
# Birch's four questions are answered by the kit's own mk_boot.py (4th answer: classic|new).  zsh smoke_v162.sh
H=~/Documents/GitHub/HoennB2; FF=$H/work/agents/freeze_fix; T=$FF/tests; PY=$H/.venv/bin/python
SM=$H/work/agents/v163_smoke; mkdir -p $SM
cp -c $H/release/Pokemon_Sapphire_NDS_v16.3.nds $SM/s.nds; cp -c $H/release/Pokemon_Ruby_NDS_v16.3.nds $SM/r.nds
F='MC9\|^Slot\|^ROM\|WIFI\|Backup\|decrypted\|DeSmuME\|Savestate\|Save created\|^$\|Microphone\|SoftRast\|^	'
st() { V=$1; ROM=$2; shift 2; for s in "$@"; do echo "=== $V $s"; (cd $T/pt && FF_ROM=$ROM $PY ff.py $V $s 2>&1 | grep -v "$F" | tail -6); done; }
boot() { V=$1; ROM=$2; shift 2; mkdir -p $FF/states/$V; echo "=== $V boot $*"; (cd $T && $PY $H/b2tools/release_kit/mk_boot.py $ROM $FF/states/$V "$@" 2>&1 | grep -v "$F" | tail -3); }
for V in A2 B2; do
  if [ $V = A2 ]; then boot $V $SM/s.nds yes yes hoenn new; else boot $V $SM/s.nds no no unova classic; fi
  st $V $SM/s.nds house lr may birch train dex catch wallmap
  echo "=== $V setmon"; (cd $T/pt && FF_ROM=$SM/s.nds FROM=ng5_caught.dst TO=evo0.dst I=0 SP=265 EXP=$([ $V = A2 ] && echo 720 || echo 500) $PY ff.py $V setmon 2>&1 | grep -v "$F" | tail -2)
  st $V $SM/s.nds evo save cont
done
boot R2 $SM/r.nds yes yes hoenn new
st R2 $SM/r.nds house lr may birch
echo "=== done"
