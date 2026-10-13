// AbandonedShip_CaptainsOffice (zone 71): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// Messages: src/text/script/0081_room_AbandonedShip_CaptainsOffice.txt
// furniture messages. Story scripts: add them after a line "// ---- story" (then this generator leaves the file
// alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_key_items.h"  // ch6
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_1
    ScriptEntry Story_CO_Aide   // 2: object 1 (Capt. Stern's aide)  // story:
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 0, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch6, ch6 agent: Sapphire data/maps/AbandonedShip_CaptainsOffice/scripts.inc; generators keep
// everything from this line on). The aide: data/story/ch6.json (uid 1). Lines 1-3 of the text file.
Story_CO_Aide:                              // AbandonedShip_CaptainsOffice_EventScript_CaptSternAide
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_EXCHANGED_SCANNER, L_CO_SSCactus
    h_checkitem ITEM_SCANNER, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 1, L_CO_Deliver
    h_goto_if_set FLAG_ITEM_ABANDONED_SHIP_HIDDEN_FLOOR_ROOM_2_SCANNER, L_CO_SSCactus
    h_msgbox 1                              // I'm investigating this ship on behalf of Capt. Stern. ...
    h_release
L_CO_Deliver:
    h_msgbox 2                              // Oh! That's a Scanner! ...
    h_release
L_CO_SSCactus:
    h_msgbox 3                              // This ship is called S.S. Cactus. ...
    h_release
    .balign 4, 0
