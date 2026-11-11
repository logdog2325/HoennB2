// Prof. Birch gives the DexNav (notes/DEXNAV.md): in the Pokédex scene (0792 Script_12), right after the rival's Poké
// Balls, and when talked to by a save that got its Pokédex before the DexNav existed (0792 Script_7, lab state 5,
// VAR_DEXNAV_STATE 0): first, before anything else Birch has for the player (the post-game starters, Emerald's Johto
// offer), which then follows as before. Either way VAR_DEXNAV_STATE becomes 1: the touch screen turns into the DexNav, and the first step
// into Route 101's tall grass starts the rival's tutorial (scenes/Route101_DexNav.inc). Every line is NEW, from Route 101's
// text file (common/dexnav_defs.inc DN_TEXT).
#include "common/dexnav_defs.inc"

DN_LabGive:                                       // the Pokédex scene: the player faced the rival; back to Birch
    h_turnobject 255, 0
    VMCall DN_LabGiveCore
    VMReturn

DN_LabOwed:                                       // Script_7, first: DN_W_GAVE = 1 when Birch gave it now
    h_setvar DN_W_GAVE, 0
    h_goto_if_ne VAR_BIRCH_LAB_STATE, 5, L_DN_OwedDone
    h_goto_if_ne VAR_DEXNAV_STATE, DN_STATE_NONE, L_DN_OwedDone
    VMCall DN_LabGiveCore
    h_setvar DN_W_GAVE, 1
L_DN_OwedDone:
    VMReturn

DN_LabGiveCore:
    h_buffer_player
    dn_msg_actor DN_T_BIRCH_GIVE, 0               // NEW: Prof. Birch: Oh, that's right! ... try it out for me
    h_closemessage
    MEPlay SEQ_ME_KEYITEM
    DexNavCmd DN_OP_INFO_MSG, DN_TEXT, DN_T_RECEIVED, DN_W_A   // NEW: <player> received the DexNav!
    MEWait
    LastKeyWait
    InfoMsgClose_0039
    h_setvar VAR_DEXNAV_STATE, DN_STATE_TUTORIAL
    DexNavCmd DN_OP_SCREEN_REFRESH, 0, 0, DN_W_A  // the touch screen turns into the DexNav now, not at the next door
    h_goto_if_girl DN_LabExplainBrendan
    dn_msg_actor DN_T_BIRCH_EXPLAIN_MAY, 0        // NEW: Prof. Birch: That's the DexNav. ... May will show you
    VMJump DN_LabExplained
DN_LabExplainBrendan:
    dn_msg_actor DN_T_BIRCH_EXPLAIN_BRENDAN, 0
DN_LabExplained:
    h_closemessage
    VMReturn
