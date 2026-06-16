"""Replace harp_base_limacon's MESH with /tmp/limacon_pedals.stl while KEEPING the object's
current transform (the user slid it). Imports the new mesh as a temp object, swaps the mesh
datablock onto harp_base_limacon, deletes the temp. The object's location is preserved.

Run: ~/blender5/blender -b blender/clements49.blend --python build123d/recon/replace_mesh_keeploc.py
"""
import bpy

target = bpy.data.objects['harp_base_limacon']
loc = tuple(target.location)
before = set(o.name for o in bpy.data.objects)
bpy.ops.wm.stl_import(filepath="/tmp/limacon_pedals.stl", global_scale=1.0)
temp = [o for o in bpy.data.objects if o.name not in before][0]
newmesh = temp.data
target.data = newmesh                      # swap mesh, keep target's transform
bpy.data.objects.remove(temp, do_unlink=True)
print("kept location:", [round(v, 2) for v in loc], "new mesh verts:", len(target.data.vertices))
bpy.ops.wm.save_mainfile()
print("SAVED")
