"""Wally's catching tutorial (chapter Ch1, Sapphire PetalburgCity_EventScript_WallyTutorial): Black 2's own catching
demo (script command CallCaptureDemo, b2:0874.s Bianca on Route 20) with Sapphire's Pokémon.

Sapphire (pokeruby src/field_specials.c PutZigzagoonInPlayerParty, src/battle_setup.c
ScrSpecial_StartWallyTutorialBattle, src/battle_controller_wally.c): Wally's Lv 7 Zigzagoon (Tackle only) against a
wild Lv 5 Ralts; Zigzagoon uses Tackle, Ralts uses Growl, then Wally throws a Poké Ball and catches it.
Black 2 (ov012 EventCaptureDemo_Create 0x02168964, read with b2tools/armdis.py): builds the two parties with
PokeParty_CreateTempPkm(pkm, species, level, 0, 0) + PokeParty_SetMove(pkm, move, slot), then BtlSetup_SetCaptureDemo
(battle type 4). The demo itself (ov167 func_ov167_021cea24, src/ov167/btlv_core.c) is fixed: the player's side uses
move 0x21 (Tackle), the wild one 0x2d (Growl), then system text 23 line 0 (the demo trainer's line) and line 1
("<name> used a Poké Ball!"), the ball, "Gotcha!". So only the two Pokémon change:
  Lillipup (506) Lv 5 Tackle/Leer/Odor Sleuth  ->  Zigzagoon (263) Lv 7 Tackle
  Purrloin (509) Lv 2 Scratch/Growl            ->  Ralts (280) Lv 5 Growl
The species come from one literal (0x2a1 = 673, also the heap allocation's debug line number): 673 - 167 = 506 for the
first, then r4 = 79 << 2 = 316 (Odor Sleuth, slot 2) and 316 + 193 = 509 for the second. Edits: the literal 430
(430 - 167 = 263), slot 2 takes 0 instead of r4, `adds r4, #193` -> `subs r4, #36` (316 - 36 = 280), levels and moves.
The two lines of system text 23 are Sapphire's Wally lines (src/text/overrides.json)."""
import os

BASE = 0x021503c0          # ov012 load address (extract/b2_us/arm9_overlays/overlays.yaml)
EDITS = [                  # (address, old bytes, new bytes) in arm9_ov012.bin
    (0x02168ab4, 'a1020000', 'ae010000'),   # literal 673 -> 430: first species 430 - 167 = 263 Zigzagoon
    (0x021689b8, '0522', '0722'),           # movs r2, #5 -> #7: Lv 7
    (0x021689ca, '2b21', '0021'),           # movs r1, #43 (Leer) -> #0: slot 1 empty (slot 0 stays Tackle 33)
    (0x021689d8, '211c', '0021'),           # adds r1, r4, #0 (Odor Sleuth 316) -> movs r1, #0: slot 2 empty
    # The wild Ralts is male, as Sapphire's (battle_setup.c ScrSpecial_StartWallyTutorialBattle: CreateMaleMon). The battle
    # takes the sex from the PID (PokeParty_GetSex -> PML_UtilDerivePkmSex: PID & 0xff below the species' ratio = female;
    # Ralts 127), so the PID must be 0xff (male; not shiny with the demo's ID 0). It has to be GIVEN at creation:
    # PokeParty_CreateTempPkm picks a random PID (pid u64 (0, -1) -> GFL_RandomLC), and changing it afterwards with
    # PokeParty_SetParam(PKM_PARAM_PID) (v15) only stores the new PID: the four data blocks stay where the old PID put them
    # and are read in the new PID's order (PML_PkmGetParamBlockCore(pkm, pkm->pid, block)), so the species came from the
    # moves block (Growl 45 = Vileplume, garbage name) unless the old order happened to match (fixes_v151, 2026-10-08).
    # So the second Pokemon calls PokeParty_CreatePkm(pkm, 280, 5, ID 0 (r3, [sp]), IVs -1 = random ([sp+4], as
    # CreateTempPkm), PID u64 ([sp+8] = 0xff, [sp+12] = the caller's saved arg, a pointer: never -1, so the PID is used as
    # given; PML_CreatePkm reads only its low word (and `ands 0` the high one)). [sp+8] is free here (next written at
    # 0x02168a9c); [sp+12] is not written. PML_CreatePkm then stores the sex from the PID (PKM_PARAM_SEX = male) and the
    # default moves (a Lv 5 Ralts: Growl only); slot 0 is set to Growl as before; the old slot 1-3 calls are skipped.
    (0x021689f2, '0020c13400900023281c211c0222b3f622fd281c0a210022b4f60bfc281c2d210122b4f606fc281c00210222b4f601fc281c00210322b4f6fcfb',
     '0020'        # movs r0, #0
     '0090'        # str r0, [sp]        ID high word 0 (ID 0, as before)
     '0138'        # subs r0, #1         -1
     '0190'        # str r0, [sp, #4]    IVs: -1 = random (as CreateTempPkm)
     'ff20'        # movs r0, #0xff
     '0290'        # str r0, [sp, #8]    PID 0xff: male, not shiny
     '243c'        # subs r4, #36        316 - 36 = 280 Ralts (r4 stays 280 for the call at 0x02168a9e, as before)
     '0023'        # movs r3, #0         ID 0
     '281c'        # adds r0, r5, #0     pkm
     '211c'        # adds r1, r4, #0     species
     '0522'        # movs r2, #5         Lv 5
     'b3f62cfd'    # bl PokeParty_CreatePkm (0x0201c464)
     '281c'        # adds r0, r5, #0
     '2d21'        # movs r1, #45        Growl
     '0022'        # movs r2, #0         slot 0
     'b4f607fc'    # bl PokeParty_SetMove (0x0201d224)
     '09e0'        # b 0x02168a2c
     + 'c046' * 10),  # nop (not reached)
]

def apply_code(code):
    path = os.path.join(code, 'arm9_ov012.bin')
    data = bytearray(open(path, 'rb').read())
    for addr, old, new in EDITS:
        at, o, n = addr - BASE, bytes.fromhex(old), bytes.fromhex(new)
        assert data[at:at + len(o)] in (o, n), f'ov012 {addr:#x}: unexpected {data[at:at + len(o)].hex()}'
        data[at:at + len(o)] = n
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)
    return f'capture demo: Zigzagoon Lv 7 (Tackle) vs Ralts Lv 5 (Growl, male), {len(EDITS)} edits in ov012'
