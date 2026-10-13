#!/bin/zsh
# dive agent build (notes/DIVE.md): like b2tools/agent_build_caves.sh, on the lead's world (the dive maps have no
# outdoor doors, so no world.py run: HOENN_WORLD_DIR, default work/world, is only read): the named maps' zone files
# (converter/gen_caves.py for maps with a cave recipe, b2tools/dive_rooms.py for the room-built ones), the maps
# (rebuild_interiors.sh into the agent's copy of work/interiors), a ROM with rebuild_slice.sh's full patch list + `dive`.
#   HOENN_AGENT=dive zsh b2tools/dive_build.sh [MAP ...]
#   DV_PATCHES=test_cave_kit ...  extra (test-only) patches after the list (caves_east's kit: badges, HMs, Mudkip, warp)
#   HOENN_TEST_WARP=zone,x,z ...  Littleroot's sign warps there (notes/TESTING.md); HOENN_TEST_NO_WILD=1: no battles
# Output: work/agents/$HOENN_AGENT/rom/hoenn.nds (copy it to a unique name before testing: notes/TESTING.md)
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
A=$PWD/work/agents/${HOENN_AGENT:-dive}
export HOENN_INTERIORS_DIR=$A/interiors HOENN_JAVA_DIR=$A/java HOENN_BUILD_DIR=$A/rom
export HOENN_WORLD_DIR=${HOENN_WORLD_DIR:-$PWD/work/world}
export HOENN_SKIP_UNBUILT_ROOMS=1          # rooms other agents added after our copy of work/interiors: left out
mkdir -p $A
[[ -d $HOENN_INTERIORS_DIR ]] || cp -c -R work/interiors $HOENN_INTERIORS_DIR
caves=(); rooms=()
for n in "$@"; do if [[ -f data/cave_layouts/$n.json ]]; then caves+=($n); else rooms+=($n); fi; done
if (( ${#caves} > 0 )); then
  (cd converter && nice python3 gen_caves.py $caves > $A/gen_caves.report.txt) && grep -v "^  " $A/gen_caves.report.txt | head -40
fi
if (( ${#rooms} > 0 )) && [[ -f b2tools/dive_rooms.py ]]; then (cd b2tools && nice python3 dive_rooms.py $rooms | tail -20); fi
(( $# > 0 )) && nice zsh b2tools/rebuild_interiors.sh "$@" | tail -2
(cd b2tools && nice python3 build_rom.py --clean test_door_to_nuvema hoenn_world area2_buildings text scripts encounters \
  encounter_rules hoenn_season hoenn_textures sprites exp_share hm_free starters interiors opening hoenn_intro title \
  zone_effects shops trade_evos centers trainers story standalone dive ${=DV_PATCHES} > $A/build_rom.log 2>&1) || { tail -20 $A/build_rom.log; exit 1; }
grep -E "nds|left out|rror|WARNING|patch dive" $A/build_rom.log | cut -c1-600
rm -rf $HOENN_BUILD_DIR/files $HOENN_BUILD_DIR/code     # keep only the ROM (disk space)
