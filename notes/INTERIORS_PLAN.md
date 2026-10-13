# O4: every Hoenn building interior, matching Sapphire (2026-10-06)

User: "do the building interiors ... make sure you're trying to make the interiors match sapphire too", "launch agents
... like you did for the overworld", "comb and check for graphical glitches in both the interior and exterior and fix".
Story scripts wait until the map is fully built.

## State when the agents start
- `converter/allocate_interiors.py` -> `data/hoenn_interiors.json`: 207 Sapphire indoor maps -> Black 2 zones.
  status: hand (Littleroot, done), b2 (Pokémon Center 1F = Black 2's own Center room, exit re-pointed), auto (157,
  generated), big (taller/wider than one chunk: 10), link (Center 2F + link rooms: not reachable, left out).
- Every outdoor door leads to its room (world.py appends door warps; hoenn_world.py; tested Petalburg house + Center).
- `converter/gen_interiors.py`: per auto room data/interiors/<zone>.json (warps in Sapphire's order, one per Sapphire
  warp tile, simple people/signs with Sapphire's text), script/text files `*_room_<Map>`, and a PLACEHOLDER recipe
  data/interior_layouts/<Map>.json (`"_auto": true`: floor + walls, no furniture).
- A recipe without `_auto`, or a room json without `"auto": true`, belongs to whoever made it: gen_interiors never
  touches it again.

## Families (one agent each) — see the workflow prompt for the room lists
houses (gTileset_GenericBuilding, 74), shops (gTileset_Shop, 21: marts with working clerks), facilities
(gTileset_Facility, 18), gyms_league (Gym tilesets + Elite Four, 20, incl. the BIG rooms: multi-chunk support),
specials (28 unique rooms). Then glitch sweeps: exterior (parallel), interior (after the rooms).

## Tools
- `HOENN_AGENT=<name> zsh b2tools/agent_build_rooms.sh [ROOM ...]`: rebuilds the named rooms into the agent's own
  copy of work/interiors and builds a ROM (the overworld in work/world is only read).
- `HOENN_TEST_WARP=zone,x,z` (env for the build): Littleroot's town sign (stand at (183,366) facing north) warps
  there; start state work/emu/base_littleroot.dst (C173,361 G184,361 G184,366 G183,366 U1 A).
- `python3 b2tools/preview_interior.py <Map>`: render a room without the emulator; `converter/render.py` renders
  Sapphire's map for the side-by-side check.
