// LilycoveCity_DepartmentStore_1F (zone 196): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0254_room_LilycoveCity_DepartmentStore_1F.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch8a
#include "hoenn_story.inc"  // ch8a
#include "scenes/ch8a_lib.inc"  // ch8a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry DS1_LotteryClerk        // 6: object 2 (Lottery Corner)  // story:
    ScriptEntry DS1_Azumarill           // 7: object 6  // story:
    ScriptEntry DS1_Init                // 8: zone init (0393): VAR_DEPT_STORE_FLOOR = 0, for the elevator  // story:
    ScriptEntriesEnd

Script_1:                                      // beauty (8,2), Sapphire LilycoveCity_DepartmentStore_1F_EventScript_Greeter
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

Script_2:                                      // woman_2 (14,5), Sapphire LilycoveCity_DepartmentStore_1F_EventScript_PokefanF
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

Script_3:                                      // little_girl_2 (4,4), Sapphire LilycoveCity_DepartmentStore_1F_EventScript_LittleGirl
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

Script_4:                                      // man_3 (3,6), Sapphire LilycoveCity_DepartmentStore_1F_EventScript_PokefanM
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

Script_5:                                      // sign (0,8), Sapphire LilycoveCity_DepartmentStore_1F_EventScript_FloorNamesSign
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 4, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/LilycoveCity_DepartmentStore_1F/scripts.inc + data/text/lottery_corner.inc. The greeter, the
// two shoppers and the floor sign are the shops agent's (above). People: data/story/ch8a.json. Lines 5-19 of the text
// file.
// Black 2 gap, the Lottery Corner: its scripts cannot read a Pokémon's ID number (PokePartyGetParam has no OT-ID
// field; boxes cannot be scanned at all). Stand-in with Sapphire's odds and wording: every Pokémon the player
// owns shares ONE ID number (VAR_LOTTERY_ID, drawn once per save: the Trainer Card's number is not readable), the
// ticket is a random number from 0 to 65534, and the matching trailing digits (2-5) give Sapphire's prizes. The
// lead Pokémon is the one that "matches". Proposal: a small overlay patch that adds PokePartyGetParam field 7 (OT ID).
#define T_DrawTicket 5
#define T_PickTicket 6
#define T_TicketNumber 7
#define T_MatchesPartyMon 8
#define T_ComeBackTomorrow 9
#define T_VisitAgain 10
#define T_NoMatch 11
#define T_VisitAgain2 12
#define T_TwoDigits 13
#define T_ThreeDigits 14
#define T_FourDigits 15
#define T_FiveDigits 16
#define T_NoRoom 17
#define T_PrizeHolding 18
#define T_Azumarill 19
DS1_LotteryClerk:                           // LilycoveCity_DepartmentStore_1F_EventScript_LotteryClerk
    c3_talk                                 // lock, faceplayer (dotimebasedevents: Black 2 resets FLAG_DAILY_* itself)
    h_buffer_player
    h_goto_if_ne VAR_LOTTERY_PRIZE, 0, L_DS1_PrizeFromEarlier
    h_goto_if_set FLAG_DAILY_PICKED_LOTTO_TICKET, L_DS1_ComeBackTomorrow
    h_yesno T_DrawTicket, C8_A
    h_goto_if_no C8_A, L_DS1_VisitAgain
    h_setflag FLAG_DAILY_PICKED_LOTTO_TICKET
    ParentActorMsg MSGFILE_SCRIPT, T_PickTicket, 0, 0           // message + waitmessage
    Random C8_B, 65535                      // special RetrieveLotteryNumber (stand-in: a random ticket)
    h_goto_if_ne VAR_LOTTERY_ID, 0, L_DS1_HaveId
    Random VAR_LOTTERY_ID, 65535            // the shared ID number of the player's Pokémon (see the gap above)
    h_addvar VAR_LOTTERY_ID, 1
L_DS1_HaveId:
    WordSetNumber 1, C8_B, 5                // special BufferLottoTicketNumber
    h_msgbox T_TicketNumber
    h_move 2, 43                            // walk_in_place_fastest_right
    h_playse SE_PC_ON
    h_delay 220                             // DoLotteryCornerComputerEffect (the screen animation: not drawn)
    h_delay 10
    ActorSetEyeToEye                        // Common_Movement_FacePlayer
    VMCall Sub_DS1_PickTicket               // special PickLotteryCornerTicket -> C8_C = 0 none, 1-4 = digits - 1
    h_goto_if_eq C8_C, 0, L_DS1_NoMatch
    c3_lead_mon                             // the lead Pokémon "matches" (all of them share the ID)
    WordSetPartyPokeName 1, C3_LEAD
    h_msgbox T_MatchesPartyMon              // TicketMatchesPartyMon
    h_goto_if_eq C8_C, 2, L_DS1_ExpShare
    h_goto_if_eq C8_C, 3, L_DS1_MaxRevive
    h_goto_if_eq C8_C, 4, L_DS1_MasterBall
    h_bufferitemname 1, ITEM_PP_UP          // sLotteryPrizes: PP Up, Exp. Share, Max Revive, Master Ball
    h_msgbox T_TwoDigits
    h_closemessage                          // (the obtain-item script opens its own window: script_check)
    h_giveitem ITEM_PP_UP, 1
    h_goto_if_eq HLIB_RESULT, 0, L_DS1_PrizePPUp
    VMJump L_DS1_VisitAgain2
L_DS1_ExpShare:                             // the Exp. Share is the player's key item (Mr. Stone gave it): a second one
    h_bufferitemname 1, ITEM_RARE_CANDY     // cannot be held, so the third prize is a Rare Candy
    h_msgbox T_ThreeDigits
    h_closemessage                          // (the obtain-item script opens its own window: script_check)
    h_giveitem ITEM_RARE_CANDY, 1
    h_goto_if_eq HLIB_RESULT, 0, L_DS1_PrizeRareCandy
    VMJump L_DS1_VisitAgain2
L_DS1_MaxRevive:
    h_bufferitemname 1, ITEM_MAX_REVIVE
    h_msgbox T_FourDigits
    h_closemessage                          // (the obtain-item script opens its own window: script_check)
    h_giveitem ITEM_MAX_REVIVE, 1
    h_goto_if_eq HLIB_RESULT, 0, L_DS1_PrizeMaxRevive
    VMJump L_DS1_VisitAgain2
L_DS1_MasterBall:
    h_bufferitemname 1, ITEM_MASTER_BALL
    h_msgbox T_FiveDigits
    h_closemessage                          // (the obtain-item script opens its own window: script_check)
    h_giveitem ITEM_MASTER_BALL, 1
    h_goto_if_eq HLIB_RESULT, 0, L_DS1_PrizeMasterBall
    VMJump L_DS1_VisitAgain2
L_DS1_PrizePPUp:                            // LilycoveCity_DepartmentStore_1F_EventScript_RecordPrizeNoRoom
    h_setvar VAR_LOTTERY_PRIZE, ITEM_PP_UP
    VMJump L_DS1_NoRoom
L_DS1_PrizeRareCandy:
    h_setvar VAR_LOTTERY_PRIZE, ITEM_RARE_CANDY
    VMJump L_DS1_NoRoom
L_DS1_PrizeMaxRevive:
    h_setvar VAR_LOTTERY_PRIZE, ITEM_MAX_REVIVE
    VMJump L_DS1_NoRoom
L_DS1_PrizeMasterBall:
    h_setvar VAR_LOTTERY_PRIZE, ITEM_MASTER_BALL
L_DS1_NoRoom:                               // ..._EventScript_NoRoomForPrize
    h_msgbox T_NoRoom
    h_release
L_DS1_PrizeFromEarlier:                     // ..._EventScript_GivePrizeFromEarlier
    h_msgbox T_PrizeHolding
    h_closemessage                          // (the obtain-item script opens its own window: script_check)
    c8_giveitem_var VAR_LOTTERY_PRIZE
    h_goto_if_eq HLIB_RESULT, 0, L_DS1_NoRoom
    h_setvar VAR_LOTTERY_PRIZE, 0
    h_release
L_DS1_ComeBackTomorrow:
    h_msgbox T_ComeBackTomorrow
    h_release
L_DS1_VisitAgain:
    h_msgbox T_VisitAgain
    h_release
L_DS1_NoMatch:
    h_msgbox T_NoMatch
L_DS1_VisitAgain2:
    h_msgbox T_VisitAgain2
    h_release

Sub_DS1_PickTicket:                         // C8_B = ticket, VAR_LOTTERY_ID = the ID: C8_C = trailing digits matched - 1
    WorkSetConst C8_C, 0                    // (GetMatchingDigits: consecutive equal digits from the right, up to 5;
    WorkSetConst C8_D, 0                    // 2 or more win)
    WorkSet C8_E, C8_B
    WorkSet C8_F, VAR_LOTTERY_ID
L_DS1_Digit:
    WorkCmpConst C8_D, 5
    VMJumpIf CMP_GE, L_DS1_DigitsDone
    WorkSet C8_G, C8_E
    WorkMod C8_G, 10
    WorkSet C8_H, C8_F
    WorkMod C8_H, 10
    WorkCmpWork C8_G, C8_H
    VMJumpIf CMP_NE, L_DS1_DigitsDone
    WorkDiv C8_E, 10
    WorkDiv C8_F, 10
    WorkAdd C8_D, 1
    VMJump L_DS1_Digit
L_DS1_DigitsDone:
    WorkCmpConst C8_D, 2
    VMJumpIf CMP_LT, L_DS1_PickReturn
    WorkSet C8_C, C8_D
    WorkSub C8_C, 1
L_DS1_PickReturn:
    VMReturn

DS1_Azumarill:                              // LilycoveCity_DepartmentStore_1F_EventScript_Azumarill
    c8_mon_cry SPECIES_AZUMARILL, T_Azumarill

DS1_Init:                                   // Sapphire's SetDepartmentStoreFloorVar reads the dynamic warp; here every floor
    h_setvar VAR_DEPT_STORE_FLOOR, 0        // sets its own number when it loads (the elevator reads it)
    VMHalt
    .balign 4, 0
