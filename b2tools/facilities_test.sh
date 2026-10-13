#!/bin/zsh
# facilities agent: one emulator test = one build of the agent's ROM with HOENN_TEST_WARP (Littleroot's town sign warps
# there) + one silent DeSmuME walk (b2tools/walk.py; one emulator at a time, closed when the walk ends).
#   zsh b2tools/facilities_test.sh ZONE,X,Z OUT.png "ROOM ..." MOVES...
# "ROOM ...": recipes to rebuild first (may be ""); rooms other agents added since this agent's copy of work/interiors was
# made are rebuilt too (the interiors patch needs every room a data/interiors json names). MOVES run after the warp.
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2
W=$1; OUT=$2; ROOMS=$3; shift 3
MISSING=$(python3 -c "
import json, glob, os
miss = set()
for f in glob.glob('data/interiors/*.json'):
    d = json.load(open(f))
    if d.get('room') and not os.path.exists(f\"work/agents/facilities/interiors/{d['room']}/room.json\"): miss.add(d['room'])
print(' '.join(sorted(miss)))")
HOENN_TEST_WARP=$W HOENN_AGENT=facilities zsh b2tools/agent_build_rooms.sh ${=MISSING} ${=ROOMS} 2>&1 | grep -E "rror|nds|Trace" | tail -3
cd b2tools && nice ../.venv/bin/python walk.py ../work/agents/facilities/rom/hoenn.nds ../work/emu/base_littleroot.dst $OUT \
  C173,361 G184,361 G184,366 G183,366 U1 A W300 "$@" 2>&1 | grep -E "calib|goto|travel|pos |shots|rror|Trace"
