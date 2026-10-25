#!/bin/zsh
# Publish a Sapphire/Ruby + Emerald release (ask the user first): download repo README/docs commit + push (no AI
# trailer), GitHub release with the three .bps and release/v<SR>_notes.md (marked latest), private tags.
# Usage: zsh publish.sh <SR version> <Emerald version> <lead commit> <main commit>
set -e -o pipefail
SR=$1; EM=$2; LC=$3; MC=$4; [[ -n "$MC" ]] || { echo "usage: publish.sh <SR> <EM> <lead commit> <main commit>"; exit 1; }
R=$HOME/Documents/GitHub/HoennB2/release
for f in Pokemon_Sapphire_NDS_v$SR.bps Pokemon_Ruby_NDS_v$SR.bps Pokemon_Emerald_NDS_v$EM.bps v${SR}_notes.md; do [[ -s $R/$f ]] || { echo "missing $f"; exit 1; }; done
python3 $HOME/Documents/GitHub/HoennB2/b2tools/gen_docs.py $HOME/Documents/GitHub/pokemon-ruby-sapphire-nds/docs | tail -1
cd $HOME/Documents/GitHub/pokemon-ruby-sapphire-nds
grep -rIl -i -E 'gmail\.com|/Use[r]s/' README.md docs && { echo "STOP: personal details"; exit 1; } || true
git add README.md docs
git diff --cached --quiet || git commit -q -m "v$SR / Emerald v$EM: download names, player guide, credits"
git push -q origin HEAD
gh release create v$SR $R/Pokemon_Sapphire_NDS_v$SR.bps $R/Pokemon_Ruby_NDS_v$SR.bps $R/Pokemon_Emerald_NDS_v$EM.bps \
  --title "Pokémon Ruby & Sapphire NDS v$SR + Emerald NDS v$EM" --notes-file $R/v${SR}_notes.md --latest 2>&1 | tail -2
gh release view v$SR --json assets --jq '.assets[] | "\(.name) \(.size)"'
git -C $HOME/HoennB2_lead tag -f v$SR $LC > /dev/null
git -C $HOME/Documents/GitHub/HoennB2 tag -f emerald-v$EM $MC > /dev/null
echo published
