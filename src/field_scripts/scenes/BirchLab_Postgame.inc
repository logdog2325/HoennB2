// The National Pokédex, the Lab's part (postgame_scripts, 2026-10-07): Emerald's LittlerootTown_ProfessorBirchsLab_
// EventScript_UpgradeToNationalDex (pokeemerald data/maps/LittlerootTown_ProfessorBirchsLab/scripts.inc), its OnWarp
// object positions (SetObjectPosForDexUpgrade) and Birch's line after it (EventScript_GrassyPatchWaiting). Included by
// 0792_birch_lab.s (guarded): PG_LabInit (VMCall from the zone init, script 10), PG_LabDexUpgrade (script 14, reserved by
// Littleroot's BeginDexUpgradeScene warp: it starts on a black screen), PG_LabBirch (from Birch's script 7).
// Black 2's own upgrade: PokeDexGiveNational (its National Dex flag; Black 2's 0856.s gives it with SEQ_ME_KEYITEM).
// Lab tiles = Sapphire/Emerald tiles + (1, 1). Text: lines 31-37 of src/text/script/0625_birch_lab.txt (Emerald's, the
// {RIVAL} line written twice: May for a boy, Brendan for a girl).
// Johto starters (state 4-6: HasAllHoennMons, every Hoenn Pokémon caught, which Sapphire alone cannot reach): Emerald build only,
// scenes/emerald/BirchLab_JohtoStarters.inc (switched off until the Lab has Emerald's table layout).
// Not ported: the rival's later Lab lines (he leaves with the scene, as Sapphire's rival stays at home), Scott's call.
#include "scenes/postgame_lib.inc"
#define PGB_T_UPGRADE_MAY 31
#define PGB_T_UPGRADE_BRENDAN 32
#define PGB_T_MAY_SO_COOL 33
#define PGB_T_BRENDAN_THANK_ME 34
#define PGB_T_ALL_DONE 35
#define PGB_T_UPGRADED 36
#define PGB_T_GRASSY_PATCH 37
#define PGB_BIRCH 0
#define PGB_AIDE 1
#define PGB_RIVAL 3
#define PGB_RIVAL_INDEX 2               // the rival's place in the zone's NPC list (Birch 0, the aide 1, then ch1's rival)
#define PGB_AIDE_INDEX 1
// The two starters the player didn't choose (postgame_dex 2026-11-09): rows of 0625 after Gen 3's (0-37), the follower
// aide's (38-43 in every version: placeholders the followers' text fills with our C on, 0792 Script_9) and, in Emerald, the
// Johto starters' (44-54, scenes/emerald/BirchLab_JohtoStarters.inc EMJ_T)
#ifdef HOENN_EMERALD
#define PGS_T 55
#else
#define PGS_T 44
#endif
#define PGS_T_OFFER (PGS_T + 0)          // NEW, approved 2026-11-09: Prof. Birch: Oh, <player>! If it isn't our new Champion! ... I'd like you to take them both!
#define PGS_T_SECOND (PGS_T + 1)         // NEW, approved 2026-11-09: Prof. Birch: Oh, <player>! I've still got the other one for you. Here you go!
#define PGS_T_RECEIVED (PGS_T + 2)       // <player> received the <species> from Prof. Birch! (pokeemerald's Johto starter line)
#define PGS_T_NICKNAME (PGS_T + 3)       // Want to give a nickname to the <species> you received? (pokeemerald's)
#define PGS_T_TRANSFERRED (PGS_T + 4)    // <species> was transferred to someone's PC. (gText_PkmnTransferredSomeonesPC)
#define PGS_T_FULL (PGS_T + 5)           // There's no more room for Pokémon! ... (gText_NoMoreRoomForPokemon)
#define PGS_T_FULL_BIRCH (PGS_T + 6)     // NEW, approved 2026-11-09: Prof. Birch: Oh, no room at all? Make some space in your Boxes, then come and see me. ...
#define PGS_T_AFTER (PGS_T + 7)          // NEW, approved 2026-11-09: Prof. Birch: Take good care of them! How about that... All three of the Pokémon ...
#define PGS_SPECIES 0x8038              // script works of this file (0x8030 HLIB_TMP .. 0x8037 are the libraries')
#define PGS_SIZE 0x8039
#define PGS_TMP 0x803A
#define PGS_SLOT 0x803B

PG_LabInit:                             // OnWarp states 1-2: LittlerootTown_ProfessorBirchsLab_EventScript_SetObjectPosForDexUpgrade
#ifdef HOENN_EMERALD
    VMCall EM_LabJohtoInit              // Emerald: the Johto starters' states 3-6 (scenes/emerald/BirchLab_JohtoStarters.inc)
#endif
    h_goto_if_eq VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 1, L_PGB_Positions
    h_goto_if_eq VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 2, L_PGB_Positions
    h_goto_if_ne VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 3, L_PGB_InitDone
    FlagSet FLAG_HIDE_RIVAL_BIRCH_LAB   // after the scene the rival has gone home again
L_PGB_InitDone:
    VMReturn
L_PGB_Positions:
    FlagReset FLAG_HIDE_RIVAL_BIRCH_LAB                     // addobject LOCALID_BIRCHS_LAB_RIVAL
    ObjInitNPCGPos PGB_RIVAL_INDEX, 0, 5 + 1, 0, 5 + 1      // the rival at (5,5) facing north
    ObjInitNPCGPos PGB_AIDE_INDEX, 3, 10 + 1, 0, 10 + 1     // the aide at (10,10) facing east (Birch stays at (6,4), south)
    VMReturn

PG_LabDexUpgrade:                       // ..._EventScript_UpgradeToNationalDex (lockall; OnFrame state 1)
    h_lock
    FadeInBlack                         // (the reserved script of Littleroot's warp starts on black)
    FadeWait
    h_delay 30
    h_buffer_player
    h_msgbox_gendered PGB_T_UPGRADE_MAY, PGB_T_UPGRADE_BRENDAN, PGB_BIRCH   // Prof. Birch: Now... <player> and <rival>, ...
    h_closemessage
    h_applymovement PGB_BIRCH, Mv_PGB_BirchRetrievePokedexes
    h_waitmovement
    h_delay 20
    SEPlay SEQ_SE_DECIDE1               // playse SE_CLICK x4 [guess: notes/STORY_SPECIALS.md]
    h_delay 10
    SEPlay SEQ_SE_DECIDE1
    h_delay 10
    SEPlay SEQ_SE_DECIDE1
    h_delay 10
    SEPlay SEQ_SE_DECIDE1
    h_delay 20
    h_applymovement PGB_RIVAL, Common_Movement_WalkInPlaceFastestRight
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_buffer_player
    h_goto_if_girl L_PGB_Brendan
    h_msgbox_actor PGB_T_MAY_SO_COOL, PGB_RIVAL            // May: Eheheh! It's so cool that even my Pokédex is getting updated! ...
    VMJump L_PGB_PCOn
L_PGB_Brendan:
    h_msgbox_actor PGB_T_BRENDAN_THANK_ME, PGB_RIVAL       // Brendan: I went out all over Hoenn ... Yep, you're lucky, <player>!
L_PGB_PCOn:
    h_closemessage
    h_playse SE_PC_ON
    h_waitse
    h_delay 20
    h_applymovement PGB_BIRCH, Mv_PGB_BirchReturnPokedex
    h_waitmovement
    h_applymovement PGB_RIVAL, Common_Movement_WalkInPlaceFastestUp
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor PGB_T_ALL_DONE, PGB_BIRCH                // Prof. Birch: Okay, all done!
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    h_buffer_player
    h_msgbox_info PGB_T_UPGRADED                            // <player>'s Pokédex was upgraded to the National Mode!
    h_waitfanfare
    h_closemessage
    PokeDexGiveNational                                     // setflag FLAG_SYS_NATIONAL_DEX + special EnableNationalPokedex
    h_msgbox_actor PGB_T_GRASSY_PATCH, PGB_BIRCH            // Prof. Birch: But listen. You've become the Champion, ...
    h_closemessage
    h_setflag FLAG_HIDE_DEX_UPGRADE_BRENDANS_DOOR           // setflag FLAG_HIDE_LITTLEROOT_TOWN_BIRCH / _RIVAL
    h_setflag FLAG_HIDE_DEX_UPGRADE_MAYS_DOOR
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 2
    // (Emerald: Scott's Battle Frontier call. Here, the user's post-game roamers: the beasts and birds start roaming
    // once the National Dex is there, notes/POSTGAME.md)
    VMCall Sub_PG_StartBeastsAndBirds
    h_release

PG_LabBirch:                            // Birch's talk in state 2 (..._EventScript_Birch -> GrassyPatchWaiting)
    h_msgbox PGB_T_GRASSY_PATCH
    ActorMsgClose
    h_release

// ---- the two Hoenn starters the player didn't choose (postgame_dex 2026-11-09; user decision 2026-11-09, every version) --
// After the Champion, Birch gives the two Pokémon of his Bag the player did not pick on Route 101 (VAR_STARTER_MON: 0 Treecko,
// 1 Torchic, 2 Mudkip), Lv 5, one after the other in the Bag's order, as Gen 3's starter gift (fanfare, "received",
// nickname). A full party sends one to the PC (Black 2's BoxAdd, the PC's next free place; Gen 3's transfer line, no
// nickname: Black 2 has no command to name a boxed Pokémon); with the PC full too he keeps it for later
// (VAR_BIRCH_OTHER_STARTERS counts what he gave: 0, 1, 2). No Gen 3 game has this: the lines marked NEW (approved by the user
// 2026-11-09) are new. Before the National Dex scene (VAR_DEX_UPGRADE_JOHTO_STARTER_STATE 1, the Lab set for it) he waits. Emerald's
// Johto starters (states 3-6) are untouched: this comes first in Birch's talk, their lines after it.
PG_LabStartersDue:                      // HLIB_TMP = 1 when Birch's talk is the starters' (0792 Script_7)
    WorkSetConst HLIB_TMP, 0
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_PGS_DueDone
    h_goto_if_ge VAR_BIRCH_OTHER_STARTERS, 2, L_PGS_DueDone
    h_goto_if_eq VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 1, L_PGS_DueDone
    WorkSetConst HLIB_TMP, 1
L_PGS_DueDone:
    VMReturn

PG_LabStarters:                         // (from 0792 Script_7: ActorsPauseAll, the talk sound, facing the player)
    h_buffer_player
    h_goto_if_ne VAR_BIRCH_OTHER_STARTERS, 0, L_PGS_Second
    h_msgbox PGS_T_OFFER
    VMJump L_PGS_Give
L_PGS_Second:
    h_msgbox PGS_T_SECOND
L_PGS_Give:
    VMCall Sub_PGS_Species              // PGS_SPECIES = the next one
    h_closemessage
    h_getpartysize PGS_SIZE
    h_goto_if_lt PGS_SIZE, 6, L_PGS_Party
    BoxGetCount PGS_TMP, 5              // free places in the PC's Boxes (scrcmd_pokemon.c s0121_BoxGetCount, kind 5)
    h_goto_if_eq PGS_TMP, 0, L_PGS_Full
    VMCall Sub_PGS_Fanfare
    BoxAdd PGS_TMP, PGS_SPECIES, 0, 5   // Black 2's give into the PC (s0122_BoxAdd: a Poké Ball, as PokePartyAdd)
    WordSetPokeSpecies 1, PGS_SPECIES
    h_msgbox_info PGS_T_TRANSFERRED     // <species> was transferred to someone's PC.
    h_closemessage
    VMJump L_PGS_Given
L_PGS_Party:
    VMCall Sub_PGS_Fanfare
    PokePartyAdd PGS_SLOT, PGS_SPECIES, 0, 5                       // givemon <species>, 5
    WordSetPokeSpecies 1, PGS_SPECIES
    h_yesno PGS_T_NICKNAME, PGS_TMP                                // Want to give a nickname to the <species> you received?
    h_goto_if_no PGS_TMP, L_PGS_Given
    h_name_received_mon PGS_SIZE                                   // (the party size before = the new one's slot)
L_PGS_Given:
    h_closemessage
    h_addvar VAR_BIRCH_OTHER_STARTERS, 1
    h_goto_if_lt VAR_BIRCH_OTHER_STARTERS, 2, L_PGS_Give          // and the other one
    h_buffer_player
    h_msgbox PGS_T_AFTER
    ActorMsgClose
    h_release
L_PGS_Full:
    h_msgbox_info PGS_T_FULL            // There's no more room for Pokémon! The Pokémon Boxes are full ...
    h_closemessage
    h_msgbox PGS_T_FULL_BIRCH
    ActorMsgClose
    h_release

Sub_PGS_Fanfare:                        // the fanfare and "<player> received the <species> from Prof. Birch!"
    h_playfanfare MUS_OBTAIN_ITEM
    h_buffer_player
    WordSetPokeSpecies 1, PGS_SPECIES
    h_msgbox_info PGS_T_RECEIVED
    h_waitfanfare
    h_closemessage
    VMReturn

Sub_PGS_Species:                        // PGS_SPECIES = the first (count 0) or second (count 1) starter not chosen, in the
    WorkSetConst PGS_SPECIES, SPECIES_TREECKO                      //   Bag's order Treecko, Torchic, Mudkip
    h_goto_if_eq VAR_STARTER_MON, 0, L_PGS_NotTreecko
    h_goto_if_eq VAR_BIRCH_OTHER_STARTERS, 0, L_PGS_SpeciesDone   // (Treecko is the first unless it was chosen)
    h_goto_if_eq VAR_STARTER_MON, 2, L_PGS_Torchic                 // Torchic chosen: Mudkip second; Mudkip chosen: Torchic
    VMJump L_PGS_Mudkip
L_PGS_NotTreecko:                       // Treecko chosen: Torchic, then Mudkip
    h_goto_if_ne VAR_BIRCH_OTHER_STARTERS, 0, L_PGS_Mudkip
L_PGS_Torchic:
    WorkSetConst PGS_SPECIES, SPECIES_TORCHIC
    VMReturn
L_PGS_Mudkip:
    WorkSetConst PGS_SPECIES, SPECIES_MUDKIP
L_PGS_SpeciesDone:
    VMReturn

Sub_PG_StartBeastsAndBirds:             // Raikou, Entei, Suicune, Articuno, Zapdos, Moltres start roaming (once)
    h_goto_if_set FLAG_ROAMING_BEASTS_BIRDS_STARTED, L_PGB_Started
    h_setflag FLAG_ROAMING_BEASTS_BIRDS_STARTED
    pg_roamer_start 1
    pg_roamer_start 2
    pg_roamer_start 3
    pg_roamer_start 4
    pg_roamer_start 5
    pg_roamer_start 6
L_PGB_Started:
    VMReturn

    .balign 4, 0
Mv_PGB_BirchRetrievePokedexes:          // LittlerootTown_ProfessorBirchsLab_Movement_BirchRetrievePokedexes
    walk_left
    walk_in_place_fastest_down
    delay_16 2
    walk_right
    walk_in_place_fastest_down
    delay_16 2
    walk_right
    walk_down 4
    walk_right 3
    walk_in_place_fastest_up
    step_end
Mv_PGB_BirchReturnPokedex:              // ..._Movement_BirchReturnPokedex
    walk_left 3
    walk_up 4
    walk_left
    walk_in_place_fastest_down
    step_end
#ifdef HOENN_EMERALD
#include "scenes/emerald/BirchLab_JohtoStarters.inc"   // Emerald's Johto starters (emerald_ch11_gameclear; switched off until the Lab has its table)
#endif
