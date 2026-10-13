#!/bin/zsh
# Test build for an interiors agent working in parallel with others (notes/INTERIORS_PLAN.md): the overworld
# (work/world, made by b2tools/rebuild_slice.sh) is only read; the agent's rooms are rebuilt into its own copy of
# work/interiors, so agents never overwrite each other's room builds.
#   HOENN_AGENT=houses zsh b2tools/agent_build_rooms.sh [ROOM ...]      (ROOM = recipe names to rebuild; none = no rooms)
#   HOENN_TEST_WARP=zone,x,z ...: Littleroot's town sign warps there (start: work/emu/base_littleroot.dst)
# Output: work/agents/$HOENN_AGENT/rom/hoenn.nds
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
: ${HOENN_AGENT:?set HOENN_AGENT to your agent name}
A=$PWD/work/agents/$HOENN_AGENT
export HOENN_BUILD_DIR=$A/rom HOENN_INTERIORS_DIR=$A/interiors HOENN_JAVA_DIR=$A/java
mkdir -p $A
[[ -d $HOENN_INTERIORS_DIR ]] || cp -R work/interiors $HOENN_INTERIORS_DIR      # every room as last built by the lead
[[ $# -gt 0 ]] && nice zsh b2tools/rebuild_interiors.sh "$@" | tail -3
(cd b2tools && nice python3 build_rom.py --clean test_door_to_nuvema hoenn_world area2_buildings text scripts encounters \
  encounter_rules hoenn_season hoenn_textures sprites boulder_1x1 objects3d exp_share hm_free starters interiors opening hoenn_intro title zone_effects shops trade_evos centers trainers story weather standalone dive capture_demo trades fixed_weather game_clear boat_demos \
  | grep -E "nds|rror|patch interiors" | cut -c1-300)
rm -rf $HOENN_BUILD_DIR/files $HOENN_BUILD_DIR/code     # keep only the ROM (disk space)
