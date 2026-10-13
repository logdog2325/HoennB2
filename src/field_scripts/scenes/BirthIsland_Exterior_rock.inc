// Birth Island's triangle: the step checks and the eleven places (generated from Emerald's sStoneMaxStepCounts and
// sDeoxysRockCoords by the events agent; included by scenes/BirthIsland_Exterior.inc).
L_BE_CheckSteps:                        // rockLevel != 0 && sStoneMaxStepCounts[rockLevel - 1] < stepCount -> failed
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 1, L_BE_Max1
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 2, L_BE_Max2
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 3, L_BE_Max3
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 4, L_BE_Max4
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 5, L_BE_Max5
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 6, L_BE_Max6
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 7, L_BE_Max7
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 8, L_BE_Max8
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 9, L_BE_Max9
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 10, L_BE_Max10
    VMJump L_BE_Progress                // (level 0: no limit)
L_BE_Max1:
    h_goto_if_gt BE_STEPS, 4, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max2:
    h_goto_if_gt BE_STEPS, 8, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max3:
    h_goto_if_gt BE_STEPS, 8, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max4:
    h_goto_if_gt BE_STEPS, 8, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max5:
    h_goto_if_gt BE_STEPS, 4, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max6:
    h_goto_if_gt BE_STEPS, 4, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max7:
    h_goto_if_gt BE_STEPS, 4, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max8:
    h_goto_if_gt BE_STEPS, 6, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max9:
    h_goto_if_gt BE_STEPS, 3, L_BE_Failed
    VMJump L_BE_Progress
L_BE_Max10:
    h_goto_if_gt BE_STEPS, 3, L_BE_Failed
    VMJump L_BE_Progress
L_BE_MoveRock:                          // ChangeDeoxysRockLevel: the rock to sDeoxysRockCoords[VAR_DEOXYS_ROCK_LEVEL]
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 0, L_BE_At0
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 1, L_BE_At1
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 2, L_BE_At2
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 3, L_BE_At3
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 4, L_BE_At4
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 5, L_BE_At5
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 6, L_BE_At6
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 7, L_BE_At7
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 8, L_BE_At8
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 9, L_BE_At9
    h_goto_if_eq VAR_DEOXYS_ROCK_LEVEL, 10, L_BE_At10
    VMReturn
L_BE_At0:                              // (15,12)
    ActorSetGPos BE_ROCK, 15 + EV_BIRTH_OX, BE_GY, 12 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At1:                              // (11,14)
    ActorSetGPos BE_ROCK, 11 + EV_BIRTH_OX, BE_GY, 14 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At2:                              // (15,8)
    ActorSetGPos BE_ROCK, 15 + EV_BIRTH_OX, BE_GY, 8 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At3:                              // (19,14)
    ActorSetGPos BE_ROCK, 19 + EV_BIRTH_OX, BE_GY, 14 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At4:                              // (12,11)
    ActorSetGPos BE_ROCK, 12 + EV_BIRTH_OX, BE_GY, 11 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At5:                              // (18,11)
    ActorSetGPos BE_ROCK, 18 + EV_BIRTH_OX, BE_GY, 11 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At6:                              // (15,14)
    ActorSetGPos BE_ROCK, 15 + EV_BIRTH_OX, BE_GY, 14 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At7:                              // (11,14)
    ActorSetGPos BE_ROCK, 11 + EV_BIRTH_OX, BE_GY, 14 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At8:                              // (19,14)
    ActorSetGPos BE_ROCK, 19 + EV_BIRTH_OX, BE_GY, 14 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At9:                              // (15,15)
    ActorSetGPos BE_ROCK, 15 + EV_BIRTH_OX, BE_GY, 15 + EV_BIRTH_OZ, 1
    VMReturn
L_BE_At10:                              // (15,10)
    ActorSetGPos BE_ROCK, 15 + EV_BIRTH_OX, BE_GY, 10 + EV_BIRTH_OZ, 1
    VMReturn
