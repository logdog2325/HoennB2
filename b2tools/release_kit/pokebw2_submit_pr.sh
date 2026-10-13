#!/bin/zsh
# submit_pr.sh BRANCH [extra line]: check, push to the fork and open a pokebw2 PR from the branch's commit message
set -e
S=${0:a:h}; b=$1; X=${2:-'`ninja` passes with both ROMs matching.'}
cd ~/Documents/GitHub/pokebw2 && git fetch -q origin
[ "$(git log -1 --format=%ae $b)" = "226450061+logdog2325@users.noreply.github.com" ] || { echo "bad author"; exit 1; }
[ "$(git rev-list --count origin/main..$b)" = 1 ] || { echo "not one commit ahead"; exit 1; }
git merge-tree --write-tree origin/main $b >/dev/null || { echo CONFLICT; exit 1; }
{ git log -1 --format='%b' $b | sed '/^Co-Authored-By:/d' | sed -e :a -e '/^\n*$/{$d;N;ba' -e '}'; printf '\n%s\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n' "$X"; } > $S/pr_$b.md
git push -q fork $b 2>&1 | grep -v "^remote:" || true
gh pr create -R fuddlesworth/pokebw2 --base main --head logdog2325:$b --title "$(git log -1 --format=%s $b)" --body-file $S/pr_$b.md 2>&1 | tail -1
