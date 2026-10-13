#!/bin/zsh
# ship_hideouts agent build (notes/INTERIORS.md, "The Abandoned Ship and the hideouts"): like b2tools/agent_build_caves.sh, but the zone files come from
# b2tools/ship_hideouts_rooms.py (the ship's rooms and the hideouts are rooms of models_interior.py, not caves):
# the agent's own world (b2tools/world.py: Route 108's door to the Abandoned Ship, Lilycove's big-room door to the Aqua
# Hideout), the zone files, the named rooms (rebuild_interiors.sh into the agent's copy of work/interiors), a ROM with
# rebuild_slice.sh's full patch list (v12: ... centers trainers story standalone).
#   HOENN_AGENT=ship_hideouts zsh b2tools/ship_hideouts_build.sh [ROOM ...]
#   NOWORLD=1 ...                 reuse the agent's world        SH_ARGS=--magma ...  also the Magma Hideout's zone files
#   SH_PATCHES=test_cave_kit ...  extra (test-only) patches after the list (caves_east's kit: badges, HMs, Mudkip)
#   HOENN_TEST_WARP=zone,x,z ...  Littleroot's sign warps there (notes/TESTING.md); HOENN_TEST_NO_WILD=1: no battles
# Output: work/agents/ship_hideouts/rom/hoenn.nds (copy it to a unique name before testing)
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
A=$PWD/work/agents/ship_hideouts
export HOENN_INTERIORS_DIR=$A/interiors HOENN_JAVA_DIR=$A/java HOENN_WORLD_DIR=$A/world HOENN_BUILD_DIR=$A/rom
export HOENN_SKIP_UNBUILT_ROOMS=1          # rooms other agents added after our copy of work/interiors: left out
mkdir -p $A
[[ -d $HOENN_INTERIORS_DIR ]] || cp -R work/interiors $HOENN_INTERIORS_DIR
CP="${HOENN_JAVA_DIR}:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar"
(cd b2tools && nice python3 ship_hideouts_rooms.py ${=SH_ARGS} > $A/rooms.report.txt)     # zone jsons first: world.py
if [[ -z $NOWORLD || ! -f $HOENN_WORLD_DIR/world.json ]]; then                           # gives big rooms their doors
  (cd b2tools && nice python3 world.py > $A/world.report.txt) && head -1 $A/world.report.txt
  for d in $HOENN_WORLD_DIR/cells/*/; do echo "${d}terrain.dae ${d}terrain.nsbmd"; done > $HOENN_WORLD_DIR/batch.txt
  nice java -Djava.awt.headless=true -cp "$CP" ToNsbmd --batch $HOENN_WORLD_DIR/batch.txt $HOENN_WORLD_DIR/palettes.txt > /dev/null
fi
(cd b2tools && nice python3 ship_hideouts_rooms.py ${=SH_ARGS} > $A/rooms.report.txt)     # door indices of this world
grep -v "^  story" $A/rooms.report.txt | head -40
(( $# > 0 )) && nice zsh b2tools/rebuild_interiors.sh "$@" | tail -2
(cd b2tools && nice python3 build_rom.py --clean test_door_to_nuvema hoenn_world area2_buildings text scripts encounters \
  encounter_rules hoenn_season hoenn_textures sprites exp_share hm_free starters interiors opening hoenn_intro title \
  zone_effects shops trade_evos centers trainers story standalone ${=SH_PATCHES} > $A/build_rom.log 2>&1) || { tail -20 $A/build_rom.log; exit 1; }
grep -E "nds|left out|rror" $A/build_rom.log | cut -c1-300
rm -rf $HOENN_BUILD_DIR/files $HOENN_BUILD_DIR/code     # keep only the ROM (disk space)
