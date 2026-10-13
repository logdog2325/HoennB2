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
