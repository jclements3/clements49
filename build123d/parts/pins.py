"""Tuning pins -- ONE parametric lathe part (revolve) instanced at every string.

The pins are axisymmetric turned parts (verified: cross-sections are circles), so a
single revolved profile represents them exactly. The default profile + placement offset
are measured from clements49.blend (recon/pin_profile.json); the pin is the brass
lost-wax / lost-PLA casting pattern, and pins() places one at each string's pin endpoint
so it scales with the 49-string set automatically.

pin(length_scale=1, radial_scale=1) -> one pin Solid, axis = world X, centred on origin.
pins(string_set=49, ...) -> Compound of one pin per string at its pin_xyz (+ measured offset).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

_HERE = os.path.dirname(os.path.abspath(__file__))
_BD = os.path.dirname(_HERE)
_PROF = json.load(open(os.path.join(_BD, "recon", "pin_profile.json")))
PROFILE = _PROF["profile"]            # [[x, r], ...] model units, axis = x
PLACE_OFFSET = _PROF["place_offset"]  # pin-centroid - string pin_xyz (world)


def pin(length_scale=1.0, radial_scale=1.0):
    """Revolve the measured (x, r) half-profile about the X axis -> one turned pin.

    length_scale / radial_scale let you adjust the real pin design (longer shaft,
    fatter diameter) while keeping the measured shape."""
    pts = [(x * length_scale, max(r, 0.0) * radial_scale) for x, r in PROFILE]
    # close the half-section along the axis (r = 0): ...-> (xmax,0) -> back to (xmin,0)
    poly = pts + [(pts[-1][0], 0.0)]
    with BuildSketch(Plane.XY) as sk:
        with BuildLine():
            Polyline(*[(float(a), float(b)) for a, b in poly], close=True)
        make_face()
    solid = revolve(sk.sketch, axis=Axis.X, revolution_arc=360)
    return solid.translate(-solid.bounding_box().center())   # centre on origin


def _strings(string_set):
    d = json.load(open(os.path.join(_BD, "params_strings.json")))
    return [s for s in d["strings"] if not (string_set < 49 and s["idx"] < 2)]


def pins(string_set=49, length_scale=1.0, radial_scale=1.0):
    """One pin per string, placed at pin_xyz + measured offset (axis along X)."""
    base = pin(length_scale, radial_scale)
    off = Vector(*PLACE_OFFSET)
    out = []
    for s in _strings(string_set):
        out.append(base.moved(Location(Vector(*s["pin_xyz"]) + off)))
    return Compound(out)


if __name__ == "__main__":
    p = pin()
    bb = p.bounding_box()
    print("pin valid", p.is_valid, "vol", round(p.volume, 3),
          "bbox", [round(v, 2) for v in bb.size],
          "-> mm", [round(v * 8.86, 1) for v in bb.size])
    allp = pins(49)
    print("pins(49):", len(allp.solids()), "solids   pins(47):", len(pins(47).solids()))
    print("assembly bbox", [round(v, 1) for v in allp.bounding_box().size])
