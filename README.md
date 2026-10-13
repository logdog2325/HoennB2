# HoennB2: source code of Pokémon Sapphire, Ruby and Emerald NDS

This is the source code behind **[Pokémon Sapphire, Ruby and Emerald NDS](https://github.com/logdog2325/pokemon-ruby-sapphire-nds)**. Those games remake Hoenn inside Pokémon Black 2's engine, with Black 2's 3D overworld, Gen 5 battles and the Hoenn story. To *play*, download a patch from that page instead; this repository is for people who want to learn from the tools or reuse them in their own projects.

Everything here is a set of Python tools (plus a little C and Java) that read the Gen 3 games' data and **patch your own Black 2 dump**. No ROMs, game dumps or built games are included, and none are downloaded.

## What's inside

| Folder | What it is |
|---|---|
| `converter/` | Reads the Gen 3 maps, scripts, trainers, wild Pokémon and text from the [pret](https://github.com/pret) decompilations and writes the project's data files. |
| `b2tools/` | The builder. It makes the 3D overworld, buildings, caves and rooms (`world.py`, `models_*.py`, `terrain/`), packs the Black 2 file formats (`narc.py`, `nsbtx.py`, `sdat.py`, ...) and patches the ROM (`build_rom.py`, `patches/`). Also the automatic checkers (`*_check.py`) and the DeSmuME test harness (`emu.py`, `playtest/`). |
| `src/` | Hand-written content: field scripts (Black 2's script language), text, trainers, wild tables, sprites, 3D objects. |
| `data/` | Generated and hand-tuned data (maps, zones, music, sprites, Emerald's overlays). |
| `notes/` | Research and design notes: Black 2's map, terrain and script formats, how each system was ported, and what was learned along the way. Start with `notes/GEN5_MAPS.md`, `notes/WORLD.md`, `notes/TOOLCHAIN.md` and `notes/TESTING.md`. |
| `viewer/` | Small HTML previews of the map plans. |

Some topics others may find useful: putting a Gen 3 region onto Gen 5's map matrix and 3D terrain, Gen 5 field scripts, adding a type (Fairy) to Black 2, porting GBA songs to the DS sound format, making a Black 2 hack run on flashcarts and 3DS loaders (`b2tools/patches/antipiracy.py`: loaders only switch off Black 2's anti-piracy for the original game), and checks for things real hardware rejects but DeSmuME allows (`b2tools/anim_tex_check.py`).

## Building

This was built and tested only on macOS (Apple Silicon). The scripts expect the checkout at `~/Documents/GitHub/HoennB2`.

You need:
- **Your own dumps** in `roms/`: Pokémon Black 2 (USA/Europe, game code IREO) as `black2_original.nds`, Pokémon Sapphire (Rev 1) as `sapphire_rev1_original.gba`, and Pokémon Emerald as `emerald_original.gba` for the Emerald version.
- **The decompilations** in `external/`: [pokeruby](https://github.com/pret/pokeruby), [pokeemerald](https://github.com/pret/pokeemerald) and [pokebw2](https://github.com/fuddlesworth/pokebw2) (its symbol files).
- **Tools** in `tools/`: [CTRMap-CE](https://github.com/ds-pokemon-hacking/CTRMap-CE) (`CTRMap.jar`) and its CTRMapV plugin, used to write 3D models.
- Java 21, Python 3 with NumPy and Pillow, LLVM/clang for the C patches, and GNU sed. `env.sh` shows how they are put on `PATH`. py-desmume is only needed for the tests.

Then:

```sh
source env.sh
zsh b2tools/rebuild_slice.sh                          # Sapphire  -> work/rom/hoenn.nds
HOENN_VERSION=ruby zsh b2tools/rebuild_slice.sh       # Ruby      -> work/rom_ruby/hoenn.nds
HOENN_VERSION=emerald zsh b2tools/rebuild_slice.sh    # Emerald   -> work/rom_emerald/hoenn.nds
```

A full build takes about 10 to 15 minutes per version and runs the automatic checkers at the end. `b2tools/bps.py make` turns a built game into a patch.

## License

The code (Python, shell, C, Java and the field scripts) is under the **MIT License** (see `LICENSE`): you can reuse it in your own projects, as long as the copyright and license notice stay with it. A credit link back here is appreciated.

The MIT License does **not** cover game content: the Pokémon games' text, maps, graphics, music and data remain the property of Nintendo, Game Freak, Creatures and The Pokémon Company. The community sprites stay under each artist's own terms (below). The artists' original sheets are not included; get them from the artists, with credit.

## Credits

- **Game Freak, Nintendo, Creatures and The Pokémon Company:** Pokémon Ruby, Sapphire, Emerald and Black 2.
- **[pret](https://github.com/pret):** the pokeruby and pokeemerald decompilations.
- **[pokebw2](https://github.com/fuddlesworth/pokebw2):** the Pokémon Black 2 / White 2 decompilation.

Community sprites (the NEW sprite set), used with credit:
- **hyo-oppa:** Brendan (overworld, battle front and back), Emerald's Brendan (battle front and back) and Wally (battle front).
- **CalculusNova:** Wally (overworld; CC BY-NC-SA 3.0).
- **Wolfang62:** Professor Birch (overworld).
- **DiegoWT:** May and Archie (originally commissioned by Zailens and Kyledove).
- **joojishibuki:** Maxie's battle sprite.
- **Kimmylube** and **AzureAquarian:** Team Aqua and Team Magma grunts.

`src/sprites/community/incoming/CREDITS.md` lists where each sheet came from and its terms.

Tools: **ds-decomp (dsd)** by AetiasHax, **CTRMap / CTRMapV** by HelloOO7, **apicula** by scurest, **DeSmuME**, **py-desmume** and **melonDS**, **Python, NumPy and Pillow**.

AI (Claude by Anthropic) was used to help code this project.

This is a non-commercial fan project. It is not affiliated with or endorsed by Nintendo, Game Freak, Creatures or The Pokémon Company. Please support the official games.
