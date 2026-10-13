"""Helpers for running inside Blender (blender --background --python script.py -- args).

Black 2 units: 1 tile = 16 units, a map chunk is 32x32 tiles = 512x512 units centred on the origin.
glTF (apicula) is Y-up; Blender imports it as Z-up (x, -z_gltf, y_gltf). We work in Blender's frame:
  tile column tx = floor((x + 256) / 16), tile row tz = floor((-y + 256) / 16)   (row 0 = north edge)
"""
import bpy, bmesh, sys
from mathutils import Vector

def args():
    return sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_glb(path):
    """Import an apicula .glb and return one mesh object with skinning applied, in world space."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == 'MESH']
    for o in meshes:
        bpy.context.view_layer.objects.active = o
        for m in list(o.modifiers):
            if m.type == 'ARMATURE':
                bpy.ops.object.modifier_apply(modifier=m.name)
        o.parent = None
        o.matrix_world = o.matrix_world.copy()
    for o in new:
        if o.type != 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)
    for o in meshes:  # bake transforms
        o.data.transform(o.matrix_world); o.matrix_world.identity()
    if len(meshes) > 1:
        with bpy.context.temp_override(active_object=meshes[0], selected_editable_objects=meshes):
            bpy.ops.object.join()
    return meshes[0]

def tile_of(x, y):
    return int((x + 256) // 16), int((-y + 256) // 16)

def material_name(obj, poly):
    m = obj.material_slots[poly.material_index].material if obj.material_slots else None
    return m.name if m else '?'

def image_name(mat):
    """The texture image a material uses (apicula names images after the game texture)."""
    if mat and mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                return n.image.name.rsplit('.', 1)[0] if n.image.name.endswith('.png') else n.image.name
    return None
