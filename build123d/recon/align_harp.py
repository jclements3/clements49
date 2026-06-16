"""Translate the whole harp so the pillar apex sits on the Z-axis and the feet on Z=0.

Move = (dX, dY, dZ) in model units. Applied to every top-level object (children follow),
so the geometry shifts in world space without touching parenting. Verifies + saves.
Run: ~/blender5/blender -b blender/clements49.blend --python build123d/recon/align_harp.py
"""
import bpy, mathutils

# Net single-pass move from the UNALIGNED blend (clements49.blend.prealign) so the pillar
# apex lands at (0,0,216.45) on the Z-axis and the feet on Z=0. The live clements49.blend
# is ALREADY aligned -- only run this on a fresh revert from .prealign.
DELTA = mathutils.Vector((5.53, 40.75, 0.00))

roots = [o for o in bpy.data.objects if o.parent is None]
for o in roots:
    o.location = o.location + DELTA

# verify in world space
apex = None; az = -1e18; zmin = 1e18
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    mw = o.matrix_world
    for v in o.data.vertices:
        w = mw @ v.co
        if w.z < zmin:
            zmin = w.z
        if 'pole' in o.name.lower() and w.z > az:
            az = w.z; apex = w

print("MOVED %d top-level objects (of %d)" % (len(roots), len(bpy.data.objects)))
print("pillar APEX now: X=%.2f Y=%.2f Z=%.2f" % (apex.x, apex.y, apex.z))
print("lowest point Z now: %.2f" % zmin)
bpy.ops.wm.save_mainfile()
print("SAVED clements49.blend")
