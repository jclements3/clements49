"""Assemble the full parametric harp from the per-part modules and emit review drawings.

Every part module under parts/ exposes a function named after the file
(soundbox(), soundboard(), pillar(), base(), pedals(), strings(), neck()) that
returns a build123d Solid or Compound in MODEL UNITS at ORIGINAL world coords.
harp() collects them into a single Compound so each part overlays the model.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "parts"))

from build123d import Compound
import util

from parts.soundbox import soundbox
from parts.soundboard import soundboard
from parts.pillar import pillar
from parts.base import base
from parts.pedals import pedals
from parts.strings import strings
from parts.neck import neck

# Order = build / report order. Each entry is (label, builder).
PARTS = [
    ("soundbox", soundbox),
    ("soundboard", soundboard),
    ("pillar", pillar),
    ("base", base),
    ("pedals", pedals),
    ("strings", strings),
    ("neck", neck),
]


def harp(string_set=49):
    """Return a Compound of all harp parts at world coords (model units).

    string_set toggles the parametric string expansion (49 = +2 bass, 47 = baseline);
    only the strings part depends on it, the frame geometry is shared.
    """
    children = []
    for label, builder in PARTS:
        shape = builder(string_set=string_set) if label == "strings" else builder()
        shape.label = label
        children.append(shape)
    return Compound(children=children)


if __name__ == "__main__":
    asm = harp()
    bb = asm.bounding_box()
    print("part count", len(asm.children))
    print("assembled bbox dims", [round(v, 1) for v in bb.size])
    print("assembled bbox min", [round(bb.min.X, 1), round(bb.min.Y, 1), round(bb.min.Z, 1)])
    print("assembled bbox max", [round(bb.max.X, 1), round(bb.max.Y, 1), round(bb.max.Z, 1)])
    n_vis, n_hid = util.hlr_svg(asm, "svg/harp_iso.svg")
    print("svg/harp_iso.svg visible", n_vis, "hidden", n_hid)
