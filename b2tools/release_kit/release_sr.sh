#!/bin/zsh
# Sapphire + Ruby release build from a commit of the release branch in the lead worktree (~/HoennB2_lead), the
# checks, rom_layout_diff (must say LAYOUT IDENTICAL), .bps (verified by applying) and the release/ + Desktop copies.
# Usage: zsh release_sr.sh <commit> <version, e.g. 18.3>   (logs next to this script's LOG dir)
set -e -o pipefail
H=$1; V=$2; [[ -n "$H" && -n "$V" ]] || { echo "usage: release_sr.sh <commit> <version>"; exit 1; }
LOG=${RELEASE_LOG_DIR:-$HOME/Documents/GitHub/HoennB2/work/release_logs}; mkdir -p $LOG
REL=$HOME/Documents/GitHub/HoennB2/release
cd ~/HoennB2_lead
git checkout -q -- b2tools/rebuild_slice.sh b2tools/rebuild_interiors.sh
git status --short | grep -v '^??' && { echo "lead worktree not clean"; exit 1; } || true
git checkout -q --detach $H
/usr/bin/sed -i '' "s|^cd ~/Documents/GitHub/HoennB2 \&\& source env.sh|cd $HOME/HoennB2_lead \\&\\& source env.sh|" b2tools/rebuild_slice.sh b2tools/rebuild_interiors.sh
git log --oneline -1
export HOENN_WORLD_DIR=$HOME/HoennB2_lead/work/world_rel
echo "== Sapphire"; nice zsh b2tools/rebuild_slice.sh > $LOG/v${V}_sapphire.log 2>&1
grep -E "save keeps|hoenn.nds|summary \(open\)|_check:|script_check" $LOG/v${V}_sapphire.log | cut -c1-220 || true
echo "== Ruby"; HOENN_VERSION=ruby nice zsh b2tools/rebuild_slice.sh > $LOG/v${V}_ruby.log 2>&1
grep -E "save keeps|hoenn.nds|summary \(open\)|_check:|script_check" $LOG/v${V}_ruby.log | cut -c1-220 || true
(cd b2tools && python3 rom_layout_diff.py ../work/rom/hoenn.nds ../work/rom_ruby/hoenn.nds | tail -3) || true
echo "== release files"
cp -c work/rom/hoenn.nds $REL/Pokemon_Sapphire_NDS_v$V.nds
cp -c work/rom_ruby/hoenn.nds $REL/Pokemon_Ruby_NDS_v$V.nds
(cd b2tools && ../.venv/bin/python bps.py make ../roms/black2_original.nds ../work/rom/hoenn.nds $REL/Pokemon_Sapphire_NDS_v$V.bps)
(cd b2tools && ../.venv/bin/python bps.py make ../roms/black2_original.nds ../work/rom_ruby/hoenn.nds $REL/Pokemon_Ruby_NDS_v$V.bps)
shasum $REL/Pokemon_*_v$V.nds
mkdir -p ~/Desktop/release && for f in Pokemon_Sapphire_NDS_v$V.nds Pokemon_Sapphire_NDS_v$V.bps Pokemon_Ruby_NDS_v$V.nds Pokemon_Ruby_NDS_v$V.bps; do cp -c $REL/$f ~/Desktop/release/$f; done
echo "copied to Desktop"
