// Dewford Hall, the Sludge Bomb man (Sapphire DewfordTown_Hall_EventScript_SludgeBombMan): chapter Ch6's beat (he
// appears once FLAG_HIDE_SLUDGE_BOMB_MAN_DEWFORD_HALL is cleared after Norman), included by 0052_room_DewfordTown_Hall.s
// as script 11 (uid 9, Sapphire object 9, data/story/ch2.json). Written by Ch2 with the Hall's trend stand-in (text
// lines 24-25 of 0032, "Hot Idol"); Ch6 may change it here.
HL_SludgeBombMan:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_TM_SLUDGE_BOMB, L_HL_ReceivedSludgeBomb
    h_msgbox 23                     // For me, Sludge Bomb is at the peak of popularity. ...
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_TM36            // TM36 Sludge Bomb (Black 2's TM36 is Sludge Bomb too)
    h_goto_if_eq HLIB_RESULT, 0, L_HL_BagFull
    h_setflag FLAG_RECEIVED_TM_SLUDGE_BOMB
    h_release
L_HL_BagFull:                       // Common_EventScript_ShowBagIsFull
    h_msgbox 25                     // Too bad! The Bag is full...
    h_release
L_HL_ReceivedSludgeBomb:
    h_msgbox 24                     // I love Sludge Bomb. But Pokémon with the "Hot Idol" move are in, too.
    h_release
