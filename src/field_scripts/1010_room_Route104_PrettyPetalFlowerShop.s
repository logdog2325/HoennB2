// Route104_PrettyPetalFlowerShop (zone 505): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0377_room_Route104_PrettyPetalFlowerShop.txt
// Story (chapter Ch1, Sapphire data/maps/Route104_PrettyPetalFlowerShop/scripts.inc), after "// ---- story": the owner,
// the Wailmer Pail, the daily Berry; map scripts 1011. People: data/story/ch1.json (uid = Sapphire local id, index =
// order there): owner 1 (index 0), the girls 2 and 3. Room tiles = Sapphire tiles + (1, 0).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_None
    ScriptEntry Script_2    // owner (Route104_PrettyPetalFlowerShop_EventScript_15BE0B)
    ScriptEntry Script_3    // girl, Wailmer Pail (15BEA4)
    ScriptEntry Script_4    // little girl, daily Berry (15BEDA)
    ScriptEntry Script_5    // zone init (Route104_PrettyPetalFlowerShop_OnTransition)
    ScriptEntriesEnd

Script_None:
    VMHalt

// ---- story
#define FS_TEMP_1 1                                  // Sapphire FLAG_TEMP_1 (Black 2 flags 0-0x63 are map-local too)
#define FS_OWNER_INDEX 0
#ifndef ITEM_WAILMER_PAIL                           // (until src/include/hoenn_key_items.h has it: Black 2's own
#define ITEM_WAILMER_PAIL ITEM_SPRAYDUCK            //  watering can, the Gen 4 Sprayduck, as the stand-in)
#endif

Script_5:                                        // OnTransition
    h_setflag FLAG_LANDMARK_FLOWER_SHOP
    h_goto_if_unset FLAG_MET_PRETTY_PETAL_SHOP_OWNER, L_FS_OwnerOut
    h_goto_if_no_badge 3, L_FS_OwnerOut
    h_setflag FS_TEMP_1                          // the owner keeps the shop
    VMHalt
L_FS_OwnerOut:
    ObjInitNPCGPos FS_OWNER_INDEX, 1, 5, 0, 6       // setobjectxyperm 1, 4, 6
    VMHalt

Script_2:                                        // the owner (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_set FS_TEMP_1, L_FS_Shop
    h_msgbox 2                                   // Hello! This is the Pretty Petal flower shop. ...
    h_goto_if_set FLAG_MET_PRETTY_PETAL_SHOP_OWNER, L_FS_Again
    h_setflag FLAG_MET_PRETTY_PETAL_SHOP_OWNER
    h_yesno 3, HLIB_TMP                          // Your name is? ... would you like to learn about Berries?
    VMJump L_FS_Answer
L_FS_Again:
    h_yesno 4, HLIB_TMP                          // <player>, would you like to learn about Berries?
L_FS_Answer:
    h_goto_if_no HLIB_TMP, L_FS_No
    h_msgbox 5                                   // Berries grow on trees that thrive only in dark, loamy soil. ...
    h_release
L_FS_No:
    h_msgbox 6                                   // Flowers bring so much happiness to people, don't they?
    h_release
L_FS_Shop:                                       // pokemartdecoration2: Black 2 has no decorations, so she sells
    h_msgbox 0                                   //   nothing (the user's choice for decoration shops, notes/DECISIONS.md)
    h_msgbox 1                                   // Please come again!
    h_release

Script_3:                                        // 15BEA4 (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_WAILMER_PAIL, L_FS_PailGiven
    h_msgbox 7                                   // Hello! The more attention you give to flowers, ... You can have this.
    h_closemessage
    h_giveitem ITEM_WAILMER_PAIL
    h_msgbox 8                                   // While Berry plants are growing, water them with the Wailmer Pail. ...
    h_setflag FLAG_RECEIVED_WAILMER_PAIL
    h_release
L_FS_PailGiven:
    h_msgbox 8
    h_release

Script_4:                                        // 15BEDA (lock, faceplayer; dotimebasedevents: Black 2 clears the
    h_lock                                       //   FLAG_DAILY_ flags itself at midnight)
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_DAILY_RECEIVED_BERRY_FLOWER_SHOP, L_FS_BerryGiven
    h_msgbox 9                                   // I'm trying to be like my big sisters. ... Here you go! It's for you!
    h_closemessage
    Random 0x8008, 8                             // random 8 + ITEM_CHERI_BERRY: Cheri .. Persim (same order in Black 2)
    WorkAdd 0x8008, ITEM_CHERI_BERRY
    ItemCheckSpace 0x8008, 1, HLIB_RESULT        // giveitem VAR_RESULT (h_giveitem with an item in a work)
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 0x8008
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
    h_goto_if_eq HLIB_RESULT, 0, L_FS_BerryDone  // (Black 2's item script has said the Bag is full)
    h_setflag FLAG_DAILY_RECEIVED_BERRY_FLOWER_SHOP
L_FS_BerryGiven:
    h_msgbox 10                                  // You can plant a Berry and grow it big, ...
L_FS_BerryDone:
    h_release
    .balign 4, 0
