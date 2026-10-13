// Chapter Ch2: Mr. Briney's boat (Sapphire Route104_EventScript_14EFD5, DewfordTown_EventScript_SailToPetalburg /
// SailToSlateport, Route109_EventScript_14F4D3). Macros only (no code): include it in the body part of a scene.
// Black 2 has no boat object (data/sprite_map.json: OBJ_EVENT_GFX_MR_BRINEYS_BOAT has no code) and no ride on the sea
// map; its boats and ferries move in its 3D demos (common/boat.inc). So: Mr. Briney steps onto the boat and is gone,
// the player follows and vanishes (Sapphire's hideobjectat), the boat music (h_play_briney_boat_music, a stand-in)
// plays, the screen fades out and Black 2's motorboat cutscene plays (h_sail_briney, boats agent 2026-10-07), then
// the destination zone's arrival script (RTReserveScript) shows the landing as Sapphire does.
    .macro ch2_sail zone, x, z, dir, script    // the crossing: after the player is hidden
    h_sail_briney \zone, \x, \z, \dir, \script
    .endm
    .macro ch2_land                            // first lines of an arrival script: the player stands on the boat's
    h_lock                                     // tile (Sapphire's showobjectat at the destination)
    FadeInBlack
    FadeWait
    .endm
    .macro ch2_hide_player                     // hideobjectat LOCALID_PLAYER (boarding)
    h_move 255, 69
    .endm
