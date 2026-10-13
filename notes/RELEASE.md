# Releases (the user's own copies; the project stays private)

A release is the built ROM plus a BPS patch made against the user's own Black 2 dump (roms/black2_original.nds, SHA-1
e51e6dfb8678a3d19dcd2a10691b96a569ca0abb). Both go to release/ (git-ignored: *.nds; the .bps stays out of git too).

    cd b2tools && ../.venv/bin/python bps.py make ../roms/black2_original.nds ../work/rom/hoenn.nds ../release/Pokemon_Sapphire_NDS_vNN.bps

b2tools/bps.py writes the BPS format (beat / Floating IPS) and checks every patch by applying it to the original and
comparing the result byte for byte (and the format's own CRC32s). Encoder: same-offset runs (SourceRead), moved
512-byte blocks and data moved inside rebuilt archives at any 4-aligned offset (SourceCopy), one-byte runs (TargetCopy),
the rest literal. v14.1: 29.3 MB patch (29.1 MB of it new data), a few seconds.
Any BPS patcher (Floating IPS, beat, Rom Patcher JS) applies it to the same original dump.

Names (user, 2026-10-08): the games are "Pokémon Sapphire NDS" and "Pokémon Ruby NDS" ("HoennB2" stays internal).
Release files: release/Pokemon_Sapphire_NDS_vNN.{nds,bps} and release/Pokemon_Ruby_NDS_vNN.{nds,bps} (the Ruby ROM is
built with HOENN_VERSION=ruby into work/rom_ruby; both .bps patch the same original Black 2 dump). Separate posts:
release/POST_Sapphire.md, release/POST_Ruby.md (never reference each other); screenshots in release/showcase/<version>/.

Showcase screenshots are native DS size only (user, 2026-10-08): 256x192 (one screen) or 256x384 (both), no upscaling; the animated titles too.

Public repo (patches only): https://github.com/logdog2325/pokemon-ruby-sapphire-nds (local clone ~/Documents/GitHub/pokemon-ruby-sapphire-nds). A release = `gh release create vNN <both .bps>` there, plus README/screenshots updates. Never push this private HoennB2 repo; never upload .nds.
