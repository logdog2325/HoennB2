"""Sapphire's intro instead of Black 2's (user request 2026-10-06: "cut out the black 2 intro, it's jarring").

Text: src/text/system/0054_game_start.txt (Black 2's intro file) carries Prof. Birch's Sapphire speech (text patch).
Code:
- No rival naming (Hugh): NewGame_Main (ov162 0x021a0174, src/ov162/game_start.c) sets state NEW_GAME_RIVAL_NAME_ENTRY
  (7) after the player's name is confirmed (intro result ENTER_RIVAL_NAME); it now sets NEW_GAME_END (12), so the game
  starts right after Birch's last line. `movs r0, #7` at 0x021a022a -> `movs r0, #12`.
- No rival picture in Birch's last lines (Hugh on a red band) and his skipped Sapphire line restored: RIVAL_PICTURE.
- No season card and no Aspertia flyover: EventGameOpening_Callback (ov035 0x0217c964, src/ov035/event_mapchange.c
  :159-187) chains EventSeasonBanner_CreateStandalone (state 1) and Event3DDemo_Create(5) (state 2) through one shared
  GameEvent_ChainNext; the two creates and the ChainNext become no-ops (Season_Set still runs, so the season is set).
- Azurill comes out of Birch's Poké Ball, as in Sapphire (user request 2026-10-06), instead of Juniper's Cinccino:
  SPECIES_CINCCINO (573) -> SPECIES_AZURILL (298) in the intro script (ov294 src/ov294/intro_script.c:24, the
  INTRO_CMD_ADD_SPRITE entry that builds the Pokémon's MCSS sprite, and :55, INTRO_CMD_POKEMON_APPEAR's argument) and
  in the cry ov162 loads before the intro (src/ov162/game_start.c:217, `PokeVoice_Load(SPECIES_CINCCINO, ...)`: the
  literal at 0x021a0170 that `ldr r0` at 0x021a012c reads, its only user). Black 2's own Azurill sprite and cry; the
  intro text names no species (Sapphire's "This is what we call a 'Pokémon.'").
  Emerald: Lotad (270) in the same three places (pokeemerald src/main_menu.c, the Birch speech's Lotad; small_fixes
  2026-10-13, player report); Sapphire and Ruby keep Azurill.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import version  # noqa: E402

CINCCINO, AZURILL, LOTAD = '3d020000', '2a010000', '0e010000'     # u32 573, 298, 270
INTRO_MON = LOTAD if version.is_emerald() else AZURILL

PATCHES = {
    'arm9_ov162.bin': [(0x021a022a - 0x0219ce80, '0720', '0c20'),
                       (0x021a0170 - 0x0219ce80, CINCCINO, INTRO_MON)],     # PokeVoice_Load species (literal pool)
    # IntroCmdEntry = u32 cmd, s32 args[4], u32 runNext (24 bytes); args[1] / args[0] are the species
    'arm9_ov294.bin': [(0x2a6c, CINCCINO, INTRO_MON),     # ADD_SPRITE (cmd 0x17) {POKEMON, species, -5.0, -0.5}
                       (0x2f60, CINCCINO, INTRO_MON)],    # POKEMON_APPEAR (cmd 0x21) {species}
    'arm9_ov035.bin': [(0x0217c9c8 - 0x0217c940, '02f0e2fa', 'c046c046'),     # bl EventSeasonBanner_CreateStandalone
                       (0x0217c9d0 - 0x0217c940, '9af6caf9', 'c046c046'),     # bl GameEvent_ChainNext (shared)
                       (0x0217c9e8 - 0x0217c940, 'e0f7aef8', 'c046c046'),     # bl Event3DDemo_Create (demo 5)
                       # Continue: EventFieldContinue_Callback state 3 enters the map with transition 3 (the season
                       # card); 0 = the plain entrance other callers use (user: no season card, Hoenn has no seasons)
                       (0x0217cd52 - 0x0217c940, '0322', '0022'),
                       # ...with their 5th argument 1 too (every type-0 caller passes 0, 0, 1): with 0 the transition
                       # (ov036 func_021b8d24) skips FieldG3D_SetLCDConfigKeepBGs, which the season card did itself,
                       # so Continue stayed on a blank top screen (tested in DeSmuME, v11: truck and Littleroot)
                       (0x0217cd4a - 0x0217c940, '0020', '0120')],     # movs r0, #0 -> #1 ([sp] = a4)
}

# ---- no rival picture in Birch's last lines (story_infra, user report 2026-10-07: "it shows Hugh's sprite for no
# reason") -- kept apart from the edits above. After the player's name, Black 2's script ASK_RIVAL_NAME (ov294
# src/ov294/intro_script.c sScriptAskRivalName; IntroCmdEntry {u32 cmd, s32 args[4], u32 runNext} = 24 bytes, file
# offset 0x274c) fades the professor out, opens a red band and fades Hugh's picture in (INTRO_CMD_OPEN_BAND,
# INTRO_CMD_OBJ_FADE_IN) for the professor's last lines. Sapphire keeps Birch on screen and shows no rival, so:
#  - 0x277c FADE_SPRITE(professor, out) -> TALK 22: Birch stays, and says Sapphire's "All right, are you ready? / Your
#    very own adventure is about to unfold." (line 22 of text 54, which Black 2's script never showed: it was skipped)
#  - 0x2794 OPEN_BAND, 0x27ac OBJ_FADE_IN -> NOP (INTRO_CMD_NOP 51). The script then says lines 23 and 24 and fades to
#    black as before (SAVE_PAUSE, FADE, END); the band and picture are never shown, so nothing has to close them.
RIVAL_PICTURE = [
    (0x277c, '1d000000' + '00' * 20, '1e000000' '16000000' '00000000' '01000000' '00000000' '00000000'),
    (0x2794, '2d000000' + '00' * 20, '33000000' + '00' * 20),
    (0x27ac, '31000000' + '00' * 20, '33000000' + '00' * 20),
]
PATCHES['arm9_ov294.bin'] = PATCHES['arm9_ov294.bin'] + RIVAL_PICTURE

def apply_code(code):
    done = []
    for name, edits in PATCHES.items():
        path = os.path.join(code, name)
        data = bytearray(open(path, 'rb').read())
        for at, old, new in edits:
            o, n = bytes.fromhex(old), bytes.fromhex(new)
            assert data[at:at + len(o)] in (o, n), f'{name} {at:#x}: unexpected {data[at:at + len(o)].hex()}'
            data[at:at + len(o)] = n
        if os.path.islink(path): os.unlink(path)
        open(path, 'wb').write(data)
        done.append(f'{name}: {len(edits)} edits')
    return '; '.join(done) + ' (no rival naming or rival picture, no season card on new game or Continue, no flyover, ' + ('Lotad' if INTRO_MON == LOTAD else 'Azurill') + ')'
