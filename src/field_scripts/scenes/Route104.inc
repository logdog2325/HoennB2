// Route 104's story (Sapphire data/maps/Route104/scripts.inc; chapter Ch1), all of it in Route 104's own zone 329 (since
// HEAD cc338ed its north end in Rustboro's cells and its middle in Petalburg's are zone 329 too: world.json zone_rects).
// converter/gen_map_content.py includes this file twice in the generated zone file 0658_auto_Route104.s: the entries
// below become scripts 1-4, then chapter Ch2's from scenes/Route104_ch2.inc (5), then 6-8 (the north end's people:
// after Ch2's, so Mr. Briney keeps script 5; one more Ch2 entry would move them, data/story/ch1.json), the generated
// signs/people follow. Text: src/text/scenes/Route104.txt (lines 0-7, Ch1's). Map scripts: scenes/Route104_init.inc.
// Story objects: data/story/ch1.json (uid 100 + Sapphire local id): the Chesto Berry woman (16) uid 116, Gina (23)
// uid 123, Mia (24) uid 124. Gina & Mia (TRAINER_GINA_AND_MIA_1, sight 0 in Sapphire: they battle when talked to)
// are story people, not eye-contact trainers, because Gina's after-battle line names the player "Big guy"/"Big girl"
// (GetPlayerBigGuyGirlString), which Black 2's trainer lines cannot do: Ch1 writes it twice (ActorMsgGendered).
#ifdef SCENE_ENTRIES
    ScriptEntry R104_Init           // 1: Route104_OnTransition (zone init): the Flower Shop worker outside
    ScriptEntry R104_WhiteHerb      // 2: flower shop worker outside (Route104_EventScript_14EF09), White Herb
    ScriptEntry R104_TM09           // 3: boy (Route104_EventScript_14EF93), TM09
    ScriptEntry Ch2_R104BrineyBoat  // 4: OnFrame VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE 1 (Route104_EventScript_14EEA1):
                                    //    chapter Ch2's boat ride (scenes/Route104_ch2.inc)
#include "scenes/Route104_ch2.inc"
    ScriptEntry R104N_Chesto        // 6: woman by the berry trees (Route104_EventScript_14EEC8), Chesto Berry
    ScriptEntry R104N_Gina          // 7: Gina (Route104_EventScript_14F25A, twins)
    ScriptEntry R104N_Mia           // 8: Mia (Route104_EventScript_14F279)
#ifdef HOENN_EMERALD                // Emerald-only entries go last (notes/EMERALD_STORY.md 2.4.1); bodies: scenes/emerald/Route104.inc
    ScriptEntry Em_R104_RivalTrigger // 9: Route104_EventScript_RivalTrigger, (17, 51) while VAR_ROUTE104_STATE is 1 (Ch2)
    ScriptEntry Em_R104_Rival       // 10: Route104_EventScript_Rival (talked to)
#endif
#else
#define R104_T(n) (n)               // Ch1's lines come first in src/text/scenes/Route104.txt (4-7: the north end's)
#define R104N_GINA 123
#define R104N_MIA 124

R104_Init:                          // Route104_EventScript_14EEAE
#ifdef HOENN_EMERALD
    h_setup_rival_gfx               // Common_EventScript_SetupRivalGfxId (the rival's model 162; Emerald's rival stands here)
#endif
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
    h_goto_if_unset FLAG_MET_PRETTY_PETAL_SHOP_OWNER, L_R104_HideWorker
    h_goto_if_no_badge 3, L_R104_HideWorker
    h_clearflag FLAG_HIDE_FLOWER_SHOP_WORKER_OUTSIDE
    VMHalt
L_R104_HideWorker:
    h_setflag FLAG_HIDE_FLOWER_SHOP_WORKER_OUTSIDE
    VMHalt

R104_WhiteHerb:                     // Route104_EventScript_14EF09 (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_WHITE_HERB, L_R104_WhiteHerbGiven
    h_msgbox R104_T(0)              // This Flower Shop started selling saplings recently. ... Would you take it, please?
    h_closemessage
    h_giveitem ITEM_WHITE_HERB
    h_goto_if_eq HLIB_RESULT, 0, L_R104_Release
    h_setflag FLAG_RECEIVED_WHITE_HERB
L_R104_Release:
    h_release
L_R104_WhiteHerbGiven:
    h_msgbox R104_T(1)              // ... Where should I put them?
    h_release

R104_TM09:                          // Route104_EventScript_14EF93 (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_TM09, L_R104_TM09Given
    h_msgbox R104_T(2)              // I like filling my mouth with seeds, then spitting them out fast! ...
    h_closemessage
    h_giveitem ITEM_TM09            // Sapphire TM09 Bullet Seed: Bullet Seed is no Gen 5 TM, so TM09 (its number,
    h_goto_if_eq HLIB_RESULT, 0, L_R104_Release   // converter/gen_items.py's rule for such TMs)
    h_setflag FLAG_RECEIVED_TM09
    h_release
L_R104_TM09Given:
    h_msgbox R104_T(3)              // A word of advice! A TM, Technical Machine, is good only for one-time use. ...
    h_release

R104N_Chesto:                       // Route104_EventScript_14EEC8 (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_CHESTO_BERRY_ROUTE104, L_R104N_ChestoGiven
    h_msgbox R104_T(6)                   // If you see Berries growing in loamy soil, feel free to take them. ...
    h_closemessage
    h_giveitem ITEM_CHESTO_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_R104N_Release
    h_setflag FLAG_RECEIVED_CHESTO_BERRY_ROUTE104
L_R104N_ChestoGiven:
    h_msgbox R104_T(7)                   // The way you look, you must be a Trainer, no? ...
L_R104N_Release:
    h_release

R104N_Gina:                         // trainerbattle_double TRAINER_GINA_AND_MIA_1 (Gina's lines: types 3/5/6)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_defeated TRAINER_GINA_AND_MIA_1, L_R104N_GinaAfter
    h_goto_if_cannot_double L_R104N_GinaNeedTwo
    TrainerBGMPlayPush TRAINER_GINA_AND_MIA_1
    TrainerSayMessage TRAINER_GINA_AND_MIA_1, 3, R104N_GINA   // Gina: Okay, let's battle with our Pokémon!
    ActorMsgClose
    h_trainerbattle TRAINER_GINA_AND_MIA_1
    h_release
L_R104N_GinaNeedTwo:
    TrainerSayMessage TRAINER_GINA_AND_MIA_1, 6, R104N_GINA   // Gina: Oh? Only one Pokémon? ...
    LastKeyWait
    ActorMsgClose
    h_release
L_R104N_GinaAfter:
    h_msgbox_gendered R104_T(4), R104_T(5), R104N_GINA      // Gina: Big guy / Big girl is strong! ...
    h_release

R104N_Mia:                          // trainerbattle_double TRAINER_GINA_AND_MIA_1 (Mia's lines: types 7/9/10)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_defeated TRAINER_GINA_AND_MIA_1, L_R104N_MiaAfter
    h_goto_if_cannot_double L_R104N_MiaNeedTwo
    TrainerBGMPlayPush TRAINER_GINA_AND_MIA_1
    TrainerSayMessage TRAINER_GINA_AND_MIA_1, 7, R104N_MIA    // Mia: We are twins, so we battle Pokémon together.
    ActorMsgClose
    h_trainerbattle TRAINER_GINA_AND_MIA_1
    h_release
L_R104N_MiaNeedTwo:
    TrainerSayMessage TRAINER_GINA_AND_MIA_1, 10, R104N_MIA   // Mia: You want to battle with us? ...
    LastKeyWait
    ActorMsgClose
    h_release
L_R104N_MiaAfter:
    TrainerSayMessage TRAINER_GINA_AND_MIA_1, 9, R104N_MIA    // Mia: We will train our Pokémon more ...
    LastKeyWait
    ActorMsgClose
    h_release

#include "scenes/Route104_ch2.inc"
#ifdef HOENN_EMERALD
#include "scenes/emerald/Route104.inc"
#endif
#endif
