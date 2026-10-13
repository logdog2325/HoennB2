// Sapphire's shared movement lists (pokeruby data/scripts/movement.inc), same labels: Common_Movement_*.
// Include at the END of your zone script (after the scripts: a script file must start with its ScriptEntry table),
// with "hoenn_story.inc" included at the top. notes/STORY_COMMON.md.
// Not here: face_player / face_away_player / face_original_direction (Black 2 has no move that turns an actor toward
// the player): for the NPC talked to use h_faceplayer; for another actor use face_<dir> with the direction you know.
#ifndef COMMON_MOVEMENT_INC
#define COMMON_MOVEMENT_INC
    .balign 4, 0                       // movement lists are read as words
Common_Movement_QuestionMark:
    emote_question_mark
    step_end
Common_Movement_ExclamationMark:
    emote_exclamation_mark
    step_end
Common_Movement_Delay48:
    delay_16 3
    step_end
Common_Movement_Delay32:
    delay_16 2
    step_end
Common_Movement_WalkInPlaceFastestLeft:
    walk_in_place_fastest_left
    step_end
Common_Movement_WalkInPlaceFastestUp:
    walk_in_place_fastest_up
    step_end
Common_Movement_WalkInPlaceFastestRight:
    walk_in_place_fastest_right
    step_end
Common_Movement_WalkInPlaceFastestDown:
    walk_in_place_fastest_down
    step_end
Common_Movement_WalkUp:
    walk_up
    step_end
Common_Movement_WalkUp2:
    walk_up 2
    step_end
Common_Movement_WalkUp4:
    walk_up 4
    step_end
Common_Movement_WalkUp6:
    walk_up 6
    step_end
#endif
