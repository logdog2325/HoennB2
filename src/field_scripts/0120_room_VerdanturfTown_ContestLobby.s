// VerdanturfTown_ContestLobby (zone 60): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0070_room_VerdanturfTown_ContestLobby.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch3b
#include "hoenn_trainers.h"  // ch3b
#include "hoenn_story.inc"  // ch3b
#include "scenes/ch3b_lib.inc"  // ch3b

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry VC_Receptionist     // 3: object 1 (VerdanturfTown_ContestLobby_EventScript_153D76, stand-in)  // story:
    ScriptEntry VC_AttractGirl      // 4: object 3 (VerdanturfTown_ContestLobby_EventScript_153E47, TM45)  // story:
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

// ---- story (chapter Ch3 part 3b, ch3b agent 2026-10-07: Sapphire data/maps/VerdanturfTown_ContestLobby/scripts.inc;
// generators must keep everything from this line on; entries above marked "// story:"). People: data/story/ch3b.json
// (uid = Sapphire local id); text lines 2-6 (0-1 are the generated people's).
// Pokémon Contests are decided later (decision 2026-10-07): the receptionist says Sapphire's own reception lines
// (contest_hall.inc's "accepting registrations for {Normal} Rank", Lilycove's "We hope you will participate another
// time.") and registers nobody, as ch3a's Slateport counter; Sapphire's Contest Pass (given here when you have none)
// waits for that decision too. Not placed (S_optional: Contests, Berry Blender): the contest reporter (object 5,
// FLAG_HIDE_CONTEST_REPORTER_VERDANTURF stays set), the Blend Master (object 2, data/scripts/pokeblocks.inc), the
// Berry Blender (12,5)/(10,3), its record board (13,1) and the contest winner's painting (11,1).
#define T_RecAccepting 2
#define T_RecAnotherTime 3
#define T_AttractTM 4
#define T_AttractAfter 5
#define T_BagFull 6

// Pokémon Contests can't run on Black 2: the receptionist offers Black 2's Pokémon Musical instead (musical agent
// 2026-10-18; common/musical.inc, b2tools/patches/musical.py). Text lines 7-20 (T_RecAccepting /
// T_RecAnotherTime stay in the file, unused).
#include "common/musical.inc"
#define T_Musical 7
VC_Receptionist:                    // the Musical's reception (Sapphire's contest receptionist's place)
    c3_talk
    musical_reception T_Musical

VC_AttractGirl:                     // VerdanturfTown_ContestLobby_EventScript_153E47
    c3_talk
    h_goto_if_set FLAG_RECEIVED_TM45, L_VC_AttractAfter
    h_msgbox T_AttractTM            // Oh, my love for Pokémon... If you're entering a Contest, try this move on for size.
    h_closemessage
    h_giveitem ITEM_TM45            // TM45 Attract (Black 2's TM45 is Attract too)
    h_goto_if_eq HLIB_RESULT, 0, L_VC_BagFull
    h_setflag FLAG_RECEIVED_TM45
    h_release
L_VC_BagFull:                       // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release
L_VC_AttractAfter:
    h_msgbox T_AttractAfter         // My feelings for Pokémon... Oh, they attract me so...
    h_release
    .balign 4, 0
