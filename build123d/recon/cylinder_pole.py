"""Replace harp_pole with a simple cylinder = narrowest pole diameter, extending from the
top of harp_pole down to the bottom of harp_pole_base, along the pillar's leaning axis.

Run: ~/blender5/blender -b blender/clements49.blend --python build123d/recon/cylinder_pole.py
"""
import bpy, bmesh, numpy as np, mathutils

def wv(o):
    mw = o.matrix_world
    return np.array([(mw @ v.co)[:] for v in o.data.vertices])

pole = bpy.data.objects['harp_pole']
P = wv(pole); z = P[:, 2]; zlo, zhi = z.min(), z.max()
nb = 24
# fit the centreline through per-Z-band section centres
cz = []; cx = []; cy = []
for k in range(nb):
    a = zlo + k / nb * (zhi - zlo); b = zlo + (k + 1) / nb * (zhi - zlo)
    m = (z >= a) & (z < b)
    if m.sum() >= 4:
        cz.append(P[m, 2].mean()); cx.append(P[m, 0].mean()); cy.append(P[m, 1].mean())
cz = np.array(cz)
ax, bx = np.polyfit(cz, cx, 1); ay, by = np.polyfit(cz, cy, 1)
axpt = lambda zz: mathutils.Vector((ax * zz + bx, ay * zz + by, zz))
# narrowest radius = min over bands of the 95th-percentile radial distance
rad = np.sqrt((P[:, 0] - (ax * z + bx)) ** 2 + (P[:, 1] - (ay * z + by)) ** 2)
bands = []
for k in range(nb):
    a = zlo + k / nb * (zhi - zlo); b = zlo + (k + 1) / nb * (zhi - zlo)
    m = (z >= a) & (z < b)
    if m.sum() >= 4:
        bands.append(np.percentile(rad[m], 95))
rmin = float(min(bands))
# bottom of harp_pole_base
base = [o for o in bpy.data.objects if o.name.lower().startswith('harp_pole_base')]
zbot = float(min(wv(o)[:, 2].min() for o in base))

top = axpt(zhi); bot = axpt(zbot); center = (top + bot) / 2; vec = top - bot; L = vec.length

# build the cylinder in WORLD coords via bmesh (context-free, robust headless)
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=64,
                      radius1=rmin, radius2=rmin, depth=L)
q = mathutils.Vector((0, 0, 1)).rotation_difference(vec.normalized())
bm.transform(mathutils.Matrix.Translation(center) @ q.to_matrix().to_4x4())
newmesh = bpy.data.meshes.new('harp_pole_cyl')
bm.to_mesh(newmesh); bm.free()
for mat in pole.data.materials:            # keep material
    newmesh.materials.append(mat)
pole.data = newmesh
pole.matrix_world = mathutils.Matrix.Identity(4)   # mesh is already world coords

print("CYL diameter=%.3f  length=%.3f  z %.2f -> %.2f  centre(%.2f,%.2f,%.2f)"
      % (2 * rmin, L, zhi, zbot, center.x, center.y, center.z))
bpy.ops.wm.save_mainfile()
print("SAVED")
