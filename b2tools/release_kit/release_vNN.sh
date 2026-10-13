#!/bin/zsh
# v16 release: Sapphire + Ruby from HEAD in the lead worktree (~/HoennB2_lead), states, .bps, release/ files.
# Usage: zsh release_v152.sh <commit>
set -e -o pipefail
H=$1
S=${0:a:h}
REL=$HOME/Documents/GitHub/HoennB2/release
cd ~/HoennB2_lead
git checkout -q -- b2tools/rebuild_slice.sh b2tools/rebuild_interiors.sh
git status --short | grep -v '^??' && { echo "lead worktree not clean"; exit 1; } || true
git checkout -q --detach $H
sed -i '' 's|^cd ~/Documents/GitHub/HoennB2 && source env.sh|cd $HOME/HoennB2_lead \&\& source env.sh|' b2tools/rebuild_slice.sh b2tools/rebuild_interiors.sh
git log --oneline -1
export HOENN_WORLD_DIR=$HOME/Documents/GitHub/HoennB2/work/world
echo "== Sapphire"; nice zsh b2tools/rebuild_slice.sh > $S/v163_sapphire.log 2>&1
grep -E "save keeps|hoenn.nds|summary \(open\)|_check:|script_check" $S/v163_sapphire.log | cut -c1-220 || true
echo "== Ruby"; HOENN_VERSION=ruby nice zsh b2tools/rebuild_slice.sh > $S/v163_ruby.log 2>&1
grep -E "save keeps|hoenn.nds|summary \(open\)|_check:|script_check" $S/v163_ruby.log | cut -c1-220 || true
(cd b2tools && python3 rom_layout_diff.py ../work/rom/hoenn.nds ../work/rom_ruby/hoenn.nds | tail -3) || true
echo "== release files"
cp -c work/rom/hoenn.nds $REL/Pokemon_Sapphire_NDS_v16.3.nds
cp -c work/rom_ruby/hoenn.nds $REL/Pokemon_Ruby_NDS_v16.3.nds
(cd b2tools && ../.venv/bin/python bps.py make ../roms/black2_original.nds ../work/rom/hoenn.nds $REL/Pokemon_Sapphire_NDS_v16.3.bps)
(cd b2tools && ../.venv/bin/python bps.py make ../roms/black2_original.nds ../work/rom_ruby/hoenn.nds $REL/Pokemon_Ruby_NDS_v16.3.bps)
shasum $REL/Pokemon_*_v16.3.nds
df -h / | tail -1
for f in Pokemon_Sapphire_NDS_v16.3.nds Pokemon_Sapphire_NDS_v16.3.bps Pokemon_Ruby_NDS_v16.3.nds Pokemon_Ruby_NDS_v16.3.bps; do cp -c $REL/$f ~/Desktop/release/$f; done
echo "copied to Desktop"
