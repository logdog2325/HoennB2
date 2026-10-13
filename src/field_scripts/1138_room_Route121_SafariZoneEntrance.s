// Route121_SafariZoneEntrance (zone 569): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0337_room_Route121_SafariZoneEntrance.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Story_SZE_Camper        // 3: object 2, the attendant at (10,2) (Ch8)
    ScriptEntry Story_SZE_Fee           // 4: trigger (8,4) VAR_TEMP_1 0, the entrance fee (Ch8)
    ScriptEntry Story_SZE_Exit          // 5: scene condition VAR_SAFARI_ZONE_STATE 1, back from the Safari Game (Ch8)
    ScriptEntriesEnd

Script_1:                                      // picnicker (17,9), Sapphire Route121_SafariZoneEntrance_EventScript_15C351
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

Script_2:                                      // sign (15,1), Sapphire Route121_SafariZoneEntrance_EventScript_15C487
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

// ---- story (chapter Ch8 part 8b, ch8b agent 2026-10-07: Sapphire data/maps/Route121_SafariZoneEntrance/scripts.inc;
// generators keep everything from this line on)
// Black 2 has no Safari Game (no Safari battle screen with Pokeblocks, bait and rocks; no step or ball limit that a
// script can count), so the Safari Zone is a normal outdoor area. Closest way: the entrance runs Sapphire's flow, the $500
// fee (checks: Pokeblock Case = Black 2's Poffin Case, a free PC Box slot with a full party, the money), the 30 Safari Balls
// are given as items (Black 2's Safari Ball is a Poke Ball with a 1.5x catch rate), the camper inside takes back the
// remaining ones when the player leaves; wild Pokemon are fought and caught in Black 2's normal battles.
// People: data/story/ch8b.json (attendant uid 3 at (8,2), camper uid 2 at (10,2)). Text lines 2-13.
#include "scenes/ch8b_lib.inc"
#define T_FirstTime 2
#define T_EnjoyAgain 3
#define T_Rules 4
#define T_FeeAsk 5
#define T_FeeDecline 6
#define T_NotEnough 7
#define T_ThatWillBe 8
#define T_HereAreBalls 9
#define T_Received 10
#define T_WellLetYouKnow 11
#define T_PCFull 12
#define T_NoCase 13
#define SZE_ATTENDANT 3
#define SZE_FEE 500
#define SZE_BALLS 30
#define SZE_SAFARI_SE_ZONE 40           // SafariZone_Southeast's zone; its door (32,33) = tile (96,97) of the Safari group's matrix
#define SZE_ENTRANCE_ZONE 569

Story_SZE_Camper:                       // Route121_SafariZoneEntrance_EventScript_15C35A
    c8b_talk
    h_yesno T_FirstTime, C8B_SEL        // Welcome to the Safari Zone! Is it your first time here?
    h_goto_if_yes C8B_SEL, L_SZE_Rules
    h_msgbox T_EnjoyAgain               // Come in and enjoy the Safari Zone!
    h_release
L_SZE_Rules:
    h_msgbox T_Rules                    // When you enter the Safari Zone, you start with 30 Safari Balls ...
    h_release

Story_SZE_Fee:                          // Route121_SafariZoneEntrance_EventScript_15C383 (lockall)
    h_lock
    h_applymovement 255, Mv_SZE_PlayerUp
    h_waitmovement
    MoneyWinDisp 31, 1                  // showmoneybox
    h_yesno_actor T_FeeAsk, SZE_ATTENDANT, C8B_SEL     // Welcome to the Safari Zone! All you can catch for just $500! Would you like to play a Safari Game?
    h_goto_if_yes C8B_SEL, L_SZE_Pay
    h_msgbox_actor T_FeeDecline, SZE_ATTENDANT         // Okay. Please play another time!
    VMJump L_SZE_StepAside
L_SZE_Pay:                              // ..._EventScript_15C3B3
    h_checkitem ITEM_POKEBLOCK_CASE, 1, C8B_SEL
    h_goto_if_eq C8B_SEL, 0, L_SZE_NoCase
    PokePartyGetCount C8B_A, 0          // ..._EventScript_15C425: a full party needs a free PC Box slot
    h_goto_if_ne C8B_A, 6, L_SZE_PartyOk
    BoxGetCount C8B_A, 4                // free slots
    h_goto_if_ne C8B_A, 0, L_SZE_PartyOk
    h_msgbox_actor T_PCFull, SZE_ATTENDANT              // Excuse me! Your PC Box is full.
    VMJump L_SZE_StepAside
L_SZE_PartyOk:
    MoneyCheck C8B_SEL, SZE_FEE
    h_goto_if_eq C8B_SEL, 0, L_SZE_NoMoney
    h_msgbox_actor T_ThatWillBe, SZE_ATTENDANT          // That will be $500, please.
    h_closemessage
    MoneySub SZE_FEE
    SEPlay SEQ_SE_SYS_22
    MoneyWinUpdate
    h_msgbox_actor T_HereAreBalls, SZE_ATTENDANT        // Here are your Safari Balls.
    h_closemessage
    h_buffer_player
    ItemAdd ITEM_SAFARI_BALL, SZE_BALLS, C8B_B
    MEPlay SEQ_ME_ITEM                  // playfanfare MUS_OBTAIN_ITEM; message ...; waitfanfare; waitmessage
    SystemMsg T_Received, 2             // <player> received 30 Safari Balls.
    MEWait
    LastKeyWait
    InfoMsgClose
    h_msgbox_actor T_WellLetYouKnow, SZE_ATTENDANT      // We'll let you know when your game is over. So, until then, enjoy yourself, please! ...
    h_closemessage
    MoneyWinClose
    h_applymovement 255, Mv_SZE_ToDoor
    h_waitmovement
    h_setvar VAR_SAFARI_ZONE_STATE, 2   // special EnterSafariMode
    MapChangeWarp SZE_SAFARI_SE_ZONE, 96, 98, 1     // warp MAP_SAFARI_ZONE_SOUTHEAST, 255, 32, 33 (Black 2's own warp: it fades in by itself; FadeOutBlack + MapChangeCore stay black without an arrival script)
                                                    // (32,33) is the building's door: Sapphire's door exit steps the player out to (32,34)
                                                    // before the arrival scene; this warp has no exit step (tested: the player stood in the
                                                    // doorway), so land on (32,34) = (96,98) (walk_sweep 2026-10-12, as wally_walk's Petalburg fix)
    h_release
L_SZE_NoCase:                           // ..._EventScript_15C450
    h_msgbox_actor T_NoCase, SZE_ATTENDANT              // Excuse me! You seem to be without a Pokeblock Case. ...
    VMJump L_SZE_StepAside
L_SZE_NoMoney:                          // ..._EventScript_15C45E
    h_msgbox_actor T_NotEnough, SZE_ATTENDANT           // You don't have enough money. Sorry.
L_SZE_StepAside:                        // ..._EventScript_15C46C
    h_closemessage
    MoneyWinClose
    h_applymovement 255, Mv_SZE_StepRight
    h_waitmovement
    h_release

Story_SZE_Exit:                         // Route121_SafariZoneEntrance_EventScript_15C333 (lockall)
    h_lock
    h_applymovement 255, Mv_SZE_Back
    h_waitmovement
    c8b_take_safari_balls               // special ExitSafariMode
    h_setvar VAR_SAFARI_ZONE_STATE, 0
    h_release

    .balign 4, 0
Mv_SZE_PlayerUp:
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
Mv_SZE_StepRight:                       // Route121_SafariZoneEntrance_Movement_15C47C
    walk_right
    step_end
    .balign 4, 0
Mv_SZE_ToDoor:                          // Route121_SafariZoneEntrance_Movement_15C47E
    walk_left 6
    walk_down
    delay_16
    step_end
    .balign 4, 0
Mv_SZE_Back:                            // Route121_SafariZoneEntrance_Movement_15C348
    walk_up
    walk_right 7
    step_end
    .balign 4, 0
