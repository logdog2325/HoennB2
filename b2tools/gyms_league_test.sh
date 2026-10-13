#!/bin/zsh
# gyms_league agent: one test = one build with HOENN_TEST_WARP + one silent emulator walk (one emulator at a time).
#   zsh b2tools/gyms_league_test.sh ZONE,X,Z OUT.png MOVES...     (moves after the town-sign warp; see b2tools/walk.py)
set -e
cd ~/Documents/GitHub/HoennB2
W=$1; OUT=$2; shift 2
GL_BUILDER=${GL_BUILDER:-models_interior.py} GL_PATCH=${GL_PATCH:-interiors} \
  HOENN_TEST_WARP=$W zsh b2tools/gyms_league_build.sh 2>&1 | grep -E "rror|nds" | tail -2
cd b2tools && nice ../.venv/bin/python walk.py ../work/agents/gyms_league/rom/hoenn.nds ../work/emu/base_littleroot.dst $OUT \
  C173,361 G184,361 G184,366 G183,366 U1 A W300 "$@" 2>&1 | grep -E "calib|goto|travel|pos |shots|rror|Trace"
