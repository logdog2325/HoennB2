// SlateportCity_PokemonFanClub (zone 13): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0019_room_SlateportCity_PokemonFanClub.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch3a
#include "hoenn_trainers.h"  // ch3a
#include "hoenn_story.inc"  // ch3a
#include "scenes/ch3_lib.inc"  // ch3a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Story_FC_Chairman       // 3: object 5  // story:
    ScriptEntry Story_FC_SootheBellWoman // 4: object 4  // story:
    ScriptEntry Story_FC_Reporter       // 5: object 3  // story:
    ScriptEntry Story_FC_Zigzagoon      // 6: object 6  // story:
    ScriptEntry Story_FC_Skitty         // 7: object 7  // story:
    ScriptEntry Story_FC_Azumarill      // 8: object 8  // story:
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
    .balign 4, 0

// ---- story (chapter Ch3 part 3a, ch3a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/SlateportCity_PokemonFanClub/scripts.inc + event_scripts.s's SlateportCity_PokemonFanClub_* (the
// TV reporter). People: data/story/ch3a.json. Lines 2-32 of the text file.
// Black 2 gaps (see the ch3a report): the Chairman's scarves need contest conditions (Cool ... Tough >= 200), which
// Black 2's scripts cannot read (PokePartyGetParam's 20 fields have none) and which no Black 2 item raises, so his
// checks all fail as they would for a Black 2 Pokémon (he says Sapphire's "not bad, not good" line); the TV
// reporter's Easy Chat answers are Black 2's word picker (c3_easy_chat) and its shows stay pending.
#define T_MeetChairman 2
#define T_HowGrowing 3
#define T_NothingElse 4
#define T_HmHm 5
#define T_MorePokeblocks 6
#define T_Impressive 7
#define T_RedScarf 8
#define T_BlueScarf 9
#define T_PinkScarf 10
#define T_GreenScarf 11
#define T_YellowScarf 12
#define T_NoSpace 13
#define T_ShowMe 14
#define T_Adores 15
#define T_TreatWithLove 16
#define T_BagFull 17
#define T_Skitty 18
#define T_Zigzagoon 19
#define T_Azumarill 20
#define T_OpWow 21
#define T_OpThanks 22
#define T_OpQ1 23
#define T_OpQ2 24
#define T_OpQ3 25
#define T_OpMore 26
#define T_OpDone 27
#define T_RepNo 28
#define T_RepEnjoy 29
#define T_LetterAsk 30
#define T_LetterYes 31
#define T_LetterDone 32
#define FC_SOOTHE_BELL_WOMAN 4
#define FC_SCARVES C3_TMP2                  // VAR_TEMP_2: scarves already given
#define FC_CONDITION C3_SEL                 // VAR_TEMP_1: which scarf the lead Pokémon earned (0 none)

Story_FC_Chairman:                          // SlateportCity_PokemonFanClub_EventScript_Chairman
    c3_talk
    h_goto_if_eq VAR_SLATEPORT_FAN_CLUB_STATE, 0, L_FC_FirstAssessment
    h_goto_if_eq VAR_SLATEPORT_FAN_CLUB_STATE, 1, L_FC_TryAssessPokemon
    h_goto_if_eq VAR_SLATEPORT_FAN_CLUB_STATE, 2, L_FC_NoMoreScarves
    h_release
L_FC_FirstAssessment:
    h_setvar VAR_SLATEPORT_FAN_CLUB_STATE, 1
    h_msgbox T_MeetChairman
    VMJump L_FC_AssessLeadMon
L_FC_TryAssessPokemon:
    WorkSetConst FC_SCARVES, 0
    h_call_if_set FLAG_RECEIVED_YELLOW_SCARF, Sub_FC_CountScarf
    h_call_if_set FLAG_RECEIVED_GREEN_SCARF, Sub_FC_CountScarf
    h_call_if_set FLAG_RECEIVED_PINK_SCARF, Sub_FC_CountScarf
    h_call_if_set FLAG_RECEIVED_BLUE_SCARF, Sub_FC_CountScarf
    h_call_if_set FLAG_RECEIVED_RED_SCARF, Sub_FC_CountScarf
    h_goto_if_ne FC_SCARVES, 5, L_FC_NotAllScarves
    h_setvar VAR_SLATEPORT_FAN_CLUB_STATE, 2 // ..._ReceivedAllScarves
L_FC_NotAllScarves:
    h_goto_if_eq VAR_SLATEPORT_FAN_CLUB_STATE, 2, L_FC_NoMoreScarves
    h_msgbox T_HowGrowing
    VMJump L_FC_AssessLeadMon
L_FC_NoMoreScarves:
    h_msgbox T_NothingElse
    h_release
L_FC_AssessLeadMon:                         // ..._ChairmanAssessLeadMon
    h_msgbox T_HmHm
    WorkSetConst FC_CONDITION, 0
    // CheckLeadMonTough / Smart / Cute / Beauty / Cool (>= 200) for every scarf not yet given: not readable in
    // Black 2 (gap above), so FC_CONDITION stays 0. The scarf branches below are Sapphire's, kept for a later port.
    c3_lead_mon
    WordSetPartyPokeSpecies 1, C3_LEAD      // bufferleadmonspeciesname 0
    h_goto_if_eq FC_CONDITION, 1, L_FC_GiveRedScarf
    h_goto_if_eq FC_CONDITION, 2, L_FC_GiveBlueScarf
    h_goto_if_eq FC_CONDITION, 3, L_FC_GivePinkScarf
    h_goto_if_eq FC_CONDITION, 4, L_FC_GiveGreenScarf
    h_goto_if_eq FC_CONDITION, 5, L_FC_GiveYellowScarf
    h_msgbox T_MorePokeblocks               // ..._NoHighConditions
    h_release

    .macro fc_give_scarf label, item, flag, line
\label:
    h_checkitemspace \item, 1, C3_TMP
    h_goto_if_eq C3_TMP, 0, L_FC_NoRoomForScarf
    h_msgbox T_Impressive
    h_setflag \flag
    h_closemessage
    h_giveitem \item, 1
    h_msgbox \line
    h_release
    .endm
    fc_give_scarf L_FC_GiveRedScarf, ITEM_RED_SCARF, FLAG_RECEIVED_RED_SCARF, T_RedScarf
    fc_give_scarf L_FC_GiveBlueScarf, ITEM_BLUE_SCARF, FLAG_RECEIVED_BLUE_SCARF, T_BlueScarf
    fc_give_scarf L_FC_GivePinkScarf, ITEM_PINK_SCARF, FLAG_RECEIVED_PINK_SCARF, T_PinkScarf
    fc_give_scarf L_FC_GiveGreenScarf, ITEM_GREEN_SCARF, FLAG_RECEIVED_GREEN_SCARF, T_GreenScarf
    fc_give_scarf L_FC_GiveYellowScarf, ITEM_YELLOW_SCARF, FLAG_RECEIVED_YELLOW_SCARF, T_YellowScarf
L_FC_NoRoomForScarf:
    h_msgbox T_NoSpace
    h_release
Sub_FC_CountScarf:
    WorkAdd FC_SCARVES, 1
    VMReturn

Story_FC_SootheBellWoman:                   // SlateportCity_PokemonFanClub_EventScript_SootheBellWoman
    c3_talk
    h_goto_if_set FLAG_RECEIVED_SOOTHE_BELL, L_FC_ReceivedSootheBell
    h_msgbox T_ShowMe
    c3_lead_mon                             // GetLeadMonFriendshipScore >= 4: friendship >= 150
    PokePartyGetHappiness C3_TMP, C3_LEAD
    h_goto_if_ge C3_TMP, 150, L_FC_GiveSootheBell
    h_release
L_FC_GiveSootheBell:
    h_closemessage
    h_applymovement FC_SOOTHE_BELL_WOMAN, Common_Movement_ExclamationMark    // playse SE_PIN: the "!" plays its own
    h_waitmovement
    h_applymovement FC_SOOTHE_BELL_WOMAN, Common_Movement_Delay48
    h_waitmovement
    h_msgbox T_Adores
    h_closemessage
    h_giveitem ITEM_SOOTHE_BELL, 1
    h_goto_if_eq HLIB_RESULT, 0, L_FC_BagFull
    h_setflag FLAG_RECEIVED_SOOTHE_BELL
    h_release
L_FC_BagFull:                               // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release
L_FC_ReceivedSootheBell:
    h_msgbox T_TreatWithLove
    h_release

// The TV reporter (event_scripts.s SlateportCity_PokemonFanClub_EventScript_1ADFA0 / _1ADE4D: the "Pokémon Fan Club
// Opinions" show for a nicknamed lead Pokémon, the "Fan Club Letter" otherwise)
Story_FC_Reporter:
    c3_talk
    c3_lead_mon
    PokePartyGetParam C3_TMP, C3_LEAD, 117  // special LeadMonNicknamed (field 0x75: 1 = it has a nickname)
    h_goto_if_eq C3_TMP, 0, L_FC_FanClubLetter
    h_goto_if_set FLAG_TV_SHOW_FAN_CLUB_OPINIONS_PENDING, L_FC_RepEnjoy   // special InterviewBefore
    WordSetPartyPokeSpecies 1, C3_LEAD      // InterviewBefore_PkmnFanClubOpinions: species, nickname
    WordSetPartyPokeName 2, C3_LEAD
    h_yesno T_OpWow, C3_TMP
    h_goto_if_no C3_TMP, L_FC_RepNo
    h_msgbox T_OpThanks
    h_random C3_TMP, 3
    h_goto_if_eq C3_TMP, 1, L_FC_OpQ2
    h_goto_if_eq C3_TMP, 2, L_FC_OpQ3
    h_msgbox T_OpQ1
    VMJump L_FC_OpAsk
L_FC_OpQ2:
    h_msgbox T_OpQ2
    VMJump L_FC_OpAsk
L_FC_OpQ3:
    h_msgbox T_OpQ3
L_FC_OpAsk:
    c3_easy_chat C3_SEL
    h_goto_if_ne C3_SEL, 1, L_FC_RepNo
    h_msgbox T_OpMore
    c3_easy_chat C3_SEL
    h_goto_if_ne C3_SEL, 1, L_FC_RepNo
    h_msgbox T_OpDone
    h_setflag FLAG_TV_SHOW_FAN_CLUB_OPINIONS_PENDING   // special InterviewAfter
    h_release
L_FC_FanClubLetter:                         // ..._1ADE4D
    h_goto_if_set FLAG_TV_SHOW_FAN_CLUB_LETTER_PENDING, L_FC_RepEnjoy
    WordSetPartyPokeSpecies 1, C3_LEAD      // InterviewBefore_FanClubLetter: species
    h_yesno T_LetterAsk, C3_TMP
    h_goto_if_no C3_TMP, L_FC_RepNo
    h_msgbox T_LetterYes
    c3_easy_chat C3_SEL
    h_goto_if_ne C3_SEL, 1, L_FC_RepNo
    h_msgbox T_LetterDone
    h_setflag FLAG_TV_SHOW_FAN_CLUB_LETTER_PENDING
    h_release
L_FC_RepNo:
    h_msgbox T_RepNo
    h_release
L_FC_RepEnjoy:
    h_msgbox T_RepEnjoy
    h_release

Story_FC_Zigzagoon:                         // the Pokémon: cry + line (waitse, playmoncry, msgbox, waitmoncry)
    c3_talk
    h_playmoncry SPECIES_ZIGZAGOON
    h_msgbox T_Zigzagoon
    h_waitmoncry
    h_release
Story_FC_Skitty:
    c3_talk
    h_playmoncry SPECIES_SKITTY
    h_msgbox T_Skitty
    h_waitmoncry
    h_release
Story_FC_Azumarill:
    c3_talk
    h_playmoncry SPECIES_AZUMARILL
    h_msgbox T_Azumarill
    h_waitmoncry
    h_release
#include "common/movement.inc"
    .balign 4, 0
