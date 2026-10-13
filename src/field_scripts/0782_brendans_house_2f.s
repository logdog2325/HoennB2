// Brendan's house 2F (zone 391). Room: data/interior_layouts/, people and signs: data/interiors/391.json.
// Messages: src/text/script/0620_brendans_house_2f.txt (Sapphire's text, Gen 5 capitalisation).
// Actors = Sapphire local ids: 1 the rival (script 21), 14 Mom on the stairs (script 2).
// Scripts 20-31 are the lead's story scenes; 20 (wall clock) and 21 (rival) hold the simple Sapphire lines until then.
// VMJumpIf CMP_STACK jumps when the comparison is FALSE.
#include "asm/field_script.inc"
#include "hoenn.h"

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
    ScriptEntry Script_22
    ScriptEntry Script_23
    ScriptEntry Script_24
    ScriptEntry Script_25
    ScriptEntry Script_26
    ScriptEntry Script_27
    ScriptEntry Script_28
    ScriptEntry Script_29
    ScriptEntry Script_30
    ScriptEntry Script_31
    ScriptEntriesEnd

Script_1:
    VMHalt                      // free

Script_2:                      // Mom upstairs (no script in Sapphire; placeholder: her simple line)
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    WordSetPlayerName 0
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                      // PC: the player's own PC in their room (Black 2's full PC menu), else the rival's e-mail
    ActorsPauseAll
    TrainerCardGetSex 0x8011
    VMStackPush 0x8011
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_RivalsPC
#ifdef HOENN_TEST_CHRP
    PokePartyGetCount 0x8012, 0          // test builds only: an empty party gets two Pokémon so Deposit works
    VMStackPush 0x8012                   // (Black 2 keeps the last one in the party)
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TestPartyDone
    PokePartyAdd 0x8013, SPECIES_MUDKIP, 0, 5
    PokePartyAdd 0x8013, SPECIES_TREECKO, 0, 5
#if (HOENN_TEST_CHRP + 0) >= 2
    PokePartyAdd 0x8013, SPECIES_TORCHIC, 0, 5     // =2: six caught for the Pokédex rating (the party holds six)
    PokePartyAdd 0x8013, SPECIES_POOCHYENA, 0, 5
    PokePartyAdd 0x8013, SPECIES_ZIGZAGOON, 0, 5
    PokePartyAdd 0x8013, SPECIES_WURMPLE, 0, 5
#endif
L_TestPartyDone:
#if (HOENN_TEST_CHRP + 0) >= 2
    FlagSet 2402                         // =2: the Pokédex flag (the PC offers Professor's PC) and 12 Hoenn species caught
    PokeDexRegist 0, SPECIES_TREECKO
    PokeDexRegist 0, SPECIES_GROVYLE
    PokeDexRegist 0, SPECIES_TORCHIC
    PokeDexRegist 0, SPECIES_COMBUSKEN
    PokeDexRegist 0, SPECIES_MUDKIP
    PokeDexRegist 0, SPECIES_MARSHTOMP
    PokeDexRegist 0, SPECIES_POOCHYENA
    PokeDexRegist 0, SPECIES_MIGHTYENA
    PokeDexRegist 0, SPECIES_ZIGZAGOON
    PokeDexRegist 0, SPECIES_LINOONE
    PokeDexRegist 0, SPECIES_WURMPLE
    PokeDexRegist 0, SPECIES_SILCOON
#endif
#endif
    RTCallGlobal 10090                   // this is the player's own room: Black 2's PC script (global file 1244, the
                                         // Pokémon Center PC): SE + "<player> booted up the PC." + "Which PC should be
                                         // accessed?" (Pokémon Storage System, <player>'s PC = Mailbox, ...) + switch off
    VMJump L_PCEnd
L_RivalsPC:
    SEPlay SEQ_SE_MESSAGE
    WordSetPlayerName 0
    SystemMsg 3, 2                       // the rival's PC: Trainer School e-mail
    LastKeyWait
    MsgWinCloseAll
L_PCEnd:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                      // notebook
    ActorsPauseAll
#if (HOENN_TEST_CHRP + 0) >= 2
    PokeDexGiveNational                  // test builds only (=2): the notebook switches the National Dex on (Birch's PC rating)
#endif
    SEPlay SEQ_SE_MESSAGE
    WordSetPlayerName 0
    SystemMsg 4, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                      // GameCube
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 5, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:
    VMHalt                      // free

Script_7:                      // Hoenn region map on the wall
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    WordSetPlayerName 0
    SystemMsg 7, 2
    LastKeyWait
    MsgWinCloseAll
    FadeOutBlackQ
    FadeWait
    CallPlaceSelect 0x8000, 0x8001
    FadeInBlackQ
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:                      // TV (read facing north)
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 8, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

#ifndef HOENN_EMERALD            // Emerald: scenes/emerald/players_house_2f.inc defines 9 (the rival's Poké Ball)
Script_9:
#endif
Script_10:
Script_11:
Script_12:
Script_13:
Script_14:
Script_15:
Script_16:
Script_17:
Script_18:
Script_19:
    VMHalt                      // free

Script_23:
Script_25:
Script_26:
Script_27:
Script_28:
Script_29:
Script_30:
Script_31:
    VMHalt

#define T_BASE 9
#define HOUSE_BRENDAN 1
#include "scenes/players_house_2f.inc"
