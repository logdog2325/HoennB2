// RustboroCity_PokemonSchool (zone 591): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0347_room_RustboroCity_PokemonSchool.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7    // teacher (RustboroCity_PokemonSchool_EventScript_Teacher), chapter Ch1
    ScriptEntry Script_8    // blackboard (RustboroCity_PokemonSchool_EventScript_Blackboard), chapter Ch1
#ifdef HOENN_EMERALD
    ScriptEntry Script_9    // Scott (RustboroCity_PokemonSchool_EventScript_Scott), Emerald only (chapter Ch1)
#endif
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 1, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 2, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 3, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 4, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 5, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt


// ---- story (chapter Ch1)
#define PS_TEACHER 6                             // Sapphire object 6 (data/story/ch1.json)
#define PS_SEL 0x8008

Script_7:                                      // Sapphire RustboroCity_PokemonSchool_EventScript_Teacher (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_QUICK_CLAW, L_PS_GaveClaw
    h_getplayerfacing HLIB_TMP                   // Sapphire VAR_FACING 4 east / 3 west = Black 2 3 / 2
    h_goto_if_eq HLIB_TMP, 3, L_PS_CheckEast
    h_goto_if_ne HLIB_TMP, 2, L_PS_Give
    h_applymovement PS_TEACHER, Mv_PS_CheckWest
    VMJump L_PS_Checked
L_PS_CheckEast:
    h_applymovement PS_TEACHER, Mv_PS_CheckEast
L_PS_Checked:
    h_waitmovement
L_PS_Give:
    h_msgbox 13                                 // Students who don't study get a little taste of my Quick Claw. ...
    h_closemessage
    h_giveitem ITEM_QUICK_CLAW
    h_goto_if_eq HLIB_RESULT, 0, L_PS_Release
    h_applymovement PS_TEACHER, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_setflag FLAG_RECEIVED_QUICK_CLAW
L_PS_Release:
    h_release
L_PS_GaveClaw:
    h_msgbox 14                                 // A Pokémon holding the Quick Claw will occasionally speed up ...
    h_closemessage
    h_applymovement PS_TEACHER, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_release

Script_8:                                      // Sapphire RustboroCity_PokemonSchool_EventScript_Blackboard (lockall)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info 6                              // The blackboard lists status changes that may affect Pokémon in battle.
L_PS_Topic:                                    // ChooseBlackboardTopic: multichoicegrid MULTI_STATUS_INFO -> Black 2's list menu
    h_closemessage
    SystemMsg 7, 2                             // Which topic do you want to read?
    ListMenu_AnchorTopRight 31, 1, 0, 1, PS_SEL
    ListMenuAdd 15, 65535, 0                     // PSN
    ListMenuAdd 16, 65535, 1                    // PAR
    ListMenuAdd 17, 65535, 2                    // SLP
    ListMenuAdd 18, 65535, 3                    // BRN
    ListMenuAdd 19, 65535, 4                    // FRZ
    ListMenuAdd 20, 65535, 5                    // Cancel
    ListMenuShow
    h_closemessage
    h_goto_if_eq PS_SEL, 0, L_PS_Poison
    h_goto_if_eq PS_SEL, 1, L_PS_Paralysis
    h_goto_if_eq PS_SEL, 2, L_PS_Sleep
    h_goto_if_eq PS_SEL, 3, L_PS_Burn
    h_goto_if_eq PS_SEL, 4, L_PS_Freeze
    h_release                                    // Cancel / B (65534)
L_PS_Poison:
    h_msgbox_info 8
    VMJump L_PS_Topic
L_PS_Paralysis:
    h_msgbox_info 9
    VMJump L_PS_Topic
L_PS_Sleep:
    h_msgbox_info 10
    VMJump L_PS_Topic
L_PS_Burn:
    h_msgbox_info 11
    VMJump L_PS_Topic
L_PS_Freeze:
    h_msgbox_info 12
    VMJump L_PS_Topic

#ifdef HOENN_EMERALD
Script_9:                                      // Emerald RustboroCity_PokemonSchool_EventScript_Scott (lock, faceplayer); text lines
    h_lock                                     // 21-24 of the room's Emerald overlay (src/text/script/emerald/0347_*)
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_MET_SCOTT_AFTER_OBTAINING_STONE_BADGE, L_PS_EmWatch
    h_goto_if_set FLAG_MET_SCOTT_RUSTBORO, L_PS_EmSpoke
    h_goto_if_badge 1, L_PS_EmGreetBadge
    h_msgbox 21                                // Hello? Didn't we meet before? I think back in Petalburg City. ... Cut.
    h_addvar VAR_SCOTT_STATE, 1
    h_setflag FLAG_MET_SCOTT_RUSTBORO
    h_release
L_PS_EmSpoke:
    h_goto_if_badge 1, L_PS_EmNotice
L_PS_EmWatch:
    h_msgbox 22                                // Scott: Hmm... The talent levels of the students here are unknown. ...
    h_release
L_PS_EmGreetBadge:
    h_msgbox 23                                // Hello? ... Oh, what's that? It's a Stone Badge, isn't it? ...
    VMJump L_PS_EmMetAfterBadge
L_PS_EmNotice:
    h_msgbox 24                                // Scott: Oh, what's that? It's a Stone Badge, isn't it? ...
L_PS_EmMetAfterBadge:
    h_addvar VAR_SCOTT_STATE, 1
    h_setflag FLAG_MET_SCOTT_AFTER_OBTAINING_STONE_BADGE
    h_release
#endif

    .balign 4, 0
Mv_PS_CheckWest:                               // RustboroCity_PokemonSchool_Movement_TeacherCheckOnStudentsWest
    walk_left
    walk_down 2
    walk_right
    walk_in_place_fastest_down
    delay_16 3
    walk_down
    walk_in_place_fastest_left
    delay_16 2
    walk_right
    delay_16 2
    delay_8
    walk_up
    walk_left 2
    walk_up 2
    walk_right
    step_end
Mv_PS_CheckEast:                               // ..._TeacherCheckOnStudentsEast
    walk_right 2
    walk_down 2
    walk_left 2
    walk_in_place_fastest_down
    delay_16 3
    walk_down
    walk_in_place_fastest_left
    delay_16 2
    walk_right
    delay_16 2
    delay_8
    walk_up
    walk_right
    walk_up 2
    walk_left 2
    step_end
#include "common/movement.inc"
    .balign 4, 0
