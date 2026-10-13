"""Black 2's Pokédex as Sapphire's / Ruby's Hoenn Pokédex (hoenn_pokedex, v16; notes/POKEDEX.md).

Text (the `text` patch packs it; made by converter/gen_dex_text.py): Sapphire's entries (Ruby's in a Ruby build) for
species 1-386, page 1 in system 0442 (Black 2's entry field), page 2 in system 0443 (733 blank lines in the US game,
never loaded); the list header 0478 "HOENN POKÉDEX", search 0479, Habitat list 0362. Categories, heights and weights
already equal Sapphire's (checked line by line), so they keep Black 2's lines.

Code (this patch): Sapphire's two-page entries. Sapphire's A button flips page 1 / page 2 on an owned Pokémon's entry
(pokeruby pokedex.c sub_8090C68) and, on the screen after a catch, A shows page 2 and the next A closes (sub_8090A3C).
- ov296 (the Pokémon info panel; work struct, ov296 func_ov296_0219d768): +0x1f0 = the handle of system 0442 (entries;
  from the table data_ov296_0219fb3c, loaded in func_ov296_0219f760), +0x78 = the entry window (2,17,28,7 tiles),
  +8 = owned (the entry text shows only then), +0xc = species, +0 = heap id. func_ov296_0219e854 clears the 4 text
  windows (and cancels their prints), func_ov296_0219e34c prints the own-language page (name, category, HT/WT, entry
  from [+0x1f0]). New field +0x2b4 = the page shown (0/1): past Black 2's struct (0x2b4 B); fairy_ui grows the struct to
  0x328 and leaves +0x2b4..+0x2df free (agreed), without fairy_ui this patch grows it to 0x2b8.
- FlipInfo(work): page 1 -> 2: load system 0443 (GFL_MsgSysLoadData(0, 2, 443, heap)), put its handle at +0x1f0, clear
  + reprint (the entry comes from page 2's line of the same species/form index), put 0442's handle back, free; page
  2 -> 1: clear + reprint. Only for an owned Pokémon of Sapphire's 386.
- ov296 func_ov296_0219e34c +4 (`movs r3, #0x1e; lsls r3, r3, #4`) -> bl HookPrint: any reprint that is not a flip
  (another species, the language view and back, a new panel) sets the page back to 1.
- ov298 func_ov298_021a2b90 (INFO tab keys; Black 2 uses A / L / R only to pick a foreign-language entry: [+0x94] the
  picked language button, 6 none; [+0x98] the language shown, 6 own): its epilogue `ldr r0, [sp, #8]; add sp, #0x10`
  -> bl InfoKeys: when that handler did nothing, the own language is shown and A is newly pressed, flip both panels of
  the INFO tab (+4 and +8) and play the Pokédex's select sound (0x54a, as its language buttons).
- ov297 (the entry shown after a catch, func_ov297_021f43c4 state 1): its `bl GCTX_HIDGetPressedKeys` -> bl CaptureKeys:
  A on page 1 flips to page 2 and is consumed; A on page 2, B or a touch close it as before.
Code in ITCM after the other patches' code (fairy_ui install_itcm's method: arena literal arm9 0x0207B400).

The AREA page on the Hoenn map (dex_area, v16.4; notes/TOWN_MAP.md section 5 "phase 2"). Needs town_map's a/0/8/4
file 21 (the 85 Hoenn records, zone table), so this patch runs after town_map. What Black 2's area page does [code: ov298
disassembly, work/agents/fairy_ui/asm_all/_dsd_gap@ov298_2.s]:
- func_ov298_021a3298 (init) loads the town map's records with func_ov144_0219f718 (a/0/8/5 #0, Unova's 85) and opens
  a/1/7/6 (habitat, 0xb0). func_ov298_021a3bf0 gives each record a habitat byte: the index of the record's zone in the
  85 zone ids of data_ov298_021ac544 (Unova's places). func_ov298_021a400c makes one highlight sprite per record:
  a/1/5/7 NCGR 15 / NCLR 5 / NCER 29 / NANR 46, anim = record field 24 at (field 25, field 26), hidden.
- func_ov298_021a57c4 reads the species' habitat file (func_ov298_021a5c14: file species - 1, 345 B = byte 0 (1: the
  same in every season, then season 0 is used; 0: by GameData_GetSeason) + 4 seasons x (1 byte: 0 found / 1 "area
  unknown", 85 bytes by habitat index)). func_ov298_021a5dac shows record r's highlight when its byte is not 0 and its
  show flag (field 16) is set (func_ov298_021a40fc). Byte bits = Black 2's encounter groups (a/1/2/7): 0x01 grass /
  cave, 0x02 dark grass, 0x04 shaking grass / dust, 0x08 surf, 0x10 rippling surf, 0x20 fishing, 0x40 rippling
  fishing; the place picked on the map (touch / cursor, capsules of fields 6-10) lights the bottom screen's three icons
  (func_ov298_021a5fac: 0x07 walking, 0x18 surfing, 0x60 fishing). The player's place (func_ov298_021a47e0):
  func_ov144_0219f73c(records, func_ov012_02160eb4(zone)) = the first record of the zone header's parent (Unova's).
- No roamer: Black 2 never reads its roamer data in the Pokédex (roamers.py has the search).
The Hoenn area page (this patch):
- habitat(): a/1/7/6 from the built game's own Hoenn encounter tables (a/1/2/7 files of data/hoenn_encounters.json, as
  the encounters patch wrote them for this version: Sapphire's or Ruby's tables) by zone -> town_map zone table ->
  record -> habitat index; every other species (Unova's, events, statics) "area unknown". Sapphire's area screen also
  counts Old/Good Rod and Rock Smash tables; so does this for the rods (rods_fix 2026-10-12: their slots are the
  rippling-fishing group, counted as fishing; patches/rods.py), not Rock Smash (Black 2's starts no battles:
  converter/gen_encounters.py), so the page shows where the Pokémon can really be found.
  Sapphire hides Wynaut (sSpeciesHiddenFromAreaScreen): so does this.
- a/1/5/7 NCGR 15 / NCER 29 / NANR 46 / NCLR 5 (only the area page and ov303 use them): Sapphire's own area art,
  pokeruby graphics/pokedex/area_glow.png (tile 0x10, the glow on a town's or route's cells) and area_marker.png (a
  dungeon), as cells town_map.dex_highlights names (record fields 24-26); semi-transparent like Black 2's (its pulsing
  blend = Sapphire's BLDALPHA glow). The archive keeps its size (padded: ROM layout unchanged).
- ov298 data_ov298_021ac544: the records' own zones (habitat index = first record of the zone).
- ov298/ov303/ov308 call func_ov144_0219f718 -> DexLoadRecords (a/0/8/4 #21), func_ov144_0219f73c -> DexFindRecord (the
  zone table: rooms and caves find their town / cave) without the Unova parent mapping (func_ov012_02160eb4 calls in
  ov298 0x021a47fa and ov303 0x021a2d42 / 0x021a3008 become `adds r0, r1, #0`); ov303 0x021a2d4c (no 0xffff check
  there) -> DexFindRecordSafe (the filler record, drawn off screen). ov144 itself is unchanged (its tuned size).
- Roamers (user): ov298 0x021a5c26 (the habitat file read) -> HabitatRead: for the seven roamers (roamers.py ROAMERS) the
  file is replaced by the roamer's place now (encounter save block +6k: hp 0 = not roaming -> "area unknown"; location
  0-19 = Sapphire's sRoamerLocations row -> its route's habitat index and its walking / surfing bits), as Sapphire's
  area screen shows its roamer.
The Habitat list (the HABITAT button; ported 2026-10-11): Hoenn's places, pages and visited bits, see the "Habitat
list" section below.
"""
import os, re, struct, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV = {296: 0x0219D6E0, 297: 0x021F4260, 298: 0x0219FBC0, 303: 0x0219FBC0, 308: 0x0219F960}   # overlays.yaml base_address

# Black 2 (decomp symbols)
GFL_MsgSysLoadData, GFL_MsgDataFree = 0x0204875C, 0x020487D4
GFL_SndSEPlay, GCTX_HIDGetPressedKeys = 0x02006254, 0x0203DEFC
INFO_CLEAR, INFO_PRINT = 0x0219E854, 0x0219E34C               # ov296
SE_DEX_SELECT = 0x54A                                          # ov298's language-button sound
PAGE2_FILE = 443
W_HANDLE, W_PAGE, W_OWNED, W_SPECIES = 0x1F0, 0x2B4, 0x8, 0xC
N_SAPPHIRE = 386

_spec = __import__('importlib.util').util.spec_from_file_location('exp_share_dex', os.path.join(HERE, 'exp_share.py'))
_es = __import__('importlib.util').util.module_from_spec(_spec); _spec.loader.exec_module(_es)


def asm(text):
    """Thumb machine code through llvm-mc (no pc-relative forms)."""
    src = '.syntax unified\n.thumb\n' + '\n'.join(l.strip() for l in text.strip().splitlines()) + '\n'
    r = subprocess.run([f'{LLVM}/llvm-mc', '-triple=thumbv5te-none-eabi', '-show-encoding'], input=src,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = bytearray()
    for m in re.finditer(r'encoding: \[([^\]]*)\]', r.stdout):
        out += bytes(int(b, 16) for b in m.group(1).split(','))
    return bytes(out)


def bl(src, dst):
    off = (dst & ~1) - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, (hex(src), hex(dst))
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)


class Blob(_es.Thumb):
    def a(self, text): self.out += asm(text)


def itcm_blob(base, area=None):
    t = Blob(base)
    t.label('flipping'); t.out += bytes(4)              # variable: 1 while FlipInfo reprints (HookPrint keeps the page)
    if area:
        area_code(t, area)
    # FlipInfo(r0 = ov296 work) -> r0 = 1 when the page changed
    t.label('FlipInfo')
    t.a('push {r3, r4, r5, r6, r7, lr}\nadds r4, r0, #0x0'); t.beq('flip_no')
    t.a('ldr r0, [r4, #0x8]\ncmp r0, #0x0'); t.beq('flip_no')                       # not owned: page 1 only
    t.a('ldrh r0, [r4, #0xc]'); t.ldr_lit(1, 'n_sapphire'); t.a('cmp r0, r1'); t.bcc('hi', 'flip_no')   # not Sapphire's
    t.ldr_lit(6, 'w_page'); t.a('ldr r0, [r4, r6]\ncmp r0, #0x0'); t.bne('flip_back')
    t.a('ldrh r3, [r4, #0x0]\nmovs r0, #0x0\nmovs r1, #0x2'); t.ldr_lit(2, 'page2_file'); t.bl(GFL_MsgSysLoadData)
    t.a('adds r5, r0, #0x0'); t.beq('flip_no')
    t.ldr_lit(1, 'w_handle'); t.a('ldr r7, [r4, r1]\nstr r5, [r4, r1]')              # 0442's handle -> r7, page 2's in
    t.a('adds r0, r4, #0x0'); t.bl_label('Redraw')
    t.ldr_lit(1, 'w_handle'); t.a('str r7, [r4, r1]\nadds r0, r5, #0x0'); t.bl(GFL_MsgDataFree)
    t.a('movs r0, #0x1\nstr r0, [r4, r6]'); t.b('flip_yes')
    t.label('flip_back')
    t.a('adds r0, r4, #0x0'); t.bl_label('Redraw'); t.a('movs r0, #0x0\nstr r0, [r4, r6]')
    t.label('flip_yes'); t.a('movs r0, #0x1\npop {r3, r4, r5, r6, r7, pc}')
    t.label('flip_no'); t.a('movs r0, #0x0\npop {r3, r4, r5, r6, r7, pc}')
    # Redraw(r0 = work): clear the panel's windows and print it again, flagged as a flip (HookPrint keeps the page)
    t.label('Redraw')
    t.a('push {r4, lr}\nadds r4, r0, #0x0'); t.ldr_lit(1, 'flipping_addr'); t.a('movs r0, #0x1\nstr r0, [r1, #0x0]')
    t.a('adds r0, r4, #0x0'); t.bl(INFO_CLEAR); t.a('adds r0, r4, #0x0'); t.bl(INFO_PRINT)
    t.ldr_lit(1, 'flipping_addr'); t.a('movs r0, #0x0\nstr r0, [r1, #0x0]\npop {r4, pc}')
    # HookPrint: func_ov296_0219e34c +4 (r0 = work; r0-r2 kept, r3 = 0x1e0 as the replaced instructions)
    t.label('HookPrint')
    t.a('push {r1, r2}'); t.ldr_lit(1, 'flipping_addr'); t.a('ldr r1, [r1, #0x0]\ncmp r1, #0x0'); t.bne('hp_keep')
    t.ldr_lit(2, 'w_page'); t.a('str r1, [r0, r2]')
    t.label('hp_keep'); t.a('pop {r1, r2}\nmovs r3, #0x1e\nlsls r3, r3, #0x4\nbx lr')
    # InfoKeys: ov298 func_ov298_021a2b90's epilogue (r5 = INFO work, sp = its frame: [sp+8] = its result), in place
    # of `ldr r0, [sp, #8]; add sp, #0x10`, returning to its `pop {r3-r7, pc}`
    t.label('InfoKeys')
    t.a('ldr r0, [sp, #0x8]\ncmp r0, #0x0'); t.bne('ik_done')
    t.a('push {r0, lr}\nmovs r1, #0x94\nldr r1, [r5, r1]\ncmp r1, #0x6'); t.bne('ik_out')
    t.a('movs r1, #0x98\nldr r1, [r5, r1]\ncmp r1, #0x6'); t.bne('ik_out')
    t.bl(GCTX_HIDGetPressedKeys); t.a('movs r1, #0x1\ntst r0, r1'); t.beq('ik_out')
    t.a('ldr r0, [r5, #0x4]'); t.bl_label('FlipInfo'); t.a('str r0, [sp, #0x0]')
    t.a('ldr r0, [r5, #0x8]'); t.bl_label('FlipInfo'); t.a('ldr r1, [sp, #0x0]\norrs r0, r1'); t.beq('ik_out')
    t.ldr_lit(0, 'se'); t.bl(GFL_SndSEPlay)
    t.label('ik_out'); t.a('pop {r0, r1}\nmov lr, r1\nmovs r0, #0x0')
    t.label('ik_done'); t.a('add sp, #0x10\nbx lr')
    # CaptureKeys: ov297 func_ov297_021f43c4 state 1 (r4 = its work, [+0x20] = the ov296 panel), in place of
    # `bl GCTX_HIDGetPressedKeys`: the keys, without A when A turned page 1 into page 2
    t.label('CaptureKeys')
    t.a('push {r4, r5, r6, lr}\nadds r6, r4, #0x0'); t.bl(GCTX_HIDGetPressedKeys)
    t.a('adds r5, r0, #0x0\nmovs r1, #0x1\ntst r0, r1'); t.beq('ck_out')
    t.a('ldr r0, [r6, #0x20]'); t.ldr_lit(1, 'w_page'); t.a('ldr r1, [r0, r1]\ncmp r1, #0x0'); t.bne('ck_out')
    t.bl_label('FlipInfo'); t.a('cmp r0, #0x0'); t.beq('ck_out')
    t.ldr_lit(0, 'se'); t.bl(GFL_SndSEPlay); t.a('movs r0, #0x1\nbics r5, r0')
    t.label('ck_out'); t.a('adds r0, r5, #0x0\npop {r4, r5, r6, pc}')
    for name, v in (('n_sapphire', N_SAPPHIRE), ('w_page', W_PAGE), ('w_handle', W_HANDLE), ('page2_file', PAGE2_FILE),
                    ('se', SE_DEX_SELECT), ('flipping_addr', base)):
        t.word(name, v)
    return t.assemble(), dict(t.labels)


GFL_ArcSysReadHeapNewLZ, GFL_ArcToolReadHeapNewLZGetLen = 0x0204B4E4, 0x0204B610
SaveControl_GetInstance, SaveControl_GetEncountSave = 0x020072FC, 0x0200DCF0
F718, F73C, PARENT_ZONE = 0x0219F718, 0x0219F73C, 0x02160EB4   # ov144 records load / find by zone; ov012 the zone's parent
HABITAT_SIZE, SEASON_SIZE = 345, 86


def area_code(t, a):
    """The area page's ITCM functions (module docstring): DexLoadRecords, DexFindRecord(Safe), HabitatRead."""
    t.label('k_species'); t.out += struct.pack('<7H', *a['species']) + bytes(2)
    t.label('k_slot'); t.out += bytes(a['slot']); t.label('k_bits'); t.out += bytes(a['bits'])
    while len(t.out) % 4: t.out += b'\0'
    # DexLoadRecords(heap r0) -> the records (a/0/8/4 #21), as func_ov144_0219f718 loads a/0/8/5 #0
    t.label('DexLoadRecords')
    t.a('push {r3, lr}\nadds r3, r0, #0x0\nmovs r0, #0x54\nmovs r1, #0x15\nmovs r2, #0x0')
    t.bl(GFL_ArcSysReadHeapNewLZ); t.a('pop {r3, pc}')
    # DexFindRecord(records r0, zone r1) -> its record (town_map's zone table), 0xffff none
    t.label('DexFindRecord')
    t.ldr_lit(2, 'nzones'); t.a('cmp r1, r2'); t.bcc('hs', 'fr_none')
    t.ldr_lit(2, 'zt_off'); t.a('adds r2, r0, r2\nldrb r0, [r2, r1]\ncmp r0, #0xff'); t.beq('fr_none')
    t.a('bx lr')
    t.label('fr_none'); t.ldr_lit(0, 'ffff'); t.a('bx lr')
    # DexFindRecordSafe: the same, the filler record (off screen) instead of 0xffff
    t.label('DexFindRecordSafe')
    t.a('push {r4, lr}'); t.bl_label('DexFindRecord'); t.ldr_lit(1, 'ffff'); t.a('cmp r0, r1'); t.bne('frs_out')
    t.movs(0, a['filler'])
    t.label('frs_out'); t.a('pop {r4, pc}')
    # HabitatRead: ov298 func_ov298_021a5c14's GFL_ArcToolReadHeapNewLZGetLen(handle, species - 1, 0, heap, &len)
    # (r4 = the species in that function); then RoamerFix
    t.label('HabitatRead')
    t.a('push {r4, r5, lr}\nsub sp, #0x4\nldr r5, [sp, #0x10]\nstr r5, [sp, #0x0]')
    t.bl(GFL_ArcToolReadHeapNewLZGetLen)
    t.a('adds r1, r4, #0x0'); t.bl_label('RoamerFix')
    t.a('add sp, #0x4\npop {r4, r5, pc}')
    # RoamerFix(buf r0, species r1) -> buf: a roamer's habitat = its place now (roamers.c save layout)
    t.label('RoamerFix')
    t.a('push {r4, r5, r6, r7, lr}\nadds r4, r0, #0x0'); t.beq('rf_out')
    t.ldr_lit(2, 'a_species'); t.a('movs r3, #0x0')
    t.label('rf_find')
    t.a('lsls r5, r3, #0x1\nldrh r5, [r2, r5]\ncmp r5, r1'); t.beq('rf_found')
    t.a('adds r3, #0x1\ncmp r3, #0x7'); t.bcc('lo', 'rf_find'); t.b('rf_out')
    t.label('rf_found')
    t.a('adds r6, r3, #0x0\nmovs r0, #0x0\nmovs r2, #0x0'); t.ldr_lit(3, 'hsize')
    t.label('rf_clear'); t.a('strb r0, [r4, r2]\nadds r2, #0x1\ncmp r2, r3'); t.bcc('lo', 'rf_clear')
    t.a('movs r0, #0x1\nstrb r0, [r4, #0x0]')                       # one table for every season
    for s in range(4):                                               # every season: "area unknown"
        t.ldr_lit(2, f'season{s}'); t.a('strb r0, [r4, r2]')
    t.bl(SaveControl_GetInstance); t.bl(SaveControl_GetEncountSave)
    t.a('movs r1, #0x6\nmuls r1, r6\nadds r7, r0, r1\nldrh r0, [r7, #0x0]\ncmp r0, #0x0'); t.beq('rf_out')   # not roaming
    t.a('ldrb r0, [r7, #0x2]\ncmp r0, #0x14'); t.bcc('hs', 'rf_out')
    t.ldr_lit(1, 'a_slot'); t.a('ldrb r2, [r1, r0]'); t.ldr_lit(1, 'a_bits'); t.a('ldrb r3, [r1, r0]')
    t.a('movs r0, #0x0\nstrb r0, [r4, #0x1]\nadds r2, #0x2\nstrb r3, [r4, r2]')
    t.label('rf_out'); t.a('adds r0, r4, #0x0\npop {r4, r5, r6, r7, pc}')
    for name, v in (('nzones', a['nzones']), ('zt_off', a['zt_off']), ('ffff', 0xFFFF), ('hsize', HABITAT_SIZE),
                    ('a_species', t.labels['k_species']), ('a_slot', t.labels['k_slot']), ('a_bits', t.labels['k_bits']),
                    *[(f'season{s}', 1 + SEASON_SIZE * s) for s in range(4)]):
        t.word(name, v)
    if a.get('hlist'): hlist_code(t, a)


EventWork_FlagGet, EventWork_FlagSet, EventWork_GetWkPtr = 0x020191AC, 0x020191D8, 0x02019294
GameData_GetEventWork, GameData_GetBag, BagSave_GetItemCountByID = 0x02017394, 0x02017354, 0x02008538
SetTeleportZoneDiscover = 0x02154F30                    # ov012 (resident with the field)


def hlist_code(t, a):
    """HabitatVisited(eventWork, flag) and HabitatDiscover(gameData, zone) (Habitat list comment above)."""
    h = a['hlist']
    t.label('k_zone_place'); t.out += h['zone_place']
    while len(t.out) % 4: t.out += b'\0'
    # HabitatVisited(ev r0, flag r1) -> BOOL: VISITED_BASE + place = that place's bit, else EventWork_FlagGet
    t.label('HabitatVisited')
    t.ldr_lit(2, 'h_base'); t.a('cmp r1, r2'); t.bcc('lo', 'hv_flag')
    t.a('push {r4, lr}\nsubs r4, r1, r2\nlsrs r1, r4, #0x4'); t.ldr_lit(2, 'h_var'); t.a('adds r1, r1, r2')
    t.bl(EventWork_GetWkPtr)
    t.a('ldrh r0, [r0, #0x0]\nmovs r1, #0xf\nands r1, r4\nlsrs r0, r1\nmovs r1, #0x1\nands r0, r1\npop {r4, pc}')
    t.label('hv_flag'); t.ldr_lit(3, 'h_flagget'); t.a('bx r3')
    # HabitatDiscover(gameData r0, zone r1): SetTeleportZoneDiscover, then the zone's place is visited; HM03 / a rod
    # in the Bag set Black 2's surfing / fishing flags of the list
    t.label('HabitatDiscover')
    t.a('push {r4, r5, r6, lr}\nadds r4, r0, #0x0\nadds r5, r1, #0x0'); t.bl(SetTeleportZoneDiscover)
    t.ldr_lit(0, 'h_nzones'); t.a('cmp r5, r0'); t.bcc('hs', 'hd_items')
    t.ldr_lit(0, 'h_zone_place'); t.a('ldrb r6, [r0, r5]\ncmp r6, #0xff'); t.beq('hd_items')
    t.a('adds r0, r4, #0x0'); t.bl(GameData_GetEventWork)
    t.a('lsrs r1, r6, #0x4'); t.ldr_lit(2, 'h_var'); t.a('adds r1, r1, r2'); t.bl(EventWork_GetWkPtr)
    t.a('ldrh r1, [r0, #0x0]\nmovs r2, #0xf\nands r2, r6\nmovs r3, #0x1\nlsls r3, r2\norrs r1, r3\nstrh r1, [r0, #0x0]')
    t.label('hd_items')
    t.a('adds r0, r4, #0x0'); t.bl(GameData_GetBag); t.a('adds r6, r0, #0x0'); t.beq('hd_out')
    t.ldr_lit(1, 'h_hm03'); t.bl(BagSave_GetItemCountByID); t.a('cmp r0, #0x0'); t.beq('hd_rods')
    t.a('adds r0, r4, #0x0'); t.bl(GameData_GetEventWork); t.ldr_lit(1, 'h_surf'); t.bl(EventWork_FlagSet)
    t.label('hd_rods')
    for k, rod in enumerate(ITEM_RODS):
        t.a('adds r0, r6, #0x0'); t.ldr_lit(1, f'h_rod{k}'); t.bl(BagSave_GetItemCountByID); t.a('cmp r0, #0x0')
        t.bne('hd_fish')
    t.b('hd_out')
    t.label('hd_fish')
    t.a('adds r0, r4, #0x0'); t.bl(GameData_GetEventWork); t.ldr_lit(1, 'h_fish'); t.bl(EventWork_FlagSet)
    t.label('hd_out'); t.a('pop {r4, r5, r6, pc}')
    for name, v in (('h_base', VISITED_BASE), ('h_var', h['visited_var']), ('h_flagget', EventWork_FlagGet | 1),
                    ('h_nzones', len(h['zone_place'])), ('h_zone_place', t.labels['k_zone_place']), ('h_hm03', ITEM_HM03),
                    ('h_surf', FLAG_SURF_OK), ('h_fish', FLAG_FISH_OK), *[(f'h_rod{k}', r) for k, r in enumerate(ITEM_RODS)]):
        t.word(name, v)


def install_itcm(code, area=None):
    """Append the blob to ITCM after the code already there (hoenn_world, roamers, fairy, fairy_ui ...): itcm.bin grows,
    itcm.yaml's code_size and the arm9 literal of the ITCM arena start move past it (roamers.py / fairy_ui.py method)."""
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    base = ITCM_BASE + size
    p9 = os.path.join(code, 'arm9.bin'); arm9 = bytearray(open(p9, 'rb').read())
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not the end of ITCM'
    blob, sym = itcm_blob(base, area)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000
    struct.pack_into('<I', arm9, lit, end)
    save(p9, arm9)
    pi = os.path.join(code, 'itcm.bin'); itcm = open(pi, 'rb').read()
    assert len(itcm) == size
    save(pi, itcm + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    return base, len(blob), sym


def save(path, data):
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(data); os.replace(path + '.tmp', path)


def edit(code, n, addr, old, new):
    """Overlay n: the bytes at addr must be `old` (asm text or bytes); write `new` (bytes, same size)."""
    p = os.path.join(code, f'arm9_ov{n:03d}.bin'); d = bytearray(open(p, 'rb').read())
    o = addr - OV[n]
    old = asm(old) if isinstance(old, str) else old
    assert bytes(d[o:o + len(old)]) == old, f'ov{n:03d} {addr:#x}: {d[o:o + len(old)].hex()} != {old.hex()}'
    assert len(new) == len(old)
    d[o:o + len(new)] = new
    save(p, d)


AREA = {}                                   # habitat() -> apply_code(): the ITCM tables and the zone list


def apply_code(code):
    base, size, sym = install_itcm(code, AREA or None)
    out = [f'ITCM {base:#x} ({size} B)']
    # ov296 work struct: +0x2b4 must be ours (fairy_ui's struct 0x328 leaves +0x2b4..+0x2df free; else grow by 4)
    p = os.path.join(code, 'arm9_ov296.bin'); d = open(p, 'rb').read()
    o = 0x0219D770 - OV[296]
    if d[o:o + 2] == asm('movs r5, #0xad'):
        edit(code, 296, 0x0219D770, 'movs r5, #0xad', asm('movs r5, #0xae'))
        out.append('ov296 work 0x2b4 -> 0x2b8')
    else:
        assert d[o:o + 2] == asm('movs r5, #0xca'), f'ov296 work size: {d[o:o + 2].hex()}'
        out.append('ov296 work 0x328 (fairy_ui): +0x2b4 in its free gap')
    edit(code, 296, 0x0219E350, 'movs r3, #0x1e\nlsls r3, r3, #0x4', bl(0x0219E350, sym['HookPrint']))
    edit(code, 298, 0x021A2CCC, 'ldr r0, [sp, #0x8]\nadd sp, #0x10', bl(0x021A2CCC, sym['InfoKeys']))
    edit(code, 297, 0x021F4420, bl(0x021F4420, GCTX_HIDGetPressedKeys), bl(0x021F4420, sym['CaptureKeys']))
    out.append('page flip: ov296 0x0219e350, ov298 0x021a2ccc, ov297 0x021f4420')
    if AREA:
        out.append(area_calls(code, sym))
    return ', '.join(out)


ZONE_LIST = 0x021AC544                      # ov298 data_ov298_021ac544: 85 u16 zones (habitat index = position)


def area_calls(code, sym):
    """The area page's call sites (module docstring) and ov298's zone list."""
    for n, at in ((298, 0x021A3332), (303, 0x021A1AC6), (308, 0x0219FC92)):
        edit(code, n, at, bl(at, F718), bl(at, sym['DexLoadRecords']))
    for n, at in ((298, 0x021A47FA), (303, 0x021A2D42), (303, 0x021A3008)):   # r1 = the zone: no Unova parent
        edit(code, n, at, bl(at, PARENT_ZONE), asm('adds r0, r1, #0x0\nnop'))
    for n, at, fn in ((298, 0x021A4804, 'DexFindRecord'), (303, 0x021A2D4C, 'DexFindRecordSafe'),
                      (303, 0x021A3012, 'DexFindRecord'), (308, 0x021A10CE, 'DexFindRecord')):
        edit(code, n, at, bl(at, F73C), bl(at, sym[fn]))
    edit(code, 298, 0x021A5C26, bl(0x021A5C26, GFL_ArcToolReadHeapNewLZGetLen), bl(0x021A5C26, sym['HabitatRead']))
    if AREA.get('hlist'):
        hlist_calls(code, sym)
    p = os.path.join(code, 'arm9_ov298.bin'); d = bytearray(open(p, 'rb').read())
    o = ZONE_LIST - OV[298]
    assert struct.unpack_from('<3H', d, o) == (389, 397, 6), 'ov298 zone list'
    struct.pack_into('<85H', d, o, *AREA['zones'])
    save(p, d)
    return 'area page: Hoenn records, zone table, habitat zones, roamers'


def hlist_calls(code, sym):
    """The Habitat list's four place tables, its visited checks, the zone-entry hook and the unknown-zone page."""
    h = AREA['hlist']
    rows = [(VISITED_BASE + i, z, i, 0) for i, z in enumerate(h['places'])]
    rows += [(VISITED_BASE + i, 0xFFFF, HLIST_FILES - 1, 0) for i in range(len(rows), HLIST_PLACES)]
    for n, at in TABLES.items():
        p = os.path.join(code, f'arm9_ov{n:03d}.bin'); d = bytearray(open(p, 'rb').read())
        o = at - OV[n]
        assert d[o:o + 6] == bytes.fromhex('b809ab011800'), f'ov{n:03d} Habitat list table at {at:#x}'
        d[o:o + 6 * HLIST_PLACES] = b''.join(struct.pack('<HHBB', *r) for r in rows)
        save(p, d)
    for n, at in ((302, 0x021AD95E), (302, 0x021ADB3E), (302, 0x021ADB98), (302, 0x021ADE32), (298, 0x021A62E6)):
        edit(code, n, at, bl(at, EventWork_FlagGet), bl(at, sym['HabitatVisited']))
    for n, at in ((35, 0x0217E57E), (36, 0x02180CD8)):
        edit(code, n, at, bl(at, SetTeleportZoneDiscover), bl(at, sym['HabitatDiscover']))
    edit(code, 302, 0x021ADD96, 'movs r0, #0x18', asm(f'movs r0, #{HLIST_FILES - 1}'))
    return 'Habitat list'


def apply(files):
    return habitat(files)


# ---------------------------------------------------------------------------------------------------- area data

ARC_HABITAT, ARC_DEX_GFX, ARC_ENC = 176, 157, 127
GFX_NCLR, GFX_NCGR, GFX_NCER, GFX_NANR = 5, 15, 29, 46      # a/1/5/7: the area page's highlight sprites (ov298, ov303)
ENC_TABLE = 8 + 56 * 4                                      # a/1/2/7: rates (8 B) + 56 slots (u16 species | form << 11, 2 levels)
GROUPS = [0] * 12 + [1] * 12 + [2] * 12 + [3] * 5 + [4] * 5 + [5] * 5 + [6] * 5   # slot -> group (habitat bit 1 << group)
HIDDEN = ('WYNAUT',)                                        # pokeruby sSpeciesHiddenFromAreaScreen
N_FILES = 684                                               # a/1/7/6: species 1-649, then the forms


def _tm():
    import importlib.util
    spec = importlib.util.spec_from_file_location('town_map_dex', os.path.join(HERE, 'town_map.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _species():
    out = {}
    for line in open(os.path.join(ROOT, 'external', 'pokebw2', 'include', 'constants', 'species.h')):
        m = re.match(r'#define SPECIES_(\w+)\s+(\d+)\s*$', line)
        if m: out[m.group(1)] = int(m.group(2))
    return out


def zone_bits(files, ztab):
    """{zone: [4 seasons x {species: habitat bits}]} of every zone with a Hoenn encounter table in the built a/1/2/7
    (data/hoenn_encounters.json's files; zone headers' encounter file) and a place on the map (town_map zone table)."""
    import json, narcio, zoneheaders
    hoenn_files = set(json.load(open(os.path.join(ROOT, 'data', 'hoenn_encounters.json'))).values())
    headers, _ = zoneheaders.load(files)
    enc = narcio.load(files, ARC_ENC)
    out = {}
    for z, h in enumerate(headers):
        f = h['encounters']
        if f not in hoenn_files or z >= len(ztab) or ztab[z] == 0xFF: continue
        data = enc[f]
        n = len(data) // ENC_TABLE
        assert n in (1, 4) and len(data) == n * ENC_TABLE, (z, f, len(data))
        seasons = []
        for s in range(4):
            t = data[ENC_TABLE * (s if n == 4 else 0):]
            bits = {}
            for k in range(56):
                sp = struct.unpack_from('<H', t, 8 + 4 * k)[0] & 0x7FF
                g = GROUPS[k]
                if g == 6: g = 5         # (rods_fix) rippling-fishing slots = the Old/Good Rod's: fishing, by its rate
                if sp and t[g]: bits[sp] = bits.get(sp, 0) | 1 << g
            seasons.append(bits)
        out[z] = seasons
    return out


def habitat(files):
    """a/1/7/6 from the game's Hoenn encounter tables, a/1/5/7's highlight art, and the tables apply_code needs."""
    import narcio
    tm = _tm()
    f21 = tm.read_file21(files)
    recs, ztab = f21['records'], f21['zone_table']
    assert len(recs) == 85, len(recs)
    rzones = [r[0] for r in recs]
    slot_of = [rzones.index(z) for z in rzones]                # habitat index of each record (its zone's first record)
    sp = _species()
    hidden = {sp[s] for s in HIDDEN}
    # species -> 4 seasons x 85 habitat bytes
    hab = {}
    zb = zone_bits(files, ztab)
    for z, seasons in zb.items():
        k = slot_of[ztab[z]]
        for s, bits in enumerate(seasons):
            for spc, b in bits.items():
                if spc in hidden: continue
                hab.setdefault(spc, [[0] * 85 for _ in range(4)])[s][k] |= b
    entries = narcio.load(files, ARC_HABITAT)
    assert len(entries) == N_FILES and all(len(e) == HABITAT_SIZE for e in entries)
    new = []
    for i in range(N_FILES):
        seasons = hab.get(i + 1) if i < 649 else None
        d = bytearray(HABITAT_SIZE)
        d[0] = 1
        for s in range(4):
            d[1 + SEASON_SIZE * s] = 1
        if seasons:
            d[0] = 1 if all(seasons[s] == seasons[0] for s in range(4)) else 0
            for s in range(4):
                if any(seasons[s]): d[1 + SEASON_SIZE * s] = 0
                d[2 + SEASON_SIZE * s:2 + SEASON_SIZE * s + 85] = bytes(seasons[s])
        new.append(bytes(d))
    narcio.save(files, ARC_HABITAT, new)
    art = highlight_art(files, tm)
    # roamers (roamers.py): species and, per Sapphire roamer location, its route's habitat index and walking/surfing bits
    import importlib.util
    spec = importlib.util.spec_from_file_location('roamers_dex', os.path.join(HERE, 'roamers.py'))
    ro = importlib.util.module_from_spec(spec); spec.loader.exec_module(ro)
    names, _, _ = ro.locations()
    zones = __import__('json').load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    slots, bits = [], []
    for name in names:
        z = zones[name]['zone']
        assert z < len(ztab) and ztab[z] != 0xFF, name
        slots.append(slot_of[ztab[z]])
        groups = 0
        for bb in zb.get(z, [{}])[0].values(): groups |= bb
        bits.append((groups & 0x01) | (groups & 0x08) or 0x01)   # grass and / or water (roamers: random encounters)
    AREA.update(zones=rzones, filler=84, nzones=len(ztab), zt_off=_zt_off(files, tm),
                species=[sp[s] for s, _ in ro.ROAMERS], slot=slots, bits=bits)
    hl = habitat_list(files, tm, hab, slot_of, rzones, ztab)
    found = sum(1 for i in range(1, 387) if i in hab)
    return (f'habitat: {found} species of 1-386 found on the Hoenn map ({len(zb)} zones with tables); {art}; '
            f'roamers {[s for s, _ in ro.ROAMERS]} on {len(names)} routes; {hl}')


# ---------------------------------------------------------------------------------------------------- Habitat list
# Black 2's Habitat list (the Pokédex's HABITAT button after the National Dex; external/pokebw2 src/ov036/scrcmd_ochiba.c
# has the data types) [code: ov302 func_ov302_021adae8 builds the list, func_ov302_021ade10 counts it, func_ov302_021ad8e0
# / 021ad80c the pages; ov303 shows a place]:
# - 57 places in one table, copied in four overlays (ov302 data_ov302_021ae41c, ov303 data_ov303_021a3414, ov298
#   data_ov298_021ac5f0, ov036 HABITAT_LIST_HEADERS): u16 visited flag, u16 zone (its place name, the map highlight,
#   the AREA page's link), u8 page, u8 0. A place is listed when its flag is set (Black 2: the respawn table's discovery
#   flags, set on entering a zone, src/ov012/respawn_zone.c) and its page has a kind the player can use: walking
#   always, surfing with flag 0x987, fishing with flag 0x985 (func_ov302_021add4c; Black 2's scripts 0664/0792 set them
#   with HM Surf and the Super Rod).
# - Pages a/2/9/6 (296), one per place: 8 bytes (0 seasonal, 1-2 0, 3/4/5 walking/surfing/fishing present, 6 the
#   picture: 0 field, 1 desert, 2 marsh, 3 cave, 4 bridge, 5 mountain/tower, 6 water; 7 0), u16 count (<= 30), 28-byte
#   entries: u16 species, u8 [4 seasons][walking, surfing, fishing], 14 bytes 0. The screens count seen / caught per
#   kind from these (func_ov302_021adc78) and keep a stamp per place and kind in the Medal Box (+74 + place).
# Hoenn: the places are the map sections with wild Pokémon in this build (Sapphire's region-map order); Ever Grande
# City's water is left out (58 sections, 57 places: every one of its Pokémon/kinds is also on Route 128 next to it).
# Pages from the AREA page's own habitat data (same species, same kinds). Visited: 57 bits in works
# VAR_HABITAT_VISITED_0-3 (src/include/hoenn.h: the free flags are all taken), set by HabitatDiscover on every zone
# entry (both callers of SetTeleportZoneDiscover: ov035 0x0217e57e map changes, ov036 0x02180cd8 walking into a zone)
# for the zone's place (town_map's zone table: rooms and caves count for their town / cave); the table's flag field
# is 0xf000 + place and the five reads of it (ov302 0x021ad95e, 0x021adb3e, 0x021adb98, 0x021ade32, ov298 0x021a62e6)
# call HabitatVisited. HabitatDiscover also sets 0x987 when the Bag holds HM03 and 0x985 with any rod (Black 2's
# meaning of the two flags). The unknown-zone page of func_ov302_021add74 (Black 2's page 24) is the empty filler.
ARC_HLIST, HLIST_PLACES, HLIST_FILES, HLIST_MAX = 296, 57, 58, 30
HLIST_LEFT_OUT = ('MAPSEC_EVER_GRANDE_CITY',)
HLIST_PICTURE = {**{s: 3 for s in ('GRANITE_CAVE', 'METEOR_FALLS', 'RUSTURF_TUNNEL', 'VICTORY_ROAD', 'SHOAL_CAVE',
                                   'SEAFLOOR_CAVERN', 'CAVE_OF_ORIGIN', 'ALTERING_CAVE', 'FIERY_PATH', 'NEW_MAUVILLE',
                                   'ABANDONED_SHIP')},
                 **{s: 5 for s in ('MT_PYRE', 'SKY_PILLAR', 'JAGGED_PASS', 'MT_CHIMNEY')}, 'ROUTE_111': 1}
VISITED_BASE = 0xF000                       # table flag field: VISITED_BASE + place (HabitatVisited)
FLAG_SURF_OK, FLAG_FISH_OK = 0x987, 0x985
ITEM_HM03, ITEM_RODS = 422, (445, 446, 447)  # Old, Good, Super Rod
TABLES = {302: 0x021AE41C, 303: 0x021A3414, 298: 0x021AC5F0, 36: 0x021D49B8}
OV[36], OV[302], OV[35] = 0x0217F600, 0x021ACEE0, 0x0217C940


def habitat_list(files, tm, hab, slot_of, rzones, ztab):
    """a/2/9/6 = one page per Hoenn place (+ the empty filler), and AREA['hlist'] for apply_code."""
    import json, narcio
    from b2files import arc_path
    spec = __import__('importlib.util').util.spec_from_file_location('hoenn_dex_order', os.path.join(HERE, 'hoenn_dex.py'))
    hd = __import__('importlib.util').util.module_from_spec(spec); spec.loader.exec_module(hd)
    dex = {n: i for i, n in enumerate(hd.hoenn_order())}
    locs = tm.locations(); locs = locs + [tm.dummy_record(locs)] * (tm.NREC - len(locs))
    order = [x['id'] for x in json.load(open(os.path.join(ROOT, 'external', 'pokeruby', 'src', 'data', 'region_map',
                                                          'region_map_sections.json')))['map_sections']]
    sec_slot = {}
    for r, l in enumerate(locs):
        if l['mapsec'] and slot_of[r] == r: sec_slot.setdefault(l['mapsec'], r)
    used = {k for spc in hab.values() for k in range(85) if spc[0][k]}
    secs = sorted((sec for sec, k in sec_slot.items() if k in used and sec not in HLIST_LEFT_OUT),
                  key=lambda sec: order.index(sec) if sec in order else len(order))
    assert len(secs) <= HLIST_PLACES, (len(secs), secs)
    pages, places = [], []
    for i, sec in enumerate(secs):
        k = sec_slot[sec]
        ents = []
        for spc in sorted(hab, key=lambda n: (dex.get(n, 999), n)):
            b = hab[spc][0][k]
            if not b: continue
            kinds = bytes([int(bool(b & 0x07)), int(bool(b & 0x18)), int(bool(b & 0x60))])
            ents.append(struct.pack('<H', spc) + kinds * 4 + bytes(14))
        assert 0 < len(ents) <= HLIST_MAX, (sec, len(ents))
        have = [any(e[2 + j] for e in ents) for j in range(3)]
        pic = HLIST_PICTURE.get(sec[7:], 6 if not have[0] else 0)
        pages.append(bytes([0, 0, 0, *map(int, have), pic, 0]) + struct.pack('<H', len(ents)) + b''.join(ents))
        places.append((rzones[k], k))
    pages += [bytes(8) + struct.pack('<H', 0)] * (HLIST_FILES - len(pages))
    path = arc_path(files, ARC_HLIST); size = os.path.getsize(path)
    assert len(narcio.load(files, ARC_HLIST)) == HLIST_FILES
    narcio.save(files, ARC_HLIST, pages)
    d = open(path, 'rb').read()
    open(path + '.tmp', 'wb').write(tm._pad_narc(d, size)); os.replace(path + '.tmp', path)
    place_of_slot = {k: i for i, (_, k) in enumerate(places)}
    zone_place = bytes(place_of_slot.get(slot_of[ztab[z]], 0xFF) if ztab[z] != 0xFF else 0xFF for z in range(len(ztab)))
    AREA['hlist'] = dict(places=[z for z, _ in places], zone_place=zone_place, names=[sec[7:] for sec in secs],
                         visited_var=_hoenn_h('VAR_HABITAT_VISITED_0'))
    return (f'Habitat list: {len(places)} places ({", ".join(sec[7:].title() for sec in secs[:3])} ...), '
            f'{sum(struct.unpack_from("<H", p, 8)[0] for p in pages)} entries; a/2/9/6 {len(d)} -> {size} B')


def _hoenn_h(name):
    t = open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()
    return int(re.search(rf'#define\s+{name}\s+(0x[0-9A-Fa-f]+|\d+)', t).group(1), 0)


def _zt_off(files, tm):
    import narcio
    d = narcio.load(files, tm.ARC_GFX)[tm.NEW_FILE]
    i = d.rfind(b'TMAP')
    return struct.unpack_from('<6H', d, i + 4)[1]


def highlight_art(files, tm):
    """a/1/5/7 entries 5, 15, 29, 46: Sapphire's area glow and marker as one cell + anim per town_map.dex_highlights
    shape. The NARC keeps its size (padded)."""
    import narcio, title_art as ta
    from b2files import arc_path
    from PIL import Image
    path = arc_path(files, ARC_DEX_GFX); size = os.path.getsize(path)
    e = narcio.load(files, ARC_DEX_GFX)
    locs = tm.locations()
    locs = locs + [tm.dummy_record(locs)] * (tm.NREC - len(locs))
    _, shapes = tm.dex_highlights(locs)
    gfx = os.path.join(ROOT, 'external', 'pokeruby', 'graphics', 'pokedex')
    glow = Image.open(os.path.join(gfx, 'area_glow.png')); gpal = glow.getpalette()
    marker = Image.open(os.path.join(gfx, 'area_marker.png')); mpal = marker.getpalette()
    gp = glow.load(); mp = marker.load()
    # colours: palette 0 of NCLR 5 (Black 2's highlights used 6-8; 1-5 unused): 1 = the glow, 2-4 = the marker's reds
    tile10 = [gp[x, 32 + y] for y in range(8) for x in range(8)]          # area_glow tile 0x10 (4 tiles a row)
    assert set(tile10) == {1}, set(tile10)
    used_m = sorted({mp[x, y] for y in range(16) for x in range(16)} - {0})
    assert used_m == [2, 3, 4], used_m
    cols = ta.nclr_colours(e[GFX_NCLR])
    cols[1] = tuple(gpal[3:6])
    for i in used_m: cols[i] = tuple(mpal[3 * i:3 * i + 3])
    nclr = ta.nclr_build(e[GFX_NCLR], cols)
    # tiles (4bpp, 1D 128K: an OAM's tile number counts 128-byte units = 4 tiles): unit 0 = 4 glow tiles (every fill
    # OBJ is at most 4 tiles: 8x8, 16x8, 32x8, 8x16, 8x32), unit 1 = the marker (16x16, tiles in 1D order)
    def t4(px): return bytes(px[i] | px[i + 1] << 4 for i in range(0, 64, 2))
    raw = t4(tile10) * 4
    for ty in range(2):
        for tx in range(2):
            raw += t4([mp[tx * 8 + x, ty * 8 + y] for y in range(8) for x in range(8)])
    old = e[GFX_NCGR]
    th, tw, depth, mapping, tiled, dsize, doff = struct.unpack_from('<HHIIIII', old, 0x18)
    assert depth == 3 and doff == 0x18 and (th, tw) == (0xFFFF, 0xFFFF)
    rahc = bytearray(old[0x10:0x10 + 0x20]) + raw
    struct.pack_into('<I', rahc, 4, len(rahc)); struct.pack_into('<I', rahc, 0x18, len(raw))
    ncgr = tm._nitro(old, [bytes(rahc)])
    # cells: one per shape; OBJs semi-transparent (mode 1) like Black 2's town / landmark dots
    SIZES = {(8, 8): (0, 0), (16, 8): (1, 0), (32, 8): (1, 1), (8, 16): (2, 0), (8, 32): (2, 1), (16, 16): (0, 1)}
    def split(n):                                          # a run of n tiles -> OBJ lengths in tiles (<= 4)
        out = []
        while n:
            k = 4 if n >= 4 else 2 if n >= 2 else 1
            out.append(k); n -= k
        return out
    cells = []
    for sh in shapes:
        if sh[0] == 'marker':
            cells.append([(0, 0, 16, 16, 1)])
            continue
        _, w, h = sh
        assert w == 1 or h == 1, sh
        objs, pos = [], 0
        for k in split(max(w, h)):
            objs.append((pos, 0, 8 * k, 8, 0) if h == 1 else (0, pos, 8, 8 * k, 0)); pos += 8 * k
        cells.append(objs)
    ncer0 = e[GFX_NCER]
    secs = tm._sections_of(ncer0)
    m, ko, ksz = secs[0]; assert m == b'KBEC'
    kb = ncer0[ko:ko + ksz]
    n0, attr, co = struct.unpack_from('<HHI', kb, 8)
    assert attr & 1 and co == 0x18
    table, oams = bytearray(), bytearray()
    for objs in cells:
        xs = [o[0] for o in objs] + [o[0] + o[2] for o in objs]; ys = [o[1] for o in objs] + [o[1] + o[3] for o in objs]
        rad = min(63, int((max(xs) ** 2 + max(ys) ** 2) ** 0.5 / 4) + 2)
        table += struct.pack('<HHIhhhh', len(objs), 0x800 | rad, len(oams), max(xs) - 1, max(ys) - 1, min(xs), min(ys))
        for x, y, w, h, unit in objs:
            shape, sz = SIZES[(w, h)]
            oams += struct.pack('<HHH', shape << 14 | 1 << 10 | (y & 0xFF), sz << 14 | (x & 0x1FF), unit)
    while len(oams) % 4: oams += b'\0'
    head = bytearray(kb[8:8 + co]); struct.pack_into('<H', head, 0, len(cells))
    kb_new = struct.pack('<4sI', b'KBEC', 8 + len(head) + len(table) + len(oams)) + bytes(head + table + oams)
    ncer = tm._nitro(ncer0, [kb_new] + [ncer0[o:o + sz] for _, o, sz in secs[1:]])
    # anims: one one-frame anim per cell (Black 2's own form: u32 1 frame, u16 0, u16 1, u32 2, u32 frame offset)
    nanr0 = e[GFX_NANR]
    secs = tm._sections_of(nanr0)
    m, ao, asz = secs[0]; assert m == b'KNBA'
    ab = nanr0[ao:ao + asz]
    nA, nF, aoff, foff, poff = struct.unpack_from('<HHIII', ab, 8)
    proto = ab[8 + aoff:8 + aoff + 16]
    anims, frames, pos = bytearray(), bytearray(), bytearray()
    for k in range(len(cells)):
        a = bytearray(proto); struct.pack_into('<I', a, 12, len(frames)); anims += a
        frames += struct.pack('<IHH', len(pos), 4, 0xBEEF)
        pos += struct.pack('<HH', k, 0xCCCC)
    head = bytearray(ab[8:8 + aoff])
    struct.pack_into('<HHIII', head, 0, len(cells), len(cells), aoff, aoff + len(anims), aoff + len(anims) + len(frames))
    ab_new = struct.pack('<4sI', b'KNBA', 8 + len(head) + len(anims) + len(frames) + len(pos)) + bytes(head + anims + frames + pos)
    nanr = tm._nitro(nanr0, [ab_new] + [nanr0[o:o + sz] for _, o, sz in secs[1:]])
    e[GFX_NCLR], e[GFX_NCGR], e[GFX_NCER], e[GFX_NANR] = nclr, ncgr, ncer, nanr
    narcio.save(files, ARC_DEX_GFX, e)
    d = open(path, 'rb').read()
    open(path + '.tmp', 'wb').write(tm._pad_narc(d, size)); os.replace(path + '.tmp', path)
    return f'a/1/5/7: {len(cells)} highlight cells (Sapphire\'s glow and marker), {len(d)} -> {size} B'
