// Verdanturf Town's story (Sapphire data/maps/VerdanturfTown/scripts.inc; chapter Ch3 part 3b, ch3b agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in 0240_auto_VerdanturfTown.s: the entries below are scripts 1-3,
// the generated signs/people follow. Text: src/text/scenes/VerdanturfTown.txt (lines 0-3). People: data/story/ch3b.json
// (uid 100 + Sapphire local id). Map scripts: scenes/VerdanturfTown_init.inc. (Route 116's lost-glasses man, whose tile
// (74,13) was in this zone while a zone covered whole 32x32 cells, is in Route 116's zone since every map has its own
// zone up to its edges: scenes/Route116.inc includes his script; zone_edges 2026-10-08.)
#ifdef SCENE_ENTRIES
    ScriptEntry VT_Init                 // 1: VerdanturfTown_OnTransition (zone init)
    ScriptEntry VT_Twin                 // 2: object 2
    ScriptEntry VT_Boy                  // 3: object 3
#else
#include "scenes/ch3b_lib.inc"

#define T_TwinDigTunnel 0
#define T_TwinDugForLove 1
#define T_BoyBustThrough 2
#define T_BoyEasyToRustboro 3

#define VT_TWIN 102                     // object 2

VT_Init:                                // VerdanturfTown_OnTransition
    h_setflag FLAG_VISITED_VERDANTURF_TOWN
    h_setvar VAR_LINK_CONTEST_ROOM_STATE, 0
    h_setflag FLAG_HIDE_CONTEST_REPORTER_VERDANTURF
    VMHalt

VT_Twin:                                // VerdanturfTown_EventScript_Twin
    c3_talk
    h_goto_if_set FLAG_RUSTURF_TUNNEL_OPENED, L_VT_TwinTunnelOpen
    h_msgbox T_TwinDigTunnel            // My papa told me. He says this tunnel is full of timid Pokémon. ...
    VMJump L_VT_TwinTurnBack
L_VT_TwinTunnelOpen:
    h_msgbox T_TwinDugForLove           // There was a man who dug a tunnel for a lady he loved. ...
L_VT_TwinTurnBack:
    ActorMsgClose
    h_turnobject VT_TWIN, 2             // Common_Movement_FaceOriginalDirection (FACE_LEFT)
    h_release

VT_Boy:                                 // VerdanturfTown_EventScript_Boy
    c3_talk
    h_goto_if_set FLAG_RUSTURF_TUNNEL_OPENED, L_VT_BoyTunnelOpen
    h_msgbox T_BoyBustThrough           // Did you see the cave next to the Pokémon Mart? ...
    h_release
L_VT_BoyTunnelOpen:
    h_msgbox T_BoyEasyToRustboro        // That cave next to the Pokémon Mart is now a tunnel to the other side. ...
    h_release

#endif
