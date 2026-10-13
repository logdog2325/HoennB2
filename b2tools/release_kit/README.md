# Release kit (lead, 2026-10-10)

Copies of the scripts that built and tested v16.1-v16.3 (they lived in a session scratchpad). Before use, replace the
version: `sed -e 's/16\.3/16.4/g; s/v163/v164/g' release_vNN.sh > /tmp/r.sh` (same for smoke_vNN.sh).

- `release_vNN.sh <commit>`: builds Sapphire and Ruby in the lead worktree ~/HoennB2_lead (detached at the commit),
  runs the checkers and rom_layout_diff (must print LAYOUT IDENTICAL), writes release/Pokemon_<V>_NDS_vNN.{nds,bps}
  (bps.py verifies each patch by applying it) and copies them to ~/Desktop/release.
- `smoke_vNN.sh`: new game with both sets of Birch's choices (A2: Fairy on, modern split, Hoenn music, NEW sprites; B2:
  Fairy off, classic split, Unova music, CLASSIC sprites) through starter, Pokédex, catch, Center heal, wall map, evolution (setmon EXP must be just
  under the NEXT level of the lead's stored level), save/Continue; Ruby to the starter. Uses freeze_fix's driver in
  work/agents/freeze_fix/tests/pt (copy lose.py there) and the kit's `mk_boot.py` for the intro.
- `mk_boot.py ROM OUTDIR yes|no yes|no hoenn|unova [classic|new]`: cold boot, Birch's four questions answered (Fairy,
  modern split, music, sprite style), truck and house states; prints the options u16 (bits 11-14).
- `lose.py`: the forced loss (party Lv1, 1 HP; return index set in RAM; cases rustboro, rustboro_old_key0(_sailed),
  rustboro_key0(_sailed), briney, rescue, sailed). Every release test includes a forced loss.
- `pokebw2_submit_pr.sh BRANCH`: pokebw2 PR helper (one commit ahead, no-reply author, clean merge; ask the user first).
