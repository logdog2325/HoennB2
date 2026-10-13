// Small helpers the Emerald scenes of builder B1 share (emerald_ch0_3, 2026-10-12). Emerald builds only; include inside an
// `#ifdef HOENN_EMERALD` after "hoenn_story.inc". Safe to include twice.
#ifndef EM_B1_COMMON_INC
#define EM_B1_COMMON_INC

// pokeemerald's "Registered X in the PokéNav" jingle (MUS_REGISTER_MATCH_CALL). Black 2 has no such short jingle; its
// item fanfare stands in until the user picks one by ear (decision 3A: the registering is a plain message with this jingle).
#ifndef MUS_REGISTER_MATCH_CALL
#define MUS_REGISTER_MATCH_CALL SEQ_ME_ITEM
#endif

    // MSGBOX_YESNO said by an actor with one line for a boy player (the rival is May) and one for a girl (the rival is Brendan):
    // ActorMsgGendered (hoenn_story.inc h_msgbox_gendered) then Black 2's YES/NO window; var = 0 YES, 1 NO
    .macro em_yesno_gendered nboy, ngirl, actor, var
    ActorMsgGendered MSGFILE_SCRIPT, \nboy, \ngirl, \actor, 0, 0
    YesNoWin \var
    .endm

#endif
