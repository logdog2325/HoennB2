// BattleFrontier_ExchangeServiceCorner (zone 419; header scripts 838 -> own file 1976), Pokémon Emerald NDS only
// (frontier_core, 2026-10-12; notes/FRONTIER.md 4). pokeemerald data/maps/BattleFrontier_ExchangeServiceCorner, plus
// until 2026-10-20 the two BP move tutors of BattleFrontier_Lounge7, now back in Lounge7 (frontier_lounges, zone 497).
// People: data/interiors/emerald/419.json (uid = script = Emerald's local id). Emerald's two decoration clerks (local ids
// 1 and 6) are back since v18.4 (notes/SECRET_BASES.md): they sell for Battle Points on the Secret Base shop menu.
// Messages: src/text/script/emerald/0648_room_BattleFrontier_ExchangeServiceCorner.txt (b2tools/frontier_text.py
// install: Emerald's words): 0 the clerks' welcome, 1 their goodbye, 2-6 the people.
// The prize clerks sell on Black 2's BP shop screen with Emerald's lists (FR_SHOP_*: b2tools/patches/frontier_core.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "common/secret_base_defs.inc"  // Secret Bases (notes/SECRET_BASES.md)
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"

    .macro c3_talk_esc
    h_lock
    h_faceplayer
    .endm
#define ESC_WELCOME 0                   // Hello, this is the Exchange Service Corner. ...
#define ESC_BYE 1                       // Thank you very much. Please visit us when you have saved up Battle Points.

    ScriptEntry ESC_DecorClerk1         // 1 (TEALA)
    ScriptEntry ESC_RichBoy             // 2
    ScriptEntry ESC_PokefanF            // 3
    ScriptEntry ESC_Sailor              // 4
    ScriptEntry ESC_Man                 // 5
    ScriptEntry ESC_DecorClerk2         // 6 (TEALA)
    ScriptEntry ESC_VitaminClerk        // 7 (TEALA)
    ScriptEntry ESC_HoldItemClerk       // 8 (TEALA)
    ScriptEntry ESC_Girl                // 9
    ScriptEntriesEnd

ESC_DecorClerk1:                        // Kiss Poster, Kiss Cushion, the dolls: 16-48 BP (sFrontierExchangeCorner_Decor1)
    c3_talk_esc
    SEPlay SEQ_SE_MESSAGE
    h_msgbox ESC_WELCOME
    h_closemessage
    sb_shop SB_SHOP_EM_EXCHANGE_1
    h_msgbox ESC_BYE
    h_release

ESC_DecorClerk2:                        // the big dolls: 128 BP (sFrontierExchangeCorner_Decor2)
    c3_talk_esc
    SEPlay SEQ_SE_MESSAGE
    h_msgbox ESC_WELCOME
    h_closemessage
    sb_shop SB_SHOP_EM_EXCHANGE_2
    h_msgbox ESC_BYE
    h_release

ESC_VitaminClerk:                       // Protein, Calcium, Iron, Zinc, Carbos, HP Up: 1 BP each
    fr_bp_shop FR_SHOP_VITAMINS, ESC_WELCOME, ESC_BYE

ESC_HoldItemClerk:                      // Leftovers, White Herb, Quick Claw, Mental Herb 48 BP; Bright Powder,
    fr_bp_shop FR_SHOP_HOLD_ITEMS, ESC_WELCOME, ESC_BYE     // Choice Band, King's Rock, Focus Band, Scope Lens 64 BP

ESC_RichBoy:
    h_msgbox_npc 2

ESC_PokefanF:                           // Emerald: lock, msgbox, release (she does not turn)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox 3
    h_closemessage
    h_release

ESC_Sailor:
    h_msgbox_npc 4

ESC_Man:
    h_msgbox_npc 5

ESC_Girl:
    h_msgbox_npc 6

    .balign 4, 0
