// MauvilleCity_GameCorner (zone 237): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0302_room_MauvilleCity_GameCorner.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch3b
#include "hoenn_trainers.h"  // ch3b
#include "hoenn_story.inc"  // ch3b
#include "scenes/ch3b_lib.inc"  // ch3b

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry GC_CoinsClerk       // 3: object 3  // story:
    ScriptEntry GC_PrizeCorner      // 4: objects 4 (dolls) and 9 (TMs)  // story:
    ScriptEntry GC_Girl             // 5: object 5 (the starter Doll)  // story:
    ScriptEntry GC_PokefanM         // 6: object 6  // story:
    ScriptEntry GC_OldMan           // 7: object 7  // story:
    ScriptEntry GC_Cook             // 8: object 8  // story:
    ScriptEntry GC_Man              // 9: object 10  // story:
    ScriptEntry GC_Maniac           // 10: object 11  // story:
    ScriptEntry GC_Woman            // 11: object 12  // story:
    ScriptEntry GC_SlotMachine      // 12: the twelve slot machines (SlotMachine0-11)  // story:
    ScriptEntry GC_Roulette         // 13: the two roulette tables (six tiles each: 1C407E, 1C40AC)  // story:
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 1, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch3 part 3b, ch3b agent 2026-10-07: Sapphire data/maps/MauvilleCity_GameCorner/scripts.inc;
// generators must keep everything from this line on; entries above marked "// story:"). People and machines:
// data/story/ch3b.json (uid = Sapphire local id); text lines 2-19 of 0302 (0-1 are the generated people's).
// Black 2 has no Coins, no Slots and no Roulette (no coin count in its save, no coin/slot/roulette script command:
// external/pokebw2/tools/scripts/field_commands.json). The Game Corner keeps Sapphire's people and lines and plays
// nothing, as the Contest counters register nobody (decision 2026-10-07): the Coins clerk and the prize ladies greet
// you (and the clerk says you need a Coin Case when you have none), the machines say you cannot play without a Coin
// Case and do nothing with one, the 20 Coins of the Pokéfan (FLAG_RECEIVED_20_COINS) are never given. The girl's
// starter Doll is a decoration, which Black 2 cannot store: she takes Sapphire's own no-room path (Common_EventScript_
// NoRoomForDecor + "You want it, but not right now?"). Asked in ch3b's report: a coin counter (a saved work) would
// let the clerk sell Coins and the prize corner give its TMs.
#define T_ThisIsGameCorner 2
#define T_NeedCoinCase 3
#define T_ExchangeForPrizes 4
#define T_TwoDolls 5
#define T_NoRoomTreecko 6
#define T_NoRoomTorchic 7
#define T_NoRoomMudkip 8
#define T_WantItNotNow 9
#define T_DontBeNegative 10
#define T_CantWinJackpot 11
#define T_NeedCoinCaseNextDoor 12
#define T_SomethingForEveryone 13
#define T_RouletteRates 14
#define T_LoseTrackOfTime 15
#define T_UpTo3Coins 16
#define T_StopOn7 17
#define T_SlotsInfo 18
#define T_CantPlayNoCase 19

GC_CoinsClerk:                      // MauvilleCity_GameCorner_EventScript_CoinsClerk
    c3_talk
    h_msgbox T_ThisIsGameCorner     // This is Mauville Game Corner.
    h_checkitem ITEM_COIN_CASE, 1, C3B_A
    h_goto_if_eq C3B_A, 1, L_GC_End
    h_msgbox T_NeedCoinCase         // Okay, you wanted some Coins for the games? But you don't have a Coin Case ...
L_GC_End:
    h_release

GC_PrizeCorner:                     // MauvilleCity_GameCorner_EventScript_PrizeCornerDolls / PrizeCornerTMs
    c3_talk
    h_msgbox T_ExchangeForPrizes    // Welcome. You can exchange your Coins for prizes here.
    h_release

GC_Girl:                            // MauvilleCity_GameCorner_EventScript_Girl
    c3_talk
    h_goto_if_set FLAG_RECEIVED_STARTER_DOLL, L_GC_GirlReceived
    h_yesno T_TwoDolls, C3B_A       // I made a mistake and got two of the same Dolls. Would you like one of them?
    h_goto_if_no C3B_A, L_GC_GirlDecline
    h_goto_if_eq VAR_STARTER_MON, 1, L_GC_TorchicDoll
    h_goto_if_eq VAR_STARTER_MON, 2, L_GC_MudkipDoll
    h_msgbox T_NoRoomTreecko        // checkdecorspace DECOR_TREECKO_DOLL fails: Common_EventScript_NoRoomForDecor
    VMJump L_GC_GirlNotNow
L_GC_TorchicDoll:
    h_msgbox T_NoRoomTorchic
    VMJump L_GC_GirlNotNow
L_GC_MudkipDoll:
    h_msgbox T_NoRoomMudkip
L_GC_GirlNotNow:                    // MauvilleCity_GameCorner_EventScript_NoRoomForStarterDoll
    h_msgbox T_WantItNotNow         // Huh? You want it, but not right now?
    h_release
L_GC_GirlDecline:
    h_msgbox T_DontBeNegative       // Oh, don't be so negative! You can have this!
    h_release
L_GC_GirlReceived:
    h_msgbox T_CantWinJackpot
    h_release

// the people at the machines turn back to them after talking (MauvilleCity_GameCorner_EventScript_NPCReturnToSlots)
GC_PokefanM:                        // MauvilleCity_GameCorner_EventScript_PokefanM (object 6, FACE_DOWN)
    c3_talk
    h_checkitem ITEM_COIN_CASE, 1, C3B_A
    h_goto_if_eq C3B_A, 1, L_GC_PokefanMNormal
    h_msgbox T_NeedCoinCaseNextDoor // Hey, kid, if you want to play here, you need a Coin Case. ...
    VMJump L_GC_PokefanMBack
L_GC_PokefanMNormal:                // (the 20 Coins: no Coins in Black 2)
    h_msgbox T_SomethingForEveryone // Mauville has something for everyone. For me, it's the Game Corner.
L_GC_PokefanMBack:
    ActorMsgClose
    h_turnobject 6, 1
    h_release
GC_OldMan:                          // object 7, FACE_LEFT
    c3_say_turn_back T_RouletteRates, 7, 2
GC_Cook:                            // object 8, FACE_RIGHT
    c3_say_turn_back T_LoseTrackOfTime, 8, 3
GC_Man:                             // object 10, FACE_RIGHT
    c3_say_turn_back T_UpTo3Coins, 10, 3
GC_Maniac:                          // object 11, FACE_LEFT
    c3_say_turn_back T_StopOn7, 11, 2
GC_Woman:                           // object 12, FACE_LEFT
    c3_say_turn_back T_SlotsInfo, 12, 2

GC_SlotMachine:                     // MauvilleCity_GameCorner_EventScript_SlotMachine0-11 (lockall; playslotmachine)
GC_Roulette:                        // MauvilleCity_GameCorner_EventScript_1C407E / 1C40AC (playroulette)
    h_lock
    h_checkitem ITEM_COIN_CASE, 1, C3B_A
    h_goto_if_eq C3B_A, 1, L_GC_MachineEnd
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info T_CantPlayNoCase  // MauvilleCity_GameCorner_EventScript_NoCoinCase
    h_closemessage
L_GC_MachineEnd:
    h_release
    .balign 4, 0
