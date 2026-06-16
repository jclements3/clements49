"""Strings -- 49 thin rods, each from its board anchor to its pin (straight).

Parametric: built directly from clements49_params.STRINGS (the 49-string schedule:
47 + 2 bass). Adding strings to the schedule adds rods automatically.
Returns a Compound of 49 cylinder Solids in model units / original world coords.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *
from clements49_params import STRINGS

# --- parameters -------------------------------------------------------------
STRING_RADIUS = 0.3   # rod radius (model units, ~2.7 mm dia); matches PART_BBOX x-dim


def _rod(board, pin):
    """One straight rod (Cylinder) spanning board->pin, oriented along that axis."""
    b = Vector(*board)
    p = Vector(*pin)
    axis = p - b
    length = axis.length
    if length < 1e-9:
        return None
    # Cylinder is built along +Z centered at origin; place its base at board,
    # pointing toward pin via a Plane whose normal is the rod axis.
    plane = Plane(origin=b, z_dir=axis.normalized())
    return Cylinder(radius=STRING_RADIUS, height=length,
                    align=(Align.CENTER, Align.CENTER, Align.MIN)).located(plane.location)


# Drawing colours by note name (C = tonic red, F = blue, rest dark gray) --------
STRING_COLORS = {"C": (0.85, 0.0, 0.0), "F": (0.0, 0.0, 0.85)}
STRING_COLOR_OTHER = (0.25, 0.25, 0.25)


def _color_for(note):
    return STRING_COLORS.get(note[0], STRING_COLOR_OTHER)


def strings_by_color(string_set=49):
    """Group string rods by draw colour -> list of (Compound, (r,g,b)).

    Same subset rule as strings(); used to overlay coloured string lines on the
    frame HLR (C red, F blue, others dark gray).
    """
    subset = STRINGS if string_set >= 49 else STRINGS[2:]
    groups = {}
    for s in subset:
        r = _rod(s["board"], s["pin"])
        if r is None:
            continue
        groups.setdefault(_color_for(s["note"]), []).append(r)
    return [(Compound(rods), col) for col, rods in groups.items()]


def strings(string_set=49):
    """Return a Compound of string rods (model units, world coords).

    string_set=49 -> all 49 (the 47 measured + 2 bass-extension strings A0,B0).
    string_set=47 -> the original 47 only (drops STRINGS[0:2], the bass extension).
    Parametric expansion toggle for the clements47 vs clements49 plates.
    """
    subset = STRINGS if string_set >= 49 else STRINGS[2:]
    rods = []
    for s in subset:
        r = _rod(s["board"], s["pin"])
        if r is not None:
            rods.append(r)
    return Compound(rods)


if __name__ == "__main__":
    c = strings()
    print("strings count", len(c.solids()))
    print("strings volume", round(c.volume, 3), "valid", c.is_valid,
          "bbox", [round(v, 1) for v in c.bounding_box().size])
