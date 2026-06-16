"""Import the limacon base ring (/tmp/limacon_base.stl, world coords, model units) into
clements49.blend as a new object 'harp_base_limacon'. Nothing else is changed.

Run: ~/blender5/blender -b blender/clements49.blend --python build123d/recon/import_limacon.py
"""
import bpy, numpy as np

before = set(o.name for o in bpy.data.objects)
bpy.ops.wm.stl_import(filepath="/tmp/limacon_base.stl", global_scale=1.0)
new = [o for o in bpy.data.objects if o.name not in before]
obj = new[0]
obj.name = "harp_base_limacon"

mw = obj.matrix_world
P = np.array([(mw @ v.co)[:] for v in obj.data.vertices])
lo = P.min(0); hi = P.max(0)
print("imported %s verts=%d  X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.2f,%.2f]"
      % (obj.name, len(P), lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
bpy.ops.wm.save_mainfile()
print("SAVED")
