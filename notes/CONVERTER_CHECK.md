# Converter check (2026-10-05)

`converter/render.py` draws each Sapphire map from pokeruby (left) next to the converter's class letters (right).
Images: `screenshots/sapphire/{LittlerootTown,Route101,OldaleTown}.png`. Checked by eye against those.

## What the converter is (and isn't)
- It only reads **pokeruby** (Sapphire) data and writes `hoenn_slice.json`: a letter grid, building boxes, NPC/warp/sign
  positions. Nothing in it reads or writes any **Black 2** format. Turning its output into Gen 5 map data is new work.
- Tall grass (`T`), ledges (`L`), water (`W`) and sand (`S`) come from the metatile **behavior** byte, so they're reliable.
- Path, flower, tree and building are guessed from **pixel colours** plus the collision bit, so they're not.

## Errors found in the three milestone maps
1. **Top row of every roof is wrong.** That row has no collision on the GBA (you walk "behind" it), so it falls to the
   colour rules: house roofs become `P` (path), the Pokémon Center's red roof becomes `F` (flowers). Every building
   footprint is therefore one row too short.
2. **Ledge direction is dropped.** Behaviors 0x38–0x3B are four different jump directions; the converter writes `L` for all.
   Route 101's ledges are all one-way, so direction matters.
3. **Ledge bend tiles become `B`** (prop) on Route 101 (the corner where the ledge turns north), because they have
   collision but a non-ledge behavior.
4. **Signs and mailboxes are `B`** like buildings; Center/Mart signs next to the door merge into the building footprint.
   Signs are only split back out later using the map's `bg_events`, mailboxes aren't.
5. `X` means both "tree" and "outside the map" (padding), so trees at the map edge can't be told from the border.
6. The three maps are hard-coded and stitched into one grid with fake padding, so per-map coordinates are offset.

## Plan to fix (before building from it)
- Classify by **metatile ID** per tileset (a small hand-checked table: which metatiles are roof, wall, door, tree, sign,
  mailbox, flower, ledge-corner) instead of colours, with colours only as a fallback that gets flagged for review.
- Keep ledge direction; keep per-map output (no stitching); separate "border" from "tree".
- Every converted map gets a side-by-side image like these, checked before it's used.
