// Mom gives the Eon Ticket (events agent, 2026-10-07; notes/EVENTS.md: in-game event tickets instead of Sapphire's Mystery
// Event, user request). Included INSIDE Mom's script 26 of scenes/players_house_1f.inc (guarded), before Ch13's
// "Dad should stay longer": after the Hall of Fame and the S.S. Ticket scene, the first time you talk to Mom in your own
// house she hands over a letter from the ferry company with the Eon Ticket (Black 2's Liberty Pass, gen_key_items.py) and
// sets FLAG_SYS_HAS_EON_TICKET, which Lilycove's harbor checks (Sapphire's own Eon Ticket scene, scenes/
// LilycoveCity_Harbor_Ch13.inc). New lines (no Sapphire text exists for this): T(28), T(29) of both houses' text files.
// The code jumps over itself when it has nothing to do. Raw commands: the house files do not include hoenn_story.inc.
#include "hoenn_key_items.h"
    TrainerCardGetSex 0x8030                     // only the player's own Mom (as Ch13's Script_30)
#if HOUSE_BRENDAN
    WorkCmpConst 0x8030, 0
#else
    WorkCmpConst 0x8030, 1
#endif
    VMJumpIf CMP_NE, L_EvMomSkip
    VMStackPushFlag FLAG_SYS_GAME_CLEAR          // goto_if_unset FLAG_SYS_GAME_CLEAR
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_EvMomSkip
    VMStackPushFlag FLAG_RECEIVED_SS_TICKET      // goto_if_unset FLAG_RECEIVED_SS_TICKET (Dad's scene first)
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_EvMomSkip
    VMStackPushFlag FLAG_SYS_HAS_EON_TICKET      // goto_if_set FLAG_SYS_HAS_EON_TICKET
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_EvMomSkip
    ParentActorMsg MSGFILE_SCRIPT, T(28), 0, 0   // Mom: Oh, <player>! A letter came for you ... the Eon Ticket ...
    LastKeyWait
    MsgWinCloseAll
    ItemCheckSpace ITEM_EON_TICKET, 1, 0x8031    // giveitem ITEM_EON_TICKET (Std_ObtainItem, global 2805)
    WorkCmpConst 0x8031, 0
    VMJumpIf CMP_EQ, L_EvMomFull
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSetConst 0x8000, ITEM_EON_TICKET
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
    FlagSet FLAG_SYS_HAS_EON_TICKET
    ParentActorMsg MSGFILE_SCRIPT, T(29), 0, 0   // Mom: The ferry leaves from Lilycove City's harbor. ...
    LastKeyWait
L_EvMomFull:                                     // (a Key Items pocket is never full)
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_EvMomSkip:
