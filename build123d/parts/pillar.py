"""Pillar -- a plain round CYLINDER along the column's (slightly leaning) axis.

The cylinder diameter is the narrowest part of the real column (harp_pole) measured
from clements49.blend. Model units, original world coords.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

# --- axis (matches the measured column: leans slightly in x-z, constant y) ---
Z_BOTTOM, Z_TOP = 15.5, 216.4
AXIS_SLOPE, AXIS_INTERCEPT = -0.0314, 1.055   # cx = slope*z + intercept
# Column moved LEFT (-Y) from the measured -40.5 to open an airgap to the lowest
# string. Y_CENTER=-42.104 gives PILLAR_AIRGAP_MM=25 between A0 and the pillar
# surface (was 12.3 mm). Set PILLAR_AIRGAP_MM and re-solve to retune.
PILLAR_AIRGAP_MM = 25.0
Y_CENTER = -42.104

# --- cylinder parameter -----------------------------------------------------
R = 4.635   # cylinder radius = narrowest pole diameter (9.27, measured from
            # clements49.blend harp_pole at z~79) / 2

def _cx(z):
    return AXIS_SLOPE * z + AXIS_INTERCEPT

def pillar():
    """Plain cylinder placed on the leaning column axis (spiral removed)."""
    bottom = Vector(_cx(Z_BOTTOM), Y_CENTER, Z_BOTTOM)
    top    = Vector(_cx(Z_TOP),    Y_CENTER, Z_TOP)
    axis   = top - bottom
    place  = Plane(origin=bottom, z_dir=axis.normalized()).location   # local +Z -> column axis
    shaft  = Cylinder(radius=R, height=axis.length,
                      align=(Align.CENTER, Align.CENTER, Align.MIN))
    return shaft.located(place)

if __name__ == "__main__":
    s = pillar()
    print("pillar volume", round(s.volume, 1), "valid", s.is_valid,
          "bbox", [round(v, 1) for v in s.bounding_box().size])
