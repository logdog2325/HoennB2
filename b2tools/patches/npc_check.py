"""Build step: the people-sprite budget of every Hoenn zone (b2tools/npc_check.py, notes/NPC_LIMIT.md). Reads the
finished files, changes nothing; put it last in the patch list."""
import os, importlib.util

def apply(files):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'npc_check.py')
    spec = importlib.util.spec_from_file_location('npc_check_tool', path)     # (not this module's own name)
    tool = importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)
    return tool.apply(files)
