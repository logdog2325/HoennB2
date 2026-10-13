// The Enigma Berry (postgame_scripts, 2026-10-07): Sapphire's PetalburgCity_Gym_EventScript_ShouldGiveEnigmaBerry and
// _GiveEnigmaBerry (pokeruby data/maps/PetalburgCity_Gym/scripts.inc), at the start of Norman's post-battle talk
// (Ch6_NormanPostBattle, scenes/PetalburgCity_Gym_ch6.inc, which includes this file there, guarded). Sapphire gave it
// only after an e-Reader Mystery Event (IsEnigmaBerryValid + VAR_ENIGMA_BERRY_AVAILABLE); here (user decision) after the
// Hall of Fame, once (FLAG_RECEIVED_ENIGMA_BERRY), and, as Sapphire, not while the Bag holds one (checkitem; Sapphire's
// checkpcitem has no Black 2 counterpart: the PC stores no items). Black 2's own Enigma Berry (item 208).
// Text: line 52 of src/text/script/0187_room_PetalburgCity_Gym.txt (PetalburgCity_Gym_Text_GiveEnigmaBerry); the bag-full
// line is ch6's PGT_BagFull (51).
#define PGT_GiveEnigmaBerry 52
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_PG_NoEnigmaBerry
    h_goto_if_set FLAG_RECEIVED_ENIGMA_BERRY, L_PG_NoEnigmaBerry
    h_checkitem ITEM_ENIGMA_BERRY, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 1, L_PG_NoEnigmaBerry
    h_buffer_player
    h_msgbox PGT_GiveEnigmaBerry                    // Dad: Hi, <player>! I just received a very rare Berry. I'd like you to have it.
    h_closemessage                                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_ENIGMA_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_PG_EnigmaBagFull
    h_setflag FLAG_RECEIVED_ENIGMA_BERRY            // setvar VAR_ENIGMA_BERRY_AVAILABLE, 0
    h_release
L_PG_EnigmaBagFull:                                 // Common_EventScript_ShowBagIsFull
    h_bag_is_full PGT_BagFull
    h_release
L_PG_NoEnigmaBerry:
