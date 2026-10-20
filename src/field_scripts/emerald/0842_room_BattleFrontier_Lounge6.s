// BattleFrontier_Lounge6 (zone 421; header scripts 842 -> own file 2078), Pokémon Emerald NDS only (em_trades,
// 2026-10-19). pokeemerald data/maps/BattleFrontier_Lounge6/scripts.inc: the Beauty's in-game trade (pokeemerald
// INGAME_TRADE_MEOWTH: her Meowth "Meowow" for a Skitty) on Black 2's own in-game trade 27 (b2tools/patches/trades.py
// EMERALD_TRADES; names on lines 54/55 of system text 37, src/text/emerald/overrides_emerald_trades.json), written like
// chapter Ch1's Rustboro trade (1170_room_RustboroCity_House1.s). The room: data/interior_layouts/BattleFrontier_Lounge6.json,
// people data/interiors/emerald/421.json (uid = script = Emerald's local id). Messages:
// src/text/script/emerald/0650_room_BattleFrontier_Lounge6.txt (pokeemerald's words, converter/gen3text.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

#define T_WouldYouLikeToTrade 0             // My Pokémon is a {STR_VAR_2}. ... trade me a {STR_VAR_1} for my {STR_VAR_2}?
#define T_PromiseIllBeGoodToIt 1            // Oh, it's adorable! ... I hope you'll be good to my {STR_VAR_2}, too!
#define T_DontTradeForAnythingButMon 2      // Oh, I'm sorry! I don't intend to trade for anything but a {STR_VAR_1}.
#define T_WellThatsFineToo 3                // Oh, you won't? Well, that's fine, too. Please come visit us again.
#define T_SkittySoMuchCuter 4               // Giggle! A Skitty is so much cuter than I had imagined. I'm delighted!
#define L6_TRADE 27                         // Black 2 in-game trade 27
#define L6_WANTED SPECIES_SKITTY
#define L6_OFFERED SPECIES_MEOWTH
#define L6_SLOT 0x8020                      // party slot picked (as Black 2's own trade scripts, b2:1040.s)
#define L6_OK 0x8021                        // 1 = a Pokémon was picked
#define L6_CHECK 0x8022                     // FieldTradeCheck: 0 = the wanted species

    ScriptEntry L6_Trader                   // 1: BattleFrontier_Lounge6_EventScript_Trader (the Beauty)
    ScriptEntriesEnd

L6_Trader:                                  // lock, faceplayer
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_BATTLE_FRONTIER_TRADE_DONE, L_L6_Completed
    h_bufferspeciesname 1, L6_WANTED        // GetInGameTradeSpeciesInfo: STR_VAR_1 the wanted species, STR_VAR_2
    FieldTradeGetSpecies HLIB_TMP, L6_TRADE //   the offered one (read from the trade)
    h_bufferspeciesname 2, HLIB_TMP
    h_yesno T_WouldYouLikeToTrade, HLIB_TMP
    h_goto_if_no HLIB_TMP, L_L6_Decline
    MsgWinCloseAll
    WorkSetConst L6_SLOT, 0
    WorkSetConst L6_OK, 0
    CallPokeSelect 0, L6_OK, L6_SLOT, 0     // ChoosePartyMon
    h_goto_if_ne L6_OK, 1, L_L6_Decline     // (none picked: PARTY_NOTHING_CHOSEN)
    WorkSetConst L6_CHECK, 0
    FieldTradeCheck L6_CHECK, L6_TRADE, L6_SLOT   // GetTradeSpecies + compare with the wanted species
    h_goto_if_ne L6_CHECK, 0, L_L6_NotRequested
    FieldTradeStart L6_TRADE, L6_SLOT       // CreateInGameTradePokemon + DoInGameTradeScene
    h_bufferspeciesname 1, L6_WANTED        // (the buffers again after the trade scene)
    h_bufferspeciesname 2, L6_OFFERED
    h_msgbox T_PromiseIllBeGoodToIt
    h_setflag FLAG_BATTLE_FRONTIER_TRADE_DONE
    VMJump L_L6_Release
L_L6_Decline:
    h_msgbox T_WellThatsFineToo
    VMJump L_L6_Release
L_L6_NotRequested:
    h_bufferspeciesname 1, L6_WANTED        // bufferspeciesname STR_VAR_1, VAR_0x8009
    h_msgbox T_DontTradeForAnythingButMon
    VMJump L_L6_Release
L_L6_Completed:
    h_msgbox T_SkittySoMuchCuter
L_L6_Release:
    WorkSetConst L6_CHECK, 0
    WorkSetConst L6_OK, 0
    WorkSetConst L6_SLOT, 0
    h_release
    .balign 4, 0
