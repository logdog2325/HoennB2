// Jirachi (postgame_scripts, 2026-10-07; user request: a post-game gift at the Mossdeep Space Center, the comet that
// wakes it): the 1F scientist at (2,2) (MossdeepCity_SpaceCenter_1F_EventScript_Scientist, "A rocket launch demands
// perfection...") gives it after the Hall of Fame; his last line answers the woman's question in the same room ("Some
// people claim that Pokémon came from space. Could it be true?"). Sapphire has no such scene (Jirachi
// came on the Pokémon Colosseum bonus disc, Wishmaker Jirachi Lv 5): the lines are NEW, written in Sapphire's style for the
// user to approve (lines 8-11 of src/text/script/0547_room_MossdeepCity_SpaceCenter_1F.txt), and the gift follows
// Sapphire's own Pokémon gift (Route119_WeatherInstitute_2F's Castform: room check, fanfare, "received", givemon).
// Script 1 of 0670 (its ScriptEntry replaces the generated Script_1, which says his Sapphire line before the Hall of Fame).
#include "scenes/postgame_lib.inc"
#define PGSC_T_INTRO 8
#define PGSC_T_RECEIVED 9
#define PGSC_T_NO_ROOM 10
#define PGSC_T_AFTER 11

PG_SC_Scientist:
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, Script_1   // before the Hall of Fame: his Sapphire line
    pg_talk
    h_goto_if_set FLAG_RECEIVED_JIRACHI, L_PGSC_After
    h_msgbox PGSC_T_INTRO                            // Oh! You're the new Champion! ... take care of Jirachi for us?
    h_getpartysize HLIB_TMP
    h_goto_if_eq HLIB_TMP, 6, L_PGSC_NoRoom
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    h_buffer_player
    h_msgbox_info PGSC_T_RECEIVED                    // <player> received Jirachi!
    h_waitfanfare
    h_closemessage
    h_givemon SPECIES_JIRACHI, PG_JIRACHI_LEVEL, HLIB_TMP
    h_setflag FLAG_RECEIVED_JIRACHI
L_PGSC_After:
    h_msgbox PGSC_T_AFTER                            // Jirachi woke up for the comet... Some people claim that Pokémon came from space. Maybe it's true!
    h_release
L_PGSC_NoRoom:
    h_msgbox PGSC_T_NO_ROOM                          // Hm? You don't seem to have any room for this Pokémon. (Sapphire's Castform line)
    h_release
