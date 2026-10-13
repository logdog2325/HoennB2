#!/bin/zsh
# Build the interior rooms (notes/INTERIORS.md) into work/interiors/<name>/: every recipe in data/interior_layouts
# (b2tools/models_interior.py, terrain converted with ToNsbmd --vcol: Black 2 rooms are shaded by vertex colours) and
# the moving truck (b2tools/models_truck.py, terrain and rear door with normals, as it was designed).
# Installed by the build patch `interiors` (b2tools/patches/interiors.py, data/interiors/<zone>.json).
#   zsh b2tools/rebuild_interiors.sh [NAME ...]          (default: all recipes and the truck)
#   b2tools/preview_interior.py NAME                    renders a room without the emulator
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
J=${HOENN_JAVA_DIR:-work/java}           # agents may compile into their own folder
CP="${J}:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar"
mkdir -p $J && javac -cp "$CP" -d $J b2tools/java/*.java
O=${HOENN_INTERIORS_DIR:-work/interiors}    # agents: their own copy (b2tools/agent_build_rooms.sh)
mkdir -p $O
O=${O:a}     # absolute: the truck step below runs in b2tools/ (a relative O put the truck in b2tools/work/interiors, emerald_wp0)
all=(${@:#truck}); [[ $# -eq 0 ]] && all=($(cd data/interior_layouts && ls *.json | grep -v '^_' | sed 's/\.json$//'))
# caves (a recipe in data/cave_layouts: b2tools/models_cave.py, notes/CAVES.md) are built by the cave builder; with no
# names, every cave too. Everything else as before.
names=(); caves=()
for n in $all; do if [[ -f data/cave_layouts/$n.json ]]; then caves+=($n); else names+=($n); fi; done
[[ $# -eq 0 && -d data/cave_layouts ]] && caves+=($(cd data/cave_layouts && ls *.json | grep -v '^_' | sed 's/\.json$//'))
if (( ${#names} > 0 )) || (( ${#caves} == 0 )); then (cd b2tools && python3 models_interior.py $names); fi
(( ${#caves} > 0 )) && (cd b2tools && python3 models_cave.py $caves)
names+=($caves)
: > $O/batch.txt; : > $O/palettes.txt
[[ ${#names} -gt 0 ]] && for n in $names; do echo "$O/$n/terrain.dae $O/$n/terrain.nsbmd" >> $O/batch.txt; cat $O/$n/palettes.txt >> $O/palettes.txt; done
[[ ${#names} -gt 0 ]] && java -Djava.awt.headless=true -cp "$CP" ToNsbmd --vcol --batch $O/batch.txt $O/palettes.txt > /dev/null
if [[ $# -eq 0 || " $* " == *" truck "* ]]; then
  (cd b2tools && python3 models_truck.py ${O:a}/truck > /dev/null)
  java -Djava.awt.headless=true -cp "$CP" ToNsbmd $O/truck/terrain.dae $O/truck/terrain.nsbmd $O/truck/palettes.txt > /dev/null
  # the open door's light: unlit (white vertex colours), so it shows at the textures' full brightness
  java -Djava.awt.headless=true -cp "$CP" ToNsbmd --vcol $O/truck/door.dae $O/truck/door.nsbmd $O/truck/palettes.txt > /dev/null
fi
ls -la $O/*/terrain.nsbmd | awk '{print $5, $9}'
