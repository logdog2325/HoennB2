// Route117_PokemonDayCare (zone 561): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0362_room_Route117_PokemonDayCare.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch3b
#include "hoenn_trainers.h"  // ch3b
#include "hoenn_story.inc"  // ch3b
#include "scenes/ch3b_lib.inc"  // ch3b

    ScriptEntry Script_None
    ScriptEntry DC_Lady             // 2: Route117_PokemonDayCare_EventScript_1B2327 (data/scripts/day_care.inc)  // story:
    ScriptEntry DC_ZoneInit         // 3: Route117_PokemonDayCare_MapScript1_15C31F  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0


// ---- story (chapter Ch3 part 3b, ch3b agent 2026-10-07: Sapphire data/scripts/day_care.inc, the Day-Care Lady, and
// data/maps/Route117_PokemonDayCare/scripts.inc; generators must keep everything from this line on; entries above
// marked "// story:"). The lady (uid 1) is in data/story/ch3b.json; text lines 1-22 of 0362 (line 0 is the
// generator's). Map scripts: 1123_room_Route117_PokemonDayCare_init.s (zone init = script 3).
// Sapphire's specials -> Black 2's own Day Care commands, as its Route 3 Day Care uses them (global 1232 Script_2):
// GetDaycareState = DayCareCheckSpawnFlag (an Egg waiting) + DayCareGetPkmCount; ChooseSendDaycareMon =
// DayCareCallPokeSelect (a slot past the party = cancelled); StoreSelectedPokemonInDaycare = DayCareDeposit;
// GetNumLevelsGainedFromDaycare = DayCareCalcLevelGain; GetDaycareCost = DayCareCalcWithdrawCost; HasEnoughMoneyFor =
// MoneyCheck; PayMoneyFor = MoneySub; TakePokemonFromDaycare = DayCareWithdraw. ShowDaycareLevelMenu (each Pokémon's
// nickname, gender and level after the steps, then Cancel) is Black 2's list menu with Black 2's own entry lines
// (lines 19-21 = its "{name}♂ Lv. {level}" lines, 1232's message file 0616 lines 35-37). Sapphire shows no money box.
#define T_Raise 1
#define T_FineThen 2
#define T_WhichMon 3
#define T_WeWillRaise 4
#define T_FineComeAgain 5
#define T_OneMore 6
#define T_JustOne 7
#define T_WhatWillYouBattle 8
#define T_HusbandLooking 9
#define T_GrownBy 10
#define T_GoodToSee 11
#define T_TakeBack 12
#define T_Cost 13
#define T_NotEnoughMoney 14
#define T_Perfect 15
#define T_TookBack 16
#define T_OtherToo 17
#define T_TeamFull 18
#define T_MenuMale 19
#define T_MenuFemale 20
#define T_MenuNone 21
#define T_Cancel 22
#define DC_LADY 1
#define DC_SLOT C3B_A                   // VAR_0x8004: party slot (deposit) / Day Care slot (withdraw)
#define DC_N C3B_B
#define DC_SPECIES C3B_X
#define DC_FORM C3B_Z
#define DC_COST C3B_SEL

DC_ZoneInit:                        // Route117_PokemonDayCare_MapScript1_15C31F
    h_setflag FLAG_LANDMARK_POKEMON_DAYCARE
#ifdef HOENN_TEST_CH3B
    h_getpartysize DC_N             // TEST ONLY (HOENN_TEST_CH3B): a second Pokémon to leave here, and money
    h_goto_if_ne DC_N, 1, L_DC_TestDone
    PokePartyAdd DC_N, SPECIES_MARILL, 0, 20
    MoneyAdd 20000
L_DC_TestDone:
#endif
    VMHalt

DC_Lady:                            // Route117_PokemonDayCare_EventScript_1B2327
    c3_talk
    DayCareCheckSpawnFlag DC_N
    h_goto_if_eq DC_N, 1, L_DC_EggWaiting
    DayCareGetPkmCount DC_N
    h_goto_if_eq DC_N, 1, L_DC_OneMon
    h_goto_if_eq DC_N, 2, L_DC_TwoMons
    h_yesno T_Raise, DC_N           // I'm the Day-Care Lady. We can raise Pokémon for you. Would you like us to raise one?
    h_goto_if_yes DC_N, L_DC_Deposit
    h_msgbox T_FineThen             // Oh, fine, then. Come again.
    h_release
L_DC_EggWaiting:                    // Route117_PokemonDayCare_EventScript_1B2407
    h_msgbox T_HusbandLooking       // My husband was looking for you.
    h_release

L_DC_Deposit:                       // Route117_PokemonDayCare_EventScript_1B236C
    PokePartyGetCount DC_N, 1       // GetNumValidDaycarePartyMons (no Eggs)
    h_goto_if_eq DC_N, 1, L_DC_JustOne
    h_msgbox T_WhichMon             // Which Pokémon should we raise for you?
    h_closemessage
    DayCareCallPokeSelect DC_SLOT   // fadescreen + ChooseSendDaycareMon + waitstate
    h_getpartysize DC_N
    h_goto_if_eq_var DC_SLOT, DC_N, L_DC_FineComeAgain      // cancelled: a slot past the party (0x8004 255)
    h_goto_if_gt DC_SLOT, 5, L_DC_FineComeAgain
    PokePartyIsEgg DC_N, DC_SLOT    // (Sapphire's Day Care party menu cannot pick an Egg)
    h_goto_if_eq DC_N, 1, L_DC_FineComeAgain
    // CountAlivePartyMonsExceptSelectedOne == 0: with one Pokémon able to battle, it must not be the chosen one
    PokePartyGetCount DC_N, 2
    h_goto_if_ge DC_N, 2, L_DC_CanDeposit
    h_goto_if_eq DC_N, 0, L_DC_WhatWillYouBattle
    PokePartyGetMemberByType DC_N, 2    // the first Pokémon able to battle
    h_goto_if_eq_var DC_N, DC_SLOT, L_DC_WhatWillYouBattle
L_DC_CanDeposit:
    PokePartyGetSpecies DC_SPECIES, DC_SLOT
    PokePartyGetForme DC_FORM, DC_SLOT
    h_waitse
    PokeVoicePlay DC_SPECIES, DC_FORM
    WordSetPartyPokeName 1, DC_SLOT
    h_msgbox T_WeWillRaise          // Fine, we'll raise your <mon> for a while. Come back for it later.
    h_waitmoncry
    DayCareDeposit DC_SLOT          // StoreSelectedPokemonInDaycare (incrementgamestat GAME_STAT_USED_DAYCARE: Black 2's
    RecordAdd 24, 1                 // own record of Day Care use, as 1232)
    DayCareGetPkmCount DC_N
    h_goto_if_eq DC_N, 1, L_DC_AskOneMore
    h_release
L_DC_AskOneMore:                    // Route117_PokemonDayCare_EventScript_1B23DA
    h_yesno T_OneMore, DC_N         // We can raise two of your Pokémon. Would you like us to raise one more?
    h_goto_if_yes DC_N, L_DC_Deposit
L_DC_FineComeAgain:                 // Route117_PokemonDayCare_EventScript_1B23D0
    h_msgbox T_FineComeAgain        // Fine. Come again.
    h_release
L_DC_JustOne:                       // Route117_PokemonDayCare_EventScript_1B23F3
    h_msgbox T_JustOne              // Oh? But you have just one Pokémon. Come back another time.
    h_release
L_DC_WhatWillYouBattle:             // Route117_PokemonDayCare_EventScript_1B23FD
    h_msgbox T_WhatWillYouBattle    // If you leave me that Pokémon, what will you battle with? ...
    h_release

L_DC_OneMon:                        // Route117_PokemonDayCare_EventScript_1B242B
    h_msgbox T_GoodToSee            // Ah, it's you! Good to see you. Your Pokémon can only be doing good!
    h_setvar DC_SLOT, 0
    VMCall Sub_DC_LevelsGained
    h_yesno T_OneMore, DC_N
    h_goto_if_yes DC_N, L_DC_Deposit
    h_yesno T_TakeBack, DC_N        // Will you take your Pokémon back?
    h_goto_if_yes DC_N, L_DC_Withdraw
    VMJump L_DC_FineComeAgain
L_DC_TwoMons:                       // Route117_PokemonDayCare_EventScript_1B2558
    h_msgbox T_GoodToSee
    h_setvar DC_SLOT, 0
    VMCall Sub_DC_LevelsGained
    h_setvar DC_SLOT, 1
    VMCall Sub_DC_LevelsGained
    h_yesno T_TakeBack, DC_N
    h_goto_if_yes DC_N, L_DC_Withdraw
    h_msgbox T_FineComeAgain        // (Route117_PokemonDayCare_Text_1B2A76)
    h_release

Sub_DC_LevelsGained:                // Route117_PokemonDayCare_EventScript_1B241A
    DayCareCalcLevelGain DC_N, DC_SLOT
    h_goto_if_eq DC_N, 0, L_DC_NoLevels
    WordSetDaycarePokeName 1, DC_SLOT
    WordSetNumber 2, DC_N, 3
    h_msgbox T_GrownBy              // By level, your <mon> has grown by <n>.
L_DC_NoLevels:
    VMReturn

L_DC_Withdraw:                      // Route117_PokemonDayCare_EventScript_1B2469
    h_getpartysize DC_N
    h_goto_if_eq DC_N, 6, L_DC_TeamFull
    h_setvar DC_SLOT, 0
    DayCareGetPkmCount DC_N
    h_goto_if_eq DC_N, 1, L_DC_Cost
    ListMenu_AnchorTopRight 31, 9, 0, 1, DC_SLOT    // ShowDaycareLevelMenu (B = Cancel)
    h_setvar DC_N, 0
L_DC_MenuEntry:
    DayCareCalcNewLevel DC_COST, DC_N
    WordSetDaycarePokeName 0, DC_N
    WordSetNumber 1, DC_COST, 3
    DayCareGetSexForNamePrint DC_SPECIES, 0, DC_N
    h_goto_if_eq DC_SPECIES, 1, L_DC_MenuMale
    h_goto_if_eq DC_SPECIES, 2, L_DC_MenuFemale
    ListMenuAdd T_MenuNone, 65535, DC_N
    VMJump L_DC_MenuNext
L_DC_MenuMale:
    ListMenuAdd T_MenuMale, 65535, DC_N
    VMJump L_DC_MenuNext
L_DC_MenuFemale:
    ListMenuAdd T_MenuFemale, 65535, DC_N
L_DC_MenuNext:
    h_addvar DC_N, 1
    h_goto_if_lt DC_N, 2, L_DC_MenuEntry
    ListMenuAdd T_Cancel, 65535, 2
    ListMenuShow
    h_goto_if_ge DC_SLOT, 2, L_DC_FineComeAgain     // Cancel (2) or B (65534)
L_DC_Cost:                          // Route117_PokemonDayCare_EventScript_1B24A8 (GetDaycareCost)
    DayCareCalcWithdrawCost DC_COST, DC_SLOT
    WordSetDaycarePokeName 1, DC_SLOT
    WordSetNumber 2, DC_COST, 5
    h_yesno T_Cost, DC_N            // If you want your <mon> back, it will cost $<n>.
    h_goto_if_no DC_N, L_DC_FineComeAgain
    MoneyCheck DC_N, DC_COST        // HasEnoughMoneyFor
    h_goto_if_eq DC_N, 1, L_DC_PayAndTake
    h_msgbox T_NotEnoughMoney       // You don't have enough money...
    h_release
L_DC_PayAndTake:                    // Route117_PokemonDayCare_EventScript_1B24DE
    h_closemessage
    h_applymovement DC_LADY, Mv_DC_FetchMon
    h_waitmovement
    DayCareGetSpecies DC_SPECIES, DC_SLOT
    DayCareGetForme DC_FORM, DC_SLOT
    WordSetDaycarePokeName 1, DC_SLOT
    MoneySub DC_COST                // PayMoneyFor
    h_playse SE_SHOP
    h_msgbox T_Perfect              // Perfect! Here's your Pokémon.
    h_waitse
    PokeVoicePlay DC_SPECIES, DC_FORM
    h_buffer_player
    h_msgbox T_TookBack             // <player> took back <mon> from the Day-Care Lady.
    h_waitmoncry
    DayCareWithdraw DC_SLOT         // TakePokemonFromDaycare
    DayCareGetPkmCount DC_N
    h_goto_if_eq DC_N, 1, L_DC_OtherToo
    VMJump L_DC_FineComeAgain
L_DC_OtherToo:                      // Route117_PokemonDayCare_EventScript_1B2520
    h_yesno T_OtherToo, DC_N        // Will you take back the other one, too?
    h_goto_if_yes DC_N, L_DC_Withdraw
    VMJump L_DC_FineComeAgain
L_DC_TeamFull:                      // Route117_PokemonDayCare_EventScript_1B2539
    h_msgbox T_TeamFull             // Your Pokémon team is full. Make room, then come see me.
    h_release

    .balign 4, 0
Mv_DC_FetchMon:                     // Route117_PokemonDayCare_Movement_1B2543 (she fetches it from the back room)
    delay_16 2
    face_left
    delay_16 2
    face_right
    delay_16 2
    face_up
    walk_slow_up
    set_invisible
    delay_16 5
    face_down
    set_visible
    walk_slow_down
    step_end
