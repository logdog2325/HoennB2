# Metatile label vocabulary (converter/metatiles.json and data/labels/*.json)

One class per Sapphire metatile, describing what the Gen 5 builder must make on that tile. Pick the closest class;
if none fits, use `other:<short description>` — never force a tile into a wrong class. When a tile mixes two things
(e.g. grass with the tip of a tree from the row below), label what stands *on* the tile in-game (that example is
`tree_tip`).

Facts on the sheets: `beh` = pokeruby metatile behaviour byte (include/constants/metatile_behaviors.h in pokeruby,
e.g. 0x02 tall grass, 0x10–0x17 water types, 0x38–0x3F ledge jumps E/W/N/S/NE/NW/SE/SW), `col` = collision bits
seen in maps (0 walkable, 1+ blocked), `n` = uses in outdoor maps, example map/position (render the map with
`converter/render.py` or `render_labels.py` to see context).

## Ground (walkable)
| Class | Meaning |
|---|---|
| `grass` | plain short grass |
| `flowers` | flower patch (decoration on grass) |
| `path` | pale path / dirt / town paving, incl. its grass-border edge pieces |
| `sand` | beach or desert sand |
| `sand_patch` | small isolated sand spot (under doors) |
| `ash_grass` | ash-covered grass (Route 113 area) |
| `tall_grass` | tall grass (wild encounters, beh 0x02) |
| `long_grass` | very tall grass (Route 119/120, beh 0x03) |
| `puddle` | shallow water you walk through |
| `mud` / `ice` / `cracked_floor` | special floors if they appear outdoors |
| `bridge` | walkable bridge or pier deck (over water or a gap) |
| `stairs` | steps between height levels |

## Trees and plants
| Class | Meaning |
|---|---|
| `tree_top_l`, `tree_top_r` | top half of a 2×2 tree, left/right |
| `tree_bot` | bottom half (trunk) of a tree |
| `tree_tip` | walkable tile with the tip of the tree below drawn on it |
| `cut_tree` | small tree removable with Cut |
| `bush` | other solid plant / hedge |

## Height and rock
| Class | Meaning |
|---|---|
| `ledge_s`, `ledge_e`, `ledge_w`, `ledge_n` | one-way ledge, jump direction (diagonal ledges: pick the main direction) |
| `ledge_cap` | solid end/corner of a ledge |
| `cliff` | rock or earth wall between height levels (solid) |
| `cliff_top` | walkable top edge of a cliff (drawn with the cliff lip) |
| `rock` | solid boulder/rock decoration (not a Strength/Rock Smash object; those are NPC-like events) |
| `cave_entrance` | opening in a cliff/mountain that has a warp |
| `mountain` | large mountain/volcano scenery that is not walkable |

## Water
| Class | Meaning |
|---|---|
| `water` | surfable water |
| `water_edge` | shoreline piece: land/sand with water drawn on it (say which side is water in a note if useful) |
| `deep_water` | dark water where Dive is used |
| `waterfall` | waterfall (Waterfall HM) |
| `current_e`, `current_w`, `current_n`, `current_s` | water current pushing the player |
| `seaweed` | underwater weed |

## Built things
| Class | Meaning |
|---|---|
| `building` | any part of a building's walls/front (collision handled by the plan) |
| `building_roof` | roof parts, incl. walk-behind roof rows |
| `door` | the door tile itself |
| `sign` | signpost / notice board |
| `fence` | fence or railing (solid) |
| `wall` | town wall, stone wall (solid) |
| `prop` | other solid object: mailbox, bin, crate, lamp, statue, machine… (add a note) |
| `bike_path` | Cycling Road surface |

## Output format (data/labels/<tileset>.json)
```json
{"_notes": {"0a3": "why unsure / what it is"},
 "gTileset_Mauville": {"0a3": "path", "0a4": "building"}}
```
Every id on the tileset's sheets must get a class. Put doubts in `_notes` (keyed by id), not in the class.
