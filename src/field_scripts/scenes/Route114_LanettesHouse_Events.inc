// Lanette gives the Mystic Ticket from her colleague Bill in Kanto (FRLG's PC maker; Navel Rock is FRLG's and Emerald's; Coupon 3 renamed).
// Events agent, 2026-10-07 (notes/EVENTS.md: in-game event tickets instead of Mystery Gift, user request). Included INSIDE
// Lanette (1118_room_Route114_LanettesHouse.s LH_Lanette)'s script right after the greeting (guarded): once the game is cleared, the first talk gives the ticket and sets
// FLAG_ENABLE_SHIP_NAVEL_ROCK (Lilycove's harbor then sails there: scenes/LilycoveCity_Harbor_Events.inc). New lines (Emerald has no text
// for this): 8, 9 of the room's text file. The code jumps over itself when it has nothing to do.
#include "hoenn_key_items.h"
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_EvLanetteSkip
    h_goto_if_set FLAG_ENABLE_SHIP_NAVEL_ROCK, L_EvLanetteSkip
    h_buffer_player
    h_msgbox 8
    h_closemessage                              // (close before the item: notes/STORY_HANDOFFS.md "From ch6")
    h_giveitem ITEM_MYSTIC_TICKET, 1
    h_setflag FLAG_ENABLE_SHIP_NAVEL_ROCK
    h_msgbox 9
    h_release
L_EvLanetteSkip:
