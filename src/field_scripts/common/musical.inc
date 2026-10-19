// The Pokémon Musical at Hoenn's Contest Hall counters (musical agent 2026-10-18; the user's idea, notes/RESUME.md
// "Emerald gaps" -> Contests). Gen 3 Contests can't run on Black 2, so the Contest receptionists send you to Black 2's
// own Musical instead: Sapphire/Ruby's four halls (Verdanturf, Fallarbor, Slateport, Lilycove), Emerald's Lilycove.
//
// Black 2's flow is Nimbasa's center reception, global script 10450 (pokebw2 data/field_scripts/1268.s Script_1, text
// 442): Cmd_0167 0 (overlays 210 + 211 and the musical's work), the yes/no/info menu, MusicalCmd_0165 11 (how many
// party Pokémon can perform: anything but an Egg), Cmd_016A (the Musical's party screen), the show menu (MusicalCmd_0165 5
// stores the show in the musical save), "Great! Please walk this way!", a walk through Nimbasa's door, a fade, then
// MusicalCmd_0163 slot, 0: the offline musical event (ov012), which ends the script. The event goes to zone 78 (the
// backstage; Black 2's zone, its scripts 3-5 = 0156_musical_backstage.s), dress-up, the stage, the photo, the comments,
// and then back. Here: the same commands with Hoenn lines, no walk (Nimbasa's movements need its room), and
// FieldSetNextZoneHere just before the show: b2tools/patches/musical.py makes the event return to that spot (Black 2
// returns to zone 77 = Ever Grande's Pokemon League in Hoenn) and makes the event's heap fit a Hoenn room.
//
// The Prop Case (Black 2's key item 578) is handed over on the first visit. The Props are the musical save's: Black 2
// gives 15 to every new game (arm9 func_0200ac60, the save block 42 init: Props 0, 1, 8, 10, 16, 28, 48, 59, 63, 66, 70,
// 75, 76, 83, 89), so every save, old or new, has them. More Props: after each show some members of the audience become
// fans with a gift (the musical save's 10 fan records, Black 2 fills them); in Nimbasa they wait in the lobby, here the
// receptionist hands their Props over (Black 2's 10466 "Received the ...!" + MusicalCmd_0169, as 1268.s L_0CF1).
//
// Text: the lobby's own file holds the lines below from line t on (same wording in every lobby). Works 0x8029-0x802D.
#ifndef HOENN_MUSICAL_INC
#define HOENN_MUSICAL_INC

#define MUS_W 0x8029
#define MUS_OK 0x802A
#define MUS_SLOT 0x802B
#define MUS_SHOW 0x802C
#define MUS_FAN 0x802D

#define MUSL_HELLO 0            // Hello, there! Contests are on hold for now... but our Musical stage is open!
#define MUSL_CASE 1             // In a Musical, Pokémon dress up ... Here's a Prop Case ...
#define MUSL_FANS 2             // Oh! Fans from your last show left you some presents!
#define MUSL_ASK 3              // Would you like to perform?
#define MUSL_NONE 4             // I'm sorry, but none of your Pokémon can perform.
#define MUSL_CHOOSE 5           // Please choose the Pokémon that will perform.
#define MUSL_WHICH 6            // Which show would you like to perform in?
#define MUSL_SHOW1 7            // Stardom              (Black 2's show names, 442 lines 29-32; the backstage
#define MUSL_SHOW2 8            // Forest Stroll         names the show from Black 2's own system text)
#define MUSL_SHOW3 9            // A Sweet Soirée
#define MUSL_SHOW4 10           // Exciting Nimbasa
#define MUSL_CANCEL 11          // Cancel
#define MUSL_GO 12              // Great! Please walk this way!
#define MUSL_BYE 13             // We hope to see you on stage another time.
#define MUSL_COUNT 14

// The whole receptionist, from c3_talk-style lock + face (done by the caller) to the release or the show.
    .macro musical_reception t
    h_msgbox (\t) + MUSL_HELLO
    h_checkitem ITEM_PROP_CASE, 1, MUS_W
    h_goto_if_eq MUS_W, 1, .Lmus_have\@
    h_msgbox (\t) + MUSL_CASE
    h_closemessage
    h_giveitem ITEM_PROP_CASE, 1            // key item: never a full Bag
.Lmus_have\@:
    // the fans' Props (1268.s L_0CF1: record n is a fan when MusicalCmd_0166 n, 0 != 0; kind 3 = 1: holds a Prop,
    // kind 4 = which; 10466 shows "Received the <Prop>!" and adds it (0x8009 = 0: Black 2's fans' value); 0169 clears)
    WorkSetConst MUS_FAN, 0
    WorkSetConst MUS_OK, 0
.Lmus_fan\@:
    WorkSetConst MUS_W, 0
    MusicalCmd_0166 MUS_FAN, 0, MUS_W
    h_goto_if_eq MUS_W, 0, .Lmus_fan_next\@
    WorkSetConst MUS_W, 0
    MusicalCmd_0166 MUS_FAN, 3, MUS_W
    h_goto_if_ne MUS_W, 1, .Lmus_fan_next\@
    h_goto_if_ne MUS_OK, 0, .Lmus_fan_give\@
    h_msgbox (\t) + MUSL_FANS
    h_closemessage
    WorkSetConst MUS_OK, 1
.Lmus_fan_give\@:
    h_closemessage                          // no balloon open at 10466's info window (script_check msg)
    MusicalCmd_0166 MUS_FAN, 4, MUS_W
    VMStackPush 0x8008
    VMStackPush 0x8009
    h_copyvar 0x8008, MUS_W
    WorkSetConst 0x8009, 0
    RTCallGlobal 10466
    VMStackPop 0x8009
    VMStackPop 0x8008
    MusicalCmd_0169 MUS_FAN
.Lmus_fan_next\@:
    WorkAdd MUS_FAN, 1
    h_goto_if_lt MUS_FAN, 10, .Lmus_fan\@
    h_yesno (\t) + MUSL_ASK, MUS_W
    h_goto_if_no MUS_W, .Lmus_bye\@
    Cmd_0167 0, 0, 0, 0                     // overlays 210 + 211 and the musical's work (freed by Cmd_0167 1 or the show)
    WorkSetConst MUS_W, 0
    MusicalCmd_0165 11, 0, MUS_W
    h_goto_if_ne MUS_W, 0, .Lmus_some\@
    h_msgbox (\t) + MUSL_NONE
    VMJump .Lmus_unload\@
.Lmus_some\@:
    h_msgbox (\t) + MUSL_CHOOSE
    h_closemessage
    WorkSetConst MUS_OK, 0
    WorkSetConst MUS_SLOT, 0
    Cmd_016A MUS_OK, MUS_SLOT               // MUS_OK != 0: chosen (party slot in MUS_SLOT); 0: backed out
    h_goto_if_eq MUS_OK, 0, .Lmus_unload\@
    ParentActorMsg MSGFILE_SCRIPT, (\t) + MUSL_WHICH, 0, 0
    ListMenu_AnchorTopRight 31, 1, 0, 1, MUS_SHOW
    ListMenuAdd (\t) + MUSL_SHOW1, 65535, 0
    ListMenuAdd (\t) + MUSL_SHOW2, 65535, 1
    ListMenuAdd (\t) + MUSL_SHOW3, 65535, 2
    ListMenuAdd (\t) + MUSL_SHOW4, 65535, 3
    ListMenuAdd (\t) + MUSL_CANCEL, 65535, 4
    ListMenuShow
    h_goto_if_eq MUS_SHOW, 4, .Lmus_unload\@        // Cancel
    h_goto_if_eq MUS_SHOW, 65534, .Lmus_unload\@    // B
    MusicalCmd_0165 5, MUS_SHOW, 0          // the show (0-3: Black 2's own four; never the downloaded 5th)
    h_msgbox (\t) + MUSL_GO
    h_closemessage
    FieldSetNextZoneHere                    // b2tools/patches/musical.py: the show ends on this spot, facing the counter
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlackQ
    SEWait
    FadeWait
    MusicalCmd_0163 MUS_SLOT, 0             // Black 2's Musical (ends this script)
.Lmus_unload\@:
    Cmd_0167 1, 0, 0, 0
.Lmus_bye\@:
    h_msgbox (\t) + MUSL_BYE
    h_release
    .endm

#endif
