// Prof. Birch's Pokémon Lab (zone 396; Sapphire's lab room from data/interior_layouts, people and signs from
// data/interiors/396.json).
// Messages: src/text/script/0625_birch_lab.txt (Sapphire's lab text). Actor 0 = Birch, 1 = Aide, 255 = the player.
// VMJumpIf CMP_STACK jumps when the comparison is FALSE.
// Story after Route 103 (chapter Ch1, the worked example of notes/STORY_PORTING.md): scripts 12-13, map scripts 0793,
// the rival NPC (uid 3, Sapphire object 3) from data/story/ch1.json.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1    // sign: PC
    ScriptEntry Script_2    // sign: book
    ScriptEntry Script_3    // sign: bookshelf
    ScriptEntry Script_4    // sign: PC
    ScriptEntry Script_5    // sign: bookshelf
    ScriptEntry Script_6    // NPC: Aide
    ScriptEntry Script_7    // NPC: Prof. Birch
    ScriptEntry Script_8    // sign: machine (interiors)
    ScriptEntry Script_9    // unused
    ScriptEntry Script_10   // map script (zone init, 0793): the rival's sprite, Birch shown once rescued (Sapphire OnTransition)
    ScriptEntry Script_11   // after Route 101 (reserved there): "I'd like you to have the Pokémon" + nickname
    ScriptEntry Script_12   // lab state 4 (0793 condition): the Pokédex (..._EventScript_GivePokedexEvent)
    ScriptEntry Script_13   // NPC: the rival (..._EventScript_Rival)
#if __has_include("scenes/BirchLab_Postgame.inc")
    ScriptEntry PG_LabDexUpgrade    // 14: post-game, reserved by Littleroot's warp: Emerald's National Dex scene
#ifdef HOENN_EMERALD
    ScriptEntry EM_LabChooseJohto   // 15: Emerald only: lab state 4 of VAR_DEX_UPGRADE_JOHTO_STARTER_STATE (0793 condition): Birch offers the Johto starters
    ScriptEntry EM_LabCyndaquil     // 16: the Poké Ball with Cyndaquil (scenes/emerald/BirchLab_JohtoStarters.inc)
    ScriptEntry EM_LabTotodile      // 17
    ScriptEntry EM_LabChikorita     // 18
#endif
#endif
    ScriptEntriesEnd

Script_1:
Script_4:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 0, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 2, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:
Script_5:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 1, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                         // ..._EventScript_Aide
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush VAR_BIRCH_LAB_STATE
    VMStackPushConst 3
    VMStackCmp CMP_GE
    VMJumpIf CMP_STACK, L_AideFieldwork
    TrainerCardGetSex 0x8011
    VMStackPush 0x8011
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_AideGirl
    ParentActorMsg MSGFILE_SCRIPT, 5, 0, 0        // the Prof enjoys May's help
    VMJump L_AideEnd
L_AideGirl:
    ParentActorMsg MSGFILE_SCRIPT, 6, 0, 0        // the Prof enjoys Brendan's help
    VMJump L_AideEnd
L_AideFieldwork:                                  // before the starter (Birch is out on Route 101): Sapphire's first
    h_goto_if_set FLAG_BIRCH_AIDE_MET, L_AideDeskWork   // talk explains fieldwork, later talks the short line
    h_setflag FLAG_BIRCH_AIDE_MET
    ParentActorMsg MSGFILE_SCRIPT, 3, 0, 0        // Hunh? Prof. Birch? The Prof's away on fieldwork...
    VMJump L_AideEnd
L_AideDeskWork:
    ParentActorMsg MSGFILE_SCRIPT, 4, 0, 0        // the Prof isn't one for desk work
L_AideEnd:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
#if __has_include("scenes/BirchLab_Postgame.inc")
    h_goto_if_eq VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 2, PG_LabBirch   // post-game: Emerald's line after the National Dex
#ifdef HOENN_EMERALD
    h_goto_if_eq VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 5, EM_LabBirchRare   // Emerald: "You can have any one of these three Pokémon!"
#endif
#endif
    h_goto_if_ne VAR_BIRCH_LAB_STATE, 5, L_BirchRoute103    // Sapphire 152D9A: state 5 = after the Pokédex
    h_msgbox 28                                   // Prof. Birch: Countless Pokémon await you!
    VMJump L_BirchDone
L_BirchRoute103:
    TrainerCardGetSex 0x8011
    VMStackPush 0x8011
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_BirchGirl
    ParentActorMsg MSGFILE_SCRIPT, 14, 0, 0       // May should be on Route 103
    VMJump L_BirchEnd
L_BirchGirl:
    ParentActorMsg MSGFILE_SCRIPT, 15, 0, 0       // Brendan should be on Route 103
L_BirchEnd:
    LastKeyWait
L_BirchDone:
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:                                         // the machine (Sapphire's ..._EventScript_Machine), text line 16
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 16, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:
    VMHalt

Script_10:                                        // zone init: Common_EventScript_SetupRivalGfxId
    h_setup_rival_gfx
    // Birch (uid 0, hide flag FLAG_HIDE_BIRCH_IN_LAB in data/interiors/396.json) is in his Lab only once he is rescued:
    // Sapphire's new game sets the flag and Route 101 clears it before its warp here. This port decides it by the Lab's
    // state on every entry (a zone init runs before the room's people appear): before Route 101's rescue (state 0-1)
    // hidden, from state 2 (Route 101 sets it before the warp) on shown. So saves from v16.5 and older, where the flag
    // was never cleared, get Birch back on entering. Sapphire's later moves (ProfBirch_EventScript_UpdateLocation:
    // Birch on Route 101/103 by VAR_BIRCH_STATE after Petalburg) are not ported, so he stays in the Lab after that.
    h_goto_if_lt VAR_BIRCH_LAB_STATE, 2, L_LabHideBirch
    h_clearflag FLAG_HIDE_BIRCH_IN_LAB
    VMJump L_LabBirchDone
L_LabHideBirch:
    h_setflag FLAG_HIDE_BIRCH_IN_LAB
L_LabBirchDone:
#if __has_include("scenes/BirchLab_Postgame.inc")
    VMCall PG_LabInit                             // post-game: the National Dex scene's positions (scenes/BirchLab_Postgame.inc)
#endif
    VMHalt

#define LAB_BIRCH 0
#define LAB_RIVAL 3
Script_12:                                        // ..._EventScript_GivePokedexEvent (lab state 4, on entering)
    h_lock
    h_applymovement 255, Mv_LabWalkToBirch        // ..._Movement_PlayerEnterLabForPokedex
    h_waitmovement
    h_buffer_player                               // ..._EventScript_GivePokedex
    h_msgbox_gendered 17, 18, LAB_BIRCH           // Prof. Birch: Oh, hi! I heard you beat <rival>... this Pokédex.
    h_closemessage
    FlagSet 2402                                  // Black 2's Pokédex flag (the start menu shows it)
    h_setflag FLAG_SYS_POKEDEX_GET
    h_obtain_pokedex 19                           // <player> received the Pokédex! (playfanfare MUS_OBTAIN_ITEM)
    h_msgbox_gendered 20, 21, LAB_BIRCH           // Prof. Birch: The Pokédex is a high-tech tool...
    h_closemessage
    h_applymovement LAB_RIVAL, Mv_LabRivalApproach    // ..._Movement_RivalApproachPlayer
    h_waitmovement
    h_applymovement 255, Mv_LabFaceRight          // Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_buffer_player
    h_goto_if_girl L_LabBrendanBalls
    h_msgbox_actor 22, LAB_RIVAL                  // May: Oh, wow, <player>! You got a Pokédex, too!...
    h_closemessage
    h_giveitem ITEM_POKE_BALL, 5
    h_goto_if_eq HLIB_RESULT, 1, L_LabMayGave
    h_msgbox_actor 26, LAB_RIVAL                  // Oh? Your Bag's full.
L_LabMayGave:
    h_msgbox_actor 23, LAB_RIVAL                  // May: It's fun if you can get a lot of Pokémon!...
    VMJump L_LabPokedexDone
L_LabBrendanBalls:
    h_msgbox_actor 24, LAB_RIVAL                  // Brendan: Huh... So you got a Pokédex, too...
    h_closemessage
    h_giveitem ITEM_POKE_BALL, 5
    h_goto_if_eq HLIB_RESULT, 1, L_LabBrendanGave
    h_msgbox_actor 27, LAB_RIVAL                  // Hey, your Bag's full.
L_LabBrendanGave:
    h_msgbox_actor 25, LAB_RIVAL                  // Brendan: You know it's more fun to have a whole bunch...
L_LabPokedexDone:
    h_closemessage
    h_setvar VAR_BIRCH_LAB_STATE, 5
    h_setflag FLAG_ADVENTURE_STARTED
    h_setvar VAR_ROUTE102_ACCESSIBLE, 1
    h_setvar VAR_LITTLEROOT_RIVAL_STATE, 4
    h_setvar VAR_LITTLEROOT_STATE, 3
    h_release

Script_13:                                        // ..._EventScript_Rival
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_girl L_LabRivalBrendan
    h_msgbox 29                                   // May: I wonder where I should go look for Pokémon next?
    VMJump L_LabRivalDone
L_LabRivalBrendan:
    h_msgbox 30                                   // Brendan: Where should I look for Pokémon next...
L_LabRivalDone:
    ActorMsgClose
    h_release

    .balign 4, 0
Mv_LabWalkToBirch:
    walk_up 7
    step_end
Mv_LabRivalApproach:
    walk_down
    walk_in_place_fastest_left
    step_end
Mv_LabFaceRight:
    walk_in_place_fastest_right
    step_end

Script_11:
    ActorsPauseAll
    FadeInBlackQ                                  // a reserved script starts on a black screen (as Black 2's 0856 Script_17)
    FadeWait
    VMStackPush VAR_STARTER_MON
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_NotTreecko
    WordSetPokeSpecies 1, SPECIES_TREECKO
    VMJump L_Named
L_NotTreecko:
    VMStackPush VAR_STARTER_MON
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Mudkip
    WordSetPokeSpecies 1, SPECIES_TORCHIC
    VMJump L_Named
L_Mudkip:
    WordSetPokeSpecies 1, SPECIES_MUDKIP
L_Named:
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, 7, 0, 1, 0           // "So, <player>. I've heard so much about you... have the Pokémon"
    MEPlay SEQ_ME_POKEGET
    MEWait
    ActorMsg MSGFILE_SCRIPT, 8, 0, 1, 0           // "why not give a nickname to that <species>?"
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_SeeRival
    MsgWinCloseAll
    FadeOutBlackQ
    FadeWait
    CallPokeNameInput 0x8010, 0, 0
    FadeInBlackQ
    FadeWait
L_SeeRival:
    TrainerCardGetSex 0x8011
    VMStackPush 0x8011
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_SeeRivalGirl
    ActorMsg MSGFILE_SCRIPT, 9, 0, 1, 0           // "My kid, May, is out on Route 103... What do you think?"
    VMJump L_SeeRivalAsk
L_SeeRivalGirl:
    ActorMsg MSGFILE_SCRIPT, 10, 0, 1, 0
L_SeeRivalAsk:
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_DontBeThatWay
    VMStackPush 0x8011
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TeachGirl
    ActorMsg MSGFILE_SCRIPT, 11, 0, 1, 0          // "Get May to teach you what it means to be a Trainer."
    VMJump L_LabDone
L_TeachGirl:
    ActorMsg MSGFILE_SCRIPT, 12, 0, 1, 0
L_LabDone:
    LastKeyWait
    MsgWinCloseAll
    WorkSetConst VAR_BIRCH_LAB_STATE, 3
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_DontBeThatWay:
    ActorMsg MSGFILE_SCRIPT, 13, 0, 1, 0          // "Oh, don't be that way. You should go meet my kid."
    VMJump L_SeeRivalAsk
    .balign 4, 0
#if __has_include("scenes/BirchLab_Postgame.inc")
#include "scenes/BirchLab_Postgame.inc"           // post-game: Emerald's National Dex scene (script 14, PG_LabInit, PG_LabBirch)
#include "common/movement.inc"
#endif
