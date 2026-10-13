// Steven's house, Chapter Ch13's two post-game beats (Sapphire data/maps/MossdeepCity_StevensHouse/scripts.inc,
// MossdeepCity_StevensHouse_EventScript_BeldumPokeball / GiveBeldum / LeaveBeldum and ..._Letter / LetterWithoutDive; ch13 agent
// 2026-10-07). Included by 0678_room_MossdeepCity_StevensHouse.s (guarded) in place of ch9's fallback, which was the same port
// (ch9 wrote it from Sapphire; this file keeps its text lines 8-15 and its labels Ch13_SH_BeldumBall = script 10, Ch13_SH_Letter
// = script 11). The room file defines T_TakeBall (8) ... T_BagFull (15), SH_BELDUM_BALL, SH_* and includes scenes/ch9_lib.inc.
// Both appear when the Hall of Fame has been seen (scenes/ch13_gameclear.inc clears FLAG_HIDE_BELDUM_BALL_STEVENS_HOUSE; ch11
// clears FLAG_HIDE_STEVENS_LETTER and sets VAR_STEVENS_HOUSE_STATE 1). Not built: Sapphire's ON_LOAD that hides the letter's
// table tile until the game is cleared (the room has no metatiles): the letter is a sign that does nothing until then.
#define C13_A 0x8040
#define C13_B 0x8041
#define C13_C 0x8042
Ch13_SH_BeldumBall:                     // MossdeepCity_StevensHouse_EventScript_BeldumPokeball (lockall)
    h_lock
    h_buffer_player
    h_yesno T_TakeBall, C13_A           // <player> checked the Poké Ball. It contained the Pokémon Beldum. Take the Poké Ball?
    h_goto_if_no C13_A, L_SH_LeaveBeldum
    h_getpartysize C13_B
    h_goto_if_eq C13_B, 6, L_SH_NoSpace
    h_removeobject SH_BELDUM_BALL, FLAG_HIDE_BELDUM_BALL_STEVENS_HOUSE
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    h_buffer_player
    h_msgbox_info T_ObtainedBeldum      // <player> obtained a Beldum.
    h_waitfanfare
    PokePartyAdd C13_C, SPECIES_BELDUM, 0, 5     // givemon SPECIES_BELDUM, 5, ITEM_NONE
    h_closemessage
    WordSetPokeSpecies 2, SPECIES_BELDUM    // bufferspeciesname 1
    h_yesno T_Nickname, C13_A           // Want to give a nickname to the Beldum you received?
    h_goto_if_no C13_A, L_SH_BeldumDone
    h_name_received_mon C13_B           // (the party size before = the new one's slot)
L_SH_BeldumDone:
    h_setflag FLAG_HIDE_BELDUM_BALL_STEVENS_HOUSE
    h_setflag FLAG_RECEIVED_BELDUM
    h_release
L_SH_NoSpace:                           // MossdeepCity_StevensHouse_EventScript_GiveBeldum
    h_msgbox T_NoSpace                  // There is no space for another Pokémon.
    h_release
L_SH_LeaveBeldum:                       // MossdeepCity_StevensHouse_EventScript_LeaveBeldum
    h_buffer_player
    h_msgbox T_LeftBall                 // <player> left the Poké Ball where it was.
    h_release

Ch13_SH_Letter:                         // MossdeepCity_StevensHouse_EventScript_Letter (lockall; the object exists once the game is cleared)
    h_lock
    h_goto_if_set FLAG_HIDE_STEVENS_LETTER, L_SH_NoLetter
    h_buffer_player
    h_goto_if_set FLAG_OMIT_DIVE_FROM_STEVEN_LETTER, L_SH_LetterWithoutDive
    h_msgbox_info T_LetterWithDive      // It's a letter. ... If you'd like, you should also take the HM Dive. ...
    h_closemessage
    h_release
L_SH_LetterWithoutDive:
    h_msgbox_info T_Letter              // It's a letter. ... I have a favor to ask of you. ...
    h_closemessage
    h_release
L_SH_NoLetter:
    h_release
