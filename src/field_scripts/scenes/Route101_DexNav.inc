// Route 101's DexNav tutorial (notes/DEXNAV.md; Omega Ruby and Alpha Sapphire's first DexNav search, here with the rival).
// Script 4: started by the decomp's dexnav.c at the player's first step into Route 101's tall grass once Birch has given
// the DexNav (VAR_DEXNAV_STATE 1, after the Lab's Pokédex scene and the rival's Poké Balls). The rival (May for a boy,
// Brendan for a girl) runs up from behind the player, explains, gives Poké Balls if the Bag has none, and the DexNav puts a
// Poochyena that knows Thunder Fang, Ice Fang or Fire Fang (dexnav.c, the config's moves) in shaking grass a few steps
// away. It is a normal wild battle: catch it or knock it out.
// Script 5: dexnav.c starts it after that battle (unless the player blacked out: then the tutorial is simply over), with
// the result in VAR_DEXNAV_STATE: the rival's line, then it leaves the way it came.
// Softlocks: the state is 2 before anything else, so the step never starts script 4 twice. If the spot goes (a zone
// change, another script), dexnav.c puts it out again at the next step in Route 101. No room for the rival (walls on
// every side): an info line instead.
#include "common/dexnav_defs.inc"

Script_4:
    h_lock
    h_setvar VAR_DEXNAV_STATE, DN_STATE_TUTORIAL_SEARCH
    h_buffer_player                               // {0100:0} in the rival's lines
    h_setup_rival_gfx
    DexNavCmd DN_OP_RIVAL_SPAWN, 0, 0, DN_W_N
    h_goto_if_eq DN_W_N, 0xffff, DN_TutNoRival
    h_move 255, 75                                // emote_exclamation_mark over the player
    DexNavCmd DN_OP_RIVAL_INFO, 0, 0, DN_W_DIR    // the rival runs up beside the player
    VMCall DN_RivalSteps
    DexNavCmd DN_OP_RIVAL_INFO, 2, 0, DN_W_DIR    // the player turns to it
    VMCall DN_PlayerFace
    h_msgbox_gendered DN_T_INTRO_MAY, DN_T_INTRO_BRENDAN, DN_RIVAL
    h_checkitem ITEM_POKE_BALL, 1, DN_W_A
    h_goto_if_ne DN_W_A, 0, DN_TutHasBalls
    h_msgbox_gendered DN_T_NO_BALLS_MAY, DN_T_NO_BALLS_BRENDAN, DN_RIVAL   // NEW: none left: two from the rival
    h_closemessage
    h_giveitem ITEM_POKE_BALL, 2
DN_TutHasBalls:
    h_msgbox_gendered DN_T_EXPLAIN_MAY, DN_T_EXPLAIN_BRENDAN, DN_RIVAL
    h_closemessage
    DexNavCmd DN_OP_TUTORIAL_SEARCH, 0, 0, DN_W_A
    h_delay 16
    DexNavCmd DN_OP_SPOT_DIR, 0, 0, DN_W_DIR      // both look at the shaking grass
    h_goto_if_eq DN_W_DIR, 0xffff, DN_TutTalk
    VMCall DN_PlayerFace
DN_TutTalk:
    h_msgbox_gendered DN_T_GO_MAY, DN_T_GO_BRENDAN, DN_RIVAL
    h_closemessage
    h_release

DN_TutNoRival:
    DexNavCmd DN_OP_TUTORIAL_SEARCH, 0, 0, DN_W_A
    h_delay 16
    dn_info DN_T_GO_NO_RIVAL
    h_release

Script_5:
    h_lock
    h_buffer_player
    DexNavCmd DN_OP_RIVAL_PRESENT, 0, 0, DN_W_A
    h_goto_if_eq DN_W_A, 0, DN_TutEndDone
    h_goto_if_eq VAR_DEXNAV_STATE, DN_STATE_TUTORIAL_CAUGHT, DN_TutCaught
    h_goto_if_eq VAR_DEXNAV_STATE, DN_STATE_TUTORIAL_KO, DN_TutKO
    h_msgbox_gendered DN_T_RAN_MAY, DN_T_RAN_BRENDAN, DN_RIVAL
    VMJump DN_TutBye
DN_TutCaught:
    h_msgbox_gendered DN_T_CAUGHT_MAY, DN_T_CAUGHT_BRENDAN, DN_RIVAL
    VMJump DN_TutBye
DN_TutKO:
    h_msgbox_gendered DN_T_KO_MAY, DN_T_KO_BRENDAN, DN_RIVAL
DN_TutBye:
    h_closemessage
    DexNavCmd DN_OP_RIVAL_INFO, 1, 0, DN_W_N      // back the way it came, then gone
    DexNavCmd DN_OP_RIVAL_INFO, 2, 0, DN_W_DIR
    h_goto_if_eq DN_W_DIR, 0xffff, DN_TutGone
    VMCall DN_RivalSteps
DN_TutGone:
    DexNavCmd DN_OP_RIVAL_DELETE, 0, 0, DN_W_A
DN_TutEndDone:
    h_setvar VAR_DEXNAV_STATE, DN_STATE_DONE
    h_release

// The rival walks DN_W_N steps (0-3) in way DN_W_DIR (walk_fast_up .. _right: 16-19)
DN_RivalSteps:
    h_goto_if_eq DN_W_N, 0, DN_StepsDone
    VMCall DN_RivalStep
    h_goto_if_eq DN_W_N, 1, DN_StepsDone
    VMCall DN_RivalStep
    h_goto_if_eq DN_W_N, 2, DN_StepsDone
    VMCall DN_RivalStep
DN_StepsDone:
    VMReturn

DN_RivalStep:
    h_goto_if_eq DN_W_DIR, 0, DN_StepUp
    h_goto_if_eq DN_W_DIR, 1, DN_StepDown
    h_goto_if_eq DN_W_DIR, 2, DN_StepLeft
    h_move DN_RIVAL, 19
    VMReturn
DN_StepUp:
    h_move DN_RIVAL, 16
    VMReturn
DN_StepDown:
    h_move DN_RIVAL, 17
    VMReturn
DN_StepLeft:
    h_move DN_RIVAL, 18
    VMReturn

// The player faces way DN_W_DIR (face_up .. face_right: 0-3)
DN_PlayerFace:
    h_goto_if_eq DN_W_DIR, 0, DN_FaceUp
    h_goto_if_eq DN_W_DIR, 1, DN_FaceDown
    h_goto_if_eq DN_W_DIR, 2, DN_FaceLeft
    h_turnobject 255, 3
    VMReturn
DN_FaceUp:
    h_turnobject 255, 0
    VMReturn
DN_FaceDown:
    h_turnobject 255, 1
    VMReturn
DN_FaceLeft:
    h_turnobject 255, 2
    VMReturn
