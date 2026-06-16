"""Pillar -- a CYLINDER shaft wrapped with an Archimedean (constant-pitch) SPIRAL ridge.

Per request: the column is a plain round cylinder along the pillar's (slightly leaning)
axis, decorated with an evenly-spaced spiral winding up it (a helix on the cylinder =
the Archimedean / constant-pitch spiral). Model units, original world coords.
Parameters below (radius, turns, ridge) are tunable.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

# --- axis (matches the measured column: leans slightly in x-z, constant y) ---
Z_BOTTOM, Z_TOP = 15.5, 216.4
AXIS_SLOPE, AXIS_INTERCEPT = -0.0314, 1.055   # cx = slope*z + intercept
Y_CENTER = -40.5

# --- cylinder + spiral parameters -------------------------------------------
R          = 4.635   # cylinder radius = narrowest pole diameter (9.27, measured from
                     # clements49.blend harp_pole at z~79) / 2
TURNS      = 10      # number of spiral turns up the column
GROOVE_R   = 1.1     # radius of the spiral groove cut INTO the shaft surface

def _cx(z):
    return AXIS_SLOPE * z + AXIS_INTERCEPT

def pillar():
    """Cylinder shaft + helical (Archimedean) spiral ridge, placed on the leaning axis."""
    bottom = Vector(_cx(Z_BOTTOM), Y_CENTER, Z_BOTTOM)
    top    = Vector(_cx(Z_TOP),    Y_CENTER, Z_TOP)
    axis   = top - bottom
    L      = axis.length
    place  = Plane(origin=bottom, z_dir=axis.normalized()).location   # local +Z -> column axis

    # build shaft + spiral in a LOCAL +Z frame, then place onto the leaning axis
    shaft = Cylinder(radius=R, height=L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with BuildLine() as ln:
        Helix(pitch=L / TURNS, height=L, radius=R)          # spiral on the cylinder surface
    path = ln.line
    prof_plane = Plane(origin=path @ 0, z_dir=path % 0)     # small circle normal to the helix
    with BuildSketch(prof_plane) as sk:
        Circle(GROOVE_R)
    spiral = sweep(sk.sketch, path=path)                    # tube following the spiral
    col = shaft - spiral                                    # GROOVE the spiral INTO the column
    return col.located(place)

if __name__ == "__main__":
    s = pillar()
    print("pillar volume", round(s.volume, 1), "valid", s.is_valid,
          "bbox", [round(v, 1) for v in s.bounding_box().size])
