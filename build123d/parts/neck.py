"""Neck -- the curved harmonic-curve arm (harp_top_wood region), z ~140.9..211.6.

The neck is a thin, curved beam ("arm") lying in the world Y-Z plane with a nearly
constant thickness in X (the slab), plus a wider block at its base ("foot") where it
joins the rest of the harp. Model units (~8.86 mm/unit), original world coords.

Construction (clean loft/extrude, NOT a mesh hull):
  * The arm silhouette is a closed YZ profile bounded by two smooth Splines:
    the TOP edge zmax(y) and the BOTTOM edge zmin(y). These two edge curves were
    sampled from planar Y-sections of neck.stl (the section centroids follow the
    harmonic curve) and are kept as module-level point lists so the part stays
    tied to the reference geometry / is easy to re-fit if the model changes.
  * That face is extruded along +X by ARM_THICKNESS to make the curved slab.
  * A Box (FOOT) is fused at the base where the neck widens in X.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

# ---------------------------------------------------------------- parameters
# Arm slab thickness in X and its X placement (measured from neck.stl: the main
# slab occupies x in ~[-6.53, -2.79], a near-constant ~3.74-unit-thick wall).
ARM_X_MIN     = -6.53    # inner face of the curved slab (world X)
ARM_THICKNESS = 3.74     # slab thickness in X

# Foot / base block: where the neck thickens in X to meet the harp body.
# Measured extents (region y>~48 of neck.stl).
FOOT_X        = (-6.9, 7.6)      # world X extent of the foot block
FOOT_Y        = (48.0, 62.3)     # world Y extent
FOOT_Z        = (152.0, 171.0)   # world Z extent

# Curved-arm YZ silhouette, sampled from planar Y-sections of neck.stl.
# Each entry is (y, z).  TOP_EDGE = upper boundary zmax(y); BOT_EDGE = lower zmin(y).
# The closed profile runs forward along TOP then back along BOT.
TOP_EDGE = [
    (-35.08, 185.23), (-32.06, 208.35), (-29.04, 211.57), (-26.02, 211.53),
    (-22.99, 211.35), (-19.97, 210.91), (-16.95, 210.27), (-13.93, 209.44),
    (-10.91, 208.26), (-7.89, 206.73), (-4.87, 204.72), (-1.84, 202.08),
    (1.18, 198.55), (4.20, 194.00), (7.22, 188.59), (10.24, 182.12),
    (13.26, 174.54), (16.29, 166.89), (19.31, 160.78), (22.33, 158.08),
    (25.35, 157.82), (28.37, 159.07), (31.39, 161.10), (34.41, 163.30),
    (37.44, 165.41), (40.46, 167.38), (43.48, 169.05), (46.50, 170.21),
]
BOT_EDGE = [
    (-35.08, 175.29), (-32.06, 180.68), (-29.04, 182.68), (-26.02, 183.62),
    (-22.99, 183.94), (-19.97, 183.67), (-16.95, 182.82), (-13.93, 181.25),
    (-10.91, 178.89), (-7.89, 175.61), (-4.87, 170.71), (-1.84, 164.75),
    (1.18, 158.51), (4.20, 152.92), (7.22, 148.51), (10.24, 145.34),
    (13.26, 143.22), (16.29, 141.85), (19.31, 141.13), (22.33, 140.92),
    (25.35, 141.21), (28.37, 142.05), (31.39, 143.37), (34.41, 145.29),
    (37.44, 147.49), (40.46, 149.86), (43.48, 152.46), (46.50, 155.27),
]


def _arm():
    """Curved slab: a smooth closed YZ profile extruded along X."""
    # Build the closed profile in the world Y-Z plane (Plane.YZ: local x->world Y,
    # local y->world Z). Points are given as (Y, Z) which map directly to (u, v).
    top = [(y, z) for (y, z) in TOP_EDGE]
    bot = [(y, z) for (y, z) in BOT_EDGE]
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            s_top = Spline(*top)                 # forward along upper edge
            s_bot = Spline(*list(reversed(bot))) # back along lower edge
            Line(top[-1], list(reversed(bot))[0])  # close at far (foot) end
            Line(list(reversed(bot))[-1], top[0])  # close at near (tip) end
        make_face()
    # Plane.YZ normal is +X; extrude from ARM_X_MIN through ARM_THICKNESS.
    arm = extrude(sk.sketch, amount=ARM_THICKNESS)
    # The sketch sits at X=0; move it to the measured slab X position.
    arm = arm.translate((ARM_X_MIN, 0, 0))
    return arm


def _foot():
    """Base block where the neck thickens in X to meet the body."""
    cx = (FOOT_X[0] + FOOT_X[1]) / 2
    cy = (FOOT_Y[0] + FOOT_Y[1]) / 2
    cz = (FOOT_Z[0] + FOOT_Z[1]) / 2
    box = Box(FOOT_X[1] - FOOT_X[0], FOOT_Y[1] - FOOT_Y[0], FOOT_Z[1] - FOOT_Z[0])
    return box.translate((cx, cy, cz))


def neck():
    """Return the neck Solid (curved arm + foot), model units, world coords."""
    arm = _arm()
    foot = _foot()
    result = arm + foot
    return result


if __name__ == "__main__":
    s = neck()
    bb = s.bounding_box()
    print("neck volume", round(s.volume, 1), "valid", s.is_valid,
          "bbox dims", [round(v, 1) for v in bb.size],
          "z", [round(bb.min.Z, 1), round(bb.max.Z, 1)])
