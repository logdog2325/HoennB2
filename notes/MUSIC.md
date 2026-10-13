# Hoenn music on Black 2's instruments (music_check, 2026-10-08)

Goal (user, notes/DECISIONS.md 2026-10-08): Hoenn's songs, from pokeruby / the user's Sapphire dump, played by Black 2's
own sound engine and instruments, like a Gen 5 remix. This check converted Littleroot Town (and the wild battle) and
plays them in game behind a build flag. Everything below was read from the decomp's data and code
(external/pokebw2), pokeruby / pokeemerald, the two ROM dumps, or measured in DeSmuME; nothing was downloaded.

Files: `b2tools/sdat.py` (sound archive reader/writer), `b2tools/sseq.py` (sequences), `b2tools/m4a.py` (GBA songs),
`b2tools/m4a_to_sseq.py` (the converter), `b2tools/m4a_render.py` (GBA reference render), `b2tools/music_voices.py`
(instrument comparison), `data/hoenn_music.json` (the mapping), `b2tools/patches/hoenn_music.py` (the flag),
`work/agents/music_check/scripts/` (test, recording and measurement scripts). Listening files: screenshots/music_check/.

## 1. How Black 2 stores and plays music

### The sound archive
`files/swan_sound_data.sdat` (NitroFS file 346, ROM 0x379600-0x58b4f60, 89,373,024 B; not a NARC, not in build_rom
RESERVE). NitroSDK SDAT, checked by parsing it and by `python3 b2tools/sdat.py --selftest` (rebuilding it from the parse
gives the same bytes):
- header 0x40: 'SDAT', size, then (offset, size) of SYMB 64 / 123,745, INFO 123,812 / 76,528, FAT 200,340 / 83,164,
  FILE 283,504 (blocks back to back; files 32-byte aligned; the archive ends padded to 32).
- SYMB: names (the decomp's include/constants/sound.h comes from it). The game never loads them.
- INFO: per kind a record (u32 count, u32 entry offsets; 0 = no entry) followed by its entries. 2,416 sequences (1,026
  ids empty, e.g. 4-999), 2,290 banks and 2,290 wave archives (341 empty each), 7 players, 5 groups, 1 stream player,
  1 stream. Entries: SEQ {u32 file, u16 bank, u8 volume, u8 channel prio, u8 player prio, u8 player, u16 0} 12 B;
  BANK {u32 file, u16 wave archive[4]} 12 B; WAVEARC {u32 file (24 bits) + flags} 4 B (flags 0 everywhere in Black 2);
  PLAYER {u8 max seqs, u8, u16 channel mask, u32 heap} 8 B; GROUP {u32 n, n x (u8 type, u8 load, u16, u32 id)}.
- FAT: 'FAT ', size, count (5,197), 16 B per file (offset from the SDAT start, size, 8 reserved).
- Each BGM has its own bank and its own wave archive: SEQ_BGM_T_01 (Nuvema, what Littleroot plays) = 7,544 B
  sequence + BANK_MUS_WB_T_01 564 B + WAVE_MUS_WB_T_01 195,080 B. The banks hold only the instruments that song uses,
  under fixed program numbers: `BANK_MUS_WB_SOUNDLIST` (bank 1000, 78 programs, wave archive 1000 = 2,509,004 B; no
  sequence uses it) is the whole Black/White instrument set, and Black/White's songs copy instruments from it with the
  same numbers and the same waves (checked wave by wave: `work/agents/music_check/scripts/bankmap.py`). Black 2's new
  songs (SEQ_BGM_SW_*, PWT) bring new samples with other numbers.

Players (INFO): 0 PLAYER_BGM (1 sequence, channels 0xBFFE = 1-13 and 15, no own heap), 1-3 and 5 SE players (channels
12-15, 10,200 B heap each), 4 PLAYER_SE_PSG (0xB800, 2,000 B), 6 PLAYER_BGM2 (all 16 channels; title, ending, Pokémon
theme). BGM sequences use channel priority 30, player priority 64. The DS has 16 channels (8-13 can also play PSG squares,
14-15 noise); a sequence has at most 16 tracks; SE share channels 12-15 with the BGM by priority.

### SSEQ, SBNK, SWAR (as Black 2's files use them; b2tools/sseq.py, sdat.py parse_sbnk/parse_swar)
- SSEQ: 'SSEQ' header 0x10, 'DATA' block with data offset 0x1C; 48 ticks per quarter note. Track 0 starts with
  FE (track mask) and 93 (open track n at offset); then per track Black 2's songs set C7 0 (note-wait off: notes overlap,
  80 waits separate them), E1 tempo, 81 program, C1 volume, C0 pan, D5 expression, C5 bend range (12), C6 priority (64),
  CA/CB/CC/CD/E0 modulation; notes are key, velocity, var-length length; 94 jumps back to the loop label. All tracks of
  a Black 2 BGM loop at the same tick (T_01: 576 -> 3456).
- SBNK: 'DATA' block, u32 count, 4-byte records {type, u16 offset, pad}: 1 PCM, 2 PSG square (wave = duty), 3 noise,
  16 drum set (low key, high key, one 12-byte entry per key), 17 key split (8 top keys, one entry per region). Entry: u16
  type, u16 wave, u16 wave-archive slot, base key, attack, decay, sustain, release, pan. (Black 2 aligns entries to 2
  bytes; build_sbnk aligns to 4: same parse.)
- SWAR: 'DATA' block, u32 count, u32 offsets; each wave: u8 encoding (0 PCM8, 1 PCM16, 2 IMA-ADPCM: 8,024 of Black 2's
  8,714 music/SE waves), u8 loop, u16 rate, u16 timer, u16 loop start (words), u32 length (words), data.
  `build_swar(parse_swar(x)) == x` for all 1,949 archives.
- Volume curves, measured in game (scripts/curve_test.py, one string note): velocity, track volume (C1) and expression
  (D5) each follow 40 log10(v/127) (64 -> -11.9 dB, 32 -> -23.9 dB); the sequence's INFO volume is linear (68 -> 82 =
  x1.20 in amplitude).

### Memory per sequence: the sound heap
GFL_SndInit (arm9 0x02005b80) makes one NNS frame heap of 0x9D000 = 643,072 B at 0x0209e278 (static, arm9 .bss) and
loads the archive's INFO and FAT into it (about 160 KB, at boot: in RAM for good). The BGM loader (func_02005980) loads
sequence + bank, then the wave archives, at the BGM stack's heap level (28-byte entries at 0x0209da7c). Measured in game
(NNS frame heap header, scripts/soundheap.py):
| where (state) | heap used | free |
|---|---|---|
| Littleroot, T_01 (203,188 B) loaded (work/emu/base_littleroot) | 564,428 | 78,580 |
| Route 101, R_A (214,268 B) (playthrough s05_route101) | 575,468 | 67,540 |
| Route 101 battle (playthrough t_battle1) | 587,660 | 55,348 |
| a wild battle, VS_NORAPOKE (239,596 B) (playthrough t_wild1) | 609,132 | 33,876 |
| the same Route 101 battle with the converted Hoenn wild battle (131,456 B) | 500,972 | 142,036 |
So everything except the BGM takes ~361 KB and one BGM has ~282 KB; in battle the battle BGM takes the field BGM's
place (used rises by about the difference, not the sum). Black 2's largest BGMs: ending 279,092 (BGM2 player), Kyurem
battles 258,868, field max D_04 249,408. **Rule for converted songs: footprint (SSEQ + SBNK + SWAR) no larger than the
Black 2 song whose place it takes** (Littleroot 179,872 B vs T_01 203,188; wild battle 131,456 vs 239,596).

### Which track plays
- Zone headers (a/0/1/2, 0x30 B each, b2tools/zoneheaders.py) have four BGM fields at +12/+14/+16/+18, one per season
  (DecideZoneHeaderBGMID 0x02018968: spring, summer, autumn, winter). patches/hoenn_season.py fixes the season to summer,
  so **bgm1 is what plays in Hoenn**; the other three are free.
- GetMapBGMIDByPlayerState (0x02030164): an override table first (GetZoneBGMOverrideID: 14 {flag, zone} at 0x02092238 ->
  BGM at 0x0209223c; Funfest -> SEQ_BGM_FES), then surfing -> 1013 SEQ_BGM_NAMINORI and cycling -> 1012
  SEQ_BGM_BICYCLE when the zone flag (header +30 bit 14) allows it, else the zone header.
- Interactive Sound System: a/0/8/6 file 0 = u8 count (44), {u16 seq, u8 type}; BGMInfo_GetISSSubsystem returns 0
  for a sequence not listed. Types (ISS_SUBSYSTEM_FUNCS 0x02092744): 2 road (25 route BGMs incl. R_A: tracks 8-9, mask
  0x300, fade up 8 per frame while the player moves and down while still), 3 city (positional emitters), 4 3D sound,
  5 dungeon, 7 switch (T_02, gyms, Battle Subway), 8 zone. T_01 is not listed. **A converted song must sit in an id
  that is not listed** (or the entry is removed), else the ISS mutes or fades its tracks.
- Battles: BtlSetup_LoadGameData (0x0201802a) sets 0x468 SEQ_BGM_VS_NORAPOKE and win 0x47C SEQ_BGM_WIN1 for every
  battle; BtlSetup_LoadTrainer sets the win BGM by class group (WIN2-WIN6); trainer battle BGM: SPECIAL_TRAINER_CLASSES
  (0x020922bc, 29 x {class, group, pedestal}) -> SPECIAL_TRAINER_BGM (ov036 0x021d28e4: VS_GYMLEADER, VS_SHITENNO,
  VS_SHIRONA, VS_HUE, VS_TRAINER, ...), class eye music u16 at 0x02092396 + 4 x class (EYE_01-EYE_13); scripts have
  s0090 TrainerBGMPlay, s008B/s008F (push), s0098 BGMPlay. Black 2 already has remixes of Hoenn's gym leader and
  champion battles (SEQ_BGM_VS_RS_LEADER, VS_RS_CHAMP, PWT).
- ME (jingles: SEQ_ME_LVUP, ITEM, KEYITEM, POKEGET, BADGE, ASA ...) are short sequences on the BGM player (push/pop).

### New sequences: add, or replace in place
- Adding is possible: INFO has empty ids (1,026 sequences, 341 banks / wave archives) and the record counts can grow;
  `SDAT.build(new_files=..., entries=...)` writes them. Costs: every INFO entry and FAT entry also lives in the sound
  heap (12 B per sequence or bank, 4 per wave archive, 16 per file), and the SDAT grows, which moves every later file of
  the ROM (the SDAT is the first NitroFS file after the banner): a new ROM layout, so all savestates are remade once
  (make_states.py). The ROM has room: 0x14d7fa00 = 349 MB used of 512 MB.
- In place (what HOENN_MUSIC=hoenn does): a song goes into a Black 2 sequence slot the Hoenn game never plays; the slot's
  sequence, bank and wave archive keep their INFO entries, their three FAT entries point into the byte range of the
  slot's old wave archive. **Nothing moves**: the SDAT keeps its size, INFO and FAT their sizes, every other file its
  offset; rom_layout_diff.py reports LAYOUT IDENTICAL between v15.2 and v15.2 + Hoenn music (only the SDAT's bytes
  and 8 bytes of a/0/1/2 differ). Each slot holds as much as its old wave archive (~190-240 KB for a BGM).
- Savestates keep the old INFO/FAT in RAM: new music needs a cold boot (Continue from the battery save is enough), or
  scripts/battle_test.py's in-RAM refresh for tests.

## 2. The GBA side (M4A / MP2K, pokeemerald src/m4a_1.s and m4a.c, pokeruby src/libs/m4a.c)
- Song table gSongTable in Sapphire rev 1 at **0x08455500** (8 B: header pointer, music player x2; found from the
  player pattern of pokeruby sound/song_table.inc). 468 entries, 119 `mus_*`.
- Song header: track count, block count, priority, reverb (0x80 | value), voicegroup pointer, track pointers.
- Voicegroup: 12-byte ToneData {type, key, length, pan/sweep, wave pointer (CGB: duty), attack, decay, sustain,
  release}; type 0 DirectSound (8 = fixed pitch, played at the mixing rate), 1/2 square (duty 0-3), 3 programmable wave
  (16 bytes = 32 4-bit samples), 4 noise; 0x40 key split (sub-voicegroup + key table), 0x80 drum kit (sub-voice = key,
  played at the sub-voice's own key and pan). WaveData: u16 type, u16 status (0x4000 loop), u32 freq (Hz x 1024 at key
  60), u32 loop start, u32 size, s8 samples. Sapphire's samples sit 0x74 after Ruby's addresses in pokeruby's
  direct_sound_data.inc (names: sc88pro_piano1_48, sc88pro_flute, ...).
- Commands: 0x80-0xB0 waits (gClockTable: 0-24 then 28 ... 96 ticks), 0xB1 FINE, B2 GOTO (pointer), B3 PATT (call,
  3 levels), B4 PEND, B5 REPT n, B9 MEMACC, BA PRIO, BB TEMPO (bpm/2), BC KEYSH, BD VOICE, BE VOL, BF PAN (64 = centre),
  C0 BEND, C1 BENDR, C2 LFOS, C3 LFODL, C4 MOD, C5 MODT, C8 TUNE, CC PORT, CD XCMD (08 xIECV / 09 xIECL pseudo-echo),
  CE EOT, CF TIE, D0-FF notes N01-N96 [key [velocity [gate+]]]; a byte below 0x80 repeats the last command 0xBD+
  (running status). Defaults per track: bend range 2, LFO speed 22.
- Time: 24 ticks per quarter; the engine runs per V-blank (59.7275 Hz) and ticks each 150 units of tempoD = 2 x TEMPO
  byte, so a TEMPO of 54 is 107.5 bpm. Loops: each track ends with GOTO back to its loop label (Littleroot: tick 36 ->
  2340, all 9 tracks; the wild battle 1056 -> 4128). Volumes are linear: ChnVolSetAsm velocity x (track vol x 64 >> 5)
  x pan; 5 DirectSound channels at 13,379 Hz, master volume 12, song reverb (50); 4 CGB channels.

## 3. The converter (b2tools/m4a_to_sseq.py)
`python3 b2tools/m4a_to_sseq.py mus_littleroot` -> work/agents/music_check/out/mus_littleroot.{sseq,sbnk,swar,txt}.
- Reads the song from the user's dump (m4a.parse_track follows patterns, repeats and running status to the GOTO).
- SSEQ: every note (TIE/EOT become lengths), ticks x 2, tempo round(2 x byte x 0.99576) (NitroSDK's sequencer: 192
  updates/s, a tick per 240 tempo units; 108 for Littleroot = 0.4 % fast), the loop as a jump to the same tick in every
  track, VOL and velocity through v' = 127 sqrt(v/127) (keeps the GBA's linear loudness on Black 2's 40 log10 curve),
  PAN as is, KEYSH folded into the keys, BEND x 2 with BENDR, MOD/LFOS/LFODL/MODT as modulation depth / speed / delay /
  type (approximate: depth mod x 8.6, speed from the LFO's Hz at 0.375 Hz per step). Dropped: pseudo-echo, TUNE, PRIO,
  MEMACC (one song uses it). Checked by decoding the output with sseq.decode (same notes and loop as the GBA).
- Instruments: each GBA voice -> a program of BANK_MUS_WB_SOUNDLIST through data/hoenn_music.json (defaults by GBA
  sample name, per-song overrides by voice index, the drum kit key for key: both kits are General MIDI, checked on the
  Black 2 kit's samples: 36 kick, 38 snare, 42/46 hats, 49 crash, 54 tambourine ...). The bank is built from the library
  programs the song plays, keeping only the key-split regions and drum keys it uses; the wave archive holds only those
  waves. Littleroot: 19 waves, 171,396 B.
- Balance: `scripts/stems.py` records each track alone in game and renders it alone from the GBA, and data/hoenn_music.json
  `track_gain` scales each track so Black 2's mix keeps the GBA's balance; `volume` (INFO) matches the song's loudness
  to the Black 2 song it replaces (Littleroot: equal RMS to T_01 within 0.1 dB).

### Instrument mapping (who plays what)
Black 2's library carries no instrument names, so each program was identified from: Black 2's own Hoenn remixes
(SEQ_BGM_VS_RS_LEADER / VS_RS_CHAMP aligned note for note with mus_vs_gym_leader / mus_vs_champion:
scripts/align.py; GF played the GBA strings with 30, trumpet and horn with 39, drum kit 80, the square leads with
synth lead 95, fingered bass with their new bass, timpani with a timpani), how Black/White's songs use each program
(range, chords, note lengths: scripts/usage.py), its envelope, and its spectrum against pokeruby's named samples
(music_voices.py, scripts/timbre.py: odd harmonics = clarinet, pure decaying = mallet, ...). The table is in
data/hoenn_music.json "instruments" and can be retuned there.

Littleroot Town (mus_littleroot, 9 tracks, 107.5 bpm, loop 53.6 s):
| GBA voice (track) | Black 2 program |
|---|---|
| string ensemble (0, 1, 5) | 30 string ensemble |
| flute (1, melody) | 47 flute |
| fretless bass (2) | 25 electric bass |
| pizzicato strings (3, 5) | 20 pizzicato strings |
| piano (4, high sparkle) | 0 piano |
| square 2, doubling the flute melody (6) | 3 celesta / vibraphone (bell-like mallet) |
| square 1, off-beat stabs (7) | 36 nylon guitar |
| drum kit: tambourine key 54 (8) | 80 drum kit, key 54 tambourine |

Wild battle (mus_vs_wild): strings 30, trumpet and horn 39 brass, fingered bass 25, harp 34, timpani 86, drum kit 80,
squares 95 synth lead, programmable wave 30.

## 4. Hooked in: HOENN_MUSIC=hoenn (test only, off by default)
- build_rom.py adds `patches/hoenn_music.py` last when HOENN_MUSIC is set; without HOENN_MUSIC=hoenn it changes
  nothing (every other build stays byte for byte). With it: each song of data/hoenn_music.json is converted and installed
  in place; Littleroot -> SEQ_BGM_MSL_DL_01 (1172, the first of four empty slots for downloadable Musical songs, its own
  bank 1150 and 238,596 B wave archive), zone 389's four BGM fields -> 1172; the wild battle -> SEQ_BGM_VS_NORAPOKE
  (1128) in place (every wild battle). Neither id is in the ISS table.
- Test ROM: `scripts/music_rom.py release/Pokemon_Sapphire_NDS_v15.2.nds work/agents/music_check/rom/hoenn_music.nds`
  runs the same apply() on the release ROM's two files and writes them back in place (LAYOUT IDENTICAL).
- Recording: libdesmume exports DeSmuME's own WAV writer (WAV_Begin/WAV_End, sound core mode: the SPU mix at 44.1 kHz in
  emulated time; scripts/wavrec.py); the emulator stays at volume 0 with SDL's dummy driver. scripts/record_field.py:
  save in game from a base state (once), cold boot, Continue, record. Do not load a savestate on the same ROM name:
  DeSmuME writes the state's battery back to <name>.dsv on exit (it erased the test save once).
- Proof it is the converted song: chroma (pitch-class) similarity with the song's own notes 0.72 for the in-game
  recording vs 0.27 for what Littleroot played before (T_01); in-game vs GBA render 0.79; the recording repeats itself
  after 53.3 s (the loop: 53.6 s x 107.5/108). scripts/compare.py.
- Wild battle, in a real battle: scripts/battle_test.py loads the playthrough's s06_bag state (Birch's bag on Route 101,
  same ROM layout), refreshes the sound archive in RAM to what a cold boot of the test ROM loads (the INFO block is in
  RAM byte for byte; the FAT too except each entry's third word, where NitroSDK keeps the address of a loaded file), picks
  the starter and records. The converted theme starts with the battle (0.76 similarity with its notes over the first 20
  s, 0.35 for Black 2's VS_NORAPOKE), loops after 39.4 s, and the sound heap has 142 KB free (55 KB in the same battle with Black 2's song).
- Balance and loudness: scripts/stems.py (per-track gains, see 3), scripts/curve_test.py (volume curves). Littleroot:
  INFO volume 100 = T_01's loudness (0.0 dB); wild battle: volume 127 and `level` 1.32 (VOL 80 -> 106) = VS_NORAPOKE's
  (+0.1 dB). Reference recordings: work/agents/music_check/out/t01_ref.wav (what Littleroot plays in v15.2),
  out/wild_ref_b2.wav (Black 2's wild battle).
- build_rom.py checks: no patches, HOENN_MUSIC unset -> "matches original" (e51e6dfb...); HOENN_MUSIC=hoenn on the same
  tree -> LAYOUT IDENTICAL to it (only swan_sound_data.sdat bytes and 8 bytes of a/0/1/2 differ).

## 5. The full soundtrack (estimate)
107 songs to convert (119 `mus_*` minus 12 unused/test: dummy, littleroot_test, gsc_route38, gsc_pewter,
c_comm_center, c_vs_legend_beast, link_contest_p1-p4, end, radio_tower_takeover):
| group | n | songs |
|---|---|---|
| field, by map | 44 | 12 towns/cities, 8 routes, caves/ship/hideouts/Mt. Pyre/Victory Road, Center, Mart, Gym, lab, museums, contests, Trick House, Safari, Battle Tower, underwater, sailing ... |
| field, by player state | 2 | surf, cycling (in place of 1013 NAMINORI / 1012 BICYCLE) |
| battles | 10 | wild, trainer, gym leader, rival, Aqua/Magma, their leaders, Elite Four, champion, Regi, Kyogre/Groudon |
| victory / caught | 6 | wild, trainer, gym leader, league, Aqua/Magma, caught |
| trainer encounter (eye) | 17 | one per class group (Black 2 has 13 EYE slots + Dancer/Clown: classes need re-pointing) |
| events | 15 | title, intro, intro battle, credits, Hall of Fame, evolution, help, follow me, cable car, Kyogre/Groudon weather, contest results/winner, roulette, route 111 |
| jingles | 13 | level up, heal, badge, item, TM, berry, evolved, move deleted, awaken legend, slots ... |
- Memory: each song is cut to its own instruments, so each fits its Black 2 counterpart's budget (Littleroot 179,872 B
  vs 203,188; wild 131,456 vs 239,596); the converter prints the footprint and install_in_place refuses a song that
  does not fit its slot. Field songs need <= ~249 KB, battle songs <= ~240 KB (measured heap: one BGM has ~282 KB).
- ROM: in place costs nothing; appended, about 107 x ~120 KB = ~13 MB of 163 MB free (and +~5 KB of sound heap for the
  new INFO/FAT entries: in place avoids that too). Slots: of Black 2's BGM sequences, 163 are played by no Hoenn zone
  header (v15.2) and own their bank and wave archive (103 of them with >= 150 KB of wave archive space): the battle,
  victory and eye-contact ones (to be replaced in place anyway), the Musical (MSL_*, the four DL slots), PWT scenario,
  Unova cutscene (E_*, SW_DEMO_*) and Unova-only area songs (battle_tower's PWT may play some PW_* and VS_*_LEADER
  ids). Hoenn's zone headers use 97 BGM ids.
- Per track by hand (the rest is automatic: conversion, bank cutting, stems balance and loudness ~3 min each in DeSmuME):
  the GBA square / programmable wave / noise parts (no Black 2 equivalent: pick an instrument per role, lead -> synth
  lead or a wind, arpeggio -> mallet/harp, stabs -> guitar/pizzicato), listening for instrument range problems (a sample
  stretched far from its base key), the ISS (no listed id; route songs never in R_* slots unless the entry goes), the
  trainer-class tables for the 17 encounter themes, songs that do not loop (jingles end with FF instead of a jump), the one
  MEMACC song, Route 118's split music, and sequences played by scripts (s0098 BGMPlay ids in Hoenn's chapter scripts).
  Machine time: conversion is seconds per song, the stems balance ~3 min per song in DeSmuME (~5 h for all 107); the
  real work is choosing instruments for the PSG parts song by song and the user's listening passes.
- Ruby: the same songs (Ruby and Sapphire share the soundtrack); one build of the music serves both versions.

### As Birch's third question (Hoenn or Unova music), or as a build flag
- Build flag (as now): HOENN_MUSIC=hoenn replaces the Black 2 songs in place; nothing else changes. Simplest.
- In-game choice: keep both. Field: the zone header's free season fields: bgm1 (summer) = Unova, bgm2 = Hoenn, and a
  small code patch makes DecideZoneHeaderBGMID / GetRegularZoneBGMID take "season" 2 when the save's music flag is set
  (one flag, a few instructions, no tables). Battles, surf/bike, jingles and script BGMs use fixed ids: one hook in
  GFL_SndBGMPlayCore (0x02005d98) that swaps the id through a small Unova -> Hoenn table when the flag is set covers
  all of them (and the field too, instead of the season trick). Birch's question writes the flag like the Fairy and
  split questions (fairy_core). Cost: both sets in the ROM; the Hoenn songs then go into slots neither choice plays
  (the 163 above minus the battle/jingle ids that the Unova choice still needs: the Unova-only cutscene and Musical
  slots are enough for the field songs, in place, no layout change; check which PWT ids battle_tower's PWT plays) or
  are appended (one SDAT growth, one layout change and savestate remake); each song's memory as above.

## 6. Done: the full soundtrack and the Hoenn / Unova option (2026-10-08; sections 4-5 are the check's plan)
- **Songs**: all 108 `mus_*` that Sapphire plays (b2tools/m4a_to_sseq.py `--all`; unused/test ones skipped:
  m4a_to_sseq.UNUSED) are converted with automatic instrument choices (data/hoenn_music.json `defaults` by GBA sample,
  `roles` for the square / wave parts by role and context, b2tools/music_roles.py) and installed in place into 108
  slots that neither option plays (b2tools/music_slots.py: Unova cutscene, Musical, Pokestar, Unova-only places, Kyurem
  SE sequences; never a fixed-use, ISS-listed or battle_tower id): 17,515,272 of 18,215,200 free bytes, the SDAT keeps
  its size (no ROM layout change). Every song fits the 282 KB BGM budget (key-split regions merged where needed).
- **Balance**: per part, automatic (`music_calib.py --gba I/N` caches each part's GBA level, `--gains` writes
  data/hoenn_music_gains.json from the calibrated Black 2 notes, data/hoenn_music_levels.json). The model counts the
  pan (the DS pans linearly: a hard-panned part is +3 dB); checked against 15 tracks measured alone in game: within
  +-2 dB. The two songs the user approved in the check (Littleroot, wild battle) keep their measured track gains
  (`no_auto_gain`). Loudness: field INFO volume 56 (Oldale / Route 104 -21.2 / -21.3 dBFS = Black 2's T_01 -21.5),
  battle 170 (127 + level; trainer / gym battle -13.8 / -13.0 dBFS, Black 2's wild battle -12.7).
- **The option**: Birch's third question (fairy_core's intro script, b2tools/patches/fairy.py; text 0054 lines 28-30,
  src/text/overrides_fairy.json): options u16 of save block 27, bit 13 = Hoenn music, fixed for the playthrough.
  b2tools/patches/hoenn_music.c (ITCM, 2,166 B): zone music from the zone header's autumn field bgm2 (378 zones, set
  by the patch), every other BGM / jingle through a Unova -> Hoenn table in GFL_SndBGMPlayCore (60 entries: surf,
  bike, battles, victories, Hall of Fame, credits, jingles), trainer encounter / battle / victory music per trainer
  class (77 classes, pokeruby's rules), wild battle music per species (Kyogre/Groudon/Rayquaza, Regis). Unova option:
  Black 2's music, except 3 Hoenn-only script songs played by a Unova stand-in. Ruby: Team Magma's encounter theme for
  the team classes, E_PLASMA -> mus_encounter_magma. The Battle Tower zones (15, 17, 21, 336, 343) get mus_b_tower.
- **Tests** (work/agents/music_check/scripts/music_test.py on a build with b2tools/patches/test_music_kit.py, TEST
  ONLY: the Littleroot sign warps / starts battles, placeholders filled in RAM): Hoenn: Route 101 mus_route101,
  Oldale mus_oldale, Route 104 mus_route104; Youngster Calvin: mus_encounter_male -> mus_vs_trainer ->
  mus_victory_trainer -> back to the town; Roxanne: mus_vs_gym_leader. Unova: Route 101 SEQ_BGM_R_A; Calvin
  EYE_01 -> VS_TRAINER -> WIN2. Sampler: screenshots/music_full/ (4 songs, 30-36 s).
- **Not tested yet** (2026-10-08): cave, surf, bike, wild battle in grass, rival, Aqua, legendary, heal / badge /
  evolution jingles, Hall of Fame / credits; the Ruby build and rom_layout_diff Sapphire vs Ruby. Done 2026-10-11 except
  grass and rom_layout_diff: section 7 (surf, bike, evolution and credits were still Black 2's).
- **v16 freeze (fixed 2026-10-09, freeze_fix)**: Black 2 waits for its jingles and short songs to end (field scripts'
  MEWait after MEPlay; the battle's capture jingle and the evolution demo's SEQ_BGM_SHINKA wait for
  GFL_SndBGMIsPlaying to be false). v16 redirected SEQ_ME_POKEGET to mus_caught and SEQ_BGM_SHINKA to mus_evolution,
  and both of those songs loop. So with Hoenn music the game hung at Birch's "received the Mudkip!" (and would also
  have hung at every gift Pokémon, every capture and every evolution). Now: POKEGET -> mus_obtain_item (Sapphire's own
  givemon jingle), SHINKA -> mus_evolution_intro, KOUKAN (the evolution/trade loop) -> mus_evolution.
  hoenn_music.py check_waits refuses any redirect (or Unova reverse) that turns a sequence that ends into one that
  loops. The evolution demo plays KOUKAN and SEQ_ME_SHINKAOME through func_02006424, not GFL_SndBGMPlayCore, so those
  two kept Black 2's songs, and mus_caught was unused (in Gen 3 it is a looping BGM after a capture; Black 2 only has
  the capture jingle): both done 2026-10-11, section 7.

## 7. The rest of the Hoenn music (music_more, 2026-10-11)
All of it only with Birch's "Hoenn music" answer (options bit 13); the Unova answer keeps Black 2's music (checked per
test below). Code: b2tools/patches/hoenn_music.c (2,776 B of ITCM), hoenn_music.py, data/hoenn_music.json,
src/include/hoenn_music.inc; check_waits still passes on every build (62 redirect pairs + the after-capture pair).

### Black 2's other ways to start a BGM (pokebw2 src/system/snd_sys.c)
GFL_SndBGMPlayCore was the only hook. Black 2 also starts BGM sequences through:
- **func_02006424** (seq, step, start): a threaded load (seq + bank, then waves), then the start. Used by the evolution
  demo (ov284 shinka_demo.c: SEQ_BGM_KOUKAN, SEQ_ME_SHINKAOME), the egg demo (ov307 egg_demo.c: the same two) and the
  **field sound system's faded BGM change** (field_sound_system.c FieldSnd_BGMChangeOut/In): **surfing, cycling** and
  other faded changes. So surf, bike, the evolution loop / fanfare and the egg hatching all played Black 2's songs with
  the Hoenn answer (seen in game: `ask load 1013 SEQ_BGM_NAMINORI`). Hook: `adds r5, r0, #0; adds r4, r1, #0` at
  0x02006428 -> bl Music_LoadShim (Music_Redirect on r0, r1-r3 kept).
- **0x02005e10** (named GFL_SndBGMStop in the decomp, but it plays on PLAYER_BGM2): the credits' SEQ_BGM_ENDING (ov012
  event_game_clear.c) and the Game Freak logo's SEQ_BGM_GF_LOGO (ov264). Hook at 0x02005e14 -> Music_Bgm2Redirect.
- **func_02005e08** (RequestBGMChange, a faded change; ov028, ov324): hook at its `bl RequestBGMChange`.
- the title's **stream** (GFL_SndStream*, ov162 only; Black 2's title song is a STRM, not a sequence): see Title.
- func_020064b8 / func_02006564 (in-memory sequences: Pokestar Studios only): not hooked.

### Songs hooked up
| song | where (Sapphire) | how |
|---|---|---|
| mus_evolution_intro, mus_evolution, mus_evolved | evolution scene, egg hatching (pokeruby egg_hatch.c plays 376, 377, then fanfare 371: the same three) | SHINKA (PlayCore), KOUKAN / SHINKAOME (func_02006424 hook) |
| mus_surf, mus_cycling | surfing, the bike | the func_02006424 hook (the table had them already) |
| mus_caught | after a capture ("Gotcha!" {PLAY_BGM MUS_CAUGHT}) | Music_Redirect: SEQ_BGM_WIN1 right after SEQ_ME_POKEGET (Black 2 plays the capture jingle, waits for it, then WIN1) -> mus_caught (data "after_catch") |
| mus_weather_kyogre (Ruby: mus_weather_groudon) | Lilycove, Mossdeep, Sootopolis, Ever Grande, Routes 124-128 while FLAG_SYS_WEATHER_CTRL (overworld.c ShouldLegendaryMusicPlayAtLocation) | Music_ZoneBGM zone rule (patches/weather.py crisis_zones); GetRegularZoneBGMID's entry now jumps to Music_ZoneBGM with the game data (`ldr r3, [pc, #8]; bx r3`) |
| mus_mt_chimney | Weather Institute 1F/2F while VAR_WEATHER_INSTITUTE_STATE 0 (IsInfiltratedWeatherInstitute) | zone rule (data "zone_rules") |
| mus_title | title screen | GFL_SndStreamInit/Play/FadeStop/Stop/IsPlaying (arm9) jump to Music_Stream*: Init decides (Hoenn answer: no stream at all), Play -> GFL_SndBGMPlay(mus_title), FadeStop -> BGM fade, IsPlaying -> fading, Stop -> BGM stop. The save is loaded at boot, so the title knows the answer of the save on the cartridge |
| mus_intro | the intro's Game Freak logo part (intro.c m4aSongNumStart(MUS_INTRO)) | SEQ_BGM_GF_LOGO -> mus_intro (BGM2 hook); ov264 fades it out when the logo ends |
| mus_credits | credits | SEQ_BGM_ENDING was already in the table but played through the BGM2 path |
| mus_encounter_may / _brendan | rival scenes (Route 103, 110, the Champion's room ...) | hoenn_story.inc MUS_ENCOUNTER_MAY/BRENDAN = their slots (were SEQ_BGM_E_HUE); Unova: reverse table -> E_HUE |
| mus_sailing | Mr. Briney's boat | MUS_SAILING = its slot (was NAMINORI, i.e. mus_surf with Hoenn); Unova: reverse -> NAMINORI |
| mus_help | Route 101, Birch chased (playbgm MUS_HELP) | h_playbgm_hoenn in 0634_route_101.s Script_10 |
| mus_encounter_elite_four | the four Elite Four rooms (playbgm before the intro) | h_playbgm_hoenn in the four room scripts |
| mus_cable_car | the cable car ride (cable_car.c FadeInNewBGM) | cable_car_ride (common/boat.inc): Hoenn answer plays it and the black-screen ride lasts 5 s instead of 1.5 s |

Scripts and the option: BGMIsPlaying (s009B, ov036) reads a BGM argument it never uses; hoenn_music.c answers
`BGMIsPlaying 0xFFF0, var` with the music option (1 = Hoenn). src/include/hoenn_music.inc: h_goto_if_hoenn_music,
h_playbgm_hoenn (keeps work 0x8007), and the MUS_HOENN_* slot names (the build checks each against data/hoenn_music.json
"slots"; music_slots.SCRIPT_SLOTS keeps them fixed).

### No matching scene in our game
mus_contest, mus_contest_results, mus_contest_winner, mus_too_bad (contests: nobody registers; too_bad is the slots' and
contests' "no luck" fanfare), mus_slots_win, mus_slots_jackpot, mus_roulette (the Game Corner has no Coins / slots /
roulette), mus_intro_battle (the intro movie's Groudon-Kyogre fight: our boot skips the movie).

### Title notes (title.py untouched)
The save is read at boot (SaveControl_Create), so the copyright, the Game Freak logo and the title already know the
save's answer (a new cartridge or a deleted save = Unova). mus_title ends after ~96 s (10,992 ticks at 143 bpm);
Sapphire then restarts the intro (title_screen.c: BGM stopped -> copyright screen); Black 2's title times out at 6,780
frames (113 s), so ~17 s of silence first. Matching Sapphire needs an ov162 change (Title_UpdateTimer: also end when
!GFL_SndBGMIsPlaying() with the Hoenn answer): title.py's business (title_anim). The hooks need Title_Main to keep
calling GFL_SndStreamInit / Play / FadeStop / IsPlaying / Stop.
The credits: mus_credits lasts ~171 s, Black 2's credits ~263 s and they are timed by frames, not by the song (THE END
starts at the same frame with either song). So mus_credits loops (user, 2026-10-11): data "songs" mus_credits
{"loop": true} makes m4a_to_sseq end every track at the song's last tick with a jump to the start, and data
"not_waited": ["SEQ_BGM_ENDING"] lets check_waits accept a looping stand-in for it (ov012 only fades it out). In game
(clearloud test, ROM 7548cf4d): mus_credits from 50.6 s to THE END at 314.0 s, -20 to -23 dBFS in every 10 s window,
no gap at the loop (~171 s in).

### In-game checks (2026-10-11)
Harness: work/agents/music_more/scripts/music_test.py (music_check's, moved onto music_more/pt, the freeze_fix copy
of the playthrough driver: work/agents/playthrough was removed) + scripts/sndhooks.py: DeSmuME exec hooks log the id
asked for (GFL_SndBGMPlayCore entry 0x02005d98, func_02006424 entry) and the id that starts (0x02005db4, 0x0200648a,
after the redirects); the BGM2 path shows in the BGM stack log. New kit modes (test_music_kit.py): 5 egg
(PokePartyAddEgg, the harness zeroes the hatch counter, CallEggHatch as global script 1234), 10 Ultra Balls. New harness
modes: evo (Torchic 1 Exp. Point under Lv 16, two moves), catch (Lv 2 foe: the bot throws at once), egg, talk
(ROOM X Z | uid N), MT_FLAGS / MT_WORKS (story flags / works), prep_party (the kit's party, then only the Lv 100
Mudkip: the battle bot loops on in-battle move-learning prompts), PT_TIMEOUT 420 s. Known harness limits: talking right
after the kit's MapChangeCore warp hangs the message window (test only: scripts/cable_test.py enters the station by its
door); the Center nurse is out of the bot's reach across the counter (the heal jingle is checked with `me 1300`);
`_fast_run` skips every frame's drawing, so pixel-based menu checks and screenshots are stale.
title_test.py: cold boot with the battery of a ROM name (ff.py save, SAVE_XY=60,93 when the menu has 4 entries,
OPT=unova). ff.py birch2 (OPT=...) for Route 101's chase.
Results (asked -> played), Hoenn / Unova; Sapphire kit ROMs ae2f7df3 (batch1-3: same code for these paths) and ea52b351 (final: batch5/6, cable car, birch2); Ruby kit ROM c288dc06 (batch4):
| check | Hoenn | Unova |
|---|---|---|
| boot / title / Continue (cold boot) | mus_intro (GF logo) -> mus_title (no stream) -> mus_littleroot | SEQ_BGM_GF_LOGO -> stream -> T_01 |
| cave (Granite Cave) | mus_petalburg_woods (Sapphire's) | SEQ_BGM_D_02 |
| surf (Route 103) | NAMINORI -> mus_surf (was Black 2's) | NAMINORI |
| bike (Route 104) | BICYCLE -> mus_cycling (was Black 2's) | BICYCLE |
| rival May (trainer 655) | mus_encounter_female -> mus_vs_rival -> WIN2 -> mus_victory_trainer | EYE_01 -> VS_TRAINER -> WIN2 |
| Aqua grunt (trainer 4) / Ruby Magma grunt | mus_encounter_aqua / _magma -> mus_vs_aqua_magma -> WIN6 -> mus_victory_aqua_magma | EYE_NEO_PLASMA -> VS_NEO_PLASMA -> WIN6 |
| Kyogre / Ruby Groudon Lv 50 | mus_vs_kyogre_groudon -> WIN1 -> mus_victory_wild | VS_NORAPOKE -> WIN1 |
| Regirock | mus_vs_regi | VS_REGI |
| capture | POKEGET -> mus_obtain_item, WIN1 -> mus_caught | POKEGET, WIN1 |
| evolution (Torchic) | SHINKA -> mus_evolution_intro, KOUKAN -> mus_evolution, SHINKAOME -> mus_evolved, LVUP -> mus_level_up | SHINKA, KOUKAN, SHINKAOME, LVUP |
| egg hatching | mus_evolution_intro, mus_evolution, mus_evolved | SHINKA, KOUKAN, SHINKAOME |
| jingles: heal (ASA), badge, item | mus_heal, mus_obtain_badge, mus_obtain_item | ASA, BADGE, ITEM |
| Pokémon Center (Oldale) | mus_poke_center | POKECEN |
| rival / boat slots (scripts) | E_CHEREN -> mus_encounter_may, E_DOCTOR -> mus_sailing | -> E_HUE, -> NAMINORI |
| Route 101 chase (ff.py birch2) | mus_route101 -> mus_help -> mus_vs_wild -> mus_birch_lab -> mus_obtain_item | R_A -> VS_NORAPOKE -> LABO -> POKEGET |
| Elite Four (Sidney's room) | mus_victory_road (room) -> mus_encounter_elite_four on talking | POKEMON_LEAGUE, nothing on talking |
| cable car (cable_test.py) | mus_cable_car during the ride -> Mt. Chimney station mus_route110 | (no song) -> SW_KAZAN |
| crisis (flag 903) Sootopolis / Route 128 / Ruby Sootopolis | mus_weather_kyogre / mus_weather_kyogre / mus_weather_groudon | SW_C_14 / R_E_SU / SW_C_14 |
| Weather Institute 1F, work 0x40BB = 0 / 1 | mus_mt_chimney / mus_rustboro | SW_R_22_SU |
| Hall of Fame, credits, THE END | mus_hall_of_fame, mus_credits (looped to THE END), mus_end (then the title: mus_title) | E_DENDOUIRI, ENDING, THEEND |
No freeze anywhere (the evolution, the egg, the capture, the lab's POKEGET, the credits all went on). Not run: a wild
battle in grass (the kit's battles use the same battle music path), rom_layout_diff Sapphire vs Ruby.

## 8. Emerald: the Battle Frontier's songs, a bigger archive, Emerald's own instruments (frontier_core_music, 2026-10-12)
- Emerald's 125 songs (Sapphire's 108 + emerald_art's 4 + the Frontier's 13) need about 2.3 MB more than the pool's free
  bytes, so **Emerald's archive grows by 4 MiB** (data/emerald/hoenn_music.json `archive_reserve`;
  patches/hoenn_music.archive_reserve, Emerald only: 89,373,024 -> 93,567,328 B; the header's size and FILE block size
  follow). The new files sit after the last file through the pool slots' own FAT entries: INFO and the FAT keep their
  sizes, so the sound heap is unchanged. The Emerald ROM's layout moved once (savestates remade); about 1.9 MB of the
  reserve stays spare so later Emerald songs do not move it again. Sapphire and Ruby: unchanged, byte for byte.
- **Emerald's own instruments**: a GBA voice whose sample has `defaults` {"gba": true} plays that sample (its bytes as
  an NDS PCM8 wave, base key 60 at WaveData freq / 1024) with its GBA envelope converted to NDS terms, by Black 2's own
  ARM7 envelope rules (b2tools/m4a_emerald.py EmeraldSong, gba_adsr, gba_swav). Its balance uses nds_note_rms x
  `gba_instruments.level_k`; that model reproduces the 318 measured melodic library notes of
  data/hoenn_music_levels.json within +-0.6 dB.
- Ids, zones and the in-game check: notes/FRONTIER.md section 5.
