# CTRMap-CE and its Gen V plugins: what they really do (researched 2026-10-05)

Real GitHub org: **ds-pokemon-hacking** (kingdom-of-ds-hacking redirects there). Official docs:
https://ds-pokemon-hacking.github.io (Gen V guides: `bw_b2w2-using_ctrmap`, `bw_b2w2-map_insertion`, `bw_b2w2-code_injection`).
Evidence below is from the CTRMapV source and release notes unless marked "docs".

## Plugins
| Plugin | Version | Status |
|---|---|---|
| **CTRMapV** | 1.4.1 (2026-04-28, flagged pre-release) | The only released Gen V plugin. Jar in `tools/ctrmap-plugins/` (SHA256 `934ba25c…a521`) |
| Nightfire | no releases, last commit 2024-08 | Unfinished: trainer/encounter/map-container/matrix editors. Encounter class can only read; matrix "Commit" button does nothing |
| Sparkplug | no releases | Example plugin only |

Related (not plugins): PMC 13.2.4 (`PMC_B2.rpm`, code injection), NitroKernel, PokeScript/SDK5, swan headers + symbol DB.

## What CTRMapV can and can't do
| Feature | Status | Notes |
|---|---|---|
| New zone | Partly | Zone Loader "+" **duplicates the loaded zone** and appends it. Whether B2 accepts zone IDs past the retail count without a code patch is unknown; per-zone side tables (sound, weather, fog) may need entries |
| New/edit map matrix | **No** | `VMapMatrix` has a reader only |
| New/edit map chunk (terrain) | **No** | `a/0/0/8` is read-only, except building positions |
| Terrain model import | **No** (in the map editor) | CreativeStudio can convert DAE/OBJ/SMD → NSBMD/NSBTX via Export > "NNS Resource". No FBX/glTF |
| Buildings | **Yes** | Add/remove/move/rotate per chunk. Area building packs can gain models: "+" imports DAE/SMD/OBJ, set UID + door model + anim. Docs warn: shared maps (e.g. interiors) change everywhere they're used |
| Collision/permissions | **No** | No editor, no auto-generation |
| Warps, NPCs, signs/hidden items, triggers | **Yes** | Event Editor, add/remove |
| Scripts | **Yes** | PokéScript compiler + IDE in core; B2W2 library in CTRMapV. "Attempt to decompile" can destroy non-user scripts. Issue #28 ("Open in IDE not doing anything", 2026-06) is open |
| Text | **Yes** | Game text + script text; archives can be expanded |
| Place names (location sign) | **Yes** | Zone Loader "Location info": name ID, display type, icon. Names are in system text bank 109 (B2W2) |
| Level scripts | No | "no dedicated editor yet" (docs) |
| Wild encounters | **No** | Zone only picks which encounter file it uses → we write `a/1/2/7` ourselves (decomp has the format) |
| Code injection (PMC) | Yes (B2W2) | Extras > Install/Update PMC. Needed by no documented feature; maybe needed for new zones |
| Export ROM | Yes | File > Export ROM |

## macOS
- Docs ("Using CTRMap", 2024-12-29): **"macOS (any version) is not supported."** No macOS bug reports found either way.
- Core jar bundles universal (x86_64 + arm64) JOGL natives. Developer recommends OpenJDK 21 (issue #14) — we use Temurin 21.
- Keep the default OpenGL 2 renderer (the GL4 one needs a profile macOS lacks). File dialogs have a JFileChooser fallback since 2026/02/01.
- DSi-enhanced ROMs supported since 2025/09/16.

## Consequence for this project
CTRMap handles events, scripts, text, place names, building placement and code patches. **Terrain models,
collision and matrices need other tools or our own scripts.** See `notes/GEN5_MAPS.md` for the formats.

## Open questions (settle by testing)
1. Does a "+"-duplicated zone work in-game on B2?
2. Does the 3D viewport render on Apple Silicon (Retina scaling, blank viewport)?
3. Limits of area building packs (model count, UID range).
4. Does the Rail editor save?
