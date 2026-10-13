// Mr. Briney at Stern's Shipyard (chapter Ch9, ch9 agent 2026-10-07; Sapphire SlateportCity_SternsShipyard_1F_EventScript_Briney,
// a whole MSGBOX_NPC script: "Mr. Briney: Ah, <player>! It's been too long! ... build one great ship, aye!"). Included by
// 0028_room_SlateportCity_SternsShipyard_1F.s after its text defines (T_Briney = line 8 of the text file, written by
// ch3a). The object (uid 4) is hidden by FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD until the Mind Badge: MossdeepCity_Gym's
// MG_TateAndLiza clears the flag (and FLAG_HIDE_WORKERS_SLATEPORT_HARBOR).
Ch9_SY_Briney:                              // SlateportCity_SternsShipyard_1F_EventScript_Briney
    h_buffer_player
    h_msgbox_npc T_Briney                   // Mr. Briney: Ah, {PLAYER}! It's been too long! ...
