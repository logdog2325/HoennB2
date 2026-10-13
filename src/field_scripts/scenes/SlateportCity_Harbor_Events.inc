// Capt. Stern gives the Old Sea Map (Emerald's Faraway Island ticket; Black 2's Journal renamed, converter/gen_key_items.py).
// Events agent, 2026-10-07 (notes/EVENTS.md: in-game event tickets instead of Mystery Gift, user request). Included INSIDE
// Capt. Stern (scenes/SlateportCity_Harbor_Ch8.inc Ch8_HB_CaptStern)'s script right after the greeting (guarded): once the game is cleared, the first talk gives the ticket and sets
// FLAG_ENABLE_SHIP_FARAWAY_ISLAND (Lilycove's harbor then sails there: scenes/LilycoveCity_Harbor_Events.inc). New lines (Emerald has no text
// for this): 35, 36 of the room's text file. The code jumps over itself when it has nothing to do.
#include "hoenn_key_items.h"
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_EvSternSkip
    h_goto_if_set FLAG_ENABLE_SHIP_FARAWAY_ISLAND, L_EvSternSkip
    h_buffer_player
    h_msgbox 35
    h_closemessage                              // (close before the item: notes/STORY_HANDOFFS.md "From ch6")
    h_giveitem ITEM_OLD_SEA_MAP, 1
    h_setflag FLAG_ENABLE_SHIP_FARAWAY_ISLAND
    h_msgbox 36
    h_release
L_EvSternSkip:
