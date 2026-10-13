// Route 123's story (Sapphire data/maps/Route123/scripts.inc; chapter Ch8 part 8b, ch8b agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file 0308_auto_Route123.s: the entry
// below is script 1, the generated signs/people follow. Text: src/text/scenes/Route123.txt (T_* below).
// Person: data/story/ch8b.json (uid 123 = Sapphire object 23, the Grass-type girl). The eight trainers are Black 2
// eye-contact trainers placed by the trainers patch; the three signs are generated. Not here: Sapphire's
// OnTransition special SetRoute123Weather and the ten COORD_EVENT_WEATHER tiles (rain/sun cycle): Black 2's field
// weather is fixed in the zone header and no script command changes it (FieldSetWeather is not used by Black 2's
// scripts), so the route keeps its header weather.
#ifdef SCENE_ENTRIES
    ScriptEntry R123_Girl               // 1: object 23 (Route123_EventScript_151C5D)
#else
#include "scenes/ch8b_lib.inc"

#define T_GirlLoves 0
#define T_GirlThanks 1
#define T_GirlTree 2
#define T_BagFull 3

R123_Girl:                              // TM19 for a Grass-type Pokémon in the party (Black 2's TM19 = Giga Drain, as Sapphire's)
    c8b_talk
    h_goto_if_set FLAG_RECEIVED_TM19, L_R123_Tree
    h_msgbox T_GirlLoves                // I love Grass-type Pokemon! Do you have any Grass-type Pokemon?
    c8b_is_grass_in_party C8B_POS
    h_goto_if_eq C8B_POS, 0, L_R123_NoGrass
    h_msgbox T_GirlThanks               // Oh? You like Grass-type Pokemon, too, don't you? ... you can have this!
    h_closemessage
    h_giveitem ITEM_TM19
    h_goto_if_eq HLIB_RESULT, 0, L_R123_BagFull
    h_setflag FLAG_RECEIVED_TM19
    h_msgbox T_GirlTree                 // I check trees with my Grass-type Pokemon. I'm like a tree doctor.
    h_release
L_R123_NoGrass:
    h_release
L_R123_Tree:
    h_msgbox T_GirlTree
    h_release
L_R123_BagFull:
    h_bag_is_full T_BagFull
    h_release
#endif
