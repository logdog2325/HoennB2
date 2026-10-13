#!/bin/zsh
# The specials agent's test build: builds the rooms other agents added since this agent's copy of work/interiors was
# made (the interiors patch installs every data/interiors/*.json room), then b2tools/agent_build_rooms.sh.
#   HOENN_TEST_WARP=zone,x,z zsh b2tools/specials_build.sh [ROOM ...]
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
export HOENN_AGENT=specials
A=$PWD/work/agents/specials
miss=($(cd b2tools && HOENN_INTERIORS_DIR=$A/interiors python3 specials.py missing))
[[ ${#miss} -gt 0 ]] && HOENN_INTERIORS_DIR=$A/interiors HOENN_JAVA_DIR=$A/java nice zsh b2tools/rebuild_interiors.sh $miss | tail -1
zsh b2tools/agent_build_rooms.sh "$@"
