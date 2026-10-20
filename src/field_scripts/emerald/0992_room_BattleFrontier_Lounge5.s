// BattleFrontier_Lounge5 (zone 496; header scripts 992 -> own file 2092), Pokémon Emerald NDS only (frontier_lounges,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_Lounge5/scripts.inc: the Nature Girl, who says what a Pokémon of your
// party is thinking by its nature (ShowNatureGirlMessage: sNatureGirlMessages[GetNature]), and three people. The nature:
// Black 2's own nature field of the Pokémon (PokePartyGetParam field 112, the one PokeParty_SetNature writes, arm9
// 0x0201d5e0), the same 25 natures in Emerald's order.
// The room: data/interior_layouts/BattleFrontier_Lounge5.json, people data/interiors/emerald/496.json (uid = script =
// Emerald's local id). Messages: src/text/script/emerald/0296_room_BattleFrontier_Lounge5.txt (lounge_rooms.py): 0-5 the
// lines, 6-30 by nature 0 (Hardy) - 24 (Quirky).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

#define T_Greeting 0
#define T_NoneShown 1
#define T_Egg 2
#define T_Nature 6
#define NG_OK 0x8020
#define NG_SLOT 0x8021
#define NG_V 0x8022
#define PKM_NATURE 112                  // Black 2's Pokémon field of its nature

    ScriptEntry NG_NatureGirl           // 1: BattleFrontier_Lounge5_EventScript_NatureGirl (LITTLE_GIRL (12,4))
    ScriptEntry NG_Gentleman            // 2: _Gentleman
    ScriptEntry NG_BlackBelt            // 3: _BlackBelt
    ScriptEntry NG_LittleBoy            // 4: _LittleBoy
    ScriptEntriesEnd

NG_NatureGirl:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_yesno T_Greeting, NG_V
    h_goto_if_no NG_V, L_NG_None
    h_closemessage
    WorkSetConst NG_OK, 0
    WorkSetConst NG_SLOT, 0
    CallPokeSelect 0, NG_OK, NG_SLOT, 0 // ChoosePartyMon
    h_faceplayer                        // (lock, faceplayer again)
    h_goto_if_ne NG_OK, 1, L_NG_None
    PokePartyIsEgg NG_V, NG_SLOT
    h_goto_if_eq NG_V, 1, L_NG_Egg
    PokePartyGetParam NG_V, NG_SLOT, PKM_NATURE
    .irp n, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24
    WorkCmpConst NG_V, \n
    VMJumpIf CMP_EQ, L_NG_N\n
    .endr
    h_msgbox T_Nature+0                 // Hardy
    VMJump L_NG_End
    .irp n, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24
L_NG_N\n:
    h_msgbox T_Nature+\n
    VMJump L_NG_End
    .endr
L_NG_Egg:
    h_msgbox T_Egg
    VMJump L_NG_End
L_NG_None:
    h_msgbox T_NoneShown
L_NG_End:
    WorkSetConst NG_OK, 0
    WorkSetConst NG_SLOT, 0
    h_release

NG_Gentleman:
    h_msgbox_npc 3

NG_BlackBelt:
    h_msgbox_npc 4

NG_LittleBoy:
    h_msgbox_npc 5

    .balign 4, 0
