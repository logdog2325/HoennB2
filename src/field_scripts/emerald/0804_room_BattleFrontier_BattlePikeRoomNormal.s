// BattleFrontier_BattlePikeRoomNormal (zone 402, Emerald only): the room behind a doorway (pokeemerald
// data/maps/BattleFrontier_BattlePikeRoomNormal + data/scripts/battle_pike.inc; frontier_pike 2026-10-12,
// notes/FRONTIER_PIKE.md). What it holds was chosen at the doorway (frontier_pike.c PK_NEXT_ROOM, Emerald's odds); the
// zone init places its two people (NPC codes 162/163: their sprites from works 0x4020/0x4021, set by PK_SETUP_ROOM),
// the map-script condition runs its event. The battles are Black 2's (CallTrainerBattle on the Pike's slots 529-531:
// frontier_pike.c fills the Frontier trainer and its party; CallTrainerBattle ..., 1 goes on after a loss).
// Messages: src/text/script/emerald/0631_room_*.txt (+ the 300 trainers' greetings, the 42 people's lines).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pike_lib.inc"

#define PK_NPC1 1                       // LOCALID_PIKE_ROOM_NPC_1 (VAR_OBJ_GFX_ID_0 = work 0x4020)
#define PK_NPC2 2                       // LOCALID_PIKE_ROOM_NPC_2 (VAR_OBJ_GFX_ID_1 = work 0x4021)
#define PK_X(x) ((x) + PK_OX)
#define PK_Z(z) ((z) + PK_OZ)

    ScriptEntry PKR_Npc                 // 1: _EventScript_NPC (the first person)
    ScriptEntry PKR_StatusMon           // 2: _EventScript_StatusMon (Kirlia / Dusclops)
    ScriptEntry PKR_Exit                // 3: _EventScript_Exit (trigger (4,3))
    ScriptEntry PKR_Entered             // 4: _SetEnteredRoom (3-5,6)
    ScriptEntry PKR_NoTurningBack       // 5: _NoTurningBack (3-5,7)
    ScriptEntry PKR_Enter               // 6: ON_FRAME _EnterRoom (condition PK_W_STATE 0)
    ScriptEntry PKR_Init                // 7: zone init (ON_TRANSITION + ON_WARP)
    ScriptEntriesEnd

// ON_TRANSITION: pike_setroomobjects + the people's places by room type; ON_WARP _InitRoomObjects: who is hidden
PKR_Init:
    EmPike PK_T0, PK_SETUP_ROOM
    FlagReset PK_F_HIDE1
    FlagReset PK_F_HIDE2
    h_goto_if_eq PK_T0, PIKE_ROOM_DOUBLE_BATTLE, L_PKR_InitDouble
    h_goto_if_eq PK_T0, PIKE_ROOM_STATUS, L_PKR_InitTwo
    h_goto_if_eq PK_T0, PIKE_ROOM_HARD_BATTLE, L_PKR_InitTwo
    h_goto_if_eq PK_T0, PIKE_ROOM_BRAIN, L_PKR_InitBrain
    h_goto_if_eq PK_T0, PIKE_ROOM_NPC, L_PKR_InitNpc
    h_setobjectxyperm 0, PK_X(4), PK_Z(4), 1                // _SetOneObjectRoomPos (single, full heal, part heal)
    FlagSet PK_F_HIDE2
    VMHalt
L_PKR_InitNpc:
    h_setobjectxyperm 0, PK_X(5), PK_Z(5), 1                // _SetNPCRoomObjPos
    FlagSet PK_F_HIDE2
    VMHalt
L_PKR_InitDouble:
    h_setobjectxyperm 0, PK_X(2), PK_Z(5), 1                // _SetDoubleBattleObjPos
    h_setobjectxyperm 1, PK_X(6), PK_Z(5), 1
    VMHalt
L_PKR_InitTwo:
    h_setobjectxyperm 0, PK_X(4), PK_Z(4), 1                // _SetTwoObjectRoomPos
    h_setobjectxyperm 1, PK_X(3), PK_Z(4), 1
    VMHalt
L_PKR_InitBrain:
    h_setobjectxyperm 0, PK_X(4), PK_Z(3), 1                // _SetBrainRoomObjPos: Lucy hidden at first
    h_setobjectxyperm 1, PK_X(4), PK_Z(4), 1
    FlagSet PK_F_HIDE1
    VMHalt

PKR_Enter:                              // _EnterRoom: pike_getroomtype
    WorkSetConst PK_W_STATE, 1
    EmPike PK_T0, PK_ROOM_TYPE
    h_goto_if_eq PK_T0, PIKE_ROOM_SINGLE_BATTLE, L_PKR_Single
    h_goto_if_eq PK_T0, PIKE_ROOM_HEAL_FULL, L_PKR_FullHeal
    h_goto_if_eq PK_T0, PIKE_ROOM_STATUS, L_PKR_Status
    h_goto_if_eq PK_T0, PIKE_ROOM_HARD_BATTLE, L_PKR_Hard
    h_goto_if_eq PK_T0, PIKE_ROOM_DOUBLE_BATTLE, L_PKR_Double
    h_goto_if_eq PK_T0, PIKE_ROOM_BRAIN, L_PKR_Brain
    VMHalt                              // (the people's room and the part-heal room: nothing on arrival)

// ---- a single battle (_EnterSingleBattleRoom) and the tougher one with a heal (_EnterHardBattleRoom)
L_PKR_Single:
    ActorsPauseAll
    h_delay 16
    VMCall Sub_PKR_TrainerA
    h_goto_if_ne PK_T1, 1, L_PKR_Lost
    h_applymovement PK_NPC1, PKR_MvNpcExit              // _WonSingleBattle
    h_waitmovement
    h_release
L_PKR_Hard:
    ActorsPauseAll
    h_delay 16
    h_msgbox_info PKL_ROOM_TOUGH        // Welcome… Here, we will have you battle a somewhat-tough Trainer…
    h_closemessage
    VMCall Sub_PKR_TrainerA
    h_goto_if_ne PK_T1, 1, L_PKR_Lost
    h_applymovement PK_NPC1, PKR_MvNpcExit              // _WonHardBattle
    h_waitmovement
    h_applymovement PK_NPC2, PKR_MvHealIn
    h_waitmovement
    h_turnobject PK_NPC2, 1
    pk_say PKL_ROOM_RESTORE, PK_NPC2    // How wonderful… To honor your victory, your Pokémon shall be restored…
    MEPlay MUS_HEAL
    MEWait
    h_heal
    pk_say PKL_ROOM_ENJOY2, PK_NPC2
    h_closemessage
    h_applymovement PK_NPC2, PKR_MvNpcExit
    h_waitmovement
    h_release
Sub_PKR_TrainerA:                       // the trainer walks up, says its greeting, the battle: PK_T1 = 1 won
    h_applymovement PK_NPC1, PKR_MvApproach
    h_waitmovement
    EmPike PK_T2, PK_INTRO, 0           // pike_gettrainerintro 0 (the line = the Frontier trainer's index)
    WorkAdd PK_T2, PKL_ROOM_INTRO
    ActorMsg MSGFILE_SCRIPT, PK_T2, PK_NPC1, 0, 0
    LastKeyWait
    h_closemessage
    CallTrainerBattle PK_TR_A, 0, 1     // SPECIAL_BATTLE_PIKE_SINGLE (three Pokémon)
    CallTrainerBattleEnd
    TrainerBattleIsVictory PK_T1
    VMReturn

// ---- _EnterDoubleBattleRoom: two trainers, one Pokémon each (SPECIAL_BATTLE_PIKE_DOUBLE)
L_PKR_Double:
    ActorsPauseAll
    h_delay 16
    h_applymovement PK_NPC1, PKR_MvRight
    h_applymovement PK_NPC2, PKR_MvLeft
    h_waitmovement
    h_applymovement PK_NPC1, PKR_MvDown2
    h_applymovement PK_NPC2, PKR_MvDown2
    h_waitmovement
    h_turnobject PK_NPC1, 3
    h_turnobject PK_NPC2, 2
    h_turnobject PK_PLAYER, 2
    EmPike PK_T2, PK_INTRO, 0
    WorkAdd PK_T2, PKL_ROOM_INTRO
    ActorMsg MSGFILE_SCRIPT, PK_T2, PK_NPC1, 0, 0
    LastKeyWait
    h_closemessage
    h_delay 16
    h_turnobject PK_PLAYER, 3
    EmPike PK_T2, PK_INTRO, 1
    WorkAdd PK_T2, PKL_ROOM_INTRO
    ActorMsg MSGFILE_SCRIPT, PK_T2, PK_NPC2, 0, 0
    LastKeyWait
    h_closemessage
    CallTrainerBattle PK_TR_A, PK_TR_B, 1
    CallTrainerBattleEnd
    TrainerBattleIsVictory PK_T1
    h_goto_if_ne PK_T1, 1, L_PKR_Lost
    h_turnobject PK_PLAYER, 3           // _WonDoubleBattle
    h_applymovement PK_NPC1, PKR_MvT1Exit
    h_waitmovement
    h_applymovement PK_NPC2, PKR_MvT2Exit
    h_waitmovement
    h_turnobject PK_PLAYER, 0
    h_release

// ---- _EnterFullHealRoom
L_PKR_FullHeal:
    ActorsPauseAll
    h_delay 16
    h_applymovement PK_NPC1, PKR_MvApproach
    h_waitmovement
    pk_print PKL_ROOM_FULL_HEAL, PK_NPC1    // Welcome… You must be commended for your luck… restored to full health…
    MEPlay MUS_HEAL
    MEWait
    h_heal
    pk_say PKL_ROOM_ENJOY, PK_NPC1
    h_closemessage
    h_applymovement PK_NPC1, PKR_MvNpcExit
    h_waitmovement
    h_release

// ---- _EnterStatusRoom: the Pokémon was already hit at the doorway (pike_setnextroom); the scene shows it
L_PKR_Status:
    ActorsPauseAll
    pk_print PKL_ROOM_WATCH_OUT, PK_NPC1    // Oh, my! Watch out!
    h_applymovement PK_NPC2, PKR_MvMonIn
    h_waitmovement
    EmPike PK_T0, PK_STATUS_MON
    EmPike PK_T1, PK_STATUS_KIND
    h_goto_if_eq PK_T0, PIKE_STATUSMON_DUSCLOPS, L_PKR_Dusclops
    pk_say PKL_ROOM_KIRLIA_STOP, PK_NPC1    // _KirliaAttack
    h_closemessage
    h_playmoncry SPECIES_KIRLIA
    h_waitmoncry
    WorkSetConst PK_T2, PKL_ROOM_K_TOXIC
    h_goto_if_eq PK_T1, PIKE_STATUS_TOXIC, L_PKR_Used
    WorkSetConst PK_T2, PKL_ROOM_K_WISP
    h_goto_if_eq PK_T1, PIKE_STATUS_BURN, L_PKR_Used
    WorkSetConst PK_T2, PKL_ROOM_K_TWAVE
    h_goto_if_eq PK_T1, PIKE_STATUS_PARALYSIS, L_PKR_Used
    WorkSetConst PK_T2, PKL_ROOM_K_HYPNOSIS
    VMJump L_PKR_Used
L_PKR_Dusclops:
    pk_say PKL_ROOM_DUSCLOPS_STOP, PK_NPC1  // _DusclopsAttack
    h_closemessage
    h_playmoncry SPECIES_DUSCLOPS
    h_waitmoncry
    WorkSetConst PK_T2, PKL_ROOM_D_ICE
    h_goto_if_eq PK_T1, PIKE_STATUS_FREEZE, L_PKR_Used
    WorkSetConst PK_T2, PKL_ROOM_D_WISP
L_PKR_Used:
    SystemMsg PK_T2, 2                  // "KIRLIA used TOXIC!" (message + waitmessage)
    VMCall Sub_PKR_Flash                // pike_flashscreen
    h_closemessage
    h_applymovement PK_NPC1, PKR_MvDown1                // _NPCApproachMon
    h_waitmovement
    h_turnobject PK_NPC2, 0                             // _MonFaceNPC
    VMCall Sub_PKR_Cry
    pk_say PKL_ROOM_ENOUGH, PK_NPC1     // Look here! That's quite enough!
    VMCall Sub_PKR_Cry
    h_closemessage
    h_applymovement PK_NPC2, PKR_MvMonAside
    h_applymovement PK_NPC1, PKR_MvStatusNpcIn
    h_waitmovement
    WorkSetConst PK_T2, PKL_ROOM_SORRY_KIRLIA
    h_goto_if_eq PK_T0, PIKE_STATUSMON_KIRLIA, L_PKR_Sorry
    WorkSetConst PK_T2, PKL_ROOM_SORRY_DUSCLOPS
L_PKR_Sorry:
    ActorMsg MSGFILE_SCRIPT, PK_T2, PK_NPC1, 0, 0
    LastKeyWait
    pk_say PKL_ROOM_STARTLED, PK_NPC1   // It attacks without warning if it is startled … Are you all right?
    h_closemessage
    h_release
Sub_PKR_Cry:
    h_goto_if_eq PK_T0, PIKE_STATUSMON_DUSCLOPS, L_PKR_CryD
    h_playmoncry SPECIES_KIRLIA
    h_waitmoncry
    VMReturn
L_PKR_CryD:
    h_playmoncry SPECIES_DUSCLOPS
    h_waitmoncry
    VMReturn
Sub_PKR_Flash:                          // StartStatusInflictionScreenFlash(0, 0, 3, 2, 2): three grey flashes
    WorkSetConst PK_T3, 3
L_PKR_FlashLoop:
    FadeEx 3, 0, 10, 1
    FadeExWait
    FadeEx 3, 10, 0, 1
    FadeExWait
    WorkSub PK_T3, 1
    h_goto_if_ne PK_T3, 0, L_PKR_FlashLoop
    VMReturn

// ---- _EnterBrainRoom: the Pike Queen Lucy
L_PKR_Brain:
    h_delay 22
    ActorsPauseAll
    h_applymovement PK_NPC2, PKR_MvApproach             // _PreQueenHealNPCApproachPlayer
    h_waitmovement
    EmPike PK_T0, PK_HEAL_BEFORE_QUEEN  // pike_prequeenheal: 0, 1 or 2 Pokémon healed by the doorway chosen
    h_goto_if_eq PK_T0, 1, L_PKR_HealOneQ
    h_goto_if_eq PK_T0, 2, L_PKR_HealTwoQ
    pk_say PKL_ROOM_NO_HEAL, PK_NPC2
    VMJump L_PKR_LucyEnter
L_PKR_HealOneQ:
    pk_say PKL_ROOM_HEAL_ONE_Q, PK_NPC2
    MEPlay MUS_HEAL
    MEWait
    VMJump L_PKR_LucyEnter
L_PKR_HealTwoQ:
    pk_say PKL_ROOM_HEAL_TWO_Q, PK_NPC2
    MEPlay MUS_HEAL
    MEWait
L_PKR_LucyEnter:                        // _LucyEnter: "I shall go fetch our master…", the curtain closes and opens
    pk_say PKL_ROOM_FETCH, PK_NPC2      // (Emerald redraws the doorway's curtain tiles: here the room darkens and
    h_closemessage                      //  Lucy steps out of the doorway)
    h_applymovement PK_NPC2, PKR_MvHealOutLucy
    h_waitmovement
    SEPlay SE_PIKE_CURTAIN
    FadeEx 3, 0, 16, 1
    FadeExWait
    h_delay 60
    h_addobject PK_NPC1, PK_F_HIDE1     // showobjectat LOCALID_PIKE_ROOM_NPC_1
    SEPlay SE_PIKE_CURTAIN
    FadeEx 3, 16, 0, 1
    FadeExWait
    h_applymovement PK_NPC1, PKR_MvLucyIn
    h_waitmovement
    EmPike PK_T0, PK_QUEEN_TYPE         // pike_getbrainstatus
    h_goto_if_eq PK_T0, FRONTIER_BRAIN_GOLD, L_PKR_IntroGold
    h_goto_if_eq PK_T0, FRONTIER_BRAIN_STREAK, L_PKR_Silver
    h_goto_if_eq PK_T0, FRONTIER_BRAIN_STREAK_LONG, L_PKR_Gold
    pk_get PKF_HEARD_BRAIN, PK_T1
    h_goto_if_ne PK_T1, 0, L_PKR_Silver
    pk_say PKL_ROOM_QUEEN, PK_NPC1      // I am Lucy… I am the law here… For I am the Pike Queen…
    pk_set PKF_HEARD_BRAIN, 1
L_PKR_Silver:
    pk_say PKL_ROOM_USED_UP_LUCK, PK_NPC1
    VMCall Sub_PKR_Queen
    h_goto_if_ne PK_T1, 1, L_PKR_Lost
    fr_symbol_get FRONTIER_FACILITY_PIKE, PK_T1         // _DefeatedLucySilver
    h_goto_if_ne PK_T1, 0, L_PKR_LucyBeaten
    pk_say PKL_ROOM_SHOW_PASS, PK_NPC1  // Lucy: … Show me your Frontier Pass…
    h_closemessage                      // (Emerald's one message box: Lucy's line gives way to the symbol's)
    MEPlay MUS_OBTAIN_SYMBOL
    h_msgbox_info PKL_ROOM_LUCK_SYMBOL  // The Luck Symbol was embossed on the Frontier Pass!
    MEWait
    h_closemessage
    fr_symbol_give FRONTIER_FACILITY_PIKE, 0
    pk_set PKF_HEARD_BRAIN, 0           // (Emerald keeps one "heard" bit per symbol: the gold intro comes next)
    pk_say PKL_ROOM_DISAPPEAR, PK_NPC1
    h_closemessage
    VMJump L_PKR_LucyBeaten
L_PKR_IntroGold:
    pk_get PKF_HEARD_BRAIN, PK_T1
    h_goto_if_ne PK_T1, 0, L_PKR_Gold
    pk_say PKL_ROOM_YOU_AGAIN, PK_NPC1  // Lucy: …You again…
    pk_set PKF_HEARD_BRAIN, 1
L_PKR_Gold:
    pk_say PKL_ROOM_COME_ON, PK_NPC1    // Now! Come on!
    VMCall Sub_PKR_Queen
    h_goto_if_ne PK_T1, 1, L_PKR_Lost
    fr_symbol_get FRONTIER_FACILITY_PIKE, PK_T1         // _DefeatedLucyGold
    h_goto_if_eq PK_T1, 2, L_PKR_LucyBeaten
    pk_say PKL_ROOM_PASS, PK_NPC1       // Lucy: … …Frontier Pass…
    h_closemessage                      // (Emerald's one message box: Lucy's line gives way to the symbol's)
    MEPlay MUS_OBTAIN_SYMBOL
    h_msgbox_info PKL_ROOM_GOLDEN       // The Luck Symbol took on a golden shine!
    MEWait
    h_closemessage
    fr_symbol_give FRONTIER_FACILITY_PIKE, 1
    pk_say PKL_ROOM_NOT_FORGET, PK_NPC1
    h_closemessage
L_PKR_LucyBeaten:                       // _DefeatedLucy: she steps aside, the player walks up, streak + 1, final room
    h_applymovement PK_NPC1, PKR_MvLucyAside
    h_waitmovement
    h_applymovement PK_PLAYER, PKR_MvUp2
    h_waitmovement
    pk_streak_win
    fr_set FR_BRAIN_BEATEN, 1           // (frontier_core's lobby: "snatched victory from the Pike Queen", +10 BP)
    VMJump L_PKR_ToFinal
Sub_PKR_Queen:                          // _DoPikeQueenBattle: PK_T1 = 1 won
    h_closemessage
    h_applymovement PK_PLAYER, PKR_MvUp2
    h_waitmovement
    CallTrainerBattle PK_TR_LUCY, 0, 1
    CallTrainerBattleEnd
    TrainerBattleIsVictory PK_T1
    VMReturn

L_PKR_Lost:                             // _WarpToLobbyLost
    fr_set FR_STATUS, FR_ST_LOST
    h_warp_arrive PK_LOBBY_ZONE, 5 + PK_OX, 6 + PK_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- talking to the room's people
PKR_Npc:                                // _EventScript_NPC: pike_getroomtype
    h_lock
    EmPike PK_T0, PK_ROOM_TYPE
    h_goto_if_eq PK_T0, PIKE_ROOM_STATUS, L_PKR_NpcStatus
    h_goto_if_eq PK_T0, PIKE_ROOM_HEAL_PART, L_PKR_NpcHeal
    SEPlay SEQ_SE_MESSAGE               // _NormalNPC: pike_getnpcmsg (an easy-chat line by room number)
    h_faceplayer
    EmPike PK_T2, PK_NPC_SPEECH
    WorkAdd PK_T2, PKL_ROOM_SPEECH
    ParentActorMsg MSGFILE_SCRIPT, PK_T2, 0, 0
    LastKeyWait
    h_closemessage
    h_release
L_PKR_NpcStatus:
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox PKL_ROOM_HOPE_FINE         // I do apologize for what happened… I do hope your Pokémon are fine.
    h_closemessage
    h_release
L_PKR_NpcHeal:                          // _HealNPC: pike_healonetwomons, then the line for one or two
    EmPike PK_T1, PK_HEAL_ONE_TWO
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    WorkSetConst PK_T2, PKL_ROOM_HEAL_TWO
    h_goto_if_eq PK_T1, 2, L_PKR_NpcHealSay
    WorkSetConst PK_T2, PKL_ROOM_HEAL_ONE
L_PKR_NpcHealSay:
    ParentActorMsg MSGFILE_SCRIPT, PK_T2, 0, 0
    LastKeyWait
    h_closemessage
    MEPlay MUS_HEAL
    MEWait
    h_msgbox PKL_ROOM_FAREWELL          // The best of luck to you. Farewell.
    h_closemessage
    h_applymovement PK_NPC1, PKR_MvHealExit
    h_waitmovement
    h_release
PKR_StatusMon:                          // Dusclops or Kirlia: "… … …"
    h_lock
    h_faceplayer
    h_msgbox PKL_ROOM_SILENCE
    h_closemessage
    h_turnobject PK_NPC2, 3
    h_release

// _EventScript_Exit (trigger (4,3)): pike_ispartyfullhealth -> pike_nohealing, streak + 1, room + 1, the next room
PKR_Exit:
    ActorsPauseAll
    EmPike PK_T0, PK_FULL_HEALTH
    pk_set PKF_HEAL_OFF, PK_T0
    pk_streak_win
    pk_room_plus_one
    EmPike PK_T0, PK_IS_FINAL
    h_applymovement PK_PLAYER, PKR_MvHide
    h_waitmovement
    h_goto_if_eq PK_T0, 1, L_PKR_ToFinal2
    pk_curtain_warp PK_THREE_ZONE, 6 + PK_OX, 10 + PK_OZ
L_PKR_ToFinal:
    h_applymovement PK_PLAYER, PKR_MvHide
    h_waitmovement
L_PKR_ToFinal2:
    pk_curtain_warp PK_FINAL_ZONE, 2 + PK_FINAL_OX, 7 + PK_FINAL_OZ

PKR_Entered:
    WorkSetConst PK_W_NO_TURN, 1
    WorkSetConst PK_W_ENTERED, 1
    VMHalt
PKR_NoTurningBack:
    WorkSetConst PK_W_NO_TURN, 0
    WorkSetConst PK_W_ENTERED, 0
    ActorsPauseAll
    h_msgbox_info PKL_ROOM_BLOCKED
    h_closemessage
    h_release

    .balign 4, 0
PKR_MvHide:
    set_invisible
    step_end
PKR_MvApproach:                         // _Movement_ApproachPlayer / _PreQueenHealNPCApproachPlayer
    walk_down 2
    step_end
PKR_MvNpcExit:                          // _Movement_NPCExit
    walk_up 3
    set_invisible
    walk_up
    step_end
PKR_MvHealExit:                         // _Movement_HealNPCExit
    walk_up
    set_invisible
    walk_up
    step_end
PKR_MvDown1:                            // _Movement_NPCApproachMon
    walk_down
    step_end
PKR_MvStatusNpcIn:                      // _Movement_StatusNPCApproachPlayer
    walk_down
    face_left
    delay_16 2
    face_down
    step_end
PKR_MvMonIn:                            // _Movement_MonApproachPlayer
    walk_fast_down
    walk_fast_right 2
    walk_fast_down
    walk_fast_left
    face_down
    step_end
PKR_MvMonAside:                         // _Movement_MonMoveAside
    walk_left
    face_right
    step_end
PKR_MvHealIn:                           // _Movement_HealNPCApproachPlayer
    walk_down 2
    walk_right
    face_down
    step_end
PKR_MvRight:                            // _Movement_Trainer1WalkRight
    walk_right
    step_end
PKR_MvLeft:                             // _Movement_Trainer2WalkLeft
    walk_left
    step_end
PKR_MvDown2:                            // _Movement_DoubleTrainersWalkDown
    walk_down 2
    step_end
PKR_MvT1Exit:                           // _Movement_Trainer1Exit
    walk_up 3
    walk_right
    walk_up
    set_invisible
    walk_up
    step_end
PKR_MvT2Exit:                           // _Movement_Trainer2Exit
    walk_up 3
    walk_left
    walk_up
    set_invisible
    walk_up
    step_end
PKR_MvUp2:                              // _Movement_PlayerWalkUp2
    walk_up 2
    step_end
PKR_MvHealOutLucy:                      // _Movement_HealNPCExitForLucy
    walk_up 3
    set_invisible
    step_end
PKR_MvLucyIn:                           // _Movement_LucyEnter
    set_visible
    walk_down
    step_end
PKR_MvLucyAside:                        // _Movement_LucyMoveAside
    walk_left
    face_right
    step_end
