"""Soundbox body -- straight-sided HALF-CONE (D cross-section). build123d Solid, model units."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *
from clements49_params import SOUNDBOX_CAPS
def _cap(p):
    with BuildSketch(Plane.XY.offset(p["z"])) as sk:
        with BuildLine():
            a = EllipticalCenterArc(center=(p["xc"], p["yflat"]), x_radius=p["W"]/2, y_radius=p["D"],
                                    start_angle=0, end_angle=180)   # arc belly to +Y
            Line(a @ 1, a @ 0)                                       # flat soundboard chord
        make_face()
    return sk.sketch
def soundbox():
    """Return the soundbox body Solid (half-cone lofted bass->treble)."""
    return loft([_cap(SOUNDBOX_CAPS["bass"]), _cap(SOUNDBOX_CAPS["treble"])])
if __name__ == "__main__":
    s = soundbox(); print("soundbox volume", round(s.volume,1), "valid", s.is_valid,
                          "bbox", [round(v,1) for v in s.bounding_box().size])
