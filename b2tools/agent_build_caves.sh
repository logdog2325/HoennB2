#!/bin/zsh
# Test build for a cave agent (notes/CAVES.md): the agent's own world (world.py writes the outdoor cave doors into
# work/agents/$HOENN_AGENT/world/world.json), the named caves' zone files (converter/gen_caves.py: warps, step
# triggers, items, encounters, from that world's door list), the caves themselves (b2tools/models_cave.py via
# rebuild_interiors.sh, into the agent's own copy of work/interiors) and a ROM with b2tools/rebuild_slice.sh's full
# patch list. Caves other agents have not built in this copy are left out by the interiors patch.
#   HOENN_AGENT=caves_east zsh b2tools/agent_build_caves.sh VictoryRoad_1F VictoryRoad_B1F ...
#   NOWORLD=1 ...                       reuse the agent's world (no world.py / ToNsbmd run: ~1.5 min saved)
#   HOENN_TEST_WARP=zone,x,z ...        Littleroot's sign warps there (notes/TESTING.md); HOENN_TEST_NO_WILD=1: no battles
# Output: work/agents/$HOENN_AGENT/rom/hoenn.nds (copy it to a unique name before testing: notes/TESTING.md)
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
: ${HOENN_AGENT:?set HOENN_AGENT to your agent name}
(( $# > 0 )) || { echo "name the caves to build (data/cave_layouts/<Map>.json)"; exit 1; }
A=$PWD/work/agents/$HOENN_AGENT
export HOENN_INTERIORS_DIR=$A/interiors HOENN_JAVA_DIR=$A/java HOENN_WORLD_DIR=$A/world HOENN_BUILD_DIR=$A/rom
mkdir -p $A
[[ -d $HOENN_INTERIORS_DIR ]] || cp -R work/interiors $HOENN_INTERIORS_DIR       # every room as last built by the lead
CP="work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar"
if [[ -z $NOWORLD || ! -f $HOENN_WORLD_DIR/world.json ]]; then
  (cd b2tools && nice python3 world.py > $A/world.report.txt) && head -1 $A/world.report.txt
  for d in $HOENN_WORLD_DIR/cells/*/; do echo "${d}terrain.dae ${d}terrain.nsbmd"; done > $HOENN_WORLD_DIR/batch.txt
  nice java -Djava.awt.headless=true -cp "$CP" ToNsbmd --batch $HOENN_WORLD_DIR/batch.txt $HOENN_WORLD_DIR/palettes.txt > /dev/null
fi
(cd converter && nice python3 gen_caves.py "$@" > $A/gen_caves.report.txt) && grep -v "^  " $A/gen_caves.report.txt | head -20
nice zsh b2tools/rebuild_interiors.sh "$@" | tail -2
(cd b2tools && nice python3 build_rom.py --clean test_door_to_nuvema hoenn_world area2_buildings text scripts encounters \
  encounter_rules hoenn_season hoenn_textures sprites boulder_1x1 objects3d exp_share hm_free starters interiors opening hoenn_intro title \
  zone_effects shops trade_evos centers trainers story weather standalone dive capture_demo trades fixed_weather game_clear boat_demos > $A/build_rom.log 2>&1) || { tail -20 $A/build_rom.log; exit 1; }
grep -E "nds|caves left out|rror" $A/build_rom.log | cut -c1-300
rm -rf $HOENN_BUILD_DIR/files $HOENN_BUILD_DIR/code     # keep only the ROM (disk space)
