// Prof. Cozmo, the meteorite researcher, gives the Aurora Ticket (Birth Island, where Deoxys came from space; Coupon 2 renamed).
// Events agent, 2026-10-07 (notes/EVENTS.md: in-game event tickets instead of Mystery Gift, user request). Included INSIDE
// Prof. Cozmo (0194_room_FallarborTown_House1.s FH1_ProfCozmo)'s script right after the greeting (guarded): once the game is cleared, the first talk gives the ticket and sets
// FLAG_ENABLE_SHIP_BIRTH_ISLAND (Lilycove's harbor then sails there: scenes/LilycoveCity_Harbor_Events.inc). New lines (Emerald has no text
// for this): 12, 13 of the room's text file. The code jumps over itself when it has nothing to do.
#include "hoenn_key_items.h"
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_EvCozmoSkip
    h_goto_if_set FLAG_ENABLE_SHIP_BIRTH_ISLAND, L_EvCozmoSkip
    h_buffer_player
    h_msgbox 12
    h_closemessage                              // (close before the item: notes/STORY_HANDOFFS.md "From ch6")
    h_giveitem ITEM_AURORA_TICKET, 1
    h_setflag FLAG_ENABLE_SHIP_BIRTH_ISLAND
    h_msgbox 13
    h_release
L_EvCozmoSkip:
