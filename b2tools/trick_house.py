"""The Trick House on Route 110 (trick_house 2026-10-19; notes/TRICK_HOUSE.md): writes its story scripts, lines, story
objects and the puzzle rooms, faithful per version (Sapphire/Ruby: pokeruby, Emerald: pokeemerald).

    python3 b2tools/trick_house.py            write everything below
    python3 b2tools/trick_house.py --check    print what would change, write nothing

Writes (Sapphire's files are the shared ones; Ruby = Sapphire, pokeruby has no Ruby lines here):
  src/field_scripts/scenes/trick_house_lib.inc          shared defines and macros (zones, puzzles built, sounds)
  src/field_scripts/NNNN_room_Route110_TrickHouse*.s    the story part of each room (after "// ---- story": the room
                                                        generators keep it, b2tools/story_merge.py) + its ScriptEntry
                                                        lines; the puzzle rooms 2-8 are wholly this script's
  src/field_scripts/NNNN_room_*_init.s                  the rooms' map scripts
  src/text/script/NNNN_room_*.txt (+ emerald/)          the lines (line 0 stays the room generator's "…"); Emerald's file
                                                        has the same lines in the same order, pokeemerald's wording
  data/story/trick_house.json (+ emerald/)              the Trick Master, trainers, Cut trees, signs, triggers
  src/field_scripts/scenes/trick_house_test.inc         the test kit (HOENN_TEST_CHTH, Littleroot's town sign)
Room tiles = Sapphire tiles + the room's origin (1, 1) (every Trick House room).
"""
import os, sys, json, re, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter')); sys.path.insert(0, HERE)
import gen_trainers                                          # noqa: E402  (load_texts)
from gen3text import convert                                 # noqa: E402
import move_codes                                            # noqa: E402

RS, EM = os.path.join(ROOT, 'external', 'pokeruby'), os.path.join(ROOT, 'external', 'pokeemerald')
TEXT = {'rs': gen_trainers.load_texts(RS), 'em': gen_trainers.load_texts(EM)}
SCRIPTS = os.path.join(ROOT, 'src', 'field_scripts')
TEXTS = os.path.join(ROOT, 'src', 'text', 'script')
ORIGIN = (1, 1)
REG = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']

ZONES = {'Entrance': 514, 'End': 513, 'Corridor': 512, 1: 552, 2: 432, 3: 434, 4: 438, 5: 441, 6: 442, 7: 447, 8: 449}
ZONE_P3_ALT = 451              # Puzzle 3's other door state (data/interiors/434.json "variants")
BUILT = {'sapphire': 8, 'emerald': 8}      # puzzles 1..n are built (the rest: "the Trick Master is still devising")
P8_READY = True                # puzzle 8 is built too (reached once 6 and 7 are; the test kit's stage 0x7B79 goes there)
P7_READY = True                # puzzle 7 is built too (th_p7: reached once 6 is; the test kit's stage 0x7B68 goes there)
PRIZES = ['ITEM_RARE_CANDY', 'ITEM_TIMER_BALL', 'ITEM_HARD_STONE', 'ITEM_SMOKE_BALL', 'ITEM_TM12', 'ITEM_MAGNET', 'ITEM_PP_MAX']
# (Sapphire/Emerald TM12 Taunt = Black 2's TM12 Taunt)
HIDING = [(6, 3), (11, 5), (9, 1), (3, 1), (0, 5), (11, 1), (8, 1), (4, 4)]   # SetHidingSpotPuzzle1-8 (both versions)

def mapname(k):
    return f'Route110_TrickHouse{k}' if isinstance(k, str) else f'Route110_TrickHousePuzzle{k}'

def files_of(k):
    r = REG[mapname(k)]
    return r['scripts'], r['init_scripts'], r['text']

def zt(x, y):
    """Sapphire tile -> zone tile."""
    return x + ORIGIN[0], y + ORIGIN[1]

def line(rs, em=None):
    """(Sapphire line, Emerald line) of a decomp label each (em: pokeemerald's label, default the same name)."""
    out = []
    for v, lab in (('rs', rs), ('em', em or rs)):
        raw = TEXT[v].get(lab)
        assert raw is not None, f'{v}: no text {lab}'
        s, unknown = convert(raw, expand=True, version_='emerald' if v == 'em' else 'sapphire')
        assert not unknown, (lab, unknown)
        out.append(s)
    return tuple(out)

class Lines:
    """A room's text: line 0 is the room generator's "…"; then ours, in the same order for both versions."""
    def __init__(self):
        self.rows = [('…', '…')]; self.names = {}
    def add(self, name, rs, em=None, same=None):
        if same is not None: pair = (same, same)
        else: pair = line(rs, em)
        self.names[name] = len(self.rows); self.rows.append(pair)
        return self.names[name]
    def defines(self):
        return '\n'.join(f'#define {k} {v}' for k, v in self.names.items())
    def text(self, v):          # (Black 2's font draws ♂/♀ as ⑭/⑮: the Day Care's lines, gen_trainers' class names)
        out = '\n'.join(r[0 if v == 'rs' else 1] for r in self.rows).replace('♂', '⑭').replace('♀', '⑮') + '\n'
        return re.sub(r"(\d)’S\b", r"\1’s", out)   # (the Mechadolls' all-caps "MECHADOLL 1'S", title-cased: "1’s")

# ---------------------------------------------------------------------------------------------------- shared library
LIB = r'''// The Trick House (trick_house 2026-10-19; notes/TRICK_HOUSE.md). GENERATED by b2tools/trick_house.py: edit the
// generator. Included by the Trick House rooms' scripts (each .s is assembled on its own: the guard is per file).
#ifndef TRICK_HOUSE_LIB_INC
#define TRICK_HOUSE_LIB_INC
#define TH_ZONE_ENTRANCE {Entrance}
#define TH_ZONE_END {End}
#define TH_ZONE_CORRIDOR {Corridor}
#define TH_ZONE_P1 {p1}
#define TH_ZONE_P2 {p2}
#define TH_ZONE_P3 {p3}
#define TH_ZONE_P3_ALT {p3alt}
#define TH_ZONE_P4 {p4}
#define TH_ZONE_P5 {p5}
#define TH_ZONE_P6 {p6}
#define TH_ZONE_P7 {p7}
#define TH_ZONE_P8 {p8}
// Puzzles 1..TH_BUILT exist in this version; the next one counts as not ready (the Trick Master keeps devising it),
// so a build is playable up to its last puzzle.
#ifdef HOENN_EMERALD
#define TH_BUILT {built_em}
#else
#define TH_BUILT {built_rs}
#endif
#define TH_P8 {p8_ready}                          // puzzle 8 built (before 6 and 7: only the test kit reaches it so far)
#define TH_P7 {p7_ready}                          // puzzle 7 built (before 6: only the test kit reaches it so far)
#define TH_TM 1                          // the Trick Master's uid in the entrance and the end room (NPC index 0)
#define TH_TM_INDEX 0
#define TH_LOCAL_SETUP 0x4000            // map-local works (Gen 3's VAR_TEMP_*: cleared at every zone init)
#define TH_LOCAL_TALKED 0x4001           // end room VAR_TEMP_2
#define TH_LOCAL_DOOR 0x4002             // end room VAR_TEMP_1 (the door has shut)
#define TH_TMP 0x8032                    // scratch
#define TH_FLAG_NUGGET 2858              // the end room's hidden Nugget (FLAG_HIDDEN_ITEM_1 / _TRICK_HOUSE_NUGGET, slot 39)
#define TH_SE_EXPLOSION SEQ_SE_ZORO_01   // SE_M_EXPLOSION: the Trick Master vanishes (Zorua's illusion pop) [guess]
#define TH_SE_PIN SEQ_SE_DECIDE1         // SE_PIN for a ding (the lock opens, a button) [guess]

    .macro th_info n                     // msgbox n, nobody says it (signs, the scroll, "You're being watched...")
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg \n, 2
    LastKeyWait
    .endm
    .macro th_info_yesno n, var          // MSGBOX_YESNO read from a sign: var = 0 YES, 1 NO
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg \n, 2
    YesNoWin \var
    .endm
    .macro th_say n, actor               // msgbox said by an actor (uid)
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, \n, \actor, 0, 0
    LastKeyWait
    .endm
    .macro th_vanish uid, flag           // Movement_TrickMasterSpin, SE_M_EXPLOSION, Movement_TrickMasterJumpAway,
    ActorCmdExec \uid, Mv_TH_Spin        // removeobject (the movement lists: th_moves)
    ActorCmdWait
    SEPlay TH_SE_EXPLOSION
    ActorCmdExec \uid, Mv_TH_JumpAway
    ActorCmdWait
    ActorDelete \uid
    FlagSet \flag
    .endm
    .macro th_moves                      // the movement lists th_vanish and the scenes use (once per file)
    .balign 4, 0
Mv_TH_Spin:                              // Route110_TrickHouse_Movement_TrickMasterSpin
    face_up
    delay_4
    face_left
    delay_4
    face_down
    delay_4
    face_right
    delay_4
    step_end
    .balign 4, 0
Mv_TH_JumpAway:                          // Route110_TrickHouse_Movement_TrickMasterJumpAway: face_up, disable_anim,
    face_up                              // slide_up x6 (Black 2 has no anim-off action: he dashes off north)
    walk_fast_up 6
    step_end
    .balign 4, 0
Mv_TH_Exclaim:                           // playse SE_PIN + Common_Movement_ExclamationMark ("!" with its own sound)
    emote_exclamation_mark
    step_end
    .balign 4, 0
Mv_TH_Delay48:                           // Common_Movement_Delay48
    delay_16 3
    step_end
    .balign 4, 0
Mv_TH_Invisible:                         // hideobjectat (Gen 3 keeps the hidden object where it is: so does this)
    set_invisible
    step_end
    .endm

// a puzzle room's scroll (Route110_TrickHousePuzzleN_EventScript_Scroll): the first read gives the secret code
    .macro th_scroll statevar, tfound, tmemorized, tagain
    h_lock
    h_goto_if_ne \statevar, 0, .Lthsa\@
    h_setvar \statevar, 1
    WordSetPlayerName 0                  // FoundScroll: playfanfare MUS_OBTAIN_ITEM, message, waitfanfare
    MEPlay SEQ_ME_ITEM
    SystemMsg \tfound, 2
    MEWait
    LastKeyWait
    SystemMsg \tmemorized, 2
    LastKeyWait
    h_release
.Lthsa\@:                                // ReadScrollAgain
    th_info \tagain
    h_release
    .endm
// a puzzle room's door (13,1) (Route110_TrickHousePuzzleN_EventScript_Door, MB_TRICK_HOUSE_PUZZLE_DOOR read facing it):
// locked until the scroll was read; then the code is written, the lock opens and its warp (moved off the map by the
// zone init while locked, th_door_init) comes back onto the door: walking into it leads to the end room.
    .macro th_door statevar, twrote, tlocked, warpidx
    h_lock
    h_goto_if_eq \statevar, 2, .Lthdo\@
    h_goto_if_eq \statevar, 0, .Lthdl\@
    th_info \twrote
    SEPlay TH_SE_PIN
    h_setvar \statevar, 2
    ObjInitWarpGPos \warpidx, 14, 0, 2   // Sapphire (13,1): setmetatile 13, 1, Stairs_Down
.Lthdo\@:
    h_release
.Lthdl\@:
    th_info \tlocked
    h_release
    .endm
// a floor button of puzzle 2 (Route110_TrickHousePuzzle2_EventScript_ButtonN, a trigger while its VAR_TEMP_N is 0):
// PressButtonN: setmetatile the hole -> Door_Shuttered: the hole (a flat object over the room's own lid art) goes
// (setmetatile Button_Pressed: the button stays drawn up)
    .macro th_button work, uid, flag
    h_lock
    h_setvar \work, 1
    SEPlay TH_SE_PIN
    ActorDelete \uid
    FlagSet \flag
    h_release
    .endm
    .macro th_door_init statevar, warpidx   // zone init: the door's warp exists only once the lock is open
    h_goto_if_eq \statevar, 2, .Lthdi\@
    ObjInitWarpGPos \warpidx, 0, 0, 0
.Lthdi\@:
    .endm
#endif
'''

def write(path, text, check, changed):
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
    if old == text: return
    changed.append(os.path.relpath(path, ROOT))
    if not check:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8').write(text)

def write_bin(path, data, check, changed):
    old = open(path, 'rb').read() if os.path.exists(path) else None
    if old == data: return
    changed.append(os.path.relpath(path, ROOT))
    if not check:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'wb').write(data)

def versions_entries(check, changed):
    """data/versions.json: Emerald installs its own maze for each built puzzle room 2-8 (read just before writing:
    other agents edit this file too)."""
    p = os.path.join(ROOT, 'data', 'versions.json')
    v = json.load(open(p, encoding='utf-8'))
    rv = v.setdefault('room_variants', {}).setdefault('emerald', {})
    for n in range(2, 9):
        if n > BUILT['emerald'] and not (n == 8 and P8_READY) and not (n == 7 and P7_READY): continue
        for name in (mapname(n),) + ((P3_ROOM[1],) if n == 3 else ()):
            rv[name] = name + '_Emerald'
            v['rooms'][name + '_Emerald'] = 'emerald'
    s = json.dumps(v, indent=1) + '\n'
    if s != open(p, encoding='utf-8').read():
        changed.append('data/versions.json')
        if not check: open(p, 'w', encoding='utf-8').write(s)

def room_file(k, kind='scripts', ext='.s', overlay=None):
    num = files_of(k)[{'scripts': 0, 'init': 1, 'text': 2}[kind]]
    name = f'{num:04d}_room_{mapname(k)}' + ('_init' if kind == 'init' else '') + ext
    base = SCRIPTS if ext == '.s' else TEXTS
    return os.path.join(base, overlay, name) if overlay else os.path.join(base, name)

def merge_room_script(path, entries, story, includes):
    """The room generator's head (comment, includes, Script_None) with our entries after its ScriptEntry table and
    our story part after the story marker (b2tools/story_merge.py keeps both on a generator rerun)."""
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
    head = old.split('\n// ---- story')[0].rstrip('\n') if old else ''
    lines = head.split('\n')
    lines = [l for l in lines if not re.match(r'\s*ScriptEntry\s+TH_|#include "scenes/trick_house_lib.inc"', l)]
    # our includes after the generator's
    inc_at = max(i for i, l in enumerate(lines) if l.startswith('#include')) + 1
    for inc in reversed(includes):
        if inc not in lines: lines.insert(inc_at, inc)
    end = next(i for i, l in enumerate(lines) if l.strip() == 'ScriptEntriesEnd')
    lines[end:end] = [f'    ScriptEntry {e}' for e in entries]
    return '\n'.join(lines) + '\n\n' + story

INCLUDES = ['#include "hoenn.h"', '#include "hoenn_trainers.h"', '#include "hoenn_story.inc"',
            '#include "scenes/trick_house_lib.inc"']

# ---------------------------------------------------------------------------------------------------- the entrance
def entrance():
    L = Lines()
    L.add('T_BeingWatched', 'Route110_TrickHouseEntrance_Text_YoureBeingWatched')
    found = ['ConcealedBeneathDesk', 'ConcealedBehindTree', 'ConcealedInDresser', 'ConealedBeyondWindow',
             'ConcealedInPlanter', 'ConcealedInCupboard', 'ConcealedBehindWindow', 'ConcealedBeneathCushion']
    for i, f in enumerate(found): L.add(f'T_Found{i}', f'Route110_TrickHouseEntrance_Text_{f}')
    for name, lab in (('T_TheyCallMe', 'TheyCallMeTrickMaster'), ('T_ComeToChallenge', 'ComeToChallengeTrickHouse'),
                      ('T_ItsAScroll', 'ItsAScroll'), ('T_GoInHole', 'GoInHoleBehindScroll'),
                      ('T_JourneyNote', 'LeavingOnJourneyNote'), ('T_NextTimeTrick', 'NextTimeUseThisTrick'),
                      ('T_Devising', 'InMidstOfDevisingNewChallenges'), ('T_AcceptReward', 'YoureHereToAcceptReward'),
                      ('T_NotClaim', 'DidYouNotComeToClaimReward')):
        L.add(name, f'Route110_TrickHouseEntrance_Text_{lab}')
    L.add('T_BagFull', 'Text_TooBadBagIsFull', 'gText_TooBadBagIsFull')
    sc, ini, tx = files_of('Entrance')
    hide = '\n'.join(f'''L_THE_Hide{i}:
    h_setobjectxyperm TH_TM_INDEX, {zt(*p)[0]}, {zt(*p)[1]}, 2
    VMReturn''' for i, p in enumerate(HIDING))
    hide_sw = '\n'.join(f'    h_goto_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, {i}, L_THE_Hide{i}' for i in range(8))
    found_sw = '\n'.join(f'    h_call_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, {i}, L_THE_FoundLine{i}' for i in range(8))
    found_lines = '\n'.join(f'''L_THE_FoundLine{i}:
    h_msgbox T_Found{i}
    VMReturn''' for i in range(8))
    ready = '\n'.join(f'''    h_call_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, {i}, L_THE_Ready{i + 1}''' for i in range(1, 8))
    badge_checks = []
    for n in range(2, 9):         # CheckReadyForPuzzleN: puzzle N needs badge N+1 (Dynamo..Rain), puzzle 8 the game cleared
        body = (f'    h_goto_if_badge {n + 1}, L_THE_ReadyBuilt{n}\n    VMJump L_THE_NotReady' if n < 8 else
                f'    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_THE_ReadyBuilt{n}\n    VMJump L_THE_NotReady')
        badge_checks.append(f'''L_THE_Ready{n}:                         // CheckReadyForPuzzle{n}
{body}
L_THE_ReadyBuilt{n}:
#if {'!TH_P8' if n == 8 else '(TH_BUILT < 7 && !TH_P7)' if n == 7 else f'TH_BUILT < {n}'}
    VMJump L_THE_NotReady                // (puzzle {n} is not built in this build: still devising)
#endif
    VMReturn''')
    prizes = '\n'.join(f'''L_THE_Prize{i + 1}:
    h_giveitem {PRIZES[i]}
    VMJump L_THE_PrizeGiven''' for i in range(7))
    prize_sw = '\n'.join(f'    h_goto_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, {i + 1}, L_THE_Prize{i + 1}' for i in range(7))
    enter_sw = '\n'.join(f'    h_goto_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, {i}, L_THE_Enter{i + 1}' for i in range(8))
    p3_reset = ('    h_setvar VAR_TRICK_HOUSE_PUZZLE_3_DOORS, 0             // puzzle 3\'s OnTransition: VAR_TEMP_1-9 = 0\n'
                '    h_setvar VAR_TRICK_HOUSE_PUZZLE_3_BUTTON, 0            // (saved here: they must last through its\n'
                + ''.join(f'    h_clearflag FLAG_TRICK_HOUSE_PUZZLE_3_ROCK_{j}\n' for j in range(1, 5)))   # zone swaps)
    enters = '\n'.join(f'''L_THE_Enter{i + 1}:
{p3_reset if i == 2 else ''}    h_warp_arrive TH_ZONE_P{i + 1}, {zt(0, 21)[0]}, {zt(0, 21)[1]}, 0
    h_release''' for i in range(8))
    story = f'''// ---- story (trick_house 2026-10-19, notes/TRICK_HOUSE.md; GENERATED by b2tools/trick_house.py: edit the generator)
// Sapphire/Ruby data/maps/Route110_TrickHouseEntrance/scripts.inc, Emerald's (pokeemerald) where it differs (#ifdef
// HOENN_EMERALD). The Trick Master = uid 1, NPC index 0 (data/story/trick_house.json); hidden = present and invisible
// (set_invisible from the scene condition TH_LOCAL_SETUP == 0, as the invisible Kecleons: scenes/ch7_lib.inc), placed per
// level by the zone init. Map scripts: {ini:04d}_room_Route110_TrickHouseEntrance_init.s. Room tiles = Sapphire + (1, 1).
{L.defines()}

TH_E_Init:                               // zone init: Route110_TrickHouseEntrance_OnTransition + the OnWarp object setup
    h_setflag FLAG_LANDMARK_TRICK_HOUSE
    VMCall L_THE_Transition
    VMCall L_THE_Place
    VMHalt

L_THE_Transition:
    h_goto_if_eq VAR_TRICK_HOUSE_STATE, 1, L_THE_FromCorridor
    h_goto_if_eq VAR_TRICK_HOUSE_PRIZE_PICKUP, 1, L_THE_RewardReady
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_2, 1, L_THE_ToDoor
    h_call_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 5, L_THE_CheckReady
    h_call_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 3, L_THE_CheckReady
    h_call_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 0, L_THE_CheckReady
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 0, L_THE_WatchedOn
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 1, L_THE_WatchedOff
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 3, L_THE_WatchedOff
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 4, L_THE_WatchedOff
    VMReturn
L_THE_WatchedOn:                         // ReadyBeingWatchedTrigger
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE, 0
    VMReturn
L_THE_WatchedOff:                        // SetNotBeingWatched1-3
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE, 1
    VMReturn
L_THE_RewardReady:                       // SetReadyToGiveReward
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE, 1
    h_goto_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, 8, L_THE_TentReady
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 2
    VMReturn
L_THE_TentReady:
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 6
    VMReturn
L_THE_FromCorridor:                      // EnterFromCorridor
    h_setvar VAR_TRICK_HOUSE_STATE, 0
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 5
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE, 1
    VMReturn
L_THE_ToDoor:                            // MoveTrickMasterToDoor: setobjectxyperm 1, 5, 2
    h_setobjectxyperm TH_TM_INDEX, {zt(5, 2)[0]}, {zt(5, 2)[1]}, 3
    VMReturn
L_THE_CheckReady:                        // CheckReadyForNextPuzzle
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 0
{ready}
    h_call_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, 8, L_THE_Finished
    VMReturn
L_THE_Finished:                          // FinishedPuzzles
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 4
    VMReturn
L_THE_NotReady:                          // NotReadyForPuzzle
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 3
    VMReturn
L_THE_Ready1:
    VMReturn
{chr(10).join(badge_checks)}

L_THE_Place:                             // the OnWarp table: who is where (spawn flag + setobjectxyperm, the zone init's way)
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_2, 1, L_THE_PlaceFound
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 0, L_THE_PlaceHiding
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 2, L_THE_PlaceAtScroll
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 3, L_THE_PlaceAtScroll
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 6, L_THE_PlaceInFront
    h_setflag FLAG_HIDE_TRICKMASTER_ENTRANCE     // 1, 4, 5: RemoveTrickMaster
    VMReturn
L_THE_PlaceFound:                        // TrickMasterFound: at (5,2) facing east (the player arrives at (6,2) facing west)
    h_clearflag FLAG_HIDE_TRICKMASTER_ENTRANCE
    VMReturn
L_THE_PlaceAtScroll:                     // SetTrickMasterFacingDoor: (5,2) facing north
    h_clearflag FLAG_HIDE_TRICKMASTER_ENTRANCE
    h_setobjectxyperm TH_TM_INDEX, {zt(5, 2)[0]}, {zt(5, 2)[1]}, 0
    VMReturn
L_THE_PlaceInFront:                      // SetTrickMasterInFrontOfDoor: (5,2) facing south
    h_clearflag FLAG_HIDE_TRICKMASTER_ENTRANCE
    h_setobjectxyperm TH_TM_INDEX, {zt(5, 2)[0]}, {zt(5, 2)[1]}, 1
    VMReturn
L_THE_PlaceHiding:                       // SetTrickMasterHidingSpot (hideobjectat: TH_E_Setup)
    h_clearflag FLAG_HIDE_TRICKMASTER_ENTRANCE
{hide_sw}
    VMReturn
{hide}

TH_E_Setup:                              // scene condition TH_LOCAL_SETUP == 0 (after every zone entry, battle or menu)
    h_setvar TH_LOCAL_SETUP, 1
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_2, 1, L_THE_SetupFound
    h_goto_if_ne VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 0, L_THE_SetupDone
    ActorCmdExec TH_TM, Mv_TH_Invisible  // hideobjectat 1
    ActorCmdWait
L_THE_SetupDone:
    VMHalt
L_THE_SetupFound:                        // turnobject LOCALID_PLAYER, DIR_WEST
    ActorCmdExec 255, Mv_THE_FaceLeft
    ActorCmdWait
    VMHalt

TH_E_Reload:                             // field load / return (MapScript 3/4): hide him again once the field is up
    h_setvar TH_LOCAL_SETUP, 0
    VMHalt

TH_E_BeginChallenge:                     // scene condition VAR_TRICK_HOUSE_ENTRANCE_STATE_2 == 1 (BeginChallenge)
    h_lock
    h_delay 20
    h_call_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, 0, L_THE_Meet
    th_say T_ComeToChallenge, TH_TM
    h_closemessage
    h_delay 20
    th_vanish TH_TM, FLAG_HIDE_TRICKMASTER_ENTRANCE
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 1
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_2, 0
    h_release
L_THE_Meet:                              // MeetTrickMaster
    th_say T_TheyCallMe, TH_TM
    VMReturn

TH_E_TrickMaster:                        // Route110_TrickHouseEntrance_EventScript_TrickMaster
    h_lock
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 0, L_THE_FoundHim
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 2, L_THE_GiveReward
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 3, L_THE_StillMaking
    h_release                            // (6: Mechadoll 5's tent: a tent never fills a PC here, see the end room)
L_THE_FoundHim:                          // FoundTrickMaster
    ActorCmdExec 255, Mv_TH_Exclaim
    ActorCmdWait
    ActorCmdExec 255, Mv_TH_Delay48
    ActorCmdWait
{found_sw}
    h_closemessage
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_2, 1
    h_warp_arrive TH_ZONE_ENTRANCE, {zt(6, 2)[0]}, {zt(6, 2)[1]}, 2      // warp(silent) to (6,2)
    h_release
{found_lines}
L_THE_StillMaking:                       // StillMakingPuzzle
    h_msgbox T_NextTimeTrick
    h_closemessage
    ActorSetEyeToEye                     // Common_Movement_FacePlayer
    ActorCmdExec TH_TM, Mv_TH_Exclaim
    ActorCmdWait
    ActorCmdExec TH_TM, Mv_TH_Delay48
    ActorCmdWait
    h_msgbox T_Devising
    ActorCmdExec TH_TM, Mv_THE_TurnUp    // Common_Movement_WalkInPlaceFastestUp
    ActorCmdWait
    h_release
L_THE_GiveReward:                        // GiveReward: the prize the full Bag kept
    ActorSetEyeToEye
    h_msgbox T_AcceptReward
    h_closemessage
{prize_sw}
    h_release
{prizes}
L_THE_PrizeGiven:
    h_goto_if_eq HLIB_RESULT, 1, L_THE_GotReward
    h_msgbox T_BagFull                   // Common_EventScript_BagIsFull
    h_msgbox T_NotClaim
    h_release
L_THE_GotReward:
    h_setvar VAR_TRICK_HOUSE_PRIZE_PICKUP, 0
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 3
    ActorCmdExec TH_TM, Mv_THE_TurnUp
    ActorCmdWait
    h_release

TH_E_Scroll:                             // Route110_TrickHouseEntrance_EventScript_Door (the scroll, read facing north)
    h_lock
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 0, L_THE_ItsAScroll
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 1, L_THE_GoInHole
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 4, L_THE_Note
    h_goto_if_eq VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 5, L_THE_CheckNote
    h_release
L_THE_ItsAScroll:
    th_info T_ItsAScroll
    h_release
L_THE_CheckNote:                         // CheckLevelForMessage
    h_goto_if_ne VAR_TRICK_HOUSE_ROOMS_COMPLETED, 8, L_THE_ItsAScroll
L_THE_Note:                              // LeftOnJourneyNote
    th_info T_JourneyNote
    h_release
L_THE_GoInHole:                          // GoInHolePrompt -> EnterPuzzleRoom
    th_info_yesno T_GoInHole, TH_TMP
    h_closemessage
    h_goto_if_eq TH_TMP, 0, L_THE_EnterRoom
    h_release
L_THE_EnterRoom:                         // (setmetatile 5, 1 Stairs_Down: the scroll stays drawn) walk_up, set_invisible
    h_delay 20
    ActorCmdExec 255, Mv_THE_IntoHole
    ActorCmdWait
{enter_sw}
    h_release
{enters}

TH_E_Watched:                            // TrickMasterHiding: trigger (4,7) (5,6) (6,6) (7,7) while ..._ENTRANCE_STATE is 0
    h_lock
    th_info T_BeingWatched
    h_closemessage
    h_goto_if_gt VAR_TRICK_HOUSE_ROOMS_COMPLETED, 2, L_THE_NoSparkle
    ActorCmdExec TH_TM, Mv_THE_Sparkle   // DoHidingSpotSparkle at his spot (no sparkle effect: the "..." balloon)
    ActorCmdWait
L_THE_NoSparkle:
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE, 1
    h_release

    th_moves
    .balign 4, 0
Mv_THE_FaceLeft:
    face_left
    step_end
    .balign 4, 0
Mv_THE_TurnUp:
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
Mv_THE_IntoHole:                         // Common_Movement_WalkUp + Movement_EnterRoom
    walk_up
    set_invisible
    step_end
    .balign 4, 0
Mv_THE_Sparkle:
    hmv 161                              // the "..." balloon
    step_end
'''
    entries = ['TH_E_TrickMaster        // story: 2: the Trick Master (uid 1)',
               'TH_E_Scroll             // story: 3: the scroll (5,1)',
               'TH_E_Watched            // story: 4: "You\'re being watched..." triggers',
               'TH_E_Init               // story: 5: zone init',
               'TH_E_Setup              // story: 6: scene condition TH_LOCAL_SETUP == 0',
               'TH_E_BeginChallenge     // story: 7: scene condition VAR_TRICK_HOUSE_ENTRANCE_STATE_2 == 1',
               'TH_E_Reload             // story: 8: field load / return']
    init = f'''// Map scripts of Route110_TrickHouseEntrance (zone {ZONES["Entrance"]}; GENERATED by b2tools/trick_house.py): zone init 5,
// field load / return 8, scene conditions: the object setup (6), then the Trick Master's intro (7).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "scenes/trick_house_lib.inc"

    MapScript 2, 5
    MapScript 3, 8
    MapScript 4, 8
    MapScriptConditions THE_Conditions
    MapScriptsEnd
THE_Conditions:
    MapScriptCondition TH_LOCAL_SETUP, 0, 6
    MapScriptCondition VAR_TRICK_HOUSE_ENTRANCE_STATE_2, 1, 7
    MapScriptConditionsEnd
    .balign 4, 0
'''
    return L, entries, story, init

# ---------------------------------------------------------------------------------------------------- the end room
def end_room():
    L = Lines()
    L.add('T_MadeItToMe', 'Route110_TrickHouseEnd_Text_YouveMadeItToMe')
    allnight = [('AllNightToPlantTrees', None), ('AllNightToMakeMaze', None), ('19C3A7', 'AllNightToPreparePanels'),
                ('AllNightToShoveBoulders', None), ('AllNightToMakeMechadolls', None), ('AllNightToInstallDoors', None),
                ('AllNightSettingUpArrows', None), ('AllNightPolishingFloors', None)]
    for i, (rs, em) in enumerate(allnight):
        L.add(f'T_AllNight{i}', f'Route110_TrickHouseEnd_Text_{rs}', f'Route110_TrickHouseEnd_Text_{em or rs}')
    for name, lab in (('T_Earned', 'YouHaveEarnedThisReward'), ('T_NewTricks', 'MakeNewTricksToStumpYou'),
                      ('T_NoRoom', 'NoRoomForThis'), ('T_RunDry', 'FountainOfIdeasRunDry'),
                      ('T_Journey', 'LeavingOnJourney'), ('T_Ignoring', 'YoureIgnoringMe')):
        L.add(name, f'Route110_TrickHouseEnd_Text_{lab}')
    L.add('T_Tent', 'Route110_TrickHouseEnd_Text_DefeatedMeTakeTent', 'Route110_TrickHouseEnd_Text_DefeatedMePreferWhichTent')
    L.add('T_BagFull', 'Text_TooBadBagIsFull', 'gText_TooBadBagIsFull')
    red, blue = (convert(TEXT['em'][k], expand=True, version_='emerald')[0] for k in ('gText_RedTent', 'gText_BlueTent')) \
        if 'gText_RedTent' in TEXT['em'] else ('Red Tent', 'Blue Tent')
    L.add('T_RedTent', None, same=red)
    L.add('T_BlueTent', None, same=blue)
    sc, ini, tx = files_of('End')
    levels = []
    for i in range(7):
        levels.append(f'''L_THX_Done{i + 1}:                        // CompletedPuzzle{i + 1}
    h_msgbox T_AllNight{i}
    h_msgbox T_Earned
    h_setvar VAR_TRICK_HOUSE_PRIZE_PICKUP, 0
    h_closemessage
    h_giveitem {PRIZES[i]}
    h_call_if_eq HLIB_RESULT, 0, L_THX_BagFull
    h_msgbox T_NewTricks
    h_closemessage
    VMCall L_THX_Exit
    h_release''')
    sw = '\n'.join(f'    h_goto_if_eq VAR_TRICK_HOUSE_ROOMS_COMPLETED, {i}, L_THX_Done{i + 1}' for i in range(8))
    story = f'''// ---- story (trick_house 2026-10-19, notes/TRICK_HOUSE.md; GENERATED by b2tools/trick_house.py: edit the generator)
// Sapphire/Ruby data/maps/Route110_TrickHouseEnd/scripts.inc, Emerald's where it differs. The Trick Master = uid 1, NPC
// index 0 (data/story/trick_house.json), at (4,5) facing east; he comes back on every entry (OnWarp addobject). The door
// you came in by (10,1) shuts behind you (OnFrame CloseDoor): its warp (warp 0: you arrive through it, stepping out
// south) is moved off the map once the field is up (TH_X_CloseDoor), so walking into the door does nothing.
// Map scripts: {ini:04d}_room_Route110_TrickHouseEnd_init.s. Room tiles = Sapphire + (1, 1).
{L.defines()}

TH_X_Init:                               // zone init (OnTransition + OnWarp): VAR_TEMP_1/2 = 0 (map-local works),
    h_setflag TH_FLAG_NUGGET             // SetTrickHouseEndRoomFlag / SetTrickHouseNuggetFlag: the Nugget under him
    h_clearflag FLAG_HIDE_TRICK_HOUSE_END_MAN    // addobject 1 (he is there whenever you come in)
    VMHalt

TH_X_CloseDoor:                          // scene condition TH_LOCAL_DOOR == 0: OnFrame CloseDoor (setmetatile 10, 1,
    h_setvar TH_LOCAL_DOOR, 1            // Door_Closed): the door's warp off the map
    ObjInitWarpGPos 0, 0, 0, 0
    VMHalt
TH_X_Reload:                             // field load / return: shut it again once the field is up (OnResume)
    h_setvar TH_LOCAL_DOOR, 0
    VMHalt

TH_X_TrickMaster:                        // Route110_TrickHouseEnd_EventScript_TrickMaster
    h_lock
    h_faceplayer
    h_msgbox T_MadeItToMe
    h_setvar TH_LOCAL_TALKED, 1
{sw}
    h_release
{chr(10).join(levels)}
L_THX_Done8:                             // CompletedPuzzle8: the last puzzle
    h_msgbox T_AllNight7
    h_closemessage
    h_getplayerfacing TH_TMP             // he turns away from the player (TrickMasterFaceAway*)
    h_call_if_eq TH_TMP, 0, L_THX_AwayUp
    h_call_if_eq TH_TMP, 1, L_THX_AwayDown
    h_call_if_eq TH_TMP, 2, L_THX_AwayLeft
    h_call_if_eq TH_TMP, 3, L_THX_AwayRight
    h_delay 30
    h_msgbox T_RunDry
    h_closemessage
    ActorSetEyeToEye                     // Common_Movement_FacePlayer
    h_delay 30
    h_msgbox T_Tent                      // (Sapphire: the Blue Tent, Ruby: the Red Tent; Emerald asks which)
    h_setvar VAR_TRICK_HOUSE_PRIZE_PICKUP, 0
#ifdef HOENN_EMERALD
    ListMenu_AnchorTopRight 31, 7, 0, 0, TH_TMP     // multichoice 0, 0, MULTI_TENT, 1 (RED TENT / BLUE TENT)
    ListMenuAdd T_RedTent, 65535, 0
    ListMenuAdd T_BlueTent, 65535, 1
    ListMenuShow
#endif
    // givedecoration DECOR_*_TENT: Black 2 has no decorations or Secret Bases (as the Wailmer Doll, Sootopolis): no
    // item, and so never "No room in your PC" (Mechadoll 5's later hand-over at the entrance can't happen either)
    h_msgbox T_Journey
    VMCall L_THX_Exit
    h_clearflag TH_FLAG_NUGGET           // ResetTrickHouseEndRoomFlag / ResetTrickHouseNuggetFlag
    h_release
L_THX_AwayUp:
    h_move TH_TM, 40
    VMReturn
L_THX_AwayDown:
    h_move TH_TM, 41
    VMReturn
L_THX_AwayLeft:
    h_move TH_TM, 42
    VMReturn
L_THX_AwayRight:
    h_move TH_TM, 43
    VMReturn
L_THX_Exit:                              // TrickMasterExit
    th_vanish TH_TM, FLAG_HIDE_TRICK_HOUSE_END_MAN
    h_addvar VAR_TRICK_HOUSE_ROOMS_COMPLETED, 1
    VMReturn
L_THX_BagFull:                           // BagFull
    h_msgbox T_BagFull                   // Common_EventScript_BagIsFull
    h_msgbox T_NoRoom
    h_setvar VAR_TRICK_HOUSE_PRIZE_PICKUP, 1
    VMReturn

TH_X_Ignoring:                           // TrickMasterExitTrigger: (2,2) while TH_LOCAL_TALKED (VAR_TEMP_2) is 0
    h_lock
    h_turnobject TH_TM, 2
    ActorCmdExec TH_TM, Mv_TH_Exclaim
    ActorCmdWait
    h_delay 20
    h_move TH_TM, 50                     // Movement_TrickMasterSurprise: jump_in_place_left
    SEPlay TH_SE_EXPLOSION
    h_move 255, 41                       // Common_Movement_WalkInPlaceFastestDown
    th_say T_Ignoring, TH_TM
    h_closemessage
    h_move 255, 13                       // Movement_KeepPlayerInRoom: walk_down
    h_delay 4
    h_turnobject TH_TM, 3
    h_release

    th_moves
'''
    entries = ['TH_X_TrickMaster        // story: 2: the Trick Master (uid 1)',
               'TH_X_Ignoring           // story: 3: trigger (2,2)',
               'TH_X_Init               // story: 4: zone init',
               'TH_X_CloseDoor          // story: 5: scene condition TH_LOCAL_DOOR == 0',
               'TH_X_Reload             // story: 6: field load / return']
    init = f'''// Map scripts of Route110_TrickHouseEnd (zone {ZONES["End"]}; GENERATED by b2tools/trick_house.py): zone init 4,
// field load / return 6, scene condition: the door shuts (5).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "scenes/trick_house_lib.inc"

    MapScript 2, 4
    MapScript 3, 6
    MapScript 4, 6
    MapScriptConditions THX_Conditions
    MapScriptsEnd
THX_Conditions:
    MapScriptCondition TH_LOCAL_DOOR, 0, 5
    MapScriptConditionsEnd
    .balign 4, 0
'''
    return L, entries, story, init

def corridor():
    story = '''// ---- story (trick_house 2026-10-19, notes/TRICK_HOUSE.md; GENERATED by b2tools/trick_house.py: edit the generator)
TH_C_Init:                               // Route110_TrickHouseCorridor_OnTransition: back in the entrance, the Trick
    h_setvar VAR_TRICK_HOUSE_STATE, 1    // Master is gone (EnterFromCorridor)
    VMHalt
'''
    init = f'''// Map scripts of Route110_TrickHouseCorridor (zone {ZONES["Corridor"]}; GENERATED by b2tools/trick_house.py): zone init 2.
#include "asm/field_script.inc"

    MapScript 2, 2
    MapScriptsEnd
    .balign 4, 0
'''
    return Lines(), ['TH_C_Init               // story: 2: zone init'], story, init

# ---------------------------------------------------------------------------------------------------- the puzzle rooms
# (Sapphire/Ruby label, Emerald label) of the lines every puzzle room has. Sapphire's door line of puzzle N is labelled
# Puzzle(N-1)'s (puzzle 1: UnknownString_819CAD1), as pokeruby's Route110_TrickHousePuzzleN_EventScript_Door uses them.
def puzzle_common(L, n):
    L.add('T_FoundScroll', 'Route110_TrickHousePuzzle1_Text_FoundAScroll', 'Route110_TrickHousePuzzle_Text_FoundAScroll')
    L.add('T_Memorized', 'Route110_TrickHousePuzzle1_Text_MemorizedTheCode', 'Route110_TrickHousePuzzle_Text_MemorizedSecretCode')
    L.add('T_CodeOnIt', 'Route110_TrickHousePuzzle1_Text_SecretCodeOnIt', 'Route110_TrickHousePuzzle_Text_SecretCodeWrittenOnIt')
    L.add('T_Locked', 'Route110_TrickHousePuzzle_Text_DoorLockedWriteSecretCodeHere',
          'Route110_TrickHouseEntrance_Text_DoorLockedWriteSecretCodeHere')
    rs = 'UnknownString_819CAD1' if n == 1 else f'Route110_TrickHousePuzzle{n - 1}_Text_WroteSecretCodeLockOpened'
    L.add('T_Wrote', rs, f'Route110_TrickHousePuzzle{n}_Text_WroteSecretCodeLockOpened')

def puzzle1():
    L = Lines(); puzzle_common(L, 1)
    sc, ini, tx = files_of(1)
    story = f'''// ---- story (trick_house 2026-10-19, notes/TRICK_HOUSE.md; GENERATED by b2tools/trick_house.py: edit the generator)
// Sapphire/Ruby data/maps/Route110_TrickHousePuzzle1/scripts.inc (Emerald's is the same script on its own maze). The
// scroll, the door (13,1), the trainers (Black 2 eye-contact trainers, global 3000 + id) and the Cut trees (code 108,
// global 10004) are in data/story/trick_house.json (Emerald: data/story/emerald/trick_house.json). Map scripts:
// {ini:04d}_room_Route110_TrickHousePuzzle1_init.s. Room tiles = Sapphire + (1, 1).
{L.defines()}
#define TH_DOOR_WARP 2                   // the door's warp: Sapphire warp 2 (13,1), third in data/interiors/552.json

TH_P1_Init:                              // OnLoad: the door is open once the code is written (VAR_..._1_STATE 2)
    th_door_init VAR_TRICK_HOUSE_PUZZLE_1_STATE, TH_DOOR_WARP
    VMHalt
TH_P1_Scroll:                            // Route110_TrickHousePuzzle1_EventScript_Scroll
    th_scroll VAR_TRICK_HOUSE_PUZZLE_1_STATE, T_FoundScroll, T_Memorized, T_CodeOnIt
TH_P1_Door:                              // Route110_TrickHousePuzzle1_EventScript_Door
    th_door VAR_TRICK_HOUSE_PUZZLE_1_STATE, T_Wrote, T_Locked, TH_DOOR_WARP
'''
    entries = ['TH_P1_Scroll            // story: 2: the scroll',
               'TH_P1_Door              // story: 3: the door (13,1)',
               'TH_P1_Init              // story: 4: zone init']
    init = f'''// Map scripts of Route110_TrickHousePuzzle1 (zone {ZONES[1]}; GENERATED by b2tools/trick_house.py): zone init 4.
#include "asm/field_script.inc"

    MapScript 2, 4
    MapScriptsEnd
    .balign 4, 0
'''
    return L, entries, story, init

# ---------------------------------------------------------------------------------------------------- new puzzle rooms
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
INTERIORS = os.path.join(ROOT, 'data', 'interiors')
HOLE_MODEL = 142               # src/objects3d/008e-trick-hole (patches/objects3d.py FREE_PEOPLE_RECORDS)
MT_SHUTTERED, MT_HOLE = 0x26A, 0x269

def scripts_inc(v, n):
    return open(os.path.join(RS if v == 'rs' else EM, 'data', 'maps', mapname(n), 'scripts.inc')).read()

def p2_buttons(v):
    """[(button (x, y), hole (x, y))] of puzzle 2: PressButton1-4's setmetatile lines (Button_Pressed, Door_Shuttered)."""
    src = scripts_inc(v, 2); out = []
    for k in range(1, 5):
        body = re.search(rf'Route110_TrickHousePuzzle2_EventScript_PressButton{k}::(.*?)return', src, re.S).group(1)
        b = re.search(r'setmetatile (\d+), (\d+), METATILE_TrickHousePuzzle_Button_Pressed', body)
        h = re.search(r'setmetatile (\d+), (\d+), METATILE_TrickHousePuzzle_Door_Shuttered', body)
        out.append(((int(b[1]), int(b[2])), (int(h[1]), int(h[2]))))
    return out

def scroll_at(v, n):
    mj = map_json(v, n)
    return next((b['x'], b['y']) for b in mj['bg_events'] if b.get('script', '').endswith(('_Scroll', '_16328B')))

def puzzle_recipe(v, n, floor_tex=(), unblock=(), doc=''):
    """A puzzle room's recipe on puzzle 1's rules (data/interior_layouts/Route110_TrickHousePuzzle1.json): the green
    check floor, the back wall with the exit door (13,1), the door mat (0,21)-(1,21), every solid tile of rows 2-21 a
    low plank box (8 high: Sapphire's plank walls), the scroll a one-tile table; Gen 3 metatile art on the floor where
    the puzzle draws something (floor_tex), tiles a script opens walkable (unblock)."""
    import models_interior as mi
    base = json.load(open(os.path.join(LAYOUTS, 'Route110_TrickHousePuzzle1.json')))
    m = ('pokeemerald/' if v == 'em' else '') + mapname(n)
    sm = mi.sapphire_map(m)
    solid = {(x, z) for z in range(sm['h']) for x in range(sm['w']) if not sm['walk'][z][x]}
    sc = scroll_at(v, n)
    keep = set(map(tuple, unblock)) | {sc}
    # (th_glitch 2026-10-19) Gen 3's ledges (MB_JUMP_*: puzzle 4's row of jump-south tiles, both versions) are Black 2
    # ledge cells ("ledges": you hop down them as in Gen 3, and can always get back to the exit mats), drawn as low
    # steps (6 high, Lavaridge B1F's ledges) with Gen 3's ledge art on top and in front, not as plank boxes
    ledges = sorted([x, z] for x, z in solid if 2 <= z <= 21 and 0x38 <= sm['beh'][z][x] <= 0x3B)
    boxes = sorted([list(t) for t in solid if 2 <= t[1] <= 21 and t not in keep and list(t) not in ledges])
    door = next(f for f in base['furniture'] if f['m'] == 'cabin_door')
    r = {'_doc': (f"Trick House puzzle room {n} ({'Emerald (pokeemerald)' if v == 'em' else 'Sapphire/Ruby (pokeruby)'}"
                  f"'s map, 15x22, zone {ZONES[n]}): GENERATED by b2tools/trick_house.py on puzzle 1's rules (green check "
                  "floor b01_mat1, wood walls, every solid tile of rows 2-21 a low plank box of in01_kibako01, the exit door "
                  f"(13,1) in the back wall, the scroll {sc} a one-tile table). " + doc),
         'map': m, 'style': base['style'], 'floor': base['floor'], 'mats': base['mats'],
         'furniture': [door, dict(m='desk02', tile=list(sc), _what=f'the scroll {sc}: a one-tile table')],
         'blocks': [dict(base['blocks'][0], tiles=boxes, _what='the plank walls: low plank boxes (8 high)')]}
    if floor_tex: r['floor_tex'] = list(floor_tex)
    if unblock: r['unblock'] = [list(t) for t in unblock]
    if ledges:
        r['ledges'] = True
        grid = gen3_grid(v, n); by_mt = {}
        for t in ledges: by_mt.setdefault(grid[tuple(t)], []).append(t)
        for mt, tiles in sorted(by_mt.items()):
            name = f'th{v[0]}{mt:03x}'; src = ['gen3', m, tiles[0][0], tiles[0][1], mt]
            r['blocks'].append({'h': 6, 'top': {'tex': name, 'src': src, 'size': 16},
                                'side': {'tex': name, 'src': src, 'u_size': 16, 'v': [0, 6 / 16]}, 'shade_top': 1.0,
                                'tiles': tiles, '_what': f'ledges (metatile {mt:#x}, MB_JUMP_*): Black 2 ledge cells'})
    return r

def gen3_floor(v, at, mt=None, what=''):
    """A floor patch showing Gen 3's own metatile art (the map's own at `at`, or metatile mt) at `at`. Texture names are
    per version and art (rooms sharing interior area 282 share them: same name, same picture)."""
    name = f'th{v[0]}_{at[0]}_{at[1]}' if mt is None else f'th{v[0]}{mt:03x}'
    d = dict(tex=name, gen3=list(at), rect=[at[0], at[1], at[0], at[1]], stretch=True, _what=what)
    if mt is not None: d['gen3_mt'] = mt
    return d

def zone_json(n, doc):
    return {'_doc': doc, 'zone': ZONES[n], 'room': mapname(n), 'area': 282, 'parent': 368, 'optional': True,
            'warps': [dict(at=[0, 21], tile_only=True, to=[ZONES['Entrance'], 2], what='Sapphire warp 0 -> Route110_TrickHouseEntrance 2'),
                      dict(at=[1, 21], tile_only=True, to=[ZONES['Entrance'], 2], what='Sapphire warp 1 -> Route110_TrickHouseEntrance 2'),
                      dict(at=[13, 1], tile_only=True, to=[ZONES['End'], 0],
                           what='Sapphire warp 2 -> Route110_TrickHouseEnd 0 (the door: off the map until the lock opens)')],
            'npcs': [], 'signs': []}

def item_balls(v, n):
    """The puzzle's item balls (data/hoenn_items.json / data/emerald/hoenn_items.json: script 7000 + slot, saved flag)."""
    items = json.load(open(os.path.join(ROOT, 'data', 'emerald' if v == 'em' else '', 'hoenn_items.json')))['balls']
    mj = map_json(v, n); out = []
    for i, o in enumerate(mj.get('object_events') or []):
        if o['graphics_id'] != 'OBJ_EVENT_GFX_ITEM_BALL': continue
        it = items[o['script']]
        uid = int(o['local_id']) if str(o.get('local_id', '')).isdigit() else i + 1
        out.append(dict(kind='npc', map=mapname(n), at=[o['x'], o['y']], uid=uid, model=110, script=it['script'],
                        flag=it['flag'], dir=1,
                        what=f"item ball {it['item']} (Sapphire object {uid}; data/{'emerald/' if v == 'em' else ''}hoenn_items.json n {it['n']})"))
    return out

P2_HEAD = '''// Route110_TrickHousePuzzle2 (zone {zone}; GENERATED by b2tools/trick_house.py: edit the generator; notes/TRICK_HOUSE.md).
// Sapphire/Ruby data/maps/Route110_TrickHousePuzzle2/scripts.inc; Emerald's is the same script on its own maze. Four
// floor buttons (triggers while map-local work 0x4001-0x4004, Gen 3's VAR_TEMP_1-4, is 0), each closes one hole: the
// hole is a flat object (code {hole}, uid 21-24, spawn flag = map-local flag 0x20-0x23: back on every entry, as
// OnTransition resets VAR_TEMP_1-4) lying over the room's lid art (Door_Shuttered). The scroll, the door (13,1), the
// trainers, the holes and the buttons are in data/story/trick_house.json (Emerald: data/story/emerald/trick_house.json).
// Map scripts: {init:04d}_room_Route110_TrickHousePuzzle2_init.s. Room tiles = Sapphire + (1, 1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"
#include "scenes/trick_house_lib.inc"

    ScriptEntry TH_P2_Scroll            // 1: the scroll
    ScriptEntry TH_P2_Door              // 2: the door (13,1)
    ScriptEntry TH_P2_Init              // 3: zone init
    ScriptEntry TH_P2_Button1           // 4-7: the buttons
    ScriptEntry TH_P2_Button2
    ScriptEntry TH_P2_Button3
    ScriptEntry TH_P2_Button4
    ScriptEntriesEnd
{defines}
#define TH_DOOR_WARP 2                   // the door's warp: Sapphire warp 2 (13,1), third in data/interiors/{zone}.json

TH_P2_Init:                              // the door is open once the code is written (VAR_..._2_STATE 2)
    th_door_init VAR_TRICK_HOUSE_PUZZLE_2_STATE, TH_DOOR_WARP
    VMHalt
TH_P2_Scroll:                            // Route110_TrickHousePuzzle2_EventScript_Scroll
    th_scroll VAR_TRICK_HOUSE_PUZZLE_2_STATE, T_FoundScroll, T_Memorized, T_CodeOnIt
TH_P2_Door:                              // Route110_TrickHousePuzzle_EventScript_Door (puzzle 2)
    th_door VAR_TRICK_HOUSE_PUZZLE_2_STATE, T_Wrote, T_Locked, TH_DOOR_WARP
{buttons}
    .balign 4, 0
'''

def puzzle2():
    L = Lines(); puzzle_common(L, 2)
    btn = '\n'.join(f'TH_P2_Button{k}:                         // Route110_TrickHousePuzzle2_EventScript_Button{k}\n'
                    f'    th_button {0x4000 + k:#06x}, {20 + k}, {0x1F + k:#04x}' for k in range(1, 5))
    sc, ini, tx = files_of(2)
    story = P2_HEAD.format(zone=ZONES[2], hole=HOLE_MODEL, init=ini, defines=L.defines(), buttons=btn)
    init = (f'// Map scripts of Route110_TrickHousePuzzle2 (zone {ZONES[2]}; GENERATED by b2tools/trick_house.py): zone init 3.\n'
            '#include "asm/field_script.inc"\n\n    MapScript 2, 3\n    MapScriptsEnd\n    .balign 4, 0\n')
    return L, story, init

def puzzle2_objects(v):
    out = []
    for k, (b, h) in enumerate(p2_buttons(v), 1):
        out.append(dict(kind='npc', map=mapname(2), at=list(h), uid=20 + k, model=HOLE_MODEL, script=0, dir=1, flag=0x1F + k,
                        what=f'hole {k} (setmetatile {h} Door_Shuttered by button {k} at {b}): map-local flag {0x1F + k:#04x}'))
        out.append(dict(kind='trigger', map=mapname(2), at=list(b), w=1, h=1, script=3 + k, var=0x4000 + k, value=0,
                        what=f'button {k} (VAR_TEMP_{k} = map-local work {0x4000 + k:#06x})'))
    return out + item_balls(v, 2)

SIMPLE_HEAD = '''// Route110_TrickHousePuzzle{n} (zone {zone}; GENERATED by b2tools/trick_house.py: edit the generator; notes/TRICK_HOUSE.md).
// Sapphire/Ruby data/maps/Route110_TrickHousePuzzle{n}/scripts.inc; Emerald's is the same script on its own maze. {what}
// The scroll, the door (13,1), the trainers and the rest are in data/story/trick_house.json (Emerald:
// data/story/emerald/trick_house.json). Map scripts: {init:04d}_room_Route110_TrickHousePuzzle{n}_init.s. Room tiles =
// Sapphire + (1, 1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"
#include "scenes/trick_house_lib.inc"

    ScriptEntry TH_P{n}_Scroll            // 1: the scroll
    ScriptEntry TH_P{n}_Door              // 2: the door (13,1)
    ScriptEntry TH_P{n}_Init              // 3: zone init
    ScriptEntriesEnd
{defines}
#define TH_DOOR_WARP 2                   // the door's warp: Sapphire warp 2 (13,1), third in data/interiors/{zone}.json

TH_P{n}_Init:                              // the door is open once the code is written (VAR_..._{n}_STATE 2)
    th_door_init VAR_TRICK_HOUSE_PUZZLE_{n}_STATE, TH_DOOR_WARP
    VMHalt
TH_P{n}_Scroll:                            // Route110_TrickHousePuzzle{n}_EventScript_Scroll
    th_scroll VAR_TRICK_HOUSE_PUZZLE_{n}_STATE, T_FoundScroll, T_Memorized, T_CodeOnIt
TH_P{n}_Door:                              // Route110_TrickHousePuzzle_EventScript_Door (puzzle {n})
    th_door VAR_TRICK_HOUSE_PUZZLE_{n}_STATE, T_Wrote, T_Locked, TH_DOOR_WARP
    .balign 4, 0
'''

SIMPLE_WHAT = {4: "Strength boulders (Black 2's Strength on the Hoenn 1x1 boulder, code 0x2004, global 10000: each "
                  'is back on every entry, as Gen 3 resets them).',
               6: "The rotating gates (rotating_gate.c) are field code: b2tools/patches/rotating_gates.c (walking into "
                  "an arm turns the gate or bumps; each arm a 3D actor, uid 100 + 4 * gate + arm, codes 119/135; the "
                  "turns in map-local works 0x4000 + gate, reset at every zone init as Gen 3's OnTransition).",
               8: "The slippery floor (MB_TRICK_HOUSE_PUZZLE_8_FLOOR, Gen 3 slips you on as on ice) is Black 2's "
                  'sliding ice (cells class 0x18 from the room recipe). Needs the game cleared (the entrance checks).'}

def simple_puzzle(n):
    """A puzzle room whose mechanics are all objects Black 2 has (puzzle 4's boulders): scroll, door, zone init."""
    L = Lines(); puzzle_common(L, n)
    sc, ini, tx = files_of(n)
    story = SIMPLE_HEAD.format(n=n, zone=ZONES[n], what=SIMPLE_WHAT[n], init=ini, defines=L.defines())
    init = (f'// Map scripts of Route110_TrickHousePuzzle{n} (zone {ZONES[n]}; GENERATED by b2tools/trick_house.py): zone init 3.\n'
            '#include "asm/field_script.inc"\n\n    MapScript 2, 3\n    MapScriptsEnd\n    .balign 4, 0\n')
    return L, story, init

def puzzle2_recipe(v):
    pairs = p2_buttons(v)
    ft = [gen3_floor(v, b, what=f'button {k} (Button_Up)') for k, (b, h) in enumerate(pairs, 1)]
    ft += [gen3_floor(v, h, MT_SHUTTERED, what=f'hole {k} closed (Door_Shuttered): the hole object lies over it until button {k}')
           for k, (b, h) in enumerate(pairs, 1)]
    return puzzle_recipe(v, 2, ft, [h for b, h in pairs],
                         'The four holes (dark doorways, solid in Sapphire) are walkable floor drawn with the lid '
                         '(Door_Shuttered) under a flat hole object (story objects, code 142) that button k removes; the '
                         "buttons are Sapphire's Button_Up art on the floor.")

def hole_object():
    """src/objects3d/008e-trick-hole: Gen 3's hole metatile (0x269, the same in both decomps) on a flat quad 2 units over
    the floor (Black 2's rug spacing: 1 unit flickers in melonDS, notes/INTERIORS.md "Flicker"; th_check67), one tile;
    3D record copied from 0x2009 with collision 1x1 (it blocks, as the solid Gen 3 tile)."""
    import models_objects as MO
    from dae import Model
    from gba import Repo, MetatileRenderer
    import numpy as np
    r = Repo(RS)
    g, lay = r.layout_grid(r.map_json(mapname(2))['layout'])
    mr = MetatileRenderer(r, lay['primary_tileset'], lay['secondary_tileset'])
    px = np.asarray(mr.render(MT_HOLE), dtype=np.uint8).copy()
    px[..., 3] = 255
    m = Model('trickhole')
    m.quad('trickhole', [(-8, 2, -8, 0, 1), (-8, 2, 8, 0, 0), (8, 2, 8, 1, 0), (8, 2, -8, 1, 1)])
    mdl = MO.to_mdl0(m, {'trickhole': px})
    bmd = MO.bmd0(mdl, MO.tex0_block([('trickhole', px, 3)]))
    meta = dict(code=HOLE_MODEL, name='trick-hole',
                what='the holes of Trick House puzzle 2 (Gen 3 metatile 0x269, solid until a button covers it with '
                     "Door_Shuttered): Sapphire's art flat on the floor, one tile (b2tools/trick_house.py)",
                record_from=0x2009, record={'collWidth': 1, 'collHeight': 1, 'offX': 0, 'offY': 0, 'offZ': 0},
                made_by='b2tools/trick_house.py')
    return bmd, px, meta

# ---------------------------------------------------------------------------------------------------- puzzle 3
ZONE_P3 = {0: ZONES[3], 1: ZONE_P3_ALT}       # door state 0 (blue open, red shut) / 1 (blue shut, red open)
P3_ROOM = {0: mapname(3), 1: mapname(3) + '_Alt'}

def metatile_ids(v):
    src = open(os.path.join(RS if v == 'rs' else EM, 'include', 'constants', 'metatile_labels.h')).read()
    return {k: int(x, 16) for k, x in re.findall(r'#define\s+(METATILE_\w+)\s+0x([0-9A-Fa-f]+)', src)}

def p3_states(v):
    """{0: {(x, y): (metatile, solid)}, 1: {...}}: SetDoorsState0 / SetDoorsState1 (setmetatile x, y, M, collision)."""
    src = scripts_inc(v, 3); ids = metatile_ids(v); out = {}
    for st in (0, 1):
        body = re.search(rf'Route110_TrickHousePuzzle3_EventScript_SetDoorsState{st}::(.*?)return', src, re.S).group(1)
        out[st] = {(int(x), int(y)): (ids[m], c in ('1', 'TRUE'))
                   for x, y, m, c in re.findall(r'setmetatile (\d+), (\d+), (METATILE_\w+), (\w+)', body)}
    return out

def p3_buttons(v):
    """[(k, (x, y))]: the button triggers (VAR_TEMP_k == 0 -> Route110_TrickHousePuzzle3_EventScript_Buttonk)."""
    mj = map_json(v, 3)
    return sorted((int(c['script'].rsplit('Button', 1)[1]), (c['x'], c['y'])) for c in mj['coord_events']
                  if 'EventScript_Button' in c.get('script', ''))

def p3_rocks(v):
    """[(uid, (x, y), button k or None)]: the breakable rocks (FLAG_TEMP_*), and the button each one covers."""
    mj = map_json(v, 3); btn = {at: k for k, at in p3_buttons(v)}; out = []
    for i, o in enumerate(mj.get('object_events') or []):
        if o['graphics_id'] == 'OBJ_EVENT_GFX_BREAKABLE_ROCK':
            uid = int(o['local_id']) if str(o.get('local_id', '')).isdigit() else i + 1
            out.append((uid, (o['x'], o['y']), btn.get((o['x'], o['y']))))
    return out

def puzzle3_recipe(v, st):
    """Puzzle 3 in door state st: every door tile drawn with Gen 3's art of that state (setmetatile simulated as
    SetDoorsState<st> does): a shut door part (collision set) a raised panel (16 high) with the art on top and in
    front, an open one the art on the floor; collision follows the state (block / unblock against Sapphire's map)."""
    import models_interior as mi
    m = ('pokeemerald/' if v == 'em' else '') + mapname(3)
    sm = mi.sapphire_map(m)
    states = p3_states(v); tiles = set(states[0]) | set(states[1])
    ft, blocks, block, unblock = [], [], [], []
    for k, at in p3_buttons(v):
        ft.append(gen3_floor(v, at, what=f'button {k} (Button_Up)'))
    for (x, y) in sorted(tiles):
        mt, solid = states[st].get((x, y), states[1 - st].get((x, y)))
        name = f'th{v[0]}{mt:03x}'
        if solid:
            src = ['gen3', m, x, y, mt]
            blocks.append({'h': 16, 'top': {'tex': name, 'src': src, 'size': 16},
                           'side': {'tex': name, 'src': src, 'u_size': 16, 'v': [0, 1]}, 'shade_top': 1.0,
                           'tiles': [[x, y]], '_what': f'door part {mt:#x} shut (state {st})'})
            if sm['walk'][y][x]: block.append([x, y])
        else:
            ft.append(gen3_floor(v, (x, y), mt, what=f'door part {mt:#x} open (state {st})'))
            if not sm['walk'][y][x]: unblock.append([x, y])
    r = puzzle_recipe(v, 3, ft, [tuple(t) for t in unblock] + [tuple(t) for t in block],
                      f'Door state {st} ({"blue shut, red open" if st else "blue open, red shut"}; '
                      + (f'zone {ZONE_P3_ALT}, a copy of zone {ZONES[3]}' if st else f'zone {ZONES[3]}') + '): '
                      f'every door tile drawn as SetDoorsState{st} leaves it (Gen 3 art: shut parts raised panels, open '
                      'parts on the floor); a button press swaps to the other zone at the same tile.')
    r['blocks'][0]['tiles'] = [t for t in r['blocks'][0]['tiles'] if tuple(t) not in tiles]
    r['blocks'] = r['blocks'] + blocks
    if unblock: r['unblock'] = unblock
    else: r.pop('unblock', None)
    if block: r['block'] = block
    return r

P3_HEAD = '''// Route110_TrickHousePuzzle3 (zones {za} and {zb}; GENERATED by b2tools/trick_house.py: edit the generator;
// notes/TRICK_HOUSE.md). Sapphire/Ruby data/maps/Route110_TrickHousePuzzle3/scripts.inc; Emerald's is the same script on
// its own maze (4 buttons, no rocks on them). Every button toggles all the red and blue doors (AlternateDoors). Black 2
// cannot change a room's collision in place and its ten map replacements are taken, so the room exists twice: zone {za}
// (VAR_TRICK_HOUSE_PUZZLE_3_DOORS 0: blue open, red shut; SetDoorsState0) and zone {zb} (1: SetDoorsState1), a copy of
// {za}'s header (data/interiors/{za}.json "variants": same people, scripts and lines) with the other room; a button fades
// and changes zone at the player's tile, facing as before (the Mauville Gym's barriers' way). The state the swap must
// keep is saved: VAR_TRICK_HOUSE_PUZZLE_3_BUTTON (SetButton: the pressed button's trigger stays off, Gen 3's
// VAR_TEMP_1-7 are rebuilt by the zone init) and the rocks over buttons (FLAG_TRICK_HOUSE_PUZZLE_3_ROCK_*: set when
// you press the button under one). The entrance scroll resets them (OnTransition). The pressed button's own art
// (VAR_TEMP_8) is not drawn. Room tiles = Sapphire + (1, 1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"
#include "scenes/trick_house_lib.inc"

    ScriptEntry TH_P3_Scroll            // 1: the scroll
    ScriptEntry TH_P3_Door              // 2: the door (13,1)
    ScriptEntry TH_P3_Init              // 3: zone init
{entries}
    ScriptEntriesEnd
{defines}
#define TH_DOOR_WARP 2                   // the door's warp: Sapphire warp 2 (13,1), third in data/interiors/{za}.json

    .macro th_p3_swap zone, x, z         // fade, then the other door state's zone at this tile (zone tiles), same facing
    PlayerGetDir TH_TMP
    FadeOutBlack
    RTReserveScript 10017                // the global arrival script fades back in (hm_free.py Script_18)
    FadeWait
    h_goto_if_ne TH_TMP, 0, .Lp3s1\\@
    MapChangeCore \\zone, \\x, 0, \\z, 0
    h_release
.Lp3s1\\@:
    h_goto_if_ne TH_TMP, 1, .Lp3s2\\@
    MapChangeCore \\zone, \\x, 0, \\z, 1
    h_release
.Lp3s2\\@:
    h_goto_if_ne TH_TMP, 2, .Lp3s3\\@
    MapChangeCore \\zone, \\x, 0, \\z, 2
    h_release
.Lp3s3\\@:
    MapChangeCore \\zone, \\x, 0, \\z, 3
    h_release
    .endm

TH_P3_Init:                              // zone init: the door; the buttons' triggers (Gen 3's VAR_TEMP_1-7) from the
    th_door_init VAR_TRICK_HOUSE_PUZZLE_3_STATE, TH_DOOR_WARP     // saved pressed button
{init}
    VMHalt
TH_P3_Scroll:                            // Route110_TrickHousePuzzle3_EventScript_Scroll
    th_scroll VAR_TRICK_HOUSE_PUZZLE_3_STATE, T_FoundScroll, T_Memorized, T_CodeOnIt
TH_P3_Door:                              // Route110_TrickHousePuzzle_EventScript_Door (puzzle 3)
    th_door VAR_TRICK_HOUSE_PUZZLE_3_STATE, T_Wrote, T_Locked, TH_DOOR_WARP
{buttons}
    .balign 4, 0
'''

def puzzle3():
    """One script file for both versions: the buttons differ (7 in Sapphire, 4 in Emerald): #ifdef HOENN_EMERALD."""
    L = Lines(); puzzle_common(L, 3)
    per = {}
    for v in ('rs', 'em'):
        rocks = {r[2]: j for j, r in enumerate([r for r in p3_rocks(v) if r[2]], 1)}
        bl, il = [], []
        for k, (x, y) in p3_buttons(v):
            zx, zz = zt(x, y)
            rock = (f'    h_setflag FLAG_TRICK_HOUSE_PUZZLE_3_ROCK_{rocks[k]}    // the rock that covered it stays smashed\n'
                    if k in rocks else '')
            bl.append(f'''TH_P3_Button{k}:                         // Route110_TrickHousePuzzle3_EventScript_Button{k} ({x},{y})
    h_lock
    h_setvar VAR_TRICK_HOUSE_PUZZLE_3_BUTTON, {k}         // SetButton
    SEPlay TH_SE_PIN
{rock}    h_goto_if_eq VAR_TRICK_HOUSE_PUZZLE_3_DOORS, 1, L_TH_P3_ToState0_{k}
    h_setvar VAR_TRICK_HOUSE_PUZZLE_3_DOORS, 1            // AlternateDoors: SetDoorsState1
    th_p3_swap TH_ZONE_P3_ALT, {zx}, {zz}
L_TH_P3_ToState0_{k}:
    h_setvar VAR_TRICK_HOUSE_PUZZLE_3_DOORS, 0            // SetDoorsState0
    th_p3_swap TH_ZONE_P3, {zx}, {zz}''')
            il.append(f'    h_goto_if_ne VAR_TRICK_HOUSE_PUZZLE_3_BUTTON, {k}, L_TH_P3_Init{k}\n    h_setvar {0x4000 + k:#06x}, 1\nL_TH_P3_Init{k}:')
        per[v] = (bl, il, [k for k, _ in p3_buttons(v)])
    def ifdef(rs, em):
        return '#ifdef HOENN_EMERALD\n' + em + '\n#else\n' + rs + '\n#endif'
    ent = {v: '\n'.join(f'    ScriptEntry TH_P3_Button{k}           // {3 + k}: button {k}' for k in per[v][2]) for v in per}
    story = P3_HEAD.format(za=ZONES[3], zb=ZONE_P3_ALT, defines=L.defines(), entries=ifdef(ent['rs'], ent['em']),
                           init=ifdef('\n'.join(per['rs'][1]), '\n'.join(per['em'][1])),
                           buttons=ifdef('\n'.join(per['rs'][0]), '\n'.join(per['em'][0])))
    init = (f'// Map scripts of Route110_TrickHousePuzzle3 (zones {ZONES[3]} and {ZONE_P3_ALT}: one entity file; GENERATED by '
            'b2tools/trick_house.py): zone init 3.\n#include "asm/field_script.inc"\n\n    MapScript 2, 3\n    MapScriptsEnd\n'
            '    .balign 4, 0\n')
    return L, story, init

def puzzle3_objects(v):
    out = []
    for k, at in p3_buttons(v):
        out.append(dict(kind='trigger', map=mapname(3), at=list(at), w=1, h=1, script=3 + k, var=0x4000 + k, value=0,
                        what=f'button {k} (VAR_TEMP_{k} = map-local work {0x4000 + k:#06x}; the zone init sets the pressed one)'))
    j = 0
    for uid, at, k in p3_rocks(v):
        flag = 0
        if k: j += 1; flag = f'FLAG_TRICK_HOUSE_PUZZLE_3_ROCK_{j}'
        out.append(dict(kind='npc', map=mapname(3), at=list(at), uid=uid, model=sprite(v, 'OBJ_EVENT_GFX_BREAKABLE_ROCK'),
                        script=10016, dir=1, flag=flag,
                        what=f'breakable rock (Sapphire object {uid}, FLAG_TEMP_*; global 10016)' +
                             (f': on button {k}, smashed for good once the button is pressed' if k else '')))
    return out + item_balls(v, 3)

# ---------------------------------------------------------------------------------------------------- puzzle 5
def _rs_string(sym):
    """A pokeruby C string constant (src/strings.c; the first definition is the English one)."""
    src = open(os.path.join(RS, 'src', 'strings.c'), encoding='utf-8', errors='replace').read()
    m = re.search(rf'const u8 {sym}\[\] = _\("(.*?)"\);', src)
    assert m, sym
    return convert(m.group(1), expand=True, version_='sapphire')[0]

def multichoice_options(v, mc):
    """The option lines of a multichoice list (pokeruby: list number, src/script_menu.c MultichoiceList_N; pokeemerald:
    MULTI_* name, src/data/script_menu.h)."""
    if v == 'rs':
        src = open(os.path.join(RS, 'src', 'script_menu.c')).read()
        body = re.search(rf'MultichoiceList_{int(mc):02d}\[\] =\s*\{{(.*?)\}};', src, re.S).group(1)
        return [_rs_string(s) for s in re.findall(r'\{(\w+), NULL\}', body)]
    src = open(os.path.join(EM, 'src', 'data', 'script_menu.h')).read()
    lst = re.search(rf'\[{mc}\]\s*=\s*MULTICHOICE\((\w+)\)', src).group(1)
    body = re.search(rf'{lst}\[\] =\s*\{{(.*?)\}};', src, re.S).group(1)
    return [convert(TEXT['em'][s], expand=True, version_='emerald')[0] for s in re.findall(r'\{(\w+)\}', body)]

def p5_spec(v):
    """[{k, uid, at, triggers [(i, at)], quizzes [(text label, options, correct)]}] of puzzle 5's Mechadolls, and the
    label of the "correct, go through" line."""
    src = scripts_inc(v, 5); mj = map_json(v, 5); out = []
    for i, o in enumerate(mj['object_events']):
        m = re.search(r'Mechadoll(\d)$', o['script'])
        if not m: continue
        k = int(m.group(1))
        uid = int(o['local_id']) if str(o.get('local_id', '')).isdigit() else i + 1
        trig = sorted((int(re.search(r'Trigger(\d)$', c['script']).group(1)), (c['x'], c['y']))
                      for c in mj['coord_events'] if f'Mechadoll{k}Trigger' in c['script'])
        quizzes = []
        for q in (1, 2, 3):
            body = re.search(rf'EventScript_Mechadoll{k}Quiz{q}::(.*?)\bend\b', src, re.S).group(1)
            text = re.search(r'msgbox (\w+)', body).group(1)
            mc = re.search(r'multichoice 0, 0, (\w+)', body).group(1)
            good = int(re.search(r'case (\d+), Route110_TrickHousePuzzle5_EventScript_CorrectAnswer', body).group(1))
            quizzes.append((text, multichoice_options(v, mc), good))
        out.append(dict(k=k, uid=uid, at=(o['x'], o['y']), triggers=trig, quizzes=quizzes))
    correct = re.search(r'EventScript_CorrectGoThrough::.*?msgbox (\w+)', src, re.S).group(1)
    return sorted(out, key=lambda d: d['k']), correct

P5_HEAD = '''// Route110_TrickHousePuzzle5 (zone {zone}; GENERATED by b2tools/trick_house.py: edit the generator; notes/TRICK_HOUSE.md).
// Sapphire/Ruby data/maps/Route110_TrickHousePuzzle5/scripts.inc; Emerald's (pokeemerald) on its own map, more
// triggers and other quizzes: #ifdef HOENN_EMERALD. Five Mechadolls (Gen 3 draws them as MAN_1, the Trick Master's
// look: model {model}, uid = Sapphire's local id). Stepping in front of one (trigger i while its VAR_TEMP_k, map-local
// work 0x400k, is 0) or talking to it: "!", it walks i tiles toward you, its intro, one of its three quizzes at random
// (a Black 2 list menu with Gen 3's three answers). Right: "Go through" (VAR_TEMP_k stays 1). Wrong: every Mechadoll
// shakes, "Wahahahaha!" and you are sent back to the start (0,21), as Gen 3's warp. The scroll, the door, the dolls and
// the triggers are in data/story/trick_house.json (Emerald: data/story/emerald/). Room tiles = Sapphire + (1, 1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"
#include "scenes/trick_house_lib.inc"

    ScriptEntry TH_P5_Scroll            // 1: the scroll
    ScriptEntry TH_P5_Door              // 2: the door (13,1)
    ScriptEntry TH_P5_Init              // 3: zone init
{entries}
    ScriptEntriesEnd
{defines}
#define TH_DOOR_WARP 2                   // the door's warp: Sapphire warp 2 (13,1), third in data/interiors/{zone}.json
#define TH_P5_DOLL 0x8033                // scratch: the Mechadoll asking (uid)
#define TH_SE_SUCCESS SEQ_SE_DECIDE2     // SE_SUCCESS [guess]
#define TH_SE_FAILURE SEQ_SE_BEEP        // SE_FAILURE [guess]

TH_P5_Init:                              // the door is open once the code is written (VAR_..._5_STATE 2)
    th_door_init VAR_TRICK_HOUSE_PUZZLE_5_STATE, TH_DOOR_WARP
    VMHalt
TH_P5_Scroll:                            // Route110_TrickHousePuzzle5_EventScript_Scroll
    th_scroll VAR_TRICK_HOUSE_PUZZLE_5_STATE, T_FoundScroll, T_Memorized, T_CodeOnIt
TH_P5_Door:                              // Route110_TrickHousePuzzle_EventScript_Door (puzzle 5)
    th_door VAR_TRICK_HOUSE_PUZZLE_5_STATE, T_Wrote, T_Locked, TH_DOOR_WARP
{body}
L_TH_P5_Correct:                         // CorrectAnswer: SE_SUCCESS, CorrectGoThrough
    SEPlay TH_SE_SUCCESS
L_TH_P5_GoThrough:
    ActorMsg MSGFILE_SCRIPT, T_GoThrough, TH_P5_DOLL, 0, 0
    LastKeyWait
    h_release
L_TH_P5_Wrong:                           // IncorrectAnswer
    SEPlay TH_SE_FAILURE
    ActorMsg MSGFILE_SCRIPT, T_Disappointment, TH_P5_DOLL, 0, 0
    LastKeyWait
{shake}
    ActorMsg MSGFILE_SCRIPT, T_Wahaha, TH_P5_DOLL, 0, 0
    LastKeyWait
    ActorCmdWait
    h_closemessage
    ActorMsg MSGFILE_SCRIPT, T_WaitNext, TH_P5_DOLL, 0, 0
    LastKeyWait
    h_closemessage
    h_warp_arrive TH_ZONE_P5, {sx}, {sz}, 0              // warp MAP_ROUTE110_TRICK_HOUSE_PUZZLE5, 0, 21
    h_release

    th_moves
    .balign 4, 0
Mv_TH_P5_Shake:                          // Movement_MechadollShake
{shake_moves}
    step_end
{walks}
'''

def puzzle5():
    L = Lines(); puzzle_common(L, 5)
    specs = {v: p5_spec(v) for v in ('rs', 'em')}
    # lines: the same names in both versions where both have them (the dolls 1-5, quizzes 1-3)
    L.add('T_GoThrough', specs['rs'][1], specs['em'][1])
    L.add('T_Disappointment', 'Route110_TrickHousePuzzle5_Text_DisappointmentError')
    L.add('T_Wahaha', 'Route110_TrickHousePuzzle5_Text_Wahahahaha')
    L.add('T_WaitNext', 'Route110_TrickHousePuzzle5_Text_WaitForNextChallenge')
    for k in range(1, 6):
        L.add(f'T_Intro{k}', f'Route110_TrickHousePuzzle5_Text_Mechadoll{k}Intro')
        for q in range(1, 4):
            L.add(f'T_Quiz{k}_{q}', specs['rs'][0][k - 1]['quizzes'][q - 1][0], specs['em'][0][k - 1]['quizzes'][q - 1][0])
            for a in range(3):
                L.names[f'T_Ans{k}_{q}_{a}'] = len(L.rows)       # the answers: strings, not labels
                L.rows.append((specs['rs'][0][k - 1]['quizzes'][q - 1][1][a], specs['em'][0][k - 1]['quizzes'][q - 1][1][a]))
    def body(v):
        dolls, _ = specs[v]; parts = []; entries = []; n = 4
        for d in dolls:
            k, uid = d['k'], d['uid']
            entries.append(f'    ScriptEntry TH_P5_Doll{k}           // {n}: Mechadoll {k} (talked to)'); n += 1
            for i, at in d['triggers']:
                entries.append(f'    ScriptEntry TH_P5_Doll{k}T{i}         // {n}: Mechadoll {k} trigger {i} {at}'); n += 1
            way = 'L' if d['triggers'][0][1][0] < d['at'][0] else 'R'
            parts.append(f'''TH_P5_Doll{k}:                           // Route110_TrickHousePuzzle5_EventScript_Mechadoll{k}
    h_lock
    h_setvar TH_P5_DOLL, {uid}
    ActorSetEyeToEye                     // Common_Movement_FacePlayer
    h_goto_if_eq {0x4000 + k:#06x}, 1, L_TH_P5_GoThrough
    h_setvar TH_TMP, 0
    VMJump L_TH_P5_Activate{k}''')
            for i, at in d['triggers']:
                parts.append(f'''TH_P5_Doll{k}T{i}:                         // Mechadoll{k}Trigger{i}
    h_lock
    h_setvar TH_P5_DOLL, {uid}
    h_setvar TH_TMP, {i}
    VMJump L_TH_P5_Activate{k}''')
            walks = '\n'.join(f'    h_call_if_eq TH_TMP, {s}, L_TH_P5_Walk{k}_{s}' for s in range(1, len(d['triggers'])))
            subs = '\n'.join(f'L_TH_P5_Walk{k}_{s}:\n    ActorCmdExec {uid}, Mv_TH_P5_{way}{s}\n    ActorCmdWait\n    VMReturn'
                             for s in range(1, len(d['triggers'])))
            quiz = []
            for q in range(1, 4):
                good = d['quizzes'][q - 1][2]
                opts = '\n'.join(f'    ListMenuAdd T_Ans{k}_{q}_{a}, 65535, {a}' for a in range(3))
                quiz.append(f'''L_TH_P5_Quiz{k}_{q}:                       // Mechadoll{k}Quiz{q}: multichoice, the answer {good}
    ActorMsg MSGFILE_SCRIPT, T_Quiz{k}_{q}, {uid}, 0, 0
    LastKeyWait
    ListMenu_AnchorTopRight 31, 7, 0, 0, TH_TMP
{opts}
    ListMenuShow
    h_closemessage
    h_goto_if_eq TH_TMP, {good}, L_TH_P5_Correct
    VMJump L_TH_P5_Wrong''')
            parts.append(f'''L_TH_P5_Activate{k}:                      // Mechadoll{k}Activate
    h_setvar {0x4000 + k:#06x}, 1
    SEPlay TH_SE_PIN
    ActorCmdExec {uid}, Mv_TH_Exclaim
    ActorCmdWait
    ActorCmdExec {uid}, Mv_TH_Delay48
    ActorCmdWait
{walks}
    ActorMsg MSGFILE_SCRIPT, T_Intro{k}, {uid}, 0, 0
    LastKeyWait
    h_random TH_TMP, 3
    h_goto_if_eq TH_TMP, 0, L_TH_P5_Quiz{k}_1
    h_goto_if_eq TH_TMP, 1, L_TH_P5_Quiz{k}_2
    VMJump L_TH_P5_Quiz{k}_3
{subs}
''' + '\n'.join(quiz))
        shake = '\n'.join(f'    ActorCmdExec {d["uid"]}, Mv_TH_P5_Shake' for d in dolls)
        return '\n'.join(entries), '\n'.join(parts), shake
    eb = {v: body(v) for v in specs}
    def ifdef(rs, em): return '#ifdef HOENN_EMERALD\n' + em + '\n#else\n' + rs + '\n#endif'
    walks = '\n'.join(f'    .balign 4, 0\nMv_TH_P5_{w}{s}:\n    walk_{"left" if w == "L" else "right"} {s}\n    step_end'
                      for w in 'LR' for s in range(1, 6))
    shake_moves = '\n'.join(('    face_left\n    delay_2\n    face_right\n    delay_2',) * 6)
    sx, sz = zt(0, 21)
    sc, ini, tx = files_of(5)
    story = P5_HEAD.format(zone=ZONES[5], model=sprite('rs', 'OBJ_EVENT_GFX_MAN_1'), defines=L.defines(),
                           entries=ifdef(eb['rs'][0], eb['em'][0]), body=ifdef(eb['rs'][1], eb['em'][1]),
                           shake=ifdef(eb['rs'][2], eb['em'][2]), shake_moves=shake_moves, walks=walks, sx=sx, sz=sz)
    init = (f'// Map scripts of Route110_TrickHousePuzzle5 (zone {ZONES[5]}; GENERATED by b2tools/trick_house.py): zone init 3.\n'
            '#include "asm/field_script.inc"\n\n    MapScript 2, 3\n    MapScriptsEnd\n    .balign 4, 0\n')
    return L, story, init

def puzzle5_objects(v):
    dolls, _ = p5_spec(v); out = []; n = 4
    mj = map_json(v, 5)
    for d in dolls:
        o = next(o for o in mj['object_events'] if o['script'].endswith(f'Mechadoll{d["k"]}'))
        mv = move_codes.npc(o['movement_type'], (0, 0), o['graphics_id'])
        out.append(dict(kind='npc', map=mapname(5), at=list(d['at']), uid=d['uid'], model=sprite(v, 'OBJ_EVENT_GFX_MAN_1'),
                        script=n, dir=mv.get('dir', 1), move=mv['move'],
                        what=f'Mechadoll {d["k"]} (Sapphire object {d["uid"]}, MAN_1, {o["movement_type"][14:]})'))
        n += 1
        for i, at in d['triggers']:
            out.append(dict(kind='trigger', map=mapname(5), at=list(at), w=1, h=1, script=n, var=0x4000 + d['k'], value=0,
                            what=f'Mechadoll {d["k"]} trigger {i} (VAR_TEMP_{d["k"]} = map-local work {0x4000 + d["k"]:#06x})'))
            n += 1
    return out + item_balls(v, 5)

def puzzle5_recipe(v):
    """Puzzle 5's walkways float over Gen 3's dark void: floor = the walkable tiles (+ the scroll's table and the door),
    no walls inside the room (open: black lips, as Black 2's League walkways), no plank boxes."""
    import models_interior as mi
    base = json.load(open(os.path.join(LAYOUTS, 'Route110_TrickHousePuzzle1.json')))
    m = ('pokeemerald/' if v == 'em' else '') + mapname(5)
    sm = mi.sapphire_map(m)
    sc = scroll_at(v, 5)
    fl = {(x, z) for z in range(2, sm['h']) for x in range(sm['w']) if sm['walk'][z][x]} | {sc}
    rects = []
    for z in range(2, sm['h']):
        x = 0
        while x < sm['w']:
            if (x, z) not in fl: x += 1; continue
            x1 = x
            while (x1 + 1, z) in fl: x1 += 1
            rects.append([x, z, x1, z]); x = x1 + 1
    door = next(f for f in base['furniture'] if f['m'] == 'cabin_door')
    return {'_doc': (f"Trick House puzzle room 5 ({'Emerald (pokeemerald)' if v == 'em' else 'Sapphire/Ruby (pokeruby)'}'s map, "
                     f"zone {ZONES[5]}): GENERATED by b2tools/trick_house.py. The walkways over Gen 3's dark void: floor = "
                     "the walkable tiles, the scroll's table and the door; open (no walls) in rows 2-21: black lips, as "
                     "Black 2's League walkways; puzzle 1's floor, back wall, door and mat."),
            'map': m, 'style': base['style'], 'floor': rects + [[13, 1, 13, 1]], 'mats': base['mats'],
            'open': [[0, 2, 14, 21]],
            # (th_glitch 2026-10-19) Gen 3's back wall (rows 0-1) runs the whole width, also above the void in row 2:
            # the floor strip in front of the wall (12 units, 3 past the side columns) across the room keeps the back
            # wall whole (it stood only behind row 2's walkways: black gaps in it, rooms_check (p) at Sapphire (10, 0))
            'floor_extra': [[-3 / 16, 2 - 12 / 16, 15 + 3 / 16, 2]],
            # (th_glitch) and no back-wall floor strip from a walkway into the void north of it (open_no_strip)
            'open_no_strip': True,
            'furniture': [door, dict(m='desk02', tile=list(sc), _what=f'the scroll {sc}: a one-tile table')]}

# ---------------------------------------------------------------------------------------------------- puzzle 6
# (th_p6 2026-10-19) The rotating gates: b2tools/patches/rotating_gates.py/.c (field code: the move check and the arms'
# drawing) reads the gates from the decomp; here every arm becomes a 3D actor standing on a walkable tile next to its
# gate's pivot (the code puts the model's origin on the pivot, a tile corner, and turns it).
def _gates():
    sys.path.insert(0, os.path.join(HERE, 'patches'))
    import rotating_gates
    return rotating_gates

def puzzle6_objects(v):
    rg = _gates(); gates = rg.gates(v)
    import models_interior as mi
    sm = mi.sapphire_map(('pokeemerald/' if v == 'em' else '') + mapname(6))
    out = []
    for g, arm, long in rg.arms(v):
        x, y, sh, o = gates[g]
        at = next(t for t in ((x, y), (x - 1, y), (x, y - 1), (x - 1, y - 1)) if sm['walk'][t[1]][t[0]])
        out.append(dict(kind='npc', map=mapname(6), at=list(at), uid=rg.GATE_UID0 + 4 * g + arm,
                        model=rg.GATE_CODE_LONG if long else rg.GATE_CODE_SHORT, script=0, dir=1, flag=0,
                        what=f"gate {g} ({rg.SHAPES[sh]} at Gen 3 ({x},{y}), turned {90 * o}): its {'NESW'[arm]} arm "
                             f"({'long' if long else 'short'}), standing on {at}"))
    return out + item_balls(v, 6)

# ---------------------------------------------------------------------------------------------------- puzzle 7
# (th_p7 2026-10-19) Sapphire/Ruby (pokeruby): arrow floors and 5 levers. Gen 3 moves you on by itself on an arrow
# (field_player_avatar.c ForcedMovement_*): the red ones (MB_WALK_*) walk you on, the blue ones (MB_SLIDE_*) slide you
# on facing as you were, the two crossings (MB_TRICK_HOUSE_PUZZLE_8_FLOOR) slip you on the way you go, until the next
# tile is blocked or is not an arrow; a raised track (elevation 4, rows 6-7) crosses the room, entered only from its
# elevation-0 ends. Each lever turns one red arrow (SetSwitchNMetatilesOn/Off); the warp pad (9,2) sends you to (3,19),
# the levers kept. Black 2 has no arrow cells, so every arrow you can walk onto is a step trigger whose script moves you
# along the slide Gen 3 makes (worked out here from pokeruby's map, the levers' flags read where a slide crosses a
# lever's arrow), the raised track is solid (Gen 3 bumps you at its edge: elevation; the slides still cross it), and
# a lever's turned arrow is a flat 3D object there while the lever is on (records P7_MODELS: only 4 empty records were
# left, so an arrow you can walk onto is drawn by an object standing on its lever (solid anyway: a Black 2 actor always
# blocks its tile), the others by one shared model on the arrow itself; the levers' lights stay drawn off).
# Emerald (pokeemerald): Mossdeep Gym's rotating tiles (rotating_tile_puzzle.c, initrotatingtilepuzzle TRUE): a colour
# button (step trigger) moves every trainer and statue on that colour's 2x2 arrow square one tile round it and turns
# it a quarter counter-clockwise; ten warp pads (MB_MOSSDEEP_GYM_WARP: the objects stay) in pairs. As
# b2tools/emerald_gyms.py mossdeep: press counts in map-local works (0 on entering, as Emerald resets the objects),
# pads = step triggers moving the player (ActorSetGPos), statues = Black 2's rock 206.
P7_DIRV = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
P7_FORCED = {0x40: ('right', 'walk'), 0x41: ('left', 'walk'), 0x42: ('up', 'walk'), 0x43: ('down', 'walk'),
             0x44: ('right', 'slide'), 0x45: ('left', 'slide'), 0x46: ('up', 'slide'), 0x47: ('down', 'slide'),
             0x48: (None, 'slip')}
P7_MODELS = [145, 146, 202, 203]                        # empty people records (patches/objects3d.py FREE_PEOPLE_RECORDS)
P7_UID0, P7_HIDE0 = 20, 0x1F                            # switch k: object uid 20 + k, hidden by map-local flag 0x1F + k
P7_PLAIN = {0x208, 0x210, 0x211, 0x212}                 # plain floor and the exit mats (the room's own floor)
P7_LEVER_OFF = 0x23E
P7E_BASE, P7E_COLORS = 0x298, ['Yellow', 'Blue', 'Green', 'Purple', 'Red']   # METATILE_TrickHousePuzzle_Arrow_YellowOnWhite_Right
P7E_WORK0 = 0x4011                                      # map-local press counts (as Mossdeep's)
P7_CCW = {3: 0, 1: 3, 2: 1, 0: 2}                       # Black 2 dir (0 up 1 down 2 left 3 right) a quarter counter-clockwise
P7_B2DIR = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}
P7_FACE = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2, 'MOVEMENT_TYPE_FACE_RIGHT': 3}

class _P7Fork(Exception):
    def __init__(self, k): self.k = k

class P7Map:
    """pokeruby's puzzle 7 as Gen 3 moves you on it: collision (solid, elevation, people), forced movement, levers,
    the warp pad. Switch states: a bit mask (bit k-1 = FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_k)."""
    def __init__(self):
        from gba import Repo, MetatileRenderer
        r = Repo(RS); mj = map_json('rs', 7)
        g, lay = r.layout_grid(mj['layout'])
        self.mr = MetatileRenderer(r, lay['primary_tileset'], lay['secondary_tileset'])
        self.H, self.W = g.shape
        self.raw = {(x, y): int(g[y, x]) for y in range(self.H) for x in range(self.W)}
        src = scripts_inc('rs', 7); ids = metatile_ids('rs')
        self.lever, self.arrow, self.arrow_mt = {}, {}, {}
        for k in range(1, 6):
            for st in ('On', 'Off'):
                body = re.search(rf'SetSwitch{k}Metatiles{st}::(.*?)return', src, re.S).group(1)
                for x, y, m, c in re.findall(r'setmetatile (\d+), (\d+), (METATILE_\w+), (\w+)', body):
                    if c in ('1', 'TRUE'): self.lever[k] = (int(x), int(y))
                    else: self.arrow[k] = (int(x), int(y)); self.arrow_mt[(k, st == 'On')] = ids[m]
        self.switch_at = {t: k for k, t in self.arrow.items()}
        self.lever_at = {t: k for k, t in self.lever.items()}
        self.objs = {(o['x'], o['y']) for o in mj['object_events']}
        pad = next(c for c in mj['coord_events'] if c['script'].endswith('_1632A8'))
        self.pad = (pad['x'], pad['y'])
        m = re.search(r'EventScript_1632A8::.*?warpteleport MAP_ROUTE110_TRICK_HOUSE_PUZZLE7, \d+, (\d+), (\d+)', src, re.S)
        self.pad_to = (int(m.group(1)), int(m.group(2)))
        self.scroll = scroll_at('rs', 7)

    def mt(self, t, get):
        k = self.switch_at.get(t)
        return self.arrow_mt[(k, bool(get(k)))] if k else self.raw[t] & 0x3FF
    def beh(self, t, get): return self.mr.behavior(self.mt(t, get))
    def elev(self, t): return (self.raw[t] >> 12) & 0xF
    def solid(self, t): return not (0 <= t[0] < self.W and 0 <= t[1] < self.H) or (self.raw[t] >> 10) & 3 != 0
    def blocked(self, t, e):
        """CheckForObjectEventCollision: outside / solid, another elevation (0 and 15 match all), a person."""
        if self.solid(t): return True
        el = self.elev(t)
        return (e != 0 and el not in (0, 15) and el != e) or t in self.objs
    def new_e(self, prev, cur, e):
        """ObjectEventUpdateElevation: a tile of elevation 15 (here or just left) keeps it."""
        return e if 15 in (self.elev(cur), self.elev(prev)) else self.elev(cur)
    def run(self, t, e, d, get):
        """The player has just stepped onto t (elevation e, moving d): Gen 3's forced movement from there ->
        ([(direction, kind)], end tile, elevation)."""
        steps, seen = [], set()
        while True:
            f = P7_FORCED.get(self.beh(t, get))
            if not f: return steps, t, e
            nd = f[0] or d
            assert (t, nd, e) not in seen, f'puzzle 7: endless slide at {t}'
            seen.add((t, nd, e))
            n = (t[0] + P7_DIRV[nd][0], t[1] + P7_DIRV[nd][1])
            if self.blocked(n, e): return steps, t, e
            e = self.new_e(t, n, e); steps.append((nd, f[1])); t, d = n, nd
    def moves(self, st):
        """[(how, next state)] from a standing state (tile, elevation, switch bits): a step (then the arrows), a
        lever read (BG_EVENT_PLAYER_FACING_ANY), the warp pad."""
        pos, e, fl = st; get = lambda k: fl >> (k - 1) & 1; out = []
        for d, (dx, dy) in P7_DIRV.items():
            n = (pos[0] + dx, pos[1] + dy)
            if n in self.lever_at: out.append((('lever', self.lever_at[n], d), (pos, e, fl ^ 1 << (self.lever_at[n] - 1))))
            if self.blocked(n, e): continue
            e2 = self.new_e(pos, n, e)
            if n == self.pad:
                out.append((('pad', d), (self.pad_to, self.elev(self.pad_to), fl))); continue
            steps, end, e3 = self.run(n, e2, d, get)
            out.append((('step', d, n, tuple(steps)), (end, e3, fl)))
        return out
    def explore(self, start=((0, 21), 3, 0)):
        """Every standing state from the exit mats: {state: (previous state, how)}."""
        from collections import deque
        prev = {start: None}; q = deque([start])
        while q:
            st = q.popleft()
            for how, nxt in self.moves(st):
                if nxt not in prev: prev[nxt] = (st, how); q.append(nxt)
        return prev
    def entries(self, prev=None):
        """{arrow tile: {(direction, elevation)}}: the arrows you can walk onto (from any standing state)."""
        out = {}
        for st in (prev or self.explore()):
            for how, nxt in self.moves(st):
                if how[0] == 'step' and P7_FORCED.get(self.beh(how[2], lambda k: st[2] >> (k - 1) & 1)):
                    out.setdefault(how[2], set()).add((how[1], self.new_e(st[0], how[2], st[1])))
        return out
    def tree(self, t, d, e, assign=()):
        """The slide from arrow t as a decision on the levers it meets: ('go', steps, end) or ('if', k, on, off)."""
        a = dict(assign)
        def get(k):
            if k not in a: raise _P7Fork(k)
            return a[k]
        try: steps, end, _ = self.run(t, e, d, get)
        except _P7Fork as f:
            return ('if', f.k, self.tree(t, d, e, tuple(sorted({**a, f.k: 1}.items()))),
                    self.tree(t, d, e, tuple(sorted({**a, f.k: 0}.items()))))
        return ('go', tuple(steps), end)
    def raised(self):
        """The raised track (elevation 4) and its crossings (15): solid in Black 2."""
        return sorted(t for t in self.raw if not self.solid(t) and self.elev(t) in (4, 15))

def p7_moves(steps):
    """A slide as Black 2 movement actions: red arrows walk (facing the way), blue ones slide (walk_fast with the
    facing locked: ForcedMovement_Slide), the crossings slip (walk_fast, facing the way)."""
    out, locked = [], False
    for (d, kind), n in _runs(steps):
        if kind == 'slide' and not locked: out.append('    lock_facing_direction'); locked = True
        if kind != 'slide' and locked: out.append('    unlock_facing_direction'); locked = False
        out.append(f'    {"walk" if kind == "walk" else "walk_fast"}_{d} {n}')
    if locked: out.append('    unlock_facing_direction')
    return out

def _runs(steps):
    out = []
    for s in steps:
        if out and out[-1][0] == s: out[-1][1] += 1
        else: out.append([s, 1])
    return [(s, n) for s, n in out]

def p7e_spec():
    """Emerald's puzzle 7: arrows {tile: (colour, arrow 0 right 1 down 2 left 3 up)}, buttons {colour: [tiles]},
    pads [(tile, partner tile)], riders {colour: [(uid, tile, Black 2 dir, statue)]}."""
    from gba import Repo
    r = Repo(EM); mj = map_json('em', 7)
    g, _ = r.layout_grid(mj['layout'])
    arrows = {}
    for y in range(g.shape[0]):
        for x in range(g.shape[1]):
            mt = int(g[y, x]) & 0x3FF
            if P7E_BASE <= mt < P7E_BASE + 5 * 8 and (mt - P7E_BASE) % 8 < 4:
                arrows[(x, y)] = ((mt - P7E_BASE) // 8, (mt - P7E_BASE) % 8)
    buttons = {}
    for c in mj['coord_events']:
        name = c['script'].split('_EventScript_')[-1]
        col = name[:-len('Button')] if name.endswith('Button') else None
        if col in P7E_COLORS: buttons.setdefault(P7E_COLORS.index(col), []).append((c['x'], c['y']))
    W = mj['warp_events']
    pads = [((w['x'], w['y']), (W[int(w['dest_warp_id'])]['x'], W[int(w['dest_warp_id'])]['y']))
            for w in W if w['dest_map'] == 'MAP_ROUTE110_TRICK_HOUSE_PUZZLE7']
    riders = {}
    for i, o in enumerate(mj['object_events'], 1):
        t = (o['x'], o['y'])
        if t in arrows:
            uid = int(o['local_id']) if str(o.get('local_id', '')).isdigit() else i
            riders.setdefault(arrows[t][0], []).append((uid, t, P7_FACE.get(o['movement_type'], 1),
                                                         o['graphics_id'] == 'OBJ_EVENT_GFX_TRICK_HOUSE_STATUE'))
    return arrows, buttons, pads, riders

def p7e_positions(arrows, uid, t, face, presses):
    """Where a rider is, facing which way, after `presses` presses of its colour (the squares are closed loops)."""
    for _ in range(presses):
        dx, dy = ((1, 0), (0, 1), (-1, 0), (0, -1))[arrows[t][1]]
        t = (t[0] + dx, t[1] + dy); face = P7_CCW[face]
    return t, face

P7_HEAD = '''// Route110_TrickHousePuzzle7 (zone {zone}; GENERATED by b2tools/trick_house.py: edit the generator; notes/TRICK_HOUSE.md).
// Sapphire/Ruby data/maps/Route110_TrickHousePuzzle7/scripts.inc: arrow floors, 5 levers, a warp pad; Emerald's
// (pokeemerald) is Mossdeep Gym's rotating-tile puzzle: #ifdef HOENN_EMERALD. How each is built: the comment above
// puzzle 7 in the generator. The scroll, the door (13,1), the trainers, the levers, the switch objects and the
// triggers are in data/story/trick_house.json (Emerald: data/story/emerald/trick_house.json). Map scripts:
// {init:04d}_room_Route110_TrickHousePuzzle7_init.s. Room tiles = Sapphire + (1, 1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"
#include "scenes/trick_house_lib.inc"

    ScriptEntry TH_P7_Scroll            // 1: the scroll
    ScriptEntry TH_P7_Door              // 2: the door (13,1)
    ScriptEntry TH_P7_Init              // 3: zone init
{entries}
    ScriptEntriesEnd
{defines}
#define TH_DOOR_WARP 2                   // the door's warp: Sapphire warp 2 (13,1), third in data/interiors/{zone}.json
#define TH_SE_CLICK SEQ_SE_DECIDE1       // SE_CLICK (a lever) [guess]

TH_P7_Init:                              // zone init: the door is open once the code is written (VAR_..._7_STATE 2)
    th_door_init VAR_TRICK_HOUSE_PUZZLE_7_STATE, TH_DOOR_WARP
{init_code}
    VMHalt
TH_P7_Scroll:                            // Route110_TrickHousePuzzle7_EventScript_Scroll
    th_scroll VAR_TRICK_HOUSE_PUZZLE_7_STATE, T_FoundScroll, T_Memorized, T_CodeOnIt
TH_P7_Door:                              // Route110_TrickHousePuzzle_EventScript_Door (puzzle 7)
    th_door VAR_TRICK_HOUSE_PUZZLE_7_STATE, T_Wrote, T_Locked, TH_DOOR_WARP
{body}
    .balign 4, 0
'''

def puzzle7_rs():
    """Sapphire/Ruby: (entries, init, body, objects (without the trainers, scroll and door), movement lists)."""
    M = P7Map(); prev = M.explore(); ent = M.entries(prev); plan = p7_switch_plan(M, ent)
    raised = set(M.raised())
    assert not raised & (set(ent) | {st[0] for st in prev}), 'puzzle 7: a raised-track tile is walked onto'
    assert {st[0] for st in prev} & {(13, 2)} and any(abs(st[0][0] - M.scroll[0]) + abs(st[0][1] - M.scroll[1]) == 1
                                                       for st in prev), 'puzzle 7: the scroll or the door is out of reach'
    entries, body, objs, lists = [], [], [], {}
    n = 4
    px, pz = zt(*M.pad_to)
    entries.append(f'    ScriptEntry TH_P7_Pad               // {n}: the warp pad {M.pad}')
    objs.append(dict(kind='trigger', map=mapname(7), at=list(M.pad), w=1, h=1, script=n, var=0, value=0,
                     what=f'the warp pad (Route110_TrickHousePuzzle7_EventScript_1632A8: to {M.pad_to}, the levers kept)'))
    body.append(f'''TH_P7_Pad:                               // Route110_TrickHousePuzzle7_EventScript_1632A8: warpteleport to {M.pad_to}
    h_lock                               // (VAR_..._7_STATE_2: the levers stay; here the zone stays, so do they)
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, {px}, 0, {pz}, 1
    h_fadescreen_from_black
    h_release''')
    n += 1
    init = ['#ifndef HOENN_EMERALD']
    for k in range(1, 6):
        lx, ly = M.lever[k]; ax, ay = M.arrow[k]; uid, hide = P7_UID0 + k, P7_HIDE0 + k
        entries.append(f'    ScriptEntry TH_P7_Lever{k}            // {n}: lever {k} {M.lever[k]} (and its switch object, uid {uid})')
        objs.append(dict(kind='sign', map=mapname(7), at=[lx, ly], script=n, dir=4,
                         what=f'lever {k} (Route110_TrickHousePuzzle7_EventScript_Switch{k}, BG_EVENT_PLAYER_FACING_ANY)'))
        sp = plan[k]
        objs.append(dict(kind='npc', map=mapname(7), at=list(sp['at']), uid=uid, model=sp['code'],
                         script=n if sp['at'] == M.lever[k] else 0, dir=1, move=0, flag=hide,
                         what=f'lever {k} on: the red arrow {M.arrow[k]} turned (3D object {sp["code"]} on '
                              + ('the lever: the arrow is walked onto' if sp['at'] == M.lever[k] else 'the arrow itself')
                              + f'; map-local flag {hide:#04x} hides it while the lever is off)'))
        on, off = M.arrow_mt[(k, True)], M.arrow_mt[(k, False)]
        body.append(f'''TH_P7_Lever{k}:                           // Route110_TrickHousePuzzle7_EventScript_Switch{k}: the arrow {M.arrow[k]}
    h_lock                               // {off:#x} <-> {on:#x}, the lever {M.lever[k]} Lever_Off <-> Lever_On
    h_delay 32
    SEPlay TH_SE_CLICK
    h_goto_if_set FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_{k}, L_TH_P7_Off{k}
    h_setflag FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_{k}             // SetSwitch{k}On
    h_addobject {uid}, {hide:#04x}
    h_release
L_TH_P7_Off{k}:
    h_clearflag FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_{k}           // SetSwitch{k}Off
    h_removeobject {uid}, {hide:#04x}
    h_release''')
        init.append(f'    h_clearflag FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_{k}  // OnTransition: every lever off')
        init.append(f'    h_setflag {hide:#04x}                              // (its switch object hidden)')
        n += 1
    init.append('#endif')
    def code(tree, lab):
        if tree[0] == 'go':
            steps = tree[1]
            if not steps: return [f'    h_release                            // (blocked at once: you stand on it)']
            key = steps
            if key not in lists: lists[key] = f'Mv_TH_P7_{len(lists)}'
            return [f'    ActorCmdExec 255, {lists[key]}         // -> {tree[2]}', '    ActorCmdWait', '    h_release']
        k = tree[1]
        return ([f'    h_goto_if_set FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_{k}, {lab}_{k}'] + code(tree[3], lab + f'_{k}0')
                + [f'{lab}_{k}:'] + code(tree[2], lab + f'_{k}1'))
    for t in sorted(ent, key=lambda t: (t[1], t[0])):
        trees = {de: M.tree(t, *de) for de in ent[t]}
        assert len(set(trees.values())) == 1, f'puzzle 7: the slide from {t} depends on how you step on: {trees}'
        tree = next(iter(trees.values()))
        b = M.mr.behavior(M.raw[t] & 0x3FF)
        what = {0x40: 'red right', 0x41: 'red left', 0x42: 'red up', 0x43: 'red down', 0x44: 'blue right',
                0x45: 'blue left', 0x46: 'blue up', 0x47: 'blue down'}.get(b, f'{b:#x}')
        lab = f'TH_P7_A_{t[0]}_{t[1]}'
        sw = f' (lever {M.switch_at[t]}\'s arrow)' if t in M.switch_at else ''
        entries.append(f'    ScriptEntry {lab:<24s}// {n}: arrow {t} {what}{sw}')
        objs.append(dict(kind='trigger', map=mapname(7), at=list(t), w=1, h=1, script=n, var=0, value=0,
                         what=f'arrow {t} ({what}{sw}): {lab}'))
        body.append(f'{lab}:\n    h_lock\n' + '\n'.join(code(tree, f'L{lab[2:]}')))
        n += 1
    mv = []
    for steps, lab in lists.items():
        mv.append(f'    .balign 4, 0\n{lab}:\n' + '\n'.join(p7_moves(steps)) + '\n    step_end')
    return entries, init, body + mv, objs

def puzzle7_em():
    """Emerald: (entries, init, body, objects (the button and pad triggers, the statues), riders)."""
    arrows, buttons, pads, riders = p7e_spec()
    entries, body, objs, lists = [], [], [], set()
    n = 4
    for k in sorted(buttons):
        col = P7E_COLORS[k]; work = P7E_WORK0 + k
        entries.append(f'    ScriptEntry TH_P7_{col:<17s}// {n}: {col.lower()} button(s) {buttons[k]}')
        for t in buttons[k]:
            objs.append(dict(kind='trigger', map=mapname(7), at=list(t), w=1, h=1, script=n, var=0, value=0,
                             what=f'{col.lower()} button (Route110_TrickHousePuzzle7_EventScript_{col}Button)'))
        b = [f'TH_P7_{col}:                           // Route110_TrickHousePuzzle7_EventScript_{col}Button: SE_SWITCH, SE_REPEL,',
             f'    h_lock                               // moverotatingtileobjects {k}, turnrotatingtileobjects',
             '    SEPlay SEQ_SE_FLD_127', '    VMSleep 8']
        for step in range(4):
            b += [f'    h_goto_if_eq 0x{work:04X}, {step}, L_TH_P7_{col}{step}']
        b.append('    h_release')
        for step in range(4):
            b.append(f'L_TH_P7_{col}{step}:')
            for uid, t, face, statue in sorted(riders.get(k, [])):
                (x, y), f = p7e_positions(arrows, uid, t, face, step)
                a = arrows[(x, y)][1]; w = ('right', 'down', 'left', 'up')[a]; nf = P7_B2DIR[P7_CCW[f]]
                lists.add((w, nf))
                b.append(f'    ActorCmdExec {uid}, Mv_TH_P7_{w}_{nf}            // ({x},{y}) -> {w}, then faces {nf}')
            if riders.get(k): b.append('    ActorCmdWait')
            b += [f'    h_setvar 0x{work:04X}, {(step + 1) % 4}', '    h_release']
        body.append('\n'.join(b))
        n += 1
    for i, (t, d) in enumerate(pads):
        dx, dz = zt(*d)
        entries.append(f'    ScriptEntry TH_P7_Pad{i:<14d}// {n}: warp pad {t} -> {d}')
        objs.append(dict(kind='trigger', map=mapname(7), at=list(t), w=1, h=1, script=n, var=0, value=0,
                         what=f'warp pad -> {d} (MB_MOSSDEEP_GYM_WARP: the objects stay)'))
        body.append(f'''TH_P7_Pad{i}:                              // warp pad {t} -> {d} (DoMossdeepGymWarp: the objects stay)
    h_lock
    SEPlay SEQ_SE_KAIDAN
    h_fadescreen_black
    ActorSetGPos 255, {dx}, 0, {dz}, 1
    h_fadescreen_from_black
    h_release''')
        n += 1
    mv = [f'''    .balign 4, 0
Mv_TH_P7_{w}_{f}:
    lock_facing_direction
    walk_{w}
    unlock_facing_direction
    face_{f}
    step_end''' for w, f in sorted(lists)]
    return entries, [], body + mv, objs, riders

def puzzle7():
    """One script file for both versions (#ifdef HOENN_EMERALD)."""
    L = Lines(); puzzle_common(L, 7)
    rs = puzzle7_rs(); em = puzzle7_em()
    def ifdef(a, b): return '#ifdef HOENN_EMERALD\n' + b + '\n#else\n' + a + '\n#endif'
    sc, ini, tx = files_of(7)
    story = P7_HEAD.format(zone=ZONES[7], init=ini, defines=L.defines(),
                           entries=ifdef('\n'.join(rs[0]), '\n'.join(em[0])),
                           init_code='\n'.join(rs[1]), body=ifdef('\n\n'.join(rs[2]), '\n\n'.join(em[2])))
    init = (f'// Map scripts of Route110_TrickHousePuzzle7 (zone {ZONES[7]}; GENERATED by b2tools/trick_house.py): zone init 3.\n'
            '#include "asm/field_script.inc"\n\n    MapScript 2, 3\n    MapScriptsEnd\n    .balign 4, 0\n')
    return L, story, init

def puzzle7_objects(v, more):
    """Puzzle 7's story objects beside puzzle_objects' (trainers, scroll, door): S/R the levers, switch objects and
    triggers; Emerald the buttons, pads and statues, and the trainers riding the squares stand (the script turns them)."""
    if v == 'rs':
        return more + puzzle7_rs()[3] + item_balls(v, 7)
    *_, objs, riders = puzzle7_em()
    ride = {uid: (t, statue) for k, rs in riders.items() for uid, t, face, statue in rs}
    for o in more:
        if o.get('kind') == 'npc' and o.get('uid') in ride and list(ride[o['uid']][0]) == o['at']:
            o['move'] = 0; o['what'] += ': rides its square (stands; the buttons turn it)'
    for uid, (t, statue) in sorted(ride.items()):
        if statue:
            objs.append(dict(kind='npc', map=mapname(7), at=list(t), uid=uid, model=STATUE_ROCK, script=0, move=0, dir=1,
                             what=f'statue (pokeemerald object {uid}, TRICK_HOUSE_STATUE: Black 2\'s rock {STATUE_ROCK} '
                                  'stands in, as the Mossdeep Gym\'s): rides its square'))
    return more + objs + item_balls(v, 7)

STATUE_ROCK = 206              # b2tools/emerald_gyms.py STATUE_MODEL (Clay Tunnel's rock)

def puzzle7_recipe(v):
    """Puzzle 1's rules + Gen 3's art on every arrow, button, pad and track tile (one texture per metatile); S/R: the
    levers raised blocks (16 high) with Gen 3's Lever_Off art on top and in front, the raised track solid."""
    m = ('pokeemerald/' if v == 'em' else '') + mapname(7)
    grid = gen3_grid(v, 7)
    import models_interior as mi
    sm = mi.sapphire_map(m)
    art = {}
    for (x, y), mt in grid.items():
        if 2 <= y <= 21 and sm['walk'][y][x] and mt not in P7_PLAIN: art.setdefault(mt, []).append((x, y))
    ft = []
    for mt, tiles in sorted(art.items()):
        for rect in row_runs(tiles):
            ft.append(dict(tex=f'th{v[0]}{mt:03x}', gen3=list(tiles[0]), gen3_mt=mt, rect=rect, size=16,
                           _what=f'Gen 3 metatile {mt:#x}'))
    if v == 'em':
        return puzzle_recipe(v, 7, ft, doc="Emerald's puzzle 7: Mossdeep Gym's coloured arrow squares, buttons and warp pads "
                             "drawn with Gen 3's art; the gold walls are low plank boxes.")
    M = P7Map()
    r = puzzle_recipe(v, 7, ft, doc="Sapphire's puzzle 7: arrows, the raised track (solid: Gen 3 bumps you at its edge, "
                      "the slides cross it), the warp pad and its landing drawn with Gen 3's art; the levers raised blocks "
                      "with Gen 3's lever art (the turned arrows: 3D objects).")
    levers = [list(t) for t in sorted(M.lever.values())]
    r['blocks'][0]['tiles'] = [t for t in r['blocks'][0]['tiles'] if t not in levers]
    name = f'th{v[0]}{P7_LEVER_OFF:03x}'; src = ['gen3', m, levers[0][0], levers[0][1], P7_LEVER_OFF]
    r['blocks'].append({'h': 16, 'top': {'tex': name, 'src': src, 'size': 16},
                        'side': {'tex': name, 'src': src, 'u_size': 16, 'v': [0, 1]}, 'shade_top': 1.0,
                        'tiles': levers, '_what': 'the levers (Lever_Off)'})
    r['block'] = [list(t) for t in M.raised()]
    return r

def p7_switch_plan(M, ent):
    """{lever k: {at, code, off (arrow - at), mt}}: where switch k's object stands and its model. An arrow you can walk
    onto: the object stands on the lever, its model draws the arrow off to the side (one model each); an arrow only
    slides cross: the object stands on the arrow (one model per art)."""
    plan, codes, free = {}, {}, list(P7_MODELS)
    for k in sorted(M.arrow, key=lambda k: (M.arrow[k] in ent, k)):
        mt = M.arrow_mt[(k, True)]
        if M.arrow[k] in ent:
            at = M.lever[k]; key = ('lever', k)
        else:
            at = M.arrow[k]; key = ('art', mt)
        if key not in codes:
            assert free, 'puzzle 7: more switch models than free object records'
            codes[key] = free.pop(0)
        plan[k] = dict(at=at, code=codes[key], off=(M.arrow[k][0] - at[0], M.arrow[k][1] - at[1]), mt=mt)
    return plan

def p7_switch_models():
    """[(code, BMD0, object.json)]: the turned red arrows (Gen 3's On metatile flat on the floor, 2 units up: Black 2's
    rug spacing, the Off art under it is part of the floor; 1 unit flickers in melonDS, notes/INTERIORS.md "Flicker"),
    drawn off the object's tile by its offset."""
    import models_objects as MO
    from dae import Model
    import numpy as np
    M = P7Map(); plan = p7_switch_plan(M, M.entries())
    out = {}
    for k, sp in sorted(plan.items()):
        if sp['code'] in out: continue
        dx, dz = sp['off'][0] * 16, sp['off'][1] * 16
        px = np.asarray(M.mr.render(sp['mt']), dtype=np.uint8).copy(); px[..., 3] = 255
        m = Model(f'trick_arrow{sp["code"]}')
        m.quad('arrow', [(dx - 8, 2, dz - 8, 0, 1), (dx - 8, 2, dz + 8, 0, 0), (dx + 8, 2, dz + 8, 1, 0), (dx + 8, 2, dz - 8, 1, 1)])
        mdl = MO.to_mdl0(m, {'arrow': px})
        bmd = MO.bmd0(mdl, MO.tex0_block([('arrow', px, 3)]))
        ks = [j for j, q in sorted(plan.items()) if q['code'] == sp['code']]
        where = ('stands on the lever ' + str(M.lever[k]) + f', the arrow {sp["off"]} off it') if sp['at'] == M.lever[k] \
            else 'stands on the arrow (only slides cross it)'
        meta = dict(code=sp['code'], name=f'trick-arrow-{sp["mt"]:03x}' + ('' if sp['at'] != M.lever[k] else f'-lever{k}'),
                    what=f'Trick House puzzle 7: the red arrow turned by lever(s) {ks} (Gen 3 metatile {sp["mt"]:#x}) flat '
                         f'on the floor; {where} (b2tools/trick_house.py)',
                    record_from=0x2009, record={'collWidth': 1, 'collHeight': 1, 'offX': 0, 'offY': 0, 'offZ': 0},
                    made_by='b2tools/trick_house.py')
        out[sp['code']] = (bmd, meta)
    return [(c, b, m) for c, (b, m) in sorted(out.items())]

# ---------------------------------------------------------------------------------------------------- puzzle 8
MB_P8_FLOOR = 0x48             # MB_TRICK_HOUSE_PUZZLE_8_FLOOR: slips you on as MB_ICE (ForcedMovement_Slip)

def gen3_grid(v, n):
    """{(x, y): metatile id} of a puzzle map (its layout's blocks)."""
    from gba import Repo
    r = Repo(RS if v == 'rs' else EM)
    g, _ = r.layout_grid(r.map_json(mapname(n))['layout'])
    return {(x, y): int(g[y, x]) & 0x3FF for y in range(g.shape[0]) for x in range(g.shape[1])}

def row_runs(tiles):
    """[[x0, z, x1, z]] runs of tiles along each row."""
    out = []
    for z in sorted({t[1] for t in tiles}):
        xs = sorted(x for x, zz in tiles if zz == z); i = 0
        while i < len(xs):
            j = i
            while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1: j += 1
            out.append([xs[i], z, xs[j], z]); i = j + 1
    return out

def puzzle8_recipe(v):
    """Puzzle 8 on puzzle 1's rules, the slippery floor as Black 2's sliding ice ("ice" cells, class 0x18) drawn with
    Gen 3's floor art (one tile per repeat), the rocks raised blocks (16 high) with Gen 3's rock art on top and in front
    (one texture per rock metatile)."""
    import models_interior as mi
    m = ('pokeemerald/' if v == 'em' else '') + mapname(8)
    sm = mi.sapphire_map(m); grid = gen3_grid(v, 8); sc = scroll_at(v, 8)
    ice = sorted((x, z) for z in range(2, 22) for x in range(sm['w']) if sm['walk'][z][x] and sm['beh'][z][x] == MB_P8_FLOOR)
    mts = {grid[t] for t in ice}
    assert len(mts) == 1, mts
    ice_mt = mts.pop()
    ft = [dict(tex=f'th{v[0]}{ice_mt:03x}', gen3=list(ice[0]), gen3_mt=ice_mt, rect=r, size=16,
               _what='the slippery floor (MB_TRICK_HOUSE_PUZZLE_8_FLOOR)') for r in row_runs(ice)]
    r = puzzle_recipe(v, 8, ft, doc="The slippery floor (MB_TRICK_HOUSE_PUZZLE_8_FLOOR) is Black 2's sliding ice "
                      "(\"ice\": class 0x18) with Gen 3's floor art; the rocks are raised blocks with Gen 3's rock art.")
    rocks = [tuple(t) for t in r['blocks'][0]['tiles']]
    by_mt = {}
    for t in rocks: by_mt.setdefault(grid[t], []).append(list(t))
    r['blocks'] = []
    for mt, tiles in sorted(by_mt.items()):
        name = f'th{v[0]}{mt:03x}'; src = ['gen3', m, tiles[0][0], tiles[0][1], mt]
        r['blocks'].append({'h': 16, 'top': {'tex': name, 'src': src, 'size': 16},
                            'side': {'tex': name, 'src': src, 'u_size': 16, 'v': [0, 1]}, 'shade_top': 1.0,
                            'tiles': tiles, '_what': f'rocks (metatile {mt:#x})'})
    r['ice'] = [list(t) for t in ice]
    return r

# ---------------------------------------------------------------------------------------------------- story objects
SPRITES = {v: json.load(open(p)) for v, p in (('rs', os.path.join(ROOT, 'data', 'sprite_map.json')),
                                              ('em', os.path.join(ROOT, 'data', 'emerald', 'sprite_map.json')))}

def sprite(v, gfx):
    s = SPRITES[v].get(gfx) or SPRITES['rs'].get(gfx)
    assert s, gfx
    return s['code']

def trainer_ids(v):
    t = json.load(open(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json')))['trainers']
    if v == 'em':
        t = dict(t, **json.load(open(os.path.join(ROOT, 'data', 'emerald', 'hoenn_trainer_data.json')))['trainers'])
    return t

def map_json(v, k):
    return json.load(open(os.path.join(RS if v == 'rs' else EM, 'data', 'maps', mapname(k), 'map.json')))

def puzzle_objects(v, n, scripts):
    """Story objects of puzzle n in version v (rs/em): the trainers, Cut trees / boulders, the scroll and the door."""
    mj = map_json(v, n); m = mapname(n); out = []
    tr = trainer_ids(v)
    for i, o in enumerate(mj.get('object_events') or []):
        uid = int(o.get('local_id', i + 1)) if str(o.get('local_id', '')).isdigit() else i + 1
        g = o['graphics_id']
        if g == 'OBJ_EVENT_GFX_CUTTABLE_TREE':
            out.append(dict(kind='npc', map=m, at=[o['x'], o['y']], uid=uid, model=108, script=10004, dir=1, flag=0,
                            what=f'Cut tree (Sapphire object {uid}; Black 2 cut-tree object, back on every entry as in Gen 3)'))
        elif g == 'OBJ_EVENT_GFX_PUSHABLE_BOULDER':
            out.append(dict(kind='npc', map=m, at=[o['x'], o['y']], uid=uid, model=8196, script=10000, dir=1, flag=0,
                            what=f'Strength boulder (Sapphire object {uid}; Hoenn 1x1 boulder 0x2004)'))
        elif o.get('trainer_type') == 'TRAINER_TYPE_NORMAL':
            name = 'TRAINER_' + o['script'].split('_EventScript_')[-1].upper()
            t = tr[name]
            mv = move_codes.npc(o['movement_type'], (o.get('movement_range_x', 0), o.get('movement_range_y', 0)), g)
            d = mv.get('dir', 1)
            out.append(dict(kind='npc', map=m, at=[o['x'], o['y']], uid=uid, model=sprite(v, g), script=3000 + t['b2_id'],
                            dir=d, move=mv['move'], evtype=1, p0=int(o['trainer_sight_or_berry_tree_id']),
                            what=f'{name} {t["b2_id"]}: eye-contact trainer (Sapphire object {uid}, {g[16:]}, '
                                 f'{o["movement_type"][14:]})'))
    for b in mj.get('bg_events') or []:
        if b.get('script', '').endswith('_Scroll') or b.get('script', '').endswith('_16328B'):
            out.append(dict(kind='sign', map=m, at=[b['x'], b['y']], script=scripts['scroll'], dir=4,
                            what='the scroll with the secret code (BG_EVENT_PLAYER_FACING_ANY)'))
    out.append(dict(kind='sign', map=m, at=[13, 1], script=scripts['door'], dir=0,
                    what='the door (13,1) (MB_TRICK_HOUSE_PUZZLE_DOOR, read facing north)'))
    return out

def story_objects(v):
    objs = [dict(kind='npc', map='Route110_TrickHouseEntrance', at=[6, 2], uid=1, model=sprite(v, 'OBJ_EVENT_GFX_MAN_1'),
                 script=2, dir=2, flag='FLAG_HIDE_TRICKMASTER_ENTRANCE',
                 what='the Trick Master (Sapphire object 1, MAN_1; NPC index 0: the zone init places him per level)'),
            dict(kind='sign', map='Route110_TrickHouseEntrance', at=[5, 1], script=3, dir=0,
                 what='the scroll (BG_EVENT_PLAYER_FACING_NORTH)')]
    for x, y in ((4, 7), (5, 6), (6, 6), (7, 7)):
        objs.append(dict(kind='trigger', map='Route110_TrickHouseEntrance', at=[x, y], w=1, h=1, script=4,
                         var='VAR_TRICK_HOUSE_ENTRANCE_STATE', value=0, what='"You\'re being watched..."'))
    objs += [dict(kind='npc', map='Route110_TrickHouseEnd', at=[4, 5], uid=1, model=sprite(v, 'OBJ_EVENT_GFX_MAN_1'),
                  script=2, dir=3, flag='FLAG_HIDE_TRICK_HOUSE_END_MAN',
                  what='the Trick Master (Sapphire object 1, MAN_1, FACE_RIGHT; NPC index 0)'),
             dict(kind='trigger', map='Route110_TrickHouseEnd', at=[2, 2], w=1, h=1, script=3, var=0x4001, value=0,
                  what='TrickMasterExitTrigger (VAR_TEMP_2 = map-local work 0x4001)')]
    built = BUILT['emerald' if v == 'em' else 'sapphire']
    for n in list(range(1, built + 1)) + ([7] if P7_READY and built < 7 else []) + ([8] if P8_READY and built < 8 else []):
        if n == 7 and not (P7_READY or built >= 7): continue
        more = puzzle_objects(v, n, PUZZLE_SCRIPTS[n])
        if n == 2: more += puzzle2_objects(v)
        if n == 3: more += puzzle3_objects(v)
        if n == 4: more += item_balls(v, 4)
        if n == 5: more += puzzle5_objects(v)
        if n == 6: more += puzzle6_objects(v)
        if n == 7: more = puzzle7_objects(v, more)
        if n == 8: more += item_balls(v, 8)
        for o in more:           # a rooms folder that predates the puzzle rooms: their objects are left out (story.py)
            o['optional'] = True
        objs += more
    return objs

PUZZLE_SCRIPTS = {1: dict(scroll=2, door=3), 2: dict(scroll=1, door=2), 3: dict(scroll=1, door=2), 4: dict(scroll=1, door=2),
                  5: dict(scroll=1, door=2), 6: dict(scroll=1, door=2), 7: dict(scroll=1, door=2),
                  8: dict(scroll=1, door=2)}

# ---------------------------------------------------------------------------------------------------- the test kit
TEST = r'''// Test start for the Trick House (test builds only: HOENN_TEST_CHTH=1 with HOENN_TEST_WARP=514,3,7; trick_house
// 2026-10-19, notes/TRICK_HOUSE.md; GENERATED by b2tools/trick_house.py). Littleroot's town sign (stand at (183,366) facing
// north) runs Test_TH_Setup, then the sign's test warp into the Trick House entrance. The stage sentinel 0x7Bxy (tests
// rewrite it in an APFS clone of the ROM, as b2tools/room_look.py does): x = puzzles done (VAR_TRICK_HOUSE_ROOMS_COMPLETED),
// y = Badges 0-8 (9 = 8 + the game cleared). Once: a Lv 100 Groudon with Rock Smash, Cut and Strength, Running Shoes, the field menu.
// Never assembled into normal builds.
#ifdef HOENN_TEST_CHTH
#ifndef TRICK_HOUSE_TEST_INC
#define TRICK_HOUSE_TEST_INC
#define TH_STAGE 0x8004
#define TH_TT 0x8005
Test_TH_Setup:
    h_setvar TH_STAGE, 0x7B03               // TH_STAGE_SENTINEL
    PokePartyGetCount TH_TT, 0
    h_goto_if_ne TH_TT, 0, L_TH_TestState
    FlagSet 2401                            // FLAG_SYS_POKEMON_GET
    FlagSet 2403                            // FLAG_SYS_B_DASH
    PokePartyAdd TH_TT, SPECIES_GROUDON, 0, 100
    PokePartyLearnMove 0, 1, MOVE_ROCK_SMASH
    PokePartyLearnMove 0, 2, MOVE_CUT
    PokePartyLearnMove 0, 3, MOVE_STRENGTH
L_TH_TestState:
    WorkSet TH_TT, TH_STAGE
    WorkDiv TH_TT, 16
    WorkAnd TH_TT, 15
    WorkSet VAR_TRICK_HOUSE_ROOMS_COMPLETED, TH_TT
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_3, 0
    h_setvar VAR_TRICK_HOUSE_ENTRANCE_STATE_2, 0
    h_setvar VAR_TRICK_HOUSE_STATE, 0
    h_setvar VAR_TRICK_HOUSE_PRIZE_PICKUP, 0
    WorkSet TH_TT, TH_STAGE
    WorkAnd TH_TT, 15
{badges}
    VMReturn
#endif
#endif
'''

def test_kit():
    b = []
    for i in range(8):
        b.append(f'    h_goto_if_lt TH_TT, {i + 1}, L_TH_TestBadgesDone\n    TrainerCardAddBadge {i}')
    b.append('    h_goto_if_lt TH_TT, 9, L_TH_TestBadgesDone\n    FlagSet 2400                            // FLAG_SYS_GAME_CLEAR')
    b.append('L_TH_TestBadgesDone:')
    return TEST.replace('{badges}', '\n'.join(b))

# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); a = ap.parse_args()
    changed = []
    lib = LIB
    for k, v in dict(Entrance=ZONES['Entrance'], End=ZONES['End'], Corridor=ZONES['Corridor'],
                     p1=ZONES[1], p2=ZONES[2], p3=ZONES[3], p3alt=ZONE_P3_ALT, p4=ZONES[4], p5=ZONES[5], p6=ZONES[6],
                     p7=ZONES[7], p8=ZONES[8], built_rs=BUILT['sapphire'], built_em=BUILT['emerald'], p8_ready=int(P8_READY),
                     p7_ready=int(P7_READY)).items():
        lib = lib.replace('{' + k + '}', str(v))
    write(os.path.join(SCRIPTS, 'scenes', 'trick_house_lib.inc'), lib, a.check, changed)
    for k, fn in (('Entrance', entrance), ('End', end_room), ('Corridor', corridor), (1, puzzle1)):
        L, entries, story, init = fn()
        p = room_file(k)
        write(p, merge_room_script(p, entries, story, INCLUDES), a.check, changed)
        write(room_file(k, 'init'), init, a.check, changed)
        if len(L.rows) > 1:
            write(room_file(k, 'text', '.txt'), L.text('rs'), a.check, changed)
            write(room_file(k, 'text', '.txt', 'emerald'), L.text('em'), a.check, changed)
    # puzzle 2: its own script/text/map-script files (named after its zone's Black 2 numbers), recipes, zone json
    L, story, init = puzzle2()
    write(room_file(2), story, a.check, changed)
    write(room_file(2, 'init'), init, a.check, changed)
    write(room_file(2, 'text', '.txt'), L.text('rs'), a.check, changed)
    write(room_file(2, 'text', '.txt', 'emerald'), L.text('em'), a.check, changed)
    for v in ('rs', 'em'):
        write(os.path.join(LAYOUTS, mapname(2) + ('_Emerald' if v == 'em' else '') + '.json'),
              json.dumps(puzzle2_recipe(v), indent=1) + '\n', a.check, changed)
    write(os.path.join(INTERIORS, f'{ZONES[2]}.json'), json.dumps(zone_json(2, (
        f"{mapname(2)} (zone {ZONES[2]}): GENERATED by b2tools/trick_house.py (notes/TRICK_HOUSE.md). Puzzle 1's look "
        "(area 282). Warps in Sapphire's order; people, signs and triggers are story objects (data/story/trick_house.json; "
        'Emerald: data/story/emerald/trick_house.json; Emerald installs Route110_TrickHousePuzzle2_Emerald, data/versions.json).')),
        indent=1) + '\n', a.check, changed)
    L, story, init = puzzle3()
    write(room_file(3), story, a.check, changed)
    write(room_file(3, 'init'), init, a.check, changed)
    write(room_file(3, 'text', '.txt'), L.text('rs'), a.check, changed)
    write(room_file(3, 'text', '.txt', 'emerald'), L.text('em'), a.check, changed)
    for v in ('rs', 'em'):
        for st in (0, 1):
            write(os.path.join(LAYOUTS, P3_ROOM[st] + ('_Emerald' if v == 'em' else '') + '.json'),
                  json.dumps(puzzle3_recipe(v, st), indent=1) + '\n', a.check, changed)
    z3 = zone_json(3, (
        f"{mapname(3)} (zone {ZONES[3]}, door state 0; zone {ZONE_P3_ALT} = its copy with {P3_ROOM[1]}, door state 1): "
        "GENERATED by b2tools/trick_house.py (notes/TRICK_HOUSE.md). Puzzle 1's look (area 282). Warps in Sapphire's order; "
        "people, signs and triggers are story objects (data/story/trick_house.json; Emerald: data/story/emerald/). "
        "\"variants\" (b2tools/patches/interiors.py): zone 451 gets this zone's header with its own room's matrix."))
    z3['variants'] = [dict(zone=ZONE_P3_ALT, room=P3_ROOM[1], what='door state 1 (VAR_TRICK_HOUSE_PUZZLE_3_DOORS 1)')]
    write(os.path.join(INTERIORS, f'{ZONES[3]}.json'), json.dumps(z3, indent=1) + '\n', a.check, changed)
    for n in (4, 8):                     # rooms with no mechanics of their own beyond Black 2's objects and cells
        if n > min(BUILT.values()) and not (n == 8 and P8_READY): continue
        L, story, init = simple_puzzle(n)
        write(room_file(n), story, a.check, changed)
        write(room_file(n, 'init'), init, a.check, changed)
        write(room_file(n, 'text', '.txt'), L.text('rs'), a.check, changed)
        write(room_file(n, 'text', '.txt', 'emerald'), L.text('em'), a.check, changed)
        for v in ('rs', 'em'):
            write(os.path.join(LAYOUTS, mapname(n) + ('_Emerald' if v == 'em' else '') + '.json'),
                  json.dumps(puzzle8_recipe(v) if n == 8 else puzzle_recipe(v, n, doc=SIMPLE_WHAT[n]), indent=1) + '\n',
                  a.check, changed)
        write(os.path.join(INTERIORS, f'{ZONES[n]}.json'), json.dumps(zone_json(n, (
            f"{mapname(n)} (zone {ZONES[n]}): GENERATED by b2tools/trick_house.py (notes/TRICK_HOUSE.md). Puzzle 1's look "
            "(area 282). Warps in Sapphire's order; people and signs are story objects (data/story/trick_house.json; "
            f'Emerald: data/story/emerald/trick_house.json; Emerald installs {mapname(n)}_Emerald, data/versions.json).')),
            indent=1) + '\n', a.check, changed)
    if 5 <= min(BUILT.values()):         # puzzle 5: the Mechadolls' quiz
        L, story, init = puzzle5()
        write(room_file(5), story, a.check, changed)
        write(room_file(5, 'init'), init, a.check, changed)
        write(room_file(5, 'text', '.txt'), L.text('rs'), a.check, changed)
        write(room_file(5, 'text', '.txt', 'emerald'), L.text('em'), a.check, changed)
        for v in ('rs', 'em'):
            write(os.path.join(LAYOUTS, mapname(5) + ('_Emerald' if v == 'em' else '') + '.json'),
                  json.dumps(puzzle5_recipe(v), indent=1) + '\n', a.check, changed)
        write(os.path.join(INTERIORS, f'{ZONES[5]}.json'), json.dumps(zone_json(5, (
            f"{mapname(5)} (zone {ZONES[5]}): GENERATED by b2tools/trick_house.py (notes/TRICK_HOUSE.md). Puzzle 1's floor "
            "(area 282) on walkways over the dark. Warps in Sapphire's order; the Mechadolls, their triggers, the scroll and "
            "the door are story objects (data/story/trick_house.json; Emerald: data/story/emerald/trick_house.json; Emerald "
            f'installs {mapname(5)}_Emerald, data/versions.json).')), indent=1) + '\n', a.check, changed)
    if 6 <= min(BUILT.values()):         # puzzle 6: the rotating gates (th_p6; arms: src/objects3d 0077/0087)
        L, story, init = simple_puzzle(6)
        write(room_file(6), story, a.check, changed)
        write(room_file(6, 'init'), init, a.check, changed)
        write(room_file(6, 'text', '.txt'), L.text('rs'), a.check, changed)
        write(room_file(6, 'text', '.txt', 'emerald'), L.text('em'), a.check, changed)
        for v in ('rs', 'em'):
            write(os.path.join(LAYOUTS, mapname(6) + ('_Emerald' if v == 'em' else '') + '.json'),
                  json.dumps(puzzle_recipe(v, 6, doc=SIMPLE_WHAT[6]), indent=1) + '\n', a.check, changed)
        write(os.path.join(INTERIORS, f'{ZONES[6]}.json'), json.dumps(zone_json(6, (
            f"{mapname(6)} (zone {ZONES[6]}): GENERATED by b2tools/trick_house.py (notes/TRICK_HOUSE.md). Puzzle 1's look "
            "(area 282). Warps in Sapphire's order; the trainers, the scroll, the door and the gate arms (3D actors turned "
            "by b2tools/patches/rotating_gates.c) are story objects (data/story/trick_house.json; Emerald: "
            f'data/story/emerald/trick_house.json; Emerald installs {mapname(6)}_Emerald, data/versions.json).')),
            indent=1) + '\n', a.check, changed)
        rg = _gates()
        for long in (False, True):
            bmd6, meta6 = rg.arm_model(long)
            od = os.path.join(ROOT, 'src', 'objects3d', f"{meta6['code']:04x}-{meta6['name']}")
            write_bin(os.path.join(od, 'model.nsbmd'), bmd6, a.check, changed)
            write(os.path.join(od, 'object.json'), json.dumps(meta6, indent=1), a.check, changed)
    if 7 <= min(BUILT.values()) or P7_READY:     # puzzle 7 (th_p7): S/R arrows + levers + warp pad; Emerald rotating tiles
        L, story, init = puzzle7()
        write(room_file(7), story, a.check, changed)
        write(room_file(7, 'init'), init, a.check, changed)
        write(room_file(7, 'text', '.txt'), L.text('rs'), a.check, changed)
        write(room_file(7, 'text', '.txt', 'emerald'), L.text('em'), a.check, changed)
        for v in ('rs', 'em'):
            write(os.path.join(LAYOUTS, mapname(7) + ('_Emerald' if v == 'em' else '') + '.json'),
                  json.dumps(puzzle7_recipe(v), indent=1) + '\n', a.check, changed)
        write(os.path.join(INTERIORS, f'{ZONES[7]}.json'), json.dumps(zone_json(7, (
            f"{mapname(7)} (zone {ZONES[7]}): GENERATED by b2tools/trick_house.py (notes/TRICK_HOUSE.md). Puzzle 1's look "
            "(area 282). Warps in Sapphire's order (Emerald's ten warp pads are step triggers, not warps); the trainers, "
            "levers, switch objects, statues, the arrows' / buttons' / pads' triggers, the scroll and the door are story "
            "objects (data/story/trick_house.json; Emerald: data/story/emerald/trick_house.json; Emerald installs "
            f'{mapname(7)}_Emerald, data/versions.json).')), indent=1) + '\n', a.check, changed)
        for code7, bmd7, meta7 in p7_switch_models():
            od = os.path.join(ROOT, 'src', 'objects3d', f"{code7:04x}-{meta7['name']}")
            write_bin(os.path.join(od, 'model.nsbmd'), bmd7, a.check, changed)
            write(os.path.join(od, 'object.json'), json.dumps(meta7, indent=1), a.check, changed)
    bmd, px, meta = hole_object()
    od = os.path.join(ROOT, 'src', 'objects3d', f'{HOLE_MODEL:04x}-trick-hole')
    write_bin(os.path.join(od, 'model.nsbmd'), bmd, a.check, changed)
    write(os.path.join(od, 'object.json'), json.dumps(meta, indent=1), a.check, changed)
    versions_entries(a.check, changed)
    for v, d in (('rs', os.path.join(ROOT, 'data', 'story')), ('em', os.path.join(ROOT, 'data', 'story', 'emerald'))):
        objs = story_objects(v)
        doc = ('The Trick House\'s story objects (trick_house 2026-10-19, notes/TRICK_HOUSE.md; GENERATED by '
               'b2tools/trick_house.py: edit the generator). ' + ('Emerald (pokeemerald): replaces data/story/trick_house.json '
               'in an Emerald build.' if v == 'em' else 'Sapphire/Ruby (pokeruby).'))
        write(os.path.join(d, 'trick_house.json'), json.dumps({'_doc': doc, 'objects': objs}, indent=1) + '\n', a.check, changed)
    write(os.path.join(SCRIPTS, 'scenes', 'trick_house_test.inc'), test_kit(), a.check, changed)
    print(('would change: ' if a.check else 'changed: ') + (', '.join(changed) or 'nothing'))

if __name__ == '__main__':
    main()
