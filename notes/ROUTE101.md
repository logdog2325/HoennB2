# Route 101 (milestone map 2) — status 2026-10-06

Replaces the southern cell of Route 1: zone 317, matrix 0 cell (24,22), chunk 3, area 2. Sapphire's 20 rows fill
chunk rows 12–31 (row 31 meets Littleroot); rows 0–11 repeat Sapphire's first two rows (path between trees) — the
12 extra rows decided on 2026-10-05. Built by `b2tools/rebuild_slice.sh` (also builds Littleroot).

| Feature | Status |
|---|---|
| Layout tile-for-tile: trees, tall grass, sandy patches, 3 ledges (incl. the bend), sign | done (`screenshots/route101/`) |
| Collision: tall grass (encounters), one-way ledges, route floor | done; ledges block from below, verified |
| Location banner "Route 101" when walking in from Littleroot | done |
| Wild encounters: Sapphire's 12 grass slots (Wurmple, Zigzagoon, Poochyena, Lv 2–3), slot order kept | done; wild Zigzagoon Lv 3 met in-game |
| Encounter **rate** | Black 2's own early-route value (1); Sapphire's 20 can't be converted until the rate code is understood |
| NPCs: youngster (look-around, sprite 10), boy (walks left/right, sprite 12) with Sapphire text | done |
| Sign "Route 101 / ↑ Oldale Town" | done |
| Story: Prof. Birch chased by Poochyena, Birch's bag, starter choice | not yet (planned with the starter sequence) |

Model 42.9 KB. Seasonal swaps for chunks 3/4 disabled (`no_season_swaps`).
