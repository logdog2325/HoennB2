#!/bin/zsh
# Emerald release build in the clean worktree ~/HoennB2_em (main's own tree may hold helpers' unfinished files):
# moves it to <commit>, full rebuild_slice with HOENN_VERSION=emerald, its checks, .bps (verified), release/ + Desktop.
# Usage: zsh release_emerald.sh <main commit> <version, e.g. 1.4>
set -e -o pipefail
H=$1; V=$2; [[ -n "$H" && -n "$V" ]] || { echo "usage: release_emerald.sh <commit> <version>"; exit 1; }
LOG=${RELEASE_LOG_DIR:-$HOME/Documents/GitHub/HoennB2/work/release_logs}; mkdir -p $LOG
REL=$HOME/Documents/GitHub/HoennB2/release
zsh ${0:A:h}/release_tree.sh $HOME/HoennB2_em $H      # creates or checks the worktree and its links
cd ~/HoennB2_em
git checkout -q -- b2tools/rebuild_slice.sh b2tools/rebuild_interiors.sh
git status --short | grep -v '^??' && { echo "worktree not clean"; exit 1; } || true
git checkout -q --detach $H
/usr/bin/sed -i '' "s|^cd ~/Documents/GitHub/HoennB2 \&\& source env.sh|cd $HOME/HoennB2_em \\&\\& source env.sh|" b2tools/rebuild_slice.sh b2tools/rebuild_interiors.sh
git log --oneline -1
# Black 2's code (notes/POKEBW2_UPGRADE.md 8.8): built from the decomp's C (HOENN_CODE=source, the default from Phase 1
# on) = decomp_changes/UPSTREAM + decomp_changes/hoennb2_decomp.patch of THIS commit, checked here; build_rom.py runs the
# decomp's ninja itself. HOENN_CODE=base zsh <this script> ... = the old way (the dump's binaries + binary patches).
# The tree's external/ is main's (a link), so the decomp tree is main's external/pokebw2_new unless HOENN_DECOMP names
# one made for this release (python3 b2tools/decomp_build.py setup DIR).
if [[ -f b2tools/decomp_build.py && "${HOENN_CODE:-source}" == source ]]; then
  python3 b2tools/decomp_build.py verify || { echo "the decomp tree is not this commit's decomp_changes/ (notes/POKEBW2_UPGRADE.md 8.8)"; exit 1; }
fi
echo "code: ${HOENN_CODE:-source}${HOENN_DECOMP:+ (decomp $HOENN_DECOMP)}"
echo "== Emerald"; HOENN_VERSION=emerald nice zsh b2tools/rebuild_slice.sh > $LOG/v${V}_emerald.log 2>&1
grep -E "^decomp |save keeps|hoenn.nds|summary \(open\)|_check:|script_check|chunk_fit|rror" $LOG/v${V}_emerald.log | cut -c1-220 | tail -40 || true
cp -c work/rom_emerald/hoenn.nds $REL/Pokemon_Emerald_NDS_v$V.nds
(cd b2tools && ../.venv/bin/python bps.py make ../roms/black2_original.nds ../work/rom_emerald/hoenn.nds $REL/Pokemon_Emerald_NDS_v$V.bps)
shasum $REL/Pokemon_Emerald_NDS_v$V.nds
mkdir -p ~/Desktop/release && cp -c $REL/Pokemon_Emerald_NDS_v$V.nds $REL/Pokemon_Emerald_NDS_v$V.bps ~/Desktop/release/
df -h / | tail -1
