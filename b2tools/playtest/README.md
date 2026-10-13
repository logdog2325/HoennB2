# Playtest tools (WIP, 2026-10-08)

The playthrough agent's emulator driver, saved when it was stopped to conserve usage: the input driver (pt.py), battle
bot (battle.py), ROM-collision router (planner.py / romdata.py), live text reader, the risk ranker over scripts
(risk.py), and the "talk to everything" crash tour (explore.py, recheck.py, report.py). Not part of any build. Paths
inside may still point at work/agents/playthrough/; adjust before reuse. Results so far: the early region and Routes
103-110 toured with no crash/hang/soft lock (notes/RESUME.md).

b2tools/progression_check.py (also WIP, from progression_check): the static story-logic solver, stopped mid-way
(the may-pass solver was next). Not in rebuild_slice.sh yet.
