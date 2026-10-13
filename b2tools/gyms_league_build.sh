#!/bin/zsh
# gyms_league agent: like b2tools/agent_build_rooms.sh, but the room builder and the interiors patch can be swapped
# for development copies (GL_BUILDER=<a copy of models_interior.py> GL_PATCH=<a copy of patches/interiors.py>), so the
# shared ones stay untouched until a change is tested. Same outputs: work/agents/gyms_league/{interiors,rom}.
#   [HOENN_TEST_WARP=zone,x,z] zsh b2tools/gyms_league_build.sh [ROOM ...]
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
A=$PWD/work/agents/gyms_league
export HOENN_BUILD_DIR=$A/rom HOENN_INTERIORS_DIR=$A/interiors HOENN_JAVA_DIR=$A/java
# GL_WORLD=1: use our own copy of the overworld (work/agents/gyms_league/world: b2tools/world.py + ToNsbmd, made by hand)
[[ -n $GL_WORLD ]] && export HOENN_WORLD_DIR=$A/world
B=${GL_BUILDER:-models_interior.py}; P=${GL_PATCH:-interiors}
mkdir -p $A
[[ -d $HOENN_INTERIORS_DIR ]] || cp -R work/interiors $HOENN_INTERIORS_DIR
J=$HOENN_JAVA_DIR; O=$HOENN_INTERIORS_DIR
# rooms other agents added since our copy was made: build them too (else the installer misses their files)
missing=($(python3 -c "
import json, glob, os
for f in glob.glob('data/interiors/*.json'):
    r = json.load(open(f)).get('room')
    if r and r != 'truck' and os.path.exists(f'data/interior_layouts/{r}.json') and not os.path.exists(f'$O/{r}/terrain.nsbmd'): print(r)
"))
# our own rooms whose recipe (or our style file) changed since they were built
mine=($(cd b2tools && python3 -c "
import os, gyms_league_rooms as g
st = os.path.getmtime('../data/interior_layouts/_styles_gyms_league.json')
for n in sorted(g.ROOMS):
    t = '$O/' + n + '/terrain.nsbmd'
    if not os.path.exists(t) or max(st, os.path.getmtime('../data/interior_layouts/' + n + '.json')) > os.path.getmtime(t): print(n)
"))
set -- "$@" $missing $mine
CP="${J}:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar"
if [[ $# -gt 0 ]]; then
  mkdir -p $J && nice javac -cp "$CP" -d $J b2tools/java/*.java
  (cd b2tools && nice python3 $B "$@" | cut -c1-200)
  : > $O/batch.txt; : > $O/palettes.txt
  for n in "$@"; do echo "$O/$n/terrain.dae $O/$n/terrain.nsbmd" >> $O/batch.txt; cat $O/$n/palettes.txt >> $O/palettes.txt; done
  nice java -Djava.awt.headless=true -cp "$CP" ToNsbmd --vcol --batch $O/batch.txt $O/palettes.txt > /dev/null
fi
(cd b2tools && nice python3 build_rom.py --clean test_door_to_nuvema hoenn_world area2_buildings text scripts encounters \
  encounter_rules hoenn_season hoenn_textures sprites exp_share hm_free starters $P opening hoenn_intro \
  | grep -E "nds|rror|patch interiors" | tr ';' '\n' | grep -E "nds|rror|camera|chunk|pack|patch interiors" | cut -c1-200 > $A/build_report.txt)
grep -E "nds|rror" $A/build_report.txt | tail -3
