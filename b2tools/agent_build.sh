#!/bin/zsh
# Test build for one agent working in parallel with others (notes/OVERWORLD_PLAN.md): only the steps that depend on
# the agent's own work, into its own folders. Shared inputs (plans, zones, encounter tables, the slice's buildings)
# are made by b2tools/rebuild_slice.sh and only read here.
#   HOENN_AGENT=water HOENN_TERRAIN=water zsh b2tools/agent_build.sh             (terrain module)
#   HOENN_AGENT=towns1 HOENN_TOWN_GROUPS=towns1 zsh b2tools/agent_build.sh       (town buildings group)
# Output: work/agents/$HOENN_AGENT/rom/hoenn.nds (world in work/agents/$HOENN_AGENT/world). Extra args = extra patches.
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
: ${HOENN_AGENT:?set HOENN_AGENT to your agent name}
python3 b2tools/version.py > /dev/null      # HOENN_VERSION=ruby|emerald: the ROM goes to rom_ruby/ or rom_emerald/ (notes/RUBY.md "WP0 layout")
A=$PWD/work/agents/$HOENN_AGENT
R=rom; [[ "${HOENN_VERSION:l}" == ruby ]] && R=rom_ruby
[[ "${HOENN_VERSION:l}" == emerald ]] && R=rom_emerald
export HOENN_WORLD_DIR=$A/world HOENN_BUILD_DIR=$A/$R
mkdir -p $A
CP="work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar"
(cd b2tools && python3 world.py > $A/world.report.txt) && head -1 $A/world.report.txt
for d in $HOENN_WORLD_DIR/cells/*/; do echo "${d}terrain.dae ${d}terrain.nsbmd"; done > $HOENN_WORLD_DIR/batch.txt
java -Djava.awt.headless=true -cp "$CP" ToNsbmd --batch $HOENN_WORLD_DIR/batch.txt $HOENN_WORLD_DIR/palettes.txt > /dev/null
(cd b2tools && python3 build_rom.py --clean test_door_to_nuvema hoenn_world area2_buildings text scripts encounters \
  encounter_rules hoenn_season hoenn_textures "$@" | grep -E "nds|patch (hoenn_world|area2|hoenn_textures)" | cut -c1-200)
# keep only the ROM: the cloned file tree and code copies are rebuilt by the next --clean build (disk space)
rm -rf $HOENN_BUILD_DIR/files $HOENN_BUILD_DIR/code
