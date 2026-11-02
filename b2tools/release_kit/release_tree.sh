#!/bin/zsh
# Create or check a release worktree (~/HoennB2_lead, ~/HoennB2_em), so a missing one is no blocker: the release scripts
# run this first. Usage: zsh release_tree.sh <path> <commit>
# A git worktree of the main repo, detached at <commit>, with links to main's git-ignored folders (.venv, external, roms,
# tools, backups: external/ holds the decomp's tree, its toolchain and build base, b2tools/decomp_build.py) and its own
# work/: rebuild_slice.sh makes the rest (buildings, world, rooms, java, ROMs), a first run in a new tree just
# takes as long as a full rebuild. Never removes anything.
set -e -o pipefail
T=$1; H=$2
[[ -n "$T" && -n "$H" ]] || { echo "usage: release_tree.sh <path> <commit>"; exit 1; }
MAIN=$HOME/Documents/GitHub/HoennB2
git -C $MAIN cat-file -e "$H^{commit}" || { echo "no commit $H"; exit 1; }
if [[ ! -e $T/.git ]]; then
  [[ -e $T ]] && { echo "$T exists but is no worktree: move it away first"; exit 1; }
  git -C $MAIN worktree prune
  git -C $MAIN worktree add --detach $T $H > /dev/null
  echo "release tree: created $T at $(git -C $T rev-parse --short HEAD)"
else
  echo "release tree: $T at $(git -C $T rev-parse --short HEAD)"
fi
for l in .venv external roms tools backups; do
  if [[ ! -e $T/$l ]]; then
    [[ -e $MAIN/$l ]] || { echo "main has no $l"; exit 1; }
    ln -s $MAIN/$l $T/$l; echo "release tree: linked $l"
  elif [[ ! -L $T/$l ]]; then
    echo "release tree: note: $T/$l is a real folder, not main's link"
  fi
done
mkdir -p $T/work
# inputs rebuild_slice doesn't make (extracted once from the dump): APFS clones of main's, in a tree that has none
for d in tex sprites models; do
  if [[ ! -e $T/work/$d ]]; then
    [[ -e $MAIN/work/$d ]] || { echo "main has no work/$d"; exit 1; }
    cp -cRp $MAIN/work/$d $T/work/$d; echo "release tree: cloned work/$d"
  fi
done
