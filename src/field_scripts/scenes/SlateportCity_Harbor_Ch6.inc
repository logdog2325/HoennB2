// Chapter Ch6's beat in the Slateport Harbor (Sapphire data/maps/SlateportCity_Harbor/scripts.inc
// SlateportCity_Harbor_EventScript_CaptSternFerryOrScannerComment to the end): once you have the Mind Badge, Capt. Stern
// trades the Abandoned Ship's Scanner for a Deepseatooth or a Deepseascale; otherwise his ferry lines. Capt. Stern's
// script is chapter Ch8's (scenes/SlateportCity_Harbor_Ch8.inc, Ch8_HB_CaptStern): it must start, after lock +
// faceplayer, with `h_goto_if_badge 7, Ch6_HB_SternScanner` (Sapphire's first check) and include this file in its body
// part. Until Ch8 writes its file the room's stand-in Stern script does that (1192_room_SlateportCity_Harbor.s).
// Text: lines 4-16 of src/text/script/0352_room_SlateportCity_Harbor.txt. VAR_TEMP_1 = work 0x4001 (cleared on every
// map load in Black 2, as Sapphire's temporary vars).
#ifndef SLATEPORT_HARBOR_CH6_INC
#define SLATEPORT_HARBOR_CH6_INC
#include "hoenn_key_items.h"
#define HB6_WouldTrade 4
#define HB6_Tooth 5
#define HB6_Scale 6
#define HB6_Handed 7
#define HB6_LetMeKnow 8
#define HB6_WhichOne 9
#define HB6_Research 10
#define HB6_WontBeLong 11
#define HB6_Finished 12
#define HB6_MTooth 13
#define HB6_MScale 14
#define HB6_MCancel 15
#define HB6_BagFull 16
#define HB6_TEMP_1 0x4001
#define HB6_SEL 0x8008

Ch6_HB_SternScanner:                        // SlateportCity_Harbor_EventScript_CaptSternFerryOrScannerComment
    h_buffer_player
    h_goto_if_eq HB6_TEMP_1, 1, L_HB6_TradedScanner
    h_checkitem ITEM_SCANNER, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 1, L_HB6_AskToTrade
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_HB6_FerryFinished
    h_msgbox HB6_WontBeLong                 // Capt. Stern: Oh, yes. Mr. Briney came to our Shipyard. ...
    h_release
L_HB6_FerryFinished:
    h_msgbox HB6_Finished                   // Capt. Stern: <player>! We finally finished making the ferry S.S. Tidal! ...
    h_release
L_HB6_AskToTrade:                           // AskToTradeScanner
    ParentActorMsg MSGFILE_SCRIPT, HB6_WouldTrade, 0, 0   // Capt. Stern: Oh? <player>, that item you have... ...
L_HB6_Choose:                               // ChooseScannerTrade (multichoice 46: Deepseatooth / Deepseascale / Cancel)
    ListMenu_AnchorTopRight 31, 9, 0, 1, HB6_SEL
    ListMenuAdd HB6_MTooth, 65535, 0
    ListMenuAdd HB6_MScale, 65535, 1
    ListMenuAdd HB6_MCancel, 65535, 2
    ListMenuShow
    h_goto_if_eq HB6_SEL, 0, L_HB6_Tooth
    h_goto_if_eq HB6_SEL, 1, L_HB6_Scale
    h_msgbox HB6_LetMeKnow                  // DeclineTrade: Capt. Stern: Are you certain? ...
    h_release
L_HB6_Tooth:
    h_yesno HB6_Tooth, HB6_SEL              // Capt. Stern: So you'll trade it for my Deepseatooth?
    h_goto_if_no HB6_SEL, L_HB6_ChooseAgain
    h_closemessage
    h_giveitem ITEM_DEEP_SEA_TOOTH
    VMJump L_HB6_Given
L_HB6_Scale:
    h_yesno HB6_Scale, HB6_SEL              // Capt. Stern: So you'll trade it for my Deepseascale?
    h_goto_if_no HB6_SEL, L_HB6_ChooseAgain
    h_closemessage
    h_giveitem ITEM_DEEP_SEA_SCALE
L_HB6_Given:
    h_goto_if_eq HLIB_RESULT, 0, L_HB6_BagFull
    h_removeitem ITEM_SCANNER, 1, HLIB_TMP
    h_buffer_player
    h_msgbox_info HB6_Handed                // <player> handed the Scanner to Capt. Stern.
    h_closemessage
    h_setflag FLAG_EXCHANGED_SCANNER
L_HB6_TradedScanner:                        // TradedScanner
    h_setvar HB6_TEMP_1, 1
    h_buffer_player
    h_msgbox HB6_Research                   // Capt. Stern: Thanks, <player>! This will help our research a lot!
    h_release
L_HB6_ChooseAgain:                          // ChooseDifferentTrade
    ParentActorMsg MSGFILE_SCRIPT, HB6_WhichOne, 0, 0     // Capt. Stern: Which one do you want?
    VMJump L_HB6_Choose
L_HB6_BagFull:
    h_bag_is_full HB6_BagFull
    h_release
#endif
