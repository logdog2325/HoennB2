#!/bin/zsh
# Shops agent test build: the steps of b2tools/agent_build_rooms.sh plus two stand-ins until the shared tools have them
# (see b2tools/shops_cells.py and b2tools/shops_rompatch.py):
#   1. rebuild ROOM ... into work/agents/shops/interiors (rebuild_interiors.sh, as agent_build_rooms.sh does)
#   2. Black 2 tile attributes in their collision (counters, shop shelves, PC, vending machine)
#   3. the ROM: HOENN_AGENT=shops zsh b2tools/agent_build_rooms.sh (no rooms: uses the rooms built above)
#   4. Sapphire's shop lists (build patch `shops`) written into that ROM in place
#   zsh b2tools/shops_build.sh [ROOM ...]          (HOENN_TEST_WARP=zone,x,z passes through)
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
export HOENN_AGENT=shops
A=$PWD/work/agents/shops
# rooms other agents added to data/interiors since our copy of work/interiors was made: build them too (else the
# interiors patch stops on their missing room.json)
missing=($(python3 -c "
import json, glob, os
for f in glob.glob('data/interiors/*.json'):
    r = json.load(open(f)).get('room')
    if r and r != 'truck' and not os.path.exists(f'$A/interiors/{r}/room.json') and os.path.exists(f'data/interior_layouts/{r}.json'): print(r)"))
[[ ${#missing} -gt 0 ]] && HOENN_INTERIORS_DIR=$A/interiors HOENN_JAVA_DIR=$A/java nice zsh b2tools/rebuild_interiors.sh $missing | tail -1
if [[ $# -gt 0 ]]; then
  HOENN_INTERIORS_DIR=$A/interiors HOENN_JAVA_DIR=$A/java nice zsh b2tools/rebuild_interiors.sh "$@" | tail -2
  (cd b2tools && python3 shops_cells.py "$@")
fi
zsh b2tools/agent_build_rooms.sh
(cd b2tools && python3 shops_rompatch.py $A/rom/hoenn.nds)
