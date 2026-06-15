#!/usr/bin/env python3
"""Export reference STL meshes (mm, z-up, origin at base centre) for OpenSCAD overlay.
whole_harp.stl  - everything
frame_only.stl  - structural shape: exclude strings, small bolts, pedal metal, discs.
"""
import re, json, numpy as np, trimesh

OBJ="/home/clementsj/projects/clements49/extract/obj/Pedal_Harp_Instrument_convert.obj"
OUT="/home/clementsj/projects/clements49/cad/reference"
A=json.load(open("/home/clementsj/projects/clements49/cad/analysis/anchors.json"))
SCALE=A["scale_mm_per_unit"]
RAW=json.load(open("/home/clementsj/projects/clements49/cad/analysis/raw_anchors.json"))
xc=RAW["origin_units"]["xc"]; yc=RAW["origin_units"]["yc"]; zmin=RAW["origin_units"]["zmin"]

# parse verts + per-group faces (triangulate fan)
verts=[]; groups={}; cur=None
for line in open(OBJ):
    if line.startswith('v '):
        p=line.split(); verts.append((float(p[1]),float(p[2]),float(p[3])))
    elif line.startswith('g '):
        cur=line[2:].strip(); groups.setdefault(cur,[])
    elif line.startswith('f ') and cur:
        idx=[int(t.split('/')[0])-1 for t in line.split()[1:]]
        for i in range(1,len(idx)-1):
            groups[cur].append((idx[0],idx[i],idx[i+1]))
V=np.array(verts,dtype=np.float64)
# transform to mm frame
Vt=np.column_stack([(V[:,0]-xc)*SCALE,(V[:,1]-yc)*SCALE,(V[:,2]-zmin)*SCALE])

def build(group_names):
    faces=[]
    for g in group_names:
        faces.extend(groups[g])
    if not faces: return None
    f=np.array(faces,dtype=np.int64)
    used=np.unique(f)
    remap=-np.ones(len(Vt),dtype=np.int64); remap[used]=np.arange(len(used))
    m=trimesh.Trimesh(vertices=Vt[used], faces=remap[f], process=False)
    return m

allg=[g for g in groups if len(groups[g])>0]
whole=build(allg)
whole.export(f"{OUT}/whole_harp.stl")
print("whole_harp.stl verts",len(whole.vertices),"faces",len(whole.faces))

# frame_only: exclude strings, small bolts, pedal mechanism metal, sharping discs/action plates.
EXCL=re.compile(r'^(harp_string_\d+|harp_string_bolt_\d+_pivot|harp_string_hole_\d+_pivot|'
                r'harp_string_hole_\d+|harp_round_bolt|harp_back_bolt|harp_hold_bolt|'
                r'harp_oval_bolts|harp_iron_bolt|harp_gold_box|harp_pedal_)')
frame_g=[g for g in allg if not EXCL.match(g)]
frame=build(frame_g)
frame.export(f"{OUT}/frame_only.stl")
print("frame_only.stl verts",len(frame.vertices),"faces",len(frame.faces),"groups",len(frame_g))

# bbox sanity (mm)
for nm,m in [("whole",whole),("frame",frame)]:
    lo=m.vertices.min(0); hi=m.vertices.max(0)
    print(nm,"bbox mm  x",round(lo[0]),round(hi[0])," y",round(lo[1]),round(hi[1])," z",round(lo[2]),round(hi[2]))
