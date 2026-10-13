"""Room script files shared by a generator and the story agents (lead's rule 2026-10-07; notes/STORY_PORTING.md §10).

A room's src/field_scripts/NNNN_room_<Map>.s is written by a generator (gen_interiors.py, gen_interior_recipes_houses.py,
specials.py, centers_rooms.py, shops_rooms.py, gyms_league_rooms.py, ship_hideouts_rooms.py, dive_rooms.py,
gen_caves.py ...), and a story agent adds Sapphire's story scripts to it after a line starting with STORY_MARK.
write_room_script(path, generated) rewrites the file from the generator's new text and keeps the story part:
  - everything from the story line to the end of the file, as it is;
  - #include lines above it that the generator does not write (hoenn_story.inc, scenes/... of a chapter), and comment
    lines between the #includes and the ScriptEntry table (a story agent's notes); other edits above the story line
    are the generator's and are lost on a rerun: fix the generator instead;
  - the ScriptEntry table as the story agent left it (its entries in place of generated ones, e.g.
    `ScriptEntry Story_H2_Girl  // story:` for Script_2, its own entries after them, #includes inside the table), plus
    the generator's entries past the old count (a new object gets the next number);
  - a generated script whose label the story part defines again is left out (the story agent replaced it).
Files without a story line are simply overwritten. write_room_script returns 'written' / 'merged (story kept)'.
"""
import re

STORY_MARK = '// ---- story'

def _split(text):
    """(head, story) at the first line starting with STORY_MARK; story '' when there is none."""
    lines = text.split('\n')
    for i, l in enumerate(lines):
        if l.strip().startswith(STORY_MARK):
            return '\n'.join(lines[:i]), '\n'.join(lines[i:])
    return text, ''

def _table(lines):
    """(start, end) of the ScriptEntry table: from the first ScriptEntry line to ScriptEntriesEnd (included), or to the
    last ScriptEntry / #include line of the table when there is no ScriptEntriesEnd."""
    start = next((i for i, l in enumerate(lines) if l.strip().startswith('ScriptEntry ')), None)
    if start is None: return None, None
    end = start
    for i in range(start, len(lines)):
        s = lines[i].strip()
        if s.startswith('ScriptEntriesEnd'): return start, i + 1
        if s.startswith(('ScriptEntry ', '#')): end = i + 1
        elif s and not s.startswith('//'): break
    return start, end

def _labels(lines):
    return [l.split()[1] for l in lines if l.strip().startswith('ScriptEntry ')]

def merge(old, generated):
    """The generator's new text with the story part of old kept (see the module docstring)."""
    head_old, story = _split(old)
    if not story: return generated
    gen = generated.rstrip('\n').split('\n')
    olds = head_old.rstrip('\n').split('\n')
    gs, ge = _table(gen)
    os_, oe = _table(olds)
    if gs is None or os_ is None:                      # no table to merge: keep the old head, the generator is ignored
        return head_old.rstrip('\n') + '\n\n' + story.rstrip('\n') + '\n'
    # the table: the old one as it is (the story's entries and comments, #includes inside it), then the generator's
    # entries past the old count
    old_tab = [l for l in olds[os_:oe] if not l.strip().startswith('ScriptEntriesEnd')]
    n_old = len(_labels(old_tab))
    gen_entries = [l for l in gen[gs:ge] if l.strip().startswith('ScriptEntry ')]
    table = old_tab + gen_entries[n_old:] + ['    ScriptEntriesEnd']
    # the story agent's #includes above the table
    gen_inc = {l.split('//')[0].strip() for l in gen[:gs] if l.strip().startswith('#include')}
    extra_inc = [l for l in olds[:os_] if l.strip().startswith('#include') and l.split('//')[0].strip() not in gen_inc]
    # comment lines a story agent put between the #includes and the table (its notes) stay too
    o_last = max((i for i, l in enumerate(olds[:os_]) if l.strip().startswith('#include')), default=-1)
    extra_inc += [l for l in olds[o_last + 1:os_] if l.strip().startswith('//')]
    pre = gen[:gs]
    last = max((i for i, l in enumerate(pre) if l.strip().startswith('#include')), default=len(pre) - 1)
    pre = pre[:last + 1] + [l for l in extra_inc if l not in pre] + pre[last + 1:]
    # the story agent's notes in the file's leading comment block (after the generator's own first lines: "// Story
    # (chapter ...) after the story line: scripts ..."; story_fixups 2026-10-07: a rerun dropped them) stay there too
    o_lead = next((i for i, l in enumerate(olds) if not l.strip().startswith('//')), len(olds))
    g_lead = next((i for i, l in enumerate(pre) if not l.strip().startswith('//')), len(pre))
    notes = [l for l in olds[:o_lead] if l not in pre]
    pre = pre[:g_lead] + notes + pre[g_lead:]
    # generated scripts the story part defines again are left out
    story_labels = set(re.findall(r'^([A-Za-z_]\w*):', story, re.M))
    body, skip = [], False
    for l in gen[ge:]:
        m = re.match(r'^([A-Za-z_]\w*):', l)
        if m: skip = m.group(1) in story_labels
        if not skip: body.append(l)
    return '\n'.join(pre + table + body).rstrip('\n') + '\n\n' + story.rstrip('\n') + '\n'

def write_room_script(path, generated):
    """Write a generated room script, keeping a story agent's part (module docstring). Returns what it did."""
    import os
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    text = merge(old, generated) if old else generated
    open(path, 'w', encoding='utf-8').write(text)
    return 'merged (story kept)' if _split(old)[1] else 'written'

def has_story(script_path):
    import os
    return os.path.exists(script_path) and bool(_split(open(script_path, encoding='utf-8').read())[1])

def write_room_text(path, lines, script_path):
    """Write a generated room text file (list of lines). When the room's script has a story part, the old file's lines
    past the generator's count stay: they are the story's (appended after the generated ones). Returns a warning when
    the generator now writes over an old line that differs (a story line may have moved)."""
    import os
    old = open(path, encoding='utf-8').read().rstrip('\n').split('\n') if os.path.exists(path) else []
    warn = ''
    if has_story(script_path) and list(lines) == ['…'] and old:   # the generator has no line of its own ('…' only
        lines = old                                                 # keeps the file from being empty): a story agent's
    elif has_story(script_path) and len(old) > len(lines):         # line 0 there is the story's (story_fixups)
        lines = list(lines) + old[len(lines):]
    elif has_story(script_path) and old[:len(lines)] != list(lines)[:len(old)]:
        warn = f'{os.path.basename(path)}: generated lines changed in a room with story lines: check the story\'s line numbers'
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    return warn
