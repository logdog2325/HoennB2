#!/bin/zsh
# Test build for a story agent (notes/STORY_PORTING.md): the lead's overworld (work/world) and rooms (work/interiors)
# are only read; the ROM goes to work/agents/$HOENN_AGENT/rom/hoenn.nds. Same patch list as b2tools/rebuild_slice.sh
# (the v12 list: same layout as work/emu's savestates); it includes the story patches: `trainers` (Sapphire's
# trainers + trainer NPCs, converter/gen_trainers.py and gen_trainer_npcs.py) and `story` (story NPCs/triggers of data/story/*.json).
#   HOENN_AGENT=ch1 zsh b2tools/story_build.sh                 (add GEN=1 to rerun converter/gen_map_content.py first,
#                                                                 after changing a scene file of an outdoor map)
# Test switches (env, see notes/TESTING.md): HOENN_TEST_PARTY=1, HOENN_TEST_WARP=zone,x,z, HOENN_TEST_NO_WILD=1,
# HOENN_TEST_TRAINER=TRAINER_X, HOENN_TEST_MOVES=1, HOENN_TRAINERS_FIT=1 (keeps a/0/9/2 at Black 2's size until
# build_rom.py has RESERVE[92]; needed for the lead's savestates).
# Version (notes/RUBY.md "WP0 layout"): HOENN_VERSION=ruby builds the Ruby ROM from the same world into
# work/agents/$HOENN_AGENT/rom_ruby/hoenn.nds (the agent's Sapphire ROM in rom/ is left alone); unset = Sapphire.
# HOENN_VERSION=emerald (notes/EMERALD.md): rom_emerald/, on the lead's Emerald world work/world_emerald (HOENN_WORLD_DIR
# wins), built from pokeemerald's maps since emerald_world (notes/EMERALD.md "Emerald's world"); while it is not built,
# work/world with a warning (Sapphire's maps).
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
: ${HOENN_AGENT:?set HOENN_AGENT to your agent name}
python3 b2tools/version.py > /dev/null      # stops on a wrong HOENN_VERSION
A=$PWD/work/agents/$HOENN_AGENT
R=rom; [[ "${HOENN_VERSION:l}" == ruby ]] && R=rom_ruby
[[ "${HOENN_VERSION:l}" == emerald ]] && R=rom_emerald
if [[ "${HOENN_VERSION:l}" == emerald && -z "$HOENN_WORLD_DIR" ]]; then
  export HOENN_WORLD_DIR=$PWD/work/world_emerald
  [[ -d $HOENN_WORLD_DIR ]] || { export HOENN_WORLD_DIR=$PWD/work/world; echo "WARNING: no work/world_emerald yet: this Emerald ROM has Sapphire's maps"; }
fi
export HOENN_BUILD_DIR=$A/$R HOENN_INTERIORS_DIR=${HOENN_INTERIORS_DIR:-$PWD/work/interiors}
mkdir -p $A
[[ -n "$GEN" ]] && (cd converter && HOENN_VERSION= nice python3 gen_map_content.py | cut -c1-160)   # shared (Sapphire) files
[[ -n "$GEN" && "${HOENN_VERSION:l}" == ruby ]] && (cd converter && nice python3 gen_ruby_text.py | sed -n '2p;$p')   # Ruby's text twins of them
(cd b2tools && nice python3 build_rom.py --clean test_door_to_nuvema hoenn_world area2_buildings text scripts encounters \
  encounter_rules hoenn_season hoenn_textures sprites boulder_1x1 objects3d exp_share hm_free starters interiors opening hoenn_intro title \
  zone_effects shops trade_evos centers trainers story weather standalone dive capture_demo trades fixed_weather game_clear boat_demos npc_check roamers fairy fairy_ui hoenn_dex pwt battle_tower town_map hoenn_music hoenn_pokedex sprite_switch trainer_card emerald_mech emerald_postgame frontier_core frontier_factory_dome frontier_pike rods frontier_palace_arena frontier_pyramid emerald_rayquaza_scene antipiracy | grep -E "nds|rror|pack 0|patch (trainers|story|hoenn_dex|hoenn_pokedex|sprite_switch|trainer_card|emerald_mech|emerald_postgame|frontier_core|frontier_factory_dome|frontier_pike|rods|emerald_rayquaza_scene|antipiracy)" | cut -c1-400)
rm -rf $HOENN_BUILD_DIR/files $HOENN_BUILD_DIR/code     # keep only the ROM (disk space)
