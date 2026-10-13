// Route109_SeashoreHouse (zone 509): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0262_room_Route109_SeashoreHouse.txt
// Story (chapter Ch2, Sapphire data/maps/Route109_SeashoreHouse/scripts.inc) after the "// ---- story" line (the
// generator placed nobody here): script 1 (Mr. Sea, uid 1), text lines 0-9; the three trainers (Dwayne uid 2, Johanna
// uid 4, Simon uid 3) are Black 2 eye-contact trainers (script 3000 + id) in data/story/ch2.json. Room origin (1,0).
// Their after-battle script (Route109_SeashoreHouse_EventScript_160F09: FLAG_DEFEATED_SEASHORE_HOUSE_TRAINERS once
// all three are beaten) has no hook in Black 2's trainer script: Mr. Sea checks the three trainer flags himself.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry SH_MrSea            // 1: Route109_SeashoreHouse_EventScript_160DD4
    ScriptEntriesEnd
// ---- story
#define FLAG_SH_TEMP_2 0x5B         // FLAG_TEMP_2 (map-local: flags 0-0x63 reset on every zone change)

SH_MrSea:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_6_SODA_POP, L_SH_SellSodaPop
    h_goto_if_not_defeated TRAINER_DWAYNE, L_SH_NotAllBeaten      // Route109_SeashoreHouse_EventScript_160F09
    h_goto_if_not_defeated TRAINER_JOHANNA, L_SH_NotAllBeaten
    h_goto_if_not_defeated TRAINER_SIMON, L_SH_NotAllBeaten
    h_setflag FLAG_DEFEATED_SEASHORE_HOUSE_TRAINERS
L_SH_NotAllBeaten:
    h_goto_if_set FLAG_DEFEATED_SEASHORE_HOUSE_TRAINERS, L_SH_GiveSodaPop
    h_goto_if_set FLAG_SH_TEMP_2, L_SH_ShowMeHotMatches
    h_msgbox 0                      // I'm the owner of the Seashore House. But you can call me Mr. Sea! ...
    h_setflag FLAG_SH_TEMP_2
    h_release
L_SH_ShowMeHotMatches:
    h_msgbox 1                      // Show me some hot matches! ...
    h_release
L_SH_GiveSodaPop:                   // Route109_SeashoreHouse_EventScript_160E08
    h_msgbox 2                      // You're scorching hot! ...As thanks for... six bottles of Soda Pop!
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_SODA_POP, 6
    h_goto_if_eq HLIB_RESULT, 0, L_SH_BagFullForSix
    h_setflag FLAG_RECEIVED_6_SODA_POP
    h_release
L_SH_BagFullForSix:
    h_msgbox 3                      // Oh, but hey, your Bag's jammed full. I'll hang on to these for you.
    h_release
L_SH_SellSodaPop:                   // Route109_SeashoreHouse_EventScript_160E36 (showmoneybox 0, 0)
    MoneyWinDisp 31, 1
    h_yesno 4, HLIB_TMP             // Want to buy some Soda Pop? ...Just ¥300 a bottle! Buy some!
    h_goto_if_yes HLIB_TMP, L_SH_Buy
    h_msgbox 7                      // No? That's too bad.
    MoneyWinClose
    h_release
L_SH_Buy:                           // checkmoney 300 / checkitemspace ITEM_SODA_POP, 1
    MoneyCheck HLIB_TMP, 300
    h_goto_if_eq HLIB_TMP, 0, L_SH_NoMoney
    h_checkitemspace ITEM_SODA_POP, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_SH_BagFull
    h_msgbox 5                      // Here you go!
    h_closemessage
    SEPlay SEQ_SE_SYS_22            // removemoney 300 + updatemoneybox (Black 2's vending sequence, 0010.s)
    MoneySub 300
    MoneyWinUpdate
    SEWait
    h_giveitem ITEM_SODA_POP
    MoneyWinClose
    h_release
L_SH_NoMoney:
    h_msgbox 6                      // You don't have the money.
    MoneyWinClose
    h_release
L_SH_BagFull:
    h_msgbox 8                      // Too bad! The Bag is full...
    MoneyWinClose
    h_release
    .balign 4, 0
