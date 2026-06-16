#!/usr/bin/env python3
"""Parse the TurboSquid pedal-harp OBJ into per-group geometry, in mm.

Frame convention for OUTPUT (mm):
  - source OBJ is z-up (model bbox z is vertical/height)
  - we keep z-up; origin moved to base centre:
        x' = (x - x_centre_of_base_footprint)
        y' = (y - y_centre_of_base_footprint)
        z' = (z - z_min)          # base sits at z=0
  - scale factor SCALE mm/unit applied to all coords.
"""
import re, json, sys
import numpy as np

OBJ = "/home/clementsj/projects/clements49/extract/obj/Pedal_Harp_Instrument_convert.obj"

# ---- pass 1: read all vertices and group->face mapping ----
verts = []
groups = {}          # name -> list of face vertex-index tuples (1-based global)
cur = None
with open(OBJ) as f:
    for line in f:
        if line.startswith('v '):
            p = line.split()
            verts.append((float(p[1]), float(p[2]), float(p[3])))
        elif line.startswith('g '):
            cur = line[2:].strip()
            groups.setdefault(cur, [])
        elif line.startswith('f '):
            if cur is None:
                continue
            idx = []
            for tok in line.split()[1:]:
                # f v/vt/vn -> take v
                vi = tok.split('/')[0]
                idx.append(int(vi))
            groups[cur].append(idx)

V = np.array(verts)            # (N,3) in model units
print(f"verts={len(V)} groups={len(groups)}", file=sys.stderr)

# global bbox
bmin = V.min(0); bmax = V.max(0)
print("model bbox min", bmin, "max", bmax, "ext", bmax-bmin, file=sys.stderr)

def group_vert_indices(name):
    s = set()
    for fc in groups.get(name, []):
        for vi in fc:
            s.add(vi-1 if vi > 0 else len(V)+vi)
    return sorted(s)

def group_verts(name):
    ii = group_vert_indices(name)
    return V[ii] if ii else np.empty((0,3))

def group_centroid(name):
    gv = group_verts(name)
    if len(gv)==0: return None
    return gv.mean(0)

# which groups actually carry faces
nonempty = [g for g in groups if len(groups[g])>0]
print(f"nonempty groups={len(nonempty)}", file=sys.stderr)

# ---------- determine base footprint extents (model units, pre-scale) ----------
base_groups = [g for g in nonempty if g.startswith('harp_base') or g.startswith('harp_leg') or g.startswith('harp_metal_plate')]
bv_list = [group_verts(g) for g in base_groups]
bv_list = [b for b in bv_list if len(b)]
BASEV = np.vstack(bv_list) if bv_list else V
base_xmin, base_ymin = BASEV[:,0].min(), BASEV[:,1].min()
base_xmax, base_ymax = BASEV[:,0].max(), BASEV[:,1].max()
xc = 0.5*(base_xmin+base_xmax)
yc = 0.5*(base_ymin+base_ymax)
zmin = V[:,2].min()
print("base footprint (units) x",base_xmin,base_xmax,"y",base_ymin,base_ymax, file=sys.stderr)

# ---------- scale ----------
# README: 75.5 in height = 1917.7 mm. model z extent:
z_ext_units = (bmax[2]-bmin[2])
SCALE = 1917.7 / z_ext_units
print(f"z_ext_units={z_ext_units:.3f}  SCALE={SCALE:.4f} mm/unit", file=sys.stderr)
# sanity: extreme width spec 40.5in=1028.7mm
print(f"x_ext_mm={ (bmax[0]-bmin[0])*SCALE:.1f}  y_ext_mm={(bmax[1]-bmin[1])*SCALE:.1f}", file=sys.stderr)

def to_mm(p):
    if p is None: return None
    return [ (p[0]-xc)*SCALE, (p[1]-yc)*SCALE, (p[2]-zmin)*SCALE ]

# ---------- tuning pins ----------
pin_names = sorted([g for g in nonempty if re.fullmatch(r'harp_string_bolt_\d+_pivot', g)],
                   key=lambda s:int(s.split('_')[3]))
pins = []
for g in pin_names:
    c = group_centroid(g)
    pins.append((g, to_mm(c)))

# ---------- string hole / string exit points ----------
# two hole families: '_NN_pivot' (sharping discs on neck) and 3-digit '_1NN' (board string-exit eyelets)
disc_names = sorted([g for g in nonempty if re.fullmatch(r'harp_string_hole_\d+_pivot', g)],
                    key=lambda s:int(s.split('_')[3]))
hole_names = sorted([g for g in nonempty if re.fullmatch(r'harp_string_hole_\d+', g)],
                    key=lambda s:int(s.split('_')[-1]))
discs = [(g, to_mm(group_centroid(g))) for g in disc_names]
holes = []
for g in hole_names:
    c = group_centroid(g)
    holes.append((g, to_mm(c)))

# string lower ends: for each harp_string_NN, take the vertex set, find the end nearest the soundboard
str_names = sorted([g for g in nonempty if re.fullmatch(r'harp_string_\d+', g)],
                   key=lambda s:int(s.split('_')[-1]))
str_lower = []
for g in str_names:
    gv = group_verts(g)
    if len(gv)==0: continue
    # lower end = min z cluster centroid
    zlo = gv[:,2].min()
    sel = gv[gv[:,2] < zlo + 0.03*(gv[:,2].max()-gv[:,2].min()+1e-9)]
    c = sel.mean(0)
    str_lower.append((g, to_mm(c)))

# ---------- pillar / column axis ----------
pole_groups = [g for g in nonempty if g.startswith('harp_pole') or g==('harp_connector')]
pv_list = [group_verts(g) for g in ['harp_pole','harp_pole_top','harp_pole_bottom','harp_pole_base'] if g in groups and len(groups[g])]
pv = np.vstack([p for p in pv_list if len(p)]) if pv_list else group_verts('harp_pole')
if len(pv):
    pz_lo = pv[:,2].min(); pz_hi = pv[:,2].max()
    band = 0.05*(pz_hi-pz_lo)
    bot = pv[pv[:,2] < pz_lo+band].mean(0)
    top = pv[pv[:,2] > pz_hi-band].mean(0)
    pillar_bottom = to_mm(bot); pillar_top = to_mm(top)
else:
    pillar_bottom = pillar_top = None

# ---------- soundboard taper ----------
# the soundboard face is harp_wood_plank (flat plank, y~0, strings exit here);
# harp_wood_zig_* are the string-rib segments running up its centreline.
sb_groups = ['harp_wood_plank']
sbv_list = [group_verts(g) for g in sb_groups if g in groups and len(groups[g])]
sbv = np.vstack([s for s in sbv_list if len(s)]) if sbv_list else np.empty((0,3))
soundboard = {}
if len(sbv):
    # board long axis ~ z (it stands up along the body). Use z as 'position'.
    zlo, zhi = sbv[:,2].min(), sbv[:,2].max()
    span = (zhi-zlo)*SCALE
    # width at bass end (low z) and treble end (high z): width in x (or the horizontal across board)
    def width_at(zfrac, half=0.06):
        zc = zlo + zfrac*(zhi-zlo)
        sel = sbv[np.abs(sbv[:,2]-zc) < half*(zhi-zlo)]
        if len(sel)<3: return None
        return (sel[:,0].max()-sel[:,0].min())*SCALE
    soundboard = {
        "bass_width_mm": width_at(0.08),
        "treble_width_mm": width_at(0.95),
        "span_mm": span,
        "z_lo_mm": (zlo-zmin)*SCALE,
        "z_hi_mm": (zhi-zmin)*SCALE,
    }

# ---------- soundbox cross sections ----------
# the body shell is harp_big_side_pivot (+ white_wood liners). Its long axis runs
# up the body diagonally; we slice perpendicular to z and report x-width & y-depth.
box_groups = ['harp_big_side_pivot','harp_white_wood_01','harp_white_wood_02']
box_groups = list(dict.fromkeys([g for g in box_groups if g in groups and len(groups[g])]))
bxv_list = [group_verts(g) for g in box_groups]
bxv = np.vstack([b for b in bxv_list if len(b)]) if bxv_list else np.empty((0,3))
sections = []
if len(bxv):
    zlo, zhi = bxv[:,2].min(), bxv[:,2].max()
    for frac in [0.1,0.25,0.4,0.55,0.7,0.85,0.95]:
        zc = zlo + frac*(zhi-zlo)
        sel = bxv[np.abs(bxv[:,2]-zc) < 0.035*(zhi-zlo)]
        if len(sel)<3: continue
        sections.append({
            "z_mm": round((zc-zmin)*SCALE,1),
            "frac": frac,
            "x_center_mm": round((0.5*(sel[:,0].min()+sel[:,0].max())-xc)*SCALE,1),
            "width_x_mm": round((sel[:,0].max()-sel[:,0].min())*SCALE,1),
            "depth_y_mm": round((sel[:,1].max()-sel[:,1].min())*SCALE,1),
        })

base_footprint = {
    "xmin_mm": (base_xmin-xc)*SCALE, "xmax_mm": (base_xmax-xc)*SCALE,
    "ymin_mm": (base_ymin-yc)*SCALE, "ymax_mm": (base_ymax-yc)*SCALE,
    "width_x_mm": (base_xmax-base_xmin)*SCALE,
    "depth_y_mm": (base_ymax-base_ymin)*SCALE,
}

out = {
    "scale_mm_per_unit": SCALE,
    "model_bbox_units": {"min": bmin.tolist(), "max": bmax.tolist(), "ext": (bmax-bmin).tolist()},
    "origin_units": {"xc":xc,"yc":yc,"zmin":zmin},
    "pins": pins,
    "holes": holes,
    "discs": discs,
    "string_lower": str_lower,
    "pillar_bottom_mm": pillar_bottom,
    "pillar_top_mm": pillar_top,
    "soundboard": soundboard,
    "soundbox_sections": sections,
    "base_footprint": base_footprint,
}
with open("/home/clementsj/projects/clements49/analysis/raw_anchors.json","w") as f:
    json.dump(out,f,indent=2)
print("WROTE raw_anchors.json", file=sys.stderr)
print(f"pins={len(pins)} holes={len(holes)} strings={len(str_lower)} sections={len(sections)}", file=sys.stderr)
