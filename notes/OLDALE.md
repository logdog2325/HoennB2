# Oldale Town (milestone map 3) — status 2026-10-06

Replaces Route 1's northern cell: matrix 0 cell (24,21), chunk 4. The cell's zone becomes 397 (Accumula's zone:
Pokémon Center and house interiors). The old Accumula cell (24,20, chunk 5) is forest until Route 103 exists.
Sapphire's rows fill chunk rows 12–31; rows 0–11 repeat its first two rows (the path north to Route 103).

| Feature | Status |
|---|---|
| Layout tile-for-tile: paths, flowers, trees, sign, 4 building footprints | done (`screenshots/oldale/`) |
| Pokémon Center and Poké Mart in Gen 3 shapes (rounded red/blue roof, Poké Ball crest, white walls, glass), Black 2 textures and Black 2's sliding door | done (`b2tools/models_oldale.py`) |
| Oldale houses (orange ribbed roof, beige siding) | done |
| Doors: Center → 398 (Black 2 Pokémon Center: nurse + shop counter), houses → 401/403, Mart → 399 (stand-in house) | done; Center entry verified |
| Location banner "Oldale Town" walking in from Route 101 | done |
| Signs: town sign, Pokémon Center and Mart wall signs (Sapphire text) | done |
| NPCs: girl, footprints man, Mart employee (Potion line) at Sapphire tiles, facing as in Sapphire | done |
| Rival, Mart employee's walk to the Mart and Potion gift (story) | not yet |
| Exits west (Route 102) and north (Route 103) | lead into forest until those routes exist |

Building placement rule learned here: put the front wall 4 units into the door tile (as Black 2 does); with the
front at the tile's south edge, Black 2's 10-unit-deep Pokémon Center door covers the player standing in front.
