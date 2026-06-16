"""Harp base pedals -- 7 radial lever boxes fanned about the base center.

Each of the 7 pedals (numbered 01..07 in the model) is a thin, narrow lever
that pivots about the central base and fans out radially.  In the original mesh
every pedal is an assembly of ~5 tiny sub-parts (bolt/copper/iron/red/rub); we
do NOT model those -- each pedal is reduced to ONE simple oriented lever box of
the measured length / width / thickness.

All values are in MODEL UNITS (~8.8598 mm/unit) and in ORIGINAL world coords so
the part overlays the full harp model.

Measured (blender world coords, harp_pedal_* objects):
  - every pedal lever is identical in size: L x W x T
  - centers all sit at z = PEDAL_Z_CENTER
  - the 7 levers fan from ~19 deg to ~165 deg (major-axis angle)
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import math
from build123d import *
from clements49_params import PART_BBOX  # noqa: F401  (sanity / reference)

# ---- Lever box dimensions (model units) ---------------------------------
PEDAL_LENGTH = 21.32   # lever length along its major (radial) axis
PEDAL_WIDTH  = 5.0     # nominal lever width (mesh body is a ~2.6u strip with a
                       # wider ~5u foot/head; 5u is a representative single box)
PEDAL_THICK  = 2.74    # vertical thickness (z extent), matches PART_BBOX z span

PEDAL_Z_CENTER = 13.617  # z of every pedal lever center (z range 12.25..14.99)

# ---- Per-pedal placement: (center_x, center_y, major_axis_angle_deg) ----
# Measured from harp_pedal_NN objects.  The levers fan symmetrically about the
# base; pedal 04 is the central one.  Angle is the lever's long-axis heading.
PEDAL_PLACEMENTS = [
    (25.917, -16.220,  18.7),   # 01
    (21.697,  -8.795,  36.0),   # 02
    (15.497,  -2.827,  54.9),   # 03
    (-9.006,   0.075, 108.2),   # 04 (center)
    (-16.494, -4.214, 127.5),   # 05
    (-22.450, -10.610, 146.7),  # 06
    (-25.753, -18.529, 165.1),  # 07
]


def _lever(cx, cy, angle_deg):
    """One pedal lever box, centered at (cx,cy,PEDAL_Z_CENTER) and rotated about
    z by angle_deg so its long axis points radially."""
    box = Box(PEDAL_LENGTH, PEDAL_WIDTH, PEDAL_THICK)
    box = Rotation(0, 0, angle_deg) * box           # spin about z
    box = Pos(cx, cy, PEDAL_Z_CENTER) * box          # move to world position
    return box


def pedals():
    """Return a Compound of the 7 pedal lever Solids (model units, world coords)."""
    return Compound([_lever(*p) for p in PEDAL_PLACEMENTS])


if __name__ == "__main__":
    c = pedals()
    bb = c.bounding_box()
    print("pedals volume", round(c.volume, 1),
          "valid", all(s.is_valid for s in c.solids()),
          "bbox", [round(v, 1) for v in bb.size],
          "z", [round(bb.min.Z, 2), round(bb.max.Z, 2)])
