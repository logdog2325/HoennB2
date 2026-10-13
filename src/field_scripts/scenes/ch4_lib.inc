// Chapter 4 helpers (ch4 agent, 2026-10-07): macros only. Include after "hoenn_story.inc".
#ifndef CH4_LIB_INC
#define CH4_LIB_INC
#include "hoenn_key_items.h"

// script works of these helpers (HLIB_TMP/HLIB_RESULT are 0x8030/0x8031; Ch3's helpers use 0x8032-0x8036)
#define C4_TMP 0x8037
#define C4_TMP2 0x8038
#define C4_DOOR 0x8039                  // door model handle (opendoor / closedoor)

// lock + faceplayer of a talked-to person, as Black 2's NPC scripts start (ActorsPauseAll, talk sound, face)
    .macro c4_talk
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    .endm

// Sapphire opendoor x, y + waitdooranim / closedoor + waitdooranim: the door model at world tile (x, z) (Black 2's
// door animation, as Littleroot's arrival scene: 0778 BMCreateHandleByGPos + BMHndAudioVisualAnmPlay 0 open / 1 close)
    .macro c4_opendoor x, z
    BMCreateHandleByGPos C4_DOOR, 1, \x, \z
    BMHndAudioVisualAnmPlay C4_DOOR, 0
    BMHndAnmWait C4_DOOR
    .endm
    .macro c4_closedoor
    BMHndAudioVisualAnmPlay C4_DOOR, 1
    BMHndAnmWait C4_DOOR
    BMReleaseHandle C4_DOOR
    .endm

// a person that says one line and turns back (msgbox MSGBOX_DEFAULT, closemessage, Common_Movement_FaceOriginalDirection)
    .macro c4_say_turn_back n, uid, dir
    c4_talk
    h_msgbox \n
    h_closemessage
    h_turnobject \uid, \dir
    h_release
    .endm

// a Pokémon that cries and says its line (lock, faceplayer, waitse, playmoncry, msgbox, waitmoncry, release)
    .macro c4_mon_cry species, n
    c4_talk
    h_playmoncry \species
    h_msgbox \n
    h_waitmoncry
    h_release
    .endm

// a yes/no question nobody says (lockall + msgbox MSGBOX_YESNO of an object such as a fossil): var = 0 YES, 1 NO
    .macro c4_yesno_info n, var
    SystemMsg \n, 2
    YesNoWin \var
    .endm

// Common_EventScript_ShowEasyChatScreen for a TV interview: Black 2's word picker (user decision 2026-10-07: nothing
// is broadcast), as ch3a's c3_easy_chat: ok = 1 when a word was picked, else 0.
    .macro c4_easy_chat ok
    MsgWinCloseAll
    FadeOutBlackQ
    FadeWait
    FieldClose
    CallPhraseSelect 4, C4_TMP, C4_TMP2, \ok
    FieldOpen
    FadeInBlackQ
    FadeWait
    .endm
#endif
