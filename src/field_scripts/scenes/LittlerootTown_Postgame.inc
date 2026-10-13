// The National Pokédex, Littleroot's part (postgame_scripts, 2026-10-07): Emerald's dex-upgrade scene (pokeemerald
// data/maps/LittlerootTown/scripts.inc: OnTransition / OnWarp / OnFrame VAR_DEX_UPGRADE_JOHTO_STARTER_STATE,
// LittlerootTown_EventScript_BeginDexUpgradeScene). Included at the end of 0778_littleroot_town.s (guarded); the file
// defines
//  - PG_LittlerootInit (VMCall from the zone init, script 9): Emerald's Hall of Fame sets the state to 1
//    (EverGrandeCity_HallOfFame_EventScript_ReadyDexUpgradeEvent); here the first Littleroot zone init with the game
//    cleared does (the player wakes at home after the credits and first passes ch13's S.S. Ticket scene, as in
//    Emerald). State 2 -> 3 (LeftLabAfterDexUpgrade). Prof. Birch and the rival stand outside the player's door while
//    the state is 1 (Emerald's OnWarp addobject + setobjectxy): two objects per house door (data/story/postgame.json,
//    uids 160-163), the player's gender's pair shown (FLAG_HIDE_DEX_UPGRADE_BRENDANS_DOOR / _MAYS_DOOR).
//  - Script_26: map-script condition VAR_DEX_UPGRADE_JOHTO_STARTER_STATE 1 (0779) = BeginDexUpgradeScene: Birch's "!",
//    his line, the warp into the Lab, where the Lab's script 14 (scenes/BirchLab_Postgame.inc) plays the upgrade.
// Text: line 16 of src/text/script/0618_littleroot_town.txt (Emerald's LittlerootTown_Text_BirchSomethingToShowYouAtLab).
#include "scenes/postgame_lib.inc"
#define PGL_T_SOMETHING_TO_SHOW 16
#define PGL_BIRCH_BOY 160               // at Emerald's (5,10) below Brendan's house door; the rival at (6,10)
#define PGL_RIVAL_BOY 161
#define PGL_BIRCH_GIRL 162              // at (14,10) below May's house door; the rival at (13,10)
#define PGL_RIVAL_GIRL 163
#define PGL_LAB_ZONE 396
#define PGL_LAB_SCENE 14                // the Lab's script 14 (scenes/BirchLab_Postgame.inc): fade in + the upgrade

PG_LittlerootInit:
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_PGL_Objects
    h_goto_if_ne VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 0, L_PGL_Left
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 1
L_PGL_Left:
    h_goto_if_ne VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 2, L_PGL_Objects
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 3        // LittlerootTown_EventScript_LeftLabAfterDexUpgrade
L_PGL_Objects:
    FlagSet FLAG_HIDE_DEX_UPGRADE_BRENDANS_DOOR
    FlagSet FLAG_HIDE_DEX_UPGRADE_MAYS_DOOR
    h_goto_if_ne VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 1, L_PGL_Done
    h_setup_rival_gfx                                      // the rival's sprite (Common_EventScript_SetupRivalGfxId)
    h_goto_if_girl L_PGL_Girl
    FlagReset FLAG_HIDE_DEX_UPGRADE_BRENDANS_DOOR          // ..._SetRivalBirchPosForDexUpgradeMale
    VMReturn
L_PGL_Girl:
    FlagReset FLAG_HIDE_DEX_UPGRADE_MAYS_DOOR              // ..._SetRivalBirchPosForDexUpgradeFemale
L_PGL_Done:
    VMReturn

Script_26:                                      // LittlerootTown_EventScript_BeginDexUpgradeScene (lockall)
    h_lock
    h_goto_if_girl L_PGL_SceneGirl
    h_applymovement PGL_BIRCH_BOY, Common_Movement_ExclamationMark   // (playse SE_PIN: the "!" has its own sound)
    h_waitmovement
    h_delay 80
    h_buffer_player
    h_msgbox_actor PGL_T_SOMETHING_TO_SHOW, PGL_BIRCH_BOY            // Prof. Birch: Well, well, <player>! ... Let's go to my Lab.
    VMJump L_PGL_SceneWarp
L_PGL_SceneGirl:
    h_applymovement PGL_BIRCH_GIRL, Common_Movement_ExclamationMark
    h_waitmovement
    h_delay 80
    h_buffer_player
    h_msgbox_actor PGL_T_SOMETHING_TO_SHOW, PGL_BIRCH_GIRL
L_PGL_SceneWarp:
    h_closemessage
    h_delay 20
    h_warp_scene PGL_LAB_ZONE, 6 + 1, 5 + 1, 0, PGL_LAB_SCENE      // warp MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB, 6, 5
    h_release                                                         // (Lab tiles = Sapphire + (1, 1))
    .balign 4, 0
#ifdef HOENN_TEST_CHPOSTGAME
#include "scenes/postgame_test.inc"
#endif
