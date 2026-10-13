// Mt. Chimney's story (Sapphire data/maps/MtChimney/scripts.inc + data/scripts/magma_chimney.inc, Sapphire branches;
// chapter Ch5, ch5 agent 2026-10-07). converter/gen_map_content.py includes this file twice in 0038_auto_MtChimney.s:
// the entries below are scripts 1-14, the generated sign ("Jagged Path") follows. Text: src/text/scenes/MtChimney.txt
// (lines MC_T_* below). People and the Meteorite machine: data/story/ch5.json (uid = 100 + Sapphire local id).
// Map scripts: scenes/MtChimney_init.inc (zone init = script 1). Matt (object 3), the grunt (object 22), Shelby,
// Melissa, Sheila and Shirley are eye-contact trainers (Black 2's global trainer script: intro, battle, after line).
// Sapphire's MSGBOX_SIGN said by an object (the grunts, the Poochyena) = the object's line without turning to you.
// EMERALD (emerald_ch45_magma 2026-10-12; pokeemerald MtChimney/scripts.inc): Team Magma is the villain here (Ruby's flow with
// Emerald's own people): Maxie at the Meteorite machine (object 2 = the entries' "MC_Archie"), Tabitha and two grunts as eye-contact
// trainers, Archie (object 1, "MC_Maxie") asking you to stop them; the entries keep their Sapphire numbers and roles, the models
// swap per object (data/story/ch5.json "model_emerald"), the lines are Emerald's (src/text/scenes/emerald/MtChimney.txt, same
// MC_T_* indices) and the six Magma grunts say six different things (Sapphire's four entries 9-12 plus Emerald-only entries
// 15 and 16, so the Emerald-only entries come last). The two Poochyena lines swap with the teams. The battle names the
// leader through hoenn_version.inc (TRAINER_MT_CHIMNEY_GRUNT_3: Archie 3 / Maxie 3 / Emerald's Maxie).
#ifdef SCENE_ENTRIES
    ScriptEntry MC_Init                 // 1: MtChimney_MapScript1_15CF87 (zone init)
    ScriptEntry MC_Maxie                // 2: object 1 (MtChimney_EventScript_1B2C95)
    ScriptEntry MC_Archie               // 3: object 2 (MtChimney_EventScript_1B2CCB)
    ScriptEntry MC_Machine              // 4: the Meteorite machine (Sapphire sign at 14,6; data/story/ch5.json sign)
    ScriptEntry MC_LavaCookie           // 5: object 9 (MtChimney_EventScript_15CF95)
    ScriptEntry MC_Magma1               // 6: object 7 (15D0F5)
    ScriptEntry MC_Magma2               // 7: object 6 (15D0FE)
    ScriptEntry MC_Magma3               // 8: object 8 (15D107)
    ScriptEntry MC_AquaAnnoying         // 9: objects 13, 17 (15D13E)
    ScriptEntry MC_AquaStomp            // 10: object 16 (15D150)
    ScriptEntry MC_AquaStayOut          // 11: object 5 (15D159)
    ScriptEntry MC_AquaHose             // 12: objects 4, 10 (15D162)
    ScriptEntry MC_PoochyenaAqua        // 13: Team Aqua's Poochyena (15D16B)
    ScriptEntry MC_PoochyenaMagma       // 14: Team Magma's Poochyena (15D174)
#ifdef HOENN_EMERALD
    ScriptEntry MC_MagmaGrunt1          // 15: Emerald: object 17 (BusyMagmaGrunt1, "That annoying Team Aqua...")
    ScriptEntry MC_MagmaGrunt6          // 16: Emerald: object 10 (BusyMagmaGrunt6, "keep making more land")
#endif
#else
#include "hoenn_key_items.h"
#include "hoenn_version.inc"             // TRAINER_MT_CHIMNEY_GRUNT_3 ...
#ifdef HOENN_EMERALD
#include "scenes/em_magma_lib.inc"
#endif
#ifdef HOENN_TEST_CH5
#include "scenes/ch5_test.inc"
#endif
#define MC_T_LavaCookie 0
#define MC_T_ThankYouDear 1
#define MC_T_FineThen 2
#define MC_T_NoMoney 3
#define MC_T_BagFull 4
#define MC_T_Magma1 5
#define MC_T_Magma2 6
#define MC_T_Magma3 7
#define MC_T_AquaAnnoying 8
#define MC_T_AquaStomp 9
#define MC_T_AquaStayOut 10
#define MC_T_AquaHose 11
#define MC_T_PoochAqua 12
#define MC_T_PoochMagma 13
#define MC_T_MachineAsk 14
#define MC_T_MachineRemoved 15
#define MC_T_MachineLeft 16
#define MC_T_MachineNoResponse 17
#define MC_T_MachineStoring 18
#define MC_T_MaxieStop1 19
#define MC_T_MaxieStop2 20
#define MC_T_ArchieMachine 21
#define MC_T_ArchieYouAgain 22
#define MC_T_ArchieWhatever 23
#define MC_T_MaxieThanks 24
#define MC_T_MagmaMessing 25            // Emerald only (the two extra Magma grunts' lines)
#define MC_T_MagmaMoreLand 26
#define MC_MAXIE 101
#define MC_ARCHIE 102
#define MC_MATT 103
#define MC_GRUNT 122
#define MC_GRUNT_F 129                  // Emerald only (data/story/emerald/e_ch5.json)
#define MC_X(x) (9+(x))                 // Sapphire tile -> tile of Mt. Chimney's own matrix (b2tools/world.py
#define MC_Z(z) (11+(z))                // standalone group MtChimney: the map at (9, 11))
#define MC_FACING 0x8024                // VAR_FACING (Black 2 directions: 0 up, 1 down, 2 left, 3 right)

    .macro mc_obj_sign n                // msgbox X, MSGBOX_SIGN on an object: lockall, the line, releaseall
    h_lock
    SEPlay SEQ_SE_MESSAGE
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0
    LastKeyWait
    ActorMsgClose
    h_release
    .endm

MC_Init:                                // MtChimney_MapScript1_15CF87 (SetupEvilTeamGfxIds: the Aqua/Magma sprites
    h_setvar VAR_JAGGED_PASS_ASH_WEATHER, 1     // are placed directly). ON_RESUME setstepcallback 1 (ash on the
#ifdef HOENN_TEST_CH5                   // grass): Black 2 has no ash, the snowy trees stand in (notes/DECISIONS.md)
    VMCall Test_Ch5Start                // test builds only: the chapter's start state (scenes/ch5_test.inc; Emerald: emerald_ch45_magma)
#endif
#ifdef HOENN_TEST_CH5_SKIP              // test builds only: the eye-contact people on the way to the machine count as beaten
    h_settrainerflag TRAINER_MT_CHIMNEY_GRUNT_2
#if HOENN_TEST_CH5_SKIP >= 2
    h_settrainerflag TRAINER_MT_CHIMNEY_GRUNT_1    // (Matt / Tabitha)
#endif
#ifdef HOENN_EMERALD
    h_settrainerflag TRAINER_GRUNT_MT_CHIMNEY_1
#endif
#endif
    VMHalt

MC_Maxie:                               // MtChimney_EventScript_1B2C95
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_set FLAG_EVIL_LEADER_PLEASE_STOP, L_MC_MaxieAgain
    h_msgbox MC_T_MaxieStop1            // Maxie: Oh, <player>! Please, you must stop Team Aqua for me! ...
    VMJump L_MC_MaxieDone
L_MC_MaxieAgain:
    h_msgbox MC_T_MaxieStop2            // Maxie: <player>! Please, you've got to stop Team Aqua for me! ...
L_MC_MaxieDone:
    h_closemessage
    h_turnobject MC_MAXIE, 2            // Common_Movement_FaceOriginalDirection (FACE_LEFT)
    h_setflag FLAG_EVIL_LEADER_PLEASE_STOP
    h_release

MC_Archie:                              // MtChimney_EventScript_1B2CCB (Emerald: MtChimney_EventScript_Maxie)
    h_lock
    SEPlay SEQ_SE_MESSAGE
#ifdef HOENN_EMERALD
    em_bgm_magma                        // playbgm MUS_ENCOUNTER_MAGMA, FALSE
#endif
    h_msgbox_actor MC_T_ArchieMachine, MC_ARCHIE    // The power contained in the Meteorite... (still at the machine)
    h_closemessage
    h_faceplayer                        // Common_Movement_FacePlayer
    h_applymovement MC_ARCHIE, Common_Movement_ExclamationMark  // playse SE_PIN: the "!" plays its own sound
    h_waitmovement
    h_applymovement MC_ARCHIE, Common_Movement_Delay48
    h_waitmovement
    h_msgbox_actor MC_T_ArchieYouAgain, MC_ARCHIE   // Archie: You again... Now listen. All life depends on the sea. ...
    h_closemessage
    h_trainerbattle TRAINER_MT_CHIMNEY_GRUNT_3   // trainerbattle_no_intro (Sapphire: Archie 3, Ruby: Maxie 3, Emerald: TRAINER_MAXIE_MT_CHIMNEY); in battle:
    h_msgbox_actor MC_T_ArchieWhatever, MC_ARCHIE   // "What?! I, Archie, was caught off guard?!"
    h_closemessage
    h_delay 30
    h_fadescreen_black
    h_removeobject MC_ARCHIE, FLAG_HIDE_EVIL_TEAM_MT_CHIMNEY
    ActorDelete MC_MATT                 // removeobject 3 / 22 (same hide flag)
    ActorDelete MC_GRUNT
#ifdef HOENN_EMERALD
    ActorDelete MC_GRUNT_F              // Emerald: the second grunt (object 29) leaves with them
#endif
    ActorSetGPos MC_MAXIE, MC_X(10), 0, MC_Z(12), 0  // setobjectxyperm 1, 10, 12 + addobject 1 (Black 2 keeps actors
    h_fadescreen_from_black                          // spawned out of view: Maxie is moved there on the black screen)
    h_getplayerfacing MC_FACING
    h_call_if_eq MC_FACING, 3, Sub_MC_MaxieFromRight     // VAR_FACING 4 (east)
    h_call_if_eq MC_FACING, 0, Sub_MC_MaxieFromBelow     // VAR_FACING 2 (north)
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_buffer_player
    h_msgbox_actor MC_T_MaxieThanks, MC_MAXIE       // Maxie: <player>! Thank you! ...
    h_closemessage
    h_call_if_eq MC_FACING, 3, Sub_MC_MaxieLeaveRight
    h_call_if_eq MC_FACING, 0, Sub_MC_MaxieLeaveBelow
    h_removeobject MC_MAXIE, FLAG_HIDE_OTHER_TEAM_MT_CHIMNEY
    h_setflag FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY
    h_clearflag FLAG_HIDE_PROF_COSMO_FALLARBOR
    h_setflag FLAG_HIDE_PROF_COSMO_METEOR_FALLS
#ifdef HOENN_EMERALD
    h_clearflag FLAG_HIDE_MT_CHIMNEY_LAVA_COOKIE_LADY   // the Lava Cookie lady is back (hidden at the start in Emerald)
#endif
    h_release

Sub_MC_MaxieFromRight:                  // MtChimney_EventScript_1B2D7D
    h_applymovement MC_MAXIE, Mv_MC_15D025
    h_waitmovement
    VMReturn
Sub_MC_MaxieFromBelow:                  // MtChimney_EventScript_1B2D88
    h_applymovement MC_MAXIE, Mv_MC_15D036
    h_waitmovement
    VMReturn
Sub_MC_MaxieLeaveRight:                 // MtChimney_EventScript_1B2D93
    h_applymovement MC_MAXIE, Mv_MC_15D02D
    h_waitmovement
    VMReturn
Sub_MC_MaxieLeaveBelow:                 // MtChimney_EventScript_1B2D9E
    h_applymovement MC_MAXIE, Mv_MC_15D03E
    h_waitmovement
    VMReturn

MC_Machine:                             // MtChimney_EventScript_15D17D (lockall; MSGBOX_DEFAULT: nobody says it)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_unset FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY, L_MC_MachineStoring
    h_goto_if_set FLAG_RECEIVED_METEORITE, L_MC_MachineDone
    SystemMsg MC_T_MachineAsk, 2        // A Meteorite is fitted on a mysterious machine... Do you want to remove it?
    YesNoWin HLIB_TMP
    h_goto_if_no HLIB_TMP, L_MC_MachineLeave
    h_buffer_player
    h_msgbox_info MC_T_MachineRemoved   // <player> removed the Meteorite from the mysterious machine.
    h_closemessage
    h_giveitem ITEM_METEORITE
    h_setflag FLAG_RECEIVED_METEORITE
    h_release
L_MC_MachineLeave:
    h_buffer_player
    h_msgbox_info MC_T_MachineLeft      // <player> left the Meteorite where it was.
    h_closemessage
    h_release
L_MC_MachineDone:
    h_msgbox_info MC_T_MachineNoResponse    // This mysterious machine... It makes no response whatsoever.
    h_closemessage
    h_release
L_MC_MachineStoring:
    h_msgbox_info MC_T_MachineStoring   // ... The machine seems to be storing energy in the Meteorite.
    h_closemessage
    h_release

MC_LavaCookie:                          // MtChimney_EventScript_15CF95 (showmoneybox: Black 2's money window)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    MoneyWinDisp 31, 1
    h_yesno MC_T_LavaCookie, HLIB_TMP   // Lava Cookies are Mt. Chimney's local specialty. Try one. It's just $200.
    h_goto_if_no HLIB_TMP, L_MC_CookieNo
    MoneyCheck HLIB_TMP, 200            // checkmoney 200 (1 = enough)
    h_goto_if_eq HLIB_TMP, 0, L_MC_CookieNoMoney
    h_msgbox MC_T_ThankYouDear          // Thank you, dear!
    h_closemessage
    h_checkitemspace ITEM_LAVA_COOKIE, 1, HLIB_TMP
    h_goto_if_ne HLIB_TMP, 1, L_MC_CookieGive
    MoneySub 200                        // removemoney 200 + updatemoneybox
    MoneyWinUpdate
L_MC_CookieGive:
    h_giveitem ITEM_LAVA_COOKIE
    h_goto_if_eq HLIB_RESULT, 0, L_MC_CookieBagFull
    MoneyWinClose
    h_release
L_MC_CookieBagFull:
    h_msgbox MC_T_BagFull               // Too bad! The Bag is full...
    MoneyWinClose
    h_release
L_MC_CookieNo:
    h_msgbox MC_T_FineThen              // Oh, fine then.
    MoneyWinClose
    h_release
L_MC_CookieNoMoney:
    h_msgbox MC_T_NoMoney               // Oh, dear. You can't buy a thing if you've not got the money.
    MoneyWinClose
    h_release

MC_Magma1:                              // 15D0F5: Darn... Team Aqua outnumbers us! ...
    mc_obj_sign MC_T_Magma1
MC_Magma2:                              // 15D0FE: If they expand the sea, there'll be less habitats ...
    mc_obj_sign MC_T_Magma2
MC_Magma3:                              // 15D107: Team Aqua wants to expand the sea... How's that for insane?
    mc_obj_sign MC_T_Magma3
MC_AquaAnnoying:                        // 15D13E: That annoying Team Magma... They always mess with our plans!
    mc_obj_sign MC_T_AquaAnnoying
MC_AquaStomp:                           // 15D150: Go! Stomp Team Magma! And expand the sea!
    mc_obj_sign MC_T_AquaStomp
MC_AquaStayOut:                         // 15D159: Stay out of our way, okay? ...
    mc_obj_sign MC_T_AquaStayOut
MC_AquaHose:                            // 15D162: Yeah! Hose them down!
    mc_obj_sign MC_T_AquaHose
MC_PoochyenaAqua:                       // 15D16B: Bushaa!
    mc_obj_sign MC_T_PoochAqua
MC_PoochyenaMagma:                      // 15D174: Bufoh! (Emerald: Bushaa!, the lines swap with the teams: text indices 12 / 13)
    mc_obj_sign MC_T_PoochMagma
#ifdef HOENN_EMERALD
MC_MagmaGrunt1:                         // BusyMagmaGrunt1: That annoying Team Aqua... They always mess with our plans!
    mc_obj_sign MC_T_MagmaMessing
MC_MagmaGrunt6:                         // BusyMagmaGrunt6: We're going to keep making more land!
    mc_obj_sign MC_T_MagmaMoreLand
#endif

    .balign 4, 0
Mv_MC_15D025:                           // Maxie comes up to the player's left (player facing east)
    walk_up 6
    walk_right
    step_end
Mv_MC_15D02D:
    walk_left
    walk_down 7
    step_end
Mv_MC_15D036:                           // (player facing north)
    walk_up 5
    walk_right 2
    step_end
Mv_MC_15D03E:
    walk_left 2
    walk_down 7
    step_end
#include "common/movement.inc"
#endif
