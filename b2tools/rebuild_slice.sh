#!/bin/zsh
# Rebuild the Hoenn overworld (all connected maps; Littleroot, Route 101, Oldale complete): plan -> terrain -> buildings -> textures -> ROM (see notes/LITTLEROOT.md). Output: work/rom/hoenn.nds
# Version (notes/RUBY.md "WP0 layout"): HOENN_VERSION=ruby makes the same shared world and Sapphire files, then Ruby's
# overlays (wild tables, Magma Hideout rooms) and the Ruby ROM in work/rom_ruby (or HOENN_BUILD_DIR); unset = Sapphire.
# HOENN_VERSION=emerald (notes/EMERALD.md): the shared world and Sapphire files as for Sapphire (Sapphire's world in work/world,
# HOENN_SAPPHIRE_WORLD_DIR wins), then Emerald's overlays and Emerald's own world from pokeemerald's maps in
# work/world_emerald (HOENN_WORLD_DIR wins; notes/EMERALD.md "Emerald's world"), and the Emerald ROM in work/rom_emerald.
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
python3 b2tools/version.py > /dev/null      # stops on a wrong HOENN_VERSION
RV=${${HOENN_VERSION:-sapphire}:l}; unset HOENN_VERSION   # the world and the shared generators are Sapphire's
ROMD=$(HOENN_VERSION=$RV python3 -c "import sys, os; sys.path.insert(0, 'b2tools'); import version; print(os.path.abspath(version.build_dir('work/rom')))")
WD=${HOENN_WORLD_DIR:-work/world}    # world output (agents use their own, with HOENN_BUILD_DIR for the ROM)
[[ $RV == emerald && -z "$HOENN_WORLD_DIR" ]] && WD=work/world_emerald   # Emerald's own world (version.world_dir)
# EMERALD-2 (emerald_world 2026-10-12): the shared (Sapphire) generators below run on Sapphire's world only (WD), never
# on Emerald's (EWD, built in the Emerald block from pokeemerald's maps); from there on everything reads Emerald's world
EWD=; if [[ $RV == emerald ]]; then EWD=$WD; WD=${HOENN_SAPPHIRE_WORLD_DIR:-work/world}; fi
mkdir -p $(dirname $WD) && REPORT="$(cd $(dirname $WD) && pwd)/$(basename $WD).report.txt"
export HOENN_WORLD_DIR=$(cd $(dirname $WD) && pwd)/$(basename $WD)
CP="work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar"
mkdir -p work/java && javac -cp "$CP" -d work/java b2tools/java/*.java   # ToNsbmd (CTRMapV writer)
# building models first (sweep_outdoor 2026-10-11: world.py reads them to decide which building tiles are walkable;
# built after it, a fresh world used the previous models): every town builder (models_<town>.py -> work/buildings/<town>/*.dae), one ToNsbmd batch per town
for T in littleroot oldale truck_ext petalburg rustboro dewford slateport mauville verdanturf fallarbor lavaridge fortree lilycove mossdeep pacifidlog routes evergrande standalone; do
  (cd b2tools && python3 models_$T.py ../work/buildings/$T > /dev/null)
  for d in work/buildings/$T/*.dae; do echo "$d ${d%.dae}.nsbmd"; done > work/buildings/$T/batch.txt
  java -Djava.awt.headless=true -cp "$CP" ToNsbmd --batch work/buildings/$T/batch.txt work/buildings/$T/palettes.txt > /dev/null
done
(cd converter && python3 allocate_zones.py > /dev/null && python3 allocate_interiors.py > /dev/null && for m in $(python3 -c "import json; print(' '.join(json.load(open('../data/hoenn_zones.json'))['maps']))"); do python3 plan_map.py ../external/pokeruby $m > /dev/null; done)
(cd b2tools && python3 world.py > $REPORT) && head -1 $REPORT
(cd converter && python3 gen_encounters.py | cut -c1-60 && python3 gen_items.py | head -1 && python3 gen_map_content.py | cut -c1-80)
# trainer NPCs follow world.json's zones too: data/hoenn_trainer_npcs.json from Oct 6 predates the zone rectangles and put
# Route 104's Billy and Ivan, Route 117's Anna & Meg and Route 126's Chad in the town/route zone of their cell, where the
# game never spawns them (outdoor sweep 2026-10-07, outdoor_check.py --rom: 'ent')
(cd converter && python3 gen_trainer_npcs.py | cut -c1-120)
(cd b2tools && python3 world.py > $REPORT)     # again, to place the generated signs/NPCs
(cd converter && python3 gen_interiors.py | cut -c1-120)     # rooms behind the doors (data/interiors, after world.json's doors)
(cd converter && python3 gen_caves.py | grep -v "^  " | cut -c1-120)   # caves with a recipe (data/cave_layouts, notes/CAVES.md)
(cd b2tools && python3 ship_hideouts_rooms.py > /dev/null && python3 dive_rooms.py > /dev/null)   # ship/hideout and Dive ship rooms (door indices after world.py)
if [[ $RV == ruby ]]; then    # Ruby's own files, only into the ruby/ overlays: wild tables that differ, the Magma Hideout
  (cd converter && HOENN_VERSION=ruby python3 gen_encounters.py | cut -c1-80 && HOENN_VERSION=ruby python3 gen_caves.py | cut -c1-120)
  # trainers (src/trainers/ruby, src/text/system/ruby 0381-0383 0485, data/ruby) and the text layer (src/text/script/ruby, the
  # place name), WP1; gen_ruby_text.py runs after gen_map_content.py above (it reads the merged src/text/script)
  (cd converter && HOENN_VERSION=ruby python3 gen_trainers.py | cut -c1-120 | sed -n '1,2p' && python3 gen_ruby_text.py | sed -n '2p;$p')
  (cd b2tools && HOENN_VERSION=ruby python3 ship_hideouts_rooms.py MagmaHideout_1F MagmaHideout_B1F MagmaHideout_B2F > /dev/null)
fi
if [[ $RV == emerald ]]; then    # Emerald's own files, only into the emerald/ overlays (notes/EMERALD.md "Phase 0")
  # pokeemerald's wild tables on Sapphire's maps: only the files that differ from Sapphire's (src/encounters/emerald)
  (cd converter && HOENN_VERSION=emerald python3 gen_encounters.py | cut -c1-80 && HOENN_VERSION=emerald python3 gen_caves.py | cut -c1-120)
  # phase 1 data (EMERALD-1, notes/EMERALD.md): trainers (src/trainers/emerald, src/text/system/emerald 0381-0383 0485,
  # data/emerald: Emerald's registry, data, classes, messages; levels by Sapphire's curve: level_scaling.py's Emerald
  # check), item balls + move tutors list, hidden items, marts, Pokédex text (src/text/emerald, system/emerald/0443)
  (cd converter && HOENN_VERSION=emerald python3 gen_trainers.py | cut -c1-200 | sed -n '1,2p')
  (cd converter && HOENN_VERSION=emerald python3 gen_items.py | head -1 | cut -c1-200 && HOENN_VERSION=emerald python3 gen_hidden_items.py | head -1 | cut -c1-200)
  (cd b2tools && HOENN_VERSION=emerald python3 shops_data.py | grep "lists differ" | cut -c1-200)
  (cd converter && HOENN_VERSION=emerald python3 gen_dex_text.py --install | tail -1)
  # TODO EMERALD-2 rooms/caves/variants (data/versions.json rooms + room_variants.emerald), EMERALD-3 story and text
  # (src/field_scripts/emerald, src/text/*/emerald, data/story/emerald, gen_map_content/gen_items in Emerald mode)
  # Emerald's world (EMERALD-2, notes/EMERALD.md "Emerald's world"): Emerald-only maps' zones and the rooms still to build
  # (data/emerald/hoenn_zones.json, hoenn_interiors.json), the labels carried over from Sapphire's, Emerald's plans
  # (data/plans/emerald) and its world (EWD); the exits, models, checks and the ROM below read EWD
  (cd converter && HOENN_VERSION=emerald python3 allocate_zones.py | tail -1 && HOENN_VERSION=emerald python3 allocate_interiors.py | head -1 && HOENN_VERSION=emerald python3 emerald_labels.py | tail -1 && for m in $(HOENN_VERSION=emerald python3 -c "import sys, os; sys.path.append('../b2tools'); import version; print(' '.join(version.load_json(os.path.join('..', 'data', 'hoenn_zones.json'))['maps']))"); do HOENN_VERSION=emerald python3 plan_map.py ../external/pokeruby $m > /dev/null; done)
  WD=$EWD; mkdir -p $(dirname $WD) && REPORT="$(cd $(dirname $WD) && pwd)/$(basename $WD).report.txt"
  export HOENN_WORLD_DIR=$(cd $(dirname $WD) && pwd)/$(basename $WD)
  (cd b2tools && HOENN_VERSION=emerald python3 world.py > $REPORT) && head -1 $REPORT
  # EMERALD-3 S0-1/S0-3 (emerald_integrate 2026-10-12, notes/EMERALD_STORY.md 2.4.1): pokeemerald's events of every map of
  # Emerald's world (data/sapphire/emerald), then its simple signs/people/item balls (src/field_scripts/emerald, src/text/
  # script/emerald, data/emerald/hoenn_content.json: Emerald's scene counts) and its trainer NPCs (data/emerald/
  # hoenn_trainer_npcs.json) on Emerald's zones, then Emerald's world.py once more to place them (as the shared block does)
  (cd converter && HOENN_VERSION=emerald python3 sapphire_data.py ../external/pokeemerald $(cd ../b2tools && HOENN_VERSION=emerald python3 -c "import world as W; cfg, lay = W.load(); _, _, m = W.compose(cfg, lay); n = list(m) + [x for _, _, fm, _ in W.standalone_frames(cfg) for x in fm]; print(' '.join(dict.fromkeys(x for x in n if x not in W.HAND_MADE_EVENTS)))") > /dev/null)
  (cd converter && HOENN_VERSION=emerald python3 gen_map_content.py | cut -c1-120 && HOENN_VERSION=emerald python3 gen_trainer_npcs.py | cut -c1-120)
  (cd b2tools && HOENN_VERSION=emerald python3 world.py > $REPORT) && head -1 $REPORT
  # Emerald's caves and dungeons (emerald_caves 2026-10-12, notes/EMERALD.md "Caves and dungeons"): the zone files of the
  # "emerald/<Map>" cave recipes (Emerald-only caves, Emerald variants with their own zone json), after Emerald's world.py
  # (their exits name its doors); the room-builder variants' recipes and zone jsons (b2tools/emerald_caves_rooms.py)
  (cd converter && HOENN_VERSION=emerald python3 gen_caves.py --emerald | grep -v "^  " | cut -c1-120)
  (cd b2tools && python3 emerald_caves_rooms.py | tail -2)
fi
# report: room exits that no longer lead to their outdoor door (rooms whose generator is not rerun here, or a world
# change); fix with the room's generator, or `python3 b2tools/check_exits.py --fix` for rooms made by hand
(HOENN_VERSION=$RV python3 b2tools/check_exits.py $HOENN_WORLD_DIR | head -40) || true
for d in $WD/cells/*/; do echo "${d}terrain.dae ${d}terrain.nsbmd"; done > $WD/batch.txt
java -Djava.awt.headless=true -cp "$CP" ToNsbmd --batch $WD/batch.txt $WD/palettes.txt > /dev/null
# report: outdoor glitch checks over the built world, every frame (the connected world, each warp-only group incl. the
# event islands when HOENN_STANDALONE builds them, the other layouts): b2tools/outdoor_check.py, notes/WORLD.md "Outdoor
# checks". Open findings are listed, by-design ones only counted. OUTDOOR_CHECK_KINDS=...,layer,view adds the slow
# geometry checks (layered surfaces, back faces, holes: ~10 min)
(HOENN_VERSION=$RV python3 b2tools/outdoor_check.py $HOENN_WORLD_DIR --kinds ${OUTDOOR_CHECK_KINDS:-place,size,walk,door,bld,zone,tex} | tail -40) || true
zsh b2tools/rebuild_interiors.sh > /dev/null    # interior rooms (notes/INTERIORS.md) for the interiors patch
(cd b2tools && HOENN_VERSION=$RV HOENN_BUILD_DIR=$ROMD python3 build_rom.py --clean test_door_to_nuvema hoenn_world area2_buildings text scripts encounters encounter_rules hoenn_season hoenn_textures sprites boulder_1x1 objects3d exp_share hm_free starters interiors opening hoenn_intro title zone_effects shops trade_evos centers trainers story weather standalone dive capture_demo trades fixed_weather game_clear boat_demos npc_check roamers fairy fairy_ui hoenn_dex pwt battle_tower town_map hoenn_music hoenn_pokedex sprite_switch trainer_card emerald_mech emerald_postgame frontier_core frontier_factory_dome frontier_pike rods frontier_palace_arena frontier_pyramid emerald_rayquaza_scene antipiracy | grep -E "nds|patch (hoenn_world|hoenn_dex|hoenn_pokedex|sprite_switch|trainer_card|emerald_mech|emerald_postgame|frontier_core|frontier_factory_dome|frontier_pike|rods|antipiracy)|pack 0")
# report (sweep_rooms 2026-10-07): every built room through b2tools/rooms_check.py (kinds a-l: stairs, furniture, people
# incl. story objects, scripted paths, warps both ways in the ROM, layers, camera, black slabs, textures in the ROM, room
# exits, floor under walkable tiles); the findings go to <world>.rooms_check.txt, the counts here
(cd b2tools && HOENN_VERSION=$RV python3 rooms_check.py --rom $ROMD/hoenn.nds --world $HOENN_WORLD_DIR > ${REPORT%.report.txt}.rooms_check.txt 2>&1;
 python3 -c "import sys,collections; c=collections.Counter(l.split('(')[1][0] for l in open(sys.argv[1]) if ': (' in l); print('rooms_check:', dict(sorted(c.items())), '->', sys.argv[1])" ${REPORT%.report.txt}.rooms_check.txt) || true
# report (sweep_caves 2026-10-07): every built cave and underwater map (a recipe in data/cave_layouts) through
# b2tools/caves_check.py (notes/CAVES.md "Cave checks": walkability vs Sapphire both ways, events vs floor heights,
# objects, ladders/ledges/ramps, chunk sizes, textures, darkness); the findings go to <world>.caves_check.txt, the counts
# here. CAVES_CHECK_KINDS=abcefhistwx adds the slow geometry checks (f layered surfaces, h holes seen from the camera)
(cd b2tools && python3 caves_check.py --kinds ${CAVES_CHECK_KINDS:-abceistwx} > ${REPORT%.report.txt}.caves_check.txt 2>&1;
 python3 -c "import sys,collections; c=collections.Counter(l.split(': (')[1][0] for l in open(sys.argv[1]) if ': (' in l); print('caves_check:', dict(sorted(c.items())), '->', sys.argv[1])" ${REPORT%.report.txt}.caves_check.txt) || true
# report (script_check 2026-10-08): the ROM's zone entities and field scripts on the built tiles (b2tools/script_check.py:
# people, signs, hidden items and triggers where they can be used, scripted warps and movement paths, message windows
# before movements and items, text and script ids, Black 2's leftover triggers in rooms); the findings go to
# <world>.script_check.txt, the counts here
(HOENN_VERSION=$RV python3 b2tools/script_check.py $ROMD/hoenn.nds --world $HOENN_WORLD_DIR --labels > ${REPORT%.report.txt}.script_check.txt 2>&1;
 tail -1 ${REPORT%.report.txt}.script_check.txt) || true
# report (walkability 2026-10-11): every map's walkable tiles against Sapphire's and blocked tiles that look open
# (b2tools/walk_diff.py: towns, routes, other outdoor maps, rooms, caves, Dive maps; open counts per family here, the
# findings in <world>.walk_diff.txt, intended differences with --all)
(HOENN_VERSION=$RV python3 b2tools/walk_diff.py --world $HOENN_WORLD_DIR --rom $ROMD/hoenn.nds > ${REPORT%.report.txt}.walk_diff.txt 2>&1;
 grep -A8 '^summary' ${REPORT%.report.txt}.walk_diff.txt) || true
rm -rf $ROMD/files $ROMD/code    # keep only the ROM (disk space; the next --clean build recreates them)
