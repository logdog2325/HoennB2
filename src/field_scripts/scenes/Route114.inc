// Route 114's story people (Sapphire data/maps/Route114/scripts.inc; chapter Ch4, ch4 agent 2026-10-07). Scripts 1-3
// of the zone's generated script file (zone 383); the generated signs follow. Text: src/text/scenes/Route114.txt.
// People and rocks: data/story/ch4.json (uid = 100 + Sapphire local id).
#ifdef SCENE_ENTRIES
    ScriptEntry R114_BerryMan               // 1: object 14
    ScriptEntry R114_RoarGentleman          // 2: object 12
    ScriptEntry R114_Poochyena              // 3: object 13
#else
#include "scenes/ch4_lib.inc"
#define T_BerryGive 0           // Route114_Text_1C5803
#define T_BerryAfter 1          // Route114_Text_1C5861
#define T_BerryDone 2           // Route114_Text_1C5878
#define T_RoarGive 3            // Route114_Text_170154
#define T_RoarAfter 4           // Route114_Text_1701C5
#define T_Bowwow 5              // Route114_Text_1701F9
#define T_BagFull 6             // Text_TooBadBagIsFull

R114_BerryMan:                              // Route114_EventScript_150733 (dotimebasedevents: Black 2's midnight reset)
    c4_talk
    h_goto_if_set FLAG_DAILY_RECEIVED_BERRY_ROUTE114, L_R114_BerryDone
    h_msgbox T_BerryGive
    h_closemessage                          // (Black 2: the item script opens its own window)
    h_random C4_TMP, 5                      // random 5 + 15 + ITEM_CHERI_BERRY: Razz, Bluk, Nanab, Wepear or Pinap
    WorkAdd C4_TMP, ITEM_RAZZ_BERRY         // (Black 2 keeps Gen 3's berry order: Razz = 164 ... Pinap = 168)
    WorkSetConst HLIB_RESULT, 0
    ItemCheckSpace C4_TMP, 1, HLIB_TMP      // giveitem VAR_RESULT (h_giveitem takes a constant)
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_NE, L_R114_BagFull
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, C4_TMP
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
    h_setflag FLAG_DAILY_RECEIVED_BERRY_ROUTE114
    h_msgbox T_BerryAfter
    h_release
L_R114_BerryDone:
    h_msgbox T_BerryDone
    h_release
L_R114_BagFull:
    h_bag_is_full T_BagFull
    h_release

R114_RoarGentleman:                         // Route114_EventScript_150782
    c4_talk
    h_goto_if_set FLAG_RECEIVED_TM05, L_R114_RoarAfter
    h_msgbox T_RoarGive
    h_closemessage                          // (Black 2: the item script opens its own window)
    h_giveitem ITEM_TM05                    // TM05 Roar (Black 2's TM05 is Roar too)
    h_goto_if_eq HLIB_RESULT, 0, L_R114_BagFull
    h_setflag FLAG_RECEIVED_TM05
L_R114_RoarAfter:
    h_msgbox T_RoarAfter
    h_release

R114_Poochyena:                             // Route114_EventScript_1507C3
    c4_mon_cry SPECIES_POOCHYENA, T_Bowwow
    .balign 4, 0
#endif
