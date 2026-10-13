// Chapter Ch6's beat in Mauville City (Sapphire data/maps/MauvilleCity/scripts.inc MauvilleCity_EventScript_Wattson to
// the end): Wattson outside the Gym after the Balance Badge: the Basement Key (New Mauville), TM24 Thunderbolt once
// the Generator is off (VAR_NEW_MAUVILLE_STATE 2). Included by chapter Ch3's scenes/MauvilleCity.inc (script 5, object
// uid 108, data/story/ch3b.json). Text: five lines of src/text/scenes/MauvilleCity.txt from MC_CH6_T on.
#ifndef MC_CH6_T
#define MC_CH6_T 15
#endif
#include "hoenn_key_items.h"
#define MC6_TakeKey (MC_CH6_T + 0)          /* MauvilleCity_Text_WattsonNeedFavorTakeKey */
#define MC6_WontBeChallenge (MC_CH6_T + 1)  /* MauvilleCity_Text_WattsonWontBeChallenge */
#define MC6_ThanksTakeTM (MC_CH6_T + 2)     /* MauvilleCity_Text_WattsonThanksTakeTM */
#define MC6_YoungTakeCharge (MC_CH6_T + 3)  /* MauvilleCity_Text_WattsonYoungTakeCharge */
#define MC6_BagFull (MC_CH6_T + 4)          /* Text_TooBadBagIsFull */

Ch6_Wattson:                                // MauvilleCity_EventScript_Wattson
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_set FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON, L_MC6_ReceivedThunderbolt
    h_goto_if_eq VAR_NEW_MAUVILLE_STATE, 2, L_MC6_CompletedNewMauville
    h_goto_if_set FLAG_RECEIVED_BASEMENT_KEY, L_MC6_BegunNewMauville
    h_msgbox MC6_TakeKey                    // Wattson: Oh, <player>! You look like you have a lot of zip! ...
    h_closemessage                          // (Black 2: the item script opens its own window)
    h_giveitem ITEM_BASEMENT_KEY
    h_setflag FLAG_RECEIVED_BASEMENT_KEY
    h_msgbox MC6_WontBeChallenge            // Wattson: Don't you worry about it. ...
    h_release
L_MC6_BegunNewMauville:
    h_msgbox MC6_WontBeChallenge
    h_release
L_MC6_CompletedNewMauville:
    h_msgbox MC6_ThanksTakeTM               // Wattson: Wahahahaha! I knew it, <player>! ...
    h_closemessage
    h_giveitem ITEM_TM24                    // TM24 Thunderbolt (Black 2's TM24 too)
    h_goto_if_eq HLIB_RESULT, 0, L_MC6_BagFull
    h_setflag FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON
    h_msgbox MC6_YoungTakeCharge            // Wattson: Wahahahaha! It pleases me to no end ...
    h_release
L_MC6_ReceivedThunderbolt:
    h_msgbox MC6_YoungTakeCharge
    h_release
L_MC6_BagFull:
    h_bag_is_full MC6_BagFull
    h_release
