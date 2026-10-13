// Route114_LanettesHouse (zone 559): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0360_room_Route114_LanettesHouse.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch4
#include "hoenn_trainers.h"  // ch4
#include "hoenn_story.inc"  // ch4
#include "scenes/ch4_lib.inc"  // ch4

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry LH_Lanette              // 3: object 1 (Route114_LanettesHouse_EventScript_15C262)  // story:
    ScriptEntry LH_Notebook             // 4: sign (5,1) (Route114_LanettesHouse_EventScript_15C299)  // story:
    ScriptEntry LH_Init                 // 5: Route114_LanettesHouse_OnTransition (zone init, 1119_..._init.s)  // story:
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 0, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 1, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch4, ch4 agent 2026-10-07: Sapphire data/maps/Route114_LanettesHouse/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). Lanette (uid 1, FLAG_HIDE_LANETTE: she comes home
// after the Fallarbor Center) and her notebook (sign (5,1)): data/story/ch4.json. Text lines 2-8 (0-1 = the PC e-mail).
// Black 2 gap: Sapphire's Lotad Doll (givedecoration) is a Secret Base decoration, which Black 2 does not have: she
// says her line and the doll is not given (FLAG_RECEIVED_DOLL_LANETTE is set as Sapphire's does after the gift).
#define T_LanetteDoll 2         // Route114_LanettesHouse_Text_192A0D
#define T_LanetteAdvice 3       // Route114_LanettesHouse_Text_192ACC
#define T_Notes1 4              // Route114_LanettesHouse_Text_192B4A
#define T_Notes2 5              // Route114_LanettesHouse_Text_192C01
#define T_Notes3 6              // Route114_LanettesHouse_Text_192CB4
#define T_ClosedNotebook 7      // Route114_LanettesHouse_Text_192DA9

LH_Init:
    h_setflag FLAG_LANDMARK_LANETTES_HOUSE
    VMHalt

LH_Lanette:                                 // Route114_LanettesHouse_EventScript_15C262
    c4_talk
#if __has_include("scenes/Route114_LanettesHouse_Events.inc")
#include "scenes/Route114_LanettesHouse_Events.inc"   // (events agent) after the game: the Mystic Ticket (text lines 8-9)
#endif
    h_goto_if_set FLAG_RECEIVED_DOLL_LANETTE, L_LH_Advice
    h_setflag FLAG_SYS_PC_LANETTE
    h_msgbox T_LanetteDoll
    h_setflag FLAG_RECEIVED_DOLL_LANETTE    // (givedecoration DECOR_LOTAD_DOLL: no decorations in Black 2)
    h_release
L_LH_Advice:
    h_msgbox T_LanetteAdvice
    h_release

LH_Notebook:                                // Route114_LanettesHouse_EventScript_15C299
    h_lock
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    c4_yesno_info T_Notes1, C4_TMP
    h_goto_if_no C4_TMP, L_LH_Closed
    c4_yesno_info T_Notes2, C4_TMP
    h_goto_if_no C4_TMP, L_LH_Done
    h_msgbox_info T_Notes3
L_LH_Done:
    h_release
L_LH_Closed:
    h_msgbox_info T_ClosedNotebook
    h_release
    .balign 4, 0
