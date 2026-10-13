// LilycoveCity_DepartmentStoreRooftop (zone 182): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0240_room_LilycoveCity_DepartmentStoreRooftop.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch8a
#include "hoenn_story.inc"  // ch8a
#include "scenes/ch8a_lib.inc"  // ch8a

    ScriptEntry Script_1
    ScriptEntry RT_Man                  // 2: object 1  // story:
    ScriptEntry RT_SaleWoman            // 3: object 3 (the rooftop sale)  // story:
    ScriptEntry RT_VendingMachine       // 4: signs (9,1) and (10,1)  // story:
    ScriptEntriesEnd

Script_1:                                      // man_4 (7,5), Sapphire LilycoveCity_DepartmentStoreRooftop_EventScript_ThirstyMan
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
    .balign 4, 0

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/LilycoveCity_DepartmentStoreRooftop/scripts.inc. The thirsty man is the shops agent's (above).
// People and signs: data/story/ch8a.json. Lines 1-14 of the text file.
// The clear-out sale: Sapphire shows the sale woman only while a Pokénews flash says the sale is on
// (OnTransition: getpricereduction 3). Black 2 has no Pokénews, and the user decided (2026-10-06) that the sale lady
// stands there with Sapphire's lines, selling nothing (no Secret Base decorations): so she is always there, her two
// lines are Sapphire's, and the man says his "been waiting for the sale" line.
// The Vending Machine follows Black 2's own vending flow (field script 0010: money window, list menu, pay, item).
#define T_SetDates 1
#define T_WaitingForSale 2
#define T_HowMayIServeYou 3
#define T_PleaseComeAgain 4
#define T_WhichDrink 5
#define T_FreshWater 6
#define T_SodaPop 7
#define T_Lemonade 8
#define T_Cancel 9
#define T_Clang 10
#define T_ExtraClang 11
#define T_NotEnoughMoney 12
#define T_DecidedAgainst 13
#define T_BagFull 14
RT_Man:                                     // LilycoveCity_DepartmentStoreRooftop_EventScript_Man (sale on)
    c3_talk
    h_msgbox T_WaitingForSale
    h_release

RT_SaleWoman:                               // ..._EventScript_SaleWoman: pokemartdecoration (nothing is sold)
    c3_talk
    h_msgbox T_HowMayIServeYou
    h_msgbox T_PleaseComeAgain
    h_release

RT_VendingMachine:                          // ..._EventScript_VendingMachine
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ParentActorMsg MSGFILE_SCRIPT, T_WhichDrink, 2, 0
    MoneyWinDisp 31, 1
L_RT_ChooseDrink:
    ListMenu_AnchorTopRight 31, 5, 0, 1, C8_SEL
    ListMenuAdd T_FreshWater, 65535, 1
    ListMenuAdd T_SodaPop, 65535, 2
    ListMenuAdd T_Lemonade, 65535, 3
    ListMenuAdd T_Cancel, 65535, 0
    ListMenuShow
    WorkCmpConst C8_SEL, 1
    VMJumpIf CMP_LT, L_RT_NoDrink          // cancel / B
    WorkCmpConst C8_SEL, 3
    VMJumpIf CMP_GT, L_RT_NoDrink
    WorkCmpConst C8_SEL, 2
    VMJumpIf CMP_EQ, L_RT_SodaPop
    WorkCmpConst C8_SEL, 3
    VMJumpIf CMP_EQ, L_RT_Lemonade
    WorkSetConst C8_A, ITEM_FRESH_WATER     // Sapphire: VAR_TEMP_0 = the item, VAR_TEMP_1 = the choice
    WorkSetConst C8_B, 200
    VMJump L_RT_TryBuy
L_RT_SodaPop:
    WorkSetConst C8_A, ITEM_SODA_POP
    WorkSetConst C8_B, 300
    VMJump L_RT_TryBuy
L_RT_Lemonade:
    WorkSetConst C8_A, ITEM_LEMONADE
    WorkSetConst C8_B, 350
L_RT_TryBuy:                                // ..._EventScript_TryBuyDrink
    MoneyCheck C8_D, C8_B                   // checkmoney: 1 = enough
    WorkCmpConst C8_D, 0
    VMJumpIf CMP_EQ, L_RT_NotEnough
    ItemCheckSpace C8_A, 1, C8_C            // checkitemspace
    WorkCmpConst C8_C, 0
    VMJumpIf CMP_EQ, L_RT_BagFull
    SEPlay SEQ_SE_SYS_22                    // removemoney, updatemoneybox, playse SE_VEND
    MoneySub C8_B
    MoneyWinUpdate
    SEWait
    WordSetItemName 1, C8_A                 // bufferitemname
    ParentActorMsg MSGFILE_SCRIPT, T_Clang, 2, 0
    LastKeyWait
    MsgWinCloseAll
    VMCall Sub_RT_GiveDrink
    Random C8_E, 64                         // random 64: 0 = an extra can (twice at most)
    WorkCmpConst C8_E, 0
    VMJumpIf CMP_NE, L_RT_ChooseNew
    ItemCheckSpace C8_A, 1, C8_C
    WorkCmpConst C8_C, 0
    VMJumpIf CMP_EQ, L_RT_BagFull
    SEPlay SEQ_SE_SYS_22
    ParentActorMsg MSGFILE_SCRIPT, T_ExtraClang, 2, 0
    LastKeyWait
    MsgWinCloseAll
    VMCall Sub_RT_GiveDrink
    Random C8_E, 64
    WorkCmpConst C8_E, 0
    VMJumpIf CMP_NE, L_RT_ChooseNew
    ItemCheckSpace C8_A, 1, C8_C
    WorkCmpConst C8_C, 0
    VMJumpIf CMP_EQ, L_RT_BagFull
    SEPlay SEQ_SE_SYS_22
    ParentActorMsg MSGFILE_SCRIPT, T_ExtraClang, 2, 0
    LastKeyWait
    MsgWinCloseAll
    VMCall Sub_RT_GiveDrink
L_RT_ChooseNew:                             // ..._EventScript_ChooseNewDrink
    ParentActorMsg MSGFILE_SCRIPT, T_WhichDrink, 2, 0
    VMJump L_RT_ChooseDrink
L_RT_NotEnough:
    ParentActorMsg MSGFILE_SCRIPT, T_NotEnoughMoney, 2, 0
    VMJump L_RT_Exit
L_RT_BagFull:
    ParentActorMsg MSGFILE_SCRIPT, T_BagFull, 2, 0
    VMJump L_RT_Exit
L_RT_NoDrink:
    ParentActorMsg MSGFILE_SCRIPT, T_DecidedAgainst, 2, 0
L_RT_Exit:                                  // ..._EventScript_ExitVendingMachine
    LastKeyWait
    MsgWinCloseAll
    MoneyWinClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Sub_RT_GiveDrink:                           // additem + "put away" (Black 2's own item flow, global 2805)
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, C8_A
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
    VMReturn
    .balign 4, 0
