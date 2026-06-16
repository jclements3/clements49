"""Extend harp_base_body downward so its flat bottom reaches the bottom of harp_base_bottom.

Moves the bottom-face vertices (the flat ring at the body's min Z) down to harp_base_bottom's
min Z, stretching the side walls. Z-only; body shape preserved.

Run: ~/blender5/blender -b blender/clements49.blend --python build123d/recon/base_extend.py
"""
import bpy

o = bpy.data.objects['harp_base_body']
bottom = bpy.data.objects['harp_base_bottom']

def wmin_z(obj):
    mw = obj.matrix_world
    return min((mw @ v.co).z for v in obj.data.vertices)

target = wmin_z(bottom)                 # bottom of harp_base_bottom
mw = o.matrix_world; mwi = mw.inverted()
mz = min((mw @ v.co).z for v in o.data.vertices)
TOL = 0.6                               # captures the flat bottom face only
dz = target - mz
moved = 0
for v in o.data.vertices:
    w = mw @ v.co
    if w.z <= mz + TOL:
        w.z += dz
        v.co = mwi @ w
        moved += 1
o.data.update()
newmin = min((o.matrix_world @ v.co).z for v in o.data.vertices)
print("moved %d bottom verts by %.2f; harp_base_body new min Z = %.2f (target %.2f)"
      % (moved, dz, newmin, target))
bpy.ops.wm.save_mainfile()
print("SAVED")
