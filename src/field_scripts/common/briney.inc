// Mr. Briney's whereabouts (pokeruby data/event_scripts.s:735-802, :834-837, :919-929), word for word.
// VAR_BRINEY_LOCATION: 1 his house (Route 104), 2 Dewford, 3 Route 109; 0 = on a boat trip (backed up in 0x8008).
// Include at the END of your zone script (after the scripts); call with VMCall. notes/STORY_COMMON.md.
//   Sub_UpdateBrineyLocation    Common_EventScript_UpdateBrineyLocation (Sapphire calls it from the Pokémon Center 1F
//                               map scripts of Oldale, Petalburg, Rustboro, Dewford, Slateport, Mauville, Verdanturf,
//                               Fallarbor, Lavaridge: on entering)
//   Sub_ResetMrBriney           EventScript_ResetMrBriney (Sapphire runs it on whiteout, EventScript_WhiteOut): puts him
//                               and his boat back where VAR_BRINEY_LOCATION says
//   Sub_BackupMrBrineyLocation  EventScript_BackupMrBrineyLocation (boarding his boat: Route 104 house, Dewford, Route 109)
//   Sub_HideMrBriney            EventScript_HideMrBriney (Petalburg Gym, after Norman: he is gone everywhere)
// Black 2 has no whiteout script hook: Sapphire's reset on whiteout is left to the chapter that needs it (Ch2).
#ifndef COMMON_BRINEY_INC
#define COMMON_BRINEY_INC
Sub_UpdateBrineyLocation:
    h_goto_if_unset FLAG_RECEIVED_POKENAV, L_BrineyReturn
    h_goto_if_set FLAG_DEFEATED_PETALBURG_GYM, L_BrineyReturn
    h_goto_if_unset FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104, L_SetBrineyLocationHouse
    h_goto_if_unset FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN, L_SetBrineyLocationDewford
    h_goto_if_unset FLAG_HIDE_MR_BRINEY_ROUTE109, L_SetBrineyLocationRoute109
L_BrineyReturn:
    VMReturn
L_SetBrineyLocationHouse:
    WorkSetConst VAR_BRINEY_LOCATION, 1
    VMReturn
L_SetBrineyLocationDewford:
    WorkSetConst VAR_BRINEY_LOCATION, 2
    VMReturn
L_SetBrineyLocationRoute109:
    WorkSetConst VAR_BRINEY_LOCATION, 3
    VMReturn

Sub_ResetMrBriney:
    h_goto_if_eq VAR_BRINEY_LOCATION, 1, L_MoveMrBrineyToHouse
    h_goto_if_eq VAR_BRINEY_LOCATION, 2, L_MoveMrBrineyToDewford
    h_goto_if_eq VAR_BRINEY_LOCATION, 3, L_MoveMrBrineyToRoute109
    VMReturn
L_MoveMrBrineyToHouse:
    FlagSet FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE109
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109
    FlagReset FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104
    FlagReset FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE
    FlagReset FLAG_HIDE_PEEKO_BRINEY_HOUSE
    VMReturn
L_MoveMrBrineyToDewford:
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE109
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE104
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE
    FlagSet FLAG_HIDE_PEEKO_BRINEY_HOUSE
    FlagReset FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN
    FlagReset FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD
    VMReturn
L_MoveMrBrineyToRoute109:
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE104
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE
    FlagSet FLAG_HIDE_PEEKO_BRINEY_HOUSE
    FlagSet FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD
    FlagReset FLAG_HIDE_MR_BRINEY_ROUTE109
    FlagReset FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109
    VMReturn

Sub_BackupMrBrineyLocation:
    WorkSet 0x8008, VAR_BRINEY_LOCATION
    WorkSetConst VAR_BRINEY_LOCATION, 0
    VMReturn

Sub_HideMrBriney:
    FlagSet FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE109
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE104
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104
    FlagSet FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE
    FlagSet FLAG_HIDE_PEEKO_BRINEY_HOUSE
    WorkSetConst VAR_BRINEY_LOCATION, 0
    VMReturn
    .balign 4, 0
#endif
