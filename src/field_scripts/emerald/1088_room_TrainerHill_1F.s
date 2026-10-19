// TrainerHill_1F (zone 544; Emerald only): the Trainer Hill's floor 1 (battle_tents, 2026-10-18,
// notes/BATTLE_TENTS.md). The four modes' rooms of this floor share these scripts (scenes/trainer_hill_floor.inc); the
// zone init picks the mode's layout (map replace events 3/4/5) and trainers. Origin (1,1). Text:
// src/text/script/emerald/NNNN_room_TrainerHill_1F.txt (b2tools/trainer_hill_text.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/trainer_hill_lib.inc"
#define TH_FLOOR 1
#include "scenes/trainer_hill_floor.inc"
