// SlateportCity_OceanicMuseum_2F (zone 11): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0017_room_SlateportCity_OceanicMuseum_2F.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch3a
#include "hoenn_trainers.h"  // ch3a
#include "hoenn_story.inc"  // ch3a
#include "scenes/ch3_lib.inc"  // ch3a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntry Script_10
    ScriptEntry Script_11
    ScriptEntry Script_12
    ScriptEntry Script_13
    ScriptEntry Script_14
    ScriptEntry Script_15
    ScriptEntry Script_16
    ScriptEntry Script_17
    ScriptEntry Script_18
    ScriptEntry Script_19
    ScriptEntry Script_20
    ScriptEntry Script_21
    ScriptEntry Story_M2_CaptStern      // 22: object 1  // story:
    ScriptEntry Story_M2_Patron1        // 23: object 5  // story:
    ScriptEntry Story_M2_Patron2        // 24: object 6  // story:
    ScriptEntry Story_M2_Patron3        // 25: object 7  // story:
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

Script_3:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 2, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 3, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 4, 2
    LastKeyWait
    MsgWinCloseAll
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

Script_7:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 6, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 7, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 8, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_10:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 9, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 10, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_12:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 11, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_13:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 12, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_14:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 13, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_15:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 14, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_16:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 15, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_17:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 16, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_18:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 17, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_19:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 18, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_20:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 19, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_21:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 20, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch3 part 3a, ch3a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/SlateportCity_OceanicMuseum_2F/scripts.inc: Capt. Stern, the two Aqua grunts, Archie, the Devon
// Goods delivered. People: data/story/ch3a.json (uid = Sapphire local id; Archie and the grunts hidden on the stairs
// (6,1) by their new-game flags until the scene). Lines 21-35 of the text file.
#define T_ThankYouForParts 21
#define T_WellTake 22
#define T_SternWhoAreYou 23
#define T_WereEvilTeam 24
#define T_BossFurious 25
#define T_LetMeTakeCare 26
#define T_MeddlingKid 27
#define T_CameToSee 28
#define T_ArchieWarning 29
#define T_SternThankYou 30
#define T_HandedOver 31
#define T_SternGotToGo 32
#define T_Patron1 33
#define T_Patron2 34
#define T_Patron3 35
#define M2_STERN 1
#define M2_ARCHIE 2
#define M2_GRUNT_A 3                        // Sapphire object 3: enters first, battles second (TRAINER_MUSEUM_2F_GRUNT_2)
#define M2_GRUNT_B 4                        // object 4: battles first (TRAINER_MUSEUM_2F_GRUNT_1)
#define M2_FACING 0x8037                    // VAR_FACING when the player talked to Stern (Black 2: 0 up 1 down 2 left 3 right)
#ifndef TRAINER_MUSEUM_2F_GRUNT_1
#define TRAINER_MUSEUM_2F_GRUNT_1 TRAINER_GRUNT_19   // Sapphire's constants/version.inc aliases
#define TRAINER_MUSEUM_2F_GRUNT_2 TRAINER_GRUNT_20
#endif

// Sapphire's lines here have no speaker name; the Black 2 speech balloon points at the one who says them: the grunt
// who came in first (object 3) speaks for the pair until object 4 steps up to battle.
Story_M2_CaptStern:                         // SlateportCity_OceanicMuseum_2F_EventScript_CaptStern
    c3_talk
    h_getplayerfacing M2_FACING
    h_msgbox T_ThankYouForParts
    h_closemessage
    h_playbgm MUS_EVIL_TEAM
    h_addobject M2_GRUNT_A, FLAG_HIDE_GRUNT_1_OCEANIC_MUSEUM_2F
    h_setflag FLAG_HIDE_GRUNT_1_OCEANIC_MUSEUM_2F   // Gen 3's addobject leaves the hide flag set (a lost battle
    h_applymovement M2_GRUNT_A, Mv_M2_FirstGruntEnter   // must not leave them on the stairs)
    h_waitmovement
    h_addobject M2_GRUNT_B, FLAG_HIDE_GRUNT_2_OCEANIC_MUSEUM_2F
    h_setflag FLAG_HIDE_GRUNT_2_OCEANIC_MUSEUM_2F
    h_applymovement M2_GRUNT_B, Mv_M2_SecondGruntEnter
    h_waitmovement
    h_applymovement M2_GRUNT_A, Mv_M2_FirstGruntApproach
    h_applymovement M2_GRUNT_B, Mv_M2_SecondGruntApproach
    h_waitmovement
    h_call_if_eq M2_FACING, 1, Sub_M2_PlayerFaceGrunts     // DIR_SOUTH
    h_call_if_eq M2_FACING, 3, Sub_M2_PlayerFaceGrunts     // DIR_EAST
    h_msgbox_actor T_WellTake, M2_GRUNT_A
    h_call_if_ne M2_FACING, 3, Sub_M2_SternFaceGrunts
    h_msgbox_actor T_SternWhoAreYou, M2_STERN
    h_msgbox_actor T_WereEvilTeam, M2_GRUNT_A
    h_closemessage
    h_applymovement M2_GRUNT_B, Mv_M2_GruntApproachToBattle
    h_waitmovement
    h_call_if_eq M2_FACING, 1, Sub_M2_PlayerApproachGruntSouth
    h_call_if_eq M2_FACING, 2, Sub_M2_PlayerApproachGruntWest  // DIR_WEST
    h_trainerbattle TRAINER_MUSEUM_2F_GRUNT_1
    h_msgbox_actor T_BossFurious, M2_GRUNT_B
    h_closemessage
    h_applymovement M2_GRUNT_B, Mv_M2_GruntDefeated
    h_waitmovement
    h_applymovement M2_GRUNT_A, Mv_M2_GruntApproachToBattle
    h_waitmovement
    h_msgbox_actor T_LetMeTakeCare, M2_GRUNT_A
    h_closemessage
    h_trainerbattle TRAINER_MUSEUM_2F_GRUNT_2       // (savebgm 0: the Museum's own music after this battle)
    h_applymovement M2_GRUNT_A, Mv_M2_GruntDefeated
    h_waitmovement
    h_applymovement M2_GRUNT_A, Common_Movement_WalkInPlaceFastestDown
    h_applymovement M2_GRUNT_B, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor T_MeddlingKid, M2_GRUNT_A
    h_closemessage
    h_delay 35
    h_addobject M2_ARCHIE, FLAG_HIDE_EVIL_TEAM_LEADER_OCEANIC_MUSEUM_2F
    h_setflag FLAG_HIDE_EVIL_TEAM_LEADER_OCEANIC_MUSEUM_2F
    h_applymovement M2_ARCHIE, Mv_M2_EvilLeaderEnter
    h_applymovement M2_GRUNT_B, Mv_M2_GruntMoveForEvilLeader
    h_waitmovement
    h_msgbox_actor T_CameToSee, M2_ARCHIE
    h_applymovement M2_ARCHIE, Mv_M2_EvilLeaderApproachPlayer
    h_waitmovement
    h_msgbox_actor T_ArchieWarning, M2_ARCHIE
    h_closemessage
    h_fadescreen_black
    h_removeobject M2_ARCHIE, FLAG_HIDE_EVIL_TEAM_LEADER_OCEANIC_MUSEUM_2F
    h_removeobject M2_GRUNT_A, FLAG_HIDE_GRUNT_1_OCEANIC_MUSEUM_2F
    h_removeobject M2_GRUNT_B, FLAG_HIDE_GRUNT_2_OCEANIC_MUSEUM_2F
    h_fadescreen_from_black
    h_delay 30
    h_setflag FLAG_HIDE_EVIL_TEAM_OCEANIC_MUSEUM
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_buffer_player
    h_msgbox_actor T_SternThankYou, M2_STERN
    h_closemessage
    h_handover_item ITEM_DEVON_GOODS, T_HandedOver  // Common_EventScript_PlayerHandedOverTheItem
    h_msgbox_actor T_SternGotToGo, M2_STERN
    h_closemessage
    h_applymovement M2_STERN, Mv_M2_SternLeave
    h_waitmovement
    h_playse SE_EXIT
    h_removeobject M2_STERN, FLAG_HIDE_STERN_OCEANIC_MUSEUM_2F
    h_setflag FLAG_HIDE_EVIL_TEAM_ROUTE110
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_clearflag FLAG_HIDE_DEVON_EMPLOYEE_ROUTE116
    h_setflag FLAG_HIDE_EMPLOYEE_DEVON_CORP_3F
#ifdef HOENN_EMERALD                // Emerald (emerald_ch0_3; SlateportCity_OceanicMuseum_2F_EventScript_...): Stern heals the party
    h_heal_party_fade               // (fadescreen, MUS_HEAL, HealPlayerParty) and Scott waits outside (Slateport's OnFrame scene)
    h_setvar VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE, 1
#endif
    h_release

Sub_M2_PlayerFaceGrunts:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    VMReturn
Sub_M2_SternFaceGrunts:
    h_applymovement M2_STERN, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    VMReturn
Sub_M2_PlayerApproachGruntSouth:
    h_applymovement 255, Mv_M2_PlayerApproachGruntSouth
    h_waitmovement
    VMReturn
Sub_M2_PlayerApproachGruntWest:
    h_applymovement 255, Mv_M2_PlayerApproachGruntWest
    h_waitmovement
    VMReturn

Story_M2_Patron1:                           // visitors (FLAG_HIDE_OCEANIC_MUSEUM_VISITORS: after Mauville)
    h_msgbox_npc T_Patron1
Story_M2_Patron2:
    h_msgbox_npc T_Patron2
Story_M2_Patron3:                           // ..._MuseumPatron3: turns back to the exhibit (FACE_RIGHT)
    c3_say_turn_back T_Patron3, 7, 3

    .balign 4, 0
Mv_M2_PlayerApproachGruntSouth:
    walk_left
    walk_down
    walk_in_place_fastest_left
    step_end
Mv_M2_PlayerApproachGruntWest:
    walk_up
    walk_left 2
    walk_down
    walk_in_place_fastest_left
    step_end
Mv_M2_SternLeave:                           // ..._EventScript_SternLeave (a movement list in Sapphire)
    walk_up
    walk_left 5
    walk_up 2
    walk_left 2
    walk_up 2
    delay_8
    step_end
Mv_M2_EvilLeaderApproachPlayer:
    walk_right
    step_end
Mv_M2_EvilLeaderEnter:
    walk_down 5
    walk_right 4
    step_end
Mv_M2_GruntApproachToBattle:
    walk_right
    step_end
Mv_M2_FirstGruntEnter:
    walk_down
    walk_right
    walk_in_place_fastest_down
    step_end
Mv_M2_FirstGruntApproach:
    walk_down 3
    walk_right 3
    step_end
Mv_M2_GruntDefeated:
    lock_facing_direction
    walk_left
    unlock_facing_direction
    step_end
Mv_M2_SecondGruntEnter:
    walk_down
    step_end
Mv_M2_SecondGruntApproach:
    walk_down 4
    walk_right 4
    step_end
Mv_M2_GruntMoveForEvilLeader:
    delay_16 8
    delay_8
    walk_fast_down
    walk_in_place_fastest_up
    step_end
#include "common/movement.inc"
    .balign 4, 0
