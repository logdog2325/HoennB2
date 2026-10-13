// Route 110's first Aqua grunt (Sapphire object 22 at (7,83), Route110_EventScript_14F946; chapter Ch3 part 3b,
// ch3b 2026-10-07). scenes/Route110.inc includes this file in both of its parts (one ScriptEntry in the SCENE_ENTRIES
// list, script 11; the body after #else, with `#define R110G1_TEXT <n>` = the line of src/text/scenes/Route110.txt that
// holds src/text/scenes/Route110_Grunt1.txt's line). data/story/ch3b.json places him (uid 122, FLAG_HIDE_EVIL_TEAM_ROUTE110).
// (Until 2026-10-08 his tile was in Route 103's zone 326, a zone covering whole 32x32 cells, and scenes/Route103.inc
// included this file: zone_edges.)
#ifdef SCENE_ENTRIES
    ScriptEntry R110G1_Grunt1       // Route110_EventScript_14F946 (chapter Ch3)
#else
#define R110G1_GRUNT 122

R110G1_Grunt1:                      // lock, faceplayer, msgbox, Common_Movement_FaceOriginalDirection (FACE_UP)
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, R110G1_TEXT, 0, 0    // Team Aqua's activities must be kept secret for now.
    LastKeyWait
    ActorMsgClose
    h_turnobject R110G1_GRUNT, 0
    h_release
#endif
