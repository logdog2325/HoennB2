// Fortree City's story (Sapphire data/maps/FortreeCity/scripts.inc; chapter Ch7, ch7 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file 0032_auto_FortreeCity.s: the
// entries below are scripts 1-5, the generated signs/people follow. Text: src/text/scenes/FortreeCity.txt (T_* below).
// People: data/story/ch7.json (outdoor uid = 100 + Sapphire local id). Map scripts: scenes/FortreeCity_init.inc.
// Route 119's north part (x 24-39, y 0-35: the rival and HM02 Fly, the first invisible Kecleon, Yasu and Hideo) was
// in Fortree's zone 16 while a zone covered whole 32x32 cells; since every map has its own zone up to its edges
// (b2tools/world.py zone_rects, zone_edges 2026-10-08) it is Route 119's zone 463: scenes/Route119.inc.
// Not ported: FortreeCity_OnResume `setstepcallback 2` (the wobbling rope-bridge planks under the player: Black 2 has
// no step callback for scripts).
#ifdef SCENE_ENTRIES
    ScriptEntry FC_Init                 // 1: FortreeCity_OnTransition (zone init)
    ScriptEntry FC_HideKecleons         // 2: scene condition C7_KECLEON_HIDDEN 0 (MOVEMENT_TYPE_INVISIBLE)
    ScriptEntry FC_FieldLoad            // 3: field load / return: the Kecleon is hidden again
    ScriptEntry FC_Woman                // 4: object 3, FortreeCity_EventScript_Woman
    ScriptEntry FC_Kecleon              // 5: object 7, FortreeCity_EventScript_Kecleon
#else
#include "scenes/ch7_lib.inc"
#include "scenes/ch7_test.inc"

#define T_SomethingBlockingGym 0
#define T_ThisTimeIllBeatWinona 1
#define T_SomethingUnseeable 2
#define T_UnseeableUseDevonScope 3
#define T_UsedDevonScopeFled 4

#define FC_KECLEON 107                  // object 7 (FLAG_HIDE_KECLEON_FORTREE)

FC_Init:                                // FortreeCity_OnTransition
#ifdef HOENN_TEST_CH7
    VMCall Test_Ch7Start
#endif
    h_setflag FLAG_VISITED_FORTREE_CITY
    h_keep_banner                       // the Kecleon scene below leaves the place-name banner shown
    VMHalt

FC_HideKecleons:                        // MOVEMENT_TYPE_INVISIBLE of Fortree's Kecleon
    h_keep_banner_end                   // (later scripts close the banner again, as in Black 2)
    h_setvar C7_KECLEON_HIDDEN, 1
    c7_hide_kecleon FC_KECLEON, FLAG_HIDE_KECLEON_FORTREE
    h_waitmovement
    VMHalt

FC_FieldLoad:                           // field rebuilt (after a battle, a menu, a warp): hide them again
    h_setvar C7_KECLEON_HIDDEN, 0
    VMHalt

FC_Woman:                               // FortreeCity_EventScript_Woman
    c7_talk
    h_goto_if_set FLAG_KECLEON_FLED_FORTREE, L_FC_WomanGymAccessible
    h_msgbox T_SomethingBlockingGym     // I want to go to the Pokémon Gym, but something's blocking the way. ...
    h_release
L_FC_WomanGymAccessible:
    h_msgbox T_ThisTimeIllBeatWinona
    h_release

FC_Kecleon:                             // FortreeCity_EventScript_Kecleon (Fortree's own lines: the Kecleon flees)
    c7_talk
    h_checkitem ITEM_DEVON_SCOPE, 1, C7_TMP
    h_goto_if_eq C7_TMP, 1, L_FC_AskUseDevonScope
    h_msgbox T_SomethingUnseeable       // Something unseeable is in the way.
    h_release
L_FC_AskUseDevonScope:
    h_yesno T_UnseeableUseDevonScope, C7_TMP    // ... Want to use the Devon Scope?
    h_goto_if_yes C7_TMP, L_FC_UseDevonScope
    h_release
L_FC_UseDevonScope:
    h_buffer_player
    h_msgbox T_UsedDevonScopeFled       // <player> used the Devon Scope. ... The startled Pokémon fled!
    h_closemessage
    h_applymovement FC_KECLEON, Mv_C7_KecleonAppears
    h_waitmovement
    h_playmoncry SPECIES_KECLEON        // waitse, playmoncry SPECIES_KECLEON, 2, delay 40, waitmoncry
    h_delay 40
    h_waitmoncry
    h_applymovement FC_KECLEON, Mv_FC_KecleonFlee
    h_waitmovement
    h_removeobject FC_KECLEON, FLAG_HIDE_KECLEON_FORTREE
    h_setflag FLAG_KECLEON_FLED_FORTREE
    h_release

    .balign 4, 0
Mv_FC_KecleonFlee:                      // FortreeCity_Movement_KecleonFlee
    walk_right
    step_end
#include "common/movement.inc"
#endif
