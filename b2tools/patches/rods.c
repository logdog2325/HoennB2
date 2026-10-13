/* The three fishing rods (rods_fix, 2026-10-12): the Old Rod and the Good Rod work like Black 2's Super Rod (Bag "Use",
 * Register on Y) and each rod fishes its own Sapphire/Ruby/Emerald table. Compiled and placed in ITCM by
 * b2tools/patches/rods.py, which has the findings (where each hook goes and why) and patches the data.
 *
 * The rod being used: ROD_ITEM, a u16 just before this code in ITCM (rods.py puts it there; not saved, 0 at boot). The
 * Bag's Use and the Y menu write it; the fishing encounter reads it. Anything but the Old or Good Rod = the Super Rod,
 * so Black 2's own path is unchanged for it.
 *
 * Tables (converter/gen_encounters.py fishing_lines): a zone's FishingEncounters = Sapphire's Super Rod slots 5-9 (Black 2
 * picks them with its own fishing odds 40/40/15/4/1, the same as Sapphire's); RipplingFishingEncounters = the Old Rod's
 * slots 0-1 then the Good Rod's 2-4 (Hoenn has no rippling water, so Black 2 never reads that group: rods.py). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#ifndef ROD_VAR
#error "ROD_VAR (the address of the rod variable) comes from rods.py"
#endif
#define ROD_ITEM (*(volatile u16 *)ROD_VAR)

#define ITEM_OLD_ROD   445
#define ITEM_GOOD_ROD  446
#define ITEM_SUPER_ROD 447
#define SC_SUPER_ROD 4      /* Y shortcut ids (ShortcutMenu_SetKeyItemID): Black 2's Super Rod */
#define SC_OLD_ROD   7      /* rods.py gives the Old and Good Rods ids 7 and 8 (Black 2's DNA Splicers, not in Hoenn) */
#define SC_GOOD_ROD  8

/* Black 2 functions (decomp symbols, config/b2_us/arm9/...; Thumb: address | 1) */
#define FN(type, addr) ((type)((addr) | 1))
#define GFL_RandomLC                     FN(u32 (*)(u32), 0x02005748)          /* random in [0, n) */
/* ov012 (field events) */
#define ShortcutMenu_SetKeyItemID        FN(u32 (*)(void *, u32), 0x0215b010)
#define ShortcutMenu_GetActionFromKeyItem FN(u32 (*)(u32, u32 *, u32 *), 0x0215b1ec)
/* ov036 (the field: encounters) */
#define FieldEncount_GenWildsCore        FN(u32 (*)(void *, void *, void *), 0x021a0bf4)
#define FieldEncount_GenWilds            FN(u32 (*)(const u8 *, void *, u32, void *), 0x021a0c38)
#define FieldEncount_PrepareActiveSlots  FN(u32 (*)(const u8 *, void *, u32, void *), 0x021a1238)
/* ov142 (the Bag) */
#define BagUseSuperRod                   FN(u32 (*)(void *), 0x0219a404)       /* func_ov142_0219a404 */

#define BAG_SELECTED_ITEM 0x8a0     /* the Bag's work: the item the menu is for (func_ov142_0219a4d0 reads it there) */
#define ENC_RIPPLING_FISHING 0xd4   /* EncData: 8 rate bytes, 12+12+12 grass, 5 surf, 5 rippling surf, 5 fishing, here */

typedef struct { u16 species; u8 minLevel; u8 maxLevel; } Slot;   /* encounters.inc Encounter */

/* The Bag's key-item Use table entry {445, 3} (Old, Good and Super Rod): remember the rod, then Black 2's Super Rod
 * handler (fishing allowed here? then leave the Bag with result 16 = fishing, else "can't use" / partner message). */
u32 Rod_BagUse(u8 *work) {
    ROD_ITEM = (u16)*(u32 *)(work + BAG_SELECTED_ITEM);
    return BagUseSuperRod(work);
}

/* Both Y-menu calls of ShortcutMenu_SetKeyItemID (popup and single shortcut): a rod remembers which one and is the
 * Super Rod's shortcut from there on (eventId 4: fishing). */
u32 Rod_SetKeyItemID(void *input, u32 sc) {
    if (sc == SC_OLD_ROD) ROD_ITEM = ITEM_OLD_ROD;
    else if (sc == SC_GOOD_ROD) ROD_ITEM = ITEM_GOOD_ROD;
    else if (sc == SC_SUPER_ROD) ROD_ITEM = ITEM_SUPER_ROD;
    if (sc == SC_OLD_ROD || sc == SC_GOOD_ROD) sc = SC_SUPER_ROD;
    return ShortcutMenu_SetKeyItemID(input, sc);
}

/* Both Y-menu calls of ShortcutMenu_GetActionFromKeyItem: the rods check the Super Rod's action (5: water in front, no
 * partner), so Black 2's "can't use" message comes for all three. */
u32 Rod_GetAction(u32 sc, u32 *action, u32 *invalid) {
    if (sc == SC_OLD_ROD || sc == SC_GOOD_ROD) sc = SC_SUPER_ROD;
    return ShortcutMenu_GetActionFromKeyItem(sc, action, invalid);
}

/* BtlSetup_CreateFishing's call of FieldEncount_GenWilds (after the bite roll). Super Rod: Black 2's own (its fishing
 * slots and odds). Old / Good Rod: the same steps, but the slot is Sapphire's pick from the rod's own slots
 * (ChooseWildMonIndex_Fishing: Old Rod 70/30, Good Rod 60/20/20), copied into every active slot, so whatever Black 2's
 * slot roll says, that Pokemon comes (levels, Repel, abilities: Black 2's code as for the Super Rod). A zone without
 * the rod's slot (a table written before rods_fix) falls back to the Super Rod's. */
u32 Rod_GenWilds(const u8 *enc, void *manager, u32 zone, void *out) {
    u32 rod = ROD_ITEM, r, i, k;
    const Slot *own;
    Slot slots[12];

    if (rod != ITEM_OLD_ROD && rod != ITEM_GOOD_ROD) return FieldEncount_GenWilds(enc, manager, zone, out);
    r = GFL_RandomLC(100);
    if (rod == ITEM_OLD_ROD) i = r < 70 ? 0 : 1;
    else i = r < 60 ? 2 : r < 80 ? 3 : 4;
    own = (const Slot *)(enc + ENC_RIPPLING_FISHING) + i;
    if (own->species == 0) return FieldEncount_GenWilds(enc, manager, zone, out);
    FieldEncount_PrepareActiveSlots(enc, manager, zone, slots);      /* fishing: the 5 slots, count, odds kind */
    for (k = 0; k < 12; k++) slots[k] = *own;                        /* (every slot an index roll can give) */
    return FieldEncount_GenWildsCore(manager, slots, out);
}
