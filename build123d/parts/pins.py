"""Tuning pins -- ONE lathe part (revolve of the ORIGINAL profile) instanced per string.

The pin shape is the model's own turned pin, measured from clements49.blend and cleaned
of mesh noise only (recon/pin_profile.json) -- NOT an invented design. It is axisymmetric
(verified), so revolving the measured (x, r) half-profile reproduces it exactly: rounded
head + neck groove at the drive end, the shaft, and the string-winding groove near the
tip. This is the brass lost-wax / lost-PLA casting pattern. pins() places one at every
string's pin endpoint (scales to the 49-string set).

  pin(length_scale=1, radial_scale=1) -> one pin Solid, axis = world X, centred on origin
  pins(string_set=49, ...)            -> Compound, one pin per string at its pin_xyz (+offset)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

_HERE = os.path.dirname(os.path.abspath(__file__))
_BD = os.path.dirname(_HERE)
_P = json.load(open(os.path.join(_BD, "recon", "pin_profile.json")))
PROFILE = _P["profile"]            # [[x, r], ...] model units (measured, cleaned), axis = x
PLACE_OFFSET = _P["place_offset"]  # pin-centroid - string pin_xyz (world), measured
UNIT_MM = 8.86


def pin(length_scale=1.0, radial_scale=1.0):
    """Revolve the measured-cleaned half-profile about X -> the model's turned pin.

    length_scale / radial_scale rescale length / diameter while keeping the real shape."""
    pts = [(x * length_scale, max(r, 0.0) * radial_scale) for x, r in PROFILE]
    # close the section ALONG THE AXIS (r=0): (x0,0) -> profile -> (xmax,0) -> back.
    # Both axis endpoints are needed or the closing edge cuts diagonally across the part.
    poly = [(pts[0][0], 0.0)] + pts + [(pts[-1][0], 0.0)]
    with BuildSketch(Plane.XY) as sk:
        with BuildLine():
            Polyline(*[(float(a), float(b)) for a, b in poly], close=True)
        make_face()
    solid = revolve(sk.sketch, axis=Axis.X, revolution_arc=360)
    return solid.translate(-solid.bounding_box().center())   # centre on origin


def _strings(string_set):
    s = json.load(open(os.path.join(_BD, "params_strings.json")))["strings"]
    return [x for x in s if not (string_set < 49 and x["idx"] < 2)]


def pins(string_set=49, length_scale=1.0, radial_scale=1.0):
    """One pin per string, placed at pin_xyz + measured offset (axis along X)."""
    base = pin(length_scale, radial_scale)
    off = Vector(*PLACE_OFFSET)
    return Compound([base.moved(Location(Vector(*s["pin_xyz"]) + off)) for s in _strings(string_set)])


if __name__ == "__main__":
    p = pin()
    bb = p.bounding_box()
    print("pin valid", p.is_valid, "vol", round(p.volume, 3),
          "bbox mm", [round(v * UNIT_MM, 2) for v in bb.size])
    print("pins(49):", len(pins(49).solids()), " pins(47):", len(pins(47).solids()))
