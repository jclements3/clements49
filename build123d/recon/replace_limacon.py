"""Replace harp_base_limacon with the current /tmp/limacon_pedals.stl (dimpled inner
a=1.5b, outer a=2b, pedal slots cut). Deletes the old object, imports the new one
with the same name, saves.

Run: ~/blender5/blender -b blender/clements49.blend --python build123d/recon/replace_limacon.py
"""
import bpy, numpy as np

old = bpy.data.objects.get('harp_base_limacon')
if old:
    bpy.data.objects.remove(old, do_unlink=True)
    print("deleted old harp_base_limacon")
else:
    print("no existing harp_base_limacon")

before = set(o.name for o in bpy.data.objects)
bpy.ops.wm.stl_import(filepath="/tmp/limacon_pedals.stl", global_scale=1.0)
obj = [o for o in bpy.data.objects if o.name not in before][0]
obj.name = "harp_base_limacon"

mw = obj.matrix_world
P = np.array([(mw @ v.co)[:] for v in obj.data.vertices])
lo = P.min(0); hi = P.max(0)
print("imported harp_base_limacon verts=%d X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.2f,%.2f]"
      % (len(P), lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
bpy.ops.wm.save_mainfile()
print("SAVED")
