// Inside of the moving truck, zone 394 (Sapphire InsideOfTruck + field_special_scene.c Task_HandleTruckSequence).
// A new game starts here (b2tools/patches/opening.py): the engine runs Script_29 before the first fade-in and
// Script_30 after it (src/ov035/event_mapchange.c:205-247), with the player hidden. Script_30 warps into the truck
// so the player is placed visibly and the reserved Script_31 plays the ride on the black screen.
// Zone tiles = Sapphire tiles + (8, 8): start (2,2) = (10,10), exit triggers (3,1..3) = (11, 9..11) -> Script_20.
// Timing: the field runs at 30 frames a second (Sapphire's 60 fps delays are halved).
// Sounds are stand-ins until the user picks Black 2 sounds for the truck (notes/OPENING.md).
// The back door: the open door (bright exit light in the doorway and on the exit column) is building res 200 (info
// type 11 -> BMSetVisible type 8) at the doorway, tile (13.2, 10.5); the closed door is the room's own terrain behind
// it (b2tools/models_truck.py). Open is the default, as in Sapphire's map: only the new-game ride (Script_31) shuts
// it, from the running script (BMSetVisible at zone init hangs). Hide and show exactly once each: a second hide
// would lose the model (FieldChunkPropHolder_SetVisible keeps one saved index).

#include "hoenn.h"

Script_20:                                       // InsideOfTruck_EventScript_15FC29: step out of the truck
    ActorsPauseAll
    FlagSet FLAG_HIDE_MAP_NAME_POPUP
    FieldSetTeleportZone 1                       // blackout/respawn: the player's house (RESPAWN_ZONE_INFO entry 0)
    TrainerCardGetSex 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TruckGirl
    WorkSetConst VAR_LITTLEROOT_INTRO_STATE, 1   // boy: Brendan's house (Sapphire 15FC45)
    FlagSet FLAG_HIDE_MAY_MOM_DOWNSTAIRS
    FlagSet FLAG_HIDE_MOVING_TRUCK_MAY
    FlagSet FLAG_HIDE_BRENDAN_MOM
    FlagSet FLAG_HIDE_BRENDAN_UPSTAIRS
#ifdef HOENN_EMERALD                             // pokeemerald InsideOfTruck_EventScript_SetIntroFlagsMale: Brendan's house is his own
    FlagSet FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_RIVAL_SIBLING
    FlagSet FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F_POKE_BALL
#endif
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE_2, 1
    VMJump L_TruckOut
L_TruckGirl:
    WorkSetConst VAR_LITTLEROOT_INTRO_STATE, 2   // girl: May's house (15FC68)
    FlagSet FLAG_HIDE_BRENDAN_MOM_DOWNSTAIRS
    FlagSet FLAG_HIDE_MOVING_TRUCK_BRENDAN
    FlagSet FLAG_HIDE_MAY_MOM
    FlagSet FLAG_HIDE_MAY_UPSTAIRS
#ifdef HOENN_EMERALD                             // ...SetIntroFlagsFemale: May's house is hers
    FlagSet FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_RIVAL_SIBLING
    FlagSet FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_2F_POKE_BALL
#endif
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE, 1
L_TruckOut:
    ActorCmdExec 255, Mv_StepOut
    ActorCmdWait
    FadeOutBlack
    RTReserveScript 31                           // Littleroot's arrival scene (0778 Script_31)
    FadeWait
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TruckOutGirl
    MapChangeCore 389, 171, 0, 362, 3            // Sapphire dynamic warp (3,10), facing right
    VMJump L_TruckOutDone
L_TruckOutGirl:
    MapChangeCore 389, 180, 0, 362, 3            // (12,10)
L_TruckOutDone:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_29:
    VMHalt

Script_30:                                       // new game, after the first fade-in (the player is hidden)
    FlagSet FLAG_HIDE_FAT_MAN_LITTLEROOT         // Sapphire's new-game flags (data/scripts/new_game.inc)
    FlagSet FLAG_HIDE_NORMAN_LITTLEROOT
    FlagSet FLAG_HIDE_MAY_PICHU_DOLL
    FlagSet FLAG_HIDE_MOM_LITTLEROOT
    FlagSet FLAG_HIDE_MOM_UPSTAIRS
    VMCall Sub_NewGameFlags                      // the rest of Sapphire's new-game flags (scenes/new_game_flags.inc)
    VMStackPushFlag FLAG_EXP_SHARE_ON            // Birch's sixth question (b2tools/patches/fairy.py intro_script):
    VMStackPushConst 1                           // YES set FLAG_EXP_SHARE_ON in the intro, so the Exp. Share starts in
    VMStackCmp CMP_EQ                            // Key Items, switched on (the Bag is only made after the intro, by
    VMJumpIf CMP_STACK, L_TruckNoExpShare        // ov279 InitItemBag). NO (flag unset): Mr. Stone gives it, as before.
    ItemAdd ITEM_EXP_SHARE, 1, 0x8010            // silently, on the black screen (a key item: the pocket has room)
L_TruckNoExpShare:
    FadeOutBlackQ
    FadeWait
    RTReserveScript 31
    MapChangeCore 394, 10, 0, 10, 3              // Sapphire (2,2), facing the back door
    VMHalt

Script_31:                                       // the ride (reserved: starts on black)
    ActorsPauseAll
    BMSetVisible 8, 13, 10, 0                    // the back door is shut for the ride (on black; see below)
    VMSleep 45                                   // 1.5 s of darkness
    SEPlay SEQ_SE_FLD_126                        // truck moving (stand-in)
    EvCameraShake 0, 1, 10, 8, 0, 0, 0, 0        // bobbing in the dark, ~2.5 s
    FadeInBlack
    EvCameraShake 0, 1, 10, 15, 0, 0, 0, 0       // bobbing while the light comes up, ~5 s
    FadeWait
    SEPlay SEQ_SE_FLD_155                        // truck stops (stand-in)
    EvCameraShake 2, 0, 6, 3, 0, 0, 0, 0         // the stop jolts the load sideways
    VMSleep 45
    SEPlay SEQ_SE_FLD_126                        // unloading (stand-in)
    VMSleep 60
    SEPlay SEQ_SE_KAIDAN                         // the back door opens (stand-in)
    BMSetVisible 8, 13, 10, 1                    // ...and light pours in at the exit (Sapphire's ExitLight tiles)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0                                 // movement lists are read as words (Black 2 aligns them too)
Mv_StepOut:                                      // onto the exit tile (Sapphire warps there)
    Move 15, 1
    MoveEnd
    .balign 4, 0

#include "new_game_flags.inc"             // Sub_NewGameFlags (converter/gen_story_ids.py; same folder)
    .balign 4, 0
