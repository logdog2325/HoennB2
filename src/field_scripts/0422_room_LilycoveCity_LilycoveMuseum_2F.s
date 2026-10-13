// LilycoveCity_LilycoveMuseum_2F (zone 211): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0270_room_LilycoveCity_LilycoveMuseum_2F.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch8a
#include "hoenn_trainers.h"  // ch8a
#include "hoenn_story.inc"  // ch8a
#include "scenes/ch8a_lib.inc"  // ch8a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry MU2_ShowExhibitHall     // 3: ON_FRAME VAR_LILYCOVE_MUSEUM_2F_STATE 0 (init file 0423)  // story:
    ScriptEntry MU2_Curator             // 4: object 1  // story:
    ScriptEntry MU2_CutePainting        // 5: signs (14,10) (15,10)  // story:
    ScriptEntry MU2_ToughPainting       // 6: signs (3,6) (2,6)  // story:
    ScriptEntry MU2_CoolPainting        // 7: signs (10,6) (11,6)  // story:
    ScriptEntry MU2_BeautyPainting      // 8: signs (19,6) (18,6)  // story:
    ScriptEntry MU2_SmartPainting       // 9: signs (6,10) (7,10)  // story:
    ScriptEntry MU2_Girl                // 10: object 2 (hidden: PATRON_2)  // story:
    ScriptEntry MU2_ExpertM             // 11: object 3 (hidden: TOURISTS)  // story:
    ScriptEntry MU2_RichBoy             // 12: object 4 (hidden: TOURISTS)  // story:
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

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 1, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/LilycoveCity_LilycoveMuseum_2F/scripts.inc. Scene: the Curator shows the empty exhibit hall (the
// player arrives from 1F at Sapphire (11,8) = zone tile (12,9); the Curator stands at (10,8)). The five contest
// paintings (Cool/Beauty/Cute/Smart/Tough) and the visitors who come with them depend on Contests (decided later):
// no painting exists yet, so every frame says Sapphire's "picture frame" line and the Curator wishes to fill the
// hall. Left out: OnLoad's setmetatile of the painted frames and showcontestwinner (the painting picture), and the
// glass ornament (givedecoration: Black 2 has no Secret Base decorations; the flag is set as Sapphire does).
// People and signs: data/story/ch8a.json. Lines 2-19 of the text file.
#define T_ThisIsExhibitHall 2
#define T_ExplainExhibitHall 3
#define T_PleaseObtain 4
#define T_WishToFill 5
#define T_ThanksAddedPainting 6
#define T_ItsYouPlayer 7
#define T_PaintingsAttracted 8
#define T_TokenOfGratitude 9
#define T_HonorToHaveYou 10
#define T_PinkFrame 11
#define T_YellowFrame 12
#define T_BlueFrame 13
#define T_RedFrame 14
#define T_GreenFrame 15
#define T_PaintingOfPokemon 16
#define T_Girl 17
#define T_ExpertM 18
#define T_RichBoy 19
MU2_ShowExhibitHall:                        // ..._EventScript_ShowExhibitHall (lockall)
    ActorsPauseAll
    FadeInBlack                             // the Curator's script on 1F left by h_warpsilent: the screen is still black
    FadeWait
    h_applymovement 1, Mv_MU2_CuratorFacePlayer
    h_applymovement 255, Mv_MU2_PlayerFaceLeft
    h_waitmovement
    h_msgbox_actor T_ThisIsExhibitHall, 1
    h_closemessage
    h_applymovement 1, Mv_MU2_FaceExhibitHall
    h_waitmovement
    h_applymovement 255, Mv_MU2_FaceExhibitHall
    h_waitmovement
    h_msgbox_actor T_ExplainExhibitHall, 1
    h_closemessage
    h_applymovement 1, Mv_MU2_CuratorFacePlayer
    h_applymovement 255, Mv_MU2_PlayerFaceLeft
    h_waitmovement
    h_msgbox_actor T_PleaseObtain, 1
    h_setvar VAR_LILYCOVE_MUSEUM_2F_STATE, 1
    h_release

MU2_Curator:                                // ..._EventScript_Curator
    c3_talk
    h_goto_if_set FLAG_RECEIVED_GLASS_ORNAMENT, L_MU2_ReceivedOrnament
    VMCall Sub_MU2_CountPaintings           // specialvar VAR_0x8004, CountPlayerMuseumPaintings -> C8_A
    h_goto_if_eq C8_A, 5, L_MU2_ThankPlayer
    h_goto_if_ne C8_A, 0, L_MU2_AddedPainting
    h_msgbox T_WishToFill
    h_release
L_MU2_AddedPainting:
    h_msgbox T_ThanksAddedPainting
    h_release
L_MU2_ThankPlayer:                          // ..._EventScript_ThankPlayer
    h_buffer_player
    h_msgbox T_ItsYouPlayer
    h_applymovement 1, Mv_MU2_FaceExhibitHall
    h_msgbox T_PaintingsAttracted
    h_closemessage
    ActorSetEyeToEye
    h_msgbox T_TokenOfGratitude             // givedecoration DECOR_GLASS_ORNAMENT: no decorations in Black 2
    h_setflag FLAG_RECEIVED_GLASS_ORNAMENT
    h_release
L_MU2_ReceivedOrnament:
    h_buffer_player
    h_msgbox T_HonorToHaveYou
    h_release

Sub_MU2_CountPaintings:                     // C8_A = how many of the five contest paintings the player made
    WorkSetConst C8_A, 0
    h_call_if_set FLAG_COOL_PAINTING_MADE, Sub_MU2_Count1
    h_call_if_set FLAG_BEAUTY_PAINTING_MADE, Sub_MU2_Count1
    h_call_if_set FLAG_CUTE_PAINTING_MADE, Sub_MU2_Count1
    h_call_if_set FLAG_SMART_PAINTING_MADE, Sub_MU2_Count1
    h_call_if_set FLAG_TOUGH_PAINTING_MADE, Sub_MU2_Count1
    VMReturn
Sub_MU2_Count1:
    WorkAdd C8_A, 1
    VMReturn

    .macro mu2_painting label, flag, nframe
\label:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set \flag, L_MU2_ShowPainting
    MsgPlaceSign \nframe, 2
    MsgPlaceSignClose
    h_release
    .endm
    mu2_painting MU2_CutePainting, FLAG_CUTE_PAINTING_MADE, T_PinkFrame
    mu2_painting MU2_ToughPainting, FLAG_TOUGH_PAINTING_MADE, T_YellowFrame
    mu2_painting MU2_CoolPainting, FLAG_COOL_PAINTING_MADE, T_RedFrame
    mu2_painting MU2_BeautyPainting, FLAG_BEAUTY_PAINTING_MADE, T_BlueFrame
    mu2_painting MU2_SmartPainting, FLAG_SMART_PAINTING_MADE, T_GreenFrame
L_MU2_ShowPainting:                         // ..._EventScript_Show*Painting (showcontestwinner: the picture is not shown)
    MsgPlaceSign T_PaintingOfPokemon, 2
    MsgPlaceSignClose
    h_release

MU2_Girl:
    h_msgbox_npc T_Girl
MU2_ExpertM:
    h_msgbox_npc T_ExpertM
MU2_RichBoy:
    h_msgbox_npc T_RichBoy

    .balign 4, 0
Mv_MU2_CuratorFacePlayer:                   // Common_Movement_FacePlayer (the player arrives to the curator's right)
    face_right
    step_end
Mv_MU2_PlayerFaceLeft:
    walk_in_place_fastest_left
    step_end
Mv_MU2_FaceExhibitHall:
    face_up
    delay_16
    step_end
    .balign 4, 0
