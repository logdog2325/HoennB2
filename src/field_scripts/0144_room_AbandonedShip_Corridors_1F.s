// AbandonedShip_Corridors_1F (zone 72): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// Messages: src/text/script/0082_room_AbandonedShip_Corridors_1F.txt
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
