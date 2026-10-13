# Map-building toolchain on macOS (researched 2026-10-05)

Rule: **no Nintendo SDK tools** (e.g. `g3dcvtr.exe`, which PDSMS uses for NSBMD export). Everything below avoids them.

## Pipeline
| Step | Tool | Runs | Status |
|---|---|---|---|
| Terrain geometry | `b2tools/build_chunk.py` (plan → DAE via `b2tools/dae.py`) | native | **working** (Littleroot) |
| Terrain tiles/textures | Black 2's own models/textures via apicula | native | working |
| Building models (Gen 3 shapes) | `b2tools/buildings.py` + `models_<town>.py` → DAE (Blender for curved shapes later) | native | **working** (Littleroot) |
| OBJ/DAE → NSBMD (no textures) | `b2tools/java/ToNsbmd.java` (CTRMapV's `NSBMDWriter`, headless) | native Java 21 | **works in-game** (2026-10-05, `screenshots/tests/2026-10-05_terrain_pipeline.png`) |
| Collision `.per` | `build_chunk.py` (Nuvema's tile values) | native | **working** |
| Map container (`WB`) | `b2files.gf_container_build` (round-trips all 1065 chunks) | native | **working** |
| Matrix `a/0/0/9`, encounters `a/1/2/7` | Our Python writers (formats in GEN5_MAPS.md) | native | planned |
| Pack NARCs | `external/pokebw2/tools/scripts/narc.py` (byte-identical round trip on `a/0/0/8`) | native | tested |
| Rebuild ROM | pokebw2 `tools/dsd rom build` | native arm64 | tested (matching build) |
| Events (warps, NPCs, signs) | `b2tools/zones.py` (round-trips all 615 entity files) | native | **working** |
| Scripts | `src/field_scripts/NNNN_*.s` + patch `scripts` (clang + decomp macros) | native | **working** |
| Text, place names | `src/text/` + patch `text` (decomp `text_data.py`) | native | **working** |
| Building textures | `b2tools/java/MergeNsbtx.java` (CTRMapV `NSBTXWriter`) | native | **working** (A5I3 re-encoded, see GEN5_TERRAIN.md) |
| CTRMap-CE GUI | CTRMap-CE + CTRMapV 1.4.1 | native Java 21 | not needed so far; 3D viewport untested on this Mac |
| Cross-check `.per`/models | BasicPerHandler 2.0-test (Windows) | Wine (launches) | optional |

## Tools on disk
- `tools/PDSMS/AdAstra-2.4/` — Pokémon DS Map Studio v2.4 (2026-09-24, AdAstra-LD fork). Launches on Java 21/arm64.
  Trifindo's original 2.2 fails here (x86-only JOGL). `.pdsmap` is plain text (script-generatable). Gen V NSBMD export
  needs `g3dcvtr` → not used; OBJ and `.per` export are its own code.
- `tools/BasicPerHandler/` — 2.0-test (Gonhex, 2021-05-30). SHA256: Win64 exe `5da3dc0a…5279`, Win32 exe `fd7f93e0…6210`.
- PDSMS 2.4 jar SHA256 `8c71f63c…7110`.
- Not usable here: SwissArmyKnife (x86_64 .NET 6 + SkiaSharp), Trifindo PDSMS 2.2. Not needed: Tinke.
- No Blender add-on writes NSBMD without `g3dcvtr`; Blender is fine as a modeller exporting OBJ/DAE.

## Format sources
- Maps: https://ds-pokemon-hacking.github.io/docs/generation-v/resources/bw_b2w2-maps/ (content 2024-01-09):
  container header, permission tile = `u16 inclination, u16 distance, u16 behavior, u16 flags` + corner list,
  B2W2 distance table (1285 entries). Inclination table "TODO" in docs → PDSMS `CollisionsBW3D.java` has one.
- Area data: https://ds-pokemon-hacking.github.io/docs/generation-v/resources/b2w2-area_data/ — areas 2..0x11A use
  **4 consecutive texture entries, one per season** (so area 2's textures are entries 2–5? → verify before writing).
- All 1065 chunks / 1081 permission sections / 416 matrices in our dump fit these layouts.

## Proven in-game (2026-10-05)
Nuvema's terrain (chunk 0) exported by apicula to DAE, written back by `ToNsbmd` and packed into `a/0/0/8`:
renders the same as the original (~1% pixels differ: NPCs/animation), and a texture swap shows up in-game.
Rules learned:
- **Texture names in the model = DAE image ids**, must equal the area texture names exactly (≤16 chars; some
  contain dots, e.g. `hana01.1`). apicula's DAE prefixes ids with `image-` and turns dots into `_`: undo both.
- **Palette names** come from texture metadata `IdxFormatPaletteName`; `ToNsbmd` takes a texture→palette list.
  Most are `<texture>_pl`, not all — take them from the game's own models.
- Header version 1 (vs retail 2) is fine for the game.

## Unknowns to test
1. Season handling of texture sets for area 2.
2. PDSMS 2.4 3D editors on this Mac; BasicPerHandler beyond launching.
