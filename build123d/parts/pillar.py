"""Pillar -- tall slightly-leaning tapered ROUND column (the "pole").

Built as a loft of horizontal Circles stacked along the pillar's axis.
The axis leans linearly in x-z (cx = AXIS_SLOPE*z + AXIS_INTERCEPT) while
y stays constant. The clean pole tapers from ~6.4 at the base to a ~4.6
waist near mid-height then widens again toward the top; the very bottom is
a wide foot flare and the top has a smaller collar flare (joints to the
neighbouring parts). Model units, original world coords.

Measured from stl/pillar.stl (trimesh, median radius per z-band).
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

# --- Axis (slight lean in x-z, constant y) -------------------------------
Z_BOTTOM      = 15.5    # bottom of pillar (model z)
Z_TOP         = 216.4   # top of pillar
AXIS_SLOPE    = -0.0314  # dcx/dz : column leans toward -x as it rises
AXIS_INTERCEPT = 1.055   # cx = AXIS_SLOPE*z + AXIS_INTERCEPT
Y_CENTER      = -40.5    # constant y of the column centerline

# --- Radius profile: (z, x_radius, y_radius) control rings ----------------
# The slender pole is round (x_radius == y_radius). The very bottom is a
# splayed FOOT flange (wider in x than y) and the top has a small collar
# flare. Anisotropic rings are lofted as ellipses.
FOOT_RX = 24.2   # bottom foot half-width in x (sets overall x bbox)
FOOT_RY = 16.2   # bottom foot half-width in y
PROFILE = [
    (15.5,  FOOT_RX, FOOT_RY),  # splayed bottom foot flange
    (18.0,   8.0,  8.0),        # foot collapsing into round pole
    (30.0,   6.6,  6.6),        # base of slender pole
    (43.6,   5.3,  5.3),
    (67.7,   4.6,  4.6),        # waist (thinnest)
    (140.0,  5.0,  5.0),
    (188.0,  5.8,  5.8),        # pole widening toward top
    (205.0,  8.5,  8.5),        # collar flare begins
    (216.4,  9.4,  9.4),        # top collar flare
]


def _cx(z):
    return AXIS_SLOPE * z + AXIS_INTERCEPT


def _ring(z, rx, ry):
    """Horizontal ring centered on the leaning axis at height z.

    Circle when rx == ry, otherwise an ellipse (full 0..360 arc).
    """
    cx = _cx(z)
    with BuildSketch(Plane.XY.offset(z)) as sk:
        if abs(rx - ry) < 1e-9:
            with Locations((cx, Y_CENTER)):
                Circle(rx)
        else:
            with BuildLine():
                EllipticalCenterArc(center=(cx, Y_CENTER), x_radius=rx, y_radius=ry,
                                    start_angle=0, end_angle=360)
            make_face()
    return sk.sketch


def pillar():
    """Return the pillar Solid: loft of round/elliptical rings along the leaning axis."""
    rings = [_ring(z, rx, ry) for (z, rx, ry) in PROFILE]
    return loft(rings)


if __name__ == "__main__":
    s = pillar()
    print("pillar volume", round(s.volume, 1),
          "valid", s.is_valid,
          "bbox", [round(v, 1) for v in s.bounding_box().size])
