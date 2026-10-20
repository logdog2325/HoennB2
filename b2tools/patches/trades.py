"""The version's in-game trades on Black 2's own in-game trade system (chapter Ch1 wrote it for Rustboro's trade).
Sapphire and Ruby: pokeruby's three (gIngameTrades); Emerald: pokeemerald's four (src/data/trade.h sIngameTrades;
em_trades 2026-10-19). TRADES is the version's table (b2tools/version.py); gen_docs.py's levels page reads it.

Black 2 keeps its in-game trades in a/1/6/3: 31 files of 27 u32 each (read from the ROM, no decomp source). Fields, as
Black 2's own entries 24-30 use them (b2:1040.s trade 24 = Petilil "Petulia" for Cottonee, OT Calla):
   0 the entry's number      1 species offered      2 form      3 level      4-9 IVs (HP Atk Def Spe SpA SpD: Petilil's
  31 is the 5th = Sp. Atk, Gigalith's (26) the 2nd = Atk; Sapphire's struct InGameTrade has the same order)
  10 ability (0 first, 1 second)   11 nature   12 sex (0 male, 1 female)   13 OT ID (32 bit)
  14-18 contest stats (all 0 in Black 2; Gen 3/4 order cool beauty cute smart tough)   19 held item   20 OT gender
  21 (0 in every entry; left 0)   22 language (2 English)   23 species wanted   24 sex wanted (2 any)
  25/26 lines of system text 37 (0037_field_trade_input_load_name.txt) with the nickname / the OT's name.
  (pokebw2 src/ov033/fld_trade.c EventFieldTrade_CreatePkm reads them in this order.)
Scripts: FieldTradeGetSpecies, CallPokeSelect, FieldTradeCheck (0 = the wanted species), FieldTradeStart (b2:1040.s).

Entries 24-30 are Black 2's own trades (Aspertia..Undella), unused in Hoenn, so Hoenn's trades take them:
  Sapphire/Ruby (pokeruby gIngameTrades 0-2):
  24 Rustboro (RustboroCity_House1): Makuhita "Makit" for Slakoth, OT Elyssa.
  25 Fortree (FortreeCity_House1, Ch7): Skitty "Skitit" for Pikachu, OT Darrell.
  26 Pacifidlog (PacifidlogTown_House3, Ch12): Corsola "Coroso" for Bellossom, OT Lane.
  Names: src/text/overrides.json, system/0037 lines 48-53.
  Emerald (pokeemerald sIngameTrades, INGAME_TRADE_SEEDOT/PLUSLE/HORSEA/MEOWTH), the same houses and one more:
  24 Rustboro: Seedot "Dots" for Ralts, OT Kobe.     25 Fortree: Plusle "Pluses" for Volbeat, OT Roman.
  26 Pacifidlog: Horsea "Seasor" for Bagon, OT Skylar.
  27 Battle Frontier (BattleFrontier_Lounge6, Emerald only): Meowth "Meowow" for Skitty, OT Isis.
  Names: src/text/emerald/overrides_emerald_trades.json, system/0037 lines 48-55 (2n, 2n + 1).
Gen 3 names are written in title case, as Sapphire's (DOTS -> Dots).

Gen 3 differences Black 2 cannot keep: the level is fixed in the entry (Gen 3 gives the level of the Pokemon the player
trades away: CreateInGameTradePokemon); sheen and the mail (Gen 3's Glitter/Tropic/Wood/Wave/Retro Mail have no Black 2
item: no held item) have no field. Emerald's levels: the lowest level of the wanted species in pokeemerald's wild
tables (wild_encounters.json), the Pokemon a player most likely hands over, on this game's curve (data/level_scaling.json:
Bagon 25 -> 26): Ralts 4 (Route 102), Volbeat 13 (Route 117), Bagon 26 (Meteor Falls B1F 2R), Skitty 7 (Route 116).
Nature = personality % 25 and sex = male unless the species' gender ratio > the personality's low byte (Gen 3's
GetNatureFromPersonality / GetGenderFromSpeciesAndPersonality), as below."""
import os, struct, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import version  # noqa: E402

ARC = 163                      # a/1/6/3
ITEM_X_ATTACK = 57             # external/pokebw2/include/constants/items.h
ITEM_CHESTO_BERRY = 150
SPECIES_MAKUHITA, SPECIES_SLAKOTH = 296, 287
SPECIES_CORSOLA, SPECIES_BELLOSSOM = 222, 182
SPECIES_SKITTY, SPECIES_PIKACHU = 300, 25
SPECIES_SEEDOT, SPECIES_RALTS = 273, 280
SPECIES_PLUSLE, SPECIES_VOLBEAT = 311, 313
SPECIES_HORSEA, SPECIES_BAGON = 116, 371
SPECIES_MEOWTH = 52

# Sapphire src/trade.c gIngameTrades[0] (ENGLISH): ivs 5,5,4,4,4,4; secondAbility TRUE; otId 49562; stats 5,5,5,5,30;
# personality 0x9C40 (nature 40000 % 25 = 0 Hardy; gender byte 0x40 >= Makuhita's 63 threshold: male); X Attack;
# otName ELYSSA, otGender MALE; playerSpecies Slakoth.
SAPPHIRE_TRADES = {
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

# pokeemerald src/data/trade.h sIngameTrades (conditions = cool beauty cute smart tough; sheen 10 each: no field). The four
# species have PERCENT_FEMALE(50) = 127. otId is 32 bit in Emerald (73996 = TID 08460 + SID 1, 91481 = TID 25945 + SID 1):
# written whole (Black 2's field is 32 bit; both games show the low 16 bits).
EMERALD_TRADES = {
    # [INGAME_TRADE_SEEDOT] RustboroCity_House1 (the Camper): DOTS, ivs 5,4,5,4,4,4, abilityNum 1 (Early Bird), otId 38726,
    # conditions 30,5,5,5,5 (cool), personality 0x84 (nature 132 % 25 = 7 Relaxed; 0x84 >= 127: male), Chesto Berry,
    # KOBE male, for a Ralts.
    24: dict(species=SPECIES_SEEDOT, level=4, ivs=(5, 4, 5, 4, 4, 4), ability=1, nature=7, sex=0, ot_id=38726,
             contest=(30, 5, 5, 5, 5), item=ITEM_CHESTO_BERRY, ot_gender=0, wanted=SPECIES_RALTS, wanted_sex=2),
    # [INGAME_TRADE_PLUSLE] FortreeCity_House1 (the Ninja Boy): PLUSES, ivs 4,4,4,5,5,4, abilityNum 0 (Plus), otId 73996,
    # conditions 5,5,30,5,5 (cute), personality 0x6F (nature 111 % 25 = 11 Hasty; 0x6F < 127: female), Wood Mail (none),
    # ROMAN male, for a Volbeat.
    25: dict(species=SPECIES_PLUSLE, level=13, ivs=(4, 4, 4, 5, 5, 4), ability=0, nature=11, sex=1, ot_id=73996,
             contest=(5, 5, 30, 5, 5), item=0, ot_gender=0, wanted=SPECIES_VOLBEAT, wanted_sex=2),
    # [INGAME_TRADE_HORSEA] PacifidlogTown_House3 (the man): SEASOR, ivs 5,4,4,4,5,4, abilityNum 0 (Swift Swim), otId
    # 46285, conditions 5,5,5,5,30 (tough), personality 0x7F (nature 127 % 25 = 2 Brave; 0x7F >= 127: male), Wave Mail
    # (none), SKYLAR male, for a Bagon.
    26: dict(species=SPECIES_HORSEA, level=26, ivs=(5, 4, 4, 4, 5, 4), ability=0, nature=2, sex=0, ot_id=46285,
             contest=(5, 5, 5, 5, 30), item=0, ot_gender=0, wanted=SPECIES_BAGON, wanted_sex=2),
    # [INGAME_TRADE_MEOWTH] BattleFrontier_Lounge6 (the Beauty): MEOWOW, ivs 4,5,4,5,4,4, abilityNum 0 (Pickup), otId
    # 91481, conditions 5,5,5,30,5 (smart), personality 0x8B (nature 139 % 25 = 14 Naive; 0x8B >= 127: male), Retro Mail
    # (none), ISIS female, for a Skitty.
    27: dict(species=SPECIES_MEOWTH, level=7, ivs=(4, 5, 4, 5, 4, 4), ability=0, nature=14, sex=0, ot_id=91481,
             contest=(5, 5, 5, 30, 5), item=0, ot_gender=1, wanted=SPECIES_SKITTY, wanted_sex=2),
}

TRADES = EMERALD_TRADES if version.is_emerald() else SAPPHIRE_TRADES

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
