// EMERALD's PlayersHouse_1F_EventScript_GetSSTicketAndSeeLatiTV (pokeemerald data/scripts/players_house.inc, written by
// emerald_ch11_gameclear 2026-10-12). Included by scenes/players_house_1f_ch13.inc in an Emerald build in place of Sapphire's
// Script_30 (the same map-script condition, VAR_LITTLEROOT_HOUSES_STATE 3, set by the Hall of Fame: ch13_gameclear.inc).
// Emerald's scene is longer than Sapphire's: Dad brings the S.S. Ticket as before, but Mom then walks over (Dad leaves), says
// he should stay longer, turns the TV on to a Lati news flash ("a Bzzt-colored Pokémon in flight") and asks YOU which colour the
// announcer said: RED or BLUE. That answer is VAR_ROAMER_POKEMON (0 Red, 1 Blue) and starts the roamer: Red = Latias roams,
// Latios waits on Southern Island; Blue = Latios roams, Latias waits (pokeemerald src/roamer.c InitRoamer: gSpecialVar_0x8004
// 0 -> Latias, 1 -> Latios; SouthernIsland_Interior_OnTransition: var 0 -> Latios on the island). Here the roamer is roamer 0 of
// b2tools/patches/roamers.c (Latias Lv 40); `pg_roamer_start 0x100` makes it Latios (an Emerald-only bit of the argument,
// PG_LATI_BY_SEED). The island is scenes/emerald/SouthernIsland_Interior.inc.
// Black 2's TV has no screen: Emerald's `special TurnOnTVScreen` / `TurnOffTVScreen` (the tile swap) and FLAG_SYS_TV_LATIAS_LATIOS
// are left out; the news is a window with no speaker, as ch1's Petalburg Gym report (players_house_1f.inc Script_22).
// Text (both houses' files, the T() rows of src/text/script/emerald/0619_* / 0621_*): T(24) Dad, the ticket; T(25) "ferry ports in
// Slateport and Lilycove" (Emerald's Dad no longer sends you to the Battle Tower); T(26) "back to Petalburg Gym"; T(27) Mom, Dad
// should stay longer; T(30) the news flash; T(31) "Is that a breaking news story?"; T(32) "what color did the announcer say?";
// T(33) "there are still unknown Pokémon"; T(34) Red; T(35) Blue.
// The movements are Emerald's own, for a boy (Brendan's house) and a girl (May's house, mirrored); raw Move codes (up 12, down 13,
// left 14, right 15; faces 0-3 up/down/left/right; walk in place fastest 40-43; delay_8 62, delay_16 63).
#include "scenes/postgame_lib.inc"                         // pg_roamer_start
#define E13_TMP 0x8030
#define E13_OK 0x8031
#define E13_MOM 1                                          // Mom's uid (data/interiors/390.json, 392.json)
#if HOUSE_BRENDAN
#define E13_MOM_X 3                                        // Mom's own tile in the house (Sapphire (2, 6) + the room's origin (1, 0)), facing right
#define E13_MOM_DIR 3
#else
#define E13_MOM_X 9                                        // (Sapphire (8, 6) + (1, 0)), facing left
#define E13_MOM_DIR 2
#endif
#define E13_TV_NEWS T(30)
#define E13_BREAKING T(31)
#define E13_WHICH_COLOR T(32)
#define E13_UNKNOWN T(33)
#define E13_RED T(34)
#define E13_BLUE T(35)

Script_30:                                       // PlayersHouse_1F_EventScript_GetSSTicketAndSeeLatiTV
    ActorsPauseAll
    TrainerCardGetSex E13_TMP
#if HOUSE_BRENDAN
    WorkCmpConst E13_TMP, 0                      // Brendan's house is the boy's own house
#else
    WorkCmpConst E13_TMP, 1                      // May's is the girl's
#endif
    VMJumpIf CMP_EQ, L_E13_Mine
    FinishAllEvents                              // the rival's house: not the scene's place (the scene waits for the player's own)
    ActorsUnpauseAll
    VMHalt
L_E13_Mine:
    ActorSetGPos E13_MOM, E13_MOM_X, 0, 6, E13_MOM_DIR   // Mom is on her own tile now (the zone init's moving-in spots are long past); her walks start here
    ActorCmdExec 255, Mv_E13_PlayerEnters        // call_if_eq PlayerEnterRoomMale / Female
    ActorCmdWait
    ActorCmdExec CH13_NORMAN, Mv_E13_DadFacesPlayer      // Common_Movement_FacePlayer
    ActorCmdWait
    ActorCmdExec CH13_NORMAN, Mv_Exclaim                 // SE_PIN + Common_Movement_ExclamationMark + Delay48
    ActorCmdWait
    VMSleep 10                                   // delay 20
    ActorCmdExec CH13_NORMAN, Mv_E13_DadApproaches       // DadApproachPlayerMale / Female
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, T(24), CH13_NORMAN, 0, 0    // Dad: Hm? Hey, it's <player>! ... This came to you from someone named Mr. Briney.
    LastKeyWait
    MsgWinCloseAll                               // (Black 2: the item script opens its own window)
    ItemCheckSpace ITEM_SS_TICKET, 1, E13_OK     // giveitem ITEM_SS_TICKET (as scenes/players_house_1f_ch13.inc)
    WorkCmpConst E13_OK, 0
    VMJumpIf CMP_EQ, L_E13_Given
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSetConst 0x8000, ITEM_SS_TICKET
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
L_E13_Given:
    ActorMsg MSGFILE_SCRIPT, T(25), CH13_NORMAN, 0, 0    // Dad: Hm, a Ticket for a ferry? If I recall, there are ferry ports in Slateport and Lilycove.
    LastKeyWait
    MsgWinCloseAll
    VMSleep 10                                   // delay 20
    ActorCmdExec E13_MOM, Mv_E13_MomApproachesDad        // MomApproachDadMale / Female (+ Dad faces Mom)
    ActorCmdWait
    ActorCmdExec CH13_NORMAN, Mv_E13_DadFacesMom
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, T(26), CH13_NORMAN, 0, 0    // Dad: I'd better get back to Petalburg Gym. Mom, thanks for looking after the house ...
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Mv_E13_WatchDadLeave       // DadExits: Mom and the player watch, Dad walks out together
    ActorCmdExec E13_MOM, Mv_E13_WatchDadLeave
    ActorCmdExec CH13_NORMAN, Mv_E13_DadLeaves
    ActorCmdWait
    SEPlay SEQ_SE_KAIDAN                         // SE_DOOR
    ActorDelete CH13_NORMAN
    FlagSet FLAG_HIDE_NORMAN_LITTLEROOT          // removeobject
    FlagSet FLAG_RECEIVED_SS_TICKET
    VMSleep 15                                   // delay 30
    ActorCmdExec E13_MOM, Mv_E13_MomApproachesPlayer     // MomApproachPlayerMale / Female
    ActorCmdExec 255, Mv_E13_PlayerFacesMom
    ActorCmdWait
    VMSleep 10                                   // delay 20
    ActorMsg MSGFILE_SCRIPT, T(27), E13_MOM, 0, 0        // Mom: That Dad of yours... He should relax and stay a little longer.
    LastKeyWait
    MsgWinCloseAll
    // setflag FLAG_SYS_TV_LATIAS_LATIOS + special TurnOnTVScreen: the TV model has no screen here
    VMSleep 30                                   // delay 60
    ActorCmdExec E13_MOM, Mv_E13_MomNoticesBroadcast     // MomNoticesLatiBroadcastMale / Female
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, E13_BREAKING, E13_MOM, 0, 0 // Mom: Is that a breaking news story?
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Mv_E13_PlayerToTV          // PlayerApproachTVForLatiMale / Female (+ Mom looks at the TV)
    ActorCmdWait
    ActorCmdExec E13_MOM, Mv_E13_MomLooksAtTV
    ActorCmdWait
    InfoMsg E13_TV_NEWS, 2                       // "We bring you this emergency news flash! ... a Bzzt-colored Pokémon in flight ..."
    LastKeyWait
    InfoMsgClose_0039
    FlagSet FLAG_LATIOS_OR_LATIAS_ROAMING        // clearflag FLAG_SYS_TV_LATIAS_LATIOS, setflag FLAG_LATIOS_OR_LATIAS_ROAMING, TurnOffTVScreen
    VMSleep 10
    ActorCmdExec E13_MOM, Mv_E13_MomComesToPlayer        // MomApproachPlayerAfterTVMale / Female
    ActorCmdExec 255, Mv_E13_PlayerFacesMomAfterTV
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, E13_WHICH_COLOR, E13_MOM, 0, 0   // Mom: <player>, did you catch that? What color did the announcer say that Pokémon was?
    ListMenu_AnchorTopRight 31, 8, 0, 0, E13_TMP        // multichoice 22, 8, MULTI_TV_LATI, TRUE (Red / Blue; B ignored)
    ListMenuAdd E13_RED, 65535, 0
    ListMenuAdd E13_BLUE, 65535, 1
    ListMenuShow
    WorkSet VAR_ROAMER_POKEMON, E13_TMP          // copyvar VAR_ROAMER_POKEMON, VAR_RESULT: 0 Red, 1 Blue
    WorkCmpConst E13_TMP, 0
    VMJumpIf CMP_EQ, L_E13_Red
    pg_roamer_start 0x100                        // Blue: special InitRoamer with Latios (roamer 0, the Latios bit)
    VMJump L_E13_RoamerStarted
L_E13_Red:
    pg_roamer_start 0                            // Red: Latias
L_E13_RoamerStarted:
    ActorMsg MSGFILE_SCRIPT, E13_UNKNOWN, E13_MOM, 0, 0  // Mom: Well, isn't that something! There are still unknown Pokémon.
    LastKeyWait
    MsgWinCloseAll
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE, 4
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE_2, 4
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
#if HOUSE_BRENDAN
Mv_E13_PlayerEnters:                             // PlayersHouse_1F_Movement_PlayerEnterRoomMale
    Move 63, 1
    Move 13, 3
    Move 42, 1
    MoveEnd
Mv_E13_DadFacesPlayer:                           // Dad (5,6) faces the player (8,6)
    Move 3, 1
    MoveEnd
Mv_E13_DadApproaches:                            // ..._DadApproachPlayerMale: walk_right x2
    Move 15, 2
    MoveEnd
Mv_E13_MomApproachesDad:                         // ..._MomApproachDadMale: up, right x4, down, face right
    Move 12, 1
    Move 15, 4
    Move 13, 1
    Move 43, 1
    MoveEnd
Mv_E13_DadFacesMom:                              // ..._DadFaceMomMale
    Move 2, 1
    MoveEnd
Mv_E13_WatchDadLeave:                            // ..._MomAndPlayerWatchDadExit: delay_8, delay_16 x2, face down
    Move 62, 1
    Move 63, 2
    Move 41, 1
    MoveEnd
Mv_E13_DadLeaves:                                // ..._DadExitsMale: down, right, down, delay_8
    Move 13, 1
    Move 15, 1
    Move 13, 1
    Move 62, 1
    MoveEnd
Mv_E13_MomApproachesPlayer:                      // ..._MomApproachPlayerMale: walk_right
    Move 15, 1
    MoveEnd
Mv_E13_PlayerFacesMom:                           // Common_Movement_WalkInPlaceFasterLeft
    Move 42, 1
    MoveEnd
Mv_E13_MomNoticesBroadcast:                      // ..._MomNoticesLatiBroadcastMale: face left, delay_16 x4, face right, delay_16 x2
    Move 42, 1
    Move 63, 4
    Move 43, 1
    Move 63, 2
    MoveEnd
Mv_E13_PlayerToTV:                               // ..._PlayerApproachTVForLatiMale: up, left x4, face up
    Move 12, 1
    Move 14, 4
    Move 40, 1
    MoveEnd
Mv_E13_MomLooksAtTV:                             // Common_Movement_WalkInPlaceFasterLeft
    Move 42, 1
    MoveEnd
Mv_E13_MomComesToPlayer:                         // ..._MomApproachPlayerAfterTVMale: up, left x2
    Move 12, 1
    Move 14, 2
    MoveEnd
Mv_E13_PlayerFacesMomAfterTV:                    // Common_Movement_WalkInPlaceFasterRight
    Move 43, 1
    MoveEnd
#else
Mv_E13_PlayerEnters:                             // ..._PlayerEnterRoomFemale
    Move 63, 1
    Move 13, 3
    Move 43, 1
    MoveEnd
Mv_E13_DadFacesPlayer:
    Move 2, 1
    MoveEnd
Mv_E13_DadApproaches:                            // ..._DadApproachPlayerFemale: walk_left x2
    Move 14, 2
    MoveEnd
Mv_E13_MomApproachesDad:                         // ..._MomApproachDadFemale: up, left x4, down, face left
    Move 12, 1
    Move 14, 4
    Move 13, 1
    Move 42, 1
    MoveEnd
Mv_E13_DadFacesMom:                              // ..._DadFaceMomFemale
    Move 3, 1
    MoveEnd
Mv_E13_WatchDadLeave:
    Move 62, 1
    Move 63, 2
    Move 41, 1
    MoveEnd
Mv_E13_DadLeaves:                                // ..._DadExitsFemale: down, left, down, delay_8
    Move 13, 1
    Move 14, 1
    Move 13, 1
    Move 62, 1
    MoveEnd
Mv_E13_MomApproachesPlayer:                      // ..._MomApproachPlayerFemale: walk_left
    Move 14, 1
    MoveEnd
Mv_E13_PlayerFacesMom:                           // Common_Movement_WalkInPlaceFasterRight
    Move 43, 1
    MoveEnd
Mv_E13_MomNoticesBroadcast:                      // ..._MomNoticesLatiBroadcastFemale: face right, delay_16 x4, face left, delay_16 x2
    Move 43, 1
    Move 63, 4
    Move 42, 1
    Move 63, 2
    MoveEnd
Mv_E13_PlayerToTV:                               // ..._PlayerApproachTVForLatiFemale: up, right x4, face up
    Move 12, 1
    Move 15, 4
    Move 40, 1
    MoveEnd
Mv_E13_MomLooksAtTV:                             // Common_Movement_WalkInPlaceFasterRight
    Move 43, 1
    MoveEnd
Mv_E13_MomComesToPlayer:                         // ..._MomApproachPlayerAfterTVFemale: up, right x2
    Move 12, 1
    Move 15, 2
    MoveEnd
Mv_E13_PlayerFacesMomAfterTV:                    // Common_Movement_WalkInPlaceFasterLeft
    Move 42, 1
    MoveEnd
#endif
    .balign 4, 0
