#!/usr/bin/env python3
import json, numpy as np

RAW="/home/clementsj/projects/clements49/cad/analysis/raw_anchors.json"
d=json.load(open(RAW))
SCALE=d["scale_mm_per_unit"]

def order_bass_treble(items):
    # items: list of [name, [x,y,z]]; bass->treble = increasing x (player/pillar side -> treble)
    pts=[(n,p) for n,p in items if p is not None]
    pts.sort(key=lambda t: t[1][0])
    return pts

pins = order_bass_treble(d["pins"])
holes = order_bass_treble(d["holes"])
strings = order_bass_treble(d["string_lower"])

pin_pts   = [[round(v,2) for v in p] for _,p in pins]
hole_pts  = [[round(v,2) for v in p] for _,p in holes]
str_pts   = [[round(v,2) for v in p] for _,p in strings]

# string-exit line: prefer the hole eyelets (on the board face, y~2); fall back to string lower ends.
# Both are reported. Use hole eyelets as primary exit points.
exit_pts = hole_pts if len(hole_pts) >= 40 else str_pts

# soundboard taper from body depth_y at bass & treble ends of the string region.
secs = d["soundbox_sections"]
bass_sec = secs[0]; treble_sec = secs[-1]
# soundboard span = distance along board between bass-most and treble-most string exit
exa=np.array(str_pts)
span = float(np.linalg.norm(exa[-1]-exa[0]))
board_taper = {
    "bass_width_mm": round(bass_sec["depth_y_mm"],1),     # body depth_y (across-board) at bass
    "treble_width_mm": round(treble_sec["depth_y_mm"],1),
    "span_mm": round(span,1),
    "note": "width = body across-board (y) extent at the bass-most/treble-most body station; span = bass->treble string-exit chord length",
}

pillar_top = [round(v,2) for v in d["pillar_top_mm"]]
pillar_bottom = [round(v,2) for v in d["pillar_bottom_mm"]]

base_fp = {k:round(v,1) for k,v in d["base_footprint"].items()}

# pin spacing stats
pa=np.array(pin_pts)
sp=np.linalg.norm(np.diff(pa,axis=0),axis=1)

anchors = {
  "scale_mm_per_unit": round(SCALE,4),
  "units_assumed": "model OBJ in arbitrary units; scaled so model z-extent (216.451) = 75.5 in = 1917.7 mm spec height",
  "frame": "z-up; origin at base-footprint centre in x,y and at global z_min (base sits on z=0). bass->treble = +x.",
  "scale_checks": {
    "spec_height_in": 75.5, "model_height_mm": round((d['model_bbox_units']['ext'][2])*SCALE,1),
    "spec_extreme_width_in": 40.5, "spec_extreme_width_mm": 1028.7,
    "model_x_extent_mm": round(d['model_bbox_units']['ext'][0]*SCALE,1),
    "model_y_extent_mm": round(d['model_bbox_units']['ext'][1]*SCALE,1),
    "note": "model is a 47-string instrument; absolute extents differ from the 49-string spec but height anchors the scale. x-extent (~1110mm) brackets the 1029mm extreme-width spec."
  },
  "tuning_pin_points_mm": pin_pts,
  "string_hole_points_mm": exit_pts,
  "string_lower_end_points_mm": str_pts,
  "n_pins": len(pin_pts), "n_holes": len(hole_pts), "n_strings": len(str_pts),
  "pin_spacing_mm": {"median": round(float(np.median(sp)),1), "min": round(float(sp.min()),1), "max": round(float(sp.max()),1)},
  "pillar_axis": {"top_mm": pillar_top, "bottom_mm": pillar_bottom,
                  "length_mm": round(float(np.linalg.norm(np.array(pillar_top)-np.array(pillar_bottom))),1)},
  "board_taper": board_taper,
  "soundbox_sections": secs,
  "base_footprint": base_fp,
}
with open("/home/clementsj/projects/clements49/cad/analysis/anchors.json","w") as f:
    json.dump(anchors,f,indent=2)
print("pins",len(pin_pts),"holes",len(hole_pts),"strings",len(str_pts))
print("span",span,"pin spacing median",np.median(sp))
print("pillar len",anchors["pillar_axis"]["length_mm"])
print(json.dumps(board_taper,indent=2))
