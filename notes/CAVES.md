# Caves (O5) — the cave builder (cave_builder agent, 2026-10-06)

Sapphire's underground maps rebuilt as Black 2 cave chunks the way Black 2 builds its own caves (Wellspring Cave,
Relic Passage, Seaside Cave, Victory Road, Reversal Mountain), with Black 2's own textures and models only.
Tags: **[code]** read in the decomp/disassembly, **[bytes]** measured in the user's dump, **[test]** seen in DeSmuME.

## Pipeline

    data/cave_layouts/<Map>.json  (recipe, often just {"map": "<Map>"})
      + data/cave_layouts/_looks.json (Black 2 cave looks) + data/cave_tiles.json (per Sapphire tileset)
      --b2tools/models_cave.py-->  $HOENN_INTERIORS_DIR/<Map>/  terrain.dae (+ terrain_c<k>.dae for multi-chunk caves),
                                   collision*.per, placements*.bin, room.json, palettes.txt, texture PNGs
    converter/gen_caves.py [Map ...]  (after world.py: reads world.json's outdoor doors)
      -->  data/interiors/<zone>.json       room, area, header, warps (Sapphire's order), step triggers, items,
                                            boulders, rocks, simple people/signs, "dark", "cave": true
           src/field_scripts/<s>_room_<Map>.s   ladder / cracked-floor step scripts (+ simple people/signs)
           src/encounters/<f>_cave_<Map>.s      Sapphire's wild table (converter/gen_encounters.py's rules)
    zsh b2tools/rebuild_interiors.sh [Map ...]   builds caves (a recipe in data/cave_layouts) with models_cave.py and
                                                 rooms with models_interior.py; ToNsbmd --vcol
    build patch `interiors` (b2tools/patches/interiors.py) installs a cave like any room (one chunk per matrix cell).

- `python3 b2tools/models_cave.py --preview <Map>` renders the built cave (whole map + a view at every warp).
- The lead's `rebuild_slice.sh` runs `gen_caves.py` after `gen_interiors.py`; `rebuild_interiors.sh` with no names
  builds every cave too. Caves an agent's interiors copy lacks are left out by the interiors patch (other agents'
  builds keep working).
- Cave agents: `HOENN_AGENT=<you> zsh b2tools/agent_build_caves.sh <Map> ...` (own world with the cave doors, the
  named caves' zone files, the caves, a ROM with the full patch list; `NOWORLD=1` reuses your world).
- Every status-cave map with a Sapphire wild table already has its encounter file in data/hoenn_encounters.json
  (`gen_caves.py --allocate`, done for all 45), so parallel runs never allocate.

## Recipe (data/cave_layouts/<Map>.json, every key optional except "map")
| key | meaning |
|---|---|
| `map` | the pokeruby map |
| `look` | a look of _looks.json (default by the secondary tileset: `_by_tileset`) |
| `origin` | zone tile of Sapphire tile (0,0) (default [0,0]); `matrix` [w,h] chunks (default: what the map needs) |
| `tiers` | rock tiers (default the look's: 2 = 32 units high) |
| `levels` | {"<Sapphire elevation>": height} for walkable tiles, e.g. {"3": 0, "4": 16}; without it everything is at 0 |
| `tiles` | {"x,y": kind}: floor, rock, boulder, ledge_e/w/n/s, ramp_n/s/e/w (a 16-unit slope tile rising that way) |
| `ladders` | {"x,y": "up"/"down"} (default: data/cave_tiles.json ladder art, else the floor numbers in the map names) |
| `decals` | false: no floor decals; `boulder_models` false: Sapphire boulder tiles stay rock |

Recipes only correct what Sapphire's data can't say. Everything else comes from the map: walkability (collision
bits), elevations, behaviours, metatile ids (data/cave_tiles.json: which blocked metatiles are loose boulders; ladder
art up/down), warp/object/bg/coord events, `requires_flash`, the music section, the wild table.

## What the builder makes (Cave.classify, models_cave.py)
| Sapphire | Black 2 cave | Evidence |
|---|---|---|
| walkable tile | floor (look `floor`, 64 units per repeat), collision `0000 h 000A 0084` (0x80 without encounters) | Wellspring chunk 486: 0x0a/0x84 walkable, flags bit 2 = wild encounters (ov036 FieldEncount_DecideTypeByTerrain) **[bytes][code]** |
| blocked tile | rock: tiers of a 16-unit face (profile 0/4/14/16 high at 0/6/10/16 units from the floor edge, bands face_low/face_mid/lip, 32 units per u, vertex colour edge→1.0→edge) and a 16-unit flat top, then a rim (`rim`, `rim_depth` units) and black. Collision `01/81` | traced: Wellspring 486/488, Seaside 630-632, Victory Road 788 (d0); Reversal Mountain 719 west wall of the y16 room (in81) **[bytes]** |
| boulder metatile next to floor (cave_tiles.json) | d0: building models drock02 (1 tile) / drock01 (2x2 squares) from the area's pack (max 32 per chunk); in81: terrain quads copied from chunk 723 (`rock_sprites`) | Black 2 scatters drock models in Wellspring; Reversal Mountain draws in81_drock1 quads (+ in81_drock2 shadow) **[bytes]** |
| arrow warp (0x62-0x65) / door (0x60) | Black 2's cave arch copied triangle for triangle (`arch`, or `arch_s/n/e/w` per wall), outside version when the warp leads outdoors; the arch tile is solid and holds a type-4 warp walked into (dir 1 S, 2 N, 3 E, 4 W) | Victory Road 788 warp (13,30) type 4 dir 1; Reversal Mtn 738 (25,27) dir 1, 740 (8,2) dir 2, 723 (4,9) dir 4 **[bytes]**; arriving through a type-4 warp walks you one step out **[test]** |
| ladder (0x61) | down: a 1-tile pit with stairs; up: stairs climbing into a notch of the rock face; the tile stays walkable, a step trigger (var 0) runs `MapChangeCore zone, x, y, z, 1` to Sapphire's destination tile; a dir-0 type-2 warp on the tile is the arrival spot | Lavaridge Gym pattern (gyms_league) **[test]**; MapChangeCore args: x/y/z each `<< 16` (tiles, 16-unit levels, tiles), s00C4_MapChangeCore ov036 0x021a80dc **[code]** |
| cracked floor 0xD2 / hole 0x66 | rubble decal (`cracked`: d29_gake3 pebbles from the same set) 2 units above the floor; a step trigger drops you to Sapphire's hole-warp map (`setholewarp`) at the same x,y unless on the bike (`PlayerGetExState` = 1) | Sapphire field_tasks.c cracked floor callback; Granite B1F (2,1) -> B2F **[test]** |
| jump tiles 0x38-0x3B with floor on both sides | Black 2's ledge ridge d0dan_001 + classes 0x72-0x75 flags 1 | Wellspring 486 row 7 (0x74) **[bytes]** |
| muddy slope 0xD0 | the top tile of each run is a south ledge (one way down, as without the Mach Bike) | Sapphire behaviour |
| one-sided walls 0x30-0x37 | a low ridge + classes 0x51-0x58 | heights.py WALL_CLASS (ov036 TileExitBlockCheck_*) |
| elevation-0 stair runs between two `levels` | slope tiles (look `stairs`, plane records from heights.py: 8/16/32 units per tile; 16 over 3 tiles = 8, 8, landing); flags 0x84 where Sapphire's tile has the encounter attribute, else 0x80 (wild_tables 2026-10-08: Black 2's own sloped 0x0a cells carry 0x84 too, e.g. Reversal Mountain's chunk 723, zone 539) | Accumula/Route 19/20 stairs (TERRAIN_HEIGHTS.md) **[bytes]**; heights checked offline with ov036's tables |
| walkable neighbours on two levels Sapphire keeps apart | a rock face between them; side walls (0x51-0x58) when < 20 units apart (actors step < 20) | field_actor_tool.c ActorRouteCollCheckCore **[code]** |
| surfable water (pokeruby sTileBitAttributes bit 1) | Wellspring's cave water: opaque `water` (d0_miz) at shore-8, sparkle `water_top` (d0_miz2) 4 above, banks `water_bank`; collision 0x3f/0x16 (0x12 without encounters), waterfall 0x40/0x13; each pool takes its nearest shore's level | Wellspring 486/487: 0x3f/0x16 at y-8, d0_miz -8, d0_miz2 -4, d0mizu_gake 0..-4 **[bytes]**; 0x3f surfing **[test]** on the overworld (TERRAIN_WATER.md), **not yet in a cave** |
| item balls / Strength boulders / Rock Smash rocks | global item scripts (data/hoenn_items.json), model 8197 + script 10000, rock model + script 10016 (hm_free) | |
| simple people/signs | one-message scripts with Sapphire's text (gen_interiors' npc_block/sign_block) | |
| `requires_flash` | "dark": true -> zone_effects.py writes (zone, 1) into a/1/4/9 | Granite B1F dark on a cold boot **[test]** (the table is read at boot: savestates show it lit) |
| warps / triggers / signs on a raised level | their y = the tile's height (room.json warp_spots "y", zone json "y") | events fire within 2 units of their y (TERRAIN_HEIGHTS.md) **[code]** |

Zone header (gen_caves): the look's Black 2 cave header (`header_zone`: Wellspring 324 / dark 325, Reversal
Mountain 539: music, weather, battle background, icon), map type 16 (interior: every chunk of the matrix loaded),
Sapphire's place name, the encounter file. Effect 3 (cave): entering from outdoors is a black fade, leaving fades to
white (ov036 transition tables 0x021d1634/0x021d16c4 [from][to]: 0->3 out 4/in 0, 3->0 out 1/in 1) **[bytes][test]**.
Black 2's place banner shows the season in its corner on every named place (also Wellspring's header) **[test]**.
Camera box: the whole matrix and a little more, as Black 2's caves (Victory Road 591: -8..520 x -40..568).

Outdoor doors: world.py writes a door per Sapphire warp into a cave (dir 2, type 3, Sapphire's order). A zone covers
whole 32x32 cells, so a door can stand in another zone's cell (Granite Cave's mouth is in Dewford's cell, Fiery
Path's in Route 112's neighbours'): Black 2 only reads the warps of the zone the player is in **[test]**, so
world.py `foreign_doors` copies such a door into the owning zone (appended last: no index moves) and gen_caves /
gen_interiors / hoenn_world point exits at the copy.

## Looks (_looks.json)
| look | Black 2 cave | area / set / pack | used by |
|---|---|---|---|
| d0 | Wellspring Cave, Mistralton Cave, Relic Passage, Seaside Cave, Victory Road (brown floor, green-grey rock) | 332 / 332 / 50 | gTileset_Cave, RusturfTunnel, MeteorFalls |
| in81 | Reversal Mountain inside (dark volcanic rock) | 388 / 388 / 80 | gTileset_Lavaridge (Fiery Path) |

Keys: floor/floor_size/floor_color, top/top_size/top_color, face_low (first tier on the floor), face_low_rock,
face_mid, lip_floor/lip_rock, face_u, edge (vertex colour), rim/rim_depth/rim_color, ledge, stairs, decals
[[tex, size, chance]], cracked [tex, size], rock1/rock2 (pack models) or rock_sprites (terrain templates), arch /
arch_s/n/e/w {chunk, box, anchor, into, materials, outside|inside}, water/water_top/water_bank, header_zone(_dark).
A template is copied from a Black 2 chunk (apicula, cached in <interiors>/_cave_templates): triangles of the listed
materials whose centre lies in box (chunk-corner units), moved so anchor is the origin. Other Black 2 cave sets seen
in set 332: Clay Tunnel/Relic Passage d29_*, Twist Mountain in51_* (ice) — new looks are a _looks.json entry.

## The first caves (2026-10-06)
| Map | Zone | Look, matrix | Doors / connections tested in DeSmuME | Proof |
|---|---|---|---|---|
| GraniteCave_1F | 118 | d0, 2x1 | Route 106 (door in Dewford's cell) <-> (37,12); (17,11) -> B1F (4,21); (5,10) <-> Steven's room | screenshots/cave_builder/GraniteCave_1F.png |
| GraniteCave_B1F | 124 (dark) | d0, 1x1 | (28,21) -> B2F; (25,13) -> 1F (35,3); cracked floor (2,1) -> B2F (2,1); darkness on a cold boot | GraniteCave_B1F.png |
| GraniteCave_B2F | 125 (dark) | d0, 1x1 | (29,13) -> B1F (29,13) | GraniteCave_B2F.png |
| GraniteCave_StevensRoom | 126 | d0, 1x1 | door (7,3) <-> 1F (5,10) | GraniteCave_StevensRoom.png |
| RusturfTunnel | 134 | d0, 2x1 | Route 116 west <-> (4,10); Verdanturf <-> (29,16); (18,20) <-> Route 116 east; rocks (24,4)/(24,5) block as in Sapphire | RusturfTunnel.png |
| FieryPath | 117 | in81, 2x2 | Route 112 south <-> (26,36) -> (26,4) <-> Route 112 north | FieryPath.png |

Wild battles in the caves use Sapphire's species/levels (Makuhita Lv 7 in Granite 1F, cave background) **[test]**.

Left for the story agents (gen_caves prints them): Granite 1F hiker (Flash), Steven (FLAG_HIDE_STEVEN_GRANITE_CAVE),
B2F hidden Everstones x2; Rusturf: Briney/Peeko/grunt/boyfriend/girlfriend scenes (coord events, map scripts),
hiker trainer, the two rocks' permanent flags (placed without them: Black 2's 10016 removes a rock until the map
reloads); Fiery Path: FLAG_LANDMARK_FIERY_PATH map script.

## Known limits / open items
- Strength boulders: Black 2's boulder (0x2003/0x2005) is 2x2 tiles (collWidth/collHeight 2, offset +8/-8,
  data/sprite_map.json), Sapphire's 1x1: Fiery Path's (17,15) blocks one more tile of the corridor; boulder puzzles
  (Fiery Path, Victory Road, Seafloor Cavern, Trick House) need a 1x1 boulder (sprite table a/0/4/7: the sprite
  agents' file) or adjusted positions — test pushing.
- Bridges (Sapphire elevation 15 crossing over a lower corridor: Victory Road, Shoal Cave): one collision layer only;
  Black 2's GC chunks have a second terrain layer (study tool: work/agents/cave_builder/study/coll.py) — not built.
- Water: drawn and collided as Wellspring's, not walked in a cave yet; currents/waterfalls in caves untested;
  Shoal Cave's tides (two map versions) not handled.
- Rock masses touching the map edge are cut there, and outer walls are only as high as Sapphire's border rows allow
  (one row = 16 units): leave room with "origin"/"matrix" where it matters.
- Lattice "black beyond the rim" also appears inside rock masses more than ~5 tiles from any floor (as Black 2).
- Hidden items (bg hidden_item) are not placed; Rock Smash tables dropped (Black 2's Rock Smash starts no battles).
- A chunk file must stay under Black 2's chunk buffer (110,600 B for caves/interiors): see "Chunk size limit" below
  (caves_misc); a bigger chunk hangs the game on the map change.

## How to test
    HOENN_AGENT=<you> HOENN_TEST_NO_WILD=1 HOENN_TEST_WARP=337,96,418 zsh b2tools/agent_build_caves.sh GraniteCave_1F
    cp work/agents/<you>/rom/hoenn.nds work/agents/<you>/rom/<unique>.nds
    cd b2tools && ../.venv/bin/python cave_test.py ../work/agents/<you>/rom/<unique>.nds OUT.png \
        SIGN C96,418 U1 U1 W30 Y37,12 W90 S ZGraniteCave_1F Q17,10 D1 W30 Y4,21 W90 S
- Test warps used: Route 106 near Granite (337,96,418), Route 116 near Rusturf (423,135,190), Verdanturf (120,176,203),
  Route 112 near Fiery Path (62,219,118 — the cell's zone, not Route 112's), any cave tile (zone,x,y).
- `COLD=1` boots without a save (darkness table), plays the intro and then takes moves from Littleroot (SIGN works).
- After a warp, `Y` waits for the arrival tile; the screen is still fading for ~100 frames, so wait before `S`.
- Routing with `Q` avoids the zone's objects; Strength boulders are bigger in Black 2 (see above).
- Tools of this work: work/agents/cave_builder/study/ (coll.py collision dump, tris.py triangle dump of a Black 2
  chunk box, mats.py materials, close.py close renders), work/agents/cave_builder/test/proof.py (proof sheets).

## Shoal Cave, Sky Pillar, New Mauville (caves_misc agent, 2026-10-06)
Proofs: screenshots/caves_misc/ (ShoalCave_tides, ShoalCave_rooms, SkyPillar, NewMauville). Tools of this work:
work/agents/caves_misc/tools/ (sapreach.py Sapphire reachability with Gen 3's elevation/surf/ice rules, comps.py
same-elevation regions, chunksize.py, path.py, findwork.py/poke.py RAM works, proof.py).

**Chunk size limit [code][test]**: Black 2 copies each chunk file (model + terrain layer(s) + buildings) into a
fixed buffer with no length check: 110,600 B for map types 0/11/15/16/19/27 (caves and interiors are 16), 86,020 B
for most others (ov036 MAP_CONFIGS 0x021ca01c, stride 0x48, field +0x34). Shoal Cave's inner room at origin (0,0) had
a 117 KB chunk 0 (100 KB model + two collision layers): the game hung on a black screen entering it. Spread big
caves over their chunks with "origin" and check with work/agents/caves_misc/tools/chunksize.py.

### Recipe keys (all optional, off by default; every older recipe builds byte-identically, checked)
| key | where | meaning |
|---|---|---|
| `layout` | models_cave.sapphire | build another pokeruby layout with the map's own events (Shoal Cave's high tide) |
| `alt_of` | gen_caves | this recipe is another layout of that map's zone: no zone of its own (gen_caves skips it) |
| `alt_rooms` | gen_caves -> zone json -> patches/interiors.py | [{"room", "event"}]: the other layout's chunks get a matrix of their own and an a/0/1/0 map replacement (kind 1, whole matrix; condition = event uid + 3) that loads it instead of the zone's matrix while the event is set |
| `tide` | gen_caves | zone-init script (MapScript 2) of a cave whose layout follows the clock, below |
| `shoals` | models_cave_misc.py | MB_SHALLOW_WATER 0x17 / MB_SHOAL_CAVE_ENTRANCE 0x1C -> Black 2 shoal cells (0x17, flags 0x10: the wading ripple) 4 below the floor, drawn as the darkened floor + the look's sparkle layer + banks |
| `ice` | models_cave_misc.py | MB_ICE 0x20 -> Black 2 sliding ice (class 0x18, flags 0x80: IsTileSlidingIce ov036 0x021a2c48 = 0x10/0x18; Icirrus 114's ice) drawn with the look's "ice" texture |
| `header_zone` | gen_caves | the Black 2 zone whose header the cave copies (overrides the look's) |
| `cave_zone` {area, header_zone} | gen_caves, in an **interior** recipe | zone files of a map the room builder builds (no cave recipe): its area and header zone |
| `encounters` | models_interior.py (room builder) | walkable tiles with Sapphire's wild-encounter behaviours get flags 0x84 (land encounters: FieldEncount_DecideTypeByTerrain tests flags bit 2) |
Also: ARROW gained 0x1C (Sapphire's MetatileBehavior_IsSouthArrowWarp); gen_caves' falls/ladders into a room-built map
use that room's origin (interior recipe "origin"); cave_tiles.json gTileset_Cave boulders + 0x37a/0x37d/0x37e (ice
rocks, only Shoal Cave's ice room); _looks.json + "in51" (Giant Chasm's ice cave, chunks 808/809, set 332).

### Tides [code][test]
Sapphire (time_events.c UpdateShoalTideFlag + the maps' OnTransition setmaplayoutindex): high tide 00-02, 09-14,
21-23 h, decided when you enter the entrance room from outdoors and kept while inside; only the entrance and inner
rooms have two layouts. Black 2 has a map replacement table (a/0/1/0, ov012 map_replace.c): entries by season,
version, or one of ten events (EVENT_MAP_REPLACE_TABLE: event uid i = work 0x4031+i == a fixed value). Uids 7-9 are
set by no Black 2 script and used by no entry (scanned a/0/5/6 for MapReplaceSetEvent/IsEventSet, read a/0/1/0).
- uid 9 (work 0x403A == 0x1028) = high tide: entries for the entrance and inner room matrices (kind 1).
- uid 8 (work 0x4039 == 0x120, saved, no map effect) = "came from inside": the stairs/lower/ice/inner rooms' zone
  init sets it; the entrance's zone init reads and clears it and decides the tide only when it was clear (a zone init
  can't see where the player came from: PlayerGetGPos needs the field's player actor, which doesn't exist yet).
- The entrance's zone init: RTCGetTime -> MapReplaceSetEvent 9, set, 1 (reload: MapMatrix_Load + MapMatrix_Patch on
  the new zone, which FieldMapControl_InitSpawn has already set; zone init runs before the field opens) + Sapphire's
  FLAG_SYS_SHOAL_TIDE for story scripts.
- Warps whose tile is water at high tide (entrance 1, inner 0/1/4/5) are moved to tile (0,0) by ObjInitWarpGPos at
  zone init (a type-4 warp fires when a surfer bumps its arch: FieldPlayerGrid_CheckWarpAtHitWall); the flooded ladder
  (38,15) is a step trigger conditioned on work 0x403A == 0 (FindTriggerAtPosGrid compares the work).
Tested: test warp at 05:00 -> low tide, at 12:00 -> high tide; a state saved inside at 05:00 and walked out to the
entrance at 12:00 keeps the low tide; inner room with the event poked (0x02225558 in this build) shows the high tide,
bridges over water walkable. Not tested: surfing in a cave (no Surf in the test saves).
Left: a stale tide after an Escape Rope/Fly out of the inner rooms (marker still set: the next entry keeps the old tide
once, then decides again); the Route 125 door does not fire (below).

### Maps
| Map | Zone | Built with | Notes |
|---|---|---|---|
| ShoalCave_LowTideEntranceRoom (+HighTide) | 138 | cave, d0, levels 3:0 4:16, shoals | Route 125's door: was y 0 with the shoal in front at -8 (warps match within 2 units, CheckWarpPositionMatch): world.py now gives doors their approach tile's height (world_fixes; tested: Route 125 -> Shoal Cave). **Open: the exit back (warp 0, arch (20,31), both tides) has y 0 but its approach (20,30) is a shoal at -4.4: you cannot leave by it [test]; its y should be -4 (gen_caves warp y = approach tile's collision height)** |
| ShoalCave_LowTideInnerRoom (+HighTide) | 146 | cave, d0, heights (0 low floor, 8 shore, 24 walkways, 48 plateaus/bridges, 64 NE nook), bridges, shoals, origin (9,13) | heights read from Sapphire's art and from what the high tide floods |
| ShoalCave_LowTideStairsRoom | 163 | cave, d0, five terraces 16 apart, one-tile ramps | |
| ShoalCave_LowTideLowerRoom | 162 | cave, d0 | the Strength boulder (25,3) blocks the way to the ice room as in Sapphire (model 0x2004 needs caves_east's boulder_1x1 patch) |
| ShoalCave_LowTideIceRoom | 139 | cave, in51, levels 3:0 4:16, ice | sliding tested: one step south on (15,12) -> (15,15), east (11,12) -> (14,12) |
| SkyPillar_Entrance | 169 | cave, d0, three terraces | Route 131's door (36,6) is deep water in Route 131's own layout; Sapphire swaps in layout 320 (LAYOUT_UNKNOWN_MAP_08302970: a cave door with sand in front) once FLAG_SYS_GAME_CLEAR is set (Route131 OnTransition): done by world_fixes as map replace event 7 (notes/WORLD.md "World fixes"; tested both ways) |
| SkyPillar_1F-5F | 164-168 | room builder (b2tools/caves_misc_skypillar.py), Dragonspiral Tower (area 295) | 2F/4F cracked floors -> fall to the floor below (tested 2F -> 1F); crossing them needs the bike, as in Sapphire |
| NewMauville_Entrance | 132 | cave, d0, P2 Lab header | the door is a cave arch |
| NewMauville_Inside | 133 | room builder (b2tools/caves_misc_newmauville.py), P2 Laboratory (area 345), 2x2 chunks, origin (12,12) | three layouts (fixups2 2026-10-07): the room = Sapphire's map (both colours up), `NewMauville_Inside_BlueDown` and `_GreenDown` (the lowered colour's two passage tiles are plain floor, `unblock`) loaded instead of it by map replace events 5 / 6 (works 0x4036 / 0x4037, `alt_rooms` in data/interiors/133.json: gen_caves copies an interior recipe's `alt_rooms`); the switches (0266 Sub_NI_Redraw) fade out and map-change onto the player's own tile so the new matrix shows; **tested**: blue switch -> cross a lowered blue barrier -> green switch -> the barrier is up again (screenshots/fixups2/04_*) |

## Meteor Falls, Victory Road, Cave of Origin, Scorched Slab, sealed chambers (caves_east agent, 2026-10-06)
Proofs: screenshots/caves_east/ (Sapphire | build per group). Code: b2tools/models_cave_levels.py (hooked into
models_cave.py like models_cave_misc.py), patches boulder_1x1.py and test_cave_kit.py (test only).

**Walk-under bridges = Black 2's second collision layer [code][bytes][test].** A `GC` chunk holds two terrain layers
(ov036 FieldChunkAccessor_GC_GetTerrain returns both); FieldG3DMapper_GetTerrain (src/ov036/field_g3d_mapper.c) takes
the valid layer whose height is nearest the actor's, ties to layer 0. Black 2: Seaside Cave chunk 631 (deck in layer 1
at 48 over the corridor at 0), Victory Road 780 (deck in layer 1, railings = blocked layer-1 cells at deck height).
Ours (recipe `"bridges": true`): Sapphire's walkable elevation-15 tiles between a higher floor and a lower floor/water
-> layer 0 = the floor or water below, layer 1 = the deck (0x0a/0x80; 0x84, on both layers' land cells, where Sapphire's
tile has the encounter attribute: Gen 3 tests the tile whatever the height, wild_tables 2026-10-08) at the higher floor's height; railings = blocked
layer-1 cells at deck height on the lower tiles beside the deck; the higher tiles at the deck's ends get a blocked
layer-0 cell at the lower height (the 16-unit steps are under the 20-unit step limit). room.json "collision1"
(+ chunks[k].collision1) -> patches/interiors.py builds a GC container. Tested: walking over and under (Victory Road
1F), surfing under (Meteor Falls 1F_1R), railings block. Sapphire's plank bridges (cave_tiles.json gTileset_Cave
"bridge" metatiles) are decks (d_hashi01, Seaside Cave's) over a chasm. cave_test.py routes over both layers and
`Mwater`/`Mland` switch between surfing and walking routes.

**Waterfalls [bytes][test].** Black 2's waterfall is one row of class 0x40 (flags 0x13, blocked) between two water
levels (Route 11 chunk 72: 72 / 32 / -8); Waterfall (FieldWaterfallTCB) moves the surfer 2 tiles, up when the water 2
tiles ahead is higher; surfing south into it descends (hm_free's nop in CheckAutoTileEvents). Recipe `"waterfalls":
true`: each Sapphire column's bottom tile = the 0x40 row at the middle height, the tiles above = upper water; the drop
is a steep sheet of the look's animated cave water (d0_miz + d0sizuku streaks + d0_mizgiwa foam: Black 2's caves have
no waterfall art). Tested up and down in Meteor Falls 1F_1R and Victory Road B2F. Surfing in a cave works (0x3f).

**Other recipe keys:** `heights` {"x,y": h} (the connected same-elevation region or water body around a tile gets that
floor height; use whole 16-unit levels: a ladder's MapChangeCore takes the level), `ramps` [[x0,y0,x1,y1,side]],
`pools` (blocked deep water drawn as still water: Kyogre's pool; `[x0,y0,x1,y1,{"metatiles": [ids]}]` takes the blocked
tiles of those metatiles instead of the surfable behaviours: Ruby's lava pools, ruby_maps 2026-10-08), `look_over` {key: value}
over the look's keys (Ruby's lava: water/water_top/water_bank = Reversal Mountain's in81_magu00/in81_magu01/in81_mizuga1 from set
388 through `tex_sets`, `water_top_size` 64; Black 2's chunks 723/726 lay magu00 at bank-10, magu01 2 above it, mizuga1 as the
bank; the lava is static in set 332's areas, its animation is area 388's), `void` (unreachable walkable filler -> rock),
`wall_decals`, `cliff`, `reach` (units a floor's capped profile counts, default 32 x tiers + 48; Altering Cave 896 = the
whole map: past the default a raised floor alone lifted a far corner, a lone rock pillar in the black; check_postgame).
With several heights the rock lattice ignores floors more than one tier below the nearest one
(a raised pool keeps its walls). Floors one rock tile apart should differ by 16 (Black 2's step, Victory Road 780).
ARROW + 0x6D (Scorched Slab's water arrow); a warp the player surfs into gets the water's height, a doorway on a raised
floor the height of the floor in front (spot_y). Outdoor doors need the same (world.py, world_fixes): Route 115 ->
Meteor Falls (floor 32, door 0) and Route 120 -> Scorched Slab (water 24, door 32) only fire with the door at the
approach tile's height (tested on a patched world copy).

**Text/script files past the end [test].** A room's own text number (data/hoenn_interiors.json own_text) beyond the
last file in src/text/script got no a/0/0/3 entry, and any script in that zone (a ladder) showed "An error has
occurred" (Victory Road 915-917). patches/text.py now writes placeholders up to the highest room number, scripts.py
pads a/0/5/6 to the highest own number.

**Strength boulders 1x1 [code][test].** The size is per object record (a/0/4/7 collWidth/collHeight/offX/offZ;
StrengthRockSpaceCheck ov036 0x021ba880 and CheckBlockedCollPathToPosition read it). Object code 0x2004 is a Strength
rock in code (IsNPCStrengthRock ov012 0x02168284: 0x6d, 0x2003-0x2005; no other code tests these numbers) with an empty
record; patches/boulder_1x1.py fills it: 0x2005's record, 1x1, no offset, model = bigrock2 at half scale (new a/0/4/8
file). gen_caves places 0x2004 (8196). **List `boulder_1x1` after `sprites` in every patch list** (without it 0x2004
is invisible). Tested: pushing down Victory Road B1F's one-tile corridor, Fiery Path's corridor beside (17,15) free.
Pushed positions are not saved (RELOADABLE_STRENGTH_ROCKS has only Black 2's zones), as Sapphire resets them.

Test kit: `EXTRA="test_cave_kit"` (work/agents/caves_east/build.sh): Littleroot's town sign gives a Mudkip, 8 badges,
HM01-06, TM70/TM94 and warps to HOENN_TEST_WARP (+ HOENN_TEST_WARP_Y level); the second sign (174,369) to
HOENN_TEST_WARP2. HOENN_TEST_NO_WILD_SURF=1 also removes surfing battles.

Story fix-up (2026-10-07): breakable rocks with a Sapphire hide flag that has an id (Rusturf Tunnel's
FLAG_HIDE_RUSTURF_TUNNEL_ROCK_1/2) get it in the zone json (converter/gen_caves.py story_flag), so they stay away once
the story sets it (hm_free's 10016 only deletes the actor: scenes/RusturfTunnel_Ch3.inc sets the flag after the
reunion). Victory Road's FLAG_VICTORY_ROAD_ROCK has no id yet (Ch11 claims one, then rerun gen_caves VictoryRoad_B1F).

## Script darkness: Sapphire's flash levels (dewford_dark, 2026-10-07) [code][test]
Black 2's darkness is ov036's FieldFlash (field->skillMapEff->flash): a black mask model drawn at the camera, scaled by
a FieldFlashAnimation scale (on-screen size proportional to it; FieldFlashG3D_Draw skips scale 0). Black 2 sets only
two sizes: dark 3.0 at field load for an a/1/4/9 zone (func_ov036_021c1d14) and Flash 10.625 (func_ov036_021c1d30,
EventFlash); no script command touches it. New command **0x1c9 `h_flash_scale scale, frames`** (src/include/hoenn_story.inc;
code in b2tools/patches/zone_effects.py, in place of Black 2's unused NDemoStart): scale in 1/256 (768 = Black 2's dark
cave, 0 = none), at once or grown over `frames` field frames by Black 2's own FieldFlashAnimation; both args may be
works. A zone outside a/1/4/9 gets a FieldFlash on the first nonzero call, so a script-dark room needs no table entry
(and Flash can't be used there: FlashPerms bit 0 is the zone's). Call it from MapScript 3/4 (field load: the field
exists, the screen is still dark; its permission byte now allows map scripts) or a normal script, never from a zone init.
`FLASH_PX(px)` = Sapphire's radius in pixels -> scale (x32): Black 2's dark circle 3.0 = Sapphire's dark-cave 24 px
(measured in Dewford Gym: ~28 px radius for tiles of ~19.5 px = 1.45 tiles; Sapphire 24 px = 1.5 tiles).
Dewford Gym (0050/0051_room_DewfordTown_Gym*.s): SetFlashLevel 24/40/56/72 px by trainers beaten on every field load;
back from a battle the old circle, then BrightenRoom (reserved script 5: SE + growth 1 px a field frame) once the
trainer's event has set its flag (a trainer's flag is set after the field reload, so the map script can't see it);
Brawly's win grows it to 200 px (whole screen) and turns it off. Tested on a cold boot (screenshots/dewford_dark/):
entering, each trainer, Brawly, re-entering lit, a menu return, Granite B1F dark and lit by Flash as before.

## Cave checks and the cave sweep (sweep_caves, 2026-10-07) [code][bytes][test]
**Checker** `python3 b2tools/caves_check.py [--dir ROOMS] [--kinds abcefhistwx] [--summary] [MAP ...]` (default: every
recipe of data/cave_layouts built in HOENN_INTERIORS_DIR or work/interiors; the docstring has the details). Kinds:
a ladders/ledges/ramps (trigger, pit/stairs, level take-off/landing, slope ends), b rock models over walkable tiles,
c people/objects (zone json + story objects) on solid tiles, e events vs heights (warps fire within 2 units of the
player's y, CheckWarpPositionMatch; triggers; signs -2..+2, CheckBGPositionMatchGrid; MapChangeCore landings), f surfaces
< 1.95 apart, h holes (orthographic views 35/45/55 deg x yaw -20/0/20, back faces culled, alpha-tested textures; not
past the map's edge or through an arch's tunnel: black there, as Black 2's own chunks), i objects Sapphire reaches and
Black 2 doesn't, s chunk files > 110,600 B, t textures (missing, stretched, coordinates past the DS's +-2048 texels),
w walkability vs Sapphire (reach from every warp with Surf/Waterfall under Gen 3's rules vs Black 2's: blocked cells,
< 20-unit steps (ActorRouteCollCheckCore), side walls (TILE_EXIT/ENTER_BLOCK_CHECKS), ledges, two layers, water,
waterfalls, ice; and single moves), x darkness. Report-only step in b2tools/rebuild_slice.sh (fast kinds;
CAVES_CHECK_KINDS=abcefhistwx adds f and h, ~10 min for all caves).

**Counts** (52 caves and underwater maps; before = the lead's v13.1 build, after = this sweep's builders):
| kind | before | after | what it was |
|---|---|---|---|
| h holes | 4,435 in 44 maps (844,201 px) | 13 in 8 maps (238 px, none over 52 px) | wall feet, levels, arches, ladders, chasms, waterfalls, water |
| t textures | 163 in 46 | 35 in 26 | smeared crease/rim/cliff faces, UVs past the DS limit; left: 22 rim fades to black (Black 2's own mapping), 13 cliff faces at 0.3 texels/unit |
| f layered surfaces | 65 in 34 | 0 | decals on decals/arches, arch spill 1 unit up, waterfall streaks/foam, banks/decks coplanar |
| w walkability | 12 in 2 | 0 | Meteor Falls 1F_1R shores at 0 under an 88-unit pool; Shoal high tide: walkway climbable from the water |
| e events | 12 in 6 | 0 | 10 story signs at y 0 on raised floors (Shoal shells, Victory Road hidden items: never readable), Seafloor Room6's water door never fired, 1 MapChangeCore landing at level 0 on an 8-unit floor (snaps: tested, not a glitch; Sapphire's 2 off-map Meteor Falls signs are skipped) |
| a ladders/ledges | 4 | 0 | 3 were slopes ending at a shoal (wading water drawn 4 below: by design, checker refined); Victory Road B2F's ledge (40,20) is jumped from a ramp tile, as in Sapphire: (40,19) -> (40,21) [test], the checker now accepts slope take-offs |
| b c i s x | 0 | 0 | largest chunk VictoryRoad_B1F 104,356 B (was 99,268) |
Navel Rock (events agent's 19 caves, built with these builders): 3 rim fades only.

**Builder fixes** (models_cave*.py; every recipe builds, chunks under the buffer):
- Wall feet: face_low (d0gake_001, in81_gake_b, in51_gake1) has transparent bottom rows; Black 2 draws the floor under
  every face_low face (Wellspring 486: every d0gake_001 triangle lies over d0yuka_001) [bytes]; ours stopped at the tile
  edge and the background showed along every wall's foot. Cave.foot_region: floor tiles + the walls' first-band
  lattice cells merged into rectangles on the lattice grid; per-face floor for the rest (beside ice/shoals, arches).
- Floors at several heights: skirts (rock faces under floor/ramp/water edges above lower rock); face bands by a second
  distance grid (LEVELS DB: at ties the lower floor's face, so a higher floor's edge is a lip, not a wall foot); band
  triangles spanning two levels drawn as cliffs; flat crease triangles get the rock top (or planar UVs); lone shores of a
  seeded pool take its height (Meteor Falls 1F_1R (6,9), (16,9)).
- Arches: the two neighbour tiles draw their rock clipped 16 units from the arch's middle (Victory Road 788's faces run
  up to the tunnel's sides) [bytes]; template flat pieces < 2 units over the floor lifted to 2 (chunk 738's spill at 1).
- Up-ladder notches: walls on the tile's edges (they stood 1 unit in, the rock beside ended open).
- Bridges: a dark chasm floor under planks and walls to the corridors beside them; deck pieces merged along the bridge,
  no overhang/side face over floor at the deck's height; waterfalls: rock beside the drop, streaks 2.2 and foam 2 off.
- Water: one level per connected body (the lowest shore's: Shoal Cave's high-tide entrance was split 16 units);
  land of elevation != 3 beside surf water < 20 units gets side walls (Gen 3 lands a surfer only on elevation 3);
  door warps in front of water take the water's height (Seafloor Room6 (14,8): surfing into it works [test]).
- Decals one per tile, none within 3 tiles of an arch; underwater: sunlight net at +2, coral at +4, none near arches.
- Texture coordinates centred per chunk: the DS stores them as s16 1/16 texels; a face straddling +-2048 texels wraps at
  one vertex (decoded our Underwater1 chunk 7: v -33 came back as 31) [bytes]; flat planar UVs near 0.
- Size: vertical faces one-sided (steps, banks, skirts, deck sides; none facing north, the camera never sees them).
- b2tools/patches/story.py: a story trigger/sign in a cave without "y" gets the floor's height (cave_y).

**Tested** in DeSmuME (screenshots/sweep_caves/10-17; renders before|after 01-03): Granite (Route 106 door, ladder to
dark B1F), Meteor Falls 1F_1R (door out to Route 114 and back, bridge, waterfalls), Shoal Cave (Route 125 door both
tides; stairs-room ladder lands on the inner room's 8-unit floor), Seafloor Room6 (current ride, surf into the water
door -> entrance), Victory Road 1F (under the deck), Fiery Path (Route 112 door), Seafloor entrance (surf, Dive ->
Underwater_SeafloorCavern).
Test kit for states made on a kit-free build: `EXTRA=test_sweep_kit` (b2tools/patches/test_sweep_kit.py: test_cave_kit
appended to Littleroot's real script file, only the town sign redirected; walk into a house and out to reload
Littleroot, then read the sign). test_cave_kit replaces all of Littleroot's scripts: leaving a house there goes black.
Follow-up (same day): Shoal Cave's inner rooms had gaps where a plank chasm, a deck end and rock meet: skirts under
the chasm floor where the rock beside it lies lower (LEVELS.geometry -> Cave.skirts(heights=)); its ice room had an ice
crystal (a boulder tile of elevation 0) on a 16-unit platform with open sides: a boulder takes the level most of its
neighbours have (Cave.classify), not the highest. Walked too: Cave of Origin (Sootopolis door, 1F dark), Desert Ruins
(Route 111 door, inner door), Victory Road B2F ledge from the ramp (screenshots/sweep_caves/04, 18-20).
**Left**: 13 specks of 6-52 px (3.5-13 square units) at odd corners; T-junction cracks between merged strips are not
checked (the DS rasterizer can show single pixels there).

## Altering Cave (postgame_maps, 2026-10-07)
Emerald's map through data/hoenn_event_maps.json, recipe data/cave_layouts/AlteringCave.json, zone 271 (notes/EVENTS.md
"Post-game maps"). New recipe keys, read by converter/gen_caves.py: `encounter_files` (fixed a/1/2/7 files, base table
first; kept in data/hoenn_encounters.json as AlteringCave, AlteringCave_2 ...) and `variants` [{zone, table}] (copies of
the zone with the map's other wild tables: data/interiors/<zone>.json "variants", installed by patches/interiors.py; an
event map's tables come from its decomp's wild_encounters.json, gen_caves.event_tables). caves_check: 2 (t) rim-fade /
cliff-face stretch findings, the kinds the sweep left. Chunk 59,036 B.
Checked (check_postgame, 2026-10-07; screenshots/check_postgame/): caves_check abcefhistwx 2 (t) before and after (the
sweep's accepted rim-fade / cliff-face classes); in DeSmuME the whole cave walked (both levels, the NE stairs), the mouth's
door in and out (banner, lit), table 9 = zone 330 (Smeargle). Fixed: a lone rock pillar at (31,3)-(31,5) floating in the
black above the raised NE room (recipe `reach`; chunk 59,036 -> about 57,850 B). Left as the levels builder draws them: the
NE room is a plateau whose rim is the one-tier rock between the levels (Emerald draws walls round it), 1-2 pixel specks
beside its stairs' top and two small floor tabs at its south corners.

## Mist caves (underwater_polish, 2026-10-08) [code][bytes][test]
Cave of Origin B2F-B4F, Seafloor Cavern Room 9 (+ their Ruby layouts) and Rusturf Tunnel have mist 9 (fixed_weather).
**Why the void was light blue**: Black 2's weathers swap the field light (ov036 0x02199734/0x02199740 ->
FieldLight_ChangeData(light, arc 61, arm9 table 0x02090124[weather], 60 or 1 frames)); mist 9 -> a/0/6/1 file 1: fog
colour 0x6318 and the clear colour of the sky per time of day (0x7b10 light blue by day; 0x4868/0x4d28/0x3f1f night,
dawn, dusk). FieldLight_FlushCore (0x02197abc) sets FieldFog_SetColor(record fog) and gfxClearColor(record clear, 31,
0x7fff, 0, fog FALSE): the rear plane is never fogged, its colour is the weather light's. Caves' own light (area 332 ->
a/0/6/0 file 32) has clear 0 / fog 0. Black 2's other mist kinds pair clear = fog (10/13: 0x2108, 11/14: 0x6b5a); only 9
(Giant Chasm, outdoors) uses the sky. So: uncovered background = light blue, and our black (rim colour 0, arch
tunnels) took the fog's grey with distance (fixed_weather sets the fog flag on every Hoenn material).
**Fix** (b2tools/models_cave_mist.py, hooks at the end of Cave.build_terrain and after the chunk split; active for caves
whose room has a mist weather in data/hoenn_weather.json "rooms", or recipe `"mist"`): the rim's all-black triangles on
material d29_gake2d (set 332's opaque near-black, used by no other Hoenn chunk), a black floor of it under the whole
matrix (min height - 24), black walls 160 high on the matrix's north/west/east edges and a 256-unit floor past its south
edge (edge chunks draw past their cell); all in 128-unit squares: **the DS hides a whole polygon that crosses the far plane**
(POLYGON_ATTR bit 12 clear, Black 2's 0x001f8081), and big quads vanished where their far end lay past it [test]. Under every
flat rock top a copy 4 units lower (the T-junction crack lines in Room 9's tops now show rock). patches/fixed_weather.py
NO_FOG = {d0ana_002 (inside arch tunnel), d29_gake2d}: those keep the fog flag off, so they stay black. (d0ana_002 has 37%
transparent texels: as the void it let the light blue through in dots [test].) Every other cave builds byte-identically.
caves_check abcefhistwx: only the accepted rim-fade (t) class, before and after. Chunks +3.4..+4.5 KB (largest Room 9 Ruby
chunk 0 86,792 B). Proofs: screenshots/underwater_polish/06 (Sapphire), 07 (Ruby). Left: a sliver of light blue in the far
top-left corner from Room 9's west edge (past the far plane), single black specks where cracks show the void.
**Mist rooms** (final_check, 2026-10-08) [test]: Lavaridge Gym 1F/B1F (room builder, mist 9 for Sapphire's steam) showed the
same light blue past their walls and in the sand holes (screenshots/weather/lavaridge_gym_mist.png). models_interior.build
now calls models_cave_mist.room_active / room_geometry / apron for a room with a mist weather in data/hoenn_weather.json
"rooms" (or recipe "mist"): the VOID floor under the matrix, the walls and apron past its edges, VOID taken from set 332 into
the room's texture list. Every other room builds as before. Proof: screenshots/final_check/02_lavaridge_gym_mist_before_after.png
(both versions); rooms_check counts unchanged.

## Floor lips and raised-floor corners (map_glitch_fix, 2026-10-09)
Meteor Falls 1F_1R's raised platform (12-17,17-18, y 48) read as a flat slab over the pool: Cave.face_tri chose the floor
lip only for a vertex exactly at r 16, but a lower floor 2+ tiles deep ties the profile at 16 for every distance 16-32
and the lattice keeps the larger one (DB), so raised floors got the dark rock lip; and models_cave_levels.lattice let a
lower floor/water touching a floor tile's corner pull the rock below the floor's edge (the platform hung out past the
rock, skirt under it). Now: floor lip for r >= 16 at full colour (Black 2's d0gake_002, chunks 486/488/630/788), and
lattice pass 3 raises rock points on a drawn floor tile's edge to the floor (not on a lower floor's own edge). Changed
geometry in 10 caves (442 floor-lip triangles, 342 lattice points): Victory Road 1F/B1F/B2F, Meteor Falls 1F_1R/B1F_1R,
Shoal Cave inner rooms (2) and stairs room, Altering Cave, Sky Pillar entrance; collision and placements unchanged.

## Victory Road and the multi-level caves (sweep_outdoor, 2026-10-11)
walk_diff's 84 open cave tiles (HEAD 9b691e0), each looked at (renders + DeSmuME, screenshots/sweep_outdoor/):
- **32 real, fixed [code]** (models_cave_levels.lattice): the chasm under Victory Road's plank bridges (deck - 32) took
  part in the rock envelope everywhere; its profile's flat top (chasm + 16) lay level with a corridor beside it, so the
  rock tile between them was a flat strip at the corridor's height, blocked (the user's 'invisible walls' along every
  bridge in Victory Road 1F/B1F/B2F and Shoal Cave's inner rooms). Within a tile of a real floor the chasm now counts
  only where it is nearer than that floor (and always within 6 units of a deck: under its overhang); the rock rises
  from the corridor and drops behind its ridge.
- **4 real, fixed** (data/cave_tiles.json): Meteor Falls' rock clusters 0x20e / 0x20f / 0x21f on floor-coloured
  ground were flat rock tops; they are boulders (drock models) now, as Granite's and Rusturf's.
- **10 checker false positives** (walk_diff WATER_TEX): Kyogre's pool, Navel Rock's pool and Ruby's lava (d0_miz,
  in81_magu) were counted as floor.
- **38 intended** (walk_diff, listed with the reason): a flat rock top in the cave's dark rock texture (d0yuka_002, half
  the floor's brightness) level with the floor beside it - the border tile Sapphire blocks at a raised floor's edge or a
  rock band's foot - reads as rock like every rock top of the cave (Black 2's own caves keep such tops too).
- After: walk_diff cave OPEN 84 -> 0 (intended 42 -> 89: the 38 above, 13 tiles the new rock shape turns into the same
  two intended kinds - 8 of Sapphire's own invisible walls, 5 rock tops). caves_check t 42 -> 42, h 13 -> 14: one new
  6 px hole at Victory Road B2F (41, 24) in one of the nine views (yaw 20); left, too small to see.
