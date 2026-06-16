import bpy, bmesh, json
import numpy as np
NAME='harp_big_side_pivot'; NSEC=11
obj=bpy.data.objects[NAME]
dg=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(dg); me=ev.to_mesh()
M=obj.matrix_world
V=np.array([(M@v.co)[:] for v in me.vertices])
zmin,zmax=float(V[:,2].min()),float(V[:,2].max())
def hull2d(pts):
    P=sorted(set((round(x,4),round(y,4)) for x,y in pts))
    if len(P)<3: return P
    cr=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[]
    for p in P:
        while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    up=[]
    for p in reversed(P):
        while len(up)>=2 and cr(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
secs=[]
zs=np.linspace(zmin+0.4, zmax-0.4, NSEC)
for z in zs:
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(M)
    res=bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:],
                               dist=1e-6, plane_co=(0,0,float(z)), plane_no=(0,0,1))
    cut=[g for g in res['geom_cut'] if isinstance(g,bmesh.types.BMVert)]
    pts=[(v.co.x,v.co.y) for v in cut]; bm.free()
    if len(pts)<3: continue
    h=hull2d(pts)
    if len(h)>=3: secs.append({'z':float(z),'outline_xy':[[round(a,3),round(b,3)] for a,b in h],'n':len(pts)})
json.dump({'name':NAME,'z_min':zmin,'z_max':zmax,'sections':secs},
          open('openscad/analysis/harp_big_side_pivot_zsections.json','w'),indent=1)
print('wrote',len(secs),'planar Z-sections; world z range',round(zmin,2),round(zmax,2))
