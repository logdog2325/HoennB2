"""Sapphire's in-game trades on Black 2's own in-game trade system (chapter Ch1 wrote it for Rustboro's trade).

Black 2 keeps its in-game trades in a/1/6/3: 31 files of 27 u32 each (read from the ROM, no decomp source). Fields, as
Black 2's own entries 24-30 use them (b2:1040.s trade 24 = Petilil "Petulia" for Cottonee, OT Calla):
   0 the entry's number      1 species offered      2 form      3 level      4-9 IVs (HP Atk Def Spe SpA SpD: Petilil's
  31 is the 5th = Sp. Atk, Gigalith's (26) the 2nd = Atk; Sapphire's struct InGameTrade has the same order)
  10 ability (0 first, 1 second)   11 nature   12 sex (0 male, 1 female)   13 OT ID (32 bit)
  14-18 contest stats (all 0 in Black 2; Gen 3/4 order cool beauty cute smart tough)   19 held item   20 OT gender
  21 (0 in every entry; left 0)   22 language (2 English)   23 species wanted   24 sex wanted (2 any)
  25/26 lines of system text 37 (0037_field_trade_input_load_name.txt) with the nickname / the OT's name.
Scripts: FieldTradeGetSpecies, CallPokeSelect, FieldTradeCheck (0 = the wanted species), FieldTradeStart (b2:1040.s).

Entries 24-30 are Black 2's own trades (Aspertia..Undella), unused in Hoenn, so Sapphire's trades take them:
  24 Rustboro (Sapphire gIngameTrades[0], RustboroCity_House1): Makuhita "Makit" for Slakoth, OT Elyssa.
  25 is free for Fortree's (Skitty "Skitit" for Pikachu); 26 = Pacifidlog's (Corsola "Coroso" for Bellossom, Ch12).
Names: src/text/overrides.json, system/0037 lines 48/49 (and 50-53 for 25/26).

Sapphire differences Black 2 cannot keep: the level is fixed in the entry (Sapphire gives the level of the Pokemon the
player trades away: CreateInGameTradePokemon); sheen and the mail (Rustboro has none) have no field."""
import os, struct, sys

ARC = 163                      # a/1/6/3
ITEM_X_ATTACK = 57             # external/pokebw2/include/constants/items.h
SPECIES_MAKUHITA, SPECIES_SLAKOTH = 296, 287
SPECIES_CORSOLA, SPECIES_BELLOSSOM = 222, 182
SPECIES_SKITTY, SPECIES_PIKACHU = 300, 25

# Sapphire src/trade.c gIngameTrades[0] (ENGLISH): ivs 5,5,4,4,4,4; secondAbility TRUE; otId 49562; stats 5,5,5,5,30;
# personality 0x9C40 (nature 40000 % 25 = 0 Hardy; gender byte 0x40 >= Makuhita's 63 threshold: male); X Attack;
# otName ELYSSA, otGender MALE; playerSpecies Slakoth.
TRADES = {
    24: dict(species=SPECIES_MAKUHITA, level=5, ivs=(5, 5, 4, 4, 4, 4), ability=1, nature=0, sex=0, ot_id=49562,
             contest=(5, 5, 5, 5, 30), item=ITEM_X_ATTACK, ot_gender=0, wanted=SPECIES_SLAKOTH, wanted_sex=2),
    # Sapphire gIngameTrades[1] (Fortree, FortreeCity_House1; chapter Ch7, ch7 agent): Skitty "Skitit" for a Pikachu, OT
    # Darrell (female), ivs 5,4,4,5,4,4, first ability, otId 2259, stats 5,5,30,5,5 (cute), personality 0x498A2E17
    # (nature 10 Timid, gender byte 23 < Skitty's 191 threshold: female). Sapphire's Glitter Mail has no field in Black 2:
    # no held item. The level is fixed (Sapphire: the level of the Pikachu handed over): 15.
    25: dict(species=SPECIES_SKITTY, level=15, ivs=(5, 4, 4, 5, 4, 4), ability=0, nature=10, sex=1, ot_id=2259,
             contest=(5, 5, 30, 5, 5), item=0, ot_gender=1, wanted=SPECIES_PIKACHU, wanted_sex=2),
    # Sapphire gIngameTrades[2] (Pacifidlog, PacifidlogTown_House3; chapter Ch12, ch6 agent): Corsola "Coroso" for a
    # Bellossom, OT Lane (female), ivs 4,4,5,4,4,5, second ability, otId 50183, stats 5,30,5,5,5 (beauty), personality
    # 0x4C970B7F (nature 20 Calm, gender byte 0x7F < Corsola's 191 threshold: female). Sapphire's Tropic Mail has no
    # field in Black 2: no held item. The level is fixed (Sapphire: the level of the Bellossom handed over).
    26: dict(species=SPECIES_CORSOLA, level=30, ivs=(4, 4, 5, 4, 4, 5), ability=1, nature=20, sex=1, ot_id=50183,
             contest=(5, 30, 5, 5, 5), item=0, ot_gender=1, wanted=SPECIES_BELLOSSOM, wanted_sex=2),
}

def entry(n, t):
    return struct.pack('<27I', n, t['species'], 0, t['level'], *t['ivs'], t['ability'], t['nature'], t['sex'],
                       t['ot_id'], *t['contest'], t['item'], t['ot_gender'], 0, 2, t['wanted'], t['wanted_sex'],
                       2 * n, 2 * n + 1)

def apply(files):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    import narcio
    arc = narcio.load(files, ARC)
    assert len(arc) == 31 and all(len(e) == 108 for e in arc), [len(e) for e in arc]
    for n, t in TRADES.items():
        old = struct.unpack('<27I', arc[n])
        assert old[0] == n and old[25:] == (2 * n, 2 * n + 1), old     # Black 2's layout as read above
        arc[n] = entry(n, t)
    narcio.save(files, ARC, arc)
    return 'in-game trades: ' + ', '.join(f'{n}: species {t["species"]} Lv {t["level"]} for {t["wanted"]}'
                                          for n, t in TRADES.items())
