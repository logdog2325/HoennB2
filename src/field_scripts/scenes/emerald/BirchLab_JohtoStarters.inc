// EMERALD's Johto starters (pokeemerald data/maps/LittlerootTown_ProfessorBirchsLab/scripts.inc: OnTransition states 3-6, OnWarp
// SetObjectPosForJohtoStarters, OnFrame ChooseJohtoStarter, the three ball scripts, Birch's state-5 line; emerald_ch11_gameclear,
// 2026-10-12). Included at the end of scenes/BirchLab_Postgame.inc in an Emerald build (it has PGB_* and the National Dex scene).
//
// WHAT IT DOES: after the National Dex upgrade (VAR_DEX_UPGRADE_JOHTO_STARTER_STATE 3), once EVERY Hoenn Pokémon is caught
// (Emerald's HasAllHoennMons: the first 200 of the Hoenn Dex, Jirachi and Deoxys left out), the Lab arms state 4. On entering the Lab
// the player walks up to Birch ("You really have completed the Hoenn region's Pokédex ... You can have any one of these three
// Pokémon!", state 5); Cyndaquil, Totodile and Chikorita are three Poké Balls on the table at (8,4) (9,4) (10,4); Birch asks "So
// the Cyndaquil is your choice?"; YES: the Lv 5 Pokémon, the nickname screen, "Listen, <player>. You've completed the Hoenn
// Pokédex, but your Pokémon journey isn't over...", state 6; the other two balls stay ("You received the promised Pokémon. Better
// leave the others alone."). NO: "Take your time before you decide." Birch in state 5 repeats that you can have any one of them.
//
// THE TABLE (switched on by emerald_rooms, 2026-10-12): Emerald draws the Lab in another layout for this (LAYOUT_..._BIRCHS_LAB_WITH_TABLE:
// a table of three tiles with the balls on it at (8..10, 4), the two boxes at (9,4) (10,4) gone). The Emerald build's Lab is the room
// variant LittlerootTown_ProfessorBirchsLab_Emerald (data/versions.json room_variants.emerald) and its table layout the alt room
// LittlerootTown_ProfessorBirchsLab_Emerald_Table (data/interiors/emerald/396.json alt_rooms, b2tools/emerald_rooms.py), loaded
// while map replace event EMJ_EVENT_TABLE is set: EM_LabJohtoInit sets it for states >= 4 and clears it otherwise, on every
// entry (the event is shared with Mauville Gym's "barriers off" layout, which that Gym also sets on every load).
// (Before: EMJ_JOHTO_ON 0, played through with HOENN_TEST_CHJOHTO=1: notes/EMERALD_STORY.md "emerald_ch11_gameclear".)
// Not ported: `showmonpic` (Black 2 has no such script command found), the PC transfer of a 7th Pokémon (the port refuses, as ch13's
// Beldum ball: "There is no space for another Pokémon.").
#define EMJ_JOHTO_ON 1
#define EMJ_EVENT_TABLE 4                         // map replace event 4 (work 0x4035): the Lab's table layout (shared with Mauville Gym's MG_EVENT_OFF)
#define EMJ_T 38                                 // rows of src/text/script/emerald/0625_birch_lab.txt (tools: work/agents/emerald_ch11_gameclear/tools/mk_text.py)
#define EMJ_T_CHOOSE (EMJ_T + 0)                 // Birch: Oh, <player>! Let's have a look at your Pokédex. ... any one of these three Pokémon!
#define EMJ_T_CYNDAQUIL (EMJ_T + 1)              // Birch: The Fire Pokémon Cyndaquil caught your eye! ... So the Cyndaquil is your choice?
#define EMJ_T_TOTODILE (EMJ_T + 2)
#define EMJ_T_CHIKORITA (EMJ_T + 3)
#define EMJ_T_TAKE_YOUR_TIME (EMJ_T + 4)
#define EMJ_T_LEAVE_OTHERS (EMJ_T + 5)           // You received the promised Pokémon. Better leave the others alone.
#define EMJ_T_RECEIVED (EMJ_T + 6)               // <player> received the <species> from Prof. Birch!
#define EMJ_T_GRASSY_PATCH (EMJ_T + 7)           // Birch: Listen, <player>. You've completed the Hoenn Pokédex, but ...
#define EMJ_T_RARE (EMJ_T + 8)                   // Birch: These are rare Pokémon only found in another region! ...
#define EMJ_T_NICKNAME (EMJ_T + 9)
#define EMJ_T_NO_SPACE (EMJ_T + 10)
#define EMJ_BALL_C 170                           // uids of the three balls (data/story/emerald/e_ch11_johto.json, model 110, Lab tiles (8,4) (9,4) (10,4))
#define EMJ_BALL_T 171
#define EMJ_BALL_K 172
#define EMJ_TMP 0x8030
#define EMJ_SIZE 0x8031
#define EMJ_SLOT 0x8032

#if EMJ_JOHTO_ON
#include "scenes/ch11_dexcount.inc"              // Sub_C11_CountDex (C11_DEXKIND 0 seen / 1 caught -> C11_DEXCOUNT)
#endif

EM_LabJohtoInit:                                 // zone init, first line of PG_LabInit (OnTransition's states 3-6 and OnWarp's 4/5/6)
#ifdef HOENN_TEST_CHROAM
    h_setvar VAR_ROAMER_POKEMON, 1               // test builds only: Mom's scene answered "Blue" (Latios roams, Latias waits on Southern Island)
    pg_roamer_start 0x100, 0                     //   and the roamer started at location 0 (with HOENN_TEST_ROAMER_PLACE0=14 + _ALWAYS: Route 101)
#endif
#ifdef HOENN_TEST_CHJOHTO
    h_goto_if_ge VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 4, L_EMJ_Armed       // test builds only (HOENN_TEST_CHJOHTO=1): the state as if every
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 4                        // Hoenn Pokémon were caught and the dex upgraded
L_EMJ_Armed:
#endif
#if EMJ_JOHTO_ON
    h_goto_if_ne VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 3, L_EMJ_NotReady    // ..._EventScript_CheckReadyForJohtoStarter: HasAllHoennMons
    WorkSetConst C11_DEXKIND, 1
    VMCall Sub_C11_CountDex
    h_goto_if_lt C11_DEXCOUNT, 200, L_EMJ_NotReady                         // (the count of the 202 Hoenn species; Jirachi and Deoxys may be two of the 200)
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 4                        // ..._EventScript_SetReadyForJohtoStarter
L_EMJ_NotReady:
    // LAYOUT: Emerald's setmaplayoutindex LAYOUT_..._WITH_TABLE for states >= 4 (OnTransition's SetJohtoStarterLayout and
    // SetAfterJohtoStarterLayout): the table room while event EMJ_EVENT_TABLE is set, else the Lab; always set both ways, with
    // reload (the zone's matrix is already loaded when its init runs, as Mauville Gym's MG_SHOW_LAYOUT; and the shared event
    // may still be set from Mauville Gym)
    h_goto_if_ge VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 4, L_EMJ_TableLayout
    MapReplaceSetEvent EMJ_EVENT_TABLE, 0, 1
    VMJump L_EMJ_LayoutDone
L_EMJ_TableLayout:
    MapReplaceSetEvent EMJ_EVENT_TABLE, 1, 1
L_EMJ_LayoutDone:
#endif
    h_goto_if_lt VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 4, L_EMJ_Done
    h_goto_if_ge VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 6, L_EMJ_After
    FlagReset FLAG_HIDE_LITTLEROOT_TOWN_BIRCHS_LAB_POKEBALL_CYNDAQUIL      // states 4 and 5: ..._SetObjectPosForJohtoStarters (addobject x3 + the rival)
    FlagReset FLAG_HIDE_LITTLEROOT_TOWN_BIRCHS_LAB_POKEBALL_TOTODILE
    FlagReset FLAG_HIDE_LITTLEROOT_TOWN_BIRCHS_LAB_POKEBALL_CHIKORITA
    FlagReset FLAG_HIDE_RIVAL_BIRCH_LAB
    ObjInitNPCGPos PGB_RIVAL_INDEX, 3, 5 + 1, 0, 5 + 1                     // the rival at (5,5) facing east (Birch stays at (6,4), south)
    VMReturn
L_EMJ_After:                                                               // state 6: the rival is back, wandering near (5,10) (Emerald's AddRivalObject + setobjectxyperm)
    FlagReset FLAG_HIDE_RIVAL_BIRCH_LAB
    ObjInitNPCGPos PGB_RIVAL_INDEX, 1, 5 + 1, 0, 10 + 1
L_EMJ_Done:
    VMReturn

EM_LabChooseJohto:                               // ..._EventScript_ChooseJohtoStarter (lockall; OnFrame state 4: 0793's condition)
    h_lock
    h_applymovement 255, Mv_EMJ_PlayerEnters
    h_waitmovement
    h_buffer_player
    h_msgbox_actor EMJ_T_CHOOSE, PGB_BIRCH       // Birch: Oh, <player>! Let's have a look at your Pokédex. ... You can have any one of these three Pokémon!
    h_closemessage
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 5
    h_release

EM_LabBirchRare:                                 // Birch's script 7 in state 5: ..._EventScript_CanHaveAnyOneOfRarePokemon
    h_msgbox EMJ_T_RARE
    ActorMsgClose
    h_release

    .macro emj_ball species, ask, hide, uid
    h_lock
    h_goto_if_ge VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 6, L_EMJ_AlreadyChose
    h_buffer_player
    h_applymovement PGB_BIRCH, Common_Movement_WalkInPlaceFastestRight     // Birch looks at the table
    h_waitmovement
    h_yesno_actor \ask, PGB_BIRCH, EMJ_TMP                                 // So the <starter> is your choice?  (Emerald shows its picture: not ported)
    h_goto_if_no EMJ_TMP, L_EMJ_TakeYourTime
    h_getpartysize EMJ_SIZE
    h_goto_if_eq EMJ_SIZE, 6, L_EMJ_NoSpace
    h_removeobject \uid, \hide                                             // removeobject: the ball is gone
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    h_buffer_player
    WordSetPokeSpecies 1, \species
    h_msgbox_info EMJ_T_RECEIVED                                           // <player> received the <starter> from Prof. Birch!
    h_waitfanfare
    PokePartyAdd EMJ_SLOT, \species, 0, 5                                  // givemon \species, 5
    h_closemessage
    WordSetPokeSpecies 1, \species
    h_yesno EMJ_T_NICKNAME, EMJ_TMP                                        // Want to give a nickname to the <starter> you received?
    h_goto_if_no EMJ_TMP, L_EMJ_Named
    h_name_received_mon EMJ_SIZE                                           // (the party size before = the new one's slot)
    VMJump L_EMJ_Named
    .endm

EM_LabCyndaquil:                                 // ..._EventScript_Cyndaquil (NPC; lock)
    emj_ball SPECIES_CYNDAQUIL, EMJ_T_CYNDAQUIL, FLAG_HIDE_LITTLEROOT_TOWN_BIRCHS_LAB_POKEBALL_CYNDAQUIL, EMJ_BALL_C
EM_LabTotodile:                                  // ..._EventScript_Totodile
    emj_ball SPECIES_TOTODILE, EMJ_T_TOTODILE, FLAG_HIDE_LITTLEROOT_TOWN_BIRCHS_LAB_POKEBALL_TOTODILE, EMJ_BALL_T
EM_LabChikorita:                                 // ..._EventScript_Chikorita
    emj_ball SPECIES_CHIKORITA, EMJ_T_CHIKORITA, FLAG_HIDE_LITTLEROOT_TOWN_BIRCHS_LAB_POKEBALL_CHIKORITA, EMJ_BALL_K
L_EMJ_Named:                                     // ..._EventScript_Received<Starter>
    h_closemessage
    h_msgbox_actor EMJ_T_GRASSY_PATCH, PGB_BIRCH // Birch: Listen, <player>. You've completed the Hoenn Pokédex, but your Pokémon journey isn't over. ...
    h_closemessage
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 6
    h_release
L_EMJ_AlreadyChose:                              // ..._EventScript_AlreadyChoseJohtoStarter
    h_msgbox_info EMJ_T_LEAVE_OTHERS
    h_closemessage
    h_release
L_EMJ_TakeYourTime:                              // ..._EventScript_TakeYourTime
    h_msgbox_actor EMJ_T_TAKE_YOUR_TIME, PGB_BIRCH
    h_closemessage
    h_release
L_EMJ_NoSpace:                                   // (Emerald: Common_EventScript_NoMoreRoomForPokemon after a PC transfer)
    h_closemessage
    h_msgbox_info EMJ_T_NO_SPACE
    h_closemessage
    h_release

    .balign 4, 0
Mv_EMJ_PlayerEnters:                             // ..._Movement_PlayerEnterLabForJohtoStarter: walk_up x7
    walk_up 7
    step_end
    .balign 4, 0
