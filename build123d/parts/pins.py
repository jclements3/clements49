"""Tuning pins -- ONE clean parametric lathe part (revolve) instanced at every string.

This is a DESIGNED turnable pin (not the art-model's bumpy shape): an axisymmetric
turning blank with named features, so it can be turned on a lathe and cast in brass
(lost-wax / lost-PLA). The square tuning-key drive is broached and the string hole is
drilled as secondary ops; everything else is a single turned profile revolved about the
axis. pins() instances the one pattern at each string's pin endpoint (scales to 49).

Dimensions are in MILLIMETRES (converted to model units internally). Edit DESIGN or pass
overrides to pin()/pins() to adjust the casting design.

  pin(**overrides)            -> one designed pin Solid, axis = world X, centred on origin
  pins(string_set=49, **ovr)  -> Compound, one pin per string at its pin_xyz (+ offset)
  profile_mm(**overrides)     -> [(x_mm, radius_mm), ...] the turning template (for drawings)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

_HERE = os.path.dirname(os.path.abspath(__file__))
_BD = os.path.dirname(_HERE)
UNIT_MM = 8.86

# --- designed turning blank (all mm). x = 0 at the drive (tuning-key) end. -------------
# Dimensions live in recon/pin_design.json (shared with the turning drawing).
DESIGN = {k: v for k, v in
          json.load(open(os.path.join(_BD, "recon", "pin_design.json"))).items()
          if not k.startswith("_")}


def profile_mm(**ovr):
    """Half-profile (x_mm, radius_mm) of the turned blank: drive -> collar -> shaft -> tip."""
    d = {**DESIGN, **ovr}
    L, c = d["length"], d["chamfer"]
    rs, rd, rc = d["d_shaft"] / 2, d["d_drive"] / 2, d["d_collar"] / 2
    ld, lc = d["l_drive"], d["l_collar"]
    return [
        (0.0,        rd - c),   # drive end face (chamfered)
        (c,          rd),
        (ld,         rd),       # drive boss
        (ld,         rc),       # collar step up
        (ld + lc,    rc),       # collar
        (ld + lc,    rs),       # step down to shaft
        (L - c,      rs),       # shaft to tip
        (L,          rs - c),   # tip chamfer
    ]


def pin(**ovr):
    """Revolve the designed profile about X; optionally drill the transverse string hole."""
    d = {**DESIGN, **ovr}
    pts = [(x / UNIT_MM, r / UNIT_MM) for x, r in profile_mm(**ovr)]
    poly = pts + [(pts[-1][0], 0.0)]            # close along the axis (r = 0)
    with BuildSketch(Plane.XY) as sk:
        with BuildLine():
            Polyline(*[(float(a), float(b)) for a, b in poly], close=True)
        make_face()
    solid = revolve(sk.sketch, axis=Axis.X, revolution_arc=360)
    if d["string_hole"] > 0:                    # drilled cross-hole near the tip
        hx = (d["length"] - d["hole_from_tip"]) / UNIT_MM
        rr = d["string_hole"] / 2 / UNIT_MM
        bore = Cylinder(radius=rr, height=d["d_shaft"] * 1.5 / UNIT_MM).rotate(Axis.X, 90)
        solid -= bore.translate((hx, 0, 0))
    return solid.translate(-solid.bounding_box().center())   # centre on origin


def _strings(string_set):
    s = json.load(open(os.path.join(_BD, "params_strings.json")))["strings"]
    return [x for x in s if not (string_set < 49 and x["idx"] < 2)]


def pins(string_set=49, **ovr):
    """One designed pin per string, placed at pin_xyz + measured offset (axis along X)."""
    base = pin(**ovr)
    off = Vector(*json.load(open(os.path.join(_BD, "recon", "pin_profile.json")))["place_offset"])
    return Compound([base.moved(Location(Vector(*s["pin_xyz"]) + off)) for s in _strings(string_set)])


if __name__ == "__main__":
    p = pin()
    bb = p.bounding_box()
    print("pin valid", p.is_valid, "vol", round(p.volume, 3),
          "bbox mm", [round(v * UNIT_MM, 2) for v in bb.size])
    print("pins(49):", len(pins(49).solids()), " pins(47):", len(pins(47).solids()))
