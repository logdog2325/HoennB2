// The Safari Zone's south-east area (Sapphire data/maps/SafariZone_Southeast/scripts.inc; chapter Ch8 part 8b, ch8b
// agent 2026-10-07). converter/gen_map_content.py includes this file twice in 0080_auto_SafariZone_Southeast.s: the
// entries below are scripts 1-5, the generated people follow. Text: src/text/scenes/SafariZone_Southeast.txt (T_*
// below). People: data/story/ch8b.json (outdoor uid = 100 + Sapphire local id; the standalone group's own matrix, the map
// at (64,64)): the camper at the exit (101), the boy and the youngster whose lines mention Pokeblocks (102, 104; the
// generator leaves them out because of the {POKEBLOCK} text code). Black 2 has no Safari Game (scenes in
// 1138_room_Route121_SafariZoneEntrance.s): the area is a normal one, the camper takes the Safari Balls back.
#ifdef SCENE_ENTRIES
    ScriptEntry SZSE_Init               // 1: zone init (MapScript1_160073: the camper steps aside on arrival)
    ScriptEntry SZSE_Arrive             // 2: scene condition VAR_SAFARI_ZONE_STATE 2 (EventScript_16004B)
    ScriptEntry SZSE_Camper             // 3: object 1 (EventScript_1600A7)
    ScriptEntry SZSE_Boy                // 4: object 2 (EventScript_16008C)
    ScriptEntry SZSE_Youngster          // 5: object 4 (EventScript_16009E)
#else
#include "scenes/ch8b_lib.inc"

#define T_CamperAsk 0
#define T_CamperKeep 1
#define T_CamperBye 2
#define T_CamperGoodLuck 3
#define T_BoyBlock 4
#define T_YoungsterFeeder 5

#define SZSE_CAMPER 101
// ObjInitNPCGPos takes the NPC's place in the zone's list: the generated people come first (one now: the man at (16,6)),
// then data/story/ch8b.json's in their order (the camper first). Checked in the built ROM (tests/lib.py zone_npcs).
#define SZSE_CAMPER_IDX 1
#define SZSE_X(x) (64+(x))               // Sapphire tile -> tile of the Safari group's matrix
#define SZSE_Z(z) (64+(z))
#define SZE_ENTRANCE_ZONE 569

SZSE_Init:                              // SafariZone_Southeast_MapScript1_160073
    h_goto_if_ne VAR_SAFARI_ZONE_STATE, 2, L_SZSE_InitDone
    ObjInitNPCGPos SZSE_CAMPER_IDX, 1, SZSE_X(31), 0, SZSE_Z(34)    // setobjectxyperm 1, 31, 34
L_SZSE_InitDone:
    VMHalt

SZSE_Arrive:                            // SafariZone_Southeast_EventScript_16004B (lockall)
    h_lock
    h_setvar 0x4001, 0                  // VAR_TEMP_1
    h_applymovement 255, Mv_SZSE_PlayerDown
    h_waitmovement
    h_applymovement SZSE_CAMPER, Mv_SZSE_CamperToDoor       // back in front of the door: (31,34) -> (32,34), the tile the player
    h_waitmovement                      // just left (the entrance's warp lands on (32,34), Sapphire's door step: walk_sweep 2026-10-12)
    h_setvar VAR_SAFARI_ZONE_STATE, 0   // (setobjectxyperm 1, 32, 34: the camper's template tile already)
    h_release

SZSE_Camper:                            // SafariZone_Southeast_EventScript_1600A7
    c8b_talk
    h_goto_if_eq 0x4001, 0, L_SZSE_First
    h_yesno T_CamperAsk, C8B_SEL        // You still have time left. Would you like to exit the Safari Zone now?
    h_goto_if_yes C8B_SEL, L_SZSE_Leave
    h_msgbox T_CamperKeep               // Please enjoy the rest of your wild adventure!
    h_release
L_SZSE_First:                           // EventScript_1600D1
    h_setvar 0x4001, 1
    h_msgbox T_CamperGoodLuck           // Good luck! If you need anything, don't hesitate to tell me, please!
    h_release
L_SZSE_Leave:                           // EventScript_1600E0
    h_msgbox T_CamperBye                // Okay. I'll take back your remaining Safari Balls. Thank you for playing. ...
    h_closemessage
    h_getplayerfacing C8B_SEL           // Sapphire VAR_FACING: 2 up, 4 right (here 0 up, 3 right); the camper stands west of the
    h_goto_if_eq C8B_SEL, 0, L_SZSE_FacingUp                // arrival tile here, so the player also talks to him facing left
    h_goto_if_eq C8B_SEL, 2, L_SZSE_FacingLeft
    h_applymovement SZSE_CAMPER, Mv_SZSE_CamperDown      // EventScript_16011F (facing right)
    h_waitmovement
    h_applymovement 255, Mv_SZSE_PlayerRight
    h_waitmovement
    VMJump L_SZSE_Warp
L_SZSE_FacingLeft:                      // (not in Sapphire) the camper steps up, the player walks left past him. Only ran
                                        // while the camper stood west of the door; he now stands in front of it with the
                                        // wall east of him, so nobody talks to him facing left (walk_sweep 2026-10-12)
    h_applymovement SZSE_CAMPER, Mv_SZSE_CamperUp
    h_waitmovement
    h_applymovement 255, Mv_SZSE_PlayerLeft
    h_waitmovement
    VMJump L_SZSE_Warp
L_SZSE_FacingUp:                        // EventScript_160105
    h_applymovement SZSE_CAMPER, Mv_SZSE_CamperLeft
    h_waitmovement
    h_applymovement 255, Mv_SZSE_PlayerUp
    h_waitmovement
L_SZSE_Warp:                            // EventScript_160139: VAR_SAFARI_ZONE_STATE 1, ExitSafariMode, warpdoor entrance (2, 5)
    h_setvar VAR_SAFARI_ZONE_STATE, 1
    MapChangeWarp SZE_ENTRANCE_ZONE, 3, 6, 1        // warpdoor MAP_ROUTE121_SAFARI_ZONE_ENTRANCE, 255, 2, 5
    h_release

SZSE_Boy:                               // SafariZone_Southeast_EventScript_16008C
    h_msgbox_npc T_BoyBlock
SZSE_Youngster:                         // SafariZone_Southeast_EventScript_16009E
    h_msgbox_npc T_YoungsterFeeder

    .balign 4, 0
Mv_SZSE_PlayerDown:                     // SafariZone_Southeast_Movement_160087
    walk_down
    step_end
    .balign 4, 0
Mv_SZSE_CamperToDoor:                   // SafariZone_Southeast_Movement_160089
    walk_right
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_SZSE_CamperUp:
    walk_up
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_SZSE_PlayerLeft:                     // (L_SZSE_FacingLeft, which no longer runs: its face-up step went to keep the
    walk_left                           //  script file's size, so the ROM's file layout stays the same)
    step_end
    .balign 4, 0
Mv_SZSE_PlayerUp:                       // SafariZone_Southeast_Movement_16014B
    walk_up
    step_end
    .balign 4, 0
Mv_SZSE_PlayerRight:                    // SafariZone_Southeast_Movement_16014D
    walk_right
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
Mv_SZSE_CamperLeft:                     // SafariZone_Southeast_Movement_160150
    walk_left
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_SZSE_CamperDown:                     // SafariZone_Southeast_Movement_160153
    walk_down
    walk_in_place_fastest_up
    step_end
#endif
