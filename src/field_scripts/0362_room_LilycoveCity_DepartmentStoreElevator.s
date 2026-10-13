// LilycoveCity_DepartmentStoreElevator (zone 181): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0239_room_LilycoveCity_DepartmentStoreElevator.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch8a
#include "hoenn_trainers.h"  // ch8a
#include "hoenn_story.inc"  // ch8a
#include "scenes/ch8a_lib.inc"  // ch8a

    ScriptEntry Script_None
    ScriptEntry EL_Attendant            // 2: object 1 (the elevator girl)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/LilycoveCity_DepartmentStoreElevator/scripts.inc. The attendant asks for the floor (multichoice 57:
// 1F-5F), sets the dynamic warp (setdynamicwarp -> FieldSetNextZone: this room's two exit tiles are Black 2's dynamic
// warp, story_fixups' b2tools/check_exits.py: they lead to the zone/tile the script set, or where you came from),
// shakes the room (ShakeScreenInElevator) and stores the floor in VAR_DEPT_STORE_FLOOR. Each floor stores its own
// number on loading (their zone inits: Sapphire's SetDepartmentStoreFloorVar reads the dynamic warp). Left out: the
// "Now on: 3F" panel (DisplayCurrentElevatorFloor). People: data/story/ch8a.json. Lines 1-7 of the text file.
// Arrival tile on each floor = the floor's elevator door, Sapphire (2,1) + the room origin (1,1) = (3,2), facing down.
#define T_WhichFloor 1
#define T_Floor1 2
#define T_Floor2 3
#define T_Floor3 4
#define T_Floor4 5
#define T_Floor5 6
#define T_Cancel 7
EL_Attendant:                               // LilycoveCity_DepartmentStoreElevator_EventScript_Attendant
    c3_talk
    ParentActorMsg MSGFILE_SCRIPT, T_WhichFloor, 0, 0       // message + waitmessage
    ListMenu_AnchorTopRight 31, 1, 0, 1, C8_SEL
    ListMenuAdd T_Floor1, 65535, 1
    ListMenuAdd T_Floor2, 65535, 2
    ListMenuAdd T_Floor3, 65535, 3
    ListMenuAdd T_Floor4, 65535, 4
    ListMenuAdd T_Floor5, 65535, 5
    ListMenuAdd T_Cancel, 65535, 0
    ListMenuShow
    ActorMsgClose
    WorkCmpConst C8_SEL, 1
    VMJumpIf CMP_LT, L_EL_Exit             // cancel / B (0, 65534)
    WorkCmpConst C8_SEL, 5
    VMJumpIf CMP_GT, L_EL_Exit
    WorkSet C8_A, C8_SEL
    WorkSub C8_A, 1                         // 0 = 1F ... 4 = 5F
    WorkCmpWork C8_A, VAR_DEPT_STORE_FLOOR
    VMJumpIf CMP_EQ, L_EL_Exit             // the floor we are on: no ride
    WorkCmpConst C8_A, 0
    VMJumpIf CMP_EQ, L_EL_To1F
    WorkCmpConst C8_A, 1
    VMJumpIf CMP_EQ, L_EL_To2F
    WorkCmpConst C8_A, 2
    VMJumpIf CMP_EQ, L_EL_To3F
    WorkCmpConst C8_A, 3
    VMJumpIf CMP_EQ, L_EL_To4F
    FieldSetNextZone 201, 1, 3, 0, 2        // setdynamicwarp MAP_LILYCOVE_CITY_DEPARTMENT_STORE_5F, 255, 2, 1
    VMJump L_EL_Ride
L_EL_To1F:
    FieldSetNextZone 196, 1, 3, 0, 2
    VMJump L_EL_Ride
L_EL_To2F:
    FieldSetNextZone 197, 1, 3, 0, 2
    VMJump L_EL_Ride
L_EL_To3F:
    FieldSetNextZone 199, 1, 3, 0, 2
    VMJump L_EL_Ride
L_EL_To4F:
    FieldSetNextZone 200, 1, 3, 0, 2
L_EL_Ride:                                  // ..._EventScript_MoveElevator
    h_move 1, 41                            // the attendant: walk_in_place_fastest_down
    SEPlay SEQ_SE_FLD_23                    // Black 2's elevator rumble (a looping sound: stopped by hand)
    EvCameraShake 4, 0, 4, 5, 1, 0, 1, 3    // special ShakeScreenInElevator
    VMSleep 60
    SEStop
    SEPlay SEQ_SE_FLD_87                    // Black 2's arrival chime
    SEWait
    WorkSet VAR_DEPT_STORE_FLOOR, C8_A
L_EL_Exit:
    h_release
    .balign 4, 0
