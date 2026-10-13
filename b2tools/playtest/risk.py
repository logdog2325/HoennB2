"""Rank every map's people / signs / triggers by what their scripts do (the release ROM's scripts, decoded with the
decomp's own disassembler through b2tools/script_check.py's Rom). Output: log/risk.json
    {zone: [{kind, uid|idx, x, z, script, cmds: [...], risk: 0-3, tags: [...]}]}
risk 0 = messages only, 1 = flags/items/moves/sounds, 2 = specials/battles/shops/trades/warps/apps, 3 = unknown/undecodable."""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.expanduser('~/Documents/GitHub/HoennB2')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import script_check as SC
from pt import ROM, LOG
import places as PL

LOW = re.compile(r'^(VM|Ev|Actor(Lock|Unlock|Msg|Face|Anm)|ParentActorMsg|MsgWin|LastKeyWait|SEPlay|SEWait|FlagCheck|'
                 r'Work(Cmp|Get|Set|Add|Sub)|Compare|Jump|Call|If|Lock|Release|FacePlayer|SystemMsg|InfoMsg|MsgPlaceSign|'
                 r'TimeWait|Wait|PlayerGet|Gender|CheckerMsg|ActorMsgClose|InfoMsgClose|MsgPlaceSignClose|CheckerMsgClose)')
HARMLESS = {'ActorsPauseAll', 'ActorsUnpauseAll', 'FinishAllEvents', 'ActorSetEyeToEye', 'FlagSet', 'FlagReset', 'FlagGet',
            'MEPlay', 'MEWait', 'PVPlay', 'PVWait', 'YesNoWin', 'MsgWaitAdvance', 'TrainerCardHasBadge', 'ActorGetSpawnFlag',
            'RecordAdd', 'ItemCheckSpace', 'ItemCheckAmount', 'ItemIsTMHM', 'ItemGetPocket', 'RTCallGlobal', 'RTEndGlobal',
            'WorkAnd', 'WorkOr', 'PokePartyGetCount', 'TrainerFlagGet', 'TrainerBattleIsVictory', 'ActorGetGPos'}
MEDIUM = {'ItemAdd', 'ActorCmdExec', 'ActorCmdWait', 'ActorDelete', 'FieldEffect', 'ActorAdd', 'ActorSetGPos', 'ObjInitNPCGPos',
          'TrainerFlagSet', 'PlayHMCutInEffect', 'FadeOutBlackQ', 'FadeInBlackQ', 'RTReserveScript', 'ItemSub'}
BATTLE = {'TrainerBattleSet', 'TrainerBattleStart', 'WildBattleSet', 'TrainerFlagSet', 'TrainerTalkTypeGet'}
TAGS = [('battle', r'Battle|Trainer|Encount'), ('item', r'Item|Bag'), ('warp', r'MapChange|Warp'), ('move', r'ActorCmd|Movement'),
        ('shop', r'Shop|Mart'), ('trade', r'Trade'), ('pkm', r'Poke|Party|Pkm|Pokemon'), ('app', r'Call|Proc|App|Box|PC|Name'),
        ('flag', r'Flag|Work'), ('special', r'Cmd_')]


def analyze():
    rom = SC.Rom(ROM)
    zones = sorted(set(PL.ZONE.values()))
    out = {}
    cache = {}

    def cmds_of(zone, sid, depth=0):
        key = (zone if sid < 2000 else None, sid)
        if key in cache: return cache[key]
        cache[key] = set()
        r = rom.resolve(zone, sid)
        if not r: cache[key] = {'?unresolved'}; return cache[key]
        f, idx, _ = r
        sf = rom.script_file(f, zone)
        if sf is None or idx is None:
            cache[key] = {'?trainer' if idx is None else '?nofile'}; return cache[key]
        import field_script as FS
        h = FS.script_header(rom.scr[f])
        if not h or idx >= len(h[0]): cache[key] = {'?noentry'}; return cache[key]
        sub = FS.ScriptFile(rom.scr[f], sf.base, sf.plugin)
        sub.trace([h[0][idx]])
        names = set()
        for pc, (cmd, args, end) in sub.instructions.items():
            names.add(cmd.name)
            if cmd.name in ('RTCallGlobal', 'RTReserveScript', 'CallGlobal') and depth < 3 and args:
                names |= cmds_of(zone, args[0], depth + 1)
        if sub.errors: names.add('?errors')
        cache[key] = names
        return names

    for z in zones:
        if z >= len(rom.hdr): continue
        try:
            ent = rom.entities(z)
        except Exception:
            continue
        rows = []
        for n in ent['npcs']:
            rows.append(dict(kind='trainer' if n['evtype'] == 1 else 'npc', uid=n['uid'], x=n['x'], z=n['z'], script=n['script'], flag=n['flag']))
        for i, s in enumerate(ent['signs']):
            rows.append(dict(kind='sign', idx=i, x=s['x'], z=s['z'], script=s['script']))
        for i, t in enumerate(ent['triggers']):
            rows.append(dict(kind='trigger', idx=i, x=t['x'], z=t['z'], script=t['script'], work=t['work'], value=t['value']))
        for r in rows:
            sid = r['script']
            if sid == 0: r['risk'] = -1; r['cmds'] = []; continue
            try:
                names = cmds_of(z, sid)
            except Exception as ex:
                names = {f'?{type(ex).__name__}'}
            high = sorted(n for n in names if not LOW.match(n) and n not in HARMLESS and not n.startswith('WordSet'))
            mid = [n for n in high if n in MEDIUM or n.startswith(('Fade', 'ListMenu', 'Item'))]
            hi = [n for n in high if n not in mid]
            tags = sorted({t for t, pat in TAGS for n in high if re.search(pat, n)})
            if r['kind'] == 'trainer' or 3000 <= sid < 7000 or '?trainer' in names:
                risk = 2; tags = sorted(set(tags) | {'battle'})
            elif any(n.startswith('?') for n in names): risk = 3
            elif hi: risk = 3 if not set(hi) <= BATTLE else 2
            elif mid: risk = 1
            else: risk = 0
            r['cmds'] = high[:40]; r['tags'] = tags; r['risk'] = risk
        out[z] = rows
    json.dump(out, open(os.path.join(LOG, 'risk.json'), 'w'), indent=0)
    return out


if __name__ == '__main__':
    out = analyze()
    tot = collections.Counter(); cmdc = collections.Counter()
    for z, rows in out.items():
        for r in rows:
            tot[r['risk']] += 1
            for c in r.get('cmds', []): cmdc[c] += 1
    print('targets by risk', dict(tot))
    print('most common non-message commands', cmdc.most_common(60))
