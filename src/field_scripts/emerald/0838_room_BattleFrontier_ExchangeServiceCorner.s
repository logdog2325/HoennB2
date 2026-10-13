// BattleFrontier_ExchangeServiceCorner (zone 419; header scripts 838 -> own file 1976), Pokémon Emerald NDS only
// (frontier_core, 2026-10-12; notes/FRONTIER.md 4). pokeemerald data/maps/BattleFrontier_ExchangeServiceCorner, plus
// the two BP move tutors of BattleFrontier_Lounge7 (the user: all of the Frontier's prizes in this room).
// People: data/interiors/emerald/419.json (uid = script = Emerald's local id, then the tutors). Emerald's two
// decoration clerks (local ids 1 and 6) are left out (the user, 2026-10-12: Black 2 has no decorations); their
// script numbers stay unused so the others keep Emerald's numbers.
// Messages: src/text/script/emerald/0648_room_BattleFrontier_ExchangeServiceCorner.txt (b2tools/frontier_text.py
// install: Emerald's words): 0 the clerks' welcome, 1 their goodbye, 2-6 the people, 7-25 / 26-44 the tutors.
// The prize clerks sell on Black 2's BP shop screen with Emerald's lists (FR_SHOP_*: b2tools/patches/frontier_core.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"

#define ESC_WELCOME 0                   // Hello, this is the Exchange Service Corner. ...
#define ESC_BYE 1                       // Thank you very much. Please visit us when you have saved up Battle Points.
#define ESC_TUTOR_LEFT 7
#define ESC_TUTOR_RIGHT 26

    ScriptEntry ESC_Unused              // 1 (Emerald's decoration clerk 1: not placed)
    ScriptEntry ESC_RichBoy             // 2
    ScriptEntry ESC_PokefanF            // 3
    ScriptEntry ESC_Sailor              // 4
    ScriptEntry ESC_Man                 // 5
    ScriptEntry ESC_Unused              // 6 (Emerald's decoration clerk 2: not placed)
    ScriptEntry ESC_VitaminClerk        // 7 (TEALA)
    ScriptEntry ESC_HoldItemClerk       // 8 (TEALA)
    ScriptEntry ESC_Girl                // 9
    ScriptEntry ESC_LeftMoveTutor       // 10 (Lounge7's left tutor)
    ScriptEntry ESC_RightMoveTutor      // 11 (Lounge7's right tutor)
    ScriptEntriesEnd

ESC_Unused:
    VMHalt

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

ESC_LeftMoveTutor:                      // Softboiled 16 ... Swords Dance 48 BP
    fr_bp_tutor 0, ESC_TUTOR_LEFT

ESC_RightMoveTutor:                     // Defense Curl 16 ... Fire Punch 48 BP
    fr_bp_tutor 1, ESC_TUTOR_RIGHT

    .balign 4, 0
