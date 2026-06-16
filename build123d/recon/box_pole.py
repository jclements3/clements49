"""Replace harp_pole (now a cylinder) with a thin rectangular beam on the SAME leaning axis.

Cross-section: Y = full pillar diameter, X = half the diameter. Beam follows the column
lean (shortest-arc rotation keeps faces ~aligned to world X/Y), centred on the same axis,
from the pole top down to the bottom of harp_pole_base.

Run: ~/blender5/blender -b blender/clements49.blend --python build123d/recon/box_pole.py
"""
import bpy, bmesh, numpy as np, mathutils

def wv(o):
    mw = o.matrix_world
    return np.array([(mw @ v.co)[:] for v in o.data.vertices])

pole = bpy.data.objects['harp_pole']
P = wv(pole); z = P[:, 2]; zlo, zhi = z.min(), z.max()
# axis through cap centres (the cylinder's centreline)
nb = 24; cz = []; cx = []; cy = []
for k in range(nb):
    a = zlo + k / nb * (zhi - zlo); b = zlo + (k + 1) / nb * (zhi - zlo)
    m = (z >= a) & (z < b)
    if m.sum() >= 4:
        cz.append(P[m, 2].mean()); cx.append(P[m, 0].mean()); cy.append(P[m, 1].mean())
cz = np.array(cz)
ax, bx = np.polyfit(cz, cx, 1); ay, by = np.polyfit(cz, cy, 1)
axpt = lambda zz: mathutils.Vector((ax * zz + bx, ay * zz + by, zz))
# diameter = current cylinder diameter (max radial dist about the axis)
rad = np.sqrt((P[:, 0] - (ax * z + bx)) ** 2 + (P[:, 1] - (ay * z + by)) ** 2)
dia = 2 * float(rad.max())
# base bottom
base = [o for o in bpy.data.objects if o.name.lower().startswith('harp_pole_base')]
zbot = float(min(wv(o)[:, 2].min() for o in base))

top = axpt(zhi); bot = axpt(zbot); center = (top + bot) / 2; vec = top - bot; L = vec.length

bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)                          # unit cube
bm.transform(mathutils.Matrix.Diagonal((dia / 2, dia, L, 1.0)))   # X=dia/2, Y=dia, Z=L
q = mathutils.Vector((0, 0, 1)).rotation_difference(vec.normalized())   # shortest arc Z->axis
bm.transform(mathutils.Matrix.Translation(center) @ q.to_matrix().to_4x4())
newmesh = bpy.data.meshes.new('harp_pole_box')
bm.to_mesh(newmesh); bm.free()
for mat in pole.data.materials:
    newmesh.materials.append(mat)
pole.data = newmesh
pole.matrix_world = mathutils.Matrix.Identity(4)

print("BOX  X=%.3f (half)  Y=%.3f (full dia)  Z(len)=%.3f  z %.2f->%.2f  centre(%.2f,%.2f,%.2f)"
      % (dia / 2, dia, L, zhi, zbot, center.x, center.y, center.z))
bpy.ops.wm.save_mainfile()
print("SAVED")
